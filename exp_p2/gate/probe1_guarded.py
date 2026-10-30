"""M0 stage 2 under the new guards: the probe-1 control run with `exp_p2/run_probe1.py` unchanged. Same wrapper as `probe2_guarded` (hold check, AC before the model load,
per-item memory/rise/AC check, slow-item rule, 1 s watchdog, memory cap `--mem-frac` set from outside because probe 1 has none, abort exit 76, argparse abbreviations off),
with one difference: probe 1 does not query GPU memory per item, so the before-item check hooks the `torch.cuda.reset_peak_memory_stats()` call that probe 1 makes at the start of
every item. Prints a one-line event-log check first.

    python tools/gpu_guard.py --log runs/P2-M0-STAGE2/telemetry.csv --every 1 --max-temp 80 --max-minutes 12 -- <project .venv python> -m exp_p2.gate.probe1_guarded ^
        --run-id P2-M0-STAGE2 --n 10 --limit 10 --soft-minutes 10
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2.gate import probe2_guarded as _g                                # noqa: E402


def run_guarded(argv, **kw) -> int:
    return _g.run_guarded(list(argv), spec=_g.PROBE1_SPEC, **kw)


def main(argv=None) -> int:
    return run_guarded(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())
