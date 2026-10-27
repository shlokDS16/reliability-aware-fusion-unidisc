"""Corruptions, cheap baselines, folds and the hard-negative builder (v2 sections 4.2, 4.3, 7.3, 7.5, Alg. 11). CPU only, no model."""
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fake_gate import fake_image                                                       # noqa: E402
from exp_p2 import core                                                               # noqa: E402
from exp_p2.gate import baselines, corruptions, data, folds, hardneg                  # noqa: E402


# ------------------------------------------------------------------------------------------------ corruptions
class _EncPix:
    """Stand-in scorer for run_probe2.corrupt: encode() returns the pixel array so images can be compared exactly."""
    @staticmethod
    def encode(img):
        return np.asarray(img).copy()


def _pil512(seed=0):
    from PIL import Image
    return fake_image(seed, 128).resize((512, 512), Image.BICUBIC)


def test_jpeg_and_noise_reproduce_probe2_exactly():
    from exp_p2 import run_probe2 as rp
    pil = _pil512(1)
    clean = np.zeros(1024, np.int64)
    a, ia = rp.corrupt("jpeg", _EncPix, pil, clean, np.random.default_rng(5))
    assert np.array_equal(np.asarray(corruptions.jpeg(pil, rp.JPEG_Q)), np.asarray(ia))
    a, ia = rp.corrupt("noise", _EncPix, pil, clean, np.random.default_rng(5))
    assert np.array_equal(np.asarray(corruptions.gaussian_noise(pil, rp.NOISE_SIGMA, np.random.default_rng(5))), np.asarray(ia))
    for name in ("swap", "patch"):
        c1, _ = rp.corrupt(name, _EncPix, pil, np.arange(1024), np.random.default_rng(3))
        c2 = corruptions.apply_token(name, np.arange(1024), np.random.default_rng(3), grid=32, patch=8, swap_frac=0.15, vocab=16384)
        assert np.array_equal(c1, c2)


def test_splice_copies_exactly_the_donor_region_and_nothing_else():
    pil, donor = _pil512(1), _pil512(2)
    out, info = corruptions.splice(pil, donor, 128, np.random.default_rng(0))
    a, d, o = np.asarray(pil), np.asarray(donor), np.asarray(out)
    (sy, sx), (ty, tx), s = info["src"], info["dst"], info["size"]
    assert s == 128 and 0 <= ty <= 512 - s and 0 <= tx <= 512 - s
    assert np.array_equal(o[ty:ty + s, tx:tx + s], d[sy:sy + s, sx:sx + s])
    mask = np.ones(a.shape[:2], bool)
    mask[ty:ty + s, tx:tx + s] = False
    assert np.array_equal(o[mask], a[mask])
    out2, info2 = corruptions.splice(pil, donor, 128, np.random.default_rng(0))
    assert info2 == info and np.array_equal(np.asarray(out2), o)                          # deterministic per seed
    assert np.array_equal(np.asarray(corruptions.apply_pixel("splice", 192, pil, np.random.default_rng(1), donor)).shape, a.shape)
    with pytest.raises(ValueError):
        corruptions.apply_pixel("splice", 128, pil, np.random.default_rng(0))


def test_ladders_are_applied_in_order_and_stronger_rungs_change_more():
    pil = _pil512(3)
    a = np.asarray(pil, float)
    d10 = np.abs(np.asarray(corruptions.apply_pixel("jpeg", 10, pil, np.random.default_rng(0)), float) - a).mean()
    d5 = np.abs(np.asarray(corruptions.apply_pixel("jpeg", 5, pil, np.random.default_rng(0)), float) - a).mean()
    n1 = np.abs(np.asarray(corruptions.apply_pixel("noise", 0.10, pil, np.random.default_rng(0)), float) - a).mean()
    n2 = np.abs(np.asarray(corruptions.apply_pixel("noise", 0.20, pil, np.random.default_rng(0)), float) - a).mean()
    assert d5 > d10 > 0 and n2 > n1 > 0
    assert corruptions.corruption_key("jpeg", 10) == "jpeg10" and corruptions.corruption_key("noise", 0.1) == "noise0.1"
    assert corruptions.corruption_key("patch") == "patch"


