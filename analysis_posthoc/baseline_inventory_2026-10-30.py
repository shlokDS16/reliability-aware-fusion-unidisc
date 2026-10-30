"""Baseline inventory (read-only audit, 2026-10-30). CPU only, standard library only, no model, no GPU.

Derives accuracies that are NOT stored as a number in an analysis file, from stored per-item predictions, and cross-checks every
derived number against the number stored elsewhere wherever one exists. Writes analysis_posthoc/baseline_inventory_2026-10-30.out.json.
Run from the repository root:  python -I analysis_posthoc/baseline_inventory_2026-10-30.py
Nothing here is a test or an interval; accuracy = mean of the stored 0/1 decision y (ties wrong, as in the stored files).
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
OUT = {}


def jl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


# ---------------------------------------------------------------- A. fresh fold (Study 2): NONE, GATE-M, LRF
A = {}
for run, conds in (("P2-LRF-L1", ["clean", "jpeg10", "noise0.1", "splice128"]),
                   ("P2-LRF-LG", ["clean", "shot_noise3", "impulse_noise3", "speckle_noise3"])):
    rows = jl(RUNS / run / "predictions.jsonl")
    for c in conds:
        r = [x for x in rows if x["condition"] == c]
        n = len(r)
        A[f"{run}:{c}"] = dict(
            n=n,
            file=f"runs/{run}/predictions.jsonl",
            NONE=sum(x["y_none"] for x in r) / n,
            GATEM=sum(x["y_gatem"] for x in r) / n,
            LRF=sum(x["y_lrf"] for x in r) / n,
        )
        if run == "P2-LRF-L1" and c == "noise0.1":     # length-matched negatives (L-LEN), one item excluded in the stored analysis
            ok = [x for x in r if x.get("neg_len_exact")]
            A[f"{run}:{c}"]["L_variant_rows_with_exact_len"] = len(ok)
            A[f"{run}:{c}"]["NONE_L_all_rows"] = sum(x["y_none_L"] for x in r) / n
            A[f"{run}:{c}"]["LRF_L_all_rows"] = sum(x["y_lrf_L"] for x in r) / n
OUT["fresh_fold"] = A

# cross-check with a6_analysis.json
a6 = json.load(open(RUNS / "P2-LRF-LG" / "a6_analysis.json", encoding="utf-8"))
chk = []
for key, cell in (("P2-LRF-L1:noise0.1", a6["family_L"]["L1"]), ("P2-LRF-L1:jpeg10", a6["family_L"]["L3"]), ("P2-LRF-L1:splice128", a6["family_L"]["L4"]),
                  ("P2-LRF-L1:clean", a6["family_L"]["L-NI"])):
    chk.append((key, "LRF", close(A[key]["LRF"], cell["acc_a"]), "NONE", close(A[key]["NONE"], cell["acc_b"])))
for k, nm in (("shot_noise3", "shot_noise3"), ("impulse_noise3", "impulse_noise3"), ("speckle_noise3", "speckle_noise3")):
    cell = a6["family_LG"]["cells"][nm]
    chk.append((f"P2-LRF-LG:{k}", "LRF", close(A[f"P2-LRF-LG:{k}"]["LRF"], cell["acc_a"]), "NONE", close(A[f"P2-LRF-LG:{k}"]["NONE"], cell["acc_b"])))
sup = a6["family_L"]["supplement_gatem_vs_none"]
for c in ("clean", "jpeg10", "noise0.1", "splice128"):
    chk.append((f"P2-LRF-L1:{c}", "GATEM", close(A[f"P2-LRF-L1:{c}"]["GATEM"], sup[c]["acc_gatem"]), "NONE", close(A[f"P2-LRF-L1:{c}"]["NONE"], sup[c]["acc_none"])))
OUT["fresh_fold_crosscheck_a6"] = [list(x) for x in chk]
assert all(x[2] and x[4] for x in chk), chk

# ---------------------------------------------------------------- B. ablation variants (exploratory): accuracy per variant and cell
abl_rows = jl(RUNS / "P2-LRF-ABL-SCORE" / "predictions_ablation.jsonl")
acc = defaultdict(lambda: defaultdict(list))
for x in abl_rows:
    acc[x["weighting"]][x["cell"]].append(x["y"])
B = {w: {c: dict(n=len(v), acc=sum(v) / len(v)) for c, v in cells.items()} for w, cells in acc.items() if "_s" not in w[-3:]}
ana = json.load(open(RUNS / "P2-LRF-ABL-SCORE" / "ablation_analysis.json", encoding="utf-8"))
mism = []
for r in ana["rows"]:
    for c, v in r["cells"].items():
        if not close(B[r["id"]][c]["acc"], v["acc"]):
            mism.append((r["id"], c))
for ref in ("NONE", "LRF"):
    for c, v in ana["references_accuracy"][ref].items():
        if not close(B[ref][c]["acc"], v):
            mism.append((ref, c))
assert not mism, mism
OUT["ablation_accuracy_crosschecked"] = B

# ---------------------------------------------------------------- C. Study 1 test items (M4, n = 500): accuracy of every arm that stores a decision y
M4 = jl(RUNS / "P2-GATE-M4" / "items.jsonl")
arm_list = ["none", "gate0.05", "gate0.01", "gate0.1", "geo0", "scat0", "topkB", "topks3", "chg"]
C = {}
for cond in ("clean", "jpeg10", "noise0.1", "splice128"):
    C[cond] = {}
    for arm in arm_list:
        ys = []
        for it in M4:
            d = it["conds"].get(cond, {}).get("img", {}).get(arm)
            if d is not None and d.get("y") is not None:
                ys.append(d["y"])
        if ys:
            C[cond][arm] = dict(n=len(ys), acc=sum(ys) / len(ys))
for cond, key in (("jpeg10", "jpeg10_dn"), ("noise0.1", "noise0.1_dn")):
    ys = [it["conds"][key]["img"]["denoised"]["y"] for it in M4 if key in it["conds"] and it["conds"][key]["img"].get("denoised")]
    C[cond]["denoised"] = dict(n=len(ys), acc=sum(ys) / len(ys))
OUT["study1_test_items_M4"] = C
a = json.load(open(RUNS / "P2-GATE-M4" / "analysis.json", encoding="utf-8"))
for cond, k in (("jpeg10", "jpeg"), ("noise0.1", "noise"), ("splice128", "splice")):
    p = a["primary"]["per_corruption"][k]
    assert close(C[cond]["gate0.05"]["acc"], p["acc_a"]) and close(C[cond]["none"]["acc"], p["acc_b"]), (cond, C[cond]["gate0.05"], p)
for cond, k in (("jpeg10", "jpeg"), ("noise0.1", "noise")):
    assert close(C[cond]["denoised"]["acc"], a["s_dn"]["per_corruption"][k]["acc_b"]), cond
OUT["study1_crosscheck"] = "gate0.05 == GATE-M and none == NONE equal analysis.json primary.per_corruption.*.{acc_a,acc_b}; denoised equals s_dn.*.acc_b"


# ---------------------------------------------------------------- D. proposed one-column table: fresh fold, n = 450, four conditions; best and second best among the
# same-evidence rows (external encoders are NOT ranked). Ties share the mark. Accuracy only; nothing here is a test.
CELLS = ["L1_noise0.1", "L1_jpeg10", "L1_splice128", "L1_clean"]
ROWS = {"NONE": "NONE", "GATE-M (fresh fold)": None, "A-UNL": "A-UNL", "A-SF": "A-SF", "A-LIN": "A-LIN", "A-S-BD": "A-S-BD", "A-MIL": "A-MIL", "LRF": "LRF"}
tab = {}
for name, key in ROWS.items():
    if key is None:
        tab[name] = {c: A["P2-LRF-L1:" + c.split("_", 1)[1]]["GATEM"] for c in CELLS}
    else:
        tab[name] = {c: B[key][c]["acc"] for c in CELLS}
rank = {}
for c in CELLS:
    vals = sorted({round(tab[r][c], 12) for r in tab}, reverse=True)
    rank[c] = {r: (1 if round(tab[r][c], 12) == vals[0] else 2 if len(vals) > 1 and round(tab[r][c], 12) == vals[1] else 0) for r in tab}
OUT["proposed_table_rows"] = dict(acc=tab, mark=rank, note="mark 1 = best, 2 = second best among these 8 same-evidence rows; ties share the mark")
json.dump(OUT, open(Path(__file__).with_suffix(".out.json"), "w", encoding="utf-8"), indent=1)
for c in CELLS:
    print(c, {r: (round(tab[r][c], 4), rank[c][r]) for r in tab})


# ---------------------------------------------------------------- E. A-UNL versus NONE: items on which the decisions differ, per cell
_by = defaultdict(dict)
for x in abl_rows:
    if x["weighting"] in ("NONE", "A-UNL"):
        _by[(x["cell"], x["idx"])][x["weighting"]] = x["y"]
_diff = defaultdict(int)
for (c, i), v in _by.items():
    if v["NONE"] != v["A-UNL"]:
        _diff[c] += 1
OUT["A-UNL_vs_NONE_items_with_different_decision"] = dict(_diff)
print("A-UNL vs NONE differing items", dict(_diff))

json.dump(OUT, open(Path(__file__).with_suffix(".out.json"), "w", encoding="utf-8"), indent=1)
print("ok; wrote", Path(__file__).with_suffix(".out.json").name)
for k, v in OUT["fresh_fold"].items():
    print(k, {m: (round(x, 4) if isinstance(x, float) else x) for m, x in v.items()})
for cond, d in OUT["study1_test_items_M4"].items():
    print(cond, {a_: (v["n"], round(v["acc"], 4)) for a_, v in d.items()})
