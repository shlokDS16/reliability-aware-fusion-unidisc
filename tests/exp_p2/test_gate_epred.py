"""E-pred loading, freeze and scoring (SAP AD.3 as demoted by AB.3, AD.13): the fit-fold disjointness check, write-once freeze with the fit-code hashes, the descriptive scoring (A of K_eval with
Clopper-Pearson, separate P and PS groups, rivals, o_c*, no p-value), the combined self-test and the CLI order and refusal rules. The fit code itself is tested in test_gate_epred_fit.py. CPU only."""
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

from exp_p2.gate import config, epred, epred_fit, seeds, stats           # noqa: E402
from test_gate_m4_analysis import build                                    # noqa: E402


# ------------------------------------------------------------------------------------------------ fit-fold check
def _folds():
    return dict(cal=[dict(image_id=i) for i in range(10)], head=[dict(image_id=100 + i) for i in range(5)], test=[dict(image_id=200 + i) for i in range(5)], test_ext=[dict(image_id=300 + i) for i in range(3)])


def test_fit_fold_must_be_disjoint_from_test_and_cal_and_equal_to_head():
    f = _folds()
    rows = [dict(image_id=100 + i) for i in range(5)]
    ok = epred.check_fit_fold_disjoint(f, rows)
    assert ok["disjoint_from_test"] and ok["n_head"] == 5 and len(ok["head_image_ids_sha256"]) == 64
    f2 = _folds()
    f2["test_ext"][0]["image_id"] = 102                                                        # an injected shared id (headroom in test_ext)
    with pytest.raises(AssertionError):
        epred.check_fit_fold_disjoint(f2, rows)
    f3 = _folds()
    f3["cal"][0]["image_id"] = 100
    with pytest.raises(AssertionError):
        epred.check_fit_fold_disjoint(f3, rows)
    with pytest.raises(AssertionError):
        epred.check_fit_fold_disjoint(_folds(), rows + [dict(image_id=999)])                    # an M3 row that is not a headroom item



# ------------------------------------------------------------------------------------------------ scoring (descriptive)
def frozen_signs(**s):
    return dict(cells={c: dict(sign=v, sign_text={1: "+", -1: "-", 0: "none (tie)", None: "none (undefined)"}[v], stability=dict(share_same_sign=0.9 if v in (1, -1) else None)) for c, v in s.items()})


def pc(b, c, n=300, ci=None):
    net = (b - c) / n
    return dict(b=b, c=c, n=n, net_difference=net, ci95=ci if ci is not None else [net - 0.05, net + 0.05])


def test_score_counts_agreements_separately_for_P_and_PS_and_has_no_p_value():
    fr = frozen_signs(P1=1, P2=-1, P3=1, PS1=1, PS2=1)
    obs = {"P1": pc(30, 10), "P2": pc(8, 20), "P3": pc(5, 25), "PS1": pc(80, 4), "PS2": pc(70, 3)}
    r = epred.epred_score(fr, obs)
    assert (r["P"]["A"], r["P"]["K_eval"]) == (2, 3) and (r["PS"]["A"], r["PS"]["K_eval"]) == (2, 2)                  # P3 disagrees: + predicted, - observed
    lo, hi = stats.clopper_pearson(2, 3, 0.95)
    assert r["P"]["cp95"] == pytest.approx([lo, hi]) and r["PS"]["cp95"] == pytest.approx(list(stats.clopper_pearson(2, 2, 0.95)))
    assert r["cells"]["P3"]["agree"] is False and r["cells"]["P1"]["agree"] is True and r["cells"]["P2"]["o"] == -1
    assert "2 of 3 cells" in r["P"]["sentence"] and "2 of 2 cells" in r["PS"]["sentence"]
    assert "predicted" not in r["P"]["sentence"] and "explain" not in r["P"]["sentence"]
    assert r["formal_test"] is None and "p-value" in r["formal_test_note"]
    flat = json.dumps(r)
    assert '"p"' not in flat and "p_value" not in flat and '"p_binom' not in flat                                   # no test, no p-value, anywhere in the output
    assert "foregone" in r["PS"]["label"] and "P1" not in r["PS"]["cells_evaluable"]
    assert r["P"]["reachability_of_withdrawn_test"]["could_reject_at_alpha"] is False and r["P"]["reachability_of_withdrawn_test"]["status"].startswith("family E withdrawn")


