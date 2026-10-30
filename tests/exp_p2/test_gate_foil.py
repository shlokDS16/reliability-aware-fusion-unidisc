"""Family B (FOIL-COCO hard negatives, SAP AD.6 / AB.6): pair construction, pool, leak check with its positive controls, fusion B1, the CPU analysis and the runner item on the fake network.
Synthetic data throughout; two tests read the real FOIL file and are skipped when it is not in the COCO cache. CPU only; no GPU, no model."""
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from fake_gate import FakeScorer, fake_image                               # noqa: E402
from exp_p2 import common, run_gate_foil                                    # noqa: E402
from exp_p2.gate import analysis_foil, config, foil, runner, stats          # noqa: E402

WORDS = "red blue green small large old new quiet loud bright dark soft hard warm cold fast slow tall short thin wide".split()


# ------------------------------------------------------------------------------------------------ synthetic FOIL file
def synth_foil(image_ids, caps_per_image=2, seed=0):
    """FOIL-shaped dict: for each image `caps_per_image` pairs, original first (capitalised, trailing blank sometimes) then its foil (lower case), same `id`, distinct foil_id."""
    rng = np.random.default_rng(seed)
    anns, cid, fid = [], 1000, 5000
    for img in image_ids:
        for _ in range(caps_per_image):
            w = list(rng.choice(WORDS, 6, replace=False))
            orig = " ".join(w).capitalize() + ". "
            foilw = "pizza"
            foil_cap = " ".join(w[:-1] + [foilw]) + "."
            anns.append(dict(id=cid, foil_id=fid, image_id=int(img), caption=orig, target_word="ORIG", foil_word="ORIG", foil=False))
            anns.append(dict(id=cid, foil_id=fid + 1, image_id=int(img), caption=foil_cap, target_word=w[-1], foil_word=foilw, foil=True))
            cid += 1
            fid += 2
    images = [dict(id=int(i), file_name=f"COCO_val2014_{int(i):012d}.jpg") for i in image_ids]
    return dict(info={}, images=images, annotations=anns, licenses=[])


def synth_folds(ids):
    mk = lambda lst, off: [dict(idx=k, gid=off + k, image_id=int(i)) for k, i in enumerate(lst)]
    return dict(meta=dict(sha1="synthetic"), cal=mk(ids[:30], 0), head=mk(ids[30:50], 1000), test=mk(ids[50:80], 2000), test_ext=mk(ids[80:100], 2300))


# ------------------------------------------------------------------------------------------------ pairs and captions
def test_norm_caption_removes_the_case_leak_and_blanks():
    assert foil.norm_caption("A man  on a Bike. ") == "a man on a bike." == foil.norm_caption("a man on a bike.")


def test_build_pairs_uses_the_shared_id_and_the_first_record_per_image():
    d = synth_foil([11, 12, 13], caps_per_image=3)
    pairs, st = foil.build_pairs(d)
    assert [p["image_id"] for p in pairs] == [11, 12, 13] and st["n_images"] == 3 and st["n_caption_ids"] == 9 and st["n_first_record_is_foil"] == 0
    p = pairs[0]
    assert p["pair_id"] == d["annotations"][0]["id"] and p["c_pos"] == foil.norm_caption(d["annotations"][0]["caption"]) and p["c_neg"] == foil.norm_caption(d["annotations"][1]["caption"])
    assert p["c_pos"] != p["c_neg"] and p["one_word_diff"] and st["n_pairs_one_word_difference"] == 3
    assert p["c_pos"] == p["c_pos"].lower() and p["c_neg"] == p["c_neg"].lower() and not p["c_pos"].endswith(" ")


def test_build_pairs_pairs_a_first_record_that_is_a_foil_with_its_original():
    d = synth_foil([11], caps_per_image=1)
    d["annotations"] = d["annotations"][::-1]                           # the foil comes first in the file
    pairs, st = foil.build_pairs(d)
    assert st["n_first_record_is_foil"] == 1 and pairs[0]["c_pos"] != pairs[0]["c_neg"] and pairs[0]["c_neg"].endswith("pizza.")


def test_build_pairs_rejects_a_file_without_the_pair_key():
    d = synth_foil([11, 12])
    d["annotations"][1]["id"] = 999999                                   # the foil no longer shares the original's id
    with pytest.raises(foil.FoilFormatError):
        foil.build_pairs(d)
    d = synth_foil([11, 12])
    d["annotations"][1]["foil"] = False                                  # two originals under one id
    with pytest.raises(foil.FoilFormatError):
        foil.build_pairs(d)


def test_normalise_image_id_reads_every_documented_format():
    for x in (391895, np.int64(391895), "391895", "000000391895", "COCO_val2014_000000391895.jpg", "val2017/000000391895.jpg", "a\\b\\000000391895.jpg"):
        assert foil.normalise_image_id(x) == 391895
    with pytest.raises(ValueError):
        foil.normalise_image_id("no id here")
    assert foil.coco_member(391895) == "val2017/000000391895.jpg"
    assert foil.check_id_mapping(synth_foil([5, 6]))["n_id_filename_mismatch"] == 0
    bad = synth_foil([5, 6])
    bad["images"][0]["file_name"] = "COCO_val2014_000000000007.jpg"
    assert foil.check_id_mapping(bad)["n_id_filename_mismatch"] == 1


# ------------------------------------------------------------------------------------------------ pool
IDS = [int(x) for x in np.random.default_rng(1).permutation(np.arange(2000, 2400))]


def _pool_inputs():
    foil_d = synth_foil(IDS[:300])                                       # FOIL covers the first 300 ids
    pairs, _ = foil.build_pairs(foil_d)
    folds = synth_folds(IDS)
    probe = set(IDS[100:112])
    val = set(IDS)
    return foil_d, pairs, folds, probe, val


