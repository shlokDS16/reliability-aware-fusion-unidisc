# P2-UNIDISC-KEYCHECK: is any UniDisc 1.4B parameter left at random init after the scorer's load?

Evidence level E4 (run here, no GPU, no weights materialised). Script: `keycheck.py`; results: `keycheck.json`.
Run: `CUDA_VISIBLE_DEVICES="" .venv\Scripts\python.exe runs/P2-UNIDISC-KEYCHECK/keycheck.py` (about a minute, RAM small: meta model plus an mmap-ed checkpoint, only metadata read).

## What the scorer does (source facts, read in code)
- `exp_p2/common.py:141` -> `exp001/unidisc_net.py:UniDiscNet` -> `runs/env-2026-10-14/scripts/unidisc_setup.py` `make_config(["eval.visualize_sample=false"])` + `build_model(cfg, bf16=True)`.
- Checkpoint: `~/.cache/huggingface/hub/models--aswerdlow--unidisc_interleaved/snapshots/2b344ca856bd108b52a2d022a3463dace131249f/unidisc_interleaved.pt` (fp32, OrderedDict of 342 tensors, no `model` wrapper).
- Load: `models/third_party/unidisc/model_setup.py` `set_accelerator._load(self.backbone, path)`: `obj.load_state_dict(state_dict, strict=config.trainer.disable_strict_load)`.
  Resolved `disable_strict_load = false` (configs/config.yaml:188, not overridden by the four experiments or by our overrides), so the call is `strict=False`. Errors would only be printed and re-raised;
  with `strict=False` missing/unexpected keys never raise (shape mismatches still do).
- Key transforms applied: substring removal of `_orig_module.`, `_orig_mod.`, `module.`; after them all 342 checkpoint keys equal the 342 model keys (the script applies the same transforms in the same order). The llama-tie and `use_orig_unidisc_dit` branches are not taken (backbone `dit`, `use_orig_unidisc_dit` false).

## Result (this script)
- Backbone built on `meta`: `models.dit.DIT`, vocab 48385 = 32001 text (incl. mask id 32000) + 16384 image; 342 parameter tensors, 1,406,870,785 elements, 0 persistent buffers.
- Checkpoint: 342 tensors, 1,406,870,785 elements, all fp32.
- Missing keys (model, not checkpoint): **0** (0 learnable, 0 persistent buffers). Unexpected keys: **0**. Shape mismatches: **0**. Dtype differences: none. 342 of 342 matched with equal shape.
- torch's own `load_state_dict` on the meta model returns empty `missing_keys` and `unexpected_keys` for both `strict=False` and the resolved value.
- Non-persistent, deterministic buffers (not in any state dict, computed at construction): `rotary_{cos,sin}_emb_img_{256,1024,2304,4096}`, `rotary_{cos,sin}_emb_txt`. Not checkpoint-loadable by design.

## Scope limits
- Checked the DIT backbone, the only module `_load` targets. The VQ tokenizer (`vq_ds16_t2i.pt`, `model.use_custom_vae_ckpt`) is loaded by a different path and is not covered here.
- The meta model is built from the same class and config but without the `Diffusion` wrapper (which would also load the VAE); the wrapper does not add parameters to `self.backbone` before the load (model_setup.py:157-204).
- Key-name and shape equality shows every parameter is overwritten by checkpoint data; it does not show the checkpoint values are the intended final weights.
