"""Chunk driver for the gate stages (M1-M5). Composition over modification: it reuses `exp_p2.driver.gates_ok` (temperature, idle GPU, free RAM) and adds
(i) the project-wide HOLD check that the probe driver does not do for other run ids, (ii) the crash-diagnosis guard settings for gpu_guard (1 s telemetry,
lower temperature limit). It never creates or deletes a hold file and never launches anything unless every hold file is absent.

    python -m exp_p2.gate.gate_driver --stage m2 [--run-id P2-GATE-M2] [--n 300]

Completion is read from the row count, never from the exit code. Exit codes: 0 complete, 3 gate not open, 4 three temperature stops, 5 two chunks
without progress, 6 max chunks, 7 on hold, 8 guard abort or battery (never relaunched), 9 new crash-signature events in the Windows logs (or the log unreadable)."""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, driver                                           # noqa: E402
from exp_p2.gate import eventlog, guards, hold                              # noqa: E402
from exp_p2.gate.watchdog import EXIT_GUARD                                 # noqa: E402

EXIT_GUARD_STOP, EXIT_EVENTS = 8, 9      # driver exit codes: a guard abort (never relaunched), new crash-signature events in the Windows logs
EVENTS_FN = eventlog.new_events          # replaceable in tests
AC_FN = guards.on_ac

# stage -> (module, default run id, default item count; 0 = number of probe-2 arrays on disk). Static on purpose: the driver stays torch-free.
# 'p2' runs run_probe2.main() unchanged inside gate/probe2_guarded.py (memory cap, AC, memory/rise/slow-item rules, watchdog); its items.jsonl rows are the completion count.
STAGES = {"p2": ("exp_p2.gate.probe2_guarded", "P2-PROBE-02", 200),      # M1 part 1: complete probe 2 with run_probe2 UNCHANGED, wrapped by the new guards (audit F2)
          "m1": ("exp_p2.run_gate_m1", "P2-GATE-M1", 0), "m2": ("exp_p2.run_gate_m2", "P2-GATE-M2", 300), "m3": ("exp_p2.run_gate_m3", "P2-GATE-M3", 100),
          "m4": ("exp_p2.run_gate_m4", "P2-GATE-M4", 300), "m5": ("exp_p2.run_gate_m5", "P2-GATE-M5", 100)}
MAX_TEMP_DEFAULT, GUARD_EVERY_S = 80.0, 1.0       # crash diagnosis section 5: '--max-temp 80', telemetry every 1 s


def build_cmd(stage_mod: str, run_id: str, n: int, mins: float, soft: float, duty: float, ch: int, log_dir: Path, max_temp: float, extra: list[str] | None = None) -> list[str]:
    return [str(common.GEN_PY), str(ROOT / "tools" / "gpu_guard.py"), "--log", str(log_dir / f"telemetry-chunk{ch:02d}.csv"), "--max-temp", str(max_temp),
            "--max-minutes", str(mins), "--every", str(GUARD_EVERY_S), "--", str(common.GEN_PY), "-m", stage_mod, "--run-id", run_id, "--n", str(n), "--resume",
            "--duty", str(duty), "--soft-minutes", str(soft)] + list(extra or [])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--duty", type=float, default=0.5)
    ap.add_argument("--first-chunk-min", type=float, default=5.0)
    ap.add_argument("--chunk-min", type=float, default=15.0)
    ap.add_argument("--wait-minutes", type=float, default=20.0)
    ap.add_argument("--max-chunks", type=int, default=12)
    ap.add_argument("--max-temp", type=float, default=MAX_TEMP_DEFAULT)
    ap.add_argument("--no-eventlog-check", action="store_true", help="skip the read-only Windows event-log check between chunks (not recommended)")
    ap.add_argument("--extra", default="", help="extra flags forwarded to the stage module, e.g. --extra \"--tbv\" for m1 or --extra \"--tbv on\" for m4")
    a = ap.parse_args(argv)
    stage_mod, default_run, default_n = STAGES[a.stage]
    run_id = a.run_id or default_run
    n = a.n if a.n is not None else default_n
    if n == 0:
        n = len(list((Path(common.RUNS) / "P2-PROBE-02" / "arrays").glob("item*.npz")))
    run = Path(common.RUNS) / run_id
    run.mkdir(parents=True, exist_ok=True)
    log = run / "driver.log"

    def say(msg):
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(log, "a", encoding="utf8") as fh:
            fh.write(line + "\n")

    holds = hold.active_holds(run_id)
    if holds:
        say("STOP: hold file(s) exist: " + "; ".join(str(h) for h in holds) + " (GPU run on hold; delete only with Shlok's go-ahead)")
        return hold.EXIT_HOLD
    n_stop, fails, pause = 0, 0, 30.0
    started = datetime.now()                                              # "since the run started" for the event-log check
    for ch in range(a.max_chunks):
        holds = hold.active_holds(run_id)                                 # re-check before every chunk: a hold can appear mid-campaign
        if holds:
            say("STOP: hold file appeared: " + "; ".join(str(h) for h in holds))
            return hold.EXIT_HOLD
        if not a.no_eventlog_check:                                           # audit F3: refuse to (re)launch after a crash signature appears in the logs
            ev = EVENTS_FN(started)
            if not ev["ok"]:
                say(f"STOP: could not read the Windows event log ({ev['error']}); fail closed (override: --no-eventlog-check)")
                return EXIT_EVENTS
            if ev["events"]:
                say("STOP: new crash-signature events since the run started: " + json.dumps(ev["events"][:5]))
                return EXIT_EVENTS
        if AC_FN() is False:
            say("STOP: running on battery; not launching a chunk")
            return EXIT_GUARD_STOP
        done = len(common.read_jsonl(run / "items.jsonl"))
        say(f"chunk {ch}: {done}/{n} done")
        if n and done >= n:
            say("COMPLETE")
            return 0
        t0 = time.time()
        while True:
            ok, why = driver.gates_ok()
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
        cmd = build_cmd(stage_mod, run_id, n, mins, max(1.0, mins - 2.5), a.duty if not n_stop else min(a.duty, 1 / 3), ch, run, a.max_temp, shlex.split(a.extra))
        n_guard_before = sum(1 for e in common.read_jsonl(run / "chunks.jsonl") if e.get("event") == "guard_stop")
        say("launch " + " ".join(cmd[-12:]))
        with open(run / f"stdout-chunk{ch:02d}.log", "w", encoding="utf8") as fh:
            r = subprocess.run(cmd, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT)
        new_done = len(common.read_jsonl(run / "items.jsonl"))
        say(f"chunk {ch} exit {r.returncode}; rows {done} -> {new_done}")
        if r.returncode == hold.EXIT_HOLD:
            return hold.EXIT_HOLD
        n_guard_after = sum(1 for e in common.read_jsonl(run / "chunks.jsonl") if e.get("event") == "guard_stop")
        if r.returncode == EXIT_GUARD or n_guard_after > n_guard_before:        # audit F1: a guard abort is reviewed by a person, never retried here
            say("STOP: guard abort (exit %d, see chunks.jsonl); not relaunching" % r.returncode)
            return EXIT_GUARD_STOP
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
