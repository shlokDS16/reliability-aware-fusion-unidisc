"""Statistician round-2 checks for EXP-001 v0.2 and EXP-002 v0.2 (no model data; formulas and simulations only).

Run:  python analysis/stats/round2_stats_check.py > analysis/stats/round2_stats_check.log
Every parameter marked [A] is an illustrative assumption, not a measurement. Nothing printed here is an
experimental result.
"""
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261015)
z = stats.norm.ppf
Phi = stats.norm.cdf


def section(t):
    print("\n== " + t)


# =============================================================================================== EXP-001
section("EXP-001 H-A1: P(95% lower limit of the ratio >= 1.5 | true 1.75), delta method, r = 0.3 [A], by cv of the window-pair average")
for n in (256, 384, 512):
    row = []
    for cv in (0.6, 0.8, 1.0, 1.5):
        se = np.sqrt((2 * cv**2 - 2 * 0.3 * cv**2) / n)
        p = Phi(np.log(1.75 / 1.5) / se - 1.96)
        row.append(f"cv={cv}: SE(ln)={se:.4f} P={p:.3f}")
    print(f"n={n}: " + " | ".join(row))
print("Three-part conjunction (two H-A1 ratios and H-A2) at n = 256 if parts independent: "
      + ", ".join(f"cv={cv}: {Phi(np.log(1.75/1.5)/np.sqrt((2*cv**2-0.6*cv**2)/256)-1.96)**3:.3f}" for cv in (0.6, 1.0, 1.5)))


def ratio_boot_sim(n, cv, zero_share, true_ratio, reps=600, B=1000):
    """Percentile bootstrap of the ratio of means (early/late), early and late independent (r = 0),
    gamma per-trajectory values with a share of exact zeros (single committed position with H < floor)."""
    k = 1 / cv**2
    hits = 0
    for _ in range(reps):
        e = rng.gamma(k, true_ratio / k, n) * (rng.random(n) > zero_share)
        l = rng.gamma(k, 1 / k, n) * (rng.random(n) > zero_share)
        idx = rng.integers(0, n, (B, n))
        r = e[idx].mean(1) / l[idx].mean(1)
        hits += np.quantile(r, 0.025) >= 1.5
    return hits / reps


section("EXP-001 H-A1: simulated percentile-bootstrap ratio of means, n = 256 (gamma values, share of zeros, early/late independent)")
for cv, zs in ((0.6, 0.0), (1.0, 0.0), (1.0, 0.3), (1.5, 0.3)):
    a = ratio_boot_sim(256, cv, zs, 1.5)
    p = ratio_boot_sim(256, cv, zs, 1.75)
    print(f"cv={cv}, zero share={zs}: P(lower >= 1.5 | 1.5) = {a:.3f} (nominal 0.025); P(lower >= 1.5 | 1.75) = {p:.3f}")

section("EXP-001 G5 as written: 'median relative difference > 0.3' between g = 4 and g = 32 when there is NO chunk bias")
print("Each I->T estimate carries Monte Carlo error from R = 8 draws; relative SD c per probe-trajectory [A]; 8 trajectories x 2 probes = 16 values")
for c in (0.15, 0.25, 0.35, 0.5):
    reps = 20000
    x4 = np.exp(rng.normal(0, c, (reps, 16)) - c**2 / 2)
    x32 = np.exp(rng.normal(0, c, (reps, 16)) - c**2 / 2)
    rel = (x4 - x32) / x32
    med_abs = np.median(np.abs(rel), 1)
    med_sgn = np.median(rel, 1)
    ratio_means = x4.mean(1) / x32.mean(1) - 1
    print(f"c={c}: P(median |rel diff| > 0.3) = {np.mean(med_abs > 0.3):.3f}; P(|median signed| > 0.3) = {np.mean(np.abs(med_sgn) > 0.3):.3f};"
          f" P(|ratio of means - 1| > 0.3) = {np.mean(np.abs(ratio_means) > 0.3):.3f}")

section("EXP-001 NC-6' as written: P(pass) under its exact null (Lift = 0 in every arm, all contrasts 0), n = 128")
print("Statements: 4 arm Lifts (J, Alt, DA, TF) and contrasts vs J (3) or all pairs (6); pass = every 95% CI contains 0 and every |estimate| < 0.3")


