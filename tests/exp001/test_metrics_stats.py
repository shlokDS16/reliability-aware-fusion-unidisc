"""Metric pipeline (7.1-7.4, 10.1-10.2) and H-A / H-C statistics (2, 10.3) on synthetic data."""
import numpy as np
import pytest

import metrics as M
import hastats as H


def synth(n=120, d=32, signal=0.6, seed=0):
    g = np.random.default_rng(seed)
    z = g.standard_normal((n, d))
    img = z + 0.5 * g.standard_normal((n, d))
    txt = signal * z + g.standard_normal((n, d))
    img /= np.linalg.norm(img, axis=1, keepdims=True)
    txt /= np.linalg.norm(txt, axis=1, keepdims=True)
    return img, txt


def test_lift_matches_definition_by_loops():
    img, txt = synth(30)
    S = M.sim_matrix(img, txt)
    n = 30
    exp = []
    for i in range(n):
        c = S[i, i]
        b = 0.5 * (np.mean([S[j, i] for j in range(n) if j != i]) + np.mean([S[i, j] for j in range(n) if j != i]))
        exp.append(100 * (c - b))
    assert np.allclose(M.lift(S), exp, atol=1e-12)
    C, B = M.lift_terms(S)
    assert np.allclose(M.psi(S), 100 * (C - 2 * B))


def test_nc5_permuted_pairs_lift_near_zero_and_signal_positive():
    img, txt = synth(400, signal=0.8)
    S = M.sim_matrix(img, txt)
    assert M.lift(S).mean() > 1.0
    g = np.random.default_rng(1)
    means = [M.lift(M.sim_matrix(img, txt[g.permutation(400)])).mean() for _ in range(60)]
    assert abs(np.mean(means)) < 0.3                       # unbiased under pair permutation (single permutations carry noise)
    Sp = M.sim_matrix(img, txt[g.permutation(400)])
    th = M.paired_bootstrap(Sp, None, B=300, seed=2)
    lo, hi = M.percentile_ci(th, 0.95)
    assert lo < 0 < hi


def test_bootstrap_se_matches_sampling_sd():
    sds = []
    for s in range(60):
        img, txt = synth(150, seed=100 + s)
        sds.append(M.lift(M.sim_matrix(img, txt)).mean())
    img, txt = synth(150, seed=999)
    th = M.paired_bootstrap(M.sim_matrix(img, txt), None, B=400, seed=0)
    assert abs(th.std() / np.std(sds) - 1.0) < 0.35


def test_paired_contrast_identical_arms_is_zero():
    img, txt = synth(80)
    S = M.sim_matrix(img, txt)
    th = M.paired_bootstrap(S, S, B=50, seed=1)
    assert np.abs(th).max() < 1e-12 and M.point_contrast(S, S) == 0


def test_p_value_rule_and_rerun():
    th = np.concatenate([np.full(900, 1.0), np.full(100, -1.0)])
    assert M.two_sided_p(th) == pytest.approx(2 * (1 + 100) / 1001, rel=1e-3)
    assert M.two_sided_p(np.zeros(10)) == 1.0
    assert M.needs_rerun(0.0125, 0.0125, 10000)
    assert not M.needs_rerun(0.5, 0.0125, 10000)


def test_holm_and_fixed_sequence_and_classes():
    h = M.holm({"a": 0.001, "b": 0.02, "c": 0.04, "d": 0.5})
    assert h["a"] == (0.004, True) and h["b"][1] is False or h["b"][0] == pytest.approx(0.06)
    fs = M.fixed_sequence(0.03, {"a": 0.001, "b": 0.02, "c": 0.04, "d": 0.5})
    assert fs["primary"][1] and fs["secondary_label"] == "confirmatory"
    fs2 = M.fixed_sequence(0.2, {"a": 0.001, "b": 0.02, "c": 0.04, "d": 0.5})
    assert fs2["secondary_label"] == "exploratory" and not fs2["secondary"]["a"][1]
    assert M.outcome_class(1.2, 0.3, 2.0, 0.01) == "positive (at or above the MEI)"
    assert M.outcome_class(0.5, 0.1, 0.9, 0.04) == "positive"
    assert M.outcome_class(-1.2, -2.0, -0.4, 0.01) == "reversed"
    assert M.outcome_class(0.1, -0.5, 0.7, 0.6) == "null"
    assert M.outcome_class(0.1, -1.5, 1.7, 0.6) == "inconclusive"


