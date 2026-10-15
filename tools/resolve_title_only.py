"""Resolve the snowball records that were auto-excluded on the title alone (decision D0029, action 2).

Population: research/review/corpus/new-records-2026-10-15-v2.jsonl rows with snowball_only, auto_excluded and
auto_excluded_abstract_missing (2,107). 1,409 of them are reference-list fragments (no identifier), 698 carry a Semantic Scholar
paperId but no abstract was found when the file was enriched.

    python tools/resolve_title_only.py local    # clean titles + duplicate check against records.jsonl and the v2 file (no network)
    python tools/resolve_title_only.py run      # local + online lookups (resumable: every lookup is cached) + string test + outputs
    python tools/resolve_title_only.py finish   # same as run but never goes online: uses the cache only

Steps (all in this file)
  1. clean_title(): strip reference-list debris (leading "2025b.", author list before the year, "In:", "arXiv preprint", trailing year / venue).
     Variants that add the venue field (a title often spills into it) are tried as well.
  2. match against research/review/screening/records.jsonl and the v2 file by identifier, normalised title (exact), token-set Jaccard >= 0.85,
     letters-and-digits-only equality (>= 25 characters) and a truncated-last-word prefix rule (>= 4 words; target has at most one more word).
  3. unmatched: Semantic Scholar /paper/batch (records with a paperId) or /paper/search/match (fragments), then arXiv API title search; OpenAlex
     title search only while the free quota lasts (it was exhausted on 2026-10-15: HTTP 429, X-RateLimit-Remaining 0). A match is accepted only
     if the normalised titles agree by the rules of step 2. Missing abstracts: arXiv id_list (arXiv id from Semantic Scholar), Crossref (DOI).
  4. resolved non-duplicates: S1, S2, S1', S2', S1'', S2'' on title + abstract and on the title alone; queue rule of the brief.
Outputs: corpus/title-resolution-2026-10-15.json (counts), corpus/title-resolution-records-2026-10-15.jsonl (one row per record),
screening/v2/title-resolved-queue.jsonl (records for dual screening), research/sources/title-resolution-raw/lookup-cache.jsonl (raw lookups).
Screens nothing; changes no existing file.
"""
from __future__ import annotations

import collections
import hashlib
import html
import json
import random
import re
import sys
import threading
import time
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_argv = sys.argv
sys.argv = _argv[:1]                       # merge_new_records reads sys.argv[1] as a date
sys.path.insert(0, str(Path(__file__).resolve().parent))
import merge_new_records as m              # noqa: E402
import merge_new_records_v2 as m2          # noqa: E402
import search_sources as ss                # noqa: E402
sys.argv = _argv

ROOT, CORPUS = ss.ROOT, ss.CORPUS
ISO = "2026-10-15"
V2 = CORPUS / f"new-records-{ISO}-v2.jsonl"
RAWDIR = ROOT / "research" / "sources" / "title-resolution-raw"
CACHE = RAWDIR / "lookup-cache.jsonl"
OUT_JSON = CORPUS / f"title-resolution-{ISO}.json"
OUT_ROWS = CORPUS / f"title-resolution-records-{ISO}.jsonl"
OUT_QUEUE = ROOT / "research" / "review" / "screening" / "v2" / "title-resolved-queue.jsonl"
JACC = 0.85
GAPS = {"api.datacite.org": 0.5, "api.semanticscholar.org": 2.0, "export.arxiv.org": 3.5, "api.crossref.org": 1.0, "api.openalex.org": 1.0}
S2F = "paperId,title,abstract,externalIds,year,venue,publicationDate"
SAMPLE_UNMARKED = 60
S2_PATIENT_UNTIL = 0.0          # epoch seconds; set by --s2-patient=<minutes>: retry Semantic Scholar 429s for that long
STRING_NAMES = ["S1", "S2", "S1'", "S2'", "S1''", "S2''"]


# ------------------------------------------------------------------ 1. cleaning
VENUE_WORDS = re.compile(r"arxiv|preprint|proceedings|conference|journal|transactions|workshop|findings|iclr|icml|neurips|nips|acl\b|emnlp|"
                         r"naacl|cvpr|iccv|eccv|aaai|ijcai|corr|github|openai|blog|http|www\.|\.com|\.org|tech(nical)? report|pp\.|vol\.", re.I)


def clean_title(t: str) -> str:
    t = unicodedata.normalize("NFKC", html.unescape(t or ""))
    t = re.sub(r"<[^>]+>", "", t)
    t = " ".join(t.split())
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"^\[\d+\]\s*", "", t)
    # author list before the year: "Electricity Maps. 2024. Electricity map: ..." / "AMC. 2023. American mathematics ..."
    mm = re.match(r"^(?P<pre>[^.]{0,160}?)\.\s*(?:19|20)\d\d[a-z]?\s*[.)]\s*(?P<t>.+)$", t)
    if mm:
        rest = mm.group("t")
        # "Title. 2025. arXiv: 2502.09992 [cs.CL": the text before the year is the title, not an author list
        t = mm.group("pre") if re.match(r"(?:arXiv|CoRR|Preprint|In[:\s]|URL|Technical report)", rest, re.I) else rest
    t = re.sub(r"^[^A-Za-z0-9]*(?:19|20)\d\d[a-z]?\s*[.):]\s*", "", t)         # leading "2025b." / ". 2023."
    t = re.sub(r"^(?:19|20)\d\d[a-z]?\s+(?=[A-Z])", "", t)
    # trailing venue / arXiv debris
    t = re.split(r"\s*[.,;]?\s*(?:arXiv\s*preprint|arXiv\s*:|arXiv\s+e-prints|CoRR\b|abs/\d|URL\b|Technical report\b|Preprint\b)", t, flags=re.I)[0]
    t = re.split(r"(?:[.,;]\s*|\s)(?:In:\s|In\s+(?:Proceedings|Proc\.|Advances|Findings|International|The\s+\w+\s+(?:International|Annual|Conference)|Conference|ICLR|ICML|NeurIPS|ACL|EMNLP|NAACL|CVPR))", t)[0]
    t = re.sub(r"[\s,.;(]*\b(?:19|20)\d\d[a-z]?\)?[\s.]*$", "", t)                # trailing year
    t = t.strip(" \t.,;:-–—*")
    return t


