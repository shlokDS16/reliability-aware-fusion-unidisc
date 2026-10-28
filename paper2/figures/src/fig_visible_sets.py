"""F3: the five visible sets (one primitive, five masking patterns). Conceptual; no data. Reads nothing from runs/.

Definitions: paper2/sections/method.tex (Eq. levels, Eq. pmi, Algorithm MaskedScore, Algorithm ReInfill) and
research/paper2/benchmark/PANEL-P2-PLAN.md section 2.1 (every quantity is the log-probability of an observed token under a
visible set). Scored modality a = image (I), other modality b = caption (T).
Output: paper2/figures/F3_visible_sets.pdf + .png (190 mm, double column)."""
from __future__ import annotations

import style as S
from style import COL, cell, pair_glyph, txt

S.apply()
W, H = S.W2, 96.0
fig, ax = S.canvas(W, H)

G = 6          # schematic grid (the real grid is 32 x 32)
NCAP = 5
GW = 21.0      # glyph width (mm)
COLW, GAP = 36.0, 2.5

SK = {(r, c) for r in range(G) for c in range(G) if (2 * r + 3 * c) % 4 == 0}   # one complementary group S_k (schematic)
TARGET = (2, 2) if (2, 2) in SK else sorted(SK)[len(SK) // 2]
GSET = {(1, 4), (2, 4), (2, 3), (4, 1)}                                           # a flagged set G (schematic)


def img(kind_default="clean", query=None):
    g = S.grid_of(G, kind_default)
    for (r, c) in (query or set()):
        g[r][c] = "query"
    return g


cols = [
    # key, title, subtitle, caption kind, image grid, flags, formula, role
    dict(key="B", title=r"$B_j$", sub="rest of the image visible,\ncaption masked", cap="capmask", grid=img(query=SK),
         formula=r"$\log p_\theta(x_j\mid x^{I}_{-S_{k(j)}},\,\varnothing^{T})$", role=r"gate: $u_j=-(B_j-D_j)$"),
    dict(key="D", title=r"$D_j$", sub="everything masked:\nthe position marginal", cap="capmask",
         grid=img(query={(r, c) for r in range(G) for c in range(G)}),
         formula=r"$\log p_\theta(x_j\mid\varnothing^{I},\,\varnothing^{T})$", role="null, cached once per layout"),
    dict(key="C", title=r"$C_j$", sub="image fully masked,\ncaption visible", cap="cap",
         grid=img(query={(r, c) for r in range(G) for c in range(G)}),
         formula=r"$\log p_\theta(x_j\mid\varnothing^{I},\,x^{T})$", role=r"decision: $\Lambda^{c}_j[y]$, $C_j-D_j$"),
    dict(key="A", title=r"$A_j$", sub="rest of the image visible,\ncaption visible", cap="cap", grid=img(query=SK),
         formula=r"$\log p_\theta(x_j\mid x^{I}_{-S_{k(j)}},\,x^{T})$", role=r"control: $A_j-B_j$"),
    dict(key="E", title="re-infill", sub="reliable tokens visible,\ncaption masked", cap="capmask", grid=img(query=GSET),
         formula=r"$\hat v_G\sim p_\theta(v_G\mid \tilde v_R,\,\varnothing^{T})$", role="repair: GATE-I fills in $G$"),
]

x0s = [i * (COLW + GAP) for i in range(5)]
for i, c in enumerate(cols):
    x0 = x0s[i]
    S.box(ax, x0 + 0.4, 38.5, COLW - 0.8, 56.0, fc="white", ec=COL["faint"], lw=0.6)
    txt(ax, x0 + COLW / 2, 90.2, c["title"], fs=10 if c["key"] != "E" else 8.5, ha="center", weight="bold")
    txt(ax, x0 + COLW / 2, 84.4, c["sub"], fs=6.8, ha="center", color=COL["sub"], linespacing=1.15)
    gx = x0 + (COLW - GW) / 2
    cap = [c["cap"]] * NCAP
    flags = GSET if c["key"] == "E" else None
    info = pair_glyph(ax, gx, 78.0, cap, c["grid"], flags=flags, w=GW, fs=0)
    # mark the scored position j in the first scored cell of the glyph
    cs = info["cs_img"]
    gy_top = info["grid"][1] + info["grid"][3]
    if c["key"] in ("B", "A"):
        r, cc = TARGET
    elif c["key"] == "E":
        r, cc = sorted(GSET)[1]
    else:
        r, cc = 2, 2
    txt(ax, gx + (cc + 0.5) * cs, gy_top - (r + 0.5) * cs, "j", fs=6.5, ha="center", style="italic", weight="bold")
    txt(ax, gx - 0.4, info["strip"][1] + info["strip"][3] / 2, r"$t$", fs=6.5, ha="right", color=COL["sub"])
    txt(ax, gx - 0.4, info["grid"][1] + info["grid"][3] / 2, r"$v$", fs=6.5, ha="right", color=COL["sub"])
    txt(ax, x0 + COLW / 2, 47.0, c["formula"], fs=7.4, ha="center")
    txt(ax, x0 + COLW / 2, 41.6, c["role"], fs=6.6, ha="center", color=COL["ink"])

# brackets: which levels the gate may use, which the tested evidence uses (evidence-separation rule)
def bracket(xa, xb, y, label, color, ls="-"):
    ax.plot([xa, xa, xb, xb], [y + 1.6, y, y, y + 1.6], color=color, lw=1.1, linestyle=ls, solid_capstyle="butt", zorder=5)
    txt(ax, (xa + xb) / 2, y - 2.4, label, fs=6.8, ha="center", color=color, weight="bold")


bracket(x0s[0] + 1.5, x0s[1] + COLW - 1.5, 33.2, "gate may use these: caption masked", COL["flag"])
bracket(x0s[1] + 1.5, x0s[2] + COLW - 1.5, 25.0, "tested evidence uses these: image fully masked", COL["ink"], ls=(0, (3, 1.6)))
txt(ax, x0s[3] + COLW / 2, 32.0, "kept out of the gate:\nthe caption it would judge\nis visible", fs=6.6, ha="center", color=COL["sub"], linespacing=1.2)
txt(ax, x0s[4] + COLW / 2, 32.0, "outside the gate and the\nevidence: it only repairs\nthe set the gate returns", fs=6.6, ha="center", color=COL["sub"], linespacing=1.2)

# PMI identity (Eq. pmi)
txt(ax, W / 2, 15.2, r"$A_j-D_j\;=\;(B_j-D_j)\,+\,(A_j-B_j)\;=\;(A_j-C_j)\,+\,(C_j-D_j)$", fs=8.2, ha="center")
txt(ax, x0s[0] + 24, 10.2, r"$q_j$: intra-modal, never sees the caption", fs=6.6, ha="center", color=COL["flag"])
txt(ax, x0s[3] + 18, 10.2, r"$C_j-D_j$: cross-modal, the decision evidence", fs=6.6, ha="center", color=COL["ink"])

S.legend_strip(ax, 0.8, 1.2, items=[
    ("cap", "caption token"), ("clean", "image token"), ("mask", "masked"), ("query", "masked and scored"), ("flag", "flagged ($j\\in G$)")])

S.save(fig, "F3_visible_sets")
print("ok")
