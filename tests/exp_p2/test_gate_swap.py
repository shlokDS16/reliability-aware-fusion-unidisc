"""Swap as an M4 condition and family PS (SAP AD.4, A2.5, AB.7 item 2, AD.13). CPU only: fake network, synthetic rows with known outcomes."""
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

from exp_p2 import core, run_gate_m4                                         # noqa: E402
from exp_p2.gate import analysis_m4 as A, arms, config, corruptions, pipeline, runner, seeds, stats   # noqa: E402
from exp_p2.scoring import IMG_VOCAB                                         # noqa: E402
from test_gate_m4_analysis import build, flips                               # noqa: E402
from test_gate_runners_fake import _fold, _m4_prereqs, _sc, _write_folds, env     # noqa: E402,F401  (env: the shared fixture)

# ------------------------------------------------------------------------------------------------ the swap corruption and its seeds
CLEAN = np.arange(1024) % 16384


def test_swap_replaces_exactly_round_015_of_the_positions_with_in_range_codes():
    out = corruptions.apply_token("swap", CLEAN, corruptions.token_rng(config.SEED_GATE, 2003, "swap"), grid=32, patch=8, swap_frac=config.SWAP_FRAC, vocab=IMG_VOCAB)
    changed = np.flatnonzero(out != CLEAN)
    assert len(changed) <= round(0.15 * 1024) and len(changed) >= round(0.15 * 1024) - 3         # a replacement code can equal the old one with probability 1/16384 per position
    assert out.min() >= 0 and out.max() < IMG_VOCAB
    ref = core.token_swap(CLEAN, config.SWAP_FRAC, IMG_VOCAB, np.random.default_rng([config.SEED_GATE, 2003, 191]))
    assert np.array_equal(out, ref)                                                               # swap is core.token_swap with the documented stream


def test_swap_stream_is_its_own_and_patch_is_bit_identical_to_the_old_formula():
    assert corruptions.TOKEN_RNG_TAG == {"patch": 190, "swap": 191}
    old_patch = corruptions.apply_token("patch", CLEAN, np.random.default_rng([config.SEED_GATE, 2003, 190]), grid=32, patch=8, swap_frac=config.SWAP_FRAC, vocab=IMG_VOCAB)
    new_patch = corruptions.apply_token("patch", CLEAN, corruptions.token_rng(config.SEED_GATE, 2003, "patch"), grid=32, patch=8, swap_frac=config.SWAP_FRAC, vocab=IMG_VOCAB)
    assert np.array_equal(old_patch, new_patch)
    sw = corruptions.apply_token("swap", CLEAN, corruptions.token_rng(config.SEED_GATE, 2003, "swap"), grid=32, patch=8, swap_frac=config.SWAP_FRAC, vocab=IMG_VOCAB)
    assert not np.array_equal(sw, old_patch)
    streams = [corruptions.token_rng(config.SEED_GATE, g, "swap").integers(0, 2 ** 31, 4).tolist() for g in range(2000, 2300)]
    assert len({tuple(s) for s in streams}) == 300                                                # distinct per item
    taken = {99} | {100 + 10 * i + r for i in range(3) for r in range(2)} | {150, 300}           # tags used by pipeline groups, M3 rungs, M3 donor, M5
    assert 191 not in taken and 190 not in taken


def test_appending_analyses_and_arm_tags_leaves_every_existing_stream_unchanged():
    old = ("load_items", "completeness_report", "arm_y_z", "exact_mcnemar", "paired_boot_diff", "primary", "s_m", "s_z", "s_dn", "s_d", "s_d2", "s_c", "headroom_check", "fap_check",
           "split_replication", "auroc", "detection_contrast", "wilcoxon_z", "fusion", "prop4_plugin", "mechanism", "calibration", "equivalence", "selftest", "denoise_check")
    assert seeds.ANALYSES[:len(old)] == old and seeds.ANALYSES[len(old):] == ("ps_family", "s2_family", "s2_descriptive", "edec", "omni_gate", "omni_r", "suite")
    for i, name in enumerate(old):
        ref = np.random.SeedSequence(seeds.ROOT_SEED).spawn(len(old))[i]
        assert np.array_equal(seeds.seed_for(name).generate_state(4), ref.generate_state(4)), name
    assert {k: v for k, v in arms.ARM_TAG.items() if v <= 5} == dict(jitter=1, geo=2, scattered=3, tbv=4, rand=5)
    assert len(set(arms.ARM_TAG.values())) == len(arms.ARM_TAG)


