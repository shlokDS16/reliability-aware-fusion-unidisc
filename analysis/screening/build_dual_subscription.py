"""Dual title/abstract screening batch for the subscription-database update (D0030 rule).

Inputs: research/review/screening/v2/subscription-queue.jsonl (string passes) and
        research/review/screening/v2/rescue-subscription/rescued-queue.jsonl (rescue include/unclear).
Output: research/review/screening/v2/dual-subscription/batch-sub-01.jsonl ({id, title, abstract}), seeded shuffle, + manifest.json
"""
import hashlib, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "research/review/screening/v2"
SEED = 20261025
srcs = {"string-pass": V2 / "subscription-queue.jsonl", "rescued": V2 / "rescue-subscription/rescued-queue.jsonl"}
rows, origin = {}, {}
for k, p in srcs.items():
    for l in p.read_text(encoding="utf8").splitlines():
        if l.strip():
            r = json.loads(l)
            assert r["id"] not in rows, r["id"]
            rows[r["id"]] = {"id": r["id"], "title": r["title"], "abstract": r["abstract"]}
            origin[r["id"]] = k
ids = sorted(rows)
random.Random(SEED).shuffle(ids)
out = V2 / "dual-subscription"
out.mkdir(exist_ok=True)
text = "".join(json.dumps(rows[i], ensure_ascii=False) + "\n" for i in ids)
(out / "batch-sub-01.jsonl").write_text(text, encoding="utf8")
man = {"seed": SEED, "sources": {k: str(p.relative_to(ROOT).as_posix()) for k, p in srcs.items()},
       "n": len(ids), "by_origin": {k: sum(1 for i in ids if origin[i] == k) for k in srcs},
       "batch-sub-01.jsonl": hashlib.sha256(text.encode("utf8")).hexdigest(), "origin": origin}
(out / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf8")
print({k: v for k, v in man.items() if k != "origin"})
