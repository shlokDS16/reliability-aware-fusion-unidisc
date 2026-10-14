"""Official UniDisc maskgit sampler as a joint (prefix -> 32-token tail + image) generator with read-only instrumentation
(EXP-003 card 2, 3, 8, 4.3 item 9). Generation venv only.

Instrumentation, all read-only (no tensor of the sampler is modified, no random number is drawn, every hook is removed afterwards):
  * forward pre-hook on the backbone: `assert_eval()` before EVERY forward inside `_sample` (a train-mode forward raises, the unit
    fails), and the count of network calls (sum of the batch dimension: a guided step is one batch-2 forward = 2 calls);
  * wrapper of `model._ddpm_forward`: at the first step with t < 1 and cfg > 0 it computes the conditional-only marginals at the same
    state (one extra forward, counted apart as `assert_calls`) and records the max absolute difference of the guided and conditional
    marginals on the tail and on the image positions (the guidance-acted assertion of card 1.2: both above 1e-3);
  * wrapper of `model._maskgit_update`: records a copy of the token row at every entry (commit-order record, card 4.3 item 9).
`run(..., instrument=False)` runs the bare `_sample` (only the `decode_sampling` grab that EXP-001 also uses) for the token-identity
check of the hooks on 8 units.
"""
from __future__ import annotations

import time

import numpy as np
import torch

from exp001.config import MASK_ID, IMG_OFFSET, IMG_VOCAB
from exp003.config import OFFICIAL_SEED_BASE, R_TEMP

GUIDANCE_MIN_DIFF = 1e-3


def commit_steps(entries: np.ndarray, final: np.ndarray, mask_id: int = MASK_ID) -> np.ndarray:
    """entries [S, n]: token rows (generated positions only) at the entry of each `_maskgit_update` call; final [n]: the row after the last
    call. Row k (0-based) is the state after k steps. Returns for every position the 1-based loop step in which it was committed
    (first row in which it is not the mask id); S + 1 = not committed by the loop (left to the final noise-removal pass)."""
    S, n = entries.shape
    rows = np.concatenate([entries, final[None]], 0)
    out = np.full(n, S + 1, dtype=np.int16)
    done = np.zeros(n, dtype=bool)
    for k in range(S + 1):
        newly = (rows[k] != mask_id) & ~done
        out[newly] = max(k, 1)
        done |= newly
    return out


def tail_vs_image_order(cs: np.ndarray, L_T: int = 32) -> dict:
    """Summary of the commit-order record (card 4.3 item 9): mean normalised commit step of tail and image tokens, and the share of the
    tail committed before 25 percent of the image tokens have been (steps strictly earlier than the 25th percentile step of the image)."""
    S = int(cs.max())
    t, i = cs[:L_T].astype(float), cs[L_T:].astype(float)
    q25 = float(np.quantile(i, 0.25))
    return dict(mean_step_tail=float(t.mean()), mean_step_image=float(i.mean()), image_q25_step=q25,
                tail_share_before_image_q25=float((t < q25).mean()), max_step=S)


