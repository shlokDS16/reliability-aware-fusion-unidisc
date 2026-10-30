"""UniDisc 1.4B checkpoint key check on the meta device (no weights allocated, no GPU).

Builds the exact backbone the scorer builds (models.dit.DIT with the config of exp001/unidisc_net.py -> runs/env-2026-10-14/scripts/unidisc_setup.make_config)
under torch.device('meta'), reads the checkpoint with mmap (only shape/dtype metadata is used; tensor data is never read),
applies the key transforms of models/third_party/unidisc/model_setup.py::set_accelerator._load, and compares with the backbone state_dict.
Run:  CUDA_VISIBLE_DEVICES="" python runs/P2-UNIDISC-KEYCHECK/keycheck.py
"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = ROOT / "runs" / "env-2026-10-14" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "shims"))
import torch
import unidisc_setup as U            # same module the scorer uses (sets env vars, sys.path to the UniDisc repo)

out = {"script": "runs/P2-UNIDISC-KEYCHECK/keycheck.py", "torch": torch.__version__}

# ---- 1. the scorer's config (exp001/unidisc_net.py: make_config(["eval.visualize_sample=false"]), load_ckpt=True)
cfg = U.make_config(["eval.visualize_sample=false"])
from omegaconf import open_dict
with open_dict(cfg):                 # build_model() mutates the config exactly like this before constructing the model
    cfg.trainer.devices = 1
    cfg.trainer.dtype = str(torch.bfloat16)
    cfg.trainer.force_bf16_eval = True
T = cfg.trainer
out["config"] = dict(
    load_from_state_dict=str(T.load_from_state_dict),
    disable_strict_load=bool(T.disable_strict_load),
    resolved_strict_kwarg=bool(T.disable_strict_load),
    use_orig_unidisc_dit=bool(getattr(T, "use_orig_unidisc_dit", False)),
    backbone=str(cfg.backbone),
    model_use_pretrained_img_emb=bool(getattr(cfg.model, "use_pretrained_img_emb", False)),
    model_img_cond=bool(getattr(cfg.model, "img_cond", False)),
    model_cond_label=bool(getattr(cfg.model, "cond_label", False)),
    mup=bool(cfg.model.mup),
    image_vocab_size=int(cfg.model.image_vocab_size),
    force_text_vocab_size=getattr(cfg.model, "force_text_vocab_size", None),
    add_labels=getattr(cfg.model, "add_labels", None),
    ckpt_is_bin=".bin" in str(T.load_from_state_dict),
)
ckpt_path = Path(str(T.load_from_state_dict))
out["checkpoint_file"] = str(ckpt_path)
out["checkpoint_bytes"] = ckpt_path.stat().st_size
out["vq_ckpt_not_part_of_backbone_load"] = str(cfg.model.use_custom_vae_ckpt)

# ---- 2. vocab sizes exactly as model_setup.init
import dataloader
tok = dataloader.get_tokenizer(cfg)
vocab = len(tok)
if getattr(cfg.model, "force_text_vocab_size", None) is not None:
    vocab = cfg.model.force_text_vocab_size
if getattr(tok, "mask_token", None) is None:
    mask_index = vocab
    vocab += 1
else:
    mask_index = tok.mask_token_id
text_vocab = vocab
vocab += int(cfg.model.image_vocab_size)
if getattr(cfg.model, "add_labels", None) is not None:
    vocab += int(cfg.model.add_labels)
out["vocab"] = dict(len_tokenizer=len(tok), has_mask_token=getattr(tok, "mask_token", None) is not None, mask_index=int(mask_index),
                    text_vocab_size=int(text_vocab), total_vocab_size=int(vocab))

# ---- 3. backbone on meta device
import models.dit
with torch.device("meta"):
    bb = models.dit.DIT(config=cfg, vocab_size=vocab, mask_index=mask_index, text_vocab_size=text_vocab, autocast_dtype=torch.float32,
                        device=torch.device("meta"), static_img_sl=None, static_txt_sl=None)
msd = bb.state_dict()
assert all(v.device.type == "meta" for v in msd.values())
out["backbone_class"] = type(bb).__module__ + "." + type(bb).__name__
out["model_n_state_dict_entries"] = len(msd)
param_names = {n for n, _ in bb.named_parameters()}
buffer_names = {n for n, _ in bb.named_buffers()}
out["model_n_parameter_tensors"] = len(param_names)
out["model_n_param_elements"] = sum(p.numel() for p in bb.parameters())
out["model_n_persistent_buffer_entries"] = len(set(msd) - param_names)
out["model_nonpersistent_buffers_not_in_state_dict"] = sorted(buffer_names - set(msd))[:50]

# ---- 4. checkpoint metadata (mmap, weights_only)
sd = torch.load(ckpt_path, mmap=True, weights_only=True, map_location="cpu")
out["ckpt_top_level_type"] = type(sd).__name__
out["ckpt_top_level_n"] = len(sd)
if 'model' in sd and len(sd) < 10:
    sd = sd['model']
    out["ckpt_unwrapped_model_key"] = True
# same transforms as _load (substring replaces, in this order)
sd = {k.replace("_orig_module.", ""): v for k, v in sd.items()}
sd = {k.replace("_orig_mod.", ""): v for k, v in sd.items()}
sd = {k.replace("module.", ""): v for k, v in sd.items()}
assert cfg.backbone != 'llama'
assert not getattr(T, 'use_orig_unidisc_dit', False)
out["ckpt_n_entries"] = len(sd)
out["ckpt_n_elements"] = sum(v.numel() for v in sd.values())
out["ckpt_dtypes"] = sorted({str(v.dtype) for v in sd.values()})

# ---- 5. compare
missing = sorted(set(msd) - set(sd))
unexpected = sorted(set(sd) - set(msd))
common = sorted(set(msd) & set(sd))
shape_mismatch = {k: dict(model=list(msd[k].shape), ckpt=list(sd[k].shape)) for k in common if tuple(msd[k].shape) != tuple(sd[k].shape)}
missing_params = [k for k in missing if k in param_names]
missing_buffers = [k for k in missing if k not in param_names]
dtype_pairs = sorted({(str(msd[k].dtype), str(sd[k].dtype)) for k in common if msd[k].dtype != sd[k].dtype})
out["result"] = dict(
    n_missing=len(missing), n_missing_learnable_params=len(missing_params), missing_learnable_params=missing_params,
    n_missing_buffers=len(missing_buffers), missing_buffers=missing_buffers,
    n_unexpected=len(unexpected), unexpected=unexpected[:200],
    n_shape_mismatch=len(shape_mismatch), shape_mismatch=dict(list(shape_mismatch.items())[:100]),
    dtype_pairs_model_vs_ckpt=[list(p) for p in dtype_pairs],
    n_matched_with_equal_shape=len(common) - len(shape_mismatch),
)
# torch's own check on the meta module (copies into meta tensors are no-ops; only the key/shape logic runs)
for label, strict in (("strict_False", False), ("resolved_strict", bool(T.disable_strict_load))):
    try:
        r = bb.load_state_dict(sd, strict=strict)
        out["torch_load_state_dict_" + label] = dict(strict=strict, ok=True, missing_keys=list(r.missing_keys), unexpected_keys=list(r.unexpected_keys))
    except Exception as e:
        out["torch_load_state_dict_" + label] = dict(strict=strict, ok=False, error=str(e)[:3000])

(HERE / "keycheck.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("config", "vocab", "model_n_state_dict_entries", "ckpt_n_entries", "result",
                                       "torch_load_state_dict_strict_False", "torch_load_state_dict_resolved_strict")}, indent=1)[:7000])
