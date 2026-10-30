"""Fig. 2 (theory, column width): the Proposition 2 frontier in the (phi_0, phi_1) plane. MODEL FIGURE: no measured point, no run data.

Source of the formulas: research/paper2/method/THEORY-ADDENDUM-2026-10-29.md R1.4 and R1.8 (Eq. snrcorr, consequences (i)-(iii)).
With mu_c = 0, gamma_01 = 0 and G = (rho m - 1) gamma_1, chi = rho sigma_c^2 / ((1 - rho)(sigma^2 + mu^2)), x = phi_1 - phi_0, Eq. snrcorr reads
    G x^2 - x (1 + 2 G (1 - phi_0)) + phi_0 (1 - phi_0)(1 + 1/chi) < 0,
so the gate raises E S / sqrt(Var S) iff phi_1 exceeds
    b(phi_0; G, chi) = phi_0 + [1 + 2G(1 - phi_0) - sqrt((1 + 2G(1 - phi_0))^2 - 4 G phi_0 (1 - phi_0)(1 + 1/chi))] / (2G)   (G > 0),
    b(phi_0; 0, chi) = 2 phi_0 - phi_0^2 + phi_0 (1 - phi_0)/chi                                                          (G = 0, Eq. snr).
Before drawing, the boundary is checked against the signal-to-noise ratio computed directly from Eq. mean and Eq. varcorr on a grid.
chi = 1 is a display value (the curves for other chi have the same shape, shifted); the figure says so.
Output: paper2-tnnls/figures/fig2_theory.pdf (+ png preview). Run: python fig2_theory.py (CPU only).
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

import figstyle as S
from figstyle import C

S.apply()
CHI = 1.0
GS = [0.0, 1.0, 4.0, 16.0]


def boundary(phi0: np.ndarray, G: float, chi: float = CHI) -> np.ndarray:
    phi0 = np.asarray(phi0, float)
    if G == 0.0:
        return 2 * phi0 - phi0 ** 2 + phi0 * (1 - phi0) / chi
    B = 1 + 2 * G * (1 - phi0)
    disc = B ** 2 - 4 * G * phi0 * (1 - phi0) * (1 + 1 / chi)
    out = np.full_like(phi0, np.inf)
    ok = disc >= 0
    out[ok] = phi0[ok] + (B[ok] - np.sqrt(disc[ok])) / (2 * G)
    return out


def snr(phi0, phi1, rho, m, mu, sig, sigc, gam1, gate=True):
    """E S / sqrt(Var S) from Eq. mean and Eq. varcorr (mu_c = 0, gamma_0 = gamma_01 = 0)."""
    m0, m1 = (1 - rho) * m, rho * m
    k0, k1 = (1 - phi0, 1 - phi1) if gate else (1.0, 1.0)
    ES = m0 * k0 * mu
    V = m0 * (k0 * sig ** 2 + k0 * (1 - k0) * mu ** 2) + m1 * k1 * sigc ** 2
    V += m1 * (m1 - 1) * k1 ** 2 * gam1 * sigc ** 2
    return ES / np.sqrt(V)


# ---- check the closed-form boundary against the SNR computed from the variance formula --------------------------------------
rho, m, sig, mu = 0.5, 1024, 1.0, 0.1
sigc = np.sqrt(CHI * (1 - rho) * (sig ** 2 + mu ** 2) / rho)         # chi = rho sigc^2 / ((1-rho)(sig^2+mu^2)) = CHI
n_checked = mism = 0
for G in GS:
    gam1 = G / (rho * m - 1)
    s0 = snr(0, 0, rho, m, mu, sig, sigc, gam1, gate=False)
    for p0 in np.linspace(0.01, 0.49, 33):
        bnd = float(boundary(np.array([p0]), G)[0])
        for p1 in np.linspace(0.0, 1.0, 51):
            if np.isfinite(bnd) and abs(p1 - bnd) < 1e-4:
                continue
            helps = snr(p0, p1, rho, m, mu, sig, sigc, gam1) > s0
            pred = p1 > bnd
            mism += int(helps != pred)
            n_checked += 1
print(f"Fig. 2 boundary check against Eq. mean / Eq. varcorr: {n_checked} grid points, {mism} mismatches")
assert mism == 0

# ---- figure ------------------------------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(S.COL1, 3.15))
ax = fig.add_axes([0.135, 0.145, 0.62, 0.80])
p0 = np.linspace(0, 0.5, 1001)
ax.fill_between(p0, p0, 0, color=S.C["vlgrey"], lw=0, zorder=0)
ax.plot([0, 0.5], [0, 0.5], color=C["grey"], lw=1.0, ls=(0, (4, 2)), zorder=3)
styles = {0.0: ("-", 1.5, C["ink"]), 1.0: ((0, (5, 1.5)), 1.3, "#3C3C3C"), 4.0: ((0, (2.5, 1.2)), 1.3, "#6A6A6A"), 16.0: ((0, (1, 1.2)), 1.5, "#8C8C8C")}
ends = {}
for G in GS:
    b = boundary(p0, G)
    ok = np.isfinite(b) & (b <= 1.0)
    x, y = p0[ok], b[ok]
    ls, lw, col = styles[G]
    ax.fill_between(x, y, 1.0, color=C["sky"], alpha=0.16, lw=0, zorder=1)
    ax.plot(x, y, ls=ls, lw=lw, color=col, zorder=4)
    ends[G] = (x[-1], y[-1])
ax.set_xlim(0, 0.5)
ax.set_ylim(0, 1.0)
ax.set_xlabel(r"$\phi_0$: clean-token withholding probability")
ax.set_ylabel(r"$\phi_1$: corrupted-token withholding probability")
ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_xticklabels(["0", "0.1", "0.2", "0.3", "0.4", "0.5"])
ax.set_yticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1"])

# direct labels to the right of the axes, with leader lines
lab_y = {0.0: 0.93, 1.0: 0.77, 4.0: 0.62, 16.0: 0.47}
lab_txt = {0.0: r"$G=0$" + "\n(independent)", 1.0: r"$G=1$", 4.0: r"$G=4$", 16.0: r"$G=16$"}
for G in GS:
    xe, ye = ends[G]
    ax.annotate(lab_txt[G], xy=(xe, ye), xytext=(0.53, lab_y[G]), textcoords="data", fontsize=S.FS, va="center", ha="left",
                annotation_clip=False, linespacing=1.0,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=C["grey"], shrinkA=0, shrinkB=1.5))
ax.annotate(r"$\phi_1=\phi_0$" + "\n(random gate)", xy=(0.5, 0.5), xytext=(0.53, 0.28), fontsize=S.FS, va="center", ha="left", annotation_clip=False,
            linespacing=1.0, color=C["grey"], arrowprops=dict(arrowstyle="-", lw=0.5, color=C["grey"], shrinkA=0, shrinkB=1.5))
ax.text(0.205, 0.93, "ratio raised\n(above each curve)", fontsize=S.FS, color=C["blue"], ha="center", va="center", linespacing=1.05)
ax.text(0.30, 0.085, r"$\phi_1\leq\phi_0$: ratio lowered" + "\n" + r"for every gate if $\gamma_{01}\geq 0$", fontsize=S.FS, color=C["grey"],
        ha="center", va="center", linespacing=1.05)
S.save(fig, "fig2_theory")
print("ends", {k: (round(float(v[0]), 4), round(float(v[1]), 4)) for k, v in ends.items()})
