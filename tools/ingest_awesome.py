"""Turn a pinned Awesome-DLMs README snapshot into review screening records.

    python tools/ingest_awesome.py research/sources/md/awesome-dlms@<sha8>.md [--no-arxiv]

Writes research/review/corpus/awesome-dlms@<sha8>.jsonl (one record per unique work) and prints
PRISMA identification counts. arXiv metadata (title, dates, abstract, authors, comment,
journal reference) is added from the arXiv API in batches of 100 with a 3 s pause.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"News", "Timeline of Diffusion Language Models", "Table of Contents", "Playground", "Citation"}
DATED = re.compile(r"^\[(\d{1,2} \w{3,9} \d{4})\]\s*\[(.+?)\]\((https?://[^\s)]+)\)")
NAMED = re.compile(r"^(?:[-*]\s*)?(?:\*\*)?([^\[\]!]{0,60}?)(?:\*\*)?:?\s*\[([^\]!][^\]]+)\]\((https?://[^\s)]+)\)")
BADGE = re.compile(r"\[!\[([^\]]*)\]\([^)]*\)\]\((https?://[^\s)]+)\)")
ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})")
ATOM = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}


def canonical(url: str) -> str:
    m = ARXIV.search(url)
    if m:
        return f"arXiv:{m.group(1)}"
    m = re.search(r"openreview\.net/(?:forum|pdf)\?id=([\w-]+)", url)
    if m:
        return f"openreview:{m.group(1)}"
    m = re.search(r"doi\.org/(10\.\S+)", url)
    if m:
        return f"doi:{m.group(1)}"
    return url.rstrip("/")


def parse(text: str) -> list[dict]:
    recs: dict[str, dict] = {}
    section, cur = None, None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            section, cur = s[3:].strip(), None
            continue
        if not s or section is None or section in SKIP:
            continue
        badges = BADGE.findall(s)
        if s.startswith("[![") and badges:
            if cur is not None:
                for label, url in badges:
                    if "github.com" in url:
                        cur.setdefault("code_url", url)
                    elif label.lower().startswith("web"):
                        cur.setdefault("website", url)
                    elif ARXIV.search(url) and not cur["canonical_id"].startswith("arXiv:"):
                        cur["canonical_id"] = canonical(url)
            continue
        m = DATED.match(s)
        date, name = (m.group(1), None) if m else (None, None)
        if not m:
            m = NAMED.match(s)
            if not m:
                continue
            name = m.group(1).strip(" :*-") or None
        title, url = (m.group(2), m.group(3))
        key = canonical(url)
        cur = recs.get(key)
        if cur is None:
            cur = recs[key] = {"canonical_id": key, "title": title.strip(), "url": url,
                               "listed_date": date, "short_name": name, "sections": []}
        if section not in cur["sections"]:
            cur["sections"].append(section)
    return list(recs.values())


def arxiv_meta(ids: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        q = urllib.parse.urlencode({"id_list": ",".join(chunk), "max_results": len(chunk)})
        req = urllib.request.Request(f"https://export.arxiv.org/api/query?{q}",
                                     headers={"User-Agent": "dlm-review-ingest/0.1"})
        raw = None
        for wait in (0, 20, 45, 90):
            time.sleep(wait)
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    raw = r.read()
                break
            except urllib.error.HTTPError as err:
                if err.code not in (429, 503):
                    raise
        if raw is None:
            print(f"  arXiv API still rate-limited at {i}; rerun later to fill the rest")
            break
        if b"<!DOCTYPE" in raw or b"<!ENTITY" in raw:  # refuse entity declarations (XXE guard)
            raise ValueError("unexpected DTD in arXiv API response")
        root = ET.fromstring(raw)
        for e in root.findall("a:entry", ATOM):
            aid = re.sub(r"v\d+$", "", e.findtext("a:id", "", ATOM).rsplit("/", 1)[-1])
            get = lambda tag: (e.findtext(tag, None, ATOM) or "").strip() or None
            cat = e.find("x:primary_category", ATOM)
            out[aid] = {"title": " ".join((get("a:title") or "").split()),
                        "published": get("a:published"), "updated": get("a:updated"),
                        "abstract": " ".join((get("a:summary") or "").split()),
                        "authors": [a.findtext("a:name", "", ATOM) for a in e.findall("a:author", ATOM)],
                        "primary_category": cat.get("term") if cat is not None else None,
                        "comment": get("x:comment"), "journal_ref": get("x:journal_ref")}
        print(f"  arXiv metadata {min(i + 100, len(ids))}/{len(ids)}")
        time.sleep(3)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshot")
    ap.add_argument("--no-arxiv", action="store_true")
    a = ap.parse_args()
    snap = Path(a.snapshot)
    recs = parse(snap.read_text(encoding="utf-8-sig"))
    ids = [r["canonical_id"][6:] for r in recs if r["canonical_id"].startswith("arXiv:")]
    meta = {} if a.no_arxiv else arxiv_meta(ids)
    for n, r in enumerate(recs, 1):
        r["record_id"] = f"AW{n:04d}"
        r["source"] = snap.stem
        r["arxiv"] = meta.get(r["canonical_id"][6:]) if r["canonical_id"].startswith("arXiv:") else None
        r["screen"] = None
    out = ROOT / "research" / "review" / "corpus" / f"{snap.stem}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n", encoding="utf-8")
    print(f"records: {len(recs)}  arXiv ids: {len(ids)}  with arXiv metadata: {sum(1 for r in recs if r['arxiv'])}")
    print(f"with code link: {sum(1 for r in recs if r.get('code_url'))}  in more than one section: {sum(1 for r in recs if len(r['sections']) > 1)}")
    for sec, c in Counter(s for r in recs for s in r["sections"]).most_common():
        print(f"  {c:4d}  {sec}")
    years = Counter((r["arxiv"] or {}).get("published", "????")[:4] for r in recs)
    print("by first-version year:", dict(sorted(years.items())))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
