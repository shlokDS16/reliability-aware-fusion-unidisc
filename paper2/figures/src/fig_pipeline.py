"""F2: the GATE pipeline (conceptual; no data, reads nothing from runs/).

Symbols and steps follow paper2/sections/method.tex: Table 1 (notation), Eq. levels / suspicion (B_j, D_j, u_j), Algorithms
ReliabilityScores, CalibrateThreshold (CRC threshold, Eq. crc), Gate, the marginalise arm (GATE-M, Eq. delta), ReInfill (GATE-I),
two-way fusion (Eq. lda). Grid sizes are schematic (the real image grid is 32 x 32 = m tokens, protocol.tex).
Output: paper2/figures/F2_pipeline.pdf + .png (190 mm, double column)."""
from __future__ import annotations

import style as S
from style import COL, arrow, box, cell, pair_glyph, txt

S.apply()
W, H = S.W2, 101.0
fig, ax = S.canvas(W, H, y0=7.0)

G8 = 8
CAP = 6
GW = 15.2
BLOCK = {(r, c) for r in range(3, 6) for c in range(3, 6)}          # a corrupted patch (schematic)
SK = {(r, c) for r in range(G8) for c in range(G8) if (2 * r + 3 * c) % 4 == 0}
FLAG_TP = {(3, 3), (3, 4), (4, 3), (4, 4), (4, 5), (5, 4)}            # flagged and corrupted
FLAG_FA = {(1, 6), (6, 1)}                                           # flagged but clean (false alarms)
FLAGS = FLAG_TP | FLAG_FA


def grid(base="clean", corrupt=BLOCK, query=None, refill=None):
    g = S.grid_of(G8, base)
    for (r, c) in corrupt or ():
        g[r][c] = "corrupt"
    for (r, c) in query or ():
        g[r][c] = "query"
    for (r, c) in refill or ():
        g[r][c] = "refill"
    return g


# ---- panel frames ----------------------------------------------------------------------------------------------------
PX = [(0.4, 25.0), (29.0, 68.0), (72.0, 108.0), (112.0, 152.0), (156.0, 189.6)]
TITLES = ["1  Tokenise", "2  Score, caption withheld", "3  Calibrate, then flag", "4  Use $R$ or repair $G$", "5  Evidence, decision"]
YB, YT = 21.4, 93.0
for (xa, xb), t in zip(PX, TITLES):
    box(ax, xa, YB, xb - xa, YT - YB, fc="white", ec=COL["faint"], lw=0.6)
    txt(ax, (xa + xb) / 2, 96.8, t, fs=7.4, ha="center", weight="bold")


def mid(i):
    return (PX[i][0] + PX[i][1]) / 2


# ---- 1: tokenise -----------------------------------------------------------------------------------------------------
x1 = PX[0][0]
box(ax, x1 + 1.6, 83.2, 10.0, 6.4, fc=COL["box"], ec=COL["clean_edge"])
txt(ax, x1 + 6.6, 86.4, "image", fs=6.8, ha="center")
box(ax, x1 + 12.6, 83.2, 10.0, 6.4, fc=COL["box"], ec=COL["clean_edge"])
txt(ax, x1 + 17.6, 86.4, "caption", fs=6.8, ha="center")
ax.plot([x1 + 6.6, x1 + 6.6, x1 + 17.6, x1 + 17.6], [83.2, 80.8, 80.8, 83.2], color=COL["ink"], lw=0.7)
arrow(ax, (x1 + 12.1, 80.8), (x1 + 12.1, 75.8), ms=5)
txt(ax, x1 + 13.4, 78.2, "UniDisc\ntokens", fs=6.2, ha="left", color=COL["sub"], linespacing=1.1)
gx1 = x1 + 4.6
g1 = pair_glyph(ax, gx1, 75.0, ["cap"] * CAP, grid(), w=GW, fs=0)
txt(ax, gx1 - 0.5, g1["strip"][1] + g1["strip"][3] / 2, r"$\tilde t$", fs=7, ha="right")
txt(ax, gx1 - 0.5, g1["grid"][1] + g1["grid"][3] / 2, r"$\tilde v$", fs=7, ha="right")
txt(ax, mid(0), 52.0, r"$\tilde x=(\tilde t,\tilde v)$", fs=7.6, ha="center")
txt(ax, mid(0), 47.8, "observed pair,\npossibly corrupted", fs=6.4, ha="center", color=COL["sub"], linespacing=1.15)
txt(ax, mid(0), 39.5, r"$v^{\circ}$: clean image" + "\ntokens, so that" + "\n" + r"$Z_j=\mathbb{1}[\tilde v_j\neq v^{\circ}_j]$" + "\n(evaluation only)",
    fs=6.2, ha="center", color=COL["sub"], linespacing=1.2)
