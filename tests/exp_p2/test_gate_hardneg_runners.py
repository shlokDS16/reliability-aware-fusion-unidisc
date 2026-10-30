"""Family H wiring (DRAFT): `--folds-path` for M3/M4/analysis_m4, `--family-run` for M4 (the n-rule and the corruption family come from H3's own family.json), and the gate_driver stages h3 and h4.
Every default must stay what it was: no option, no change. CPU only, fake scorer, temp directories."""
import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from fake_gate import fake_image                                              # noqa: E402
from test_gate_runners_fake import _fold, _m4_prereqs, _sc, _write_folds       # noqa: E402,F401  (fixture helpers of the existing runner tests)
from test_gate_integration import _capture, _parse_with_the_runner, driver     # noqa: E402,F401  (driver is a fixture)
from exp_p2 import common, run_gate_m3, run_gate_m4                             # noqa: E402
from exp_p2.gate import analysis_m4, folds, gate_driver, runner                 # noqa: E402

H3, H4 = "P2-GATE-H3", "P2-GATE-H4"


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "_cuda", lambda: None)
    monkeypatch.setattr(gate_driver.time, "sleep", lambda s: None)
    monkeypatch.setattr(common, "load_image", lambda iid: fake_image(iid, 96))

    def init_run(run_id, config_):
        d = tmp_path / run_id
        d.mkdir(parents=True, exist_ok=True)
        if not (d / "config.json").exists():
            (d / "config.json").write_text(json.dumps(dict(config_, run_id=run_id)))
        return d
    monkeypatch.setattr(common, "init_run", init_run)
    return tmp_path


def _hard_folds(env, n=4, offset=7000):
    """A family-H folds file: head (H3) and test (H4), SugarCrepe-style negatives that are NOT other items' captions."""
    def mk(off):
        items = _fold(n, offset=off)
        for it in items:
            it.update(neg_caption=it["caption"] + " blue", subset="add_att", n_tok_neg=it["n_tok"] + 1, tok_diff=1, neg_source="sugarcrepe")
        return items
    p = env / "P2-HARDNEG-ITEMS"
    p.mkdir(exist_ok=True)
    doc = dict(meta={}, cal=[], head=mk(6000), test=mk(offset), test_ext=[])
    (p / "folds_hardneg.json").write_text(json.dumps(doc))
    return p / "folds_hardneg.json", doc


def _family(env, run_id, rule, test_fold, fam=(("jpeg", 10),), endpoint="d"):
    (env / run_id).mkdir(exist_ok=True)
    (env / run_id / "family.json").write_text(json.dumps(dict(endpoint=endpoint, n_rule=dict(rule=rule, test_fold=test_fold), family=[dict(corruption=c, severity=s, key=f"{c}{s}") for c, s in fam])))


# ------------------------------------------------------------------------------------------------ defaults unchanged
def test_defaults_are_the_old_ones(env, monkeypatch):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10), ("noise", 0.1)])
    _write_folds(env, test=_fold(4, offset=2000))
    seen = {}
    orig = folds.ensure_folds
    monkeypatch.setattr(folds, "ensure_folds", lambda fn, path=None: seen.setdefault("path", path) or orig(fn, path))
    (env / "P2-GATE-M4").mkdir()
    ctx = run_gate_m4.make_ctx_factory(SimpleNamespace(tbv="off", denoise_for=""), env)(sc, env / "P2-GATE-M4")        # a bare namespace, as the existing tests build it
    assert seen["path"] is None and [it["image_id"] for it in ctx.fold] == [it["image_id"] for it in _fold(4, offset=2000)] and ctx.family == [("jpeg", 10), ("noise", 0.1)]
    assert run_gate_m4.load_prereqs(env)[1] == run_gate_m4.load_prereqs(env, "P2-GATE-M3")[1]
    ns = _parse_with_the_runner(monkeypatch, "exp_p2.run_gate_m4", [])
    assert ns.folds_path is None and ns.family_run == "P2-GATE-M3"
    assert _parse_with_the_runner(monkeypatch, "exp_p2.run_gate_m3", []).folds_path is None
    assert _parse_with_the_runner(monkeypatch, "exp_p2.gate.analysis_m4", []).folds_path is None


def test_the_default_config_of_an_m4_run_has_no_family_h_keys(env, monkeypatch):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    captured = {}
    monkeypatch.setattr(runner, "run_items", lambda **kw: captured.update(kw) or 0)
    assert run_gate_m4.main(["--n", "300", "--sanity", "", "--denoise-for", ""]) == 0
    assert not {"folds_path", "folds_sha256", "family_run"} & set(captured["cfg"])


