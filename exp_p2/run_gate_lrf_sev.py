"""Severity sweep (research/paper2/tnnls/EXPLORATORY-PLAN-SEVERITY-2026-10-31.md): Gaussian noise at sigma 0.05, 0.2 and 0.3 on the Study 2 fresh fold, scored as L1. EXPLORATORY.

    python -m exp_p2.run_gate_lrf_sev --sweep noise --run-id P2-LRF-SEV <the lrf-l1 flags> [--limit N] [--soft-minutes M]
    python -m exp_p2.gate.gate_driver --stage lrf-sev --extra "<guard flags>"          # the production route (chunked, resumable, telemetry)

A thin entry point around the pinned L1 runner `exp_p2/run_gate_m4.py`, which it does NOT edit (pattern of `exp_p2/run_gate_lrf_dn.py`). With `--sweep none` (the default) it calls
`run_gate_m4.main` and patches nothing. With `--sweep noise` it swaps in, for the duration of the call only:
  * `build_conditions`  the conditions of an item are `noise0.05`, `noise0.2`, `noise0.3`: `corruptions.apply_pixel("noise", sigma, ...)` with the noise0.1 stream of L1 for EVERY level,
                        `rung_rng(gid, "noise", 0)` (common random numbers: numpy Generator.normal(0, sigma) is sigma times the same standard normal for one seed, so the levels differ in
                        severity only). Each is a full `pixel` condition (B, D, s3, tbv, tex, nbr, flags, delta, deltaL stored), marked `extra` so the text-direction passes are skipped, and
                        `python -m exp_p2.gate.lrf_score --conds noise0.05,noise0.2,noise0.3` scores it with the frozen LRF exactly as L1. Clean and noise0.1 are NOT re-run (they are in P2-LRF-L1).
                        Positive control (encode only, no network pass): the sigma 0.1 image is rebuilt with the same call and stored as `noise0.1_codes_crn`, to compare with L1's `noise0.1_codes`.
  * `process`          = the L1 `process`, plus `noise0.1_codes_crn`.
  * `run_items`        the run config records the sweep levels and the stream.
Required flags with --sweep noise (checked before the model is touched): the L1 set `--folds-path runs/P2-LRF-FOLD/folds_lrf.json --family-run P2-LRF-PLAN --sanity "" --denoise-for ""
--tbv on --layout-fix 13 --neg-len`, and a run id that is not one of the existing runs."""
from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import run_gate_m4 as m4                                               # noqa: E402
from exp_p2 import run_gate_lrf_dn as dn                                           # noqa: E402  (check_flags: the L1 flag set)
from exp_p2.gate import config, corruptions, runner                                # noqa: E402

RUN_ID = "P2-LRF-SEV"
SWEEP_MODES = ("none", "noise")
SIGMAS = (0.05, 0.2, 0.3)
REF_SIGMA = 0.1                                   # L1's noise level; its stream (ladder rung 0) is used for every level
PC_KEY = "noise0.1_codes_crn"
PROTECTED_RUN_IDS = dn.PROTECTED_RUN_IDS + ("P2-LRF-DN",)
L_FIX = 13


def sev_key(sigma: float) -> str:
    return corruptions.corruption_key("noise", float(sigma))


def ref_rung() -> int:
    r = list(config.LADDERS["noise"]).index(REF_SIGMA)
    if r != 0:
        raise ValueError(f"noise {REF_SIGMA} is ladder rung {r}, expected 0 (the L1 stream)")
    return r


def noisy(pil, gid: int, sigma: float):
    """The L1 noise call with L1's noise0.1 stream at another sigma (common random numbers)."""
    return corruptions.apply_pixel("noise", float(sigma), pil, m4.rung_rng(gid, "noise", ref_rung()), None)


