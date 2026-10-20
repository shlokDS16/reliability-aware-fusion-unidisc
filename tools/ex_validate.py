"""Extraction evidence validator for Paper 1 (form v0.5).

Specification: research/review/extraction/EXTRACTION-PLAN-v0.5.md (s10.3 sign checks, s11), -v0.4.md (s5.4
string keys), -v0.3.md s6 (table-aware checks N1-N6, checks 1-12), -v0.2.md s6 (prose checks P1-P4, row match,
caption, record-level checks), extractor-brief-v0.5.md E1-E5, KA1, U9, U11; schema extraction-schema-v0.5.json.
Resolutions of ambiguous spec text are listed in analysis/extraction/ex_validate-test-log.txt.

    python -I tools/ex_validate.py --record <extraction .json> --text <fulltext .txt> [--schema <schema>]
        [--metric-lookup <csv>] [--out <report .jsonl>]
    python -I tools/ex_validate.py --self-test       (built-in synthetic fixtures; exit 0 if all pass, else 1)
A whole session (many records, the dispatched texts, pass tags, block checks) goes through tools/ex_validate_batch.py.

Output: one JSON line per check {id, extractor, check, ref, status, severity, detail}, then one summary line.
severity is pass, fail, warn (the unit goes to the second reader), info, or route (EC review list). Exit 0 if
no check fails, 1 if any check fails, 2 on a usage, input or schema-load error.

analysis/screening/quote_check.py is imported read-only by file path (never edited); prose quotes go through
quote_check.quote_status unchanged. Standard library only: the record is validated with jsonschema
(Draft 2020-12) when it imports, else with the built-in validator below, which implements every keyword the
v0.5 schema uses. The run is deterministic: no randomness, no clock, output in record order.

Shared sign rules (section "sign"): the metric direction list (the KA1(b) list below plus the lookup CSV), the metric
key, the printed arrows of a unit and the final-sign rule live here and are imported by
analysis/extraction/agreement.py, so both tools give one unit the same sign (analysis/extraction/stageA-gaps-log.txt
G3). Changes of 1.1.0 against the A20/A21 resolutions of ex_validate-test-log.txt: an arrow in metric_printed counts
like one in column_printed; a K unit whose sign a printed arrow settles is not routed; a null higher_is_better that
the lookup direction settles is not routed (info line null_resolved_by_lookup; agreement R3: null is not a
conflict); a header arrow against the lookup direction routes like one against higher_is_better; the CSV must use
true / false / empty and may not change a KA1(b) direction.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

TOOL_VERSION = "1.1.0"
ROOT = Path(__file__).resolve().parents[1]
QUOTE_CHECK_PATH = ROOT / "analysis" / "screening" / "quote_check.py"
DEFAULT_SCHEMA = ROOT / "research" / "review" / "extraction" / "extraction-schema-v0.5.json"


def _load_quote_check():
    spec = importlib.util.spec_from_file_location("quote_check_readonly", QUOTE_CHECK_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {QUOTE_CHECK_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qc = _load_quote_check()

# ------------------------------------------------------------------------------------------------ constants
MAX_WORDS = 40                     # prose quotes and cell entries (label tokens + cell tokens)
MIN_LETTER_WORDS = 3               # P3
CAPTION_MIN, CAPTION_MAX = 6, 40
NOTES_MAX_WORDS = 60
PAGE_RE = re.compile(r"^=== page (\d+) ===$")
VALUE_RE = re.compile(r"^[-+−±]?(\d[\d.,]*|\.\d+)(%|x|×)?[↑↓*†‡]*$")
VALUE_WORDS = frozenset({"-", "–", "—", "n/a", "N/A", "✓", "✗", "×"})
ARROWS = "↑↓"
FORMS = ("raw", "kept", "dropped")          # N2: no join, line-end hyphen kept, hyphen dropped
_PAREN_SPLIT = re.compile(r"(?<=\))(?=[A-Za-z0-9])")      # N3
_ARROW_SPLIT = re.compile(r"([↑↓])")                       # N3
_HYPH_END = re.compile(r"[A-Za-z0-9]-$")                    # N2
_INT_LINE = re.compile(r"^\s*\d+\s*$")                     # N6
_CIT_TRAIL = re.compile(r"\s*\([^()]*\b(?:19|20)\d{2}[a-z]?\)\s*$")
_OURS = re.compile(r"\(\s*ours\s*\)", re.IGNORECASE)
_MARKERS = re.compile(r"[†‡§¶*]")
_TRAIL_PAREN = re.compile(r"\s*\([^()]*\)\s*$")
_LOC_RE = re.compile(r"^p\.\s?\d+, (§.+|abstract)$")
_CAPTION_START = re.compile(r"^(Table|Tab\.|Figure|Fig\.)\s")
F2_ORDER = "ATPSCGM"

# KA1(b) convention list = the metric lookup of plan v0.5 s5.4 (normalised key -> (metric id, higher_is_better))
_KA1_TRUE = {"accuracy": "accuracy", "acc": "accuracy", "acc.": "accuracy", "exactmatch": "exact-match",
             "em": "exact-match", "bleu": "bleu", "rouge-l": "rouge-l", "rougel": "rouge-l", "cider": "cider",
             "clipscore": "clip-score", "clip-score": "clip-score", "tokenspersecond": "tps", "tps": "tps",
             "tokensperforward": "tpf", "tpf": "tpf", "speed-up": "speed-up", "speedup": "speed-up"}
_KA1_FALSE = {"perplexity": "perplexity", "ppl": "perplexity", "nll": "nll", "bitspertoken": "bits-per-token",
              "fid": "fid", "latency": "latency", "numberofsteps": "steps", "steps": "steps", "nfe": "nfe"}
_KA1_QUALIFIERS = {"top-1", "top1", "avg.", "avg", "gen.", "gen", "average", "mean"}
_PASS_AT = re.compile(r"^pass@(\d+|k)$")


# ------------------------------------------------------------------------------------------------ normalisation
def norm(s):
    """N1: quote_check.normalise (read-only import)."""
    return qc.normalise(s or "")


def _split_token(tok, keep_arrows=False):
    out = []
    for part in _PAREN_SPLIT.split(tok):
        for p in _ARROW_SPLIT.split(part):
            if not p:
                continue
            if p in ARROWS and not keep_arrows:
                continue
            out.append(p)
    return out


def _strip_enclosing(tok):
    """N5: a header token compared without enclosing parentheses."""
    if tok.startswith("("):
        tok = tok[1:]
    if tok.endswith(")"):
        tok = tok[:-1]
    return tok


def tokens_of(s, header=False, keep_arrows=False):
    """N1, N3, N4 (and N5 for header tokens) on one string."""
    out = []
    for raw in norm(s).split(" "):
        if not raw:
            continue
        for t in _split_token(raw, keep_arrows):
            if header and t not in ARROWS:
                t = _strip_enclosing(t)
            if t and t != "|":
                out.append(t)
    return out


def needle_forms(s, header=False):
    """N2 on a quoted string: a token ending in letter/digit + '-' joined with the next token, two ways."""
    toks = tokens_of(s, header)

    def join(drop):
        out, i = [], 0
        while i < len(toks):
            t = toks[i]
            if i + 1 < len(toks) and _HYPH_END.search(t):
                out.append((t[:-1] if drop else t) + toks[i + 1])
                i += 2
            else:
                out.append(t)
                i += 1
        return out

    return {"raw": toks, "kept": join(False), "dropped": join(True)}


def value_like(tok):
    return bool(VALUE_RE.match(tok)) or tok in VALUE_WORDS


def label_key(s):
    """U11 key: normalise, trailing citation with a year, '(ours)' and markers removed, lower case, no whitespace."""
    t = _CIT_TRAIL.sub("", norm(s))
    t = _OURS.sub("", t)
    t = _MARKERS.sub("", t)
    return re.sub(r"\s+", "", t.lower())


def string_key(s):
    """Plan v0.4 s5.4 key of a benchmark or metric string."""
    t = _CIT_TRAIL.sub("", norm(s)).lower()
    toks = [_strip_enclosing(x) for x in _ARROW_SPLIT.sub(" ", t).split()]
    return "".join(x for x in toks if x not in ARROWS)


def col_key(s):
    return re.sub(r"\s+", "", norm(s))


def lenient_equal(a, b):
    """string_key equality, or label-core: one equals the other plus one trailing parenthesis (U11)."""
    ka, kb = string_key(a), string_key(b)
    if ka == kb:
        return True
    ca, cb = _TRAIL_PAREN.sub("", norm(a)), _TRAIL_PAREN.sub("", norm(b))
    return string_key(ca) == kb or ka == string_key(cb)


def leaf_parts(leaf):
    return [p.strip() for p in leaf.split(" / ")]


# ------------------------------------------------------------------------------------------------ text model
class Page:
    def __init__(self, number, lines):
        self.number = number
        self.lines = list(lines)
        self.footer = None
        nonblank = [i for i, ln in enumerate(self.lines) if ln.strip()]
        for i in reversed(nonblank[-3:]):                      # N6: one footer per page, nearest the end
            if _INT_LINE.match(self.lines[i]):
                self.footer = i
                self.lines[i] = ""
                break
        self.norm_lines = [" ".join(norm(ln).split()) for ln in self.lines]
        self.rows = self._forms(header=False)
        self.heads = self._forms(header=True)
        self._lis = {}

    def _forms(self, header):
        per_line = [tokens_of(ln, header) for ln in self.lines]
        raw = [(t, li, j == 0) for li, toks in enumerate(per_line) for j, t in enumerate(toks)]
        kept, dropped, consumed = [], [], set()
        for li, toks in enumerate(per_line):
            nxt = per_line[li + 1] if li + 1 < len(per_line) else []
            for j, t in enumerate(toks):
                if j == 0 and li in consumed:
                    continue
                if j == len(toks) - 1 and nxt and _HYPH_END.search(t):
                    kept.append((t + nxt[0], li, j == 0))
                    dropped.append((t[:-1] + nxt[0], li, j == 0))
                    consumed.add(li + 1)
                else:
                    kept.append((t, li, j == 0))
                    dropped.append((t, li, j == 0))
        return {"raw": raw, "kept": kept, "dropped": dropped}

    def token_range(self, kind, form, l0, l1):
        """Token index range of lines [l0, l1) in a form."""
        key = (kind, form)
        if key not in self._lis:
            self._lis[key] = [x[1] for x in (self.rows if kind == "rows" else self.heads)[form]]
        lis = self._lis[key]
        return bisect.bisect_left(lis, l0), bisect.bisect_left(lis, l1)


class Text:
    def __init__(self, lines):
        self.lines = [ln.rstrip("\r") for ln in lines]
        self.full = "\n".join(self.lines)
        buckets, cur = {}, None
        for ln in self.lines:
            m = PAGE_RE.match(ln.strip())
            if m:
                cur = int(m.group(1))
                buckets.setdefault(cur, [])
                continue
            buckets.setdefault(0 if cur is None else cur, []).append(ln)
        self.has_markers = any(k > 0 for k in buckets)
        if not self.has_markers:
            buckets = {1: buckets.get(0, [])}
        self.pages = {n: Page(n, ls) for n, ls in buckets.items()}

    @classmethod
    def from_file(cls, path):
        data = Path(path).read_bytes().decode("utf-8", errors="replace")
        return cls(data.split("\n"))

    def page(self, n):
        return self.pages.get(n)

    def page_text(self, n):
        p = self.pages.get(n)
        return "\n".join(p.lines) if p else ""


def find_runs(toks, needle, lo=0, hi=None):
    """Start positions p in [lo, hi) with toks[p:p+len(needle)] == needle (toks: list of (str, li, init))."""
    n = len(needle)
    hi = len(toks) if hi is None else hi
    if n == 0:
        return []
    out = []
    for p in range(lo, hi - n + 1):
        if toks[p][0] == needle[0] and all(toks[p + k][0] == needle[k] for k in range(1, n)):
            out.append(p)
    return out


def whole_word_find(hay, needle):
    start = hay.find(needle)
    while start >= 0:
        end = start + len(needle)
        left_ok = start == 0 or not (qc._joined(hay[start - 1]) and qc._joined(needle[0]))
        right_ok = end == len(hay) or not (qc._joined(hay[end]) and qc._joined(needle[-1]))
        if left_ok and right_ok:
            return True
        start = hay.find(needle, start + 1)
    return False


def passage_found(passage, text):
    """Contiguous whole-word occurrence after normalise (and the de-hyphenated fallback); no negation window."""
    q, t = norm(passage), norm(text)
    if not q:
        return False
    return whole_word_find(t, q) or whole_word_find(qc._dehyphen(t), qc._dehyphen(q))


# ------------------------------------------------------------------------------------------------ findings
class Report:
    def __init__(self, rid="", extractor=""):
        self.rid, self.extractor, self.items = rid, extractor, []

    def emit(self, check, ref, status, severity, detail=""):
        self.items.append({"id": self.rid, "extractor": self.extractor, "check": check, "ref": ref,
                           "status": status, "severity": severity, "detail": detail})

    def ok(self, check, ref, status="pass", detail=""):
        self.emit(check, ref, status, "pass", detail)

    def fail(self, check, ref, status, detail=""):
        self.emit(check, ref, status, "fail", detail)

    def warn(self, check, ref, status, detail=""):
        self.emit(check, ref, status, "warn", detail)

    @property
    def n_fail(self):
        return sum(1 for x in self.items if x["severity"] == "fail")


# ------------------------------------------------------------------------------------------------ tables
class TableInfo:
    def __init__(self, entry):
        self.entry = entry
        self.id = entry.get("id", "")
        self.columns = list(entry.get("columns") or [])
        self.roles = list(entry.get("column_roles") or [])
        self.row_groups = list(entry.get("row_groups") or [])
        self.levels = entry.get("header_levels", 1)
        self.header_page = None
        self.header_ok = False
        self.map_ok = False
        self.order = "skipped"          # verified | mismatch | unverified | skipped
        self.header_needle = needle_forms(entry.get("header", ""), header=True)
        self.leaf_arrows = {}           # column index (0-based) -> set of directions printed after the leaf

    def part_roles(self, leaf):
        parts = leaf_parts(leaf)
        if not self.roles:
            return [(p, None) for p in parts]
        return [(p, self.roles[min(i, len(self.roles) - 1)]) for i, p in enumerate(parts)]

    @property
    def column_order_clean(self):
        return self.header_ok and self.map_ok and self.order == "verified"


def locate_header(text, info, pages):
    """First (page, form, last line index) where the header tokens are a contiguous run."""
    for pn in pages:
        page = text.page(pn)
        if page is None:
            continue
        for f in FORMS:
            hits = find_runs(page.heads[f], info.header_needle[f])
            if hits:
                p = hits[0]
                return pn, f, page.heads[f][p + len(info.header_needle[f]) - 1][1]
    return None


def _seq_align(header_toks, parts):
    pos, out = 0, []
    for part in parts:
        if not part:
            return None
        n, hit = len(part), -1
        for p in range(pos, len(header_toks) - n + 1):
            if header_toks[p:p + n] == part:
                hit = p
                break
        if hit < 0:
            return None
        out.append((hit, hit + n))
        pos = hit + n
    return out


def check_table(text, info, rep):
    e, tid = info.entry, info.id
    page = e.get("page")
    loc = locate_header(text, info, [page, page - 1] if isinstance(page, int) else [])
    if loc:
        info.header_page, info.header_ok = loc[0], True
        rep.ok("table", tid, "header_found", f"page {loc[0]} ({loc[1]} form)")
    else:
        prev = page - 1 if isinstance(page, int) else "?"
        rep.fail("table", tid, "header_not_found", f"header tokens not a contiguous run on page {page} or {prev}")

    # caption (v0.2 check 6)
    cap = e.get("caption", "")
    if e.get("where") == "untitled table" and cap == "":
        rep.ok("table", tid, "caption_exempt", "untitled table")
    else:
        nwords = len(norm(cap).split())
        pages = [page - 1, page, page + 1] if isinstance(page, int) else []
        if not any(passage_found(cap, text.page_text(p)) for p in pages):
            rep.fail("table", tid, "caption_not_found", f"not on pages {pages}")
        elif not CAPTION_MIN <= nwords <= CAPTION_MAX:
            rep.fail("table", tid, "caption_length", f"{nwords} words")
        elif not _CAPTION_START.match(norm(cap)):
            rep.fail("table", tid, "caption_start", "caption must start with Table, Tab., Figure or Fig.")
        else:
            rep.ok("table", tid, "caption_found", f"{nwords} words")

    # leaf map membership (every token of every part occurs in the header tokens, in some N2 form)
    missing = []
    hsets = {f: set(info.header_needle[f]) for f in FORMS}
    for leaf in info.columns:
        for part in leaf_parts(leaf):
            pf = needle_forms(part, header=True)
            if not pf["raw"] or not any(all(t in hsets[f] for t in pf[f]) for f in FORMS):
                missing.append(part)
    if missing:
        rep.fail("table", tid, "map_not_in_header", "parts not in header: " + "; ".join(missing))
    else:
        info.map_ok = True
        rep.ok("table", tid, "map_in_header", f"{len(info.columns)} leaves")

    # order: single-level leaves in header order (fail); two-level bottom and level-1 parts (warning)
    if not info.columns:
        return
    two = verify_order(info)
    if info.order == "verified":
        rep.ok("table", tid, "column_order_verified", "two-level: bottom and level-1 parts" if two else "single-level")
    elif two:
        rep.warn("table", tid, "column_order_unverified", "two-level header: order of the leaf parts not confirmed")
    else:
        rep.fail("table", tid, "column_order_mismatch", "leaves do not occur in header order")


def verify_order(info):
    """Column order from the record alone (header string and leaves; no text): sets info.order to verified,
    unverified (two-level) or mismatch (single-level) and, when verified, the header arrows of each leaf.
    Returns True for a two-level header. check_table and record_arrows both use it."""
    two = info.levels == 2
    if not info.columns:
        return two
    for f in FORMS:
        bottom = [needle_forms(leaf_parts(leaf)[-1], header=True)[f] for leaf in info.columns]
        if not two:
            whole = [needle_forms(leaf, header=True)[f] for leaf in info.columns]
            al = _seq_align(info.header_needle[f], whole)
            if al is not None:
                info.order = "verified"
                break
        else:
            top, prev = [], None
            for leaf in info.columns:
                t = needle_forms(leaf_parts(leaf)[0], header=True)[f]
                if t != prev:
                    top.append(t)
                prev = t
            if _seq_align(info.header_needle[f], bottom) is not None and _seq_align(info.header_needle[f], top) is not None:
                info.order = "verified"
                break
    if info.order == "verified":
        _leaf_arrows(info)
    elif two:
        info.order = "unverified"
    else:
        info.order = "mismatch"
    return two


def _leaf_arrows(info):
    """Arrows printed with each leaf in the header (raw form), for the sign route; only after a verified order."""
    toks = tokens_of(info.entry.get("header", ""), header=True, keep_arrows=True)
    plain_idx = [i for i, t in enumerate(toks) if t not in ARROWS]
    plain = [toks[i] for i in plain_idx]
    parts = [tokens_of(leaf if info.levels == 1 else leaf_parts(leaf)[-1], header=True) for leaf in info.columns]
    al = _seq_align(plain, parts)
    if al is None:
        return
    for ci, (s, e) in enumerate(al):
        first, last = plain_idx[s], plain_idx[e - 1]
        dirs = {("up" if t == "↑" else "down") for t in toks[first:last + 1] if t in ARROWS}
        k = last + 1
        while k < len(toks) and toks[k] in ARROWS:
            dirs.add("up" if toks[k] == "↑" else "down")
            k += 1
        if dirs:
            info.leaf_arrows[ci] = dirs


# ------------------------------------------------------------------------------------------------ cells
class RowMatch:
    def __init__(self):
        self.status = "row_not_found"
        self.form = None
        self.end = None          # token index after the last cell token in the page form
        self.page = None


def _element_tokens(el):
    return len(tokens_of(el)) if el != "" else 0


def _segment(text, info, cell, rep, cid):
    """Row-group segment (line range) of the cell's page and the row_group finding."""
    page = text.page(cell.get("page"))
    if page is None:
        return None, None
    start = 0
    hdr = locate_header(text, info, [cell.get("page")])
    if hdr is not None and hdr[0] == cell.get("page"):
        start = hdr[2] + 1
    n = len(page.lines)
    rg = cell.get("row_group", "")
    groups = info.row_groups
    gnorm = [" ".join(norm(g).split()) for g in groups]

    def first_line(targets, lo):
        for i in range(lo, n):
            if page.norm_lines[i] in targets:
                return i
        return None

    if not groups:
        if rg:
            rep.fail("row_group", cid, "row_group_unknown", f"table {info.id} declares no row groups")
        else:
            rep.ok("row_group", cid, "pass", "table has no row groups")
        return page, (start, n)
    if rg == "":
        first = first_line(set(gnorm), start)
        pre = (start, first if first is not None else n)
        return page, ("pre", pre, (start, n))
    if rg not in groups:
        rep.fail("row_group", cid, "row_group_unknown", f"'{rg}' is not one of the table's row groups")
        return page, (start, n)
    gi = groups.index(rg)
    later = set(gnorm[gi + 1:])
    g0 = first_line({gnorm[gi]}, start)
    if g0 is not None:
        end = first_line(later, g0 + 1) if later else None
        rep.ok("row_group", cid, "pass", f"segment lines {g0 + 1}-{end if end is not None else n}")
        return page, (g0 + 1, end if end is not None else n)
    prev = text.page(cell.get("page") - 1) if isinstance(cell.get("page"), int) else None
    if prev is not None and hdr is None and gnorm[gi] in prev.norm_lines:
        end = first_line(later, 0) if later else None
        rep.ok("row_group", cid, "pass", "row group continues from the previous page")
        return page, (0, end if end is not None else n)
    rep.fail("row_group", cid, "row_group_not_found", f"'{rg}' is not a whole line after the header on page {cell.get('page')}")
    return page, (start, n)


