"""Random-sample census (framework-v2 D2; codebook v1.1): draw the coding order and fetch full texts.

Population: records that both title-and-abstract screeners passed to full text
(research/review/screening/screener-A and screener-B; include or unclear for both) and that have an
arXiv ID. The population is put in a random order with a fixed seed; coders work down the order,
check full-text eligibility, and stop when the target number of eligible papers is coded, so the
sample is a simple random sample of eligible records.

    python tools/census_sample.py order               # write census-order.csv (seed 20261015)
    python tools/census_sample.py fetch --first 220   # fetch arXiv HTML and write plain text

Full texts are cached in the MAIN checkout (research/sources/, gitignored), shared by worktrees.
"""
import argparse
import csv
import html
import json
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR = ROOT / "research" / "review" / "screening"
OUT = ROOT / "research" / "review" / "census"
MAIN = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model")
HTML = MAIN / "research" / "sources" / "html"
TEXT = MAIN / "research" / "sources" / "census-text"
SEED = 20261015


def decisions(folder):
    d = {}
    for f in sorted((SCR / folder).glob("batch-*.jsonl")):
        for line in open(f, encoding="utf8"):
            x = json.loads(line)
            d[x["sid"]] = x["decision"]
    return d


def order():
    A, B = decisions("screener-A"), decisions("screener-B")
    recs = [json.loads(l) for l in open(SCR / "records.jsonl", encoding="utf8")]
    pop = [r for r in recs if r["arxiv"] and A.get(r["sid"]) != "exclude" and B.get(r["sid"]) != "exclude"]
    rng = random.Random(SEED)
    rng.shuffle(pop)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "census-order.csv", "w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "sid", "arxiv", "title"])
        for i, r in enumerate(pop, 1):
            w.writerow([i, r["sid"], r["arxiv"], r["title"]])
    print(f"population {len(pop)} (both screeners pass, with arXiv ID); order written, seed {SEED}")


SCRIPT = re.compile(r"<(script|style|nav|header|footer)[^>]*>.*?</\1>", re.S | re.I)
BLOCK = re.compile(r"</?(p|div|section|h[1-6]|li|tr|table|figcaption|br|caption)[^>]*>", re.I)
TAG = re.compile(r"<[^>]+>")


def to_text(raw: str) -> str:
    s = SCRIPT.sub(" ", raw)
    s = BLOCK.sub("\n", s)
    s = re.sub(r"</t[dh]>", " | ", s, flags=re.I)
    s = html.unescape(TAG.sub(" ", s))
    lines = [" ".join(l.split()) for l in s.splitlines()]
    return "\n".join(l for l in lines if l)


def fetch_one(aid: str) -> str | None:
    f = HTML / f"{aid}.html"
    if f.exists():
        return f.read_text(encoding="utf-8", errors="replace") or None
    req = urllib.request.Request(f"https://arxiv.org/html/{aid}", headers={"User-Agent": "dlm-review-census/0.1"})
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
                f.write_text("", encoding="utf-8")
                time.sleep(3)
                return None
            if e.code not in (429, 503):
                return None
        except (urllib.error.URLError, TimeoutError):
            continue
    return None


def fetch(first: int):
    TEXT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(OUT / "census-order.csv", encoding="utf8")))[:first]
    status = []
    for r in rows:
        t = TEXT / f"{r['arxiv']}.txt"
        if not t.exists():
            raw = fetch_one(r["arxiv"])
            if raw:
                t.write_text(to_text(raw), encoding="utf8")
        status.append({"rank": r["rank"], "arxiv": r["arxiv"], "text": t.exists(),
                       "chars": t.stat().st_size if t.exists() else 0})
    (OUT / "fetch-status.json").write_text(json.dumps(status, indent=1), encoding="utf8")
    ok = sum(s["text"] for s in status)
    print(f"texts available for {ok} of the first {len(rows)} in order (no HTML rendering: {len(rows) - ok})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["order", "fetch"])
    ap.add_argument("--first", type=int, default=220)
    a = ap.parse_args()
    order() if a.cmd == "order" else fetch(a.first)
