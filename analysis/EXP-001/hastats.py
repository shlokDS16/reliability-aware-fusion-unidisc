"""H-A and H-C statistics (EXP-001 card v0.5, sections 2, 10.3). Pure numpy.

H-A decision statistic: the composition-standardised ratio pair (pooled and complete-case), percentile bootstrap over
trajectories with the stratum weights omega_s fixed at their full-sample values; supported iff both lower 95% limits >= 1.5;
Negative only if both 97.5% upper limits < 1.5 and R_Q2 fails by the same limits; the h guard blocks Negative/reversed when
h lies outside [0.85, 1.18]. H-C: rho_strat with the exact null (convolution of two n = 8 Spearman permutation distributions).
"""
from __future__ import annotations

import itertools
import math

import numpy as np

STRATA = ("noun", "other", "function")
MIN_OMEGA = 0.10
MIN_OBS = 20


def merge_thin_strata(omega: dict) -> dict:
    """Strata with full-sample weight < 0.10 are merged into 'other' (content). Returns {stratum: merged_into}."""
    return {s: ("other" if (omega[s] < MIN_OMEGA and s != "other") else s) for s in STRATA}


def standardised_ratio(traj, group, stratum, value, omega=None, mapping=None):
    """traj, group (0 early / 1 late), stratum (str), value: aligned 1-D arrays of observations (T->I: one per source probe with
    value S-bar; I->T: one per receiving position with value I_hat^c). Returns (ratio, info). omega and mapping are computed on
    the full sample if not given (then reused inside bootstrap replicates)."""
    traj, group, stratum, value = map(np.asarray, (traj, group, stratum, value))
    if omega is None:
        tot = len(value)
        omega = {s: float(np.sum(stratum == s)) / tot for s in STRATA}
        mapping = merge_thin_strata(omega)
        # weights after merging
        om2 = {}
        for s in STRATA:
            om2[mapping[s]] = om2.get(mapping[s], 0.0) + omega[s]
        omega = om2
    if mapping is None:
        mapping = {s: s for s in STRATA}
    merged = np.array([mapping.get(s, s) for s in stratum])
    num = den = 0.0
    counts = {}
    for s, w in omega.items():
        e = value[(merged == s) & (group == 0)]
        l = value[(merged == s) & (group == 1)]
        counts[s] = (len(e), len(l))
        if len(e) == 0 or len(l) == 0:
            return None, {"empty_stratum": s, "counts": counts, "omega": omega, "mapping": mapping}
        num += w * e.mean()
        den += w * l.mean()
    return (num / den if den > 0 else np.inf), {"counts": counts, "omega": omega, "mapping": mapping}


def thin_stratum_inconclusive(info) -> bool:
    """(d): any stratum with omega >= 0.10 that has fewer than 20 observations at the early or late probes."""
    for s, (ne, nl) in info["counts"].items():
        if info["omega"][s] >= MIN_OMEGA and (ne < MIN_OBS or nl < MIN_OBS):
            return True
    return False


def bootstrap_ratio(traj, group, stratum, value, omega, mapping, B=10000, seed=0):
    """Percentile bootstrap over trajectories (whole trajectories resampled), omega fixed at the full-sample values; replicates
    with an empty stratum are redrawn (redraw share returned). The complete-case variant is this function applied to the
    trajectories that have an observation at all four centre probes (the caller filters)."""
    traj, group, stratum, value = map(np.asarray, (traj, group, stratum, value))
    ids = np.unique(traj)
    by = {t: np.nonzero(traj == t)[0] for t in ids}
    g = np.random.default_rng(seed)
    out, redraws = [], 0
    while len(out) < B:
        pick = g.choice(ids, len(ids))
        sel = np.concatenate([by[t] for t in pick])
        r, _ = standardised_ratio(traj[sel], group[sel], stratum[sel], value[sel], omega, mapping)
        if r is None:
            redraws += 1
            continue
        out.append(r)
    return np.array(out), redraws / (len(out) + redraws)


def decide_direction(ratio_pooled_reps, ratio_cc_reps, rq2_reps, info_pooled, h, noun_share_diff):
    """Per direction. Returns label in {'supported','negative','inconclusive','inconclusive (composition)','reversed'} with
    the limits used. rq2_reps may be None (then Negative cannot be declared)."""
    lo_p, lo_c = np.quantile(ratio_pooled_reps, 0.025), np.quantile(ratio_cc_reps, 0.025)
    hi_p, hi_c = np.quantile(ratio_pooled_reps, 0.975), np.quantile(ratio_cc_reps, 0.975)
    lim = {"lo95_pooled": float(lo_p), "lo95_cc": float(lo_c), "hi975_pooled": float(hi_p), "hi975_cc": float(hi_c)}
    if thin_stratum_inconclusive(info_pooled):
        return "inconclusive (composition)", lim
    if lo_p >= 1.5 and lo_c >= 1.5:
        return "supported", lim
    h_ok = 0.85 <= h <= 1.18
    if not h_ok:
        return "inconclusive (composition)", lim
    rq2_fail = rq2_reps is not None and np.quantile(rq2_reps, 0.975) < 1.5
    if hi_p < 1.5 and hi_c < 1.5 and rq2_fail:
        rev = hi_p < 1.0 and hi_c < 1.0 and np.quantile(rq2_reps, 0.975) < 1.0
        return ("reversed" if rev else "negative"), lim
    return "inconclusive", lim


