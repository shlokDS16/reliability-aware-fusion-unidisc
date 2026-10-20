"""Workbook for the human author's check OQ5-04 (replaces OQ4-04; research/review/extraction/OPEN-QUESTIONS-v0.5.md),
required by D0042 before any extraction draw. Not a blind screening task: the sheet shows the current class.

Records (ids copied from OPEN-QUESTIONS-v0.4/v0.5 and analysis/extraction/multimodal_options-log.txt):
  item 1  split text/multimodal records (3)
  item 2  A = B on the decision, A != B on i1 or nonlang_only (6; also D0039: the human author resolves the field)
  item 3  B2 (15) and B3 (2) borderline ids of OQ3-04; duplicate-work candidates (6 pairs, own sheet)
  item 4  29 side-experiment ids, 10 frame-R joint-model candidates, 20 C2 records with no multimodal hit (OQ5-04)
One row per record; "Why listed" names every item it is in. Construct codes under D0042 option (d):
joint-model, side-experiment, text.

    python analysis/extraction/oq5_04_sheet.py        (needs openpyxl; no -I so the user site-packages load)

Writes research/review/extraction/human-check-oq5-04.xlsx and analysis/extraction/oq5-04-ids.json.
"""
import json, math
from collections import defaultdict
from pathlib import Path
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/review/extraction/human-check-oq5-04.xlsx"
ITEMS = {
    "1 split screeners (text vs multimodal)": "M02955 M18118 M18656",
    "2 i1 / nonlang_only differ between screeners": "M10840 M12859 U04330 M16043 M11389 M18059",
    "3 B2: screeners said multimodal, no keyword in title/abstract": "M00285 M05642 M05663 M07324 M09298 M09321 M10881 M12175 M13247 M14560 M14706 M14711 M16251 M16730 M18406",
    "3 B3: screeners said text/other, keyword in title": "M13760 M15613",
    "4 side-experiment candidate": "M00285 M02955 M04297 M04350 M04373 M05608 M05642 M05663 M06218 M09321 M10881 M11247 M12175 M13247 M13444 M13674 M14706 M15373 M15652 M15895 M16133 M16251 M16263 M16730 M16813 M18406 M18456 M19099 U04378",
    "4 joint-model candidate in the text frame": "M07165 M13735 M14023 M15097 M15613 M15736 M16249 M17056 M17150 M18118",
    "4 multimodal class, no multimodal benchmark or model name found": "M01397 M04245 M04407 M05954 M08275 M08783 M08804 M09403 M10855 M13342 M13470 M13774 M15668 M16116 M17332 U00130 U00134 U00173 U00398 U04330",
}
DUPS = [("M03951", "M16269"), ("M07769", "M16343"), ("M09657", "M15091"), ("M14067", "M14568"), ("M14370", "M14372"), ("M16133", "M16134")]
ITEM2 = set(ITEMS["2 i1 / nonlang_only differ between screeners"].split())
why = defaultdict(list)
for k, v in ITEMS.items():
    for i in v.split():
        why[i].append(k)
ids = sorted(why)
titles = {}
for p in (ROOT / "research/review/fulltext/ft-routes.jsonl", ROOT / "analysis/screening/ft-routes-extra.jsonl"):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        titles.setdefault(r["id"], r.get("title") or "")
dec = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl", encoding="utf-8") if l.strip()}
need = set(ids) | {x for p in DUPS for x in p}
assert need <= set(titles) and need <= set(dec), sorted(need - set(titles) - set(dec))
assert all(dec[i]["decision"] == "include" for i in need), [i for i in need if dec[i]["decision"] != "include"]

thin = Side(style="thin", color="BFBFBF"); box = Border(left=thin, right=thin, top=thin, bottom=thin)
head_fill, head_font = PatternFill("solid", fgColor="1F3864"), Font(bold=True, color="FFFFFF", size=11)
wrap, center = Alignment(wrap_text=True, vertical="top"), Alignment(horizontal="center", vertical="top", wrap_text=True)
wb = Workbook()
s = wb.active; s.title = "Start here"
s.column_dimensions["A"].width = 6; s.column_dimensions["B"].width = 115
s["A1"] = f"Extraction check OQ5-04: {len(ids)} papers and {len(DUPS)} possible duplicate pairs (about 1.5-2.5 hours)"
s["A1"].font = Font(bold=True, size=14)
steps = [
    "Why: D0042 (your choice of option (d)) needs these papers coded before any extraction draw. This is not blind screening; you may look at anything.",
    "Open the PDF path in the 'Papers' sheet (the text path is for searching). 'Why listed' says which question applies; one paper can be on several lists.",
    "Construct (every paper except the five that are only on list 2): joint-model = one model (shared weights or one jointly trained system) whose diffusion component takes in or puts out image, video, audio/speech or 3D AND produces the text; side-experiment = the paper's main model is a text (or general discrete) diffusion model and its image/audio/3D work is a separate model or a side experiment; text = no image/video/audio/3D experiment that counts.",
    "List 2 papers: pick the I1 basis (a = text diffusion LM; b = unified multimodal model; ab = both) and nonlang_only (yes = the text-pretrained model is trained or evaluated only on non-language strings). Both screeners agreed to include; only this field differs.",
    "If unsure, pick the code you lean to and write 'doubt' and why in Note.",
    "Sheet 'Duplicates': for each pair, say whether the second paper is a report of the same study as the first (same model and experiments, e.g. thesis chapter and paper, workshop and conference version). 'yes' means the second leaves the extraction frames.",
    "Save the file with -DONE added before .xlsx and tell Claude. Claude writes analysis/extraction/mm-construct.jsonl, strata-overrides.jsonl and duplicate-works.jsonl from it and records the file's sha256.",
]
for k, t in enumerate(steps, start=3):
    s.cell(row=k, column=1, value=k - 2).alignment = center
    c = s.cell(row=k, column=2, value=t); c.alignment = wrap
    s.row_dimensions[k].height = 15 * max(1, math.ceil(len(t) / 110))

