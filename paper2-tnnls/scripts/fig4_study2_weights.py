"""Fig. 4 (Study 2, frozen weight model, two-column). Descriptive: no accuracy, no correctness mark.

(a) Partial dependence of the token weight w = sigmoid(f(x)) on the 6 features with the largest learned effect range, all other standardised
    features at their mean 0, x axis in original feature units (mu + sd * x). f(x) = b + a_k x + sum_m c_km relu(x - t_km) (spec.json "family").
    Domain of each curve: first to last knot of that feature (the 1/9 ... 8/9 quantiles of the standardised design-token features, from
    analysis_posthoc/learned_ceiling/families.py F1GAM.build). Effect range = max w - min w over that domain. Selection rule fixed here, before the plot.
(b) Token-weight maps (32 x 32 grid, row-major token index), clean and under Gaussian noise 0.1 side by side on ONE colour scale, for the FIRST THREE items in runs/P2-LRF-L1/items.jsonl order,
    computed with analysis_posthoc.learned_ceiling.lrf.load_frozen / infer_item on runs/P2-LRF-L1/arrays/item000{0,1,2}.npz (arrays are verified against
    arrays_manifest.json sha256 before use). Items are chosen by position only, never by outcome.

Reads: runs/P2-LRF-FROZEN-LFIX/{model.npz,spec.json}, runs/P2-LRF-L1/{items.jsonl,arrays_manifest.json,arrays/item0000..0002.npz}.
Writes (traceability): runs/P2-PAPER-FIGS/fig4_pd_curves.json, fig4_token_weights.npz, fig4_meta.json (script sha256 included).
Output: paper2-tnnls/figures/fig4_study2_weights.pdf (+ png preview). CPU only (CUDA_VISIBLE_DEVICES is emptied before torch is imported).
"""
from __future__ import annotations

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
    purpose="Fig. 4 of paper2-tnnls (descriptive: partial dependence of the frozen weight model and three token-weight maps); no accuracy computed",
    script="paper2-tnnls/scripts/fig4_study2_weights.py", script_sha256=S.sha256(S.HERE / "fig4_study2_weights.py"),
    figstyle_sha256=S.sha256(S.HERE / "figstyle.py"),
    frozen_dir="runs/P2-LRF-FROZEN-LFIX", model_sha256=S.sha256(FROZEN / "model.npz"), spec_model_sha256=fz["spec"]["model_sha256"],
    selection_rule_features="the 6 of 35 features with the largest range of w = sigmoid(f) over the knot span, other features at standardised mean 0",
    selection_rule_items="first 3 items in runs/P2-LRF-L1/items.jsonl order (position only)", conditions=list(CONDS),
    features_shown=[names[k] for k in top], effect_ranges={names[k]: curves[k]["range"] for k in order}, items=meta_items,
    colour_scale=dict(vmin=float(vmin), vmax=float(vmax), norm="PowerNorm gamma 0.5 (square root)", rule="shared minimum and maximum of the six maps (three items, clean and noisy)"),
    numpy=np.__version__, created_unix=time.time(), cpu_only=True, cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"),
)
json.dump(meta, open(OUT / "fig4_meta.json", "w", encoding="utf-8"), indent=1)

# ---- figure ----------------------------------------------------------------------------------------------------------------------
GROUP = lambda n: ("position" if n in ("row", "col", "rad") else "neighbourhood" if n.startswith(("nb3", "nb5")) else "rank" if n.startswith("rank_")
                   else "item-level" if n.startswith("item") else "token score")
GSTYLE = {"token score": (C["green"], "-"), "position": (C["orange"], (0, (5, 1.5))), "neighbourhood": (C["purple"], (0, (2.5, 1.2))),
          "rank": (C["verm"], (0, (1, 1.2))), "item-level": ("#444444", (0, (6, 1.5, 1.5, 1.5)))}
