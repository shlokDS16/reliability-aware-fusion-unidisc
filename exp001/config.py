"""Constants fixed by the card. Section references are to EXP-001 v0.5."""
from __future__ import annotations

# Section 3 item 1: vocabulary and layout
TEXT_VOCAB = 32001          # Llama-2 SentencePiece + mask id 32000
MASK_ID = 32000
PAD_IDS = (0, 2)            # P: <unk> used as pad, </s>  (section 2)
IMG_OFFSET = 32001          # image code c has id 32001 + c
IMG_VOCAB = 16384
TOTAL_VOCAB = TEXT_VOCAB + IMG_VOCAB   # 48385
L_T = 32                    # masked text tail positions
W = 8                       # windows
GRID = {"k0": 32, "k+": 16, "k-": 64}   # N passes (section 2 notation)


def image_tokens(res: int) -> int:
    """(res/16)^2 image tokens at resolution res (section 3 item 1)."""
    assert res % 16 == 0
    return (res // 16) ** 2


# Section 4.5 seed pools (disjoint); half-open [lo, hi)
POOLS = {
    "PG": (90000, 90048), "PG2": (90100, 90148), "D0": (0, 64), "D1": (10000, 10128),
    "D2": (20000, 20256), "D3": (30000, 31000), "D4": (40000, 40250), "D5": (50000, 50128),
}
# Pool codes used as Philox key high word (stable, never reused)
POOL_CODE = {"PG": 1, "PG2": 2, "D0": 3, "D1": 4, "D2": 5, "D3": 6, "D4": 7, "D5": 8, "REF": 9, "GATE": 10}

# Streams of the counter-based generator (section 4.5: probes use a separate stream and never touch the sampler stream)
STREAM_SAMPLER = 0     # one float64 uniform per generated position, drawn once per sample
STREAM_PRAND = 1       # fixed random priorities for P_rand / condition R
STREAM_PROBE = 2       # probe draws
STREAM_PROBE_ORDER = 3 # probe chunk-order / auxiliary


def pool_range(name: str) -> range:
    lo, hi = POOLS[name]
    return range(lo, hi)
