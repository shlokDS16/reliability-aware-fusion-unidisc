"""Round-2 reliability intervals and planning calculations for the claim-evaluability rubric.

    python analysis/reliability/round2_intervals.py > analysis/reliability/round2_output.txt

Inputs : research/review/reliability/round2/rater-claude.jsonl, rater-codex.jsonl
Seed   : 20261014 (all resampling). Bootstrap: 10,000 resamples of PAPERS (cluster bootstrap),
         percentile intervals. A naive cell-level bootstrap is shown beside it to expose clustering.
Sections: A intervals (task 1) | B design effect (task 2) | C sample size for kappa (task 3)
          D stratified prevalence estimator and subsample size (task 4) | E power for E1-E3 (task 5)
          F pilot-count intervals (task 6)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
R2 = ROOT / "research" / "review" / "reliability" / "round2"
TYPES = ["CT1", "CT2", "CT3", "CT4", "CT5", "CT6"]
NAMES = {"CT1": "steps", "CT2": "time", "CT3": "inference quality", "CT4": "training quality",
         "CT5": "unification", "CT6": "vs autoregressive"}
SEED, B = 20261014, 10_000


def load(p: Path) -> dict:
    return {r["record_id"]: r for r in (json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip())}


A, Bq = load(R2 / "rater-claude.jsonl"), load(R2 / "rater-codex.jsonl")
IDS = sorted(set(A) & set(Bq))
N = len(IDS)


def yes(v) -> int:
    return int(v == "yes")


def ev(R, i, t) -> int:
    c = R[i]["claims"][t]
    return int(c["a"] == "yes" and c["b"] == "yes")


# counts[i, t, k]: k = 2*A + B  (A = Claude, B = Codex; 1 = yes). 0 nn, 1 ny, 2 yn, 3 yy
asr = np.zeros((N, 6, 4))
evl = np.zeros((N, 6, 4))
for ii, i in enumerate(IDS):
    for ti, t in enumerate(TYPES):
        a, b = yes(A[i]["claims"][t]["asserted"]), yes(Bq[i]["claims"][t]["asserted"])
        asr[ii, ti, 2 * a + b] = 1
        if a and b:
            evl[ii, ti, 2 * ev(A, i, t) + ev(Bq, i, t)] = 1


def stats2x2(c):
    """c[..., 4] -> dict of arrays: kappa, pabak, bias index, prevalence index, shares."""
    c = np.asarray(c, float)
    n = c.sum(-1)
    with np.errstate(all="ignore"):
        po = (c[..., 0] + c[..., 3]) / n
        pa, pb = (c[..., 2] + c[..., 3]) / n, (c[..., 1] + c[..., 3]) / n
        pe = pa * pb + (1 - pa) * (1 - pb)
        kap = np.where(pe < 1, (po - pe) / (1 - pe), np.nan)
        return dict(n=n, kappa=kap, po=po, pabak=2 * po - 1, bi=(c[..., 2] - c[..., 1]) / n,
                    pi=(c[..., 0] - c[..., 3]) / n, share_a=pa, share_b=pb)


def ci(x, lo=2.5, hi=97.5):
    x = np.asarray(x)
    ok = x[~np.isnan(x)]
    return (np.percentile(ok, lo), np.percentile(ok, hi), 1 - len(ok) / len(x)) if len(ok) else (np.nan, np.nan, 1.0)


rng = np.random.default_rng(SEED)
IDX = rng.integers(0, N, size=(B, N))  # one paper-resampling matrix, reused for every statistic


def boot(cnt):
    """cnt[N, 4] per-paper 2x2 counts -> bootstrap draws of stats (resampling papers)."""
    return stats2x2(cnt[IDX].sum(1))


def naive_boot(cnt, seed):
    """cell-level multinomial bootstrap (ignores clustering of cells within papers)."""
    tot = cnt.sum(0)
    r = np.random.default_rng(seed)
    return stats2x2(r.multinomial(int(tot.sum()), tot / tot.sum(), size=B))


def line(label, point, lo, hi, extra=""):
    return f"  {label:<34} {point:6.2f}  [{lo:5.2f}, {hi:5.2f}]  width {hi - lo:4.2f} {extra}"


def section_a():
    print(f"== A. Round 2 intervals: {N} papers, {B} paper-cluster bootstrap resamples, seed {SEED}, percentile ==")
    pa_cnt, pe_cnt = asr.sum(1), evl.sum(1)  # pooled over types: [N, 4]
    for lab, cnt in (("asserted, pooled 6 types (240 cells)", pa_cnt), ("evaluable flag, pooled (jointly asserted)", pe_cnt)):
        s0, sb, sn = stats2x2(cnt.sum(0)), boot(cnt), naive_boot(cnt, SEED + 1)
        lo, hi, _ = ci(sb["kappa"])
        nlo, nhi, _ = ci(sn["kappa"])
        print(line(f"kappa {lab}", float(s0["kappa"]), lo, hi, f"n={int(s0['n'])}; naive cell bootstrap [{nlo:.2f}, {nhi:.2f}]"))
    print("  per-type asserted kappa (n = 40 papers each):")
    for ti, t in enumerate(TYPES):
        s0, sb = stats2x2(asr[:, ti].sum(0)), boot(asr[:, ti])
        lo, hi, und = ci(sb["kappa"])
        c = asr[:, ti].sum(0)
        print(line(f"{t} {NAMES[t]}", float(s0["kappa"]), lo, hi,
                   f"yes: claude {int(c[2] + c[3])}, codex {int(c[1] + c[3])}, both {int(c[3])}; undefined draws {und:.0%}"))
    pe = evl.sum(1)
    s0, sb = stats2x2(pe.sum(0)), boot(pe)
    c = pe.sum(0)
    print("  evaluable flag, pooled over jointly asserted cells (n = %d):" % int(c.sum()))
    for lab, key in (("share evaluable, claude", "share_a"), ("share evaluable, codex", "share_b")):
        lo, hi, _ = ci(sb[key])
        print(line(lab, float(s0[key]), lo, hi))
    d = sb["share_a"] - sb["share_b"]
    lo, hi, _ = ci(d)
    print(line("share difference claude - codex", float(s0["share_a"] - s0["share_b"]), lo, hi, "(paired, = bias index)"))
    for lab, key in (("PABAK = 2*po - 1", "pabak"), ("bias index (c_yn - c_ny)/n", "bi"), ("prevalence index (c_nn - c_yy)/n", "pi")):
        lo, hi, _ = ci(sb[key])
        print(line(lab, float(s0[key]), lo, hi))
    lo, hi, _ = ci(sb["po"])
    print(line("raw agreement", float(s0["po"]), lo, hi))
    print(f"  evaluable 2x2 (rows claude, cols codex): nn {int(c[0])}, ny {int(c[1])}, yn {int(c[2])}, yy {int(c[3])}; "
          f"McNemar exact p = {stats.binomtest(int(c[1]), int(c[1] + c[2]), 0.5).pvalue:.3f}")
    print("  P(kappa_evaluable >= 0.60) among bootstrap draws: %.3f ; P(kappa_asserted < 0.60): %.3f" % (
        float(np.mean(np.nan_to_num(sb["kappa"], nan=-1) >= 0.60)),
        float(np.mean(np.nan_to_num(boot(asr.sum(1))["kappa"], nan=-1) < 0.60))))
    print("  per-type evaluable share (claude, codex) where both asserted:")
    for ti, t in enumerate(TYPES):
        c = evl[:, ti].sum(0)
        n = c.sum()
        print(f"    {t} {NAMES[t]:<18} n={int(n):2d}  claude {(c[2] + c[3]) / max(n, 1):.2f}  codex {(c[1] + c[3]) / max(n, 1):.2f}")
    return pa_cnt, pe_cnt


def section_b(pa_cnt, pe_cnt):
    print("\n== B. Clustering: design effect of papers on the kappa variance ==")
    for lab, cnt in (("asserted pooled", pa_cnt), ("evaluable pooled", pe_cnt)):
        vc = np.nanvar(boot(cnt)["kappa"])
        vn = np.nanvar(naive_boot(cnt, SEED + 2)["kappa"])
        cells_per_paper = cnt.sum() / N
        print(f"  {lab}: var ratio cluster/naive = {vc / vn:.2f} (DEFF), cells per paper {cells_per_paper:.2f}")
    # cross-type heterogeneity: pooled kappa vs mean of per-type kappas, and between-paper dependence of disagreement
    ks = [float(stats2x2(asr[:, ti].sum(0))["kappa"]) for ti in range(6)]
    print("  per-type asserted kappa mean (unweighted) %.2f vs pooled %.2f" % (np.mean(ks), float(stats2x2(pa_cnt.sum(0))["kappa"])))
    dis = (asr[:, :, 1] + asr[:, :, 2]).sum(1)  # disagreements per paper on asserted
    m, v = dis.mean(), dis.var(ddof=1)
    print(f"  asserted disagreements per paper: mean {m:.2f}, variance {v:.2f}; variance/mean {v / m:.2f} (1 = binomial-like; >1 = clustering)")
    dev = (evl[:, :, 1] + evl[:, :, 2]).sum(1)
    print(f"  evaluable disagreements per paper: mean {dev.mean():.2f}, variance {dev.var(ddof=1):.2f}; papers with >=1: {int((dev > 0).sum())}, with >=2: {int((dev > 1).sum())}")


# ---------- C. sample size for kappa -------------------------------------------------------
def cells_from(pa, pb, kap):
    pe = pa * pb + (1 - pa) * (1 - pb)
    po = pe + kap * (1 - pe)
    p11 = (po + pa + pb - 1) / 2
    return np.array([po - p11, pb - p11, pa - p11, p11])  # nn, ny, yn, yy


def _kap(p):
    """Cohen kappa from cell probabilities p[..., 4] = nn, ny, yn, yy (vectorised)."""
    po = p[..., 0] + p[..., 3]
    pa, pb = p[..., 2] + p[..., 3], p[..., 1] + p[..., 3]
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe)


def delta_se(p, n, h=1e-6):
    """Delta-method SE of kappa under multinomial(n, p): var = (sum p g^2 - (sum p g)^2) / n, g = numerical gradient."""
    p = np.asarray(p, float)
    g = np.stack([(_kap(p + h * np.eye(4)[k]) - _kap(p - h * np.eye(4)[k])) / (2 * h) for k in range(4)], -1)
    v = (p * g ** 2).sum(-1) - ((p * g).sum(-1)) ** 2
    return np.sqrt(np.maximum(v, 1e-12) / n)


def power_lb(n, pa, pb, kap_true, thr=0.60, reps=20000, z=1.96, seed=1):
    r = np.random.default_rng(seed)
    cnt = r.multinomial(n, cells_from(pa, pb, kap_true), size=reps).astype(float)
    ph = cnt / n
    with np.errstate(all="ignore"):
        k = _kap(ph)
        lb = k - z * delta_se(np.clip(ph, 1e-9, 1), n)
    return float(np.mean(np.nan_to_num(lb, nan=-1) > thr))


def section_c(pe_cnt):
    print("\n== C. Claims needed so that the lower 95% bound of kappa clears 0.60 when true kappa = 0.75 ==")
    print("  (delta-method SE inside a Monte Carlo of 20000 multinomial samples; two-sided 95% bound, z = 1.96;"
          " iid claims, i.e. before the paper/group design effect)")
    grid = list(range(30, 321, 10))
    for pa, pb in ((0.40, 0.40), (0.50, 0.50), (0.30, 0.30), (0.44, 0.34)):
        pw = {n: power_lb(n, pa, pb, 0.75, seed=n) for n in grid}
        n50 = next((n for n in grid if pw[n] >= 0.5), None)
        n80 = next((n for n in grid if pw[n] >= 0.8), None)
        p = cells_from(pa, pb, 0.75)
        ok = bool((p >= 0).all())
        print(f"  marginals evaluable-yes {pa:.2f}/{pb:.2f} (cells valid: {ok}): n for P(LB>0.60)>=0.5 : {n50}; >=0.8 : {n80};"
              f" P at n=30: {pw[30]:.2f}, n=60: {pw[60]:.2f}; analytic SE at n=100: {float(delta_se(p, 100)):.3f}")
    deff = 1.0
    print("  Paper/group design effect multiplies these n; a validation round of m papers yields about 1.55 jointly asserted"
          " claims per paper (62 / 40 in round 2): n_claims 150 ~ 97 papers, before any DEFF.")
    print("  Per type: needs n jointly asserted claims EACH; round-2 jointly asserted per type were:",
          {NAMES[t]: int(evl[:, ti].sum()) for ti, t in enumerate(TYPES)})
    # 30 human claims
    print("  30-claim human sheet: SE of a kappa at true 0.75, n=30 (marginals .4/.4): %.3f -> expected 95%% bounds %.2f to %.2f" % (
        float(delta_se(cells_from(.4, .4, .75), 30)), 0.75 - 1.96 * float(delta_se(cells_from(.4, .4, .75), 30)), 0.75 + 1.96 * float(delta_se(cells_from(.4, .4, .75), 30))))
    for k, n in ((0, 10), (1, 10)):
        print(f"  Clopper-Pearson upper 95% (one-sided) for error rate with {k}/{n} human-vs-model errors among agreements: "
              f"{stats.beta.ppf(0.95, k + 1, n - k):.3f}")
    for k in (10, 14, 15):
        lo, hi = stats.beta.ppf(0.025, k, 20 - k + 1), stats.beta.ppf(0.975, k + 1, 20 - k)
        print(f"  human sides with one named rater in {k}/20 disagreements: 95% CI [{lo:.2f}, {hi:.2f}]")
    c = pe_cnt.sum(0)
    print("  sheet weights: round-2 evaluable cells nn %d, ny %d, yn %d, yy %d; 20 disagreements all rated, 10 of %d agreements"
          " sampled -> agreement weight %.1f" % (c[0], c[1], c[2], c[3], int(c[0] + c[3]), (c[0] + c[3]) / 10))


# ---------- D. stratified, misclassification-corrected prevalence ------------------------------
def strat_estimate(N_s, n_s, y_s, draws=20000, seed=7):
    """Design-based (two-phase, stratified) estimate of the evaluable share for one claim type.
    Strata s: 'AA' both raters evaluable, 'NN' both not, 'D' discordant. N_s: stratum sizes in the corpus;
    n_s: number human-rated (random within stratum, D usually all); y_s: human-evaluable counts.
    Returns point, 95% interval (Jeffreys-Beta posterior draws with finite-population correction)."""
    r = np.random.default_rng(seed)
    tot = sum(N_s.values())
    pt = sum(N_s[s] / tot * (y_s[s] / n_s[s]) for s in N_s)
    sim = np.zeros(draws)
    for s in N_s:
        th = r.beta(y_s[s] + .5, n_s[s] - y_s[s] + .5, draws)
        rest = N_s[s] - n_s[s]  # unrated claims in the stratum
        sim += (n_s[s] * (y_s[s] / n_s[s]) + (r.binomial(rest, th) if rest > 0 else 0)) / tot
    return pt, np.percentile(sim, 2.5), np.percentile(sim, 97.5)


def plan_n(Ntot, w, p, target, deff=1.3):
    """Smallest human subsample n (agreements only; discordant claims all rated) with 95% half-width <= target,
    Neyman allocation between AA and NN. w = (wAA, wNN, wD), p = (pAA, pNN, pD) planning values."""
    wAA, wNN, wD = w
    NAA, NNN = wAA * Ntot, wNN * Ntot
    sd = {"AA": math.sqrt(p[0] * (1 - p[0])), "NN": math.sqrt(p[1] * (1 - p[1]))}
    for n in range(2, int(NAA + NNN) + 1):
        nAA = min(NAA, max(2, round(n * NAA * sd["AA"] / (NAA * sd["AA"] + NNN * sd["NN"]))))
        nNN = min(NNN, max(2, n - nAA))
        v = wAA ** 2 * p[0] * (1 - p[0]) * (1 / nAA - 1 / NAA) + wNN ** 2 * p[1] * (1 - p[1]) * (1 / nNN - 1 / NNN)
        if 1.96 * math.sqrt(deff * v) <= target:
            return n, nAA, nNN
    return None


def section_d(pe_cnt):
    c = pe_cnt.sum(0)
    tot = c.sum()
    w = (c[3] / tot, c[0] / tot, (c[1] + c[2]) / tot)
    print("\n== D. Stratified prevalence: planning table (human-rates ALL discordant claims + random subsample of agreements) ==")
    print(f"  round-2 stratum shares of jointly asserted claims: AA {w[0]:.2f}, NN {w[1]:.2f}, discordant {w[2]:.2f}")
    print("  planning values (ASSUMED, to be replaced by the validation round): human-evaluable rate AA 0.90, NN 0.10;"
          " group-clustering DEFF 1.3")
    print("  N_t = jointly asserted claims of the type | half-width 0.10 | half-width 0.07 : (total agreements to rate; AA, NN)")
    for Nt in (60, 150, 300):
        r1, r2 = plan_n(Nt, w, (.9, .1, .5), .10), plan_n(Nt, w, (.9, .1, .5), .07)
        d = int(round(w[2] * Nt))
        print(f"   N_t={Nt:3d} (discordant ~{d}) | {r1} | {r2}")
    print("  A demo of strat_estimate() needs human ratings and is run only on real adjudication data (none yet).")


def section_e():
    print("\n== E. Planning numbers for E1-E3 ==")
    z = stats.norm.ppf
    for pi in (0.30, 0.40, 0.44):
        for alpha, lab in ((0.05, "alpha .05"), (0.05 / 6, "Holm worst case .05/6")):
            n = ((z(1 - alpha) * 0.5 + z(0.8) * math.sqrt(pi * (1 - pi))) / (0.5 - pi)) ** 2
            print(f"  E1 one-sided, true share {pi:.2f} vs 0.50, {lab}: n asserted claims per type for 80% power = {math.ceil(n)}"
                  f" (x1.3 clustering = {math.ceil(1.3 * n)})")
    for p0, d in ((0.40, 0.0), (0.40, 0.03)):
        n = 2 * p0 * (1 - p0) * (z(0.95) + z(0.8)) ** 2 / (0.10 - d) ** 2
        print(f"  E2 TOST margin 0.10, per-group n for 80% power, true diff {d:.2f}, base share {p0}: {math.ceil(n)} claims per group")
    print("  E2 SE of a difference of two shares (p=.4) at n per group 40 / 100 / 200: "
          + " / ".join(f"{math.sqrt(2 * .24 / n):.3f}" for n in (40, 100, 200)) + "  (equivalence needs 1.645*SE < 0.10 even at zero true difference)")
    for p1 in (0.60, 0.65, 0.70):
        for n in range(10, 400):
            crit = stats.binom.isf(0.05, n, 0.5)  # reject if X > crit, i.e. P(X>=crit+1) <= .05
            if stats.binom.sf(crit, n, p1) >= 0.8:
                print(f"  E3 exact sign test (one-sided .05) true P(controlled smaller)={p1:.2f}: papers needed for 80% power = {n}")
                break
    print("  E1 sample frame: jointly asserted claims per paper by type in round 2 x 550 papers:",
          {NAMES[t]: round(evl[:, ti].sum() / N * 550) for ti, t in enumerate(TYPES)})


def section_f():
    print("\n== F. Pilot counts that the protocol and summaries word as support ==")
    for k, n, lab in ((2, 9, "H2(a): papers with a swept baseline reaching 2 T_m (pre-set: support if < 1/3, contradict if >= 1/2)"),
                      (7, 9, "papers not publishing the sweep"),):
        lo, hi = stats.beta.ppf(0.025, k, n - k + 1), stats.beta.ppf(0.975, k + 1, n - k)
        print(f"  {k}/{n}: {k / n:.2f}, Clopper-Pearson 95% [{lo:.2f}, {hi:.2f}] -- {lab}")
    print("  H2(b): 0.00 in 2 computable papers; one-sided 95%% upper bound for a proportion with 0/2 = %.2f" % stats.beta.ppf(0.95, 1, 2))


if __name__ == "__main__":
    pa_cnt, pe_cnt = section_a()
    section_b(pa_cnt, pe_cnt)
    section_c(pe_cnt)
    section_d(pe_cnt)
    section_e()
    section_f()
