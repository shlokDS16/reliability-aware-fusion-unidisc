"""Minimum detectable net gain of the exact two-sided McNemar test at a completed n (SAP A3.1 item 2, A3b.6 item 5, A3b.3 item 6). CPU only; no data.

The same machinery as `analysis/paper2/gate/a2_power.py` (exact favourable-tail rejection with the discordant count n_d ~ Binomial(n, pi_d), theta searched on a grid of step 0.005, power 0.8),
re-implemented here so that `exp_p2` does not import from `analysis/`. Net gain Delta = pi_d * (2 theta - 1). Every number is an assumption-conditional calculation (pi_d and theta are ASSUMED), not a forecast
and not a result. alpha' is the per-test threshold: 0.025 for family S2 (Holm m = 2), 0.05 for family B (m = 1). `reproduces_a3_table()` checks the code against the A3.1 table."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
from scipy import stats as ss

PI_D = (0.05, 0.10, 0.15, 0.20)          # the discordance grid of the A3.1 table
POWER = 0.8
THETA_GRID = np.arange(0.5, 1.0001, 0.005)


@lru_cache(maxsize=None)
def _kcrit(nd: int, alpha_prime: float) -> int:
    """Largest c with 2 P(Bin(nd, 0.5) <= c) <= alpha'; -1 if none."""
    if nd == 0:
        return -1
    cs = np.arange(nd + 1)
    ok = 2 * ss.binom.cdf(cs, nd, 0.5) <= alpha_prime
    return int(cs[ok].max()) if ok.any() else -1


def power(n: int, pi_d: float, theta: float, alpha_prime: float) -> float:
    """Exact favourable-direction rejection probability with n items, discordance pi_d and share theta of discordant items favouring the first arm."""
    nds = np.arange(n + 1)
    w = ss.binom.pmf(nds, n, pi_d)
    tot = 0.0
    for i in nds:
        if w[i] <= 1e-12:
            continue
        kc = _kcrit(int(i), alpha_prime)
        if kc >= 0:
            tot += float(w[i]) * float(ss.binom.cdf(kc, int(i), 1 - theta))
    return tot


def mde(n: int, pi_d: float, alpha_prime: float) -> dict:
    """Smallest net gain with power 0.8 at (n, pi_d, alpha'); net_gain None if unreachable even at theta = 1."""
    for t in THETA_GRID:
        if power(int(n), pi_d, float(t), alpha_prime) >= POWER:
            return dict(pi_d=pi_d, theta=round(float(t), 3), net_gain=round(pi_d * (2 * float(t) - 1), 3))
    return dict(pi_d=pi_d, theta=None, net_gain=None)


def mde_table(n: int, alpha_prime: float, pi_ds=PI_D) -> dict:
    """{pi_d: net gain or None} at the completed n, plus the assumptions in words."""
    rows = {f"{p:g}": mde(n, p, alpha_prime) for p in pi_ds}
    return dict(n=int(n), alpha_prime=alpha_prime, power=POWER, by_pi_d={k: v["net_gain"] for k, v in rows.items()}, theta_at_mde={k: v["theta"] for k, v in rows.items()},
                note="minimum detectable net gain (b - c)/n for power 0.8, exact two-sided McNemar, favourable tail; pi_d (discordance) and theta (split) are ASSUMED, not forecasts (SAP A3.1)")


def mde_sentence(n: int, alpha_prime: float) -> str:
    """'minimum detectable net gain at the achieved n = 238 is 0.055 at an assumed discordance of 0.10 (0.069 at 0.15, 0.079 at 0.20; unreachable at 0.05); ...'"""
    t = mde_table(n, alpha_prime)["by_pi_d"]
    fmt = lambda k: ("unreachable" if t[k] is None else f"{t[k]:.3f}")             # noqa: E731
    return (f"minimum detectable net gain at the achieved n = {n} is {fmt('0.1')} at an assumed discordance of 0.10 ({fmt('0.15')} at 0.15, {fmt('0.2')} at 0.20, {fmt('0.05')} at 0.05; "
            f"power 0.8, exact two-sided McNemar, alpha' {alpha_prime:g}; discordance and split are assumed, not forecasts)")


def reproduces_a3_table() -> bool:
    """The A3.1 table, n = 300 at alpha' 0.025 (S2) and 0.05 (B), pi_d 0.10: 0.057 and 0.053."""
    return bool(mde(300, 0.10, 0.025)["net_gain"] == 0.057 and mde(300, 0.10, 0.05)["net_gain"] == 0.053)
