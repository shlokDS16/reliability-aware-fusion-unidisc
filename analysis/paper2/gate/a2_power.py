"""SAP-GATE Addendum A2 (debate decisions): assumption-conditional power tables. CPU only, no data files read.
Run: python a2_power.py
Every number printed is a calculation under stated assumptions (pi_d = discordance rate, theta = share of
discordant items favouring the first arm), NOT a result. Same exact-McNemar machinery as SAP Appendix A.
"""
import math
import numpy as np
from scipy import stats as ss


def kcrit(nd, a):  # largest c with 2*P(Bin(nd,.5)<=c) <= a ; -1 if none
    if nd == 0:
        return -1
    cs = np.arange(nd + 1)
    ok = 2 * ss.binom.cdf(cs, nd, 0.5) <= a
    return int(cs[ok].max()) if ok.any() else -1


_kc = {}


def KC(nd, a):
    key = (nd, a)
    if key not in _kc:
        _kc[key] = kcrit(nd, a)
    return _kc[key]


def power_given_nd(nd, theta, a):  # favourable-direction rejection, discordant count fixed
    kc = KC(nd, a)
    return 0.0 if kc < 0 else float(ss.binom.cdf(kc, nd, 1 - theta))


def power(nn, pi_d, theta, a):
    nds = np.arange(nn + 1)
    w = ss.binom.pmf(nds, nn, pi_d)
    return float(sum(w[i] * power_given_nd(int(i), theta, a) for i in nds if w[i] > 1e-12))


AL = {'0.05': 0.05, '0.025': 0.025, '0.0167': 0.05 / 3, '0.0125': 0.05 / 4}


def theta_min(nn, pi_d, a):
    t = next((t for t in np.arange(0.5, 1.0001, 0.005) if power(nn, pi_d, t, a) >= 0.8), None)
    return None if t is None else float(t)


if __name__ == '__main__':
    print('A) MINIMUM theta and net gain Delta=pi_d*(2theta-1) for power 0.8 (exact, favourable tail)')
    for nn in (100, 120, 150, 300):
        for nm in ('0.05', '0.025', '0.0167'):
            row = []
            for pid in (0.05, 0.10, 0.15, 0.20, 0.30):
                t = theta_min(nn, pid, AL[nm])
                row.append((pid, None if t is None else round(t, 3), None if t is None else round(pid * (2 * t - 1), 3)))
            print('n', nn, "alpha'", nm, row)

    print('\nB) POWER at selected (pi_d, theta)')
    for nn, nm in ((300, '0.025'), (300, '0.05'), (150, '0.05'), (150, '0.025'), (150, '0.0167'), (120, '0.05')):
        print('n', nn, "alpha'", nm, [(p, t, round(power(nn, p, t, AL[nm]), 3)) for p, t in
                                      ((0.10, 0.75), (0.10, 0.80), (0.15, 0.75), (0.20, 0.70), (0.20, 0.80))])

    print('\nC) E-pred: exact one-sided binomial p (H0: agreement prob 0.5) when all K cells agree, and K-1 of K')
    for K in range(3, 10):
        print('K', K, 'all agree p=', round(float(ss.binom.sf(K - 1, K, 0.5)), 4),
              ' K-1 agree p=', round(float(ss.binom.sf(K - 2, K, 0.5)), 4))

    print('\nD) chance of at least one family-level rejection if every family were null and independent, F families at 0.05')
    for F in (1, 3, 5, 8, 10, 12):
        print('F', F, round(1 - 0.95 ** F, 3))

    print('\nE) Size check (theta=0.5): one-tail rejection probability, n=150, pi_d=0.10')
    for nm in ('0.05', '0.025', '0.0167'):
        print("alpha'", nm, round(power(150, 0.10, 0.5, AL[nm]), 4))
