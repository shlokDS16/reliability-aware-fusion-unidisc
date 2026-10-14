"""Statistician checks for the EXP-002 v0.1 card (no model data; formulas and simulations only).

Run:  python analysis/stats/exp002_stats_check.py > analysis/stats/exp002_stats_check.log
All parameter values marked [A] are illustrative assumptions, not measurements. Nothing printed here is
an experimental result.
"""
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261014)
z = stats.norm.ppf
Phi = stats.norm.cdf
d_cp = 0.03


def section(t):
    print("\n== " + t)


# ---------------------------------------------------------------- 9.6 constants
section("9.6 constant (z_{1-0.025/(2m)} + z_0.80)^2 and n_B")
const = {}
for mR in (4, 3, 2, 1):
    za = z(1 - 0.025 / (2 * mR))
    const[mR] = (za + z(0.80)) ** 2
    print(f"m={mR}: z={za:.4f}  z_0.80={z(0.80):.4f}  constant={const[mR]:.3f}")
print("card uses 12.75 (m=4, z rounded to 2.73) and 12.1 (m=3)")
for s in (0.25, 0.40, 0.60):
    print(f"sigma_up={s}: n_B(m=4) exact={int(np.ceil(const[4] * s**2 / d_cp**2))}  with 12.75={int(np.ceil(12.75 * s**2 / d_cp**2))}"
          f"  | m=3: {int(np.ceil(const[3] * s**2 / d_cp**2))}  m=2: {int(np.ceil(const[2] * s**2 / d_cp**2))}  m=1: {int(np.ceil(const[1] * s**2 / d_cp**2))}")
npil = 32
f = np.sqrt((npil - 1) / stats.chi2.ppf(0.20, npil - 1))
print(f"pilot n_p=32: chi2_0.20,31 = {stats.chi2.ppf(0.20, 31):.3f}; sigma_up / sigma_c = {f:.4f}")

section("MDE at n_B = 1000 (power 0.80, Bonferroni-worst-case Holm level) by sigma_c")
for s in (0.25, 0.40, 0.60):
    print(f"sigma_c={s}: " + "  ".join(f"m={mR}: {np.sqrt(const[mR]) * s / np.sqrt(1000):.4f}" for mR in (4, 3, 2, 1)))

section("Analytic sigma_c of the IR1 estimator (delta method) under [A] component values")
# psi_s for one arm = (1-w)(y_lo - beta h_lo) + w (y_hi - beta h_hi) (centred); G_cp = Y(A3) - Y(A1)
print("sigma_psi^2 = sigma_y^2 + beta^2 sigma_h^2 - 2 beta rho_yh sigma_y sigma_h ; w = 0.5 ;"
      " rho_tau = corr of psi between tau_lo and tau_hi cells of one arm (same s, CRN) ; rho_arm = corr between A1 and A3")
print(" sigma_y beta sigma_h rho_yh rho_tau rho_arm | sigma_psi  sigma_c  n_B(m=4, sigma_up=1.13 sigma_c)")
for sy, b, sh, ryh, rt, ra in [(0.30, 3, 0.10, 0.5, 0.3, 0.1), (0.35, 3, 0.12, 0.5, 0.3, 0.1),
                               (0.35, 5, 0.12, 0.3, 0.3, 0.1), (0.50, 3, 0.15, 0.3, 0.5, 0.0),
                               (0.35, 3, 0.12, 0.5, 0.3, 0.5)]:
    sp2 = sy**2 + b**2 * sh**2 - 2 * b * ryh * sy * sh
    v_arm = (0.25 + 0.25 + 2 * 0.25 * rt) * sp2
    sc = np.sqrt(2 * v_arm * (1 - ra))
    nB = int(np.ceil(const[4] * (f * sc) ** 2 / d_cp**2))
    print(f"  {sy:5.2f} {b:4.1f} {sh:6.2f} {ryh:6.2f} {rt:6.2f} {ra:6.2f}  | {np.sqrt(sp2):8.3f} {sc:8.3f}  {nB}")