def test_five_of_five_agreement_is_still_descriptive_not_a_test():
    fr = frozen_signs(P1=1, P2=1, P3=1, PS1=1, PS2=1)
    obs = {c: pc(40, 5) for c in epred.CELLS}
    r = epred.epred_score(fr, obs)
    assert r["P"]["A"] == 3 and r["PS"]["A"] == 2 and r["formal_test"] is None
    assert r["P"]["K_eval"] + r["PS"]["K_eval"] == 5 and "p" not in r and "p_value" not in r


def test_score_excludes_ties_missing_signs_and_missing_tests_and_counts_them():
    fr = frozen_signs(P1=1, P2=0, P3=None, PS1=-1, PS2=1)
    fr["cells"].pop("PS2")                                               # PS2 never fitted
    obs = {"P1": pc(10, 10), "P2": pc(20, 5), "P3": pc(20, 5), "PS1": pc(30, 2)}                      # P1 has b = c_cnt; PS2 has no test
    r = epred.epred_score(fr, obs)
    assert r["P"]["K_eval"] == 0 and r["PS"]["K_eval"] == 1 and r["PS"]["A"] == 0                       # PS1: - predicted, + observed
    ex = r["P"]["excluded"]
    assert set(ex) == {"P1", "P2", "P3"}
    assert "b = c_cnt" in ex["P1"] and "no committed sign" in ex["P2"] and "no committed sign" in ex["P3"]
    assert "no test" in r["PS"]["excluded"]["PS2"]
    assert r["P"]["sentence"] == "no cell is evaluable"
    assert r["cells"]["P1"]["o"] is None and r["cells"]["P1"]["evaluable"] is False


def test_observed_sign_is_on_Y_and_o_star_needs_an_interval_that_excludes_zero():
    fr = frozen_signs(P1=1, P2=-1, P3=1)
    obs = {"P1": pc(30, 10, ci=[0.02, 0.11]), "P2": pc(6, 20, ci=[-0.09, 0.01]), "P3": pc(4, 25, ci=[-0.12, -0.04])}
    r = epred.epred_score(fr, obs)
    assert r["cells"]["P1"]["o"] == 1 and r["cells"]["P1"]["o_star"] == 1
    assert r["cells"]["P2"]["o"] == -1 and r["cells"]["P2"]["o_star"] is None                      # interval includes 0: o_c* = none
    assert r["cells"]["P3"]["o"] == -1 and r["cells"]["P3"]["o_star"] == -1
    assert r["P"]["agreement_where_observed_interval_excludes_0"] == dict(A=1, K=2, cells=["P1", "P3"], note="descriptive column o_c*")
    assert r["refutation_rule_met_for_cells"] == ["P3"]                                           # s = +, o* = -: the spec 5.3 refutation rule, for that cell only


def test_rival_rules_are_scored_on_the_same_evaluable_cells():
    fr = frozen_signs(P1=1, P2=1, P3=-1, PS1=1, PS2=-1)
    obs = {"P1": pc(5, 20), "P2": pc(4, 20), "P3": pc(3, 30), "PS1": pc(60, 2), "PS2": pc(50, 1)}      # P all negative, PS all positive
    r = epred.epred_score(fr, obs)
    assert r["P"]["rivals"]["always +"] == dict(A=0, K_eval=3)
    assert r["P"]["rivals"]["- for P cells, + for PS cells"] == dict(A=3, K_eval=3)
    assert r["PS"]["rivals"]["always +"] == dict(A=2, K_eval=2) and r["PS"]["rivals"]["- for P cells, + for PS cells"] == dict(A=2, K_eval=2)
    assert r["P"]["A"] == 1 and r["PS"]["A"] == 1                                                    # the plug-in itself: P3 and PS1 agree


def test_unknown_cell_in_p_cells_is_refused():
    with pytest.raises(ValueError):
        epred.epred_score(frozen_signs(P1=1), {"SUITE1": pc(3, 1)})


