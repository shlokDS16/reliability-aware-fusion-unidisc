"""Shared CPU fakes of the Omni stack (no transformers, no weights): a tokenizer with the real special ids, a model with `forward_dream` returning bf16 logits over the real vocabulary size,
and a MAGVIT stand-in. The module name starts with test_ only so that it sits with the other Omni tests; it contains no tests."""
from __future__ import annotations

import re
import sys
import zlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2.omni import layout as L                                           # noqa: E402

SPECIAL = {"<|im_start|>": 151644, "<|im_end|>": 151645, "<|begin_of_image|>": 151667, "<|end_of_image|>": 151668, "<|mask|>": 151666, "\n": 198, "user": 872, "assistant": 77091}
_TOK_RE = re.compile(r"<\|[a-z_0-9]+\|>|\n|[^\s<]+")


class FakeOmniTokenizer:
    """Words -> ids below 151643 (crc32), the structural tokens and <|image_k|> -> the real ids. Splits at newlines like the real regex, so tokens(A + B) == tokens(A) + tokens(B) when A ends with a newline."""
    vocab_size = L.OMNI_VOCAB

    def __len__(self):
        return L.OMNI_VOCAB

    def _one(self, t):
        if t in SPECIAL:
            return SPECIAL[t]
        m = re.fullmatch(r"<\|image_(\d+)\|>", t)
        if m:
            return L.OMNI_IMG_OFFSET + int(m.group(1))
        return 1000 + zlib.crc32(t.encode()) % 100000

    def __call__(self, s, add_special_tokens=False):
        return {"input_ids": [self._one(t) for t in _TOK_RE.findall(s)]}

    def convert_tokens_to_ids(self, t):
        return self._one(t)

    def convert_ids_to_tokens(self, ids):
        def one(i):
            if L.OMNI_IMG_OFFSET <= i < L.OMNI_IMG_OFFSET + L.OMNI_N_CODES:
                return f"<|image_{i - L.OMNI_IMG_OFFSET}|>"
            for k, v in SPECIAL.items():
                if v == i:
                    return k
            return f"t{i}"
        return [one(int(i)) for i in ids] if isinstance(ids, (list, tuple)) else one(int(ids))

    def decode(self, ids):
        return " ".join(f"t{i}" for i in ids)


class FakeOmniModel(torch.nn.Module):
    """forward_dream(input_ids) -> logits [B, L, 176264] bf16: a tiny random function of the visible tokens plus a per-position term. Records the real-id rows it saw."""

    def __init__(self, seed=0, d=8):
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.E = torch.randn(L.OMNI_VOCAB, d, generator=g)
        self.O = torch.randn(d, L.OMNI_VOCAB, generator=g) * 0.5
        self.P = torch.randn(1024, d, generator=g)
        self.dummy = torch.nn.Parameter(torch.zeros(1), requires_grad=False)
        self.config = SimpleNamespace(mask_token_id=L.OMNI_MASK_ID, vocab_size=L.OMNI_VOCAB)
        self.seen: list[torch.Tensor] = []
        self.forward_calls = 0

    def forward_dream(self, input_ids=None, attention_mask=None, position_ids=None, inputs_embeds=None, use_cache=None, return_dict=None, **kw):
        assert attention_mask is None and use_cache is False
        x = input_ids
        self.forward_calls += 1
        self.seen.extend(x.clone())
        B, T = x.shape
        vis = (x != L.OMNI_MASK_ID).float()[..., None]
        ctx = (self.E[x] * vis).sum(1, keepdim=True) / (vis.sum(1, keepdim=True) + 1.0)
        h = self.P[:T][None] + ctx
        return SimpleNamespace(logits=(h @ self.O).to(torch.bfloat16))


class FakeMagvit:
    """get_code: block-mean quantiser to [0, 8192) on the (normalised) image; decode_code: constant-colour blocks."""

    def __init__(self, grid=16):
        self.grid = grid

    def get_code(self, x):
        B, C, H, W = x.shape
        k = H // self.grid
        a = ((x + 1) / 2).clamp(0, 1).reshape(B, 3, self.grid, k, self.grid, k).mean(dim=(3, 5))
        q = (a * 15.999).long()
        return ((q[:, 0] * 16 + q[:, 1]) * 2 + (q[:, 2] > 7).long()).reshape(B, -1) % L.OMNI_N_CODES

    def decode_code(self, z):
        B, N = z.shape
        g = int(round(N ** 0.5))
        v = (z.float() / L.OMNI_N_CODES * 2 - 1).reshape(B, 1, g, g).repeat(1, 3, 1, 1)
        return torch.nn.functional.interpolate(v, scale_factor=16, mode="nearest")


def make_scorer(grid=4, micro_bs=1, **kw):
    from exp_p2.omni.scorer import OmniScorer
    return OmniScorer(FakeOmniModel(), FakeOmniTokenizer(), FakeMagvit(grid), grid=grid, micro_bs=micro_bs, device="cpu", **kw)
