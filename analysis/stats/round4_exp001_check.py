"""Statistician round-4 checks for EXP-001 v0.4 (no model data; card arithmetic and simulations only).

Run (CPU, single thread because of the system-commit limit):
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python analysis/stats/round4_exp001_check.py > analysis/stats/round4_exp001_check.log
Every parameter marked [A] is an illustrative assumption, not a measurement. Nothing printed here is an
experimental result. Card references are to research/preregistration/EXP-001-crossmodal-unidisc.md v0.4.
"""
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261017)
z = stats.norm.ppf


def section(t):
    print("\n== " + t)


# ============================================================================ 1. budget arithmetic (10.4, 12.1, change log D)
section("1a. Non-D3 passes X and core totals from the card's per-trajectory formulas")
st1 = (96 + 16) * 32
pilot_probe = 27392 + 640 + 640 + 256
st2 = 64 * 96 + pilot_probe
pcb = 96 * (3 * (21 + 3 * 2.2) + 24 * 2.2 + 24)
d1 = 128 * (32 + 8 * 8 + 4 * 8) + 64 * 4 * 32 + 64 * (16 + 8 * 16)
d2 = 256 * (32 + 4 * 40) + 128 * 40 + 32 * 5 * 8


def rtr(nR):
    return nR * (32 + 4 * 40) + (nR // 2) * 40


nc6 = 128 * (64 + 32 + 48 + 52)
d3_fixed = 250 * (24 + 24)
for k, v in (("stage 1 gates", st1), ("pilot probe+gate", pilot_probe), ("stage 2", st2), ("PC-B", pcb), ("D1", d1),
             ("D2", d2), ("4r (64)", rtr(64)), ("4r (128)", rtr(128)), ("NC-6'", nc6), ("D3 fixed (Jd, Ref-T2I)", d3_fixed)):
    print(f"  {k}: {v:,.1f}")
X64 = st1 + st2 + pcb + d1 + d2 + rtr(64) + nc6 + d3_fixed
X128 = X64 - rtr(64) + rtr(128)
print(f"X (trace 64) = {X64:,.1f} (card 193,978); X (trace 128) = {X128:,.1f} (card 207,546)")


def ev(n):
    return 1.5 + 0.00116 * (n - 500)


def wall(n, X, tb, duty=0.5):
    return ((X + 192 * n) * tb / 3600 + 1.0 + ev(n)) / duty


def comp(n, X, tb):
    return (X + 192 * n) * tb / 3600 + 1.0 + ev(n)


fac = np.sqrt(63 / stats.chi2.ppf(0.20, 63))
sig_up = 5.657 * fac
nreq = int(np.ceil(1.5 * ((1.96 + 1.2816) * sig_up) ** 2))
nreq566 = int(np.ceil(1.5 * ((1.96 + 1.2816) * 5.66 * fac) ** 2))
print(f"n_req with sigma_d rounded to 5.66 (as the card and round 3): {nreq566}")
print(f"n_req at planning sigma_d 5.657: sigma_d,up {sig_up:.3f}, n_req = {nreq} (card 596); "
      f"MDE at 596 = {(1.96+1.2816)*sig_up/np.sqrt(596):.3f} (card 0.82)")
print("n     trace passes   compute@0.129 wall@0.129 wall@0.09")
for n, X, lab in ((500, X64, 64), (500, X128, 128), (596, X64, 64), (596, X128, 128)):
    print(f"{n}   {lab:>4}  {X+192*n:,.0f}  {comp(n,X,0.129):.2f}         {wall(n,X,0.129):.2f}      {wall(n,X,0.09):.2f}")

section("1b. n_cap and n_conf = min(max(500, n_req), max(500, n_cap)); cap 32 h; X sized with the 128-trajectory trace")


def ncap(X, tb, cap=32.0):
    ok = [n for n in range(500, 1001) if wall(n, X, tb) <= cap]
    return max(ok) if ok else None


def nconf(nreq, X, tb):
    nc = ncap(X, tb)
    return min(max(500, nreq), max(500, nc if nc else 500)), nc


G5, PR = 54272, 4096
for lab, X in (("plan", X128), ("+P_rand", X128 + PR), ("+G5 fallback", X128 + G5), ("+G5 +P_rand", X128 + G5 + PR)):
    for tb in (0.09, 0.129, 0.15, 0.17):
        nf, nc = nconf(nreq, X, tb)
        print(f"  {lab:13s} t_b={tb}: n_cap={nc if nc else 'none (read as 500)'}, n_conf={nf}, wall(n_conf)={wall(nf,X,tb):.2f} h")
print(f"  card: n_cap 826 (plan, 0.129), 1,000 (0.09), 566 (G5 + P_rand, 0.129), 593 (0.15), none at 0.17 with wall(500) 33.7")
# exhaustive check that the rule always returns a defined n >= 500 and that, when n_cap exists, wall(n_conf) <= 32
bad = 0
for tb in np.arange(0.05, 0.40, 0.001):
    for X in (X64, X128, X128 + PR, X128 + G5, X128 + G5 + PR):
        for nr in (300, 500, 596, 800, 1200):
            nf, nc = nconf(nr, X, tb)
            if nf is None or nf < 500 or (nc is not None and wall(nf, X, tb) > 32 + 1e-9):
                bad += 1
print(f"  grid t_b 0.05-0.40 s x 5 X x 5 n_req: violations of 'defined, >= 500, under 32 h whenever n_cap exists' = {bad}")
tb_none = min(tb for tb in np.arange(0.12, 0.30, 0.0001) if ncap(X128, tb) is None)
print(f"  plan X (trace 128): n_cap ceases to exist at t_b = {tb_none:.4f} s; with G5 + P_rand at "
      f"{min(tb for tb in np.arange(0.10, 0.30, 0.0001) if ncap(X128+G5+PR, tb) is None):.4f} s")

# ============================================================================ 2. source-limited guard (2, 11.2)
section("2. Source entropy drift h = mean H_src(early)/mean H_src(late) under the v0.4 guard [A: I scales with H_src]")


def corr_lognormal(n, cv, r):
    s2 = np.log(1 + cv**2)
    L = np.linalg.cholesky(np.array([[s2, r * s2], [r * s2, s2]]))
    x = rng.standard_normal((n, 2)) @ L.T - s2 / 2
    return np.exp(x[:, 0]), np.exp(x[:, 1])


def guard_sim(Rnorm, h, n=256, cv=0.8, r=0.3, cvH=0.5, reps=600, B=1000):
    """per trajectory: H_e = h*G_e, H_l = G_l (lognormal, cv cvH); S_e = Rnorm*H_e*X_e, S_l = H_l*X_l.
    raw = sum S_e / sum S_l; R_Q2 ~ (sum S_e/sum H_e)/(sum S_l/sum H_l) (source side binding in the min)."""
    out = dict(wf_raw=0, label=0, neg_v04=0, wf_q2=0, neg_prop=0, pos_raw=0)
    for _ in range(reps):
        Xe, Xl = corr_lognormal(n, cv, r)
        Ge, Gl = corr_lognormal(n, cvH, 0.3)
        He, Hl = h * Ge, Gl
        Se, Sl = Rnorm * He * Xe, Hl * Xl
        idx = rng.integers(0, n, (B, n))
        raw = Se[idx].sum(1) / Sl[idx].sum(1)
        q2 = (Se[idx].sum(1) / He[idx].sum(1)) / (Sl[idx].sum(1) / Hl[idx].sum(1))
        lo_raw, up_raw = np.quantile(raw, [0.025, 0.975])
        up_q2 = np.quantile(q2, 0.975)
        label = He.mean() < 0.5 * Hl.mean()
        wf = up_raw < 1.5
        out["wf_raw"] += wf
        out["label"] += label
        out["neg_v04"] += wf and not label
        out["wf_q2"] += up_q2 < 1.5
        out["neg_prop"] += wf and (up_q2 < 1.5)
        out["pos_raw"] += lo_raw >= 1.5
    return {k: v / reps for k, v in out.items()}


print("true normalised ratio 1.75 (front-loaded relative to the source entropy); cv 0.8, r 0.3, n = 256 [A]")
print("h     P(raw WF)  P(label h<0.5)  P(counted Negative, v0.4)  P(counted, R_Q2 rule)")
for h in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
    o = guard_sim(1.75, h)
    print(f"{h:.1f}   {o['wf_raw']:.3f}      {o['label']:.3f}           {o['neg_v04']:.3f}                      {o['neg_prop']:.3f}")
print("true normalised ratio 1.0 (flat): the R_Q2 rule must still let a true negative count")
for h in (0.6, 1.0):
    o = guard_sim(1.0, h)
    print(f"h={h}: P(raw WF) {o['wf_raw']:.3f}; P(counted, v0.4) {o['neg_v04']:.3f}; P(counted, R_Q2 rule) {o['neg_prop']:.3f}")
print("opposite drift (h > 1) inflates the raw ratio; true normalised ratio 1.0:")
for h in (1.5, 1.75, 2.0):
    o = guard_sim(1.0, h)
    print(f"h={h}: P(raw lower 95% >= 1.5) = {o['pos_raw']:.3f}")

# ============================================================================ 3. source availability selection
section("3. Source availability at late probes: pooled-over-available ratio vs balanced panel [A: hardness model]")


def avail_sim(R=1.75, beta=0.5, p_late=0.5, n=256, reps=400, B=1000, sign=+1):
    """u_i ~ N(0,1) trajectory hardness; dependence at every probe scales with exp(sign*beta*u_i);
    a late source exists iff u_i > z_{1-p_late} (late candidates left masked are the hard ones)."""
    c = z(1 - p_late)
    hit_main = hit_bal = 0
    est_main, est_bal = [], []
    for _ in range(reps):
        u = rng.standard_normal(n)
        sc = np.exp(sign * beta * u)
        Xe, Xl = corr_lognormal(n, 0.8, 0.3)
        e, l = R * sc * Xe, sc * Xl
        av = u > c
        idx = rng.integers(0, n, (B, n))
        e_b, l_b, a_b = e[idx], l[idx], av[idx]
        main = (e_b.sum(1) / n) / np.maximum((l_b * a_b).sum(1) / np.maximum(a_b.sum(1), 1), 1e-300)  # mean over all early / mean over available late
        bal = (e_b * a_b).sum(1) / np.maximum((l_b * a_b).sum(1), 1e-300)
        est_main.append(e.mean() / l[av].mean())
        est_bal.append(e[av].sum() / l[av].sum())
        hit_main += np.quantile(main, 0.025) >= 1.5
        hit_bal += np.quantile(bal, 0.025) >= 1.5
    return np.median(est_main), np.median(est_bal), hit_main / reps, hit_bal / reps


print("true within-trajectory ratio 1.75 at every hardness level")
for p_late in (1.0, 0.8, 0.5, 0.3):
    for beta, sign in ((0.5, +1), (0.5, -1)):
        if p_late == 1.0 and sign == -1:
            continue
        m, b, hm, hb = avail_sim(p_late=min(p_late, 0.9999), beta=beta, sign=sign)
        lab = "late sources are high-dependence" if sign > 0 else "late sources are low-dependence"
        print(f"  late availability {p_late:.1f}, {lab}: median main ratio {m:.2f}, balanced {b:.2f}; "
              f"P(lower >= 1.5) main {hm:.2f}, balanced {hb:.2f}")
print("true within-trajectory ratio 1.0 (flat), late sources low-dependence, availability 0.5:")
m, b, hm, hb = avail_sim(R=1.0, p_late=0.5, beta=0.5, sign=-1)
print(f"  median main ratio {m:.2f}, balanced {b:.2f}; P(lower >= 1.5) main {hm:.3f}, balanced {hb:.3f}")

# ============================================================================ 4. dynamic-range gate on the completion increment (decline of R2-M3)
section("4. Dynamic-range gate: P(increment estimate < 2.0 | true increment) at n = 64, SE 0.5-0.7 [A]")
for se in (0.5, 0.7):
    print(f"  SE {se}: " + ", ".join(f"true {t}: {stats.norm.cdf((2.0-t)/se):.2f}" for t in (1.0, 1.5, 2.0, 2.5, 3.0)))
