"""Agreement of the blind human census check with the adjudicated census rows (pairs human_check_census_sheet.py).

    python -E -P analysis/census/human_check_census_agreement.py [--sheets A.xlsx B.xlsx ...] [--out file.json]

Default sheets: research/HUMAN-CHECK-CENSUS.xlsx plus any research/HUMAN-CHECK-CENSUS-*.xlsx (a second reader's copy);
a second reader may also add a row at the bottom of the main sheet with the same Paper id. The human answer compared
with the census is the first reading of a paper (main sheet first, top to bottom).

Per question: pairs where neither side is 'unclear' or blank, raw agreement, Cohen's kappa with a percentile bootstrap
95 percent interval (papers resampled, 2000 draws, seed 20261024), the cross table; 'unclear' counted apart.
  Q2 value-rule class (non-plain / plain / not stated), also as the census claim's split (non-plain or not stated
     vs plain), and agreement weighted back to the frame (the draw oversampled plain); optional letters compared
     with the census F2 code
  Q1 headline right (share yes)    Q3 diversity (census F3)    Q4 step sweep (census F4; also yes-or-partial vs no)
Human-human agreement on papers two readers both read. Writes analysis/census/human-check-census-agreement.json.
"""
import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "analysis/census"
SEED, REPS = 20261024, 2000
COLS = {"Q1": "Q1 Headline right?", "Q2": "Q2 Value rule", "L": "Q2 Letters (optional)", "Q3": "Q3 Diversity",
        "Q4": "Q4 Step sweep"}
VALID = {"Q1": {"yes", "no", "unclear"}, "Q2": {"non-plain", "plain", "not stated", "unclear"},
         "Q3": {"yes", "no", "unclear"}, "Q4": {"yes", "partial", "no", "unclear"}}

ap = argparse.ArgumentParser()
ap.add_argument("--sheets", nargs="*")
ap.add_argument("--answers", default=str(D / "human-check-census-model-answers.json"))
ap.add_argument("--out", default=str(D / "human-check-census-agreement.json"))
a = ap.parse_args()
sheets = [Path(p) for p in a.sheets] if a.sheets else (
    [ROOT / "research/HUMAN-CHECK-CENSUS.xlsx"] + sorted((ROOT / "research").glob("HUMAN-CHECK-CENSUS-*.xlsx")))
M = json.load(open(a.answers, encoding="utf-8"))
model = M["answers"]
frame_n, sample_n = M["frame_class_counts"], M["sizes"]


def norm(v):
    return str(v).strip() if v is not None else ""


readings, warnings = [], []
for p in sheets:
    ws = openpyxl.load_workbook(p, data_only=True)["check"]
    hdr = [norm(c.value) for c in ws[1]]
    ci = {k: hdr.index(v) for k, v in COLS.items()}
    ci["id"], ci["reader"] = hdr.index("Paper id"), hdr.index("Reader")
    for k, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        i = norm(row[ci["id"]])
        ans = {q: norm(row[ci[q]]).lower() for q in VALID}
        letters = norm(row[ci["L"]]).upper().replace(" ", "")
        if not i or not (any(ans.values()) or letters):
            continue
        if i not in model:
            warnings.append(f"{p.name} row {k}: {i} is not a drawn paper")
            continue
        for q, v in ans.items():
            if v and v not in VALID[q]:
                warnings.append(f"{p.name} row {k} {i}: {q} '{v}' not allowed; ignored")
                ans[q] = ""
        readings.append({"sheet": p.name, "row": k, "id": i, "reader": norm(row[ci["reader"]]).upper() or "?",
                         "letters": letters, **ans})

first = {}
for r in readings:
    first.setdefault(r["id"], r)


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(x == y for x, y in pairs) / n
    cats = {x for p in pairs for x in p}
    pe = sum((sum(x == c for x, _ in pairs) / n) * (sum(y == c for _, y in pairs) / n) for c in cats)
    return None if pe == 1 else (po - pe) / (1 - pe)


def boot(pairs):
    if not pairs:
        return None, 0
    rng = random.Random(SEED)
    ks = sorted(k for k in (kappa([pairs[rng.randrange(len(pairs))] for _ in pairs]) for _ in range(REPS)) if k is not None)
    return ([ks[int(0.025 * (len(ks) - 1))], ks[int(0.975 * (len(ks) - 1))]], len(ks)) if ks else (None, 0)


def stat(pairs):
    ci, valid = boot(pairs)
    return {"pairs": len(pairs), "agree": sum(x == y for x, y in pairs),
            "agreement": sum(x == y for x, y in pairs) / len(pairs) if pairs else None,
            "kappa": kappa(pairs), "kappa_ci95": ci, "bootstrap_valid_draws": valid,
            "table_human_vs_census": {f"{x} | {y}": c for (x, y), c in sorted(Counter(pairs).items())}}