# ------------------------------------------------------------------------------------------------ files: write-once, hashes
def test_write_once_refuses_to_overwrite(tmp_path):
    p = tmp_path / "epred_frozen.json"
    epred.write_once_exclusive(p, "{}")
    with pytest.raises(FileExistsError):
        epred.write_once_exclusive(p, "{\"changed\": 1}")
    assert p.read_text() == "{}" and not list(tmp_path.glob("*.tmp*"))


def test_fit_code_hashes_cover_the_files_and_have_both_line_ending_forms(tmp_path):
    h = epred.fit_code_hashes()
    assert set(h) == set(epred.FIT_CODE_FILES) and "tests/exp_p2/test_gate_epred_fit.py" in h and "exp_p2/gate/theory.py" in h and "exp_p2/gate/epred_fit.py" in h
    assert "exp_p2/gate/seeds.py" not in h and "exp_p2/gate/epred.py" not in h                       # seeds enter as a fingerprint; the score/CLI module may be fixed after the freeze
    for v in h.values():
        assert len(v["sha256"]) == 64 and len(v["sha256_lf"]) == 64 and len(v["git_blob_sha1"]) == 40
    f = tmp_path / "a.txt"
    f.write_bytes(b"x\r\ny\r\n")
    s = epred.sha256_file(f)
    g = tmp_path / "b.txt"
    g.write_bytes(b"x\ny\n")
    assert s["sha256_lf"] == epred.sha256_file(g)["sha256"] and s["sha256"] != s["sha256_lf"]
    assert s["git_blob_sha1"] == epred.sha256_file(g)["git_blob_sha1"]


# ------------------------------------------------------------------------------------------------ CLI on a temporary runs directory
M = 64


