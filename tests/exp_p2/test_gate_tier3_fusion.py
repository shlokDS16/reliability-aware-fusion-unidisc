"""Tier-3 comparators (SAP A4.1, exp_p2/gate/tier3_fusion.py): each arm on hand-computable fixtures, the A4.1.3 consistency gate, the A4.1.9 refusal, write-once, bootstrap
determinism by seed, MDD, the trimming control on d, and that no p-value is produced. SYNTHETIC data only (a temporary run directory and a temporary git repository); no real
M2, M3 or M4 file is read. CPU only."""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import analysis_m4, tier3_fusion as C, config, evidence, fit_threshold, pipeline, scores, seeds     # noqa: E402

M = C.M_TOKENS
AK = C.ALPHA_KEY


# ------------------------------------------------------------------------------------------------ hand-computable arms
def pool10(tau=6.5):
    """Calibration tokens u = 0..9 (N = 10)."""
    return C.CalPool(np.arange(10, dtype=np.float64), tau)


def test_none_and_gm_equal_evidence_from_delta():
    rng = np.random.default_rng(0)
    d = rng.normal(0.1, 1.0, M).astype(np.float32)
    F = rng.random(M) < 0.07
    mg = C.item_margins(d, F, rng.normal(size=M).astype(np.float32), pool10())
    assert mg["NONE"][0] == evidence.evidence_from_delta(d)["mean"]
    assert mg["GM"][0] == evidence.evidence_from_delta(d, ~F)["mean"]
    assert int(mg["NONE"][0] > 0) == evidence.evidence_from_delta(d)["y"] and int(mg["GM"][0] > 0) == evidence.evidence_from_delta(d, ~F)["y"]


DELTA8 = np.array([-10, -2, -1, 1, 2, 3, 4, 5], np.float32)      # sorted; NONE mean = 2/8 = 0.25


def test_med_tm_g_tm20_by_hand():
    u = np.zeros(8, np.float32)
    F1 = np.array([1, 0, 0, 0, 0, 0, 0, 0], bool)                 # g = 1 -> k = 0 -> TM-G = NONE
    mg = C.item_margins(DELTA8, F1, u, pool10())
    assert mg["NONE"][0] == pytest.approx(0.25)
    assert mg["GM"][0] == pytest.approx(12 / 7)                    # (-2-1+1+2+3+4+5) / 7
    assert mg["MED"][0] == pytest.approx(1.5)                      # mean of sorted[3], sorted[4] = (1 + 2) / 2
    assert mg["TM-G"][0] == mg["NONE"][0]
    assert mg["TM20"][0] == pytest.approx(7 / 6)                   # k = floor(0.2 * 8) = 1 -> sorted[1:7] = -2,-1,1,2,3,4
    F4 = np.array([1, 1, 0, 0, 0, 0, 1, 1], bool)                  # g = 4 -> k = 2 per tail -> sorted[2:6] = -1,1,2,3
    assert C.item_margins(DELTA8, F4, u, pool10())["TM-G"][0] == pytest.approx(1.25)
    F5 = np.array([1, 1, 1, 0, 0, 0, 1, 1], bool)                  # g = 5 -> k = 2 (floor)
    assert C.item_margins(DELTA8, F5, u, pool10())["TM-G"][0] == pytest.approx(1.25)


def test_tm20_removes_204_per_tail_of_1024():
    rng = np.random.default_rng(1)
    d = rng.normal(size=M)
    srt = np.sort(d)
    mg = C.item_margins(d, np.zeros(M, bool), np.zeros(M, np.float32), pool10())
    assert mg["TM20"][0] == pytest.approx(srt[204:M - 204].mean())
    assert M - 2 * 204 == 616


def test_trimmed_mean_511_per_tail_equals_median():
    rng = np.random.default_rng(2)
    d = rng.normal(size=M)
    F = np.zeros(M, bool)
    F[:1022] = True                                                # g = 1022 -> k = 511 per tail
    mg = C.item_margins(d, F, np.zeros(M, np.float32), pool10())
    assert mg["TM-G"][0] == pytest.approx(np.median(d), abs=1e-15)
    assert mg["MED"][0] == np.median(d)


def test_tm_g_g_le_1_equals_none_exactly():
    rng = np.random.default_rng(3)
    d = rng.normal(0.02, 1.0, M).astype(np.float32)
    for g in (0, 1):
        F = np.zeros(M, bool)
        F[:g] = True
        mg = C.item_margins(d, F, np.zeros(M, np.float32), pool10())
        assert mg["TM-G"] == mg["NONE"]


def test_weights_by_hand():
    p = pool10(6.5)
    assert float(p.survival(6.5)) == pytest.approx(0.3)           # 7, 8, 9
    u = np.array([1.0, 7.0, 8.0, 9.0, 6.7])
    F = np.array([0, 1, 1, 1, 1], bool)
    wg = p.weights_g(u, F)
    assert wg == pytest.approx([1.0, 2 / 3, 1 / 3, 0.0, 1.0])     # S(7) = .2, S(8) = .1, S(9) = 0, S(6.7) = .3 -> min(1, 1)
    wa = p.weights_a(np.array([9.0, -1.0, 4.5, 3.0]))
    assert wa == pytest.approx([2 / 11, 1.0, 6 / 11, 8 / 11])      # (1 + #{>= x}) / 11
    d = np.array([2.0, 3.0, 3.0, -30.0])
    mg = C.item_margins(d, F[:4], u[:4], p)
    assert mg["SOFT-G"][0] == pytest.approx((2 + 3 * 2 / 3 + 3 / 3 + 0) / (1 + 2 / 3 + 1 / 3 + 0))     # = 5 / 2
    wa4 = p.weights_a(u[:4])                                      # u = 1, 7, 8, 9 -> (1+9)/11, (1+3)/11, (1+2)/11, (1+1)/11
    assert mg["SOFT-A"][0] == pytest.approx(float(np.sum(wa4 * d) / wa4.sum()))
    assert float(np.sum(wa4 * d) / wa4.sum()) == pytest.approx((10 * 2 + 4 * 3 + 3 * 3 - 2 * 30) / (10 + 4 + 3 + 2))


