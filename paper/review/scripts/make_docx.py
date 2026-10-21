"""Word version of the main paper (main.tex -> docx/main.docx), matching main.pdf.

    python -E -P paper/review/scripts/make_docx.py        (needs pandoc on PATH, python-docx and pymupdf)

Run after a full LaTeX build (main.aux, main.bbl and main.pdf current). Steps:
1. Flatten main.tex (\\input resolved), drop LaTeX comments (so no "% src" note reaches Word).
2. Resolve every \\ref/\\eqref from main.aux and every \\cite from main.aux's \\bibcite numbers, so section, table,
   figure, equation and citation numbers are those of main.pdf; captions get "Table N." / "Figure N." prefixes.
3. Figures: PDF figures rendered to PNG at 300 dpi; Algorithm 1 cropped from main.pdf as an image.
4. Bibliography: main.bbl (the ACM-Reference-Format output the PDF uses) turned into numbered entries. Each entry
   carries a bookmark ref_n; every in-text citation number is an internal hyperlink to it, and every DOI, URL and
   arXiv identifier is an external hyperlink (pandoc's "Hyperlink" character style: blue, underlined).
5. Placeholders for what the authors supply later ([Funding statement ... to be added]) are kept and highlighted
   yellow.
6. pandoc (LaTeX -> docx, equations as Word equations, --number-sections), then a python-docx pass: title block,
   authors, abstract, CCS concepts and keywords, fonts, tables, captions. No line or page numbers are added.
"""
import re
import subprocess
import sys
from pathlib import Path

import fitz
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.text.paragraph import Paragraph
from docx.text.run import Run
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
    # each number is an internal link to its reference entry (bookmark ref_n, set in the bibliography below)
    keys = [k.strip() for k in m.group(1).split(",")]
    nums = sorted(CIT[k] for k in keys)
    return "[" + ", ".join(f"\\hyperlink{{ref_{n}}}{{{n}}}" for n in nums) + "]"


body = re.sub(r"\\cite[pt]?\{([^}]*)\}", cite, body)
for k, v in SUPP.items():
    body = body.replace("\\" + k + "{}", v).replace("\\" + k, v)

# ---------------------------------------------------------------- placeholders and small fixes
PH = {"funding":"[Funding statement, competing-interests statement and acknowledgements to be added]"}


def todo(arg):
    for key, val in PH.items():
        if key.lower() in arg.lower():
            return "\\textbf{" + val + "}"
    return "\\textbf{[" + arg + "]}"


body = replace_cmd(body, "todo", todo)
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
    txt = re.sub(r"\\showeprint\[[^\]]*\]\{([^}]*)\}", r"\\href{https://arxiv.org/abs/\1}{arXiv:\1}", txt)
    txt = replace_cmd(txt, "nolinkurl", lambda x: x)   # DOI link text as plain text (not monospace)
    txt = txt.replace("\\natexlab{}", "").replace("\\newblock", " ").replace("\\mbox{.}", ".").replace("{and}", "and")
    txt = re.sub(r"\s+", " ", txt).strip()
    refs.append((CIT[key], txt))
refs.sort()
bib = "\\section*{References}\n\n" + "\n\n".join(f"[\\hypertarget{{ref_{n}}}{{{n}}}] {t}" for n, t in refs) + "\n"
body = re.sub(r"\\bibliographystyle\{[^}]*\}", "", body)
body = re.sub(r"\\bibliography\{[^}]*\}", lambda m: bib, body)


