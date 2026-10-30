"""Study 2 exploratory ablation (column width): forest plot of the paired accuracy difference, variant minus frozen LRF, with its 95% paired
percentile-bootstrap interval, on the L1 noise cell (Gaussian noise sigma 0.1, fresh fold), for every fitted/unlearned variant (block 3a) and
every knockout with an interval (block 3b), in the plan's order (research/paper2/tnnls/ABLATION-PLAN-2026-10-30.md section 3; KO-ALL is an
exact-equality control with no interval and is not drawn). Exploratory; added after the primary, family H and Study 2 results; intervals only,
no test. No ranking, no better/worse wording (plan section 8). Row names describe each variant by formula (as in sections/study2.tex V-G).

Reads: runs/P2-LRF-ABL-SCORE/ablation_analysis.json keys rows[*].{id,block,cells.L1_noise0.1.{acc,vs_LRF.{d,ci95,b,c}}}, n_per_cell,
       references_accuracy.LRF.L1_noise0.1, ko_all_control, controls_ok, meta.{label,sign,interval,n_boot}.
Writes runs/P2-PAPER-FIGS/fig_ablation.json. Output paper2-tnnls/figures/fig_ablation.pdf (+ png preview).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

import figstyle as S
from figstyle import C, MINUS

S.apply()
AB = S.jload("P2-LRF-ABL-SCORE/ablation_analysis.json")
CELL = "L1_noise0.1"
assert AB["controls_ok"] is True and AB["ko_all_control"]["decisions_identical"] is True
ORDER_3A = ["A-LIN", "A-S-BD", "A-S-s3", "A-S-tbv", "A-S-ltex", "A-S-nbr", "A-S-pos", "A-SF", "A-MIL", "A-UNL"]
ORDER_3B = ["KO-S-BD", "KO-S-s3", "KO-S-tbv", "KO-S-ltex", "KO-S-nbr", "KO-S-pos", "KO-F-token", "KO-F-position", "KO-F-neighbourhood",
            "KO-F-rank", "KO-F-item"]
NAME = {"A-LIN": "linear logit, 35 features", "A-S-BD": r"from $B$ and $D$ only", "A-S-s3": r"uncertainty of $B$ pass only",
        "A-S-tbv": "one-pass score only", "A-S-ltex": "patch texture only", "A-S-nbr": "neighbour distance only",
        "A-S-pos": "grid position only", "A-SF": "single feature (selected)", "A-MIL": "attention pooling (MIL style)",
        "A-UNL": "unlearned rank weight",
        "KO-S-BD": r"features from $B$ and $D$", "KO-S-s3": r"uncertainty of $B$ pass", "KO-S-tbv": "one-pass score",
        "KO-S-ltex": "patch texture", "KO-S-nbr": "neighbour distance", "KO-S-pos": "grid position (by source)",
        "KO-F-token": "token scores", "KO-F-position": "position (by formula)", "KO-F-neighbourhood": "neighbourhood",
        "KO-F-rank": "within-image rank", "KO-F-item": "image-level"}
byid = {r["id"]: r for r in AB["rows"]}
assert set(byid) == set(ORDER_3A) | set(ORDER_3B), sorted(set(byid) ^ (set(ORDER_3A) | set(ORDER_3B)))
assert [byid[i]["block"] for i in ORDER_3A] == ["3a"] * 10 and [byid[i]["block"] for i in ORDER_3B] == ["3b"] * 11
N = AB["n_per_cell"][CELL]
rec = [dict(id=i, block=byid[i]["block"], acc=byid[i]["cells"][CELL]["acc"], **byid[i]["cells"][CELL]["vs_LRF"]) for i in ORDER_3A + ORDER_3B]
S.trace("fig_ablation", "fig_ablation.py", dict(source=f"runs/P2-LRF-ABL-SCORE/ablation_analysis.json rows[*].cells.{CELL}.vs_LRF", cell=CELL, n=N,
                                                 lrf_accuracy=AB["references_accuracy"]["LRF"][CELL], label=AB["meta"]["label"],
                                                 sign=AB["meta"]["sign"], interval=AB["meta"]["interval"], rows=rec))

# layout: header row before each block
items, y = [], 0
for blk, hdr, ids in (("3a", "refitted and unlearned weightings", ORDER_3A), ("3b", "knockouts of the frozen LRF", ORDER_3B)):
    items.append(("hdr", hdr, y))
    y += 1
    for i in ids:
        items.append(("row", i, y))
        y += 1
NY = y
H = 0.30 + 0.128 * NY + 0.42
fig = plt.figure(figsize=(S.COL1, H))
ax = fig.add_axes([1.50 / S.COL1, 0.42 / H, 1.90 / S.COL1, (0.128 * NY) / H])
lo = min(r["ci95"][0] for r in rec)
hi = max(r["ci95"][1] for r in rec)
ax.set_xlim(lo - 0.012, hi + 0.012)
ax.set_ylim(NY - 0.5, -0.6)
ax.axvline(0, color=C["ink"], lw=0.8, zorder=1)
G = C["green"]
tr = blended_transform_factory(fig.transFigure, ax.transData)
recd = {r["id"]: r for r in rec}
for kind, key, yy in items:
    if kind == "hdr":
        ax.text(0.03 / S.COL1, yy, key, transform=tr, ha="left", va="center", fontsize=S.FS, style="italic", color=C["grey"])
        if yy > 0:
            ax.axhline(yy - 0.5, color=C["lgrey"], lw=0.6, zorder=0)
        continue
    r = recd[key]
    mfc = "white" if r["block"] == "3b" else G
    ax.plot(r["ci95"], [yy, yy], color=G, lw=1.1, solid_capstyle="butt", zorder=3)
    ax.plot([r["d"]], [yy], marker="D", ms=3.0, mfc=mfc, mec=G, mew=0.8, ls="none", zorder=4)
    ax.text(1.46 / S.COL1, yy, NAME[key], transform=tr, ha="right", va="center", fontsize=S.FS)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.xaxis.set_major_locator(plt.MultipleLocator(0.05))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: "0" if abs(v) < 1e-9 else f"{v:+.2f}".replace("-", MINUS)))
ax.set_xlabel("accuracy difference, variant minus LRF", labelpad=1.5)
ax.text(0, -1.05, "frozen LRF", ha="center", va="bottom", fontsize=S.FS, color=C["ink"])
S.save(fig, "fig_ablation")
print([(r["id"], round(r["d"], 3), [round(v, 3) for v in r["ci95"]]) for r in rec])
