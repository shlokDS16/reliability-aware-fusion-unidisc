"""S2 re-infill (SAP AD.5, AB.4): sampler semantics, equal-size random comparator, rows and arrays of the runner on the fake network, prerequisite stops, figure subset, and the analysis
(family S2, Holm m = 2 with p = 1 fill, g_i = 0 concordance, n >= 120 rule, claim limits). CPU only; no model, no GPU."""
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import torch                                                                   # noqa: E402
from exp_p2 import common, run_gate_s2                                         # noqa: E402
from exp_p2.gate import analysis_s2 as S, arms, config, evidence, pipeline, reinfill, runner, seeds, stats    # noqa: E402
from exp_p2.scoring import IMG_HI, IMG_LO, IMG_OFFSET, MASK_ID                 # noqa: E402
from fake_gate import FakeScorer, fake_image                                    # noqa: E402
from test_gate_runners_fake import _fold, _sc, _write_folds, env                # noqa: E402,F401  (env: the shared fixture)

M = 16          # tokens of the fake 4 x 4 grid


# ------------------------------------------------------------------------------------------------ schedule
def test_step_sizes_exhaust_the_set_in_at_most_16_steps():
    assert reinfill.step_sizes(64) == [4] * 16 and reinfill.step_sizes(10) == [1] * 10 and reinfill.step_sizes(0) == []
    for g in range(0, 300):
        ks = reinfill.step_sizes(g)
        assert sum(ks) == g and len(ks) == min(g, 16) and all(k >= 1 for k in ks), g
        assert ks == sorted(ks, reverse=True) or g == 0 or max(ks) - min(ks) <= 1               # k_s = ceil(|U| / steps left): sizes differ by at most one
    assert reinfill.step_sizes(20) == [2, 2, 2, 2] + [1] * 12 and reinfill.n_passes(20) == 4 * 16


# ------------------------------------------------------------------------------------------------ the sampler on the fake network
def _setup(seed=0, caption="red blue green small"):
    sc = FakeScorer(grid=4, seed=seed)
    cap = sc.caption_ids(caption)
    codes = (np.arange(M) * 977 + 5) % 16384
    return sc, cap, codes, sc.build(cap, codes)


def test_rows_mask_exactly_the_remaining_set_and_the_caption_and_nothing_else():
    sc, cap, codes, st = _setup()
    S_ = np.array([2, 5, 6, 9, 11])
    reinfill.reinfill(sc, st, codes, [S_, S_], [np.random.default_rng(1), np.random.default_rng(2)], [10, 11])
    ks = reinfill.step_sizes(5)
    assert len(sc.rows) == 2 * len(ks)
    base, img, cp = st["base"], st["img_pos"], st["cap_pos"]
    for step, k in enumerate(ks):
        for b in range(2):
            x = sc.rows[step * 2 + b]
            masked_img = (x[img] == MASK_ID).nonzero().flatten().tolist()
            assert (x[cp] == MASK_ID).all()                                                # R1: caption masked in every row
            assert len(masked_img) == 5 - sum(ks[:step]) and set(masked_img) <= set(S_.tolist())
            done = [j for j in S_.tolist() if j not in masked_img]
            assert all(IMG_LO <= int(x[img[j]]) < IMG_HI for j in done)                    # already sampled positions hold image-vocabulary ids
            outside = [j for j in range(M) if j not in S_.tolist()]
            assert (x[img[outside]] == base[img[outside]]).all()                           # the rest of the image is the observed (corrupted) code
            assert (x[:cp[0]] == base[:cp[0]]).all() and x[-1] == base[-1]                  # layout and closing token untouched


def test_caption_visible_leaves_the_caption_in_every_row():
    sc, cap, codes, st = _setup()
    reinfill.reinfill(sc, st, codes, [np.array([1, 4, 8])], [np.random.default_rng(1)], [3], caption_visible=True)
    assert all((x[st["cap_pos"]] == st["base"][st["cap_pos"]]).all() for x in sc.rows)


