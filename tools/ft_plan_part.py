"""Write the next T1 full-text batch plan: every record of ft-routes.jsonl or analysis/screening/ft-routes-extra.jsonl
that has a converted text (research/sources/md/fulltext-pymupdf/<id>.txt) and is in no earlier
t1-batches-part*.json plan, shuffled with random.Random(seed) and cut into batches of SIZE. Re-check, C8 and
title/abstract-pass records are mixed in one order with no flag (criteria v1.6 A s5.1 'Dispatch').

    python tools/ft_plan_part.py <part number> <first batch number> <seed> [size, default 10]
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FT = ROOT / "research/review/fulltext"
TXT = ROOT / "research/sources/md/fulltext-pymupdf"

part, first, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
size = int(sys.argv[4]) if len(sys.argv) > 4 else 10
out = FT / f"t1-batches-part{part}.json"
if out.exists():
    sys.exit(f"{out.name} exists; plans are never rewritten")
planned = set()
for p in FT.glob("t1-batches-part*.json"):
    for ids in json.loads(p.read_text(encoding="utf-8"))["batches"].values():
        planned.update(ids)
ids = set()
for table in (FT / "ft-routes.jsonl", ROOT / "analysis/screening/ft-routes-extra.jsonl"):
    for line in open(table, encoding="utf-8"):
        if line.strip():
            i = json.loads(line)["id"]
            if (TXT / f"{i}.txt").exists() and i not in planned:
                ids.add(i)
ids = sorted(ids)
random.Random(seed).shuffle(ids)
batches = {f"t1b{first + k:03d}": ids[k * size:(k + 1) * size] for k in range((len(ids) + size - 1) // size)}
out.write_text(json.dumps({"tranche": "T1", "part": "texts retrieved 2026-10-17 (open access, OpenReview API, "
                           "e-gateway IEEE, OA retry; not yet in any plan)", "seed": seed, "n": len(ids),
                           "batches": batches}, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"n": len(ids), "batches": len(batches), "first": min(batches), "last": max(batches)}))
