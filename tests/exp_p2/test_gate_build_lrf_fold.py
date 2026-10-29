"""A6.3 fold builder (exp_p2/gate/build_lrf_fold.py): determinism, disjointness from every excluded set (SugarCrepe and FOIL included), the 5-32 token rule, the category-disjoint negatives, the length-matched
negative, the gid range, the leak check L0-L8 and the CLI refusals. CPU only; synthetic captions, annotations and pools."""
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
from exp_p2.gate import build_hardneg_items as bh, build_lrf_fold as blf, config, folds   # noqa: E402

N_TOK = lambda c: len(c.split())                                           # noqa: E731  (one token per word)
CATS = ("cat", "dog", "car", "bus", "tree", "boat", "sofa", "bird")


def _world(n_img=900, seed=0):
    rng = np.random.default_rng(seed)
    caps, cats = {}, {}
    for i in range(n_img):
        iid = 1000 + i
        caps[iid] = [" ".join(f"w{iid}_{k}_{j}" for j in range(int(rng.integers(3, 40)))) for k in range(5)]
        if i % 50 != 7:                                                    # a few images have no instance annotation
            cats[iid] = {CATS[int(c)] for c in rng.choice(len(CATS), int(rng.integers(1, 4)), replace=False)}
    return caps, cats


def _sources(caps, exclude_per=40):
    ids = sorted(caps)
    names = ("folds.cal", "folds.head", "folds.test", "folds.test_ext", "probe1+probe2", "P2-GATE-M1", "P2-GATE-M5", "foil.pool", "sugarcrepe")
    return {n: set(ids[k * exclude_per:(k + 1) * exclude_per]) for k, n in enumerate(names)}


def _build(seed=blf.SELECT_SEED, n=60, **kw):
    caps, cats = _world()
    src = _sources(caps)
    excl = set().union(*src.values())
    fold = blf.build(caps, cats, excl, N_TOK, n=n, seed=seed, **kw)
    return caps, cats, src, excl, fold


def test_schema_ids_and_token_rule():
    caps, cats, src, excl, fold = _build()
    t = fold["test"]
    assert fold["cal"] == fold["head"] == fold["test_ext"] == [] and len(t) == 60 and [it["idx"] for it in t] == list(range(60))
    assert [it["gid"] for it in t] == [8000 + i for i in range(60)]
    assert all(5 <= it["n_tok"] <= 32 and N_TOK(it["caption"]) == it["n_tok"] and it["caption"] in caps[it["image_id"]] for it in t)
    assert all(it["image_id"] in cats and it["image_id"] not in excl for it in t)       # annotated, and outside every excluded set
    assert len({it["image_id"] for it in t}) == 60
    u = fold["meta"]["universe"]
    assert u["n_no_instance_annotation"] > 0 and u["n_in_excluded_pools"] > 0 and u["n_no_caption_in_token_range"] >= 0 and u["n_eligible_images"] + u["n_no_instance_annotation"] + u["n_in_excluded_pools"] + u["n_no_caption_in_token_range"] == u["n_captioned"]
    folds.check_folds(fold, excl)


def test_deterministic_and_seed_dependent_and_independent_of_input_order():
    _, _, _, _, a = _build()
    _, _, _, _, b = _build()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) and a["meta"]["sha1"] == b["meta"]["sha1"]
    _, _, _, _, c = _build(seed=[config.SEED_GATE, 11])
    assert [it["image_id"] for it in c["test"]] != [it["image_id"] for it in a["test"]]
    caps, cats = _world()
    rev = {k: caps[k] for k in sorted(caps, reverse=True)}
    d = blf.build(rev, cats, set().union(*_sources(caps).values()), N_TOK, n=60)
    assert d["meta"]["sha1"] == a["meta"]["sha1"]


def test_the_stream_is_the_documented_one_and_unused_by_the_other_builders():
    assert blf.SELECT_SEED == [config.SEED_GATE, 10] and bh.SELECT_SEED == [config.SEED_GATE, 9]
    assert blf.GID_OFFSET == 8000 and all(not (lo <= 8000 < hi) for lo, hi in blf.used_gid_ranges().values())
    assert set(blf.used_gid_ranges()) >= {"folds.cal", "folds.head", "folds.test", "foil.fit", "foil.test", "hardneg.head", "hardneg.test"}


