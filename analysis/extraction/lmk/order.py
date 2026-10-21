"""Seeded extraction order for the landmark tranche (D0061; scope set by the user: "Extract till 90 percent").

    python -I analysis/extraction/lmk/order.py

Frame: every include of analysis/screening/ft-lmk/lmk-decisions-all.jsonl that is not non-language only (as the
D0052 frames). Order: random.Random(20261024).shuffle(sorted(ids)), fixed before any extraction session starts. One
study per session (batch lmx<NNN> = position NNN), so the extracted set is always a prefix of this order; blocks
L, Q, H, K for every study (as the seed stratum). Second reader and adjudicator: the first max(2, ceil(n/10))
positions of random.Random(20261025).shuffle over the extracted prefix, drawn after the stop point is known.
Writes analysis/extraction/lmk/extraction-order.json (refuses to overwrite) and batches/lmx<NNN>.ids.
"""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = Path(__file__).resolve().parent
out = D / "extraction-order.json"
if out.exists():
    raise SystemExit("extraction-order.json exists; the order is fixed")
rows = [json.loads(l) for l in open(ROOT / "analysis/screening/ft-lmk/lmk-decisions-all.jsonl", encoding="utf-8") if l.strip()]
ids = sorted(r["id"] for r in rows if r["decision"] == "include" and not r["nonlang_only"])
order = list(ids)
random.Random(20261024).shuffle(order)
txt = ROOT / "research/sources/md/fulltext-pymupdf"
(D / "batches").mkdir(exist_ok=True)
for k, i in enumerate(order, 1):
    (D / "batches" / f"lmx{k:03d}.ids").write_text(i + "\n", encoding="utf-8")
doc = {"decision": "D0061 (extraction scope: user 'Extract till 90 percent', relayed 2026-10-21)", "seed": 20261024,
       "frame": "includes of lmk-decisions-all.jsonl, nonlang_only false", "N": len(ids),
       "frame_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(), "order": order,
       "bytes": {i: (txt / f"{i}.txt").stat().st_size for i in order},
       "batches": {f"lmx{k:03d}": [i] for k, i in enumerate(order, 1)}, "blocks": "LQHK",
       "second_reader_rule": "random.Random(20261025).shuffle(extracted prefix); first max(2, ceil(n/10))"}
out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in doc.items() if k not in ("bytes", "batches")}))
