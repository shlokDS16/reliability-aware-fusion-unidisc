"""E1 analysis (EXPLORATORY-PLAN-BASELINES-2026-10-30.md): pixel denoiser (Study 1's S-DN, OpenCV NLM) before scoring, on the Study 2 fresh fold. CPU only; no model, no GPU.

    "C:/.../.venv/Scripts/python.exe" -m analysis.paper2.lrf.e1_denoise [--dn-run runs/P2-LRF-DN] [--l1-run runs/P2-LRF-L1] [--out runs/P2-LRF-DN/dn_analysis.json]

Inputs: `<dn-run>/predictions.jsonl` (written by `python -m exp_p2.gate.lrf_score --run-id P2-LRF-DN --pins runs/P2-LRF-PINS/pins.json --conds noise0.1_nlm,jpeg10_nlm`; conditions
`noise0.1_nlm` and `jpeg10_nlm`) and `<l1-run>/predictions.jsonl` (conditions `noise0.1`, `jpeg10`; the undenoised NONE and LRF). Items are matched by idx; idx, gid and image_id must agree.
Arms: DN+NONE = `y_none` of the denoised condition (unweighted sum of per-token evidence), DN+LRF = `y_lrf` (frozen LRF, unchanged). References: NONE = `y_none`, LRF = `y_lrf` of the same idx
and condition in L1. Primary negative (`y_*`); the length-matched negative (`y_*_L`) is reported in `length_matched` when every row has it.
Reporting: accuracy of each arm; paired difference arm minus reference = (b - c) / n with discordant counts b (arm right, reference wrong) and c (arm wrong, reference right); 95 percent paired
percentile bootstrap interval (10,000 resamples of items; one index matrix per condition from numpy.random.SeedSequence(0), shared by every contrast of the cell, as analysis/paper2/lrf/e2_combiners.py;
numpy.quantile 0.025 and 0.975). No p-value, no test, no multiplicity claim. Optional corruption check: if the DN run's arrays hold `<cond>_nlm_codes_corr`, they are compared with L1's stored
`<cond>_codes` (the same corruption seed must give the same corrupted image; reported, not a gate)."""
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

from exp_p2.gate import tier3_fusion as T3                                             # noqa: E402

CONDS = ("noise0.1", "jpeg10")                    # the two S-DN conditions; keys as in runs/P2-LRF-L1/predictions.jsonl
SUFFIX = "_nlm"
N_BOOT = 10000
SEED = 0
LABEL = "exploratory (EXPLORATORY-PLAN-BASELINES-2026-10-30.md E1); no p-value, no test, no multiplicity claim; added after the preregistered Study 2 results"


def paired(ya: np.ndarray, yr: np.ndarray, idx: np.ndarray) -> dict:
    """Arm minus reference over the same items: (b - c) / n, discordant counts, 95 percent percentile bootstrap interval of the mean difference."""
    diff = np.asarray(ya, np.int8) - np.asarray(yr, np.int8)
    n = int(diff.size)
    b, c = int((diff == 1).sum()), int((diff == -1).sum())
    boots = diff[idx].mean(axis=1)
    return dict(diff=(b - c) / n, b=b, c=c, ci95=[float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))])


