"""Summarise Probe 1 from runs/<run-id>/items.jsonl into summary.json (CPU only).  python -m exp_p2.analyze_probe1 [--run-id P2-PROBE-01]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp_p2 import core, common                                            # noqa: E402

# name -> (function of (true, mis) row dicts giving the score difference true - mismatched, label, status)
def d(key):
    return lambda t, m: t[key] - m[key]


def pmi(key, null):
    return lambda t, m: (t[key] - t[null]) - (m[key] - m[null])


PRIMARY = {
    "a_text": (d("a8"), "mean log p(caption tokens | image), K=8 complementary masks, image visible"),
    "b_image": (d("b8"), "mean log p(image tokens | caption), K=8 complementary masks, caption visible"),
    "a_plus_b": (lambda t, m: (t["a8"] + t["b8"]) - (m["a8"] + m["b8"]), "sum of the two per-token mean log-likelihoods"),
}
SUPPL = {
    "ctrl_text_only": (d("a8null"), "CONTROL: a_text with the whole image masked (caption prior only, no image information)"),
    "a_pmi": (pmi("a8", "a8null"), "text direction minus its image-masked null (same text masks)"),
    "a_full": (d("afull"), "all caption tokens masked in one pass, image visible"),
    "a_full_pmi": (pmi("afull", "afull_null"), "a_full minus the same pass with the image masked"),
    "b_k2": (d("b2"), "image direction, K=2 complementary passes (50 percent masked)"),
    "b_full": (d("bfull"), "image direction, all 1024 image tokens masked in one pass"),
    "a_pmi_plus_b": (lambda t, m: ((t["a8"] - t["a8null"]) + t["b8"]) - ((m["a8"] - m["a8null"]) + m["b8"]), "a_pmi + b_image"),
    "a_full_pmi_plus_b_full": (lambda t, m: ((t["afull"] - t["afull_null"]) + t["bfull"]) - ((m["afull"] - m["afull_null"]) + m["bfull"]), "a_full_pmi + b_full"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-PROBE-01")
    a = ap.parse_args()
    run = common.RUNS / a.run_id
    rows = common.read_jsonl(run / "items.jsonl")
    n = len(rows)
    out = dict(run_id=a.run_id, n_items=n, source=str(run / "items.jsonl"), config=json.loads((run / "config.json").read_text(encoding="utf8")))
    res = {}
    for group, table in (("primary", PRIMARY), ("supplementary_exploratory", SUPPL)):
        res[group] = {}
        for name, (fn, label) in table.items():
            diff = np.array([fn(r["true"], r["mis"]) for r in rows])
            ind = core.match_indicator(diff, np.zeros_like(diff))
            acc, lo, hi = core.bootstrap_mean_ci(ind, n_boot=10000, seed=0)
            res[group][name] = dict(label=label, accuracy=acc, ci95=[lo, hi], mean_diff=float(diff.mean()), median_diff=float(np.median(diff)),
                                    n_true_greater=int((diff > 0).sum()), n=n)
    out["results"] = res
    kill_a, kill_b = res["primary"]["a_text"]["accuracy"], res["primary"]["b_image"]["accuracy"]
    out["kill_criterion"] = dict(rule="both directions <= 0.55", a_text=kill_a, b_image=kill_b, met=bool(kill_a <= 0.55 and kill_b <= 0.55),
                                 upper_ci_a=res["primary"]["a_text"]["ci95"][1], upper_ci_b=res["primary"]["b_image"]["ci95"][1])
    sec = np.array([r["seconds"] for r in rows])
    out["cost"] = dict(seconds_per_item_mean=float(sec.mean()), seconds_per_item_median=float(np.median(sec)), seconds_per_item_max=float(sec.max()),
                       passes_per_item=int(rows[0]["true"]["n_passes"] + rows[0]["mis"]["n_passes"]), peak_vram_gb_max=float(max(r["peak_gb"] for r in rows)),
                       gpu_busy_hours_items=float(sec.sum() / 3600))
    nt = np.array([r["true"]["n_tok"] for r in rows])
    nm = np.array([r["mis"]["n_tok"] for r in rows])
    out["caption_tokens"] = dict(true_mean=float(nt.mean()), mismatched_mean=float(nm.mean()))
    (run / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf8")
    for g in res:
        for k, v in res[g].items():
            print(f"{g:28s} {k:24s} acc={v['accuracy']:.3f} [{v['ci95'][0]:.3f},{v['ci95'][1]:.3f}] mean_diff={v['mean_diff']:+.3f}")
    print("kill:", out["kill_criterion"])
    print("cost:", out["cost"])


if __name__ == "__main__":
    main()
