"""Fig. 6 of the main paper (Study 2, frozen weight model: schematic only, two-column) and Fig. S-PD of the supplement (partial dependence).
Descriptive: no accuracy, no correctness mark.
Layout change 2026-10-30 (Mask-DiFuser pass): panel (b) partial dependence moved to the supplement as figure fig4b_pd_curves (one row of six);
panel (c) token-weight maps dropped from the paper (the real-image figure fig_qualitative replaces it); the maps stay in runs/P2-PAPER-FIGS/fig4_token_weights.npz.

(a) Partial dependence of the token weight w = sigmoid(f(x)) on the 6 features with the largest learned effect range, all other standardised
    features at their mean 0, x axis in original feature units (mu + sd * x). f(x) = b + a_k x + sum_m c_km relu(x - t_km) (spec.json "family").
    Domain of each curve: first to last knot of that feature (the 1/9 ... 8/9 quantiles of the standardised design-token features, from
    analysis_posthoc/learned_ceiling/families.py F1GAM.build). Effect range = max w - min w over that domain. Selection rule fixed here, before the plot.
(b) Token-weight maps (32 x 32 grid, row-major token index), clean and under Gaussian noise 0.1 side by side on ONE colour scale, for the FIRST THREE items in runs/P2-LRF-L1/items.jsonl order,
    computed with analysis_posthoc.learned_ceiling.lrf.load_frozen / infer_item on runs/P2-LRF-L1/arrays/item000{0,1,2}.npz (arrays are verified against
    arrays_manifest.json sha256 before use). Items are chosen by position only, never by outcome.

Reads: runs/P2-LRF-FROZEN-LFIX/{model.npz,spec.json}, runs/P2-LRF-L1/{items.jsonl,arrays_manifest.json,arrays/item0000..0002.npz}.
Writes (traceability): runs/P2-PAPER-FIGS/fig4_pd_curves.json, fig4_token_weights.npz, fig4_meta_2026-10-31.json (script sha256 included; a NEW dated file, never the committed fig4_meta.json, which
is the record of the earlier run and must not be edited in place: red-team F15).
Output: paper2-tnnls/figures/fig4_study2_weights.pdf (+ png preview). CPU only (CUDA_VISIBLE_DEVICES is emptied before torch is imported).
"""
from __future__ import annotations

META_NAME = "fig4_meta_2026-10-31.json"

import json
import os
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

import figstyle as S
from figstyle import C

sys.path.insert(0, str(S.REPO))
from analysis_posthoc.learned_ceiling.lrf import infer_item, load_frozen  # noqa: E402

S.apply()
FROZEN = S.RUNS / "P2-LRF-FROZEN-LFIX"
L1 = S.RUNS / "P2-LRF-L1"
OUT = S.RUNS / "P2-PAPER-FIGS"
OUT.mkdir(exist_ok=True)
COND = "noise0.1"
N_ITEMS_SHOWN, N_FEAT_SHOWN, NGRID = 3, 6, 400

fz = load_frozen(FROZEN)                       # raises if model.npz does not match spec.json sha256
names = list(fz["spec"]["features"])
a, b, c, knots, mu, sd = (fz[k] for k in ("a", "b", "c", "knots", "mu", "sd"))
assert a.shape == (35,) and c.shape == knots.shape == (35, 8)


def f_k(k: int, x: np.ndarray) -> np.ndarray:
    return float(b) + a[k] * x + (np.maximum(x[:, None] - knots[k][None, :], 0.0) * c[k][None, :]).sum(1)


curves = []
for k, nm in enumerate(names):
    x = np.linspace(knots[k].min(), knots[k].max(), NGRID)
    w = 1.0 / (1.0 + np.exp(-f_k(k, x)))
    curves.append(dict(name=nm, x_std=x, x_orig=mu[k] + sd[k] * x, w=w, range=float(w.max() - w.min()),
                       w_at_mean=float(1.0 / (1.0 + np.exp(-f_k(k, np.array([0.0]))[0])))))
order = sorted(range(35), key=lambda k: -curves[k]["range"])
top = order[:N_FEAT_SHOWN]
print("top features by effect range:", [(names[k], round(curves[k]["range"], 4)) for k in top])
print("next three:", [(names[k], round(curves[k]["range"], 4)) for k in order[N_FEAT_SHOWN:N_FEAT_SHOWN + 3]])

