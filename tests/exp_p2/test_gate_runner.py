"""Resume / append logic of the shared runner, the HOLD check at run level, guards, and the gate driver's refusal to start. CPU only, no model, no GPU, no real runs/."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import gate_driver, guards, hold, runner                   # noqa: E402


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Temporary runs/ root, no CUDA, light init_run (no pip freeze)."""
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "_cuda", lambda: None)

    def init_run(run_id, config):
        d = tmp_path / run_id
        d.mkdir(parents=True, exist_ok=True)
        if not (d / "config.json").exists():
            (d / "config.json").write_text(json.dumps(dict(config, run_id=run_id)))
        return d
    monkeypatch.setattr(common, "init_run", init_run)
    return tmp_path


def _items(n=10):
    return [dict(idx=i, v=i) for i in range(n)]


def _process(sc, it, ctx):
    return dict(value=it["v"] * 2), dict(a=np.arange(3) + it["v"])


def _run(env, limit=None, n=10, run_id="P2-GATE-T", process=_process, **kw):
    loaded = []
    rc = runner.run_items(run_id=run_id, cfg=dict(n_items=n), load=lambda: loaded.append(1) or object(), get_items=lambda sc, run: _items(n), process=process,
                          soft_minutes=12.5, duty=1.0, limit=limit, **kw)
    return rc, loaded


def _rows(env, run_id="P2-GATE-T"):
    return common.read_jsonl(env / run_id / "items.jsonl")


def test_resume_appends_each_item_once_and_arrays_precede_rows(env):
    rc, _ = _run(env, limit=4)
    assert rc == runner.EXIT_MORE_WORK and [r["idx"] for r in _rows(env)] == [0, 1, 2, 3]
    rc, _ = _run(env)
    assert rc == runner.EXIT_DONE
    rows = _rows(env)
    assert [r["idx"] for r in rows] == list(range(10)) and all(r["value"] == 2 * r["idx"] for r in rows)
    for i in range(10):
        assert np.load(env / "P2-GATE-T" / "arrays" / f"item{i:04d}.npz")["a"].tolist() == [i, i + 1, i + 2]
    rc, loaded = _run(env)
    assert rc == runner.EXIT_DONE and not loaded                              # complete: returns before loading the model
    ev = [e["event"] for e in common.read_jsonl(env / "P2-GATE-T" / "chunks.jsonl")]
    assert ev == ["chunk_start", "chunk_start", "complete"]


def test_torn_last_row_is_repaired_and_the_item_is_redone_without_losing_the_next_row(env):
    _run(env, limit=3)
    p = env / "P2-GATE-T" / "items.jsonl"
    with open(p, "a", encoding="utf8") as fh:
        fh.write('{"idx": 3, "value": ')                                       # hard kill in the middle of a row (no newline)
    assert len(_rows(env)) == 3
    rc, _ = _run(env)
    rows = _rows(env)
    assert rc == runner.EXIT_DONE and [r["idx"] for r in rows] == list(range(10))     # item 3 redone, and the row after the torn line was not glued to it
    assert len({r["idx"] for r in rows}) == 10


def test_repair_torn_tail_is_a_noop_on_clean_files(tmp_path):
    p = tmp_path / "x.jsonl"
    assert runner.repair_torn_tail(p) is False
    p.write_text('{"a": 1}\n')
    assert runner.repair_torn_tail(p) is False and p.read_text() == '{"a": 1}\n'
    p.write_text('{"a": 1}\n{"b"')
    assert runner.repair_torn_tail(p) is True and p.read_text().endswith('{"b"\n')


def test_arrays_without_a_row_are_overwritten_on_resume(env):
    (env / "P2-GATE-T" / "arrays").mkdir(parents=True)
    np.savez(env / "P2-GATE-T" / "arrays" / "item0002.npz", a=np.array([99]))      # crash after arrays, before the row
    _run(env)
    assert np.load(env / "P2-GATE-T" / "arrays" / "item0002.npz")["a"].tolist() == [2, 3, 4]
    assert len(_rows(env)) == 10


def test_hold_stops_before_loading_anything(env):
    (env / "P2-PROBE-02").mkdir()
    (env / "P2-PROBE-02" / "HOLD.txt").write_text("on hold")
    called = []
    rc = runner.run_items(run_id="P2-GATE-T", cfg=dict(n_items=3), load=lambda: called.append("load"), get_items=lambda sc, r: called.append("items") or [],
                          process=lambda *a: called.append("process"), soft_minutes=12.5, duty=1.0, limit=None)
    assert rc == hold.EXIT_HOLD == 7 and called == []
    assert not (env / "P2-GATE-T").exists()                                       # not even a run directory was created
    assert (env / "P2-PROBE-02" / "HOLD.txt").exists()                            # never deleted


def test_run_level_hold_file_also_stops(env):
    (env / "P2-GATE-T").mkdir()
    (env / "P2-GATE-T" / "HOLD.txt").write_text("x")
    rc, loaded = _run(env)
    assert rc == 7 and not loaded


