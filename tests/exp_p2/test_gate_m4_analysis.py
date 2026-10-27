"""Numeric tests of the M4 analysis on synthetic runs with KNOWN outcomes (audit: 'real assertions'): family P, S-M with gatekeeping and K5/K6, S-C, S-DN, S-Z, S-D2,
Z_cal and the 2.13 rule, the split replication, per-test reporting (98.33 percent CI, Clopper-Pearson, mid-p), completeness and K7, seeds, selftest. CPU only."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import analysis_m4 as A, config, fit_threshold, report, scores, seeds, stats   # noqa: E402

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
