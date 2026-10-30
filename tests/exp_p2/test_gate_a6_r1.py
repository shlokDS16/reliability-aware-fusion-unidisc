"""A6 r1 additions: the gate_driver stages lrf-rescore / lrf-l1 / lrf-lg, the CLIP/SigLIP baseline script (fakes only, nothing downloaded), and the n-rule. CPU only; nothing is launched."""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from fake_gate import FakeScorer, fake_image                                          # noqa: E402
from test_gate_integration import _capture, _parse_with_the_runner, driver, env        # noqa: E402,F401  (fixtures)
from exp_p2 import common, run_gate_m4 as m4                                           # noqa: E402
from exp_p2.gate import config, corruptions, gate_driver, lrf_nrule, suite              # noqa: E402

_bspec = importlib.util.spec_from_file_location("a6_baselines_r1", ROOT / "analysis" / "paper2" / "lrf" / "baselines.py")
BL = importlib.util.module_from_spec(_bspec)
_bspec.loader.exec_module(BL)

LRF_STAGES = ("lrf-rescore", "lrf-l1", "lrf-lg")


# ------------------------------------------------------------------------------------------------ driver stages
def test_lrf_stages_are_in_the_table_and_nothing_existing_changed():
    assert gate_driver.STAGES["lrf-rescore"] == ("exp_p2.run_gate_lrf_rescore", "P2-LRF-RESCORE", 500)
    assert gate_driver.STAGES["lrf-l1"][:2] == ("exp_p2.run_gate_m4", "P2-LRF-L1") and gate_driver.STAGES["lrf-lg"] == ("exp_p2.run_gate_m4", "P2-LRF-LG", 300)
    assert gate_driver.STAGES["m4"] == ("exp_p2.run_gate_m4", "P2-GATE-M4", 300) and gate_driver.STAGES["h4"][1] == "P2-GATE-H4"
    assert "lrf-rescore" in json.dumps(sorted(gate_driver.STAGES)) and gate_driver.STAGE_ARGS["h3"][0] == "--folds-path"
    assert gate_driver.STAGES["lrf-rescore"][1] == importlib.import_module("exp_p2.run_gate_lrf_rescore").RUN_ID


def test_explicit_max_chunks_defaults_apply_to_the_lrf_stages_only():
    assert gate_driver.resolve_max_chunks("lrf-rescore", None) == 40 and gate_driver.resolve_max_chunks("lrf-l1", None) == 60 and gate_driver.resolve_max_chunks("lrf-lg", None) == 40
    for st in ("m1", "m4", "h3", "h4", "s2", "suite", "foil-test"):
        assert gate_driver.resolve_max_chunks(st, None) == 12                                  # the driver default is unchanged for every other stage
    assert gate_driver.resolve_max_chunks("lrf-l1", 7) == 7


def test_default_n_of_lrf_l1_is_the_committed_n_l(tmp_path):
    assert gate_driver.default_n("lrf-l1", 533, tmp_path) == 533                           # no plan file: the 533-list
    (tmp_path / "P2-LRF-PLAN").mkdir()
    (tmp_path / "P2-LRF-PLAN" / "family.json").write_text(json.dumps(dict(endpoint="d", n_rule=dict(rule="A6.3", test_fold=466), family=[])))
    assert gate_driver.default_n("lrf-l1", 533, tmp_path) == 466
    (tmp_path / "P2-LRF-PLAN" / "family.json").write_text("{not json")
    assert gate_driver.default_n("lrf-l1", 533, tmp_path) == 533
    assert gate_driver.default_n("lrf-lg", 300, tmp_path) == 300 and gate_driver.default_n("m4", 300, tmp_path) == 300


