"""Audit fixes F2 to F6 of GATE-CODE-AUDIT-A6-LRF-2026-10-29: the enforced re-score gate (F3), the re-freeze entry point (F2), the cross-fit entry point and the n-rule record from its file (F4), the plan-file writer (F5)
and the re-score run id (F6). F1 (the scorer) is in test_gate_lrf_score.py. Fakes and tiny synthetic arrays only; the re-freeze and cross-fit tests use the real learned-ceiling code with a reduced budget."""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from test_gate_a6_options import _rescore, _source_run                                 # noqa: E402
from test_gate_runners_fake import _sc, env                                            # noqa: E402,F401  (env is a fixture)
from test_gate_lrf_score import _arrays                                                # noqa: E402
from exp_p2 import common, run_gate_lrf_rescore as rescore                              # noqa: E402
from exp_p2.gate import gate_driver, lrf_nrule, lrf_plan, runner                        # noqa: E402

SMALL_R, SMALL_N = 3, 3


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------------ F6
def test_f6_the_rescore_run_id_is_the_saps_everywhere():
    assert rescore.RUN_ID == "P2-LRF-RESCORE" and gate_driver.STAGES["lrf-rescore"][1] == "P2-LRF-RESCORE"
    src = "".join(p.read_text(encoding="utf8") for p in (ROOT / "exp_p2" / "run_gate_lrf_rescore.py", ROOT / "exp_p2" / "gate" / "gate_driver.py", ROOT / "analysis" / "paper2" / "lrf" / "refreeze.py"))
    assert "M4-LFIX" not in src and "DRAFT" not in (ROOT / "exp_p2" / "run_gate_lrf_rescore.py").read_text(encoding="utf8")


# ------------------------------------------------------------------------------------------------ F3
def test_f3_a_failed_invariance_stops_the_stage_and_leaves_no_row_or_arrays(env, monkeypatch):
    sc = _sc()
    _source_run(env, sc, 5)
    monkeypatch.setattr(rescore, "invariance", lambda *a, **k: {"pos_B": 1e-3})
    with pytest.raises(rescore.ChecksFailed, match="invariance"):
        _rescore(env, sc, 6)
    assert not (env / "RS6" / "arrays" / "item0000.npz").exists() and common.read_jsonl(env / "RS6" / "items.jsonl") == []
    ev = [e for e in common.read_jsonl(env / "RS6" / "chunks.jsonl") if e.get("event") == "item_error"]
    assert ev and "ChecksFailed" in ev[0]["error"]
    res = rescore.check_rows(env / "RS6", slot_len=6)
    assert res["ok"] is False and "ChecksFailed event" in res["reason"]


def test_f3_a_failed_positive_control_stops_the_stage(env, monkeypatch):
    sc = _sc()
    _source_run(env, sc, 5)
    monkeypatch.setattr(rescore, "positive_control", lambda *a, **k: 3e-5)               # above the 1e-5 tolerance
    with pytest.raises(rescore.ChecksFailed, match="positive control"):
        _rescore(env, sc, 6)
    assert common.read_jsonl(env / "RS6" / "items.jsonl") == []