def test_derangement_and_vlift():
    for seed in (0, 1, 2):
        p = M.derangement(50, seed)
        assert sorted(p) == list(range(50)) and not np.any(p == np.arange(50))
    assert np.allclose(M.vlift(np.array([1.0, 0.5]), np.array([0.2, 0.1]), np.array([0.4, 0.3])), [0.7, 0.3])


def test_reading_conditions_and_guardrails():
    img, txt = synth(100, signal=0.9, seed=5)
    S = M.sim_matrix(img, txt)
    Sp = M.sim_matrix(img, txt * 0.5 + 0.0)
    rc = M.reading_conditions(S, S, Sp, Sp, np.random.default_rng(0).normal(0.3, 0.1, 500), B=60, seed=3)
    assert rc["R-a"]["pass"] is False and rc["R-b"]["pass"] is False      # identical arms: no effect
    assert rc["R-c"]["pass"] is True
    a = dict(comp_len=9, img_cos=0.50, cap_cos=0.60, empty_rate=0.0, trunc77_rate=0.0, clipiqa=0.5, kid=0.01, presence=0.6)
    j = dict(a)
    assert M.guardrails(a, j, 0.1, 0.005)["all_pass"]
    a2 = dict(a, img_cos=0.52)
    g = M.guardrails(a2, j, 0.1, 0.005)
    assert not g["ii_img_diversity"] and not g["all_pass"]


def test_mean_pairwise_cos():
    E = np.eye(4)
    assert M.mean_pairwise_cos(E) == 0.0
    assert M.mean_pairwise_cos(np.ones((4, 3)) / np.sqrt(3)) == pytest.approx(1.0)


# ----------------------------------------------------------------------------------------------------------------- H-C
def test_rho_strat_exact_null_matches_card():
    p, _ = H.rho_strat_exact_p(0.452)
    assert p == pytest.approx(0.0479, abs=6e-4)                  # card: P = 0.0479 at 0.452
    p05, _ = H.rho_strat_exact_p(0.5)
    assert p05 == pytest.approx(0.031, abs=2e-3)                  # support rule binds (null probability 0.031)
    p440, _ = H.rho_strat_exact_p(0.440)
    assert p440 == pytest.approx(0.0528, abs=1e-3)
    crit, pc = H.rho_strat_critical(0.05, 2)
    assert crit == pytest.approx(0.452, abs=1e-3) and pc <= 0.05
    c1, p1 = H.rho_strat_critical(0.05, 1)
    assert c1 == pytest.approx(0.643, abs=1e-3) and p1 == pytest.approx(0.048, abs=1e-3)


def test_spearman_and_rho_strat():
    x = np.arange(8.0)
    assert H.spearman(x, x) == pytest.approx(1.0) and H.spearman(x, -x) == pytest.approx(-1.0)
    r = H.rho_strat({"k0": x, "k+": x}, {"k0": x, "k+": x * 2})
    assert r == pytest.approx(1.0)
    d = H.hc_decision(1.0)
    assert d["supported"] and d["p_exact"] < 1e-4


# ----------------------------------------------------------------------------------------------------------------- H-A
def make_obs(true_ratio, comp_shift, n_traj=200, seed=0):
    """Observations with three strata whose mean value differs by type, the early probes dominated by function words when
    comp_shift > 0 (a composition confound): raw ratio differs from the standardised one."""
    g = np.random.default_rng(seed)
    base = {"noun": 3.0, "other": 2.0, "function": 0.5}
    tr, gp, st, val = [], [], [], []
    for t in range(n_traj):
        for grp in (0, 1):
            for _ in range(2):
                p_noun = 0.35 - (comp_shift if grp == 0 else 0)
                u = g.random()
                s = "noun" if u < p_noun else ("other" if u < p_noun + 0.35 else "function")
                v = base[s] * (true_ratio if grp == 0 else 1.0) * g.lognormal(0, 0.25)
                tr.append(t); gp.append(grp); st.append(s); val.append(v)
    return np.array(tr), np.array(gp), np.array(st), np.array(val)


def test_standardised_ratio_removes_composition_confound():
    tr, gp, st, val = make_obs(1.0, comp_shift=0.2)
    raw = val[gp == 0].mean() / val[gp == 1].mean()
    r, info = H.standardised_ratio(tr, gp, st, val)
    assert raw < 0.9 and abs(r - 1.0) < 0.12            # raw ratio is biased low by composition, standardised is near 1
    tr, gp, st, val = make_obs(2.0, comp_shift=0.0, seed=1)
    r, info = H.standardised_ratio(tr, gp, st, val)
    assert abs(r - 2.0) < 0.2


