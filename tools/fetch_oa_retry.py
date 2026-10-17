"""Retry the open-access full texts of ft-routes.jsonl and analysis/screening/ft-routes-extra.jsonl that failed in tools/fetch_fulltext.py (user approved
2026-10-17: open access only, no OpenReview, no e-gateway).

For each oa_url record without an 'ok' row in fetch-log.jsonl, candidate PDF URLs are tried in order:
  1. other open-access locations of the DOI in OpenAlex (batched DOI filter, anonymous, no key or mailto):
     every location with a pdf_url, repositories and arXiv first;
  2. the landing page's <meta name="citation_pdf_url"> (one page request), for the original URL and the DOI;
     a landing page that is a bot check (Akamai bm-verify, Cloudflare, CAPTCHA, or a short script-only page
     without citation metadata, which may also be a script redirect) is recorded and not followed.
URLs already tried are not tried again, and hosts that answered with a bot wall (HTTP 403 from dl.acm.org,
sciencedirect.com, ssrn.com, researchgate.net, authorea.com, wiley.com) are not retried: no challenge is
answered or worked around. Every attempt is appended to fetch-log.jsonl (route 'oa_retry', with
candidate_source). Records still without a PDF go to research/review/fulltext/oa-retry-unresolved.csv (for the
user's Chrome or the e-gateway); a summary goes to oa-retry-summary.json.

    python tools/fetch_oa_retry.py
"""
import csv
import datetime as dt
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_fulltext as ff  # noqa: E402  (fetch(), host gaps, log path, output folder)

FT = ff.ROOT / "research/review/fulltext"
WALL = ("dl.acm.org", "sciencedirect.com", "ssrn.com", "researchgate.net", "authorea.com", "wiley.com")
META = re.compile(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']|'
                  r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']', re.I)


CHECK = re.compile(r"bm-verify|challenge-platform|cf-chl|captcha|_Incapsula_|Just a moment", re.I)


def walled(url):
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(host == w or host.endswith("." + w) for w in WALL)


def reason(r, last, sm):
    if walled(r["url"]) or "403" in str(last.get("error")):
        return "bot wall (HTTP 403), not retried"
    if sm.get("landing_bot_check"):
        return "landing page is a bot check (not answered): " + ", ".join(sorted(set(sm["landing_bot_check"])))
    if sm.get("landing_script_only"):
        return ("landing page is a short script-only page (bot check or script redirect), not followed: "
                + ", ".join(sorted(set(sm["landing_script_only"]))))
    if sm.get("landing_errors"):
        return "landing page unreachable: " + sm["landing_errors"][0]
    return "landing page has no citation_pdf_url and OpenAlex has no other PDF location"


