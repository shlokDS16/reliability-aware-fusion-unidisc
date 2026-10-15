"""Logged searches on the free sources for the review (protocol section 3), plus snowballing.

    python tools/search_sources.py arxiv-exact          # arXiv, protocol strings S1 and S2 verbatim (ti OR abs)
    python tools/search_sources.py s2 [S1 S2]           # Semantic Scholar Graph API, bulk search
    python tools/search_sources.py oa [S1 S2]           # OpenAlex works, title_and_abstract.search (credit-limited)
    python tools/search_sources.py orv [S1 S2]          # OpenReview API v2 /notes/search, ICLR/NeurIPS/ICML/TMLR
    python tools/search_sources.py acl                  # ACL Anthology metadata export, strings applied locally
    python tools/search_sources.py snowball backward|forward [--resume FILE]

Revised strings (D0026, protocol section 10 amendment of 2026-10-15): the same commands accept S1p and S2p
(logged as S1' and S2'); each is run part by part (arXiv, Semantic Scholar, OpenAlex), the union of the parts
being the string. `acl` applies all four strings to the snapshot of the ACL export already on disk
(`acl --refresh` downloads it again).

Every search appends one row to research/review/corpus/search-log.jsonl (same keys as the arXiv rows:
database, string, query, filters, executed_utc, hits_reported, records_retrieved, export, sha256; `export`
is a repository-relative path under research/sources/search-raw/). Raw responses are kept as JSON.
Records are normalised and deduplicated by tools/merge_new_records.py, not here.

The protocol strings S1 and S2 (protocol.md section 3) are held once below as phrase lists, rendered
into each source's syntax, and evaluated locally with `matches()` where a source has no boolean search.
Read "non-autoregressive AND diffusion" with AND binding tighter than OR (one OR-term).
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "research" / "review" / "corpus"
RAW = ROOT / "research" / "sources" / "search-raw"
LOG = CORPUS / "search-log.jsonl"
UA = "dlm-review-search/0.2 (systematic review; polite, rate-limited)"
DATE_FROM, DATE_TO = "2021-01-01", dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

# ---------------------------------------------------------------- protocol strings, held once
S1_PHRASES = ["diffusion language model*", "discrete diffusion", "masked diffusion", "absorbing diffusion",
              "absorbing state", "discrete flow matching", "diffusion LLM", "diffusion large language model*",
              "text diffusion"]
S1_NAR = ("non-autoregressive", "diffusion")            # the OR-term ("non-autoregressive" AND diffusion)
S1_AND = ["language", "text", "token*", "language model*"]
S2_A = ["unified multimodal", "unified understanding and generation", "understanding and generation", "any-to-any"]
S2_B = ["diffusion", "masked generative", "discrete flow", "flow matching"]
S2_C = ["multimodal", "vision-language", "text-to-image"]

PROTOCOL_VERBATIM = {
    "S1": '("diffusion language model*" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR '
          '"absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model*" OR '
          '"text diffusion" OR "non-autoregressive" AND diffusion) AND (language OR text OR token* OR "language model*")',
    "S2": '("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR '
          '"any-to-any") AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND '
          '(multimodal OR "vision-language" OR "text-to-image")',
}


def words(p: str) -> list[str]:
    return re.findall(r"[a-z0-9*]+", p.lower())


def phrase_in(tokens: list[str], p: str) -> bool:
    w = words(p)
    n = len(w)
    for i in range(len(tokens) - n + 1):
        if all(tokens[i + j].startswith(x[:-1]) if x.endswith("*") else tokens[i + j] == x for j, x in enumerate(w)):
            return True
    return False



# ---------------------------------------------------------------- revised strings S1' and S2' (D0026)
# Nested specification: a phrase (str; trailing * = word-prefix wildcard) or ("OR"|"AND"|"NOT", [children]).
# ("NOT", [x, y]) means NOT (x OR y) and is only used as a child of an AND. Derived from the 540 seed
# abstracts and checked in three rounds (research/review/corpus/string-revision-2026-10-15.json).
_OR = lambda *a: ("OR", list(a))
_AND = lambda *a: ("AND", list(a))
_NOT = lambda *a: ("NOT", list(a))
P_BIO = _OR("protein*", "molecul*", "antibod*", "peptide*", "rna", "dna", "drug*", "crystal*", "chemi*", "genom*",
            "biolog*", "graph generation", "traveling salesman", "recommend*")
P_VIS = _OR("image*", "video*", "3d", "audio", "visual*", "pixel*", "photo*", "segmentation")
P_CTX = _OR("language", "text", "token*", "language model*")
P_CTX4 = _OR("language", "text", "token*", "language model*", "llm*", "vocabulary", "autoregressive", "reasoning")
P_LM = _OR("language model*", "llm*")
A2_DD = _OR("discrete diffusion", "masked diffusion", "discrete flow*", "discrete state-space*")
A2_WITH_CONTEXT = _AND(A2_DD, P_CTX4)                      # discrete / masked diffusion or flow with a language word
A2_NO_CONTEXT = _AND(A2_DD, _NOT(P_BIO), _NOT(P_VIS))      # the same without a language word, outside biochemical and visual contexts
S1P_PARTS = {
    # A1: names of diffusion language models (no context clause needed)
    "A1": _OR("diffusion language model*", "language diffusion model*", "diffusion llm*", "diffusion lm*", "dllm", "dllms",
              "diffusion-based language model*", "diffusion-based llm*", "diffusion large language model*",
              "diffusion-based large language model*", "text diffusion", "block diffusion", "absorbing diffusion",
              "diffusion mllm*", "diffusion vlm*", "diffusion vision-language model*", "dmllm", "dmllms", "dvlm", "dvlms"),
    # A2: discrete-state-space diffusion and flow: a language context, or no biochemical and no visual context
    "A2": _OR(A2_WITH_CONTEXT, A2_NO_CONTEXT),
    # A3: the original absorbing-state and non-autoregressive terms, any-order generation
    "A3": _OR(_AND("absorbing state", P_CTX), _AND("any-order", P_CTX), "non-autoregressive language model*",
              _AND("non-autoregressive", "diffusion", _NOT(P_BIO))),
    # B: diffusion together with text-generation or NLP-task vocabulary
    "B": _AND("diffusion",
              _OR("text generation", "language generation", "natural language generation", "sequence-to-sequence",
                  "seq2seq", "discrete sequence*", "speculative decoding", "categorical data", "discrete data",
                  "paraphras*", "textual diffusion", "text modeling", "named entity", "sentiment", "summarization",
                  "dialog*", "dialogue", "machine translation", "text style", "commonsense", "topic model*",
                  "triple extraction", "information extraction"),
              _NOT(P_BIO)),
    # C: diffusion with a language model, outside biochemical and visual contexts
    "C": _AND("diffusion", P_LM, _NOT(P_BIO), _NOT(P_VIS)),
}
S2P_PARTS = {
    "M": _AND(_OR("unified multimodal", "unified multi-modal", "unified understanding and generation",
                  "understanding and generation", "any-to-any", "mixed-modal*", "mixed-modality"),
              _OR("diffusion", "masked generative", "discrete flow*", "flow matching", "rectified flow", "discrete denoising"),
              _OR("multimodal", "multi-modal", "vision-language", "text-to-image", "image generation", "mllm", "mllms",
                  "visual understanding", "image understanding")),
    "VLA": _AND(_OR("vision-language-action", "vla", "vlas"),
                _OR("discrete diffusion", "discrete denoising", "masked diffusion", "diffusion-based", "unified diffusion",
                    "diffusion language model*", "dllm", "dllms")),
}
P_SPECS = {"S1'": _OR(*S1P_PARTS.values()), "S2'": _OR(*S2P_PARTS.values())}
P_PARTS = {"S1'": S1P_PARTS, "S2'": S2P_PARTS}
P_ARG = {"S1": "S1", "S2": "S2", "S1p": "S1'", "S2p": "S2'"}


def ev_p(spec, t):
    if isinstance(spec, str):
        return phrase_in(t, spec)
    op, items = spec
    if op == "OR":
        return any(ev_p(i, t) for i in items)
    if op == "AND":
        return all(ev_p(i, t) for i in items)
    return not any(ev_p(i, t) for i in items)


def part_of(name: str, text: str):
    """Names of the parts of S1' / S2' that match the text (the tier of the match)."""
    t = re.findall(r"[a-z0-9]+", text.lower())
    return [k for k, sp in P_PARTS[name].items() if ev_p(sp, t)]


# OpenAlex stems words but has no wildcard: wildcard terms are expanded by hand where the stem differs
OA_EXPAND = {"molecul*": ["molecule", "molecular"], "antibod*": ["antibody"], "chemi*": ["chemical", "chemistry"],
             "genom*": ["genome", "genomic"], "biolog*": ["biology", "biological"],
             "recommend*": ["recommendation", "recommender"], "paraphras*": ["paraphrase", "paraphrasing"],
             "token*": ["token", "tokens", "tokenizer"], "visual*": ["visual", "visually"],
             "photo*": ["photo", "photograph"], "drug*": ["drug"], "crystal*": ["crystal"], "peptide*": ["peptide"],
             "protein*": ["protein"], "image*": ["image"], "video*": ["video"], "dialog*": ["dialog", "dialogue"],
             "sequence*": ["sequence"], "visual*": ["visual", "visualization"]}


def _alts(p: str, syntax: str):
    """Alternatives (OR-ed) that express one phrase in a syntax."""
    if syntax == "oa":
        return [q(x, False) for x in OA_EXPAND[p]] if p in OA_EXPAND else [q(p, False)]
    if syntax == "arxiv":
        if p.endswith("*") and " " not in p and "-" not in p:
            # arXiv stems plain terms but a wildcard term switches stemming off (abs:image* finds 11,800 records, abs:image 104,864,
            # and ANDNOT abs:image* removes almost nothing), so the stem forms are written out as for OpenAlex
            return [f"(ti:{x} OR abs:{x})" for x in (OA_EXPAND.get(p) or [p.rstrip("*")])]
        base = p.rstrip("*")
        out = []
        for b in [base] + ([base + "s"] if p.endswith("*") else []):
            out.append(f'(ti:"{b}" OR abs:"{b}")' if " " in b or "-" in b else f"(ti:{b} OR abs:{b})")
        return out
    return [q(p, True)]


def _terms(items, syntax):
    out = []
    for i in items:
        out += _alts(i, syntax) if isinstance(i, str) else _terms(i[1], syntax)
    return out


def render_spec(spec, syntax: str, top: bool = True) -> str:
    """syntax: plain (AND, OR, AND NOT), s2 (+, |, -), oa (AND, OR, AND NOT; no wildcards), arxiv (ti: / abs:, ANDNOT)."""
    orr, andd = (" | ", " + ") if syntax == "s2" else (" OR ", " AND ")
    if isinstance(spec, str):
        a = _alts(spec, syntax)
        return a[0] if len(a) == 1 else "(" + orr.join(a) + ")"
    op, items = spec
    if op == "OR":
        body = orr.join(render_spec(i, syntax, False) for i in items)
    else:
        pos = [i for i in items if not (isinstance(i, tuple) and i[0] == "NOT")]
        neg = [i for i in items if isinstance(i, tuple) and i[0] == "NOT"]
        body = andd.join(render_spec(i, syntax, False) for i in pos)
        for n in neg:
            terms = _terms(n[1], syntax)
            if syntax == "s2":
                body += " + " + " + ".join("-" + t for t in terms)
            elif syntax == "arxiv":
                body = f"({body}) ANDNOT (" + " OR ".join(terms) + ")"
            else:
                body += " AND NOT (" + " OR ".join(terms) + ")"
    return body if top else "(" + body + ")"


def render_part(name: str, part: str, syntax: str) -> str:
    return render_spec(P_PARTS[name][part], syntax)


def matches(name: str, text: str) -> bool:
    """Exact local evaluation of the protocol string on title + abstract (case-insensitive, word-based)."""
    t = re.findall(r"[a-z0-9]+", text.lower())
    if name in P_SPECS:
        return ev_p(P_SPECS[name], t)
    anyp = lambda ps: any(phrase_in(t, p) for p in ps)
    if name == "S1":
        a = anyp(S1_PHRASES) or (phrase_in(t, S1_NAR[0]) and phrase_in(t, S1_NAR[1]))
        return a and anyp(S1_AND)
    return anyp(S2_A) and anyp(S2_B) and anyp(S2_C)


def q(p: str, wild: bool = True) -> str:
    """Quote a phrase (or leave a single word bare) for the source's syntax; optionally drop the * wildcard."""
    if not wild:
        p = p.replace("*", "")
    return f'"{p}"' if " " in p or "-" in p else p


