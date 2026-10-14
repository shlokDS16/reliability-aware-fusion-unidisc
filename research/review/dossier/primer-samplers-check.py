"""Exact-enumeration check of the framework-v0 section 2 identity (primer-samplers.md).
Run: python primer-samplers-check.py   (numpy only; L=4 positions, V=3 values)
Checks
 A. state-dependent deterministic policy, sampled values, learned marginals:
    KL(q||p) == sum_n E_q[TC(x_An | z_n)] + sum_n E_q[sum_{i in An} KL(q_i||p_theta_i)]   (equality)
 B. randomised policy (seed fixed in advance): KL(q||mean_rho p_rho) <= mean_rho KL(q||p_rho)
 C. sample-dependent selection (sample all masked, keep the most confident samples), exact marginals, k=1:
    KL(q||p) > 0 although E_fact = 0 and E_learn = 0 (selection term), and output entropy drops
 D. one-step product of exact marginals has HIGHER entropy than q (so lower entropy alone does not imply E_sel)
"""
import itertools, math
import numpy as np

L, V = 4, 3
rng = np.random.default_rng(0)


def rand_joint(temp=0.35):
    t = rng.dirichlet(np.ones(V ** L) * temp).reshape((V,) * L)
    return t


def marg(joint, state, i):
    """P(x_i | x_S = state) for state = {pos: val}; returns vector length V."""
    idx = tuple(state[j] if j in state else slice(None) for j in range(L))
    sub = joint[idx]
    axes_left = [j for j in range(L) if j not in state]
    pos = axes_left.index(i)
    other = tuple(a for a in range(len(axes_left)) if a != pos)
    m = sub.sum(axis=other) if other else sub
    return m / m.sum()


def joint_cond(joint, state, A):
    """P(x_A | x_S = state) as dict val-tuple -> prob."""
    out = {}
    for vals in itertools.product(range(V), repeat=len(A)):
        s2 = dict(state)
        s2.update(dict(zip(A, vals)))
        idx = tuple(s2[j] if j in s2 else slice(None) for j in range(L))
        out[vals] = joint[idx].sum()
    tot = sum(out.values())
    return {k: v / tot for k, v in out.items()}


def perturb(joint):
    """Learned marginal predictor: true marginals times a state-dependent random tilt."""
    cache = {}

    def p_theta(state, i):
        key = (tuple(sorted(state.items())), i)
        if key not in cache:
            m = marg(joint, state, i) * np.exp(rng.normal(0, 0.4, V))
            cache[key] = m / m.sum()
        return cache[key]
    return p_theta


def policy_conf(joint, k):
    """deterministic, state-dependent: pick the k unrevealed positions whose TRUE-marginal max prob is largest."""
    def f(state):
        un = [i for i in range(L) if i not in state]
        sc = sorted(un, key=lambda i: -marg(joint, state, i).max())
        return tuple(sorted(sc[: min(k, len(un))]))
    return f


def sampler_law(p_theta, f):
    """exact output law of: state-only policy f, values sampled independently from p_theta marginals."""
    law = np.zeros((V,) * L)

    def rec(state, prob):
        if len(state) == L:
            law[tuple(state[j] for j in range(L))] += prob
            return
        A = f(state)
        for vals in itertools.product(range(V), repeat=len(A)):
            pr = prob
            for i, v in zip(A, vals):
                pr *= p_theta(state, i)[v]
            s2 = dict(state)
            s2.update(dict(zip(A, vals)))
            rec(s2, pr)
    rec({}, 1.0)
    return law


def kl(q, p):
    m = q > 0
    return float((q[m] * (np.log(q[m]) - np.log(p[m]))).sum())


def ent(p):
    m = p > 0
    return float(-(p[m] * np.log(p[m])).sum())


def decomposition(q, p_theta, f):
    fact = learn = 0.0
    for x in itertools.product(range(V), repeat=L):
        qx = q[x]
        state = {}
        while len(state) < L:
            A = f(state)
            jc = joint_cond(q, state, A)
            lq = math.log(jc[tuple(x[i] for i in A)])
            lmq = sum(math.log(marg(q, state, i)[x[i]]) for i in A)
            lmp = sum(math.log(p_theta(state, i)[x[i]]) for i in A)
            fact += qx * (lq - lmq)
            learn += qx * (lmq - lmp)
            state.update({i: x[i] for i in A})
    return fact, learn


# ---- A
q = rand_joint()
pt = perturb(q)
for k in (1, 2, 3):
    f = policy_conf(q, k)
    p = sampler_law(pt, f)
    fact, learn = decomposition(q, pt, f)
    print(f"A k={k}: KL(q||p)={kl(q,p):.6f}  E_fact+E_learn={fact+learn:.6f}  (fact={fact:.4f}, learn={learn:.4f})  diff={kl(q,p)-fact-learn:.2e}")

# ---- B
laws, kls = [], []
for seed in range(6):
    r = np.random.default_rng(100 + seed)
    perm = r.permutation(L)

    def f(state, perm=perm):
        un = [i for i in perm if i not in state]
        return tuple(sorted(un[:2]))
    p = sampler_law(pt, f)
    laws.append(p); kls.append(kl(q, p))
print(f"B: KL(q||mixture)={kl(q, np.mean(laws,0)):.6f} <= mean KL={np.mean(kls):.6f}")

# ---- C  sample all masked positions (exact marginals), keep the most confident sample, k=1
exact = lambda state, i: marg(q, state, i)


def selection_law(p_theta, keep=1):
    law = np.zeros((V,) * L)

    def rec(state, prob):
        if len(state) == L:
            law[tuple(state[j] for j in range(L))] += prob
            return
        un = [i for i in range(L) if i not in state]
        for vals in itertools.product(range(V), repeat=len(un)):
            pr = prob
            conf = []
            for i, v in zip(un, vals):
                pi = p_theta(state, i)[v]
                pr *= pi
                conf.append((pi, i, v))
            conf.sort(key=lambda t: (-t[0], t[1]))
            kept = conf[: min(keep, len(un))]
            s2 = dict(state)
            for _, i, v in kept:
                s2[i] = v
            rec(s2, pr)
    rec({}, 1.0)
    return law


p_sel = selection_law(exact, 1)
p_seq = sampler_law(exact, policy_conf(q, 1))
print(f"C: state-only k=1 exact marginals: KL={kl(q,p_seq):.2e}, H={ent(p_seq):.4f} (H(q)={ent(q):.4f})")
print(f"C: sample-then-keep-most-confident k=1: KL={kl(q,p_sel):.4f}, H={ent(p_sel):.4f}")

# ---- D  perfectly correlated pair: product of exact marginals raises entropy
qd = np.zeros((V, V)); np.fill_diagonal(qd, 1.0 / V)
prod = np.outer(qd.sum(1), qd.sum(0))
print(f"D: H(q)={ent(qd):.4f}  H(product of marginals)={ent(prod):.4f}  KL={kl(qd, prod):.4f} (= TC = ln3 = {math.log(3):.4f})")