def squash(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def ntitle(t: str) -> str:
    return m.norm_title(t)


def variants_of(title: str, venue: str | None):
    """Cleaned title first; then the title with the venue field appended / prepended when that field is short and not a venue name
    (a fragment's title often spills into the next field)."""
    v0 = clean_title(title)
    out = [v0]
    ven = " ".join((venue or "").split())
    if ven and 1 <= len(ven.split()) <= 10 and not VENUE_WORDS.search(ven) and v0:
        out.append(clean_title(v0 + " " + ven))
        if ven.endswith(":") or not v0[:1].isupper():
            out.append(clean_title(ven.rstrip(":") + (": " if ven.endswith(":") else " ") + v0))
    seen, res = set(), []
    for v in out:
        if v and v.lower() not in seen:
            seen.add(v.lower())
            res.append(v)
    return res


def plausible_title(v: str) -> bool:
    """Gate before an online lookup: a bibliographic title has 2-40 words and is mostly letters (not math, prose with equations, ...)."""
    toks = v.split()
    if not (2 <= len(toks) <= 40):
        return False
    chars = re.sub(r"\s", "", v)
    if not chars:
        return False
    alpha = sum(c.isalpha() or c.isdigit() for c in chars) / len(chars)
    if alpha < 0.8 or "(cid:" in v:
        return False
    return len(m.tset(v)) >= 1


# ------------------------------------------------------------------ 2. title agreement and matching
def agree(a: str, b: str):
    """Do two titles agree? -> (kind, jaccard) or None. a is the (cleaned) fragment, b the candidate."""
    na, nb = ntitle(a), ntitle(b)
    if not na or not nb:
        return None
    if na == nb:
        return ("exact", 1.0)
    ta, tb = m.tset(a), m.tset(b)
    if len(ta) >= 3 and len(tb) >= 3:
        j = len(ta & tb) / len(ta | tb)
        if j >= JACC:
            return ("jaccard", round(j, 3))
    sa, sb = squash(a), squash(b)
    if len(sa) >= 25 and sa == sb:
        return ("squashed", 1.0)
    wa, wb = na.split(), nb.split()
    if len(wa) >= 4 and len(wb) >= len(wa) and len(wb) - len(wa) <= 1 and wa[:-1] == wb[:len(wa) - 1] and wb[len(wa) - 1].startswith(wa[-1]) and len(wa[-1]) >= 2:
        return ("prefix-truncated", round(len(m.tset(a) & tb) / max(1, len(m.tset(a) | tb)), 3))
    return None


RANK = {"exact": 4, "squashed": 3, "jaccard": 2, "prefix-truncated": 1}


def pick(v: str, cands, need: str | None = None):
    """Best title-agreeing candidate (exact > squashed > jaccard > prefix, then Jaccard) -> (candidate, agreement) or (None, None)."""
    best = None
    for c in cands or []:
        if not c.get("title") or (need and not c.get(need)):
            continue
        a = agree(v, c["title"])
        if a and (best is None or (RANK[a[0]], a[1]) > (RANK[best[1][0]], best[1][1])):
            best = (c, a)
    return best if best else (None, None)


class Targets:
    """Existing records (records.jsonl, sid R....) and the v2 file outside the population (nid M....)."""

    def __init__(self, pop_ids: set[str]):
        existing = [json.loads(l) for l in open(ROOT / "research/review/screening/records.jsonl", encoding="utf8")]
        venues = json.load(open(CORPUS / "venues-semantic-scholar.json"))["records"]
        v2 = [json.loads(l) for l in open(V2, encoding="utf8") if l.strip()]
        self.items = []          # (id, title)
        self.ids = {"arxiv": {}, "doi": {}, "s2": {}, "oa": {}}
        for e in existing:
            self.items.append((e["sid"], e["title"]))
            if e.get("arxiv"):
                self.ids["arxiv"].setdefault(e["arxiv"], e["sid"])
                d = (venues.get(e["arxiv"]) or {}).get("doi")
                if d:
                    self.ids["doi"].setdefault(d.lower(), e["sid"])
        self.n_existing = len(existing)
        self.n_v2 = 0
        for r in v2:
            if r["nid"] in pop_ids:
                continue
            self.n_v2 += 1
            self.items.append((r["nid"], r["title"]))
            if r["arxiv"]:
                self.ids["arxiv"].setdefault(r["arxiv"], r["nid"])
            if r["doi"]:
                self.ids["doi"].setdefault(r["doi"].lower(), r["nid"])
            if r["s2_id"]:
                self.ids["s2"].setdefault(r["s2_id"], r["nid"])
            if r["openalex_id"]:
                self.ids["oa"].setdefault(r["openalex_id"], r["nid"])
        self.ts = [m.tset(clean_title(t)) for _, t in self.items]
        self.inv = collections.defaultdict(list)
        for i, ts in enumerate(self.ts):
            for w in ts:
                self.inv[w].append(i)

    def by_id(self, arxiv=None, doi=None, s2=None, oa=None):
        for k, v in (("arxiv", arxiv), ("doi", (doi or "").lower() or None), ("s2", s2), ("oa", oa)):
            if v and v in self.ids[k]:
                return self.ids[k][v], "id:" + k
        return None, None

    def by_title(self, variants):
        best = None
        for v in variants:
            tv = m.tset(v)
            cand = collections.Counter(i for w in tv for i in self.inv.get(w, ()))
            pool = [i for i, _ in cand.most_common(60)]
            for i in pool:
                tt = self.items[i][1]
                a = agree(v, clean_title(tt)) or agree(v, tt)
                if a:
                    rank = {"exact": 3, "squashed": 3, "jaccard": 2, "prefix-truncated": 1}[a[0]]
                    key = (rank, a[1])
                    if best is None or key > best[0]:
                        best = (key, self.items[i][0], a[0], a[1], tt, v)
        if not best:
            return None
        return {"id": best[1], "kind": "title:" + best[2], "jaccard": best[3], "target_title": best[4], "variant": best[5]}


# ------------------------------------------------------------------ online lookups (cached)
_lock_cache = threading.Lock()
_host_locks: dict[str, threading.Lock] = collections.defaultdict(threading.Lock)
_cache: dict[str, dict] = {}
_online = True
_openalex_ok = True
_stats = collections.Counter()


def load_cache():
    RAWDIR.mkdir(parents=True, exist_ok=True)
    if CACHE.exists():
        for l in open(CACHE, encoding="utf8"):
            if l.strip():
                d = json.loads(l)
                _cache[d["k"]] = d


_breaker: dict[str, list] = collections.defaultdict(lambda: [0, 0.0])    # host -> [consecutive failures, blocked until]; Semantic Scholar and arXiv throttle hard
_deferred = collections.Counter()
BREAKER_HOSTS = {"api.semanticscholar.org", "export.arxiv.org"}


def cached(kind: str, key: str, url: str, parse, data=None, headers=None, definitive=(200, 404), tries=6):
    """GET/POST url once; cache the parsed result by (kind, key). Returns the parsed result, or {"__error__": ...} on a transient failure."""
    k = f"{kind}|{key}"
    if k in _cache:
        return _cache[k]["v"]
    if not _online:
        return {"__error__": "not-cached"}
    host = urllib.parse.urlparse(url).netloc
    br = host in BREAKER_HOSTS and not (host == "api.semanticscholar.org" and S2_PATIENT_UNTIL)
    if br and time.time() < _breaker[host][1]:
        _deferred[kind] += 1
        return {"__error__": "deferred"}
    s2 = host == "api.semanticscholar.org"
    if s2 and S2_PATIENT_UNTIL:
        if time.time() > S2_PATIENT_UNTIL:
            _deferred[kind] += 1
            return {"__error__": "deferred"}
        with _host_locks[host]:                                   # patient mode: the shared unauthenticated pool answers about every third request
            for _ in range(8):
                st, raw, hdr = ss.http(url, 4.0, data=data, headers=headers, tries=1)
                if st in definitive:
                    break
                time.sleep(6)
    else:
        with _host_locks[host]:
            st, raw, hdr = ss.http(url, GAPS.get(host, 2.0), data=data, headers=headers, tries=2 if br else tries)
    _stats[f"{kind}:{st}"] += 1
    if br:
        if st in definitive:
            _breaker[host][0] = 0
        else:
            _breaker[host][0] += 1
            if _breaker[host][0] >= 3:
                _breaker[host][1] = time.time() + 600
                _breaker[host][0] = 0
                print(f"{host} rate-limited: paused 10 min", flush=True)
    if st not in definitive:
        return {"__error__": st, "__hdr__": {a_: b_ for a_, b_ in hdr.items() if "ratelimit" in a_.lower()}}
    v = parse(st, raw)
    with _lock_cache:
        _cache[k] = {"k": k, "status": st, "v": v}
        with CACHE.open("a", encoding="utf8") as fh:
            fh.write(json.dumps(_cache[k], ensure_ascii=False) + "\n")
    return v


def p_s2_match(st, raw):
    if st == 404:
        return None
    d = (json.loads(raw).get("data") or [None])[0]
    return d


def s2_match(q: str):
    return cached("s2match", q, "https://api.semanticscholar.org/graph/v1/paper/search/match?" +
                  urllib.parse.urlencode({"query": q[:300], "fields": S2F}), p_s2_match)


def s2_batch(ids: list[str]):
    out, todo = {}, []
    for i in ids:
        k = f"s2batch|{i}"
        if k in _cache:
            out[i] = _cache[k]["v"]
        else:
            todo.append(i)
    for a in range(0, len(todo) if _online else 0, 250):
        chunk = todo[a:a + 250]
        host = "api.semanticscholar.org"
        with _host_locks[host]:
            st, raw, _ = ss.http(f"https://api.semanticscholar.org/graph/v1/paper/batch?fields={S2F}", 3.0, tries=6,
                                 data=json.dumps({"ids": chunk}).encode(), headers={"Content-Type": "application/json"})
        _stats[f"s2batch:{st}"] += 1
        if st != 200:
            print(f"S2 batch status {st}; stopped at {a}", flush=True)
            break
        for i, p in zip(chunk, json.loads(raw)):
            k = f"s2batch|{i}"
            _cache[k] = {"k": k, "status": 200, "v": p}
            out[i] = p
            with CACHE.open("a", encoding="utf8") as fh:
                fh.write(json.dumps(_cache[k], ensure_ascii=False) + "\n")
    return out


def clean_abs(a):
    return " ".join((a or "").split())


def p_arxiv(st, raw):
    if b"<!ENTITY" in raw or b"<!DOCTYPE" in raw:
        return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in ET.fromstring(raw).findall("a:entry", ns):
        aid = re.sub(r"v\d+$", "", e.findtext("a:id", "", ns).rsplit("/", 1)[-1])
        out.append({"arxiv": aid, "title": " ".join(e.findtext("a:title", "", ns).split()), "abstract": clean_abs(e.findtext("a:summary", "", ns)),
                    "published": (e.findtext("a:published", "", ns) or "")[:10], "doi": (e.findtext("{http://arxiv.org/schemas/atom}doi") or None)})
    return out


def arxiv_title(q: str):
    words = re.findall(r"[A-Za-z0-9]+", q)
    if len(words) < 2:
        return []
    sq = 'ti:"' + " ".join(words[:25]) + '"'
    r = cached("arxivti", q, "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": sq, "max_results": 5}), p_arxiv)
    if isinstance(r, dict) and "__error__" in r:
        _arxiv_err[0] += 1
        return None
    return r if isinstance(r, list) else []