def test_output_changes_only_the_set_and_stays_in_the_image_vocabulary_and_is_deterministic():
    sc, cap, codes, st = _setup()
    S_ = np.array([0, 3, 4, 10, 15, 7])
    args = ([S_] * 4, [np.random.default_rng(100 + b) for b in range(4)], [7, 8, 9, 10])
    r1 = reinfill.reinfill(sc, st, codes, *args)
    outside = np.setdiff1d(np.arange(M), S_)
    assert (r1["codes"][:, outside] == codes[outside]).all() and r1["codes"].min() >= 0 and r1["codes"].max() < 16384
    assert len({tuple(r1["codes"][b, S_]) for b in range(4)}) > 1                           # independent draws differ (fake net is not deterministic argmax)
    r2 = reinfill.reinfill(sc, st, codes, [S_] * 4, [np.random.default_rng(100 + b) for b in range(4)], [7, 8, 9, 10])
    assert np.array_equal(r1["codes"], r2["codes"]) and np.array_equal(r1["logp"], r2["logp"])
    assert np.array_equal(np.sort(r1["order"], axis=1), np.tile(np.sort(S_), (4, 1)))       # each draw visits every set position once
    assert len({tuple(o) for o in r1["order"]}) > 1


def test_a_draw_does_not_depend_on_the_batch_it_is_run_in():
    sc, cap, codes, st = _setup()
    S_ = np.array([1, 2, 6, 9, 12])
    mk = lambda: ([S_] * 4, [np.random.default_rng(40 + b) for b in range(4)], [1, 2, 3, 4])
    together = reinfill.reinfill(sc, st, codes, *mk(), bs=4)
    alone = reinfill.reinfill(sc, st, codes, *mk(), bs=1)
    assert np.array_equal(together["codes"], alone["codes"]) and np.allclose(together["logp"], alone["logp"], atol=1e-5)


def test_chain_likelihood_is_the_sum_of_log_probs_of_the_sampled_tokens_given_the_growing_context():
    sc, cap, codes, st = _setup()
    S_ = np.array([3, 7])
    rf = reinfill.reinfill(sc, st, codes, [S_], [np.random.default_rng(5)], [123])
    perm = S_[np.random.default_rng(5).permutation(2)]
    f = sc.logits_fn(st)
    base, img, cp = st["base"], st["img_pos"], st["cap_pos"]
    x = base.clone()
    x[cp] = MASK_ID
    x[img[torch.as_tensor(S_)]] = MASK_ID
    total = 0.0
    for j in perm:
        lp = torch.log_softmax(f(x[None])[0, img[j], IMG_LO:IMG_HI].float(), -1)
        c = int(rf["codes"][0, j])
        total += float(lp[c])
        x[img[j]] = c + IMG_OFFSET
    assert rf["logp"][0] == pytest.approx(total, abs=1e-4) and rf["logp"][0] < 0
    assert rf["n_steps"] == 2


def test_empty_set_costs_nothing_and_unequal_sets_are_refused():
    sc, cap, codes, st = _setup()
    r = reinfill.reinfill(sc, st, codes, [np.zeros(0, int)] * 4, [np.random.default_rng(1)] * 4, [1, 2, 3, 4])
    assert np.array_equal(r["codes"], np.tile(codes, (4, 1))) and r["n_steps"] == 0 and sc.rows == []
    with pytest.raises(AssertionError, match="equal gate size"):
        reinfill.reinfill(sc, st, codes, [np.array([1, 2]), np.array([3])], [np.random.default_rng(1)] * 2, [1, 2])


def test_keep_best_takes_the_highest_own_likelihood_and_ties_go_to_the_lowest_draw():
    assert reinfill.keep_best(np.array([-3.0, -1.0, -2.0, -1.0])) == 1
    assert reinfill.keep_best(np.array([-2.0, -2.0, -2.0, -2.0])) == 0


