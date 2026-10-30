"""E1 (pixel denoiser before scoring, EXPLORATORY-PLAN-BASELINES-2026-10-30.md): the entry point exp_p2/run_gate_lrf_dn.py, the lrf-dn driver stage and the analysis script. CPU only, fake network,
temp directories; nothing is launched and no real array is read."""
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fake_gate import fake_image                                                     # noqa: E402
from test_gate_runners_fake import _fold, _m4_prereqs, _sc, _write_folds             # noqa: E402  (helpers only)
from exp_p2 import common, run_gate_lrf_dn as dn, run_gate_m4 as m4                  # noqa: E402
from exp_p2.gate import config, corruptions, denoise_check, gate_driver, runner       # noqa: E402
from analysis.paper2.lrf import e1_denoise as E1                                      # noqa: E402

FAM = [("jpeg", 10), ("noise", 0.1), ("splice", 128)]


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
    a = SimpleNamespace(tbv="on", denoise_for="", sanity="", neg_len=True, caption_slot_len=dn.L_FIX)
    (env / "P2-LRF-DN").mkdir(exist_ok=True)
    return items, m4.make_ctx_factory(a, env)(sc, env / "P2-LRF-DN")


def _small_array():
    rng = np.random.default_rng(3)
    a = (np.clip(120 + 60 * np.sin(np.add.outer(np.arange(96), np.arange(96)) / 9.0)[..., None] + rng.normal(0, 25, (96, 96, 3)), 0, 255)).astype(np.uint8)
    return a


# ------------------------------------------------------------------------------------------------ the transform
def test_denoise_transform_is_the_s_dn_setting_of_denoise_check():
    import cv2
    from PIL import Image
    pil = Image.fromarray(_small_array())
    got = np.asarray(dn.denoise_nlm_sdn(pil))
    assert np.array_equal(got, denoise_check.chosen(pil))                            # Study 1's chosen arm
    assert np.array_equal(got, np.asarray(corruptions.denoise(pil, config.DENOISE_PARAMS)))
    ref = cv2.cvtColor(cv2.fastNlMeansDenoisingColored(cv2.cvtColor(_small_array(), cv2.COLOR_RGB2BGR), None, 25.5, 25.5, 7, 21), cv2.COLOR_BGR2RGB)     # literal h = hColor = 25.5, windows 7 and 21
    assert np.array_equal(got, ref) and not np.array_equal(got, _small_array())