p1_right = (g1["right"], g1["grid"][1] + g1["grid"][3] / 2)

# ---- 2: score with the caption withheld --------------------------------------------------------------------------------
x2 = PX[1][0]
txt(ax, mid(1), 90.2, "ReliabilityScores", fs=6.4, ha="center", color=COL["sub"], style="italic")
gx2 = x2 + 2.6
g2 = pair_glyph(ax, gx2, 80.0, ["capmask"] * CAP, grid(query=SK, corrupt=BLOCK - SK), w=GW, fs=4.2)
txt(ax, gx2 + GW + 1.4, g2["strip"][1] + g2["strip"][3] / 2, "caption\nwithheld", fs=6.2, ha="left", color=COL["sub"], linespacing=1.1)
txt(ax, gx2 + GW + 1.4, g2["grid"][1] + g2["grid"][3] / 2, "one group\n" + r"$S_k$ scored," + "\nrest visible", fs=6.2, ha="left", color=COL["sub"], linespacing=1.15)
txt(ax, mid(1), 56.0, r"$B_j=\log p_\theta(x_j\mid x^{I}_{-S_{k(j)}},\varnothing^{T})$", fs=6.4, ha="center")
txt(ax, mid(1), 52.4, r"$D_j=\log p_\theta(x_j\mid\varnothing^{I},\varnothing^{T})$", fs=6.4, ha="center")
txt(ax, mid(1), 49.0, r"all $K$ groups; $D_j$ cached", fs=6.0, ha="center", color=COL["sub"])
YU = 38.5
box(ax, x2 + 5.0, YU - 3.6, PX[1][1] - x2 - 10.0, 7.2, fc="white", ec=COL["flag"], lw=1.1)
txt(ax, mid(1), YU, r"$u_j=-q_j=-(B_j-D_j)$", fs=7.2, ha="center")
txt(ax, mid(1), 31.6, "larger $u_j$: more suspicious", fs=6.2, ha="center", color=COL["sub"])
txt(ax, mid(1), 28.0, "no candidate caption seen", fs=6.2, ha="center", color=COL["sub"])
arrow(ax, (p1_right[0] + 3.0, p1_right[1]), (gx2 - 0.9, p1_right[1]), ms=6)

# ---- 3: calibrate, then flag ------------------------------------------------------------------------------------------
x3 = PX[2][0]
box(ax, x3 + 1.2, 53.4, PX[2][1] - x3 - 2.4, 37.2, fc=COL["box"], ec=COL["faint"], lw=0.6, ls=(0, (3, 1.6)))
txt(ax, mid(2), 88.4, "CalibrateThreshold", fs=6.4, ha="center", color=COL["sub"], style="italic")
for k in range(3):
    ox = x3 + 3.4 + 1.5 * (2 - k)
    oy = 84.0 - 1.1 * (2 - k)
    pair_glyph(ax, ox, oy, ["cap"] * 4, S.grid_of(4), w=7.0, fs=0)
txt(ax, x3 + 16.0, 80.0, r"$\mathcal{D}_{\mathrm{cal}}$: $n_{\mathrm{cal}}$" + "\nclean pairs", fs=6.6, ha="left", linespacing=1.15)
txt(ax, mid(2), 69.8, r"$\hat\tau=\inf\{\tau:$", fs=6.6, ha="center")
txt(ax, mid(2), 65.9, r"$\frac{n_{\mathrm{cal}}}{n_{\mathrm{cal}}+1}\widehat{R}(\tau)+\frac{1}{n_{\mathrm{cal}}+1}\leq\alpha\}$", fs=6.6, ha="center")
txt(ax, mid(2), 60.4, r"$\mathbb{E}[L_{\mathrm{test}}(\hat\tau)]\leq\alpha$", fs=7.0, ha="center", weight="bold")
txt(ax, mid(2), 56.4, "clean items only; nothing else\nis guaranteed", fs=6.0, ha="center", color=COL["sub"], linespacing=1.1)
gx3 = x3 + 2.0
g3 = pair_glyph(ax, gx3, 48.0, ["cap"] * CAP, grid(), flags=FLAGS, w=GW, fs=0)
YG3 = g3["grid"][1] + g3["grid"][3] / 2
arrow(ax, (gx3 + GW / 2, 53.4), (gx3 + GW / 2, 48.4), ms=5, color=COL["ink"])
txt(ax, gx3 + GW / 2 + 1.0, 51.0, r"$\hat\tau$", fs=7.0, ha="left")
txt(ax, g3["right"] + 1.8, 41.0, "flag if\n" + r"$u_j>\hat\tau$", fs=6.4, ha="left", linespacing=1.15)
txt(ax, mid(2), 26.2, r"$G=\{j:u_j>\hat\tau\}$", fs=6.8, ha="center")
txt(ax, mid(2), 23.8, r"$R$: complement of $G$", fs=6.2, ha="center", color=COL["sub"])
arrow(ax, (PX[1][1] - 5.0, YU), (gx3 - 0.6, YG3), ms=6)

