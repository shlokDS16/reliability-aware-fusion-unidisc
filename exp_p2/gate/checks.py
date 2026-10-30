"""Checks that touch the model (v1 L10; v2 Alg. 12 coherence test, M5). Pure index logic is separated so it can be unit-tested with the fake network.

Coherence gap (Alg. 12), for two image tokens j, k, with context R (all other image tokens visible, or a random half of them masked; caption masked):
    g = [log p(x_j | R) + log p(x_k | R, x_j)] - [log p(x_k | R) + log p(x_j | R, x_k)]        zero for a coherent (joint-consistent) model.
Three passes per (pair, context): {j,k} masked -> log p(x_j|R), log p(x_k|R); only k masked (j revealed) -> log p(x_k|R,x_j); only j masked -> log p(x_j|R,x_k).
Noise floor g0 = gap of a repeat of the same passes in a different batch composition (reversed order, different batch size); the reading is fixed in advance:
  coherent within numerical noise  : median |g| <= 95th percentile of |g0|
  incoherent at the evidence scale : median |g| >  mu, the clean mean per-token paired evidence measured in M4.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from exp_p2.gate import dcache
from exp_p2.scoring import Spec, masked_logprobs, IMG_LO, IMG_HI, SDPA_BS


def l10_once(sc, run: Path, n: int = 8, atol: float = 1e-5) -> dict:
    """Layout-only check of the cached nulls (v1 L10, 4 passes), written once to <run>/l10.json; raises if it fails (the caches would be invalid)."""
    p = Path(run) / "l10.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf8"))
    cap_a, cap_b = [100 + i for i in range(n)], [900 + i for i in range(n)]
    ca, cb = np.zeros(sc.L_I, np.int64), (np.arange(sc.L_I) * 7) % 16384
    r = dcache.check_layout_only(sc, cap_a, cap_b, ca, cb, atol=atol)
    p.write_text(json.dumps(r, indent=1), encoding="utf8")
    if not r["ok"]:
        raise RuntimeError(f"L10 failed: nulls depend on content ({r}); do not use the null cache")
    return r


# ------------------------------------------------------------------------------------------------ coherence test (pure index logic)
def coherence_pairs(grid: int, rng: np.random.Generator, min_sep: int = 8) -> list[dict]:
    """4 pairs per item: one horizontally and one vertically adjacent, two at Chebyshev distance >= min_sep on the grid."""
    def pos(y, x):
        return y * grid + x
    out = []
    y, x = int(rng.integers(0, grid)), int(rng.integers(0, grid - 1))
    out.append(dict(j=pos(y, x), k=pos(y, x + 1), kind="adjacent_h"))
    y, x = int(rng.integers(0, grid - 1)), int(rng.integers(0, grid))
    out.append(dict(j=pos(y, x), k=pos(y + 1, x), kind="adjacent_v"))
    for _ in range(2):
        while True:
            y1, x1, y2, x2 = (int(v) for v in rng.integers(0, grid, 4))
            if max(abs(y1 - y2), abs(x1 - x2)) >= min_sep:
                break
        out.append(dict(j=pos(y1, x1), k=pos(y2, x2), kind="far"))
    return out


def half_masks(m: int, pairs: list[dict], rng: np.random.Generator) -> list[np.ndarray]:
    """Per pair, a random half of the OTHER image tokens (never j or k) to be masked in context 2."""
    out = []
    for p in pairs:
        others = np.array([t for t in range(m) if t not in (p["j"], p["k"])])
        out.append(np.sort(rng.permutation(others)[:len(others) // 2]))
    return out


def coherence_gaps(sc, st: dict, pairs: list[dict], halves: list[np.ndarray], *, bs: int = SDPA_BS, reverse: bool = False) -> np.ndarray:
    """Gap g for every (pair, context) -> array [n_pairs, 2] (context 0 = all other image tokens visible, 1 = random half masked).
    3 passes per (pair, context); `reverse` and `bs` change the batch composition (used for the noise floor)."""
    base, cap, img = st["base"], st["cap_pos"], st["img_pos"]
    specs, keys = [], []
    for pi, p in enumerate(pairs):
        for ctx in (0, 1):
            extra = cap if ctx == 0 else torch.cat([cap, img[torch.as_tensor(halves[pi], device=img.device)]])
            j, k = img[p["j"]], img[p["k"]]
            specs += [Spec(torch.stack([j, k]), IMG_LO, IMG_HI, extra=extra), Spec(k[None], IMG_LO, IMG_HI, extra=extra), Spec(j[None], IMG_LO, IMG_HI, extra=extra)]
            keys += [(pi, ctx, "jk"), (pi, ctx, "k|j"), (pi, ctx, "j|k")]
    order = list(range(len(specs)))[::-1] if reverse else list(range(len(specs)))
    res = {}
    for o, lp in zip(order, masked_logprobs(sc.logits_fn(st), base, [specs[o] for o in order], bs=bs)):
        res[keys[o]] = lp
    g = np.zeros((len(pairs), 2))
    for pi, p in enumerate(pairs):
        cj, ck = int(base[img[p["j"]]]) - IMG_LO, int(base[img[p["k"]]]) - IMG_LO
        for ctx in (0, 1):
            lp_jk = res[(pi, ctx, "jk")]
            a = float(lp_jk[0, cj]) + float(res[(pi, ctx, "k|j")][0, ck])
            b = float(lp_jk[1, ck]) + float(res[(pi, ctx, "j|k")][0, cj])
            g[pi, ctx] = a - b
    return g


def coherence_summary(g: np.ndarray, g0: np.ndarray, mu: float | None = None) -> dict:
    """g: all gaps (any shape); g0: noise-floor differences (repeat minus original). Applies the pre-stated reading."""
    g, g0 = np.abs(np.asarray(g, float).ravel()), np.abs(np.asarray(g0, float).ravel())
    med, p95 = float(np.median(g)), float(np.quantile(g0, 0.95)) if g0.size else float("nan")
    out = dict(median_abs_gap=med, p95_abs_noise_floor=p95, n_gaps=int(g.size), n_floor=int(g0.size), mu=mu,
               coherent_within_noise=bool(g0.size and med <= p95))
    out["incoherent_at_evidence_scale"] = None if mu is None else bool(med > mu)
    return out
