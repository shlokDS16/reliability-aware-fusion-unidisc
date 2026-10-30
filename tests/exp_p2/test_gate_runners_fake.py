"""End-to-end runs of the M1-M5 item functions on the fake network (tiny 4x4 token grid, real layout and vocabulary ranges). CPU only; every path is a temp dir.
Checks structure, determinism, the itemised pass counts of the spec (v2 11.1) and that gate/controls/arms are wired as specified."""
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

from fake_gate import FakeScorer, fake_image                               # noqa: E402
from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import analysis_m4, checks, config, fit_threshold, headroom, pipeline, runner   # noqa: E402
from exp_p2 import run_gate_m1, run_gate_m2, run_gate_m3, run_gate_m4, run_gate_m5                # noqa: E402

WORDS = "red blue green small large old new quiet loud bright dark soft hard warm cold fast slow tall short thin wide".split()


@pytest.fixture
def env(tmp_path, monkeypatch):
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


def _fold(n, offset=0, n_words=6):
    rng = np.random.default_rng(offset + 1)
    items = [dict(idx=i, gid=offset + i, image_id=100 + offset + i, caption=" ".join(rng.choice(WORDS, n_words, replace=False)), n_tok=n_words) for i in range(n)]
    for i, it in enumerate(items):
        j = (i + 1) % n
        it.update(neg_idx=j, neg_image_id=items[j]["image_id"], neg_caption=items[j]["caption"], neg_restricted=True)
    return items


def _sc(**kw):
    return runner.Counting(FakeScorer(grid=4, **kw))


def _run(env, rid, mod, items, sc, make_ctx=None, n=None, **kw):
    return runner.run_items(run_id=rid, cfg=dict(mod.CONFIG, n_items=n or len(items)), load=lambda: sc, get_items=lambda s, r: items, process=mod.process,
                            make_ctx=make_ctx or mod.make_ctx, duty=1.0, soft_minutes=30, **kw)


# ------------------------------------------------------------------------------------------------ M2
def test_m2_item_has_12_passes_and_the_documented_outputs(env):
    items, sc = _fold(3), _sc()
    (env / "P2-GATE-M2x").mkdir()
    ctx = run_gate_m2.make_ctx(sc, env / "P2-GATE-M2x")
    run_gate_m2.process(sc, items[0], ctx)                                    # warms the null caches
    r0 = sc.rows
    row, arrays = run_gate_m2.process(sc, items[1], ctx)
    assert sc.rows - r0 == 12                                                 # B 8 + image direction 2 + text direction 2 (v2 11.1 M2), nulls cached
    assert row["n_rows"] == 12                                                # logged per item, as M4 does (read by analysis_omni.pass_counts: SAP AD.7 "as logged")
    assert set(arrays) == {"codes", "B", "D", "s3", "delta"} and arrays["B"].shape == (16,) and arrays["D"].dtype == np.float32
    assert set(row["img"]) >= {"n", "mean", "z", "d", "y"} and set(row["txt"]) == {"pmi_pos", "pmi_neg", "d", "y"}
    assert (arrays["B"] <= 0).all() and (arrays["s3"] >= 0).all()
    row2, arrays2 = run_gate_m2.process(sc, items[1], ctx)                   # deterministic
    assert row2 == row and all(np.array_equal(arrays[k], arrays2[k]) for k in arrays)


