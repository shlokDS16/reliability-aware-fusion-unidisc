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

if __name__ == '__main__':
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
