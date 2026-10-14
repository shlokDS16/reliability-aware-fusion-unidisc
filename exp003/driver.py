"""EXP-003 autonomous driver (card section 8 order). Run with the EVAL venv python (it only needs the standard library):

    python -m exp003.driver            (from the repo root; resumable: every step re-checks its own done markers)

Order: unit tests -> pools/manifest -> freeze (pilot firewall script hashed) -> pilot generation -> pilot scoring -> pilot analysis
(firewalled; n rule and stop rules 9.1-9.3, 9.6 by script) -> controls generation -> controls scoring -> controls decision (9.4; stop on
NC-1) -> M1 (P64, G) -> M2 (O0) -> M3 (P32) -> freeze of the analysis -> main scoring -> runs/EXP-003/DONE.txt. The confirmatory analysis is
NOT run here. A stop writes runs/EXP-003/STOPPED.txt and exits with code 3; to continue after a decision write the matching ACK file
(ACK_STOP_PILOT.txt, ACK_STOP_CONTROLS.txt, ACK_STOP_BUDGET.txt) and delete STOPPED.txt, then restart.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp003 import config as C, manifest as MF                       # noqa: E402
from exp003.chunks import Clock, StageStop, run_stage                # noqa: E402
from exp003.units import units_for, stage_done                       # noqa: E402

RUNS = C.RUNS
AN = ROOT / "analysis" / "EXP-003"
LOGF = RUNS / "driver.log"


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOGF, "a", encoding="utf8") as fh:
        fh.write(line + "\n")


def stop(reason, stage):
    (RUNS / "STOPPED.txt").write_text(f"STOPPED at {time.strftime('%Y-%m-%d %H:%M:%S')}\nstage: {stage}\nreason: {reason}\n"
                                      f"The driver is not running. Decide, write the ACK file named in exp003/driver.py if continuing, delete this file, "
                                      f"and restart `python -m exp003.driver`.\n", encoding="utf8")
    log(f"STOP [{stage}]: {reason}")
    return 3


def cpu(args, name):
    r = subprocess.run([str(C.EVAL_PY), *map(str, args)], cwd=str(ROOT), capture_output=True, text=True)
    (RUNS / f"{name}.out").write_text(r.stdout + "\n--- stderr ---\n" + r.stderr[-4000:], encoding="utf8")
    return r.returncode


def score_done(scope):
    n = {"pilot": 16, "ctrl": 48}.get(scope) or json.loads((RUNS / "n_conf.json").read_text())["n_generate"]
    arms = {"pilot": ("P64", "G", "O0", "P32", "Ind", "TF"), "ctrl": ("Ind", "TF"), "main": ("P64", "G", "O0", "P32")}[scope]
    ok = all((RUNS / "score" / scope / a / f"p{p:03d}.json").exists() for a in arms for p in range(n))
    return ok and (scope != "ctrl" or (RUNS / "score" / "ctrl" / "pc2.json").exists())


def gen_stage(name, clock, budget=None):
    units = units_for(name)
    run_stage(name, C.GEN_PY, ROOT / "exp003" / "gen.py", ["--stage", name], lambda: stage_done(units), clock, log, budget)


def score_stage(scope, clock, budget=None):
    run_stage(f"score-{scope}", C.EVAL_PY, AN / "score.py", ["--scope", scope], lambda: score_done(scope), clock, log, budget)


def budget_check_factory():
    def check(clock):
        if clock.hours >= C.HARD_STOP_H and not (RUNS / "ACK_STOP_BUDGET.txt").exists():
            return f"9.1: hard stop, cumulative GPU wall-clock {clock.hours:.2f} h >= {C.HARD_STOP_H} h"
        if clock.hours >= C.BUDGET_H and not (RUNS / "ACK_STOP_BUDGET.txt").exists():
            m1 = units_for("m1")
            if not stage_done(m1):
                return (f"9.1: cumulative GPU wall-clock {clock.hours:.2f} h >= {C.BUDGET_H} h before P64 and G are complete "
                        f"(inconclusive by budget; arm-level n is reported by the analysis)")
        return None
    return check


def main():
    RUNS.mkdir(parents=True, exist_ok=True)
    if (RUNS / "STOPPED.txt").exists():
        log("STOPPED.txt present: not starting (see file)")
        return 3
    (RUNS / "DRIVER_PID.txt").write_text(str(__import__("os").getpid()))
    log(f"driver start, pid {__import__('os').getpid()}")
    clock = Clock()
    try:
        # ---- 0. CPU: tests, pools, manifest, freeze of the pilot firewall script
        if not (RUNS / "tests_result.json").exists():
            r = subprocess.run([str(C.EVAL_PY), "-m", "pytest", "tests/exp003", "-q", "-x", "-p", "no:cacheprovider"], cwd=str(ROOT), capture_output=True, text=True)
            (RUNS / "tests_result.json").write_text(json.dumps(dict(returncode=r.returncode, tail=r.stdout[-1500:])))
            if r.returncode != 0:
                return stop("unit tests failed: " + r.stdout[-300:], "tests")
        pools = json.loads((RUNS / "pools.json").read_text())
        if not (pools["disjoint_from_coco_draw"] and pools["pools_pairwise_disjoint"] and pools["enough"]):
            return stop("pools.json: disjointness or size check failed", "pools")
        m = MF.manifest()
        if m["reused_exp001"]["mismatches"]:
            return stop(f"reused EXP-001 files differ from the EXP-001 manifest: {m['reused_exp001']['mismatches']}", "manifest")
        if not (RUNS / "freeze-pilot.json").exists():
            MF.freeze("pilot", MF.PILOT_FILES)
            log("pilot firewall script frozen")
        # ---- 1. pilot
        gen_stage("pilot", clock)
        score_stage("pilot", clock)
        if not (RUNS / "n_conf.json").exists():
            if cpu([AN / "pilot_analysis.py"], "pilot_analysis") != 0:
                return stop("pilot analysis failed; see runs/EXP-003/pilot_analysis.out", "pilot-analysis")
            log("pilot analysis done")
        if not (RUNS / "pilot" / "scrambled_analysis_digest.json").exists():
            if cpu([AN / "frozen_analysis.py", "pilot-scrambled"], "scrambled_analysis") != 0:
                return stop("label-scrambled end-to-end analysis failed; see scrambled_analysis.out", "pilot-analysis")
        nc = json.loads((RUNS / "n_conf.json").read_text())
        if nc["stop_reasons"] and not (RUNS / "ACK_STOP_PILOT.txt").exists():
            return stop("; ".join(nc["stop_reasons"]), "pilot-rules")
        # ---- 2. controls
        gen_stage("ctrl", clock)
        score_stage("ctrl", clock)
        if not (RUNS / "ctrl" / "controls_decision.json").exists():
            if cpu([AN / "frozen_analysis.py", "controls"], "controls_decision") != 0:
                return stop("controls decision script failed", "controls")
        cd = json.loads((RUNS / "ctrl" / "controls_decision.json").read_text())
        log(f"controls: NC-1 pass {cd['nc1']['passes']}, PC-1 pass {cd['pc1']['passes']}, PC-2 {None if cd['pc2'] is None else cd['pc2']['passes']}")
        if not cd["nc1"]["passes"] and not (RUNS / "ACK_STOP_CONTROLS.txt").exists():
            return stop(f"9.4: NC-1 failed (Lambda_b(Ind) {cd['nc1']['lambda_b_ind']:.3f}, 95 percent interval {cd['nc1']['pct95']}); the pipeline or the wrapper is biased", "controls")
        # ---- 3. main stage
        if nc["n_generate"] <= 0:
            return stop("n_generate is 0", "main")
        budget = budget_check_factory()
        for st in ("m1", "m2", "m3"):
            gen_stage(st, clock, budget)
        if not (RUNS / "freeze-analysis.json").exists():
            if MF.check_freeze("pilot"):
                return stop(f"pilot-frozen files changed: {MF.check_freeze('pilot')}", "freeze")
            MF.freeze("analysis", MF.FROZEN_ANALYSIS_FILES)
            log("analysis scripts frozen before main-stage scoring")
        score_stage("main", clock, lambda c: f"hard stop {c.hours:.2f} h" if c.hours >= C.HARD_STOP_H and not (RUNS / "ACK_STOP_BUDGET.txt").exists() else None)
        (RUNS / "DONE.txt").write_text(f"main-stage generation and scoring complete {time.strftime('%Y-%m-%d %H:%M:%S')}; cumulative GPU wall-clock {clock.hours:.2f} h\n"
                                       f"next: orchestrator final check, then python analysis/EXP-003/frozen_analysis.py main\n")
        log("DONE")
        return 0
    except StageStop as ex:
        return stop(str(ex), "stage")
    except Exception as ex:                                              # noqa: BLE001
        import traceback
        (RUNS / "driver_crash.txt").write_text(traceback.format_exc())
        return stop(f"driver exception: {type(ex).__name__}: {ex}", "driver")


if __name__ == "__main__":
    sys.exit(main())