def test_primary_negatives_are_the_m4_rule_and_unchanged_function():
    _, cats, _, _, fold = _build()
    t = fold["test"]
    for it in t:
        j = it["neg_idx"]
        assert j != it["idx"] and t[j]["caption"] == it["neg_caption"] and t[j]["image_id"] == it["neg_image_id"] and it["neg_caption"] != it["caption"]
        assert it["neg_restricted"] and not (cats[it["image_id"]] & cats[it["neg_image_id"]])
        assert it["n_tok_neg"] == t[j]["n_tok"]
    # the same draw as folds.assign_negatives on the same list and stream
    import copy
    ref = copy.deepcopy(t)
    for it in ref:
        for k in ("neg_idx", "neg_image_id", "neg_caption", "neg_restricted"):
            it.pop(k)
    folds.assign_negatives(ref, cats, np.random.default_rng([*blf.SELECT_SEED, 1]))
    assert [it["neg_idx"] for it in ref] == [it["neg_idx"] for it in t]


def test_length_matched_negative_is_exact_when_possible_and_closest_otherwise():
    _, cats, _, _, fold = _build(n=200)
    t = fold["test"]
    by_len = {}
    for it in t:
        by_len.setdefault(it["n_tok"], []).append(it)
    for it in t:
        j = it["neg_len_idx"]
        assert j != it["idx"] and t[j]["caption"] == it["neg_caption_len"] and it["n_tok_neg_len"] == t[j]["n_tok"] and it["neg_len_diff"] == it["n_tok_neg_len"] - it["n_tok"]
        assert it["neg_len_exact"] == (it["neg_len_diff"] == 0) and it["neg_len_restricted"] and not (cats[it["image_id"]] & cats[t[j]["image_id"]])
        ok = [k for k in t if k["idx"] != it["idx"] and not (cats[it["image_id"]] & cats[k["image_id"]]) and k["caption"] != it["caption"]]
        best = min(abs(k["n_tok"] - it["n_tok"]) for k in ok)
        assert abs(it["neg_len_diff"]) == best                                  # exact if any candidate has the same count, else the smallest difference
    st = fold["meta"]["length_matching"]
    assert st["n"] == 200 and st["n_exact"] + st["n_not_exact"] == 200 and st["n_exact"] > st["primary_negative_n_equal_length"]
    assert st["mean_abs_diff"] < st["primary_negative_mean_abs_diff"]


def test_length_matched_fallback_when_every_pair_shares_a_category():
    items = [dict(idx=i, image_id=i, caption=f"c{i} x", n_tok=2 + i) for i in range(4)]
    blf.assign_length_matched(items, {i: {"cat"} for i in range(4)}, np.random.default_rng(0))
    assert all(not it["neg_len_restricted"] and it["neg_len_idx"] != it["idx"] for it in items)
    assert items[0]["neg_len_idx"] == 1                                         # closest length among the others


def test_too_few_eligible_images_raises():
    caps, cats = _world(n_img=30)
    with pytest.raises(RuntimeError, match="eligible"):
        blf.build(caps, cats, set(), N_TOK, n=500)


def test_available_limits_the_universe():
    caps, cats = _world()
    avail = set(sorted(caps)[:200])
    fold = blf.build(caps, cats, set(), N_TOK, n=40, available=avail)
    assert {it["image_id"] for it in fold["test"]} <= avail and fold["meta"]["universe"]["n_not_available"] == 700


# ------------------------------------------------------------------------------------------------ leak check
def test_leak_check_passes_and_prints_l7():
    caps, cats, src, excl, fold = _build()
    universe = {i for i in caps if i in cats}
    log = blf.leak_check(fold, src, universe, image_cats=cats, val_ids=set(caps))
    assert log["ok"] and {c["name"] for c in log["checks"]} >= {"L0_ids_are_integers", "L4_no_repeated_image_id", "L6_positive_control_ids_match_universe", "L7_hand_check_sample_printed"}
    l7 = [c for c in log["checks"] if c["name"].startswith("L7")][0]["detail"]
    assert [h["group"] for h in l7] == list(blf.CATEGORY_GROUPS) and all(h["coco_member"].startswith("val2017/") and h["coco_member"].endswith(".jpg") for h in l7)


