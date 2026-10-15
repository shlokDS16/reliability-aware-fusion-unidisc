"""Screening batches for the 2026-10-15 search update (D0026, D0027, D0028).

Queue = records passing S1''/S2'' (screening-queue-final-2026-10-15.jsonl) plus auto-excluded records
that match the protocol's original strings S1 or S2 (released by D0028). Writes shuffled batches of
at most 500 records (id, title, abstract only: screeners see nothing else) to
research/review/screening/v2/batch-NN.jsonl and a manifest with SHA-256.

    python tools/make_screening_batches_v2.py
"""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COR = ROOT / "research" / "review" / "corpus"
OUT = ROOT / "research" / "review" / "screening" / "v2"
SEED, SIZE = 20261022, 500


def rows(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


queue = rows(COR / "screening-queue-final-2026-10-15.jsonl")
released = [r for r in rows(COR / "auto-excluded-2026-10-15.jsonl")
            if r["string_match"].get("S1") or r["string_match"].get("S2")]
ids = {r["id"] for r in queue}
assert not ids & {r["id"] for r in released}
allrec = queue + released
random.Random(SEED).shuffle(allrec)
OUT.mkdir(parents=True, exist_ok=True)
man = dict(seed=SEED, n_queue=len(queue), n_released_S1_S2=len(released), n_total=len(allrec), batches={})
for i in range(0, len(allrec), SIZE):
    name = f"batch-{i // SIZE + 1:02d}.jsonl"
    text = "".join(json.dumps(dict(id=r["id"], title=r["title"], abstract=r.get("abstract") or ""), ensure_ascii=False) + "\n"
                   for r in allrec[i:i + SIZE])
    (OUT / name).write_text(text, encoding="utf-8")
    man["batches"][name] = dict(n=len(allrec[i:i + SIZE]), sha256=hashlib.sha256(text.encode()).hexdigest())
(OUT / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in man.items() if k != "batches"}), {k: v["n"] for k, v in man["batches"].items()})
