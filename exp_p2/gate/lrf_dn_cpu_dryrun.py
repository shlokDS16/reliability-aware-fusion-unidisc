"""CPU-only dry run of E1 (exp_p2/run_gate_lrf_dn.py). NO GPU, NO UniDisc: the network is the project's stub (tests/exp_p2/fake_gate.py, 32 x 32 token map), so every number it produces is meaningless.
What it proves is the plumbing, on REAL fold items, REAL COCO images, the REAL corruption seeds, the REAL OpenCV denoiser, the REAL thresholds, family and codebook (read only) and the REAL frozen LRF:
item -> corrupt (L1 seed) -> NLM denoise -> encode -> gate scores / delta / deltaL / tbv / tex / nbr -> arrays -> `lrf_score.score_run` with the pinned frozen object -> `e1_denoise.analyse`.

    "C:/.../.venv/Scripts/python.exe" -m exp_p2.gate.lrf_dn_cpu_dryrun --n 2 [--out runs/P2-LRF-DN-CPUDRY]

`common.RUNS` is redirected to a scratch directory, so the null cache (P2-GATE-DCACHE) and every other path of the real runs is untouched; only `--out/dryrun_report.json` is written under runs/.
The stub is not a stand-in for the measured speed of the GPU path; the report gives CPU timings of the CPU parts (corruption, NLM, encode stub) and of the whole stub item."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

os.environ["CUDA_VISIBLE_DEVICES"] = ""
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests" / "exp_p2"))

from exp_p2 import common, run_gate_lrf_dn as dn, run_gate_m4 as m4                 # noqa: E402
from exp_p2.gate import config, corruptions, lrf_score, pipeline, runner            # noqa: E402

REAL_RUNS = Path(common.RUNS)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--out", default=str(REAL_RUNS / "P2-LRF-DN-CPUDRY"))
    a = ap.parse_args(argv)
    from fake_gate import FakeScorer
    import torch
    assert not torch.cuda.is_available() or os.environ.get("CUDA_VISIBLE_DEVICES") == "", "CUDA must be hidden for the dry run"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="lrf_dn_dry_", dir=out))
    t_all = time.perf_counter()
    common.RUNS = scratch                                                              # the null cache and the dry-run run directory live here
    folds = json.loads((REAL_RUNS / "P2-LRF-FOLD" / "folds_lrf.json").read_text(encoding="utf8"))
    items = folds["test"][:a.n]
    # thresholds: the M2 file, family: the L1 plan (read only); load_prereqs reads common.RUNS, so call it with the real directory explicitly
    thr, family, eps0 = m4.load_prereqs(REAL_RUNS, "P2-LRF-PLAN")
    cb = np.load(REAL_RUNS / "P2-GATE-M1" / "codebook.npy")
    fake = FakeScorer(grid=32)
    fake.P = torch.randn(2048, 8, generator=torch.Generator().manual_seed(1))          # the stub's positional table holds 1024 rows; the real layout with a 32 x 32 map is 1044 + slot positions
    sc = runner.Counting(fake)
    ctx = SimpleNamespace(run=scratch / "P2-LRF-DN", dcache=pipeline.dcache_for(), thr=thr, family=family, eps0=eps0, fold=items, grid=32, extra_cells=(), ic=None, neg_len=True, slot_len=dn.L_FIX,
                          gate_true=False, patch=8, codebook=cb, tbv=True, denoise_for=(), sanity=(), dn_side={})
    run = scratch / "P2-LRF-DN"
    (run / "arrays").mkdir(parents=True)
    rows = []
    t_nlm = []
    orig_denoise = dn.denoise_nlm_sdn

    def timed(img):
        t = time.perf_counter()
        r = orig_denoise(img)
        t_nlm.append(time.perf_counter() - t)
        return r
    dn.denoise_nlm_sdn = timed
    item_s = []
    try:
        with dn.dn_patched(dn.denoise_record()):
            for it in items:
                t = time.perf_counter()
                row, arrays = m4.process(sc, it, ctx)
                item_s.append(time.perf_counter() - t)
                row = dict(row, idx=it["idx"], seconds=item_s[-1])
                np.savez(run / "arrays" / f"item{it['idx']:04d}.npz", **arrays)
                rows.append(row)
    finally:
        dn.denoise_nlm_sdn = orig_denoise
    with open(run / "items.jsonl", "w", encoding="utf8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    # ---- the real frozen LRF on the stub arrays (verifies the pins file, the frozen hashes and the feature code exactly as the production scorer does; the run-input hash check needs the GPU run's config and is not applicable)
    pins_user = json.loads((REAL_RUNS / "P2-LRF-PINS" / "pins.json").read_text(encoding="utf8"))
    pins = dict(lrf_score.DEFAULT_PINS, **{k: v for k, v in pins_user.items() if k != "code_sha256"})
    pins["code_sha256"] = dict(lrf_score.DEFAULT_PINS["code_sha256"], **(pins_user.get("code_sha256") or {}))
    fz = lrf_score.load_frozen(REAL_RUNS / "P2-LRF-FROZEN-LFIX", lrf_score.CODE_DIR, pins)
    conds = ("noise0.1_nlm", "jpeg10_nlm")
    lines, meta = lrf_score.score_run(run, fz, conds)
    lrf_score.write_predictions(lines, meta, run / "predictions.jsonl", force=True)
    # ---- analysis on the 2-item prefix of the real L1 predictions (the dry-run item set), written to the scratch run
    l1 = [json.loads(l) for l in open(REAL_RUNS / "P2-LRF-L1" / "predictions.jsonl", encoding="utf-8") if l.strip()]
    keep = {it["idx"] for it in items}
    l1_dir = scratch / "P2-LRF-L1-prefix"
    l1_dir.mkdir()
    (l1_dir / "predictions.jsonl").write_text("".join(json.dumps(x) + "\n" for x in l1 if x["idx"] in keep), encoding="utf-8")
    from analysis.paper2.lrf import e1_denoise as E1
    res = E1.analyse(run, l1_dir)
    (run / "dn_analysis.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    cond_keys = sorted(rows[0]["conds"])
    arr0 = dict(np.load(run / "arrays" / f"item{items[0]['idx']:04d}.npz"))
    report = dict(
        what="CPU dry run of E1 with the STUB network (tests/exp_p2/fake_gate.py); no GPU, no UniDisc. Numbers below are stub numbers and mean nothing.",
        n_items=len(items), idx=[it["idx"] for it in items], conditions_in_rows=cond_keys, conditions_scored_by_lrf_score=list(conds), n_prediction_lines=len(lines),
        positive_control=meta["positive_control"], frozen_pins_verified=meta["hashes"]["pins_verified"], pinned_externally=meta["hashes"]["pinned_externally"],
        arrays_item0_noise_keys=sorted(k for k in arr0 if k.startswith("noise0.1_nlm")),
        corruption_reproduction_note="not applicable with the stub encoder (its codes differ from UniDisc's); on the GPU run e1_denoise.corruption_check compares noise0.1_nlm_codes_corr with L1's noise0.1_codes",
        timing_s=dict(wall_total=time.perf_counter() - t_all, stub_item_mean=float(np.mean(item_s)), stub_item_each=[round(x, 3) for x in item_s],
                      nlm_per_image_mean=float(np.mean(t_nlm)), nlm_per_image_each=[round(x, 3) for x in t_nlm], n_nlm_calls=len(t_nlm)),
        stub_rows_pushed_through_network_per_item=[r["n_rows"] for r in rows],
        analysis_cells_stub=res["cells"], analysis_keys=sorted(res), opencv=__import__("cv2").__version__, cpu_count=os.cpu_count())
    (out / "dryrun_report.json").write_text(json.dumps(report, indent=1, default=str), encoding="utf8")
    shutil.rmtree(scratch, ignore_errors=True)
    print(json.dumps({k: report[k] for k in ("n_items", "conditions_in_rows", "n_prediction_lines", "positive_control", "frozen_pins_verified", "timing_s", "stub_rows_pushed_through_network_per_item")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
