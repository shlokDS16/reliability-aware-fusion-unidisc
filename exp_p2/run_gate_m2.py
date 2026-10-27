"""M2 (v2 section 11.1): calibration fold. 300 clean COCO pairs (disjoint from every probe item).

    python -m exp_p2.run_gate_m2 --resume --soft-minutes 12.5 [--limit N] [--run-id P2-GATE-M2]

Per item (12 passes + 1 encode, plus the cached nulls): clean encode; B (K=8 masks, caption masked) = 8; image direction caption-only for c+ and c- = 2
(Lambda matrices, 'none' arm of Alg. 5'); text direction full-mask for c+ and c- = 2 (image visible). c- is the item's deranged negative caption.
Stores B, D (at the observed codes), s3 and the clean codes per item; the threshold is fitted afterwards on the CPU:

    python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2

Nothing here runs while a HOLD file exists (exit code 7)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import config, folds, pipeline, runner, scores, checks     # noqa: E402
from exp_p2.gate.evidence import evidence_from_delta                        # noqa: E402

RUN_ID = "P2-GATE-M2"
CONFIG = dict(stage="M2", fold="cal", n_items=config.N_CAL, seed=config.SEED_GATE, K=config.K, statistic=config.STAT_NAME, duty=0.5,
              scoring="fp32 log-softmax of bf16 logits restricted to the modality vocabulary; batch 4; backbone eval bf16",
              spec="research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md section 11.1 M2")


def get_items(sc, run, n=None):
    f = folds.ensure_folds(lambda c: len(sc.caption_ids(c)))
    return f["cal"][:n] if n else f["cal"]


def make_ctx(sc, run):
    dc = pipeline.dcache_for()
    checks.l10_once(sc, run)
    return SimpleNamespace(run=run, dcache=dc)


def process(sc, it, ctx):
    gid = it["gid"]
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
    pil, codes = pipeline.prep_image(sc, it["image_id"])
    gs = pipeline.gate_scores(sc, cap_tok, codes, pipeline.item_groups(sc, gid), ctx.dcache)                    # 8 passes + cached null
    lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap_tok, neg_tok, codes)                                     # 2 passes
    delta = pipeline.image_delta(lam_pos, lam_neg, codes)
    txt = pipeline.text_direction(sc, cap_tok, neg_tok, codes, [None], ctx.dcache)[0]                            # 2 passes
    row = dict(gid=gid, image_id=it["image_id"], caption=it["caption"], neg_caption=it["neg_caption"], n_tok=len(cap_tok), n_tok_neg=len(neg_tok),
               img=pipeline.compact(evidence_from_delta(delta)), txt=txt)
    arrays = dict(codes=codes.astype(np.int16), B=gs["B"], D=gs["D"].astype(np.float32), s3=gs["s3"], delta=delta)
    return row, arrays


def main(argv=None):
    ap = runner.base_parser(RUN_ID, CONFIG["n_items"])
    a = ap.parse_args(argv)
    cfg = dict(CONFIG, n_items=a.n, duty=a.duty, mem_frac=a.mem_frac)

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    def selfcheck(sc, items):
        return sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=lambda sc, run: get_items(sc, run, a.n), process=process, make_ctx=make_ctx,
                            soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit, guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=selfcheck, watchdog_factory=runner.default_watchdog)


if __name__ == "__main__":
    sys.exit(main())
