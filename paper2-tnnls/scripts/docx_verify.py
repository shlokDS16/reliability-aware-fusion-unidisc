"""Verification of a generated DOCX: structure (sections, columns, styles, equations, tables, figures, links) and a word-level
comparison of its text with `pdftotext` of the compiled PDF (hyphenation, running heads and page numbers ignored)."""
from __future__ import annotations

import collections
import re
import subprocess
import unicodedata
from pathlib import Path

import docx
from docx.oxml.ns import qn

S = "§§"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def doc_paragraph_texts(d) -> list[dict]:
    """Every paragraph of the body (table cells included) in document order: {text, style, in_table, has_math}."""
    out = []
    body = d.element.body
    for p in body.iter(qn("w:p")):
        txt = []
        has_math = False
        for e in p.iter():
            if e.tag == qn("w:t") or e.tag == "{%s}t" % M_NS:
                txt.append(e.text or "")
                if e.tag != qn("w:t"):
                    has_math = True
            elif e.tag == qn("w:tab"):
                txt.append(" ")
            elif e.tag == qn("w:br"):
                txt.append(" ")
        st = p.find(qn("w:pPr") + "/" + qn("w:pStyle"))
        x = p.getparent()
        in_tbl = False
        while x is not None:
            if x.tag == qn("w:tc"):
                in_tbl = True
                break
            x = x.getparent()
        out.append({"text": "".join(txt), "style": st.get(qn("w:val")) if st is not None else None, "in_table": in_tbl,
                    "has_math": has_math})
    return out


def norm_tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("​", "").replace("­", "")
    text = re.sub(r"[\-‐-―−]", "", text)       # hyphens, dashes, minus: removed (pdftotext joins at line ends)
    return re.findall(r"[a-z0-9]+", text)


def pdf_text(pdf: Path) -> str:
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, encoding="utf-8", errors="replace")
    t = r.stdout
    keep = []
    for ln in t.split("\n"):
        s = ln.strip()
        if re.fullmatch(r"IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS", s) or re.fullmatch(r"\d{1,3}", s) or s == "\f":
            continue
        keep.append(ln)
    return "\n".join(keep)


def shingles(tokens: list[str], n: int = 5) -> list[tuple]:
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def structure(d, path: Path) -> list[str]:
    lines = []
    secs = d.sections
    lines.append(f"sections: {len(secs)}")
    for i, s in enumerate(secs):
        cols = s._sectPr.find(qn("w:cols"))
        num = cols.get(qn("w:num")) if cols is not None else None
        widths = [c.get(qn("w:w")) for c in cols.findall(qn("w:col"))] if cols is not None else []
        lines.append(f"  section {i}: columns={num or 1} widths_twips={widths} page={s.page_width.inches:.2f}x{s.page_height.inches:.2f} in "
                     f"margins L{s.left_margin.inches:.2f} R{s.right_margin.inches:.2f} T{s.top_margin.inches:.2f} B{s.bottom_margin.inches:.2f} "
                     f"type={s._sectPr.find(qn('w:type')).get(qn('w:val')) if s._sectPr.find(qn('w:type')) is not None else 'nextPage'}")
    paras = doc_paragraph_texts(d)
    st = collections.Counter(p["style"] for p in paras if not p["in_table"])
    lines.append("paragraph styles (outside tables): " + ", ".join(f"{k}={v}" for k, v in st.most_common()))
    body = d.element.body
    n_tbl = len(list(body.iter(qn("w:tbl"))))
    n_draw = len(list(body.iter(qn("w:drawing"))))
    n_omath = len(list(body.iter("{%s}oMath" % M_NS)))
    eq_paras = [p for p in paras if p["style"] == "Equation"]
    nums = [int(m.group(1)) for p in eq_paras for m in [re.search(r"\((S?\d+)\)\s*$", p["text"].strip())] if m and m.group(1).isdigit()]
    lines.append(f"tables={n_tbl} (floating={len(list(body.iter(qn('w:tblpPr'))))}) drawings={n_draw} OMML math zones={n_omath} "
                 f"equation paragraphs={len(eq_paras)} numbered={len(nums)} sequence_ok={nums == list(range(1, len(nums) + 1))}")
    marks = {b.get(qn("w:name")) for b in body.iter(qn("w:bookmarkStart"))}
    anchors = [h.get(qn("w:anchor")) for h in body.iter(qn("w:hyperlink")) if h.get(qn("w:anchor"))]
    broken = sorted({a for a in anchors if a not in marks})
    lines.append(f"hyperlinks={len(list(body.iter(qn('w:hyperlink'))))} (internal {len(anchors)}, external {len(list(body.iter(qn('w:hyperlink')))) - len(anchors)}) "
                 f"bookmarks={len(marks)} internal links without bookmark={len(broken)} {broken[:5]}")
    sentinel = [p["text"][:60] for p in paras if S in p["text"]]
    lines.append(f"leftover sentinels: {len(sentinel)} {sentinel[:3]}")
    raw_tex = [p["text"][:80] for p in paras if re.search(r"\\[a-zA-Z]{3,}", p["text"]) and not p["has_math"]]
    lines.append(f"paragraphs with a raw LaTeX command left: {len(raw_tex)} {raw_tex[:3]}")
    undefined = [p["text"][:80] for p in paras if "??" in p["text"] or "[?" in p["text"]]
    lines.append(f"undefined reference markers: {len(undefined)} {undefined[:3]}")
    heads = [(p["style"], p["text"]) for p in paras if p["style"] in ("Heading1", "Heading2", "ReferenceHead")]
    lines.append(f"headings: {len(heads)} (H1 {sum(1 for h in heads if h[0] == 'Heading1')}, H2 {sum(1 for h in heads if h[0] == 'Heading2')})")
    refs = [p for p in paras if p["style"] == "References"]
    lines.append(f"reference entries: {len(refs)}")
    tabs = [p["text"] for p in paras if re.match(r"TABLE\s", p["text"])]
    figs = [p["text"][:12] for p in paras if re.match(r"Fig\.\s", p["text"])]
    lines.append(f"table labels: {tabs}; figure captions: {figs}")
    return lines


