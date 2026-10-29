"""A6.2 step 5 / A6.3: the cross-fit at L_FIX that feeds the n-rule. CPU only; exploratory, supplement only; it cannot stop, delay or change Study 2 except through the n-rule.

    python -m analysis.paper2.lrf.crossfit [--src runs/P2-LRF-RESCORE] [--out runs/P2-LRF-CF-LFIX]

The learned-ceiling cross-fit protocol (analysis_posthoc/learned_ceiling/run.py) for family F1 only, on the re-scored arrays: 5 outer folds of 100 items (`outer_folds`, seed key (0,)), 3 inner folds, random search + synchronous
halving (9 configurations, rungs 4 / 13 / 40 epochs), final seed keys (4, k, fi, s), one final seed for F1, the same feature table and token subsample. Nothing of the protocol is re-implemented: the checkpoints are written
by `run.run_family_fold` into --out/ckpt (with `run.OUT` pointed at --out; runs/P2-POSTHOC-LEARNED is never touched).
Result `--out/results.json`: for noise0.1 ONLY (the n-rule's input) the 2 x 2 table of the cross-fitted F1 decision against NONE (b: F1 right and NONE wrong; c: the reverse), n, `delta_cf` = (b - c) / n, `pi_cf` = (b + c) / n,
and the input hashes (re-scored arrays digest, source config, code files, this file). `lrf_nrule --cf-results` reads it and records its SHA-256. Requires the re-score run to have passed the A6.2 step 2-3 gate AND the re-frozen object (runs/P2-LRF-FROZEN-LFIX/model.npz and spec.json) to be committed and unchanged at HEAD (A6.10 order; the commit SHA is recorded). The result
refuses to overwrite. SEL minus NONE of the n-rule text is F1 minus NONE here, because only F1 is fitted (A6.2 step 5)."""
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
from analysis.paper2.lrf import refreeze as rf                                       # noqa: E402

SRC_RUN, OUT_NAME, OBJECT_NAME = "P2-LRF-RESCORE", "P2-LRF-CF-LFIX", "P2-LRF-FROZEN-LFIX"
NOISE = "noise0.1"


def folds(n_items: int, n_outer: int = run.N_OUTER) -> list[np.ndarray]:
    """The outer folds of the learned-ceiling run: a seeded permutation (key (0,)) cut into n_outer sorted parts; for 500 items exactly `run.outer_folds()`."""
    perm = np.random.default_rng(run.ss(0)).permutation(n_items)
    return [np.sort(a) for a in np.array_split(perm, n_outer)]


def _git(repo: Path, *args: str) -> bytes:
    import subprocess
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if r.returncode != 0:
        raise rf.RefreezeRefused(f"git {' '.join(args)} failed: {r.stderr.decode('utf8', 'replace').strip()[:200]}")
    return r.stdout


def object_commit(frozen_dir: Path, repo: Path = ROOT) -> str:
    """A6.10 order (audit D2): the cross-fit runs only after the re-frozen object is COMMITTED. model.npz and spec.json of `frozen_dir` must exist, be tracked at HEAD and equal the committed blobs (CRLF normalised);
    returns the SHA of the last commit that touched them (recorded in results.json). Raises RefreezeRefused otherwise."""
    frozen_dir = Path(frozen_dir).resolve()
    repo = Path(_git(Path(repo), "rev-parse", "--show-toplevel").decode().strip()).resolve()          # paths are taken relative to the repository root, whatever directory was given
    shas = []
    for name in ("model.npz", "spec.json"):
        f = frozen_dir / name
        if not f.exists():
            raise rf.RefreezeRefused(f"{f} missing: the re-frozen object must exist and be committed before the cross-fit (A6.10)")
        try:
            rel = f.relative_to(repo).as_posix()
        except ValueError:
            raise rf.RefreezeRefused(f"{f} is not inside the repository {repo}") from None
        if not _git(repo, "ls-files", "--", rel).strip():
            raise rf.RefreezeRefused(f"{rel} is not tracked: commit the re-frozen object (hash set) before the cross-fit (A6.10)")
        committed = _git(repo, "show", f"HEAD:{rel}")
        if committed.replace(b"\r\n", b"\n") != f.read_bytes().replace(b"\r\n", b"\n"):
            raise rf.RefreezeRefused(f"{rel} differs from its committed version at HEAD: the object on disk is not the committed one")
        shas.append(_git(repo, "log", "-n1", "--format=%H", "--", rel).decode().strip())
    return shas[0] if shas[0] == shas[1] else ",".join(shas)