def test_f3_the_check_reads_the_committed_rows_and_the_auditor_tolerance_needs_its_row(env, monkeypatch):
    sc = _sc()
    _source_run(env, sc, 5)
    assert _rescore(env, sc, 6) == 0
    ok = rescore.check_rows(env / "RS6", slot_len=6)
    assert ok["ok"] and ok["invariance_max_abs_diff"] == 0.0 and ok["positive_control_max_abs_diff"] == 0.0
    assert not rescore.check_rows(env / "RS6", slot_len=13)["ok"]                          # the run's config says slot 6
    rows = common.read_jsonl(env / "RS6" / "items.jsonl")

    def write(mut):
        (env / "RS6" / "items.jsonl").write_text("".join(json.dumps(mut(dict(r))) + "\n" for r in rows))
    write(lambda r: dict(r, invariance_max_abs_diff=5e-7) if r["idx"] == 2 else r)
    assert not rescore.check_rows(env / "RS6", slot_len=6)["ok"]                           # exact zero is the rule
    assert rescore.check_rows(env / "RS6", inv_tol=rescore.INV_TOL_AUDITOR, slot_len=6)["ok"]    # <= 1e-6 only by the auditor's row
    write(lambda r: dict(r, invariance_max_abs_diff=2e-6) if r["idx"] == 2 else r)
    assert not rescore.check_rows(env / "RS6", inv_tol=rescore.INV_TOL_AUDITOR, slot_len=6)["ok"]    # larger: Study 2 stops
    write(lambda r: dict(r, positive_control_max_abs_diff=2e-5) if r["idx"] == 0 else r)
    assert "positive control" in rescore.check_rows(env / "RS6", inv_tol=rescore.INV_TOL_AUDITOR, slot_len=6)["reason"]
    write(lambda r: {k: v for k, v in r.items() if k != "positive_control"} if r["idx"] == 1 else r)
    assert not rescore.check_rows(env / "RS6", slot_len=6)["ok"]
    write(lambda r: dict(r, invariance_max_abs_diff=float("nan")) if r["idx"] == 1 else r)
    assert not rescore.check_rows(env / "RS6", slot_len=6)["ok"]
    write(lambda r: r)
    monkeypatch.setattr(common, "RUNS", env)
    assert rescore.main(["--check", "--run-id", "RS6", "--slot-len", "6"]) == 0
    write(lambda r: dict(r, invariance_max_abs_diff=1.0) if r["idx"] == 0 else r)
    assert rescore.main(["--check", "--run-id", "RS6", "--slot-len", "6"]) == 1


def test_f3_the_auditor_row_option_sets_the_stage_tolerance(env, monkeypatch):
    from types import SimpleNamespace
    sc = _sc()
    _source_run(env, sc, 5)
    a = SimpleNamespace(source_run="P2-GATE-M4", slot_len=6, conds=",".join(rescore.CONDS), family_run="P2-GATE-M3", auditor_row="AUD-7")
    ctx = rescore.make_ctx_factory(a, env)(sc, env / "x")
    assert ctx.inv_tol == rescore.INV_TOL_AUDITOR
    a.auditor_row = None
    assert rescore.make_ctx_factory(a, env)(sc, env / "x").inv_tol == 0.0
    assert rescore.build_cfg(a, env, 3)["auditor_row"] is None


def _git(repo, *args):
    import subprocess
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _committed_object(repo: Path, commit=True):
    """A throw-away git repository holding a (fake) re-frozen object runs/P2-LRF-FROZEN-LFIX/{model.npz, spec.json}."""
    repo.mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.org")
    _git(repo, "config", "user.name", "t")
    _git(repo, "config", "core.autocrlf", "false")
    obj = repo / "runs" / "P2-LRF-FROZEN-LFIX"
    obj.mkdir(parents=True)
    (obj / "model.npz").write_bytes(b"model bytes")
    (obj / "spec.json").write_bytes(b'{"caption_slot_len": 13}\n')
    (repo / "README").write_text("x")
    _git(repo, "add", "-A")
    if commit:
        _git(repo, "commit", "-q", "-m", "object")
    return repo, obj


