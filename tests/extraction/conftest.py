import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "analysis" / "extraction" / "fixtures",):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def agreement():
    return load("agreement_mod", ROOT / "analysis" / "extraction" / "agreement.py")


@pytest.fixture(scope="session")
def draw_pilot():
    return load("draw_pilot_mod", ROOT / "analysis" / "extraction" / "draw_pilot.py")


@pytest.fixture(scope="session")
def ex_dispatch():
    return load("ex_dispatch_mod", ROOT / "tools" / "ex_dispatch.py")
