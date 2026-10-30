"""Fig. 3 (Study 1, family P, column width): net accuracy change of GATE-M against no gate, per corruption, with 90% (thick) and 95% (thin)
paired percentile-bootstrap intervals and the +-0.05 margin lines. Nothing else on the canvas (SAP A4.2.5 items 1 and 4).

Reads runs/P2-GATE-M4/analysis.json, keys primary.per_corruption.{jpeg,noise,splice}.{delta,ci90,ci95,b,c,n,p_holm}, outcome.label.
Base: paper2/figures/src/fig_p_result.py (same data keys, redrawn at IEEE column width).
Output: paper2-tnnls/figures/fig3_study1_P.pdf (+ png preview).
"""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import figstyle as S
from figstyle import C, MINUS

S.apply()
A = S.jload("P2-GATE-M4/analysis.json")
pc = A["primary"]["per_corruption"]
assert A["outcome"]["label"] == "negative"
ROWS = [("jpeg", "JPEG, quality 10"), ("noise", "noise, $\\sigma=0.1$"), ("splice", "splice, 128 px")]
MARGIN = 0.05

fig = plt.figure(figsize=(S.COL1, 2.05))
ax = fig.add_axes([0.40, 0.235, 0.57, 0.56])
ax.set_xlim(-0.06, 0.06)
ax.set_ylim(len(ROWS) - 0.5, -0.5)
ax.axvspan(-MARGIN, MARGIN, color=C["blue"], alpha=0.0, lw=0, zorder=0)
for v in (-MARGIN, MARGIN):
    ax.axvline(v, color=C["grey"], lw=0.8, ls=(0, (3, 2)), zorder=1)
ax.axvline(0, color=C["ink"], lw=0.8, zorder=1)
for i, (k, _) in enumerate(ROWS):
    r = pc[k]
    ax.plot(r["ci95"], [i, i], color=C["blue"], lw=1.0, solid_capstyle="butt", zorder=3)
    ax.plot(r["ci90"], [i, i], color=C["blue"], lw=3.8, solid_capstyle="butt", zorder=3)
    ax.plot([r["delta"]], [i], marker="o", ms=3.0, mfc="white", mec=C["ink"], mew=0.9, ls="none", zorder=5)
ax.set_yticks(range(len(ROWS)))
ax.set_yticklabels([f"{pc[k]['label']}: {nm}" for k, nm in ROWS])
ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
ax.set_xticks([-0.05, 0, 0.05])
ax.set_xticklabels([MINUS + "0.05", "0", "+0.05"])
ax.set_xlabel("Net accuracy change, GATE-M minus no gate")
handles = [
    Line2D([], [], marker="o", ms=3.0, mfc="white", mec=C["ink"], mew=0.9, ls="none", label="net change"),
    Line2D([], [], color=C["blue"], lw=3.8, solid_capstyle="butt", label="90% interval"),
    Line2D([], [], color=C["blue"], lw=1.0, label="95% interval"),
    Line2D([], [], color=C["grey"], lw=0.8, ls=(0, (3, 2)), label=r"$\pm0.05$ margin"),
]
fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.62, 1.0), ncol=2, frameon=False, handlelength=1.8, columnspacing=1.2,
           labelspacing=0.25, handletextpad=0.5, borderaxespad=0.1)
S.save(fig, "fig3_study1_P")
print(json.dumps({k: {x: pc[k][x] for x in ("b", "c", "n", "delta", "ci90", "ci95", "p_holm")} for k, _ in ROWS}))
