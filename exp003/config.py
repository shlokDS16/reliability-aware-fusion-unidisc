"""Constants of EXP-003 (card v0.3.2). Section numbers refer to the card. Importable from both venvs (numpy only at import)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs" / "EXP-003"
GEN_PY = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe")
EVAL_PY = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv-eval\Scripts\python.exe")

# section 3: pools, seed bases and Philox pool codes (additive registration in exp001's table, no edit of exp001/config.py)
POOL_ORDER = ("E3-PILOT", "E3-CTRL", "E3-MAIN")
POOL_SIZE = {"E3-PILOT": 16, "E3-CTRL": 48, "E3-MAIN": 150}
SEED_BASE = {"E3-PILOT": 61000, "E3-CTRL": 62000, "E3-MAIN": 60000}
RNG_POOL = {"E3-PILOT": "E3P", "E3-CTRL": "E3C", "E3-MAIN": "E3M"}
RNG_CODE = {"E3P": 31, "E3C": 32, "E3M": 33}
PERM_SEED = 1303
OFFICIAL_SEED_BASE = 7_000_000          # torch and numpy seeds = 7,000,000 + seed index i
DERANGEMENT_SEED_CROSS = 5301           # all-noun cross-prefix derangement (descriptive)
DERANGEMENT_SEED_PLACEBO = 5302         # NC-2 placebo nouns
DERANGEMENT_SEED_PC2 = 5303             # PC-2 (the card says "one fixed derangement" without a seed; chosen here, flagged)

# section 2: arms
STEPS_OFFICIAL = 32
CFG_G = 3.0
R_TEMP = 4.5
CALLS = {"P64": 64, "P32": 32, "O0": 33, "G": 64, "Ind": 64, "TF": 32}   # network calls per sample (card table; Ind: 2 per pass)
MAIN_ARMS = ("P64", "G", "O0", "P32")
PLAIN_N = {"P64": 64, "P32": 32, "Ind": 32, "TF": 32}                    # passes of the plain-sampler arms

# section 8 regime
DUTY = 0.5
CHUNK_MIN = 15.0
FIRST_CHUNK_MIN = 5.0
MAX_TEMP = 85.0
READY_TEMP = 65.0
PAUSE_S = 30.0
BUDGET_H = 6.0
HARD_STOP_H = 7.0


def register_pools():
    """Register the Philox pool codes 31-33 in exp001's table (additive and idempotent; exp001/config.py is not edited)."""
    from exp001.config import POOL_CODE
    for k, v in RNG_CODE.items():
        assert POOL_CODE.setdefault(k, v) == v
    return dict(RNG_CODE)


def seed_index(pool: str, p: int, e: int) -> int:
    return SEED_BASE[pool] + 2 * p + e