def nc6_sim(sig, rho, n=128, pairs="vsJ", bound_on_arms=False, alpha_ci=0.05, use_bound=True, reps=200000):
    cov = sig**2 * (rho * np.ones((4, 4)) + (1 - rho) * np.eye(4)) / n
    L = rng.multivariate_normal(np.zeros(4), cov, reps)
    se_arm = sig / np.sqrt(n)
    se_con = sig * np.sqrt(2 * (1 - rho)) / np.sqrt(n)
    zc = z(1 - alpha_ci / 2)
    ok = np.all(np.abs(L) < zc * se_arm, 1)
    if bound_on_arms and use_bound:
        ok &= np.all(np.abs(L) < 0.3, 1)
    if pairs == "vsJ":
        C = L[:, 1:] - L[:, :1]
    else:
        C = np.stack([L[:, i] - L[:, j] for i in range(4) for j in range(i + 1, 4)], 1)
    ok &= np.all(np.abs(C) < zc * se_con, 1)
    if use_bound:
        ok &= np.all(np.abs(C) < 0.3, 1)
    return ok.mean(), se_con


for sig in (2.5, 3.0, 4.0):
    for rho in (0.0, 0.3, 0.6):
        p1, se = nc6_sim(sig, rho)
        p2, _ = nc6_sim(sig, rho, pairs="all", bound_on_arms=True)
        p3, _ = nc6_sim(sig, rho, alpha_ci=0.05 / 7, use_bound=False)
        print(f"sigma_L={sig} [A], rho_arm={rho} [A]: contrast SE={se:.3f}; P(pass) as written: {p1:.3f} (3 contrasts) / {p2:.3f} (6 pairs, bound on arms too);"
              f" Bonferroni 7 statements, no point bound: {p3:.3f}")
print("Achieved equivalence bound of one contrast (half-width of its 90% CI + |estimate|), median under the null: "
      + ", ".join(f"SE={s:.2f}: {1.645*s + 0.674*s:.2f}" for s in (0.31, 0.40, 0.50)))

section("EXP-001 PG-1 operating characteristics [A: per-item SD of raw matched CLIP 3.0 points, per-seed SD of Lift_i 4.0, lift 8.0 at 1,024 px]")
sC, sL, lift = 3.0, 4.0, 8.0
for design, n512, n1024, rho in (("as written (32 vs 16, unpaired)", 32, 16, 0.0), ("paired, 32 vs 32, rho 0.5", 32, 32, 0.5)):
    se_raw = np.sqrt(sC**2 / n512 + sC**2 / n1024 - 2 * rho * sC**2 / np.sqrt(n512 * n1024) * (min(n512, n1024) / max(n512, n1024)) ** 0.5)
    for deficit, ratio in ((0.0, 1.0), (1.0, 0.9), (2.0, 0.8), (3.0, 0.6)):
        p_raw = Phi((2.0 - deficit) / se_raw)
        m = lift * ratio - 0.8 * lift
        se_l = np.sqrt(sL**2 / n512 + 0.64 * sL**2 / n1024 - 2 * 0.8 * rho * sL**2 / np.sqrt(n512 * n1024))
        p_lift = Phi(m / se_l)
        print(f"{design}: true raw deficit {deficit}, true lift ratio {ratio}: P(raw ok)={p_raw:.3f}, P(lift ok)={p_lift:.3f}, P(pass) ~ {p_raw*p_lift:.3f}")

section("EXP-001 PG-2: P(at least 12 of 16 captions with >= 4 non-special tokens) by true rate p")
print(", ".join(f"p={p}: {1 - stats.binom.cdf(11, 16, p):.3f}" for p in (0.5, 0.6, 0.7, 0.75, 0.8, 0.9)))