def get(url, accept="text/html,*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": ff.UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(1_500_000), r.geturl()


def log(rec):
    rec["ts"] = dt.datetime.now().isoformat(timespec="seconds")
    with ff.LOG.open("a", encoding="utf8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main():
    rows = {}
    for table in (FT / "ft-routes.jsonl", ff.ROOT / "analysis/screening/ft-routes-extra.jsonl"):
        rows.update({json.loads(l)["id"]: json.loads(l) for l in table.read_text(encoding="utf8").splitlines() if l.strip()})
    hist = {}
    for l in ff.LOG.read_text(encoding="utf8").splitlines():
        if l.strip():
            r = json.loads(l); hist.setdefault(r["id"], []).append(r)
    todo = [i for i, r in rows.items() if r["route_type"] == "oa_url" and r.get("url")
            and not any(h["status"] == "ok" for h in hist.get(i, []))]
    print(f"{len(todo)} oa_url records without a PDF", flush=True)

    dois = sorted({rows[i]["doi"].lower() for i in todo if rows[i].get("doi")})
    cache_p = FT / "cache/oa-retry-openalex.json"   # OpenAlex answers, reused so a rerun needs no new calls
    cache = json.loads(cache_p.read_text(encoding="utf8")) if cache_p.exists() else {}
    need = [d for d in dois if d not in cache]
    for k in range(0, len(need), 50):
        q = "|".join(urllib.parse.quote(d, safe="/.:()-_;") for d in need[k:k + 50])
        try:
            body, _ = get(f"https://api.openalex.org/works?per-page=50&select=doi,locations&filter=doi:{q}", "application/json")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise SystemExit(f"OpenAlex daily budget used up (Retry-After {e.headers.get('Retry-After')} s); "
                                 "nothing written, rerun after the reset")
            raise
        found = {(w.get("doi") or "").lower().replace("https://doi.org/", ""): w.get("locations") or []
                 for w in json.loads(body)["results"]}
        for d in need[k:k + 50]:
            cache[d] = found.get(d)          # None = DOI not in OpenAlex
    cache_p.parent.mkdir(exist_ok=True)
    cache_p.write_text(json.dumps(cache) + "\n", encoding="utf8")
    locs = {d: cache[d] for d in dois if cache.get(d) is not None}

    summary, unresolved = {}, []
    for i in todo:
        r = rows[i]; doi = (r.get("doi") or "").lower()
        tried = {h["url"] for h in hist.get(i, [])}
        cands = []
        ls = sorted(locs.get(doi, []), key=lambda x: ((x.get("source") or {}).get("type") != "repository",))
        for x in ls:
            if x.get("is_oa") and x.get("pdf_url"):
                cands.append((x["pdf_url"], "openalex:" + str((x.get("source") or {}).get("display_name"))))
        for page in [r["url"]] + ([f"https://doi.org/{doi}"] if doi else []):
            if walled(page):
                continue
            try:
                body, final = get(page)
            except Exception as e:  # landing page unreachable: logged in the summary only
                summary.setdefault(i, {}).setdefault("landing_errors", []).append(repr(e)[:120])
                continue
            text = body.decode("utf8", "replace")
            host = urllib.parse.urlparse(final).netloc
            if CHECK.search(text):
                summary.setdefault(i, {}).setdefault("landing_bot_check", []).append(host)
                continue
            if len(body) < 10_000 and "<script" in text.lower() and "citation_" not in text:
                summary.setdefault(i, {}).setdefault("landing_script_only", []).append(host)
                continue
            for m in META.finditer(text):
                u = html.unescape(m.group(1) or m.group(2))
                cands.append((urllib.parse.urljoin(final, u), "citation_pdf_url:" + urllib.parse.urlparse(final).netloc))
        seen, outcome = set(), "unresolved"
        for url, src in cands:
            if url in tried or url in seen or walled(url):
                continue
            seen.add(url)
            rec = ff.fetch({"id": i, "url": url, "route_type": "oa_retry"})
            rec["candidate_source"] = src
            log(rec)
            if rec["status"] == "ok":
                outcome = f"ok via {src}"
                break
        summary.setdefault(i, {}).update(outcome=outcome, candidates_tried=len(seen))
        if outcome == "unresolved":
            last = hist.get(i, [{}])[-1]
            unresolved.append({"id": i, "title": r.get("title"), "doi": doi or None, "url": r["url"],
                               "first_failure": last.get("error") or last.get("status"),
                               "reason": reason(r, last, summary[i]), "downloaded": ""})
        print(i, summary[i]["outcome"], flush=True)

    with open(FT / "oa-retry-unresolved.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "title", "doi", "url", "first_failure", "reason", "downloaded"])
        w.writeheader(); w.writerows(unresolved)
    retry_ok = sorted({json.loads(l)["id"] for l in ff.LOG.read_text(encoding="utf8").splitlines()
                       if l.strip() and '"oa_retry"' in l and json.loads(l)["status"] == "ok"})
    out = {"date": dt.date.today().isoformat(), "recovered_by_retry_all_runs": len(retry_ok), "recovered_ids": retry_ok,
           "n_this_run": len(todo),
           "ok": sum(1 for v in summary.values() if v["outcome"].startswith("ok")),
           "unresolved": len(unresolved), "openalex_dois_queried": len(dois), "openalex_dois_found": len(locs),
           "records": summary}
    (FT / "oa-retry-summary.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("records", "recovered_ids")}), flush=True)


if __name__ == "__main__":
    main()
