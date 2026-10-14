"""Load the frozen modules of analysis/EXP-001 by path (the directory name has a hyphen, so it is not a package)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN_DIR = ROOT / "analysis" / "EXP-001"


def load(name: str):
    key = f"exp001_frozen_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, FROZEN_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod
