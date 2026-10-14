"""Metric pipeline (EXP-001 card v0.5, sections 7.1-7.4, 10.1-10.2). Pure numpy; inputs are L2-normalised embeddings or
precomputed n x n similarity matrices, so every bootstrap replicate recomputes the shuffled baseline cheaply.

Lift_i = 100 (C_i - B_i); C_i = S[i,i]; B_i = 0.5 [mean_{j!=i} S[j,i] + mean_{j!=i} S[i,j]] with S[a,b] = cos(e_I(x_a), e_T(c_b)).
psi_i = 100 (C_i - 2 B_i) is the per-seed influence value (Hajek projection).
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------------------------------------------- lift


def sim_matrix(E_img: np.ndarray, E_txt: np.ndarray) -> np.ndarray:
    return E_img.astype(np.float64) @ E_txt.astype(np.float64).T


def lift_terms(S: np.ndarray, exclude: np.ndarray | None = None):
    """C [n], B [n]. `exclude` [n, n] bool marks pairs that must not enter the baseline (duplicate seed draws)."""
    n = S.shape[0]
    C = np.diag(S).copy()
    ok = ~np.eye(n, dtype=bool) if exclude is None else ~exclude & ~np.eye(n, dtype=bool)
    cnt = ok.sum(1)
    row = (S * ok).sum(1) / np.maximum(cnt, 1)            # mean_{j} S[i, j]
    cnt_c = ok.sum(0)
    col = (S * ok).sum(0) / np.maximum(cnt_c, 1)          # mean_{j} S[j, i]
    return C, 0.5 * (row + col)


def lift(S: np.ndarray, exclude=None) -> np.ndarray:
    C, B = lift_terms(S, exclude)
    return 100.0 * (C - B)


def psi(S: np.ndarray) -> np.ndarray:
    C, B = lift_terms(S)
    return 100.0 * (C - 2.0 * B)


def completion_increment(S_full: np.ndarray, S_prefix: np.ndarray) -> np.ndarray:
    """Per-seed Lift(full) - Lift(prefix-only) (7.1). Read only as a contrast across arms (R-b)."""
    return lift(S_full) - lift(S_prefix)


# ------------------------------------------------------------------------------------------------------------- bootstrap


def _stat(S: np.ndarray, idx: np.ndarray, which: str) -> float:
    sub = S[np.ix_(idx, idx)]
    excl = idx[:, None] == idx[None, :]
    C, B = lift_terms(sub, excl)
    if which == "lift":
        return 100.0 * float((C - B).mean())
    if which == "C":
        return float(C.mean())
    if which == "B":
        return float(B.mean())
    raise ValueError(which)


def paired_bootstrap(SA: np.ndarray, SB: np.ndarray | None, B: int = 10000, seed: int = 0, which: str = "lift") -> np.ndarray:
    """Replicates of mean(stat(A)) - mean(stat(B)) over paired seeds (same resampled seed index in both arms); SB None gives the
    single-arm statistic. The shuffled baseline is recomputed inside each replicate; partners with the same original seed index
    are excluded when a seed is drawn twice (10.1)."""
    n = SA.shape[0]
    g = np.random.default_rng(seed)
    out = np.empty(B)
    for b in range(B):
        idx = g.integers(0, n, n)
        v = _stat(SA, idx, which)
        if SB is not None:
            v -= _stat(SB, idx, which)
        out[b] = v
    return out


def point_contrast(SA, SB, which="lift"):
    n = SA.shape[0]
    idx = np.arange(n)
    return _stat(SA, idx, which) - (0.0 if SB is None else _stat(SB, idx, which))


def percentile_ci(theta: np.ndarray, level: float = 0.95):
    a = (1 - level) / 2
    return float(np.quantile(theta, a)), float(np.quantile(theta, 1 - a))


def two_sided_p(theta: np.ndarray) -> float:
    """R5: p = 2 min{(1+#{theta*<=0})/(B+1), (1+#{theta*>=0})/(B+1)}, capped at 1."""
    B = len(theta)
    lo = (1 + np.sum(theta <= 0)) / (B + 1)
    hi = (1 + np.sum(theta >= 0)) / (B + 1)
    return float(min(1.0, 2 * min(lo, hi)))


def needs_rerun(p: float, threshold: float, B: int) -> bool:
    """R5: rerun with B = 100,000 if p lies within 2 sqrt(p(1-p)/B) of the Holm threshold it is compared with."""
    return abs(p - threshold) <= 2 * np.sqrt(max(p * (1 - p), 0) / B)


def arm_swap_test(EA_img, EA_txt, EB_img, EB_txt, draws=10000, seed=0) -> float:
    """O8 sensitivity: swap the two arms' samples (image and caption together) within seed with probability 1/2, recompute both
    baselines from embeddings, compare |contrast| with the observed one. Reported, not decisive."""
    n = EA_img.shape[0]
    g = np.random.default_rng(seed)
    obs = point_contrast(sim_matrix(EA_img, EA_txt), sim_matrix(EB_img, EB_txt))
    cnt = 0
    for _ in range(draws):
        sw = (g.random(n) < 0.5)[:, None]
        Ai, At = np.where(sw, EB_img, EA_img), np.where(sw, EB_txt, EA_txt)
        Bi, Bt = np.where(sw, EA_img, EB_img), np.where(sw, EA_txt, EB_txt)
        cnt += abs(point_contrast(sim_matrix(Ai, At), sim_matrix(Bi, Bt))) >= abs(obs) - 1e-12
    return (1 + cnt) / (draws + 1)


# ----------------------------------------------------------------------------------------------- multiplicity and classes


def holm(pvals: dict, alpha: float = 0.05) -> dict:
    """Holm step-down; returns {name: (adjusted_p, reject)}. A test that is not run enters with p = 1."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for k, (name, p) in enumerate(items):
        adj = min(1.0, (m - k) * p)
        running = max(running, adj)
        out[name] = (running, running <= alpha)
    return out


def fixed_sequence(p_primary: float, p_secondary: dict, alpha: float = 0.05) -> dict:
    """10.2: step 1 H-B1 two-sided alpha; step 2, only if step 1 rejects, Holm over the four secondary tests. Otherwise the four
    are reported with Holm-adjusted p and labelled exploratory."""
    primary_reject = p_primary <= alpha
    h = holm(p_secondary, alpha)
    return {"primary": (p_primary, primary_reject),
            "secondary": {k: (v[0], v[1] and primary_reject) for k, v in h.items()},
            "secondary_label": "confirmatory" if primary_reject else "exploratory"}


def outcome_class(d: float, lo: float, hi: float, p_adj: float, m: float = 1.0, alpha: float = 0.05) -> str:
    """R4: positive (p<=alpha, d>0; 'at or above the MEI' if d>=m), reversed (same, d<0), null (lo,hi inside (-m,m)), else
    inconclusive."""
    if p_adj <= alpha and d > 0:
        return "positive (at or above the MEI)" if d >= m else "positive"
    if p_adj <= alpha and d < 0:
        return "reversed"
    if lo > -m and hi < m:
        return "null"
    return "inconclusive"


# -------------------------------------------------------------------------------------------- reading conditions and guardrails


def reading_conditions(SA, SB, Sp_A, Sp_B, V_contrast_reps, B=10000, seed=0) -> dict:
    """7.4: R-a (95% interval of dC > 0), R-b (95% interval of the completion-increment contrast lower limit > 0),
    R-c (90% interval of the V-lift contrast lower limit > 0). SA/SB full-caption similarity matrices of the two arms,
    Sp_A/Sp_B the prefix-only ones. V_contrast_reps: bootstrap replicates of the V-lift contrast (or None)."""
    n = SA.shape[0]
    g = np.random.default_rng(seed)
    dC = np.empty(B); dB = np.empty(B); dInc = np.empty(B); dPre = np.empty(B)
    for b in range(B):
        idx = g.integers(0, n, n)
        ex = idx[:, None] == idx[None, :]
        subs = [M[np.ix_(idx, idx)] for M in (SA, SB, Sp_A, Sp_B)]
        (CA, BA), (CB, BB), (CpA, BpA), (CpB, BpB) = [lift_terms(s, ex) for s in subs]
        dC[b] = (CA - CB).mean()
        dB[b] = (BA - BB).mean()
        incA = 100 * ((CA - BA) - (CpA - BpA))
        incB = 100 * ((CB - BB) - (CpB - BpB))
        dInc[b] = (incA - incB).mean()
        dPre[b] = 100 * ((CpA - BpA) - (CpB - BpB)).mean()
    out = {"R-a": {"ci95": percentile_ci(dC, 0.95)}, "R-b": {"ci95": percentile_ci(dInc, 0.95)},
           "dB_neg100_ci95": percentile_ci(-100 * dB, 0.95), "dC100_ci95": percentile_ci(100 * dC, 0.95),
           "prefix_only_lift_contrast_ci95": percentile_ci(dPre, 0.95)}
    out["R-a"]["pass"] = out["R-a"]["ci95"][0] > 0
    out["R-b"]["pass"] = out["R-b"]["ci95"][0] > 0
    if V_contrast_reps is not None:
        ci = percentile_ci(V_contrast_reps, 0.90)
        out["R-c"] = {"ci90": ci, "pass": ci[0] > 0}
    else:
        out["R-c"] = {"ci90": None, "pass": None}
    return out


def guardrails(a: dict, j: dict, sd_clipiqa_j: float, sd_kid_j: float) -> dict:
    """7.3 guardrails (i)-(vii), point estimates. a, j: dicts for DA and J with keys comp_len, img_cos, cap_cos, empty_rate,
    trunc77_rate, clipiqa, kid, presence."""
    g = {
        "i_length": 0.8 <= a["comp_len"] / j["comp_len"] <= 1.25,
        "ii_img_diversity": abs(a["img_cos"] - j["img_cos"]) <= 0.01,
        "iib_cap_diversity": abs(a["cap_cos"] - j["cap_cos"]) <= 0.01,
        "iii_empty": a["empty_rate"] - j["empty_rate"] <= 0.02,
        "iv_trunc77": abs(a["trunc77_rate"] - j["trunc77_rate"]) <= 0.05,
        "v_clipiqa": a["clipiqa"] >= j["clipiqa"] - 0.2 * sd_clipiqa_j,
        "vi_kid": a["kid"] <= j["kid"] + sd_kid_j,
        "vii_presence": a["presence"] >= j["presence"] - 0.03,
    }
    g["all_pass"] = all(g.values())
    return g


def mean_pairwise_cos(E: np.ndarray) -> float:
    n = E.shape[0]
    S = E @ E.T
    return float((S.sum() - np.trace(S)) / (n * (n - 1)))


def vlift(s_matched: np.ndarray, s_pi1: np.ndarray, s_pi2: np.ndarray) -> np.ndarray:
    """7.2: V_i = s(x_i, c_i) - 0.5 [ s(x_i, c_pi1(i)) + s(x_pi2(i), c_i) ] with two fixed derangements."""
    return s_matched - 0.5 * (s_pi1 + s_pi2)


def derangement(n: int, seed: int) -> np.ndarray:
    """Fixed derangement (no fixed point) from a seed, by rejection on a shifted permutation (deterministic)."""
    g = np.random.default_rng(seed)
    while True:
        p = g.permutation(n)
        if not np.any(p == np.arange(n)):
            return p
