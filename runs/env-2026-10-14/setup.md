# Environment and smoke tests: UniDisc (C1) and MDLM-OWT (C2), 2026-10-14

Agent: lab-engineer. Brief: make two frozen checkpoints runnable on the laptop GPU and measure their cost; no experiments.
Evidence tags follow `research/CONTRACT.md`: E3 = code read at the pinned SHA, E4 = reproduced here (artifact path given).
Everything below was run from `runs/env-2026-10-14/`; paths are relative to it unless absolute. No ledger rows were written.

## 0. Status

| Item | Status | Where |
|---|---|---|
| C1 UniDisc interleaved 1.4B | done: (a) joint generation, (b) marginals, (c) timing batch 1/4/8 | `smoke_unidisc/`, `timing.json` |
| C2 MDLM-OWT | done: sample L=1024, marginals, timing batch 1/8/32, gen-PPL evaluator located and timed | `smoke_mdlm/`, `timing.json` |
| C3 LLaDA-8B-Instruct | NOT done. Weights are downloading in the background at about 2 MB/s (16.0 GB, roughly 2.5 h); no code was run on them. `scripts/get_llada.sh` resumes the download. | `logs/get_llada.log` |

### Setup surprises that matter for every later job (read this first)

1. **System commit is almost exhausted by other sessions, and on this machine CUDA memory is charged to it.** At the start of the
   work Windows reported 118 of 127 GB committed; about 350 `node.exe`, 38 `claude.exe` and 25 `python.exe` processes
   (stale MCP helpers started 2026-10-06 to 2026-10-13) hold about 60 GB. Measured: each GB of `cudaMalloc` consumed about 1 GB of free commit
   (free commit 7.83 GB before, 3.76 GB after a 4 GB allocation); with 1 GB chunks the process could only allocate 5 GB of "VRAM" even though
   `nvidia-smi` showed 12 GB free, and with 16 GB free commit it could allocate 16 GB (the driver spills past 12.8 GB into system memory).
   Free commit swings between about 1 and 17 GB within minutes. CPU allocations above about 5 GB crash Python with an access violation
   (`nn.Linear.__init__`), and hf-xet crashed with "memory allocation failed". Consequences: (a) a CUDA "OOM" with several GB reported free is
   a commit failure, not VRAM; (b) `scripts/common.py::wait_commit` gates each heavy stage on free commit and `commit_free_gb()` is logged in every result
   (`free_system_commit_gb` in OOM records); (c) numbers in `timing.json` are valid timings, but the OOM boundaries may move if commit is freed.
   I did not kill any process or change the pagefile (not mine to touch). Recommended before long runs: reboot, or close the stale processes,
   then re-run `scripts/mdlm_smoke.py` and `scripts/unidisc_smoke.py --stage c` to get commit-independent OOM boundaries.
2. **The network delivers about 1-2 MB/s**, with one DNS failure and a hung `uv`. A 1.9 GB torch wheel, the 5.6 GB UniDisc checkpoint and the 3.2 GB GPT-2 large took about 1.5 h
   of wall time in total. `scripts/pardl.py` (resumable range downloader, 8-16 connections) was needed; hf-xet crashed on this machine. Files were checked against the HF LFS SHA-256.
3. **Disk**: free space on C: swung between 0.06 GB and 110 GB during the session. The cause is `docker_data.vhdx` (22 GB, Docker Desktop with a Supabase stack, not mine) growing and shrinking.
   For about two minutes the disk was effectively full while my download was running; I stopped the download and nothing was lost.
4. System Python 3.14 cannot run either repo (UniDisc needs Python below 3.13; `transformers` 5.x breaks the MDLM remote code). Everything uses the venv below.

## 1. Environment

* venv: `C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv` (CPython 3.12.14 from uv, created with the interpreter path because `uv venv --python 3.12` hit a broken minor-version link). Activate: `.venv\Scripts\python.exe`.
* Lock file: `env-lock.txt` (149 lines, `uv pip freeze`). Key pins: torch 2.11.0+cu130, torchvision 0.26.0+cu130, transformers 4.49.0, huggingface-hub 0.36.2,
  tokenizers 0.21.4, accelerate 1.5.2, diffusers 0.32.2, datasets 3.2.0, tensordict 0.14.3, numpy 2.5.2, lightning 2.6.6, hydra-core 1.3.7, omegaconf 2.3.1, torchmetrics 1.9.0, torchtnt 0.2.4, image-utilities 0.0.3.
  GPU/driver: RTX 5070 Ti Laptop (12.82 GB reported, sm_120), driver 595.71, CUDA 13.0 runtime in the torch wheel. No triton, no flash-attn, no nvcc.
