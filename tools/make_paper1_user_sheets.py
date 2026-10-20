"""User sheets for the Paper 1 evening of 2026-10-20 (session 0839c9f4):
 (1) research/review/screening/human-p4/human-p4-sheet-R0308.xlsx: R0308, B-unavailable in R797 (D0041 route), same
     columns as human-p4-sheet.xlsx; screened blind (no screener row shown).
 (2) research/review/screening/d0039-fields/d0039-fields-sheet.xlsx: the 9 records where A and B agreed on the decision
     but set a secondary field differently (D0039); both values shown (the decision is not in question), the author
     picks one per field.
    python tools/make_paper1_user_sheets.py   (openpyxl is a user-site package, so not -I)
"""
import json
from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment, Font

ROOT = Path(__file__).resolve().parents[1]
SCR = ROOT / "analysis/screening"
IDS39 = ["M17653", "M18667", "M17462", "M10840", "M12859", "U04330", "M16043", "M11389", "M18059"]


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def title(i):
    for p, k in ((ROOT / "research/review/corpus/new-records-2026-10-15-v2.jsonl", "nid"),
                 (ROOT / "research/review/corpus/subscription-records-2026-10-15.jsonl", "id"),
                 (ROOT / "research/review/screening/records.jsonl", "sid")):
        for r in jl(p):
            if r[k] == i:
                return r["title"]
    return ""


def start(ws, lines):
    ws.column_dimensions["B"].width = 110
    for n, (a, b) in enumerate(lines, 1):
        ws.cell(n, 1, a).font = Font(bold=True)
        c = ws.cell(n, 2, b)
        c.alignment = Alignment(wrap_text=True, vertical="top")


# (1) R0308
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Start here"
start(ws, [("One paper for you to screen (about 5 minutes)", None),
           (None, "Screener B could not screen this paper in the re-check tranche (a safety filter stopped it twice), "
                  "so the second screener is missing. Under decision D0041 you are the second screener. Screen it blind: "
                  "do not open any screener file for it first."),
           (None, "Fill Decision (include or exclude), Code (X0-X8 if exclude), I1 (a, b or ab if include), one verbatim "
                  "quote of 6-40 words and its page. Criteria: research/review/screening/criteria-v1.6-screener.md section E."),
           (None, "Your decision stands as the protocol s4 step 4 resolution if it differs from screener A (D0046).")])
ws2 = wb.create_sheet("Papers")
hdr = ["No.", "ID", "Title", "PDF (open this)", "Text (search only)", "Decision", "Code", "I1", "Quote (6-40 words)", "Location", "Note"]
ws2.append(hdr)
pdf = next((str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "research/sources/pdfs").rglob("R0308.pdf")), "not found: e-gateway or open access")
ws2.append([1, "R0308", title("R0308"), pdf, "research/sources/md/fulltext-pymupdf/R0308.txt", None, None, None, None, None, None])
for c in ws2[1]:
    c.font = Font(bold=True)
out1 = ROOT / "research/review/screening/human-p4/human-p4-sheet-R0308.xlsx"
wb.save(out1)

# (2) D0039 fields
t1 = {r["id"]: r for r in jl(SCR / "ft-t1/t1-decisions-all.jsonl")}
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Start here"
start(ws, [("Nine field choices (about 15 minutes)", None),
           (None, "Screeners A and B agreed on the decision for each of these papers but recorded one secondary field "
                  "differently (exclusion code, I1 basis, or whether the output is non-language only). The counts now use "
                  "A's value (D0039). Open the PDF, pick the value you think is right in column 'Your value', and note why if useful."),
           (None, "Codes: X0 no diffusion component; X1 non-text diffusion; X2 text only as conditioning; X3 secondary "
                  "study; X4 no method/theory/result. I1: a text-output diffusion model; b unified understanding+generation "
                  "model; ab both.")])
ws2 = wb.create_sheet("Records")
ws2.append(["No.", "ID", "Title", "Decision (agreed)", "Field", "Screener A", "Screener B", "Your value", "Note", "PDF"])
n = 0
for i in IDS39:
    r = t1[i]
    rows = {who: next((x for x in jl(SCR / "ft-t1" / r["batch"] / f"F{who}-{r['batch']}.jsonl") if x["id"] == i), {})
            for who in "AB"}
    for fld in ("code", "i1", "nonlang_only"):
        a, b = rows["A"].get(fld), rows["B"].get(fld)
        if a != b:
            n += 1
            pdf = next((str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "research/sources/pdfs").rglob(f"{i}.pdf")), "")
            ws2.append([n, i, title(i), r["decision"], fld, str(a), str(b), None, None, pdf])
for c in ws2[1]:
    c.font = Font(bold=True)
out2 = ROOT / "research/review/screening/d0039-fields/d0039-fields-sheet.xlsx"
out2.parent.mkdir(exist_ok=True)
wb.save(out2)
print(out1, out2, "field rows", n)
