"""Convert full-text PDFs (research/sources/pdfs/fulltext/*.pdf) to markdown with the markitdown CLI.
Output research/sources/md/fulltext/<id>.md (gitignored); log research/review/fulltext/convert-log.jsonl
(id, status, chars, sha256 of the PDF). Skips ids already converted. CPU only.
    python tools/pdf_to_md.py
"""
import hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "research/sources/pdfs/fulltext", ROOT / "research/sources/md/fulltext"
LOG = ROOT / "research/review/fulltext/convert-log.jsonl"
EXE = r"C:\Users\Shlok\AppData\Roaming\Python\Python314\Scripts\markitdown.exe"
OUT.mkdir(parents=True, exist_ok=True)
for pdf in sorted(SRC.glob("*.pdf")):
    md = OUT / (pdf.stem + ".md")
    if md.exists() and md.stat().st_size > 0:
        continue
    r = subprocess.run([EXE, str(pdf), "-o", str(md)], capture_output=True, text=True, timeout=300)
    n = md.stat().st_size if md.exists() else 0
    rec = {"id": pdf.stem, "status": "ok" if r.returncode == 0 and n > 2000 else "failed", "chars": n,
           "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "stderr": r.stderr[-200:] if r.returncode else ""}
    with LOG.open("a", encoding="utf8") as fh:
        fh.write(json.dumps(rec) + "\n")
print("done")
