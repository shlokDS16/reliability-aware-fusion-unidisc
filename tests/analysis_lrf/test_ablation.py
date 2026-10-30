"""Tier-3 ablation harness (analysis/paper2/lrf/ablation.py) on SYNTHETIC arrays only: no real design or fresh array is read. CPU only.

Covers: partitions, variant list, R0 logic and an end-to-end fit with R0 on a synthetic design set, KO-ALL = NONE with the float-tie tolerance, GAMLin = F1 with knots 0, AttnMIL starts at NONE and its numpy path,
A-SF tie rule, A-UNL, the seed slot and common resamples, hash and GATE-field refusals, controls written first and halting, scorer allow-list, determinism, analyse output (K = 336, section 3 order)."""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.paper2.lrf import ablation as A, a6_analysis as A6                      # noqa: E402
from analysis_posthoc.learned_ceiling import data, families as fam, run as lrun       # noqa: E402
from exp_p2.gate import lrf_score as LS                                               # noqa: E402

M = data.M
CONDS4 = data.COND


# ---------------------------------------------------------------------------------------------------------------- synthetic arrays
def write_items(dirpath: Path, n: int, conds, seed: int, with_gate: bool = True) -> None:
    rng = np.random.default_rng(seed)
    dirpath.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        d = {}
        for c in conds:
            B = -rng.gamma(2.0, 1.0, M).astype(np.float32)
            D = B - rng.normal(0.3, 0.5, M).astype(np.float32)
            d[f"{c}_B"], d[f"{c}_D"] = B, D
            d[f"{c}_s3"] = rng.uniform(0, 1, M).astype(np.float32)
            d[f"{c}_tbv"] = -rng.gamma(2.0, 1.0, M).astype(np.float32)
            d[f"{c}_tex"] = rng.gamma(2.0, 1.0, M).astype(np.float32)
            d[f"{c}_nbr"] = rng.uniform(0, 2, M).astype(np.float32)
            d[f"{c}_delta"] = (0.02 + 0.2 * (B - D) + rng.normal(0, 1.0, M)).astype(np.float32)
            if with_gate:                                                   # fields the ablation must never read
                d[f"{c}_flag0.05"] = rng.uniform(0, 1, M) < 0.1
                d[f"{c}_z"] = rng.uniform(0, 1, M) < 0.1
                d[f"{c}_codes"] = rng.integers(0, 16384, M)
                d[f"{c}_deltaL"] = rng.normal(0, 1, M).astype(np.float32)
        np.savez(dirpath / f"item{i:04d}.npz", **d)


