"""Helpers shared by the result figures F6-F10 (read-only on runs/; no number typed by hand)."""
from __future__ import annotations

import json
import math

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import style as S
from style import COL, MM

MINUS = "−"
RUNS = S.REPO / "runs"


def jload(rel: str):
    return json.load(open(RUNS / rel, encoding="utf-8"))


def fmt(x: float, nd: int = 3, plus: bool = False) -> str:
    s = f"{x:+.{nd}f}" if plus else f"{x:.{nd}f}"
    return s.replace("-", MINUS)


def wilson(k: float, n: int, z: float = 1.959964):
    """Wilson 95% interval of a proportion k/n (derived from accuracy x n; the arms are paired, see the paired panel)."""
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def hatch_row(ax, y, x0, x1, text, h=0.9):
    ax.add_patch(Rectangle((x0, y - h / 2), x1 - x0, h, facecolor="none", edgecolor=COL["faint"], hatch="////", lw=0.4, zorder=1))
    ax.text((x0 + x1) / 2, y, text, ha="center", va="center", fontsize=6.2, color=COL["sub"], zorder=3,
            bbox=dict(fc="white", ec="none", pad=0.8))


def effect_figure(rows, names, name_out, n_label_fn):
    """Paired-effect figure used by F6 (family P) and F7 (family PS) with the same encoding.
    rows: list of dicts from analysis.json (keys acc_a [GATE-M], acc_b [none], n, b, c, delta, ci90, ci95, p_holm, tested).
    (a) matching accuracy of none and GATE-M with Wilson 95% intervals; (b) GATE-M minus none, thick 90% and thin 95% bootstrap intervals,
    solid line at 0, dashed lines at +-0.05 (SAP A4.2.5 item 1); (c) discordant counts b, c, n_d and the Holm-adjusted p."""
    S.apply()
    nrow = len(rows)
    W = S.W2
    pitch = 13.0
    AXH = pitch * nrow
    BOT, TOP = 13.5, 14.0
    H = BOT + AXH + TOP
    fig = plt.figure(figsize=(W * MM, H * MM))
    ax1_x, ax1_w = 25.0, 58.0
    ax2_x, ax2_w = 100.0, 56.0
    txt_x = 160.5

    def mk(x0, w):
        ax = fig.add_axes([x0 / W, BOT / H, w / W, AXH / H])
        ax.set_ylim(nrow - 0.5, -0.5)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        return ax

    a1, a2 = mk(ax1_x, ax1_w), mk(ax2_x, ax2_w)
    a1.set_xlim(0.55, 1.0)
    a1.set_xticks([0.6, 0.7, 0.8, 0.9, 1.0])
    a1.set_xticklabels(["0.6", "0.7", "0.8", "0.9", "1.0"])
    a1.set_xlabel("matching accuracy (Y), 95% Wilson interval per arm", fontsize=7)
    a2.set_xlim(-0.06, 0.06)
    a2.set_xticks([-0.05, 0, 0.05])
    a2.set_xticklabels([MINUS + "0.05", "0", "+0.05"])
    a2.set_xlabel("GATE-M minus none (paired accuracy difference)", fontsize=7)
    a2.axvline(0, color=COL["ink"], lw=0.8, zorder=1)
    for v in (-0.05, 0.05):
        a2.axvline(v, color=COL["ctrl"], lw=0.7, ls=(0, (3, 2)), zorder=1)
    for i, (r, nm) in enumerate(zip(rows, names)):
        yc = BOT + AXH - (i + 0.5) * pitch
        for a in (a1, a2):
            if i % 2 == 0:
                a.axhspan(i - 0.5, i + 0.5, color="#F6F6F6", zorder=0, lw=0)
        fig.text((ax1_x - 2.0) / W, (yc + 1.2) / H, nm, fontsize=7.5, weight="bold", ha="right", va="center")
        fig.text((ax1_x - 2.0) / W, (yc - 2.6) / H, n_label_fn(r), fontsize=6.2, color=COL["sub"], ha="right", va="center")
        if not r.get("tested", True):
            hatch_row(a1, i, 0.55, 1.0, "not tested")
            hatch_row(a2, i, -0.06, 0.06, "not tested")
            continue
        n = r["n"]
        for acc, off, col, mkr, mfc in ((r["acc_b"], -0.17, COL["ctrl"], "s", "white"), (r["acc_a"], 0.17, COL["gate"], "o", COL["gate"])):
            lo, hi = wilson(round(acc * n), n)
            y = i + off
            a1.plot([lo, hi], [y, y], color=col, lw=1.1, solid_capstyle="butt", zorder=3)
            a1.plot([acc], [y], marker=mkr, ms=4.0, mfc=mfc, mec=col, mew=0.9, ls="none", zorder=4)
            a1.text(min(hi + 0.008, 0.985), y, f"{acc:.3f}", fontsize=6.2, va="center", ha="left", color=COL["ink"])
        d = r["delta"]
        a2.plot(r["ci95"], [i, i], color=COL["gate"], lw=1.0, solid_capstyle="butt", zorder=3)
        a2.plot(r["ci90"], [i, i], color=COL["gate"], lw=3.0, solid_capstyle="butt", zorder=3)
        a2.plot([d], [i], marker="o", ms=3.3, mfc="white", mec=COL["ink"], mew=0.8, ls="none", zorder=5)
        fig.text(txt_x / W, (yc + 2.6) / H, f"$b={r['b']}$, $c={r['c']}$", fontsize=7, va="center")
        fig.text(txt_x / W, (yc - 0.9) / H, f"$n_d={r['n_d']}$", fontsize=6.2, color=COL["sub"], va="center")
        fig.text(txt_x / W, (yc - 4.2) / H, f"Holm $p={r['p_holm']:.2f}$", fontsize=6.2, color=COL["sub"], va="center")
    yh = (BOT + AXH + 8.6) / H
    fig.text(ax1_x / W, yh, "(a) accuracy", fontsize=8, weight="bold", va="center")
    fig.text(ax2_x / W, yh, "(b) paired difference", fontsize=8, weight="bold", va="center")
    fig.text(txt_x / W, yh, "(c) discordance", fontsize=8, weight="bold", va="center")
    ly = (BOT + AXH + 3.4) / H
    for xx, mkr, mfc, col, lab in ((ax1_x, "s", "white", COL["ctrl"], "none"), (ax1_x + 14, "o", COL["gate"], COL["gate"], "GATE-M")):
        fig.add_artist(plt.Line2D([xx / W], [ly], marker=mkr, ms=4, mfc=mfc, mec=col, mew=0.9, ls="none", transform=fig.transFigure))
        fig.text((xx + 2.2) / W, ly, lab, fontsize=6.6, va="center")
    xx = ax2_x
    fig.add_artist(plt.Line2D([xx / W, (xx + 7) / W], [ly, ly], color=COL["gate"], lw=3.0, solid_capstyle="butt", transform=fig.transFigure))
    fig.text((xx + 8.2) / W, ly, "90% bootstrap", fontsize=6.6, va="center")
    fig.add_artist(plt.Line2D([(xx + 28) / W, (xx + 35) / W], [ly, ly], color=COL["gate"], lw=1.0, transform=fig.transFigure))
    fig.text((xx + 36.2) / W, ly, "95% bootstrap", fontsize=6.6, va="center")
    fig.text(txt_x / W, ly, "$b$: GATE-M right, none wrong", fontsize=6.0, color=COL["sub"], va="center")
    fig.text(txt_x / W, (BOT + AXH + 0.6) / H, "$c$: the reverse", fontsize=6.0, color=COL["sub"], va="center")
    S.save(fig, name_out)
    return fig
