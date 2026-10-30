"""Study 1 method figure (two-column): masked-likelihood token gating with a threshold from conformal risk control, and the calibration check.

(a) Schematic (matplotlib patches, no data; token patterns are a fixed pseudo-random drawing, seed 5): clean calibration pairs -> suspicion
    u_ij = D_ij - B_ij -> threshold tau-hat by conformal risk control at level alpha -> on a test pair, keep indicator I_j = 1[u_j <= tau-hat];
    flagged tokens (I_j = 0) are withheld by masking -> S_G = sum_j I_j Delta_j -> Y_G = 1[S_G > 0]. Study 1 symbols only (sections/study1.tex).
(b) Realised flagged share of the clean test pairs against the nominal level alpha, with the line y = x (the bound of prop:crc).
(c) The same as an excess F - alpha with its 95% bootstrap interval, plus the exploratory re-split replication at the primary level.
Nothing of family P, PS, detection or H on this canvas (SAP A4.2.5 items 3-4).

Reads: runs/P2-GATE-M4/analysis.json keys calibration.fap_check.per_alpha.<alpha>.{alpha,F,ci_bootstrap,n_test,n_cal,Z_cal,violation},
       calibration.fap_check.critical_value, calibration.split_replication.{alpha,reps,mean_F_minus_alpha,q025,q975};
       runs/P2-GATE-M2/threshold.json keys n_cal, K, thresholds.<alpha>.feasible.
Writes: runs/P2-PAPER-FIGS/fig_gate_method.json (plotted values, script sha). Output: paper2-tnnls/figures/fig_gate_method.pdf (+ png preview).
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

import figstyle as S
from figstyle import C, MINUS
from schem import Canvas, tint

S.apply()
A = S.jload("P2-GATE-M4/analysis.json")["calibration"]
THR = S.jload("P2-GATE-M2/threshold.json")
fc = A["fap_check"]
alphas = sorted(fc["per_alpha"], key=float)
pts = []
for k in alphas:
    r = fc["per_alpha"][k]
    assert r["violation"] is False and all(THR["thresholds"][k]["feasible"] for _ in [0])
    pts.append(dict(alpha=r["alpha"], F=r["F"], lo=r["ci_bootstrap"][0], hi=r["ci_bootstrap"][1], n_test=r["n_test"], n_cal=r["n_cal"],
                    Z_cal=r["Z_cal"]))
assert len({p["n_test"] for p in pts}) == 1 and pts[0]["n_cal"] == THR["n_cal"]
SR = A["split_replication"]
N_CAL, N_TEST = THR["n_cal"], pts[0]["n_test"]
S.trace("fig_gate_method", "fig_gate_method.py", dict(
    source="runs/P2-GATE-M4/analysis.json calibration.fap_check.per_alpha.*, calibration.split_replication; runs/P2-GATE-M2/threshold.json n_cal",
    points=pts, split_replication=SR, critical_value=fc["critical_value"], schematic="no data; token patterns drawn with numpy seed 5"))

# ---- canvas -------------------------------------------------------------------------------------------------------------------------------
W_MM, H_MM, WA = S.COL2 / (1 / 25.4), 57.0, 124.0
fig = plt.figure(figsize=(S.COL2, H_MM / 25.4))
cv = Canvas(fig, [0, 0, WA / W_MM, 1], WA, H_MM)
BLUE = C["blue"]
rng = np.random.default_rng(5)
N, CS = 5, 2.1
GW = N * CS


def u_grid(x, y, seed_shift=0.0):
    u = rng.normal(0, 1, (N, N)) + seed_shift
    cols = [[tint(BLUE, 0.12 + 0.75 * (np.clip(v, -2, 2.4) + 2) / 4.4) for v in row] for row in u]
    cv.grid(x, y, cols, CS)
    return u


cv.tag(0.5, H_MM - 0.3, "(a)")
YT, YB = 41.5, 13.0          # lane centres
cv.text(5.5, H_MM - 2.2, "calibration, before any test item", ha="left", fs=S.FS, style="italic", color=C["grey"])
cv.text(5.5, 26.6, "test pair", ha="left", fs=S.FS, style="italic", color=C["grey"])

# top lane: clean calibration pairs -> u_ij -> tau-hat
cv.box(1.0, YT - 6.5, 24.5, 13)
cv.text(13.25, YT + 2.2, "clean pairs", fs=S.FS)
cv.text(13.25, YT - 2.6, rf"$n_{{\rm cal}}={N_CAL}$", fs=S.FS)
cv.arrow(26.5, YT, 31.0, YT)
u_grid(32.0, YT - GW / 2)
cv.text(32.0 + GW / 2, YT - GW / 2 - 2.8, r"$u_{ij}$", fs=S.FS)
cv.arrow(32.0 + GW + 1.0, YT, 48.0, YT)
cv.box(49.0, YT - 8.0, 31.0, 16.0, ec=BLUE, lw=1.0)
cv.text(64.5, YT + 4.4, "conformal risk control", fs=S.FS)
cv.text(64.5, YT - 0.2, r"$L_i(\tau)$: share of $u_{ij}>\tau$", fs=S.FS)
cv.text(64.5, YT - 4.6, r"$\hat\tau$ at level $\alpha$", fs=S.FS)
cv.box(84.0, YT - 6.5, 39.0, 13.0, ls=(0, (3, 1.6)), lw=0.7)
cv.text(103.5, YT + 2.3, "guarantee for a clean pair:", fs=S.FS)
cv.text(103.5, YT - 2.5, r"$\mathbb{E}\,L_{\rm test}(\hat\tau)\leq\alpha$  (checked in b, c)", fs=S.FS)
cv.arrow(80.0, YT, 84.0, YT, style="-", lw=0.7)

# bottom lane: test pair -> u_j -> I_j -> S_G -> Y_G
cv.box(1.0, YB - 6.5, 24.5, 13)
cv.text(13.25, YB + 2.2, "image tokens", fs=S.FS)
cv.text(13.25, YB - 2.6, r"$j=1,\dots,m$", fs=S.FS)
cv.arrow(26.5, YB, 31.0, YB)
u = u_grid(32.0, YB - GW / 2, 0.15)
cv.text(32.0 + GW / 2, YB - GW / 2 - 2.8, r"$u_j=D_j-B_j$", fs=S.FS)
cv.arrow(32.0 + GW + 1.0, YB, 58.5, YB)
thr = np.quantile(u, 0.84)
keep = u <= thr
gx = 59.5
cv.grid(gx, YB - GW / 2, [["#F2F2F2" if k else "#3F3F3F" for k in row] for row in keep], CS)
cv.text(gx + GW / 2, YB - GW / 2 - 2.8, r"$I_j=\mathbb{1}[u_j\leq\hat\tau]$", fs=S.FS)
cv.arrow(64.5, YT - 8.0, gx + GW / 2, YB + GW / 2 + 1.0, color=BLUE, lw=1.0)
cv.text(65.8, 26.6, r"$\hat\tau$", ha="left", fs=S.FS, color=BLUE)
cv.text(gx + GW + 1.4, YB + 3.9, "flagged:", ha="left", fs=S.FS)
cv.text(gx + GW + 1.4, YB + 0.4, "withheld", ha="left", fs=S.FS)
cv.ax.add_patch(plt.Rectangle((gx + GW + 1.4, YB - 4.3), 2.1, 2.1, fc="#3F3F3F", ec="#8A8A8A", lw=0.35, zorder=3))
cv.text(gx + GW + 4.3, YB - 3.25, r"$I_j=0$", ha="left", fs=S.FS)
cv.arrow(84.0, YB, 87.5, YB)
cv.box(88.5, YB - 6.5, 17.0, 13)
cv.text(97.0, YB + 2.4, "sum", fs=S.FS)
cv.text(97.0, YB - 2.4, r"$S_{\rm G}=\sum_j I_j\Delta_j$", fs=S.FS - 0.5)
cv.arrow(97.0, 26.0, 97.0, YB + 6.5)
cv.text(97.0, 28.2, r"$\Delta_j$ (Fig. 1)", fs=S.FS)
cv.arrow(105.5, YB, 108.5, YB)
cv.box(109.5, YB - 6.5, 13.5, 13, lw=1.0)
cv.text(116.25, YB + 2.4, "decision", fs=S.FS)
cv.text(116.25, YB - 2.4, r"$S_{\rm G}>0$", fs=S.FS)

# ---- (b) realised vs nominal, (c) excess -------------------------------------------------------------------------------------------------
L, Wd = 139.0 / W_MM, 41.0 / W_MM
axb = fig.add_axes([L, 30.5 / H_MM, Wd, 23.5 / H_MM])
axc = fig.add_axes([L, 8.0 / H_MM, Wd, 17.5 / H_MM], sharex=axb)
al = np.array([p["alpha"] for p in pts])
F = np.array([p["F"] for p in pts])
lo = np.array([p["lo"] for p in pts])
hi = np.array([p["hi"] for p in pts])
xmax = 0.11
axb.fill_between([0, xmax], [0, 0], [0, xmax], color=C["blue"], alpha=0.10, lw=0, zorder=0)
axb.plot([0, xmax], [0, xmax], color=C["ink"], lw=0.8, ls=(0, (3, 2)), zorder=1)
axb.errorbar(al, F, yerr=[F - lo, hi - F], fmt="o", ms=3.4, mfc=BLUE, mec=C["ink"], mew=0.5, ecolor=BLUE, elinewidth=1.0, capsize=0, zorder=4)
axb.set_xlim(0, xmax)
axb.set_ylim(0, xmax)
axb.set_yticks([0, 0.05, 0.10])
axb.set_yticklabels(["0", "0.05", "0.10"])
axb.set_ylabel("flagged share", labelpad=2)
axb.text(0.072, 0.087, r"$\mathrm{share}=\alpha$", rotation=0, fontsize=S.FS, ha="right", va="bottom")
axb.text(0.104, 0.010, r"$\mathrm{share}\leq\alpha$", fontsize=S.FS, ha="right", va="bottom", color=C["grey"])
plt.setp(axb.get_xticklabels(), visible=False)
axb.text(-0.36, 1.0, "(b)", transform=axb.transAxes, fontsize=S.FS + 1, fontweight="bold", va="top", ha="left")

axc.axhline(0, color=C["ink"], lw=0.8, zorder=1)
axc.errorbar(al, F - al, yerr=[F - lo, hi - F], fmt="o", ms=3.4, mfc=BLUE, mec=C["ink"], mew=0.5, ecolor=BLUE, elinewidth=1.0, capsize=1.6,
             capthick=0.8, zorder=4)
xs = SR["alpha"] + 0.008
axc.errorbar([xs], [SR["mean_F_minus_alpha"]], yerr=[[SR["mean_F_minus_alpha"] - SR["q025"]], [SR["q975"] - SR["mean_F_minus_alpha"]]],
             fmt="o", ms=3.4, mfc="white", mec=C["ink"], mew=0.8, ecolor=C["grey"], elinewidth=1.0, capsize=1.6, capthick=0.8, zorder=4)
lo_y = min(SR["q025"], float((lo - al).min()))
axc.set_ylim(lo_y * 1.55, -lo_y * 0.55)
axc.yaxis.set_major_locator(plt.MaxNLocator(3))
axc.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: "0" if abs(v) < 1e-12 else f"{v:.3f}".replace("-", MINUS)))
axc.set_xticks([0.01, 0.05, 0.10])
axc.set_xticklabels(["0.01", "0.05", "0.10"])
axc.set_xlabel(r"nominal level $\alpha$", labelpad=1.5)
axc.set_ylabel(r"share $-\ \alpha$", labelpad=2)
axc.text(-0.36, 1.06, "(c)", transform=axc.transAxes, fontsize=S.FS + 1, fontweight="bold", va="top", ha="left")
S.save(fig, "fig_gate_method")
print("points:", [(p["alpha"], round(p["F"], 4)) for p in pts], "re-split:", SR["mean_F_minus_alpha"])
