"""Integration of the new stages into `gate_driver` (2026-10-28): the stage table, the command each stage launches, that the command parses with the runner's own argument parser, the Omni interpreter and
memory flags, and that every existing refusal rule (hold file, dirty tree, pin, battery, event log, guard stop) applies to the new stages unchanged. CPU only; nothing is launched."""
import argparse
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import common, run_gate_omni_r, run_omni_timing                    # noqa: E402
from exp_p2.gate import epred, foil, gate_driver, hold, pins, runner, suite     # noqa: E402
from exp_p2.omni import build                                                   # noqa: E402

NEW = ("foil-fit", "foil-test", "epred-fit", "suite", "omni-timing", "omni-r-cal", "omni-r-pos", "omni-r-test")
OMNI = ("omni-timing", "omni-r-cal", "omni-r-pos", "omni-r-test")
RUN_IDS = {"foil-fit": foil.FIT_RUN_ID, "foil-test": foil.TEST_RUN_ID, "epred-fit": epred.FIT_RUN_ID, "suite": suite.SUITE_RUN_ID, "omni-timing": run_omni_timing.RUN_ID,
           "omni-r-cal": run_gate_omni_r.CAL_RUN, "omni-r-pos": run_gate_omni_r.POS_RUN, "omni-r-test": run_gate_omni_r.TEST_RUN}
OMNI_PY = gate_driver.OMNI_PY


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "_cuda", lambda: None)
    monkeypatch.setattr(gate_driver.time, "sleep", lambda s: None)

    def init_run(run_id, config):
        d = tmp_path / run_id
        d.mkdir(parents=True, exist_ok=True)
        (d / "config.json").write_text(json.dumps(config))
        return d
    monkeypatch.setattr(common, "init_run", init_run)
    return tmp_path


@pytest.fixture
def driver(env, monkeypatch):
    monkeypatch.setattr(gate_driver.driver, "gates_ok", lambda: (True, "ok"))
    monkeypatch.setattr(gate_driver, "EVENTS_FN", lambda since: dict(ok=True, events=[], error=None))
    monkeypatch.setattr(gate_driver, "AC_FN", lambda: True)
    monkeypatch.setattr(gate_driver, "PIN_FN", lambda: dict(ok=True, via="committed blob"))
    return env


def _capture(monkeypatch, rc=0, rows=0, run_dir_of=None):
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return SimpleNamespace(returncode=rc)
    monkeypatch.setattr(gate_driver.subprocess, "run", fake_run)
    return calls


class _Parsed(Exception):
    def __init__(self, ns):
        self.ns = ns


def _parse_with_the_runner(monkeypatch, module: str, argv: list[str]):
    """Run `<module>.main(argv)` with ArgumentParser.parse_args replaced by 'parse with the real parser, then stop': an unknown or malformed flag exits with code 2 (SystemExit) as in production."""
    orig = argparse.ArgumentParser.parse_args

    def stop(self, args=None, namespace=None):
        raise _Parsed(orig(self, args, namespace))
    with monkeypatch.context() as m:
        m.setattr(argparse.ArgumentParser, "parse_args", stop)
        with pytest.raises(_Parsed) as e:
            importlib.import_module(module).main(argv)
    return e.value.ns


# ------------------------------------------------------------------------------------------------ the table
def test_new_stages_are_in_the_table_with_the_runners_own_run_ids():
    for st in NEW:
        mod, rid, n = gate_driver.STAGES[st]
        assert rid == RUN_IDS[st] and n > 0 and hasattr(importlib.import_module(mod), "main"), st
    assert gate_driver.STAGES["omni-timing"][2] == run_omni_timing.N_PASSES == 20
    assert gate_driver.STAGES["omni-r-cal"][2] == run_gate_omni_r.N_CAL and gate_driver.STAGES["omni-r-pos"][2] == run_gate_omni_r.N_POS
    assert gate_driver.STAGES["epred-fit"][2] == importlib.import_module("exp_p2.run_gate_epred_chunk").CONFIG["n_items"] == 100
    assert gate_driver.STAGES["suite"][2] == importlib.import_module("exp_p2.run_gate_suite").N_ITEMS == 200
    for old in ("p2", "m1", "m2", "m3", "m4", "m5", "s2"):                                  # nothing existing was changed
        assert old in gate_driver.STAGES
    assert gate_driver.STAGES["m4"] == ("exp_p2.run_gate_m4", "P2-GATE-M4", 300) and gate_driver.STAGES["s2"][1] == "P2-GATE-S2"