# ------------------------------------------------------------------------------------------------ F2 and F4: synthetic re-scored run
def _fake_rescore_run(tmp, n, slot=13, inv=0.0, pc=0.0, seed=0):
    run = tmp / "runs" / "P2-LRF-RESCORE"
    (run / "arrays").mkdir(parents=True)
    (run / "config.json").write_text(json.dumps(dict(slot_len=slot, codebook_sha256="a", dcache_di_sha256="b")))
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        d = _arrays(rng, conds=rescore.CONDS)
        for c in rescore.CONDS:
            d[f"{c}_z"] = rng.random(1024) < 0.1
            d[f"{c}_delta"] = (rng.normal(0.1, 1.5, 1024) + 0.8 * d[f"{c}_z"] * np.sign(d[f"{c}_B"] - d[f"{c}_D"])).astype(np.float32)
        np.savez(run / "arrays" / f"item{i:04d}.npz", **d)
        r = dict(idx=i, gid=i, image_id=i)
        if i < 5:
            r.update(invariance={c: {"pos_B": inv} for c in rescore.CONDS}, invariance_max_abs_diff=inv, positive_control={c: pc for c in rescore.CONDS}, positive_control_max_abs_diff=pc)
        rows.append(r)
    (run / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return run


@pytest.fixture(scope="module")
def mods():
    rf = _load("a6_refreeze_t", "analysis/paper2/lrf/refreeze.py")
    cf = _load("a6_crossfit_t", "analysis/paper2/lrf/crossfit.py")
    return rf, cf


def test_f2_refreeze_refuses_without_the_gate_and_never_overwrites(tmp_path, mods):
    rf, _ = mods
    run = _fake_rescore_run(tmp_path, 6, inv=1e-3)
    with pytest.raises(rf.RefreezeRefused, match="gate"):
        rf.refreeze(run, tmp_path / "out", n_items=6, rmax=SMALL_R, n_cfg=SMALL_N)
    assert not (tmp_path / "out").exists()
    run2 = _fake_rescore_run(tmp_path / "b", 6)
    (tmp_path / "out2").mkdir()
    with pytest.raises(rf.RefreezeRefused, match="exists"):
        rf.refreeze(run2, tmp_path / "out2", n_items=6)
    retired = tmp_path / "runs" / "P2-LRF-FROZEN"
    retired.mkdir(parents=True)
    with pytest.raises(rf.RefreezeRefused, match="new directory"):
        rf.refreeze(run2, retired, retired=retired, n_items=6)
    with pytest.raises(rf.RefreezeRefused, match="new directory"):
        rf.refreeze(run2, run2 / "sub", retired=retired, n_items=6)                       # inside the source run
    with pytest.raises(rf.RefreezeRefused, match="incomplete"):
        rf.refreeze(run2, tmp_path / "out3", retired=retired, n_items=7)                  # item 6 was never re-scored
    assert rf.main(["--src", str(run), "--out", str(tmp_path / "out4")]) == 2 and not (tmp_path / "out4").exists()


def test_f2_refreeze_produces_the_model_of_the_unchanged_freeze_on_its_own_arrays(tmp_path, mods, monkeypatch):
    rf, _ = mods
    from analysis_posthoc.learned_ceiling import families as fam, lrf, run as lrun
    n = 10
    src = _fake_rescore_run(tmp_path, n)
    out = tmp_path / "newdir"
    spec = rf.refreeze(src, out, retired=tmp_path / "runs" / "P2-LRF-FROZEN", n_items=n, rmax=SMALL_R, n_cfg=SMALL_N, log=lambda m: None)
    # the unchanged lrf.freeze with the paths swapped and the same reduced budget
    orig = fam.F1GAM
    ref_dir = tmp_path / "ref"
    monkeypatch.setattr(lrun, "ARR", src / "arrays")
    monkeypatch.setattr(lrun, "N_ITEMS", n)
    monkeypatch.setattr(lrf, "FROZEN", ref_dir)
    monkeypatch.setattr(fam, "F1GAM", lambda name, r, k: orig(name, SMALL_R, SMALL_N))
    lrf.freeze()
    a, b = np.load(out / "model.npz"), np.load(ref_dir / "model.npz")
    assert list(a["feature_names"]) == list(b["feature_names"])
    for k in ("a", "b", "c", "knots", "mu", "sd"):
        assert np.allclose(a[k], b[k], atol=1e-6, rtol=1e-5), k
    ref_spec = json.loads((ref_dir / "spec.json").read_text())
    assert spec["selected_cfg"] == ref_spec["selected_cfg"] and spec["seed"] == ref_spec["seed"] and spec["T"] == pytest.approx(ref_spec["T"]) and spec["inner_cv_o1"] == pytest.approx(ref_spec["inner_cv_o1"])
    assert spec["hpo"]["seed_keys"] == ref_spec["hpo"]["seed_keys"] and spec["training_conditions"] == ref_spec["training_conditions"]


def test_f2_refreeze_writes_no_accuracy_and_records_what_it_must(tmp_path, mods, capsys):
    rf, _ = mods
    src = _fake_rescore_run(tmp_path, 8)
    out = tmp_path / "frozen"
    spec = rf.refreeze(src, out, retired=tmp_path / "runs" / "P2-LRF-FROZEN", n_items=8, rmax=SMALL_R, n_cfg=SMALL_N)
    printed = capsys.readouterr().out
    assert sorted(p.name for p in out.iterdir()) == ["hpo.json", "model.npz", "selfcheck.json", "spec.json"]       # no freeze_check.json, no insample_weights.npz
    blob = (out / "spec.json").read_text() + (out / "hpo.json").read_text() + (out / "selfcheck.json").read_text() + printed

    def keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k)
                yield from keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from keys(v)
    all_keys = set(keys(json.loads((out / "spec.json").read_text()))) | set(keys(json.loads((out / "hpo.json").read_text()))) | set(keys(json.loads((out / "selfcheck.json").read_text())))
    assert not any("acc" in k.lower() for k in all_keys) and "insample" not in blob and "none_accuracy" not in blob and "decision_count" not in blob
    sc = json.loads((out / "selfcheck.json").read_text())
    assert sc["selfcheck_max_abs_diff_numpy_vs_torch"] < 1e-5
    assert spec["caption_slot_len"] == 13 and spec["source_run"] == "P2-LRF-RESCORE" and spec["rescore_checks"]["ok"] and len(spec["rescored_arrays_digest"]) == 64
    assert set(spec["code_sha256"]) == {"data.py", "families.py", "lrf.py", "run.py"} and spec["model_sha256"] == rf.sha256_file(out / "model.npz")
    assert json.loads(printed.strip().splitlines()[-1])["model_sha256"] == spec["model_sha256"]
    assert not (tmp_path / "runs" / "P2-LRF-FROZEN").exists()                                           # the retired directory was never created or written


