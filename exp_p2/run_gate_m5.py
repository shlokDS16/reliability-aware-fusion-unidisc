"""M5 (v2 Alg. 12, 11.1): coherence test of the network on clean image tokens, 100 calibration items (the first 100 of the calibration fold).

    python -m exp_p2.run_gate_m5 --resume --soft-minutes 12.5 [--limit N] [--run-id P2-GATE-M5]
    python -m exp_p2.gate.coherence_report --run-id P2-GATE-M5 [--mu <clean mean per-token paired evidence from M4>]    # CPU

Per item: 4 token pairs (one horizontally and one vertically adjacent, two at least grid/4 tokens apart), each in two contexts (all other image tokens
visible; a random half of them masked), caption masked: 3 passes per (pair, context) = 24 passes. For items with idx % 4 == 0 (25 of 100) the same 24 passes
are repeated in a different batch composition (reversed order, batch 3); the difference of the two gap arrays is the noise floor g0."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import checks, config, folds, pipeline, runner            # noqa: E402

RUN_ID = "P2-GATE-M5"
N_ITEMS = 100
CONFIG = dict(stage="M5", fold="cal[:100]", n_items=N_ITEMS, seed=config.SEED_GATE, noise_floor_rule="idx % 4 == 0", duty=0.5,
              spec="research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md Alg. 12, section 11.1 M5")


def get_items(sc, run, n=None):
    f = folds.ensure_folds(lambda c: len(sc.caption_ids(c)))
    pipeline.check_fold_tokens(sc, f, run)                                       # audit M9: stop if the runtime tokenizer disagrees with the frozen counts
    return f["cal"][:(n or N_ITEMS)]


def make_ctx(sc, run):
    grid = int(round(sc.L_I ** 0.5))
    return SimpleNamespace(run=run, grid=grid, min_sep=max(2, grid // 4))


def process(sc, it, ctx):
    cap_tok = sc.caption_ids(it["caption"])
    pil, codes = pipeline.prep_image(sc, it["image_id"])
    st = sc.build(cap_tok, codes)
    rng = np.random.default_rng([config.SEED_GATE, it["gid"], 300])
    pairs = checks.coherence_pairs(ctx.grid, rng, min_sep=ctx.min_sep)
    halves = checks.half_masks(sc.L_I, pairs, rng)
    g = checks.coherence_gaps(sc, st, pairs, halves)                                          # 24 passes
    row = dict(gid=it["gid"], image_id=it["image_id"], pairs=pairs, g=g.tolist(), n_tok=len(cap_tok))
    arrays = dict(g=g)
    if it["idx"] % 4 == 0:                                                                   # noise floor: same passes, different batch composition
        g_rep = checks.coherence_gaps(sc, st, pairs, halves, bs=3, reverse=True)
        row["g0"] = (g_rep - g).tolist()
        arrays["g0"] = g_rep - g
    return row, arrays


def main(argv=None):
    ap = runner.base_parser(RUN_ID, N_ITEMS)
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
