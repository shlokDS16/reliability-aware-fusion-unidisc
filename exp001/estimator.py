"""S_theta estimator (card section 8): mixture-reference estimator, pad/content stratified T->I decomposition, chunked I->T joint
draw, no-information floors and the wrapper networks of the validity gates. All arithmetic in float64, natural logs.

Array conventions: M is [R, J, V] (R requery marginals of J receiving positions over V values), float64, rows normalised.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import torch

from .network import to_prob
from .sampler import inverse_cdf, draw_from_class

TINY = 1e-300


def kl(p: torch.Tensor, q: torch.Tensor) -> torch.Tensor:
    """KL(p||q) over the last dim, 0 log 0 = 0."""
    t = torch.where(p > 0, p * (torch.log(p.clamp_min(TINY)) - torch.log(q.clamp_min(TINY))), torch.zeros_like(p))
    return t.sum(-1)


def entropy(p: torch.Tensor) -> torch.Tensor:
    return -torch.where(p > 0, p * torch.log(p.clamp_min(TINY)), torch.zeros_like(p)).sum(-1)


def mixture_estimate(M: torch.Tensor, p1: torch.Tensor | None = None) -> dict:
    """Plug-in mixture estimator I_hat_j = (1/R) sum_r KL(m_r || mbar), mbar the mean of the R marginals (bounded by ln R).
    With a one-pass reference p1 [J, V]: naive_j = (1/R) sum_r KL(m_r||p1) and I_inc_j = KL(mbar||p1) with the exact identity
    naive = I_hat + I_inc (any R)."""
    mbar = M.mean(0)
    I_hat = kl(M, mbar.unsqueeze(0)).mean(0)
    out = {"I_hat": I_hat, "mbar": mbar, "H_mbar": entropy(mbar)}
    if p1 is not None:
        out["naive"] = kl(M, p1.unsqueeze(0)).mean(0)
        out["I_inc"] = kl(mbar, p1)
    return out


def stratified_estimate(M: torch.Tensor, pad_draw, w: float, p1: torch.Tensor | None = None, min_mass: float = 1e-6) -> dict:
    """Card 8.2 step 4. pad_draw: bool [R], True for draws from the pad class P. w = p1_src(P).

    total = between + within_pad + within_content (exact identity at any R). A class with source mass < min_mass or no draws
    contributes 0 to every term and the mixture reference is the other class's mean (the bounded-by-1e-5 rule of the card)."""
    pad_draw = torch.as_tensor(pad_draw, dtype=torch.bool, device=M.device)
    nP, nC = int(pad_draw.sum()), int((~pad_draw).sum())
    availP = nP > 0 and w >= min_mass
    availC = nC > 0 and (1.0 - w) >= min_mass
    zero = torch.zeros(M.shape[1], dtype=M.dtype, device=M.device)
    mP = M[pad_draw].mean(0) if availP else None
    mC = M[~pad_draw].mean(0) if availC else None
    if availP and availC:
        piP, piC = w, 1.0 - w
        mbar = piP * mP + piC * mC
    elif availP:
        piP, piC, mbar = 1.0, 0.0, mP
    elif availC:
        piP, piC, mbar = 0.0, 1.0, mC
    else:
        raise ValueError("no usable class")
    wp = piP * kl(M[pad_draw], mP.unsqueeze(0)).mean(0) if availP else zero
    wc = piC * kl(M[~pad_draw], mC.unsqueeze(0)).mean(0) if availC else zero
    btw = zero.clone()
    if availP:
        btw = btw + piP * kl(mP, mbar)
    if availC:
        btw = btw + piC * kl(mC, mbar)
    out = {"total": btw + wp + wc, "between": btw, "within_pad": wp, "within_content": wc, "mbar": mbar, "H_mbar": entropy(mbar),
           "avail_pad": availP, "avail_content": availC, "w": w}
    if p1 is not None:
        inc = kl(mbar, p1)
        out["I_inc"] = inc
        out["naive"] = out["total"] + inc          # exact identity; verified against a direct computation in the tests
    return out


def stratified_halves(M, pad_draw, w, min_mass=1e-6):
    """Two disjoint halves (R/2 draws, half of each class) for the Monte Carlo SD (card 8.3)."""
    pad_draw = torch.as_tensor(pad_draw, dtype=torch.bool, device=M.device)
    idxP = torch.nonzero(pad_draw).flatten()
    idxC = torch.nonzero(~pad_draw).flatten()
    out = []
    for h in (0, 1):
        sel = torch.cat([idxP[h::2], idxC[h::2]])
        out.append(stratified_estimate(M[sel], pad_draw[sel], w, None, min_mass))
    return out