def crossfit(src: Path, out: Path, *, n_items: int = 500, rmax: int = 40, n_cfg: int = 9, auditor_row: str | None = None, log=print,
             frozen_dir: Path | None = None, repo: Path = ROOT) -> dict:
    src, out = Path(src), Path(out)
    if (out / "results.json").exists():
        raise rf.RefreezeRefused(f"{out / 'results.json'} exists; not overwriting")
    obj_commit = object_commit(Path(frozen_dir) if frozen_dir else Path(common.RUNS) / OBJECT_NAME, repo)
    chk = rescore.check_rows(src, inv_tol=(rescore.INV_TOL_AUDITOR if auditor_row else rescore.INV_TOL))
    if not chk["ok"]:
        raise rf.RefreezeRefused(f"the re-score run did not pass the A6.2 step 2-3 gate: {chk['reason']}")
    arr = src / "arrays"
    t0 = time.time()
    d = data.load(arr, n_items)
    ctx = SimpleNamespace(X=data.engineer(d["raw"]), delta=d["delta"], z=d["z"], gm=d["gm"], codes=d["codes"], mask=data.token_subsample(run.ss(7), d["delta"].shape, 0.25), raw=d["raw"])
    out.mkdir(parents=True, exist_ok=True)
    (out / "ckpt").mkdir(exist_ok=True)
    (out / "hpo").mkdir(exist_ok=True)
    old_out, old_n = run.OUT, run.N_ITEMS
    run.OUT, run.N_ITEMS = out, n_items                                # run_family_fold / log write under `out`
    try:
        f1 = fam.F1GAM("F1", rmax, n_cfg)
        y = np.zeros((n_items, len(data.COND)), bool)
        for k, test in enumerate(folds(n_items)):
            train = np.setdiff1d(np.arange(n_items), test)
            run.run_family_fold(ctx, f1, 0, k, test, train)
            ck = np.load(out / "ckpt" / f"F1_fold{k}.npz")
            y[ck["test"]] = ck["y"]
    finally:
        run.OUT, run.N_ITEMS = old_out, old_n
    c = list(data.COND).index(NOISE)
    none = ctx.delta.mean(-1)[:, c] > 0
    f1y = y[:, c]
    b, cc = int((f1y & ~none).sum()), int((~f1y & none).sum())
    code_dir = Path(lrf.__file__).parent
    res = dict(condition=NOISE, n=n_items, b=b, c=cc, delta_cf=(b - cc) / n_items, pi_cf=(b + cc) / n_items, arm="F1 (cross-fitted) minus NONE; SEL = F1 because only F1 is fitted",
               protocol=dict(family="F1", n_outer=run.N_OUTER, n_inner=run.N_INNER, n_configs=n_cfg, rmax=rmax, root_seed=run.ROOT_SEED, final_seeds=run.FINAL_SEEDS["F1"]),
               inputs=dict(source_run=src.name, refrozen_object_commit=obj_commit, refrozen_object=OBJECT_NAME, rescored_arrays_digest=rf.arrays_digest(arr, n_items), rescore_config_sha256=rf.sha256_file(src / "config.json"), rescore_checks=chk,
                           code_sha256={f: rf.sha256_file(code_dir / f) for f in (*lrf.CODE_FILES, "run.py")}, crossfit_py_sha256=rf.sha256_file(Path(__file__))),
               label="post hoc, exploratory; sets the n-rule only; never quoted as performance (A6.2 step 5, C6-8)", sec=round(time.time() - t0, 1))
    (out / "results.json").write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf8")
    log(json.dumps(dict(out=str(out / "results.json"), sha256=hashlib.sha256((out / "results.json").read_bytes()).hexdigest(), delta_cf=res["delta_cf"], pi_cf=res["pi_cf"])))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(Path(common.RUNS) / SRC_RUN))
    ap.add_argument("--out", default=str(Path(common.RUNS) / OUT_NAME))
    ap.add_argument("--auditor-row", default=None)
    ap.add_argument("--frozen-dir", default=None, help=f"the committed re-frozen object (default runs/{OBJECT_NAME}); the cross-fit refuses unless it is tracked and unchanged at HEAD")
    a = ap.parse_args(argv)
    try:
        crossfit(Path(a.src), Path(a.out), auditor_row=a.auditor_row, frozen_dir=Path(a.frozen_dir) if a.frozen_dir else None)
    except (rf.RefreezeRefused, FileNotFoundError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
