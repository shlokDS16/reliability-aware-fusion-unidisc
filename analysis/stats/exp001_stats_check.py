"""Statistician checks for the EXP-001 v0.1 card (no model data; formulas and simulations only).

Run:  python analysis/stats/exp001_stats_check.py > analysis/stats/exp001_stats_check.log
Every number printed here is an operating characteristic of a statistical rule under stated
assumptions. None is an experimental result.
"""
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261014)
z = stats.norm.ppf
Phi = stats.norm.cdf


def section(t):
    print("\n== " + t)


# ---------------------------------------------------------------- 10.4 sizing
section("10.4 sample size for H-B (sigma_L, rho_pair = 0, m = 1.0 point)")
m = 1.0
for a_lab, a in [("0.05", 0.05), ("0.05/7", 0.05 / 7)]:
    for sL in (4.0,):
        sd = sL * np.sqrt(2)
        n = ((z(1 - a / 2) + z(0.90)) * sd / m) ** 2
        print(f"alpha {a_lab}: z={z(1 - a / 2):.4f}  sigma_d={sd:.3f}  n={n:.1f} -> {int(np.ceil(n))}")
for sL in (4.0, 5.0, 6.0):
    sd = sL * np.sqrt(2)
    se = sd / np.sqrt(500)
    p1 = Phi(m / se - z(0.975))
    p7 = Phi(m / se - z(1 - 0.05 / 14))
    print(f"n=500 sigma_L={sL}: SE={se:.3f}  power(primary)={p1:.3f}  power(alpha .05/7)={p7:.3f}")

section("Decision-rule operating characteristics, n = 500, sigma_L = 4, rho = 0 (10.2 outcome classes)")
se = 4 * np.sqrt(2) / np.sqrt(500)
for d in (0.0, 0.5, 1.0, 1.25, 1.5):
    # positive: lo > 0 and dhat >= m ; null: |CI| inside (-m, m)
    sims = rng.normal(d, se, 400000)
    lo, hi = sims - 1.96 * se, sims + 1.96 * se
    pos = np.mean((lo > 0) & (sims >= m))
    sig = np.mean(lo > 0)
    nul = np.mean((lo > -m) & (hi < m))
    print(f"true d={d:4.2f}: P(lo>0)={sig:.3f}  P('positive' = lo>0 & dhat>=1)={pos:.3f}  P('null')={nul:.3f}")

section("H-B2: percentile bootstrap of max(TF,IF)-Alt vs intersection-union test (IUT), data-level, n = 500")
# per-seed differences TF-Alt and IF-Alt, SD 5.66 each, correlation 0.5 (shared Alt); H0 boundary max = 1.0
n_s, sd_s, reps, nb = 500, 4 * np.sqrt(2), 600, 1000
cov_s = np.array([[1, 0.5], [0.5, 1]]) * sd_s ** 2
for true in [(1.0, 1.0), (1.0, -1.0), (0.0, 0.0)]:
    r_iut = r_max = 0
    for _ in range(reps):
        dat = rng.multivariate_normal(true, cov_s, n_s)
        mu = dat.mean(0)
        se_hat = dat.std(0, ddof=1) / np.sqrt(n_s)
        r_iut += np.all(mu + z(0.95) * se_hat < 1.0)
        idx = rng.integers(0, n_s, (nb, n_s))
        bmax = dat[idx].mean(1).max(1)
        r_max += np.quantile(bmax, 0.95) < 1.0
    print(f"true (TF-Alt, IF-Alt)={true}: reject H0[max>=1] IUT={r_iut / reps:.3f}  percentile-bootstrap-of-max={r_max / reps:.3f}")

# ---------------------------------------------------------------- H-A
section("H-A1 SE and the probability that the 95% lower limit of the ratio is >= 1.5 (n = 128 and 512)")
cv, r = 0.6, 0.3
for n in (128, 256, 512):
    se_l = np.sqrt((cv ** 2 + cv ** 2 - 2 * r * cv * cv) / n)
    row = []
    for R in (1.5, 1.75, 2.0, 2.5):
        row.append(f"R={R}: {Phi((np.log(R) - np.log(1.5)) / se_l - 1.96):.3f}")
    print(f"n={n}: SE(ln ratio)={se_l:.4f}  " + "  ".join(row))

section("H-A extension rule (11.2): type I error of 'positive' when the true ratio is exactly 1.5")
# one-sided test of ln R > ln 1.5 ; Z1 from first 128, Z2 cumulative 512 ; corr(Z1, Z2) = sqrt(128/512) = 0.5
reps = 2_000_000
t = 128 / 512
z1 = rng.standard_normal(reps)
z2 = np.sqrt(t) * z1 + np.sqrt(1 - t) * rng.standard_normal(reps)
c = 1.96
rej1 = z1 >= c
straddle = (z1 < c) & (z1 > -c)          # interval contains 1.5 -> extend
rej2 = straddle & (z2 >= c)
print(f"naive rule (1.96 at both looks): alpha = {np.mean(rej1 | rej2):.4f}  (nominal 0.025)")
# conjunction over three ratios (H-A1 two directions, H-A2): extension if ANY straddles; worst case independent
# Pocock-type equal boundary and an O'Brien-Fleming-type spending boundary, with binding futility at -1.96
from scipy.optimize import brentq


def alpha_two_look(c1, c2, fut=-1.96):
    rej_1 = z1 >= c1
    cont = (z1 < c1) & (z1 > fut)
    return np.mean(rej_1 | (cont & (z2 >= c2)))


