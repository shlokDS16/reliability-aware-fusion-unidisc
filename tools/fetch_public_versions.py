"""Public versions of the anonymous double-blind include texts (D0043, 2026-10-20): for quality appraisal QA1/QA2 and
affiliations only; screening decisions are not revisited and the screened text is not replaced.

List: T1 include records (analysis/screening/ft-t1/t1-decisions-all.jsonl) whose screened text has "Anonymous
author(s)" before the second page marker (the red-team v0.1 count rule: 287 of 608).
Lookup (metadata): arXiv API title search (export.arxiv.org, one request every 3.1 s); a hit is accepted only if
its normalised title equals the record title or their word sets agree at least 0.9 (Jaccard on words of 3+ letters).
Fetch (open access, approved by D0043): https://arxiv.org/pdf/<id> (latest version), 3 s gap, one connection.
The PDF must start with %PDF and its first page must not say "Anonymous author(s)"; it is converted with PyMuPDF
(page markers as tools/pdf_to_text.py) and its first 6,000 characters must contain the record title (normalised).

Files: research/sources/pdfs/public-version/<id>.pdf, research/sources/md/public-version/<id>.txt (both gitignored);
log research/review/fulltext/public-version-log.jsonl (one row per record and step: lookup / fetch, with sha256);
summary research/review/fulltext/public-version-summary.json. Resumable: records with a final row are skipped.

    python tools/fetch_public_versions.py list           # count only, no network (no -I: PyMuPDF is in the user site)
    python tools/fetch_public_versions.py run [--limit N]
"""
import datetime as dt, hashlib, json, re, sys, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path
import defusedxml.ElementTree as ET
import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "research/sources/md/fulltext-pymupdf"
PDF_OUT, TXT_OUT = ROOT / "research/sources/pdfs/public-version", ROOT / "research/sources/md/public-version"
LOG = ROOT / "research/review/fulltext/public-version-log.jsonl"
SUMMARY = ROOT / "research/review/fulltext/public-version-summary.json"
UA = "dlm-public-version/1.0 (systematic review; metadata lookups and open-access PDFs)"
ANON = re.compile(r"Anonymous\s+authors?", re.I)
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def norm(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    t = re.sub(r"\\[a-z]+|[{}$]", " ", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def words(t):
    return {w for w in norm(t).split() if len(w) >= 3}


def score(a, b):
    if norm(a) == norm(b):
        return 1.0
    A, B = words(a), words(b)
    return len(A & B) / max(1, len(A | B))


def anonymous_includes():
    inc = sorted(d["id"] for d in jl(ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl") if d["decision"] == "include")
    out = []
    for i in inc:
        first = (TXT / f"{i}.txt").read_text(encoding="utf-8", errors="replace").split("=== page 2 ===")[0]
        if ANON.search(first):
            out.append(i)
    return inc, out


def titles():
    t = {}
    for p in (ROOT / "research/review/fulltext/ft-routes.jsonl", ROOT / "analysis/screening/ft-routes-extra.jsonl"):
        for r in jl(p):
            t.setdefault(r["id"], r.get("title") or "")
    return t


_last = [0.0]


def get(url, timeout=60):
    w = 3.1 - (time.time() - _last[0])
    if w > 0:
        time.sleep(w)
    _last[0] = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def arxiv_search(title):
    q = " ".join(w for w in norm(title).split() if len(w) >= 3)[:300]
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": f'ti:"{q}"', "max_results": 5})
    root = ET.fromstring(get(url))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    hits = []
    for e in root.findall("a:entry", ns):
        aid = (e.findtext("a:id", "", ns) or "").rsplit("/abs/", 1)[-1]
        hits.append({"arxiv_id": re.sub(r"v\d+$", "", aid), "title": re.sub(r"\s+", " ", e.findtext("a:title", "", ns)).strip()})
    return hits


def log(rec):
    rec["ts"] = dt.datetime.now().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run(limit=None):
    inc, anon = anonymous_includes()
    T = titles()
    done = {r["id"] for r in jl(LOG) if r.get("final")} if LOG.exists() else set()
    todo = [i for i in anon if i not in done][:limit] if limit else [i for i in anon if i not in done]
    PDF_OUT.mkdir(parents=True, exist_ok=True); TXT_OUT.mkdir(parents=True, exist_ok=True)
    print(f"{len(anon)} anonymous of {len(inc)} includes; {len(todo)} to do", flush=True)
    for n, i in enumerate(todo, 1):
        title = T.get(i, "")
        try:
            hits = arxiv_search(title) if title else []
        except Exception as e:
            log({"id": i, "step": "lookup", "status": "error", "error": repr(e)[:200], "final": False}); continue
        best = max(hits, key=lambda h: score(title, h["title"]), default=None)
        sc = round(score(title, best["title"]), 3) if best else 0.0
        if not best or sc < 0.9:
            log({"id": i, "step": "lookup", "status": "not_found_arxiv", "best": best, "score": sc, "final": True}); continue
        log({"id": i, "step": "lookup", "status": "found", "arxiv_id": best["arxiv_id"], "arxiv_title": best["title"], "score": sc, "final": False})
        url = f"https://arxiv.org/pdf/{best['arxiv_id']}"
        rec = {"id": i, "step": "fetch", "arxiv_id": best["arxiv_id"], "url": url}
        try:
            body = get(url, timeout=120)
        except Exception as e:
            log({**rec, "status": "error", "error": repr(e)[:200], "final": False}); continue
        if not body.startswith(b"%PDF"):
            log({**rec, "status": "not_pdf", "bytes": len(body), "final": True}); continue
        doc = fitz.open(stream=body, filetype="pdf")
        text = "".join(f"\n=== page {k} ===\n" + p.get_text() for k, p in enumerate(doc, 1))
        first = text.split("=== page 2 ===")[0]
        status = "ok"
        if ANON.search(first):
            status = "still_anonymous"
        elif norm(title)[:40] not in norm(text[:6000]) and len(words(title) & words(text[:6000])) < 0.8 * len(words(title)):
            status = "title_not_on_first_page"
        (PDF_OUT / f"{i}.pdf").write_bytes(body)
        (TXT_OUT / f"{i}.txt").write_text(text, encoding="utf-8")
        log({**rec, "status": status, "bytes": len(body), "pages": len(doc), "sha256": hashlib.sha256(body).hexdigest(), "final": True})
        if n % 25 == 0:
            print(f"  {n}/{len(todo)}", flush=True)
    rows = jl(LOG)
    fin = {r["id"]: r for r in rows if r.get("final")}
    summ = {"anonymous_includes": len(anon), "includes": len(inc), "final_rows": len(fin),
            "by_status": {s: sum(1 for r in fin.values() if r["status"] == s) for s in sorted({r["status"] for r in fin.values()})},
            "not_final": sorted(set(anon) - set(fin))}
    SUMMARY.write_text(json.dumps(summ, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summ)[:600])


if __name__ == "__main__":
    if sys.argv[1] == "list":
        inc, anon = anonymous_includes()
        print(len(inc), len(anon))
    else:
        run(int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None)