H = 3.45
fig = plt.figure(figsize=(S.COL2, H))
ylo = min(curves[k]["w"].min() for k in top)
yhi = max(curves[k]["w"].max() for k in top)
pad = 0.06 * (yhi - ylo)
ax_w, gap, left = 0.118, 0.040, 0.068
bot_a, h_a = 2.05 / H, 1.05 / H
axes_a = []
for i, k in enumerate(top):
    ax = fig.add_axes([left + i * (ax_w + gap), bot_a, ax_w, h_a], sharey=axes_a[0] if axes_a else None)
    col, ls = GSTYLE[GROUP(names[k])]
    ax.plot(curves[k]["x_orig"], curves[k]["w"], color=col, ls=ls, lw=1.6)
    ax.plot(mu[k] + sd[k] * knots[k], np.full(8, ylo - 0.5 * pad), ls="none", marker="|", ms=3.5, color=C["grey"], clip_on=False, zorder=1)
    ax.axhline(float(1 / (1 + np.exp(-0.0))), lw=0)
    ax.set_title(f"{names[k]}", fontsize=S.FS, pad=14)
    ax.text(0.5, 1.03, GROUP(names[k]), transform=ax.transAxes, ha="center", va="bottom", fontsize=S.FS, color=C["grey"], style="italic")
    ax.set_xlabel("feature value", labelpad=1.0)
    ax.locator_params(axis="x", nbins=3)
    if i > 0:
        plt.setp(ax.get_yticklabels(), visible=False)
    axes_a.append(ax)
axes_a[0].set_ylim(ylo - 2 * pad, yhi + pad)
axes_a[0].set_ylabel(r"weight $w=\sigma(f(x))$")
fig.text(0.004, 0.975, "(a)", fontsize=S.FS + 1, fontweight="bold", va="top")

side = 0.118
side_in = side * S.COL2
bot_b = 0.40 / H
h_b = side_in / H
x0b, g_in, g_out = 0.064, 0.022, 0.034
xs = []
for gi in range(3):
    base = x0b + gi * (2 * side + g_in + g_out)
    xs += [base, base + side + g_in]
ims = []
for i in range(6):
    gi, cnd = divmod(i, 2)
    m = maps[CONDS[cnd]][gi]
    ax = fig.add_axes([xs[i], bot_b, side, h_b])
    im = ax.imshow(m, cmap="cividis", norm=PowerNorm(0.5, vmin=vmin, vmax=vmax), interpolation="nearest", origin="upper")
    ims.append(im)
    ax.set_xticks([0, 31])
    ax.set_yticks([0, 31])
    ax.set_xticklabels(["0", "31"])
    ax.set_yticklabels(["0", "31"] if i == 0 else [])
    ax.set_xlabel("token column", labelpad=1.0)
    if i == 0:
        ax.set_ylabel("token row", labelpad=1.0)
    ax.set_title("clean" if cnd == 0 else "noise", fontsize=S.FS, pad=2)
    for sp in ax.spines.values():
        sp.set_visible(True)
        sp.set_linewidth(0.6)
    if cnd == 0:
        fig.text((xs[i] + side + g_in / 2) , bot_b + h_b + 0.052, f"Item {gi + 1}", fontsize=S.FS, ha="center", va="bottom", fontweight="bold") if False else None
        ax.annotate(f"Item {gi + 1}", xy=(1.0 + (g_in / side) / 2, 1.0), xycoords="axes fraction", xytext=(0, 12), textcoords="offset points",
                    ha="center", va="bottom", fontsize=S.FS, fontweight="bold")
fig.text(0.004, bot_b + h_b + 0.075, "(b)", fontsize=S.FS + 1, fontweight="bold", va="top")
cax = fig.add_axes([xs[5] + side + 0.016, bot_b, 0.010, h_b])
cb = fig.colorbar(ims[0], cax=cax)
cb.set_label(r"weight $w_j$ (square-root scale)", labelpad=2.0)
cb.outline.set_linewidth(0.5)
cb.ax.tick_params(length=2.0, width=0.5)
S.save(fig, "fig4_study2_weights")
