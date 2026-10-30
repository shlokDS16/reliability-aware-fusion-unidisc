"""Study 1 detection figure (column width; replaces the main-text detection table, which stays for the supplement).

(a) Mean per-item AUROC against changed-code labels with the 95% percentile-bootstrap interval over items, per corruption, for the gate's
    masked-likelihood score q, the one-pass TbV score of the non-finetuned model, and the best cheap rival in the orientation chosen on the
    same items (sign oracle; its name and sign in the row label). Dotted line: chance (0.5).
(b) Paired difference q minus rival with its 95% interval: on the detection items, where the rival and its sign were selected (filled), and
    with the rival frozen on all detection items and re-scored on the test items (S-D2; JPEG and noise only; open).
Own canvas: nothing of family P, PS accuracy, Tier 3 or H (SAP A4.2.5 item 4).

Reads: runs/P2-GATE-M1/analysis.json keys table.<corr>.{q,tbv,<rival>}.{mean,lo,hi,n}, paired_q_vs_best_cheap.<corr>.{best_cheap,rival_sign,
       diff_mean,ci95,n_items}; runs/P2-GATE-M4/analysis.json keys s_d2.per_corruption.{jpeg,noise}.{rival,diff_mean,ci95,n_eligible,tested}.
Writes runs/P2-PAPER-FIGS/fig_detection.json. Output paper2-tnnls/figures/fig_detection.pdf (+ png preview).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import figstyle as S
from figstyle import C, MINUS

S.apply()
M1 = S.jload("P2-GATE-M1/analysis.json")
SD2 = S.jload("P2-GATE-M4/analysis.json")["s_d2"]["per_corruption"]
ROWS = [("patch", r"patch, $8\times8$ codes"), ("swap", r"swap, 15% of codes"), ("jpeg", "JPEG, quality 10"), ("noise", r"noise, $\sigma=0.1$")]
RNAME = {"tex": "texture", "plainB": r"plain $B$"}
rec = []
for k, nm in ROWS:
    t, p = M1["table"][k], M1["paired_q_vs_best_cheap"][k]
    rv = p["best_cheap"]
    assert t["q"]["n"] == t["tbv"]["n"] == t[rv]["n"]
    r = dict(corr=k, label=nm, n=t["q"]["n"], q=t["q"], tbv=t["tbv"], rival=rv, rival_base=p["rival_base"], rival_sign=p["rival_sign"],
             rival_auroc=t[rv], diff_same=dict(mean=p["diff_mean"], ci95=p["ci95"], n=p["n_items"]))
    if k in SD2 and SD2[k]["tested"]:
        sd = SD2[k]
        assert sd["rival"] == rv, "frozen rival must be the M1 rival"
        r["diff_frozen"] = dict(mean=sd["diff_mean"], ci95=sd["ci95"], n=sd["n_eligible"])
    rec.append(r)
S.trace("fig_detection", "fig_detection.py", dict(
    source="runs/P2-GATE-M1/analysis.json table.*, paired_q_vs_best_cheap.*; runs/P2-GATE-M4/analysis.json s_d2.per_corruption.*", rows=rec))

fig = plt.figure(figsize=(S.COL1, 2.55))
axa = fig.add_axes([0.385, 0.155, 0.355, 0.60])
axb = fig.add_axes([0.770, 0.155, 0.215, 0.60], sharey=axa)
OFF = 0.22
SER = [("q", C["blue"], "o", C["blue"]), ("tbv", C["grey"], "s", "white"), ("rival", C["verm"], "^", C["verm"])]
for i, r in enumerate(rec):
    for j, (key, col, mk, mfc) in enumerate(SER):
        v = r["rival_auroc"] if key == "rival" else r[key]
        y = i + (j - 1) * OFF
        axa.plot([v["lo"], v["hi"]], [y, y], color=col, lw=1.1, solid_capstyle="butt", zorder=3)
        axa.plot([v["mean"]], [y], marker=mk, ms=3.1, mfc=mfc, mec=col if mfc != "white" else C["ink"], mew=0.7, ls="none", zorder=4)
    d = r["diff_same"]
    axb.plot(d["ci95"], [i - 0.12] * 2, color=C["ink"], lw=1.1, solid_capstyle="butt", zorder=3)
    axb.plot([d["mean"]], [i - 0.12], marker="D", ms=3.0, mfc=C["ink"], mec=C["ink"], ls="none", zorder=4)
    if "diff_frozen" in r:
        d = r["diff_frozen"]
        axb.plot(d["ci95"], [i + 0.12] * 2, color=C["ink"], lw=1.1, solid_capstyle="butt", zorder=3)
        axb.plot([d["mean"]], [i + 0.12], marker="D", ms=3.0, mfc="white", mec=C["ink"], mew=0.8, ls="none", zorder=4)
for i in range(len(rec) - 1):
    for ax in (axa, axb):
        ax.axhline(i + 0.5, color=C["vlgrey"], lw=0.6, zorder=0)
axa.axvline(0.5, color=C["grey"], lw=0.8, ls=(0, (1, 1.5)), zorder=1)
axa.set_xlim(0.45, 1.0)
axa.set_xticks([0.5, 0.75, 1.0])
axa.set_xticklabels(["0.5", "0.75", "1"])
axa.set_xlabel("AUROC (95% CI)", labelpad=1.5)
axa.set_ylim(len(rec) - 0.5, -0.5)
axa.set_yticks(range(len(rec)))
sgn = lambda s: MINUS if s < 0 else "+"
axa.set_yticklabels([f"{r['label']}, $n={r['n']}$\nrival: {RNAME[r['rival_base']]} ({sgn(r['rival_sign'])})" for r in rec], linespacing=1.15)
axa.tick_params(axis="y", length=0)
axb.axvline(0, color=C["ink"], lw=0.8, zorder=1)
lo = min(min(r["diff_same"]["ci95"][0], r.get("diff_frozen", r["diff_same"])["ci95"][0]) for r in rec)
axb.set_xlim(lo * 1.12, -lo * 0.12)
axb.set_xticks([-0.2, 0])
axb.set_xticklabels([f"{MINUS}0.2", "0"])
axb.set_xlabel(r"$q$ minus rival", labelpad=1.5)
plt.setp(axb.get_yticklabels(), visible=False)
axb.tick_params(axis="y", length=0)
axa.text(-0.02, 1.02, "(a)", transform=axa.transAxes, fontsize=S.FS + 1, fontweight="bold", va="bottom", ha="left")
axb.text(-0.02, 1.02, "(b)", transform=axb.transAxes, fontsize=S.FS + 1, fontweight="bold", va="bottom", ha="left")
h = [Line2D([], [], color=C["blue"], marker="o", ms=3.1, lw=1.1, label=r"gate score $q$"),
     Line2D([], [], color=C["grey"], marker="s", ms=3.1, mfc="white", mec=C["ink"], lw=1.1, label="one-pass TbV score"),
     Line2D([], [], color=C["verm"], marker="^", ms=3.1, lw=1.1, label="rival, sign chosen on same items"),
     Line2D([], [], color=C["ink"], marker="D", ms=3.0, lw=1.1, label=r"(b) same items"),
     Line2D([], [], color=C["ink"], marker="D", ms=3.0, mfc="white", lw=1.1, label=r"(b) frozen rival, test items")]
fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.005, 1.0), ncol=2, frameon=False, handlelength=1.8, columnspacing=1.0,
           handletextpad=0.5, borderaxespad=0.2, labelspacing=0.3)
S.save(fig, "fig_detection")