def test_token_agreement_is_over_changed_tokens_and_over_the_reinfilled_positions():
    clean = np.array([1, 2, 3, 4, 5, 6])
    corr = np.array([1, 9, 9, 4, 5, 9])                  # tokens 1, 2, 5 changed
    final = np.array([1, 2, 7, 4, 5, 9])                  # token 1 restored, 2 re-infilled wrongly, 5 not covered
    rep = np.array([0, 1, 1, 0, 0, 0], bool)
    a = reinfill.token_agreement(final, clean, corr, rep)
    assert a["agree_changed"] == pytest.approx(1 / 3) and a["agree_set"] == pytest.approx(1 / 2)
    assert math.isnan(reinfill.token_agreement(clean, clean, clean, rep)["agree_changed"]) and math.isnan(reinfill.token_agreement(final, clean, corr, np.zeros(6, bool))["agree_set"])


# ------------------------------------------------------------------------------------------------ arms: equal-size random comparator
def test_irand_sets_have_gate_size_are_new_per_draw_and_ignore_the_gate_content():
    G = np.zeros(M, bool)
    G[[0, 1, 2, 3, 4]] = True
    z = np.zeros(M, bool)
    z[[8, 9]] = True
    sets, orders, seeds_ = run_gate_s2._arm_sets("irand", 2001, 0, G, z, 4, M)
    assert all(len(s) == 5 for s in sets) and len({tuple(s) for s in sets}) > 1
    G2 = np.zeros(M, bool)
    G2[[10, 11, 12, 13, 14]] = True
    sets2, _, _ = run_gate_s2._arm_sets("irand", 2001, 0, G2, z, 4, M)
    assert all(np.array_equal(a, b) for a, b in zip(sets, sets2))                         # independent of G's content, equal only in size
    gs, _, _ = run_gate_s2._arm_sets("igate", 2001, 0, G, z, 4, M)
    cs, _, _ = run_gate_s2._arm_sets("ichg", 2001, 0, G, z, 4, M)
    assert all(np.array_equal(s, np.flatnonzero(G)) for s in gs) and all(np.array_equal(s, np.flatnonzero(z)) for s in cs)
    assert len(set(seeds_)) == 4                                                           # one sampling seed per draw
    others = [run_gate_s2._arm_sets(a, 2001, 0, G, z, 4, M)[2] for a in ("igate", "ichg", "ileak")]
    assert len({tuple(o) for o in others + [seeds_]}) == 4                                  # every arm has its own sampling seeds


# ------------------------------------------------------------------------------------------------ the runner on a hand-made M4 run
CONDS = ["patch", "splice128"]


def make_m4(env, sc, items, g_of):
    """Write runs/P2-GATE-M4 the way run_gate_m4 does for the keys S2 reads: arrays clean_codes, <cond>_codes/_z/_flag0.05 and rows with the stored Y of none and GATE-M."""
    m4 = env / "P2-GATE-M4"
    (m4 / "arrays").mkdir(parents=True, exist_ok=True)
    rows = []
    for it in items:
        pil, clean = pipeline.prep_image(sc, it["image_id"])
        cap, neg = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
        lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap, neg, clean)
        arrays, row = {"clean_codes": clean.astype(np.int16)}, dict(idx=it["idx"], conds={})
        for cond in CONDS:
            rng = np.random.default_rng([it["idx"], len(cond)])
            pos = rng.choice(M, 4, replace=False)
            codes = clean.copy()
            codes[pos] = (clean[pos] + 1 + rng.integers(0, 5000, 4)) % 16384
            z = codes != clean
            G = np.zeros(M, bool)
            G[g_of(it["idx"], cond, z)] = True
            d = pipeline.image_delta(lam_pos, lam_neg, codes)
            arrays.update({f"{cond}_codes": codes.astype(np.int16), f"{cond}_z": z, f"{cond}_flag0.05": G})
            row["conds"][cond] = dict(img={"none": {"y": int(d.mean() > 0)}, "gate0.05": {"y": evidence.evidence_from_delta(d, ~G)["y"]}})
        np.savez(m4 / "arrays" / f"item{it['idx']:04d}.npz", **arrays)
        rows.append(row)
    (m4 / "items.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    (m4 / "token_exclusions.json").write_text(json.dumps(dict(excluded={"test": [], "test_ext": []}, n_excluded_total=0)))
    (env / "P2-GATE-M3").mkdir(exist_ok=True)
    (env / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="d", n_rule=dict(rule="R1", test_fold=300), family=[dict(corruption="splice", severity=128, key="splice128")])))


