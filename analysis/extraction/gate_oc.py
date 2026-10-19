"""Joint operating characteristics of the extraction gate, form v0.3 (EXTRACTION-PLAN-v0.3 s10).

Simulates ALL hard gate criteria of s10.4 together, with record-level correlation inside each metric
(Beta heterogeneity, intra-record correlation ICC) and across metrics (Gaussian copula on the record
effects, weight OMEGA), the stratified design (three equal strata) and the stratified cluster
bootstrap the gate uses. Prints, for a candidate gate size n, P(pass) when every quantity is at its
GOOD level, when exactly one quantity is at its BAD level (all others good), and when all are bad;
then a search over n and a sensitivity table. Not a result about any paper; every input below is an
assumption stated in the plan (s10.6).

Run from the worktree root:  python -I analysis/extraction/gate_oc.py [--quick]
Seed: numpy default_rng(SEED + scenario index), SEED = 20262000 (plan seed table s2.10).
"""
import argparse
import platform
import sys
import time

import numpy as np
from scipy import special, stats

SEED = 20262000
B = 500          # bootstrap resamples per simulated gate
LB_Q = 0.05      # LB90 = 5th percentile of the stratified cluster bootstrap
THR = {"G3 QA kappa": 0.45, "G4 M-val": 0.86}   # lines above the bad level (see the comment below)

# quantity: (kind, size parameter, good level, bad level). Rule for every 'ratio', 'f1' and 'class'
# quantity: pass iff LB90 >= THR.get(quantity, bad level). Two lines sit above their bad level because the
# percentile cluster bootstrap under-covers there: QA kappa (mean of 8 per-item kappas) 0.45 for bad 0.40,
# and M-val (skewed value counts) 0.86 for bad 0.85. 'count' quantity: pass iff successes >= c(n), the smallest c with
# P(X >= c | n, bad) <= 0.05 (exact binomial).
Q = {
    "G1 accept EA":  ("ratio", ("pois", 60), 0.95, 0.85),
    "G1 accept EB":  ("ratio", ("pois", 60), 0.95, 0.85),
    "G3 raw S":      ("ratio", ("fixed", 16), 0.85, 0.70),
    "G3 raw D":      ("ratio", ("fixed", 13), 0.85, 0.70),
    "G3 raw F":      ("ratio", ("fixed", 6), 0.85, 0.70),
    "G3 raw QA-sub": ("ratio", ("fixed", 22), 0.85, 0.70),
    "G3 raw CT":     ("ratio", ("fixed", 6), 0.85, 0.70),
    "G3 raw H-attr": ("ratio", ("pois", 9), 0.85, 0.70),   # value_type, arm_role, metric_kind on matched H units
    "G3 QA kappa":   ("kappa", 8, 0.70, 0.40),
    "G4 F1_H":       ("f1", ("pois", 4), 0.85, 0.70),
    "G4 F1_G":       ("f1", ("nb", 3), 0.75, 0.60),
    "G4 F1_K":       ("f1", ("nb", 8), 0.75, 0.60),
    "G4 M-val":      ("ratio", ("nb", 15), 0.95, 0.85),
    "G4 M-class":    ("class", None, 0.85, 0.65),
    "G5 anchors":    ("count", None, 0.85, 0.60),
}
NAMES = list(Q)
# QA score marginals for the 8 gated items (QA1-QA7, QA9; scores 0/1/2), an E0 assumption
QA_MARG = np.array([[.30, .35, .35], [.30, .40, .30], [.15, .45, .40], [.55, .25, .20],
                    [.60, .25, .15], [.35, .40, .25], [.25, .35, .40], [.30, .45, .25]])
W = 1 - np.abs(np.subtract.outer(np.arange(3), np.arange(3))) / 2.0   # linear weights


def counts(rng, spec, size, nb_k):
    kind, lam = spec
    if kind == "fixed":
        return np.full(size, lam)
    if kind == "pois":
        return rng.poisson(lam, size)
    return rng.negative_binomial(nb_k, nb_k / (nb_k + lam), size)   # mean lam, overdispersed


def beta_from_u(u, p, icc):
    k = 1.0 / icc - 1.0
    return special.betaincinv(p * k, (1 - p) * k, u)


