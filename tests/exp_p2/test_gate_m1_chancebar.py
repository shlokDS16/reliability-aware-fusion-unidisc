"""The patch/swap chance bar of M1 (SAP AB.7 item 3 as completed by A3b.5 and A3b.5a): two pools (the closed prefix and the items after the 21 dry-run items), a cell-pool is decided only at
n >= 100, verdict PASSED / FAILED / UNDECIDED recomputed from the per-cell n and lower95. SYNTHETIC DATA ONLY: nothing under runs/P2-PROBE-02 or runs/P2-GATE-M1 is read by these tests
(blinding attestation). CPU only."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import analyze_gate_m1                                           # noqa: E402
from exp_p2.gate import detect                                               # noqa: E402

N_TOK = 1024
CELLS = analyze_gate_m1.CHANCE_CELLS


def _cb(n=200, lower=0.9, mean=None, overrides=None, drop=()):
    """A detect.chance_bar-shaped result; `overrides[cell]` = dict of fields replacing the default for that cell; `drop` = cells missing from the table. The `passes` fields are deliberately
    set from `lower` only so that a test can also make them lie (see test_the_passes_fields_of_the_inputs_are_ignored)."""
    per = {}
    for k in CELLS:
        if k in drop:
            continue
        v = dict(available=True, n=n, mean=(lower + 0.05 if mean is None else mean), lower95=lower, upper95=0.99, passes=bool(lower > 0.5))
        v.update((overrides or {}).get(k, {}))
        per[k] = v
    return dict(per_score=per, passes=True, failed=False, audit_trigger=False)


def test_min_n_is_one_constant_shared_with_the_partial_floor():
    assert analyze_gate_m1.MIN_N_PARTIAL == analyze_gate_m1.MIN_N_CHANCE_BAR == 100 and CELLS == ("patch/plainB", "patch/q", "swap/plainB", "swap/q")


def test_passed_only_when_every_cell_is_decided_and_passes_in_both_pools():
    r = analyze_gate_m1.combine_chance_bars(_cb(200), _cb(179), 200, 179)
    assert r["verdict"] == "PASSED" and r["passes"] is True and not r["failed"] and not r["audit_trigger"] and r["complete"] is True and r["min_n"] == 100
    assert r["n_all"] == 200 and r["n_late"] == 179 and all(v["result"] == "pass" and v["passes_both"] is True for v in r["per_score"].values())
    assert r["per_score"]["swap/q"]["n_all_cell"] == 200 and r["per_score"]["swap/q"]["n_late_cell"] == 179 and r["per_score"]["swap/q"]["status_late"] == "decided_pass"


def test_the_stopped_prefix_of_106_items_is_undecided_whatever_the_bounds_are():
    r = analyze_gate_m1.combine_chance_bars(_cb(106, lower=0.9), _cb(85, lower=0.9), 106, 85)
    assert r["verdict"] == "UNDECIDED" and r["passes"] is None and not r["failed"] and not r["audit_trigger"] and r["complete"] is False
    assert all(v["status_all"] == "decided_pass" and v["status_late"] == "undecided" for v in r["per_score"].values())


def test_the_floor_is_100_exactly():
    assert analyze_gate_m1.combine_chance_bars(_cb(150), _cb(100), 150, 100)["verdict"] == "PASSED"
    r = analyze_gate_m1.combine_chance_bars(_cb(150), _cb(99), 150, 99)
    assert r["verdict"] == "UNDECIDED" and r["per_score"]["patch/q"]["status_late"] == "undecided"
    low = analyze_gate_m1.combine_chance_bars(_cb(150), _cb(99, lower=0.3), 150, 99)               # a bound below 0.5 at n = 99 is printed but does not decide
    assert low["verdict"] == "UNDECIDED" and not low["failed"]


def test_a_decided_failure_dominates_an_undecided_cell():
    late = _cb(110, overrides={"swap/plainB": dict(lower95=0.48, mean=0.52, passes=False), "patch/q": dict(n=60)})
    r = analyze_gate_m1.combine_chance_bars(_cb(130), late, 130, 110)
    assert r["verdict"] == "FAILED" and r["passes"] is False and r["failed"] and r["audit_trigger"]
    assert r["per_score"]["swap/plainB"]["result"] == "fail" and r["per_score"]["patch/q"]["result"] == "undecided"


def test_a_cell_failing_in_the_all_pool_but_undecided_in_the_late_pool_fails():
    r = analyze_gate_m1.combine_chance_bars(_cb(130, overrides={"patch/plainB": dict(lower95=0.4, mean=0.45)}), _cb(85), 130, 85)
    assert r["verdict"] == "FAILED" and r["per_score"]["patch/plainB"]["status_all"] == "decided_fail" and r["per_score"]["patch/plainB"]["status_late"] == "undecided"


def test_a_q_cell_below_the_floor_leaves_the_bar_undecided_while_plain_b_cells_pass():
    q_short = {"patch/q": dict(n=90), "swap/q": dict(n=90)}
    r = analyze_gate_m1.combine_chance_bars(_cb(200, overrides=q_short), _cb(179, overrides=q_short), 200, 179)
    assert r["verdict"] == "UNDECIDED" and r["per_score"]["patch/plainB"]["result"] == "pass" and r["per_score"]["swap/q"]["result"] == "undecided"


def test_without_a_late_pool_the_bar_is_undecided_or_failed_by_a_decided_failure():
    r = analyze_gate_m1.combine_chance_bars(_cb(120), None, 120, 0)
    assert r["verdict"] == "UNDECIDED" and r["passes"] is None and all(v["status_late"] == "undecided" and v["late"] is None for v in r["per_score"].values())
    r = analyze_gate_m1.combine_chance_bars(_cb(120, overrides={"swap/q": dict(lower95=0.4, mean=0.45)}), None, 120, 0)
    assert r["verdict"] == "FAILED" and r["failed"]


def test_a_missing_cell_key_is_undecided_never_skipped():
    r = analyze_gate_m1.combine_chance_bars(_cb(200, drop=("swap/q",)), _cb(179), 200, 179)
    assert r["verdict"] == "UNDECIDED" and r["per_score"]["swap/q"]["result"] == "undecided" and r["per_score"]["swap/q"]["all"] is None


def test_the_passes_fields_of_the_inputs_are_ignored():
    bad = _cb(200, overrides={"patch/q": dict(lower95=0.45, mean=0.5, passes=True)})              # claims a pass with a bound below 0.5
    bad["passes"], bad["failed"] = True, False
    assert analyze_gate_m1.combine_chance_bars(bad, _cb(179), 200, 179)["verdict"] == "FAILED"
    ok = _cb(200)
    ok["passes"], ok["failed"] = False, True                                                       # claims a failure although every cell passes
    assert analyze_gate_m1.combine_chance_bars(ok, _cb(179), 200, 179)["verdict"] == "PASSED"
    nan = _cb(200, overrides={"patch/q": dict(lower95=None)})
    assert analyze_gate_m1.combine_chance_bars(nan, _cb(179), 200, 179)["verdict"] == "UNDECIDED"


def test_a_point_estimate_at_or_below_half_in_an_undecided_cell_is_only_a_flag():
    r = analyze_gate_m1.combine_chance_bars(_cb(106), _cb(85, mean=0.45), 106, 85)
    assert r["verdict"] == "UNDECIDED" and set(r["audit_flag_point_estimate"]) == set(CELLS) and not r["failed"]
    assert analyze_gate_m1.combine_chance_bars(_cb(200), _cb(179), 200, 179)["audit_flag_point_estimate"] == []


# ------------------------------------------------------------------------------------------------ end to end on synthetic arrays
def _synth(tmp, n_items, signal, seed=0, with_q=True):
    """Probe-2 and M1 arrays shaped like exp_p2.run_probe2 / run_gate_m1 output; `signal(i)` is the strength of the code-change signal of item i (0 = chance)."""
    rng = np.random.default_rng(seed)
    p2, m1 = tmp / "P2-PROBE-02", tmp / "P2-GATE-M1"
    (p2 / "arrays").mkdir(parents=True)
    (m1 / "arrays").mkdir(parents=True)
    (p2 / "selection.json").write_text(json.dumps(dict(items=[dict(image_id=i, caption="x", n_tok=5) for i in range(n_items)])))
    for i in range(n_items):
        arrs, m1a, s = dict(clean=rng.integers(0, 16384, N_TOK)), {}, float(signal(i))
        for c in detect.P2_CORRS:
            z = np.zeros(N_TOK, bool)
            z[rng.choice(N_TOK, 150, replace=False)] = True
            B = -s * z + rng.normal(0, 1.5, N_TOK)
            D = s * 0.5 * z + rng.normal(0, 0.2, N_TOK)
            r = rng.normal(0, 0.01, N_TOK)
            arrs.update({f"{c}_s1": (B + r).astype(np.float32), f"{c}_r_original": r.astype(np.float32), f"{c}_s2": rng.normal(size=N_TOK).astype(np.float32),
                         f"{c}_s3": rng.random(N_TOK).astype(np.float32), f"{c}_codes": rng.integers(0, 16384, N_TOK), f"{c}_z": z})
            m1a[f"{c}_D"] = D.astype(np.float32)
        np.savez(p2 / "arrays" / f"item{i:04d}.npz", **arrs)
        if with_q:
            np.savez(m1 / "arrays" / f"item{i:04d}.npz", **m1a)
    return p2, m1


def test_end_to_end_all_items_pass_but_items_after_the_dry_run_do_not_gives_failed(tmp_path):
    """First 21 items carry a strong signal, the rest none: the pooled bar passes, the late pool fails, so the combined bar is FAILED (the point of AB.7 item 3). 130 items: both pools hold n >= 100."""
    n = 130
    p2, m1 = _synth(tmp_path, n, lambda i: 3.0 if i < analyze_gate_m1.DRY_RUN_N else 0.0)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=400)
    assert res["chance_bar"]["n_unavailable"] == 0 and res["chance_bar"]["per_score"]["patch/plainB"]["n"] == n and "descriptive" in res["chance_bar"]["note"]
    assert res["chance_bar"]["per_score"]["patch/plainB"]["lower95"] > 0.5            # the 21 informative items lift the pooled bound
    late = res["chance_bar_after_dry_run"]
    assert late["per_score"]["patch/plainB"]["n"] == n - analyze_gate_m1.DRY_RUN_N     # items 21 and later only
    assert late["per_score"]["patch/plainB"]["lower95"] <= 0.5
    both = res["chance_bar_both"]
    assert both["verdict"] == "FAILED" and both["failed"] and both["passes"] is False and both["n_all"] == n and both["n_late"] == n - 21
    assert both["per_score"]["patch/plainB"]["result"] == "fail"


def test_end_to_end_signal_everywhere_is_passed_in_both_pools(tmp_path):
    n = 125
    p2, m1 = _synth(tmp_path, n, lambda i: 3.0, seed=1)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=400)
    both = res["chance_bar_both"]
    assert both["verdict"] == "PASSED" and both["passes"] is True and not both["failed"] and both["n_late"] == n - 21 == 104 and both["complete"] is False
    assert all(v["result"] == "pass" for v in both["per_score"].values())
    assert res["chance_bar"]["passes"] is True            # the original single-pool key keeps its descriptive meaning
    pool = res["pool"]
    assert pool["n_items"] == n and pool["n_late"] == 104 and pool["last_idx"] == n - 1 and pool["complete"] is False
    import hashlib
    assert pool["item_idx_sha256"] == hashlib.sha256(json.dumps(list(range(n))).encode()).hexdigest()
    again = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=400)
    assert again["chance_bar_both"] == both and again["pool"] == pool                      # a re-run on the same pool reproduces the bar exactly (fixed seed)


def test_end_to_end_a_pool_below_the_floor_is_undecided_not_a_pass(tmp_path):
    """60 items with a strong signal everywhere: every bound is above 0.5 but n_late = 39 < 100."""
    p2, m1 = _synth(tmp_path, 60, lambda i: 3.0, seed=4)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=300)
    assert res["chance_bar"]["passes"] is True and res["chance_bar_both"]["verdict"] == "UNDECIDED" and res["chance_bar_both"]["passes"] is None


def test_end_to_end_only_dry_run_items_available(tmp_path):
    """With 21 items or fewer there is no late pool: the combined bar is undecided, never a pass."""
    p2, m1 = _synth(tmp_path, 21, lambda i: 3.0, seed=2)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=300)
    assert res["chance_bar_after_dry_run"] is None and res["chance_bar_both"]["verdict"] == "UNDECIDED" and res["chance_bar"]["passes"] is True


def test_a_pool_that_is_not_a_contiguous_prefix_raises(tmp_path):
    p2, m1 = _synth(tmp_path, 40, lambda i: 3.0, seed=3)
    for i in (0, 1, 2, 30):
        (p2 / "arrays" / f"item{i:04d}.npz").unlink()
        (m1 / "arrays" / f"item{i:04d}.npz").unlink()
    with pytest.raises(ValueError, match="contiguous prefix") as e:
        analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=200)
    assert "[3, 4, 5" in str(e.value) and "[0, 1, 2, 3" in str(e.value)                    # both lists are printed


def test_main_prints_the_three_state_verdict(tmp_path, monkeypatch, capsys):
    from exp_p2 import common
    p2, m1 = _synth(tmp_path, 50, lambda i: 3.0, seed=5)
    monkeypatch.setattr(common, "RUNS", tmp_path)
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "200"]) == 0
    out = capsys.readouterr().out
    assert "UNDECIDED" in out and "not a pass" in out and "completed prefix of k = 50 items" in out and "detection_frozen.json NOT written" in out and "--closed-k" in out
