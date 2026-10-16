"""Convert full-text PDFs to plain text with PyMuPDF (replaces tools/pdf_to_md.py for screening, 2026-10-16).

markitdown dropped the spaces between words in 72 of the first 123 papers (up to 14 percent of tokens),
so quotes from those passages could not meet the 6-word evidence rule; PyMuPDF's rate on the worst four
was 0.0003 or less. Output research/sources/md/fulltext-pymupdf/<id>.txt with a line
'=== page N ===' before each PDF page, so evidence locations can cite p.N. Log
research/review/fulltext/convert-pymupdf-log.jsonl (id, status, pages, chars, glued_rate, pdf_sha256).
    python tools/pdf_to_text.py
"""
import hashlib, json, re
from pathlib import Path
import fitz  # PyMuPDF 1.27.2.3

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "research/sources/pdfs/fulltext", ROOT / "research/sources/md/fulltext-pymupdf"
LOG = ROOT / "research/review/fulltext/convert-pymupdf-log.jsonl"
OUT.mkdir(parents=True, exist_ok=True)

def glued(t):
    toks = re.findall(r"\S+", t)
    return sum(1 for w in toks if len(re.sub(r"[^A-Za-z]", "", w)) >= 25 and not w.startswith("http")) / max(1, len(toks))

done = {json.loads(l)["id"] for l in LOG.read_text(encoding="utf8").splitlines() if l.strip()} if LOG.exists() else set()
for pdf in sorted(SRC.glob("*.pdf")):
    if pdf.stem in done:
        continue
    b = pdf.read_bytes()
    try:
        doc = fitz.open(stream=b, filetype="pdf")
        text = "".join(f"\n=== page {i} ===\n" + p.get_text() for i, p in enumerate(doc, 1))
        (OUT / f"{pdf.stem}.txt").write_text(text, encoding="utf8")
        rec = {"id": pdf.stem, "status": "ok" if len(text) > 2000 else "too_short", "pages": len(doc), "chars": len(text), "glued_rate": round(glued(text), 5)}
    except Exception as e:
        rec = {"id": pdf.stem, "status": "failed", "error": repr(e)[:200]}
    rec["pdf_sha256"] = hashlib.sha256(b).hexdigest()
    with LOG.open("a", encoding="utf8") as fh:
        fh.write(json.dumps(rec) + "\n")
print("done")
