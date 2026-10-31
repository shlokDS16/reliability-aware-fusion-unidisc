"""Flickr30K transfer test (SAP addendum A7): the fold builder exp_p2/gate/build_f30k_fold.py, the entry point exp_p2/run_gate_lrf_f30k.py, the lrf-f30k driver stage and the analysis script. CPU only,
fake network, temp directories; nothing is launched, no real image or array is read (except the optional check of the committed family file)."""
import csv
import hashlib
import io
import json
import math
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fake_gate import fake_image                                                     # noqa: E402
from test_gate_runners_fake import _fold, _m4_prereqs, _sc, _write_folds             # noqa: E402  (helpers only)
from exp_p2 import common, run_gate_lrf_f30k as f30k, run_gate_m4 as m4              # noqa: E402
from exp_p2.gate import build_f30k_fold as bf, corruptions, gate_driver, pipeline, runner     # noqa: E402
from analysis.paper2.lrf import f30k_analysis as FA                                   # noqa: E402

FAM = [("noise", 0.1)]
GOOD = ["--run-id", "P2-LRF-F30K", "--folds-path", str(ROOT / "runs" / "P2-LRF-F30K-FOLD" / "folds_f30k.json"), "--family-run", "P2-LRF-PLAN-F30K", "--sanity", "", "--denoise-for", "", "--tbv", "on",
        "--layout-fix", "13", "--neg-len"]


# ------------------------------------------------------------------------------------------------ the entry point
@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "_cuda", lambda: None)
    monkeypatch.setattr(common, "load_image", lambda iid: fake_image(iid, 96))
    return tmp_path


def _images(tmp_path, ids):
    d = tmp_path / "imgs"
    d.mkdir(exist_ok=True)
    h = {}
    for iid in ids:
        fake_image(iid + 5000, 96).save(d / f"{iid}.jpg", "PNG")                    # PNG bytes under a .jpg name: lossless, the loader only decodes
        h[f"{iid}.jpg"] = hashlib.sha256((d / f"{iid}.jpg").read_bytes()).hexdigest()
    return d, h


def _ctx(env, sc, n=3):
    _m4_prereqs(env, sc, FAM)
    items = _fold(n, offset=0)
    for it in items:
        it["gid"] = bf.GID_OFFSET + it["idx"]
    for i, it in enumerate(items):
        it["neg_caption_len"] = items[(i + 2) % n]["caption"]
    _write_folds(env, test=items)
    a = SimpleNamespace(tbv="on", denoise_for="", sanity="", neg_len=True, caption_slot_len=f30k.L_FIX)
    (env / "P2-LRF-F30K").mkdir(exist_ok=True)
    return items, m4.make_ctx_factory(a, env)(sc, env / "P2-LRF-F30K")


