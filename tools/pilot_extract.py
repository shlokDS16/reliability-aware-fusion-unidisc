"""H2 pilot sample: inference papers whose captions pair a cost with a task-quality outcome.

    python tools/pilot_extract.py [--n 15]

Fixed-seed sample from the Inference Optimization section, excluding papers already read in
stage 2. Writes one extract per paper (abstract plus every table whose caption or cells mention
steps, forward passes, speed or throughput) to research/review/pilot/papers/ and a manifest.
"""
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

import stage2_extract as s2

ROOT = s2.ROOT
OUT = ROOT / "research" / "review" / "pilot"
COST = re.compile(r"\bNFEs?\b|speed-?up|faster|throughput|tokens?/s|\bTPS\b|latency|\bsteps?\b", re.I)
QUAL = re.compile(r"accuracy|GSM8K|HumanEval|MBPP|MATH|pass@1|\bacc\b|score", re.I)


def blocks(text: str) -> list[str]:
    spans, out, seen = s2.figure_spans(text), [], set()
    for m in s2.CAP.finditer(text):
        cap = s2.clean(m.group(1))
        inner = min((s for s in spans if s[0] <= m.start() < s[1]), key=lambda s: s[1] - s[0], default=None)
        if inner is None or inner in seen:
            continue
        rows = [" | ".join(s2.clean(c) for c in s2.CELL.findall(r)) for r in s2.ROW.findall(text[inner[0]:inner[1]])]
        rows = [r for r in rows if r.strip(" |")]
        body = "\n".join(rows[:70])[:7000]
        if not (COST.search(cap) or COST.search(body[:1500])):
            continue
        seen.add(inner)
        out.append(f"### {cap[:400]}\n\n{body or '(figure or image: numbers not in HTML)'}\n")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=15)
    a = ap.parse_args()
    rows = [json.loads(x) for x in (s2.FEAS / "captions.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    done = set()
    for f in (s2.OUT).glob("batch-*.json"):
        done |= {m["record_id"] for m in json.loads(f.read_text(encoding="utf-8"))}
    pool = sorted((r for r in rows if r["has_html"] and "Inference Optimization" in r["sections"]
                   and r["record_id"] not in done
                   and any(c["kind"] == "table" and COST.search(c["text"]) and QUAL.search(c["text"])
                           for c in r["captions"])), key=lambda r: r["record_id"])
    sample = random.Random(s2.SEED + 1).sample(pool, min(a.n, len(pool)))
    corpus = {}
    for f in (ROOT / "research" / "review" / "corpus").glob("awesome-dlms@*.jsonl"):
        for x in f.read_text(encoding="utf-8").splitlines():
            if x.strip():
                r = json.loads(x)
                corpus[r["record_id"]] = r
    (OUT / "papers").mkdir(parents=True, exist_ok=True)
    manifest = []
    for r in sample:
        text = (s2.CACHE / f"{r['arxiv']}.html").read_text(encoding="utf-8", errors="replace")
        bl = blocks(text)
        meta = corpus.get(r["record_id"], {}).get("arxiv") or {}
        md = OUT / "papers" / f"{r['record_id']}_{r['arxiv']}.md"
        md.write_text(f"# {r['title']}\n\narXiv:{r['arxiv']} | record {r['record_id']} | first version "
                      f"{str(meta.get('published'))[:10]}\n\n**Abstract.** {meta.get('abstract', '(missing)')}\n\n"
                      "## Tables and figures mentioning cost\n\n" + ("\n".join(bl) or "(none)") + "\n", encoding="utf-8")
        manifest.append({"record_id": r["record_id"], "arxiv": r["arxiv"], "title": r["title"],
                         "file": str(md.relative_to(ROOT)).replace("\\", "/"), "blocks": len(bl),
                         "chars": md.stat().st_size, "html": f"research/sources/html/{r['arxiv']}.html"})
    (OUT / "batch.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"eligible pool: {len(pool)}  sampled: {len(manifest)}  blocks: {sum(m['blocks'] for m in manifest)}  "
          f"chars: {sum(m['chars'] for m in manifest) // 1000} k")


if __name__ == "__main__":
    main()