def _match_row(page, cell, seg, offset_tokens):
    """Row match (v0.2 step 3 on the segment): RowMatch with status pass, row_not_found, cells_mismatch,
    ambiguous_row or occurrence_mismatch."""
    res = RowMatch()
    res.page = page
    label_n = needle_forms(cell.get("row_label", ""))
    cells_n = needle_forms(" ".join(c for c in (cell.get("cells") or []) if c != ""))
    occ = cell.get("occurrence")
    any_label = False
    for f in FORMS:
        toks = page.rows[f]
        lo, hi = page.token_range("rows", f, seg[0], seg[1])
        L, C = label_n[f], cells_n[f]
        matches = []
        for p in find_runs(toks, L, lo, hi):
            if not (toks[p][2] or (p > 0 and value_like(toks[p - 1][0]))):
                continue
            any_label = True
            q = p + len(L) + offset_tokens
            if q + len(C) <= len(toks) and [t[0] for t in toks[q:q + len(C)]] == C:
                matches.append(q + len(C))
        if matches:
            res.form = f
            if occ is None:
                if len(matches) == 1:
                    res.status, res.end = "pass", matches[0]
                else:
                    res.status = "ambiguous_row"
            elif occ <= len(matches):
                res.status, res.end = "pass", matches[occ - 1]
            else:
                res.status = "occurrence_mismatch"
            res.detail = f"{len(matches)} match(es) in segment, {f} form"
            return res
    res.status = "cells_mismatch" if any_label else "row_not_found"
    res.detail = "label found at a row start but the cells differ" if any_label else "label not at a row start in the segment"
    return res


