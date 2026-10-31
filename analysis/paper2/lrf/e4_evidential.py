"""E4 (research/paper2/tnnls/EXPLORATORY-PLAN-EVIDENTIAL-2026-10-31.md): Dempster combination of evidence-derived token opinions on the Study 2 fresh fold. CPU only; no model, no GPU.

    "C:/.../.venv/Scripts/python.exe" -I -m analysis.paper2.lrf.e4_evidential [--run-dir runs/P2-LRF-L1] [--out runs/P2-LRF-E4/evidential.json]

Per token: e+ = lam max(Delta, 0), e- = lam max(-Delta, 0), S = e+ + e- + 2, b+ = e+/S, b- = e-/S; Shafer discount r (1 = none, or 1 - rank_s3 = the A-UNL weight);
Dempster's rule multiplies the commonalities q(+) = 1 - r b-, q(-) = 1 - r b+, so the decision is D = sum_j [log q(+) - log q(-)] > 0 (tie wrong). Primary arm: lam 1, A-UNL discount.
Consistency gate (before anything is written): NONE recomputed from `<cond>_delta` equals `y_none` of predictions.jsonl for every item and condition, and A-UNL recomputed from `<cond>_s3`
reproduces the stored A-UNL accuracy (runs/P2-LRF-ABL-SCORE/ablation_analysis.json rows[A-UNL].cells.L1_<cond>.acc). Reporting as e2_combiners.py: accuracy, paired difference against NONE,
A-UNL and LRF, (b - c)/n, discordant counts, 95 percent percentile bootstrap (10,000 item resamples, SeedSequence(0), one index matrix per condition shared by all arms). No test."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2.gate import tier3_fusion as T3                                            # noqa: E402

CONDS = ("noise0.1", "jpeg10", "splice128", "clean")
LAMS = (1.0, 0.1, 10.0)
PRIMARY = "DS-l1-disc"
N_BOOT, SEED = 10000, 0
LABEL = "exploratory (EXPLORATORY-PLAN-EVIDENTIAL-2026-10-31.md E4); no p-value, no test, no multiplicity claim; added after the preregistered Study 2 results"


def rank(a: np.ndarray) -> np.ndarray:
    """Within-item percentile rank over the last axis (0..1): analysis_posthoc/learned_ceiling/data._rank, verbatim."""
    return (np.argsort(np.argsort(a, axis=-1), axis=-1) / (a.shape[-1] - 1)).astype(np.float32)


def ds_score(delta: np.ndarray, r: np.ndarray, lam: float) -> float:
    d = np.asarray(delta, np.float64)
    ep, em = lam * np.maximum(d, 0.0), lam * np.maximum(-d, 0.0)
    S = ep + em + 2.0
    bp, bm = ep / S, em / S
    r = np.asarray(r, np.float64)
    return float(np.sum(np.log1p(-r * bm) - np.log1p(-r * bp)))


def arm_name(lam: float, disc: bool) -> str:
    return f"DS-l{lam:g}-{'disc' if disc else 'nodisc'}"


def paired(ya, yr, idx) -> dict:
    d = np.asarray(ya, np.int8) - np.asarray(yr, np.int8)
    n, b, c = int(d.size), int((d == 1).sum()), int((d == -1).sum())
    boots = d[idx].mean(axis=1)
    return dict(diff=(b - c) / n, b=b, c=c, ci95=[float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))])


def analyse(run_dir: Path, abl_path: Path) -> dict:
    lines = [json.loads(l) for l in open(run_dir / "predictions.jsonl", encoding="utf-8") if l.strip()]
    abl = json.loads(abl_path.read_text(encoding="utf-8"))
    unl = next(r for r in abl["rows"] if r["id"] == "A-UNL")["cells"]
    cells, absd = {}, []
    for cond in CONDS:
        rows = sorted((x for x in lines if x["condition"] == cond), key=lambda x: x["idx"])
        n = len(rows)
        ys = {k: [] for k in ["NONE", "LRF", "A-UNL"] + [arm_name(l, dsc) for l in LAMS for dsc in (True, False)]}
        for x in rows:
            with np.load(run_dir / "arrays" / f"item{x['idx']:04d}.npz") as z:
                delta, s3 = z[f"{cond}_delta"].astype(np.float64), z[f"{cond}_s3"].astype(np.float32)
            y_none = int(delta.mean() > 0)
            if y_none != int(x["y_none"]):
                raise RuntimeError(f"gate: NONE recomputed != y_none (cond {cond}, idx {x['idx']})")
            w = 1.0 - rank(s3).astype(np.float64)
            ys["NONE"].append(y_none)
            ys["LRF"].append(int(x["y_lrf"]))
            ys["A-UNL"].append(int(np.sum(w * delta) > 0))
            for lam in LAMS:
                ys[arm_name(lam, True)].append(int(ds_score(delta, w, lam) > 0))
                ys[arm_name(lam, False)].append(int(ds_score(delta, np.ones_like(delta), lam) > 0))
            absd.append(np.abs(delta))
        acc_unl = float(np.mean(ys["A-UNL"]))
        if abs(acc_unl - unl[f"L1_{cond}"]["acc"]) > 1e-12:
            raise RuntimeError(f"gate: A-UNL recomputed {acc_unl} != stored {unl[f'L1_{cond}']['acc']} ({cond})")
        idx = T3.index_matrix(n, np.random.SeedSequence(SEED), N_BOOT)
        arms = {}
        for k, y in ys.items():
            a = dict(acc=float(np.mean(y)))
            if k.startswith("DS"):
                a.update(vs_NONE=paired(y, ys["NONE"], idx), vs_A_UNL=paired(y, ys["A-UNL"], idx), vs_LRF=paired(y, ys["LRF"], idx))
            arms[k] = a
        cells[cond] = dict(n=n, arms=arms)
    allabs = np.concatenate(absd)
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()                    # noqa: E731
    return dict(label=LABEL, plan="research/paper2/tnnls/EXPLORATORY-PLAN-EVIDENTIAL-2026-10-31.md", primary=PRIMARY,
                definitions="DS-l<lam>-disc: lam = evidence scale, discount r = 1 - rank_s3 (A-UNL weight); -nodisc: r = 1. Decision sum_j[log(1 - r b-) - log(1 - r b+)] > 0, tie wrong",
                consistency_gate=dict(none_matches_y_none=True, a_unl_matches_stored=True),
                bootstrap=dict(n_boot=N_BOOT, seed="numpy.random.SeedSequence(0), one index matrix per condition shared by all arms", interval="percentile 0.025/0.975", unit="items"),
                abs_delta_descriptive=dict(median=float(np.median(allabs)), p95=float(np.quantile(allabs, 0.95)), note="read after the accuracies were written; feeds no choice"),
                inputs=dict(predictions_sha256=sha(run_dir / "predictions.jsonl"), ablation_sha256=sha(abl_path), numpy=np.__version__),
                cells=cells)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default=str(ROOT / "runs" / "P2-LRF-L1"))
    ap.add_argument("--abl", default=str(ROOT / "runs" / "P2-LRF-ABL-SCORE" / "ablation_analysis.json"))
    ap.add_argument("--out", default=str(ROOT / "runs" / "P2-LRF-E4" / "evidential.json"))
    a = ap.parse_args(argv)
    try:
        res = analyse(Path(a.run_dir), Path(a.abl))
    except (RuntimeError, FileNotFoundError, KeyError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    for cond, c in res["cells"].items():
        print(cond, {k: round(v["acc"], 4) for k, v in c["arms"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
