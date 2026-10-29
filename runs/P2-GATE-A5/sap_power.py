"""SAP-GATE power inputs from probe 1 (CPU only).  python -I sap_power.py <path-to-items.jsonl>
Every output is an assumption-conditional calculation, not a result. Seed fixed."""
import json, sys, math
import numpy as np
from scipy import stats as ss
from scipy.optimize import brentq

rng = np.random.default_rng(20261028)
rows = [json.loads(l) for l in open(sys.argv[1])]
d = np.array([r['true']['bfull'] - r['mis']['bfull'] for r in rows])      # clean paired margin, image direction
n = len(d)
print('n', n, 'acc', (d > 0).mean(), 'n_wrong', int((d <= 0).sum()), 'n_ties', int((d == 0).sum()))
k = int((d > 0).sum())
z = 1.959964
ph = k / n; den = 1 + z * z / n
c = (ph + z * z / (2 * n)) / den; h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
print('wilson95', round(c - h, 4), round(c + h, 4))
bs = np.array([(d[rng.integers(0, n, n)] > 0).mean() for _ in range(10000)])
print('boot95', np.percentile(bs, [2.5, 97.5]))
print('mean', d.mean(), 'sd', d.std(ddof=1), 'skew', ss.skew(d), 'exkurt', ss.kurtosis(d), 'shapiro_p', ss.shapiro(d).pvalue)
print('quantiles 5,25,50,75,95', np.percentile(d, [5, 25, 50, 75, 95]))
sd = d.std(ddof=1)
for t in (0.1, 0.25, 0.5, 1.0):
    print('items with |d| <', t, 'sd:', int((np.abs(d) < t * sd).sum()))

# ---------- exact McNemar machinery ----------
def kcrit(nd, a):                       # largest c with 2*P(Bin(nd,.5)<=c) <= a ; -1 if none
    if nd == 0: return -1
    cs = np.arange(nd + 1)
    ok = 2 * ss.binom.cdf(cs, nd, 0.5) <= a
    return int(cs[ok].max()) if ok.any() else -1

_kc = {}
def KC(nd, a):
    key = (nd, a)
    if key not in _kc: _kc[key] = kcrit(nd, a)
    return _kc[key]

def power_given_nd(nd, theta, a):       # reject in the favourable direction, discordant count nd fixed
    kc = KC(nd, a)
    return 0.0 if kc < 0 else ss.binom.cdf(kc, nd, 1 - theta)   # c = nd - b ~ Bin(nd, 1-theta)

def power(nn, pi_d, theta, a):          # unconditional exact power, n items, discordance rate pi_d
    nds = np.arange(nn + 1)
    w = ss.binom.pmf(nds, nn, pi_d)
    return float(sum(w[i] * power_given_nd(int(i), theta, a) for i in nds if w[i] > 1e-12))

A = {'0.05': 0.05, '0.025': 0.025, '0.0167': 0.05 / 3}
print('\nTABLE A: smallest discordant count n_d with exact conditional power >= 0.8 (stays >= 0.8 for next 5 n_d)')
for th in (0.65, 0.70, 0.75, 0.80, 0.90):
    out = []
    for nm, a in A.items():
        for nd in range(5, 600):
            if all(power_given_nd(nd + j, th, a) >= 0.8 for j in range(6)):
                out.append((nm, nd)); break
    print('theta', th, out)

print('\nTABLE B: n=300, min theta (grid 0.005) with unconditional exact power >= 0.8; delta_acc = pi_d*(2theta-1)')
for nn in (300, 500):
    for nm in ('0.05', '0.0167'):
        for pid in (0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.30):
            th = next((t for t in np.arange(0.5, 1.0001, 0.005) if power(nn, pid, t, A[nm]) >= 0.8), None)
            print('n', nn, "alpha'", nm, 'pi_d', pid, 'theta_min', None if th is None else round(float(th), 3),
                  'delta_acc', None if th is None else round(pid * (2 * th - 1), 4),
                  'nd_expected', round(nn * pid, 1))

