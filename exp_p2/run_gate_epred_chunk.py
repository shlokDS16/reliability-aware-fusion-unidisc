"""E-pred FIT CHUNK (SAP AD.3 as demoted by AB.3 items 5 and 6; A3.6 item 3). GPU runner; its author has NOT executed it on a GPU.

    python -m exp_p2.run_gate_epred_chunk --resume --soft-minutes 12.5 --audit-record <gate-auditor record> [--limit N] [--run-id P2-GATE-EPRED-FIT]
    python -m exp_p2.gate.epred fit --run-id P2-GATE-M3 --fit-run P2-GATE-EPRED-FIT --audit-record <same record>     # CPU, afterwards: writes the write-once epred_frozen.json; COMMIT IT before M4

What it computes, and nothing else (AD.3, AB.3 item 6): the GATE-M flags (alpha 0.05, the frozen M2 threshold, mask seed 20261029 = config.SEED_GATE, one jitter draw) on the 100 HEADROOM items at the
`family.json` operating points (the P cells with an operating point) and at the token-level PS cells (patch, swap), plus the per-token image-direction Delta of the PS codes. It reads the headroom items' M3
arrays (clean codes, rung codes, rung Delta): NO image is loaded and NO encode is run. Per item: 2 caption passes (Lambda^{c+}, Lambda^{c-}, only if a PS cell is run) + 8 B-passes per cell (+ the cached null D);
at most 2 + 8 x 5 = 42 rows. The output is the contract of `epred.load_fit_inputs` (`runs/P2-GATE-EPRED-FIT/arrays/item{idx:04d}.npz`, one per M3 item, after the arrays a row in `items.jsonl`):
    {key}_flag   bool[L_I]    for each P cell with an operating point (key = the family.json key, e.g. jpeg10): flags on the M3 rung codes `{key}_codes`
    patch_codes / patch_delta / patch_flag, swap_codes / swap_delta / swap_flag   (int16 / float32 / bool): codes from corruptions.apply_token(name, clean, token_rng(SEED_GATE, gid, name), ...) exactly as
    M4 builds them, delta = Lambda^{c+}[codes] - Lambda^{c-}[codes]; a PS cell that is not run (--sanity) has no *_flag in any item and is "absent, counted" in the fit.
The jitter stream uses the condition index M4 would give the same condition (clean 0, each family corruption, its denoised copy if any, then the sanity names), so a flag is the flag M4's procedure draws.

Fences (AB.3 items 5 and 6; the runner refuses, exit code in brackets, before any model is touched):
  [2]  runs/P2-GATE-M2/threshold.json or a committed runs/P2-GATE-M3/family.json (endpoint d) is missing, the M3 run is incomplete (fewer rows than its effective n), an M3 array lacks a needed key,
       or --audit-record is missing / does not exist (the fit code is "committed and gate-auditor-checked before the fit chunk runs"; --allow-unaudited is for rehearsals and is recorded);
  [3]  an M4 item already exists, or epred_frozen.json already exists (the chunk must precede the first M4 item);
  [11] the fit-code files (epred.FIT_CODE_FILES) or family.json have uncommitted changes (--allow-dirty records them).
No decision depends on this run: not the n-rule, the order of runs, any cut, the S2 cells, the B or R go decisions, nor any wording (AB.3 item 6). Its output directory is read only by `epred.py`
(`fit`); no headroom, M4, S2, B, R or suite code reads it. If the chunk cannot run before M4 is ready, E-pred is "not run" and M4 does not wait (AB.3 item 5, AB.9)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                          # noqa: E402
from exp_p2.scoring import IMG_VOCAB                                                # noqa: E402
from exp_p2.gate import arms, calibrate as cal, checks, config, corruptions, epred, folds, foil, pins, pipeline, runner      # noqa: E402
from exp_p2.run_gate_m4 import SANITY_ALL, load_prereqs, parse_sanity               # noqa: E402

RUN_ID = epred.FIT_RUN_ID                                  # "P2-GATE-EPRED-FIT"
M3_RUN, M4_RUN = "P2-GATE-M3", "P2-GATE-M4"
EXIT_ORDER = 3
CONFIG = dict(stage="EPRED-FIT", fold="head", n_items=config.N_HEAD, seed=config.SEED_GATE, K=config.K, alpha=config.ALPHA_PRIMARY, sanity=list(SANITY_ALL), duty=0.5,
              spec="research/paper2/prereg/SAP-GATE-2026-10-28.md AD.3, AB.3 items 5 and 6, A3.6", no_decision_depends_on_this_run=True)


class Refusal(RuntimeError):
    """A fence of AB.3 item 5 or 6 was not met. `code` is the process exit code."""

    def __init__(self, msg: str, code: int = 2):
        super().__init__(msg)
        self.code = code


# ------------------------------------------------------------------------------------------------ conditions (the M4 condition order, without any encode)
def condition_indices(family: list[tuple[str, object]], denoise_for=config.DENOISE_FOR, sanity=SANITY_ALL) -> dict[str, int]:
    """Name -> M4 condition index (the `ci` that seeds M4's jitter draw): clean 0, then for each family corruption its key and, if the corruption is in `denoise_for`, the denoised copy, then the sanity
    names in their fixed order. Mirrors `run_gate_m4.build_conditions` (tested against it)."""
    out, ci = {"clean": 0}, 1
    for corr, sev in family:
        key = corruptions.corruption_key(corr, sev)
        out[key] = ci
        ci += 1
        if corr in denoise_for:
            out[key + "_dn"] = ci
            ci += 1
    for name in sanity:
        out[name] = ci
        ci += 1
    return out


def plan(family_json: dict, sanity) -> tuple[list[str], list[str]]:
    """(P keys with an operating point in family.json order, PS names run)."""
    return [f["key"] for f in family_json["family"]], list(sanity)


# ------------------------------------------------------------------------------------------------ prerequisites (all CPU, before the model)
def check_prereqs(runs: Path | None = None, *, audit_record: str | None = None, allow_unaudited: bool = False, allow_dirty: bool = False,
                  check_git: bool = True, fit_run: str = RUN_ID) -> dict:
    """Raises Refusal (with the exit code) or FileNotFoundError / ValueError from `run_gate_m4.load_prereqs`. Returns what the runner needs."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    thr, family, eps0 = load_prereqs(runs)                                           # M2 threshold, family.json with endpoint d
    fam_path = runs / M3_RUN / "family.json"
    fam_json = json.loads(fam_path.read_text(encoding="utf8"))
    if check_git:
        try:
            foil.require_committed(fam_path)                                         # AD.3: the operating points are committed before any flag exists on a headroom item
        except (RuntimeError, ValueError) as e:
            raise Refusal(f"family.json must be committed and unmodified before the fit chunk runs (AD.3, AD.12): {e}")
    m4_items = runs / M4_RUN / "items.jsonl"
    if m4_items.exists() and m4_items.stat().st_size > 0:
        raise Refusal(f"{m4_items} already has M4 items: the fit chunk must precede the first M4 item (AB.3 item 5). E-pred is 'not run'.", EXIT_ORDER)
    if (runs / fit_run / epred.FROZEN_NAME).exists():
        raise Refusal(f"{runs / fit_run / epred.FROZEN_NAME} exists: the fit is frozen (write-once); nothing more is computed", EXIT_ORDER)
    dirty = []
    if check_git:
        dirty = epred.git_status_lines(list(epred.FIT_CODE_FILES))
        if dirty and not allow_dirty:
            raise Refusal("the fit code must be committed before the fit chunk runs (AB.3 item 5):" + "".join("\n  " + l for l in dirty), pins.EXIT_DIRTY)
    audit = None
    if audit_record:
        ap = Path(audit_record)
        if not ap.exists():
            raise Refusal(f"--audit-record {ap} does not exist")
        audit = dict(path=str(ap), **epred.sha256_file(ap))
    elif not allow_unaudited:
        raise Refusal("--audit-record is required: the fit code (epred_fit.py, theory.py, test_gate_epred_fit.py) is gate-auditor-checked before the fit chunk runs (AB.3 item 5); --allow-unaudited is for rehearsals and is recorded")
    m3 = runs / M3_RUN
    rows = {}
    for r in common.read_jsonl(m3 / "items.jsonl") if (m3 / "items.jsonl").exists() else []:
        rows.setdefault(r["idx"], r)
    eff = m3 / "effective_n.json"
    want = min(config.N_HEAD, json.loads(eff.read_text(encoding="utf8"))["effective"]) if eff.exists() else config.N_HEAD
    if len(rows) < want:
        raise Refusal(f"the M3 run has {len(rows)} of {want} headroom items; the fit chunk follows a COMPLETE M3 (AD.12)")
    return dict(thr=thr, family=family, eps0=eps0, family_json=fam_json, m3_rows=rows, dirty=dirty, audit=audit, n_m3=len(rows))


# ------------------------------------------------------------------------------------------------ items
def load_folds_frozen() -> dict:
    p = folds.folds_path()
    if not p.exists():
        raise FileNotFoundError(f"{p} missing (the frozen folds; the fit chunk does not build folds)")
    return json.loads(p.read_text(encoding="utf8"))


def get_items(runs: Path, pre: dict, f: dict | None = None) -> list[dict]:
    """The headroom items that have an M3 row, in idx order, with their captions from folds.json 'head'. The M3 row and the fold entry must agree on gid and image id (no re-selection, no replacement)."""
    f = f if f is not None else load_folds_frozen()
    head = {it["idx"]: it for it in f["head"]}
    out = []
    for idx in sorted(pre["m3_rows"]):
        r = pre["m3_rows"][idx]
        it = head.get(idx)
        if it is None or it["gid"] != r["gid"] or it["image_id"] != r["image_id"]:
            raise Refusal(f"M3 row idx {idx} (gid {r['gid']}, image {r['image_id']}) does not match folds.json 'head' ({None if it is None else (it['gid'], it['image_id'])})")
        out.append(it)
    keys, _ = plan(pre["family_json"], ())
    need = ["clean"] + [f"{k}_codes" for k in keys]
    for it in out:                                                                   # every needed M3 array is checked now, not at the item
        p = Path(runs) / M3_RUN / "arrays" / f"item{it['idx']:04d}.npz"
        if not p.exists():
            raise Refusal(f"{p} missing: M3 arrays are needed for the clean and rung codes")
        with np.load(p) as z:
            miss = [k for k in need if k not in z.files]
        if miss:
            raise Refusal(f"{p} lacks {miss}")
    return out


# ------------------------------------------------------------------------------------------------ per item
def make_ctx_factory(pre: dict, runs: Path | None = None, sanity=SANITY_ALL):
    def make_ctx(sc, run):
        runs_ = Path(runs) if runs is not None else Path(common.RUNS)
        checks.l10_once(sc, run)
        grid = int(round(sc.L_I ** 0.5))
        keys, ps = plan(pre["family_json"], sanity)
        return SimpleNamespace(run=run, runs=runs_, dcache=pipeline.dcache_for(), tau=pre["thr"][config.ALPHA_PRIMARY].tau, eps0=pre["eps0"], family=pre["family"], keys=keys, ps=ps,
                               ci=condition_indices(pre["family"], config.DENOISE_FOR, tuple(sanity)), grid=grid, patch=max(2, grid // 4))
    return make_ctx


def process(sc, it, ctx):
    gid, K = it["gid"], config.K
    rows0 = getattr(sc, "rows", None)
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
    with np.load(Path(ctx.runs) / M3_RUN / "arrays" / f"item{it['idx']:04d}.npz") as z:
        clean = np.asarray(z["clean"], np.int64)                                   # the clean codes M3 stored (int16 on disk; the encoder returns int64)
        rung = {k: np.asarray(z[f"{k}_codes"], np.int64) for k in ctx.keys}
    groups = pipeline.item_groups(sc, gid, K)
    arrays, cells = {}, {}
    conds = [(k, rung[k], False) for k in ctx.keys]
    if ctx.ps:
        lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap_tok, neg_tok, clean)           # 2 passes, only for the PS cells' Delta
        for name in ctx.ps:
            tc = corruptions.apply_token(name, clean, corruptions.token_rng(config.SEED_GATE, gid, name), grid=ctx.grid, patch=ctx.patch, swap_frac=config.SWAP_FRAC, vocab=IMG_VOCAB)
            arrays[f"{name}_codes"], arrays[f"{name}_delta"] = tc.astype(np.int16), pipeline.image_delta(lam_pos, lam_neg, tc)
            conds.append((name, tc, True))
    for name, codes, _is_ps in conds:
        gs = pipeline.gate_scores(sc, cap_tok, codes, groups, ctx.dcache, K)                  # 8 passes (+ cached null)
        uj = cal.jitter(gs["u"], ctx.eps0, arms.arm_rng(config.SEED_GATE, gid, ctx.ci[name], arms.ARM_TAG["jitter"], 0))
        flag = uj > ctx.tau
        arrays[f"{name}_flag"] = flag
        cells[name] = dict(n_flag=int(flag.sum()), n_changed=int((codes != clean).sum()))
    row = dict(gid=gid, image_id=it["image_id"], n_tok=len(cap_tok), cells=cells)
    if isinstance(rows0, int):
        row["n_rows"] = int(sc.rows) - rows0
    return row, arrays


def main(argv=None, *, runs: Path | None = None):
    ap = runner.base_parser(RUN_ID, CONFIG["n_items"])
    ap.add_argument("--audit-record", default=None, help="the gate-auditor's record for the fit code (required; its SHA-256 goes into the run config)")
    ap.add_argument("--allow-unaudited", action="store_true", help="rehearsals only; recorded in the run config")
    ap.add_argument("--sanity", default=",".join(SANITY_ALL), help="token-level PS cells to flag (default both); a cell not run is 'absent, counted' in the fit")
    a = ap.parse_args(argv)
    try:                                                                             # every prerequisite is checked BEFORE the model is touched
        sanity = parse_sanity(a.sanity)
        pre = check_prereqs(runs, audit_record=a.audit_record, allow_unaudited=a.allow_unaudited, allow_dirty=a.allow_dirty)
        items = get_items(Path(runs) if runs is not None else Path(common.RUNS), pre)
    except Refusal as e:
        print("STOP:", e, file=sys.stderr)
        return e.code
    except (FileNotFoundError, ValueError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    cfg = dict(CONFIG, n_items=a.n, duty=a.duty, mem_frac=a.mem_frac, sanity=list(sanity), family=[f["key"] for f in pre["family_json"]["family"]], audit_record=pre["audit"],
               unaudited=bool(a.allow_unaudited and not pre["audit"]), dirty_fit_code=pre["dirty"], fit_code=epred.fit_code_hashes())

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    def selfcheck(sc, its):
        return sc.selfcheck(common.load_image(its[0]["image_id"]), its[0]["caption"])

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=lambda sc, run: items, process=process, make_ctx=make_ctx_factory(pre, runs, sanity),
                            soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit, guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=selfcheck,
                            watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
