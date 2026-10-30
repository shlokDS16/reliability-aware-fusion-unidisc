"""imagecorruptions exploratory suite (SAP A2 AD.9, AB.8): GPU runner. NOT executed by its author (no GPU use by the implementer). First cut in the SAP cut order (AD.8).

    python -m exp_p2.run_gate_suite --resume --soft-minutes 12.5 [--limit N] [--run-id P2-GATE-SUITE]
    python -m exp_p2.gate.suite analyze                    # CPU, after the run: cell table, E-dec, b / c_cnt / net difference with a 95 percent bootstrap CI (no p-value)

Items (planned 200, position = idx): the 100 headroom items (folds.json "head", fit fold for E-pred) then the first 100 items of the test list (folds.json "test"). Out-of-range captions are excluded, counted,
not replaced (A2.1 item 2). Cells: pixelate, defocus_blur, fog, impulse_noise at severities 2 and 4 of the package's 1-to-5 scale (`exp_p2/gate/suite.py`), applied to the 512 x 512 image the model sees, then
tokenised; the corruption seed is derived from the item id. Per item (66 passes, 9 encodes, plus the cached null): clean encode; Lambda^{c+}, Lambda^{c-} once = 2 passes (they do not depend on the image
codes, as in M4); for each of the 8 cells: encode, B = 8 passes (caption masked), cached null D, u = -(B - D), one jitter draw, GATE-M flags at alpha 0.05 with the frozen M2 threshold, arms none / GATE-M / changed-code
(oracle), image-direction evidence (gathers). No text direction, no other arm, no operating-point choice, no cell dropped for its result.
Prerequisites (checked before the model is touched): runs/P2-GATE-M2/threshold.json and a committed runs/P2-GATE-M3/family.json (the operating points are fixed before any gate flag exists on a headroom item;
the headroom analysis never reads this run). The imagecorruptions package must be importable; a type absent under its name is dropped, never replaced (recorded in runs/<run>/suite_types.json).
Memory: only the two caption matrices (2 x 67 MB) stay alive across cells; each corrupted PIL image is freed after its encode."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import arms, calibrate as cal, checks, config, folds, foil, pipeline, runner, suite    # noqa: E402
from exp_p2.gate.evidence import evidence_from_delta                        # noqa: E402

RUN_ID = suite.SUITE_RUN_ID
M2_RUN, M3_RUN = "P2-GATE-M2", "P2-GATE-M3"
N_ITEMS = suite.HEAD_N + suite.TEST_N
CONFIG = dict(stage="SUITE", family="suite (exploratory, Tier 3)", n_items=N_ITEMS, seed=config.SEED_GATE, K=config.K, alpha=config.ALPHA_PRIMARY, cells=list(suite.CELL_KEYS), package=suite.PACKAGE, duty=0.5,
              spec="research/paper2/prereg/SAP-GATE-2026-10-28.md AD.9 + AB.8")


def load_threshold(runs: Path | None = None) -> tuple["cal.Threshold", float]:
    """Frozen M2 threshold at the primary alpha and its eps0. Raises FileNotFoundError with the command to run if missing."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    tp = runs / M2_RUN / "threshold.json"
    if not tp.exists():
        raise FileNotFoundError(f"{tp} missing; create it with: python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2")
    t = pipeline.load_json(tp)
    thr = {float(k): cal.Threshold.from_json(v) for k, v in t["thresholds"].items()}
    if config.ALPHA_PRIMARY not in thr:
        raise ValueError(f"{tp} has no threshold for alpha {config.ALPHA_PRIMARY}")
    return thr[config.ALPHA_PRIMARY], thr[config.ALPHA_PRIMARY].eps0


def check_prereqs(runs: Path | None = None, *, require_commit: bool = True) -> tuple["cal.Threshold", float, list[str]]:
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    thr, eps0 = load_threshold(runs)
    fp = runs / M3_RUN / "family.json"
    if not fp.exists():
        raise FileNotFoundError(f"{fp} missing: the operating points must be fixed (committed) before gate flags are computed on headroom items (SAP 5, AD.3)")
    if require_commit:
        foil.require_committed(fp)
    types = suite.available_types()
    return thr, eps0, types


def planned_items(f: dict) -> list[dict]:
    """The planned list: head[:100] then the first 100 of the test list; idx = position; fold_idx = the item's index inside folds.json."""
    out, k = [], 0
    for fold, lst in (("head", f["head"][:suite.HEAD_N]), ("test", folds.test_items(f)[:suite.TEST_N])):
        for it in lst:
            out.append(dict(it, fold=fold, fold_idx=it["idx"], idx=k))
            k += 1
    return out


