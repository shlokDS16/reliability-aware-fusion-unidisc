"""M1 closed below 200 items (SAP A3b.12 and A3b.12a): the minimum n of 100 in `detect` (candidate_means, freeze_rivals, paired_vs_best_cheap, falsifier), the partial detection_frozen.json written
only with --closed-k / --closed-nq equal to the closing row, `frozen_meta` in the M4 analysis. SYNTHETIC DATA ONLY: nothing under runs/P2-PROBE-02 or runs/P2-GATE-M1 is read (blinding
attestation); every directory is a pytest temporary. CPU only."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import analyze_gate_m1, common                                   # noqa: E402
from exp_p2.gate import analysis_m4 as A, detect                              # noqa: E402
from test_gate_m1_chancebar import _synth                                     # noqa: E402
from test_gate_m4_analysis import build                                       # noqa: E402


def _items(n, q_gain=0.1, n_target=None, rival_means=None, rival_n=None, seed=0):
    """per_item list: jpeg and noise rows with q (n_target finite) and candidates `plainB`, `s3`, `rarity` with the given means and finite counts."""
    rng = np.random.default_rng(seed)
    rival_means = rival_means or {"plainB": 0.60, "s3": 0.55, "rarity": 0.52}
    rival_n = rival_n or {}
    n_target = n if n_target is None else n_target
    out = []
    for i in range(n):
        rec = {}
        for c in ("jpeg", "noise"):
            r = {"q": (0.60 + q_gain + rng.normal(0, 0.03)) if i < n_target else np.nan}
            for k, m in rival_means.items():
                r[k] = (m + rng.normal(0, 0.03)) if i < rival_n.get(k, n) else np.nan
            rec[c] = r
        out.append(rec)
    return out


# ------------------------------------------------------------------------------------------------ detect.py, min_n
def test_candidate_means_with_min_n_drops_short_candidates_even_when_their_mean_is_highest():
    rows = [dict(a=0.9 if i < 99 else np.nan, b=0.6) for i in range(150)]
    assert set(detect.candidate_means(rows, cheap=("a", "b"))) == {"a", "b"}                    # old behaviour
    assert set(detect.candidate_means(rows, cheap=("a", "b"), min_n=None)) == {"a", "b"}
    assert set(detect.candidate_means(rows, cheap=("a", "b"), min_n=100)) == {"b"}              # 99 finite items: not selected although the mean is the highest
    rows2 = [dict(a=0.9 if i < 100 else np.nan, b=0.6) for i in range(150)]
    assert set(detect.candidate_means(rows2, cheap=("a", "b"), min_n=100)) == {"a", "b"}        # exactly 100 is eligible


def test_freeze_rivals_never_selects_a_candidate_with_99_finite_items():
    pi = _items(150, rival_means={"plainB": 0.60, "s3": 0.80}, rival_n={"s3": 99})
    old = detect.freeze_rivals(pi)
    assert old["jpeg"]["rival"] == "s3" and old["jpeg"]["n_items"] == 150 and "n_pool" not in old["jpeg"]            # default behaviour unchanged
    new = detect.freeze_rivals(pi, min_n=100)
    e = new["jpeg"]
    assert e["available"] and e["rival"] == "plainB" and e["n_items"] == 150 and e["n_pool"] == 150 and e["all_n"] == {"plainB": 150} and e["min_n"] == 100


def test_freeze_rivals_reports_n_items_as_the_finite_count_of_the_selected_rival():
    pi = _items(150, rival_means={"plainB": 0.60}, rival_n={"plainB": 120})
    e = detect.freeze_rivals(pi, min_n=100)["noise"]
    assert e["n_items"] == 120 and e["n_pool"] == 150 and e["all_n"]["plainB"] == 120


def test_freeze_rivals_with_no_eligible_candidate_is_unavailable_with_a_reason():
    pi = _items(99)
    for c, e in detect.freeze_rivals(pi, min_n=100).items():
        assert e == dict(available=False, reason="no candidate with n >= 100", n_pool=99)
    assert detect.freeze_rivals(pi)["jpeg"]["available"] is True                                  # the 200-item code path has no floor
    assert detect.freeze_rivals([], min_n=100)["jpeg"] == dict(available=False, reason="no candidate with n >= 100", n_pool=0)


def test_paired_vs_best_cheap_is_unavailable_below_the_floor_in_both_branches():
    pi = _items(150, n_target=99)                                                                   # q finite on 99 items only
    for rs in (False, True):
        r = detect.paired_vs_best_cheap(pi, "jpeg", "q", n_boot=200, reselect=rs, min_n=100)
        assert r["available"] is False and r["n"] == 99 and "n < 100" in r["reason"] and r["corr"] == "jpeg"
        assert detect.paired_vs_best_cheap(pi, "jpeg", "q", n_boot=200, reselect=rs)["available"] is True          # no floor by default
    ok = _items(150, n_target=100)
    assert detect.paired_vs_best_cheap(ok, "jpeg", "q", n_boot=200, min_n=100)["available"] is True
    short_rival = _items(150, rival_means={"plainB": 0.6}, rival_n={"plainB": 99})
    assert detect.paired_vs_best_cheap(short_rival, "jpeg", "q", n_boot=200, min_n=100) == dict(corr="jpeg", available=False, reason="no candidate with n >= 100", n=0)
    # reselect branch: the pairwise-complete count over all eligible candidates must also reach the floor
    staggered = _items(150, rival_means={"plainB": 0.6, "s3": 0.58}, rival_n={"plainB": 150, "s3": 100})
    for i in range(100, 150):
        staggered[i]["jpeg"]["s3"] = np.nan
    assert detect.paired_vs_best_cheap(staggered, "jpeg", "q", n_boot=100, reselect=True, min_n=100)["available"] is True


def test_default_behaviour_is_reproduced_exactly_when_min_n_is_none():
    pi = _items(120, seed=3)
    a = detect.paired_vs_best_cheap(pi, "jpeg", "q", n_boot=300)
    b = detect.paired_vs_best_cheap(pi, "jpeg", "q", n_boot=300, min_n=None)
    assert a == b
    fa, fb = detect.falsifier(pi, "q", n_boot=300), detect.falsifier(pi, "q", n_boot=300, min_n=None)
    assert fa == fb and "min_n" not in fa and fa["falsified"] is bool(not fa["q_significantly_better_on"])
    assert detect.freeze_rivals(pi) == detect.freeze_rivals(pi, min_n=None)
    assert detect.falsifier([], "q", n_boot=50)["falsified"] is None


def test_falsifier_with_min_n_is_not_evaluated_when_both_corruptions_have_n_99():
    pi = _items(150, n_target=99)
    f = detect.falsifier(pi, "q", n_boot=200, min_n=100)
    assert f["falsified"] is None and "not evaluated" in f["note"] and f["min_n"] == 100 and f["n"] == {"jpeg": 99, "noise": 99}


def test_falsifier_with_min_n_is_met_when_both_are_evaluated_and_neither_wins():
    pi = _items(150, q_gain=-0.2)                                                                    # q far below the rival on both corruptions
    f = detect.falsifier(pi, "q", n_boot=300, min_n=100)
    assert f["falsified"] is True and f["q_significantly_better_on"] == [] and f["n"] == {"jpeg": 150, "noise": 150} and f["min_n"] == 100
    assert detect.falsifier(pi, "q", n_boot=300)["falsified"] is True                                # same as the old line `not wins`


def test_falsifier_with_min_n_is_false_when_one_corruption_wins_and_the_other_has_n_50():
    pi = _items(150, q_gain=0.25)
    for i in range(150):
        if i >= 50:
            pi[i]["noise"]["q"] = np.nan
    f = detect.falsifier(pi, "q", n_boot=300, min_n=100)
    assert f["per_corruption"]["noise"]["available"] is False and f["n"]["noise"] == 50
    assert f["q_significantly_better_on"] == ["jpeg"] and f["falsified"] is False
    only_loser = _items(150, q_gain=-0.2)
    for i in range(50, 150):
        only_loser[i]["noise"]["q"] = np.nan
    g = detect.falsifier(only_loser, "q", n_boot=300, min_n=100)
    assert g["falsified"] is None and "not evaluated" in g["note"]                                    # one corruption evaluated with no win, the other not evaluated: neither met nor unmet


# ------------------------------------------------------------------------------------------------ analyze_gate_m1: the partial freeze
def _write_args(tmp_path, monkeypatch, n, with_q=False, seed=0):
    p2, m1 = _synth(tmp_path, n, lambda i: 2.0, seed=seed, with_q=with_q)
    monkeypatch.setattr(common, "RUNS", tmp_path)
    return p2, m1


def test_partial_pool_of_120_with_the_closing_row_writes_a_partial_file_without_q(tmp_path, monkeypatch, capsys):
    _write_args(tmp_path, monkeypatch, 120)
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "200", "--closed-k", "120", "--closed-nq", "0"]) == 0
    f = json.loads((tmp_path / "P2-GATE-M1" / "detection_frozen.json").read_text())
    assert f["partial"] is True and f["closed_k"] == 120 and f["closed_nq"] == 0 and f["min_n"] == 100 and f["n_items"] == 120 and "closed partial" in f["source"]
    for c in ("jpeg", "noise"):
        e = f["frozen"][c]
        assert e["available"] and e["rival"] and e["n_items"] >= 100 and e["n_pool"] == 120 and set(e["all_n"]) == set(e["all_means"])
    assert "PARTIAL" in capsys.readouterr().out
    res = json.loads((tmp_path / "P2-GATE-M1" / "analysis.json").read_text())
    assert res["n_items_with_q"] == 0 and res["min_n"] == 100 and res["falsifier"]["falsified"] is None and res["pool"]["complete"] is False


def test_partial_pool_of_99_items_writes_a_file_with_every_corruption_unavailable(tmp_path, monkeypatch):
    _write_args(tmp_path, monkeypatch, 99, seed=1)
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "200", "--closed-k", "99", "--closed-nq", "0"]) == 0
    f = json.loads((tmp_path / "P2-GATE-M1" / "detection_frozen.json").read_text())
    assert f["partial"] is True and all(e["available"] is False and "no candidate with n >= 100" in e["reason"] and e["n_pool"] == 99 for e in f["frozen"].values())


def test_a_closing_row_that_differs_from_the_directories_returns_2_and_writes_nothing(tmp_path, monkeypatch, capsys):
    _write_args(tmp_path, monkeypatch, 120, seed=2)
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "100", "--closed-k", "119", "--closed-nq", "0"]) == 2
    err = capsys.readouterr().err
    assert "k = 119" in err and "k = 120" in err
    assert not (tmp_path / "P2-GATE-M1" / "detection_frozen.json").exists() and not (tmp_path / "P2-GATE-M1" / "analysis.json").exists()
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "100", "--closed-k", "120", "--closed-nq", "7"]) == 2          # n_q differs
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "100", "--closed-k", "120"]) == 2                              # the two numbers go together
    assert not (tmp_path / "P2-GATE-M1" / "detection_frozen.json").exists()


def test_k_120_without_the_flags_writes_nothing_as_before(tmp_path, monkeypatch, capsys):
    _write_args(tmp_path, monkeypatch, 120, seed=3)
    assert analyze_gate_m1.main(["--no-pixels", "--boot", "100"]) == 0
    assert not (tmp_path / "P2-GATE-M1" / "detection_frozen.json").exists()
    out = capsys.readouterr().out
    assert "NOT written" in out and "--closed-k" in out and "--closed-nq" in out
    res = json.loads((tmp_path / "P2-GATE-M1" / "analysis.json").read_text())
    assert res["min_n"] is None and res["label"].startswith("exploratory")                         # old floor-free behaviour


def test_the_partial_file_is_write_once(tmp_path, monkeypatch, capsys):
    _write_args(tmp_path, monkeypatch, 120, seed=4)
    args = ["--no-pixels", "--boot", "100", "--closed-k", "120", "--closed-nq", "0"]
    assert analyze_gate_m1.main(args) == 0
    assert analyze_gate_m1.main(args) == 2                                                          # artifacts.write_once refuses without --force


# ------------------------------------------------------------------------------------------------ analysis_m4: frozen_meta and S-D2
def test_s_d2_gives_p_one_and_keeps_m_2_for_an_unavailable_entry_and_labels_the_pool(tmp_path):
    run, rows = build(tmp_path, 12, {}, conds=("clean", "jpeg10", "noise0.1", "patch"), tex=True)
    fam = [dict(corruption="jpeg", severity=10, key="jpeg10"), dict(corruption="noise", severity=0.1, key="noise0.1")]
    frozen = {"jpeg": dict(available=False, reason="no candidate with n >= 100", n_pool=99), "noise": dict(available=False, reason="no candidate with n >= 100", n_pool=99)}
    meta = dict(partial=True, closed_k=99, closed_nq=0, min_n=100)
    r = A.s_d2(run, rows, fam, frozen, None, 200, meta)
    assert r["holm_m"] == 2 and all(x["tested"] is False and x["p"] == 1.0 and x["p_holm"] == 1.0 and "no candidate with n >= 100" in x["reason"] for x in r["per_corruption"].values())
    assert "completed prefix of k = 99 items (not 200)" in r["rival_frozen_label"] and "n_q = 0" in r["rival_frozen_label"]
    assert A.s_d2(run, rows, fam, frozen, None, 100)["rival_frozen_label"] == "rival frozen on the complete M1 set (200 items)"           # no meta: the old label


def test_analysis_json_carries_frozen_meta(tmp_path):
    run, rows = build(tmp_path, 12, {}, conds=("clean", "jpeg10", "noise0.1", "patch"), tex=True)
    fam = [dict(corruption="jpeg", severity=10, key="jpeg10"), dict(corruption="noise", severity=0.1, key="noise0.1")]
    meta = dict(partial=True, closed_k=106, closed_nq=0, min_n=100)
    res = A.run(run, fam, n_boot=100, frozen={"jpeg": dict(available=False), "noise": dict(available=False)}, frozen_meta=meta)
    assert res["frozen_meta"] == meta and "k = 106" in res["s_d2"]["rival_frozen_label"]
    assert A.run(run, fam, n_boot=100)["frozen_meta"] is None


# ------------------------------------------------------------------------------------------------ code audit part 1: m-1 and m-3
def test_falsifier_n_is_the_paired_finite_count_not_the_pool_size():
    pi = _items(150, q_gain=0.25, n_target=120)                                  # q is finite on 120 of the 150 pool items
    f = detect.falsifier(pi, "q", n_boot=200, min_n=100)
    assert f["n"] == {"jpeg": 120, "noise": 120}
    r = f["per_corruption"]["jpeg"]
    assert r["n_pair"] == 120 and r["n_items"] == 150
    assert "n_pair" not in detect.paired_vs_best_cheap(pi, "jpeg", "q", n_boot=100)          # default behaviour unchanged


def test_ps_output_text_has_the_ab1_sentence_and_not_the_superseded_ad4_clause():
    r = A.ps_family([], rule="R1", family=None, n_boot=10)
    assert r["positive_control"] == "not met" and "barred" not in r["on_not_met"] and "pipeline defect suspected" in r["on_not_met"]
    assert "not permitted whether PS is met or not" in r["label"] and "the pipeline is not broken" in r["label"]
    assert "bars the sentence" not in (A.ps_family.__doc__ or "")
