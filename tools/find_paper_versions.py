"""Paper versions of the 20 web-only seed records (D0047, 2026-10-20): S1243 records whose route is web_page or
web_repository (analysis/screening/ft-routes-seed1243.jsonl) are searched for a paper version (metadata only); a found
open-access paper version is downloaded, logged and hashed, and screened as the record's full text; records with no
paper version are reported in PRISMA as "no study report retrievable".

Query: the record title; for a repository title "owner/name" the name with - and _ read as spaces. Sources: arXiv
API title search (export.arxiv.org, 3.1 s gap) and Semantic Scholar /paper/search/match (no key, 1.2 s gap).
Score: 1.0 if normalised titles are equal, else Jaccard on words of 3+ letters (as tools/fetch_public_versions.py).
A hit scoring >= 0.9 is "found"; 0.5-0.9 is "candidate" (the orchestrator reads it and, if it is the same work,
adds the id to research/review/fulltext/paper-version-accepted.json with a note); below 0.5 "not_found".

    python tools/find_paper_versions.py lookup      # writes paper-version-log.jsonl (step lookup), resumable
    python tools/find_paper_versions.py fetch       # found + accepted ids with an arXiv id: PDF to
                                                    # research/sources/pdfs/fulltext/<id>.pdf, row in fetch-log.jsonl
                                                    # (route paper_version_arxiv), then run tools/pdf_to_text.py and
                                                    # tools/ft_title_check.py as for any downloaded text
    python tools/find_paper_versions.py summary     # paper-version-summary.json
Run without -I: defusedxml is in the user site.
"""
import datetime as dt, hashlib, json, re, sys, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path
import defusedxml.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "analysis/screening/ft-routes-seed1243.jsonl"
FT = ROOT / "research/review/fulltext"
LOG, ACC, SUMMARY = FT / "paper-version-log.jsonl", FT / "paper-version-accepted.json", FT / "paper-version-summary.json"
FETCH_LOG, PDF_OUT = FT / "fetch-log.jsonl", ROOT / "research/sources/pdfs/fulltext"
UA = "dlm-paper-version/1.0 (systematic review; metadata lookups and open-access PDFs)"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.exists() else []
_last = {}


def norm(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", re.sub(r"\\[a-z]+|[{}$]", " ", t)).strip()


def words(t):
    return {w for w in norm(t).split() if len(w) >= 3}


def score(a, b):
    if norm(a) == norm(b):
        return 1.0
    A, B = words(a), words(b)
    return len(A & B) / max(1, len(A | B))


def get(url, gap, timeout=60):
    host = urllib.parse.urlparse(url).netloc
    w = gap - (time.time() - _last.get(host, 0))
    if w > 0:
        time.sleep(w)
    _last[host] = time.time()
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
        return r.read()


def query_of(row):
    t = row["title"]
    if row["route_type"] == "web_repository" and re.fullmatch(r"[\w.-]+/[\w.-]+", t.strip()):
        t = re.sub(r"[-_]+", " ", t.split("/", 1)[1])
    return t


def arxiv(q):
    s = " ".join(w for w in norm(q).split() if len(w) >= 3)[:300]
    root = ET.fromstring(get("http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": f'ti:"{s}"', "max_results": 5}), 3.1))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    return [{"source": "arxiv", "arxiv_id": re.sub(r"v\d+$", "", (e.findtext("a:id", "", ns) or "").rsplit("/abs/", 1)[-1]),
             "title": re.sub(r"\s+", " ", e.findtext("a:title", "", ns)).strip()} for e in root.findall("a:entry", ns)]


def s2(q):
    url = "https://api.semanticscholar.org/graph/v1/paper/search/match?" + urllib.parse.urlencode(
        {"query": q[:300], "fields": "title,externalIds,openAccessPdf,year,venue"})
    for k in range(4):
        try:
            d = json.loads(get(url, 1.2))
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
            if e.code == 429 and k < 3:
                time.sleep(5 * (k + 1)); continue
            raise
    return [{"source": "s2", "s2_id": p.get("paperId"), "title": p.get("title") or "",
             "arxiv_id": (p.get("externalIds") or {}).get("ArXiv"), "doi": (p.get("externalIds") or {}).get("DOI"),
             "oa_pdf": (p.get("openAccessPdf") or {}).get("url"), "year": p.get("year"), "venue": p.get("venue")}
            for p in d.get("data", [])]