def test_denoise_runs_and_keeps_shape_and_reduces_noise():
    pil = _pil512(4)
    noisy = corruptions.gaussian_noise(pil, 0.1, np.random.default_rng(0))
    den = corruptions.denoise(noisy)
    assert den.size == noisy.size
    a = np.asarray(pil, float)
    assert np.abs(np.asarray(den, float) - a).mean() < np.abs(np.asarray(noisy, float) - a).mean()


# ------------------------------------------------------------------------------------------------ baselines
def test_patch_texture_flat_vs_noisy():
    pix = np.full((64, 64, 3), 128, np.uint8)
    pix[0:16, 0:16] = np.random.default_rng(0).integers(0, 256, (16, 16, 3))
    t = baselines.patch_texture(pix, 4)
    assert t.shape == (16,) and t[0] > 1000 and np.allclose(t[1:], 0)
    assert np.isnan(baselines.patch_texture(None, 4)).all()


def test_neighbour_codebook_distance():
    grid = 5
    cb = np.random.default_rng(0).normal(size=(30, 6))
    same = baselines.neighbour_codebook_distance(np.full(grid * grid, 3), cb, grid)
    assert np.allclose(same, 0)
    codes = np.full(grid * grid, 3)
    codes[12] = 9                                                                         # centre token differs from all 8 neighbours
    d = baselines.neighbour_codebook_distance(codes, cb, grid)
    assert d[12] == pytest.approx(np.linalg.norm(cb[3] - cb[9]))
    assert d[13] == pytest.approx(np.linalg.norm(cb[3] - cb[9]) / 8)                      # a neighbour: 1 differing of 8 neighbours
    assert d[0] == 0                                                                      # corner far away: 0
    assert np.isnan(baselines.neighbour_codebook_distance(codes, None, grid)).all()


def test_code_rarity_and_leave_one_out():
    arrays = [np.array([0, 0, 1]), np.array([0, 2, 2]), np.array([3, 3, 3])]
    f = baselines.CodeFreq.fit(arrays, 5)
    r = f.rarity(np.array([0, 4]))
    assert r[1] > r[0]                                                                    # unseen code is rarer
    assert r[0] == pytest.approx(-np.log((3 + 1) / (9 + 5)))
    f2 = baselines.CodeFreq.fit(arrays, 5, exclude=0)
    assert f2.total == 6 and f2.counts[1] == 0


def test_tbv_helpers_and_copy_statistic():
    lp = np.log(np.full(100, 0.999))
    s = baselines.copy_through_stat(lp)
    assert s["copy_suspected"] and s["frac_p_obs_gt_0p99"] == 1.0
    assert not baselines.copy_through_stat(np.log(np.full(100, 0.01)))["copy_suspected"]
    assert np.isnan(baselines.tbv_suspicion(None, 4)).all() and baselines.tbv_suspicion(np.array([-1.0]), 1)[0] == 1.0
    assert baselines.extract_codebook(object()) is None


# ------------------------------------------------------------------------------------------------ folds
def _fake_captions(n=400, seed=0):
    rng = np.random.default_rng(seed)
    caps = {}
    for i in range(1, n + 1):
        caps[i * 3] = [" ".join(f"w{int(x)}" for x in rng.integers(0, 50, int(rng.integers(3, 40)))) for _ in range(3)]
    return caps


def _cats_for(ids, seed=0):
    rng = np.random.default_rng(seed)
    names = ["person", "dog", "cat", "car", "bus", "pizza", "cake", "bench"]
    return {i: set(rng.choice(names, size=int(rng.integers(1, 4)), replace=False)) for i in ids}


def test_folds_are_disjoint_exclude_probe_ids_and_are_deterministic():
    caps = _fake_captions()
    excl = set(list(caps)[:50])
    cats = _cats_for(caps)
    f = folds.build_folds(caps, lambda c: len(c.split()), excl, sizes=(60, 20, 60), image_cats=cats)
    folds.check_folds(f, excl)
    assert [len(f[k]) for k in ("cal", "head", "test")] == [60, 20, 60]
    assert all(5 <= it["n_tok"] <= 32 for k in ("cal", "head", "test") for it in f[k])
    f2 = folds.build_folds(caps, lambda c: len(c.split()), excl, sizes=(60, 20, 60), image_cats=cats)
    assert f == f2                                                                         # deterministic
    gids = [it["gid"] for k in ("cal", "head", "test") for it in f[k]]
    assert len(set(gids)) == len(gids)
    f3 = folds.build_folds(caps, lambda c: len(c.split()), excl, sizes=(60, 20, 60), image_cats=cats, seed=1)
    assert f3 != f


