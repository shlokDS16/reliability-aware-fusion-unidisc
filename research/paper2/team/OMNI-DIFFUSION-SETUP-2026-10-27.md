---
agent: lab-engineer
date: 2026-10-27
brief: clone, security-review and install Omni-Diffusion in an isolated env (no GPU)
status: done, CPU-only smoke passed; no weights loaded; GPU not used for any inference or load
evidence: E3 (code inspected at pinned SHAs) plus E4 for the import/config/tokenizer smoke (CPU, this machine)
---

# Omni-Diffusion setup (2026-10-27)

Authorisation: Shlok, lead session 2026-10-27 ~21:20 IST ("Do it as it might improve our results I believe").
The permission check did not block any step. Everything below was run on CPU. Stricter rule received
after the 23:25 crash: no CUDA at all, `CUDA_VISIBLE_DEVICES=""` on every Python command. The re-check and
final smoke after that message followed it. Disclosure of what happened before it: the first smoke runs
printed `torch.cuda.is_available()` (True) and one `nvidia-smi --query-gpu=memory.used` call returned
0 MiB. No tensor, model or CUDA context was created on the GPU. The crash at ~23:25 was not caused by this
work (no GPU workload ran from this task), but I cannot prove that from here.

## 1. Pinned commits (source facts)

| Repo | URL | SHA | Date / subject |
|---|---|---|---|
| Omni-Diffusion | https://github.com/VITA-MLLM/Omni-Diffusion | `c4f4625f84197a72d556ea00f10e5b2775524252` | 2026-03-12 "update" |
| GLM-4-Voice (submodule, a fork) | https://github.com/shenyunhang/GLM-4-Voice | `54d667262bc1b92a62211aca44c7fcfe290e5df9` | gitlink in Omni-Diffusion `.gitmodules` |
| Matcha-TTS (submodule of the fork) | https://github.com/shivammehta25/Matcha-TTS | `dd9105b34bf2be2230f4aa1e4769fb586a3c824e` | gitlink in GLM-4-Voice `.gitmodules` |

Location: `C:\Users\Shlok\Downloads\Multi-Modality Language model\models\third_party\Omni-Diffusion`
(submodules checked out inside it). After the crash: `git status` clean in all three, `git fsck` clean,
HEADs unchanged. The GLM-4-Voice fork and Matcha-TTS were cloned because the official repo's README
(`git submodule update --init --recursive`) and `tools/inference.py:27-30` (sys.path entries) require them.
They are two more third-party repos beyond the one named in the brief; I treated them as part of the
official repo's dependency chain. Tell me if you want them removed.

## 2. Security review

