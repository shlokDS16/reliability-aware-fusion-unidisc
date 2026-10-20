"""Draw the human-validation sample of a later full-text tranche (criteria v1.6 audit copy s4 item 6, "Tranches";
protocol s4 step 3) BEFORE any screener row of the tranche exists.

Rule (criteria v1.6 s4 item 6): simple random sample, seed 20261016, over the tranche's ids sorted, 15 percent
(ceil); the minimum of 100 applies to T1 only. Frame: the tranche's full-text set as fixed by its decision row
(every record the tranche screens, whether or not its text has been retrieved yet), so the draw never has to be
redone when texts arrive later (T1 needed extra draws for late arrivals). Sampled records whose text is never
retrieved are reported as such.

    python -I analysis/screening/human_validation_draw.py --tranche R797 --frame <file, one id per line> --decision D0035

Writes research/review/screening/human-validation-<tranche>/sample-manifest.json and sample-ids.txt. Refuses to
overwrite an existing manifest and refuses to draw if any screener row of the tranche exists
(analysis/screening/ft-<tranche lower>/).
"""
import argparse, hashlib, json, math, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261016
ap = argparse.ArgumentParser()
ap.add_argument("--tranche", required=True)
ap.add_argument("--frame", required=True)
ap.add_argument("--decision", required=True)
a = ap.parse_args()
out = ROOT / f"research/review/screening/human-validation-{a.tranche.lower()}"
if (out / "sample-manifest.json").exists():
    raise SystemExit(f"{out}/sample-manifest.json exists: the draw is frozen")
rows_dir = ROOT / f"analysis/screening/ft-{a.tranche.lower()}"
if rows_dir.exists() and any(rows_dir.rglob("F[ABC]-*.jsonl")):
    raise SystemExit(f"screener rows already exist under {rows_dir}: drawing now would break the blind rule")
frame = sorted({l.strip() for l in open(a.frame, encoding="utf-8") if l.strip()})
k = math.ceil(0.15 * len(frame))
sample = sorted(random.Random(SEED).sample(frame, k))
out.mkdir(parents=True, exist_ok=True)
(out / "sample-ids.txt").write_text("\n".join(sample) + "\n", encoding="utf-8")
man = {"tranche": a.tranche, "decision": a.decision, "frame_file": str(Path(a.frame).resolve().relative_to(ROOT)).replace("\\", "/"),
       "frame_note": "the tranche's full-text set as fixed by the decision row, before retrieval and before any screener row",
       "frame_n": len(frame), "frame_sha256": hashlib.sha256("\n".join(frame).encode()).hexdigest(), "seed": SEED,
       "rule": "random.Random(seed).sample(sorted frame ids, ceil(0.15 N)) (criteria v1.6 s4 item 6; minimum 100 is for T1 only)",
       "k": k, "sample_sha256": hashlib.sha256("\n".join(sample).encode()).hexdigest()}
(out / "sample-manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
print(json.dumps(man, indent=1))