def wkappa(c):
    """c: (..., 9) joint counts of (X, Y) scores; linear-weighted kappa per leading index."""
    c = c.reshape(c.shape[:-1] + (3, 3)).astype(float)
    n = c.sum((-1, -2), keepdims=True)
    p = c / np.maximum(n, 1)
    po = (p * W).sum((-1, -2))
    pe = (p.sum(-1)[..., :, None] * p.sum(-2)[..., None, :] * W).sum((-1, -2))
    return (po - pe) / np.maximum(1 - pe, 1e-12)


def c_min(n, bad):
    return next(c for c in range(n + 1) if stats.binom.sf(c - 1, n, bad) <= 0.05)


def simulate(n, levels, sims, seed, icc=0.10, omega=0.0, nb_k=1.5, lam_scale=None):
    """Returns (sims, len(NAMES)) boolean pass matrix."""
    rng = np.random.default_rng(seed)
    strata = np.repeat(np.arange(3), n // 3)
    n = len(strata)
    cmin = c_min(n, Q["G5 anchors"][3])
    out = np.zeros((sims, len(NAMES)), bool)
    for s in range(sims):
        z = rng.standard_normal(n)
        def u():
            return stats.norm.cdf(np.sqrt(omega) * z + np.sqrt(1 - omega) * rng.standard_normal(n))
        # one bootstrap index matrix per simulated gate, shared by every metric (joint resampling)
        idx = np.concatenate([np.flatnonzero(strata == h)[rng.integers(0, n // 3, (B, n // 3))] for h in range(3)], 1)
        def lb(num, den):
            return np.quantile(num[idx].sum(1) / np.maximum(den[idx].sum(1), 1e-12), LB_Q)
        both_g = None
        for j, name in enumerate(NAMES):
            kind, size, _, bad = Q[name]
            thr = THR.get(name, bad)
            p = levels[name]
            if kind == "ratio":
                spec = size if lam_scale is None or size[0] == "fixed" else (size[0], size[1] * lam_scale.get(name, 1))
                m = counts(rng, spec, n, nb_k)
                x = rng.binomial(m, beta_from_u(u(), p, icc))
                out[s, j] = lb(x.astype(float), m.astype(float)) >= thr
            elif kind == "f1":
                lam = size[1] * (lam_scale.get(name, 1) if lam_scale else 1)
                U = counts(rng, (size[0], lam), n, nb_k)
                both = rng.binomial(U, beta_from_u(u(), p / (2 - p), icc))
                if name == "G4 F1_G":
                    both_g = both
                out[s, j] = lb(2.0 * both, (U + both).astype(float)) >= thr
            elif kind == "class":
                m = both_g
                x = rng.binomial(m, beta_from_u(u(), p, icc))
                out[s, j] = lb(x.astype(float), m.astype(float)) >= thr
            elif kind == "kappa":
                a = beta_from_u(u(), np.sqrt(p), icc)[:, None]          # rater accuracy; kappa_w = a^2
                T = (rng.random((n, size, 1)) > QA_MARG.cumsum(1)[None]).sum(-1)
                def rate():
                    e = (rng.random((n, size, 1)) > QA_MARG.cumsum(1)[None]).sum(-1)
                    return np.where(rng.random((n, size)) < a, T, e)
                X, Y = rate(), rate()
                onehot = np.zeros((n, size, 9), np.int16)
                np.put_along_axis(onehot, (3 * X + Y)[..., None], 1, -1)
                kb = wkappa(onehot[idx].sum(1)).mean(-1)                  # (B,) mean per-item kappa
                out[s, j] = np.quantile(kb, LB_Q) >= thr
            elif kind == "count":
                out[s, j] = (u() < p).sum() >= cmin
    return out


def levels_with(bad=None, all_bad=False):
    return {k: (v[3] if (all_bad or k == bad) else v[2]) for k, v in Q.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--quick", action="store_true", help="fewer replicates for the search and sensitivity tables")
    a = ap.parse_args()
    t0 = time.time()
    print(f"python {platform.python_version()}, numpy {np.__version__}, scipy {__import__('scipy').__version__}; "
          f"SEED {SEED}; bootstrap B {B}; LB90 = {int(LB_Q*100)}th percentile")
    print("\nQuantities, levels and rules (pass iff LB90 >= line; G5: count >= c(n)):")
    for k, (kind, size, g, b) in Q.items():
        line = f"count >= c(n) (P(pass | {b:.2f}) <= 0.05)" if kind == "count" else f"LB90 >= {THR.get(k, b):.2f}"
        print(f"  {k:<14} {kind:<6} size {str(size):<14} good {g:.2f}  bad {b:.2f}  rule {line}")

    n, S = a.n, a.sims
    print(f"\n== Design n = {n} (3 strata x {n//3}), ICC 0.10, OMEGA 0 (independent record effects across metrics), "
          f"{S} replicates; G5 c(n) = {c_min(n, 0.60)} ==")
    good = simulate(n, levels_with(), S, SEED)
    print(f"  ALL GOOD: joint P(pass) = {good.all(1).mean():.3f} (MC s.e. {np.sqrt(good.all(1).mean()*(1-good.all(1).mean())/S):.3f})")
    print("  marginal P(pass | good): " + "; ".join(f"{k} {good[:, j].mean():.3f}" for j, k in enumerate(NAMES)))
    print("  ONE QUANTITY BAD (others good):           joint P(pass)   P(that criterion passes)")
    worst = 0
    for i, k in enumerate(NAMES, start=1):
        r = simulate(n, levels_with(bad=k), S, SEED + i)
        worst = max(worst, r.all(1).mean())
        print(f"    {k:<16}                            {r.all(1).mean():.3f}           {r[:, NAMES.index(k)].mean():.3f}")
    allb = simulate(n, levels_with(all_bad=True), S, SEED + 99)
    print(f"  ALL BAD: joint P(pass) = {allb.all(1).mean():.3f}")
    print(f"  max over single bad quantities = {worst:.3f}")

    S2 = 500 if a.quick else 1000
    print(f"\n== Search over n ({S2} replicates; ICC 0.10, OMEGA 0) ==")
    print("   n   P(pass|all good)   max_q P(pass|q bad)   c(n)   gate EA+EB records")
    for nn in (30, 36, 45, 54, 60, 72):
        g = simulate(nn, levels_with(), S2, SEED + 200 + nn).all(1).mean()
        wb = max(simulate(nn, levels_with(bad=k), S2, SEED + 300 + nn + i).all(1).mean()
                 for i, k in enumerate(("G4 F1_G", "G4 F1_K", "G5 anchors", "G3 raw F", "G3 QA kappa", "G4 M-class", "G4 M-val")))
        print(f"  {nn:3d}        {g:.3f}               {wb:.3f}          {c_min(nn, 0.60):3d}      {2*nn}")
    print("  (the search evaluates seven quantities: those with the highest bad-level pass rates in trial runs at n = 45 and 60)")

    print(f"\n== Sensitivity at n = {n} ({S2} replicates; P(pass | all good)) ==")
    cases = [("baseline ICC 0.10, OMEGA 0", {}),
             ("OMEGA 0.5 (correlated record effects)", {"omega": 0.5}),
             ("ICC 0.20", {"icc": 0.20}),
             ("ICC 0.20, OMEGA 0.5", {"icc": 0.20, "omega": 0.5}),
             ("fewer units: groups 2, K 5, H 3, values 10 per record", {"lam_scale": {"G4 F1_G": 2/3, "G4 F1_K": 5/8, "G4 F1_H": 3/4, "G4 M-val": 10/15}}),
             ("unit counts more skewed (NB shape 0.7)", {"nb_k": 0.7})]
    for i, (lab, kw) in enumerate(cases):
        g = simulate(n, levels_with(), S2, SEED + 500 + i, **kw).all(1).mean()
        b1 = simulate(n, levels_with(bad="G4 F1_G"), S2, SEED + 600 + i, **kw).all(1).mean()
        print(f"  {lab:<58} good {g:.3f}   F1_G bad {b1:.3f}")
    print(f"\nelapsed {time.time() - t0:.0f} s")


if __name__ == "__main__":
    sys.exit(main())
