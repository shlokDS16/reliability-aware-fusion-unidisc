"""Shared visual identity for the Paper 2 (GATE) figures.

One palette, one token glyph, one legend strip, one font setup, for every figure. Nothing here depends on run data.

Colour roles (Okabe-Ito, colour-blind safe; each colour has exactly one meaning in the paper):
    caption token ........ orange   #E69F00
    clean image token .... light grey fill
    corrupted token ...... vermillion fill #D55E00   (label Z_j = 1, evaluation only)
    flagged token ........ blue outline #0072B2, thick  (j in G)
    re-infilled token .... bluish-green fill #009E73
    masked token ......... black fill, white M
    queried (target) ..... white fill, thick dark outline (masked in the input; its observed value is scored)
Method colours: GATE-M / the gate statistic q = blue; GATE-I = bluish-green; TbV = sky blue #56B4E9;
cheap rivals = reddish purple #CC79A7 (hollow); controls = grey; oracle = dashed black.
Symbols follow paper2/sections/method.tex (Table 1) exactly; SYM below is the only place they are spelled, so a notation
pass in the manuscript needs one edit here.
"""
from __future__ import annotations

import pathlib

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent  # paper2/figures
REPO = HERE.parents[2]

MM = 1 / 25.4
W1, W2 = 90.0, 190.0  # Elsevier single and double column widths (mm)

COL = dict(
    cap="#E69F00", clean="#E3E3E3", clean_edge="#8A8A8A", corrupt="#D55E00", flag="#0072B2", refill="#009E73",
    mask="#111111", ink="#1B1B1B", sub="#555555", faint="#BDBDBD", box="#F4F4F4", tbv="#56B4E9", rival="#CC79A7",
    ctrl="#7F7F7F", gate="#0072B2", gatei="#009E73",
)

# Symbols as typeset in method.tex (mathtext strings).
SYM = dict(
    pair=r"$\tilde x=(\tilde t,\tilde v)$", pair_clean=r"$x=(t,v)$", mask=r"$\mathsf{M}$",
    null_T=r"$\varnothing^{T}$", null_I=r"$\varnothing^{I}$",
    A=r"$A_j$", B=r"$B_j$", C=r"$C_j$", D=r"$D_j$", q=r"$q_j$", u=r"$u_j$",
    tau=r"$\hat\tau$", alpha=r"$\alpha$", G=r"$G$", R=r"$R$",
    cplus=r"$c^{+}$", cminus=r"$c^{-}$", Delta=r"$\Delta_j$", Dbar=r"$\bar\Delta_R$", YR=r"$Y_R$",
)


def apply() -> None:
    """Global matplotlib setup: sans-serif text, TrueType (Type 42) fonts embedded in PDF, sizes for final print width."""
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
        "mathtext.fontset": "stixsans",
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "legend.fontsize": 7, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "lines.linewidth": 1.0, "axes.spines.top": False,
        "axes.spines.right": False, "savefig.dpi": 300, "figure.dpi": 150, "text.color": COL["ink"],
        "axes.edgecolor": COL["ink"], "axes.labelcolor": COL["ink"], "xtick.color": COL["ink"], "ytick.color": COL["ink"],
        "pdf.compression": 6,
    })