def arxiv_id(aid: str):
    r = cached("arxivid", aid, "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": aid, "max_results": 1}), p_arxiv)
    return (r or [None])[0] if isinstance(r, list) else None


def p_crossref(st, raw):
    if st == 404:
        return None
    msg = json.loads(raw)["message"]
    ab = re.sub(r"<[^>]+>", " ", msg.get("abstract") or "")
    ab = re.sub(r"^\s*Abstract\s*[:.]?\s*", "", clean_abs(ab), flags=re.I)
    return {"title": " ".join(((msg.get("title") or [""])[0]).split()), "abstract": ab if len(ab) >= 80 else ""}


def crossref(doi: str):
    return cached("crossref", doi.lower(), "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"), p_crossref)


def p_datacite(st, raw):
    out = []
    for d in json.loads(raw).get("data", []):
        a = d["attributes"]
        doi = (a.get("doi") or "").lower()
        ab = next((x["description"] for x in a.get("descriptions", []) if x.get("descriptionType") == "Abstract"), "")
        mm = re.match(r"10\.48550/arxiv\.(\d{4}\.\d{4,5})", doi)
        out.append({"arxiv": mm.group(1) if mm else None, "doi": doi, "title": " ".join(((a.get("titles") or [{}])[0].get("title") or "").split()),
                    "abstract": clean_abs(ab), "published": str(a.get("publicationYear") or "")})
    return out


