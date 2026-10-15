"""Figure 1: PRISMA 2020 flow diagram, every number read from files.

Reads  research/review/corpus/search-log.jsonl, corpus/awesome-dlms@194aa6bd.jsonl,
       screening/dedup-report.json, screening/records.jsonl, screening/screener-A|B/batch-*.jsonl,
       screening/human-sample.csv, census/census-order.csv, census/census-random-final.jsonl (the last
       through censuscounts.py, which reproduces analysis/census/summary-random.log and asserts it).
Writes paper/review/figures/fig01-prisma.pdf, preview/fig01-prisma.png and fig01-prisma.log (numbers read).
Stages that have not been run are drawn dashed and labelled "not yet run"; the only count on a dashed box
is the size of the pool not yet sampled, which is pool minus sample (both read from files).

    python paper/review/scripts/fig01_prisma.py
"""
import csv
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

import censuscounts
from figstyle import C, FIGDIR, REV, TEXTWIDTH_IN, save, setup

setup()

# ------------------------------------------------------------------ numbers from files
search = {}
for line in open(REV / "corpus" / "search-log.jsonl", encoding="utf8"):
    d = json.loads(line)
    assert d["hits_reported"] == d["records_retrieved"]
    search[d["string"]] = d["records_retrieved"]
awesome = sum(1 for l in open(REV / "corpus" / "awesome-dlms@194aa6bd.jsonl", encoding="utf8") if l.strip())
identified = awesome + search["S1"] + search["S2"]
dedup = json.load(open(REV / "screening" / "dedup-report.json", encoding="utf8"))
recs = [json.loads(l) for l in open(REV / "screening" / "records.jsonl", encoding="utf8")]
assert len(recs) == dedup["records"]
assert identified - dedup["records"] == dedup["duplicates_merged"], "identified - records != duplicates merged"


def decisions(folder):
    out = {}
    for p in sorted(glob.glob(str(REV / "screening" / folder / "batch-*.jsonl"))):
        for l in open(p, encoding="utf8"):
            d = json.loads(l)
            out[d["sid"]] = d["decision"]
    return out


A, B = decisions("screener-A"), decisions("screener-B")
assert set(A) == set(B) == {r["sid"] for r in recs}
pa = {s: A[s] != "exclude" for s in A}
pb = {s: B[s] != "exclude" for s in B}
both_ex = sum(1 for s in A if not pa[s] and not pb[s])
a_only = sum(1 for s in A if pa[s] and not pb[s])
b_only = sum(1 for s in A if pb[s] and not pa[s])
both_pass = sum(1 for s in A if pa[s] and pb[s])
split = a_only + b_only
assert both_ex + split + both_pass == len(recs)
with_id = {r["sid"] for r in recs if r.get("arxiv")}
pool_ids = {s for s in A if pa[s] and pb[s] and s in with_id}
order = list(csv.DictReader(open(REV / "census" / "census-order.csv", encoding="utf-8-sig")))
assert {o["sid"] for o in order} == pool_ids, "census-order.csv is not the both-pass records with an arXiv ID"
pool = len(pool_ids)
no_id = both_pass - pool

fin, sen, extra = censuscounts.load()          # asserted against analysis/census/summary-random.log
assert fin["ranks"] == 176
n_remaining = pool - fin["ranks"]
no_text_ranks = sorted(int(r) for r, d in extra["rows"].items() if d.get("exclusion_code") == "NO_TEXT")
assert len(no_text_ranks) == fin["no_text"]
judged = fin["ranks"] - fin["no_text"]
excl = fin["excluded"]
n_excl = sum(excl.values())
assert judged - n_excl == fin["eligible"]
assert fin["n_v"] + fin["n_noF2"] == fin["eligible"]
assert fin["n_m"] + fin["n_ql"] == fin["n_v"]
human_rows = sum(1 for _ in csv.DictReader(open(REV / "screening" / "human-sample.csv", encoding="utf-8-sig")))

n = dict(awesome=awesome, S1=search["S1"], S2=search["S2"], identified=identified,
         duplicates=dedup["duplicates_merged"], screened=len(recs), both_exclude=both_ex, split=split,
         a_pass_b_excl=a_only, a_excl_b_pass=b_only, both_pass=both_pass, no_arxiv_id=no_id, pool=pool,
         sampled=fin["ranks"], not_yet_sampled=n_remaining, no_full_text=fin["no_text"],
         no_text_ranks=no_text_ranks, judged=judged, excluded_full_text=n_excl, excluded_codes=excl,
         eligible=fin["eligible"], value_rule_coded=fin["n_v"], with_metric=fin["n_m"],
         samples_only=fin["n_ql"], no_F2_code=fin["n_noF2"], human_sample_rows=human_rows)
