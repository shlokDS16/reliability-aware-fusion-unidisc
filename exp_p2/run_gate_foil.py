"""Family B (SAP A2 AD.6, AB.6): FOIL-COCO hard negatives on clean images, two stages. GPU runner; the author of this file has NOT executed it (no GPU use by the implementer).

    python -m exp_p2.run_gate_foil --stage fit  --resume --soft-minutes 12.5 [--limit N]     # run id P2-GATE-FOIL-FIT: the fit pairs (FOIL pairs on folds.json "cal" images, at most 300)
    python -m exp_p2.gate.analysis_foil freeze                                             # CPU: fusion weights, best direction, rules (i) and (ii) -> runs/P2-GATE-FOIL/fusion_frozen.json; COMMIT IT
    python -m exp_p2.run_gate_foil --stage test --resume --soft-minutes 12.5 [--limit N]     # run id P2-GATE-FOIL-TEST: the test pairs; refuses unless fusion_frozen.json is committed with status ok
    python -m exp_p2.gate.analysis_foil analyze                                            # CPU: B1 (exact McNemar of Y_fus against Y_best)

Before the model is touched (CPU): the FOIL file SHA-256, the committed pool, and the leak check L0 to L8 (stops with exit code 2 on any failure; log in runs/P2-GATE-FOIL/leak_check.json).
Per pair (4 passes + 1 encode, plus the cached text null): clean encode; image direction caption-only for c+ and c- (2 passes, the 'none' arm of Alg. 5'); text direction full caption mask with the image
visible for c+ and c- (2 passes). Nothing is gated and no corruption is applied: B is a clean-image hard-negative test. The caption token rule (5 to 32, runtime tokenizer) EXCLUDES a pair, it is never replaced.
Margins stored per pair: T = pmi(c+) - pmi(c-), I = mean over the 1,024 image tokens of the paired evidence Delta_j = Lambda^{c+}_j[v_j] - Lambda^{c-}_j[v_j]. Captions are lower-cased on both sides (case leak).
Memory: the decoded PIL image is freed after the encode and the two [1024, 16384] log-probability matrices after the gather; nothing larger than one pair is alive at a time."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import checks, config, foil, pipeline, runner              # noqa: E402
from exp_p2.gate.evidence import evidence_from_delta                        # noqa: E402

STAGES = {"fit": foil.FIT_RUN_ID, "test": foil.TEST_RUN_ID}
CONFIG = dict(stage="B", family="B", spec="research/paper2/prereg/SAP-GATE-2026-10-28.md AD.6 + AB.6", seed=config.SEED_GATE, duty=0.5, caption_normalisation="lower case, white space collapsed",
              scoring="fp32 log-softmax of bf16 logits restricted to the modality vocabulary; batch 4; backbone eval bf16")


def frozen_path() -> Path:
    return foil.pool_dir() / "fusion_frozen.json"


def check_prereqs(stage: str) -> dict:
    """CPU checks before any model load. Raises FileNotFoundError / RuntimeError / foil.LeakCheckFailed (the caller turns them into exit code 2)."""
    foil.verify_file()
    pool_path = foil.pool_dir() / "pool.json"
    foil.require_committed(pool_path)                                       # AD.6: 'the pool list is committed before any GPU use'
    pool = foil.load_pool(pool_path)
    log = foil.check_pool(pool)                                              # L0 to L8; raises on failure
    (foil.pool_dir() / "leak_check.json").write_text(json.dumps(log, indent=1, default=str), encoding="utf8")
    info = dict(pool_sha256=log["pool_sha256"], foil_sha256=foil.FOIL_SHA256, leak_check="passed")
    if stage == "test":
        fp = frozen_path()
        foil.require_committed(fp)                                          # rule (iii)
        fz = json.loads(fp.read_text(encoding="utf8"))
        if fz.get("fit", {}).get("status") != "ok":
            raise RuntimeError(f"fusion_frozen.json status is {fz.get('fit', {}).get('status')!r}: the test pairs are not run (AD.6 rules (i), (ii)); B is reported as {fz.get('fit', {}).get('status')}")
        info["fusion_frozen"] = fz.get("sha256_of_fit_run_rows")
    return info


def stage_items(pool: dict, stage: str) -> list[dict]:
    """Runner items in the committed pool order; exclusions are applied at run time with the real tokenizer (get_items)."""
    return [dict(idx=int(p["idx"]), gid=int(p["gid"]), image_id=int(p["image_id"]), caption=p["c_pos"], neg_caption=p["c_neg"], pair_id=int(p["pair_id"]), pool_excluded=p.get("excluded"))
            for p in pool["fit" if stage == "fit" else "test"]]


def get_items_factory(stage: str, n: int | None):
    def get_items(sc, run):
        items = stage_items(foil.load_pool(), stage)
        if n:
            items = items[:n]
        lo, hi = config.TOK_RANGE
        keep, why, differs = [], {}, []
        for it in items:
            a, b = len(sc.caption_ids(it["caption"])), len(sc.caption_ids(it["neg_caption"]))
            it["n_tok_pos"], it["n_tok_neg"] = a, b
            r = ("pos_and_neg_out_of_range" if not (lo <= a <= hi) and not (lo <= b <= hi) else "pos_out_of_range" if not (lo <= a <= hi) else "neg_out_of_range" if not (lo <= b <= hi) else None)
            if r != it["pool_excluded"]:
                differs.append(dict(idx=it["idx"], pool=it["pool_excluded"], runtime=r))
            if r:
                why[r] = why.get(r, 0) + 1
            else:
                keep.append(it)
        Path(run).mkdir(parents=True, exist_ok=True)
        (Path(run) / "token_exclusions.json").write_text(json.dumps(dict(stage=stage, n_planned=len(items), n_excluded=len(items) - len(keep), by_reason=why, runtime_differs_from_pool_time=differs,
                                                                          rule="A2.1 item 2: excluded, counted, not replaced")), encoding="utf8")
        return keep
    return get_items


def make_ctx(sc, run):
    checks.l10_once(sc, run)
    return SimpleNamespace(run=run, dcache=pipeline.dcache_for())


def process(sc, it, ctx):
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
    pil, codes = pipeline.prep_image(sc, it["image_id"])
    del pil                                                                                 # the decoded image is not needed after the encode
    lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap_tok, neg_tok, codes)                # 2 passes
    delta = pipeline.image_delta(lam_pos, lam_neg, codes)
    del lam_pos, lam_neg                                                                    # free the two [1024, 16384] matrices before the text passes
    txt = pipeline.text_direction(sc, cap_tok, neg_tok, codes, [None], ctx.dcache)[0]       # 2 passes (+ the cached null of each caption length)
    ev = evidence_from_delta(delta)
    row = dict(gid=it["gid"], pair_id=it["pair_id"], image_id=it["image_id"], caption=it["caption"], neg_caption=it["neg_caption"], n_tok=len(cap_tok), n_tok_neg=len(neg_tok),
               T=float(txt["d"]), I=float(ev["mean"]), img=pipeline.compact(ev), txt=txt)
    return row, dict(delta=delta, codes=codes.astype(np.int16))


def main(argv=None) -> int:
    import argparse
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--stage", choices=sorted(STAGES), required=True)
    known, _ = pre.parse_known_args(argv)
    ap = runner.base_parser(STAGES[known.stage], None)
    ap.add_argument("--stage", choices=sorted(STAGES), required=True)
    a = ap.parse_args(argv)
    try:                                                                                    # every prerequisite is checked BEFORE the model is touched
        info = check_prereqs(a.stage)
    except (FileNotFoundError, RuntimeError, foil.LeakCheckFailed) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    planned = len(foil.load_pool()["fit" if a.stage == "fit" else "test"])
    n = a.n or planned
    cfg = dict(CONFIG, stage=f"B-{a.stage}", run_stage=a.stage, n_items=n, duty=a.duty, mem_frac=a.mem_frac, **info)

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    def selfcheck(sc, items):
        return sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=get_items_factory(a.stage, n), process=process, make_ctx=make_ctx, soft_minutes=a.soft_minutes, duty=a.duty,
                            limit=a.limit, guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=selfcheck, watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