# ---------------------------------------------------------------- table column specs (used for Word column widths)
def tab_specs(t):
    """[(columns, header_rows)] for every tabular in order; a column is ('p', width_cm) or ('l'|'r'|'c', None)."""
    out, i = [], 0
    while True:
        k = t.find("\\begin{tabular}", i)
        if k < 0:
            return out
        spec, j = braced(t, k + len("\\begin{tabular}"))
        e = t.find("\\end{tabular}", j)
        cols, s = [], 0
        while s < len(spec):
            c = spec[s]
            if c == "@":
                _, s = braced(spec, s + 1)
                continue
            if c in "pmb" and spec[s + 1:s + 2] == "{":
                w, s = braced(spec, s + 1)
                m = re.match(r"([\d.]*)\\(?:linewidth|textwidth)", w)
                cols.append(("p", float(m.group(1) or 1) * 13.97 if m else float(w.replace("cm", ""))))
                continue
            if c in "lrc":
                cols.append((c, None))
            s += 1
        inner = t[j:e]
        mid = inner.find("\\midrule")
        out.append((cols, inner[:mid].count("\\\\") if mid >= 0 else 1))
        i = e


TABSPECS = tab_specs(body)

tex = ("\\documentclass{article}\n\\usepackage{amsmath}\n" + macros + "\n\\begin{document}\n" + body + "\n\\end{document}\n")
(OUT / "main-flat.tex").write_text(tex, encoding="utf-8")
raw = OUT / "main-pandoc.docx"
cmd = ["pandoc", str(OUT / "main-flat.tex"), "-f", "latex", "-t", "docx", "--number-sections", "-o", str(raw)]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if r.returncode:
    sys.exit("pandoc failed: " + r.stderr[-2000:])
warn = [l for l in r.stderr.splitlines() if l.strip()]

# ---------------------------------------------------------------- Word pass
# Layout follows the authors' earlier Word manuscripts (A4, 2.5 cm margins, Times New Roman, justified text,
# Body Text / First Paragraph with a first-line indent, bold "Figure N." / "Table N." captions, centred booktabs
# tables, hanging-indent references) and main.pdf (no space between paragraphs, indent except after a heading,
# figure or table, equation numbers at the right margin).
TEXT_W = 16.0                     # cm: A4 width 21 cm minus 2 x 2.5 cm margins
MAX_FIG_H = 20.0                  # cm: page body is 24.7 cm; leaves room for the caption on the same page
ACM_TEXT_W = 13.97                # cm: \linewidth in acmsmall, the unit pandoc used for image sizes
EMU, DXA = 360000, 1440 / 2.54    # per cm
MNS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
TNR = fitz.Font(fontfile="C:/Windows/Fonts/times.ttf")
TNRB = fitz.Font(fontfile="C:/Windows/Fonts/timesbd.ttf")

doc = Document(raw)
st = doc.styles
body_el = doc.element.body
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


def lname(el):
    return el.tag.split("}")[1] if isinstance(el.tag, str) and "}" in el.tag else ""


def put(parent, child, order):
    """Insert or replace child in parent, keeping the schema order given as a list of local names."""
    old = parent.find(child.tag)
    if old is not None:
        parent.replace(old, child)
        return child
    idx = order.index(lname(child))
    for ex in parent:
        ln = lname(ex)
        if ln in order and order.index(ln) > idx:
            ex.addprevious(child)
            return child
    parent.append(child)
    return child


def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn("w:" + k), str(v))
    return e


def sty(name):
    return st[name] if name in [s.name for s in st] else None


def fmt(name, size=None, bold=None, italic=None, align=None, sb=None, sa=None, ls=None, first=None, left=None,
        kwn=None, base=None):
    s = sty(name)
    if s is None:
        s = st.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = st[base or "Normal"]
    f, pf = s.font, s.paragraph_format
    f.name = "Times New Roman"
    if size is not None:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if align is not None:
        pf.alignment = align
    if sb is not None:
        pf.space_before = Pt(sb)
    if sa is not None:
        pf.space_after = Pt(sa)
    if ls is not None:
        pf.line_spacing = ls
    if first is not None:
        pf.first_line_indent = Cm(first)
    if left is not None:
        pf.left_indent = Cm(left)
    if kwn is not None:
        pf.keep_with_next = kwn
    return s


