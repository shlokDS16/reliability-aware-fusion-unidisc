"""Severity sweep analysis (research/paper2/tnnls/EXPLORATORY-PLAN-SEVERITY-2026-10-31.md). CPU only; no model, no GPU.

    "C:/.../.venv/Scripts/python.exe" -m analysis.paper2.lrf.e1_severity [--sev-run runs/P2-LRF-SEV] [--l1-run runs/P2-LRF-L1] [--out runs/P2-LRF-SEV/sev_analysis.json]

Inputs: `<sev-run>/predictions.jsonl` (written by `python -m exp_p2.gate.lrf_score --run-id P2-LRF-SEV --pins runs/P2-LRF-PINS/pins.json --conds noise0.05,noise0.2,noise0.3`) and
`<l1-run>/predictions.jsonl` (conditions `clean` and `noise0.1`). Items matched by idx; idx, gid and image_id must agree and every level must hold the same item set.
Per level sigma in {0 (clean, L1), 0.05, 0.1 (L1), 0.2, 0.3}: accuracy of NONE (`y_none`, unweighted sum) and LRF (`y_lrf`, frozen weights); LRF minus NONE = (b - c) / n with discordant counts;
gain(sigma) minus gain(clean) = mean over items of [(LRF - NONE) at sigma - (LRF - NONE) on clean]. 95 percent paired percentile bootstrap intervals, 10,000 item resamples, ONE index matrix
(numpy.random.SeedSequence(0), as e1_denoise.py) shared by every level and contrast, numpy.quantile 0.025 and 0.975. Length-matched negative (`y_*_L`) under `length_matched` when every row has it.
Optional positive control: if the sweep arrays hold `noise0.1_codes_crn`, they are compared with L1's `noise0.1_codes`. No p-value, no test, no multiplicity claim."""
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

from analysis.paper2.lrf.e1_denoise import _rows, load                               # noqa: E402
from exp_p2.gate import tier3_fusion as T3                                             # noqa: E402

LEVELS = (("0", "clean", "l1"), ("0.05", "noise0.05", "sev"), ("0.1", "noise0.1", "l1"), ("0.2", "noise0.2", "sev"), ("0.3", "noise0.3", "sev"))
N_EXPECTED = 450                                  # the n-rule's n_L (runs/P2-LRF-PLAN/family.json n_rule.test_fold)
PC_MIN = 0.99                                     # plan stop rule: positive-control token agreement below this invalidates the sweep
N_BOOT = 10000
SEED = 0
LABEL = "exploratory (EXPLORATORY-PLAN-SEVERITY-2026-10-31.md); no p-value, no test, no multiplicity claim; added after the preregistered Study 2 results"


def _ci(d: np.ndarray, idx: np.ndarray) -> list[float]:
    boots = d[idx].mean(axis=1)
    return [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]


def _analyse(rows: dict[str, dict[int, dict]], suffix: str, idx_cache: dict) -> dict:
    ids = sorted(rows["0"])
    for lv, r in rows.items():
        if sorted(r) != ids:
            raise RuntimeError(f"level {lv}: item set differs from clean ({len(r)} vs {len(ids)} rows)")
        for i in ids:
            if (r[i]["gid"], r[i]["image_id"]) != (rows["0"][i]["gid"], rows["0"][i]["image_id"]):
                raise RuntimeError(f"level {lv} idx {i}: gid or image_id differ")
    n = len(ids)
    if n not in idx_cache:
        idx_cache[n] = T3.index_matrix(n, np.random.SeedSequence(SEED), N_BOOT)
    idx = idx_cache[n]
    y = lambda r, k: np.array([int(r[i][k]) for i in ids], np.int8)                   # noqa: E731
    g0 = (y(rows["0"], "y_lrf" + suffix) - y(rows["0"], "y_none" + suffix)).astype(np.float64)
    out = {}
    for lv, cond, src in LEVELS:
        none, lrf = y(rows[lv], "y_none" + suffix), y(rows[lv], "y_lrf" + suffix)
        d = (lrf - none).astype(np.float64)
        b, c = int((d == 1).sum()), int((d == -1).sum())
        cell = dict(condition=cond, source="P2-LRF-L1" if src == "l1" else "P2-LRF-SEV", n=n, NONE=float(none.mean()), LRF=float(lrf.mean()),
                    LRF_minus_NONE=dict(diff=(b - c) / n, b=b, c=c, ci95=_ci(d, idx)))
        if lv != "0":
            cell["gain_minus_clean_gain"] = dict(diff=float((d - g0).mean()), ci95=_ci(d - g0, idx))
        out[lv] = cell
    return out


