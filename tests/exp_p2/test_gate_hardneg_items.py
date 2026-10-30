"""Family H builder (exp_p2/gate/build_hardneg_items.py, DRAFT): disjointness from every existing pool, determinism by seed, stratification over the seven SugarCrepe subsets, the 5-32 token rule on
both captions, the folds.json schema, and the committed SugarCrepe metadata. CPU only; synthetic rows except where the test names the committed files."""
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
from exp_p2.gate import build_hardneg_items as bh, config, foil, folds, seeds      # noqa: E402

SUBS = bh.SUBSETS
N_TOK = lambda c: len(c.split())                                           # noqa: E731  (synthetic tokenizer: one token per word)


def _caps(n_words, tag):
    return " ".join(f"{tag}{i}" for i in range(n_words))


def _rows(per_sub=220, n_images=1500, seed=0, scarce=None):
    """Synthetic SugarCrepe-like rows. Images are drawn from a shared id range so the same image appears in several subsets and sometimes twice in one subset. A few rows break the token rule."""
    rng = np.random.default_rng(seed)
    rows = []
    for s in SUBS:
        k = per_sub if s != scarce else 60
        ids = rng.integers(1000, 1000 + n_images, size=k)
        for j, iid in enumerate(ids):
            n = int(rng.integers(6, 20))
            neg_n = n + (2 if s.startswith("add") else 0)
            if j == 0:
                n = 3                                                       # positive too short
            if j == 1:
                neg_n = 40                                                  # negative too long
            rows.append(dict(subset=s, key=j, image_id=int(iid), caption=_caps(n, f"p{iid}_"), neg_caption=_caps(neg_n, f"n{iid}_")))
    return rows


def _build(rows=None, excluded=frozenset(), **kw):
    return bh.build(rows if rows is not None else _rows(), set(excluded), N_TOK, **kw)


# ------------------------------------------------------------------------------------------------ disjointness
def test_h3_h4_and_every_existing_pool_are_disjoint_and_one_row_per_image():
    rows = _rows()
    excluded = {r["image_id"] for r in rows[::7]}                          # every 7th row's image belongs to an existing pool
    out = _build(rows, excluded)
    h3, h4 = out["head"], out["test"]
    i3, i4 = [it["image_id"] for it in h3], [it["image_id"] for it in h4]
    assert len(h3) == 50 and len(h4) == 300
    assert len(set(i3)) == 50 and len(set(i4)) == 300                       # one row per image
    assert not (set(i3) & set(i4)) and not ((set(i3) | set(i4)) & excluded)
    assert out["cal"] == [] and out["test_ext"] == []
    folds.check_folds(out, excluded)                                         # the pipeline's own disjointness check
    assert len({it["gid"] for it in h3 + h4}) == 350


def test_gids_use_a_range_no_other_stage_uses():
    out = _build()
    assert {it["gid"] for it in out["head"]} == set(range(6000, 6050)) and {it["gid"] for it in out["test"]} == set(range(7000, 7300))
    assert config.FOLD_GID_OFFSET["test"] + folds.TEST_TOTAL <= foil.GID_FIT < foil.GID_FIT + 1000 <= foil.GID_TEST and foil.GID_TEST + 1000 <= 6000      # no overlap with folds (0-2499) or family B (4000-5999)


def test_an_image_is_never_used_in_two_subsets():
    out = _build()
    ids = [it["image_id"] for it in out["head"] + out["test"]]
    assert len(ids) == len(set(ids))


def test_a_pool_that_is_too_small_raises_instead_of_filling_from_elsewhere():
    rows = [r for r in _rows() if r["subset"] != "swap_obj" or r["key"] < 20]
    with pytest.raises(RuntimeError, match="swap_obj"):
        _build(rows)


def test_the_scarcest_subset_is_filled_first_and_reaches_its_quota():
    out = _build(_rows(scarce="swap_obj"))
    assert out["meta"]["selection"]["fill_order"][0] == "swap_obj"
    assert out["meta"]["per_subset"]["test"]["swap_obj"] in (42, 43) and out["meta"]["per_subset"]["head"]["swap_obj"] in (7, 8)