def test_m2_end_to_end_then_threshold_fit_writes_a_valid_file(env):
    items = _fold(24)
    rc = _run(env, "P2-GATE-M2", run_gate_m2, items, _sc())
    assert rc == 0 and len(common.read_jsonl(env / "P2-GATE-M2" / "items.jsonl")) == 24
    assert (env / "P2-GATE-M2" / "l10.json").exists() and (env / "P2-GATE-DCACHE" / "DI_n006.npy").exists()
    assert fit_threshold.main(["--run-id", "P2-GATE-M2", "--min-items", "24"]) == 0
    t = json.loads((env / "P2-GATE-M2" / "threshold.json").read_text())
    assert set(t["thresholds"]) == {"0.05", "0.01", "0.1"} and t["n_cal"] == 24 and t["statistic"] == "q"
    assert t["thresholds"]["0.01"]["tau"] == "inf" and not t["thresholds"]["0.01"]["feasible"]          # 1/25 > 0.01
    assert t["thresholds"]["0.05"]["feasible"] is True and isinstance(t["thresholds"]["0.05"]["tau"], float)  # 1/25 = 0.04 <= 0.05
    assert (env / "P2-GATE-M2" / "codefreq.npy").exists()
    assert fit_threshold.main(["--run-id", "P2-GATE-M2"]) == 2                                              # fewer than the fixed 300: refuses


# ------------------------------------------------------------------------------------------------ M3
def test_m3_rungs_clean_and_the_headroom_decision_runs_on_its_rows(env):
    items = _fold(5, offset=1000)
    sc = _sc()
    assert _run(env, "P2-GATE-M3", run_gate_m3, items, sc, make_ctx=lambda s, run: SimpleNamespace(run=run, fold=items)) == 0
    rows = common.read_jsonl(env / "P2-GATE-M3" / "items.jsonl")
    assert len(rows) == 5
    assert set(rows[0]["rungs"]) == {"jpeg10", "jpeg5", "noise0.1", "noise0.2", "splice128", "splice192"}
    r = rows[0]["rungs"]["splice192"]
    assert set(r) >= {"corruption", "severity", "n_changed", "none", "chg"} and r["chg"]["n"] == 16 - r["n_changed"] and r["none"]["n"] == 16
    assert rows[0]["clean"]["n"] == 16
    assert not any("gate" in k for k in rows[0])                              # blind to the method: no gate flags in M3
    res = headroom.decide(rows)
    assert set(res) >= {"family", "excluded", "rungs", "n_rule", "endpoint"} and len(res["family"]) + len(res["excluded"]) == 3
    # per item: 2 caption-only passes (+ nothing else): measured on a warm call
    ctx = SimpleNamespace(run=env, fold=items)
    r0 = sc.rows
    run_gate_m3.process(sc, items[2], ctx)
    assert sc.rows - r0 == 2


def test_m3_splice_donor_is_another_fold_item(env):
    items = _fold(4, offset=1000)
    ctx = SimpleNamespace(run=env, fold=items)
    sc = FakeScorer(grid=4)
    d = run_gate_m3.donor_for(ctx, sc, items[1])
    own = sc.preprocess(fake_image(items[1]["image_id"], 96))
    assert not np.array_equal(np.asarray(d), np.asarray(own))
    assert np.array_equal(np.asarray(d), np.asarray(run_gate_m3.donor_for(ctx, sc, items[1])))


# ------------------------------------------------------------------------------------------------ M4
def _write_folds(env, **folds):
    d = env / "P2-GATE-FOLDS"
    d.mkdir(exist_ok=True)
    (d / "folds.json").write_text(json.dumps(folds))


def _m4_prereqs(env, sc, family):
    """Thresholds fitted on 30 fake clean items (real gate scores), family.json written as M3's decision would."""
    dc = pipeline.dcache_for()
    U = []
    for it in _fold(30, offset=0):
        pil, codes = pipeline.prep_image(sc, it["image_id"])
        gs = pipeline.gate_scores(sc, sc.caption_ids(it["caption"]), codes, pipeline.item_groups(sc, it["gid"]), dc)
        U.append(gs["u"])
    res = fit_threshold.fit_from_arrays(U, list(range(30)), "q")
    (env / "P2-GATE-M2").mkdir(exist_ok=True)
    (env / "P2-GATE-M2" / "threshold.json").write_text(json.dumps(res))
    (env / "P2-GATE-M1").mkdir(exist_ok=True)
    (env / "P2-GATE-M1" / "detection_frozen.json").write_text(json.dumps(dict(frozen={})))
    (env / "P2-GATE-M3").mkdir(exist_ok=True)
    (env / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="d", n_rule=dict(rule="R1", test_fold=300), family=[dict(corruption=c, severity=s, key=f"{c}{s}") for c, s in family])))
    return res