# ---- token-weight maps for the first three items of the fold --------------------------------------------------------------
manifest = S.jload("P2-LRF-L1/arrays_manifest.json")["files"]
items = [json.loads(line) for line in open(L1 / "items.jsonl", encoding="utf-8")][:N_ITEMS_SHOWN]
CONDS = ("clean", COND)
maps, meta_items = {c: [] for c in CONDS}, []
for it in items:
    fn = f"item{it['idx']:04d}.npz"
    assert S.sha256(L1 / "arrays" / fn) == manifest[fn], f"{fn} does not match arrays_manifest.json"
    d = np.load(L1 / "arrays" / fn)
    rec = dict(position_in_items_jsonl=len(meta_items), idx=it["idx"], gid=it["gid"], image_id=it["image_id"], array=fn, array_sha256=manifest[fn])
    for cnd in CONDS:
        w = np.asarray(infer_item(fz, d, cnd)["w"], float)
        assert w.shape == (1024,) and np.isfinite(w).all()
        maps[cnd].append(w.reshape(32, 32))
        rec[cnd] = dict(w_min=float(w.min()), w_max=float(w.max()), w_mean=float(w.mean()))
    meta_items.append(rec)
allmaps = [m for c in CONDS for m in maps[c]]
vmin, vmax = min(m.min() for m in allmaps), max(m.max() for m in allmaps)

# ---- trace to a run directory -----------------------------------------------------------------------------------------------
json.dump({curves[k]["name"]: dict(x_orig=curves[k]["x_orig"].tolist(), w=curves[k]["w"].tolist(), effect_range=curves[k]["range"],
                                   w_at_standardised_mean=curves[k]["w_at_mean"], shown=k in top) for k in range(35)},
          open(OUT / "fig4_pd_curves.json", "w", encoding="utf-8"))
np.savez_compressed(OUT / "fig4_token_weights.npz", **{f"item{i}_{c}_w": maps[c][i] for c in CONDS for i in range(len(items))})
meta = dict(
    purpose="Fig. 6 (schematic of the frozen weight model) and supplement partial-dependence figure of paper2-tnnls (descriptive); the stored token-weight maps are no longer plotted; no accuracy computed",
    script="paper2-tnnls/scripts/fig4_study2_weights.py", script_sha256=S.sha256(S.HERE / "fig4_study2_weights.py"),
    figstyle_sha256=S.sha256(S.HERE / "figstyle.py"),
    frozen_dir="runs/P2-LRF-FROZEN-LFIX", model_sha256=S.sha256(FROZEN / "model.npz"), spec_model_sha256=fz["spec"]["model_sha256"],
    selection_rule_features="the 6 of 35 features with the largest range of w = sigmoid(f) over the knot span, other features at standardised mean 0",
    selection_rule_items="first 3 items in runs/P2-LRF-L1/items.jsonl order (position only)", conditions=list(CONDS),
    features_shown=[names[k] for k in top], effect_ranges={names[k]: curves[k]["range"] for k in order}, items=meta_items,
    colour_scale=dict(vmin=float(vmin), vmax=float(vmax), norm="PowerNorm gamma 0.5 (square root)", rule="shared minimum and maximum of the six maps (three items, clean and noisy)"),
    numpy=np.__version__, created_unix=time.time(), cpu_only=True, cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"),
)
json.dump(meta, open(OUT / META_NAME, "w", encoding="utf-8"), indent=1)

# ---- figure ----------------------------------------------------------------------------------------------------------------------
# group names are those of tables/tab_features_main.tex; titles use its notation (B_j, r_j, log(1+v_j), ...)
def GROUP(n):
    if n in ("row", "col", "rad"):
        return "position"
    if n.startswith(("nb3", "nb5")):
        return "neighbourhood"
    if n.startswith("rank_"):
        return "within-image rank"
    if n.startswith("itemmean_"):
        return "image mean"
    if n.startswith("itemsd_"):
        return "image standard deviation"
    if n == "itemz_q":
        return "image z-score"
    return "token scores"


