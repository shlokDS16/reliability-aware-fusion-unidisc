"""Build a readable Excel checklist for the e-gateway papers the user downloads by hand.

    python tools/egateway_sheet.py            (needs openpyxl; run without -I so the user site-packages load)
    python tools/egateway_sheet.py --src <csv> --out <xlsx> --label "<tranche label>"   (another tranche, same layout)

Reads research/review/fulltext/egateway-manual.csv and writes research/review/fulltext/egateway-manual-checklist.xlsx:
sheet "Start here" (steps, one per row, wide wrapped column), sheet "Papers" (one row per paper, grouped by
publisher, clickable DOI link, file name to save as, a Status drop-down and a Note column; header and ID
columns frozen, wrapped text, row heights sized to the title) and sheet "Progress" (counts by status).
The import step does not read this file: tools/egateway_import.py picks up whatever <id>.pdf files are in Downloads.
"""
import argparse, csv, math
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--src", default=str(ROOT / "research/review/fulltext/egateway-manual.csv"))
ap.add_argument("--out", default=str(ROOT / "research/review/fulltext/egateway-manual-checklist.xlsx"))
ap.add_argument("--label", default="")
_a = ap.parse_args()
SRC, OUT = Path(_a.src), Path(_a.out)
STATUSES = ["Saved", "Not in VIT subscription", "Link broken", "Skip for now"]

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
for r in rows:
    r["publisher"] = r["publisher"] or "unknown"
order = {"Elsevier": 0, "Springer Nature": 1, "ACM": 2, "IEEE": 3}
rows.sort(key=lambda r: (order.get(r["publisher"], 4), r["publisher"], r["id"]))

def short_reason(r):
    t = r["reason"]
    if t.startswith("ScienceDirect"): return "ScienceDirect shows a Cloudflare check to the automated browser."
    if t.startswith("Springer") and r["doi"].startswith("10.1007/978-"):
        return "Springer book or chapter: the automated tab showed a purchase page. Try once; if VIT has no access, mark 'Not in VIT subscription'."
    if t.startswith("Springer"): return "Springer journal: automated access was stopped after HTML/503 replies. Download by hand."
    if t.startswith("ACM"): return "ACM: Chrome saved no file when the download was automated."
    if t.startswith("IEEE"): return "IEEE Xplore: subscription PDF. Open the link through the VIT e-gateway and use the PDF button."
    if t.startswith("not attempted"): return "Not tried in the automated browser. Open the link; download if free or through the e-gateway."
    return t[:160]

thin = Side(style="thin", color="BFBFBF")
box = Border(left=thin, right=thin, top=thin, bottom=thin)
head_fill = PatternFill("solid", fgColor="1F3864")
head_font = Font(bold=True, color="FFFFFF", size=11)
wrap_top = Alignment(wrap_text=True, vertical="top")
center_top = Alignment(horizontal="center", vertical="top", wrap_text=True)
pub_fill = {"Elsevier": "FFF2CC", "Springer Nature": "E2EFDA", "ACM": "DDEBF7", "IEEE": "FCE4D6"}

wb = Workbook()

# Sheet 1: Start here
s = wb.active
s.title = "Start here"
s.column_dimensions["A"].width = 6
s.column_dimensions["B"].width = 110
s["A1"] = f"E-gateway papers to download by hand ({len(rows)}){(' - ' + _a.label) if _a.label else ''}"
s["A1"].font = Font(bold=True, size=14)
steps = [
    "Open Chrome where you are signed in to the VIT e-gateway (library proxy). Check the VIT access line on one Springer article first: during the automated run it vanished after a burst of requests.",
    "Go to the sheet 'Papers'. Work down the list; rows are grouped by publisher (yellow Elsevier, green Springer, blue ACM, orange IEEE, white others).",
    "Click 'Open' in the Link column. It opens the DOI page. If the page offers no PDF, use the e-gateway search for the title instead.",
    "Download the PDF and save it in your Downloads folder with the exact name in the 'Save as' column (for example M11784.pdf). Do not rename or edit the PDF.",
    "Set Status from the drop-down: Saved / Not in VIT subscription / Link broken / Skip for now. Add a short note if something was odd (wrong paper, only an abstract, a preview of 2 pages).",
    "If the PDF is a different paper from the title in the row, do not save it under that ID; set 'Link broken' and write what you got in Note.",
    "You do not need to finish in one sitting. The sheet 'Progress' counts how many are done.",
    "When done (or partly done), save this file and tell Claude: 'import the e-gateway PDFs'. Claude runs tools/egateway_import.py, which hashes each file, converts it to text and checks the title against the record. Rows you marked 'Not in VIT subscription' are reported as 'reports not retrieved' in PRISMA.",
    "Never paste passwords or e-gateway cookies anywhere for Claude; Claude does not need them for this step.",
]
for k, t in enumerate(steps, start=3):
    s.cell(row=k, column=1, value=k - 2).alignment = center_top
    c = s.cell(row=k, column=2, value=t)
    c.alignment = wrap_top
    s.row_dimensions[k].height = 15 * max(1, math.ceil(len(t) / 105))

