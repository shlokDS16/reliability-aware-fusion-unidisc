"""Agreement of the first author's blind check with the final extraction records (pairs human_check_sheet.py).

    python -E -P analysis/extraction/d0052/human_check_agreement.py      -> human-check-agreement.json

Reads research/HUMAN-CHECK-2026-10-21.xlsx as filled by the author and human-check-model-answers.json. Per question
and overall: pairs where both answered yes or no, raw agreement and Cohen's kappa; 'unclear' and 'NA' answers are
counted separately and left out of the agreement. The model answer 'unclear' (QA sub-items) is treated the same way.
"""
import json
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "analysis/extraction/d0052"
M = json.load(open(D / "human-check-model-answers.json", encoding="utf-8"))
ws = openpyxl.load_workbook(ROOT / "research/HUMAN-CHECK-2026-10-21.xlsx").active
hdr = [c.value for c in ws[1]]
human = {}
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[1]:
        human[row[1]] = {q: (str(row[hdr.index(q)]).strip().lower() if row[hdr.index(q)] else "") for q in M["questions"]}


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a == "yes" for a, _ in pairs) / n
    pb = sum(b == "yes" for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


out = {"filled": sum(1 for h in human.values() if any(h.values())), "of": len(M["answers"]), "per_question": {}}
allp = []
for q in M["questions"]:
    pairs, other = [], 0
    for i, m in M["answers"].items():
        h = human.get(i, {}).get(q, "")
        if h in ("yes", "no") and m[q] in ("yes", "no"):
            pairs.append((h, m[q]))
        elif h:
            other += 1
    allp += pairs
    out["per_question"][q] = {"pairs": len(pairs), "agree": sum(a == b for a, b in pairs), "kappa": kappa(pairs),
                              "unclear_or_na": other}
out["overall"] = {"pairs": len(allp), "agree": sum(a == b for a, b in allp), "kappa": kappa(allp)}
# 95 percent percentile bootstrap of the overall kappa, resampling studies (pairs stay with their study); added 2026-10-21
import random
by = {}
for i, m in M["answers"].items():
    p = [(human.get(i, {}).get(q, ""), m[q]) for q in M["questions"]]
    p = [(h, v) for h, v in p if h in ("yes", "no") and v in ("yes", "no")]
    if p:
        by[i] = p
ids = sorted(by)
rng = random.Random(20261022)
ks = sorted(k for k in (kappa([x for _ in ids for x in by[ids[rng.randrange(len(ids))]]]) for _ in range(2000)) if k is not None)
out["overall"].update({"studies": len(ids), "kappa_ci95": [ks[int(0.025 * (len(ks) - 1))], ks[int(0.975 * (len(ks) - 1))]] if ks else None,
                       "bootstrap": {"reps": 2000, "seed": 20261022, "valid_draws": len(ks), "unit": "study"}})
(D / "human-check-agreement.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out["overall"]), "filled", out["filled"], "of", out["of"])
