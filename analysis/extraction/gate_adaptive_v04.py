"""Operating characteristics of the gate with internal ICC re-estimation (EXTRACTION-PLAN-v0.4 s10.7, design B-IP;
red-team audit 3, M1). Not a result about any paper; every input is the E0 model of gate_oc_v04.py.

Design B-IP: draw 60 gate records (3 strata x 20). On them compute the pooled ICC of the eight count metrics and
its Neyman 80 percent upper bound U_N (icc_check.py). Set n = the smallest n in {60, 72, 90, 105, 120} with
P(pass | all good) >= 0.85 at ICC U_N (grid of gate_oc_v04-log.txt section B, linear interpolation; 120 if none).
If n > 60, extract n - 60 more fresh records (same strata, same seeds continued), then apply the s10.4 rule once,
to all n records. The ICC decision never looks at whether a criterion passes. This script measures what that
costs in false passes: P(pass | all good) and P(pass | one quantity bad) of the whole procedure, and the
distribution of the final n.

Imports gate_oc_v04.py and icc_check.py from this directory by explicit file path (no sys.path change).
Run from the worktree root: python -u -E -P analysis/extraction/gate_adaptive_v04.py [--reps 400]
Seeds: 20263950 + scenario (offsets 950-979 of the simulation block 20263000-20263999; gate_oc_v04.py uses 0-932 and 990-999).
"""
import argparse
import importlib.util
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = load("gate_oc_v04")
I = load("icc_check")
SEED = 20263950
PER_MAX, PER_1 = 40, 20                 # records per stratum: maximum (n 120) and phase 1 (n 60)
ICC_METRICS = ("G4 F1_G", "G4 F1_K", "G4 M-val", "G3 K-attr", "G4 M-class", "G4 M-anchorG", "G4 M-sign", "G4 M-pool")


def gen(rng, levels, icc, nb_k=1.5):
    """Per-record data of every criterion for 3 x PER_MAX records (stratum h = records h*PER_MAX ...)."""
    n = 3 * PER_MAX
    D, matched, raw = {}, {}, {}
    for name in G.ORDER_G + [k for k in G.NAMES if k not in G.ORDER_G]:
        kind, size, _, bad, block = G.Q[name]
        p = levels[name]
        u = stats.norm.cdf(rng.standard_normal(n))
        if kind == "ratio":
            m = G.counts(rng, size, n, nb_k)
            x = rng.binomial(m, G.beta_from_u(u, p, icc))
            D[name], raw[name] = (x.astype(float), m.astype(float)), (x, m)
        elif kind == "f1":
            U = G.counts(rng, size, n, nb_k)
            both = rng.binomial(U, G.beta_from_u(u, p / (2 - p), icc))
            matched[name] = both
            D[name], raw[name] = (2.0 * both, (U + both).astype(float)), (both, U)
        elif kind in ("onG", "onK"):
            m = matched["G4 F1_G" if kind == "onG" else "G4 F1_K"]
            x = rng.binomial(m, G.beta_from_u(u, p, icc))
            D[name], raw[name] = (x.astype(float), m.astype(float)), (x, m)
        elif kind == "kappa":
            a = G.beta_from_u(u, np.sqrt(p), icc)[:, None]
            T = (rng.random((n, size, 1)) > G.QA_MARG.cumsum(1)[None]).sum(-1)

            def rate():
                e = (rng.random((n, size, 1)) > G.QA_MARG.cumsum(1)[None]).sum(-1)
                return np.where(rng.random((n, size)) < a, T, e)
            X, Y = rate(), rate()
            oh = np.zeros((n, size, 9), np.int16)
            np.put_along_axis(oh, (3 * X + Y)[..., None], 1, -1)
            D[name] = ("kappa", oh)
        elif kind == "count":
            D[name] = ("count", u < p)
    return D, raw


def sel(per):
    return np.concatenate([np.arange(h * PER_MAX, h * PER_MAX + per) for h in range(3)])


def evaluate(D, per, rng):
    """s10.4 rule on the first `per` records of each stratum; returns a boolean pass vector over G.NAMES."""
    S = sel(per)
    idx = np.concatenate([S[h * per:(h + 1) * per][rng.integers(0, per, (G.B, per))] for h in range(3)], 1)
    cmin = G.c_min(3 * per, G.Q["G5 anchors"][3])
    out = np.zeros(len(G.NAMES), bool)
    for j, name in enumerate(G.NAMES):
        line = G.THR.get(name, G.Q[name][3])
        d = D[name]
        if isinstance(d[0], str) and d[0] == "kappa":
            out[j] = np.quantile(G.wkappa(d[1][idx].sum(1)).mean(-1), G.LB_Q) >= line
        elif isinstance(d[0], str) and d[0] == "count":
            out[j] = d[1][S].sum() >= cmin
        else:
            num, den = d
            out[j] = np.quantile(num[idx].sum(1) / np.maximum(den[idx].sum(1), 1e-12), G.LB_Q) >= line
    return out


def run(levels, icc, reps, seed, grid, rn):
    rng = np.random.default_rng(seed)
    passed, ns = np.zeros(reps, bool), []
    for r in range(reps):
        D, raw = gen(rng, levels, icc)
        S1 = sel(PER_1)
        xs = [raw[k][0][S1] for k in ICC_METRICS]
        ms = [raw[k][1][S1] for k in ICC_METRICS]
        un, _ = I.upper80_neyman(xs, ms, rng, R=rn)
        n = I.n_required(un, grid) or 120
        ns.append(n)
        passed[r] = evaluate(D, n // 3, rng).all()
    return passed.mean(), np.array(ns)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=400)
    ap.add_argument("--rn", type=int, default=200, help="simulations per grid point for U_N (production: 1,000)")
    a = ap.parse_args()
    t0 = time.time()
    grid = I.read_grid(str(HERE / "gate_oc_v04-log.txt"))
    assert grid is not None, "run gate_oc_v04.py first"
    print(f"python {platform.python_version()}, numpy {np.__version__}; SEED {SEED}; reps {a.reps}; U_N with {a.rn} "
          f"simulations per grid point; grid ICC {[float(x) for x in grid[0]]} x n {grid[1]} from gate_oc_v04-log.txt")
    lv = G.levels_with
    print("\n== Design B-IP: P(pass | all good) and final n ==")
    print("  true ICC   P(pass)   n=60   n=72   n=90  n=105  n=120   mean n")
    for i, icc in enumerate((0.05, 0.10, 0.15, 0.20, 0.30)):
        p, ns = run(lv(), icc, a.reps, SEED + i, grid, a.rn)
        print(f"  {icc:.2f}       {p:.3f}    " + "  ".join(f"{np.mean(ns == n):.2f}" for n in (60, 72, 90, 105, 120))
              + f"   {ns.mean():.1f}")
    print("\n== Design B-IP: P(pass | one quantity bad, others good) ==")
    for i, (bad, icc) in enumerate([(b, c) for c in (0.10, 0.30) for b in
                                    ("G4 F1_G", "G4 M-anchorG", "G4 M-sign", "G4 M-class", "G1 accept EB")]):
        p, ns = run(lv(bad=bad), icc, a.reps, SEED + 20 + i, grid, a.rn)
        print(f"  {bad:<14} ICC {icc:.2f}: P(pass) {p:.3f}; mean n {ns.mean():.1f}")
    print(f"\nelapsed {time.time() - t0:.0f} s")


if __name__ == "__main__":
    sys.exit(main())
