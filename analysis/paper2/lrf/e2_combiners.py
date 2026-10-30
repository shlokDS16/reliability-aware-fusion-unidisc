"""E2 (EXPLORATORY-PLAN-BASELINES-2026-10-30.md): detector-free robust combiners on the Study 2 fresh fold. CPU only; no model, no GPU.

    "C:/.../.venv/Scripts/python.exe" -I -m analysis.paper2.lrf.e2_combiners [--run-dir runs/P2-LRF-L1] [--out runs/P2-LRF-E2/combiners.json]

Arms MED (median of the 1,024 per-token evidence values), TM20 (20 percent trimmed mean) and TM-G (trimmed at the gate's flag count) are NOT
re-implemented: the item margins come from `exp_p2.gate.tier3_fusion.item_margins` (the Study 1 Tier-3 code, A4.1.4), called with a stub
calibration pool because those three arms (and NONE) never read it. Y = 1[margin > 0] and not empty (ties wrong), as `tier3_fusion.cell_results`.
Inputs: `<run-dir>/arrays/item<idx:04d>.npz` keys `<cond>_delta` and `<cond>_flag0.05`; items, labels and conditions from
`<run-dir>/predictions.jsonl` (the same 450 items per condition). Consistency gate before anything is written: NONE recomputed from the arrays
must equal `y_none` of predictions.jsonl for every item and condition, and the gate arm (mean of the unflagged tokens > 0) must equal `y_gatem`.
Reporting: accuracy per arm and condition; paired difference against NONE = (b - c) / n with discordant counts b (arm right, NONE wrong) and
c; 95 percent paired percentile bootstrap interval (10,000 resamples of items, one index matrix per condition from SeedSequence(0), shared by
all arms, numpy.quantile 0.025 and 0.975). No p-value, no test, no multiplicity claim. Label: exploratory (plan E2)."""
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

from exp_p2.gate import evidence, tier3_fusion as T3                                   # noqa: E402

CONDS = ("noise0.1", "jpeg10", "splice128", "clean")                                  # family-L conditions, in the order of the paper's table
ARMS = ("MED", "TM20", "TM-G")                                                       # plan E2; NONE is the reference
FLAG_KEY = f"flag{T3.ALPHA_KEY}"                                                     # "flag0.05"
N_BOOT = 10000
SEED = 0
LABEL = "exploratory (EXPLORATORY-PLAN-BASELINES-2026-10-30.md E2); no p-value, no test, no multiplicity claim; added after the preregistered Study 2 results"


class _StubPool:
    """Stands in for the Study 1 calibration pool. MED, TM20, TM-G and NONE never read it; SOFT-G / SOFT-A are not used here."""

    def weights_g(self, u, F):
        return np.ones(np.asarray(F).shape, np.float64)

    def weights_a(self, u):
        return np.ones(np.asarray(u).shape, np.float64)


_POOL = _StubPool()


def decisions(delta: np.ndarray, flag: np.ndarray) -> dict[str, int]:
    """Y of NONE, MED, TM20, TM-G (via tier3_fusion.item_margins) and of the hard gate GM, for one item and condition."""
    mg = T3.item_margins(delta, flag, np.zeros_like(delta, dtype=np.float64), _POOL)
    return {a: int(mg[a][0] > 0 and not mg[a][1]) for a in ("NONE", "GM") + ARMS}


def paired(ya: np.ndarray, yr: np.ndarray, idx: np.ndarray) -> dict:
    """Arm minus reference, over the same items: (b - c) / n, discordant counts, 95 percent percentile bootstrap interval."""
    diff = ya.astype(np.int8) - yr.astype(np.int8)
    n = int(diff.size)
    b, c = int((diff == 1).sum()), int((diff == -1).sum())
    boots = diff[idx].mean(axis=1)
    return dict(diff=(b - c) / n, b=b, c=c, ci95=[float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))])


