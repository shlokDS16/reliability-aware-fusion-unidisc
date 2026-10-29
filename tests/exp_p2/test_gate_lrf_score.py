"""A6.11 item 5: the LRF scorer (exp_p2/gate/lrf_score.py). A fake frozen model in the documented format (spec.json + model.npz as written by analysis_posthoc/learned_ceiling/lrf.py --freeze) with the REAL committed
feature code; synthetic stored item arrays. CPU only."""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import common                                                   # noqa: E402
from exp_p2.gate import evidence, lrf_score as ls                           # noqa: E402

FEATURE_SRC = ROOT / "analysis_posthoc" / "learned_ceiling" / "data.py"
M = 1024
CONDS = ls.L1_CONDS


def _make_frozen(tmp_path, seed=0, knots=3):
    code = tmp_path / "code"
    code.mkdir(exist_ok=True)
    shutil.copy(FEATURE_SRC, code / "data.py")
    (code / "families.py").write_text("# stand-in\n")
    (code / "lrf.py").write_text("# stand-in\n")
    ns = {}
    exec(compile(FEATURE_SRC.read_text(encoding="utf8"), "data.py", "exec"), ns)
    names = ns["feature_names"]()
    F = len(names)
    rng = np.random.default_rng(seed)
    fz_dir = tmp_path / "frozen"
    fz_dir.mkdir(exist_ok=True)
    np.savez(fz_dir / "model.npz", a=rng.normal(0, 0.3, F), b=np.array(0.2), c=rng.normal(0, 0.1, (F, knots)), knots=np.sort(rng.normal(0, 1, (F, knots)), axis=1), mu=rng.normal(0, 1, F),
             sd=rng.uniform(0.5, 2, F), feature_names=np.array(names))
    spec = dict(name="fake LRF", features=names, model_sha256=ls.sha256_file(fz_dir / "model.npz"), code_sha256={f: ls.sha256_file(code / f) for f in ("data.py", "families.py", "lrf.py")})
    (fz_dir / "spec.json").write_text(json.dumps(spec))
    return fz_dir, code, names


def _arrays(rng, conds=CONDS, with_L=False, tbv=True):
    d = {}
    for c in conds:
        B = rng.normal(-8, 3, M).astype(np.float32)
        D = (B + rng.normal(0.5, 1, M)).astype(np.float32)
        d[f"{c}_B"], d[f"{c}_D"], d[f"{c}_s3"] = B, D, rng.uniform(0, 1, M).astype(np.float32)
        d[f"{c}_tex"], d[f"{c}_nbr"] = rng.uniform(0, 50, M).astype(np.float32), rng.uniform(0, 5, M).astype(np.float32)
        if tbv:
            d[f"{c}_tbv"] = rng.normal(-5, 2, M).astype(np.float32)
        d[f"{c}_delta"] = rng.normal(0.05, 1.5, M).astype(np.float32)
        d[f"{c}_flag0.05"] = rng.random(M) < 0.1
        d[f"{c}_codes"] = rng.integers(0, 16000, M).astype(np.int16)
        if with_L:
            d[f"{c}_deltaL"] = rng.normal(0.05, 1.5, M).astype(np.float32)
    return d


