"""Chunked, guarded execution of a GPU stage (card 8 "GPU regime", applied unchanged from EXP-001 12.2). Pure Python (no torch).

Each chunk is  python tools/gpu_guard.py --log runs/EXP-003/<stage>/telemetry-<stage>-<chunk>.csv --max-temp 85 --max-minutes M -- <py> <script> ... --resume
M = 5 for the first chunk of a stage, 15 afterwards, 10 after an exit 90. A chunk starts only when the GPU is below 65 C, no other compute
process is on it and free system commit exceeds the gate. Between chunks: 30 s (60 s, 120 s ... after each exit 90). After an exit 90 the
in-chunk duty idle doubles (duty 1/3). Three exit-90 stops stop the stage. Completion is read from the per-unit done markers, never from
exit codes (the Python teardown on this machine can exit 0xC0000409 after finishing).
"""
from __future__ import annotations

import ctypes
import json
import subprocess
import sys
import time
from pathlib import Path

from exp003.config import RUNS, CHUNK_MIN, FIRST_CHUNK_MIN, MAX_TEMP, READY_TEMP, PAUSE_S, DUTY, ROOT

COMMIT_GATE_GB = 6.0


def commit_free_gb() -> float:
    class MS(ctypes.Structure):
        _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("totp", ctypes.c_ulonglong), ("availp", ctypes.c_ulonglong),
                    ("totpf", ctypes.c_ulonglong), ("availpf", ctypes.c_ulonglong), ("totv", ctypes.c_ulonglong),
                    ("availv", ctypes.c_ulonglong), ("ext", ctypes.c_ulonglong)]
    m = MS()
    m.l = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.availpf / 1e9, 2)


def gpu_state():
    r = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True)
    t, m = [float(x) for x in r.stdout.strip().split(",")]
    r2 = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,name", "--format=csv,noheader"], capture_output=True, text=True)
    return t, m, [l for l in r2.stdout.strip().splitlines() if l.strip()]


def wait_ready(log, max_wait_s: float = 6 * 3600):
    """Block until the GPU is below 65 C, free of other compute processes, and free commit exceeds the gate. Returns (ok, seconds waited)."""
    t0 = time.time()
    while time.time() - t0 < max_wait_s:
        t, _, apps = gpu_state()
        if t < READY_TEMP and not apps and commit_free_gb() >= COMMIT_GATE_GB:
            return True, time.time() - t0
        time.sleep(20)
    return False, time.time() - t0


class Clock:
    """Cumulative GPU wall-clock of EXP-003 (chunk wall time plus the inter-chunk pauses; time waiting for the GPU to become available is
    not counted), persisted in runs/EXP-003/clock.json so that it survives restarts."""

    def __init__(self, path: Path = RUNS / "clock.json"):
        self.path = path
        self.d = json.loads(path.read_text()) if path.exists() else dict(gpu_wall_s=0.0, by_stage={})

    def add(self, stage: str, s: float):
        self.d["gpu_wall_s"] += s
        self.d["by_stage"][stage] = self.d["by_stage"].get(stage, 0.0) + s
        self.path.write_text(json.dumps(self.d, indent=1))

    @property
    def hours(self) -> float:
        return self.d["gpu_wall_s"] / 3600.0


class StageStop(Exception):
    pass


def run_stage(name: str, py: Path, script: Path, args: list, done_fn, clock: Clock, log, budget_check=None, max_chunks: int = 200,
              duty_flag: str = "--duty"):
    """Run chunks of `script` until done_fn() is true. Raises StageStop(reason) on three exit-90 stops, on a crash loop (three chunks in a
    row without progress), or when budget_check(clock) returns a reason string."""
    sdir = RUNS / name
    sdir.mkdir(parents=True, exist_ok=True)
    chunk = len(list(sdir.glob(f"telemetry-{name}-*.csv")))
    temp_stops, pause, stalls = 0, PAUSE_S, 0
    while not done_fn():
        if budget_check is not None:
            why = budget_check(clock)
            if why:
                raise StageStop(why)
        ok, waited = wait_ready(log)
        if not ok:
            raise StageStop(f"{name}: GPU not ready (temperature, foreign compute process or commit) after {waited:.0f} s")
        minutes = FIRST_CHUNK_MIN if chunk == 0 else (10.0 if temp_stops else CHUNK_MIN)
        duty = DUTY if not temp_stops else 1.0 / (1.0 + 2.0 ** temp_stops)       # idle doubles after each exit 90
        soft = max(minutes - 2.0, 1.0)
        tele = sdir / f"telemetry-{name}-{chunk:03d}.csv"
        cmd = [sys.executable, str(ROOT / "tools" / "gpu_guard.py"), "--log", str(tele), "--max-temp", str(MAX_TEMP), "--max-minutes", str(minutes),
               "--", str(py), str(script), *map(str, args), "--resume", "--soft-minutes", str(soft), duty_flag, str(round(duty, 4))]
        log(f"[{name}] chunk {chunk} start: {minutes} min, duty {duty:.3f}, clock {clock.hours:.3f} h")
        t0 = time.time()
        code = subprocess.run(cmd, cwd=str(ROOT), stdout=open(sdir / f"chunk-{chunk:03d}.out", "w"), stderr=subprocess.STDOUT).returncode
        wall = time.time() - t0
        chunk += 1
        clock.add(name, wall + pause)
        log(f"[{name}] chunk {chunk - 1} exit {code} wall {wall:.0f} s")
        if code == 90:
            temp_stops += 1
            pause *= 2
            with open(RUNS / "failures.jsonl", "a") as fh:
                fh.write(json.dumps(dict(stage=name, chunk=chunk - 1, event="temperature stop (exit 90)", t=time.time())) + "\n")
            if temp_stops >= 3:
                raise StageStop(f"{name}: three temperature stops (exit 90)")
        if done_fn():
            break
        stalls = 0 if _progressed(sdir) else stalls + 1
        if stalls >= 3:
            raise StageStop(f"{name}: three chunks without progress (crash loop); see {sdir}/chunk-*.out")
        if chunk >= max_chunks:
            raise StageStop(f"{name}: max chunks {max_chunks} reached")
        time.sleep(pause)


_last = {}


def _progressed(sdir: Path) -> bool:
    """Progress = the stage log grew since the previous chunk (a unit or scoring record was written)."""
    p = sdir.parent / "gen" / sdir.name / "stage_log.jsonl"
    p2 = sdir / "stage_log.jsonl"
    n = sum(len(q.read_text().splitlines()) for q in (p, p2) if q.exists())
    prev = _last.get(str(sdir), -1)
    _last[str(sdir)] = n
    return n > prev + 1                      # more than the chunk_start line itself
