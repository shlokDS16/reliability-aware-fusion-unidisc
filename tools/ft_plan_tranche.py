"""Write the next full-text batch plan of a later tranche (R797, D0035; S1243, D0037), as tools/ft_plan_part.py does
for T1: every tranche id with a converted text that passed the title check and is in no earlier plan of the tranche,
shuffled with random.Random(seed), cut into batches of SIZE. Nothing in a batch says why a record is there.

Biology-heavy records (title or first 3,000 characters match BIO) go into their own batches of BIO_SIZE, placed in
the same shuffled order: Screener B (claude-opus-5-5) hit a safety-classifier stop on such papers in T1 and the
harness then continues on another model (criteria v1.6 s4 item 1 forbids that; memory screener-model-fallback), so
small batches keep a stop from voiding rows of other records. Records B cannot screen go to the human author
(D0041). The plan lists which batches are bio batches (orchestrator file; screeners never see it).

    python -I tools/ft_plan_tranche.py <tranche: r797|s1243> <part> <first batch number> <seed> [size 10] [bio size 3]

Writes research/review/fulltext/<tranche>-batches-part<part>.json and tools/ft-session/<batch>.ids, and copies the
.ids files to the dispatch root given by FT_DISPATCH_ROOT if set. Plans are never rewritten.
"""
import json, os, random, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FT = ROOT / "research/review/fulltext"
TXT = ROOT / "research/sources/md/fulltext-pymupdf"
FRAMES = {"r797": ROOT / "analysis/screening/r797-tranche-ids.txt", "s1243": ROOT / "analysis/screening/s1243-tranche-ids.txt"}
BIO = re.compile(r"\b(protein|peptide|antibod\w*|enzyme|m?RNA|ncRNA|DNA|genom\w*|nucleotide|amino[- ]acid|"
                 r"molecul\w*|drug|ligand|biolog\w*|cell(?:s|ular)?|gene|virus|viral|pathogen|toxin)\b", re.I)

tr, part, first, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
size = int(sys.argv[5]) if len(sys.argv) > 5 else 10
bsize = int(sys.argv[6]) if len(sys.argv) > 6 else 3
out = FT / f"{tr}-batches-part{part}.json"
if out.exists():
    sys.exit(f"{out.name} exists; plans are never rewritten")
frame = set(FRAMES[tr].read_text(encoding="utf-8").split())
planned = set()
for p in FT.glob(f"{tr}-batches-part*.json"):
    for ids in json.loads(p.read_text(encoding="utf-8"))["batches"].values():
        planned.update(ids)
conv = {}
for l in open(FT / "convert-pymupdf-log.jsonl", encoding="utf-8"):
    r = json.loads(l); conv[r["id"]] = r["status"]
tc = json.loads((FT / "title-check.json").read_text(encoding="utf-8"))
flagged = {f["id"] for f in tc["flags"] if not f.get("verified")}
ready = sorted(i for i in frame - planned if conv.get(i) == "ok" and (TXT / f"{i}.txt").exists() and i not in flagged)
held = sorted(i for i in frame - planned if conv.get(i) == "ok" and i in flagged)
titles = {}
for t in ("analysis/screening/ft-routes-recheck797.jsonl", "analysis/screening/ft-routes-seed1243.jsonl"):
    for l in open(ROOT / t, encoding="utf-8"):
        r = json.loads(l); titles.setdefault(r["id"], r.get("title") or "")
bio = {i for i in ready if BIO.search(titles.get(i, "") + " " + (TXT / f"{i}.txt").read_text(encoding="utf-8", errors="replace")[:3000])}
random.Random(seed).shuffle(ready)
norm_ids, bio_ids = [i for i in ready if i not in bio], [i for i in ready if i in bio]
chunks = [norm_ids[k:k + size] for k in range(0, len(norm_ids), size)] + [bio_ids[k:k + bsize] for k in range(0, len(bio_ids), bsize)]
random.Random(seed + 1).shuffle(chunks)
batches = {f"{tr}b{first + k:03d}": c for k, c in enumerate(chunks)}
plan = {"tranche": tr.upper(), "part": part, "seed": seed, "size": size, "bio_size": bsize, "n": len(ready),
        "bio_batches": sorted(b for b, c in batches.items() if c and c[0] in bio),
        "held_title_check": held, "batches": batches}
out.write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8")
droot = os.environ.get("FT_DISPATCH_ROOT")
for b, c in batches.items():
    (ROOT / f"tools/ft-session/{b}.ids").write_text("\n".join(c) + "\n", encoding="utf-8")
    if droot:
        (Path(droot) / f"{b}.ids").write_text("\n".join(c) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in plan.items() if k != "batches"}), list(batches)[:3], "...", list(batches)[-1:])
