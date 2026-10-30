"""HOLD check for the gate runners. The existing `exp_p2.driver` only looks at `runs/<run-id>/HOLD.txt`; gate runs have their own run ids,
so the project-wide hold (`runs/P2-PROBE-02/HOLD.txt`, v1 section 13 / v2 section 11) must be checked explicitly. A runner or driver
that finds any hold file stops with exit code 7 before it loads a model or touches a GPU. This module never creates or deletes a hold file."""
from __future__ import annotations

from pathlib import Path

from exp_p2 import common
from exp_p2.gate import config

EXIT_HOLD = 7


class HoldActive(RuntimeError):
    pass


def hold_files(run_id: str) -> list[Path]:
    runs = Path(common.RUNS)
    return [runs / run_id / "HOLD.txt", runs.joinpath(*config.GLOBAL_HOLD), runs / "GATE-HOLD.txt"]


def active_holds(run_id: str) -> list[Path]:
    return [p for p in hold_files(run_id) if p.exists()]


def require_clear(run_id: str) -> None:
    h = active_holds(run_id)
    if h:
        raise HoldActive("GPU run on hold: " + "; ".join(str(p) for p in h) + " (delete a hold file only with ANONYMIZED's go-ahead)")