def test_eligible_order_follows_the_fold_order_then_a_seeded_permutation():
    _, pairs, folds, probe, val = _pool_inputs()
    order, counts = foil.eligible_order(pairs, folds, probe, val)
    ids = [p["image_id"] for p in order]
    cal, head = set(IDS[:30]), set(IDS[30:50])
    assert not (set(ids) & cal) and not (set(ids) & head) and not (set(ids) & probe)
    assert ids[:30] == IDS[50:80] and ids[30:50] == IDS[80:100]          # folds test then test_ext, stored order
    assert counts["excluded_by_reason"]["in_calibration_fold"] == 30 and counts["excluded_by_reason"]["in_headroom_fold"] == 20
    assert counts["n_eligible"] == len(ids) == 300 - 30 - 20 - len(probe & set(IDS[:300]))
    rest = sorted(ids[50:])
    assert ids[50:] == [rest[int(j)] for j in np.random.default_rng(foil.SEED_POOL).permutation(len(rest))]
    order2, _ = foil.eligible_order(pairs, folds, probe, val)
    assert [p["image_id"] for p in order2] == ids                        # deterministic
    order3, _ = foil.eligible_order(pairs, folds, probe, val, seed=1)
    assert [p["image_id"] for p in order3][:50] == ids[:50] and [p["image_id"] for p in order3][50:] != ids[50:]


def test_images_outside_val2017_are_not_eligible():
    _, pairs, folds, probe, val = _pool_inputs()
    order, counts = foil.eligible_order(pairs, folds, probe, val - set(IDS[200:300]))
    assert counts["excluded_by_reason"]["not_in_val2017"] == len(set(IDS[200:300]) - probe) or counts["excluded_by_reason"]["not_in_val2017"] == 100
    assert not ({p["image_id"] for p in order} & set(IDS[200:300]))


def test_pool_fit_is_cal_test_is_first_n_and_the_token_rule_marks_without_replacing():
    _, pairs, folds, probe, val = _pool_inputs()
    ntok = lambda c: 3 if "blue" in c.split() else 8                    # captions containing "blue" fall outside 5 to 32
    pool = foil.foil_pool(pairs, folds, probe, val, n_test=60, n_tok_fn=ntok, file_sha="x")
    assert len(pool["test"]) == 60 and [p["idx"] for p in pool["test"]] == list(range(60))
    assert [p["gid"] for p in pool["test"]][:2] == [foil.GID_TEST, foil.GID_TEST + 1] and pool["fit"][0]["gid"] == foil.GID_FIT
    assert [p["image_id"] for p in pool["fit"]] == IDS[:30]               # fit = cal images in cal order
    ex = [p for p in pool["test"] if p["excluded"]]
    assert len(ex) > 0 and all(p["excluded"] in ("pos_out_of_range", "neg_out_of_range", "pos_and_neg_out_of_range") for p in ex)
    pool_all = foil.foil_pool(pairs, folds, probe, val, n_test=60, n_tok_fn=lambda c: 8)
    assert [p["image_id"] for p in pool_all["test"]] == [p["image_id"] for p in pool["test"]]       # exclusion does not change who is in the pool (not replaced)
    assert pool["counts"]["n_test_after_pool_time_token_rule"] == 60 - len(ex)
    assert pool["counts"]["n_test_in_P_test_fold"] == 50 and foil.pool_sha256(pool) != foil.pool_sha256(pool_all)


def test_pool_fit_is_capped_and_only_foil_covered_cal_images_enter():
    foil_d = synth_foil(IDS[10:300])                                     # FOIL misses the first 10 cal images
    pairs, _ = foil.build_pairs(foil_d)
    pool = foil.foil_pool(pairs, synth_folds(IDS), set(), set(IDS), n_test=40, n_fit_max=15)
    assert [p["image_id"] for p in pool["fit"]] == IDS[10:25]


# ------------------------------------------------------------------------------------------------ leak check
def _checked(pool_mod=None, **kw):
    foil_d, pairs, folds, probe, val = _pool_inputs()
    pool = foil.foil_pool(pairs, folds, probe, val, n_test=60, n_tok_fn=lambda c: 8)
    if pool_mod:
        pool_mod(pool)
    return foil.foil_leak_check(pool, folds, probe, foil_images=foil_d["images"], val_ids=val, **kw)


def test_leak_check_passes_on_a_clean_pool_and_logs_the_positive_control():
    log = _checked()
    names = {c["name"]: c for c in log["checks"]}
    assert log["ok"] and all(c["ok"] for c in log["checks"]) and log["counts"]["n_eligible"] > 0
    for n in ("L0_id_mapping_whole_file", "L1_fit_subset_of_cal", "L2_fit_test_disjoint", "L3_test_disjoint_from_cal_head_probe", "L4_no_repeated_image_id", "L5_counts_logged", "L6_matched_ids_positive_control", "L7_hand_check_sample_printed"):
        assert n in names
    assert names["L6_matched_ids_positive_control"]["detail"]["total"] > 0 and all(v > 0 for v in names["L6_matched_ids_positive_control"]["detail"]["counts"].values())
    assert [h["group"] for h in names["L7_hand_check_sample_printed"]["detail"]] == ["cal", "head", "test", "test_ext", "probe"]
    assert "NOT recorded" in log["L7_status"]


@pytest.mark.parametrize("mod,expect", [
    (lambda p: p["test"].append(dict(image_id=IDS[3], idx=99, gid=1)), "L3_test_disjoint_from_cal_head_probe"),           # L8: one id shared with cal
    (lambda p: p["test"].append(dict(image_id=IDS[35], idx=99, gid=1)), "L3_test_disjoint_from_cal_head_probe"),          # head
    (lambda p: p["test"].append(dict(image_id=IDS[100], idx=99, gid=1)), "L3_test_disjoint_from_cal_head_probe"),         # probe
    (lambda p: p["fit"].append(dict(image_id=IDS[150], idx=99, gid=1)), "L1_fit_subset_of_cal"),
    (lambda p: p["test"].append(dict(p["test"][0])), "L4_no_repeated_image_id"),
    (lambda p: p["fit"].append(dict(image_id=p["test"][0]["image_id"], idx=99, gid=1)), "L2_fit_test_disjoint"),
])
def test_leak_check_stops_on_each_injected_leak(mod, expect):
    with pytest.raises(foil.LeakCheckFailed) as e:
        _checked(mod)
    assert expect in [c["name"] for c in e.value.log["checks"] if not c["ok"]]