# ------------------------------------------------------------------------------------------------ --folds-path
def test_folds_path_loads_the_h_items_with_their_own_negatives(env):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    path, doc = _hard_folds(env)
    (env / "P2-GATE-M4").mkdir()
    a = SimpleNamespace(tbv="off", denoise_for="", folds_path=str(path), family_run=None)
    ctx = run_gate_m4.make_ctx_factory(a, env)(sc, env / "P2-GATE-M4")
    assert ctx.fold == doc["test"] and all(it["neg_caption"].endswith(" blue") for it in ctx.fold)          # splice donors come from the H4 images, not from folds.json
    assert not (env / "P2-GATE-FOLDS" / "folds.json").exists()                                              # the default folds file was neither read nor built


def test_an_explicit_folds_path_that_does_not_exist_is_never_built(env, tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        run_gate_m3.load_folds(lambda c: 6, str(tmp_path / "nope.json"))
    assert not (tmp_path / "nope.json").exists() and not (env / "P2-GATE-FOLDS" / "folds.json").exists()


def test_m3_reads_the_head_list_of_the_given_file(env):
    path, doc = _hard_folds(env)
    sc = _sc()
    (env / "P2-GATE-H3").mkdir()
    items = run_gate_m3.get_items(sc, env / "P2-GATE-H3", None, str(path))
    assert items == doc["head"]
    assert run_gate_m3.make_ctx(sc, env / "P2-GATE-H3", str(path)).fold == doc["head"]
    assert (env / "P2-GATE-H3" / "token_exclusions.json").exists()


def test_main_refuses_a_missing_folds_file_before_any_model_is_loaded(env, monkeypatch):
    monkeypatch.setattr(runner, "run_items", lambda **kw: (_ for _ in ()).throw(AssertionError("must not start")))
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    _family(env, H3, "R1", 300)
    assert run_gate_m4.main(["--n", "300", "--sanity", "", "--folds-path", str(env / "missing.json"), "--family-run", H3]) == 2
    assert run_gate_m3.main(["--folds-path", str(env / "missing.json")]) == 2


def test_analysis_m4_takes_the_folds_path(env, capsys):
    _family(env, H3, "R1", 300)
    (env / "P2-GATE-M1").mkdir(exist_ok=True)
    (env / "P2-GATE-M1" / "detection_frozen.json").write_text(json.dumps(dict(frozen={})))
    rc = analysis_m4.main(["--run-id", H4, "--family-run", H3, "--folds-path", str(env / "missing.json"), "--skip-selftest"])
    assert rc == 2 and "does not exist" in capsys.readouterr().err


# ------------------------------------------------------------------------------------------------ the n-rule of family H
def test_n_is_checked_against_h3s_own_family_file_not_m3s(env):
    _family(env, "P2-GATE-M3", "R2", 500)
    _family(env, H3, "R1", 300)
    assert run_gate_m4.check_n_against_rule(300, env, H3) == 300 and run_gate_m4.check_n_against_rule(None, env, H3) == 300
    with pytest.raises(ValueError, match="--n 300"):
        run_gate_m4.check_n_against_rule(300, env)                                    # default: M3's R2 still refuses 300
    with pytest.raises(ValueError, match="--n 500"):
        run_gate_m4.check_n_against_rule(500, env, H3)                                # and H3's rule still refuses a wrong n: there is no bypass
    _family(env, H3, "R2", 500)
    assert run_gate_m4.check_n_against_rule(500, env, H3) == 500
    with pytest.raises(ValueError):
        run_gate_m4.check_n_against_rule(300, env, H3)


def test_a_missing_h3_family_file_stops_the_run(env):
    _family(env, "P2-GATE-M3", "R1", 300)
    with pytest.raises(FileNotFoundError):
        run_gate_m4.check_n_against_rule(300, env, H3)
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    with pytest.raises(FileNotFoundError, match="P2-GATE-H3"):
        run_gate_m4.load_prereqs(env, H3)


def test_the_corruption_family_comes_from_the_same_family_run(env):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10), ("noise", 0.1), ("splice", 128)])
    _family(env, H3, "R1", 300, fam=(("jpeg", 5), ("noise", 0.2)))
    assert [c for c, _ in run_gate_m4.load_prereqs(env)[1]] == ["jpeg", "noise", "splice"]
    thr, fam, _ = run_gate_m4.load_prereqs(env, H3)
    assert fam == [("jpeg", 5), ("noise", 0.2)] and set(thr) == {0.05, 0.01, 0.1}                  # thresholds are still M2's
    _family(env, H3, "R1", 300, endpoint="z")
    with pytest.raises(ValueError, match="endpoint"):
        run_gate_m4.load_prereqs(env, H3)


