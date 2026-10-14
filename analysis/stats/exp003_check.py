"""EXP-003 v0.1 statistician check: simulation of the ratio-of-sums discordant-noun statistic.
Synthetic data only (no EXP-003 data exist). Seeds fixed. Not evidence on any hypothesis.
Run: python analysis/stats/exp003_check.py > analysis/stats/exp003_check.log
"""
import numpy as np
from scipy.stats import norm
rng = np.random.default_rng(20261015)

def sim_arm(P, nd_mean, link, tau_img=0.6, base_sd=0.5, p0=0.28, ov=True):
    """per prefix: num_p, den_p of Lambda_d. nd_mean = mean discordant nouns per sample.
    Presence prob of noun in sibling image = base_p + image effect; own image adds `link`."""
    num = np.zeros(P); den = np.zeros(P)
    for p in range(P):
        base = np.clip(p0 + base_sd * (rng.beta(2, 5) - 2/7), 0.02, 0.9)   # prefix-level base rate
        u = rng.normal(0, tau_img, 2)                                      # image-level "object-likeness"
        for e in (0, 1):
            k = rng.poisson(nd_mean)
            if k == 0: continue
            lg = lambda b, uu: 1/(1+np.exp(-(np.log(b/(1-b)) + uu)))
            po = np.clip(lg(base, u[e]) + link, 0, 1)
            ps = lg(base, u[1-e])
            yo = rng.random(k) < po; ys = rng.random(k) < ps
            num[p] += (yo.astype(int) - ys.astype(int)).sum(); den[p] += k
    return num, den

def boot(numA, denA, numB, denB, B=2000, idx=None):
    P = len(numA)
    I = rng.integers(0, P, (B, P))
    a = numA[I].sum(1) / np.maximum(denA[I].sum(1), 1e-9)
    b = numB[I].sum(1) / np.maximum(denB[I].sum(1), 1e-9)
    return a - b

def influence_sd(num, den):
    L = num.sum()/den.sum(); return ((num - L*den)/den.mean()).std(ddof=1), L

def run(P, ndA, ndB, trueD, nrep=400, B=1000, label=''):
    sdA=[]; sdD=[]; rej=0; nullc=0; cov90=0; est=[]
    for r in range(nrep):
        nA, dA = sim_arm(P, ndA, 0.0 + trueD)    # arm G with link trueD
        nB, dB = sim_arm(P, ndB, 0.0)            # arm P64 with link 0
        la, lb = nA.sum()/dA.sum(), nB.sum()/dB.sum()
        d = la - lb; est.append(d)
        th = boot(nA, dA, nB, dB, B)
        lo95, hi95 = np.percentile(th, [2.5, 97.5]); lo90, hi90 = np.percentile(th, [5, 95])
        rej += (lo95 > 0) or (hi95 < 0)
        nullc += (lo90 > -0.10) and (hi90 < 0.10)
        cov90 += (lo90 <= trueD <= hi90)
        ia = (nA - la*dA)/dA.mean(); ib = (nB - lb*dB)/dB.mean()
        sdD.append((ia - ib).std(ddof=1))
    est = np.array(est)
    print(f"{label:34s} P={P} nd/sample A={ndA} B={ndB} trueD={trueD:.2f} | sd_diff(prefix influence) mean={np.mean(sdD):.3f} "
          f"| mean est={est.mean():+.3f} (bias {est.mean()-trueD:+.3f}) emp SE={est.std():.3f} "
          f"| P(reject95)={rej/nrep:.3f} P(null90)={nullc/nrep:.3f} cover90={cov90/nrep:.3f}")