def test_unchanged_pinned_runner():
    pins = json.loads((ROOT / "runs" / "P2-LRF-PINS" / "pins.json").read_text(encoding="utf8"))
    for rel in ("exp_p2/run_gate_m4.py", "exp_p2/gate/lrf_score.py", "exp_p2/run_gate_lrf_rescore.py"):
        assert hashlib.sha256((ROOT / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == pins["entry_points"][rel], rel


def test_loader_reads_the_local_folder_and_checks_the_manifest(tmp_path):
    d, h = _images(tmp_path, [11, 12])
    ld = f30k.make_loader(d, h)
    assert ld(11).size == (96, 96) and ld(11).mode == "RGB"
    with pytest.raises(KeyError):
        ld(99)
    bad = dict(h, **{"12.jpg": "0" * 64})
    with pytest.raises(ValueError):
        f30k.make_loader(d, bad)(12)


def test_swap_is_restored_after_normal_exit_and_after_an_error(env, tmp_path):
    d, h = _images(tmp_path, [1])
    orig = (common.load_image, runner.run_items)
    ld = f30k.make_loader(d, h)
    with f30k.f30k_patched(ld, {}):
        assert common.load_image is ld and runner.run_items is not orig[1]
    assert (common.load_image, runner.run_items) == orig
    with pytest.raises(RuntimeError):
        with f30k.f30k_patched(ld, {}):
            raise RuntimeError("boom")
    assert (common.load_image, runner.run_items) == orig


def test_nothing_else_is_patched(env, tmp_path):
    d, h = _images(tmp_path, [1])
    before = (m4.build_conditions, m4.process, m4.make_ctx_factory, m4.main)
    with f30k.f30k_patched(f30k.make_loader(d, h), {}):
        assert before == (m4.build_conditions, m4.process, m4.make_ctx_factory, m4.main)


def test_run_config_records_dataset_and_image_folder(monkeypatch, tmp_path):
    seen = {}
    monkeypatch.setattr(runner, "run_items", lambda **kw: seen.update(kw) or 0)
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps(dict(image_sha256={})), encoding="utf8")
    rec = f30k.f30k_record(tmp_path / "imgs", man)
    d, h = _images(tmp_path, [1])
    with f30k.f30k_patched(f30k.make_loader(d, h), rec):
        runner.run_items(cfg={"stage": "M4"}, process=m4.process)
    c = seen["cfg"]
    assert c["stage"] == "M4" and "Flickr30K" in c["dataset"] and c["image_dir"] == str(tmp_path / "imgs") and c["conditions"] == ["clean", "noise0.1"]
    assert c["image_manifest_sha256"] == hashlib.sha256(man.read_bytes()).hexdigest() and c["dataset_revision"] == bf.HF_REVISION


def test_an_item_has_exactly_clean_and_noise01_and_reads_flickr_images(env, tmp_path):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    d, h = _images(tmp_path, [it["image_id"] for it in items])
    with f30k.f30k_patched(f30k.make_loader(d, h), {}):
        m4.process(sc, items[1], ctx)                                              # warm
        row, arr = m4.process(sc, items[1], ctx)
        pil, codes = pipeline.prep_image(sc, items[1]["image_id"])
    assert set(row["conds"]) == {"clean", "noise0.1"} and row["slot_len"] == 13
    assert not any("_dn" in k or k.startswith(("patch", "swap")) for k in arr)
    for name in ("clean", "noise0.1"):
        for key in ("B", "D", "s3", "tbv", "tex", "nbr", "delta", "deltaL", "flag0.05", "codes", "z"):
            assert f"{name}_{key}" in arr, (name, key)
    from PIL import Image
    want = sc.preprocess(Image.open(d / f"{items[1]['image_id']}.jpg").convert("RGB"))
    assert np.array_equal(np.asarray(pil), np.asarray(want)) and np.array_equal(codes, arr["clean_codes"])      # the Flickr file, not the COCO fake
    assert row["conds"]["noise0.1"]["kind"] == "pixel" and "imgL" in row["conds"]["noise0.1"]


def test_noise_stream_is_the_l1_call_with_the_new_gid(env, tmp_path):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    d, h = _images(tmp_path, [it["image_id"] for it in items])
    it = items[0]
    assert it["gid"] == 9000
    with f30k.f30k_patched(f30k.make_loader(d, h), {}):
        pil, clean = pipeline.prep_image(sc, it["image_id"])
        conds = m4.build_conditions(sc, it, pil, clean, ctx)
    assert [c["name"] for c in conds] == ["clean", "noise0.1"]
    want = corruptions.apply_pixel("noise", 0.1, pil, m4.rung_rng(9000, "noise", 0), None)
    other = corruptions.apply_pixel("noise", 0.1, pil, m4.rung_rng(8000, "noise", 0), None)
    assert np.array_equal(conds[1]["pix"], np.asarray(want)) and not np.array_equal(np.asarray(want), np.asarray(other))


def test_check_flags_and_main(monkeypatch, capsys):
    assert f30k.check_flags(GOOD) == []
    for key, val in (("--run-id", "P2-LRF-L1"), ("--run-id", "P2-LRF-F30K2"), ("--family-run", "P2-LRF-PLAN"), ("--tbv", "off"), ("--layout-fix", "12"), ("--sanity", "patch"), ("--denoise-for", "jpeg")):
        flags = GOOD.copy()
        flags[flags.index(key) + 1] = val
        assert f30k.check_flags(flags), (key, val)
    assert f30k.check_flags([f for f in GOOD if f != "--neg-len"])
    flags = GOOD.copy()
    flags[flags.index("--folds-path") + 1] = str(ROOT / "runs" / "P2-LRF-FOLD" / "folds_lrf.json")
    assert f30k.check_flags(flags)
    assert f30k.check_flags(GOOD + ["--extra-cells", "shot_noise3"]) and f30k.check_flags(GOOD + ["--gate-true-layout"])
    called = []
    monkeypatch.setattr(m4, "main", lambda argv=None: called.append(argv) or 0)
    assert f30k.main(["--run-id", "P2-LRF-DN"]) == 2 and not called
    assert "STOP" in capsys.readouterr().err


def test_main_refuses_when_the_fold_images_are_missing(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(f30k, "ROOT", tmp_path)
    monkeypatch.setattr(m4, "main", lambda argv=None: pytest.fail("must not start"))
    (tmp_path / "runs" / bf.RUN_ID).mkdir(parents=True)
    (tmp_path / f30k.MANIFEST_REL).write_text(json.dumps(dict(image_sha256={})), encoding="utf8")
    (tmp_path / f30k.FOLDS_REL).write_text(json.dumps(dict(test=[dict(image_id=5)])), encoding="utf8")
    flags = GOOD.copy()
    flags[flags.index("--folds-path") + 1] = str(tmp_path / f30k.FOLDS_REL)
    assert f30k.main(flags) == 2 and "missing" in capsys.readouterr().err


# ------------------------------------------------------------------------------------------------ the driver stage
def test_driver_stage_lrf_f30k(tmp_path):
    assert gate_driver.STAGES["lrf-f30k"][:2] == ("exp_p2.run_gate_lrf_f30k", "P2-LRF-F30K")
    args = gate_driver.STAGE_ARGS["lrf-f30k"]
    assert args[args.index("--family-run") + 1] == "P2-LRF-PLAN-F30K" and args[args.index("--layout-fix") + 1] == "13" and "--neg-len" in args
    assert args[args.index("--sanity") + 1] == "" and args[args.index("--denoise-for") + 1] == "" and args[args.index("--tbv") + 1] == "on"
    assert f30k.check_flags(args + ["--run-id", "P2-LRF-F30K"]) == []
    assert gate_driver.resolve_max_chunks("lrf-f30k", None) == 24 and gate_driver.resolve_max_chunks("lrf-f30k", 3) == 3
    assert gate_driver.resolve_max_chunks("lrf-l1", None) == 60 and gate_driver.resolve_max_chunks("lrf-sev", None) == 20 and gate_driver.resolve_max_chunks("m4", None) == gate_driver.DEFAULT_MAX_CHUNKS
    # default_n: the n of THIS stage's family file; the older stages still read P2-LRF-PLAN
    for name, n in (("P2-LRF-PLAN", 450), ("P2-LRF-PLAN-F30K", 987)):
        (tmp_path / name).mkdir()
        (tmp_path / name / "family.json").write_text(json.dumps(dict(n_rule=dict(test_fold=n))), encoding="utf8")
    assert gate_driver.default_n("lrf-f30k", 1, tmp_path) == 987
    assert gate_driver.default_n("lrf-l1", 1, tmp_path) == gate_driver.default_n("lrf-sev", 1, tmp_path) == gate_driver.default_n("lrf-dn", 1, tmp_path) == 450
    assert gate_driver.default_n("lrf-f30k", 7, tmp_path / "nowhere") == 7
    cmd = gate_driver.build_cmd(gate_driver.STAGES["lrf-f30k"][0], "P2-LRF-F30K", 987, 15.0, 12.5, 0.5, 1, tmp_path, 80.0, args)
    assert "exp_p2.run_gate_lrf_f30k" in cmd and cmd[cmd.index("--n") + 1] == "987" and cmd[cmd.index("--run-id") + 1] == "P2-LRF-F30K"


def test_committed_family_and_n_rule_are_accepted_by_the_runner():
    fam = ROOT / "runs" / "P2-LRF-PLAN-F30K" / "family.json"
    if not fam.exists():
        pytest.skip("family file not built yet")
    f = json.loads(fam.read_text(encoding="utf8"))
    assert f["endpoint"] == "d" and [(x["corruption"], x["severity"], x["key"]) for x in f["family"]] == [("noise", 0.1, "noise0.1")]
    _, family, _ = m4.load_prereqs(ROOT / "runs", "P2-LRF-PLAN-F30K")
    assert family == [("noise", 0.1)]
    n = f["n_rule"]["test_fold"]
    assert m4.check_n_against_rule(n, ROOT / "runs", "P2-LRF-PLAN-F30K") == n
    fold = json.loads((ROOT / "runs" / bf.RUN_ID / "folds_f30k.json").read_text(encoding="utf8"))
    assert len(fold["test"]) == n


# ------------------------------------------------------------------------------------------------ the builder
def _rows(caps):
    return [dict(filename=f"{1000 + i}.jpg", image_id=1000 + i, caption0=c, n_captions=5) for i, c in enumerate(caps)]


def _w(k):
    """An alphabetic word of four letters (the content-word rule ignores digits and words under three letters)."""
    return "qq" + chr(97 + (k // 26) % 26) + chr(97 + k % 26)


def _synthetic(n=60, seed=0):
    rng = np.random.default_rng(seed)
    vocab = [_w(k) for k in range(300)]
    caps = [" ".join(rng.choice(vocab, int(rng.integers(3, 14)), replace=False)) for _ in range(n)]
    return _rows(caps)


N_TOK = lambda c: len(c.split())                                                      # noqa: E731  (one token per word)


def _build(rows, decoded=None, dist=None):
    decoded = decoded if decoded is not None else {r["filename"]: True for r in rows}
    dist = dist if dist is not None else {r["filename"]: (30, 1) for r in rows}
    return bf.build(rows, decoded, dist, N_TOK)


def test_content_words_and_stop_words():
    assert bf.content_words("A man, in the Red-hat; at 5pm!") == frozenset({"man", "red", "hat"})
    assert bf.content_words("Two men and a dog") == frozenset({"men", "dog"})            # 'two', 'and' are stop words; 'a' is too short
    assert "the" in bf.STOP_WORDS and bf.norm_caption("  a  b\n c ") == "a b c"


def test_read_annotations_filters_the_split_and_sorts_by_file_name_string(tmp_path):
    p = tmp_path / "a.csv"
    with open(p, "w", encoding="utf8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["raw", "sentids", "split", "filename", "img_id"])
        for fn, sp in (("20.jpg", "test"), ("100.jpg", "test"), ("3.jpg", "train"), ("1000.jpg", "test"), ("9.jpg", "val")):
            w.writerow([json.dumps([f"first  caption {fn}", "second"]), "[0, 1]", sp, fn, 0])
    rows = bf.read_annotations(p)
    assert [r["filename"] for r in rows] == ["100.jpg", "1000.jpg", "20.jpg"]            # string order, as specified: file name, ascending
    assert rows[0]["caption0"] == "first caption 100.jpg" and rows[0]["image_id"] == 100
    with pytest.raises(ValueError):
        bf.image_id_of("007.jpg")


def test_builder_is_deterministic_and_ordered():
    rows = _synthetic()
    a, b = _build(rows), _build(rows)
    assert json.dumps(a["fold"], sort_keys=True) == json.dumps(b["fold"], sort_keys=True)
    t = a["fold"]["test"]
    assert len(t) == 60 and [it["idx"] for it in t] == list(range(60)) and [it["gid"] for it in t] == [9000 + i for i in range(60)]
    assert [it["filename"] for it in t] == sorted(it["filename"] for it in t)
    assert a["fold"]["cal"] == a["fold"]["head"] == a["fold"]["test_ext"] == []
    assert all(it["image_id"] == int(it["filename"][:-4]) for it in t)


def test_negatives_use_the_prescribed_generator_and_are_word_disjoint():
    rows = _synthetic()
    t = _build(rows)["fold"]["test"]
    caps = [r["caption0"] for r in rows]
    W = [bf.content_words(c) for c in caps]
    for i, it in enumerate(t):
        rng = np.random.default_rng([2026, 1031, i])
        while True:                                                                  # the A7.2 redraw rule, written out independently
            j = int(rng.integers(0, len(caps)))
            if j != i and not (W[i] & W[j]):
                break
        assert it["neg_idx"] == j and it["neg_caption"] == caps[j] and it["neg_image_id"] == t[j]["image_id"]
        assert not (bf.content_words(it["neg_caption"]) & bf.content_words(it["caption"]))
        assert not (bf.content_words(it["neg_caption_len"]) & bf.content_words(it["caption"]))
        assert it["neg_caption_len"] == t[it["neg_len_idx"]]["caption"] and it["neg_len_diff"] == it["n_tok_neg_len"] - it["n_tok"] and it["neg_len_exact"] == (it["neg_len_diff"] == 0)
    seq = [it["neg_idx"] for it in t]
    assert len(set(seq)) > 10                                                      # a real random draw, not a constant


def test_length_matched_negative_is_exact_when_possible_else_nearest():
    rows = _synthetic(80)
    t = _build(rows)["fold"]["test"]
    W = [bf.content_words(it["caption"]) for it in t]
    for i, it in enumerate(t):
        adm = [j for j in range(len(t)) if j != i and not (W[i] & W[j])]
        exact = [j for j in adm if t[j]["n_tok"] == it["n_tok"]]
        if exact:
            assert it["neg_len_exact"] and it["neg_len_idx"] in exact
        else:
            best = min(abs(t[j]["n_tok"] - it["n_tok"]) for j in adm)
            assert abs(it["neg_len_diff"]) == best and not it["neg_len_exact"]
    # a case with no exact match: the lone 25-token caption must get the nearest length (diff recorded)
    odd = _synthetic(30, seed=3)
    odd[7]["caption0"] = " ".join(f"zz{k}" for k in range(25))
    ft = _build(odd)["fold"]["test"][7]
    others = [N_TOK(r["caption0"]) for k, r in enumerate(odd) if k != 7]
    assert not ft["neg_len_exact"] and abs(ft["neg_len_diff"]) == min(abs(o - 25) for o in others)


def test_exclusions_a_b_c_are_listed_with_reasons_and_idx_follows_the_survivors():
    rows = _synthetic(40)
    decoded = {r["filename"]: True for r in rows}
    decoded["1003.jpg"] = False
    dist = {r["filename"]: (30, 1) for r in rows}
    dist["1005.jpg"] = (4, 777)                                                      # exactly at the threshold: excluded
    dist["1006.jpg"] = (5, 778)                                                      # one above: kept
    res = _build(rows, decoded, dist)
    reasons = {e["filename"]: e["reason"] for e in res["exclusions"]}
    assert reasons == {"1003.jpg": "a_undecodable", "1005.jpg": "b_near_duplicate_of_coco"}
    assert [e for e in res["exclusions"] if e["filename"] == "1005.jpg"][0]["coco_image_id"] == 777
    t = res["fold"]["test"]
    assert len(t) == 38 and "1006.jpg" in {it["filename"] for it in t} and [it["idx"] for it in t] == list(range(38))
    assert res["report"]["n_excluded_a_undecodable"] == 1 and res["report"]["n_excluded_b_near_duplicate"] == 1 and res["report"]["n_kept"] == 38
    # (c): item 4's caption shares a content word with every other caption, so it has no admissible negative; the others do (once it is out of the pool)
    rows2 = _rows([f"{_w(100 + i)} {_w(200 + i)}" for i in range(20)])
    rows2[4]["caption0"] = " ".join(_w(100 + i) for i in range(20) if i != 4)
    res2 = _build(rows2)
    assert [e["filename"] for e in res2["exclusions"]] == ["1004.jpg"] and res2["exclusions"][0]["reason"] == "c_no_admissible_negative"
    assert res2["report"]["n_excluded_c_no_admissible_negative"] == 1 and res2["report"]["c_fixpoint_iterations"] == 2 and len(res2["fold"]["test"]) == 19
    assert [it["idx"] for it in res2["fold"]["test"]] == list(range(19)) and all(it["filename"] != "1004.jpg" for it in res2["fold"]["test"])
    for it in res2["fold"]["test"]:                                                  # after the fixpoint every negative points at a kept item
        assert it["neg_caption"] in {x["caption"] for x in res2["fold"]["test"]} and it["neg_idx"] != it["idx"]


def test_token_range_is_counted_not_applied():
    rows = _synthetic(30, seed=2)
    rows[3]["caption0"] = " ".join(f"tt{k}" for k in range(40))                     # 40 tokens: outside 5 to 32
    rows[4]["caption0"] = "short one"                                                # 2 tokens
    res = _build(rows)
    assert res["report"]["n_kept"] == 30                                             # A7.2 lists no token-range step: the item stays
    tr = res["report"]["token_range"]
    assert tr["n_outside"] >= 2 and 3 in tr["outside_idx"] and 4 in tr["outside_idx"] and tr["n_expected_scored"] == 30 - tr["n_outside"]
    assert tr["would_stop_run"] == (tr["n_outside"] / 30 > 0.10)


def test_dhash_catches_recompressed_copies_and_not_other_images():
    from PIL import Image
    a, b = fake_image(1, 128), fake_image(2, 128)
    assert bf.hamming(bf.dhash(a), bf.dhash(a)) == 0
    buf = io.BytesIO()
    a.resize((115, 115)).save(buf, "JPEG", quality=70)
    assert bf.hamming(bf.dhash(a), bf.dhash(Image.open(io.BytesIO(buf.getvalue())).convert("RGB"))) <= bf.HAMMING_MAX
    assert bf.hamming(bf.dhash(a), bf.dhash(b)) > bf.HAMMING_MAX
    assert 0 <= bf.dhash(a) < 2 ** 64
    pc = bf.dhash_positive_control([fake_image(i, 128) for i in range(20)])
    assert pc["ok"] and pc["n_caught"] == 20


def test_extract_uses_basenames_skips_resource_forks_and_reports_missing(tmp_path):
    z = tmp_path / "a.zip"
    img = lambda k: (lambda b: (fake_image(k, 32).save(b, "JPEG"), b.getvalue())[1])(io.BytesIO())      # noqa: E731
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("flickr30k-images/1.jpg", img(1))
        zf.writestr("flickr30k-images/2.jpg", img(2))
        zf.writestr("__MACOSX/flickr30k-images/._1.jpg", b"junk")
        zf.writestr("../../escape/3.jpg", img(3))                                    # a hostile member name: only its basename is used
    out = bf.extract_test_images(z, ["1.jpg", "3.jpg"], tmp_path / "out")
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["1.jpg", "3.jpg"] and not (tmp_path.parent / "escape").exists()
    assert out["1.jpg"]["sha256"] == hashlib.sha256((tmp_path / "out" / "1.jpg").read_bytes()).hexdigest()
    assert (tmp_path / "out" / "1.jpg").read_bytes() != b"junk"
    with pytest.raises(FileNotFoundError):
        bf.extract_test_images(z, ["1.jpg", "404.jpg"], tmp_path / "out2")
    assert bf.decode_image(b"not an image") is None and bf.decode_image((tmp_path / "out" / "1.jpg").read_bytes()).mode == "RGB"


def test_leak_check_passes_and_catches_injected_defects():
    rows = _synthetic(50)
    res = _build(rows)
    dist = {r["filename"]: (30, 1) for r in rows}
    fold = res["fold"]
    assert bf.leak_check(fold, dist, rows)["ok"]
    import copy

    def fails(f, d=dist):
        try:
            bf.leak_check(f, d, rows)
            return False
        except bf.LeakCheckFailed:
            return True
    f = copy.deepcopy(fold)
    f["test"][3]["gid"] = 8100
    assert fails(f)                                                                  # gid collision with the LRF fold
    f = copy.deepcopy(fold)
    f["test"][2]["neg_caption"] = f["test"][2]["caption"]
    assert fails(f)                                                                  # wrong caption equals the true one
    f = copy.deepcopy(fold)
    f["test"][1]["image_id"] = f["test"][0]["image_id"]
    assert fails(f)                                                                  # repeated image
    assert fails(fold, dict(dist, **{fold["test"][5]["filename"]: (3, 1)}))          # a kept image too close to a COCO image
    f = copy.deepcopy(fold)
    f["test"][4]["n_tok"] += 1
    assert fails(f)                                                                  # length bookkeeping broken
    f = copy.deepcopy(fold)
    f["test"].reverse()
    assert fails(f)


def test_builder_refuses_to_overwrite(tmp_path, capsys):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "folds_f30k.json").write_text("{}", encoding="utf8")
    assert bf.main(["--out-dir", str(tmp_path / "out"), "--plan-dir", str(tmp_path / "plan"), "--f30k-dir", str(tmp_path / "none")]) == 2
    assert "not overwriting" in capsys.readouterr().err
    assert (tmp_path / "out" / "folds_f30k.json").read_text(encoding="utf8") == "{}" and not (tmp_path / "plan").exists()


def test_image_dir_is_outside_the_repository_next_to_the_coco_data():
    assert bf.F30K_DIR == common.COCO_DIR.parent / "flickr30k" and ROOT not in bf.F30K_DIR.parents


# ------------------------------------------------------------------------------------------------ the analysis
def _lines(path, cond, yn, yl, ynL=None, ylL=None, exact=None):
    with open(path, "a", encoding="utf-8") as fh:
        for i in range(len(yn)):
            d = dict(idx=i, gid=9000 + i, image_id=500 + i, condition=cond, n_tok=10, n_tok_neg=12, y_none=int(yn[i]), y_lrf=int(yl[i]))
            if ylL is not None:
                d.update(y_none_L=int(ynL[i]), y_lrf_L=int(ylL[i]), neg_len_exact=bool(exact[i]), n_tok_neg_len=10, neg_len_diff=0 if exact[i] else 1)
            fh.write(json.dumps(d) + "\n")


def _tail(n, k):
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2.0 ** n


def _pairs(n, b, c, base_right=0.5):
    """none/lrf vectors with exactly b items LRF-right-NONE-wrong and c the reverse, the rest both right (half) or both wrong."""
    yn, yl = np.ones(n, int), np.ones(n, int)
    yn[:b], yl[:b] = 0, 1
    yn[b:b + c], yl[b:b + c] = 1, 0
    rest = np.arange(b + c, n)
    yn[rest[::2]] = yl[rest[::2]] = 0
    return yn, yl


def test_analysis_known_mcnemar_and_labels(tmp_path):
    n = 1000
    yn, yl = _pairs(n, 20, 5)
    ex = np.ones(n, bool)
    ex[-100:] = False                                                                # 100 items whose length-matched caption differs in length
    ynL, ylL = _pairs(n, 14, 4)
    _lines(tmp_path / "predictions.jsonl", "noise0.1", yn, yl, ynL, ylL, ex)
    cn, cl = _pairs(n, 10, 12)
    _lines(tmp_path / "predictions.jsonl", "clean", cn, cl, cn, cl, np.ones(n, bool))
    r = FA.analyse(tmp_path, need_meta=False)
    f1 = r["F1"]
    assert (f1["b"], f1["c"], f1["n"]) == (20, 5, 1000) and f1["net"] == pytest.approx(0.015)
    assert f1["p_one"] == pytest.approx(_tail(25, 20), rel=1e-12) and f1["p_one"] < 0.025
    assert f1["confirmed"] and f1["label"] == "confirmed" and f1["headline_gain_claim_allowed"] and "raised accuracy" in f1["wording"]
    assert f1["ci95"][0] < f1["net"] < f1["ci95"][1] and f1["ci90"][0] > f1["ci95"][0]
    ni = r["F_NI"]
    assert (ni["b"], ni["c"]) == (10, 12) and ni["net"] == pytest.approx(-0.002) and ni["non_inferior"] is True and ni["lower90"] > -0.03
    ln = r["F_LEN"]
    assert ln["n_excluded_length_mismatch"] == 100 and ln["n"] == 900 and ln["n_with_length_matched_negative"] == 1000
    assert (ln["b"], ln["c"]) == (14, 4) and ln["p_one"] == pytest.approx(_tail(18, 14), rel=1e-12) and ln["label"] == "confirmed"
    d = r["descriptive"]
    assert d["noise0.1"]["acc_lrf"] - d["noise0.1"]["acc_none"] == pytest.approx(f1["net"]) and d["gain_on_clean"] == pytest.approx(-0.002)
    assert r["underpowered"] is False and r["n_scored"] == 1000
    a2 = FA.analyse(tmp_path, need_meta=False)
    assert a2["F1"]["ci95"] == f1["ci95"] and a2["F_NI"]["ci90"] == ni["ci90"]       # fixed seed: byte-identical rerun


def test_analysis_not_confirmed_ties_and_noninferiority_failure(tmp_path):
    n = 1000
    yn, yl = _pairs(n, 12, 10)                                                       # p about 0.42
    _lines(tmp_path / "predictions.jsonl", "noise0.1", yn, yl)
    cn, cl = _pairs(n, 5, 80)                                                        # clean: LRF loses 7.5 points
    _lines(tmp_path / "predictions.jsonl", "clean", cn, cl)
    r = FA.analyse(tmp_path, need_meta=False)
    assert r["F1"]["label"] == "not confirmed" and not r["F1"]["confirmed"] and not r["F1"]["headline_gain_claim_allowed"]
    assert r["F1"]["p_one"] == pytest.approx(_tail(22, 12)) and "did not confirm" in r["F1"]["wording"] and "one-sided p" in r["F1"]["wording"]
    assert r["F_NI"]["non_inferior"] is False and r["F_NI"]["lower90"] < -0.03
    assert r["F_LEN"]["status"] == "not run"
    yn, yl = _pairs(n, 0, 0)                                                         # b == c == 0: p = 1, not confirmed
    p2 = tmp_path / "t"
    p2.mkdir()
    _lines(p2 / "predictions.jsonl", "noise0.1", yn, yl)
    _lines(p2 / "predictions.jsonl", "clean", yn, yl)
    r2 = FA.analyse(p2, need_meta=False)
    assert r2["F1"]["p_one"] == 1.0 and r2["F1"]["label"] == "not confirmed" and r2["F_NI"]["non_inferior"] is True


def test_analysis_p_between_0025_and_005_confirms_without_headline(tmp_path):
    n = 1000
    # b = 17, c = 7: one-sided exact p = P(Bin(24, .5) >= 17) = 0.032
    yn, yl = _pairs(n, 17, 7)
    _lines(tmp_path / "predictions.jsonl", "noise0.1", yn, yl)
    _lines(tmp_path / "predictions.jsonl", "clean", yn, yl)
    f1 = FA.analyse(tmp_path, need_meta=False)["F1"]
    assert 0.025 < f1["p_one"] <= 0.05 and f1["confirmed"] and not f1["headline_gain_claim_allowed"]


def test_analysis_underpowered_below_800_items(tmp_path):
    n = 799
    yn, yl = _pairs(n, 30, 2)
    _lines(tmp_path / "predictions.jsonl", "noise0.1", yn, yl)
    _lines(tmp_path / "predictions.jsonl", "clean", yn, yl)
    r = FA.analyse(tmp_path, need_meta=False)
    assert r["underpowered"] and r["underpowered_label"] == "underpowered (799 of 1,000)" and r["F1"]["confirmed"] and not r["F1"]["headline_gain_claim_allowed"]
    assert "underpowered (799 of 1,000)" in r["F1"]["label"]
    d = tmp_path / "ok"
    d.mkdir()
    yn, yl = _pairs(800, 30, 2)
    _lines(d / "predictions.jsonl", "noise0.1", yn, yl)
    _lines(d / "predictions.jsonl", "clean", yn, yl)
    assert FA.analyse(d, need_meta=False)["underpowered"] is False


def test_analysis_refuses_mismatched_items_and_checks_the_scorer_meta(tmp_path):
    yn, yl = _pairs(10, 2, 1)
    _lines(tmp_path / "predictions.jsonl", "noise0.1", yn, yl)
    _lines(tmp_path / "predictions.jsonl", "clean", yn[:9], yl[:9])
    with pytest.raises(RuntimeError):
        FA.analyse(tmp_path, need_meta=False)
    ok = dict(conds=["clean", "noise0.1"], conds_absent_in_rows=[], n_items_skipped_no_arrays=0, positive_control=dict(ok=True), hashes={"x": 1}, n_items_rows=10)
    (tmp_path / "lrf_score_meta.json").write_text(json.dumps(ok), encoding="utf8")
    assert FA.check_meta(tmp_path)["ok"]
    for bad in (dict(conds=["clean"]), dict(n_items_skipped_no_arrays=2), dict(positive_control=dict(ok=False)), dict(hashes={})):
        (tmp_path / "lrf_score_meta.json").write_text(json.dumps(dict(ok, **bad)), encoding="utf8")
        with pytest.raises(RuntimeError):
            FA.check_meta(tmp_path)
    only = tmp_path / "only"
    only.mkdir()
    _lines(only / "predictions.jsonl", "noise0.1", yn, yl)
    with pytest.raises(RuntimeError):
        FA.analyse(only, need_meta=False)


def test_analysis_cli_writes_json(tmp_path, capsys):
    n = 1000
    yn, yl = _pairs(n, 20, 5)
    _lines(tmp_path / "predictions.jsonl", "noise0.1", yn, yl)
    _lines(tmp_path / "predictions.jsonl", "clean", yn, yl)
    (tmp_path / "lrf_score_meta.json").write_text(json.dumps(dict(conds=["clean", "noise0.1"], conds_absent_in_rows=[], n_items_skipped_no_arrays=0, positive_control=dict(ok=True), hashes={"x": 1}, n_items_rows=n)), encoding="utf8")
    assert FA.main(["--run", str(tmp_path)]) == 0
    out = json.loads((tmp_path / "f30k_analysis.json").read_text(encoding="utf8"))
    assert out["F1"]["label"] == "confirmed" and out["F_NI"]["non_inferior"] is True and out["scorer_meta"]["ok"]
    assert FA.main(["--run", str(tmp_path / "nowhere")]) == 2


def test_optional_token_range_rule_is_off_by_default_and_drops_before_the_pool():
    rows = _synthetic(40, seed=2)
    rows[3]["caption0"] = " ".join(_w(k) for k in range(40))                        # 40 tokens
    rows[4]["caption0"] = "short one"                                                # 2 tokens
    off, on = _build(rows), bf.build(rows, {r["filename"]: True for r in rows}, {r["filename"]: (30, 1) for r in rows}, N_TOK, token_range_rule=True)
    assert off["report"]["n_kept"] == 40 and off["report"]["n_excluded_d_token_range"] == 0 and not off["report"]["token_range_rule_applied"]
    assert on["report"]["token_range_rule_applied"] and on["report"]["n_excluded_d_token_range"] >= 2
    gone = {e["filename"] for e in on["exclusions"] if e["reason"] == "d_token_range_5_32"}
    assert {"1003.jpg", "1004.jpg"} <= gone
    assert on["report"]["token_range"]["n_outside"] == 0 and on["report"]["token_range"]["would_stop_run"] is False
    assert all(5 <= it["n_tok"] <= 32 and 5 <= it["n_tok_neg"] <= 32 and 5 <= it["n_tok_neg_len"] <= 32 and it["filename"] not in gone for it in on["fold"]["test"])
    assert [it["idx"] for it in on["fold"]["test"]] == list(range(len(on["fold"]["test"])))


def test_analysis_flags_a_partial_run(tmp_path):
    """Audit F2: a run stopped before the planned fold size is labelled partial and loses the headline claim."""
    import json as _json
    from analysis.paper2.lrf import f30k_analysis as FA
    run = tmp_path / "P2-LRF-F30K"
    run.mkdir()
    (tmp_path / "P2-LRF-PLAN-F30K").mkdir()
    (tmp_path / "P2-LRF-PLAN-F30K" / "family.json").write_text(_json.dumps({"n_rule": {"test_fold": 900}}), encoding="utf-8")
    with open(run / "predictions.jsonl", "w", encoding="utf-8") as fh:
        for i in range(850):
            for c in ("clean", "noise0.1"):
                yl = 1 if (c == "noise0.1" and i < 100) else int(i % 3 != 0)
                fh.write(_json.dumps(dict(idx=i, gid=9000 + i, image_id=i, condition=c, y_none=int(i % 3 != 0), y_lrf=yl)) + "\n")
    r = FA.analyse(run, need_meta=False)
    assert r["complete"] is False and "partial (850 of 900)" in r["F1"]["label"] and not r["F1"]["headline_gain_claim_allowed"]