@pytest.mark.parametrize("stage", LRF_STAGES)
def test_every_lrf_stage_launches_a_command_its_runner_parses(stage, driver, monkeypatch):
    calls = _capture(monkeypatch, rc=0)
    gate_driver.main(["--stage", stage, "--max-chunks", "1", "--n", str(gate_driver.STAGES[stage][2]), "--extra", gate_driver.LRF_MEM_SLOW])
    assert len(calls) == 1
    cmd = calls[0]
    i = cmd.index("--")
    assert cmd[0] == str(common.GEN_PY) and cmd[1].endswith("gpu_guard.py") and cmd[i + 1] == str(common.GEN_PY) and cmd[i + 2] == "-m" and cmd[i + 3] == gate_driver.STAGES[stage][0]
    ns = _parse_with_the_runner(monkeypatch, cmd[i + 3], cmd[i + 4:])                      # the runner's own argparse accepts every flag, including the empty --sanity / --denoise-for
    assert ns.run_id == gate_driver.STAGES[stage][1] and ns.n == gate_driver.STAGES[stage][2] and ns.resume
    assert (ns.mem_frac, ns.max_used_first_mib, ns.max_used_mib, ns.max_rise_mib, ns.slow_factor, ns.slow_min_s) == (0.75, 11000.0, 11000.0, 4500.0, 3.0, 2.0)      # MEM + slow-rule flags came through --extra
    if stage == "lrf-rescore":
        assert ns.slot_len == 13 and ns.source_run == "P2-GATE-M4"
    else:
        assert ns.folds_path.replace("\\", "/").endswith("P2-LRF-FOLD/folds_lrf.json") and ns.sanity == "" and ns.denoise_for == "" and ns.tbv == "on" and ns.caption_slot_len == 13
    if stage == "lrf-l1":
        assert ns.family_run == "P2-LRF-PLAN" and ns.neg_len and ns.extra_cells == ""
    if stage == "lrf-lg":
        assert ns.family_run == "P2-LRF-PLAN-LG" and not ns.neg_len and ns.extra_cells == "shot_noise3,impulse_noise3,speckle_noise3"
        assert [c[0] for c in m4.parse_extra_cells(ns.extra_cells)] == ["shot_noise3", "impulse_noise3", "speckle_noise3"]


def test_the_mem_and_slow_flags_are_not_baked_into_the_stages():
    for st in LRF_STAGES:
        assert not any(f.startswith("--max-used") or f.startswith("--mem-frac") or f.startswith("--slow") for f in gate_driver.STAGE_ARGS[st])
    assert gate_driver.LRF_MEM_SLOW == "--max-used-first-mib 11000 --max-used-mib 11000 --max-rise-mib 4500 --mem-frac 0.75 --slow-factor 3 --slow-min-s 2"


@pytest.mark.parametrize("stage", LRF_STAGES)
def test_existing_refusals_apply_to_the_lrf_stages(stage, driver, monkeypatch):
    from exp_p2.gate import hold, pins
    calls = _capture(monkeypatch, rc=0)
    monkeypatch.setattr(pins, "dirty_files", lambda: ["M exp_p2/run_gate_m4.py"])
    assert gate_driver.main(["--stage", stage, "--max-chunks", "1"]) == pins.EXIT_DIRTY and not calls
    monkeypatch.setattr(pins, "dirty_files", lambda: [])
    monkeypatch.setattr(gate_driver, "AC_FN", lambda: False)
    assert gate_driver.main(["--stage", stage, "--max-chunks", "1"]) == gate_driver.EXIT_GUARD_STOP and not calls


# ------------------------------------------------------------------------------------------------ n-rule
def test_power_matches_the_appendix_values():
    assert lrf_nrule.power(520, 0.238, 0.05) == pytest.approx(0.730, abs=0.001) and lrf_nrule.power(520, 0.238, 0.06) == pytest.approx(0.863, abs=0.001)
    assert lrf_nrule.power(533, 0.238, 0.05) == pytest.approx(0.74, abs=0.005) and lrf_nrule.power(533, 0.238, 0.05, 0.025) == pytest.approx(0.63, abs=0.005)
    assert lrf_nrule.power(520, 0.238, 0.0, 0.05) < 0.06                                    # size under the null (conservative exact test)


def test_n_rule_cap_clamp_floor_and_fallback():
    r = lrf_nrule.n_rule(0.102, 0.238)                                                      # the draft's exploratory values: 630 would be needed, so the cap
    assert r["n_L"] == 533 and r["delta_plan"] == pytest.approx(0.051) and r["power_at_n_L"]["one_sided_0.05"] > 0.74
    assert lrf_nrule.n_rule(0.02, 0.238)["n_L"] == 533 and lrf_nrule.n_rule(-0.05, 0.2)["n_L"] == 533 and lrf_nrule.n_rule(0.02, 0.238)["n_req"] is None
    big = lrf_nrule.n_rule(0.30, 0.24)
    assert big["n_L"] == 400 and big["n_req"] < 400                                         # clamped to the floor
    mid = lrf_nrule.n_rule(0.14, 0.24)                                                      # Delta_plan 0.07
    assert 400 <= mid["n_L"] <= 533 and mid["n_req"] % 10 == 0 and lrf_nrule.power(mid["n_req"], 0.24, 0.07) >= 0.8 and lrf_nrule.power(mid["n_req"] - 10, 0.24, 0.07) < 0.8
    assert lrf_nrule.fallback_record()["n_L"] == 520


