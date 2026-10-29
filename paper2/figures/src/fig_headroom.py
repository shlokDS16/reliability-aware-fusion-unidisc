"""F10 / F10s: decision headroom, POST HOC and DESCRIPTIVE (not an account of the P result, AB.1).
Per cell: (i) number of items whose none-arm decision under the corruption differs from the clean-image decision
    = per_condition.<cell>.share_items_corruption_flips_clean_decision x n   (runs/P2-A23-AUDIT/a23_ps_audit.json);
(ii) number of items on which GATE-M and none disagree = n_d (runs/P2-GATE-M4/analysis.json primary.per_corruption / ps.per_corruption);
(iii) the discordance the exact two-sided McNemar test needs even if c = 0: min_b_with_c0 (a23_ps_audit.json; keys '0.025' and '0.05').
F10 = P cells, F10s = PS cells (separate canvases, as F6/F7)."""
from __future__ import annotations

import json

import matplotlib.pyplot as plt

import resultlib as R
import style as S
from style import COL, MM

aud = R.jload("P2-A23-AUDIT/a23_ps_audit.json")
ana = R.jload("P2-GATE-M4/analysis.json")
pcond = aud["per_condition"]
need = aud["per_condition"]["min_b_with_c0"]
need_a, need_b = need["0.025"], need["0.05"]
P = [("jpeg10", "JPEG", ana["primary"]["per_corruption"]["jpeg"]), ("noise0.1", "noise", ana["primary"]["per_corruption"]["noise"]),
     ("splice128", "splice", ana["primary"]["per_corruption"]["splice"])]
PS = [("patch", "patch", ana["ps"]["per_corruption"]["patch"]), ("swap", "swap", ana["ps"]["per_corruption"]["swap"])]


def draw(cells, out):
    S.apply()
    nrow = len(cells)
    W = S.W2
    pitch = 11.0
    AXH = pitch * nrow
    BOT, TOP = 14.0, 17.0
    H = BOT + AXH + TOP
    LEFT, AXW = 24.0, 118.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    ax = fig.add_axes([LEFT / W, BOT / H, AXW / W, AXH / H])
    ax.set_xscale("symlog", linthresh=10, linscale=0.6)
    ax.set_xlim(-0.8, 200)
    ax.set_ylim(nrow - 0.5, -0.5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ticks = [0, 2, 4, 6, 8, 10, 20, 50, 100, 200]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])
    ax.minorticks_off()
    ax.set_xlabel("items (of 500); axis linear to 10, logarithmic above", fontsize=7)
    ax.axvline(need_a, color=COL["ctrl"], lw=0.8, ls=(0, (3, 2)), zorder=1)
    ax.axvline(need_b, color=COL["ctrl"], lw=0.8, ls=":", zorder=1)
    for i, (key, nm, row) in enumerate(cells):
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color="#F6F6F6", zorder=0, lw=0)
        n = pcond[key]["n"]
        flips = round(pcond[key]["share_items_corruption_flips_clean_decision"] * n)
        nd = row["n_d"]
        fig.text((LEFT - 2.0) / W, (BOT + AXH - (i + 0.5) * pitch) / H, nm, fontsize=7.5, weight="bold", ha="right", va="center")
        ax.plot([flips], [i - 0.15], marker="o", ms=5.0, mfc=COL["ctrl"], mec=COL["ctrl"], ls="none", zorder=4)
        ax.text(flips * 1.22 if flips >= 10 else flips + 1.3, i - 0.15, f"{flips}", fontsize=6.6, va="center", ha="left")
        ax.plot([nd], [i + 0.22], marker="o", ms=5.0, mfc=COL["gate"], mec=COL["gate"], ls="none", zorder=4)
        ax.text(nd + 0.9, i + 0.22, f"{nd}", fontsize=6.6, va="center", ha="left", color=COL["gate"])
    yh = (BOT + AXH + 10.0) / H
    fig.text(LEFT / W, yh, "per-cell decision counts (post hoc, descriptive)", fontsize=8, weight="bold", va="center")
    ly = (BOT + AXH + 4.6) / H
    items = [("o", COL["ctrl"], "none-arm decision differs from the clean image", 0.0),
             ("o", COL["gate"], "GATE-M and none disagree ($n_d$)", 70.0)]
    for mk, col, lab, dx in items:
        fig.add_artist(plt.Line2D([(LEFT + dx) / W], [ly], marker=mk, ms=4.5, mfc=col, mec=col, ls="none", transform=fig.transFigure))
        fig.text((LEFT + dx + 2.2) / W, ly, lab, fontsize=6.6, va="center")
    # right-hand key for the two reference lines
    kx = LEFT + AXW + 5.0
    fig.text(kx / W, (BOT + AXH - 2.0) / H, "needed with $c=0$,", fontsize=6.4, va="center", color=COL["sub"])
    fig.text(kx / W, (BOT + AXH - 5.0) / H, "exact two-sided McNemar:", fontsize=6.4, va="center", color=COL["sub"])
    for yy, ls, lv, lab in ((BOT + AXH - 9.0, (0, (3, 2)), need_a, f"$b\\geq{need_a}$ at level 0.025"), (BOT + AXH - 12.4, ":", need_b, f"$b\\geq{need_b}$ at level 0.05")):
        fig.add_artist(plt.Line2D([kx / W, (kx + 6) / W], [yy / H, yy / H], color=COL["ctrl"], lw=0.8, ls=ls, transform=fig.transFigure))
        fig.text((kx + 7.5) / W, yy / H, lab, fontsize=6.4, va="center")
    S.save(fig, out)
    return {k: dict(flips=round(pcond[k]["share_items_corruption_flips_clean_decision"] * pcond[k]["n"]), n_d=r["n_d"], n=pcond[k]["n"]) for k, _, r in cells}


r1 = draw(P, "F10_decision_headroom")
r2 = draw(PS, "F10s_decision_headroom_ps")
print(json.dumps(r1), json.dumps(r2), need_a, need_b)
