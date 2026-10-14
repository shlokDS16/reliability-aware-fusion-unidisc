"""Caption-end rule (EXP-001 card v0.5, section 4.1b). FROZEN before PG-V; hash recorded in runs/EXP-001/gates/manifest.json.

A pure function of the final tail tokens t_1..t_32 (1-indexed as in the card) and of their decoded pieces:
  P = {0, 2}; alphanumeric: the decoded piece contains a letter or a digit; terminator: the piece contains '.', '!', '?' or a newline.
  f  = smallest index with t_f alphanumeric (none: inf)
  e0 = smallest index with t_i in P (none: inf)
  e1 = smallest index i > f with t_i a terminator (none: inf)
  e2 = smallest index i > f whose piece matches a pattern of debris_patterns.txt (none: inf)
  e  = min(e0, e1, e2, 33).  Completion = t_1..t_{e-1}, empty if e <= f (including f = inf).  Positions i >= e are post-caption;
  post-caption tokens not in P are debris; debris share = (#debris) / 32.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

PAD_IDS = (0, 2)
INF = math.inf
HERE = Path(__file__).resolve().parent
DEFAULT_PATTERNS = HERE / "debris_patterns.txt"
TAIL_LEN = 32


def load_patterns(path: str | Path = DEFAULT_PATTERNS) -> dict:
    contains, equals_ci, digits_only = [], [], False
    for line in Path(path).read_text(encoding="utf8").splitlines():
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("contains:"):
            contains.append(line[len("contains:"):])
        elif line.startswith("equals_ci:"):
            equals_ci.append(line[len("equals_ci:"):].lower())
        elif line.strip() == "digits_only":
            digits_only = True
        else:
            raise ValueError(f"unknown pattern line: {line!r}")
    return {"contains": tuple(contains), "equals_ci": tuple(equals_ci), "digits_only": digits_only}


def is_alnum(piece: str) -> bool:
    return any(ch.isalpha() or ch.isdigit() for ch in piece)


def is_terminator(piece: str) -> bool:
    return any(c in piece for c in (".", "!", "?", "\n"))


def is_e2(piece: str, pat: dict) -> bool:
    s = piece.strip()
    if any(c in piece for c in pat["contains"]):
        return True
    if s.lower() in pat["equals_ci"]:
        return True
    if pat["digits_only"] and s != "" and all(ch.isdigit() for ch in s):
        return True
    return False


@dataclass(frozen=True)
class CaptionEnd:
    e: int                 # caption end index (1-based, <= 33)
    f: float               # first alphanumeric index (inf if none)
    e0: float
    e1: float
    e2: float
    set_by: str            # 'e0' | 'e1' | 'e2' | 'cap' (cap = 33, no terminator/pad/debris pattern)
    completion_len: int    # tokens before the caption end that belong to the completion (0 if e <= f)
    n_debris: int          # post-caption tokens not in P
    debris_share: float
    e2_set: bool           # the end was set by e2 strictly (e2 < e0 and e2 < e1 and e2 < 33)


def caption_end(tail_ids, pieces, patterns: dict | None = None) -> CaptionEnd:
    """tail_ids: the 32 final tail token ids; pieces: their decoded pieces (same length)."""
    pat = patterns if patterns is not None else load_patterns()
    n = len(tail_ids)
    assert len(pieces) == n
    f = next((i for i in range(1, n + 1) if is_alnum(pieces[i - 1])), INF)
    e0 = next((i for i in range(1, n + 1) if tail_ids[i - 1] in PAD_IDS), INF)
    e1 = next((i for i in range(1, n + 1) if i > f and is_terminator(pieces[i - 1])), INF)
    e2 = next((i for i in range(1, n + 1) if i > f and is_e2(pieces[i - 1], pat)), INF)
    cap = n + 1
    e = int(min(e0, e1, e2, cap))
    if e == e0:
        set_by = "e0"
    elif e == e1:
        set_by = "e1"
    elif e == e2:
        set_by = "e2"
    else:
        set_by = "cap"
    comp_len = 0 if e <= f else e - 1
    n_debris = sum(1 for i in range(e, n + 1) if tail_ids[i - 1] not in PAD_IDS)
    e2_set = e2 < e0 and e2 < e1 and e2 < cap and e == e2
    return CaptionEnd(e, f, e0, e1, e2, set_by, comp_len, n_debris, n_debris / n, bool(e2_set))


def completion_ids(tail_ids, ce: CaptionEnd) -> list[int]:
    return list(tail_ids[:ce.completion_len])


def post_caption_mask(ce: CaptionEnd, n: int = TAIL_LEN) -> list[bool]:
    """True for tail index i (0-based list position i-1) with i >= e."""
    return [i >= ce.e for i in range(1, n + 1)]


class PieceTable:
    """Decoded piece per token id, computed once from the pinned tokenizer and hashed, so that the rule is a pure function of
    ids and the table (tests use a synthetic table)."""

    def __init__(self, pieces: dict[int, str]):
        self.pieces = pieces

    @classmethod
    def from_tokenizer(cls, tok, n_ids: int = 32001):
        pieces = {}
        for i in range(n_ids):
            try:
                pieces[i] = tok.decode([i], skip_special_tokens=False)
            except Exception:
                pieces[i] = ""
        return cls(pieces)

    def __call__(self, ids):
        return [self.pieces.get(int(i), "") for i in ids]