# ---------------- v0.2 check: seed-balanced link Lambda_b vs instance-weighted ratio Lambda_d ----------------
def sim_arm_v2(P, nd_mean, link, couple=0.0, tau_img=0.6, noun_sd=1.0, od=None):
    """Return per-prefix arrays: Lp (nan if a side has no discordant noun), num, den (for Lambda_d).
    couple: count of a seed scales as exp(couple*u_e) with u_e its image-level logit yes-bias (red-team F-1 toy).
    od: if not None, counts are negative binomial with size od (overdispersion), else Poisson.
    Noun-level base logits a_n ~ N(logit(base_p), noun_sd) (heterogeneous nouns)."""
    Lp = np.full(P, np.nan); num = np.zeros(P); den = np.zeros(P)
    for p in range(P):
        base = np.clip(0.28 + 0.5*(rng.beta(2, 5) - 2/7), 0.02, 0.9)
        u = rng.normal(0, tau_img, 2)
        sides = []
        for e in (0, 1):
            lam = nd_mean*np.exp(couple*u[e])
            k = rng.poisson(lam) if od is None else rng.negative_binomial(od, od/(od+lam))
            if k == 0: sides.append(None); continue
            a = np.log(base/(1-base)) + rng.normal(0, noun_sd, k)
            f = lambda z: 1/(1+np.exp(-z))
            po = np.clip(f(a + u[e]) + link, 0, 1); ps = f(a + u[1-e])
            d = (rng.random(k) < po).astype(int) - (rng.random(k) < ps).astype(int)
            sides.append(d.mean()); num[p] += d.sum(); den[p] += k
        if sides[0] is not None and sides[1] is not None: Lp[p] = 0.5*(sides[0] + sides[1])
    return Lp, num, den

