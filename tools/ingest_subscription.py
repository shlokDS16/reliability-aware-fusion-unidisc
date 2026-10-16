"""Re-runnable ingest of the subscription-database exports (decision D0031).

    python tools/ingest_subscription.py                      # every database folder that holds an export
    python tools/ingest_subscription.py --db scopus,wos      # only these databases
    python tools/ingest_subscription.py --no-fetch           # never go online (SpringerLink abstracts stay missing)
    python tools/ingest_subscription.py --no-log             # do not append rows to corpus/search-log.jsonl
    python tools/ingest_subscription.py --raw-root DIR --out-dir DIR --queue-out FILE --no-log   # fixtures / dry runs

Exports are read from research/sources/search-raw/<folder>/ (folders that hold no export are skipped):

  scopus/          *.csv                      Scopus CSV (citation, bibliographic, abstract and keywords)
  web-of-science/  *.txt *.ris *.tsv *.tab    Web of Science full record: plain text (tagged), tab-delimited or RIS
  ieee-xplore/     *.csv                      IEEE Xplore CSV
  acm-dl/          *.bib *.bibtex *.ris       ACM Digital Library BibTeX or RIS
  springerlink/    *.csv                      SpringerLink CSV (no abstracts: fetched by DOI, Crossref then Semantic Scholar, cached)
  sciencedirect/   *.ris                      ScienceDirect RIS

Query id of a file = token Q<n> / I<n> / union / S1p-A2-r2 ... in its file name (scopus-Q1-20261016.csv -> Q1).
Expected row counts are read from the <db>-queries-*.md note in the same folder when it has them.

Steps
  1. parse + sha256 every export file; normalise (title, abstract, authors, year, venue, DOI, arXiv id, source ids, source db, query id);
     strip publisher copyright footers from abstracts; flag proceedings front matter (Scopus "Conference review" volumes whose
     abstract lists the titles of the volume: not a paper, would match the strings by accident).
  2. deduplicate within and across databases (DOI, arXiv id, source id, exact normalised title, letters-and-digits title,
     token-set Jaccard >= 0.85 as in tools/resolve_title_only.py, abstract hash).
  3. deduplicate the unique records against the existing corpus: screening/records.jsonl (R), corpus/new-records-2026-10-15-v2.jsonl (M;
     labelled by where the record went: screening batches, rescue queue, other), screening/v2/title-resolved-queue.jsonl when it exists.
  4. S1, S2, S1', S2', S1'', S2'' locally on title + abstract; queue rule of D0027/D0028: a new record goes to subscription-queue
     if it passes S1''/S2'' or matches the original S1 or S2.
  5. outputs (all rewritten from the raw files on every run; record ids are kept stable through the previous records file):
       research/review/corpus/subscription-records-<date>.jsonl       every normalised record, dedup and string flags
       research/review/screening/v2/subscription-queue.jsonl          new records that pass (id, title, abstract: batch-0*.jsonl format)
       research/review/corpus/subscription-ingest-<date>.json         counts per database and query, PRISMA-ready
       research/review/corpus/search-log.jsonl                        one row appended per export file (never rewritten)
Screens nothing; changes no existing file except by appending to search-log.jsonl.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import html
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

_argv = sys.argv
sys.argv = _argv[:1]                       # merge_new_records reads sys.argv[1] as a date
sys.path.insert(0, str(Path(__file__).resolve().parent))
import merge_new_records as m              # noqa: E402
import merge_new_records_v2 as m2          # noqa: E402
import resolve_title_only as rto           # noqa: E402  (agree(), clean_title(): the title rules of D0029)
import search_sources as ss                # noqa: E402
import string_rounds as sr                 # noqa: E402  (Index: fast evaluation of the S1''/S2'' specs)
sys.argv = _argv

csv.field_size_limit(sys.maxsize)
ROOT, CORPUS, RAW = ss.ROOT, ss.CORPUS, ss.RAW
SCREEN = ROOT / "research" / "review" / "screening"
V2DIR = SCREEN / "v2"
JACC = 0.85
YEAR_GAP = 3                               # a title-only match is refused when both years are known and differ by more than this
STRINGS = ("S1", "S2", "S1'", "S2'", "S1''", "S2''")
CACHE_DIR = RAW / "_ingest-cache"
ABS_CACHE = CACHE_DIR / "doi-abstracts.jsonl"

TARGET_ORDER = ["records.jsonl", "v2 screening batches", "v2 rescue queue", "title-resolved queue", "v2 other (not queued)"]


# ================================================================== parsers: file -> raw dicts
def rawrec(**kw):
    d = {"title": "", "abstract": "", "authors": "", "year": "", "venue": "", "doi": "", "arxiv": None, "source_ids": {},
         "doc_type": "", "keywords_author": "", "keywords_index": "", "language": "", "volume": ""}
    d.update(kw)
    return d


def read_text(path: Path) -> str:
    b = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return b.decode(enc)
        except UnicodeError:
            continue
    return b.decode("utf-8", errors="replace")


def pick(row: dict, *names, default=""):
    low = {k.strip().lower(): v for k, v in row.items() if k}
    for n in names:
        v = low.get(n.lower())
        if v is not None and str(v).strip():
            return str(v).strip()
    return default


def csv_rows(path: Path):
    return list(csv.DictReader(io.StringIO(read_text(path), newline="")))


def parse_scopus(path):
    out = []
    for r in csv_rows(path):
        out.append(rawrec(title=pick(r, "Title"), abstract=pick(r, "Abstract"), authors=pick(r, "Authors"), year=pick(r, "Year"),
                          venue=pick(r, "Source title"), doi=pick(r, "DOI"), doc_type=pick(r, "Document Type"),
                          keywords_author=pick(r, "Author Keywords"), keywords_index=pick(r, "Index Keywords"),
                          language=pick(r, "Language of Original Document"), volume=pick(r, "Volume"),
                          source_ids={"scopus_eid": pick(r, "EID")} if pick(r, "EID") else {}))
    return out


def parse_ieee(path):
    out = []
    for r in csv_rows(path):
        out.append(rawrec(title=pick(r, "Document Title", "Title"), abstract=pick(r, "Abstract"), authors=pick(r, "Authors"),
                          year=pick(r, "Publication Year", "Year"), venue=pick(r, "Publication Title"), doi=pick(r, "DOI"),
                          doc_type=pick(r, "Document Identifier"), keywords_author=pick(r, "Author Keywords"),
                          keywords_index="; ".join(x for x in (pick(r, "IEEE Terms"), pick(r, "INSPEC Controlled Terms"),
                                                               pick(r, "INSPEC Non-Controlled Terms")) if x),
                          volume=pick(r, "Volume")))
    return out


def parse_springer(path):
    out = []
    for r in csv_rows(path):
        doi = pick(r, "Item DOI", "DOI")
        url = pick(r, "URL")
        if not doi:
            mm = re.search(r"10\.\d{4,9}/[^\s\"<>]+", url)
            doi = mm.group(0) if mm else ""
        out.append(rawrec(title=pick(r, "Item Title", "Title"), abstract=pick(r, "Abstract"), authors=pick(r, "Authors"),
                          year=pick(r, "Publication Year", "Year"), venue=pick(r, "Publication Title", "Book Series Title"),
                          doi=doi, doc_type=pick(r, "Content Type"), volume=pick(r, "Journal Volume")))
    return out


def parse_wos_tagged(text: str):
    """WoS plain text full record: two-letter tags, continuation lines start with three spaces, ER ends a record."""
    recs, cur, tag = [], None, None
    for line in text.splitlines():
        if not line.strip() or line.startswith(("FN", "VR", "EF")):
            continue
        if line.startswith("ER"):
            if cur is not None:
                recs.append(cur)
            cur, tag = None, None
            continue
        if line.startswith("   ") and cur is not None and tag:
            cur[tag].append(line.strip())
            continue
        mm = re.match(r"^([A-Z][A-Z0-9])(?: (.*))?$", line)
        if mm:
            tag = mm.group(1)
            if tag == "PT" and cur:
                recs.append(cur)
                cur = None
            if cur is None:
                cur = {}
            cur.setdefault(tag, []).append((mm.group(2) or "").strip())
    if cur:
        recs.append(cur)
    return recs


def wos_to_raw(get):
    return rawrec(title=get("TI"), abstract=get("AB"), authors=get("AF") or get("AU"), year=get("PY"), venue=get("SO"),
                  doi=get("DI"), doc_type=get("DT"), keywords_author=get("DE"), keywords_index=get("ID"), language=get("LA"),
                  volume=get("VL"), source_ids={"wos_ut": get("UT")} if get("UT") else {})


def parse_wos(path):
    text = read_text(path)
    head = text.lstrip()[:200]
    if head.startswith("TY  -"):
        return parse_ris(path)
    if head.startswith("PT\t") or re.match(r"^PT\t", head):
        rows = list(csv.reader(text.splitlines(), delimiter="\t", quoting=csv.QUOTE_NONE))
        hdr = rows[0]
        out = []
        for r in rows[1:]:
            if not any(r):
                continue
            d = dict(zip(hdr, r))
            out.append(wos_to_raw(lambda k: (d.get(k) or "").strip()))
        return out
    out = []
    for rec in parse_wos_tagged(text):
        multi = {"AU", "AF", "DE", "ID"}
        out.append(wos_to_raw(lambda k, rec=rec: ("; " if k in multi else " ").join(rec.get(k, [])).strip()))
    return out


# Web of Science RIS sometimes loses a line break, gluing the next tag onto the previous value ("...USAC3  - Stanford University",
# "...(CPCI-S)AN  - WOS:001213927502043"): split before any known tag that follows a non-space character.
RIS_TAGS = ("AN", "C3", "FU", "FX", "PU", "PI", "PA", "SN", "J9", "JI", "WE", "N1", "ER", "AD", "DO", "VL", "IS", "SP", "EP", "DA", "PY",
            "KW", "LA", "CP", "C6", "C7", "TY", "AU", "ED", "A1", "UT", "ID", "AB", "TI", "T2", "T1", "N2", "JO", "JF", "UR", "DB", "CY")
GLUE = re.compile(r"(?<=[^\s])(" + "|".join(RIS_TAGS) + r")  - ")


NL = chr(10)


def parse_ris_text(text: str):
    recs, cur = [], None
    lines = []
    for ln in text.splitlines():
        lines.extend(GLUE.sub(lambda mm: NL + mm.group(0), ln).split(NL))
    for line in lines:
        mm = re.match(r"^([A-Z][A-Z0-9])  ?- ?(.*)$", line)
        if not mm:
            if cur is not None and line.strip() and cur.get("_last"):
                cur[cur["_last"]][-1] += " " + line.strip()          # continuation line
            continue
        tag, val = mm.group(1), mm.group(2).strip()
        if tag == "TY":
            if cur:
                recs.append(cur)
            cur = {}
        if tag == "ER":
            if cur is not None:
                recs.append(cur)
            cur = None
            continue
        if cur is None:
            cur = {}
        cur.setdefault(tag, []).append(val)
        cur["_last"] = tag
    if cur:
        recs.append(cur)
    return recs


def ris_to_raw(rec: dict):
    g = lambda *tags: next((rec[t][0] for t in tags if rec.get(t)), "")
    allv = lambda *tags: "; ".join(v for t in tags for v in rec.get(t, []))
    doi = g("DO")
    if not doi:
        for t in ("UR", "L3", "M3", "N1", "ID"):
            for v in rec.get(t, []):
                mm = re.search(r"10\.\d{4,9}/[^\s\"<>]+", v)
                if mm:
                    doi = mm.group(0)
                    break
            if doi:
                break
    year = g("PY", "Y1", "DA")
    sid = {}
    if g("UT"):
        sid["wos_ut"] = g("UT")
    if g("AN"):
        sid["wos_ut" if g("AN").startswith("WOS:") else "accession"] = g("AN")
    return rawrec(title=g("TI", "T1"), abstract=g("AB", "N2"), authors=allv("AU", "A1"), year=(re.search(r"(19|20)\d\d", year) or [""])[0] if year else "",
                  venue=g("T2", "JF", "JO", "JA", "T3", "BT"), doi=doi, doc_type=g("TY"), keywords_author=allv("KW"),
                  volume=g("VL"), source_ids=sid)


def parse_ris(path):
    return [ris_to_raw(r) for r in parse_ris_text(read_text(path))]


def bib_entries(text: str):
    """Minimal brace-aware BibTeX reader -> list of {field: value}."""
    out, i, n = [], 0, len(text)
    while True:
        i = text.find("@", i)
        if i < 0:
            break
        mm = re.compile(r"@(\w+)\s*([{(])").match(text, i)
        if not mm:
            i += 1
            continue
        etype, opener = mm.group(1).lower(), mm.group(2)
        closer = "}" if opener == "{" else ")"
        j, depth = mm.end(), 1
        while j < n and depth:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        body = text[mm.end():j - 1]
        i = j
        if etype in ("comment", "string", "preamble"):
            continue
        key, _, rest = body.partition(",")
        fields, p = {"_type": etype, "_key": key.strip()}, 0
        while p < len(rest):
            fm = re.compile(r"\s*([A-Za-z][\w-]*)\s*=\s*").match(rest, p)
            if not fm:
                p += 1
                continue
            name, p = fm.group(1).lower(), fm.end()
            if p < len(rest) and rest[p] == "{":
                d, q = 1, p + 1
                while q < len(rest) and d:
                    d += (rest[q] == "{") - (rest[q] == "}")
                    q += 1
                val, p = rest[p + 1:q - 1], q
            elif p < len(rest) and rest[p] == '"':
                q = p + 1
                while q < len(rest) and not (rest[q] == '"' and rest[q - 1] != "\\"):
                    q += 1
                val, p = rest[p + 1:q], q + 1
            else:
                q = p
                while q < len(rest) and rest[q] not in ",\n":
                    q += 1
                val, p = rest[p:q].strip(), q
            fields[name] = " ".join(val.split())
        out.append(fields)
    return out


def parse_bib(path):
    out = []
    for e in bib_entries(read_text(path)):
        cl = ss.clean_tex
        out.append(rawrec(title=cl(e.get("title", "")), abstract=cl(e.get("abstract", "")), authors=cl(e.get("author", "")).replace(" and ", "; "),
                          year=e.get("year", ""), venue=cl(e.get("journal") or e.get("booktitle") or e.get("series") or ""),
                          doi=e.get("doi", ""), doc_type=e.get("_type", ""), keywords_author=cl(e.get("keywords", "")),
                          volume=e.get("volume", ""), source_ids={"bibkey": e["_key"]} if e.get("_key") else {}))
    return out


def parse_acm_jsonl(path):
    # in-page export of the result pages (acm-dl-results-*.jsonl): the abstract is the results-page snippet, often cut with "...";
    # such records are refetched by DOI in step 3 (TRUNCATED)
    out = []
    for line in read_text(path).splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        y = re.search(r"(19|20)\d\d", e.get("date") or "")
        out.append(rawrec(title=e.get("title", ""), abstract=e.get("abstract", ""), authors="; ".join(e.get("authors") or []),
                          year=y.group(0) if y else "", venue=e.get("venue", ""), doi=e.get("doi", ""), doc_type=e.get("type", ""),
                          source_ids={"acm_query": e.get("query"), "acm_rank": e.get("rank")}))
    return out


TRUNCATED = re.compile(r"(\.\.\.|…)\s*$")


def parse_acm(path):
    sfx = path.suffix.lower()
    return parse_bib(path) if sfx in (".bib", ".bibtex") else parse_acm_jsonl(path) if sfx == ".jsonl" else parse_ris(path)


DBS = [
    dict(key="scopus", folder="scopus", label="Scopus", exts={".csv"}, parser=parse_scopus, fetch=False,
         access="VIT institutional access, CSV export (citation, bibliographic, abstract and keywords)"),
    dict(key="wos", folder="web-of-science", label="Web of Science Core Collection", exts={".txt", ".ris", ".tsv", ".tab"},
         parser=parse_wos, fetch=False, access="VIT institutional access, full-record export"),
    dict(key="ieee", folder="ieee-xplore", label="IEEE Xplore", exts={".csv"}, parser=parse_ieee, fetch=False,
         access="VIT institutional access, CSV export"),
    dict(key="acm", folder="acm-dl", label="ACM Digital Library", exts={".bib", ".bibtex", ".ris", ".jsonl"}, parser=parse_acm, fetch=True,
         access="ACM DL open search (Basic Edition), results pages read in the tab (JSONL; snippet abstracts refetched by DOI), or BibTeX/RIS export"),
    dict(key="springer", folder="springerlink", label="SpringerLink", exts={".csv"}, parser=parse_springer, fetch=True,
         access="CSV export without abstracts (abstracts fetched by DOI)"),
    dict(key="sciencedirect", folder="sciencedirect", label="ScienceDirect", exts={".ris"}, parser=parse_ris, fetch=False,
         access="VIT institutional access, RIS export"),
]
DB_ORDER = {d["key"]: i for i, d in enumerate(DBS)}


# ================================================================== normalisation
def strip_markup(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", "", s)
    return " ".join(unicodedata.normalize("NFKC", s).split())


FOOT = re.compile(r"\s*(?:\u00a9|\ufffd(?=\s)|\(c\)(?=\s*(?:19|20)\d\d)|Copyright\b(?=\s*(?:\u00a9|\ufffd|(?:19|20)\d\d|held\b|by\b|\Z)))[^\u00a9]{0,250}$", re.I)
FOOT_WORDS = re.compile(r"(19|20)\d\d|authors?\b|elsevier|springer|ieee|acm\b|association|publishing|publisher|company|society|press\b|ltd|inc\b|foundation|"
                        r"rights reserved|licen[cs]e|owner|institute|university|wiley|taylor|sage|mdpi|nature", re.I)


def clean_abstract(a: str):
    """-> (abstract, flags). Placeholder abstracts are emptied; a trailing publisher copyright statement is removed."""
    a = strip_markup(a)
    flags = []
    if re.fullmatch(r"\[?\s*no abstract( available)?\s*\]?\.?", a, re.I):
        return "", ["placeholder-abstract"]
    mm = FOOT.search(a)
    if mm and len(a) - len(mm.group(0)) >= 40:
        g = mm.group(0).strip()
        # a copyright sign is always a footer; a replacement character (lost copyright sign) or the word Copyright needs footer words
        if g.startswith("©") or FOOT_WORDS.search(g) or re.fullmatch(r"copyright", g, re.I):
            a, flags = a[:mm.start()].rstrip(), ["copyright-footer-stripped"]
    a = re.sub(r"^abstract[\s:.\-]+", "", a, flags=re.I)
    return a, flags


def is_proceedings_volume(r: dict) -> bool:
    """Scopus 'Conference review' volume: no authors and an abstract of the form 'The proceedings contain N papers. ... The topics include: <titles>'."""
    return bool(re.match(r"\s*the proceedings contain\b", r["abstract"], re.I) and not r["authors"].strip())


def normalise(raw: dict, db: dict, fname: str, qid: str, rowno: int):
    ab, aflags = clean_abstract(raw["abstract"])
    doi = m.doi_norm(raw["doi"])
    if doi:
        doi = doi.rstrip(".,;)").strip() or None
    year = (re.search(r"(?:19|20)\d\d", raw["year"] or "") or [None])[0]
    r = {"db": db["key"], "file": fname, "query": qid, "row": rowno, "title": strip_markup(raw["title"]), "abstract": ab,
         "abstract_flags": aflags, "authors": " ".join((raw["authors"] or "").split()), "year": year,
         "venue": strip_markup(raw["venue"]) or None, "doi": doi, "arxiv": m.arxiv_ext({"DOI": doi}) if doi else None,
         "source_ids": {k: v for k, v in raw["source_ids"].items() if v}, "doc_type": raw["doc_type"],
         "keywords_author": raw["keywords_author"], "keywords_index": raw["keywords_index"], "volume": raw["volume"]}
    if not r["arxiv"]:
        r["arxiv"] = m2.embedded_arxiv(r["title"])
    r["proceedings_volume"] = is_proceedings_volume(r)
    return r


# ================================================================== helpers: hashes, file discovery, expected counts
def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


QID_RE = re.compile(r"(?<![A-Za-z0-9])(Q\d+|I\d+|union|S[12]p{0,2}(?:-(?!\d{8}\b)[A-Za-z0-9]+)*)(?![A-Za-z0-9])", re.I)


def query_id(fname: str) -> str:
    stem = Path(fname).stem
    mm = QID_RE.search(stem)
    if not mm:
        return "unspecified"
    q = mm.group(1)
    return q.upper() if re.fullmatch(r"[QIqi]\d+", q) else q.lower() if q.lower() == "union" else q


def discover(folder: Path, exts):
    return sorted(p for p in folder.glob("*")
                  if p.is_file() and p.suffix.lower() in exts and not p.name.lower().endswith(".meta.txt")
                  and not re.search(r"queries|expected-counts", p.name, re.I))


def notes_of(folder: Path):
    """Expected counts, labels and query texts from the <db>-queries-*.md note kept beside the exports (all optional)."""
    exp, label, qtext, notes = {}, {}, {}, []
    for md in sorted(folder.glob("*queries*.md")):
        lines = md.read_text(encoding="utf8", errors="replace").splitlines()
        notes.append(md.relative_to(ROOT).as_posix())
        for k, ln in enumerate(lines):
            mm = re.match(r"^\s*-?\s*Rows:\s*(.*)$", ln)
            if mm:
                for q, n in re.findall(r"\b([QI]\d+)\s+([\d,]+)", mm.group(1)):
                    exp[q] = int(n.replace(",", ""))
                continue
            mm = re.match(r"^\s*-?\s*(Q\d+)\b[^:]*:\s*([\d,]+)", ln) or re.match(r"^\s*(I\d+)\b.*?\bhits\s+([\d,]+)", ln)
            if mm and mm.group(1) not in exp:
                exp[mm.group(1)] = int(mm.group(2).replace(",", ""))
            mm = re.match(r"^\s*-?\s*Union[^:]*:\s*([\d,]+)", ln)
            if mm:
                exp["union"] = int(mm.group(1).replace(",", ""))
            for q, part in re.findall(r"\b(Q\d+)\s*=\s*(S[12]p-[A-Za-z0-9-]+)", ln):
                label[q] = part
            mm = re.match(r"^\s*(Q\d+|I\d+)\s*(?:\(([^)]*)\))?[^:\n]*:\s*$", ln) or re.match(r"^\s*(I\d+)\s*\((.*?)\)\s*:?\s*hits", ln)
            if mm:
                q = mm.group(1)
                if mm.group(2):
                    label.setdefault(q, mm.group(2))
                body = []
                for ln2 in lines[k + 1:k + 6]:
                    if ln2.strip().startswith("```"):
                        if body:
                            break
                        continue
                    if not ln2.strip():
                        if body:
                            break
                        continue
                    body.append(ln2.strip())
                    if not lines[k + 1].strip().startswith("```"):
                        break
                if body:
                    qtext.setdefault(q, " ".join(body))
    return exp, label, qtext, notes


Q1_NOTE = "union of S1, S2, S1' (A1, A2-r1, A3-r1..r3) and S2' (M, VLA), D0031 combined query"


def pretty_string(qid: str, note: str | None):
    if qid == "Q1":
        return f"Q1: {Q1_NOTE}"
    if note:
        mm = re.search(r"S([12])p-([A-Za-z0-9-]+)", note)
        if mm:
            return f"S{mm.group(1)}':{mm.group(2)}"
        return f"{qid}: {note}"
    mm = re.fullmatch(r"S([12])(p{0,2})(?:-([A-Za-z0-9-]+))?", qid, re.I)
    if mm:
        return f"S{mm.group(1)}{'' if not mm.group(2) else chr(39) * len(mm.group(2))}" + (f":{mm.group(3)}" if mm.group(3) else "")
    return qid


# ================================================================== abstract fetch by DOI (SpringerLink and any record without abstract when asked)
def load_abs_cache():
    c = {}
    if ABS_CACHE.exists():
        for ln in ABS_CACHE.read_text(encoding="utf8").splitlines():
            if ln.strip():
                d = json.loads(ln)
                c[d["doi"]] = d
    return c


def crossref_abstract(doi: str):
    st, body, _ = ss.http(f"https://api.crossref.org/works/{doi}", 1.0, tries=4, timeout=60)
    if st == 404:
        return "definitive", None
    if st != 200:
        return "transient", None
    try:
        a = json.loads(body).get("message", {}).get("abstract") or ""
    except ValueError:
        return "transient", None
    a = re.sub(r"</?jats:[^>]+>|<[^>]+>", " ", html.unescape(a))
    a = " ".join(a.split())
    a = re.sub(r"^abstract[\s:.\-]*", "", a, flags=re.I)
    return "definitive", (a if len(a) >= 40 else None)


def s2_abstract(doi: str):
    st, body, _ = ss.http(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract", 2.0, tries=4, timeout=60)
    if st == 404:
        return "definitive", None
    if st != 200:
        return "transient", None
    try:
        a = json.loads(body).get("abstract") or ""
    except ValueError:
        return "transient", None
    a = " ".join(a.split())
    return "definitive", (a if len(a) >= 40 else None)


def fetch_abstracts(dois, stats):
    """DOI -> (abstract, source) with a persistent cache; transient failures are not cached."""
    cache = load_abs_cache()
    res = {}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with ABS_CACHE.open("a", encoding="utf8") as fh:
        for doi in dois:
            if doi in cache:
                res[doi] = (cache[doi].get("abstract"), cache[doi].get("source"))
                stats["cache_hits"] += 1
                continue
            ab, src, ok = None, None, True
            for name, fn in (("crossref", crossref_abstract), ("semantic-scholar", s2_abstract)):
                state, a = fn(doi)
                stats[f"{name}_calls"] += 1
                if state == "transient":
                    ok = False
                if a:
                    ab, src = a, name
                    break
            if ab or ok:
                fh.write(json.dumps({"doi": doi, "abstract": ab, "source": src, "fetched_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")},
                                    ensure_ascii=False) + "\n")
                fh.flush()
            else:
                stats["transient_failures"] += 1
            res[doi] = (ab, src)
            stats["found" if ab else "not_found"] += 1
    return res


# ================================================================== dedup keys, clustering
def year_ok(a, b):
    try:
        return a is None or b is None or abs(int(str(a)[:4]) - int(str(b)[:4])) <= YEAR_GAP
    except ValueError:
        return True


def keys_of(r: dict):
    ks = []
    if r["proceedings_volume"]:
        for k, v in r["source_ids"].items():
            ks.append((k, v))
        if r["doi"]:
            ks.append(("doi", r["doi"]))
        ks.append(("pv", m.norm_title(r["title"]), r["year"], r["volume"], r["venue"]))
        return ks
    if r["doi"]:
        ks.append(("doi", r["doi"]))
    if r["arxiv"]:
        ks.append(("arxiv", r["arxiv"]))
    for k, v in r["source_ids"].items():
        ks.append((k, v))
    nt = m.norm_title(r["title"])
    if len(nt.split()) >= 3:
        ks.append(("t", nt))
    sq = rto.squash(r["title"])
    if len(sq) >= 25:
        ks.append(("sq", sq))
    na = m.norm_title(r["abstract"])
    if len(na) >= 200:
        ks.append(("a", hashlib.md5(na.encode()).hexdigest()))
    return ks


def cluster(rows):
    """Union-find on shared keys, then Jaccard merges (token-set >= 0.85 and same word order, years within YEAR_GAP). -> (groups, merge reasons)."""
    parent = list(range(len(rows)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    seen, reasons = {}, collections.Counter()
    for i, r in enumerate(rows):
        for k in keys_of(r):
            if k in seen:
                a, b = find(i), find(seen[k])
                if a != b:
                    # a title-only key never merges across a large year gap
                    if k[0] in ("t", "sq", "a") and not year_ok(rows[i]["year"], rows[seen[k]]["year"]):
                        reasons["refused-year-gap:" + k[0]] += 1
                        continue
                    parent[a] = b
                    reasons[k[0]] += 1
            else:
                seen[k] = i
    # Jaccard merges between the remaining roots
    inv = collections.defaultdict(set)
    ts = {}
    for i, r in enumerate(rows):
        if r["proceedings_volume"]:
            continue
        ts[i] = m.tset(r["title"])
        for w in ts[i]:
            inv[w].add(i)
    for i, t in ts.items():
        if len(t) < 3:
            continue
        cand = collections.Counter(j for w in t for j in inv[w] if j != i)
        for j, c in cand.most_common(30):
            if find(i) == find(j) or len(ts[j]) < 3:
                continue
            u = len(t | ts[j])
            if c / u < JACC:
                continue
            if len(t & ts[j]) / u >= JACC and rto.agree(rows[i]["title"], rows[j]["title"]) and year_ok(rows[i]["year"], rows[j]["year"]):
                parent[find(i)] = find(j)
                reasons["jaccard"] += 1
    groups = collections.defaultdict(list)
    for i in range(len(rows)):
        groups[find(i)].append(i)
    return sorted(groups.values(), key=lambda g: g[0]), reasons


def merge_cluster(rs):
    """One record from a group of raw rows (rows are in db / file order)."""
    best_abs = max(rs, key=lambda r: (len(r["abstract"]), -rs.index(r)))
    out = {"title": next((r["title"] for r in rs if r["abstract"]), rs[0]["title"]) or rs[0]["title"],
           "abstract": best_abs["abstract"], "abstract_source": best_abs["db"] if best_abs["abstract"] else None,
           "authors": next((r["authors"] for r in rs if r["authors"]), ""), "year": None, "venue": None, "doi": None, "arxiv": None,
           "source_ids": {}, "doc_type": [], "keywords_author": "", "keywords_index": "", "proceedings_volume": rs[0]["proceedings_volume"]}
    for r in rs:
        for k in ("year", "venue", "doi", "arxiv"):
            out[k] = out[k] or r[k]
        for k, v in r["source_ids"].items():
            out["source_ids"].setdefault(k, v)
        if r["doc_type"] and r["doc_type"] not in out["doc_type"]:
            out["doc_type"].append(r["doc_type"])
        out["keywords_author"] = out["keywords_author"] or r["keywords_author"]
        out["keywords_index"] = out["keywords_index"] or r["keywords_index"]
    seen_abs, out["abstract_variants"] = set(), []
    for r in rs:                                   # distinct abstracts of the group (string tests use all of them: recall-protective)
        k = m.norm_title(r["abstract"])
        if k and k not in seen_abs:
            seen_abs.add(k)
            out["abstract_variants"].append(r["abstract"])
    out["title_variants"] = list(dict.fromkeys(r["title"] for r in rs))
    out["doi_variants"] = list(dict.fromkeys(r["doi"] for r in rs if r["doi"]))
    out["abstract_flags"] = sorted({f for r in rs for f in r["abstract_flags"]})
    out["found_in"] = [{"db": r["db"], "query": r["query"], "file": r["file"], "row": r["row"]} for r in rs]
    out["dbs"] = sorted({r["db"] for r in rs}, key=DB_ORDER.get)
    out["queries"] = sorted({f"{r['db']}:{r['query']}" for r in rs})
    return out


# ================================================================== existing corpus (targets)
def jl(p: Path):
    return [json.loads(l) for l in p.open(encoding="utf8") if l.strip()]


def id_set(paths):
    s = set()
    for p in paths:
        s |= {json.loads(l)["id"] for l in p.open(encoding="utf8") if l.strip()}
    return s


class TargetIndex:
    """records.jsonl (R), the v2 file (M, labelled by where the record went) and the title-resolved queue when it exists."""

    def __init__(self):
        self.items = []                        # dicts: id, label, title, year, abstract, non_blocking
        self.ids = {"doi": collections.defaultdict(list), "arxiv": collections.defaultdict(list)}
        self.exact = collections.defaultdict(list)
        self.squash = collections.defaultdict(list)
        self.abs = collections.defaultdict(list)
        self.inv = collections.defaultdict(set)
        self.tsets = []
        self.stats = collections.Counter()
        existing = jl(SCREEN / "records.jsonl")
        venues = json.load(open(CORPUS / "venues-semantic-scholar.json"))["records"]
        for e in existing:
            doi = ((venues.get(e["arxiv"]) or {}).get("doi") if e.get("arxiv") else None)
            self._add(e["sid"], "records.jsonl", e["title"], (e.get("published") or "")[:4], e.get("abstract") or "", arxiv=e.get("arxiv"), doi=doi)
        batches = id_set(sorted(V2DIR.glob("batch-*.jsonl")))
        rescue = id_set(sorted((V2DIR / "rescue").glob("rescue-*.jsonl")))
        self.batches, self.rescue = batches, rescue
        for r in jl(CORPUS / "new-records-2026-10-15-v2.jsonl"):
            title_only = bool(r.get("snowball_only") and r.get("auto_excluded") and r.get("auto_excluded_abstract_missing"))
            label = ("v2 screening batches" if r["nid"] in batches else "v2 rescue queue" if r["nid"] in rescue else "v2 other (not queued)")
            self._add(r["nid"], label, r["title"], (r.get("published") or "")[:4], r.get("abstract") or "", arxiv=r.get("arxiv"), doi=r.get("doi"),
                      non_blocking=title_only, extra={"auto_excluded": r.get("auto_excluded"), "snowball_only": r.get("snowball_only")})
        tq = V2DIR / "title-resolved-queue.jsonl"
        self.title_resolved_present = tq.exists() and tq.stat().st_size > 0
        if self.title_resolved_present:
            for k, r in enumerate(jl(tq)):
                rid = r.get("id") or r.get("nid") or f"TR{k + 1:05d}"
                self._add(rid, "title-resolved queue", r.get("title") or r.get("resolved_title") or "", str(r.get("published") or r.get("year") or "")[:4],
                          r.get("abstract") or "", arxiv=r.get("arxiv"), doi=r.get("doi"))

    def _add(self, tid, label, title, year, abstract, arxiv=None, doi=None, non_blocking=False, extra=None):
        it = {"id": tid, "label": label, "title": title or "", "year": year or None, "has_abstract": bool(abstract), "non_blocking": non_blocking}
        if extra:
            it.update(extra)
        idx = len(self.items)
        self.items.append(it)
        self.stats[label] += 1
        if doi:
            self.ids["doi"][m.doi_norm(doi)].append(idx)
        if arxiv:
            self.ids["arxiv"][arxiv].append(idx)
        for tt in {title or "", rto.clean_title(title or "")}:
            nt = m.norm_title(tt)
            if len(nt.split()) >= 3:
                self.exact[nt].append(idx)
            sq = rto.squash(tt)
            if len(sq) >= 25:
                self.squash[sq].append(idx)
        na = m.norm_title(abstract)
        if len(na) >= 200:
            self.abs[hashlib.md5(na.encode()).hexdigest()].append(idx)
        ts = [m.tset(title or ""), m.tset(rto.clean_title(title or ""))]
        self.tsets.append(ts)
        for t in ts:
            for w in t:
                self.inv[w].add(idx)

    def matches(self, r):
        """All matches of a record -> list of (rank, kind, item, jaccard); rank orders id > exact > squashed > abstract > jaccard."""
        out, seen, rejected = [], set(), []

        def add(rank, kind, idxs, jac=None):
            for i in idxs:
                if i not in seen:
                    seen.add(i)
                    out.append((rank, kind, self.items[i], jac))

        def add_title(rank, kind, idxs):
            ok = [i for i in idxs if year_ok(r["year"], self.items[i]["year"])]
            rejected.extend((kind, self.items[i]["id"], self.items[i]["title"][:100], self.items[i]["year"]) for i in idxs if i not in ok and i not in seen)
            add(rank, kind, ok)

        if r["doi"]:
            add(6, "doi", self.ids["doi"].get(r["doi"], []))
        for ax in (r["arxiv"],):
            if ax:
                add(5, "arxiv", self.ids["arxiv"].get(ax, []))
        nt = m.norm_title(r["title"])
        if len(nt.split()) >= 3:
            add_title(4, "title-exact", self.exact.get(nt, []))
        sq = rto.squash(r["title"])
        if len(sq) >= 25:
            add_title(3, "title-letters-digits", self.squash.get(sq, []))
        na = m.norm_title(r["abstract"])
        if len(na) >= 200:
            add_title(2, "abstract", self.abs.get(hashlib.md5(na.encode()).hexdigest(), []))
        t = m.tset(r["title"])
        if len(t) >= 3:
            cand = collections.Counter(i for w in t for i in self.inv.get(w, ()))
            for i, c in cand.most_common(60):
                if i in seen:
                    continue
                best = 0.0
                for tt in self.tsets[i]:
                    if len(tt) >= 3:
                        best = max(best, len(t & tt) / len(t | tt))
                if best >= JACC and year_ok(r["year"], self.items[i]["year"]):
                    tit = self.items[i]["title"]
                    if rto.agree(r["title"], tit) or rto.agree(r["title"], rto.clean_title(tit)):
                        add(1, "title-jaccard", [i], round(best, 3))
                        continue
        return out, rejected


# ================================================================== string tests
def string_flags(rows_text: dict, keys_text: dict):
    """rows_text: id -> title + abstract; keys_text: id -> (title + abstract + author keywords, ... + index keywords).
    Returns id -> flags (S1, S2, S1', S2', S1'', S2'', parts). The queue rule uses title + abstract only (as for the free sources);
    the original strings S1 / S2 are also tested with the keywords, for information (the protocol's fields are title, abstract, keywords)."""
    toks = {k: sr.toks(v) for k, v in rows_text.items()}
    ix = sr.Index(toks)
    s1_parts = {k: ix.ev(sp) for k, sp in ss.S1PP_PARTS.items()}
    s2_parts = {k: ix.ev(sp) for k, sp in ss.S2PP_PARTS.items()}
    a2c = ix.ev(ss.S1PP_PARTS["A2"][1][0])
    out = {}
    for k, text in rows_text.items():
        p1 = [p for p in ss.S1PP_PARTS if k in s1_parts[p]]
        p2 = [p for p in ss.S2PP_PARTS if k in s2_parts[p]]
        sm = {s: ss.matches(s, text) for s in ("S1", "S2", "S1'", "S2'")}
        sm["S1''"], sm["S2''"] = bool(p1), bool(p2)
        smk = {"S1_author_keywords": ss.matches("S1", keys_text[k][0]), "S2_author_keywords": ss.matches("S2", keys_text[k][0]),
               "S1_all_keywords": ss.matches("S1", keys_text[k][1]), "S2_all_keywords": ss.matches("S2", keys_text[k][1])}
        if sm["S1"] or sm["S2"] or "A1" in p1 or p2:
            tier = 1
        elif "A3" in p1 or k in a2c:
            tier = 2
        elif "B" in p1 or "C" in p1:
            tier = 3
        else:
            tier = 4
        out[k] = {"string_match": sm, "s1pp_parts": p1, "s2pp_parts": p2, "tier": tier,
                  "string_match_with_keywords": smk}
    return out


# ================================================================== main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", help="comma-separated database keys: " + ",".join(d["key"] for d in DBS))
    ap.add_argument("--date", default="2026-10-15", help="date in the output file names (the search date)")
    ap.add_argument("--no-fetch", action="store_true", help="never go online (no abstract fetch by DOI)")
    ap.add_argument("--fetch-all-missing", action="store_true", help="also fetch missing abstracts by DOI for databases other than SpringerLink")
    ap.add_argument("--no-log", action="store_true", help="do not append rows to search-log.jsonl")
    ap.add_argument("--raw-root", default=str(RAW), help="folder that holds the database folders")
    ap.add_argument("--out-dir", default=str(CORPUS), help="folder for the records and summary files")
    ap.add_argument("--queue-out", default=str(V2DIR / "subscription-queue.jsonl"))
    args = ap.parse_args(_argv[1:])
    raw_root, out_dir, queue_path = Path(args.raw_root), Path(args.out_dir), Path(args.queue_out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rec_path = out_dir / f"subscription-records-{args.date}.jsonl"
    sum_path = out_dir / f"subscription-ingest-{args.date}.json"
    run_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    want = set(args.db.split(",")) if args.db else None
    warnings = []

    # ---- 1. parse
    files, rows = [], []
    for db in DBS:
        if want and db["key"] not in want:
            continue
        folder = raw_root / db["folder"]
        paths = discover(folder, db["exts"]) if folder.is_dir() else []
        if not paths:
            files.append({"db": db["key"], "status": "skipped: no export in " + db["folder"] + "/"})
            continue
        exp, labels, qtexts, note_files = notes_of(folder)
        hashes = {}
        for p in paths:
            h = sha256(p)
            fm = {"db": db["key"], "database": db["label"], "folder": db["folder"], "file": p.name,
                  "path": p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p), "sha256": h, "bytes": p.stat().st_size,
                  "mtime_utc": dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                  "query": query_id(p.name), "notes": note_files}
            if h in hashes:
                fm.update(status="skipped: byte-identical to " + hashes[h], rows=0)
                warnings.append(f"{p.name} is byte-identical to {hashes[h]}: skipped")
                files.append(fm)
                continue
            hashes[h] = p.name
            raw = db["parser"](p)
            fm.update(status="parsed", rows=len(raw), label=labels.get(fm["query"]), query_text=qtexts.get(fm["query"]),
                      access=db["access"])
            files.append(fm)
            for i, rr in enumerate(raw, 1):
                rows.append(normalise(rr, db, p.name, fm["query"], i))
        # expected counts: per query id (sum of the files of that query); a union export is checked against the db-wide "union" count
        by_q = collections.Counter()
        for fm in files:
            if fm.get("db") == db["key"] and fm.get("status") == "parsed":
                by_q[fm["query"]] += fm["rows"]
        total = sum(by_q.values())
        for fm in files:
            if fm.get("db") != db["key"] or fm.get("status") != "parsed":
                continue
            q = fm["query"]
            e = exp.get(q)
            scope = "query"
            if e is None and "union" in exp and (q in ("union", "unspecified") or all(k not in exp for k in by_q)):
                e, scope = exp["union"], "union (all files of the database)"
            fm["expected_rows"] = e
            fm["expected_scope"] = scope if e is not None else None
            got = by_q[q] if scope == "query" else total
            fm["rows_match_expected"] = None if e is None else (got == e)
            if e is not None and got != e:
                warnings.append(f"{db['key']} {q}: parsed {got} rows, expected {e} ({scope})")
    parsed_files = [f for f in files if f.get("status") == "parsed"]
    if not rows:
        print("no exports found under", raw_root, "; nothing to do")
        return
    print(f"parsed {len(rows)} rows from {len(parsed_files)} files", flush=True)

    # ---- 2. dedup within and across databases
    groups, reasons = cluster(rows)
    recs = []
    for g in groups:
        rec = merge_cluster([rows[i] for i in g])
        rec["_rows"] = g
        recs.append(rec)
    print(f"{len(recs)} unique records after within/across-database dedup ({dict(reasons)})", flush=True)

    # ---- 3. dedup against the existing corpus
    tg = TargetIndex()
    print("targets:", dict(tg.stats), "title-resolved queue present:", tg.title_resolved_present, flush=True)
    for rec in recs:
        rec["dup_matches"], rec["nonblocking_matches"], rec["rejected_year_gap"], rec["dup_primary"] = [], [], [], None
        if rec["proceedings_volume"]:
            continue
        found, rec["rejected_year_gap"] = tg.matches(rec)
        ms = sorted(found, key=lambda x: (-x[0], TARGET_ORDER.index(x[2]["label"])))
        for rank, kind, it, jac in ms:
            d = {"target": it["label"], "id": it["id"], "kind": kind, "target_title": it["title"][:160], "target_year": it["year"],
                 "target_has_abstract": it["has_abstract"]}
            if jac:
                d["jaccard"] = jac
            if "auto_excluded" in it:
                d["target_auto_excluded"] = it["auto_excluded"]
            (rec["nonblocking_matches"] if it["non_blocking"] else rec["dup_matches"]).append(d)
        rec["dup_primary"] = rec["dup_matches"][0] if rec["dup_matches"] else None

    # ---- abstracts by DOI for new records without one
    fetch_stats = collections.Counter()
    dbs_fetch = {d["key"] for d in DBS if d["fetch"]} | ({d["key"] for d in DBS} if args.fetch_all_missing else set())
    need = [r for r in recs if not r["proceedings_volume"] and not r["dup_primary"] and (not r["abstract"] or TRUNCATED.search(r["abstract"])) and r["doi"]
            and any(d in dbs_fetch for d in r["dbs"])]
    if need and not args.no_fetch:
        print(f"fetching abstracts for {len(need)} records by DOI", flush=True)
        got = fetch_abstracts(sorted({r["doi"] for r in need}), fetch_stats)
        for r in need:
            ab, src = got.get(r["doi"], (None, None))
            if ab:
                r["abstract"], r["abstract_source"] = clean_abstract(ab)[0], src
                r["abstract_variants"] = [r["abstract"]]
                r["abstract_flags"] = sorted(set(r["abstract_flags"]) | {"fetched-by-doi"})
    elif need:
        fetch_stats["skipped_no_fetch"] = len(need)

    # ---- 4. strings and queue rule
    live = [r for r in recs if not r["proceedings_volume"]]
    texts = {i: r["title"] + " " + " ".join(dict.fromkeys([r["abstract"]] + r["abstract_variants"])) for i, r in enumerate(live)}
    ktexts = {i: (texts[i] + " " + r["keywords_author"], texts[i] + " " + r["keywords_author"] + " " + r["keywords_index"]) for i, r in enumerate(live)}
    flags = string_flags(texts, ktexts)
    for i, r in enumerate(live):
        r.update(flags[i])
    for r in recs:
        if r["proceedings_volume"]:
            r["string_match"] = {s: None for s in STRINGS}
            r["s1pp_parts"], r["s2pp_parts"], r["tier"], r["string_match_with_keywords"] = [], [], None, None
            # would the volume abstract (a list of titles) have passed? informational only
            t = r["title"] + " " + r["abstract"]
            r["volume_abstract_matches_S1pp_S2pp"] = bool(ss.matches("S1''", t) or ss.matches("S2''", t))
        sm = r["string_match"]
        r["abstract_missing"] = not r["abstract"]
        if r["proceedings_volume"]:
            r["status"], r["queued"], r["queue_reason"] = "excluded: proceedings front matter (not a document)", False, None
        elif r["dup_primary"]:
            r["status"], r["queued"], r["queue_reason"] = "duplicate of " + r["dup_primary"]["target"], False, None
        elif sm["S1''"] or sm["S2''"] or sm["S1"] or sm["S2"]:
            r["status"], r["queued"] = "new, passes string filter", True
            r["queue_reason"] = ("database record; passes S1''/S2''" if (sm["S1''"] or sm["S2''"])
                                 else "database record; matches original S1/S2 (released, D0028)")
        else:
            r["status"], r["queued"], r["queue_reason"] = "new, fails S1''/S2'' (auto-excluded, D0027; rescue pass applies as for the free sources, D0029)", False, None
        # a duplicate whose target had no abstract and was never screened on content, while this record passes the strings
        r["dup_gains_abstract"] = bool(r["dup_primary"] and not r["dup_primary"]["target_has_abstract"] and r["abstract"]
                                       and (sm["S1''"] or sm["S2''"] or sm["S1"] or sm["S2"]))
        r["dup_target_auto_excluded_but_passes"] = bool(r["dup_primary"] and r["dup_primary"].get("target_auto_excluded")
                                                        and (sm["S1''"] or sm["S2''"]))

    # ---- stable ids through the previous records file
    prev = {}
    prev_run = None
    if rec_path.exists():
        for p in jl(rec_path):
            prev_run = prev_run or p.get("first_seen_run")
            for k in prev_keys(p):
                prev.setdefault(k, p)
    used, top = set(), max([int(p["id"][1:]) for p in prev.values()] + [0])
    for r in recs:
        old = next((prev[k] for k in rec_keys(r) if k in prev and prev[k]["id"] not in used), None)
        if old:
            r["id"], r["first_seen_run"] = old["id"], old["first_seen_run"]
        else:
            top += 1
            r["id"], r["first_seen_run"] = f"U{top:05d}", run_utc
        used.add(r["id"])
    recs.sort(key=lambda r: r["id"])

    # ---- 5. outputs
    def row_out(r):
        o = {"id": r["id"], "title": r["title"], "abstract": r["abstract"], "abstract_source": r["abstract_source"], "abstract_flags": r["abstract_flags"],
             "authors": r["authors"], "year": r["year"], "venue": r["venue"], "doi": r["doi"], "arxiv": r["arxiv"], "source_ids": r["source_ids"],
             "doc_type": r["doc_type"], "title_variants": r["title_variants"] if len(r["title_variants"]) > 1 else None,
             "doi_variants": r["doi_variants"] if len(r["doi_variants"]) > 1 else None, "dbs": r["dbs"], "queries": r["queries"], "found_in": r["found_in"],
             "keywords_author": r["keywords_author"], "keywords_index": r["keywords_index"], "proceedings_volume": r["proceedings_volume"],
             "abstract_missing": r["abstract_missing"], "status": r["status"], "duplicate_of": r["dup_matches"] or None,
             "matches_title_only_snowball_fragment": r["nonblocking_matches"] or None,
             "string_match": r["string_match"], "s1pp_parts": r["s1pp_parts"], "s2pp_parts": r["s2pp_parts"],
             "string_match_with_keywords": r["string_match_with_keywords"], "queue_tier_final": r["tier"] if r["queued"] else None,
             "queued": r["queued"], "queue_reason": r["queue_reason"], "dup_gains_abstract": r["dup_gains_abstract"],
             "dup_target_auto_excluded_but_passes": r["dup_target_auto_excluded_but_passes"], "first_seen_run": r["first_seen_run"]}
        if r["proceedings_volume"]:
            o["volume_abstract_matches_S1pp_S2pp"] = r["volume_abstract_matches_S1pp_S2pp"]
        return o

    with rec_path.open("w", encoding="utf8") as fh:
        for r in recs:
            fh.write(json.dumps(row_out(r), ensure_ascii=False) + "\n")
    queued = [r for r in recs if r["queued"]]
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("w", encoding="utf8") as fh:
        for r in queued:
            fh.write(json.dumps({"id": r["id"], "title": r["title"], "abstract": r["abstract"]}, ensure_ascii=False) + "\n")
    delta = [r for r in queued if r["first_seen_run"] == run_utc] if prev else []
    delta_path = None
    if prev and delta:
        delta_path = queue_path.with_name(f"subscription-queue-delta-{run_utc}.jsonl")
        with delta_path.open("w", encoding="utf8") as fh:
            for r in delta:
                fh.write(json.dumps({"id": r["id"], "title": r["title"], "abstract": r["abstract"]}, ensure_ascii=False) + "\n")

    # ---- counts per file (db, query) with first-sighting attribution
    rec_of_row = {}
    for r in recs:
        for i in r["_rows"]:
            rec_of_row[i] = r
    first_seen = {}          # record id -> (db, file) of first sighting in processing order
    cat_file = collections.defaultdict(collections.Counter)
    tgt_file = collections.defaultdict(collections.Counter)
    for i, row in enumerate(rows):
        r = rec_of_row[i]
        fk = (row["db"], row["file"])
        c = cat_file[fk]
        c["rows"] += 1
        if r["proceedings_volume"]:
            c["proceedings_front_matter"] += 1
            continue
        if r["id"] in first_seen:
            fdb, ffile = first_seen[r["id"]]
            c["dup_within_file" if (fdb, ffile) == fk else "dup_within_db" if fdb == row["db"] else "dup_across_db"] += 1
            continue
        first_seen[r["id"]] = fk
        if r["dup_primary"]:
            c["dup_existing"] += 1
            tgt_file[fk][r["dup_primary"]["target"]] += 1
            if r["dup_gains_abstract"]:
                c["dup_existing_gains_abstract_and_passes"] += 1
            if r["dup_target_auto_excluded_but_passes"]:
                c["dup_existing_target_auto_excluded_but_passes_S1pp_S2pp"] += 1
        else:
            c["new_unique"] += 1
            if r["queued"]:
                c["new_pass_strings"] += 1
                c["queued"] += 1
            else:
                c["new_fail_strings"] += 1
            if r["abstract_missing"]:
                c["new_abstract_missing"] += 1
            if r["nonblocking_matches"]:
                c["new_also_matches_title_only_snowball_fragment"] += 1
    CAT_KEYS = ["rows", "proceedings_front_matter", "dup_within_file", "dup_within_db", "dup_across_db", "dup_existing", "new_unique",
                "new_pass_strings", "new_fail_strings", "queued", "new_abstract_missing", "new_also_matches_title_only_snowball_fragment",
                "dup_existing_gains_abstract_and_passes", "dup_existing_target_auto_excluded_but_passes_S1pp_S2pp"]
    for fm in parsed_files:
        fk = (fm["db"], fm["file"])
        fm["counts"] = {k: cat_file[fk][k] for k in CAT_KEYS}
        fm["dup_existing_by_target"] = {t: tgt_file[fk][t] for t in TARGET_ORDER if tgt_file[fk][t]}
        assert (fm["counts"]["rows"] == fm["rows"]), fm
        parts = sum(fm["counts"][k] for k in ("proceedings_front_matter", "dup_within_file", "dup_within_db", "dup_across_db", "dup_existing", "new_unique"))
        assert parts == fm["rows"], (fm["file"], parts, fm["rows"])
    per_db = {}
    for db in DBS:
        fs = [f for f in parsed_files if f["db"] == db["key"]]
        if not fs:
            continue
        d = {k: sum(f["counts"][k] for f in fs) for k in CAT_KEYS}
        d["files"] = len(fs)
        t = collections.Counter()
        for f in fs:
            t.update(f["dup_existing_by_target"])
        d["dup_existing_by_target"] = {k: t[k] for k in TARGET_ORDER if t[k]}
        per_db[db["key"]] = d
    tot = {k: sum(d[k] for d in per_db.values()) for k in CAT_KEYS}
    tt = collections.Counter()
    for d in per_db.values():
        tt.update(d["dup_existing_by_target"])
    tot["dup_existing_by_target"] = {k: tt[k] for k in TARGET_ORDER if tt[k]}
    live_recs = [r for r in recs if not r["proceedings_volume"]]
    new_recs = [r for r in live_recs if not r["dup_primary"]]
    kinds = collections.Counter(r["dup_primary"]["kind"] for r in live_recs if r["dup_primary"])
    summary = {
        "date": args.date, "run_utc": run_utc, "script": "tools/ingest_subscription.py",
        "command": "python tools/ingest_subscription.py" + ("" if len(_argv) < 2 else " " + " ".join(_argv[1:])),
        "decision": "D0031 (subscription databases); D0027/D0028 queue rule", "targets": dict(tg.stats),
        "title_resolved_queue_present": tg.title_resolved_present,
        "rules": {"title_jaccard": JACC, "year_gap_refused_above": YEAR_GAP, "within_db_merge_reasons": dict(reasons)},
        "files": [{k: v for k, v in f.items() if k not in ("notes",)} for f in files],
        "per_db_query": {f"{f['db']}:{f['query']}:{f['file']}": {"rows": f["rows"], "expected_rows": f.get("expected_rows"),
                                                              "rows_match_expected": f.get("rows_match_expected"), **f["counts"],
                                                              "dup_existing_by_target": f["dup_existing_by_target"]} for f in parsed_files},
        "per_db": per_db, "totals": tot,
        "unique_records": len(recs), "unique_records_excluding_proceedings": len(live_recs),
        "duplicates_of_existing_unique_records": len(live_recs) - len(new_recs),
        "duplicate_match_kinds_unique_records": dict(kinds),
        "new_unique_records": len(new_recs),
        "new_pass_strings_queued": len(queued),
        "new_fail_strings": len(new_recs) - len(queued),
        "queued_by_tier": {f"T{t}": sum(1 for r in queued if r["tier"] == t) for t in (1, 2, 3, 4)},
        "queued_reason": dict(collections.Counter(r["queue_reason"] for r in queued)),
        "queued_abstract_missing": sum(1 for r in queued if r["abstract_missing"]),
        "new_failing_that_match_original_S1_or_S2_only_with_author_keywords": sum(
            1 for r in new_recs if not r["queued"] and (r["string_match_with_keywords"]["S1_author_keywords"] or r["string_match_with_keywords"]["S2_author_keywords"])),
        "new_failing_that_match_original_S1_or_S2_only_with_author_or_index_keywords": sum(
            1 for r in new_recs if not r["queued"] and (r["string_match_with_keywords"]["S1_all_keywords"] or r["string_match_with_keywords"]["S2_all_keywords"])),
        "title_matches_refused_for_year_gap": sum(1 for r in recs if r["rejected_year_gap"] and not r["dup_primary"]),
        "title_matches_refused_for_year_gap_examples": [
            {"id": r["id"], "title": r["title"][:100], "year": r["year"], "refused": r["rejected_year_gap"][:2]}
            for r in recs if r["rejected_year_gap"] and not r["dup_primary"]][:40],
        "new_matches_title_only_snowball_fragment": sum(1 for r in new_recs if r["nonblocking_matches"]),
        "dup_gains_abstract_and_passes": sum(1 for r in recs if r["dup_gains_abstract"]),
        "dup_target_auto_excluded_but_passes_S1pp_S2pp": sum(1 for r in recs if r["dup_target_auto_excluded_but_passes"]),
        "proceedings_front_matter_records": sum(1 for r in recs if r["proceedings_volume"]),
        "proceedings_front_matter_records_whose_volume_abstract_matches_strings": sum(1 for r in recs if r["proceedings_volume"] and r["volume_abstract_matches_S1pp_S2pp"]),
        "abstract_fetch": dict(fetch_stats), "warnings": warnings,
        "prisma": None,
        "outputs": {"records": rec_path.relative_to(ROOT).as_posix() if rec_path.is_relative_to(ROOT) else str(rec_path),
                    "queue": queue_path.relative_to(ROOT).as_posix() if queue_path.is_relative_to(ROOT) else str(queue_path),
                    "queue_delta": (delta_path.name if delta_path else None), "queue_delta_rows": len(delta) if prev else None},
    }
    summary["prisma"] = {
        "records_identified_subscription_databases": tot["rows"],
        "by_database": {k: v["rows"] for k, v in per_db.items()},
        "removed_before_screening": {
            "proceedings_front_matter_not_documents": tot["proceedings_front_matter"],
            "duplicates_within_file": tot["dup_within_file"], "duplicates_within_database": tot["dup_within_db"],
            "duplicates_across_databases": tot["dup_across_db"],
            "duplicates_of_records_already_in_corpus": tot["dup_existing"], "duplicates_of_records_already_in_corpus_by_target": tot["dup_existing_by_target"]},
        "new_unique_records": tot["new_unique"],
        "excluded_by_automation_string_filter_S1pp_S2pp": tot["new_fail_strings"],
        "passed_to_screening_subscription_queue": tot["queued"],
        "note": "counts are attributed to the first file in which a record appears (database order scopus, wos, ieee, acm, springer, sciencedirect; then file name)",
    }
    sum_path.write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf8")

    # ---- search log: one row per export file, appended once (same export path + sha256 is never logged twice)
    n_log = 0
    if not args.no_log:
        have = set()
        if ss.LOG.exists():
            for ln in ss.LOG.read_text(encoding="utf8").splitlines():
                if ln.strip():
                    j = json.loads(ln)
                    have.add((j["export"], j["sha256"]))
        for fm in parsed_files:
            if (fm["path"], fm["sha256"]) in have:
                continue
            q = fm["query"]
            note = fm.get("label")
            qtext = fm.get("query_text") or (f"verbatim part {note} of research/review/corpus/subscription-search-sheet.md ({fm['database']} section); "
                                             f"query text not repeated in {', '.join(fm['notes']) or 'the folder'}" if note else
                                             f"see {', '.join(fm['notes']) or 'the query note in the folder'}")
            filt = (f"D0031 combined/part queries, subscription database via {fm['access']}; S1''/S2'' applied locally after export; "
                    f"file mtime (export time) used as executed_utc; rows parsed {fm['rows']}"
                    + (f", expected {fm['expected_rows']} ({fm['expected_scope']})" if fm.get("expected_rows") is not None else ", expected count not available")
                    + ("; searches run 2026-10-15 (the 20261016 in the Scopus file names is a naming error, see web-of-science/wos-queries-20261015.md)" if fm["db"] == "scopus" else ""))
            row = {"database": f"{fm['database']} (subscription export, ingest tools/ingest_subscription.py)", "string": pretty_string(q, note),
                   "query": qtext, "filters": filt, "executed_utc": fm["mtime_utc"],
                   "hits_reported": fm.get("expected_rows") if fm.get("expected_rows") is not None else fm["rows"],
                   "records_retrieved": fm["rows"], "export": fm["path"], "sha256": fm["sha256"]}
            with ss.LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n_log += 1
        summary["search_log_rows_appended"] = n_log
        sum_path.write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf8")

    # ---- console summary
    print(json.dumps({"rows": tot["rows"], "unique": len(recs), "proceedings": tot["proceedings_front_matter"],
                      "dup_within_db": tot["dup_within_db"], "dup_across_db": tot["dup_across_db"], "dup_existing": tot["dup_existing"],
                      "dup_existing_by_target": tot["dup_existing_by_target"], "new_unique": tot["new_unique"], "queued": tot["queued"],
                      "search_log_rows_appended": n_log, "warnings": warnings}, indent=1))
    for fm in parsed_files:
        print(fm["db"], fm["query"], fm["file"], fm["rows"], "expected", fm.get("expected_rows"), fm["counts"])


def rec_keys(r: dict):
    """Keys that tie a record to the same record in the previous run (ids stay stable when exports are added)."""
    ks = []
    if r.get("doi"):
        ks.append(("doi", r["doi"]))
    for k, v in (r.get("source_ids") or {}).items():
        ks.append((k, v))
    if r.get("arxiv"):
        ks.append(("arxiv", r["arxiv"]))
    if not r.get("proceedings_volume"):
        sq = rto.squash(r["title"])
        if len(sq) >= 25:
            ks.append(("sq", sq))
    return ks


def prev_keys(p: dict):
    return rec_keys(p)


if __name__ == "__main__":
    main()
