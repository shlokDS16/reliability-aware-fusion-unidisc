"""Build a readable Excel sheet for a human-author screening task (blind full-text screening of listed records).

    python tools/human_sheet.py --ids <file, one id per line> --out <xlsx> --title "<task title>" [--why "<one line>"]
    (needs openpyxl; run without -I so the user site-packages load)

Sheets: "Start here" (steps, one per row, wide wrapped column; the rules are criteria-v1.6-screener.md sections A-C,
blindness rules as in research/review/screening/human-validation-t1/INSTRUCTIONS.md), "Papers" (one row per record:
id, title, PDF and text paths, decision / code / I1 drop-downs, quote, location, note; header and id frozen, wrapped
text, rows sized to the title) and "Progress" (counts). The sheet shows no screener, adjudicator or sample field.
"""
import argparse, json, math
from pathlib import Path
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--ids", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--title", required=True); ap.add_argument("--why", default="")
a = ap.parse_args()
ids = [l.strip() for l in open(a.ids, encoding="utf-8") if l.strip()]
titles = {}
for p, k in ((ROOT / "research/review/corpus/new-records-2026-10-15-v2.jsonl", "nid"), (ROOT / "research/review/screening/records.jsonl", "sid"),
             (ROOT / "research/review/corpus/subscription-records-2026-10-15.jsonl", "id")):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if r[k] in ids and r[k] not in titles:
            titles[r[k]] = r.get("title") or ""
missing = [i for i in ids if i not in titles]
assert not missing, missing

thin = Side(style="thin", color="BFBFBF"); box = Border(left=thin, right=thin, top=thin, bottom=thin)
head_fill, head_font = PatternFill("solid", fgColor="1F3864"), Font(bold=True, color="FFFFFF", size=11)
wrap, center = Alignment(wrap_text=True, vertical="top"), Alignment(horizontal="center", vertical="top", wrap_text=True)
wb = Workbook()

s = wb.active; s.title = "Start here"
s.column_dimensions["A"].width = 6; s.column_dimensions["B"].width = 110
s["A1"] = a.title; s["A1"].font = Font(bold=True, size=14)
if a.why:
    s["B2"] = a.why; s["B2"].alignment = wrap
steps = [
    "Work alone: no Claude or other model reads the papers for you. Do not open anything under analysis/screening/, criteria-v1.6.md (the audit copy), progress.md or USER-ACTIONS beyond the item that sent you here, until this sheet is finished (blindness). If you open one by accident, write which in the Note of row 1.",
    "Rules: research/review/screening/criteria-v1.6-screener.md, sections A-C only (definitions, rules, codes). It names no record.",
    "For each paper: open the PDF path in the Papers sheet (the text path is only for searching). Decide include or exclude from the full text.",
    "Decision: include or exclude (drop-down). If unsure, pick the one you lean to and write 'doubt' and why in Note. There is no 'adjudicate' for you.",
    "Code (exclusions only): the first code that applies in the order X8, X3, X5, X4, X0, X1, X2, X7 (section C). I1 (inclusions only): a, b or ab.",
    "Quote: one contiguous passage of 6 to 40 words copied from the paper that carries the decision; Location: page and section, e.g. p.5, s4.1.",
    "Save the file under the same name with -DONE added before .xlsx and tell Claude. Claude records its sha256 and date before showing you any screener row.",
]
for k, t in enumerate(steps, start=4):
    s.cell(row=k, column=1, value=k - 3).alignment = center
    c = s.cell(row=k, column=2, value=t); c.alignment = wrap
    s.row_dimensions[k].height = 15 * max(1, math.ceil(len(t) / 105))

p = wb.create_sheet("Papers")
cols = [("No.", 6), ("ID", 10), ("Title", 55), ("PDF (open this)", 34), ("Text (search only)", 34), ("Decision", 13),
        ("Code", 9), ("I1", 7), ("Quote (6-40 words)", 50), ("Location", 14), ("Note", 30)]
for j, (h, w) in enumerate(cols, start=1):
    c = p.cell(row=1, column=j, value=h); c.fill, c.font, c.border = head_fill, head_font, box
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    p.column_dimensions[c.column_letter].width = w
dvs = {6: '"include,exclude"', 7: '"X8,X3,X5,X4,X0,X1,X2,X7"', 8: '"a,b,ab"'}
for col, f in dvs.items():
    dv = DataValidation(type="list", formula1=f, allow_blank=True); p.add_data_validation(dv)
    for i in range(2, len(ids) + 2):
        dv.add(p.cell(row=i, column=col))
for i, rid in enumerate(ids, start=2):
    vals = [i - 1, rid, titles[rid], f"research/sources/pdfs/fulltext/{rid}.pdf", f"research/sources/md/fulltext-pymupdf/{rid}.txt",
            "", "", "", "", "", ""]
    for j, v in enumerate(vals, start=1):
        c = p.cell(row=i, column=j, value=v); c.border = box; c.alignment = center if j in (1, 6, 7, 8) else wrap
    p.row_dimensions[i].height = 15 * max(3, math.ceil(len(titles[rid]) / 52)) + 4
last = len(ids) + 1
p.freeze_panes = "C2"; p.auto_filter.ref = f"A1:K{last}"
p.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"include"'], fill=PatternFill("solid", fgColor="C6EFCE")))
p.conditional_formatting.add(f"F2:F{last}", CellIsRule(operator="equal", formula=['"exclude"'], fill=PatternFill("solid", fgColor="F8CBAD")))
p.page_setup.orientation = "landscape"; p.page_setup.fitToWidth, p.page_setup.fitToHeight = 1, 0
p.sheet_properties.pageSetUpPr.fitToPage = True

g = wb.create_sheet("Progress")
g.column_dimensions["A"].width = 22; g.column_dimensions["B"].width = 10
for r, (k, f) in enumerate([("include", f'=COUNTIF(Papers!F2:F{last},"include")'), ("exclude", f'=COUNTIF(Papers!F2:F{last},"exclude")'),
                            ("not yet done", f"=COUNTBLANK(Papers!F2:F{last})"), ("total", len(ids))], start=1):
    g.cell(row=r, column=1, value=k).border = box; g.cell(row=r, column=2, value=f).border = box
wb.active = 0
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
wb.save(a.out)
print(a.out, len(ids))