# ------------------------------------------------------------------------------------------------ determinism
def test_same_seed_same_file_different_seed_different_items():
    a, b = _build(), _build()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    c = _build(seed=[config.SEED_GATE, 123])
    assert [it["image_id"] for it in c["test"]] != [it["image_id"] for it in a["test"]]
    assert a["meta"]["sha1"] != c["meta"]["sha1"]


def test_the_selection_does_not_depend_on_the_order_of_the_input_rows():
    rows = _rows()
    a = _build(rows)
    b = _build(list(reversed(rows)))
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_the_seed_is_a_local_constant_and_seeds_py_is_untouched():
    assert bh.SELECT_SEED == [config.SEED_GATE, 9]
    assert not any("hardneg" in n for n in seeds.ANALYSES)                   # no append: the next position (32) is reserved for tier3_fusion (tier3_fusion.SEED_SPAWN_KEY = (32,))


# ------------------------------------------------------------------------------------------------ stratification
def test_every_subset_has_an_even_share_in_both_folds():
    out = _build()
    ps = out["meta"]["per_subset"]
    assert set(ps["test"]) == set(SUBS) == set(ps["head"])
    assert sorted(ps["test"].values()) == [42] + [43] * 6                    # 300 = 42 + 6 x 43
    assert sorted(ps["head"].values()) == [7] * 6 + [8]                      # 50 = 6 x 7 + 8
    for fold in ("head", "test"):
        for s in SUBS:
            assert sum(1 for it in out[fold] if it["subset"] == s) == ps[fold][s]


def test_the_final_order_is_shuffled_over_subsets_so_a_partial_run_is_spread():
    out = _build()
    first = [it["subset"] for it in out["test"][:70]]
    assert len(set(first)) == 7                                              # not sorted by subset
    assert [it["idx"] for it in out["test"]] == list(range(300))


# ------------------------------------------------------------------------------------------------ token rule and schema
def test_both_captions_are_inside_the_token_range_and_the_difference_is_recorded():
    out = _build()
    lo, hi = config.TOK_RANGE
    for it in out["head"] + out["test"]:
        assert lo <= it["n_tok"] <= hi and lo <= it["n_tok_neg"] <= hi
        assert it["n_tok"] == N_TOK(it["caption"]) and it["n_tok_neg"] == N_TOK(it["neg_caption"]) and it["tok_diff"] == it["n_tok_neg"] - it["n_tok"]
        assert it["neg_source"] == "sugarcrepe" and it["subset"] in SUBS
        assert it["tok_diff"] == (2 if it["subset"].startswith("add") else 0)
    why = out["meta"]["row_filter"]
    assert why["token_rule"] == 14 and why["total"] == len(_rows()) and why["eligible_rows"] == why["total"] - why["in_existing_pool"] - why["token_rule"] - why["same_caption"]


def test_a_negative_equal_to_the_positive_is_dropped():
    rows = _rows()
    for r in rows[:30]:
        r["neg_caption"] = r["caption"]
    elig, why = bh.eligible_rows(rows, set(), N_TOK)
    assert why["same_caption"] >= 1 and all(r["caption"] != r["neg_caption"] for r in elig)


def test_the_output_has_the_folds_schema_and_passes_the_runtime_token_check():
    out = _build()
    for it in out["head"] + out["test"]:
        assert {"idx", "gid", "image_id", "caption", "n_tok", "neg_caption"} <= set(it)
    rep = folds.token_check(out, N_TOK)                                     # what pipeline.check_fold_tokens runs at the start of M3/M4
    assert not rep["defect"] and rep["n_excluded_total"] == 0 and rep["per_fold"]["test"]["n"] == 300 and rep["per_fold"]["head"]["n"] == 50
    assert out["meta"]["sha1"] and out["meta"]["family"] == "H" and out["meta"]["tok_range"] == [5, 32]
    assert folds.test_items(out) == out["test"] and folds.test_items(out, 500) == out["test"]       # test_ext is empty, so the splice-donor pool is the 300 H4 images


