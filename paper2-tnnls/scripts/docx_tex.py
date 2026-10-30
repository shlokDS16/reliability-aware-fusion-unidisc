"""LaTeX side of the DOCX converter for Paper 2 (IEEE TNNLS).

Reads main.tex (or supplement.tex), expands \\input, honours the \\ifanon switch, resolves everything pandoc cannot know
(\\cite, \\cref, \\ref, \\eqref, \\todo, \\nolinkurl, floats, theorem environments, equation numbers, heading numbers) using
main.aux / main.bbl, and returns ONE LaTeX string for pandoc plus side tables. All information that pandoc would lose is
carried as text sentinels (paragraphs that start with the section sign pair) which docx_ast.py turns into structure.

No file of the paper is modified; everything is read-only.
"""
from __future__ import annotations

import re
from pathlib import Path

S = "\u00a7\u00a7"  # sentinel bracket: two section signs


class TexError(Exception):
    pass


# --------------------------------------------------------------------------------------------------------------------
# small text helpers
# --------------------------------------------------------------------------------------------------------------------
def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def strip_comments(s: str) -> str:
    """TeX semantics: % drops the rest of the line, the line break and the leading blanks of the next line."""
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n:
            out.append(s[i:i + 2])
            i += 2
            continue
        if c == "%":
            j = s.find("\n", i)
            if j < 0:
                break
            i = j + 1
            while i < n and s[i] in " \t":
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def grab(s: str, i: int, open_: str = "{", close: str = "}") -> tuple[str, int]:
    """s[i] must be `open_`; return (content, index just after the matching close)."""
    if i >= len(s) or s[i] != open_:
        raise TexError(f"expected {open_!r} at {i}: {s[i:i + 40]!r}")
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == open_:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise TexError(f"unbalanced {open_}{close} starting {s[i:i + 60]!r}")


def skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i] in " \t\r\n":
        i += 1
    return i


def cmd_re(name: str) -> re.Pattern:
    return re.compile(r"\\" + re.escape(name) + r"(?![a-zA-Z@])")


def replace_cmd(s: str, name: str, fn, nargs: int = 1, opt: bool = False, star: bool = False) -> str:
    """Replace every \\name[opt]{a1}...{an} by fn(args, optarg). Scans left to right and rescans the replacement."""
    pat = cmd_re(name)
    pos = 0
    while True:
        m = pat.search(s, pos)
        if not m:
            return s
        i = m.end()
        if star and i < len(s) and s[i] == "*":
            i += 1
        j = skip_ws(s, i) if (opt or nargs) else i
        optarg = None
        if opt and j < len(s) and s[j] == "[":
            optarg, j = grab(s, j, "[", "]")
        args = []
        k = j
        try:
            for _ in range(nargs):
                k = skip_ws(s, k)
                a, k = grab(s, k)
                args.append(a)
        except TexError:
            pos = m.end()
            continue
        rep = fn(args, optarg)
        s = s[:m.start()] + rep + s[k:]
        pos = m.start()


def roman(n: int) -> str:
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, r in vals:
        while n >= v:
            out += r
            n -= v
    return out


def alpha(n: int) -> str:
    return chr(64 + n)


def bm(label: str) -> str:
    """Word bookmark-safe identifier for a LaTeX label."""
    return "L_" + re.sub(r"[^A-Za-z0-9]", "_", label)


# --------------------------------------------------------------------------------------------------------------------
# aux / bbl
# --------------------------------------------------------------------------------------------------------------------
class Aux:
    def __init__(self, path: Path):
        self.cites: dict[str, str] = {}
        self.labels: dict[str, dict] = {}
        text = read(path) if Path(path).exists() else ""
        for key, num in re.findall(r"\\bibcite\{([^}]*)\}\{([^}]*)\}", text):
            self.cites[key] = num
        for m in re.finditer(r"\\newlabel\{", text):
            try:
                name, j = grab(text, m.end() - 1)
                val, _ = grab(text, j)
            except TexError:
                continue
            if name.endswith("@cref"):
                base = name[:-5]
                first, _ = grab(val, 0)
                mm = re.match(r"\[(\w+)\]\[([^\]]*)\]\[([^\]]*)\](.*)$", first, re.S)
                if not mm:
                    continue
                disp = re.sub(r"\\mbox\s*\{([^}]*)\}", r"\1", mm.group(4)).strip()
                self.labels.setdefault(base, {}).update(type=mm.group(1), display=disp)
            else:
                first, _ = grab(val, 0)
                disp = re.sub(r"\\mbox\s*\{([^}]*)\}", r"\1", first).strip()
                self.labels.setdefault(name, {}).update(plain=disp)

    def display(self, label: str) -> str | None:
        d = self.labels.get(label)
        if not d:
            return None
        return d.get("display", d.get("plain"))


