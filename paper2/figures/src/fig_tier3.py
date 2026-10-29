"""F8 / F8s: Tier-3 fusion comparison (pre-specified exploratory, SAP A4; confidence intervals only, no p-value).
Reads runs/P2-GATE-M4/tier3_fusion.json: cells.<jpeg10|noise0.1|splice128>.contrasts.<COMP>_minus_GM {diff, ci95, n_d, reading} for family P (F8);
ps_cells.<patch|swap>.contrasts.* for family PS on its own canvas (F8s; the file's ps_note: never plotted beside the P cells).
Output: F8_tier3_fusion (P cells), F8s_tier3_fusion_ps (PS cells). GATE-M is the reference (zero line)."""
from __future__ import annotations

import json

import matplotlib.pyplot as plt

import resultlib as R
import style as S
from style import COL, MM

COMPS = [  # key, label, marker
    ("MED", "median", "s"),
    ("TM-G", "trimmed mean, gate's flag count", "D"),
    ("TM20", "20% trimmed mean", "^"),
    ("SOFT-G", "discounting of gate-flagged tokens", "v"),
    ("SOFT-A", "reliability weighting, all tokens", "P"),
]
READ = {"below": "below", "above": "above", "not_distinguishable": "n.d.", "identical": "identical"}
t3 = R.jload("P2-GATE-M4/tier3_fusion.json")


def draw(cells, titles, out, xlim, ticks):
    S.apply()
    ncell = len(cells)
    W = S.W2
    LEFT, PW, TW, GAP = 47.0, 29.0, 15.0, 2.0
    pitch = 8.0
    AXH = pitch * len(COMPS)
    BOT, TOP = 13.0, 17.0
    H = BOT + AXH + TOP
    fig = plt.figure(figsize=(W * MM, H * MM))
    for j, (ck, title) in enumerate(zip(cells, titles)):
        c = (t3["cells"] if ck in t3["cells"] else t3["ps_cells"])[ck]
        x0 = LEFT + j * (PW + TW + GAP)
        ax = fig.add_axes([x0 / W, BOT / H, PW / W, AXH / H])
        ax.set_xlim(*xlim)
        ax.set_ylim(len(COMPS) - 0.5, -0.5)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_xticks(ticks)
        ax.set_xticklabels([R.fmt(v, 2, plus=(v > 0)) if v != 0 else "0" for v in ticks])
        ax.axvline(0, color=COL["gate"], lw=1.0, zorder=1)
        ax.set_xlabel("comparator minus GATE-M", fontsize=7)
        fig.text(x0 / W, (BOT + AXH + 8.0) / H, title, fontsize=8, weight="bold", va="center")
        fig.text(x0 / W, (BOT + AXH + 4.2) / H, f"$n={c['n']}$", fontsize=6.2, color=COL["sub"], va="center")
        fig.text((x0 + PW + 1.0) / W, (BOT + AXH + 4.2) / H, "$n_d$, reading", fontsize=6.2, color=COL["sub"], va="center")
        for i, (key, lab, mk) in enumerate(COMPS):
            ct = c["contrasts"][f"{key}_minus_GM"]
            if i % 2 == 0:
                ax.axhspan(i - 0.5, i + 0.5, color="#F6F6F6", zorder=0, lw=0)
            lo, hi = ct["ci95"]
            filled = ct["reading"] in ("below", "above")
            ax.plot([lo, hi], [i, i], color=COL["ink"], lw=1.1, solid_capstyle="butt", zorder=3)
            ax.plot([ct["diff"]], [i], marker=mk, ms=4.2, mfc=COL["ink"] if filled else "white", mec=COL["ink"], mew=0.9, ls="none", zorder=4)
            yc = BOT + AXH - (i + 0.5) * pitch
            fig.text((x0 + PW + 1.0) / W, yc / H, f"{ct['n_d']}, {READ[ct['reading']]}", fontsize=6.4, va="center",
                     weight="bold" if filled else "normal")
            if j == 0:
                fig.text((LEFT - 2.0) / W, yc / H, lab, fontsize=6.8, ha="right", va="center")
    fig.text((LEFT - 2.0) / W, (BOT + AXH + 4.2) / H, "comparator (reference: GATE-M)", fontsize=6.2, color=COL["sub"], ha="right", va="center")
    S.save(fig, out)
    return {ck: {k: (t3["cells"] if ck in t3["cells"] else t3["ps_cells"])[ck]["contrasts"][f"{k}_minus_GM"] for k, _, _ in COMPS} for ck in cells}


def span(cells):
    v = []
    for ck in cells:
        c = (t3["cells"] if ck in t3["cells"] else t3["ps_cells"])[ck]
        for k, _, _ in COMPS:
            v += c["contrasts"][f"{k}_minus_GM"]["ci95"]
    return min(v), max(v)


P = ["jpeg10", "noise0.1", "splice128"]
PS = ["patch", "swap"]
lo, hi = span(P + PS)
xlim = (-0.075, 0.045)
ticks = [-0.05, 0.0, 0.03]
rp = draw(P, ["JPEG", "noise", "splice"], "F8_tier3_fusion", xlim, ticks)
rs = draw(PS, ["patch", "swap"], "F8s_tier3_fusion_ps", xlim, ticks)
print("span", lo, hi)
for ck, d in {**rp, **rs}.items():
    print(ck, {k: (round(v["diff"], 4), [round(x, 4) for x in v["ci95"]], v["n_d"], v["reading"]) for k, v in d.items()})
print(t3["label"], "|", t3["multiplicity"])
