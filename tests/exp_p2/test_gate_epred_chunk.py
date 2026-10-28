"""E-pred fit chunk (SAP AD.3, AB.3 items 5 and 6, A3.6 item 3): the runner on the fake network (4 x 4 token grid), its fences, and the file contract of `epred.load_fit_inputs`.
CPU only; every path is a temp dir; no GPU, no model."""
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import common, run_gate_epred_chunk as chunk, run_gate_m3, run_gate_m4   # noqa: E402
from exp_p2.gate import config, epred, epred_fit, foil, pins, pipeline, ps_freeze, runner         # noqa: E402
from test_gate_runners_fake import _fold, _m4_prereqs, _sc, _write_folds, env           # noqa: E402,F401  (env: the shared fixture)

FAM = [("jpeg", 10), ("noise", 0.1), ("splice", 128)]
KEYS = ["jpeg10", "noise0.1", "splice128"]
N = 4


def _headroom(env, n=N):
    """M2 threshold, family.json (endpoint d), folds.json and a complete M3 run on the fake network for n headroom items."""
    sc = _sc()
    _m4_prereqs(env, sc, FAM)
    ps_freeze.write(env)                                                          # the PS parameters are frozen after M3 / family.json and before the chunk (code audit part 1, M-1)
    items = _fold(n, offset=1000)
    _write_folds(env, cal=[], head=items, test=_fold(3, 2000), test_ext=[])
    rc = runner.run_items(run_id="P2-GATE-M3", cfg=dict(run_gate_m3.CONFIG, n_items=n), load=lambda: sc, get_items=lambda s, r: items, process=run_gate_m3.process,
                          make_ctx=lambda s, run: SimpleNamespace(run=run, fold=items), duty=1.0, soft_minutes=30)
    assert rc == 0
    (env / "P2-GATE-M3" / "effective_n.json").write_text(json.dumps(dict(planned=config.N_HEAD, effective=n, reason="fake: fewer headroom items than the planned 100")), encoding="utf8")     # what a real M3 with exclusions leaves
    return sc, items


def _pre(env, **kw):
    return chunk.check_prereqs(env, allow_unaudited=True, check_git=False, **kw)


def _run_chunk(env, sc, **kw):
    pre = _pre(env)
    items = chunk.get_items(env, pre)
    rc = runner.run_items(run_id=chunk.RUN_ID, cfg=dict(chunk.CONFIG, n_items=len(items)), load=lambda: sc, get_items=lambda s, r: items, process=chunk.process,
                          make_ctx=chunk.make_ctx_factory(pre, env), duty=1.0, soft_minutes=30, **kw)
    return rc, pre, items


# ------------------------------------------------------------------------------------------------ the item, the contract, fidelity to M4
def test_chunk_writes_exactly_the_fit_contract_and_epred_fit_accepts_it(env):
    sc, items = _headroom(env)
    rc, pre, _ = _run_chunk(env, sc)
    fit_dir = env / chunk.RUN_ID
    assert rc == 0 and chunk.RUN_ID == "P2-GATE-EPRED-FIT" and len(common.read_jsonl(fit_dir / "items.jsonl")) == N
    a = np.load(fit_dir / "arrays" / "item0001.npz")
    assert set(a.files) == {"jpeg10_flag", "noise0.1_flag", "splice128_flag", "patch_codes", "patch_delta", "patch_flag", "swap_codes", "swap_delta", "swap_flag"}
    assert all(a[f"{k}_flag"].dtype == bool and a[f"{k}_flag"].shape == (16,) for k in KEYS + ["patch", "swap"])
    assert a["patch_codes"].dtype == np.int16 and a["patch_delta"].dtype == np.float32
    rows = sorted(common.read_jsonl(fit_dir / "items.jsonl"), key=lambda r: r["idx"])
    assert [r["idx"] for r in rows] == list(range(N)) and set(rows[0]["cells"]) == set(KEYS) | {"patch", "swap"}
    assert rows[1]["n_rows"] == 2 + 8 * 5 and rows[2]["n_rows"] == 42           # 2 caption passes + 8 B-passes for each of 3 P cells and 2 PS cells (warm null caches); no encode, no image
    family = json.loads((env / "P2-GATE-M3" / "family.json").read_text())
    tokens, flags, absent, files = epred.load_fit_inputs(env / "P2-GATE-M3", fit_dir, family, n_expected=N)
    assert set(tokens) == set(epred_fit.CELLS) and absent == {} and len(files) == 2 * N
    fit = epred_fit.epred_fit(tokens, flags, n_boot=100, absent=absent)
    assert set(fit["cells"]) | set(fit["absent"]) == set(epred_fit.CELLS)
    cfg = json.loads((fit_dir / "config.json").read_text())
    assert cfg["no_decision_depends_on_this_run"] is True and cfg["stage"] == "EPRED-FIT"


