"""Chunk driver for a GPU stage under the GPU-safety regime of card 12.2.

Each chunk runs `python exp001/gate_gen.py ...` inside tools/gpu_guard.py (85 C stop after 3 hot readings, per-chunk time limit,
telemetry CSV per chunk). Between chunks: >= 2 minutes with no GPU process of ours, the GPU must be below 65 C and no OTHER compute
process may be on the GPU; the first chunk of a stage is 5 minutes; after an exit-90 temperature stop chunks are 10 minutes and the
pause doubles; three exit-90 stops stop the stage. The in-chunk duty cycle (~50 percent) is applied by gate_gen (sleep per unit).
Completion is read from stage_log.jsonl (the Python teardown on this machine can exit 0xC0000409 after finishing, so exit codes
other than 90/91 are not trusted).

usage: python exp001/gate_driver.py --stage pg1g -- <args passed to gate_gen.py>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_GEN = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe")
OUT = ROOT / "runs" / "EXP-001" / "gates"


def gpu_state():
    r = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True)
    t, m = [float(x) for x in r.stdout.strip().split(",")]
    r2 = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,name", "--format=csv,noheader"], capture_output=True, text=True)
    apps = [l for l in r2.stdout.strip().splitlines() if l.strip()]
    return t, m, apps


def wait_ready(max_temp=65.0, timeout_s=3600):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        t, m, apps = gpu_state()
        if t < max_temp and not apps:
            return True, t
        time.sleep(15)
    return False, gpu_state()[0]


def stage_complete(stage_dir: Path, since: float) -> bool:
    p = stage_dir / "stage_log.jsonl"
    if not p.exists():
        return False
    for line in p.read_text(encoding="utf8").splitlines():
        row = json.loads(line)
        if row.get("event") == "complete" and row.get("t", 0) >= since:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--max-chunks", type=int, default=40)
    ap.add_argument("--first-minutes", type=float, default=5.0)
    ap.add_argument("--chunk-minutes", type=float, default=15.0)
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    rest = a.rest[1:] if a.rest and a.rest[0] == "--" else a.rest
    stage_dir = OUT / (a.stage + (f"_{a.tag}" if a.tag else ""))
    stage_dir.mkdir(parents=True, exist_ok=True)
    chunk_idx = len(list(OUT.glob(f"telemetry-{a.stage}{('_' + a.tag) if a.tag else ''}-*.csv")))
    temp_stops, pause = 0, 120.0
    t_stage0 = time.time()
    for c in range(a.max_chunks):
        ok, temp = wait_ready()
        if not ok:
            print("GPU not ready (temperature or foreign compute process); stopping", flush=True)
            return 2
        minutes = a.first_minutes if chunk_idx == 0 else (10.0 if temp_stops else a.chunk_minutes)
        soft = minutes - (2.0 if minutes <= 5 else 2.0)
        tele = OUT / f"telemetry-{a.stage}{('_' + a.tag) if a.tag else ''}-{chunk_idx:03d}.csv"
        t0 = time.time()
        cmd = [sys.executable, str(ROOT / "tools" / "gpu_guard.py"), "--log", str(tele), "--max-temp", "85", "--max-minutes", str(minutes), "--",
               str(PY_GEN), str(ROOT / "exp001" / "gate_gen.py"), "--stage", a.stage, "--resume", "--soft-minutes", str(soft), *rest]
        print("chunk", chunk_idx, "minutes", minutes, flush=True)
        code = subprocess.run(cmd, cwd=str(ROOT)).returncode
        wall = time.time() - t0
        chunk_idx += 1
        print(f"chunk exit {code} wall {wall:.0f}s", flush=True)
        if code == 90:
            temp_stops += 1
            pause *= 2
            (OUT / "failures.jsonl").open("a").write(json.dumps(dict(stage=a.stage, chunk=chunk_idx - 1, event="temperature stop (exit 90)", t=time.time())) + "\n")
            if temp_stops >= 3:
                print("three temperature stops: stage stopped for the orchestrator", flush=True)
                return 90
        if stage_complete(stage_dir, t0):
            print("stage complete", flush=True)
            return 0
        time.sleep(pause)                     # 2-minute pause between chunks (the per-unit duty sleep inside the chunk gives ~50 percent)
    return 3


if __name__ == "__main__":
    sys.exit(main())