def test_m4_item_has_75_passes_and_all_arms(env):
    sc = _sc()
    fam = [("jpeg", 10), ("noise", 0.1), ("splice", 128)]
    _m4_prereqs(env, sc, fam)
    items = _fold(4, offset=2000)
    _write_folds(env, test=items)
    a = SimpleNamespace(tbv="on", denoise_for="jpeg,noise")
    (env / "P2-GATE-M4").mkdir()
    ctx = run_gate_m4.make_ctx_factory(a, env)(sc, env / "P2-GATE-M4")
    assert ctx.fold == items
    assert ctx.family == fam and ctx.tbv and set(ctx.thr) == {0.05, 0.01, 0.1}
    run_gate_m4.process(sc, items[0], ctx)                                   # warm caches
    row, arrays = run_gate_m4.process(sc, items[1], ctx)
    assert row["n_rows"] == 75                                               # 40 B + 5 TbV + 2 image direction + 24 + 4 text direction (v2 11.1 M4)
    assert list(row["conds"]) == ["clean", "jpeg10", "jpeg10_dn", "noise0.1", "noise0.1_dn", "splice128", "patch"]
    clean, jp = row["conds"]["clean"], row["conds"]["jpeg10"]
    assert set(clean["img"]) >= {"none", "gate0.05", "gate0.01", "gate0.1", "geo0", "geo1", "geo2", "scat0", "scat1", "scat2", "topkB", "topks3"} and "chg" not in clean["img"]
    assert set(jp["img"]) >= set(clean["img"]) | {"chg"}
    assert set(clean["txt"]) == {"none", "gate"} and set(jp["txt"]) == {"none", "gate", "geo0", "chg"}
    assert set(row["conds"]["jpeg10_dn"]["img"]) == {"denoised"} and row["conds"]["patch"]["txt"] == {}
    assert clean["n_changed"] == 0 and row["conds"]["patch"]["n_changed"] > 0
    # arms are sized as specified
    for name in ("clean", "jpeg10", "noise0.1", "splice128", "patch"):
        n_g = row["conds"][name]["gate"]["0.05"]["n_flag"]
        for arm in ("geo0", "geo1", "geo2", "scat0", "scat1", "scat2", "topkB", "topks3"):
            assert row["conds"][name]["img"][arm]["n"] == 16 - n_g          # equal size to GATE-M's gate
        assert row["conds"][name]["img"]["gate0.05"]["n"] == 16 - n_g and row["conds"][name]["img"]["none"]["n"] == 16
    assert row["conds"]["jpeg10"]["img"]["chg"]["n"] == 16 - jp["n_changed"]
    # saved arrays: flags, labels, deltas per condition; flags nested across alpha
    assert np.array_equal(arrays["patch_z"], arrays["patch_codes"] != arrays["clean_codes"])
    assert not arrays["clean_z"].any()
    assert (arrays["clean_flag0.01"] <= arrays["clean_flag0.05"]).all() and (arrays["clean_flag0.05"] <= arrays["clean_flag0.1"]).all()
    row2, _ = run_gate_m4.process(sc, items[1], ctx)
    assert {k: v for k, v in row2.items() if k != "n_rows"} == {k: v for k, v in row.items() if k != "n_rows"}      # deterministic
    # TbV off: 70 passes
    ctx.tbv = False
    r0 = sc.rows
    run_gate_m4.process(sc, items[1], ctx)
    assert sc.rows - r0 == 70