def run_v2(P, ndA, ndB, trueD, couple=0.0, od=None, nrep=300, B=1000, label='', coupleB=None):
    coupleB = couple if coupleB is None else coupleB
    out = dict(sdb=[], sdd=[], dd=[], db=[], rejb=0, rejd=0, nullb=0, nulld=0, excl=[], covb=0)
    for r in range(nrep):
        LA, nA, dA = sim_arm_v2(P, ndA, trueD, couple, od=od)
        LB, nB, dB = sim_arm_v2(P, ndB, 0.0, coupleB, od=od)
        el = ~np.isnan(LA) & ~np.isnan(LB)             # eligible in both arms (card 4.1)
        out['excl'].append(1 - el.mean())
        db_ = np.nanmean(LA[el]) - np.nanmean(LB[el]); out['db'].append(db_)
        dd_ = nA.sum()/dA.sum() - nB.sum()/dB.sum(); out['dd'].append(dd_)
        I = rng.integers(0, P, (B, P))
        e_, a_, b_ = el[I], np.where(el, LA, 0)[I], np.where(el, LB, 0)[I]
        thb = (a_.sum(1) - b_.sum(1)) / np.maximum(e_.sum(1), 1)
        thd = nA[I].sum(1)/np.maximum(dA[I].sum(1), 1e-9) - nB[I].sum(1)/np.maximum(dB[I].sum(1), 1e-9)
        for nm, th in (('b', thb), ('d', thd)):
            lo95, hi95 = np.percentile(th, [2.5, 97.5]); lo90, hi90 = np.percentile(th, [5, 95])
            out['rej'+nm] += (lo95 > 0) or (hi95 < 0); out['null'+nm] += (lo90 > -0.1) and (hi90 < 0.1)
            if nm == 'b': out['covb'] += (lo90 <= trueD <= hi90)
        ia = np.where(el, LA - np.nanmean(LA[el]), 0) - np.where(el, LB - np.nanmean(LB[el]), 0)
        out['sdb'].append(ia[el].std(ddof=1)*np.sqrt(el.mean()))   # SD of per-prefix contribution to the mean over all P prefixes
        ra = (nA - dA*nA.sum()/dA.sum())/dA.mean(); rb = (nB - dB*nB.sum()/dB.sum())/dB.mean()
        out['sdd'].append((ra - rb).std(ddof=1))
    n = nrep
    print(f"{label:30s} nd A/B={ndA}/{ndB} od={od} couple={couple}/{coupleB} true={trueD:.2f} | excluded share {np.mean(out['excl']):.3f} | "
          f"Lambda_b: mean {np.mean(out['db']):+.3f} SE {np.std(out['db']):.3f} P(rej95) {out['rejb']/n:.3f} P(null90) {out['nullb']/n:.3f} cov90 {out['covb']/n:.3f} | "
          f"Lambda_d: mean {np.mean(out['dd']):+.3f} SE {np.std(out['dd']):.3f} P(rej95) {out['rejd']/n:.3f} P(null90) {out['nulld']/n:.3f}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'v2':
        print("v0.2 check: Lambda_b (seed-balanced, eligible prefixes only) against Lambda_d (instance-weighted ratio), P = 150, 300 reps, B = 1000")
        print("-- F-1 toy: seed count coupled to image yes-bias, true link 0 (bias of the estimators = mean column)")
        run_v2(150, 3.0, 3.0, 0.0, couple=0.0, label='no coupling')
        run_v2(150, 3.0, 3.0, 0.0, couple=0.5, label='coupling 0.5')
        run_v2(150, 3.0, 3.0, 0.0, couple=1.0, label='coupling 1.0')
        print("-- coupling in arm A only (arm-level bias of the absolute statistic; arm B uncoupled), true link 0")
        run_v2(150, 3.0, 3.0, 0.0, couple=1.0, coupleB=0.0, label='A coupled 1.0, B none')
        run_v2(150, 3.0, 3.0, 0.0, couple=2.0, coupleB=0.0, label='A coupled 2.0, B none')
        print("-- efficiency, no coupling")
        for (a, b, t) in ((4, 4, 0.0), (4, 4, 0.10), (2, 4, 0.0), (2, 4, 0.10), (1, 3, 0.0), (1, 3, 0.10)):
            run_v2(150, a, b, t, label='Poisson counts')
        print("-- overdispersed counts (NB size 1.5), efficiency")
        for (a, b, t) in ((3, 3, 0.0), (3, 3, 0.10), (1.5, 3, 0.0), (1.5, 3, 0.10)):
            run_v2(150, a, b, t, od=1.5, label='NB counts')
        sys.exit(0)

    print("Analytic check of card table (sigma_d 0.45, n 150):")
    se = 0.45/np.sqrt(150); print(f" SE={se:.4f}; power(0.10)={norm.cdf(0.10/se-1.96)+norm.cdf(-0.10/se-1.96):.3f}; "
          f"P(null|0)={norm.cdf((0.10-1.645*se)/se)-norm.cdf((-0.10+1.645*se)/se):.3f}; n(0.90 power)={((1.96+1.2816)*0.45/0.10)**2:.0f}")
    for s in (0.30, 0.35, 0.45, 0.55, 0.65, 0.80):
        se = s/np.sqrt(150)
        print(f" sigma_d={s:.2f}: SE={se:.4f} power@0.10={norm.cdf(0.10/se-1.96):.3f} P(null|true 0)={max(0,2*norm.cdf((0.10-1.645*se)/se)-1):.3f} "
              f"P(null|true 0.05)={max(0,norm.cdf((0.10-1.645*se-0.05)/se)-norm.cdf((-0.10+1.645*se-0.05)/se)):.3f}")
    print("Simulation, 150 prefixes (nd = mean discordant nouns per sample; stated bootstrap B=1000, 400 reps):")
    run(150, 4.0, 4.0, 0.0, label='plenty of nouns, null')
    run(150, 2.0, 4.0, 0.0, label='G sparse (2 vs 4), null')
    run(150, 1.0, 3.0, 0.0, label='G very sparse (1 vs 3), null')
    run(150, 2.0, 4.0, 0.10, label='G sparse, true 0.10')
    run(150, 4.0, 4.0, 0.10, label='plenty of nouns, true 0.10')
    run(150, 1.0, 3.0, 0.10, label='G very sparse, true 0.10')
    run(60, 1.0, 3.0, 0.0, nrep=300, label='n=60 very sparse, null')
