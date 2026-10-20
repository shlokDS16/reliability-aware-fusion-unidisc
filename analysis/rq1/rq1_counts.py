"""RQ1 counts over every include (D0051 item 2: from screening fields), T1 (608) + R797 frozen (7).
    python -I analysis/rq1/rq1_counts.py
Reads analysis/screening/ft-t1/t1-decisions-all.jsonl, ft-r797/r797-decisions-all.jsonl (final decision, i1,
nonlang_only), the screener rows FA-/FB-<batch>.jsonl of each include's batch (mm, rq tags, body3d) and record
metadata (corpus/new-records-2026-10-15-v2.jsonl 'published', subscription-records 'year', screening/records.jsonl
'published'). Writes analysis/rq1/rq1-counts.json and rq1-includes.jsonl. Fields that A and B set differently are
reported as 'split' (mm) or counted by agreement level (rq tags: both, either); no field is taken from a third source.
"""
import collections, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SCR, REV, OUT = ROOT / "analysis/screening", ROOT / "research/review", ROOT / "analysis/rq1"


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


inc = []
for tr, f in (("T1", "ft-t1/t1-decisions-all.jsonl"), ("R797", "ft-r797/r797-decisions-all.jsonl")):
    for r in jl(SCR / f):
        if r["decision"] == "include":
            inc.append({**r, "tranche": tr})
assert len({r["id"] for r in inc}) == len(inc)
meta = {}
for r in jl(REV / "corpus/new-records-2026-10-15-v2.jsonl"):
    meta[r["nid"]] = (str(r.get("published") or "")[:4], r.get("venue"))
for r in jl(REV / "corpus/subscription-records-2026-10-15.jsonl"):
    meta[r["id"]] = (str(r.get("year") or "")[:4], r.get("venue"))
for r in jl(REV / "screening/records.jsonl"):
    meta.setdefault(r["sid"], (str(r.get("published") or "")[:4], None))


def rows(tr, batch, who):
    p = SCR / f"ft-{tr.lower()}" / batch / f"F{who}-{batch}.jsonl"
    return {x["id"]: x for x in jl(p)} if p.exists() else {}


cache, out = {}, []
for r in inc:
    k = (r["tranche"], r["batch"])
    if k not in cache:
        cache[k] = (rows(*k, "A"), rows(*k, "B"))
    A, B = (c.get(r["id"]) or {} for c in cache[k])
    mmA, mmB = A.get("mm"), B.get("mm")
    rqA, rqB = set(A.get("rq") or []), set(B.get("rq") or [])
    y, venue = meta.get(r["id"], ("", None))
    out.append({"id": r["id"], "tranche": r["tranche"], "source": r["source"], "i1": r["i1"],
                "nonlang_only": r["nonlang_only"], "mm_A": mmA, "mm_B": mmB,
                "mm": mmA if mmA == mmB else f"split:{mmA}/{mmB}", "rq_both": sorted(rqA & rqB),
                "rq_either": sorted(rqA | rqB), "rows_found": [bool(A), bool(B)], "year": y or "unknown",
                "venue_listed": bool(venue and str(venue) not in ("None", "", "arXiv", "arXiv.org"))})
C = collections.Counter
res = {"n": len(out), "by_tranche": dict(C(o["tranche"] for o in out)),
       "i1": dict(C(o["i1"] for o in out)), "nonlang_only": sum(o["nonlang_only"] for o in out),
       "mm": dict(C(o["mm"] for o in out)), "year": dict(sorted(C(o["year"] for o in out).items())),
       "i1_by_year": {y: dict(C(o["i1"] for o in out if o["year"] == y)) for y in sorted({o["year"] for o in out})},
       "rq_both": dict(sorted(C(t for o in out for t in o["rq_both"]).items())),
       "rq_either": dict(sorted(C(t for o in out for t in o["rq_either"]).items())),
       "venue_listed": sum(o["venue_listed"] for o in out),
       "screener_rows_missing": [o["id"] for o in out if not all(o["rows_found"])],
       "note": "i1: a = diffusion model with text or code output; b = unified understanding-and-generation model; "
               "ab = both (criteria v1.6). mm: screeners' modality field (text, multimodal, other). rq tags: which RQ "
               "a screener judged the study to carry evidence for (both = A and B; either = A or B). C-decided "
               "includes keep A's and B's own fields."}
(OUT / "rq1-includes.jsonl").write_text("".join(json.dumps(o) + "\n" for o in out), encoding="utf-8")
(OUT / "rq1-counts.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
print(json.dumps(res, indent=1))
