"""Summarise Probe 2 (AUROC per score and corruption, bootstrap over images) and render the example heatmaps (CPU only).
    python -m exp_p2.analyze_probe2 [--run-id P2-PROBE-02]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp_p2 import core, common                                            # noqa: E402

CORRS = ("swap", "patch", "jpeg", "noise")
SCORES = ("s1", "s2", "s3", "r_original", "random")
EXAMPLE_CORR = ("swap", "patch", "jpeg", "noise", "swap", "patch")


def figures(run: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    for j, name in enumerate(EXAMPLE_CORR):
        f = run / "arrays" / f"item{j:04d}.npz"
        if not f.exists():
            continue
        z = np.load(f)
        fig, ax = plt.subplots(2, 4, figsize=(14, 7.4))
        for a_, (t, p) in zip(ax[0, :3], (("original (512 px)", run / "examples" / f"ex{j}_{name}_original.png"),
                                          ("clean VQ reconstruction", run / "examples" / f"ex{j}_{name}_vqrecon.png"),
                                          (f"corrupted: {name}", run / "examples" / f"ex{j}_{name}_corrupted.png"))):
            a_.imshow(Image.open(p))
            a_.set_title(t, fontsize=10)
        ax[0, 3].imshow(z[f"{name}_z"].reshape(32, 32), cmap="gray_r", interpolation="nearest")
        ax[0, 3].set_title(f"true corrupted tokens ({int(z[f'{name}_z'].sum())} of 1024)", fontsize=10)
        for a_, (k, t, flip) in zip(ax[1], (("s1", "s1 = log p(x_i | context, caption)\n(dark = low likelihood)", False),
                                            ("s2", "s2 = s1 - log p(x_i | caption only)", False),
                                            ("s3", "s3 = 1 - max prob (dark = confident)", True),
                                            ("r_original", "r_original = s1 - s1(caption masked)", False))):
            m = z[f"{name}_{k}"].reshape(32, 32)
            im = a_.imshow(m, cmap="viridis_r" if flip else "viridis", interpolation="nearest")
            a_.set_title(t, fontsize=9)
            plt.colorbar(im, ax=a_, fraction=0.046)
        for a_ in ax.ravel():
            a_.set_xticks([])
            a_.set_yticks([])
        fig.suptitle(f"P2-PROBE-02 example {j}: item {j}, corruption {name} (per-token scores on the 32x32 token grid)", fontsize=11)
        fig.tight_layout()
        fig.savefig(run / "examples" / f"ex{j}_{name}_scores.png", dpi=110)
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-PROBE-02")
    a = ap.parse_args()
    run = common.RUNS / a.run_id
    rows = common.read_jsonl(run / "items.jsonl")
    n = len(rows)
    out = dict(run_id=a.run_id, n_items=n, source=str(run / "items.jsonl"), config=json.loads((run / "config.json").read_text(encoding="utf8")), auroc={})
    for c in CORRS:
        per = {s: np.array([r["corr"][c]["auroc"][s] for r in rows], float) for s in SCORES}
        valid = ~np.isnan(per["s1"])
        fr = np.array([r["corr"][c]["frac"] for r in rows])
        out["auroc"][c] = dict(n_images_valid=int(valid.sum()), mean_corrupted_fraction=float(fr.mean()), median_corrupted_fraction=float(np.median(fr)),
                               scores={}, paired_vs_s1={})
        for s in SCORES:
            m, lo, hi = core.bootstrap_mean_ci(per[s][valid], n_boot=10000, seed=0)
            out["auroc"][c]["scores"][s] = dict(mean=m, ci95=[lo, hi])
        for s in ("s2", "s3", "r_original", "random"):
            diff = (per[s] - per["s1"])[valid]
            m, lo, hi = core.bootstrap_mean_ci(diff, n_boot=10000, seed=1)
            out["auroc"][c]["paired_vs_s1"][s] = dict(mean_diff=m, ci95=[lo, hi])
        best = max(("s1", "s2", "s3"), key=lambda s: out["auroc"][c]["scores"][s]["mean"])
        out["auroc"][c]["best_of_s1_s2_s3"] = best
    # pooled AUROC (point estimate only): all tokens of all images
    pooled = {c: {s: None for s in ("s1", "s2", "s3", "r_original")} for c in CORRS}
    zs = {c: [] for c in CORRS}
    sc_ = {c: {s: [] for s in ("s1", "s2", "s3", "r_original")} for c in CORRS}
    for r in rows:
        f = run / "arrays" / f"item{r['idx']:04d}.npz"
        z = np.load(f)
        for c in CORRS:
            zs[c].append(z[f"{c}_z"])
            for s in sc_[c]:
                sc_[c][s].append(z[f"{c}_{s}"])
    for c in CORRS:
        zc = np.concatenate(zs[c])
        for s in sc_[c]:
            v = np.concatenate(sc_[c][s]).astype(np.float64)
            pooled[c][s] = core.auroc(v if s == "s3" else -v, zc)
    out["pooled_auroc_point_estimates"] = pooled
    sec = np.array([r["seconds"] for r in rows])
    out["cost"] = dict(seconds_per_item_mean=float(sec.mean()), seconds_per_item_median=float(np.median(sec)), peak_vram_gb_max=float(max(r["peak_gb"] for r in rows)),
                       gpu_busy_hours_items=float(sec.sum() / 3600))
    (run / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf8")
    for c in CORRS:
        o = out["auroc"][c]
        print(f"{c:6s} valid={o['n_images_valid']} frac={o['mean_corrupted_fraction']:.3f} best={o['best_of_s1_s2_s3']}")
        for s in SCORES:
            v = o["scores"][s]
            print(f"   {s:11s} {v['mean']:.3f} [{v['ci95'][0]:.3f},{v['ci95'][1]:.3f}]")
    print("cost", out["cost"])
    figures(run)


if __name__ == "__main__":
    main()
