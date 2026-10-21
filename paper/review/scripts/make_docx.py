"""Word version of the main paper (main.tex -> docx/main.docx), matching main.pdf.

    python -E -P paper/review/scripts/make_docx.py        (needs pandoc on PATH, python-docx and pymupdf)

Run after a full LaTeX build (main.aux, main.bbl and main.pdf current). Steps:
1. Flatten main.tex (\\input resolved), drop LaTeX comments (so no "% src" note reaches Word).
2. Resolve every \\ref/\\eqref from main.aux and every \\cite from main.aux's \\bibcite numbers, so section, table,
   figure, equation and citation numbers are those of main.pdf; captions get "Table N." / "Figure N." prefixes.
3. Figures: PDF figures rendered to PNG at 300 dpi; Algorithm 1 cropped from main.pdf as an image.
4. Bibliography: main.bbl (the ACM-Reference-Format output the PDF uses) turned into numbered entries.
5. Placeholders for what the authors supply later ([Zenodo DOI to be added], [GitHub repository link to be added],
   [Funding statement to be added]) are kept and highlighted yellow.
6. pandoc (LaTeX -> docx, equations as Word equations, --number-sections), then a python-docx pass: title block,
   authors, abstract, CCS concepts and keywords, fonts, tables, captions. No line or page numbers are added.
"""
import re
import subprocess
import sys
from pathlib import Path

import fitz
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm

R = Path(__file__).resolve().parents[1]
OUT = R / "docx"
OUT.mkdir(exist_ok=True)
IMG = OUT / "img"
IMG.mkdir(exist_ok=True)

