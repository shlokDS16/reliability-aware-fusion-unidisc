"""imagecorruptions exploratory suite (SAP AD.9, AB.8): cells, seeded application, the analysis (b, c_cnt, net difference, E-dec, E-pred agreement) and the runner item on the fake network.
Synthetic data; the package tests are skipped when imagecorruptions is not importable. CPU only; no GPU, no model."""
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

from fake_gate import FakeScorer, fake_image                               # noqa: E402
from exp_p2 import common, run_gate_suite                                   # noqa: E402
from exp_p2.gate import arms, calibrate as cal, config, edec as edec_mod, epred, epred_fit, folds as folds_mod, pipeline, runner, seeds as seeds_mod, suite   # noqa: E402

try:
    suite.load_package()
    HAVE_IC = True
except ImportError:
    HAVE_IC = False
needs_ic = pytest.mark.skipif(not HAVE_IC, reason="imagecorruptions not installed in this interpreter")


# ------------------------------------------------------------------------------------------------ cells and seeds
def test_the_eight_cells_are_fixed_by_kind_and_severity():
    assert suite.TYPES == ("pixelate", "defocus_blur", "fog", "impulse_noise") and suite.SEVERITIES == (2, 4)
    assert suite.CELL_KEYS == ("pixelate2", "pixelate4", "defocus_blur2", "defocus_blur4", "fog2", "fog4", "impulse_noise2", "impulse_noise4")
    assert (suite.HEAD_N, suite.TEST_N) == (100, 100) and suite.PACKAGE["commit"] == "c959e659c9713837d2acd7ce785a81202d4be799" and suite.PACKAGE["licence"] == "Apache-2.0"


def test_corruption_seed_is_a_pure_function_of_item_and_cell():
    assert suite.corruption_seed(2005, 3) == suite.corruption_seed(2005, 3)
    seeds = {suite.corruption_seed(g, c) for g in range(2000, 2100) for c in range(8)}
    assert len(seeds) == 800 and all(0 <= s < 2 ** 32 for s in seeds)


# ------------------------------------------------------------------------------------------------ the package
def _img(seed=0):
    from PIL import Image
    rng = np.random.default_rng(seed)
    base = np.linspace(0, 255, 512)[None, :, None] * np.ones((512, 1, 3))
    return Image.fromarray(np.clip(base + rng.normal(0, 20, (512, 512, 3)), 0, 255).astype(np.uint8))


@needs_ic
def test_installed_package_is_the_pinned_commit():
    import importlib.metadata as md
    d = md.distribution("imagecorruptions")
    raw = d.read_text("direct_url.json")
    if raw is None:
        pytest.skip("not installed from a VCS URL in this interpreter")
    assert json.loads(raw)["vcs_info"]["commit_id"] == suite.PACKAGE["commit"]
    assert suite.available_types() == list(suite.TYPES)


@needs_ic
@pytest.mark.parametrize("name,sev", suite.CELLS)
def test_every_cell_runs_keeps_shape_and_changes_the_image(name, sev):
    pil = _img()
    out = suite.apply_corruption(name, sev, pil, seed=123)
    a, b = np.asarray(pil), np.asarray(out)
    assert out.size == (512, 512) and b.dtype == np.uint8 and b.shape == a.shape and np.abs(a.astype(int) - b.astype(int)).mean() > 0.5


@needs_ic
@pytest.mark.parametrize("name", suite.TYPES)
def test_same_seed_same_pixels_and_random_types_vary_with_the_seed(name):
    pil = _img(1)
    a, b, c = (np.asarray(suite.apply_corruption(name, 4, pil, seed=s)) for s in (7, 7, 8))
    assert np.array_equal(a, b)
    assert (not np.array_equal(a, c)) == (name in ("fog", "impulse_noise"))      # pixelate and defocus_blur are deterministic transforms


@needs_ic
def test_seeding_context_restores_global_state():
    import skimage.util as sku
    orig, st = sku.random_noise, np.random.get_state()
    suite.apply_corruption("impulse_noise", 2, _img(), seed=5)
    suite.apply_corruption("fog", 2, _img(), seed=5)
    assert sku.random_noise is orig
    st2 = np.random.get_state()
    assert st[0] == st2[0] and np.array_equal(st[1], st2[1]) and st[2:] == st2[2:]          # the caller's global numpy RNG is untouched