def test_soft_g_with_no_flags_equals_none_and_zero_survival_equals_gm():
    rng = np.random.default_rng(4)
    d = rng.normal(0.05, 1.0, 64)
    u = rng.normal(size=64).astype(np.float32)
    mg0 = C.item_margins(d, np.zeros(64, bool), u, pool10())
    assert mg0["SOFT-G"][0] == pytest.approx(mg0["NONE"][0], rel=1e-12, abs=1e-15)
    top = C.CalPool(np.arange(10, dtype=np.float64), 9.0)         # S_cal(tau) = 0 -> flagged weight 0
    F = rng.random(64) < 0.2
    mg = C.item_margins(d, F, u, top)
    assert float(top.survival(9.0)) == 0.0
    assert mg["SOFT-G"][0] == pytest.approx(mg["GM"][0], rel=1e-12, abs=1e-15)


def test_weight_ranges_and_monotonicity():
    rng = np.random.default_rng(5)
    cal_u = rng.normal(size=500).astype(np.float32)
    p = C.CalPool(np.sort(cal_u.astype(np.float64)), float(np.quantile(cal_u, 0.95)))
    u = np.sort(rng.normal(0, 1.5, 300)).astype(np.float32)
    F = np.asarray(u, np.float64) > p.tau
    wg, wa = p.weights_g(u, F), p.weights_a(u)
    assert np.all((wg >= 0) & (wg <= 1)) and np.all(wg[~F] == 1.0)
    assert np.all(np.diff(wg[F]) <= 1e-15)                         # non-increasing in u on the flagged set
    assert np.all(wa >= 1 / (p.n + 1) - 1e-15) and np.all(wa <= 1.0) and np.all(np.diff(wa) <= 1e-15)
    assert float(p.weights_a(np.array([cal_u.max() + 1.0]))[0]) == pytest.approx(1 / (p.n + 1))      # more suspicious than every clean token


def test_ties_and_empty_sets_give_y_zero_and_are_counted():
    p = pool10()
    d = np.array([1.0, -1.0, 0.0, 0.0])
    mg = C.item_margins(d, np.array([0, 0, 0, 0], bool), np.zeros(4, np.float32), p)
    assert mg["NONE"] == (0.0, False)                              # tie: margin 0 -> Y = 0, not empty
    allflag = C.item_margins(d, np.ones(4, bool), np.zeros(4, np.float32), p)
    assert allflag["GM"] == (0.0, True)                            # empty retained set
    assert allflag["TM-G"] == (0.0, True)                          # g = m = 4 -> k = 2 -> empty
    zero_survival = C.CalPool(np.arange(10, dtype=np.float64), 9.0)
    z = C.item_margins(np.array([1.0, 1.0]), np.ones(2, bool), np.array([9.5, 9.7], np.float32), zero_survival)
    assert z["SOFT-G"] == (0.0, True)                              # weight sum 0
    # cell level: Y = 0 and the counts
    cd = _tiny_cell([np.array([1.0, -1.0, 0.0, 0.0])], [np.array([1, 1, 1, 1], bool)], m=4)
    res = C.cell_results(cd, p, "clean", "clean", n_boot=50)
    assert res["arms"]["GM"] == dict(acc=0.0, n_empty=1, n_ties=0)
    assert res["arms"]["NONE"] == dict(acc=0.0, n_empty=0, n_ties=1)


# ------------------------------------------------------------------------------------------------ bootstrap, MDD, readings
def test_mdd_formula_on_known_sd():
    idx = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])
    diff = np.array([1.0, 0.0])
    boots = diff[idx].mean(axis=1)                                 # 1, .5, 0, .5
    iv = C.bootstrap_interval(boots)
    sd = np.sqrt(0.5 / 3)                                          # ddof 1
    assert iv["se_boot"] == pytest.approx(sd)
    assert iv["mdd"] == pytest.approx((1.959964 + 0.841621) * sd) and C.Z_MDD == pytest.approx(2.801585)
    assert iv["lo"] == pytest.approx(np.quantile(boots, 0.025)) and iv["hi"] == pytest.approx(np.quantile(boots, 0.975))


