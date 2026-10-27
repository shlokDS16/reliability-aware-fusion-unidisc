"""CPU report of M5: applies the pre-stated reading of Alg. 12 to runs/P2-GATE-M5/items.jsonl.

    python -m exp_p2.gate.coherence_report --run-id P2-GATE-M5 [--mu <clean mean per-token paired evidence measured in M4>]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import checks                                              # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-GATE-M5")
    ap.add_argument("--mu", type=float, default=None)
    a = ap.parse_args(argv)
    run = Path(common.RUNS) / a.run_id
    rows = common.read_jsonl(run / "items.jsonl")
    g = np.array([r["g"] for r in rows], float)
    g0 = np.array([r["g0"] for r in rows if "g0" in r], float)
    res = checks.coherence_summary(g, g0, a.mu)
    res["by_kind"] = {k: float(np.median(np.abs([r["g"][i] for r in rows for i, p in enumerate(r["pairs"]) if p["kind"] == k]))) for k in ("adjacent_h", "adjacent_v", "far")}
    res["by_context_median_abs"] = [float(np.median(np.abs(g[:, :, c]))) for c in (0, 1)]
    (run / "coherence.json").write_text(json.dumps(res, indent=1), encoding="utf8")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
