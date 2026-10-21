"""Agreement of the blind human screening check with the final model decisions (pairs human_check_screening_sheet.py).

    python -E -P analysis/screening/human_check_screening_agreement.py [--sheets A.xlsx B.xlsx ...] [--out file.json]

Default sheets: research/HUMAN-CHECK-SCREENING.xlsx plus any research/HUMAN-CHECK-SCREENING-*.xlsx (a second reader's
copy). A second reader may also add a row at the bottom of the main sheet with the same Record id. Every filled row is
one reading (reader, record, decision, code). The human answer compared with the model is the first reading of a
record (main sheet first, top to bottom); every reader is also compared with the model on their own rows.

Writes analysis/screening/human-check-screening-agreement.json:
  decision  include/exclude pairs, raw agreement, Cohen's kappa with a percentile bootstrap 95 percent interval
            (records resampled with replacement, 2000 draws, seed 20261023), the 2x2 table
  unclear   'unclear' readings, counted apart and left out of the agreement
  code      exclusion-code agreement on records both the human and the model call exclude
  human_human  agreement between two readers on records both read (decision and code)
  filled    rows and records filled, by reader
"""
import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "analysis/screening"
SEED, REPS = 20261023, 2000
CODES = {"X8", "X3", "X5", "X4", "X0", "X1", "X2", "X7"}

ap = argparse.ArgumentParser()
ap.add_argument("--sheets", nargs="*")
ap.add_argument("--answers", default=str(S / "human-check-screening-model-answers.json"))
ap.add_argument("--out", default=str(S / "human-check-screening-agreement.json"))
a = ap.parse_args()
sheets = [Path(p) for p in a.sheets] if a.sheets else (
    [ROOT / "research/HUMAN-CHECK-SCREENING.xlsx"] + sorted((ROOT / "research").glob("HUMAN-CHECK-SCREENING-*.xlsx")))
M = json.load(open(a.answers, encoding="utf-8"))
model = M["answers"]


def norm(v):
    return str(v).strip() if v is not None else ""


readings, warnings = [], []
for p in sheets:
    ws = openpyxl.load_workbook(p, data_only=True)["check"]
    hdr = [norm(c.value) for c in ws[1]]
    col = {h: hdr.index(h) for h in ("Record id", "Decision", "Exclusion code", "Reader", "Notes")}
    for k, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        i = norm(row[col["Record id"]])
        dec = norm(row[col["Decision"]]).lower()
        code = norm(row[col["Exclusion code"]]).upper()
        reader = norm(row[col["Reader"]]).upper() or "?"
        if not i or not (dec or code):
            continue
        if i not in model:
            warnings.append(f"{p.name} row {k}: {i} is not a drawn record")
            continue
        if dec not in ("include", "exclude", "unclear"):
            warnings.append(f"{p.name} row {k} {i}: decision '{dec}' not include/exclude/unclear")
            continue
        if code and code not in CODES:
            warnings.append(f"{p.name} row {k} {i}: code '{code}' not a valid code; ignored")
            code = ""
        if dec == "exclude" and not code:
            warnings.append(f"{p.name} row {k} {i}: exclude without a code")
        if dec != "exclude" and code:
            warnings.append(f"{p.name} row {k} {i}: code {code} given with '{dec}'; code ignored")
            code = ""
        readings.append({"sheet": p.name, "row": k, "id": i, "reader": reader, "decision": dec, "code": code})

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


def boot_ci(pairs):
    if not pairs:
        return None, 0
    rng = random.Random(SEED)
    ks = [k for k in (kappa([pairs[rng.randrange(len(pairs))] for _ in pairs]) for _ in range(REPS)) if k is not None]
    if not ks:
        return None, 0
    ks.sort()
    return [ks[int(0.025 * (len(ks) - 1))], ks[int(0.975 * (len(ks) - 1))]], len(ks)