def test_l6_positive_control_fails_when_the_id_format_does_not_match():
    caps, cats, src, excl, fold = _build()
    bad = dict(src, **{"folds.cal": {f"{i:012d}" for i in src["folds.cal"]}})          # string ids never match the integer universe
    universe = {i for i in caps if i in cats}
    with pytest.raises(blf.LeakCheckFailed, match="L6"):
        blf.leak_check(fold, bad, universe)


def test_l8_the_checker_catches_every_injected_leak():
    caps, cats, src, excl, fold = _build()
    universe = {i for i in caps if i in cats}
    st = blf.selftest(fold, src, universe)
    assert st["ok"] and st["clean_fold_passes"]
    for name in src:
        assert st[f"L8_injected_leak_with_{name}_is_caught"], name              # incl. sugarcrepe and foil.pool
    assert st["L8_repeated_image_is_caught"] and st["L8_gid_collision_is_caught"] and st["L8_wrong_length_matched_negative_is_caught"]


def test_the_checker_flags_sugarcrepe_and_foil_overlaps_separately():
    caps, cats, src, excl, fold = _build()
    universe = {i for i in caps if i in cats}
    f = json.loads(json.dumps(fold))
    f["test"][3]["image_id"] = sorted(src["sugarcrepe"])[0]
    with pytest.raises(blf.LeakCheckFailed) as e:
        blf.leak_check(f, src, universe)
    names = [c["name"] for c in e.value.log["checks"] if not c["ok"]]
    assert any(n.startswith("L3_") for n in names) and e.value.log["checks"][[c["name"] for c in e.value.log["checks"]].index(names[0])]["detail"]["sugarcrepe"] == 1


# ------------------------------------------------------------------------------------------------ the committed SugarCrepe files and the CLI
def test_sources_include_every_sugarcrepe_image_and_the_foil_pool(tmp_path):
    runs = tmp_path
    (runs / "P2-GATE-FOLDS").mkdir()
    (runs / "P2-GATE-FOLDS" / "folds.json").write_text(json.dumps(dict(cal=[dict(image_id=1)], head=[dict(image_id=2)], test=[dict(image_id=3)], test_ext=[dict(image_id=4)])))
    for rid, iid in (("P2-PROBE-01", 5), ("P2-PROBE-02", 6)):
        (runs / rid).mkdir()
        (runs / rid / "selection.json").write_text(json.dumps(dict(items=[dict(image_id=iid)])))
    for rid, iid in (("P2-GATE-M1", 7), ("P2-GATE-M5", 8)):
        (runs / rid).mkdir()
        (runs / rid / "items.jsonl").write_text(json.dumps(dict(image_id=iid)) + "\n")
    (runs / "P2-GATE-FOIL").mkdir()
    (runs / "P2-GATE-FOIL" / "pool.json").write_text(json.dumps(dict(fit=[dict(image_id=9)], test=[dict(image_id=10)])))
    src, rep = blf.collect_sources(runs, bh.SUGARCREPE_DIR)
    assert src["folds.cal"] == {1} and src["probe1+probe2"] == {5, 6} and src["P2-GATE-M1"] == {7} and src["foil.pool"] == {9, 10}
    rows = bh.load_sugarcrepe(bh.SUGARCREPE_DIR)
    assert src["sugarcrepe"] == {r["image_id"] for r in rows} and rep["sugarcrepe_n_images"] == len(src["sugarcrepe"]) == 1560
    # missing M1/M5/FOIL is an error unless the dry-run flag is given
    (runs / "P2-GATE-M5" / "items.jsonl").unlink()
    with pytest.raises(FileNotFoundError, match="M1/M5"):
        blf.collect_sources(runs, bh.SUGARCREPE_DIR)
    (runs / "P2-GATE-FOIL" / "pool.json").unlink()
    src2, rep2 = blf.collect_sources(runs, bh.SUGARCREPE_DIR, allow_missing_optional=True)
    assert "foil.pool" not in src2 and any("pool.json" in m for m in rep2["missing_optional"])


