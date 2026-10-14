"""Probe schedules and a J trajectory with probes (card 8.2-8.4). The probes run inside the sampler hook on copies of the state and
use the probe stream only (G6). Not run on any endpoint data in this implementation phase; tested on the toy network."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import estimator as E, frozen, plan as P, rng
from .sampler import run_sample


@dataclass
class ProbeSpec:
    pass_index: int
    kind: str          # 'price_t2i' (plan's committed text token), 'ha_t2i' (plan-independent source a*), 'i2t'


def schedule(stage: str, traj_index: int, N: int = 32, W: int = 8, n_traj: int | None = None) -> dict[int, list[ProbeSpec]]:
    """Probe passes by stage (8.3). stage in {'D1','D2','R'}; traj_index is the 0-based index within the stage."""
    centres = P.window_centres(N // W)            # 2, 6, 10, ..., 30
    ha = [centres[0], centres[1], centres[6], centres[7]]    # window centres 1, 2, 7, 8 -> passes 2, 6, 26, 30
    sch: dict[int, list[ProbeSpec]] = {}

    def add(q, kind):
        sch.setdefault(q, []).append(ProbeSpec(q, kind))

    if stage == "D1":
        for q in centres:
            add(q, "price_t2i")
        for q in ha:
            add(q, "ha_t2i")
            if traj_index < 64:
                add(q, "i2t")
    elif stage in ("D2", "R"):
        for q in ha:
            add(q, "ha_t2i")
            add(q, "i2t")
        if (stage == "D2" and traj_index < 128) or (stage == "R" and n_traj is not None and traj_index < n_traj // 2):
            add(1, "ha_t2i")                         # pass 1 on the first 128 (D2) / n_R/2 (condition R) trajectories
            add(1, "i2t")
    else:
        raise ValueError(stage)
    return sch


def run_with_probes(net, plan, pool: str, i: int, sched: dict, L_c: int, R: int = 8, g: int = 4, rule: str = "conf",
                    u=None, prio=None, state_dtype=None):
    """J trajectory with probes. Returns (SampleResult, list of dict(probe results)). The sampler stream and the probe stream are
    disjoint, and probes never alter the state, so the tokens equal those of a probe-off run (G6)."""
    hs = frozen.load("ha_source")
    n = net.L_T + net.L_I
    u = rng.sampler_uniforms(pool, i, n) if u is None else u
    if rule == "rand" and prio is None:
        prio = rng.position_priorities(pool, i, n)
    results = []

    def hook(q, tail, img, ctx):
        for spec in sched.get(q, []):
            direction = {"price_t2i": 0, "ha_t2i": 1, "i2t": 2}[spec.kind]
            rg = rng.probe_generator(pool, i, q, direction)
            row = {"pass": q, "kind": spec.kind}
            if spec.kind == "price_t2i":
                r = E.probe_t2i(net, tail, img, ctx, [int(x) for x in ctx["sets"][0]], rg, R=R)
                sel = np.searchsorted(r.positions, ctx["sets"][1])
                row.update(source=r.source, w=r.w, passes=r.passes, price_total=float(r.arrays["total"][sel].sum()),
                           price_content=float(r.arrays["within_content"][sel].sum()) if "within_content" in r.arrays else None,
                           mean_total=float(r.arrays["total"].mean()), arrays=r.arrays, positions=r.positions)
            elif spec.kind == "ha_t2i":
                s = hs.select_source(ctx["masked_text_idx"], ctx["conf_text"], ctx["pad_mass_text"], L_c)
                if s is None:
                    row.update(no_source=True, passes=0)
                else:
                    r = E.probe_t2i(net, tail, img, ctx, [s[0]], rg, R=R)
                    row.update(source=r.source, w=r.w, passes=r.passes, arrays=r.arrays, positions=r.positions, src_maxp=s[2], tokens=r.tokens)
            else:
                r = E.probe_i2t(net, tail, img, ctx, ctx["sets"][1], rg, R=R, g=g)
                row.update(passes=r.passes, arrays=r.arrays, positions=r.positions, img_set=r.img_set,
                           pad_mass=np.asarray(ctx["pad_mass_text"]))
            results.append(row)

    res = run_sample(net, plan, u, rule=rule, prio=prio, hook=hook)
    return res, results


def expected_extra_passes(sched: dict, R: int = 8, g: int = 4, k_T: int = 1) -> int:
    """Card 8.4: extra forward passes per trajectory = sum over probes of R k_T (T->I) and R g (I->T)."""
    n = 0
    for specs in sched.values():
        for s in specs:
            n += R * k_T if s.kind != "i2t" else R * g
    return n
