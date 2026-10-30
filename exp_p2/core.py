"""Pure numpy logic of the Paper 2 probes: complementary masks, corruptions, AUROC, matching accuracy, bootstrap.
No torch, no model. Everything here is covered by tests/exp_p2/test_core.py."""
from __future__ import annotations

import numpy as np


# ------------------------------------------------------------------------------------------------ complementary masks
def complementary_groups(n: int, k: int, rng: np.random.Generator) -> np.ndarray:
    """Assign each of n positions to one of k groups: a random permutation, position gets group (rank mod k).
    Every position is masked in exactly one of the k passes; group sizes differ by at most one."""
    perm = rng.permutation(n)
    g = np.empty(n, dtype=np.int64)
    g[perm] = np.arange(n) % k
    return g


def groups_from_priority(u: np.ndarray, k: int) -> np.ndarray:
    """Group = rank of the priority u[j] among the n positions, mod k. Two sequences of different length n1, n2 that share a
    leading prefix of priorities (u1 = u[:n1], u2 = u[:n2]) get nearly the same partition shape: this is the common-random-numbers
    device for texts of different length (identical priorities, same K). Ties are broken by position (stable)."""
    order = np.argsort(u, kind="stable")
    g = np.empty(len(u), dtype=np.int64)
    g[order] = np.arange(len(u)) % k
    return g


def masks_from_groups(groups: np.ndarray, k: int) -> list[np.ndarray]:
    """List of index arrays, one per non-empty group (empty groups are skipped)."""
    out = [np.nonzero(groups == j)[0] for j in range(k)]
    return [m for m in out if len(m)]


# ------------------------------------------------------------------------------------------------ corruptions (token level)
def token_swap(codes: np.ndarray, frac: float, vocab: int, rng: np.random.Generator) -> np.ndarray:
    """Replace a random frac of the tokens by uniform random codes (the position set is exactly round(frac * n))."""
    out = codes.copy()
    n = len(codes)
    m = int(round(frac * n))
    idx = rng.choice(n, size=m, replace=False)
    out[idx] = rng.integers(0, vocab, size=m)
    return out


def patch_occlusion(codes: np.ndarray, grid: int, patch: int, vocab: int, rng: np.random.Generator) -> np.ndarray:
    """Replace a patch x patch block of the grid x grid token map (random top-left corner, fully inside) by uniform random codes."""
    assert len(codes) == grid * grid
    top = int(rng.integers(0, grid - patch + 1))
    left = int(rng.integers(0, grid - patch + 1))
    m = codes.reshape(grid, grid).copy()
    m[top:top + patch, left:left + patch] = rng.integers(0, vocab, size=(patch, patch))
    return m.reshape(-1)


def corrupted_mask(clean: np.ndarray, corrupted: np.ndarray) -> np.ndarray:
    """A token is 'corrupted' iff its code differs from the clean image's code."""
    return clean != corrupted


# ------------------------------------------------------------------------------------------------ metrics
def _rankdata(x: np.ndarray) -> np.ndarray:
    """Average ranks (1-based), ties get the mean rank."""
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    ranks = np.empty(len(x), dtype=np.float64)
    i = 0
    n = len(x)
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def auroc(score: np.ndarray, positive: np.ndarray) -> float:
    """AUROC of `score` (higher = more likely positive) against the boolean labels `positive`; ties count 1/2. NaN if a class is empty."""
    score = np.asarray(score, dtype=np.float64)
    positive = np.asarray(positive, dtype=bool)
    n_pos = int(positive.sum())
    n_neg = len(positive) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    r = _rankdata(score)
    return float((r[positive].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def match_indicator(s_true: np.ndarray, s_mis: np.ndarray) -> np.ndarray:
    """1 if the true pair scores higher than the mismatched pair, 0.5 on an exact tie, else 0."""
    s_true, s_mis = np.asarray(s_true, float), np.asarray(s_mis, float)
    return np.where(s_true > s_mis, 1.0, np.where(s_true == s_mis, 0.5, 0.0))


def bootstrap_mean_ci(x: np.ndarray, n_boot: int = 10000, seed: int = 0, alpha: float = 0.05) -> tuple[float, float, float]:
    """Mean and percentile bootstrap CI over items (NaNs dropped). Returns (mean, lo, hi)."""
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    means = x[idx].mean(axis=1)
    return float(x.mean()), float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def derangement(n: int, rng: np.random.Generator) -> np.ndarray:
    """Random permutation without fixed points (rejection sampling; expected ~e attempts)."""
    assert n >= 2
    while True:
        p = rng.permutation(n)
        if not np.any(p == np.arange(n)):
            return p
