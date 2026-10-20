"""Red-team v0.5 scratch: is the product approximation ('reach') biased in heterogeneous scenarios?
Simulates the fixed-n gate at n=90 and 120 at the scenario's true ICC vector with the committed model
(gate_oc_v05.simulate, read-only import) and compares each gated marginal with the grid marginal at its theta_c."""
import importlib.util, json
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
SC = {"H10": {"G4 M-sign": 0.6, "G4 M-pool": 0.6, "G4 M-anchorG": 0.3, "_": 0.10},
      "HG": {"G4 M-anchorG": 0.4, "G4 M-pool": 0.4, "G4 M-class": 0.4, "_": 0.10},
      "HP": {"G4 M-pool": 0.5, "_": 0.05},
      "F60": {"G4 F1_G": 0.6, "_": 0.05}}


def job(a):
    key, n, seed = a
    cfg = G.load_config(G.CONFIG_DEFAULT)
    M = G.Model(cfg)
    st = G.simulate(cfg, n, M.levels(), 1000, seed, icc=SC[key])
    return key, n, M.passes(st, n)


if __name__ == "__main__":
    cfg = G.load_config(G.CONFIG_DEFAULT)
    M = G.Model(cfg)
    grid = json.loads((EX / "bip-grid-v2.json").read_text(encoding="utf-8"))
    t = np.asarray(grid["theta"])
    ns = grid["n"]
    tasks = [(k, n, 77000 + 10 * i + j + 100 * c) for i, k in enumerate(SC) for j, n in enumerate((90, 120)) for c in range(2)]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(job, tasks))
    agg = {}
    for k, n, ps in res:
        agg.setdefault((k, n), []).append(ps)
    for (k, n), L in agg.items():
        ps = np.concatenate(L)
        icc = SC[k]
        joint = M.joint(ps).mean()
        prod_sim = np.prod([ps[:, M.names.index(c)].mean() for c in M.gated])

        def th(c):
            q = M.Q[c]
            if q["kind"] == "kattr":
                return max(M.ic(icc, f"{c}:{f}", parent=c) for f in M.fields)
            if q["kind"] == "count":
                return t[0]
            if q["kind"] == "kappa":
                return max(M.ic(icc, x) for x in q["icc_from"])
            return M.ic(icc, c)
        gm = {c: float(np.interp(th(c), t, [r[ns.index(n)] for r in grid["marginal"][c]])) for c in M.gated}
        reach = np.prod(list(gm.values()))
        print(f"{k} n {n}: simulated joint {joint:.3f} ({len(ps)} gates, se {np.sqrt(joint * (1 - joint) / len(ps)):.3f}); "
              f"product of simulated marginals {prod_sim:.3f}; grid product ('reach') {reach:.3f}")
        for c in M.gated:
            s = ps[:, M.names.index(c)].mean()
            if abs(s - gm[c]) > 0.01:
                print(f"    {c}: simulated marginal {s:.3f} vs grid marginal at theta {th(c):.2f}: {gm[c]:.3f}")
