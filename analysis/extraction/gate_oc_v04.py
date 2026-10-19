"""Joint operating characteristics of the extraction gate, form v0.4 (EXTRACTION-PLAN-v0.4 s10).

Extends gate_oc.py (v0.3; left unchanged so that gate_oc-log.txt stays reproducible) by the four criteria
red-team audit 3 asked for (C1): group-anchor agreement on matched groups (M-anchorG), sign agreement
(higher_is_better) on matched K units (M-sign), raw agreement on the K attributes that set poolability
(K-attr: held_fixed, budget_across_arms, credited_ablation per matched group; scoring per matched arm),
and agreement of the derived pooling flag K15 'matched' on matched K units (M-pool). It also takes the
intra-record correlation (ICC) per metric, so that the gate can be re-run with Stage A estimates (M1), and
simulates the split design of the red-team's m8 (L/Q/H criteria on 30 records, K and anchor criteria on 60).

Model (unchanged from v0.3): per record and metric, agreement ~ Beta(mean, ICC); record effects of different
metrics joined by a Gaussian copula with weight OMEGA (0 = independent, conservative for P(pass | good));
units per record Poisson or negative binomial (shape 1.5); QA kappa via rater accuracy sqrt(kappa); the same
stratified cluster bootstrap (B resamples per simulated gate, records resampled within three equal strata).
Every input is an assumption (E0). Not a result about any paper.

Run from the worktree root:  python -u -E -P analysis/extraction/gate_oc_v04.py [--quick] [--n 60]
                             [--icc-json path]   (per-metric ICC, Stage A rerun; keys = criterion names)
Seeds: numpy default_rng(SEED + offset), SEED = 20263000 (plan v0.4 seed table s2.10). Offsets: A 0-19 and 99, B 200-264,
C 400-468, D 500-644, E 700-701, --split 800-898, --calibrate 900-932, --icc-json 990-999 (gate_adaptive_v04.py: 950-979).
"""
import argparse
import json
import platform
import sys
import time

import numpy as np
from scipy import special, stats

SEED = 20263000
B = 500          # bootstrap resamples per simulated gate
LB_Q = 0.05      # LB90 = 5th percentile of the stratified cluster bootstrap

# quantity: (kind, size parameter, good level, bad level, block). kind 'ratio': units per record from the size
# parameter; 'f1': union units per record, matched ~ Bin(union, J) with J = F1 / (2 - F1); 'onG' / 'onK': a
# ratio whose units are the matched groups (from F1_G) or matched K units (from F1_K) of the same record;
# 'kappa': mean per-item linear-weighted kappa; 'count': records with F1 unit and S14 identical.
# block 'LQ' = criteria computed on blocks L, Q, H (split design: first 30 records); 'K' = block K and G5.
Q = {
    "G1 accept EA":  ("ratio", ("pois", 60), 0.95, 0.85, "K"),
    "G1 accept EB":  ("ratio", ("pois", 60), 0.95, 0.85, "K"),
    "G3 raw S":      ("ratio", ("fixed", 16), 0.85, 0.70, "LQ"),
    "G3 raw D":      ("ratio", ("fixed", 13), 0.85, 0.70, "LQ"),
    "G3 raw F":      ("ratio", ("fixed", 6), 0.85, 0.70, "LQ"),
    "G3 raw QA-sub": ("ratio", ("fixed", 22), 0.85, 0.70, "LQ"),
    "G3 raw CT":     ("ratio", ("fixed", 6), 0.85, 0.70, "LQ"),
    "G3 raw H-attr": ("ratio", ("pois", 9), 0.85, 0.70, "LQ"),
    "G3 K-attr":     ("ratio", ("nb", 18), 0.85, 0.70, "K"),     # new (C1): held_fixed, budget, credited, scoring
    "G3 QA kappa":   ("kappa", 8, 0.70, 0.40, "LQ"),
    "G4 F1_H":       ("f1", ("pois", 4), 0.85, 0.70, "LQ"),
    "G4 F1_G":       ("f1", ("nb", 3), 0.75, 0.60, "K"),
    "G4 F1_K":       ("f1", ("nb", 8), 0.75, 0.60, "K"),
    "G4 M-val":      ("ratio", ("nb", 15), 0.95, 0.85, "K"),
    "G4 M-class":    ("onG", None, 0.85, 0.65, "K"),
    "G4 M-anchorG":  ("onG", None, 0.85, 0.70, "K"),             # new (C1): anchor arm on matched groups
    "G4 M-sign":     ("onK", None, 0.97, 0.90, "K"),             # new (C1): higher_is_better on matched K units
    "G4 M-pool":     ("onK", None, 0.85, 0.70, "K"),             # new (C1): derived K15 'matched' flag
    "G5 anchors":    ("count", None, 0.85, 0.60, "K"),
}
NAMES = list(Q)
# Lines (pass iff LB90 >= line). Default line = bad level. Raised where the percentile cluster bootstrap
# under-covers at the bad level (v0.3: QA kappa, M-val; v0.4 calibration run printed by --calibrate).
THR = {"G3 QA kappa": 0.45, "G4 M-val": 0.86, "G3 K-attr": 0.71, "G4 M-anchorG": 0.71, "G4 M-sign": 0.91,
       "G4 M-pool": 0.71}