def test_f2_the_refrozen_object_loads_in_the_scorer_with_a_pins_file(tmp_path, mods):
    rf, _ = mods
    from exp_p2.gate import lrf_score as ls
    src = _fake_rescore_run(tmp_path, 8)
    out = tmp_path / "frozen"
    rf.refreeze(src, out, retired=tmp_path / "runs" / "P2-LRF-FROZEN", n_items=8, rmax=SMALL_R, n_cfg=SMALL_N)
    code_dir = ROOT / "analysis_posthoc" / "learned_ceiling"
    spec = json.loads((out / "spec.json").read_text())
    fz = ls.load_frozen(out, code_dir, pins=dict(model_sha256=spec["model_sha256"], spec_sha256=ls.sha256_file(out / "spec.json")))
    assert fz["hashes"]["pinned_externally"] is True and fz["spec"]["caption_slot_len"] == 13
    d = dict(np.load(src / "arrays" / "item0001.npz"))
    assert ls.weights(fz, d, "noise0.1").shape == (1024,)


# ------------------------------------------------------------------------------------------------ F4
def test_f4_outer_folds_are_the_learned_ceiling_folds(mods):
    _, cf = mods
    from analysis_posthoc.learned_ceiling import run as lrun
    a, b = cf.folds(500), lrun.outer_folds()
    assert len(a) == 5 and all(np.array_equal(x, y) for x, y in zip(a, b))
    assert sorted(np.concatenate(cf.folds(10)).tolist()) == list(range(10))


