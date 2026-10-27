"""Image-direction evidence (v2 Alg. 5') and text-direction evidence, from already-computed log-probability matrices.

Image direction: Lambda^c = log-probs at all image tokens with the image fully masked and caption c visible ([m, 16384]; it never
sees the image). For observed codes v and an arm's included set R:
    Delta_j = Lambda^{c+}_j[v_j] - Lambda^{c-}_j[v_j]   (the null D_j cancels for a fixed image)
    Y = 1[mean_R Delta > 0]  (ties count wrong, as Appendix A of the spec), z_R = mean / (sd / sqrt(|R|)).
Empty R (L2, all gated): the evidence is exactly 0, Y = 0, z = 0, n = 0.
NOTE (spec inconsistency, see implementation notes): z_R scales with sqrt(|R|), so a RANDOM gate lowers z by sqrt(1 - g) in expectation; the spec says
'unchanged'. The size-invariant effect size d = mean / sd is therefore recorded as well; the headroom check can use either.
Text direction: E_{T<-I}(c) = mean over caption tokens of [log p(t_j | image minus gated tokens) - log p(t_j | all masked)]  (the probe-1
a_full_pmi layout with gated image tokens masked); paired over (c+, c-).
"""
from __future__ import annotations

import numpy as np


def gather_codes(lp, codes) -> np.ndarray:
    """lp [m, V] (torch tensor on any device, or numpy), codes [m] in 0..V-1 -> float32 numpy [m]."""
    codes = np.asarray(codes, dtype=np.int64)
    if hasattr(lp, "gather"):                                   # torch
        import torch
        idx = torch.as_tensor(codes, device=lp.device)[:, None]
        return lp.gather(1, idx)[:, 0].float().cpu().numpy().astype(np.float32)
    return np.asarray(lp)[np.arange(len(codes)), codes].astype(np.float32)


def evidence_from_delta(delta: np.ndarray, included: np.ndarray | None = None) -> dict:
    """Summarise per-token paired evidence over the included set. `included` is a bool array (R) or None for all tokens."""
    d = np.asarray(delta, np.float64)
    if included is not None:
        d = d[np.asarray(included, bool)]
    n = int(d.size)
    if n == 0:
        return dict(n=0, sum=0.0, mean=0.0, sd=float("nan"), z=0.0, d=0.0, y=0)
    mean = float(d.mean())
    sd = float(d.std(ddof=1)) if n > 1 else float("nan")
    z = mean / (sd / np.sqrt(n)) if (n > 1 and sd > 0) else float("nan")
    eff = mean / sd if (n > 1 and sd > 0) else float("nan")
    return dict(n=n, sum=float(d.sum()), mean=mean, sd=sd, z=float(z), d=float(eff), y=int(mean > 0))


def arm_summary(delta: np.ndarray, G: np.ndarray) -> dict:
    """Summary for an arm defined by its gate G (R = ~G)."""
    return evidence_from_delta(delta, ~np.asarray(G, bool))


def text_pmi(lp_obs: np.ndarray, lp_null: np.ndarray) -> float:
    """Mean over caption tokens of (conditional - null) log-probability at the observed tokens."""
    return float(np.mean(np.asarray(lp_obs, np.float64) - np.asarray(lp_null, np.float64)))


def text_pair(pmi_pos: float, pmi_neg: float) -> dict:
    d = pmi_pos - pmi_neg
    return dict(pmi_pos=float(pmi_pos), pmi_neg=float(pmi_neg), d=float(d), y=int(d > 0))
