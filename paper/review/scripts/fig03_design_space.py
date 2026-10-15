"""Figure 3: the 47 models placed on the design space (a design matrix).

Rows are the models, grouped by C1 channel; the marker beside each name is its family, a hollow marker
and a tinted row mean the notation fits the model only partly. Columns are the cells of the choices
C4 position rule, C4 value rule and C5 revision.

Reads  research/review/coverage/design-space-v1.csv   (id, name, family, fits (yes/partly/no), the value-rule
       classes and headline column) and paper/review/tables/design-space-condensed.tex, the table generated
       by scripts/design_space_tables.py, for the writer's condensed C1, position, value and revision codes,
       so that this figure and Table 4 cannot disagree. Those codes are the writer's condensation of the
       free-text cells (see the todo in section 4 of the manuscript).
Asserts the family and fit counts against paper/review/tables/design-space-counts.log.
Writes paper/review/figures/fig03-design-space.pdf (+ preview PNG) and fig03-design-space.log.

    python paper/review/scripts/fig03_design_space.py
"""
import ast
import csv
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from figstyle import C, FIGDIR, REV, ROOT, TEXTWIDTH_IN, save, setup

setup()
CSV = REV / "coverage" / "design-space-v1.csv"
TEX = ROOT / "paper" / "review" / "tables" / "design-space-condensed.tex"
COUNTS = ROOT / "paper" / "review" / "tables" / "design-space-counts.log"
K_FIT = "fits (yes/partly/no)"

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
codes = {}
for ln in open(TEX, encoding="utf-8"):
    p = ln.rstrip("\n").rstrip("\\").split(" & ")
    if len(p) >= 8 and re.match(r"M\d\d$", p[0]):
        codes[p[0]] = dict(c1=p[2].strip(), pos=p[3].strip(), val=p[4].strip(), rev=p[5].strip(), fit=p[7].strip().replace(r"\textbf{partly}", "partly").replace("\\\\", "").strip())
assert set(codes) == {r["id"] for r in rows} and len(rows) == 47
for r in rows:
    assert codes[r["id"]]["fit"].strip(" \\") == r[K_FIT], r["id"]


def family(f):
    """Same grouping as grp() in design_space_tables.py (counts asserted against its log below)."""
    if "unified" in f or "hybrid AR+diffusion" in f:
        return "unified multimodal and hybrids"
    if "Gaussian" in f:
        return "Gaussian, embedding or simplex"
    if f.startswith("absorbing"):
        return "absorbing"
    if f.startswith("sampler-only"):
        return "sampler-only"
    if f.startswith("general discrete"):
        return "general discrete"
    if f.startswith("uniform"):
        return "uniform"
    if f.startswith("AR-adapted"):
        return "adapted from autoregressive"
    return "other (flow, block, distillation)"


def channel(code):
    if code in ("Er", "Er/Un"):
        return "Erasure"
    if code in ("Un", "Un+aux"):
        return "Uniform"
    if code in ("Gs", "Sx"):
        return "Gaussian on embeddings or logits"
    if code == "Q":
        return "General Markov or CTMC"
    if code == "Fl":
        return "Flow"
    return "Mixed or hybrid channel"


def short(name):
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", name)
    if not m:
        return name
    base, par = m.groups()
    return par if (len(base) > 20 and " " not in par) else base


fam_of = {r["id"]: family(r["family"]) for r in rows}
# assert the family and fit counts against the log of the table script
log = COUNTS.read_text(encoding="utf-8")
fit_c = Counter(r[K_FIT] for r in rows)
assert f"fits {dict(fit_c)}" in log, "fit counts differ from design-space-counts.log"
grp_log = ast.literal_eval(re.search(r"^groups (\{.*\})$", log, re.M).group(1))
mine = Counter(fam_of.values())
assert mine["unified multimodal and hybrids"] == grp_log["unified multimodal (incl. hybrids)"]
assert mine["Gaussian, embedding or simplex"] == grp_log["Gaussian/embedding/logit simplex"]
assert mine["absorbing"] == grp_log["absorbing"] and mine["sampler-only"] == grp_log["sampler-only"]
assert mine["general discrete"] == grp_log["general discrete"] and mine["uniform"] == grp_log["uniform"]
assert mine["adapted from autoregressive"] == grp_log["AR-adapted absorbing (incl. edit)"]
assert mine["other (flow, block, distillation)"] == (grp_log["flow (probability path)"] + grp_log["block (semi-AR)"]
                                                     + grp_log["distillation (joint over positions)"])

