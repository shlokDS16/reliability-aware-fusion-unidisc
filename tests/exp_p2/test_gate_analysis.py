"""Statistics, headroom decision, Prop. 4 calculator, detection analysis and fusion (v2 sections 5.3, 7.3, 7.6, 8, 9). Synthetic data only; CPU."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import analyze_gate_m1, common                                  # noqa: E402
from exp_p2.gate import detect, fusion, headroom, stats, theory             # noqa: E402


# ------------------------------------------------------------------------------------------------ stats
def test_power_table_matches_the_spec():
    spec = {0.70: (47, 63), 0.75: (29, 39), 0.80: (20, 27)}
    for theta, (a, b) in spec.items():
        assert math.ceil(stats.power_nd(theta, 0.05)) == a
        assert math.ceil(stats.power_nd(theta, 0.0167)) == b                    # the spec rounds alpha' = 0.05/3 to 0.0167; exact 0.05/3 can add one pair
    assert stats.exact_sign_power(60, 0.75, 0.05) > 0.95 and stats.exact_sign_power(10, 0.5, 0.05) <= 0.05
    assert 0.6 < stats.exact_sign_power(math.ceil(stats.power_nd(0.75, 0.05)), 0.75, 0.05) < 0.95     # exact power near the approximation's 0.8


def test_mcnemar_exact_and_holm():
    r = stats.mcnemar_exact([1] * 9 + [0] * 1 + [1] * 5, [0] * 9 + [1] * 1 + [1] * 5)
    assert (r["b"], r["c"], r["n_discordant"]) == (9, 1, 10)
    assert r["p"] == pytest.approx(2 * (1 + 10) / 1024)                                                # 2 * P(Bin(10,.5) <= 1)
    assert stats.mcnemar_exact([1, 0], [1, 0])["p"] == 1.0
    assert stats.mcnemar_exact([1, 1], [0, 0])["p"] == pytest.approx(0.5)
    assert stats.mcnemar_exact([1, np.nan], [0, 1])["n"] == 1                                          # NaN items dropped
    adj = stats.holm([0.01, 0.04, 0.03])
    assert adj == [pytest.approx(0.03), pytest.approx(0.06), pytest.approx(0.06)]
    assert stats.holm([0.5]) == [0.5] and stats.holm([]) == []


def test_paired_diff_drops_nonfinite_and_counts():
    d = stats.paired_diff([3, 4, np.nan, 5, np.inf], [1, 1, 1, 1, 1])
    assert d["n"] == 3 and d["n_dropped"] == 2 and d["diff"] == pytest.approx(3.0) and d["se"] == pytest.approx(np.std([2, 3, 4], ddof=1) / math.sqrt(3))


# ------------------------------------------------------------------------------------------------ headroom (SAP section 5, 4.6, Addendum 1)
def _rows(spec, n=100, seed=0):
    """spec: rung key -> (drop of the corrupted-none evidence from clean, gain of the changed-code evidence over none, n discordant items with chg right and none wrong).
    Evidence is stored on both scales: z = 10 d here (m = 1024 in the real data)."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        dc = 0.5 + rng.normal(0, 0.1)
        row = dict(clean=dict(n=1024, d=dc, z=10 * dc, y=1), rungs={})
        for key, (drop, gain, disc) in spec.items():
            dn = dc - 0.2 * drop + rng.normal(0, 0.05)
            dg = dn + 0.2 * gain + rng.normal(0, 0.05)
            row["rungs"][key] = dict(n_changed=100, none=dict(n=1024, d=dn, z=10 * dn, y=int(i >= disc)), chg=dict(n=924, d=dg, z=10 * dg, y=1))
        rows.append(row)
    return rows


SPEC = {"jpeg10": (0.0, 0.0, 0), "jpeg5": (2.0, 1.5, 5), "noise0.1": (2.0, 0.0, 0), "noise0.2": (2.0, 0.0, 0), "splice128": (2.0, 1.5, 30), "splice192": (3.0, 2.0, 40)}


