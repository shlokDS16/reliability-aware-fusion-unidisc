"""Run a GPU command under guard: telemetry every few seconds, stop on sustained high temperature.

The laptop crashed twice on 2026-10-14 under sustained full GPU load (bugcheck 0x20001). Every GPU
job runs through this wrapper so that (a) temperature, power, clocks, utilisation and memory are
logged to CSV, flushed after every row, which survives a crash; (b) the job is terminated if the
GPU temperature stays at or above --max-temp for --strikes consecutive readings; (c) the job is
terminated after --max-minutes, so long work is split into checkpointed chunks by the caller.

    python tools/gpu_guard.py --log runs/<exp>/telemetry-<stage>.csv [--max-temp 85] \
        [--max-minutes 15] -- python my_stage.py --resume

Exit code: the child's exit code, or 90 (temperature stop) or 91 (time limit).
"""
import argparse
import csv
import datetime as dt
import subprocess
import sys
import time
from pathlib import Path

FIELDS = "temperature.gpu,power.draw,clocks.sm,clocks.mem,utilization.gpu,memory.used,pstate,clocks_throttle_reasons.active"


def sample() -> list[str]:
    r = subprocess.run(["nvidia-smi", f"--query-gpu={FIELDS}", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    return [x.strip() for x in r.stdout.strip().split(",")] if r.returncode == 0 else ["NA"] * 8


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--max-temp", type=float, default=85.0)
    ap.add_argument("--strikes", type=int, default=3)
    ap.add_argument("--max-minutes", type=float, default=15.0)
    ap.add_argument("--every", type=float, default=5.0)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        sys.exit("no command given")
    log = Path(a.log)
    log.parent.mkdir(parents=True, exist_ok=True)
    new = not log.exists()
    fh = open(log, "a", newline="", encoding="utf8")
    w = csv.writer(fh)
    if new:
        w.writerow(["time", "elapsed_s", *FIELDS.split(","), "event"])
    t0 = time.time()
    child = subprocess.Popen(cmd)
    w.writerow([dt.datetime.now().isoformat(timespec="seconds"), 0, *sample(), "start " + " ".join(cmd)[:200]])
    fh.flush()
    strikes, code = 0, None
    while True:
        time.sleep(a.every)
        s = sample()
        el = round(time.time() - t0, 1)
        event = ""
        try:
            hot = float(s[0]) >= a.max_temp
        except ValueError:
            hot = False
        strikes = strikes + 1 if hot else 0
        if child.poll() is not None:
            code = child.returncode
            event = f"child exited {code}"
        elif strikes >= a.strikes:
            child.terminate()
            code, event = 90, f"STOP: temperature >= {a.max_temp} for {strikes} readings"
        elif el > a.max_minutes * 60:
            child.terminate()
            code, event = 91, f"STOP: time limit {a.max_minutes} min (chunk boundary)"
        w.writerow([dt.datetime.now().isoformat(timespec="seconds"), el, *s, event])
        fh.flush()
        if code is not None:
            break
    try:
        child.wait(timeout=60)
    except subprocess.TimeoutExpired:
        child.kill()
    fh.close()
    print(f"gpu_guard: {event}; telemetry in {log}")
    return code


if __name__ == "__main__":
    sys.exit(main())
