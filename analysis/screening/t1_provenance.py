"""Full-text provenance for every T1 record (gate audit 2026-10-20, finding 9: the dispatch 'ft' string says
"open-access PDF" for every record; the true route is in research/review/fulltext/fetch-log.jsonl).

    python -I analysis/screening/t1_provenance.py

Writes analysis/screening/ft-t1/t1-provenance.jsonl: one row per T1 id with the last successful fetch-log entry
(route, url, sha256 of the PDF, timestamp, api or note if present) and prints counts by route.
"""
import collections, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ok = {}
for line in open(ROOT / "research/review/fulltext/fetch-log.jsonl", encoding="utf-8"):
    r = json.loads(line)
    if r.get("status") == "ok":
        ok[r["id"]] = r
t1 = [json.loads(l)["id"] for l in open(ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl", encoding="utf-8") if l.strip()]
rows, c = [], collections.Counter()
for i in sorted(t1):
    r = ok.get(i)
    row = {"id": i, "route": r["route"] if r else "no ok fetch-log entry", "url": r and r.get("url"), "pdf_sha256": r and r.get("sha256"),
           "ts": r and r.get("ts"), "api": r and r.get("api"), "note": r and r.get("note")}
    rows.append(row); c[row["route"]] += 1
with open(ROOT / "analysis/screening/ft-t1/t1-provenance.jsonl", "w", encoding="utf-8", newline="\n") as fh:
    for row in rows:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps({"n": len(rows), "by_route": dict(c)}))