def vs_model(rs):
    pairs = [(r["decision"], model[r["id"]]["decision"]) for r in rs if r["decision"] in ("include", "exclude")]
    unclear = [r for r in rs if r["decision"] == "unclear"]
    ci, valid = boot_ci(pairs)
    tab = Counter(f"human_{h}_model_{m}" for h, m in pairs)
    both_exc = [r for r in rs if r["decision"] == "exclude" and model[r["id"]]["decision"] == "exclude"]
    coded = [r for r in both_exc if r["code"]]
    return {
        "decision": {"pairs": len(pairs), "agree": sum(h == m for h, m in pairs),
                     "agreement": (sum(h == m for h, m in pairs) / len(pairs)) if pairs else None,
                     "kappa": kappa(pairs), "kappa_ci95": ci,
                     "bootstrap": {"reps": REPS, "seed": SEED, "valid_draws": valid, "method": "percentile, records resampled"},
                     "table": {k: tab.get(k, 0) for k in ("human_include_model_include", "human_include_model_exclude",
                                                          "human_exclude_model_include", "human_exclude_model_exclude")},
                     "human_include_model_exclude": [r["id"] for r in rs if r["decision"] == "include" and model[r["id"]]["decision"] == "exclude"],
                     "human_exclude_model_include": [r["id"] for r in rs if r["decision"] == "exclude" and model[r["id"]]["decision"] == "include"]},
        "unclear": {"n": len(unclear), "model_include": sum(model[r["id"]]["decision"] == "include" for r in unclear),
                    "model_exclude": sum(model[r["id"]]["decision"] == "exclude" for r in unclear),
                    "ids": [r["id"] for r in unclear]},
        "code": {"both_exclude": len(both_exc), "with_human_code": len(coded),
                 "agree": sum(r["code"] == model[r["id"]]["code"] for r in coded),
                 "agreement": (sum(r["code"] == model[r["id"]]["code"] for r in coded) / len(coded)) if coded else None,
                 "kappa": kappa([(r["code"], model[r["id"]]["code"]) for r in coded]),
                 "disagreements": [{"id": r["id"], "human": r["code"], "model": model[r["id"]]["code"]}
                                   for r in coded if r["code"] != model[r["id"]]["code"]]},
    }


out = {"sheets": [str(p) for p in sheets], "answers": a.answers, "of": len(model),
       "filled": {"readings": len(readings), "records": len(first),
                  "by_reader": dict(Counter(r["reader"] for r in readings)),
                  "include_stratum": sum(model[i]["decision"] == "include" for i in first),
                  "exclude_stratum": sum(model[i]["decision"] == "exclude" for i in first)},
       "primary": "first reading of each record (main sheet first, top to bottom)"}
out.update(vs_model(list(first.values())))
by_reader = defaultdict(list)
for r in readings:
    by_reader[r["reader"]].append(r)
out["per_reader"] = {k: {kk: vv for kk, vv in vs_model(v).items()} for k, v in by_reader.items()} if len(by_reader) > 1 else {}

# human-human: records read by two different readers (first reading per reader)
per = defaultdict(dict)
for r in readings:
    per[r["id"]].setdefault(r["reader"], r)
hh_dec, hh_code, overlap = [], [], []
for i, d in per.items():
    rs = list(d.values())
    if len(rs) >= 2:
        x, y = rs[0], rs[1]
        overlap.append({"id": i, "readers": [x["reader"], y["reader"]], "decisions": [x["decision"], y["decision"]],
                        "codes": [x["code"], y["code"]]})
        if x["decision"] in ("include", "exclude") and y["decision"] in ("include", "exclude"):
            hh_dec.append((x["decision"], y["decision"]))
        if x["decision"] == y["decision"] == "exclude" and x["code"] and y["code"]:
            hh_code.append((x["code"], y["code"]))
ci, valid = boot_ci(hh_dec)
out["human_human"] = {"overlap_records": len(overlap),
                      "decision_pairs": len(hh_dec), "decision_agree": sum(x == y for x, y in hh_dec),
                      "decision_kappa": kappa(hh_dec), "decision_kappa_ci95": ci, "bootstrap_valid_draws": valid,
                      "code_pairs": len(hh_code), "code_agree": sum(x == y for x, y in hh_code),
                      "unclear_in_overlap": sum("unclear" in o["decisions"] for o in overlap), "rows": overlap}
out["warnings"] = warnings
Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
d = out["decision"]
print(f"filled {out['filled']['records']} of {out['of']} records ({out['filled']['readings']} readings); "
      f"decision pairs {d['pairs']} agree {d['agree']} kappa {d['kappa']} CI {d['kappa_ci95']}; "
      f"unclear {out['unclear']['n']}; code {out['code']['agree']}/{out['code']['with_human_code']}; "
      f"human-human overlap {out['human_human']['overlap_records']}; warnings {len(warnings)}")