def compare(d, pdf: Path) -> list[str]:
    paras = doc_paragraph_texts(d)
    # DOCX text: prose paragraphs only for the main figure (math paragraphs and equation numbers carry glyph differences)
    d_tokens_all = norm_tokens(" ".join(p["text"] for p in paras))
    p_text = pdf_text(pdf)
    p_tokens = norm_tokens(p_text)
    out = []
    out.append(f"tokens: pdf={len(p_tokens)} docx={len(d_tokens_all)}")
    dset = collections.Counter(d_tokens_all)
    pc = collections.Counter(p_tokens)
    hit = sum(min(c, dset.get(t, 0)) for t, c in pc.items())
    out.append(f"word recall (PDF words found in DOCX, multiset): {hit / max(len(p_tokens), 1):.4f}")
    dsh = set(shingles(d_tokens_all))
    psh = shingles(p_tokens)
    found = [s in dsh for s in psh]
    out.append(f"5-gram match rate (PDF 5-grams present in DOCX): {sum(found) / max(len(psh), 1):.4f}")
    # prose-only view: words of three or more letters (drops math glyphs, numbers and table cells, whose order differs)
    d_prose = [t for t in d_tokens_all if re.fullmatch(r"[a-z]{3,}", t)]
    p_prose = [t for t in p_tokens if re.fullmatch(r"[a-z]{3,}", t)]
    dpc, ppc = collections.Counter(d_prose), collections.Counter(p_prose)
    out.append(f"prose words (>= 3 letters): pdf={len(p_prose)} docx={len(d_prose)}; recall "
               f"{sum(min(c, dpc.get(t, 0)) for t, c in ppc.items()) / max(len(p_prose), 1):.4f}")
    dsh_p = set(shingles(d_prose))
    psh_p = shingles(p_prose)
    out.append(f"prose 5-gram match rate (PDF prose 5-grams present in DOCX): {sum(1 for s_ in psh_p if s_ in dsh_p) / max(len(psh_p), 1):.4f}")
    mark_p = [False] * len(p_prose)
    for k, s_ in enumerate(psh_p):
        if s_ in dsh_p:
            for j in range(k, k + 5):
                mark_p[j] = True
    pspans, i = [], 0
    while i < len(p_prose):
        if not mark_p[i]:
            j = i
            while j < len(p_prose) and not mark_p[j]:
                j += 1
            pspans.append((i, j))
            i = j
        else:
            i += 1
    plong = [(a, b) for a, b in pspans if b - a >= 4]
    dvocab = set(d_prose)
    order_only = [(a, b) for a, b in plong if all(w in dvocab for w in p_prose[a:b])]
    content = [(a, b) for a, b in plong if (a, b) not in set(order_only)]
    out.append(f"prose spans of the PDF not found in sequence in the DOCX (>= 4 words): {len(plong)}; of these {len(order_only)} have every "
               f"word present in the DOCX (reading order of table cells, figure labels or math only) and {len(content)} contain words absent from the DOCX")
    for a, b in content[:60]:
        miss = sorted({w for w in p_prose[a:b] if w not in dvocab})
        out.append("   CONTENT-MISSING?  absent words " + ", ".join(miss[:8]) + " | " + " ".join(p_prose[max(a - 2, 0):min(b + 2, len(p_prose))])[:160])
    # all-token view (math glyphs and table order make this lower)
    spans, i = [], 0
    mark = [False] * len(p_tokens)
    for k, f in enumerate(found):
        if f:
            for j in range(k, k + 5):
                mark[j] = True
    i = 0
    while i < len(p_tokens):
        if not mark[i]:
            j = i
            while j < len(p_tokens) and not mark[j]:
                j += 1
            spans.append((i, j))
            i = j
        else:
            i += 1
    long_spans = [(a, b) for a, b in spans if b - a >= 6]
    out.append(f"PDF token spans not found in DOCX: {len(spans)} (>= 6 tokens: {len(long_spans)}; tokens in them: {sum(b - a for a, b in long_spans)})")
    for a, b in long_spans[:60]:
        out.append("   MISSING?  " + " ".join(p_tokens[max(a - 2, 0):min(b + 2, len(p_tokens))])[:200])
    # DOCX prose paragraphs absent from the PDF
    psh_set = set(psh)
    bad = []
    for p in paras:
        if p["has_math"] or p["in_table"] or p["style"] in ("Equation",):
            continue
        tk = norm_tokens(p["text"])
        if len(tk) < 8:
            continue
        sh = shingles(tk)
        frac = sum(1 for s in sh if s in psh_set) / max(len(sh), 1)
        if frac < 0.6:
            bad.append((frac, p["text"][:110]))
    out.append(f"DOCX prose paragraphs (no math) with < 60% of 5-grams in the PDF: {len(bad)}")
    for frac, t in sorted(bad)[:25]:
        out.append(f"   {frac:.2f}  {t}")
    return out