def check_cells(text, tables, cells, rep):
    """Table-entry checks and cell checks 1-6; returns {cell id: RowMatch} and per-row completeness data."""
    infos = {}
    for t in tables:
        info = TableInfo(t)
        infos[info.id] = info
        check_table(text, info, rep)
    if not text.has_markers:
        rep.warn("text", "-", "no_page_markers", "text has no '=== page N ===' markers; read as page 1")

    by_id = {c.get("id"): c for c in cells}
    row_of, matches = {}, {}
    rows = {}
    for c in cells:
        cid = c.get("id", "")
        info = infos.get(c.get("table"))
        if info is None:
            rep.fail("refs", cid, "table_missing", f"table {c.get('table')} not in table_evidence")
            continue
        key = (c.get("table"), c.get("row_group", ""), c.get("row_label", ""), c.get("occurrence"))
        rows.setdefault(key, []).append(cid)
        row_of[cid] = key

    for c in cells:
        cid = c.get("id", "")
        info = infos.get(c.get("table"))
        if info is None:
            continue
        cpage = c.get("page")
        if text.page(cpage) is None:
            rep.fail("row", cid, "row_not_found", f"page {cpage} not in the text")
            matches[cid] = RowMatch()
            continue
        near = locate_header(text, info, [cpage, cpage - 1])
        if near is None:
            rep.fail("header_near_row", cid, "header_not_near_row", f"header of {info.id} not on page {cpage} or {cpage - 1}")
        else:
            rep.ok("header_near_row", cid, "pass", f"header on page {near[0]}")
        page, seg = _segment(text, info, c, rep, cid)
        # token offset of first_col: from entries of the same row that cover the earlier elements
        fc = c.get("first_col", 1) or 1
        offset = 0
        if fc > 1:
            known = {}
            for oid in rows.get(row_of[cid], []):
                o = by_id[oid]
                for k, el in enumerate(o.get("cells") or []):
                    known.setdefault((o.get("first_col", 1) or 1) + k, _element_tokens(el))
            offset = sum(known.get(k, 1) for k in range(1, fc))
        if isinstance(seg, tuple) and seg and seg[0] == "pre":
            _, pre, whole = seg
            m = _match_row(page, c, pre, offset)
            if m.status == "pass":
                rep.ok("row_group", cid, "pass", "ungrouped row before the first row group")
            else:
                rep.fail("row_group", cid, "row_group_missing", "the table declares row groups and the cell names none")
                m = _match_row(page, c, whole, offset)
        else:
            m = _match_row(page, c, seg, offset)
        matches[cid] = m
        if m.status == "pass":
            rep.ok("row", cid, "pass", m.detail)
        else:
            rep.fail("row", cid, m.status, m.detail)
        n_tok = len(tokens_of(c.get("row_label", ""))) + len(tokens_of(" ".join(x for x in (c.get("cells") or []) if x)))
        if n_tok > MAX_WORDS:
            rep.fail("length", cid, "too_long", f"{n_tok} label and cell tokens (max {MAX_WORDS})")
        else:
            rep.ok("length", cid, "pass", f"{n_tok} tokens")

    # rows: start, completeness, width
    complete, blanks = {}, {}
    for key, cids in rows.items():
        info = infos[key[0]]
        ref = "+".join(cids)
        entries = [by_id[x] for x in cids]
        if not any((e.get("first_col", 1) or 1) == 1 for e in entries):
            rep.fail("row_start", ref, "row_start_missing", "no entry of this row has first_col 1")
        else:
            rep.ok("row_start", ref, "pass")
        last = max(entries, key=lambda e: (e.get("first_col", 1) or 1) + len(e.get("cells") or []) - 1)
        width = (last.get("first_col", 1) or 1) + len(last.get("cells") or []) - 1
        nblank = sum(1 for e in entries for x in (e.get("cells") or []) if x == "")
        m = matches.get(last.get("id"))
        is_complete = False
        if m is not None and m.status == "pass":
            toks = m.page.rows[m.form]
            is_complete = m.end >= len(toks) or (not value_like(toks[m.end][0]) and toks[m.end][2])
        for x in cids:
            complete[x], blanks[x] = is_complete, nblank
        rep.emit("row_complete", ref, "complete" if is_complete else "incomplete", "info",
                 "next token is not a value and begins a line, or the page ends" if is_complete else "row not matched or followed by a value or mid-line token")
        nleaves = len(info.columns)
        if not is_complete:
            rep.emit("row_width", ref, "not_checked", "info", "row incomplete")
        elif width != nleaves:
            rep.fail("row_width", ref, "row_width_mismatch", f"{width} vs {nleaves}" + (f" with {nblank} declared blank" if nblank else ""))
        else:
            rep.ok("row_width", ref, "pass", f"{width} = {nleaves}" + (f" with {nblank} declared blank" if nblank else ""))
    return infos, by_id, matches, complete, blanks


# ------------------------------------------------------------------------------------------------ prose
def check_prose(text, prose, rep):
    """P1-P3 per prose entry, plus the loc format of E5 (warning)."""
    for e in prose:
        pid, quote = e.get("id", ""), e.get("quote", "")
        st = qc.quote_status(quote, text.full)
        if st == "found":
            rep.ok("prose_quote", pid, "found")
        else:
            rep.fail("prose_quote", pid, st, "quote_check.quote_status")
        nw = len(norm(quote).split())
        if nw > MAX_WORDS:
            rep.fail("prose_length", pid, "too_long", f"{nw} words (max {MAX_WORDS})")
        else:
            rep.ok("prose_length", pid, "pass", f"{nw} words")
        nl = sum(1 for w in norm(quote).split() if any(ch.isalpha() for ch in w))
        if nl < MIN_LETTER_WORDS:
            rep.fail("prose_letters", pid, "numeric_only", f"{nl} words with letters (min {MIN_LETTER_WORDS})")
        else:
            rep.ok("prose_letters", pid, "pass")
        if not _LOC_RE.match(e.get("loc", "")):
            rep.warn("loc", pid, "loc_format", "expected 'p.<page>, §<section>' or 'p.<page>, abstract'")


def value_in_quote(value, quote, occurrence):
    q, v = norm(quote), norm(value)
    if not v:
        return "value_not_in_quote", 0
    pat = re.compile(r"(?<![\w.])" + re.escape(v) + r"(?![\w]|\.\d)")
    n = len(pat.findall(q))
    if n == 0:
        return "value_not_in_quote", n
    if occurrence is None:
        return ("pass" if n == 1 else "value_ambiguous"), n
    return ("pass" if occurrence <= n else "value_not_in_quote"), n


# ------------------------------------------------------------------------------------------------ values
VALUE_KEYS = ("ref", "kind", "group", "cell", "col", "prose", "value_printed", "value_occurrence", "column_printed",
              "figure_only", "origin", "arm_label", "orientation", "benchmark_printed", "metric_printed",
              "condition_printed", "second_factor_printed", "where")