def render(name: str, syntax: str) -> str:
    """Adapted string for a source. syntax: s2 (| + ), oa (OR AND, no wildcards), plain (OR AND, as protocol)."""
    if syntax == "s2":
        orr, andd, wild = " | ", " + ", True
    elif syntax == "oa":
        orr, andd, wild = " OR ", " AND ", False
    else:
        orr, andd, wild = " OR ", " AND ", True
    nar = f'({q(S1_NAR[0])}{andd}{q(S1_NAR[1])})'
    if name == "S1":
        a = orr.join([q(p, wild) for p in S1_PHRASES] + [nar])
        return f'({a}){andd}({orr.join(q(p, wild) for p in S1_AND)})'
    j = lambda ps: orr.join(q(p, wild) for p in ps)
    return f'({j(S2_A)}){andd}({j(S2_B)}){andd}({j(S2_C)})'


# ---------------------------------------------------------------- plumbing
_last: dict[str, float] = {}


def http(url, gap, data=None, headers=None, tries=7, timeout=180):
    host = urllib.parse.urlparse(url).netloc
    for k in range(tries):
        w = gap - (time.time() - _last.get(host, 0))
        if w > 0:
            time.sleep(w)
        _last[host] = time.time()
        req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            body = e.read()
            if e.code == 429 and e.headers.get("X-RateLimit-Remaining") == "0":
                return e.code, body, dict(e.headers)            # daily quota exhausted (OpenAlex): waiting is pointless
            if e.code in (429, 500, 502, 503, 504):
                ra = e.headers.get("Retry-After")
                time.sleep(min(float(ra), 300) if ra and ra.replace(".", "").isdigit() else min(20 * 2 ** k, 300))
                continue
            return e.code, body, dict(e.headers)
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(min(10 * 2 ** k, 120))
    return None, b"", {}


