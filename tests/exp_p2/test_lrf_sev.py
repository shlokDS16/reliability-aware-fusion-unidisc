"""Severity sweep (EXPLORATORY-PLAN-SEVERITY-2026-10-31.md): the entry point exp_p2/run_gate_lrf_sev.py, the lrf-sev driver stage and the analysis script. CPU only, fake network, temp
directories; nothing is launched and no real array is read."""
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fake_gate import fake_image                                                     # noqa: E402
from test_gate_runners_fake import _fold, _m4_prereqs, _sc, _write_folds             # noqa: E402  (helpers only)
from exp_p2 import common, run_gate_lrf_sev as sev, run_gate_m4 as m4                # noqa: E402
from exp_p2.gate import corruptions, gate_driver, runner                             # noqa: E402
from analysis.paper2.lrf import e1_severity as E                                      # noqa: E402

FAM = [("jpeg", 10), ("noise", 0.1), ("splice", 128)]
GOOD = ["--run-id", "P2-LRF-SEV", "--folds-path", "f.json", "--family-run", "P2-LRF-PLAN", "--sanity", "", "--denoise-for", "", "--tbv", "on", "--layout-fix", "13", "--neg-len"]


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "_cuda", lambda: None)
    monkeypatch.setattr(common, "load_image", lambda iid: fake_image(iid, 96))
    return tmp_path


def _ctx(env, sc, n=3):
    _m4_prereqs(env, sc, FAM)
    items = _fold(n, offset=2000)
    for i, it in enumerate(items):
        it["neg_caption_len"] = items[(i + 2) % n]["caption"]
    _write_folds(env, test=items)
    a = SimpleNamespace(tbv="on", denoise_for="", sanity="", neg_len=True, caption_slot_len=sev.L_FIX)
    (env / "P2-LRF-SEV").mkdir(exist_ok=True)
    return items, m4.make_ctx_factory(a, env)(sc, env / "P2-LRF-SEV")