J, C, L, RIGHT = WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT
fmt("Normal", 11, align=J, sb=0, sa=0, ls=1.15)
st["Normal"].element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st["Normal"].paragraph_format.widow_control = True
fmt("Body Text", sb=0, sa=0, first=0.5)
fmt("First Paragraph", first=0)
fmt("Compact", 9, align=L, sb=1, sa=1, ls=1.0, first=0)                 # pandoc's style for table cells
for lvl, size, ital, sb, sa, tab in ((1, 13, False, 18, 6, 1.0), (2, 11.5, False, 12, 4, 1.15), (3, 11, True, 10, 3, 1.4)):
    h = fmt(f"Heading {lvl}", size, bold=True, italic=ital, align=L, sb=sb, sa=sa, ls=1.0, first=0, left=0, kwn=True)
    h.font.color.rgb = None
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    h.paragraph_format.keep_together = True
    h.paragraph_format.tab_stops.add_tab_stop(Cm(tab))
fmt("Caption", 10, italic=False, align=J, ls=1.0, first=0)
fmt("Image Caption", 10, italic=False, align=J, sb=4, sa=12, ls=1.0, first=0)
fmt("Table Caption", 10, italic=False, align=J, sb=12, sa=5, ls=1.0, first=0, kwn=True)
fmt("Figure", align=C, sb=12, sa=0, first=0, kwn=True)
fmt("Captioned Figure", align=C, sb=12, sa=0, first=0, kwn=True)
fmt("Definition Term", bold=True, align=L, sb=4, sa=0, first=0, kwn=True)
fmt("Definition", align=J, sb=0, sa=2, first=0, left=0.6)
fmt("Equation", align=C, sb=4, sa=4, ls=1.0, first=0, left=0)
fmt("Reference", 9.5, align=L, sb=0, sa=3, ls=1.0, first=-0.8, left=0.8)
fmt("Front Matter", 10, align=J, sb=0, sa=0, ls=1.15, first=0)
# \texttt (pandoc's Verbatim Char) takes the size of its paragraph, so it is 9 pt inside tables
vc = sty("Verbatim Char")
if vc is not None:
    vc.font.size = None
    vc.font.name = "Consolas"
for nm in ("Compact", "Reference", "Front Matter", "Heading 1", "Heading 2", "Heading 3", "Definition Term"):
    # no automatic hyphenation in cells, references, the title block or headings
    put(st[nm].element.get_or_add_pPr(), el("w:suppressAutoHyphens"), ["pStyle", "keepNext", "keepLines",
        "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
        "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
        "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
        "suppressOverlap", "jc"])

# justified text reads better with hyphenation, as in the PDF
settings = doc.settings.element
put(settings, el("w:autoHyphenation"), ["writeProtection", "view", "zoom", "removePersonalInformation",
    "removeDateAndTime", "doNotDisplayPageBoundaries", "displayBackgroundShape", "printPostScriptOverText",
    "printFractionalCharacterWidth", "printFormsData", "embedTrueTypeFonts", "embedSystemFonts", "saveSubsetFonts",
    "saveFormsData", "mirrorMargins", "alignBordersAndEdges", "bordersDoNotSurroundHeader",
    "bordersDoNotSurroundFooter", "gutterAtTop", "hideSpellingErrors", "hideGrammaticalErrors", "activeWritingStyle",
    "proofState", "formsDesign", "attachedTemplate", "linkStyles", "stylePaneFormatFilter", "stylePaneSortMethod",
    "documentType", "mailMerge", "revisionView", "trackRevisions", "doNotTrackMoves", "doNotTrackFormatting",
    "documentProtection", "autoFormatOverride", "styleLockTheme", "styleLockQFSet", "defaultTabStop",
    "autoHyphenation", "consecutiveHyphenLimit", "hyphenationZone", "doNotHyphenateCaps"])


def pstyle(p_el):
    ppr = p_el.find(qn("w:pPr"))
    ps = ppr.find(qn("w:pStyle")) if ppr is not None else None
    return ps.get(qn("w:val")) if ps is not None else None


def set_pstyle(p_el, sid):
    ppr = p_el.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p_el.insert(0, ppr)
    ps = ppr.find(qn("w:pStyle"))
    if ps is None:
        ps = OxmlElement("w:pStyle")
        ppr.insert(0, ps)
    ps.set(qn("w:val"), sid)