def test_negatives_share_no_category_with_the_image_and_stay_in_fold():
    caps = _fake_captions()
    cats = _cats_for(caps)
    f = folds.build_folds(caps, lambda c: len(c.split()), set(), sizes=(60, 20, 60), image_cats=cats)
    for k in ("cal", "head", "test"):
        items = f[k]
        for it in items:
            j = it["neg_idx"]
            assert j != it["idx"] and items[j]["image_id"] == it["neg_image_id"] and items[j]["caption"] == it["neg_caption"] != it["caption"]
            if it["neg_restricted"]:
                assert not (cats[it["image_id"]] & cats[it["neg_image_id"]])
    assert sum(it["neg_restricted"] for it in f["test"]) > 0.5 * 60
    g = folds.build_folds(caps, lambda c: len(c.split()), set(), sizes=(10, 5, 10), image_cats=None)         # no annotations: fallback, flagged
    assert not any(it["neg_restricted"] for it in g["cal"])


def test_folds_file_roundtrip_and_ensure_does_not_rebuild(tmp_path):
    caps = _fake_captions()
    f = folds.build_folds(caps, lambda c: len(c.split()), set(), sizes=(10, 5, 10))
    p = folds.save_folds(f, tmp_path / "x" / "folds.json")
    assert folds.ensure_folds(lambda c: (_ for _ in ()).throw(AssertionError("must not tokenize")), p) == f


def test_extending_the_test_fold_keeps_the_other_folds_and_the_test_prefix():
    caps = _fake_captions(900)
    cats = _cats_for(caps)
    f = folds.build_folds(caps, lambda c: len(c.split()), set(), sizes=(60, 20, 60), image_cats=cats)
    g = folds.extend_test_fold(f, 100, caps, lambda c: len(c.split()), set(), cats)
    assert g["cal"] == f["cal"] and g["head"] == f["head"] and len(g["test"]) == 100 and g["meta"]["test_extended_from"] == 60
    assert [i["image_id"] for i in g["test"][:60]] == [i["image_id"] for i in f["test"]]
    folds.check_folds(g, set())


def test_probe_ids_exclude_both_probes(tmp_path):
    import json
    for rid, ids in (("P2-PROBE-01", [1, 2]), ("P2-PROBE-02", [2, 3])):
        (tmp_path / rid).mkdir()
        (tmp_path / rid / "selection.json").write_text(json.dumps(dict(items=[dict(image_id=i) for i in ids])))
    assert data.probe_image_ids(tmp_path) == {1, 2, 3}


def test_real_probe_ids_are_found_and_overlap_is_small():
    ids = data.probe_image_ids()
    if not ids:
        pytest.skip("probe selection files not in this worktree")
    assert 450 <= len(ids) <= 500                                                          # 300 + 200 minus the shared ones (spec: 6 shared)


# ------------------------------------------------------------------------------------------------ hard negatives
SUP = {"person": "person", "dog": "animal", "cat": "animal", "elephant": "animal", "zebra": "animal", "giraffe": "animal", "bird": "animal", "horse": "animal",
       "bear": "animal", "sheep": "animal", "cow": "animal", "skateboard": "sports", "surfboard": "sports", "kite": "sports", "snowboard": "sports",
       "frisbee": "sports", "bench": "outdoor", "stop sign": "outdoor", "fire hydrant": "outdoor", "teddy bear": "indoor", "dining table": "furniture",
       "chair": "furniture", "couch": "furniture", "bed": "furniture"}
SUP = {c: SUP.get(c, "other") for c in hardneg.CATS} | SUP


def test_table_has_80_categories_and_matches_the_real_instances_file():
    assert len(hardneg.CATS) == 80
    try:
        sup, _ = data.load_instances()
    except FileNotFoundError:
        pytest.skip("instances_val2017.json not available")
    assert set(sup) == set(hardneg.CATS)


def test_matcher_phrases_plurals_and_ambiguous_words():
    m = hardneg.find_matches("A teddy bear and two bears on a dining table with oranges and an orange cat")
    cats = [(x["cat"], x["plural"]) for x in m]
    assert cats == [("teddy bear", False), ("bear", True), ("dining table", False), ("orange", True), ("cat", False)]
    assert hardneg.find_matches("An orange sunset") == []
    assert [x["cat"] for x in hardneg.find_matches("two men, a woman, and a bike")] == ["person", "person", "bicycle"]


