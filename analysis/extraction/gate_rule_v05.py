"""Decision function of gate design B-IP, extraction form v0.5 (EXTRACTION-PLAN-v0.5 s10.7; red-team audit 4, MA1
and MA3). Reference implementation that agreement.py must import or reproduce exactly; gate_bip_v05.py simulates
the whole procedure with it. Not a result about any paper.

What it fixes in advance (all read from the declared config, default analysis/extraction/gate-config-v05.json,
and the grid file analysis/extraction/bip-grid-v2.json; both hashed in the B2 gate row):
  1. Per-metric Neyman 80 percent upper bound U_m of the intra-record correlation (ICC) for every ICC metric
     (the ratio, F1, matched-group and sign criteria, and the four K-attr fields), computed on the phase-1
     records only: obs = icc_check.icc_anova(x, m) (the v0.4 estimator, imported unchanged); for theta on the
     grid 0.02-0.60, simulate R = 1,000 estimates with the observed unit counts m_r and mean pbar
     (clipped to [0.01, 0.995]); U_m = the largest grid theta with P_theta(estimate <= obs) >= 0.20, found by
     bisection over the grid (about 5 evaluations instead of 30). An undefined estimate (fewer than 5 records
     with units, or N <= k) gives the grid maximum, 0.60.
  2. theta_c for each gated criterion = max of U_m over the metrics its 'icc_from' list names (K-attr: its four
     fields; QA kappa: the seven L/Q/H criteria; G5: none, it does not depend on the ICC in the model).
  3. Product rule: P_hat(n) = prod_c P_c(theta_c, n), P_c = the criterion's marginal pass probability at its
     good level in the grid file (simulated with the ICC common to all metrics; linear interpolation in
     theta, theta clipped to [0.02, 0.60]). n = the smallest grid n <= n_cap with P_hat(n) >= 0.85; if none,
     n = n_cap and the step-6 statement is due.
  For comparison only: the max rule (n from the common-ICC joint grid at the largest U_m of the eight count
  metrics) and the v0.4 pooled rule (n from the same grid at the Neyman bound of the mean ICC of the eight
  count metrics, found by bisection).

Run from the worktree root: python -u -E -P analysis/extraction/gate_rule_v05.py   (self-tests and the coverage
table of the per-metric bound; log gate_rule_v05-log.txt). Seeds 20265900-20265999 (plan v0.5 s2.10).
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
warnings.simplefilter("ignore", RuntimeWarning)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


I = _load("icc_check")          # icc_anova: the v0.4 estimator, unchanged
SEED = 20265900


def model_sha(cfg):
    """Hash of everything the grid depends on (criteria, levels, lines, unit model, n grid). The grid file stores
    it; gate_bip_v05.py and agreement.py refuse a grid whose model hash differs from the config's."""
    m = {"criteria": cfg["criteria"], "units": {k: v for k, v in cfg["units"].items() if k != "note"},
         "kattr_fields": cfg["kattr_fields"], "n_grid": cfg["design"]["n_grid"]}
    return hashlib.sha256(json.dumps(m, sort_keys=True).encode("utf-8")).hexdigest()


def icc_metrics(cfg):
    out = []
    for k, q in cfg["criteria"].items():
        if q["kind"] in ("ratio", "f1", "onG", "onS"):
            out.append(k)
        elif q["kind"] == "kattr":
            out += [f"{k}:{f}" for f in cfg["kattr_fields"]]
    return out


def largest_true(n, pred):
    """Largest index i in 0..n-1 with pred(i) true, assuming pred is true then false; -1 if pred(0) is false.
    Bisection: about log2(n) + 1 evaluations of pred, in a fixed order."""
    lo, hi = -1, n
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if pred(mid):
            lo = mid
        else:
            hi = mid
    return lo


def _sim_est(rng, p, m, th, R):
    a = 1.0 / th - 1.0
    mm = np.broadcast_to(np.rint(m).astype(np.int64), (R, len(m)))
    return I.icc_anova(rng.binomial(mm, rng.beta(p * a, (1 - p) * a, (R, len(m)))), mm)


def neyman_upper(x, m, rng, R=1000, grid=None, conf=0.80, scan=False):
    """Per-metric Neyman upper bound. Returns (U, observed ICC). scan=True: full scan of the grid (self-test)."""
    grid = I.GRID if grid is None else np.asarray(grid)
    x, m = np.asarray(x, float), np.asarray(m, float)
    use = m > 0
    x, m = x[use], m[use]
    obs = float(I.icc_anova(x, m)) if len(m) else float("nan")
    if np.isnan(obs):
        return float(grid[-1]), obs
    p = float(np.clip(x.sum() / m.sum(), 0.01, 0.995))

    def ok(i):
        return np.mean(_sim_est(rng, p, m, grid[i], R) <= obs) >= 1 - conf
    if scan:
        good = [i for i in range(len(grid)) if ok(i)]
        i = good[-1] if good else -1
    else:
        i = largest_true(len(grid), ok)
    return float(grid[0] if i < 0 else grid[i]), obs