@needs_ic
def test_impulse_noise_would_not_be_reproducible_without_the_seeding_wrapper():
    """Documents why `_seeded` wraps skimage.util.random_noise: with only np.random.seed the output still differs between calls (scikit-image >= 0.19 draws from a fresh default_rng)."""
    ic = suite.load_package()
    arr = np.asarray(_img())
    np.random.seed(0)
    a = ic.corrupt(arr, 3, "impulse_noise")
    np.random.seed(0)
    b = ic.corrupt(arr, 3, "impulse_noise")
    assert not np.array_equal(a, b)


def test_a_missing_type_is_dropped_not_replaced(monkeypatch):
    fake_ic = SimpleNamespace(get_corruption_names=lambda subset: ["pixelate", "fog", "impulse_noise", "snow"])
    assert suite.available_types(fake_ic) == ["pixelate", "fog", "impulse_noise"]         # defocus_blur absent: dropped, no stand-in


# ------------------------------------------------------------------------------------------------ analysis
def _frame(n=100, b=12, c=4, fold="test", cell="pixelate2", seed=0, extra_cells=()):
    """Long frame with exactly b items where GATE-M is right and none wrong, c the reverse, and the d columns satisfying known E-dec values."""
    import pandas as pd
    rng = np.random.default_rng(seed)
    recs = []
    for k in (cell, *extra_cells):
        y_none, y_gm = np.zeros(n), np.zeros(n)
        y_none[:20], y_gm[:20] = 1, 1                                   # concordant right
        y_gm[20:20 + b] = 1                                              # b: GM right, none wrong
        y_none[40:40 + c] = 1                                            # c: none right, GM wrong
        d_clean = rng.normal(0.30, 0.02, n)
        d_none = d_clean - 0.20 + rng.normal(0, 0.01, n)               # T about 0.20
        d_chg = d_clean - 0.05 + rng.normal(0, 0.01, n)                # U about 0.05
        d_gm = d_none + 0.10 + rng.normal(0, 0.01, n)                  # R about 0.10, V about 0.05
        for i in range(n):
            recs.append(dict(fold=fold, idx=i, cell=k, y_clean=1.0, y_none=y_none[i], y_gm=y_gm[i], y_chg=1.0, d_clean=d_clean[i], d_none=d_none[i], d_gm=d_gm[i], d_chg=d_chg[i],
                             n_changed=100, n_flag=80, n_tp=60))
    return pd.DataFrame.from_records(recs, columns=list(suite.SUITE_COLS))


def test_suite_cells_counts_b_and_c_and_the_net_difference():
    r = suite.suite_cells(_frame(b=12, c=4), n_boot=500)
    c = r["cells"]["pixelate2"]
    assert c["n_items"] == 100 and c["gm_vs_none"]["b"] == 12 and c["gm_vs_none"]["c"] == 4 and c["gm_vs_none"]["n_d"] == 16
    assert c["net_difference"] == pytest.approx(0.08) and c["gm_vs_none"]["ci95"][0] < 0.08 < c["gm_vs_none"]["ci95"][1] and c["sign_observed"] == 1
    assert c["acc_gm"] == pytest.approx(0.32) and c["acc_none"] == pytest.approx(0.24) and c["flag_precision"] == pytest.approx(0.75) and c["flag_recall"] == pytest.approx(0.6)


def test_no_p_value_and_a_tier3_label_in_the_output():
    r = suite.suite_cells(_frame(), n_boot=200)
    blob = json.dumps(r, default=str)
    assert "Tier 3" in r["label"] and "researcher choice" in r["choice"]
    c = r["cells"]["pixelate2"]["gm_vs_none"]
    assert not any(k in c for k in ("p", "p_mid", "ci9833", "ci90"))
    assert '"p_holm"' not in blob and '"p":' not in blob


def test_fold_filter_and_absent_cells():
    df = _frame(fold="test", cell="fog4", extra_cells=("pixelate4",))
    other = _frame(fold="head", cell="fog4", b=0, c=30)
    import pandas as pd
    both = pd.concat([df, other])
    r = suite.suite_cells(both, fold="test", n_boot=100)
    assert set(r["cells"]) == {"fog4", "pixelate4"} and r["cells"]["fog4"]["n_items"] == 100 and r["cells"]["fog4"]["gm_vs_none"]["b"] == 12
    assert suite.suite_cells(both, fold="head", n_boot=100)["cells"]["fog4"]["gm_vs_none"]["c"] == 30


