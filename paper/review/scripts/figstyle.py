"""Shared helpers for the Paper 1 figure scripts: fonts, palette, paths, saving.

One palette for the whole paper (Okabe-Ito, colour-blind safe). Colour never carries meaning alone:
every encoded class also has a marker shape, a label or a line style.
"""
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

ROOT = Path(__file__).resolve().parents[3]          # repository root
REV = ROOT / "research" / "review"
FIGDIR = ROOT / "paper" / "review" / "figures"
PREVIEW = FIGDIR / "preview"
STYLE = Path(__file__).with_name("dlm.mplstyle")

TEXTWIDTH_IN = 395.8225 / 72.27                      # \textwidth of acmsmall (main.log)

# Okabe and Ito (2008)
C = dict(black="#000000", orange="#E69F00", sky="#56B4E9", green="#009E73", yellow="#F0E442",
         blue="#0072B2", vermilion="#D55E00", purple="#CC79A7", grey="#7F7F7F", lightgrey="#E6E6E6")

def setup():
    """Load the project style. Arial (a TrueType sans, close to the Helvetica-like ACM sans) with DejaVu Sans as
    fallback; Linux Biolinum was tried and dropped because matplotlib cannot rasterise or reliably embed its
    CFF OpenType files on this machine."""
    plt.style.use(str(STYLE))


def save(fig, stem):
    """Vector PDF into figures/, 300 dpi PNG preview into figures/preview/."""
    FIGDIR.mkdir(exist_ok=True)
    PREVIEW.mkdir(exist_ok=True)
    fig.savefig(FIGDIR / f"{stem}.pdf")
    fig.savefig(PREVIEW / f"{stem}.png", dpi=300)
    plt.close(fig)
    print(f"wrote {FIGDIR / (stem + '.pdf')} and preview/{stem}.png")