def test_unchanged_pinned_runner_and_parameters():
    pins = json.loads((ROOT / "runs" / "P2-LRF-PINS" / "pins.json").read_text(encoding="utf8"))
    h = hashlib.sha256((ROOT / "exp_p2" / "run_gate_m4.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    assert h == pins["entry_points"]["exp_p2/run_gate_m4.py"]                        # this change did not touch the pinned L1 runner
    assert dict(config.DENOISE_PARAMS) == dict(h=25.5, hColor=25.5, templateWindowSize=7, searchWindowSize=21)


# ------------------------------------------------------------------------------------------------ flag off = byte-identical
def test_flag_off_calls_the_l1_runner_untouched(monkeypatch):
    seen = {}
    monkeypatch.setattr(m4, "main", lambda argv=None: seen.update(argv=list(argv)) or 0)
    before = (m4.build_conditions, m4.process, m4.make_ctx_factory, runner.run_items)
    assert dn.main(["--run-id", "X", "--limit", "1"]) == 0 and seen["argv"] == ["--run-id", "X", "--limit", "1"]
    assert dn.main(["--denoise", "none", "--run-id", "X"]) == 0 and seen["argv"] == ["--run-id", "X"]
    assert before == (m4.build_conditions, m4.process, m4.make_ctx_factory, runner.run_items)


def test_flag_off_pipeline_is_byte_identical_before_and_after_the_patch_block(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    m4.process(sc, items[0], ctx)                                                    # warms the null caches (n_rows counts the cache fills)
    r0, a0 = m4.process(sc, items[0], ctx)
    with dn.dn_patched({"denoise": "nlm-sdn"}):
        ctx.dn_side = {}
        assert m4.process is not dn and m4.build_conditions is dn.build_conditions_dn
    r1, a1 = m4.process(sc, items[0], ctx)                                           # hooks restored
    assert m4.build_conditions is not dn.build_conditions_dn and runner.run_items.__name__ == "run_items"
    assert r0["conds"].keys() == r1["conds"].keys() == {"clean", "jpeg10", "noise0.1", "splice128"}
    assert {k: v for k, v in r0.items() if k != "seconds"} == {k: v for k, v in r1.items() if k != "seconds"}
    assert a0.keys() == a1.keys()
    assert [k for k in a0 if not np.array_equal(a0[k], a1[k], equal_nan=a0[k].dtype.kind == "f")] == []


def test_hooks_are_restored_after_an_error(env):
    orig = (m4.build_conditions, m4.process, m4.make_ctx_factory, runner.run_items)
    with pytest.raises(RuntimeError):
        with dn.dn_patched({}):
            raise RuntimeError("boom")
    assert orig == (m4.build_conditions, m4.process, m4.make_ctx_factory, runner.run_items)


# ------------------------------------------------------------------------------------------------ flag on
def test_flag_on_item_has_only_the_denoised_conditions_with_the_same_corruption_seed(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    m4.process(sc, items[1], ctx)                                                     # warm
    ref_row, ref_arr = m4.process(sc, items[1], ctx)                                  # the L1 path (flag off)
    with dn.dn_patched({}):
        ctx.dn_side = {}
        m4.process(sc, items[1], ctx)
        row, arr = m4.process(sc, items[1], ctx)
        assert ctx.dn_side == {}                                                      # side channel consumed
    assert set(row["conds"]) == {"jpeg10_nlm", "noise0.1_nlm"}
    for k in ("jpeg10", "noise0.1"):
        name = k + "_nlm"
        assert row["conds"][name]["kind"] == "pixel" and row["conds"][name]["txt"] == {}          # full pixel condition, no text-direction passes
        for key in ("B", "D", "s3", "tbv", "tex", "nbr", "delta", "deltaL", "flag0.05", "codes", "z"):
            assert f"{name}_{key}" in arr, key                                          # everything lrf_score.NEEDED asks for
        assert np.array_equal(arr[f"{name}_codes_corr"], ref_arr[f"{k}_codes"])         # same seed, same corrupted image as L1, before denoising
        assert not np.array_equal(arr[f"{name}_codes"], arr[f"{name}_codes_corr"])
    assert row["n_rows"] < ref_row["n_rows"]
    assert row["slot_len"] == dn.L_FIX and row["gate_layout"] == "fixed"


def test_flag_on_denoised_codes_come_from_the_documented_denoiser(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    pil, _ = __import__("exp_p2.gate.pipeline", fromlist=["x"]).prep_image(sc, items[0]["image_id"])
    with dn.dn_patched({}):
        ctx.dn_side = {}
        conds = dn.build_conditions_dn(sc, items[0], pil, None, ctx)
    img = corruptions.apply_pixel("noise", 0.1, pil, m4.rung_rng(items[0]["gid"], "noise", 0), None)
    want = sc.encode(Image.fromarray(denoise_check.chosen(img)))
    got = next(c for c in conds if c["name"] == "noise0.1_nlm")
    assert np.array_equal(got["codes"], want) and np.array_equal(got["pix"], denoise_check.chosen(img))


def test_flag_on_requires_the_l1_flags_and_a_new_run_id(monkeypatch, capsys):
    good = ["--run-id", "P2-LRF-DN", "--folds-path", "f.json", "--family-run", "P2-LRF-PLAN", "--sanity", "", "--denoise-for", "", "--tbv", "on", "--layout-fix", "13", "--neg-len"]
    assert dn.check_flags(good) == []
    for bad in (["--run-id", "P2-LRF-L1"], ["--tbv", "off"], ["--layout-fix", "12"], ["--sanity", "patch"], ["--denoise-for", "jpeg"], ["--family-run", "P2-GATE-M3"], ["--extra-cells", "shot_noise3"]):
        flags = good.copy()
        for i in range(0, len(bad), 2):
            j = flags.index(bad[i]) if bad[i] in flags else None
            if j is None:
                flags += bad[i:i + 2]
            else:
                flags[j + 1] = bad[i + 1]
        assert dn.check_flags(flags), bad
    assert dn.check_flags([f for f in good if f != "--neg-len"]) and dn.check_flags(good[2:])          # no --neg-len / no --run-id
    called = []
    monkeypatch.setattr(m4, "main", lambda argv=None: called.append(argv) or 0)
    assert dn.main(["--denoise", "nlm-sdn", "--run-id", "P2-GATE-M4"]) == 2 and not called             # refused before the runner is touched
    assert "STOP" in capsys.readouterr().err
    assert dn.main(["--denoise", "nlm-sdn"] + good) == 0 and called and called[0] == good            # the flag is consumed, the rest is forwarded unchanged


def test_run_config_records_the_denoiser(monkeypatch):
    seen = {}
    monkeypatch.setattr(runner, "run_items", lambda **kw: seen.update(kw) or 0)
    with dn.dn_patched(dn.denoise_record()):
        runner.run_items(cfg={"stage": "M4"}, process=m4.process)
    assert seen["cfg"]["stage"] == "M4" and seen["cfg"]["denoise"] == "nlm-sdn" and seen["cfg"]["denoise_params"] == dict(config.DENOISE_PARAMS)
    assert seen["cfg"]["denoise_conditions"] == ["jpeg10_nlm", "noise0.1_nlm"]


def test_driver_stage_lrf_dn_reuses_the_l1_flags_and_leaves_other_stages_alone():
    assert gate_driver.STAGES["lrf-dn"] == ("exp_p2.run_gate_lrf_dn", "P2-LRF-DN", 450)
    assert gate_driver.STAGE_ARGS["lrf-dn"][:-2] == gate_driver.STAGE_ARGS["lrf-l1"] and gate_driver.STAGE_ARGS["lrf-dn"][-2:] == ["--denoise", "nlm-sdn"]
    assert gate_driver.STAGES["lrf-l1"][:2] == ("exp_p2.run_gate_m4", "P2-LRF-L1") and gate_driver.resolve_max_chunks("lrf-l1", None) == 60
    assert gate_driver.resolve_max_chunks("lrf-dn", None) == 24 and gate_driver.resolve_max_chunks("m4", None) == 12
    assert dn.check_flags(gate_driver.STAGE_ARGS["lrf-dn"] + ["--run-id", "P2-LRF-DN"]) == []              # the driver's flags pass the entry point's own check


# ------------------------------------------------------------------------------------------------ the analysis
def _preds(path, cond, ys_none, ys_lrf, L=None):
    with open(path, "a", encoding="utf-8") as fh:
        for i, (yn, yl) in enumerate(zip(ys_none, ys_lrf)):
            r = dict(idx=i, gid=8000 + i, image_id=10 + i, condition=cond, y_none=yn, y_lrf=yl, y_gatem=yn)
            if L:
                r.update(y_none_L=yn, y_lrf_L=yl)
            fh.write(json.dumps(r) + "\n")


def test_analysis_reproduces_known_numbers_on_a_synthetic_input(tmp_path):
    n = 20
    l1_none = [1] * 14 + [0] * 6
    l1_lrf = [1] * 16 + [0] * 4
    dn_none = [1] * 10 + [0] * 4 + [1] * 2 + [0] * 4          # vs NONE: loses items 10-13 (c = 4), gains 14-15 (b = 2)
    dn_lrf = [1] * 16 + [0] * 4                                # equals LRF
    d_dn, d_l1 = tmp_path / "dn", tmp_path / "l1"
    d_dn.mkdir(), d_l1.mkdir()
    for cond in E1.CONDS:
        _preds(d_l1 / "predictions.jsonl", cond, l1_none, l1_lrf, L=True)
        _preds(d_dn / "predictions.jsonl", cond + "_nlm", dn_none, dn_lrf, L=True)
    res = E1.analyse(d_dn, d_l1)
    c = res["cells"]["noise0.1"]
    assert c["n"] == 20 and set(c["arms"]) == {"NONE", "LRF", "DN+NONE", "DN+LRF"}
    a = c["arms"]
    assert a["NONE"]["acc"] == 0.7 and a["LRF"]["acc"] == 0.8 and a["DN+NONE"]["acc"] == 0.6 and a["DN+LRF"]["acc"] == 0.8
    v = a["DN+NONE"]["vs_NONE"]
    assert (v["b"], v["c"]) == (2, 4) and v["diff"] == pytest.approx(-0.1)
    v = a["DN+NONE"]["vs_LRF"]                                                       # LRF right on 0-15, DN+NONE right on 0-9 and 14-15
    assert (v["b"], v["c"]) == (0, 4) and v["diff"] == pytest.approx(-0.2)
    v = a["DN+LRF"]["vs_LRF"]
    assert (v["b"], v["c"]) == (0, 0) and v["diff"] == 0.0 and v["ci95"] == [0.0, 0.0]
    v = a["DN+LRF"]["vs_NONE"]                                                       # +2 (items 14, 15), -0
    assert (v["b"], v["c"]) == (2, 0) and v["diff"] == pytest.approx(0.1) and v["ci95"][0] >= 0.0 and v["ci95"][1] <= 0.25
    assert "length_matched" in c and c["length_matched"]["arms"]["DN+NONE"]["vs_NONE"]["b"] == 2
    assert not any(k.startswith("p_") or k == "p" for k in v)                       # no p-values


def test_analysis_bootstrap_is_10000_resamples_seed_0_and_deterministic(tmp_path):
    rng = np.random.default_rng(5)
    n = 50
    ya, yr = rng.integers(0, 2, n), rng.integers(0, 2, n)
    idx = E1.T3.index_matrix(n, np.random.SeedSequence(0), 10000)
    assert idx.shape == (10000, n)
    got = E1.paired(ya, yr, idx)
    boots = (ya.astype(int) - yr.astype(int))[np.random.default_rng(np.random.SeedSequence(0)).integers(0, n, size=(10000, n))].mean(axis=1)
    assert got["ci95"] == [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]
    assert got["b"] == int(((ya == 1) & (yr == 0)).sum()) and got["c"] == int(((ya == 0) & (yr == 1)).sum()) and got["diff"] == pytest.approx((got["b"] - got["c"]) / n)
    assert E1.paired(ya, yr, idx) == got


def test_analysis_refuses_mismatched_item_sets_and_missing_conditions(tmp_path):
    d_dn, d_l1 = tmp_path / "dn", tmp_path / "l1"
    d_dn.mkdir(), d_l1.mkdir()
    for cond in E1.CONDS:
        _preds(d_l1 / "predictions.jsonl", cond, [1, 0, 1], [1, 1, 1])
    _preds(d_dn / "predictions.jsonl", "noise0.1_nlm", [1, 0], [1, 1])
    with pytest.raises(RuntimeError):
        E1.analyse(d_dn, d_l1)                                                       # jpeg10_nlm absent
    _preds(d_dn / "predictions.jsonl", "jpeg10_nlm", [1, 0], [1, 1])
    with pytest.raises(RuntimeError):
        E1.analyse(d_dn, d_l1)                                                       # 2 items against 3
    assert E1.main(["--dn-run", str(d_dn), "--l1-run", str(d_l1)]) == 2 and not (d_dn / "dn_analysis.json").exists()


def test_analysis_output_schema_matches_the_combiners_file(tmp_path):
    d_dn, d_l1 = tmp_path / "dn", tmp_path / "l1"
    d_dn.mkdir(), d_l1.mkdir()
    for cond in E1.CONDS:
        _preds(d_l1 / "predictions.jsonl", cond, [1, 0, 1, 1], [1, 1, 0, 1])
        _preds(d_dn / "predictions.jsonl", cond + "_nlm", [1, 1, 1, 0], [0, 1, 0, 1])
    assert E1.main(["--dn-run", str(d_dn), "--l1-run", str(d_l1)]) == 0
    r = json.loads((d_dn / "dn_analysis.json").read_text(encoding="utf-8"))
    for cond in ("noise0.1", "jpeg10"):
        cell = r["cells"][cond]
        assert cell["n"] == 4
        for arm in ("DN+NONE", "DN+LRF"):
            assert set(cell["arms"][arm]) >= {"acc", "vs_NONE", "vs_LRF"}
            for ref in ("vs_NONE", "vs_LRF"):
                assert set(cell["arms"][arm][ref]) == {"diff", "ci95", "b", "c"}
    assert r["label"].startswith("exploratory")