def make_runs(tmp, n=12, overlap=False, seed=0):
    rng = np.random.default_rng(seed)
    runs = Path(tmp) / "runs"
    m3, fit = runs / "P2-GATE-M3", runs / "P2-GATE-EPRED-FIT"
    for d in (m3 / "arrays", fit / "arrays", runs / "P2-GATE-FOLDS", runs / "P2-GATE-M4"):
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    helps = {"jpeg10": True, "splice128": False, "patch": True}
    for i in range(n):
        clean = rng.integers(0, 1000, M)
        a3, af = {"clean": clean.astype(np.int16)}, {}
        for key, h in helps.items():
            z = rng.random(M) < 0.2
            d = np.where(z, rng.normal(0, 3, M), rng.normal(0.3, 0.5, M))
            f = (z & (rng.random(M) < (0.7 if h else 0))) | (~z & (rng.random(M) < (0.03 if h else 0.3)))
            codes = np.where(z, (clean + 1) % 1000, clean).astype(np.int16)
            if key == "patch":
                af.update({f"{key}_codes": codes, f"{key}_delta": d.astype(np.float32)})
            else:
                a3.update({f"{key}_codes": codes, f"{key}_delta": d.astype(np.float32)})
            af[f"{key}_flag"] = f
        np.savez(m3 / "arrays" / f"item{i:04d}.npz", **a3)
        np.savez(fit / "arrays" / f"item{i:04d}.npz", **af)
        rows.append(dict(idx=i, gid=1000 + i, image_id=100 + i))
    (m3 / "items.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    (fit / "items.jsonl").write_text("\n".join(json.dumps(dict(idx=r["idx"])) for r in rows) + "\n")
    fam = dict(endpoint="d", family=[dict(corruption="jpeg", severity=10, key="jpeg10"), dict(corruption="splice", severity=128, key="splice128")])
    (m3 / "family.json").write_text(json.dumps(fam))
    folds = dict(cal=[dict(image_id=i) for i in range(10)], head=[dict(image_id=100 + i) for i in range(n)], test=[dict(image_id=(105 if overlap else 500) + i) for i in range(5)], test_ext=[])
    (runs / "P2-GATE-FOLDS" / "folds.json").write_text(json.dumps(folds))
    return runs, fam


def test_cli_fit_writes_a_write_once_frozen_file_with_hashes(tmp_path):
    runs, fam = make_runs(tmp_path)
    args = ["fit", "--runs-dir", str(runs), "--skip-git-checks", "--min-items", "12", "--boot", "400"]
    assert epred.main(args) == 0
    out = runs / "P2-GATE-EPRED-FIT" / "epred_frozen.json"
    fr = json.loads(out.read_text())
    assert fr["kind"] == "epred_frozen" and fr["s_c"] == {"P1": 1, "P3": -1, "PS1": 1}
    assert set(fr["absent_cells"]) == {"P2", "PS2"} and "operating point" in fr["absent_cells"]["P2"] and "no swap_flag" in fr["absent_cells"]["PS2"]
    assert set(fr["fit_code"]["files"]) == set(epred.FIT_CODE_FILES) and all(len(v["sha256"]) == 64 for v in fr["fit_code"]["files"].values())
    assert fr["fit_code"]["files"]["exp_p2/gate/epred_fit.py"]["sha256_lf"] == epred.sha256_file(ROOT / "exp_p2/gate/epred_fit.py")["sha256_lf"]
    assert fr["fit_code"]["seed_fingerprint"]["name"] == "prop4_plugin" and fr["fit_code"]["seed_fingerprint"] == epred._jsonable(epred.seed_fingerprint())
    for k in ("family.json", "m3_items.jsonl", "folds.json", "arrays", "fit_items.jsonl"):
        assert k in fr["inputs"]
    assert fr["fit_fold_check"]["disjoint_from_test"] is True and fr["selftest"]["all_ok"] and fr["n_boot"] == 400 and fr["audit_record"] is None
    assert fr["cells"]["P1"]["stability"]["share_same_sign"] > 0.9
    assert epred.verify_frozen(fr) == []
    before = out.read_text()
    assert epred.main(args) == 2                                           # write-once: a second fit refuses
    assert out.read_text() == before


def test_cli_fit_refuses_after_the_first_m4_item_overlap_dirty_code_and_partial_chunk(tmp_path, monkeypatch):
    runs, _ = make_runs(tmp_path)
    (runs / "P2-GATE-M4" / "items.jsonl").write_text(json.dumps(dict(idx=0)) + "\n")
    base = ["fit", "--runs-dir", str(runs), "--skip-git-checks", "--min-items", "12", "--boot", "100"]
    assert epred.main(base) == 3 and not (runs / "P2-GATE-EPRED-FIT" / "epred_frozen.json").exists()
    runs2, _ = make_runs(tmp_path / "b", overlap=True)
    with pytest.raises(AssertionError):                                      # headroom ids shared with the test fold
        epred.main(["fit", "--runs-dir", str(runs2), "--skip-git-checks", "--min-items", "12"])
    runs3, _ = make_runs(tmp_path / "c")
    monkeypatch.setattr(epred, "git_status_lines", lambda paths, repo=ROOT: [" M exp_p2/gate/epred.py"])
    assert epred.main(["fit", "--runs-dir", str(runs3), "--min-items", "12", "--boot", "100"]) == 11                      # uncommitted fit code
    assert not (runs3 / "P2-GATE-EPRED-FIT" / "epred_frozen.json").exists()
    assert epred.main(["fit", "--runs-dir", str(runs3), "--min-items", "12", "--boot", "100", "--allow-dirty"]) == 0
    fr = json.loads((runs3 / "P2-GATE-EPRED-FIT" / "epred_frozen.json").read_text())
    assert fr["allow_dirty"] is True and fr["dirty_files_at_freeze"] == [" M exp_p2/gate/epred.py"]                     # recorded, not hidden
    runs4, _ = make_runs(tmp_path / "d")
    items = (runs4 / "P2-GATE-EPRED-FIT" / "items.jsonl").read_text().splitlines()
    (runs4 / "P2-GATE-EPRED-FIT" / "items.jsonl").write_text("\n".join(items[:7]) + "\n")
    with pytest.raises(ValueError, match="partial fit is refused"):
        epred.main(["fit", "--runs-dir", str(runs4), "--skip-git-checks", "--min-items", "12"])


def test_cli_score_reads_m4_rows_and_waits_for_analysis_json(tmp_path):
    runs, fam = make_runs(tmp_path)
    assert epred.main(["fit", "--runs-dir", str(runs), "--skip-git-checks", "--min-items", "12", "--boot", "200"]) == 0
    m4 = runs / "P2-GATE-M4"
    (m4 / "items.jsonl").unlink(missing_ok=True)
    n = 60
    y = {}
    y[("jpeg10", "gate0.05")] = np.r_[np.ones(35), np.zeros(25)].astype(int)           # P1: b = 35 (gate right, none wrong) > c = 0 -> o = +, s = + : agree
    y[("jpeg10", "none")] = np.r_[np.ones(10), np.zeros(50)].astype(int)
    y[("splice128", "gate0.05")] = np.r_[np.ones(5), np.zeros(55)].astype(int)           # P3: gate worse -> o = -, s = - : agree
    y[("splice128", "none")] = np.r_[np.ones(25), np.zeros(35)].astype(int)
    y[("patch", "gate0.05")] = np.r_[np.ones(50), np.zeros(10)].astype(int)              # PS1 + , s = + : agree
    y[("patch", "none")] = np.r_[np.ones(10), np.zeros(50)].astype(int)
    run, rows = build(tmp_path / "scratch", n, y, conds=("clean", "jpeg10", "splice128", "patch"))
    (m4 / "items.jsonl").write_text((run / "items.jsonl").read_text())
    frozen_path = runs / "P2-GATE-EPRED-FIT" / "epred_frozen.json"
    args = ["score", "--frozen", str(frozen_path), "--runs-dir", str(runs), "--skip-git-checks", "--boot", "300"]
    assert epred.main(args) == 3                                                       # AD.12: after family P and PS (analysis.json)
    (m4 / "analysis.json").write_text(json.dumps(dict(meta=dict(allow_partial=False))))
    assert epred.main(args) == 0
    out = json.loads((m4 / "epred_score.json").read_text())
    assert (out["P"]["A"], out["P"]["K_eval"]) == (2, 2) and (out["PS"]["A"], out["PS"]["K_eval"]) == (1, 1)
    assert set(out["P"]["excluded"]) == {"P2"} and set(out["PS"]["excluded"]) == {"PS2"} and out["fit_code_matches_frozen"] is True and out["formal_test"] is None
    assert out["cells"]["P1"]["o_star"] == 1 and out["cells"]["P3"]["o_star"] == -1 and out["refutation_rule_met_for_cells"] == []
    assert len(out["frozen_sha256"]) == 64
    # the interval is the one the P test prints: same arrays, the seed of family P
    from exp_p2.gate import report
    rep = report.report_test(y[("jpeg10", "gate0.05")], y[("jpeg10", "none")], n_boot=300, seed=seeds.seed_for("primary"))
    assert out["cells"]["P1"]["ci95"] == pytest.approx(rep["ci95"])
    # a changed fit code is refused
    fr = json.loads(frozen_path.read_text())
    fr["fit_code"]["files"]["exp_p2/gate/theory.py"]["sha256_lf"] = "0" * 64
    bad = tmp_path / "bad_frozen.json"
    bad.write_text(json.dumps(fr))
    assert epred.verify_frozen(fr) and epred.main(["score", "--frozen", str(bad), "--runs-dir", str(runs), "--skip-git-checks"]) == 2


def test_combined_selftest_passes_and_includes_the_fit_selftest():
    st = epred.selftest()
    assert st["all_ok"] and st["o_star_rule"] and st["reachability_K5_can_reject_K4_cannot"] and st["planted_helpful_gate_gets_plus"], st
    assert epred_fit.selftest()["all_ok"]
    assert epred.main(["selftest"]) == 0


def test_verify_frozen_flags_a_changed_seed_fingerprint_and_ignores_appended_analysis_names(monkeypatch):
    fr = dict(fit_code=dict(files=epred.fit_code_hashes(), seed_fingerprint=epred._jsonable(epred.seed_fingerprint())))
    assert epred.verify_frozen(json_roundtrip(fr)) == []
    monkeypatch.setattr(seeds, "ANALYSES", seeds.ANALYSES + ("some_future_family",))              # appending after the freeze: the fit is unaffected
    assert epred.verify_frozen(json_roundtrip(fr)) == []
    monkeypatch.setattr(seeds, "ANALYSES", tuple(reversed(seeds.ANALYSES[:20])) + seeds.ANALYSES[20:])   # reordering the names the fit uses: refused
    assert epred.verify_frozen(json_roundtrip(fr))


def json_roundtrip(x):
    return json.loads(json.dumps(x))
