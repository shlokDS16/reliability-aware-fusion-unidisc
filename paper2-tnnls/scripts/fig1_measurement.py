"""Fig. 1 (two-column): schematic of the SHARED measurement only (SPEC v2.2 section 4 item 1): image and caption to tokens, the per-token evidence map,
the unweighted sum, the decision, and corruption as input damage. No weight rule, no study labels, no 0-to-learned axis, no result number.
Conceptual drawing in matplotlib patches; the token pattern is a fixed pseudo-random schematic (seed 3), not data.
Notation: Delta_j (per-token evidence), S = sum_j Delta_j (Section III notation of the paper); decision 1[S > 0].
Output: paper2-tnnls/figures/fig1_measurement.pdf (+ png preview). CPU only."""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

import figstyle as S
from figstyle import C

S.apply()
MM = 1 / 25.4
W, H = S.COL2 / MM, 51.5                       # mm
fig = plt.figure(figsize=(W * MM, H * MM))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")

CAP, IMG, DMG = "#F0E442", "#DADADA", C["purple"]
POS, NEG = C["blue"], C["orange"]
INK = C["ink"]
FS = S.FS


def box(x, y, w, h, fc="white", ec=INK, lw=0.7, ls="-", r=1.0, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def arrow(x0, y0, x1, y1, lw=0.9):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=6, lw=lw, color=INK, shrinkA=0, shrinkB=0, zorder=5))


def text(x, y, s, ha="center", va="center", fs=FS, **kw):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=INK, zorder=6, **kw)


def grid(x, y, n, cs, colours, ec="#8A8A8A", lw=0.4):
    for r in range(n):
        for c in range(n):
            ax.add_patch(Rectangle((x + c * cs, y + (n - 1 - r) * cs), cs, cs, fc=colours[r][c], ec=ec, lw=lw, zorder=3))


def strip(x, y, n, cs, fc=CAP, ec="#8C8300", hatch=None):
    for i in range(n):
        ax.add_patch(Rectangle((x + i * cs, y), cs, cs * 0.9, fc=fc, ec=ec, lw=0.4, zorder=3, hatch=hatch))


rng = np.random.default_rng(3)
N, CS = 6, 2.5
YC = 26.0                                                    # vertical centre of the main row (mm)

# ---- 1. image -> input damage -> damaged image --------------------------------------------------------------------------------------
box(1.5, YC - 7.5, 15, 15, fc="#EDEDED")
for k in range(5):                                           # a few strokes: "a picture"
    ax.plot([3 + 2.2 * k, 5 + 2.2 * k], [YC - 5 + 1.6 * k, YC - 2 + 1.1 * k], color="#9B9B9B", lw=0.8, zorder=3)
text(9, YC - 11.2, "image")
arrow(17.5, YC, 32.0, YC)
text(24.8, YC + 3.6, "input damage", fs=FS)
text(24.8, YC - 3.6, "noise, JPEG,\nsplice", fs=FS, linespacing=0.95)
box(33, YC - 7.5, 15, 15, fc="#EDEDED")
rr = np.random.default_rng(11)
xs, ys = rr.uniform(34, 47, 70), rr.uniform(YC - 6.8, YC + 6.8, 70)
ax.scatter(xs, ys, s=0.9, color="#6F6F6F", lw=0, zorder=3)
text(40.5, YC - 11.2, "damaged image")

# ---- 2. tokenise -> tokens ----------------------------------------------------------------------------------------------------------------
arrow(49.5, YC, 60.0, YC)
text(54.8, YC + 3.2, "tokenise", fs=FS)
dm = rng.random((N, N)) < 0.28
cols = [[DMG if dm[r, c] else IMG for c in range(N)] for r in range(N)]
gx, gy = 61.0, YC - N * CS / 2 + 1.5
grid(gx, gy, N, CS, cols)
text(gx + N * CS / 2, gy - 4.2, "image tokens", fs=FS)
strip(gx, YC + 14.2, 6, CS)
strip(gx, YC + 10.8, 6, CS, hatch="////")
text(gx + N * CS / 2, YC + 21.0, "true and wrong captions\n(caption tokens)", fs=FS, linespacing=0.95, va="center")

# ---- 3. masked diffusion model ---------------------------------------------------------------------------------------------------------
arrow(gx + N * CS + 1.0, YC, 86.0, YC)
box(87, YC - 10, 29, 20, fc="#F6F6F6")
text(101.5, YC + 3.4, "masked diffusion model", fs=FS)
text(101.5, YC - 2.2, "image tokens masked,\ncaption visible", fs=FS, linespacing=0.95)

# ---- 4. per-token evidence map -------------------------------------------------------------------------------------------------------------
arrow(117, YC, 125.0, YC)
d = rng.normal(0.35, 0.55, (N, N))
d[dm] += 0.0


def evid_col(v):
    t = float(np.clip(abs(v) / 1.4, 0, 1))
    base = np.array(matplotlib_hex(POS if v >= 0 else NEG))
    return tuple(1 - t * (1 - base))


def matplotlib_hex(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


ex, ey = 126.0, YC - N * CS / 2 + 1.5
grid(ex, ey, N, CS, [[evid_col(d[r, c]) for c in range(N)] for r in range(N)])
text(ex + N * CS / 2, ey - 4.2, "per-token evidence", fs=FS)
text(ex + N * CS / 2, ey + N * CS + 3.2, r"$\Delta_j$", fs=FS + 1)

# ---- 5. unweighted sum -> decision ------------------------------------------------------------------------------------------------------
arrow(ex + N * CS + 1.0, YC, 147.0, YC)
box(148, YC - 7, 15.5, 14, fc="white")
text(155.75, YC + 2.2, "sum", fs=FS)
text(155.75, YC - 2.6, r"$S=\sum_j\Delta_j$", fs=FS)
arrow(164.5, YC, 168.5, YC)
box(169.5, YC - 7, 11.5, 14, fc="white", lw=1.0)
text(175.25, YC + 2.4, "decision", fs=FS)
text(175.25, YC - 2.6, r"$S>0$", fs=FS)

text(181.0, YC - 15.0, "the true caption is chosen if $S>0$", ha="right", fs=FS)

# ---- legend strip ------------------------------------------------------------------------------------------------------------------------
LY = 4.3
items = [(CAP, "caption token", None), (IMG, "image token", None), (DMG, "token changed by the damage", None), (POS, r"evidence $\Delta_j>0$", None),
         (NEG, r"evidence $\Delta_j<0$", None)]
cx = 3.0
for fc, lab, _ in items:
    ax.add_patch(Rectangle((cx, LY - 1.4), 2.8, 2.8, fc=fc, ec="#6A6A6A", lw=0.4, zorder=3))
    t = ax.text(cx + 3.8, LY, lab, ha="left", va="center", fontsize=FS, color=INK, zorder=6)
    bb = t.get_window_extent(fig.canvas.get_renderer())
    cx = ax.transData.inverted().transform((bb.x1, bb.y0))[0] + 4.5
S.save(fig, "fig1_measurement")
print("legend ends at", round(cx, 1), "of", round(W, 1))
