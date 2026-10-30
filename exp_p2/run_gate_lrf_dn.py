"""E1 (research/paper2/tnnls/EXPLORATORY-PLAN-BASELINES-2026-10-30.md): a classical pixel denoiser applied BEFORE UniDisc scoring, on the Study 2 fresh fold. EXPLORATORY.

    python -m exp_p2.run_gate_lrf_dn --denoise nlm-sdn --run-id P2-LRF-DN <the lrf-l1 flags> [--limit N] [--soft-minutes M]
    python -m exp_p2.gate.gate_driver --stage lrf-dn --extra "<guard flags>"          # the production route (chunked, resumable, telemetry)

This module is a thin entry point around the pinned L1 runner `exp_p2/run_gate_m4.py`, which it does NOT edit (the A6.0 pins file pins that file's hash, and `lrf_score` re-checks it). With
`--denoise none` (the default) it simply calls `run_gate_m4.main` and patches nothing. With `--denoise nlm-sdn` it swaps in, for the duration of the call only, two hooks of the L1 item
function and one wrapper of the run loop:
  * `build_conditions`  the conditions of an item are the denoised copies of the family's `jpeg10` and `noise0.1` cells, named `<key>_nlm` (`jpeg10_nlm`, `noise0.1_nlm`): the SAME corruption call
                        with the SAME seed (`rung_rng(gid, corr, rung)`, as L1), then `corruptions.denoise` = OpenCV fastNlMeansDenoisingColored with `config.DENOISE_PARAMS`, unchanged (Study 1's
                        S-DN arm, `denoise_check.chosen`), then `sc.encode`. Each is a full `pixel` condition, so everything L1 stores for a condition (B, D, s3, tbv, tex, nbr, flags, delta, deltaL) is stored
                        and `python -m exp_p2.gate.lrf_score --conds noise0.1_nlm,jpeg10_nlm` scores it with the frozen LRF exactly as L1. They are marked `extra`, which M4 already uses to skip the
                        text-direction passes. The clean and splice cells and the undenoised cells are NOT re-run (they are in runs/P2-LRF-L1).
  * `process`          = the L1 `process`, plus the codes of the corrupted-but-not-denoised image as `<key>_nlm_codes_corr` (to check against L1's stored `<key>_codes`).
  * `run_items`        the run config records `denoise`, the denoiser parameters and the OpenCV version.
The guards, telemetry, chunking and resume are those of the L1 runner and driver. Required flags with --denoise nlm-sdn (checked before the model is touched): the L1 set `--folds-path
runs/P2-LRF-FOLD/folds_lrf.json --family-run P2-LRF-PLAN --sanity "" --denoise-for "" --tbv on --layout-fix 13 --neg-len`, and a run id that is not one of the existing runs."""
from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, run_gate_m4 as m4                                       # noqa: E402
from exp_p2.gate import config, corruptions, runner                                # noqa: E402

RUN_ID = "P2-LRF-DN"
DENOISE_MODES = ("none", "nlm-sdn")
DN_CORRUPTIONS = ("jpeg", "noise")              # the two S-DN conditions (Study 1); splice is not denoised
SUFFIX = "_nlm"
PROTECTED_RUN_IDS = ("P2-GATE-M4", "P2-LRF-L1", "P2-LRF-LG", "P2-LRF-RESCORE", "P2-GATE-H3", "P2-GATE-H4")
L_FIX = 13


def dn_key(corr: str, severity) -> str:
    return corruptions.corruption_key(corr, severity) + SUFFIX


def denoise_nlm_sdn(pil512):
    """Study 1's S-DN denoiser, unchanged: `corruptions.denoise` with config.DENOISE_PARAMS (== denoise_check.chosen)."""
    return corruptions.denoise(pil512)


def build_conditions_dn(sc, it, pil, clean, ctx) -> list[dict]:
    """The denoised copies of the family's jpeg and noise cells, as full `pixel` conditions (see the module docstring). Same corruption seed as L1."""
    if not getattr(ctx, "tbv", False) or getattr(ctx, "slot_len", None) != L_FIX or not getattr(ctx, "neg_len", False):
        raise ValueError("--denoise nlm-sdn needs --tbv on, --layout-fix 13 and --neg-len (the L1 settings)")
    gid = it["gid"]
    side = ctx.dn_side.setdefault(gid, {})
    conds = []
    for corr, sev in ctx.family:
        if corr not in DN_CORRUPTIONS:
            continue
        r = list(config.LADDERS[corr]).index(sev)
        img = corruptions.apply_pixel(corr, sev, pil, m4.rung_rng(gid, corr, r), None)       # identical call and seed to run_gate_m4.build_conditions
        den = denoise_nlm_sdn(img)
        name = dn_key(corr, sev)
        side[name] = sc.encode(img)
        conds.append(dict(name=name, kind="pixel", codes=sc.encode(den), pix=np.asarray(den), corr=corr, extra=True))
    if not conds:
        raise ValueError(f"the family {ctx.family} has no jpeg or noise cell to denoise")
    return conds


