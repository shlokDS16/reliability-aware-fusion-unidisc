"""Statistics of EXP-003 (card v0.3.2, sections 4, 5, 7). numpy/scipy only; no model, no file access.

Prefix record (one per prefix and arm), a dict:
  ok        both seeds generated
  D         [D0, D1]            discordant noun surfaces of seed 0 and 1 (nouns this completion names and the sibling's does not)
  own, sib  [a0, a1], [b0, b1]  y(n, own image) and y(n, sibling image) for n in D[e] (arrays of 0/1)
  pown, psib  same for the placebo nouns of each seed (NC-2)
  q         [iqa0, iqa1]        CLIP-IQA of the two images (quality-matched sensitivity)
Every statistic is a ratio of sums over prefixes, so a bootstrap replicate is cheap and uses the same resampled prefix indices in every arm.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm

MEI = 0.10


# ------------------------------------------------------------------------------------------------------ discordance and links
def discordant(N0, N1, keyfn):
    k0, k1 = {keyfn(n) for n in N0}, {keyfn(n) for n in N1}
    return [n for n in N0 if keyfn(n) not in k1], [n for n in N1 if keyfn(n) not in k0]


def L_p(own, sib) -> float:
    """Seed-balanced link of one prefix: (1/2) sum_e mean_{n in D_pe} (y(n, own) - y(n, sibling)); NaN unless both sides are non-empty."""
    if len(own[0]) == 0 or len(own[1]) == 0:
        return float("nan")
    return 0.5 * sum(float(np.mean(np.asarray(own[e], float) - np.asarray(sib[e], float))) for e in (0, 1))


def ratio_parts(own, sib):
    """v0.1 instance-weighted ratio Lambda_d: (numerator, denominator) of one prefix."""
    num = sum(float(np.sum(np.asarray(own[e], float) - np.asarray(sib[e], float))) for e in (0, 1))
    return num, float(len(own[0]) + len(own[1]))


def arm_L(recs, own="own", sib="sib") -> np.ndarray:
    return np.array([L_p(r[own], r[sib]) if r.get("ok", True) else np.nan for r in recs], float)


def arm_ratio(recs):
    nd = [ratio_parts(r["own"], r["sib"]) if r.get("ok", True) else (0.0, 0.0) for r in recs]
    return np.array([a for a, _ in nd]), np.array([b for _, b in nd])


def lam_parts(L):
    """(numerator, denominator) arrays of Lambda_b over eligible prefixes."""
    el = ~np.isnan(L)
    return np.where(el, L, 0.0), el.astype(float)


def contrast_parts(LA, LB):
    """Lambda_b(A) - Lambda_b(B) on the prefixes eligible in both arms."""
    com = (~np.isnan(LA)) & (~np.isnan(LB))
    return np.where(com, LA - LB, 0.0), com.astype(float)


def point(parts):
    num, den = parts
    return float(num.sum() / den.sum()) if den.sum() > 0 else float("nan")


def jackknife(parts):
    num, den = parts
    n = len(num)
    S, D = num.sum(), den.sum()
    d = D - den
    return np.where(d > 0, (S - num) / np.where(d > 0, d, 1.0), np.nan)


# ------------------------------------------------------------------------------------------------------------------- bootstrap
def bootstrap(parts, B=10000, seed=0):
    """Percentile-cluster bootstrap replicates, shape [B, len(parts)]; the SAME resampled prefix indices for every statistic. A replicate with
    a zero denominator in any statistic is redrawn; returns (replicates, number of redrawn replicates)."""
    n = len(parts[0][0])
    g = np.random.default_rng(seed)
    out = np.empty((B, len(parts)))
    todo = np.arange(B)
    redraws = 0
    while len(todo):
        idx = g.integers(0, n, (len(todo), n))
        vals = np.empty((len(todo), len(parts)))
        ok = np.ones(len(todo), bool)
        for k, (num, den) in enumerate(parts):
            d = den[idx].sum(1)
            ok &= d > 0
            vals[:, k] = num[idx].sum(1) / np.where(d > 0, d, 1.0)
        out[todo[ok]] = vals[ok]
        redraws += int((~ok).sum())
        todo = todo[~ok]
    return out, redraws


def percentile_ci(theta, level=0.95):
    a = (1 - level) / 2
    return float(np.quantile(theta, a)), float(np.quantile(theta, 1 - a))


def bca_ci(theta, theta_hat, jack, level=0.95):
    """BCa interval of a bootstrap distribution `theta` for the estimate `theta_hat` with leave-one-cluster-out values `jack`."""
    theta = np.asarray(theta)
    p0 = np.clip((np.sum(theta < theta_hat) + 0.5 * np.sum(theta == theta_hat)) / len(theta), 1e-6, 1 - 1e-6)
    z0 = norm.ppf(p0)
    j = np.asarray(jack)[~np.isnan(jack)]
    dj = j.mean() - j
    den = 6.0 * (np.sum(dj ** 2) ** 1.5)
    acc = float(np.sum(dj ** 3) / den) if den > 0 else 0.0
    out = []
    for q in ((1 - level) / 2, 1 - (1 - level) / 2):
        z = norm.ppf(q)
        a = norm.cdf(z0 + (z0 + z) / (1 - acc * (z0 + z)))
        out.append(float(np.quantile(theta, np.clip(a, 0, 1))))
    return out[0], out[1]


def two_sided_p(theta) -> float:
    """Card 7 / EXP-001 10.1 (R5): p = 2 min{(1 + #{theta* <= 0})/(B + 1), (1 + #{theta* >= 0})/(B + 1)}, capped at 1."""
    B = len(theta)
    return float(min(1.0, 2 * min((1 + np.sum(theta <= 0)) / (B + 1), (1 + np.sum(theta >= 0)) / (B + 1))))


def needs_rerun(p, threshold, B) -> bool:
    return bool(abs(p - threshold) <= 2 * math.sqrt(max(p * (1 - p), 0.0) / B))


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, run = len(items), {}, 0.0
    for j, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - j) * p))
        out[k] = run
    return out


