"""Safety code from the code audit (F1, F2, F3, M1, M11): distinct guard exit code, no relaunch after a guard abort, probe-2 completion under the new guards, AC check
before the model load, event-log check between chunks, in-process watchdog. CPU only; every clock, sensor and subprocess is injected."""
import json
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import eventlog, gate_driver, guards, hold, probe2_guarded, runner, watchdog   # noqa: E402


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


def _items(n):
    return [dict(idx=i) for i in range(n)]


def _proc(sc, it, ctx):
    return dict(v=1), {}


def _run(env, g=None, n=6, process=_proc, **kw):
    called = []
    rc = runner.run_items(run_id="P2-GATE-S", cfg=dict(n_items=n), load=lambda: called.append("load") or object(), get_items=lambda sc, r: _items(n), process=process,
                          soft_minutes=12.5, duty=1.0, guards=g, **kw)
    return rc, called


# ------------------------------------------------------------------------------------------------ F1: exit codes
def test_guard_abort_has_its_own_exit_code_distinct_from_the_soft_deadline(env):
    assert watchdog.EXIT_GUARD == runner.EXIT_GUARD == 76 and runner.EXIT_MORE_WORK == 75
    rc, _ = _run(env, guards.Guards(used_fn=lambda: 99999.0, ac_fn=lambda: True))
    assert rc == 76
    times = iter([1.0, 1.0, 1.0, 50.0])
    g = guards.Guards(used_fn=lambda: 100.0, ac_fn=lambda: True)
    orig = g.after_item
    g.after_item = lambda busy: orig(next(times))
    (env / "P2-GATE-S").mkdir(exist_ok=True)
    rc, _ = _run(env, g)
    assert rc == 76
    rc = runner.run_items(run_id="P2-GATE-S2", cfg=dict(n_items=6), load=lambda: object(), get_items=lambda sc, r: _items(6), process=_proc, soft_minutes=0.0, duty=1.0)
    assert rc == 75                                                          # the soft deadline keeps 75


def _fake_child(env, rc_seq, rows_per_chunk=1, events=None):
    """Replaces subprocess.run in the driver: each call appends rows, optionally a guard_stop event, and returns the next exit code."""
    run = env / "P2-GATE-M2"
    calls = []

    def fake_run(cmd, **kw):
        k = len(calls)
        calls.append(cmd)
        for _ in range(rows_per_chunk):
            common.append_jsonl(run / "items.jsonl", dict(idx=len(common.read_jsonl(run / "items.jsonl"))))
        if events and events[k]:
            common.append_jsonl(run / "chunks.jsonl", dict(event="guard_stop", reason=events[k]))
        return SimpleNamespace(returncode=rc_seq[k])
    return fake_run, calls


@pytest.fixture
def driver(env, monkeypatch):
    monkeypatch.setattr(gate_driver.driver, "gates_ok", lambda: (True, "ok"))
    monkeypatch.setattr(gate_driver, "EVENTS_FN", lambda since: dict(ok=True, events=[], error=None))
    monkeypatch.setattr(gate_driver, "AC_FN", lambda: True)
    return env


def test_driver_never_relaunches_after_exit_76(driver, monkeypatch):
    fake, calls = _fake_child(driver, [76, 0])
    monkeypatch.setattr(gate_driver.subprocess, "run", fake)
    assert gate_driver.main(["--stage", "m2", "--n", "5"]) == gate_driver.EXIT_GUARD_STOP == 8
    assert len(calls) == 1                                                    # progress was made (a row was committed) and it still stopped


def test_driver_stops_when_the_child_logged_a_guard_stop_even_with_another_exit_code(driver, monkeypatch):
    fake, calls = _fake_child(driver, [1, 0], events=["slow_item"])
    monkeypatch.setattr(gate_driver.subprocess, "run", fake)
    assert gate_driver.main(["--stage", "m2", "--n", "5"]) == 8 and len(calls) == 1