def test_f4_crossfit_writes_the_noise_result_the_n_rule_reads(tmp_path, mods):
    rf, cf = mods
    from analysis_posthoc.learned_ceiling import run as lrun
    n = 10
    src = _fake_rescore_run(tmp_path, n, seed=3)
    out = tmp_path / "cf"
    repo, obj = _committed_object(tmp_path / "gitrepo")
    old_out = lrun.OUT
    res = cf.crossfit(src, out, n_items=n, rmax=SMALL_R, n_cfg=SMALL_N, log=lambda m: None, frozen_dir=obj, repo=repo)
    assert lrun.OUT == old_out and lrun.N_ITEMS == 500                                           # the learned-ceiling module's globals are restored; runs/P2-POSTHOC-LEARNED untouched
    assert (out / "results.json").exists() and len(list((out / "ckpt").glob("F1_fold*.npz"))) == 5
    r = json.loads((out / "results.json").read_text())
    assert r["condition"] == "noise0.1" and r["n"] == n and r["b"] + r["c"] <= n and r["delta_cf"] == pytest.approx((r["b"] - r["c"]) / n) and r["pi_cf"] == pytest.approx((r["b"] + r["c"]) / n)
    assert r["inputs"]["refrozen_object_commit"] == _git(repo, "rev-parse", "HEAD") and r["inputs"]["refrozen_object"] == "P2-LRF-FROZEN-LFIX"        # the commit of the object is recorded
    assert set(r["inputs"]) >= {"rescored_arrays_digest", "rescore_config_sha256", "code_sha256", "crossfit_py_sha256", "source_run"} and r["protocol"]["family"] == "F1"
    assert set(r) >= {"label"} and not any(k.startswith("acc") for k in r)                       # noise0.1 only: no other condition is looked at
    # recompute b and c from the checkpoints
    y = np.zeros(n, bool)
    for k in range(5):
        ck = np.load(out / "ckpt" / f"F1_fold{k}.npz")
        y[ck["test"]] = ck["y"][:, 2]
    none = np.stack([np.load(src / "arrays" / f"item{i:04d}.npz")["noise0.1_delta"].mean() > 0 for i in range(n)])
    assert (int((y & ~none).sum()), int((~y & none).sum())) == (r["b"], r["c"])
    with pytest.raises(cf.rf.RefreezeRefused, match="exists"):       # cf imports refreeze as a package module, a different class object than this file's rf
        cf.crossfit(src, out, n_items=n, rmax=SMALL_R, n_cfg=SMALL_N, frozen_dir=obj, repo=repo)
    bad = _fake_rescore_run(tmp_path / "bad", n, pc=1e-3)
    with pytest.raises(cf.rf.RefreezeRefused, match="gate"):
        cf.crossfit(bad, tmp_path / "cf2", n_items=n, rmax=SMALL_R, n_cfg=SMALL_N, frozen_dir=obj, repo=repo)
    assert not (tmp_path / "cf2" / "results.json").exists()
    # the n-rule reads that file and records its hash; hand-typed numbers cannot make a record
    rec_path = tmp_path / "n_rule.json"
    assert lrf_nrule.main(["--cf-results", str(out / "results.json"), "--out", str(rec_path)]) == 0
    rec = json.loads(rec_path.read_text())
    assert rec["cf_results_sha256"] == rf.sha256_file(out / "results.json") and rec["delta_cf"] == r["delta_cf"] and rec["pi_cf"] == r["pi_cf"] and 400 <= rec["n_L"] <= 533


def test_f4_the_n_rule_record_comes_only_from_the_results_file(tmp_path, capsys):
    assert lrf_nrule.main(["--delta-cf", "0.1", "--pi-cf", "0.24", "--out", str(tmp_path / "a.json")]) == 2 and not (tmp_path / "a.json").exists()      # hand-typed + record: refused
    assert lrf_nrule.main(["--delta-cf", "0.1", "--pi-cf", "0.24"]) == 0                                                                       # exploration still prints
    capsys.readouterr()
    good = dict(condition="noise0.1", n=500, b=85, c=34, delta_cf=51 / 500, pi_cf=119 / 500)
    p = tmp_path / "r.json"
    p.write_text(json.dumps(good))
    rec = lrf_nrule.from_cf_results(p)
    assert rec["n_L"] == 533 and rec["cf_b"] == 85 and len(rec["cf_results_sha256"]) == 64
    for bad in (dict(good, condition="clean"), dict(good, delta_cf=0.5), {k: v for k, v in good.items() if k != "pi_cf"}):
        p.write_text(json.dumps(bad))
        with pytest.raises(ValueError):
            lrf_nrule.from_cf_results(p)
        assert lrf_nrule.main(["--cf-results", str(p), "--out", str(tmp_path / "b.json")]) == 2
    assert lrf_nrule.main(["--not-committed", "--out", str(tmp_path / "fallback.json")]) == 0 and json.loads((tmp_path / "fallback.json").read_text())["n_L"] == 520


# ------------------------------------------------------------------------------------------------ F5
def _m3(tmp_path, fam=(("jpeg", 10), ("noise", 0.1), ("splice", 128)), endpoint="d"):
    p = tmp_path / "runs" / "P2-GATE-M3" / "family.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dict(endpoint=endpoint, n_rule=dict(rule="R1", test_fold=300), family=[dict(corruption=c, severity=s, key=f"{c}{s}") for c, s in fam])))
    return p


def _nrec(tmp_path, n_l):
    p = tmp_path / "runs" / "P2-LRF-PLAN" / "n_rule.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dict(n_L=n_l)))
    return p