def test_headroom_default_endpoint_is_d_and_family_json_records_it():
    res = headroom.decide(_rows(SPEC))
    assert res["endpoint"] == "d" and "z* = sqrt(m) * d" in res["endpoint_note"]
    assert [(f["corruption"], f["severity"]) for f in res["family"]] == [("jpeg", 5), ("splice", 128)]          # first passing rung; noise fails H2 on both rungs
    assert [e["corruption"] for e in res["excluded"]] == ["noise"]
    r = res["rungs"]["jpeg5"]
    assert r["endpoint"] == "d" and r["n_v"] == 100 and r["T1"] >= 2 and r["T2"] >= 2 and r["passes"] and not res["rungs"]["jpeg10"]["passes"]
    assert res["rungs"]["noise0.1"]["H1_pass"] and not res["rungs"]["noise0.1"]["H2_pass"]
    assert r["z_star_scale"] == pytest.approx(32.0) and r["mean_drop_z_star"] == pytest.approx(32 * r["H1"]["mean"])
    assert res["go"] and not res["downstream_claim_withdrawn"] and "z" in res["sensitivity_other_endpoint"]


def test_z_verdict_is_a_sensitivity_row_and_never_changes_the_family():
    rows = _rows(SPEC)
    for r in rows:                                                              # make the z endpoint of the changed-code gate worse than none (fewer tokens, sqrt(|R|) cost)
        c = r["rungs"]["jpeg5"]
        c["chg"]["z"] = c["none"]["z"] - 1.0
    res = headroom.decide(rows, "d")
    assert any(f["key"] == "jpeg5" for f in res["family"])
    sens = res["sensitivity_other_endpoint"]["z"]["jpeg5"]
    assert sens["endpoint"] == "z" and sens["passes"] is False and sens["H1_pass"] is True
    assert headroom.decide(rows, "z")["sensitivity_other_endpoint"]["d"]["jpeg5"]["passes"] is True         # and the other way round when z is the primary (flagged invalid by the SAP)
    assert not any(f["key"] == "jpeg5" for f in headroom.decide(rows, "z")["family"])


def test_rung_needs_at_least_90_valid_items_and_t_at_least_2():
    rows = _rows(SPEC)
    for r in rows[:11]:
        r["rungs"]["jpeg5"]["none"]["d"] = float("nan")                         # 89 valid items
    ev = headroom.evaluate_rung(rows, "jpeg5")
    assert ev["n_v"] == 89 and ev["n_missing"] == 11 and ev["T1"] >= 2 and ev["T2"] >= 2 and not ev["passes"]
    rows[0]["rungs"]["jpeg5"]["none"]["d"] = rows[0]["clean"]["d"] - 0.4        # restore one item: 90 valid items
    ev = headroom.evaluate_rung(rows, "jpeg5")
    assert ev["n_v"] == 90 and ev["passes"]
    weak = headroom.evaluate_rung(_rows({"jpeg5": (0.05, 0.05, 0)}, seed=3), "jpeg5")
    assert weak["n_v"] == 100 and not weak["passes"]                           # T below 2: a rung with a tiny drop is excluded


def test_n_rule_uses_exact_N_star_43_kappa_half_and_the_r1_r2_r3_boundaries():
    assert headroom.N_STAR == 43 and headroom.KAPPA == 0.5
    assert stats.exact_sign_min_n(0.75, 0.0167) == headroom.N_STAR                 # the exact value, not the normal approximation (39)
    assert (stats.exact_sign_min_n(0.75, 0.05), stats.exact_sign_min_n(0.75, 0.025)) == (35, 42)
    rule = lambda d: headroom.sample_size_rule(d, 100)
    assert rule(29)["rule"] == "R1" and rule(28)["rule"] == "R2"                   # kappa * 3 * D* >= 43  <=>  D* >= 29
    assert rule(18)["rule"] == "R2" and rule(17)["rule"] == "R3"                   # kappa * 5 * D* >= 43  <=>  D* >= 18
    assert rule(29)["test_fold"] == 300 and rule(18)["test_fold"] == 500 and rule(17)["test_fold"] == 300
    assert rule(29)["primary_endpoint"] == "Y" and rule(18)["primary_endpoint"] == "Y" and "Wilcoxon" in rule(17)["primary_endpoint"]
    assert rule(30)["expected_discordant_300"] == pytest.approx(45.0) and rule(30)["N_star"] == 43 and rule(30)["kappa"] == 0.5
    assert rule(None)["rule"] == "NO-GO"