def test_m4_requires_its_prerequisites(env):
    with pytest.raises(FileNotFoundError, match="fit_threshold"):
        run_gate_m4.load_prereqs(env)
    (env / "P2-GATE-M2").mkdir()
    (env / "P2-GATE-M2" / "threshold.json").write_text("{}")
    with pytest.raises(FileNotFoundError, match="headroom"):
        run_gate_m4.load_prereqs(env)
    (env / "P2-GATE-M3").mkdir()
    (env / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="z", family=[])))
    with pytest.raises(ValueError, match="endpoint"):                       # a family.json without endpoint d is invalid for the SAP (Addendum 1)
        run_gate_m4.load_prereqs(env)


def test_analysis_m4_main_refuses_a_family_json_without_endpoint_d(env):
    (env / "P2-GATE-M3").mkdir()
    (env / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="z", family=[])))
    assert analysis_m4.main(["--run-id", "P2-GATE-M4"]) == 2


def test_m4_n_must_match_the_committed_n_rule_and_frozen_file_is_required(env, monkeypatch):
    (env / "P2-GATE-M3").mkdir()
    fj = env / "P2-GATE-M3" / "family.json"
    fj.write_text(json.dumps(dict(endpoint="d", family=[], n_rule=dict(rule="R2", test_fold=500))))
    assert run_gate_m4.check_n_against_rule(500, env) == 500
    with pytest.raises(ValueError, match="--n 500"):
        run_gate_m4.check_n_against_rule(None, env)                                # forgetting --n under R2 would run a 300-item fold
    with pytest.raises(ValueError):
        run_gate_m4.check_n_against_rule(300, env)
    fj.write_text(json.dumps(dict(endpoint="d", family=[], n_rule=dict(rule="R3", test_fold=300))))
    assert run_gate_m4.check_n_against_rule(None, env) == 300
    fj.write_text(json.dumps(dict(endpoint="d", family=[], n_rule=dict(rule="NO-GO", test_fold=300))))
    assert run_gate_m4.check_n_against_rule(300, env) == 300
    with pytest.raises(FileNotFoundError, match="detection_frozen"):
        pipeline.require_frozen(env)
    (env / "P2-GATE-M1").mkdir()
    (env / "P2-GATE-M1" / "detection_frozen.json").write_text("{}")
    assert pipeline.require_frozen(env).name == "detection_frozen.json"


def test_m3_and_m4_mains_refuse_before_touching_any_model(env, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("must not load a model or start the loop")
    monkeypatch.setattr(runner, "run_items", boom)
    assert run_gate_m3.main([]) == 2                                           # no detection_frozen.json
    assert run_gate_m4.main([]) == 2                                           # no threshold / family / frozen
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    (env / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="d", n_rule=dict(rule="R2", test_fold=500), family=[dict(corruption="jpeg", severity=10, key="jpeg10")])))
    assert run_gate_m4.main([]) == 2                                           # --n 300 (default) does not match R2
    (env / "P2-GATE-M1" / "detection_frozen.json").unlink()
    assert run_gate_m3.main([]) == 2


def _tok_folds(n=30):
    return dict(cal=_fold(n), head=_fold(n, 1000), test=_fold(n, 2000), test_ext=[])