def has_drawing(p_el):
    return p_el.find(".//" + qn("w:drawing")) is not None


# ---- paragraph after a figure, a table or the algorithm starts flush left (First Paragraph), as after a heading
prev = None
for ch in list(body_el):
    ln = lname(ch)
    if ln in ("bookmarkStart", "bookmarkEnd"):
        continue
    if ln == "p" and prev is not None and pstyle(ch) == "BodyText" and not has_drawing(ch):
        pl = lname(prev)
        if pl == "tbl" or (pl == "p" and (has_drawing(prev) or pstyle(prev) in ("ImageCaption", "TableCaption"))):
            set_pstyle(ch, "FirstParagraph")
    if ln == "p" and prev is not None and lname(prev) == "tbl":
        Paragraph(ch, None).paragraph_format.space_before = Pt(12)      # air below the table's bottom rule
    prev = ch

# ---- figures: scaled to the text width (aspect kept, height capped), centred, kept with the caption
for p in doc.paragraphs:
    if not has_drawing(p._p):
        continue
    for inline in p._p.iter(WP + "inline"):
        ext = inline.find(WP + "extent")
        w, h = int(ext.get("cx")) / EMU, int(ext.get("cy")) / EMU
        k = min(TEXT_W / ACM_TEXT_W, TEXT_W / w, MAX_FIG_H / h)
        cx, cy = int(w * k * EMU), int(h * k * EMU)
        ext.set("cx", str(cx))
        ext.set("cy", str(cy))
        for aext in inline.iter(A + "ext"):
            if aext.get("cx") is not None:
                aext.set("cx", str(cx))
                aext.set("cy", str(cy))
    pf = p.paragraph_format
    pf.alignment, pf.first_line_indent, pf.left_indent = C, Cm(0), Cm(0)
    if p.style.name not in ("Captioned Figure", "Figure"):            # Algorithm 1 (its caption is in the image)
        pf.space_before, pf.space_after = Pt(10), Pt(10)

# ---- numbered list items: a little air between items
for p in doc.paragraphs:
    if p._p.find(qn("w:pPr")) is not None and p._p.find(qn("w:pPr")).find(qn("w:numPr")) is not None:
        p.paragraph_format.space_after = Pt(2)

# ---- tables: widths from the LaTeX column specs and the measured text, booktabs rules, bold header, 9 pt
TBLPR = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc",
         "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption",
         "tblDescription"]
TCPR = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection",
        "tcFitText", "vAlign", "hideMark"]
TRPR = ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter", "cantSplit", "trHeight", "tblHeader",
        "tblCellSpacing", "jc", "hidden"]
NUM = re.compile(r"^[\d\s.,;:\[\]/=%()+\u2013\u2212\u2009\u00a0-]*\d[\d\s.,;:\[\]/=%()+\u2013\u2212\u2009\u00a0-]*$")
PAD = 0.32                        # cm per column: two 0.1 cm cell margins plus slack


def cell_text(tc):
    return ["".join(t.text or "" for t in p.iter(qn("w:t"), MNS + "t")) for p in tc.iter(qn("w:p"))]


def borders(tag, **edges):
    b = OxmlElement(tag)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge in edges:
            v = edges[edge]
            e = el("w:" + edge, val="single" if v else "nil")
            if v:
                e.set(qn("w:sz"), str(v))
                e.set(qn("w:space"), "0")
                e.set(qn("w:color"), "000000")
            b.append(e)
    return b


def table_grid(tbl, widths):
    grid = tbl.find(qn("w:tblGrid"))
    for g in list(grid):
        grid.remove(g)
    for w in widths:
        grid.append(el("w:gridCol", w=int(round(w * DXA))))
    tblPr = tbl.find(qn("w:tblPr"))
    put(tblPr, el("w:tblW", w=int(round(sum(widths) * DXA)), type="dxa"), TBLPR)
    put(tblPr, el("w:jc", val="center"), TBLPR)
    put(tblPr, el("w:tblLayout", type="fixed"), TBLPR)


