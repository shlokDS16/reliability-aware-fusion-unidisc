"""Stage A estimate of the intra-record correlation (ICC) the gate depends on (EXTRACTION-PLAN-v0.4 s10.7; red-team
audit 3, M1). Reference implementation of the estimator agreement.py must reproduce, a self-test, and its
sampling behaviour with 7 and 12 records under the gate model of gate_oc_v04.py. Not a result about any paper.

Estimator (per metric, records with m_r > 0 only): x_r agreements out of m_r units in record r (for an F1 metric:
x_r = matched units, m_r = union units, so the ICC is on the Jaccard scale the gate simulation uses);
  N = sum m_r, k = number of records, p_r = x_r / m_r, pbar = sum x_r / N,
  MSB = sum m_r (p_r - pbar)^2 / (k - 1),  MSW = sum x_r (1 - p_r) / (N - k),
  m0 = (N - sum m_r^2 / N) / (k - 1),     ICC = (MSB - MSW) / (MSB + (m0 - 1) MSW), truncated to [0, 0.95]
(the one-way ANOVA estimator for clustered binary data). A metric enters the pooled value if at least 5 records
have m_r > 0 and N > k. Pooled ICC = mean of the per-metric values.

Upper 80 percent bound used by the gate rule (U_N, a Neyman bound by parametric simulation): for each theta on the
grid 0.02, 0.04, ..., 0.60, simulate the pooled estimator 1,000 times with the observed unit counts m_r of every
metric and its observed mean pbar_m (clipped to [0.01, 0.995]), x_r ~ Bin(m_r, Beta(pbar_m, theta)) (numpy
Generator.beta with a = pbar_m (1/theta - 1), b = (1 - pbar_m)(1/theta - 1)); U_N = the
largest theta with P_theta(pooled <= observed pooled) >= 0.20 (0.60 if every theta qualifies; 0.02 if none).
Seed 20264900 in Stage A. The record-level percentile bootstrap bound (U_B: 80th percentile of the pooled value
over record resamples) is printed for comparison only: the sampling table below shows that it under-covers.

Run from the worktree root: python -u -E -P analysis/extraction/icc_check.py [--quick]
Seeds: simulation 20264000 + s (plan v0.4 seed table).
"""
import argparse
import platform
import sys
import time
import warnings

import numpy as np
from scipy import special

SEED = 20264000
warnings.simplefilter("ignore", RuntimeWarning)   # nanmean over all-nan bootstrap draws


def icc_anova(x, m):
    """x, m: arrays (..., k). Returns ICC per leading index (nan if undefined). Records with m = 0 are dropped
    by giving them zero weight (they add nothing to N, MSB, MSW; k counts only records with m > 0)."""
    x = np.asarray(x, float)
    m = np.asarray(m, float)
    use = m > 0
    k = use.sum(-1)
    N = m.sum(-1)
    p = np.where(use, x / np.where(use, m, 1), 0.0)
    pbar = x.sum(-1) / np.maximum(N, 1e-12)
    msb = (m * (p - pbar[..., None]) ** 2).sum(-1) / np.maximum(k - 1, 1)
    msw = (x * (1 - p)).sum(-1) / np.maximum(N - k, 1e-12)
    m0 = (N - (m ** 2).sum(-1) / np.maximum(N, 1e-12)) / np.maximum(k - 1, 1)
    den = msb + (m0 - 1) * msw
    r = np.where(den > 0, (msb - msw) / np.where(den > 0, den, 1), 0.0)
    ok = (k >= 5) & (N > k)
    return np.where(ok, np.clip(r, 0.0, 0.95), np.nan)


def pooled(est):
    """est: (n_metrics, ...) per-metric ICC; mean over defined metrics."""
    return np.nanmean(est, axis=0)


def upper80(xs, ms, rng, B=2000):
    """xs, ms: lists of (k,) arrays per metric. Record bootstrap, same indices for every metric."""
    k = len(ms[0])
    idx = rng.integers(0, k, (B, k))
    est = np.stack([icc_anova(x[idx], m[idx]) for x, m in zip(xs, ms)])
    return float(np.quantile(pooled(est), 0.80))