# ---- 4: GATE-M and GATE-I ----------------------------------------------------------------------------------------------
x4, x4b = PX[3]
bm = (x4 + 0.8, 57.0, x4b - x4 - 1.6, 33.8)
bi = (x4 + 0.8, 24.0, x4b - x4 - 1.6, 31.6)
box(ax, *bm, fc="white", ec=COL["gate"], lw=1.2)
box(ax, *bi, fc="white", ec=COL["gatei"], lw=1.2)
txt(ax, bm[0] + 1.6, 87.6, "GATE-M", fs=7.6, weight="bold", color=COL["gate"])
txt(ax, bm[0] + bm[2] - 1.6, 87.6, "drop flagged evidence", fs=6.2, ha="right", color=COL["sub"])
gm = pair_glyph(ax, bm[0] + 3.2, 83.2, ["cap"] * CAP, grid(), flags=FLAGS, drops=FLAGS, w=GW, fs=0)
txt(ax, gm["right"] + 2.6, 72.0, "flagged tokens\nleave the sum;\nno extra\nnetwork pass", fs=6.2, ha="left", color=COL["ink"], linespacing=1.15)
txt(ax, bm[0] + bm[2] / 2, 60.4, r"evidence summed over $j\in R$ only", fs=6.2, ha="center", color=COL["sub"])
txt(ax, bi[0] + 1.6, 52.6, "GATE-I", fs=7.6, weight="bold", color=COL["gatei"])
txt(ax, bi[0] + bi[2] - 1.6, 52.6, "re-mask and re-infill", fs=6.2, ha="right", color=COL["sub"])
gi = pair_glyph(ax, bi[0] + 3.2, 49.4, ["capmask"] * CAP, grid(corrupt=BLOCK - FLAGS, refill=FLAGS), flags=FLAGS, w=GW, fs=3.8)
txt(ax, gi["right"] + 2.6, 40.0, "fill in " + r"$G$" + ",\ncaption masked\n(no leakage);\n" + r"$R=\{1,\dots,m\}$", fs=6.2, ha="left", linespacing=1.15)
txt(ax, bi[0] + bi[2] / 2, 28.4, r"$\hat v_G\sim p_\theta(v_G\mid\tilde v_R,\varnothing^{T})$", fs=6.3, ha="center")
txt(ax, bi[0] + bi[2] / 2, 25.6, r"$S_r$ steps, $L$ draws, optional $\kappa$", fs=6.0, ha="center", color=COL["sub"])
busx3 = (PX[2][1] + PX[3][0]) / 2
YW = YG3 - 8.0
ax.plot([g3["right"] + 0.2, busx3], [YW, YW], color=COL["ink"], lw=0.8, zorder=4)
ax.plot([busx3, busx3], [YW, 74.0], color=COL["ink"], lw=0.8, zorder=4)
arrow(ax, (busx3, 74.0), (bm[0] - 0.2, 74.0), ms=5)
arrow(ax, (busx3, YW), (bi[0] - 0.2, YW), ms=5)
txt(ax, g3["right"] + 1.6, YW + 1.9, r"$G,\ R$", fs=6.2, ha="left")

# ---- 5: evidence and decision ------------------------------------------------------------------------------------------
x5, x5b = PX[4]
txt(ax, mid(4), 90.2, "ImageEvidence", fs=6.4, ha="center", color=COL["sub"], style="italic")
for lab, xx in [(r"$c^{+}$", x5 + 4.4), (r"$c^{-}$", x5 + 19.0)]:
    pair_glyph(ax, xx, 87.6, ["cap"] * 4, grid(corrupt=BLOCK, query={(r, c) for r in range(G8) for c in range(G8)} - BLOCK), w=10.0, fs=0)
    txt(ax, xx + 5.0, 71.0, lab, fs=7.2, ha="center")