def test_reading_and_counts_against():
    assert C.reading(0.01, 0.1) == "above" and C.reading(-0.1, -0.01) == "below" and C.reading(-0.1, 0.1) == "not_distinguishable" and C.reading(0.0, 0.1) == "not_distinguishable"
    assert C.counts_against("MED", "above", 0.2, 30, 0.2) == "finding_against_the_method"
    assert C.counts_against("TM20", "not_distinguishable", 0.05, 12, 0.5) == "finding_against_added_value"      # n_d >= 10: MDD <= 0.05 inclusive
    assert C.counts_against("TM-G", "not_distinguishable", 0.0501, 12, 0.0) == "uninformative_at_this_n"
    assert C.counts_against("SOFT-G", "above", 0.2, 30, 0.2) == "finding_against_discarding"
    assert C.counts_against("SOFT-A", "not_distinguishable", 0.2, 30, 0.2) == "discarding_and_weighting_not_distinguishable"
    assert C.counts_against("SOFT-G", "identical", 0.0, 0, 0.0074) == "discarding_and_discounting_not_distinguishable_identical"
    assert C.counts_against("SOFT-A", "identical", 0.0, 0, 0.0074) == "discarding_and_weighting_not_distinguishable_identical"
    assert C.counts_against("MED", "below", 0.2, 30, 0.2) == "gate_higher"
    assert C.counts_against("MED", "undefined", float("nan"), 0, float("nan")) == "undefined"


def test_exact_theta_interval_and_reading():
    from scipy.stats import beta
    assert C.exact_reading(4, 0) == "not_distinguishable" and C.exact_reading(5, 0) == "not_distinguishable"
    assert C.exact_reading(6, 0) == "above" and C.exact_reading(0, 6) == "below" and C.exact_reading(0, 0) == "identical"
    assert C.exact_reading(0, 5) == "not_distinguishable" and C.exact_reading(3, 3) == "not_distinguishable"
    assert all(np.isnan(x) for x in C.exact_theta_interval(0, 0))
    assert C.exact_theta_interval(0, 5) == (0.0, pytest.approx(float(beta.ppf(0.975, 1, 5))))      # b = 0: lower 0
    assert C.exact_theta_interval(5, 0) == (pytest.approx(float(beta.ppf(0.025, 5, 1))), 1.0)      # b = n_d: upper 1
    lo, hi = C.exact_theta_interval(6, 0)
    assert lo == pytest.approx(0.025 ** (1 / 6)) and lo > 0.5 and hi == 1.0                         # 0.025^(1/6) = 0.541
    assert 0.025 ** (1 / 5) < 0.5 and C.exact_theta_interval(5, 0)[0] == pytest.approx(0.478, abs=1e-3)
    lo, hi = C.exact_theta_interval(3, 7)                                                           # interior b: both Beta quantiles
    assert lo == pytest.approx(float(beta.ppf(0.025, 3, 8))) and hi == pytest.approx(float(beta.ppf(0.975, 4, 7)))
    assert 0 < lo < 0.3 < hi < 1


def test_discordance_bound_values():
    assert C.discordance_bound(0, 300) == pytest.approx(0.0122, abs=1e-4)
    assert C.discordance_bound(0, 500) == pytest.approx(0.0074, abs=1e-4)
    assert C.discordance_bound(5, 5) == 1.0 and C.discordance_bound(7, 5) == 1.0
    assert C.discordance_bound(15, 500) <= 0.05                                                       # r3 item 4: B <= 0.05 for every n_d <= 15 at n = 500
    assert C.discordance_bound(3, 100) < C.discordance_bound(4, 100)


def test_counts_against_uses_the_bound_below_ten_and_the_mdd_from_ten():
    assert C.counts_against("MED", "identical", 0.0, 0, C.discordance_bound(0, 500)) == "finding_against_added_value"
    assert C.counts_against("TM20", "not_distinguishable", 0.0, 9, 0.06) == "uninformative_at_this_n"        # n_d < 10: B governs; mdd 0.0 is not used
    assert C.counts_against("TM20", "not_distinguishable", 0.06, 12, 0.001) == "uninformative_at_this_n"    # n_d >= 10: MDD governs; B is not used
    assert C.counts_against("MED", "not_distinguishable", 0.06, 12, 0.5) == "uninformative_at_this_n"
    assert C.counts_against("MED", "not_distinguishable", 0.0, 9, 0.05) == "finding_against_added_value"


def test_bootstrap_above_but_exact_not_distinguishable_gives_no_finding_against():
    """b = 4, c = 0 of n = 40: the percentile bootstrap lower bound is above 0 (red-team G3), the exact reading is not_distinguishable."""
    Y = {a: np.zeros(40, np.int8) for a in C.ARMS}
    Y["MED"][:4] = 1
    idx = C.index_matrix(40, C.cell_seed_sequence("jpeg"), 2000)
    row = C.accuracy_contrasts(Y, idx, "P")["MED_minus_GM"]
    assert row["b"] == 4 and row["c"] == 0 and row["ci95"][0] > 0 and row["reading_bootstrap"] == "above"
    assert row["reading"] == "not_distinguishable" and row["mdd_used"] is False
    assert not row["counts_against"].startswith("finding_against_the_method")
    assert row["discordance_bound_B"] > 0.05 and row["counts_against"] == "uninformative_at_this_n"           # B(4, 40) = 0.23
    assert row["theta_ci95_exact"] == list(C.exact_theta_interval(4, 0)) and row["discordance_bound_B"] == pytest.approx(C.discordance_bound(4, 40))
    # six discordant pairs on one side are "above" (exact)
    Y["MED"][:6] = 1
    row6 = C.accuracy_contrasts(Y, idx, "P")["MED_minus_GM"]
    assert row6["reading"] == "above" and row6["counts_against"] == "finding_against_the_method"
    # identical on every item: n_d = 0 and the degenerate mdd of 0.0 is flagged as not used
    ident = C.accuracy_contrasts({a: np.zeros(40, np.int8) for a in C.ARMS}, idx, "P")["TM20_minus_GM"]
    assert ident["reading"] == "identical" and ident["n_d"] == 0 and ident["mdd"] == 0.0 and ident["mdd_used"] is False
    assert ident["counts_against"] == "uninformative_at_this_n"                                      # B(0, 40) = 0.088 > 0.05
    Y500 = {a: np.zeros(500, np.int8) for a in C.ARMS}
    r500 = C.accuracy_contrasts(Y500, C.index_matrix(500, C.cell_seed_sequence("jpeg"), 50), "P")
    assert r500["MED_minus_GM"]["counts_against"] == "finding_against_added_value" and r500["SOFT-G_minus_GM"]["counts_against"] == "discarding_and_discounting_not_distinguishable_identical"
    assert r500["MED_minus_NONE"].get("counts_against") is None                                       # only "minus GM" carries a counts_against label