def test_driver_still_relaunches_after_a_soft_deadline(driver, monkeypatch):
    fake, calls = _fake_child(driver, [75, 75, 0], rows_per_chunk=2)
    monkeypatch.setattr(gate_driver.subprocess, "run", fake)
    assert gate_driver.main(["--stage", "m2", "--n", "5"]) == 0 and len(calls) == 3


def test_driver_refuses_on_battery_and_on_new_events_and_on_unreadable_log(driver, monkeypatch):
    def no(*a, **k):
        raise AssertionError("must not launch")
    monkeypatch.setattr(gate_driver.subprocess, "run", no)
    monkeypatch.setattr(gate_driver, "AC_FN", lambda: False)
    assert gate_driver.main(["--stage", "m2", "--n", "5"]) == 8
    monkeypatch.setattr(gate_driver, "AC_FN", lambda: True)
    monkeypatch.setattr(gate_driver, "EVENTS_FN", lambda since: dict(ok=True, events=[dict(id=117, log="System", message="x")], error=None))
    assert gate_driver.main(["--stage", "m2", "--n", "5"]) == gate_driver.EXIT_EVENTS == 9
    monkeypatch.setattr(gate_driver, "EVENTS_FN", lambda since: dict(ok=False, events=[], error="boom"))
    assert gate_driver.main(["--stage", "m2", "--n", "5"]) == 9
    assert "fail closed" in (driver / "P2-GATE-M2" / "driver.log").read_text()


def test_event_check_runs_before_every_chunk_including_a_second_one(driver, monkeypatch):
    seen = []
    seq = iter([dict(ok=True, events=[], error=None), dict(ok=True, events=[dict(id=41, log="System", message="reboot")], error=None)])
    monkeypatch.setattr(gate_driver, "EVENTS_FN", lambda since: seen.append(since) or next(seq))
    fake, calls = _fake_child(driver, [75, 0])
    monkeypatch.setattr(gate_driver.subprocess, "run", fake)
    assert gate_driver.main(["--stage", "m2", "--n", "5"]) == 9 and len(calls) == 1
    assert len(seen) == 2 and seen[0] == seen[1] and isinstance(seen[0], datetime)           # both queries use the time the run started


def test_p2_stage_runs_the_guarded_wrapper_not_run_probe2_directly():
    assert gate_driver.STAGES["p2"][0] == "exp_p2.gate.probe2_guarded"


# ------------------------------------------------------------------------------------------------ F3: AC before load, event log
def test_ac_is_checked_before_the_model_load(env):
    rc, called = _run(env, guards.Guards(used_fn=lambda: 0.0, ac_fn=lambda: False, slow_factor=1e9))   # slow-item rule off: fake items take microseconds, jitter tripped it (flaky 2026-10-28)
    assert rc == 76 and called == []                                         # load() was never called
    ev = common.read_jsonl(env / "P2-GATE-S" / "chunks.jsonl")
    assert ev[-1]["event"] == "guard_stop" and ev[-1]["reason"] == "ac_lost_before_load"
    rc, called = _run(env, guards.Guards(used_fn=lambda: 0.0, ac_fn=lambda: None, slow_factor=1e9))      # unknown power state does not stop
    assert rc == 0 and called == ["load"]


def test_m0_stage1_refuses_on_battery(env, monkeypatch):
    from exp_p2 import run_gate_m0
    monkeypatch.setattr(guards, "on_ac", lambda: False)
    assert run_gate_m0.main(["--run-id", "P2-M0-STAGE1", "--no-eventlog-check"]) == 76 and not (env / "P2-M0-STAGE1").exists()


CANNED = json.dumps([
    dict(Id=41, LogName="System", ProviderName="Microsoft-Windows-Kernel-Power", T="2026-10-27T23:25:29+05:30", M="The system has rebooted without cleanly shutting down"),
    dict(Id=1001, LogName="Application", ProviderName="Windows Error Reporting", T="2026-10-27T23:26:00+05:30", M="Fault bucket LiveKernelEvent, type 141"),
    dict(Id=1001, LogName="Application", ProviderName="Windows Error Reporting", T="2026-10-27T23:27:00+05:30", M="Fault bucket for chrome.exe crash"),
])


