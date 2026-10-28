"""The 179-item variant of the patch/swap chance bar (SAP AB.7 item 3): the bar is computed on all M1 items AND on the items after the 21 dry-run items, and passes only if the lower
95 percent bound exceeds 0.5 in both. SYNTHETIC DATA ONLY: nothing under runs/P2-PROBE-02 or runs/P2-GATE-M1 is read by these tests (blinding attestation). CPU only."""
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


def _cb(passes, failed=False, scores=("patch/plainB", "patch/q", "swap/plainB", "swap/q"), lower=0.9):
    """A detect.chance_bar-shaped result."""
    return dict(per_score={k: dict(available=passes is not None or failed, n=40, lower95=lower, passes=(None if passes is None and not failed else bool(passes))) for k in scores},
                passes=(False if failed else passes), failed=failed, audit_trigger=failed)


def test_combine_passes_only_when_both_pools_pass():
    r = analyze_gate_m1.combine_chance_bars(_cb(True), _cb(True), 200, 179)
    assert r["passes"] is True and not r["failed"] and r["n_all"] == 200 and r["n_late"] == 179
    assert all(v["passes_both"] is True for v in r["per_score"].values())


def test_combine_fails_when_the_179_pool_fails_even_if_all_items_pass():
    late = _cb(True)
    late["per_score"]["swap/plainB"] = dict(available=True, n=179, lower95=0.49, passes=False)
    late["passes"], late["failed"] = False, True
    r = analyze_gate_m1.combine_chance_bars(_cb(True), late, 200, 179)
    assert r["passes"] is False and r["failed"] and r["audit_trigger"]
    assert r["per_score"]["swap/plainB"]["passes_both"] is False and r["per_score"]["patch/q"]["passes_both"] is True


def test_combine_fails_when_all_items_fail_but_the_late_pool_passes():
    r = analyze_gate_m1.combine_chance_bars(_cb(False, failed=True), _cb(True), 200, 179)
    assert r["passes"] is False and r["failed"]


def test_combine_is_undecided_when_q_is_missing_in_either_pool_and_nothing_failed():
    r = analyze_gate_m1.combine_chance_bars(_cb(None), _cb(True), 200, 179)
    assert r["passes"] is None and not r["failed"]
    r = analyze_gate_m1.combine_chance_bars(_cb(True), _cb(None), 200, 179)
    assert r["passes"] is None and not r["failed"]


def test_combine_without_a_late_pool_cannot_pass():
    r = analyze_gate_m1.combine_chance_bars(_cb(True), None, 21, 0)
    assert r["passes"] is None and not r["failed"] and "no items" in r["incomplete"]
    r = analyze_gate_m1.combine_chance_bars(_cb(False, failed=True), None, 21, 0)
    assert r["passes"] is False and r["failed"]


def _synth(tmp, n_items, signal, seed=0):
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
        np.savez(m1 / "arrays" / f"item{i:04d}.npz", **m1a)
    return p2, m1


def test_end_to_end_all_items_pass_but_items_after_the_dry_run_do_not(tmp_path):
    """First 21 items carry a strong signal, the rest none: the pooled bar passes, the 179-style pool fails, so the combined bar FAILS (the point of AB.7 item 3)."""
    n = 60
    p2, m1 = _synth(tmp_path, n, lambda i: 3.0 if i < analyze_gate_m1.DRY_RUN_N else 0.0)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=400)
    assert res["chance_bar"]["n_unavailable"] == 0 and res["chance_bar"]["per_score"]["patch/plainB"]["n"] == n
    assert res["chance_bar"]["per_score"]["patch/plainB"]["lower95"] > 0.5            # the 21 informative items lift the pooled bound
    late = res["chance_bar_after_dry_run"]
    assert late["per_score"]["patch/plainB"]["n"] == n - analyze_gate_m1.DRY_RUN_N     # items 21 and later only
    assert late["per_score"]["patch/plainB"]["lower95"] <= 0.5 and late["failed"]
    both = res["chance_bar_both"]
    assert both["failed"] and both["passes"] is False and both["n_all"] == n and both["n_late"] == n - 21
    assert both["per_score"]["patch/plainB"]["passes_both"] is False


def test_end_to_end_signal_everywhere_passes_in_both_pools(tmp_path):
    n = 45
    p2, m1 = _synth(tmp_path, n, lambda i: 3.0, seed=1)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=400)
    both = res["chance_bar_both"]
    assert both["passes"] is True and not both["failed"] and both["n_late"] == n - 21
    assert all(v["passes_both"] is True for v in both["per_score"].values())
    assert res["chance_bar"]["passes"] is True            # the original single-pool key keeps its meaning


def test_end_to_end_only_dry_run_items_available(tmp_path):
    """With 21 items or fewer there is no late pool: the combined bar is undecided, never a pass."""
    p2, m1 = _synth(tmp_path, 21, lambda i: 3.0, seed=2)
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=300)
    assert res["chance_bar_after_dry_run"] is None and res["chance_bar_both"]["passes"] is None and res["chance_bar"]["passes"] is True


def test_the_late_pool_is_defined_by_item_index_not_by_position(tmp_path):
    """Probe-2 files named item0000..: if some low indices are missing the late pool still starts at index 21."""
    p2, m1 = _synth(tmp_path, 40, lambda i: 3.0, seed=3)
    for i in (0, 1, 2, 30):
        (p2 / "arrays" / f"item{i:04d}.npz").unlink()
        (m1 / "arrays" / f"item{i:04d}.npz").unlink()
    res = analyze_gate_m1.run_analysis(p2, m1, pixels=False, n_boot=200)
    assert res["n_items"] == 36
    assert res["chance_bar_both"]["n_late"] == len([i for i in range(40) if i >= 21 and i != 30])