def build_conditions_sev(sc, it, pil, clean, ctx) -> list[dict]:
    if not getattr(ctx, "tbv", False) or getattr(ctx, "slot_len", None) != L_FIX or not getattr(ctx, "neg_len", False):
        raise ValueError("--sweep noise needs --tbv on, --layout-fix 13 and --neg-len (the L1 settings)")
    if ("noise", REF_SIGMA) not in [(c, float(s)) for c, s in ctx.family]:
        raise ValueError(f"the family {ctx.family} has no noise{REF_SIGMA:g} cell (L1's)")
    gid = it["gid"]
    ctx.sev_side[gid] = sc.encode(noisy(pil, gid, REF_SIGMA))                                # positive control, encode only
    conds = []
    for s in SIGMAS:
        img = noisy(pil, gid, s)
        conds.append(dict(name=sev_key(s), kind="pixel", codes=sc.encode(img), pix=np.asarray(img), corr="noise", extra=True))
    return conds


def make_process_sev(orig_process):
    def process_sev(sc, it, ctx):
        row, arrays = orig_process(sc, it, ctx)
        arrays[PC_KEY] = np.asarray(ctx.sev_side.pop(it["gid"])).astype(np.int16)
        return row, arrays
    return process_sev


def sweep_record() -> dict:
    return dict(sweep="noise", sigmas=list(SIGMAS), stream=f"rung_rng(gid, 'noise', {ref_rung()}) for every level (the L1 noise0.1 stream; common random numbers)",
                positive_control=f"{PC_KEY} vs P2-LRF-L1 noise0.1_codes", exploratory_plan="research/paper2/tnnls/EXPLORATORY-PLAN-SEVERITY-2026-10-31.md",
                l1_runner="exp_p2/run_gate_m4.py (unchanged); score with exp_p2.gate.lrf_score --conds " + ",".join(sev_key(s) for s in SIGMAS))


@contextlib.contextmanager
def sev_patched(record: dict | None = None):
    """Install the sweep hooks on `run_gate_m4` for the duration of the block and restore the originals on exit (also on error)."""
    saved = dict(build_conditions=m4.build_conditions, process=m4.process, make_ctx_factory=m4.make_ctx_factory, run_items=runner.run_items)

    def make_ctx_factory(a, runs=None):
        inner = saved["make_ctx_factory"](a, runs)

        def make_ctx(sc, run):
            ctx = inner(sc, run)
            ctx.sev_side = {}
            return ctx
        return make_ctx

    def run_items(**kw):
        return saved["run_items"](**dict(kw, cfg=dict(kw["cfg"], **(record or {}))))

    m4.build_conditions, m4.process, m4.make_ctx_factory = build_conditions_sev, make_process_sev(saved["process"]), make_ctx_factory
    runner.run_items = run_items
    try:
        yield
    finally:
        m4.build_conditions, m4.process, m4.make_ctx_factory = saved["build_conditions"], saved["process"], saved["make_ctx_factory"]
        runner.run_items = saved["run_items"]


def check_flags(rest: list[str]) -> list[str]:
    """The L1 flag checks of the denoiser entry point, with P2-LRF-DN also protected."""
    bad = dn.check_flags(rest)
    ap = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    ap.add_argument("--run-id", default=None)
    a, _ = ap.parse_known_args(rest)
    if a.run_id in PROTECTED_RUN_IDS and not any("--run-id" in b for b in bad):
        bad.append(f"--run-id must not be one of {PROTECTED_RUN_IDS} (got {a.run_id!r})")
    return bad


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    ap.add_argument("--sweep", choices=SWEEP_MODES, default="none", help="none = the L1 runner, nothing patched; noise = the severity sweep (module docstring)")
    a, rest = ap.parse_known_args(argv)
    if a.sweep == "none":
        return m4.main(rest)
    bad = check_flags(rest)
    if bad:
        print("STOP: " + "; ".join(bad), file=sys.stderr)
        return 2
    with sev_patched(sweep_record()):
        return m4.main(rest)


if __name__ == "__main__":
    sys.exit(main())
