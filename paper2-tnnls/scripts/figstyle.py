"""Shared style and loaders for the Paper 2 (IEEE TNNLS) figures and tables.

One palette (Okabe-Ito, colour-blind safe), STIX General (Times-like, ships with matplotlib, so the output does not depend on installed
fonts), TrueType fonts embedded (pdf.fonttype 42), sizes set at final print width: IEEE column 3.5 in, text width 7.16 in.
Study identity: Study 1 (GATE-M) is drawn in blue with circles; Study 2 (learned reliability-aware fusion) in bluish green with diamonds.
No figure or table may hold both (SPEC rule 3); this module only provides colours.
Nothing here reads a number from a run except through `jload`, which reads committed files under runs/.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent                 # paper2-tnnls
REPO = ROOT.parent                 # worktree root
RUNS = REPO / "runs"
FIGDIR = ROOT / "figures"
TABDIR = ROOT / "tables"
FIGDIR.mkdir(exist_ok=True)
TABDIR.mkdir(exist_ok=True)

COL1, COL2 = 3.5, 7.16             # inches, IEEE Transactions

C = dict(
    blue="#0072B2", green="#009E73", verm="#D55E00", orange="#E69F00", sky="#56B4E9", purple="#CC79A7",
    ink="#1A1A1A", grey="#6E6E6E", lgrey="#BDBDBD", vlgrey="#EFEFEF",
)
MINUS = "−"
FS = 8.0                           # text size at final width (pt)


def apply() -> None:
    mpl.rcParams.update({
        "font.family": "serif", "font.serif": ["STIXGeneral"], "mathtext.fontset": "stix",
        "pdf.fonttype": 42, "ps.fonttype": 42, "pdf.compression": 6,
        "font.size": FS, "axes.labelsize": FS, "axes.titlesize": FS, "xtick.labelsize": FS, "ytick.labelsize": FS,
        "legend.fontsize": FS, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "xtick.major.pad": 2.0, "ytick.major.pad": 2.0,
        "lines.linewidth": 1.0, "axes.spines.top": False, "axes.spines.right": False,
        "text.color": C["ink"], "axes.edgecolor": C["ink"], "axes.labelcolor": C["ink"],
        "xtick.color": C["ink"], "ytick.color": C["ink"], "savefig.dpi": 300, "figure.dpi": 150,
        "axes.labelpad": 2.0,
    })


def jload(rel: str):
    """Read a committed run file, path relative to runs/."""
    with open(RUNS / rel, encoding="utf-8") as fh:
        return json.load(fh)


def sha256(p) -> str:
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def fmt(x: float, nd: int = 3, plus: bool = False) -> str:
    s = f"{x:+.{nd}f}" if plus else f"{x:.{nd}f}"
    return s.replace("-", MINUS)


def save(fig, name: str) -> None:
    """Vector PDF into paper2-tnnls/figures/ plus a 300 dpi PNG preview (inspection only; not for the manuscript)."""
    fig.savefig(FIGDIR / f"{name}.pdf", format="pdf")
    fig.savefig(FIGDIR / f"{name}.png", format="png", dpi=300)
    plt.close(fig)


def panel_letter(ax, s: str, dx: float = -0.02, dy: float = 1.02) -> None:
    ax.text(dx, dy, s, transform=ax.transAxes, fontsize=FS + 1, fontweight="bold", va="bottom", ha="right")