def test_leak_check_is_vacuous_when_formats_do_not_match_and_stops():
    foil_d, pairs, folds, probe, val = _pool_inputs()
    pool = foil.foil_pool(pairs, folds, probe, val, n_test=60)
    shifted = [dict(id=im["id"] + 10_000_000, file_name=f"COCO_val2014_{im['id'] + 10_000_000:012d}.jpg") for im in foil_d["images"]]   # FOIL ids in a different numbering (e.g. 2014 vs 2017)
    with pytest.raises(foil.LeakCheckFailed) as e:
        foil.foil_leak_check(pool, folds, probe, foil_images=shifted, val_ids=val)
    bad = [c for c in e.value.log["checks"] if not c["ok"]]
    assert any(c["name"] == "L6_matched_ids_positive_control" and c["detail"]["total"] == 0 for c in bad)


def test_leak_check_normalises_zero_padded_names_on_both_sides():
    foil_d, pairs, folds, probe, val = _pool_inputs()
    pool = foil.foil_pool(pairs, folds, probe, val, n_test=60)
    folds2 = json.loads(json.dumps(folds))
    for k in ("cal", "head", "test", "test_ext"):
        for it in folds2[k]:
            it["image_id"] = f"{it['image_id']:012d}"                    # a fold file with zero-padded string ids must still match
    log = foil.foil_leak_check(pool, folds2, {f"{i:012d}" for i in probe}, foil_images=foil_d["images"], val_ids={f"{i:012d}" for i in val})
    assert log["ok"] and log["checks"][-2]["detail"]["total"] > 0


def test_selftest_catches_every_known_bad_case():
    st = foil.selftest()
    assert st["ok"] and st["clean_pool_passes"] and st["all_known_bad_cases_caught"]
    assert "L3_test_disjoint_from_cal_head_probe" in st["L8_known_leak_with_cal_is_caught"] and "L6_matched_ids_positive_control" in st["id_format_mismatch_is_vacuous_and_stops"]


# ------------------------------------------------------------------------------------------------ fusion B1
def _margins(n, shift_T, shift_I, rho=0.0, seed=0):
    rng = np.random.default_rng(seed)
    z = rng.multivariate_normal([0, 0], [[1, rho], [rho, 1]], size=n)
    return z + np.array([shift_T, shift_I])


def test_fit_b1_status_rules():
    assert foil.fit_b1(_margins(99, 1.0, 0.3))["status"] == "not_estimable"                    # (i) fewer than 100 fit pairs
    assert foil.fit_b1(_margins(100, 1.0, 0.3))["status"] == "ok"
    hi = foil.fit_b1(_margins(240, 3.5, 0.3, seed=1))                                         # best direction accuracy >= 0.95: (ii)
    assert hi["best_acc"] >= 0.95 and hi["status"] == "untestable_at_ceiling" and not hi["test_pairs_may_run"]
    ok = foil.fit_b1(_margins(240, 0.8, 0.3, seed=2))
    assert ok["status"] == "ok" and ok["test_pairs_may_run"] and ok["best"] == "T" and len(ok["lda_w"]) == 2 and len(ok["stouffer_w"]) == 2


def test_best_direction_tie_goes_to_text():
    X = np.array([[1.0, 1.0]] * 150 + [[-1.0, -1.0]] * 50)                                    # identical accuracy 0.75 in both directions
    f = foil.fit_b1(X)
    assert f["acc_T"] == f["acc_I"] == 0.75 and f["best"] == "T"
    X2 = np.array([[1.0, 1.0]] * 140 + [[-1.0, 1.0]] * 60)
    assert foil.fit_b1(X2)["best"] == "I"


def test_non_finite_margins_are_dropped_and_counted():
    X = np.vstack([_margins(120, 0.8, 0.3, seed=3), [[np.nan, 1.0], [1.0, np.inf]]])
    assert foil.fit_b1(X)["n_fit"] == 120
    r = foil.fusion_b1(_margins(150, 0.8, 0.3, seed=3), np.vstack([_margins(130, 0.8, 0.3, seed=4), [[np.nan, 0.0]]]), n_boot=200)
    assert r["n_test_completed"] == 130 and r["n_test_dropped_nonfinite"] == 1


def test_fusion_helps_when_the_directions_carry_independent_information():
    fit, test = _margins(240, 0.7, 0.7, seed=5), _margins(300, 0.7, 0.7, seed=6)
    r = foil.fusion_b1(fit, test, n_boot=500)
    assert r["status"] == "tested" and r["tested"] and r["combination_beat_best_single"] and r["p"] < 0.05 and r["test"]["b"] > r["test"]["c"]
    assert r["test"]["acc_a"] > r["test"]["acc_b"] and r["descriptive"]["acc_stouffer_unfitted"] > r["descriptive"]["acc_text_alone"] and r["wording"].startswith("the combination of the two UniDisc scores beat the better single score")


def test_fusion_does_not_help_when_one_direction_is_noise():
    fit, test = _margins(240, 0.9, 0.0, seed=7), _margins(300, 0.9, 0.0, seed=8)
    r = foil.fusion_b1(fit, test, n_boot=200)
    assert not r["combination_beat_best_single"] or r["test"]["b"] > r["test"]["c"]            # never true with b <= c
    assert r["best_direction"] == "T" and r["descriptive"]["acc_image_alone"] < 0.6        # the image margin alone is near chance here
    assert abs(r["test"]["delta"]) < 0.1                                                    # fusion neither helps nor hurts much