def test_soft_deadline_returns_more_work_before_any_item(env):
    rc = runner.run_items(run_id="P2-GATE-T", cfg=dict(n_items=10), load=lambda: object(), get_items=lambda sc, r: _items(), process=_process, soft_minutes=0.0, duty=1.0)
    assert rc == runner.EXIT_MORE_WORK and _rows(env) == []
    ev = common.read_jsonl(env / "P2-GATE-T" / "chunks.jsonl")
    assert ev[-1]["event"] == "soft_deadline"


def test_guard_stop_leaves_no_row_and_is_logged(env):
    g = guards.Guards(used_fn=lambda: 99999.0, ac_fn=lambda: True)
    rc, _ = _run(env, guards=g)
    assert rc == runner.EXIT_GUARD == 76 and _rows(env) == []
    assert common.read_jsonl(env / "P2-GATE-T" / "chunks.jsonl")[-1]["event"] == "guard_stop"


def test_slow_item_guard_stops_after_the_item_is_committed(env):
    times = iter([1.0, 1.0, 1.0, 50.0])
    g = guards.Guards(used_fn=lambda: 100.0, ac_fn=lambda: True)
    orig = g.after_item
    g.after_item = lambda busy: orig(next(times))
    rc, _ = _run(env, guards=g)
    assert rc == runner.EXIT_GUARD and len(_rows(env)) == 4                  # the slow item itself is kept; the run stops after it
    assert "slow_item" in common.read_jsonl(env / "P2-GATE-T" / "chunks.jsonl")[-1]["reason"]


def test_failed_item_is_logged_and_reraised_without_a_row(env):
    def bad(sc, it, ctx):
        if it["idx"] == 2:
            raise ValueError("boom")
        return _process(sc, it, ctx)
    with pytest.raises(ValueError):
        _run(env, process=bad)
    assert [r["idx"] for r in _rows(env)] == [0, 1]
    e = common.read_jsonl(env / "P2-GATE-T" / "chunks.jsonl")[-1]
    assert e["event"] == "item_error" and e["idx"] == 2 and "boom" in e["error"]


def test_selfcheck_failure_returns_2(env):
    rc, _ = _run(env, selfcheck=lambda sc, items: dict(ids_equal=False, modality_equal=True, image_tokens_frac_equal=1.0))
    assert rc == runner.EXIT_SELFCHECK == 2 and _rows(env) == []
    rc, _ = _run(env, run_id="P2-GATE-T2", selfcheck=lambda sc, items: dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=1.0))
    assert rc == 0


def test_limit_done_vs_more_work(env):
    rc, _ = _run(env, limit=10)
    assert rc == runner.EXIT_DONE                                              # the limit coincides with the end


def test_counting_proxy_counts_rows():
    from fake_gate import FakeScorer
    sc = runner.Counting(FakeScorer(grid=4))
    st = sc.build([101, 102, 103], np.zeros(16, np.int64))
    import torch
    sc.logits_fn(st)(torch.stack([st["base"]] * 3))
    assert sc.rows == 3 and sc.L_I == 16                                       # attribute delegation


# ------------------------------------------------------------------------------------------------ gate driver
def test_gate_driver_refuses_to_launch_while_on_hold(env, monkeypatch):
    (env / "P2-PROBE-02").mkdir()
    (env / "P2-PROBE-02" / "HOLD.txt").write_text("on hold")

    def no(*a, **k):
        raise AssertionError("must not launch or probe the GPU")
    monkeypatch.setattr(gate_driver.subprocess, "run", no)
    monkeypatch.setattr(gate_driver.driver, "gates_ok", no)
    for st in ("p2", "m1", "m2", "m3", "m4", "m5"):
        assert gate_driver.main(["--stage", st]) == 7
    assert (env / "P2-PROBE-02" / "HOLD.txt").exists()


def test_gate_driver_command_uses_the_diagnosis_guard_settings(tmp_path):
    cmd = gate_driver.build_cmd("exp_p2.run_gate_m4", "P2-GATE-M4", 300, 5.0, 2.5, 0.5, 0, tmp_path, 80.0)
    s = " ".join(cmd)
    assert "gpu_guard.py" in s and "--every 1.0" in s and "--max-temp 80.0" in s and "-m exp_p2.run_gate_m4" in s and "--resume" in s
    assert gate_driver.build_cmd("exp_p2.run_gate_m1", "P2-GATE-M1", 200, 5.0, 2.5, 0.5, 0, tmp_path, 80.0, ["--tbv"])[-1] == "--tbv"


def test_stage_table_matches_the_modules_and_run_ids():
    import importlib
    for st, (mod, rid, n) in gate_driver.STAGES.items():
        m = importlib.import_module(mod)
        if st != "p2":                                                          # run_probe2 predates RUN_ID; its default run id is the argparse default
            assert m.RUN_ID == rid
        if n and hasattr(m, "CONFIG"):
            assert m.CONFIG["n_items"] == n
    import exp_p2.run_probe2 as rp2                                             # the wrapped module, whose item count the p2 stage uses
    assert rp2.CONFIG["n_items"] == 200 and gate_driver.STAGES["p2"][1] == "P2-PROBE-02"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