def test_seed_slots_independent_of_absent_cells_and_equal_the_spawn_child():
    a = C.cell_seed_sequence("splice")
    b = C.cell_seed_sequence("splice")
    assert a.spawn_key == b.spawn_key == (32, 3)
    assert [C.cell_seed_sequence(s).spawn_key for s in C.SEED_SLOTS] == [(32, i) for i in range(6)]
    # equals the child that an append of `tier3_fusion` at position 32 of seeds.ANALYSES would give (A3.7)
    child32 = np.random.SeedSequence(seeds.ROOT_SEED).spawn(33)[32]
    assert child32.spawn_key == C.SEED_SPAWN_KEY and child32.entropy == seeds.ROOT_SEED
    assert np.array_equal(child32.generate_state(4), np.random.SeedSequence(seeds.ROOT_SEED, spawn_key=(32,)).generate_state(4))
    m1 = C.index_matrix(7, C.cell_seed_sequence("jpeg"), 100)
    assert np.array_equal(m1, C.index_matrix(7, C.cell_seed_sequence("jpeg"), 100))
    assert not np.array_equal(m1, C.index_matrix(7, C.cell_seed_sequence("noise"), 100))


# ------------------------------------------------------------------------------------------------ trimming control on d
def test_d_control_by_hand_and_drops():
    # item 0: g = 4 flags on the four lowest; GM keeps [1,2,3,4,5]; TM-G trims k = 2 per tail of the 8 values; NONE keeps all.
    d0 = np.array([-10, -2, -1, 1, 2, 3, 4, 5], np.float64)
    F0 = np.array([1, 1, 1, 1, 0, 0, 0, 0], bool)
    dv = C.retained_d(d0, F0)
    gm = np.array([2, 3, 4, 5.0])
    tmg = np.array([-1, 1, 2, 3.0])                                 # sorted[2:6]
    assert dv["GM"] == pytest.approx(gm.mean() / gm.std(ddof=1))
    assert dv["TM-G"] == pytest.approx(tmg.mean() / tmg.std(ddof=1))
    assert dv["NONE"] == pytest.approx(d0.mean() / d0.std(ddof=1))
    tm20 = np.sort(d0)[1:7]
    assert dv["TM20"] == pytest.approx(tm20.mean() / tm20.std(ddof=1))
    # |R| < 2 and sd = 0 give NaN (dropped)
    assert np.isnan(C.retained_d(np.array([1.0, 2.0, 3.0]), np.array([1, 1, 0], bool))["GM"])
    assert np.isnan(C.retained_d(np.array([1.0, 1.0, 1.0]), np.zeros(3, bool))["NONE"])
    # contrast: two valid items and one dropped
    dvals = {"NONE": np.array([1.0, 1.0, 1.0]), "GM": np.array([1.0, 2.0, np.nan]), "TM-G": np.array([2.0, 5.0, 1.0]), "TM20": np.array([1.0, 2.0, 3.0])}
    idx = np.tile(np.arange(3), (20, 1))                           # every resample is the sample itself
    out = C.d_control(dvals, idx)
    c = out["contrasts"]["TM-G_minus_GM"]
    assert c["n_valid"] == 2 and c["n_dropped"] == 1 and c["mean_diff"] == pytest.approx(((2 - 1) + (5 - 2)) / 2)
    assert c["ci95"] == pytest.approx([2.0, 2.0]) and c["reading"] == "above"
    assert out["per_arm"]["GM"]["n_dropped"] == 1 and out["per_arm"]["GM"]["mean_d"] == pytest.approx(1.5)
    assert "MED" not in out["per_arm"] and "SOFT-G" not in out["per_arm"]
    # r3 (A4.1.12 item 7): every valid paired difference exactly 0 -> "identical_on_every_item"; the other contrast keeps the bootstrap reading
    same = {"NONE": np.ones(3), "GM": np.array([1.0, 2.0, np.nan]), "TM-G": np.array([1.0, 2.0, 5.0]), "TM20": np.array([2.0, 3.0, 4.0])}
    o2 = C.d_control(same, idx)["contrasts"]
    assert o2["TM-G_minus_GM"]["reading"] == "identical_on_every_item" and o2["TM-G_minus_GM"]["n_valid"] == 2
    assert o2["TM20_minus_GM"]["reading"] == "above"


