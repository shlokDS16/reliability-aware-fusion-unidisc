"""Detection analysis of M1 / the CPU fallback (v2 sections 7.6, 11.4): per-item AUROC of every score against the changed-code map Z, per corruption, and the
paired bootstrap of q against the best cheap baseline. Works on probe-2 arrays alone (no q, no TbV: labelled exploratory) or with the M1 post-hoc arrays.

Probe-2 array keys (run_probe2.py): clean, and per corruption c in (swap, patch, jpeg, noise): c_s1, c_s2, c_s3, c_r_original, c_codes, c_z.
B (caption masked, same masks) = s1 - r_original.  q = B - D with D from run_gate_m1 (c_D).  Suspicions (higher = more suspicious):
  s1 -> -s1, s2 -> -s2, s3, r_original -> -r_original, plainB -> -B, q -> -(B - D), tbv -> -log p(observed | nothing masked), random (probe 2's own draw),
  tex (pixel patch variance), nbr (neighbour codebook distance), rarity (code rarity).
Items with fewer than 5 corrupted or 5 clean tokens are excluded for that corruption (as run_probe2) and counted.
Pixel baselines are regenerated deterministically on the CPU (probe 2's own seeds): jpeg q10 and noise sigma 0.1 on the preprocessed image; swap and patch have no pixel
image (texture = NaN, reported as not applicable)."""
from __future__ import annotations

import numpy as np

from exp_p2 import core
from exp_p2.gate import baselines, corruptions

P2_SEED = 20261028
P2_CORRS = ("swap", "patch", "jpeg", "noise")
CHEAP = ("tex", "nbr", "rarity", "s3", "plainB", "tbv")          # candidates for 'best cheap baseline' (random and r_original are controls, not rivals)
GRID, PATCH_PX = 32, 16


def preprocess512(pil):
    """Copy of UniScorer.preprocess (centre square crop, bicubic to 512): needed to regenerate pixels without a model."""
    from PIL import Image
    w, h = pil.size
    s = min(w, h)
    l, t = (w - s) // 2, (h - s) // 2
    return pil.convert("RGB").crop((l, t, l + s, t + s)).resize((512, 512), Image.BICUBIC)


def regen_pixels(pil_raw, i: int, corr: str):
    """Observed pixels of probe 2 item i under `corr` as uint8 [512,512,3], or None for token-level corruptions."""
    if corr not in ("jpeg", "noise"):
        return None
    pil = preprocess512(pil_raw)
    ci = P2_CORRS.index(corr)
    if corr == "jpeg":
        img = corruptions.jpeg(pil, 10)
    else:
        img = corruptions.gaussian_noise(pil, 0.1, np.random.default_rng([P2_SEED, i, ci]))
    return np.asarray(img)


def suspicions(arr, corr: str, i: int, m1=None, extra: dict | None = None) -> dict[str, np.ndarray]:
    m = len(arr[f"{corr}_s1"])
    s1, r = np.asarray(arr[f"{corr}_s1"], np.float32), np.asarray(arr[f"{corr}_r_original"], np.float32)
    B = s1 - r
    ci = P2_CORRS.index(corr)
    out = dict(s1=-s1, s2=-np.asarray(arr[f"{corr}_s2"], np.float32), s3=np.asarray(arr[f"{corr}_s3"], np.float32), r_original=-r, plainB=-B,
               random=np.random.default_rng([P2_SEED, i, 50 + ci]).random(m))
    if m1 is not None and f"{corr}_D" in m1:
        out["q"] = -(B - np.asarray(m1[f"{corr}_D"], np.float32))
    if m1 is not None and f"{corr}_tbv" in m1:
        out["tbv"] = -np.asarray(m1[f"{corr}_tbv"], np.float32)
    if extra:
        out.update(extra)
    return out


def item_aurocs(sus: dict, z: np.ndarray, min_class: int = 5) -> dict:
    n_c, m = int(z.sum()), len(z)
    ok = min_class <= n_c <= m - min_class
    return {k: (core.auroc(v, z) if ok and not np.isnan(v).any() else float("nan")) for k, v in sus.items()} | {"_eligible": float(ok), "_n_corrupted": float(n_c)}


def aggregate(per_item: list[dict], n_boot: int = 10000, seed: int = 0) -> dict:
    """per_item: list of {corr: {score: auroc, _eligible, _n_corrupted}}. -> {corr: {score: dict(mean, lo, hi, n)}, _excluded: ...}."""
    out: dict = {}
    for corr in P2_CORRS:
        rows = [p[corr] for p in per_item if corr in p]
        if not rows:
            continue
        names = sorted({k for r in rows for k in r if not k.startswith("_")})
        out[corr] = {n: dict(zip(("mean", "lo", "hi"), core.bootstrap_mean_ci(np.array([r.get(n, np.nan) for r in rows]), n_boot, seed)),
                             n=int(np.sum(~np.isnan([r.get(n, np.nan) for r in rows])))) for n in names}
        out[corr]["_n_items"] = len(rows)
        out[corr]["_n_excluded"] = int(sum(1 for r in rows if not r["_eligible"]))
    return out


def paired_vs_best_cheap(per_item: list[dict], corr: str, target: str = "q", cheap=CHEAP, n_boot: int = 10000, seed: int = 0) -> dict:
    """Per-item AUROC of `target` minus that of the cheap baseline with the highest mean AUROC on this corruption; bootstrap CI over items.
    Falsifier (v2 7.6): the CI does not exclude 0 on jpeg AND noise."""
    rows = [p[corr] for p in per_item if corr in p]
    cand = [c for c in cheap if any(not np.isnan(r.get(c, np.nan)) for r in rows)]
    if not rows or not cand or not any(not np.isnan(r.get(target, np.nan)) for r in rows):
        return dict(corr=corr, available=False)
    means = {c: float(np.nanmean([r.get(c, np.nan) for r in rows])) for c in cand}
    best = max(means, key=means.get)
    a = np.array([r.get(target, np.nan) for r in rows])
    b = np.array([r.get(best, np.nan) for r in rows])
    m, lo, hi = core.bootstrap_mean_ci(a - b, n_boot, seed)
    return dict(corr=corr, available=True, target=target, best_cheap=best, cheap_means=means, diff_mean=m, diff_lo=lo, diff_hi=hi, excludes_zero=bool(lo > 0 or hi < 0))


def falsifier(per_item: list[dict], target: str = "q", n_boot: int = 10000, seed: int = 0) -> dict:
    """v2 7.6 read literally: falsified when the paired CI of (AUROC of q minus best cheap baseline) does not exclude 0 on jpeg AND on noise.
    `q_significantly_better_on` and `q_significantly_worse_on` are reported so a CI that excludes 0 on the wrong side is not hidden."""
    res = {c: paired_vs_best_cheap(per_item, c, target, n_boot=n_boot, seed=seed) for c in ("jpeg", "noise")}
    if not all(r.get("available") for r in res.values()):
        return dict(per_corruption=res, falsified=None, note="needs q (M1 post-hoc arrays) and a cheap baseline on both jpeg and noise")
    return dict(per_corruption=res, falsified=bool(not any(r["excludes_zero"] for r in res.values())),
                q_significantly_better_on=[c for c, r in res.items() if r["excludes_zero"] and r["diff_mean"] > 0],
                q_significantly_worse_on=[c for c, r in res.items() if r["excludes_zero"] and r["diff_mean"] < 0],
                rule="v2 7.6: falsified when the paired CI of (AUROC q minus best cheap) does not exclude 0 on jpeg and on noise")