GRID = np.round(np.arange(0.02, 0.601, 0.02), 2)


def upper80_neyman(xs, ms, rng, R=1000, grid=GRID):
    """Neyman 80 percent upper bound for the pooled ICC, conditional on the observed unit counts."""
    obs = float(pooled(np.array([icc_anova(x, m) for x, m in zip(xs, ms)])))
    pb = [float(np.clip(x.sum() / max(m.sum(), 1), 0.01, 0.995)) for x, m in zip(xs, ms)]
    best = None
    for th in grid:
        a = 1.0 / th - 1.0
        est = np.stack([icc_anova(rng.binomial(np.broadcast_to(m, (R, len(m))),
                                               rng.beta(p * a, (1 - p) * a, (R, len(m)))),
                                  np.broadcast_to(m, (R, len(m))))
                        for p, m in zip(pb, ms)])
        if np.mean(pooled(est) <= obs) >= 0.20:
            best = th
    return float(grid[0] if best is None else best), obs


# ---- gate model (gate_oc_v04.py) for the metrics with per-record counts --------------------------------
def beta(rng, p, icc, k):
    a = 1.0 / icc - 1.0
    return special.betaincinv(p * a, (1 - p) * a, rng.random(k))


def nb(rng, lam, k, shape=1.5):
    return rng.negative_binomial(shape, shape / (shape + lam), k)


def draw_records(rng, k, icc):
    """Eight gated metrics with per-record counts: F1_G, F1_K (Jaccard scale), M-val, K-attr, M-class,
    M-anchorG (on matched groups), M-sign, M-pool (on matched K units). Good levels of plan s10.4."""
    xs, ms, names = [], [], []
    ug = nb(rng, 3, k)
    bg = rng.binomial(ug, beta(rng, 0.75 / 1.25, icc, k))
    uk = nb(rng, 8, k)
    bk = rng.binomial(uk, beta(rng, 0.75 / 1.25, icc, k))
    for name, (x, m) in (("F1_G", (bg, ug)), ("F1_K", (bk, uk))):
        xs.append(x), ms.append(m), names.append(name)
    mv = nb(rng, 15, k)
    ma = nb(rng, 18, k)
    for name, p, m in (("M-val", 0.95, mv), ("K-attr", 0.85, ma), ("M-class", 0.85, bg), ("M-anchorG", 0.85, bg),
                       ("M-sign", 0.97, bk), ("M-pool", 0.85, bk)):
        xs.append(rng.binomial(m, beta(rng, p, icc, k))), ms.append(m), names.append(name)
    return xs, ms, names


def read_grid(path="analysis/extraction/gate_oc_v04-log.txt"):
    """Section B of the gate log: P(pass | all good) by (ICC, n). Returns (iccs, ns, P) or None."""
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError:
        return None
    i = next(j for j, l in enumerate(lines) if l.startswith("== B."))
    ns = [int(t.split("=")[1]) for t in lines[i + 1].split()[1:]]
    iccs, P = [], []
    for l in lines[i + 2:]:
        t = l.split()
        if len(t) != len(ns) + 1:
            break
        iccs.append(float(t[0])), P.append([float(v) for v in t[1:]])
    return np.array(iccs), ns, np.array(P)