FIGDIR.mkdir(exist_ok=True)
(FIGDIR / "fig01-prisma.log").write_text("\n".join(f"{k} = {v}" for k, v in n.items()) + "\n", encoding="utf8")

# ------------------------------------------------------------------ drawing (units are points of the final figure)
W = TEXTWIDTH_IN * 72
LH, FS = 8.6, 7.0
XM, XR = 150.0, 317.0                            # main and right column centres
WM, WR = 150.0, 150.0
STRIP = 16.0
BOLD, NORM = "bold", "normal"


def hbox(lines):
    return len(lines) * LH + 7


def draw_box(ax, xc, yc, w, lines, kind="solid"):
    h = hbox(lines)
    kw = dict(boxstyle="square,pad=0", linewidth=0.7, edgecolor=C["black"], facecolor="white", zorder=2)
    if kind == "excl":
        kw["facecolor"] = C["lightgrey"]
    if kind == "dashed":
        kw.update(linestyle=(0, (3, 2)), edgecolor="#404040")
    ax.add_patch(FancyBboxPatch((xc - w / 2, yc - h / 2), w, h, **kw))
    y0 = yc - (len(lines) - 1) * LH / 2
    for i, (txt, wt) in enumerate(lines):
        dashed = kind == "dashed"
        ax.text(xc, y0 + i * LH, txt, ha="center", va="center", fontsize=FS, fontweight=wt,
                color="#404040" if dashed else C["black"],
                zorder=3)


rows_main = [
    [("Records identified", BOLD), (f"n = {n['identified']}", NORM)],
    [("Records screened", BOLD), ("title and abstract, two screeners", NORM), (f"n = {n['screened']}", NORM)],
    [("Passed by both screeners", BOLD), ("include or unclear", NORM), (f"n = {n['both_pass']}", NORM)],
    [("Census pool", BOLD), ("passed by both, with an arXiv ID", NORM), (f"n = {n['pool']}", NORM),
     (f"({n['no_arxiv_id']} passed without an arXiv ID)", NORM)],
    [("Sampled in random order", BOLD), (f"ranks 1 to {n['sampled']}", NORM), (f"n = {n['sampled']}", NORM)],
    [("Full text available, eligibility judged", BOLD), (f"n = {n['judged']}", NORM)],
    [("Eligible", BOLD), (f"n = {n['eligible']}", NORM)],
    [("Value-rule code assigned", BOLD), (f"n = {n['value_rule_coded']}", NORM),
     (f"{n['with_metric']} with a generated-sample metric", NORM), (f"{n['samples_only']} with samples only", NORM)],
]
# right-hand boxes per gap g (gap g lies between main row g-1 and main row g, 0-based rows)
G = {
    1: [("excl", [("Duplicates merged", BOLD), (f"n = {n['duplicates']}", NORM), ("arXiv ID, then normalised title", NORM)], "main")],
    2: [("excl", [("Excluded by both screeners", BOLD), (f"n = {n['both_exclude']}", NORM)], "main"),
        ("excl", [("Split decision, held out", BOLD), (f"n = {n['split']}", NORM),
                  (f"A passes, B excludes: {n['a_pass_b_excl']}; reverse: {n['a_excl_b_pass']}", NORM)], "main")],
    3: [("dashed", [("Human validation", BOLD), (f"random {n['human_sample_rows']} and the {n['split']} splits", NORM),
                    ("not yet run", BOLD)], "none")],
    4: [("dashed", [("Rest of the pool", BOLD), (f"n = {n['not_yet_sampled']}", NORM), ("full-text screening not yet run", BOLD)], "main")],
    5: [("excl", [("No full text", BOLD), (f"n = {n['no_full_text']}", NORM),
                  ("ranks " + ", ".join(map(str, n["no_text_ranks"])), NORM)], "main")],
    6: [("excl", [("Excluded at full text", BOLD), (f"n = {n['excluded_full_text']}", NORM),
                  (", ".join(f"{k}: {v}" for k, v in n["excluded_codes"].items()), NORM)], "main")],
    7: [("excl", [("No value-rule code", BOLD), (f"n = {n['no_F2_code']}", NORM), ("no generated-sample metric", NORM)], "main")],
}
src = [
    ([("Awesome-DLMs list", BOLD), (f"n = {n['awesome']}", NORM)], "solid"),
    ([("arXiv string S1", BOLD), (f"n = {n['S1']}", NORM)], "solid"),
    ([("arXiv string S2", BOLD), (f"n = {n['S2']}", NORM)], "solid"),
    ([("Other databases", BOLD), ("and snowballing", NORM), ("not yet run", BOLD)], "dashed"),
]
SX = [66, 158, 250, 342]