def test_out_of_range_captions_are_excluded_counted_and_not_replaced(env):
    sc = _sc()
    f = _tok_folds(30)
    rep = pipeline.check_fold_tokens(sc, f, env / "chk")
    assert rep["n_excluded_total"] == 0 and not rep["defect"] and json.loads((env / "chk" / "token_exclusions.json").read_text())["n_excluded_total"] == 0
    f["cal"][4]["caption"] = "one two"                                          # runtime count 2 < 5 (frozen count 6)
    f["test"][7]["caption"] = " ".join(["w"] * 40)                              # runtime count 40 > 32
    rep = pipeline.check_fold_tokens(sc, f, env / "chk")
    assert rep["excluded"] == {"cal": [4], "head": [], "test": [7], "test_ext": []} and rep["n_excluded_total"] == 2 and not rep["defect"]
    kept = pipeline.drop_excluded(f["cal"], rep, "cal")
    assert [it["idx"] for it in kept] == [i for i in range(30) if i != 4]        # not replaced, order unchanged
    assert len(pipeline.drop_excluded(f["test"], rep, "test")) == 29 and len(pipeline.drop_excluded(f["head"], rep, "head")) == 30
    on_disk = json.loads((env / "chk" / "token_exclusions.json").read_text())
    assert on_disk["excluded"]["cal"] == [4] and json.loads((env / "chk" / "folds_check.json").read_text())["per_fold"]["cal"]["fraction_excluded"] == pytest.approx(1 / 30)


def test_a_count_that_differs_but_stays_in_range_is_reported_not_excluded_and_over_10_percent_is_a_defect(env):
    sc = _sc()
    f = _tok_folds(30)
    f["cal"][1]["n_tok"] = 7                                                    # frozen 7, runtime 6: both inside 5-32
    rep = pipeline.check_fold_tokens(sc, f, env / "chk")
    assert rep["per_fold"]["cal"]["n_mismatch_in_range"] == 1 and rep["excluded"]["cal"] == []
    for i in range(4):                                                          # 4 of 30 = 13 percent excluded: a fold-construction defect
        f["head"][i]["caption"] = "a b"
    with pytest.raises(pipeline.FoldDefect, match="stop and report"):
        pipeline.check_fold_tokens(sc, f, env / "chk")
    assert json.loads((env / "chk" / "folds_check.json").read_text())["defect_folds"] == ["head"]      # the report is on disk before the stop
    g = _tok_folds(30)
    for i in range(3):                                                          # 3 of 30 = exactly 10 percent: allowed
        g["cal"][i]["caption"] = "a b"
    assert pipeline.check_fold_tokens(sc, g, env / "chk2")["n_excluded_total"] == 3