def test_n_rule_in_family_json_uses_the_max_discordance_over_passing_corruptions():
    res = headroom.decide(_rows(SPEC))
    dc = {f["key"]: f["D_c"] for f in res["family"]}
    assert dc == {"jpeg5": 5, "splice128": 30}                                  # D_c counts Y flips in either direction between the changed-code gate and none
    assert res["n_rule"]["D_star"] == 30 and res["n_rule"]["rule"] == "R1"
    low = headroom.decide(_rows({k: (v[0], v[1], min(v[2], 20)) for k, v in SPEC.items()}))
    assert low["n_rule"]["D_star"] == 20 and low["n_rule"]["rule"] == "R2" and low["n_rule"]["test_fold"] == 500
    r3 = headroom.decide(_rows({k: (v[0], v[1], min(v[2], 10)) for k, v in SPEC.items()}))
    assert r3["n_rule"]["rule"] == "R3"


def test_headroom_empty_family_is_no_go():
    res = headroom.decide(_rows({k: (0.0, 0.0, 0) for k in SPEC}))
    assert res["family"] == [] and not res["go"] and res["downstream_claim_withdrawn"] and res["n_rule"]["rule"] == "NO-GO" and len(res["excluded"]) == 3


def test_headroom_never_reads_gate_flags():
    rows = _rows(SPEC)
    headroom.assert_blind(rows)
    rows[3]["rungs"]["jpeg5"]["gate0.05"] = dict(y=1)
    with pytest.raises(AssertionError, match="gate"):
        headroom.decide(rows)


