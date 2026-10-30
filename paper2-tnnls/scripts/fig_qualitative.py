"""Qualitative figure (two-column, E4 of research/paper2/tnnls/EXPLORATORY-PLAN-BASELINES-2026-10-30.md). DESCRIPTIVE: three real fresh-fold items under Gaussian noise 0.1.

Rows are chosen by a rule fixed before the figure was made (plan E4): the first item in fold-file order (smallest `idx` in runs/P2-LRF-L1/predictions.jsonl, condition noise0.1) of each kind
  (i)   unweighted (NONE) correct and LRF correct,
  (ii)  NONE wrong and LRF correct,
  (iii) NONE correct and LRF wrong.
Columns (fixed order): (a) clean 512 px centre crop, (b) the noisy image, regenerated with the experiment's own corruption code and seed so it is pixel-identical to what was scored
(exp_p2.gate.suite.center_crop_512 = UniScorer.preprocess; exp_p2.gate.corruptions.apply_pixel('noise', 0.1, ..., exp_p2.run_gate_m3.rung_rng(gid, 'noise', rung)); the call run_gate_m4.build_conditions makes),
(c) the per-token evidence Delta_j on the 32 x 32 token grid (stored `noise0.1_delta`), (d) the LRF token weight w_j (frozen model runs/P2-LRF-FROZEN-LFIX applied by
analysis_posthoc.learned_ceiling.lrf.infer_item to the stored arrays, as Fig. 4 does; w is not stored in the arrays).
Checks before drawing (assert): array sha256 against arrays_manifest.json; recomputed Y_NONE, Y_LRF, margins, w_sum and w_mean equal the stored prediction row; the noise draw is deterministic.
Writes runs/P2-PAPER-FIGS/fig_qualitative.json (selection, fields, colour-scale rule, sha256 of the regenerated noisy pixels) and
paper2-tnnls/figures/fig_qualitative.{pdf,png}. CPU only, nothing downloaded.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import textwrap

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, PowerNorm
from matplotlib.ticker import MultipleLocator

import figstyle as S
from figstyle import C, MINUS

sys.path.insert(0, str(S.REPO))
from analysis_posthoc.learned_ceiling.lrf import infer_item, load_frozen  # noqa: E402
from exp_p2 import common  # noqa: E402
from exp_p2.gate import config, corruptions, suite  # noqa: E402
from exp_p2.run_gate_m3 import rung_rng  # noqa: E402

S.apply()
L1 = S.RUNS / "P2-LRF-L1"
FROZEN = S.RUNS / "P2-LRF-FROZEN-LFIX"
COND, SIGMA = "noise0.1", 0.1
KINDS = [
    ("i", "NONE correct, LRF correct", lambda r: r["y_none"] == 1 and r["y_lrf"] == 1),
    ("ii", "NONE wrong, LRF correct", lambda r: r["y_none"] == 0 and r["y_lrf"] == 1),
    ("iii", "NONE correct, LRF wrong", lambda r: r["y_none"] == 1 and r["y_lrf"] == 0),
]

# ---- selection: the fixed rule ------------------------------------------------------------------------------------------------------------
pred = [json.loads(l) for l in open(L1 / "predictions.jsonl", encoding="utf-8")]
rows = [r for r in pred if r["condition"] == COND]
assert [r["idx"] for r in rows] == sorted(r["idx"] for r in rows) and len({r["idx"] for r in rows}) == len(rows) == 450   # fold-file order = idx order
items = {r["idx"]: r for r in map(json.loads, open(L1 / "items.jsonl", encoding="utf-8"))}
manifest = S.jload("P2-LRF-L1/arrays_manifest.json")["files"]
fz = load_frozen(FROZEN)                                   # raises if model.npz does not match spec.json sha256
MODEL_SHA = S.jload("P2-LRF-FROZEN-LFIX/HASHES.json")["new"]["runs/P2-LRF-FROZEN-LFIX/model.npz"]
assert MODEL_SHA == fz["spec"]["model_sha256"] == S.sha256(FROZEN / "model.npz")

sel = []
for tag, label, pick in KINDS:
    cands = [r for r in rows if pick(r)]
    sel.append(dict(kind=tag, kind_label=label, n_items_of_this_kind_in_fold=len(cands), row=cands[0]))
for s in sel:
    assert all(not KINDS[[k[0] for k in KINDS].index(s["kind"])][2](r) for r in rows if r["idx"] < s["row"]["idx"])           # nothing of this kind comes earlier

# ---- per-row data ---------------------------------------------------------------------------------------------------------------------------
data = []
for s in sel:
    r = s["row"]
    it = items[r["idx"]]
    assert it["gid"] == r["gid"] and it["image_id"] == r["image_id"]
    fn = f"item{r['idx']:04d}.npz"
    assert S.sha256(L1 / "arrays" / fn) == manifest[fn], f"{fn} does not match arrays_manifest.json"
    d = dict(np.load(L1 / "arrays" / fn))
    delta = np.asarray(d[f"{COND}_delta"], float)
    inf = infer_item(fz, d, COND)
    w = np.asarray(inf["w"], float)
    assert w.shape == delta.shape == (1024,) and np.isfinite(w).all() and np.isfinite(delta).all()
    sum_none, sum_lrf = float(delta.sum()), float((w * delta).sum())
    # positive control: everything recomputed from the stored arrays must equal the stored prediction row
    assert int(sum_none / 1024 > 0) == r["y_none"] and int(sum_lrf > 0) == r["y_lrf"] == int(inf["decision"])
    assert abs(sum_none / 1024 - r["m_none"]) < 1e-6 and abs(inf["margin"] - r["m_lrf"]) < 1e-9
    assert abs(float(w.sum()) - r["w_sum"]) < 1e-9 and abs(float(w.mean()) - r["w_mean"]) < 1e-12
    # pixels: the code path of run_gate_m4.build_conditions
    pil = suite.center_crop_512(common.load_image(it["image_id"]))
    rung = list(config.LADDERS["noise"]).index(SIGMA)
    noisy = corruptions.apply_pixel("noise", SIGMA, pil, rung_rng(it["gid"], "noise", rung))
    again = corruptions.apply_pixel("noise", SIGMA, pil, rung_rng(it["gid"], "noise", rung))
    assert np.array_equal(np.asarray(noisy), np.asarray(again))
    data.append(dict(sel=s, row=r, item=it, delta=delta, w=w, sum_none=sum_none, sum_lrf=sum_lrf, clean=np.asarray(pil), noisy=np.asarray(noisy), array=fn))

# ---- colour scales (rules fixed here, shared by the three rows) -----------------------------------------------------------------------------
all_abs = np.concatenate([np.abs(x["delta"]) for x in data])
DMAX = float(np.percentile(all_abs, 99))                   # symmetric diverging limit: 99th percentile of |Delta| pooled over the three maps (larger values are clipped)
WMAX = float(max(x["w"].max() for x in data))             # sequential 0 .. largest weight of the three maps, square-root scale as Fig. 4
n_clipped = int((all_abs > DMAX).sum())
CM_DELTA = LinearSegmentedColormap.from_list("delta", [C["verm"], "#F7F7F7", C["blue"]])     # Okabe-Ito vermillion (favours the wrong caption) - white - blue (favours the true caption)
CM_W = LinearSegmentedColormap.from_list("w", ["#F7F7F7", "#8ED3B8", C["green"], "#00513A"])  # Study 2 colour, luminance falls monotonically
NORM_D, NORM_W = Normalize(-DMAX, DMAX), PowerNorm(0.5, vmin=0.0, vmax=WMAX)

# ---- layout in inches -------------------------------------------------------------------------------------------------------------------------
W, H = S.COL2, 3.2
SZ, GAP = 0.82, 0.07
X0, TOPM, HDR = 0.30, 0.03, 0.17
FSM = 6.9
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor("white")


def ax_in(x, y_top, w, h):
    return fig.add_axes([x / W, 1 - (y_top + h) / H, w / W, h / H])


col_x = [X0 + k * (SZ + GAP) for k in range(4)]
HEAD = ["(a) Clean", r"(b) Noisy, $\sigma=0.1$", r"(c) Evidence $\Delta_j$", r"(d) LRF weight $w_j$"]
for k, h in enumerate(HEAD):
    fig.text((col_x[k] + SZ / 2) / W, 1 - (TOPM + HDR - 0.03) / H, h, ha="center", va="bottom", fontsize=FSM, fontweight="bold")
TX = col_x[3] + SZ + 0.16
fig.text(TX / W, 1 - (TOPM + HDR - 0.03) / H, "(e) Captions and decisions", ha="left", va="bottom", fontsize=FSM, fontweight="bold")


def frame(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(True)
        sp.set_linewidth(0.5)
        sp.set_edgecolor(C["grey"])


rend = fig.canvas.get_renderer()
TW = W - 0.06 - TX


def wrap(s, bold=False, prefix_w=0.0, width_in=None):
    """Greedy wrap of s to the text width using the renderer (font as drawn)."""
    width_in = (TW if width_in is None else width_in) - prefix_w
    words, lines, cur = s.split(), [], ""
    t = fig.text(0, 0, "", fontsize=FSM, fontweight="bold" if bold else "normal")
    for wd in words:
        trial = (cur + " " + wd).strip()
        t.set_text(trial)
        if t.get_window_extent(rend).width / fig.dpi > width_in and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    lines.append(cur)
    t.remove()
    return lines


def tw(s, bold=False):
    t = fig.text(0, 0, s, fontsize=FSM, fontweight="bold" if bold else "normal")
    v = t.get_window_extent(rend).width / fig.dpi
    t.remove()
    return v


def sgn(v, nd=1):
    return (f"+{v:.{nd}f}" if v >= 0 else f"{MINUS}{abs(v):.{nd}f}")


def word(y):
    return "correct" if y == 1 else "wrong"


LH = 0.135
for i, x in enumerate(data):
    y0 = TOPM + HDR + i * (SZ + GAP)
    ims = [(x["clean"], None, None), (x["noisy"], None, None), (x["delta"].reshape(32, 32), CM_DELTA, NORM_D), (x["w"].reshape(32, 32), CM_W, NORM_W)]
    for k, (im, cm, nm) in enumerate(ims):
        ax = ax_in(col_x[k], y0, SZ, SZ)
        if cm is None:
            ax.imshow(im, interpolation="antialiased")
        else:
            ax.imshow(im, cmap=cm, norm=nm, interpolation="nearest")
        frame(ax)
    fig.text((col_x[0] - 0.05) / W, 1 - (y0 + SZ / 2) / H, x["sel"]["kind"], ha="right", va="center", fontsize=FSM + 0.5, fontweight="bold")
    # text block (e)
    r, it = x["row"], x["item"]
    ty = y0 + 0.005
    lines = []                                          # (text, style)
    lines.append((f"unweighted: {word(r['y_none'])}; LRF: {word(r['y_lrf'])}", "dec"))
    lines += [(l, "cap_t" if j else "cap_t0") for j, l in enumerate(wrap(it["caption"], prefix_w=tw("True: ", True)))]
    lines += [(l, "cap_w" if j else "cap_w0") for j, l in enumerate(wrap(it["neg_caption"], prefix_w=tw("Wrong: ", True)))]
    lines.append((rf"$\sum\Delta_j={sgn(x['sum_none'])}$;  $\sum w_j\Delta_j={sgn(x['sum_lrf'], 2)}$", "sum"))
    lines.append((f"COCO val2017 image {it['image_id']}, fold index {r['idx']}", "id"))
    yy = ty
    for text, st in lines:
        yc = 1 - (yy + LH / 2) / H
        if st == "head":
            fig.text(TX / W, yc, text, ha="left", va="center", fontsize=FSM, fontweight="bold")
        elif st in ("cap_t0", "cap_w0"):
            lab = "True: " if st == "cap_t0" else "Wrong: "
            fig.text(TX / W, yc, lab, ha="left", va="center", fontsize=FSM, fontweight="bold", color=C["blue"] if st == "cap_t0" else C["verm"])
            fig.text((TX + tw(lab, True)) / W, yc, text, ha="left", va="center", fontsize=FSM)
        elif st in ("cap_t", "cap_w"):
            lab = "True: " if st == "cap_t" else "Wrong: "
            fig.text((TX + tw(lab, True)) / W, yc, text, ha="left", va="center", fontsize=FSM)
        elif st == "dec":
            fig.text(TX / W, yc, text, ha="left", va="center", fontsize=FSM, fontweight="bold")
        elif st == "sum":
            fig.text(TX / W, yc, text, ha="left", va="center", fontsize=FSM)
        else:
            fig.text(TX / W, yc, text, ha="left", va="center", fontsize=FSM - 0.6, color=C["grey"])
        yy += LH
    assert yy - ty <= SZ + 0.02, f"row {x['sel']['kind']}: text block {yy - ty:.2f} in exceeds the panel height {SZ}"
    if i < 2:
        ln_y = 1 - (y0 + SZ + GAP / 2) / H
        fig.add_artist(plt.Line2D([(col_x[0] - 0.22) / W, (W - 0.05) / W], [ln_y, ln_y], color=C["vlgrey"], lw=0.5))

# ---- shared colour bars (one per map type), under columns (c) and (d) -----------------------------------------------------------------------------
yb = TOPM + HDR + 3 * SZ + 2 * GAP + 0.09
CBH = 0.07
for k, (cm, nm, tk, lab) in enumerate([(CM_DELTA, NORM_D, MultipleLocator(1.0), None), (CM_W, NORM_W, None, None)], start=2):
    cax = ax_in(col_x[k], yb, SZ, CBH)
    sm = plt.cm.ScalarMappable(norm=nm, cmap=cm)
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.outline.set_linewidth(0.5)
    cax.tick_params(labelsize=FSM - 0.4, length=2, width=0.5, pad=1.5)
    if k == 2:
        cb.set_ticks([-1, 0, 1])
        cb.set_ticklabels([f"{MINUS}1", "0", "1"])
    else:
        cb.set_ticks([0, 0.1, 0.4, 0.8])
        cb.set_ticklabels(["0", "0.1", "0.4", "0.8"])
note = [
    r"Colour bars are shared by the rows. $\Delta_j>0$ favours the true caption, $\Delta_j<0$ the wrong one.",
    rf"$\Delta_j$ is clipped at $\pm${DMAX:.1f} (99th percentile of $|\Delta_j|$ over the three maps).",
    r"Weights: square-root scale. Maps are the $32\times32$ token grid, not overlaid on the images.",
]
for j, t in enumerate(note):
    fig.text(TX / W, 1 - (yb - 0.045 + j * 0.098) / H, t, ha="left", va="top", fontsize=6.3, color=C["grey"])

S.save(fig, "fig_qualitative")

# ---- trace ------------------------------------------------------------------------------------------------------------------------------------------
payload = dict(
    purpose="Qualitative figure (plan E4): three fresh-fold items under Gaussian noise 0.1, selected by a fixed rule; descriptive only",
    selection_rule="first item in fold-file order (smallest idx in runs/P2-LRF-L1/predictions.jsonl, condition noise0.1) of each kind; decisions are the primary-negative fields y_none and y_lrf (not the _L length-matched fields)",
    kinds=[dict(kind=k[0], definition=k[1]) for k in KINDS],
    fold=dict(run="P2-LRF-L1", folds_path="runs/P2-LRF-FOLD/folds_lrf.json", fold_name="test", n_items=450, condition=COND, sigma=SIGMA),
    items=[dict(kind=x["sel"]["kind"], kind_label=x["sel"]["kind_label"], n_items_of_this_kind_in_fold=x["sel"]["n_items_of_this_kind_in_fold"], idx=x["row"]["idx"], gid=x["row"]["gid"],
                coco_val2017_image_id=x["row"]["image_id"], caption=x["item"]["caption"], neg_caption=x["item"]["neg_caption"],
                fields={k: x["row"][k] for k in ("y_none", "y_lrf", "m_none", "m_lrf", "y_none_L", "y_lrf_L", "m_none_L", "m_lrf_L", "w_sum", "w_mean")},
                sum_delta=x["sum_none"], sum_w_delta=x["sum_lrf"], w_min=float(x["w"].min()), w_max=float(x["w"].max()), delta_min=float(x["delta"].min()), delta_max=float(x["delta"].max()),
                array=f"runs/P2-LRF-L1/arrays/{x['array']}", array_sha256=manifest[x["array"]],
                noisy_pixels_sha256=hashlib.sha256(x["noisy"].tobytes()).hexdigest(), clean_pixels_sha256=hashlib.sha256(x["clean"].tobytes()).hexdigest()) for x in data],
    pixel_regeneration=dict(preprocess="exp_p2.gate.suite.center_crop_512 (copy of UniScorer.preprocess)", corruption="exp_p2.gate.corruptions.apply_pixel('noise', 0.1, pil, exp_p2.run_gate_m3.rung_rng(gid, 'noise', rung))",
                            seed_root=config.SEED_GATE, deterministic_twice=True, vq_token_parity_check="NOT run (needs UniDisc VQ, GPU); same calls as run_gate_m4.build_conditions lines 183-185"),
    weights=dict(source="analysis_posthoc.learned_ceiling.lrf.infer_item on the stored arrays, frozen model runs/P2-LRF-FROZEN-LFIX", model_sha256=MODEL_SHA,
                 recomputed_equal_to_stored=["y_none", "y_lrf", "m_none", "m_lrf", "w_sum", "w_mean"]),
    colour_scales=dict(delta=dict(cmap="vermillion-white-blue (Okabe-Ito)", vmin=-DMAX, vmax=DMAX, rule="99th percentile of |Delta| pooled over the three maps", n_tokens_clipped=n_clipped, n_tokens=int(all_abs.size)),
                       w=dict(cmap="white-to-dark-green sequential", vmin=0.0, vmax=WMAX, norm="PowerNorm gamma 0.5", rule="0 to the largest weight of the three maps")),
    caption_draft=("Descriptive; rows selected by a fixed rule written before the figure was made (first item of each kind in fold order); "
                   "not evidence that the weights track reliability or corruption."),
    attribution="COCO val2017 images (annotations CC BY 4.0; image licences per Flickr terms listed by COCO); ids in items[].coco_val2017_image_id",
)
S.trace("fig_qualitative", "fig_qualitative.py", payload)
print("selected:", [(x["sel"]["kind"], x["row"]["idx"], x["row"]["image_id"], x["row"]["y_none"], x["row"]["y_lrf"]) for x in data], "DMAX", round(DMAX, 3), "WMAX", round(WMAX, 3), "clipped", n_clipped)