def test_thin_stratum_merge_and_inconclusive_rule():
    omega = {"noun": 0.05, "other": 0.6, "function": 0.35}
    assert H.merge_thin_strata(omega) == {"noun": "other", "other": "other", "function": "function"}
    tr = np.arange(30)
    gp = np.array([0] * 15 + [1] * 15)
    st = np.array(["noun"] * 10 + ["other"] * 20)
    r, info = H.standardised_ratio(tr, gp, st, np.ones(30))
    assert H.thin_stratum_inconclusive(info) or r is None


def test_bootstrap_and_decision_supported_negative_h_guard():
    tr, gp, st, val = make_obs(2.5, 0.0, seed=2)
    r, info = H.standardised_ratio(tr, gp, st, val)
    reps, rd = H.bootstrap_ratio(tr, gp, st, val, info["omega"], info["mapping"], B=300, seed=1)
    lab, lim = H.decide_direction(reps, reps, reps, info, h=1.0, noun_share_diff=0.0)
    assert lab == "supported" and lim["lo95_pooled"] >= 1.5
    tr, gp, st, val = make_obs(1.0, 0.0, seed=3)
    r, info = H.standardised_ratio(tr, gp, st, val)
    reps, rd = H.bootstrap_ratio(tr, gp, st, val, info["omega"], info["mapping"], B=300, seed=1)
    lab, _ = H.decide_direction(reps, reps, reps, info, h=1.0, noun_share_diff=0.0)
    assert lab in ("negative", "reversed")
    lab, _ = H.decide_direction(reps, reps, reps, info, h=1.5, noun_share_diff=0.0)      # h outside [0.85, 1.18] blocks Negative
    assert lab == "inconclusive (composition)"
    lab, _ = H.decide_direction(reps, reps, None, info, h=1.0, noun_share_diff=0.0)       # without R_Q2 there is no Negative
    assert lab == "inconclusive"


def test_condition_r_table_and_guard():
    assert H.condition_r_table(1.1, 2.0).startswith("front-loaded")
    assert H.condition_r_table(0.9, 1.2).startswith("front-loading")
    assert H.condition_r_table(0.9, 1.4).startswith("not distinguishable")
    g = H.composition_guard(2.0, 2.0, 0.4, 0.1)
    assert g["h_ok"] and not g["noun_ok"]


def test_frozen_analysis_end_to_end_scrambled_and_deterministic():
    import frozen_analysis as FA
    arms = ("J", "Alt", "DA", "DA-low", "TFJ")
    data = FA.synthetic(n=70, effect=0.6)
    r1 = FA.run(data, arms, FA.CONTRASTS, B=120, scr=True)
    r2 = FA.run(data, arms, FA.CONTRASTS, B=120, scr=True)
    assert FA.digest(r1) == FA.digest(r2)                                       # deterministic, hashable
    for a in arms:
        assert abs(r1["arms"][a]["lift"]) < 4.0                                 # scrambled labels: no signal (loose, n = 70)
    unscr = FA.run(data, arms, FA.CONTRASTS, B=120, scr=False)
    assert unscr["arms"]["DA"]["lift"] > unscr["arms"]["J"]["lift"]
    assert "H-B1" in r1["contrasts"] and r1["fixed_sequence"]["secondary_label"] in ("confirmatory", "exploratory")
    assert "reading_conditions" in r1


def test_pilot_analysis_firewall_and_sizing_rule():
    import pilot_analysis as PA
    import frozen_analysis as FA
    from scipy import stats as _st
    s_up = 5.66 * np.sqrt(63 / _st.chi2.ppf(0.20, 63))            # planning sigma_d 5.66 -> sigma_d,up 6.147 (chi-square factor 1.0861)
    assert abs(np.sqrt(63 / _st.chi2.ppf(0.20, 63)) - 1.0861) < 5e-4
    assert PA.n_req(s_up) == 596                                    # card 10.4: n_req = 596 at the planning sigma_d 5.66
    d = FA.synthetic(n=64, effect=0.0)
    d2 = {"img_J": d["img_J"], "cap_J": d["cap_J"], "pre_J": d["pre_J"], "img_Alt": d["img_Alt"], "cap_Alt": d["cap_Alt"]}
    out = PA.run(d2, B=100)
    allowed = {"n", "sd_psi_J", "sd_psi_Alt", "rho_pair_psi", "bootstrap_se_Alt_minus_J", "sigma_d_up", "n_req", "lift_J", "prefix_only_lift_J",
               "dynamic_range_gate", "lift_ref_real"}
    assert set(out) <= allowed
    assert not any("contrast" in k or "lift_Alt" in k for k in out)
    assert out["dynamic_range_gate"]["bootstrap_se"] > 0
