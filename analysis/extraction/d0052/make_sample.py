"""D0052 extraction sample: positions 1..27 of each gate list (draw_pilot.py gate manifest), the 8-record second-reader
subset (random.Random(20266300).sample(sorted(ids), 8)), and session batches by the ex_dispatch.py size rule.
    python -I analysis/extraction/d0052/make_sample.py
Writes analysis/extraction/d0052/sample.json and batches/*.ids. Python 3.14.3 (random.sample pinned by version).
"""
import hashlib, json, random, sys, platform
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "analysis/extraction/d0052"
MD = ROOT / "research/sources/md/fulltext-pymupdf"
LARGE = 133280
assert platform.python_version() == "3.14.3", platform.python_version()
g = json.loads((D / "gate-manifest.json").read_text(encoding="utf-8"))
sa = json.loads((D / "stage-a-manifest.json").read_text(encoding="utf-8"))
N = 27
strata = {s: g["lists"][s][:N] for s in g["lists"]}
ids = sorted(i for s in strata for i in strata[s])
assert len(ids) == len(set(ids)) == 3 * N
sizes = {i: (MD / f"{i}.txt").stat().st_size for i in ids}
check = sorted(random.Random(20266300).sample(ids, 8))
# stratum sizes after the stage-a exclusions, from the manifest
Nh = {s: g.get("strata_sizes", {}).get(s) for s in strata}
out = {"decision": "D0052", "gate_manifest_sha256": hashlib.sha256((D / "gate-manifest.json").read_bytes()).hexdigest(),
       "stage_a_ids": sa["ids"], "per_stratum": N, "strata": strata, "stratum_available": g.get("available"),
       "ids": ids, "ids_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
       "second_reader_seed": 20266300, "second_reader_ids": check,
       "text_bytes": sizes, "large": sorted(i for i in ids if sizes[i] > LARGE)}
# batches (v2, 2026-10-20): phase 1 = positions 1..20 of each list, phase 2 = positions 21..27, so phase 1 is complete
# before any phase-2 record (keeps a 20-per-stratum design open while the human author decides on a seed stratum);
# strata interleaved round robin; texts above LARGE alone, others in pairs, in list order within a stratum.
def pairs(lst):
    out, pend = [], []
    for i in lst:
        if sizes[i] > LARGE:
            out.append([i])
        else:
            pend.append(i)
            if len(pend) == 2:
                out.append(pend); pend = []
    if pend:
        out.append(pend)
    return out
batches = []
for lo, hi in ((0, 20), (20, N)):
    per = [pairs(strata[s][lo:hi]) for s in sorted(strata)]
    for k in range(max(map(len, per))):
        for b in per:
            if k < len(b):
                batches.append(b[k])
bd = D / "batches"; bd.mkdir(exist_ok=True)
for f in bd.glob("exs*.ids"):
    f.unlink()   # v1 batch names; exs001, exs002 folders were built but never launched (dispatch-log)
names = []
for n, b in enumerate(batches, 1):
    name = f"exb{n:03d}"; names.append(name)
    (bd / f"{name}.ids").write_text("\n".join(b) + "\n", encoding="utf-8")
out["batches"] = dict(zip(names, batches))
out["phase1_batches"] = [n for n, b in zip(names, batches) if all(strata[s].index(i) < 20 for i in b for s in strata if i in strata[s])]
(D / "sample.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("sample", len(ids), "large", len(out["large"]), "batches", len(batches), "check", check)
print({s: len(v) for s, v in strata.items()}, "available", g.get("available"))
