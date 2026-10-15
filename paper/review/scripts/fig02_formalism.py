"""Figure 2: the commitment process and where the five design choices C1 to C5 act.

A vector schematic, no data. Content follows paper/review/sections/03-notation.tex (Section 3.1, 3.2) and
Algorithm 2 (GENERATE): training fixes C1, C2 and trains the predictor C3; the sampler repeats
state -> network (C3) -> position law and value law (C4) -> commit -> optional revision (C5).

    python paper/review/scripts/fig02_formalism.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from figstyle import C, TEXTWIDTH_IN, save, setup

setup()
W = TEXTWIDTH_IN * 72
H = 272.0
FS = 7.0
LH = 8.8
fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, H / 72))
fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")

CHIP = {"C1": C["sky"], "C2": C["yellow"], "C3": C["green"], "C4": C["orange"], "C5": C["purple"]}
ARR = dict(arrowstyle="-|>", mutation_scale=6, lw=0.8, color=C["black"], shrinkA=0, shrinkB=0)
ARR_D = dict(arrowstyle="-|>", mutation_scale=6, lw=0.8, color="#404040", linestyle=(0, (3, 2)), shrinkA=0, shrinkB=0)


def box(xc, yc, w, h, title, sub, chip=None, dashed=False):
    kw = dict(boxstyle="square,pad=0", linewidth=0.8, edgecolor="#404040" if dashed else C["black"], facecolor="white", zorder=2)
    if dashed:
        kw["linestyle"] = (0, (3, 2))
    ax.add_patch(FancyBboxPatch((xc - w / 2, yc - h / 2), w, h, **kw))
    lines = [(title, "bold")] + [(t, "normal") for t in sub]
    y0 = yc - (len(lines) - 1) * LH / 2 + (3 if chip else 0)
    for i, (t, wt) in enumerate(lines):
        ax.text(xc, y0 + i * LH, t, ha="center", va="center", fontsize=FS, fontweight=wt, zorder=3,
                color="#202020")
    if chip:
        cw, ch = 17, 10
        ax.add_patch(FancyBboxPatch((xc - w / 2 + 3, yc - h / 2 - ch / 2), cw, ch, boxstyle="round,pad=0,rounding_size=2",
                                    facecolor=CHIP[chip], edgecolor=C["black"], linewidth=0.6, zorder=4))
        ax.text(xc - w / 2 + 3 + cw / 2, yc - h / 2, chip, ha="center", va="center", fontsize=FS, fontweight="bold", zorder=5)


def arrow(p, q, dashed=False):
    ax.annotate("", xy=q, xytext=p, arrowprops=ARR_D if dashed else ARR, zorder=1)


def line(pts, dashed=False):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color="#404040" if dashed else C["black"], lw=0.8, ls=(0, (3, 2)) if dashed else "-", zorder=1)


# ---- training band
ax.text(4, 9, "Training: fixes C1, C2 and fits the predictor C3", fontsize=7.5, fontweight="bold", va="center")
yT, hT, wT = 45, 46, 84
XT = [47, 143, 239, 335]
box(XT[0], yT, wT, hT, "Data", [r"sequence $x\sim q$", "over vocabulary $\\mathcal{V}$"])
box(XT[1], yT, wT, hT, "Channel", ["corrupts positions:", "erasure, uniform,", "Gaussian"], "C1")
box(XT[2], yT, wT, hT, "Reveal law", ["which positions are clean", "together; loss weight"], "C2")
box(XT[3], yT, wT, hT, "Predictor", [r"fitted $p_\theta$: marginals,", "scores or velocity"], "C3")
for a, b in zip(XT[:-1], XT[1:]):
    arrow((a + wT / 2, yT), (b - wT / 2, yT))

# separator
ax.plot([0, W], [86, 86], color=C["grey"], lw=0.5, ls=(0, (1, 2)), zorder=0)

# ---- sampling band
ax.text(4, 97, r"Sampling loop, for $n=1,\dots,T$", fontsize=7.5,
        fontweight="bold", va="center")
XA = [82, 207, 332]
yA, yB, hA, wA = 146, 230, 40, 108
box(XA[0], yA, wA, hA, "State", [r"$s_n=(z_n,m_n)$", "partly revealed sequence,", "memory"])
box(XA[1], yA, wA, hA, "Network", [r"marginals $p_\theta^i(\cdot\mid s_n)$", "at masked positions"], "C3")
box(XA[2], yA, wA, hA, "Position law", [r"$\rho(A\mid s)$: choose the", r"set $A_n\subseteq M_n$"], "C4")
box(XA[2], yB, wA, hA, "Value law", [r"$\kappa(y\mid A,s)$: temperature,", "argmax, truncation, guidance"], "C4")
box(XA[1], yB, wA, hA, "Commit", [r"write $y$ at the positions $A_n$;", r"$k_n=|A_n|$ tokens this step"])
box(XA[0], yB, wA, hA, "Revision (optional)", [r"remask a set $R_n$:", r"$z_n^{R_n}\leftarrow\mathsf{m}$"], "C5", dashed=True)
arrow((XA[0] + wA / 2, yA), (XA[1] - wA / 2, yA))
arrow((XA[1] + wA / 2, yA), (XA[2] - wA / 2, yA))
arrow((XA[2], yA + hA / 2), (XA[2], yB - hA / 2))
arrow((XA[2] - wA / 2, yB), (XA[1] + wA / 2, yB))
arrow((XA[1] - wA / 2, yB), (XA[0] + wA / 2, yB), dashed=True)
arrow((XA[0], yB - hA / 2), (XA[0], yA + hA / 2), dashed=True)
# commit without revision skips C5: solid return path below the boxes
yR = yB + hA / 2 + 10
line([(XA[1], yB + hA / 2), (XA[1], yR), (XA[0] - wA / 2 - 12, yR), (XA[0] - wA / 2 - 12, yA)])
arrow((XA[0] - wA / 2 - 12, yA), (XA[0] - wA / 2, yA))
ax.text(XA[0] - wA / 2 - 20, (yA + yR) / 2 + 8, "no revision", rotation=90, fontsize=7, ha="center", va="center")
# output
ax.text(XA[0], yA - hA / 2 - 9, r"after $T$ steps: output $z_T$", fontsize=7, ha="center", va="center")
# trained predictor feeds the network
line([(XT[3], yT + hT / 2), (XT[3], 80)], dashed=True)
line([(XT[3], 80), (XA[1], 80)], dashed=True)
arrow((XA[1], 80), (XA[1], yA - hA / 2 - 0), dashed=True)
save(fig, "fig02-formalism")