def test_headroom_cli_defaults_to_d_and_refuses_a_partial_run(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    (tmp_path / "P2-GATE-M3").mkdir()
    (tmp_path / "P2-GATE-M3" / "items.jsonl").write_text("\n".join(json.dumps(r) for r in _rows(SPEC, n=30)) + "\n")
    assert headroom.main(["--run-id", "P2-GATE-M3"]) == 2                          # 30 < 100 items
    (tmp_path / "P2-GATE-M3" / "items.jsonl").write_text("\n".join(json.dumps(r) for r in _rows(SPEC)) + "\n")
    assert headroom.main(["--run-id", "P2-GATE-M3"]) == 0
    fam = json.loads((tmp_path / "P2-GATE-M3" / "family.json").read_text())
    assert fam["endpoint"] == "d" and [f["key"] for f in fam["family"]] == ["jpeg5", "splice128"] and fam["n_rule"]["rule"] == "R1"


# ------------------------------------------------------------------------------------------------ Prop. 4
def test_prop4_general_form_reduces_to_the_corrected_special_case():
    rng = np.random.default_rng(0)
    for _ in range(300):
        rho, a, b = rng.uniform(0.02, 0.6), rng.uniform(0.0, 0.3), rng.uniform(0.0, 1.0)
        mu, s2, s2c = rng.uniform(0.05, 1), rng.uniform(0.1, 2), rng.uniform(0.1, 4)
        assert theory.gating_helps(1000, rho, a, b, mu, s2, 0.0, s2c) == theory.special_case_inequality(rho, a, b, mu, s2, s2c)


def test_prop4_consequences():
    kw = dict(m=1024, rho=0.3, mu=0.2, sigma2=0.25, mu_c=0.0, sigma2_c=1.0)
    assert theory.gating_helps(alpha=0.0, beta=1.0, **kw)                      # oracle gate helps
    assert not theory.gating_helps(alpha=0.05, beta=0.05, **kw)                # random gate (beta = alpha) lowers SNR
    assert not theory.gating_helps(alpha=0.05, beta=0.0, **{**kw, "rho": 0.0})    # clean input: any gate with alpha > 0 costs a little
    assert theory.gating_helps(alpha=0.05, beta=0.8, **kw)
    # a corrupted mean different from zero changes the verdict: faulty sensors that carry positive evidence are worth keeping
    assert not theory.gating_helps(alpha=0.05, beta=0.8, **{**kw, "mu_c": 0.2, "sigma2_c": 0.25})


def test_prop4_plug_in_estimation():
    rng = np.random.default_rng(1)
    z = rng.random(5000) < 0.3
    delta = np.where(z, rng.normal(0, 1, 5000), rng.normal(0.2, 0.5, 5000))
    flagged = np.where(z, rng.random(5000) < 0.8, rng.random(5000) < 0.05)
    r = theory.plug_in_from_deltas(delta, z, flagged)
    assert r["rho"] == pytest.approx(0.3, abs=0.03) and r["mu"] == pytest.approx(0.2, abs=0.03) and r["alpha_obs"] == pytest.approx(0.05, abs=0.02)
    assert r["predicted_helps"] is True


# ------------------------------------------------------------------------------------------------ detection analysis
def _synth_probe(tmp, n_items=10, q_better=True, seed=0):
    rng = np.random.default_rng(seed)
    p2, m1 = tmp / "P2-PROBE-02", tmp / "P2-GATE-M1"
    (p2 / "arrays").mkdir(parents=True)
    (m1 / "arrays").mkdir(parents=True)
    (p2 / "selection.json").write_text(json.dumps(dict(items=[dict(image_id=i, caption="x", n_tok=5) for i in range(n_items)])))
    for i in range(n_items):
        arrs, m1a = dict(clean=rng.integers(0, 16384, 1024)), {}
        for c in detect.P2_CORRS:
            z = np.zeros(1024, bool)
            z[rng.choice(1024, 150, replace=False)] = True
            B = -2.0 * z + rng.normal(0, 1.5, 1024)
            D = (1.0 * z + rng.normal(0, 0.2, 1024)) if q_better else np.zeros(1024)
            r = rng.normal(0, 0.01, 1024)
            arrs.update({f"{c}_s1": (B + r).astype(np.float32), f"{c}_r_original": r.astype(np.float32), f"{c}_s2": rng.normal(size=1024).astype(np.float32),
                         f"{c}_s3": rng.random(1024).astype(np.float32), f"{c}_codes": rng.integers(0, 16384, 1024), f"{c}_z": z})
            m1a[f"{c}_D"] = D.astype(np.float32)
        np.savez(p2 / "arrays" / f"item{i:04d}.npz", **arrs)
        np.savez(m1 / "arrays" / f"item{i:04d}.npz", **m1a)
    return p2, m1


def test_detection_analysis_orders_scores_and_falsifier_logic(tmp_path):
    p2, m1 = _synth_probe(tmp_path, q_better=True)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=300)
    assert res["n_items"] == 10 and res["has_q"]
    t = res["table"]["jpeg"]
    assert t["q"]["mean"] > t["plainB"]["mean"] > 0.8 and abs(t["random"]["mean"] - 0.5) < 0.06 and abs(t["r_original"]["mean"] - 0.5) < 0.1
    assert t["_n_items"] == 10 and t["_n_excluded"] == 0
    pq = res["paired_q_vs_best_cheap"]["jpeg"]
    assert pq["available"] and pq["best_cheap"] == "plainB" and pq["excludes_zero"] and pq["diff_mean"] > 0
    assert res["falsifier"]["falsified"] is False and res["falsifier"]["q_significantly_better_on"] == ["jpeg", "noise"]
    p2b, m1b = _synth_probe(tmp_path / "b", q_better=False, seed=1)
    res2 = analyze_gate_m1.run_analysis(p2b, m1b, pixels=False, n_boot=300)
    assert res2["falsifier"]["falsified"] is True                                # q == plain-B here: the CI of the difference includes 0 on both
    p2c, m1c = _synth_probe(tmp_path / "c", q_better=True, seed=2)               # q systematically WORSE than plain-B: also falsified, and reported as worse
    for f in (m1c / "arrays").glob("*.npz"):
        d = {k: -np.load(f)[k] * 3 for k in np.load(f).files}
        np.savez(f, **d)
    res4 = analyze_gate_m1.run_analysis(p2c, m1c, pixels=False, n_boot=300)
    assert res4["falsifier"]["falsified"] is True or res4["falsifier"]["q_significantly_better_on"]
    res3 = analyze_gate_m1.run_analysis(p2, None, pixels=False, n_boot=200)      # CPU fallback: no M1 arrays -> no q, labelled exploratory
    assert not res3["has_q"] and "q" not in res3["table"]["jpeg"] and res3["falsifier"]["falsified"] is None and "exploratory" in res3["label"]


def test_ineligible_items_are_excluded_and_counted():
    sus = dict(a=np.arange(10.0))
    z = np.zeros(10, bool)
    z[:3] = True
    r = detect.item_aurocs(sus, z)
    assert np.isnan(r["a"]) and r["_eligible"] == 0.0
    agg = detect.aggregate([{c: r for c in detect.P2_CORRS}])
    assert agg["jpeg"]["_n_excluded"] == 1 and agg["jpeg"]["a"]["n"] == 0


