"""Exact-enumeration checks for research/review/method/selection-term.md (T2 to T7).

    python analysis/framework/check_selection.py > analysis/framework/check_selection.log

numpy only, all seeds fixed, natural logarithms. Every claim tagged [V] in the report has a
line here; each check prints PASS or FAIL and the script ends with a summary.

Conventions (shared with check_decomposition.py and primer-samplers-check.py):
  * state z: tuple of length L, -1 marks a masked position;
  * a step kernel maps a state to {(A, y): prob}, A a sorted tuple of positions, y their values;
  * sample-then-filter (SF): draw every masked position from its (possibly tempered) law,
    score each draw, keep the top k; ties broken by lowest index (as in the earlier scripts)
    unless tie="random" (exact average over all priority orders);
  * position law rho(A | z) = sum_y kernel(z)[(A, y)];
  * matched rank-then-sample (mRS): same rho, values drawn independently from p_theta;
  * data path law Q: q(x) times prod_n rho(A_n | z_n), z_n built from x;
  * sampler path law P: prod_n kernel(z_n)[(A_n, y_n)].
"""
from __future__ import annotations

import itertools
import math
from functools import lru_cache

import numpy as np

FAILS: list[str] = []
NCHECK = [0]


def check(name: str, cond: bool, detail: str = "") -> None:
    NCHECK[0] += 1
    if not cond:
        FAILS.append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}{(' | ' + detail) if detail else ''}")


def ent(p) -> float:
    p = np.asarray(p, float).ravel()
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def klv(a, b) -> float:
    a = np.asarray(a, float).ravel()
    b = np.asarray(b, float).ravel()
    m = a > 0
    if np.any(b[m] <= 0):
        return math.inf
    return float((a[m] * (np.log(a[m]) - np.log(b[m]))).sum())


def kld(P: dict, Q: dict) -> float:
    s = 0.0
    for key, a in P.items():
        if a > 0:
            b = Q.get(key, 0.0)
            if b <= 0:
                return math.inf
            s += a * math.log(a / b)
    return s


def masked(z):
    return [i for i, v in enumerate(z) if v < 0]


def reveal(z, A, y):
    z = list(z)
    for i, v in zip(A, y):
        z[i] = v
    return tuple(z)


# ----------------------------------------------------------------------------- data side
class Data:
    def __init__(self, q: np.ndarray):
        self.q = q / q.sum()
        self.L = q.ndim
        self.V = q.shape[0]
        self._cache = {}

    def joint(self, z, A):
        """q(x^A | revealed part of z) as an array with axes in the order of sorted A.
        Uniform if the state has zero probability (only used off-support)."""
        key = (z, tuple(A))
        if key in self._cache:
            return self._cache[key]
        idx = tuple(v if v >= 0 else slice(None) for v in z)
        t = self.q[idx]
        M = masked(z)
        keep = [M.index(i) for i in A]
        other = tuple(a for a in range(len(M)) if a not in keep)
        m = t.sum(axis=other) if other else t
        tot = m.sum()
        m = m / tot if tot > 0 else np.full(m.shape, 1.0 / m.size)
        self._cache[key] = m
        return m

    def marg(self, z, i):
        return self.joint(z, (i,))

    def prob_state(self, z):
        idx = tuple(v if v >= 0 else slice(None) for v in z)
        return float(self.q[idx].sum())


def make_pred(D: Data, noise=0.0, seed=0):
    """p_theta(x^i | z): exact conditional marginal, optionally tilted by a state-seeded log-normal."""
    cache = {}

    def p(z, i):
        key = (z, i)
        if key not in cache:
            m = D.marg(z, i).copy()
            if noise > 0:
                h = seed
                for v in z:
                    h = h * 13 + (v + 2)
                h = h * 13 + i
                r = np.random.default_rng(h % (2 ** 63))
                m = m * np.exp(r.normal(0.0, noise, m.size))
                m = m / m.sum()
            cache[key] = m
        return cache[key]
    return p


# ----------------------------------------------------------------------------- kernels
def k_sf(p, k, V, tau=1.0, score="prob", tie="index"):
    """Sample-then-filter kernel. score: 'prob' = probability of the drawn value under the
    untempered marginal; 'margin' = p(y) - max_{u != y} p(u) (margin of the drawn value)."""
    cache = {}

    def law(z, i):
        m = p(z, i)
        if tau == 1.0:
            return m
        w = m ** (1.0 / tau)
        return w / w.sum()

    def sc(z, i, v):
        m = p(z, i)
        if score == "prob":
            return m[v]
        others = np.delete(m, v)
        return m[v] - others.max()

    def ker(z):
        if z in cache:
            return cache[z]
        M = masked(z)
        kk = min(k, len(M))
        laws = [law(z, i) for i in M]
        prios = list(itertools.permutations(range(len(M)))) if tie == "random" else [tuple(range(len(M)))]
        out: dict = {}
        for vals in itertools.product(range(V), repeat=len(M)):
            pr = 1.0
            for j, v in enumerate(vals):
                pr *= laws[j][v]
            if pr == 0:
                continue
            scores = [sc(z, M[j], vals[j]) for j in range(len(M))]
            for pri in prios:
                order = sorted(range(len(M)), key=lambda j: (-scores[j], pri[j]))
                sel = sorted(order[:kk])
                key = (tuple(M[j] for j in sel), tuple(vals[j] for j in sel))
                out[key] = out.get(key, 0.0) + pr / len(prios)
        cache[z] = out
        return out
    return ker


def pos_law(kd: dict) -> dict:
    r: dict = {}
    for (A, _), a in kd.items():
        r[A] = r.get(A, 0.0) + a
    return r


def k_rs(p, rho, V, transform=None):
    """Rank-then-sample: positions from rho(z) (dict A -> prob, state only), values independent
    from transform(p) (state-only marginal transform: temperature, top-p, guidance...)."""
    cache = {}

    def ker(z):
        if z in cache:
            return cache[z]
        out = {}
        for A, ra in rho(z).items():
            laws = [p(z, i) if transform is None else transform(p(z, i)) for i in A]
            for y in itertools.product(range(V), repeat=len(A)):
                pr = ra
                for j, v in enumerate(y):
                    pr *= laws[j][v]
                if pr > 0:
                    out[(A, y)] = out.get((A, y), 0.0) + pr
        cache[z] = out
        return out
    return ker


def k_matched(ker, p, V):
    """Matched rank-then-sample: the position law of ker, values from p_theta."""
    return k_rs(p, lambda z: pos_law(ker(z)), V)


def k_joint(D: Data, rho, V):
    """Exact joint draw inside the committed set (value rule = q(y | A, z))."""
    cache = {}

    def ker(z):
        if z in cache:
            return cache[z]
        out = {}
        for A, ra in rho(z).items():
            jq = D.joint(z, A)
            for y in itertools.product(range(V), repeat=len(A)):
                if jq[y] > 0:
                    out[(A, y)] = ra * float(jq[y])
        cache[z] = out
        return out
    return ker


def rho_conf(p, k):
    """deterministic: top-k masked positions by max_v p(v | z), ties by index (state only)."""
    def r(z):
        M = masked(z)
        s = sorted(M, key=lambda i: (-p(z, i).max(), i))
        return {tuple(sorted(s[:min(k, len(M))])): 1.0}
    return r


def rho_fixed(order_steps):
    """deterministic fixed partition: list of position tuples, committed in turn."""
    def r(z):
        for A in order_steps:
            if all(z[i] < 0 for i in A):
                return {tuple(sorted(A)): 1.0}
        raise RuntimeError("no step left")
    return r


def rho_uniform(k):
    def r(z):
        M = masked(z)
        c = list(itertools.combinations(M, min(k, len(M))))
        return {A: 1.0 / len(c) for A in c}
    return r


# ----------------------------------------------------------------------------- laws and paths
def out_law(ker, L):
    out: dict = {}

    def rec(z, w):
        if not masked(z):
            out[z] = out.get(z, 0.0) + w
            return
        for (A, y), a in ker(z).items():
            rec(reveal(z, A, y), w * a)
    rec((-1,) * L, 1.0)
    return out


def paths_P(ker, L):
    out: dict = {}

    def rec(z, path, w):
        if not masked(z):
            out[path] = out.get(path, 0.0) + w
            return
        for (A, y), a in ker(z).items():
            rec(reveal(z, A, y), path + ((A, y),), w * a)
    rec((-1,) * L, (), 1.0)
    return out


def paths_Q(D: Data, rho_of, L, V):
    out: dict = {}

    def rec(z, path, w):
        if not masked(z):
            out[path] = out.get(path, 0.0) + w
            return
        for A, ra in rho_of(z).items():
            jq = D.joint(z, A)
            for y in itertools.product(range(V), repeat=len(A)):
                if jq[y] > 0:
                    rec(reveal(z, A, y), path + ((A, y),), w * ra * float(jq[y]))
    rec((-1,) * L, (), 1.0)
    return out