def corruption_check(sev_run: Path, l1_run: Path, ids: list[int]) -> dict:
    eq = items_eq = n = 0
    for i in ids:
        ps, pl = sev_run / "arrays" / f"item{i:04d}.npz", l1_run / "arrays" / f"item{i:04d}.npz"
        if not (ps.exists() and pl.exists()):
            return dict(checked=False, reason="arrays missing")
        with np.load(ps) as zs, np.load(pl) as zl:
            if "noise0.1_codes_crn" not in zs.files or "noise0.1_codes" not in zl.files:
                return dict(checked=False, reason="codes not stored")
            a, b = zs["noise0.1_codes_crn"], zl["noise0.1_codes"]
        eq += int((a == b).sum())
        items_eq += int((a == b).all())
        n += 1
    frac = eq / (n * 1024) if n else None
    return dict(checked=True, n_items=n, token_equal_fraction=frac, items_all_tokens_equal=items_eq, min_required=PC_MIN, ok=bool(frac is not None and frac >= PC_MIN))


def check_meta(sev_run: Path, n: int, n_expected: int | None = N_EXPECTED) -> dict:
    """The scorer's own record: the planned conditions, every item scored, its positive control passed, and the item count of the plan."""
    meta = json.loads((sev_run / "lrf_score_meta.json").read_text(encoding="utf8"))
    want = ["noise0.05", "noise0.2", "noise0.3"]
    bad = []
    if meta.get("conds") != want:
        bad.append(f"scorer conds {meta.get('conds')} != {want}")
    if meta.get("conds_absent_in_rows") or meta.get("n_items_skipped_no_arrays"):
        bad.append("scorer skipped conditions or items")
    if not (meta.get("positive_control") or {}).get("ok"):
        bad.append("scorer positive control not ok")
    if not meta.get("hashes"):
        bad.append("scorer recorded no input hashes (run it with --pins runs/P2-LRF-PINS/pins.json)")
    if n_expected is not None and n != n_expected:
        bad.append(f"n = {n}, plan says {n_expected}")
    if bad:
        raise RuntimeError("; ".join(bad))
    return dict(ok=True, n_items_rows=meta.get("n_items_rows"), predictions_sha256=meta.get("predictions_sha256"))


def analyse(sev_run: Path, l1_run: Path, n_expected: int | None = N_EXPECTED, need_meta: bool = True) -> dict:
    sev_run, l1_run = Path(sev_run), Path(l1_run)
    lines = dict(sev=load(sev_run / "predictions.jsonl"), l1=load(l1_run / "predictions.jsonl"))
    rows = {lv: _rows(lines[src], cond) for lv, cond, src in LEVELS}
    res = dict(label=LABEL, plan="research/paper2/tnnls/EXPLORATORY-PLAN-SEVERITY-2026-10-31.md",
               definitions="NONE = y_none (unweighted sum), LRF = y_lrf (frozen weights, unchanged; fitted at noise 0.1 only); levels 0 and 0.1 from runs/P2-LRF-L1, others from the sweep run; "
                           "every sweep level uses L1's noise0.1 stream (common random numbers)",
               sign="LRF minus NONE; positive favours LRF; b = LRF right and NONE wrong, c = LRF wrong and NONE right",
               bootstrap=dict(n_boot=N_BOOT, seed="numpy.random.SeedSequence(0), one index matrix shared by all levels and contrasts", interval="percentile, numpy.quantile 0.025 and 0.975", unit="items"),
               levels=_analyse(rows, "", {}))
    if all(r.get("y_lrf_L") is not None for lv in rows for r in rows[lv].values()):
        res["length_matched"] = _analyse(rows, "_L", {})
    res["positive_control"] = corruption_check(sev_run, l1_run, sorted(rows["0.05"]))
    if need_meta:
        res["scorer_meta"] = check_meta(sev_run, len(rows["0"]), n_expected)
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()                    # noqa: E731
    res["inputs"] = dict(sev_predictions_sha256=sha(sev_run / "predictions.jsonl"), l1_predictions_sha256=sha(l1_run / "predictions.jsonl"), numpy=np.__version__)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sev-run", default=str(ROOT / "runs" / "P2-LRF-SEV"))
    ap.add_argument("--l1-run", default=str(ROOT / "runs" / "P2-LRF-L1"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else Path(a.sev_run) / "sev_analysis.json"
    try:
        res = analyse(Path(a.sev_run), Path(a.l1_run))
    except (RuntimeError, FileNotFoundError, KeyError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    pc = res["positive_control"]
    if pc.get("checked") is False or not pc.get("ok"):
        print("STOP: positive control failed or not checked (plan stop rule; results written but INVALID):", pc, file=sys.stderr)
        return 2
    for lv, c in res["levels"].items():
        print(lv, c["NONE"], c["LRF"], c["LRF_minus_NONE"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
