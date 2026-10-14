"""Unit lists of the generation stages (card 8) and their on-disk layout. Pure Python (no torch), importable from both venvs.

A unit is (arm, prefix p, seed e) of one stage; its outputs are runs/EXP-003/gen/<stage>/<tag>/p<PPP>_e<E>.{npz,json,png}; the .json is
the done marker (written last, atomically). Stage names: pilot, ctrl, m1 (P64 and G interleaved by prefix), m2 (O0), m3 (P32).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from exp003.config import RUNS, RNG_POOL, SEED_BASE, seed_index, PLAIN_N

GEN = RUNS / "gen"
STAGE_POOL = {"pilot": "E3-PILOT", "ctrl": "E3-CTRL", "m1": "E3-MAIN", "m2": "E3-MAIN", "m3": "E3-MAIN"}


@dataclass(frozen=True)
class Unit:
    stage: str
    arm: str              # P64 P32 O0 G Ind TF  (G50 = G with 50 steps)
    tag: str              # sub-directory: the arm, or G50, rerun/<arm>, hookcheck/<arm>
    p: int
    e: int
    steps: int = 32       # official arms
    cfg: float = 0.0
    instrument: bool = True
    save_png: bool = True

    @property
    def pool(self) -> str:
        return STAGE_POOL[self.stage]

    @property
    def i(self) -> int:
        return seed_index(self.pool, self.p, self.e)

    @property
    def kind(self) -> str:
        return "official" if self.arm in ("O0", "G") else "plain"

    def base(self, gen_dir: Path = GEN) -> Path:
        return Path(gen_dir) / self.stage / self.tag / f"p{self.p:03d}_e{self.e}"

    def marker(self, gen_dir: Path = GEN) -> Path:
        return self.base(gen_dir).with_suffix(".json")


def _arm_unit(stage, arm, p, e, tag=None, **kw):
    cfg = 3.0 if arm == "G" else 0.0
    return Unit(stage, arm, tag or arm, p, e, cfg=cfg, **kw)


def pilot_units(n_prefix: int = 16) -> list:
    """Cost pilot (card 8 item 1): P64, P32, O0, G on 16 prefixes x 2 seeds interleaved by prefix; G at 50 steps on the first 8 prefixes
    (seed 0); Ind and TF on the first 4 prefixes; determinism reruns of 4 plain and 4 official units; the hook check on 8 official units
    (first 4 prefixes, seed 0, bare `_sample` without the read-only hooks)."""
    u = []
    for p in range(n_prefix):
        for e in (0, 1):
            for arm in ("P64", "G", "O0", "P32"):
                u.append(_arm_unit("pilot", arm, p, e))
        if p < 8:
            u.append(Unit("pilot", "G", "G50", p, 0, steps=50, cfg=3.0))
        if p < 4:
            for e in (0, 1):
                u.append(Unit("pilot", "Ind", "Ind", p, e))
                u.append(Unit("pilot", "TF", "TF", p, e))
    for arm in ("P64", "P32"):
        for p in (0, 1):
            u.append(_arm_unit("pilot", arm, p, 0, tag=f"rerun/{arm}", save_png=False))
    for arm in ("O0", "G"):
        for p in (0, 1):
            u.append(_arm_unit("pilot", arm, p, 0, tag=f"rerun/{arm}", save_png=False))
        for p in range(4):
            u.append(_arm_unit("pilot", arm, p, 0, tag=f"hookcheck/{arm}", instrument=False, save_png=False))
    return u


def ctrl_units(n_prefix: int = 48) -> list:
    return [Unit("ctrl", arm, arm, p, e) for p in range(n_prefix) for e in (0, 1) for arm in ("Ind", "TF")]


def main_units(stage: str, n_gen: int) -> list:
    arms = {"m1": ("P64", "G"), "m2": ("O0",), "m3": ("P32",)}[stage]
    return [_arm_unit(stage, arm, p, e) for p in range(n_gen) for e in (0, 1) for arm in arms]


def units_for(stage: str, n_gen: int | None = None) -> list:
    if stage == "pilot":
        return pilot_units()
    if stage == "ctrl":
        return ctrl_units()
    if n_gen is None:
        n_gen = json.loads((RUNS / "n_conf.json").read_text())["n_generate"]
    return main_units(stage, n_gen)


def load_pool_items(pool: str, pools_json: Path = RUNS / "pools.json") -> list:
    return json.loads(Path(pools_json).read_text(encoding="utf8"))["pools"][pool]["items"]


def stage_done(units, gen_dir: Path = GEN) -> bool:
    return all(u.marker(gen_dir).exists() for u in units)


def plain_passes(arm: str) -> int:
    return PLAIN_N[arm]