# generate_state(2) of every child seed that existed before the 2026-10-28 integration append, taken from the committed code BEFORE the append (positions 0 to 27)
PINNED_CHILD_STATES = {
    "load_items": [3458662461, 120824907], "completeness_report": [1334675065, 4289651540], "arm_y_z": [3661117191, 2747377106], "exact_mcnemar": [1350303508, 1030060],
    "paired_boot_diff": [3870639956, 85204196], "primary": [8877476, 2339256909], "s_m": [968133149, 17037775], "s_z": [1411562759, 3877490036], "s_dn": [3992135531, 1369830523],
    "s_d": [2375801364, 3347953186], "s_d2": [3676282196, 533490309], "s_c": [3683846524, 2116412728], "headroom_check": [2064910752, 1315251617], "fap_check": [2776190707, 183230860],
    "split_replication": [1763477818, 341304458], "auroc": [657830656, 3022808854], "detection_contrast": [2797472673, 2842381725], "wilcoxon_z": [643057741, 1858764172],
    "fusion": [669159009, 1290250544], "prop4_plugin": [1783527896, 1966023535], "mechanism": [120622869, 227623426], "calibration": [2766538161, 164287317],
    "equivalence": [35810075, 1970453583], "selftest": [3929955576, 3847895947], "denoise_check": [2674509556, 2360531449], "ps_family": [50047534, 2999836831],
    "s2_family": [3407153610, 628317643], "s2_descriptive": [2600813101, 738724086]}


def test_every_pre_existing_child_seed_is_unchanged_by_the_integration_append():
    assert list(PINNED_CHILD_STATES) == list(seeds.ANALYSES[:28])                                   # same names in the same positions
    for name, state in PINNED_CHILD_STATES.items():
        assert [int(x) for x in seeds.seed_for(name).generate_state(2)] == state, name
    for i, name in enumerate(seeds.ANALYSES[28:], start=28):                                      # the appended names sit at their spawn positions and are distinct streams
        assert np.array_equal(seeds.seed_for(name).generate_state(4), np.random.SeedSequence(seeds.ROOT_SEED, spawn_key=(i,)).generate_state(4)), name
    assert [seeds.ANALYSES.index(n) for n in ("edec", "omni_gate", "omni_r", "suite")] == [28, 29, 30, 31]
    assert len({tuple(seeds.seed_for(n).generate_state(2)) for n in seeds.ANALYSES}) == len(seeds.ANALYSES) == len(set(seeds.ANALYSES))


# ------------------------------------------------------------------------------------------------ swap inside M4 (fake network, 4 x 4 token grid)
def _ctx(env, sc, sanity):
    fam = [("jpeg", 10), ("noise", 0.1), ("splice", 128)]
    _m4_prereqs(env, sc, fam)
    items = _fold(4, offset=2000)
    _write_folds(env, test=items)
    a = SimpleNamespace(tbv="off", denoise_for="jpeg,noise", **({} if sanity is None else dict(sanity=sanity)))
    (env / "P2-GATE-M4").mkdir(exist_ok=True)
    return items, run_gate_m4.make_ctx_factory(a, env)(sc, env / "P2-GATE-M4")


def test_m4_with_swap_has_the_swap_condition_after_patch_with_all_arms_and_costs_8_more_passes(env):
    sc = _sc()
    items, ctx = _ctx(env, sc, "patch,swap")
    assert ctx.sanity == ("patch", "swap")
    run_gate_m4.process(sc, items[0], ctx)                                    # warm the null caches
    row, arrays = run_gate_m4.process(sc, items[1], ctx)
    assert list(row["conds"]) == ["clean", "jpeg10", "jpeg10_dn", "noise0.1", "noise0.1_dn", "splice128", "patch", "swap"]
    assert row["n_rows"] == 70 + 8                                            # 70 without TbV (test_gate_runners_fake) + one B per group for swap
    sw = row["conds"]["swap"]
    assert sw["kind"] == "token" and sw["txt"] == {} and 1 <= sw["n_changed"] <= round(config.SWAP_FRAC * 16)
    assert np.array_equal(arrays["swap_z"], arrays["swap_codes"] != arrays["clean_codes"])
    for arm in ("none", "gate0.05", "gate0.01", "gate0.1", "geo0", "geo1", "geo2", "scat0", "scat1", "scat2", "topkB", "topks3", "chg"):
        assert arm in sw["img"]
    n_g = sw["gate"]["0.05"]["n_flag"]
    for arm in ("geo0", "geo1", "geo2", "scat0", "scat1", "scat2", "topkB", "topks3"):
        assert sw["img"][arm]["n"] == 16 - n_g                                # equal size to GATE-M's gate
    for k in ("B", "D", "s3", "delta", "flag0.05", "flag0.01", "flag0.1", "tex", "nbr"):
        assert f"swap_{k}" in arrays
    row2, _ = run_gate_m4.process(sc, items[1], ctx)
    assert {k: v for k, v in row2.items() if k != "n_rows"} == {k: v for k, v in row.items() if k != "n_rows"}


