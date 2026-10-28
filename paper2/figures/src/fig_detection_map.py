"""F4: detection map. Per-item mean AUROC of each score against the changed-code labels Z, with 95% intervals, per corruption.

Reads ONLY runs/P2-GATE-M1/analysis.json (keys table.<corruption>.<score> = {mean, lo, hi, n}; falsifier.per_corruption and
paired_q_vs_best_cheap for the paired differences). Nothing is typed by hand. 200 items; JPEG 197 and noise 198 usable
(table.<c>._n_excluded). Interval: percentile bootstrap over items, 10,000 resamples (analysis.json meta).
Rivals (patch texture, neighbour codebook distance, code rarity) are drawn in the better of their two orientations (the sign oracle
of SAP A1.2); a trailing minus in the number column marks the reversed orientation. No claim that q beats cheap methods (K2).
Output: paper2/figures/F4_detection_map.pdf + .png (190 mm)."""
from __future__ import annotations

import json

import matplotlib.pyplot as plt

import style as S
from style import COL, MM

S.apply()
MINUS = "−"
d = json.load(open(S.REPO / "runs" / "P2-GATE-M1" / "analysis.json", encoding="utf-8"))
T = d["table"]
CORRS = [("patch", "patch", "sanity corruption"), ("swap", "swap", "sanity corruption"),
         ("jpeg", "JPEG", "realistic corruption"), ("noise", "noise", "realistic corruption")]

# row spec: (key, label, marker, colour, hollow, group, choose_orientation)
ROWS = [
    ("q", r"$q_j$ (null-normalised)", "o", COL["flag"], False, 0, False),
    ("plainB", r"plain $B_j$", "s", COL["flag"], True, 0, False),
    ("tbv", "TbV-score (non-finetuned)", "^", COL["tbv"], False, 0, False),
    ("tex", "patch texture", "D", COL["rival"], True, 1, True),
    ("nbr", "neighbour code distance", "D", COL["rival"], True, 1, True),
    ("rarity", "code rarity", "D", COL["rival"], True, 1, True),
    ("s3", r"uncertainty $s_3$", "D", COL["rival"], True, 1, False),
    ("r_original", r"$A_j-B_j$ (cancellation)", "x", COL["ctrl"], False, 2, False),
    ("random", "random scores", "x", COL["ctrl"], False, 2, False),
]
GROUPS = ["UniDisc masked likelihood", "cheap rivals (sign chosen on data)", "controls"]


def value(corr, key, choose):
    """(mean, lo, hi, n, reversed) or None; for rivals the better of the two orientations."""
    t = T[corr]
    cands = []
    if key in t:
        cands.append((t[key], False))
    if choose and f"{key}_neg" in t:
        cands.append((t[f"{key}_neg"], True))
    cands = [(v, r) for v, r in cands if isinstance(v, dict) and v.get("mean") is not None and v["mean"] == v["mean"]]
    if not cands:
        return None
    v, r = max(cands, key=lambda c: c[0]["mean"])
    return v["mean"], v["lo"], v["hi"], v["n"], r


# ---- geometry (mm) ---------------------------------------------------------------------------------------------------------
W, H = S.W2, 89.0
fig = plt.figure(figsize=(W * MM, H * MM))
LEFT, AXW, NUMW, GAPX = 41.0, 25.5, 8.5, 1.6
BOT, AXH = 22.0, 55.0
ypos, y = [], 0.0
prev = None
for r in ROWS:
    if prev is not None and r[5] != prev:
        y += 0.9
    ypos.append(y)
    y += 1.0
    prev = r[5]
