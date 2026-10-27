"""Chunk driver for the Paper 2 probes. Pure Python (no torch). Every chunk runs inside tools/gpu_guard.py (telemetry CSV, stop at 85 C
for 3 readings, hard stop at the chunk length). Before every chunk: GPU temperature below 65 C, no other GPU job (memory used below
1500 MiB and utilisation below 30 percent on three readings), free physical RAM at least 4 GB. If a gate does not open within
--wait-minutes the driver stops and says so (the run is resumable). Completion is read from the row count, never from the exit code.

    python -m exp_p2.driver --probe 1 --run-id P2-PROBE-01 --n 300
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp_p2 import common                                                  # noqa: E402

READY_TEMP, MAX_TEMP, MIN_RAM_GB = 65.0, 85.0, 4.0
MEM_BUSY_MIB, UTIL_BUSY = 1500.0, 30.0


def gates_ok() -> tuple[bool, str]:
    reads = []
    for _ in range(3):
        reads.append(common.gpu_state())
        time.sleep(4)
    ram = common.mem_status()["free_ram_gb"]
    temp = max(r["temp_c"] for r in reads)
    busy = [r for r in reads if r["mem_used_mib"] > MEM_BUSY_MIB or r["util_pct"] > UTIL_BUSY]
    why = []
    if temp >= READY_TEMP:
        why.append(f"temp {temp}")
    if busy:
        why.append(f"gpu busy {busy[-1]}")
    if ram < MIN_RAM_GB:
        why.append(f"free ram {ram} GB")
    return (not why), "; ".join(why) or f"ok temp={temp} ram={ram}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=int, required=True, choices=[1, 2])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--duty", type=float, default=0.5)
    ap.add_argument("--first-chunk-min", type=float, default=5.0)
    ap.add_argument("--chunk-min", type=float, default=15.0)
    ap.add_argument("--wait-minutes", type=float, default=20.0)
    ap.add_argument("--max-chunks", type=int, default=12)
    a = ap.parse_args()
    run = common.RUNS / a.run_id
    log = run / "driver.log"
    run.mkdir(parents=True, exist_ok=True)

    def say(msg):
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(log, "a", encoding="utf8") as fh:
            fh.write(line + "\n")

    mod = f"exp_p2.run_probe{a.probe}"
    n_stop, fails, pause = 0, 0, 30.0
    for ch in range(a.max_chunks):
        done = len(common.read_jsonl(run / "items.jsonl"))
        say(f"chunk {ch}: {done}/{a.n} done")
        if done >= a.n:
            say("COMPLETE")
            return 0
        t0 = time.time()
        while True:
            ok, why = gates_ok()
            if ok:
                break
            if time.time() - t0 > a.wait_minutes * 60:
                say(f"STOP: gate not open after {a.wait_minutes} min ({why}); run is resumable")
                return 3
            say(f"waiting: {why}")
            time.sleep(30)
        mins = a.first_chunk_min if ch == 0 else a.chunk_min
        if n_stop:
            mins = min(mins, 10.0)
        soft = max(1.0, mins - 2.5)
        cmd = [str(common.GEN_PY), str(ROOT / "tools" / "gpu_guard.py"), "--log", str(run / f"telemetry-chunk{ch:02d}.csv"),
               "--max-temp", str(MAX_TEMP), "--max-minutes", str(mins), "--",
               str(common.GEN_PY), "-m", mod, "--run-id", a.run_id, "--n", str(a.n), "--resume", "--duty", str(a.duty if not n_stop else min(a.duty, 1 / 3)),
               "--soft-minutes", str(soft)]
        say("launch " + " ".join(cmd[-12:]))
        with open(run / f"stdout-chunk{ch:02d}.log", "w", encoding="utf8") as fh:
            r = subprocess.run(cmd, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT)
        new_done = len(common.read_jsonl(run / "items.jsonl"))
        say(f"chunk {ch} exit {r.returncode}; rows {done} -> {new_done}")
        if r.returncode == 90:
            n_stop += 1
            pause = 60.0 * (2 ** (n_stop - 1))
            say(f"temperature stop #{n_stop}; pause {pause} s")
            if n_stop >= 3:
                say("STOP: three temperature stops")
                return 4
        if new_done == done:
            fails += 1
            if fails >= 2:
                say("STOP: two chunks without progress (see stdout logs)")
                return 5
        else:
            fails = 0
        time.sleep(pause)
        pause = 30.0
    say("STOP: max chunks reached")
    return 6


if __name__ == "__main__":
    sys.exit(main())