def report(docx_path: Path, pdf_path: Path, out_txt: Path):
    d = docx.Document(str(docx_path))
    lines = [f"DOCX: {docx_path}", f"PDF : {pdf_path}", "== structure"] + structure(d, docx_path)
    if Path(pdf_path).exists():
        lines += ["== text comparison with pdftotext"] + compare(d, pdf_path)
    else:
        lines.append("PDF missing: text comparison skipped")
    Path(out_txt).write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:60]))
    print(f"(full report: {out_txt})")


RENDER_PS = r"""
param([string]$In,[string]$Out)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open($In, $false, $true)
  $d.ExportAsFixedFormat($Out, 17)
  "pages: " + $d.ComputeStatistics(2)
  $d.Close($false)
} finally { $w.Quit() }
"""


def render_with_word(docx_path: Path, pdf_out: Path):
    """Export through Microsoft Word (COM). Skipped quietly when Word is not installed."""
    import tempfile
    ps = Path(tempfile.gettempdir()) / "docx_render.ps1"
    ps.write_text(RENDER_PS, encoding="utf-8")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps), "-In", str(docx_path),
                            "-Out", str(pdf_out)], capture_output=True, encoding="utf-8", timeout=300)
        print((r.stdout or "").strip() or (r.stderr or "").strip()[:300])
    except Exception as e:  # noqa: BLE001
        print(f"render skipped: {e}")