def test_the_omni_flags_are_the_committed_omni_defaults():
    flags = dict(zip(gate_driver.OMNI_FLAGS[::2], gate_driver.OMNI_FLAGS[1::2]))
    p = build.PROPOSED
    assert float(flags["--mem-frac"]) == p["mem_frac"] and float(flags["--max-used-first-mib"]) == p["max_used_first_mib"] and float(flags["--max-used-mib"]) == p["max_used_mib"]
    assert float(flags["--max-rise-mib"]) == p["max_rise_mib"] and float(flags["--max-peak-alloc-mib"]) == p["max_peak_alloc_mib"]
    assert float(flags["--max-used-before-load-mib"]) == p["max_used_before_load_mib"] and len(flags) == 6
    assert OMNI_PY.name == "python.exe" and OMNI_PY.parent.parent.parent.name == "Multi-Modality Language model" and OMNI_PY.parent.parent.name == ".venv-omni"


# ------------------------------------------------------------------------------------------------ the command each stage launches
@pytest.mark.parametrize("stage", NEW)
def test_every_new_stage_launches_a_command_its_runner_parses(stage, driver, monkeypatch):
    calls = _capture(monkeypatch, rc=0)
    extra = ["--extra", "--audit-record rec.md"] if stage == "epred-fit" else []
    gate_driver.main(["--stage", stage, "--max-chunks", "1", "--n", str(gate_driver.STAGES[stage][2])] + extra)
    assert len(calls) == 1
    cmd = calls[0]
    i = cmd.index("--")                                                             # gpu_guard.py [...] -- <child python> -m <module> <args>
    assert cmd[0] == str(common.GEN_PY) and cmd[1].endswith("gpu_guard.py")           # the pinned safety wrapper always runs under the project interpreter
    assert cmd[i + 1] == str(OMNI_PY if stage in OMNI else common.GEN_PY) and cmd[i + 2] == "-m" and cmd[i + 3] == gate_driver.STAGES[stage][0]
    ns = _parse_with_the_runner(monkeypatch, cmd[i + 3], cmd[i + 4:])
    assert ns.run_id == RUN_IDS[stage] and ns.n == gate_driver.STAGES[stage][2] and ns.resume and ns.duty == 0.5
    if stage in ("foil-fit", "foil-test", "omni-r-cal", "omni-r-pos", "omni-r-test"):
        assert ns.stage == {"foil-fit": "fit", "foil-test": "test", "omni-r-cal": "cal", "omni-r-pos": "pos", "omni-r-test": "test"}[stage]
    if stage in OMNI:
        assert (ns.mem_frac, ns.max_used_first_mib, ns.max_used_mib, ns.max_rise_mib, ns.max_peak_alloc_mib, ns.max_used_before_load_mib) == (0.62, 9500.0, 9000.0, 1500.0, 7000.0, 2500.0)
        assert ns.corrupt_at == 512 if stage.startswith("omni-r") else True            # A3.5 item 1: corruptions at 512 px
        assert cmd[cmd.index("--max-minutes") + 1] == "25.0" and ns.soft_minutes == 22.5
    else:
        assert cmd[cmd.index("--max-minutes") + 1] == "5.0" and ns.soft_minutes == 2.5
    if stage == "epred-fit":
        assert ns.audit_record == "rec.md"


def test_user_extra_flags_override_the_driver_defaults_and_allow_dirty_is_forwarded(driver, monkeypatch):
    calls = _capture(monkeypatch)
    gate_driver.main(["--stage", "omni-timing", "--max-chunks", "1", "--allow-dirty", "--extra", "--max-used-mib 8800 --max-rise-mib 1200"])
    cmd = calls[0]
    ns = _parse_with_the_runner(monkeypatch, "exp_p2.run_omni_timing", cmd[cmd.index("-m") + 2:])
    assert ns.max_used_mib == 8800.0 and ns.max_rise_mib == 1200.0 and ns.max_used_first_mib == 9500.0 and ns.allow_dirty is True
    assert gate_driver.main(["--stage", "m2", "--max-chunks", "1", "--first-chunk-min", "3"]) in (0, 5, 6)
    assert calls[-1][calls[-1].index("--max-minutes") + 1] == "3.0"