def x_of(path, L):
    z = [-1] * L
    for A, y in path:
        for i, v in zip(A, y):
            z[i] = v
    return tuple(z)


def marg_x(pd: dict, L):
    out: dict = {}
    for path, a in pd.items():
        x = x_of(path, L)
        out[x] = out.get(x, 0.0) + a
    return out


def kernel_array(kd, A, V):
    r = sum(a for (B, _), a in kd.items() if B == A)
    arr = np.zeros((V,) * len(A))
    for (B, y), a in kd.items():
        if B == A:
            arr[y] += a / r
    return arr, r


def prod_array(vecs):
    out = np.array(1.0)
    for v in vecs:
        out = np.multiply.outer(out, v)
    return out


def budget(D: Data, p, ker, V):
    """Data-side budget along Q (position law of ker): E_fact, E_learn, E_sel."""
    acc = {"fact": 0.0, "learn": 0.0, "sel": 0.0}

    def rec(z, w):
        if not masked(z) or w == 0:
            return
        kd = ker(z)
        for A, ra in pos_law(kd).items():
            jq = D.joint(z, A)
            margs = [D.marg(z, i) for i in A]
            kap, _ = kernel_array(kd, A, V)
            PA = prod_array([p(z, i) for i in A])
            acc["fact"] += w * ra * klv(jq, prod_array(margs))
            acc["learn"] += w * ra * sum(klv(margs[j], p(z, A[j])) for j in range(len(A)))
            acc["sel"] += w * ra * (klv(jq, kap) - klv(jq, PA))
            for y in itertools.product(range(V), repeat=len(A)):
                if jq[y] > 0:
                    rec(reveal(z, A, y), w * ra * float(jq[y]))
    rec((-1,) * D.L, 1.0)
    return acc["fact"], acc["learn"], acc["sel"]


def step_distortion(kd, p, z):
    """D(z) = KL(kernel(z) || rho(z) prod p_theta) (reverse, model-only)."""
    rho = pos_law(kd)
    s = 0.0
    for (A, y), a in kd.items():
        ref = rho[A]
        for i, v in zip(A, y):
            ref *= p(z, i)[v]
        s += a * math.log(a / ref)
    return s


def self_distortion(ker, p, L):
    tot = [0.0]

    def rec(z, w):
        if not masked(z):
            return
        kd = ker(z)
        tot[0] += w * step_distortion(kd, p, z)
        for (A, y), a in kd.items():
            rec(reveal(z, A, y), w * a)
    rec((-1,) * L, 1.0)
    return tot[0]


def sampler_states(ker, L):
    """all states visited by the sampler with their visit probability."""
    st: dict = {}

    def rec(z, w):
        if not masked(z):
            return
        st[z] = st.get(z, 0.0) + w
        for (A, y), a in ker(z).items():
            rec(reveal(z, A, y), w * a)
    rec((-1,) * L, 1.0)
    return st


# ----------------------------------------------------------------------------- T2 closed form
def sf_closed(laws, scores, k, prio=None):
    """Closed-form law of the SF commit for one state. laws[j], scores[j]: arrays over V for the
    j-th masked position (in index order). prio[j]: tie priority (smaller wins). Returns
    {(A_idx, y): prob} with A_idx indices into the masked list."""
    n = len(laws)
    V = len(laws[0])
    prio = list(range(n)) if prio is None else prio
    out = {}
    for A in itertools.combinations(range(n), min(k, n)):
        rest = [j for j in range(n) if j not in A]
        for y in itertools.product(range(V), repeat=len(A)):
            pr = 1.0
            for a, v in zip(A, y):
                pr *= laws[a][v]
            if pr == 0:
                continue
            cs = [scores[a][v] for a, v in zip(A, y)]
            m = min(cs)
            tied = [a for a, c in zip(A, cs) if c == m]
            istar = max(tied, key=lambda a: prio[a])
            for j in rest:
                lose = laws[j][(scores[j] < m)].sum() + (laws[j][(scores[j] == m)].sum() if prio[j] > prio[istar] else 0.0)
                pr *= lose
            if pr > 0:
                out[(A, y)] = pr
    return out


def sf_enum_onestate(laws, scores, k, prio=None):
    n = len(laws)
    V = len(laws[0])
    prio = list(range(n)) if prio is None else prio
    out = {}
    for vals in itertools.product(range(V), repeat=n):
        pr = math.prod(laws[j][vals[j]] for j in range(n))
        if pr == 0:
            continue
        order = sorted(range(n), key=lambda j: (-scores[j][vals[j]], prio[j]))
        A = tuple(sorted(order[:k]))
        key = (A, tuple(vals[a] for a in A))
        out[key] = out.get(key, 0.0) + pr
    return out


def r_max(p, N):
    """law of the value committed by SF at k = 1 among N iid positions with marginal p (distinct
    probabilities): max of N draws in score order."""
    out = np.zeros_like(p)
    for v in range(len(p)):
        F = p[p < p[v]].sum()
        out[v] = (F + p[v]) ** N - F ** N
    return out


def iid_random_D(p, N, k):
    """D = KL(kappa || rho prod p) for SF with N iid positions of marginal p, top-k by own
    probability, random tie-breaking. Vectorised over y in V^k. By symmetry rho is uniform and
    kappa(y | A) = C(N,k) prod p(y_i) Phi(y), Phi(y) = sum_u C(N-k,u) F^(N-k-u) g^u / C(t+u,t),
    m = min score in y, t = #entries of y at score m, F = P(score < m), g = P(score = m)."""
    V = len(p)
    grids = np.meshgrid(*([np.arange(V)] * k), indexing="ij")
    ys = np.stack([g.ravel() for g in grids], axis=1)
    sc = p[ys]
    m = sc.min(axis=1)
    t = (sc == m[:, None]).sum(axis=1)
    F = np.array([p[p < mm].sum() for mm in m])
    g = np.array([p[p == mm].sum() for mm in m])
    R = N - k
    Phi = np.zeros(len(m))
    for u in range(R + 1):
        Phi += math.comb(R, u) * F ** (R - u) * g ** u / np.array([math.comb(int(tt) + u, int(tt)) for tt in t])
    base = np.prod(p[ys], axis=1)
    kap = math.comb(N, k) * base * Phi
    assert abs(kap.sum() - 1) < 1e-9, kap.sum()
    msk = kap > 0
    return float((kap[msk] * np.log(math.comb(N, k) * Phi[msk])).sum())


def iid_topk_count_law(p, m, k):
    """law of the value counts of the top-k (by own probability) among m iid draws from p.
    Returns {count tuple: prob}. Ties between equal scores do not change the counts."""
    V = len(p)
    order = list(np.argsort(-p, kind="stable"))
    out: dict = {}

    def comps(n, parts):
        if parts == 1:
            yield (n,)
            return
        for i in range(n + 1):
            for rest in comps(n - i, parts - 1):
                yield (i,) + rest
    for c in comps(m, V):
        pr = math.factorial(m) / math.prod(math.factorial(x) for x in c) * math.prod(p[v] ** c[v] for v in range(V))
        t = [0] * V
        left = k
        for v in order:
            take = min(left, c[v])
            t[v] = take
            left -= take
        t = tuple(t)
        out[t] = out.get(t, 0.0) + pr
    return out


def iid_sf_count_law(p, N, sched):
    """log-probabilities of the final value counts of SF on N iid positions; sched = tokens per step.
    Unselected draws are re-masked and redrawn, and with iid data the remaining positions stay iid p."""
    V = len(p)
    logd = {(0,) * V: 0.0}
    m = N
    for k in sched:
        if k == 1:
            step = {tuple(int(u == v) for u in range(V)): r for v, r in enumerate(r_max(p, m))}
        else:
            step = iid_topk_count_law(p, m, k)
        nd: dict = {}
        for c, la in logd.items():
            for t, pr in step.items():
                if pr <= 0:
                    continue
                c2 = tuple(a + b for a, b in zip(c, t))
                v = la + math.log(pr)
                nd[c2] = float(np.logaddexp(nd[c2], v)) if c2 in nd else v
        logd = nd
        m -= k
    return logd


def iid_count_kls(p, N, logd):
    """forward and reverse KL between iid q = p^N and the SF law, on counts (both laws exchangeable)."""
    fwd = rev = 0.0
    for c, lp in logd.items():
        lq = math.lgamma(N + 1) - sum(math.lgamma(x + 1) for x in c) + sum(c[v] * math.log(p[v]) for v in range(len(p)))
        fwd += math.exp(lq) * (lq - lp)
        rev += math.exp(lp) * (lp - lq)
    return fwd, rev