# ---------------------------------------------------------------- decision rules
section("9.5 outcome classes: operating characteristics at the sized n (SE = d_cp / (z_m + z_0.80), m = 4)")
zm = z(1 - 0.025 / 8)
se = d_cp / (zm + z(0.80))
print(f"SE at sized n = {se:.4f}")
for G in (0.0, 0.015, 0.03, 0.04, 0.05):
    sims = rng.normal(G, se, 500000)
    sig = np.abs(sims / se) > zm
    clear = sig & (np.abs(sims) >= d_cp)
    p0_975 = np.mean((sims - z(1 - 0.0125) * se > -d_cp) & (sims + z(1 - 0.0125) * se < d_cp))
    p0_95 = np.mean((sims - z(0.975) * se > -d_cp) & (sims + z(0.975) * se < d_cp))
    print(f"true G={G:5.3f}: P(sig at Bonf level)={np.mean(sig):.3f}  P('clearly +/-')={np.mean(clear):.3f}  "
          f"P('practically 0', 97.5% CI)={p0_975:.3f}  (95% CI: {p0_95:.3f})")
print("H1 negative needs 'practically 0' at every estimable k; with 4 independent k and G = 0 at all k:")
for lab, zz in (("97.5%", z(1 - 0.0125)), ("95%", z(0.975))):
    p1 = 2 * Phi((d_cp - zz * se) / se) - 1
    print(f"  {lab}: per-k {p1:.3f}; all four (independent) {p1**4:.3f}; all two (R2) {p1**2:.3f}")

section("F2 (Delta2 = 2 Y3 - Y1 - Y2, delta 0.05) power relative to F1 at the n sized for F1, arms uncorrelated")
ratio = (0.05 / np.sqrt(6)) / (d_cp / np.sqrt(2))
print(f"effect/SE scale factor = {ratio:.3f}; power F2 at delta = {Phi(ratio * (zm + z(0.80)) - zm):.3f} (F1: 0.800)")

# ---------------------------------------------------------------- H1b gatekeeping
section("H1b: Holm on F1 then H1b at full 0.025 if >= 1 rejection. FWER over {F1, H1b} when H1b's null is true")
reps = 400000
x = np.log2([2, 4, 8, 16])
xc = x - x.mean()
for true in [(0, 0, 0, 0), (6, 0, 0, 6), (6, 6, 6, 6), (6, 0, 0, 0)]:
    t = np.array(true, float) * se
    G = rng.normal(t, se, (reps, 4))
    p = 2 * (1 - Phi(np.abs(G) / se))
    order = np.argsort(p, axis=1)
    ps = np.take_along_axis(p, order, 1)
    thr = 0.025 / np.array([4, 3, 2, 1])
    ok = np.cumprod(ps <= thr, axis=1).astype(bool)
    rej = np.zeros_like(ok)
    np.put_along_axis(rej, order, ok, 1)
    false_f1 = np.any(rej & (t == 0), axis=1)
    slope = (G @ xc) / (xc @ xc)
    se_s = se / np.sqrt(xc @ xc)
    true_slope = (t @ xc) / (xc @ xc)
    gate = rej.any(axis=1)
    h1b = gate & (np.abs(slope / se_s) > z(1 - 0.0125)) & (np.sign(slope) == np.sign(G[:, 3]))
    false_h1b = h1b & (abs(true_slope) < 1e-12)
    print(f"true G/SE={true}: true slope={true_slope / se:.2f} SE-units  FWER(F1)={np.mean(false_f1):.4f}  "
          f"FWER(F1 or H1b)={np.mean(false_f1 | false_h1b):.4f}")
# Holm with H1b as a fifth member (m = 5)
t = np.array((6, 0, 0, 6), float) * se
G = rng.normal(t, se, (reps, 4))
slope = (G @ xc) / (xc @ xc)
pp = np.c_[2 * (1 - Phi(np.abs(G) / se)), 2 * (1 - Phi(np.abs(slope) / (se / np.sqrt(xc @ xc))))]
tt = np.r_[t, 0.0]
order = np.argsort(pp, axis=1)
ps = np.take_along_axis(pp, order, 1)
ok = np.cumprod(ps <= 0.025 / np.array([5, 4, 3, 2, 1]), axis=1).astype(bool)
rej = np.zeros_like(ok)
np.put_along_axis(rej, order, ok, 1)
print(f"Holm with H1b as 5th member, true (6,0,0,6): FWER = {np.mean(np.any(rej & (tt == 0), axis=1)):.4f}")

