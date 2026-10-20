"""Whole-procedure operating characteristics of gate design B-IP, extraction form v0.5 (EXTRACTION-PLAN-v0.5
s10.7; red-team audit 4, MA1 and mi5). Not a result about any paper; every input is the E0 model of
gate_oc_v05.py and the declared config.

One replicate = one gate: 3 strata x 40 ordered records are generated (gate_oc_v05.Model.gen); the first 20 per
stratum are phase 1. On phase 1 the per-metric Neyman bounds are computed (gate_rule_v05, R = 1,000 as in
production) and each candidate sizing rule sets n; the s10.4 rule is then applied once to the first n/3
records of each stratum. The rules share the replicate's data (common random numbers):
  P80   per-metric 80 percent bounds, product rule (binding candidate of plan v0.5 s10.7)
  P50   per-metric 50 percent bounds (median-unbiased), product rule
  X80   largest per-metric 80 percent bound of the gated count metrics, common-ICC joint grid
  V4    v0.4 rule: Neyman 80 percent bound of the mean ICC of the eight v0.4 count metrics (bisection), joint grid
Scenarios: ICC common to every metric, the red-team's H1 and H10 (ICC by metric), and others; one quantity
bad with the others good. Reported per rule: P(pass), its MC s.e., the distribution of n, mean n, expected gate
cost (mean n x gate-record cost of the config) and, for the product rules, P(step-6 statement).

Run from the worktree root:
  python -u -E -P analysis/extraction/gate_bip_v05.py --reps 1000 --chunks 4 --workers 16
      [--scenarios G10,H1] [--config ...] [--grid analysis/extraction/bip-grid-v2.json]
  -> stdout (log gate_bip_v05-log.txt) and gate_bip_v05-results.json
Seeds: 20265500 + 10 x scenario index + chunk (scenario index < 40, chunk < 10; plan v0.5 s2.10). Results do
not depend on --workers.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = _load("gate_oc_v05")
R = _load("gate_rule_v05")
SEED = 20265500
RULES = ("P80", "P50", "X80", "V4")


def scenarios(M):
    lv = M.levels
    lq = {k: 0.40 for k in M.names if M.Q[k]["block"] == "LQ" or k.startswith("G1")}
    H1 = {"G4 M-sign": 0.5, "G4 M-pool": 0.5, "_": 0.10}
    H10 = {"G4 M-sign": 0.6, "G4 M-pool": 0.6, "G4 M-anchorG": 0.3, "_": 0.10}
    HP = {"G4 M-pool": 0.5, "_": 0.05}
    HG = {"G4 M-anchorG": 0.4, "G4 M-pool": 0.4, "G4 M-class": 0.4, "_": 0.10}
    S = [  # (key, label, levels, icc, nb_k)
        ("G05", "good; ICC 0.05 all", lv(), 0.05, None),
        ("G10", "good; ICC 0.10 all", lv(), 0.10, None),
        ("G20", "good; ICC 0.20 all", lv(), 0.20, None),
        ("G30", "good; ICC 0.30 all", lv(), 0.30, None),
        ("H1", "good; red-team H1: M-sign, M-pool 0.5, others 0.10", lv(), H1, None),
        ("H10", "good; red-team H10: M-sign, M-pool 0.6, M-anchorG 0.3, others 0.10", lv(), H10, None),
        ("H2", "good; F1_G 0.40, others 0.10", lv(), {"G4 F1_G": 0.4, "_": 0.10}, None),
        ("H3", "good; M-anchorG 0.40, others 0.05", lv(), {"G4 M-anchorG": 0.4, "_": 0.05}, None),
        ("H6", "good; L/Q/H and G1 criteria 0.40, others 0.05", lv(), {**lq, "_": 0.05}, None),
        ("N07", "good; ICC 0.10 all, unit counts NB shape 0.7", lv(), 0.10, 0.7),
        ("HG", "good; M-anchorG, M-pool, M-class 0.40, others 0.10", lv(), HG, None),
        ("HP", "good; M-pool 0.50, others 0.05", lv(), HP, None),
    ]
    for k in ("G4 F1_G", "G4 M-anchorG", "G4 M-pool", "G3 K-attr", "G4 M-class", "G1 accept EB", "G4 F1_K", "G4 M-val"):
        S.append((f"B10 {k}", f"{k} bad; ICC 0.10 all", lv(bad=k), 0.10, None))
    S += [("BH1 M-pool", "G4 M-pool bad; H1", lv(bad="G4 M-pool"), H1, None),
          ("BH10 M-pool", "G4 M-pool bad; H10", lv(bad="G4 M-pool"), H10, None),
          ("BH10 M-anchorG", "G4 M-anchorG bad; H10", lv(bad="G4 M-anchorG"), H10, None),
          ("B30 F1_G", "G4 F1_G bad; ICC 0.30 all", lv(bad="G4 F1_G"), 0.30, None),
          ("B30 M-anchorG", "G4 M-anchorG bad; ICC 0.30 all", lv(bad="G4 M-anchorG"), 0.30, None),
          ("B30 G1 EB", "G1 accept EB bad; ICC 0.30 all", lv(bad="G1 accept EB"), 0.30, None),
          ("BHP M-pool", "G4 M-pool bad; M-pool 0.50, others 0.05", lv(bad="G4 M-pool"), HP, None)]
    return S


def rows(per, per_max):
    return [np.arange(h * per_max, h * per_max + per) for h in range(3)]


def replicate(M, cfg, grid, levels, icc, nb_k, rng):
    d = cfg["design"]
    pmax, p1 = d["per_stratum_list"], d["per_stratum_phase1"]
    D, raw = M.gen(rng, 3 * pmax, levels, icc, nb_k=nb_k)
    S1 = np.concatenate(rows(p1, pmax))
    xm = {k: (raw[k][0][S1], raw[k][1][S1]) for k in M.icc_metrics}
    b = cfg["bound"]
    U80 = {k: R.neyman_upper(*xm[k], rng, R=b["R"], grid=b["theta_grid"], conf=0.80)[0] for k in M.icc_metrics}
    U50 = {k: R.neyman_upper(*xm[k], rng, R=b["R"], grid=b["theta_grid"], conf=0.50)[0] for k in M.icc_metrics}
    n = {}
    n["P80"], P80, f80 = R.n_product(R.theta_by_criterion(U80, cfg, grid), cfg, grid)
    n["P50"], P50, f50 = R.n_product(R.theta_by_criterion(U50, cfg, grid), cfg, grid)
    n["X80"], umax = R.n_max_rule(U80, cfg, grid)
    xs, ms = [], []
    for k in cfg["count_metrics_v04_pooled_rule"]:
        parts = M.Q[k]["icc_from"]
        xs.append(sum(xm[p][0] for p in parts)), ms.append(sum(xm[p][1] for p in parts))
    upool, _ = R.neyman_upper_pooled(xs, ms, rng, R=b["R"], grid=b["theta_grid"], conf=0.80)
    n["V4"] = R.n_common(upool, cfg, grid)[0]
    res = {}
    for nn in sorted(set(n.values())):
        st = M.stats(D, rows(nn // 3, pmax), rng)
        res[nn] = bool(M.joint(M.passes(st, nn)))
    return {"n": n, "pass": {r: res[n[r]] for r in RULES}, "step6": {"P80": f80, "P50": f50},
            "umax": umax, "upool": upool, "u80": U80}


def run_chunk(args):
    cfg_path, grid_path, si, chunk, reps = args
    cfg = G.load_config(cfg_path)
    grid = json.loads(Path(grid_path).read_text(encoding="utf-8"))
    M = G.Model(cfg)
    key, lab, levels, icc, nb_k = scenarios(M)[si]
    rng = np.random.default_rng(SEED + 10 * si + chunk)
    return [replicate(M, cfg, grid, levels, icc, nb_k, rng) for _ in range(reps)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(G.CONFIG_DEFAULT))
    ap.add_argument("--grid", default=str(HERE / "bip-grid-v2.json"))
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--chunks", type=int, default=4)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--scenarios", default="")
    ap.add_argument("--results", default=str(HERE / "gate_bip_v05-results.json"))
    a = ap.parse_args()
    t0 = time.time()
    cfg = G.load_config(a.config)
    grid = json.loads(Path(a.grid).read_text(encoding="utf-8"))
    M = G.Model(cfg)
    assert M.icc_metrics == R.icc_metrics(cfg)
    assert grid["model_sha256"] == R.model_sha(cfg), "grid was made from another model: rerun gate_oc_v05.py --grid-out"
    S = scenarios(M)
    keys = [s[0] for s in S]
    pick = [keys.index(k) for k in a.scenarios.split(",")] if a.scenarios else list(range(len(S)))
    assert len(S) <= 40 and a.chunks <= 10
    per = a.reps // a.chunks
    tasks = [(a.config, a.grid, si, c, per) for si in pick for c in range(a.chunks)]
    print(f"python {platform.python_version()}, numpy {np.__version__}; SEED {SEED}; reps {per * a.chunks} per scenario "
          f"({a.chunks} chunks); bound R {cfg['bound']['R']}; simulated gate bootstrap B {G.B_SIM} (production "
          f"{cfg['bootstrap']['B']})")
    print(f"config {cfg['_path']} sha256 {cfg['_sha256']}; model sha256 {R.model_sha(cfg)}")
    print(f"grid {a.grid} sha256 {hashlib.sha256(Path(a.grid).read_bytes()).hexdigest()}; scripts sha256: "
          f"gate_bip_v05 {G.sha256(__file__)[:16]}, gate_rule_v05 {G.sha256(R.__file__)[:16]}, "
          f"gate_oc_v05 {G.sha256(G.__file__)[:16]}")
    print(f"gated criteria ({len(M.gated)}): {', '.join(M.gated)}; report only: "
          f"{', '.join(k for k in M.names if k not in M.gated)}")
    if a.workers > 1:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            out = list(ex.map(run_chunk, tasks))
    else:
        out = [run_chunk(t) for t in tasks]
    lo, hi = cfg["cost"]["gate_record_ktokens"]
    ns = cfg["design"]["n_grid"]
    results = {"config_sha256": cfg["_sha256"], "model_sha256": R.model_sha(cfg),
               "grid_sha256": hashlib.sha256(Path(a.grid).read_bytes()).hexdigest(), "scenarios": {}}
    print(f"\nPer rule: P(pass) [MC s.e.]; share of n = {'/'.join(map(str, ns))}; mean n; expected gate cost "
          f"(mean n x {lo}k-{hi}k tokens); P(step 6) for the product rules")
    for j, si in enumerate(pick):
        key, lab = S[si][0], S[si][1]
        reps = [r for c in range(a.chunks) for r in out[j * a.chunks + c]]
        N = len(reps)
        print(f"\n[{key}] {lab} ({N} replicates); median largest U80 of the gated count metrics "
              f"{np.median([r['umax'] for r in reps]):.2f}; median pooled U (V4) {np.median([r['upool'] for r in reps]):.2f}")
        sc = {"label": lab, "replicates": N}
        for rule in RULES:
            p = np.mean([r["pass"][rule] for r in reps])
            nn = np.array([r["n"][rule] for r in reps])
            dist = [float(np.mean(nn == v)) for v in ns]
            s6 = np.mean([r["step6"][rule] for r in reps]) if rule in ("P80", "P50") else None
            sc[rule] = {"p_pass": float(p), "se": float(np.sqrt(p * (1 - p) / N)), "n_dist": dist,
                        "mean_n": float(nn.mean()), "cost_M": [nn.mean() * lo / 1000, nn.mean() * hi / 1000],
                        "p_step6": None if s6 is None else float(s6)}
            print(f"  {rule}: P(pass) {p:.3f} [{np.sqrt(p * (1 - p) / N):.3f}]; n " + " ".join(f"{v:.2f}" for v in dist)
                  + f"; mean n {nn.mean():.1f}; cost {nn.mean() * lo / 1000:.1f}M-{nn.mean() * hi / 1000:.1f}M"
                  + (f"; P(step 6) {s6:.2f}" if s6 is not None else ""))
        med = {k: float(np.median([r["u80"][k] for r in reps])) for k in M.icc_metrics}
        sc["median_u80"] = med
        print("  median U80 per metric: " + "; ".join(f"{k.replace('G3 K-attr:', 'KA:')} {v:.2f}" for k, v in med.items()))
        results["scenarios"][key] = sc
    Path(a.results).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"\nwritten {a.results}; elapsed {time.time() - t0:.0f} s")


if __name__ == "__main__":
    sys.exit(main())