def check_values(text, values, prose_by_id, infos, cells_by_id, matches, complete, blanks, rep):
    """Checks 7-12 for cell values, P4 for prose values, figure-only and unreadable rules."""
    seen = {}
    for v in values:
        ref, val = v["ref"], v.get("value_printed", "")
        cid, pid = v.get("cell"), v.get("prose")
        if val == "figure-only" and (v.get("figure_only") or (v.get("kind") == "H" and v.get("origin") == "F1-figure")):
            rep.ok("value", ref, "exempt", "figure_only")
            if pid and pid not in prose_by_id:
                rep.fail("refs", ref, "evidence_missing", f"prose {pid} not in evidence")
            continue
        if not cid and not pid:
            rep.fail("value", ref, "missing_evidence", "value has neither a cell nor a prose entry")
            continue
        if pid:
            e = prose_by_id.get(pid)
            if e is None:
                rep.fail("refs", ref, "evidence_missing", f"prose {pid} not in evidence")
            elif val == "unreadable":
                rep.fail("value", ref, "unreadable_needs_cell", "an unreadable F1 value needs a cell entry")
            else:
                st, n = value_in_quote(val, e.get("quote", ""), v.get("value_occurrence"))
                if st == "pass":
                    rep.ok("value", ref, "pass", f"{n} occurrence(s) in {pid}")
                else:
                    rep.fail("value", ref, st, f"{n} occurrence(s) in {pid}")
        if not cid:
            continue
        c = cells_by_id.get(cid)
        if c is None:
            rep.fail("refs", ref, "evidence_missing", f"cell {cid} not in cell_evidence")
            continue
        info = infos.get(c.get("table"))
        if info is None:
            continue
        col = v.get("col")
        if not isinstance(col, int):
            rep.fail("value", ref, "col_missing", "a cell value needs col")
            continue
        if v.get("where") and info.entry.get("where") and v["where"] != info.entry["where"]:
            rep.fail("where", ref, "where_mismatch", f"unit or group at {v['where']}, cell in {info.entry['where']}")
        # 7 value
        fc = c.get("first_col", 1) or 1
        els = c.get("cells") or []
        if val == "unreadable":
            rep.emit("value", ref, "no_value_check", "info", "unreadable F1 value: row located only")
        elif not fc <= col < fc + len(els):
            rep.fail("value", ref, "value_outside_cells", f"col {col} outside {fc}-{fc + len(els) - 1}")
        elif norm(els[col - fc]) != norm(val):
            rep.fail("value", ref, "value_mismatch", f"element {col} is {els[col - fc]!r}")
        else:
            rep.ok("value", ref, "pass")
        # 8-9 column
        leaf = info.columns[col - 1] if 1 <= col <= len(info.columns) else None
        cp = v.get("column_printed")
        if leaf is None:
            rep.fail("column", ref, "column_mismatch", f"col {col} beyond the {len(info.columns)}-leaf map")
        elif cp is None or col_key(cp) != col_key(leaf):
            rep.fail("column", ref, "column_mismatch", f"column_printed {cp!r} but map leaf {col} is {leaf!r}")
        elif complete.get(cid) and not blanks.get(cid) and info.column_order_clean:
            rep.ok("column", ref, "column_verified")
        else:
            why = []
            if not complete.get(cid):
                why.append("row incomplete")
            if blanks.get(cid):
                why.append("declared blank")
            if not info.column_order_clean:
                why.append(f"column order {info.order}")
            rep.warn("column", ref, "column_unverified", ", ".join(why))
        # 10 row group, second factor, benchmark, metric, condition
        rg = c.get("row_group", "")
        role_rg = info.entry.get("row_group_role", "none")
        bench, metric = v.get("benchmark_printed"), v.get("metric_printed")
        if role_rg == "benchmark" and bench is not None and rg:
            if label_key(bench) == label_key(rg):
                rep.ok("row_group", ref, "pass", "benchmark equals the row group")
            else:
                rep.fail("row_group", ref, "rowgroup_benchmark_mismatch", f"benchmark {bench!r}, row group {rg!r}")
        parts = info.part_roles(leaf) if leaf else []
        sf = v.get("second_factor_printed")
        if sf is not None and v.get("kind") == "K":
            targets = []
            if role_rg == "second-factor":
                targets.append(("row group", rg))
            targets += [("level-1 column part", p) for p, r in parts[:1] if r == "second-factor"]
            for what, tgt in targets:
                if label_key(sf) == label_key(tgt):
                    rep.ok("second_factor", ref, "pass", f"equals the {what}")
                else:
                    rep.fail("second_factor", ref, "second_factor_mismatch", f"{sf!r} against {what} {tgt!r}")
        for field, role, status in (("benchmark_printed", "benchmark", "benchmark_column_mismatch"),
                                    ("metric_printed", "metric", "metric_column_mismatch")):
            got = v.get(field)
            want = [p for p, r in parts if r == role]
            if got is None or not want:
                continue
            if lenient_equal(got, " / ".join(want)) or any(lenient_equal(got, w) for w in want):
                rep.ok(role, ref, "pass")
            else:
                rep.fail(role, ref, status, f"{got!r} against {' / '.join(want)!r}")
        cond = v.get("condition_printed")
        if cond is not None and v.get("kind") == "K":
            orient = v.get("orientation") or info.entry.get("orientation")
            want = [p for p, r in parts if r == "condition"]
            if role_rg == "condition":
                want.append(rg)
            if orient == "columns":
                rl = c.get("row_label", "")
                if not any(x is not None and lenient_equal(rl, x) for x in (bench, metric)):
                    want.append(rl)
            got = [p for p in leaf_parts(cond) if p] if cond else []
            pool = list(got)
            ok = len(got) == len(want)
            for w in want:
                hit = next((g for g in pool if lenient_equal(g, w)), None)
                if hit is None:
                    ok = False
                    break
                pool.remove(hit)
            if ok:
                rep.ok("condition", ref, "pass")
            else:
                rep.fail("condition", ref, "condition_mismatch", f"{cond!r} against {' / '.join(want)!r}")
        # 11 arm label
        arm = v.get("arm_label")
        if arm is not None and v.get("kind") == "K" and leaf is not None:
            orient = v.get("orientation") or info.entry.get("orientation")
            if orient == "rows":
                if label_key(arm) == label_key(c.get("row_label", "")):
                    rep.ok("label_row", ref, "pass")
                else:
                    rep.fail("label_row", ref, "label_row_mismatch", f"arm {arm!r}, row {c.get('row_label')!r}")
            elif orient == "columns":
                top = leaf_parts(leaf)[0]
                if label_key(arm) == label_key(top):
                    rep.ok("arm_column", ref, "pass")
                else:
                    rep.fail("arm_column", ref, "arm_column_mismatch", f"arm {arm!r}, column {top!r}")
        # 12 reuse
        k = (v.get("group"), cid, col)
        if k in seen:
            rep.fail("reuse", ref, "cell_reused", f"({cid}, col {col}) already used by {seen[k]} in group {k[0]}")
        else:
            seen[k] = ref
            rep.ok("reuse", ref, "pass")


def check_evidence(text, tables, cells, values, prose=(), rep=None):
    """Every evidence item of one record: tables, cells, prose entries and the values that cite them."""
    rep = rep or Report()
    prose = list(prose)
    infos, cells_by_id, matches, complete, blanks = check_cells(text, list(tables), list(cells), rep)
    check_prose(text, prose, rep)
    check_values(text, list(values), {e.get("id"): e for e in prose}, infos, cells_by_id, matches, complete, blanks, rep)
    return rep, infos, cells_by_id


# ------------------------------------------------------------------------------------------------ sign (v0.5 s10.3)
# Shared sign rules: the one source of metric directions and of the final-sign rule for this tool and for
# analysis/extraction/agreement.py, which imports this file by path (plan v0.4 s11.1: "one module, imported by
# ex_validate where the two share rules"). Direction list = the KA1(b) list above plus the lookup CSV
# (analysis/extraction/lookups/metric-ids-v1.csv); metric key = metric_norm (agreement's s5.4 key); printed arrows
# = unit_arrows; final sign = resolve_sign (agreement R3, plan v0.5 s10.3).
_MN_CIT = re.compile(r"\s*[\(\[][^()\[\]]*?(?:19|20)\d{2}[a-z]?[^()\[\]]*[\)\]]\s*$")
_MN_OURS = re.compile(r"\(\s*ours\s*\)", re.I)
_ARROW_ANY = re.compile(r"[↑↓⬆⬇]")
_UP, _DOWN = "↑⬆", "↓⬇"


def _mn_strip_tail(s):
    prev = None
    while prev != s:
        prev = s
        s = _MN_OURS.sub("", s).strip()
        s = _MN_CIT.sub("", s).strip()
    return s


def _mn_balanced(s):
    d = 0
    for ch in s:
        d += (ch == "(") - (ch == ")")
        if d < 0:
            return False
    return d == 0


def metric_norm(s):
    """Plan v0.4 s5.4 key of a metric or benchmark string (agreement.py's norm_bm): quote_check.normalise, lower
    case, arrows and enclosing parentheses removed, a trailing citation with a year and "(ours)" removed, all
    whitespace removed."""
    if s is None:
        return ""
    s = norm(_mn_strip_tail(_ARROW_ANY.sub("", str(s)))).lower()
    s = _ARROW_ANY.sub("", s)
    s = _mn_strip_tail(s).strip()
    while len(s) >= 2 and s[0] == "(" and s[-1] == ")" and _mn_balanced(s[1:-1]):
        s = s[1:-1].strip()
    return re.sub(r"\s+", "", s)


def parse_direction(s):
    """higher_is_better cell of the metric CSV: true, false or empty (any case); anything else is an error."""
    t = (s or "").strip().lower()
    if t in ("true", "false", ""):
        return True if t == "true" else False if t == "false" else None
    raise ValueError(f"higher_is_better must be true, false or empty, not {s!r}")


def ka1_table():
    """The KA1(b) list as {metric key: (metric id, higher_is_better)}."""
    table = {k: (v, True) for k, v in _KA1_TRUE.items()}
    table.update({k: (v, False) for k, v in _KA1_FALSE.items()})
    return table


def load_metric_lookup(path=None):
    """{metric key: (metric id, higher_is_better or None)} = the KA1(b) list, then the rows of the metric CSV
    (columns printed, id, higher_is_better), keyed by metric_norm(printed); a CSV row may give a KA1(b) name another
    id but not another direction. ValueError when a column is missing, a printed or id cell is empty, a printed
    cell starts with '#' (no comment rows), a direction is not true/false/empty, a KA1(b) name or a pass@k name
    gets another direction, or one metric id gets two directions."""
    table = ka1_table()
    ka1 = dict(table)
    if path:
        with open(path, encoding="utf-8", newline="") as f:
            rd = csv.DictReader(f)
            missing = [c for c in ("printed", "id", "higher_is_better") if c not in (rd.fieldnames or [])]
            if missing:
                raise ValueError(f"{path}: header lacks {missing} (first line must be printed,id,higher_is_better)")
            for n, row in enumerate(rd, start=2):
                printed, mid = (row.get("printed") or "").strip(), (row.get("id") or "").strip()
                if not printed or not mid:
                    raise ValueError(f"{path} line {n}: empty printed or id")
                if printed.startswith("#"):
                    raise ValueError(f"{path} line {n}: comment rows are not allowed")
                key, d = metric_norm(printed), parse_direction(row.get("higher_is_better"))
                if key in ka1 and ka1[key][1] != d:
                    raise ValueError(f"{path} line {n}: {printed!r} is a KA1(b) name with direction {ka1[key][1]}, not {d}")
                if _PASS_AT.match(key) and d is not True:
                    raise ValueError(f"{path} line {n}: pass@k is higher-is-better in KA1(b)")
                table[key] = (mid, d)
    dirs = {"pass@k": True}
    for mid, d in table.values():
        if mid in dirs and dirs[mid] != d:
            raise ValueError(f"metric id {mid} has two directions")
        dirs[mid] = d
    return table


def metric_directions(table):
    """{metric id: higher_is_better or None} of a lookup table (load_metric_lookup), pass@k included."""
    out = {"pass@k": True}
    out.update({mid: d for mid, d in table.values()})
    return out


def metric_lookup(metric, table):
    """(metric id, direction) or None: the whole key, else the key without KA1 qualifiers (top-1, avg., gen. ...),
    arrows and enclosing parentheses of single tokens, with pass@<n> or pass@k as one id."""
    key = metric_norm(metric)
    if key in table:
        return table[key]
    toks = [_strip_enclosing(t) for t in _ARROW_ANY.sub(" ", norm(metric).lower()).split()]
    toks = [t for t in toks if t and t not in _KA1_QUALIFIERS]
    core = "".join(toks)
    if _PASS_AT.match(core):
        return ("pass@k", True)
    return table.get(core)


def metric_key(metric, table):
    hit = metric_lookup(metric, table)
    return hit[0] if hit else "raw:" + metric_norm(metric)


def printed_dirs(s):
    """Directions of the arrows in one string: a subset of {"up", "down"}."""
    t = s if isinstance(s, str) else ""
    return ({"up"} if any(c in t for c in _UP) else set()) | ({"down"} if any(c in t for c in _DOWN) else set())


def unit_arrows(u, infos, cells_by_id):
    """(certain, header) directions printed with one sign unit (KA1(a)). certain: arrows in metric_printed, in each
    value's column_printed and, when the group (or the table) is columns-oriented, in the row label of each cited
    cell. header: arrows printed next to the cited leaf in a verified table header (A20: attribution in a
    linearised header is not certain, so they only route)."""
    dirs, header_dirs = set(printed_dirs(u.get("metric_printed"))), set()
    for v in u["values"]:
        dirs |= printed_dirs(v.get("column_printed"))
        c = cells_by_id.get(v.get("cell")) if v.get("cell") else None
        info = infos.get(c.get("table")) if c else None
        if c and info and (u.get("orientation") or info.entry.get("orientation")) == "columns":
            dirs |= printed_dirs(c.get("row_label", ""))
        if info and isinstance(v.get("col"), int):
            header_dirs |= info.leaf_arrows.get(v["col"] - 1, set())
    return dirs, header_dirs