# =============================================================================================== EXP-002
d_cp = 0.03
section("EXP-002 constants (z_{1-0.025/(2M)} + z_0.80)^2 and illustrations")
const = {}
for M in (5, 4, 3, 2, 1):
    const[M] = (z(1 - 0.025 / (2 * M)) + z(0.80)) ** 2
    print(f"M={M}: z={z(1 - 0.025/(2*M)):.4f} constant={const[M]:.3f} SE at sized n = {d_cp/np.sqrt(const[M]):.5f}  n_B(0.25,0.40,0.60) = "
          + ", ".join(str(int(np.ceil(const[M] * s**2 / d_cp**2))) for s in (0.25, 0.40, 0.60)))

section("EXP-002 12.5 arithmetic: n_B affordable = (36 - fixed - S4 - N5b) / (S5 + S6 per n_B)")
rows = {"bf16": (7.75, {"R0": (9.68, 45.42, 2.44, 5), "R1": (4.92, 22.61, 2.00, 4), "R2": (1.94, 9.08, 1.22, 2), "R3": (0.75, 3.38, 0.78, 1)}, 0.45),
        "fp32": (8.80, {"R0": (20.59, 89.16, 2.44, 5), "R1": (10.69, 45.35, 2.00, 4), "R2": (4.12, 17.83, 1.22, 2), "R3": (1.64, 6.88, 0.78, 1)}, 0.68)}
for br, (fixed, rr, n5) in rows.items():
    for R, (s4, s5, s6, M) in rr.items():
        nB = int(np.floor((36 - fixed - s4 - n5) / ((s5 + s6) / 1000)))
        smax = np.sqrt(nB * d_cp**2 / const[M]) if nB > 0 else float("nan")
        print(f"{br} {R}: n_B affordable = {nB}, sigma_up max = {smax:.3f}, sigma_c max = {smax/1.1305:.3f}")

section("EXP-002 P(H1 negative | G_cp = 0 at every k in K_R), 95% (card rule) and 97.5% intervals, bivariate/multivariate normal, corr between k")


def p_neg(se, nk, rho, level, reps=400000):
    cov = se**2 * (rho * np.ones((nk, nk)) + (1 - rho) * np.eye(nk))
    G = rng.multivariate_normal(np.zeros(nk), cov, reps)
    zc = z(1 - (1 - level) / 2)
    return np.mean(np.all(np.abs(G) + zc * se < d_cp, 1))


for rung, nk, M in (("R0", 4, 5), ("R1", 3, 4), ("R2", 2, 2)):
    se = d_cp / np.sqrt(const[M])
    for shrink, lab in ((1.0, "sigma = sigma_up"), (1 / 1.1305, "sigma = sigma_up / 1.13")):
        out = []
        for rho in (0.0, 0.3, 0.6):
            out.append(f"rho_k={rho}: 95% {p_neg(se*shrink, nk, rho, 0.95):.3f}, 97.5% {p_neg(se*shrink, nk, rho, 0.975):.3f}")
        print(f"{rung} ({nk} k, M={M}, SE={se*shrink:.4f}, {lab}): " + " | ".join(out))
se1 = d_cp / np.sqrt(const[1])
print(f"R3 (k = 16 only, SE={se1:.4f}): P('practically 0 at k = 16' | 0) = 95%: {2*Phi(d_cp/se1 - 1.96)-1:.3f}, 97.5%: {2*Phi(d_cp/se1 - z(0.9875))-1:.3f}")
print(f"Card 9.5 states 0.80 at two k (95%) and 0.67 (97.5%); those are 0.895^2 and 0.819^2 from the M = 4 SE 0.0084, not R2's SE {d_cp/np.sqrt(const[2]):.4f}")

section("EXP-002 N2: TOST 90% CI inside +-m with m = 3.29 sigma_up sqrt(2/n_1); P(pass | exact null) by sigma_true / sigma_up")
for ratio in (0.7, 0.85, 1.0, 1.2, 1.5):
    print(f"sigma_true/sigma_up={ratio}: P(pass)={2*Phi(3.29/ratio - 1.645)-1:.3f}  (with m = 3.886 SE_up: {2*Phi(3.886/ratio - 1.645)-1:.3f})")