def test_supports_requires_b_greater_than_c():
    fit = _margins(240, 0.7, 0.7, seed=9)
    r = foil.fusion_b1(fit, _margins(300, 0.7, 0.7, seed=10), n_boot=100)
    assert r["combination_beat_best_single"] is (r["test"]["p"] < 0.05 and r["test"]["b"] > r["test"]["c"])
    # force a significant c > b: test pairs where the image margin carries the sign against the fitted weights
    fw = dict(r["fit"], lda_w=[1.0, -1.0])
    flipped = foil.fusion_b1(None, _margins(300, 0.7, 0.7, seed=11), n_boot=100, frozen_fit=fw)
    assert flipped["test"]["c"] > flipped["test"]["b"] and flipped["combination_beat_best_single"] is False


def test_p_is_one_and_no_test_when_not_estimable_or_at_ceiling():
    r = foil.fusion_b1(_margins(60, 1.0, 0.5), _margins(300, 1.0, 0.5), n_boot=100)
    assert r["status"] == "not_estimable" and r["p"] == 1.0 and r["tested"] is False and "test" not in r and not r["combination_beat_best_single"]
    r = foil.fusion_b1(_margins(240, 3.5, 0.5, seed=1), _margins(300, 3.5, 0.5), n_boot=100)
    assert r["status"] == "untestable_at_ceiling" and r["p"] == 1.0 and "test" not in r


def test_completed_n_below_120_is_descriptive():
    r = foil.fusion_b1(_margins(240, 0.7, 0.7, seed=5), _margins(119, 0.7, 0.7, seed=6), n_boot=100)
    assert r["status"] == "descriptive_n_below_120" and r["descriptive_only"] and r["combination_beat_best_single"] is False and "test" in r
    assert foil.fusion_b1(_margins(240, 0.7, 0.7, seed=5), _margins(120, 0.7, 0.7, seed=6), n_boot=100)["status"] == "tested"


def test_frozen_weights_are_used_and_a_refit_check_is_recorded():
    fit = _margins(240, 0.7, 0.7, seed=5)
    frozen = foil.fit_b1(fit)
    r = foil.fusion_b1(fit, _margins(200, 0.7, 0.7, seed=6), n_boot=100, frozen_fit=frozen)
    assert r["weights_source"] == "fusion_frozen.json" and r["refit_matches_frozen"] is True
    r2 = foil.fusion_b1(_margins(240, 0.2, 0.9, seed=12), _margins(200, 0.7, 0.7, seed=6), n_boot=100, frozen_fit=frozen)
    assert r2["refit_matches_frozen"] is False and r2["fit"]["lda_w"] == frozen["lda_w"]      # the committed weights decide, the refit is only a record


def test_exact_mcnemar_size_at_n_150_is_at_most_nominal():
    """Under H0 (a discordant pair favours either arm with probability 1/2) the exact two-sided McNemar test rejects at most 5 percent at n = 150."""
    rng = np.random.default_rng(0)
    rej = 0
    for _ in range(3000):
        n_d = int(rng.binomial(150, 0.15))
        b = int(rng.binomial(n_d, 0.5))
        y_a = np.r_[np.ones(b), np.zeros(n_d - b), np.zeros(150 - n_d)]
        y_b = np.r_[np.zeros(b), np.ones(n_d - b), np.zeros(150 - n_d)]
        rej += stats.mcnemar_exact(y_a, y_b)["p"] < 0.05
    assert rej / 3000 <= 0.05 + 3 * np.sqrt(0.05 * 0.95 / 3000)


# ------------------------------------------------------------------------------------------------ git rule (iii)
def test_require_committed(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True)
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    f = repo / "fusion_frozen.json"
    f.write_text("{}")
    with pytest.raises(RuntimeError, match="not tracked"):
        foil.require_committed(f, repo)
    run("add", "fusion_frozen.json")
    run("commit", "-q", "-m", "x")
    foil.require_committed(f, repo)
    f.write_text('{"a": 1}')
    with pytest.raises(RuntimeError, match="uncommitted"):
        foil.require_committed(f, repo)
    with pytest.raises(FileNotFoundError):
        foil.require_committed(repo / "missing.json", repo)


# ------------------------------------------------------------------------------------------------ CPU analysis on synthetic run directories
def _write_rows(d, X, pair0=100):
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "items.jsonl", "w") as fh:
        for i, (t, im) in enumerate(X):
            fh.write(json.dumps(dict(idx=i, pair_id=pair0 + i, gid=i, image_id=i, T=float(t), I=float(im), seconds=1.0)) + "\n")
    (d / "token_exclusions.json").write_text(json.dumps(dict(n_planned=len(X), n_excluded=0, by_reason={})))


@pytest.fixture
def foil_env(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    pool = dict(meta={}, counts={}, fit=[dict(image_id=1, pair_id=1, c_pos="a", c_neg="b", idx=0, gid=0, excluded=None)], test=[])
    (tmp_path / foil.FOIL_RUN_ID).mkdir()
    (tmp_path / foil.FOIL_RUN_ID / "pool.json").write_text(json.dumps(pool))
    return tmp_path


def test_freeze_then_analyze_end_to_end(foil_env):
    fam = foil_env / foil.FOIL_RUN_ID
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(240, 0.7, 0.7, seed=5))
    p = analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    assert p["fit"]["status"] == "ok" and p["n_rows"] == 240 and len(p["sha256_of_fit_run_rows"]) == 64
    with pytest.raises(Exception):                                                   # write-once
        analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    _write_rows(foil_env / foil.TEST_RUN_ID, _margins(300, 0.7, 0.7, seed=6), pair0=5000)
    res = analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", foil_env / foil.FIT_RUN_ID, fam / "analysis.json", n_boot=200, check_commit=False)
    assert res["combination_beat_best_single"] and res["completed_vs_expected"] == [300, 300] and res["refit_matches_frozen"] and not res["partial"] and res["limits"] == foil.B_LIMITS
    assert json.loads((fam / "analysis.json").read_text())["test"]["b"] == res["test"]["b"]