def test_edec_identity_and_values():
    r = suite.suite_cells(_frame(n=100, seed=3), n_boot=500)["cells"]["pixelate2"]["edec"]
    ds = r["d_scale"]
    t, u, rr, v = (ds["tau"][k]["mean"] for k in "TURV")
    assert t == pytest.approx(u + rr + v, abs=1e-12) and t == pytest.approx(0.20, abs=0.01) and u == pytest.approx(0.05, abs=0.01) and rr == pytest.approx(0.10, abs=0.01) and v == pytest.approx(0.05, abs=0.01)
    assert ds["identity_in_all_resamples"] is True and r["n_complete"] == 100 and r["n_dropped_incomplete"] == 0
    assert ds["shares"]["U"] + ds["shares"]["R"] + ds["shares"]["V"] == pytest.approx(1.0)
    assert "accuracy_scale" in r and "ci9833" not in ds["tau"]["T"]                       # suite cells are not P cells: 95 percent only


def test_the_suite_calls_the_audited_edec_and_epred_not_copies():
    for name in ("edec_split", "edec_cell", "_boot_means", "epred_agreement"):
        assert not hasattr(suite, name), name                                             # the private copies are gone (integration, IMPL-D concern 5)
    assert suite.edec_mod is edec_mod and suite.epred is epred and suite.epred_fit is epred_fit
    assert suite.SEED_NAME == "suite" and "suite" in seeds_mod.ANALYSES


def test_edec_shares_are_undefined_when_the_total_loss_is_not_clearly_positive():
    rng = np.random.default_rng(0)
    n = 80
    c = rng.normal(0.3, 0.1, n)
    r = edec_mod.edec_cell("fog4", (c, c + rng.normal(0, 0.1, n), c + rng.normal(0, 0.1, n), c + rng.normal(0, 0.1, n)), None, n_boot=300)
    assert isinstance(r["d_scale"]["shares"], str) and "undefined" in r["d_scale"]["shares"]


def test_edec_is_complete_case_and_the_identity_is_asserted():
    d = [np.array([1.0, 2, 3, np.nan]), np.array([0.5, 1, 2, 3]), np.array([0.7, 1.5, 2.5, 3]), np.array([0.6, 1.6, 2.2, 3])]
    sp = edec_mod.edec_split(*d)
    assert sp["n"] == 3 and sp["n_dropped"] == 1 and np.allclose(sp["d"]["T"], sp["d"]["U"] + sp["d"]["R"] + sp["d"]["V"])
    # V is negative when GATE-M beats the oracle gate (not detection)
    assert sp["d"]["V"][1] == pytest.approx(1.5 - 1.6) and sp["d"]["V"][1] < 0


def _headroom_item(rng, helps):
    z = np.zeros(1024, bool)
    z[:200] = True
    delta = rng.normal(0.10, 0.3, 1024)
    delta[z] = rng.normal(0.0, 1.0, 200)                               # changed tokens carry no signal and a large variance (hand computation: SNR 0.153 before; 0.264 with flags on them; 0.137 with random flags)
    flag = np.zeros(1024, bool)
    if helps:
        flag[:180] = True                                              # flags sit on the changed tokens (beta high, alpha ~ 0)
    else:
        flag[rng.choice(1024, 200, replace=False)] = True              # random flags
    return dict(delta=delta, z=z, flag=flag)


def test_epred_signs_come_from_the_audited_fit_and_agreement_from_epred():
    rng = np.random.default_rng(0)
    s = suite.epred_signs({"fog4": [_headroom_item(rng, True) for _ in range(20)], "pixelate2": [_headroom_item(rng, False) for _ in range(20)], "empty": []}, n_boot=200)
    assert s["fog4"]["sign"] == 1 and s["pixelate2"]["sign"] == -1 and s["empty"]["sign"] is None and s["fog4"]["n_items"] == 20
    assert s["fog4"]["cell"] == "fog4" and "stability" in s["fog4"]                                       # the audited cell record, re-keyed to the suite cell
    ok = dict(b=20, c=5, n=100, ci95=[0.05, 0.25])
    a = epred.epred_agreement(s, {"fog4": ok, "pixelate2": ok, "empty": ok})
    assert a["K_eval"] == 2 and a["A"] == 1 and "no committed sign" in a["excluded"]["empty"] and a["cp95"][0] < 0.5 < a["cp95"][1]
    assert "never pooled" in a["label"] and a["formal_test"] is None and "p" not in a and "p_value" not in a
    assert a["refutation_rule_met_for_cells"] == ["pixelate2"]                                             # s = -1 against an observed interval that excludes 0 on the + side
    assert a["rivals"]["always +"] == dict(A=2, K_eval=2)
    tie = dict(b=7, c=7, n=100, ci95=[-0.1, 0.1])
    a2 = epred.epred_agreement(s, {"fog4": tie, "pixelate2": dict(b=3, c=20, n=100, ci95=[-0.3, -0.05])})
    assert a2["K_eval"] == 1 and a2["A"] == 1 and a2["excluded"]["fog4"].startswith("b = c_cnt") and a2["refutation_rule_met_for_cells"] == []


