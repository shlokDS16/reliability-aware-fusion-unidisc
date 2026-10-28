"""Loader of the Omni-Diffusion stack for the family R adapter. Runs in `.venv-omni` only. Everything omni-specific is imported inside functions.

Decisions (debate DECISION-R1 item 6, OMNI-DIFFUSION-SETUP-2026-10-27 sections 2, 4, 6 and the SenseVoice addendum):
  * `trust_remote_code=False`, `HF_HUB_OFFLINE=1`, local snapshot paths only (nothing is downloaded, nothing from the snapshot's .py files is executed: the repo classes
    registered by `omni_diffusion.models.dream` are used);
  * the audio encoder is a STUB: `DreamBaseModel.__init__` builds `AudioEncoder()` unconditionally (modeling_dream.py:763) and the real one downloads and builds SenseVoiceSmall
    (modeling_sensevoice.py:1080-1082, trust_remote_code=True inside funasr). Text and image never reach it (`audios is None`, modeling_dream.py:793-806). The stub raises if its forward is called;
  * `DreamPreTrainedModel.from_pretrained` (modeling_dream.py:634-701) does `_model, _ = super().from_pretrained(...)` inside a try/except, which fails to unpack and then loads the
    whole model a SECOND time. We call `PreTrainedModel.from_pretrained` directly (once);
  * 4-bit NF4, bf16 compute, no double quantisation; `llm_int8_skip_modules` = audio_model, audio_projection, lm_head, embed_tokens. Checked on the meta-device skeleton with
    transformers' own `replace_with_bnb_linear`: exactly the 196 decoder Linear layers (6.525 B parameters) become Linear4bit, `lm_head` and `audio_projection.mlp.*` stay Linear."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_MODULES = ("audio_model", "audio_projection", "lm_head", "embed_tokens")
OMNI_REPO_ID, MAGVIT_REPO_ID = "lijiang/Omni-Diffusion", "showlab/magvitv2"
EXPECTED_SNAPSHOT = "2233ee1ae2aa2b63e00466197afdeea0ca9e0901"          # revision seen in the HF cache on 2026-10-28 (read, not downloaded)
EXPECTED_MAGVIT = "5c3fa78f8b3523347c5cd1a4c97f3c4e96f33d5d"
EXPECTED_OMNI_SHA = "c4f4625f84197a72d556ea00f10e5b2775524252"


def find_omni_repo() -> Path:
    """models/third_party/Omni-Diffusion of the project root (the clone lives in the main checkout, not in worktrees). Override: env OMNI_DIFFUSION_REPO."""
    cands = [os.environ.get("OMNI_DIFFUSION_REPO"), ROOT / "models" / "third_party" / "Omni-Diffusion"]
    cands += [p / "models" / "third_party" / "Omni-Diffusion" for p in ROOT.parents]
    for c in cands:
        if c and (Path(c) / "omni_diffusion").is_dir():
            return Path(c)
    raise FileNotFoundError("Omni-Diffusion clone not found; set OMNI_DIFFUSION_REPO")


def offline_env() -> None:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def ensure_import_paths(repo: Path | None = None) -> Path:
    """`import omni_diffusion` pulls in the data package, which imports GLM-4-Voice modules (setup doc section 4): put its three directories on sys.path (no pip install)."""
    repo = Path(repo) if repo else find_omni_repo()
    g = repo / "third_party" / "GLM-4-Voice"
    for p in (g, g / "cosyvoice", g / "third_party" / "Matcha-TTS"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    return repo


def snapshot(repo_id: str) -> Path:
    offline_env()
    from huggingface_hub import snapshot_download
    return Path(snapshot_download(repo_id, local_files_only=True))


def make_audio_stub():
    import torch.nn as nn

    class AudioStub(nn.Module):
        """Replaces `AudioEncoder`. No parameters; the checkpoint's 917 `model.audio_model.*` tensors become 'unexpected keys' and are ignored. Raises if used."""
        calls = 0

        def __init__(self, *a, **k):
            super().__init__()

        def forward(self, *a, **k):
            type(self).calls += 1
            raise RuntimeError("audio encoder stub was called: an audio input reached the model (family R is text + image only)")

    return AudioStub


