"""F9: real output. Selection rule fixed before looking (outcome-blind): M4 items 0, 1, 2 by index (runs/P2-GATE-M4/items.jsonl, field idx), with the corruption
assigned by position: item 0 JPEG (quality 10), item 1 Gaussian noise (sigma 0.1), item 2 splice (128 px).
Per row: clean 512 px image (exp_p2.common.load_image + the centre-crop/512 preprocessing of detect.preprocess512), the corrupted image regenerated with the pinned
exp_p2.gate.corruptions.apply_pixel and the M3/M4 seeds (run_gate_m3.rung_rng, donor_for), and the 32 x 32 token map from runs/P2-GATE-M4/arrays/item<idx>.npz:
changed tokens z (key <cond>_z, tinted vermillion) and gate-flagged tokens at alpha 0.05 (key <cond>_flag0.05, blue outline). Counts are computed from those arrays.
Read-only: no model, no GPU (CUDA hidden), no decoding of re-infilled images, nothing under runs/P2-GATE-S2* is opened."""
from __future__ import annotations

import json
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import PatchCollection  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

import style as S  # noqa: E402
from style import COL  # noqa: E402

sys.path.insert(0, str(S.REPO))
from types import SimpleNamespace  # noqa: E402

from exp_p2 import common  # noqa: E402
from exp_p2.gate import config, corruptions, detect  # noqa: E402
from exp_p2.run_gate_m3 import donor_for, rung_rng  # noqa: E402

S.apply()
RUN = S.REPO / "runs" / "P2-GATE-M4"
rows = {}
for line in open(RUN / "items.jsonl", encoding="utf-8"):
    r = json.loads(line)
    rows.setdefault(r["idx"], r)
fold = [rows[i] for i in sorted(rows)]
assert len(fold) == 500

SEL = [(0, "jpeg", 10, "jpeg10", "JPEG, quality 10"), (1, "noise", 0.1, "noise0.1", "Gaussian noise, $\\sigma=0.1$"),
       (2, "splice", 128, "splice128", "splice, 128 px region")]
G = 32


def gray_faded(arr):
    g = arr.astype(np.float32).mean(axis=2, keepdims=True)
    g = 255 - 0.55 * (255 - g)
    return np.repeat(g, 3, axis=2).clip(0, 255).astype(np.uint8)


s, gap, LEFT = 48.0, 6.0, 25.0
W = S.W2
rowh = s + 14.0
H = 12.0 + 3 * rowh + 8.0
fig, ax = S.canvas(W, H)
stats = []
for r_i, (idx, corr, sev, key, lab) in enumerate(SEL):
    it = rows[idx]
    pil = detect.preprocess512(common.load_image(it["image_id"]))
    r = list(config.LADDERS[corr]).index(sev)
    donor = donor_for(SimpleNamespace(fold=fold), SimpleNamespace(preprocess=detect.preprocess512), it) if corr == "splice" else None
    img = corruptions.apply_pixel(corr, sev, pil, rung_rng(it["gid"], corr, r), donor)
    clean = np.asarray(pil)
    cor = np.asarray(img)
    z = np.load(RUN / "arrays" / f"item{idx:04d}.npz")
    zz, ff = z[f"{key}_z"].reshape(G, G), z[f"{key}_flag0.05"].reshape(G, G)
    n_z, n_f, n_tp = int(zz.sum()), int(ff.sum()), int((zz & ff).sum())
    cond = it["conds"][key]
    assert n_z == cond["n_changed"] and n_f == cond["gate"]["0.05"]["n_flag"] and n_tp == cond["gate"]["0.05"]["n_tp"], (idx, key)
    # consistency of the regenerated pixels with the stored labels: share of 16 px blocks with any pixel change, among changed / unchanged tokens
    blk = (np.abs(cor.astype(int) - clean.astype(int)).sum(axis=2) > 0).reshape(G, 16, G, 16).any(axis=(1, 3))
    stats.append(dict(item=idx, cond=key, n_changed=n_z, n_flagged=n_f, flagged_and_changed=n_tp, flagged_unchanged=n_f - n_tp,
                      pixel_block_changed=int(blk.sum()), z_in_pixel_changed=int((zz & blk).sum()), z_outside_pixel_changed=int((zz & ~blk).sum())))
    ytop = H - 12.0 - r_i * rowh
    y0 = ytop - s
    xs = [LEFT + k * (s + gap) for k in range(3)]
    ax.imshow(clean, extent=(xs[0], xs[0] + s, y0, ytop), origin="upper", interpolation="bilinear", zorder=1)
    ax.imshow(cor, extent=(xs[1], xs[1] + s, y0, ytop), origin="upper", interpolation="nearest", zorder=1)
    ax.imshow(gray_faded(cor), extent=(xs[2], xs[2] + s, y0, ytop), origin="upper", interpolation="bilinear", zorder=1)
    rgba = np.zeros((G, G, 4), np.float32)
    rgba[zz] = (*[int(COL["corrupt"][i:i + 2], 16) / 255 for i in (1, 3, 5)], 0.42)
    ax.imshow(rgba, extent=(xs[2], xs[2] + s, y0, ytop), origin="upper", interpolation="nearest", zorder=2)
    cs = s / G
    pats = [Rectangle((xs[2] + c * cs, ytop - (rr + 1) * cs), cs, cs) for rr, c in zip(*np.nonzero(ff))]
    ax.add_collection(PatchCollection(pats, facecolor="none", edgecolor=COL["flag"], linewidth=0.55, zorder=4))
    for x in xs:
        ax.add_patch(Rectangle((x, y0), s, s, facecolor="none", edgecolor=COL["ink"], linewidth=0.5, zorder=5))
    ax.text(LEFT - 3.0, ytop - 3.0, f"item {idx}", fontsize=7.5, weight="bold", ha="right", va="center")
    ax.text(LEFT - 3.0, ytop - 7.0, f"COCO {it['image_id']}", fontsize=6.2, color=COL["sub"], ha="right", va="center")
    ax.text(xs[0], y0 - 2.6, "clean image", fontsize=6.8, va="center")
    ax.text(xs[1], y0 - 2.6, f"corrupted: {lab}", fontsize=6.8, va="center")
    ax.text(xs[2], y0 - 2.6, f"changed {n_z} of {G * G}", fontsize=6.8, va="center")
    ax.text(xs[2], y0 - 6.2, f"flagged {n_f}: {n_tp} changed, {n_f - n_tp} unchanged", fontsize=6.4, va="center", color=COL["flag"])
    if r_i == 0:
        ax.text(xs[2], ytop + 2.4, "token map ($32\\times32$) on the corrupted image", fontsize=6.8, weight="bold", va="center")
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ly = 2.2
ax.add_patch(Rectangle((LEFT, ly), 2.8, 2.8, facecolor="#E3E3E3", edgecolor="none", zorder=2))
ax.add_patch(Rectangle((LEFT, ly), 2.8, 2.8, facecolor=COL["corrupt"], alpha=0.42, edgecolor=COL["clean_edge"], linewidth=0.5, zorder=3))
ax.text(LEFT + 3.9, ly + 1.4, "changed token ($Z_j=1$), tint", fontsize=6.6, va="center")
ax.add_patch(Rectangle((LEFT + 52.0, ly), 2.8, 2.8, facecolor="#E3E3E3", edgecolor=COL["flag"], linewidth=1.0, zorder=3))
ax.text(LEFT + 55.9, ly + 1.4, r"gate-flagged token ($j\in G$, $\alpha=0.05$), outline", fontsize=6.6, va="center")
S.save(fig, "F9_real_outputs")
print(json.dumps(stats, indent=0))
