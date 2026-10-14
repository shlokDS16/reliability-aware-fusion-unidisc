import json
import time

from exp001 import runtools as RT, gate_driver as GD, rng


def test_atomic_write_and_npz(tmp_path):
    import numpy as np
    RT.atomic_write_json(tmp_path / "a" / "x.json", {"k": 1})
    assert json.loads((tmp_path / "a" / "x.json").read_text())["k"] == 1
    assert not list(tmp_path.rglob("*.tmp"))
    RT.atomic_save_npz(tmp_path / "z.npz", a=np.arange(4))
    assert np.load(tmp_path / "z.npz")["a"].tolist() == [0, 1, 2, 3]


def test_duty_and_deadline():
    d = RT.Duty(0.5)
    t0 = time.time()
    d.after_unit(0.2)
    assert 0.18 <= time.time() - t0 <= 0.5 and abs(d.idle - 0.2) < 1e-9
    assert RT.Deadline(0.0).reached() and not RT.Deadline(10).reached()


def test_stage_complete_reads_log(tmp_path):
    RT.log_jsonl(tmp_path / "stage_log.jsonl", dict(event="unit", t=1))
    assert not GD.stage_complete(tmp_path, 0)
    RT.log_jsonl(tmp_path / "stage_log.jsonl", dict(event="complete", t=100))
    assert GD.stage_complete(tmp_path, 50) and not GD.stage_complete(tmp_path, 200)


def test_rng_streams_disjoint_and_reproducible():
    a = rng.sampler_uniforms("D0", 3, 100)
    assert (a == rng.sampler_uniforms("D0", 3, 100)).all()
    assert not (a == rng.sampler_uniforms("D0", 4, 100)).any()
    assert not (a == rng.sampler_uniforms("D1", 3, 100)).any()
    p = rng.probe_generator("D0", 3, 2, 0).random(100)
    assert not (a == p).any()
    assert (rng.probe_generator("D0", 3, 2, 0).random(5) == rng.probe_generator("D0", 3, 2, 0).random(5)).all()
    assert (rng.probe_generator("D0", 3, 2, 0).random(5) != rng.probe_generator("D0", 3, 6, 0).random(5)).all()
    assert (rng.position_priorities("D0", 3, 10) != a[:10]).all()