def _single(dirs):
    return True if dirs == {"up"} else False if dirs == {"down"} else None


def sign_inputs(dirs, header_dirs):
    """(arrow, header_arrow) as True / False / None: one certain direction, else None; the header direction counts
    only when no certain arrow is printed at all (both directions printed = ambiguous = no arrow)."""
    return _single(dirs), (_single(header_dirs) if not dirs else None)


def resolve_sign(values, arrow, header_arrow, lookup_dir, ec_given=False, ec_value=None):
    """Final sign of a K unit (agreement.py R3, plan v0.5 s10.3), shared by both tools. values: the extractors'
    higher_is_better values (null allowed). Returns (final, source, routed).
    (1) a certain printed arrow sets the sign; (2) else the lookup direction when it is non-null, no non-null
    extractor value differs from it (null is not a conflict) and no header arrow differs from it or from an
    extractor value; (3) else the unit is routed to EC: EC's value, or "pending EC" without an EC file, or
    "unsigned" when EC gives none."""
    if arrow is not None:
        return arrow, "KA1(a) printed arrow", False
    nonnull = [v for v in values if v is not None]
    header_conflict = header_arrow is not None and (any(v != header_arrow for v in nonnull)
                                                    or (lookup_dir is not None and lookup_dir != header_arrow))
    if not header_conflict and lookup_dir is not None and all(v == lookup_dir for v in nonnull):
        return lookup_dir, "lookup", False
    if not ec_given:
        return None, "pending EC", True
    if ec_value is not None:
        return ec_value, "EC", True
    return None, "unsigned", True


def record_arrows(rec):
    """{(kind, index in units_h or units_k): (certain, header)} from the record alone (no text), exactly as
    check_signs sees them; agreement.py uses it for the printed-arrow step of the final sign."""
    infos = {}
    for t in _lst(rec.get("table_evidence")):
        if isinstance(t, dict):
            info = TableInfo(t)
            verify_order(info)
            infos[info.id] = info
    cells_by_id = {c.get("id"): c for c in _lst(rec.get("cell_evidence")) if isinstance(c, dict)}
    _, signs = record_values(rec)
    return {(u["kind"], u["index"]): unit_arrows(u, infos, cells_by_id) for u in signs}


def check_signs(sign_units, infos, cells_by_id, lookup, rep):
    """sign_units: dicts {ref, kind, group, metric_printed, hib, values: [{column_printed, cell, col}]}."""
    for u in sign_units:
        ref, hib = u["ref"], u.get("hib")
        dirs, header_dirs = unit_arrows(u, infos, cells_by_id)
        if len(dirs) > 1:
            rep.warn("sign_arrow", ref, "arrow_ambiguous", "both arrows printed with this metric")
        elif dirs:
            d = next(iter(dirs))
            if hib is None:
                rep.warn("sign_arrow", ref, "direction_null_with_arrow", f"arrow {d} printed, higher_is_better null (KA1 a)")
            elif hib != (d == "up"):
                rep.fail("sign_arrow", ref, "arrow_conflict", f"printed arrow {d} against higher_is_better {hib}")
            else:
                rep.ok("sign_arrow", ref, "pass", f"arrow {d}")
        header_routed = False
        if len(header_dirs) == 1 and not dirs:
            d = next(iter(header_dirs))
            if hib is not None and hib != (d == "up"):
                rep.warn("sign_header_arrow", ref, "header_arrow_conflict", f"header arrow {d} next to the leaf against higher_is_better {hib}")
                rep.emit("sign_route", ref, "header_arrow_conflict", "route", "EC: check the printed direction")
                header_routed = True
        if u["kind"] != "K":
            continue
        hit = metric_lookup(u.get("metric_printed", ""), lookup)
        ld = hit[1] if hit else None
        arrow, header_arrow = sign_inputs(dirs, header_dirs)
        _, source, routed = resolve_sign([hib], arrow, header_arrow, ld)
        if not routed:
            if source == "lookup" and hib is None:
                rep.emit("sign_lookup", ref, "null_resolved_by_lookup", "info", f"lookup {hit[0]} {ld}")
            continue
        if header_arrow is not None and not header_routed and ld is not None and ld != header_arrow:
            rep.emit("sign_route", ref, "header_arrow_conflict", "route", f"header arrow against the lookup direction {ld}")
        if ld is None:
            rep.emit("sign_route", ref, "sign_extractor_only", "route",
                     "metric unmapped" if hit is None else f"lookup {hit[0]} has no direction")
        elif hib is not None and hib != ld:
            rep.emit("sign_route", ref, "sign_lookup_conflict", "route", f"higher_is_better {hib}, lookup {hit[0]} {ld}")
    by_key = {}
    for u in sign_units:
        if u["kind"] == "K":
            by_key.setdefault((u["group"], metric_key(u.get("metric_printed", ""), lookup)), []).append(u)
    for (g, mk), us in by_key.items():
        vals = {json.dumps(u.get("hib")) for u in us}
        if len(us) > 1 and len(vals) > 1:
            for u in us:
                rep.fail("sign_group", u["ref"], "sign_conflict_in_group", f"group {g}, metric key {mk}: higher_is_better differs")
        elif len(us) > 1:
            rep.ok("sign_group", "+".join(u["ref"] for u in us), "pass", f"group {g}, metric key {mk}")


# ------------------------------------------------------------------------------------------------ schema
def _json_type_ok(x, t):
    if t == "null":
        return x is None
    if t == "boolean":
        return isinstance(x, bool)
    if t == "integer":
        return (isinstance(x, int) and not isinstance(x, bool)) or (isinstance(x, float) and x.is_integer())
    if t == "number":
        return isinstance(x, (int, float)) and not isinstance(x, bool)
    if t == "string":
        return isinstance(x, str)
    if t == "array":
        return isinstance(x, list)
    if t == "object":
        return isinstance(x, dict)
    return False