* Install commands (exact): torch from the downloaded wheel
  `uv pip install --python .venv/Scripts/python.exe C:/Users/Shlok/.cache/dlm_dl/torch-2.11.0+cu130-cp312-cp312-win_amd64.whl torchvision==0.26.0 --extra-index-url https://download.pytorch.org/whl/cu130`, then
  `uv pip install transformers==4.49.0 "huggingface_hub>=0.26,<1.0" einops hydra-core omegaconf lightning torchmetrics datasets==3.2.0 timm requests rich pandas scikit-learn safetensors sentencepiece protobuf accelerate~=1.5.2`, then
  `diffusers~=0.32.2 tensordict torchtnt jaxtyping wandb image_utilities==0.0.3.* typer ml_collections torchinfo lovely-tensors ipdb ipython braceexpand h5py pynvml lightning_utilities fastapi uvicorn pydantic hf_transfer peft webdataset submitit evaluate ftfy simple_slurm opencv-python-headless clean-fid psutil`.
  (UniDisc pins torch 2.6 cu124, which has no Blackwell kernels; torch 2.11 cu130 is the system version and works.)
* Third-party code, cloned to `C:\Users\Shlok\Downloads\Multi-Modality Language model\models\third_party\` (git-ignored by `models/`), **unmodified** (`git status` clean):

  | Repo | URL | Commit used | Licence |
  |---|---|---|---|
  | UniDisc | https://github.com/alexanderswerdlow/unidisc | `3ee3e47a9e64bac2fdca59957726f14723371ced` (HEAD of `main`, pushed 2025-04-02) | **none stated**: no LICENSE file in the root, GitHub API `license: null` |
  | its submodules (shallow) | LlamaGen fork `alexanderswerdlow/LlamaGen` @ `c4cc58b`; Lumina-mGPT fork @ `5888993`; Show-o @ `b00d96e`; 1d-tokenizer @ `bdec006` | as pinned by UniDisc | LlamaGen: MIT (its LICENSE); Show-o and 1d-tokenizer have LICENSE files; Lumina-mGPT fork has none |
  | MDLM | https://github.com/kuleshov-group/mdlm | `c112c526d193436838c98d81455ee51f90309470` (2025-09-29) | Apache-2.0 (LICENSE, GitHub API) |
  | ReMDM (read only, for sampler settings) | https://github.com/Kuleshov-group/remdm | `f830d659fb98d9b2c79ff71bfa12d578312b688a` | LICENSE file present (Apache text) |

* Weights, all in the Hugging Face cache `C:\Users\Shlok\.cache\huggingface\hub` (hard links, no symlinks on this account):

  | Repo ID (verified on the HF API) | Revision | Files used | Licence |
  |---|---|---|---|
  | `aswerdlow/unidisc_interleaved` | `2b344ca856bd108b52a2d022a3463dace131249f` (2025-03-31) | `unidisc_interleaved.pt` 5,627,633,316 B (SHA-256 `578ff991...3654c`, matches the LFS oid; fp32 weights), `vq_ds16_t2i.pt` 287.9 MB (SHA-256 `0e21fc13...d4cb`) | **none stated**: no `license` tag, model card has only `pipeline_tag`. The tokenizer checkpoint is LlamaGen's VQ-16 (MIT code). |
  | `kuleshov-group/mdlm-owt` | `d0958fa851335ece6c15260ce0025f030673c0fb` (2026-04-11) | `model.safetensors`, `modeling_mdlm.py`, `configuration_mdlm.py`, `config.json` | Apache-2.0 (tag `license:apache-2.0`) |
  | `openai-community/gpt2-large` (alias `gpt2-large`) | `32b71b12589c2f8d625668d2335a01cac3249519` | `model.safetensors` 3.25 GB (SHA-256 matches), tokenizer files | MIT |
  | `gpt2` (tokenizer only) | `607a30d783dfa663caf39e06633721c8d4cfcd7e` | tokenizer files | MIT (not re-verified) |
  | `NousResearch/Llama-2-7b-hf` (tokenizer files only) | `8efe6c9b93655b934e27bd9981e3ec13e55aee9d` | `tokenizer*`, `config.json` | no licence tag on the mirror; Llama 2 Community Licence applies to the original (not verified here) |
  | `GSAI-ML/LLaDA-8B-Instruct` (C3, partial) | `08b83a6feb34df1a6011b80c3c00c7563e963b07` | 6 safetensors shards, 16.04 GB in total | MIT (tag) |

  The brief's repo IDs `aswerdlow/unidisc_interleaved` (5.63 GB, licence not stated) and `kuleshov-group/mdlm-owt` are confirmed. The official UniDisc code repository is `alexanderswerdlow/unidisc` (named by the HF card); `aswerdlow/unidisc` does not exist on GitHub.
* Disk used: venv 3.4 GB, UniDisc 5.9 GB, GPT-2 large 3.3 GB, MDLM 0.7 GB, torch wheel kept in `C:\Users\Shlok\.cache\dlm_dl\` 1.9 GB, repos 0.3 GB.

Compatibility shims (all in `scripts/`, none in the repos):
`shims/flash_attn/` (pure-PyTorch stand-in for the three flash-attn calls MDLM's HF and repo code make: `apply_rotary_emb_qkv_`, `flash_attn_varlen_qkvpacked_func`, plus `flash_attn_func` for UniDisc; there is no Windows wheel);
`common.stub_modules` (empty `causal_conv1d`/`mamba_ssm` modules so `models/__init__.py` of MDLM imports); `os.sched_getaffinity` stand-in (used at import time by both repos);
UniDisc: `unidisc_smoke.patch_attention` replaces `flex_attention(block_mask)` by SDPA (see 2.6), `Accelerator(mixed_precision="no")` instead of `"bf16"` (see 2.7), default device `cuda` + `torch.load(mmap=True, weights_only=True)` while building, to avoid a 5.6 GB CPU copy.

## 2. C1: UniDisc (arXiv 2503.20853, AW0261)

Entry points: `scripts/unidisc_setup.py` (config + model, mirrors `demo/inference.py::setup`), `scripts/unidisc_smoke.py` (stages a-e), `scripts/unidisc_precision_check.py`.
Command: `.venv\Scripts\python.exe scripts\unidisc_smoke.py --stage a,b,d --res 1024` (stage c = timing, e = CFG switch). Logs: `logs/unidisc_smoke_1024_abd.log`, `logs/unidisc_timing_c.log`, `logs/unidisc_stage_e.log`, `logs/unidisc_precision_check.log`.
Config: hydra `experiments=[large_scale_train,large_scale_train_high_res_interleaved,eval_unified,large_scale_high_res_interleaved_inference]` exactly as `demo/demo.sh`; resolved config saved as `smoke_unidisc/resolved_config.yaml`.

### 2.1 What was run (E4)

* Model: `models.dit.DIT`, 1,406,870,785 parameters (24 blocks, width 2048, 16 heads, RMSNorm, QK-norm, 2D RoPE for image tokens, modality embedding), no time conditioning (`force_null_sigma: true`). Loaded in bf16 (checkpoint is fp32): 2.82 GB VRAM, load 9.7-12.3 s (`timing.json`, `info_by_run`).
* (a) Joint generation, 1024 px, seed 0, official `maskgit` sampler at the inference experiment's defaults (50 steps, CFG 3.0, r_temp 4.5): **49.8 s, peak 6.75 GB**.
  Input row: observed system prompt plus the fixed prompt "a photo of a red bicycle leaning against a brick wall"; 32 mask tokens (text) and 4,096 masked image tokens generated together.
  Outputs: `smoke_unidisc/joint_image_1024px.png` (a coherent red bicycle against a brick wall, viewed), `smoke_unidisc/joint_text_1024px.txt` (the 32 generated text tokens read "(c) photoshiko shui copyright (c) 1 2 3 / 02 a / 12 3 / 15 a", web-caption debris, as expected for 32 free tokens), `smoke_unidisc/joint_tokens_1024px.json`, `smoke_unidisc/layout_1024px.json`.
  The text-side result is a plumbing check only; the image shows that checkpoint, tokenizer offset, VQ decoder, CFG and sampler are wired correctly.
* (b) Marginals on a partially masked interleaved state (prompt observed, 25% of the other positions revealed from the sample): `smoke_unidisc/marginals_summary_1024px.json`. Shape (1, 4171, 48385). Masked text positions put mass 0.998 on text ids and 0 on image ids; masked image positions put mass 1.000 on the 16,384 image ids and 0 on text ids; the mask id has probability 0; observed positions are one-hot. Mean top-1 probability 0.18 (text), 0.042 (image); mean entropy 5.0 and 6.5 nats.
  The log-probabilities come out in bf16, so row sums deviate by up to about 2e-3 (0.9977 to 1.0009 in the summary).
* (c) Forward timing with the SDPA attention patch (2.6), synthetic rows (text then image, 50% random masked), median of 3 after 1 warm-up, `smoke_unidisc/smoke_unidisc_bf16_1024px_stages_c.json`:

  | Row length | Batch | Plain pass: s, peak GB | CFG pass (2x effective batch): s, peak GB |
  |---|---|---|---|
  | 1,536 (512 text + 1,024 image tokens, 512 px) | 1 | 0.129, 3.13 | 0.301, 3.42 |
  | | 4 | 0.589, 4.02 | 1.17, 5.21 |
  | | 8 | 1.167, 5.21 | 2.575, 7.59 |
  | 5,120 (1,024 text + 4,096 image tokens, 1,024 px) | 1 | 0.606, 3.82 | 1.252, 4.81 |
  | | 4 | 2.50, 6.79 | 4.969, 10.76 |
  | | 8 | 5.164, 10.76 | OOM (effective batch 16; logits alone are 7.9 GB in bf16) |

  Cost model from these: about 0.12 s per 1,000 tokens per sequence per pass. A 50-step joint sample at 1024 px with CFG costs about 50 s; at 512 px about 15 s (estimate from the 0.30 s pass, not measured). Peak VRAM is dominated by the full-vocabulary logits (B x L x 48,385), not the 2.8 GB of weights.
* Precision (`smoke_unidisc/precision_check_256px.json`, 256 px rows, L=331, batch 1): bf16 weights against the checkpoint's own fp32 weights with bf16 autocast (the demo's configuration), same token states. Top-1 agreement 0.972 (288 masked positions, prompt only) and 0.962 (133 positions, half revealed); mean total-variation distance 0.0055 and 0.0164; mean absolute entropy difference 0.059 and 0.125 nats. bf16 weights are acceptable for marginal work but not identical.
* (ii) functional check of a custom commit order (stage d, `smoke_unidisc/smoke_unidisc_bf16_1024px_stages_abd.json`): 12 steps of 4 positions each, committed sets equal the prescribed sets (`true`); flex attention against SDPA on random q,k,v with a single-document block mask: max abs difference 4.3e-4 (fp32).
* CFG switch (stage e, `smoke_unidisc/smoke_unidisc_bf16_1024px_stages_e.json`): with `eval.cfg=3.0` the guided marginal makes one network call on batch 2 (conditional and unconditional stacked); with `eval.cfg=0.0` or `null` one call on batch 1, identical to the unguided marginal (max difference 0.0).

### 2.2 How UniDisc lays out a text-and-image row (iv; E3 `demo/inference_utils.py::messages_to_batch`, `unidisc/tokenizers/tokenize_interleaved.py`, E4 `layout_1024px.json`)

* Tokenizer: Llama-2 SentencePiece (`NousResearch/Llama-2-7b-hf`, slow tokenizer, `add_eos_token=True`), text vocab 32,001: ids 0-31999 are Llama tokens (0 = `<unk>` = pad, 1 = `<s>`, 2 = `</s>`, 811 is re-purposed as the `<image>` marker) and **id 32000 is the mask token** (`<m>` in the demo). Image tokens are ids 32,001 + code, code in [0, 16384), so the joint vocabulary is 48,385. One mask id serves both modalities; the modality of a position is given by a separate `modality` tensor (0 text, 1 image), passed to the network (modality embedding) and to the output head, which masks the other modality's vocabulary slice.
* Image tokenizer: LlamaGen **VQ-16** (`vq_ds16_t2i.pt`), downsample 16, **codebook 16,384**, embedding dim 8. Resolution r gives (r/16)^2 tokens: 256 px = 256, 512 px = 1,024, 768 px = 2,304, 1024 px = 4,096 (the RoPE tables exist for exactly these four sizes). Tokens are in raster order and use 2D RoPE; text uses 1D RoPE over `txt_length` = 1,024.
* Row (text-to-image with masked caption tail), from `layout_1024px.json`: `<s> You are a highly intelligent multimodal AI with the ability to analyze and generate images. </s> <s> {prompt} <m>*32 </s> <s> ' ' <image> {4096 image tokens} </s>`. Positions: bos at 0, 23, 72; masked text 39-70; image marker 73; image tokens 74-4169; eos 4170; length 4,171 (config maximum 5,120 = 1,024 + 4,096). Images are placed last by the demo (`force_reorder`). Everything is in one document, `sample_ids` all 0.
* Attention is full (bidirectional) within a document; across documents/padding, positions with different `sample_ids` do not attend. For single-document rows this is full attention, which is why the SDPA replacement is exact up to rounding.
* Classifier-free guidance **needs a second network pass**: `model_eval._ddpm_forward` (E3, model_eval.py L1761-1834) builds `x_uncond` by replacing every observed token with the mask id, stacks `[x, x_uncond]` along the batch (or two calls if `eval.split_cfg_batches`), and combines logits as `(1+w)*logit_cond - w*logit_uncond` with `w = cfg*(1-t)` (`get_cfg_weight`, L1737; `t` runs 1 to 0, so guidance fades as decoding proceeds). It is applied only when `eval.cfg` is not null, some token is observed (`x0_unmask.sum() > 0`) and `w > 0` somewhere. Cost: 2x batch per step (table above).

### 2.3 (i) How to get p(x^i | s) for any masked state

```python
import sys; sys.path.insert(0, r"<worktree>\runs\env-2026-10-14\scripts")
import unidisc_setup as U, unidisc_smoke as S
cfg = U.make_config(["eval.visualize_sample=false"]); S.patch_attention()
model, cfg = U.build_model(cfg)                       # bf16 weights, ~2.8 GB
st = S.build_state(model, cfg, 1024, joint=True)      # dict: x0, unmask (bool), modality, sample_ids, attention_mask, layout
x = S.prior(model, st)                                # observed tokens kept, everything else = mask id 32000
p = S.marginals_raw(model, x, st)                     # [B, L, 48385]; exp of model.forward(...), no guidance
pg = S.marginals_guided(model, x, st, t=0.5)          # what the sampler sees: CFG-combined if eval.cfg > 0 (2x cost)
```
`model.forward(x=x, sigma=None, modality=..., sample_ids=..., block_mask=True)` returns log-probabilities from the SUBS parameterisation (`model.py` L621-658): the mask id and the other modality's slice are forced to -inf, rows are normalised by a log-sum-exp, and **observed positions are replaced by a one-hot**. Marginals of any state: put the mask id 32000 at the positions to hide and set `x0_unmask`/`unmask` accordingly (only used for CFG). To build a state from your own text and image tokens, build the row with `messages_to_batch` (it handles templates and VQ encoding) or directly: text ids as is, image ids = code + 32001, `modality` 0/1, `sample_ids` zeros.
Memory: the full tensor is B x L x 48,385 bf16 (0.5 GB per sequence at L=5,120) and the SUBS step makes several copies; slice the logits to the positions you need if batch matters.

### 2.4 (ii) Custom commit order

The official `maskgit` sampler (`model_eval.py` L3046, schedule `adap_sche` L2964, E3) does not accept an order. Per step it (1) takes `p_x0 = _ddpm_forward(...)` for all positions (text and image pooled), (2) draws a token per position with `torch.multinomial` (temperature 1, no top-p), (3) scores each masked position `log p(sampled token) + r_temp * Gumbel * t` (`np.random.gumbel`, `r_temp` = 4.5, `t` from 1 to 0), (4) commits the top `schedule[step]` of them, where `schedule` splits the number of masked positions by the arccos schedule (`arccos(r)/(pi/2)`, normalised). Ties at the threshold can commit more than k.
To impose an order, use `S.ordered_commit(model, st, order, k_per_step, guided=...)`: one network call per step (`_ddpm_forward` if `guided`, so CFG is included), sample only the positions in `order[pos:pos+k]` from their marginals, leave the rest masked. Tested (2.1). For a modality schedule (text first, image first, alternating) construct `order` from `st["modality"]` and the masked positions. Passing a custom `schedule` only changes how many positions are committed per step, not which.

### 2.5 (iii) Defaults and how to switch them off (E3 `resolved_config.yaml`, `model_eval.py`)

| Setting | Default | Switch off / change |
|---|---|---|
| Sampler | `sampling.predictor=maskgit` (others in `_sample`: `first_hitting`, `maskgit_nucleus`, `ddpm`, `ddpm_cache`, `ddpm_tweedie`, `analytic`) | `sampling.predictor=...` |
| Steps | 50 (`sampling.steps` and `sampling.max_sampling_steps` must be equal: `_validate_configuration` asserts). The demo server's request defaults are 35 steps, CFG 3.5, resolution 256; its UI shows 32 steps, CFG 2.5 | override both keys |
| Randomness | token: multinomial from the marginal; ordering: Gumbel noise with `maskgit_r_temp=4.5` scaled by `t`, from the global NumPy RNG | `eval.maskgit_r_temp=0` makes the order deterministic given the tokens (tokens still sampled); seed with `torch.manual_seed` and `np.random.seed` |
| Temperature, top-p | **not used by `maskgit`**. The demo's `top_p=0.95`, `temperature=0.9` only take effect in `maskgit_nucleus` and the AR sampler; config keys `eval.top_p`, `eval.temperature` are unset | n/a |
| CFG | `eval.cfg=3.0` in this experiment (null in the base config), weight `cfg*(1-t)`, needs the second pass | `eval.cfg=0.0` or `null`: single pass (verified, stage e) |
| Modality dropout | training only (`mask_entire_modality`) | n/a |
| Final step | `sampling.noise_removal=true`: after the loop one extra pass without CFG and `argmax` fills any position still masked | `sampling.noise_removal=false` |
| Attention caching | `eval.attention_caching=false` | leave off (needs real flex attention) |
| Precision | demo: fp32 weights, `Accelerator(mixed_precision="bf16")` (logits returned in fp32). Here: bf16 weights, `mixed_precision="no"`, bf16 logits (`trainer.force_bf16_eval=true`, a repo option) | `U.build_model(cfg, bf16=False)` keeps fp32 weights (6.3 GB VRAM) |

### 2.6 Problems hit and fixes (UniDisc)

* `DIT` construction crashed with an access violation: it builds 5.6 GB of fp32 parameters on the CPU, above the commit-limited allocation ceiling. Fix: default device `cuda` during construction.
* The checkpoint is read inside `set_accelerator`, not in `Diffusion.__init__`; my first `mmap` wrapper missed it, leaving 7 GB of private memory after the build. Fix: patch `torch.load` around both calls (`unidisc_setup.build_model`); after the fix private bytes fell from 14.3 GB to 7.2 GB.
* `torch.nn.attention.flex_attention` runs eagerly without triton and would materialise B*H*L*L scores; replaced by SDPA for single-document rows (check in stage d). Do not use that patch for packed rows with several documents or padding.
* `Diffusion.decode_sampling` writes text-on-image visualisations using `/usr/share/fonts/...`; the script grabs the final token row instead and decodes with `decode_latents` and the Llama tokenizer.
* `_sample` is wrapped by `try_except`, which swallows exceptions and returns `None` (my first OOM showed up as a `KeyError`); read `smoke_unidisc/failed_attempts/exception_*.out` and the log.
* `sampling.steps` must equal `sampling.max_sampling_steps`.
* Failed or abandoned runs, kept on disk: `logs/unidisc_smoke_1024_abd_try1_OOM_commit.log` (two OOMs at 1.5 GiB with 6 GiB reported free: commit), `logs/unidisc_smoke_1024_a.log` (stopped while waiting for commit), `logs/unidisc_dev_*.log` (random-weight plumbing tests, outputs deleted), `logs/unidisc_probe.log`, `smoke_unidisc/_prev_v1_assistant_turn_layout/` (first layout: masked tokens in an assistant turn; the model filled it with `<unk>`; replaced by the demo's own `<m>`-in-user-turn layout), `smoke_unidisc/failed_attempts/`.
* The 4,096-token layout was chosen because it is the official inference experiment (`large_scale_high_res_interleaved_inference`). The demo server itself defaults to 256 px.

## 3. C2: MDLM trained on OpenWebText (arXiv 2406.07524)

Entry point: `scripts/mdlm_smoke.py` (`--steps 128 --long-steps 1000`). Log: `logs/mdlm_smoke.log`; results `smoke_mdlm/smoke_mdlm.json`, `smoke_mdlm/sample_L1024.txt`, `smoke_mdlm/sample_L1024_tokens.json`.
It goes through the official class: `diffusion.Diffusion` with `backbone=hf_dit` and `eval.checkpoint_path=kuleshov-group/mdlm-owt` (the repo's own route for this HF checkpoint, `main._load_from_checkpoint`), `ema=None` (as `eval.disable_ema`), then `restore_model_and_sample` and `compute_generative_perplexity`, as in `main.generate_samples`.

### 3.1 Results (E4)

* Model: 169,627,218 parameters (12 blocks, width 768, 12 heads, context 1,024), vocabulary 50,258 = GPT-2 (50,257) + mask id **50257**; no time conditioning; fp32 weights (0.68 GB), blocks and head hard-code bf16 autocast. Load 3-18 s.
* Sample, L=1024, seed 1, repo defaults (`ddpm_cache`, 128 steps): **3.5-4.5 s** (two runs), peak 1.41 GB; 1,000 steps: **18.1-18.6 s** (caching makes the cost less than linear in steps). Text in `smoke_mdlm/sample_L1024.txt` (fluent OpenWebText-style prose with `<|endoftext|>` markers).
* Forward at L=1024, 50% random masking, median of 5 (`timing.json`, `mdlm.forward_L1024`):

  | Batch | Full `Diffusion.forward` (backbone + SUBS) s, peak GB | Backbone only s, peak GB |
  |---|---|---|
  | 1 | 0.021, 1.08 | 0.016, 1.08 |
  | 8 | 0.089, 2.34 | 0.079, 1.86 |
  | 32 | 0.408, 7.28 | 0.325, 4.52 |

  (The first attempt, `logs/mdlm_smoke_try1.log` and `smoke_mdlm/_try1_smoke_mdlm_commit_limited.json`, hit commit-limited OOMs at batch 8 and 32; rerun succeeded.) Throughput is about 80 sequences per second at batch 32.
* Generative-perplexity evaluator: the repo's `Diffusion.compute_generative_perplexity` (`diffusion.py` L515), **GPT-2 large**, fp32, retokenised with the GPT-2 tokenizer, context 1,024, tokens after the first EOS dropped, `torch.exp(mean NLL)` via torchmetrics. Both MDLM (`configs/config.yaml` L53) and ReMDM (`configs/config.yaml` L60) set `gen_ppl_eval_model_name_or_path: gpt2-large` (Llama-2 is the alternative in the comment); `eval_retokenize` has a `llama2` branch with a 4,096 context. One sample took **4.5-5.4 s including loading GPT-2 large**, peak 4.65 GB, value 77.17 for that single sample (plumbing check only, not a quality measurement).
  Settings in the ReMDM scripts for the MDLM baseline (`remdm/scripts/mdlm.sh`, E3): `sampling.steps=1024` (T), `nucleus_p=0.9`, batch 1, `sampling.num_sample_batches=5000`, same GPT-2 large evaluator. ReMDM also replaces fp32 Gumbel noise by fp64 (`diffusion.py` L26-31) and adds MAUVE and entropy.

### 3.2 (i) Marginals

`diff.forward(x, sigma)` (`diffusion.py` L312, SUBS parameterisation L261): the mask id gets -1e6 added, logits are normalised by a log-sum-exp, observed positions become one-hot; `time_conditioning=false` so `sigma` is ignored (pass zeros). `p = diff.forward(x, zeros(B)).exp()` has shape [B, 1024, 50258]; use `mdlm_smoke.marginals`.
**Precision warning (E4, `smoke_mdlm.json`, `marginals` and `marginals_fp32_check`)**: the DIT blocks and the output layer run under a hard-coded `torch.cuda.amp.autocast(dtype=torch.bfloat16)`, so the returned probabilities are bf16 and row sums are 0.926 to 1.070 on masked positions. Disabling every autocast (`mdlm_smoke.marginals_fp32`, 0.035 s per sequence instead of 0.021 s) gives row sums 1 +/- 2e-6, but on a 50%-masked state the two versions differ materially: top-1 agreement 0.785 over 525 masked positions, max absolute probability difference 0.57, mean absolute entropy difference 0.32 nats. The checkpoint was trained in bf16 mixed precision, so the bf16 marginals are the ones the model was trained with, and the fp32 ones are an out-of-distribution evaluation. Pick one precision for a preregistered analysis and state it; any CMI or entropy estimate depends on it at the 0.3-nat level.

### 3.3 (ii) Custom commit order

Official sampler (`_ddpm_caching_update`, L592, E3): loglinear noise, so `move_chance_t = t`; one network call gives `p_x0`, `q_xs = p_x0*(t-s)`, mask probability `s`, each masked position independently draws from `q_xs` (Gumbel-max), so the set committed per step is random with expected fraction `(t-s)/t`; no confidence ordering exists. `ddpm_cache` reuses `p_x0` when nothing changed in the last step (valid because there is no time conditioning), so NFE is below `steps`. Order cannot be set; use `mdlm_smoke.ordered_unmask(m, order, k_per_step)` (one forward per step, samples only the chosen positions; tested: committed sets equal prescribed sets for 16 steps of 4 positions). ReMDM adds remasking samplers (`remdm-cap/rescale/conf/loop`) in the other repo, not run here.

### 3.4 (iii) Defaults

`sampling.predictor=ddpm_cache`, `sampling.steps=128` in the MDLM repo config (the ReMDM scripts use 1,024), `noise_removal=true` (a final greedy `argmax` pass over any position still masked), **no temperature, no top-p, no guidance** in the MDLM sampler. Sampling is exact ancestral sampling from the marginals through fp32 Gumbel-max with `torch.rand_like` (global torch RNG, seed with `torch.manual_seed`). Nucleus sampling and fp64 Gumbel exist only in the ReMDM repo (`sampling.nucleus_p`, default 1.0 = off in its `configs/config.yaml`, 0.9 in its scripts; its default `sampling.steps` is also 128). Switch off noise removal with `sampling.noise_removal=false`.

### 3.5 Problems hit and fixes (MDLM)

* `transformers` 5.3 fails on the HF remote code (`all_tied_weights_keys`): use 4.49.
* The HF and repo code import `flash_attn` (no Windows wheel): `scripts/shims/flash_attn` (equivalence not separately tested; the sample text is fluent and the marginals are well-formed, which is only indirect evidence).
* `models/__init__.py` imports `dimamba` (needs `mamba_ssm`, `causal_conv1d`): stubbed; `dataloader.py` evaluates `os.sched_getaffinity` at import: stand-in.
* A first run of the stub raised `AttributeError: 'function' object has no attribute 'endswith'` because the stub answered every attribute, including `__file__`; fixed (dunder names raise).

## 4. C3: LLaDA-8B-Instruct (not done)

Verified: `GSAI-ML/LLaDA-8B-Instruct`, revision `08b83a6f...`, licence MIT, custom code (`modeling_llada.py`), six safetensors shards of 2.1 to 3.0 GB (16.04 GB). `bitsandbytes` 0.50.2 has a Windows wheel. The download was started with `scripts/get_llada.sh` into `C:\Users\Shlok\.cache\dlm_dl\llada\` (first shard 2.1 GB at 1.9 MB/s when I stopped). Remaining work after it finishes: place the files in an HF snapshot directory, load in 4-bit (`BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)`), time one forward at L=256. No full-precision reference fits in 12 GB, so no quantisation comparison would be possible except 4-bit against 8-bit. Nothing has been measured; no number is claimed.

## 5. Index of artifacts

* `timing.json`: all timings and VRAM numbers (`mdlm`, `unidisc`); `env-lock.txt`.
* `smoke_unidisc/`: `joint_image_1024px.png`, `joint_text_1024px.txt`, `joint_tokens_1024px.json`, `layout_1024px.json`, `marginals_summary_1024px.json`, `precision_check_256px.json`, `resolved_config.yaml`, per-stage JSON, `failed_attempts/`, `_prev_v1_assistant_turn_layout/`.
* `smoke_mdlm/`: `smoke_mdlm.json`, `sample_L1024.txt`, `sample_L1024_tokens.json`, `_try1_smoke_mdlm_commit_limited.json`.
* `scripts/`: `common.py` (timing, commit gate, stubs), `mdlm_smoke.py`, `unidisc_setup.py`, `unidisc_smoke.py`, `unidisc_precision_check.py`, `finalize.py`, `pardl.py`, `download_weights.py`, `get_llada.sh`, `shims/flash_attn/`.
* `logs/`: every run, including failed and abandoned ones.
* Not committed to git (the brief did not ask for it); `*.pt` files are git-ignored, so JSON copies of the token dumps are provided.
