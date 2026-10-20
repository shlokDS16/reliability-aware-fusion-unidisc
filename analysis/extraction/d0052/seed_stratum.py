"""D0053 (option A): seed stratum of the extraction sample, and the 80-record design.

    python -I analysis/extraction/d0052/seed_stratum.py

Frame: the census sample's full-text-eligible records (research/review/census/census-random-final.jsonl, eligible
'yes', 167), a simple random sample (seed 20261015, ranks 1-176) of the 1,106 seed records that both title/abstract
screeners passed and that have an arXiv identifier. Draw: random.Random(20266400).sample(sorted(sids), 20).
Texts: the census's own arXiv HTML texts (main checkout research/sources/census-text/<arxiv>.txt, written by
tools/census_sample.py), copied with one leading '=== page 1 ===' marker (HTML has no pages) to
research/sources/md/census-text-paged/<sid>.txt; sha256 of source and copy recorded.
The update strata keep positions 1-20 of each gate list (60); positions 21-27 are dropped. Second reader: 8 ids,
random.Random(20266300).sample(sorted(80 ids), 8), replacing the D0052 draw over 81 (no second-reader session had run).
Batches: update phase-1 batches exb001-exb033 unchanged; seed batches exc001.. (texts above 133,280 bytes alone,
others in pairs, in draw order). Writes analysis/extraction/d0052/seed-sample.json and batches/exc*.ids.
"""
import hashlib
import json
import platform
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "analysis/extraction/d0052"
SRC = Path(r"C:/Users/Shlok/Downloads/Multi-Modality Language model/research/sources/census-text")
OUT = ROOT / "research/sources/md/census-text-paged"
LARGE = 133280
assert platform.python_version() == "3.14.3"
rows = [json.loads(l) for l in open(ROOT / "research/review/census/census-random-final.jsonl", encoding="utf-8") if l.strip()]
assert len(rows) == 176
elig = {r["sid"]: r["arxiv"] for r in rows if r["eligible"] == "yes"}
assert len(elig) == 167
t1 = {json.loads(l)["id"] for l in open(ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl", encoding="utf-8")}
r7 = {json.loads(l)["id"] for l in open(ROOT / "analysis/screening/ft-r797/r797-decisions-all.jsonl", encoding="utf-8")}
assert not set(elig) & (t1 | r7), "census record also screened at full text"
pick = random.Random(20266400).sample(sorted(elig), 20)
OUT.mkdir(parents=True, exist_ok=True)
prov = {}
for s in pick:
    src = SRC / f"{elig[s]}.txt"
    assert src.exists(), src
    b = src.read_bytes()
    (OUT / f"{s}.txt").write_bytes(b"=== page 1 ===\n" + b)
    prov[s] = {"arxiv": elig[s], "source": str(src), "source_sha256": hashlib.sha256(b).hexdigest(),
               "copy_sha256": hashlib.sha256((OUT / f"{s}.txt").read_bytes()).hexdigest(), "bytes": len(b)}
sample = json.load(open(D / "sample.json", encoding="utf-8"))
upd = {h: v[:20] for h, v in sample["strata"].items()}
ids80 = sorted([i for v in upd.values() for i in v] + pick)
assert len(set(ids80)) == 80
check = sorted(random.Random(20266300).sample(ids80, 8))
batches, pend = [], []
for s in pick:
    if prov[s]["bytes"] > LARGE:
        batches.append([s])
    else:
        pend.append(s)
        if len(pend) == 2:
            batches.append(pend)
            pend = []
if pend:
    batches.append(pend)
for n, b in enumerate(batches, 1):
    (D / "batches" / f"exc{n:03d}.ids").write_text("\n".join(b) + "\n", encoding="utf-8")
out = {"decision": "D0053", "frame": "census eligible 167 (random sample of the 1,106 both-pass seed records with an arXiv id)",
       "frame_ids_sha256": hashlib.sha256("\n".join(sorted(elig)).encode()).hexdigest(), "seed": 20266400,
       "seed_ids": pick, "provenance": prov, "update_strata_positions_1_20": upd, "ids80": ids80,
       "second_reader_seed": 20266300, "second_reader_ids": check,
       "batches": {f"exc{n:03d}": b for n, b in enumerate(batches, 1)},
       "census_pool": 1106, "census_ranks": 176, "census_no_text": 4, "census_eligible": 167}
(D / "seed-sample.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("seed ids", pick)
print("second reader", check)
print("seed batches", len(batches), {k: v for k, v in out["batches"].items()})
