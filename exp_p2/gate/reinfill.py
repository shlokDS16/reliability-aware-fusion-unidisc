"""S2 re-infill (SAP AD.5, AB.4; spec v2 11.2 S2, v1 Algorithm 6): true in-network re-masking of a set of image tokens and re-infilling it with UniDisc's own conditional.

What one draw is (the sampler of SAP AD.5, deliberately the plain one of Algorithm 6 and not UniDisc's T2I sampler, see below):
  1. start from the observed (corrupted) codes; set the positions of the set S to [MASK]; the caption is masked as well (R1: hypothesis-free, no leakage, Prop. 7) unless
     `caption_visible` (the optional leakage control, true caption visible);
  2. S_r = 16 unmask steps in a FIXED RANDOM ORDER: a permutation of S is drawn up front from the draw's rng (it does not look at the model or at the content); at step s the next
     k_s = ceil(|U| / (S_r - s + 1)) positions of the permutation, U = positions still masked, are unmasked, so S is exhausted in at most S_r steps (|S| < 16 gives |S| steps of one);
  3. one forward pass per step; the k_s positions are sampled from the fp32 softmax of the raw bf16 logits restricted to the image vocabulary (temperature 1, no guidance, same
     convention as `scoring.masked_logprobs`), then written into the row;
  4. the draw's own likelihood is the chain sum of log pi_j(y_j) over the sampled positions, with the caption masked (it never sees a caption: the best-of-n selection cannot leak the
     hypothesis). The kept draw of an arm is the one with the highest value (ties: lowest draw index).
Draws of one arm are independent: own permutation, own torch generator (seeded from `arms.arm_rng`), so a draw does not depend on the batch it is run in. `n_draw` rows share one forward
(`bs` = SDPA_BS = 4 rows, the batch the probes and M4 use; peak memory is then that of an M4 batch).

Memory discipline (probe-2 finding: allocated peaks of about 4.1 and 8.2 GB, a sub-second 10.5 GB whole-GPU spike tripped the watchdog): the full-vocabulary logits [B, L, 48385] of a step are
sliced to the sampled image positions immediately and deleted before the next step; nothing is decoded here; the caller scores the codes by gathering from the two cached caption-only
tables (`pipeline.caption_lambdas`), 2 passes per item for all arms.

Why not `model._sample(..., x0=, x0_unmask=)` (UniDisc's entry point, models/third_party/unidisc/model_eval.py:2109, used by `UniDiscNet.official_t2i`)? Because the SAP fixes the recipe:
S_r = 16, a fixed random order and an unguided sampler (AD.5), whereas `_sample` runs MaskGIT with an arccos schedule, confidence-ordered unmasking with Gumbel noise from the global numpy
RNG and, in the demo configuration, classifier-free guidance; a draw could not be seeded per (item, arm, draw) and the order rule would differ from the preregistered one. Algorithm 6 of
the spec lists max-probability order as its primary rule and random order as an ablation; the SAP (later, binding) says random, and that is what is implemented. See the report.
"""
from __future__ import annotations

import math

import numpy as np
import torch

from exp_p2.scoring import IMG_HI, IMG_LO, IMG_OFFSET, MASK_ID, SDPA_BS

S_R = 16
N_DRAW = 4
assert IMG_LO == IMG_OFFSET


def step_sizes(g: int, S_r: int = S_R) -> list[int]:
    """k_s = ceil(|U| / (S_r - s + 1)) for s = 1, 2, ... while U is not empty. sum(k_s) = g and len = min(g, S_r), e.g. g = 64 -> 16 x 4; g = 10 -> 10 x 1."""
    out, u = [], int(g)
    for s in range(1, S_r + 1):
        if u <= 0:
            break
        k = math.ceil(u / (S_r - s + 1))
        out.append(k)
        u -= k
    assert u == 0
    return out


def n_passes(g: int, n_draw: int = N_DRAW, S_r: int = S_R) -> int:
    """Rows through the network for one arm of one condition: n_draw chains of len(step_sizes(g)) steps."""
    return n_draw * len(step_sizes(g, S_r))


