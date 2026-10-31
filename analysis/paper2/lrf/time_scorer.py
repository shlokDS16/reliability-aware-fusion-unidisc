"""CPU wall time of the pinned LRF scorer on the stored L1 arrays (triage F2). Re-scores runs/P2-LRF-L1 into a temporary file (the run's own predictions are not touched),
checks that the re-scored lines equal the stored predictions, and writes runs/P2-LRF-TIMING/scorer_timing.json. Wall time includes interpreter start-up and file reading.

    "C:/.../.venv/Scripts/python.exe" analysis/paper2/lrf/time_scorer.py [--repeats 3]"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args(argv)
    ref = sorted(l for l in (ROOT / "runs" / "P2-LRF-L1" / "predictions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())
    times = []
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "pred.jsonl"
        cmd = [sys.executable, "-m", "exp_p2.gate.lrf_score", "--run-id", "P2-LRF-L1", "--pins", "runs/P2-LRF-PINS/pins.json", "--out", str(out)]
        for _ in range(a.repeats):
            for f in (out, out.parent / "lrf_score_meta.json"):
                f.unlink(missing_ok=True)
            t0 = time.perf_counter()
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=dict(os.environ, CUDA_VISIBLE_DEVICES=""))
            times.append(time.perf_counter() - t0)
            if r.returncode != 0:
                print("STOP: scorer exit", r.returncode, r.stderr[-800:], file=sys.stderr)
                return 2
            got = sorted(l for l in out.read_text(encoding="utf-8").splitlines() if l.strip())
            if got != ref:
                print("STOP: re-scored predictions differ from runs/P2-LRF-L1/predictions.jsonl", file=sys.stderr)
                return 2
    n = len(ref)
    med = statistics.median(times)
    rec = dict(what="pinned LRF scorer (exp_p2.gate.lrf_score) on the stored arrays of runs/P2-LRF-L1, CPU only, including interpreter start-up and file reading",
               n_decisions=n, n_items=450, n_conditions=n // 450, wall_s=times, median_wall_s=med, ms_per_decision=1000 * med / n,
               identical_to_stored=True, cpu=platform.processor(), python=platform.python_version(), machine="the authors' laptop (RTX 5070 Ti laptop GPU unused)")
    d = ROOT / "runs" / "P2-LRF-TIMING"
    d.mkdir(parents=True, exist_ok=True)
    (d / "scorer_timing.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("n_decisions", "median_wall_s", "ms_per_decision")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
