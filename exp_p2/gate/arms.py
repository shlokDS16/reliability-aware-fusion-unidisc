"""Gate arms (v2 sections 4.3, 7.4; Alg. 10). A gate is a boolean array over the m image tokens (True = in G, i.e. withdrawn/re-masked);
the included set is R = ~G. The no-gate arm is the empty gate."""
from __future__ import annotations

import numpy as np


def no_gate(m: int) -> np.ndarray:
    return np.zeros(m, dtype=bool)


def changed_code_gate(clean: np.ndarray, observed: np.ndarray) -> np.ndarray:
    """v2 'changed-code gate' G^chg = {j : Z_j = 1} (v1's 'oracle'; NOT an evidence oracle, see v2 7.4)."""
    return np.asarray(clean) != np.asarray(observed)


def topk_gate(score: np.ndarray, k: int) -> np.ndarray:
    """Flag the k largest values of `score` (higher = more suspicious); ties broken by position (stable). Used for plain-B top-k
    (score = -B) and s3 top-k with k = |G| of GATE-M (equal size, no calibration)."""
    score = np.asarray(score, np.float64)
    k = int(min(max(k, 0), len(score)))
    g = np.zeros(len(score), dtype=bool)
    if k:
        order = np.argsort(-score, kind="stable")
        g[order[:k]] = True
    return g


def scattered_gate(n_flag: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """Scattered random gate: same size as GATE's, uniform positions (v2 7.4)."""
    g = np.zeros(m, dtype=bool)
    k = int(min(max(n_flag, 0), m))
    if k:
        g[rng.choice(m, size=k, replace=False)] = True
    return g


def geometry_matched_gate(G: np.ndarray, grid: int, rng: np.random.Generator) -> np.ndarray:
    """Alg. 10: GATE's own mask translated by a uniformly random non-zero shift (dx, dy) on the grid x grid torus. Same size, same shape,
    different place. The empty gate maps to the empty gate (the rng is still advanced so that seeds stay aligned across items)."""
    G = np.asarray(G, bool)
    assert G.size == grid * grid
    s = int(rng.integers(0, grid * grid - 1)) + 1          # uniform over the grid^2 - 1 non-zero shifts
    dy, dx = divmod(s, grid)
    return np.roll(G.reshape(grid, grid), shift=(dy, dx), axis=(0, 1)).reshape(-1)


def random_word_gate(n_words: int, n_flag: int, rng: np.random.Generator) -> np.ndarray:
    """Text analogue of the random gate: n_flag random words out of n_words (word-level mask)."""
    return scattered_gate(n_flag, n_words, rng)


def arm_rng(seed: int, gid: int, cond_index: int, arm_tag: int, rep: int) -> np.random.Generator:
    """Deterministic rng per (item, condition, arm, repetition); the tags are fixed numbers, not strings (stable across runs)."""
    return np.random.default_rng([seed, gid, cond_index, arm_tag, rep])


ARM_TAG = dict(jitter=1, geo=2, scattered=3, tbv=4, rand=5,
               s2_gate_order=6, s2_rand_set=7, s2_rand_order=8, s2_chg_order=9, s2_leak_order=10, s2_sample=11)
"""Tags 1-5 are the M4 streams and are unchanged. 6-11 are the S2 re-infill streams (reinfill.py): the visiting order of the flagged set, the equal-size random set and its order,
the order of the changed-code set, the order of the caption-visible leakage control, and the sampling seed of every draw. `arm_rng(seed, gid, cond_index, tag, rep)` takes the draw number as `rep`."""