QA_MARG = np.array([[.30, .35, .35], [.30, .40, .30], [.15, .45, .40], [.55, .25, .20],
                    [.60, .25, .15], [.35, .40, .25], [.25, .35, .40], [.30, .45, .25]])
W = 1 - np.abs(np.subtract.outer(np.arange(3), np.arange(3))) / 2.0
ORDER_G = ["G4 F1_G", "G4 F1_K"]        # computed first: they supply matched groups / K units


def counts(rng, spec, size, nb_k):
    kind, lam = spec
    if kind == "fixed":
        return np.full(size, lam)
    if kind == "pois":
        return rng.poisson(lam, size)
    return rng.negative_binomial(nb_k, nb_k / (nb_k + lam), size)


def beta_from_u(u, p, icc):
    icc = min(max(icc, 1e-4), 0.95)
    k = 1.0 / icc - 1.0
    return special.betaincinv(p * k, (1 - p) * k, u)


def wkappa(c):
    c = c.reshape(c.shape[:-1] + (3, 3)).astype(float)
    n = c.sum((-1, -2), keepdims=True)
    p = c / np.maximum(n, 1)
    po = (p * W).sum((-1, -2))
    pe = (p.sum(-1)[..., :, None] * p.sum(-2)[..., None, :] * W).sum((-1, -2))
    return (po - pe) / np.maximum(1 - pe, 1e-12)


def c_min(n, bad):
    return next(c for c in range(n + 1) if stats.binom.sf(c - 1, n, bad) <= 0.05)