YMAX = y - 0.5
for i, (corr, nm, sub) in enumerate(CORRS):
    x0 = LEFT + i * (AXW + NUMW + GAPX)
    ax = fig.add_axes([x0 / W, BOT / H, AXW / W, AXH / H])
    ax.set_xlim(0.4, 1.0)
    ax.set_ylim(YMAX, -0.6)
    ax.axvline(0.5, color=COL["ctrl"], lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.set_xticks([0.5, 0.75, 1.0])
    ax.set_xticklabels(["0.5", "0.75", "1"])
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", length=2.5)
    ax.set_xlabel("per-item AUROC", fontsize=7)
    n_q = T[corr]["q"]["n"]
    ax.set_title(f"{nm}  ($n={n_q}$)", fontsize=8, weight="bold", loc="left", pad=11)
    ax.text(0, 1.012, sub, transform=ax.transAxes, fontsize=6.2, color=COL["sub"], va="bottom")
    vals = [value(corr, r[0], r[6]) for r in ROWS]
    best = max((v[0] for v in vals if v), default=None)
    prevg = None
    for (key, lab, mk, col, hollow, g, ch), yy, v in zip(ROWS, ypos, vals):
        if prevg is not None and g != prevg:
            ax.axhline(yy - 0.95 / 2 - 0.05, color=COL["faint"], lw=0.5, zorder=0)
        prevg = g
        if v is None:
            ax.text(0.7, yy, "n/a (no pixels)" if key == "tex" else "n/a", fontsize=6.2, color=COL["sub"], va="center", ha="center")
            continue
        m, lo, hi, n, rev = v
        ax.plot([lo, hi], [yy, yy], color=col, lw=1.1, solid_capstyle="butt", zorder=3)
        ax.plot([m], [yy], marker=mk, ms=3.8 if mk != "x" else 3.6, mfc="white" if hollow else col, mec=col, mew=0.9 if mk != "x" else 1.0,
                ls="none", zorder=4)
        ax.text(1.025, yy, f"{m:.3f}" + (MINUS if rev else ""), fontsize=6.2, ha="left", va="center", clip_on=False,
                weight="bold" if abs(m - best) < 1e-12 else "normal", color=COL["ink"])
    if i == 0:
        ax.text(0.515, ypos[-1], "chance", fontsize=6.0, color=COL["ctrl"], va="center", ha="left")
        for (key, lab, mk, col, hollow, g, ch), yy in zip(ROWS, ypos):
            ax.text(-0.012, yy, lab, transform=ax.get_yaxis_transform(), fontsize=6.8, ha="right", va="center", clip_on=False)
        gy = {}
        for r, yy in zip(ROWS, ypos):
            gy.setdefault(r[5], yy)
        for g, yy in gy.items():
            ax.text(-(LEFT - 1.0) / AXW, yy - 0.78, GROUPS[g], transform=ax.get_yaxis_transform(), fontsize=6.2, ha="left", va="center",
                    color=COL["sub"], weight="bold", clip_on=False)

# paired differences under each panel (paired bootstrap, 95% percentile interval)
pq = d["paired_q_vs_best_cheap"]
fa = d["falsifier"]["per_corruption"]
NAMES = {"plainB": r"plain $B_j$", "tex_neg": "texture, reversed", "tex": "texture"}
for i, (corr, nm, sub) in enumerate(CORRS):
    x0 = LEFT + i * (AXW + NUMW + GAPX)
    src = fa.get(corr) or pq.get(corr)
    diff, lo, hi, rival = src["diff_mean"], src["ci95"][0], src["ci95"][1], src["best_cheap"]
    fig.text(x0 / W, (BOT - 12.2) / H, r"$q$ minus best rival:", fontsize=6.2, color=COL["sub"], va="center")
    fig.text(x0 / W, (BOT - 15.2) / H, NAMES.get(rival, rival), fontsize=6.2, color=COL["sub"], va="center")
    fig.text(x0 / W, (BOT - 18.4) / H, f"{diff:+.3f} [{lo:+.3f}, {hi:+.3f}]".replace("-", MINUS), fontsize=6.6, va="center", color=COL["ink"])

S.save(fig, "F4_detection_map")
print(json.dumps({c: {r[0]: (round(value(c, r[0], r[6])[0], 3) if value(c, r[0], r[6]) else None) for r in ROWS} for c, _, _ in CORRS}))