# ------------------------------------------------------------------------------------------------ cells on tiny fixtures
def _row_for(delta, flag):
    ev = lambda inc: pipeline.compact(evidence.evidence_from_delta(delta, inc))        # noqa: E731
    return dict(img={"none": ev(None), f"gate{AK}": ev(~flag)}, gate={AK: dict(n_flag=int(flag.sum()))})


def _tiny_cell(deltas, flags, m=None, stored=None):
    deltas = [np.asarray(d, np.float32) for d in deltas]
    flags = [np.asarray(f, bool) for f in flags]
    return C.CellData("x", list(range(len(deltas))), np.stack(deltas), np.stack(flags), np.zeros((len(deltas), deltas[0].size), np.float32),
                      stored if stored is not None else [_row_for(d, f) for d, f in zip(deltas, flags)], {})


def test_consistency_gate_passes_and_stops_on_injected_mismatch():
    rng = np.random.default_rng(6)
    ds = [rng.normal(0.1, 1, 32) for _ in range(3)]
    fs = [rng.random(32) < 0.2 for _ in range(3)]
    cd = _tiny_cell(ds, fs)
    assert C.consistency_problems(cd) == []
    for mut in ("y_none", "mean_gm", "n_flag"):
        bad = _tiny_cell(ds, fs)
        st = bad.stored[1]
        if mut == "y_none":
            st["img"]["none"]["y"] = 1 - st["img"]["none"]["y"]
        elif mut == "mean_gm":
            st["img"][f"gate{AK}"]["mean"] += 1e-6                  # beyond 1e-9
        else:
            st["gate"][AK]["n_flag"] += 1
        probs = C.consistency_problems(bad)
        assert len(probs) == 1 and "idx 1" in probs[0]
    ok = _tiny_cell(ds, fs)
    ok.stored[0]["img"]["none"]["mean"] += 1e-12                     # within 1e-9: no problem
    assert C.consistency_problems(ok) == []
    del ok.stored[2]["gate"]
    assert "n_flag" in C.consistency_problems(ok)[0]


# ------------------------------------------------------------------------------------------------ a full synthetic run directory
CELLS = ("clean", "jpeg10", "noise0.1", "splice128", "patch", "swap")


def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "-C", str(cwd), *args], capture_output=True, text=True, check=True)


def make_world(tmp, n_items=12, n_cal=30, seed=0, commit=True, rule="R1", cells=CELLS):
    """runs/P2-GATE-M2 (calibration), -M3 (family.json, ps_frozen.json), -M4 (items.jsonl, arrays, analysis.json) in a temporary git repository."""
    tmp = Path(tmp)
    rng = np.random.default_rng(seed)
    runs = tmp / "runs"
    m2, m3, m4 = runs / "P2-GATE-M2", runs / "P2-GATE-M3", runs / "P2-GATE-M4"
    for d in (m2 / "arrays", m3, m4 / "arrays"):
        d.mkdir(parents=True, exist_ok=True)
    U, rows2, ids = [], [], []
    for i in range(n_cal):
        B = rng.normal(-3, 1, M).astype(np.float32)
        D = rng.normal(-3, 0.3, M).astype(np.float32)
        np.savez(m2 / "arrays" / f"item{i:04d}.npz", B=B, D=D)
        U.append(scores.suspicion_q(B, D))
        ids.append(1000 + i)
        rows2.append(dict(idx=i, gid=1000 + i))
    (m2 / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows2), encoding="utf8")
    thr = fit_threshold.fit_from_arrays(U, ids, "q")
    (m2 / "threshold.json").write_text(json.dumps(thr), encoding="utf8")
    tau = float(thr["thresholds"][AK]["tau"])
    fam_cells = [c for c in cells if c in ("jpeg10", "noise0.1", "splice128")]
    corr = {"jpeg10": "jpeg", "noise0.1": "noise", "splice128": "splice"}
    (m3 / "family.json").write_text(json.dumps(dict(endpoint="d", family=[dict(corruption=corr[c], key=c) for c in fam_cells], n_rule=dict(rule=rule))), encoding="utf8")
    (m3 / "ps_frozen.json").write_text(json.dumps(dict(params=dict(sanity_order=["patch", "swap"]))), encoding="utf8")
    rows4 = []
    for i in range(n_items):
        arrs, row = {}, dict(idx=i, gid=5000 + i, conds={})
        for c in cells:
            B = rng.normal(-3, 1, M).astype(np.float32)
            D = rng.normal(-3, 0.3, M).astype(np.float32)
            u = scores.suspicion_q(B, D)
            flag = np.asarray(u, np.float64) > tau
            delta = (rng.normal(0.0, 1.0, M) + rng.normal(0.01, 0.03) - 1.5 * flag).astype(np.float32)      # item mean near 0 so that Y varies; flagged tokens carry negative evidence
            arrs.update({f"{c}_delta": delta, f"{c}_B": B, f"{c}_D": D, f"{c}_flag{AK}": flag})
            row["conds"][c] = _row_for(delta, flag)
        np.savez(m4 / "arrays" / f"item{i:04d}.npz", **arrs)
        rows4.append(row)
    (m4 / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows4), encoding="utf8")
    per = {corr[c]: dict(tested=True, b=3, c=1, n_d=4, n=n_items, acc_a=0.6, acc_b=0.5, delta=0.1, ci95=[0.0, 0.2], p=0.04, p_mid=0.03, p_holm=0.04, label="P") for c in fam_cells}
    analysis = dict(n_items=n_items, family=fam_cells, rule=rule, primary=dict(per_corruption=per), secondary_y=dict(per_corruption=per) if rule == "R3" else None)
    (m4 / "analysis.json").write_text(json.dumps(analysis), encoding="utf8")
    if commit:
        _git(tmp, "init", "-q")
        _git(tmp, "add", "runs/P2-GATE-M4/analysis.json")
        _git(tmp, "commit", "-q", "-m", "analysis")
    return tmp


