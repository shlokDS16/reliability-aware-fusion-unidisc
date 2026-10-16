"""Download the OpenReview full texts that have no other open route, with the user's own OpenReview account.

Uses the official client (openreview-py). Credentials are NEVER passed or printed by this script: the client
reads OPENREVIEW_USERNAME and OPENREVIEW_PASSWORD from the environment, which the user sets.

    pip install openreview-py
    either put the two lines OPENREVIEW_USERNAME=... and OPENREVIEW_PASSWORD=... in the git-ignored .env file at the
    repository root (the user writes it; Claude never opens it), or set them in the shell:
    set OPENREVIEW_USERNAME=...   (PowerShell: $env:OPENREVIEW_USERNAME="...")
    set OPENREVIEW_PASSWORD=...
    python tools/fetch_openreview.py --limit 3     # test first
    python tools/fetch_openreview.py               # then all (resumable)

Targets: research/review/fulltext/arxiv-map/unmapped.jsonl rows whose failed route is openreview; the note id
comes from the route URL in research/review/fulltext/ft-routes.jsonl. Tries API v2 (api2.openreview.net),
then API v1 (api.openreview.net) for older venues. One request every 3 s. Stops after 5 consecutive
failures (for example a challenge page) and prints why. PDFs go to research/sources/pdfs/fulltext/<id>.pdf;
one row per record is appended to research/review/fulltext/fetch-log.jsonl (route 'openreview-api').
"""
import datetime as dt, hashlib, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/sources/pdfs/fulltext"
LOG = ROOT / "research/review/fulltext/fetch-log.jsonl"


def load_dotenv():
    """Read OPENREVIEW_USERNAME / OPENREVIEW_PASSWORD from the git-ignored .env at the repository root, if present.
    Values go straight into this process's environment; nothing is printed or logged."""
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf8-sig").splitlines():
        k, sep, v = line.strip().partition("=")
        if sep and k.strip() in ("OPENREVIEW_USERNAME", "OPENREVIEW_PASSWORD") and not os.environ.get(k.strip()):
            os.environ[k.strip()] = v.strip().strip("'\"")


def main():
    load_dotenv()
    if not (os.environ.get("OPENREVIEW_USERNAME") and os.environ.get("OPENREVIEW_PASSWORD")):
        sys.exit("Set OPENREVIEW_USERNAME and OPENREVIEW_PASSWORD in this shell first (see the docstring).")
    import openreview  # openreview-py
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    routes = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "research/review/fulltext/ft-routes.jsonl", encoding="utf8")}
    unm = [json.loads(l) for l in open(ROOT / "research/review/fulltext/arxiv-map/unmapped.jsonl", encoding="utf8")]
    ids = [u["id"] for u in unm if routes.get(u["id"], {}).get("route_type") == "openreview"]
    ok = {json.loads(l)["id"] for l in LOG.read_text(encoding="utf8").splitlines() if l.strip() and json.loads(l).get("status") == "ok"} if LOG.exists() else set()
    todo = [i for i in ids if i not in ok][:limit] if limit else [i for i in ids if i not in ok]
    print(f"{len(ids)} OpenReview records without another route; {len(todo)} to fetch now")
    c2 = openreview.api.OpenReviewClient(baseurl="https://api2.openreview.net")
    c1 = None
    OUT.mkdir(parents=True, exist_ok=True)
    fails = n_ok = 0
    for k, rid in enumerate(todo, 1):
        note = routes[rid]["url"].split("id=")[-1]
        rec = {"id": rid, "route": "openreview-api", "url": f"openreview note {note}"}
        body, err = None, ""
        for api in ("v2", "v1"):
            try:
                if api == "v1" and c1 is None:
                    c1 = openreview.Client(baseurl="https://api.openreview.net")
                body = (c2 if api == "v2" else c1).get_pdf(note)
                if body and body[:4] == b"%PDF":
                    rec["api"] = api
                    break
                err, body = f"{api}: not a PDF", None
            except Exception as e:
                err, body = f"{api}: {repr(e)[:160]}", None
            time.sleep(3)
        if body:
            (OUT / f"{rid}.pdf").write_bytes(body)
            rec.update(status="ok", bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
            fails, n_ok = 0, n_ok + 1
        else:
            rec.update(status="error", error=err)
            fails += 1
        rec["ts"] = dt.datetime.now().isoformat(timespec="seconds")
        with LOG.open("a", encoding="utf8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"{k}/{len(todo)} {rid} {rec['status']} {rec.get('api', '')} {err if not body else ''}", flush=True)
        if fails >= 5:
            sys.exit(f"Stopped after 5 failures in a row; last error: {err}. Tell Claude this message.")
        time.sleep(3)
    print(f"done: {n_ok} ok of {len(todo)}")


if __name__ == "__main__":
    main()
