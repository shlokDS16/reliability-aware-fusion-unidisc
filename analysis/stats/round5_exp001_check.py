"""Statistician check of EXP-001 v0.5 (composition-standardised H-A1 pair). No model data; simulation only.

Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python analysis/stats/round5_exp001_check.py > analysis/stats/round5_exp001_check.log
All parameters are [A] illustrations. Nothing printed is an experimental result.
Model (T->I, one source per probe, 4 centre probes per trajectory: 2 early, 2 late): the source's stratum is drawn from an
early or a late composition; value = level_s x (R if early) x trajectory effect x noise; a late probe has a source with
probability p_late, independently of the values (no availability selection, so power is isolated from bias).
"""
import numpy as np

rng = np.random.default_rng(20261018)
LEVEL = np.array([2.0, 1.0, 0.5])          # noun, other content, function [A]
COMP_E = np.array([0.2, 0.3, 0.5])         # early source composition [A]
COMP_L = np.array([0.5, 0.4, 0.1])         # late source composition [A]


def lognorm(cv, size):
    s2 = np.log(1 + cv**2)
    return np.exp(rng.normal(-s2 / 2, np.sqrt(s2), size))


def simulate(n, R, p_late):
    traj = lognorm(0.5, n)[:, None]
    strat = np.empty((n, 4), int)
    strat[:, :2] = rng.choice(3, (n, 2), p=COMP_E)
    strat[:, 2:] = rng.choice(3, (n, 2), p=COMP_L)
    has = np.ones((n, 4), bool)
    has[:, 2:] = rng.random((n, 2)) < p_late
    val = LEVEL[strat] * traj * lognorm(0.6, (n, 4))
    val[:, :2] *= R
    return val, strat, has


def std_ratio(val, strat, has, w, rows):
    v, s, h = val[rows], strat[rows], has[rows]
    num = den = 0.0
    for k in range(3):
        e = (s[:, :2] == k) & h[:, :2]
        l = (s[:, 2:] == k) & h[:, 2:]
        if e.sum() == 0 or l.sum() == 0:
            return np.nan
        num += w[k] * v[:, :2][e].mean()
        den += w[k] * v[:, 2:][l].mean()
    return num / den


def raw_ratio(val, has, rows):
    v, h = val[rows], has[rows]
    return v[:, :2][h[:, :2]].mean() / v[:, 2:][h[:, 2:]].mean()


def run(n=256, R=1.75, p_late=1.0, reps=300, B=600):
    hits = dict(raw=0, std_pool=0, std_cc=0, pair=0, cc_nan=0)
    for _ in range(reps):
        val, strat, has = simulate(n, R, p_late)
        w = np.array([((strat == k) & has).sum() for k in range(3)], float)
        w /= w.sum()                                   # fixed full-sample weights, held fixed in replicates
        cc = np.where(has.all(1))[0]
        bs_raw, bs_pool, bs_cc = [], [], []
        for _b in range(B):
            idx = rng.integers(0, n, n)
            bs_raw.append(raw_ratio(val, has, idx))
            bs_pool.append(std_ratio(val, strat, has, w, idx))
            idc = cc[rng.integers(0, len(cc), len(cc))]
            bs_cc.append(std_ratio(val, strat, has, w, idc))
        lo = lambda x: np.nanquantile(np.array(x), 0.025)
        a, b, c = lo(bs_raw) >= 1.5, lo(bs_pool) >= 1.5, lo(bs_cc) >= 1.5
        hits["raw"] += a
        hits["std_pool"] += b
        hits["std_cc"] += c
        hits["pair"] += b and c
        hits["cc_nan"] += np.isnan(np.array(bs_cc)).mean()
    return {k: v / reps for k, v in hits.items()}


print("P(lower 95% >= 1.5), n = 256, true within-stratum ratio R; raw ratio confounded by composition by design")
for R in (1.75, 2.0, 1.5):
    for p_late in (1.0, 0.8, 0.5):
        o = run(R=R, p_late=p_late)
        print(f"R={R} late availability {p_late}: raw {o['raw']:.3f} | std pooled {o['std_pool']:.3f} | "
              f"std complete-case {o['std_cc']:.3f} | IUT pair {o['pair']:.3f} | share of replicates with an empty stratum {o['cc_nan']:.4f}")