def _json_eq(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(_json_eq(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_json_eq(a[k], b[k]) for k in a)
    return a == b


class MiniValidator:
    """Draft 2020-12 subset: every keyword used by extraction-schema-v0.5.json."""

    def __init__(self, schema):
        self.root = schema

    def _resolve(self, ref):
        if not ref.startswith("#/"):
            raise ValueError(f"unsupported $ref {ref}")
        node = self.root
        for part in ref[2:].split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
        return node

    def errors(self, inst, schema=None, path="$"):
        schema = self.root if schema is None else schema
        out = []
        if schema is True or schema == {}:
            return out
        if schema is False:
            return [(path, "false schema")]
        if "$ref" in schema:
            out += self.errors(inst, self._resolve(schema["$ref"]), path)
        if "type" in schema:
            ts = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
            if not any(_json_type_ok(inst, t) for t in ts):
                return out + [(path, f"type {ts}")]
        if "enum" in schema and not any(_json_eq(inst, e) for e in schema["enum"]):
            out.append((path, f"not in enum {schema['enum']}"))
        if "const" in schema and not _json_eq(inst, schema["const"]):
            out.append((path, f"not const {schema['const']!r}"))
        if isinstance(inst, str):
            if "pattern" in schema and not re.search(schema["pattern"], inst):
                out.append((path, f"does not match {schema['pattern']}"))
            if "minLength" in schema and len(inst) < schema["minLength"]:
                out.append((path, f"shorter than {schema['minLength']}"))
            if "maxLength" in schema and len(inst) > schema["maxLength"]:
                out.append((path, f"longer than {schema['maxLength']}"))
        if isinstance(inst, (int, float)) and not isinstance(inst, bool):
            if "minimum" in schema and inst < schema["minimum"]:
                out.append((path, f"below {schema['minimum']}"))
            if "maximum" in schema and inst > schema["maximum"]:
                out.append((path, f"above {schema['maximum']}"))
        if isinstance(inst, list):
            if "minItems" in schema and len(inst) < schema["minItems"]:
                out.append((path, f"fewer than {schema['minItems']} items"))
            if "maxItems" in schema and len(inst) > schema["maxItems"]:
                out.append((path, f"more than {schema['maxItems']} items"))
            if schema.get("uniqueItems"):
                for i in range(len(inst)):
                    if any(_json_eq(inst[i], inst[j]) for j in range(i)):
                        out.append((f"{path}[{i}]", "duplicate item"))
            if "items" in schema:
                for i, x in enumerate(inst):
                    out += self.errors(x, schema["items"], f"{path}[{i}]")
        if isinstance(inst, dict):
            for k in schema.get("required", []):
                if k not in inst:
                    out.append((path, f"missing required {k!r}"))
            props = schema.get("properties", {})
            for k, x in inst.items():
                if k in props:
                    out += self.errors(x, props[k], f"{path}.{k}")
                elif "additionalProperties" in schema:
                    ap = schema["additionalProperties"]
                    if ap is False:
                        out.append((f"{path}.{k}", "additional property"))
                    elif isinstance(ap, dict):
                        out += self.errors(x, ap, f"{path}.{k}")
            if "propertyNames" in schema:
                for k in inst:
                    out += [(f"{path}.{k}", "property name: " + m) for _, m in self.errors(k, schema["propertyNames"], path)]
            if "maxProperties" in schema and len(inst) > schema["maxProperties"]:
                out.append((path, f"more than {schema['maxProperties']} properties"))
        for sub in schema.get("allOf", []):
            out += self.errors(inst, sub, path)
        if "anyOf" in schema and not any(not self.errors(inst, sub, path) for sub in schema["anyOf"]):
            out.append((path, "matches no anyOf branch"))
        if "if" in schema:
            if not self.errors(inst, schema["if"], path):
                if "then" in schema:
                    out += self.errors(inst, schema["then"], path)
            elif "else" in schema:
                out += self.errors(inst, schema["else"], path)
        return out


def schema_errors(record, schema):
    """(engine, sorted list of (path, message))."""
    try:
        import jsonschema  # noqa: PLC0415
        v = jsonschema.Draft202012Validator(schema)
        errs = [("$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in e.absolute_path), e.message)
                for e in v.iter_errors(record)]
        from importlib.metadata import version  # noqa: PLC0415
        return f"jsonschema {version('jsonschema')}", sorted(errs)
    except Exception:  # noqa: BLE001 -- jsonschema absent or broken under -I: fall back to the built-in subset
        return "builtin", sorted(set(MiniValidator(schema).errors(record)))


# ------------------------------------------------------------------------------------------------ record adapter
def _lst(x):
    return x if isinstance(x, list) else []


def record_values(rec):
    """Value contexts (VALUE_KEYS) and sign units from H units and K units."""
    values, signs = [], []
    for hi, u in enumerate(_lst(rec.get("units_h"))):
        if not isinstance(u, dict):
            continue
        ref = u.get("unit_id", "?")
        er = u.get("evidence_ref") or ""
        bench = u.get("benchmark_printed")
        values.append({"ref": ref, "kind": "H", "group": ref,
                       "cell": er if er.startswith("C") else None, "prose": er if er.startswith("E") else None,
                       "col": u.get("col"), "value_printed": u.get("value_printed", ""),
                       "value_occurrence": u.get("value_occurrence"), "column_printed": u.get("column_printed"),
                       "origin": u.get("origin"), "figure_only": False,
                       "benchmark_printed": None if bench in (None, "not stated") else bench,
                       "metric_printed": u.get("metric_printed") or None,
                       "where": (u.get("loc") or {}).get("where")})
        signs.append({"ref": ref, "kind": "H", "index": hi, "group": ref, "metric_printed": u.get("metric_printed", ""),
                      "hib": u.get("higher_is_better"),
                      "values": [{"column_printed": u.get("column_printed"), "cell": values[-1]["cell"], "col": u.get("col")}]})
    groups = {g.get("group_id"): g for g in _lst(rec.get("groups")) if isinstance(g, dict)}
    for ki, u in enumerate(_lst(rec.get("units_k"))):
        if not isinstance(u, dict):
            continue
        g = groups.get(u.get("group_id"), {})
        arms = {a.get("arm_id"): a for a in _lst(g.get("arms")) if isinstance(a, dict)}
        svals = []
        for v in _lst(u.get("values")):
            if not isinstance(v, dict):
                continue
            arm = arms.get(v.get("arm_id"), {})
            values.append({"ref": f"{u.get('unit_id')}.{v.get('arm_id')}", "kind": "K", "group": u.get("group_id"),
                           "cell": v.get("cell"), "prose": v.get("prose"), "col": v.get("col"),
                           "value_printed": v.get("value_printed", ""), "value_occurrence": v.get("value_occurrence"),
                           "column_printed": v.get("column_printed"), "figure_only": bool(u.get("figure_only")),
                           "arm_label": arm.get("label_printed"), "orientation": g.get("orientation"),
                           "benchmark_printed": u.get("benchmark_printed"), "metric_printed": u.get("metric_printed"),
                           "condition_printed": u.get("condition_printed"),
                           "second_factor_printed": g.get("second_factor_printed"), "where": g.get("where")})
            svals.append({"column_printed": v.get("column_printed"), "cell": v.get("cell"), "col": v.get("col")})
        signs.append({"ref": u.get("unit_id", "?"), "kind": "K", "index": ki, "group": u.get("group_id"),
                      "orientation": g.get("orientation"), "metric_printed": u.get("metric_printed", ""),
                      "hib": u.get("higher_is_better"), "values": svals})
    return values, signs


def check_record_level(rec, text, infos, cells_by_id, rep):
    """Plan v0.2 s6.4 as changed by v0.3 s6.4: ids, references, anchors, F1, couplings, S06, S12, S14, QA n."""
    ids = {}
    for arr, key in (("evidence", "id"), ("cell_evidence", "id"), ("table_evidence", "id"),
                     ("units_h", "unit_id"), ("groups", "group_id"), ("units_k", "unit_id")):
        for x in _lst(rec.get(arr)):
            if isinstance(x, dict):
                i = x.get(key)
                if i in ids:
                    rep.fail("ids", str(i), "duplicate_id", f"in {arr} and {ids[i]}")
                ids[i] = arr
    prose_ids = {x.get("id") for x in _lst(rec.get("evidence")) if isinstance(x, dict)}
    cell_ids = set(cells_by_id)
    groups = {g.get("group_id"): g for g in _lst(rec.get("groups")) if isinstance(g, dict)}
    for g in groups.values():
        gid = g.get("group_id")
        arms = [a for a in _lst(g.get("arms")) if isinstance(a, dict)]
        aids = [a.get("arm_id") for a in arms]
        if len(set(aids)) != len(aids):
            rep.fail("ids", gid, "duplicate_arm_id")
        anchors = [a.get("arm_id") for a in arms if a.get("role") == "anchor"]
        if g.get("anchor_rule") == "none":
            if g.get("anchor_arm") is not None or anchors:
                rep.fail("anchor", gid, "anchor_with_rule_none", "anchor_rule none needs anchor_arm null and no anchor role")
            else:
                rep.ok("anchor", gid, "pass", "no anchor (rule none)")
        elif len(anchors) != 1 or g.get("anchor_arm") not in aids or anchors[0] != g.get("anchor_arm"):
            rep.fail("anchor", gid, "anchor_count", f"anchor_arm {g.get('anchor_arm')}, arms with role anchor {anchors}")
        else:
            rep.ok("anchor", gid, "pass")
        for r in _lst(g.get("evidence_refs")):
            if r not in prose_ids and r not in cell_ids:
                rep.fail("refs", gid, "evidence_missing", f"{r} not in evidence or cell_evidence")
    for u in _lst(rec.get("units_k")):
        if not isinstance(u, dict):
            continue
        g = groups.get(u.get("group_id"))
        if g is None:
            rep.fail("refs", u.get("unit_id", "?"), "group_missing", f"group {u.get('group_id')} not in groups")
            continue
        aids = {a.get("arm_id") for a in _lst(g.get("arms")) if isinstance(a, dict)}
        for v in _lst(u.get("values")):
            if isinstance(v, dict) and v.get("arm_id") not in aids:
                rep.fail("refs", f"{u.get('unit_id')}.{v.get('arm_id')}", "arm_missing", f"arm not in group {u.get('group_id')}")
    hs = [u for u in _lst(rec.get("units_h")) if isinstance(u, dict)]
    for u in hs:
        t = u.get("trace")
        if t and t not in cell_ids:
            rep.fail("refs", u.get("unit_id", "?"), "trace_missing", f"trace {t} not in cell_evidence")
    claims = rec.get("claims") if isinstance(rec.get("claims"), dict) else {}
    for cl in _lst(claims.get("list")):
        if isinstance(cl, dict):
            for t in _lst(cl.get("trace")):
                if t not in prose_ids and t not in cell_ids:
                    rep.fail("refs", cl.get("claim_id", "?"), "trace_missing", f"trace {t} not found")
    census = rec.get("census") if isinstance(rec.get("census"), dict) else None
    study = rec.get("study") if isinstance(rec.get("study"), dict) else None
    if census:
        st = census.get("F1_status")
        f1 = [u for u in hs if u.get("is_F1")]
        if st in ("number", "figure-only", "unreadable"):
            if len(f1) != 1 or census.get("F1_unit") != f1[0].get("unit_id"):
                rep.fail("f1", "F1", "f1_unit", f"{len(f1)} H units with is_F1; F1_unit {census.get('F1_unit')}")
            else:
                rep.ok("f1", "F1", "pass")
        elif f1 or census.get("F1_unit") != "NA":
            rep.fail("f1", "F1", "f1_unit", f"F1_status {st} needs no is_F1 unit and F1_unit NA")
        else:
            rep.ok("f1", "F1", "pass")
        fields = ["F2_codes", "F3", "F4", "F5", "F6"] if st == "NA" else ["F3", "F4", "F5", "F6"] if st == "QL" else []
        bad = [k for k in fields if census.get(k) != "NA"]
        if bad:
            rep.fail("census_coupling", "F1", "coupling", f"F1_status {st} needs NA in {bad}")
        codes = census.get("F2_codes") or ""
        letters = [c for c in codes.split("+") if len(c) == 1 and c in F2_ORDER]
        if letters != sorted(letters, key=F2_ORDER.index) or len(set(letters)) != len(letters):
            rep.fail("f2_order", "F2", "f2_letter_order", f"{codes} not in order {F2_ORDER}")
        if study:
            want = f1[0].get("task_family") if f1 else ("NA" if st == "NA" else None)
            if want is not None and study.get("primary_task_family") != want:
                rep.fail("s06", "S06", "s06_mismatch", f"S06 {study.get('primary_task_family')} against {want}")
    if study:
        vl = study.get("venue_line_text")
        if isinstance(vl, str) and vl != "none":
            if passage_found(vl, text.full):
                rep.ok("s12", "S12", "pass")
            else:
                rep.fail("s12", "S12", "s12_not_found", "venue line not in the text")
        mc = study.get("main_comparison")
        if isinstance(mc, dict):
            _check_s14(text, mc, infos, rep)
        qa = rec.get("qa") if isinstance(rec.get("qa"), dict) else None
        if qa and mc is not None:
            want = "yes" if mc == "NA" else "no"
            for q in ("QA4", "QA5", "QA6"):
                n = ((qa.get(q) or {}).get("sub") or {}).get("n")
                if n != want:
                    rep.fail("qa_n", q, "qa_n_mismatch", f"{q} n {n}; S14 {'NA' if mc == 'NA' else 'given'} needs {want}")
    notes = rec.get("notes")
    if isinstance(notes, str) and not str(rec.get("extractor", "")).startswith("EC"):
        nw = len(notes.split())
        if nw > NOTES_MAX_WORDS:
            rep.warn("notes", "R05", "notes_too_long", f"{nw} words (max {NOTES_MAX_WORDS})")


def _check_s14(text, mc, infos, rep):
    page = text.page(mc.get("page"))
    if page is None:
        rep.fail("s14_row", "S14", "s14_row_not_found", f"page {mc.get('page')} not in the text")
        return
    info = next((i for i in infos.values() if i.entry.get("where") == mc.get("where")), None)
    for role in ("own_row", "baseline_row"):
        label = mc.get(role, "")
        seg = (0, len(page.lines))
        if info is not None:
            fake = {"page": mc.get("page"), "row_group": mc.get("row_group", ""), "row_label": label}
            sub = Report()
            _, s = _segment(text, info, fake, sub, "S14")
            if isinstance(s, tuple) and s and s[0] == "pre":
                s = s[1]
            seg = s or seg
        found = False
        nf = needle_forms(label)
        for f in FORMS:
            toks = page.rows[f]
            lo, hi = page.token_range("rows", f, seg[0], seg[1])
            for p in find_runs(toks, nf[f], lo, hi):
                if toks[p][2] or (p > 0 and value_like(toks[p - 1][0])):
                    found = True
                    break
            if found:
                break
        if found:
            rep.ok("s14_row", f"S14.{role}", "pass")
        else:
            rep.fail("s14_row", f"S14.{role}", "s14_row_not_found", f"{label!r} not at a row start on page {mc.get('page')}")


def validate_record(rec, text, schema, lookup=None):
    """All checks on one record. Returns (Report, schema engine)."""
    rep = Report(str(rec.get("id", "")) if isinstance(rec, dict) else "", str(rec.get("extractor", "")) if isinstance(rec, dict) else "")
    engine, errs = schema_errors(rec, schema)
    if errs:
        for path, msg in errs:
            rep.fail("schema", path, "schema_error", msg)
    else:
        rep.ok("schema", "$", "pass", engine)
    if not isinstance(rec, dict):
        return rep, engine
    tables = [t for t in _lst(rec.get("table_evidence")) if isinstance(t, dict)]
    cells = [c for c in _lst(rec.get("cell_evidence")) if isinstance(c, dict)]
    prose = [e for e in _lst(rec.get("evidence")) if isinstance(e, dict)]
    values, signs = record_values(rec)
    _, infos, cells_by_id = check_evidence(text, tables, cells, values, prose, rep)
    check_signs(signs, infos, cells_by_id, lookup if lookup is not None else load_metric_lookup(), rep)
    check_record_level(rec, text, infos, cells_by_id, rep)
    return rep, engine


# ------------------------------------------------------------------------------------------------ CLI
def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_record(path):
    raw = Path(path).read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        lines = [ln for ln in raw.splitlines() if ln.strip()]
        if len(lines) == 1:
            return json.loads(lines[0])
        raise


def report_lines(rep, engine, hashes):
    """The report of one record: its finding dicts, then the summary dict (CLI and tools/ex_validate_batch.py).
    hashes: record_sha256, text_sha256, schema_sha256 and metric_lookup_sha256 (None = built-in KA1(b) only)."""
    sev = {}
    for x in rep.items:
        sev[x["severity"]] = sev.get(x["severity"], 0) + 1
    summary = {"summary": True, "id": rep.rid, "extractor": rep.extractor, "tool_version": TOOL_VERSION,
               "status": "rejected" if rep.n_fail else "accepted", "checks": len(rep.items),
               "fail": sev.get("fail", 0), "warn": sev.get("warn", 0), "route": sev.get("route", 0),
               "schema_engine": engine, "record_sha256": hashes["record_sha256"], "text_sha256": hashes["text_sha256"],
               "schema_sha256": hashes["schema_sha256"], "quote_check_sha256": _sha256(QUOTE_CHECK_PATH),
               "metric_lookup_sha256": hashes.get("metric_lookup_sha256")}
    return list(rep.items) + [summary]


# ------------------------------------------------------------------------------------------------ self-test
# Built-in synthetic fixtures (invented labels and numbers; no paper text): the v0.2 s6.6 tests T01-T20 and T22 in
# the v0.3 entry shape, the v0.5 sign checks and the shared direction list. The pinned-text cases (the 35 of
# validator-tests.jsonl, T21) need the screened full texts and stay in tests/test_ex_validate.py.
_ST_CAPTION = "Table 2: Synthetic ablation of a toy masked diffusion model on a toy benchmark."
_ST_LINES = ["=== page 2 ===", "Some prose before the table describes the toy setting in a few words.", _ST_CAPTION,
             "Method", "QA", "QB", "QC", "Full model 71.5 72.0 70.9", "w/o token remasking 60.2 61.8 58.4",
             "w/o noise schedule 55.1 56.3 50.7", "w/o lr warmup 69.3 69.9 68.5",
             "The text continues after the table with more prose.", "=== page 3 ===", "A later page of prose."]
_ST_TABLE = {"id": "T01", "where": "Table 2", "page": 2, "orientation": "rows", "header": "Method QA QB QC",
             "header_levels": 1, "columns": ["QA", "QB", "QC"], "column_roles": ["metric"], "row_groups": [],
             "row_group_role": "none", "caption": _ST_CAPTION}
_ST_PROSE = ["=== page 1 ===", "In our runs the model reaches 45.21 accuracy on the test set after tuning.",
             "The gain is 7.56 points on split A and 7.56 points on split B of the benchmark.",
             "0.61 0.98 0.72 0.54 0.82 0.19", " ".join(f"word{i}" for i in range(41)) + "."]
_SIGN_LINES = ["=== page 1 ===", "Abstract. We study a synthetic masked diffusion model on two toy benchmarks in this note.",
               "Table 1: Synthetic results of two decoding variants on the toy benchmark.",
               "Variant", "Acc. ↑", "FID ↓", "Cohesion", "Base", "61.2", "12.5", "0.30", "Ours", "64.8", "10.1", "0.35",
               "The text continues after the table with more prose."]


def _st_cell(cid, label, cells, first_col=1, occurrence=None, page=2, table="T01"):
    return {"id": cid, "cond": "K01", "table": table, "page": page, "row_label": label, "row_group": "",
            "first_col": first_col, "cells": cells, "occurrence": occurrence}


def _st_val(ref, cid, col, value, column, **kw):
    d = {"ref": ref, "kind": kw.pop("kind", "H"), "group": kw.pop("group", ref), "cell": cid, "col": col,
         "value_printed": value, "column_printed": column}
    d.update(kw)
    return d


def _st_run(lines, tables, cells, values, prose=()):
    rep, _, _ = check_evidence(Text(lines), tables, cells, values, prose)
    return rep.items


def _st_find(items, check, ref=None):
    return [x["status"] for x in items if x["check"] == check and (ref is None or x["ref"] == ref)]


def _st_ok(items):
    return not any(x["severity"] == "fail" for x in items)


def _st_kunit(uid, col, metric, column, hib, vals=("61.2", "64.8")):
    def v(arm, val, cid):
        return {"arm_id": arm, "value_printed": val, "value_num": None, "cell": cid, "col": col, "prose": None,
                "value_occurrence": None, "variance": {"kind": "none", "value_printed": "", "n_runs": None},
                "column_printed": column}
    return {"unit_id": uid, "group_id": "G01", "benchmark_printed": "toy", "metric_printed": metric,
            "condition_printed": "", "metric_kind": "generated-sample", "higher_is_better": hib, "scale": "raw",
            "split": "test", "task_family": "other", "n_eval_printed": "not_stated", "figure_only": False,
            "values": [v("A1", vals[0], "C01"), v("A2", vals[1], "C02")],
            "matched": None, "metric_id": None, "benchmark_id": None, "duplicate": None}


def _st_arm(aid, label, role):
    return {"arm_id": aid, "label_printed": label, "role": role, "generator": "diffusion", "level_printed": label,
            "level_num": None, "params_printed": "", "train_tokens_printed": "", "shots_printed": "",
            "scoring": "generated", "number_source": "run-by-authors", "steps_printed": "", "gen_length_printed": "",
            "ar_label_source": "NA"}


def _st_sign_record(units, columns=("Acc. ↑", "FID ↓", "Cohesion")):
    return {
        "id": "S00001", "form_version": "0.5", "extractor": "EA-test-model", "ft": "pymupdf-v1", "blocks": ["K"],
        "meta": None, "study": None, "design": None, "census": None, "claims": None, "qa": None, "units_h": [],
        "groups": [{"group_id": "G01", "rq_class": None, "factor_type": "order-rule", "factor_printed": "decoding variant",
                    "dose_unit": "NA", "where": "Table 1", "page": 1, "source_kind": "main-table", "orientation": "rows",
                    "second_factor_printed": "", "anchor_arm": "A2", "anchor_rule": "focal-label",
                    "arms": [_st_arm("A1", "Base", "comparison"), _st_arm("A2", "Ours", "anchor")],
                    "credited_ablation": True, "held_fixed": "not stated", "other_changes": "",
                    "budget_across_arms": "not reported", "shape": "NA", "evidence_refs": ["C01"], "duplicate": None}],
        "units_k": units, "evidence": [],
        "table_evidence": [{"id": "T01", "where": "Table 1", "page": 1, "orientation": "rows",
                            "header": "Variant Acc. ↑ FID ↓ Cohesion", "header_levels": 1, "columns": list(columns),
                            "column_roles": ["metric"], "row_groups": [], "row_group_role": "none",
                            "caption": "Table 1: Synthetic results of two decoding variants on the toy benchmark."}],
        "cell_evidence": [{"id": "C01", "cond": "K01", "table": "T01", "page": 1, "row_label": "Base", "row_group": "",
                           "first_col": 1, "cells": ["61.2", "12.5", "0.30"], "occurrence": None},
                          {"id": "C02", "cond": "K01", "table": "T01", "page": 1, "row_label": "Ours", "row_group": "",
                           "first_col": 1, "cells": ["64.8", "10.1", "0.35"], "occurrence": None}],
        "searched": {}, "doubt": [], "notes": ""}


def _st_csv_refused(text):
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "metric-ids-v1.csv"
        p.write_text(text, encoding="utf-8")
        try:
            load_metric_lookup(p)
        except ValueError:
            return True
    return False


def self_test(verbose=True):
    """Built-in fixtures; returns the number of failed checks (0 = all passed)."""
    import io  # noqa: PLC0415
    from contextlib import redirect_stdout  # noqa: PLC0415
    schema = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    L, T = _ST_LINES, [_ST_TABLE]
    WNS = _st_cell("C01", "w/o noise schedule", ["55.1", "56.3", "50.7"])
    FUL = _st_cell("C02", "Full model", ["71.5", "72.0", "70.9"])
    results = []

    def check(desc, fn):
        try:
            ok = bool(fn())
        except Exception as exc:  # noqa: BLE001 -- a crashing check is a failed check
            ok, desc = False, f"{desc} [{type(exc).__name__}: {exc}]"
        results.append(ok)
        if verbose:
            print(f"self-test {len(results):2d} {'ok  ' if ok else 'FAIL'} {desc}")

    def sign(units, columns=("Acc. ↑", "FID ↓", "Cohesion")):
        return validate_record(_st_sign_record(units, columns), Text(_SIGN_LINES), schema)[0].items

    def prose(eid, quote, loc="p.1, §4.2", cond="H01"):
        return {"id": eid, "cond": cond, "quote": quote, "loc": loc}

    def prose_items(entries, lines=_ST_PROSE):
        rep = Report()
        check_prose(Text(lines), entries, rep)
        return rep.items

    rows_vals = [_st_val("K01.A1", "C02", 1, "71.5", "QA", kind="K", group="G01", arm_label="Full model", orientation="rows"),
                 _st_val("K01.A2", "C01", 1, "55.1", "QA", kind="K", group="G01", arm_label="w/o noise schedule", orientation="rows")]
    check("T01 correct row passes", lambda: _st_find(_st_run(L, T, [WNS], []), "row") == ["pass"])
    check("T02 wrong label gives cells_mismatch",
          lambda: _st_find(_st_run(L, T, [dict(WNS, row_label="w/o token remasking")], []), "row") == ["cells_mismatch"])
    check("T03 label not at a row start gives row_not_found",
          lambda: _st_find(_st_run(L, T, [dict(WNS, row_label="noise schedule")], []), "row") == ["row_not_found"])
    check("T04 a table row as prose: negation_before; the 11-token passage from the first w/o row is found",
          lambda: _st_find(prose_items([prose("E01", "w/o noise schedule 55.1 56.3 50.7", "p.2, §5"),
                                        prose("E02", "w/o token remasking 60.2 61.8 58.4 w/o noise schedule 55.1 56.3 50.7",
                                              "p.2, §5")], L), "prose_quote") == ["negation_before", "found"])
    check("T05 value position: pass, value_mismatch, value_outside_cells",
          lambda: [_st_find(_st_run(L, T, [WNS], [_st_val("H01", "C01", c, "56.3", "QB")]), "value")[0] for c in (2, 3, 4)]
          == ["pass", "value_mismatch", "value_outside_cells"])
    check("T06 rows group passes with both columns verified",
          lambda: (lambda it: _st_ok(it) and _st_find(it, "column") == ["column_verified"] * 2)(_st_run(L, T, [FUL, WNS], rows_vals)))
    check("T07 arm cites another arm's row: label_row_mismatch",
          lambda: _st_find(_st_run(L, T, [WNS], [dict(rows_vals[0], cell="C01", value_printed="55.1")]), "label_row") == ["label_row_mismatch"])
    check("T08 wrong page gives row_not_found",
          lambda: _st_find(_st_run(L, T, [dict(WNS, page=3)], []), "row") == ["row_not_found"])
    check("T09 continuation entry (first_col 2) passes",
          lambda: (lambda it: _st_ok(it) and _st_find(it, "value") == ["pass"])(
              _st_run(L, T, [WNS, _st_cell("C03", "w/o noise schedule", ["56.3", "50.7"], first_col=2)],
                      [_st_val("H01", "C03", 2, "56.3", "QB")])))
    check("T10 header not printed: header_not_found",
          lambda: "header_not_found" in _st_find(_st_run(L, [dict(_ST_TABLE, header="Method QA QB QX")], [WNS], []), "table"))
    check("T11 (v0.3 shape) column_printed other than the map leaf: column_mismatch",
          lambda: _st_find(_st_run(L, T, [FUL, WNS], [dict(v, column_printed="QZ") for v in rows_vals]), "column")
          == ["column_mismatch"] * 2)
    check("T12 caption cut to four words: caption_length",
          lambda: "caption_length" in _st_find(_st_run(L, [dict(_ST_TABLE, caption="Table 2: Synthetic ablation")], [WNS], []), "table"))
    check("T13 two values of one group on one (cell, col): cell_reused",
          lambda: "cell_reused" in _st_find(_st_run(L, T, [WNS], [dict(rows_vals[1]), dict(rows_vals[1], ref="K02.A2")]), "reuse"))
    wide = (["=== page 1 ===", "Table 5: Synthetic seven-column ablation table used for the cell-kind test.",
             "Model", "A", "B", "C", "D", "E", "F", "G", "Ours", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0"]
            + [x for i in range(1, 7) for x in [f"w/o c{i}"] + [f"{i}.{k}" for k in range(1, 8)]])
    wide_t = {"id": "T01", "where": "Table 5", "page": 1, "orientation": "rows", "header_levels": 1,
              "header": "Model A B C D E F G", "columns": list("ABCDEFG"), "column_roles": ["metric"], "row_groups": [],
              "row_group_role": "none", "caption": "Table 5: Synthetic seven-column ablation table used for the cell-kind test."}
    check("T14 wide row as a cell passes; as prose it gives negation_before",
          lambda: _st_ok(_st_run(wide, [wide_t], [_st_cell("C01", "w/o c5", [f"5.{k}" for k in range(1, 8)], page=1)],
                                 [_st_val("H01", "C01", 3, "5.3", "C")]))
          and _st_find(prose_items([prose("E01", "w/o c5 5.1 5.2 5.3 5.4 5.5 5.6 5.7", "p.1, §4")], wide), "prose_quote") == ["negation_before"])
    twice = ["=== page 1 ===", "Table 9: Synthetic table with the identical row printed twice on one page.",
             "Model", "A", "B", "Ours", "1.0", "2.0", "Ours", "1.0", "2.0"]
    twice_t = {"id": "T01", "where": "Table 9", "page": 1, "orientation": "rows", "header_levels": 1, "header": "Model A B",
               "columns": ["A", "B"], "column_roles": ["metric"], "row_groups": [], "row_group_role": "none",
               "caption": "Table 9: Synthetic table with the identical row printed twice on one page."}
    check("T15 identical row twice: ambiguous_row; occurrence 2 passes",
          lambda: _st_find(_st_run(twice, [twice_t], [_st_cell("C01", "Ours", ["1.0", "2.0"], page=1)], []), "row") == ["ambiguous_row"]
          and _st_find(_st_run(twice, [twice_t], [_st_cell("C01", "Ours", ["1.0", "2.0"], occurrence=2, page=1)], []), "row") == ["pass"])
    check("T16 prose of 41 words: too_long",
          lambda: _st_find(prose_items([prose("E01", " ".join(f"word{i}" for i in range(41)))]), "prose_length") == ["too_long"])
    check("T17 numbers-only prose: numeric_only",
          lambda: _st_find(prose_items([prose("E01", "0.61 0.98 0.72 0.54 0.82 0.19")]), "prose_letters") == ["numeric_only"])
    e18 = prose("E01", "the model reaches 45.21 accuracy on the test set")
    check("T18 value not in the quote: value_not_in_quote",
          lambda: _st_find(_st_run(_ST_PROSE, [], [], [{"ref": "H01", "kind": "H", "group": "H01", "prose": "E01",
                                                         "value_printed": "45.2"}], [e18]), "value") == ["value_not_in_quote"])
    e19 = prose("E01", "The gain is 7.56 points on split A and 7.56 points on split B")
    v19 = {"ref": "H01", "kind": "H", "group": "H01", "prose": "E01", "value_printed": "7.56"}
    check("T19 value twice in the quote: value_ambiguous; value_occurrence 2 passes",
          lambda: _st_find(_st_run(_ST_PROSE, [], [], [v19], [e19]), "value") == ["value_ambiguous"]
          and _st_find(_st_run(_ST_PROSE, [], [], [dict(v19, value_occurrence=2)], [e19]), "value") == ["pass"])
    hy = ["=== page 1 ===", "Table 4: Synthetic table with a label split by line-end hyphenation here.",
          "Model", "A", "B", "Diffu-", "sion-LM 1.0 2.0"]
    hy_t = dict(twice_t, where="Table 4", caption="Table 4: Synthetic table with a label split by line-end hyphenation here.")
    check("T20 label split by line-end hyphenation passes",
          lambda: _st_find(_st_run(hy, [hy_t], [_st_cell("C01", "Diffusion-LM", ["1.0", "2.0"], page=1)], []), "row") == ["pass"])

    def t22():
        buf = io.StringIO()
        with redirect_stdout(buf):
            return qc.self_test() == 0
    check("T22 quote_check.py self-test passes unchanged (read-only import)", t22)
    # v0.5 sign checks (plan v0.5 s10.3) and the shared rules
    check("sign: printed arrow against higher_is_better is rejected (arrow_conflict)",
          lambda: _st_find(sign([_st_kunit("K01", 2, "FID", "FID ↓", True, ("12.5", "10.1"))]), "sign_arrow", "K01") == ["arrow_conflict"])
    check("sign: agreeing arrow passes and is not routed",
          lambda: (lambda it: _st_ok(it) and "sign_route" not in [x["check"] for x in it])(
              sign([_st_kunit("K01", 2, "FID", "FID ↓", False, ("12.5", "10.1"))])))
    check("sign: one group and metric key with two values is rejected",
          lambda: _st_find(sign([_st_kunit("K01", 1, "Acc.", "Acc. ↑", True), dict(_st_kunit("K02", 1, "acc", "Acc. ↑", None),
                                benchmark_printed="toy-2")]), "sign_group") == ["sign_conflict_in_group"] * 2)
    check("sign: unmapped metric and lookup conflict are routed to EC, not rejected",
          lambda: _st_find(sign([_st_kunit("K01", 3, "Cohesion", "Cohesion", True, ("0.30", "0.35"))]), "sign_route") == ["sign_extractor_only"]
          and "sign_lookup_conflict" in _st_find(sign([_st_kunit("K01", 3, "PPL", "Cohesion", True, ("0.30", "0.35"))]), "sign_route"))
    check("sign: header arrow against higher_is_better is routed (A20)",
          lambda: "header_arrow_conflict" in _st_find(sign([_st_kunit("K01", 2, "FID", "FID", True, ("12.5", "10.1"))],
                                                           ("Acc.", "FID", "Cohesion")), "sign_route"))
    check("sign: a null value resolved by the lookup is not routed (agreement R3)",
          lambda: (lambda it: "sign_route" not in [x["check"] for x in it] and _st_find(it, "sign_lookup") == ["null_resolved_by_lookup"])(
              sign([_st_kunit("K01", 2, "FID", "FID", None, ("12.5", "10.1"))], ("Acc.", "FID", "Cohesion"))))
    check("shared rules: record_arrows (no text) equals the arrows check_signs reads",
          lambda: record_arrows(_st_sign_record([_st_kunit("K01", 2, "FID", "FID", True, ("12.5", "10.1"))], ("Acc.", "FID", "Cohesion")))
          == {("K", 0): (set(), {"down"})})
    check("shared rules: resolve_sign order (arrow > lookup unless a value or header arrow conflicts > EC)",
          lambda: [resolve_sign([True], False, None, True)[1], resolve_sign([None], None, None, False)[1],
                   resolve_sign([True], None, None, False)[1], resolve_sign([False], None, True, False)[1],
                   resolve_sign([None], None, None, None, True, True)[1]] == ["KA1(a) printed arrow", "lookup", "pending EC", "pending EC", "EC"])
    lk = load_metric_lookup()
    check("KA1(b) lookup with qualifiers (Avg. acc, pass@1, FID with arrow, unlisted metric)",
          lambda: metric_lookup("Avg. acc", lk) == ("accuracy", True) and metric_lookup("pass@1", lk) == ("pass@k", True)
          and metric_lookup("FID ↓", lk) == ("fid", False) and metric_lookup("Cohesion index", lk) is None)
    check("lookup CSV refusals: comment row, yes/no direction, KA1(b) direction changed, one id two directions",
          lambda: _st_csv_refused("printed,id,higher_is_better\n# draft,x,\n")
          and _st_csv_refused("printed,id,higher_is_better\nscore,score,yes\n")
          and _st_csv_refused("printed,id,higher_is_better\nFID,fid,true\n")
          and _st_csv_refused("printed,id,higher_is_better\nfoo,m1,true\nbar,m1,false\n")
          and _st_csv_refused("# comment first\nprinted,id,higher_is_better\n"))
    check("schema: the built-in sign record is valid (built-in engine)",
          lambda: MiniValidator(schema).errors(_st_sign_record([_st_kunit("K01", 1, "Acc.", "Acc. ↑", True)])) == [])
    n_fail = results.count(False)
    if verbose:
        print(f"self-tests passed {len(results) - n_fail}/{len(results)}")
    return n_fail


def main(argv=None):
    ap = argparse.ArgumentParser(description="Extraction evidence validator (form v0.5).")
    ap.add_argument("--record", help="one extraction record (JSON object)")
    ap.add_argument("--text", help="the screened full text of that record")
    ap.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    ap.add_argument("--metric-lookup", help="CSV with columns printed,id,higher_is_better (default: KA1(b) list)")
    ap.add_argument("--out", help="also write the report lines to this file")
    ap.add_argument("--self-test", action="store_true", help="run the built-in fixtures; exit 0 if all pass, else 1")
    a = ap.parse_args(argv)
    if a.self_test:
        return 1 if self_test() else 0
    if not (a.record and a.text):
        ap.error("--record and --text are required (or --self-test)")
    try:
        rec = _load_record(a.record)
        schema = json.loads(Path(a.schema).read_text(encoding="utf-8"))
        text = Text.from_file(a.text)
        lookup = load_metric_lookup(a.metric_lookup)
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"summary": True, "status": "error", "detail": f"{type(exc).__name__}: {exc}"}, ensure_ascii=True))
        return 2
    rep, engine = validate_record(rec, text, schema, lookup)
    items = report_lines(rep, engine, {"record_sha256": _sha256(a.record), "text_sha256": _sha256(a.text),
                                       "schema_sha256": _sha256(a.schema),
                                       "metric_lookup_sha256": _sha256(a.metric_lookup) if a.metric_lookup else None})
    lines = [json.dumps(x, ensure_ascii=True) for x in items]
    print("\n".join(lines))
    if a.out:
        Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 1 if rep.n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
