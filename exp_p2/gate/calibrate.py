"""Conformal risk control calibration of the gate threshold (v1 section 5 + v2 section 6; Alg. 3 and Alg. 4').

Loss of a clean item i at threshold tau: L_i(tau) = (1/m_i) * #{j : u_ij > tau}, in [0,1], non-increasing in tau.
tau_hat = inf{ tau : n/(n+1) * Rhat(tau) + 1/(n+1) <= alpha },  Rhat = mean_i L_i.
Guarantee (conformal risk control, Angelopoulos et al.; citation id still to be validated): for a clean test item exchangeable with the
calibration items, E[L_test(tau_hat)] <= alpha. Nothing about power, nothing under shift, nothing for the clean tokens of corrupted items.

Ties (v2 section 6): calibration AND test suspicions get an independent jitter U(0, eps0) before the comparison, with eps0 below the
smallest non-zero gap between distinct calibration scores (computed here, not chosen). Strict inequality u > tau throughout.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np


@dataclass
class Threshold:
    tau: float                  # +inf = flag nothing (alpha < 1/(n+1)); -inf = flag everything (alpha >= 1)
    alpha: float
    n_cal: int
    eps0: float
    statistic: str
    K: int
    seed: int
    ids_hash: str
    feasible: bool              # False when alpha < 1/(n+1): the finite-sample slack alone exceeds alpha
    r_hat: float                # empirical (jittered) calibration risk at tau
    eps0_resolvable: bool       # False if eps0 is below float64 resolution of the largest score (jitter would not break ties)

    def to_json(self) -> dict:
        d = asdict(self)
        d["tau"] = _enc(self.tau)
        return d

    @staticmethod
    def from_json(d: dict) -> "Threshold":
        d = dict(d)
        d["tau"] = _dec(d["tau"])
        return Threshold(**d)


def _enc(x: float):
    return "inf" if x == float("inf") else "-inf" if x == float("-inf") else float(x)


def _dec(x):
    return float(x) if isinstance(x, str) else x


def ids_hash(ids) -> str:
    return hashlib.sha1(json.dumps(sorted(int(i) for i in ids)).encode()).hexdigest()[:16]


def min_positive_gap(U_list) -> float | None:
    v = np.unique(np.concatenate([np.asarray(u, np.float64).ravel() for u in U_list]))
    return float(np.diff(v).min()) if len(v) > 1 else None


def eps0_from(U_list) -> float:
    """Half the smallest non-zero gap between distinct pooled calibration suspicions (1.0 if all scores are equal: pure random gate)."""
    gap = min_positive_gap(U_list)
    return 0.5 * gap if gap else 1.0


def jitter(u, eps0: float, rng: np.random.Generator) -> np.ndarray:
    u = np.asarray(u, np.float64)
    return u + rng.uniform(0.0, eps0, size=u.shape)


def fit_threshold(U_list, alpha: float, eps0: float, seed: int, *, statistic: str = "q", K: int = 8, ids=()) -> Threshold:
    """U_list: list of per-item suspicion arrays (any lengths). Jitter is drawn here with default_rng(seed)."""
    n = len(U_list)
    if n < 1:
        raise ValueError("need at least one calibration item")
    rng = np.random.default_rng(seed)
    J = [jitter(u, eps0, rng) for u in U_list]
    resolvable = bool(eps0 > 8 * np.spacing(max(float(np.max(np.abs(np.concatenate(J)))), 1e-300)))
    h = ids_hash(ids) if len(ids) else ""
    if alpha >= 1.0:
        return Threshold(float("-inf"), alpha, n, eps0, statistic, K, seed, h, True, 1.0, resolvable)
    r_star = (alpha * (n + 1) - 1.0) / n
    if r_star < 0:
        return Threshold(float("inf"), alpha, n, eps0, statistic, K, seed, h, False, 0.0, resolvable)
    vals = np.concatenate(J)
    w = np.concatenate([np.full(len(u), 1.0 / (n * len(u))) for u in J])
    uv, inv = np.unique(vals, return_inverse=True)
    wu = np.bincount(inv, weights=w)
    tail = np.concatenate([np.cumsum(wu[::-1])[::-1][1:], [0.0]])      # tail[i] = weight of values strictly above uv[i] = Rhat(tau=uv[i])
    ok = tail <= r_star
    i0 = int(np.argmax(ok))                                           # first (smallest) tau that satisfies; tail[-1] = 0 <= r_star always
    return Threshold(float(uv[i0]), alpha, n, eps0, statistic, K, seed, h, True, float(tail[i0]), resolvable)


def flag(u, thr: Threshold, rng: np.random.Generator) -> np.ndarray:
    """Alg. 4': jitter then strict comparison. Returns a bool array, True = flagged (in G)."""
    if thr.tau == float("inf"):
        return np.zeros(np.shape(u), dtype=bool)
    if thr.tau == float("-inf"):
        return np.ones(np.shape(u), dtype=bool)
    return jitter(u, thr.eps0, rng) > thr.tau


def false_alarm_proportion(flags_per_item) -> np.ndarray:
    return np.array([float(np.mean(f)) if len(f) else float("nan") for f in flags_per_item])


# ------------------------------------------------------------------------------------------------ text units (words)
def word_ids_from_pieces(pieces: list[str]) -> np.ndarray:
    """SentencePiece pieces -> word index per piece. A new word starts at a piece that begins with the word-boundary mark U+2581
    (and at piece 0, which in this layout follows <s> without a dummy prefix)."""
    ids, w = [], -1
    for i, p in enumerate(pieces):
        if i == 0 or p.startswith("▁"):
            w += 1
        ids.append(w)
    return np.asarray(ids, dtype=np.int64)


def word_suspicion(u_piece, word_ids) -> np.ndarray:
    """Word score = minimum piece score, i.e. word suspicion = maximum piece suspicion (v1 section 3.2 design choice)."""
    u_piece, word_ids = np.asarray(u_piece, np.float64), np.asarray(word_ids)
    out = np.full(int(word_ids.max()) + 1, -np.inf)
    np.maximum.at(out, word_ids, u_piece)
    return out


def expand_word_flags(flag_word, word_ids) -> np.ndarray:
    """Gating a word masks all its pieces."""
    return np.asarray(flag_word, bool)[np.asarray(word_ids)]