# ------------------------------------------------------------------------------------------------ SAP Addendum 1: detection p-values, Holm m = 2, frozen rival, 179-item sensitivity
def test_bootstrap_p_and_holm_m2_in_the_falsifier(tmp_path):
    assert detect.bootstrap_p(np.zeros(999)) == 1.0
    assert detect.bootstrap_p(np.full(999, 0.1)) == pytest.approx(2 / 1000)
    assert 0.5 < detect.bootstrap_p(np.r_[np.full(500, -0.1), np.full(499, 0.1)]) <= 1.0
    p2, m1 = _synth_probe(tmp_path, n_items=12, q_better=True)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=400)
    f = res["falsifier"]
    assert f["holm_m"] == 2 and f["falsified"] is False
    for c in ("jpeg", "noise"):
        r = f["per_corruption"][c]
        assert {"p", "p_holm", "ci95", "ci975", "diff_mean", "best_cheap", "rival_sign"} <= set(r)
        assert r["p_holm"] == pytest.approx(min(1.0, 2 * r["p"]), abs=1e-9) or r["p_holm"] >= r["p"]          # Holm over two: the smaller p is doubled, the larger is not smaller
        assert r["ci975"][0] <= r["ci95"][0] and r["ci975"][1] >= r["ci95"][1]                                  # the 97.5 percent interval is wider
    assert sorted(f["q_significantly_better_on"]) == ["jpeg", "noise"]


def test_missing_q_on_one_corruption_keeps_it_in_the_family_with_p_equal_one():
    base = {"plainB": 0.7, "tex": 0.6, "q": 0.9}
    per = [{"jpeg": dict(base, _eligible=1.0, _n_corrupted=10.0), "noise": {"plainB": 0.7, "tex": 0.6, "_eligible": 1.0, "_n_corrupted": 10.0}} for _ in range(8)]
    per = [{c: {k: v + 0.01 * (j % 3) for k, v in d.items() if not k.startswith("_")} | {"_eligible": 1.0, "_n_corrupted": 10.0} for c, d in item.items()} for j, item in enumerate(per)]
    f = detect.falsifier(per, "q", n_boot=500)
    assert f["per_corruption"]["noise"]["available"] is False and f["per_corruption"]["jpeg"]["p_holm"] == pytest.approx(min(1.0, 2 * f["per_corruption"]["jpeg"]["p"]))
    assert f["holm_m"] == 2


def test_frozen_rival_records_name_sign_and_is_only_written_from_a_complete_m1(tmp_path, monkeypatch):
    p2, m1 = _synth_probe(tmp_path, n_items=12, q_better=True)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=100)
    fr = res["frozen"]
    assert set(fr) == {"jpeg", "noise"} and fr["jpeg"]["available"] and fr["jpeg"]["rival"] == "plainB" and fr["jpeg"]["sign"] == 1 and fr["jpeg"]["base"] == "plainB"
    assert detect.split_sign("tex_neg") == ("tex", -1) and detect.split_sign("s3") == ("s3", 1)
    monkeypatch.setattr(common, "RUNS", tmp_path)
    assert analyze_gate_m1.main(["--probe-run", "P2-PROBE-02", "--m1-run", "P2-GATE-M1", "--no-pixels", "--boot", "50"]) == 0
    assert not (m1 / "detection_frozen.json").exists()                           # 12 of 200 items: not frozen
    monkeypatch.setattr(analyze_gate_m1, "N_M1", 12)
    assert analyze_gate_m1.main(["--probe-run", "P2-PROBE-02", "--m1-run", "P2-GATE-M1", "--no-pixels", "--boot", "50"]) == 0
    z = json.loads((m1 / "detection_frozen.json").read_text())
    assert z["frozen"]["jpeg"]["rival"] == "plainB" and z["dry_run_items"] == 21 and z["n_items"] == 12


