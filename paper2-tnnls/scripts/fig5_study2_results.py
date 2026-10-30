"""Fig. 5 (Study 2 results, two-column): net accuracy change of the frozen learned reliability-aware fusion (LRF), with minus without reliability weights,
on the fresh preregistered fold, family L only. (a) L1 (primary, emphasised), L3 and L4 with their Holm-adjusted p; (b) L-NI in its own panel with its 90%
interval and the -0.03 margin. LG is reported in Table II only (no across-noise-types figure; GATE-AUDIT-FAMILY-LG). No GATE-M, CLIP or SigLIP number.

Reads runs/P2-LRF-L1/a6_analysis.json, keys family_L.{L1,L3,L4,L-NI}.{net,ci95,ci90,p_one,p_holm,margin,label}; branch.branch.
Output: paper2-tnnls/figures/fig5_study2_results.pdf (+ png preview).
"""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import figstyle as S
from figstyle import C, MINUS

S.apply()
FL = S.jload("P2-LRF-L1/a6_analysis.json")["family_L"]
assert FL["branch"]["branch"] == "A" and FL["L1"]["label"] == "confirmed"


def pfmt(p: float) -> str:
    return f"{p:.4f}" if p < 0.001 else f"{p:.3f}"


ROWS_A = [
    ("L1: noise, $\\sigma=0.1$", f"one-sided $p={pfmt(FL['L1']['p_one'])}$", FL["L1"], True),
    ("L3: JPEG, quality 10", f"Holm $p={pfmt(FL['L3']['p_holm'])}$", FL["L3"], False),
    ("L4: splice, 128 px", f"Holm $p={pfmt(FL['L4']['p_holm'])}$", FL["L4"], False),
]
NI = FL["L-NI"]
H_FIG, H_ROW, BOT = 1.95, 0.36, 0.55
fig = plt.figure(figsize=(S.COL2, H_FIG))


def make_axes(x0, w, nrows, xlim, ticks):
    top = BOT + 3 * H_ROW
    h = H_ROW * nrows
    ax = fig.add_axes([x0, (top - h) / H_FIG, w, h / H_FIG])
    ax.set_xlim(*xlim)
    ax.set_ylim(nrows - 0.5, -0.5)
    ax.axvline(0, color=C["ink"], lw=0.8, zorder=1)
    ax.set_xticks(ticks)
    ax.set_xticklabels([("0" if t == 0 else (MINUS if t < 0 else "") + f"{abs(t):.2f}") for t in ticks])
    ax.set_xlabel("net accuracy change, with minus without weights")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_yticks(range(nrows))
    return ax


def bar(ax, i, lo, hi, net, mk, emph):
    ax.plot([lo, hi], [i, i], color=C["green"], lw=1.8 if emph else 1.2, solid_capstyle="butt", zorder=3)
    for e in (lo, hi):
        ax.plot([e, e], [i - 0.13, i + 0.13], color=C["green"], lw=1.0, zorder=3)
    ax.plot([net], [i], marker=mk, ms=6.0 if emph else 4.6, mfc=C["green"] if emph else "white", mec=C["ink"] if emph else C["green"], mew=1.0, ls="none", zorder=5)


axa = make_axes(0.215, 0.285, 3, (-0.04, 0.13), [0, 0.05, 0.10])
axa.set_yticklabels([f"{a}\n{b}" for a, b, *_ in ROWS_A], linespacing=1.12)
for i, (_, _, rec, emph) in enumerate(ROWS_A):
    if emph:
        axa.axhspan(i - 0.5, i + 0.5, color=C["green"], alpha=0.10, lw=0, zorder=0)
    bar(axa, i, *rec["ci95"], rec["net"], "D", emph)

axb = make_axes(0.735, 0.225, 1, (-0.05, 0.08), [-0.04, 0, 0.04, 0.08])
axb.set_xlabel("net accuracy change, with minus without")
axb.set_yticklabels([f"L-NI: clean images\n90% interval"], linespacing=1.12)
bar(axb, 0, *NI["ci90"], NI["net"], "D", False)
m = -NI["margin"]
axb.plot([m, m], [-0.45, 0.45], color=C["verm"], lw=1.0, ls=(0, (3, 1.6)), zorder=2)

top = BOT + 3 * H_ROW + 0.25
fig.text(0.005, top / H_FIG, "(a)", fontsize=S.FS + 1, fontweight="bold", va="center")
fig.text(0.545, top / H_FIG, "(b)", fontsize=S.FS + 1, fontweight="bold", va="center")
handles = [
    Line2D([], [], marker="D", ms=5.2, mfc="white", mec=C["green"], mew=1.0, color=C["green"], lw=1.2, label="net change; bar: 95% interval in (a), 90% in (b)"),
    Line2D([], [], color=C["verm"], lw=1.0, ls=(0, (3, 1.6)), label=f"non-inferiority margin ({MINUS}{NI['margin']:.2f})"),
]
fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=2, frameon=False, handlelength=2.2, columnspacing=2.5, borderaxespad=0.0)
S.save(fig, "fig5_study2_results")
print(json.dumps({k: {x: FL[k].get(x) for x in ("net", "ci95", "ci90", "p_one", "p_holm")} for k in ("L1", "L3", "L4", "L-NI")}))