def g_of(idx, cond, z):
    if idx == 1:
        return np.zeros(0, int)                                   # g_i = 0
    if cond == "patch":
        return np.flatnonzero(z)[:3]                              # 3 of the 4 changed tokens
    return np.concatenate([np.flatnonzero(z)[:2], [(np.flatnonzero(z)[0] + 5) % M]]) if idx % 2 else np.flatnonzero(z)       # splice: odd items include one clean token


def _stable(row):
    """A row without its wall-clock fields."""
    return {k: ({c: {kk: vv for kk, vv in cr.items() if kk != "seconds_cond"} for c, cr in v.items()} if k == "conds" else v) for k, v in row.items() if k != "n_rows"}


def _ns(**kw):
    return SimpleNamespace(**dict(dict(m4_run="P2-GATE-M4", arms="igate,irand,ichg", leak=False, n=4), **kw))


@pytest.fixture
def s2env(env):
    sc = _sc()
    items = _fold(4, offset=2000)
    _write_folds(env, test=items)
    make_m4(env, sc, items, g_of)
    return env, sc, items


def test_s2_item_rows_arrays_pass_count_and_m4_agreement(s2env):
    env, sc, items = s2env
    ctx = run_gate_s2.make_ctx_factory(_ns(), env)(sc, env / "P2-GATE-S2")
    assert ctx.conds == CONDS and ctx.arms == ("igate", "irand", "ichg")
    row, arrays = run_gate_s2.process(sc, items[0], ctx)
    for cond in CONDS:
        cr = row["conds"][cond]
        assert set(cr["arms"]) == {"none", "m", "igate", "irand", "ichg"}
        assert cr["s2_y_matches_m4"] == dict(none=True, gate=True)                      # S2's own two passes reproduce M4's stored Y of NONE and GATE-M on the fake net
        g = cr["g"]
        for arm in ("igate", "irand"):
            a = cr["arms"][arm]
            assert a["n_set"] == g and len(a["y_draws"]) == 4 and a["y"] == a["y_draws"][a["kept"]] and a["kept"] == int(np.argmax(a["logp"])) and a["n_steps"] == min(g, 16)
        assert cr["arms"]["ichg"]["n_set"] == cr["n_changed"] == 4
        assert arrays[f"{cond}_codes_igate"].shape == (4, M) and arrays[f"{cond}_set_irand"].sum(axis=1).tolist() == [g] * 4 and arrays[f"{cond}_G"].sum() == g
        assert (arrays[f"{cond}_set_ichg"][0] == arrays[f"{cond}_z"]).all()
    want = 2 + sum(reinfill.n_passes(row["conds"][c]["g"]) * 2 + reinfill.n_passes(4) for c in CONDS)        # 2 caption-only passes + igate + irand + ichg per condition
    assert row["n_rows"] == want
    row2, arrays2 = run_gate_s2.process(sc, items[0], ctx)                              # deterministic
    assert _stable(row2) == _stable(row)
    assert all(np.array_equal(arrays[k], arrays2[k]) for k in arrays)


def test_g_zero_items_are_identical_across_arms_and_cost_only_the_oracle_arm(s2env):
    env, sc, items = s2env
    ctx = run_gate_s2.make_ctx_factory(_ns(), env)(sc, env / "P2-GATE-S2")
    row, arrays = run_gate_s2.process(sc, items[1], ctx)
    cr = row["conds"]["patch"]
    assert cr["g"] == 0 and cr["arms"]["igate"]["n_steps"] == 0 and cr["arms"]["igate"]["y_draws"] == [cr["arms"]["none"]["y"]] * 4
    assert cr["arms"]["igate"]["y"] == cr["arms"]["irand"]["y"] == cr["arms"]["none"]["y"] == cr["arms"]["m"]["y"]
    assert (arrays["patch_codes_igate"] == arrays["patch_codes"]).all() and (arrays["patch_codes_irand"] == arrays["patch_codes"]).all()
    assert row["n_rows"] == 2 + 2 * reinfill.n_passes(4)                                # caption passes + I-CHG of the two conditions; I-GATE and I-RAND4 cost nothing