# -------------------------------------------------------------------------------------------------------------- decisions (sec 5)
def outcome_class(d, ci_pct95, ci_bca95, p, ci_pct90, ci_bca90, m=MEI, alpha=0.05) -> str:
    """Delta1 outcome class. Positive/Reversed need p <= alpha AND agreement of the BCa 95 percent interval with the percentile interval
    (both exclude 0 on the same side); Null needs the percentile AND BCa 90 percent intervals inside (-m, +m); else Inconclusive."""
    if p <= alpha and d > 0 and ci_pct95[0] > 0 and ci_bca95[0] > 0:
        return "positive_at_or_above_MEI" if d >= m else "positive"
    if p <= alpha and d < 0 and ci_pct95[1] < 0 and ci_bca95[1] < 0:
        return "reversed"
    if ci_pct90[0] > -m and ci_pct90[1] < m and ci_bca90[0] > -m and ci_bca90[1] < m:
        return "null"
    return "inconclusive"


def contrast_report(name, parts, B, seed, m=MEI):
    """Point, percentile and BCa intervals (95 and 90 percent), R5 p-value (with the B = 100,000 rerun flag) of one contrast."""
    th, red = bootstrap([parts], B, seed)
    th = th[:, 0]
    d = point(parts)
    jk = jackknife(parts)
    r = dict(name=name, d=d, n_prefix=int(parts[1].sum()), pct95=percentile_ci(th, .95), bca95=bca_ci(th, d, jk, .95),
             pct90=percentile_ci(th, .90), bca90=bca_ci(th, d, jk, .90), p=two_sided_p(th), redraws=red, B=B)
    r["sd"] = float(np.std(th, ddof=1))
    return r


def identity_four_arm(LG, LP64, LO0, LP32):
    """On the prefixes eligible in all four arms: Delta1 = Delta2a + Delta2b + (L(P32) - L(P64)) (exact)."""
    com = ~(np.isnan(LG) | np.isnan(LP64) | np.isnan(LO0) | np.isnan(LP32))
    f = lambda L: float(np.mean(L[com])) if com.any() else float("nan")
    d1, d2a, d2b, t = f(LG) - f(LP64), f(LG) - f(LO0), f(LO0) - f(LP32), f(LP32) - f(LP64)
    return dict(n_common=int(com.sum()), delta1=d1, delta2a=d2a, delta2b=d2b, plain_doubling_term=t, residual=d1 - (d2a + d2b + t))


def nc_pass(ci95, half_width_max=0.10):
    """NC-1 / NC-2 pass: 95 percent interval contains 0 and half-width at most 0.10."""
    lo, hi = ci95
    return bool(lo <= 0 <= hi and (hi - lo) / 2 <= half_width_max)


def quality_matched(L, q, B=10000, seed=0):
    """Lambda_b on the prefixes whose two images differ in CLIP-IQA by less than the median absolute sibling difference, and the slope of L_p
    on the absolute sibling difference (cluster bootstrap)."""
    dq = np.array([abs(a[0] - a[1]) if a is not None else np.nan for a in q], float)
    el = ~np.isnan(L) & ~np.isnan(dq)
    if el.sum() < 4:
        return dict(n=int(el.sum()))
    med = float(np.median(dq[el]))
    match = el & (dq < med)
    parts = lam_parts(np.where(match, L, np.nan))
    th, _ = bootstrap([parts], B, seed)
    x, y = dq[el], L[el]
    slope = float(np.polyfit(x, y, 1)[0]) if x.std() > 0 else float("nan")
    g = np.random.default_rng(seed + 1)
    idx_all = np.where(el)[0]
    sl = []
    for _ in range(min(B, 2000)):
        s = g.integers(0, len(idx_all), len(idx_all))
        xs, ys = dq[idx_all[s]], L[idx_all[s]]
        if xs.std() > 0:
            sl.append(np.polyfit(xs, ys, 1)[0])
    return dict(n_matched=int(match.sum()), median_abs_sibling_iqa_diff=med, lambda_b_matched=point(parts), ci95=percentile_ci(th[:, 0]),
                slope=slope, slope_ci95=percentile_ci(np.array(sl)) if sl else None)


def sample_size(sd_paired, n_pilot_eligible=None, factor=1.21, mei=MEI, z_a=1.96, z_b=1.2816):
    """Card 7: sigma_d,up = 1.21 x pilot SD of the paired per-prefix difference; n_req = ceil(((z_a + z_b) sigma_up / MEI)^2)."""
    up = factor * sd_paired
    return up, int(math.ceil(((z_a + z_b) * up / mei) ** 2))