@pytest.fixture
def world(tmp_path, monkeypatch):
    make_world(tmp_path)
    monkeypatch.setattr(common, "RUNS", tmp_path / "runs")
    return tmp_path


def _run_cli(*extra):
    return C.main(["--run-id", "P2-GATE-M4", "--cal-run", "P2-GATE-M2", *extra])


def _walk_keys(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk_keys(v)


def test_end_to_end_cells_arms_and_no_p_value(world, capsys):
    assert _run_cli() == 0
    out = json.loads((world / "runs" / "P2-GATE-M4" / C.OUT_NAME).read_text(encoding="utf8"))
    assert list(out["cells"]) == ["jpeg10", "noise0.1", "splice128"] and out["clean"]["kind"] == "clean" and list(out["ps_cells"]) == ["patch", "swap"]
    jp = out["cells"]["jpeg10"]
    assert jp["n"] == 12 and jp["seed_slot"] == "jpeg" and set(jp["arms"]) == set(C.ARMS)
    assert len(jp["contrasts"]) == 10 and set(jp["contrasts"]) == {f"{k}_minus_{r}" for k in C.COMPARATORS for r in ("GM", "NONE")}
    assert len(jp["d_control"]["contrasts"]) == 2
    first = jp["contrasts"]["MED_minus_GM"]
    assert {"n", "acc_comparator", "acc_reference", "b", "c", "n_d", "diff", "ci95", "mdd", "reading", "counts_against"} <= set(first)
    assert "counts_against" not in out["clean"]["contrasts"]["MED_minus_GM"] and "counts_against" not in out["ps_cells"]["patch"]["contrasts"]["MED_minus_GM"]
    assert out["clean"]["seed_slot"] == "clean" and out["ps_cells"]["swap"]["seed_slot"] == "swap"
    assert jp["gm_minus_none_quoted"]["b"] == 3 and "p" not in jp["gm_minus_none_quoted"] and "p_holm" not in jp["gm_minus_none_quoted"]
    allc = list(out["cells"].values()) + [out["clean"]] + list(out["ps_cells"].values())
    assert any(0 < c["arms"]["NONE"]["acc"] < 1 for c in allc) and any(k["n_d"] > 0 for c in allc for k in c["contrasts"].values())      # the fixture is not degenerate
    assert out["multiplicity"] == dict(n_intervals=6 * 12, statement="no multiplicity adjustment (SAP 7)")
    assert out["seed"]["documented_fallback"] and out["seed"]["spawn_key"] == [32] and out["seed"]["root"] == 20261028
    # exploratory, no p-value anywhere in the output
    bad = [k for k in _walk_keys(out) if re.search(r"(^p$|^p_|_p$|pval|p-val|p_value)", k.lower())]
    assert bad == []
    assert "no p-value" in out["label"] and "Tier 3" in out["label"]
    stdout = capsys.readouterr().out
    assert "no multiplicity adjustment (SAP 7)" in stdout


def test_module_imports_and_calls_no_test_function():
    import ast
    tree = ast.parse((ROOT / "exp_p2" / "gate" / "tier3_fusion.py").read_text(encoding="utf8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names} | {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert {m for m in imported if m and m.split(".")[0] == "scipy"} <= {"scipy.stats"}
    scipy_names = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module == "scipy.stats" for a in n.names}
    assert scipy_names == {"beta"}                                  # A4.1.12 item 1: only the Clopper-Pearson quantiles, no test function
    called = {n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not {c for c in called if re.search(r"mcnemar|wilcoxon|holm|ttest|permutation|report_test|binomtest|fisher|\bcdf\b|\bsf\b", c, flags=re.I)}


def test_arm_values_in_the_run_match_a_direct_recomputation(world):
    res = C.run("P2-GATE-M4", "P2-GATE-M2")
    run_dir = world / "runs" / "P2-GATE-M4"
    thr = json.loads((world / "runs" / "P2-GATE-M2" / "threshold.json").read_text(encoding="utf8"))
    pool, _ = C.build_cal_pool(world / "runs" / "P2-GATE-M2", thr)
    rows, _ = analysis_m4.load_items(run_dir)
    cd = C.load_cell(run_dir, rows, "noise0.1")
    Y = {a: [] for a in C.ARMS}
    for i in range(len(cd.idx)):
        mg = C.item_margins(cd.delta[i], cd.flag[i], cd.u[i], pool)
        for a in C.ARMS:
            Y[a].append(int(mg[a][0] > 0 and not mg[a][1]))
    cell = res["cells"]["noise0.1"]
    for a in C.ARMS:
        assert cell["arms"][a]["acc"] == pytest.approx(np.mean(Y[a]))
    diff = np.array(Y["TM20"]) - np.array(Y["GM"])
    c = cell["contrasts"]["TM20_minus_GM"]
    assert c["diff"] == pytest.approx(diff.mean()) and c["b"] == int((diff == 1).sum()) and c["c"] == int((diff == -1).sum()) and c["n_d"] == c["b"] + c["c"]
    # paired: the stored NONE and GM y of the rows are reproduced by the NONE and GM arms (consistency gate)
    assert [r["conds"]["noise0.1"]["img"]["none"]["y"] for r in rows] == Y["NONE"]
    assert [r["conds"]["noise0.1"]["img"][f"gate{AK}"]["y"] for r in rows] == Y["GM"]


def test_bootstrap_determinism_and_byte_identical_recomputation(world):
    a = C.dumps(C.run("P2-GATE-M4", "P2-GATE-M2"))
    b = C.dumps(C.run("P2-GATE-M4", "P2-GATE-M2"))
    assert a == b


def test_one_index_matrix_per_cell_is_shared_by_arms_and_contrasts():
    rng = np.random.default_rng(7)
    n = 9
    cd = _tiny_cell([rng.normal(0.1, 1, 40) for _ in range(n)], [rng.random(40) < 0.15 for _ in range(n)])
    cd.u = rng.normal(size=cd.delta.shape).astype(np.float32)
    p = pool10()
    r1 = C.cell_results(cd, p, "P", "jpeg", n_boot=300)
    r2 = C.cell_results(cd, p, "P", "jpeg", n_boot=300)
    assert C.dumps(r1) == C.dumps(r2)                               # same seed slot: identical (NaN-safe: n_d = 0 gives a NaN exact interval)
    r3 = C.cell_results(cd, p, "P", "noise", n_boot=300)             # another slot: the resamples differ, the point estimates do not
    assert r3["contrasts"]["MED_minus_GM"]["diff"] == r1["contrasts"]["MED_minus_GM"]["diff"]
    assert any(r3["contrasts"][k]["ci95"] != r1["contrasts"][k]["ci95"] or r3["contrasts"][k]["se_boot"] != r1["contrasts"][k]["se_boot"] for k in r1["contrasts"])


def test_slot_of_a_cell_does_not_change_when_another_cell_is_absent(tmp_path, monkeypatch):
    full = make_world(tmp_path / "a", seed=11)
    part = make_world(tmp_path / "b", seed=11, cells=("clean", "jpeg10", "swap"))
    monkeypatch.setattr(common, "RUNS", full / "runs")
    r_full = C.run("P2-GATE-M4", "P2-GATE-M2")
    monkeypatch.setattr(common, "RUNS", part / "runs")
    r_part = C.run("P2-GATE-M4", "P2-GATE-M2")
    assert list(r_part["cells"]) == ["jpeg10"] and list(r_part["ps_cells"]) == ["swap"] and r_part["not_run_ps_cells"] == ["patch"]
    # same draws in a world whose other cells differ: the swap slot is 5 in both, and the jpeg slot is 1 in both
    assert r_full["ps_cells"]["swap"]["seed_slot_index"] == r_part["ps_cells"]["swap"]["seed_slot_index"] == 5
    assert r_full["cells"]["jpeg10"]["seed_slot_index"] == r_part["cells"]["jpeg10"]["seed_slot_index"] == 1


def test_incomplete_items_are_excluded_with_a_reason_for_every_arm(world, monkeypatch):
    m4 = world / "runs" / "P2-GATE-M4"
    p = m4 / "arrays" / "item0003.npz"
    with np.load(p) as z:
        arrs = {k: z[k] for k in z.files}
    arrs["jpeg10_delta"] = arrs["jpeg10_delta"].copy()
    arrs["jpeg10_delta"][5] = np.nan
    del arrs["noise0.1_flag0.05"]
    arrs["splice128_B"] = arrs["splice128_B"].copy()
    arrs["splice128_B"][0] = np.inf
    np.savez(p, **arrs)
    (m4 / "arrays" / "item0004.npz").unlink()
    res = C.run("P2-GATE-M4", "P2-GATE-M2")
    assert res["cells"]["jpeg10"]["n"] == 10 and res["cells"]["jpeg10"]["n_excluded"] == 2        # idx 3 (NaN in delta), idx 4 (npz missing)
    assert res["cells"]["jpeg10"]["excluded"]["jpeg10_delta is not 1024 finite values"] == dict(n=1, idx=[3])
    assert res["cells"]["noise0.1"]["n"] == 10 and res["cells"]["noise0.1"]["n_excluded"] == 2
    assert res["clean"]["n"] == 11 and res["clean"]["excluded"] == {"npz missing": dict(n=1, idx=[4])}
    assert any("finite" in k for k in res["cells"]["splice128"]["excluded"])
    assert res["cells"]["jpeg10"]["n"] == len(set(range(12)) - {3, 4})                              # one item set for every arm


def test_injected_mismatch_stops_the_run_with_exit_3(world, capsys):
    m4 = world / "runs" / "P2-GATE-M4"
    rows = [json.loads(l) for l in (m4 / "items.jsonl").read_text(encoding="utf8").splitlines()]
    rows[2]["conds"]["jpeg10"]["gate"][AK]["n_flag"] += 1
    (m4 / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf8")
    assert _run_cli() == 3
    assert "jpeg10 idx 2" in capsys.readouterr().err
    assert not (m4 / C.OUT_NAME).exists()
    with pytest.raises(C.ConsistencyError):
        C.run("P2-GATE-M4", "P2-GATE-M2")


# ------------------------------------------------------------------------------------------------ refusal and write-once
def test_refuses_without_analysis_json(tmp_path, monkeypatch, capsys):
    make_world(tmp_path, commit=False)
    (tmp_path / "runs" / "P2-GATE-M4" / "analysis.json").unlink()
    monkeypatch.setattr(common, "RUNS", tmp_path / "runs")
    assert _run_cli() == 2
    assert "analysis.json" in capsys.readouterr().err


def test_refuses_when_analysis_json_is_not_committed(tmp_path, monkeypatch, capsys):
    make_world(tmp_path, commit=False)
    _git(tmp_path, "init", "-q")                                    # untracked file
    monkeypatch.setattr(common, "RUNS", tmp_path / "runs")
    assert _run_cli() == 2
    assert "not tracked" in capsys.readouterr().err
    _git(tmp_path, "add", "runs/P2-GATE-M4/analysis.json")          # staged, not committed
    assert _run_cli() == 2
    assert "uncommitted" in capsys.readouterr().err
    assert not (tmp_path / "runs" / "P2-GATE-M4" / C.OUT_NAME).exists()


def test_refuses_when_analysis_json_has_changed_since_its_commit(world, capsys):
    ap = world / "runs" / "P2-GATE-M4" / "analysis.json"
    ap.write_text(ap.read_text(encoding="utf8") + " ", encoding="utf8")
    assert _run_cli() == 2
    assert "uncommitted" in capsys.readouterr().err


def test_refuses_when_the_p_section_is_missing(tmp_path, monkeypatch, capsys):
    make_world(tmp_path, commit=False)
    ap = tmp_path / "runs" / "P2-GATE-M4" / "analysis.json"
    ap.write_text(json.dumps(dict(n_items=12, family=["jpeg10", "noise0.1", "splice128"])), encoding="utf8")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "runs/P2-GATE-M4/analysis.json")
    _git(tmp_path, "commit", "-q", "-m", "x")
    monkeypatch.setattr(common, "RUNS", tmp_path / "runs")
    assert _run_cli() == 2
    assert "P section" in capsys.readouterr().err


def test_refusal_happens_before_the_m4_rows_are_opened(tmp_path, monkeypatch):
    make_world(tmp_path, commit=False)
    monkeypatch.setattr(common, "RUNS", tmp_path / "runs")
    opened = []
    real = common.read_jsonl
    monkeypatch.setattr(common, "read_jsonl", lambda p: (opened.append(Path(p)), real(p))[1])
    assert _run_cli() == 2
    assert opened == []                                             # no items.jsonl (M4 or M2) was read


def test_refuses_on_item_count_family_or_calibration_mismatch(world, capsys):
    m4, m2 = world / "runs" / "P2-GATE-M4", world / "runs" / "P2-GATE-M2"
    rows = (m4 / "items.jsonl").read_text(encoding="utf8").splitlines()
    (m4 / "items.jsonl").write_text("\n".join(rows[:-1]) + "\n", encoding="utf8")           # analysis.json analysed 12, 11 rows now
    assert _run_cli() == 2 and "analysed" in capsys.readouterr().err
    (m4 / "items.jsonl").write_text("\n".join(rows) + "\n", encoding="utf8")
    cal_rows = (m2 / "items.jsonl").read_text(encoding="utf8").splitlines()
    (m2 / "items.jsonl").write_text("\n".join(cal_rows[:-1]) + "\n", encoding="utf8")       # id hash no longer matches threshold.json
    assert _run_cli() == 2 and "ids_hash" in capsys.readouterr().err


def test_write_once(world, capsys):
    out = world / "runs" / "P2-GATE-M4" / C.OUT_NAME
    assert _run_cli() == 0
    first = out.read_bytes()
    assert _run_cli() == 2
    assert "write-once" in capsys.readouterr().err
    assert out.read_bytes() == first
    assert not list(out.parent.glob("tier3_fusion.json.prev-*"))      # no forced rewrite exists


def test_r3_note_and_quote_come_from_the_y_contrast(tmp_path, monkeypatch):
    make_world(tmp_path, rule="R3")
    monkeypatch.setattr(common, "RUNS", tmp_path / "runs")
    res = C.run("P2-GATE-M4", "P2-GATE-M2")
    assert res["rule"] == "R3" and "not on P's R3 endpoint" in res["r3_note"]
    assert "secondary_y" in res["cells"]["jpeg10"]["gm_minus_none_quoted"]["source"]
    assert len(res["cells"]["jpeg10"]["d_control"]["contrasts"]) == 2


def test_cal_pool_matches_fit_threshold_inputs(world):
    thr = json.loads((world / "runs" / "P2-GATE-M2" / "threshold.json").read_text(encoding="utf8"))
    pool, info = C.build_cal_pool(world / "runs" / "P2-GATE-M2", thr)
    assert pool.n == 30 * M == info["n_cal_tokens"] and info["n_cal_items"] == 30 and len(info["m2_npz_sha256"]) == 30
    assert np.all(np.diff(pool.u) >= 0)
    assert pool.tau == thr["thresholds"][AK]["tau"]
    # S_cal(tau) is about alpha (CRC on the pool itself): the share of calibration tokens above tau
    assert float(pool.survival(pool.tau)) <= config.ALPHA_PRIMARY + 1.0 / pool.n
