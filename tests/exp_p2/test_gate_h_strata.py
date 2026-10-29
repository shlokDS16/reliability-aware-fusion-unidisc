"""exp_p2/gate/h_strata.py (SAP addendum A5.7 to A5.9): identity checks, length strata and subsets, the stratified bootstrap, the seed stream, the label function and the length rule. CPU only; synthetic."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import common                                                   # noqa: E402
from exp_p2.gate import config, h_strata as hs, seeds                       # noqa: E402

SUBS = hs.SUBSETS
KEY = {"jpeg": "jpeg10", "noise": "noise0.1", "splice": "splice128"}


def _items(per=3):
    """per items in each of the 7 subsets, in a fixed non-sorted order."""
    out = []
    for i in range(per * 7):
        out.append(dict(idx=i, gid=7000 + i, image_id=20000 + i, caption=f"a cat {i} sits", n_tok=4, neg_caption=f"a dog {i} sits", subset=SUBS[i % 7], n_tok_neg=4, tok_diff=0, neg_source="sugarcrepe"))
    return out


def _rows(items, gate_minus_none):
    """gate_minus_none: function (idx, subset, corr) -> (yn, yg)."""
    rows = []
    for it in items:
        conds = {"clean": {"img": {"none": {"y": 1.0}, "gate0.05": {"y": 1.0}}}}
        for c, k in KEY.items():
            yn, yg = gate_minus_none(it["idx"], it["subset"], c)
            conds[k] = {"img": {"none": {"y": yn}, "gate0.05": {"y": yg}}}
        rows.append(dict(idx=it["idx"], gid=it["gid"], image_id=it["image_id"], caption=it["caption"], neg_caption=it["neg_caption"], conds=conds))
    return rows


def _gm(idx, sub, c):
    """jpeg: gate wins on every add_* item (LA) and loses on the first replace_obj item; noise: no difference; splice: gate wins on swap_att items only."""
    if c == "jpeg":
        if sub.startswith("add"):
            return 0.0, 1.0
        if sub == "replace_obj" and idx == 0:
            return 1.0, 0.0
        return 1.0, 1.0
    if c == "splice" and sub == "swap_att":
        return 0.0, 1.0
    return 1.0, 1.0


# ------------------------------------------------------------------------------------------------ identity checks
def test_identity_checks_pass_on_matching_rows_and_report_the_overlap_check():
    items = _items()
    rep = hs.identity_checks(_rows(items, _gm), items, m4_items=[dict(image_id=1)])
    assert rep["n_rows"] == 21 and rep["m4_image_overlap"] == dict(checked=True, n_shared=0)
    assert hs.identity_checks(_rows(items, _gm), items)["m4_image_overlap"]["checked"] is False


@pytest.mark.parametrize("field,value", [("gid", 6005), ("gid", 7300), ("image_id", 5), ("caption", "other"), ("neg_caption", "other")])
def test_identity_checks_refuse_a_row_that_differs_from_the_items_file(field, value):
    items = _items()
    rows = _rows(items, _gm)
    rows[4][field] = value
    with pytest.raises(hs.IdentityError):
        hs.identity_checks(rows, items)


def test_identity_checks_refuse_equal_captions_shared_m4_images_and_a_wrong_hash(tmp_path):
    items = _items()
    bad = [dict(it) for it in items]
    bad[2]["neg_caption"] = bad[2]["caption"]
    with pytest.raises(hs.IdentityError, match="equals neg_caption"):
        hs.identity_checks(_rows(bad, _gm), bad)
    with pytest.raises(hs.IdentityError, match="M4 test images"):
        hs.identity_checks(_rows(items, _gm), items, m4_items=[dict(image_id=items[0]["image_id"])])
    f = tmp_path / "folds_hardneg.json"
    f.write_text(json.dumps(dict(test=items)))
    run = tmp_path / "run"
    run.mkdir()
    (run / "config.json").write_text(json.dumps(dict(folds_sha256="0" * 64)))
    with pytest.raises(hs.IdentityError, match="folds_sha256"):
        hs.identity_checks(_rows(items, _gm), items, run_dir=run, folds_path=f)
    raw, lf = hs.sha256_pair(f)
    for h in (raw, lf):
        (run / "config.json").write_text(json.dumps(dict(folds_sha256=h)))
        assert hs.identity_checks(_rows(items, _gm), items, run_dir=run, folds_path=f)["folds_sha256"]["match"] is True


# ------------------------------------------------------------------------------------------------ strata
def test_length_strata_and_subsets_partition_the_items_and_count_b_and_c_exactly():
    items = _items()
    s = hs.strata_for(_rows(items, _gm), items, [dict(corruption=c, key=k) for c, k in KEY.items()], n_boot=200)
    j = s["jpeg"]
    assert j["LM"]["n"] == 15 and j["LA"]["n"] == 6 and j["all"]["n"] == 21                       # LM: 5 subsets x 3; LA: add_obj, add_att x 3
    assert (j["LA"]["b"], j["LA"]["c"], j["LA"]["net"]) == (6, 0, 1.0) and (j["LM"]["b"], j["LM"]["c"]) == (0, 1) and j["LM"]["net"] == pytest.approx(-1 / 15)
    assert (j["all"]["b"], j["all"]["c"]) == (6, 1) and j["all"]["p_unadjusted"] == pytest.approx(0.125) and j["all"]["exploratory"] is True
    assert set(j["per_subset"]) == set(SUBS) and j["per_subset"]["replace_obj"]["c"] == 1 and j["per_subset"]["add_att"]["b"] == 3 and all(v["n"] == 3 for v in j["per_subset"].values())
    assert s["noise"]["all"]["n_d"] == 0 and s["noise"]["all"]["p_unadjusted"] == 1.0
    assert s["splice"]["per_subset"]["swap_att"]["b"] == 3 and s["splice"]["LM"]["b"] == 3 and s["splice"]["LA"]["b"] == 0
    assert j["stratified_bootstrap"]["net"] == pytest.approx(5 / 21) and j["stratified_bootstrap"]["n"] == 21
    lo, hi = j["stratified_bootstrap"]["ci95"]
    lo90, hi90 = j["stratified_bootstrap"]["ci90"]
    assert lo <= lo90 <= 5 / 21 <= hi90 <= hi


def test_headroom_flips_use_the_none_arm_only():
    items = _items()
    rows = _rows(items, _gm)
    for r in rows[:3]:
        r["conds"]["jpeg10"]["img"]["none"]["y"] = 0.0                                           # clean right, corrupted wrong: F-
    rows[3]["conds"]["clean"]["img"]["none"]["y"] = 0.0                                          # clean wrong, corrupted right: F+
    h = hs.strata_for(rows, items, [dict(corruption="jpeg", key="jpeg10")], n_boot=50)["jpeg"]["decision_headroom"]
    assert h["F_minus"] >= 3 and h["F_plus"] >= 1 and 0 < h["restore_clean_bound_p"] <= 1 and h["descriptive"] is True


def test_strata_are_deterministic_and_the_seed_stream_is_the_registered_one():
    items = _items()
    fam = [dict(corruption=c, key=k) for c, k in KEY.items()]
    a, b = hs.strata_for(_rows(items, _gm), items, fam, n_boot=300), hs.strata_for(_rows(items, _gm), items, fam, n_boot=300)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    only_splice = hs.strata_for(_rows(items, _gm), items, [dict(corruption="splice", key="splice128")], n_boot=300)
    assert json.dumps(only_splice["splice"], sort_keys=True) == json.dumps(a["splice"], sort_keys=True)      # a corruption's stream does not depend on which others are run
    assert hs.SEED_SPAWN_KEY == (33,)
    kid = np.random.SeedSequence(seeds.ROOT_SEED, spawn_key=(33,)).spawn(3)[2]
    assert kid.spawn_key == (33, 2) and hs._child("splice").integers(0, 10**9) == np.random.default_rng(kid).integers(0, 10**9)
    assert (33,) != (32,)                                                                         # tier3_fusion.SEED_SPAWN_KEY


# ------------------------------------------------------------------------------------------------ label (A5.9)
def _per(**kw):
    base = {c: dict(tested=False, b=0, c=0, p_holm=1.0, gate_better=False) for c in config.REALISTIC}
    for c, v in kw.items():
        base[c] = {**dict(tested=True, p_holm=1.0, gate_better=False), **v}
    return base


def _an(per, sm=None, label="inconclusive", cal=False):
    return dict(primary=dict(per_corruption=per), s_m=dict(per_corruption={c: dict(rejected=bool(v)) for c, v in (sm or {}).items()}), outcome=dict(label=label),
                calibration=dict(fap_check=dict(K4_violation_evidence=cal)))


def _fam(rule="R1", test_fold=300, family=("jpeg",), status="ok"):
    return dict(family=[dict(corruption=c) for c in family], excluded=[dict(corruption="noise", reason="G 0 < 3")], n_rule=dict(rule=rule, test_fold=test_fold, G_star=2 if rule == "NO-GO" else 9, time_rule=dict(status=status)))


def test_label_nogo_and_not_run_statuses():
    assert hs.h_label(None, _fam("NO-GO", 0, (), "not tested (NO-GO)"))["label"] == "H-NOGO"
    r = hs.h_label(None, _fam("NO-GO", 0, (), "not run (pilot incomplete)"))
    assert r["label"] is None and r["status"] == "not run (pilot incomplete)"
    r = hs.h_label(None, _fam("R1", 0, ("jpeg",), "cut by time"))
    assert r["label"] is None and r["status"] == "not run (cut by time)"


def test_label_positive_split_into_m_and_g_per_corruption():
    per = _per(jpeg=dict(b=20, c=2, gate_better=True, p_holm=0.01), splice=dict(b=9, c=0, gate_better=True, p_holm=0.02))
    both = hs.h_label(_an(per, sm={"jpeg": True, "splice": True}), _fam(family=("jpeg", "splice")))
    assert both["label"] == "H-POS-M" and both["positive_split"] == {"jpeg": "M", "splice": "M"}
    one = hs.h_label(_an(per, sm={"jpeg": True, "splice": False}, cal=True), _fam(family=("jpeg", "splice")))
    assert one["label"] == "H-POS-G" and one["positive_split"] == {"jpeg": "M", "splice": "G"} and one["h_cal_clause_required"] is True
    assert hs.h_label(_an(per, sm={"jpeg": True, "splice": True}, cal=False), _fam())["h_cal_clause_required"] is False


def test_label_mixed_harm_negative_inconclusive():
    pos_and_harm = _per(jpeg=dict(b=20, c=2, gate_better=True, p_holm=0.01), splice=dict(b=0, c=9, p_holm=0.03))
    assert hs.h_label(_an(pos_and_harm, sm={"jpeg": True}), _fam())["label"] == "H-MIXED"
    harm = _per(splice=dict(b=0, c=9, p_holm=0.03))
    assert hs.h_label(_an(harm), _fam())["label"] == "H-HARM" and hs.h_label(_an(harm), _fam())["harm"] == ["splice"]
    null = _per(jpeg=dict(b=2, c=3, p_holm=1.0))
    assert hs.h_label(_an(null, label="negative"), _fam())["label"] == "H-NEG"
    assert hs.h_label(_an(null, label="inconclusive"), _fam())["label"] == "H-INC"
    c_gt_b_but_not_significant = _per(jpeg=dict(b=1, c=5, p_holm=0.4))
    assert hs.h_label(_an(c_gt_b_but_not_significant), _fam())["label"] == "H-INC"


# ------------------------------------------------------------------------------------------------ length rule (A5.7)
def test_length_rule_adds_the_clause_only_for_an_opposite_signed_lm_estimate_with_ci_excluding_zero():
    s = {"jpeg": dict(LM=dict(net=-0.08, ci95=[-0.15, -0.01])), "noise": dict(LM=dict(net=-0.08, ci95=[-0.15, 0.02])), "splice": dict(LM=dict(net=0.05, ci95=[0.01, 0.09]))}
    an = _an(_per(jpeg=dict(b=9, c=1, gate_better=True, p_holm=0.01), noise=dict(b=9, c=1, gate_better=True, p_holm=0.01), splice=dict(b=9, c=1, gate_better=True, p_holm=0.01)))
    lr = hs.length_rule(s, an)
    assert lr["jpeg"]["add_clause"] is True and lr["jpeg"]["clause"] == "not present on the length-matched subsets"
    assert lr["noise"]["add_clause"] is False and lr["splice"]["add_clause"] is False                 # CI includes 0 / same sign
    an2 = _an(_per(jpeg=dict(b=1, c=1, p_holm=1.0)))
    assert hs.length_rule(s, an2)["jpeg"]["add_clause"] is False                                       # no rejection, no clause
    assert hs.length_rule(None, an) == {} and hs.length_rule(s, None) == {}


# ------------------------------------------------------------------------------------------------ run / main
def _write_run(tmp_path, items, with_analysis=True):
    runs = tmp_path
    h4 = runs / "P2-GATE-H4"
    h4.mkdir()
    (h4 / "items.jsonl").write_text("\n".join(json.dumps(r) for r in _rows(items, _gm)) + "\n")
    d = runs / "P2-HARDNEG-ITEMS"
    d.mkdir()
    f = d / "folds_hardneg.json"
    f.write_text(json.dumps(dict(cal=[], head=[], test=items, test_ext=[])))
    (h4 / "config.json").write_text(json.dumps(dict(folds_sha256=hs.sha256_pair(f)[0])))
    h3 = runs / "P2-GATE-H3"
    h3.mkdir()
    (h3 / "family.json").write_text(json.dumps(_fam(family=("jpeg", "splice"))))
    if with_analysis:
        per = _per(jpeg=dict(b=6, c=1, gate_better=True, p_holm=0.01), splice=dict(b=3, c=0, p_holm=0.2))
        (h4 / "analysis.json").write_text(json.dumps(_an(per, sm={"jpeg": False})))
    return runs


def test_main_writes_h_strata_json_with_label_strata_and_length_rule(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    items = _items()
    runs = _write_run(tmp_path, items)
    fam = json.loads((runs / "P2-GATE-H3" / "family.json").read_text())
    fam["family"] = [dict(corruption="jpeg", key="jpeg10"), dict(corruption="splice", key="splice128")]
    (runs / "P2-GATE-H3" / "family.json").write_text(json.dumps(fam))
    assert hs.main(["--boot", "200"]) == 0
    out = json.loads((runs / "P2-GATE-H4" / "h_strata.json").read_text())
    assert out["label"]["label"] == "H-POS-G" and out["family"] == ["jpeg10", "splice128"] and set(out["strata"]) == {"jpeg", "splice"}
    assert out["length_rule"]["jpeg"]["add_clause"] is False and out["identity"]["folds_sha256"]["match"] is True and out["meta"]["h_strata_spawn_key"] == [33]


def test_main_stops_on_an_identity_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    items = _items()
    runs = _write_run(tmp_path, items)
    fam = json.loads((runs / "P2-GATE-H3" / "family.json").read_text())
    fam["family"] = [dict(corruption="jpeg", key="jpeg10")]
    (runs / "P2-GATE-H3" / "family.json").write_text(json.dumps(fam))
    (runs / "P2-GATE-H4" / "config.json").write_text(json.dumps(dict(folds_sha256="1" * 64)))
    assert hs.main(["--boot", "50"]) == 2 and "folds_sha256" in capsys.readouterr().err and not (runs / "P2-GATE-H4" / "h_strata.json").exists()