def test_arms_can_be_cut_but_igate_and_irand_are_required_and_leak_is_one_draw_with_the_caption_visible(s2env):
    env, sc, items = s2env
    ctx = run_gate_s2.make_ctx_factory(_ns(arms="igate,irand", leak=True), env)(sc, env / "P2-GATE-S2")
    row, arrays = run_gate_s2.process(sc, items[0], ctx)
    assert set(row["conds"]["patch"]["arms"]) == {"none", "m", "igate", "irand", "ileak"} and len(row["conds"]["patch"]["arms"]["ileak"]["y_draws"]) == 1
    assert arrays["patch_codes_ileak"].shape == (1, M)
    assert run_gate_s2.main(["--arms", "igate"]) == 2 and run_gate_s2.main(["--arms", "igate,irand,bogus"]) == 2


def test_runner_loop_writes_rows_with_seconds_resumes_and_leaves_arrays(s2env, monkeypatch):
    env, sc, items = s2env
    ns = _ns()
    kw = dict(run_id="P2-GATE-S2", cfg=dict(run_gate_s2.CONFIG, n_items=4), load=lambda: sc, get_items=lambda s, r: items, process=run_gate_s2.process,
              make_ctx=run_gate_s2.make_ctx_factory(ns, env), duty=1.0, soft_minutes=30)
    assert runner.run_items(limit=2, **kw) == runner.EXIT_MORE_WORK
    assert len(common.read_jsonl(env / "P2-GATE-S2" / "items.jsonl")) == 2
    assert runner.run_items(**kw) == 0
    rows = common.read_jsonl(env / "P2-GATE-S2" / "items.jsonl")
    assert [r["idx"] for r in rows] == [0, 1, 2, 3] and all(r["seconds"] > 0 and "n_rows" in r for r in rows)          # peak_gb is added by the runner when CUDA is present (GPU only)
    assert all((env / "P2-GATE-S2" / "arrays" / f"item{i:04d}.npz").exists() for i in range(4))


# ------------------------------------------------------------------------------------------------ prerequisites are checked before any model is touched
def test_main_stops_without_m4_family_or_complete_rows_and_never_loads_a_model(env, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("must not load a model or start the loop")
    monkeypatch.setattr(runner, "run_items", boom)
    assert run_gate_s2.main([]) == 2                                                     # no family.json
    sc = _sc()
    items = _fold(4, offset=2000)
    _write_folds(env, test=items)
    make_m4(env, sc, items, g_of)
    (env / "P2-GATE-M4" / "arrays" / "item0003.npz").unlink()
    assert run_gate_s2.main(["--n", "4"]) == 2                                           # M4 incomplete for the S2 list
    (env / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="z", family=[])))
    assert run_gate_s2.main(["--n", "4"]) == 2


def test_the_s2_list_follows_m4s_order_and_exclusions_without_replacement(env):
    items = _fold(6, offset=2000)
    _write_folds(env, test=items)
    (env / "P2-GATE-M4").mkdir()
    (env / "P2-GATE-M4" / "token_exclusions.json").write_text(json.dumps(dict(excluded={"test": [2], "test_ext": []})))
    got, info = run_gate_s2.plan_items(5, env)
    assert [it["idx"] for it in got] == [0, 1, 3, 4] and info == dict(planned=5, excluded=1, n_requested=5)
    with pytest.raises(ValueError, match="asked for more"):
        run_gate_s2.plan_items(9, env)


def test_conditions_are_patch_plus_the_splice_key_only_if_it_has_an_operating_point(env):
    (env / "P2-GATE-M3").mkdir()
    fp = env / "P2-GATE-M3" / "family.json"
    fp.write_text(json.dumps(dict(endpoint="d", family=[dict(corruption="jpeg", severity=10, key="jpeg10"), dict(corruption="splice", severity=192, key="splice192")])))
    assert run_gate_s2.s2_conditions(env) == ["patch", "splice192"]
    fp.write_text(json.dumps(dict(endpoint="d", family=[dict(corruption="jpeg", severity=10, key="jpeg10")])))
    assert run_gate_s2.s2_conditions(env) == ["patch"]