class OfficialRunner:
    def __init__(self, net):
        self.net = net
        self.model = net.model

    # ---------------------------------------------------------------------------------------------- one unit
    def run(self, prefix: str, i: int, steps: int, cfg: float, instrument: bool = True, res: int = 512) -> dict:
        from omegaconf import open_dict
        net, model = self.net, self.model
        st = net.set_prompt(prefix, n_txt=32, res=res)
        with open_dict(model.config):
            model.config.eval.cfg = cfg
            model.config.sampling.steps = steps
            model.config.sampling.max_sampling_steps = steps
        assert int(model.config.sampling.steps) == int(model.config.sampling.max_sampling_steps) == steps
        assert abs(float(model.config.eval.maskgit_r_temp) - R_TEMP) < 1e-9
        assert bool(model.config.sampling.noise_removal) and str(model.config.sampling.predictor) == "maskgit"
        rec: dict = {}
        stats = dict(calls=0, forwards=0, assert_calls=0, entries=[], after=[], guidance=None, in_assert=False)
        orig_decode, orig_ddpm, orig_update = model.decode_sampling, model._ddpm_forward, model._maskgit_update
        a0, L_T, i0, L_I = net.a0, 32, net.i0, net.L_I
        gen_sl = torch.as_tensor(np.r_[a0:a0 + L_T, i0:i0 + L_I], dtype=torch.long, device='cuda')

        def grab(x, *a, **k):
            rec["x"] = x.clone()
            return [], []

        def pre_hook(mod, args, kwargs):
            net.assert_eval()
            if not stats["in_assert"]:
                x = args[0] if args else kwargs.get("input_ids", kwargs.get("indices"))
                stats["calls"] += int(x.shape[0])
                stats["forwards"] += 1

        def ddpm_wrap(x, t, sigma_t, x0=None, x0_unmask=None, force_cfg=None, **kwargs):
            out = orig_ddpm(x, t, sigma_t, x0=x0, x0_unmask=x0_unmask, force_cfg=force_cfg, **kwargs)
            if cfg > 0 and stats["guidance"] is None and float(t.flatten()[0]) < 1.0 - 1e-9:
                stats["in_assert"] = True
                try:
                    cond = model.forward(x=x, sigma=sigma_t, **kwargs).exp().float()
                finally:
                    stats["in_assert"] = False
                stats["assert_calls"] += 1
                g = out.float()
                dt = (g[0, a0:a0 + L_T] - cond[0, a0:a0 + L_T]).abs().max().item()
                di = (g[0, i0:i0 + L_I] - cond[0, i0:i0 + L_I]).abs().max().item()
                stats["guidance"] = dict(t=float(t.flatten()[0]), max_abs_diff_text=dt, max_abs_diff_img=di,
                                         acted=bool(dt > GUIDANCE_MIN_DIFF and di > GUIDANCE_MIN_DIFF))
            return out

        def update_wrap(x, t, dt, schedule=None, step=None, **kwargs):
            stats["entries"].append(x[0, gen_sl].detach().cpu().numpy().astype(np.int32))
            x_new, nfe = orig_update(x, t, dt, schedule=schedule, step=step, **kwargs)
            stats["after"].append(x_new[0, gen_sl].detach().cpu().numpy().astype(np.int32))
            return x_new, nfe

        handle = None
        model.decode_sampling = grab
        if instrument:
            handle = model.backbone.register_forward_pre_hook(pre_hook, with_kwargs=True)
            model._ddpm_forward, model._maskgit_update = ddpm_wrap, update_wrap
        torch.manual_seed(OFFICIAL_SEED_BASE + i)
        np.random.seed(OFFICIAL_SEED_BASE + i)
        net.assert_eval()
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        try:
            model._sample(text_only=False, num_steps=steps, batch_size_per_gpu=1,
                          example_batch=dict(input_ids=st["x0"], attention_mask=st["attention_mask"]), sample_batch_idx=0,
                          modality=st["modality"], sample_ids=st["sample_ids"], allow_interleaved_conditional=True,
                          x0_unmask=st["unmask"], x0=st["x0"])
            torch.cuda.synchronize()
            secs = time.perf_counter() - t0
        finally:
            model.decode_sampling = orig_decode
            if instrument:
                handle.remove()
                model._ddpm_forward, model._maskgit_update = orig_ddpm, orig_update

        net.assert_eval()                                           # the sampler must not have switched the backbone to train mode
        if "x" not in rec:
            raise RuntimeError("official sampler returned no sample (exception swallowed by try_except)")
        x = rec["x"][0]
        tail = x[a0:a0 + L_T].detach().cpu()
        codes = (x[i0:i0 + L_I] - IMG_OFFSET).detach().cpu()
        res_d = dict(tail=tail.numpy().astype(np.int64), img=codes.clamp(0, IMG_VOCAB - 1).numpy().astype(np.int64), seconds=secs,
                     n_masked_text=int((x[a0:a0 + L_T] == MASK_ID).sum()), n_masked_img=int((x[i0:i0 + L_I] == MASK_ID).sum()),
                     steps=steps, cfg=cfg, torch_seed=OFFICIAL_SEED_BASE + i)
        if instrument:
            if cfg > 0:
                g = stats["guidance"]
                if g is None or not g["acted"]:
                    raise AssertionError(f"guidance-acted assertion failed: {g}")
            entries = np.stack(stats["entries"]) if stats["entries"] else np.zeros((0, len(gen_sl)), dtype=np.int32)
            after_last = stats["after"][-1] if stats["after"] else entries[0]
            # row after the last pass of the loop = state entering the noise-removal pass
            res_d["n_masked_before_final"] = int((after_last == MASK_ID).sum())
            res_d["entries"] = entries
            res_d["commit_step"] = commit_steps(entries, after_last) if len(entries) else np.zeros(len(gen_sl), np.int16)
            res_d["calls"] = stats["calls"]
            res_d["forwards"] = stats["forwards"]
            res_d["assert_calls"] = stats["assert_calls"]
            res_d["guidance"] = stats["guidance"]
        return res_d