def datacite_arxiv(q: str):
    """arXiv records as registered at DataCite (client arxiv.content): title phrase query, with the abstract."""
    words = re.findall(r"[A-Za-z0-9]+", q)
    if len(words) < 2:
        return []
    r = cached("datacite", q, "https://api.datacite.org/dois?" + urllib.parse.urlencode(
        {"query": 'titles.title:"' + " ".join(words[:25]) + '"', "client-id": "arxiv.content", "page[size]": 10}), p_datacite)
    if isinstance(r, dict) and "__error__" in r:
        return None
    return r if isinstance(r, list) else []


def p_crossref_search(st, raw):
    out = []
    for w in json.loads(raw)["message"].get("items", []):
        ab = re.sub(r"<[^>]+>", " ", w.get("abstract") or "")
        ab = re.sub(r"^\s*Abstract\s*[:.]?\s*", "", clean_abs(ab), flags=re.I)
        yr = ((w.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        out.append({"doi": (w.get("DOI") or "").lower(), "title": " ".join(((w.get("title") or [""])[0]).split()), "abstract": ab if len(ab) >= 80 else "",
                    "year": yr, "venue": (w.get("container-title") or [None])[0]})
    return out


def crossref_title(q: str):
    r = cached("crossref-bib", q, "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": q[:300], "rows": 3, "select": "DOI,title,abstract,issued,container-title"}), p_crossref_search)
    if isinstance(r, dict) and "__error__" in r:
        return None
    return r if isinstance(r, list) else []


def p_openalex(st, raw):
    out = []
    for w in json.loads(raw).get("results", []):
        inv = w.get("abstract_inverted_index") or {}
        pos = sorted((i, t) for t, ix in inv.items() for i in ix)
        out.append({"id": w.get("id"), "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower() or None, "title": " ".join((w.get("title") or "").split()),
                    "abstract": " ".join(t for _, t in pos), "year": w.get("publication_year")})
    return out


def openalex_title(q: str):
    global _openalex_ok
    if not _openalex_ok:
        return []
    r = cached("openalex", q, "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": q[:300], "per-page": 3, "select": "id,doi,title,publication_year,abstract_inverted_index"}), p_openalex)
    if isinstance(r, dict) and "__error__" in r:
        if r["__error__"] == 429 and _online:
            _openalex_ok = False
            print("OpenAlex quota exhausted (429); skipped from here", flush=True)
        return []
    return r or []


# ------------------------------------------------------------------ resolution of one record
def p_datacite_one(st, raw):
    if st == 404:
        return None
    a = json.loads(raw)["data"]["attributes"]
    ab = next((x["description"] for x in a.get("descriptions", []) if x.get("descriptionType") == "Abstract"), "")
    return {"title": " ".join(((a.get("titles") or [{}])[0].get("title") or "").split()), "abstract": clean_abs(ab)}


def datacite_doi(arxiv: str):
    """Abstract of an arXiv paper from its DataCite record (DOI 10.48550/arXiv.<id>); fast, unlike the arXiv API."""
    r = cached("datacite-doi", arxiv, "https://api.datacite.org/dois/" + urllib.parse.quote("10.48550/arxiv." + arxiv), p_datacite_one)
    return r if isinstance(r, dict) and "__error__" not in r else None


def _mk(c, src, a, v, **kw):
    d = {"title": c["title"], "arxiv": None, "doi": None, "s2_id": None, "openalex_id": None, "year": None, "venue": None, "abstract": "",
         "abstract_source": None, "source": src, "match_kind": a[0], "jaccard": a[1], "query": v}
    d.update(kw)
    d["abstract_source"] = src if d["abstract"] else None
    return d