def test_adding_swap_does_not_change_any_earlier_condition_nor_its_seeds(env):
    sc = _sc()
    items, ctx2 = _ctx(env, sc, "patch,swap")
    _, ctx1 = _ctx(env, sc, "patch")
    r2, a2 = run_gate_m4.process(sc, items[2], ctx2)
    r1, a1 = run_gate_m4.process(sc, items[2], ctx1)
    assert list(r1["conds"]) == list(r2["conds"])[:-1]
    for c in r1["conds"]:
        assert r1["conds"][c] == r2["conds"][c]
    for k in a1:
        assert np.array_equal(a1[k], a2[k], equal_nan=a1[k].dtype.kind == "f"), k


def test_a_bare_namespace_keeps_the_pre_swap_behaviour_and_the_cli_default_has_swap(env, monkeypatch):
    sc = _sc()
    items, ctx = _ctx(env, sc, None)
    assert ctx.sanity == ("patch",)
    seen = {}
    monkeypatch.setattr(run_gate_m4, "load_prereqs", lambda *a, **k: None)
    monkeypatch.setattr(pipeline, "require_frozen", lambda *a, **k: None)
    monkeypatch.setattr(run_gate_m4, "check_n_against_rule", lambda *a, **k: 300)
    monkeypatch.setattr(runner, "run_items", lambda **kw: seen.update(kw) or 0)
    assert run_gate_m4.main([]) == 0
    assert seen["cfg"]["sanity"] == ["patch", "swap"]
    assert run_gate_m4.main(["--sanity", "swap,bogus"]) == 2
    assert run_gate_m4.parse_sanity("swap,patch") == ("patch", "swap")        # fixed order: condition indices (hence seeds) never depend on the flag order


# ------------------------------------------------------------------------------------------------ family PS
def _rows(tmp_path, n, y, conds=("clean", "patch", "swap")):
    run, rows = build(tmp_path, n, y, conds=conds)
    return rows


def test_ps_both_rejected_with_right_sign_is_met_and_holm_uses_m2(tmp_path):
    n = 100
    gp, op = flips(n, 20, 2)
    gs, os_ = flips(n, 15, 1)
    rows = _rows(tmp_path, n, {("patch", "gate0.05"): gp, ("patch", "none"): op, ("swap", "gate0.05"): gs, ("swap", "none"): os_})
    ps = A.ps_family(rows, n_boot=300)
    p1, p2 = ps["per_corruption"]["patch"], ps["per_corruption"]["swap"]
    assert (p1["b"], p1["c"], p1["n_d"]) == (20, 2, 22) and (p2["b"], p2["c"]) == (15, 1)
    assert p1["label"] == "PS1" and p2["label"] == "PS2" and ps["holm_m"] == 2
    assert np.allclose([p1["p_holm"], p2["p_holm"]], stats.holm([p1["p"], p2["p"]]))
    assert p1["gate_better"] and p2["gate_better"] and ps["positive_control"] == "met" and ps["on_not_met"] is None
    assert "no headline claim" in ps["label"]


def test_ps_swap_not_run_gets_p1_and_stays_in_m2_so_the_best_reading_is_partly_met(tmp_path):
    n = 100
    gp, op = flips(n, 12, 0)
    rows = _rows(tmp_path, n, {("patch", "gate0.05"): gp, ("patch", "none"): op}, conds=("clean", "patch"))
    ps = A.ps_family(rows, n_boot=200)
    sw = ps["per_corruption"]["swap"]
    assert not sw["tested"] and sw["p"] == 1.0 and sw["p_holm"] == 1.0 and not sw["gate_better"]
    p1 = ps["per_corruption"]["patch"]
    assert p1["p_holm"] == pytest.approx(min(1.0, 2 * p1["p"]))                                    # m = 2 even though only one cell exists
    assert ps["positive_control"] == "partly met" and ps["n_rejected_right_sign"] == 1 and "audit" in ps["on_not_met"]


def test_ps_a_significant_difference_in_the_wrong_direction_does_not_count(tmp_path):
    n = 100
    gp, op = flips(n, 1, 20)                                                                       # GATE-M loses on patch
    gs, os_ = flips(n, 15, 1)
    rows = _rows(tmp_path, n, {("patch", "gate0.05"): gp, ("patch", "none"): op, ("swap", "gate0.05"): gs, ("swap", "none"): os_})
    ps = A.ps_family(rows, n_boot=200)
    assert ps["per_corruption"]["patch"]["p_holm"] < 0.05 and not ps["per_corruption"]["patch"]["gate_better"]
    assert ps["positive_control"] == "partly met"
    nul = A.ps_family(_rows(tmp_path / "x", n, {}), n_boot=100)
    assert nul["positive_control"] == "not met" and nul["n_rejected_right_sign"] == 0