GROUPS = ["token scores", "position", "neighbourhood", "within-image rank", "image mean", "image standard deviation", "image z-score"]
GCOUNT = {g: sum(GROUP(n) == g for n in names) for g in GROUPS}
assert sum(GCOUNT.values()) == len(names) == 35
GSTYLE = {"token scores": (C["green"], "-"), "position": (C["orange"], (0, (5, 1.5))), "neighbourhood": (C["purple"], (0, (2.5, 1.2))),
          "within-image rank": (C["verm"], (0, (1, 1.2))), "image mean": (C["blue"], (0, (3, 1, 1, 1))),
          "image standard deviation": ("#444444", (0, (6, 1.5, 1.5, 1.5))), "image z-score": (C["sky"], (0, (4, 2)))}
BASE = {"B": r"$B_j$", "D": r"$D_j$", "q": r"$r_j$", "s3": r"$1-\max_y p(y)$", "tbv": "one-pass\nlog-probability", "ltex": r"$\log(1+v_j)$",
        "nbr": "neighbour\ndistance"}
PREFIX = {"rank_": "rank of", "nb3mean_": "neighbour mean of", "nb3min_": "neighbour minimum of", "nb5mean_": r"$5\times5$ mean of",
          "itemmean_": "image mean of", "itemsd_": "image std. dev. of", "itemz_": "image z-score of"}


def pretty(n):
    for pre, txt in PREFIX.items():
        if n.startswith(pre):
            return txt + "\n" + BASE[n[len(pre):]].replace("\n", " ")
    if n in BASE:
        return BASE[n]
    return {"row": "grid row", "col": "grid column", "rad": "distance from centre"}[n]


from matplotlib.lines import Line2D  # noqa: E402
from schem import Canvas, tint  # noqa: E402

MODEL_SHA = S.jload("P2-LRF-FROZEN-LFIX/HASHES.json")["new"]["runs/P2-LRF-FROZEN-LFIX/model.npz"]
assert MODEL_SHA == fz["spec"]["model_sha256"] == meta["model_sha256"]
NEVER = fz["spec"]["inputs_never_used"]
assert {"Delta", "captions", "condition identity"} <= set(NEVER)
Q = knots.shape[1]
json.dump(dict(meta, panel_a=dict(group_counts=GCOUNT, model_sha256_prefix=MODEL_SHA[:8], knots_per_feature=int(Q),
                                  inputs_never_used_printed=["Delta", "captions", "condition identity"],
                                  schematic="no data; weight grid drawn with numpy seed 7")),
          open(OUT / META_NAME, "w", encoding="utf-8"), indent=1)

W_MM, HA = S.COL2 * 25.4, 44.0
H = HA / 25.4
fig = plt.figure(figsize=(S.COL2, H))

# ---- (a) schematic: features -> GAM f -> w_j -> weighted sum -> decision -------------------------------------------------------------------
cv = Canvas(fig, [0, 1 - HA / (H * 25.4), 1, HA / (H * 25.4)], W_MM, HA)
GREEN = C["green"]
YC = 22.0
fx, fw, rowh = 4.0, 52.0, 3.55
ftop = YC + 3.55 * 3.5 + 3.0
cv.box(fx, YC - 3.55 * 3.5 - 1.6, fw, 3.55 * 7 + 7.6, fc="#FAFAFA")
cv.text(fx + fw / 2, ftop + 0.9, rf"per-token features $x_j$ ({len(names)})", fs=S.FS)
for i, g in enumerate(GROUPS):
    y = ftop - 3.6 - i * rowh
    col, ls = GSTYLE[g]
    cv.ax.plot([fx + 2.5, fx + 9.0], [y, y], color=col, ls=ls, lw=1.6, zorder=4)
    cv.text(fx + 10.5, y, f"{g} ({GCOUNT[g]})", ha="left", fs=S.FS)
