"""Cut one record's part out of a converted full text that holds a whole volume (proceedings, abstract book), so
screeners get only that record. The excerpt runs from the first occurrence of START (a literal string, e.g. the
record's own DOI line) up to, not including, the next occurrence of END after it; the '=== page N ===' marker of
the page where the excerpt starts is kept at its head, and every page marker inside it is kept. The full text
moves to research/sources/md/fulltext-pymupdf/full/<id>.txt; a row goes to convert-pymupdf-log.jsonl
(status 'excerpt', start/end strings, page range, chars, sha256 of the PDF).

    python tools/ft_excerpt.py M17477 "https://doi.org/10.5327/CBN241424" "https://doi.org/10.5327/CBN241425"
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "research/sources/md/fulltext-pymupdf"
LOG = ROOT / "research/review/fulltext/convert-pymupdf-log.jsonl"

rid, start, end = sys.argv[1:4]
src = TXT / f"{rid}.txt"
full = TXT / "full" / f"{rid}.txt"
text = (full if full.exists() else src).read_text(encoding="utf-8")
s = text.find(start)
e = text.find(end, s + len(start)) if s >= 0 else -1
if s < 0 or e < 0:
    sys.exit(f"start or end not found (start {s}, end {e})")
marks = [(m.start(), int(m.group(1))) for m in re.finditer(r"=== page (\d+) ===", text)]
p0 = max(n for pos, n in marks if pos <= s)
p1 = max(n for pos, n in marks if pos <= e)
excerpt = f"\n=== page {p0} ===\n" + text[s:e]
if not full.exists():
    full.parent.mkdir(exist_ok=True)
    shutil.move(str(src), full)
src.write_text(excerpt, encoding="utf-8")
pdf = ROOT / "research/sources/pdfs/fulltext" / f"{rid}.pdf"
rec = {"id": rid, "status": "excerpt", "start": start, "end": end, "pdf_pages": [p0, p1], "chars": len(excerpt),
       "full_text": str(full.relative_to(ROOT)).replace("\\", "/"),
       "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest() if pdf.exists() else None}
with LOG.open("a", encoding="utf8") as fh:
    fh.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