def test_freeze_and_analyze_refuse_an_empty_or_unstarted_run(foil_env):
    fam = foil_env / foil.FOIL_RUN_ID
    with pytest.raises(FileNotFoundError):
        analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")          # no run directory at all: nothing may be frozen
    assert not (fam / "fusion_frozen.json").exists()
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(240, 0.7, 0.7, seed=5))
    (foil_env / foil.FIT_RUN_ID / "token_exclusions.json").unlink()
    with pytest.raises(analysis_foil.PartialRun):                                             # planned n unknown: refused unless --allow-partial
        analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    assert not (fam / "fusion_frozen.json").exists()
    with pytest.raises(FileNotFoundError):
        analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", None, fam / "a.json", check_commit=False)


def test_analysis_refuses_a_partial_fold_and_freeze_refuses_a_partial_fit(foil_env):
    fam = foil_env / foil.FOIL_RUN_ID
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(240, 0.7, 0.7, seed=5))
    (foil_env / foil.FIT_RUN_ID / "token_exclusions.json").write_text(json.dumps(dict(n_planned=300, n_excluded=0)))        # 240 of 300 done
    with pytest.raises(analysis_foil.PartialRun):
        analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    p = analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json", allow_partial=True)
    assert p["allow_partial"] is True and p["expected_rows"] == 300
    _write_rows(foil_env / foil.TEST_RUN_ID, _margins(200, 0.7, 0.7, seed=6))
    (foil_env / foil.TEST_RUN_ID / "token_exclusions.json").write_text(json.dumps(dict(n_planned=300, n_excluded=4)))        # expects 296
    with pytest.raises(analysis_foil.PartialRun):
        analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", None, fam / "a.json", n_boot=100, check_commit=False)
    res = analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", None, fam / "a.json", allow_partial=True, n_boot=100, check_commit=False)
    assert res["partial"] and res["completed_vs_expected"] == [200, 296]


def test_analysis_with_a_status_that_forbids_the_test_returns_p_one(foil_env):
    fam = foil_env / foil.FOIL_RUN_ID
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(60, 0.7, 0.7, seed=5))
    p = analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    assert p["fit"]["status"] == "not_estimable" and p["fit"]["test_pairs_may_run"] is False
    _write_rows(foil_env / foil.TEST_RUN_ID, _margins(5, 0.7, 0.7))
    res = analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", None, fam / "a.json", n_boot=50, check_commit=False)
    assert res["p"] == 1.0 and res["tested"] is False


def test_runner_refuses_the_test_stage_without_a_committed_ok_freeze(foil_env, monkeypatch):
    monkeypatch.setattr(foil, "verify_file", lambda *a, **k: {})
    monkeypatch.setattr(foil, "check_pool", lambda pool=None, inp=None: dict(pool_sha256="x"))
    monkeypatch.setattr(foil, "require_committed", lambda p, repo=foil.ROOT: None)
    fam = foil_env / foil.FOIL_RUN_ID
    with pytest.raises(FileNotFoundError):
        run_gate_foil.check_prereqs("test")                                            # no fusion_frozen.json yet
    (fam / "fusion_frozen.json").write_text(json.dumps(dict(fit=dict(status="untestable_at_ceiling"))))
    with pytest.raises(RuntimeError, match="untestable_at_ceiling"):
        run_gate_foil.check_prereqs("test")
    (fam / "fusion_frozen.json").write_text(json.dumps(dict(fit=dict(status="ok"), sha256_of_fit_run_rows="abc")))
    assert run_gate_foil.check_prereqs("test")["fusion_frozen"] == "abc" and run_gate_foil.check_prereqs("fit")["leak_check"] == "passed"
    monkeypatch.setattr(foil, "require_committed", lambda p, repo=foil.ROOT: (_ for _ in ()).throw(RuntimeError("not tracked")))
    with pytest.raises(RuntimeError, match="not tracked"):
        run_gate_foil.check_prereqs("fit")


# ------------------------------------------------------------------------------------------------ the GPU runner's item on the fake network
@pytest.fixture
def renv(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "_cuda", lambda: None)
    monkeypatch.setattr(common, "load_image", lambda iid: fake_image(iid, 96))

    def init_run(run_id, config_):
        d = tmp_path / run_id
        d.mkdir(parents=True, exist_ok=True)
        if not (d / "config.json").exists():
            (d / "config.json").write_text(json.dumps(dict(config_, run_id=run_id)))
        return d
    monkeypatch.setattr(common, "init_run", init_run)
    return tmp_path


def _items(n):
    rng = np.random.default_rng(3)
    out = []
    for i in range(n):
        w = list(rng.choice(WORDS, 6, replace=False))
        out.append(dict(idx=i, gid=foil.GID_TEST + i, image_id=300 + i, caption=" ".join(w), neg_caption=" ".join(w[:-1] + ["pizza"]), pair_id=i, pool_excluded=None))
    return out


def test_runner_item_has_four_passes_and_the_margins(renv):
    sc = runner.Counting(FakeScorer(grid=4))
    (renv / "P2-GATE-FOILx").mkdir()
    ctx = run_gate_foil.make_ctx(sc, renv / "P2-GATE-FOILx")
    items = _items(3)
    run_gate_foil.process(sc, items[0], ctx)                                           # warms the null caches
    r0 = sc.rows
    row, arrays = run_gate_foil.process(sc, items[1], ctx)
    assert sc.rows - r0 == 4                                                           # image direction 2 + text direction 2; nothing gated, nothing corrupted
    assert set(arrays) == {"delta", "codes"} and arrays["delta"].shape == (16,)
    assert row["T"] == row["txt"]["d"] and row["I"] == row["img"]["mean"] == pytest.approx(float(arrays["delta"].mean()), rel=1e-5) and np.isfinite(row["T"]) and np.isfinite(row["I"])
    row2, _ = run_gate_foil.process(sc, items[1], ctx)
    assert row2["T"] == row["T"] and row2["I"] == row["I"]                             # deterministic