data_tables = [t._tbl for t in doc.tables]
assert len(data_tables) == len(TABSPECS), (len(data_tables), len(TABSPECS))
table_sizes = []
for tbl, (cols, nhead) in zip(data_tables, TABSPECS):
    n = len(cols)
    rows = tbl.findall(qn("w:tr"))
    cells = []                                                          # (row, tc, first column, span)
    for ri, tr in enumerate(rows):
        c = 0
        for tc in tr.findall(qn("w:tc")):
            gs = tc.find(qn("w:tcPr")).find(qn("w:gridSpan")) if tc.find(qn("w:tcPr")) is not None else None
            span = int(gs.get(qn("w:val"))) if gs is not None else 1
            cells.append((ri, tc, c, span))
            c += span
        assert c == n, ("column count", c, n)
    numeric = []
    for ci in range(n):
        vals = [" ".join(cell_text(tc)).strip() for ri, tc, c, sp in cells if c == ci and sp == 1 and ri >= nhead]
        vals = [v for v in vals if v and v not in ("NA", "\u2014", "-")]
        numeric.append(bool(vals) and all(NUM.match(v) for v in vals))

    def layout(size):
        nat, minw = [0.0] * n, [0.0] * n
        for ri, tc, c, sp in cells:
            if sp != 1:
                continue
            font = TNRB if ri < nhead else TNR
            for line in cell_text(tc):
                nat[c] = max(nat[c], font.text_length(line, fontsize=size) / 72 * 2.54)
                for word in line.split():
                    minw[c] = max(minw[c], font.text_length(word, fontsize=size) / 72 * 2.54)
        ps = [i for i in range(n) if cols[i][0] == "p"]
        widths = [nat[i] + PAD for i in range(n)]
        if ps:                                                          # paragraph columns share what is left
            fixed = sum(widths[i] for i in range(n) if i not in ps)
            psum = sum(cols[i][1] for i in ps)
            for i in ps:
                widths[i] = (TEXT_W - fixed) * cols[i][1] / psum
            ok = all(widths[i] >= minw[i] + PAD for i in ps)
            return widths, ok
        if sum(widths) <= TEXT_W:
            return widths, True
        # too wide: text columns may wrap (never below their longest word); numeric columns never wrap
        slack = [(widths[i] - minw[i] - PAD) if not numeric[i] else 0 for i in range(n)]
        need = sum(widths) - TEXT_W
        if sum(slack) < need:
            return widths, False
        for i in range(n):
            widths[i] -= need * slack[i] / sum(slack)
        return widths, True

    for size in (9, 8.5, 8):
        widths, ok = layout(size)
        if ok:
            break
    table_sizes.append(size)
    table_grid(tbl, widths)
    tblPr = tbl.find(qn("w:tblPr"))
    put(tblPr, borders("w:tblBorders", top=8, bottom=8, left=0, right=0, insideH=0, insideV=0), TBLPR)
    mar = OxmlElement("w:tblCellMar")
    for edge, v in (("top", 0), ("left", 57), ("bottom", 0), ("right", 57)):
        mar.append(el("w:" + edge, w=v, type="dxa"))
    put(tblPr, mar, TBLPR)
    for ri, tc, c, sp in cells:
        tcPr = tc.find(qn("w:tcPr"))
        if tcPr is None:
            tcPr = OxmlElement("w:tcPr")
            tc.insert(0, tcPr)
        put(tcPr, el("w:tcW", w=int(round(sum(widths[c:c + sp]) * DXA)), type="dxa"), TCPR)
        if ri == nhead - 1:                                             # rule under the header (booktabs \midrule)
            put(tcPr, borders("w:tcBorders", bottom=4), TCPR)
        elif ri < nhead - 1 and sp > 1 and "".join(cell_text(tc)).strip():   # \cmidrule under spanning headings
            put(tcPr, borders("w:tcBorders", bottom=4), TCPR)
        put(tcPr, el("w:vAlign", val="top" if ri >= nhead else "bottom"), TCPR)
        for p in tc.iter(qn("w:p")):
            pp = Paragraph(p, None)
            if sp > 1 and ri < nhead:
                pp.alignment = C
            elif numeric[c] and sp == 1:
                pp.alignment = RIGHT
            pp.paragraph_format.keep_with_next = ri < len(rows) - 1      # keep the table on one page where it fits
        for r in tc.iter(qn("w:r")):
            rr = Run(r, None)
            if size != 9:
                rr.font.size = Pt(size)
            if ri < nhead:
                rr.font.bold = True
    for ri, tr in enumerate(rows):
        trPr = tr.find(qn("w:trPr"))
        if trPr is None:
            trPr = OxmlElement("w:trPr")
            tr.insert(0, trPr)
        put(trPr, el("w:cantSplit"), TRPR)
        if ri < nhead:
            put(trPr, el("w:tblHeader"), TRPR)

