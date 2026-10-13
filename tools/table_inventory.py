"""Corpus-wide feasibility inventory from arXiv HTML, with no language model involved.

    python tools/table_inventory.py research/review/corpus/awesome-dlms@<sha8>.jsonl [--limit N]

For every arXiv record: fetch the HTML rendering (cached under research/sources/html/), pull every
table and figure caption, and flag by keyword the captions that look like (a) an ablation or
matched contrast, (b) a sweep over denoising or sampling steps, (c) a remasking contrast,
(d) a comparison with autoregressive models. Also flags whether the text mentions seeds, standard
deviations, intervals or a code repository. Output: research/review/feasibility/captions.jsonl and
a printed summary per README section. These are keyword signals (evidence level E1): they say
where to read, not what the paper shows.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "research" / "sources" / "html"
OUT = ROOT / "research" / "review" / "feasibility"
CAPTION = re.compile(r"<figcaption[^>]*>(.*?)</figcaption>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
FLAGS = {
    "ablation": re.compile(r"ablat|w/o\b|without\b|effect of|impact of|contribution of|component", re.I),
    "steps": re.compile(r"\b(denoising|sampling|diffusion|inference|decoding)\s+steps?\b|\bNFEs?\b|function evaluations|number of steps|step count", re.I),
    "remask": re.compile(r"re-?mask", re.I),
    "vs_ar": re.compile(r"autoregress|\bAR\b", re.I),
    "synergy": re.compile(r"synerg|joint training|mutual|understanding and generation", re.I),
}
TEXT_FLAGS = {
    "variance": re.compile(r"\bseeds?\b|standard deviation|std\.?\s*dev|±|\\pm", re.I),
    "interval": re.compile(r"confidence interval|error bars?|statistically significant|p\s*[<=]\s*0?\.\d", re.I),
    "code": re.compile(r"github\.com/[\w.-]+/[\w.-]+", re.I),
}


def fetch(aid: str) -> str | None:
    f = CACHE / f"{aid}.html"
    if f.exists():
        return f.read_text(encoding="utf-8", errors="replace") or None
    req = urllib.request.Request(f"https://arxiv.org/html/{aid}", headers={"User-Agent": "dlm-review-inventory/0.1"})
    for wait in (0, 30, 90, 240):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                text = r.read().decode("utf-8", errors="replace")
            f.write_text(text, encoding="utf-8")
            time.sleep(3)
            return text
        except urllib.error.HTTPError as e:
            if e.code == 404:
                f.write_text("", encoding="utf-8")  # no HTML rendering for this paper
                time.sleep(3)
                return None
            if e.code not in (429, 503):
                return None
        except (urllib.error.URLError, TimeoutError):
            continue
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    recs = [json.loads(x) for x in Path(a.corpus).read_text(encoding="utf-8").splitlines() if x.strip()]
    recs = [r for r in recs if r["canonical_id"].startswith("arXiv:")]
    if a.limit:
        recs = recs[: a.limit]
    rows, per_section = [], defaultdict(Counter)
    for n, r in enumerate(recs, 1):
        aid = r["canonical_id"][6:]
        text = fetch(aid)
        row = {"record_id": r["record_id"], "arxiv": aid, "title": r["title"], "sections": r["sections"],
               "has_html": bool(text), "captions": [], "flags": {}, "text_flags": {}}
        if text:
            for raw in CAPTION.findall(text):
                cap = " ".join(html.unescape(TAG.sub(" ", raw)).split())
                kind = "table" if cap.lower().startswith("table") else "figure"
                hits = [k for k, rx in FLAGS.items() if rx.search(cap)]
                if hits:
                    row["captions"].append({"kind": kind, "flags": hits, "text": cap[:300]})
            for k in FLAGS:
                row["flags"][k] = sum(1 for c in row["captions"] if k in c["flags"])
            for k, rx in TEXT_FLAGS.items():
                row["text_flags"][k] = bool(rx.search(text))
        rows.append(row)
        for s in r["sections"]:
            c = per_section[s]
            c["papers"] += 1
            c["html"] += bool(text)
            for k in FLAGS:
                c[k] += bool(row["flags"].get(k))
            for k in TEXT_FLAGS:
                c[k] += bool(row["text_flags"].get(k))
        if n % 25 == 0:
            print(f"  {n}/{len(recs)} fetched", flush=True)
    (OUT / "captions.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    cols = ["papers", "html", *FLAGS, *TEXT_FLAGS]
    print("papers with at least one flagged caption or text signal, by README section")
    print(f"{'section':<26}" + "".join(f"{c[:8]:>9}" for c in cols))
    for s, c in sorted(per_section.items(), key=lambda kv: -kv[1]["papers"]):
        print(f"{s[:25]:<26}" + "".join(f"{c[k]:>9}" for k in cols))
    tot = Counter()
    for row in rows:
        tot["papers"] += 1
        tot["html"] += row["has_html"]
        for k in FLAGS:
            tot[k] += bool(row["flags"].get(k))
        for k in TEXT_FLAGS:
            tot[k] += bool(row["text_flags"].get(k))
    print(f"{'ALL (unique)':<26}" + "".join(f"{tot[k]:>9}" for k in cols))


if __name__ == "__main__":
    main()