def test_f5_plan_files_content(tmp_path):
    l1, lg = lrf_plan.plan_files(_nrec(tmp_path, 466), _m3(tmp_path))
    assert l1["endpoint"] == "d" and l1["n_rule"]["test_fold"] == 466 and [(f["corruption"], f["severity"]) for f in l1["family"]] == lrf_plan.P_OPERATING_POINTS
    assert lg["endpoint"] == "d" and lg["family"] == [] and lg["n_rule"]["test_fold"] == 300 and len(l1["sources"]["m3_family_sha256"]) == 64
    for bad_fam in ((("jpeg", 10), ("noise", 0.1)), (("noise", 0.1), ("jpeg", 10), ("splice", 128)), (("jpeg", 5), ("noise", 0.1), ("splice", 128))):
        with pytest.raises(ValueError, match="operating points"):
            lrf_plan.plan_files(_nrec(tmp_path, 466), _m3(tmp_path, bad_fam))
    with pytest.raises(ValueError, match="endpoint"):
        lrf_plan.plan_files(_nrec(tmp_path, 466), _m3(tmp_path, endpoint="z"))
    for bad_n in (399, 534, 100):
        with pytest.raises(ValueError, match="outside"):
            lrf_plan.plan_files(_nrec(tmp_path, bad_n), _m3(tmp_path))
    assert lrf_plan.plan_files(_nrec(tmp_path, 520), _m3(tmp_path))[0]["n_rule"]["test_fold"] == 520        # the rule's fallback value