HH = [hbox(r) for r in rows_main]
src_h = max(hbox(s[0]) for s in src)
y_src = 6 + src_h / 2
y_bus = y_src + src_h / 2 + 9
stack_h = {g: sum(hbox(b[1]) for b in bl) + 6 * (len(bl) - 1) for g, bl in G.items()}
gap_of = {i: 19.0 for i in range(1, len(rows_main))}
for _ in range(50):                               # push rows apart until neighbouring right stacks clear each other
    ys = [y_bus + 22 + HH[0] / 2]
    for i in range(1, len(rows_main)):
        ys.append(ys[-1] + HH[i - 1] / 2 + gap_of[i] + HH[i] / 2)
    mid = {g: ys[g - 1] + HH[g - 1] / 2 + gap_of[g] / 2 for g in G}
    ok = True
    gs = sorted(G)
    for a, b in zip(gs, gs[1:]):
        need = (stack_h[a] + stack_h[b]) / 2 + 5
        if mid[b] - mid[a] < need:
            gap_of[b] += need - (mid[b] - mid[a]) + 0.1
            ok = False
    if ok:
        break
assert ok
H = ys[-1] + HH[-1] / 2 + 8
fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, H / 72))
fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")

ARR = dict(arrowstyle="-|>", mutation_scale=6, lw=0.7, color=C["black"], shrinkA=0, shrinkB=0)
ARR_D = dict(arrowstyle="-|>", mutation_scale=6, lw=0.7, color="#404040", linestyle=(0, (3, 2)), shrinkA=0, shrinkB=0)


def arrow(p, q, dashed=False):
    ax.annotate("", xy=q, xytext=p, arrowprops=ARR_D if dashed else ARR, zorder=1)


for xc, (ln, kind) in zip(SX, src):
    draw_box(ax, xc, y_src, 84, ln, kind)
for xc in SX[:3]:
    ax.plot([xc, xc], [y_src + src_h / 2, y_bus], color=C["black"], lw=0.7, zorder=1)
ax.plot([SX[0], SX[2]], [y_bus, y_bus], color=C["black"], lw=0.7, zorder=1)
ax.plot([SX[3], SX[3]], [y_src + src_h / 2, y_bus], color="#404040", lw=0.7, ls=(0, (3, 2)), zorder=1)
ax.plot([SX[2], SX[3]], [y_bus, y_bus], color="#404040", lw=0.7, ls=(0, (3, 2)), zorder=1)

for i, ln in enumerate(rows_main):
    draw_box(ax, XM, ys[i], WM, ln, "solid")
arrow((XM, y_bus), (XM, ys[0] - HH[0] / 2))
for i in range(1, len(rows_main)):
    arrow((XM, ys[i - 1] + HH[i - 1] / 2), (XM, ys[i] - HH[i] / 2))

BUS_X = XM + WM / 2 + 12
centres_of = {}
for g, bl in G.items():
    ym = mid[g]
    heights = [hbox(b[1]) for b in bl]
    top = ym - stack_h[g] / 2
    centres = []
    for h in heights:
        centres.append(top + h / 2)
        top += h + 6
    centres_of[g] = (centres, heights)
    for (kind, ln, how), yc in zip(bl, centres):
        draw_box(ax, XR, yc, WR, ln, kind)
        if how == "main":
            if len(bl) == 1:
                arrow((XM, yc), (XR - WR / 2, yc), dashed=(kind == "dashed"))
            else:
                arrow((BUS_X, yc), (XR - WR / 2, yc))
    if len(bl) > 1:
        ax.plot([XM, BUS_X], [ym, ym], color=C["black"], lw=0.7, zorder=1)
        ax.plot([BUS_X, BUS_X], [centres[0], centres[-1]], color=C["black"], lw=0.7, zorder=1)

# split decision -> human validation (dashed, within the right column)
c2, h2 = centres_of[2]
c3, h3 = centres_of[3]
arrow((XR, c2[1] + h2[1] / 2), (XR, c3[0] - h3[0] / 2), dashed=True)


def band(r0, r1, label, colour):
    top = 0 if r0 == 0 else ys[r0] - HH[r0] / 2 - gap_of[r0] / 2
    bot = H if r1 == len(rows_main) - 1 else ys[r1] + HH[r1] / 2 + gap_of[r1 + 1] / 2
    ax.add_patch(Rectangle((0, top + 1), STRIP - 3, bot - top - 2, facecolor=colour, edgecolor="none", zorder=0, alpha=0.45))
    ax.text((STRIP - 3) / 2, (top + bot) / 2, label, rotation=90, ha="center", va="center", fontsize=FS, fontweight=BOLD)


band(0, 0, "Identification", C["sky"])
band(1, 3, "Screening", C["green"])
band(4, 7, "Full-text check, random sample", C["orange"])
save(fig, "fig01-prisma")
