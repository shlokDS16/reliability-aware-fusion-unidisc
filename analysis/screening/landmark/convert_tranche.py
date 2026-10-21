"""Convert the landmark tranche PDFs (D0061) to text, exactly as tools/pdf_to_text.py does,
but only for the ids in landmark-tranche-ids.txt (pdf_to_text.py would also convert the
other unscreened S1243 PDFs). Output research/sources/md/fulltext-pymupdf/<id>.txt with
'=== page N ===' markers; rows appended to research/review/fulltext/convert-pymupdf-log.jsonl.
Also checks each PDF's sha256 against its 'ok' row in fetch-log.jsonl.

    python -I analysis/screening/landmark/convert_tranche.py
"""
import hashlib
import json
import re
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "research/sources/pdfs/fulltext"
OUT = ROOT / "research/sources/md/fulltext-pymupdf"
LOG = ROOT / "research/review/fulltext/convert-pymupdf-log.jsonl"
FETCH = ROOT / "research/review/fulltext/fetch-log.jsonl"
IDS = (Path(__file__).resolve().parent / "landmark-tranche-ids.txt").read_text().split()


def glued(t):
    toks = re.findall(r"\S+", t)
    return sum(1 for w in toks if len(re.sub(r"[^A-Za-z]", "", w)) >= 25 and not w.startswith("http")) / max(1, len(toks))


fetched = {}
for line in FETCH.read_text(encoding="utf8").splitlines():
    if line.strip():
        r = json.loads(line)
        if r.get("status") == "ok":
            fetched[r["id"]] = r.get("sha256")
done = {json.loads(l)["id"] for l in LOG.read_text(encoding="utf8").splitlines() if l.strip()} if LOG.exists() else set()
OUT.mkdir(parents=True, exist_ok=True)
summary = {"converted": 0, "skipped_logged": 0, "sha_mismatch": [], "not_ok": []}
for rid in IDS:
    if rid in done:
        summary["skipped_logged"] += 1
        continue
    b = (SRC / f"{rid}.pdf").read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    if fetched.get(rid) != sha:
        summary["sha_mismatch"].append(rid)
    try:
        doc = fitz.open(stream=b, filetype="pdf")
        text = "".join(f"\n=== page {i} ===\n" + p.get_text() for i, p in enumerate(doc, 1))
        (OUT / f"{rid}.txt").write_text(text, encoding="utf8")
        rec = {"id": rid, "status": "ok" if len(text) > 2000 else "too_short", "pages": len(doc),
               "chars": len(text), "glued_rate": round(glued(text), 5)}
    except Exception as e:  # noqa: BLE001 - logged, like pdf_to_text.py
        rec = {"id": rid, "status": "failed", "error": repr(e)[:200]}
    rec["pdf_sha256"] = sha
    rec["tranche"] = "L"
    with LOG.open("a", encoding="utf8") as fh:
        fh.write(json.dumps(rec) + "\n")
    summary["converted"] += 1
    if rec["status"] != "ok":
        summary["not_ok"].append(rid)
print(json.dumps(summary))
