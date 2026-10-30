"""Chunk driver for the gate stages (M1-M5). Composition over modification: it reuses `exp_p2.driver.gates_ok` (temperature, idle GPU, free RAM) and adds
(i) the project-wide HOLD check that the probe driver does not do for other run ids, (ii) the crash-diagnosis guard settings for gpu_guard (1 s telemetry,
lower temperature limit). It never creates or deletes a hold file and never launches anything unless every hold file is absent.

    python -m exp_p2.gate.gate_driver --stage m2 [--run-id P2-GATE-M2] [--n 300]

Stages: p2, m1-m5, s2; h3, h4 (family H, hard negatives, SAP A5); lrf-rescore, lrf-l1, lrf-lg (Study 2, SAP A6 r1); foil-fit, foil-test (family B, two runs); epred-fit (the E-pred fit chunk, after M3 and before M4); suite (imagecorruptions, exploratory); omni-timing, omni-r-cal, omni-r-pos,
omni-r-test (Omni-Diffusion 8B, 4-bit, family R: the stage runs in the OMNI interpreter, gpu_guard.py in the project one). Order of use and exact commands: research/paper2/method/IMPL-E-INTEGRATION-2026-10-28.md.

Completion is read from the row count, never from the exit code. Exit codes: 0 complete, 3 gate not open, 4 three temperature stops, 5 two chunks
without progress, 6 max chunks, 7 on hold, 8 guard abort or battery (never relaunched), 9 new crash-signature events in the Windows logs (or the log unreadable), 10 tools/gpu_guard.py does not match its pin, 11 uncommitted changes under exp_p2/ or tools/."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, driver                                           # noqa: E402
from exp_p2.gate import eventlog, guards, hold, pins                        # noqa: E402
from exp_p2.gate.watchdog import EXIT_GUARD                                 # noqa: E402

EXIT_GUARD_STOP, EXIT_EVENTS, EXIT_PIN = 8, 9, 10      # driver exit codes: a guard abort (never relaunched), new crash-signature events in the Windows logs
EVENTS_FN = eventlog.new_events          # replaceable in tests
AC_FN = guards.on_ac
PIN_FN = pins.gpu_guard_pin              # the safety wrapper must be the pinned one (committed blob or CRLF-normalised copy; re-audit N4)

# stage -> (module, default run id, default item count; 0 = number of probe-2 arrays on disk). Static on purpose: the driver stays torch-free.
# 'p2' runs run_probe2.main() unchanged inside gate/probe2_guarded.py (memory cap, AC, memory/rise/slow-item rules, watchdog); its items.jsonl rows are the completion count.
STAGES = {"p2": ("exp_p2.gate.probe2_guarded", "P2-PROBE-02", 200),      # M1 part 1: complete probe 2 with run_probe2 UNCHANGED, wrapped by the new guards (audit F2)
          "m1": ("exp_p2.run_gate_m1", "P2-GATE-M1", 0), "m2": ("exp_p2.run_gate_m2", "P2-GATE-M2", 300), "m3": ("exp_p2.run_gate_m3", "P2-GATE-M3", 100),
          "m4": ("exp_p2.run_gate_m4", "P2-GATE-M4", 300), "m5": ("exp_p2.run_gate_m5", "P2-GATE-M5", 100),
          "s2": ("exp_p2.run_gate_s2", "P2-GATE-S2", 300)}      # S2 re-infill (SAP AD.5): reads M4's flags, so it runs after M4; figures: --stage s2 --run-id P2-GATE-S2-FIG --extra "--figures" (see run_gate_s2.py)
# Integration stages (2026-10-28). Same loop, same refusals (hold files, dirty tree exit 11, gpu_guard pin exit 10, event log exit 9, battery) and same exit codes as every other stage.
STAGES.update({"foil-fit": ("exp_p2.run_gate_foil", "P2-GATE-FOIL-FIT", 240),         # family B stage 1: the fit pairs (240 planned; token-rule exclusions shrink it through effective_n.json); then CPU freeze and COMMIT
               "foil-test": ("exp_p2.run_gate_foil", "P2-GATE-FOIL-TEST", 300),       # family B stage 2: refuses unless fusion_frozen.json is committed with status ok (runner exit 2)
               "epred-fit": ("exp_p2.run_gate_epred_chunk", "P2-GATE-EPRED-FIT", 100),     # E-pred fit chunk: needs --extra "--audit-record <gate-auditor record>"; after M3 + committed family.json, before the first M4 item
               "suite": ("exp_p2.run_gate_suite", "P2-GATE-SUITE", 200),
               "omni-timing": ("exp_p2.run_omni_timing", "P2-OMNI-TIMING", 20),
               "omni-r-cal": ("exp_p2.run_gate_omni_r", "P2-OMNI-R-CAL", 100),
               "omni-r-pos": ("exp_p2.run_gate_omni_r", "P2-OMNI-R-POS", 50),
               "omni-r-test": ("exp_p2.run_gate_omni_r", "P2-OMNI-R-TEST", 150)})    # 150 is the default n_R; the driver reads the n_R of omni_gate.json when --n is not given (default_n)
OMNI_PY = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv-omni\Scripts\python.exe")      # the Omni stages need the omni venv (transformers/bitsandbytes pins); gpu_guard.py still runs under GEN_PY
STAGE_PY = {st: OMNI_PY for st in ("omni-timing", "omni-r-cal", "omni-r-pos", "omni-r-test")}
# Omni memory settings of IMPL-C section 5 (UNVERIFIED estimates, written before any Omni run: SAP A3.5 item 3 adopts them as committed; none is raised after an Omni memory reading has been seen).
# They equal the defaults of exp_p2/omni/build.py (tests/exp_p2/test_gate_integration.py asserts it), so a --extra with the same flag overrides them (argparse: the last one wins).
OMNI_FLAGS = ["--mem-frac", "0.62", "--max-used-first-mib", "9500", "--max-used-mib", "9000", "--max-rise-mib", "1500", "--max-peak-alloc-mib", "7000", "--max-used-before-load-mib", "2500"]
STAGE_ARGS = {"foil-fit": ["--stage", "fit"], "foil-test": ["--stage", "test"], "omni-timing": list(OMNI_FLAGS),
              "omni-r-cal": ["--stage", "cal"] + OMNI_FLAGS, "omni-r-pos": ["--stage", "pos"] + OMNI_FLAGS, "omni-r-test": ["--stage", "test"] + OMNI_FLAGS}      # forwarded before --extra
STAGE_ENV = {st: {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"} for st in STAGE_PY}      # lead decision T2/PM 2: HF_HUB_OFFLINE=1 for every Omni stage (assigned, so a shell's HF_HUB_OFFLINE=0 cannot win)
STAGE_CHUNK_MIN = {st: (25.0, 25.0) for st in STAGE_PY}      # (first chunk, later chunks) in minutes: the 4-bit load is the long part (IMPL-C used --max-minutes 25 --soft-minutes 22); others keep 5 / 15
# Family H (SAP addendum A5: hard negatives on fresh COCO images). Both stages run the M4 stage (run_gate_m4):
#   H3 = the 50 H3 items (the derived file folds_hardneg_h3.json holds them under `test`), corruption family and n from the plan file runs/P2-GATE-H3-PLAN/family.json (h3_gonogo plan);
#   H4 = the 300 H4 items (`test` of folds_hardneg.json), corruption family and n-rule from runs/P2-GATE-H3/family.json (h3_gonogo decide; test_fold 300, 200 or 0).
HARDNEG_FOLDS = Path(common.RUNS) / "P2-HARDNEG-ITEMS" / "folds_hardneg.json"
HARDNEG_FOLDS_H3 = Path(common.RUNS) / "P2-HARDNEG-ITEMS" / "folds_hardneg_h3.json"
STAGES.update({"h3": ("exp_p2.run_gate_m4", "P2-GATE-H3", 50), "h4": ("exp_p2.run_gate_m4", "P2-GATE-H4", 300)})
STAGE_ARGS.update({"h3": ["--folds-path", str(HARDNEG_FOLDS_H3), "--family-run", "P2-GATE-H3-PLAN"],
                   "h4": ["--folds-path", str(HARDNEG_FOLDS), "--family-run", "P2-GATE-H3"]})       # forwarded before --extra, so --extra can still override
# Study 2 (SAP addendum A6 r1, A6.10 run order: re-score M4 at L_FIX -> re-freeze -> L1 -> LG). All three stages are `run_gate_m4` / `run_gate_lrf_rescore` with the A6.11 options; nothing here changes a default of another stage.
#   lrf-rescore  runs/P2-GATE-M4 (read only) -> runs/P2-LRF-RESCORE: B, s3, D, tbv at the fixed slot of 13 tokens for the 500 M4 items x 4 conditions (36 passes per item, no encoding), invariance + positive control on the first 5 items
#   lrf-l1       the fresh fold runs/P2-LRF-FOLD/folds_lrf.json, family runs/P2-LRF-PLAN/family.json (P's three operating points, test_fold = n_L from the n-rule), `--layout-fix 13 --neg-len`, no sanity / denoised copies, tbv on
#   lrf-lg       the first 300 fold items, family runs/P2-LRF-PLAN-LG/family.json (EMPTY family, test_fold 300): clean + shot_noise3, impulse_noise3, speckle_noise3 only, `--layout-fix 13`, tbv on
# --n for lrf-l1 defaults to the n_L of runs/P2-LRF-PLAN/family.json (default_n); the explicit --max-chunks defaults are STAGE_MAX_CHUNKS. The memory and slow-item flags are NOT baked in (the thresholds are Shlok's to approve): pass LRF_MEM_SLOW through --extra,
# exactly as the S2 run card does.
LRF_FOLD = Path(common.RUNS) / "P2-LRF-FOLD" / "folds_lrf.json"
LRF_MEM_SLOW = "--max-used-first-mib 11000 --max-used-mib 11000 --max-rise-mib 4500 --mem-frac 0.75 --slow-factor 3 --slow-min-s 2"      # the S2 run card values (row 8); the lead decides per stage
LRF_L_FIX = "13"
STAGES.update({"lrf-rescore": ("exp_p2.run_gate_lrf_rescore", "P2-LRF-RESCORE", 500), "lrf-l1": ("exp_p2.run_gate_m4", "P2-LRF-L1", 533), "lrf-lg": ("exp_p2.run_gate_m4", "P2-LRF-LG", 300)})
STAGE_ARGS.update({"lrf-rescore": ["--slot-len", LRF_L_FIX],
                   "lrf-l1": ["--folds-path", str(LRF_FOLD), "--family-run", "P2-LRF-PLAN", "--sanity", "", "--denoise-for", "", "--tbv", "on", "--layout-fix", LRF_L_FIX, "--neg-len"],
                   "lrf-lg": ["--folds-path", str(LRF_FOLD), "--family-run", "P2-LRF-PLAN-LG", "--sanity", "", "--denoise-for", "", "--tbv", "on", "--layout-fix", LRF_L_FIX,
                              "--extra-cells", "shot_noise3,impulse_noise3,speckle_noise3"]})
# E1 (exploratory plan 2026-10-30): the L1 fold, family and flags with the pixel denoiser (S-DN, Study 1) applied before scoring; conditions jpeg10_nlm and noise0.1_nlm only. Run through the thin entry point
# exp_p2.run_gate_lrf_dn, which leaves the pinned run_gate_m4.py untouched. Guards are passed with --extra (LRF_MEM_SLOW), as for the other lrf-* stages.
STAGES.update({"lrf-dn": ("exp_p2.run_gate_lrf_dn", "P2-LRF-DN", 450)})
STAGE_ARGS.update({"lrf-dn": STAGE_ARGS["lrf-l1"] + ["--denoise", "nlm-sdn"]})
STAGE_MAX_CHUNKS = {"lrf-rescore": 40, "lrf-l1": 60, "lrf-lg": 40, "lrf-dn": 24}       # explicit, not the driver default 12 (which stopped M4 once, CONFIRM 13): about 2.5 h, 4.3 h and 2.25 h of wall time in 15-minute chunks, with 1.5x slack
DEFAULT_MAX_CHUNKS = 12


def resolve_max_chunks(stage: str, given: int | None) -> int:
    """--max-chunks if given; else the explicit per-stage value of the lrf-* stages; else the driver default 12 (every other stage, unchanged)."""
    return given if given is not None else STAGE_MAX_CHUNKS.get(stage, DEFAULT_MAX_CHUNKS)
MAX_TEMP_DEFAULT, GUARD_EVERY_S = 80.0, 1.0      # crash diagnosis section 5: '--max-temp 80', telemetry every 1 s


def build_cmd(stage_mod: str, run_id: str, n: int, mins: float, soft: float, duty: float, ch: int, log_dir: Path, max_temp: float, extra: list[str] | None = None, *,
              child_py: Path | None = None) -> list[str]:
    """gpu_guard.py always runs under GEN_PY (the pinned safety wrapper); the stage module runs under `child_py` (default GEN_PY; the Omni stages use the omni venv)."""
    return [str(common.GEN_PY), str(ROOT / "tools" / "gpu_guard.py"), "--log", str(log_dir / f"telemetry-chunk{ch:02d}.csv"), "--max-temp", str(max_temp),
            "--max-minutes", str(mins), "--every", str(GUARD_EVERY_S), "--", str(child_py or common.GEN_PY), "-m", stage_mod, "--run-id", run_id, "--n", str(n), "--resume",
            "--duty", str(duty), "--soft-minutes", str(soft)] + list(extra or [])


REFUSAL_EXITS = (2, 3, 10, 11)       # runner exits that mean "a fence was not met" (missing prerequisite, order violation, pin, uncommitted code); the reason is the last stderr line


def refusal_reason(log: Path, tail_bytes: int = 8192) -> str:
    """The child's refusal reason from its stdout/stderr log (stderr is merged into it): the last line that starts with STOP, else the last non-empty line, else a note. Never raises."""
    try:
        with open(log, "rb") as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - tail_bytes))
            lines = [l.strip() for l in fh.read().decode("utf8", "replace").splitlines() if l.strip()]
    except OSError as e:
        return f"(log unreadable: {e})"
    stops = [l for l in lines if l.startswith("STOP")]
    return (stops or lines or ["(no output)"])[-1][:600]