def test_n_rule_cli_writes_once(tmp_path, capsys):
    out = tmp_path / "n_rule.json"
    cf = tmp_path / "cf.json"
    cf.write_text(json.dumps(dict(condition="noise0.1", n=500, b=85, c=34, delta_cf=51 / 500, pi_cf=119 / 500)))
    assert lrf_nrule.main(["--cf-results", str(cf), "--out", str(out)]) == 0
    assert json.loads(out.read_text())["n_L"] == 533 and json.loads(capsys.readouterr().out.strip().splitlines()[-1])["n_L"] == 533
    assert lrf_nrule.main(["--not-committed", "--out", str(out)]) == 2                      # refuses to overwrite
    assert lrf_nrule.main(["--not-committed"]) == 0


# ------------------------------------------------------------------------------------------------ baselines
class FakeSim:
    """A deterministic stand-in for CLIP / SigLIP: similarity of an image to a caption from their bytes."""
    def __init__(self, salt):
        self.salt, self.calls = salt, 0

    def pair(self, image, pos, neg):
        self.calls += 1
        a = float(np.asarray(image, np.float64).mean())
        h = lambda t: (sum(map(ord, t)) * 31 + self.salt) % 97 / 97.0                        # noqa: E731
        return a / 255.0 + h(pos), a / 255.0 + h(neg)


def _setup(env, monkeypatch, n=6, family=(("jpeg", 10), ("noise", 0.1), ("splice", 128))):
    monkeypatch.setattr(common, "RUNS", env)
    monkeypatch.setattr(common, "load_image", lambda iid: fake_image(iid, 96))
    items = []
    rng = np.random.default_rng(0)
    for i in range(n):
        items.append(dict(idx=i, gid=8000 + i, image_id=100 + i, caption=f"red blue {i} small large", n_tok=5, neg_caption=f"green old {(i + 1) % n} tall short", n_tok_neg=5))
    fp = env / "P2-LRF-FOLD"
    fp.mkdir()
    (fp / "folds_lrf.json").write_text(json.dumps(dict(meta={}, cal=[], head=[], test=items, test_ext=[])))
    (env / "P2-LRF-PLAN").mkdir()
    (env / "P2-LRF-PLAN" / "family.json").write_text(json.dumps(dict(endpoint="d", n_rule=dict(rule="x", test_fold=n), family=[dict(corruption=c, severity=s, key=f"{c}{s}") for c, s in family])))
    return items, fp / "folds_lrf.json"


@pytest.fixture
def fake_pkg(monkeypatch):
    def apply(name, severity, pil, seed, ic=None):
        a = np.asarray(pil.convert("RGB")).astype(np.int16)
        rng = np.random.default_rng(seed)
        return __import__("PIL.Image", fromlist=["Image"]).fromarray(np.clip(a + rng.integers(-30, 30, a.shape), 0, 255).astype(np.uint8))
    monkeypatch.setattr(suite, "apply_corruption", apply)
    monkeypatch.setattr(suite, "load_package", lambda: "stub-package")


def test_regenerated_pixels_equal_the_m4_stage_pixels(env, monkeypatch, fake_pkg):
    items, fp = _setup(env, monkeypatch)
    sc = FakeScorer(grid=4)
    extra = m4.parse_extra_cells("shot_noise3,impulse_noise3")
    ctx = SimpleNamespace(family=[("jpeg", 10), ("noise", 0.1), ("splice", 128)], fold=items, denoise_for=(), sanity=(), grid=4, patch=2, extra_cells=extra, ic="stub-package")
    for it in (items[0], items[3], items[5]):
        pil = sc.preprocess(common.load_image(it["image_id"]))
        conds = m4.build_conditions(sc, it, pil, sc.encode(pil), ctx)
        mine = BL.condition_images(it, items, ctx.family, extra, "stub-package", preprocess=sc.preprocess)
        assert [c["name"] for c in conds] == list(mine)
        for c in conds:
            assert np.array_equal(c["pix"], np.asarray(mine[c["name"]])), (it["idx"], c["name"])
    # and with the default pre-processing (suite.center_crop_512 = the code of UniScorer.preprocess)
    it = items[2]
    pil = sc.preprocess(common.load_image(it["image_id"]))
    assert np.array_equal(np.asarray(BL.condition_images(it, items, ctx.family)["splice128"]), next(c["pix"] for c in m4.build_conditions(sc, it, pil, sc.encode(pil), ctx) if c["name"] == "splice128"))


