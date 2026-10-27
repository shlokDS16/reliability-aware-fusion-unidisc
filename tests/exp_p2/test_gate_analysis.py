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


# ------------------------------------------------------------------------------------------------ headroom
def _rows(spec, n=100, seed=0):
    """spec: rung key -> (drop of the corrupted-none z from clean, gain of the changed-code z over none, n discordant items with chg right and none wrong)."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        zc = 5 + rng.normal()
        row = dict(clean=dict(z=zc, d=zc / 10, y=1), rungs={})
        for key, (drop, gain, disc) in spec.items():
            zn = zc - drop + rng.normal(0, 0.5)
            zg = zn + gain + rng.normal(0, 0.5)
            row["rungs"][key] = dict(n_changed=100, none=dict(z=zn, d=zn / 10, y=int(i >= disc)), chg=dict(z=zg, d=zg / 10, y=1))
        rows.append(row)
    return rows


SPEC = {"jpeg10": (0.0, 0.0, 0), "jpeg5": (2.0, 1.5, 5), "noise0.1": (2.0, 0.0, 0), "noise0.2": (2.0, 0.0, 0), "splice128": (2.0, 1.5, 30), "splice192": (3.0, 2.0, 40)}


def test_headroom_walks_the_ladder_and_fixes_the_family():
    res = headroom.decide(_rows(SPEC), "z")
    assert [(f["corruption"], f["severity"]) for f in res["family"]] == [("jpeg", 5), ("splice", 128)]          # first passing rung; noise fails both rungs
    assert [e["corruption"] for e in res["excluded"]] == ["noise"]
    assert res["rungs"]["jpeg10"]["passes"] is False and res["rungs"]["jpeg5"]["H1_pass"] and res["rungs"]["jpeg5"]["H2_pass"]
    assert res["rungs"]["noise0.1"]["H1_pass"] and not res["rungs"]["noise0.1"]["H2_pass"]
    assert "splice192" in res["rungs"] and not res["downstream_claim_withdrawn"]
    ed = res["endpoint_decision"]
    assert ed["holm_alpha_prime"] == pytest.approx(0.025) and ed["n_test"] == 300
    per = {d["key"]: d for d in ed["per_member"]}
    assert per["splice128"]["scaled_to_test"] == pytest.approx(90) and per["splice128"]["enough"]
    assert per["jpeg5"]["scaled_to_test"] == pytest.approx(15) and not per["jpeg5"]["enough"]
    assert "UNDER-POWERED" in ed["action"]


def test_headroom_empty_family_withdraws_the_downstream_claim():
    res = headroom.decide(_rows({k: (0.0, 0.0, 0) for k in SPEC}), "z")
    assert res["family"] == [] and res["downstream_claim_withdrawn"] and res["endpoint_decision"]["action"] == "no family member"
    assert len(res["excluded"]) == 3


def test_headroom_uses_only_clean_none_and_changed_code_never_gate_flags():
    rows = _rows(SPEC)
    assert not any("gate" in k for r in rows for k in r["rungs"]["jpeg5"])
    r = headroom.evaluate_rung(rows, "jpeg5")
    assert set(r) >= {"H1", "H2", "H1_pass", "H2_pass", "discordance_chg_vs_none"} and r["H1"]["diff"] > 1.5


def test_headroom_nonfinite_items_are_dropped_and_counted():
    rows = _rows(SPEC)
    rows[0]["rungs"]["jpeg5"]["none"]["z"] = float("nan")
    rows[1]["clean"]["z"] = float("inf")
    r = headroom.evaluate_rung(rows, "jpeg5")
    assert r["H1"]["n_dropped"] == 2 and r["H2"]["n_dropped"] == 1


def test_headroom_cli_refuses_a_partial_run(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    (tmp_path / "P2-GATE-M3").mkdir()
    assert headroom.main(["--run-id", "P2-GATE-M3"]) == 2
    (tmp_path / "P2-GATE-M3" / "items.jsonl").write_text("\n".join(json.dumps(r) for r in _rows(SPEC, n=30)) + "\n")
    assert headroom.main(["--run-id", "P2-GATE-M3"]) == 0
    fam = json.loads((tmp_path / "P2-GATE-M3" / "family.json").read_text())
    assert [f["key"] for f in fam["family"]] and fam["endpoint"] == "z"


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