def test_runner_loop_resumes_and_writes_rows(renv):
    sc = runner.Counting(FakeScorer(grid=4))
    items = _items(4)
    kw = dict(run_id="P2-GATE-FOIL-FITx", cfg=dict(run_gate_foil.CONFIG, n_items=4), load=lambda: sc, get_items=lambda s, r: items, process=run_gate_foil.process, make_ctx=run_gate_foil.make_ctx,
              duty=1.0, soft_minutes=30)
    assert runner.run_items(limit=2, **kw) == runner.EXIT_MORE_WORK
    assert runner.run_items(**kw) == runner.EXIT_DONE
    rows = common.read_jsonl(renv / "P2-GATE-FOIL-FITx" / "items.jsonl")
    assert [r["idx"] for r in rows] == [0, 1, 2, 3] and all("T" in r and "I" in r and "seconds" in r for r in rows)
    assert len(list((renv / "P2-GATE-FOIL-FITx" / "arrays").glob("item*.npz"))) == 4


def test_runtime_token_rule_excludes_without_replacement(renv, monkeypatch):
    pool = dict(fit=[], test=[dict(idx=i, gid=foil.GID_TEST + i, image_id=300 + i, c_pos=p["caption"], c_neg=p["neg_caption"], pair_id=i, excluded=None) for i, p in enumerate(_items(6))])
    monkeypatch.setattr(foil, "load_pool", lambda path=None: pool)
    sc = FakeScorer(grid=4)
    sc.caption_ids = lambda c: [1] * (3 if c.startswith(WORDS[0]) or "wide" in c else 8)       # some captions get 3 tokens (outside 5 to 32)
    run = renv / "r"
    keep = run_gate_foil.get_items_factory("test", None)(sc, run)
    ex = json.loads((run / "token_exclusions.json").read_text())
    assert ex["n_planned"] == 6 and ex["n_excluded"] == 6 - len(keep) and [it["idx"] for it in keep] == sorted(it["idx"] for it in keep)
    assert all(it["n_tok_pos"] >= 5 for it in keep)
    assert analysis_foil.expected_n(run) == len(keep)


# ------------------------------------------------------------------------------------------------ the real file (skipped when it is not in the COCO cache)
real = pytest.mark.skipif(not foil.foil_path().exists(), reason="FOIL test file not in the COCO cache")


@real
def test_real_file_hash_and_pair_key():
    assert foil.verify_file()["sha256"] == foil.FOIL_SHA256
    d = foil.load_foil()
    pairs, st = foil.build_pairs(d)
    assert st["n_records"] == 198960 and st["n_caption_ids"] == 99480 and st["n_images"] == 32150 and st["n_first_record_is_foil"] == 0
    assert st["n_identical_after_normalisation"] == 0 and st["n_pairs_one_word_difference"] > 0.99 * 32150
    assert foil.check_id_mapping(d)["n_id_filename_mismatch"] == 0
    assert all(p["c_pos"] == p["c_pos"].lower() and p["c_neg"] == p["c_neg"].lower() for p in pairs[:2000])


@real
def test_real_pool_is_reproducible_from_the_committed_inputs():
    pp = Path(common.RUNS) / foil.FOIL_RUN_ID / "pool.json"
    if not pp.exists():
        pytest.skip("pool.json not built")
    committed = json.loads(pp.read_text(encoding="utf8"))
    d = foil.load_foil()
    pairs, _ = foil.build_pairs(d)
    from exp_p2.gate import data, folds as folds_mod
    f = json.loads(folds_mod.folds_path().read_text(encoding="utf8"))
    pool = foil.foil_pool(pairs, f, data.probe_image_ids(), set(common.load_captions()), n_test=committed["meta"]["n_test_planned"], file_sha=foil.FOIL_SHA256)
    assert [p["image_id"] for p in pool["test"]] == [p["image_id"] for p in committed["test"]]
    assert [p["image_id"] for p in pool["fit"]] == [p["image_id"] for p in committed["fit"]]
    assert [(p["c_pos"], p["c_neg"]) for p in pool["test"]] == [(p["c_pos"], p["c_neg"]) for p in committed["test"]]


# ------------------------------------------------------------------------------------------------ audit fixes (GATE-CODE-AUDIT-A3-PART2): M2, M3, M4, m7, m8
def test_m3_analyze_handles_untestable_at_ceiling_with_no_test_rows(foil_env):
    """The auditor's failure: after the runner refuses the test stage there are no test rows, and analyze raised FileNotFoundError before writing the p = 1 record."""
    fam = foil_env / foil.FOIL_RUN_ID
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(240, 3.5, 0.3, seed=1))
    p = analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    assert p["fit"]["status"] == "untestable_at_ceiling"
    assert not (foil_env / foil.TEST_RUN_ID).exists()                                                    # the runner never ran the test stage
    res = analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", foil_env / foil.FIT_RUN_ID, fam / "analysis.json", n_boot=50, check_commit=False)
    assert res["status"] == "untestable_at_ceiling" and res["p"] == 1.0 and res["tested"] is False and "test" not in res
    assert res["wording"] == "the best single direction met the preregistered ceiling on the fit pairs; text-only cues are not excluded as a cause"
    on_disk = json.loads((fam / "analysis.json").read_text())
    assert on_disk["p"] == 1.0 and on_disk["wording"] == res["wording"] and on_disk["limits"] and on_disk["label"]


def test_m3_analyze_handles_not_estimable_with_no_test_rows(foil_env):
    fam = foil_env / foil.FOIL_RUN_ID
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(60, 0.7, 0.7, seed=5))
    analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    res = analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", None, fam / "analysis.json", n_boot=50, check_commit=False)
    assert res["status"] == "not_estimable" and res["p"] == 1.0 and not res["tested"] and "not estimable" in res["wording"] and "100" in res["wording"]
    assert "fusion" not in res["wording"]


def test_m3_test_rows_under_a_non_ok_status_are_ignored_and_flagged(foil_env):
    fam = foil_env / foil.FOIL_RUN_ID
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(240, 3.5, 0.3, seed=1))
    analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    _write_rows(foil_env / foil.TEST_RUN_ID, _margins(5, 0.7, 0.7))
    res = analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", None, fam / "analysis.json", n_boot=50, check_commit=False)
    assert res["p"] == 1.0 and "test" not in res and res["unexpected_test_rows_ignored"] == 5