def test_chunk_loads_no_image_and_runs_no_encode(env, monkeypatch):
    sc, items = _headroom(env)

    def boom(*a, **k):
        raise AssertionError("the fit chunk must not load an image or encode")
    monkeypatch.setattr(common, "load_image", boom)
    sc._sc.encode = boom
    rc, _, _ = _run_chunk(env, sc)
    assert rc == 0


def test_flags_equal_the_flags_m4_procedure_gives_on_the_same_codes(env):
    sc, items = _headroom(env)
    rc, pre, _ = _run_chunk(env, sc)
    assert rc == 0
    thr, family, eps0 = run_gate_m4.load_prereqs(env)
    m4ctx = SimpleNamespace(run=env / "P2-GATE-M4x", dcache=pipeline.dcache_for(), thr=thr, family=family, eps0=eps0, fold=items, grid=4, patch=2, codebook=None, tbv=False,
                            denoise_for=tuple(config.DENOISE_FOR), sanity=("patch", "swap"))
    for it in items:
        row, m4 = run_gate_m4.process(sc, it, m4ctx)
        a = np.load(env / chunk.RUN_ID / "arrays" / f"item{it['idx']:04d}.npz")
        for name in KEYS + ["patch", "swap"]:
            assert np.array_equal(a[f"{name}_flag"], m4[f"{name}_flag0.05"]), (it["idx"], name)       # same codes, same jitter condition index, same groups: the same flags
        for name in ("patch", "swap"):
            assert np.array_equal(a[f"{name}_codes"], m4[f"{name}_codes"]) and np.array_equal(a[f"{name}_delta"], m4[f"{name}_delta"])
        ci = {n: i for i, n in enumerate(row["conds"])}
        assert chunk.condition_indices(family) == ci                                                  # the jitter condition index of every cell is M4's


def test_condition_indices_follow_the_m4_order_for_other_families_and_sanity_sets():
    assert chunk.condition_indices([("jpeg", 10), ("noise", 0.1), ("splice", 128)]) == {"clean": 0, "jpeg10": 1, "jpeg10_dn": 2, "noise0.1": 3, "noise0.1_dn": 4, "splice128": 5, "patch": 6, "swap": 7}
    assert chunk.condition_indices([("splice", 192)], sanity=("patch",)) == {"clean": 0, "splice192": 1, "patch": 2}
    assert chunk.condition_indices([("noise", 0.2), ("splice", 128)], sanity=("swap",)) == {"clean": 0, "noise0.2": 1, "noise0.2_dn": 2, "splice128": 3, "swap": 4}


def test_a_ps_cell_that_is_not_run_is_absent_and_counted_in_the_fit(env):
    sc, items = _headroom(env)
    pre = _pre(env)
    its = chunk.get_items(env, pre)
    rc = runner.run_items(run_id=chunk.RUN_ID, cfg=dict(chunk.CONFIG, n_items=N), load=lambda: sc, get_items=lambda s, r: its, process=chunk.process,
                          make_ctx=chunk.make_ctx_factory(pre, env, sanity=("patch",)), duty=1.0, soft_minutes=30)
    assert rc == 0
    a = np.load(env / chunk.RUN_ID / "arrays" / "item0000.npz")
    assert "swap_flag" not in a.files and "patch_flag" in a.files
    family = json.loads((env / "P2-GATE-M3" / "family.json").read_text())
    tokens, flags, absent, _ = epred.load_fit_inputs(env / "P2-GATE-M3", env / chunk.RUN_ID, family, n_expected=N)
    assert "PS2" in absent and "PS1" in tokens