# ---------------------------------------------------------------- aux numbers
aux = (R / "main.aux").read_text(encoding="latin-1")
LAB = {k: v for k, v in re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", aux)}
CIT = {k: int(v) for k, v in re.findall(r"\\bibcite\{([^}]*)\}\{\{(\d+)\}", aux)}


def braced(s, i):
    """s[i] == '{'; return (content, index after closing brace)."""
    assert s[i] == "{", s[i:i + 30]
    depth, j = 0, i
    while True:
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1


def strip_comments(t):
    out = []
    for line in t.split("\n"):
        j = 0
        while True:
            j = line.find("%", j)
            if j < 0:
                break
            if j > 0 and line[j - 1] == "\\":
                j += 1
                continue
            line = line[:j]
            break
        out.append(line)
    return "\n".join(out)


def flatten(path):
    t = strip_comments(path.read_text(encoding="utf-8"))

    def rep(m):
        name = m.group(1)
        p = R / (name if name.endswith(".tex") else name + ".tex")
        return flatten(p)
    return re.sub(r"\\input\{([^}]*)\}", rep, t)


def remove_cmd(t, cmd):
    """Remove \\cmd{...} with balanced braces."""
    while True:
        i = t.find("\\" + cmd + "{")
        if i < 0:
            return t
        _, j = braced(t, i + len(cmd) + 1)
        t = t[:i] + t[j:]


def replace_cmd(t, cmd, fn):
    out, i = [], 0
    pat = "\\" + cmd + "{"
    while True:
        k = t.find(pat, i)
        if k < 0:
            out.append(t[i:])
            return "".join(out)
        arg, j = braced(t, k + len(pat) - 1)
        out.append(t[i:k])
        out.append(fn(arg))
        i = j


src = flatten(R / "main.tex")
pre, body = src.split("\\begin{document}", 1)
body = body.split("\\end{document}", 1)[0]
macros = "\n".join(l for l in pre.split("\n") if l.startswith("\\newcommand{\\") and "todo" not in l and "aud" not in l
                   and "suppTab" not in l)
SUPP = dict(re.findall(r"\\newcommand\{\\(suppTab\w+)\}\{([^}]*)\}", (R / "supprefs.tex").read_text(encoding="utf-8")))

# ---------------------------------------------------------------- front matter (rebuilt in Word later)
title = re.search(r"\\title\[[^\]]*\]\{(.*?)\}\n", body).group(1)
abstract = body[body.index("\\begin{abstract}") + 16:body.index("\\end{abstract}")].strip()
ccs = re.findall(r"\\ccsdesc(?:\[\d+\])?\{([^}]*)\}", body)
keywords = re.search(r"\\keywords\{([^}]*)\}", body).group(1)
body = body[body.index("\\maketitle") + len("\\maketitle"):]

# ---------------------------------------------------------------- algorithm as image (cropped from main.pdf)
pdf = fitz.open(R / "main.pdf")
alg_png = None
for pg in pdf:
    hit = pg.search_for("Algorithm 1:")
    if hit:
        ys = sorted({round(d["rect"].y0, 1) for d in pg.get_drawings() if d["rect"].height < 2 and d["rect"].width > 200})
        top, bot = ys[0] - 3, ys[-1] + 3
        clip = fitz.Rect(40, top, pg.rect.width - 40, bot)
        alg_png = IMG / "algorithm1.png"
        pg.get_pixmap(dpi=300, clip=clip).save(alg_png)
        break
assert alg_png, "Algorithm 1 not found in main.pdf"
a = body.index("\\begin{algorithm}")
b = body.index("\\end{algorithm}") + len("\\end{algorithm}")
body = body[:a] + "\\begin{center}\n\\includegraphics[width=\\linewidth]{" + alg_png.as_posix() + "}\n\\end{center}" + body[b:]


# ---------------------------------------------------------------- figures to PNG
def fig_png(m):
    opts, path = m.group(1) or "", m.group(2)
    p = R / path
    if p.suffix.lower() == ".pdf":
        d = fitz.open(p)
        out = IMG / (p.stem + ".png")
        d[0].get_pixmap(dpi=300).save(out)
        p = out
    return "\\includegraphics" + opts + "{" + p.as_posix() + "}"


body = re.sub(r"\\includegraphics(\[[^\]]*\])?\{([^}]*)\}", fig_png, body)
body = remove_cmd(body, "Description")


# ---------------------------------------------------------------- caption numbers
def number_floats(t, env, word):
    out, i = [], 0
    while True:
        k = t.find("\\begin{" + env, i)
        if k < 0:
            out.append(t[i:])
            return "".join(out)
        e = t.find("\\end{" + env, k)
        blk = t[k:e]
        lab = re.search(r"\\label\{([^}]*)\}", blk)
        if lab and "\\caption{" in blk:
            n = LAB[lab.group(1)]
            c = blk.index("\\caption{")
            blk = blk[:c] + "\\caption{\\textbf{" + word + " " + n + ".} " + blk[c + len("\\caption{"):]
        out.append(t[i:k])
        out.append(blk)
        i = e


for env, word in (("table*", "Table"), ("table}", "Table"), ("figure*", "Figure"), ("figure}", "Figure")):
    body = number_floats(body, env, word)

# equations: append the PDF's equation number
def eq_num(m):
    inner = m.group(2)
    lab = re.search(r"\\label\{([^}]*)\}", inner)
    if lab:
        n = LAB[lab.group(1)]
        inner = inner.replace(lab.group(0), "") + "\\qquad\\text{(" + n + ")}"
    return "\\begin{equation*}" + inner + "\\end{equation*}"


body = re.sub(r"\\begin\{equation(\*?)\}(.*?)\\end\{equation\*?\}", eq_num, body, flags=re.S)

# ---------------------------------------------------------------- refs and cites
body = re.sub(r"\\eqref\{([^}]*)\}", lambda m: "(" + LAB[m.group(1)] + ")", body)
body = re.sub(r"\\ref\{([^}]*)\}", lambda m: LAB[m.group(1)], body)


def cite(m):
    keys = [k.strip() for k in m.group(1).split(",")]
    nums = sorted(CIT[k] for k in keys)
    return "[" + ", ".join(str(n) for n in nums) + "]"


body = re.sub(r"\\cite[pt]?\{([^}]*)\}", cite, body)
for k, v in SUPP.items():
    body = body.replace("\\" + k + "{}", v).replace("\\" + k, v)

# ---------------------------------------------------------------- placeholders and small fixes
PH = {"Zenodo DOI": "[Zenodo DOI to be added]",
      "funding": "[Funding statement, competing-interests statement and acknowledgements to be added]"}


def todo(arg):
    for key, val in PH.items():
        if key.lower() in arg.lower():
            return "\\textbf{" + val + "}"
    return "\\textbf{[" + arg + "]}"


body = replace_cmd(body, "todo", todo)
body = body.replace("\\url{https://github.com/shlokDS16/dlm-review-prisma}", "\\textbf{[GitHub repository link to be added]}")
body = body.replace("\\begin{acks}", "\\section*{Acknowledgments}").replace("\\end{acks}", "")
body = re.sub(r"\\paragraph\{([^}]*)\}", lambda m: "\\textbf{" + m.group(1) + "} ", body)
body = re.sub(r"\\cmidrule(\([a-z]*\))?\{[^}]*\}", "", body)
body = body.replace("\\begin{table*}", "\\begin{table}").replace("\\end{table*}", "\\end{table}")   # pandoc drops table* captions
body = re.sub(r"\\multicolumn\{(\d+)\}\{@\{\}([lcr])(@\{\})?\}", r"\\multicolumn{\1}{\2}", body)   # pandoc cannot parse @{} here
body = body.replace("\\aud{}", "").replace("\\aud", "")
for size in ("footnotesize", "scriptsize", "small", "normalsize"):
    body = body.replace("\\" + size + "\n", "\n").replace("\\" + size + " ", " ")

# ---------------------------------------------------------------- bibliography from main.bbl
bbl = (R / "main.bbl").read_text(encoding="utf-8")
bbl = bbl[bbl.index("\\bibitem"):bbl.index("\\end{thebibliography}")]
entries = re.split(r"\\bibitem\[", bbl)[1:]
refs = []
for e in entries:
    key = re.search(r"\]%?\s*\{([^}]*)\}", e).group(1)
    txt = e[re.search(r"\]%?\s*\{[^}]*\}", e).end():]
    for cmd in ("bibfield", "bibinfo"):
        txt = re.sub(r"\\" + cmd + r"\{[^}]*\}\{", r"\\keep{", txt)
    while "\\keep{" in txt:                              # nested (author list holds per-person fields)
        txt = replace_cmd(txt, "keep", lambda x: x)
    txt = replace_cmd(txt, "showarticletitle", lambda x: x)
    txt = replace_cmd(txt, "showDOI", lambda x: x)
    txt = replace_cmd(txt, "showURL", lambda x: x)
    txt = re.sub(r"\\showeprint\[[^\]]*\]\{([^}]*)\}", r"arXiv:\1", txt)
    txt = txt.replace("\\natexlab{}", "").replace("\\newblock", " ").replace("\\mbox{.}", ".").replace("{and}", "and")
    txt = re.sub(r"\s+", " ", txt).strip()
    refs.append((CIT[key], txt))
refs.sort()
bib = "\\section*{References}\n\n" + "\n\n".join(f"[{n}] {t}" for n, t in refs) + "\n"
body = re.sub(r"\\bibliographystyle\{[^}]*\}", "", body)
body = re.sub(r"\\bibliography\{[^}]*\}", lambda m: bib, body)

tex = ("\\documentclass{article}\n\\usepackage{amsmath}\n" + macros + "\n\\begin{document}\n" + body + "\n\\end{document}\n")
(OUT / "main-flat.tex").write_text(tex, encoding="utf-8")
raw = OUT / "main-pandoc.docx"
cmd = ["pandoc", str(OUT / "main-flat.tex"), "-f", "latex", "-t", "docx", "--number-sections", "-o", str(raw)]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if r.returncode:
    sys.exit("pandoc failed: " + r.stderr[-2000:])
warn = [l for l in r.stderr.splitlines() if l.strip()]

# ---------------------------------------------------------------- Word pass
doc = Document(raw)
st = doc.styles
# theme fonts (Aptos/Calibri) override the font name; drop the theme attributes so Times New Roman applies everywhere
for s in st:
    rpr = s.element.find(qn("w:rPr"))
    if rpr is None:
        continue
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        continue
    for att in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(att)) is not None:
            del rf.attrib[qn(att)]
    rf.set(qn("w:ascii"), "Times New Roman")
    rf.set(qn("w:hAnsi"), "Times New Roman")
