"""Figure 4: census of value rules and reporting (random sample, 176 ranks of the 1106-record pool).

Panel (a): value-rule classes on the value-rule denominator (153 final, 154 sensitivity) and the reporting
fields F3, F4, F5, as bars with 95 percent Wilson intervals. Panel (b): number of papers carrying each
value-rule letter.

Every count comes from research/review/census/census-random-final.jsonl through the definitions of
analysis/census/summary_random.py (censuscounts.py runs that script, requires its output to equal
analysis/census/summary-random.log, and asserts each number used here against the log text). The Wilson
intervals use the same formula as summary_random.wilson; the five intervals printed in the log are asserted
string for string, and the two extra bars (NS and U) use the same function.

Writes paper/review/figures/fig04-census.pdf (+ preview PNG) and fig04-census.log (numbers plotted).

    python paper/review/scripts/fig04_census.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt

import censuscounts
from figstyle import C, FIGDIR, TEXTWIDTH_IN, save, setup

setup()
fin, sen, extra = censuscounts.load()
log = extra["log"]
W = extra["wilson"]               # summary_random.wilson, the string formatter of the log


def bar(c, key):
    """(k, n) for a bar of panel (a) under count dictionary c."""
    return {
        "either": (c["either"], c["n_v"]), "stated": (c["stated"], c["n_v"]), "NS": (c["NS"], c["n_v"]),
        "U": (c["U"], c["n_v"]), "f3": (c["f3"], c["n_m"]), "f4": (c["sweeps"], c["n_m"]), "f5": (c["f5"], c["n_sw"]),
    }[key]


# the five proportions printed in the log must be reproduced string for string; NS and U counts must be in the log
for name, c in (("final", fin), ("sensitivity", sen)):
    block = log.split("== sensitivity")[1] if name == "sensitivity" else log.split("== sensitivity")[0]
    for key, label in (("either", "non-plain or not stated:"), ("stated", "non-plain stated:       "),
                       ("f3", "diversity paired (F3):  "), ("f4", "step settings >= 2 (F4 yes/partial):"),
                       ("f5", "rule fixed stated among sweeps (F5):")):
        k, n = bar(c, key)
        assert f"  {label} {W(k, n)}" in block, (name, key)
    assert f"plain stated (U) {c['U']}, not stated (NS) {c['NS']};" in block

GROUPS = [
    ("Value rule of the headline result", "n_v", [("either", "Non-plain or not stated"), ("stated", "Stated non-plain"),
                                                  ("NS", "Not stated (NS)"), ("U", "Plain sampling stated (U)")]),
    ("Reporting, papers with a generated-sample metric", "n_m", [("f3", "Diversity paired with headline (F3)"),
                                                                 ("f4", "Headline at 2+ step settings (F4)")]),
    ("Papers that sweep steps", "n_sw", [("f5", "Value rule stated as fixed (F5)")]),
]
LETTERS = [("A", "A  argmax or greedy"), ("C", "C  confidence-ranked, token rule unstated"), ("G", "G  guidance"),
           ("M", "M  sequence-level selection"), ("P", "P  top-p or top-k"), ("S", "S  sample-then-filter"),
           ("T", "T  temperature")]

# ---------------------------------------------------------------- layout in inches
W_IN = TEXTWIDTH_IN
SLOT_A, SLOT_B = 0.235, 0.215
n_slots_a = sum(1 + len(rows) for _, _, rows in GROUPS)
n_slots_b = len(LETTERS)
LEFT_A, AX_W = 1.95, 2.0
H_A, H_B = n_slots_a * SLOT_A, n_slots_b * SLOT_B
TOP, GAP, BOT = 0.12, 0.62, 0.42
H_IN = TOP + H_A + GAP + H_B + BOT
fig = plt.figure(figsize=(W_IN, H_IN))
axa = fig.add_axes([LEFT_A / W_IN, (BOT + H_B + GAP) / H_IN, AX_W / W_IN, H_A / H_IN])
axb = fig.add_axes([LEFT_A / W_IN, BOT / H_IN, AX_W / W_IN, H_B / H_IN])

BLUE, VERM = C["blue"], C["vermilion"]
BH = 0.34
log_lines = []


def draw_bar(ax, y, val, lo, hi, final):
    off = -BH / 2 if final else BH / 2
    if final:
        ax.barh(y + off, val, height=BH * 0.92, color=BLUE, edgecolor=BLUE, linewidth=0.6, zorder=2)
    else:
        ax.barh(y + off, val, height=BH * 0.92, facecolor="white", edgecolor=VERM, hatch="////", linewidth=0.6, zorder=2)
    if lo is not None:
        ax.plot([lo, hi], [y + off, y + off], color=C["black"], lw=0.8, zorder=3)
        for xx in (lo, hi):
            ax.plot([xx, xx], [y + off - 0.09, y + off + 0.09], color=C["black"], lw=0.8, zorder=3)


# ---------------------------------------------------------------- panel (a)
slot = 0
ytick, ylab = [], []
for title, nkey, rows in GROUPS:
    ndf, nds = fin[nkey], sen[nkey]
    axa.text(-(LEFT_A - 0.3) / AX_W, slot, f"{title} (n = {ndf}; sensitivity {nds})", ha="left", va="center", fontsize=7,
             fontweight="bold", transform=axa.get_yaxis_transform(), clip_on=False)
    slot += 1
    for key, lab in rows:
        for c, final in ((fin, True), (sen, False)):
            k, n = bar(c, key)
            p, lo, hi = censuscounts.wilson_num(k, n)
            draw_bar(axa, slot, p, lo, hi, final)
            log_lines.append(f"(a) {key} {'final' if final else 'sensitivity'}: {W(k, n)}")
        ytick.append(slot)
        ylab.append(lab)
        kf, nf = bar(fin, key)
        ks, ns_ = bar(sen, key)
        axa.text(1.14, slot, f"{kf}/{nf}", ha="left", va="center", fontsize=7, color=BLUE, fontweight="bold",
                 transform=axa.get_yaxis_transform(), clip_on=False)
        axa.text(1.48, slot, f"{ks}/{ns_}", ha="left", va="center", fontsize=7, color=VERM, fontweight="bold",
                 transform=axa.get_yaxis_transform(), clip_on=False)
        slot += 1
axa.set_ylim(n_slots_a - 0.5, -0.5)
axa.set_xlim(0, 1)
axa.set_yticks(ytick)
axa.set_yticklabels(ylab)
axa.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
axa.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
axa.set_xlabel("proportion of papers (bar) with 95% Wilson interval (line)")
axa.tick_params(axis="y", length=0)
axa.xaxis.grid(True, color=C["lightgrey"], lw=0.5, zorder=0)
axa.set_axisbelow(True)
axa.spines["left"].set_visible(False)
# key for the two series (colour and fill both carry it)
from matplotlib.patches import Rectangle
tr = axa.get_yaxis_transform()
axa.add_patch(Rectangle((1.06, -0.2), 0.06, 0.4, facecolor=BLUE, edgecolor=BLUE, lw=0.6, transform=tr, clip_on=False))
axa.add_patch(Rectangle((1.40, -0.2), 0.06, 0.4, facecolor="white", edgecolor=VERM, hatch="////", lw=0.6, transform=tr, clip_on=False))
axa.text(1.14, 0, "final", ha="left", va="center", fontsize=7, color=BLUE, fontweight="bold", transform=tr, clip_on=False)
axa.text(1.48, 0, "sensitivity", ha="left", va="center", fontsize=7, color=VERM, fontweight="bold", transform=tr, clip_on=False)

# ---------------------------------------------------------------- panel (b)
ymax = max(max(fin["letters"].values()), max(sen["letters"].values()))
for i, (L, lab) in enumerate(LETTERS):
    for c, final in ((fin, True), (sen, False)):
        v = c["letters"][L]
        off = -BH / 2 if final else BH / 2
        if final:
            axb.barh(i + off, v, height=BH * 0.92, color=BLUE, edgecolor=BLUE, linewidth=0.6, zorder=2)
        else:
            axb.barh(i + off, v, height=BH * 0.92, facecolor="white", edgecolor=VERM, hatch="////", linewidth=0.6, zorder=2)
        axb.text(v + 0.6, i + off, str(v), ha="left", va="center", fontsize=7, color=BLUE if final else VERM, fontweight="bold")
        log_lines.append(f"(b) letter {L} {'final' if final else 'sensitivity'}: {v}")
axb.set_ylim(len(LETTERS) - 0.5, -0.5)
axb.set_xlim(0, 40)
axb.set_yticks(range(len(LETTERS)))
axb.set_yticklabels([lab for _, lab in LETTERS])
axb.tick_params(axis="y", length=0)
axb.set_xlabel("papers carrying the letter (a paper can carry several)")
axb.xaxis.grid(True, color=C["lightgrey"], lw=0.5, zorder=0)
axb.set_axisbelow(True)
axb.spines["left"].set_visible(False)

fig.text(0.004, 1 - 0.02, "(a)", fontsize=8, fontweight="bold", va="top")
fig.text(0.004, (BOT + H_B + 0.1) / H_IN, "(b)", fontsize=8, fontweight="bold", va="top")

(FIGDIR / "fig04-census.log").write_text("\n".join(log_lines) + "\n", encoding="utf8")
save(fig, "fig04-census")