def default_n(stage: str, fallback: int, runs: Path | None = None) -> int:
    """The item count when --n is not given. omni-r-test: the n_R recorded in runs/P2-OMNI-TIMING/omni_gate.json (the runner refuses a different --n), else the fallback 150."""
    if stage in ("lrf-l1", "lrf-dn"):                                                       # the n-rule record's n_L, committed in runs/P2-LRF-PLAN/family.json as n_rule.test_fold (run_gate_m4 refuses any other --n)
        p = Path(runs if runs is not None else common.RUNS) / "P2-LRF-PLAN" / "family.json"
        try:
            n = int(json.loads(p.read_text(encoding="utf8"))["n_rule"]["test_fold"])
            if n > 0:
                return n
        except (OSError, ValueError, TypeError, KeyError):
            pass
        return fallback
    if stage == "omni-r-test":
        p = Path(runs if runs is not None else common.RUNS) / "P2-OMNI-TIMING" / "omni_gate.json"
        try:
            g = json.loads(p.read_text(encoding="utf8"))
            if g.get("go") and int(g.get("n_R")) > 0:
                return int(g["n_R"])
        except (OSError, ValueError, TypeError):
            pass
    return fallback


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--duty", type=float, default=0.5)
    ap.add_argument("--first-chunk-min", type=float, default=None, help="minutes for the first chunk (default 5; Omni stages 25)")
    ap.add_argument("--chunk-min", type=float, default=None, help="minutes for later chunks (default 15; Omni stages 25)")
    ap.add_argument("--wait-minutes", type=float, default=20.0)
    ap.add_argument("--max-chunks", type=int, default=None, help=f"default {DEFAULT_MAX_CHUNKS}; the lrf-* stages have explicit defaults (STAGE_MAX_CHUNKS)")
    ap.add_argument("--max-temp", type=float, default=MAX_TEMP_DEFAULT)
    ap.add_argument("--allow-dirty", action="store_true", help="launch although exp_p2/ or tools/ has uncommitted changes (recorded in driver.log and passed to the stage)")
    ap.add_argument("--no-eventlog-check", action="store_true", help="skip the read-only Windows event-log check between chunks (not recommended)")
    ap.add_argument("--extra", default="", help="extra flags forwarded to the stage module, e.g. --extra \"--tbv\" for m1 or --extra \"--tbv on\" for m4")
    a = ap.parse_args(argv)
    stage_mod, default_run, fallback_n = STAGES[a.stage]
    first_min, later_min = STAGE_CHUNK_MIN.get(a.stage, (5.0, 15.0))
    first_min, later_min = (a.first_chunk_min if a.first_chunk_min is not None else first_min), (a.chunk_min if a.chunk_min is not None else later_min)
    run_id = a.run_id or default_run
    n = a.n if a.n is not None else default_n(a.stage, fallback_n)
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
    clean_ok, dirty = pins.require_clean(a.allow_dirty, label="gate_driver")
    if not clean_ok:
        say("STOP: uncommitted changes under exp_p2/ or tools/: " + "; ".join(dirty[:10]) + " (commit first, or --allow-dirty)")
        return pins.EXIT_DIRTY
    if dirty:
        say("--allow-dirty: continuing with uncommitted changes: " + "; ".join(dirty[:10]))
    pin = PIN_FN()
    if pin.get("ok") is False:
        say(f"STOP: tools/gpu_guard.py does not match its pin ({pin.get('expected')}): committed {pin.get('committed_blob')}, working copy normalised {pin.get('working_normalised')}")
        return EXIT_PIN
    n_stop, fails, pause = 0, 0, 30.0
    started = datetime.now()                                              # "since the run started" for the event-log check
    max_chunks = resolve_max_chunks(a.stage, a.max_chunks)
    for ch in range(max_chunks):
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
        eff = run / "effective_n.json"
        n_eff = min(n, json.loads(eff.read_text(encoding="utf8"))["effective"]) if (n and eff.exists()) else n          # items excluded by the real-tokenizer rule are not replaced
        say(f"chunk {ch}: {done}/{n_eff} done" + (f" (planned {n}, excluded {n - n_eff})" if n_eff != n else ""))
        if n_eff and done >= n_eff:
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
        mins = first_min if ch == 0 else later_min
        if n_stop:
            mins = min(mins, 10.0)
        cmd = build_cmd(stage_mod, run_id, n, mins, max(1.0, mins - 2.5), a.duty if not n_stop else min(a.duty, 1 / 3), ch, run, a.max_temp, STAGE_ARGS.get(a.stage, []) + shlex.split(a.extra) + (["--allow-dirty"] if a.allow_dirty else []),
                        child_py=STAGE_PY.get(a.stage))
        n_guard_before = sum(1 for e in common.read_jsonl(run / "chunks.jsonl") if e.get("event") == "guard_stop")
        say("launch " + " ".join(cmd[-12:]))
        with open(run / f"stdout-chunk{ch:02d}.log", "w", encoding="utf8") as fh:
            r = subprocess.run(cmd, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT, **({"env": dict(os.environ, **STAGE_ENV[a.stage])} if a.stage in STAGE_ENV else {}))
        new_done = len(common.read_jsonl(run / "items.jsonl"))
        say(f"chunk {ch} exit {r.returncode}; rows {done} -> {new_done}")
        if r.returncode in REFUSAL_EXITS:                                      # a prerequisite / order / pin / dirty-tree refusal: say why now (the loop's stop rules are unchanged)
            say(f"chunk {ch} refused (exit {r.returncode}): " + refusal_reason(run / f"stdout-chunk{ch:02d}.log"))
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