def log(p, rec):
    rec["ts"] = dt.datetime.now().isoformat(timespec="seconds")
    with p.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def records():
    return [r for r in jl(ROUTES) if r["route_type"] in ("web_page", "web_repository")]


def lookup():
    done = {r["id"] for r in jl(LOG) if r.get("step") == "lookup" and r.get("status") != "error"}
    for row in records():
        if row["id"] in done:
            continue
        q = query_of(row); hits, errs = [], []
        for fn in (arxiv, s2):
            try:
                hits += fn(q)
            except Exception as e:
                errs.append(f"{fn.__name__}: {repr(e)[:150]}")
        for h in hits:
            h["score"] = round(score(q, h["title"]), 3)
        best = max(hits, key=lambda h: (h["score"], bool(h.get("arxiv_id"))), default=None)
        sc = best["score"] if best else 0.0
        st = "error" if errs and not hits else "found" if sc >= 0.9 else "candidate" if sc >= 0.5 else "not_found"
        log(LOG, {"id": row["id"], "step": "lookup", "query": q, "record_title": row["title"], "url": row["url"],
                  "status": st, "best": best, "hits": hits[:6], "errors": errs})
        print(row["id"], st, sc, (best or {}).get("title", "")[:70], flush=True)


def fetch():
    acc = json.loads(ACC.read_text(encoding="utf-8")) if ACC.exists() else {}
    lk = {r["id"]: r for r in jl(LOG) if r.get("step") == "lookup"}
    ok = {r["id"] for r in jl(FETCH_LOG) if r.get("status") == "ok"}
    for i, r in sorted(lk.items()):
        b = r.get("best") or {}
        if not (r["status"] == "found" or i in acc) or i in ok:
            continue
        aid = (acc.get(i) or {}).get("arxiv_id") or b.get("arxiv_id")
        if not aid:
            log(LOG, {"id": i, "step": "fetch", "status": "no_arxiv_id", "best": b}); continue
        url = f"https://arxiv.org/pdf/{aid}"
        rec = {"id": i, "route": "paper_version_arxiv", "url": url}
        try:
            body = get(url, 3.1, timeout=120)
        except Exception as e:
            log(FETCH_LOG, {**rec, "status": "error", "error": repr(e)[:200]}); continue
        if not body.startswith(b"%PDF"):
            log(FETCH_LOG, {**rec, "status": "not_pdf", "bytes": len(body)}); continue
        PDF_OUT.mkdir(parents=True, exist_ok=True)
        (PDF_OUT / f"{i}.pdf").write_bytes(body)
        log(FETCH_LOG, {**rec, "status": "ok", "content_type": "application/pdf", "bytes": len(body),
                        "sha256": hashlib.sha256(body).hexdigest()})
        log(LOG, {"id": i, "step": "fetch", "status": "ok", "arxiv_id": aid})
        print(i, "ok", aid, flush=True)


def summary():
    acc = json.loads(ACC.read_text(encoding="utf-8")) if ACC.exists() else {}
    lk = {r["id"]: r for r in jl(LOG) if r.get("step") == "lookup"}
    ok = {r["id"] for r in jl(FETCH_LOG) if r.get("status") == "ok" and r.get("route") == "paper_version_arxiv"}
    s = {"decision": "D0047", "records": len(records()), "looked_up": len(lk),
         "lookup_status": {k: sum(r["status"] == k for r in lk.values()) for k in ("found", "candidate", "not_found", "error")},
         "accepted_after_reading": sorted(acc), "downloaded": sorted(ok),
         "no_paper_version": sorted(i for i, r in lk.items() if i not in ok and r["status"] != "error"
                                    and not (r["status"] == "found" or i in acc))}
    SUMMARY.write_text(json.dumps(s, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(s))


if __name__ == "__main__":
    {"lookup": lookup, "fetch": fetch, "summary": summary}[sys.argv[1]]()