FAMS = OrderedDict([  # family -> (colour, marker)
    ("unified multimodal and hybrids", (C["vermilion"], "o")),
    ("Gaussian, embedding or simplex", (C["blue"], "s")),
    ("absorbing", (C["black"], "^")),
    ("sampler-only", (C["green"], "D")),
    ("general discrete", (C["orange"], "v")),
    ("uniform", (C["purple"], "P")),
    ("adapted from autoregressive", (C["sky"], "X")),
    ("other (flow, block, distillation)", (C["grey"], "*")),
])
assert set(FAMS) == set(fam_of.values())

POS = ["rnd", "cnf", "ent", "blk", "all", "ar", "ns"]
VAL = ["A", "T", "P", "S", "G", "M", "plain", "lik.", "ns"]
REVC = ["none", "impl", "corr", "remask", "edit", "out", "ns"]


def toks(s, split):
    s = s.replace(r"$^\dagger$", "").replace("(M)", ", M")
    return [t.strip() for t in re.split(split, s) if t.strip()]


cells = {}
for r in rows:
    c = codes[r["id"]]
    t = (toks(c["pos"], r"[,/]"), toks(c["val"], r"[,/\s]+"), toks(c["rev"], r"[,/]"))
    for lst, allowed in zip(t, (POS, VAL, REVC)):
        assert all(x in allowed for x in lst), (r["id"], lst)
    cells[r["id"]] = t

# group order: by channel (largest first), inside by family then id
by_ch = OrderedDict()
for r in rows:
    by_ch.setdefault(channel(codes[r["id"]]["c1"]), []).append(r)
order = sorted(by_ch.items(), key=lambda kv: -len(kv[1]))
FORD = list(FAMS)
for _, lst in order:
    lst.sort(key=lambda r: (FORD.index(fam_of[r["id"]]), r["id"]))

# ------------------------------------------------------------------ drawing (points)
W = TEXTWIDTH_IN * 72
PITCH = 7.9
FS = 7.0
X_MARK, X_NAME, X_FIT, X0 = 8.0, 15.0, 123.0, 138.0
ncol = len(POS) + len(VAL) + len(REVC)
CP = (W - X0 - 3) / ncol
HEAD = 38.0
n_rows = len(rows) + len(order)
LEG = 30.0
H = HEAD + n_rows * PITCH + 6 + LEG
fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, H / 72))
fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")

col_x = {}
x = X0 + CP / 2
for grp_name, lab in (("pos", POS), ("val", VAL), ("rev", REVC)):
    for l in lab:
        col_x[(grp_name, l)] = x
        x += CP
# column headers
for grp_name, lab, title in (("pos", POS, "Position rule (C4)"), ("val", VAL, "Value rule (C4)"), ("rev", REVC, "Revision (C5)")):
    xs = [col_x[(grp_name, l)] for l in lab]
    ax.text((xs[0] + xs[-1]) / 2, 5, title, ha="center", va="center", fontsize=FS, fontweight="bold")
    ax.plot([xs[0] - CP / 2 + 1, xs[-1] + CP / 2 - 1], [11, 11], color=C["black"], lw=0.6)
    for l in lab:
        ax.text(col_x[(grp_name, l)], HEAD - 3, l, rotation=90, ha="center", va="bottom", fontsize=FS)
ax.text(X_FIT, 5, "Fit", ha="center", va="center", fontsize=FS, fontweight="bold")
ax.text(X_NAME, 5, "Model", ha="left", va="center", fontsize=FS, fontweight="bold")
ax.plot([X_NAME - 1, X_FIT + 8], [11, 11], color=C["black"], lw=0.6)

