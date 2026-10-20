"""Abstract lookup (metadata only) for records without an abstract (D0044, 2026-10-20: the 217 free-source rescue
positives in research/review/screening/v2/dual-rescue-free/pending-no-abstract-rf.jsonl).

Order per record: OpenAlex (batched DOI filter, 50 per request; abstract rebuilt from abstract_inverted_index),
then Crossref (DOI; JATS tags stripped), then Semantic Scholar (paper id or DOI; no key, 1.2 s gap, backs off on
429). The first non-empty abstract of at least 200 characters is kept with its source and URL. Every request
outcome is logged. Resumable: ids already found are skipped; not-found ids are retried on the next run
(OpenAlex returns 429 once its daily allowance is used; it resets about 05:30 IST).

    python -I tools/lookup_abstracts.py run [--limit N]

Writes dual-rescue-free/abstract-lookup-log.jsonl (one row per record: id, source, url, chars, status) and
dual-rescue-free/abstracts-found.jsonl ({id, title, abstract, abstract_source}).
"""
import html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "research/review/screening/v2/dual-rescue-free"
LOG, FOUND = D / "abstract-lookup-log.jsonl", D / "abstracts-found.jsonl"
UA = "dlm-review-abstracts/1.0 (systematic review metadata lookups)"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
_last = {}


def get(url, gap=1.0, tries=4):
    host = urllib.parse.urlparse(url).netloc
    for k in range(tries):
        w = gap - (time.time() - _last.get(host, 0))
        if w > 0:
            time.sleep(w)
        _last[host] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                time.sleep(10 * (k + 1)); continue
            if k == tries - 1:
                raise
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(3)
    return None


def from_inverted(ix):
    pos = [(p, w) for w, ps in (ix or {}).items() for p in ps]
    return " ".join(w for _, w in sorted(pos))


def clean(t):
    t = re.sub(r"<[^>]+>", " ", t or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def main(limit=None):
    pend = jl(D / "pending-no-abstract-rf.jsonl")
    meta = {}
    for l in open(ROOT / "research/review/corpus/new-records-2026-10-15-v2.jsonl", encoding="utf-8"):
        r = json.loads(l)
        meta[r["nid"]] = r
    done = {r["id"] for r in jl(LOG) if r.get("status") == "found"} if LOG.exists() else set()   # not_found rows are retried
    todo = [p["id"] for p in pend if p["id"] not in done][:limit] if limit else [p["id"] for p in pend if p["id"] not in done]
    print(f"{len(todo)} to look up", flush=True)
    oa = {}
    dois = sorted({meta[i]["doi"].lower() for i in todo if meta[i].get("doi")})
    for k in range(0, len(dois), 50):
        ch = dois[k:k + 50]
        url = ("https://api.openalex.org/works?per-page=50&select=doi,abstract_inverted_index&filter=doi:"
               + "|".join(urllib.parse.quote(d, safe="/.:()-_;") for d in ch))
        try:
            res = get(url, gap=1.0) or {"results": []}
        except Exception as e:
            print("openalex batch failed", repr(e)[:120])
            with LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"id": None, "status": "openalex_batch_failed", "error": repr(e)[:120], "dois": len(ch)}) + "
")
            continue
        for w in res["results"]:
            oa[(w.get("doi") or "").lower().replace("https://doi.org/", "")] = from_inverted(w.get("abstract_inverted_index"))
    n = 0
    for i in todo:
        r = meta[i]; doi = (r.get("doi") or "").lower(); found = None; tried = []
        if doi and len(oa.get(doi, "")) >= 200:
            found = ("openalex", f"https://api.openalex.org/works/doi:{doi}", oa[doi])
        tried.append("openalex" if doi else "openalex:no-doi")
        if not found and doi:
            try:
                cr = get(f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}", gap=1.0)
                a = clean(((cr or {}).get("message") or {}).get("abstract"))
                if len(a) >= 200:
                    found = ("crossref", f"https://api.crossref.org/works/{doi}", a)
            except Exception as e:
                tried.append(f"crossref:error {repr(e)[:60]}")
            tried.append("crossref")
        if not found and (r.get("s2_id") or doi):
            pid = r.get("s2_id") or f"DOI:{doi}"
            try:
                s2 = get(f"https://api.semanticscholar.org/graph/v1/paper/{urllib.parse.quote(pid, safe=':')}?fields=abstract", gap=1.2)
                a = clean((s2 or {}).get("abstract"))
                if len(a) >= 200:
                    found = ("semantic-scholar", f"https://api.semanticscholar.org/graph/v1/paper/{pid}", a)
            except Exception as e:
                tried.append(f"s2:error {repr(e)[:60]}")
            tried.append("semantic-scholar")
        row = {"id": i, "tried": tried, "status": "found" if found else "not_found"}
        if found:
            row.update(source=found[0], url=found[1], chars=len(found[2]))
            with FOUND.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"id": i, "title": r["title"], "abstract": found[2], "abstract_source": found[0]}, ensure_ascii=False) + "\n")
            n += 1
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    print(f"found {n} of {len(todo)}", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None)