def test_dry_run_items_are_excluded_in_the_sensitivity_and_rival_can_be_reselected(tmp_path):
    p2, m1 = _synth_probe(tmp_path, n_items=24, q_better=True, seed=5)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=200)
    late = res["falsifier_excluding_dry_run_items"]
    assert late["n_items"] == 3 and late["holm_m"] == 2                         # items 21, 22, 23 of 24: the first 21 are the dry run
    assert late["per_corruption"]["jpeg"]["n_items"] == 3
    rs = res["falsifier_rival_reselected_in_each_resample"]
    assert rs["reselect"] is True and rs["per_corruption"]["jpeg"]["reselect"] is True
    assert rs["per_corruption"]["jpeg"]["diff_mean"] == pytest.approx(res["falsifier"]["per_corruption"]["jpeg"]["diff_mean"])
    assert rs["per_corruption"]["jpeg"]["ci95"][1] <= res["falsifier"]["per_corruption"]["jpeg"]["ci95"][1] + 1e-9      # re-selection can only lower the difference's upper tail


# ------------------------------------------------------------------------------------------------ tolerant probe-2 loader (N16)
def test_tolerant_reader_recovers_rows_from_glued_lines_and_reports_losses(tmp_path):
    from exp_p2.gate import jsonl
    p = tmp_path / "items.jsonl"
    good = lambda i: json.dumps(dict(idx=i, corr={"swap": {"n_corrupted": 3}}, seconds=1.0))
    p.write_text(good(0) + "\n" + '{"idx": 1, "corr": {"swap": {"n_cor' + good(2) + "\n" + good(3) + "\n" + '{"idx": 4, "co' + "\n" + good(5) + "\n")
    rows, rep = jsonl.read_jsonl_tolerant(p)
    assert [r["idx"] for r in rows] == [0, 2, 3, 5]                               # idx 1 and 4 were torn and are lost; the row glued behind the torn one (idx 2) is recovered
    assert rep["n_lines"] == 5
    assert rep["n_clean_lines"] == 3 and rep["n_glued_lines"] == 1 and rep["n_recovered_rows"] == 1 and rep["n_unparseable_lines"] == 1
    r2 = jsonl.probe2_row_report(tmp_path, [0, 1, 2, 3, 4, 5])
    assert r2["rows_lost_arrays_present"] == [1, 4] and r2["n_rows"] == 4 and r2["n_array_items"] == 6
    assert common.read_jsonl(p) != rows and len(common.read_jsonl(p)) == 3          # the strict reader (used by the probes) loses the glued row as well
    assert jsonl.read_jsonl_tolerant(tmp_path / "nope.jsonl")[1]["exists"] is False


def test_tolerant_reader_does_not_mistake_inner_objects_for_rows(tmp_path):
    from exp_p2.gate import jsonl
    p = tmp_path / "x.jsonl"
    p.write_text('{"idx": 7, "corr": {"swap": {"n_corrupted": 3, "frac": 0.1}, "patch": {"n_cor' + "\n")
    rows, rep = jsonl.read_jsonl_tolerant(p)
    assert rows == [] and rep["n_unparseable_lines"] == 1


def test_run_analysis_reports_lost_probe2_rows(tmp_path):
    p2, m1 = _synth_probe(tmp_path, n_items=6, q_better=True)
    good = lambda i: json.dumps(dict(idx=i, seconds=1.0))
    (p2 / "items.jsonl").write_text(good(0) + "\n" + '{"idx": 1, "se' + good(2) + "\n" + good(3) + "\n" + good(4) + "\n")
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=50)
    rr = res["rows_report"]
    assert res["n_items"] == 6 and rr["rows_lost_arrays_present"] == [1, 5] and rr["n_glued_lines"] == 1 and rr["n_rows"] == 4


# ------------------------------------------------------------------------------------------------ write-once artifacts (audit M6) and freezing only from a complete q (M8)
def test_write_once_refuses_then_amends_with_a_log(tmp_path):
    from exp_p2.gate import artifacts
    f = tmp_path / "family.json"
    artifacts.write_once(f, "v1")
    with pytest.raises(artifacts.WriteOnceError, match="--force"):
        artifacts.write_once(f, "v2")
    assert f.read_text() == "v1"
    artifacts.write_once(f, "v2", force=True)
    assert f.read_text() == "v2"
    assert len(list(tmp_path.glob("family.json.prev-*"))) == 1 and list(tmp_path.glob("family.json.prev-*"))[0].read_text() == "v1"
    line = json.loads((tmp_path / "amendments.jsonl").read_text().splitlines()[-1])
    assert line["file"] == "family.json" and line["old_sha1"] != line["new_sha1"]