def simulate(n, levels, sims, seed, icc=0.10, omega=0.0, nb_k=1.5, thr=None, n_lq=None):
    """Returns (sims, len(NAMES)) boolean pass matrix. icc: float or {name: icc}. n_lq: records used by the
    'LQ' criteria (split design; the first n_lq/3 records of each stratum); None = all n."""
    thr = THR if thr is None else thr
    rng = np.random.default_rng(seed)
    per = n // 3
    strata = np.repeat(np.arange(3), per)
    n = len(strata)
    sub = None if n_lq is None else np.concatenate([np.arange(h * per, h * per + n_lq // 3) for h in range(3)])
    cmin = c_min(n, Q["G5 anchors"][3])
    ic = (lambda name: icc.get(name, 0.10)) if isinstance(icc, dict) else (lambda name: icc)
    out = np.zeros((sims, len(NAMES)), bool)
    order = ORDER_G + [k for k in NAMES if k not in ORDER_G]
    for s in range(sims):
        z = rng.standard_normal(n)

        def u():
            return stats.norm.cdf(np.sqrt(omega) * z + np.sqrt(1 - omega) * rng.standard_normal(n))
        idx = np.concatenate([np.flatnonzero(strata == h)[rng.integers(0, per, (B, per))] for h in range(3)], 1)
        idx_lq = None
        if sub is not None:
            q = n_lq // 3
            idx_lq = np.concatenate([sub[h * q:(h + 1) * q][rng.integers(0, q, (B, q))] for h in range(3)], 1)

        def lb(num, den, block):
            ii = idx_lq if (block == "LQ" and idx_lq is not None) else idx
            return np.quantile(num[ii].sum(1) / np.maximum(den[ii].sum(1), 1e-12), LB_Q)
        matched = {}
        for name in order:
            j = NAMES.index(name)
            kind, size, _, bad, block = Q[name]
            line = thr.get(name, bad)
            p = levels[name]
            if kind == "ratio":
                m = counts(rng, size, n, nb_k)
                x = rng.binomial(m, beta_from_u(u(), p, ic(name)))
                out[s, j] = lb(x.astype(float), m.astype(float), block) >= line
            elif kind == "f1":
                U = counts(rng, size, n, nb_k)
                both = rng.binomial(U, beta_from_u(u(), p / (2 - p), ic(name)))
                matched[name] = both
                out[s, j] = lb(2.0 * both, (U + both).astype(float), block) >= line
            elif kind in ("onG", "onK"):
                m = matched["G4 F1_G" if kind == "onG" else "G4 F1_K"]
                x = rng.binomial(m, beta_from_u(u(), p, ic(name)))
                out[s, j] = lb(x.astype(float), m.astype(float), block) >= line
            elif kind == "kappa":
                a = beta_from_u(u(), np.sqrt(p), ic(name))[:, None]
                T = (rng.random((n, size, 1)) > QA_MARG.cumsum(1)[None]).sum(-1)

                def rate():
                    e = (rng.random((n, size, 1)) > QA_MARG.cumsum(1)[None]).sum(-1)
                    return np.where(rng.random((n, size)) < a, T, e)
                X, Y = rate(), rate()
                onehot = np.zeros((n, size, 9), np.int16)
                np.put_along_axis(onehot, (3 * X + Y)[..., None], 1, -1)
                ii = idx_lq if idx_lq is not None else idx
                kb = wkappa(onehot[ii].sum(1)).mean(-1)
                out[s, j] = np.quantile(kb, LB_Q) >= line
            elif kind == "count":
                out[s, j] = (u() < p).sum() >= cmin
    return out


def levels_with(bad=None, all_bad=False):
    return {k: (v[3] if (all_bad or k == bad) else v[2]) for k, v in Q.items()}


WEAK = ("G4 F1_G", "G4 F1_K", "G4 M-anchorG", "G4 M-sign", "G4 M-pool", "G3 K-attr", "G4 M-class",
        "G4 M-val", "G5 anchors")
LQ_WEAK = ("G3 raw F", "G3 raw CT", "G3 QA kappa", "G4 F1_H", "G3 raw H-attr")


def calibrate(S):
    """P(criterion passes | its bad level) for candidate lines of the new criteria (n 60, ICC 0.10)."""
    print(f"\n== Calibration of lines for the new criteria (n 60, ICC 0.10, {S} replicates) ==")
    for i, (name, lines) in enumerate((("G3 K-attr", (0.70, 0.71)), ("G4 M-anchorG", (0.70, 0.71, 0.72)),
                                       ("G4 M-sign", (0.90, 0.91, 0.92)), ("G4 M-pool", (0.70, 0.71, 0.72)))):
        for k, line in enumerate(lines):
            r = simulate(60, levels_with(bad=name), S, SEED + 900 + 10 * i + k, thr={**THR, name: line})
            print(f"  {name:<14} line {line:.2f}: P(criterion passes | bad {Q[name][3]:.2f}) = {r[:, NAMES.index(name)].mean():.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--icc-json", help="per-metric ICC (Stage A rerun): only the design check at --n is run")
    ap.add_argument("--split", action="store_true", help="only the split-design table (m8), log gate_oc_v04-split-log.txt")
    a = ap.parse_args()
    t0 = time.time()
    print(f"python {platform.python_version()}, numpy {np.__version__}, scipy {__import__('scipy').__version__}; "
          f"SEED {SEED}; bootstrap B {B}; LB90 = {int(LB_Q*100)}th percentile")
    print("\nQuantities, levels and rules (pass iff LB90 >= line; G5: count >= c(n)):")
    for k, (kind, size, g, b, blk) in Q.items():
        line = f"count >= c(n) (P(pass | {b:.2f}) <= 0.05)" if kind == "count" else f"LB90 >= {THR.get(k, b):.2f}"
        print(f"  {k:<14} {kind:<6} size {str(size):<14} good {g:.2f}  bad {b:.2f}  block {blk:<2}  rule {line}")
    S2 = 400 if a.quick else 1000
    if a.calibrate:
        calibrate(S2)
        return

    if a.split:
        print(f"\n== Split designs (m8): L/Q/H criteria on 30 records, K criteria and G5 on n ({S2} replicates) ==")
        for ci, (nn, ic) in enumerate([(nn, ic) for nn in (60, 90) for ic in (0.10, 0.20, 0.30)]):
            g = simulate(nn, levels_with(), S2, SEED + 800 + 10 * ci, icc=ic, n_lq=30).all(1).mean()   # offsets 800-850
            wb = max((simulate(nn, levels_with(bad=k), S2, SEED + 851 + 8 * ci + i, icc=ic, n_lq=30).all(1).mean(), k)
                     for i, k in enumerate(LQ_WEAK + ("G4 F1_G", "G4 M-anchorG", "G4 M-sign")))
            print(f"  K on {nn}, L/Q on 30, ICC {ic:.2f}: P(pass | all good) {g:.3f}; largest P(pass | one of 8 quantities bad) "
                  f"{wb[0]:.3f} ({wb[1]})")
        print(f"\nelapsed {time.time() - t0:.0f} s")
        return

    if a.icc_json:
        with open(a.icc_json, encoding="utf-8") as f:
            icc = json.load(f)
        print(f"\n== Stage A rerun: n {a.n}, per-metric ICC {icc}, {a.sims} replicates ==")
        g = simulate(a.n, levels_with(), a.sims, SEED + 990, icc=icc)
        print(f"  ALL GOOD: joint P(pass) = {g.all(1).mean():.3f}; lowest marginals: "
              + "; ".join(f"{NAMES[j]} {g[:, j].mean():.3f}" for j in np.argsort(g.mean(0))[:4]))
        wb = max((simulate(a.n, levels_with(bad=k), S2, SEED + 991 + i, icc=icc).all(1).mean(), k)
                 for i, k in enumerate(WEAK))
        print(f"  max over the {len(WEAK)} weakest single-bad scenarios: {wb[0]:.3f} ({wb[1]})")
        print(f"\nelapsed {time.time() - t0:.0f} s")
        return

    n, S = a.n, a.sims
    print(f"\n== A. Design n = {n} (3 x {n//3}), ICC 0.10, OMEGA 0, {S} replicates; G5 c(n) = {c_min(n, 0.60)} ==")
    good = simulate(n, levels_with(), S, SEED)
    pg = good.all(1).mean()
    print(f"  ALL GOOD: joint P(pass) = {pg:.3f} (MC s.e. {np.sqrt(pg*(1-pg)/S):.3f})")
    print("  marginal P(pass | good): " + "; ".join(f"{k} {good[:, j].mean():.3f}" for j, k in enumerate(NAMES)))
    print("  ONE QUANTITY BAD (others good):           joint P(pass)   P(that criterion passes)")
    worst = (0, "")
    for i, k in enumerate(NAMES, start=1):
        r = simulate(n, levels_with(bad=k), S, SEED + i)
        worst = max(worst, (r.all(1).mean(), k))
        print(f"    {k:<16}                            {r.all(1).mean():.3f}           {r[:, NAMES.index(k)].mean():.3f}")
    allb = simulate(n, levels_with(all_bad=True), S, SEED + 99)
    print(f"  ALL BAD: joint P(pass) = {allb.all(1).mean():.3f}")
    print(f"  max over single bad quantities = {worst[0]:.3f} ({worst[1]})")

    iccs = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40)
    ns = (60, 72, 90, 105, 120)
    print(f"\n== B. P(pass | all good) over ICC (common to every metric) and n ({S2} replicates; OMEGA 0) ==")
    print("   ICC   " + "".join(f"n={nn:<8}" for nn in ns))
    grid = {}
    for ii, ic in enumerate(iccs):
        row = []
        for jj, nn in enumerate(ns):
            grid[(ic, nn)] = simulate(nn, levels_with(), S2, SEED + 200 + 10 * ii + jj, icc=ic).all(1).mean()
            row.append(f"{grid[(ic, nn)]:.3f}    ")
        print(f"  {ic:.2f}   " + "".join(row))
    print("  smallest n in the grid with P(pass | all good) >= 0.85 (the B1 lookup):")
    for ic in iccs:
        ok = [nn for nn in ns if grid[(ic, nn)] >= 0.85]
        print(f"    ICC {ic:.2f}: {ok[0] if ok else 'none <= 120'}")

    print(f"\n== C. Largest P(pass | one bad) over the {len(WEAK)} weakest quantities ({S2} replicates) ==")
    for ci, (nn, ic) in enumerate(((60, 0.30), (90, 0.10), (90, 0.30), (120, 0.30))):
        wb = max((simulate(nn, levels_with(bad=k), S2, SEED + 400 + 20 * ci + i, icc=ic).all(1).mean(), k)
                 for i, k in enumerate(WEAK))
        print(f"  n {nn:3d}, ICC {ic:.2f}: {wb[0]:.3f} ({wb[1]})")

    print(f"\n== D. Split design (m8): L/Q/H criteria on the first 30 records, K criteria and G5 on 60 ({S2} replicates) ==")
    for ci, ic in enumerate((0.10, 0.20, 0.30)):
        g = simulate(60, levels_with(), S2, SEED + 500 + 10 * ci, icc=ic, n_lq=30).all(1).mean()
        wb = max((simulate(60, levels_with(bad=k), S2, SEED + 600 + 20 * ci + i, icc=ic, n_lq=30).all(1).mean(), k)
                 for i, k in enumerate(LQ_WEAK))
        print(f"  ICC {ic:.2f}: P(pass | all good) {g:.3f}; largest P(pass | one L/Q quantity bad) {wb[0]:.3f} ({wb[1]})")

    print(f"\n== E. Sensitivity at n = {n}, ICC 0.10 ({S2} replicates; P(pass | all good)) ==")
    for i, (lab, kw) in enumerate((("OMEGA 0.5 (correlated record effects)", {"omega": 0.5}),
                                   ("unit counts more skewed (NB shape 0.7)", {"nb_k": 0.7}))):
        g = simulate(n, levels_with(), S2, SEED + 700 + i, **kw).all(1).mean()
        print(f"  {lab:<58} good {g:.3f}")
    print(f"\nelapsed {time.time() - t0:.0f} s")


if __name__ == "__main__":
    sys.exit(main())