def test_m4_no_sentence_says_that_foil_tests_shows_or_supports_fusion():
    fit, test = _margins(240, 0.7, 0.7, seed=5), _margins(300, 0.7, 0.7, seed=6)
    r = foil.fusion_b1(fit, test, n_boot=300, n_planned=298)
    assert r["tested"] and r["combination_beat_best_single"] and "supports_fusion_helps" not in r
    w = r["wording"]
    assert w.startswith("the combination of the two UniDisc scores beat the better single score on these FOIL pairs; part of the gain may come from text-only cues; no text-only baseline was run")
    assert "ball to racket 11 of 300 test against 1 of 240 fit" in w and "a/an 15 of 300 against 7 of 240" in w
    assert "the combination weights were fitted on the same negative type but not the same mix of negatives" in w
    for bad in ("supports", "shows", "tests fusion", "fusion helps"):
        assert bad not in w


def test_m4_non_rejecting_sentence_carries_the_mde_and_no_fusion_sentence():
    from exp_p2.gate import mde
    fit, test = _margins(240, 0.9, 0.0, seed=7), _margins(238, 0.9, 0.0, seed=8)
    r = foil.fusion_b1(fit, test, n_boot=200, n_planned=238)
    assert not r["combination_beat_best_single"]
    assert r["wording"].startswith("the combination did not beat the better single score; minimum detectable net gain at the achieved n = 238 is ")
    assert mde.mde_sentence(238, 0.05) in r["wording"] and "fusion" not in r["wording"] and "supports" not in r["wording"]
    assert r["mde_at_achieved_n"]["by_pi_d"] == mde.mde_table(238, 0.05)["by_pi_d"]
    d = foil.fusion_b1(fit, _margins(100, 0.9, 0.0, seed=8), n_boot=100)
    assert d["descriptive_only"] and d["wording"].startswith("completed n 100 is below 120: descriptive only, no test statement; minimum detectable net gain")


def test_m4_limits_carry_the_text_only_cue_mix_label_noise_and_cap_statements(foil_env):
    fam = foil_env / foil.FOIL_RUN_ID
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(240, 0.7, 0.7, seed=5))
    analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    _write_rows(foil_env / foil.TEST_RUN_ID, _margins(300, 0.7, 0.7, seed=6), pair0=5000)
    res = analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", None, fam / "analysis.json", n_boot=100, check_commit=False)
    blob = " ".join(res["limits"])
    for need in ("text-only cues", "no text-only baseline was run", "ball to racket 11 of 300 test against 1 of 240 fit", "a/an 15 of 300 against 7 of 240",
                 "26 of 300 test pairs (8.7 percent) are flagged", "this is a flag rate, not an error rate and not a bound", "12 of 300 (4.0 percent; 5 plausibly true, 7 ambiguous)",
                 "other 14 of the 26", "33 of 240 fit pairs", "not bounded by these data", "no judgement exists for the 240 fit pairs", "attainable net gain is at most 1 minus the better single accuracy minus the label-noise share",
                 "does not include this cap", "sign of any bias on Delta_B is not established"):
        assert need in blob, need
    assert "up to" not in blob and "supports 'fusion helps'" not in blob and "plausibly lowers" not in blob
    acc_best = res["descriptive"]["acc_text_alone"] if res["best_direction"] == "T" else res["descriptive"]["acc_image_alone"]
    assert res["max_net_gain_before_label_noise"] == pytest.approx(1 - acc_best)


def test_the_caveat_numbers_match_the_committed_artifacts():
    pool_p = ROOT / "runs" / "P2-GATE-FOIL" / "pool.json"
    l7_p = ROOT / "runs" / "P2-GATE-FOIL-L7" / "l7_out.json"
    if not (pool_p.exists() and l7_p.exists()):
        pytest.skip("committed FOIL artifacts not present")
    n = foil.caveat_numbers_from_artifacts(json.loads(pool_p.read_text(encoding="utf8")))
    assert (n["ball_to_racket_test"], n["n_test"], n["ball_to_racket_fit"], n["n_fit"]) == (11, 300, 1, 240) and "11 of 300 test against 1 of 240 fit" in foil.MIX_SENTENCE
    o = json.loads(l7_p.read_text(encoding="utf8"))["out"]
    assert (o["test"]["foil_cat_present"], o["test"]["n"], o["fit"]["foil_cat_present"], o["fit"]["n"]) == (26, 300, 18, 240)
    assert (len(o["test"]["target_mapped_but_absent"]), len(o["fit"]["target_mapped_but_absent"])) == (26, 33)
    blob = " ".join(foil.LABEL_NOISE_STATEMENTS)
    assert "26 of 300" in blob and "18 of 240" in blob and "33 of 240" in blob and "12 of 300" in blob


def test_m2_b_sensitivity_is_the_first_150_pool_positions_and_labelled():
    fit = _margins(240, 0.7, 0.7, seed=5)
    X = _margins(298, 0.7, 0.7, seed=6)
    idx = np.arange(298) + 2                                                      # pool positions 0 and 1 and a few more were excluded by the token rule
    r = foil.fusion_b1(fit, X, n_boot=100, n_planned=298, pool_idx=idx)
    s = r["sensitivity_first150_pool_positions"]
    assert s["exists"] and s["label"] == "sensitivity (first 150 pool positions), not confirmatory, not in the Holm set" and s["n_completed_in_prefix"] == 148 and s["tested"]
    w = np.array(r["fit"]["lda_w"])
    top = foil.report.report_test((X[:148] @ w > 0).astype(float), (X[:148, 0 if r["fit"]["best"] == "T" else 1] > 0).astype(float), n_boot=50, seed=1)
    assert (s["b"], s["c"]) == (top["b"], top["c"]) and s["p"] == pytest.approx(top["p"])
    assert s["primary_rejects"] is r["combination_beat_best_single"]