# ------------------------------------------------------------------------------------------------ figures
def _frow(idx, g, yi, yn, cond="patch"):
    return dict(idx=idx, conds={cond: dict(g=g, arms=dict(igate=dict(y=yi), none=dict(y=yn)))})


def test_figure_subset_is_first_8_with_g_ge_1_and_first_4_harm_cases_in_list_order():
    rows = [_frow(i, 0 if i < 3 else 2, 1, 1) for i in range(30)]
    rows[12] = _frow(12, 2, 0, 1)
    rows[14] = _frow(14, 0, 0, 1)                         # harm case with g = 0 still counts as a harm case
    for i in (20, 21, 22, 25):
        rows[i] = _frow(i, 2, 0, 1)
    sel = run_gate_s2.select_figure_items(rows, ["patch", "splice128"])
    assert sel["patch"]["first"] == [3, 4, 5, 6, 7, 8, 9, 10] and sel["patch"]["harm"] == [12, 14, 20, 21]
    assert sel["splice128"] == dict(first=[], harm=[])


def test_process_fig_decodes_only_the_subset_and_names_the_not_selected_draw(s2env, tmp_path):
    env, sc, items = s2env
    ctx = run_gate_s2.make_ctx_factory(_ns(), env)(sc, env / "P2-GATE-S2")
    out_rows = []
    for it in items[:1]:
        row, arrays = run_gate_s2.process(sc, it, ctx)
        (env / "P2-GATE-S2" / "arrays").mkdir(parents=True, exist_ok=True)
        np.savez(env / "P2-GATE-S2" / "arrays" / f"item{it['idx']:04d}.npz", **arrays)
        out_rows.append(dict(row, idx=it["idx"]))
    calls = []
    sc._sc.decode = lambda codes: calls.append(1) or fake_image(int(np.sum(codes)) % 1000, 64)
    figctx = SimpleNamespace(run=env / "P2-GATE-S2-FIG", s2=env / "P2-GATE-S2", s2_rows={r["idx"]: r for r in out_rows})
    figctx.run.mkdir()
    row, arrays = run_gate_s2.process_fig(sc, dict(items[0], roles={"patch": "first"}), figctx)
    assert arrays == {} and len(calls) == len(row["files"]) - 1 and len(calls) == 1 + 1 + 4 + 1          # clean, corrupted, igate x2, irand x2, ichg (overlay is a numpy blend of the corrupted decode)
    names = set(row["files"])
    assert "item0000_clean.png" in names and "item0000_patch_corrupted.png" in names and "item0000_patch_overlay_G.png" in names and "item0000_patch_ichg_selected.png" in names
    assert any(n.startswith("item0000_patch_igate_draw1") for n in names) and any(n.startswith("item0000_patch_irand_draw1") for n in names)
    assert all((figctx.run / "png" / n).exists() for n in names) and "caption masked; not typical samples" in row["roles"]["patch"]["caption"]


def test_overlay_tints_only_the_flagged_cells():
    from PIL import Image
    img = Image.new("RGB", (64, 64), (100, 100, 100))
    G = np.zeros(16, bool)
    G[5] = True                                            # cell (1, 1) of the 4 x 4 grid = pixels 16..31
    a = np.asarray(run_gate_s2.overlay(img, G))
    assert (a[16:32, 16:32, 0] > 100).all() and (a[16:32, 16:32, 1] < 100).all()
    mask = np.ones((64, 64), bool)
    mask[16:32, 16:32] = False
    assert (a[mask] == 100).all()


# ------------------------------------------------------------------------------------------------ analysis (family S2)
def _arm(y, g=3, draws=None):
    return dict(y=y, d=0.0, kept=0, y_draws=draws or [y] * 4, logp=[0.0] * 4, n_steps=min(g, 16), n_set=g, agree_changed=0.5, agree_set=0.5, agree_changed_mean=0.5)