def canvas(w_mm: float, h_mm: float, y0: float = 0.0):
    """A figure of exact size w_mm x h_mm whose single axes uses millimetres as data units (origin bottom-left)."""
    fig = plt.figure(figsize=(w_mm * MM, (h_mm - y0) * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_mm)
    ax.set_ylim(y0, h_mm)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, name: str) -> None:
    """Vector PDF plus a 300 dpi PNG preview in paper2/figures/."""
    fig.savefig(OUT / f"{name}.pdf", format="pdf")
    fig.savefig(OUT / f"{name}.png", format="png", dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------------------------------------------------------------
# Token glyph (the home-base glyph of the paper): a caption strip over an image grid, one cell per token.
# ---------------------------------------------------------------------------------------------------------------------
def cell(ax, x, y, s, kind="clean", text=None, flag=False, drop=False, fs=None, lw=0.5):
    """One token cell with lower-left corner (x, y) and side s (mm). kind: cap, capmask, clean, corrupt, mask, query, refill."""
    fill, edge, ew, txt, tc = COL["clean"], COL["clean_edge"], lw, text, COL["ink"]
    if kind == "cap":
        fill, edge = COL["cap"], "#9A6A00"
    elif kind == "corrupt":
        fill, edge = COL["corrupt"], "#7A3300"
    elif kind in ("mask", "capmask"):
        fill, edge, txt, tc = COL["mask"], COL["mask"], (text if text is not None else "M"), "white"
    elif kind == "query":
        fill, edge, ew = "white", COL["ink"], lw * 2.2
    elif kind == "refill":
        fill, edge = COL["refill"], "#005C43"
    if drop:
        fill = "white"
    ax.add_patch(Rectangle((x, y), s, s, facecolor=fill, edgecolor=edge, linewidth=ew, zorder=2, joinstyle="miter"))
    if drop:
        ax.plot([x + 0.15 * s, x + 0.85 * s], [y + 0.15 * s, y + 0.85 * s], color=COL["flag"], lw=0.5, zorder=3)
        ax.plot([x + 0.15 * s, x + 0.85 * s], [y + 0.85 * s, y + 0.15 * s], color=COL["flag"], lw=0.5, zorder=3)
    if flag:
        ax.add_patch(Rectangle((x - 0.05 * s, y - 0.05 * s), 1.10 * s, 1.10 * s, facecolor="none", edgecolor=COL["flag"],
                               linewidth=1.3, zorder=4, linestyle=(0, (2.2, 1.0)) if drop else "-"))
    if txt:
        ax.text(x + s / 2, y + s / 2 - 0.02 * s, txt, ha="center", va="center", fontsize=fs or max(4.2, 2.1 * s), color=tc,
                zorder=5, fontweight="bold" if kind in ("mask", "capmask") else "normal")


def pair_glyph(ax, x, ytop, cap, img, flags=None, drops=None, w=15.2, labels=None, fs=None):
    """Caption strip over image grid, total width w (mm). cap: list of kinds; img: 2-D list of kinds; flags/drops: sets of
    (row, col) in the grid. Returns dict of anchor points: strip box, grid box."""
    n, g = len(cap), len(img)
    cs_cap, cs_img = w / n, w / g
    hcap = cs_cap
    y_cap = ytop - hcap
    for i, k in enumerate(cap):
        cell(ax, x + i * cs_cap, y_cap, cs_cap, k, fs=fs)
    gap = 1.2
    y_grid_top = y_cap - gap
    flags = flags or set()
    drops = drops or set()
    for r in range(g):
        for c in range(g):
            kind = img[r][c]
            cell(ax, x + c * cs_img, y_grid_top - (r + 1) * cs_img, cs_img, kind, flag=(r, c) in flags, drop=(r, c) in drops, fs=fs)
    return dict(strip=(x, y_cap, w, hcap), grid=(x, y_grid_top - g * cs_img, w, g * cs_img), cs_img=cs_img, cs_cap=cs_cap,
                bottom=y_grid_top - g * cs_img, right=x + w, left=x, top=ytop)


def grid_of(g, kind="clean"):
    return [[kind] * g for _ in range(g)]


def legend_strip(ax, x, y, items=None, fs=6.8, s=2.8, gap=3.4):
    """The same legend strip in every figure that shows token cells. Returns the right end (mm)."""
    items = items or [
        ("cap", "caption token"), ("clean", "clean image token"), ("corrupt", r"corrupted token ($Z_j=1$)"),
        ("mask", "masked"), ("query", "scored (target)"), ("refill", "re-infilled"), ("flag", "flagged ($j\\in G$)"),
    ]
    cx = x
    for kind, label in items:
        if kind == "flag":
            cell(ax, cx, y, s, "clean", flag=True)
        elif kind == "drop":
            cell(ax, cx, y, s, "clean", flag=True, drop=True)
        else:
            cell(ax, cx, y, s, kind)
        t = ax.text(cx + s + 1.1, y + s / 2, label, ha="left", va="center", fontsize=fs, color=COL["ink"])
        fig = ax.figure
        bb = t.get_window_extent(fig.canvas.get_renderer())
        inv = ax.transData.inverted()
        x1 = inv.transform((bb.x1, bb.y0))[0]
        cx = x1 + gap
    return cx


def box(ax, x, y, w, h, fc=None, ec=None, lw=0.7, r=1.2, ls="-", z=1):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", facecolor=fc or COL["box"], edgecolor=ec or COL["faint"],
                       linewidth=lw, linestyle=ls, zorder=z)
    ax.add_patch(p)
    return p


def arrow(ax, p0, p1, color=None, lw=0.9, ls="-", ms=6, rad=0.0, z=6, style="-|>"):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, linewidth=lw, color=color or COL["ink"], linestyle=ls,
                        connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0, zorder=z)
    ax.add_patch(a)
    return a


def txt(ax, x, y, s, fs=7, ha="left", va="center", color=None, weight="normal", style="normal", **kw):
    return ax.text(x, y, s, fontsize=fs, ha=ha, va=va, color=color or COL["ink"], fontweight=weight, fontstyle=style, zorder=7, **kw)
