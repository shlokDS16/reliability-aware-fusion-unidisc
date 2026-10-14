"""Statistician round-3 checks for EXP-001 v0.3 (no model data; card arithmetic, exact enumerations, simulations).

Run (CPU, single thread because of the system-commit limit noted in round 2):
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python analysis/stats/round3_exp001_check.py > analysis/stats/round3_exp001_check.log
Every parameter marked [A] is an illustrative assumption, not a measurement. Nothing printed here is an
experimental result. Card references are to research/preregistration/EXP-001-crossmodal-unidisc.md v0.3.
"""
import itertools
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261016)
z = stats.norm.ppf
Phi = stats.norm.cdf


def section(t):
    print("\n== " + t)


# ============================================================================ 1. plan generator and pass counts
def f(q, c, m):
    """floor rule of card 5.1: tokens committed at pass q of m when c are spread over m passes"""
    return (q * c) // m - ((q - 1) * c) // m


def window(kind, P, cT, cI):
    """list of (text, image) per pass inside one window"""
    if kind == "joint":
        return [(f(q, cT, P), f(q, cI, P)) for q in range(1, P + 1)]
    if kind == "pure":
        return [(cT, 0)] + [(0, f(q - 1, cI, P - 1)) for q in range(2, P + 1)]
    if kind == "tfj":
        return [(cT, f(1, cI, P))] + [(0, f(q, cI, P)) for q in range(2, P + 1)]
    raise ValueError(kind)


