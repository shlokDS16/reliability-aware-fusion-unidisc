"""Sampler with an explicit per-pass commit plan (card 5, 6, 9).

Value rule (fixed across arms): plain sampling at temperature 1 from the unmodified marginals; all draws by float64 inverse-CDF
using one float64 uniform per generated position (common random numbers, 4.5); no top-p / top-k / guidance (condition P).
Position rule: within-modality confidence ranking (max marginal probability, ties lowest index) or P_rand (fixed random
priorities per position, uniformly random subset each pass). One forward pass per executed pass; a pass that commits nothing is
a no-op and is skipped (no time input, card 3 item 2).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
import torch

from .network import to_prob, pad_mass
from .plan import Plan


def inverse_cdf(p: torch.Tensor, u: torch.Tensor) -> torch.Tensor:
    """float64 inverse-CDF draw: p [n, V] rows (float64), u [n] float64 in [0,1)."""
    cdf = torch.cumsum(p, dim=-1)
    thr = (u.to(device=p.device, dtype=p.dtype) * cdf[:, -1]).unsqueeze(-1)
    idx = torch.searchsorted(cdf.contiguous(), thr.contiguous(), right=True).squeeze(-1)
    return idx.clamp(max=p.shape[-1] - 1)


def draw_from_class(p: torch.Tensor, in_class: torch.Tensor, u: float) -> int:
    """Inverse-CDF draw from p restricted to the ids in `in_class` (bool [V]) and renormalised; p is a 1-D float64 row."""
    q = p * in_class.to(p.dtype)
    cdf = torch.cumsum(q, 0)
    thr = u * cdf[-1]
    idx = int(torch.searchsorted(cdf, thr.reshape(1), right=True).item())
    # land on a class member even under rounding at the boundary
    idx = min(idx, p.shape[0] - 1)
    if not bool(in_class[idx]):
        members = torch.nonzero(in_class).flatten()
        later = members[members >= idx]
        idx = int(later[0]) if len(later) else int(members[-1])
    return idx


def rank_positions(conf: np.ndarray, count: int, prio: Optional[np.ndarray] = None) -> np.ndarray:
    """Indices (into the candidate list) of the `count` committed candidates.

    Confidence rule: top-count by `conf`, ties broken by lowest index (stable sort). P_rand: lowest `prio` first (prio unique)."""
    if count <= 0:
        return np.zeros(0, dtype=int)
    if prio is not None:
        order = np.argsort(prio, kind="stable")
    else:
        order = np.argsort(-conf, kind="stable")
    return order[:count]


@dataclass
class PassRecord:
    q: int                   # 1-based pass index in the plan
    window: int
    text_pos: list           # tail indices committed (sorted)
    img_pos: list            # image positions committed (sorted)
    text_tok: list           # committed token ids (aligned to text_pos)
    n_masked_text: int
    n_masked_img: int
    text_state_pad: list     # per committed text token: state-pad flag at this pass (p1 mass on P >= 0.5)
    text_pad_mass: list      # p1 mass on P at each committed text position
    maxp_text: list          # max marginal prob of every masked tail position (aligned to masked_text_idx)
    padmass_text: list       # P mass of every masked tail position
    masked_text_idx: list
    seconds: float = 0.0


@dataclass
class SampleResult:
    tail: torch.Tensor
    img: torch.Tensor
    records: list = field(default_factory=list)
    n_forward: int = 0
    plan_name: str = ""

    def committed_sets(self):
        return [(r.q, r.text_pos, r.img_pos) for r in self.records]


def run_sample(net, plan: Plan, u: np.ndarray, rule: str = "conf", prio: Optional[np.ndarray] = None,
               hook: Optional[Callable] = None, state=None, start_pass: int = 1, stop_pass: Optional[int] = None,
               keep_marginal_stats: bool = True) -> SampleResult:
    """Run `plan` on `net`. u: float64 uniforms [L_T + L_I] (text tail first). prio: same layout, used when rule == 'rand'.

    hook(q, tail, img, ctx) is called before each executed pass commits, with ctx = dict(p_text, p_img (float64, masked rows
    only, others zero), masked_text_idx, masked_img_idx, sets=(text_pos, img_pos) the plan's committed sets for this pass, record
    stats). It must not change `tail`/`img` or any RNG used by the sampler (probe isolation, G6)."""
    import time
    L_T, L_I = net.L_T, net.L_I
    if state is None:
        tail = torch.full((L_T,), net.mask_id, dtype=torch.long)
        img = torch.full((L_I,), -1, dtype=torch.long)
    else:
        tail, img = state[0].clone(), state[1].clone()
    u_t = torch.as_tensor(u[:L_T], dtype=torch.float64)
    u_i = torch.as_tensor(u[L_T:L_T + L_I], dtype=torch.float64)
    pr_t = None if prio is None else np.asarray(prio[:L_T])
    pr_i = None if prio is None else np.asarray(prio[L_T:L_T + L_I])
    use_rand = rule == "rand"
    if use_rand and prio is None:
        raise ValueError("rule 'rand' needs prio")
    res = SampleResult(tail, img, [], 0, plan.name)
    for q, ps in enumerate(plan.passes, 1):
        if q < start_pass:
            continue
        if stop_pass is not None and q > stop_pass:
            break
        if ps.total == 0:
            continue                                   # no-op pass
        t0 = time.perf_counter()
        lp_t, lp_i = net.forward(tail, img)
        res.n_forward += 1
        m_t = (tail == net.mask_id).nonzero().flatten()
        m_i = (img < 0).nonzero().flatten()
        p_t = to_prob(lp_t, m_t.to(lp_t.device)) if len(m_t) else torch.zeros(0, lp_t.shape[-1], dtype=torch.float64)
        p_i = to_prob(lp_i, m_i.to(lp_i.device)) if len(m_i) else torch.zeros(0, lp_i.shape[-1], dtype=torch.float64)
        conf_t = p_t.max(-1).values.cpu().numpy() if len(m_t) else np.zeros(0)
        conf_i = p_i.max(-1).values.cpu().numpy() if len(m_i) else np.zeros(0)
        m_t_np, m_i_np = m_t.cpu().numpy(), m_i.cpu().numpy()
        if ps.pooled:
            conf = np.concatenate([conf_t, conf_i])
            gidx = np.concatenate([m_t_np, L_T + m_i_np])           # global index: tail first, then image
            pr = None if not use_rand else np.concatenate([pr_t[m_t_np], pr_i[m_i_np]])
            sel = rank_positions(conf, ps.n_pooled, pr)
            # ties lowest global position index: rank_positions is stable over the concatenated (index-ordered) candidates
            chosen = gidx[sel]
            sel_t = np.sort(chosen[chosen < L_T])
            sel_i = np.sort(chosen[chosen >= L_T] - L_T)
        else:
            st = rank_positions(conf_t, ps.n_text, None if not use_rand else pr_t[m_t_np])
            si = rank_positions(conf_i, ps.n_img, None if not use_rand else pr_i[m_i_np])
            sel_t = np.sort(m_t_np[st]) if len(st) else np.zeros(0, dtype=int)
            sel_i = np.sort(m_i_np[si]) if len(si) else np.zeros(0, dtype=int)
        pm = pad_mass(p_t, net.pad_ids).cpu().numpy() if len(m_t) else np.zeros(0)
        row_of_t = {int(j): k for k, j in enumerate(m_t_np)}
        ctx = dict(p_text=p_t, p_img=p_i, masked_text_idx=m_t_np, masked_img_idx=m_i_np, sets=(sel_t, sel_i), q=q, window=ps.window,
                   logp=(lp_t, lp_i), conf_text=conf_t, conf_img=conf_i, pad_mass_text=pm)
        if hook is not None:
            hook(q, tail, img, ctx)
        # values: float64 inverse CDF at the position's own uniform
        new_t = []
        if len(sel_t):
            rows = torch.as_tensor([row_of_t[int(j)] for j in sel_t])
            new_t = inverse_cdf(p_t[rows], u_t[torch.as_tensor(sel_t)]).cpu()
        new_i = []
        if len(sel_i):
            row_of_i = {int(j): k for k, j in enumerate(m_i_np)}
            rows = torch.as_tensor([row_of_i[int(j)] for j in sel_i])
            new_i = inverse_cdf(p_i[rows], u_i[torch.as_tensor(sel_i)]).cpu()
        rec = PassRecord(q, ps.window, [int(j) for j in sel_t], [int(j) for j in sel_i], [int(x) for x in new_t],
                         len(m_t), len(m_i), [bool(pm[row_of_t[int(j)]] >= 0.5) for j in sel_t],
                         [float(pm[row_of_t[int(j)]]) for j in sel_t],
                         conf_t.tolist() if keep_marginal_stats else [], pm.tolist() if keep_marginal_stats else [],
                         m_t_np.tolist())
        if len(sel_t):
            tail[torch.as_tensor(sel_t)] = torch.as_tensor(new_t, dtype=torch.long)
        if len(sel_i):
            img[torch.as_tensor(sel_i)] = torch.as_tensor(new_i, dtype=torch.long)
        rec.seconds = time.perf_counter() - t0
        res.records.append(rec)
    res.tail, res.img = tail, img
    return res
