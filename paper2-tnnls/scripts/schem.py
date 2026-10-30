"""Drawing helpers for the method schematics (matplotlib patches in millimetre coordinates, same look as Fig. 1).
No data is read here. A `Canvas` wraps one axes whose data units are millimetres of the printed figure."""
from __future__ import annotations

import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

import figstyle as S
from figstyle import C

MM = 1 / 25.4
INK = C["ink"]


def hex_rgb(h: str):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])


def tint(h: str, t: float):
    """Mix colour h with white: t = 0 white, t = 1 the full colour."""
    t = float(np.clip(t, 0, 1))
    return tuple(1 - t * (1 - hex_rgb(h)))


class Canvas:
    def __init__(self, fig, rect_in, w_mm: float, h_mm: float):
        """rect_in: [left, bottom, width, height] in figure fraction; w_mm, h_mm: the axes size in millimetres."""
        self.ax = ax = fig.add_axes(rect_in)
        ax.set_xlim(0, w_mm)
        ax.set_ylim(0, h_mm)
        ax.set_aspect("equal")
        ax.axis("off")
        self.fig = fig

    def box(self, x, y, w, h, fc="white", ec=INK, lw=0.7, ls="-", r=1.0, z=2, hatch=None):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls,
                                         zorder=z, hatch=hatch))

    def arrow(self, x0, y0, x1, y1, lw=0.9, color=INK, ls="-", style="-|>", conn=None, z=5):
        kw = dict(arrowstyle=style, mutation_scale=6, lw=lw, color=color, shrinkA=0, shrinkB=0, zorder=z, linestyle=ls)
        if conn:
            kw["connectionstyle"] = conn
        self.ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), **kw))

    def text(self, x, y, s, ha="center", va="center", fs=S.FS, color=INK, **kw):
        return self.ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, zorder=6, **kw)

    def grid(self, x, y, colours, cs, ec="#8A8A8A", lw=0.35, hatches=None, z=3):
        n_r, n_c = len(colours), len(colours[0])
        for r in range(n_r):
            for c in range(n_c):
                h = None if hatches is None else hatches[r][c]
                self.ax.add_patch(Rectangle((x + c * cs, y + (n_r - 1 - r) * cs), cs, cs, fc=colours[r][c], ec=ec, lw=lw, zorder=z,
                                            hatch=h))

    def tag(self, x, y, s):
        """Panel letter at (x, y) in mm (top-left anchor)."""
        self.text(x, y, s, ha="left", va="top", fs=S.FS + 1, fontweight="bold")
