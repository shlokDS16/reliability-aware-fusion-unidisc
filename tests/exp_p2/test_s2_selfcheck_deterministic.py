"""S2 self-check under deterministic cuDNN (diagnosis research/paper2/method/S2-SELFCHECK-DIAG-2026-10-29.md). CPU only; no model, no GPU.
The self-check must see benchmark off / deterministic on, the pass rule (runner.selfcheck_passed, threshold 0.99) must be unchanged, and the production flags must be
restored afterwards, also when the self-check raises, so that no S2 item runs under changed backend settings."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import torch                                                                   # noqa: E402
from exp_p2 import common, run_gate_s2                                         # noqa: E402
from exp_p2.gate import runner                                                 # noqa: E402


class _Rec:
    def __init__(self, fail=False):
        self.seen, self.fail = [], fail

    def selfcheck(self, img, cap):
        self.seen.append((torch.backends.cudnn.benchmark, torch.backends.cudnn.deterministic, cap))
        if self.fail:
            raise RuntimeError("boom")
        return dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=1.0)


@pytest.fixture
def production_flags():
    old = (torch.backends.cudnn.benchmark, torch.backends.cudnn.deterministic)
    torch.backends.cudnn.benchmark, torch.backends.cudnn.deterministic = True, False      # what UniDisc's set_torch_defaults() leaves behind
    yield
    torch.backends.cudnn.benchmark, torch.backends.cudnn.deterministic = old


def test_selfcheck_runs_with_deterministic_cudnn_and_restores_the_flags(production_flags, monkeypatch):
    monkeypatch.setattr(common, "load_image", lambda image_id: f"img{image_id}")
    sc = _Rec()
    out = run_gate_s2.selfcheck_deterministic(sc, [dict(image_id=7, caption="a cat")])
    assert sc.seen == [(False, True, "a cat")]
    assert (torch.backends.cudnn.benchmark, torch.backends.cudnn.deterministic) == (True, False)
    assert runner.selfcheck_passed(out)


def test_flags_are_restored_when_the_selfcheck_raises(production_flags, monkeypatch):
    monkeypatch.setattr(common, "load_image", lambda image_id: None)
    with pytest.raises(RuntimeError):
        run_gate_s2.selfcheck_deterministic(_Rec(fail=True), [dict(image_id=1, caption="x")])
    assert (torch.backends.cudnn.benchmark, torch.backends.cudnn.deterministic) == (True, False)


def test_the_pass_rule_is_unchanged():
    assert runner.selfcheck_passed(dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=0.99))
    assert not runner.selfcheck_passed(dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=0.9853515625))


def test_main_hands_the_deterministic_selfcheck_to_the_runner(monkeypatch):
    seen = {}

    def fake_run_items(**kw):
        seen.update(kw)
        return 0
    monkeypatch.setattr(run_gate_s2, "s2_conditions", lambda runs=None: ["patch"])
    monkeypatch.setattr(run_gate_s2, "plan_items", lambda n, runs=None, m4_run=None: ([dict(idx=0, gid=0, image_id=1, caption="c", neg_caption="d")], {}))
    monkeypatch.setattr(run_gate_s2, "m4_complete_for", lambda *a, **k: dict(rows={}, missing=[], bad_keys=[]))
    monkeypatch.setattr(runner, "run_items", fake_run_items)
    monkeypatch.setattr(runner, "guards_from_args", lambda a: None)
    assert run_gate_s2.main(["--n", "1"], load=lambda: None) == 0
    assert seen["selfcheck"] is run_gate_s2.selfcheck_deterministic
    assert seen["process"] is run_gate_s2.process                                          # the item function is untouched
