"""Exploratory Gaussian-noise severity sweep (plan research/paper2/tnnls/EXPLORATORY-PLAN-SEVERITY-2026-10-31.md), one column, two panels.
(a) accuracy of the unweighted sum and the frozen LRF against sigma (0 = clean); (b) LRF minus unweighted sum with its 95% paired percentile bootstrap
interval. Levels 0 and 0.1 come from the confirmatory run (runs/P2-LRF-L1), the others from runs/P2-LRF-SEV; all read from
runs/P2-LRF-SEV/sev_analysis.json. Exploratory; no test. Values written to runs/P2-PAPER-FIGS/fig_severity.json.
    python scripts/fig_severity.py      (from paper2-tnnls/)"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figstyle as S
from figstyle import C

S.apply()
R = S.jload("P2-LRF-SEV/sev_analysis.json")
assert R["positive_control"]["ok"]
LV = ["0", "0.05", "0.1", "0.2", "0.3"]
sig = [float(v) for v in LV]
none = [R["levels"][v]["NONE"] for v in LV]
lrf = [R["levels"][v]["LRF"] for v in LV]
d = [R["levels"][v]["LRF_minus_NONE"]["diff"] for v in LV]
lo = [R["levels"][v]["LRF_minus_NONE"]["ci95"][0] for v in LV]
hi = [R["levels"][v]["LRF_minus_NONE"]["ci95"][1] for v in LV]

fig, (a, b) = plt.subplots(1, 2, figsize=(S.COL1, 1.55), gridspec_kw=dict(wspace=0.55))
fig.subplots_adjust(left=0.13, right=0.98, bottom=0.25, top=0.9)
a.plot(sig, none, "-o", color=C["grey"], ms=3, label="Unweighted sum")
a.plot(sig, lrf, "-s", color=C["blue"], ms=3, label="LRF (frozen)")
a.axvline(0.1, color=C["lgrey"], lw=0.6, ls=":", zorder=0)
a.set_xlabel(r"Gaussian noise $\sigma$")
a.set_ylabel("Accuracy")
a.set_xticks(sig, ["0", ".05", ".1", ".2", ".3"])
a.set_ylim(0.55, 0.95)
a.legend(frameon=False, loc="lower left", handlelength=1.4, borderaxespad=0.1)
S.panel_letter(a, "a", dx=-0.25)

b.axhline(0, color=C["ink"], lw=0.5)
b.axvline(0.1, color=C["lgrey"], lw=0.6, ls=":", zorder=0)
b.errorbar(sig, d, yerr=[[x - l for x, l in zip(d, lo)], [h - x for x, h in zip(d, hi)]], fmt="s", color=C["blue"], ms=3, capsize=1.5, elinewidth=0.7)
b.set_xlabel(r"Gaussian noise $\sigma$")
b.set_ylabel(r"LRF $" + S.MINUS + "$ unweighted")
b.set_xticks(sig, ["0", ".05", ".1", ".2", ".3"])
b.set_ylim(-0.02, 0.14)
S.panel_letter(b, "b", dx=-0.3)

S.save(fig, "fig_severity")
S.trace("fig_severity", "fig_severity.py", dict(source="runs/P2-LRF-SEV/sev_analysis.json", sigma=sig, none=none, lrf=lrf, diff=d, ci_lo=lo, ci_hi=hi,
                                                 note="exploratory; levels 0 and 0.1 from runs/P2-LRF-L1; dotted line = fitted (confirmatory) level"))
print("ok")
