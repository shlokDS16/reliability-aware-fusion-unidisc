"""Measure empty space in each column of the two-column PDF: the blank run at the bottom of each column and the largest blank run
inside it, in text lines. Adapted from paper/review/scripts/check_column_gaps.py (review project, 2026-10-28, written after the
author found columns with empty space) for IEEEtran journal geometry (10 pt text, 12 pt baseline skip, US Letter).

Run from paper2-tnnls:
    python -E scripts/check_column_gaps.py [main.pdf] [--max-bottom 4] [--max-inner 6]
Needs pdftoppm (poppler; ships with MiKTeX) and Pillow. The last page is exempt from the bottom check (end of the document;
IEEEtran does not balance the last page's columns). Exit status 1 if any page is flagged.
Note: a float (figure, table, algorithm) that moves to the next page leaves a bottom gap on the page it left; fix by moving the
float in the source, not by changing this threshold.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("pdf", nargs="?", default="main.pdf")
ap.add_argument("--dpi", type=int, default=50)
ap.add_argument("--line-pt", type=float, default=12.0, help="baseline skip of body text in pt (IEEEtran 10 pt: 12)")
ap.add_argument("--max-bottom", type=float, default=4.0, help="flag a bottom blank run longer than this many lines")
ap.add_argument("--max-inner", type=float, default=6.0, help="flag an inner blank run longer than this many lines")
a = ap.parse_args()

pdf = Path(a.pdf).resolve()
tmp = Path(tempfile.mkdtemp())
subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", str(pdf), str(tmp / "p")], check=True)
pages = sorted(tmp.glob("p-*.png"), key=lambda f: int(f.stem.split("-")[1]))
LINE = a.line_pt / 72 * a.dpi
bad = 0
for f in pages:
    im = Image.open(f).convert("L")
    w, h = im.size
    px = im.load()
    top, bot = int(h * 0.075), int(h * 0.93)          # inside the running head and the page-bottom margin
    n = int(f.stem.split("-")[1])
    out = []
    for name, (x0, x1) in {"L": (0.065, 0.49), "R": (0.51, 0.935)}.items():
        xs = range(int(w * x0), int(w * x1), 2)
        rows = [any(px[x, y] < 190 for x in xs) for y in range(top, bot)]
        last = max((i for i, r in enumerate(rows) if r), default=-1)
        bottom = (len(rows) - 1 - last) / LINE
        gap = run = 0
        for r in rows[: last + 1]:
            run = 0 if r else run + 1
            gap = max(gap, run)
        out.append((name, bottom, gap / LINE))
    is_last = n == len(pages)
    flags = [f"{nm}: bottom {b:.0f} lines, inner gap {g:.0f}"
             for nm, b, g in out if (b > a.max_bottom and not is_last) or g > a.max_inner]
    if flags:
        bad += 1
        print(f"p{n}: " + "; ".join(flags))
print(f"pages with an empty column region: {bad} of {len(pages)}")
sys.exit(1 if bad else 0)