def test_suite_cells_can_carry_the_epred_block():
    r = suite.suite_cells(_frame(b=12, c=4), n_boot=100, s_c={"pixelate2": 1})
    assert r["epred_suite"]["A"] == 1 and r["epred_suite"]["K_eval"] == 1


# ------------------------------------------------------------------------------------------------ the GPU runner on the fake network
@pytest.fixture
def renv(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "_cuda", lambda: None)
    monkeypatch.setattr(common, "load_image", lambda iid: fake_image(iid, 96))

    def init_run(run_id, config_):
        d = tmp_path / run_id
        d.mkdir(parents=True, exist_ok=True)
        if not (d / "config.json").exists():
            (d / "config.json").write_text(json.dumps(dict(config_, run_id=run_id)))
        return d
    monkeypatch.setattr(common, "init_run", init_run)
    return tmp_path


def _fold_items(n, offset, tag, n_words=6):
    rng = np.random.default_rng(offset)
    words = "red blue green small large old new quiet loud bright dark soft hard warm cold fast slow tall short thin wide".split()
    items = [dict(idx=i, gid=offset + i, image_id=400 + offset + i, caption=" ".join(rng.choice(words, n_words, replace=False)), n_tok=n_words) for i in range(n)]
    for i, it in enumerate(items):
        j = (i + 1) % n
        it.update(neg_idx=j, neg_image_id=items[j]["image_id"], neg_caption=items[j]["caption"], neg_restricted=True)
    return items


def _folds():
    return dict(meta={}, cal=[], head=_fold_items(100, 1000, "h"), test=_fold_items(300, 2000, "t"), test_ext=[])


def test_planned_items_are_head_100_then_the_first_100_test_items():
    items = run_gate_suite.planned_items(_folds())
    assert len(items) == 200 and [it["idx"] for it in items] == list(range(200))
    assert [it["fold"] for it in items] == ["head"] * 100 + ["test"] * 100 and items[100]["gid"] == 2000 and items[100]["fold_idx"] == 0 and items[99]["gid"] == 1099 and items[199]["gid"] == 2099


def test_get_items_excludes_out_of_range_captions_without_replacement(renv, monkeypatch):
    f = _folds()
    f["head"][5]["n_tok"] = 3
    f["test"][7]["n_tok"] = 40
    monkeypatch.setattr(folds_mod, "ensure_folds", lambda fn, path=None: f)
    sc = SimpleNamespace(caption_ids=lambda c: [1] * len(c.split()))
    sc.caption_ids = lambda c: [1] * (3 if c == f["head"][5]["caption"] else 40 if c == f["test"][7]["caption"] else 6)
    items = run_gate_suite.get_items_factory(None)(sc, renv / "r")
    assert len(items) == 198 and {(it["fold"], it["fold_idx"]) for it in items}.isdisjoint({("head", 5), ("test", 7)})
    assert [it["idx"] for it in items] == [i for i in range(200) if i not in (5, 107)]           # positions unchanged, nothing shifted into the gap
    assert json.loads((renv / "r" / "token_exclusions.json").read_text())["n_excluded_total"] == 2


def test_prereqs_need_the_m2_threshold_and_a_committed_family_json(renv, monkeypatch):
    with pytest.raises(FileNotFoundError, match="fit_threshold"):
        run_gate_suite.check_prereqs(renv)
    (renv / "P2-GATE-M2").mkdir()
    thr = cal.Threshold(tau=0.0, alpha=0.05, n_cal=300, eps0=1e-6, statistic="q", K=8, seed=0, ids_hash="x", feasible=True, r_hat=0.05, eps0_resolvable=True)
    (renv / "P2-GATE-M2" / "threshold.json").write_text(json.dumps(dict(thresholds={"0.05": thr.to_json()})))
    with pytest.raises(FileNotFoundError, match="family.json"):
        run_gate_suite.check_prereqs(renv, require_commit=False)
    (renv / "P2-GATE-M3").mkdir()
    (renv / "P2-GATE-M3" / "family.json").write_text("{}")
    got, eps0, types = run_gate_suite.check_prereqs(renv, require_commit=False) if HAVE_IC else (None, None, None)
    if HAVE_IC:
        assert got.tau == 0.0 and eps0 == 1e-6 and types == list(suite.TYPES)


