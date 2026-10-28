"""S2 smoke with an outcome firewall (SAP A3.2 item 2, A3b.7 item 4). GPU runner; its author has NOT executed it on a GPU.

    python -m exp_p2.run_gate_s2_smoke [--run-id P2-GATE-S2-SMOKE] [--limit 3] [--n 300] [--arms igate,irand,ichg] [--m4-run P2-GATE-M4] [runner flags]

Runs the real S2 item loop (`run_gate_s2.main`, same prerequisites, same sampler, same guards) on the first `--limit` (default 3) items of the S2 list under a SEPARATE run id, to measure `peak_gb`, `seconds` and the
number of network rows `n_rows` and nothing else. The firewall: the item function is wrapped so that the row handed to the runner holds `n_rows` only (the runner adds idx, seconds, free_ram_gb and, with CUDA,
peak_gb) and the arrays are dropped, so no Y, no draw, no position set, no arm comparison and no token is ever written to the smoke directory; the runner's console output is discarded; this script prints
and stores (runs/<run-id>/smoke_summary.json) the three lists `peak_gb`, `seconds`, `n_rows` (one value per item) and nothing else. `analysis_s2` is not run on the smoke directory (its rows carry no cells).
Its Y values, I-GATE versus I-RAND4 comparisons and figures cannot be read from it and are not used: the items are re-run inside the real run (A3.2 item 2). The firewall is also an honour rule: the run card
records this script (A3b.7 item 4). A crash found by the smoke may be fixed; a sampler parameter may not be changed."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, run_gate_s2                                        # noqa: E402

SMOKE_RUN_ID = "P2-GATE-S2-SMOKE"
DEFAULT_LIMIT = 3
ROW_KEYS_ALLOWED = {"idx", "seconds", "free_ram_gb", "peak_gb", "n_rows"}       # the keys a smoke row may ever hold (the runner adds all but n_rows)
SUMMARY_KEYS = ("peak_gb", "seconds", "n_rows")


def firewall(process):
    """Wrap an S2 item function so that only the number of network rows leaves it; the arrays (codes, sets, chain likelihoods) are dropped."""
    def wrapped(sc, it, ctx):
        row, _arrays = process(sc, it, ctx)
        return {"n_rows": row.get("n_rows")}, {}
    return wrapped


def summarize(run_dir: Path) -> dict:
    """The only thing the smoke reports: per item `peak_gb` (None without CUDA), `seconds`, `n_rows`."""
    rows = common.read_jsonl(Path(run_dir) / "items.jsonl")
    return {k: [r.get(k) for r in rows] for k in SUMMARY_KEYS}


def main(argv=None, *, load=None) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run-id", default=SMOKE_RUN_ID)
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    known, rest = ap.parse_known_args(argv)
    if known.run_id in (run_gate_s2.RUN_ID, run_gate_s2.FIG_RUN_ID):
        print(f"STOP: the smoke must use its own run id, not {known.run_id} (the real run would resume from it)", file=sys.stderr)
        return 2
    if "--figures" in rest:
        print("STOP: the smoke never decodes figures (A3.2 item 2)", file=sys.stderr)
        return 2
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):                                       # selfcheck dict, 'complete': nothing but the three lists may be printed
        code = run_gate_s2.main(["--run-id", known.run_id, "--limit", str(known.limit)] + rest, process_wrap=firewall, load=load)
    out = summarize(Path(common.RUNS) / known.run_id)
    run_dir = Path(common.RUNS) / known.run_id
    if run_dir.exists():
        (run_dir / "smoke_summary.json").write_text(json.dumps(out), encoding="utf8")
    print(json.dumps(out))
    return code


if __name__ == "__main__":
    sys.exit(main())
