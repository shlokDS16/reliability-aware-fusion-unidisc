"""--slow-factor / --slow-min-s (2026-10-28): the slow-item guard rule is configurable from every parser that builds a Guards / OmniGuards, with the dataclass defaults (2.0 / 1.0) unchanged
when the flags are absent. CPU only; no GPU, no model."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from exp_p2 import common                                                              # noqa: E402
from exp_p2.gate import gate_driver, guards, probe2_guarded, runner                    # noqa: E402
from exp_p2.omni import build                                                          # noqa: E402
from test_gate_safety import env, _guarded                                             # noqa: E402,F401  (fixture + probe-2 harness of the existing safety tests)
from test_gate_integration import driver, _capture, _parse_with_the_runner             # noqa: E402,F401

FLAGS = ["--slow-factor", "3", "--slow-min-s", "2"]
PRIOR = [1.4, 1.4, 1.4]                                                                 # median 1.4 s: the default rule trips above 2.8 s, the relaxed one above 4.2 s


def test_dataclass_defaults_are_unchanged():
    g = guards.Guards()
    assert (g.slow_factor, g.slow_min_s) == (2.0, 1.0)
    assert (build.OmniGuards().slow_factor, build.OmniGuards().slow_min_s) == (2.0, 1.0)


def _feed(g, times):
    return [g.after_item(t) for t in times]


def test_relaxed_rule_lets_a_3s_item_through_and_stops_a_5s_item():
    g = guards.Guards(slow_factor=3.0, slow_min_s=2.0)
    assert _feed(g, PRIOR + [3.0]) == [None] * 4                                        # 3.0 s against a 1.4 s median does not trip
    g = guards.Guards(slow_factor=3.0, slow_min_s=2.0)
    out = _feed(g, PRIOR + [5.0])
    assert out[:3] == [None] * 3 and out[3] and out[3].startswith("slow_item")
    assert _feed(guards.Guards(), PRIOR + [3.0])[3] is not None                          # the default rule does trip on the same item (this is tonight's stop)


def test_slow_min_s_floor_is_honoured():
    g = guards.Guards(slow_factor=1.5, slow_min_s=2.0)
    assert _feed(g, [0.5, 0.5, 0.5, 1.9]) == [None] * 4                                  # 3.8x the median but under the 2 s floor
    assert guards.Guards(slow_factor=1.5, slow_min_s=2.0).after_item(2.5) is None        # fewer than min_items_for_median earlier items: never trips
    g = guards.Guards(slow_factor=1.5, slow_min_s=2.0)
    assert _feed(g, [0.5, 0.5, 0.5, 2.5])[3] is not None


# ------------------------------------------------------------------------------------------------ runner.base_parser / guards_from_args (m1..m5, s2, foil, suite, epred chunk)
def test_runner_parser_defaults_and_flags():
    ns = runner.base_parser("X", 1).parse_args([])
    assert (ns.slow_factor, ns.slow_min_s) == (2.0, 1.0)
    g = runner.guards_from_args(ns)
    assert (g.slow_factor, g.slow_min_s) == (2.0, 1.0)
    ns = runner.base_parser("X", 1).parse_args(FLAGS)
    assert (ns.slow_factor, ns.slow_min_s) == (3.0, 2.0)
    g = runner.guards_from_args(ns)
    assert (g.slow_factor, g.slow_min_s) == (3.0, 2.0)
    assert _feed(g, PRIOR + [3.0]) == [None] * 4 and _feed(runner.guards_from_args(ns), PRIOR + [5.0])[3] is not None


# ------------------------------------------------------------------------------------------------ omni.build.omni_parser / omni_guards_from_args (omni timing, family R)
def test_omni_parser_defaults_and_flags():
    ns = build.omni_parser("X", None).parse_args([])
    g = build.omni_guards_from_args(ns)
    assert isinstance(g, build.OmniGuards) and (ns.slow_factor, ns.slow_min_s) == (2.0, 1.0) and (g.slow_factor, g.slow_min_s) == (2.0, 1.0)
    ns = build.omni_parser("X", None).parse_args(FLAGS)
    g = build.omni_guards_from_args(ns)
    assert (g.slow_factor, g.slow_min_s) == (3.0, 2.0)
    assert _feed(g, PRIOR + [3.0]) == [None] * 4
    assert _feed(build.omni_guards_from_args(ns), PRIOR + [5.0])[3] is not None


# ------------------------------------------------------------------------------------------------ probe2_guarded.run_guarded (its own argparse), end to end on the fake CUDA
def test_probe2_guarded_default_rule_stops_on_a_3s_item(env, monkeypatch):
    rc, _ = _guarded(env, monkeypatch, [3000.0] * 6, PRIOR + [3.0])
    assert rc == 76 and "slow_item" in common.read_jsonl(env / "P2-PROBE-X" / "chunks.jsonl")[-1]["reason"]


def test_probe2_guarded_flags_relax_and_still_catch_a_5s_item(env, monkeypatch):
    rc, _ = _guarded(env, monkeypatch, [3000.0] * 6, PRIOR + [3.0], argv=FLAGS)
    assert rc == 0
    (env / "P2-PROBE-X" / "items.jsonl").unlink()
    rc, _ = _guarded(env, monkeypatch, [3000.0] * 6, PRIOR + [5.0], argv=FLAGS)
    assert rc == 76 and "slow_item" in common.read_jsonl(env / "P2-PROBE-X" / "chunks.jsonl")[-1]["reason"]


def test_probe2_guarded_guards_object_gets_the_values(env, monkeypatch):
    seen = {}
    monkeypatch.setattr(common, "load_net", lambda: "net")
    from types import SimpleNamespace
    from test_gate_safety import Cuda
    noop = SimpleNamespace(start=lambda: None, stop=lambda: None)

    def fac(g, run):
        seen["g"] = g
        return noop
    for argv, want in (([], (2.0, 1.0)), (FLAGS, (3.0, 2.0))):
        probe2_guarded.run_guarded(["--run-id", "P2-PROBE-X", "--n", "1", "--resume", *argv], probe_main=lambda: 0, cuda=Cuda([3000.0]), watchdog_factory=fac, ac_fn=lambda: True,
                                   events_fn=lambda since: dict(ok=True, events=[], error=None))
        assert (seen["g"].slow_factor, seen["g"].slow_min_s) == want


# ------------------------------------------------------------------------------------------------ gate_driver --extra reaches the stage parsers unchanged
@pytest.mark.parametrize("stage,module", [("m2", "exp_p2.run_gate_m2"), ("omni-timing", "exp_p2.run_omni_timing"), ("omni-r-cal", "exp_p2.run_gate_omni_r")])
def test_driver_extra_passes_the_flags_to_the_stage_parser(stage, module, driver, monkeypatch):
    calls = _capture(monkeypatch)
    gate_driver.main(["--stage", stage, "--max-chunks", "1", "--extra", "--slow-factor 3 --slow-min-s 2"])
    cmd = calls[0]
    ns = _parse_with_the_runner(monkeypatch, module, cmd[cmd.index("-m") + 2:])
    assert (ns.slow_factor, ns.slow_min_s) == (3.0, 2.0)
    calls.clear()
    gate_driver.main(["--stage", stage, "--max-chunks", "1"])
    cmd = calls[0]
    ns = _parse_with_the_runner(monkeypatch, module, cmd[cmd.index("-m") + 2:])
    assert (ns.slow_factor, ns.slow_min_s) == (2.0, 1.0)