def make_process_dn(orig_process):
    def process_dn(sc, it, ctx):
        row, arrays = orig_process(sc, it, ctx)
        for name, codes in ctx.dn_side.pop(it["gid"], {}).items():
            arrays[f"{name}_codes_corr"] = np.asarray(codes).astype(np.int16)
        return row, arrays
    return process_dn


def denoise_record() -> dict:
    import cv2
    return dict(denoise="nlm-sdn", denoise_params=dict(config.DENOISE_PARAMS), denoise_function="exp_p2.gate.corruptions.denoise (cv2.fastNlMeansDenoisingColored)", opencv=cv2.__version__,
                denoise_conditions=[dn_key(c, s) for c in DN_CORRUPTIONS for s in (config.LADDERS[c][0],)], exploratory_plan="research/paper2/tnnls/EXPLORATORY-PLAN-BASELINES-2026-10-30.md E1",
                l1_runner="exp_p2/run_gate_m4.py (unchanged); score with exp_p2.gate.lrf_score --conds noise0.1_nlm,jpeg10_nlm")


@contextlib.contextmanager
def dn_patched(record: dict | None = None):
    """Install the E1 hooks on `run_gate_m4` for the duration of the block and restore the originals on exit (also on error)."""
    saved = dict(build_conditions=m4.build_conditions, process=m4.process, make_ctx_factory=m4.make_ctx_factory, run_items=runner.run_items)

    def make_ctx_factory(a, runs=None):
        inner = saved["make_ctx_factory"](a, runs)

        def make_ctx(sc, run):
            ctx = inner(sc, run)
            ctx.dn_side = {}
            return ctx
        return make_ctx

    def run_items(**kw):
        return saved["run_items"](**dict(kw, cfg=dict(kw["cfg"], **(record or {}))))

    m4.build_conditions, m4.process, m4.make_ctx_factory = build_conditions_dn, make_process_dn(saved["process"]), make_ctx_factory
    runner.run_items = run_items
    try:
        yield
    finally:
        m4.build_conditions, m4.process, m4.make_ctx_factory = saved["build_conditions"], saved["process"], saved["make_ctx_factory"]
        runner.run_items = saved["run_items"]


def check_flags(rest: list[str]) -> list[str]:
    """Problems with the L1 flags given with --denoise nlm-sdn (empty = fine). `--run-id` must be given and must not be an existing run."""
    ap = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--tbv", default=None)
    ap.add_argument("--sanity", default=None)
    ap.add_argument("--denoise-for", default=None)
    ap.add_argument("--folds-path", default=None)
    ap.add_argument("--family-run", default=None)
    ap.add_argument("--layout-fix", "--caption-slot-len", dest="slot", type=int, default=None)
    ap.add_argument("--neg-len", action="store_true")
    ap.add_argument("--extra-cells", default="")
    ap.add_argument("--gate-true-layout", action="store_true")
    a, _ = ap.parse_known_args(rest)
    bad = []
    if not a.run_id or a.run_id in PROTECTED_RUN_IDS:
        bad.append(f"--run-id must be given and must not be one of {PROTECTED_RUN_IDS} (got {a.run_id!r})")
    for flag, val, want in (("--tbv", a.tbv, "on"), ("--sanity", a.sanity, ""), ("--denoise-for", a.denoise_for, ""), ("--layout-fix", a.slot, L_FIX), ("--family-run", a.family_run, "P2-LRF-PLAN")):
        if val != want:
            bad.append(f"{flag} must be {want!r} (got {val!r})")
    if not a.neg_len:
        bad.append("--neg-len is required")
    if not a.folds_path:
        bad.append("--folds-path is required (runs/P2-LRF-FOLD/folds_lrf.json)")
    if a.extra_cells or a.gate_true_layout:
        bad.append("--extra-cells and --gate-true-layout are not allowed")
    return bad


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    ap.add_argument("--denoise", choices=DENOISE_MODES, default="none", help="none = the L1 runner, nothing patched; nlm-sdn = E1 (module docstring)")
    a, rest = ap.parse_known_args(argv)
    if a.denoise == "none":
        return m4.main(rest)
    bad = check_flags(rest)
    if bad:
        print("STOP: " + "; ".join(bad), file=sys.stderr)
        return 2
    with dn_patched(denoise_record()):
        return m4.main(rest)


if __name__ == "__main__":
    sys.exit(main())
