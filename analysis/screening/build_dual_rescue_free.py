"""Dual title/abstract screening batches for the free-source rescue positives (D0036, 2026-10-20).

D0036: the 348 free-source rescue positives (Haiku rescue pass, D0029; include or unclear) get dual
title/abstract screening (A Sonnet, B Opus) as was done for the subscription rescue
(build_dual_subscription.py). The subscription strand screened only records with an abstract and held the
others in pending-no-abstract.txt; the same split is made here: records with an abstract go to the dual
batches, records without one are listed in pending-no-abstract-rf.jsonl until the human author decides
their route (EVENING page).

Input:  research/review/screening/v2/rescue/screener-R-rescue-*.jsonl and rescue-0*.jsonl ({id, title, abstract})
Output: research/review/screening/v2/dual-rescue-free/batch-rf-NN.jsonl ({id, title, abstract}; seeded shuffle,
        at most SIZE records per batch), pending-no-abstract-rf.jsonl, manifest.json (sha256 per batch).

    python -I analysis/screening/build_dual_rescue_free.py
"""
import glob, hashlib, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "research/review/screening/v2"
OUT = V2 / "dual-rescue-free"
SEED, SIZE = 20261026, 70     # seeds 20261022-20261025 are used by earlier v2 steps


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


R = [r for p in sorted(glob.glob(str(V2 / "rescue/screener-R-rescue-*.jsonl"))) for r in jl(p)]
rec = {r["id"]: r for p in sorted(glob.glob(str(V2 / "rescue/rescue-0*.jsonl"))) for r in jl(p)}
pos = sorted(r["id"] for r in R if r["decision"] != "exclude")
assert len(pos) == len(set(pos)) and set(pos) <= set(rec)
with_abs = [i for i in pos if (rec[i].get("abstract") or "").strip()]
no_abs = [i for i in pos if i not in set(with_abs)]
ids = list(with_abs)
random.Random(SEED).shuffle(ids)
OUT.mkdir(exist_ok=True)
man = {"seed": SEED, "decision": "D0036", "source": "research/review/screening/v2/rescue/ (Haiku rescue pass, D0029)",
       "n_rescue_positives": len(pos), "n_with_abstract": len(with_abs), "n_without_abstract": len(no_abs),
       "batches": {}}
for k in range(0, len(ids), SIZE):
    name = f"batch-rf-{k // SIZE + 1:02d}.jsonl"
    text = "".join(json.dumps({"id": i, "title": rec[i]["title"], "abstract": rec[i]["abstract"]}, ensure_ascii=False) + "\n"
                   for i in ids[k:k + SIZE])
    (OUT / name).write_text(text, encoding="utf-8")
    man["batches"][name] = {"n": len(ids[k:k + SIZE]), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
rdec = {r["id"]: r["decision"] for r in R}
(OUT / "pending-no-abstract-rf.jsonl").write_text(
    "".join(json.dumps({"id": i, "title": rec[i]["title"], "rescue_decision": rdec[i]}, ensure_ascii=False) + "\n" for i in no_abs),
    encoding="utf-8")
(OUT / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
print(json.dumps(man, indent=1))