def n_required(u, grid, target=0.85):
    """Smallest grid n with P(pass | all good) >= target at ICC u (linear interpolation in ICC); None if none."""
    iccs, ns, P = grid
    for j, n in enumerate(ns):
        if np.interp(u, iccs, P[:, j]) >= target:
            return n
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    print(f"python {platform.python_version()}, numpy {np.__version__}; SEED {SEED}")

    # self-test 1: hand example (two records, equal rates -> ICC 0 after truncation; k < 5 -> nan)
    assert np.isnan(icc_anova(np.array([3, 3]), np.array([4, 4]))), "k < 5 must give nan"
    t = icc_anova(np.array([4, 4, 4, 4, 4, 4]), np.array([5, 5, 5, 5, 5, 5]))
    assert abs(t) < 1e-12, t
    t = icc_anova(np.array([5, 0, 5, 0, 5, 0]), np.array([5, 5, 5, 5, 5, 5]))
    assert t > 0.9, t
    print("self-test 1 (hand cases: k < 5 nan; equal rates 0; all-or-nothing records > 0.9): ok")
    # self-test 2: recovery with many records
    rng = np.random.default_rng(SEED)
    print("self-test 2 (recovery, k = 4,000 records, NB(1.5) unit counts):")
    for p, lam, icc in ((0.60, 3, 0.10), (0.60, 8, 0.30), (0.95, 15, 0.10), (0.85, 18, 0.20)):
        m = nb(rng, lam, 4000)
        x = rng.binomial(m, beta(rng, p, icc, 4000))
        e = float(icc_anova(x, m))
        print(f"  mean {p:.2f}, units {lam:2d}, true ICC {icc:.2f}: estimate {e:.3f}")
        assert abs(e - icc) < 0.05, (p, lam, icc, e)
    print("  ok (|estimate - true| < 0.05 in every case)")

    R = 100 if a.quick else 300
    Bb, Rn = 400, (200 if a.quick else 400)
    print(f"\nSampling behaviour under the gate model ({R} replicates per cell; record bootstrap {Bb} for U_B; {Rn} simulations per grid point for U_N; U_N in Stage A uses 1,000):")
    print("  k   true  | F1_G est. median [10%, 90%] | M-val est. median [10%, 90%] | pooled median [10%, 90%] | "
          "U_B median, coverage | U_N median [90%], coverage")
    rows = []
    grid = read_grid()
    nreq = {}
    for ci, (k, icc) in enumerate([(kk, ii) for kk in (7, 12) for ii in (0.05, 0.10, 0.20, 0.30)]):
        rng = np.random.default_rng(SEED + 10 + ci)
        fg, mv, po, up, un = [], [], [], [], []
        for _ in range(R):
            xs, ms, names = draw_records(rng, k, icc)
            est = np.array([icc_anova(x, m) for x, m in zip(xs, ms)])
            fg.append(est[0]), mv.append(est[2]), po.append(np.nanmean(est))
            up.append(upper80(xs, ms, rng, Bb))
            un.append(upper80_neyman(xs, ms, rng, Rn)[0])
        fg, mv, po, up, un = map(np.array, (fg, mv, po, up, un))

        def q(v):
            v = v[~np.isnan(v)]
            return f"{np.median(v):.2f} [{np.quantile(v, .1):.2f}, {np.quantile(v, .9):.2f}]" if len(v) else "n/a"
        cov, covn = float(np.mean(up >= icc)), float(np.mean(un >= icc))
        rows.append((k, icc, np.median(un), np.quantile(un, 0.9), covn))
        if grid is not None:
            nreq[(k, icc)] = [n_required(u, grid) for u in un]
        print(f"  {k:2d}  {icc:.2f}  | {q(fg):<27} | {q(mv):<28} | {q(po):<24} | {np.median(up):.2f}, {cov:.2f}"
              f"        | {np.median(un):.2f} [{np.quantile(un, .9):.2f}], {covn:.2f}")
    if grid is not None:
        ns = grid[1]
        print("\nGate size the rule of plan s10.7 would set from U_N (grid of gate_oc_v04-log.txt section B, linear "
              "interpolation in ICC; share of replicates):")
        print("  k   true  " + "".join(f"n={n:<6}" for n in ns) + "none<=120")
        for (k, icc), v in nreq.items():
            print(f"  {k:2d}  {icc:.2f}  " + "".join(f"{np.mean([x == n for x in v]):.2f}    " for n in ns)
                  + f"{np.mean([x is None for x in v]):.2f}")
    print("\nReading: with 7 or 12 records the per-metric estimate is very imprecise; the pooled value over eight"
          " metrics is less so. Coverage = P(true ICC <= bound): U_B (percentile bootstrap) under-covers once the"
          " true ICC is 0.10 or more; U_N (Neyman) covers in at least about 0.80 of replicates and is the bound the"
          " gate rule uses.")
    print(f"\nelapsed {time.time() - t0:.0f} s")


if __name__ == "__main__":
    sys.exit(main())
