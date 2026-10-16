"""Rescue-pass batches (D0029 design) for the subscription-database records that fail S1''/S2''.

Input:  research/review/corpus/subscription-records-2026-10-15.jsonl (status 'new, fails S1''/S2'' ...')
Output: research/review/screening/v2/rescue-subscription/rescue-sub-0N.jsonl ({id, title, abstract}) + manifest.json
Order is a seeded shuffle (seed 20261024) so batch position carries no information.
"""
import hashlib, json, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/review/corpus/subscription-records-2026-10-15.jsonl"
OUT = ROOT / "research/review/screening/v2/rescue-subscription"
SEED, PER = 20261024, 910

rows = [json.loads(l) for l in SRC.read_text(encoding="utf8").splitlines() if l.strip()]
fails = sorted((r for r in rows if r["status"].startswith("new, fails S1''/S2''")), key=lambda r: r["id"])
random.Random(SEED).shuffle(fails)
OUT.mkdir(parents=True, exist_ok=True)
man = {"seed": SEED, "source": SRC.relative_to(ROOT).as_posix(), "n": len(fails), "batches": {}}
for i in range(0, len(fails), PER):
    name = f"rescue-sub-{i // PER + 1:02d}.jsonl"
    text = "".join(json.dumps({"id": r["id"], "title": r["title"], "abstract": r["abstract"]}, ensure_ascii=False) + "\n" for r in fails[i:i + PER])
    (OUT / name).write_text(text, encoding="utf8")
    man["batches"][name] = {"n": len(fails[i:i + PER]), "sha256": hashlib.sha256(text.encode("utf8")).hexdigest()}
(OUT / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf8")
print(json.dumps(man, indent=1))
