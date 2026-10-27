"""Figures F1 and F2 for Probe 1 (P2-PROBE-01). CPU only; reads runs/P2-PROBE-01/{summary.json,items.jsonl}.

    python analysis/paper2/fig_probe1.py

Writes figures/paper2/F1_probe1_accuracy.{pdf,png} and F2_probe1_paired_diffs.{pdf,png}.
Accuracies, CIs, counts: summary.json only. Per-item differences (F2): items.jsonl, with the
score definitions of exp_p2/analyze_probe1.py (PRIMARY and SUPPL); the script asserts that the
recomputed count of true>mismatched, mean and median equal the summary.json values for every
plotted score.
"""
import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "runs" / "P2-PROBE-01"
OUT = ROOT / "figures" / "paper2"
OUT.mkdir(parents=True, exist_ok=True)

# Okabe-Ito colour-blind-safe palette
BLUE, VERM, GREEN, ORANGE, GREY = "#0072B2", "#D55E00", "#009E73", "#E69F00", "#555555"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.dpi": 300, "figure.dpi": 150,
})

summary = json.loads((RUN / "summary.json").read_text(encoding="utf8"))
res = summary["results"]
flat = {}
for grp, tab in res.items():
    for k, v in tab.items():
        flat[k] = dict(v, group=grp)
N = summary["n_items"]
rows = [json.loads(l) for l in (RUN / "items.jsonl").read_text(encoding="utf8").splitlines() if l.strip()]
assert len(rows) == N == 300


def save(fig, stem):
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{stem}.{ext}", dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


# ----------------------------------------------------------------------------- F1
LAYOUT = [  # (group title, colour, marker, [(key, display name)])
    ("Primary (declared before the run)", BLUE, "o", [("a_text", "a_text"), ("b_image", "b_image"), ("a_plus_b", "a_plus_b")]),
    ("Control (caption only)", VERM, "X", [("ctrl_text_only", "ctrl_text_only")]),
    ("Exploratory", GREEN, "s", [("a_pmi", "a_pmi"), ("a_full", "a_full"), ("a_full_pmi", "a_full_pmi"),
                                 ("b_k2", "b_k2"), ("b_full", "b_full"),
                                 ("a_pmi_plus_b", "a_pmi_plus_b"), ("a_full_pmi_plus_b_full", "a_full_pmi_plus_b_full")]),
]


def fig1():
    fig, ax = plt.subplots(figsize=(6.5, 3.9))
    y, yticks, ylabels, group_spans = 0.0, [], [], []
    for gname, col, mk, items in LAYOUT:
        y0 = y
        for key, name in items:
            v = flat[key]
            acc, lo, hi = v["accuracy"], v["ci95"][0], v["ci95"][1]
            ax.errorbar(acc, y, xerr=[[acc - lo], [hi - acc]], fmt=mk, color=col, ms=5.5 if mk != "X" else 6.5,
                        mec="black" if mk == "X" else col, mew=0.5, elinewidth=1.3, capsize=2.5, zorder=3)
            ax.text(1.04, y, f"{acc:.3f} [{lo:.3f}, {hi:.3f}]", transform=ax.get_yaxis_transform(),
                    va="center", ha="left", fontsize=8, color="black")
            yticks.append(y)
            ylabels.append(name)
            y += 1.0
        group_spans.append((gname, col, y0 - 0.5, y - 0.5))
        y += 1.5
    ymax = group_spans[-1][3]
    for gname, col, a, b in group_spans:
        ax.axhspan(a, b, color=col, alpha=0.10 if gname.startswith("Control") else 0.05, lw=0, zorder=0)
        ax.text(0.405, a - 0.12, gname, fontsize=8, fontweight="bold", color=col, va="bottom", ha="left", zorder=6,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.axvline(0.5, color=GREY, ls="--", lw=1.0, zorder=1)
    ax.text(0.5, -1.55, "chance", color=GREY, fontsize=8, ha="center", va="bottom")
    ax.set_xlim(0.40, 1.02)
    ax.set_ylim(ymax + 0.2, -1.6)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, family="monospace", fontsize=7.5)
    ax.set_xlabel(f"Matching accuracy (share of {N} images with true caption scoring higher)")
    ax.set_xticks(np.arange(0.4, 1.01, 0.1))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.text(1.04, -1.55, "acc. [95% CI]", transform=ax.get_yaxis_transform(), va="bottom", ha="left",
            fontsize=8, fontstyle="italic")
    save(fig, "F1_probe1_accuracy")


# ----------------------------------------------------------------------------- F2
def dd(key):
    return lambda t, m: t[key] - m[key]


DIFFS = {
    "a_text": dd("a8"),
    "a_pmi": lambda t, m: (t["a8"] - t["a8null"]) - (m["a8"] - m["a8null"]),
    "a_full_pmi": lambda t, m: (t["afull"] - t["afull_null"]) - (m["afull"] - m["afull_null"]),
    "b_image": dd("b8"),
    "b_full": dd("bfull"),
}
PANEL_COL = {"a_text": BLUE, "a_pmi": BLUE, "a_full_pmi": BLUE, "b_image": ORANGE, "b_full": ORANGE}


def fig2():
    diffs = {}
    for k, fn in DIFFS.items():
        d = np.array([fn(r["true"], r["mis"]) for r in rows])
        assert int((d > 0).sum()) == flat[k]["n_true_greater"], k
        assert abs(d.mean() - flat[k]["mean_diff"]) < 1e-9 and abs(np.median(d) - flat[k]["median_diff"]) < 1e-9, k
        diffs[k] = d
    fig, axes = plt.subplots(1, 5, figsize=(7.0, 3.1))
    rng = np.random.default_rng(0)
    for ax, (k, d) in zip(axes, diffs.items()):
        col = PANEL_COL[k]
        vp = ax.violinplot(d, positions=[0], widths=0.85, showextrema=False)
        for b in vp["bodies"]:
            b.set_facecolor(col)
            b.set_alpha(0.28)
            b.set_edgecolor(col)
            b.set_linewidth(0.8)
        ax.scatter(rng.uniform(-0.28, 0.28, len(d)), d, s=3, color=col, alpha=0.45, lw=0, zorder=2, rasterized=True)
        ax.boxplot(d, positions=[0], widths=0.2, showfliers=False, patch_artist=True, zorder=4,
                   medianprops=dict(color="black", lw=1.4), boxprops=dict(facecolor="white", edgecolor="black", lw=0.8),
                   whiskerprops=dict(lw=0.8), capprops=dict(lw=0.8))
        ax.axhline(0, color=VERM, lw=1.1, ls="--", zorder=5)
        ax.set_xlim(-0.6, 0.6)
        ax.set_xticks([])
        ax.set_title(k, family="monospace", fontsize=7.5, pad=14)
        ax.text(0.5, 1.015, f"acc. {flat[k]['accuracy']:.3f}", transform=ax.transAxes, ha="center", va="bottom", fontsize=8)
        ax.tick_params(axis="y", labelsize=7.5)
        for s in ("top", "right", "bottom"):
            ax.spines[s].set_visible(False)
        lo, hi = d.min(), d.max()
        pad = 0.05 * (hi - lo)
        ax.set_ylim(min(lo, 0) - pad, max(hi, 0) + pad)
    axes[0].set_ylabel("true minus mismatched score (nats)", fontsize=7.5)
    fig.tight_layout(w_pad=0.6)
    save(fig, "F2_probe1_paired_diffs")


if __name__ == "__main__":
    fig1()
    fig2()
    print("wrote", sorted(p.name for p in OUT.glob("F*_probe1_*")))