def test_eventlog_parse_filters_application_1001_to_gpu_kernel_events():
    ev = eventlog.relevant(eventlog.parse(CANNED))
    assert [e["id"] for e in ev] == [41, 1001] and "LiveKernelEvent" in ev[1]["message"]
    assert eventlog.parse("") == [] and eventlog.parse("   \n") == []
    one = eventlog.relevant(eventlog.parse(json.dumps(dict(Id=105, LogName="System", ProviderName="Kernel-Power", T="t", M="Power source change."))))
    assert [e["id"] for e in one] == [105]                                   # PowerShell prints a bare object for a single event
    assert eventlog.relevant([dict(Id=7, LogName="System", M="irrelevant")]) == []


def test_eventlog_script_watches_the_listed_ids_and_failure_is_reported_not_swallowed():
    s = eventlog.ps_script(datetime(2026, 10, 28, 9, 30, 0))
    for i in ("41", "105", "117", "141", "1001"):
        assert i in s
    assert "2026-10-28T09:30:00" in s and "Get-WinEvent" in s and "Set-" not in s and "Remove-" not in s        # read-only
    r = eventlog.new_events(datetime.now(), run=lambda script: CANNED)
    assert r["ok"] and len(r["events"]) == 2
    assert eventlog.new_events(datetime.now(), run=lambda script: "")["events"] == []
    bad = eventlog.new_events(datetime.now(), run=lambda script: (_ for _ in ()).throw(RuntimeError("no powershell")))
    assert bad["ok"] is False and "no powershell" in bad["error"]


# ------------------------------------------------------------------------------------------------ M1: in-process watchdog
def _wd(used, ac=lambda: True, **gkw):
    g = guards.Guards(used_fn=used, ac_fn=ac, **gkw)
    return g, watchdog.Watchdog(g, on_trip=lambda why: trips.append(why), sleep=lambda s: None)


trips: list = []


def test_watchdog_rules_memory_first_item_rise_and_ac():
    g, w = _wd(lambda: 9500.0)
    assert w.check_once() is None                                             # first item: allowance 10,000
    g.first_item_active = False
    assert "gpu_memory 9500" in w.check_once()                                # later items: 9,000
    vals = iter([5000.0, 7000.0])
    g, w = _wd(lambda: next(vals))
    assert w.check_once() is None and "rise 2000" in w.check_once().replace("_", " ")      # +2 GB between two 1 s samples
    g, w = _wd(lambda: 100.0, ac=lambda: False)
    assert w.check_once() == "ac_lost"
    g, w = _wd(lambda: 100.0, ac=lambda: None)
    assert w.check_once() is None


def test_watchdog_thread_trips_once_calls_on_trip_and_stops_on_request():
    trips.clear()
    seq = iter([100.0, 200.0, 12000.0, 300.0])
    g, w = _wd(lambda: next(seq))
    w.start()
    w._thread.join(timeout=5)
    assert w.tripped is not None and len(trips) == 1 and "gpu_memory" in trips[0]
    trips.clear()
    g, w = _wd(lambda: 100.0)
    w.sleep = lambda s: __import__("time").sleep(0.001)
    w.start()
    w.stop()
    assert not w._thread.is_alive() and trips == []
    trips.clear()
    g, w = _wd(lambda: (_ for _ in ()).throw(OSError("nvml gone")))
    w.start()
    w._thread.join(timeout=5)
    assert trips and "sensor_error" in trips[0]                               # an unreadable sensor fails closed


