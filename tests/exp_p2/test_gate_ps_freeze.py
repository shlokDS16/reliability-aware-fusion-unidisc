"""ps_frozen.json (SAP AD.4, AD.12 step 2, A3.3 item 1, AB.8) and the run-time geometry assertion (AB.7 item 2, A3.3 item 3): code audit A3 part 1, M-1 and M-2. CPU only."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import run_gate_epred_chunk as chunk, run_gate_m4                      # noqa: E402
from exp_p2.gate import config, corruptions, foil, ps_freeze, runner               # noqa: E402
from test_gate_epred_chunk import FAM, _headroom                                    # noqa: E402,F401
from test_gate_runners_fake import _fold, _m4_prereqs, _sc, _write_folds, env       # noqa: E402,F401


def test_the_file_holds_the_frozen_parameters_and_is_write_once(env):
    r = ps_freeze.write(env)
    f = env / "P2-GATE-M3" / "ps_frozen.json"
    assert r["forced"] is False and f.exists()
    doc = json.loads(f.read_text())
    p = doc["params"]
    assert p["grid"] == 32 and p["n_tokens"] == 1024 and p["patch"] == 8 and p["swap_frac"] == 0.15 and p["swap_n_positions"] == 154 and p["vocab"] == 16384
    assert p["token_rng_tag"] == {"patch": 190, "swap": 191} and p["sanity_order"] == ["patch", "swap"] and p["denoise_for"] == ["jpeg", "noise"] and p["seed_gate"] == 20261029
    assert abs(p["patch_share"] - 0.0625) < 1e-12 and doc["kind"] == "ps_frozen" and "code_commit" in doc
    with pytest.raises(FileExistsError):
        ps_freeze.write(env)
    ps_freeze.write(env, force=True)                                                   # logged amendment, old file kept
    assert (env / "P2-GATE-M3" / "amendments.jsonl").exists() and list((env / "P2-GATE-M3").glob("ps_frozen.json.prev-*"))


def test_check_refuses_a_missing_file_a_changed_parameter_and_an_uncommitted_file(env, monkeypatch):
    with pytest.raises(ps_freeze.PsFrozenError, match="ps_freeze write"):
        ps_freeze.check(env, require_commit=False)
    ps_freeze.write(env)
    assert ps_freeze.check(env, require_commit=False)["params"]["patch"] == 8
    monkeypatch.setattr(config, "SWAP_FRAC", 0.2)
    with pytest.raises(ps_freeze.PsFrozenError, match="swap_frac"):
        ps_freeze.check(env, require_commit=False)
    monkeypatch.setattr(config, "SWAP_FRAC", 0.15)
    monkeypatch.setattr(corruptions, "TOKEN_RNG_TAG", {"patch": 190, "swap": 192})
    with pytest.raises(ps_freeze.PsFrozenError, match="token_rng_tag"):
        ps_freeze.check(env, require_commit=False)
    monkeypatch.undo()
    with pytest.raises(ps_freeze.PsFrozenError, match="committed"):                   # a temp dir is not in the repository: not tracked
        ps_freeze.check(env)

    def untracked(p, repo=None):
        raise RuntimeError("ps_frozen.json is not tracked by git")
    monkeypatch.setattr(foil, "require_committed", untracked)
    with pytest.raises(ps_freeze.PsFrozenError, match="before the first M4 item"):
        ps_freeze.check(env)


def test_cli_write_then_check(env, capsys):
    assert ps_freeze.main(["check", "--runs-dir", str(env)]) == 2
    assert ps_freeze.main(["write", "--runs-dir", str(env)]) == 0
    assert ps_freeze.main(["write", "--runs-dir", str(env)]) == 2                      # write-once
    assert "commit runs/P2-GATE-M3/ps_frozen.json" in capsys.readouterr().out


def test_the_geometry_assertion_accepts_32_and_8_and_stops_anything_else(monkeypatch):
    monkeypatch.setattr(ps_freeze, "EXPECTED_GEOMETRY", (config.GRID, config.PATCH))
    assert (config.GRID, config.PATCH) == (32, 8)
    ps_freeze.assert_runtime(32, 8)
    for g, p in ((16, 4), (4, 2), (32, 4), (64, 16)):
        with pytest.raises(ps_freeze.PsGeometryError, match="STOP: token grid"):
            ps_freeze.assert_runtime(g, p)


def test_m4_make_ctx_asserts_the_geometry(env, monkeypatch):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    _write_folds(env, test=_fold(3, offset=2000))
    (env / "P2-GATE-M4").mkdir()
    a = SimpleNamespace(tbv="off", denoise_for="jpeg,noise", sanity="patch,swap")
    assert run_gate_m4.make_ctx_factory(a, env)(sc, env / "P2-GATE-M4").patch == 2        # the fake geometry (4, 2) set by conftest
    monkeypatch.setattr(ps_freeze, "EXPECTED_GEOMETRY", (32, 8))
    with pytest.raises(ps_freeze.PsGeometryError):                                         # the fake 4 x 4 map is not the frozen 32 x 32
        run_gate_m4.make_ctx_factory(a, env)(sc, env / "P2-GATE-M4")


def test_the_chunk_asserts_the_geometry_and_refuses_without_ps_frozen(env, monkeypatch):
    sc, items = _headroom(env)
    (env / "P2-GATE-EPRED-FIT").mkdir(exist_ok=True)
    pre = chunk.check_prereqs(env, allow_unaudited=True, check_git=False)
    assert pre["ps_doc"]["params"]["patch"] == 8
    monkeypatch.setattr(ps_freeze, "EXPECTED_GEOMETRY", (32, 8))
    with pytest.raises(ps_freeze.PsGeometryError):
        chunk.make_ctx_factory(pre, env)(sc, env / "P2-GATE-EPRED-FIT")
    monkeypatch.undo()
    (env / "P2-GATE-M3" / "ps_frozen.json").unlink()
    with pytest.raises(chunk.Refusal, match="ps_frozen.json") as e:
        chunk.check_prereqs(env, allow_unaudited=True, check_git=False)
    assert e.value.code == 2


def test_the_chunk_takes_the_denoise_list_that_fixes_the_condition_indices_from_the_frozen_file(env):
    sc, items = _headroom(env)
    (env / "P2-GATE-EPRED-FIT").mkdir(exist_ok=True)
    pre = chunk.check_prereqs(env, allow_unaudited=True, check_git=False)
    ctx = chunk.make_ctx_factory(pre, env)(sc, env / "P2-GATE-EPRED-FIT")
    assert ctx.ci == chunk.condition_indices(FAM, tuple(pre["ps_doc"]["params"]["denoise_for"]), ("patch", "swap"))
    assert ctx.ci["patch"] == 6 and ctx.ci["swap"] == 7


def test_swap_without_patch_is_not_allowed_so_swap_keeps_its_condition_index():
    assert run_gate_m4.parse_sanity("patch,swap") == ("patch", "swap") and run_gate_m4.parse_sanity("patch") == ("patch",) and run_gate_m4.parse_sanity("") == ()
    with pytest.raises(ValueError, match="swap without patch"):
        run_gate_m4.parse_sanity("swap")
    with pytest.raises(ValueError, match="swap without patch"):
        chunk.parse_sanity("swap")