# ---------------------------------------------------------------- N2
section("N2 gate (k = 1, A1 vs A3 identical in law): P(pass) of 'TOST 90% CI inside +-0.05', rho_arm = 0")
print("sigma_y   n_1=256   n_1=512   n_1=1024  n_1 for P(pass)=0.90")
for sy in (0.25, 0.30, 0.40, 0.50):
    row = []
    for n1 in (256, 512, 1024):
        sed = np.sqrt(2) * sy / np.sqrt(n1)
        row.append(max(0.0, 2 * Phi((0.05 - z(0.95) * sed) / sed) - 1))
    nreq = int(np.ceil(2 * sy**2 * (z(0.95) + z(0.95)) ** 2 / 0.05**2))
    print(f"{sy:7.2f}   " + "   ".join(f"{r:7.3f}" for r in row) + f"   {nreq}")

# ---------------------------------------------------------------- IR estimator simulation
section("IR1-IR5 estimator + paired percentile bootstrap: type I error and SE check (synthetic, [A] parameters)")
hstar = 5.40


def frontier(E, c, b, kappa):
    return c + b * (E - hstar) + kappa * (E - hstar) ** 2


def simulate(n, arms, rho_arm, sy, sh, ryh, rho_tau, calib_sd, B=1000, reps=600, use_ir4=False):
    """arms: dict name -> (c, beta, kappa). Returns rejection rate for G = Y(A3) - Y(A1), mean boot SE, sd of estimates."""
    rej, ses, ests = 0, [], []
    names = list(arms)
    for _ in range(reps):
        # shared latent per sample (CRN): common component across arms and cells
        common = rng.standard_normal((n, 2))
        cells = {}
        for a in names:
            c, b, kap = arms[a]
            lat_arm = np.sqrt(rho_arm) * common + np.sqrt(1 - rho_arm) * rng.standard_normal((n, 2))
            for side, off in (("lo", -0.05), ("hi", +0.05)):
                Ecell = hstar + off + rng.normal(0, calib_sd)
                lat = np.sqrt(rho_tau) * lat_arm + np.sqrt(1 - rho_tau) * rng.standard_normal((n, 2))
                e1, e2 = lat[:, 0], lat[:, 1]
                h = Ecell + sh * e1
                y = frontier(Ecell, c, b, kap) + sy * (ryh * e1 + np.sqrt(1 - ryh**2) * e2)
                cells[(a, side)] = (y, h)
        keys = list(cells)
        data = np.column_stack([cells[k][j] for k in keys for j in (0, 1)])  # n x (2*cells)
        W = rng.multinomial(n, np.full(n, 1 / n), size=B) / n            # B x n bootstrap weights
        M = np.vstack([data.mean(0), W @ data])                          # row 0 = point estimate

        def Yh(a, Mrow):
            ylo, hlo = Mrow[2 * keys.index((a, "lo"))], Mrow[2 * keys.index((a, "lo")) + 1]
            yhi, hhi = Mrow[2 * keys.index((a, "hi"))], Mrow[2 * keys.index((a, "hi")) + 1]
            gap = hhi - hlo
            out = np.where(np.abs(gap) < 0.02, np.nan, ylo + (hstar - hlo) / np.where(gap == 0, 1, gap) * (yhi - ylo))
            return out
        Ycols = {a: Yh(a, M.T) for a in names}
        G = Ycols["A3"] - Ycols["A1"]
        g0, gb = G[0], G[1:]
        gb = gb[~np.isnan(gb)]
        p = min(1.0, 2 * min((1 + np.sum(gb <= 0)) / (len(gb) + 1), (1 + np.sum(gb >= 0)) / (len(gb) + 1)))
        rej += p < 0.05
        ses.append(np.std(gb, ddof=1))
        ests.append(g0)
    return rej / reps, np.mean(ses), np.std(ests, ddof=1)


base = dict(sy=0.35, sh=0.12, ryh=0.5, rho_tau=0.3, calib_sd=0.015)
for lab, arms in [("same frontier for A1 and A3 (G = 0)", {"A1": (4.5, 3.0, 2.0), "A3": (4.5, 3.0, 2.0)}),
                  ("different slopes and curvature, same value at h* (G = 0)", {"A1": (4.5, 2.0, 0.0), "A3": (4.5, 5.0, 6.0)})]:
    r, se_b, sd_e = simulate(1000, arms, rho_arm=0.1, **base)
    print(f"{lab}: n=1000, 600 reps, B=1000: rejection at 0.05 = {r:.3f} (MC SE 0.009); mean bootstrap SE = {se_b:.4f};"
          f" SD of estimate over reps = {sd_e:.4f}; implied sigma_c = {sd_e * np.sqrt(1000):.3f}")