def parse_bbl(path: Path) -> list[tuple[str, str]]:
    """Return [(key, raw_latex_body)] in bbl (= citation) order."""
    text = strip_comments(read(path))
    text = text.split("\\bibitem", 1)[1] if "\\bibitem" in text else ""
    text = "\\bibitem" + text
    text = text.split("\\end{thebibliography}")[0]
    items = []
    for part in re.split(r"\\bibitem(?![a-zA-Z])", text)[1:]:
        part = part.strip()
        if part.startswith("["):
            _, k = grab(part, 0, "[", "]")
            part = part[k:].lstrip()
        key, k = grab(part, 0)
        items.append((key, part[k:].strip()))
    return items


# --------------------------------------------------------------------------------------------------------------------
# tabular parsing
# --------------------------------------------------------------------------------------------------------------------
def split_top(s: str, sep: str) -> list[str]:
    """Split on a top-level separator ('&' or the row break) outside braces, math dollars and \\begin..\\end groups."""
    parts, cur = [], []
    depth = env = 0
    math = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            if s.startswith("\\begin{", i):
                env += 1
            elif s.startswith("\\end{", i):
                env -= 1
            if sep == "\\\\" and s.startswith("\\\\", i) and depth == 0 and env == 0 and not math:
                parts.append("".join(cur))
                cur = []
                i += 2
                if i < len(s) and s[i] == "*":
                    i += 1
                continue
            if sep == "&" and s.startswith("\\&", i):
                cur.append("\\&")
                i += 2
                continue
            cur.append(s[i:i + 2])
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "$":
            math = not math
        if sep == "&" and c == "&" and depth == 0 and env == 0 and not math:
            parts.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    parts.append("".join(cur))
    return parts


def parse_colspec(spec: str) -> list[dict]:
    cols = []
    i = 0
    while i < len(spec):
        c = spec[i]
        if c in "lcr":
            cols.append({"align": c, "w": None})
            i += 1
        elif c in "pmb":
            w, i2 = grab(spec, i + 1)
            mm = re.match(r"\s*([0-9.]+)\s*\\(linewidth|columnwidth|textwidth)", w)
            cols.append({"align": "l", "w": float(mm.group(1)) if mm else None})
            i = i2
        elif c in "@!>":
            _, i = grab(spec, i + 1)
        elif c == "*":
            n, i2 = grab(spec, i + 1)
            sub, i3 = grab(spec, i2)
            for _ in range(int(n)):
                cols.extend(parse_colspec(sub))
            i = i3
        else:
            i += 1
    return cols


RULE_RE = re.compile(r"\\(toprule|midrule|bottomrule|hline|cmidrule|addlinespace|specialrule|noalign)(?![a-zA-Z])")


def parse_tabular(spec: str, body: str) -> dict:
    cols = parse_colspec(spec)
    rows_raw = split_top(body, "\\\\")
    rows = []
    pending_rules: list[str] = []
    for raw in rows_raw:
        t = raw.strip()
        # optional vertical space after the row break: \\[2pt]
        if t.startswith("["):
            try:
                _, k = grab(t, 0, "[", "]")
                t = t[k:].strip()
            except TexError:
                pass
        while True:
            m = RULE_RE.match(t)
            if not m:
                break
            name = m.group(1)
            k = m.end()
            if name == "cmidrule":
                if k < len(t) and t[k] == "(":
                    _, k = grab(t, k, "(", ")")
                rng = None
                if k < len(t) and t[k] == "{":
                    g, k = grab(t, k)
                    mr = re.match(r"\s*(\d+)\s*-\s*(\d+)", g)
                    rng = (int(mr.group(1)), int(mr.group(2))) if mr else None
                pending_rules.append(("cmid", rng))
            elif name in ("addlinespace",):
                if k < len(t) and t[k] == "[":
                    _, k = grab(t, k, "[", "]")
            elif name in ("specialrule",):
                for _ in range(3):
                    k = skip_ws(t, k)
                    _, k = grab(t, k)
                pending_rules.append(("mid", None))
            elif name == "noalign":
                _, k = grab(t, skip_ws(t, k))
            else:
                pending_rules.append(({"toprule": "top", "bottomrule": "bottom", "midrule": "mid", "hline": "mid"}[name], None))
            t = t[k:].lstrip()
        if not t:
            continue
        cells = []
        for ctext in split_top(t, "&"):
            ctext = ctext.strip()
            span, align = 1, None
            mm = re.match(r"\\multicolumn\s*\{(\d+)\}\s*\{((?:[^{}]|\{[^{}]*\})*)\}\s*", ctext)   # column spec may hold one brace level, e.g. @{}l
            if mm:
                span = int(mm.group(1))
                am = re.search(r"[lcr]", mm.group(2))
                align = am.group(0) if am else None
                k = mm.end()
                content, k2 = grab(ctext, k)
                ctext = content.strip()
            cells.append({"span": span, "align": align, "text": ctext})
        rows.append({"cells": cells, "rules_before": pending_rules})
        pending_rules = []
    return {"cols": cols, "rows": rows, "rules_after": pending_rules}