cv.text(fx + fw / 2, YC - 3.55 * 3.5 - 4.6, r"no input uses $\Delta_j$, a caption or the condition", fs=S.FS, style="italic", color=C["grey"])
cv.arrow(fx + fw + 1.0, YC, 63.0, YC)
gx0, gw = 64.0, 46.0
cv.box(gx0, YC - 9.5, gw, 19.0, ec=GREEN, lw=1.0)
cv.text(gx0 + gw / 2, YC + 5.6, "logistic additive model (hinge basis)", fs=S.FS)
cv.text(gx0 + gw / 2, YC + 0.8, r"$f(x_j)=\beta_0+\sum_k a_k x_{jk}$", fs=S.FS)
cv.text(gx0 + gw / 2, YC - 4.2, rf"$+\sum_{{k}}\sum_{{l=1}}^{{{Q}}} c_{{kl}}(x_{{jk}}-t_{{kl}})_+$", fs=S.FS)
cv.box(gx0, YC - 21.0, gw, 9.4, fc=tint(GREEN, 0.12), ec=GREEN, lw=0.6, ls=(0, (3, 1.6)))
cv.text(gx0 + gw / 2, YC - 14.0, "frozen before any test image", fs=S.FS)
cv.text(gx0 + gw / 2, YC - 18.4, f"SHA-256 {MODEL_SHA[:8]}...", fs=S.FS)
cv.arrow(gx0 + gw + 1.0, YC, 115.5, YC)
rng7 = np.random.default_rng(7)
N7, CS7 = 6, 2.3
wv = rng7.beta(0.7, 2.2, (N7, N7))
wx = 116.5
cv.grid(wx, YC - N7 * CS7 / 2, [[tint(GREEN, 0.08 + 0.92 * v) for v in row] for row in wv], CS7)
cv.text(wx + N7 * CS7 / 2, YC - N7 * CS7 / 2 - 3.0, r"$w_j=\mathrm{sigm}(f(x_j))$", fs=S.FS)
cv.text(wx + N7 * CS7 / 2, YC + N7 * CS7 / 2 + 2.6, "token weights", fs=S.FS)
cv.arrow(wx + N7 * CS7 + 1.0, YC, 135.5, YC)
cv.box(136.5, YC - 6.5, 21.0, 13.0)
cv.text(147.0, YC + 2.4, "weighted sum", fs=S.FS)
cv.text(147.0, YC - 2.4, r"$\sum_j w_j\Delta_j$", fs=S.FS)
cv.arrow(147.0, YC + 13.5, 147.0, YC + 6.5)
cv.text(147.0, YC + 15.6, r"$\Delta_j$ (Fig. 1)", fs=S.FS)
cv.arrow(158.5, YC, 161.5, YC)
cv.box(162.5, YC - 6.5, 18.5, 13.0, lw=1.0)
cv.text(171.75, YC + 2.4, "decision", fs=S.FS)
cv.text(171.75, YC - 2.4, r"$\sum_j w_j\Delta_j>0$", fs=S.FS - 0.5)

S.save(fig, "fig4_study2_weights")

# ---- supplement figure: partial dependence, one row of six ---------------------------------------------------------------------------------
ylo = min(curves[k]["w"].min() for k in top)
yhi = max(curves[k]["w"].max() for k in top)
pad = 0.06 * (yhi - ylo)
HS = 1.45
pw, ph, pgx = 0.92, 0.62, 0.19                     # inches
px0, pb = 0.50, 0.40
figb = plt.figure(figsize=(S.COL2, HS))
axes_b = []
for i, k in enumerate(top):
    ax = figb.add_axes([(px0 + i * (pw + pgx)) / S.COL2, pb / HS, pw / S.COL2, ph / HS], sharey=axes_b[0] if axes_b else None)
    col, ls = GSTYLE[GROUP(names[k])]
    ax.plot(curves[k]["x_orig"], curves[k]["w"], color=col, ls=ls, lw=1.6)
    ax.plot(mu[k] + sd[k] * knots[k], np.full(knots.shape[1], ylo - 0.5 * pad), ls="none", marker="|", ms=3.0, color=C["grey"],
            clip_on=False, zorder=1)
    ax.set_title(pretty(names[k]), fontsize=S.FS, pad=2, linespacing=1.0)
    ax.locator_params(axis="x", nbins=3)
    if i > 0:
        plt.setp(ax.get_yticklabels(), visible=False)
    ax.set_xlabel("feature value", labelpad=1.0)
    axes_b.append(ax)
axes_b[0].set_ylim(ylo - 2 * pad, yhi + pad)
figb.text(0.06 / S.COL2, (pb + ph / 2) / HS, r"weight $w=\mathrm{sigm}(f(x))$", rotation=90, va="center", ha="left", fontsize=S.FS)
S.save(figb, "fig4b_pd_curves")