def test_default_trip_logs_and_ends_the_process_with_76(tmp_path, monkeypatch):
    codes = []
    monkeypatch.setattr(watchdog.os, "_exit", lambda c: codes.append(c))
    watchdog.kill_process_on_trip(tmp_path / "chunks.jsonl")("gpu_memory 9999 MiB > 9000")
    assert codes == [76]
    e = json.loads((tmp_path / "chunks.jsonl").read_text().splitlines()[-1])
    assert e["event"] == "guard_stop" and e["source"] == "watchdog" and "9999" in e["reason"]


def test_run_items_starts_and_stops_the_watchdog(env):
    log = []

    class W:
        def start(self):
            log.append("start")
            return self

        def stop(self):
            log.append("stop")
    rc, _ = _run(env, guards.Guards(used_fn=lambda: 0.0, ac_fn=lambda: True), watchdog_factory=lambda g, run: W())
    assert rc == 0 and log == ["start", "stop"]
    log.clear()
    (env / "P2-GATE-S" / "items.jsonl").unlink()
    rc, _ = _run(env, guards.Guards(used_fn=lambda: 99999.0, ac_fn=lambda: True), n=3, watchdog_factory=lambda g, run: W())
    assert rc == 76 and log == ["start", "stop"]                              # stopped on the abort path too


# ------------------------------------------------------------------------------------------------ M11: hold per item
def test_hold_created_mid_chunk_stops_before_the_next_item(env):
    def proc(sc, it, ctx):
        if it["idx"] == 1:
            (env / "GATE-HOLD.txt").write_text("hold")
        return dict(v=1), {}
    rc, _ = _run(env, process=proc)
    assert rc == 7 and [r["idx"] for r in common.read_jsonl(env / "P2-GATE-S" / "items.jsonl")] == [0, 1]
    assert common.read_jsonl(env / "P2-GATE-S" / "chunks.jsonl")[-1]["event"] == "hold_stop"


# ------------------------------------------------------------------------------------------------ F2: guarded probe-2 completion
class Cuda:
    def __init__(self, used_seq):
        self.used = iter(used_seq)
        self.cur = 0.0

    def mem_get_info(self):
        try:
            self.cur = next(self.used)
        except StopIteration:
            pass
        return ((12288 - self.cur) * 2**20, 12288 * 2**20)


def _probe_main(cuda, run_id, seconds, calls=None):
    """Stand-in for run_probe2.main: per item, the memory query then the row append, exactly where the real code does them."""
    def main():
        if calls is not None:
            calls.append(("load", sys.argv[1:]))
            common.load_net()
        run = Path(common.RUNS) / run_id
        run.mkdir(parents=True, exist_ok=True)
        for i, s in enumerate(seconds):
            cuda.mem_get_info()
            common.append_jsonl(run / "items.jsonl", dict(idx=i, seconds=s))
        return 0
    return main


def _guarded(env, monkeypatch, used, seconds, ac=lambda: True, argv=(), calls=None):
    monkeypatch.setattr(common, "load_net", lambda: "net")
    cuda = Cuda(used)
    orig = (cuda.mem_get_info, common.append_jsonl, common.load_net)      # bound method objects compare equal when restored
    noop = SimpleNamespace(start=lambda: None, stop=lambda: None)
    rc = probe2_guarded.run_guarded(["--run-id", "P2-PROBE-X", "--n", "5", "--resume", *argv], probe_main=_probe_main(cuda, "P2-PROBE-X", seconds, calls), cuda=cuda,
                                    watchdog_factory=lambda g, run: noop, ac_fn=ac, events_fn=lambda since: dict(ok=True, events=[], error=None))
    assert (cuda.mem_get_info, common.append_jsonl, common.load_net) == orig         # the hooks are removed again, also after an abort
    return rc, cuda