def _row(i, g, yg, yr, yn=0, ym=0, yc=1, cond="patch", dg=None, dr=None):
    return dict(idx=i, conds={cond: dict(g=g, n_changed=4, n_tp=min(g, 4), recall=min(g, 4) / 4, precision=1.0 if g else float("nan"), s2_y_matches_m4=dict(none=True, gate=True),
                                         arms=dict(none=dict(y=yn, d=0.0), m=dict(y=ym, d=0.0), igate=_arm(yg, g, dg), irand=_arm(yr, g, dr), ichg=_arm(yc, 4)))})


def _table(b, c, n_g0=0, n_conc=0, cond="patch"):
    rows = [_row(i, 3, 1, 0, cond=cond) for i in range(b)] + [_row(b + i, 3, 0, 1, cond=cond) for i in range(c)]
    rows += [_row(b + c + i, 3, 1, 1, cond=cond) for i in range(n_conc)] + [_row(b + c + n_conc + i, 0, 1, 1, cond=cond) for i in range(n_g0)]
    return rows


def test_s2_family_counts_p_holm_and_g_zero_items_stay_in_n():
    rows = _table(30, 4, n_g0=20, n_conc=80)
    out = S.s2_family(rows, n_boot=300)
    e = out["per_cell"]["patch"]
    assert (e["b"], e["c"], e["n_d"], e["n"], e["n_g0"], e["n_g0_discordant"]) == (30, 4, 34, 134, 20, 0)
    assert e["p"] == pytest.approx(stats.mcnemar_exact([1] * 30 + [0] * 4, [0] * 30 + [1] * 4)["p"])
    sp = out["per_cell"]["splice"]
    assert not sp["tested"] and sp["p"] == 1.0 and sp["p_holm"] == 1.0 and sp["reading"] == "not run"                  # no splice rows: p = 1, m stays 2
    assert e["p_holm"] == pytest.approx(min(1.0, 2 * e["p"])) and e["location_supported"] and out["holm_m"] == 2
    assert out["comparator"] == "random-gate best-of-4 re-infill (G.1-inspired)" and "G.1 comparator" in " ".join(out["forbidden_wording"])
    assert "improves" not in e["sentence"].replace("improvement of verification over no repair", "")


def test_s2_below_n_min_is_descriptive_only_and_wrong_direction_is_not_support():
    out = S.s2_family(_table(40, 2, n_conc=30), n_boot=200)                              # n = 72 < 120
    e = out["per_cell"]["patch"]
    assert not e["tested"] and e["p_used"] == 1.0 and e["p_holm"] == 1.0 and not e["location_supported"] and "descriptive only" in e["note"]
    big = S.s2_family(_table(2, 30, n_conc=100), n_boot=300)["per_cell"]["patch"]       # I-GATE worse than I-RAND4
    assert big["tested"] and big["p_holm"] < 0.05 and not big["location_supported"] and big["location_refuted"] and big["reading"].startswith("refuted")


def test_s2_prints_the_descriptive_contrasts_beside_every_test_with_no_p_values():
    rows = _table(30, 4, n_conc=100)
    for r in rows[:30]:                                                                  # igate beats none on the b-items by construction below; set none = 0 there
        r["conds"]["patch"]["arms"]["none"]["y"] = 0
    out = S.s2_family(rows, n_boot=300)["per_cell"]["patch"]["desc"]
    for k in ("igate_vs_none", "igate_vs_m", "irand_vs_none", "igate_vs_ichg"):
        assert out[k] is not None and "p" not in out[k] and "p_mid" not in out[k] and {"b", "c", "n_d", "delta", "ci95"} <= set(out[k])
    assert {"draw_level_accuracy_igate_minus_irand", "all_four_correct_igate_minus_irand", "kept_draw_igate_minus_irand", "token_agreement_with_clean_codes", "gate_recall_mean",
            "gate_precision_mean_over_g_ge_1", "s2_y_differs_from_m4"} <= set(out)
    assert out["token_agreement_with_clean_codes"]["igate_agree_changed"] == pytest.approx(0.5) and out["s2_y_differs_from_m4"]["none"] == 0


