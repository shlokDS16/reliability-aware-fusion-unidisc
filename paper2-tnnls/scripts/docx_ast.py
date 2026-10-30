"""Pandoc-AST side of the DOCX converter: run pandoc on the preprocessed LaTeX, restructure the AST (sentinels -> equations,
floats, headings, bibliography, front matter) and write the DOCX with pandoc using the IEEE Word template as reference doc.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

S = "§§"
ZWSP = "​"


# --------------------------------------------------------------------------------------------------------------------
# AST constructors
# --------------------------------------------------------------------------------------------------------------------
def Str(t): return {"t": "Str", "c": t}
def Space(): return {"t": "Space"}
def LineBreak(): return {"t": "LineBreak"}
def Para(i): return {"t": "Para", "c": i}
def Plain(i): return {"t": "Plain", "c": i}
def Emph(i): return {"t": "Emph", "c": i}
def Strong(i): return {"t": "Strong", "c": i}
def Attr(id_="", cls=None, kv=None): return [id_, cls or [], kv or []]
def Div(attr, blocks): return {"t": "Div", "c": [attr, blocks]}
def Span(attr, inls): return {"t": "Span", "c": [attr, inls]}
def Link(inls, url): return {"t": "Link", "c": [Attr(), inls, [url, ""]]}
def Math(kind, tex): return {"t": "Math", "c": [{"t": kind}, tex]}
def Image(width_in, path): return {"t": "Image", "c": [Attr("", [], [["width", f"{width_in}in"]]), [], [path, ""]]}
def cstyle(name, blocks): return Div(Attr("", [], [["custom-style", name]]), blocks)
def sstyle(name, inls): return Span(Attr("", [], [["custom-style", name]]), inls)


def words(txt: str) -> list:
    out = []
    for i, w in enumerate(txt.split(" ")):
        if i:
            out.append(Space())
        if w:
            out.append(Str(w))
    return out


# --------------------------------------------------------------------------------------------------------------------
# generic walkers
# --------------------------------------------------------------------------------------------------------------------
INL_LIST = {"Emph", "Strong", "Underline", "Strikeout", "Superscript", "Subscript", "SmallCaps"}


def map_inlines(inls: list, fn) -> list:
    out = []
    for x in inls:
        t = x["t"]
        if t in INL_LIST:
            x = {"t": t, "c": map_inlines(x["c"], fn)}
        elif t == "Quoted":
            x = {"t": t, "c": [x["c"][0], map_inlines(x["c"][1], fn)]}
        elif t == "Span":
            x = {"t": t, "c": [x["c"][0], map_inlines(x["c"][1], fn)]}
        elif t == "Link":
            x = {"t": t, "c": [x["c"][0], map_inlines(x["c"][1], fn), x["c"][2]]}
        elif t == "Note":
            x = {"t": t, "c": map_blocks(x["c"], None, fn)}
        res = fn(x)
        if res is None:
            out.append(x)
        else:
            out.extend(res)
    return out


def map_blocks(blocks: list, bfn, ifn) -> list:
    out = []
    for b in blocks:
        t = b["t"]
        if t in ("Para", "Plain"):
            b = {"t": t, "c": map_inlines(b["c"], ifn) if ifn else b["c"]}
        elif t == "Header":
            c = b["c"]
            b = {"t": t, "c": [c[0], c[1], map_inlines(c[2], ifn) if ifn else c[2]]}
        elif t == "Div":
            b = {"t": t, "c": [b["c"][0], map_blocks(b["c"][1], bfn, ifn)]}
        elif t == "BlockQuote":
            b = {"t": t, "c": map_blocks(b["c"], bfn, ifn)}
        elif t == "BulletList":
            b = {"t": t, "c": [map_blocks(x, bfn, ifn) for x in b["c"]]}
        elif t == "OrderedList":
            b = {"t": t, "c": [b["c"][0], [map_blocks(x, bfn, ifn) for x in b["c"][1]]]}
        elif t == "DefinitionList":
            b = {"t": t, "c": [[map_inlines(term, ifn) if ifn else term, [map_blocks(d, bfn, ifn) for d in defs]]
                               for term, defs in b["c"]]}
        res = bfn(b) if bfn else None
        if res is None:
            out.append(b)
        else:
            out.extend(res)
    return out


def itext(inls: list) -> str:
    out = []
    for x in inls:
        t = x["t"]
        if t == "Str":
            out.append(x["c"])
        elif t == "Space" or t == "SoftBreak":
            out.append(" ")
        elif t == "LineBreak":
            out.append("\n")
        elif t in INL_LIST:
            out.append(itext(x["c"]))
        elif t in ("Span", "Link"):
            out.append(itext(x["c"][1]))
        elif t == "Quoted":
            out.append(itext(x["c"][1]))
        elif t == "Code":
            out.append(x["c"][1])
        elif t == "Math":
            out.append(x["c"][1])
    return "".join(out)


def btext(blocks: list) -> str:
    out = []
    for b in blocks:
        if b["t"] in ("Para", "Plain"):
            out.append(itext(b["c"]))
        elif b["t"] == "Div":
            out.append(btext(b["c"][1]))
    return " ".join(out)


# --------------------------------------------------------------------------------------------------------------------
# pandoc
# --------------------------------------------------------------------------------------------------------------------
def run_pandoc_json(latex: str, workdir: Path) -> tuple[dict, str]:
    src = Path(workdir) / "pandoc_input.tex"
    src.write_text(latex, encoding="utf-8")
    r = subprocess.run(["pandoc", "-f", "latex", "-t", "json", "--wrap=none", str(src)], capture_output=True,
                       encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError("pandoc (latex->json) failed:\n" + r.stderr)
    return json.loads(r.stdout), r.stderr


def run_pandoc_docx(doc: dict, reference: Path, out: Path, workdir: Path):
    j = Path(workdir) / "pandoc_ast.json"
    j.write_text(json.dumps(doc), encoding="utf-8")
    r = subprocess.run(["pandoc", "-f", "json", "-t", "docx", f"--reference-doc={reference}", "-o", str(out), str(j)],
                       capture_output=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError("pandoc (json->docx) failed:\n" + r.stderr)
    return r.stderr


# --------------------------------------------------------------------------------------------------------------------
# the restructuring
# --------------------------------------------------------------------------------------------------------------------
SENT = re.compile(re.escape(S) + r"([A-Z]+)(?::([^" + re.escape(S) + r"]*))?" + re.escape(S))
ALIGN = {"l": "AlignLeft", "c": "AlignCenter", "r": "AlignRight", None: "AlignDefault"}


def zw_url(t: str) -> str:
    return re.sub(r"([/?&=_\-\.%#])", r"\1" + ZWSP, t)


def zw_code(t: str) -> str:
    return re.sub(r"([/_\-])", r"\1" + ZWSP, t)


class Restructurer:
    def __init__(self, prep: dict, doc: dict):
        self.prep = prep
        self.doc = doc
        self.floats = {f["id"]: f for f in prep["floats"]}
        self.urls = prep["urls"]
        self.warnings: list[str] = []
        self.tbl_specs: dict[int, dict] = {}
        self.frags: dict[str, list] = {}
        self._split()

    # ----- fragments -----
    def _split(self):
        blocks = self.doc["blocks"]
        idx = None
        for i, b in enumerate(blocks):
            if b["t"] == "Para" and itext(b["c"]).strip() == S + "FRAGMENTS" + S:
                idx = i
                break
        if idx is None:
            raise RuntimeError("FRAGMENTS sentinel lost in pandoc output")
        self.main = blocks[:idx]
        cur = None
        for b in blocks[idx + 1:]:
            if b["t"] in ("Para", "Plain"):
                m = re.fullmatch(re.escape(S) + r"FRAG:(\w+)" + re.escape(S), itext(b["c"]).strip())
                if m:
                    cur = m.group(1)
                    self.frags[cur] = []
                    continue
            if cur is not None:
                self.frags[cur].append(b)

    def frag_blocks(self, fid):
        return self.frags.get(fid, [])

    def frag_inlines(self, fid) -> list:
        out = []
        for b in self.frag_blocks(fid):
            if b["t"] in ("Para", "Plain"):
                if out:
                    out.append(LineBreak())
                out.extend(b["c"])
            elif b["t"] == "Div":
                out.extend(self._flat(b["c"][1]))
            elif b["t"] == "DefinitionList" or b["t"] == "BulletList" or b["t"] == "OrderedList":
                self.warnings.append(f"list inside fragment {fid} flattened")
        return out

    def _flat(self, blocks):
        out = []
        for b in blocks:
            if b["t"] in ("Para", "Plain"):
                out.extend(b["c"])
        return out

    # ----- inline clean-up -----
    def fix_inline(self, x):
        t = x["t"]
        if t == "Link":
            url = x["c"][2][0]
            if url.startswith("#") and url[1:] in self.urls:
                real = self.urls[url[1:]]
                txt = itext(x["c"][1])
                inner = [Str(zw_url(real))] if txt.strip() == S + "URL" + S else x["c"][1]
                return [{"t": "Link", "c": [x["c"][0], inner, [real, ""]]}]
            return None
        if t == "Code":
            return [{"t": "Code", "c": [x["c"][0], zw_code(x["c"][1])]}]
        if t == "Span":
            attr = x["c"][0]
            if "mark" in attr[1]:
                return [sstyle("Todo", x["c"][1])]
            kv = dict(attr[2])
            if "label" in kv and not x["c"][1] and not attr[0].startswith("L_"):
                return []  # stray \label
            return None
        if t == "RawInline":
            self.warnings.append(f"unhandled raw inline dropped: {x['c'][1][:60]!r}")
            return []
        if t == "Str" and S in x["c"] and not x["c"].startswith(S):
            return None
        return None

    # ----- floats -----
    def float_blocks(self, fid: int) -> list:
        fl = self.floats[fid]
        if fl["kind"] == "figure":
            return self._figure(fl)
        return self._table(fl)

    def _label_span(self, fl, inls):
        if fl.get("label"):
            from docx_tex import bm
            return [Span(Attr(bm(fl["label"])), [])] + inls
        return inls

    def _figure(self, fl):
        cap = self.frag_inlines(fl["caption"])
        capi = self._label_span(fl, [Str("Fig."), Str(" " + fl["number"] + "."), Space()] + cap)
        imgs = []
        for im in fl["images"]:
            imgs.append(Image(im["width_in"], im["path"]))
        if not fl["wide"]:
            blocks = [cstyle("Figure Image", [Plain(imgs)]), cstyle("Figure Caption", [Plain(capi)])]
            return blocks
        tid = fl["id"]
        rows = [[self._tc([cstyle("Figure Image", [Plain(imgs)])], "AlignCenter", 1)],
                [self._tc([cstyle("Figure Caption", [Plain(capi)])], "AlignLeft", 1)]]
        self.tbl_specs[tid] = {"kind": "figure", "wide": True, "ncols": 1,
                               "rows": [{"role": "image"}, {"role": "figcap"}], "weights": [1.0], "font": None}
        return [self._table_node(tid, [self._trow(r) for r in rows], ["AlignCenter"])]

    def _tc(self, blocks, align, span):
        return [Attr(), {"t": align}, 1, span, blocks]

    def _trow(self, cells):
        return [Attr(), cells]

    def _table_node(self, tid, rows, aligns):
        colspecs = [[{"t": a}, {"t": "ColWidthDefault"}] for a in aligns]
        cap = [None, [Plain([Str(S + "TBL:" + str(tid) + S)])]]
        return {"t": "Table", "c": [Attr(), cap, colspecs, [Attr(), []], [[Attr(), 0, [], rows]], [Attr(), []]]}

    def _table(self, fl):
        tab = fl["tabular"]
        cap = self.frag_inlines(fl["caption"])
        lab1 = self._label_span(fl, [Str("TABLE"), Str(" " + fl["number"])])
        title_blocks = [cstyle("Table Title", [Plain(lab1)]), cstyle("Table Title", [Plain(cap)])]
        note_blocks = []
        if fl.get("note"):
            note_blocks = [cstyle("Table Note", [Plain(self.frag_inlines(fl["note"]))])]
        if not tab:
            return title_blocks + note_blocks
        ncols = max(len(tab["cols"]), max((sum(c["span"] for c in r["cells"]) for r in tab["rows"]), default=1))
        aligns = [ALIGN[c["align"]] for c in tab["cols"]] + ["AlignLeft"] * (ncols - len(tab["cols"]))
        weights = [0.0] * ncols
        rows, rspec = [], []
        for r in tab["rows"]:
            cells, ci = [], 0
            for c in r["cells"]:
                inl = self.frag_inlines(c["frag"])
                al = ALIGN[c["align"]] if c["align"] else aligns[ci] if ci < ncols else "AlignLeft"
                cells.append(self._tc([cstyle("Table Text", [Plain(inl)])], al, c["span"]))
                txt = itext(inl)
                ln = max((len(x) for x in txt.split("\n")), default=0)
                if c["span"] == 1 and ci < ncols:
                    weights[ci] = max(weights[ci], min(ln, 45))
                ci += c["span"]
            while ci < ncols:
                cells.append(self._tc([cstyle("Table Text", [Plain([])])], "AlignLeft", 1))
                ci += 1
            rows.append(self._trow(cells))
            rspec.append({"role": "data", "rules_before": r["rules_before"]})
        for i, c in enumerate(tab["cols"]):
            if c["w"]:
                weights[i] = max(weights[i], c["w"] * 90)
        weights = [max(w, 1.0) for w in weights]
        if rspec:
            rspec[-1]["rules_after"] = tab["rules_after"]
        tid = fl["id"]
        if not fl["wide"]:
            self.tbl_specs[tid] = {"kind": "table", "wide": False, "ncols": ncols, "rows": rspec, "weights": weights}
            return title_blocks + [self._table_node(tid, rows, aligns)] + note_blocks
        head = [self._trow([self._tc([title_blocks[0]], "AlignCenter", ncols)]),
                self._trow([self._tc([title_blocks[1]], "AlignCenter", ncols)])]
        tail = []
        spec_rows = [{"role": "title"}, {"role": "title"}] + rspec
        if note_blocks:
            tail = [self._trow([self._tc(note_blocks, "AlignLeft", ncols)])]
            spec_rows.append({"role": "note"})
        self.tbl_specs[tid] = {"kind": "table", "wide": True, "ncols": ncols, "rows": spec_rows, "weights": weights}
        return [self._table_node(tid, head + rows + tail, aligns)]

    # ----- equations -----
    def equation_block(self, num: str, bmk: str, math_tex: str) -> dict:
        inls = []
        if bmk:
            inls.append(Span(Attr(bmk), []))
        inls += [Str(S + "EQTAB" + S), Math("InlineMath", math_tex)]
        if num:
            inls += [Str(S + "EQTAB" + S), Str("(" + num + ")")]
        return cstyle("Equation", [Para(inls)])

    # ----- bibliography -----
    def bib_blocks(self) -> list:
        out = [cstyle("Reference Head", [Para([Str("References")])])]
        for key, num, fid in self.prep["bib"]:
            inls = [Span(Attr(f"ref_{num}"), [])] + self.frag_inlines(fid)
            out.append(cstyle("References", [Para(inls)]))
        return out

    # ----- main transform -----
    def block_fn(self, b):
        t = b["t"]
        if t in ("Para", "Plain"):
            inls = b["c"]
            txt = itext(inls[:1]) if inls else ""
            m = SENT.fullmatch(txt) if inls and inls[0]["t"] == "Str" else None
            if m:
                kind, arg = m.group(1), m.group(2)
                if kind == "FLOAT":
                    return self.float_blocks(int(arg))
                if kind == "BIB":
                    return self.bib_blocks()
                if kind == "EQ":
                    num, _, bmk = arg.partition(":")
                    mathn = [x for x in inls[1:] if x["t"] == "Math"]
                    if not mathn:
                        self.warnings.append(f"equation {num} lost its math")
                        return []
                    return [self.equation_block(num, bmk, mathn[0]["c"][1])]
                if kind == "CONT":
                    rest = inls[1:]
                    while rest and rest[0]["t"] in ("Space", "SoftBreak"):
                        rest = rest[1:]
                    if not rest:
                        return []
                    return [{"t": t, "c": [Str(S + "CONT" + S)] + rest}]
            # display math that came out of the source directly
            return None
        if t == "Div":
            cls = b["c"][0][1]
            if cls and cls[0] in ("thmplain", "thmdef"):
                return self.theorem_block(b, cls[0] == "thmplain")
            return None
        if t == "DefinitionList":
            out = []
            for term, defs in b["c"]:
                for d in defs:
                    first = True
                    for blk in d:
                        if blk["t"] in ("Para", "Plain"):
                            inls = ([Strong(term), Space()] if first else []) + blk["c"]
                            out.append(Para(inls))
                            first = False
            return out
        if t == "OrderedList":
            start, (sty, dl) = b["c"][0][0], (b["c"][0][1], b["c"][0][2])
            return [{"t": "OrderedList", "c": [[start, {"t": "Decimal"}, {"t": "OneParen"}], b["c"][1]]}]
        if t == "Header":
            lvl, attr, inls = b["c"]
            return None
        if t == "RawBlock":
            self.warnings.append(f"unhandled raw block dropped: {b['c'][1][:60]!r}")
            return []
        return None

    def theorem_block(self, b, plain: bool):
        blocks = b["c"][1]
        out = []
        seen = False
        for blk in blocks:
            if blk["t"] in ("Para", "Plain"):
                inls = blk["c"]
                if not seen:
                    k = next((i for i, x in enumerate(inls) if x["t"] == "Str" and S + "B" + S in x["c"]), None)
                    if k is not None:
                        seen = True
                        pre, post = inls[k]["c"].split(S + "B" + S, 1)
                        head = inls[:k] + ([Str(pre)] if pre else [])
                        tail = ([Str(post)] if post else []) + inls[k + 1:]
                        while tail and tail[0]["t"] in ("Space", "SoftBreak"):
                            tail = tail[1:]
                        if plain and tail:
                            tail = [Emph(tail)]
                        out.append({"t": blk["t"], "c": head + [Space()] + tail})
                        continue
                out.append({"t": blk["t"], "c": [Emph(inls)] if plain and inls else inls})
            else:
                out.append(blk)
        return out

    def run(self) -> dict:
        main = map_blocks(self.main, self.block_fn, None)
        main = self.front_matter() + main
        main = [b for b in main if not (b["t"] in ("Para", "Plain") and not b["c"])]
        main = map_blocks(main, None, self.fix_inline)
        return {"pandoc-api-version": self.doc["pandoc-api-version"], "meta": {}, "blocks": main}

    def front_matter(self) -> list:
        title = self.frag_inlines("title")
        out = [cstyle("Title", [Para(title)])]
        auth = self.frag_inlines("author")
        out.append(cstyle("Authors", [Para(auth)]))
        if self.prep.get("unit") != "supplement":
            out.append(Para([Str(S + "SECTIONBREAK" + S)]))
        abstract = self.frag_inlines("abstract")
        if abstract:
            out.append(cstyle("Abstract", [Para([Emph([Str("Abstract")]), Str("—")] + abstract)]))
        kw = self.frag_inlines("keywords")
        if kw:
            out.append(cstyle("IndexTerms", [Para([Emph([Str("Index Terms")]), Str("—")] + kw)]))
        for i in range(len(self.prep["meta"]["thanks"])):
            out.append(cstyle("footnote text", [Para(self.frag_inlines(f"thanks{i}"))]))
        return out