def units(name):
    """(label, part) pairs to run for a string: S1 / S2 run as one query, S1' / S2' part by part (union = the string).
    A name with a part ("S1':A2") runs that part only."""
    base, _, part = name.partition(":")
    if part:
        return [(f"{base}:{part}", part)]
    return [(name, None)] if name in ("S1", "S2") else [(f"{name}:{k}", k) for k in P_PARTS[name]]


def fname(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", label.replace("'", "p")).strip("-")


def stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def save_raw(source: str, name: str, obj) -> Path:
    d = RAW / source
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    return p


def log(database, string, query, filters, executed, hits, got, path: Path):
    row = {"database": database, "string": string, "query": query, "filters": filters, "executed_utc": executed,
           "hits_reported": hits, "records_retrieved": got,
           "export": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"  logged {database} [{string}] hits {hits} retrieved {got} -> {row['export']}", flush=True)


# ---------------------------------------------------------------- arXiv, protocol strings verbatim
def arxiv_query(name: str, part=None) -> str:
    if part:
        cats = "(cat:cs.CL OR cat:cs.LG OR cat:cs.CV OR cat:cs.AI OR cat:stat.ML)"
        win = f"submittedDate:[{DATE_FROM.replace('-', '')}0000 TO {DATE_TO.replace('-', '')}2359]"
        return f"({render_part(name, part, 'arxiv')}) AND {cats} AND {win}"
    f = lambda p, wild=True: (f'(ti:"{p.replace("*", "")}" OR abs:"{p.replace("*", "")}")' if " " in p or "-" in p
                              else f'(ti:{p} OR abs:{p})')
    if name == "S1":
        ph = []
        for p in S1_PHRASES:
            if p.endswith("model*"):
                ph += [f(p.replace("*", "")), f(p.replace("*", "s"))]   # arXiv has no wildcard inside a phrase
            else:
                ph.append(f(p))
        ph.append(f'({f(S1_NAR[0])} AND {f(S1_NAR[1])})')
        c = " OR ".join([f("language"), f("text"), "(ti:token* OR abs:token*)", f("language model"), f("language models")])
        body = f'(({" OR ".join(ph)}) AND ({c}))'
    else:
        a = " OR ".join(f(p) for p in S2_A)
        b = " OR ".join(f(p) for p in S2_B)
        c = " OR ".join(f(p) for p in S2_C)
        body = f"(({a}) AND ({b}) AND ({c}))"
    cats = "(cat:cs.CL OR cat:cs.LG OR cat:cs.CV OR cat:cs.AI OR cat:stat.ML)"
    win = f"submittedDate:[{DATE_FROM.replace('-', '')}0000 TO {DATE_TO.replace('-', '')}2359]"
    return f"{body} AND {cats} AND {win}"


def cmd_arxiv_exact(names):
    ns = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/"}
    for name, label, part in [(n.split(":")[0], l, k) for n in names for l, k in units(n)]:
        qq, start, total, rows, ex = arxiv_query(name, part), 0, None, [], stamp()
        while total is None or start < total:
            url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
                {"search_query": qq, "start": start, "max_results": 200, "sortBy": "submittedDate", "sortOrder": "ascending"})
            st, raw, _ = http(url, 3.5)
            if st != 200 or b"<!ENTITY" in raw or b"<!DOCTYPE" in raw:
                print(f"  arXiv {label}: request failed at {start} (status {st})")
                break
            root = ET.fromstring(raw)
            total = int(root.findtext("o:totalResults", "0", ns))
            ents = root.findall("a:entry", ns)
            if not ents:
                break
            for e in ents:
                aid = re.sub(r"v\d+$", "", e.findtext("a:id", "", ns).rsplit("/", 1)[-1])
                rows.append({"arxiv": aid, "title": " ".join(e.findtext("a:title", "", ns).split()),
                             "published": e.findtext("a:published", "", ns)[:10],
                             "abstract": " ".join(e.findtext("a:summary", "", ns).split()), "string": label})
            start += len(ents)
            print(f"  arXiv {label}: {start}/{total}", flush=True)
        out = save_raw("arxiv", f"arxiv-protocol-{fname(label)}-{ex}.json", {"query": qq, "total": total, "records": rows})
        log("arXiv API (export.arxiv.org), " + ("protocol string verbatim" if not part else "revised string, part " + part), label, qq,
            "categories cs.CL cs.LG cs.CV cs.AI stat.ML and submittedDate window inside the query; ti OR abs per term; "
            "no wildcard inside phrases (model/models listed separately)", ex, total, len(rows), out)


