"""Synthetic prefix records for the EXP-003 statistics tests."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT / "analysis" / "EXP-003", ROOT / "analysis" / "EXP-001"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import nounkey                      # noqa: E402
import stats as S                   # noqa: E402

VOCAB = [f"thing{i}" for i in range(40)]


def make_arm(n, link=0.0, bias=(0.0, 0.0), seed=0, base=0.3, k=(3, 7), couple_count_to_bias=False):
    """n prefix records. Presence of a discordant noun in its own image: base + link + bias_e; in the sibling image: base + bias_(1-e)."""
    g = np.random.default_rng(seed)
    recs, smp, sets = [], [], []
    for p in range(n):
        ks = [int(g.integers(k[0], k[1] + 1)) for _ in (0, 1)]
        if couple_count_to_bias:                       # more nouns on the image with the larger yes-bias
            ks = [k[1], k[0]] if bias[0] > bias[1] else [k[0], k[1]]
        N = [list(g.choice(VOCAB, ks[e], replace=False)) for e in (0, 1)]
        D = list(S.discordant(N[0], N[1], nounkey.key))
        pr = lambda e, own: np.clip(base + (link if own else 0.0) + (bias[e] if own else bias[1 - e]), 0, 1)
        own = [(g.random(len(D[e])) < pr(e, True)).astype(float) for e in (0, 1)]
        sib = [(g.random(len(D[e])) < pr(e, False)).astype(float) for e in (0, 1)]
        all_own = [(g.random(len(N[e])) < pr(e, True)).astype(float) for e in (0, 1)]
        all_sib = [(g.random(len(N[e])) < pr(e, False)).astype(float) for e in (0, 1)]
        # placebo nouns: unrelated to the sample's text, so no link, only the additive bias
        npl = [len(D[e]) for e in (0, 1)]
        pown = [(g.random(npl[e]) < base + bias[e]).astype(float) for e in (0, 1)]
        psib = [(g.random(npl[e]) < base + bias[1 - e]).astype(float) for e in (0, 1)]
        recs.append(dict(ok=True, N=N, D=D, own=own, sib=sib, all_own=all_own, all_sib=all_sib, all_cross=[(g.random(len(N[e])) < base).astype(float) for e in (0, 1)],
                         pown=pown, psib=psib, iqa=[float(g.random()), float(g.random())], PL=[[], []]))
        ce = SimpleNamespace(completion_len=int(g.integers(3, 20)), debris_share=0.1, e2_set=False)
        smp.append([dict(cend=ce, nouns=[str(x) for x in N[e]], comp=" ".join(N[e]), commit_step=None, meta={}) for e in (0, 1)])
        sets.append(dict(N=N, D=D))
    return smp, sets, None, recs
