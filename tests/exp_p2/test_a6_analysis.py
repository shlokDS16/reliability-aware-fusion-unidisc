"""A6 analysis module (analysis/paper2/lrf/a6_analysis.py) on synthetic predictions: exact one-sided McNemar, the fixed sequence, Holm, the non-inferiority bound, the length control, LG, the partial-prefix label,
determinism, and the A6 power appendix as a cross-check of the exact test. CPU only."""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT,):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

_spec = importlib.util.spec_from_file_location("a6_analysis", ROOT / "analysis" / "paper2" / "lrf" / "a6_analysis.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
_bspec = importlib.util.spec_from_file_location("a6_baselines", ROOT / "analysis" / "paper2" / "lrf" / "baselines.py")
BL = importlib.util.module_from_spec(_bspec)
_bspec.loader.exec_module(BL)


def _lines(n=520, gain=0.12, seed=0, conds=("clean", "jpeg10", "noise0.1", "splice128"), harm_clean=0.0, length_exact=True):
    """Synthetic predictions: NONE accuracy 0.7; on noise0.1 LRF repairs a share `gain` of NONE's errors; clean loses `harm_clean` of its correct items."""
    r = np.random.default_rng(seed)
    out = []
    for i in range(n):
        ntok, nneg = 10, 10 + int(r.integers(-2, 3))
        for c in conds:
            yn = int(r.random() < 0.7)
            yl = yn
            if c == "noise0.1" and yn == 0 and r.random() < gain / 0.3:
                yl = 1
            if c == "clean" and yn == 1 and r.random() < harm_clean:
                yl = 0
            ylL = yl
            out.append(dict(idx=i, gid=8000 + i, image_id=i, condition=c, n_tok=ntok, n_tok_neg=nneg, y_none=yn, y_gatem=yn, y_lrf=yl, y_none_L=yn, y_gatem_L=yn, y_lrf_L=ylL,
                            n_tok_neg_len=ntok if (length_exact or i % 5) else ntok + 1, neg_len_diff=0 if (length_exact or i % 5) else 1, neg_len_exact=bool(length_exact or i % 5)))
    return out


def _write(tmp_path, lines, name="p.jsonl"):
    p = tmp_path / name
    p.write_text("".join(json.dumps(l) + "\n" for l in lines))
    return p


# ------------------------------------------------------------------------------------------------ the exact test
def test_exact_mcnemar_values():
    assert A.mcnemar_p(0, 0)["p_one"] == 1.0
    p = A.mcnemar_p(7, 3)
    assert p["p_one"] == pytest.approx(sum(math.comb(10, i) for i in range(7, 11)) / 1024, abs=1e-15)
    assert p["p_two"] == pytest.approx(2 * p["p_one"]) and p["p_mid_one"] < p["p_one"]
    assert A.mcnemar_p(3, 7)["p_one"] > 0.9 and A.mcnemar_p(3, 7)["p_two"] == pytest.approx(p["p_two"])
    # the Appendix A6 critical value: at n_d = 119 the one-sided 0.05 rejects from b = 71
    nd = 119
    crit = min(b for b in range(nd + 1) if A.mcnemar_p(b, nd - b)["p_one"] <= 0.05)
    assert crit == math.ceil(nd / 2 + 1.645 * math.sqrt(nd) / 2) or abs(crit - (nd / 2 + 1.645 * math.sqrt(nd) / 2)) < 2
    try:
        from scipy.stats import binom
        assert A.mcnemar_p(71, 48)["p_one"] == pytest.approx(float(binom.sf(70, 119, 0.5)), abs=1e-12)
    except ImportError:
        pass


def test_selftest_passes():
    st = A.selftest(n_sim=600)
    assert st["ok"], st


def test_holm_matches_the_reference():
    assert A.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert A.holm([0.5]) == [0.5]


# ------------------------------------------------------------------------------------------------ family L
def test_l1_confirmed_and_the_fixed_sequence_reaches_l2_l3_l4(tmp_path):
    res = A.analyse_l(_lines(gain=0.15))
    l1 = res["L1"]
    assert l1["rejected"] and l1["label"] == "confirmed" and l1["sided"] == "one" and l1["b"] > l1["c"] and l1["n"] == 520 and l1["passes_two_sided_005"]
    assert l1["ci95"][0] < l1["net"] < l1["ci95"][1] and l1["ci90"][0] > l1["ci95"][0] and l1["cp95_b_over_nd"][0] < l1["b"] / l1["n_d"] <= l1["cp95_b_over_nd"][1]
    assert "L2" not in res                                                       # r1: L2 (LRF vs GATE-M) is removed
    assert res["L3"]["status"] == "tested" and res["L4"]["status"] == "tested" and res["partial_label"] is None


def test_fixed_sequence_stops_when_l1_is_not_confirmed(tmp_path):
    res = A.analyse_l(_lines(gain=0.0, seed=3))
    assert res["L1"]["label"] == "not confirmed" and not res["L1"]["rejected"]
    for k in ("L3", "L4"):
        assert res[k]["status"] == "not tested (gatekept)" and res[k]["descriptive"] is not None
    assert res["L-NI"]["margin"] == 0.03 and res["L-LEN"]["label"] in ("rejected", "not rejected")      # always computed


def test_l3_l4_are_two_sided_holm_and_can_declare_a_harm():
    ls = _lines(gain=0.2, seed=4)
    for l in ls:
        if l["condition"] == "splice128" and l["y_none"] == 1 and l["idx"] % 3 == 0:        # LRF breaks a third of the correct items on splice128
            l["y_lrf"] = 0
    res = A.analyse_l(ls)
    assert res["L1"]["rejected"] and res["L4"]["status"] == "tested" and res["L4"]["sided"] == "two"
    assert res["L4"]["harm"] and not res["L4"]["rejected"] and res["L4"]["p_holm"] >= res["L4"]["p_two"] - 1e-15
    assert res["L3"]["p_holm"] >= res["L3"]["p_two"] - 1e-15 and not res["L3"]["harm"]


def test_branch_is_chosen_mechanically_from_l1():
    a = A.analyse_l(_lines(gain=0.2, seed=11))
    assert a["L1"]["p_one"] <= 0.025 and a["branch"]["branch"] == "A" and a["L1"]["headline_p_le_0025"]
    mid = A.branch_of(dict(rejected=True, p_one=0.04, label="confirmed"))
    assert mid["branch"] == "B"
    assert A.branch_of(dict(rejected=True, p_one=0.01, label="confirmed, partial prefix (300 of 520)"))["branch"] == "B"      # partial: never a headline claim
    assert A.analyse_l(_lines(gain=0.0, seed=3))["branch"]["branch"] == "C"
    assert A.branch_of(dict(rejected=False, p_one=0.5, label="inconclusive, partial prefix (300 of 520)"))["branch"] == "C"
    assert A.branch_of(dict(status="not run"))["branch"] == "D"


def test_gate_m_on_the_fresh_fold_is_a_descriptive_supplement_only():
    res = A.analyse_l(_lines(gain=0.15))
    sup = res["supplement_gatem_vs_none"]
    assert set(sup) == {"clean", "jpeg10", "noise0.1", "splice128"} and all(v["descriptive_only"] and "p" not in v and "p_one" not in v for v in sup.values())
    assert "L2" not in res and not any("gatem" in k and k != "supplement_gatem_vs_none" for k in res)           # no LRF-versus-GATE-M number anywhere


def test_the_partial_threshold_follows_n_l():
    assert A.label_partial(420, 520) is None and A.label_partial(415, 520) == "partial prefix (415 of 520)"
    assert A.label_partial(420, 533) == "partial prefix (420 of 533)" and A.label_partial(427, 533) is None          # 0.8 * 533 = 426.4
    res = A.analyse_l(_lines(n=420, gain=0.0, seed=6), n_l=533)
    assert res["partial_label"] == "partial prefix (420 of 533)" and res["L1"]["label"].startswith("inconclusive")


def test_partial_prefix_labels():
    full = A.analyse_l(_lines(n=400, gain=0.0, seed=5))
    assert full["partial_label"] == "partial prefix (400 of 520)" and full["L1"]["label"] == "inconclusive, partial prefix (400 of 520)"
    conf = A.analyse_l(_lines(n=400, gain=0.2))
    assert conf["L1"]["label"] == "confirmed, partial prefix (400 of 520)"
    ok = A.analyse_l(_lines(n=420, gain=0.0, seed=6))
    assert ok["partial_label"] is None and ok["L1"]["label"] == "not confirmed"


def test_non_inferiority_is_a_bound_on_the_90_percent_interval():
    ok = A.analyse_l(_lines(n=520, gain=0.1, harm_clean=0.01, seed=7))["L-NI"]
    bad = A.analyse_l(_lines(n=520, gain=0.1, harm_clean=0.2, seed=7))["L-NI"]
    assert ok["non_inferior"] and ok["label"] == "shown" and ok["lower90"] > -0.03
    assert not bad["non_inferior"] and bad["label"] == "not shown" and bad["lower90"] < -0.03 and bad["net"] < -0.05
    assert ok["ci90"][0] >= ok["ci95"][0] and ok["ci90"][1] <= ok["ci95"][1]


def test_length_control_excludes_items_whose_matched_negative_differs():
    res = A.analyse_l(_lines(n=400, gain=0.15, length_exact=False))
    ll = res["L-LEN"]
    assert ll["n_excluded_length_mismatch"] == 80 and ll["n"] == 320 and ll["n_with_length_matched_negative"] == 400
    none = A.analyse_l([{k: v for k, v in l.items() if not k.endswith("_L") and not k.startswith("neg_len") and k != "n_tok_neg_len"} for l in _lines(n=50)])
    assert none["L-LEN"]["status"] == "not run" and "not tested on fresh data" in none["L-LEN"]["label"]


def test_length_strata_secondary_is_descriptive():
    st = A.analyse_l(_lines(n=400, gain=0.15))["length_strata"]
    assert set(st) >= {"true_shorter", "equal", "true_longer", "longer_minus_shorter", "descriptive_only"}
    assert st["true_shorter"]["n"] + st["equal"]["n"] + st["true_longer"]["n"] == 400 and len(st["longer_minus_shorter"]["ci95"]) == 2


# ------------------------------------------------------------------------------------------------ LG
def _lg_lines(n=300, gain=0.12, cells=A.LG_CELLS, seed=1):
    r = np.random.default_rng(seed)
    out = []
    for i in range(n):
        for c in ("clean",) + tuple(cells):
            yn = int(r.random() < (0.8 if c == "clean" else 0.65))
            yl = 1 if (c != "clean" and yn == 0 and r.random() < gain / 0.35) else yn
            ygm = yn if r.random() < 0.9 else 1 - yn
            out.append(dict(idx=i, gid=i, image_id=i, condition=c, n_tok=10, n_tok_neg=11, y_none=yn, y_gatem=ygm, y_lrf=yl))
    return out


def test_lg_holm_over_three_and_generalisation_flag():
    res = A.analyse_lg(_lg_lines(gain=0.15))
    assert res["m_preregistered"] == 3 and res["n_cells_present"] == 3 and res["all_three_rejected_with_b_gt_c"]
    for c in A.LG_CELLS:
        t = res["cells"][c]
        assert t["p_holm"] >= t["p_one"] - 1e-15 and t["rejected"] and t["n"] == 300 and t["clean_to_corrupted_drop_of_none"]["drop_none"] > 0 and "b" in t["descriptive_gatem_vs_none"]
    nul = A.analyse_lg(_lg_lines(gain=0.0, seed=2))
    assert not nul["all_three_rejected_with_b_gt_c"]


def test_lg_absent_cell_enters_holm_as_p_one_and_short_prefix_is_descriptive():
    res = A.analyse_lg(_lg_lines(gain=0.15, cells=A.LG_CELLS[:2]))
    assert res["cells"]["speckle_noise3"]["status"].startswith("absent") and res["n_cells_present"] == 2 and not res["all_three_rejected_with_b_gt_c"]
    a = A.analyse_lg(_lg_lines(gain=0.15))
    s = A.analyse_lg(_lg_lines(n=200, gain=0.15))
    assert all(s["cells"][c]["descriptive_only"] and not s["cells"][c]["rejected"] for c in A.LG_CELLS) and not any(a["cells"][c]["descriptive_only"] for c in A.LG_CELLS)
    only_300 = A.analyse_lg(_lg_lines(n=350, gain=0.15))
    assert all(only_300["cells"][c]["n"] == 300 for c in A.LG_CELLS)                 # the first 300 items (prefix)


# ------------------------------------------------------------------------------------------------ run, determinism, CLI
def test_run_is_byte_identical_on_rerun_and_reads_only_the_predictions(tmp_path):
    p1, p2 = _write(tmp_path, _lines(gain=0.12), "l1.jsonl"), _write(tmp_path, _lg_lines(), "lg.jsonl")
    out1, out2 = tmp_path / "a.json", tmp_path / "b.json"
    assert A.main(["--l1", str(p1), "--lg", str(p2), "--out", str(out1)]) == 2 and not out1.exists()          # no n_L given: refused, no silent default
    assert A.main(["--l1", str(p1), "--lg", str(p2), "--out", str(out1), "--n-l", "520"]) == 0
    assert A.main(["--l1", str(p1), "--lg", str(p2), "--out", str(out2), "--n-l", "520"]) == 0
    assert out1.read_bytes() == out2.read_bytes()
    res = json.loads(out1.read_text())
    assert set(res) == {"meta", "family_L", "family_LG", "multiplicity_note"} and res["meta"]["spawn_key"] == [34] and res["meta"]["n_boot"] == 10000 and res["meta"]["n_l"] == 520
    assert res["family_LG"]["wording"] == "other noise types (shot, impulse, speckle; imagecorruptions severity 3)"
    nr = tmp_path / "n_rule.json"
    nr.write_text(json.dumps(dict(n_L=533)))
    assert A.main(["--l1", str(p1), "--n-rule", str(nr), "--out", str(tmp_path / "c.json")]) == 0
    assert json.loads((tmp_path / "c.json").read_text())["meta"]["n_l"] == 533
    assert res["meta"]["l1_predictions_sha256"] == A.hashlib.sha256(p1.read_bytes()).hexdigest()


def test_seed_slots_are_fixed_children_of_the_documented_root():
    assert A.ROOT_SEED == 20261028 and A.SPAWN_KEY == (34,)
    from exp_p2.gate import h_strata, tier3_fusion
    assert A.SPAWN_KEY != tuple(h_strata.SEED_SPAWN_KEY) and A.SPAWN_KEY != tuple(tier3_fusion.SEED_SPAWN_KEY)
    kids = np.random.SeedSequence(A.ROOT_SEED, spawn_key=A.SPAWN_KEY).spawn(len(A.SEED_SLOTS))
    assert np.random.default_rng(kids[0]).integers(0, 10 ** 9) == A._rng("L1").integers(0, 10 ** 9)
    assert len(set(A.SEED_SLOTS)) == len(A.SEED_SLOTS)
    assert A.SEED_SLOTS[A.SEED_SLOTS.index("BASELINES")] == "BASELINES" and A.SEED_SLOTS.index("BASELINES") == len(A.SEED_SLOTS) - 1 and A.SEED_SLOTS[1] == "L2_removed"      # appended last; no earlier child moved


def test_cli_selftest_flag(capsys):
    assert A.main(["--selftest"]) == 0
    assert json.loads(capsys.readouterr().out.strip().splitlines()[-1])["ok"] is True


def test_missing_noise_condition_is_reported_as_not_run():
    res = A.analyse_l(_lines(conds=("clean", "jpeg10")))
    assert res["L1"]["status"] == "not run"


# ------------------------------------------------------------------------------------------------ baselines (descriptive hooks)
def test_baseline_constants_decision_and_summary():
    assert BL.MODELS["clip"]["revision"].startswith("32bd6428") and BL.MODELS["siglip"]["revision"].startswith("9fdffc58")
    assert BL.decide([1, 2, 2], [0, 2, 3]).tolist() == [1, 0, 0]                    # a tie is wrong
    r = np.random.default_rng(0)
    y = {"clean": (r.random(300) < 0.9).astype(int), "noise0.1": (r.random(300) < 0.7).astype(int)}
    s = BL.summarise(y, np.random.default_rng(1), n_boot=500)
    assert "drop" in s["noise0.1"] and "drop" not in s["clean"] and s["noise0.1"]["drop_ci95"][0] < s["noise0.1"]["drop"] < s["noise0.1"]["drop_ci95"][1]
    assert BL.pixel_parity_ok([0.99, 0.985]) and not BL.pixel_parity_ok([0.99, 0.97]) and not BL.pixel_parity_ok([])
