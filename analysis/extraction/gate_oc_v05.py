"""Gate model and operating characteristics, extraction form v0.5 (EXTRACTION-PLAN-v0.5 s10.3-s10.8; red-team
audit 4, MA1, MA3, mi2, mi5). gate_oc_v04.py is left unchanged so that its logs stay reproducible.

Changes from the v0.4 model:
  * Every criterion, level, line and unit-count assumption is read from a declared config file
    (default analysis/extraction/gate-config-v05.json; --config for Stage A's counts, MA3). The script holds no
    unit count.
  * M-sign is counted over sign decisions, i.e. (matched group, metric key) pairs, not over K units (MA1: the
    sign is set per metric, so K units of one metric are copies of one decision).
  * M-pool is counted over matched groups, not over K units (MA1: the derived flag is a group-level value
    copied to every K unit of the group).
  * K-attr is the mean of four per-field agreements (held_fixed, budget_across_arms, credited_ablation on
    matched groups; scoring on matched arms), each pooled separately (mi2). credited_ablation alone is
    computed as a report-only diagnostic ('D credited_ablation alone').
  * The per-record data generator (gen) and the gate's decision statistic (evaluate) are shared with
    gate_bip_v05.py, so that the adaptive simulation and the fixed-n tables use one model.
Model otherwise as v0.4: per record and quantity, agreement ~ Beta(mean, ICC) with the quantity's own ICC
(a float or a {name: icc} dict, '_' = default, 'G3 K-attr:<field>' for a K-attr field); Gaussian copula weight
OMEGA; units per record Poisson, fixed or negative binomial; QA kappa via rater accuracy sqrt(kappa); the
gate's stratified cluster bootstrap (B_SIM resamples per simulated gate; production uses B = 4,000).
Every input is an assumption (E0). Not a result about any paper.

Run from the worktree root:
  python -u -E -P analysis/extraction/gate_oc_v05.py --calibrate [--workers 8]     -> gate_oc_v05-calibrate-log.txt
  python -u -E -P analysis/extraction/gate_oc_v05.py --table-a   [--workers 8]     -> gate_oc_v05-tableA-log.txt
  python -u -E -P analysis/extraction/gate_oc_v05.py --grid-out analysis/extraction/bip-grid-v2.json [--workers 8]
                                                                                   -> gate_oc_v05-grid-log.txt
  python -u -E -P analysis/extraction/gate_oc_v05.py --icc-json <per-metric ICC .json> --n 90   (B1 rerun)
Seeds (plan v0.5 s2.10): 20265000 + offset; calibrate 0-99, table A 100-199, grid 200-399, --icc-json 400-449.
Results do not depend on --workers (every task has its own seed).
"""
import argparse
import hashlib
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import special, stats

HERE = Path(__file__).resolve().parent
CONFIG_DEFAULT = HERE / "gate-config-v05.json"
SEED = 20265000
B_SIM = 500
QA_MARG = np.array([[.30, .35, .35], [.30, .40, .30], [.15, .45, .40], [.55, .25, .20],
                    [.60, .25, .15], [.35, .40, .25], [.25, .35, .40], [.30, .45, .25]])
W = 1 - np.abs(np.subtract.outer(np.arange(3), np.arange(3))) / 2.0
FIRST = ("G4 F1_G", "G4 F1_K")          # generated first: they supply matched groups and matched K units


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_config(path=CONFIG_DEFAULT):
    path = Path(path)
    cfg = json.loads(path.read_text(encoding="utf-8"))
    cfg["_sha256"] = sha256(path)
    cfg["_path"] = str(path)
    return cfg


def model_sha(cfg):
    """Same definition as gate_rule_v05.model_sha (kept here so the model module imports nothing)."""
    m = {"criteria": cfg["criteria"], "units": {k: v for k, v in cfg["units"].items() if k != "note"},
         "kattr_fields": cfg["kattr_fields"], "n_grid": cfg["design"]["n_grid"]}
    return hashlib.sha256(json.dumps(m, sort_keys=True).encode("utf-8")).hexdigest()


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


