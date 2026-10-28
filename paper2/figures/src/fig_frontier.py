"""F_frontier: when does hard gating raise the SNR of an additive evidence sum? THEORY ONLY, no measured points, no run data.

Closed form: paper2/sections/method.tex (Eq. snr, lines ~290-314), read from exp_p2/gate/theory.py (pinned; imported by file path,
never edited). For mu_c = 0 the gate raises E[S]/sqrt(Var[S]) iff
    rho sigma_c^2 (beta - 2 alpha + alpha^2) > alpha (1 - alpha) (1 - rho) (sigma^2 + mu^2),
i.e. with kappa = rho sigma_c^2 / ((1 - rho)(sigma^2 + mu^2)):
    beta > beta*(alpha; kappa) = 2 alpha - alpha^2 + alpha (1 - alpha) / kappa .
The frontier reaches beta = 1 at alpha = kappa / (1 + kappa); beta = 2 alpha - alpha^2 is the kappa -> infinity limit (necessary).
The script verifies the analytic boundary against theory.special_case_inequality on a grid before drawing.
Output: paper2/figures/F5_gating_frontier.pdf + .png (190 mm)."""
from __future__ import annotations

import importlib.util
import json

import matplotlib.pyplot as plt
import numpy as np

import style as S
from style import COL, MM

S.apply()

spec = importlib.util.spec_from_file_location("theory", S.REPO / "exp_p2" / "gate" / "theory.py")
theory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(theory)

KAPPAS = [0.5, 1, 2, 5, 20]
ALPHAS_PROTOCOL = [0.01, 0.05, 0.10]      # protocol.tex: alpha in {0.01, 0.05, 0.10}, 0.05 primary
A_MAX, B_MAX = 0.15, 0.70


def beta_star(alpha, kappa):
    return 2 * alpha - alpha ** 2 + alpha * (1 - alpha) / kappa


# ---- check the analytic boundary against the pinned closed form -------------------------------------------------------
rng = np.random.default_rng(0)
mism = 0
n_checked = 0
for kappa in KAPPAS:
    for a in np.linspace(0.005, 0.30, 40):
        for b in np.linspace(0.0, 1.0, 41):
            gap = b - beta_star(a, kappa)
            if abs(gap) < 1e-6:
                continue
            # rho = 0.5, mu = 0, sigma^2 = 1, sigma_c^2 = kappa  ->  kappa_model = rho sigma_c^2 / ((1-rho)(sigma^2+mu^2)) = kappa
            helps = theory.special_case_inequality(0.5, a, b, 0.0, 1.0, kappa)
            mism += int(helps != (gap > 0))
            n_checked += 1
print(f"boundary check against exp_p2/gate/theory.py: {n_checked} grid points, {mism} mismatches")
assert mism == 0
nec_005 = 2 * 0.05 - 0.05 ** 2
assert abs(nec_005 - 0.0975) < 1e-12

# ---- figure -------------------------------------------------------------------------------------------------------------
W, H = S.W2, 74.0
fig = plt.figure(figsize=(W * MM, H * MM))


def axmm(x, y, w, h):
    return fig.add_axes([x / W, y / H, w / W, h / H])


axa = axmm(15.0, 12.0, 76.0, 54.0)
axb = axmm(131.0, 12.0, 54.0, 54.0)

# (a) the (alpha, beta) plane --------------------------------------------------------------------------------------------
al = np.linspace(0, A_MAX, 400)
blue = plt.get_cmap("Blues")
fills = []
for i, kappa in enumerate(KAPPAS[::-1]):                         # largest kappa first (largest region, lightest)
    axa.fill_between(al, np.minimum(beta_star(al, kappa), B_MAX), B_MAX, color=COL["flag"], alpha=0.13, lw=0, zorder=1)
for i, kappa in enumerate(KAPPAS):
    shade = blue(0.45 + 0.5 * (len(KAPPAS) - 1 - i) / (len(KAPPAS) - 1))
    shade = blue(0.95 - 0.5 * i / (len(KAPPAS) - 1))
    axa.plot(al, beta_star(al, kappa), color=shade, lw=1.2, zorder=3)
    xe = A_MAX
    ye = beta_star(xe, kappa)
    ytxt = [0.64, 0.545, 0.455, 0.37, 0.285][i] if False else None
nec = 2 * al - al ** 2
axa.plot(al, nec, color=COL["ink"], lw=1.3, ls=(0, (4, 2)), zorder=4)
axa.plot(al, al, color=COL["ctrl"], lw=1.0, zorder=3)
axa.set_xlim(0, A_MAX)
axa.set_ylim(0, B_MAX)
axa.set_xlabel(r"$\alpha$: false-alarm rate on clean tokens")
axa.set_ylabel(r"$\beta$: flag rate on corrupted tokens")
axa.set_xticks([0, 0.05, 0.10, 0.15])
axa.set_yticks([0, 0.2, 0.4, 0.6])
for a0 in ALPHAS_PROTOCOL:
    axa.plot([a0, a0], [0, 2 * a0 - a0 ** 2], color=COL["ink"], lw=0.5, ls=":", zorder=2)
