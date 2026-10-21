"""Revision 2026-10-21 (assessment Q3, Q4): robustness of the RQ2-RQ5 verdicts on the included studies.

Runs rq_analysis.py for its records, strata, weights and verdict rule (its outputs are rewritten unchanged), then
1. per-stratum population size N_h, sampled n_h, extracted records, weight N_h/n_h, and the Kish effective sample
   size of the included column and of each verdict's signed-study domain;
2. a joint threshold grid: direction share x control share x minimum signed studies (5 x 4 x 3 = 60 settings);
3. stratum misclassification: (a) the two language strata merged (one stratum, N = N_short + N_long);
   (b) 1,000 draws that move each language-only sampled study to the other language stratum with probability 0.2
   (the short/long cut is a median file size, the only boundary a study can sit on wrongly);
4. leave-one-out: each included sampled study dropped in turn (post hoc exclusions).
Point estimates only (the verdict rule uses point shares and counts), so no bootstrap is needed here.

    python analysis/extraction/d0052/revision_sensitivity.py
"""
import contextlib
import io
import json
import runpy
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path(str(HERE / "rq_analysis.py"))
G = ns["verdict"].__globals__            # live module namespace
VARS, N_h, recs, UPD = G["VARS"], dict(G["N_h"]), G["recs"], G["UPD"]
done0 = {h: list(G["done"][h]) for h in UPD}
verdict = G["verdict"]
NEED = ["RQ2_better_majority", "RQ2_worse_majority", "RQ2_signed", "RQ2_control",
        "RQ3_anchor_better_majority", "RQ3_anchor_worse_majority", "RQ3_signed", "RQ3_control",
        "RQ4_sweep_up_majority", "RQ4_sweep_down_majority", "RQ4_has_sweep", "RQ4_sweep_control",
        "RQ5_joint_better_majority", "RQ5_joint_worse_majority", "RQ5_signed", "RQ5_control"]
RQS = ("RQ2", "RQ3", "RQ4", "RQ5")
val = {(v, i): VARS[v](recs[i]) for v in NEED for h in UPD for i in done0[h]}


def point(var, done, Nh):
    num_, den_, count = 0.0, 0.0, 0
    for h, ids in done.items():
        a = [val[(var, i)] for i in ids]
        dom = sum(x is not None for x in a)
        k = sum(x is True or x == 1 for x in a if x is not None)
        count += k
        if not ids or dom == 0:
            continue
        w = Nh[h] * dom / len(ids)
        num_ += w * k / dom
        den_ += w
    return {"count": count, "share": (num_ / den_) if den_ else None}


def verdicts(done, Nh, **kw):
    E = {v: point(v, done, Nh) for v in NEED}
    return {rq: verdict(rq, E, **kw)["verdict"] for rq in RQS}


base = verdicts(done0, N_h)
assert base == {rq: G["P"]["verdicts"]["included"][rq]["verdict"] for rq in RQS}, (base, "differs from rq_analysis")
OUT = {"base_verdicts": base}

# 1. strata, weights, effective n
OUT["strata"] = {h: {"N_h": round(N_h[h], 1), "n_extracted": len(done0[h]), "weight": round(N_h[h] / len(done0[h]), 2)}
                 for h in UPD}


def kish(ids_by_h):
    w = [N_h[h] / len(done0[h]) for h, ids in ids_by_h.items() for _ in ids]
    return round(sum(w) ** 2 / sum(x * x for x in w), 1) if w else 0.0


OUT["kish_effective_n_included"] = {"n": sum(len(v) for v in done0.values()), "n_eff": kish(done0)}
SIGNED = {"RQ2": "RQ2_signed", "RQ3": "RQ3_signed", "RQ4": "RQ4_has_sweep", "RQ5": "RQ5_signed"}
OUT["kish_effective_n_signed_domain"] = {}
for rq, var in SIGNED.items():
    dom = {h: [i for i in done0[h] if val[(var, i)] in (True, 1)] for h in UPD}
    OUT["kish_effective_n_signed_domain"][rq] = {"n": sum(len(v) for v in dom.values()), "n_eff": kish(dom),
                                                  "by_stratum": {h: len(v) for h, v in dom.items()}}

# 2. joint threshold grid
grid = []
for ds in (0.55, 0.60, 2 / 3, 0.75, 0.80):
    for cs in (0.30, 0.40, 0.50, 0.60):
        for ms in (3, 5, 8):
            v = verdicts(done0, N_h, min_signed=ms, direction_share=ds, control_share=cs)
            grid.append({"direction_share": round(ds, 3), "control_share": cs, "min_signed": ms, "verdicts": v})
OUT["threshold_grid"] = {
    "n_settings": len(grid),
    "verdict_counts": {rq: dict(Counter(g["verdicts"][rq] for g in grid)) for rq in RQS},
    "settings_with_any_well_supported": sum(any(x == "well supported" for x in g["verdicts"].values()) for g in grid),
    "settings_identical_to_base": sum(g["verdicts"] == base for g in grid),
    "grid": grid}

# 3a. language strata merged
merged = {"G-mm": done0["G-mm"], "G-lang": done0["G-short"] + done0["G-long"]}
Nm = {"G-mm": N_h["G-mm"], "G-lang": N_h["G-short"] + N_h["G-long"]}
OUT["misclass_merged_language_strata"] = verdicts(merged, Nm)
# 3b. random swaps between the language strata
rng = np.random.default_rng(20261021)
changes = Counter()
for _ in range(1000):
    d = {"G-mm": done0["G-mm"], "G-short": [], "G-long": []}
    for h in ("G-short", "G-long"):
        o = "G-long" if h == "G-short" else "G-short"
        for i in done0[h]:
            d[o if rng.random() < 0.2 else h].append(i)
    v = verdicts(d, N_h)
    changes.update(f"{rq}: {base[rq]} -> {v[rq]}" for rq in RQS if v[rq] != base[rq])
    changes["draws_any_change"] += any(v[rq] != base[rq] for rq in RQS)
OUT["misclass_random_swaps"] = {"draws": 1000, "p_swap": 0.2, "seed": 20261021, "changes": dict(changes)}

# 4. leave one out
loo = Counter()
for h in UPD:
    for i in done0[h]:
        d = {k: [x for x in v if x != i] for k, v in done0.items()}
        v = verdicts(d, N_h)
        for rq in RQS:
            if v[rq] != base[rq]:
                loo[f"{rq}: {base[rq]} -> {v[rq]}"] += 1
OUT["leave_one_out"] = {"n_runs": sum(len(v) for v in done0.values()), "changes": dict(loo)}

(HERE / "revision-sensitivity.json").write_text(json.dumps(OUT, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in OUT.items() if k != "threshold_grid"}, indent=1))
print(json.dumps({k: v for k, v in OUT["threshold_grid"].items() if k != "grid"}, indent=1))
