"""EA vs EB agreement on the 2 landmark second-reader ids (second-reader.json), as d0052/agreement_8.py does for the 8.

    python -I analysis/extraction/lmk/agreement_2.py      -> ec-input/EA-pairs.jsonl, EB-pairs.jsonl, manifest-2.json,
                                                             validator-2.jsonl
    python -E -P analysis/extraction/agreement.py --mode stage-a --x analysis/extraction/lmk/ec-input/EA-pairs.jsonl
        --y analysis/extraction/lmk/ec-input/EB-pairs.jsonl --manifest analysis/extraction/lmk/ec-input/manifest-2.json
        --lookups analysis/extraction/lookups --validator analysis/extraction/lmk/ec-input/validator-2.jsonl
        --config analysis/extraction/gate-config-v05.json --texts research/sources/md/fulltext-pymupdf
        --out analysis/extraction/lmk/agreement-2

EA and EB records are the final pass of each session (pass 2 when the session was returned once, else pass 1); the
validator file is the first-pass lines of the 2 ids from both extractors.
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ids = json.load(open(D / "second-reader.json", encoding="utf-8"))["ids"]


def final(role):
    out = {}
    for folder in sorted((D / role).glob("*")):
        files = sorted(folder.glob(f"{role}-*.jsonl"))
        p2 = [f for f in files if f.stem.endswith("-pass2")]
        for f in (p2 or [f for f in files if not f.stem.endswith("-pass2")]):
            for l in open(f, encoding="utf-8"):
                if l.strip().startswith("{"):
                    r = json.loads(l)
                    if r["id"] in ids:
                        out[r["id"]] = l.strip()
    return out


(D / "ec-input").mkdir(exist_ok=True)
for role in ("EA", "EB"):
    recs = final(role)
    assert set(recs) == set(ids), (role, sorted(recs))
    (D / "ec-input" / f"{role}-pairs.jsonl").write_text("".join(recs[i] + "\n" for i in ids), encoding="utf-8")
man = {"stage": "stage-a", "ids": ids, "stratum": {i: "L-lmk" for i in ids}, "strata_order": ["L-lmk"],
       "worked_examples": [], "drawn": ids, "note": "D0063 landmark second-reader ids; stage-a wrapper (agreement_2.py)"}
(D / "ec-input" / "manifest-2.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
rows = [l for l in open(D / "validate-pass1.jsonl", encoding="utf-8") if l.strip() and json.loads(l)["id"] in ids]
(D / "ec-input" / "validator-2.jsonl").write_text("".join(rows), encoding="utf-8")
print(ids, len(rows), "validator lines")
