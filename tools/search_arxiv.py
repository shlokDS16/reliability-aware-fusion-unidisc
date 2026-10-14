"""Logged arXiv searches for the review (protocol section 3) and published-version lookup.

    python tools/search_arxiv.py count            # hit counts for each candidate string (pilot)
    python tools/search_arxiv.py run S1 S2        # retrieve all hits, log the run, report recall and new records
    python tools/search_arxiv.py venues           # Semantic Scholar batch lookup of published venue and DOI

Every run appends to research/review/corpus/search-log.jsonl: database, exact query, filters,
execution time (UTC), hit count, export file and its SHA-256.
"""
from __future__ import annotations

import datetime as dt
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
NS = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/"}
CATS = "(cat:cs.CL OR cat:cs.LG OR cat:cs.CV OR cat:cs.AI OR cat:stat.ML)"
WINDOW = "submittedDate:[202101010000 TO 202610142359]"
STRINGS = {
    # S1: diffusion language models, discrete and continuous
    "S1": '(abs:"diffusion language model" OR abs:"diffusion language models" OR abs:"discrete diffusion" OR '
          'abs:"masked diffusion" OR abs:"absorbing diffusion" OR abs:"discrete flow matching" OR abs:"diffusion LLM" OR '
          'abs:"diffusion large language model" OR abs:"text diffusion" OR ti:"Diffusion-LM") AND '
          '(abs:language OR abs:text OR abs:token OR abs:tokens)',
    # S2: unified multimodal understanding and generation with a diffusion-type component
    "S2": '(abs:"unified multimodal" OR abs:"understanding and generation" OR abs:"any-to-any") AND '
          '(abs:diffusion OR abs:"masked generative" OR abs:"discrete flow" OR abs:"flow matching") AND '
          '(abs:multimodal OR abs:"vision-language" OR abs:"text-to-image")',
    # narrower variant of S1 kept for the sensitivity report
    "S1n": '(abs:"diffusion language model" OR abs:"diffusion language models" OR abs:"masked diffusion language" OR '
           'abs:"discrete diffusion language" OR abs:"diffusion LLM" OR abs:"diffusion large language model")',
}


def get(url: str, data: bytes | None = None, headers: dict | None = None) -> bytes | None:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "dlm-review-search/0.1", **(headers or {})})
    for wait in (0, 20, 60, 180):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 503):
                print(f"  HTTP {e.code} for {url[:90]}")
                return None
        except (urllib.error.URLError, TimeoutError):
            continue
    return None


def query(name: str) -> str:
    return f"({STRINGS[name]}) AND {CATS} AND {WINDOW}"


def page(q: str, start: int, n: int) -> ET.Element | None:
    raw = get("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q, "start": start, "max_results": n, "sortBy": "submittedDate", "sortOrder": "ascending"}))
    if raw is None or b"<!DOCTYPE" in raw or b"<!ENTITY" in raw:
        return None
    return ET.fromstring(raw)


def known_ids() -> set[str]:
    ids = set()
    for f in CORPUS.glob("awesome-dlms@*.jsonl"):
        for x in f.read_text(encoding="utf-8").splitlines():
            if x.strip():
                c = json.loads(x)["canonical_id"]
                if c.startswith("arXiv:"):
                    ids.add(c[6:])
    return ids


def cmd_count() -> None:
    for name in STRINGS:
        root = page(query(name), 0, 1)
        total = root.findtext("o:totalResults", "?", NS) if root is not None else "request failed"
        print(f"{name}: {total} hits")
        time.sleep(3)


def cmd_run(names: list[str]) -> None:
    known, found = known_ids(), {}
    for name in names:
        q, start, total, rows = query(name), 0, None, []
        while total is None or start < total:
            root = page(q, start, 200)
            if root is None:
                print(f"  {name}: request failed at offset {start}; rerun later")
                break
            total = int(root.findtext("o:totalResults", "0", NS))
            entries = root.findall("a:entry", NS)
            if not entries:
                break
            for e in entries:
                aid = re.sub(r"v\d+$", "", e.findtext("a:id", "", NS).rsplit("/", 1)[-1])
                rows.append({"arxiv": aid, "title": " ".join(e.findtext("a:title", "", NS).split()),
                             "published": e.findtext("a:published", "", NS)[:10],
                             "abstract": " ".join(e.findtext("a:summary", "", NS).split()), "string": name})
            start += len(entries)
            print(f"  {name}: {start}/{total}", flush=True)
            time.sleep(3)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = CORPUS / f"arxiv-{name}-{stamp}.jsonl"
        out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
        with (CORPUS / "search-log.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"database": "arXiv API (export.arxiv.org)", "string": name, "query": q,
                                 "filters": "categories and submittedDate window inside the query; no other filter",
                                 "executed_utc": stamp, "hits_reported": total, "records_retrieved": len(rows),
                                 "export": out.name, "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}) + "\n")
        for r in rows:
            found.setdefault(r["arxiv"], r)
        got = {r["arxiv"] for r in rows}
        print(f"{name}: reported {total}, retrieved {len(rows)}, recall of the {len(known)} Awesome-DLMs arXiv records "
              f"{len(got & known)} ({len(got & known) / len(known):.0%}), not in Awesome-DLMs {len(got - known)}")
    if len(names) > 1:
        allf = set(found)
        print(f"union: {len(allf)} unique; recall {len(allf & known) / len(known):.0%}; new candidates {len(allf - known)}")


def cmd_venues() -> None:
    ids, out = sorted(known_ids()), {}
    for i in range(0, len(ids), 400):
        raw = get("https://api.semanticscholar.org/graph/v1/paper/batch?fields=externalIds,venue,publicationVenue,"
                  "publicationTypes,journal,year,citationCount",
                  data=json.dumps({"ids": [f"ARXIV:{x}" for x in ids[i:i + 400]]}).encode(),
                  headers={"Content-Type": "application/json"})
        if raw is None:
            print(f"  Semantic Scholar request failed at {i}; rerun later")
            break
        for aid, p in zip(ids[i:i + 400], json.loads(raw)):
            if p:
                out[aid] = {"venue": p.get("venue") or None, "venue_type": (p.get("publicationVenue") or {}).get("type"),
                            "doi": (p.get("externalIds") or {}).get("DOI"), "types": p.get("publicationTypes"),
                            "journal": (p.get("journal") or {}).get("name"), "year": p.get("year"),
                            "citations": p.get("citationCount")}
        time.sleep(5)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (CORPUS / "venues-semantic-scholar.json").write_text(json.dumps({"retrieved_utc": stamp, "records": out}, indent=0), encoding="utf-8")
    ven = [v for v in out.values() if v["venue"] and "arxiv" not in v["venue"].lower()]
    print(f"looked up {len(ids)}; found {len(out)}; with a non-arXiv venue {len(ven)}; "
          f"with a non-arXiv DOI {sum(1 for v in out.values() if v['doi'] and 'arxiv' not in v['doi'].lower())}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "count":
        cmd_count()
    elif cmd == "run":
        cmd_run(sys.argv[2:] or ["S1", "S2"])
    elif cmd == "venues":
        cmd_venues()
    else:
        sys.exit(__doc__)
