"""SAP addendum A5.11 item 4: run_gate_m4 builds its conditions and passes its ps_frozen and --denoise-for checks with a one- or two-corruption family (H4 runs only the corruptions that
passed the H3 rule). CPU only; fake scorer."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from test_gate_hardneg_runners import H3, H4, _family, _hard_folds, env              # noqa: E402,F401  (env is a fixture)
from test_gate_runners_fake import _m4_prereqs, _sc                                  # noqa: E402
from exp_p2 import run_gate_m4                                                       # noqa: E402
from exp_p2.gate import foil, ps_freeze, runner                                      # noqa: E402


@pytest.mark.parametrize("fam,names", [((("splice", 128),), ["clean", "splice128", "patch", "swap"]),
                                       ((("jpeg", 10), ("splice", 128)), ["clean", "jpeg10", "jpeg10_dn", "splice128", "patch", "swap"]),
                                       ((("noise", 0.1),), ["clean", "noise0.1", "noise0.1_dn", "patch", "swap"])])
def test_m4_runs_with_a_reduced_family_and_passes_the_ps_frozen_and_denoise_checks(env, monkeypatch, fam, names):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10), ("noise", 0.1), ("splice", 128)])
    path, doc = _hard_folds(env)
    _family(env, H3, "R1", 4, fam=fam)                                                # a 4-item rule so that the fake 4-item H4 file is complete
    ps_freeze.write(env)                                                              # ps_frozen.json lives in the M3 run directory; the frozen denoise_for stays (jpeg, noise)
    monkeypatch.setattr(foil, "require_committed", lambda p, repo=None: None)         # a temp dir is not in git
    captured = {}
    monkeypatch.setattr(runner, "run_items", lambda **kw: captured.update(kw) or 0)
    assert run_gate_m4.main(["--run-id", H4, "--n", "4", "--folds-path", str(path), "--family-run", H3]) == 0       # default --sanity patch,swap and default --denoise-for jpeg,noise
    (env / H4).mkdir(exist_ok=True)
    ctx = captured["make_ctx"](sc, env / H4)
    assert ctx.family == list(fam) and ctx.sanity == ("patch", "swap") and ctx.denoise_for == ("jpeg", "noise")
    row, arrays = run_gate_m4.process(sc, doc["test"][0], ctx)
    assert list(row["conds"]) == names
    for key in names:
        if key in ("clean", "patch", "swap") or key.endswith("_dn"):
            continue
        assert "gate0.05" in row["conds"][key]["img"] and "chg" in row["conds"][key]["img"]          # every family corruption has its gate and changed-code arms
    assert "patch_z" in arrays and "swap_z" in arrays


def test_m4_refuses_a_denoise_for_that_differs_from_the_frozen_one_also_for_family_h(env, monkeypatch):
    sc = _sc()
    _m4_prereqs(env, sc, [("jpeg", 10)])
    path, _ = _hard_folds(env)
    _family(env, H3, "R1", 4, fam=(("splice", 128),))
    ps_freeze.write(env)
    monkeypatch.setattr(foil, "require_committed", lambda p, repo=None: None)
    monkeypatch.setattr(runner, "run_items", lambda **kw: (_ for _ in ()).throw(AssertionError("must not start")))
    assert run_gate_m4.main(["--run-id", H4, "--n", "4", "--folds-path", str(path), "--family-run", H3, "--denoise-for", "jpeg"]) == 2