y = HEAD + PITCH / 2
log_lines = []
for ch, lst in order:
    ax.add_patch(Rectangle((0, y - PITCH / 2), W, PITCH, facecolor=C["lightgrey"], edgecolor="none", zorder=0))
    ax.text(3, y, f"{ch}  (n = {len(lst)})", ha="left", va="center", fontsize=FS, fontweight="bold")
    log_lines.append(f"{ch}: {len(lst)} models")
    y += PITCH
    for r in lst:
        mid = r["id"]
        partly = r[K_FIT] == "partly"
        if partly:
            ax.add_patch(Rectangle((0, y - PITCH / 2), W, PITCH, facecolor="#F8DCCB", edgecolor="none", zorder=0))
        colr, mk = FAMS[fam_of[mid]]
        ax.plot([X_MARK], [y], marker=mk, color=colr, markersize=3.6 if mk != "*" else 5.0, mec=colr, lw=0, zorder=3)
        ax.text(X_NAME, y, f"{mid} {short(r['name'])}", ha="left", va="center", fontsize=FS)
        ax.plot([X_FIT], [y], marker="o", markersize=3.6, mfc="white" if partly else C["black"], mec=C["black"], mew=0.9, lw=0, zorder=3)
        for grp_name, lst_ in zip(("pos", "val", "rev"), cells[mid]):
            for l in lst_:
                nsq = l == "ns"
                ax.plot([col_x[(grp_name, l)]], [y], marker="o", markersize=3.6, mfc="white" if nsq else "#303030",
                        mec="#808080" if nsq else "#303030", mew=0.8, lw=0, zorder=3)
        y += PITCH
    ax.plot([0, W], [y - PITCH / 2, y - PITCH / 2], color=C["grey"], lw=0.3, zorder=1)
# faint column guides between groups
for xg in (X0 + len(POS) * CP, X0 + (len(POS) + len(VAL)) * CP):
    ax.plot([xg, xg], [HEAD - 2, y - PITCH / 2], color=C["grey"], lw=0.4, ls=(0, (2, 2)), zorder=1)

# legend
yl = y + 8
xl = 4
ax.text(xl, yl, "Family:", fontsize=FS, fontweight="bold", va="center")
items = list(FAMS.items())
LEG_COLS = [[0, 7, 4], [1, 2, 3], [5, 6]]          # indices into FAMS, three legend columns of up to three rows
LEG_X = [34, 168, 284]
for ci, idxs in enumerate(LEG_COLS):
    for ri, i in enumerate(idxs):
        fname, (colr, mk) = items[i]
        xx, yy = LEG_X[ci], yl + ri * 9.5
        ax.plot([xx], [yy], marker=mk, color=colr, markersize=3.6 if mk != "*" else 5.0, lw=0, mec=colr)
        ax.text(xx + 5, yy, fname, fontsize=FS, va="center")
ax.text(xl, yl + 29.0, "Fit:", fontsize=FS, fontweight="bold", va="center")
ax.plot([30], [yl + 29.0], marker="o", markersize=3.6, mfc=C["black"], mec=C["black"], lw=0)
ax.text(35, yl + 29.0, "fits", fontsize=FS, va="center")
ax.plot([62], [yl + 29.0], marker="o", markersize=3.6, mfc="white", mec=C["black"], mew=0.9, lw=0)
ax.text(67, yl + 29.0, "fits partly (tinted row)", fontsize=FS, va="center")
ax.plot([178], [yl + 29.0], marker="o", markersize=3.6, mfc="white", mec="#808080", mew=0.8, lw=0)
ax.text(183, yl + 29.0, "not stated in the parts read (ns)", fontsize=FS, va="center")
ax.set_ylim(yl + 37, 0)
fig.set_size_inches(TEXTWIDTH_IN, (yl + 37) / 72)
ax.set_ylim(yl + 37, 0)

(FIGDIR / "fig03-design-space.log").write_text(
    "\n".join(log_lines + [f"fits {dict(fit_c)}", f"families {dict(mine)}", f"rows {len(rows)}"]) + "\n", encoding="utf8")
save(fig, "fig03-design-space")