def test_guarded_probe2_passes_a_healthy_run_through_and_restores_the_hooks(env, monkeypatch):
    calls = []
    rc, cuda = _guarded(env, monkeypatch, [3000.0] * 5, [2.0] * 5, calls=calls)
    assert rc == 0 and len(common.read_jsonl(env / "P2-PROBE-X" / "items.jsonl")) == 5
    assert calls[0][1] == ["--run-id", "P2-PROBE-X", "--n", "5", "--resume"]          # in particular '--n' is not read as an abbreviation of '--no-ac-check'          # our flags are stripped, probe 2's own flags are passed on
    assert common.load_net() == "net"


def test_guarded_probe2_stops_on_memory_after_the_first_item_with_the_lower_limit(env, monkeypatch):
    rc, _ = _guarded(env, monkeypatch, [9500.0, 9500.0, 9500.0], [2.0] * 5)
    assert rc == 76                                                           # 9,500 is allowed for the first item (10,000) but not for the second (9,000)
    rows = common.read_jsonl(env / "P2-PROBE-X" / "items.jsonl")
    assert [r["idx"] for r in rows] == [0]
    e = common.read_jsonl(env / "P2-PROBE-X" / "chunks.jsonl")[-1]
    assert e["event"] == "guard_stop" and e["source"] == "probe2_guarded" and "gpu_memory" in e["reason"]


def test_guarded_probe2_rise_rule_slow_item_and_ac(env, monkeypatch):
    rc, _ = _guarded(env, monkeypatch, [3000.0, 5000.0], [2.0] * 5)
    assert rc == 76 and "rise" in common.read_jsonl(env / "P2-PROBE-X" / "chunks.jsonl")[-1]["reason"]
    (env / "P2-PROBE-X" / "items.jsonl").unlink()
    rc, _ = _guarded(env, monkeypatch, [3000.0] * 6, [2.0, 2.0, 2.0, 9.0, 2.0])
    assert rc == 76 and [r["idx"] for r in common.read_jsonl(env / "P2-PROBE-X" / "items.jsonl")] == [0, 1, 2, 3]       # the slow row is kept, then stop
    (env / "P2-PROBE-X" / "items.jsonl").unlink()
    rc, _ = _guarded(env, monkeypatch, [3000.0] * 6, [2.0] * 5, ac=lambda: False)
    assert rc == 76 and not (env / "P2-PROBE-X" / "items.jsonl").exists()                 # battery: nothing ran


def test_guarded_probe2_checks_ac_again_right_before_the_model_load(env, monkeypatch):
    acs = iter([True, False])
    calls = []
    rc, _ = _guarded(env, monkeypatch, [3000.0] * 6, [2.0] * 5, ac=lambda: next(acs), calls=calls)
    assert rc == 76 and "ac_lost_before_load" in common.read_jsonl(env / "P2-PROBE-X" / "chunks.jsonl")[-1]["reason"]
    assert not (env / "P2-PROBE-X" / "items.jsonl").exists()


def test_guarded_probe2_respects_hold_files(env, monkeypatch):
    (env / "P2-PROBE-02").mkdir()
    (env / "P2-PROBE-02" / "HOLD.txt").write_text("on hold")
    called = []
    rc = probe2_guarded.run_guarded(["--run-id", "P2-PROBE-02"], probe_main=lambda: called.append(1), cuda=Cuda([0.0]), events_fn=lambda since: dict(ok=True, events=[], error=None))
    assert rc == 7 and called == []
    (env / "P2-PROBE-02" / "HOLD.txt").unlink()

    def sneaky(cuda):
        def main():
            (env / "P2-PROBE-Y").mkdir(exist_ok=True)
            for i in range(4):
                if i == 2:
                    (env / "GATE-HOLD.txt").write_text("hold")
                cuda.mem_get_info()
                common.append_jsonl(env / "P2-PROBE-Y" / "items.jsonl", dict(idx=i, seconds=1.0))
            return 0
        return main
    cuda = Cuda([100.0] * 10)
    rc = probe2_guarded.run_guarded(["--run-id", "P2-PROBE-Y"], probe_main=sneaky(cuda), cuda=cuda, watchdog_factory=lambda g, run: SimpleNamespace(start=lambda: None, stop=lambda: None),
                                    ac_fn=lambda: True, events_fn=lambda since: dict(ok=True, events=[], error=None))
    assert rc == 7 and len(common.read_jsonl(env / "P2-PROBE-Y" / "items.jsonl")) == 2


