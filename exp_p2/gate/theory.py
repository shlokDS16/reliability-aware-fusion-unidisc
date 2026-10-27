"""Proposition 4 (v2 section 5.3) as a plug-in calculator: when does gating raise the SNR of the additive image-direction statistic S = sum_j I_j Delta_j?

Per-token paired evidence Delta_j: clean tokens mean mu, variance sigma2 (kept with probability 1-alpha); corrupted tokens mean mu_c, variance sigma2_c (kept
with probability 1-beta); corrupted fraction rho; tokens independent (approximation). With m tokens:
    E S   = m [ (1-rho)(1-alpha) mu + rho (1-beta) mu_c ]
    Var S = m [ (1-rho){(1-alpha) sigma2 + alpha(1-alpha) mu^2} + rho{(1-beta) sigma2_c + beta(1-beta) mu_c^2} ]
No gate: alpha = beta = 0. Special case mu_c = 0: gate raises SNR iff  rho sigma2_c (beta - 2 alpha + alpha^2) > alpha (1-alpha)(1-rho)(sigma2 + mu^2).
Refutation rule stated in advance: if the plug-in sign disagrees with the observed GATE-M-minus-none sign for a corruption whose observed difference has a CI
excluding 0, the independent-token model is refuted for that corruption."""
from __future__ import annotations

import math


def mean_var(m: int, rho: float, alpha: float, beta: float, mu: float, sigma2: float, mu_c: float, sigma2_c: float) -> tuple[float, float]:
    e = m * ((1 - rho) * (1 - alpha) * mu + rho * (1 - beta) * mu_c)
    v = m * ((1 - rho) * ((1 - alpha) * sigma2 + alpha * (1 - alpha) * mu ** 2) + rho * ((1 - beta) * sigma2_c + beta * (1 - beta) * mu_c ** 2))
    return e, v


def snr(m: int, rho: float, alpha: float, beta: float, mu: float, sigma2: float, mu_c: float, sigma2_c: float) -> float:
    e, v = mean_var(m, rho, alpha, beta, mu, sigma2, mu_c, sigma2_c)
    return e / math.sqrt(v) if v > 0 else float("nan")


def gating_helps(m, rho, alpha, beta, mu, sigma2, mu_c, sigma2_c) -> bool:
    """Plug-in prediction: SNR after gating (alpha, beta) exceeds SNR before (0, 0)."""
    return snr(m, rho, alpha, beta, mu, sigma2, mu_c, sigma2_c) > snr(m, rho, 0.0, 0.0, mu, sigma2, mu_c, sigma2_c)


def special_case_inequality(rho, alpha, beta, mu, sigma2, sigma2_c) -> bool:
    """The mu_c = 0 closed form (corrected v1 inequality)."""
    return rho * sigma2_c * (beta - 2 * alpha + alpha ** 2) > alpha * (1 - alpha) * (1 - rho) * (sigma2 + mu ** 2)


def plug_in_from_deltas(delta: "np.ndarray", corrupted: "np.ndarray", flagged: "np.ndarray") -> dict:
    """Estimate the inputs from one condition's per-token Delta, the changed-code labels Z and GATE's flags (pooled over items by the caller if desired)."""
    import numpy as np
    d, z, f = np.asarray(delta, float), np.asarray(corrupted, bool), np.asarray(flagged, bool)
    rho = float(z.mean())
    clean, cor = d[~z], d[z]
    out = dict(rho=rho, mu=float(clean.mean()) if clean.size else float("nan"), sigma2=float(clean.var(ddof=1)) if clean.size > 1 else float("nan"),
               mu_c=float(cor.mean()) if cor.size else float("nan"), sigma2_c=float(cor.var(ddof=1)) if cor.size > 1 else float("nan"),
               alpha_obs=float(f[~z].mean()) if clean.size else float("nan"), beta_obs=float(f[z].mean()) if cor.size else float("nan"), m=int(d.size))
    if all(np.isfinite(v) for v in out.values()):
        out["predicted_helps"] = bool(gating_helps(out["m"], out["rho"], out["alpha_obs"], out["beta_obs"], out["mu"], out["sigma2"], out["mu_c"], out["sigma2_c"]))
    return out
