"""Build the official UniDisc `Diffusion` model for inference on Windows / 12 GB (mirrors demo/inference.py::setup, no demo server).
Experiments used by the official demo: large_scale_train, large_scale_train_high_res_interleaved, eval_unified,
large_scale_high_res_interleaved_inference (see demo/demo.sh)."""
import os, sys
from pathlib import Path
from common import *  # noqa

REPO = THIRD / "unidisc"
os.environ.setdefault("UNIDISC_FORCE_CUDNN_SPDA_CONTEXT", "1")   # as demo/inference.py
os.environ.setdefault("UNIDISC_DISABLE_APEX_RMSNORM", "1")       # as demo/inference.py
os.environ.setdefault("DIFFUSION_DATA_DIR", str(OUT / "_unused_data_dir"))  # referenced (never read) by the training data_dir_* interpolations
os.environ.setdefault("UNIDISC_DIR", str(REPO))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("WANDB_MODE", "disabled")
sys.path.insert(0, str(REPO))
os.chdir(OUT / "smoke_unidisc") if (OUT / "smoke_unidisc").exists() else None

EXPERIMENTS = "[large_scale_train,large_scale_train_high_res_interleaved,eval_unified,large_scale_high_res_interleaved_inference]"


def hf_path(repo, fname):
    from huggingface_hub import hf_hub_download
    return hf_hub_download(repo, fname, local_files_only=True)


def make_config(extra=(), load_ckpt=True):
    from hydra import compose, initialize_config_dir
    import utils
    utils.set_omega_conf_resolvers()
    ckpt = hf_path("aswerdlow/unidisc_interleaved", "unidisc_interleaved.pt") if load_ckpt else "null"
    vq = hf_path("aswerdlow/unidisc_interleaved", "vq_ds16_t2i.pt")
    ov = [f"experiments={EXPERIMENTS}", f"trainer.load_from_state_dict={ckpt}", f"model.use_custom_vae_ckpt={vq}",
          "loader.num_workers=0", "loader.num_eval_workers=0", "wandb.mode=disabled", *extra]
    with initialize_config_dir(config_dir=str(REPO / "configs"), version_base=None):
        return compose(config_name="config", overrides=ov)


def build_model(config, bf16=True):
    """Returns (model, config). Compat notes (all in this script, repo untouched):
    * default device = cuda while the model is constructed, so the 1.4B fp32 parameters are created on the GPU and never as a
      second 5.6 GB CPU copy (CPU allocations above ~5 GB crash this machine: system commit is nearly exhausted, see setup.md);
    * torch.load is called with mmap=True for the 5.6 GB checkpoint for the same reason;
    * bf16=True -> trainer.force_bf16_eval: backbone weights are cast to bf16 after loading (repo code path, model_setup.py)."""
    import torch, dataloader
    from omegaconf import open_dict
    from accelerate import Accelerator, PartialState
    from utils import set_torch_defaults
    set_torch_defaults()
    accelerator = Accelerator(mixed_precision="no")  # demo uses "bf16": that wrapper converts the logits to fp32 (2x logits memory); see setup.md
    with open_dict(config):
        config.trainer.devices = 1
        config.trainer.dtype = str(torch.bfloat16)
        if bf16:
            config.trainer.force_bf16_eval = True
    from model import Diffusion
    orig_load = torch.load
    torch.load = lambda *a, **k: orig_load(*a, **{"mmap": True, "weights_only": True, **k})   # the checkpoint is read in set_accelerator()
    torch.set_default_device("cuda")
    try:
        model = Diffusion(config=config, tokenizer=dataloader.get_tokenizer(config), device=PartialState().device)
        torch.set_default_device("cpu")
        model.set_accelerator(accelerator)   # loads trainer.load_from_state_dict into the backbone (and casts to bf16 if force_bf16_eval)
    finally:
        torch.set_default_device("cpu"); torch.load = orig_load
    import gc; gc.collect(); torch.cuda.empty_cache()   # drop the mmap-ed checkpoint dict (it holds ~3 GB of system commit)
    return model, config