def test_run_probe2_file_is_not_modified_by_this_work():
    import subprocess
    out = subprocess.run(["git", "-C", str(ROOT), "diff", "--stat", "HEAD", "--", "exp_p2/run_probe2.py", "exp_p2/run_probe1.py", "exp_p2/scoring.py", "exp_p2/driver.py", "tools/gpu_guard.py"],
                         capture_output=True, text=True).stdout
    assert out.strip() == ""


# ------------------------------------------------------------------------------------------------ probe-1 wrapper (M0 stage 2) and the event-log line
class Cuda1(Cuda):
    """Probe 1 does not call mem_get_info per item; it calls reset_peak_memory_stats at the start of every item."""

    def __init__(self, used_seq):
        super().__init__(used_seq)
        self.cap = None
        self.resets = 0

    def reset_peak_memory_stats(self):
        self.resets += 1

    def set_per_process_memory_fraction(self, f):
        self.cap = f


def _probe1_main(cuda, run_id, seconds, calls=None):
    def main():
        if calls is not None:
            calls.append(("argv", sys.argv[:]))
        run = Path(common.RUNS) / run_id
        run.mkdir(parents=True, exist_ok=True)
        for i, sec in enumerate(seconds):
            cuda.reset_peak_memory_stats()
            common.append_jsonl(run / "items.jsonl", dict(idx=i, seconds=sec))
        return 0
    return main


def _guarded1(env, used, seconds, ac=lambda: True, argv=(), calls=None, events=None):
    from exp_p2.gate import probe1_guarded
    cuda = Cuda1(used)
    orig = (cuda.reset_peak_memory_stats, cuda.mem_get_info, common.append_jsonl)
    rc = probe1_guarded.run_guarded(["--run-id", "P2-M0-STAGE2", "--n", "10", "--limit", "10", *argv], probe_main=_probe1_main(cuda, "P2-M0-STAGE2", seconds, calls), cuda=cuda,
                                    watchdog_factory=lambda g, run: SimpleNamespace(start=lambda: None, stop=lambda: None), ac_fn=ac,
                                    events_fn=events or (lambda since: dict(ok=True, events=[], error=None)))
    assert (cuda.reset_peak_memory_stats, cuda.mem_get_info, common.append_jsonl) == orig
    return rc, cuda


def test_probe1_wrapper_passes_a_healthy_run_sets_the_cap_and_strips_its_flags(env):
    calls = []
    rc, cuda = _guarded1(env, [3000.0] * 6, [2.0] * 4, calls=calls, argv=("--mem-frac", "0.6"))
    assert rc == 0 and cuda.cap == 0.6 and cuda.resets == 4                 # probe 1 has no cap of its own: the wrapper sets it; the per-item hook still calls the real function
    assert len(common.read_jsonl(env / "P2-M0-STAGE2" / "items.jsonl")) == 4
    assert calls[0][1] == ["run_probe1", "--run-id", "P2-M0-STAGE2", "--n", "10", "--limit", "10"]      # '--n' is not read as '--no-ac-check'; probe 1 sees only its own flags


