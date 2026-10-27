"""Shared resumable item loop of the gate runners (same pattern as run_probe2.py): `runs/<run-id>/` with config.json, git SHA and env lock
(common.init_run), `items.jsonl` (one row per finished item, appended and fsynced AFTER the item's `arrays/itemNNNN.npz` is written atomically, so a row
is the commit marker), `chunks.jsonl` (events), soft deadline, duty cycle, per-item resource guards, exit codes 0 done / 75 more work / 2 selfcheck failed /
7 on hold. Re-running the same command resumes at the first item without a row; a torn last row is ignored and that item is redone.

The loop never imports a model: `load()` returns the scorer (UniScorer in production, the fake in tests)."""
from __future__ import annotations

import argparse
import sys
import time
import traceback
from pathlib import Path
from types import SimpleNamespace

from exp_p2 import common
from exp_p2.gate import hold
from exp_p2.gate.guards import Guards

EXIT_DONE, EXIT_MORE_WORK, EXIT_SELFCHECK = 0, 75, 2


def base_parser(default_run_id: str, default_n: int | None = None) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=default_run_id)
    ap.add_argument("--soft-minutes", type=float, default=12.5)
    ap.add_argument("--duty", type=float, default=0.5)
    ap.add_argument("--limit", type=int, default=None, help="stop after this many NEW items (smoke runs)")
    ap.add_argument("--n", type=int, default=default_n)
    ap.add_argument("--resume", action="store_true", help="accepted for symmetry with run_probe*; resuming is always on")
    ap.add_argument("--mem-frac", type=float, default=0.75, help="per-process CUDA memory cap (probe 2 used 0.75; the crash diagnosis suggests trying 0.60)")
    ap.add_argument("--max-used-mib", type=float, default=Guards.max_used_mib)
    ap.add_argument("--max-used-first-mib", type=float, default=Guards.max_used_first_mib)
    ap.add_argument("--max-rise-mib", type=float, default=Guards.max_rise_mib)
    ap.add_argument("--no-ac-check", action="store_true")
    return ap


def guards_from_args(a) -> Guards:
    return Guards(max_used_mib=a.max_used_mib, max_used_first_mib=a.max_used_first_mib, max_rise_mib=a.max_rise_mib, require_ac=not a.no_ac_check)


class Counting:
    """Proxy around a scorer that counts the rows pushed through the network (the 'passes' of the spec's itemised budgets)."""

    def __init__(self, sc):
        self._sc = sc
        self.rows = 0

    def __getattr__(self, k):
        return getattr(self._sc, k)

    def logits_fn(self, st):
        f = self._sc.logits_fn(st)

        def g(x):
            self.rows += int(x.shape[0])
            return f(x)
        return g


def repair_torn_tail(path: Path) -> bool:
    """After a hard kill the last JSONL line may be partial. common.append_jsonl would glue the next row onto it and lose that row, so end the file with a
    newline first (the partial line stays on disk, is skipped by common.read_jsonl, and its item is redone). Returns True if a repair was made."""
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return False
    with open(path, "rb+") as fh:
        fh.seek(-1, 2)
        if fh.read(1) == b"\n":
            return False
        fh.write(b"\n")
    return True


def _cuda():
    try:
        import torch
        return torch if torch.cuda.is_available() else None
    except ImportError:
        return None