def load(path: Path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def _rows(lines: list[dict], cond: str) -> dict[int, dict]:
    out = {}
    for x in lines:
        if x["condition"] == cond:
            if x["idx"] in out:
                raise RuntimeError(f"duplicate row for condition {cond} idx {x['idx']}")
            out[x["idx"]] = x
    if not out:
        raise RuntimeError(f"no prediction rows for condition {cond}")
    return out


def cell(dn: dict[int, dict], l1: dict[int, dict], suffix: str, idx_mat_cache: dict) -> dict:
    ids = sorted(dn)
    if ids != sorted(l1):
        raise RuntimeError(f"the item sets differ: {len(ids)} denoised rows, {len(l1)} L1 rows")
    for i in ids:
        if (dn[i]["gid"], dn[i]["image_id"]) != (l1[i]["gid"], l1[i]["image_id"]):
            raise RuntimeError(f"idx {i}: gid or image_id differ between the denoised run and L1")
    n = len(ids)
    if n not in idx_mat_cache:
        idx_mat_cache[n] = T3.index_matrix(n, np.random.SeedSequence(SEED), N_BOOT)
    idx = idx_mat_cache[n]
    y = lambda rows, key: np.array([int(rows[i][key]) for i in ids], np.int8)          # noqa: E731
    dn_none, dn_lrf = y(dn, "y_none" + suffix), y(dn, "y_lrf" + suffix)
    none, lrf = y(l1, "y_none" + suffix), y(l1, "y_lrf" + suffix)
    return dict(n=n, arms={
        "NONE": dict(acc=float(none.mean())),
        "LRF": dict(acc=float(lrf.mean())),
        "DN+NONE": dict(acc=float(dn_none.mean()), vs_NONE=paired(dn_none, none, idx), vs_LRF=paired(dn_none, lrf, idx)),
        "DN+LRF": dict(acc=float(dn_lrf.mean()), vs_NONE=paired(dn_lrf, none, idx), vs_LRF=paired(dn_lrf, lrf, idx), vs_DN_NONE=paired(dn_lrf, dn_none, idx))})


def corruption_check(dn_run: Path, l1_run: Path, ids: list[int], cond: str) -> dict:
    """Fraction of token codes of the corrupted-but-not-denoised image (DN run) equal to L1's stored `<cond>_codes`; None if the DN arrays do not hold them."""
    eq_tokens = items_equal = n = 0
    for i in ids:
        pd, pl = dn_run / "arrays" / f"item{i:04d}.npz", l1_run / "arrays" / f"item{i:04d}.npz"
        if not (pd.exists() and pl.exists()):
            return dict(checked=False, reason="arrays missing")
        with np.load(pd) as zd, np.load(pl) as zl:
            if f"{cond}{SUFFIX}_codes_corr" not in zd.files or f"{cond}_codes" not in zl.files:
                return dict(checked=False, reason="codes_corr not stored")
            a, b = zd[f"{cond}{SUFFIX}_codes_corr"], zl[f"{cond}_codes"]
        eq_tokens += int((a == b).sum())
        items_equal += int((a == b).all())
        n += 1
    return dict(checked=True, n_items=n, token_equal_fraction=eq_tokens / (n * 1024) if n else None, items_all_tokens_equal=items_equal)


def analyse(dn_run: Path, l1_run: Path) -> dict:
    dn_run, l1_run = Path(dn_run), Path(l1_run)
    dn_lines, l1_lines = load(dn_run / "predictions.jsonl"), load(l1_run / "predictions.jsonl")
    cells, cache, lm_cache = {}, {}, {}
    for cond in CONDS:
        dn, l1 = _rows(dn_lines, cond + SUFFIX), _rows(l1_lines, cond)
        c = cell(dn, l1, "", cache)
        if all(r.get("y_lrf_L") is not None for r in list(dn.values()) + list(l1.values())):
            c["length_matched"] = cell(dn, l1, "_L", lm_cache)
        c["corruption_reproduction"] = corruption_check(dn_run, l1_run, sorted(dn), cond)
        cells[cond] = c
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()                    # noqa: E731
    rel = lambda p: str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)       # noqa: E731
    return dict(
        label=LABEL, plan="research/paper2/tnnls/EXPLORATORY-PLAN-BASELINES-2026-10-30.md E1",
        definitions="DN+NONE = y_none and DN+LRF = y_lrf of the denoised condition (OpenCV fastNlMeansDenoisingColored, config.DENOISE_PARAMS, unchanged; frozen LRF unchanged and out of its training distribution on denoised images); "
                    "NONE and LRF = y_none and y_lrf of the same idx and condition in runs/P2-LRF-L1 (primary negative)",
        sign="differences are arm minus reference; positive favours the arm; b = arm right and reference wrong, c = arm wrong and reference right",
        bootstrap=dict(n_boot=N_BOOT, seed="numpy.random.SeedSequence(0), one index matrix per condition shared by all contrasts", interval="percentile, numpy.quantile 0.025 and 0.975", unit="items"),
        inputs=dict(dn_predictions=rel(dn_run / "predictions.jsonl"), dn_predictions_sha256=sha(dn_run / "predictions.jsonl"),
                    l1_predictions=rel(l1_run / "predictions.jsonl"), l1_predictions_sha256=sha(l1_run / "predictions.jsonl"), numpy=np.__version__),
        cells=cells, conditions=list(CONDS), arms=["NONE", "LRF", "DN+NONE", "DN+LRF"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dn-run", default=str(ROOT / "runs" / "P2-LRF-DN"))
    ap.add_argument("--l1-run", default=str(ROOT / "runs" / "P2-LRF-L1"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else Path(a.dn_run) / "dn_analysis.json"
    try:
        res = analyse(Path(a.dn_run), Path(a.l1_run))
    except (RuntimeError, FileNotFoundError, KeyError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    for cond, c in res["cells"].items():
        print(cond, {k: round(v["acc"], 4) for k, v in c["arms"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
