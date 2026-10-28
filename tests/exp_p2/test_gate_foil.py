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
    assert r["status"] == "tested" and r["tested"] and r["supports_fusion_helps"] and r["p"] < 0.05 and r["test"]["b"] > r["test"]["c"]
    assert r["test"]["acc_a"] > r["test"]["acc_b"] and r["descriptive"]["acc_stouffer_unfitted"] > r["descriptive"]["acc_text_alone"] and "supports" in r["wording"]


def test_fusion_does_not_help_when_one_direction_is_noise():
    fit, test = _margins(240, 0.9, 0.0, seed=7), _margins(300, 0.9, 0.0, seed=8)
    r = foil.fusion_b1(fit, test, n_boot=200)
    assert not r["supports_fusion_helps"] or r["test"]["b"] > r["test"]["c"]            # never true with b <= c
    assert r["best_direction"] == "T" and r["descriptive"]["acc_image_alone"] < 0.6        # the image margin alone is near chance here
    assert abs(r["test"]["delta"]) < 0.1                                                    # fusion neither helps nor hurts much


def test_supports_requires_b_greater_than_c():
    fit = _margins(240, 0.7, 0.7, seed=9)
    r = foil.fusion_b1(fit, _margins(300, 0.7, 0.7, seed=10), n_boot=100)
    assert r["supports_fusion_helps"] is (r["test"]["p"] < 0.05 and r["test"]["b"] > r["test"]["c"])
    # force a significant c > b: test pairs where the image margin carries the sign against the fitted weights
    fw = dict(r["fit"], lda_w=[1.0, -1.0])
    flipped = foil.fusion_b1(None, _margins(300, 0.7, 0.7, seed=11), n_boot=100, frozen_fit=fw)
    assert flipped["test"]["c"] > flipped["test"]["b"] and flipped["supports_fusion_helps"] is False


def test_p_is_one_and_no_test_when_not_estimable_or_at_ceiling():
    r = foil.fusion_b1(_margins(60, 1.0, 0.5), _margins(300, 1.0, 0.5), n_boot=100)
    assert r["status"] == "not_estimable" and r["p"] == 1.0 and r["tested"] is False and "test" not in r and not r["supports_fusion_helps"]
    r = foil.fusion_b1(_margins(240, 3.5, 0.5, seed=1), _margins(300, 3.5, 0.5), n_boot=100)
    assert r["status"] == "untestable_at_ceiling" and r["p"] == 1.0 and "test" not in r


def test_completed_n_below_120_is_descriptive():
    r = foil.fusion_b1(_margins(240, 0.7, 0.7, seed=5), _margins(119, 0.7, 0.7, seed=6), n_boot=100)
    assert r["status"] == "descriptive_n_below_120" and r["descriptive_only"] and r["supports_fusion_helps"] is False and "test" in r
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
    assert res["supports_fusion_helps"] and res["completed_vs_expected"] == [300, 300] and res["refit_matches_frozen"] and not res["partial"] and len(res["limits"]) == 5
    assert json.loads((fam / "analysis.json").read_text())["test"]["b"] == res["test"]["b"]


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