axa.plot([0.05], [nec_005], marker="o", ms=3.2, color=COL["ink"], zorder=6)
axa.annotate(r"$\beta>0.0975$ at $\alpha=0.05$", xy=(0.05, nec_005), xytext=(0.006, 0.235), fontsize=6.6, color=COL["ink"], va="center", bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.92),
             arrowprops=dict(arrowstyle="-", lw=0.5, color=COL["ink"], shrinkA=0, shrinkB=2))
# direct labels, spaced to the right of the axes with leader lines
ylab = [0.66, 0.54, 0.43, 0.32, 0.215]
for i, kappa in enumerate(KAPPAS):
    shade = blue(0.95 - 0.5 * i / (len(KAPPAS) - 1))
    ye = beta_star(A_MAX, kappa)
    axa.annotate(rf"$\kappa={kappa:g}$", xy=(A_MAX, ye), xytext=(A_MAX + 0.012, ylab[i]), xycoords="data", textcoords="data", fontsize=6.8,
                 color=COL["ink"], va="center", annotation_clip=False,
                 arrowprops=dict(arrowstyle="-", lw=0.5, color=COL["sub"], shrinkA=0, shrinkB=0, connectionstyle="arc3"))
axa.text(A_MAX + 0.012, 0.115, r"$\kappa\to\infty$:" + "\n" + r"$\beta=2\alpha-\alpha^{2}$" + "\n(necessary)", fontsize=6.6, color=COL["ink"],
         va="center", clip_on=False, linespacing=1.1)
axa.annotate("", xy=(A_MAX, nec[-1]), xytext=(A_MAX + 0.012, 0.115), annotation_clip=False,
             arrowprops=dict(arrowstyle="-", lw=0.5, color=COL["sub"], shrinkA=0, shrinkB=0))
axa.text(0.0035, 0.60, "gating raises\nthe SNR", fontsize=6.8, color=COL["flag"], weight="bold", va="top", linespacing=1.1)
axa.text(0.145, 0.015, "gating lowers the SNR\nfor every " + r"$\kappa$" + " below the dashed line", fontsize=6.4, color=COL["sub"], ha="right", va="bottom", linespacing=1.1)
axa.text(0.0035, 0.056, r"random gate $\beta=\alpha$", fontsize=6.4, color=COL["ctrl"], rotation=0, va="bottom", zorder=7,
         bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
axa.text(-0.20, 1.04, "(a)", transform=axa.transAxes, fontsize=8.5, weight="bold")
axa.text(0.0, 1.015, r"$\beta>\beta^{*}(\alpha;\kappa)=2\alpha-\alpha^{2}+\alpha(1-\alpha)/\kappa$", transform=axa.transAxes, fontsize=7.0, va="bottom")

# (b) how good must validation be, per alpha -----------------------------------------------------------------------------
kap = np.logspace(-2.2, 2.0, 600)
styles = {0.01: (COL["ink"], "-"), 0.05: (COL["ink"], (0, (5, 2))), 0.10: (COL["sub"], (0, (1, 1.6)))}
for a0 in ALPHAS_PROTOCOL:
    c, ls = styles[a0]
    bs = beta_star(a0, kap)
    ok = bs <= 1.0
    axb.plot(kap[ok], bs[ok], color=c, ls=ls, lw=1.3)
    axb.axhline(2 * a0 - a0 ** 2, color=c, ls=ls, lw=0.45, alpha=0.55)
    kmin = a0 / (1 - a0)
    axb.plot([kmin], [1.0], marker="o", ms=2.6, color=c, clip_on=False, zorder=5)
axb.set_xscale("log")
axb.set_xlim(0.008, 100)
axb.set_ylim(0, 1.0)
axb.set_xlabel(r"$\kappa=\rho\sigma_c^{2}\,/\,[(1-\rho)(\sigma^{2}+\mu^{2})]$")
axb.set_ylabel(r"smallest $\beta$ for which gating helps")
axb.set_xticks([0.01, 0.1, 1, 10, 100])
axb.set_xticklabels(["0.01", "0.1", "1", "10", "100"])
axb.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
axb.set_yticklabels(["0", "0.25", "0.5", "0.75", "1"])
for a0 in ALPHAS_PROTOCOL:
    c, _ = styles[a0]
    axb.text(4.0, beta_star(a0, 4.0) + 0.035, rf"$\alpha={a0:g}$", fontsize=6.8, color=c, ha="left", zorder=7)
axb.text(70, 0.93, "dots: smallest " + r"$\kappa$" + " at which\n" + r"$\beta\leq1$ can help", fontsize=6.2, color=COL["sub"], ha="right", va="top", linespacing=1.1)
axb.text(-0.30, 1.04, "(b)", transform=axb.transAxes, fontsize=8.5, weight="bold")
axb.text(0.0, 1.015, r"at the protocol's $\alpha$ levels; thin lines: $\beta=2\alpha-\alpha^{2}$", transform=axb.transAxes, fontsize=6.4, va="bottom")

S.save(fig, "F5_gating_frontier")
print(json.dumps(dict(necessary_beta_at_alpha_0_05=nec_005, kappa_min={str(a): a / (1 - a) for a in ALPHAS_PROTOCOL})))
