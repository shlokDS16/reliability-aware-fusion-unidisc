"""Probe-2 completion under the NEW guards (audit finding F2). `exp_p2/run_probe2.py` is not edited and its scoring is untouched; this wrapper runs its `main()` in the
same process after installing, from the outside:

  * the hold check (any hold file: exit 7) and an AC-power check, both BEFORE the model is loaded (it hooks `common.load_net`);
  * the per-process CUDA memory cap `--mem-frac` (default 0.75, as in probe 2) and a whole-GPU limit equal to the first-item allowance (probe 2's own item-level check then
    uses that value; the stricter later-item limit is enforced here);
  * before every item (it hooks `torch.cuda.mem_get_info`, which probe 2 calls once per item): hold file, AC, whole-GPU memory (first-item allowance, then the lower limit) and
    the rise rule;
  * after every committed row (it hooks `common.append_jsonl` for `items.jsonl`): the slow-item rule on the row's `seconds`;
  * the 1 s watchdog thread of `gate/watchdog.py` for memory jumps inside an item.
Any trip logs a `guard_stop` event to `chunks.jsonl` and exits with 76 (EXIT_GUARD); the driver never relaunches after 76.

    python -m exp_p2.gate.probe2_guarded --run-id P2-PROBE-02 --n 200 --resume --duty 0.5 --soft-minutes 12.5 [--limit N] [--mem-frac 0.75] [--max-used-mib ...]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import hold, runner                                        # noqa: E402
from exp_p2.gate.guards import Guards                                       # noqa: E402
from exp_p2.gate.watchdog import EXIT_GUARD                                 # noqa: E402


class GuardAbort(RuntimeError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _event(run_id: str, why: str, **kw):
    d = Path(common.RUNS) / run_id
    d.mkdir(parents=True, exist_ok=True)
    common.append_jsonl(d / "chunks.jsonl", dict(event="guard_stop", t=time.time(), source="probe2_guarded", reason=why, **kw))


def run_guarded(argv: list[str], *, probe_main=None, cuda=None, watchdog_factory=None, ac_fn=None) -> int:
    """probe_main/cuda/ac_fn are injectable for tests (default: run_probe2.main, torch.cuda, guards.on_ac)."""
    ap = argparse.ArgumentParser(add_help=False, allow_abbrev=False)          # abbreviations off: '--n' must never match '--no-ac-check'
    ap.add_argument("--mem-frac", type=float, default=0.75)
    ap.add_argument("--max-used-mib", type=float, default=Guards.max_used_mib)
    ap.add_argument("--max-used-first-mib", type=float, default=Guards.max_used_first_mib)
    ap.add_argument("--max-rise-mib", type=float, default=Guards.max_rise_mib)
    ap.add_argument("--no-ac-check", action="store_true")
    ga, rest = ap.parse_known_args(argv)
    rid_ap = argparse.ArgumentParser(add_help=False, allow_abbrev=False)          # abbreviations off: '--n' must never match '--no-ac-check'
    rid_ap.add_argument("--run-id", default="P2-PROBE-02")
    ra, _ = rid_ap.parse_known_args(rest)
    run_id = ra.run_id
    try:
        hold.require_clear(run_id)
    except hold.HoldActive as e:
        print("STOP:", e, file=sys.stderr)
        return hold.EXIT_HOLD
    g = Guards(max_used_mib=ga.max_used_mib, max_used_first_mib=ga.max_used_first_mib, max_rise_mib=ga.max_rise_mib, require_ac=not ga.no_ac_check, **({"ac_fn": ac_fn} if ac_fn else {}))
    if g.require_ac and g.ac_fn() is False:
        _event(run_id, "ac_lost_before_load")
        print("STOP: running on battery (checked before the model load)", file=sys.stderr)
        return EXIT_GUARD

    if probe_main is None:
        from exp_p2 import run_probe2 as rp
        probe_main = rp.main
        rp.MEM_FRAC, rp.MAX_GPU_USED_MIB = ga.mem_frac, ga.max_used_first_mib      # probe 2 reads these module globals at run time
    if cuda is None:
        import torch
        cuda = torch.cuda
    orig_mem, orig_append, orig_load = cuda.mem_get_info, common.append_jsonl, common.load_net

    def used_mib() -> float:
        free_b, total_b = orig_mem()
        return (total_b - free_b) / 2**20
    g.used_fn = used_mib
    state = {"done": 0}

    def mem_info():                                         # probe 2 calls this once per item, before the item starts
        held = hold.active_holds(run_id)
        if held:
            raise GuardAbort("hold_appeared " + "; ".join(str(h) for h in held))
        why = g.before_item(state["done"])
        if why:
            raise GuardAbort(why)
        return orig_mem()

    def append(path, row):
        orig_append(path, row)                              # the row is committed first; then the slow-item rule may stop the run
        if Path(path).name == "items.jsonl" and isinstance(row, dict) and "seconds" in row:
            state["done"] += 1
            why = g.after_item(float(row["seconds"]))
            if why:
                raise GuardAbort(why)

    def load_net(*a, **k):                                  # checks that must precede the model load
        held = hold.active_holds(run_id)
        if held:
            raise GuardAbort("hold_appeared " + "; ".join(str(h) for h in held))
        if g.require_ac and g.ac_fn() is False:
            raise GuardAbort("ac_lost_before_load")
        return orig_load(*a, **k)

    cuda.mem_get_info, common.append_jsonl, common.load_net = mem_info, append, load_net
    wd = (watchdog_factory or runner.default_watchdog)(g, Path(common.RUNS) / run_id)
    old_argv = sys.argv
    sys.argv = ["run_probe2"] + rest
    try:
        wd.start()
        return int(probe_main() or 0)
    except GuardAbort as e:
        _event(run_id, e.reason)
        print("STOP:", e.reason, file=sys.stderr)
        return hold.EXIT_HOLD if e.reason.startswith("hold_appeared") else EXIT_GUARD
    finally:
        sys.argv = old_argv
        wd.stop()
        cuda.mem_get_info, common.append_jsonl, common.load_net = orig_mem, orig_append, orig_load


def main(argv=None) -> int:
    return run_guarded(list(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    sys.exit(main())