def test_f5_main_writes_both_files_once_and_n_is_consistent_everywhere(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(common, "RUNS", runs)
    _m3(tmp_path)
    _nrec(tmp_path, 470)
    assert lrf_plan.main([]) == 0
    plan, plan_lg = runs / "P2-LRF-PLAN" / "family.json", runs / "P2-LRF-PLAN-LG" / "family.json"
    assert plan.exists() and plan_lg.exists() and lrf_plan.check_consistent(runs) == dict(n_L=470, lg_n=300)
    before = plan.read_bytes()
    assert lrf_plan.main([]) == 2 and plan.read_bytes() == before                                         # refuses to overwrite
    # run_gate_m4's own reading of the plan, the driver's default n and a6_analysis --n-rule all see the same n_L
    from exp_p2 import run_gate_m4 as m4
    assert m4.check_n_against_rule(470, runs, "P2-LRF-PLAN") == 470 and m4.check_n_against_rule(300, runs, "P2-LRF-PLAN-LG") == 300
    with pytest.raises(ValueError, match="n-rule"):
        m4.check_n_against_rule(533, runs, "P2-LRF-PLAN")
    assert gate_driver.default_n("lrf-l1", 533, runs) == 470 and gate_driver.default_n("lrf-lg", 300, runs) == 300
    thr, fam, eps0 = (None, None, None)
    assert [(f["corruption"], f["severity"]) for f in json.loads(plan.read_text())["family"]] == lrf_plan.P_OPERATING_POINTS
    A = _load("a6_analysis_f5", "analysis/paper2/lrf/a6_analysis.py")
    preds = tmp_path / "p.jsonl"
    preds.write_text("".join(json.dumps(dict(idx=i, gid=i, image_id=i, condition="noise0.1", n_tok=10, n_tok_neg=11, y_none=0, y_gatem=0, y_lrf=1)) + "\n" for i in range(30)))
    assert A.main(["--l1", str(preds), "--n-rule", str(runs / "P2-LRF-PLAN" / "n_rule.json"), "--out", str(tmp_path / "a.json")]) == 0
    assert json.loads((tmp_path / "a.json").read_text())["meta"]["n_l"] == 470
    (runs / "P2-LRF-PLAN" / "n_rule.json").write_text(json.dumps(dict(n_L=480)))
    with pytest.raises(ValueError, match="inconsistent"):
        lrf_plan.check_consistent(runs)


def test_f5_main_stops_on_bad_inputs(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(common, "RUNS", runs)
    assert lrf_plan.main([]) == 2                                                                         # nothing committed yet
    _m3(tmp_path, (("jpeg", 10),))
    _nrec(tmp_path, 470)
    assert lrf_plan.main([]) == 2 and not (runs / "P2-LRF-PLAN" / "family.json").exists() and not (runs / "P2-LRF-PLAN-LG" / "family.json").exists()


# ------------------------------------------------------------------------------------------------ D1: a failed check is final; deterministic cuDNN on the re-score path
def test_d1_a_checks_failed_event_is_final_and_cannot_be_retried_into_a_pass(env, monkeypatch):
    sc = _sc()
    _source_run(env, sc, 5)
    real = rescore.invariance
    monkeypatch.setattr(rescore, "invariance", lambda *a, **k: {"pos_B": 1e-3})
    with pytest.raises(rescore.ChecksFailed):
        _rescore(env, sc, 6)
    monkeypatch.setattr(rescore, "invariance", real)                                      # the retry would now pass the check ...
    assert "ChecksFailed" in rescore.failed_event(env / "RS6")
    with pytest.raises(rescore.ChecksFailed, match="final"):                                # ... but the runner refuses to resume this run id
        _rescore(env, sc, 6)
    assert common.read_jsonl(env / "RS6" / "items.jsonl") == [] and not (env / "RS6" / "arrays" / "item0000.npz").exists()
    res = rescore.check_rows(env / "RS6", slot_len=6)
    assert res["ok"] is False
    # even with passing rows written by hand next to the event, check_rows stays not ok
    good = rescore.CONDS
    rows = [dict(idx=i, invariance={c: {"pos_B": 0.0} for c in good}, invariance_max_abs_diff=0.0, positive_control={c: 0.0 for c in good}, positive_control_max_abs_diff=0.0) for i in range(5)]
    (env / "RS6" / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    res = rescore.check_rows(env / "RS6", slot_len=6)
    assert res["ok"] is False and "ChecksFailed event" in res["reason"] and "new run id" in res["reason"]
    # a new run id beside it works
    sc2 = _sc()
    assert rescore.failed_event(env / "RS9") is None and _rescore(env, sc2, 9) == 0 and rescore.failed_event(env / "RS9") is None


def test_d1_the_stage_main_refuses_a_run_with_the_event_and_the_driver_treats_it_as_a_refusal(env, monkeypatch):
    sc = _sc()
    _source_run(env, sc, 5)
    monkeypatch.setattr(rescore, "invariance", lambda *a, **k: {"pos_B": 1e-3})
    with pytest.raises(rescore.ChecksFailed):
        _rescore(env, sc, 6)
    monkeypatch.undo()
    monkeypatch.setattr(common, "RUNS", env)
    calls = []
    monkeypatch.setattr(runner, "run_items", lambda **kw: calls.append(kw) or 0)
    assert rescore.main(["--run-id", "RS6", "--slot-len", "6"]) == 2 and not calls                      # STOP before the model is touched
    assert 2 in gate_driver.REFUSAL_EXITS                                                                 # the driver reports the reason and its no-progress rule ends the campaign
    assert rescore.main(["--run-id", "RSnew", "--slot-len", "6"]) == 0 and len(calls) == 1               # a fresh id is not blocked


def test_d1_deterministic_cudnn_wraps_process_and_selfcheck_and_restores(env, monkeypatch):
    torch = pytest.importorskip("torch")
    cd = torch.backends.cudnn
    old = (cd.benchmark, cd.deterministic)
    cd.benchmark, cd.deterministic = True, False                                           # what UniDisc's set_torch_defaults() leaves behind
    seen = []
    try:
        wrapped = rescore.deterministic(lambda x: seen.append((cd.benchmark, cd.deterministic)) or x + 1)
        assert wrapped(1) == 2 and seen == [(False, True)] and (cd.benchmark, cd.deterministic) == (True, False)
        def boom():
            raise RuntimeError("x")
        with pytest.raises(RuntimeError):
            rescore.deterministic(boom)()
        assert (cd.benchmark, cd.deterministic) == (True, False)                           # restored also on an exception
        # main hands the runner the wrapped process and self-check
        sc = _sc()
        _source_run(env, sc, 5)
        monkeypatch.setattr(common, "RUNS", env)
        monkeypatch.setattr(common, "load_image", lambda iid: None)
        captured = {}
        monkeypatch.setattr(runner, "run_items", lambda **kw: captured.update(kw) or 0)
        assert rescore.main(["--run-id", "RSdet", "--slot-len", "6"]) == 0
        assert captured["process"].__wrapped__ is rescore.process and captured["selfcheck"].__wrapped__ is not None
        flags = []
        fake_sc = type("S", (), {"selfcheck": lambda self, img, cap: flags.append((cd.benchmark, cd.deterministic)) or {}})()
        captured["selfcheck"](fake_sc, [dict(image_id=1, caption="a b")])
        assert flags == [(False, True)] and (cd.benchmark, cd.deterministic) == (True, False)
    finally:
        cd.benchmark, cd.deterministic = old


# ------------------------------------------------------------------------------------------------ D2: the cross-fit needs the committed re-frozen object
def test_d2_object_commit_requires_a_tracked_unchanged_object(tmp_path, mods):
    rf, cf = mods
    repo, obj = _committed_object(tmp_path / "ok")
    sha = cf.object_commit(obj, repo)
    assert sha == _git(repo, "rev-parse", "HEAD")
    with pytest.raises(cf.rf.RefreezeRefused, match="missing"):
        cf.object_commit(tmp_path / "ok" / "runs" / "nope", repo)
    repo2, obj2 = _committed_object(tmp_path / "untracked", commit=False)
    with pytest.raises(cf.rf.RefreezeRefused, match="differs|failed"):                       # staged but never committed: HEAD does not exist / blob absent
        cf.object_commit(obj2, repo2)
    repo3 = tmp_path / "notracked"
    repo3.mkdir()
    _git(repo3, "init", "-q")
    _git(repo3, "config", "user.email", "t@example.org")
    _git(repo3, "config", "user.name", "t")
    (repo3 / "README").write_text("x")
    _git(repo3, "add", "-A")
    _git(repo3, "commit", "-q", "-m", "x")
    o3 = repo3 / "runs" / "P2-LRF-FROZEN-LFIX"
    o3.mkdir(parents=True)
    (o3 / "model.npz").write_bytes(b"m")
    (o3 / "spec.json").write_text("{}")
    with pytest.raises(cf.rf.RefreezeRefused, match="not tracked"):
        cf.object_commit(o3, repo3)
    (obj / "model.npz").write_bytes(b"model bytes CHANGED")
    with pytest.raises(cf.rf.RefreezeRefused, match="differs from its committed version"):
        cf.object_commit(obj, repo)
    (obj / "model.npz").write_bytes(b"model bytes")
    (obj / "spec.json").write_bytes(b'{"caption_slot_len": 13}\r\n')                           # a CRLF checkout of the same text is accepted
    assert cf.object_commit(obj, repo) == sha
    elsewhere = tmp_path / "elsewhere" / "P2-LRF-FROZEN-LFIX"
    elsewhere.mkdir(parents=True)
    (elsewhere / "model.npz").write_bytes(b"model bytes")
    (elsewhere / "spec.json").write_bytes(b"{}")
    with pytest.raises(cf.rf.RefreezeRefused, match="not inside"):
        cf.object_commit(elsewhere, repo)
    assert cf.object_commit(obj, repo / "runs") == sha                                        # the repository root is found from a subdirectory


def test_d2_crossfit_refuses_without_the_committed_object_and_writes_nothing(tmp_path, mods):
    rf, cf = mods
    src = _fake_rescore_run(tmp_path, 10, seed=5)
    out = tmp_path / "cf"
    repo, obj = _committed_object(tmp_path / "r", commit=False)
    with pytest.raises(cf.rf.RefreezeRefused):
        cf.crossfit(src, out, n_items=10, rmax=SMALL_R, n_cfg=SMALL_N, frozen_dir=obj, repo=repo)
    with pytest.raises(cf.rf.RefreezeRefused, match="missing"):
        cf.crossfit(src, out, n_items=10, rmax=SMALL_R, n_cfg=SMALL_N, frozen_dir=tmp_path / "nowhere", repo=repo)
    assert not out.exists()                                                                 # refused before anything was computed or written


def test_d2_the_cli_exits_non_zero_with_the_reason_on_stderr(tmp_path, mods, monkeypatch, capsys):
    rf, cf = mods
    src = _fake_rescore_run(tmp_path, 6, seed=6)
    monkeypatch.setattr(common, "RUNS", tmp_path / "runs")
    assert cf.main(["--src", str(src), "--out", str(tmp_path / "cf")]) == 2
    err = capsys.readouterr().err
    assert err.startswith("STOP:") and ("missing" in err or "not inside" in err) and not (tmp_path / "cf").exists()
