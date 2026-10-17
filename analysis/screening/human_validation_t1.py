"""Draw the human validation sample of full-text tranche T1 (criteria v1.6 audit copy s4 item 6; protocol s4
step 3) and write the blind sheet for the human author.

Frame: every record of the T1 batch plans (research/review/fulltext/t1-batches-part*.json) that has a
screened full text (research/sources/md/fulltext-pymupdf/<id>.txt), i.e. the 715 records of t1b001-t1b076.
Draw: simple random sample, random.Random(20261016).sample over the frame ids sorted, size
max(100, ceil(0.15 * N)). The sheet holds id, title (ft-routes.jsonl) and the local full-text paths only:
no screener, adjudicator or title/abstract decision, no source or re-check flag. The plan files are read
for ids only; no screening output is opened.

    python analysis/screening/human_validation_t1.py
"""
import csv
import hashlib
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FT = ROOT / "research/review/fulltext"
TXT = ROOT / "research/sources/md/fulltext-pymupdf"
PDF = ROOT / "research/sources/pdfs/fulltext"
OUT = ROOT / "research/review/screening/human-validation-t1"
SEED = 20261016

frame = set()
for p in sorted(FT.glob("t1-batches-part*.json")):
    b = json.loads(p.read_text(encoding="utf-8"))["batches"]
    for ids in (b.values() if isinstance(b, dict) else b):
        frame.update(ids)
frame = sorted(i for i in frame if (TXT / f"{i}.txt").exists())
k = max(100, math.ceil(0.15 * len(frame)))
sample = sorted(random.Random(SEED).sample(frame, k))

titles = {}
for line in open(FT / "ft-routes.jsonl", encoding="utf-8"):
    d = json.loads(line)
    titles[d["id"]] = d.get("title") or ""

OUT.mkdir(parents=True, exist_ok=True)
cols = ["n", "id", "title", "pdf_file", "text_file", "decision", "code", "quote", "quote_location", "note"]
rows = []
for n, i in enumerate(sample, 1):
    pdf = PDF / f"{i}.pdf"
    rows.append({"n": n, "id": i, "title": titles.get(i, ""),
                 "pdf_file": str(pdf.relative_to(ROOT)).replace("\\", "/") if pdf.exists() else "",
                 "text_file": str((TXT / f"{i}.txt").relative_to(ROOT)).replace("\\", "/"),
                 "decision": "", "code": "", "quote": "", "quote_location": "", "note": ""})

with open(OUT / "human-validation-t1-sheet.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation
wb = Workbook(); ws = wb.active; ws.title = "T1 validation"
ws.append(cols)
for r in rows:
    ws.append([r[c] for c in cols])
for c in ws[1]:
    c.font = Font(bold=True)
for col, width in zip("ABCDEFGHIJ", (5, 9, 60, 38, 46, 11, 8, 60, 16, 30)):
    ws.column_dimensions[col].width = width
for row in ws.iter_rows(min_row=2, min_col=3, max_col=3):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")
dv = DataValidation(type="list", formula1='"include,exclude"', allow_blank=True)
dv_code = DataValidation(type="list", formula1='"X8,X3,X5,X4,X0,X1,X2,X7"', allow_blank=True)
ws.add_data_validation(dv); ws.add_data_validation(dv_code)
dv.add(f"F2:F{len(rows) + 1}"); dv_code.add(f"G2:G{len(rows) + 1}")
ws.freeze_panes = "C2"
wb.save(OUT / "human-validation-t1-sheet.xlsx")

manifest = {"tranche": "T1", "frame_note": "T1 records with a screened full text on 2026-10-17 (t1b001-t1b076). T1 records "
            "screened later (re-check sample, C8, e-gateway, ScienceDirect passes) get their own 15 percent draw with the "
            "same seed over their sorted ids, so the frozen draw here is never redrawn (deviation from a single draw "
            "over the fixed T1 set, criteria v1.6 A s4 item 6; to be logged as a decision).", "frame_n": len(frame), "frame_sha256": hashlib.sha256("\n".join(frame).encode()).hexdigest(),
            "seed": SEED, "rule": "random.Random(seed).sample(sorted frame ids, max(100, ceil(0.15 N)))",
            "k": k, "sample_sha256": hashlib.sha256("\n".join(sample).encode()).hexdigest(),
            "missing_pdf": [r["id"] for r in rows if not r["pdf_file"]],
            "missing_title": [r["id"] for r in rows if not r["title"]]}
(OUT / "sample-manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
print(json.dumps(manifest))
