"""masked_logprobs semantics with a fake network (CPU torch). Run with pytest, or `python tests/exp_p2/test_scoring.py` in the generation venv."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import torch
except ImportError:                                   # the eval venv may have no torch
    torch = None

if torch is not None:
    from exp_p2.scoring import Spec, masked_logprobs, gather_true, MASK_ID

V, L = 50, 12


def _fake(seen):
    """logits[b, l, v] depend on the position and on the number of visible tokens in the row, so a wrong mask changes the result."""
    def f(x):
        seen.append(x.clone())
        vis = (x != MASK_ID).sum(1).float()                              # [B]
        pos = torch.arange(x.shape[1]).float()
        v = torch.arange(V).float()
        return -0.1 * (v[None, None, :] - (pos[None, :, None] * 3) % V).abs() + 0.01 * vis[:, None, None]
    return f


def _expected(base, spec, vis):
    pos = torch.arange(L).float()
    v = torch.arange(V).float()
    lg = -0.1 * (v[None, :] - (pos[:, None] * 3) % V).abs() + 0.01 * vis
    return torch.log_softmax(lg[spec.pos, spec.lo:spec.hi].float(), dim=-1)


def test_masks_and_values_and_order():
    if torch is None:
        return
    base = torch.arange(L) % 7 + 1                                       # no mask ids in the base row
    specs = [Spec(torch.tensor([1, 4]), 0, 40), Spec(torch.tensor([2]), 10, 50, extra=torch.tensor([7, 8, 9])),
             Spec(torch.arange(L), 0, V), Spec(torch.tensor([0, 11]), 5, 30), Spec(torch.tensor([3]), 0, 40, extra=torch.tensor([0, 1]))]
    seen = []
    out = list(masked_logprobs(_fake(seen), base, specs, bs=2))
    assert len(out) == len(specs)
    rows = torch.cat(seen, 0)
    assert rows.shape == (5, L)
    for r, sp in zip(rows, specs):
        m = torch.zeros(L, dtype=torch.bool)
        m[sp.pos] = True
        if sp.extra is not None:
            m[sp.extra] = True
        assert ((r == MASK_ID) == m).all()                               # exactly pos + extra masked
        assert (r[~m] == base[~m]).all()                                 # everything else untouched
    for o, sp, r in zip(out, specs, rows):
        vis = float((r != MASK_ID).sum())
        assert torch.allclose(o, _expected(base, sp, vis), atol=1e-6)
        assert o.shape == (len(sp.pos), sp.hi - sp.lo)
        assert torch.allclose(o.exp().sum(1), torch.ones(len(sp.pos)), atol=1e-5)


def test_gather_true_indexes_the_observed_token():
    if torch is None:
        return
    base = torch.tensor([5, 9, 3, 12])
    lp = torch.log_softmax(torch.randn(2, 20), dim=-1)
    pos = torch.tensor([1, 3])
    lpt, mp = gather_true(lp, base, pos, lo=2)                           # targets are base - lo = 7, 10
    assert torch.allclose(lpt, torch.stack([lp[0, 7], lp[1, 10]]))
    assert torch.allclose(mp, lp.max(1).values.exp())


if __name__ == "__main__":
    test_masks_and_values_and_order()
    test_gather_true_indexes_the_observed_token()
    print("ok")
