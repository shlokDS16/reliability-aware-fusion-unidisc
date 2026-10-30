"""python-docx post-processing of the pandoc output: IEEE styles, two-section / two-column layout from the template's own
sectPr, equation tabs, floating wide tables and figures, booktabs-like rules, list indents, metadata scrub."""
from __future__ import annotations

import copy
import re
from pathlib import Path

import docx
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Twips
from docx.text.paragraph import Paragraph

S = "§§"
COL_W = 5040          # twips, one column of the template (3.5 in)
PAGE_TEXT_W = 10368   # twips, page text width of the template (7.2 in)


def W(tag):
    return qn("w:" + tag)


def el(tag, **attrs):
    e = OxmlElement("w:" + tag)
    for k, v in attrs.items():
        e.set(qn("w:" + k), str(v))
    return e


def pstyle_of(p) -> str | None:
    ppr = p.find(W("pPr"))
    if ppr is None:
        return None
    ps = ppr.find(W("pStyle"))
    return ps.get(W("val")) if ps is not None else None


def set_pstyle(p, style_id: str):
    ppr = p.find(W("pPr"))
    if ppr is None:
        ppr = el("pPr")
        p.insert(0, ppr)
    ps = ppr.find(W("pStyle"))
    if ps is None:
        ps = el("pStyle")
        ppr.insert(0, ps)
    ps.set(W("val"), style_id)


def ptext(p) -> str:
    return "".join(t.text or "" for t in p.iter(W("t")))


def in_table(p) -> bool:
    x = p.getparent()
    while x is not None:
        if x.tag == W("tc"):
            return True
        x = x.getparent()
    return False


