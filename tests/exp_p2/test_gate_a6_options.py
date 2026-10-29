"""A6.11 runner options of run_gate_m4 (--neg-len, --extra-cells, --caption-slot-len, --gate-true-layout) and the LRF re-score stage (run_gate_lrf_rescore). CPU, fake scorer (4 x 4 token map), temp dirs.
Central properties: with every option absent the stage is byte-identical to the pre-A6 code (parity against the module as committed before A6); the options add arrays and rows without moving any existing one."""
import importlib.util
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

from fake_gate import fake_image                                              # noqa: E402
from test_gate_runners_fake import _fold, _m4_prereqs, _sc, _write_folds, env  # noqa: E402,F401  (env is a fixture)
from exp_p2 import common, run_gate_lrf_rescore as rescore, run_gate_m4 as m4  # noqa: E402
from exp_p2.gate import corruptions, runner, suite                            # noqa: E402

BASE_REV = "89fb513a"          # the merge commit before the A6 options: exp_p2/run_gate_m4.py as it was


def _ctx(env, sc, *, family=None, **kw):
    fam = [("jpeg", 10), ("noise", 0.1), ("splice", 128)]
    _m4_prereqs(env, sc, fam)
    items = _fold(4, offset=2000)
    _write_folds(env, test=items)
    (env / "P2-GATE-M4").mkdir(exist_ok=True)
    a = SimpleNamespace(tbv="on", denoise_for="jpeg,noise", **kw)
    ctx = m4.make_ctx_factory(a, env)(sc, env / "P2-GATE-M4")
    if family is not None:
        ctx.family = family
    return items, ctx


