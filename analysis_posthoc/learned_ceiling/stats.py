"""Intervals and labels (plan Section 8). No p-value is computed anywhere in this module."""
from __future__ import annotations

import numpy as np
from scipy.stats import beta, norm


def wilson(k: int, n: int, level: float = 0.95) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    zq = norm.ppf(0.5 + level / 2)
    p = k / n
    den = 1 + zq ** 2 / n
    centre = (p + zq ** 2 / (2 * n)) / den
    half = zq * np.sqrt(p * (1 - p) / n + zq ** 2 / (4 * n ** 2)) / den
    return [float(centre - half), float(centre + half)]


def clopper_pearson(k: int, n: int, level: float = 0.95) -> list[float]:
    if n == 0:
        return [0.0, 1.0]
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return [lo, hi]


def contrast(ya: np.ndarray, yr: np.ndarray, boot_idx: np.ndarray) -> dict:
    """Paired accuracy contrast arm minus reference over the same items. ya, yr: bool [n]."""
    ya, yr = ya.astype(bool), yr.astype(bool)
    n = ya.size
    b = int((ya & ~yr).sum())
    c = int((~ya & yr).sum())
    nd = b + c
    diff = (ya.astype(np.float64) - yr.astype(np.float64))
    boots = diff[boot_idx].mean(1)
    lo, hi = np.quantile(boots, [0.025, 0.975])
    cp = clopper_pearson(b, nd)
    if nd == 0:
        lab = "identical"
    elif cp[0] > 0.5:
        lab = "above"
    elif cp[1] < 0.5:
        lab = "below"
    else:
        lab = "not distinguishable"
    return dict(n=n, acc_arm=float(ya.mean()), acc_ref=float(yr.mean()), diff=float(diff.mean()), ci95=[float(lo), float(hi)],
                b=b, c=c, n_d=nd, theta=(b / nd if nd else None), theta_cp95=cp, label=lab,
                discordance_cp95_upper=clopper_pearson(nd, n)[1])