class Model:
    def __init__(self, cfg):
        self.cfg = cfg
        self.Q = cfg["criteria"]
        self.names = list(self.Q)
        self.gated = [k for k in self.names if not self.Q[k].get("report_only")]
        self.units = cfg["units"]
        self.fields = cfg["kattr_fields"]
        self.lines = {k: v["line"] for k, v in self.Q.items()}
        # ICC metrics: per-record (x, m) pairs on which the per-metric bound is computed
        self.icc_metrics = []
        for k in self.names:
            kind = self.Q[k]["kind"]
            if kind in ("ratio", "f1", "onG", "onS"):
                self.icc_metrics.append(k)
            elif kind == "kattr":
                self.icc_metrics += [f"{k}:{f}" for f in self.fields]

    @staticmethod
    def ic(icc, name, parent=None):
        if not isinstance(icc, dict):
            return float(icc)
        if name in icc:
            return icc[name]
        if parent is not None and parent in icc:
            return icc[parent]
        return icc.get("_", 0.10)

    def levels(self, bad=None, all_bad=False, extra=None):
        lv = {k: (v["bad"] if (all_bad or k == bad) else v["good"]) for k, v in self.Q.items()}
        lv.update(extra or {})
        return lv

    def gen(self, rng, n, levels, icc, omega=0.0, nb_k=None):
        """Per-record data of every criterion for n records. Returns (D, raw): D[name] = decision data,
        raw[icc metric] = (x, m) per record (F1 metrics: matched and union units, the Jaccard scale)."""
        nb_k = self.units["nb_shape"] if nb_k is None else nb_k
        z = rng.standard_normal(n)

        def u():
            return stats.norm.cdf(np.sqrt(omega) * z + np.sqrt(1 - omega) * rng.standard_normal(n))
        D, raw, matched = {}, {}, {}
        for name in list(FIRST) + [k for k in self.names if k not in FIRST]:
            q = self.Q[name]
            kind = q["kind"]
            if kind == "field":
                continue
            p = levels[name]
            if kind == "ratio":
                m = counts(rng, q["size"], n, nb_k)
                x = rng.binomial(m, beta_from_u(u(), p, self.ic(icc, name)))
                D[name], raw[name] = ("ratio", x.astype(float), m.astype(float)), (x, m)
            elif kind == "f1":
                U = counts(rng, q["size"], n, nb_k)
                both = rng.binomial(U, beta_from_u(u(), p / (2 - p), self.ic(icc, name)))
                matched[name] = both
                D[name], raw[name] = ("ratio", 2.0 * both, (U + both).astype(float)), (both, U)
            elif kind == "onG":
                m = matched["G4 F1_G"]
                x = rng.binomial(m, beta_from_u(u(), p, self.ic(icc, name)))
                D[name], raw[name] = ("ratio", x.astype(float), m.astype(float)), (x, m)
            elif kind == "onS":
                k, g = matched["G4 F1_K"], matched["G4 F1_G"]
                c = np.where(k > 0, np.maximum(g, 1), 0)
                d = np.minimum(k, c + rng.poisson(self.units["sign_extra_per_group"] * c))
                x = rng.binomial(d, beta_from_u(u(), p, self.ic(icc, name)))
                D[name], raw[name] = ("ratio", x.astype(float), d.astype(float)), (x, d)
            elif kind == "kattr":
                g = matched["G4 F1_G"]
                a = 2 * g + rng.poisson(self.units["arms_extra_per_group"] * g)
                fl = []
                for f in self.fields:
                    key = f"{name}:{f}"
                    m = a if f == "scoring" else g
                    x = rng.binomial(m, beta_from_u(u(), levels.get(key, p), self.ic(icc, key, parent=name)))
                    fl.append((x.astype(float), m.astype(float)))
                    raw[key] = (x, m)
                D[name] = ("kattr", fl)
            elif kind == "kappa":
                a = beta_from_u(u(), np.sqrt(p), self.ic(icc, name))[:, None]
                size = q["size"]
                T = (rng.random((n, size, 1)) > QA_MARG.cumsum(1)[None]).sum(-1)

                def rate():
                    e = (rng.random((n, size, 1)) > QA_MARG.cumsum(1)[None]).sum(-1)
                    return np.where(rng.random((n, size)) < a, T, e)
                X, Y = rate(), rate()
                oh = np.zeros((n, size, 9), np.int16)
                np.put_along_axis(oh, (3 * X + Y)[..., None], 1, -1)
                D[name] = ("kappa", oh)
            elif kind == "count":
                D[name] = ("count", u() < p)
        for name in self.names:
            q = self.Q[name]
            if q["kind"] == "field":
                j = self.fields.index(q["field"])
                x, m = D[q["of"]][1][j]
                D[name] = ("ratio", x, m)
        return D, raw

    def stats(self, D, strata_rows, rng, B=B_SIM):
        """Decision statistic of every criterion on the records in strata_rows (one index array per stratum):
        LB90 (5th percentile of the stratified cluster bootstrap) for ratio, K-attr and kappa criteria; the
        count for G5. One bootstrap index matrix shared by every criterion, as in production."""
        idx = np.concatenate([s[rng.integers(0, len(s), (B, len(s)))] for s in strata_rows], 1)
        S = np.concatenate(strata_rows)
        out = np.zeros(len(self.names))
        for j, name in enumerate(self.names):
            d = D[name]
            if d[0] == "ratio":
                out[j] = np.quantile(d[1][idx].sum(1) / np.maximum(d[2][idx].sum(1), 1e-12), 0.05)
            elif d[0] == "kattr":
                r = [x[idx].sum(1) / np.maximum(m[idx].sum(1), 1e-12) for x, m in d[1]]
                out[j] = np.quantile(np.mean(r, 0), 0.05)
            elif d[0] == "kappa":
                out[j] = np.quantile(wkappa(d[1][idx].sum(1)).mean(-1), 0.05)
            elif d[0] == "count":
                out[j] = d[1][S].sum()
        return out

    def passes(self, st, n, lines=None):
        """st: (..., len(names)) statistics -> boolean pass array. G5 compares its count with c(n)."""
        lines = self.lines if lines is None else lines
        thr = np.array([c_min(n, self.Q[k]["bad"]) if self.Q[k]["kind"] == "count" else lines[k]
                        for k in self.names])
        return st >= thr - 1e-12

    def joint(self, ps):
        g = [self.names.index(k) for k in self.gated]
        return ps[..., g].all(-1)