txt(ax, mid(4), 66.6, "image fully masked, caption\n" + r"$c$ visible: $\Lambda^{c}_j[y]$", fs=6.0, ha="center", color=COL["sub"], linespacing=1.15)
txt(ax, mid(4), 61.4, r"$\Delta_j=\Lambda^{c^{+}}_j[\tilde v_j]-\Lambda^{c^{-}}_j[\tilde v_j]$", fs=6.1, ha="center")
txt(ax, x5 + 3.4, 57.0, r"$\bar\Delta_R=\frac{1}{|R|}$", fs=7.2, ha="left")
txt(ax, x5 + 16.6, 57.2, r"$\sum$", fs=9.0, ha="center")
txt(ax, x5 + 20.6, 57.0, r"$\Delta_j$", fs=7.2, ha="left")
bb = dict(boxstyle="round,pad=0.18", fc="white", ec=COL["flag"], lw=1.1)
ax.text(x5 + 16.6, 53.0, r"$j\in R$", fontsize=6.2, ha="center", va="center", bbox=bb, zorder=8, color=COL["flag"])
box(ax, x5 + 2.0, 43.2, x5b - x5 - 4.0, 6.6, fc="white", ec=COL["ink"], lw=1.2)
txt(ax, mid(4), 46.5, r"$Y_R=\mathbb{1}[\bar\Delta_R>0]$", fs=7.2, ha="center", weight="bold")
txt(ax, mid(4), 41.0, "ties, empty " + r"$R$" + ": wrong", fs=6.0, ha="center", color=COL["sub"])
txt(ax, mid(4), 38.0, r"$d_R=\bar\Delta_R/s_R$,", fs=6.0, ha="center", color=COL["sub"])
txt(ax, mid(4), 35.4, r"$z_R=\sqrt{|R|}\,d_R$ (secondary)", fs=6.0, ha="center", color=COL["sub"])
box(ax, x5 + 1.0, 22.2, x5b - x5 - 2.0, 10.6, fc="white", ec=COL["sub"], lw=0.7, ls=(0, (3, 1.6)))
txt(ax, mid(4), 31.0, r"optional two-way fusion", fs=6.0, ha="center", color=COL["sub"], weight="bold")
txt(ax, mid(4), 28.1, r"$F(c)=\hat\omega_T\,E_{T\leftarrow I}(c)$", fs=6.2, ha="center")
txt(ax, mid(4), 25.0, r"$+\,\hat\omega_I\,E_{I\leftarrow T}(c)$", fs=6.2, ha="center")
busx4 = (PX[3][1] + PX[4][0]) / 2
ax.plot([bm[0] + bm[2] + 0.2, busx4], [74.0, 74.0], color=COL["ink"], lw=0.8, zorder=4)
ax.plot([bi[0] + bi[2] + 0.2, busx4], [40.0, 40.0], color=COL["ink"], lw=0.8, zorder=4)
ax.plot([busx4, busx4], [40.0, 74.0], color=COL["ink"], lw=0.8, zorder=4)
arrow(ax, (busx4, 57.5), (x5 - 0.2, 57.5), ms=5)

# ---- bottom bands ---------------------------------------------------------------------------------------------------------
def band(xa, xb, y, label, color, ls="-"):
    ax.plot([xa, xa, xb, xb], [y + 1.4, y, y, y + 1.4], color=color, lw=1.1, linestyle=ls, solid_capstyle="butt")
    txt(ax, (xa + xb) / 2, y - 2.3, label, fs=6.6, ha="center", color=color, weight="bold")


band(PX[1][0], PX[2][1], 18.6, "gate: only passes with the caption masked (evidence-separation rule)", COL["flag"])
band(PX[4][0] + 0.2, PX[4][1] - 0.4, 18.6, "tested evidence", COL["ink"], ls=(0, (3, 1.6)))
S.legend_strip(ax, 0.8, 8.2, items=[
    ("cap", "caption token"), ("clean", "clean image token"), ("corrupt", r"corrupted ($Z_j=1$)"), ("mask", "masked"),
    ("query", "masked and scored"), ("refill", "re-infilled"), ("flag", r"flagged ($j\in G$)"), ("drop", "flagged, dropped")], fs=6.4, s=2.6, gap=2.4)

S.save(fig, "F2_pipeline")
print("ok")
