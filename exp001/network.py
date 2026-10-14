"""Network interface used by the sampler and the estimator, and a CPU toy network for tests.

A *state* is a pair of integer tensors:
  tail : [L_T]   text ids of the generated tail, mask id (net.mask_id) where still masked
  img  : [L_I]   image CODES (0..V_I-1), -1 where still masked
Everything else in the row (system prompt, observed prefix, markers) is fixed by the net.

net.forward(tail, img) returns (logp_text [L_T, V_T], logp_img [L_I, V_I]): log-probabilities (any float dtype) over the tail
positions and the image positions, each renormalised inside its own modality slice by the model head (observed positions
one-hot). `to_prob` converts selected rows to float64 and renormalises inside the slice (card 6, 9 item 5).
"""
from __future__ import annotations

from typing import Protocol

import numpy as np
import torch


class Net(Protocol):
    L_T: int
    L_I: int
    V_T: int
    V_I: int
    mask_id: int
    pad_ids: tuple

    def forward(self, tail: torch.Tensor, img: torch.Tensor, drop_prefix: bool = False): ...


def to_prob(logp: torch.Tensor, rows=None) -> torch.Tensor:
    """float64 probabilities of selected rows, renormalised inside the slice."""
    x = logp if rows is None else logp[rows]
    p = x.to(torch.float64).exp()
    return p / p.sum(-1, keepdim=True)


def pad_mass(p_text: torch.Tensor, pad_ids) -> torch.Tensor:
    return p_text[..., list(pad_ids)].sum(-1)


class ToyNet:
    """Small deterministic masked model with controllable cross-modal coupling.

    Revealed tokens contribute through random embeddings E; logits = base + W h. Text-to-image weight scale `c_ti`, image-to-text
    `c_it`, within-modality `c_tt`/`c_ii`. Pad ids (0 and 2) get a boost at later tail positions (a crude 'tail after caption').
    This is a test object, not a model of UniDisc.
    """

    def __init__(self, seed=0, L_T=8, L_I=16, V_T=12, V_I=20, d=6, c_ti=1.0, c_it=1.0, c_tt=0.5, c_ii=0.5, base_scale=1.0,
                 pad_boost=2.0, device="cpu", dtype=torch.float32):
        g = torch.Generator().manual_seed(seed)
        self.L_T, self.L_I, self.V_T, self.V_I = L_T, L_I, V_T, V_I
        self.mask_id = V_T - 1
        self.pad_ids = (0, 2)
        self.device, self.dtype = device, dtype
        n = L_T + L_I
        self.n_forward = 0
        self.E_t = torch.randn(L_T, V_T, d, generator=g)       # embedding of (tail pos, token)
        self.E_i = torch.randn(L_I, V_I, d, generator=g)
        self.Wt = torch.randn(L_T, d, V_T, generator=g) / d ** 0.5
        self.Wi = torch.randn(L_I, d, V_I, generator=g) / d ** 0.5
        self.bt = torch.randn(L_T, V_T, generator=g) * base_scale
        self.bi = torch.randn(L_I, V_I, generator=g) * base_scale
        boost = torch.zeros(L_T, V_T)
        for j in range(L_T):
            boost[j, 0] = pad_boost * j / max(L_T - 1, 1)
            boost[j, 2] = pad_boost * j / max(L_T - 1, 1) * 0.5
        self.bt = self.bt + boost
        self.bt[:, self.mask_id] = -1e9
        self.c = dict(ti=c_ti, it=c_it, tt=c_tt, ii=c_ii)

    def _h(self, tail, img):
        mt = tail != self.mask_id
        mi = img >= 0
        ht = (self.E_t[torch.arange(self.L_T), tail.clamp(max=self.V_T - 1)] * mt[:, None]).sum(0)
        hi = (self.E_i[torch.arange(self.L_I), img.clamp(min=0)] * mi[:, None]).sum(0)
        return ht, hi

    @torch.no_grad()
    def forward(self, tail, img, drop_prefix=False):
        self.n_forward += 1
        tail, img = tail.cpu().long(), img.cpu().long()
        ht, hi = self._h(tail, img)
        lt = self.bt + torch.einsum("d,jdv->jv", self.c["tt"] * ht + self.c["it"] * hi, self.Wt)
        li = self.bi + torch.einsum("d,jdv->jv", self.c["ti"] * ht + self.c["ii"] * hi, self.Wi)
        lt[:, self.mask_id] = -1e9
        lp_t = torch.log_softmax(lt, -1)
        lp_i = torch.log_softmax(li, -1)
        # observed positions: one-hot, as the real model head returns
        for j in range(self.L_T):
            if tail[j] != self.mask_id:
                lp_t[j] = -1e9
                lp_t[j, tail[j]] = 0.0
        for j in range(self.L_I):
            if img[j] >= 0:
                lp_i[j] = -1e9
                lp_i[j, img[j]] = 0.0
        return lp_t.to(self.dtype), lp_i.to(self.dtype)


def initial_state(net, device=None):
    tail = torch.full((net.L_T,), net.mask_id, dtype=torch.long)
    img = torch.full((net.L_I,), -1, dtype=torch.long)
    if device is not None:
        tail, img = tail.to(device), img.to(device)
    return tail, img