def test_pure_parts_decision_table_and_parity_rule():
    assert BL.MODELS["clip"]["id"] == "openai/clip-vit-large-patch14" and BL.MODELS["clip"]["revision"].startswith("32bd6428") and BL.MODELS["siglip"]["revision"].startswith("9fdffc58")
    assert BL.decide([1, 2, 2], [0, 2, 3]).tolist() == [1, 0, 0]                           # a tie is wrong
    rows = []
    r = np.random.default_rng(1)
    for model in ("clip", "siglip"):
        for i in range(120):
            for cond, p in (("clean", 0.9), ("noise0.1", 0.7)):
                rows.append(dict(idx=i, gid=i, image_id=i, model=model, condition=cond, s_pos=0.0, s_neg=0.0, y=int(r.random() < p)))
    t = BL.table(rows, BL.baseline_rng(), n_boot=400)
    assert set(t) == {"clip", "siglip"} and "drop" in t["clip"]["noise0.1"] and "drop" not in t["clip"]["clean"] and t["clip"]["noise0.1"]["n"] == 120
    lo, hi = t["siglip"]["noise0.1"]["drop_ci95"]
    assert lo < t["siglip"]["noise0.1"]["drop"] < hi
    assert all(set(c) <= {"n", "acc", "drop", "drop_ci95"} for m in t.values() for c in m.values())               # no p-value, no LRF or UniDisc column
    assert BL.pixel_parity_ok([0.99, 0.98]) and not BL.pixel_parity_ok([0.99, 0.97]) and not BL.pixel_parity_ok([])
    assert BL.SEED_SPAWN_KEY == (34, 13) and BL.parity_agreement([1, 2, 3, 4], [1, 2, 3, 5]) == 0.75


def test_baseline_seed_is_the_baselines_slot_of_a6_analysis():
    spec = importlib.util.spec_from_file_location("a6_analysis_r1", ROOT / "analysis" / "paper2" / "lrf" / "a6_analysis.py")
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    assert A.SEED_SLOTS.index("BASELINES") == BL.SEED_SPAWN_KEY[1] and BL.SEED_SPAWN_KEY[:1] == A.SPAWN_KEY
    assert BL.baseline_rng().integers(0, 10 ** 9) == A._rng("BASELINES").integers(0, 10 ** 9)


def test_main_end_to_end_with_fake_models_and_extra_cells(env, monkeypatch, fake_pkg):
    items, fp = _setup(env, monkeypatch, n=8)
    made = {}

    def factory(kind, device, ok):
        made[kind] = (device, ok)
        return FakeSim(len(kind))
    out = env / "base"
    argv = ["--folds-path", str(fp), "--family-run", "P2-LRF-PLAN", "--n", "8", "--extra-cells", "shot_noise3,speckle_noise3", "--extra-n", "5", "--out-dir", str(out), "--n-boot", "200"]
    assert BL.main(argv, scorer_factory=factory) == 0
    assert made == {"clip": ("cpu", False), "siglip": ("cpu", False)}                       # CPU, and no download approval unless the flag is given
    rows = [json.loads(l) for l in (out / "predictions.jsonl").read_text().splitlines()]
    conds = sorted({r["condition"] for r in rows})
    assert conds == ["clean", "jpeg10", "noise0.1", "shot_noise3", "speckle_noise3", "splice128"]
    assert sum(r["condition"] == "shot_noise3" and r["model"] == "clip" for r in rows) == 5 and sum(r["condition"] == "clean" and r["model"] == "clip" for r in rows) == 8
    res = json.loads((out / "baselines.json").read_text())
    assert set(res["table"]) == {"clip", "siglip"} and res["pixel_parity"].startswith("not run") and "no test" in res["note"] and res["models"]["clip"]["revision"].startswith("32bd")
    assert BL.main(argv, scorer_factory=factory) == 2                                       # no overwrite
    shutil_target = env / "base2"
    assert BL.main(argv[:-4] + ["--out-dir", str(shutil_target), "--download-approved", "--models", "siglip"], scorer_factory=factory) == 0 and made["siglip"] == ("cpu", True)