def test_main_runs_end_to_end_up_to_the_loop_with_family_h_options(env, monkeypatch):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    path, doc = _hard_folds(env)
    _family(env, H3, "R1", 4)                                                         # a 4-item rule so that the fake H4 file (4 items) is complete
    captured = {}
    monkeypatch.setattr(runner, "run_items", lambda **kw: captured.update(kw) or 0)
    assert run_gate_m4.main(["--run-id", H4, "--n", "4", "--sanity", "", "--denoise-for", "", "--folds-path", str(path), "--family-run", H3]) == 0
    cfg = captured["cfg"]
    assert cfg["folds_path"] == str(path) and cfg["family_run"] == H3 and len(cfg["folds_sha256"]) == 64 and cfg["n_items"] == 4
    (env / H4).mkdir(exist_ok=True)
    items = captured["get_items"](_sc(), env / H4)
    assert items == doc["test"]
    ctx = captured["make_ctx"](_sc(), env / H4)
    assert ctx.fold == doc["test"] and ctx.family == [("jpeg", 10)]
    monkeypatch.setattr(runner, "run_items", lambda **kw: (_ for _ in ()).throw(AssertionError("must not start")))
    assert run_gate_m4.main(["--run-id", H4, "--n", "300", "--sanity", "", "--denoise-for", "", "--folds-path", str(path), "--family-run", H3]) == 2      # wrong n for H3's rule


# ------------------------------------------------------------------------------------------------ gate_driver stages
def test_the_h_stages_are_in_the_table_and_nothing_else_changed():
    assert gate_driver.STAGES["h3"] == ("exp_p2.run_gate_m4", H3, 50) and gate_driver.STAGES["h4"] == ("exp_p2.run_gate_m4", H4, 300)
    assert gate_driver.STAGES["m3"] == ("exp_p2.run_gate_m3", "P2-GATE-M3", 100) and gate_driver.STAGES["m4"] == ("exp_p2.run_gate_m4", "P2-GATE-M4", 300)
    assert "m3" not in gate_driver.STAGE_ARGS and "m4" not in gate_driver.STAGE_ARGS and "m5" not in gate_driver.STAGE_ARGS
    fp = str(gate_driver.HARDNEG_FOLDS)
    fp3 = str(gate_driver.HARDNEG_FOLDS_H3)       # SAP A5.11 delta 1: H3 runs the M4 stage on the derived H3 file under the plan family
    assert gate_driver.STAGE_ARGS["h3"] == ["--folds-path", fp3, "--family-run", "P2-GATE-H3-PLAN"] and gate_driver.STAGE_ARGS["h4"] == ["--folds-path", fp, "--family-run", H3]
    assert gate_driver.HARDNEG_FOLDS_H3.parts[-2:] == ("P2-HARDNEG-ITEMS", "folds_hardneg_h3.json")
    assert gate_driver.HARDNEG_FOLDS.parts[-2:] == ("P2-HARDNEG-ITEMS", "folds_hardneg.json")


@pytest.mark.parametrize("stage", ["h3", "h4"])
def test_the_h_stages_launch_a_command_their_runner_parses(stage, driver, monkeypatch):
    calls = _capture(monkeypatch, rc=0)
    gate_driver.main(["--stage", stage, "--max-chunks", "1"])
    cmd = calls[0]
    i = cmd.index("--")
    assert cmd[i + 3] == gate_driver.STAGES[stage][0]
    ns = _parse_with_the_runner(monkeypatch, cmd[i + 3], cmd[i + 4:])
    assert ns.run_id == (H3 if stage == "h3" else H4) and ns.n == (50 if stage == "h3" else 300) and ns.resume
    assert ns.folds_path == str(gate_driver.HARDNEG_FOLDS_H3 if stage == "h3" else gate_driver.HARDNEG_FOLDS)
    assert ns.family_run == ("P2-GATE-H3-PLAN" if stage == "h3" else H3)
    assert (common.RUNS / ns.run_id).is_dir()


@pytest.mark.parametrize("stage", ["m3", "m4"])
def test_the_old_stages_still_launch_without_the_new_options(stage, driver, monkeypatch):
    calls = _capture(monkeypatch, rc=0)
    gate_driver.main(["--stage", stage, "--max-chunks", "1"])
    cmd = calls[0]
    assert "--folds-path" not in cmd and "--family-run" not in cmd
    ns = _parse_with_the_runner(monkeypatch, cmd[cmd.index("--") + 3], cmd[cmd.index("--") + 4:])
    assert ns.folds_path is None and getattr(ns, "family_run", "P2-GATE-M3") == "P2-GATE-M3"


def test_a_user_extra_flag_can_still_override_the_h4_family_run(driver, monkeypatch):
    calls = _capture(monkeypatch)
    gate_driver.main(["--stage", "h4", "--max-chunks", "1", "--extra", "--family-run P2-GATE-H3B"])
    cmd = calls[0]
    ns = _parse_with_the_runner(monkeypatch, "exp_p2.run_gate_m4", cmd[cmd.index("--") + 4:])
    assert ns.family_run == "P2-GATE-H3B"