def test_omni_r_test_takes_its_n_from_omni_gate_json_unless_n_is_given(driver, monkeypatch):
    assert gate_driver.default_n("omni-r-test", 150) == 150 and gate_driver.default_n("m4", 300) == 300
    (driver / "P2-OMNI-TIMING").mkdir()
    gj = driver / "P2-OMNI-TIMING" / "omni_gate.json"
    gj.write_text(json.dumps(dict(go=True, n_R=120)))
    assert gate_driver.default_n("omni-r-test", 150) == 120
    gj.write_text(json.dumps(dict(go=False, n_R=120)))
    assert gate_driver.default_n("omni-r-test", 150) == 150                                   # NO-GO: the runner refuses anyway
    gj.write_text("not json")
    assert gate_driver.default_n("omni-r-test", 150) == 150
    gj.write_text(json.dumps(dict(go=True, n_R=120)))
    calls = _capture(monkeypatch)
    gate_driver.main(["--stage", "omni-r-test", "--max-chunks", "1"])
    assert calls[0][calls[0].index("--n") + 1] == "120"
    gate_driver.main(["--stage", "omni-r-test", "--max-chunks", "1", "--n", "150"])
    assert calls[1][calls[1].index("--n") + 1] == "150"


# ------------------------------------------------------------------------------------------------ the refusal rules are the old ones
@pytest.mark.parametrize("stage", NEW)
def test_a_hold_file_stops_every_new_stage_before_anything_is_launched(stage, env, monkeypatch):
    rid = gate_driver.STAGES[stage][1]
    (env / "P2-PROBE-02").mkdir()
    (env / "P2-PROBE-02" / "HOLD.txt").write_text("on hold")

    def no(*a, **k):
        raise AssertionError("must not launch or probe the GPU")
    monkeypatch.setattr(gate_driver.subprocess, "run", no)
    monkeypatch.setattr(gate_driver.driver, "gates_ok", no)
    assert gate_driver.main(["--stage", stage]) == hold.EXIT_HOLD == 7
    assert (env / "P2-PROBE-02" / "HOLD.txt").exists() and not (env / rid / "stdout-chunk00.log").exists()


@pytest.mark.parametrize("stage", NEW)
def test_dirty_tree_pin_battery_and_events_stop_every_new_stage(stage, driver, monkeypatch):
    def no(*a, **k):
        raise AssertionError("must not launch")
    monkeypatch.setattr(gate_driver.subprocess, "run", no)
    monkeypatch.setattr(pins, "dirty_files", lambda: [" M exp_p2/gate/theory.py"])
    assert gate_driver.main(["--stage", stage]) == pins.EXIT_DIRTY == 11
    monkeypatch.setattr(pins, "dirty_files", lambda: [])
    monkeypatch.setattr(gate_driver, "PIN_FN", lambda: dict(ok=False, expected="x", committed_blob="a", working_normalised="b"))
    assert gate_driver.main(["--stage", stage]) == gate_driver.EXIT_PIN == 10
    monkeypatch.setattr(gate_driver, "PIN_FN", lambda: dict(ok=True))
    monkeypatch.setattr(gate_driver, "AC_FN", lambda: False)
    assert gate_driver.main(["--stage", stage]) == gate_driver.EXIT_GUARD_STOP == 8
    monkeypatch.setattr(gate_driver, "AC_FN", lambda: True)
    monkeypatch.setattr(gate_driver, "EVENTS_FN", lambda since: dict(ok=True, events=[dict(id=117, log="System", message="x")], error=None))
    assert gate_driver.main(["--stage", stage]) == gate_driver.EXIT_EVENTS == 9