def test_ps_holm_thresholds_are_0_025_and_0_05(tmp_path):
    n = 200
    # constructed p-values: patch about 0.043 (b=21, c=9), swap far smaller; Holm adjusted p of the larger is its own p, of the smaller twice its own
    gp, op = flips(n, 21, 9)
    gs, os_ = flips(n, 25, 5)
    rows = _rows(tmp_path, n, {("patch", "gate0.05"): gp, ("patch", "none"): op, ("swap", "gate0.05"): gs, ("swap", "none"): os_})
    ps = A.ps_family(rows, n_boot=100)
    p1, p2 = ps["per_corruption"]["patch"], ps["per_corruption"]["swap"]
    assert p2["p"] < p1["p"]
    assert p2["p_holm"] == pytest.approx(2 * p2["p"]) and p1["p_holm"] == pytest.approx(max(p1["p"], 2 * p2["p"]))
    assert 0.025 < p1["p"] < 0.05 and p1["gate_better"] and p2["gate_better"]                       # the larger p is the second Holm step (threshold 0.05), the smaller the first (0.025)


def test_ps_under_rule_r3_uses_wilcoxon_on_d_and_a_positive_difference(tmp_path):
    n = 80
    d = {("patch", "gate0.05"): np.full(n, 0.4) + np.linspace(0, 0.05, n), ("patch", "none"): np.full(n, 0.1),
         ("swap", "gate0.05"): np.full(n, 0.1) + np.linspace(0, 0.05, n), ("swap", "none"): np.full(n, 0.4)}
    rows = _rows(tmp_path, n, {}, conds=("clean", "patch", "swap"))
    run, rows = build(tmp_path / "r3", n, {}, d=d, conds=("clean", "patch", "swap"))
    ps = A.ps_family(rows, rule="R3", n_boot=100)
    assert ps["endpoint"].startswith("d")
    assert ps["per_corruption"]["patch"]["gate_better"] and not ps["per_corruption"]["swap"]["gate_better"]       # swap: significant but negative
    assert ps["positive_control"] == "partly met"


def test_ps_accepts_a_dataframe_and_prints_descriptive_numbers_beside_the_tests(tmp_path):
    import pandas as pd
    n = 60
    gp, op = flips(n, 10, 1)
    run, rows = build(tmp_path, n, {("patch", "gate0.05"): gp, ("patch", "none"): op, ("jpeg10", "gate0.05"): gp, ("jpeg10", "none"): op}, conds=("clean", "jpeg10", "patch", "swap"))
    fam = [dict(corruption="jpeg", severity=10, key="jpeg10")]
    ps = A.ps_family(pd.DataFrame(rows), "R1", fam, n_boot=200)
    d = ps["per_corruption"]["patch"]["desc"]
    assert d["share_discordant"] == pytest.approx(11 / 60) and "jpeg10" in d["ps_minus_P_cell_accuracy_difference"]
    assert d["ps_minus_P_cell_accuracy_difference"]["jpeg10"]["diff"] == pytest.approx(0.0)
    assert set(d) >= {"acc_none", "acc_clean_none", "headroom_T1_clean_minus_none", "headroom_T2_changed_code_minus_none", "mean_n_changed"}
    lst = A.ps_family(rows, "R1", fam, n_boot=200)                                                 # a DataFrame and a list of rows give the same numbers
    assert {c: (e["b"], e["c"], e["p"], e["p_holm"]) for c, e in ps["per_corruption"].items()} == {c: (e["b"], e["c"], e["p"], e["p_holm"]) for c, e in lst["per_corruption"].items()}


def test_run_includes_ps_and_the_swap_condition_in_mechanism_and_calibration(tmp_path):
    n = 60
    g, o = flips(n, 8, 1)
    run, rows = build(tmp_path, n, {("patch", "gate0.05"): g, ("patch", "none"): o, ("swap", "gate0.05"): g, ("swap", "none"): o}, conds=("clean", "jpeg10", "patch", "swap"))
    res = A.run(run, [dict(corruption="jpeg", severity=10, key="jpeg10")], n_boot=100)
    assert res["ps"]["holm_m"] == 2 and res["ps"]["positive_control"] in ("met", "partly met", "not met")
    assert {"patch", "swap", "jpeg10"} <= set(res["mechanism"]) and {"patch", "swap"} <= set(res["calibration"]["per_condition"])
    old, _ = build(tmp_path / "old", n, {}, conds=("clean", "jpeg10", "patch"))                       # a run made before swap existed still analyses
    res0 = A.run(old, [dict(corruption="jpeg", severity=10, key="jpeg10")], n_boot=100)
    assert not res0["ps"]["per_corruption"]["swap"]["tested"] and "swap" not in res0["mechanism"]
