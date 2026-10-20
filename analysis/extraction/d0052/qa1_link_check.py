"""QA1 d, dated link check (EXTRACTION-PLAN-v0.2 s7.1 QA1: d = dated link check by script).

    python -I analysis/extraction/d0052/qa1_link_check.py            -> qa1-links.jsonl (one row per record)

For every final record (rq_analysis.py's choice: EC for the second-reader ids, else EA pass 2 or pass 1) whose QA1 a
(own-code URL) is yes, the candidate own-code URLs are the code-host URLs printed on the page QA1's loc names
(github, gitlab, huggingface, bitbucket, codeberg, zenodo, anonymous.4open.science, sourceforge), or anywhere in the
text when the loc gives no page or that page has none. Each candidate is fetched once (GET, redirects followed,
timeout 20 s, one request per second). PDF line breaks inside URLs are joined first. Only repository-level URLs count
(owner/repo on GitHub, GitLab, Bitbucket, Codeberg or Hugging Face; anonymous.4open.science/r/<id>; a Zenodo record),
and only those whose context (250 characters before, 80 after) says our, we, code or implementation ("own" URLs).
d = "yes" if an own URL answers 200 and is not GitHub's 404 page; "no" if every own URL fails; "unclear-owner" if
repository URLs are printed but none has own wording; "no-repo-url" or "no-url" otherwise. Only "yes" counts as d.
Rows where the rule picks third-party URLs are settled by a model read in qa1-owner-reads.jsonl (id, d, own_url,
quote, reason; d "check" fetches own_url; D0056: model reads, author confirms), which replaces d and keeps the script's value as d_script.
Nothing is decided about ownership beyond the extractor's QA1 a and the page rule; the row keeps every URL and status.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "analysis/extraction/d0052"
TXT = [ROOT / "research/sources/md/fulltext-pymupdf", ROOT / "research/sources/md/census-text-paged"]
HOST = re.compile(r"https?://(?:www\.)?(?:github\.com|gitlab\.com|huggingface\.co|bitbucket\.org|codeberg\.org|zenodo\.org"
                  r"|anonymous\.4open\.science|sourceforge\.net|[a-z0-9-]+\.github\.io)/[^\s\)\]\}>\"',;]*", re.I)
UA = "Mozilla/5.0 (systematic-review link check)"


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip().startswith("{")]


def final_records():
    seed = json.load(open(D / "seed-sample.json", encoding="utf-8"))
    recs = {}
    for folder in sorted((D / "EA").glob("*")):
        files = sorted(folder.glob("EA-*.jsonl"))
        p2 = [f for f in files if f.stem.endswith("-pass2")]
        for f in (p2 or [f for f in files if not f.stem.endswith("-pass2")]):
            for r in jl(f):
                recs[r["id"]] = r
    for f in sorted((D / "EC").glob("*/*.jsonl")):
        for r in jl(f):
            if r.get("id") in seed["second_reader_ids"]:
                recs[r["id"]] = r
    return recs


def text_of(i):
    for d in TXT:
        p = d / f"{i}.txt"
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    return ""


def page(t, n):
    parts = re.split(r"^=== page (\d+) ===\s*$", t, flags=re.M)
    pages = {int(parts[k]): parts[k + 1] for k in range(1, len(parts) - 1, 2)}
    return pages.get(n, "")


def clean(u):
    u = u.rstrip(".")
    return u


def fetch(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(200000).decode("utf-8", errors="replace")
            code = r.status
            final = r.geturl()
    except urllib.error.HTTPError as e:
        return {"url": u, "status": e.code, "ok": False}
    except Exception as e:  # network errors, timeouts
        return {"url": u, "status": type(e).__name__, "ok": False}
    ok = code == 200 and not ("github.com" in final and "Page not found" in body[:5000])
    return {"url": u, "status": code, "final": final, "ok": ok}


REPO = re.compile(r"^https?://(?:www\.)?(?:(?:github\.com|gitlab\.com|bitbucket\.org|codeberg\.org|huggingface\.co)/[^/\s]+/[^/\s]+"
                  r"|anonymous\.4open\.science/r/[^/\s]+|zenodo\.org/(?:record|records|doi)/\S+)", re.I)
OWN = re.compile(r"(?<![A-Za-z])(our|we|code|codes|implementation)\b", re.I)


def own_context(t, u):
    """True when the 250 characters before the URL (or 80 after) say our, we, code or implementation."""
    k = t.find(u)
    if k < 0:
        return False
    return bool(OWN.search(t[max(0, k - 250):k] + " " + t[k:k + len(u) + 80]))


def dewrap(t):
    """Join URLs broken by a PDF line end after '/', '-' or '_'."""
    return re.sub(r"(https?://\S*[/\-_])\n(\S+)", r"\1\2", t)


def main():
    recs = final_records()
    out = []
    for i, r in sorted(recs.items()):
        q = ((r.get("qa") or {}).get("QA1") or {})
        a = (q.get("sub") or {}).get("a")
        if a != "yes":
            continue
        t = dewrap(text_of(i))
        loc = q.get("loc") or ""
        m = re.search(r"p\.?\s*(\d+)", loc)
        cand = sorted({clean(u) for u in HOST.findall(page(t, int(m.group(1))) if m else "")})
        where = "loc page"
        if not cand:
            cand = sorted({clean(u) for u in HOST.findall(t)})
            where = "whole text"
        repo = [u for u in cand if REPO.match(u)]
        own = [u for u in repo if own_context(t, u)]
        checks = []
        for u in own[:6]:
            checks.append(fetch(u))
            time.sleep(1)
        d = ("no-url" if not cand else "no-repo-url" if not repo else "unclear-owner" if not own
             else "yes" if any(c["ok"] for c in checks) else "no")
        out.append({"id": i, "loc": loc, "where": where, "candidates": cand, "repo_urls": repo, "own_urls": own,
                    "checks": checks, "d": d,
                    "checked_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        sys.stdout.write(f"{i} {d} {len(cand)}\n")
        sys.stdout.flush()
    reads = {x["id"]: x for x in jl(D / "qa1-owner-reads.jsonl")} if (D / "qa1-owner-reads.jsonl").exists() else {}
    for x in out:                      # model reads of the owner where the script's own-URL rule is ambiguous (D0056)
        if x["id"] in reads:
            rd = reads[x["id"]]
            x["d_script"], x["owner_read"] = x["d"], rd
            if rd["d"] == "check":         # fetch the read's own URL
                c = fetch(rd["own_url"])
                x["owner_check"] = c
                x["d"] = "yes" if c["ok"] else "no"
            else:
                x["d"] = rd["d"]
    (D / "qa1-links.jsonl").write_text("".join(json.dumps(x) + "\n" for x in out), encoding="utf-8")
    print(sum(x["d"] == "yes" for x in out), "of", len(out), "resolve")


if __name__ == "__main__":
    main()