# ---------------------------------------------------------------- Semantic Scholar bulk search
S2_FIELDS = "paperId,externalIds,title,abstract,year,publicationDate,venue,publicationTypes,citationCount"


def cmd_s2(names):
    for name, label, part in [(n.split(":")[0], l, k) for n in names for l, k in units(n)]:
        qq, ex, token, pages, total = (render_part(name, part, "s2") if part else render(name, "s2")), stamp(), None, [], None
        while True:
            p = {"query": qq, "fields": S2_FIELDS, "publicationDateOrYear": f"{DATE_FROM}:{DATE_TO}", "limit": 1000}
            if token:
                p["token"] = token
            for attempt in range(40):                       # the shared unauthenticated pool is often throttled: wait and retry the same page
                st, raw, _ = http("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(p), 4.0, tries=3)
                if st == 200 or st not in (None, 429):
                    break
                print(f"  S2 {label}: throttled (status {st}); waiting 90 s [{attempt + 1}/40]", flush=True)
                time.sleep(90)
            if st != 200:
                print(f"  S2 {label}: status {st}: {raw[:200]!r}")
                break
            d = json.loads(raw)
            total = d.get("total")
            pages.append(d.get("data", []))
            print(f"  S2 {label}: {sum(map(len, pages))}/{total}", flush=True)
            token = d.get("token")
            if not token:
                break
        recs = [r for pg in pages for r in pg]
        out = save_raw("semantic-scholar", f"s2bulk-{fname(label)}-{ex}.json",
                       {"endpoint": "/graph/v1/paper/search/bulk", "query": qq, "fields": S2_FIELDS, "total": total, "records": recs})
        log("Semantic Scholar Graph API (paper/search/bulk)", label, qq,
            f"publicationDateOrYear={DATE_FROM}:{DATE_TO}; title+abstract match (S2 field semantics); no language filter available; "
            "wildcard kept in quoted phrases as S2 documents prefix wildcard", ex, total, len(recs), out)


# ---------------------------------------------------------------- OpenAlex (credit-limited without a key)
OA_SELECT = ("id,doi,title,publication_date,publication_year,type,language,ids,primary_location,locations,"
             "abstract_inverted_index,cited_by_count")


def cmd_oa(names, max_pages=1000):
    import os
    key = os.environ.get("OPENALEX_API_KEY")
    for name, label, part in [(n.split(":")[0], l, k) for n in names for l, k in units(n)]:
        qq, ex, cursor, recs, count, done = (render_part(name, part, "oa") if part else render(name, "oa")), stamp(), "*", [], None, False
        flt = (f"title_and_abstract.search:{qq},from_publication_date:{DATE_FROM},to_publication_date:{DATE_TO},language:en")
        pageno = 0
        for _ in range(max_pages):
            pageno += 1
            p = {"filter": flt, "per-page": 200, "select": OA_SELECT}
            if key:
                p.update({"cursor": cursor, "api_key": key})
            else:                       # cursor paging needs a key; basic paging (page=) does not
                p["page"] = pageno
            url = "https://api.openalex.org/works?" + urllib.parse.urlencode(p, safe=':,()*"|')
            st, raw, hdr = http(url, 1.5, tries=2)
            if st != 200:
                print(f"  OA {label}: status {st}: {raw[:300]!r}; stopping (remaining credits "
                      f"{hdr.get('X-RateLimit-Remaining')})")
                break
            d = json.loads(raw)
            count = d["meta"]["count"]
            recs += d["results"]
            cursor = d["meta"].get("next_cursor") if key else (True if len(recs) < count else None)
            rem = int(hdr.get("X-RateLimit-Remaining", "0") or 0)
            print(f"  OA {label}: {len(recs)}/{count}, credits remaining {rem}", flush=True)
            if not cursor:
                done = True
                break
            if not key and rem < 20:
                print("  OA: stopping to keep a credit reserve (daily unauthenticated limit)")
                break
        out = save_raw("openalex", f"openalex-{fname(label)}-{ex}.json",
                       {"endpoint": "/works", "filter": flt, "count": count, "complete": done, "next_cursor": cursor,
                        "records": recs})
        log("OpenAlex works API (title_and_abstract.search)", label, flt,
            "from/to_publication_date window, language:en (drops works whose language is null); stemmed search, wildcards "
            "unsupported on this field so token* and model* are written without the star; "
            + ("COMPLETE" if done else "PARTIAL: stopped by the unauthenticated daily credit limit, resume with cursor in the raw file"),
            ex, count, len(recs), out)


# ---------------------------------------------------------------- OpenReview API v2 search
OR_GROUPS = ["ICLR.cc", "NeurIPS.cc", "ICML.cc", "TMLR"]


# search terms of the revised strings: the phrase lists of A1, A2, A3 and the text-generation terms of B and C as
# short phrases (the API is a term search; the full boolean string is applied locally to title, abstract and keywords)
OR_TERMS_P = {
    "S1'": ["diffusion language model", "language diffusion model", "diffusion llm", "diffusion lm", "dllm",
            "diffusion-based language model", "diffusion large language model", "text diffusion", "block diffusion",
            "absorbing diffusion", "diffusion mllm", "diffusion vision-language model", "dmllm", "discrete diffusion",
            "masked diffusion", "discrete flow", "discrete state-space", "any-order", "non-autoregressive language model",
            "diffusion text generation", "diffusion speculative decoding", "diffusion machine translation",
            "diffusion summarization", "diffusion dialogue", "diffusion paraphrase", "diffusion language generation",
            "diffusion large language model reasoning"],
    "S2'": ["unified multimodal", "unified multi-modal", "unified understanding and generation",
            "understanding and generation", "any-to-any", "mixed-modal", "vision-language-action diffusion",
            "multimodal discrete diffusion", "multimodal masked diffusion", "multimodal flow matching"],
}


def or_terms(name):
    if name in OR_TERMS_P:
        return [f'"{t}"' for t in OR_TERMS_P[name]]
    if name == "S1":
        return [f'"{p.replace("*", "")}"' for p in S1_PHRASES] + ['"non-autoregressive"']
    return [f'"{p}"' for p in S2_A]


def cmd_orv(names):
    for name in names:
        for term in or_terms(name):
            for grp in OR_GROUPS:
                ex, notes, count, off = stamp(), [], None, 0
                while True:
                    p = {"term": term, "source": "forum", "group": grp, "limit": 1000, "offset": off}
                    st, raw, _ = http("https://api2.openreview.net/notes/search?" + urllib.parse.urlencode(p), 1.5, tries=3)
                    if st != 200:
                        print(f"  OR {term} {grp}: status {st}: {raw[:200]!r}")
                        break
                    d = json.loads(raw)
                    count = d.get("count")
                    ns = d.get("notes", [])
                    notes += ns
                    off += len(ns)
                    if len(ns) < 1000 or off >= min(count or 0, 10000):
                        break
                out = save_raw("openreview", f"openreview-{name}-{re.sub('[^a-z]+', '_', term.lower()).strip('_')}-{grp.replace('.', '')}-{ex}.json",
                               {"endpoint": "/notes/search", "term": term, "group": grp, "count": count, "notes": notes})
                log("OpenReview API v2 (api2.openreview.net/notes/search)", f"{name}:{term}", f"term={term}&source=forum&group={grp}",
                    "group restricts to the venue family; date (cdate>=2021-01-01), the second clause of the string and the "
                    "phrase test are applied locally by tools/merge_new_records.py; result window capped at 10000 by the API",
                    ex, count, len(notes), out)


# ---------------------------------------------------------------- ACL Anthology metadata export
ACL_URL = "https://aclanthology.org/anthology+abstracts.bib.gz"


def clean_tex(s: str) -> str:
    s = re.sub(r"\\[`'^\"~=.uvHtcdbkr]\s*\{?([A-Za-z])\}?", r"\1", s)
    s = s.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_").replace("\\#", "#").replace("\\$", "$")
    s = re.sub(r"\\(?:textbf|textit|emph|texttt|mathrm|mathbf|mathcal)\s*", "", s)
    return " ".join(re.sub(r"[{}]", "", s).split())


def parse_bib(text: str):
    for ent in re.split(r"\n(?=@)", text):
        m = re.match(r"@(\w+)\{([^,\s]+),", ent)
        if not m or m.group(1).lower() == "proceedings":
            continue
        f = {}
        for k, v1, v2 in re.findall(r'\n\s*(\w+)\s*=\s*(?:"((?:[^"\\]|\\.)*)"|(\w+))\s*,?', ent, flags=re.S):
            f[k.lower()] = v1 or v2
        yield m.group(2), f


def cmd_acl(names=("S1", "S2"), refresh=True):
    ex = stamp()
    d = RAW / "acl-anthology"
    d.mkdir(parents=True, exist_ok=True)
    snaps = sorted(d.glob("anthology+abstracts-*.bib.gz"))
    if snaps and not refresh:
        gz = snaps[-1]                                   # same snapshot as the earlier run: strings compared on identical data
        raw = gz.read_bytes()
    else:
        st, raw, hdr = http(ACL_URL, 2.0, timeout=600)
        if st != 200:
            sys.exit(f"ACL Anthology export not retrieved: status {st}")
        gz = d / f"anthology+abstracts-{ex}.bib.gz"
        gz.write_bytes(raw)
    gz_sha = hashlib.sha256(raw).hexdigest()
    entries = list(parse_bib(gzip.decompress(raw).decode("utf-8", "replace")))
    print(f"  ACL: {len(raw)} bytes gz, {len(entries)} entries, sha256 {gz_sha[:12]}", flush=True)
    for name in names:
        hits = []
        for key, f in entries:
            try:
                yr = int(f.get("year", "0")[:4])
            except ValueError:
                yr = 0
            if yr < 2021:
                continue
            title, abstract = clean_tex(f.get("title", "")), clean_tex(f.get("abstract", ""))
            if matches(name, title + " " + abstract):
                url = f.get("url", "")
                hits.append({"bibkey": key, "acl_id": url.rstrip("/").rsplit("/", 1)[-1] if "aclanthology.org" in url else None,
                             "title": title, "abstract": abstract, "year": yr, "month": f.get("month"), "doi": f.get("doi"),
                             "url": url, "booktitle": clean_tex(f.get("booktitle", "") or f.get("journal", ""))})
        out = save_raw("acl-anthology", f"acl-matches-{fname(name)}-{ex}.json",
                       {"source_file": gz.name, "source_url": ACL_URL, "source_sha256": gz_sha, "entries_in_file": len(entries),
                        "query_evaluated_locally": render_spec(P_SPECS[name], "plain") if name in P_SPECS else render(name, "plain"),
                       "records": hits})
        log("ACL Anthology (metadata export anthology+abstracts.bib.gz, string applied locally)", name,
            render_spec(P_SPECS[name], "plain") if name in P_SPECS else render(name, "plain"),
            f"year>=2021 (month not in all entries, so the window is by year); title+abstract only (the export has no keywords); "
            f"word-based case-insensitive match of the protocol string; no language field in the export; source file {gz.name} sha256 {gz_sha}",
            ex, len(hits), len(hits), out)


# ---------------------------------------------------------------- snowballing (Semantic Scholar)
def seeds():
    ids = []
    for line in open(CORPUS / "awesome-dlms@194aa6bd.jsonl", encoding="utf8"):
        c = json.loads(line)["canonical_id"]
        if c.startswith("arXiv:"):
            ids.append(re.sub(r"v\d+$", "", c[6:]))
    return sorted(set(ids))


FWD_SKIP_ABOVE = 5000   # forward snowballing skipped for seeds with more citations than this (image-diffusion foundations)
NODE = "paperId,externalIds,title,abstract,year,publicationDate,venue"


def cmd_snowball(direction, resume=None):
    sd = seeds()
    cites = {}
    vf = CORPUS / "venues-semantic-scholar.json"
    if vf.exists():
        cites = {k: (v.get("citations") or 0) for k, v in json.load(open(vf))["records"].items()}
    ex = stamp()
    path = Path(resume) if resume else RAW / "semantic-scholar" / f"snowball-{direction}-{ex}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    if resume:
        ex = path.stem.rsplit("-", 1)[-1]
    done = set()
    if path.exists():
        done = {json.loads(l)["seed"] for l in open(path, encoding="utf8") if l.strip()}
    todo = [s for s in sd if s not in done]
    skipped = []
    with path.open("a", encoding="utf-8") as fh:
        if direction == "backward":
            for i in range(0, len(todo), 40):
                chunk = todo[i:i + 40]
                fields = "paperId,externalIds," + ",".join(f"references.{f}" for f in NODE.split(","))
                st, raw, _ = http("https://api.semanticscholar.org/graph/v1/paper/batch?fields=" + fields, 4.0,
                                  data=json.dumps({"ids": [f"ARXIV:{x}" for x in chunk]}).encode(),
                                  headers={"Content-Type": "application/json"})
                if st != 200:
                    print(f"  backward: status {st} at {i}: {raw[:200]!r}")
                    break
                for sid, p in zip(chunk, json.loads(raw)):
                    fh.write(json.dumps({"seed": sid, "found": p is not None,
                                         "references": (p or {}).get("references") or []}, ensure_ascii=False) + "\n")
                fh.flush()
                print(f"  backward: {i + len(chunk)}/{len(todo)}", flush=True)
        else:
            for n, s in enumerate(todo, 1):
                if cites.get(s, 0) > FWD_SKIP_ABOVE:
                    skipped.append(s)
                    fh.write(json.dumps({"seed": s, "skipped": f"S2 citation count {cites[s]} > {FWD_SKIP_ABOVE}", "citations": []}) + "\n")
                    continue
                off, cits, ok = 0, [], True
                while True:
                    st, raw, _ = http(f"https://api.semanticscholar.org/graph/v1/paper/ARXIV:{s}/citations?fields={NODE}&limit=500&offset={off}", 3.5)
                    if st == 404:
                        break
                    if st != 200:
                        print(f"  forward {s}: status {st}")
                        ok = False
                        break
                    d = json.loads(raw)
                    cits += [x["citingPaper"] for x in d.get("data", []) if x.get("citingPaper")]
                    if d.get("next") is None:
                        break
                    off = d["next"]
                if not ok:
                    break
                fh.write(json.dumps({"seed": s, "citations": cits}, ensure_ascii=False) + "\n")
                fh.flush()
                if n % 20 == 0:
                    print(f"  forward: {n}/{len(todo)} seeds", flush=True)
    rows = [json.loads(l) for l in open(path, encoding="utf8") if l.strip()]
    key = "references" if direction == "backward" else "citations"
    n_rec = sum(len(r[key]) for r in rows)
    complete = len(rows) == len(sd)
    log("Semantic Scholar Graph API (" + ("paper/batch references" if direction == "backward" else "paper/{id}/citations") + ")",
        f"snowball-{direction}", f"seed set = {len(sd)} arXiv IDs of Awesome-DLMs@194aa6bd; one level",
        f"{direction} citations; window and dedup applied later; "
        + (f"seeds with S2 citation count above {FWD_SKIP_ABOVE} skipped (listed in raw file)" if direction == "forward" else "all seeds")
        + ("; COMPLETE" if complete else f"; PARTIAL {len(rows)}/{len(sd)} seeds"),
        ex, n_rec, n_rec, path)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    names = [P_ARG[x.split(":")[0]] + (":" + x.split(":")[1] if ":" in x else "") for x in a[1:] if x.split(":")[0] in P_ARG] or ["S1", "S2"]
    if a[0] == "arxiv-exact":
        cmd_arxiv_exact(names)
    elif a[0] == "s2":
        cmd_s2(names)
    elif a[0] == "oa":
        cmd_oa(names)
    elif a[0] == "orv":
        cmd_orv(names)
    elif a[0] == "acl":
        cmd_acl([P_ARG[x] for x in a[1:] if x in P_ARG] or ["S1", "S2"], refresh="--refresh" in a)
    elif a[0] == "snowball":
        cmd_snowball(a[1], a[a.index("--resume") + 1] if "--resume" in a else None)
    else:
        sys.exit(__doc__)
