"""Model passes of GATE (v1 section 3, Alg. 1-2; v2 4.1, 4.2). Every function takes an object `sc` with the `exp_p2.scoring.UniScorer`
interface (`sc.logits_fn(st)`, `sc.L_I`) and a layout dict `st = sc.build(caption_tokens, codes)`; none loads a model itself.

Context levels (v1 3.1), for image token j in mask group S_k:
  B_j = log p(x_j | image tokens outside S_k, caption MASKED)      K passes      gate statistic input, hypothesis-free (evidence-separation rule)
  D_j = log p(x_j | everything masked)                               1 pass per caption length n (layout only); see dcache.py
  C_j = log p(x_j | image fully masked, caption visible)             1 pass per caption (never sees the image)
  q_j = B_j - D_j  (primary gate statistic); suspicion u_j = -q_j.
"""
from __future__ import annotations

import numpy as np
import torch

from exp_p2.scoring import Spec, masked_logprobs, TEXT_LO, TEXT_HI, IMG_LO, IMG_HI, MASK_ID, SDPA_BS
from exp_p2 import core


def _pos(idx, ref: torch.Tensor) -> torch.Tensor:
    return ref[torch.as_tensor(np.asarray(idx), device=ref.device)]


def image_B(sc, st: dict, groups: np.ndarray, K: int, *, allow_degenerate: bool = False, bs: int = SDPA_BS) -> dict:
    """K complementary-mask passes over the image tokens with the caption masked. Returns B [m] (float32 log p of the observed code) and
    maxp [m] (max probability of the same pass; s3 = 1 - maxp). K < 2 is refused for the gate statistic (v1 L6: with one group B == D, q == 0)."""
    if K < 2 and not allow_degenerate:
        raise ValueError("K=1 makes B identical to D (q == 0): degenerate gate statistic (v1 limiting case L6)")
    base, cap, img = st["base"], st["cap_pos"], st["img_pos"]
    masks = core.masks_from_groups(groups, K)
    specs = [Spec(_pos(m, img), IMG_LO, IMG_HI, extra=cap) for m in masks]
    B = np.zeros(sc.L_I, np.float32)
    maxp = np.zeros(sc.L_I, np.float32)
    for m, sp, lp in zip(masks, specs, masked_logprobs(sc.logits_fn(st), base, specs, bs=bs)):
        tgt = base[sp.pos] - IMG_LO
        B[m] = lp.gather(1, tgt[:, None])[:, 0].cpu().numpy()
        maxp[m] = lp.max(dim=1).values.exp().cpu().numpy()
    return dict(B=B, maxp=maxp)


def full_image_lp(sc, st: dict, caption_masked: bool, *, bs: int = SDPA_BS) -> torch.Tensor:
    """One pass, all image tokens masked. caption_masked=False -> Lambda^c / C (caption visible); True -> D (layout only).
    Returns the fp32 log-softmax matrix [m, 16384] (64 MiB at m = 1024) on the scorer's device."""
    sp = Spec(st["img_pos"], IMG_LO, IMG_HI, extra=st["cap_pos"] if caption_masked else None)
    return next(iter(masked_logprobs(sc.logits_fn(st), st["base"], [sp], bs=bs)))


def full_text_lp(sc, st: dict, *, image_mask_pos: torch.Tensor | None = None, image_all_masked: bool = False, bs: int = SDPA_BS) -> torch.Tensor:
    """One pass, all caption tokens masked ([n, 32000] matrix). Image visible except `image_mask_pos` (gated tokens) or fully masked."""
    extra = st["img_pos"] if image_all_masked else image_mask_pos
    if extra is not None and len(extra) == 0:
        extra = None
    sp = Spec(st["cap_pos"], TEXT_LO, TEXT_HI, extra=extra)
    return next(iter(masked_logprobs(sc.logits_fn(st), st["base"], [sp], bs=bs)))


def text_arms_lp(sc, st: dict, gates: list[np.ndarray | None], *, bs: int = SDPA_BS) -> list[torch.Tensor]:
    """Text-direction conditioning arms of one image condition and one caption: one spec per gate (None/empty = image fully visible).
    All specs share the base row, so up to `bs` arms are one batched forward. Returns one [n, 32000] matrix per gate."""
    img = st["img_pos"]
    specs = []
    for g in gates:
        extra = None if (g is None or not np.any(g)) else _pos(np.nonzero(np.asarray(g, bool))[0], img)
        specs.append(Spec(st["cap_pos"], TEXT_LO, TEXT_HI, extra=extra))
    return list(masked_logprobs(sc.logits_fn(st), st["base"], specs, bs=bs))


def text_B(sc, st: dict, groups: np.ndarray, K_T: int, *, bs: int = SDPA_BS) -> dict:
    """Caption-side gate input (SHOULD tier S1): K_T = min(K, n) passes, image fully masked. Returns B [n], maxp [n] per piece."""
    base, cap, img = st["base"], st["cap_pos"], st["img_pos"]
    masks = core.masks_from_groups(groups, K_T)
    specs = [Spec(_pos(m, cap), TEXT_LO, TEXT_HI, extra=img) for m in masks]
    n = len(cap)
    B, maxp = np.zeros(n, np.float32), np.zeros(n, np.float32)
    for m, sp, lp in zip(masks, specs, masked_logprobs(sc.logits_fn(st), base, specs, bs=bs)):
        tgt = base[sp.pos] - TEXT_LO
        B[m] = lp.gather(1, tgt[:, None])[:, 0].cpu().numpy()
        maxp[m] = lp.max(dim=1).values.exp().cpu().numpy()
    return dict(B=B, maxp=maxp)


@torch.no_grad()
def observed_unmasked_logprob(sc, st: dict) -> np.ndarray:
    """Trust-but-Verify-style score (v2 4.2): log p(observed code | NOTHING masked in the image, caption masked), read at the observed
    (visible) position. One pass. Meaningful only if the network does not simply copy visible inputs (U7); the caller checks the
    copy statistic from the returned values (mean of exp(.) near 1 on every token means a copy-through parameterisation)."""
    base, cap, img = st["base"], st["cap_pos"], st["img_pos"]
    x = base.clone()
    x[cap] = MASK_ID
    logits = sc.logits_fn(st)(x[None])
    lp = torch.log_softmax(logits[0, img, IMG_LO:IMG_HI].float(), dim=-1)
    tgt = base[img] - IMG_LO
    return lp.gather(1, tgt[:, None])[:, 0].cpu().numpy().astype(np.float32)


def suspicion_q(B: np.ndarray, D: np.ndarray) -> np.ndarray:
    """u = -(B - D) in float32 arithmetic (so the minimum gap between distinct values is the float32 grid, see calibrate.eps0_from)."""
    return -(np.asarray(B, np.float32) - np.asarray(D, np.float32))