# ------------------------------------------------------------------------------------------------ the committed SugarCrepe files
def test_the_committed_sugarcrepe_files_match_their_pinned_hashes_and_have_the_documented_counts():
    assert bh.verify_sha256() == []                                         # LF-normalised: a checkout with core.autocrlf=true rewrites the bytes
    rows = bh.load_sugarcrepe()
    assert len(rows) == 7511 and len({r["image_id"] for r in rows}) == 1560
    per = {s: sum(1 for r in rows if r["subset"] == s) for s in SUBS}
    assert per == dict(replace_obj=1652, replace_att=788, replace_rel=1406, swap_obj=245, swap_att=666, add_obj=2062, add_att=692)
    assert all(r["caption"] and r["neg_caption"] and r["caption"] != r["neg_caption"] for r in rows)


def test_a_modified_sugarcrepe_file_is_refused(tmp_path):
    for s in SUBS:
        (tmp_path / f"{s}.json").write_bytes((bh.SUGARCREPE_DIR / f"{s}.json").read_bytes())
    (tmp_path / "SHA256SUMS.txt").write_bytes((bh.SUGARCREPE_DIR / "SHA256SUMS.txt").read_bytes())
    assert bh.verify_sha256(tmp_path) == []
    (tmp_path / "add_obj.json").write_text("{}", encoding="utf8")
    assert bh.verify_sha256(tmp_path) == ["add_obj.json"]


def test_the_full_build_on_the_committed_files_with_a_synthetic_tokenizer():
    out = bh.build(bh.load_sugarcrepe(), set(), N_TOK)                       # no existing pool excluded here: only the quota logic is exercised on the real captions
    assert len(out["head"]) == 50 and len(out["test"]) == 300
    ids = [it["image_id"] for it in out["head"] + out["test"]]
    assert len(set(ids)) == 350


# ------------------------------------------------------------------------------------------------ the exclusion list
def _runs(tmp_path, with_probe2=True, with_items=True):
    d = tmp_path / config.FOLDS_RUN_ID
    d.mkdir()
    mk = lambda ids: [dict(image_id=i) for i in ids]                        # noqa: E731
    (d / "folds.json").write_text(json.dumps(dict(cal=mk([1]), head=mk([2]), test=mk([3]), test_ext=mk([4]))))
    for rid, ids in (("P2-PROBE-01", [5]), ("P2-PROBE-02", [6])):
        if rid == "P2-PROBE-02" and not with_probe2:
            continue
        (tmp_path / rid).mkdir()
        (tmp_path / rid / "selection.json").write_text(json.dumps(dict(items=mk(ids))))
    if with_items:
        (tmp_path / "P2-GATE-M1").mkdir()
        (tmp_path / "P2-GATE-M1" / "items.jsonl").write_text(json.dumps(dict(image_id=7)) + "\n")
    return tmp_path


def test_exclusion_ids_collect_every_pool_and_report_missing_optional_files(tmp_path):
    ids, rep = bh.exclusion_ids(_runs(tmp_path))
    assert ids == {1, 2, 3, 4, 5, 6, 7} and rep["n_excluded_images"] == 7
    assert rep["sources"]["folds.test_ext"] == 1 and rep["sources"]["P2-GATE-M1"] == 1 and len(rep["missing_optional"]) == 1 and "P2-GATE-M5" in rep["missing_optional"][0]


def test_exclusion_ids_refuse_a_missing_folds_file_or_probe_selection(tmp_path):
    with pytest.raises(FileNotFoundError, match="folds"):
        bh.exclusion_ids(tmp_path)
    with pytest.raises(FileNotFoundError, match="P2-PROBE-02"):
        bh.exclusion_ids(_runs(tmp_path, with_probe2=False))                  # data.probe_image_ids alone would skip it silently


def test_main_refuses_to_overwrite_an_existing_items_file(tmp_path, monkeypatch):
    out = tmp_path / "folds_hardneg.json"
    out.write_text("{}")
    monkeypatch.setattr(common, "RUNS", tmp_path)
    assert bh.main(["--out", str(out)]) == 2 and out.read_text() == "{}"


# ------------------------------------------------------------------------------------------------ leak check H-L6, H-L7, H-L8 (SAP A5.2, A5.11 item 5)
def test_h_l6_positive_control_needs_at_least_one_matching_image_id():
    rows = bh.load_sugarcrepe()
    some = {rows[0]["image_id"], rows[100]["image_id"]}
    ok = bh.h_l6(rows, some)
    assert ok["ok"] is True and ok["n_rows_in_existing_pools"] >= 2
    bad = bh.h_l6(rows, {-1})                                                  # an id format that never matches: the filter would prove nothing
    assert bad == dict(n_rows_in_existing_pools=0, ok=False)