def test_probe1_wrapper_memory_rise_slow_item_battery_and_hold(env):
    rc, _ = _guarded1(env, [9500.0, 9500.0, 9500.0], [2.0] * 4)
    assert rc == 76 and [r["idx"] for r in common.read_jsonl(env / "P2-M0-STAGE2" / "items.jsonl")] == [0]          # 10,000 first item, 9,000 later
    e = common.read_jsonl(env / "P2-M0-STAGE2" / "chunks.jsonl")[-1]
    assert e["event"] == "guard_stop" and e["source"] == "probe1_guarded" and "gpu_memory" in e["reason"]
    (env / "P2-M0-STAGE2" / "items.jsonl").unlink()
    rc, _ = _guarded1(env, [3000.0, 5000.0], [2.0] * 4)
    assert rc == 76 and "rise" in common.read_jsonl(env / "P2-M0-STAGE2" / "chunks.jsonl")[-1]["reason"]
    (env / "P2-M0-STAGE2" / "items.jsonl").unlink()
    rc, _ = _guarded1(env, [3000.0] * 6, [2.0, 2.0, 2.0, 9.0, 2.0])
    assert rc == 76 and [r["idx"] for r in common.read_jsonl(env / "P2-M0-STAGE2" / "items.jsonl")] == [0, 1, 2, 3]
    (env / "P2-M0-STAGE2" / "items.jsonl").unlink()
    rc, cuda = _guarded1(env, [3000.0] * 6, [2.0] * 4, ac=lambda: False)
    assert rc == 76 and cuda.cap is None and not (env / "P2-M0-STAGE2" / "items.jsonl").exists()                    # battery: nothing ran, not even the cap
    (env / "GATE-HOLD.txt").write_text("hold")
    rc, _ = _guarded1(env, [3000.0] * 6, [2.0] * 4)
    assert rc == 7


def test_probe1_wrapper_does_not_touch_run_probe1():
    import subprocess
    out = subprocess.run(["git", "-C", str(ROOT), "diff", "--stat", "HEAD", "--", "exp_p2/run_probe1.py"], capture_output=True, text=True).stdout
    assert out.strip() == ""
    from exp_p2.gate import probe1_guarded
    assert probe1_guarded._g.PROBE1_SPEC["module"] == "run_probe1" and probe1_guarded._g.PROBE1_SPEC["default_run"] == "P2-PROBE-01"


def test_event_log_line_is_printed_at_the_start_of_every_hand_launched_stage(env, capsys, monkeypatch):
    ev = dict(ok=True, events=[dict(id=41, log="System", time="2026-10-27T23:25:29+05:30", message="The system has rebooted without cleanly shutting down first")], error=None)
    _guarded1(env, [3000.0] * 3, [2.0], events=lambda since: ev)
    out = capsys.readouterr().out
    assert out.splitlines()[0].startswith("event-log check (last 12 h): 1 crash-signature event(s), latest Id 41 System at 2026-10-27T23:25:29") and "review before launching" in out
    assert eventlog.summary_line(dict(ok=True, events=[], error=None), 12).endswith("Application 1001 GPU)") and "no crash-signature" in eventlog.summary_line(dict(ok=True, events=[], error=None), 12)
    assert "UNREADABLE" in eventlog.summary_line(dict(ok=False, events=[], error="boom"), 6)
    seen = []
    _guarded1(env, [3000.0] * 3, [2.0], argv=("--eventlog-hours", "3"), events=lambda since: seen.append(since) or dict(ok=True, events=[], error=None))
    assert len(seen) == 1 and (datetime.now() - seen[0]).total_seconds() == pytest.approx(3 * 3600, abs=30)
    capsys.readouterr()
    _guarded1(env, [3000.0] * 3, [2.0], argv=("--no-eventlog-check",), events=lambda since: (_ for _ in ()).throw(AssertionError("must not query")))
    assert "event-log check" not in capsys.readouterr().out
    # probe 2 wrapper and M0 stage 1 print it too
    rc, _ = _guarded(env, monkeypatch, [3000.0] * 5, [2.0] * 5)
    from exp_p2 import run_gate_m0
    monkeypatch.setattr(eventlog, "new_events", lambda since: ev)
    monkeypatch.setattr(guards, "on_ac", lambda: False)
    capsys.readouterr()
    assert run_gate_m0.main(["--run-id", "P2-M0-STAGE1"]) == 76
    assert capsys.readouterr().out.startswith("event-log check (last 12 h): 1 crash-signature event(s)")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
