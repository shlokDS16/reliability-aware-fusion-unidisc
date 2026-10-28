"""Numeric tests of the M4 analysis on synthetic runs with KNOWN outcomes (audit: 'real assertions'): family P, S-M with gatekeeping and K5/K6, S-C, S-DN, S-Z, S-D2,
Z_cal and the 2.13 rule, the split replication, per-test reporting (98.33 percent CI, Clopper-Pearson, mid-p), completeness and K7, seeds, selftest. CPU only."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import analyze_gate_m1, common                                  # noqa: E402
from exp_p2.gate import analysis_m4 as A, config, fit_threshold, report, scores, seeds, stats   # noqa: E402
from test_gate_analysis import _synth_probe                                 # noqa: E402

M = 64            # tokens per synthetic image
ARMS = ["none", "gate0.05", "gate0.01", "gate0.1", "geo0", "geo1", "geo2", "scat0", "scat1", "scat2", "topkB", "topks3", "chg"]


def ev(y, d=0.1):
    return dict(n=M, mean=0.01 * d, sd=0.1, z=8 * d, d=d, y=int(y))


def build(tmp, n, y, d=None, conds=("clean", "jpeg10", "patch"), dn=(), tex=False, seed=0):
    """y[(cond, arm)] -> 0/1 array over items (default 0); d[(cond, arm)] -> evidence d array (default 0.1). Writes items.jsonl and arrays/ like run_gate_m4."""
    rng = np.random.default_rng(seed)
    run = Path(tmp) / "P2-GATE-M4"
    (run / "arrays").mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(n):
        row = dict(idx=i, gid=2000 + i, n_tok=6 + i % 5, conds={})
        for c in conds:
            img = {a: ev(int(np.asarray(y.get((c, a), np.zeros(n)))[i]), float(np.asarray((d or {}).get((c, a), np.full(n, 0.1)))[i])) for a in ARMS if not (c == "clean" and a == "chg")}
            row["conds"][c] = dict(kind="clean" if c == "clean" else "pixel", n_changed=0, img=img, txt={}, gate={})
        for c in dn:
            row["conds"][c] = dict(kind="denoise", n_changed=0, img={"denoised": ev(int(np.asarray(y.get((c, "denoised"), np.zeros(n)))[i]))}, txt={}, gate={})
        rows.append(row)
        arrs = {}
        for c in conds:
            z = np.zeros(M, bool) if c == "clean" else (rng.random(M) < 0.3)
            arrs[f"{c}_z"] = z
            arrs[f"{c}_delta"] = rng.normal(0.1, 0.5, M).astype(np.float32)
            B = rng.normal(-3, 1, M).astype(np.float32)
            B[z] -= 2
            arrs[f"{c}_B"], arrs[f"{c}_D"] = B, np.full(M, -2.0, np.float32)
            for al in config.ALPHAS:
                arrs[f"{c}_flag{al:g}"] = (rng.random(M) < al) if c == "clean" else (z & (rng.random(M) < 0.5)) | (rng.random(M) < al)
            arrs[f"{c}_s3"] = rng.random(M).astype(np.float32)
            arrs[f"{c}_codes"] = rng.integers(0, 100, M).astype(np.int16)
            if tex:
                arrs[f"{c}_tex"] = (rng.random(M) + z).astype(np.float32)
        np.savez(run / "arrays" / f"item{i:04d}.npz", **arrs)
    (run / "items.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return run, rows


def flips(n, b, c):
    """gate and comparator outcome arrays with exactly b items (gate right, other wrong), c items (gate wrong, other right) and the rest concordant (half right)."""
    g, o = np.zeros(n, int), np.zeros(n, int)
    g[:b], o[:b] = 1, 0
    g[b:b + c], o[b:b + c] = 0, 1
    g[b + c:], o[b + c:] = 1, 1
    return g, o


FAM = [dict(corruption="jpeg", severity=10, key="jpeg10")]


# ------------------------------------------------------------------------------------------------ family P
def test_primary_numbers_holm_with_fixed_m3_and_direction(tmp_path):
    n = 100
    g, o = flips(n, 30, 2)
    run, rows = build(tmp_path, n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    pr = A.primary(rows, FAM, n_boot=400)
    j = pr["per_corruption"]["jpeg"]
    assert (j["b"], j["c"], j["n_d"], j["n"]) == (30, 2, 32, 100)
    assert j["p"] == pytest.approx(2 * sum(math.comb(32, i) for i in range(3)) / 2 ** 32)
    assert j["p_holm"] == pytest.approx(min(1.0, 3 * j["p"])) and j["gate_better"] and pr["claim_survives"] and j["label"] == "P1"
    for c in ("noise", "splice"):
        assert pr["per_corruption"][c]["tested"] is False and pr["per_corruption"][c]["p"] == 1.0 and pr["per_corruption"][c]["p_holm"] == 1.0
    assert pr["holm_m"] == 3
    g, o = flips(n, 2, 30)                                                     # GATE-M worse: rejected but does not count toward the claim
    run, rows = build(tmp_path / "w", n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    pr = A.primary(rows, FAM, n_boot=400)
    assert pr["per_corruption"]["jpeg"]["p_holm"] < 0.05 and not pr["per_corruption"]["jpeg"]["gate_better"] and not pr["claim_survives"]
    g, o = flips(n, 6, 6)
    run, rows = build(tmp_path / "e", n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    assert A.primary(rows, FAM, n_boot=400)["per_corruption"]["jpeg"]["p"] == 1.0


def test_per_test_report_fields_are_complete_and_consistent():
    g, o = flips(300, 25, 10)
    r = report.report_test(g, o, n_boot=3000, seed=seeds.seed_for("primary"))
    assert (r["b"], r["c"], r["n_d"], r["n"]) == (25, 10, 35, 300) and r["delta"] == pytest.approx(15 / 300)
    assert r["acc_a"] == pytest.approx(g.mean()) and r["acc_b"] == pytest.approx(o.mean())
    lo95, hi95 = r["ci95"]
    lo98, hi98 = r["ci9833"]
    assert lo98 <= lo95 < r["delta"] < hi95 <= hi98                            # 98.33 percent interval is wider
    assert r["ci90"][0] >= lo95 and r["ci90"][1] <= hi95
    lo, hi = r["theta_cp95"]
    assert r["theta"] == pytest.approx(25 / 35) and lo < r["theta"] < hi and lo == pytest.approx(0.5369553554, abs=1e-6) and hi == pytest.approx(0.8536452547, abs=1e-6)      # scipy binomtest(25, 35).proportion_ci(method='exact')
    assert r["p_mid"] < r["p"] and r["p_mid"] == pytest.approx(stats.mcnemar_midp(25, 10))
    assert r["equivalent_within_0p05"] is False
    z = report.report_test(*flips(300, 3, 3), n_boot=2000, seed=1)
    assert z["equivalent_within_0p05"] is True and z["p"] == 1.0 and z["p_mid"] == 1.0
    again = report.report_test(g, o, n_boot=3000, seed=seeds.seed_for("primary"))
    assert again["ci9833"] == r["ci9833"]                                      # same seed, same interval


def test_clopper_pearson_and_midp_known_values():
    assert stats.clopper_pearson(0, 10, 0.95)[0] == 0.0 and stats.clopper_pearson(0, 10, 0.95)[1] == pytest.approx(0.3085, abs=1e-3)
    assert stats.clopper_pearson(5, 10, 0.95) == pytest.approx((0.1871, 0.8129), abs=1e-3)
    assert stats.mcnemar_midp(9, 1) == pytest.approx(2 * (sum(math.comb(10, i) for i in range(1)) + 0.5 * 10) / 1024)
    assert math.isnan(stats.clopper_pearson(0, 0)[0])


# ------------------------------------------------------------------------------------------------ rule R3 routing (audit F8, card D15) and the outcome reading
def test_rule_record_in_family_json_content():
    from exp_p2.gate import headroom
    r = {d: headroom.sample_size_rule(d, 100) for d in (29, 18, 17)}
    assert (r[29]["rule"], r[29]["primary_endpoint_code"], r[29]["negative_reading_available"]) == ("R1", "Y", True)
    assert (r[18]["rule"], r[18]["test_fold"], r[18]["negative_reading_available"]) == ("R2", 500, True)
    assert (r[17]["rule"], r[17]["primary_endpoint_code"], r[17]["negative_reading_available"], r[17]["test_fold"]) == ("R3", "d", False, 300)
    assert "negative" in r[17]["note"] and headroom.sample_size_rule(None, 100)["negative_reading_available"] is False


def test_r3_makes_wilcoxon_on_d_primary_with_the_same_labels_and_m3_and_moves_y_to_secondary(tmp_path):
    n = 120
    g, o = flips(n, 6, 6)                                                        # Y: no difference at all
    d = {("jpeg10", "gate0.05"): 0.30 + 0.002 * np.arange(n) / n, ("jpeg10", "none"): np.full(n, 0.1)}      # d: GATE-M clearly higher in every item
    run, rows = build(tmp_path, n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o}, d)
    res = A.run(run, FAM, n_boot=300, rule="R3")
    p = res["primary"]
    assert res["rule"] == "R3" and p["rule"] == "R3" and p["endpoint"] == "d" and p["holm_m"] == 3 and res["negative_available"] is False and p["negative_available"] is False
    j = p["per_corruption"]["jpeg"]
    assert j["label"] == "P1" and j["tested"] and j["p"] < 1e-10 and j["p_holm"] == pytest.approx(min(1.0, 3 * j["p"])) and j["mean_diff"] == pytest.approx(0.2, abs=0.01) and j["gate_better"]
    assert p["per_corruption"]["noise"]["tested"] is False and p["per_corruption"]["noise"]["p"] == 1.0 and p["per_corruption"]["noise"]["p_holm"] == 1.0
    assert p["claim_survives"] and res["outcome"]["label"] == "positive"
    sec = res["secondary_y"]["per_corruption"]["jpeg"]                          # Y is secondary: no difference there
    assert (sec["b"], sec["c"]) == (6, 6) and sec["p"] == 1.0 and not sec["gate_better"] and res["primary_endpoint"].startswith("d")
    r1 = A.run(run, FAM, n_boot=300, rule="R1")                                 # the same data under R1: the primary is Y and finds nothing
    assert r1["primary"]["per_corruption"]["jpeg"]["p"] == 1.0 and not r1["primary"]["claim_survives"] and r1["secondary_y"] is None and r1["negative_available"] is True


def test_r3_rejection_needs_a_positive_difference_and_negative_is_unavailable(tmp_path):
    n = 300
    g, o = flips(n, 0, 0)
    worse = {("jpeg10", "gate0.05"): np.full(n, 0.1) - 0.002 * np.arange(n) / n, ("jpeg10", "none"): np.full(n, 0.3)}   # GATE-M clearly LOWER in d
    run, rows = build(tmp_path / "w", n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o}, worse)
    r3 = A.run(run, FAM, n_boot=200, rule="R3")
    j = r3["primary"]["per_corruption"]["jpeg"]
    assert j["p_holm"] < 0.05 and j["mean_diff"] < 0 and not j["gate_better"] and not r3["primary"]["claim_survives"]     # rejected, wrong sign: does not count toward the claim
    assert r3["outcome"]["label"] == "inconclusive" and any("R3" in x for x in r3["outcome"]["reasons"])
    same = {("jpeg10", "gate0.05"): np.full(n, 0.1), ("jpeg10", "none"): np.full(n, 0.1)}
    run, rows = build(tmp_path / "s", n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o}, same)
    r1 = A.run(run, FAM, n_boot=300, rule="R1")
    assert r1["outcome"]["label"] == "negative" and "loss larger than 0.05 is excluded" in r1["outcome"]["sentence"]          # tight CI, n = 300 >= 240, no rejection
    r3 = A.run(run, FAM, n_boot=300, rule="R3")
    assert r3["outcome"]["label"] == "inconclusive" and not r3["negative_available"]        # identical data, but under R3 'negative' can never be printed
    nogo = A.run(run, [], n_boot=100, rule="NO-GO")
    assert nogo["outcome"]["label"] == "inconclusive" and any("K1" in x for x in nogo["outcome"]["reasons"])


def test_outcome_reading_requires_n_240_and_a_tight_ci_for_every_corruption_with_an_operating_point(tmp_path):
    n = 200
    g, o = flips(n, 0, 0)
    run, rows = build(tmp_path, n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    assert A.run(run, FAM, n_boot=200, rule="R1")["outcome"]["label"] == "inconclusive"          # n = 200 < 240
    n = 300
    g, o = flips(n, 40, 40)                                                      # discordance 27 percent: 90 percent half-width about 0.047 + noise: wider than the margin or not
    run, rows = build(tmp_path / "wide", n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    res = A.run(run, FAM, n_boot=2000, rule="R1")
    ci = res["primary"]["per_corruption"]["jpeg"]["ci90"]
    assert res["outcome"]["label"] == ("negative" if (ci[0] > -0.05 and ci[1] < 0.05) else "inconclusive")
    g, o = flips(n, 120, 0)                                                      # large discordance with a clear win: positive
    run, rows = build(tmp_path / "pos", n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    assert A.run(run, FAM, n_boot=200, rule="R1")["outcome"]["label"] == "positive"


def test_wording_says_exactly_what_was_tested_and_r3_output_has_no_verification_claim(tmp_path):
    n = 120
    g, o = flips(n, 6, 6)
    d = {("jpeg10", "gate0.05"): 0.30 + 0.002 * np.arange(n) / n, ("jpeg10", "none"): np.full(n, 0.1)}
    run, rows = build(tmp_path, n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o}, d)
    r3 = A.run(run, FAM, n_boot=200, rule="R3")
    text = json.dumps(r3, default=float).lower()
    assert "verification" not in text and "improved" not in text                                         # nothing in the R3 output claims verification or an improvement of it
    assert r3["outcome"]["label"] == "positive" and r3["outcome"]["tested"] == "higher per-item mean/sd evidence ratio d (R3 primary)"
    assert r3["outcome"]["sentence"].startswith("GATE-M had a higher per-item mean/sd evidence ratio d (R3 primary) than no gate on jpeg")
    assert "not matching accuracy" in r3["outcome"]["sentence"] and "trimming heavy-tailed tokens" in r3["outcome"]["sentence"]
    assert r3["tested_by_primary"] == A.WORDING_D and r3["primary"]["tested"] == A.WORDING_D
    assert any("trimming heavy-tailed tokens" in c and "plain-B top-k" in c for c in r3["caveats"]) and any("S-M under R3" in c and "uninformative" in c for c in r3["caveats"])
    assert r3["s_m"]["uninformative_under_R3"] is True
    flat_d = {("jpeg10", "gate0.05"): np.full(n, 0.1), ("jpeg10", "none"): np.full(n, 0.1)}
    run, rows = build(tmp_path / "null", n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o}, flat_d)
    nul = A.run(run, FAM, n_boot=200, rule="R3")
    assert nul["outcome"]["label"] == "inconclusive" and "verification" not in json.dumps(nul, default=float).lower() and nul["outcome"]["sentence"].startswith("no higher per-item mean/sd evidence ratio d (R3 primary)")
    g2, o2 = flips(n, 30, 2)
    run, rows = build(tmp_path / "y", n, {("jpeg10", "gate0.05"): g2, ("jpeg10", "none"): o2})
    r1 = A.run(run, FAM, n_boot=200, rule="R1")
    assert r1["outcome"]["sentence"].startswith("GATE-M had a higher matching accuracy (McNemar on Y) than no gate on jpeg") and r1["primary"]["tested"] == A.WORDING_Y
    assert "verification" not in r1["outcome"]["sentence"].lower() and r1["caveats"] == [A.CAVEAT_D]       # the d caveat is recorded whenever d is reported (S-Z), not only under R3
    assert A.wording("R1") == A.wording("R2") == "higher matching accuracy (McNemar on Y)"


# ------------------------------------------------------------------------------------------------ S-M, S-C, K5, K6
def test_s_m_uses_seed_one_gatekeeps_and_flags_k5_k6(tmp_path):
    n = 100
    g, none = flips(n, 30, 2)
    geo_lose = g.copy()
    geo_lose[:25] = 0                                                           # an equally shaped random mask does much worse: S-M rejects
    y = {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): none, ("jpeg10", "geo0"): geo_lose, ("jpeg10", "geo1"): g, ("jpeg10", "geo2"): geo_lose}
    run, rows = build(tmp_path, n, y)
    pr = A.primary(rows, FAM, 300)
    sm = A.s_m(rows, FAM, pr, 300)
    j = sm["per_corruption"]["jpeg"]
    assert j["tested"] and j["b"] == 25 and j["c"] == 0 and j["rejected"] and sm["seed_confirmatory"].startswith("geo0")
    assert set(j["replications"]) == {"geo1", "geo2"} and j["replications"]["geo1"]["p"] == 1.0 and j["replications"]["geo2"]["b"] == 25      # own p, uncombined
    assert sm["per_corruption"]["noise"]["tested"] is False and sm["per_corruption"]["noise"]["p"] == 1.0 and sm["holm_m"] == 3
    assert sm["K5_not_attributable_to_detection"] == [] and sm["K6_geometry_equals_gate"] is False
    y2 = dict(y)
    y2[("jpeg10", "geo0")] = g.copy()
    y2[("jpeg10", "geo0")][:2] = 0                                              # geo within 2 of GATE-M
    run, rows = build(tmp_path / "k", n, y2)
    sm = A.s_m(rows, FAM, A.primary(rows, FAM, 300), 300)
    assert sm["K5_not_attributable_to_detection"] == ["jpeg"] and sm["K6_geometry_equals_gate"] is True
    run, rows = build(tmp_path / "n", n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): g})       # P not rejected: S-M untested, K flags undefined
    sm = A.s_m(rows, FAM, A.primary(rows, FAM, 300), 300)
    assert sm["per_corruption"]["jpeg"]["tested"] is False and sm["K5_not_attributable_to_detection"] is None and sm["K6_geometry_equals_gate"] is None


def test_s_c_clean_control_detects_a_loss(tmp_path):
    n = 100
    g, o = flips(n, 1, 9)
    run, rows = build(tmp_path, n, {("clean", "gate0.05"): g, ("clean", "none"): o})
    sc = A.s_c(rows, 300)
    assert (sc["b"], sc["c"]) == (1, 9) and sc["holm_m"] == 1 and sc["p"] == pytest.approx(2 * (1 + 10) / 1024) and sc["gate_worse"] and not sc["gate_better"]


def test_s_dn_and_s_z_numbers(tmp_path):
    n = 100
    g, dn = flips(n, 20, 1)
    y = {("jpeg10", "gate0.05"): g, ("jpeg10_dn", "denoised"): dn}
    d = {("jpeg10", "gate0.05"): np.full(n, 0.3) + 0.01 * np.arange(n) / n, ("jpeg10", "none"): np.full(n, 0.1)}
    run, rows = build(tmp_path, n, y, d, conds=("clean", "jpeg10", "patch"), dn=("jpeg10_dn",))
    sdn = A.s_dn(rows, FAM, 300)
    assert sdn["holm_m"] == 2 and set(sdn["per_corruption"]) == {"jpeg", "noise"}
    assert sdn["per_corruption"]["jpeg"]["b"] == 20 and sdn["per_corruption"]["jpeg"]["p_holm"] == pytest.approx(min(1.0, 2 * sdn["per_corruption"]["jpeg"]["p"])) and sdn["per_corruption"]["jpeg"]["gate_better"]
    assert sdn["per_corruption"]["noise"]["p"] == 1.0
    sz = A.s_z(rows, FAM, "d", 300)
    j = sz["per_corruption"]["jpeg"]
    assert j["endpoint"] == "d" and j["n"] == 100 and j["p"] < 1e-10 and j["ci"]["diff"] == pytest.approx(0.2 + 0.01 * 0.495, abs=1e-3) and sz["holm_m"] == 3
    assert j["p_holm"] == pytest.approx(min(1.0, 3 * j["p"])) and sz["per_corruption"]["splice"]["p"] == 1.0
    assert "z" in j["sensitivity_other_endpoint"]


# ------------------------------------------------------------------------------------------------ calibration: Z_cal and K4
def test_z_cal_formula_and_the_2_13_rule():
    assert A.Z_CAL_CRIT == 2.13
    assert A.z_cal(0.07, 0.05, 0.1, 300, 300) == pytest.approx(0.02 / (0.1 * math.sqrt(2 / 300)))
    assert A.z_cal(0.05, 0.05, 0.1, 300, 300) == 0.0
    rng = np.random.default_rng(0)
    base = rng.beta(2, 38, 300)                                                 # item-level loss, mean about 0.05
    ok = A.fap_check({0.05: base, 0.01: base * 0.2, 0.1: base * 2}, None, 300, n_boot=300)
    assert ok["K4_violation_evidence"] is False and ok["per_alpha"]["0.05"]["sigma_source"] == "test items only"
    hi = A.fap_check({0.05: np.clip(base + 0.03, 0, 1), 0.01: base * 0.2, 0.1: base * 2}, None, 300, n_boot=300)
    assert hi["per_alpha"]["0.05"]["violation"] and hi["K4_violation_evidence"] is True and "never 'validated'" in hi["wording"]
    # pooled sigma uses calibration items too
    s = A.pooled_sd(np.array([0., 0., 1., 1.]), np.array([0., 1.]))
    assert s == pytest.approx(math.sqrt((3 * (1 / 3) + 1 * 0.5) / 4))


def test_calibration_losses_are_reproduced_from_the_stored_jitter_seed(tmp_path):
    rng = np.random.default_rng(3)
    m2 = tmp_path / "P2-GATE-M2"
    (m2 / "arrays").mkdir(parents=True)
    rows, U, ids = [], [], []
    for i in range(40):
        B = rng.normal(-3, 1, 32).astype(np.float32)
        D = rng.normal(-2, 0.3, 32).astype(np.float32)
        np.savez(m2 / "arrays" / f"item{i:04d}.npz", B=B, D=D)
        rows.append(dict(idx=i, gid=i))
        U.append(scores.suspicion_q(B, D))
        ids.append(i)
    (m2 / "items.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    thr = fit_threshold.fit_from_arrays(U, ids, "q")
    for al in (0.05, 0.1):
        L = A.cal_losses(m2, thr, al)
        assert L.mean() == pytest.approx(thr["thresholds"][f"{al:g}"]["r_hat"], abs=1e-12)        # the same jitter draws as the fit: exactly the stored empirical risk
        assert 40 / 41 * L.mean() + 1 / 41 <= al + 1e-12
    assert A.cal_losses(tmp_path / "nowhere", thr, 0.05) is None


def test_split_replication_is_centred_near_zero_for_exchangeable_items():
    rng = np.random.default_rng(1)
    mu = np.linspace(-1, 1, 20)
    U = [mu + rng.standard_t(5, 20) for _ in range(160)]
    r = A.split_replication(U[:80], U[80:], 0.1, reps=60, seed=5)
    assert r["reps"] == 60 and -0.06 < r["mean_F_minus_alpha"] < 0.03 and r["q025"] <= r["mean_F_minus_alpha"] <= r["q975"] and "exploratory" in r["label"]


# ------------------------------------------------------------------------------------------------ completeness, K7, partial runs, dedup
def _planned(n):
    return [dict(idx=i, n_tok=6 + i % 5) for i in range(n)]


def test_load_items_dedups_by_item_keeping_the_first_row(tmp_path):
    run = tmp_path / "P2-GATE-M4"
    run.mkdir(parents=True)
    (run / "items.jsonl").write_text("\n".join(json.dumps(x) for x in [dict(idx=0, v=1), dict(idx=1, v=1), dict(idx=0, v=2)]) + "\n")
    rows, dup = A.load_items(run)
    assert [r["v"] for r in rows] == [1, 1] and dup == 1


def test_completeness_prefix_missing_covariates_and_worst_case(tmp_path):
    n = 100
    g, o = flips(n, 30, 2)
    run, rows = build(tmp_path, n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    comp = A.completeness_report(rows[:70], _planned(100), FAM, n_dup=2)
    assert (comp["planned_n"], comp["completed_n"], comp["n_missing"], comp["n_duplicates_removed"]) == (100, 70, 30, 2) and comp["prefix_ok"] and comp["below_80_percent"]
    assert comp["covariates"]["mean_order_missing"] > comp["covariates"]["mean_order_completed"]
    gap = A.completeness_report(rows[:3] + rows[4:20], _planned(100), FAM)
    assert gap["prefix_ok"] is False                                           # item 3 missing from the middle: not a prefix
    w = comp["worst_case_first_holm_step"]["jpeg"]
    assert w["p_worst_case_all_missing_favour_none"] > w["p_observed"]
    full = A.completeness_report(rows, _planned(100), FAM)
    assert full["K7"] is False and not full["below_80_percent"] and full["n_missing"] == 0


def test_k7_stops_the_analysis_and_partial_runs_wait_for_the_planned_fold(tmp_path):
    n = 50
    g, o = flips(n, 12, 1)
    run, rows = build(tmp_path, n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    res = A.run(run, FAM, n_boot=100, planned=_planned(50), split_reps=0)
    assert res["completeness"]["K7"] is False and res["primary"]["per_corruption"]["jpeg"]["b"] == 12 and res["meta"]["root_seed"] == 20261028
    with pytest.raises(A.PartialRun, match="SAP 8.2"):
        A.run(run, FAM, n_boot=100, planned=_planned(80))
    res = A.run(run, FAM, n_boot=100, planned=_planned(80), allow_partial=True)
    assert res["meta"]["allow_partial"] is True and res["completeness"]["completed_n"] == 50
    lines = [json.loads(l) for l in (run / "items.jsonl").read_text().splitlines()]
    for r in lines[:5]:                                                         # 10 percent of the none-arm evidence is NaN: a pipeline defect
        r["conds"]["jpeg10"]["img"]["none"]["d"] = float("nan")
    (run / "items.jsonl").write_text("\n".join(json.dumps(r) for r in lines) + "\n")
    with pytest.raises(A.PipelineDefect, match="K7"):
        A.run(run, FAM, n_boot=100, planned=_planned(50))


def test_main_refuses_partial_missing_frozen_and_wrong_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    (tmp_path / "P2-GATE-M3").mkdir()
    (tmp_path / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="z", family=[])))
    assert A.main(["--run-id", "P2-GATE-M4"]) == 2
    (tmp_path / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="d", family=[], n_rule=dict(test_fold=300))))
    assert A.main(["--run-id", "P2-GATE-M4"]) == 2                              # detection_frozen.json missing
    assert A.main(["--run-id", "P2-GATE-M4", "--skip-selftest"]) == 2


# ------------------------------------------------------------------------------------------------ S-D2 with a frozen rival
def test_s_d2_compares_q_with_the_frozen_rival_and_keeps_missing_corruptions_at_p_one(tmp_path):
    n = 30
    run, rows = build(tmp_path, n, {}, conds=("clean", "jpeg10", "noise0.1", "patch"), tex=True)
    fam = [dict(corruption="jpeg", severity=10, key="jpeg10"), dict(corruption="noise", severity=0.1, key="noise0.1")]
    frozen = {"jpeg": dict(available=True, rival="tex", base="tex", sign=1), "noise": dict(available=True, rival="plainB", base="plainB", sign=1)}
    r = A.s_d2(run, rows, fam, frozen, None, 500)
    assert r["holm_m"] == 2
    for c in ("jpeg", "noise"):
        x = r["per_corruption"][c]
        assert x["tested"] and x["n_eligible"] == 30 and 0 <= x["p"] <= 1 and x["p_holm"] >= x["p"] and x["ci9833"][0] <= x["ci95"][0]
    # q = B - D is lower on corrupted tokens by construction (B shifted by -2), so q separates better than a noisy texture
    assert r["per_corruption"]["jpeg"]["auroc_q"] > 0.7
    only = A.s_d2(run, rows, [fam[0]], frozen, None, 200)
    assert only["per_corruption"]["noise"]["tested"] is False and only["per_corruption"]["noise"]["p_holm"] == 1.0
    assert A.s_d2(run, rows, fam, None, None, 100)["per_corruption"]["jpeg"]["p"] == 1.0                          # no frozen file: p = 1 (main refuses this case)


# ------------------------------------------------------------------------------------------------ C1 (clean-image recovery) and the chance bar (card D16)
def test_c1_numbers_trigger_and_sentence():
    from exp_p2.gate import c1
    assert (c1.PROBE1_K, c1.PROBE1_N, c1.PROBE1_CI) == (253, 300, (0.798, 0.880))
    same = c1.c1([1] * 253 + [0] * 47, "cal")
    assert same["accuracy"] == pytest.approx(253 / 300) and same["wilson95"] == pytest.approx([0.7979, 0.8801], abs=1e-3) and same["overlaps_probe1_interval"] and not same["audit_trigger"]
    assert same["sentence"] == "the clean none-arm accuracy was 0.843 (95 percent CI 0.798 to 0.880), against 0.843 (0.798 to 0.880) in probe 1"
    near = c1.c1([1] * 230 + [0] * 70)                                          # 0.767, Wilson about 0.716-0.810: still overlaps 0.798
    assert near["overlaps_probe1_interval"] and not near["audit_trigger"]
    low = c1.c1([1] * 200 + [0] * 100)                                          # 0.667: interval ends below 0.798
    assert low["audit_trigger"] and not low["overlaps_probe1_interval"] and not low["above_interval"] and "audit" in low["rule"]
    high = c1.c1([1] * 298 + [0] * 2)                                           # above 0.88: flagged as non-overlap, but the SAP says a high value is not alarming by itself
    assert high["audit_trigger"] and high["above_interval"]
    assert c1.c1([float("nan")] * 3)["sentence"] == "no items"
    assert "validat" not in same["sentence"] and "power" not in same["sentence"]


def test_c1_looks_read_the_right_fields_and_each_look_is_recorded_once(tmp_path, monkeypatch):
    from exp_p2.gate import c1
    monkeypatch.setattr(common, "RUNS", tmp_path)
    cal_rows = [dict(idx=i, img=dict(y=int(i % 5 != 0))) for i in range(300)]
    head_rows = [dict(idx=i, clean=dict(y=int(i % 5 != 0))) for i in range(100)]
    test_rows = [dict(idx=i, conds=dict(clean=dict(img={"none": dict(y=int(i % 5 != 0)), "gate0.05": dict(y=0)}))) for i in range(300)]
    assert c1.ys_from_rows(cal_rows, "cal") == [r["img"]["y"] for r in cal_rows] and sum(c1.ys_from_rows(head_rows, "head")) == 80
    assert c1.ys_from_rows(test_rows, "test") == [r["conds"]["clean"]["img"]["none"]["y"] for r in test_rows]
    for rid, rows in (("P2-GATE-M2", cal_rows), ("P2-GATE-M3", head_rows), ("P2-GATE-M4", test_rows)):
        (tmp_path / rid).mkdir()
        (tmp_path / rid / "items.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    assert c1.main(["--look", "cal"]) == 0 and c1.main(["--look", "head"]) == 0 and c1.main(["--look", "test"]) == 0
    got = json.loads((tmp_path / "P2-GATE-M2" / "c1_cal.json").read_text())
    assert got["n"] == 300 and got["k"] == 240 and got["look"] == "calibration" and got["accuracy"] == 0.8 and not got["audit_trigger"]
    assert c1.main(["--look", "cal"]) == 2                                      # looks are recorded once and never pooled


def test_c1_test_look_refuses_a_partial_m4_fold(tmp_path, monkeypatch):
    from exp_p2.gate import c1
    monkeypatch.setattr(common, "RUNS", tmp_path)
    m4 = tmp_path / "P2-GATE-M4"
    m4.mkdir()
    row = lambda i: dict(idx=i, conds=dict(clean=dict(img={"none": dict(y=1)})))
    (m4 / "items.jsonl").write_text("\n".join(json.dumps(row(i)) for i in range(299)) + "\n")
    assert c1.expected_test_n() == 300 and c1.main(["--look", "test"]) == 2 and not (m4 / "c1_test.json").exists()         # 299 of 300: refused, nothing written
    (m4 / "items.jsonl").write_text("\n".join(json.dumps(row(i)) for i in range(300)) + "\n")
    assert c1.main(["--look", "test"]) == 0 and (m4 / "c1_test.json").exists()
    (m4 / "c1_test.json").unlink()
    (tmp_path / "P2-GATE-M3").mkdir()
    (tmp_path / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(n_rule=dict(rule="R2", test_fold=500))))
    assert c1.expected_test_n() == 500 and c1.main(["--look", "test"]) == 2                                              # R2: the planned fold is 500
    (m4 / "effective_n.json").write_text(json.dumps(dict(planned=500, effective=300)))
    assert c1.expected_test_n() == 300 and c1.main(["--look", "test"]) == 0                                              # exclusions lower the expectation
    (tmp_path / "P2-GATE-M2").mkdir()                                                                                    # the calibration look is not affected
    (tmp_path / "P2-GATE-M2" / "items.jsonl").write_text("\n".join(json.dumps(dict(idx=i, img=dict(y=1))) for i in range(10)) + "\n")
    assert c1.main(["--look", "cal"]) == 0


def test_analysis_reports_c1_on_the_clean_test_items(tmp_path):
    n = 60
    g, o = flips(n, 5, 1)
    run, rows = build(tmp_path, n, {("clean", "none"): o, ("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o})
    res = A.run(run, FAM, n_boot=100)
    c = res["c1_test"]
    assert c["n"] == 60 and c["k"] == int(o.sum()) and c["look"].startswith("test") and c["probe1"]["wilson95"] == [0.798, 0.88]


def test_chance_bar_passes_fails_and_waits_for_q():
    from exp_p2.gate import detect
    def item(pb, q):
        d = {c: {"plainB": pb, "_eligible": 1.0} | ({"q": q} if q is not None else {}) for c in ("patch", "swap")}
        return d
    rng = np.random.default_rng(0)
    good = [item(0.95 + 0.01 * rng.standard_normal(), 0.96 + 0.01 * rng.standard_normal()) for _ in range(40)]
    r = detect.chance_bar(good, n_boot=500)
    assert r["passes"] is True and not r["failed"] and not r["audit_trigger"] and r["per_score"]["patch/q"]["lower95"] > 0.9 and set(r["per_score"]) == {"patch/plainB", "patch/q", "swap/plainB", "swap/q"}
    no_q = [item(0.95 + 0.01 * rng.standard_normal(), None) for _ in range(40)]
    r = detect.chance_bar(no_q, n_boot=500)
    assert r["passes"] is None and r["n_unavailable"] == 2 and not r["failed"] and r["per_score"]["swap/q"]["available"] is False
    chance = [item(0.5 + 0.05 * rng.standard_normal(), 0.96) for _ in range(40)]       # plain-B at chance on patch and swap: a pipeline defect
    r = detect.chance_bar(chance, n_boot=500)
    assert r["failed"] and r["audit_trigger"] and r["passes"] is False and not r["per_score"]["patch/plainB"]["passes"] and r["per_score"]["patch/q"]["passes"]
    sign_flipped = [item(0.05, 0.05) for _ in range(40)]                              # reversed sign: far below 0.5, also a failure
    assert detect.chance_bar(sign_flipped, n_boot=200)["failed"]
    edge = [item(0.5 + 0.2 * (-1) ** i, 0.9) for i in range(40)]                      # mean 0.5, wide: lower bound below 0.5
    assert detect.chance_bar(edge, n_boot=500)["per_score"]["patch/plainB"]["passes"] is False


def test_m1_analysis_includes_the_chance_bar(tmp_path):
    p2, m1 = _synth_probe(tmp_path, n_items=12, q_better=True)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=300)
    cb = res["chance_bar"]
    assert cb["passes"] is True and cb["per_score"]["patch/q"]["n"] == 12 and cb["per_score"]["swap/plainB"]["lower95"] > 0.5
    res2 = analyze_gate_m1.run_analysis(p2, None, pixels=False, n_boot=300)             # no D yet (CPU fallback): q unavailable, plain-B still judged
    assert res2["chance_bar"]["passes"] is None and res2["chance_bar"]["per_score"]["patch/plainB"]["passes"] is True


# ------------------------------------------------------------------------------------------------ seeds, selftest
def test_seed_sequence_per_analysis_is_deterministic_and_distinct():
    a, b = seeds.seed_for("primary"), seeds.seed_for("primary")
    assert np.random.default_rng(a).integers(0, 2**31) == np.random.default_rng(b).integers(0, 2**31)
    assert np.random.default_rng(seeds.seed_for("s_m")).integers(0, 2**31) != np.random.default_rng(seeds.seed_for("s_c")).integers(0, 2**31)
    with pytest.raises(KeyError):
        seeds.seed_for("made_up")
    m = seeds.meta()
    assert m["root_seed"] == 20261028 and m["numpy_version"] == np.__version__ and m["spawn_order"][0] == "load_items"


def test_selftest_passes():
    st = A.selftest(n_sim=4000)
    assert st["all_ok"], st
    assert st["mcnemar_size"] <= 0.05 and st["holm_ok"] and st["boot_ok"]


def test_full_run_writes_meta_with_seed_and_numpy_version(tmp_path):
    n = 40
    g, o = flips(n, 10, 1)
    run, rows = build(tmp_path, n, {("jpeg10", "gate0.05"): g, ("jpeg10", "none"): o, ("clean", "gate0.05"): g, ("clean", "none"): g})
    res = A.run(run, FAM, n_boot=200)
    json.dumps(res, default=float)
    assert res["meta"]["numpy_version"] == np.__version__ and res["s_c"]["holm_m"] == 1 and res["s_m"]["holm_m"] == 3
    assert res["calibration"]["fap_check"]["per_alpha"]["0.05"]["sigma_source"] == "test items only"
    assert set(res["calibration"]["fap_check"]["per_alpha"]) == {"0.05", "0.01", "0.1"}


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