def test_main_stops_when_weights_are_not_cached_or_inputs_are_missing(env, monkeypatch, fake_pkg):
    items, fp = _setup(env, monkeypatch, n=3)

    def no_weights(kind, device, ok):
        raise BL.WeightsNotCached(f"{kind} not cached")
    assert BL.main(["--folds-path", str(fp), "--n", "3", "--out-dir", str(env / "o1")], scorer_factory=no_weights) == 2 and not (env / "o1" / "baselines.json").exists()
    assert BL.main(["--folds-path", str(env / "missing.json"), "--out-dir", str(env / "o2")], scorer_factory=lambda *a: FakeSim(1)) == 2
    assert BL.main(["--folds-path", str(fp), "--models", "dino", "--out-dir", str(env / "o3")], scorer_factory=lambda *a: FakeSim(1)) == 2
    assert BL.main(["--folds-path", str(fp), "--parity", "--out-dir", str(env / "o4")], scorer_factory=lambda *a: FakeSim(1)) == 2          # --parity without --parity-run


def test_pixel_parity_positive_control(env, monkeypatch, fake_pkg):
    items, fp = _setup(env, monkeypatch, n=6)
    sc = FakeScorer(grid=4)
    run = env / "P2-LRF-L1" / "arrays"
    run.mkdir(parents=True)
    ctx = SimpleNamespace(family=[("jpeg", 10), ("noise", 0.1), ("splice", 128)], fold=items, denoise_for=(), sanity=(), grid=4, patch=2, extra_cells=(), ic=None)
    for it in items[:5]:
        pil = sc.preprocess(common.load_image(it["image_id"]))
        conds = m4.build_conditions(sc, it, pil, sc.encode(pil), ctx)
        np.savez(run / f"item{it['idx']:04d}.npz", **{f"{c['name']}_codes": c["codes"].astype(np.int16) for c in conds})
    base = ["--folds-path", str(fp), "--n", "6", "--parity", "--parity-run", "P2-LRF-L1", "--n-boot", "100"]
    assert BL.main(base + ["--out-dir", str(env / "p1")], scorer_factory=lambda *a: FakeSim(1), encoder=sc.encode) == 0
    ok = json.loads((env / "p1" / "baselines.json").read_text())["pixel_parity"]
    assert ok["ok"] is True and ok["min"] == 1.0 and len(ok["agreement"]) == 5 * 4
    wrong = lambda img: (sc.encode(img) + 1) % 16384                                         # noqa: E731  (an encoder that disagrees everywhere)
    assert BL.main(base + ["--out-dir", str(env / "p2")], scorer_factory=lambda *a: FakeSim(1), encoder=wrong) == 0
    bad = json.loads((env / "p2" / "baselines.json").read_text())["pixel_parity"]
    assert bad["ok"] is False and bad["min"] < 0.98


def test_the_hf_scorer_does_not_touch_the_network_without_approval(monkeypatch, tmp_path):
    pytest.importorskip("transformers")
    hub = tmp_path / "hub"
    monkeypatch.setenv("HF_HUB_CACHE", str(hub))                                            # an empty cache of its own: nothing can be found, nothing may be created
    monkeypatch.setenv("HF_HOME", str(tmp_path))
    import huggingface_hub.constants as hc
    monkeypatch.setattr(hc, "HF_HUB_CACHE", str(hub), raising=False)
    monkeypatch.setattr(hc, "HUGGINGFACE_HUB_CACHE", str(hub), raising=False)
    # transformers reads its default cache_dir from a module global set at import (transformers/utils/hub.py, TRANSFORMERS_CACHE), so the
    # env vars above miss it once the real cache holds the pinned weights; point it at the empty cache too (test-only, card row A-9)
    import transformers.utils.hub as th
    for name in ("TRANSFORMERS_CACHE", "PYTORCH_TRANSFORMERS_CACHE", "PYTORCH_PRETRAINED_BERT_CACHE"):
        monkeypatch.setattr(th, name, str(hub), raising=False)
    for k in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"):
        monkeypatch.delenv(k, raising=False)
    import socket
    def no_net(*a, **k):
        raise AssertionError("network access attempted")
    monkeypatch.setattr(socket.socket, "connect", no_net)
    with pytest.raises(BL.WeightsNotCached):
        BL.HFScorer("clip")                                                                   # offline forced: stops, nothing fetched
    assert not any(hub.rglob("*.json")) if hub.exists() else True
