"""CPU analysis of family B (SAP A2 AD.6): freeze the fusion weights on the fit pairs, then test Y_fus against Y_best on the test pairs. No model, no GPU.

    python -m exp_p2.gate.analysis_foil freeze  [--fit-run P2-GATE-FOIL-FIT]  [--allow-partial] [--force]   -> runs/P2-GATE-FOIL/fusion_frozen.json   (write-once; COMMIT before the test stage)
    python -m exp_p2.gate.analysis_foil analyze [--test-run P2-GATE-FOIL-TEST] [--allow-partial] [--boot N]   -> runs/P2-GATE-FOIL/analysis.json

`freeze` reads only the fit run (FOIL pairs on calibration-fold images). `analyze` uses the COMMITTED weights, never a refit (it also records whether a refit would agree), refuses a partial test run
unless --allow-partial (SAP 8.2: no look at an outcome before the planned fold is complete), and labels a completed n below 120 descriptive. Wording limits are written into the output."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import artifacts, foil, seeds                              # noqa: E402


class PartialRun(RuntimeError):
    """SAP 8.2: the outcome analysis is not run before the planned fold is complete (unless --allow-partial)."""


def load_rows(run_dir: Path) -> tuple[list[dict], int]:
    """Rows de-duplicated by item index (first complete row kept, SAP 8.1) with finite margins counted separately; returns (rows, n_duplicates)."""
    raw = common.read_jsonl(Path(run_dir) / "items.jsonl")
    seen, rows = set(), []
    for r in raw:
        if r["idx"] not in seen:
            seen.add(r["idx"])
            rows.append(r)
    return rows, len(raw) - len(rows)


def expected_n(run_dir: Path) -> int | None:
    """Pairs the run should finish: planned minus the runtime token exclusions (never replaced). None if the run has not written its exclusion file."""
    p = Path(run_dir) / "token_exclusions.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf8"))
    return int(d["n_planned"]) - int(d["n_excluded"])


def rows_sha256(rows: list[dict]) -> str:
    return hashlib.sha256(json.dumps([[r["idx"], r["pair_id"], round(r["T"], 12), round(r["I"], 12)] for r in sorted(rows, key=lambda r: r["idx"])]).encode("utf8")).hexdigest()


def git_sha() -> str:
    try:
        return common.git_sha()
    except Exception:
        return "unknown"


def freeze(fit_dir: Path, out: Path, *, allow_partial: bool = False, force: bool = False) -> dict:
    rows, ndup = load_rows(fit_dir)
    exp = expected_n(fit_dir)
    if not rows:
        raise FileNotFoundError(f"no fit rows under {fit_dir}: run `python -m exp_p2.run_gate_foil --stage fit` first (nothing is frozen from an empty run)")
    if exp is None and not allow_partial:
        raise PartialRun(f"{fit_dir} has no token_exclusions.json, so the planned number of fit pairs is unknown; the fit run must have started and finished (or --allow-partial, which is recorded)")
    if exp is not None and len(rows) < exp and not allow_partial:
        raise PartialRun(f"fit run has {len(rows)} of {exp} pairs; finish it first (or --allow-partial, which is recorded)")
    X = foil.margins_from_rows(rows)
    fit = foil.fit_b1(X)
    payload = dict(fit=fit, n_rows=len(rows), n_duplicate_rows_removed=ndup, expected_rows=exp, allow_partial=bool(allow_partial), sha256_of_fit_run_rows=rows_sha256(rows),
                   pool_sha256=foil.pool_sha256(foil.load_pool()), foil_sha256=foil.FOIL_SHA256, fit_run=str(Path(fit_dir).name), code_git_sha=git_sha(), created=time.strftime("%Y-%m-%dT%H:%M:%S"),
                   rule=foil.THRESHOLD_NOTE, label="frozen before any B test pair; commit this file (rule iii)",
                   note="LDA weights act on the raw margins (T, I); Y_fus = 1[w . (T, I) > 0]; best direction ties go to the text direction")
    artifacts.write_once(Path(out), json.dumps(payload, indent=1), force)
    return payload


def analyze(test_dir: Path, frozen_path: Path, fit_dir: Path | None, out: Path, *, allow_partial: bool = False, n_boot: int = 10000, check_commit: bool = True) -> dict:
    if check_commit:
        foil.require_committed(frozen_path)
    frozen = json.loads(Path(frozen_path).read_text(encoding="utf8"))
    rows, ndup = load_rows(test_dir)
    exp = expected_n(test_dir)
    if not rows:
        raise FileNotFoundError(f"no test rows under {test_dir}: run `python -m exp_p2.run_gate_foil --stage test` first")
    if exp is not None and len(rows) < exp and not allow_partial:
        raise PartialRun(f"test run has {len(rows)} of {exp} pairs; the outcome analysis waits for the planned fold (SAP 8.2) or runs with --allow-partial and is then descriptive")
    X_test = foil.margins_from_rows(rows)
    X_fit = foil.margins_from_rows(load_rows(fit_dir)[0]) if fit_dir is not None and Path(fit_dir, "items.jsonl").exists() else None
    res = foil.fusion_b1(X_fit, X_test, n_boot=n_boot, seed=seeds.seed_for("fusion"), n_planned=exp, frozen_fit=frozen["fit"])
    res.update(n_duplicate_rows_removed=ndup, partial=bool(exp is not None and len(rows) < exp), frozen_file_sha256_of_fit_rows=frozen.get("sha256_of_fit_run_rows"),
               meta=seeds.meta(), label="family B, m = 1, alpha 0.05 (own family, no cross-family adjustment)",
               limits=["not a corruption test: a within-modality gate cannot see a fluent foil word (derivation, E0, untested)",
                       "all test images are in folds.json test/test_ext, so P and B are dependent in their data (separate families, separate alpha)",
                       "the COCO captions c+ are probably in UniDisc's training data (U8) and the text direction may be memorised; contamination of FOIL images (U8) is unmeasured",
                       "supports 'fusion helps' only with b > c_cnt; the label 'negative' is not available at these n",
                       "foil captions are lower-cased on both sides because of the case leak; the FOIL file revision (July 2017 vs Oct 2018) is unverified"],
               created=time.strftime("%Y-%m-%dT%H:%M:%S"), code_git_sha=git_sha())
    if exp is not None:
        res["completed_vs_expected"] = [len(rows), exp]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)), encoding="utf8")
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["freeze", "analyze"])
    ap.add_argument("--fit-run", default=foil.FIT_RUN_ID)
    ap.add_argument("--test-run", default=foil.TEST_RUN_ID)
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--boot", type=int, default=10000)
    a = ap.parse_args(argv)
    fam = foil.pool_dir()
    try:
        if a.cmd == "freeze":
            p = freeze(Path(common.RUNS) / a.fit_run, fam / "fusion_frozen.json", allow_partial=a.allow_partial, force=a.force)
            print(json.dumps({k: p["fit"].get(k) for k in ("n_fit", "acc_T", "acc_I", "best", "best_acc", "acc_lda", "acc_stouffer", "status", "test_pairs_may_run")}, indent=1))
            print("wrote fusion_frozen.json: COMMIT it before the test stage" if p["fit"]["status"] == "ok" else f"status {p['fit']['status']}: the test pairs are not run (AD.6 rules i, ii); commit this file anyway")
        else:
            r = foil.fusion_b1  # noqa: F841  (import check)
            res = analyze(Path(common.RUNS) / a.test_run, fam / "fusion_frozen.json", Path(common.RUNS) / a.fit_run, fam / "analysis.json", allow_partial=a.allow_partial, n_boot=a.boot)
            print(json.dumps({k: res.get(k) for k in ("status", "tested", "p", "supports_fusion_helps", "n_test_completed", "best_direction", "wording")}, indent=1, default=str))
            if "test" in res:
                print({k: res["test"][k] for k in ("b", "c", "n_d", "p", "acc_a", "acc_b", "delta", "ci95")})
    except (PartialRun, artifacts.WriteOnceError, RuntimeError, FileNotFoundError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
