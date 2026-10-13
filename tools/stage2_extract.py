"""Stage-2 feasibility sample: pick flagged papers and cut out their flagged tables as text.

    python tools/stage2_extract.py

Reads research/review/feasibility/captions.jsonl and the cached arXiv HTML. Draws a fixed-seed
stratified sample (30 step-sweep papers across README sections, 15 remasking, all synergy), writes
one compact markdown file per paper under research/review/feasibility/stage2/papers/ containing
the abstract and every flagged table (caption plus cell text) and flagged figure caption, and
writes two batch manifests for the reading agents.
"""
from __future__ import annotations

import html
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEAS = ROOT / "research" / "review" / "feasibility"
CACHE = ROOT / "research" / "sources" / "html"
OUT = FEAS / "stage2"
SEED = 20261013
STEP_QUOTA = {"Inference Optimization": 12, "Discrete DLMs": 8, "Training Strategies": 3,
              "Continuous DLMs": 3, "Multimodal DLMs": 4}
MATH = re.compile(r'<math[^>]*?alttext="([^"]*)"[^>]*>.*?</math>', re.S)
TAG = re.compile(r"<[^>]+>")
FIG = re.compile(r"<(/?)figure\b[^>]*>", re.I)
CAP = re.compile(r"<figcaption[^>]*>(.*?)</figcaption>", re.S | re.I)
ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S | re.I)
CELL = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.S | re.I)
WANT = re.compile(r"ablat|w/o\b|without\b|effect of|impact of|\bsteps?\b|\bNFEs?\b|function evaluations|"
                  r"re-?mask|synerg|joint training|understanding and generation", re.I)


def clean(s: str) -> str:
    return " ".join(html.unescape(TAG.sub(" ", MATH.sub(lambda m: f" {m.group(1)} ", s))).split())


def figure_spans(text: str) -> list[tuple[int, int]]:
    spans, stack = [], []
    for m in FIG.finditer(text):
        if m.group(1):
            if stack:
                spans.append((stack.pop(), m.end()))
        else:
            stack.append(m.start())
    return spans


def flagged_blocks(text: str) -> list[str]:
    spans, out, seen = figure_spans(text), [], set()
    for m in CAP.finditer(text):
        cap = clean(m.group(1))
        if not WANT.search(cap):
            continue
        inner = min((s for s in spans if s[0] <= m.start() < s[1]), key=lambda s: s[1] - s[0], default=None)
        if inner is None or inner in seen:
            continue
        seen.add(inner)
        rows = [" | ".join(clean(c) for c in CELL.findall(r)) for r in ROW.findall(text[inner[0]:inner[1]])]
        rows = [r for r in rows if r.strip(" |")]
        body = "\n".join(rows[:60])[:6000] if rows else "(no table cells in HTML: figure or image; numbers not extractable from HTML)"
        out.append(f"### {cap[:400]}\n\n{body}\n")
    return out


def main() -> None:
    rng = random.Random(SEED)
    rows = [json.loads(x) for x in (FEAS / "captions.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    rows = [r for r in rows if r["has_html"]]
    corpus = {}
    for f in (ROOT / "research" / "review" / "corpus").glob("awesome-dlms@*.jsonl"):
        for x in f.read_text(encoding="utf-8").splitlines():
            if x.strip():
                r = json.loads(x)
                corpus[r["record_id"]] = r
    chosen: dict[str, str] = {}
    for sec, k in STEP_QUOTA.items():
        pool = sorted((r for r in rows if r["flags"].get("steps") and sec in r["sections"]
                       and r["record_id"] not in chosen), key=lambda r: r["record_id"])
        for r in rng.sample(pool, min(k, len(pool))):
            chosen[r["record_id"]] = "steps"
    for r in sorted((r for r in rows if r["flags"].get("synergy")), key=lambda r: r["record_id"]):
        chosen.setdefault(r["record_id"], "synergy")
    pool = sorted((r for r in rows if r["flags"].get("remask") and r["record_id"] not in chosen),
                  key=lambda r: r["record_id"])
    for r in rng.sample(pool, min(15, len(pool))):
        chosen[r["record_id"]] = "remask"
    (OUT / "papers").mkdir(parents=True, exist_ok=True)
    by_id = {r["record_id"]: r for r in rows}
    manifest = []
    for rid, stratum in chosen.items():
        r = by_id[rid]
        text = (CACHE / f"{r['arxiv']}.html").read_text(encoding="utf-8", errors="replace")
        blocks = flagged_blocks(text)
        meta = (corpus.get(rid, {}).get("arxiv") or {})
        md = OUT / "papers" / f"{rid}_{r['arxiv']}.md"
        md.write_text(f"# {r['title']}\n\narXiv:{r['arxiv']} | record {rid} | stratum {stratum} | "
                      f"first version {str(meta.get('published'))[:10]} | sections {', '.join(r['sections'])}\n\n"
                      f"**Abstract.** {meta.get('abstract', '(missing)')}\n\n## Flagged tables and figures\n\n"
                      + ("\n".join(blocks) or "(none extracted)") + "\n", encoding="utf-8")
        manifest.append({"record_id": rid, "arxiv": r["arxiv"], "stratum": stratum, "title": r["title"],
                         "file": str(md.relative_to(ROOT)).replace("\\", "/"), "blocks": len(blocks),
                         "chars": md.stat().st_size, "html": f"research/sources/html/{r['arxiv']}.html"})
    a = [m for m in manifest if m["stratum"] == "steps"]
    b = [m for m in manifest if m["stratum"] != "steps"]
    (OUT / "batch-steps.json").write_text(json.dumps(a, indent=1), encoding="utf-8")
    (OUT / "batch-remask-synergy.json").write_text(json.dumps(b, indent=1), encoding="utf-8")
    for name, batch in (("steps", a), ("remask+synergy", b)):
        print(f"{name}: {len(batch)} papers, {sum(m['blocks'] for m in batch)} blocks, "
              f"{sum(m['chars'] for m in batch) // 1000} k chars, "
              f"{sum(1 for m in batch if m['blocks'] == 0)} with no block")
    print("strata:", {s: sum(1 for m in manifest if m['stratum'] == s) for s in ('steps', 'remask', 'synergy')})


if __name__ == "__main__":
    main()
