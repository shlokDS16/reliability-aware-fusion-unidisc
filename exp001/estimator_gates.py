"""Pass/fail rules of the estimator validity gates (card 8.7, 8.8) as pure functions over probe summaries, so that the same rules
run on the toy network now and on the D0 probe arrays later. Each returns a dict with the numbers used and a boolean `pass`."""
from __future__ import annotations

import numpy as np


def g1_floor(probe_mean: float, floor_mean: float, factor: float = 20.0) -> dict:
    """G1 pass rule: the probe-level mean of the statistic is at least 20 times that probe's own mean floor (same positions)."""
    ratio = probe_mean / floor_mean if floor_mean > 0 else np.inf
    return {"probe_mean": probe_mean, "floor_mean": floor_mean, "ratio": float(ratio), "pass": bool(probe_mean >= factor * floor_mean)}


def g2_blind(max_abs_t2i: float, max_abs_i2t: float, max_inc: float, floor_t2i: float, floor_i2t: float) -> dict:
    """G2 null by construction: |S| and I_inc below the G1 floor at the probes."""
    ok = max_abs_t2i < floor_t2i and max_abs_i2t < floor_i2t and max_inc < max(floor_t2i, floor_i2t)
    return {"pass": bool(ok)}


def g3_injection(mixture_mean: float, naive_mean: float, inc_mean: float, floor: float) -> dict:
    """G3: mixture below the floor; naive equals I_inc within 1e-6 and is above 10 x the floor at the first probe."""
    return {"mixture_below_floor": bool(mixture_mean < floor), "naive_equals_inc": bool(abs(naive_mean - inc_mean) < 1e-6),
            "naive_gt_10_floor": bool(naive_mean > 10 * floor),
            "pass": bool(mixture_mean < floor and abs(naive_mean - inc_mean) < 1e-6 and naive_mean > 10 * floor)}


def g3b_nonsemantic(total_mean: float, between_mean: float, within_content_mean: float, floor: float) -> dict:
    """G3b: total T->I exceeds 10 x the floor, the between-class term carries >= 90 percent of it, within-content below the floor."""
    share = between_mean / total_mean if total_mean > 0 else 0.0
    ok = total_mean > 10 * floor and share >= 0.9 and within_content_mean < floor
    return {"total_gt_10_floor": bool(total_mean > 10 * floor), "between_share": float(share), "within_content_below_floor": bool(within_content_mean < floor), "pass": bool(ok)}


def g4_bias(ratio_r8: float, ratio_r32: float) -> dict:
    """G4: the early/late ratio with R = 8 within 25 percent of the one with R = 32 (both directions are checked by the caller).
    The pilot prints only this agreement, not the ratio itself (e1)."""
    agree = abs(ratio_r8 / ratio_r32 - 1.0) <= 0.25
    return {"agree_within_25pct": bool(agree), "pass": bool(agree)}


def g5_choose_g(by_g: dict) -> dict:
    """G5 granularity. by_g[g] = dict(r_p2, r_p30, early_late) where r_* = S(g)/S(32) per probe (ratio of means over trajectories)
    and early_late = early/late ratio of means with that g; by_g[32] must carry early_late. Registered g = 4 if both per-probe
    ratios lie in [0.77, 1.30] and its early/late ratio is within 25 percent of g = 32's; else g = 8 under the same rule; else
    'chunk-dependent' (H-A1 decided on T->I alone, wording 'T->I only')."""
    ref = by_g[32]["early_late"]
    for g in (4, 8):
        d = by_g.get(g)
        if d is None:
            continue
        ok = all(0.77 <= d[k] <= 1.30 for k in ("r_p2", "r_p30")) and abs(d["early_late"] / ref - 1.0) <= 0.25
        if ok:
            return {"g": g, "chunk_dependent": False}
    return {"g": None, "chunk_dependent": True, "wording": "T->I only"}


def g5_order(s_conf: float, s_rev: float) -> dict:
    """An order difference above 0.3 (relative) makes S_theta the mean over both orders (f_ord = 2)."""
    rel = abs(s_conf - s_rev) / max(abs(s_conf), 1e-12)
    return {"relative_difference": float(rel), "f_ord": 2 if rel > 0.3 else 1}


def g6_rate(n_diff_probe_on: int, n_diff_off_off: int, n: int) -> dict:
    """G6: generation with probes on equals probes off; with nondeterministic kernels the rate of differing sequences must not
    exceed the rate between two probe-off runs."""
    return {"rate_on_vs_off": n_diff_probe_on / n, "rate_off_vs_off": n_diff_off_off / n, "pass": bool(n_diff_probe_on <= n_diff_off_off)}


def nc3_permutation(types, Q, n_perm: int = 1000, seed: int = 0, a="noun", b="function") -> dict:
    """NC-3: permute type labels within a sample; the Q_O / Q_F ratio-of-means distribution must be centred within 0.05 of 1.
    types, Q: lists (one entry per sample) of equal-length sequences."""
    g = np.random.default_rng(seed)
    ratios = []
    for _ in range(n_perm):
        num = den = nn = nd = 0.0
        for t, q in zip(types, Q):
            t = np.asarray(t, dtype=object)[g.permutation(len(t))]
            q = np.asarray(q, float)
            ma, mb = t == a, t == b
            num += q[ma].sum(); nn += ma.sum(); den += q[mb].sum(); nd += mb.sum()
        if nn and nd and den > 0:
            ratios.append((num / nn) / (den / nd))
    c = float(np.median(ratios)) if ratios else float("nan")
    return {"median_ratio": c, "pass": bool(abs(c - 1.0) <= 0.05)}


def nc4_padding(q_post_caption: float, q_function: float) -> dict:
    return {"pass": bool(q_post_caption < q_function), "Q_post": q_post_caption, "Q_function": q_function}


def pc_d_prime(content_stat_p1: float, floor_p1: float, content_stat_p2: float | None, floor_p2: float | None, n_eligible_p1: int) -> dict:
    """PC-D': probe-level mean of the content-term statistic >= 10 x the G1b floor at pass 1 and (if eligible) pass 2; at least 12
    of 16 trajectories eligible at pass 1."""
    ok1 = content_stat_p1 >= 10 * floor_p1 and n_eligible_p1 >= 12
    ok2 = True if content_stat_p2 is None else content_stat_p2 >= 10 * floor_p2
    return {"pass1": bool(ok1), "pass2": bool(ok2), "pass": bool(ok1 and ok2)}


def information_fraction(I_hat_content: np.ndarray, H_mbar: np.ndarray, min_entropy: float = 0.05):
    """Q_j = I_hat^c_j / H(mbar_j), positions with H(mbar_j) < 0.05 nats excluded (8.5). Returns (Q, kept_mask)."""
    keep = H_mbar >= min_entropy
    q = np.where(keep, I_hat_content / np.maximum(H_mbar, 1e-300), np.nan)
    return q, keep


def batch_invariance(forward_single, forward_batch, states, tol=0.0) -> dict:
    """G1a: the same state run alone and inside a batch (different composition / position): max abs difference of the marginals."""
    import torch
    singles = [forward_single(s) for s in states]
    batched = forward_batch(states)
    worst = max(float((a.to(torch.float64) - b.to(torch.float64)).abs().max()) for a, b in zip(singles, batched))
    return {"max_abs_diff": worst, "pass": bool(worst <= tol) if tol else None}