def pad_content_split(M: torch.Tensor, pad_ids) -> dict:
    """Descriptive chain-rule split (r2) of the mean receiving KL of the unstratified estimator into the pad-versus-content
    indicator part and the within-class parts. M [R, J, V]."""
    V = M.shape[-1]
    inP = torch.zeros(V, dtype=torch.bool, device=M.device)
    inP[list(pad_ids)] = True
    q = M[..., inP].sum(-1)                                   # [R, J]
    qbar = q.mean(0)
    mbar = M.mean(0)
    ind = (torch.where(q > 0, q * torch.log(q.clamp_min(TINY) / qbar.clamp_min(TINY)), torch.zeros_like(q))
           + torch.where(q < 1, (1 - q) * torch.log((1 - q).clamp_min(TINY) / (1 - qbar).clamp_min(TINY)), torch.zeros_like(q))).mean(0)
    Mp = M[..., inP]
    Mc = M[..., ~inP]
    mp = Mp / Mp.sum(-1, keepdim=True).clamp_min(TINY)
    mc = Mc / Mc.sum(-1, keepdim=True).clamp_min(TINY)
    bp = mbar[..., inP]
    bp = bp / bp.sum(-1, keepdim=True).clamp_min(TINY)
    bc = mbar[..., ~inP]
    bc = bc / bc.sum(-1, keepdim=True).clamp_min(TINY)
    within = (q * kl(mp, bp.unsqueeze(0)) + (1 - q) * kl(mc, bc.unsqueeze(0))).mean(0)
    return {"indicator": ind, "within": within, "total": ind + within}


@dataclass
class T2IResult:
    positions: np.ndarray          # masked image positions (aligned with all arrays)
    arrays: dict                   # name -> float64 numpy [J]
    w: float
    source: list
    tokens: list
    passes: int
    flags: dict


def _np(x):
    return x.detach().cpu().numpy().astype(np.float64)


