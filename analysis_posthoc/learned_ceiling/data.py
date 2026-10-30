"""Load the M4 arrays and build the caption-withheld feature table (plan LEARNED-CEILING-PLAN-2026-10-29.md, Section 2).

Delta, z and the GATE flag are loaded as separate arrays and never enter the feature table X.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

COND = ("clean", "jpeg10", "noise0.1", "splice128")
GRID = 32
M = GRID * GRID
RAW = ("B", "D", "q", "s3", "tbv", "ltex", "nbr")          # columns 0..6 of X (the grid model uses only these)
NB3_MEAN = ("q", "B", "s3", "tbv", "ltex", "nbr")
ITEM_STATS = ("q", "B", "s3", "tbv", "ltex", "nbr")
RANKS = ("q", "B", "s3", "tbv")


def feature_names() -> list[str]:
    n = list(RAW) + ["row", "col", "rad"]
    n += [f"nb3mean_{k}" for k in NB3_MEAN] + ["nb3min_q", "nb5mean_q"]
    n += [f"rank_{k}" for k in RANKS]
    n += [f"itemmean_{k}" for k in ITEM_STATS] + [f"itemsd_{k}" for k in ITEM_STATS] + ["itemz_q"]
    return n


def _nb_mean(a: np.ndarray, r: int) -> np.ndarray:
    """Mean over the (2r+1)^2 neighbourhood excluding self, edge-aware. a: [..., 32, 32]."""
    pad = [(0, 0)] * (a.ndim - 2) + [(r, r), (r, r)]
    ap = np.pad(a, pad)
    one = np.pad(np.ones(a.shape[-2:], np.float32), r)
    s = np.zeros_like(a)
    cnt = np.zeros(a.shape[-2:], np.float32)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dy == 0 and dx == 0:
                continue
            s += ap[..., r + dy:r + dy + GRID, r + dx:r + dx + GRID]
            cnt += one[r + dy:r + dy + GRID, r + dx:r + dx + GRID]
    return s / cnt


def _nb_min(a: np.ndarray) -> np.ndarray:
    pad = [(0, 0)] * (a.ndim - 2) + [(1, 1), (1, 1)]
    ap = np.pad(a, pad, constant_values=np.inf)
    out = np.full_like(a, np.inf)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            out = np.minimum(out, ap[..., 1 + dy:1 + dy + GRID, 1 + dx:1 + dx + GRID])
    return out


def _rank(a: np.ndarray) -> np.ndarray:
    """Within-item percentile rank over the last axis (0..1)."""
    return (np.argsort(np.argsort(a, axis=-1), axis=-1) / (a.shape[-1] - 1)).astype(np.float32)


def load(arr_dir: str | Path, n_items: int = 500) -> dict:
    arr_dir = Path(arr_dir)
    N, C = n_items, len(COND)
    raw = {k: np.zeros((N, C, M), np.float32) for k in RAW}
    delta = np.zeros((N, C, M), np.float32)
    z = np.zeros((N, C, M), bool)
    gm = np.zeros((N, C, M), bool)
    codes = np.zeros((N, C, M), np.int64)
    for i in range(N):
        d = np.load(arr_dir / f"item{i:04d}.npz")
        for c, name in enumerate(COND):
            B, D = d[f"{name}_B"].astype(np.float32), d[f"{name}_D"].astype(np.float32)
            raw["B"][i, c], raw["D"][i, c], raw["q"][i, c] = B, D, B - D
            raw["s3"][i, c], raw["tbv"][i, c] = d[f"{name}_s3"], d[f"{name}_tbv"]
            raw["ltex"][i, c] = np.log1p(np.maximum(d[f"{name}_tex"], 0))
            raw["nbr"][i, c] = d[f"{name}_nbr"]
            delta[i, c] = d[f"{name}_delta"]
            z[i, c] = d[f"{name}_z"]
            gm[i, c] = d[f"{name}_flag0.05"]
            codes[i, c] = d[f"{name}_codes"]
    for k, v in raw.items():
        if not np.isfinite(v).all():
            raise ValueError(f"non-finite values in feature {k}")
    return dict(raw=raw, delta=delta, z=z, gm=gm, codes=codes)


def engineer(raw: dict) -> np.ndarray:
    N, C, _ = raw["q"].shape
    cols = [raw[k] for k in RAW]
    rr, cc = np.divmod(np.arange(M), GRID)
    row, col = (rr / (GRID - 1)).astype(np.float32), (cc / (GRID - 1)).astype(np.float32)
    rad = np.sqrt((row - 0.5) ** 2 + (col - 0.5) ** 2).astype(np.float32)
    for p in (row, col, rad):
        cols.append(np.broadcast_to(p, (N, C, M)))
    g = lambda a: a.reshape(N, C, GRID, GRID)
    for k in NB3_MEAN:
        cols.append(_nb_mean(g(raw[k]), 1).reshape(N, C, M))
    cols.append(_nb_min(g(raw["q"])).reshape(N, C, M))
    cols.append(_nb_mean(g(raw["q"]), 2).reshape(N, C, M))
    for k in RANKS:
        cols.append(_rank(raw[k]))
    for k in ITEM_STATS:
        cols.append(np.broadcast_to(raw[k].mean(-1, keepdims=True), (N, C, M)))
    for k in ITEM_STATS:
        cols.append(np.broadcast_to(raw[k].std(-1, keepdims=True), (N, C, M)))
    q = raw["q"]
    cols.append((q - q.mean(-1, keepdims=True)) / (q.std(-1, keepdims=True) + 1e-6))
    X = np.stack([np.asarray(c, np.float32) for c in cols], axis=-1)
    assert X.shape[-1] == len(feature_names())
    return X


def token_subsample(seed_seq: np.random.SeedSequence, shape: tuple, frac: float = 0.25) -> np.ndarray:
    """Fixed, seeded token subsample per item-condition (exactly frac*M tokens each)."""
    rng = np.random.default_rng(seed_seq)
    N, C, m = shape
    k = int(round(frac * m))
    mask = np.zeros(shape, bool)
    for i in range(N):
        for c in range(C):
            mask[i, c, rng.choice(m, k, replace=False)] = True
    return mask
