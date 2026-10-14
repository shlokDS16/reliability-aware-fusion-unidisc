"""Shared setup for the G4 MDLM reproduction (T1-T4). Reuses runs/env-2026-10-14/scripts/common.py (commit gate, stubs).

Shim selection: env G4_SHIM=v1 puts the ORIGINAL pure-PyTorch flash_attn stand-in (verbatim copy in ./shim_v1) first on sys.path;
anything else (default "v2") uses runs/env-2026-10-14/scripts/shims (fixed: rotary computed in fp32 inside, as the flash-attn kernel does).
"""
import os, sys, json, time, platform
from pathlib import Path

G4 = Path(__file__).resolve().parent.parent            # runs/G4-mdlm-repro-2026-10-14
ENV_SCRIPTS = G4.parent / "env-2026-10-14" / "scripts"
sys.path.insert(0, str(ENV_SCRIPTS))
from common import (commit_free_gb, wait_commit, stub_modules, timeit_cuda, env_info, THIRD)  # noqa: E402

SHIM = os.environ.get("G4_SHIM", "v2")
if SHIM == "v1":
    sys.path.insert(0, str(G4 / "scripts" / "shim_v1"))
else:
    sys.path.insert(0, str(ENV_SCRIPTS / "shims"))

stub_modules("causal_conv1d", "mamba_ssm.ops.selective_scan_interface", "mamba_ssm.ops.triton.layernorm",
             "mamba_ssm.ops.triton.selective_state_update")
import torch  # noqa: E402

REPO = THIRD / os.environ.get("G4_REPO", "mdlm")      # "mdlm" (default) or "remdm" (T4 comparison with the ReMDM paper setting)
CKPT = "kuleshov-group/mdlm-owt"
OWT_SHARD = Path(r"C:\Users\Shlok\.cache\dlm_dl\owt\train-00079-of-00080.parquet")
OWT_CACHE = Path(r"C:\Users\Shlok\.cache\dlm_dl\owt\cache")


def setup_repo_import():
    import omegaconf
    sys.path.insert(0, str(REPO))
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    for name, fn in dict(cwd=os.getcwd, device_count=torch.cuda.device_count, eval=eval, div_up=lambda x, y: (x + y - 1) // y).items():
        if not omegaconf.OmegaConf.has_resolver(name):
            omegaconf.OmegaConf.register_new_resolver(name, fn)


def make_cfg(extra=(), bs=16, steps=128):
    import hydra
    with hydra.initialize_config_dir(config_dir=str(REPO / "configs"), version_base=None):
        return hydra.compose(config_name="config", overrides=[
            "mode=ppl_eval", f"loader.batch_size={bs}", f"loader.eval_batch_size={bs}", "loader.num_workers=0",
            "data=openwebtext-split", "model=small", "parameterization=subs", "backbone=hf_dit", "model.length=1024",
            "time_conditioning=false", f"eval.checkpoint_path={CKPT}", "sampling.predictor=ddpm_cache",
            f"sampling.steps={steps}", f"eval.perplexity_batch_size={bs}", "eval.generate_samples=False", "seed=1",
            f"data.cache_dir={OWT_CACHE.as_posix()}", *extra])


def load_diffusion(cfg, tok):
    """Official class, hf_dit backbone (== main._load_from_checkpoint for the HF checkpoint). EMA object is created by the class from
    the loaded HF weights (so ema.copy_to is a no-op) exactly as in main._ppl_eval."""
    import diffusion as mdlm_diffusion
    return mdlm_diffusion.Diffusion(cfg, tokenizer=tok).to("cuda")


def git_sha(path):
    import subprocess
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def jdump(obj, path):
    Path(path).write_text(json.dumps(obj, indent=2, default=str))