def probe_t2i(net, tail, img, ctx, sources, rg, R: int = 8, stratify: bool = True, min_mass: float = 1e-6) -> T2IResult:
    """T->I probe (card 8.2 step 2): reveal the source token(s) with R draws and requery the image marginals.

    One source (k0): stratified 4 draws from the conditional given P and 4 from not-P (R/2 each) whenever both classes have mass
    >= min_mass; otherwise all R from the available class. Several sources (k+): sequential iid draws, total only."""
    L_T = net.L_T
    row_of = {int(j): k for k, j in enumerate(ctx["masked_text_idx"])}
    mi = torch.as_tensor(ctx["masked_img_idx"])
    p1_img = ctx["p_img"]
    dev = p1_img.device
    J, V = p1_img.shape
    M = torch.empty(R, J, V, dtype=torch.float64, device=dev)
    inP = torch.zeros(ctx["p_text"].shape[-1], dtype=torch.bool, device=ctx["p_text"].device)
    inP[list(net.pad_ids)] = True
    sources = [int(s) for s in sources]
    tokens = []
    passes = 0
    if len(sources) == 1 and stratify:
        src = sources[0]
        p_src = ctx["p_text"][row_of[src]]
        w = float(p_src[inP].sum())
        availP, availC = w >= min_mass, (1 - w) >= min_mass
        if availP and availC:
            pad_draw = torch.tensor([True] * (R // 2) + [False] * (R - R // 2))
        elif availP:
            pad_draw = torch.ones(R, dtype=torch.bool)
        else:
            pad_draw = torch.zeros(R, dtype=torch.bool)
        us = rg.random(R)
        for r in range(R):
            cls = inP if bool(pad_draw[r]) else ~inP
            tok = draw_from_class(p_src, cls, float(us[r]))
            tokens.append(tok)
            tr = tail.clone()
            tr[src] = tok
            _, lp_i = net.forward(tr, img)
            passes += 1
            M[r] = to_prob(lp_i, mi.to(lp_i.device))
        est = stratified_estimate(M, pad_draw, w, p1_img, min_mass)
        halves = stratified_halves(M, pad_draw, w, min_mass)
        arrays = {k: _np(est[k]) for k in ("total", "between", "within_pad", "within_content", "H_mbar", "I_inc", "naive")}
        arrays["total_h1"], arrays["total_h2"] = _np(halves[0]["total"]), _np(halves[1]["total"])
        arrays["content_h1"], arrays["content_h2"] = _np(halves[0]["within_content"]), _np(halves[1]["within_content"])
        flags = {"avail_pad": est["avail_pad"], "avail_content": est["avail_content"], "stratified": True}
    else:
        w = float("nan")
        us = rg.random((R, len(sources)))
        for r in range(R):
            tr = tail.clone()
            for s_i, src in enumerate(sources):
                if s_i == 0:
                    p = ctx["p_text"][row_of[src]]
                else:
                    lp_t, _ = net.forward(tr, img)
                    passes += 1
                    p = to_prob(lp_t, torch.as_tensor([src]).to(lp_t.device))[0]
                tok = int(inverse_cdf(p.unsqueeze(0), torch.as_tensor([us[r, s_i]], dtype=torch.float64))[0])
                tr[src] = tok
                tokens.append(tok)
            _, lp_i = net.forward(tr, img)
            passes += 1
            M[r] = to_prob(lp_i, mi.to(lp_i.device))
        est = mixture_estimate(M, p1_img)
        arrays = {"total": _np(est["I_hat"]), "H_mbar": _np(est["H_mbar"]), "I_inc": _np(est["I_inc"]), "naive": _np(est["naive"])}
        flags = {"stratified": False}
    return T2IResult(ctx["masked_img_idx"].copy(), arrays, w, sources, tokens, passes, flags)


@dataclass
class I2TResult:
    positions: np.ndarray          # masked tail positions (aligned)
    arrays: dict
    passes: int
    img_set: list
    chunks: int


def chunk_order(img_set, conf_img, masked_img_idx, order="conf"):
    """Confidence order of the committed image set (descending max marginal, ties lowest index); 'reverse' for the G5 check."""
    row = {int(j): k for k, j in enumerate(masked_img_idx)}
    s = sorted((int(j) for j in img_set), key=lambda j: (-float(conf_img[row[j]]), j))
    return s[::-1] if order == "reverse" else s


def probe_i2t(net, tail, img, ctx, img_set, rg, R: int = 8, g: int = 4, order: str = "conf") -> I2TResult:
    """I->T probe (card 8.2 step 3): draw the committed image set in g chunks (within a chunk from the product of marginals,
    between chunks requery with the earlier chunks revealed), then one requery pass gives the text marginals of all still-masked
    tail positions. Passes per draw: g."""
    ordered = chunk_order(img_set, ctx["conf_img"], ctx["masked_img_idx"], order)
    n = len(ordered)
    sizes = [n // g + (1 if k < n % g else 0) for k in range(g)]
    bounds = np.cumsum([0] + sizes)
    row_i = {int(j): k for k, j in enumerate(ctx["masked_img_idx"])}
    mt = torch.as_tensor(ctx["masked_text_idx"])
    p1_text = ctx["p_text"]
    Jt, Vt = p1_text.shape
    M = torch.empty(R, Jt, Vt, dtype=torch.float64, device=p1_text.device)
    passes = 0
    us = rg.random((R, n))
    for r in range(R):
        ir = img.clone()
        for c in range(g):
            pos = ordered[bounds[c]:bounds[c + 1]]
            if not pos:
                continue
            if c == 0:
                p = ctx["p_img"][[row_i[j] for j in pos]]
            else:
                _, lp_i = net.forward(tail, ir)
                passes += 1
                p = to_prob(lp_i, torch.as_tensor(pos).to(lp_i.device))
            toks = inverse_cdf(p, torch.as_tensor(us[r, bounds[c]:bounds[c + 1]], dtype=torch.float64))
            ir[torch.as_tensor(pos)] = toks.cpu()
        lp_t, _ = net.forward(tail, ir)
        passes += 1
        M[r] = to_prob(lp_t, mt.to(lp_t.device))
    est = mixture_estimate(M, p1_text)
    split = pad_content_split(M, net.pad_ids)
    h = M.shape[0] // 2
    h1, h2 = mixture_estimate(M[:h])["I_hat"], mixture_estimate(M[h:])["I_hat"]
    arrays = {"total": _np(est["I_hat"]), "H_mbar": _np(est["H_mbar"]), "I_inc": _np(est["I_inc"]), "naive": _np(est["naive"]),
              "split_indicator": _np(split["indicator"]), "split_within": _np(split["within"]),
              "total_h1": _np(h1), "total_h2": _np(h2),
              "pad_mass_mbar": _np(est["mbar"][:, list(net.pad_ids)].sum(-1))}
    return I2TResult(ctx["masked_text_idx"].copy(), arrays, passes, list(ordered), g)


def noinfo_floor(net, tail, img, ctx, direction: str, R: int = 8, thr: float = 0.999, fallback: float = 0.99,
                 min_positions: int = 6):
    """G1b (card 8.7): no-information reveal. T->I: reveal R different tail positions with max marginal >= thr (near-
    deterministic: post-EOS / pad tail) with their argmax token; I->T: reveal image positions the same way. Fewer than
    `min_positions`: use >= fallback on the same side; still fewer: floor unmeasured (None). Returns dict with the mixture
    estimator over the requeries (per receiving position) and the thresholds actually used."""
    if direction == "t2i":
        p_src, idx_src, other_p, other_idx = ctx["p_text"], ctx["masked_text_idx"], ctx["p_img"], ctx["masked_img_idx"]
    else:
        p_src, idx_src, other_p, other_idx = ctx["p_img"], ctx["masked_img_idx"], ctx["p_text"], ctx["masked_text_idx"]
    mx, am = p_src.max(-1)
    used = None
    for t in (thr, fallback):
        cand = [k for k in range(len(idx_src)) if float(mx[k]) >= t]
        if len(cand) >= min_positions:
            used = t
            break
    if used is None:
        return None
    cand = cand[:R]
    M = torch.empty(len(cand), other_p.shape[0], other_p.shape[1], dtype=torch.float64, device=other_p.device)
    for r, k in enumerate(cand):
        tr, ir = tail.clone(), img.clone()
        if direction == "t2i":
            tr[int(idx_src[k])] = int(am[k])
            lp_t, lp_i = net.forward(tr, ir)
            M[r] = to_prob(lp_i, torch.as_tensor(other_idx).to(lp_i.device))
        else:
            ir[int(idx_src[k])] = int(am[k])
            lp_t, lp_i = net.forward(tr, ir)
            M[r] = to_prob(lp_t, torch.as_tensor(other_idx).to(lp_t.device))
    est = mixture_estimate(M)
    return {"floor": _np(est["I_hat"]), "H_mbar": _np(est["H_mbar"]), "threshold": used, "n_reveals": len(cand), "positions": np.asarray(other_idx)}


# --------------------------------------------------------------------------------------------- wrapper networks (G2, G3, G3b, NC-6')

class _Wrap:
    def __init__(self, net):
        self.net = net
        for a in ("L_T", "L_I", "V_T", "V_I", "mask_id", "pad_ids"):
            setattr(self, a, getattr(net, a))

    def _masked(self, tail, img):
        return (torch.full_like(tail, self.mask_id), torch.full_like(img, -1))

    @property
    def n_forward(self):
        return self.net.n_forward


class BlindNet(_Wrap):
    """Modality-blind model (card 8.7 G2, 8.8 NC-1, NC-6'): text marginals from a pass with all image positions masked; image
    marginals from a pass with all text positions masked, prefix included (drop_prefix)."""

    def forward(self, tail, img, drop_prefix=False):
        tmask, imask = self._masked(tail, img)
        lp_t, _ = self.net.forward(tail, imask)
        _, lp_i = self.net.forward(tmask, img, drop_prefix=True)
        return lp_t, lp_i


class InjectionNet(_Wrap):
    """G3 / G3b injection: blind image marginals mixed 70/30 with uniform (over the image slice) when the trigger fires.
    mode 'any'  (G3): any text token beyond the reference state s is revealed (true dependence is zero).
    mode 'pad'  (G3b): a revealed text token beyond s is in the pad class P (a length-only dependence)."""

    def __init__(self, net, mode="any", mix=0.7):
        super().__init__(net)
        self.blind = BlindNet(net)
        self.mode, self.mix = mode, mix
        self.ref_tail = None

    def set_reference(self, tail_s):
        self.ref_tail = tail_s.clone()

    def forward(self, tail, img, drop_prefix=False):
        lp_t, lp_i = self.blind.forward(tail, img)
        new = (tail != self.mask_id) & (self.ref_tail == self.mask_id)
        if self.mode == "any":
            trig = bool(new.any())
        else:
            pad = torch.zeros_like(new)
            for pid in self.pad_ids:
                pad |= tail == pid
            trig = bool((new & pad).any())
        if trig:
            p = lp_i.to(torch.float64).exp()
            p = self.mix * p + (1 - self.mix) / p.shape[-1]
            lp_i = p.log().to(lp_i.dtype)
        return lp_t, lp_i