def test_unchanged_pinned_runner():
    pins = json.loads((ROOT / "runs" / "P2-LRF-PINS" / "pins.json").read_text(encoding="utf8"))
    h = hashlib.sha256((ROOT / "exp_p2" / "run_gate_m4.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    assert h == pins["entry_points"]["exp_p2/run_gate_m4.py"]


def test_common_random_numbers_scale_one_standard_normal():
    a = np.random.default_rng([7, 11, 100]).normal(0.0, 0.05, size=1000)
    b = np.random.default_rng([7, 11, 100]).normal(0.0, 0.3, size=1000)
    assert np.array_equal(a * 6.0, b) or np.allclose(a * 6.0, b, rtol=0, atol=1e-12)


def test_flag_off_calls_the_l1_runner_untouched(monkeypatch):
    seen = {}
    monkeypatch.setattr(m4, "main", lambda argv=None: seen.update(argv=list(argv)) or 0)
    before = (m4.build_conditions, m4.process, m4.make_ctx_factory, runner.run_items)
    assert sev.main(["--run-id", "X"]) == 0 and seen["argv"] == ["--run-id", "X"]
    assert sev.main(["--sweep", "none", "--run-id", "X"]) == 0 and seen["argv"] == ["--run-id", "X"]
    assert before == (m4.build_conditions, m4.process, m4.make_ctx_factory, runner.run_items)


def test_hooks_are_restored_after_an_error():
    orig = (m4.build_conditions, m4.process, m4.make_ctx_factory, runner.run_items)
    with pytest.raises(RuntimeError):
        with sev.sev_patched({}):
            raise RuntimeError("boom")
    assert orig == (m4.build_conditions, m4.process, m4.make_ctx_factory, runner.run_items)


def test_flag_on_item_has_the_three_levels_and_the_positive_control(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    m4.process(sc, items[1], ctx)                                                     # warm
    ref_row, ref_arr = m4.process(sc, items[1], ctx)                                  # the L1 path (flag off)
    with sev.sev_patched({}):
        ctx.sev_side = {}
        m4.process(sc, items[1], ctx)
        row, arr = m4.process(sc, items[1], ctx)
        assert ctx.sev_side == {}
    assert set(row["conds"]) == {"noise0.05", "noise0.2", "noise0.3"}
    for name in row["conds"]:
        assert row["conds"][name]["kind"] == "pixel" and row["conds"][name]["txt"] == {}
        for key in ("B", "D", "s3", "tbv", "tex", "nbr", "delta", "deltaL", "flag0.05", "codes", "z"):
            assert f"{name}_{key}" in arr, (name, key)
    assert np.array_equal(arr[sev.PC_KEY], ref_arr["noise0.1_codes"])               # same stream and call as L1 at sigma 0.1
    assert np.array_equal(arr["noise0.05_delta"].shape, ref_arr["noise0.1_delta"].shape)
    assert row["n_rows"] < ref_row["n_rows"] and row["slot_len"] == sev.L_FIX


def test_levels_use_the_l1_noise_stream(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    pil, _ = __import__("exp_p2.gate.pipeline", fromlist=["x"]).prep_image(sc, items[0]["image_id"])
    ctx.sev_side = {}
    conds = sev.build_conditions_sev(sc, items[0], pil, None, ctx)
    for s in sev.SIGMAS:
        img = corruptions.apply_pixel("noise", s, pil, m4.rung_rng(items[0]["gid"], "noise", 0), None)
        got = next(c for c in conds if c["name"] == sev.sev_key(s))
        assert np.array_equal(got["pix"], np.asarray(img)) and np.array_equal(got["codes"], sc.encode(img))
    assert [c["name"] for c in conds] == ["noise0.05", "noise0.2", "noise0.3"]


def test_flag_on_requires_the_l1_flags_and_a_new_run_id(monkeypatch, capsys):
    assert sev.check_flags(GOOD) == []
    for rid in ("P2-LRF-L1", "P2-LRF-DN", "P2-GATE-M4"):
        flags = GOOD.copy()
        flags[1] = rid
        assert sev.check_flags(flags), rid
    assert sev.check_flags([f for f in GOOD if f != "--neg-len"])
    called = []
    monkeypatch.setattr(m4, "main", lambda argv=None: called.append(argv) or 0)
    assert sev.main(["--sweep", "noise", "--run-id", "P2-LRF-DN"]) == 2 and not called
    assert "STOP" in capsys.readouterr().err
    assert sev.main(["--sweep", "noise"] + GOOD) == 0 and called[0] == GOOD


def test_run_config_records_the_sweep(monkeypatch):
    seen = {}
    monkeypatch.setattr(runner, "run_items", lambda **kw: seen.update(kw) or 0)
    with sev.sev_patched(sev.sweep_record()):
        runner.run_items(cfg={"stage": "M4"}, process=m4.process)
    assert seen["cfg"]["sweep"] == "noise" and seen["cfg"]["sigmas"] == [0.05, 0.2, 0.3]


def test_driver_stage_lrf_sev_reuses_the_l1_flags_and_leaves_other_stages_alone():
    assert gate_driver.STAGES["lrf-sev"] == ("exp_p2.run_gate_lrf_sev", "P2-LRF-SEV", 450)
    assert gate_driver.STAGE_ARGS["lrf-sev"][:-2] == gate_driver.STAGE_ARGS["lrf-l1"] and gate_driver.STAGE_ARGS["lrf-sev"][-2:] == ["--sweep", "noise"]
    assert gate_driver.resolve_max_chunks("lrf-sev", None) == 20 and gate_driver.resolve_max_chunks("lrf-dn", None) == 24 and gate_driver.resolve_max_chunks("lrf-l1", None) == 60
    assert sev.check_flags(gate_driver.STAGE_ARGS["lrf-sev"] + ["--run-id", "P2-LRF-SEV"]) == []


# ------------------------------------------------------------------------------------------------ the analysis
def _preds(path, cond, ys_none, ys_lrf):
    with open(path, "a", encoding="utf-8") as fh:
        for i, (yn, yl) in enumerate(zip(ys_none, ys_lrf)):
            fh.write(json.dumps(dict(idx=i, gid=8000 + i, image_id=10 + i, condition=cond, y_none=yn, y_lrf=yl)) + "\n")


def test_analysis_known_numbers(tmp_path):
    s, l1 = tmp_path / "S", tmp_path / "L1"
    s.mkdir(), l1.mkdir()
    n = 10
    _preds(l1 / "predictions.jsonl", "clean", [1] * 8 + [0] * 2, [1] * 9 + [0])          # gain +0.1
    _preds(l1 / "predictions.jsonl", "noise0.1", [1] * 5 + [0] * 5, [1] * 8 + [0] * 2)   # gain +0.3
    _preds(s / "predictions.jsonl", "noise0.05", [1] * 7 + [0] * 3, [1] * 7 + [0] * 3)   # gain 0
    _preds(s / "predictions.jsonl", "noise0.2", [1] * 5 + [0] * 5, [1] * 3 + [0] * 7)    # gain -0.2 (harm)
    _preds(s / "predictions.jsonl", "noise0.3", [1] * 4 + [0] * 6, [1] * 4 + [0] * 6)
    res = E.analyse(s, l1, n_expected=None, need_meta=False)
    lv = res["levels"]
    assert lv["0"]["NONE"] == 0.8 and lv["0"]["LRF"] == 0.9 and lv["0"]["LRF_minus_NONE"]["diff"] == pytest.approx(0.1)
    assert lv["0.1"]["LRF_minus_NONE"]["diff"] == pytest.approx(0.3) and lv["0.1"]["source"] == "P2-LRF-L1"
    assert lv["0.2"]["LRF_minus_NONE"]["diff"] == pytest.approx(-0.2) and lv["0.2"]["LRF_minus_NONE"]["c"] == 2
    assert lv["0.2"]["gain_minus_clean_gain"]["diff"] == pytest.approx(-0.3)
    assert lv["0.1"]["gain_minus_clean_gain"]["diff"] == pytest.approx(0.2)
    assert res["levels"]["0.05"]["n"] == n
    a, b = E.analyse(s, l1, None, False), E.analyse(s, l1, None, False)
    assert a["levels"]["0.2"]["LRF_minus_NONE"]["ci95"] == b["levels"]["0.2"]["LRF_minus_NONE"]["ci95"]


def test_analysis_refuses_mismatched_items(tmp_path):
    s, l1 = tmp_path / "S", tmp_path / "L1"
    s.mkdir(), l1.mkdir()
    for c in ("clean", "noise0.1"):
        _preds(l1 / "predictions.jsonl", c, [1, 0, 1], [1, 1, 1])
    for c in ("noise0.05", "noise0.2"):
        _preds(s / "predictions.jsonl", c, [1, 0, 1], [1, 1, 1])
    _preds(s / "predictions.jsonl", "noise0.3", [1, 0], [1, 1])
    with pytest.raises(RuntimeError):
        E.analyse(s, l1, None, False)


def test_analysis_meta_check_and_positive_control_verdict(tmp_path):
    (tmp_path / "lrf_score_meta.json").write_text(json.dumps(dict(conds=["noise0.05", "noise0.2", "noise0.3"], conds_absent_in_rows=[], n_items_skipped_no_arrays=0,
                                                                  positive_control=dict(ok=True), hashes={"x": 1})), encoding="utf8")
    assert E.check_meta(tmp_path, 450)["ok"]
    with pytest.raises(RuntimeError):
        E.check_meta(tmp_path, 449)
    (tmp_path / "lrf_score_meta.json").write_text(json.dumps(dict(conds=["noise0.05"], positive_control=dict(ok=True), hashes={"x": 1})), encoding="utf8")
    with pytest.raises(RuntimeError):
        E.check_meta(tmp_path, 450)
