"""CPU stand-in for `exp_p2.scoring.UniScorer` used by the gate tests. No model, no weights, no GPU.

Same interface as UniScorer: caption_ids, preprocess, encode, build, logits_fn, L_I (plus tok for word pieces). The layout is the real one
(sys prompt, <s> caption </s> <s> marker, image ids, </s>) with the real vocabulary ranges (text 0..31999, mask 32000, image 32001..48384),
so every Spec index/vocab range used on the real model is exercised. The "network" is a tiny random function of the visible tokens:
    logits[l] = bias + O^T (P[l] + a[mod_l, T] * mean-ish sum of visible text embeddings + a[mod_l, I] * ... of visible image embeddings)
`cross` scales the text<->image coupling (cross=0 makes the joint independent), `uniform=True` returns all-zero logits.
"""
from __future__ import annotations

import zlib

import numpy as np
import torch

from exp_p2.scoring import MASK_ID, IMG_OFFSET, IMG_HI

V_ALL = IMG_HI          # 48385


class FakeTok:
    def convert_ids_to_tokens(self, ids):
        return [("▁" if i % 3 == 0 else "") + f"p{i}" for i in ids]


class FakeScorer:
    def __init__(self, grid: int = 8, seed: int = 0, cross: float = 1.0, intra: float = 1.0, uniform: bool = False, d: int = 8):
        self.grid, self.L_I = grid, grid * grid
        g = torch.Generator().manual_seed(seed)
        self.E = torch.randn(V_ALL, d, generator=g)
        self.O = torch.randn(d, V_ALL, generator=g)
        self.P = torch.randn(1024, d, generator=g)
        self.bias = torch.randn(V_ALL, generator=g) * 0.5
        self.a = torch.tensor([[intra, cross], [cross, intra]])
        self.uniform = uniform
        self.sys_ids, self.marker = [1, 5, 6, 2], 811
        self.tok = FakeTok()
        self.n_forward_rows = 0                      # rows pushed through the fake network (for pass accounting tests)
        self.rows: list[torch.Tensor] = []           # every input row seen (clone), for mask-semantics tests

    # ---- text / image front end
    def caption_ids(self, caption: str) -> list[int]:
        return [100 + zlib.crc32(w.encode()) % 31000 for w in caption.split()]

    def preprocess(self, pil):
        from PIL import Image
        w, h = pil.size
        s = min(w, h)
        l, t = (w - s) // 2, (h - s) // 2
        return pil.convert("RGB").crop((l, t, l + s, t + s)).resize((512, 512), Image.BICUBIC)

    def encode(self, pil512) -> np.ndarray:
        """Block-mean quantiser: code = (r>>3)<<9 | (g>>3)<<4 | (b>>4) of the mean colour of each (512/grid)^2 pixel block (< 16384)."""
        a = np.asarray(pil512.convert("RGB"), np.float64)
        k = 512 // self.grid
        blocks = a.reshape(self.grid, k, self.grid, k, 3).mean(axis=(1, 3)).astype(np.int64).reshape(-1, 3)
        return ((blocks[:, 0] >> 3) << 9 | (blocks[:, 1] >> 3) << 4 | (blocks[:, 2] >> 4)).astype(np.int64)

    # ---- layout identical to UniScorer.build, CPU tensors
    def build(self, caption_tok, codes):
        codes = torch.as_tensor(np.asarray(codes), dtype=torch.long)
        assert codes.numel() == self.L_I
        head = self.sys_ids + [1] + list(caption_tok) + [2, 1, self.marker]
        cap0, i0 = len(self.sys_ids) + 1, len(head)
        ids = torch.cat([torch.tensor(head, dtype=torch.long), codes + IMG_OFFSET, torch.tensor([2], dtype=torch.long)])
        mod = torch.zeros_like(ids)
        mod[i0:i0 + self.L_I] = 1
        return dict(base=ids, mod=mod[None], sid=torch.zeros_like(ids)[None],
                    cap_pos=torch.arange(cap0, cap0 + len(caption_tok)), img_pos=torch.arange(i0, i0 + self.L_I))

    def logits_fn(self, st):
        mod = st["mod"][0]
        mT, mI = (mod == 0).float()[None, :, None], (mod == 1).float()[None, :, None]
        aT, aI = self.a[mod, 0][None, :, None], self.a[mod, 1][None, :, None]

        def f(x):
            B, L = x.shape
            self.n_forward_rows += B
            self.rows.extend(x.clone())
            if self.uniform:
                return torch.zeros(B, L, V_ALL)
            vis = (x != MASK_ID).float()[..., None]
            ev = self.E[x] * vis
            evT, evI = ev * mT, ev * mI
            cT, cI = (vis * mT).sum(1, keepdim=True), (vis * mI).sum(1, keepdim=True)
            ctxT = (evT.sum(1, keepdim=True) - evT) / torch.sqrt(cT + 1.0)
            ctxI = (evI.sum(1, keepdim=True) - evI) / torch.sqrt(cI + 1.0)
            h = self.P[:L][None] + aT * ctxT + aI * ctxI
            return h @ self.O + self.bias
        return f


def fake_image(image_id: int, size: int = 96):
    """Deterministic smooth-ish synthetic RGB image (PIL) for a COCO-like id; no files."""
    from PIL import Image
    rng = np.random.default_rng(image_id)
    base = rng.integers(0, 256, size=(4, 4, 3)).astype(np.float32)
    big = np.kron(base, np.ones((size // 4, size // 4, 1), np.float32))
    big = np.clip(big + rng.normal(0, 6, big.shape), 0, 255)
    return Image.fromarray(big.astype(np.uint8))
