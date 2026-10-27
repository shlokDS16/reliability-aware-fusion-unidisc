"""M0 stage 1 of the crash diagnosis (PROBE2-CRASH-DIAGNOSIS-2026-10-28.md section 5): load UniDisc only, run ONE batch-4 forward, then idle for a few minutes
while the guard logs 1 s telemetry. It answers 'does the driver survive load, one ramp and idle?' and nothing else. It scores nothing and writes no items.

    python tools/gpu_guard.py --log runs/P2-M0-STAGE1/telemetry.csv --every 1 --max-temp 80 --max-minutes 12 -- ^
        <project .venv python> -m exp_p2.run_gate_m0 --run-id P2-M0-STAGE1 --idle-minutes 5

Refuses to start while any hold file exists (exit 7). Prints whole-GPU memory every 10 s so an abort rule can be applied by eye as well as by the guard."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import hold                                                # noqa: E402


def one_batch(sc, rows: int = 4) -> float:
    """One forward of `rows` rows (the production batch) on a dummy image and caption; returns seconds. Uses the same masked_logprobs path as every probe."""
    import numpy as np
    import torch
    from exp_p2.scoring import Spec, masked_logprobs, IMG_LO, IMG_HI
    st = sc.build([100 + i for i in range(10)], np.zeros(sc.L_I, np.int64))
    specs = [Spec(st["img_pos"][k::rows], IMG_LO, IMG_HI) for k in range(rows)]
    t0 = time.perf_counter()
    for lp in masked_logprobs(sc.logits_fn(st), st["base"], specs):
        pass
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    return time.perf_counter() - t0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-M0-STAGE1")
    ap.add_argument("--idle-minutes", type=float, default=5.0)
    ap.add_argument("--mem-frac", type=float, default=0.75)
    a = ap.parse_args(argv)
    try:
        hold.require_clear(a.run_id)
    except hold.HoldActive as e:
        print("STOP:", e, file=sys.stderr)
        return hold.EXIT_HOLD
    from exp_p2.gate import guards
    if guards.on_ac() is False:                                           # audit F3: power state is checked before CUDA or the model is touched
        print("STOP: running on battery; plug in the AC adapter first", file=sys.stderr)
        return 76
    import torch
    run = common.RUNS / a.run_id
    run.mkdir(parents=True, exist_ok=True)
    torch.cuda.set_per_process_memory_fraction(a.mem_frac)
    t0 = time.perf_counter()
    from exp_p2.scoring import UniScorer
    sc = UniScorer(common.load_net())
    load_s = time.perf_counter() - t0
    fwd_s = one_batch(sc)
    log = [dict(event="loaded_and_one_forward", load_s=load_s, forward_s=fwd_s, peak_gb=torch.cuda.max_memory_allocated() / 1e9, gpu=common.gpu_state())]
    print(log[0], flush=True)
    t_end = time.time() + a.idle_minutes * 60
    while time.time() < t_end:
        time.sleep(10)
        g = common.gpu_state()
        log.append(dict(event="idle", t=time.time(), gpu=g))
        print("idle", g, flush=True)
    (run / "stage1.json").write_text(json.dumps(log, indent=1), encoding="utf8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