@torch.no_grad()
def reinfill(sc, st: dict, codes: np.ndarray, sets: list[np.ndarray], orders: list[np.random.Generator], seeds: list[int], *, caption_visible: bool = False,
             S_r: int = S_R, bs: int = SDPA_BS) -> dict:
    """Re-infill `sets[b]` (token indices 0..m-1, all of one size g) of the observed `codes` [m], one independent draw per set.
    st = sc.build(caption_tokens, codes). Returns dict(codes [n, m] int64, logp [n] float64 chain log-likelihood of the sampled tokens, n_steps int, order [n, g] the visiting orders)."""
    n = len(sets)
    assert n == len(orders) == len(seeds) and n >= 1
    g = len(sets[0])
    assert all(len(s) == g for s in sets), "all draws of an arm re-infill sets of one size (equal gate size, SAP AD.5)"
    m = sc.L_I
    codes = np.asarray(codes, np.int64)
    out = np.tile(codes, (n, 1))
    logp = np.zeros(n, np.float64)
    ks = step_sizes(g, S_r)
    perms = [np.asarray(sets[b], np.int64)[orders[b].permutation(g)] if g else np.zeros(0, np.int64) for b in range(n)]
    if g == 0:
        return dict(codes=out, logp=logp, n_steps=0, order=np.zeros((n, 0), np.int64))
    base, img, cap = st["base"], st["img_pos"], st["cap_pos"]
    dev = base.device
    gens = [torch.Generator(device=dev).manual_seed(int(s)) for s in seeds]
    f = sc.logits_fn(st)
    for c0 in range(0, n, bs):
        rows = list(range(c0, min(n, c0 + bs)))
        x = base.unsqueeze(0).repeat(len(rows), 1)
        if not caption_visible:
            x[:, cap] = MASK_ID
        for j, b in enumerate(rows):
            x[j, img[torch.as_tensor(perms[b], device=img.device)]] = MASK_ID
        done = 0
        for k in ks:
            logits = f(x)                                                    # [rows, L, V] bf16: sliced and dropped inside this step
            for j, b in enumerate(rows):
                sel = perms[b][done:done + k]
                pos = img[torch.as_tensor(sel, device=img.device)]
                lp = torch.log_softmax(logits[j, pos, IMG_LO:IMG_HI].float(), dim=-1)
                y = torch.multinomial(lp.exp(), 1, generator=gens[b])[:, 0]
                logp[b] += float(lp.gather(1, y[:, None]).sum())
                x[j, pos] = y + IMG_OFFSET
                out[b, sel] = y.cpu().numpy()
                del lp, y
            del logits
            done += k
        assert done == g
    return dict(codes=out, logp=logp, n_steps=len(ks), order=np.stack(perms))


class NonFiniteDrawError(ValueError):
    """A draw's chain log-likelihood is NaN or infinite; the item stops (runner `item_error`) instead of keeping a broken draw."""


def keep_best(logp: np.ndarray) -> int:
    """Index of the kept draw: highest own (caption-masked) chain likelihood, ties to the lowest index.
    Raises NonFiniteDrawError on any non-finite entry (re-audit A3 m1); otherwise unchanged."""
    a = np.asarray(logp, np.float64)
    if not np.all(np.isfinite(a)):
        raise NonFiniteDrawError(f"non-finite draw log-likelihood: {a.tolist()}")
    return int(np.argmax(a))


def token_agreement(final_codes: np.ndarray, clean: np.ndarray, corrupted: np.ndarray, reinfilled: np.ndarray) -> dict:
    """Descriptive, not a restoration claim (AB.4 item 5): `agree_changed` = share of the truly changed tokens whose code after the repair equals the original clean code (a changed token the
    set did not cover keeps its corrupted code and counts as not agreeing); `agree_set` = share of the re-infilled positions whose new code equals the clean code (NaN for an empty set)."""
    final_codes, clean, corrupted = (np.asarray(a, np.int64) for a in (final_codes, clean, corrupted))
    z = clean != corrupted
    reinfilled = np.asarray(reinfilled, bool)
    return dict(agree_changed=float((final_codes[z] == clean[z]).mean()) if z.any() else float("nan"),
                agree_set=float((final_codes[reinfilled] == clean[reinfilled]).mean()) if reinfilled.any() else float("nan"))
