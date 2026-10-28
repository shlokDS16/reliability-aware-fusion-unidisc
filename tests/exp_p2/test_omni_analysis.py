"""CPU tests of exp_p2/gate/analysis_omni.py: the GO rule and n rule of SAP AD.7 / AB.5 on synthetic timing logs (hand-computed), the pass-count derivation, the positive control, the
threshold fit, and omni_r (eligibility from P, McNemar, Holm over |P+|, wording)."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from exp_p2 import common                                                          # noqa: E402
from exp_p2.gate import analysis_omni as ao, stats                                  # noqa: E402

SIG = dict(signed_by="gate-auditor", verdict="PASS")
SEL = dict(ids_equal=True, adapter=dict(all_ok=True, failed=[], results=[dict(id=f"A{i}", ok=True, detail=(dict(per_shift={"1": dict(mean_logp=-3.0, top1=0.2)}) if i == 5 else {})) for i in range(1, 8)]))


def timing(t=0.3, peak=6400.0, n=20):
    return [dict(idx=i, fwd_s=(5.0 if i < 5 else t), peak_alloc_mib=peak, finite=True) for i in range(n)]


M2 = [dict(idx=i, n_rows=12) for i in range(10)]
M4 = [dict(idx=i, n_rows=75, conds={"clean": {"kind": "clean"}, "jpeg10": {"kind": "pixel"}, "jpeg10_dn": {"kind": "denoise"}, "patch": {"kind": "token"}}) for i in range(10)]
KW = dict(adapter_signature=SIG, selfcheck=SEL, guard_cap_mib=7500.0)


def test_t_is_the_median_of_passes_6_to_20_not_the_warmup():
    t = ao.timing_t(timing(0.3))
    assert t["complete"] and abs(t["t_seconds"] - 0.3) < 1e-12 and t["n_used"] == 15
    rows = timing(0.3)
    rows[7]["fwd_s"] = 99.0                                                              # one outlier does not move the median
    assert abs(ao.timing_t(rows)["t_seconds"] - 0.3) < 1e-12
    assert not ao.timing_t(timing(0.3, n=12))["complete"]


def test_pass_counts_from_logs_and_the_flagged_fallbacks():
    pc = ao.pass_counts(M2, M4)
    assert pc["p_cal"] == 12 and pc["p_test"] == 25 and pc["p_B"] == 8                    # 75 passes / 3 gated conditions (clean, jpeg10, patch; the denoised copy is not gated)
    assert "median" in pc["p_cal_source"]
    pc2 = ao.pass_counts([dict(idx=0)], M4)
    assert pc2["p_cal"] == 12 and "docstring" in pc2["p_cal_source"]
    pc3 = ao.pass_counts(M2, [dict(idx=0, conds={})])
    assert pc3["p_test"] is None
    assert ao.pass_counts(M2, M4, p_cal=10, p_test=20)["p_test"] == 20


def test_T_formula_by_hand():
    pc = dict(p_cal=12, p_test=25, p_B=8)
    assert abs(ao.T_hours(0.3, 150, 2, pc) - 0.3 * (1200 + 150 * 25 * 3 + 400) / 3600) < 1e-12
    assert abs(ao.T_hours(0.3, 120, 1, pc) - 0.3 * (1200 + 120 * 25 * 2 + 400) / 3600) < 1e-12


def test_go_rule_and_n_rule():
    g = ao.omni_gate(timing(0.3), M2, M4, n_plus=2, time_left_h=10.0, **KW)
    assert g["go"] and g["n_R"] == 150 and abs(g["T_hours"]["150"] - 1.0708333333) < 1e-9
    g = ao.omni_gate(timing(0.6), M2, M4, n_plus=1, time_left_h=10.0, **KW)                # T(150) = 1.517 > 1.5, T(120) = 1.267
    assert g["go"] and g["n_R"] == 120 and g["conditions"]["d"]["per_n"] == {"150": False, "120": True}
    g = ao.omni_gate(timing(1.0), M2, M4, n_plus=1, time_left_h=10.0, **KW)                # T(120) = 2.11 > 1.5
    assert not g["go"] and g["n_R"] is None and not g["conditions"]["d"]["ok"]
    g = ao.omni_gate(timing(0.3), M2, M4, n_plus=2, time_left_h=2.0, **KW)                 # 2 T(150) = 2.14 > 2, 2 T(120) = 1.89 <= 2
    assert g["go"] and g["n_R"] == 120 and g["conditions"]["e"]["per_n"] == {"150": False, "120": True}
    g = ao.omni_gate(timing(0.3), M2, M4, n_plus=2, time_left_h=1.0, **KW)
    assert not g["go"] and not g["conditions"]["e"]["ok"]


def test_each_go_condition_can_fail_alone():
    ok = dict(timing=timing(0.3), m2_log=M2, m4_log=M4, n_plus=1, time_left_h=10.0)
    def run(**over):
        a = dict(ok, **KW)
        a.update(over)
        return ao.omni_gate(a.pop("timing"), a.pop("m2_log"), a.pop("m4_log"), **a)
    assert run()["go"]
    assert not run(timing=timing(0.3, n=19))["go"] and not run(timing=timing(0.3, n=19))["conditions"]["a"]["ok"]            # (a) fewer than 20 passes
    assert not run(chunk_events=[dict(event="guard_stop", reason="gpu_memory")])["conditions"]["a"]["ok"]                    # (a) a guard stop
    assert not run(crash_events=[dict(id=41)])["conditions"]["a"]["ok"]                                                      # (a) a crash-log event
    assert not run(adapter_signature=None)["conditions"]["b"]["ok"]                                                          # (b) unsigned
    assert not run(adapter_signature=dict(signed_by="lab-engineer", verdict="PASS"))["conditions"]["b"]["ok"]                # (b) signed by the author's role
    assert not run(selfcheck=dict(ids_equal=True, adapter=dict(all_ok=False, failed=["A5"])))["conditions"]["b"]["ok"]       # (b) a failed check
    assert not run(guard_cap_mib=6000.0)["conditions"]["c"]["ok"]                                                            # (c) peak 6400 over the cap
    assert not run(guard_cap_mib=None)["conditions"]["c"]["ok"]
    assert not run(m4_log=[dict(idx=0, conds={})])["go"]                                                                     # no derivable p_test: no invention
    r = ao.omni_gate(timing(0.3), M2, M4, n_plus=0, time_left_h=10.0, **KW)
    assert r["status"] == "not_run" and not r["go"]


# ------------------------------------------------------------------------------------------------ calibration and positive control
def _write_run(tmp, name, rows, arrays):
    d = tmp / name
    (d / "arrays").mkdir(parents=True)
    for r, arr in zip(rows, arrays):
        np.savez(d / "arrays" / f"item{r['idx']:04d}.npz", **arr)
        common.append_jsonl(d / "items.jsonl", r)
    return d


def test_threshold_fit_alpha_005_only_and_write_once(tmp_path):
    rng = np.random.default_rng(0)
    rows = [dict(idx=i, gid=i) for i in range(30)]
    arrays = [dict(codes=rng.integers(0, 8192, 16).astype(np.int16), B=-rng.gamma(2, 1, 16).astype(np.float32), D=-rng.gamma(2, 1, 16).astype(np.float32), s3=rng.random(16).astype(np.float32)) for _ in rows]
    d = _write_run(tmp_path, "cal", rows, arrays)
    res = ao.fit_omni_threshold(d)
    assert set(res["thresholds"]) == {"0.05"} and res["n_cal"] == 30 and res["thresholds"]["0.05"]["feasible"]
    with pytest.raises(Exception):
        ao.fit_omni_threshold(d)                                                              # write-once


def test_positive_control_passes_on_informative_B_and_fails_at_chance(tmp_path):
    rng = np.random.default_rng(1)
    rows = [dict(idx=i, gid=i) for i in range(40)]
    informative, chance = [], []
    for _ in rows:
        z = np.zeros(64, bool)
        z[rng.choice(64, 6, replace=False)] = True
        B = -rng.gamma(2, 1, 64) - 3.0 * z                                                    # corrupted tokens have lower B
        informative.append(dict(B=B.astype(np.float32), z=z))
        chance.append(dict(B=(-rng.gamma(2, 1, 64)).astype(np.float32), z=z))
    p1 = ao.omni_positive_control(_write_run(tmp_path, "pos1", rows, informative), n_boot=2000)
    p2 = ao.omni_positive_control(_write_run(tmp_path, "pos2", rows, chance), n_boot=2000)
    assert p1["passed"] and p1["lower_bound"] > 0.5 and not p2["passed"] and p2["lower_bound"] <= 0.5
    assert (tmp_path / "pos1" / "pos_control.json").exists() and p1["n_finite"] == 40


# ------------------------------------------------------------------------------------------------ omni_r
def _rows(n, jpeg_b=0, jpeg_c=0, noise_b=0, noise_c=0, n_flag_clean=13):
    """Rows with conds clean / jpeg10 / noise0.1; the none arm and the GATE-M arm differ on b + c items (b: GATE right, none wrong)."""
    out = []
    for i in range(n):
        def cond(kind, yn, yg, nf):
            return dict(kind=kind, n_tokens=256, img={"none": dict(n=256, y=yn, mean=0.1, sd=1.0, z=1.0, d=0.1), "gate0.05": dict(n=250, y=yg, mean=0.1, sd=1.0, z=1.0, d=0.1)},
                        gate={"0.05": dict(n_flag=nf, n_tp=0, n_corrupted=0, n_fp_on_clean_tokens=nf)})
        def pair(b, c):                                                                    # (none, gate): b = GATE right and none wrong, c = the reverse, else both right
            return (0, 1) if i < b else ((1, 0) if i < b + c else (1, 1))
        j, k = pair(jpeg_b, jpeg_c), pair(noise_b, noise_c)
        out.append(dict(idx=300 + i, conds={"clean": cond("clean", 1, 1, n_flag_clean), "jpeg10": cond("pixel", j[0], j[1], 5), "noise0.1": cond("pixel", k[0], k[1], 5)}))
    return out


def P_result(**gb):
    return {"primary": {"per_corruption": {c: {"gate_better": bool(gb.get(c, False))} for c in ("jpeg", "noise", "splice")}}}


def test_p_plus_and_empty_p_means_not_run():
    assert ao.p_plus(P_result(jpeg=True, splice=True)) == ["jpeg", "splice"]
    assert ao.p_plus({"primary": P_result(noise=True)["primary"]}) == ["noise"]
    r = ao.omni_r(_rows(10), P_result(), n_boot=200)
    assert r["status"] == "not_run" and r["p_plus"] == []


def test_omni_r_mcnemar_holm_over_p_plus_and_wording():
    rows = _rows(150, jpeg_b=14, jpeg_c=2, noise_b=3, noise_c=3)                          # jpeg: b = 14, c = 2 ; noise: 3 vs 3
    r = ao.omni_r(rows, P_result(jpeg=True, noise=True), rule="R1", n_boot=500)
    assert r["status"] == "analysed" and r["holm_m"] == 2 and r["formal"] and r["completed_n"] == 150
    j, nz = r["per_corruption"]["jpeg"], r["per_corruption"]["noise"]
    assert (j["b"], j["c"]) == (14, 2) and abs(j["p"] - stats.mcnemar_exact([1] * 14 + [0] * 2, [0] * 14 + [1] * 2)["p"]) < 1e-12
    assert abs(j["p_holm"] - min(1.0, 2 * j["p"])) < 1e-12 and j["replicated"] and not nz["replicated"]
    assert r["replicated_any"] and r["wording"] == ao.WORDING_REPLICATED
    r2 = ao.omni_r(rows, P_result(jpeg=True, noise=True), rule="R2", n_boot=200)
    assert r2["wording"].endswith(ao.WORDING_R2_TAIL)
    assert "generalis" not in r["wording"] and "negative" not in r["wording"]


def test_omni_r_not_replicated_small_n_descriptive_and_pipeline_defect():
    rows = _rows(150, jpeg_b=5, jpeg_c=4)
    r = ao.omni_r(rows, P_result(jpeg=True), n_boot=200)
    assert r["formal"] and not r["replicated_any"] and r["wording"] == ao.WORDING_NOT
    r = ao.omni_r(_rows(100, jpeg_b=20, jpeg_c=0), P_result(jpeg=True), n_boot=200)       # n = 100 < 120
    assert not r["formal"] and not r["replicated_any"] and r["wording"].startswith("descriptive only")
    r = ao.omni_r(rows, P_result(jpeg=True), pos_control=dict(passed=False), n_boot=200)
    assert r["status"] == "pipeline_defect"
    r = ao.omni_r(rows, P_result(splice=True), n_boot=200)                                 # P+ = splice but no splice rows: p = 1 stays in the family
    assert r["per_corruption"]["splice"]["p"] == 1.0 and not r["per_corruption"]["splice"]["tested"]


def test_omni_r_descriptives_clean_flag_share_and_accuracy_drop():
    rows = _rows(150, jpeg_b=14, jpeg_c=2, n_flag_clean=13)
    d = ao.omni_r(rows, P_result(jpeg=True), n_boot=200)["descriptive"]["jpeg"]
    assert abs(d["flagged_share_on_clean_test_items"] - 13 / 256) < 1e-12
    assert d["none_acc_clean"] == 1.0 and abs(d["none_accuracy_drop"] - (1.0 - d["none_acc_corrupted"])) < 1e-12


def test_selftest_function():
    s = ao.selftest()
    assert s["go_150"] and s["n120"] == 120 and s["nogo_slow"] and s["time_rule_n"] == 120


# ------------------------------------------------------------------------------------------------ code audit part 3: M-1 (wording) and M-2 (A1..A7 required)
def test_r3_never_says_directional_replication_and_uses_the_a3b4_item7_sentence():
    rows = _rows(150, jpeg_b=14, jpeg_c=2, noise_b=3, noise_c=3)
    r1 = ao.omni_r(rows, P_result(jpeg=True, noise=True), rule="R1", n_boot=300)
    r3 = ao.omni_r(rows, P_result(jpeg=True, noise=True), rule="R3", n_boot=300)
    assert r1["wording"] == ao.WORDING_REPLICATED and r1["directional_replication_available"] is True and r1["replicated_any"] is True
    assert r3["wording"] == ao.WORDING_R3_ACCOMPANIED and "directional replication" not in r3["wording"] and r3["directional_replication_available"] is False
    assert r3["replicated_any"] is None and r3["accompanied_any"] is True and "A3b.4 item 7" in r3["forbidden"]
    r3n = ao.omni_r(_rows(150, jpeg_b=5, jpeg_c=4), P_result(jpeg=True), rule="R3", n_boot=200)
    assert r3n["wording"].startswith(ao.WORDING_R3_NOT.split(";")[0]) and "was not accompanied" in r3n["wording"] and r3n["accompanied_any"] is False
    r3d = ao.omni_r(_rows(100, jpeg_b=20, jpeg_c=0), P_result(jpeg=True), rule="R3", n_boot=200)       # n = 100 < 120: descriptive under R3 too
    assert r3d["wording"].startswith("descriptive only")


def test_a_rejection_with_b_below_c_refutes_the_direction():
    rows = _rows(150, jpeg_b=2, jpeg_c=14)
    r = ao.omni_r(rows, P_result(jpeg=True), rule="R1", n_boot=300)
    j = r["per_corruption"]["jpeg"]
    assert j["p_holm"] < 0.05 and j["refutes_direction"] and not j["replicated"] and r["refutes_direction_any"]
    assert ao.WORDING_REFUTES in r["wording"] and r["wording"].startswith(ao.WORDING_NOT) and not r["replicated_any"]
    r3 = ao.omni_r(rows, P_result(jpeg=True), rule="R3", n_boot=300)
    assert ao.WORDING_REFUTES in r3["wording"]
    ok = ao.omni_r(_rows(150, jpeg_b=14, jpeg_c=2), P_result(jpeg=True), rule="R1", n_boot=300)
    assert not ok["refutes_direction_any"] and ao.WORDING_REFUTES not in ok["wording"]


def test_every_r_result_carries_the_confound_list_and_the_positive_control_wording():
    for rule in ("R1", "R2", "R3"):
        r = ao.omni_r(_rows(150, jpeg_b=5, jpeg_c=4), P_result(jpeg=True), rule=rule, n_boot=200)
        assert r["confounds"] == ao.CONFOUNDS and len(r["confounds"]) == 6 and "4-bit quantisation" in r["confounds"][0]
        pcw = r["positive_control_wording"]
        assert "not at chance on the patch corruption at code level, without the encode path" in pcw and "512 px" in pcw and "never saw in training" in pcw
        assert "independently verified" in r["forbidden"]


def test_go_rule_b_requires_a1_to_a7_present_and_ok():
    ok = dict(timing=timing(0.3), m2_log=M2, m4_log=M4, n_plus=1, time_left_h=10.0)

    def run(sel):
        return ao.omni_gate(ok["timing"], ok["m2_log"], ok["m4_log"], n_plus=1, time_left_h=10.0, adapter_signature=SIG, selfcheck=sel, guard_cap_mib=7500.0)
    assert run(SEL)["go"] and run(SEL)["conditions"]["b"]["checks_missing"] == []
    only_123 = dict(ids_equal=True, adapter=dict(all_ok=True, failed=[], results=[dict(id=f"A{i}", ok=True) for i in (1, 2, 3)]))             # what --skip-gpu-adapter-checks produces
    r = run(only_123)
    assert not r["go"] and not r["conditions"]["b"]["ok"] and r["conditions"]["b"]["checks_missing"] == ["A4", "A5", "A6", "A7"]
    assert not run(dict(ids_equal=True, adapter=dict(all_ok=True, failed=[])))["go"]                                                          # no results list at all
    dup = dict(ids_equal=True, adapter=dict(all_ok=True, failed=[], results=[dict(id=f"A{i}", ok=True) for i in (1, 2, 3, 4, 5, 6, 7, 7)]))
    assert not run(dup)["go"]
    one_bad = dict(ids_equal=True, adapter=dict(all_ok=True, failed=[], results=[dict(id=f"A{i}", ok=(i != 5)) for i in range(1, 8)]))        # all_ok field lying
    assert not run(one_bad)["go"]
    assert ao.selfcheck_ok(SEL) and not ao.selfcheck_ok(None) and not ao.selfcheck_ok(dict(SEL, ids_equal=False))