MODEL_KEY = {"Q2": "class", "Q3": "F3", "Q4": "F4"}


def vs_census(rs):
    o = {}
    for q in ("Q2", "Q3", "Q4"):
        prs = [(r[q], model[r["id"]][MODEL_KEY[q]]) for r in rs if r[q] and r[q] != "unclear"]
        o[q] = stat(prs)
        o[q]["unclear"] = [r["id"] for r in rs if r[q] == "unclear"]
        o[q]["disagreements"] = [{"id": r["id"], "human": r[q], "census": model[r["id"]][MODEL_KEY[q]]}
                                 for r in rs if r[q] and r[q] != "unclear" and r[q] != model[r["id"]][MODEL_KEY[q]]]
    bi = lambda v: "plain" if v == "plain" else "non-plain or not stated"
    o["Q2_claim_split"] = stat([(bi(r["Q2"]), bi(model[r["id"]]["class"])) for r in rs if r["Q2"] and r["Q2"] != "unclear"])
    # agreement weighted back to the frame: each census class weighted by frame share / sample share
    w_num = w_den = 0.0
    for r in rs:
        if r["Q2"] and r["Q2"] != "unclear":
            c = model[r["id"]]["class"]
            w = frame_n[c] / sample_n[c]
            w_den += w
            w_num += w * (r["Q2"] == c)
    o["Q2"]["agreement_frame_weighted"] = w_num / w_den if w_den else None
    sweep = lambda v: "yes or partial" if v in ("yes", "partial") else v
    o["Q4_yes_or_partial_vs_no"] = stat([(sweep(r["Q4"]), sweep(model[r["id"]]["F4"])) for r in rs
                                         if r["Q4"] and r["Q4"] != "unclear"])
    q1 = [r["Q1"] for r in rs if r["Q1"]]
    o["Q1"] = {"answered": len(q1), "yes": q1.count("yes"), "no": q1.count("no"), "unclear": q1.count("unclear"),
               "no_ids": [r["id"] for r in rs if r["Q1"] == "no"]}
    lt = [r for r in rs if r["letters"]]
    st = lambda s: {t for t in s.split("+") if t}
    o["Q2_letters"] = {"given": len(lt), "exact_match": sum(st(r["letters"]) == st(model[r["id"]]["F2_codes"]) for r in lt),
                       "rows": [{"id": r["id"], "human": r["letters"], "census": model[r["id"]]["F2_codes"]} for r in lt]}
    return o


out = {"sheets": [str(p) for p in sheets], "answers": a.answers, "of": len(model),
       "filled": {"readings": len(readings), "papers": len(first), "by_reader": dict(Counter(r["reader"] for r in readings)),
                  "by_census_class": dict(Counter(model[i]["class"] for i in first))},
       "primary": "first reading of each paper (main sheet first, top to bottom)",
       "weights": {"frame_class_counts": frame_n, "sample_sizes": sample_n}}
out.update(vs_census(list(first.values())))
byr = defaultdict(list)
for r in readings:
    byr[r["reader"]].append(r)
out["per_reader"] = {k: vs_census(v) for k, v in byr.items()} if len(byr) > 1 else {}
per = defaultdict(dict)
for r in readings:
    per[r["id"]].setdefault(r["reader"], r)
hh = {"overlap_papers": 0}
for q in ("Q2", "Q3", "Q4"):
    prs = []
    for d in per.values():
        rs = list(d.values())
        if len(rs) >= 2 and rs[0][q] and rs[1][q] and "unclear" not in (rs[0][q], rs[1][q]):
            prs.append((rs[0][q], rs[1][q]))
    hh[q] = stat(prs)
hh["overlap_papers"] = sum(len(d) >= 2 for d in per.values())
out["human_human"] = hh
out["warnings"] = warnings
Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
q2 = out["Q2"]
print(f"filled {out['filled']['papers']} of {out['of']} ({out['filled']['readings']} readings); Q2 {q2['agree']}/{q2['pairs']} "
      f"kappa {q2['kappa']} CI {q2['kappa_ci95']} weighted {q2['agreement_frame_weighted']}; claim split kappa "
      f"{out['Q2_claim_split']['kappa']}; Q3 kappa {out['Q3']['kappa']}; Q4 kappa {out['Q4']['kappa']}; "
      f"Q1 yes {out['Q1']['yes']}/{out['Q1']['answered']}; overlap {hh['overlap_papers']}; warnings {len(warnings)}")
