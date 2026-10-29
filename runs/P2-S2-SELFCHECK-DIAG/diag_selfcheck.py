"""S2 self-check diagnosis (2026-10-29). Reads only: the S2 list's items[0] (image + caption, the self-check reference) and M4's stored clean_codes for that item.
No S2 item is processed; no outcome file is opened.

    PY tools/gpu_guard.py --log runs/P2-S2-SELFCHECK-DIAG/telemetry-<n>.csv --every 1 --max-temp 80 --max-minutes 10 -- PY runs/P2-S2-SELFCHECK-DIAG/diag_selfcheck.py --tag <n>

What it records (runs/P2-S2-SELFCHECK-DIAG/diag-<tag>.json):
  flags      cuDNN / TF32 / matmul-precision state after the model load (what set_torch_defaults left behind)
  inputs     whether the two tokeniser inputs (UniScorer.encode vs messages_to_batch) are bitwise equal, and their strides / memory format
  sc0        UniScorer.selfcheck exactly as the runner calls it (first call in the process, production flags)
  variants   for each backend setting: K repeated encodes of each input path; agreement mine-vs-ref, mine-vs-mine, vs M4 clean_codes
  sc_det     UniScorer.selfcheck run inside the deterministic-cuDNN context (the candidate fix), K times
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent


def _get(expr):
    try:
        return eval(expr)
    except Exception as e:                                                # torch 2.11 refuses legacy reads after a mix of legacy and new precision APIs
        return f"ERR {type(e).__name__}"


FLAG_EXPRS = dict(cudnn_enabled="torch.backends.cudnn.enabled", cudnn_benchmark="torch.backends.cudnn.benchmark", cudnn_deterministic="torch.backends.cudnn.deterministic",
                  cudnn_allow_tf32="torch.backends.cudnn.allow_tf32", matmul_allow_tf32="torch.backends.cuda.matmul.allow_tf32",
                  float32_matmul_precision="torch.get_float32_matmul_precision()", conv_fp32_precision="torch.backends.cudnn.conv.fp32_precision",
                  matmul_fp32_precision="torch.backends.cuda.matmul.fp32_precision", cudnn_version="torch.backends.cudnn.version()", torch="torch.__version__")


def flags():
    return {k: _get(v) for k, v in FLAG_EXPRS.items()}


@contextlib.contextmanager
def backend(benchmark=None, deterministic=None, ieee=False):
    """benchmark / deterministic: cuDNN switches. ieee=True: full fp32 for cuDNN convolutions and cuBLAS matmuls (new API), restored afterwards."""
    cd = torch.backends.cudnn
    old = (cd.benchmark, cd.deterministic) + ((cd.conv.fp32_precision, torch.backends.cuda.matmul.fp32_precision) if ieee else (None, None))
    try:
        if benchmark is not None:
            cd.benchmark = benchmark
        if deterministic is not None:
            cd.deterministic = deterministic
        if ieee:
            cd.conv.fp32_precision = "ieee"
            torch.backends.cuda.matmul.fp32_precision = "ieee"
        yield
    finally:
        cd.benchmark, cd.deterministic = old[:2]
        if ieee:
            cd.conv.fp32_precision, torch.backends.cuda.matmul.fp32_precision = old[2], old[3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--k", type=int, default=3)
    a = ap.parse_args()
    torch.cuda.set_per_process_memory_fraction(0.75)                     # as the runner does, before the load
    from exp_p2 import common, run_gate_s2
    from exp_p2.scoring import UniScorer
    items, _ = run_gate_s2.plan_items(300)
    it0 = items[0]
    t0 = time.perf_counter()
    sc = UniScorer(common.load_net())
    res = dict(tag=a.tag, idx=it0["idx"], image_id=it0["image_id"], load_s=time.perf_counter() - t0, flags_after_load=flags())
    pil = common.load_image(it0["image_id"])

    # 1. the runner's call, first in the process, production flags
    res["sc0"] = sc.selfcheck(pil, it0["caption"])

    # 2. the two tokeniser inputs
    from demo.inference_utils import tensor_center_crop
    from unidisc.tokenizers.image_tokenizers import get_image_batch
    img512 = sc.preprocess(pil)
    x_mine = torch.from_numpy(np.array(img512.convert("RGB"))).permute(2, 0, 1)[None].float() / 255.0          # UniScorer.encode
    x_ref = tensor_center_crop(torch.from_numpy(np.array(img512))[None, :].permute(0, 3, 1, 2) / 255, (512, 512))   # messages_to_batch
    res["inputs"] = dict(bitwise_equal=bool(torch.equal(x_mine, x_ref)), max_abs=float((x_mine - x_ref).abs().max()),
                         stride_mine=list(x_mine.stride()), stride_ref=list(x_ref.stride()),
                         mine_channels_last=bool(x_mine.is_contiguous(memory_format=torch.channels_last)), ref_channels_last=bool(x_ref.is_contiguous(memory_format=torch.channels_last)),
                         mine_contig=bool(x_mine.is_contiguous()), ref_contig=bool(x_ref.is_contiguous()))
    m4 = np.load(ROOT / "runs" / "P2-GATE-M4" / "arrays" / f"item{it0['idx']:04d}.npz")
    clean = m4["clean_codes"].astype(np.int64)

    def enc(x):
        return get_image_batch(sc.model.config, sc.model.get_vae(), {"img": x}, sc.model.device).reshape(-1).cpu().numpy().astype(np.int64)

    def agree(u, v):
        return float((u == v).mean())

    variants = dict(production=dict(), det=dict(benchmark=False, deterministic=True), det_fp32=dict(benchmark=False, deterministic=True, ieee=True))
    res["variants"] = {}
    for name, kw in variants.items():
        with backend(**kw):
            mines = [enc(x_mine) for _ in range(a.k)]
            refs = [enc(x_ref) for _ in range(a.k)]
            fl = flags()
        res["variants"][name] = dict(flags=fl, mine_vs_ref=[agree(m, r) for m, r in zip(mines, refs)], mine_repeat=[agree(mines[0], m) for m in mines[1:]],
                                     ref_repeat=[agree(refs[0], r) for r in refs[1:]], mine_vs_m4clean=[agree(m, clean) for m in mines], ref_vs_m4clean=[agree(r, clean) for r in refs])
        print(name, res["variants"][name]["mine_vs_ref"], res["variants"][name]["mine_vs_m4clean"], flush=True)

    # 3. the candidate fix: the self-check inside the deterministic-cuDNN context, production flags restored afterwards
    res["sc_det"] = []
    for _ in range(a.k):
        with backend(benchmark=False, deterministic=True):
            res["sc_det"].append(sc.selfcheck(pil, it0["caption"]))
    res["flags_at_end"] = flags()
    res["peak_gb"] = torch.cuda.max_memory_allocated() / 1e9
    (OUT / f"diag-{a.tag}.json").write_text(json.dumps(res, indent=1), encoding="utf8")
    print("sc0 frac", res["sc0"].get("image_tokens_frac_equal"), "sc_det", [d.get("image_tokens_frac_equal") for d in res["sc_det"]], "inputs", res["inputs"], flush=True)


if __name__ == "__main__":
    main()