def get_items_factory(n: int | None):
    def get_items(sc, run):
        f = folds.ensure_folds(lambda c: len(sc.caption_ids(c)))
        rep = pipeline.check_fold_tokens(sc, f, run)                                       # excluded, counted, not replaced
        bad = {fold: set(rep["excluded"].get(fold, [])) for fold in ("head", "test", "test_ext")}
        items = planned_items(f)
        items = items[:n] if n else items
        return [it for it in items if it["fold_idx"] not in bad[it["fold"]]]
    return get_items


def make_ctx_factory(runs: Path | None = None):
    def make_ctx(sc, run):
        thr, eps0, types = check_prereqs(runs)
        ic = suite.load_package()
        cells = [(ci, t, s) for ci, (t, s) in enumerate(suite.CELLS) if t in types]
        Path(run).mkdir(parents=True, exist_ok=True)
        (Path(run) / "suite_types.json").write_text(json.dumps(dict(package=suite.PACKAGE, installed_commit=suite.verify_pinned_commit(), versions=suite._versions(), types_requested=list(suite.TYPES), types_available=types,
                                                                    types_dropped=[t for t in suite.TYPES if t not in types], cells_run=[suite.cell_key(t, s) for _, t, s in cells],
                                                                    rule="a type absent under its name is dropped, not replaced (AD.9)")), encoding="utf8")
        checks.l10_once(sc, run)
        return SimpleNamespace(run=run, dcache=pipeline.dcache_for(), thr=thr, eps0=eps0, ic=ic, cells=cells, grid=int(round(sc.L_I ** 0.5)))
    return make_ctx


def process(sc, it, ctx):
    gid, K = it["gid"], config.K
    rows0 = getattr(sc, "rows", None)
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
    pil, clean = pipeline.prep_image(sc, it["image_id"])
    lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap_tok, neg_tok, clean)                          # 2 passes, shared by all cells
    groups = pipeline.item_groups(sc, gid, K)
    row = dict(gid=gid, fold=it["fold"], fold_idx=it["fold_idx"], image_id=it["image_id"], caption=it["caption"], neg_caption=it["neg_caption"], n_tok=len(cap_tok), n_tok_neg=len(neg_tok), cells={})
    delta_clean = pipeline.image_delta(lam_pos, lam_neg, clean)
    row["clean"] = pipeline.compact(evidence_from_delta(delta_clean))
    arrays = dict(clean_codes=clean.astype(np.int16), clean_delta=delta_clean)
    for ci, t, s in ctx.cells:
        key = suite.cell_key(t, s)
        img = suite.apply_corruption(t, s, pil, suite.corruption_seed(gid, ci), ctx.ic)
        codes = sc.encode(img)
        del img                                                                                         # the corrupted decoded image is not needed after the encode
        z = arms.changed_code_gate(clean, codes)
        delta = pipeline.image_delta(lam_pos, lam_neg, codes)
        gs = pipeline.gate_scores(sc, cap_tok, codes, groups, ctx.dcache, K)                            # 8 passes (+ cached null)
        uj = cal.jitter(gs["u"], ctx.eps0, arms.arm_rng(config.SEED_GATE, gid, 10 + ci, arms.ARM_TAG["jitter"], 0))
        G = uj > ctx.thr.tau
        arm_G = {"none": arms.no_gate(sc.L_I), "gm": G, "chg": z}
        row["cells"][key] = dict(n_changed=int(z.sum()), n_flag=int(G.sum()), n_tp=int((G & z).sum()), n_fp_on_clean_tokens=int((G & ~z).sum()),
                                 img={an: pipeline.compact(evidence_from_delta(delta, ~g)) for an, g in arm_G.items()})
        arrays.update({f"{key}_codes": codes.astype(np.int16), f"{key}_z": z, f"{key}_delta": delta, f"{key}_flag": G, f"{key}_u": gs["u"].astype(np.float32)})
    if isinstance(rows0, int):
        row["n_rows"] = int(sc.rows) - rows0
    return row, arrays


def main(argv=None) -> int:
    ap = runner.base_parser(RUN_ID, N_ITEMS)
    a = ap.parse_args(argv)
    try:                                                                                                # every prerequisite is checked BEFORE the model is touched
        check_prereqs()
    except (FileNotFoundError, ValueError, RuntimeError, ImportError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    cfg = dict(CONFIG, n_items=a.n or N_ITEMS, duty=a.duty, mem_frac=a.mem_frac, installed_commit=suite.installed_commit())      # read from the installed metadata at run time (audit m4)

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    def selfcheck(sc, items):
        return sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=get_items_factory(a.n), process=process, make_ctx=make_ctx_factory(), soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit,
                            guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=selfcheck, watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