for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if name in [s.name for s in st]:
        s = st[name]
        s.font.name, s.font.size = "Times New Roman", Pt(11)
        s.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        s.paragraph_format.space_after = Pt(4)
        s.paragraph_format.line_spacing = 1.15
for lvl, size in ((1, 13), (2, 12), (3, 11)):
    nm = f"Heading {lvl}"
    if nm in [s.name for s in st]:
        s = st[nm]
        s.font.name, s.font.size, s.font.bold = "Times New Roman", Pt(size), True
        s.font.color.rgb = None
        s.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
for nm in ("Caption", "Image Caption", "Table Caption"):
    if nm in [s.name for s in st]:
        s = st[nm]
        s.font.name, s.font.size, s.font.italic = "Times New Roman", Pt(9.5), False

# title block at the start
first = doc.paragraphs[0]


def before(p, text, size=11, bold=False, italic=False, align=None, style=None):
    q = p.insert_paragraph_before("", style=style)
    run = q.add_run(text)
    run.font.size, run.font.bold, run.font.italic, run.font.name = Pt(size), bold, italic, "Times New Roman"
    if align is not None:
        q.alignment = align
    return q


before(first, re.sub(r"\s+", " ", title), 16, bold=True)
authors = [("Shlok Goenka", "shlok.goenka2023@vitstudent.ac.in"),
           ("Subramaniyaswamy Vairavasundaram", "subramaniyaswamy.v@vit.ac.in"),
           ("Balaji G N", "balaji.gn@vit.ac.in")]