@needs_ic
def test_runner_item_has_66_passes_and_the_documented_outputs(renv):
    sc = runner.Counting(FakeScorer(grid=4))
    (renv / "P2-GATE-SUITEx").mkdir()
    thr = cal.Threshold(tau=0.0, alpha=0.05, n_cal=300, eps0=1e-6, statistic="q", K=8, seed=0, ids_hash="x", feasible=True, r_hat=0.05, eps0_resolvable=True)
    ctx = SimpleNamespace(run=renv / "P2-GATE-SUITEx", dcache=pipeline.dcache_for(), thr=thr, eps0=1e-6, ic=suite.load_package(), cells=[(ci, t, s) for ci, (t, s) in enumerate(suite.CELLS)], grid=4)
    items = [dict(it, fold="test", fold_idx=it["idx"]) for it in _fold_items(3, 2000, "t")]
    run_gate_suite.process(sc, items[0], ctx)                                          # warms the null caches
    r0 = sc.rows
    row, arrays = run_gate_suite.process(sc, items[1], ctx)
    assert sc.rows - r0 == 2 + 8 * 8                                                   # Lambda^{c+}, Lambda^{c-} once, then B = 8 passes in each of the 8 cells
    assert set(row["cells"]) == set(suite.CELL_KEYS) and set(row["cells"]["fog4"]["img"]) == {"none", "gm", "chg"} and set(row["clean"]) >= {"d", "y", "mean"}
    for k in suite.CELL_KEYS:
        assert {f"{k}_codes", f"{k}_z", f"{k}_delta", f"{k}_flag", f"{k}_u"} <= set(arrays) and arrays[f"{k}_flag"].dtype == bool
        c = row["cells"][k]
        assert c["n_changed"] == int(arrays[f"{k}_z"].sum()) and c["n_flag"] == int(arrays[f"{k}_flag"].sum()) and c["n_tp"] == int((arrays[f"{k}_flag"] & arrays[f"{k}_z"]).sum())
        assert c["img"]["none"]["n"] == 16 and c["img"]["chg"]["n"] == 16 - c["n_changed"] and c["img"]["gm"]["n"] == 16 - c["n_flag"]
    row2, arrays2 = run_gate_suite.process(sc, items[1], ctx)                          # deterministic (corruption seeds come from the item id)
    assert json.dumps(row2["cells"], sort_keys=True) == json.dumps(row["cells"], sort_keys=True) and all(np.array_equal(arrays[k], arrays2[k]) for k in arrays)
    # the frame and the analysis accept the runner's rows
    r = dict(row, idx=1)
    df = suite.suite_frame([r])
    assert len(df) == 8 and set(df.columns) == set(suite.SUITE_COLS)


@needs_ic
def test_runner_loop_resumes(renv):
    sc = runner.Counting(FakeScorer(grid=4))
    thr = cal.Threshold(tau=0.0, alpha=0.05, n_cal=300, eps0=1e-6, statistic="q", K=8, seed=0, ids_hash="x", feasible=True, r_hat=0.05, eps0_resolvable=True)
    items = [dict(it, fold="head", fold_idx=it["idx"]) for it in _fold_items(3, 1000, "h")]
    mk = lambda s, run: SimpleNamespace(run=run, dcache=pipeline.dcache_for(), thr=thr, eps0=1e-6, ic=suite.load_package(), cells=[(0, "pixelate", 2), (4, "fog", 2)], grid=4)
    kw = dict(run_id="P2-GATE-SUITEy", cfg=dict(run_gate_suite.CONFIG, n_items=3), load=lambda: sc, get_items=lambda s, r: items, process=run_gate_suite.process, make_ctx=mk, duty=1.0, soft_minutes=30)
    assert runner.run_items(limit=2, **kw) == runner.EXIT_MORE_WORK and runner.run_items(**kw) == runner.EXIT_DONE
    rows = common.read_jsonl(renv / "P2-GATE-SUITEy" / "items.jsonl")
    assert [r["idx"] for r in rows] == [0, 1, 2] and set(rows[0]["cells"]) == {"pixelate2", "fog2"} and "peak_gb" not in rows[0]