# ---- numbered equations: borderless three-cell row, equation centred, number at the right margin
# cm: the number cell fits "(7)"; a narrow left cell leaves 15 cm, so equations (4) and (7) (about 14.5 cm in Times
# New Roman 11 pt) stay on one line, at the cost of centring them 2 mm left of the text centre
EQ_LEFT, EQ_RIGHT = 0.25, 0.75
eq_count = 0
for mp in list(body_el.iter(MNS + "oMathPara")):
    p_el = mp.getparent()
    if lname(p_el) != "p":
        continue
    set_pstyle(p_el, "Equation")
    ppr = p_el.find(qn("w:pPr"))
    for tag in ("w:ind", "w:jc", "w:numPr"):
        x = ppr.find(qn(tag))
        if x is not None:
            ppr.remove(x)
    runs = list(mp.iter(MNS + "r"))
    last = "".join(t.text or "" for t in runs[-1].iter(MNS + "t")) if runs else ""
    if not re.fullmatch(r"\(\d+\)", last):
        continue
    parent = runs[-1].getparent()
    parent.remove(runs[-1])
    if len(runs) > 1 and not "".join(t.text or "" for t in runs[-2].iter(MNS + "t")).strip():
        runs[-2].getparent().remove(runs[-2])                         # the \qquad before the number
    tbl = OxmlElement("w:tbl")
    tblPr = OxmlElement("w:tblPr")
    tbl.append(tblPr)
    tblPr.append(el("w:tblW", w=int(round(TEXT_W * DXA)), type="dxa"))
    tblPr.append(el("w:jc", val="center"))
    tblPr.append(borders("w:tblBorders", top=0, left=0, bottom=0, right=0, insideH=0, insideV=0))
    tblPr.append(el("w:tblLayout", type="fixed"))
    mar = OxmlElement("w:tblCellMar")
    for edge in ("left", "right"):
        mar.append(el("w:" + edge, w=0, type="dxa"))
    tblPr.append(mar)
    look = el("w:tblLook", val="0000", firstRow=0, lastRow=0, firstColumn=0, lastColumn=0, noHBand=1, noVBand=1)
    tblPr.append(look)
    tblPr.append(el("w:tblDescription", val="Equation " + last))
    grid = OxmlElement("w:tblGrid")
    ws = (EQ_LEFT, TEXT_W - EQ_LEFT - EQ_RIGHT, EQ_RIGHT)
    for w in ws:
        grid.append(el("w:gridCol", w=int(round(w * DXA))))
    tbl.append(grid)
    tr = OxmlElement("w:tr")
    tr.append(el("w:trPr"))
    tr[0].append(el("w:cantSplit"))
    tbl.append(tr)
    p_el.addprevious(tbl)
    for i, w in enumerate(ws):
        tc = OxmlElement("w:tc")
        tcPr = OxmlElement("w:tcPr")
        tcPr.append(el("w:tcW", w=int(round(w * DXA)), type="dxa"))
        tcPr.append(el("w:vAlign", val="center"))
        tc.append(tcPr)
        if i == 1:
            tc.append(p_el)
        else:
            q = OxmlElement("w:p")
            tc.append(q)
            qq = Paragraph(q, None)
            set_pstyle(q, "Equation")
            if i == 2:
                qq.alignment = RIGHT
                qq.add_run(last)
        tr.append(tc)
    eq_count += 1

