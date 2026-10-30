"""Study 2 item-level margins (column width, descriptive): margin without weighting (m_none = mean_j Delta_j) against the LRF margin
(M = sum_j w_j Delta_j / sum_j w_j), one point per fresh-fold item, (a) Gaussian noise sigma 0.1 (L1 cell), (b) clean images (L-NI cell, same items).
Quadrants: upper left = correct only with LRF (b items), lower right = correct only without weighting (c items); a decision is correct iff its
margin > 0 (tie wrong), checked against the stored y_none / y_lrf on every point. Counts asserted equal to runs/P2-LRF-L1/a6_analysis.json
family_L.{L1,L-NI}.{b,c,n}. No field of the GATE-M arm is read or plotted (only the six fields in KEEP are read).

Reads: runs/P2-LRF-L1/predictions.jsonl fields condition, idx, m_none, m_lrf, y_none, y_lrf (sha256 checked against a6_analysis.json
meta.l1_predictions_sha256); runs/P2-LRF-L1/a6_analysis.json. Writes runs/P2-PAPER-FIGS/fig_margins.json. Output figures/fig_margins.pdf (+ png).
"""
from __future__ import annotations

import json

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import figstyle as S
from figstyle import C, MINUS

S.apply()
A6 = S.jload("P2-LRF-L1/a6_analysis.json")
PRED = S.RUNS / "P2-LRF-L1" / "predictions.jsonl"
assert S.sha256(PRED) == A6["meta"]["l1_predictions_sha256"], "predictions.jsonl differs from the file a6_analysis.json was computed on"
KEEP = ("condition", "idx", "m_none", "m_lrf", "y_none", "y_lrf")          # the only fields read
rows = [{k: r[k] for k in KEEP} for r in map(json.loads, open(PRED, encoding="utf-8"))]
CELLS = [("noise0.1", "L1", r"Gaussian noise, $\sigma=0.1$"), ("clean", "L-NI", "clean images")]
data, rec = {}, {}
for cond, fam, _ in CELLS:
    rr = sorted((r for r in rows if r["condition"] == cond), key=lambda r: r["idx"])
    mn, ml = np.array([r["m_none"] for r in rr]), np.array([r["m_lrf"] for r in rr])
    yn, yl = np.array([r["y_none"] for r in rr]), np.array([r["y_lrf"] for r in rr])
    assert ((mn > 0) == (yn == 1)).all() and ((ml > 0) == (yl == 1)).all()
    b, c = int(((yl == 1) & (yn == 0)).sum()), int(((yl == 0) & (yn == 1)).sum())
    ref = A6["family_L"][fam]
    assert (b, c, len(rr)) == (ref["b"], ref["c"], ref["n"]), (fam, b, c, len(rr))
    data[cond] = (mn, ml, yn, yl)
    rec[cond] = dict(family=fam, n=len(rr), b=b, c=c, both_correct=int(((yl == 1) & (yn == 1)).sum()),
                     both_wrong=int(((yl == 0) & (yn == 0)).sum()), pearson_r=float(np.corrcoef(mn, ml)[0, 1]),
                     m_none_range=[float(mn.min()), float(mn.max())], m_lrf_range=[float(ml.min()), float(ml.max())])
S.trace("fig_margins", "fig_margins.py", dict(source="runs/P2-LRF-L1/predictions.jsonl (fields " + ", ".join(KEEP) + "); a6_analysis.json family_L.{L1,L-NI}.{b,c,n}",
                                               cells=rec, label="descriptive"))

allv = np.concatenate([np.concatenate(data[c][:2]) for c in data])
lim = (np.floor(allv.min() * 10 - 0.5) / 10, np.ceil(allv.max() * 10 + 0.5) / 10)
fig = plt.figure(figsize=(S.COL1, 2.20))
side = 1.30
axs = [fig.add_axes([0.52 / S.COL1, 0.36 / 2.20, side / S.COL1, side / 2.20]),
       fig.add_axes([(0.52 + side + 0.24) / S.COL1, 0.36 / 2.20, side / S.COL1, side / 2.20])]
GREEN, VERM = C["green"], C["verm"]
for ax, (cond, fam, title), lab in zip(axs, CELLS, ("(a)", "(b)")):
    mn, ml, yn, yl = data[cond]
    conc = (yn == yl)
    bmask = (yl == 1) & (yn == 0)
    cmask = (yl == 0) & (yn == 1)
    ax.plot(lim, lim, color=C["lgrey"], lw=0.7, zorder=1)
    ax.axhline(0, color=C["ink"], lw=0.6, zorder=2)
    ax.axvline(0, color=C["ink"], lw=0.6, zorder=2)
    ax.scatter(mn[conc], ml[conc], s=3.0, color=C["lgrey"], lw=0, zorder=3)
    ax.scatter(mn[bmask], ml[bmask], s=7, marker="D", color=GREEN, lw=0, zorder=4)
    ax.scatter(mn[cmask], ml[cmask], s=9, marker="v", facecolor="white", edgecolor=VERM, lw=0.6, zorder=4)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_aspect("equal")
    ax.text(lim[0] + 0.05, lim[1] - 0.05, f"$b={rec[cond]['b']}$", ha="left", va="top", fontsize=S.FS, color=GREEN)
    ax.text(lim[1] - 0.05, lim[0] + 0.05, f"$c={rec[cond]['c']}$", ha="right", va="bottom", fontsize=S.FS, color=VERM)
    ax.set_title(f"{title}, $n={rec[cond]['n']}$", fontsize=S.FS, pad=3)
    ax.text(-0.05, 1.11, lab, transform=ax.transAxes, fontsize=S.FS + 1, fontweight="bold", ha="right", va="bottom")
    ax.set_xlabel(r"margin, no weighting", labelpad=1.5)
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.5))
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))
    fmt = plt.FuncFormatter(lambda v, _: "0" if abs(v) < 1e-9 else f"{v:g}".replace("-", MINUS))
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
axs[0].set_ylabel(r"margin with LRF, $M$", labelpad=1.5)
plt.setp(axs[1].get_yticklabels(), visible=False)
h = [Line2D([], [], marker="D", ms=3.0, color=GREEN, ls="none", label="correct only with LRF"),
     Line2D([], [], marker="v", ms=3.4, mfc="white", mec=VERM, mew=0.6, ls="none", label="correct only without"),
     Line2D([], [], marker="o", ms=2.0, color=C["lgrey"], ls="none", label="same decision")]
fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, handletextpad=0.2, columnspacing=0.9,
           borderaxespad=0.1)
S.save(fig, "fig_margins")
print(rec)