def test_resume_after_a_soft_stop_redoes_nothing_and_matches_a_single_run(env):
    sc, items = _headroom(env)
    pre = _pre(env)
    its = chunk.get_items(env, pre)
    kw = dict(run_id=chunk.RUN_ID, cfg=dict(chunk.CONFIG, n_items=N), load=lambda: sc, get_items=lambda s, r: its, process=chunk.process, make_ctx=chunk.make_ctx_factory(pre, env), duty=1.0, soft_minutes=30)
    assert runner.run_items(limit=2, **kw) == runner.EXIT_MORE_WORK
    assert runner.run_items(**kw) == 0
    rows = common.read_jsonl(env / chunk.RUN_ID / "items.jsonl")
    assert sorted(r["idx"] for r in rows) == list(range(N))
    split = {i: np.load(env / chunk.RUN_ID / "arrays" / f"item{i:04d}.npz")["patch_flag"].copy() for i in range(N)}
    import shutil
    shutil.rmtree(env / chunk.RUN_ID)
    assert runner.run_items(**kw) == 0
    for i in range(N):
        assert np.array_equal(split[i], np.load(env / chunk.RUN_ID / "arrays" / f"item{i:04d}.npz")["patch_flag"])


# ------------------------------------------------------------------------------------------------ the fences of AB.3 items 5 and 6
def test_audit_record_is_required_and_hashed(env, tmp_path):
    _headroom(env)
    with pytest.raises(chunk.Refusal, match="audit-record") as e:
        chunk.check_prereqs(env, check_git=False)
    assert e.value.code == 2
    with pytest.raises(chunk.Refusal, match="does not exist"):
        chunk.check_prereqs(env, audit_record=str(tmp_path / "nope.md"), check_git=False)
    rec = tmp_path / "audit.md"
    rec.write_text("gate-auditor: fit code PASS", encoding="utf8")
    pre = chunk.check_prereqs(env, audit_record=str(rec), check_git=False)
    assert pre["audit"]["sha256"] == epred.sha256_file(rec)["sha256"] and pre["n_m3"] == N


def test_refuses_once_an_m4_item_or_the_frozen_file_exists(env):
    _headroom(env)
    (env / "P2-GATE-M4").mkdir()
    (env / "P2-GATE-M4" / "items.jsonl").write_text("")                            # an empty file is not an item
    assert _pre(env)["n_m3"] == N
    (env / "P2-GATE-M4" / "items.jsonl").write_text(json.dumps(dict(idx=0)) + "\n")
    with pytest.raises(chunk.Refusal, match="precede the first M4 item") as e:
        _pre(env)
    assert e.value.code == 3
    (env / "P2-GATE-M4" / "items.jsonl").write_text("")
    (env / chunk.RUN_ID).mkdir(exist_ok=True)
    (env / chunk.RUN_ID / epred.FROZEN_NAME).write_text("{}")
    with pytest.raises(chunk.Refusal, match="frozen") as e:
        _pre(env)
    assert e.value.code == 3


def test_refuses_an_incomplete_m3_or_missing_prerequisites(env):
    _headroom(env)
    p = env / "P2-GATE-M3" / "items.jsonl"
    lines = p.read_text().splitlines()
    p.write_text("\n".join(lines[:-1]) + "\n")
    with pytest.raises(chunk.Refusal, match="COMPLETE M3"):
        _pre(env)
    (env / "P2-GATE-M2" / "threshold.json").unlink()
    with pytest.raises(FileNotFoundError, match="fit_threshold"):
        _pre(env)


def test_uncommitted_fit_code_or_family_json_stops_the_chunk(env, monkeypatch, tmp_path):
    _headroom(env)
    rec = tmp_path / "audit.md"
    rec.write_text("x", encoding="utf8")
    monkeypatch.setattr(foil, "require_committed", lambda p, repo=None: None)
    monkeypatch.setattr(epred, "git_status_lines", lambda paths, repo=None: [" M exp_p2/gate/theory.py"])
    with pytest.raises(chunk.Refusal, match="committed before the fit chunk") as e:
        chunk.check_prereqs(env, audit_record=str(rec))
    assert e.value.code == pins.EXIT_DIRTY == 11
    pre = chunk.check_prereqs(env, audit_record=str(rec), allow_dirty=True)               # recorded, not hidden
    assert pre["dirty"] == [" M exp_p2/gate/theory.py"]

    def not_committed(p, repo=None):
        raise RuntimeError("runs/P2-GATE-M3/family.json is not tracked by git")
    monkeypatch.setattr(foil, "require_committed", not_committed)
    with pytest.raises(chunk.Refusal, match="family.json must be committed") as e:
        chunk.check_prereqs(env, audit_record=str(rec))
    assert e.value.code == 2


