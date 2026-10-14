"""Plan generator (card 5.1, 5.2). A plan is the list of per-pass commit counts; positions are chosen by the sampler's
position rule. Pure Python, no torch. Floor rule f(q, c, m) = floor(q c / m) - floor((q-1) c / m).

Arms: J, Alt, DA, DA-low, TFJ (windows), Sep_w, TF, IF, J-global, Jd, plus the identity variants of I2/I3.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

from .config import L_T, W


def f(q: int, c: int, m: int) -> int:
    """Floor rule (card 5.1): tokens committed in step q (1-based) when c tokens are spread over m steps."""
    return (q * c) // m - ((q - 1) * c) // m


@dataclass(frozen=True)
class Pass:
    n_text: int          # text tail tokens committed in this pass (chosen among masked tail positions)
    n_img: int           # image tokens committed in this pass
    window: int          # 1-based window index, 0 if the arm has no windows
    kind: str            # 'joint' | 'text' | 'image' | 'tfj1' | 'noop' | 'pooled'
    pooled: bool = False  # J-global: n_text/n_img unused, n_pooled tokens from the pooled ranking
    n_pooled: int = 0

    @property
    def total(self) -> int:
        return self.n_pooled if self.pooled else self.n_text + self.n_img


@dataclass(frozen=True)
class Plan:
    name: str
    passes: tuple
    N: int
    c_T: int
    c_I: int
    L_T: int
    L_I: int
    M: tuple = ()
    windows: int = W
    meta: dict = field(default_factory=dict, compare=False)

    def counts(self) -> list[tuple[int, int]]:
        return [(p.n_text, p.n_img) for p in self.passes]

    def totals(self) -> tuple[int, int]:
        return sum(p.n_text for p in self.passes), sum(p.n_img for p in self.passes)

    def n_forward_passes(self) -> int:
        """Passes that commit something. A pass that commits nothing is a no-op (card 3 item 2: no time input), so the
        sampler skips it and it costs no forward."""
        return sum(1 for p in self.passes if p.total > 0)


def _check(N: int, W_: int, L_T_: int, L_I: int):
    if N % W_ != 0:
        raise ValueError(f"W={W_} must divide N={N}")
    P_w = N // W_
    if P_w < 2:
        raise ValueError(f"P_w = N/W must be >= 2, got {P_w}")
    if L_T_ % W_ or L_I % W_:
        raise ValueError("W must divide L_T and L_I")
    return P_w, L_T_ // W_, L_I // W_


def _joint_window(w: int, P_w: int, c_T: int, c_I: int) -> list[Pass]:
    return [Pass(f(q, c_T, P_w), f(q, c_I, P_w), w, "joint") for q in range(1, P_w + 1)]


def _pure_window(w: int, P_w: int, c_T: int, c_I: int) -> list[Pass]:
    out = [Pass(c_T, 0, w, "text")]
    out += [Pass(0, f(q - 1, c_I, P_w - 1), w, "image") for q in range(2, P_w + 1)]
    return out


def _tfj_window(w: int, P_w: int, c_T: int, c_I: int) -> list[Pass]:
    out = [Pass(c_T, f(1, c_I, P_w), w, "tfj1")]
    out += [Pass(0, f(q, c_I, P_w), w, "image") for q in range(2, P_w + 1)]
    return out


def window_plan(name: str, M: Iterable[int], kind: str, N: int, L_I: int, L_T_: int = L_T, W_: int = W) -> Plan:
    """A schedule is a set M of non-joint windows of one kind ('pure' or 'tfj'); the other windows are joint."""
    P_w, c_T, c_I = _check(N, W_, L_T_, L_I)
    Mset = tuple(sorted(set(int(m) for m in M)))
    if any(m < 1 or m > W_ for m in Mset):
        raise ValueError("windows are 1..W")
    passes: list[Pass] = []
    for w in range(1, W_ + 1):
        if w in Mset:
            passes += _pure_window(w, P_w, c_T, c_I) if kind == "pure" else _tfj_window(w, P_w, c_T, c_I)
        else:
            passes += _joint_window(w, P_w, c_T, c_I)
    return Plan(name, tuple(passes), N, c_T, c_I, L_T_, L_I, Mset, W_, {"kind": kind})


def plan_J(N, L_I, **kw):
    return window_plan("J", (), "pure", N, L_I, **kw)


def plan_Alt(N, L_I, **kw):
    return window_plan("Alt", range(1, W + 1), "pure", N, L_I, **kw)


def plan_DA(N, L_I, M, **kw):
    return window_plan("DA", M, "pure", N, L_I, **kw)


def plan_DAlow(N, L_I, M, **kw):
    return window_plan("DA-low", M, "pure", N, L_I, **kw)


def plan_TFJ(N, L_I, M, **kw):
    return window_plan("TFJ", M, "tfj", N, L_I, **kw)


def plan_Sep(N, L_I, w, **kw):
    return window_plan(f"Sep{w}", (w,), "pure", N, L_I, **kw)


def plan_TF(N, L_I, L_T_=L_T):
    """Passes 1..8 text-only (4 tokens each), then N-8 image-only passes (floor rule). Off-support, conditional stage."""
    n_text_passes = 8
    passes = [Pass(L_T_ // n_text_passes, 0, 0, "text") for _ in range(n_text_passes)]
    m = N - n_text_passes
    passes += [Pass(0, f(q, L_I, m), 0, "image") for q in range(1, m + 1)]
    return Plan("TF", tuple(passes), N, L_T_ // n_text_passes, L_I // W, L_T_, L_I, (), 0)


def plan_IF(N, L_I, L_T_=L_T):
    n_text_passes = 8
    m = N - n_text_passes
    passes = [Pass(0, f(q, L_I, m), 0, "image") for q in range(1, m + 1)]
    passes += [Pass(L_T_ // n_text_passes, 0, 0, "text") for _ in range(n_text_passes)]
    return Plan("IF", tuple(passes), N, L_T_ // n_text_passes, L_I // W, L_T_, L_I, (), 0)


def plan_Jglobal(N, L_I, L_T_=L_T):
    """No plan: pooled top-count over both modalities, total tokens per pass f(q, L_gen, N)."""
    L_gen = L_T_ + L_I
    passes = [Pass(0, 0, 0, "pooled", True, f(q, L_gen, N)) for q in range(1, N + 1)]
    return Plan("J-global", tuple(passes), N, 0, 0, L_T_, L_I, (), 0)


def plan_Jd(N, L_I, L_T_=L_T, W_=W):
    """Diagnostic, not pass-matched: Alt's image pass structure (N - W image passes, counts as in Alt) with the L_T text
    tokens co-committed over those image passes by the floor rule."""
    alt = plan_Alt(N, L_I, L_T_=L_T_, W_=W_)
    img_counts = [p.n_img for p in alt.passes if p.n_img > 0]
    m = len(img_counts)
    assert m == N - W_
    passes = tuple(Pass(f(q, L_T_, m), c, 0, "joint") for q, c in enumerate(img_counts, 1))
    return Plan("Jd", passes, m, 0, 0, L_T_, L_I, (), 0, {"note": "not pass-matched"})


def plan_Alt_empty_text(N, L_I, L_T_=L_T, W_=W):
    """I2 (card 8.8): Alt in which the text-only passes commit nothing (no-ops) while the text is co-committed over the image
    passes as in Jd. After dropping the no-ops it equals Jd; the sampled tokens must be identical (the state does not change in a
    no-op and values are drawn by position-keyed uniforms)."""
    alt = plan_Alt(N, L_I, L_T_=L_T_, W_=W_)
    jd = plan_Jd(N, L_I, L_T_=L_T_, W_=W_)
    jd_iter = iter(jd.passes)
    out = []
    for p in alt.passes:
        if p.kind == "text":
            out.append(Pass(0, 0, p.window, "noop"))
        else:
            q = next(jd_iter)
            out.append(Pass(q.n_text, p.n_img, p.window, "image"))
    return Plan("Alt-empty-text", tuple(out), N, alt.c_T, alt.c_I, L_T_, L_I, alt.M, W_, {"I2": True})


def drop_noops(plan: Plan) -> Plan:
    return Plan(plan.name + "-dropnoop", tuple(p for p in plan.passes if p.total > 0), plan.N, plan.c_T, plan.c_I, plan.L_T,
                plan.L_I, plan.M, plan.windows, plan.meta)


def boundary_fractions(plan: Plan) -> list[tuple[int, int]]:
    """Cumulative (text, image) tokens committed at the end of each window (window arms only)."""
    cum_t = cum_i = 0
    out = {}
    for p in plan.passes:
        cum_t += p.n_text
        cum_i += p.n_img
        out[p.window] = (cum_t, cum_i)
    return [out[w] for w in sorted(out)]


def window_centres(P_w: int, W_: int = W) -> list[int]:
    """H-A / price probe centres (card 8.3): centre(w) = (w-1) P_w + 2 (passes 2, 6, ..., 30 at k0)."""
    return [(w - 1) * P_w + 2 for w in range(1, W_ + 1)]


def window_centres_kplus(W_: int = W) -> list[int]:
    """k+ probes: first pass of each 2-pass window, centre(w) = 2(w-1)+1 (passes 1, 3, ..., 15)."""
    return [2 * (w - 1) + 1 for w in range(1, W_ + 1)]


def build(arm: str, N: int, L_I: int, M: Sequence[int] = (), **kw) -> Plan:
    arm_l = arm.lower()
    if arm_l == "j":
        return plan_J(N, L_I, **kw)
    if arm_l == "alt":
        return plan_Alt(N, L_I, **kw)
    if arm_l == "da":
        return plan_DA(N, L_I, M, **kw)
    if arm_l in ("da-low", "dalow"):
        return plan_DAlow(N, L_I, M, **kw)
    if arm_l == "tfj":
        return plan_TFJ(N, L_I, M, **kw)
    if arm_l.startswith("sep"):
        return plan_Sep(N, L_I, int(arm_l[3:]), **kw)
    if arm_l == "tf":
        return plan_TF(N, L_I)
    if arm_l == "if":
        return plan_IF(N, L_I)
    if arm_l in ("j-global", "jglobal"):
        return plan_Jglobal(N, L_I)
    if arm_l == "jd":
        return plan_Jd(N, L_I)
    raise ValueError(arm)