def write_run(run_dir: Path, n: int, seed: int, image_offset: int = 0, frozen_dir: Path | None = None, conds=CONDS4) -> None:
    """A synthetic 'fresh' run: arrays, items.jsonl, arrays_manifest.json and predictions.jsonl (y_none, y_lrf from the lrf_score functions, i.e. independent of the ablation code)."""
    write_items(run_dir / "arrays", n, conds, seed)
    rows = [dict(idx=i, gid=i, image_id=1000 + image_offset + i, caption="x", n_tok=5, n_tok_neg=5, conds={c: {} for c in conds}) for i in range(n)]
    (run_dir / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf8")
    man = dict(n=n, files={f"item{i:04d}.npz": A.sha256_file(run_dir / "arrays" / f"item{i:04d}.npz") for i in range(n)})
    (run_dir / "arrays_manifest.json").write_text(json.dumps(man), encoding="utf8")
    fz = LS.load_frozen(frozen_dir)
    lines = []
    for i in range(n):
        d = dict(np.load(run_dir / "arrays" / f"item{i:04d}.npz"))
        for c in conds:
            w = LS.weights(fz, d, c)
            lines.append(dict(idx=i, gid=i, image_id=1000 + image_offset + i, condition=c, y_none=LS.arm_y(d[f"{c}_delta"], None)[0], y_gatem=1, y_lrf=LS.decide(w, d[f"{c}_delta"])["y"]))
    (run_dir / "predictions.jsonl").write_text("".join(json.dumps(l) + "\n" for l in lines), encoding="utf8")


def make_synthetic_frozen(frozen_dir: Path, arr_dir: Path, n_items: int, rmax: int, n_cfg: int) -> dict:
    """A frozen LRF built exactly as refreeze.py does (F1GAM, successive_halving on [99, 0], final seed ss(4, 99, 0, 0)), with the real pinned code hashes, on the synthetic design set."""
    ctx = A.load_design(arr_dir, n_items)
    allit = np.arange(n_items)
    f1 = fam.F1GAM("F1", rmax, n_cfg)
    cfg, score, hl = lrun.successive_halving(ctx, f1, allit, 99, 0)
    seed = int(lrun.ss(4, 99, 0, 0).generate_state(1)[0])
    model = f1.fit(ctx, cfg, allit, f1.rmax, seed)
    net = model["net"]
    frozen_dir.mkdir(parents=True)
    np.savez(frozen_dir / "model.npz", a=net.a.detach().numpy(), b=net.b.detach().numpy(), c=net.c.detach().numpy(), knots=net.knots.numpy(), mu=model["mu"], sd=model["sd"],
             feature_names=np.array(data.feature_names()))
    code_dir = ROOT / "analysis_posthoc" / "learned_ceiling"
    spec = dict(name="synthetic frozen LRF", caption_slot_len=13, features=data.feature_names(), selected_cfg=cfg, inner_cv_o1=float(score), seed=seed, T=fam.temperature(ctx.delta),
                code_sha256={f: A.sha256_file(code_dir / f) for f in A.PINNED_FILES}, model_sha256=A.sha256_file(frozen_dir / "model.npz"),
                rescored_arrays_digest=A.arrays_digest(arr_dir, n_items))
    (frozen_dir / "spec.json").write_text(json.dumps(spec), encoding="utf8")
    return spec


# ---------------------------------------------------------------------------------------------------------------- module-scoped end-to-end fixtures
N_DES, RMAX, NCFG = 6, 3, 3


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    root = tmp_path_factory.mktemp("abl")
    src = root / "src"
    write_items(src / "arrays", N_DES, CONDS4, seed=1)
    frozen = root / "frozen"
    spec = make_synthetic_frozen(frozen, src / "arrays", N_DES, RMAX, NCFG)
    out = root / "fit"
    res = A.fit(src, frozen, out, n_items=N_DES, rmax=RMAX, n_cfg=NCFG, log=lambda *_: None)
    l1, lg = root / "l1", root / "lg"
    write_run(l1, 5, seed=11, frozen_dir=frozen)
    write_run(lg, 4, seed=12, image_offset=0, frozen_dir=frozen, conds=LS.LG_CONDS)
    return dict(root=root, src=src, frozen=frozen, spec=spec, fit=out, l1=l1, lg=lg, res=res)


# ---------------------------------------------------------------------------------------------------------------- partitions and the variant list
def test_partitions_cover_35_features_exactly_once():
    assert A.N_FEAT == 35
    for part, sizes in ((A.PARTITION_S, [14, 5, 5, 4, 4, 3]), (A.PARTITION_F, [7, 3, 8, 4, 13])):
        flat = [n for v in part.values() for n in v]
        assert sorted(flat) == sorted(A.FEATURES) and len(flat) == len(set(flat)) == 35
        assert [len(v) for v in part.values()] == sizes
    with pytest.raises(ValueError):
        A.check_partition({"x": A.FEATURES[:-1]})


def test_variant_list_is_the_plan_section_3():
    assert len(A.VARIANTS) == 22 and len(A.BLOCK_3A) == 10 and len(A.BLOCK_3B) == 12 and len(A.FITTED) == 9
    assert A.INTERVAL_ROWS == tuple(v for v in A.VARIANTS if v != "KO-ALL") and len(A.INTERVAL_ROWS) == 21
    assert A.variants_record()["n_intervals_K"] == 336 == 21 * 8 * 2
    assert A.BLOCK_3A[0] == "A-LIN" and A.BLOCK_3A[-1] == "A-UNL" and A.BLOCK_3B[-1] == "KO-ALL"
    assert set(A.KNOCKOUT_GROUPS["KO-ALL"]) == set(A.FEATURES)


# ---------------------------------------------------------------------------------------------------------------- R0 logic
def test_r0_logic_toy_model():
    spec = dict(selected_cfg=dict(knots=8, ridge=0.0027, lr=0.0168), inner_cv_o1=0.375)
    w = np.random.default_rng(0).uniform(size=(3, 4, 16))
    ok = A.r0_check(spec, dict(knots=8, ridge=0.0027, lr=0.0168), 0.375 + 1e-9, w + 3e-7, w)
    assert ok["ok"] and ok["max_abs_weight_diff"] <= 1e-5
    assert not A.r0_check(spec, dict(knots=8, ridge=0.0027, lr=0.0168), 0.375, w + 2e-5, w)["ok"]            # weights off by more than 1e-5
    assert not A.r0_check(spec, dict(knots=4, ridge=0.0027, lr=0.0168), 0.375, w, w)["ok"]                    # different configuration
    assert not A.r0_check(spec, dict(knots=8, ridge=0.0027, lr=0.0168), 0.40, w, w)["ok"]                     # different inner O1


def test_fit_end_to_end_reproduces_frozen_and_writes_files(world):
    out = world["fit"]
    r0 = json.loads((out / "R0.json").read_text())
    assert r0["ok"] and r0["cfg_equal"] and r0["max_abs_weight_diff"] <= 1e-5
    for v in A.FITTED + (A.HARNESS_LRF,):
        for f in ("model.npz", "model_seed1.npz", "model_seed2.npz", "spec.json", "hpo.json", "selfcheck.json"):
            assert (out / v / f).exists(), (v, f)
        sc = json.loads((out / v / "selfcheck.json").read_text())
        assert sc["selfcheck_max_abs_diff_numpy_vs_torch"] <= 1e-5, v
    assert (out / "A-UNL" / "spec.json").exists() and not (out / "A-UNL" / "model.npz").exists()
    for f in ("config.json", "env-lock.txt", "timing.json", "variants.json", "controls_design.json", "HASHES.json"):
        assert (out / f).exists()
    # the design-item stage stores no inner-fold accuracy
    for p in list(out.rglob("hpo.json")) + list(out.rglob("candidates.json")):
        assert '"acc"' not in p.read_text()
    sp = json.loads((out / "A-SF" / "spec.json").read_text())
    assert sp["chosen_feature"] in A.FEATURES and len(sp["candidate_inner_cv_o1"]) == 35
    H = json.loads((out / "HASHES.json").read_text())
    assert "A-LIN/model.npz" in H["files"] and "analysis/paper2/lrf/ablation.py" in H["code"] and set(H["pinned_learned_ceiling"]) == set(A.PINNED_FILES)


def test_r0_failure_stops_before_any_variant(world, tmp_path):
    bad = tmp_path / "frozen_bad"
    shutil.copytree(world["frozen"], bad)
    spec = json.loads((bad / "spec.json").read_text())
    spec["selected_cfg"] = dict(spec["selected_cfg"], lr=spec["selected_cfg"]["lr"] * 1.5)
    (bad / "spec.json").write_text(json.dumps(spec))
    out = tmp_path / "fit_bad"
    with pytest.raises(A.R0Failed):
        A.fit(world["src"], bad, out, n_items=N_DES, rmax=RMAX, n_cfg=NCFG, log=lambda *_: None)
    assert not json.loads((out / "R0.json").read_text())["ok"]
    assert not any((out / v).exists() for v in A.FITTED)


def test_fit_refuses_wrong_design_digest_and_existing_out(world, tmp_path):
    bad = tmp_path / "frozen_bad"
    shutil.copytree(world["frozen"], bad)
    spec = json.loads((bad / "spec.json").read_text())
    spec["rescored_arrays_digest"] = "0" * 64
    (bad / "spec.json").write_text(json.dumps(spec))
    with pytest.raises(A.FitRefused):
        A.fit(world["src"], bad, tmp_path / "o", n_items=N_DES, rmax=RMAX, n_cfg=NCFG, log=lambda *_: None)
    assert not (tmp_path / "o").exists()
    with pytest.raises(A.FitRefused):
        A.fit(world["src"], world["frozen"], world["fit"], n_items=N_DES, rmax=RMAX, n_cfg=NCFG, log=lambda *_: None)


def test_harness_lrf_equals_f1_directly(world):
    """R0 on the toy: the harness path (GAMCols over all 35) gives the same weights as families.F1GAM within 1e-5 (here exactly)."""
    ctx = A.load_design(world["src"] / "arrays", N_DES)
    allit = np.arange(N_DES)
    f1 = fam.F1GAM("F1", RMAX, NCFG)
    cfg, sc, _ = lrun.successive_halving(ctx, f1, allit, 99, 0)
    m1 = f1.fit(ctx, cfg, allit, RMAX, A._seed(0))
    fh = A.make_family(A.HARNESS_LRF, RMAX, NCFG)
    cfgh, sch, _ = lrun.successive_halving(ctx, fh, allit, 99, 0)
    mh = fh.fit(ctx, cfgh, allit, RMAX, A._seed(0))
    assert cfg == cfgh and sc == sch
    assert np.abs(f1.weights(ctx, m1, allit) - fh.weights(ctx, mh, allit)).max() <= 1e-5


# ---------------------------------------------------------------------------------------------------------------- KO-ALL and tolerance
def test_ko_all_equals_none_and_float_tie_tolerance(world):
    fz = LS.load_frozen(world["frozen"])
    ctx = A.load_design(world["src"] / "arrays", N_DES)
    res = A.ko_all_control(A.frozen_model(fz), ctx.X, ctx.delta)
    assert res["ok"] and res["max_within_item_condition_weight_spread"] == 0.0 and res["n_differing_beyond_tolerance"] == 0
    # weights constant within an item-condition: decisions equal NONE's by construction
    W = A.model_weights(A.frozen_model(fz), ctx.X, zero_cols=range(35))
    for i in range(N_DES):
        for c in range(4):
            assert LS.decide(W[i, c], ctx.delta[i, c])["y"] == LS.arm_y(ctx.delta[i, c], None)[0]
    # tolerance rule: a sum that is zero in exact arithmetic (rounding residue) is allowed to differ, a real margin is not
    d_tie = np.array([0.1, 0.2, -0.3] + [0.0] * (M - 3), np.float64)       # exact sum is 0; the float sum is 0 or a rounding residue near 1e-17
    assert abs(float(d_tie.sum())) < 1e-15 and A.tie_tolerance_ok(d_tie)
    assert A.tie_tolerance_ok(np.array([1.0, -1.0, 0.0]))
    assert not A.tie_tolerance_ok(np.array([1.0, 0.5, -0.2]))


def test_ko_all_with_nonconstant_weights_would_fail_control():
    """Sanity of the control itself: a frozen model whose weights vary within an item (not a knockout) does differ from NONE somewhere."""
    rng = np.random.default_rng(0)
    X = rng.normal(size=(8, 4, M, 35)).astype(np.float32)
    delta = rng.normal(0.01, 1.0, (8, 4, M)).astype(np.float32)
    model = dict(kind="gam", cols=np.arange(35), a=rng.normal(size=35) * 2, b=np.array(0.0), c=np.zeros((35, 0)), knots=np.zeros((35, 0)), mu=np.zeros(35), sd=np.ones(35))
    W = A.model_weights(model, X)
    assert (W.max(-1) - W.min(-1)).max() > 0
    diff = sum(LS.decide(W[i, c], delta[i, c])["y"] != LS.decide(np.ones(M), delta[i, c])["y"] for i in range(8) for c in range(4))
    assert diff > 0


# ---------------------------------------------------------------------------------------------------------------- families
def test_gamlin_equals_f1_with_knots_zero(world):
    ctx = A.load_design(world["src"] / "arrays", N_DES)
    allit = np.arange(N_DES)
    lin = A.make_family("A-LIN", RMAX, NCFG)
    rng = np.random.default_rng(lrun.ss(2, 99, 0))
    cfgs = [lin.sample(rng) for _ in range(NCFG)]
    rng2 = np.random.default_rng(lrun.ss(2, 99, 0))
    f1 = fam.F1GAM("F1", RMAX, NCFG)
    cfgs_f1 = [f1.sample(rng2) for _ in range(NCFG)]
    assert all(c["knots"] == 0 for c in cfgs)
    assert [(c["ridge"], c["lr"]) for c in cfgs] == [(c["ridge"], c["lr"]) for c in cfgs_f1]       # the same draws as LRF, knots overridden
    cfg = dict(cfgs_f1[0], knots=0)
    m_lin, m_f1 = lin.fit(ctx, cfg, allit, RMAX, 5), f1.fit(ctx, cfg, allit, RMAX, 5)
    assert np.array_equal(lin.weights(ctx, m_lin, allit), f1.weights(ctx, m_f1, allit))
    assert m_lin["net"].knots.shape[1] == 0


def test_single_source_uses_only_its_columns(world):
    ctx = A.load_design(world["src"] / "arrays", N_DES)
    f = A.make_family("A-S-pos", RMAX, NCFG)
    assert f.cols == [A.FEATURES.index(n) for n in A.PARTITION_S["S-pos"]]
    cfg = f.sample(np.random.default_rng(0))
    tm = f.fit(ctx, cfg, np.arange(N_DES), RMAX, 3)
    mdl = A.export_model(f, tm)
    assert list(mdl["cols"]) == f.cols and mdl["mu"].shape == (3,)
    assert np.abs(A.model_weights(mdl, ctx.X) - f.weights(ctx, tm, np.arange(N_DES))).max() <= 1e-5


def test_attn_mil_zero_v_equals_none_and_numpy_path(world, tmp_path):
    ctx = A.load_design(world["src"] / "arrays", N_DES)
    f = A.AttnMIL("A-MIL", RMAX, NCFG)
    cfg = f.sample(np.random.default_rng(0))
    # zero epochs: the net is at its initialisation, v = 0, so every weight is 1/1024 and the decision is NONE's
    tm = f.fit(ctx, cfg, np.arange(N_DES), 0, 7)
    w = f.weights(ctx, tm, np.arange(N_DES))
    assert np.allclose(w, 1.0 / M, atol=1e-7) and np.allclose(w.sum(-1), 1.0, atol=1e-5)
    for i in range(N_DES):
        for c in range(4):
            assert LS.decide(w[i, c], ctx.delta[i, c])["y"] == LS.arm_y(ctx.delta[i, c], None)[0] or A.tie_tolerance_ok(ctx.delta[i, c])
    # trained: softmax weights, and the numpy path equals the torch path
    tm = f.fit(ctx, cfg, np.arange(N_DES), 3, 7)
    w = f.weights(ctx, tm, np.arange(N_DES))
    assert np.allclose(w.sum(-1), 1.0, atol=1e-5) and (w > 0).all()
    mdl = A.export_model(f, tm)
    A.save_model(tmp_path / "attn.npz", mdl)
    loaded = A.load_model(tmp_path / "attn.npz")                            # the form that is frozen and scored
    assert loaded["kind"] == "attn" and np.abs(A.model_weights(loaded, ctx.X) - w).max() <= 1e-5


def test_a_sf_tie_goes_to_first_feature():
    assert A.select_column([0.5, 0.4, 0.4, 0.6]) == 1
    assert A.select_column([0.3, 0.3, 0.3]) == 0
    assert A.select_column([0.3] * 34 + [0.2]) == 34


def test_a_unl_weights():
    rng = np.random.default_rng(0)
    raw = {k: rng.normal(size=(2, 1, M)).astype(np.float32) for k in data.RAW}
    X = data.engineer(raw)
    w = A.unl_weights(X)
    assert w.shape == (2, 1, M) and (w >= 0).all() and (w <= 1).all() and (w.sum(-1) > 0).all()
    assert (w.min(-1) == 0).all()                                           # the single rank-1 token has weight 0
    assert np.allclose(w, 1.0 - data._rank(raw["s3"]))                      # rank_s3 is the LRF input feature (data._rank of s3)


# ---------------------------------------------------------------------------------------------------------------- seed slot and common resamples
def test_seed_slot_children_fixed():
    kids = A.cell_children()
    assert len(kids) == 8 and [tuple(k.spawn_key) for k in kids] == [(35, i) for i in range(8)]
    assert A.ROOT_SEED_ANALYSIS == 20261028 and A.SPAWN_KEY == (35,)
    assert A.CELL_NAMES == ("L1_clean", "L1_jpeg10", "L1_noise0.1", "L1_splice128", "LG_clean", "LG_shot_noise3", "LG_impulse_noise3", "LG_speckle_noise3")
    a6_keys = {tuple(c.spawn_key) for c in np.random.SeedSequence(A6.ROOT_SEED, spawn_key=A6.SPAWN_KEY).spawn(len(A6.SEED_SLOTS))}
    assert not a6_keys & {tuple(k.spawn_key) for k in kids}
    assert A.variants_record()["seed_slot"]["child_keys"] == [[35, i] for i in range(8)]


def test_common_resamples_within_a_cell_and_new_function_matches_a6():
    n = 50
    b1, b2 = A.CellBoot("L1_noise0.1", n), A.CellBoot("L1_noise0.1", n)
    assert np.array_equal(b1.idx, b2.idx) and b1.idx.shape == (10000, n)
    other = A.CellBoot("L1_clean", n)
    assert not np.array_equal(b1.idx, other.idx)
    rng = np.random.default_rng(3)
    yv, yn, yl = (rng.random(n) < p for p in (0.8, 0.7, 0.75))
    # the NONE contrast and the LRF contrast of one variant resample the SAME items
    d1, d2 = yv.astype(float) - yn, yv.astype(float) - yl
    m1 = (d1[b1.idx]).mean(1)
    assert b1.ci(d1) == [float(x) for x in np.quantile(m1, [0.025, 0.975])]
    assert np.array_equal(d1[b1.idx] - d2[b1.idx], (yl.astype(float) - yn)[b1.idx])     # same index matrix: contrasts are additive per resample
    # boot_ci_shared on an index matrix drawn the way a6_analysis.boot_ci draws it gives the same interval
    diff = rng.integers(-1, 2, 60).astype(float)
    r1, r2 = np.random.default_rng(9), np.random.default_rng(9)
    idx = np.concatenate([r2.integers(0, 60, size=(1000, 60)) for _ in range(10)])
    assert A.boot_ci_shared(diff, idx) == A6.boot_ci(diff, r1, levels=(0.95,))["ci95"]
    with pytest.raises(ValueError):
        b1.ci(np.zeros(n + 1))


# ---------------------------------------------------------------------------------------------------------------- refusals
def test_field_guard_refuses_gate_and_other_fields(tmp_path):
    write_items(tmp_path / "a", 1, ["clean"], 0)
    with np.load(tmp_path / "a" / "item0000.npz") as z:
        g = A.FieldGuard(z)
        for f in ("B", "D", "s3", "tbv", "tex", "nbr", "delta"):
            g[f"clean_{f}"]
        for bad in ("clean_flag0.05", "clean_z", "clean_codes", "clean_deltaL", "y_gatem", "m_gatem", "clean_flag0.1"):
            with pytest.raises(A.GateFieldRefused):
                g[bad]
        assert "clean_flag0.05" not in g and "clean_B" in g
        assert all(not k.endswith(("flag0.05", "_z", "_codes", "deltaL")) for k in g.accessed)


def test_prediction_reader_keeps_only_two_fields(tmp_path):
    p = tmp_path / "p.jsonl"
    p.write_text(json.dumps(dict(idx=0, condition="clean", y_none=1, y_lrf=0, y_gatem=1, m_gatem=0.2)) + "\n")
    r = A.read_prediction_controls(p)
    assert r == {(0, "clean"): dict(idx=0, condition="clean", y_none=1, y_lrf=0)}


def test_scorer_never_reads_gate_fields(world, tmp_path, monkeypatch):
    """Spy on np.load of the fresh arrays: every key the score path touches is an allowed field."""
    touched = []
    real = np.load

    class Spy:
        def __init__(self, z):
            self.z = z

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self.z.close()

        def __getitem__(self, k):
            touched.append(k)
            return self.z[k]

        def __contains__(self, k):
            return k in self.z

    def spy(path, *a, **kw):
        z = real(path, *a, **kw)
        parts = Path(str(path)).parts
        fresh = str(path).endswith(".npz") and "arrays" in parts and ("l1" in parts or "lg" in parts)
        return Spy(z) if fresh else z

    monkeypatch.setattr(A.np, "load", spy)
    A.score(world["fit"], world["l1"], world["lg"], tmp_path / "score_spy", frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    assert touched, "the spy saw no array access"
    assert all(A.FieldGuard.field_of(k) in A.ALLOWED_FIELDS for k in touched), sorted({k for k in touched if A.FieldGuard.field_of(k) not in A.ALLOWED_FIELDS})
    assert not any("flag" in k or "gatem" in k or k.endswith(("_z", "_codes", "deltaL")) for k in touched)


def test_hash_mismatch_refuses(world, tmp_path):
    cp = tmp_path / "fit_copy"
    shutil.copytree(world["fit"], cp)
    A.verify_fit(cp, require_git=False)                                     # intact copy passes
    with pytest.raises(A.HashMismatch):
        A.verify_fit(cp, require_git=True)                                  # not tracked in git
    (cp / "A-LIN" / "spec.json").write_text((cp / "A-LIN" / "spec.json").read_text() + " ")
    with pytest.raises(A.HashMismatch):
        A.verify_fit(cp, require_git=False)
    cp2 = tmp_path / "fit_copy2"
    shutil.copytree(world["fit"], cp2)
    H = json.loads((cp2 / "HASHES.json").read_text())
    H["code"]["analysis/paper2/lrf/ablation.py"] = dict(sha256="0" * 64, sha256_lf="0" * 64)
    (cp2 / "HASHES.json").write_text(json.dumps(H))
    with pytest.raises(A.HashMismatch):
        A.verify_fit(cp2, require_git=False)
    (cp2 / "HASHES.json").unlink()
    with pytest.raises(A.HashMismatch):
        A.verify_fit(cp2, require_git=False)


def test_score_refuses_on_hash_mismatch_before_touching_fresh_arrays(world, tmp_path):
    cp = tmp_path / "fit_copy"
    shutil.copytree(world["fit"], cp)
    (cp / "A-MIL" / "model.npz").write_bytes((cp / "A-MIL" / "model.npz").read_bytes() + b"0")
    with pytest.raises(A.HashMismatch):
        A.score(cp, world["l1"], world["lg"], tmp_path / "s", frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    assert not (tmp_path / "s" / "controls.json").exists() and not (tmp_path / "s" / "predictions_ablation.jsonl").exists()


def test_non_finite_input_stops(world, tmp_path):
    bad = tmp_path / "l1_nan"
    shutil.copytree(world["l1"], bad)
    p = bad / "arrays" / "item0001.npz"
    d = dict(np.load(p))
    d["clean_nbr"] = d["clean_nbr"].copy()
    d["clean_nbr"][3] = np.nan
    np.savez(p, **d)
    man = json.loads((bad / "arrays_manifest.json").read_text())
    man["files"]["item0001.npz"] = A.sha256_file(p)
    (bad / "arrays_manifest.json").write_text(json.dumps(man))
    with pytest.raises(A.NonFinite):
        A.score(world["fit"], bad, world["lg"], tmp_path / "s", frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    assert not (tmp_path / "s" / "predictions_ablation.jsonl").exists()
    with pytest.raises(A.NonFinite):                                        # an all-zero weight vector or non-finite Delta is a stop, never a wrong decision
        LS.decide(np.zeros(M), np.ones(M))
    with pytest.raises(A.NonFinite):
        LS.decide(np.ones(M), np.r_[np.nan, np.ones(M - 1)])


def test_manifest_mismatch_refuses(world, tmp_path):
    bad = tmp_path / "l1_bad"
    shutil.copytree(world["l1"], bad)
    p = bad / "arrays" / "item0000.npz"
    p.write_bytes(p.read_bytes() + b"0")
    with pytest.raises(A.HashMismatch):
        A.verify_manifest(bad)


# ---------------------------------------------------------------------------------------------------------------- controls first; end to end
def test_controls_written_before_any_variant_weighting(world, tmp_path, monkeypatch):
    seen = {}

    def spy(cells, weightings, out_path):
        seen["controls_exists"] = (tmp_path / "s" / "controls.json").exists()
        seen["n_weightings"] = len(weightings)
        raise RuntimeError("stop after the check")

    monkeypatch.setattr(A, "compute_variant_predictions", spy)
    with pytest.raises(RuntimeError, match="stop after the check"):
        A.score(world["fit"], world["l1"], world["lg"], tmp_path / "s", frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    assert seen["controls_exists"] is True and seen["n_weightings"] == 24 + 3 + 18
    c = json.loads((tmp_path / "s" / "controls.json").read_text())
    assert c["ok"] and c["NONE_vs_y_none"]["n_mismatch"] == 0 and c["LRF_vs_y_lrf"]["n_mismatch"] == 0 and c["KO_ALL_vs_NONE"]["n_differing_beyond_tolerance"] == 0
    assert c["lg_l1_image_overlap"]["n_image_overlap"] == 4 and c["lg_l1_image_overlap"]["lg_image_ids_equal_first_n_of_l1"] is True


def test_control_mismatch_halts_with_no_variant_output(world, tmp_path):
    l1 = tmp_path / "l1_flip"
    shutil.copytree(world["l1"], l1)
    lines = [json.loads(l) for l in (l1 / "predictions.jsonl").read_text().splitlines()]
    lines[2]["y_lrf"] = 1 - lines[2]["y_lrf"]
    (l1 / "predictions.jsonl").write_text("".join(json.dumps(l) + "\n" for l in lines))
    with pytest.raises(A.ControlMismatch):
        A.score(world["fit"], l1, world["lg"], tmp_path / "s", frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    c = json.loads((tmp_path / "s" / "controls.json").read_text())
    assert not c["ok"] and c["LRF_vs_y_lrf"]["n_mismatch"] == 1
    assert sorted(p.name for p in (tmp_path / "s").iterdir()) == ["controls.json", "env-lock.txt"]
    l1b = tmp_path / "l1_flipnone"
    shutil.copytree(world["l1"], l1b)
    lines = [json.loads(l) for l in (l1b / "predictions.jsonl").read_text().splitlines()]
    lines[0]["y_none"] = 1 - lines[0]["y_none"]
    (l1b / "predictions.jsonl").write_text("".join(json.dumps(l) + "\n" for l in lines))
    with pytest.raises(A.ControlMismatch):
        A.score(world["fit"], l1b, world["lg"], tmp_path / "s2", frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    assert not (tmp_path / "s2" / "predictions_ablation.jsonl").exists()


@pytest.fixture(scope="module")
def scored(world, tmp_path_factory):
    out = tmp_path_factory.mktemp("scored") / "score"
    meta = A.score(world["fit"], world["l1"], world["lg"], out, frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    return out, meta


def test_score_and_analyse_end_to_end(world, scored):
    out, meta = scored
    n_expected = (5 * 4 + 4 * 4) * (24 + 21)
    assert meta["n_lines"] == n_expected and meta["controls_ok"]
    # once only
    with pytest.raises(A.FitRefused):
        A.score(world["fit"], world["l1"], world["lg"], out, frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    res = A.analyse(out)
    assert res["K"] == 336 == res["K_expected"]
    assert [r["id"] for r in res["rows"]] == list(A.INTERVAL_ROWS) and "KO-ALL" not in [r["id"] for r in res["rows"]]
    assert list(res["n_per_cell"]) == list(A.CELL_NAMES)
    assert res["n_per_cell"]["L1_clean"] == 5 and res["n_per_cell"]["LG_clean"] == 4
    for r in res["rows"]:
        for cell, v in r["cells"].items():
            for k in ("vs_NONE", "vs_LRF"):
                d = v[k]
                n = res["n_per_cell"][cell]
                assert abs(d["d"] - (d["b"] - d["c"]) / n) < 1e-12 and len(d["ci95"]) == 2
    assert res["ko_all_control"]["n_differing_beyond_tolerance"] == 0 and isinstance(res["ko_all_control"]["decisions_identical"], bool)
    assert res["meta"]["child_keys"] == [[35, i] for i in range(8)] and res["meta"]["levels"] == [0.95]
    assert "sign" in res["meta"] and "{K}" in res["mandatory_text_sc1"]
    s = res["seed_spread"]["rows"]
    assert set(s) == {"LRF-H", *A.FITTED}
    for v, cells in s.items():
        for cell, x in cells.items():
            assert len(x["acc_seed0_seed1_seed2"]) == 3 and abs(x["range"] - (max(x["acc_seed0_seed1_seed2"]) - min(x["acc_seed0_seed1_seed2"]))) < 1e-12
    # no flags, no ranking keys anywhere in the output
    def keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield k
                yield from keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from keys(v)
    allkeys = set(keys(res))
    for bad in ("significant", "excludes_zero", "above_zero", "below_zero", "rank", "ranking", "p_value", "p_one", "p", "holm", "flag"):
        assert bad not in allkeys
    # the NONE row of the references equals the NONE weighting
    P = A.load_ablation_predictions(out / "predictions_ablation.jsonl")
    for cell in A.CELL_NAMES:
        assert res["references_accuracy"]["NONE"][cell] == float(P["NONE"][cell][1].mean())


def test_ko_all_prediction_rows_equal_none_within_tolerance(scored):
    out, _ = scored
    P = A.load_ablation_predictions(out / "predictions_ablation.jsonl")
    for cell in A.CELL_NAMES:
        assert np.array_equal(P["KO-ALL"][cell][1], P["NONE"][cell][1])


def test_determinism(world, scored, tmp_path):
    out, _ = scored
    out2 = tmp_path / "score2"
    A.score(world["fit"], world["l1"], world["lg"], out2, frozen_dir=world["frozen"], require_git=False, log=lambda *_: None)
    assert A.sha256_file(out / "predictions_ablation.jsonl") == A.sha256_file(out2 / "predictions_ablation.jsonl")
    r1, r2 = A.analyse(out, out_path=tmp_path / "a1.json"), A.analyse(out2, out_path=tmp_path / "a2.json")
    assert (tmp_path / "a1.json").read_text() == (tmp_path / "a2.json").read_text() and r1["K"] == r2["K"]
    # the fit is deterministic: refitting A-LIN from scratch gives the identical model file contents
    src = world["src"]
    ctx = A.load_design(src / "arrays", N_DES)
    f = A.make_family("A-LIN", RMAX, NCFG)
    cfg, score, _ = lrun.successive_halving(ctx, f, np.arange(N_DES), 99, 0)
    m = A.export_model(f, f.fit(ctx, cfg, np.arange(N_DES), RMAX, A._seed(0)))
    z = np.load(world["fit"] / "A-LIN" / "model.npz")
    assert all(np.array_equal(z[k], m[k]) for k in ("a", "b", "c", "knots", "mu", "sd"))
    assert float(score) == json.loads((world["fit"] / "A-LIN" / "spec.json").read_text())["inner_cv_o1"]


def test_lrf_recomputed_by_scorer_equals_lrf_score_weights(world):
    """The scorer's numpy LRF weights equal lrf_score.weights (the code that wrote y_lrf) on a stored item."""
    fz = LS.load_frozen(world["frozen"])
    d = dict(np.load(world["l1"] / "arrays" / "item0000.npz"))
    cell = A._load_cell(world["l1"], "noise0.1", LS.committed_rows(world["l1"]), fz["engineer"])
    w = A.model_weights(A.frozen_model(fz), cell["X"])[0]
    assert np.abs(w - LS.weights(fz, d, "noise0.1")).max() <= 1e-12


def test_load_design_matches_data_load(world):
    d = data.load(world["src"] / "arrays", N_DES)
    X = data.engineer(d["raw"])
    ctx = A.load_design(world["src"] / "arrays", N_DES)
    assert np.array_equal(ctx.X, X) and np.array_equal(ctx.delta, d["delta"])


def test_real_r0_recorded_if_present():
    p = ROOT / "runs" / "P2-LRF-ABL-FIT" / "R0.json"
    if not p.exists():
        pytest.skip("real fit not run yet")
    r0 = json.loads(p.read_text())
    assert r0["ok"] and r0["cfg_equal"] and r0["max_abs_weight_diff"] <= 1e-5
