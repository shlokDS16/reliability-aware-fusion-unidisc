"""Exact check of the error-budget identity in research/review/framework-v0.md, section 2.

    python analysis/framework/check_decomposition.py

Small sequences are enumerated exactly (no sampling noise). For a random data distribution q over
V^L and a perturbed marginal predictor p_theta, the script compares

    KL(q || p_sampler)   against   sum_n E_q[ TC(x^A_n | z_n) ] + sum_n E_q[ sum_i KL(q_i || p_theta,i) ]

for (1) a deterministic state-dependent policy (expects equality), (2) a uniformly random policy
(expects KL <= right-hand side), and (3) a sample-dependent policy that keeps the sampled tokens
with the highest own probability (expects a lower output entropy than policy 1 with the same
predictor: the selection-bias term). Pure standard library; runs in seconds.
"""
from __future__ import annotations

import itertools
import math
import random

V, L, K = 3, 4, 2          # vocabulary size, length, tokens committed per step
MASK = None


def kl(p: dict, q: dict) -> float:
    return sum(a * math.log(a / q[k]) for k, a in p.items() if a > 0)


def entropy(p: dict) -> float:
    return -sum(a * math.log(a) for a in p.values() if a > 0)


def make_q(rng: random.Random) -> dict:
    w = [rng.gammavariate(0.6, 1.0) for _ in range(V ** L)]
    s = sum(w)
    return {x: a / s for x, a in zip(itertools.product(range(V), repeat=L), w)}


def consistent(x: tuple, z: tuple) -> bool:
    return all(zi is MASK or zi == xi for xi, zi in zip(x, z))


def cond_joint(q: dict, z: tuple, A: tuple) -> dict:
    """q(x^A | revealed part of z)."""
    out, tot = {}, 0.0
    for x, a in q.items():
        if consistent(x, z):
            key = tuple(x[i] for i in A)
            out[key] = out.get(key, 0.0) + a
            tot += a
    return {k: v / tot for k, v in out.items()}


def marginal(joint: dict, j: int) -> dict:
    out = {}
    for key, a in joint.items():
        out[key[j]] = out.get(key[j], 0.0) + a
    return {v: out.get(v, 0.0) for v in range(V)}


def make_predictor(q: dict, rng: random.Random, noise: float):
    """p_theta(x^i | z): the true conditional marginal mixed with a fixed random distribution."""
    cache = {}

    def p(z: tuple, i: int) -> dict:
        if (z, i) not in cache:
            true = marginal(cond_joint(q, z, (i,)), 0)
            r = random.Random(hash((z, i, rng.random() if False else 7)))
            w = [r.random() + 0.05 for _ in range(V)]
            s = sum(w)
            cache[(z, i)] = {v: (1 - noise) * true[v] + noise * w[v] / s for v in range(V)}
        return cache[(z, i)]
    return p


def masked(z: tuple) -> list[int]:
    return [i for i, zi in enumerate(z) if zi is MASK]


def policy_confidence(p):
    def pi(z: tuple) -> tuple:
        m = masked(z)
        return tuple(sorted(sorted(m, key=lambda i: (-max(p(z, i).values()), i))[:K]))
    return pi


def reveal(z: tuple, A: tuple, vals: tuple) -> tuple:
    z = list(z)
    for i, v in zip(A, vals):
        z[i] = v
    return tuple(z)


def sampler_law(p, choose) -> dict:
    """Exact output law of a sampler. `choose(z)` returns a list of (probability, set A)."""
    out: dict = {}

    def rec(z: tuple, w: float) -> None:
        if not masked(z):
            out[z] = out.get(z, 0.0) + w
            return
        for pa, A in choose(z):
            for vals in itertools.product(range(V), repeat=len(A)):
                pv = math.prod(p(z, i)[v] for i, v in zip(A, vals))
                if pv > 0:
                    rec(reveal(z, A, vals), w * pa * pv)
    rec((MASK,) * L, 1.0)
    return out


def budget(q: dict, p, choose) -> tuple[float, float]:
    """Expected total-correlation term and model-error term along data-driven trajectories."""
    fact = learn = 0.0

    def rec(z: tuple, w: float) -> None:
        nonlocal fact, learn
        if not masked(z) or w == 0:
            return
        for pa, A in choose(z):
            joint = cond_joint(q, z, A)
            margs = [marginal(joint, j) for j in range(len(A))]
            prod = {k: math.prod(margs[j][k[j]] for j in range(len(A))) for k in joint}
            fact += w * pa * kl(joint, prod)
            learn += w * pa * sum(kl(margs[j], p(z, A[j])) for j in range(len(A)))
            for vals, a in joint.items():
                rec(reveal(z, A, vals), w * pa * a)
    rec((MASK,) * L, 1.0)
    return fact, learn


def sample_dependent_law(p) -> dict:
    """Sample every masked position, keep the K samples with the highest own probability."""
    out: dict = {}

    def rec(z: tuple, w: float) -> None:
        m = masked(z)
        if not m:
            out[z] = out.get(z, 0.0) + w
            return
        for vals in itertools.product(range(V), repeat=len(m)):
            pv = math.prod(p(z, i)[v] for i, v in zip(m, vals))
            if pv == 0:
                continue
            keep = sorted(range(len(m)), key=lambda j: (-p(z, m[j])[vals[j]], m[j]))[:K]
            rec(reveal(z, tuple(m[j] for j in keep), tuple(vals[j] for j in keep)), w * pv)
    rec((MASK,) * L, 1.0)
    return out


def main() -> None:
    print(f"V={V} L={L} tokens per step K={K}; exact enumeration, natural logarithms")
    worst_gap = 0.0
    for seed in range(5):
        rng = random.Random(seed)
        q = make_q(rng)
        for noise in (0.0, 0.2):
            p = make_predictor(q, rng, noise)
            det = lambda z, pi=policy_confidence(p): [(1.0, pi(z))]
            law = sampler_law(p, det)
            lhs = kl(q, law)
            fact, learn = budget(q, p, det)
            worst_gap = max(worst_gap, abs(lhs - fact - learn))
            def pairs(z: tuple) -> list:
                combos = list(itertools.combinations(masked(z), min(K, len(masked(z)))))
                return [(1 / len(combos), c) for c in combos]
            lhs_r = kl(q, sampler_law(p, pairs))
            fr, lr = budget(q, p, pairs)
            sel = sample_dependent_law(p)
            print(f"seed {seed} noise {noise}: deterministic policy KL {lhs:.6f} = fact {fact:.6f} + learn {learn:.6f} "
                  f"(gap {lhs - fact - learn:+.1e}) | random policy KL {lhs_r:.6f} <= {fr + lr:.6f}: {lhs_r <= fr + lr + 1e-12} "
                  f"| entropy: data {entropy(q):.3f}, state-dependent {entropy(law):.3f}, sample-dependent {entropy(sel):.3f}")
    print(f"largest absolute gap for the deterministic identity: {worst_gap:.2e}")


if __name__ == "__main__":
    main()