# --------------------------------------------------------------------------------------------------------------------
# the preprocessor
# --------------------------------------------------------------------------------------------------------------------
ENV_NAMES = {
    "figure": ("Fig.", "Figs."), "table": ("Table", "Tables"), "section": ("Section", "Sections"),
    "subsection": ("Section", "Sections"), "subsubsection": ("Section", "Sections"),
    "appendix": ("Appendix", "Appendices"), "proposition": ("Proposition", "Propositions"),
    "lemma": ("Lemma", "Lemmas"), "theorem": ("Theorem", "Theorems"), "corollary": ("Corollary", "Corollaries"),
    "definition": ("Definition", "Definitions"), "assumption": ("Assumption", "Assumptions"),
    "remark": ("Remark", "Remarks"), "algocf": ("Algorithm", "Algorithms"),
}
PLAIN_THM = {"theorem", "proposition", "lemma", "corollary"}


class Preprocessor:
    def __init__(self, tex_path: Path, aux_path: Path, bbl_path: Path | None, anon: bool = True,
                 unit: str = "main"):
        self.tex_path = Path(tex_path)
        self.root = self.tex_path.parent
        self.aux = Aux(aux_path)
        self.bbl_path = bbl_path
        self.anon = anon
        self.unit = unit  # "main" (two-column, roman sections) or "supplement"
        self.warnings: list[str] = []
        self.fragments: dict[str, str] = {}
        self.floats: list[dict] = []
        self.anchors: set[str] = set()
        self.eq_numbers: dict[str, str] = {}
        self.thm_numbers: dict[str, str] = {}
        self.float_numbers: dict[str, str] = {}
        self.sec_numbers: dict[str, str] = {}
        self.url_table: dict[str, str] = {}
        self.macros: list[str] = []
        self.thm_names: dict[str, str] = {}
        self.meta: dict[str, str] = {}
        self._fid = 0
        self.col_in = 7.2 if unit == "supplement" else 3.5

    # ----- bookkeeping -----
    def warn(self, msg: str):
        self.warnings.append(msg)

    def frag(self, text: str, kind: str = "f") -> str:
        self._fid += 1
        fid = f"{kind}{self._fid}"
        self.fragments[fid] = text
        return fid

    # ----- flatten -----
    def flatten(self, s: str, depth: int = 0) -> str:
        def rep(m):
            name = m.group(1).strip()
            p = self.root / name
            if not p.suffix:
                p = p.with_suffix(".tex")
            if not p.exists():
                self.warn(f"\\input file not found: {name}")
                return ""
            if depth > 8:
                raise TexError("\\input nesting too deep")
            return "\n" + self.flatten(strip_comments(read(p)), depth + 1) + "\n"
        return re.sub(r"\\input\{([^}]*)\}", rep, s)

    # ----- conditionals -----
    def flags(self, src: str) -> dict[str, bool]:
        names = re.findall(r"\\newif\\if([a-zA-Z]+)", src)
        fl = {}
        for n in names:
            vals = re.findall(r"\\" + n + r"(true|false)(?![a-zA-Z])", src)
            fl[n] = (vals[-1] == "true") if vals else False
        if "anon" in fl:
            fl["anon"] = self.anon
        return fl

    def resolve_ifs(self, s: str, flags: dict[str, bool]) -> str:
        tok = re.compile(r"\\(if[a-zA-Z]*|else|fi)(?![a-zA-Z])")
        while True:
            start = None
            for m in tok.finditer(s):
                nm = m.group(1)
                if nm.startswith("if") and nm[2:] in flags:
                    start = m
                    break
            if not start:
                return s
            name = start.group(1)[2:]
            depth = 1
            else_at = None
            end = None
            for m in tok.finditer(s, start.end()):
                nm = m.group(1)
                if nm == "fi":
                    depth -= 1
                    if depth == 0:
                        end = m
                        break
                elif nm == "else":
                    if depth == 1:
                        else_at = m
                elif nm.startswith("if") and nm != "iff":
                    depth += 1
            if end is None:
                raise TexError(f"unterminated \\if{name}")
            then_part = s[start.end():else_at.start() if else_at else end.start()]
            else_part = s[else_at.end():end.start()] if else_at else ""
            s = s[:start.start()] + (then_part if flags[name] else else_part) + s[end.end():]

    # ----- macros defined in the preamble -----
    def collect_preamble(self, pre: str):
        for m in re.finditer(r"\\newcommand\s*\{(\\[a-zA-Z]+)\}", pre):
            name = m.group(1)
            if name in ("\\todo", "\\anonlink"):
                continue
            try:
                j = m.end()
                nargs = ""
                if pre[j] == "[":
                    n, j = grab(pre, j, "[", "]")
                    nargs = f"[{n}]"
                body, _ = grab(pre, j)
            except (TexError, IndexError):
                continue
            self.macros.append(f"\\newcommand{{{name}}}{nargs}{{{body}}}")
        for m in re.finditer(r"\\newtheorem\{(\w+)\}\{([^}]*)\}", pre):
            self.thm_names[m.group(1)] = m.group(2)

    # ----- the cleaning pass applied to the body and to every fragment -----
    def clean_text(self, s: str) -> str:
        def todo(a, o):
            return "\\hl{\\textbf{[" + a[0] + "]}}"
        s = replace_cmd(s, "todo", todo)

        def anonlink(a, o):
            if self.anon:
                return "\\textit{[link withheld for double-anonymous review]}"
            return "\\href{" + a[0] + "}{" + a[1] + "}"
        s = replace_cmd(s, "anonlink", anonlink, nargs=2)

        def verb(a, o):
            txt = re.sub(r"\s+", " ", a[0]).strip()
            for d in "|!+@#=^~":
                if d not in txt:
                    return "\\verb" + d + txt + d
            return txt
        s = replace_cmd(s, "nolinkurl", verb)
        s = replace_cmd(s, "seqsplit", lambda a, o: a[0])
        s = replace_cmd(s, "IEEEPARstart", lambda a, o: a[0] + a[1], nargs=2)
        s = replace_cmd(s, "vspace", lambda a, o: "", star=True)
        s = replace_cmd(s, "hspace", lambda a, o: " ", star=True)
        s = replace_cmd(s, "setlength", lambda a, o: "", nargs=2)
        s = replace_cmd(s, "textminus", lambda a, o: "\u2212", nargs=0)
        s = s.replace("\\textminus", "\u2212")
        s = replace_cmd(s, "url", self._url_repl)
        for junk in ("allowbreak", "noindent", "centering", "scriptsize", "footnotesize", "small", "normalsize", "tiny",
                     "bigskip", "medskip", "smallskip", "nobreak", "clearpage", "newpage", "raggedright", "sloppy"):
            s = re.sub(r"\\" + junk + r"(?![a-zA-Z])\s?", "", s)
        s = s.replace("\\-", "")
        s = re.sub(r"\\relax(?![a-zA-Z])\s?", "", s)
        s = re.sub(r"\\hskip\s*[-0-9.]*\s*(?:pt|em|ex|mm)?", " ", s)
        # pandoc swallows the word after a text-mode \; : use a plain four-per-em space (math mode is left alone)
        s = "".join(part if part.startswith("$") else re.sub(r"\\[;:](?![a-zA-Z])", " ", part)
                    for part in re.split(r"(\$\$.*?\$\$|\$[^$]*\$)", s, flags=re.S))
        s = re.sub(r"\\qed(?![a-zA-Z])", " □", s)
        s = re.sub(r"\\nobreakspace(?![a-zA-Z])\s?", "~", s)
        # {\rm text} -> \mathrm{text}  (texmath does not know \rm)
        s = self._fix_rm(s)
        s = self._cites_and_refs(s)
        s = re.sub(r"\\label\{(?!L_)[^}]*\}", "", s)
        return s

    def _url_repl(self, a, o):
        u = a[0].replace("\\%", "%").replace("\\#", "#").replace("\\_", "_").replace("\\&", "&").replace("\\~{}", "~")
        k = f"url{len(self.url_table) + 1}"
        self.url_table[k] = u
        return "\\hyperlink{" + k + "}{" + S + "URL" + S + "}"

    def _fix_rm(self, s: str) -> str:
        pat = re.compile(r"\{\s*\\(rm|bf|it|sf|tt)(?![a-zA-Z])\s*")
        mp = {"rm": "mathrm", "bf": "mathbf", "it": "mathit", "sf": "mathsf", "tt": "mathtt"}
        while True:
            m = pat.search(s)
            if not m:
                return s
            i = m.start()
            content, j = grab(s, i)
            inner = content[m.end() - i - 1:]
            s = s[:i] + "\\" + mp[m.group(1)] + "{" + inner + "}" + s[j:]

    # ----- references -----
    def _bm_link(self, label: str, text: str) -> str:
        if label in self.anchors:
            return "\\hyperlink{" + bm(label) + "}{" + text + "}"
        return text

    def _cites_and_refs(self, s: str) -> str:
        def cite(a, o):
            keys = [k.strip() for k in a[0].split(",") if k.strip()]
            nums = []
            for k in keys:
                n = self.aux.cites.get(k)
                if n is None:
                    self.warn(f"undefined citation key: {k}")
                    nums.append((10 ** 6, k))
                else:
                    nums.append((int(n), k))
            nums = sorted(set(nums))
            vals = [n for n, _ in nums]
            out, i = [], 0
            while i < len(nums):
                j = i
                while j + 1 < len(nums) and nums[j + 1][0] == nums[j][0] + 1 and nums[j][0] < 10 ** 6:
                    j += 1
                def one(idx):
                    n, k = nums[idx]
                    if n >= 10 ** 6:
                        return "[?" + k + "]"
                    return "\\hyperlink{ref_" + str(n) + "}{[" + str(n) + "]}"
                if j - i >= 2:
                    out.append(one(i) + "\u2013" + one(j))
                else:
                    out.extend(one(x) for x in range(i, j + 1))
                i = j + 1
            return ", ".join(out)
        s = replace_cmd(s, "cite", cite, opt=True)

        def refs(labels: list[str], cap: bool) -> str:
            items = []
            for lab in labels:
                lab = lab.strip()
                d = self.aux.labels.get(lab)
                if not d or "display" not in d:
                    self.warn(f"undefined reference label: {lab}")
                    items.append(("?", "??", lab))
                    continue
                items.append((d.get("type", "section"), d["display"], lab))
            groups = []
            for it in items:
                if groups and groups[-1][0] == it[0]:
                    groups[-1][1].append(it)
                else:
                    groups.append((it[0], [it]))
            pieces = []
            for typ, its in groups:
                if typ == "equation":
                    txts = [self._bm_link(l, "(" + d + ")") for _, d, l in its]
                    pieces.append(self._join(txts))
                    continue
                names = ENV_NAMES.get(typ, (typ.capitalize(), typ.capitalize() + "s"))
                if len(its) == 1:
                    _, d, l = its[0]
                    pieces.append(self._bm_link(l, names[0] + "~" + d))
                else:
                    pieces.append(names[1] + "~" + self._join([self._bm_link(l, d) for _, d, l in its]))
            return " and ".join(pieces) if len(pieces) <= 2 else ", ".join(pieces[:-1]) + ", and " + pieces[-1]
        s = replace_cmd(s, "cref", lambda a, o: refs(a[0].split(","), False))
        s = replace_cmd(s, "Cref", lambda a, o: refs(a[0].split(","), True))
        s = replace_cmd(s, "eqref", lambda a, o: refs(a[0].split(","), False))

        def plainref(a, o):
            lab = a[0].strip()
            d = self.aux.display(lab)
            if d is None:
                self.warn(f"undefined reference label: {lab}")
                return "??"
            return self._bm_link(lab, d)
        s = replace_cmd(s, "ref", plainref)
        return s

    @staticmethod
    def _join(txts: list[str]) -> str:
        if len(txts) == 1:
            return txts[0]
        if len(txts) == 2:
            return txts[0] + " and " + txts[1]
        return ", ".join(txts[:-1]) + ", and " + txts[-1]

    # ----- structural passes -----
    def pass_equations(self, s: str) -> str:
        counter = [0]
        pat = re.compile(r"\\begin\{(equation|align|gather|eqnarray)(\*?)\}(.*?)\\end\{\1\2\}", re.S)

        def disp(n: int) -> str:
            return f"S{n}" if self.unit == "supplement" else str(n)

        def sub(m):
            env, star, body = m.group(1), m.group(2), m.group(3)
            lines = [body] if env == "equation" else split_top(body, "\\\\")
            groups, cur_lines, cur_labels = [], [], []
            for ln in lines:
                labs = re.findall(r"\\label\{([^}]*)\}", ln)
                notag = bool(re.search(r"\\(notag|nonumber)(?![a-zA-Z])", ln))
                ln = re.sub(r"\\label\{[^}]*\}", "", ln)
                ln = re.sub(r"\\(notag|nonumber)(?![a-zA-Z])", "", ln).strip()
                if not ln:
                    continue
                cur_lines.append(ln)
                cur_labels += labs
                if not notag and not star:
                    groups.append((cur_lines, cur_labels, True))
                    cur_lines, cur_labels = [], []
            if cur_lines:
                groups.append((cur_lines, cur_labels, False))
            out = []
            for g_lines, g_labels, numbered in groups:
                if len(g_lines) == 1 and env == "equation":
                    math = g_lines[0]
                else:
                    math = "\\begin{aligned}" + " \\\\ ".join(g_lines) + "\\end{aligned}"
                num = ""
                lab = ""
                if numbered:
                    counter[0] += 1
                    num = disp(counter[0])
                    for l in g_labels:
                        self.eq_numbers[l] = num
                    if g_labels:
                        lab = g_labels[0]
                        self.anchors.add(lab)
                        for extra in g_labels[1:]:
                            self.anchors.add(extra)
                out.append("\n\n" + S + "EQ:" + num + ":" + (bm(lab) if lab else "") + S + "$$" + math + "$$\n\n")
            after = m.string[m.end():]
            cont = "" if re.match(r"[ \t]*\n[ \t]*\n", after) or not after.strip() else S + "CONT" + S
            return "".join(out) + cont
        return pat.sub(sub, s)

    def pass_theorems(self, s: str) -> str:
        counters: dict[str, int] = {}
        pat = re.compile(r"\\begin\{(theorem|proposition|lemma|corollary|definition|assumption|remark)\}(?:\[([^\]]*)\])?(.*?)\\end\{\1\}", re.S)

        def sub(m):
            env, title, body = m.group(1), m.group(2), m.group(3)
            counters[env] = counters.get(env, 0) + 1
            n = counters[env]
            numtxt = f"S{n}" if self.unit == "supplement" else str(n)
            name = self.thm_names.get(env, env.capitalize())
            labs = re.findall(r"\\label\{([^}]*)\}", body)
            body = re.sub(r"\\label\{[^}]*\}", "", body)
            hdr = "\\textbf{" + name + " " + numtxt + "}"
            if labs:
                self.anchors.add(labs[0])
                self.thm_numbers[labs[0]] = f"{name} {numtxt}"
                hdr = hdr + "\\label{" + bm(labs[0]) + "}"
            tail = (" (" + title + ").") if title else "."
            cls = "thmplain" if env in PLAIN_THM else "thmdef"
            return ("\n\n\\begin{" + cls + "}" + hdr + tail + S + "B" + S + " " + body.strip() +
                    "\n\\end{" + cls + "}\n\n")
        return pat.sub(sub, s)

    def pass_headings(self, s: str) -> str:
        sec = sub = subsub = app = 0
        in_appendix = False
        out = []
        pos = 0
        pat = re.compile(r"\\(appendices|appendix(?![a-zA-Z])|section|subsection|subsubsection|paragraph)(\*?)")
        while True:
            m = pat.search(s, pos)
            if not m:
                out.append(s[pos:])
                break
            out.append(s[pos:m.start()])
            kind, star = m.group(1), m.group(2)
            if kind in ("appendices", "appendix"):
                in_appendix = True
                pos = m.end()
                continue
            j = skip_ws(s, m.end())
            if j < len(s) and s[j] == "[":
                _, j = grab(s, j, "[", "]")
                j = skip_ws(s, j)
            title, k = grab(s, j)
            label = None
            lm = re.match(r"\s*\\label\{([^}]*)\}", s[k:])
            if lm:
                label = lm.group(1)
                k += lm.end()
            pos = k
            numtxt = None
            if kind == "section":
                if star:
                    htxt = title
                elif in_appendix:
                    app += 1
                    sub = subsub = 0
                    numtxt = alpha(app)
                    htxt = "Appendix~" + numtxt + "\\\\ " + title
                else:
                    sec += 1
                    sub = subsub = 0
                    numtxt = (("S-" + roman(sec)) if self.unit == "supplement" else roman(sec))
                    htxt = numtxt + ".~" + title
                hd = "\\hypertarget{" + bm(label) + "}{" + htxt + "}" if label else htxt
                if label:
                    self.anchors.add(label)
                out.append("\n\n\\section*{" + hd + "}\n\n")
            elif kind == "subsection":
                if star:
                    htxt = title
                else:
                    sub += 1
                    subsub = 0
                    base = alpha(app) if in_appendix else (("S-" + roman(sec)) if self.unit == "supplement" else roman(sec))
                    numtxt = alpha(sub)
                    htxt = alpha(sub) + ".~" + title
                hd = "\\hypertarget{" + bm(label) + "}{" + htxt + "}" if label else htxt
                if label:
                    self.anchors.add(label)
                out.append("\n\n\\subsection*{" + hd + "}\n\n")
            elif kind == "subsubsection":
                subsub += 1
                htxt = f"{subsub}) {title}:" if not star else f"{title}:"
                hd = "\\textit{" + htxt + "}" + ("\\label{" + bm(label) + "}" if label else "")
                if label:
                    self.anchors.add(label)
                out.append("\n\n" + hd + " ")
            else:  # paragraph
                hd = "\\textit{" + title + ":}"
                if label:
                    self.anchors.add(label)
                    hd = hd + "\\label{" + bm(label) + "}"
                out.append("\n\n" + hd + " ")
        return "".join(out)

    # ----- floats -----
    def pass_floats(self, s: str) -> str:
        counters = {"figure": 0, "table": 0}
        pat = re.compile(r"\\begin\{(figure|table)(\*?)\}(?:\[[^\]]*\])?(.*?)\\end\{\1\2\}", re.S)

        def sub(m):
            kind, star, body = m.group(1), m.group(2), m.group(3)
            counters[kind] += 1
            n = counters[kind]
            if kind == "table":
                numtxt = ("S" + str(n)) if self.unit == "supplement" else roman(n)
            else:
                numtxt = ("S" + str(n)) if self.unit == "supplement" else str(n)
            fl = {"id": len(self.floats) + 1, "kind": kind, "wide": bool(star) and self.unit != "supplement", "number": numtxt}
            # caption
            cm = cmd_re("caption").search(body)
            if not cm:
                self.warn(f"{kind} {numtxt} has no caption")
                cap = ""
            else:
                j = cm.end()
                if j < len(body) and body[j] == "[":
                    _, j = grab(body, j, "[", "]")
                cap, k = grab(body, skip_ws(body, j))
                body = body[:cm.start()] + body[k:]
            labs = re.findall(r"\\label\{([^}]*)\}", body) + re.findall(r"\\label\{([^}]*)\}", cap)
            cap = re.sub(r"\\label\{[^}]*\}", "", cap)
            body = re.sub(r"\\label\{[^}]*\}", "", body)
            if labs:
                fl["label"] = labs[0]
                self.anchors.update(labs)
                self.float_numbers[labs[0]] = numtxt
                # remember so that cleveref text can be checked against aux
            fl["caption"] = self.frag(cap, "cap")
            if kind == "figure":
                igs = []
                for im in cmd_re("includegraphics").finditer(body):
                    j = skip_ws(body, im.end())
                    opts = ""
                    if j < len(body) and body[j] == "[":
                        opts, j = grab(body, j, "[", "]")
                    path, _ = grab(body, skip_ws(body, j))
                    igs.append((opts, path))
                if not igs:
                    self.warn(f"figure {numtxt} has no \\includegraphics")
                fl["images"] = [self._image_spec(o, p, fl["wide"]) for o, p in igs]
                fl["note"] = None
            else:
                tm = re.search(r"\\begin\{tabular\}", body)
                if not tm:
                    self.warn(f"table {numtxt} has no tabular")
                    fl["tabular"] = None
                    rest = body
                else:
                    spec, j = grab(body, tm.end())
                    em = re.search(r"\\end\{tabular\}", body[j:])
                    tab_body = body[j:j + em.start()]
                    fl["tabular"] = parse_tabular(spec, tab_body)
                    rest = body[:tm.start()] + body[j + em.end():]
                    # drop the (now empty) wrappers around the tabular
                for cname, na in (("resizebox", 2), ("parbox", 1), ("adjustbox", 1)):
                    rest = re.sub(r"\\begin\{adjustbox\}\{[^}]*\}|\\end\{adjustbox\}", "", rest)
                rest = re.sub(r"\\resizebox\s*\{[^}]*\}\s*\{[^}]*\}\s*\{\s*\}", "", rest)
                rest = re.sub(r"\\parbox(?:\[[^\]]*\])?\s*\{[^}]*\}\s*\{", "{", rest)
                rest = re.sub(r"\\renewcommand\s*\{[^}]*\}\s*\{[^}]*\}", "", rest)
                rest = re.sub(r"\\(centering|vspace\*?\{[^}]*\})", "", rest)
                rest = rest.strip()
                if rest.startswith("{") and rest.endswith("}"):
                    try:
                        inner, e = grab(rest, 0)
                        if e == len(rest):
                            rest = inner.strip()
                    except TexError:
                        pass
                fl["note"] = self.frag(rest, "note") if rest.strip() else None
                if fl["tabular"]:
                    for r in fl["tabular"]["rows"]:
                        for c in r["cells"]:
                            c["frag"] = self.frag(self._cell(c["text"]), "cell")
            self.floats.append(fl)
            return "\n\n" + S + "FLOAT:" + str(fl["id"]) + S + "\n\n"
        return pat.sub(sub, s)

    def _cell(self, t: str) -> str:
        def mk(a, o):
            return re.sub(r"\\\\\*?", r"\\newline ", a[0])
        t = replace_cmd(t, "makecell", mk, opt=True)
        t = replace_cmd(t, "thead", mk, opt=True)
        return t

    def _image_spec(self, opts: str, path: str, wide: bool) -> dict:
        full = 7.2 if wide else self.col_in
        width = full
        mm = re.search(r"width\s*=\s*([0-9.]*)\s*\\(textwidth|columnwidth|linewidth)", opts)
        if mm:
            frac = float(mm.group(1)) if mm.group(1) else 1.0
            base = {"textwidth": 7.2, "columnwidth": self.col_in, "linewidth": full}[mm.group(2)]
            width = frac * base
        else:
            mm = re.search(r"width\s*=\s*([0-9.]+)\s*(in|cm|pt|mm)", opts)
            if mm:
                v = float(mm.group(1))
                width = v / {"in": 1, "cm": 2.54, "pt": 72.27, "mm": 25.4}[mm.group(2)]
        width = min(width, full)
        p = (self.root / path)
        png = p.with_suffix(".png")
        if not png.exists():
            self.warn(f"no PNG preview for {path}")
        return {"path": str(png.resolve()), "width_in": round(width, 3), "source": path}

    OK_CMDS = {"emph", "textit", "textbf", "texttt", "textsc", "textsubscript", "textsuperscript", "underline", "hyperlink",
               "hl", "hypertarget", "verb", "item", "begin", "end", "section", "subsection", "label", "ldots", "dots", "par", "newline",
               "textendash", "textemdash", "oe", "OE", "ae", "AE", "ss", "o", "O", "textrm", "textsf", "mathrm",
               "href", "url", "quad", "qquad", "textbackslash", "textasciitilde", "textasciicircum", "textquotesingle",
               "textquotedbl", "textless", "textgreater", "textbar", "textdegree", "texttimes", "textpm", "S", "P",
               "copyright", "dag", "ddag", "pounds", "euro", "i", "j", "L", "l"}

    def audit(self, text: str, where: str = "body"):
        """Warn about LaTeX commands that survive preprocessing and that pandoc may silently drop."""
        t = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
        t = re.sub(r"\$[^$]*\$", "", t)
        t = re.sub(r"\\verb(.).*?\1", "", t)
        left = sorted({c for c in re.findall(r"\\([a-zA-Z]+)", t) if c not in self.OK_CMDS})
        if left:
            self.warn(f"LaTeX command(s) left in {where} that pandoc may drop silently: " + ", ".join("\\" + c for c in left))

    # ----- main entry -----
    def run(self) -> dict:
        src = strip_comments(read(self.tex_path))
        pre, rest = src.split("\\begin{document}", 1)
        body = rest.split("\\end{document}")[0]
        self.collect_preamble(pre)
        for m in re.finditer(r"\\externaldocument(?:\[([^\]]*)\])?\{([^}]*)\}", pre):   # xr: labels of another document
            ext = (self.root / m.group(2)).with_suffix(".aux")
            if ext.exists():
                other = Aux(ext)
                for lab, d in other.labels.items():
                    self.aux.labels[(m.group(1) or "") + lab] = d
            else:
                self.warn(f"external aux not found: {ext}")
        flags = self.flags(src)
        body = self.flatten(body)
        body = self.resolve_ifs(body, flags)

        def take(name, opt=False):
            nonlocal body
            got = []
            def f(a, o):
                got.append(a[0])
                return ""
            body = replace_cmd(body, name, f, opt=opt)
            return got[-1] if got else None
        self.meta["title"] = take("title") or ""
        author = take("author") or ""
        thanks = []
        author = replace_cmd(author, "thanks", lambda a, o: thanks.append(a[0]) or "")
        author = replace_cmd(author, "IEEEmembership", lambda a, o: ", \\textit{" + a[0] + "}")
        self.meta["author"] = re.sub(r"%.*", "", author).strip()
        self.meta["thanks"] = thanks
        body = replace_cmd(body, "markboth", lambda a, o: "", nargs=2)
        body = re.sub(r"\\maketitle", "", body)
        am = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", body, re.S)
        self.meta["abstract"] = am.group(1).strip() if am else ""
        if am:
            body = body[:am.start()] + body[am.end():]
        km = re.search(r"\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}", body, re.S)
        self.meta["keywords"] = km.group(1).strip() if km else ""
        if km:
            body = body[:km.start()] + body[km.end():]
        body = re.sub(r"\\bibliographystyle\{[^}]*\}", "", body)
        body = re.sub(r"\\bibliography\{[^}]*\}", "\n\n" + S + "BIB" + S + "\n\n", body)
        body = re.sub(r"\\nocite\{[^}]*\}", "", body)
        # biographies (camera-ready build only)
        body = re.sub(r"\\begin\{IEEEbiography(?:nophoto)?\}\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}(.*?)\\end\{IEEEbiography(?:nophoto)?\}",
                      lambda m: "\n\n\\textbf{" + m.group(1) + "} " + m.group(2).strip() + "\n\n", body, flags=re.S)

        body = self.pass_floats(body)
        body = self.pass_equations(body)
        body = self.pass_theorems(body)
        body = self.pass_headings(body)
        # check numbering against the LaTeX run
        for lab, num in self.eq_numbers.items():
            d = self.aux.display(lab)
            if d is not None and d != num:
                self.warn(f"equation number mismatch for {lab}: own {num}, aux {d}")
        for lab, num in self.float_numbers.items():
            d = self.aux.display(lab)
            if d is not None and d != num:
                self.warn(f"float number mismatch for {lab}: own {num}, aux {d}")
        self.fragments["title"] = self.meta["title"]
        self.fragments["author"] = self.meta["author"]
        self.fragments["abstract"] = self.meta["abstract"]
        self.fragments["keywords"] = self.meta["keywords"]
        for i, t in enumerate(self.meta["thanks"]):
            self.fragments[f"thanks{i}"] = t
        # bibliography fragments
        self.bib = []
        if self.bbl_path and Path(self.bbl_path).exists():
            for key, raw in parse_bbl(self.bbl_path):
                num = self.aux.cites.get(key)
                raw = re.sub(r"\\BIBentry(ALT|STD)interwordspacing", "", raw)
                raw = re.sub(r"\\newblock\s*", " ", raw)
                raw = re.sub(r"\\BIBforeignlanguage\{[^}]*\}\{([^}]*)\}", r"\1", raw)
                fid = f"bib{num}"
                self.fragments[fid] = raw.strip()
                self.bib.append((key, num, fid))
        body = self.clean_text(body)
        for fid in list(self.fragments):
            self.fragments[fid] = self.clean_text(self.fragments[fid])
        self.audit(body)
        for fid, txt in self.fragments.items():
            self.audit(txt, fid)
        macros = "\n".join(self.macros)
        parts = [macros, "", body, "", S + "FRAGMENTS" + S, ""]
        for fid, txt in self.fragments.items():
            parts.append(S + "FRAG:" + fid + S)
            parts.append("")
            parts.append(txt)
            parts.append("")
        return {"latex": "\n".join(parts), "floats": self.floats, "bib": self.bib, "urls": self.url_table,
                "warnings": self.warnings, "anchors": sorted(self.anchors), "meta": self.meta, "unit": self.unit}
