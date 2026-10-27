"""CPU step after M2: fit the conformal-risk-control thresholds on the 300 calibration items (v2 section 6).

    python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2 [--statistic q|plainB]

Reads runs/<run>/arrays/item*.npz (B, D per item, written by run_gate_m2) and items.jsonl; writes runs/<run>/threshold.json with one Threshold per alpha in
{0.05, 0.01, 0.10} (primary first; the others are sensitivity, not selected), the shared jitter scale eps0 (half the smallest non-zero gap of the pooled
calibration suspicions), the id hash, and the in-sample calibration risk; also codefreq.npy (clean-code counts for the code-rarity baseline).
Mandatory wording for the paper: 'The threshold is calibrated so that, for a clean test pair exchangeable with the calibration pairs, the expected proportion
of its tokens that are flagged is at most alpha.' Nothing stronger."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import artifacts, baselines, calibrate as cal, config, scores         # noqa: E402


def suspicion_from_arrays(arr, statistic: str) -> np.ndarray:
    if statistic == "q":
        return scores.suspicion_q(arr["B"], arr["D"])
    if statistic == "plainB":
        return -np.asarray(arr["B"], np.float32)
    raise ValueError(statistic)


def fit_from_arrays(U_list, ids, statistic: str, seed: int = config.SEED_GATE, alphas=config.ALPHAS) -> dict:
    eps0 = cal.eps0_from(U_list)
    thr = {f"{a:g}": cal.fit_threshold(U_list, a, eps0, seed, statistic=statistic, K=config.K, ids=ids).to_json() for a in alphas}
    return dict(statistic=statistic, K=config.K, seed=seed, n_cal=len(U_list), eps0=eps0, min_gap=cal.min_positive_gap(U_list), ids_hash=cal.ids_hash(ids), thresholds=thr,
                wording="The threshold is calibrated so that, for a clean test pair exchangeable with the calibration pairs, the expected proportion of its tokens that are flagged is at most alpha.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-GATE-M2")
    ap.add_argument("--statistic", choices=["q", "plainB"], default=config.STAT_NAME)
    ap.add_argument("--force", action="store_true", help="overwrite an existing threshold file (write-once; the old file is kept and an amendment is logged)")
    ap.add_argument("--min-items", type=int, default=None, help="refuse to fit on fewer items (default: 300, or the effective n after real-tokenizer exclusions)")
    a = ap.parse_args(argv)
    run = Path(common.RUNS) / a.run_id
    rows = common.read_jsonl(run / "items.jsonl")
    eff = run / "effective_n.json"
    min_items = a.min_items if a.min_items is not None else (json.loads(eff.read_text(encoding="utf8"))["effective"] if eff.exists() else config.N_CAL)
    if len(rows) < min_items:
        print(f"{len(rows)} calibration items < {min_items}; finish M2 first (or lower --min-items for a labelled smoke fit)", file=sys.stderr)
        return 2
    U, ids, codes = [], [], []
    for r in sorted(rows, key=lambda r: r["idx"]):
        arr = np.load(run / "arrays" / f"item{r['idx']:04d}.npz")
        U.append(suspicion_from_arrays(arr, a.statistic))
        ids.append(r["gid"])
        codes.append(arr["codes"])
    res = fit_from_arrays(U, ids, a.statistic)
    out = run / ("threshold.json" if a.statistic == config.STAT_NAME else f"threshold_{a.statistic}.json")
    try:
        artifacts.write_once(out, json.dumps(res, indent=1), a.force)
    except artifacts.WriteOnceError as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    np.save(run / "codefreq.npy", baselines.CodeFreq.fit(codes, 16384).counts)
    print(json.dumps({k: res[k] for k in ("statistic", "n_cal", "eps0", "ids_hash")} | {a_: v["tau"] for a_, v in res["thresholds"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