section("IR4 with beta_A treated as a fixed constant: missing variance")
for n_A, gapE in ((64, 0.15), (64, 0.30)):
    se_beta = np.sqrt(2) * 0.35 / np.sqrt(n_A) / gapE
    for dist in (0.03, 0.05, 0.10):
        print(f"n_A={n_A}, stage-A E gap {gapE}: SE(beta_A) ~ {se_beta:.3f}; at |h* - E_cell| = {dist}: omitted SD = {dist * se_beta:.4f}"
              f" (per-arm SE at n_B=1000 is about {0.35 / np.sqrt(1000) * 0.9:.4f})")

# ---------------------------------------------------------------- placebo N4
section("N4 placebo: P(rejection rate over 200 random splits lies in [0.02, 0.09]) under a valid test")
n_B, nsplit, reps = 1000, 200, 3000
inside = []
rates = []
for _ in range(reps):
    yv = rng.standard_normal(n_B)
    idx = np.argsort(rng.random((nsplit, n_B)), axis=1)
    a, b = yv[idx[:, : n_B // 2]], yv[idx[:, n_B // 2:]]
    zz = (a.mean(1) - b.mean(1)) / np.sqrt(a.var(1, ddof=1) / (n_B // 2) + b.var(1, ddof=1) / (n_B // 2))
    rate = np.mean(np.abs(zz) > 1.96)
    rates.append(rate)
    inside.append(0.02 <= rate <= 0.09)
print(f"single (arm, k) cell pair: P(pass) = {np.mean(inside):.3f}; SD of rate = {np.std(rates):.4f} (binomial iid: {np.sqrt(0.05 * 0.95 / 200):.4f})")
print(f"if the gate is applied to 12 (arm, k) pairs and all must pass (independent): P(all pass) = {np.mean(inside) ** 12:.3f}")
pooled = np.array(rates).reshape(-1, 12).mean(1)
print(f"if the gate uses the mean rate over 12 pairs: P(pass) = {np.mean((pooled >= 0.02) & (pooled <= 0.09)):.3f}")

section("IR1 decomposition of the 0.188 rejection rate: slope difference vs curvature difference vs cell placement")
for lab, arms, csd in [("slopes differ (2 vs 5), no curvature, calib_sd 0.015", {"A1": (4.5, 2.0, 0.0), "A3": (4.5, 5.0, 0.0)}, 0.015),
                       ("curvature differs (0 vs 6), calib_sd 0", {"A1": (4.5, 2.0, 0.0), "A3": (4.5, 5.0, 6.0)}, 0.0),
                       ("curvature differs (0 vs 2), calib_sd 0.015", {"A1": (4.5, 2.0, 0.0), "A3": (4.5, 5.0, 2.0)}, 0.015)]:
    pars = dict(base); pars["calib_sd"] = csd
    r, se_b, sd_e = simulate(1000, arms, rho_arm=0.1, reps=400, **pars)
    print(f"{lab}: rejection = {r:.3f}; bootstrap SE = {se_b:.4f}; SD over reps = {sd_e:.4f};"
          f" analytic curvature bias at symmetric cells = {(arms['A3'][2] - arms['A1'][2]) * 0.05**2:.4f}")

section("N2 entropy part: P(pass) of 'TOST 90% CI of H(A1)-H(A3) inside +-0.03', rho_arm = 0, n_1 = 256")
for sh_ in (0.10, 0.15, 0.20):
    sed = np.sqrt(2) * sh_ / np.sqrt(256)
    print(f"sigma_H={sh_:.2f}: P(pass)={max(0.0, 2 * Phi((0.03 - z(0.95) * sed) / sed) - 1):.3f}"
          f"  n_1 for 0.90: {int(np.ceil(2 * sh_**2 * (2 * z(0.95)) ** 2 / 0.03**2))}")

section("Stage-B GPU-hours per unit n_B by ladder rung (card constants [A]: t_f 7 ms, w1+w2+w3 = 5.92, w4 = 1.3)")
TF = 7e-3 / 3600
for lab, Ks in (("R0", (2, 4, 8, 16)), ("R1", (4, 8, 16)), ("R2", (8, 16)), ("R3", (16,))):
    P = sum(1024 / k for k in Ks)
    P4 = sum(1024 / k for k in Ks if k in (4, 16))
    per_n = TF * (2 * 5.92 * P + 2 * 1.3 * P4)
    print(f"{lab}: sum P(k) = {P:.0f}; GPU-h per n_B = {per_n:.5f}; n_B affordable at 45 GPU-h = {int(45 / per_n)}")
