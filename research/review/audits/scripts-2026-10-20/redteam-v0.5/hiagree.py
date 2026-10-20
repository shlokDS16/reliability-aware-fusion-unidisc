"""Red-team v0.5 scratch: what does rule P80 do when an instrument is BETTER than the good level on some metrics?
Committed model and decision function imported read-only (gate_oc_v05.Model, gate_rule_v05). P80 only."""
import importlib.util, json, sys
from pathlib import Path
import numpy as np
from concurrent.futures import ProcessPoolExecutor
EX = Path(r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706/analysis/extraction")


def load(n):
    s = importlib.util.spec_from_file_location(n, EX / f"{n}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


G = load("gate_oc_v05")
R = load("gate_rule_v05")
SC = {
    "G10": {},
    "G10 + M-class 0.97": {"G4 M-class": 0.97},
    "G10 + M-anchorG, M-pool 0.95": {"G4 M-anchorG": 0.95, "G4 M-pool": 0.95},
    "G10 + M-class, M-anchorG, M-pool 0.97": {"G4 M-class": 0.97, "G4 M-anchorG": 0.97, "G4 M-pool": 0.97},
    "G10 + K-attr fields 0.97": {"G3 K-attr": 0.97},
}
WATCH = ["G4 M-class", "G4 M-anchorG", "G4 M-pool", "G3 K-attr:held_fixed", "G4 F1_G"]


def job(a):
    key, seed, reps = a
    cfg = G.load_config(G.CONFIG_DEFAULT)
    M = G.Model(cfg)
    grid = json.loads((EX / "bip-grid-v2.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(seed)
    lv = M.levels(extra=SC[key])
    d, b = cfg["design"], cfg["bound"]
    out = []
    for _ in range(reps):
        D, raw = M.gen(rng, 120, lv, 0.10)
        S1 = np.concatenate([np.arange(h * 40, h * 40 + 20) for h in range(3)])
        U = {k: R.neyman_upper(raw[k][0][S1], raw[k][1][S1], rng, R=b["R"], grid=b["theta_grid"], conf=0.80)[0]
             for k in M.icc_metrics}
        n, P, f = R.n_product(R.theta_by_criterion(U, cfg, grid), cfg, grid)
        st = M.stats(D, [np.arange(h * 40, h * 40 + n // 3) for h in range(3)], rng)
        out.append((n, f, bool(M.joint(M.passes(st, n))), [U[w] for w in WATCH]))
    return key, out


if __name__ == "__main__":
    reps, chunks = int(sys.argv[1]), 6
    tasks = [(k, 88000 + 100 * i + c, reps // chunks) for i, k in enumerate(SC) for c in range(chunks)]
    with ProcessPoolExecutor(15) as ex:
        res = list(ex.map(job, tasks))
    agg = {}
    for k, o in res:
        agg.setdefault(k, []).extend(o)
    for k, o in agg.items():
        n = np.array([x[0] for x in o]); f = np.mean([x[1] for x in o]); p = np.mean([x[2] for x in o])
        U = np.array([x[3] for x in o])
        print(f"[{k}] {len(o)} reps: P80 mean n {n.mean():.1f}; share n=120 {np.mean(n == 120):.2f}; P(step 6) {f:.2f}; "
              f"P(pass) {p:.3f}; median U80 " + "; ".join(f"{w} {np.median(U[:, j]):.2f}" for j, w in enumerate(WATCH)))