# Sheet 2: Papers
p = wb.create_sheet("Papers")
cols = [("No.", 6), ("ID", 10), ("Publisher", 18), ("Title", 62), ("Link", 10), ("Save as", 14),
        ("Why by hand", 46), ("Status", 22), ("Note", 36)]
for j, (h, w) in enumerate(cols, start=1):
    c = p.cell(row=1, column=j, value=h)
    c.fill, c.font, c.border = head_fill, head_font, box
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    p.column_dimensions[c.column_letter].width = w
p.row_dimensions[1].height = 22
dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
dv.error, dv.errorTitle = "Pick a status from the list.", "Status"
p.add_data_validation(dv)
for i, r in enumerate(rows, start=2):
    why = short_reason(r)
    vals = [i - 1, r["id"], r["publisher"], r["title"], "Open", f'{r["id"]}.pdf', why, "", ""]
    fill = PatternFill("solid", fgColor=pub_fill.get(r["publisher"], "FFFFFF"))
    for j, v in enumerate(vals, start=1):
        c = p.cell(row=i, column=j, value=v)
        c.border, c.alignment = box, (center_top if j in (1, 5, 6) else wrap_top)
        if j <= 3: c.fill = fill
    link = r["url"] or (f'https://doi.org/{r["doi"]}' if r["doi"] else "")
    if link:
        p.cell(row=i, column=5).hyperlink = link
        p.cell(row=i, column=5).font = Font(color="0563C1", underline="single")
    else:
        p.cell(row=i, column=5, value="(no link)")
    dv.add(p.cell(row=i, column=8))
    lines = max(math.ceil(len(r["title"]) / 58), math.ceil(len(why) / 42), 1)
    p.row_dimensions[i].height = 15 * lines + 4
last = len(rows) + 1
p.freeze_panes = "C2"
p.auto_filter.ref = f"A1:I{last}"
green, grey = PatternFill("solid", fgColor="C6EFCE"), PatternFill("solid", fgColor="EDEDED")
p.conditional_formatting.add(f"H2:H{last}", CellIsRule(operator="equal", formula=['"Saved"'], fill=green))
for st in STATUSES[1:]:
    p.conditional_formatting.add(f"H2:H{last}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=grey))
p.page_setup.orientation = "landscape"
p.page_setup.fitToWidth, p.page_setup.fitToHeight = 1, 0
p.sheet_properties.pageSetUpPr.fitToPage = True
p.print_title_rows = "1:1"

# Sheet 3: Progress
g = wb.create_sheet("Progress")
g.column_dimensions["A"].width = 28
g.column_dimensions["B"].width = 10
g["A1"], g["B1"] = "Status", "Count"
for c in (g["A1"], g["B1"]):
    c.fill, c.font, c.border = head_fill, head_font, box
for k, st in enumerate(STATUSES + ["(not yet done)"], start=2):
    g.cell(row=k, column=1, value=st).border = box
    f = f'=COUNTIF(Papers!H2:H{last},"{st}")' if st != "(not yet done)" else f'=COUNTBLANK(Papers!H2:H{last})'
    g.cell(row=k, column=2, value=f).border = box
g.cell(row=len(STATUSES) + 3, column=1, value="Total").font = Font(bold=True)
g.cell(row=len(STATUSES) + 3, column=2, value=len(rows)).font = Font(bold=True)

wb.active = 1
wb.save(OUT)
print(OUT, len(rows))