def test_build_one_replaces_noun_keeps_number_and_fixes_article():
    rng = np.random.default_rng(0)
    r = hardneg.build_one("An elephant standing in a field", {"elephant"}, ["an elephant in the grass"], SUP, rng)
    assert r["ok"] and r["old_cat"] == "elephant" and r["new_cat"] in {"zebra", "giraffe", "bird", "horse", "bear", "sheep", "cow", "dog", "cat"}
    assert r["negative"].startswith(("A ", "An ")) and "lephant" not in r["negative"]
    r = hardneg.build_one("an animal; an elephant", {"elephant"}, [], SUP, np.random.default_rng(1))
    assert r["ok"] and not r["negative"].endswith("an elephant")
    for seed in range(40):                                                                 # article agrees with the new noun
        r = hardneg.build_one("A dog on a bench", {"dog", "bench"}, [], SUP, np.random.default_rng(seed))
        assert r["ok"] and r["old_cat"] == "dog"                                           # leftmost eligible
        words = r["negative"].split()
        art, noun = words[0], words[1]
        assert art.lower() == ("an" if noun[0] in "aeiou" else "a")
    r = hardneg.build_one("Two dogs on a bench", {"dog", "bench"}, [], SUP, np.random.default_rng(2))
    assert r["ok"] and r["negative"].startswith("Two ") and r["negative"].split()[1] != "dogs"


def test_build_one_never_uses_annotated_or_mentioned_categories_and_skips_person():
    allowed = set()
    for seed in range(300):
        r = hardneg.build_one("An elephant in a field", {"elephant", "zebra"}, ["a giraffe and a bird next to an elephant"], SUP, np.random.default_rng(seed))
        assert r["ok"]
        allowed.add(r["new_cat"])
    assert allowed.isdisjoint({"elephant", "zebra", "giraffe", "bird"}) and allowed >= {"dog", "cat", "horse"}
    assert hardneg.build_one("A man standing", {"person"}, [], SUP, np.random.default_rng(0)) == dict(ok=False, reason="no_same_supercategory_alternative")
    assert hardneg.build_one("A dog standing", {"cat"}, [], SUP, np.random.default_rng(0))["reason"] == "noun_not_annotated"
    assert hardneg.build_one("A quiet room", {"cat"}, [], SUP, np.random.default_rng(0))["reason"] == "no_known_noun"
    r = hardneg.build_one("A dog standing", {"dog"}, [], {}, np.random.default_rng(0))
    assert not r["ok"]                                                                     # unknown supercategories never match each other


def test_build_hard_negatives_counts_skips_and_audit(tmp_path):
    items = [dict(gid=i, idx=i, image_id=i, caption=c) for i, c in enumerate(["An elephant here", "A man there", "A quiet room", "A dog on a bench"])]
    cats = {0: {"elephant"}, 1: {"person"}, 2: {"cat"}, 3: {"dog", "bench"}}
    recs, skipped = hardneg.build_hard_negatives(items, cats, {}, SUP, seed=1)
    assert [r["gid"] for r in recs] == [0, 3] and skipped == Counter(no_same_supercategory_alternative=1, no_known_noun=1)
    hardneg.audit_sheet(recs, tmp_path / "a.jsonl")
    rows = [__import__("json").loads(l) for l in (tmp_path / "a.jsonl").read_text().splitlines()]
    assert set(rows[0]) == {"gid", "image_id", "caption"} and rows[0]["caption"] == recs[0]["negative"]
    res = hardneg.apply_audit(recs, {0: "incorrect", 3: "correct"})
    assert res["n_kept"] == 1 and res["n_judged_correct"] == 1 and res["false_negative_rate"] == 0.5
    lo, hi = res["false_negative_ci95"]
    assert 0.09 < lo < 0.2 and 0.8 < hi < 0.91
    assert hardneg.apply_audit(recs, {})["n_missing"] == 2


def test_wilson_interval():
    lo, hi = hardneg.wilson(0, 100)
    assert lo == 0.0 and 0.03 < hi < 0.04
    assert np.isnan(hardneg.wilson(0, 0)[0])


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