def contiguous(n):
    per = n // 3
    return [np.arange(h * per, (h + 1) * per) for h in range(3)]


def simulate(cfg, n, levels, sims, seed, icc=0.10, omega=0.0, nb_k=None):
    """(sims, len(names)) matrix of decision statistics for a fixed-n gate."""
    M = Model(cfg)
    rng = np.random.default_rng(seed)
    rows = contiguous(n)
    out = np.zeros((sims, len(M.names)))
    for s in range(sims):
        D, _ = M.gen(rng, n, levels, icc, omega, nb_k)
        out[s] = M.stats(D, rows, rng)
    return out


# ---- tasks (top level, picklable) -------------------------------------------------------------------------
def task(args):
    cfg_path, n, levels, sims, seed, icc, omega, nb_k = args
    return simulate(load_config(cfg_path), n, levels, sims, seed, icc, omega, nb_k)


def run_tasks(tasks, workers):
    if workers <= 1:
        return [task(t) for t in tasks]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(task, tasks))


def header(cfg, M):
    print(f"python {platform.python_version()}, numpy {np.__version__}, scipy {__import__('scipy').__version__}; "
          f"SEED {SEED}; bootstrap B {B_SIM} per simulated gate (production {cfg['bootstrap']['B']})")
    print(f"config {cfg['_path']} sha256 {cfg['_sha256']}; model sha256 {model_sha(cfg)}; script sha256 {sha256(__file__)}")
    print("criteria (pass iff LB90 >= line; G5: count >= c(n)):")
    for k in M.names:
        q = M.Q[k]
        rule = "count >= c(n)" if q["kind"] == "count" else f"LB90 >= {q['line']:.2f}"
        print(f"  {k:<26} {q['kind']:<6} size {str(q.get('size')):<14} good {q['good']:.2f} bad {q['bad']:.2f} "
              f"{rule}{'  (report only)' if q.get('report_only') else ''}")
    print(f"units: {json.dumps({k: v for k, v in cfg['units'].items() if k != 'note'})}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(CONFIG_DEFAULT))
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--table-a", action="store_true")
    ap.add_argument("--grid-out")
    ap.add_argument("--icc-json")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--sims", type=int, default=1000)
    a = ap.parse_args()
    t0 = time.time()
    cfg = load_config(a.config)
    M = Model(cfg)
    header(cfg, M)
    C = a.config

    if a.calibrate:
        cands = {"G4 M-sign": (0.90, 0.91, 0.92, 0.93, 0.94), "G4 M-pool": (0.70, 0.71, 0.72, 0.73),
                 "G3 K-attr": (0.70, 0.71, 0.72, 0.73), "D credited_ablation alone": (0.70, 0.71, 0.72, 0.73)}
        sets = [(60, 0.10), (120, 0.30), (120, 0.50)]
        tasks, keys = [], []
        for i, name in enumerate(cands):
            lv = M.levels(bad=name)
            if name == "D credited_ablation alone":
                lv = M.levels(extra={"G3 K-attr:credited_ablation": M.Q[name]["bad"]})
            for j, (n, ic) in enumerate(sets):
                tasks.append((C, n, lv, a.sims, SEED + 10 * i + j, ic, 0.0, None))
                keys.append((name, n, ic))
        res = run_tasks(tasks, a.workers)
        print(f"\n== Calibration: P(criterion passes | its bad level, others good), {a.sims} simulated gates each ==")
        print("Rule (unchanged from v0.4): the line is the smallest candidate >= the bad level with P <= 0.05 at n 60, ICC 0.10.")
        for (name, n, ic), st in zip(keys, res):
            j = M.names.index(name)
            row = "  ".join(f"line {L:.2f}: {np.mean(st[:, j] >= L - 1e-12):.3f}" for L in cands[name])
            print(f"  {name:<26} n {n:3d} ICC {ic:.2f}: {row}")
        print(f"\nelapsed {time.time() - t0:.0f} s")
        return

    if a.table_a:
        S = 2000
        scen = [("every quantity good", M.levels())]
        scen += [(f"{k} bad", M.levels(bad=k)) for k in M.gated]
        scen += [(f"K-attr field {f} bad (others good)", M.levels(extra={f"G3 K-attr:{f}": 0.70}))
                 for f in M.fields]
        scen += [("every quantity bad", M.levels(all_bad=True))]
        tasks = [(C, 60, lv, S, SEED + 100 + i, 0.10, 0.0, None) for i, (_, lv) in enumerate(scen)]
        tasks += [(C, 60, M.levels(), 1000, SEED + 190, 0.10, 0.5, None),
                  (C, 60, M.levels(), 1000, SEED + 191, 0.10, 0.0, 0.7)]
        res = run_tasks(tasks, a.workers)
        print(f"\n== A. Fixed n = 60 (3 x 20), ICC 0.10, OMEGA 0, {S} simulated gates per scenario; G5 c(60) = {c_min(60, 0.60)} ==")
        print("  scenario                                         P(gate passes)  P(that criterion passes)  P(D credited alone passes)")
        jd = M.names.index("D credited_ablation alone")
        worst = (0, "")
        for (lab, lv), st in zip(scen, res[:len(scen)]):
            ps = M.passes(st, 60)
            pj = M.joint(ps).mean()
            crit = lab[:-4] if lab.endswith(" bad") and lab[:-4] in M.names else None
            cp = f"{ps[:, M.names.index(crit)].mean():.3f}" if crit else "     "
            print(f"  {lab:<48} {pj:.3f}           {cp}                     {ps[:, jd].mean():.3f}")
            if crit:
                worst = max(worst, (pj, crit))
            if lab == "every quantity good":
                se = np.sqrt(pj * (1 - pj) / S)
                print(f"    MC s.e. {se:.3f}; marginals: " + "; ".join(f"{k} {ps[:, j].mean():.3f}" for j, k in enumerate(M.names)))
                print(f"    joint P(pass) if 'D credited_ablation alone' were a 20th gated criterion: "
                      f"{(M.joint(ps) & ps[:, jd]).mean():.3f}")
        print(f"  max over single bad gated quantities = {worst[0]:.3f} ({worst[1]})")
        for lab, st in zip(("OMEGA 0.5 (correlated record effects)", "unit counts more skewed (NB shape 0.7)"), res[len(scen):]):
            print(f"  sensitivity, {lab}: P(pass | all good) {M.joint(M.passes(st, 60)).mean():.3f} (1000)")
        print(f"\nelapsed {time.time() - t0:.0f} s")
        return

    if a.grid_out:
        thetas = (0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60)
        ns = tuple(cfg["design"]["n_grid"])
        tasks = [(C, n, M.levels(), a.sims, SEED + 200 + 10 * i + j, th, 0.0, None)
                 for i, th in enumerate(thetas) for j, n in enumerate(ns)]
        res = run_tasks(tasks, a.workers)
        marg = {k: [[0.0] * len(ns) for _ in thetas] for k in M.names}
        joint = [[0.0] * len(ns) for _ in thetas]
        prod = [[0.0] * len(ns) for _ in thetas]
        it = iter(res)
        for i, th in enumerate(thetas):
            for j, n in enumerate(ns):
                ps = M.passes(next(it), n)
                for c, k in enumerate(M.names):
                    marg[k][i][j] = float(ps[:, c].mean())
                joint[i][j] = float(M.joint(ps).mean())
                prod[i][j] = float(np.prod([ps[:, M.names.index(k)].mean() for k in M.gated]))
        out = {"version": "bip-grid-v2", "config": cfg["_path"], "config_sha256": cfg["_sha256"],
               "model_sha256": model_sha(cfg),
               "script_sha256": sha256(__file__), "seed_base": SEED + 200, "sims_per_cell": a.sims,
               "bootstrap_B_sim": B_SIM, "icc_common_to_all_metrics": True, "theta": list(thetas), "n": list(ns),
               "marginal": marg, "joint": joint, "product_of_marginals": prod,
               "python": platform.python_version(), "numpy": np.__version__}
        Path(a.grid_out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"\n== B. Grid: P(pass | every quantity good), ICC common to every metric, {a.sims} simulated gates per cell ==")
        print("   ICC   " + "".join(f"n={n:<16}" for n in ns))
        for i, th in enumerate(thetas):
            print(f"  {th:.2f}   " + "".join(f"{joint[i][j]:.3f} ({prod[i][j]:.3f})  " for j in range(len(ns))))
        print(f"  (joint P; in parentheses the product of the {len(M.gated)} gated marginals, the approximation the product rule uses)")
        d = np.array(prod) - np.array(joint)
        print(f"  product - joint: mean {d.mean():+.4f}, min {d.min():+.4f}, max {d.max():+.4f}")
        print("  smallest n with joint P >= 0.85: " + "; ".join(
            f"ICC {th:.2f}: {next((n for j, n in enumerate(ns) if joint[i][j] >= 0.85), 'none')}" for i, th in enumerate(thetas)))
        low = sorted(M.gated, key=lambda k: marg[k][2][0])[:6]
        print("  weakest marginals at ICC 0.10, n 60: " + "; ".join(f"{k} {marg[k][2][0]:.3f}" for k in low))
        print(f"  written {a.grid_out} sha256 {sha256(a.grid_out)}")
        print(f"\nelapsed {time.time() - t0:.0f} s")
        return

    if a.icc_json:
        icc = json.loads(Path(a.icc_json).read_text(encoding="utf-8"))
        weak = ("G4 F1_G", "G4 F1_K", "G4 M-anchorG", "G4 M-sign", "G4 M-pool", "G3 K-attr", "G4 M-class", "G4 M-val",
                "G5 anchors")
        tasks = [(C, a.n, M.levels(), a.sims, SEED + 400, icc, 0.0, None)]
        tasks += [(C, a.n, M.levels(bad=k), a.sims, SEED + 401 + i, icc, 0.0, None) for i, k in enumerate(weak)]
        res = run_tasks(tasks, a.workers)
        ps = M.passes(res[0], a.n)
        print(f"\n== Design check at n {a.n}, per-metric ICC {icc} ({a.sims} each) ==")
        print(f"  ALL GOOD: joint P(pass) {M.joint(ps).mean():.3f}; lowest marginals: "
              + "; ".join(f"{M.names[j]} {ps[:, j].mean():.3f}" for j in np.argsort(ps.mean(0))[:4]))
        wb = max((M.joint(M.passes(st, a.n)).mean(), k) for st, k in zip(res[1:], weak))
        print(f"  max over the {len(weak)} weakest single-bad scenarios: {wb[0]:.3f} ({wb[1]})")
        print(f"\nelapsed {time.time() - t0:.0f} s")
        return
    ap.print_help()


if __name__ == "__main__":
    sys.exit(main())
