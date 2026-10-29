"""LRF re-freeze stage (coordinator addendum to A6.11; LRF-FROZEN report section 3): re-score the caption-withheld scores of the existing M4 items at a FIXED caption-slot length (L_FIX = 13) into a new run id, storing only what LRF needs.

    python -m exp_p2.run_gate_lrf_rescore --resume --soft-minutes 12.5 [--limit N] [--n 500] [--source-run P2-GATE-M4] [--slot-len 13] [--run-id P2-GATE-M4-LFIX]

What is re-used and what is re-scored. The source run (default runs/P2-GATE-M4) already holds, per item and condition, the corrupted token codes, the changed-code labels z, the paired evidence Delta (caption visible, own
lengths: unchanged by the fixed slot), the patch texture `tex` and the neighbour codebook distance `nbr` (both depend on pixels and codes only). Those are copied as stored: nothing is re-encoded and no Lambda pass is made.
Re-scored, on the GPU, per condition at the fixed slot (`sc.build([PAD] * L_FIX, codes)`; every one of these passes masks the caption, so the slot content is irrelevant and only the count matters):
    B and s3   8 complementary-mask passes (scores.image_B), D from the cached layout-only null of length L_FIX (DI_n013.npy), tbv 1 pass (raw logits)  ->  9 passes per condition, 36 per item (4 conditions)
GATE-M flags (`<cond>_flag<alpha>`) are re-derived from the fixed-layout u with the M2 threshold and the SAME jitter stream as the source run (condition index = position in the source row's conditions); the M4 GATE-M
arm of the source run is untouched. They are stored because analysis_posthoc.learned_ceiling.data.load reads `flag0.05`; they are not an input of LRF.

Stored per item (arrays/itemNNNN.npz, the key names data.load reads): `<cond>_{codes,z,delta,B,D,s3,tbv,tex,nbr,flag0.05,flag0.01,flag0.1}` for the conditions in --conds (default clean, jpeg10, noise0.1, splice128).
Invariance check (A6.2 step 3, L10-style, before any outcome): for the first INV_ITEMS items and every condition, B, D, s3 and tbv are recomputed with the slot filled by the c+ tokens and by the c- tokens (padded or cut to L_FIX)
and compared with the PAD slot; the maximum absolute differences are written into the item row (`invariance`, `invariance_max_abs_diff`) and must be 0.
Positive control (A6.2 step 2): for the same items and conditions the scores are also computed at the item's TRUE caption length and compared with the stored source arrays (`positive_control`, `positive_control_max_abs_diff`, tolerance PC_TOL = 1e-5);
the run's config.json records the SHA-256 of runs/P2-GATE-M1/codebook.npy and of the D-cache file DI_n<slot>.npy (A6.2 hash set).
The source run's arrays are only read."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                          # noqa: E402
from exp_p2.gate import arms, calibrate as cal, config, pipeline, runner, scores   # noqa: E402
from exp_p2.run_gate_m4 import input_hashes, load_prereqs, slot_tokens, M3_RUN                    # noqa: E402

RUN_ID = "P2-GATE-M4-LFIX"
SOURCE_RUN = "P2-GATE-M4"
L_FIX = 13                                                                          # the M4 median true-caption length (LRF-FROZEN report section 3)
CONDS = ("clean", "jpeg10", "noise0.1", "splice128")                                # = analysis_posthoc.learned_ceiling.data.COND
INV_ITEMS = 5
PC_TOL = 1e-5                                                                       # A6.2 step 2: positive control at the TRUE length reproduces the stored M4 B, s3, D, tbv within this (GPU arithmetic)
INV_TOL = 0.0                                                                       # A6.2 step 3: invariance is exact; a looser bound (1e-6) is only the gate-auditor's, by a dated row before any re-frozen output exists
COPIED = ("codes", "z", "delta", "tex", "nbr")                                      # read from the source arrays, not recomputed
CONFIG = dict(stage="M4-LFIX", source_run=SOURCE_RUN, slot_len=L_FIX, conds=list(CONDS), seed=config.SEED_GATE, K=config.K, n_items=500,
              spec="research/paper2/posthoc/LRF-FROZEN-2026-10-29.md section 3 (length-neutral layout); SAP addendum A6 (DRAFT)")


def fit_slot(tokens: list[int], n: int) -> list[int]:
    """Caption tokens cut or padded (PAD) to n, for the invariance check only."""
    return (list(tokens) + slot_tokens(n))[:n]


def source_arrays(runs: Path, source_run: str, idx: int) -> dict:
    p = Path(runs) / source_run / "arrays" / f"item{idx:04d}.npz"
    if not p.exists():
        raise FileNotFoundError(f"{p} missing: the source run must have stored this item's arrays")
    return dict(np.load(p))


def fixed_layout_scores(sc, slot_tok: list[int], codes: np.ndarray, groups: np.ndarray, dcache, K: int = config.K) -> dict:
    """B, D, s3, u (gate_scores) and the raw-logit tbv score, all on the layout with `slot_tok` in the caption slot (9 passes)."""
    gs = pipeline.gate_scores(sc, slot_tok, codes, groups, dcache, K)
    gs["tbv"] = scores.tbv_score_raw_logits(sc, sc.build(slot_tok, codes))
    return gs


def invariance(sc, gs_pad: dict, cap_tok, neg_tok, codes, groups, dcache, n: int) -> dict:
    """Max absolute difference of B, D, s3, tbv between the PAD slot and a slot holding c+ / c- (cut or padded to n). Costs 18 passes per call."""
    out = {}
    for tag, tok in (("pos", cap_tok), ("neg", neg_tok)):
        g = fixed_layout_scores(sc, fit_slot(tok, n), codes, groups, dcache)
        for k in ("B", "D", "s3", "tbv"):
            out[f"{tag}_{k}"] = float(np.abs(np.asarray(g[k], np.float64) - np.asarray(gs_pad[k], np.float64)).max())
    return out


def positive_control(sc, src: dict, name: str, cap_tok, codes, groups, dcache) -> float:
    """Max abs difference between B, s3, D, tbv scored at the item's TRUE caption length and the stored source arrays (the entry point reproduces M4 when the slot is the true length)."""
    g = fixed_layout_scores(sc, list(cap_tok), codes, groups, dcache)
    return max(float(np.abs(np.asarray(g[k], np.float64) - np.asarray(src[f"{name}_{k}"], np.float64)).max()) for k in ("B", "s3", "D", "tbv") if f"{name}_{k}" in src)


