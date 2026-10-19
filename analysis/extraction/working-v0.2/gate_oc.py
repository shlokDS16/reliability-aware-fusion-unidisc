"""Operating characteristics of the v0.2 gate rules (simulation; seed fixed). Not a result about any paper."""
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261020)
SIMS = 2000
BOOT = 1000


def beta_params(p, rho):
    k = 1.0 / rho - 1.0
    return p * k, (1 - p) * k


def lower_bound_ratio(num, den, strata, rng):
    """5th percentile of the pooled ratio sum(num)/sum(den) under a stratified cluster bootstrap."""
    idx_all = []
    for s in np.unique(strata):
        ids = np.where(strata == s)[0]
        idx_all.append(ids[rng.integers(0, len(ids), size=(BOOT, len(ids)))])
    idx = np.concatenate(idx_all, axis=1)
    r = num[idx].sum(1) / np.maximum(den[idx].sum(1), 1)
    return np.quantile(r, 0.05)


def block_oc(p, m, n_strata=(20, 10), rho=0.10, thr=0.70):
    a, b = beta_params(p, rho)
    strata = np.concatenate([np.full(k, i) for i, k in enumerate(n_strata)])
    n = len(strata)
    ok = 0
    for _ in range(SIMS):
        pr = rng.beta(a, b, size=n)
        x = rng.binomial(m, pr).astype(float)
        den = np.full(n, float(m))
        if lower_bound_ratio(x, den, strata, rng) >= thr:
            ok += 1
    return ok / SIMS


def f1_oc(f, lam, n_strata=(20, 10), rho=0.10, thr=0.70):
    pb = f / (2 - f)                      # share of union units found by both readers
    a, b = beta_params(pb, rho)
    strata = np.concatenate([np.full(k, i) for i, k in enumerate(n_strata)])
    n = len(strata)
    ok = 0
    for _ in range(SIMS):
        u = rng.poisson(lam, size=n)
        pr = rng.beta(a, b, size=n)
        both = rng.binomial(u, pr)
        only = u - both
        onlyA = rng.binomial(only, 0.5)
        onlyB = only - onlyA
        num = 2.0 * both
        den = (2 * both + onlyA + onlyB).astype(float)
        if lower_bound_ratio(num, den, strata, rng) >= thr:
            ok += 1
    return ok / SIMS


print("== block raw agreement, n=30 (20+10), lower 90% bound >= 0.70 ==")
for m, name in ((10, "S categorical ~10"), (11, "D ~11"), (6, "F ~6"), (25, "QA sub-items ~25"), (9, "QA scores 9"), (6, "CT 6")):
    row = []
    for p in (0.65, 0.70, 0.75, 0.80, 0.85, 0.90):
        row.append(f"{p:.2f}:{block_oc(p, m):.2f}")
    print(name, " ".join(row))
print("rho sensitivity, m=10, rho=0.20:", " ".join(f"{p:.2f}:{block_oc(p, 10, rho=0.20):.2f}" for p in (0.70, 0.80, 0.85, 0.90)))
print("old design n=12 (one stratum), m=10:", " ".join(f"{p:.2f}:{block_oc(p, 10, n_strata=(12,)):.2f}" for p in (0.70, 0.80, 0.85, 0.90)))

print("== unit identification F1 ==")
for lam, thr, name in ((6, 0.70, "H lam=6 thr .70"), (5, 0.60, "K lam=5 thr .60"), (3, 0.60, "K lam=3 thr .60")):
    print(name, " ".join(f"{f:.2f}:{f1_oc(f, lam, thr=thr):.2f}" for f in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90)))

print("== binomial rules ==")
# census F1 unit identical, n=30: pass if one-sided 95% Clopper-Pearson lower bound >= 0.70
def cp_lower(x, n, a=0.05):
    return 0.0 if x == 0 else stats.beta.ppf(a, x, n - x + 1)
n = 30
cmin = min(x for x in range(n + 1) if cp_lower(x, n) >= 0.70)
print("F1-unit / S14 rule n=30: pass if x >=", cmin, "of 30;", " ".join(f"{p:.2f}:{1 - stats.binom.cdf(cmin - 1, n, p):.2f}" for p in (0.70, 0.75, 0.80, 0.85, 0.90, 0.95)))
cmin60 = min(x for x in range(n + 1) if cp_lower(x, n) >= 0.60)
print("S14 rule (>=0.60) n=30: pass if x >=", cmin60, " ".join(f"{p:.2f}:{1 - stats.binom.cdf(cmin60 - 1, n, p):.2f}" for p in (0.60, 0.70, 0.75, 0.80, 0.85, 0.90)))
print("per-field flag thresholds (flag if x <= c; P(flag|0.90) <= 0.06)")
for nf in range(15, 31):
    c = max(x for x in range(nf + 1) if stats.binom.cdf(x, nf, 0.90) <= 0.06)
    print(nf, c, f"false {stats.binom.cdf(c, nf, 0.90):.3f}", f"det.65 {stats.binom.cdf(c, nf, 0.65):.2f}", f"det.70 {stats.binom.cdf(c, nf, 0.70):.2f}", f"det.75 {stats.binom.cdf(c, nf, 0.75):.2f}")
# composition: P(no MM) under old SRS 12 vs gate
print("P(no i1 b/ab in SRS of 12 from 608 with 53):", round(stats.hypergeom.pmf(0, 608, 53, 12), 3))