def resolve_online(rec: dict, variants: list[str], identified: bool, slow: bool):
    """Fast sources (DataCite for arXiv, Crossref, cached Semantic Scholar batch) when slow is False; the throttled ones (Semantic
    Scholar title match, arXiv API, OpenAlex) when slow is True. Returns the resolved metadata or None; rec["_incomplete"] is set when
    a source could not be asked."""
    res = None
    if identified:
        p = rec["_s2batch"].get(rec["s2_id"]) if rec.get("_s2batch") and rec["s2_id"] else None
        ex = (p or {}).get("externalIds") or {}
        res = {"title": (p or {}).get("title") or rec["title"], "arxiv": rec["arxiv"] or ex.get("ArXiv"), "doi": rec["doi"] or (ex.get("DOI") or "").lower() or None,
               "s2_id": rec["s2_id"], "openalex_id": rec["openalex_id"], "year": (p or {}).get("year"), "venue": (p or {}).get("venue") or rec["venue"],
               "abstract": clean_abs((p or {}).get("abstract")), "source": "s2-id" if p else "record-identifier", "match_kind": "identifier", "jaccard": 1.0}
        res["abstract_source"] = "semantic-scholar-batch" if res["abstract"] else None
    else:
        for v in variants[:2]:
            cs = datacite_arxiv(v)
            if cs is None:
                rec["_incomplete"] = True
                cs = []
            c, a = pick(v, cs, "arxiv")
            if c:
                res = _mk(c, "datacite-arxiv", a, v, arxiv=c["arxiv"], abstract=c["abstract"], year=int(c["published"]) if c["published"].isdigit() else None)
                break
        if not res:
            for v in variants[:2]:
                cs = crossref_title(v)
                if cs is None:
                    rec["_incomplete"] = True
                    cs = []
                c, a = pick(v, cs)
                if c:
                    res = _mk(c, "crossref-title", a, v, doi=c["doi"], abstract=c["abstract"], year=c.get("year"), venue=c.get("venue"))
                    break
        if not res and slow:
            for v in variants:
                d = s2_match(v)
                if isinstance(d, dict) and "__error__" in d:
                    rec["_incomplete"] = True
                    continue
                if isinstance(d, dict) and d.get("title"):
                    a = agree(v, d["title"])
                    if a:
                        ex = d.get("externalIds") or {}
                        res = _mk(d, "s2-match", a, v, arxiv=ex.get("ArXiv"), doi=(ex.get("DOI") or "").lower() or None, s2_id=d.get("paperId"),
                                  year=d.get("year"), venue=d.get("venue"), abstract=clean_abs(d.get("abstract")))
                        break
        if not res and slow:
            for v in variants[:2]:
                cs = arxiv_title(v)
                if cs is None:
                    rec["_incomplete"] = True
                    cs = []
                c, a = pick(v, cs)
                if c:
                    res = _mk(c, "arxiv-title", a, v, arxiv=c["arxiv"], doi=(c.get("doi") or "").lower() or None,
                              year=int(c["published"][:4]) if c.get("published") else None, abstract=c["abstract"])
                    break
        if not res and slow:
            for v in variants[:2]:
                c, a = pick(v, openalex_title(v))
                if c:
                    res = _mk(c, "openalex-title", a, v, doi=c["doi"], openalex_id=c["id"], year=c.get("year"), abstract=clean_abs(c["abstract"]))
                    break
    if not res:
        return None
    # abstract fill, fast sources first
    if not res["abstract"] and res["arxiv"]:
        e = datacite_doi(res["arxiv"])
        if e and e.get("abstract"):
            res["abstract"], res["abstract_source"] = e["abstract"], "datacite-arxiv-id"
    if not res["abstract"] and res["doi"] and not res["doi"].startswith("10.48550/"):
        c = crossref(res["doi"])
        if isinstance(c, dict) and c.get("abstract"):
            res["abstract"], res["abstract_source"] = c["abstract"], "crossref-doi"
    if not res["abstract"] and not res["arxiv"]:                                 # is there a preprint with this title?
        c, _ = pick(variants[0], [x for x in (datacite_arxiv(variants[0]) or []) if x.get("arxiv")], "abstract")
        if c:
            res["abstract"], res["abstract_source"], res["arxiv"] = c["abstract"], "datacite-arxiv-title", c["arxiv"]
    if not res["abstract"] and slow and res["arxiv"]:
        e = arxiv_id(res["arxiv"])
        if e and e.get("abstract"):
            res["abstract"], res["abstract_source"] = e["abstract"], "arxiv-id"
    if not res["abstract"] and slow and not res["arxiv"]:
        c, _ = pick(variants[0], arxiv_title(variants[0]), "abstract")
        if c:
            res["abstract"], res["abstract_source"], res["arxiv"] = c["abstract"], "arxiv-title", c["arxiv"]
    if not res["abstract"] and slow and res["source"] != "openalex-title":
        c, _ = pick(variants[0], openalex_title(variants[0]), "abstract")
        if c:
            res["abstract"], res["abstract_source"] = clean_abs(c["abstract"]), "openalex-title"
    return res


# ------------------------------------------------------------------ 4. strings
def string_tests(title: str, abstract: str):
    ta = {s: ss.matches(s, title + " " + abstract) for s in STRING_NAMES}
    to = {s: ss.matches(s, title) for s in STRING_NAMES}
    rule = [s for s in ("S1''", "S2''", "S1", "S2") if ta[s]] + ["title:" + s for s in ("S1", "S2", "S1'", "S2'") if to[s]]
    return ta, to, rule


# ------------------------------------------------------------------ main
def population():
    rows = [json.loads(l) for l in open(V2, encoding="utf8") if l.strip()]
    return [r for r in rows if r["snowball_only"] and r["auto_excluded"] and r["auto_excluded_abstract_missing"]]


