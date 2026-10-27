"""U7, the TbV-score (non-finetuned): it must be computed from the RAW logits, never from UniDisc's SUBS output (exactly log p = 0 at every observed token). Fake network only, no weights."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fake_gate import FakeScorer, V_ALL                                       # noqa: E402
from exp_p2.scoring import MASK_ID, IMG_LO, IMG_HI                             # noqa: E402
from exp_p2.gate import baselines, scores                                      # noqa: E402

GRID = 4
CAP = [101, 202, 303, 404, 505]


class SubsFake(FakeScorer):
    """A scorer whose `model.forward` (without return_logits) returns the SUBS output: log p = 0 at the observed token of every UNMASKED position and -inf elsewhere there. Its
    `logits_fn` returns the raw (non-constant) logits, like UniScorer.logits_fn does with return_logits=True."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.subs_calls = 0
        outer = self

        def forward(x, **k):
            outer.subs_calls += 1
            raw = outer.logits_fn(outer._st)(x)
            out = torch.log_softmax(raw.float(), -1)
            vis = x != MASK_ID
            sub = torch.full_like(out, float("-inf"))
            sub.scatter_(-1, x[..., None], 0.0)
            return torch.where(vis[..., None], sub, out)
        self.model = SimpleNamespace(forward=forward)

    def build(self, caption_tok, codes):
        st = super().build(caption_tok, codes)
        self._st = st
        return st


def _setup():
    sc = SubsFake(grid=GRID)
    codes = np.random.default_rng(0).integers(0, 16384, GRID * GRID)
    return sc, codes, sc.build(CAP, codes)


def test_tbv_score_uses_the_raw_logits_and_never_the_subs_output():
    sc, codes, st = _setup()
    v = scores.tbv_score_raw_logits(sc, st)
    x = st["base"].clone()
    x[st["cap_pos"]] = MASK_ID
    raw = sc.logits_fn(st)(x[None])[0]
    expect = torch.log_softmax(raw[st["img_pos"], IMG_LO:IMG_HI].float(), -1).gather(1, torch.as_tensor(codes)[:, None])[:, 0].numpy()
    assert np.allclose(v, expect, atol=1e-6)                                     # same normalisation as GATE: fp32 log-softmax restricted to the image vocabulary
    assert np.ptp(v) > 1e-2 and (v < 0).all() and not np.any(v == 0)             # informative: not constant
    assert sc.subs_calls == 0                                                    # the SUBS path was never touched
    subs = sc.model.forward(x[None])[0, st["img_pos"]].gather(1, (torch.as_tensor(codes) + IMG_LO)[:, None])[:, 0]
    assert torch.all(subs == 0)                                                  # what a SUBS-based score would have returned: exactly 0 everywhere
    assert sc.subs_calls == 1 and v.shape == (GRID * GRID,)


def test_a_subs_style_output_is_rejected_as_degenerate():
    sc, codes, st = _setup()
    base_f = sc.logits_fn

    def subs_like(_st):
        def f(x):
            out = torch.full((x.shape[0], x.shape[1], V_ALL), -1e4)
            out.scatter_(-1, x[..., None], 0.0)                                   # one-hot at the observed token: log-softmax is exactly 0 there
            return out
        return f
    sc.logits_fn = subs_like
    with pytest.raises(RuntimeError, match="SUBS"):
        scores.tbv_score_raw_logits(sc, st)
    sc.logits_fn = base_f
    assert scores.observed_unmasked_logprob is scores.tbv_score_raw_logits       # old name still works


def test_label_and_copy_through_statistic():
    assert baselines.TBV_LABEL == "TbV-score (non-finetuned)"
    sc, codes, st = _setup()
    s = baselines.copy_through_stat(scores.tbv_score_raw_logits(sc, st))
    assert s["label"] == baselines.TBV_LABEL and not s["copy_suspected"]
    assert baselines.copy_through_stat(np.zeros(100))["copy_suspected"]          # the SUBS-like constant would be flagged as copy-through


def _forward_calls():
    """(file, enclosing function, has return_logits=True) of every `.forward(...)` call in exp_p2."""
    out = []
    for f in sorted((ROOT / "exp_p2").rglob("*.py")):
        tree = ast.parse(f.read_text(encoding="utf8"))
        for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            for c in [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "forward"]:
                rl = any(k.arg == "return_logits" and isinstance(k.value, ast.Constant) and k.value.value is True for k in c.keywords)
                out.append((f.relative_to(ROOT).as_posix(), fn.name, rl))
    return sorted(set(out))


def test_no_score_in_exp_p2_reads_subs_output_at_observed_positions():
    calls = _forward_calls()
    # the only model.forward calls: UniScorer.f inside logits_fn (return_logits=True: raw logits) and UniScorer.selfcheck (SUBS reference, compared at MASKED positions only)
    assert ("exp_p2/scoring.py", "f", True) in calls
    others = [c for c in calls if c not in (("exp_p2/scoring.py", "f", True), ("exp_p2/scoring.py", "logits_fn", True))]      # the nested f is also seen as part of logits_fn
    assert others == [("exp_p2/scoring.py", "selfcheck", False)], others
    src = (ROOT / "exp_p2" / "scoring.py").read_text(encoding="utf8")
    sc = src[src.index("def selfcheck"):]
    assert "x[pos] = MASK_ID" in sc and "ref_i = lp_ref[ip, st[\"base\"][ip]]" in sc      # selfcheck reads the SUBS output only at positions it masked first
    # nothing in the gate package or the runners imports the exp001 wrapper whose forward returns the SUBS output (the AST scan above already shows they call no forward)
    for f in list((ROOT / "exp_p2" / "gate").glob("*.py")) + list((ROOT / "exp_p2").glob("run_gate_m*.py")):
        for n in ast.walk(ast.parse(f.read_text(encoding="utf8"))):
            mod = (n.module or "") if isinstance(n, ast.ImportFrom) else " ".join(a.name for a in n.names) if isinstance(n, ast.Import) else ""
            assert "unidisc_net" not in mod, f.name


def test_m1_rows_carry_the_label_and_the_analysis_output_names_the_arm(tmp_path, monkeypatch):
    import json
    from exp_p2 import analyze_gate_m1, common, run_gate_m1
    from exp_p2.gate import pipeline, runner
    monkeypatch.setattr(common, "RUNS", tmp_path)
    sc = runner.Counting(FakeScorer(grid=GRID))
    p2 = tmp_path / "P2-PROBE-02"
    (p2 / "arrays").mkdir(parents=True)
    rng = np.random.default_rng(1)
    d = dict(clean=rng.integers(0, 16384, 16))
    for c in run_gate_m1.NAMES[1:]:
        d[f"{c}_codes"] = rng.integers(0, 16384, 16)
    np.savez(p2 / "arrays" / "item0000.npz", **d)
    (tmp_path / "P2-GATE-M1x").mkdir()
    ctx = run_gate_m1.make_ctx_factory(True, tmp_path)(sc, tmp_path / "P2-GATE-M1x")
    row, arrays = run_gate_m1.process(sc, dict(idx=0, image_id=1, caption="a b c d e"), ctx)
    assert all(v["label"] == "TbV-score (non-finetuned)" for v in row["tbv"].values()) and set(row["tbv"]) == set(run_gate_m1.NAMES[1:])
    assert all(np.ptp(arrays[f"{c}_tbv"]) > 1e-3 for c in run_gate_m1.NAMES[1:])


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