def _eq(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return np.array_equal(a, b, equal_nan=a.dtype.kind == 'f')


def _same(a, b):
    assert set(a) == set(b)
    for k in a:
        assert a[k].dtype == b[k].dtype and _eq(a[k], b[k]), k


def _j(x):
    return json.dumps(x, sort_keys=True)          # NaN-safe equality of nested rows


def _rows_wo(row):
    return {k: v for k, v in row.items() if k != "n_rows"}


@pytest.fixture
def fake_corruptions(monkeypatch):
    """imagecorruptions is not needed: a deterministic stand-in with the same signature, and a package stub."""
    def apply(name, severity, pil, seed, ic=None):
        a = np.asarray(pil.convert("RGB")).astype(np.int16)
        rng = np.random.default_rng(seed)
        return __import__("PIL.Image", fromlist=["Image"]).fromarray(np.clip(a + rng.integers(-40, 40, a.shape), 0, 255).astype(np.uint8))
    monkeypatch.setattr(suite, "apply_corruption", apply)
    monkeypatch.setattr(suite, "load_package", lambda: "stub-package")
    return apply


# ------------------------------------------------------------------------------------------------ defaults are the old ones
def _load_base_module():
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE_REV}:exp_p2/run_gate_m4.py"], capture_output=True)
    if r.returncode != 0:
        pytest.skip("pre-A6 revision not available")
    spec = importlib.util.spec_from_loader("run_gate_m4_base", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(ROOT / "exp_p2" / "run_gate_m4.py")
    exec(compile(r.stdout.decode("utf8"), "run_gate_m4_base.py", "exec"), mod.__dict__)
    return mod


def test_with_every_option_absent_the_item_is_byte_identical_to_the_pre_a6_code(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    base = _load_base_module()
    m4.process(sc, items[0], ctx)                                              # warm the null cache
    row, arrays = m4.process(sc, items[1], ctx)
    row0, arrays0 = base.process(sc, items[1], ctx)
    assert _j(row) == _j(row0) and _same(arrays, arrays0) is None
    assert not any(k.endswith("deltaL") for k in arrays) and "imgL" not in row["conds"]["clean"] and "slot_len" not in row


def test_the_config_of_a_default_run_has_no_a6_keys(env, monkeypatch):
    seen = {}
    monkeypatch.setattr(runner, "run_items", lambda **kw: seen.setdefault("cfg", kw["cfg"]) and 0)
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    monkeypatch.setattr(m4.pipeline, "require_frozen", lambda *a, **k: None)
    monkeypatch.setattr(m4.ps_freeze, "check", lambda *a, **k: dict(params=dict(denoise_for=["jpeg", "noise"]), code_commit="x"))
    monkeypatch.setattr(m4.ps_freeze, "sha256", lambda *a, **k: "x")
    (env / "P2-GATE-M3" / "family.json").write_text(json.dumps(dict(endpoint="d", n_rule=dict(rule="R1", test_fold=300), family=[dict(corruption="jpeg", severity=10, key="jpeg10")])))
    m4.main(["--n", "300"])
    cfg = seen["cfg"]
    assert not ({"neg_len", "extra_cells", "caption_slot_len", "gate_true_layout"} & set(cfg))
    seen.clear()
    m4.main(["--n", "300", "--neg-len", "--caption-slot-len", "13", "--extra-cells", "shot_noise3"])
    assert seen["cfg"]["neg_len"] is True and seen["cfg"]["caption_slot_len"] == 13 and seen["cfg"]["extra_cells"] == "shot_noise3"


def test_option_validation():
    assert m4.parse_extra_cells("shot_noise3, impulse_noise3,shot_noise3") == (("shot_noise3", "shot_noise", 3), ("impulse_noise3", "impulse_noise", 3))
    assert m4.parse_extra_cells("") == () and m4.parse_extra_cells(None) == ()
    for bad in ("fog3", "shot_noise", "shot_noise9", "shot_noise0"):
        with pytest.raises(ValueError):
            m4.parse_extra_cells(bad)
    assert m4.extra_cell_index("shot_noise", 3) != m4.extra_cell_index("impulse_noise", 3) and m4.extra_cell_index("shot_noise", 3) >= 1000
    assert m4.slot_tokens(13) == [0] * 13
    assert m4.main(["--gate-true-layout"]) == 2 and m4.main(["--caption-slot-len", "0"]) == 2 and m4.main(["--extra-cells", "fog3"]) == 2      # refuses before touching anything


def test_the_fold_may_hold_more_than_500_items(env):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    items = _fold(7, offset=2000)
    _write_folds(env, test=items, cal=[], head=[], test_ext=[])
    (env / "P2-GATE-M4").mkdir(exist_ok=True)
    ctx = m4.make_ctx_factory(SimpleNamespace(tbv="off", denoise_for=""), env)(sc, env / "P2-GATE-M4")
    assert len(ctx.fold) == 7
    big = _fold(520, offset=8000)
    _write_folds(env, test=big, cal=[], head=[], test_ext=[])
    ctx = m4.make_ctx_factory(SimpleNamespace(tbv="off", denoise_for=""), env)(sc, env / "P2-GATE-M4")
    assert len(ctx.fold) == 520 and ctx.fold[519]["idx"] == 519               # the 520 items of the A6 fold are all donors' candidates; a 500-item fold is cut exactly as before


# ------------------------------------------------------------------------------------------------ --neg-len
def test_neg_len_adds_one_pass_and_deltaL_without_moving_anything_else(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    for it in items:
        it["neg_caption_len"] = it["neg_caption"]                              # same text as the primary negative -> deltaL == delta
    m4.process(sc, items[0], ctx)
    r0 = sc.rows
    row, arrays = m4.process(sc, items[1], ctx)
    n_plain = sc.rows - r0
    ctx.neg_len = True
    r1 = sc.rows
    rowL, arraysL = m4.process(sc, items[1], ctx)
    assert sc.rows - r1 == n_plain + 1 and rowL["n_tok_neg_len"] == 6
    for k in arrays:
        assert _eq(arrays[k], arraysL[k]), k
    names = list(rowL["conds"])
    assert {f"{n}_deltaL" for n in names} == {k for k in arraysL if k.endswith("_deltaL")}      # every condition, denoised and token-level ones included
    for n in names:
        assert _eq(arraysL[f"{n}_deltaL"], arraysL[f"{n}_delta"])
    assert rowL["conds"]["clean"]["imgL"]["none"] == rowL["conds"]["clean"]["img"]["none"] and set(rowL["conds"]["jpeg10_dn"]["imgL"]) == {"denoised"}
    assert {k: v for k, v in rowL.items() if k not in ("n_rows", "neg_caption_len", "n_tok_neg_len")} != {} and "imgL" not in row["conds"]["clean"]
    # a different negative gives a different delta, computed from its own Lambda
    items[1]["neg_caption_len"] = items[0]["caption"]
    row2, arrays2 = m4.process(sc, items[1], ctx)
    assert not _eq(arrays2["clean_deltaL"], arrays2["clean_delta"])
    del items[1]["neg_caption_len"]
    with pytest.raises(ValueError, match="neg_caption_len"):
        m4.process(sc, items[1], ctx)


# ------------------------------------------------------------------------------------------------ --extra-cells
def test_extra_cells_leave_every_existing_cell_byte_identical_and_match_the_ordinary_pixel_path(env, fake_corruptions, monkeypatch):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    m4.process(sc, items[0], ctx)
    row, arrays = m4.process(sc, items[1], ctx)
    ctx.extra_cells, ctx.ic = m4.parse_extra_cells("shot_noise3,impulse_noise3,speckle_noise3"), "stub-package"
    rowX, arraysX = m4.process(sc, items[1], ctx)
    assert list(rowX["conds"])[-3:] == ["shot_noise3", "impulse_noise3", "speckle_noise3"] and list(rowX["conds"])[:-3] == list(row["conds"])
    _same(arrays, {k: v for k, v in arraysX.items() if k in arrays})           # existing cells: byte-identical (arrays) ...
    assert all(_j(rowX["conds"][k]) == _j(row["conds"][k]) for k in row["conds"])      # ... and rows
    cell = {k for k in arraysX if k.startswith("shot_noise3_")}
    assert cell == {f"shot_noise3_{s}" for s in ("codes", "z", "delta", "B", "D", "s3", "tex", "nbr", "tbv", "flag0.05", "flag0.01", "flag0.1")}      # exactly the arrays of a pixel condition
    assert rowX["conds"]["shot_noise3"]["txt"] == {}                           # no text-direction passes for the extra cells
    # parity: the same pixel image through the ordinary family path and through the extra-cell path gives equal arrays (same condition index 1)
    seed = suite.corruption_seed(items[1]["gid"], m4.extra_cell_index("shot_noise", 3))
    monkeypatch.setattr(corruptions, "apply_pixel", lambda corr, sev, pil, rng, donor=None: fake_corruptions("shot_noise", 3, pil, seed))
    _, ctxA = _ctx(env, sc, family=[("jpeg", 10)])
    ctxA.sanity, ctxA.denoise_for = (), ()
    _, ctxB = _ctx(env, sc, family=[])
    ctxB.sanity, ctxB.denoise_for, ctxB.extra_cells, ctxB.ic = (), (), m4.parse_extra_cells("shot_noise3"), "stub-package"
    _, aA = m4.process(sc, items[1], ctxA)
    _, aB = m4.process(sc, items[1], ctxB)
    pa = {k[len("jpeg10_"):]: v for k, v in aA.items() if k.startswith("jpeg10_")}
    pb = {k[len("shot_noise3_"):]: v for k, v in aB.items() if k.startswith("shot_noise3_")}
    assert len(pa) == 12
    _same(pa, pb)
    _same({k: v for k, v in aA.items() if k.startswith("clean_")}, {k: v for k, v in aB.items() if k.startswith("clean_")})


# ------------------------------------------------------------------------------------------------ --caption-slot-len
def test_a_fixed_slot_of_the_true_length_changes_nothing_and_content_is_irrelevant(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    m4.process(sc, items[0], ctx)
    row, arrays = m4.process(sc, items[1], ctx)                                # captions have 6 tokens
    ctx.slot_len = 6
    rowS, arraysS = m4.process(sc, items[1], ctx)
    _same(arrays, arraysS)                                                     # PAD slot of the true length: every array identical (the caption is masked in B, D, s3, tbv)
    assert rowS["slot_len"] == 6 and rowS["gate_layout"] == "fixed" and _j(_rows_wo({k: v for k, v in rowS.items() if k not in ("slot_len", "gate_layout")})) == _j(_rows_wo(row))


def test_a_different_slot_moves_the_caption_withheld_scores_only(env):
    sc = _sc()
    items, ctx = _ctx(env, sc)
    m4.process(sc, items[0], ctx)
    row, arrays = m4.process(sc, items[1], ctx)
    ctx.slot_len = 9
    rowS, arraysS = m4.process(sc, items[1], ctx)
    for n in ("clean", "jpeg10", "noise0.1", "splice128"):
        for k in ("codes", "z", "delta", "tex", "nbr"):
            assert _eq(arrays[f"{n}_{k}"], arraysS[f"{n}_{k}"]), (n, k)       # Delta needs the real captions: unchanged
        assert not _eq(arrays[f"{n}_B"], arraysS[f"{n}_B"]) and not _eq(arrays[f"{n}_tbv"], arraysS[f"{n}_tbv"])
        assert not _eq(arrays[f"{n}_D"], arraysS[f"{n}_D"])
    # the slot content and the true caption do not matter: another caption of the same image gives the same fixed-slot scores
    other = dict(items[1], caption="quiet loud bright dark soft hard warm cold", neg_caption=items[2]["caption"])
    _, arraysO = m4.process(sc, other, ctx)
    for n in ("clean", "jpeg10", "noise0.1"):
        for k in ("B", "D", "s3", "tbv", "flag0.05", "tex", "nbr", "codes"):
            assert _eq(arraysS[f"{n}_{k}"], arraysO[f"{n}_{k}"]), (n, k)
    assert not _eq(arraysS["clean_delta"], arraysO["clean_delta"])
    # --gate-true-layout: scores at the fixed slot, flags at the true layout (8 more passes per gated condition)
    rowS, _ = m4.process(sc, items[1], ctx)                                    # warm: the slot-9 null is cached now
    ctx.gate_true = True
    rowT, arraysT = m4.process(sc, items[1], ctx)
    assert rowT["gate_layout"] == "true"
    for n in ("clean", "jpeg10"):
        assert _eq(arraysT[f"{n}_B"], arraysS[f"{n}_B"]) and _eq(arraysT[f"{n}_flag0.05"], arrays[f"{n}_flag0.05"])
    assert rowT["n_rows"] - rowS["n_rows"] == 8 * 5                            # clean, jpeg10, noise0.1, splice128, patch (the bare namespace has no swap)
    with pytest.raises(ValueError, match="caption-slot-len"):
        m4.make_ctx_factory(SimpleNamespace(tbv="off", denoise_for="", gate_true_layout=True), env)(sc, env / "P2-GATE-M4")


# ------------------------------------------------------------------------------------------------ the re-score stage
def _source_run(env, sc, n=3):
    fam = [("jpeg", 10), ("noise", 0.1), ("splice", 128)]
    _m4_prereqs(env, sc, fam)
    items = _fold(n, offset=2000)
    _write_folds(env, test=items)
    a = SimpleNamespace(tbv="on", denoise_for="jpeg,noise")
    rc = runner.run_items(run_id="P2-GATE-M4", cfg=dict(m4.CONFIG, n_items=n), load=lambda: sc, get_items=lambda s, r: items, process=m4.process, make_ctx=m4.make_ctx_factory(a, env), duty=1.0, soft_minutes=30)
    assert rc == 0
    return items


def _rescore(env, sc, slot):
    a = SimpleNamespace(source_run="P2-GATE-M4", slot_len=slot, conds=",".join(rescore.CONDS), family_run="P2-GATE-M3")
    rescore.check_prereqs(a, env)
    items = rescore.source_items(env, "P2-GATE-M4")
    return runner.run_items(run_id=f"LFIX{slot}", cfg=dict(rescore.CONFIG, n_items=len(items)), load=lambda: sc, get_items=lambda s, r: items, process=rescore.process, make_ctx=rescore.make_ctx_factory(a, env),
                            duty=1.0, soft_minutes=30)


def test_rescore_at_the_true_length_reproduces_the_source_and_at_another_length_moves_only_the_scores(env):
    sc = _sc()
    _source_run(env, sc)
    assert _rescore(env, sc, 6) == 0                                           # captions have 6 tokens -> a fixed slot of 6 is the true layout
    for idx in range(3):
        src = dict(np.load(env / "P2-GATE-M4" / "arrays" / f"item{idx:04d}.npz"))
        new = dict(np.load(env / "LFIX6" / "arrays" / f"item{idx:04d}.npz"))
        keys = {f"{n}_{k}" for n in rescore.CONDS for k in ("codes", "z", "delta", "B", "D", "s3", "tbv", "tex", "nbr", "flag0.05", "flag0.01", "flag0.1")}
        assert set(new) == keys                                                # only what LRF needs (and the flags data.load reads)
        _same({k: src[k] for k in keys}, new)                                  # incl. the flags: same condition index, same jitter stream
    rows = common.read_jsonl(env / "LFIX6" / "items.jsonl")
    assert [r["conds"]["noise0.1"]["cond_index"] for r in rows] == [3, 3, 3] and [r["conds"]["splice128"]["cond_index"] for r in rows] == [5, 5, 5]      # noise0.1 follows jpeg10_dn / splice128 follows noise0.1_dn
    assert all(r["n_rows"] == 36 for r in rows[1:]) or all(r["n_rows"] >= 36 for r in rows)                                       # 4 conditions x (8 B + 1 tbv) (+ invariance passes for the first items)
    assert rows[0]["invariance_max_abs_diff"] == 0.0 and all(r["invariance_max_abs_diff"] == 0.0 for r in rows)
    assert _rescore(env, sc, 9) == 0
    src = dict(np.load(env / "P2-GATE-M4" / "arrays" / "item0001.npz"))
    new = dict(np.load(env / "LFIX9" / "arrays" / "item0001.npz"))
    for n in rescore.CONDS:
        for k in ("codes", "z", "delta", "tex", "nbr"):
            assert _eq(src[f"{n}_{k}"], new[f"{n}_{k}"])
        assert not _eq(src[f"{n}_B"], new[f"{n}_B"])


def test_rescore_invariance_helper_returns_zero_on_the_fake(env):
    sc = _sc()
    items = _fold(1, offset=2000)
    pil, codes = m4.pipeline.prep_image(sc, items[0]["image_id"])
    groups = m4.pipeline.item_groups(sc, items[0]["gid"])
    dc = m4.pipeline.dcache_for()
    gs = rescore.fixed_layout_scores(sc, m4.slot_tokens(6), codes, groups, dc)
    inv = rescore.invariance(sc, gs, sc.caption_ids(items[0]["caption"]), sc.caption_ids("a b c d e f g h"), codes, groups, dc, 6)
    assert set(inv) == {f"{t}_{k}" for t in ("pos", "neg") for k in ("B", "D", "s3", "tbv")} and max(inv.values()) == 0.0
    assert rescore.fit_slot([1, 2, 3], 5) == [1, 2, 3, 0, 0] and rescore.fit_slot([1, 2, 3, 4], 2) == [1, 2]


def test_rescore_refuses_without_its_prerequisites(env):
    a = SimpleNamespace(source_run="P2-GATE-M4", slot_len=13, conds="clean", family_run="P2-GATE-M3")
    with pytest.raises(FileNotFoundError):
        rescore.check_prereqs(a, env)
    assert rescore.main(["--source-run", "nope"]) == 2
