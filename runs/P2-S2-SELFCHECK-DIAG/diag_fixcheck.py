"""Check of the proposed fix (S2-only): import `selfcheck_deterministic` from the patched copy of exp_p2/run_gate_s2.py (path given on the command line; the pinned
working copy is not edited), call it FIRST in a fresh process exactly as runner.run_items would (mem_frac 0.75 set before the load, items from plan_items(300)),
then record the backend flags after it and, for contrast, the unpatched production self-check in the same process. Reads only the S2 list's items[0].

    PY tools/gpu_guard.py --log runs/P2-S2-SELFCHECK-DIAG/telemetry-<n>.csv --every 1 --max-temp 80 --max-minutes 10 -- PY runs/P2-S2-SELFCHECK-DIAG/diag_fixcheck.py --patched <file> --tag <n>
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patched", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    torch.cuda.set_per_process_memory_fraction(0.75)
    from exp_p2 import common, run_gate_s2
    from exp_p2.gate import runner
    from exp_p2.scoring import UniScorer
    raw = Path(a.patched).read_bytes()
    spec = importlib.util.spec_from_file_location("run_gate_s2_patched", a.patched)
    patched = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patched)
    items, _ = run_gate_s2.plan_items(300)
    sc = runner.Counting(UniScorer(common.load_net()))                       # the production load()
    fl = lambda: dict(benchmark=torch.backends.cudnn.benchmark, deterministic=torch.backends.cudnn.deterministic)
    res = dict(tag=a.tag, patched_sha256_lf=hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(), idx=items[0]["idx"], flags_before=fl())
    res["fixed"] = patched.selfcheck_deterministic(sc, items)
    res["fixed_passed"] = runner.selfcheck_passed(res["fixed"])
    res["flags_after_fixed"] = fl()
    res["production"] = sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])
    res["production_passed"] = runner.selfcheck_passed(res["production"])
    (OUT / f"fixcheck-{a.tag}.json").write_text(json.dumps(res, indent=1), encoding="utf8")
    print("fixed", res["fixed"]["image_tokens_frac_equal"], res["fixed_passed"], "production", res["production"]["image_tokens_frac_equal"], "flags", res["flags_before"], res["flags_after_fixed"], flush=True)


if __name__ == "__main__":
    main()