def test_a_guard_stop_of_an_omni_stage_is_never_relaunched_and_the_loop_completes_on_rows(driver, monkeypatch):
    run = driver / "P2-OMNI-TIMING"
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        common.append_jsonl(run / "items.jsonl", dict(idx=len(common.read_jsonl(run / "items.jsonl"))))
        return SimpleNamespace(returncode=76 if len(calls) == 1 else 0)
    monkeypatch.setattr(gate_driver.subprocess, "run", fake_run)
    assert gate_driver.main(["--stage", "omni-timing", "--n", "3"]) == gate_driver.EXIT_GUARD_STOP and len(calls) == 1
    run2 = driver / "P2-OMNI-R-CAL"
    n = {"k": 0}

    def fake_run2(cmd, **kw):
        n["k"] += 1
        for _ in range(2):
            common.append_jsonl(run2 / "items.jsonl", dict(idx=len(common.read_jsonl(run2 / "items.jsonl"))))
        return SimpleNamespace(returncode=75 if n["k"] < 2 else 0)
    monkeypatch.setattr(gate_driver.subprocess, "run", fake_run2)
    assert gate_driver.main(["--stage", "omni-r-cal", "--n", "4"]) == 0 and n["k"] == 2          # 75 = relaunch the same command; complete when the rows reach n


def test_effective_n_lets_a_new_stage_complete_after_exclusions(driver, monkeypatch):
    run = driver / "P2-GATE-FOIL-FIT"
    run.mkdir()
    (run / "effective_n.json").write_text(json.dumps(dict(planned=240, effective=3)))
    for i in range(3):
        common.append_jsonl(run / "items.jsonl", dict(idx=i))
    monkeypatch.setattr(gate_driver.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError("already complete")))
    assert gate_driver.main(["--stage", "foil-fit"]) == 0


# ------------------------------------------------------------------------------------------------ the child's refusal reason reaches driver.log (exit codes and stop rules unchanged)
@pytest.mark.parametrize("rc", [2, 3, 10, 11])
def test_a_refusal_exit_writes_the_reason_to_driver_log_at_the_time_and_changes_no_stop_rule(rc, driver, monkeypatch):
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        kw["stdout"].write("some banner\nSTOP: runs/P2-GATE-M3/family.json missing; create it with: python -m exp_p2.gate.headroom\n")
        kw["stdout"].flush()
        return SimpleNamespace(returncode=rc)
    monkeypatch.setattr(gate_driver.subprocess, "run", fake_run)
    out = gate_driver.main(["--stage", "m4", "--n", "300"])
    log = (driver / "P2-GATE-M4" / "driver.log").read_text(encoding="utf8")
    assert f"chunk 0 refused (exit {rc}): STOP: runs/P2-GATE-M3/family.json missing" in log and f"chunk 1 refused (exit {rc})" in log
    assert log.index("chunk 0 exit") < log.index("chunk 0 refused")
    assert out == 5 and len(calls) == 2 and "STOP: two chunks without progress" in log           # the old rule: no progress twice -> exit 5; nothing relaunched beyond it


def test_the_reason_falls_back_to_the_last_line_and_other_exits_write_none(driver, monkeypatch, tmp_path):
    f = tmp_path / "x.log"
    f.write_text("a\nTraceback (most recent call last):\nValueError: bad\n", encoding="utf8")
    assert gate_driver.refusal_reason(f) == "ValueError: bad"
    f.write_text("STOP: first\nmore\nSTOP: second\ntail\n", encoding="utf8")
    assert gate_driver.refusal_reason(f) == "STOP: second"
    assert gate_driver.refusal_reason(tmp_path / "missing.log").startswith("(log unreadable")
    f.write_text("", encoding="utf8")
    assert gate_driver.refusal_reason(f) == "(no output)"
    run = driver / "P2-GATE-M2"

    def fake_run(cmd, **kw):
        common.append_jsonl(run / "items.jsonl", dict(idx=len(common.read_jsonl(run / "items.jsonl"))))
        kw["stdout"].write("STOP: not a refusal exit\n")
        return SimpleNamespace(returncode=75)
    monkeypatch.setattr(gate_driver.subprocess, "run", fake_run)
    assert gate_driver.main(["--stage", "m2", "--n", "2"]) == 0
    assert "refused" not in (run / "driver.log").read_text(encoding="utf8")
