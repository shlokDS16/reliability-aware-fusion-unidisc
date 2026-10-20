"""EA vs EB agreement on the 8 second-reader ids of D0054 (plan v0.2 s10.2-s10.4), with agreement.py in stage-a mode.

    python -I analysis/extraction/d0052/gather_pairs.py
    python -I analysis/extraction/d0052/agreement_8.py          -> writes ec-input/manifest-8.json and validator-8.jsonl
    python -E -P analysis/extraction/agreement.py --mode stage-a --x analysis/extraction/d0052/ec-input/EA-pairs.jsonl
        --y analysis/extraction/d0052/ec-input/EB-pairs.jsonl --manifest analysis/extraction/d0052/ec-input/manifest-8.json
        --lookups analysis/extraction/lookups --validator analysis/extraction/d0052/ec-input/validator-8.jsonl
        --config analysis/extraction/gate-config-v05.json --texts <folder with the 8 texts> --out analysis/extraction/d0052/agreement-8-texts
    (agreement-8 is the same run without --texts: headline units then match by quote and F1_H drops to 2/52; the
    canonical run is agreement-8-texts, with the five pymupdf texts and the three census-text-paged texts in one folder)

The manifest is a stage-a shaped wrapper (no worked examples; every id "drawn"); strata are the D0054 strata.
The validator file is the first-pass lines (validate-pass1.jsonl) of the 8 ids, as agreement.py defines first pass.
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ss = json.load(open(D / "seed-sample.json", encoding="utf-8"))
ids = ss["second_reader_ids"]
strata = json.load(open(D / "sample.json", encoding="utf-8"))["strata"]
stratum = {}
for i in ids:
    hit = [s for s, L in strata.items() if i in L]
    stratum[i] = hit[0] if hit else ("S-seed" if i in ss["seed_ids"] else None)
assert all(stratum.values()), stratum
order = sorted(set(stratum.values()))
man = {"stage": "stage-a", "ids": ids, "stratum": stratum, "strata_order": order, "worked_examples": [],
       "drawn": ids, "note": "D0054 second-reader ids; stage-a wrapper for agreement.py (agreement_8.py)"}
(D / "ec-input").mkdir(exist_ok=True)
(D / "ec-input" / "manifest-8.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
rows = [l for l in open(D / "validate-pass1.jsonl", encoding="utf-8") if l.strip() and json.loads(l)["id"] in ids]
(D / "ec-input" / "validator-8.jsonl").write_text("".join(rows), encoding="utf-8")
print(stratum, len(rows), "validator lines")
