"""A6.2 step 4: the re-freeze of LRF on the M4 items RE-SCORED at the fixed caption slot (L_FIX = 13). CPU only (torch, 4 threads), about 4 minutes on the 500 items.

    python -m analysis.paper2.lrf.refreeze [--src runs/P2-LRF-RESCORE] [--out runs/P2-LRF-FROZEN-LFIX] [--auditor-row ID]

The protocol is the one of `analysis_posthoc/learned_ceiling/lrf.py --freeze`, UNCHANGED: the same feature table (data.engineer), the same token subsample (ss(7), 25 percent), logistic-GAM F1 (rmax 40, 9 configurations), the same
`run.successive_halving` (random search + synchronous halving, eta 3, 3 inner folds, seed keys configs [2, 99, 0], inner folds [1, 99]), the same final seed key [4, 99, 0, 0], refit on all 500 items x 4 conditions.
What differs, as A6.2 step 4 requires:
  * input   only the re-scored run (default runs/P2-LRF-RESCORE, arrays/itemNNNN.npz); runs/P2-GATE-M4 is not read
  * output  a NEW directory (default runs/P2-LRF-FROZEN-LFIX: model.npz, spec.json, hpo.json, selfcheck.json); it must not exist; runs/P2-LRF-FROZEN (the retired first object) and the source run are never written
  * gate    refuses unless the re-score run passed the A6.2 step 2-3 gate (`run_gate_lrf_rescore.check_rows`: invariance exactly 0, or at most 1e-6 with --auditor-row; positive control at most 1e-5) and holds all n items
  * NO ACCURACY: nothing here computes, prints or writes an accuracy, a decision count or a margin of the re-frozen model (no insample_accuracy, none_accuracy, insample_weights.npz). The inner-fold accuracies that
    `successive_halving` logs internally are dropped from hpo.json; the O1 criterion (a training loss) and the numpy-versus-torch maximum weight difference (a code-equality check, selfcheck.json) are kept.
The spec records L_FIX, the source run, the SHA-256 of the re-scored arrays (digest over the per-file hashes) and of the code (data.py, families.py, lrf.py, run.py, this file) so that the A6.0 item 2 row can copy them."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, run_gate_lrf_rescore as rescore                          # noqa: E402
from analysis_posthoc.learned_ceiling import data, families as fam, lrf, run        # noqa: E402

SRC_RUN, OUT_NAME, RETIRED_NAME = "P2-LRF-RESCORE", "P2-LRF-FROZEN-LFIX", "P2-LRF-FROZEN"
FROZEN_KEY = lrf.FROZEN_KEY               # 99
L_FIX = rescore.L_FIX


class RefreezeRefused(RuntimeError):
    """A precondition of A6.2 step 4 does not hold; nothing was written."""


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def arrays_digest(arr_dir: Path, n_items: int) -> str:
    """SHA-256 over the per-file SHA-256 values of item0000..item{n-1}.npz, in order."""
    h = hashlib.sha256()
    for i in range(n_items):
        h.update(sha256_file(Path(arr_dir) / f"item{i:04d}.npz").encode())
    return h.hexdigest()


def preflight(src: Path, out: Path, retired: Path, n_items: int, auditor_row: str | None) -> dict:
    src, out, retired = Path(src).resolve(), Path(out).resolve(), Path(retired).resolve()
    if out in (retired, src) or retired in out.parents or src in out.parents:
        raise RefreezeRefused(f"--out {out} must be a new directory, not the retired object {retired} nor the source run {src}")
    if out.exists():
        raise RefreezeRefused(f"{out} exists; the re-frozen object is written once (a defect is handled by a rerun beside it, card v3 section 17)")
    chk = rescore.check_rows(src, inv_tol=(rescore.INV_TOL_AUDITOR if auditor_row else rescore.INV_TOL))
    if not chk["ok"]:
        raise RefreezeRefused(f"the re-score run did not pass the A6.2 step 2-3 gate: {chk['reason']}")
    missing = [i for i in range(n_items) if not (src / "arrays" / f"item{i:04d}.npz").exists()]
    if missing:
        raise RefreezeRefused(f"{len(missing)} re-scored arrays missing (first {missing[:5]}): the re-score is incomplete")
    return chk


def refreeze(src: Path, out: Path, *, retired: Path | None = None, n_items: int = 500, rmax: int = 40, n_cfg: int = 9, auditor_row: str | None = None, log=print) -> dict:
    """Run the re-freeze. `n_items`, `rmax` and `n_cfg` are the protocol's 500, 40 and 9 (the tests shrink them). Returns the spec dict (no accuracy in it)."""
    src, out = Path(src), Path(out)
    retired = Path(retired) if retired else Path(common.RUNS) / RETIRED_NAME
    chk = preflight(src, out, retired, n_items, auditor_row)
    arr = src / "arrays"
    t0 = time.time()
    d = data.load(arr, n_items)
    ctx = SimpleNamespace(X=data.engineer(d["raw"]), delta=d["delta"], z=d["z"], gm=d["gm"], codes=d["codes"], mask=data.token_subsample(run.ss(7), d["delta"].shape, 0.25))
    allit = np.arange(n_items)
    f1 = fam.F1GAM("F1", rmax, n_cfg)
    cfg, score, hl = run.successive_halving(ctx, f1, allit, FROZEN_KEY, 0)
    seed = int(run.ss(4, FROZEN_KEY, 0, 0).generate_state(1)[0])
    model = f1.fit(ctx, cfg, allit, f1.rmax, seed)
    net = model["net"]
    out.mkdir(parents=True)
    np.savez(out / "model.npz", a=net.a.detach().numpy(), b=net.b.detach().numpy(), c=net.c.detach().numpy(), knots=net.knots.numpy(), mu=model["mu"], sd=model["sd"], feature_names=np.array(data.feature_names()))
    T = fam.temperature(ctx.delta)
    for e in hl["log"]:
        e.pop("acc", None)                                           # inner-fold accuracy: computed inside successive_halving, never stored (A6.2 step 4)
    code_dir = Path(lrf.__file__).parent
    spec = dict(name="LRF (learned reliability-aware evidence fusion), logistic-GAM F1, RE-FROZEN at a fixed caption-slot length",
                decision="D0083", status="re-frozen on the M4 items re-scored at L_FIX; no accuracy computed before the hash commit (A6.2 step 4); no out-of-sample estimate",
                family="F1 logistic-GAM: w_j = sigmoid(b + sum_k a_k x_k + sum_k sum_m c_km relu(x_k - t_km)), x standardised",
                objective="item-level O1: mean softplus(-M/T), M = sum_j w_j Delta_j / sum_j w_j, + ridge * (|a|^2 + |c|^2); AdamW (wd 0), mini-batch 32 item-conditions",
                training_conditions=list(data.COND), n_items=n_items, T=T, selected_cfg=cfg, inner_cv_o1=score, epochs=f1.rmax, seed=seed,
                hpo=dict(method="random search + synchronous successive halving, eta 3, %d configs, 3 inner folds over all %d items" % (n_cfg, n_items),
                         seed_keys=dict(configs=[2, FROZEN_KEY, 0], inner_folds=[1, FROZEN_KEY], final_fit=[4, FROZEN_KEY, 0, 0]), root_seed=run.ROOT_SEED),
                features=data.feature_names(), n_features=len(data.feature_names()),
                preprocessing="raw_from_npz -> data.engineer (per item and condition, no cross-item statistics) -> (X - mu) / sd with the stored mu, sd",
                inputs_never_used=["Delta", "Lambda", "captions", "z", "GATE flags", "condition identity"],
                caption_slot_len=L_FIX, layout="B, s3, D, tbv scored on sc.build([PAD] * 13, codes); Lambda and Delta at their own caption lengths; tex and nbr layout-free",
                source_run=str(src.name), rescore_checks=chk, rescored_arrays_digest=arrays_digest(arr, n_items), rescore_config_sha256=sha256_file(src / "config.json"),
                inference="analysis_posthoc.learned_ceiling.lrf.infer_item(load_frozen(<this dir>), np.load(item.npz), cond)",
                code_sha256={f: sha256_file(code_dir / f) for f in (*lrf.CODE_FILES, "run.py")}, refreeze_py_sha256=sha256_file(Path(__file__)), model_sha256=sha256_file(out / "model.npz"),
                torch=__import__("torch").__version__, numpy=np.__version__)
    (out / "spec.json").write_text(json.dumps(spec, indent=1), encoding="utf8")
    (out / "hpo.json").write_text(json.dumps(hl, indent=1), encoding="utf8")
    # code-equality check only: the numpy inference path equals the torch training path (weights, never decisions)
    fz = lrf.load_frozen(out)
    chk_idx = np.arange(0, n_items, max(1, n_items // 20))
    w_torch = f1.weights(ctx, model, chk_idx)
    maxdiff = 0.0
    for j, i in enumerate(chk_idx):
        dd = np.load(arr / f"item{int(i):04d}.npz")
        for c, name in enumerate(data.COND):
            maxdiff = max(maxdiff, float(np.abs(lrf.infer_item(fz, dd, name)["w"] - w_torch[j, c]).max()))
    (out / "selfcheck.json").write_text(json.dumps(dict(selfcheck_max_abs_diff_numpy_vs_torch=maxdiff, sec=round(time.time() - t0, 1), note="weights only; no accuracy computed (A6.2 step 4)"), indent=1), encoding="utf8")
    log(json.dumps(dict(out=str(out), model_sha256=spec["model_sha256"], spec_sha256=sha256_file(out / "spec.json"), selfcheck_max_abs_diff=maxdiff, rescored_arrays_digest=spec["rescored_arrays_digest"])))
    return spec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(Path(common.RUNS) / SRC_RUN))
    ap.add_argument("--out", default=str(Path(common.RUNS) / OUT_NAME))
    ap.add_argument("--auditor-row", default=None, help="id of the gate-auditor row accepting an invariance difference of at most 1e-6")
    a = ap.parse_args(argv)
    try:
        refreeze(Path(a.src), Path(a.out), auditor_row=a.auditor_row)
    except (RefreezeRefused, FileNotFoundError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