# ---- references: hanging indent, label then a tab, 9.5 pt; links kept
in_refs = False
n_refs = 0
for p in doc.paragraphs:
    if p.style.name.startswith("Heading"):
        in_refs = p.text.strip() == "References"
        continue
    if not in_refs or not p.text.strip():
        continue
    set_pstyle(p._p, "Reference")
    p.paragraph_format.first_line_indent = None
    n_refs += 1
    for t in p._p.iter(qn("w:t")):
        if t.text and "] " in t.text:
            before_, after_ = t.text.split("] ", 1)
            t.text = before_ + "]"
            tab = OxmlElement("w:tab")
            t.addnext(tab)
            t2 = OxmlElement("w:t")
            t2.text = after_
            t2.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            tab.addnext(t2)
            break

# ---- title block at the start (centred, as in the authors' earlier manuscripts)
first = doc.paragraphs[0]


def before(p, text, size=11, bold=False, italic=False, align=None, sb=0, sa=0, style="Front Matter"):
    q = p.insert_paragraph_before("", style=style)
    run = q.add_run(text)
    run.font.size, run.font.bold, run.font.italic, run.font.name = Pt(size), bold, italic, "Times New Roman"
    if align is not None:
        q.alignment = align
    q.paragraph_format.space_before, q.paragraph_format.space_after = Pt(sb), Pt(sa)
    return q


before(first, re.sub(r"\s+", " ", title), 16, bold=True, align=C, sa=14).paragraph_format.line_spacing = 1.0
authors = [("Shlok Goenka", "shlok.goenka2023@vitstudent.ac.in"),
           ("Subramaniyaswamy Vairavasundaram", "subramaniyaswamy.v@vit.ac.in"),
           ("Balaji G N", "balaji.gn@vit.ac.in")]
before(first, ", ".join(n for n, _ in authors), 12, bold=True, align=C, sa=6)
before(first, "School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, 632014, Tamil Nadu, India", 10, italic=True, align=C, sa=3)
before(first, "; ".join(m for _, m in authors), 10, align=C, sa=18)
before(first, "Abstract", 11, bold=True, align=L, sa=4)
abs_txt = re.sub(r"\s+", " ", abstract)
before(first, abs_txt, 10, align=J, sa=8)
q = before(first, "CCS Concepts: ", 10, bold=True, align=J, sa=4)
r2 = q.add_run("; ".join("\u2022 " + c.replace("~", " \u2192 ") for c in ccs))
r2.font.size, r2.font.name = Pt(10), "Times New Roman"
q = before(first, "Additional Key Words and Phrases: ", 10, bold=True, align=J, sa=6)
r2 = q.add_run(keywords)
r2.font.size, r2.font.name = Pt(10), "Times New Roman"
put(q._p.get_or_add_pPr(), borders("w:pBdr", bottom=6), ["pStyle", "keepNext", "keepLines", "pageBreakBefore",
    "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
    "spacing", "ind", "jc"])
q._p.get_or_add_pPr().find(qn("w:pBdr")).find(qn("w:bottom")).set(qn("w:space"), "8")

# placeholders yellow
for p in doc.paragraphs:
    for run in p.runs:
        if "to be added]" in run.text:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW

for sec in doc.sections:
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.5)
    sec.top_margin = sec.bottom_margin = Cm(2.5)
    sec.header_distance = sec.footer_distance = Cm(1.25)
final = OUT / "main.docx"
doc.save(final)
print("written", final, "| pandoc warnings:", len(warn), "| equations numbered:", eq_count, "| references:", n_refs,
      "| table font sizes:", table_sizes)
for w in warn[:15]:
    print("  ", w[:200])
