"""Download the open-access full texts listed in research/review/fulltext/ft-routes.jsonl (user approved 2026-10-16).

Routes downloaded: openreview, arxiv, acl, oa_url (e-gateway, duplicate and no_full_text are skipped).
Files go to research/sources/pdfs/fulltext/<id>.pdf (gitignored); a row per record is appended to
research/review/fulltext/fetch-log.jsonl (id, route, url, status, content_type, bytes, sha256, ts).
At most 4 connections in total and one request per host at a time, with a per-host gap
(arxiv.org 3 s, others 1 s). Resumable: ids with an 'ok' row in the log are skipped.
A response that is not a PDF (landing page) is logged 'not_pdf' and not kept.

    python tools/fetch_fulltext.py [--limit N]
"""
import collections, datetime as dt, hashlib, json, sys, threading, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "research/review/fulltext/ft-routes.jsonl"
LOG = ROOT / "research/review/fulltext/fetch-log.jsonl"
OUT = ROOT / "research/sources/pdfs/fulltext"
UA = "Mozilla/5.0 (systematic review full-text retrieval; contact via VIT Vellore)"
GAP = collections.defaultdict(lambda: 1.0, {"arxiv.org": 3.0, "export.arxiv.org": 3.0})
_host_lock = collections.defaultdict(threading.Lock)
_last = {}
_log_lock = threading.Lock()


def fetch(row):
    url = row["url"]
    host = urllib.parse.urlparse(url).netloc
    rec = {"id": row["id"], "route": row["route_type"], "url": url}
    with _host_lock[host]:
        w = GAP[host] - (time.time() - _last.get(host, 0))
        if w > 0:
            time.sleep(w)
        _last[host] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/pdf,*/*"})
            with urllib.request.urlopen(req, timeout=120) as r:
                body, ctype = r.read(), r.headers.get("Content-Type", "")
            rec.update(http=200, content_type=ctype, bytes=len(body))
        except Exception as e:
            rec.update(status="error", error=repr(e)[:200])
            return rec
    if not body.startswith(b"%PDF"):
        rec["status"] = "not_pdf"
        return rec
    (OUT / f"{row['id']}.pdf").write_bytes(body)
    rec.update(status="ok", sha256=hashlib.sha256(body).hexdigest())
    return rec


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    OUT.mkdir(parents=True, exist_ok=True)
    done = set()
    if LOG.exists():
        done = {json.loads(l)["id"] for l in LOG.read_text(encoding="utf8").splitlines() if l.strip() and json.loads(l).get("status") == "ok"}
    rows = [json.loads(l) for l in ROUTES.read_text(encoding="utf8").splitlines() if l.strip()]
    todo = [r for r in rows if r["route_type"] in ("openreview", "arxiv", "acl", "oa_url") and r.get("url") and r["id"] not in done]
    todo = todo[:limit] if limit else todo
    print(f"{len(todo)} to fetch ({len(done)} already ok)", flush=True)
    stats = collections.Counter()
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, rec in enumerate(ex.map(fetch, todo), 1):
            rec["ts"] = dt.datetime.now().isoformat(timespec="seconds")
            with _log_lock, LOG.open("a", encoding="utf8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            stats[rec["status"]] += 1
            if i % 25 == 0:
                print(f"  {i}/{len(todo)} {dict(stats)}", flush=True)
    print(json.dumps(dict(stats)), flush=True)


if __name__ == "__main__":
    main()