def install_audio_stub():
    """Patch `AudioEncoder` in modeling_dream before any DreamModel is constructed. Returns the stub class."""
    ensure_import_paths()
    import omni_diffusion.models.dream.modeling_dream as md
    stub = make_audio_stub()
    md.AudioEncoder = stub
    return stub


def bnb_config():
    import torch
    from transformers import BitsAndBytesConfig
    return BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=False,
                              llm_int8_skip_modules=list(SKIP_MODULES))


def load_tokenizer(snap: Path):
    ensure_import_paths()
    from omni_diffusion.models.dream import DreamTokenizer
    return DreamTokenizer.from_pretrained(str(snap))


def load_config(snap: Path):
    ensure_import_paths()
    import omni_diffusion.models.dream  # noqa: F401  (registers DreamConfig / DreamModel with the Auto classes)
    from transformers import AutoConfig
    return AutoConfig.from_pretrained(str(snap), trust_remote_code=False)


def load_model(snap: Path, *, device_index: int = 0, quantize: bool = True):
    """The 4-bit model on cuda:<device_index>, eval mode. GPU only (bitsandbytes kernels). One load, no remote code."""
    import torch
    ensure_import_paths()
    stub = install_audio_stub()
    from omni_diffusion.models.dream import DreamModel
    from omni_diffusion.models.dream.modeling_dream import DreamPreTrainedModel
    cfg = load_config(snap)
    kw = dict(config=cfg, torch_dtype=torch.bfloat16, attn_implementation="sdpa", low_cpu_mem_usage=True, local_files_only=True, use_safetensors=True)
    if quantize:
        kw.update(quantization_config=bnb_config(), device_map={"": device_index})
    model = super(DreamPreTrainedModel, DreamModel).from_pretrained(str(snap), **kw)        # skips the double-loading override of DreamPreTrainedModel
    model.eval()
    model.requires_grad_(False)
    return model, stub


def load_magvit(path: Path, device: str = "cpu"):
    """MAGVIT-v2 (95.4 M parameters, fp32). CPU by default: it saves about 0.4 GB of GPU memory, and encoding one 256 px image takes about 0.5 s on this CPU (measured 2026-10-28)."""
    ensure_import_paths()
    from omni_diffusion.models.magvit.modeling_magvitv2 import MAGVITv2
    m = MAGVITv2().from_pretrained(str(path), use_safetensors=True)
    m.eval()
    m.requires_grad_(False)
    return m.to(device)


def meta_skeleton(snap: Path):
    """The DreamModel on the meta device with the audio stub (no weights, no memory). CPU-only structural checks."""
    ensure_import_paths()
    install_audio_stub()
    from accelerate import init_empty_weights
    from omni_diffusion.models.dream import DreamModel
    with init_empty_weights():
        return DreamModel(load_config(snap))


def quantisation_plan(model, skip=SKIP_MODULES) -> dict:
    """Run transformers' own conversion on a meta skeleton and report which Linear layers would be 4-bit. CPU only (imports bitsandbytes, which loads without a GPU)."""
    import copy
    from transformers.integrations.bitsandbytes import replace_with_bnb_linear
    m = replace_with_bnb_linear(model, modules_to_not_convert=list(skip), quantization_config=bnb_config())
    q = [n for n, mod in m.named_modules() if type(mod).__name__ == "Linear4bit"]
    plain = [n for n, mod in m.named_modules() if type(mod).__name__ == "Linear"]
    qset = set(q)
    n_q = sum(p.numel() for n, p in m.named_parameters() if n.rsplit(".", 1)[0] in qset)
    n_all = sum(p.numel() for p in m.parameters())
    return dict(n_linear4bit=len(q), plain_linear=plain, params_in_4bit=n_q, params_total=n_all, first=q[:2], last=q[-2:],
                all_decoder_layers=all(n.startswith("model.layers.") for n in q))


def versions() -> dict:
    out = {}
    for name in ("torch", "transformers", "accelerate", "bitsandbytes", "tokenizers", "safetensors", "numpy"):
        try:
            mod = __import__(name)
            out[name] = getattr(mod, "__version__", "?")
        except Exception as e:                                                  # noqa: BLE001
            out[name] = f"unavailable ({type(e).__name__})"
    return out