def test_items_must_match_folds_and_m3_arrays_must_exist(env):
    sc, items = _headroom(env)
    pre = _pre(env)
    bad = json.loads((env / "P2-GATE-FOLDS" / "folds.json").read_text())
    bad["head"][1]["gid"] += 1
    with pytest.raises(chunk.Refusal, match="does not match folds.json"):
        chunk.get_items(env, pre, bad)
    (env / "P2-GATE-M3" / "arrays" / "item0002.npz").unlink()
    with pytest.raises(chunk.Refusal, match="missing"):
        chunk.get_items(env, pre)


def _boom(*a, **k):
    raise AssertionError("must not load a model or start the loop")


def test_main_refuses_before_touching_any_model_without_prerequisites(env, monkeypatch):
    monkeypatch.setattr(runner, "run_items", _boom)
    assert chunk.main(["--allow-unaudited"]) == 2                                          # no threshold / family / M3
    with pytest.raises(SystemExit):
        chunk.main(["--sanity-typo"])


def test_main_refuses_before_touching_any_model_when_a_fence_is_not_met(env, monkeypatch):
    _headroom(env)
    monkeypatch.setattr(runner, "run_items", _boom)
    assert chunk.main([]) == 2                                                             # no --audit-record (and, in a temp dir, family.json cannot be shown to be committed)
    (env / "P2-GATE-M4").mkdir()
    (env / "P2-GATE-M4" / "items.jsonl").write_text(json.dumps(dict(idx=0)) + "\n")
    monkeypatch.setattr(foil, "require_committed", lambda p, repo=None: None)
    monkeypatch.setattr(epred, "git_status_lines", lambda paths, repo=None: [])
    assert chunk.main(["--allow-unaudited"]) == 3


def test_main_runs_the_loop_when_every_fence_is_met(env, monkeypatch, tmp_path):
    sc, items = _headroom(env)
    rec = tmp_path / "audit.md"
    rec.write_text("PASS", encoding="utf8")
    monkeypatch.setattr(foil, "require_committed", lambda p, repo=None: None)
    monkeypatch.setattr(epred, "git_status_lines", lambda paths, repo=None: [])
    seen = {}

    def fake_run_items(**kw):
        seen.update(kw)
        return 0
    monkeypatch.setattr(runner, "run_items", fake_run_items)
    assert chunk.main(["--audit-record", str(rec), "--limit", "2"]) == 0
    assert seen["run_id"] == "P2-GATE-EPRED-FIT" and seen["limit"] == 2 and seen["cfg"]["audit_record"]["path"] == str(rec) and seen["cfg"]["unaudited"] is False
    assert seen["cfg"]["n_items"] == 100 and seen["cfg"]["family"] == KEYS and "fit_code" in seen["cfg"] and seen["watchdog_factory"] is runner.default_watchdog and seen["guards"] is not None


def test_no_decision_code_reads_the_fit_run_directory():
    """AB.3 item 6: the output directory is read only by the sign function and the final E-pred table (epred.py). Static check over the code that makes decisions or analyses other families."""
    must_not = ["gate/headroom.py", "gate/analysis_m4.py", "run_gate_m4.py", "run_gate_m3.py", "run_gate_m5.py", "gate/analysis_s2.py", "run_gate_s2.py", "gate/analysis_foil.py", "gate/foil.py",
                "run_gate_foil.py", "gate/analysis_omni.py", "run_gate_omni_r.py", "gate/suite.py", "run_gate_suite.py", "gate/fit_threshold.py", "gate/edec.py", "gate/folds.py", "gate/config.py"]
    for rel in must_not:
        src = (ROOT / "exp_p2" / rel).read_text(encoding="utf8")
        assert not re.search(r"P2-GATE-EPRED-FIT|epred\.FIT_RUN_ID|epred_frozen|run_gate_epred_chunk", src), rel