def run_items(*, run_id: str, cfg: dict, load, get_items, process, make_ctx=None, soft_minutes: float = 12.5, duty: float = 0.5, limit: int | None = None,
              guards: Guards | None = None, mem_frac: float | None = None, selfcheck=None) -> int:
    """load() -> scorer; get_items(sc, run) -> list of dicts with a unique integer 'idx'; process(sc, item, ctx) -> (row dict, arrays dict);
    make_ctx(sc, run) -> context object; selfcheck(sc, items) -> dict or None (production: the UniScorer layout self-check, as probes 1 and 2)."""
    from exp001.runtools import Duty, Deadline, atomic_save_npz, atomic_write_json
    try:
        hold.require_clear(run_id)
    except hold.HoldActive as e:
        print("STOP:", e, file=sys.stderr)
        return hold.EXIT_HOLD
    dl, dty = Deadline(soft_minutes), Duty(duty)
    run = common.init_run(run_id, cfg)
    rows_path = run / "items.jsonl"
    repair_torn_tail(rows_path)
    done = {r["idx"] for r in common.read_jsonl(rows_path)}
    n_items = cfg.get("n_items")
    if n_items is not None and len(done) >= n_items:
        print("complete")
        return EXIT_DONE
    (run / "arrays").mkdir(exist_ok=True)
    torch = _cuda()
    if torch is not None and mem_frac:
        torch.cuda.set_per_process_memory_fraction(mem_frac)
    t_load = time.perf_counter()
    sc = load()
    load_s = time.perf_counter() - t_load
    items = get_items(sc, run)
    if n_items is not None:
        items = items[:n_items]
    if selfcheck is not None and not (run / "selfcheck.json").exists():
        chk = selfcheck(sc, items)
        if chk is not None:
            atomic_write_json(run / "selfcheck.json", chk)
            print("selfcheck", chk)
            if not (chk.get("ids_equal") and chk.get("modality_equal") and chk.get("image_tokens_frac_equal", 0) >= 0.99):
                print("SELF-CHECK FAILED", file=sys.stderr)
                return EXIT_SELFCHECK
    ctx = make_ctx(sc, run) if make_ctx else SimpleNamespace(run=run, cfg=cfg)
    common.append_jsonl(run / "chunks.jsonl", dict(event="chunk_start", t=time.time(), load_s=load_s, done=len(done), mem=_mem(), gpu=_gpu()))
    n_new = 0
    for it in items:
        idx = it["idx"]
        if idx in done:
            continue
        if dl.reached(margin_s=45):
            common.append_jsonl(run / "chunks.jsonl", dict(event="soft_deadline", t=time.time(), remaining=len(items) - len(done) - n_new))
            return EXIT_MORE_WORK
        if guards is not None:
            why = guards.before_item(n_new)
            if why:
                common.append_jsonl(run / "chunks.jsonl", dict(event="guard_stop", t=time.time(), reason=why, idx=idx))
                print("STOP:", why, file=sys.stderr)
                return EXIT_MORE_WORK
        t0 = time.perf_counter()
        if torch is not None:
            torch.cuda.reset_peak_memory_stats()
        try:
            row, arrays = process(sc, it, ctx)
        except Exception as e:                                   # failed items stay on disk: event row + traceback, then re-raise
            common.append_jsonl(run / "chunks.jsonl", dict(event="item_error", t=time.time(), idx=idx, error=repr(e), tb=traceback.format_exc()[-2000:]))
            raise
        if torch is not None:
            torch.cuda.synchronize()
        busy = time.perf_counter() - t0
        row = dict(row, idx=idx, seconds=busy, free_ram_gb=_mem().get("free_ram_gb"))
        if torch is not None:
            row["peak_gb"] = torch.cuda.max_memory_allocated() / 1e9
        if arrays:
            atomic_save_npz(run / "arrays" / f"item{idx:04d}.npz", **arrays)
        common.append_jsonl(rows_path, row)                      # commit marker
        n_new += 1
        dty.after_unit(busy)
        if guards is not None:
            why = guards.after_item(busy)
            if why:
                common.append_jsonl(run / "chunks.jsonl", dict(event="guard_stop", t=time.time(), reason=why, idx=idx))
                print("STOP:", why, file=sys.stderr)
                return EXIT_MORE_WORK
        if limit and n_new >= limit:
            return EXIT_DONE if len(done) + n_new >= len(items) else EXIT_MORE_WORK
    common.append_jsonl(run / "chunks.jsonl", dict(event="complete", t=time.time()))
    return EXIT_DONE


def _mem() -> dict:
    try:
        return common.mem_status()
    except Exception:
        return {}


def _gpu() -> dict:
    try:
        return common.gpu_state() if _cuda() is not None else {}
    except Exception:
        return {}