def neyman_upper_pooled(xs, ms, rng, R=1000, grid=None, conf=0.80):
    """v0.4 statistic (mean of the per-metric ICCs), bound found by bisection. For comparison only."""
    grid = I.GRID if grid is None else np.asarray(grid)
    obs = float(np.nanmean([I.icc_anova(np.asarray(x, float), np.asarray(m, float)) for x, m in zip(xs, ms)]))
    pb = [float(np.clip(np.sum(x) / max(np.sum(m), 1), 0.01, 0.995)) for x, m in zip(xs, ms)]

    def ok(i):
        est = np.stack([_sim_est(rng, p, np.asarray(m, float), grid[i], R) for p, m in zip(pb, ms)])
        return np.mean(np.nanmean(est, 0) <= obs) >= 1 - conf
    i = largest_true(len(grid), ok)
    return float(grid[0] if i < 0 else grid[i]), obs


def phase1_bounds(xm, cfg, rng):
    """xm: {icc metric: (x, m)} on the phase-1 records. Bounds in the fixed icc_metrics order (one Generator)."""
    b = cfg["bound"]
    return {k: neyman_upper(*xm[k], rng, R=b["R"], grid=b["theta_grid"], conf=b["conf"])[0] for k in icc_metrics(cfg)}


def theta_by_criterion(U, cfg, grid):
    out = {}
    for k, q in cfg["criteria"].items():
        if q.get("report_only"):
            continue
        out[k] = max((U[m] for m in q["icc_from"]), default=float(grid["theta"][0]))
    return out


def _interp(th, grid, col):
    t = np.asarray(grid["theta"], float)
    return float(np.interp(min(max(th, t[0]), t[-1]), t, col))


def n_product(theta, cfg, grid):
    """Returns (n, {n: P_hat(n)}, step6). step6 is True when no grid n <= n_cap reaches the target."""
    ns, cap, target = grid["n"], cfg["design"]["n_cap"], cfg["design"]["target"]
    P = {}
    for j, n in enumerate(ns):
        P[n] = float(np.prod([_interp(th, grid, [row[j] for row in grid["marginal"][c]]) for c, th in theta.items()]))
    for n in ns:
        if n <= cap and P[n] >= target:
            return n, P, False
    return cap, P, True


def n_common(u, cfg, grid):
    """Smallest grid n <= n_cap whose common-ICC joint P at ICC u reaches the target; n_cap if none."""
    ns, cap, target = grid["n"], cfg["design"]["n_cap"], cfg["design"]["target"]
    for j, n in enumerate(ns):
        if n <= cap and _interp(u, grid, [row[j] for row in grid["joint"]]) >= target:
            return n, False
    return cap, True


def n_max_rule(U, cfg, grid):
    vals = []
    for k in cfg["count_metrics_v04_pooled_rule"]:
        if not cfg["criteria"][k].get("report_only"):
            vals += [U[m] for m in cfg["criteria"][k]["icc_from"]]
    return n_common(max(vals), cfg, grid)[0], max(vals)


# ---- self-tests and coverage -------------------------------------------------------------------------------
def _nb(rng, lam, k, shape=1.5):
    return rng.negative_binomial(shape, shape / (shape + lam), k)


