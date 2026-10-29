"""M3 (v2 section 11.1, 7.3, Alg. 9): headroom check on 100 held-out items. NO gate flags are computed here (the decision is blind to the method).

    python -m exp_p2.run_gate_m3 --resume --soft-minutes 12.5 [--limit N] [--run-id P2-GATE-M3]
    python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d   # CPU: writes runs/P2-GATE-M3/family.json  (commit it before any M4 item is scored)

Per item (2 passes + 7 encodes): clean encode; every ladder rung encoded (jpeg q10, q5; noise 0.10, 0.20; splice 128, 192); Lambda^{c+}, Lambda^{c-}
(caption-only, image fully masked); image-direction evidence for the 'none' arm on clean and on each rung, and for the changed-code gate on each rung."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                          # noqa: E402
from exp_p2.gate import arms, config, corruptions, evidence, folds, pipeline, runner       # noqa: E402

RUN_ID = "P2-GATE-M3"
CONFIG = dict(stage="M3", fold="head", n_items=config.N_HEAD, seed=config.SEED_GATE, ladders={k: list(v) for k, v in config.LADDERS.items()}, duty=0.5,
              spec="research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md sections 7.3, 11.1 M3, Alg. 9")


def load_folds(n_tok_fn, folds_path=None) -> dict:
    """Default: runs/P2-GATE-FOLDS/folds.json as before. An explicit path (family H only) must exist; it is never built here."""
    if not folds_path:
        return folds.ensure_folds(n_tok_fn)
    if not Path(folds_path).exists():
        raise FileNotFoundError(f"--folds-path {folds_path} does not exist (an explicit folds file is committed before the run; it is not built here)")
    return folds.ensure_folds(n_tok_fn, Path(folds_path))


def get_items(sc, run, n=None, folds_path=None):
    f = load_folds(lambda c: len(sc.caption_ids(c)), folds_path)
    rep = pipeline.check_fold_tokens(sc, f, run)                                 # SAP A2.1: out-of-range captions are excluded, counted, not replaced
    return pipeline.drop_excluded(f["head"][:n] if n else f["head"], rep, "head")


def make_ctx(sc, run, folds_path=None):
    f = load_folds(lambda c: len(sc.caption_ids(c)), folds_path)
    return SimpleNamespace(run=run, fold=f["head"])


def rung_rng(gid: int, corr: str, rung: int) -> np.random.Generator:
    return np.random.default_rng([config.SEED_GATE, gid, 100 + 10 * list(config.LADDERS).index(corr) + rung])


def donor_for(ctx, sc, it) -> object:
    """Splice donor: a uniformly random OTHER item of the same block (seeded by the item), preprocessed to 512 px. Blocks are the base 300 and the extension 301-500, so
    the donors of the base test items do not depend on whether the extension is used."""
    lo = 300 * (it["idx"] // 300)
    pool = [j for j in range(lo, min(len(ctx.fold), lo + 300)) if j != it["idx"]]
    j = pool[int(np.random.default_rng([config.SEED_GATE, it["gid"], 150]).integers(0, len(pool)))]
    return sc.preprocess(common.load_image(ctx.fold[j]["image_id"]))


def process(sc, it, ctx):
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
    pil, clean = pipeline.prep_image(sc, it["image_id"])
    lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap_tok, neg_tok, clean)                         # 2 passes
    d_clean = pipeline.image_delta(lam_pos, lam_neg, clean)
    row = dict(gid=it["gid"], image_id=it["image_id"], clean=pipeline.compact(evidence.evidence_from_delta(d_clean)), rungs={})
    arrays = dict(clean=clean.astype(np.int16), delta_clean=d_clean)
    donor = None
    for corr, ladder in config.LADDERS.items():
        if corr == "splice" and donor is None:
            donor = donor_for(ctx, sc, it)
        for r, sev in enumerate(ladder):
            img = corruptions.apply_pixel(corr, sev, pil, rung_rng(it["gid"], corr, r), donor if corr == "splice" else None)
            codes = sc.encode(img)
            chg = arms.changed_code_gate(clean, codes)
            d = pipeline.image_delta(lam_pos, lam_neg, codes)
            key = corruptions.corruption_key(corr, sev)
            row["rungs"][key] = dict(corruption=corr, severity=sev, n_changed=int(chg.sum()), none=pipeline.compact(evidence.evidence_from_delta(d)),
                                     chg=pipeline.compact(evidence.arm_summary(d, chg)))
            arrays[f"{key}_codes"], arrays[f"{key}_delta"] = codes.astype(np.int16), d
    return row, arrays


def main(argv=None):
    ap = runner.base_parser(RUN_ID, CONFIG["n_items"])
    ap.add_argument("--folds-path", default=None, help="family H only: folds file whose 'head' list is the headroom fold (default: runs/P2-GATE-FOLDS/folds.json); must exist, is never built")
    a = ap.parse_args(argv)
    try:
        pipeline.require_frozen()                                          # the frozen rival must exist before M3 (SAP A1.2 rule 5); checked before the model is touched
        if a.folds_path and not Path(a.folds_path).exists():
            raise FileNotFoundError(f"--folds-path {a.folds_path} does not exist")
    except FileNotFoundError as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    cfg = dict(CONFIG, n_items=a.n, duty=a.duty, mem_frac=a.mem_frac)
    if a.folds_path:                                                       # recorded only for family H, so the config of every existing run id is unchanged
        import hashlib
        cfg.update(folds_path=a.folds_path, folds_sha256=hashlib.sha256(Path(a.folds_path).read_bytes()).hexdigest())

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    def selfcheck(sc, items):
        return sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=lambda sc, run: get_items(sc, run, a.n, a.folds_path), process=process, make_ctx=(lambda sc, run: make_ctx(sc, run, a.folds_path)),
                            soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit, guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=selfcheck, watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
