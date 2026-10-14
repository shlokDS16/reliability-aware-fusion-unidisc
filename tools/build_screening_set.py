"""Build the title-and-abstract screening set (protocol section 4, step 1).

Merges the Awesome-DLMs seed and the logged arXiv S1/S2 exports, deduplicates on arXiv ID then on
normalised title, and writes research/review/screening/records.jsonl (one record per line: sid,
arxiv, title, abstract, published, sources) plus batch files of 100 records for the screeners and a
dedup report. Deterministic: records are sorted by arXiv ID, then title.

    python tools/build_screening_set.py
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "research" / "review" / "corpus"
OUT = ROOT / "research" / "review" / "screening"


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def arxiv_id(s: str | None) -> str | None:
    m = re.search(r"(\d{4}\.\d{4,5})", s or "")
    return m.group(1) if m else None


recs: dict[str, dict] = {}
by_title: dict[str, str] = {}
seen_dups = []


def add(aid, title, abstract, published, source):
    key = aid or "title:" + norm_title(title)
    nt = norm_title(title)
    if aid is None and nt in by_title:
        key = by_title[nt]
    if aid is not None and key not in recs and nt in by_title and by_title[nt].startswith("title:"):
        old = recs.pop(by_title[nt])  # a title-only record later found with an arXiv ID
        old["arxiv"] = aid
        recs[aid] = old
    if key in recs:
        r = recs[key]
        r["sources"] = sorted(set(r["sources"]) | {source})
        r["abstract"] = r["abstract"] or abstract
        seen_dups.append((key, source))
        return
    recs[key] = {"arxiv": aid, "title": title, "abstract": abstract or "", "published": published,
                 "sources": [source]}
    by_title[nt] = key


for line in open(CORPUS / "awesome-dlms@194aa6bd.jsonl", encoding="utf8"):
    r = json.loads(line)
    a = r.get("arxiv") or {}
    aid = arxiv_id(r.get("canonical_id")) or arxiv_id(r.get("url"))
    add(aid, a.get("title") or r.get("title"), a.get("abstract"), (a.get("published") or "")[:10],
        "awesome-dlms@194aa6bd")

for f in sorted(CORPUS.glob("arxiv-S*-*.jsonl")):
    tag = f.stem.split("-")[1]
    for line in open(f, encoding="utf8"):
        r = json.loads(line)
        add(arxiv_id(r.get("arxiv")), r.get("title"), r.get("abstract"), (r.get("published") or "")[:10],
            f"arxiv-{tag}")

rows = sorted(recs.values(), key=lambda r: (r["arxiv"] or "9999", norm_title(r["title"])))
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "batches").mkdir(exist_ok=True)
with open(OUT / "records.jsonl", "w", encoding="utf8") as fh:
    for i, r in enumerate(rows, 1):
        r["sid"] = f"R{i:04d}"
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
for b in range(0, len(rows), 100):
    with open(OUT / "batches" / f"batch-{b // 100 + 1:02d}.jsonl", "w", encoding="utf8") as fh:
        for r in rows[b:b + 100]:
            fh.write(json.dumps({"sid": r["sid"], "title": r["title"], "abstract": r["abstract"]},
                                ensure_ascii=False) + "\n")

sha = hashlib.sha256((OUT / "records.jsonl").read_bytes()).hexdigest()
n_noabs = sum(1 for r in rows if not r["abstract"])
src = {}
for r in rows:
    k = "+".join(r["sources"])
    src[k] = src.get(k, 0) + 1
report = {"records": len(rows), "duplicates_merged": len(seen_dups), "without_abstract": n_noabs,
          "by_source_combination": src, "records_sha256": sha, "batches": (len(rows) + 99) // 100}
(OUT / "dedup-report.json").write_text(json.dumps(report, indent=2), encoding="utf8")
print(json.dumps(report, indent=2))