def test_cli_refuses_to_overwrite_and_a_failed_prerequisite_stops(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    out = tmp_path / "P2-LRF-FOLD"
    out.mkdir()
    (out / "folds_lrf.json").write_text("{}")
    assert blf.main([]) == 2 and (out / "folds_lrf.json").read_text() == "{}"
    (out / "folds_lrf.json").unlink()
    assert blf.main([]) == 2                                                    # no folds.json / probes under the temp RUNS: STOP, nothing written
    assert not (out / "folds_lrf.json").exists()


# ------------------------------------------------------------------------------------------------ A6 r1: 533-list and the union exclusions (C6-10)
def test_r1_default_is_the_533_item_list_and_n_l_is_a_prefix():
    assert blf.N_L == 533
    caps, cats = _world(n_img=1500)
    excl = set().union(*_sources(caps).values())
    full = blf.build(caps, cats, excl, N_TOK, n=533)
    pre = blf.build(caps, cats, excl, N_TOK, n=520)
    assert [it["image_id"] for it in full["test"]][:520] == [it["image_id"] for it in pre["test"]]
    assert [it["caption"] for it in full["test"]][:520] == [it["caption"] for it in pre["test"]]
    assert len(full["test"]) == 533 and full["test"][-1]["gid"] == 8532


def _make_runs(tmp_path):
    runs = tmp_path / "runs"
    def w(rel, obj, jsonl=False):
        p = runs / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(("".join(json.dumps(o) + "\n" for o in obj)) if jsonl else json.dumps(obj))
    w("P2-GATE-FOLDS/folds.json", dict(cal=[dict(image_id=1)], head=[dict(image_id=2)], test=[dict(image_id=3)], test_ext=[dict(image_id=4)]))
    w("P2-PROBE-01/selection.json", dict(items=[dict(image_id=5)]))
    w("P2-PROBE-02/selection.json", dict(items=[dict(image_id=6)]))
    w("P2-GATE-M1/items.jsonl", [dict(image_id=7)], True)
    w("P2-GATE-M5/items.jsonl", [dict(image_id=8)], True)
    w("P2-GATE-FOIL/pool.json", dict(fit=[dict(image_id=9)], test=[dict(image_id=10)]))
    w("P2-GATE-S2/items.jsonl", [dict(image_id=11, idx=0), dict(image_id=12, idx=1)], True)
    w("P2-GATE-SUITE/items.jsonl", [dict(image_id=13)], True)
    w("P2-SUITE-SMOKE/smoke.json", dict(image_ids=[14]))                         # not one of the discovered names: not read
    w("P2-HARDNEG-ITEMS/folds_hardneg.json", dict(cal=[], head=[dict(image_id=15)], test=[dict(image_id=16)], test_ext=[]))
    w("P2-GATE-S2/arrays/notes.json", dict(image_id=99))                          # not a discovered name either
    w("P2-LRF-FOLD/items.jsonl", [dict(image_id=17)], True)                       # the builder's own directory is never a source
    w("P2-GATE-M3/items.jsonl", [dict(image_id=18, rungs={"jpeg10": dict(image_id=19)})], True)       # nested ids are read too
    w("other-run/items.jsonl", [dict(image_id=20)], True)                         # not a runs/P2-* directory
    return runs


def test_union_exclusions_read_every_p2_items_selection_and_pool_file(tmp_path):
    runs = _make_runs(tmp_path)
    found = blf.discover_sources(runs)
    ids = set().union(*found.values())
    assert ids == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19}
    assert "P2-LRF-FOLD/items.jsonl" not in found and "other-run/items.jsonl" not in found and "P2-SUITE-SMOKE/smoke.json" not in found
    assert found["P2-GATE-FOLDS/folds.json"] == {1, 2, 3, 4} and found["P2-GATE-S2/items.jsonl"] == {11, 12}


def test_collect_sources_adds_the_discovered_files_and_lists_them_in_the_report(tmp_path):
    runs = _make_runs(tmp_path)
    src, rep = blf.collect_sources(runs, bh.SUGARCREPE_DIR)
    assert src["file:P2-GATE-S2/items.jsonl"] == {11, 12} and src["folds.cal"] == {1} and "sugarcrepe" in src
    assert rep["discovered_files"]["P2-GATE-SUITE/items.jsonl"] == 1 and rep["n_union"] == len(set().union(*src.values()))
    assert {11, 12, 13, 15, 16, 18, 19} <= set().union(*src.values())            # beyond the named groups of the draft
