"""End-to-end CPU runs of the Omni timing runner and the family R runner (cal, pos, test) on the fake Omni stack, through `runner.run_items` with its real bookkeeping (rows, arrays,
resume, exclusions, prerequisites). No GPU, no weights, no real folds; every path is a temp dir."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fake_gate import fake_image                                                       # noqa: E402
from test_omni_fakes import make_scorer                                                # noqa: E402
from exp_p2 import common, run_gate_omni_r as R, run_omni_timing as T                  # noqa: E402
from exp_p2.gate import analysis_omni as ao, folds, runner, guards as gmod             # noqa: E402
from exp_p2.omni import build                                                          # noqa: E402

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
    monkeypatch.setattr(folds, "folds_path", lambda run_id=None: tmp_path / "folds.json")
    monkeypatch.setattr(T, "adapter_selfcheck", lambda sc, items, info, a: dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=1.0, adapter=dict(all_ok=True, failed=[])))
    (tmp_path / "folds.json").write_text(json.dumps(_folds()))
    return tmp_path


def _items(n, offset, gid0, n_words=6, seed=1):
    rng = np.random.default_rng(seed + offset)
    its = [dict(idx=offset + i, gid=gid0 + offset + i, image_id=100 + gid0 + offset + i, caption=" ".join(rng.choice(WORDS, n_words, replace=False)), n_tok=n_words) for i in range(n)]
    for i, it in enumerate(its):
        j = (i + 1) % n
        it.update(neg_idx=offset + j, neg_image_id=its[j]["image_id"], neg_caption=its[j]["caption"], neg_restricted=True)
    return its


def _folds():
    test = _items(300, 0, 2000)
    ext = _items(200, 300, 2000)
    return dict(meta={}, cal=_items(40, 0, 0), head=_items(5, 0, 1000), test=test, test_ext=ext)


def _run_timing(env, extra=()):
    return T.main(["--n", "8", "--soft-minutes", "30", "--duty", "1", *extra], scorer_factory=lambda: runner.Counting(make_scorer(grid=4)), guards_factory=lambda a: None)


def test_timing_runner_rows_selfcheck_and_resume(env):
    assert _run_timing(env, ["--limit", "5"]) == 75                                         # soft stop after 5 new items
    rows = common.read_jsonl(env / "P2-OMNI-TIMING" / "items.jsonl")
    assert len(rows) == 5
    assert _run_timing(env) == 0
    rows = common.read_jsonl(env / "P2-OMNI-TIMING" / "items.jsonl")
    assert len(rows) == 8 and [r["idx"] for r in rows] == list(range(8))
    r = rows[0]
    assert r["fwd_s"] > 0 and r["finite"] and r["n_masked"] > 0 and r["seq_len"] > 0 and "proc_pass" in r and "seconds" in r
    assert (env / "P2-OMNI-TIMING" / "selfcheck.json").exists() and (env / "P2-OMNI-TIMING" / "omni_token_exclusions.json").exists()
    # the rows feed omni_gate: t is the median of passes 6-8 here (3 of 8 rows after the warm-up), so the rule (a) '20 passes' is not met
    assert not ao.timing_t(rows)["complete"]


def test_timing_runner_stops_on_a_failed_selfcheck(env, monkeypatch):
    monkeypatch.setattr(T, "adapter_selfcheck", lambda sc, items, info, a: dict(ids_equal=False, modality_equal=True, image_tokens_frac_equal=1.0))
    assert _run_timing(env) == runner.EXIT_SELFCHECK
    assert not (env / "P2-OMNI-TIMING" / "items.jsonl").exists() or not common.read_jsonl(env / "P2-OMNI-TIMING" / "items.jsonl")


def test_omni_guards_peak_rule_and_preload_check():
    g = build.OmniGuards(peak_fn=lambda: 7100.0, max_peak_alloc_mib=7000.0, used_fn=lambda: 0.0, ac_fn=lambda: True)
    assert "peak_allocated" in g.after_item(0.1)
    g2 = build.OmniGuards(peak_fn=lambda: 6900.0, max_peak_alloc_mib=7000.0, used_fn=lambda: 0.0, ac_fn=lambda: True)
    assert g2.after_item(0.1) is None
    a = build.omni_parser("X", None).parse_args([])
    assert a.mem_frac == 0.62 and a.max_used_first_mib == 9500.0 and a.max_used_mib == 9000.0 and a.max_peak_alloc_mib == 7000.0 and a.micro_bs == 1 and a.magvit_device == "cpu"
    assert build.preload_check(a, lambda: dict(mem_used_mib=3000.0)) == runner.EXIT_GUARD
    assert build.preload_check(a, lambda: dict(mem_used_mib=99999.0)) == runner.EXIT_GUARD       # unreadable sensor: fail closed
    assert build.preload_check(a, lambda: dict(mem_used_mib=900.0)) is None


def test_omni_token_filter_excludes_counts_and_never_replaces():
    sc = make_scorer()
    items = [dict(idx=0, caption="red blue green small large", neg_caption="a b c d e f"), dict(idx=1, caption="red blue", neg_caption="a b c d e f"),
             dict(idx=2, caption=" ".join(["w"] * 40), neg_caption="a b c d e f"), dict(idx=3, caption="red blue green small large old", neg_caption="x"),
             dict(idx=4, caption="red blue green <|mask|> large old", neg_caption="a b c d e f")]
    kept, rep = build.omni_token_filter(sc, items)
    assert [k["idx"] for k in kept] == [0] and rep["excluded"] == {"too_short": [1, 3], "too_long": [2], "special_token": [4]} and rep["n_excluded"] == 4
    kept2, _ = build.omni_token_filter(sc, items, need_neg=False)
    assert [k["idx"] for k in kept2] == [0, 3]                                              # item 3 survives when c- is not needed (calibration)


# ------------------------------------------------------------------------------------------------ family R
PASSING_SELFCHECK = dict(ids_equal=True, adapter=dict(all_ok=True, failed=[], results=[dict(id=f"A{i}", ok=True) for i in range(1, 8)]))


def _prereqs(env, n_R=6, go=True, sign=True, p_plus=("jpeg",)):
    t = env / "P2-OMNI-TIMING"
    t.mkdir(exist_ok=True)
    (t / "selfcheck.json").write_text(json.dumps(PASSING_SELFCHECK))
    (t / "omni_gate.json").write_text(json.dumps(dict(go=go, status="GO" if go else "NO-GO", n_R=n_R)))
    if sign:
        (t / "adapter_signature.json").write_text(json.dumps(dict(signed_by="gate-auditor", verdict="PASS", selfcheck_sha256=hashlib.sha256((t / "selfcheck.json").read_bytes()).hexdigest())))
    (env / "P2-GATE-M3").mkdir(exist_ok=True)
    (env / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="d", family=[dict(corruption="jpeg", severity=10, key="jpeg10"), dict(corruption="noise", severity=0.1, key="noise0.1")], n_rule=dict(rule="R1", test_fold=300))))
    (env / "P2-GATE-M4").mkdir(exist_ok=True)
    (env / "P2-GATE-M4" / "analysis.json").write_text(json.dumps({"rule": "R1", "primary": {"per_corruption": {c: {"gate_better": c in p_plus} for c in ("jpeg", "noise", "splice")}}}))


def _go(env, stage, extra=(), **kw):
    return R.main(["--stage", stage, "--soft-minutes", "30", "--duty", "1", *extra], scorer_factory=lambda: runner.Counting(make_scorer(grid=4)), runs=env, guards_factory=lambda a: None, **kw)


def test_prerequisites_are_enforced_before_any_model_is_touched(env, capsys):
    def boom():
        raise AssertionError("the model factory must not be called")
    assert R.main(["--stage", "cal"], scorer_factory=boom, runs=env, guards_factory=lambda a: None) == 2         # no omni_gate.json
    _prereqs(env, sign=False)
    assert R.main(["--stage", "cal"], scorer_factory=boom, runs=env, guards_factory=lambda a: None) == 2         # no auditor signature
    _prereqs(env, go=False)
    assert R.main(["--stage", "cal"], scorer_factory=boom, runs=env, guards_factory=lambda a: None) == 2         # NO-GO: R is not run
    _prereqs(env)
    (env / "P2-OMNI-TIMING" / "selfcheck.json").write_text(json.dumps(dict(PASSING_SELFCHECK, changed=1)))      # the signature binds the file it was given
    assert R.main(["--stage", "cal"], scorer_factory=boom, runs=env, guards_factory=lambda a: None) == 2
    partial = dict(ids_equal=True, adapter=dict(all_ok=True, failed=[], results=[dict(id=f"A{i}", ok=True) for i in range(1, 4)]))      # a --skip-gpu-adapter-checks self-check (A1-A3 only), even if signed
    _prereqs(env)
    t = env / "P2-OMNI-TIMING"
    (t / "selfcheck.json").write_text(json.dumps(partial))
    (t / "adapter_signature.json").write_text(json.dumps(dict(signed_by="gate-auditor", verdict="PASS", selfcheck_sha256=hashlib.sha256((t / "selfcheck.json").read_bytes()).hexdigest())))
    assert R.main(["--stage", "cal"], scorer_factory=boom, runs=env, guards_factory=lambda a: None) == 2
    assert "A1..A7" in capsys.readouterr().err
    _prereqs(env)
    assert R.main(["--stage", "pos"], scorer_factory=boom, runs=env, guards_factory=lambda a: None) == 2         # needs the calibration threshold
    assert R.main(["--stage", "test"], scorer_factory=boom, runs=env, guards_factory=lambda a: None) == 2        # needs threshold, positive control
    assert "STOP" in capsys.readouterr().err


def test_cal_pos_test_pipeline_end_to_end(env, monkeypatch):
    monkeypatch.setattr(R, "N_CAL", 30)
    monkeypatch.setattr(R, "N_POS", 6)
    monkeypatch.setitem(R.STAGE_DEFAULTS, "cal", (R.CAL_RUN, 30))
    _prereqs(env, n_R=6, p_plus=("jpeg", "noise"))
    # --- calibration
    assert _go(env, "cal") == 0
    crow = common.read_jsonl(env / "P2-OMNI-R-CAL" / "items.jsonl")
    assert len(crow) == 30 and crow[0]["n_rows"] == 8 + 1 and (env / "P2-OMNI-DCACHE").exists() and not (env / "P2-GATE-DCACHE").exists()      # 8 passes + one null on a cold cache; its own cache
    res = ao.fit_omni_threshold(env / "P2-OMNI-R-CAL")
    assert set(res["thresholds"]) == {"0.05"} and res["thresholds"]["0.05"]["feasible"]
    # --- positive control (the stage itself; the pass/fail verdict is data, here written by hand to continue)
    assert _go(env, "pos") == 0
    prow = common.read_jsonl(env / "P2-OMNI-R-POS" / "items.jsonl")
    assert len(prow) == 6 and [r["idx"] for r in prow] == list(range(300, 306)) and prow[0]["n_rows"] <= 8 and prow[0]["n_changed"] > 0
    arr = np.load(env / "P2-OMNI-R-POS" / "arrays" / "item0300.npz")
    assert arr["z"].sum() == prow[0]["n_changed"] and arr["B"].shape == (16,) and arr["codes_patched"].max() < 8192
    pc = ao.omni_positive_control(env / "P2-OMNI-R-POS", n_boot=200)
    assert set(pc) >= {"mean_auroc", "lower_bound", "passed"}
    assert _go(env, "test") == 2                                                            # positive control not written as passed: refuse (patch the file to continue)
    (env / "P2-OMNI-R-POS" / "pos_control.json").write_text(json.dumps(dict(passed=True)))
    # --- test
    assert _go(env, "test") == 0
    rows = common.read_jsonl(env / "P2-OMNI-R-TEST" / "items.jsonl")
    assert len(rows) == 6 and [r["idx"] for r in rows] == list(range(300, 306))             # positions 301..306 of the ordered test list
    r0 = rows[0]
    assert set(r0["conds"]) == {"clean", "jpeg10", "noise0.1"} and set(r0["conds"]["jpeg10"]["img"]) == {"none", "gate0.05"} and r0["corrupt_at"] == 512
    assert r0["conds"]["clean"]["n_changed"] == 0 and r0["conds"]["jpeg10"]["n_tokens"] == 16 and r0["n_rows"] == 2 + 3 * 8              # 2 lambda passes + 8 B passes per condition, nulls cached
    a0 = np.load(env / "P2-OMNI-R-TEST" / "arrays" / "item0300.npz")
    assert a0["jpeg10_B"].shape == (16,) and a0["jpeg10_codes"].max() < 8192
    P = json.loads((env / "P2-GATE-M4" / "analysis.json").read_text())
    out = ao.omni_r(rows, P, family=["jpeg10", "noise0.1"], n_boot=100)
    assert out["status"] == "analysed" and out["p_plus"] == ["jpeg", "noise"] and out["completed_n"] == 6 and not out["formal"] and out["wording"].startswith("descriptive only")


def test_test_stage_uses_only_p_plus_and_n_must_match_omni_gate(env, monkeypatch):
    monkeypatch.setattr(R, "N_CAL", 30)
    monkeypatch.setitem(R.STAGE_DEFAULTS, "cal", (R.CAL_RUN, 30))
    _prereqs(env, n_R=4, p_plus=("noise",))
    assert _go(env, "cal") == 0
    ao.fit_omni_threshold(env / "P2-OMNI-R-CAL")
    (env / "P2-OMNI-R-POS").mkdir(exist_ok=True)
    (env / "P2-OMNI-R-POS" / "pos_control.json").write_text(json.dumps(dict(passed=True)))
    assert _go(env, "test", ["--n", "5"]) == 2                                              # --n must equal n_R
    assert _go(env, "test") == 0
    rows = common.read_jsonl(env / "P2-OMNI-R-TEST" / "items.jsonl")
    assert len(rows) == 4 and set(rows[0]["conds"]) == {"clean", "noise0.1"}               # P+ = {noise}: jpeg is never run
    assert R.check_prereqs("test", env)["n_R"] == 4


def test_empty_p_plus_means_r_is_not_run(env):
    _prereqs(env, p_plus=())
    (env / "P2-OMNI-R-CAL").mkdir(exist_ok=True)
    (env / "P2-OMNI-R-CAL" / "threshold.json").write_text(json.dumps(dict(thresholds={"0.05": dict(tau=1.0, alpha=0.05, n_cal=30, eps0=0.1, statistic="q", K=8, seed=1, ids_hash="", feasible=True, r_hat=0.0, eps0_resolvable=True)})))
    (env / "P2-OMNI-R-POS").mkdir(exist_ok=True)
    (env / "P2-OMNI-R-POS" / "pos_control.json").write_text(json.dumps(dict(passed=True)))
    with pytest.raises(ValueError, match="P\\+ is empty"):
        R.check_prereqs("test", env)


def test_item_selection_positions_and_corrupt_at_256(env, monkeypatch):
    monkeypatch.setattr(R, "N_CAL", 30)
    monkeypatch.setitem(R.STAGE_DEFAULTS, "cal", (R.CAL_RUN, 30))
    _prereqs(env, n_R=3)
    assert _go(env, "cal") == 0
    ao.fit_omni_threshold(env / "P2-OMNI-R-CAL")
    (env / "P2-OMNI-R-POS").mkdir(exist_ok=True)
    (env / "P2-OMNI-R-POS" / "pos_control.json").write_text(json.dumps(dict(passed=True)))
    assert _go(env, "test", ["--corrupt-at", "256", "--run-id", "P2-OMNI-R-TEST256"]) == 0
    rows = common.read_jsonl(env / "P2-OMNI-R-TEST256" / "items.jsonl")
    assert len(rows) == 3 and rows[0]["corrupt_at"] == 256 and [r["idx"] for r in rows] == [300, 301, 302]
