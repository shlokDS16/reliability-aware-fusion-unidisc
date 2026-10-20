"""Summary tables of gate design B-IP v0.5 for EXTRACTION-PLAN-v0.5 s10.6-s10.7 (red-team audit 4, MA1). Reads
gate_bip_v05-results.json, bip-grid-v2.json and the config; simulates nothing new. Not a result about any paper.

Prints:
  (1) per scenario and sizing rule: P(pass), MC s.e., mean n, expected gate cost, P(step 6);
  (2) reachability: the product of the grid marginals at the scenario's TRUE ICC vector at n = 120 (the best any
      rule capped at 120 can do, by the product approximation whose error on the common-ICC grid is at most
      0.011, gate_oc_v05-grid-log.txt);
  (3) the selection of the binding rule by the criterion fixed before the simulation was run (plan v0.5 s10.7):
      among P80, P50 and X80, the rules with P(pass | good) >= 0.85 - 2 MC s.e. in every good scenario whose
      reachability is >= 0.85, and P(step 6) >= 0.80 in every good scenario whose reachability is < 0.85, and
      max P(pass | one bad) <= 0.08; of these, the one with the smallest mean n averaged over the good scenarios;
  (4) the alternative 'M-sign gated' (OQ5-02): product approximation at the true ICC vector with M-sign's
      marginal included, n = 60 and 120.
Run from the worktree root: python -E -P analysis/extraction/gate_bip_v05_summary.py
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    G = _load("gate_oc_v05")
    BIP = _load("gate_bip_v05")
    cfg = G.load_config(G.CONFIG_DEFAULT)
    M = G.Model(cfg)
    grid = json.loads((HERE / "bip-grid-v2.json").read_text(encoding="utf-8"))
    res = json.loads((HERE / "gate_bip_v05-results.json").read_text(encoding="utf-8"))
    assert res["model_sha256"] == grid["model_sha256"] == G.model_sha(cfg)
    print(f"results sha256 {hashlib.sha256((HERE / 'gate_bip_v05-results.json').read_bytes()).hexdigest()[:16]}; grid sha256 "
          f"{hashlib.sha256((HERE / 'bip-grid-v2.json').read_bytes()).hexdigest()[:16]}; config sha256 {cfg['_sha256'][:16]}")
    S = {s[0]: s for s in BIP.scenarios(M)}
    t = np.asarray(grid["theta"], float)
    ns = grid["n"]

    def marg(c, th, n):
        return float(np.interp(min(max(th, t[0]), t[-1]), t, [row[ns.index(n)] for row in grid["marginal"][c]]))

    def reach(key, n, with_sign=False):
        _, _, levels, icc, nb_k = S[key]
        crit = list(M.gated) + (["G4 M-sign"] if with_sign else [])
        p = 1.0
        for c in crit:
            q = M.Q[c]
            if q["kind"] == "kattr":
                th = max(M.ic(icc, f"{c}:{f}", parent=c) for f in M.fields)
            elif q["kind"] == "count":
                th = t[0]
            elif q["kind"] == "kappa":
                th = max(M.ic(icc, k) for k in q["icc_from"])
            else:
                th = M.ic(icc, c)
            p *= marg(c, th, n)
        return p

    good = [k for k in res["scenarios"] if not k.startswith("B")]
    bad = [k for k in res["scenarios"] if k.startswith("B")]
    rules = ("P80", "P50", "X80", "V4")
    print("\n(1)-(2) P(pass | every quantity good) by rule [MC s.e.], mean n; reachability at n 120 (product approximation; "
          "NB 0.7 scenario: grid made with NB 1.5, approximate)")
    print("  scenario  reach120 | " + " | ".join(f"{r}: P [se] mean n, P(step6)" for r in rules))
    for k in good:
        sc = res["scenarios"][k]
        cells = []
        for r in rules:
            x = sc[r]
            s6 = f", {x['p_step6']:.2f}" if x["p_step6"] is not None else ""
            cells.append(f"{r}: {x['p_pass']:.3f} [{x['se']:.3f}] {x['mean_n']:.1f}{s6}")
        print(f"  {k:<9} {reach(k, 120):.3f}    | " + " | ".join(cells))
    print("\n    P(pass | one quantity bad, others good) by rule (mean n)")
    for k in bad:
        sc = res["scenarios"][k]
        print(f"  {k:<16} " + " | ".join(f"{r}: {sc[r]['p_pass']:.3f} ({sc[r]['mean_n']:.1f})" for r in rules))

    print("\n(3) Selection of the binding rule (criterion fixed before the run; plan v0.5 s10.7)")
    ok = {}
    for r in ("P80", "P50", "X80"):
        fails = []
        for k in good:
            x = res["scenarios"][k][r]
            if reach(k, 120) >= 0.85 and x["p_pass"] < 0.85 - 2 * x["se"]:
                fails.append(f"{k} P {x['p_pass']:.3f}")
            if reach(k, 120) < 0.85 and (x["p_step6"] if x["p_step6"] is not None else 0) < 0.80 and r != "X80":
                fails.append(f"{k} step6 {x['p_step6']:.2f}")
        mb = max(res["scenarios"][k][r]["p_pass"] for k in bad)
        if mb > 0.08:
            fails.append(f"max one-bad {mb:.3f}")
        mn = float(np.mean([res["scenarios"][k][r]["mean_n"] for k in good]))
        ok[r] = (not fails, mn)
        print(f"  {r}: {'meets' if not fails else 'fails'} the criterion" + (f" ({'; '.join(fails)})" if fails else "")
              + f"; max P(pass | one bad) {mb:.3f}; mean n over the good scenarios {mn:.1f}")
    cand = [r for r in ok if ok[r][0]]
    pick = min(cand, key=lambda r: ok[r][1]) if cand else None
    print(f"  selected: {pick}")
    if pick:
        pg = [res["scenarios"][k][pick]["p_pass"] for k in good]
        het = [k for k in good if k not in ("G05", "G10", "G20", "G30")]
        print(f"  {pick}: P(pass | good) {min(pg):.3f}-{max(pg):.3f} over all good scenarios; over the heterogeneous ones "
              f"({', '.join(het)}) {min(res['scenarios'][k][pick]['p_pass'] for k in het):.3f}-"
              f"{max(res['scenarios'][k][pick]['p_pass'] for k in het):.3f}; max P(pass | one bad) "
              f"{max(res['scenarios'][k][pick]['p_pass'] for k in bad):.3f} "
              f"({max(bad, key=lambda k: res['scenarios'][k][pick]['p_pass'])})")

    print("\n(4) Alternative: M-sign gated (good 0.97, bad 0.90, line 0.92, counted over sign decisions), product "
          "approximation at the true ICC vector")
    for k in good:
        print(f"  {k:<9} n 60: {reach(k, 60, True):.3f} (without M-sign {reach(k, 60):.3f}); n 120: {reach(k, 120, True):.3f} "
              f"(without {reach(k, 120):.3f})")
    print("  M-sign marginal at n 120 by ICC: " + "; ".join(f"{th:.2f} {marg('G4 M-sign', th, 120):.3f}" for th in grid["theta"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