def process(sc, it, ctx):
    gid, K = it["gid"], config.K
    rows0 = getattr(sc, "rows", None)
    src = source_arrays(ctx.runs, ctx.source_run, it["idx"])
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it.get("neg_caption", it["caption"]))
    groups = pipeline.item_groups(sc, gid, K)
    slot = slot_tokens(ctx.slot_len)
    row, arrays = dict(gid=gid, image_id=it["image_id"], n_tok=len(cap_tok), slot_len=int(ctx.slot_len), source_run=ctx.source_run, conds={}), {}
    inv, pc = {}, {}
    for name in ctx.conds:
        codes = src[f"{name}_codes"].astype(np.int64)
        gs = fixed_layout_scores(sc, slot, codes, groups, ctx.dcache, K)
        ci = ctx.cond_index(it, name)                                               # the source run's condition index: the same jitter stream as the source GATE-M flags
        uj = cal.jitter(gs["u"], ctx.eps0, arms.arm_rng(config.SEED_GATE, gid, ci, arms.ARM_TAG["jitter"], 0))
        flags = {al: uj > t.tau for al, t in ctx.thr.items()}
        arrays.update({f"{name}_{k}": src[f"{name}_{k}"] for k in COPIED})
        arrays.update({f"{name}_B": gs["B"], f"{name}_D": gs["D"].astype(np.float32), f"{name}_s3": gs["s3"], f"{name}_tbv": gs["tbv"]})
        for al, f in flags.items():
            arrays[f"{name}_flag{al:g}"] = f
        row["conds"][name] = dict(cond_index=int(ci), n_flag=int(flags[config.ALPHA_PRIMARY].sum()))
        if it["idx"] < INV_ITEMS:
            inv[name] = invariance(sc, gs, cap_tok, neg_tok, codes, groups, ctx.dcache, ctx.slot_len)
            pc[name] = positive_control(sc, src, name, cap_tok, codes, groups, ctx.dcache)
    if inv:
        row["invariance"] = inv
        row["invariance_max_abs_diff"] = max(v for d in inv.values() for v in d.values())
        row["positive_control"] = pc
        row["positive_control_max_abs_diff"] = max(pc.values())
        row["checks_ok"] = bool(row["invariance_max_abs_diff"] <= INV_TOL and row["positive_control_max_abs_diff"] <= PC_TOL)
    if isinstance(rows0, int):
        row["n_rows"] = int(sc.rows) - rows0
    return row, arrays