def analyse(run_dir: Path) -> dict:
    run_dir = Path(run_dir)
    pred_path = run_dir / "predictions.jsonl"
    rows = [json.loads(l) for l in open(pred_path, encoding="utf-8") if l.strip()]
    out_cells, problems = {}, []
    cache: dict[int, dict] = {}
    for cond in CONDS:
        r = sorted((x for x in rows if x["condition"] == cond), key=lambda x: x["idx"])
        if not r:
            raise RuntimeError(f"no prediction rows for condition {cond}")
        Y = {a: [] for a in ("NONE", "GM") + ARMS}
        flagged, empties, ties = [], {a: 0 for a in ARMS}, {a: 0 for a in ARMS}
        for x in r:
            i = x["idx"]
            if i not in cache:
                with np.load(run_dir / "arrays" / f"item{i:04d}.npz") as z:
                    cache[i] = {k: z[k] for k in z.files if k.endswith(("_delta", "_" + FLAG_KEY))}
            delta, flag = cache[i][f"{cond}_delta"], cache[i][f"{cond}_{FLAG_KEY}"].astype(bool)
            if delta.shape != (T3.M_TOKENS,) or not np.all(np.isfinite(delta)):
                raise RuntimeError(f"{cond} idx {i}: delta is not {T3.M_TOKENS} finite values")
            y = decisions(delta, flag)
            if y["NONE"] != evidence.evidence_from_delta(delta)["y"] or y["NONE"] != int(x["y_none"]):
                problems.append(f"{cond} idx {i}: NONE recomputed {y['NONE']} stored y_none {x['y_none']}")
            if y["GM"] != int(x["y_gatem"]):
                problems.append(f"{cond} idx {i}: gate arm recomputed {y['GM']} stored y_gatem {x['y_gatem']}")
            mg = T3.item_margins(delta, flag, np.zeros_like(delta, dtype=np.float64), _POOL)
            for a in ARMS:
                empties[a] += int(mg[a][1])
                ties[a] += int(mg[a][0] == 0.0 and not mg[a][1])
            for a in Y:
                Y[a].append(y[a])
            flagged.append(int(flag.sum()))
        Y = {a: np.array(v, np.int8) for a, v in Y.items()}
        n = len(r)
        idx = T3.index_matrix(n, np.random.SeedSequence(SEED), N_BOOT)
        cell = dict(n=n, mean_flagged=float(np.mean(flagged)),
                    arms={"NONE": dict(acc=float(Y["NONE"].mean()), n_empty=0, n_ties=0)})
        for a in ARMS:
            cell["arms"][a] = dict(acc=float(Y[a].mean()), n_empty=empties[a], n_ties=ties[a], vs_NONE=paired(Y[a], Y["NONE"], idx))
        out_cells[cond] = cell
    if problems:
        raise RuntimeError("consistency gate failed (nothing written): " + "; ".join(problems[:5]) + f" ... ({len(problems)} problems)")
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()               # noqa: E731
    return dict(
        label=LABEL, plan="research/paper2/tnnls/EXPLORATORY-PLAN-BASELINES-2026-10-30.md E2",
        definitions="exp_p2/gate/tier3_fusion.py item_margins (MED = numpy.median; TM20 = trimmed mean, k = floor(0.20 m) per tail; TM-G = trimmed mean, k = g // 2 per tail, g = flag0.05 count); Y = 1[margin > 0], ties and empty sets wrong",
        sign="differences are arm minus NONE; positive favours the arm",
        bootstrap=dict(n_boot=N_BOOT, seed="numpy.random.SeedSequence(0), one index matrix per condition shared by all arms", interval="percentile, numpy.quantile 0.025 and 0.975", unit="items"),
        consistency=dict(ok=True, checked="NONE recomputed == y_none and gate arm == y_gatem for every item and condition", n_rows_checked=sum(c["n"] for c in out_cells.values())),
        inputs=dict(predictions=str(pred_path.relative_to(ROOT)) if pred_path.is_relative_to(ROOT) else str(pred_path), predictions_sha256=sha(pred_path),
                    arrays_dir=str((run_dir / "arrays").relative_to(ROOT)) if run_dir.is_relative_to(ROOT) else str(run_dir / "arrays"),
                    tier3_fusion_sha256=sha(ROOT / "exp_p2" / "gate" / "tier3_fusion.py"), numpy=np.__version__),
        cells=out_cells, conditions=list(CONDS), arms=["NONE", *ARMS])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default=str(ROOT / "runs" / "P2-LRF-L1"))
    ap.add_argument("--out", default=str(ROOT / "runs" / "P2-LRF-E2" / "combiners.json"))
    a = ap.parse_args(argv)
    res = analyse(Path(a.run_dir))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("wrote", out)
    for c, v in res["cells"].items():
        print(c, v["n"], {k: round(x["acc"], 4) for k, x in v["arms"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