def test_m2_b_sensitivity_coincides_with_the_primary_when_fewer_than_150_positions_are_covered():
    fit = _margins(240, 0.7, 0.7, seed=5)
    r = foil.fusion_b1(fit, _margins(140, 0.7, 0.7, seed=6), n_boot=100, n_planned=298, pool_idx=np.arange(140))
    s = r["sensitivity_first150_pool_positions"]
    assert not s["exists"] and "coincides with the primary" in s["reason"]
    d = foil.fusion_b1(fit, _margins(100, 0.7, 0.7, seed=6), n_boot=100, n_planned=298, pool_idx=np.arange(100))
    assert d["descriptive_only"] and not d["sensitivity_first150_pool_positions"]["exists"]


def test_m2_b_sensitivity_reports_sensitivity_to_n():
    y_best = np.r_[np.ones(150), np.zeros(148)]
    y_fus = np.r_[np.ones(150), np.ones(30), np.zeros(118)]                         # b = c = 0 in the first 150 positions; b = 30, c = 0 beyond them
    pos = np.arange(298)
    s = foil._sensitivity_first150(y_fus, y_best, pos, True, True, 100, 1)
    assert s["exists"] and s["n_completed_in_prefix"] == 150 and (s["b"], s["c"]) == (0, 0) and not s["sens_rejects"] and s["primary_rejects"] and s["sensitive_to_n"]
    assert "sensitive to n" in s["statement"] and "opposite sides of rejection" in s["statement"]
    agree = foil._sensitivity_first150(np.r_[np.ones(30), np.zeros(268)], np.zeros(298), pos, True, True, 100, 1)          # b = 30, c = 0 inside the first 150 positions
    assert agree["sens_rejects"] and not agree["sensitive_to_n"] and "statement" not in agree
    assert not foil._sensitivity_first150(y_fus, y_best, pos, False, False, 100, 1)["exists"] and not foil._sensitivity_first150(y_fus, y_best, None, True, True, 100, 1)["exists"]


def test_m2_b_partial_prefix_label_and_mde():
    from exp_p2.gate import mde
    fit = _margins(240, 0.7, 0.7, seed=5)
    r = foil.fusion_b1(fit, _margins(200, 0.7, 0.7, seed=6), n_boot=100, n_planned=298, pool_idx=np.arange(200))
    pp = r["partial_prefix"]
    assert pp["label"] == "partial prefix (under 80 percent of plan)" and pp["completed_n"] == 200 and pp["mde"]["by_pi_d"] == mde.mde_table(200, 0.05)["by_pi_d"] and "not described as an n = 300 result" in pp["note"]
    assert foil.fusion_b1(fit, _margins(240, 0.7, 0.7, seed=6), n_boot=100, n_planned=298, pool_idx=np.arange(240))["partial_prefix"] is None
    assert foil.fusion_b1(fit, _margins(298, 0.7, 0.7, seed=6), n_boot=100, n_planned=298, pool_idx=np.arange(298))["partial_prefix"] is None
    assert foil.fusion_b1(fit, _margins(130, 0.7, 0.7, seed=6), n_boot=100, n_planned=130, pool_idx=np.arange(130))["partial_prefix"] is None        # the planned fold is complete


def test_m7_analyze_refuses_a_pool_that_differs_from_the_frozen_one(foil_env):
    fam = foil_env / foil.FOIL_RUN_ID
    _write_rows(foil_env / foil.FIT_RUN_ID, _margins(240, 0.7, 0.7, seed=5))
    analysis_foil.freeze(foil_env / foil.FIT_RUN_ID, fam / "fusion_frozen.json")
    _write_rows(foil_env / foil.TEST_RUN_ID, _margins(300, 0.7, 0.7, seed=6), pair0=5000)
    pool = json.loads((fam / "pool.json").read_text())
    pool["fit"][0]["c_pos"] = "changed"
    (fam / "pool.json").write_text(json.dumps(pool))
    with pytest.raises(RuntimeError, match="pool"):
        analysis_foil.analyze(foil_env / foil.TEST_RUN_ID, fam / "fusion_frozen.json", None, fam / "analysis.json", n_boot=50, check_commit=False)


def test_m7_the_runner_writes_its_leak_check_into_the_run_dir_and_never_rewrites_the_committed_one(foil_env, monkeypatch):
    fam = foil_env / foil.FOIL_RUN_ID
    committed = dict(ok=True, pool_sha256="x", counts={"a": 1}, created="2026-10-28T13:50:02", test_images_also_in_P_test_fold=300, checks=[dict(name="L1", ok=True, detail="d1")])
    (fam / "leak_check.json").write_text(json.dumps(committed))
    before = (fam / "leak_check.json").read_text()
    monkeypatch.setattr(foil, "verify_file", lambda *a, **k: {})
    monkeypatch.setattr(foil, "require_committed", lambda p, repo=foil.ROOT: None)
    rerun = dict(committed, created="2026-10-29T09:00:00", checks=[dict(name="L1", ok=True, detail="other detail")])            # only timestamp and detail differ
    monkeypatch.setattr(foil, "check_pool", lambda pool=None, inp=None: rerun)
    info = run_gate_foil.check_prereqs("fit")
    assert info["leak_check_matches_committed"] is True and (fam / "leak_check.json").read_text() == before
    assert json.loads((foil_env / foil.FIT_RUN_ID / "leak_check.json").read_text())["created"] == "2026-10-29T09:00:00"
    monkeypatch.setattr(foil, "check_pool", lambda pool=None, inp=None: dict(rerun, counts={"a": 2}))
    with pytest.raises(RuntimeError, match="differs from the committed"):
        run_gate_foil.check_prereqs("fit")
    assert (fam / "leak_check.json").read_text() == before


def test_m8_constant_margins_do_not_put_nan_into_the_frozen_record():
    X = np.array([[1.0, 2.0]] * 120)                                              # constant columns: the correlation is 0/0
    f = foil.fit_b1(X)
    assert f["stouffer_r"] is None and f["corr_T_I"] is None and f["status"] in ("ok", "untestable_at_ceiling")
    assert "NaN" not in json.dumps(f, allow_nan=True)
