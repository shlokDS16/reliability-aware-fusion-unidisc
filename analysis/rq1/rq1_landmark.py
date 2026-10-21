"""RQ1 screening fields for the landmark tranche L (D0061), reported apart from the 615 (rq1_counts.py).

    python -I analysis/rq1/rq1_landmark.py

Reads analysis/screening/ft-lmk/lmk-decisions-all.jsonl (final decision, i1, nonlang_only, A's and B's mm and rq tags)
and record dates (research/review/screening/records.jsonl 'published'; corpus/new-records-2026-10-15-v2.jsonl
'published'). Same field rules as rq1_counts.py: mm 'split' when A and B differ; rq tags counted as both and either.
Writes analysis/rq1/rq1-landmark.json.
"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


rows = [r for r in jl(ROOT / "analysis/screening/ft-lmk/lmk-decisions-all.jsonl") if r["decision"] == "include"]
year = {}
for r in jl(ROOT / "research/review/screening/records.jsonl"):
    year[r["sid"]] = str(r.get("published") or "")[:4]
for r in jl(ROOT / "research/review/corpus/new-records-2026-10-15-v2.jsonl"):
    year.setdefault(r["nid"], str(r.get("published") or "")[:4])
mm = collections.Counter(r["mm_A"] if r["mm_A"] == r["mm_B"] else f"split:{r['mm_A']}/{r['mm_B']}" for r in rows)
both = collections.Counter(t for r in rows for t in set(r["rq_A"]) & set(r["rq_B"]))
either = collections.Counter(t for r in rows for t in set(r["rq_A"]) | set(r["rq_B"]))
out = {"n": len(rows), "i1": dict(collections.Counter(r["i1"] for r in rows)),
       "nonlang_only": sum(r["nonlang_only"] for r in rows), "mm": dict(mm),
       "mm_split_total": sum(v for k, v in mm.items() if k.startswith("split")),
       "year": dict(sorted(collections.Counter(year.get(r["id"], "") for r in rows).items())),
       "rq_both": dict(sorted(both.items())), "rq_either": dict(sorted(either.items())),
       "note": "landmark tranche L (D0061): includes of the targeted other-methods tranche; not part of the 615."}
assert all(year.get(r["id"]) for r in rows), [r["id"] for r in rows if not year.get(r["id"])]
(ROOT / "analysis/rq1/rq1-landmark.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1))