Scope read: setup.py, requirements_ds_gpu.txt, `.gitmodules`, scripts/*.sh, all of `omni_diffusion/`
(grep for network, exec, pickle, subprocess, trust_remote_code, torch.load, eval/exec, base64, ctypes,
rmtree), `tools/inference.py`, the six model files in the HF snapshot (executed under trust_remote_code),
and the GLM-4-Voice and Matcha-TTS files on the inference path. Not read line by line: `web_demo.py`,
`model_server.py` (GLM-4-Voice demo servers, not on our path), training code (`tools/trainer_v4_51_3.py`,
`tools/finetune_dream_v4_51_3.py`, vendored HF Trainer).
Hidden Unicode: scanned every .py/.sh/.json/.yaml/.txt/.md/.gitmodules in the clone and every .py/.json
in the HF snapshot for Cf-category characters, zero-width, BOM (beyond file start) and tag characters:
**0 hits** (checked by an inline script, not the hidden-unicode skill's tool).

**Verdict: SAFE WITH CAVEATS.** No obfuscation, no exec/eval/os.system/subprocess in the package, no
import-time network calls, no post-install hooks (`setup.py` is a 10-line setuptools stub with
`install_requires=[]`). The caveats are all "this loads code or pickles from other repos at run time":

| # | Finding | Location | Risk | Mitigation |
|---|---|---|---|---|
| 1 | `trust_remote_code=True` on AutoConfig/AutoTokenizer/AutoModel/GenerationConfig | `tools/inference.py:83,92,100,110` (same pattern in `tools/evaluate_*.py`) | Runs the .py files in the HF snapshot. I diffed them against the repo: configuration_dream, generation_utils, modeling_dream, resampler_projector are identical to the repo copies modulo CRLF; modeling_sensevoice and tokenization_dream differ only in a regex rewrite, docstrings and one import (below). No malicious content found. | Do not use `tools/inference.py` as is. Import `omni_diffusion.models.dream` (it registers `DreamConfig`/`DreamModel` with `AutoConfig`/`AutoModelForCausalLM`, `models/dream/__init__.py:8-9`) and call with `trust_remote_code=False`. Verified for AutoConfig (smoke below). `AutoTokenizer` still refuses (auto_map) so use `DreamTokenizer.from_pretrained(snap)` directly (verified). |
| 2 | `snapshot_download("FunAudioLLM/SenseVoiceSmall")` then `build_model(..., trust_remote_code=True)` | `omni_diffusion/models/dream/modeling_sensevoice.py:1080-1082`, `:729-731`; `omni_diffusion/tokenizer_sensevoice_glm4voice.py:118-121` | Network access at model construction, and funasr executes `model.py` from the SenseVoiceSmall repo (Alibaba FunAudioLLM org). Unconditional: `DreamBaseModel.__init__` builds `AudioEncoder()` at `modeling_dream.py:763` even for text/image use. | Pre-download that repo once, pin its revision, read its `model.py`, then run with `HF_HUB_OFFLINE=1`. Not done here (see section 7). |
| 3 | `torch.load` without `weights_only` | GLM-4-Voice `flow_inference.py:28,30` (flow.pt, hift.pt), `cosyvoice/cli/model.py:28-33`, `cosyvoice/cli/frontend.py:55`; Matcha `cli.py:87`, `hifigan/xutils.py:44` | Pickle execution if a decoder checkpoint were tampered with. | torch 2.11 defaults `weights_only=True`, so a malicious pickle fails to load rather than executing (stated from torch docs for >=2.6, not tested here). Only needed for the optional speech decoder. |
| 4 | `load_hyperpyyaml(config.yaml)` | GLM-4-Voice `flow_inference.py:14-15` | HyperPyYAML can instantiate arbitrary Python classes from YAML (`!new:`). The decoder `config.yaml` comes from `THUDM/glm-4-voice-decoder`. | Read that config.yaml after download; pin revision. |
| 5 | Magvit loader falls back to `pytorch_model.bin` pickle if safetensors fetch errors | `omni_diffusion/models/magvit/modeling_utils.py:546-551,727-730` | Only if safetensors is missing; `showlab/magvitv2` ships `pytorch_model.safetensors` (HF API listing: config.json, pytorch_model.safetensors, README). | Pass `use_safetensors=True`. |
| 6 | Shell scripts `pip install` unpinned packages, set `HF_ENDPOINT=https://hf-mirror.com` | `scripts/set_env_ds_gpu.sh:10-11`, `scripts/deepspeed/diffusion_dream/finetune.sh:26-28`, `evaluate_*.sh:24-25,38` | Third-party mirror and unpinned installs. | Never run these scripts. We did not. |
| 7 | `from export_meta import export_rebuild_model` | `modeling_sensevoice.py:1061` (repo copy only) | Imports a module that is not in any repo; only reached in an ONNX export path. The snapshot copy defines the function inline instead. | None needed; do not call export. |
| 8 | Hard-coded `/workspace/audio_checkpoints/...` torch.load paths | GLM-4-Voice `cosyvoice/dataset/processor.py:63-64` | Training-data code, not imported by inference. | None. |

Matcha-TTS: setup.py is `cythonize` + requirements install; **we did not pip install it**, we only put it
on `PYTHONPATH` as `tools/inference.py` does. `matcha.utils.utils` has a `wget.download` helper
(`utils.py:208-219`) used for checkpoint download in its own CLI, not on our path.

## 3. Environment

`C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv-omni`, CPython 3.12.14 (uv). `.venv` was not
touched. Full lock: `.venv-omni\freeze-2026-10-27.txt` (124 lines). `uv pip check`: all installed packages
compatible (re-run after the crash).

### Exact commands (cwd = project root; `UV_CONCURRENT_DOWNLOADS=4`)

```
uv venv .venv-omni --python 3.12
uv pip install --python .venv-omni/Scripts/python.exe --index-url https://download.pytorch.org/whl/cu130 \
    "torch==2.11.0" "torchvision==0.26.0" "torchaudio==2.11.0"            # 25 min wall (slow link + extraction)
# /tmp/omni-constraints.txt = the three torch pins above with +cu130
uv pip install --python .venv-omni/Scripts/python.exe -r /tmp/omni-req.txt -c /tmp/omni-constraints.txt \
    --extra-index-url https://download.pytorch.org/whl/cu130 --index-strategy unsafe-best-match
uv pip install --python .venv-omni/Scripts/python.exe -e models/third_party/Omni-Diffusion --no-deps
uv pip install --python .venv-omni/Scripts/python.exe decord -c /tmp/omni-constraints.txt
# deepspeed: DS_BUILD_OPS=0 uv pip install deepspeed  -> FAILED (see conflicts); replaced by a local shim
```

`/tmp/omni-req.txt` (inference subset, not the repo's full requirements file): transformers==4.51.3,
accelerate>=1.1.1, safetensors, huggingface_hub<1.0, einops, timm, diffusers==0.32.2, peft==0.17.1,
jaxtyping, typeguard, datasets, funasr, hyperpyyaml, conformer, omegaconf, hydra-core, lightning,
modelscope, natsort, termcolor, tabulate, xlsxwriter, soundfile, librosa, opencv-python, pillow, tqdm,
regex, tiktoken, wget, inflect, bitsandbytes. The temp files are in the system temp dir, not in the repo.

### Key versions (from the freeze file)

torch 2.11.0+cu130 (CUDA 13.0, arch list sm_75 ... sm_120 as reported by `torch.cuda.get_arch_list()`
in the first smoke run, a pure-metadata call), torchvision 0.26.0+cu130, torchaudio 2.11.0+cu130,
transformers 4.51.3, tokenizers 0.21.4, accelerate 1.15.0, bitsandbytes 0.50.2, diffusers 0.32.2,
peft 0.17.1, timm 1.0.30, safetensors 0.8.0, huggingface-hub 0.36.2, numpy 2.5.2, funasr 1.4.16,
modelscope 1.40.2, hyperpyyaml 1.2.3, conformer 0.3.2, jaxtyping 0.3.11, datasets 5.0.1, librosa 1.0.0,
lightning 2.6.6, opencv-python 5.0.0.93, decord 0.6.0, omni-diffusion 0.0.1 (editable).

## 4. Conflicts and deviations

| Item | Repo pin | What we did | Consequence |
|---|---|---|---|
| torch | none in Omni-Diffusion; GLM-4-Voice `requirements.txt` pins torch==2.3.0, torchaudio==2.3.0 (no sm_120) | Kept 2.11.0+cu130 | GLM-4-Voice requirements file was **not** installed. Its code imported fine on 2.11 (speech_tokenizer, flow_inference, cosyvoice.flow/hifigan). Audio numerical behaviour on new torch is untested. |
| transformers | `==4.51.3` | Installed 4.51.3 with torch 2.11 | Imports and config/tokenizer work. Generation/forward not run. GLM-4-Voice pins 4.44.1; ignored. |
| numpy | GLM-4-Voice pins 1.24.4 | numpy 2.5.2 | Imports OK. |
| deepspeed | in `requirements_ds_gpu.txt`; `import deepspeed` at `modeling_dream.py:738`, used at `:870` only for training gradient checkpointing | The sdist does not build on Windows (`No such file or directory: 'bin\deepspeed.bat'`). Created a **local shim** `.venv-omni\Lib\site-packages\deepspeed\__init__.py` mapping `deepspeed.checkpointing.checkpoint` to `torch.utils.checkpoint.checkpoint`. | Import works. Shim is not DeepSpeed; delete the folder if real DeepSpeed is ever installed. Inference does not reach it. |
| flash-attn | `tools/inference.py:103` passes `attn_implementation="flash_attention_2"` | Not installed, not compiled | **Not needed.** `DreamDecoderLayer` hard-codes `DreamSdpaAttention` (`modeling_dream.py:536`, with the flash-attn branch commented out), and the attention call uses `torch.nn.functional.scaled_dot_product_attention` with an explicit boolean mask and `is_causal=False` (about `:495-520`). Use `attn_implementation="sdpa"` (transformers would raise on `flash_attention_2` without the package). Smoke confirms the layer class is `DreamSdpaAttention`. |
| Not installed (in repo requirements) | pyworld==v0.3.4, WeTextProcessing (needs pynini), openai-whisper, onnxruntime, snac, flask(+restful), expecttest, tensorboardX, pyarrow, evaluate, zhconv/jiwer/zhon, gdown, fire, einx, loguru, lightning extras | Skipped | Only needed for the evaluation scripts and the text-normalisation front end; nothing on the import path failed without them. |
| `setup.py` packages | lists only `omni_diffusion` | Editable install maps the whole directory, so subpackages import | Fine for `-e`; a non-editable install would omit subpackages. |
| Import side effect | `import omni_diffusion` pulls in the data package, which imports GLM-4-Voice modules | Requires `PYTHONPATH=<GLM-4-Voice>;<GLM-4-Voice>/cosyvoice;<GLM-4-Voice>/third_party/Matcha-TTS` | Without it: `ModuleNotFoundError: speech_tokenizer`. |

## 5. Smoke result (CPU only, `CUDA_VISIBLE_DEVICES=""`, `HF_HUB_OFFLINE=1`)

Script: `C:\Users\Shlok\AppData\Local\Temp\omnismoke\smoke.py` (not in the repo; log `smoke.log` beside it).
Re-run after the crash with the stricter rule, exit 0:

- `import omni_diffusion` OK (editable install, from the clone).
- `AutoConfig.from_pretrained(snapshot, trust_remote_code=False)` returns `omni_diffusion.models.dream.configuration_dream.DreamConfig`: hidden 3584, 28 layers, vocab 176264, mask_token_id 151666.
- `DreamTokenizer.from_pretrained(snapshot)`: 176264 tokens; "Describe the image." encodes to [74785, 279, 2168, 13] and decodes back.
- `DreamModel(cfg)` on the meta device (`init_empty_weights`, no memory): **7.804 B parameters in the language model**, 15.61 GB in bf16, attention class `DreamSdpaAttention`. This count excludes the audio encoder, which I replaced with an empty stub **in the smoke script only**, because the real `AudioEncoder.__init__` downloads SenseVoiceSmall (finding 2). So the audio encoder's parameter count is not measured; the checkpoint index has 917 `model.audio_model.*` and 4 `model.audio_projection.*` tensors, so its weights are inside the snapshot.
- `MAGVITv2()` built on CPU: 95.4 M parameters (random init, no weights loaded).
- GLM-4-Voice decoder modules (`cosyvoice.flow.flow`, `cosyvoice.hifigan.generator`, `flow_inference`, `speech_tokenizer.modeling_whisper`) import OK on torch 2.11.
- Warning noise: "ffmpeg is not installed. torchaudio is used to load audio".

Not done: loading any weights, a forward pass, generation, anything on GPU, SenseVoiceSmall/GLM-4-Voice/MAGVIT weight loading, bitsandbytes import (it may touch CUDA at import; `uv pip check` is fine).

## 6. Fitting the 8B model in 12 GB (all UNVERIFIED, nothing below was run)

Source facts: HF snapshot is 15 GiB on disk (4 safetensors shards, bf16). LM = 7.80 B parameters (15.6 GB bf16),
of which embedding and lm_head are each 176264 x 3584 = 0.63 B (1.26 GB each in bf16). The audio encoder
(SenseVoiceSmall, checkpoint model.pt is 936 MB in the upstream repo, about 0.23 B parameters if fp32) is
extra and always constructed.
The GPU has 12227 MiB total (reported earlier by nvidia-smi); the desktop and other sessions use some.

Options, in the order I would try them:
1. **8-bit (bitsandbytes LLM.int8)**: about 7.8 GB of weights for the LM decoder layers plus embeddings; leaves about 3-4 GB for activations and a 512-1024 token context. Tight but plausible for short sequences. int8 inference is slow.
2. **4-bit NF4 with bf16 compute**: about 4 GB of weights if only the 28 decoder blocks are quantised and embeddings/lm_head are kept bf16 (2.5 GB), about 6.5 GB total. Comfortable, but 4-bit changes logits and could contaminate a sampler comparison; any result must name the quantisation.
3. **bf16 with layer offload** (`accelerate` `device_map` + `max_memory`, e.g. 9 GiB GPU / rest CPU): exact numerics, but RAM is about 9 GB free, the 15.6 GB of weights cannot be held in RAM; would need disk offload (very slow for an iterative diffusion sampler with many forward passes). Not recommended.
4. Whichever is used: `attn_implementation="sdpa"`, gradient checkpointing off for inference, batch 1, `torch_dtype=torch.bfloat16`.

Risks to check before any GPU use: (a) bitsandbytes 0.50.2 ships `libbitsandbytes_cuda130.dll` and
`cuda132.dll` but I have **not** verified its kernels run on sm_120 (needs a GPU test); (b) `from_pretrained`
quantisation of custom `DreamModel` with the nonstandard `AudioEncoder` submodule (funasr model) is untested,
so `llm_int8_skip_modules=["audio_model"]` (and probably `["audio_model","audio_projection","lm_head","embed_tokens"]`)
should be set; (c) the diffusion sampler runs many full forward passes, so time per sample is the real
cost, not memory; (d) loading shards uses CPU RAM peaks; load shard by shard with `low_cpu_mem_usage=True`.

## 7. Extra components and downloads (sizes from the HF API tree listings, 2026-10-27; none downloaded)

| Component | Repo | Size | Needed for | Notes |
|---|---|---|---|---|
| MAGVIT-v2 image tokenizer | `showlab/magvitv2` | 382 MB (`pytorch_model.safetensors`) | image encode and decode (`tokenizer_magvitv2.py`, `ImageProcessor`) | Required for any image task. |
| SenseVoiceSmall (speech feature encoder structure) | `FunAudioLLM/SenseVoiceSmall` | 944 MB (29 files; `model.pt` 936 MB) | Constructing `DreamModel` at all (finding 2), even for text/image | Weights are also inside the Omni-Diffusion checkpoint, so `model.pt` is probably redundant, but `snapshot_download` fetches everything. Possible to restrict with `allow_patterns` (excluding `model.pt`), but funasr `build_model` may look for it: unverified. Executes remote `model.py` (finding 2). |
| GLM-4-Voice speech tokenizer (encoder) | `THUDM/glm-4-voice-tokenizer` | 1458 MB | speech input | Not needed for text-image work. |
| GLM-4-Voice decoder (flow + hift) | `THUDM/glm-4-voice-decoder` | 527 MB (flow.pt 445, hift.pt 82) | speech output | `.pt` pickles + `config.yaml` (findings 3-4). Not needed for text-image work. |

Totals: text+image path = 382 MB + 944 MB = about 1.3 GB; plus speech = about 3.3 GB. All under 5 GB.
The README expects local paths under `../models/...`; our snapshot is in the HF cache, so pass explicit paths.

## 8. Next steps (for the lead)

1. Decide whether Paper 2 needs speech. If not, skip the two THUDM downloads and avoid the pickle/yaml caveats (findings 3-4).
2. Approve the 1.3 GB download of `showlab/magvitv2` and `FunAudioLLM/SenseVoiceSmall`; pin revisions, read the SenseVoiceSmall `model.py` before first load.
3. Write a loader script (outside the sampler code) that: sets `PYTHONPATH` as in section 4, `trust_remote_code=False`, `attn_implementation="sdpa"`, quantisation config, `HF_HUB_OFFLINE=1`, and logs GPU telemetry.
4. First GPU step, only with Shlok's go-ahead and `tools/gpu_guard.py`: one 4-bit load of the LM with a memory cap well below 12 GB and no other GPU job running, one forward pass, record peak memory. Then 8-bit.
5. Read `generation_utils.py` (`DreamGenerationMixin`, the sampler around lines 440-560 of the repo copy: classifier-free guidance with an unconditional mask, `transfer_index_t_s`, block mask) as the target of the Paper 2 sampler work before any experiment card.
6. Optional: ask whether to keep the two extra submodule clones or delete them.

## Addendum 2026-10-28 00:40 IST (lead): SenseVoiceSmall security read
Snapshot `FunAudioLLM/SenseVoiceSmall` 3847d57b6bdf2dd8875cb1508d2af43d80a16bf7 (downloaded 2026-10-27 23:48): no Python model
code (only `demo.py`), `config.yaml`, `model.pt` (936 MB pickle), BPE model, `am.mvn`, `requirements.txt`.

**Blocking finding.** Omni-Diffusion builds it with `AutoModel.build_model(model=..., trust_remote_code=True)`
(`omni_diffusion/models/dream/modeling_sensevoice.py:731` and `:1082`). In funasr 1.4.16, `trust_remote_code=True` does two things
(`funasr/download/download_model_from_hub.py:103-115`):
1. If the snapshot has a `requirements.txt`, it **pip-installs it** (`install_model_requirements.install_requirements`). This one asks
   for `numpy<=1.26.4`, `gradio`, `modelscope`, `torch>=1.13` and `torchaudio`. That would downgrade numpy and add packages inside
   `.venv-omni` at model-build time.
2. It runs `import_module_from_path("model")`, so a module named `model` is imported from wherever Python looks (the snapshot has none).

`model.pt` is read with `torch.load(path, map_location=...)` (`funasr/train_utils/load_pretrained_model.py:39`) without an explicit
`weights_only`. torch 2.11 defaults to `weights_only=True`, so a pickle with arbitrary objects fails instead of executing.

**Required before the first load:** build SenseVoice with `trust_remote_code=False` (funasr registers `SenseVoiceEncoderSmall`
itself), pass the local snapshot path instead of calling `snapshot_download`, and set `HF_HUB_OFFLINE=1`. Do it as a small local
patch to the two lines above in the clone (recorded with `git diff`), or as a monkeypatch in our loader. Run from a clean working
directory. After the first load, check with `uv pip freeze` that `.venv-omni` is unchanged against `freeze-2026-10-27.txt`.