def main(mode: str):
    global _online
    t0 = time.time()
    pop = population()
    assert len(pop) == 2107, len(pop)
    tg = Targets({r["nid"] for r in pop})
    print(f"population {len(pop)}; targets: {tg.n_existing} existing + {tg.n_v2} v2 records", flush=True)
    for r in pop:
        r["_variants"] = variants_of(r["title"], r["venue"])
        r["_identified"] = bool(r["s2_id"] or r["doi"] or r["arxiv"])
    out = {r["nid"]: {"nid": r["nid"], "original_title": r["title"], "venue_field": r["venue"], "seed": (r.get("extra") or {}).get("seed"),
                      "identified": r["_identified"], "cleaned_title": r["_variants"][0] if r["_variants"] else "", "variants": r["_variants"]} for r in pop}

    # step 2: local duplicates (before any lookup)
    todo = []
    for r in pop:
        o = out[r["nid"]]
        d_id, k_id = tg.by_id(r["arxiv"], r["doi"], r["s2_id"], r["openalex_id"])
        d_t = tg.by_title(r["_variants"]) if r["_variants"] else None
        ea = m2.embedded_arxiv(r["title"])
        if not d_id and ea and ea in tg.ids["arxiv"]:
            d_id, k_id = tg.ids["arxiv"][ea], "id:embedded-arxiv"
        if d_id:
            o.update(status="duplicate", duplicate_of=d_id, duplicate_match=k_id, duplicate_stage="local")
        elif d_t:
            o.update(status="duplicate", duplicate_of=d_t["id"], duplicate_match=d_t["kind"], duplicate_jaccard=d_t["jaccard"],
                     duplicate_target_title=d_t["target_title"], duplicate_stage="local")
        else:
            todo.append(r)
    print(f"local duplicates: {len(pop) - len(todo)}; to resolve: {len(todo)}", flush=True)
    if mode == "local":
        print(collections.Counter(o.get("duplicate_match") for o in out.values() if o.get("status") == "duplicate"))
        return

    # step 3: lookups
    load_cache()
    _online = mode == "run"
    ident = [r for r in todo if r["_identified"]]
    b = s2_batch([r["s2_id"] for r in ident if r["s2_id"]])
    for r in ident:
        r["_s2batch"] = b
    gate = {}
    for r in todo:
        o = out[r["nid"]]
        if r["_identified"]:
            gate[r["nid"]] = True
        else:
            gate[r["nid"]] = bool(r["_variants"]) and plausible_title(r["_variants"][0])
            if not gate[r["nid"]]:
                o.update(status="unresolvable", unresolvable_reason="not a bibliographic title (fewer than 2 or more than 40 words, equations, prose or symbols)")
    work = [r for r in todo if gate[r["nid"]]]
    done = [0]

    def run_pass(rows, slow, workers):
        done = [0]

        def job(r):
            try:
                res = resolve_online(r, r["_variants"], r["_identified"], slow)
            except Exception as e:                                               # a bad response must not stop 2,000 lookups
                res = None
                out[r["nid"]]["error"] = repr(e)[:200]
            done[0] += 1
            if done[0] % 50 == 0:
                print(f"  {'slow' if slow else 'fast'} pass {done[0]}/{len(rows)}  {time.time() - t0:.0f}s  {dict(_stats)}", flush=True)
            return r["nid"], res

        with ThreadPoolExecutor(max_workers=workers) as ex:
            return dict(ex.map(job, rows))

    def reference_like(r):
        o = r["title"]
        return int(clean_title(o) != " ".join(o.split())) + int(bool(r["venue"] and VENUE_WORDS.search(r["venue"]))) + int(bool(re.match(r"^\W*(19|20)\d\d", o)))

    results = run_pass(work, False, 6)
    unresolved = sorted([r for r in work if not results[r["nid"]]], key=lambda r: -reference_like(r))
    # Semantic Scholar and arXiv throttle hard (HTTP 429 for minutes at a time), so the slow pass covers the records that carry reference-list
    # markers (a leading year, debris stripped by clean_title, an arXiv/venue string in the venue field) plus a random check sample of the others.
    marked = [r for r in unresolved if reference_like(r) >= 1]
    unmarked = [r for r in unresolved if reference_like(r) == 0]
    check = random.Random(20261015).sample(sorted(unmarked, key=lambda r: r["nid"]), min(SAMPLE_UNMARKED, len(unmarked))) if unmarked else []
    check_ids = {r["nid"] for r in check}
    rest = marked + check
    skipped_slow = [r for r in unmarked if r["nid"] not in check_ids]
    for r in rest:
        r["_incomplete"] = False
    for r in skipped_slow:
        out[r["nid"]]["slow_lookup"] = "not queried (no reference-list marker)"
    for r in check:
        out[r["nid"]]["slow_lookup"] = "random check sample"
    for r in marked:
        out[r["nid"]]["slow_lookup"] = "queried"
    print(f"fast pass resolved {len(work) - len(rest)} of {len(work)}; slow pass over {len(rest)}", flush=True)
    results.update(run_pass(rest, True, 2) if _online or rest else {})
    for r in work:
        o, res = out[r["nid"]], results[r["nid"]]
        if res:
            o.update(status="resolved", resolved=res)
        elif out[r["nid"]].get("slow_lookup") == "not queried (no reference-list marker)":
            o.update(status="unresolvable", unresolvable_reason="no title-agreeing record in DataCite (arXiv) or Crossref; Semantic Scholar/arXiv API not queried (no reference-list marker, see random check)")
        elif r.get("_incomplete"):
            o.update(status="unresolved-lookup-incomplete", unresolvable_reason="a lookup source was rate-limited or not cached; rerun to finish")
        else:
            o.update(status="unresolvable", unresolvable_reason="no title-agreeing record in Semantic Scholar" +
                     (", OpenAlex (quota exhausted)" if not _openalex_ok else ", OpenAlex") + " or arXiv")

    # duplicates after resolution: by identifier and by the resolved title; and among the resolved themselves
    first_by_key = {}
    for r in work:
        o = out[r["nid"]]
        if o["status"] != "resolved":
            continue
        res = o["resolved"]
        d_id, k_id = tg.by_id(res["arxiv"], res["doi"], res["s2_id"], res["openalex_id"])
        d_t = None if d_id else tg.by_title([res["title"]])
        if d_id or d_t:
            o.update(status="duplicate", duplicate_of=d_id or d_t["id"], duplicate_match=k_id or d_t["kind"], duplicate_stage="after-resolution",
                     duplicate_target_title=(d_t or {}).get("target_title"))
            continue
        keys = [k for k in (("arxiv", res["arxiv"]), ("doi", res["doi"]), ("s2", res["s2_id"]), ("t", ntitle(res["title"]))) if k[1] and (k[0] != "t" or len(k[1].split()) >= 3)]
        prior = next((first_by_key[k] for k in keys if k in first_by_key), None)
        if prior:
            o.update(status="duplicate", duplicate_of=prior, duplicate_match="within-population", duplicate_stage="after-resolution")
            continue
        for k in keys:
            first_by_key[k] = r["nid"]

    # step 4: strings
    queue = []
    for r in pop:
        o = out[r["nid"]]
        if o["status"] != "resolved":
            continue
        res = o["resolved"]
        ta, to, rule = string_tests(res["title"], res["abstract"])
        o["string_match"] = {"title_abstract": ta, "title_only": to}
        o["queue_rule_hits"] = rule
        o["queued"] = bool(rule)
        if rule:
            queue.append({"id": r["nid"], "title": res["title"], "abstract": res["abstract"],
                          "ids": {"arxiv": res["arxiv"], "doi": res["doi"], "s2_id": res["s2_id"], "openalex_id": res["openalex_id"]},
                          "string_match": {**{s: ta[s] for s in STRING_NAMES}, "title_only": to, "rule_hits": rule},
                          "original_title": r["title"], "year": res.get("year"), "venue": res.get("venue"), "abstract_source": res["abstract_source"],
                          "resolution_source": res["source"], "title_agreement": {"kind": res["match_kind"], "jaccard": res["jaccard"]},
                          "seed": (r.get("extra") or {}).get("seed"), "sources": r["sources"], "found_by": r["found_by"],
                          "queue_reason": "snowball record excluded on the title alone (D0026), resolved by title lookup (D0029 item 2)"})
    # unresolved fragments whose cleaned title (or the title joined with the venue field it spilled into) matches a string: the title is the
    # only metadata there is, and it is in scope by the strings, so they go to the queue as title-only records (counted apart from the resolved ones)
    frag_queue = []
    for r in pop:
        o = out[r["nid"]]
        if o["status"] not in ("unresolvable", "unresolved-lookup-incomplete") or o["identified"]:
            continue
        hits = []
        for v in o["variants"]:
            h = [n for n in ("S1", "S2", "S1'", "S2'", "S1''", "S2''") if ss.matches(n, v)]
            if h:
                hits.append((v, h))
        if not hits:
            continue
        v, h = max(hits, key=lambda x: len(x[1]))
        tv = m.tset(v)
        cand = collections.Counter(i for w in tv for i in tg.inv.get(w, ()))
        best = None
        for i, _ in cand.most_common(30):
            inter = len(tv & tg.ts[i])
            if len(tv) >= 3 and inter / len(tv) >= 0.9 and (best is None or inter / len(tv | tg.ts[i]) > best[0]):
                best = (inter / len(tv | tg.ts[i]), tg.items[i][0], tg.items[i][1])
        o["fragment_title_match"] = {"variant": v, "strings": h, "possible_duplicate_of": best[1] if best else None, "possible_duplicate_title": best[2] if best else None}
        frag_queue.append({"id": r["nid"], "title": v, "abstract": "", "ids": {"arxiv": None, "doi": None, "s2_id": None, "openalex_id": None},
                           "string_match": {**{n: (n in h) for n in STRING_NAMES}, "title_only": {n: (n in h) for n in STRING_NAMES}, "rule_hits": ["title:" + n for n in h]},
                           "original_title": r["title"], "year": None, "venue": r["venue"], "abstract_source": None, "resolution_source": "none (unresolved fragment, title only)",
                           "title_agreement": None, "seed": (r.get("extra") or {}).get("seed"), "sources": r["sources"], "found_by": r["found_by"],
                           "possible_duplicate_of": best[1] if best else None, "possible_duplicate_title": best[2] if best else None,
                           "queue_reason": "snowball fragment excluded on the title alone (D0026); cleaned title matches the strings; no metadata could be retrieved"})
    queue_all = queue + frag_queue
    # ---- outputs
    OUT_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_QUEUE.open("w", encoding="utf8") as fh:
        for q in queue_all:
            fh.write(json.dumps(q, ensure_ascii=False) + "\n")
    with OUT_ROWS.open("w", encoding="utf8") as fh:
        for r in pop:
            fh.write(json.dumps(out[r["nid"]], ensure_ascii=False) + "\n")
    st = collections.Counter(o["status"] for o in out.values())
    res_rows = [o for o in out.values() if o["status"] == "resolved"]
    dup_rows = [o for o in out.values() if o["status"] == "duplicate"]
    unres = [o for o in out.values() if o["status"] == "unresolvable"]
    incomplete = [o for o in out.values() if o["status"] == "unresolved-lookup-incomplete"]
    rep = {
        "date": ISO, "decision": "D0029 item 2", "script": "tools/resolve_title_only.py", "mode": mode,
        "population": len(pop), "population_definition": "snowball_only and auto_excluded and auto_excluded_abstract_missing in corpus/new-records-2026-10-15-v2.jsonl",
        "population_with_identifier": sum(1 for o in out.values() if o["identified"]), "population_fragments_without_identifier": sum(1 for o in out.values() if not o["identified"]),
        "duplicates_of_existing_records": len(dup_rows),
        "duplicates_by_stage": dict(collections.Counter(o["duplicate_stage"] for o in dup_rows)),
        "duplicates_by_match_kind": dict(collections.Counter(o["duplicate_match"] for o in dup_rows)),
        "duplicates_of_records_jsonl_R": sum(1 for o in dup_rows if o["duplicate_of"].startswith("R")),
        "duplicates_of_v2_file_M": sum(1 for o in dup_rows if o["duplicate_of"].startswith("M")),
        "duplicates_within_population": sum(1 for o in dup_rows if o["duplicate_match"] == "within-population"),
        "slow_pass": {"fast_pass_resolved": len(work) - len(unresolved), "unresolved_after_fast_pass": len(unresolved),
                      "with_reference_marker_queried": len(marked), "without_marker_not_queried": len(skipped_slow),
                      "without_marker_random_check_sample": {"n": len(check), "resolved": sum(1 for r in check if results.get(r["nid"]))}},
        "resolved": len(res_rows),
        "resolved_with_abstract": sum(1 for o in res_rows if o["resolved"]["abstract"]),
        "resolved_without_abstract": sum(1 for o in res_rows if not o["resolved"]["abstract"]),
        "resolved_by_source": dict(collections.Counter(o["resolved"]["source"] for o in res_rows)),
        "resolved_by_title_agreement": dict(collections.Counter(o["resolved"]["match_kind"] for o in res_rows)),
        "resolved_abstract_source": dict(collections.Counter(o["resolved"]["abstract_source"] or "none" for o in res_rows)),
        "unresolved_lookup_incomplete": len(incomplete),
        "unresolvable": len(unres),
        "unresolvable_by_reason": dict(collections.Counter(o["unresolvable_reason"] for o in unres)),
        "resolved_and_matching_strings_queued": len(queue),
        "unresolved_fragments_with_cleaned_title_matching_strings_queued_title_only": len(frag_queue),
        "queue_total": len(queue_all),
        "unresolved_fragment_queue_possible_duplicates": sum(1 for q in frag_queue if q["possible_duplicate_of"]),
        "queued_by_rule_hit": dict(collections.Counter(h for q in queue for h in q["string_match"]["rule_hits"])),
        "queued_with_abstract": sum(1 for q in queue if q["abstract"]), "queued_without_abstract": sum(1 for q in queue if not q["abstract"]),
        "resolved_not_matching": len(res_rows) - len(queue),
        "check_sum": {"duplicates+resolved+unresolvable+incomplete": len(dup_rows) + len(res_rows) + len(unres) + len(incomplete), "population": len(pop)},
        "lookup_calls_this_run": dict(_stats),
        "openalex": "free budget exhausted on 2026-10-15 (HTTP 429, X-RateLimit-Remaining 0, reset at midnight UTC) apart from a few early answers (3 resolutions)",
        "notes": [
            "Sources used, in order: Semantic Scholar /paper/batch (698 records with a paperId; 670 answered, none returned an abstract), DataCite REST API restricted to "
            "client arxiv.content (arXiv records with abstracts), Crossref query.bibliographic, Semantic Scholar /paper/search/match, arXiv API ti:\"...\", OpenAlex.",
            "OpenAlex: free budget exhausted on 2026-10-15 (HTTP 429, X-RateLimit-Remaining 0) apart from a few early answers; no OpenAlex DOI batch could be run for the "
            "abstract-less records. Rerunning 'python tools/resolve_title_only.py run' after the daily reset (cache-resumable) would use it.",
            "Semantic Scholar (unauthenticated shared pool) answered HTTP 429 to about two requests in three for hours; the title-match step is therefore incomplete: "
            "records listed under unresolved_lookup_incomplete were not answered by it. The arXiv API added no match beyond DataCite.",
            "A fragment whose cleaned title (or the title joined to the venue field it spilled into) matches S1, S2, S1', S2', S1'' or S2'' but which could not be "
            "resolved is queued title-only and counted apart (unresolved_fragments_with_cleaned_title_matching_strings_queued_title_only); possible duplicates are flagged.",
        ],
        "title_agreement_rules": f"normalised-title equality; token-set Jaccard >= {JACC} (stop words removed, >= 3 tokens each); letters-and-digits equality (>= 25 chars); "
                                 "prefix-truncated (fragment of >= 4 words equals the start of the target, last word may be cut, target has at most one more word)",
        "queue_rule": "S1'' or S2'' or S1 or S2 on title + abstract of the resolved record, or the resolved title alone matches S1, S2, S1' or S2'",
        "queue_file": OUT_QUEUE.relative_to(ROOT).as_posix(), "records_file": OUT_ROWS.relative_to(ROOT).as_posix(),
        "queue_sha256": hashlib.sha256(OUT_QUEUE.read_bytes()).hexdigest(),
        "elapsed_seconds": round(time.time() - t0),
    }
    OUT_JSON.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf8")
    print(json.dumps(rep, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    for a_ in sys.argv[2:]:
        if a_.startswith("--s2-patient="):
            S2_PATIENT_UNTIL = time.time() + 60 * float(a_.split("=", 1)[1])
    main(sys.argv[1] if len(sys.argv) > 1 else "run")