print('\nTABLE C: smallest n (step 5; power >= 0.8 at it and the next 3 grid points) for (pi_d, theta)')
for pid in (0.08, 0.10, 0.15, 0.20):
    for th in (0.65, 0.70, 0.75, 0.80):
        row = []
        for nm in ('0.05', '0.0167'):
            nfound = None
            for nn in range(50, 3001, 5):
                if all(power(nn + 5 * j, pid, th, A[nm]) >= 0.8 for j in range(4)):
                    nfound = nn; break
            row.append((nm, nfound))
        print('pi_d', pid, 'theta', th, row)

print('\nPOWER AT n=300 for a given (pi_d, theta)  [alpha 0.05, 0.0167]')
for pid, th in ((0.10, 0.75), (0.10, 0.70), (0.13, 0.75), (0.15, 0.70), (0.20, 0.65)):
    print(pid, th, round(power(300, pid, th, 0.05), 3), round(power(300, pid, th, 0.05 / 3), 3))
print('size check at theta=0.5, pi_d=0.10, n=300:', round(power(300, 0.10, 0.5, 0.05), 4), round(power(300, 0.10, 0.5, 0.05 / 3), 4))

# ---------- scenario model (ASSUMED): dilution/noise; corruption adds N(0, tau^2) to the item margin; gate removes fraction f ----------
print('\nSCENARIOS: margin_none = x + e1 + e2 ; margin_gate = x + e1 ; e1~N(0,tau^2 (1-f)), e2~N(0,tau^2 f); x = resampled probe-1 clean margins')
N = 400000
x = d[rng.integers(0, n, N)]
g1 = rng.standard_normal(N); g2 = rng.standard_normal(N)
res = []
for tau in (0.10, 0.20, 0.30, 0.40):
    for f in (0.3, 0.5, 0.7, 0.9):
        mn = x + tau * (math.sqrt(1 - f) * g1 + math.sqrt(f) * g2)
        mg = x + tau * math.sqrt(1 - f) * g1
        yn, yg = mn > 0, mg > 0
        pb = float(((yg) & (~yn)).mean()); pc = float(((~yg) & (yn)).mean())
        pid = pb + pc; th = pb / pid
        row = dict(tau=tau, f=f, acc_clean=float((x > 0).mean()), acc_none=float(yn.mean()), acc_gate=float(yg.mean()),
                   pi_d=pid, theta=th, delta=pb - pc,
                   pow300_a05=power(300, pid, th, 0.05), pow300_a0167=power(300, pid, th, 0.05 / 3), pow500_a0167=power(500, pid, th, 0.05 / 3))
        res.append(row)
        print({k_: (round(v, 4) if isinstance(v, float) else v) for k_, v in row.items()})
json.dump(res, open(sys.argv[1] + '.scen.json' if False else 'scenarios.json', 'w'), indent=1)

# ---------- headroom rule: P(pass 2-SE rule) vs true standardised drop ----------
print('\nHEADROOM RULE (one condition, n=100, t-test form mean/(sd/sqrt(n)) >= 2): P(pass) vs true d/sigma_d')
for e in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
    p = ss.nct.sf(2.0, 99, e * 10) if e > 0 else ss.t.sf(2.0, 99)
    print('d/sigma', e, round(float(p), 3))

# ---------- z-score secondary: MDE (paired t, noncentral-t exact) ----------
print('\nZ-SCORE MDE in units of sigma_d (power 0.8, two-sided paired t)')
for nn in (100, 300, 500):
    for nm in ('0.05', '0.0167'):
        a = A[nm]
        f_ = lambda dlt: ss.nct.sf(ss.t.ppf(1 - a / 2, nn - 1), nn - 1, dlt * math.sqrt(nn)) - 0.8
        print('n', nn, "alpha'", nm, round(brentq(f_, 0.01, 1.0), 4))

# ---------- AUROC falsifier precision ----------
print('\nDETECTION: MDE of mean paired per-item AUROC difference, n=200 items (normal approx, power 0.8)')
for a_nm, a in (('0.05', 0.05), ('0.025', 0.025)):
    for sdd in (0.05, 0.10, 0.15, 0.20):
        print("alpha'", a_nm, 'sd_diff', sdd, round((ss.norm.ppf(1 - a / 2) + ss.norm.ppf(0.8)) * sdd / math.sqrt(200), 4))