def make_ctx_factory(a, runs: Path | None = None):
    def make_ctx(sc, run):
        runs_ = Path(runs) if runs is not None else Path(common.RUNS)
        thr, _fam, eps0 = load_prereqs(runs_, getattr(a, "family_run", None) or M3_RUN)
        src_rows = {r["idx"]: r for r in common.read_jsonl(runs_ / a.source_run / "items.jsonl")}

        def cond_index(it, name):
            keys = list(src_rows[it["idx"]]["conds"])
            if name not in keys:
                raise KeyError(f"condition {name} not in the source row of item {it['idx']} ({keys})")
            return keys.index(name)
        return SimpleNamespace(run=run, runs=runs_, dcache=pipeline.dcache_for(), thr=thr, eps0=eps0, source_run=a.source_run, slot_len=int(a.slot_len),
                               conds=tuple(c for c in a.conds.split(",") if c), cond_index=cond_index)
    return make_ctx


def source_items(runs: Path, source_run: str) -> list[dict]:
    """The item list of the source run, in its order (idx, gid, image_id, caption, neg_caption from its committed rows)."""
    rows = common.read_jsonl(Path(runs) / source_run / "items.jsonl")
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: r["idx"]):
        if r["idx"] not in seen:
            seen.add(r["idx"])
            out.append(dict(idx=r["idx"], gid=r["gid"], image_id=r["image_id"], caption=r["caption"], neg_caption=r["neg_caption"]))
    return out


def check_prereqs(a, runs: Path | None = None) -> None:
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    load_prereqs(runs, getattr(a, "family_run", None) or M3_RUN)                       # threshold.json and family.json (endpoint d)
    if not (runs / a.source_run / "items.jsonl").exists():
        raise FileNotFoundError(f"{runs / a.source_run / 'items.jsonl'} missing: nothing to re-score")
    if a.slot_len < 1:
        raise ValueError("--slot-len must be a positive token count")
    bad = [c for c in a.conds.split(",") if c and c not in CONDS]
    if bad:
        raise ValueError(f"--conds {bad} not in {CONDS}")


def build_cfg(a, runs: Path, n_items: int) -> dict:
    """The run's config.json content: the stage constants, the options, and the SHA-256 of the codebook and of the D-cache file of the slot (A6.2 hash set; None if a file is missing)."""
    return dict(CONFIG, n_items=n_items, source_run=a.source_run, slot_len=a.slot_len, conds=[c for c in a.conds.split(",") if c], duty=getattr(a, "duty", None), mem_frac=getattr(a, "mem_frac", None),
                **input_hashes(Path(runs), a.slot_len))


def main(argv=None) -> int:
    ap = runner.base_parser(RUN_ID, None)
    ap.add_argument("--source-run", default=SOURCE_RUN, help="run whose items, codes, z, delta, tex and nbr are re-used (read only)")
    ap.add_argument("--slot-len", type=int, default=L_FIX, help="fixed caption-slot length in tokens (LRF-FROZEN report: 13, the M4 median)")
    ap.add_argument("--conds", default=",".join(CONDS), help="conditions to re-score (default: the four LRF training conditions)")
    ap.add_argument("--family-run", default=M3_RUN)
    a = ap.parse_args(argv)
    try:
        check_prereqs(a)
    except (FileNotFoundError, ValueError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    n_src = len(source_items(Path(common.RUNS), a.source_run))
    cfg = build_cfg(a, Path(common.RUNS), a.n or n_src)

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    def selfcheck(sc, items):
        return sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])

    def get_items(sc, run):
        items = source_items(Path(common.RUNS), a.source_run)
        return items[:a.n] if a.n else items

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=get_items, process=process, make_ctx=make_ctx_factory(a), soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit,
                            guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=selfcheck, watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