def harmonic(n):
    return sum(1.0 / j for j in range(1, n + 1))


def kl_cont(N, k):
    return math.log(math.comb(N, k)) - (N - k) * (harmonic(N) - harmonic(N - k))


# ============================================================================= checks
def section(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


def main():
    rng = np.random.default_rng(20261014)

    # ------------------------------------------------------------------ T2
    section("T2  law of the committed (position, value) under sample-then-filter")
    worst = 0.0
    for trial in range(300):
        n = int(rng.integers(1, 5))
        V = int(rng.integers(2, 5))
        if trial % 3 == 0:   # marginals with exact ties (multiples of 1/4 or 1/8)
            laws = []
            for _ in range(n):
                w = rng.integers(0, 4, V).astype(float)
                if w.sum() == 0:
                    w[0] = 1
                laws.append(w / w.sum())
        else:
            laws = [rng.dirichlet(np.ones(V) * rng.choice([0.2, 1.0, 5.0])) for _ in range(n)]
        kind = trial % 2
        scores = laws if kind == 0 else [np.array([l[v] - np.delete(l, v).max() for v in range(V)]) for l in laws]
        k = int(rng.integers(1, n + 1))
        prio = list(rng.permutation(n))
        a = sf_closed(laws, scores, k, prio)
        b = sf_enum_onestate(laws, scores, k, prio)
        keys = set(a) | set(b)
        worst = max(worst, max(abs(a.get(x, 0) - b.get(x, 0)) for x in keys))
    check("T2.1 closed form (any k, ties, prob or margin score, any priority) = enumeration, 300 states",
          worst < 1e-12, f"max abs diff {worst:.1e}")

    # monotone reweighting and majorisation, k = 1
    viol_mono = viol_H = 0
    worst_ratio = 0.0
    for trial in range(2000):
        n = int(rng.integers(2, 6))
        V = int(rng.integers(2, 6))
        laws = [rng.dirichlet(np.ones(V) * rng.choice([0.2, 1.0, 5.0])) for _ in range(n)]
        kd = sf_closed(laws, laws, 1)
        for i in range(n):
            ri = sum(val for (A, y), val in kd.items() if A == (i,))
            if ri < 1e-14:
                continue
            kap = np.array([kd.get(((i,), (v,)), 0.0) for v in range(V)]) / ri
            o = np.argsort(laws[i])
            ratio = kap[o] / laws[i][o]
            d = np.diff(ratio)
            worst_ratio = min(worst_ratio, d.min() / max(ratio.max(), 1e-300))
            if np.any(d < -1e-9 * ratio.max()):
                viol_mono += 1
            if ent(kap) > ent(laws[i]) + 1e-12:
                viol_H += 1
    check("T2.2 k=1: kappa_i(v)/p_i(v) nondecreasing in p_i(v) (2000 states)", viol_mono == 0, f"violations {viol_mono}")
    check("T2.3 k=1: H(kappa_i) <= H(p_i) at every selected position (majorisation)", viol_H == 0, f"violations {viol_H}")

    # equality conditions
    l1 = [np.array([0.5, 0.3, 0.2])]
    kd = sf_closed(l1, l1, 1)
    check("T2.4 one masked position: SF = RS", max(abs(kd[((0,), (v,))] - l1[0][v]) for v in range(3)) < 1e-15)
    lu = [np.full(4, 0.25), np.array([0.25, 0.25, 0.5, 0.0])]
    kd = sf_closed(lu, lu, 1)
    r0 = sum(val for (A, y), val in kd.items() if A == (0,))
    kap0 = np.array([kd.get(((0,), (v,)), 0) for v in range(4)]) / r0
    check("T2.5 position with a flat marginal on its support: committed value law unchanged", np.allclose(kap0, lu[0]))
    lk = [np.array([0.6, 0.4]), np.array([0.3, 0.7])]
    kd = sf_closed(lk, lk, 2)
    rs = {((0, 1), (a, b)): lk[0][a] * lk[1][b] for a in range(2) for b in range(2)}
    check("T2.6 k = number of masked positions: SF = RS", max(abs(kd.get(x, 0) - rs[x]) for x in rs) < 1e-15)

    # k >= 2: committed values are coupled through the minimum score
    tcv = 0.0
    for trial in range(400):
        V = int(rng.integers(2, 5))
        laws = [rng.dirichlet(np.ones(V) * rng.choice([0.3, 1.0, 3.0])) for _ in range(3)]
        kd = sf_closed(laws, laws, 2)
        for A, ra in pos_law(kd).items():
            if ra < 1e-6:
                continue
            arr, _ = kernel_array({key: v for key, v in kd.items() if key[0] == A}, A, V)
            tcv = max(tcv, klv(arr, np.outer(arr.sum(1), arr.sum(0))))
    check("T2.7 k=2: SF value law inside the committed set is not a product (max TC over 400 states > 0)", tcv > 1e-3, f"max TC = {tcv:.4f} nats")

    # iid identical marginals: max-of-N law
    worst = 0.0
    for trial in range(200):
        V = int(rng.integers(2, 5))
        N = int(rng.integers(1, 5))
        p = rng.dirichlet(np.ones(V))
        kd = sf_enum_onestate([p] * N, [p] * N, 1)
        val = np.zeros(V)
        for (A, y), a in kd.items():
            val[y[0]] += a
        worst = max(worst, np.abs(val - r_max(p, N)).max())
    check("T2.8 iid marginals, k=1: committed value law = (F+p)^N - F^N", worst < 1e-12, f"max abs diff {worst:.1e}")

    # many-position limit: r_N -> point mass at the mode; large-vocabulary limit -> continuous
    p = np.array([0.45, 0.35, 0.2])
    print("  many positions, p = (0.45, 0.35, 0.20): N, P(commit mode), KL(r_N||p), -log p_max, log N - 1 + 1/N")
    prev = -1
    mono = True
    for N in (1, 2, 4, 8, 16, 32, 64, 128):
        r = r_max(p, N)
        d = klv(r, p)
        mono &= d >= prev - 1e-15
        prev = d
        print(f"    N={N:4d}  {r[0]:.6f}  {d:.6f}  {-math.log(p.max()):.6f}  {math.log(N) - 1 + 1 / N:.6f}")
    check("T2.9 KL(r_N||p) nondecreasing in N and -> -log p_max (fixed p)", mono and abs(prev + math.log(p.max())) < 1e-6)

    # ------------------------------------------------------------------ T3 sizes
    section("T3  size: universal bounds, iid closed forms, continuous limit, the [V] toy decomposed")
    viol = viol2 = viol3 = 0
    maxratio = 0.0
    for trial in range(1500):
        n = int(rng.integers(2, 6))
        V = int(rng.integers(2, 5))
        laws = [rng.dirichlet(np.ones(V) * rng.choice([0.2, 1.0, 5.0])) for _ in range(n)]
        k = int(rng.integers(1, n + 1))
        kd = sf_closed(laws, laws, k)
        rho = pos_law(kd)
        Dv = sum(a * math.log(a / (rho[A] * math.prod(laws[i][v] for i, v in zip(A, y)))) for (A, y), a in kd.items())
        Hr = ent(list(rho.values()))
        if Dv > Hr + 1e-10:
            viol += 1
        if Hr > math.log(math.comb(n, k)) + 1e-10:
            viol2 += 1
        if Hr > 1e-8:
            maxratio = max(maxratio, Dv / Hr)
    check("T3.1 per-step distortion D <= H(rho) (1500 random states, k = 1..n)", viol == 0, f"violations {viol}, max D/H(rho) = {maxratio:.3f}")
    check("T3.2 H(rho) <= log C(N, k)", viol2 == 0)

    # iid, k = 1, random tie-breaking: D = KL(r_N || p) <= log N - 1 + 1/N; index tie-breaking D >= KL(r_N||p)
    viol = viol_idx = 0
    for trial in range(300):
        V = int(rng.integers(2, 5))
        N = int(rng.integers(2, 5))
        p = rng.dirichlet(np.ones(V) * rng.choice([0.3, 1.0, 10.0]))
        dr = klv(r_max(p, N), p)
        if dr > math.log(N) - 1 + 1 / N + 1e-12:
            viol += 1
        kd = sf_enum_onestate([p] * N, [p] * N, 1)
        rho = pos_law(kd)
        Didx = sum(a * math.log(a / (rho[A] * p[y[0]])) for (A, y), a in kd.items())
        if Didx < dr - 1e-12:
            viol_idx += 1
    check("T3.3 iid k=1: KL(r_N||p) <= log N - 1 + 1/N (continuous best-of-N value)", viol == 0, f"violations {viol}")
    check("T3.4 iid k=1, index tie-breaking: D >= KL(r_N||p) (position-value coupling adds)", viol_idx == 0)

    # iid marginals, random tie-breaking: closed form (vectorised) checked against the permutation average
    worst = 0.0
    for trial in range(60):
        V = int(rng.integers(2, 4))
        N = int(rng.integers(2, 5))
        k = int(rng.integers(1, N + 1))
        p = rng.dirichlet(np.ones(V))
        if trial % 4 == 0:
            p = np.array([0.5, 0.25, 0.25][:V]) if V == 3 else np.array([0.5, 0.5])
        prios = list(itertools.permutations(range(N)))
        agg: dict = {}
        for pr in prios:
            for key, a in sf_closed([p] * N, [p] * N, k, list(pr)).items():
                agg[key] = agg.get(key, 0.0) + a / len(prios)
        rho = pos_law(agg)
        Dv = sum(a * math.log(a / (rho[A] * math.prod(p[v] for v in y))) for (A, y), a in agg.items())
        worst = max(worst, abs(Dv - iid_random_D(p, N, k)))
    check("T3.5 iid, random tie-breaking: vectorised closed form for D = permutation-averaged enumeration (60 cases, with ties)",
          worst < 1e-10, f"max abs diff {worst:.1e}")

    # continuous limit for general k: fine near-uniform vocabulary
    print("  fine vocabulary (V=150 for k<3, V=60 for k=3; near-uniform), random tie-breaking: N, k, D_discrete, KL_cont(N,k), log C(N,k)")
    ok = True
    for N, k in ((2, 1), (4, 1), (8, 1), (3, 2), (4, 2), (8, 2), (6, 3), (8, 3)):
        p = np.random.default_rng(N * 10 + k).dirichlet(np.ones(150 if k < 3 else 60) * 500.0)
        Dv = iid_random_D(p, N, k)
        kc = kl_cont(N, k)
        ok &= (Dv <= kc + 1e-9) and (Dv > 0.9 * kc)
        print(f"    N={N} k={k}  {Dv:.6f}  {kc:.6f}  {math.log(math.comb(N, k)):.6f}")
    check("T3.6 random tie-breaking: D_discrete <= KL_cont(N,k) and within 10% of it (fine vocabulary)", ok)
    viol = 0
    for trial in range(300):
        V = int(rng.integers(2, 8))
        p = rng.dirichlet(np.ones(V) * rng.choice([0.2, 1.0, 5.0]))
        for k in (1, 2):
            for N in range(k, 7):
                if iid_random_D(p, N, k) > kl_cont(N, k) + 1e-10:
                    viol += 1
    check("T3.7 KL_cont(N,k) bounds D for any marginal (300 random p, k=1,2, N<=6)", viol == 0, f"violations {viol}")
    viol = 0
    for trial in range(300):
        V = int(rng.integers(2, 8))
        p = rng.dirichlet(np.ones(V) * rng.choice([0.2, 1.0, 5.0]))
        prev = -1.0
        for N in range(1, 65):
            d = klv(r_max(p, N), p)
            if d < prev - 1e-12 or d > -math.log(p.max()) + 1e-12:
                viol += 1
            prev = d
    check("T3.8 iid k=1: KL(r_N||p) nondecreasing in N and <= -log p_max (300 random p, N<=64)", viol == 0, f"violations {viol}")

    # iid sequences: SF every step, random tie-breaking, exact on counts (log domain)
    print("  iid sequence of N positions, V=3, p=(0.45,0.35,0.20), SF k=1 every step, random tie-breaking, exact on counts:")
    print("    N   KL(q||p_SF)  KL(p_SF||q)  sum_m KL(r_m||p) (self-distortion)  log N!-N+H_N (fine-V value)")
    p = np.array([0.45, 0.35, 0.2])
    rows = []
    okb = True
    for N in (1, 2, 4, 8, 16, 32, 64):
        logd = iid_sf_count_law(p, N, [1] * N)
        fwd, rev = iid_count_kls(p, N, logd)
        selfd = sum(klv(r_max(p, m), p) for m in range(1, N + 1))
        okb &= rev <= selfd + 1e-9
        rows.append((N, fwd, rev, selfd))
        print(f"    {N:3d}  {fwd:10.5f}  {rev:10.5f}  {selfd:10.5f}  {math.lgamma(N + 1) - N + harmonic(N):10.5f}")
    check("T3.9 iid run: KL(p_SF||q) <= summed self-distortion (data processing)", okb)
    check("T3.10 iid run: forward KL(q||p_SF) grows with N and faster than linearly (ratio KL(64)/KL(32) > 2)",
          all(rows[i + 1][1] > rows[i][1] for i in range(len(rows) - 1)) and rows[-1][1] / rows[-2][1] > 2,
          f"KL(32)={rows[-2][1]:.2f}, KL(64)={rows[-1][1]:.2f}")
    check("T3.10b iid run: self-distortion grows at most linearly: per-token value <= -log p_max",
          all(r[3] / r[0] <= -math.log(p.max()) + 1e-12 for r in rows))
    # dependence on the number of steps T at fixed length (iid data, so E_fact = 0 for every schedule)
    Lr = 24
    print(f"  iid, L={Lr}, k tokens per step (T = L/k steps), SF top-k: KL(q||p_SF), KL(p_SF||q), self-distortion (E_fact = 0 here)")
    prevf = math.inf
    monoT = True
    for k in (24, 12, 8, 6, 4, 3, 2, 1):
        sched = [k] * (Lr // k)
        logd = iid_sf_count_law(p, Lr, sched)
        fwd, rev = iid_count_kls(p, Lr, logd)
        m, selfd = Lr, 0.0
        for kk in sched:
            selfd += iid_random_D(p, m, kk) if kk <= 4 else float("nan")
            m -= kk
        print(f"    k={k:2d} T={Lr // k:2d}  {fwd:9.5f}  {rev:9.5f}  {selfd:9.5f}")
        if k < 24:
            monoT &= fwd > prevf - 1e-12
        prevf = fwd
    check("T3.10c iid data (E_fact = 0): SF forward KL increases as k falls (more steps, more selection rounds)", monoT)

    # The [V] toy of primer-samplers-check.py, section C, reproduced and decomposed
    q0 = np.random.default_rng(0).dirichlet(np.ones(81) * 0.35).reshape((3,) * 4)
    D0 = Data(q0)
    pe = make_pred(D0, 0.0)
    sf = k_sf(pe, 1, 3)
    law_sf = out_law(sf, 4)
    qd0 = {x: float(q0[x]) for x in itertools.product(range(3), repeat=4)}
    kl_toy = kld(qd0, law_sf)
    f0, l0, s0 = budget(D0, pe, sf, 3)
    PP = paths_P(sf, 4)
    QQ = paths_Q(D0, lambda z: pos_law(sf(z)), 4, 3)
    klpath = kld(QQ, PP)
    blocked = sum(a for path, a in QQ.items() if PP.get(path, 0.0) == 0)
    mrs = k_matched(sf, pe, 3)
    law_m = out_law(mrs, 4)
    selfd = self_distortion(sf, pe, 4)
    klpp = kld(PP, paths_P(mrs, 4))
    print(f"  toy (primer-samplers-check C): KL(q||p_SF)={kl_toy:.6f} H(p_SF)={ent(list(law_sf.values())):.6f} H(q)={ent(q0):.6f}")
    print(f"    forward path KL(Q||P_SF) = {klpath}; E_fact {f0:.2e}, E_learn {l0:.2e}, E_sel_path {s0}; Q-mass of data paths SF never takes = {blocked:.4f}")
    print(f"    matched RS: KL(q||p_mRS)={kld(qd0, law_m):.2e} (exact marginals, k=1 => p_mRS = q), so E_sel^Delta = KL(q||p_SF) = {kl_toy:.6f}")
    print(f"    reverse: self-distortion sum E_P[D] = {selfd:.6f} = KL(P_SF||P_mRS) on paths {klpp:.6f} >= KL(p_SF||q) = {kld(law_sf, qd0):.6f}; bound log 4! = {math.log(24):.4f}")
    check("T3.11 toy reproduced: KL(q||p_SF) = 1.288", abs(kl_toy - 1.288) < 5e-4, f"{kl_toy:.6f}")
    check("T3.12 toy: forward per-step (path) E_sel is infinite (SF never commits some data (position, value) pairs)",
          math.isinf(klpath) and math.isinf(s0) and blocked > 0)
    check("T3.13 toy: output-level E_sel^Delta = KL(q||p_SF) - KL(q||p_mRS) is finite", math.isfinite(kl_toy))
    check("T3.14 toy: self-distortion = path KL(P_SF||P_mRS) >= KL(p_SF||q)", abs(selfd - klpp) < 1e-10 and kld(law_sf, qd0) <= selfd + 1e-12)

    # ------------------------------------------------------------------ T1 path identity, all kernels, exact and perturbed
    section("T1  path identity KL(Q_rho||P_kappa) = E_fact + E_learn + E_sel for every kernel; output KL = path KL - G")
    worst = 0.0
    negsel = 0
    gmin = 0.0
    inf_sf = n_sf = 0
    consistent = True
    out_finite = True
    neg_delta = 0
    for seed in range(4):
        L, V = (4, 3) if seed < 2 else (3, 3)
        qq = np.random.default_rng(100 + seed).dirichlet(np.ones(V ** L) * 0.4).reshape((V,) * L)
        Dd = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(V), repeat=L)}
        for noise in (0.0, 0.5):
            p = make_pred(Dd, noise, seed=7 + seed)
            kers = {
                "SF k=1": k_sf(p, 1, V),
                "SF k=2": k_sf(p, 2, V),
                "SF k=1 tau=0.7": k_sf(p, 1, V, tau=0.7),
                "SF k=1 margin score": k_sf(p, 1, V, score="margin"),
                "RS conf k=2": k_rs(p, rho_conf(p, 2), V),
                "RS conf k=2 tau=0.5": k_rs(p, rho_conf(p, 2), V, transform=lambda m: (m ** 2) / (m ** 2).sum()),
                "joint draw k=2": k_joint(Dd, rho_conf(p, 2), V),
                "RS uniform k=2": k_rs(p, rho_uniform(2), V),
            }
            for name, ker in kers.items():
                PP = paths_P(ker, L)
                QQ = paths_Q(Dd, lambda z, ker=ker: pos_law(ker(z)), L, V)
                klp = kld(QQ, PP)
                fa, le, se = budget(Dd, p, ker, V)
                klo = kld(qd, marg_x(PP, L))
                if name.startswith("SF"):
                    n_sf += 1
                    inf_sf += math.isinf(klp)
                    out_finite &= math.isfinite(klo)
                    klm = kld(qd, out_law(k_matched(ker, p, V), L))
                    neg_delta += (klo - klm) < -1e-9
                    print(f"    L={L} seed={seed} noise={noise} {name:22s} KL_out={klo:.5f} KL_out(mRS)={klm:.5f} E_sel^Delta={klo - klm:+.5f} path={klp:.5f} sel_path={se:+.5f}")
                else:
                    print(f"    L={L} seed={seed} noise={noise} {name:22s} KL_out={klo:.5f} path={klp:.5f} fact={fa:.5f} learn={le:.5f} sel={se:+.5f} G={klp - klo:.5f}")
                if math.isinf(klp) or math.isinf(se):
                    consistent &= math.isinf(klp) and math.isinf(se)
                    continue
                worst = max(worst, abs(klp - fa - le - se))
                gmin = min(gmin, klp - klo)
                if se < -1e-9:
                    negsel += 1
    check("T1.1 path identity holds for every kernel where finite (RS, tempered RS, joint draw, random RS)", worst < 1e-10, f"max gap {worst:.1e}")
    check("T1.1b where the path KL is infinite, E_sel_path is infinite too (identity holds as inf = inf)", consistent)
    check("T1.2 G = path KL - output KL >= 0 in every finite case", gmin > -1e-10)
    check("T1.3 E_sel is signed (joint draws give E_sel = -(E_fact + E_learn) < 0)", negsel > 0, f"{negsel} negative cases")
    check("T1.3b SF kernels: forward path E_sel infinite in some cases", inf_sf > 0, f"{inf_sf} of {n_sf}")
    check("T1.3c SF output law KL(q||p_SF) finite in every case (support lemma)", out_finite)
    print(f"    output-level E_sel^Delta = KL(q||p_SF) - KL(q||p_mRS) negative in {neg_delta} of {n_sf} SF cases")

    # deterministic RS has G = 0 ; randomised position law has G > 0
    qq = np.random.default_rng(5).dirichlet(np.ones(81) * 0.4).reshape((3,) * 4)
    Dd = Data(qq)
    qd = {x: float(qq[x]) for x in itertools.product(range(3), repeat=4)}
    p = make_pred(Dd, 0.4, seed=3)
    ker = k_rs(p, rho_conf(p, 2), 3)
    PP = paths_P(ker, 4)
    QQ = paths_Q(Dd, lambda z: pos_law(ker(z)), 4, 3)
    check("T1.4 deterministic state-only policy: G = 0 (identity exact for x)", abs(kld(QQ, PP) - kld(qd, marg_x(PP, 4))) < 1e-12)
    ker = k_matched(k_sf(p, 1, 3), p, 3)
    PP = paths_P(ker, 4)
    QQ = paths_Q(Dd, lambda z: pos_law(ker(z)), 4, 3)
    check("T1.5 matched RS of SF (randomised position law): identity is a strict upper bound, G > 0",
          kld(QQ, PP) - kld(qd, marg_x(PP, 4)) > 1e-6)

    # exact marginals, k = 1: p_mRS = q, so E_sel^Delta = KL(q||p_SF) >= 0, and the reverse is bounded by self-distortion
    viol = 0
    for seed in range(6):
        qq = np.random.default_rng(300 + seed).dirichlet(np.ones(81) * rng.choice([0.2, 0.5, 1.0])).reshape((3,) * 4)
        Dd = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(3), repeat=4)}
        p = make_pred(Dd, 0.0)
        ker = k_sf(p, 1, 3)
        lsf = out_law(ker, 4)
        lm = out_law(k_matched(ker, p, 3), 4)
        klo, klm = kld(qd, lsf), kld(qd, lm)
        rev, sd = kld(lsf, qd), self_distortion(ker, p, 4)
        if not (klm < 1e-12 and math.isfinite(klo) and klo > 0 and rev <= sd + 1e-12):
            viol += 1
    check("T1.6 exact marginals, k=1: KL(q||p_mRS)=0, 0 < KL(q||p_SF) < inf, KL(p_SF||q) <= self-distortion (6 random q)", viol == 0)

    # support lemma bound: p_SF(x) >= prod_n prod_{j in M_n} p_j(x^j | z_n) along the own-score greedy order of x
    viol = 0
    for seed in range(6):
        qq = np.random.default_rng(700 + seed).dirichlet(np.ones(81) * 0.4).reshape((3,) * 4)
        Dd = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(3), repeat=4)}
        for noise in (0.0, 0.4):
            p = make_pred(Dd, noise, seed=seed)
            for k in (1, 2):
                lsf = out_law(k_sf(p, k, 3), 4)
                Bx = 0.0
                for x, qx in qd.items():
                    z = (-1,) * 4
                    lp = 0.0
                    while masked(z):
                        M = masked(z)
                        lp += sum(math.log(p(z, j)[x[j]]) for j in M)
                        A = tuple(sorted(sorted(M, key=lambda j: (-p(z, j)[x[j]], j))[:min(k, len(M))]))
                        z = reveal(z, A, tuple(x[a] for a in A))
                    viol += lsf[x] < math.exp(lp) * (1 - 1e-9)
                    Bx += qx * (math.log(qx) - lp)
                viol += kld(qd, lsf) > Bx + 1e-10
    check("T1.9 support lemma: p_SF(x) >= prod over greedy steps of all masked marginals; KL(q||p_SF) <= that cross-entropy bound", viol == 0)

    # E_sel^Delta can be negative: an over-dispersed model whose errors SF sharpening partly undoes
    qn = np.einsum("a,b,c->abc", *([np.array([0.9, 0.05, 0.05])] * 3))
    Dn = Data(qn)
    qdn = {x: float(qn[x]) for x in itertools.product(range(3), repeat=3)}
    flat = lambda z, i: np.array([0.5, 0.25, 0.25])
    ksn = k_sf(flat, 1, 3)
    d_neg = kld(qdn, out_law(ksn, 3)) - kld(qdn, out_law(k_matched(ksn, flat, 3), 3))
    check("T1.8 E_sel^Delta < 0 is possible (over-dispersed model, independent peaked data)", d_neg < -1e-6, f"E_sel^Delta = {d_neg:+.5f}")

    # dependent data and the number of steps: E_fact falls with T, the SF excess rises with T
    Lm = 6
    flip = 0.1
    qmk = np.zeros((2,) * Lm)
    for x in itertools.product((0, 1), repeat=Lm):
        pr = 0.5
        for a, b in zip(x[:-1], x[1:]):
            pr *= flip if a != b else 1 - flip
        qmk[x] = pr
    Dmk = Data(qmk)
    qdm = {x: float(qmk[x]) for x in itertools.product((0, 1), repeat=Lm)}
    pm = make_pred(Dmk, 0.0)
    print(f"  Markov chain L={Lm}, flip {flip}, exact marginals: k, T, KL(q||p_RS-conf), KL(q||p_mRS), KL(q||p_SF), E_sel^Delta, H(p_SF), H(q)={ent(qmk):.4f}")
    rows_m = []
    for k in (6, 3, 2, 1):
        krs = k_rs(pm, rho_conf(pm, k), 2)
        ksf = k_sf(pm, k, 2)
        kmr = k_matched(ksf, pm, 2)
        a1 = kld(qdm, out_law(krs, Lm))
        lsf = out_law(ksf, Lm)
        a2, a3 = kld(qdm, out_law(kmr, Lm)), kld(qdm, lsf)
        rows_m.append((k, a1, a2, a3))
        print(f"    k={k} T={Lm // k}  {a1:.5f}  {a2:.5f}  {a3:.5f}  {a3 - a2:+.5f}  {ent(list(lsf.values())):.4f}")
    check("T3.15 Markov toy: RS error falls to 0 at k=1 while the SF excess over matched RS is largest at k=1",
          rows_m[-1][1] < 1e-12 and (rows_m[-1][3] - rows_m[-1][2]) > max(r[3] - r[2] for r in rows_m[:-1]))
    sf_kl = [r[3] for r in rows_m]
    check("T3.16 Markov toy: KL(q||p_SF) is U-shaped in the number of steps (interior minimum)",
          min(sf_kl) < sf_kl[0] and min(sf_kl) < sf_kl[-1], "T = 1, 2, 3, 6: " + ", ".join(f"{v:.4f}" for v in sf_kl))

    # matched RS: same position law, values from p; kernel-level KL projection
    qq = np.random.default_rng(11).dirichlet(np.ones(81) * 0.4).reshape((3,) * 4)
    Dd = Data(qq)
    p = make_pred(Dd, 0.3, seed=1)
    ker = k_sf(p, 2, 3)
    z0 = (-1,) * 4
    kd = ker(z0)
    rho = pos_law(kd)
    base = step_distortion(kd, p, z0)
    worse = 0
    for t in range(200):
        alt = {A: r * math.exp(rng.normal(0, 0.5)) for A, r in rho.items()}
        s = sum(alt.values())
        alt = {A: r / s for A, r in alt.items()}
        val = sum(a * math.log(a / (alt[A] * math.prod(p(z0, i)[v] for i, v in zip(A, y)))) for (A, y), a in kd.items())
        if val < base - 1e-12:
            worse += 1
    check("T1.7 matched RS is the KL(kappa||.) projection of SF onto rank-then-sample kernels (200 perturbed position laws)", worse == 0)

    # ------------------------------------------------------------------ T4 entropy
    section("T4  entropy")
    # (a) per state, k = 1: H(kappa(.|z)) <= H(mRS(.|z)); k = 2: search
    viol1 = viol2 = 0
    ex2 = None
    for trial in range(3000):
        n = int(rng.integers(2, 5))
        V = int(rng.integers(2, 5))
        laws = [rng.dirichlet(np.ones(V) * rng.choice([0.1, 0.3, 1.0, 5.0])) for _ in range(n)]
        for k in (1, 2):
            if k > n:
                continue
            kd = sf_closed(laws, laws, k)
            rho = pos_law(kd)
            hs = ent(list(kd.values()))
            hr = ent(list(rho.values())) + sum(r * sum(ent(laws[i]) for i in A) for A, r in rho.items())
            if hs > hr + 1e-12:
                if k == 1:
                    viol1 += 1
                else:
                    viol2 += 1
                    if ex2 is None:
                        ex2 = (laws, hs, hr)
    check("T4.1 k=1, per state: H(SF step) <= H(matched RS step) (3000 states)", viol1 == 0, f"violations {viol1}")
    print(f"  k=2 per-state violations of H(SF step) <= H(mRS step): {viol2} of up to 3000")
    if ex2 is not None:
        print("    first k=2 counterexample: marginals", [np.round(l, 4).tolist() for l in ex2[0]], f"H_SF={ex2[1]:.6f} H_mRS={ex2[2]:.6f}")

    # (a) output level: constructed counterexample (SF sharpening steers into high-entropy futures)
    V = 3
    qc = np.zeros((3, 3, 3, 3))
    pa = 0.7
    for x1 in (0, 1):
        for x2 in range(3):
            for x3 in range(3):
                for x4 in range(3):
                    if x1 == 0:
                        pr = pa * (1 / 3) * (1 / 9)
                    else:
                        pr = (1 - pa) * (1 / 3) * (1.0 if (x3 == 0 and x4 == 0) else 0.0)
                    qc[x1, x2, x3, x4] = pr
    Dc = Data(qc)
    pc = make_pred(Dc, 0.0)
    sfc = k_sf(pc, 1, 3)
    mc = k_matched(sfc, pc, 3)
    hs, hm = ent(list(out_law(sfc, 4).values())), ent(list(out_law(mc, 4).values()))
    print(f"  constructed q (x1 in {{0,1}} w.p. 0.7/0.3; x2 uniform; x3,x4 uniform iff x1=0, else 0): H(p_SF)={hs:.5f}  H(p_mRS)={hm:.5f}  H(q)={ent(qc):.5f}")
    check("T4.2 output entropy under SF can exceed that of matched RS (counterexample)", hs > hm + 1e-9)
    cnt = tot = 0
    for seed in range(40):
        qq = np.random.default_rng(500 + seed).dirichlet(np.ones(81) * [0.1, 0.3, 1.0][seed % 3]).reshape((3,) * 4)
        Dd = Data(qq)
        p = make_pred(Dd, 0.0 if seed % 2 == 0 else 0.4, seed=seed)
        s = k_sf(p, 1, 3)
        m = k_matched(s, p, 3)
        tot += 1
        cnt += ent(list(out_law(s, 4).values())) < ent(list(out_law(m, 4).values()))
    print(f"  random q (40 cases, exact or perturbed predictor): H(p_SF) < H(p_mRS) in {cnt} of {tot}")

    # (b) multi-step state-only sampler with exact marginals: H(p) >= H(q)? Counterexample.
    eps = 0.1
    qb = np.zeros((4, 4, 4, 4))
    for x1 in (0, 1):
        for x2 in (0, 1):
            pr12 = (1 - eps) / 2 if x1 == x2 else eps / 2
            for x3 in range(4):
                for x4 in range(4):
                    if x1 == x2:
                        qb[x1, x2, x3, x4] = pr12 / 16
                    elif x3 == 0 and x4 == 0:
                        qb[x1, x2, x3, x4] = pr12
    Db = Data(qb)
    pb = make_pred(Db, 0.0)
    kb = k_rs(pb, rho_fixed([(0, 1), (2, 3)]), 4)
    lb = out_law(kb, 4)
    qdb = {x: float(qb[x]) for x in itertools.product(range(4), repeat=4) if qb[x] > 0}
    Hp, Hq = ent(list(lb.values())), ent(qb)
    fb, lrn, _ = budget(Db, pb, kb, 4)
    print(f"  T4(b) construction: eps={eps}, steps {{x1,x2}} then {{x3,x4}}, exact marginals, sampled values")
    print(f"    H(p)={Hp:.5f}  H(q)={Hq:.5f}  closed forms: 2ln2 + ln16/2 = {2 * math.log(2) + math.log(16) / 2:.5f};"
          f" ln2 + h(eps) + (1-eps) ln16 = {math.log(2) - eps * math.log(eps) - (1 - eps) * math.log(1 - eps) + (1 - eps) * math.log(16):.5f}")
    print(f"    KL(q||p)={kld(qdb, lb):.5f} = E_fact {fb:.5f} (= ln2 - h(eps) = {math.log(2) + eps * math.log(eps) + (1 - eps) * math.log(1 - eps):.5f}), E_learn {lrn:.1e}")
    check("T4.3 exact marginals, sampled values, deterministic state-only policy: H(p) < H(q) is possible", Hp < Hq - 0.5)
    cnt = 0
    for seed in range(300):
        qq = np.random.default_rng(900 + seed).dirichlet(np.ones(81) * [0.05, 0.2, 1.0][seed % 3]).reshape((3,) * 4)
        Dd = Data(qq)
        p = make_pred(Dd, 0.0)
        perm = np.random.default_rng(seed).permutation(4)
        kr = k_rs(p, rho_fixed([tuple(perm[:2]), tuple(perm[2:])]), 3)
        cnt += ent(list(out_law(kr, 4).values())) < ent(qq) - 1e-12
    print(f"    random q (300, Dirichlet 0.05/0.2/1.0), fixed 2+2 partition, exact marginals: H(p) < H(q) in {cnt} cases")
    # one-shot product: always >= H(q)
    viol = 0
    for seed in range(300):
        qq = np.random.default_rng(1300 + seed).dirichlet(np.ones(81) * 0.3).reshape((3,) * 4)
        hp = sum(ent(qq.sum(axis=tuple(a for a in range(4) if a != i))) for i in range(4))
        viol += hp < ent(qq) - 1e-12
    check("T4.4 one-shot product of exact marginals: entropy >= H(q) (300 cases)", viol == 0)

    # ------------------------------------------------------------------ T5 estimators
    section("T5  estimators from logits (and data)")
    # (i) forward, data-side per-step estimator log rho(i) - log Pi_i(p_i(x^i)): infinite with positive probability
    qq = np.random.default_rng(21).dirichlet(np.ones(81) * 0.4).reshape((3,) * 4)
    Dd = Data(qq)
    for noise in (0.0, 0.4):
        p = make_pred(Dd, noise, seed=2)
        ker = k_sf(p, 1, 3)
        pinf = [0.0]

        def Pi_of(z, i, v):
            M = masked(z)
            laws = [p(z, j) for j in M]
            j0 = M.index(i)
            c = laws[j0][v]
            Pi = 1.0
            for jj, lj in enumerate(laws):
                if jj != j0:
                    Pi *= lj[lj < c].sum() + (lj[lj == c].sum() if jj > j0 else 0.0)
            return Pi

        def rec(z, w, hit):
            if not masked(z):
                pinf[0] += w * hit
                return
            for A, ra in pos_law(ker(z)).items():
                i = A[0]
                jq = Dd.marg(z, i)
                for v in range(3):
                    if jq[v] > 0:
                        rec(reveal(z, A, (v,)), w * ra * jq[v], hit or Pi_of(z, i, v) == 0.0)
        rec((-1,) * 4, 1.0, False)
        print(f"    noise={noise}: probability that a data path meets a (position, value) pair SF can never commit = {pinf[0]:.4f}")
        check(f"T5.1 noise={noise}: the forward data-side per-step estimator is infinite with positive probability", pinf[0] > 0)

    # (ii) reverse, model-only self-distortion along the sampler's own trajectories: MC = exact; D(z) from the closed form
    p = make_pred(Dd, 0.4, seed=2)
    ker = k_sf(p, 1, 3)
    exact = self_distortion(ker, p, 4)
    r2 = np.random.default_rng(78)
    vals = []
    dmatch = 0.0
    for s in range(20000):
        z = (-1,) * 4
        tot = 0.0
        while masked(z):
            kd = ker(z)
            M = masked(z)
            cf = sf_closed([p(z, i) for i in M], [p(z, i) for i in M], 1)
            cfd = {(tuple(M[a] for a in A), y): v for (A, y), v in cf.items()}
            rho = pos_law(cfd)
            dz = sum(a * math.log(a / (rho[A] * math.prod(p(z, i)[v] for i, v in zip(A, y)))) for (A, y), a in cfd.items())
            dmatch = max(dmatch, abs(dz - step_distortion(kd, p, z)))
            tot += dz
            keys = list(kd)
            (A, y) = keys[r2.choice(len(keys), p=np.array([kd[kk] for kk in keys]) / sum(kd.values()))]
            z = reveal(z, A, y)
        vals.append(tot)
    vals = np.array(vals)
    mc, se_mc = vals.mean(), vals.std() / math.sqrt(len(vals))
    print(f"    SF k=1, perturbed predictor: exact sum_n E_P[D] = {exact:.6f}; MC over 20000 sampler paths = {mc:.5f} +- {se_mc:.5f}; per-path sd {vals.std():.4f}, max {vals.max():.4f}")
    check("T5.2 self-distortion: closed-form per-state D equals the enumerated kernel's D", dmatch < 1e-12, f"max diff {dmatch:.1e}")
    check("T5.3 self-distortion: Monte Carlo along sampler paths is within 3 SE of the exact value", abs(mc - exact) < 3 * se_mc + 1e-12)

    # (iii) top-K truncation bracket for F_j(c) = P_j(score < c)
    bad = 0
    for t in range(2000):
        Vv = int(rng.integers(3, 12))
        pj = rng.dirichlet(np.ones(Vv) * rng.choice([0.2, 1.0]))
        K = int(rng.integers(1, Vv))
        c = float(rng.uniform(0, pj.max() * 1.1))
        srt = np.sort(pj)[::-1]
        top, eps_tail = srt[:K], srt[K:].sum()
        ge_top = top[top >= c].sum()
        lo = 1 - ge_top - (eps_tail if c <= srt[K - 1] else 0.0)
        hi = 1 - ge_top
        true = pj[pj < c].sum()
        bad += not (lo - 1e-12 <= true <= hi + 1e-12)
    check("T5.4 top-K truncation brackets F_j(c) within the tail mass (2000 random cases)", bad == 0)

    # argmax: self-distortion equals -log p_mRS(x*) along a deterministic policy (equality case)
    p = make_pred(Dd, 0.4, seed=2)
    amax = lambda m: (m == m.max()).astype(float) / (m == m.max()).sum()
    karg = k_rs(p, rho_conf(p, 1), 3, transform=amax)
    lawa = out_law(karg, 4)
    xs_ = [x for x, a in lawa.items() if a > 0]
    kref = k_rs(p, rho_conf(p, 1), 3)
    lref = out_law(kref, 4)
    sd = self_distortion(lambda z: {key: v for key, v in karg(z).items()}, p, 4)
    check("T5.5 argmax with a deterministic position rule: self-distortion = -log p_RS(x*) = KL(delta_x*||p_RS)",
          len(xs_) == 1 and abs(sd + math.log(lref[xs_[0]])) < 1e-10, f"{sd:.6f} vs {-math.log(lref[xs_[0]]):.6f}")
    qd = {x: float(qq[x]) for x in itertools.product(range(3), repeat=4)}
    check("T5.6 argmax: forward KL(q||p_argmax) = infinity (E_tilt infinite in the forward direction)", math.isinf(kld(qd, lawa)))

    # temperature: state-only transform, identity exact with p_tilde; E_sel = E_tilt = cross-entropy difference on data
    tau = 0.7
    tr = lambda m: (m ** (1 / tau)) / (m ** (1 / tau)).sum()
    kt = k_rs(p, rho_conf(p, 2), 3, transform=tr)
    ptil = lambda z, i: tr(p(z, i))
    f1, l1_, s1 = budget(Dd, p, kt, 3)
    f2, l2_, s2 = budget(Dd, ptil, kt, 3)
    check("T5.7 temperature is a state-only tilt: E_learn[p] + E_sel = E_learn[p_tilde] and E_sel(p_tilde ref) = 0",
          abs(l1_ + s1 - l2_) < 1e-10 and abs(s2) < 1e-10, f"E_tilt = {s1:+.5f}")

    # ------------------------------------------------------------------ T6 cross-modal
    section("T6  cross-modal term: X = I(a;b|s), set-to-token S = sum_j I(a;b_j|s), pairwise P = sum_ij I(a_i;b_j|s)")

    def Hsub(qq, S):
        S = tuple(sorted(S))
        if not S:
            return 0.0
        return ent(qq.sum(axis=tuple(a for a in range(qq.ndim) if a not in S)))

    def Hc(qq, S, R):
        return Hsub(qq, set(S) | set(R)) - Hsub(qq, R)

    def MI(qq, S1, S2, R):
        return Hc(qq, S1, R) + Hc(qq, S2, R) - Hc(qq, tuple(S1) + tuple(S2), R)

    def TC(qq, S, R):
        return sum(Hc(qq, (i,), R) for i in S) - Hc(qq, S, R)

    def TCcond(qq, S, R, C):  # TC(S | R, C) = sum H(i | R,C) - H(S | R,C)
        RC = tuple(R) + tuple(C)
        return TC(qq, S, RC)

    a_, b_ = (0, 1), (2, 3)
    signs = {"X>S": 0, "X<S": 0, "S>P": 0, "S<P": 0}
    worst = 0.0
    for t in range(500):
        qq = rng.dirichlet(np.ones(81) * rng.choice([0.05, 0.3, 1.0])).reshape((3,) * 4)
        X = MI(qq, a_, b_, ())
        S = sum(MI(qq, a_, (j,), ()) for j in b_)
        P = sum(MI(qq, (i,), (j,), ()) for i in a_ for j in b_)
        tcab = TC(qq, a_ + b_, ())
        worst = max(worst, abs(tcab - (TC(qq, a_, ()) + S + TCcond(qq, b_, (), a_))),
                    abs(tcab - (TC(qq, a_, ()) + TC(qq, b_, ()) + X)))
        signs["X>S" if X > S else "X<S"] += 1
        signs["S>P" if S > P else "S<P"] += 1
    check("T6.1 two exact splits: TC(A) = TC(a)+TC(b)+X = TC(a)+S+TC(b|a) (500 random q)", worst < 1e-12, f"max err {worst:.1e}")
    print(f"    sign counts over 500 random q: {signs}  (X - S and S - P take both signs)")
    check("T6.2 X - S and S - P are not sign-definite in general", min(signs.values()) > 0)

    viol = 0
    for t in range(300):  # image tokens conditionally independent given text: X <= S
        qa = rng.dirichlet(np.ones(9) * rng.choice([0.1, 0.5, 2.0])).reshape(3, 3)
        b1 = rng.dirichlet(np.ones(3) * 0.5, size=(3, 3))
        b2 = rng.dirichlet(np.ones(3) * 0.5, size=(3, 3))
        qq = qa[:, :, None, None] * b1[:, :, :, None] * b2[:, :, None, :]
        X = MI(qq, a_, b_, ())
        S = sum(MI(qq, a_, (j,), ()) for j in b_)
        viol += X > S + 1e-12
    check("T6.3 image tokens conditionally independent given text => X <= S", viol == 0)
    viol = 0
    for t in range(300):  # text tokens mutually independent: P <= S
        a1 = rng.dirichlet(np.ones(3) * 0.7)
        a2 = rng.dirichlet(np.ones(3) * 0.7)
        bq = rng.dirichlet(np.ones(9) * 0.3, size=(3, 3)).reshape(3, 3, 3, 3)
        qq = a1[:, None, None, None] * a2[None, :, None, None] * bq
        S = sum(MI(qq, a_, (j,), ()) for j in b_)
        P = sum(MI(qq, (i,), (j,), ()) for i in a_ for j in b_)
        viol += P > S + 1e-12
    check("T6.4 text tokens mutually independent given the state => P <= S", viol == 0)

    # reveal-and-requery estimator: E_{a ~ joint} sum_j KL(p(b_j|s,a)||p(b_j|s)) = S under an exact model;
    # with a drawn from the product of marginals (what a one-pass sampler has) it is biased
    qq = rng.dirichlet(np.ones(243) * 0.3).reshape((3,) * 5)   # axis 0: revealed context c
    Dd = Data(qq)
    z = (int(np.argmax(qq.sum(axis=(1, 2, 3, 4)))), -1, -1, -1, -1)
    ja = Dd.joint(z, (1, 2))
    ma = [Dd.marg(z, 1), Dd.marg(z, 2)]
    mb = [Dd.marg(z, 3), Dd.marg(z, 4)]

    def requery(weights):
        tot = 0.0
        for a1 in range(3):
            for a2 in range(3):
                w = weights[a1, a2]
                if w == 0:
                    continue
                z2 = (z[0], a1, a2, -1, -1)
                if Dd.prob_state(z2) == 0:
                    continue
                tot += w * sum(klv(Dd.marg(z2, j), mb[jj]) for jj, j in enumerate((3, 4)))
        return tot
    qs = qq[z[0]] / qq[z[0]].sum()          # condition on the context value: axes text1, text2, img1, img2
    S_true = sum(MI(qs, (0, 1), (j,), ()) for j in (2, 3))
    X_true = MI(qs, (0, 1), (2, 3), ())
    est_joint = requery(ja)
    est_prod = requery(np.outer(ma[0], ma[1]))
    tca = klv(ja, np.outer(ma[0], ma[1]))
    print(f"    state with context revealed: X={X_true:.5f}  S={S_true:.5f}  requery(a~joint)={est_joint:.5f}  requery(a~product)={est_prod:.5f}  TC(a|s)={tca:.5f}")
    check("T6.5 exact model, a drawn from the joint (sequential reveal): requery estimator = S", abs(est_joint - S_true) < 1e-12)

    # ------------------------------------------------------------------ T7 memory
    section("T7  memory: identity on the augmented path; equality for x")

    def run_memory(qq, pred, rho, mu, m0, L, V):
        """augmented sampler: state (z, m). pred(z, m, i) -> marginal; rho(z, m) -> {A: prob};
        mu(z, m, A, y) -> {m_new: prob} (fresh noise, same mechanism under data and sampler)."""
        Dd = Data(qq)
        PPd: dict = {}
        QQd: dict = {}
        acc = {"fact": 0.0, "learn": 0.0}

        def recP(z, m, path, w):
            if not masked(z):
                PPd[path] = PPd.get(path, 0.0) + w
                return
            for A, ra in rho(z, m).items():
                for y in itertools.product(range(V), repeat=len(A)):
                    pv = ra * math.prod(pred(z, m, i)[v] for i, v in zip(A, y))
                    if pv == 0:
                        continue
                    z2 = reveal(z, A, y)
                    for m2, pm in mu(z, m, A, y).items():
                        recP(z2, m2, path + ((A, y, m2),), w * pv * pm)

        def recQ(z, m, path, w):
            if not masked(z):
                QQd[path] = QQd.get(path, 0.0) + w
                return
            for A, ra in rho(z, m).items():
                jq = Dd.joint(z, A)
                margs = [Dd.marg(z, i) for i in A]
                acc["fact"] += w * ra * klv(jq, prod_array(margs))
                acc["learn"] += w * ra * sum(klv(margs[j], pred(z, m, A[j])) for j in range(len(A)))
                for y in itertools.product(range(V), repeat=len(A)):
                    if jq[y] == 0:
                        continue
                    z2 = reveal(z, A, y)
                    for m2, pm in mu(z, m, A, y).items():
                        recQ(z2, m2, path + ((A, y, m2),), w * ra * float(jq[y]) * pm)
        recP((-1,) * L, m0, (), 1.0)
        recQ((-1,) * L, m0, (), 1.0)
        klpath = kld(QQd, PPd)

        def xm(d):
            out: dict = {}
            for path, a in d.items():
                zz = [-1] * L
                for A, y, _ in path:
                    for i, v in zip(A, y):
                        zz[i] = v
                out[tuple(zz)] = out.get(tuple(zz), 0.0) + a
            return out
        klx = kld(xm(QQd), xm(PPd))
        return klpath, acc["fact"] + acc["learn"], klx

    L, V = 3, 3
    qm = np.random.default_rng(42).dirichlet(np.ones(27) * 0.5).reshape((3,) * 3)
    Dm = Data(qm)
    base = make_pred(Dm, 0.3, seed=9)

    def tilt(m_, bit, strength=0.8):
        w = m_ * np.exp(strength * (np.arange(len(m_)) == bit))
        return w / w.sum()
    conf1 = lambda z, m: {(sorted(masked(z), key=lambda i: (-base(z, i).max(), i))[0],): 1.0}
    unif1 = lambda z, m: {(i,): 1.0 / len(masked(z)) for i in masked(z)}
    cases = {
        "(a1) deterministic rho, memory = last committed value (function of revealed path)":
            (lambda z, m, i: tilt(base(z, i), m), conf1, lambda z, m, A, y: {y[0]: 1.0}),
        "(a2) random rho, memory = first committed position (path, not z)":
            (lambda z, m, i: tilt(base(z, i), m), unif1, lambda z, m, A, y: {(A[0] if m == -1 else m): 1.0}),
        "(b) deterministic rho, fresh random memory bit used by predictor":
            (lambda z, m, i: tilt(base(z, i), m), conf1, lambda z, m, A, y: {0: 0.5, 1: 0.5}),
        "(c) deterministic rho, fresh random memory bit ignored by predictor and policy":
            (lambda z, m, i: base(z, i), conf1, lambda z, m, A, y: {0: 0.5, 1: 0.5}),
    }
    res = {}
    for name, (pred, rho, mu) in cases.items():
        klpath, rhs, klx = run_memory(qm, pred, rho, mu, -1, L, V)
        res[name[:4]] = (klpath, rhs, klx)
        print(f"    {name}: path KL {klpath:.6f}  E_fact+E_learn {rhs:.6f}  KL(q||p) on x {klx:.6f}  gap {klpath - klx:.2e}")
    check("T7.1 augmented-path identity is an equality in all four memory cases",
          all(abs(v[0] - v[1]) < 1e-10 for v in res.values()))
    check("T7.2 (a1) memory a function of the revealed path, deterministic rho: equality for x", abs(res["(a1)"][0] - res["(a1)"][2]) < 1e-10)
    check("T7.3 (a2) memory a function of the revealed path but rho random: strict inequality for x", res["(a2)"][0] - res["(a2)"][2] > 1e-6)
    check("T7.4 (b) stochastic memory used by the predictor: strict inequality for x", res["(b) "][0] - res["(b) "][2] > 1e-6)
    check("T7.5 (c) stochastic memory not used: equality for x (so 'only when' in framework-v1 2.1 is too strong)",
          abs(res["(c) "][0] - res["(c) "][2]) < 1e-10)

    # ------------------------------------------------------------------ summary
    section("SUMMARY")
    print(f"  checks run: {NCHECK[0]}; failures: {len(FAILS)}")
    for f in FAILS:
        print("   FAILED:", f)
    print("  ALL CHECKS PASSED" if not FAILS else "  SOME CHECKS FAILED")


if __name__ == "__main__":
    main()