class Poster:
    def __init__(self, raw: Path, specs: dict, anon: bool, title: str, unit: str = "main"):
        self.unit = unit
        self.col_w = PAGE_TEXT_W if unit == "supplement" else COL_W
        self.doc = docx.Document(str(raw))
        self.body = self.doc.element.body
        self.specs = {int(k): v for k, v in specs.items()}
        self.anon = anon
        self.title = title
        self.log: list[str] = []
        self.table_styles: dict[int, str] = {}

    # ----- styles -----
    def style(self, name: str, kind=WD_STYLE_TYPE.PARAGRAPH, base: str | None = "Normal"):
        try:
            return self.doc.styles[name]
        except KeyError:
            st = self.doc.styles.add_style(name, kind)
            if base:
                st.base_style = self.doc.styles[base]
            return st

    def sid(self, name: str) -> str:
        return self.doc.styles[name].style_id

    def ensure_styles(self):
        st = self.style("Figure Image")
        st.paragraph_format.alignment = 1
        st.paragraph_format.space_before = Pt(2)
        st.paragraph_format.space_after = Pt(2)
        st.paragraph_format.keep_with_next = True
        for name, size in (("Table Text", 7), ("Table Note", 7)):
            st = self.style(name)
            st.font.size = Pt(size)
            st.paragraph_format.space_before = Pt(0)
            st.paragraph_format.space_after = Pt(0)
        self.doc.styles["Table Note"].paragraph_format.alignment = 3
        fc = self.doc.styles["Figure Caption"]
        fc.paragraph_format.space_before = Pt(2)
        fc.paragraph_format.space_after = Pt(4)
        tt = self.doc.styles["Table Title"]
        tt.paragraph_format.space_after = Pt(2)
        todo = self.style("Todo", WD_STYLE_TYPE.CHARACTER, None)
        todo.font.bold = True
        from docx.enum.text import WD_COLOR_INDEX
        todo.font.highlight_color = WD_COLOR_INDEX.YELLOW
        vb = self.style("Verbatim Char", WD_STYLE_TYPE.CHARACTER, None)
        vb.font.name = "Courier New"
        vb.font.size = Pt(8)
        rpr = vb.element.get_or_add_rPr()
        rf = rpr.find(W("rFonts"))
        if rf is None:
            rf = el("rFonts")
            rpr.insert(0, rf)
        for a in ("ascii", "hAnsi", "cs", "eastAsia"):
            rf.set(W(a), "Courier New")
        # all hyperlinks blue, no underline (as the blue links of the PDF)
        try:
            hl = self.doc.styles["Hyperlink"]
            from docx.shared import RGBColor
            hl.font.color.rgb = RGBColor(0x00, 0x00, 0xFF)
            hl.font.underline = False
        except KeyError:
            pass

    # ----- paragraph pass -----
    def paragraph_pass(self):
        for p in list(self.body.iter(W("p"))):
            sid = pstyle_of(p)
            intable = in_table(p)
            text = ptext(p)
            ppr = p.find(W("pPr"))
            if sid in ("BodyText", "FirstParagraph", "Compact", None, "Normal") and not intable:
                numpr = ppr.find(W("numPr")) if ppr is not None else None
                set_pstyle(p, "Text")
                if numpr is not None:
                    para = Paragraph(p, None)
                    para.paragraph_format.left_indent = Twips(360)
                    para.paragraph_format.first_line_indent = Twips(-360)
            if sid in ("Heading2", "Heading3"):
                self._set_numpr(p, 0, 0)
            if sid == self.sid("References"):
                self._set_numpr(p, 1, 0)
                para = Paragraph(p, None)
                para.paragraph_format.left_indent = Twips(270)
                para.paragraph_format.first_line_indent = Twips(-270)
            if text.startswith(S + "CONT" + S):
                self._strip_prefix(p, S + "CONT" + S)
                Paragraph(p, None).paragraph_format.first_line_indent = Twips(0)

    @staticmethod
    def _set_numpr(p, num_id: int, ilvl: int):
        ppr = p.find(W("pPr"))
        if ppr is None:
            ppr = el("pPr")
            p.insert(0, ppr)
        old = ppr.find(W("numPr"))
        if old is not None:
            ppr.remove(old)
        np_ = el("numPr")
        np_.append(el("ilvl", val=ilvl))
        np_.append(el("numId", val=num_id))
        idx = 0
        for k, ch in enumerate(ppr):
            if ch.tag in (W("pStyle"), W("keepNext"), W("keepLines"), W("pageBreakBefore"), W("framePr"), W("widowControl")):
                idx = k + 1
        ppr.insert(idx, np_)

    @staticmethod
    def _strip_prefix(p, prefix: str):
        for t in p.iter(W("t")):
            if t.text and t.text.startswith(prefix):
                t.text = t.text[len(prefix):]
                return
            if t.text and t.text.strip() == "":
                continue
            break

    # ----- equations -----
    def equation_pass(self):
        for p in list(self.body.iter(W("p"))):
            if pstyle_of(p) != "Equation":
                continue
            para = Paragraph(p, None)
            ts = para.paragraph_format.tab_stops
            from docx.enum.text import WD_TAB_ALIGNMENT
            ts.add_tab_stop(Twips(self.col_w // 2), WD_TAB_ALIGNMENT.CENTER)
            ts.add_tab_stop(Twips(self.col_w), WD_TAB_ALIGNMENT.RIGHT)
            para.paragraph_format.first_line_indent = Twips(0)
            for r in list(p.iter(W("r"))):
                t = r.find(W("t"))
                if t is None or not t.text or (S + "EQTAB" + S) not in t.text:
                    continue
                pieces = t.text.split(S + "EQTAB" + S)
                rpr = r.find(W("rPr"))
                anchor = r
                for k, piece in enumerate(pieces):
                    if k > 0:
                        tr = el("r")
                        if rpr is not None:
                            tr.append(copy.deepcopy(rpr))
                        tr.append(el("tab"))
                        anchor.addnext(tr)
                        anchor = tr
                    if piece:
                        nr = el("r")
                        if rpr is not None:
                            nr.append(copy.deepcopy(rpr))
                        nt = el("t")
                        nt.text = piece
                        nt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                        nr.append(nt)
                        anchor.addnext(nr)
                        anchor = nr
                r.getparent().remove(r)

    # ----- front matter and sections -----
    def front_pass(self):
        framecancel = dict(w=0, hSpace=0, vSpace=0, wrap="auto", vAnchor="margin", hAnchor="text", xAlign="left", yAlign="inline")
        for p in self.body.iter(W("p")):
            sid = pstyle_of(p)
            if sid in ("Title", "Authors"):
                ppr = p.find(W("pPr"))
                fp = ppr.find(W("framePr"))
                if fp is not None:
                    ppr.remove(fp)
                fp = el("framePr", **framecancel)
                ps = ppr.find(W("pStyle"))
                ppr.insert(list(ppr).index(ps) + 1 if ps is not None else 0, fp)
            if sid == "Authors":
                pass
        final = self.body.find(W("sectPr"))
        if self.unit == "supplement":
            return  # one column, one section: the template section 0 as pandoc copied it
        first = copy.deepcopy(final)
        second = copy.deepcopy(final)
        for hr in second.findall(W("headerReference")):
            second.remove(hr)
        pn = second.find(W("pgNumType"))
        if pn is not None:
            second.remove(pn)
        cols = second.find(W("cols"))
        newcols = el("cols", num=2, space=720, equalWidth=0)
        newcols.append(el("col", w=COL_W, space=288))
        newcols.append(el("col", w=COL_W, space=0))
        second.replace(cols, newcols)
        self.body.replace(final, second)
        sb = None
        for p in self.body.iter(W("p")):
            if ptext(p).strip() == S + "SECTIONBREAK" + S:
                sb = p
                break
        if sb is None:
            raise RuntimeError("section break sentinel missing")
        for ch in list(sb):
            sb.remove(ch)
        ppr = el("pPr")
        ppr.append(first)
        sb.append(ppr)

    # ----- tables -----
    def table_pass(self):
        sentinel = re.compile(re.escape(S) + r"TBL:(\d+)" + re.escape(S))
        paras = [p for p in self.body.iter(W("p")) if sentinel.fullmatch(ptext(p).strip() or "")]
        for p in paras:
            tid = int(sentinel.fullmatch(ptext(p).strip()).group(1))
            tbl = p.getnext()
            while tbl is not None and tbl.tag != W("tbl"):
                tbl = tbl.getnext()
            parent = p.getparent()
            parent.remove(p)
            if tbl is None:
                self.log.append(f"table {tid}: no table found after sentinel")
                continue
            self.format_table(tbl, self.specs.get(tid))

    def table_style_for(self, size_half_pt: int) -> str:
        name = f"Table Text {size_half_pt / 2:g}"
        st = self.style(name, base="Table Text")
        st.font.size = Pt(size_half_pt / 2)
        st.paragraph_format.space_before = Pt(0)
        st.paragraph_format.space_after = Pt(0)
        st.paragraph_format.line_spacing = 1.0
        return st.style_id

    def format_table(self, tbl, spec):
        if spec is None:
            self.log.append("table without spec left unformatted")
            return
        wide = spec["wide"]
        total = PAGE_TEXT_W if wide else self.col_w
        ncols = spec["ncols"]
        weights = spec["weights"]
        pad = 110  # twips: cell margins plus air
        fs_pt = (total - ncols * pad) / (max(sum(weights), 1) * 10.0)   # 0.5 em per character
        size = int(max(12, min(16, fs_pt * 2)))                          # half-points, 6 to 8 pt
        charw = size * 5.0                                               # twips per character
        raw = [w * charw + pad for w in weights]
        if sum(raw) < total:
            extra = total - sum(raw)
            raw = [r + extra * w / sum(weights) for r, w in zip(raw, weights)]
        else:
            raw = [r * total / sum(raw) for r in raw]
        widths = [max(250, int(r)) for r in raw]
        widths[-1] += total - sum(widths)
        data_style = self.table_style_for(size)
        # tblPr rebuilt
        old = tbl.find(W("tblPr"))
        tp = el("tblPr")
        if wide:
            tp.append(el("tblpPr", leftFromText=0, rightFromText=0, topFromText=60, bottomFromText=100,
                         vertAnchor="margin", horzAnchor="margin", tblpXSpec="center", tblpYSpec="top"))
            tp.append(el("tblOverlap", val="never"))
        tp.append(el("tblW", w=total, type="dxa"))
        if not wide:
            tp.append(el("jc", val="center"))
        tp.append(el("tblLayout", type="fixed"))
        mar = el("tblCellMar")
        for side, v in (("top", 15), ("left", 40), ("bottom", 15), ("right", 40)):
            mar.append(el(side, w=v, type="dxa"))
        tp.append(mar)
        tp.append(el("tblLook", val="0000", firstRow=0, lastRow=0, firstColumn=0, lastColumn=0, noHBand=1, noVBand=1))
        tbl.replace(old, tp)
        grid = tbl.find(W("tblGrid"))
        for g in list(grid):
            grid.remove(g)
        for w_ in widths:
            grid.append(el("gridCol", w=w_))
        rows = tbl.findall(W("tr"))
        if len(rows) != len(spec["rows"]):
            self.log.append(f"table row count {len(rows)} != spec {len(spec['rows'])}")
        for ri, tr in enumerate(rows):
            rs = spec["rows"][ri] if ri < len(spec["rows"]) else {"role": "data"}
            role = rs["role"]
            trpr = tr.find(W("trPr"))
            if trpr is None:
                trpr = el("trPr")
                tr.insert(0, trpr)
            trpr.append(el("cantSplit"))
            col = 0
            for tc in tr.findall(W("tc")):
                tcpr = tc.find(W("tcPr"))
                if tcpr is None:
                    tcpr = el("tcPr")
                    tc.insert(0, tcpr)
                gs = tcpr.find(W("gridSpan"))
                span = int(gs.get(W("val"))) if gs is not None else 1
                for ch in list(tcpr):
                    tcpr.remove(ch)
                tcpr.append(el("tcW", w=sum(widths[col:col + span]), type="dxa"))
                if span > 1:
                    tcpr.append(el("gridSpan", val=span))
                borders = el("tcBorders")
                added = False
                for rtype, rng in (rs.get("rules_before") or []):
                    if rtype == "cmid" and rng and not (rng[0] - 1 <= col <= rng[1] - 1):
                        continue
                    sz = 8 if rtype in ("top", "bottom") else 4
                    borders.append(el("top", val="single", sz=sz, space=0, color="000000"))
                    added = True
                    break
                if rs.get("rules_after"):
                    borders.append(el("bottom", val="single", sz=8, space=0, color="000000"))
                    added = True
                if added:
                    tcpr.append(borders)
                tcpr.append(el("vAlign", val="center" if role != "data" else "center"))
                for p in tc.findall(W("p")):
                    self._cell_para(p, role, data_style, ri)
                col += span

    def _cell_para(self, p, role, data_style, ri):
        ppr = p.find(W("pPr"))
        jc = ppr.find(W("jc")) if ppr is not None else None
        keep = jc.get(W("val")) if jc is not None else None
        if role == "data":
            set_pstyle(p, data_style)
        elif role == "title":
            set_pstyle(p, self.sid("Table Title"))
            keep = "center"
        elif role == "note":
            set_pstyle(p, self.sid("Table Note"))
            keep = "both"
        elif role == "image":
            set_pstyle(p, self.sid("Figure Image"))
            keep = "center"
        elif role == "figcap":
            set_pstyle(p, self.sid("Figure Caption"))
            keep = "both"
        ppr = p.find(W("pPr"))
        for x in ppr.findall(W("jc")):
            ppr.remove(x)
        from docx.enum.text import WD_ALIGN_PARAGRAPH as A
        mp = {"left": A.LEFT, "center": A.CENTER, "right": A.RIGHT, "both": A.JUSTIFY}
        Paragraph(p, None).paragraph_format.alignment = mp.get(keep or "left", A.LEFT)

    # ----- misc -----
    def scrub(self):
        for tag in (qn("wp:docPr"), qn("pic:cNvPr")):
            for e in self.body.iter(tag):
                e.set("descr", "")
                e.set("title", "")
        # drop template relationships that nothing references any more (sample images, IEEE links)
        used = set()
        for e in self.body.iter():
            for k, v in e.attrib.items():
                if k.startswith("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"):
                    used.add(v)
        for rid, rel in list(self.doc.part.rels.items()):
            if rel.reltype.rsplit("/", 1)[-1] in ("image", "hyperlink", "oleObject") and rid not in used:
                del self.doc.part.rels[rid]
        cp = self.doc.core_properties
        cp.author = "Anonymous" if self.anon else ""
        cp.last_modified_by = "Anonymous" if self.anon else ""
        cp.title = self.title
        cp.comments = ""
        cp.keywords = ""

    def header(self, text: str):
        sec = self.doc.sections[0]
        hdr = sec.header
        ps = hdr.paragraphs
        for p in ps:
            if "MANUSCRIPT ID" in p.text:
                for r in p.runs[1:]:
                    r._r.getparent().remove(r._r)
                if p.runs:
                    p.runs[0].text = text
                else:
                    p.add_run(text)
        # the template header carries the page number (right) above the line; keep it.

    def typeset_pass(self):
        """Match the PDF's typesetting where Word differs: IEEEtran sets references in 8 pt on 9 pt lines, breaks URLs at
        / . - _ ? = & #, and hyphenates. Display text gains invisible U+200B break points; link targets are unchanged."""
        from docx.enum.text import WD_LINE_SPACING
        rf = self.doc.styles["References"].paragraph_format
        rf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        rf.line_spacing = Pt(9)
        rf.space_before = Pt(0)
        rf.space_after = Pt(0)
        zw = "​"
        brk = re.compile(r"([/.\-_?=&#])(?=\S)")
        url = re.compile(r"(https?://\S+|doi\.org/\S+|\S+/\S+)")
        ref_sid = self.sid("References")
        n = 0
        for p in self.body.iter(W("p")):
            if pstyle_of(p) != ref_sid:
                continue
            # DOIs come as \nolinkurl (Verbatim Char, Courier); in Word the URLs print in the text font, so do the DOIs
            for rs in p.iter(W("rStyle")):
                if rs.get(W("val")) in ("VerbatimChar", self.sid("Verbatim Char")):
                    rs.getparent().remove(rs)
            for t in p.iter(W("t")):
                s = t.text or ""
                new = url.sub(lambda m: brk.sub(lambda k: k.group(1) + zw, m.group(0)), s)
                if new != s:
                    t.text = new
                    n += 1
        st = self.doc.settings.element
        if st.find(W("autoHyphenation")) is None:
            ah = el("autoHyphenation", val="true")
            dts = st.find(W("defaultTabStop"))
            if dts is not None:
                dts.addnext(ah)
            else:
                st.insert(0, ah)
        # never hyphenate the title, the author line or headings (LaTeX does not either)
        for name in ("Title", "Authors", "Heading 1", "Heading 2", "Heading 3", "Reference Head"):
            try:
                ppr = self.doc.styles[name].element.get_or_add_pPr()
            except KeyError:
                continue
            if ppr.find(W("suppressAutoHyphens")) is None:
                later = ("kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi",
                         "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
                         "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl",
                         "divId", "cnfStyle", "rPr", "sectPr", "pPrChange")
                nxt = next((c for c in ppr if c.tag in {W(t) for t in later}), None)
                sah = el("suppressAutoHyphens")
                if nxt is not None:
                    nxt.addprevious(sah)
                else:
                    ppr.append(sah)
        self.log.append(f"typeset: references 8/9 pt, {n} URL runs given break points, hyphenation on (not in title or headings)")

    def run(self, out: Path, header_text: str):
        self.ensure_styles()
        self.front_pass()
        self.paragraph_pass()
        self.equation_pass()
        self.table_pass()
        self.typeset_pass()
        self.scrub()
        self.header(header_text)
        self.doc.save(str(out))
        return self.log