p = wb.create_sheet("Papers")
cols = [("No.", 6), ("ID", 10), ("Title", 50), ("Why listed", 40), ("PDF (open this)", 30), ("Text (search only)", 30),
        ("Construct", 16), ("I1 (list 2)", 9), ("nonlang_only (list 2)", 11), ("Note", 34)]
for j, (h, w) in enumerate(cols, start=1):
    c = p.cell(row=1, column=j, value=h); c.fill, c.font, c.border = head_fill, head_font, box
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    p.column_dimensions[c.column_letter].width = w
p.row_dimensions[1].height = 32
dv_c = DataValidation(type="list", formula1='"joint-model,side-experiment,text"', allow_blank=True)
dv_i = DataValidation(type="list", formula1='"a,b,ab"', allow_blank=True)
dv_n = DataValidation(type="list", formula1='"yes,no"', allow_blank=True)
for dv in (dv_c, dv_i, dv_n):
    p.add_data_validation(dv)
grey = PatternFill("solid", fgColor="EDEDED")
for r, rid in enumerate(ids, start=2):
    w = "; ".join(why[rid])
    vals = [r - 1, rid, titles[rid], w, f"research/sources/pdfs/fulltext/{rid}.pdf", f"research/sources/md/fulltext-pymupdf/{rid}.txt", "", "", "", ""]
    for j, v in enumerate(vals, start=1):
        c = p.cell(row=r, column=j, value=v); c.border = box; c.alignment = center if j in (1, 7, 8, 9) else wrap
    only2 = why[rid] == ["2 i1 / nonlang_only differ between screeners"]
    if only2:
        p.cell(row=r, column=7, value="(not needed)").fill = grey
    else:
        dv_c.add(p.cell(row=r, column=7))
    if rid in ITEM2:
        dv_i.add(p.cell(row=r, column=8)); dv_n.add(p.cell(row=r, column=9))
    else:
        p.cell(row=r, column=8).fill = grey; p.cell(row=r, column=9).fill = grey
    p.row_dimensions[r].height = 15 * max(2, math.ceil(len(titles[rid]) / 47), math.ceil(len(w) / 38)) + 4
last = len(ids) + 1
p.freeze_panes = "C2"; p.auto_filter.ref = f"A1:J{last}"
for v, col in (("joint-model", "C6EFCE"), ("side-experiment", "FFF2CC"), ("text", "DDEBF7")):
    p.conditional_formatting.add(f"G2:G{last}", CellIsRule(operator="equal", formula=[f'"{v}"'], fill=PatternFill("solid", fgColor=col)))
p.page_setup.orientation = "landscape"; p.page_setup.fitToWidth, p.page_setup.fitToHeight = 1, 0
p.sheet_properties.pageSetUpPr.fitToPage = True

d = wb.create_sheet("Duplicates")
dcols = [("No.", 6), ("First ID", 10), ("First title", 50), ("Second ID", 10), ("Second title", 50), ("Same study?", 12), ("Note", 34)]
for j, (h, wd) in enumerate(dcols, start=1):
    c = d.cell(row=1, column=j, value=h); c.fill, c.font, c.border = head_fill, head_font, box
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    d.column_dimensions[c.column_letter].width = wd
dv_d = DataValidation(type="list", formula1='"yes,no"', allow_blank=True); d.add_data_validation(dv_d)
for r, (x, y) in enumerate(DUPS, start=2):
    for j, v in enumerate([r - 1, x, titles[x], y, titles[y], "", ""], start=1):
        c = d.cell(row=r, column=j, value=v); c.border = box; c.alignment = center if j in (1, 6) else wrap
    dv_d.add(d.cell(row=r, column=6))
    d.row_dimensions[r].height = 15 * max(2, math.ceil(max(len(titles[x]), len(titles[y])) / 47)) + 4
d.freeze_panes = "B2"

g = wb.create_sheet("Progress")
g.column_dimensions["A"].width = 34; g.column_dimensions["B"].width = 10
rows = [("Construct: joint-model", f'=COUNTIF(Papers!G2:G{last},"joint-model")'), ("Construct: side-experiment", f'=COUNTIF(Papers!G2:G{last},"side-experiment")'),
        ("Construct: text", f'=COUNTIF(Papers!G2:G{last},"text")'), ("Construct: not yet done", f'=COUNTBLANK(Papers!G2:G{last})'),
        ("List 2: I1 filled", f'=COUNTA(Papers!H2:H{last})-COUNTIF(Papers!H2:H{last},"")'), ("Duplicates answered", f'=COUNTA(Duplicates!F2:F{len(DUPS) + 1})'),
        ("Papers in total", len(ids))]
for r, (k, f) in enumerate(rows, start=1):
    g.cell(row=r, column=1, value=k).border = box; g.cell(row=r, column=2, value=f).border = box
wb.active = 0
wb.save(OUT)
(ROOT / "analysis/extraction/oq5-04-ids.json").write_text(json.dumps({"ids": ids, "why": why, "duplicate_pairs": DUPS}, indent=1) + "\n", encoding="utf-8")
print(OUT, len(ids), "papers,", len(DUPS), "pairs")
