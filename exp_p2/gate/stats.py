"""Small statistics used by the headroom decision and the M4 analysis (stdlib + numpy; no scipy)."""
from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np


def mcnemar_exact(y_a, y_b) -> dict:
    """Exact two-sided McNemar test on paired binary outcomes. b = items where A is right and B wrong; c = the reverse; p from Binomial(b+c, 1/2)."""
    a, b_ = np.asarray(y_a, float), np.asarray(y_b, float)
    ok = ~(np.isnan(a) | np.isnan(b_))
    a, b_ = a[ok] > 0.5, b_[ok] > 0.5
    b, c = int((a & ~b_).sum()), int((~a & b_).sum())
    n = b + c
    if n == 0:
        return dict(b=b, c=c, n_discordant=0, p=1.0, n=int(ok.sum()))
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2.0 ** n
    return dict(b=b, c=c, n_discordant=n, p=float(min(1.0, 2.0 * tail)), n=int(ok.sum()))


def holm(pvals: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values (monotone), in the input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj, run = [0.0] * m, 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * pvals[i]))
        adj[i] = run
    return adj


def paired_diff(a, b) -> dict:
    """Mean of (a - b) over items with both finite, its SE (sd/sqrt(n)) and the number of items dropped for NaN/inf."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    d = (a - b)[ok]
    n = int(d.size)
    if n < 2:
        return dict(diff=float(d.mean()) if n else float("nan"), se=float("nan"), n=n, n_dropped=int((~ok).sum()), sd=float("nan"))
    sd = float(d.std(ddof=1))
    return dict(diff=float(d.mean()), se=sd / math.sqrt(n), n=n, n_dropped=int((~ok).sum()), sd=sd)


def power_nd(theta: float, alpha_prime: float, power: float = 0.8) -> float:
    """Discordant pairs needed (normal approximation to the sign test, v2 section 9): [(0.5 z_{1-a/2} + z_power sqrt(theta(1-theta))) / (theta - 0.5)]^2."""
    nd = NormalDist()
    z_a, z_p = nd.inv_cdf(1 - alpha_prime / 2), nd.inv_cdf(power)
    return float(((0.5 * z_a + z_p * math.sqrt(theta * (1 - theta))) / (theta - 0.5)) ** 2)


def exact_sign_power(n_d: int, theta: float, alpha_prime: float) -> float:
    """Exact power of the two-sided sign test with n_d discordant pairs when each favours the treatment with probability theta."""
    if n_d <= 0:
        return 0.0
    pmf = [math.comb(n_d, k) * theta ** k * (1 - theta) ** (n_d - k) for k in range(n_d + 1)]
    pw = 0.0
    for k in range(n_d + 1):
        kk = min(k, n_d - k)
        p = min(1.0, 2.0 * sum(math.comb(n_d, i) for i in range(kk + 1)) / 2.0 ** n_d)
        if p <= alpha_prime:
            pw += pmf[k]
    return float(pw)


def exact_sign_min_n(theta: float, alpha_prime: float, power: float = 0.8, stay: int = 5, n_max: int = 1000) -> int:
    """Smallest n_d at which the exact two-sided sign test has power >= `power` and keeps it for the next `stay` values (SAP 4.2 Table A: 35, 42, 43 for theta 0.75)."""
    for n in range(2, n_max):
        if all(exact_sign_power(m, theta, alpha_prime) >= power for m in range(n, n + stay + 1)):
            return n
    raise ValueError("no n_d up to n_max reaches the power")


def mcnemar_midp(b: int, c: int) -> float:
    """Mid-p version of the exact two-sided McNemar test (sensitivity only; it does not guarantee size): 2 * (P(X < k) + 0.5 P(X = k)), k = min(b, c), X ~ Bin(b + c, 1/2)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    below = sum(math.comb(n, i) for i in range(k)) / 2.0 ** n
    at = math.comb(n, k) / 2.0 ** n
    return float(min(1.0, 2.0 * (below + 0.5 * at)))


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Exact (Clopper-Pearson) interval of a binomial proportion k/n."""
    if n == 0:
        return float("nan"), float("nan")
    from scipy.stats import beta
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return lo, hi


def wilson_ci(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Wilson score interval of a binomial proportion."""
    if n == 0:
        return float("nan"), float("nan")
    z = NormalDist().inv_cdf(1 - (1 - level) / 2)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)