def test_s2_draw_level_and_all_four_contrasts_use_the_four_draws():
    rows = [_row(i, 3, 1, 1, dg=[1, 1, 1, 1], dr=[1, 0, 0, 0]) for i in range(100)] + [_row(100 + i, 3, 1, 1, dg=[1, 1, 1, 0], dr=[1, 1, 1, 1]) for i in range(40)]
    d = S.s2_family(rows, n_boot=300)["per_cell"]["patch"]["desc"]
    assert d["draw_level_accuracy_igate_minus_irand"]["diff"] == pytest.approx((100 * (1 - 0.25) + 40 * (0.75 - 1)) / 140)
    assert d["all_four_correct_igate_minus_irand"]["diff"] == pytest.approx((100 * (1 - 0) + 40 * (0 - 1)) / 140)
    assert d["kept_draw_igate_minus_irand"]["diff"] == 0.0                              # same kept-draw Y: the confirmatory contrast sees nothing, the tail contrasts do


def test_s2_no_repair_claim_when_not_better_than_none_and_not_rejected():
    rows = [_row(i, 3, 1, 1, yn=1) for i in range(150)]
    e = S.s2_family(rows, n_boot=200)["per_cell"]["patch"]
    assert e["reading"] == "inconclusive" and not e["repair_helps_claim"] and "no claim that repair helps" in e["note_v"] and "not shown to be better or worse" in e["sentence"]


def test_s2_splice_cell_uses_the_splice_key_and_holm_covers_both_cells():
    rows = _table(35, 3, n_conc=100, cond="patch")
    sp = _table(14, 6, n_conc=130, cond="splice128")
    for r, s_ in zip(rows, sp + [None] * len(rows)):
        if s_ is not None:
            r["conds"]["splice128"] = s_["conds"]["splice128"]
    out = S.s2_family(rows, n_boot=200)
    p1, p2 = out["per_cell"]["patch"], out["per_cell"]["splice"]
    assert p2["key"] == "splice128" and p2["label"] == "S2-splice" and p1["label"] == "S2-patch"
    assert np.allclose([p1["p_holm"], p2["p_holm"]], stats.holm([p1["p"], p2["p"]]))


def test_s2_prefix_rule_and_selftest_and_seed_streams():
    rows = _table(10, 1, n_conc=10)
    planned = [dict(idx=i) for i in range(30)]
    ok = S.s2_family(rows, planned, n_boot=100)["completeness"]
    assert ok["prefix_ok"] and ok["completed_n"] == 21 and ok["below_80_percent"]
    gap = S.s2_family(rows[:5] + rows[6:], planned, n_boot=100)["completeness"]
    assert not gap["prefix_ok"]
    assert S.selftest()["all_ok"]
    assert not np.array_equal(seeds.seed_for("s2_family").generate_state(2), seeds.seed_for("s2_descriptive").generate_state(2))


def test_analysis_main_waits_for_the_planned_fold_and_writes_analysis_json(s2env):
    env, sc, items = s2env
    kw = dict(run_id="P2-GATE-S2", cfg=dict(run_gate_s2.CONFIG, n_items=4), load=lambda: sc, get_items=lambda s, r: items, process=run_gate_s2.process,
              make_ctx=run_gate_s2.make_ctx_factory(_ns(), env), duty=1.0, soft_minutes=30)
    assert runner.run_items(limit=2, **kw) == runner.EXIT_MORE_WORK
    assert S.main(["--n", "4", "--boot", "100"]) == 3                                     # SAP 8.2: no outcome analysis on a partial fold
    assert runner.run_items(**kw) == 0
    assert S.main(["--n", "4", "--boot", "100"]) == 0
    res = json.loads((env / "P2-GATE-S2" / "analysis.json").read_text())
    assert res["family"] == "S2" and res["holm_m"] == 2 and res["completeness"]["prefix_ok"] and res["per_cell"]["splice"]["key"] == "splice128" and res["meta"]["root_seed"] == 20261028