def test_h_l7_samples_give_one_matched_id_per_source_with_both_file_names():
    rows = bh.load_sugarcrepe()
    ids = sorted({r["image_id"] for r in rows})
    by_source = {"folds.cal": {ids[5], 1}, "folds.head": {ids[3]}, "folds.test": {ids[9], ids[2]}, "folds.test_ext": {2}, "probe1+probe2": {ids[7]}}
    out = bh.h_l7_samples(rows, by_source)
    assert [o["source"] for o in out] == ["folds.cal", "folds.head", "folds.test", "folds.test_ext", "probe1+probe2"]
    assert out[0]["image_id"] == ids[5] and out[2]["image_id"] == ids[2] and out[3]["image_id"] is None and out[3]["n_matched"] == 0
    for o in out:
        if o["image_id"] is not None:
            assert o["sugarcrepe_filename"] == f"{o['image_id']:012d}.jpg" and o["coco_file"] == f"val2017/{o['image_id']:012d}.jpg" and o["sugarcrepe_subset"] in SUBS


def test_h_l8_an_injected_leak_makes_the_builder_fail(monkeypatch):
    """If the exclusion filter were broken (a pool sharing an id with cal gets through), folds.check_folds inside build() stops the build."""
    rows = _rows()
    leak = {r["image_id"] for r in rows[::3]}
    monkeypatch.setattr(bh, "eligible_rows", lambda rs, ex, fn, tr=config.TOK_RANGE: ([dict(r, n_tok=5, n_tok_neg=5) for r in rs], dict(total=len(rs), in_existing_pool=0, token_rule=0, same_caption=0, eligible_rows=len(rs))))
    with pytest.raises(AssertionError, match="probe image"):
        bh.build(rows, leak, N_TOK)
    monkeypatch.undo()
    assert bh.build(rows, leak, N_TOK)["head"]                                  # with the real filter the same call succeeds


def test_h_l4_foil_pool_overlap_is_asserted_and_counted():
    """FX-1: no H image is in the FOIL pool (family B); the count is recorded in the file's meta."""
    rows = _rows()
    clean = bh.build(rows, set(), N_TOK, foil_ids={1, 2, 3})
    assert clean["meta"]["h_l4"] == dict(checked=True, n_foil_pool_images=3, n_overlap=0)
    assert bh.build(rows, set(), N_TOK)["meta"]["h_l4"] == dict(checked=False)
    assert bh.build(rows, set(), N_TOK, foil_ids={1})["meta"]["sha1"] == clean["meta"]["sha1"]            # the check does not change the items
    leaked = clean["test"][5]["image_id"]
    with pytest.raises(AssertionError, match="H-L4"):
        bh.build(rows, set(), N_TOK, foil_ids={leaked, 1})
    with pytest.raises(AssertionError, match="H-L4"):
        bh.h_l4(clean["head"], {clean["head"][0]["image_id"]})


def test_foil_pool_ids_read_fit_and_test_and_a_missing_pool_stops_the_builder(tmp_path, monkeypatch):
    d = tmp_path / "P2-GATE-FOIL"
    d.mkdir()
    (d / "pool.json").write_text(json.dumps(dict(fit=[dict(image_id=11)], test=[dict(image_id=12), dict(image_id="13")], counts={})))
    assert bh.foil_pool_ids(tmp_path) == {11, 12, 13}
    with pytest.raises(FileNotFoundError, match="H-L4"):
        bh.foil_pool_ids(tmp_path / "nowhere")
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(bh, "verify_sha256", lambda d=None: [])
    monkeypatch.setattr(bh, "exclusion_ids", lambda runs=None, extra_files=(), by_source=None: ({1}, dict(sources={}, missing_optional=[])))
    (d / "pool.json").unlink()
    assert bh.main(["--out", str(tmp_path / "out.json")]) == 2 and not (tmp_path / "out.json").exists()


def test_exclusion_ids_can_return_the_per_source_sets(tmp_path):
    by = {}
    bh.exclusion_ids(_runs(tmp_path), by_source=by)
    assert by["folds.test"] == {3} and by["probe1+probe2"] == {5, 6} and by["P2-GATE-M1"] == {7}