def plan(M, kind, N, LT=32, LI=1024, W=8):
    P = N // W
    out = []
    for w in range(1, W + 1):
        out += window(kind if w in M else "joint", P, LT // W, LI // W)
    return out


section("1a. Plan generator at k0 (N = 32, 512 px): per-window counts and blind-model passes (NC-6', card 8.8 and 12.1)")
DAw = {1, 2, 3, 4}  # any 4 windows; the count does not depend on which
arms = {"J": plan(set(), "joint", 32), "Alt": plan(set(range(1, 9)), "pure", 32),
        "DA": plan(DAw, "pure", 32), "TFJ": plan(DAw, "tfj", 32)}
blind_total = 0
for name, p in arms.items():
    assert len(p) == 32
    assert sum(t for t, _ in p) == 32 and sum(i for _, i in p) == 1024
    blind = sum((t > 0) + (i > 0) for t, i in p)  # a blind pass computes only the marginals the commit needs
    blind_total += blind
    print(f"{name}: passes {len(p)}, text {sum(t for t,_ in p)}, image {sum(i for _,i in p)}, "
          f"window-1 pattern {p[:4]}, blind-model passes {blind}")
print(f"blind passes per seed over the four arms = {blind_total} (card: 196); x 128 seeds = {128*blind_total} (card: 25,088)")
print("pure window at k+ (P=2):", window("pure", 2, 4, 128), "; at k- (P=8):", window("pure", 8, 4, 128))

section("1b. Core passes by stage (card 12.1), recomputed from the card's own per-trajectory formulas")
R, g, kT0, kTp = 8, 4, 1, 2
tri, itr = R * kT0, R * g                       # 8 and 32 extra passes per probed pass at k0
d1 = 128 * (32 + 8 * tri) + 64 * (4 * itr) + 64 * (16 + 8 * R * kTp)
d2 = 256 * (32 + 4 * (tri + itr)) + 128 * (tri + itr) + 32 * 5 * 8
rtr = 64 * (32 + 4 * (tri + itr)) + 32 * (tri + itr)
nc6 = 128 * blind_total
d3 = 500 * (5 * 32 + 2 * 16) + 250 * (24 + 24)
pcb_per = 3 * (21 + 3 * 2.2) + 24 * 2.2 + 24   # CFG on 1-3, 12-14, 22-24 (3 guided steps each), all 24 guided, unguided
pcb = 96 * pcb_per
pilot_card = 40000
stages = {"2 pilot (card value, not re-derivable: see 1c)": pilot_card, "2b PC-B": pcb, "3 D1": d1, "4a D2": d2,
          "4b condition-R trace": rtr, "5 NC-6'": nc6, "6 D3": d3}
for k, v in stages.items():
    print(f"stage {k}: {v:,.1f}")
print(f"  D1 parts: {128*(32+8*tri):,} + {64*4*itr:,} + {64*(16+8*R*kTp):,}; PC-B pass-equivalents per prompt = {pcb_per:.1f} (card 159.6)")
core = sum(stages.values())
print(f"core passes = {core:,.0f} (card: about 287,000); with the P_rand regeneration (+4,096) = {core+4096:,.0f}")
for tb in (0.129, 0.09):
    comp = core * tb / 3600
    print(f"t_b={tb}: pass compute {comp:.2f} h; + gates 1.0 + evaluation 1.5 = {comp+2.5:.2f} h; wall at duty 0.5 = {2*(comp+2.5):.2f} h")
print(f"non-D3 passes in the general rule = core - 192 x 500 = {core-96000:,.0f} (card: 191,000)")
print(f"stage-1 gate passes counted only as hours: PG-V + D-ref 96 x 32 = {96*32:,} passes = {96*32*0.129/3600:.2f} h at 0.129 s "
      "(card stage 1 'about 0.8 h' = 0.7 guided + 0.1 P leg; these 0.11 h are not in it)")

section("1c. Pilot probe and gate passes (card: 'about 31,000'); reconstruction under stated assumptions [A]")
parts = {
    "16 traj x 5 probes (1,2,6,26,30) x 40": 16 * 5 * 40,
    "G1b 16 x 5 x 8": 16 * 5 * 8,
    "NC-1 blind wrapper, 16 x 5 x 40": 16 * 5 * 40,
    "G3 + G3b injection, 2 x 16 x 5 x 8 (T->I only)": 2 * 16 * 5 * 8,
    "G4 R=32 at 3 probes, 16 x 3 x (32 + 128)": 16 * 3 * (32 + 128),
    "G5 g=8 and g=32 at 2 probes, 16 x 2 x (64 + 256)": 16 * 2 * (64 + 256),
    "G5 reverse order, 8 x 2 x 32": 8 * 2 * 32,
    "G6 probe-off regeneration 16 x 32": 16 * 32,
    "precision block 64 x 2": 128,
}
for k, v in parts.items():
    print(f"  {k}: {v:,}")
print(f"  sum = {sum(parts.values()):,} (card: about 31,000; the card gives no formula for this line)")

section("1d. n_cap rule (card 10.4, 12.1): wall(n) = (1/duty)[(X + 192 n) t_b/3600 + 2.5] <= 26 h")


def ncap(tb, X=191000, duty=0.5, cap=26.0, lo=500, hi=1000):
    nmax = ((cap * duty - 2.5) * 3600 / tb - X) / 192
    if nmax < lo:
        return None, nmax
    return int(min(hi, np.floor(nmax))), nmax


for tb in (0.09, 0.10, 0.12, 0.125, 0.129, 0.130, 0.1317, 0.135, 0.14):
    nc, raw = ncap(tb)
    print(f"t_b={tb:.4f}: wall(500) = {2*((191000+96000)*tb/3600+2.5):.2f} h; n_cap = {nc if nc else 'EMPTY SET (rule undefined)'} (unclipped n_max {raw:.0f})")
tb_star = (26 * 0.5 - 2.5) * 3600 / (191000 + 192 * 500)
print(f"t_b above which no n in [500, 1000] satisfies the cap: {tb_star:.4f} s ({100*(tb_star/0.129-1):.1f} percent above the planning 0.129 s)")
extra = {"G5 falls back to g = 8 (+32 per I->T probe: D1 64x4, D2 256x4 + 128, condition R 64x4 + 32)":
         32 * (64 * 4 + 256 * 4 + 128 + 64 * 4 + 32),
         "f_ord = 2 (I->T probes doubled at g = 4: same sets)": 32 * (64 * 4 + 256 * 4 + 128 + 64 * 4 + 32),
         "P_rand regeneration on D0": 4096}
for k, v in extra.items():
    nc, raw = ncap(0.129, X=191000 + v)
    print(f"  {k}: +{v:,} passes = +{v*0.129/3600:.2f} compute h = +{2*v*0.129/3600:.2f} wall h; n_cap at 0.129 s with it = {nc} (n_max {raw:.0f})")
print("  Evaluation is held at 1.5 h in the rule; it scales with n (V-lift 3 forwards per scored sample at about 0.2 s [A]):"
      f" at n = 1000 about +{(7*500*3*0.2)/3600:.2f} compute h for V-lift alone")

# ============================================================================ 2. Spearman critical values
section("2. Spearman critical values (card 10.3): exact enumeration, n = 8, no ties")
n8 = 8
base = np.arange(n8)
D = np.array([int(((base - np.array(p)) ** 2).sum()) for p in itertools.permutations(range(n8))])
vals, counts = np.unique(D, return_counts=True)
pD = counts / counts.sum()
rho_vals = 1 - 6 * vals / (n8 * (n8**2 - 1))
print(f"permutations {counts.sum()}, distinct rho values {len(vals)}, rho step {6*2/(n8*(n8**2-1)):.5f}")
tail = {r: pD[rho_vals >= r - 1e-12].sum() for r in rho_vals}
for r in sorted(tail, reverse=True):
    if 0.55 <= r <= 0.75:
        print(f"  P(rho >= {r:.4f}) = {tail[r]:.5f}")
crit1 = min(r for r in rho_vals if tail[r] <= 0.05)
print(f"single stratum: smallest rho with P(rho >= rho) <= 0.05 is {crit1:.4f}, P = {tail[crit1]:.5f} (card: 0.643, P = 0.048)")
# mean of two independent strata: exact convolution over D1 + D2
S = {}
for i, a in enumerate(vals):
    for j, b in enumerate(vals):
        S[a + b] = S.get(a + b, 0.0) + pD[i] * pD[j]
Ss = np.array(sorted(S))
pS = np.array([S[s] for s in Ss])
rbar = 1 - 6 * Ss / (2 * n8 * (n8**2 - 1))  # mean of the two rhos
order = np.argsort(-rbar)
cum = np.cumsum(pS[order])
for idx in range(len(order)):
    r = rbar[order[idx]]
    if 0.38 <= r <= 0.50:
        print(f"  P(rho_strat >= {r:.4f}) = {cum[idx]:.5f}")
ok = [rbar[order[i]] for i in range(len(order)) if cum[i] <= 0.05]
crit2 = min(ok)
print(f"two strata: smallest rho_strat with P(rho_strat >= c) <= 0.05 is c = {crit2:.4f}, P = {cum[list(rbar[order]).index(crit2)]:.5f} "
      "(card: 0.440 / simulated 0.4405)")
print(f"P(rho_strat >= 0.5) under the null = {pS[rbar >= 0.5 - 1e-12].sum():.5f}; P(rho >= 0.5) single stratum = {pD[rho_vals >= 0.5-1e-12].sum():.5f}")

# ============================================================================ 3. sizing figures with the 4-member Holm family
section("3. Sizing figures of 10.4 with the current 4-member Holm family (sigma_d = sqrt(2) sigma_L, rho_pair 0, m = 1)")
for a_lab, a in (("0.05", 0.05), ("0.05/4 = 0.0125 (smallest Holm level, 4 members)", 0.0125), ("0.05/7 (card text, stale)", 0.05 / 7)):
    sd = np.sqrt(2) * 4
    nn = ((z(1 - a / 2) + z(0.9)) * sd) ** 2
    pw = {(sL, n): Phi(np.sqrt(n) / (np.sqrt(2) * sL) - z(1 - a / 2)) for sL in (4, 5, 6) for n in (500, 530)}
    print(f"alpha {a_lab}: n(0.90, sigma_L 4) = {nn:.1f}; power n=500: " +
          ", ".join(f"sL={sL}: {pw[(sL,500)]:.3f}" for sL in (4, 5, 6)) +
          "; n=530: " + ", ".join(f"sL={sL}: {pw[(sL,530)]:.3f}" for sL in (4, 5, 6)))
fac = np.sqrt(63 / stats.chi2.ppf(0.20, 63))
print(f"chi2 upper-bound factor sqrt(63/chi2_0.20,63) = {fac:.4f}")
for sig_hat in (4.5, 5.0, 5.23, 5.66, 6.0, 7.07):
    up = sig_hat * fac
    nreq = int(np.ceil(1.5 * ((1.96 + 1.2816) * up) ** 2))
    print(f"  pilot sigma_d {sig_hat}: sigma_d,up {up:.3f}, n_req {nreq}, n_conf at t_b 0.129 = {min(531, max(500, nreq))}, "
          f"achieved MDE at n_conf {(1.96+1.2816)*up/np.sqrt(min(531, max(500, nreq))):.3f}")
s500 = np.sqrt(500 / 1.5) / (1.96 + 1.2816) / fac
s531 = np.sqrt(531 / 1.5) / (1.96 + 1.2816) / fac
print(f"n_req <= 500 iff pilot sigma_d <= {s500:.3f}; n_req <= 531 iff pilot sigma_d <= {s531:.3f} (card planning sigma_d = 5.657)")

# ============================================================================ 4. condition R (64 trajectories)
section("4a. Condition R, 64 trajectories: delta method on ln(ratio of pooled means); cv of per-trajectory early and late averages, correlation r [A]")


def se_ln(cv, r, n):
    return np.sqrt((2 * cv**2 - 2 * r * cv**2) / n)


print("P(lower 90% > 1.0 | true ratio)  and  P(upper 90% < 1.25 | true ratio):")
for cv in (0.5, 0.75, 1.0, 1.5):
    for r in (0.0, 0.3, 0.6):
        se = se_ln(cv, r, 64)
        lo = {tr: Phi(np.log(tr) / se - z(0.95)) for tr in (1.0, 1.15, 1.3, 1.5)}
        up = {tr: Phi((np.log(1.25) - np.log(tr)) / se - z(0.95)) for tr in (1.0, 1.15)}
        print(f"  cv={cv} r={r}: SE(ln)={se:.3f} | lower>1: " + " ".join(f"{k}:{v:.2f}" for k, v in lo.items())
              + " | upper<1.25: " + " ".join(f"{k}:{v:.2f}" for k, v in up.items()))
print("Both directions must agree (conjunction): at cv 0.5, r 0.3, true 1.3 in both, independent directions: "
      f"{Phi(np.log(1.3)/se_ln(0.5,0.3,64)-z(0.95))**2:.2f}; at cv 1.0: {Phi(np.log(1.3)/se_ln(1.0,0.3,64)-z(0.95))**2:.2f}")
print("Unpaired ratio of ratios (confidence D2 n = 256 over random n = 64), P(lower 90% of ln ratio-of-ratios > 0):")
for cv in (0.5, 1.0):
    se = np.sqrt(se_ln(cv, 0.3, 256) ** 2 + se_ln(cv, 0.3, 64) ** 2)
    print(f"  cv={cv}: SE {se:.3f}; conf 1.75 vs random 1.0: {Phi(np.log(1.75)/se - z(0.95)):.2f}; vs random 1.3: {Phi(np.log(1.75/1.3)/se - z(0.95)):.2f}")


def boot_ratio_sim(n, cv, r, true_ratio, zero_share=0.0, reps=1500, B=2000):
    """percentile bootstrap of the ratio of pooled means, lognormal per-trajectory early/late with correlation r"""
    s2 = np.log(1 + cv**2)
    cov = np.array([[s2, r * s2], [r * s2, s2]])
    L = np.linalg.cholesky(cov)
    hit_lo, hit_up = 0, 0
    for _ in range(reps):
        x = rng.standard_normal((n, 2)) @ L.T - s2 / 2
        e = true_ratio * np.exp(x[:, 0]) * (rng.random(n) > zero_share)
        l = np.exp(x[:, 1]) * (rng.random(n) > zero_share)
        idx = rng.integers(0, n, (B, n))
        rr = e[idx].sum(1) / np.maximum(l[idx].sum(1), 1e-300)
        q05, q95 = np.quantile(rr, [0.05, 0.95])
        hit_lo += q05 > 1.0
        hit_up += q95 < 1.25
    return hit_lo / reps, hit_up / reps


section("4b. Condition R, simulated percentile bootstrap at n = 64 (lognormal, optional exact zeros) [A]")
for cv, r, zs in ((0.5, 0.3, 0.0), (1.0, 0.3, 0.0), (1.0, 0.3, 0.3)):
    out = []
    for tr in (1.0, 1.3, 1.5):
        lo, up = boot_ratio_sim(64, cv, r, tr, zs)
        out.append(f"true {tr}: P(lo90>1) {lo:.3f}, P(up90<1.25) {up:.3f}")
    print(f"cv={cv} r={r} zeros={zs}: " + " | ".join(out))

# ============================================================================ 5. PG-V and PC-F operating characteristics
section("5. PG-V (n = 48) and PC-F operating characteristics by simulation [A: noun-genericity model]")


def pgv_sim(q, m, d, n=48, reps=40000, conc=4.0, thr=(0.60, 0.50, 0.25)):
    """q = P(N_i non-empty); m = overall matched rate; d = m - s. For non-empty i: genericity ps_i ~ Beta(mean s/q, conc);
    matched prob pm_i = ps_i + (1 - ps_i) h with h set so that the mean of pm_i is m/q; 4 derangement draws ~ Bern(ps_i)."""
    pmc, psc = m / q, (m - d) / q
    if not (0 < psc < pmc <= 1):
        return None
    a, b = psc * conc, (1 - psc) * conc
    h = (pmc - psc) / (1 - psc)
    ne = rng.random((reps, n)) < q
    ps = rng.beta(a, b, (reps, n))
    pm = ps + (1 - ps) * h
    mt = (rng.random((reps, n)) < pm) & ne
    sh = ((rng.random((reps, n, 4)) < ps[..., None]).mean(2)) * ne
    share = ne.mean(1)
    mh, sh_ = mt.mean(1), sh.mean(1)
    pa, pb, pc = share >= thr[0], mh >= thr[1], (mh - sh_) >= thr[2]
    return (pa & pb & pc).mean(), pa.mean(), pb.mean(), pc.mean(), (mh - sh_).std(), mh.std()


print("q    m     m-s   P(pass)  P(a)   P(b)   P(c)   SD(m-s) SD(m)   designer normal approx (SE 0.07, 0.09, (a) ignored)")
for q in (0.65, 0.75, 0.9, 1.0):
    for m in (0.55, 0.65, 0.75):
        for d in (0.10, 0.25, 0.30, 0.40):
            res = pgv_sim(q, m, d)
            if res is None:
                continue
            approx = Phi((m - 0.5) / 0.07) * Phi((d - 0.25) / 0.09)
            print(f"{q:.2f} {m:.2f}  {d:.2f}  {res[0]:.3f}    {res[1]:.3f}  {res[2]:.3f}  {res[3]:.3f}  {res[4]:.3f}   {res[5]:.3f}   {approx:.3f}")
print("Ladder: P(terminal false stop) = P(fail rung 1) x P(fail rung 2) if both rungs are adequate and independent:")
for p1 in (0.95, 0.8, 0.6):
    print(f"  P(pass) per rung {p1}: {(1-p1)**2:.3f}")
print("PC-F (real pairs, q = 1): pass iff m_real >= 0.70 and m_real - s_real >= 0.40")
for m in (0.75, 0.85, 0.95):
    for s in (0.20, 0.30, 0.40):
        res = pgv_sim(1.0, m, m - s, thr=(0.0, 0.70, 0.40))
        if res is not None:
            print(f"  m_real {m:.2f}, s_real {s:.2f}: P(pass) {res[0]:.3f}")

# ============================================================================ 6. stratified T->I estimator (card 8.2) on a toy
section("6. Stratified T->I estimator on a toy with known I (card 8.2 step 2 and 4; G0 addition)")


def kl(p, q):
    return float(np.sum(p * (np.log(p) - np.log(q))))


def make_toy(w, KP=2, KC=20, V=40, conc=0.3):
    pa = np.concatenate([w * rng.dirichlet(np.ones(KP)), (1 - w) * rng.dirichlet(np.ones(KC))])
    pb = rng.dirichlet(conc * np.ones(V), KP + KC) * 0.9 + 0.1 / V
    pb /= pb.sum(1, keepdims=True)
    return pa, pb, KP


def truths(pa, pb, KP):
    mb = pa @ pb
    I = sum(pa[i] * kl(pb[i], mb) for i in range(len(pa)))
    w = pa[:KP].sum()
    mP = pa[:KP] @ pb[:KP] / w
    mC = pa[KP:] @ pb[KP:] / (1 - w)
    between = w * kl(mP, mb) + (1 - w) * kl(mC, mb)
    wC = (1 - w) * sum(pa[KP + i] / (1 - w) * kl(pb[KP + i], mC) for i in range(len(pa) - KP))
    wP = w * sum(pa[i] / w * kl(pb[i], mP) for i in range(KP))
    return I, between, wP, wC


def strat_est(pa, pb, KP, nP=4, nC=4):
    w = pa[:KP].sum()
    aP = rng.choice(KP, nP, p=pa[:KP] / w)
    aC = KP + rng.choice(len(pa) - KP, nC, p=pa[KP:] / (1 - w))
    mP, mC = pb[aP].mean(0), pb[aC].mean(0)
    mb = w * mP + (1 - w) * mC
    wP = w * np.mean([kl(pb[a], mP) for a in aP])
    wC = (1 - w) * np.mean([kl(pb[a], mC) for a in aC])
    btw = w * kl(mP, mb) + (1 - w) * kl(mC, mb)
    tot_direct = w * np.mean([kl(pb[a], mb) for a in aP]) + (1 - w) * np.mean([kl(pb[a], mb) for a in aC])
    return btw, wP, wC, tot_direct


def unstrat_est(pa, pb, R=8):
    a = rng.choice(len(pa), R, p=pa)
    mb = pb[a].mean(0)
    return np.mean([kl(pb[x], mb) for x in a])


maxdev = 0.0
for w in (0.5, 0.9, 0.99, 0.995):
    pa, pb, KP = make_toy(w)
    I, btw_t, wP_t, wC_t = truths(pa, pb, KP)
    st = np.array([strat_est(pa, pb, KP) for _ in range(4000)])
    maxdev = max(maxdev, np.abs(st[:, 0] + st[:, 1] + st[:, 2] - st[:, 3]).max())
    un = np.array([unstrat_est(pa, pb) for _ in range(4000)])
    print(f"w={w}: true I {I:.4f} = between {btw_t:.4f} + within-pad {wP_t:.4f} + within-content {wC_t:.4f} "
          f"(content share {wC_t/I:.2f})")
    print(f"   stratified 4/4 mean: total {st[:,3].mean():.4f} (between {st[:,0].mean():.4f}, within-content {st[:,2].mean():.4f}); "
          f"unstratified R=8 mean {un.mean():.4f}; SDs {st[:,3].std():.4f} vs {un.std():.4f}")
    if w >= 0.99:
        print(f"   card rule (class mass < 0.01 -> all 8 draws from the other class): within-content has no draws; "
              f"its true value {wC_t:.4f} is {100*wC_t/I:.0f} percent of I and is undefined/dropped")
print(f"max |between + within-pad + within-content - direct total| over all stratified draws = {maxdev:.2e} (exact identity)")

# ============================================================================ 7. receiving-set sizes per probe at k0
section("7. Still-masked receiving positions per probe at k0 (512 px; state before pass n; same under condition R)")
for npass in (1, 2, 6, 26, 30):
    print(f"pass {npass}: image {1024 - (npass-1)*32}, text {32 - (npass-1)} (I->T before pad-class exclusion)")
print("I->T late probes (26, 30) pool at most 256 x (7 + 3) = 2,560 text positions in D2 and 64 x 10 = 640 in condition R")

# ============================================================================ 6b. finite-R agreement (what the G0 addition can require)
section("6b. Stratified vs unstratified vs exact I on the toy as R grows (per-class draws R/2 for the stratified estimator)")
for w in (0.5, 0.9):
    pa, pb, KP = make_toy(w)
    I = truths(pa, pb, KP)[0]
    for Rtot in (8, 64, 256):
        st = np.array([strat_est(pa, pb, KP, Rtot // 2, Rtot // 2)[3] for _ in range(1500)])
        un = np.array([unstrat_est(pa, pb, Rtot) for _ in range(1500)])
        print(f"w={w} R={Rtot}: exact {I:.4f}; stratified {st.mean():.4f} (MC SE {st.std()/np.sqrt(len(st)):.4f}, bias {100*(st.mean()/I-1):+.1f}%); "
              f"unstratified {un.mean():.4f} (MC SE {un.std()/np.sqrt(len(un)):.4f}, bias {100*(un.mean()/I-1):+.1f}%); "
              f"difference / combined SE = {(st.mean()-un.mean())/np.sqrt(st.var()/len(st)+un.var()/len(un)):+.1f}")

# ============================================================================ 8. resolvable ratio for condition R
section("8. Condition R: true ratio resolvable with P(lower 90% > 1.0) = 0.8 and 0.9 at n = 64, per direction (delta method) [A]")
for cv in (0.5, 0.75, 1.0, 1.5):
    for r in (0.0, 0.3):
        se = se_ln(cv, r, 64)
        print(f"  cv={cv} r={r}: power 0.8 at ratio {np.exp(se*(z(0.95)+z(0.8))):.2f}; power 0.9 at {np.exp(se*(z(0.95)+z(0.9))):.2f}")