def _records(rng, kind, p, th, k):
    """Per-record (x, m) for one metric under the gate model of gate_oc_v05.py (record effect Beta(p, th))."""
    if kind == "sign":            # (matched group, metric) pairs
        g = rng.binomial(_nb(rng, 3, k), 0.6)
        kk = rng.binomial(_nb(rng, 8, k), 0.6)
        c = np.where(kk > 0, np.maximum(g, 1), 0)
        m = np.minimum(kk, c + rng.poisson(0.6 * c))
    elif kind == "group":         # matched groups (M-anchorG, M-pool, M-class)
        m = rng.binomial(_nb(rng, 3, k), 0.6)
    elif kind == "f1g":           # F1_G on the Jaccard scale: union units
        m = _nb(rng, 3, k)
    else:                         # M-val
        m = _nb(rng, 15, k)
    a = 1.0 / th - 1.0
    return rng.binomial(m, rng.beta(p * a, (1 - p) * a, k)), m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    a = ap.parse_args()
    t0 = time.time()
    print(f"python {platform.python_version()}, numpy {np.__version__}; SEED {SEED}")
    # 1. search logic on deterministic predicates
    for n, cut in ((30, -1), (30, 0), (30, 13), (30, 29), (1, 0), (2, 1)):
        assert largest_true(n, lambda i: i <= cut) == cut, (n, cut)
    print("self-test 1 (bisection returns the last true index; -1 when none): ok")
    # 2. product rule on a hand grid
    g = {"theta": [0.05, 0.10, 0.20], "n": [60, 90, 120],
         "marginal": {"A": [[0.99, 1, 1], [0.95, 0.99, 1], [0.80, 0.93, 0.97]],
                      "B": [[0.99, 1, 1], [0.90, 0.97, 0.99], [0.70, 0.88, 0.95]]},
         "joint": [[0.98, 1, 1], [0.855, 0.96, 0.99], [0.56, 0.82, 0.92]]}
    cfg = {"design": {"n_cap": 120, "target": 0.85},
           "criteria": {"A": {"icc_from": ["A"]}, "B": {"icc_from": ["B"]}}}
    n, P, f = n_product({"A": 0.10, "B": 0.10}, cfg, g)
    assert (n, f) == (60, False) and abs(P[60] - 0.855) < 1e-12, (n, P)
    n, P, f = n_product({"A": 0.20, "B": 0.10}, cfg, g)       # 0.80 * 0.90 at 60; 0.93 * 0.97 at 90
    assert (n, f) == (90, False), (n, P)
    n, P, f = n_product({"A": 0.20, "B": 0.20}, cfg, g)       # 0.97 * 0.95 = 0.9215 at 120
    assert (n, f) == (120, False), (n, P)
    n, P, f = n_product({"A": 0.20, "B": 0.20}, {"design": {"n_cap": 90, "target": 0.85}, "criteria": cfg["criteria"]}, g)
    assert (n, f) == (90, True), (n, P)                       # cap 90 (MA4): no n reaches 0.85 -> n_cap, step 6
    n, P, f = n_product({"A": 0.15, "B": 0.02}, cfg, g)       # interpolation; theta below grid clipped to 0.05
    assert n == 60 and abs(P[60] - 0.875 * 0.99) < 1e-12, (n, P)
    assert n_common(0.15, cfg, g) == (90, False) and n_common(0.10, cfg, g) == (60, False)
    print("self-test 2 (product rule, interpolation, clipping, n_cap and step-6 flag on a hand grid): ok")
    # 3. bisection against the full scan on random data (both are Monte Carlo; they may differ by MC noise only)
    rng = np.random.default_rng(SEED)
    diffs = []
    for i in range(24):
        kind = ("sign", "group", "f1g", "mval")[i % 4]
        p = {"sign": 0.97, "group": 0.85, "f1g": 0.60, "mval": 0.95}[kind]
        th = (0.05, 0.15, 0.30, 0.50)[(i // 4) % 4]
        x, m = _records(rng, kind, p, th, 60)
        ub = neyman_upper(x, m, np.random.default_rng(SEED + 1 + i), R=1000)[0]
        us = neyman_upper(x, m, np.random.default_rng(SEED + 1 + i), R=1000, scan=True)[0]
        diffs.append(ub - us)
    diffs = np.round(diffs, 2)
    print(f"self-test 3 (bisection vs full scan, 24 data sets, R 1,000): equal in {np.mean(diffs == 0):.2f}; "
          f"differences {sorted(set(diffs.tolist()))}")
    assert np.max(np.abs(diffs)) <= 0.06
    # 4. coverage of the per-metric bound with 60 records
    print(f"\nCoverage of the per-metric Neyman bound, 60 phase-1 records, R 1,000, {a.reps} replicates per cell "
          "(coverage = P(true ICC <= U)):")
    print("  metric (good level, units)                  true ICC   estimate median   U median [10%, 90%]   coverage")
    cases = [("M-sign (0.97, sign decisions)", "sign", 0.97), ("M-anchorG / M-pool (0.85, matched groups)", "group", 0.85),
             ("F1_G (0.75, Jaccard 0.60, union groups)", "f1g", 0.60), ("M-val (0.95, NB 15 units)", "mval", 0.95)]
    for ci, (lab, kind, p) in enumerate(cases):
        for ti, th in enumerate((0.10, 0.30, 0.50)):
            r = np.random.default_rng(SEED + 100 + 10 * ci + ti)
            us, es = [], []
            for _ in range(a.reps):
                x, m = _records(r, kind, p, th, 60)
                u, e = neyman_upper(x, m, r, R=1000)
                us.append(u), es.append(e)
            us, es = np.array(us), np.array(es)
            print(f"  {lab:<44} {th:.2f}       {np.nanmedian(es):.2f}              {np.median(us):.2f} "
                  f"[{np.quantile(us, .1):.2f}, {np.quantile(us, .9):.2f}]     {np.mean(us >= th - 1e-9):.2f}")
    print(f"\nelapsed {time.time() - t0:.0f} s")


if __name__ == "__main__":
    sys.exit(main())
