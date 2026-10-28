"""E-dec (SAP AD.2, AB.2, AD.13): the identity T = U + R + V item by item and in every bootstrap resample, the shares rule, complete-case counting, the interval levels, absent cells,
the seed, and the CLI order check. CPU only, synthetic data with known answers."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2.gate import config, edec, epred, seeds                         # noqa: E402
from test_gate_m4_analysis import build                                    # noqa: E402


def arms(n, seed=0, means=(0.5, 0.2, 0.4, 0.35), sd=0.3):
    rng = np.random.default_rng(seed)
    return [rng.normal(m, sd, n) for m in means]


# ------------------------------------------------------------------------------------------------ identity (AD.13 self-test: T = U + R + V on random data)
def test_identity_holds_item_by_item_on_random_data():
    for seed in range(20):
        d = arms(80, seed)
        sp = edec.edec_split(*d)
        T, U, R, V = (sp["d"][k] for k in "TURV")
        assert np.max(np.abs(T - (U + R + V))) <= 1e-9
        assert sp["n"] == 80 and sp["n_dropped"] == 0
        assert np.allclose(T, d[0] - d[1]) and np.allclose(U, d[0] - d[2]) and np.allclose(R, d[3] - d[1]) and np.allclose(V, d[2] - d[3])


def test_identity_holds_in_every_resample_and_on_the_accuracy_scale():
    rng = np.random.default_rng(1)
    d = arms(90, 1)
    y = [(rng.random(90) < p).astype(float) for p in (0.9, 0.55, 0.8, 0.7)]
    res = edec.edec_cell("P1", d, y, n_boot=1000, seed=3)
    assert res["d_scale"]["identity_in_all_resamples"] is True and res["accuracy_scale"]["identity_in_all_resamples"] is True
    t = res["d_scale"]["tau"]
    assert t["T"]["mean"] == pytest.approx(t["U"]["mean"] + t["R"]["mean"] + t["V"]["mean"], abs=1e-12)
    a = res["accuracy_scale"]["tau"]
    assert a["T"]["mean"] == pytest.approx(y[0].mean() - y[1].mean(), abs=1e-12)                      # tau_T = A_clean - A_none on the accuracy scale
    assert a["R"]["mean"] == pytest.approx(y[3].mean() - y[1].mean(), abs=1e-12)
    assert a["U"]["mean"] == pytest.approx(y[0].mean() - y[2].mean(), abs=1e-12)
    assert a["V"]["mean"] == pytest.approx(y[2].mean() - y[3].mean(), abs=1e-12)


def test_the_assertion_trips_when_the_split_is_broken():
    sp = edec.split_parts(*arms(50, 2))
    edec.assert_identity(sp)
    sp["V"] = sp["V"] + 1e-6
    with pytest.raises(edec.IdentityError):
        edec.assert_identity(sp)
    sp2 = edec.split_parts(*arms(50, 2))
    sp2["R"] = sp2["R"] * 1.001
    with pytest.raises(AssertionError):
        edec.assert_identity(sp2)


def test_a_mislabelled_arm_order_is_not_silently_accepted():
    """If the caller swaps the chg and gm columns the identity still holds (it is algebra), but the numbers move: U and V swap meaning. The names in the output guard against reading them wrongly."""
    d = arms(60, 4)
    ok = edec.edec_split(*d)
    sw = edec.edec_split(d[0], d[1], d[3], d[2])
    assert np.allclose(ok["d"]["U"], d[0] - d[2]) and np.allclose(sw["d"]["U"], d[0] - d[3])
    assert edec.NAMES["U"] == "residual loss under the oracle gate" and edec.NAMES["V"] == "gap to the oracle gate"


# ------------------------------------------------------------------------------------------------ known-answer cases
def test_oracle_equals_gate_gives_V_zero_and_oracle_equals_clean_gives_U_zero():
    rng = np.random.default_rng(5)
    n = 100
    clean = rng.normal(0.5, 0.2, n)
    none = clean - rng.uniform(0.2, 0.5, n)                       # a clear corruption loss
    res = edec.edec_cell("P2", [clean, none, clean.copy(), clean.copy()], None, n_boot=500, seed=1)       # chg = gm = clean: gate recovers everything
    t = res["d_scale"]["tau"]
    assert t["U"]["mean"] == pytest.approx(0, abs=1e-12) and t["V"]["mean"] == pytest.approx(0, abs=1e-12)
    assert t["R"]["mean"] == pytest.approx(t["T"]["mean"], abs=1e-12)
    sh = res["d_scale"]["shares"]
    assert sh["R"] == pytest.approx(1.0) and sh["U"] == pytest.approx(0, abs=1e-9) and sh["V"] == pytest.approx(0, abs=1e-9)


def test_gate_beating_the_oracle_gives_negative_V():
    rng = np.random.default_rng(6)
    n = 100
    clean = rng.normal(0.5, 0.1, n)
    none = clean - 0.3
    chg = clean - 0.1
    gm = clean + 0.05                                             # GATE-M better than the oracle (variance trimming): V = chg - gm < 0
    res = edec.edec_cell("P1", [clean, none, chg, gm], None, n_boot=500, seed=1)
    v = res["d_scale"]["tau"]["V"]
    assert v["mean"] == pytest.approx(-0.15, abs=1e-12) and v["ci95"][1] < 0                      # the AB.2 case "V < 0 with a CI excluding 0 voids any detection reading"
    assert res["d_scale"]["tau"]["R"]["mean"] == pytest.approx(0.35, abs=1e-12)


# ------------------------------------------------------------------------------------------------ shares rule
def test_shares_reported_only_when_the_lower_bound_of_tau_T_exceeds_zero():
    rng = np.random.default_rng(7)
    n = 100
    clean = rng.normal(0.5, 0.2, n)
    big = edec.edec_cell("P1", [clean, clean - 0.4 + rng.normal(0, 0.05, n), clean - 0.1, clean - 0.05], None, n_boot=800, seed=2)
    assert isinstance(big["d_scale"]["shares"], dict)
    assert sum(big["d_scale"]["shares"].values()) == pytest.approx(1.0, abs=1e-12)                # shares sum to 1 by the identity
    assert big["d_scale"]["tau"]["T"]["ci95"][0] > 0
    zero = edec.edec_cell("P1", [clean, clean + rng.normal(0, 0.3, n), clean, clean], None, n_boot=800, seed=2)       # no corruption loss on average
    assert zero["d_scale"]["tau"]["T"]["ci95"][0] < 0 < zero["d_scale"]["tau"]["T"]["ci95"][1]
    assert isinstance(zero["d_scale"]["shares"], str) and zero["d_scale"]["shares"].startswith("undefined")
    nearly = edec.edec_cell("P1", [clean, clean - 1e-9, clean - 5e-10, clean - 7e-10], None, n_boot=300, seed=2)         # tau_T numerically zero although its bound is >0: not reported
    assert isinstance(nearly["d_scale"]["shares"], str)


# ------------------------------------------------------------------------------------------------ complete case, absent cells, levels
def test_complete_case_drops_and_counts_by_arm():
    d = arms(100, 8)
    d[2][:4] = np.nan
    d[3][2:7] = np.nan
    d[1][50] = np.inf
    r = edec.edec_cell("P3", d, None, n_boot=200, seed=1)
    bad = set(range(0, 7)) | {50}
    assert r["n_complete"] == 100 - len(bad) and r["n_dropped_incomplete"] == len(bad)
    assert r["n_nonfinite_by_arm"] == dict(clean=0, none=1, chg=4, gm=5)


def test_levels_9833_only_for_P_cells_and_wider_than_95():
    d = arms(100, 9)
    p = edec.edec_cell("P2", d, None, n_boot=2000, seed=1)["d_scale"]["tau"]["T"]
    ps = edec.edec_cell("PS1", d, None, n_boot=2000, seed=1)["d_scale"]["tau"]["T"]
    assert "ci9833" in p and "ci9833" not in ps
    assert p["ci9833"][0] < p["ci95"][0] and p["ci9833"][1] > p["ci95"][1]


def test_bootstrap_interval_covers_the_true_mean_about_95_percent():
    rng = np.random.default_rng(10)
    cover, reps = 0, 150
    for r in range(reps):
        n = 100
        clean = rng.normal(0.5, 0.3, n)
        none = clean - 0.2 + rng.normal(0, 0.2, n)                     # true tau_T = 0.2
        res = edec.edec_cell("PS1", [clean, none, clean - 0.05, clean - 0.1], None, n_boot=300, seed=r)
        lo, hi = res["d_scale"]["tau"]["T"]["ci95"]
        cover += lo <= 0.2 <= hi
    assert 0.86 <= cover / reps <= 1.0


def test_deterministic_for_a_seed_and_seed_fallback_is_the_appended_child():
    d = arms(60, 11)
    a = edec.edec_cell("P1", d, None, n_boot=300, seed=np.random.SeedSequence(4))
    b = edec.edec_cell("P1", d, None, n_boot=300, seed=np.random.SeedSequence(4))
    assert a == b
    # seeds.py is untouched by this module: while "edec" is not in seeds.ANALYSES the child is the one that APPENDING it would give (spawn position 28, after s2_descriptive)
    pos = seeds.ANALYSES.index("edec") if "edec" in seeds.ANALYSES else edec.EDEC_SEED_POSITION
    if "edec" not in seeds.ANALYSES:
        assert pos == len(seeds.ANALYSES) == 28
    ref = np.random.SeedSequence(seeds.ROOT_SEED).spawn(pos + 1)[pos]
    assert np.array_equal(edec.edec_seed().generate_state(4), ref.generate_state(4))
    assert np.array_equal(np.random.SeedSequence(seeds.ROOT_SEED).spawn(40)[28].generate_state(4), np.random.SeedSequence(seeds.ROOT_SEED, spawn_key=(28,)).generate_state(4))


def test_cell_constants_agree_with_epred_and_config():
    assert edec.CELLS == epred.CELLS and edec.P_CELLS == epred.P_CELLS and edec.PS_CELLS == epred.PS_CELLS and edec.PS_KEY == epred.PS_KEY
    assert tuple(edec.P_CORRUPTION.values()) == config.REALISTIC and edec.A0 == epred.A0 == "gate0.05"


# ------------------------------------------------------------------------------------------------ from M4 rows
FAM = [dict(corruption="jpeg", severity=10, key="jpeg10")]


def _rows(tmp_path, n=60, conds=("clean", "jpeg10", "patch")):
    rng = np.random.default_rng(12)
    y, dd = {}, {}
    dd[("clean", "none")] = rng.normal(0.5, 0.05, n)
    for c in conds[1:]:
        dd[(c, "none")] = dd[("clean", "none")] - 0.3
        dd[(c, "chg")] = dd[("clean", "none")] - 0.1
        dd[(c, "gate0.05")] = dd[("clean", "none")] - 0.15
        y[(c, "none")] = np.r_[np.ones(20), np.zeros(n - 20)].astype(int)
        y[(c, "gate0.05")] = np.r_[np.ones(35), np.zeros(n - 35)].astype(int)
        y[(c, "chg")] = np.r_[np.ones(40), np.zeros(n - 40)].astype(int)
    y[("clean", "none")] = np.r_[np.ones(50), np.zeros(n - 50)].astype(int)
    return build(tmp_path, n, y, d=dd, conds=conds)


def test_cells_from_rows_and_the_split_numbers(tmp_path):
    run, rows = _rows(tmp_path)
    recs, absent = edec.cells_from_m4_rows(rows, FAM)
    assert sorted({r["cell"] for r in recs}) == ["P1", "PS1"]
    assert set(absent) == {"P2", "P3", "PS2"} and "operating point" in absent["P2"] and "not run" in absent["PS2"]
    res = edec.edec(recs, n_boot=400, absent=absent)
    assert res["n_cells"] == 2 and res["n_absent"] == 3 and set(res["absent"]) == {"P2", "P3", "PS2"}
    t = res["cells"]["P1"]["d_scale"]["tau"]
    assert t["T"]["mean"] == pytest.approx(0.3, abs=1e-6) and t["U"]["mean"] == pytest.approx(0.1, abs=1e-6)
    assert t["R"]["mean"] == pytest.approx(0.15, abs=1e-6) and t["V"]["mean"] == pytest.approx(0.05, abs=1e-6)
    ta = res["cells"]["P1"]["accuracy_scale"]["tau"]
    assert ta["T"]["mean"] == pytest.approx(50 / 60 - 20 / 60) and ta["R"]["mean"] == pytest.approx(35 / 60 - 20 / 60) and ta["U"]["mean"] == pytest.approx(50 / 60 - 40 / 60)
    assert res["cells"]["P1"]["d_scale"]["shares"]["R"] == pytest.approx(0.5, abs=1e-6)
    assert "ci9833" in t["T"] and "ci9833" not in res["cells"]["PS1"]["d_scale"]["tau"]["T"]
    assert "no p-value" in res["label"] and "p" not in {k for k in res if k in ("p", "p_value")}


def test_edec_accepts_a_dataframe_and_rejects_unknown_cells():
    import pandas as pd
    d = arms(40, 13)
    df = pd.DataFrame(dict(cell="P1", idx=range(40), d_clean=d[0], d_none=d[1], d_chg=d[2], d_gm=d[3]))
    res = edec.edec(df, n_boot=200)
    assert res["cells"]["P1"]["n_complete"] == 40 and "accuracy_scale" not in res["cells"]["P1"]            # no y columns: only the d scale
    df["cell"] = "Q9"
    with pytest.raises(ValueError):
        edec.edec(df, n_boot=100)


def test_a_cell_with_a_duplicate_item_is_refused():
    d = arms(10, 14)
    recs = [dict(cell="P1", idx=min(i, 8), d_clean=d[0][i], d_none=d[1][i], d_chg=d[2][i], d_gm=d[3][i]) for i in range(10)]
    with pytest.raises(ValueError):
        edec.edec(recs, n_boot=100)


# ------------------------------------------------------------------------------------------------ self-test and CLI
def test_module_selftest_passes():
    st = edec.selftest()
    assert st["all_ok"], st


def test_cli_waits_for_family_p_and_ps_and_then_writes_edec_json(tmp_path):
    run, rows = _rows(tmp_path / "runs_unused")                                   # writes tmp/runs_unused/P2-GATE-M4
    runs = tmp_path / "runs"
    (runs / "P2-GATE-M3").mkdir(parents=True)
    (runs / "P2-GATE-M4").mkdir(parents=True)
    (runs / "P2-GATE-M4" / "items.jsonl").write_text((run / "items.jsonl").read_text())
    (runs / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="d", family=FAM)))
    assert edec.main(["run", "--runs-dir", str(runs), "--boot", "200"]) == 3                       # analysis.json (family P and PS) does not exist yet: AD.12 order
    (runs / "P2-GATE-M4" / "analysis.json").write_text(json.dumps(dict(meta=dict(allow_partial=False))))
    assert edec.main(["run", "--runs-dir", str(runs), "--boot", "200"]) == 0
    out = json.loads((runs / "P2-GATE-M4" / "edec.json").read_text())
    assert set(out["cells"]) == {"P1", "PS1"} and set(out["absent"]) == {"P2", "P3", "PS2"} and out["allow_partial_in_analysis_json"] is False and out["selftest"]["all_ok"]