def condition_r_table(L_R: float, U_R: float) -> str:
    """Decision table for condition R (section 2): (i) L_R > 1.0; (ii) L_R <= 1.0 and U_R < 1.25; (iii) otherwise."""
    if L_R > 1.0:
        return "front-loaded under both position rules tested"
    if U_R < 1.25:
        return "front-loading follows the confidence rule"
    return "not distinguishable at n_R trajectories"


def composition_guard(h_early, h_late, noun_early, noun_late):
    h = h_early / h_late if h_late > 0 else np.inf
    d = noun_early - noun_late
    return {"h": h, "noun_share_diff": d, "h_ok": 0.85 <= h <= 1.18, "noun_ok": abs(d) <= 0.20}


def h_a2_ratio(Q_noun, Q_func) -> float:
    return float(np.mean(Q_noun) / np.mean(Q_func))


# --------------------------------------------------------------------------------------------------------------------- H-C
def _spearman_null(n=8):
    """Distribution of Spearman rho under a uniform permutation: dict {sum d^2: count}."""
    cnt = {}
    for p in itertools.permutations(range(n)):
        s = sum((i - p[i]) ** 2 for i in range(n))
        cnt[s] = cnt.get(s, 0) + 1
    return cnt


_NULL8 = None


def _rho_from_d2(d2, n=8):
    return 1.0 - 6.0 * d2 / (n * (n * n - 1))


def rho_strat_exact_p(obs: float, n_strata: int = 2, n: int = 8):
    """Exact one-sided P(rho_strat >= obs) under independent within-k permutation (convolution of the n = 8 null)."""
    global _NULL8
    if _NULL8 is None:
        _NULL8 = _spearman_null(n)
    total = float(math.factorial(n))
    # represent the sum of rho values by the sum of d2 values (integers): rho_strat = 1 - 6 (d2_1 + d2_2) / (2 n (n^2-1))
    sums = {0: 1.0}
    for _ in range(n_strata):
        new = {}
        for a, pa in sums.items():
            for d2, c in _NULL8.items():
                new[a + d2] = new.get(a + d2, 0.0) + pa * c / total
        sums = new
    k = n * (n * n - 1)
    return float(sum(p for s, p in sums.items() if 1.0 - 6.0 * s / (n_strata * k) >= obs - 1e-12)), sums


def rho_strat_critical(alpha: float = 0.05, n_strata: int = 2, n: int = 8):
    _, sums = rho_strat_exact_p(2.0, n_strata, n)
    k = n * (n * n - 1)
    vals = sorted(((1.0 - 6.0 * s / (n_strata * k), p) for s, p in sums.items()), reverse=True)
    cum, crit, pcrit = 0.0, None, None
    for v, p in vals:
        if cum + p > alpha + 1e-12:
            break
        cum += p
        crit, pcrit = v, cum
    return crit, pcrit


def spearman(x, y):
    rx = np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(float)
    ry = np.argsort(np.argsort(y, kind="stable"), kind="stable").astype(float)
    # average ranks for ties
    def avg_rank(a):
        order = np.argsort(a, kind="stable")
        r = np.empty(len(a))
        i = 0
        while i < len(a):
            j = i
            while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
                j += 1
            r[order[i:j + 1]] = (i + j) / 2.0
            i = j + 1
        return r
    rx, ry = avg_rank(np.asarray(x, float)), avg_rank(np.asarray(y, float))
    rx, ry = rx - rx.mean(), ry - ry.mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


def rho_strat(M_by_k: dict, Delta_by_k: dict) -> float:
    """mean over k of the within-k Spearman correlation of (M_{w,k}, Delta_{w,k}) over w = 1..8."""
    return float(np.mean([spearman(M_by_k[k], Delta_by_k[k]) for k in M_by_k]))


def hc_decision(rho: float, n_strata: int = 2):
    p, _ = rho_strat_exact_p(rho, n_strata)
    return {"rho_strat": rho, "p_exact": p, "supported": bool(rho >= 0.5 and p <= 0.05)}