def _run(tmp_path, n=6, with_L=False, seed=1, tbv=True):
    rng = np.random.default_rng(seed)
    run = tmp_path / "runs" / "P2-LRF-L1"
    (run / "arrays").mkdir(parents=True)
    rows = []
    for i in range(n):
        d = _arrays(rng, with_L=with_L, tbv=tbv)
        np.savez(run / "arrays" / f"item{i:04d}.npz", **d)
        conds = {}
        for c in CONDS:
            flag = d[f"{c}_flag0.05"]
            conds[c] = dict(img={"none": evidence.evidence_from_delta(d[f"{c}_delta"]), "gate0.05": evidence.arm_summary(d[f"{c}_delta"], flag)})
        rows.append(dict(idx=i, gid=8000 + i, image_id=500 + i, n_tok=10 + i, n_tok_neg=12, conds=conds, **(dict(n_tok_neg_len=10 + i + (i % 2)) if with_L else {})))
    (run / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return run, rows


# ------------------------------------------------------------------------------------------------ hashes
def test_load_frozen_verifies_and_exposes_the_documented_format(tmp_path):
    fz_dir, code, names = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    assert fz["feature_names"] == names and fz["a"].shape == (35,) and fz["c"].shape == fz["knots"].shape == (35, 3)
    assert fz["hashes"]["model_sha256"] == ls.sha256_file(fz_dir / "model.npz") and fz["hashes"]["pinned_externally"] is False and len(fz["hashes"]["scoring_code_sha256"]) == 64
    assert ls.load_frozen(fz_dir, code, pins=dict(model_sha256=fz["hashes"]["model_sha256"], code_sha256=fz["hashes"]["code_sha256"], decision_rule=ls.DECISION_RULE,
                                                   scoring_code_sha256=ls.this_code_sha256()))["hashes"]["pinned_externally"] is True


def test_any_hash_difference_refuses(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    good = ls.load_frozen(fz_dir, code)["hashes"]
    with pytest.raises(ls.HashMismatch, match="pins model_sha256"):
        ls.load_frozen(fz_dir, code, pins=dict(model_sha256="0" * 64))
    with pytest.raises(ls.HashMismatch, match="pins code_sha256"):
        ls.load_frozen(fz_dir, code, pins=dict(code_sha256={"data.py": "0" * 64}))
    with pytest.raises(ls.HashMismatch, match="scoring_code_sha256"):
        ls.load_frozen(fz_dir, code, pins=dict(scoring_code_sha256="0" * 64))
    with pytest.raises(ls.HashMismatch, match="decision_rule"):
        ls.load_frozen(fz_dir, code, pins=dict(decision_rule="Y = 1[mean w Delta >= 0]"))
    (code / "data.py").write_text((code / "data.py").read_text() + "\n# edit\n")
    with pytest.raises(ls.HashMismatch, match="data.py"):
        ls.load_frozen(fz_dir, code)
    shutil.copy(FEATURE_SRC, code / "data.py")
    assert ls.load_frozen(fz_dir, code)["hashes"] == good
    (code / "lrf.py").unlink()
    with pytest.raises(FileNotFoundError, match="lrf.py"):
        ls.load_frozen(fz_dir, code)
    (code / "lrf.py").write_text("# stand-in\n")
    z = dict(np.load(fz_dir / "model.npz"))
    z["a"] = z["a"] + 1e-3
    np.savez(fz_dir / "model.npz", **z)
    with pytest.raises(ls.HashMismatch, match="model.npz"):
        ls.load_frozen(fz_dir, code)


def test_a_crlf_checkout_of_the_pinned_feature_code_is_accepted(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    spec = json.loads((fz_dir / "spec.json").read_text())
    lf = FEATURE_SRC.read_bytes().replace(b"\r\n", b"\n")
    (code / "data.py").write_bytes(lf.replace(b"\n", b"\r\n"))
    spec["code_sha256"]["data.py"] = ls.hashlib.sha256(lf).hexdigest()           # the pin was taken on the LF bytes
    (fz_dir / "spec.json").write_text(json.dumps(spec))
    assert ls.load_frozen(fz_dir, code)["spec"]["name"] == "fake LRF"


def test_feature_list_mismatch_refuses(tmp_path):
    fz_dir, code, names = _make_frozen(tmp_path)
    spec = json.loads((fz_dir / "spec.json").read_text())
    spec["features"] = names[::-1]
    (fz_dir / "spec.json").write_text(json.dumps(spec))
    with pytest.raises(ls.HashMismatch, match="feature list"):
        ls.load_frozen(fz_dir, code)


# ------------------------------------------------------------------------------------------------ inference and the decision rule
def test_weights_equal_an_independent_evaluation_of_the_frozen_formula(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    d = _arrays(np.random.default_rng(3), conds=("noise0.1",))
    w = ls.weights(fz, d, "noise0.1")
    raw = ls.raw_from_arrays(d, "noise0.1")
    X = fz["engineer"](raw)[0, 0]
    Xs = (X - fz["mu"]) / fz["sd"]
    f = fz["b"] + Xs @ fz["a"]
    for fi in range(Xs.shape[1]):
        for k in range(fz["knots"].shape[1]):
            f = f + fz["c"][fi, k] * np.maximum(Xs[:, fi] - fz["knots"][fi, k], 0.0)
    assert w.shape == (M,) and np.allclose(w, 1 / (1 + np.exp(-f)), atol=1e-12) and ((w > 0) & (w < 1)).all()
    # caption-withheld only: Delta, z and the flag do not enter
    d2 = dict(d, **{"noise0.1_delta": d["noise0.1_delta"] * -3, "noise0.1_flag0.05": ~d["noise0.1_flag0.05"], "noise0.1_codes": d["noise0.1_codes"][::-1]})
    assert np.array_equal(ls.weights(fz, d2, "noise0.1"), w)


def test_decision_rule_ties_are_wrong_and_non_finite_is_an_error():
    w = np.full(M, 0.5)
    assert ls.decide(w, np.full(M, 0.1))["y"] == 1 and ls.decide(w, np.full(M, -0.1))["y"] == 0
    assert ls.decide(w, np.zeros(M))["y"] == 0                                  # tie
    d = np.zeros(M)
    d[0], d[1] = 1.0, -1.0
    assert ls.decide(np.full(M, 0.5), d)["y"] == 0                              # exact cancellation: tie
    with pytest.raises(ls.NonFinite):                                           # all-zero weights: margin 0/0 is non-finite -> an error, never a "wrong" decision (A6 r1, C6-2)
        ls.decide(np.zeros(M), np.full(M, 1.0))
    r = ls.decide(np.concatenate([np.ones(1), np.zeros(M - 1)]), np.concatenate([[2.0], np.full(M - 1, -5.0)]))
    assert r["y"] == 1                                                          # only the weighted tokens count


# ------------------------------------------------------------------------------------------------ a run
def test_score_run_positive_control_primary_and_length_matched(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    run, rows = _run(tmp_path, n=6, with_L=True)
    lines, meta = ls.score_run(run, fz)
    assert len(lines) == 6 * 4 and meta["positive_control"] == dict(n_checked=24, ok=True) and meta["hashes"]["model_sha256"] == fz["hashes"]["model_sha256"]
    l0 = lines[0]
    assert {"y_none", "y_gatem", "y_lrf", "m_lrf", "y_none_L", "y_gatem_L", "y_lrf_L", "neg_len_diff", "neg_len_exact", "n_tok", "n_tok_neg"} <= set(l0) and l0["condition"] == "clean" and l0["idx"] == 0
    d = dict(np.load(run / "arrays" / "item0002.npz"))
    exp = ls.decide(ls.weights(fz, d, "noise0.1"), d["noise0.1_deltaL"])
    got = [l for l in lines if l["idx"] == 2 and l["condition"] == "noise0.1"][0]
    assert got["y_lrf_L"] == exp["y"] and got["neg_len_exact"] == (rows[2]["n_tok_neg_len"] == rows[2]["n_tok"])
    assert got["y_none"] == int(d["noise0.1_delta"].mean() > 0)
    lines5, _ = ls.score_run(run, fz, n_items=2)
    assert len(lines5) == 8 and lines5 == lines[:8]


def test_positive_control_catches_a_row_that_disagrees_with_the_arrays(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    run, rows = _run(tmp_path, n=3)
    rows[1]["conds"]["jpeg10"]["img"]["none"]["y"] ^= 1
    (run / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(AssertionError, match="Y_NONE"):
        ls.score_run(run, fz)
    rows[1]["conds"]["jpeg10"]["img"]["none"]["y"] ^= 1
    rows[2]["conds"]["clean"]["img"]["gate0.05"]["y"] ^= 1
    (run / "items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(AssertionError, match="GATE-M"):
        ls.score_run(run, fz)


def test_missing_tbv_arrays_stop_the_scorer(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    run, _ = _run(tmp_path, n=2, tbv=False)
    with pytest.raises(KeyError, match="tbv"):
        ls.score_run(run, fz)


def test_incomplete_items_and_absent_conditions_are_skipped_and_counted(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    run, rows = _run(tmp_path, n=4)
    (run / "arrays" / "item0003.npz").unlink()
    lines, meta = ls.score_run(run, fz, CONDS + ("shot_noise3",))
    assert meta["n_items_skipped_no_arrays"] == 1 and meta["conds_absent_in_rows"] == ["shot_noise3"] and len(lines) == 3 * 4


def test_write_predictions_is_deterministic_and_refuses_to_overwrite(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    run, _ = _run(tmp_path, n=3)
    l1, m1 = ls.score_run(run, fz)
    out = ls.write_predictions(l1, m1, run / "predictions.jsonl")
    b1 = out.read_bytes()
    with pytest.raises(FileExistsError):
        ls.write_predictions(l1, m1, out)
    l2, m2 = ls.score_run(run, fz)
    ls.write_predictions(l2, m2, out, force=True)
    assert out.read_bytes() == b1
    meta = json.loads((run / "lrf_score_meta.json").read_text())
    assert meta["predictions_sha256"] == ls.sha256_file(out) and meta["positive_control"]["ok"]


def _inputs(tmp_path, run, codebook=b"codebook bytes", di=b"di bytes"):
    """Tiny stand-ins for the two untracked inputs and the run's config.json record of their hashes (A6.2 hash set)."""
    runs = tmp_path / "runs"
    (runs / "P2-GATE-M1").mkdir(parents=True, exist_ok=True)
    (runs / "P2-GATE-DCACHE").mkdir(parents=True, exist_ok=True)
    (runs / "P2-GATE-M1" / "codebook.npy").write_bytes(codebook)
    (runs / "P2-GATE-DCACHE" / "DI_n013.npy").write_bytes(di)
    cb, dh = ls.sha256_file(runs / "P2-GATE-M1" / "codebook.npy"), ls.sha256_file(runs / "P2-GATE-DCACHE" / "DI_n013.npy")
    (run / "config.json").write_text(json.dumps(dict(codebook_sha256=cb, dcache_di_sha256=dh, dcache_di_file="DI_n013.npy")))
    return runs, dict(codebook_sha256=cb, di_sha256=dh, di_file="DI_n013.npy")


def test_default_pins_are_the_r1_table():
    assert ls.EXPECTED_CODEBOOK_SHA256.startswith("ff15b9b5") and ls.EXPECTED_DI_N013_SHA256.startswith("f7744253")
    assert ls.DEFAULT_PINS["code_sha256"]["data.py"].startswith("14421ffb") and ls.DEFAULT_PINS["code_sha256"]["families.py"].startswith("1c49827d")
    assert ls.FROZEN_DIR.name == "P2-LRF-FROZEN-LFIX"                           # the retired model (runs/P2-LRF-FROZEN) is never the default


def test_run_inputs_are_hashed_on_disk_and_against_the_runs_config(tmp_path):
    run, _ = _run(tmp_path, n=1)
    runs, pins = _inputs(tmp_path, run)
    assert ls.verify_run_inputs(run, runs, pins)["codebook_sha256"] == pins["codebook_sha256"]
    with pytest.raises(ls.HashMismatch, match="pinned"):                         # the on-disk file differs from the pinned table
        ls.verify_run_inputs(run, runs, dict(pins, codebook_sha256="0" * 64))
    (runs / "P2-GATE-M1" / "codebook.npy").unlink()                              # missing codebook
    with pytest.raises(ls.HashMismatch, match="codebook.npy missing"):
        ls.verify_run_inputs(run, runs, pins)
    (runs / "P2-GATE-M1" / "codebook.npy").write_bytes(b"codebook bytes")
    (runs / "P2-GATE-DCACHE" / "DI_n013.npy").unlink()                           # missing DI_n013
    with pytest.raises(ls.HashMismatch, match="DI_n013.npy missing"):
        ls.verify_run_inputs(run, runs, pins)
    (runs / "P2-GATE-DCACHE" / "DI_n013.npy").write_bytes(b"di bytes")
    (run / "config.json").write_text(json.dumps(dict(codebook_sha256=pins["codebook_sha256"], dcache_di_sha256="1" * 64)))     # the GPU run recorded another D cache
    with pytest.raises(ls.HashMismatch, match="recorded dcache_di_sha256"):
        ls.verify_run_inputs(run, runs, pins)
    (run / "config.json").unlink()                                               # no record at all
    with pytest.raises(ls.HashMismatch, match="recorded"):
        ls.verify_run_inputs(run, runs, pins)


def test_non_finite_anywhere_is_an_error_never_a_wrong_decision(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    for key in ("B", "D", "s3", "tbv", "tex", "nbr"):
        d = _arrays(np.random.default_rng(8), conds=("noise0.1",))
        d[f"noise0.1_{key}"][17] = np.nan
        with pytest.raises(ls.NonFinite):
            ls.score_item(fz, d, "noise0.1")
    d = _arrays(np.random.default_rng(8), conds=("noise0.1",))
    d["noise0.1_B"][3] = np.inf
    with pytest.raises(ls.NonFinite):
        ls.weights(fz, d, "noise0.1")
    d = _arrays(np.random.default_rng(8), conds=("noise0.1",), with_L=True)
    d["noise0.1_delta"][5] = np.nan
    with pytest.raises(ls.NonFinite, match="delta"):
        ls.score_item(fz, d, "noise0.1")
    d = _arrays(np.random.default_rng(8), conds=("noise0.1",), with_L=True)
    d["noise0.1_deltaL"][5] = np.inf
    with pytest.raises(ls.NonFinite, match="deltaL"):
        ls.score_item(fz, d, "noise0.1", with_L=True)
    with pytest.raises(ls.NonFinite):
        ls.decide(np.full(M, np.nan), np.ones(M))
    run, _ = _run(tmp_path, n=3)                                                 # a poisoned stored item stops the whole run
    d = dict(np.load(run / "arrays" / "item0001.npz"))
    d["jpeg10_tbv"][0] = np.nan
    np.savez(run / "arrays" / "item0001.npz", **d)
    with pytest.raises(ls.NonFinite):
        ls.score_run(run, fz)


def test_cli_end_to_end_and_refusal(tmp_path, monkeypatch):
    fz_dir, code, _ = _make_frozen(tmp_path)
    run, _ = _run(tmp_path, n=3)
    runs, in_pins = _inputs(tmp_path, run)
    monkeypatch.setattr(common, "RUNS", runs)
    spec = json.loads((fz_dir / "spec.json").read_text())
    pins_ok = tmp_path / "pins_ok.json"
    pins_ok.write_text(json.dumps(dict(in_pins, code_sha256=spec["code_sha256"])))       # the A6.0 item 2 row for this fake object
    base = ["--run-id", "P2-LRF-L1", "--frozen-dir", str(fz_dir), "--code-dir", str(code)]
    assert ls.main(base) == 2                                                    # the default pins are the r1 table: this fake object and its inputs do not match
    assert ls.main(base + ["--pins", str(pins_ok)]) == 0 and (run / "predictions.jsonl").exists()
    meta = json.loads((run / "lrf_score_meta.json").read_text())
    assert meta["hashes"]["codebook_sha256"] == in_pins["codebook_sha256"] and meta["hashes"]["di_sha256"] == in_pins["di_sha256"] and "exp_p2/gate/lrf_score.py" in meta["hashes"]["entry_points"]
    assert ls.main(base + ["--pins", str(pins_ok)]) == 2                         # exists
    bad = tmp_path / "pins_bad.json"
    bad.write_text(json.dumps(dict(in_pins, code_sha256=spec["code_sha256"], model_sha256="1" * 64)))
    assert ls.main(base + ["--pins", str(bad), "--force"]) == 2                  # hash mismatch: refuses
    assert ls.main(["--run-id", "P2-LRF-L1", "--frozen-dir", str(tmp_path / "nope"), "--code-dir", str(code), "--pins", str(pins_ok), "--force"]) == 2
    d = dict(np.load(run / "arrays" / "item0002.npz"))                           # a NaN in a stored array: the CLI stops (exit 2), nothing is written
    d["noise0.1_nbr"][4] = np.nan
    np.savez(run / "arrays" / "item0002.npz", **d)
    before = (run / "predictions.jsonl").read_bytes()
    assert ls.main(base + ["--pins", str(pins_ok), "--force"]) == 2 and (run / "predictions.jsonl").read_bytes() == before


def test_crosscheck_is_none_when_the_freeze_module_is_not_importable(tmp_path):
    fz_dir, code, _ = _make_frozen(tmp_path)
    fz = ls.load_frozen(fz_dir, code)
    d = _arrays(np.random.default_rng(5), conds=("clean",))
    res = ls.crosscheck(fz, d, "clean")
    assert res is None or res < 1e-9          # None on this branch (lrf.py is committed with the freeze); a small number where the freeze code is importable