for n1, br in ((300, "bf16"), (150, "fp32")):
    f = np.sqrt(2 / n1)
    print(f"{br} n_1={n1}: demotion m_H > 0.06 <=> sigma_up,H > {0.06/(3.29*f):.3f} <=> raw pilot SD_H > {0.06/(3.29*f)/(1.1305*1.2):.3f};"
          f" m_Y > 0.10 <=> sigma_up,Y > {0.10/(3.29*f):.3f} <=> raw pilot SD_Y > {0.10/(3.29*f)/(1.1305*1.2):.3f}")
    for sy in (0.25, 0.30, 0.40):
        print(f"   sigma_up,Y={sy}: m_Y = {3.29*sy*f:.3f} (P(pass | true |Y(A1)-Y(A3)| = 0.03) = "
              f"{Phi((3.29*sy*f - 0.03)/(sy*f) - 1.645) - Phi((-3.29*sy*f - 0.03)/(sy*f) + 1.645):.3f})")
print("Primary power after N2-Y (independent k = 1 samples): P(supported and N2-Y passes | G_cp = 0.03 at one k) = 0.80 x 0.90 = 0.72 (0.80 x 0.975 = 0.78 with m = 3.886 SE)")

section("EXP-002 IR8 (iv) curvature flag: WLS quadratic on stage-A cells (|E-h*| <= 0.3, n_A = 64) plus two stage-B cells (+-0.05, n_B)")


def kappa_se(offsets_A, nA, nB, sig):
    x = np.concatenate([offsets_A, [-0.05, 0.05]])
    w = np.concatenate([np.full(len(offsets_A), nA), [nB, nB]]) / sig**2
    X = np.stack([np.ones_like(x), x, x**2], 1)
    cov = np.linalg.inv(X.T @ (w[:, None] * X))
    return np.sqrt(cov[2, 2])


for step in (0.10, 0.15, 0.20):
    shift = 0.3 * step
    a1 = np.array([j * step + shift for j in range(-4, 5)])
    a1 = a1[np.abs(a1) <= 0.3]
    a3 = np.array([j * step + shift for j in range(-2, 3)])
    a3 = a3[np.abs(a3) <= 0.3]
    for sig in (0.3, 0.5):
        s1 = kappa_se(a1, 64, 2500, sig)
        s3 = kappa_se(a3, 64, 2500, sig)
        sd_b = np.sqrt(s1**2 + s3**2) * 0.05 * 0.05
        p0 = 2 * Phi(-0.01 / sd_b)
        p6 = Phi((0.015 - 0.01) / sd_b) + Phi((-0.015 - 0.01) / sd_b)
        print(f"E per grid step {step} [A], sigma_y={sig} [A]: cells used A1 {len(a1)}, A3 {len(a3)}; SE(kappa) A1 {s1:.2f}, A3 {s3:.2f};"
              f" SD(b_theta)={sd_b:.4f}; P(flag | equal curvature)={p0:.3f}; P(flag | curvature diff 6)={p6:.3f}")

section("EXP-002 N5(b): flag if 95% CI of the paired Y difference excludes 0 and |diff| >= 0.01, n = 512, by paired SD [A]")
for sd in (0.05, 0.1, 0.2, 0.42):
    se = sd / np.sqrt(512)
    thr = max(1.96 * se, 0.01)
    for true in (0.0, 0.01, 0.03):
        p = Phi((true - thr) / se) + Phi((-true - thr) / se)
        print(f"paired SD={sd}: SE={se:.4f}; true diff {true}: P(flag)={p:.3f}")

section("EXP-002 H4 (i): TOST 90% inside +-0.05 on H(A1)-H(A3) pooled over 5 taus, n_A = 64 per tau, P(pass | true 0)")
for sH in (0.10, 0.15, 0.20):
    for rt in (0.0, 0.5, 0.8):
        var = 2 * sH**2 / 64 * (1 + 4 * rt) / 5
        se = np.sqrt(var)
        print(f"sigma_H={sH} [A], corr across taus within s={rt} [A]: SE={se:.4f}, P(pass | 0)={2*Phi(0.05/se - 1.645)-1:.3f};"
              f" single cell SE={np.sqrt(2*sH**2/64):.4f}, P={max(0.0, 2*Phi(0.05/np.sqrt(2*sH**2/64) - 1.645)-1):.3f}")