def test_effective_n_after_exclusions_lets_the_run_and_the_driver_finish(env, monkeypatch):
    items = _fold(30)
    kept = [it for it in items if it["idx"] != 4]
    sc = _sc()
    rc = runner.run_items(run_id="P2-GATE-EX", cfg=dict(n_items=30), load=lambda: sc, get_items=lambda s, r: kept, process=lambda s, it, c: (dict(v=1), {}), duty=1.0, soft_minutes=30)
    assert rc == 0 and len(common.read_jsonl(env / "P2-GATE-EX" / "items.jsonl")) == 29
    e = json.loads((env / "P2-GATE-EX" / "effective_n.json").read_text())
    assert (e["planned"], e["effective"]) == (30, 29)
    called = []
    rc = runner.run_items(run_id="P2-GATE-EX", cfg=dict(n_items=30), load=lambda: called.append(1), get_items=lambda s, r: kept, process=None, duty=1.0, soft_minutes=30)
    assert rc == 0 and called == []                                              # complete at 29: returns before loading the model
    from exp_p2.gate import gate_driver
    monkeypatch.setattr(gate_driver.driver, "gates_ok", lambda: (True, "ok"))
    monkeypatch.setattr(gate_driver, "EVENTS_FN", lambda since: dict(ok=True, events=[], error=None))
    monkeypatch.setattr(gate_driver, "AC_FN", lambda: True)
    monkeypatch.setattr(gate_driver, "PIN_FN", lambda: dict(ok=True))
    monkeypatch.setattr(gate_driver.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not launch: already complete")))
    (env / "P2-GATE-M2").mkdir()
    (env / "P2-GATE-M2" / "effective_n.json").write_text(json.dumps(dict(planned=30, effective=2)))
    (env / "P2-GATE-M2" / "items.jsonl").write_text(json.dumps(dict(idx=0)) + "\n" + json.dumps(dict(idx=1)) + "\n")
    assert gate_driver.main(["--stage", "m2", "--n", "30"]) == 0


def test_completeness_report_counts_the_exclusions_and_fit_threshold_uses_the_effective_n(env):
    from exp_p2.gate import analysis_m4 as A
    rows = [dict(idx=i, n_tok=6, conds={"jpeg10": dict(img={"none": dict(d=0.1, n=64, y=1), "gate0.05": dict(d=0.1, n=60, y=1)})}) for i in range(10) if i != 3]
    comp = A.completeness_report(rows, [dict(idx=i, n_tok=6) for i in range(10)], ["jpeg10"], excluded_idx=[3])
    assert comp["planned_n"] == 9 and comp["n_excluded_token_rule"] == 1 and comp["excluded_idx"] == [3] and comp["planned_before_exclusion"] == 10
    assert comp["completed_n"] == 9 and comp["n_missing"] == 0 and comp["prefix_ok"]
    from exp_p2.gate import fit_threshold
    m2 = env / "P2-GATE-M2x"
    (m2 / "arrays").mkdir(parents=True)
    rng = np.random.default_rng(0)
    for i in range(20):
        np.savez(m2 / "arrays" / f"item{i:04d}.npz", B=rng.normal(-3, 1, 8).astype(np.float32), D=rng.normal(-2, .2, 8).astype(np.float32), codes=rng.integers(0, 50, 8))
    (m2 / "items.jsonl").write_text("\n".join(json.dumps(dict(idx=i, gid=i)) for i in range(20)) + "\n")
    (m2 / "effective_n.json").write_text(json.dumps(dict(planned=300, effective=20)))
    assert fit_threshold.main(["--run-id", "P2-GATE-M2x"]) == 0                  # 20 items, not the fixed 300, because the effective n is 20


def test_m4_tbv_auto_follows_the_m1_verdict(env):
    assert run_gate_m4.tbv_enabled("on", env) and not run_gate_m4.tbv_enabled("off", env)
    assert not run_gate_m4.tbv_enabled("auto", env)                          # no verdict yet: off
    (env / "P2-GATE-M1").mkdir()
    (env / "P2-GATE-M1" / "tbv_verdict.json").write_text(json.dumps(dict(copy_suspected=True)))
    assert not run_gate_m4.tbv_enabled("auto", env)
    (env / "P2-GATE-M1" / "tbv_verdict.json").write_text(json.dumps(dict(copy_suspected=False)))
    assert run_gate_m4.tbv_enabled("auto", env)


def test_m4_end_to_end_and_analysis_smoke(env):
    sc = _sc()
    fam = [("jpeg", 10), ("splice", 128)]
    _m4_prereqs(env, sc, fam)
    items = _fold(6, offset=2000)
    _write_folds(env, test=items)
    a = SimpleNamespace(tbv="off", denoise_for="jpeg")
    rc = runner.run_items(run_id="P2-GATE-M4", cfg=dict(run_gate_m4.CONFIG, n_items=6), load=lambda: sc, get_items=lambda s, r: items, process=run_gate_m4.process,
                          make_ctx=run_gate_m4.make_ctx_factory(a, env), duty=1.0, soft_minutes=30)
    assert rc == 0
    frozen = {"jpeg": dict(available=True, rival="plainB", base="plainB", sign=1), "noise": dict(available=True, rival="tex_neg", base="tex", sign=-1)}
    fam = [dict(corruption="jpeg", severity=10, key="jpeg10"), dict(corruption="splice", severity=128, key="splice128")]
    res = analysis_m4.run(env / "P2-GATE-M4", fam, n_boot=200, frozen=frozen)
    assert res["n_items"] == 6 and res["endpoint"] == "d"
    pp = res["primary"]["per_corruption"]
    assert set(pp) == {"jpeg", "noise", "splice"} and res["primary"]["holm_m"] == 3             # SAP 2.4: m = 3 always
    assert pp["noise"]["tested"] is False and pp["noise"]["p"] == 1.0 and pp["noise"]["p_holm"] == 1.0 and pp["jpeg"]["label"] == "P1"
    for k in ("jpeg", "splice"):
        assert {"b", "c", "p", "p_holm"} <= set(pp[k])
    for k in ("jpeg10", "splice128"):
        assert set(res["mechanism"][k]["y"]) >= {"gate_minus_none", "gate_minus_geo", "gate_minus_changed_code"}
    assert res["s_dn"]["holm_m"] == 2 and set(res["s_dn"]["per_corruption"]) == {"jpeg", "noise"}      # S-DN: m = 2, splice has no denoise arm
    assert res["s_dn"]["per_corruption"]["jpeg"]["tested"] and not res["s_dn"]["per_corruption"]["noise"]["tested"] and res["s_dn"]["per_corruption"]["noise"]["p"] == 1.0
    sz = res["s_z"]
    assert sz["holm_m"] == 3 and sz["endpoint"] == "d" and "z" in sz["per_corruption"]["jpeg"]["sensitivity_other_endpoint"] and not sz["per_corruption"]["noise"]["tested"]
    d2 = res["s_d2"]
    assert d2["holm_m"] == 2 and d2["per_corruption"]["noise"]["tested"] is False and d2["per_corruption"]["noise"]["p"] == 1.0           # no operating point: p = 1, stays in m = 2
    assert d2["per_corruption"]["jpeg"]["rival"] == "plainB" and 0 <= d2["per_corruption"]["jpeg"]["p_holm"] <= 1
    assert analysis_m4.run(env / "P2-GATE-M4", fam, n_boot=50)["s_d2"]["per_corruption"]["jpeg"]["p"] == 1.0    # no frozen file: p = 1
    assert analysis_m4.run(env / "P2-GATE-M4", ["jpeg10", "splice128"], n_boot=50, endpoint="z")["endpoint"] == "z"
    assert set(res["calibration"]["realised_fap_clean"]) == {"0.05", "0.01", "0.1"}
    json.dumps(res, default=float)


# ------------------------------------------------------------------------------------------------ M5 coherence
def test_coherence_is_zero_for_a_context_free_network_and_nonzero_otherwise():
    for intra, expect_zero in ((0.0, True), (1.0, False)):
        sc = FakeScorer(grid=4, intra=intra, cross=0.0)
        st = sc.build([101, 102, 103, 104], np.random.default_rng(0).integers(0, 16384, 16))
        rng = np.random.default_rng(1)
        pairs = checks.coherence_pairs(4, rng, min_sep=2)
        halves = checks.half_masks(16, pairs, rng)
        sc.rows.clear()
        g = checks.coherence_gaps(sc, st, pairs, halves)
        assert len(sc.rows) == 24 and g.shape == (4, 2)                       # 4 pairs x 2 contexts x 3 passes
        assert (np.abs(g).max() < 1e-4) == expect_zero
        g2 = checks.coherence_gaps(sc, st, pairs, halves, bs=3, reverse=True)
        assert np.allclose(g, g2, atol=1e-5)                                  # the fake is batch-composition independent: noise floor ~ 0


def test_coherence_pairs_and_masks():
    rng = np.random.default_rng(0)
    for _ in range(50):
        pairs = checks.coherence_pairs(32, rng, min_sep=8)
        assert [p["kind"] for p in pairs] == ["adjacent_h", "adjacent_v", "far", "far"]
        gy = lambda p: (p["j"] // 32, p["j"] % 32, p["k"] // 32, p["k"] % 32)
        y1, x1, y2, x2 = gy(pairs[0])
        assert y1 == y2 and x2 == x1 + 1
        y1, x1, y2, x2 = gy(pairs[1])
        assert x1 == x2 and y2 == y1 + 1
        for p in pairs[2:]:
            y1, x1, y2, x2 = gy(p)
            assert max(abs(y1 - y2), abs(x1 - x2)) >= 8
        halves = checks.half_masks(1024, pairs, rng)
        for p, h in zip(pairs, halves):
            assert len(h) == 511 and p["j"] not in h and p["k"] not in h and len(set(h)) == 511


def test_m5_item_24_passes_and_noise_floor_every_fourth_item(env):
    items = _fold(4)
    sc = _sc()
    ctx = run_gate_m5.make_ctx(sc, env)
    r0 = sc.rows
    row, arrays = run_gate_m5.process(sc, items[1], ctx)
    assert sc.rows - r0 == 24 and "g0" not in row and arrays["g"].shape == (4, 2)
    r0 = sc.rows
    row, arrays = run_gate_m5.process(sc, items[0], ctx)                      # idx % 4 == 0: repeat
    assert sc.rows - r0 == 48 and np.array(row["g0"]).shape == (4, 2) and np.abs(arrays["g0"]).max() < 1e-4
    s = checks.coherence_summary(np.array([[0.5, -0.4]]), np.array([[0.001, -0.002]]), mu=0.2)
    assert s["coherent_within_noise"] is False and s["incoherent_at_evidence_scale"] is True


# ------------------------------------------------------------------------------------------------ M1 post-hoc
def test_m1_posthoc_reads_probe2_arrays_and_writes_nulls(env):
    sc = _sc()
    p2 = env / "P2-PROBE-02"
    (p2 / "arrays").mkdir(parents=True)
    sel = _fold(3)
    (p2 / "selection.json").write_text(json.dumps(dict(items=[dict(image_id=i["image_id"], caption=i["caption"], n_tok=6) for i in sel])))
    rng = np.random.default_rng(0)
    for i in (0, 2):                                                          # item 1 has no arrays yet (probe 2 still running)
        d = dict(clean=rng.integers(0, 16384, 16))
        for c in run_gate_m1.NAMES[1:]:
            d[f"{c}_codes"] = rng.integers(0, 16384, 16)
        np.savez(p2 / "arrays" / f"item{i:04d}.npz", **d)
    items = run_gate_m1.get_items(sc, env / "x", runs=env)
    assert [it["idx"] for it in items] == [0, 2]
    (env / "P2-GATE-M1").mkdir()
    ctx = run_gate_m1.make_ctx_factory(True, env)(sc, env / "P2-GATE-M1")
    row, arrays = run_gate_m1.process(sc, items[0], ctx)
    assert set(arrays) == {f"{c}_D" for c in run_gate_m1.NAMES} | {f"{c}_tbv" for c in run_gate_m1.NAMES[1:]}
    assert set(row["tbv"]) == set(run_gate_m1.NAMES[1:]) and all("copy_suspected" in v for v in row["tbv"].values())
    assert json.loads((env / "P2-GATE-M1" / "codebook.json").read_text())["available"] is False       # the fake has no VQ model: logged, not crashed
    st = sc.build(sc.caption_ids(items[0]["caption"]), np.load(p2 / "arrays" / "item0000.npz")["clean"])
    ref = np.asarray(pipeline.dcache_for().image_matrix(sc, st, 6))[np.arange(16), np.load(p2 / "arrays" / "item0000.npz")["clean"]]
    assert np.array_equal(arrays["clean_D"], ref.astype(np.float32))


def test_m0_stage1_forward_and_hold(env):
    from exp_p2 import run_gate_m0
    assert run_gate_m0.one_batch(FakeScorer(grid=4)) >= 0
    (env / "P2-PROBE-02").mkdir()
    (env / "P2-PROBE-02" / "HOLD.txt").write_text("hold")
    assert run_gate_m0.main(["--run-id", "P2-M0-STAGE1"]) == 7                   # returns before importing a model or touching CUDA
    assert not (env / "P2-M0-STAGE1").exists()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