cp = brentq(lambda cc: alpha_two_look(cc, cc) - 0.025, 1.8, 3.0)
print(f"Pocock-type equal boundary with binding futility at z1 <= -1.96: c = {cp:.3f} at both looks")
# Lan-DeMets OBF spending at t = 0.25: alpha1 = 2 - 2 Phi(z_{1-0.025/2} / sqrt(t))
a1 = 2 - 2 * Phi(z(1 - 0.025 / 2) / np.sqrt(t))
c1 = z(1 - a1)
c2 = brentq(lambda cc: alpha_two_look(c1, cc) - 0.025, 1.5, 3.0)
print(f"OBF-type spending: alpha1 = {a1:.2e} (c1 = {c1:.3f}), final c2 = {c2:.3f} (binding futility at -1.96)")
c2nb = brentq(lambda cc: alpha_two_look(c1, cc, fut=-np.inf) - 0.025, 1.5, 3.0)
print(f"OBF-type spending, non-binding futility: final c2 = {c2nb:.3f}")
print(f"fixed n = 256 (no look): 95% lower limit rule unchanged; SE(ln ratio) = {np.sqrt(0.504 / 256):.4f}")

# ---------------------------------------------------------------- H-C
section("H-C: Spearman over 16 cells. Critical value and the pooled-strata artefact")
nperm = 200000
x = np.arange(16)
perm_r = np.array([stats.spearmanr(x, rng.permutation(16))[0] for _ in range(20000)])
print(f"one-sided 5% critical value, 16 exchangeable cells (20,000 perms): {np.quantile(perm_r, 0.95):.3f}")


def pooled_vs_stratified(shift_M, shift_D, n_rep=4000):
    """Two strata (k0, k+), 8 windows each. M and Delta independent within strata; strata differ by a shift."""
    pooled, strat = [], []
    for _ in range(n_rep):
        M = np.r_[rng.normal(0, 1, 8) + shift_M, rng.normal(0, 1, 8)]
        D = np.r_[rng.normal(0, 1, 8) + shift_D, rng.normal(0, 1, 8)]
        pooled.append(stats.spearmanr(M, D)[0])
        strat.append(0.5 * (stats.spearmanr(M[:8], D[:8])[0] + stats.spearmanr(M[8:], D[8:])[0]))
    return np.array(pooled), np.array(strat)


strat_null = []
for _ in range(20000):
    strat_null.append(0.5 * (stats.spearmanr(x[:8], rng.permutation(8))[0] + stats.spearmanr(x[:8], rng.permutation(8))[0]))
crit_s = np.quantile(strat_null, 0.95)
print(f"stratified statistic (mean of two within-k Spearman, permute within k): one-sided 5% critical = {crit_s:.3f}")
crit_p = np.quantile(perm_r, 0.95)
for sM, sD in [(0, 0), (3, 1), (3, 3), (3, -3)]:
    p, s = pooled_vs_stratified(sM, sD)
    print(f"no within-k association; between-k shift M={sM}, Delta={sD}: "
          f"P(pooled rho>=0.5 & > crit)={np.mean((p >= 0.5) & (p > crit_p)):.3f}  "
          f"median pooled rho={np.median(p):.3f} | P(stratified > crit)={np.mean(s > crit_s):.3f}")

# ---------------------------------------------------------------- Lift estimator
section("Lift: variance of the mean Lift vs per-seed SD / sqrt(n) (synthetic embeddings)")
d_emb, n = 64, 200


def lift_mean(I, T, idx):
    I, T = I[idx], T[idx]
    S = I @ T.T                                     # S[a, b] = cos(img a, txt b)
    same = idx[:, None] == idx[None, :]             # exclude partners with the same original seed
    C = np.diag(S)
    off = np.where(same, np.nan, S)
    B = 0.5 * (np.nanmean(off, axis=0) + np.nanmean(off, axis=1))  # per i: mean over j of cos(I_j,T_i) and cos(I_i,T_j)
    return 100 * np.mean(C - B), 100 * (C - B)


def emb(n):
    z0 = rng.standard_normal((n, d_emb))
    I = z0 + 1.2 * rng.standard_normal((n, d_emb)) + 2.0  # shared offset (collapse-like component)
    T = 0.6 * z0 + 1.2 * rng.standard_normal((n, d_emb)) + 2.0
    I /= np.linalg.norm(I, axis=1, keepdims=True)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    return I, T


I, T = emb(n)
full, per = lift_mean(I, T, np.arange(n))
boot = [lift_mean(I, T, rng.integers(0, n, n))[0] for _ in range(2000)]
mc = [lift_mean(*emb(n), np.arange(n))[0] for _ in range(400)]
# influence values of mean(C) - mean_offdiag: psi_i = C_i - 2 B_i (Hajek projection), not Lift_i = C_i - B_i
S_full = I @ T.T
off = S_full.copy(); np.fill_diagonal(off, np.nan)
B_full = 0.5 * (np.nanmean(off, axis=0) + np.nanmean(off, axis=1))
psi = 100 * (np.diag(S_full) - 2 * B_full)
print(f"influence SD/sqrt(n) (psi_i = 100 (C_i - 2 B_i)) = {psi.std(ddof=1) / np.sqrt(n):.4f}")
print(f"n={n}: per-seed SD/sqrt(n) = {per.std(ddof=1) / np.sqrt(n):.4f}; bootstrap SE (with same-seed exclusion) = "
      f"{np.std(boot, ddof=1):.4f}; true sampling SD (400 fresh draws) = {np.std(mc, ddof=1):.4f}")