before(first, ", ".join(n for n, _ in authors), 12, bold=True)
before(first, "School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, 632014, Tamil Nadu, India", 10, italic=True)
before(first, "; ".join(m for _, m in authors), 10)
before(first, "Abstract", 12, bold=True)
abs_txt = re.sub(r"\s+", " ", abstract)
before(first, abs_txt, 11)
q = before(first, "CCS Concepts: ", 10, bold=True)
r2 = q.add_run("; ".join("\u2022 " + c.replace("~", " \u2192 ") for c in ccs))
r2.font.size, r2.font.name = Pt(10), "Times New Roman"
q = before(first, "Additional Key Words and Phrases: ", 10, bold=True)
r2 = q.add_run(keywords)
r2.font.size, r2.font.name = Pt(10), "Times New Roman"

# placeholders yellow
for p in doc.paragraphs:
    for run in p.runs:
        if "to be added]" in run.text:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW


# tables: booktabs look (top, header, bottom rules), 9 pt
def set_borders(tbl):
    tblPr = tbl._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge, val in (("top", "single"), ("bottom", "single"), ("left", "nil"), ("right", "nil"),
                      ("insideH", "nil"), ("insideV", "nil")):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), val)
        if val == "single":
            el.set(qn("w:sz"), "8")
        b.append(el)
    tblPr.append(b)
    if tbl.rows:
        for cell in tbl.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            cb = OxmlElement("w:tcBorders")
            bt = OxmlElement("w:bottom")
            bt.set(qn("w:val"), "single")
            bt.set(qn("w:sz"), "4")
            cb.append(bt)
            tcPr.append(cb)


for tbl in doc.tables:
    set_borders(tbl)
    for row in tbl.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                for run in p.runs:
                    run.font.size = Pt(9)
                    run.font.name = "Times New Roman"

for sec in doc.sections:
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = sec.bottom_margin = Cm(2.2)
final = OUT / "main.docx"
doc.save(final)
print("written", final, "| pandoc warnings:", len(warn))
for w in warn[:15]:
    print("  ", w[:200])