def test_headroom_fit_threshold_and_freeze_are_write_once(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    (tmp_path / "P2-GATE-M3").mkdir()
    (tmp_path / "P2-GATE-M3" / "items.jsonl").write_text("\n".join(json.dumps(r) for r in _rows(SPEC)) + "\n")
    assert headroom.main(["--run-id", "P2-GATE-M3"]) == 0
    first = (tmp_path / "P2-GATE-M3" / "family.json").read_text()
    assert headroom.main(["--run-id", "P2-GATE-M3"]) == 2 and (tmp_path / "P2-GATE-M3" / "family.json").read_text() == first
    assert headroom.main(["--run-id", "P2-GATE-M3", "--force"]) == 0 and (tmp_path / "P2-GATE-M3" / "amendments.jsonl").exists()
    # threshold
    from exp_p2.gate import fit_threshold
    m2 = tmp_path / "P2-GATE-M2"
    (m2 / "arrays").mkdir(parents=True)
    rng = np.random.default_rng(0)
    rows = []
    for i in range(24):
        np.savez(m2 / "arrays" / f"item{i:04d}.npz", B=rng.normal(-3, 1, 16).astype(np.float32), D=rng.normal(-2, .2, 16).astype(np.float32), codes=rng.integers(0, 50, 16))
        rows.append(dict(idx=i, gid=i))
    (m2 / "items.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    assert fit_threshold.main(["--run-id", "P2-GATE-M2", "--min-items", "24"]) == 0
    assert fit_threshold.main(["--run-id", "P2-GATE-M2", "--min-items", "24"]) == 2
    assert fit_threshold.main(["--run-id", "P2-GATE-M2", "--min-items", "24", "--force"]) == 0
    # freeze needs q for ALL items
    p2, m1 = _synth_probe(tmp_path / "x", n_items=12, q_better=True)
    monkeypatch.setattr(common, "RUNS", tmp_path / "x")
    monkeypatch.setattr(analyze_gate_m1, "N_M1", 12)
    f = dict(np.load(m1 / "arrays" / "item0005.npz"))
    np.savez(m1 / "arrays" / "item0005.npz", **{k: v for k, v in f.items() if not k.startswith("swap")})            # one item loses its q for one corruption
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "50"]) == 0
    assert not (m1 / "detection_frozen.json").exists()                          # 11 of 12 items with a complete q
    np.savez(m1 / "arrays" / "item0005.npz", **f)
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "50"]) == 0 and (m1 / "detection_frozen.json").exists()
    z = json.loads((m1 / "detection_frozen.json").read_text())
    assert z["meta"]["root_seed"] == 20261028 and "numpy_version" in z["meta"]
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "50"]) == 2           # write-once
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "50", "--force"]) == 0


# ------------------------------------------------------------------------------------------------ fusion
def test_L3_uninformative_direction_gets_zero_lda_weight_and_stouffer_is_symmetric():
    rng = np.random.default_rng(0)
    n = 1000
    informative = rng.normal(1.0, 1.0, n)                                       # margin of the useful direction: mean 1
    useless = rng.normal(0.0, 1.0, n)                                           # independent model: margin symmetric about 0
    w = fusion.lda_weights(np.stack([informative, useless], 1))
    assert abs(w[1]) < 0.1 * abs(w[0])
    sw = fusion.stouffer_weights(np.stack([informative, informative * 2 + rng.normal(0, 0.1, n)], 1))
    assert sw["r"] > 0.95 and sw["w"][0] > 0 and sw["w"][1] > 0
    both = fusion.fused_accuracy(np.stack([informative, useless], 1), w)
    assert both == pytest.approx(float(np.mean(informative > 0)), abs=0.03)


# ------------------------------------------------------------------------------------------------ coherence summary
def test_coherence_summary_reading():
    s = checks_summary(np.full(100, 0.001), np.linspace(-0.01, 0.01, 50), 0.1)
    assert s["coherent_within_noise"] and not s["incoherent_at_evidence_scale"]
    s = checks_summary(np.full(100, 0.5), np.linspace(-0.01, 0.01, 50), 0.1)
    assert not s["coherent_within_noise"] and s["incoherent_at_evidence_scale"]
    assert checks_summary(np.array([0.5]), np.array([]), None)["incoherent_at_evidence_scale"] is None


def checks_summary(g, g0, mu):
    from exp_p2.gate import checks
    return checks.coherence_summary(g, g0, mu)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
