"""H-A source rule (EXP-001 card v0.5, section 2). Hashed in runs/EXP-001/pilot/ before D0 is generated (the code is written now
and hashed in the gate manifest as well); L_c is read from analysis/EXP-001/L_c.txt after PG-V.

Definitions (all functions of the state alone: no look-ahead, no draws, no dependence on the commit plan or the position rule):
  Pad class P = ids {0, 2}.
  A still-masked text position j is *state-pad* if the baseline-pass marginal p1_j (float64, renormalised inside the text slice)
  puts at least 0.5 of its mass on P.
  The T->I source a* at a probe is the still-masked tail position with tail index (1-based) at most L_c that is NOT state-pad and
  has the largest max_v p1_j(v) (ties: lowest index). If none exists the probe has NO SOURCE.
  w = p1_{a*}(P) < 0.5 (content weight 1 - w > 0.5).
"""
from __future__ import annotations

import math
from pathlib import Path

PAD_IDS = (0, 2)
STATE_PAD_THRESHOLD = 0.5
HERE = Path(__file__).resolve().parent
L_C_FILE = HERE / "L_c.txt"
L_C_MIN, L_C_MAX = 8, 16


def compute_L_c(completion_lengths) -> int:
    """90th percentile of the completion length over the PG-V J samples of the rung that passes, rounded up, bounded to [8, 16]."""
    xs = sorted(completion_lengths)
    if not xs:
        raise ValueError("no completion lengths")
    # percentile by linear interpolation (numpy default), then ceil
    k = (len(xs) - 1) * 0.9
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    v = xs[lo] + (xs[hi] - xs[lo]) * (k - lo)
    return int(min(max(math.ceil(v - 1e-12), L_C_MIN), L_C_MAX))


def read_L_c(path: Path = L_C_FILE) -> int:
    return int(Path(path).read_text().split()[0])


def select_source(masked_tail_idx, maxp, pad_mass, L_c: int):
    """masked_tail_idx: 0-based tail indices of still-masked tail positions; maxp / pad_mass: aligned sequences (baseline-pass
    max marginal probability and P-mass). Returns (tail_index_0based, w, max_p) or None (no source).

    Tail index in the card is 1-based: eligible iff idx + 1 <= L_c."""
    best = None
    for j, mp, pm in zip(masked_tail_idx, maxp, pad_mass):
        j = int(j)
        if j + 1 > L_c:
            continue
        if pm >= STATE_PAD_THRESHOLD:
            continue
        if best is None or mp > best[2] or (mp == best[2] and j < best[0]):
            best = (j, float(pm), float(mp))
    return best


def state_pad_flags(pad_mass):
    return [bool(pm >= STATE_PAD_THRESHOLD) for pm in pad_mass]
