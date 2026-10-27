"""The per-test record that SAP 2.3 requires 'with every test': b, c, n_d, n, both accuracies, effect size (b - c)/n with a paired percentile bootstrap CI at 95 percent
and at 98.33 percent (the Bonferroni equivalent of the first Holm step), theta = b/n_d with its Clopper-Pearson interval, the exact p and the mid-p (sensitivity only),
and the 90 percent CI against the +/-0.05 equivalence margin of SAP section 9. Items with a NaN outcome on either side are dropped and counted."""
from __future__ import annotations

import numpy as np

from exp_p2.gate import stats

EQUIV_MARGIN = 0.05


def _pct(boots: np.ndarray, level: float) -> list[float]:
    a = (100 - level) / 2
    return [float(np.quantile(boots, a / 100)), float(np.quantile(boots, 1 - a / 100))]


def report_test(y_a, y_b, *, n_boot: int = 10000, seed=None) -> dict:
    """y_a is the arm that is hoped to win (GATE-M); y_b the comparator. Values are 0/1 (NaN = missing)."""
    a, b_ = np.asarray(y_a, float), np.asarray(y_b, float)
    ok = ~(np.isnan(a) | np.isnan(b_))
    a, b_ = a[ok], b_[ok]
    mc = stats.mcnemar_exact(a, b_)
    n = int(ok.sum())
    out = dict(b=mc["b"], c=mc["c"], n_d=mc["n_discordant"], n=n, n_dropped=int((~ok).sum()), p=mc["p"], p_mid=stats.mcnemar_midp(mc["b"], mc["c"]),
               acc_a=float(a.mean()) if n else float("nan"), acc_b=float(b_.mean()) if n else float("nan"), delta=(mc["b"] - mc["c"]) / n if n else float("nan"))
    if n >= 2:
        d = a - b_
        idx = np.random.default_rng(seed).integers(0, n, size=(n_boot, n))
        boots = d[idx].mean(axis=1)
        out.update(ci95=_pct(boots, 95.0), ci9833=_pct(boots, 98.33), ci90=_pct(boots, 90.0))
        out["equivalent_within_0p05"] = bool(out["ci90"][0] > -EQUIV_MARGIN and out["ci90"][1] < EQUIV_MARGIN)
    else:
        out.update(ci95=[float("nan")] * 2, ci9833=[float("nan")] * 2, ci90=[float("nan")] * 2, equivalent_within_0p05=None)
    out["theta"] = mc["b"] / mc["n_discordant"] if mc["n_discordant"] else float("nan")
    out["theta_cp95"] = list(stats.clopper_pearson(mc["b"], mc["n_discordant"], 0.95))
    return out
