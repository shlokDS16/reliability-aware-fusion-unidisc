"""Toy prior for EXP-002: decompose sample-then-filter (SF) at k tokens per step into per-position
sharpening and joint coupling, by exact enumeration.

Arms, all from the same marginals p^i(. | s) at every state:
  A1 SF        sample every masked position, keep top-k by own probability p^i(y^i), commit them
  A2 resample  SF's position law, values redrawn independently from p^i
  A3 tilted    SF's position law, values independent per position from SF's per-position value law
  A4 RS-conf   top-k positions by max_v p^i, values sampled from p^i
At k = 1, A1 and A3 have the same law (red-team F1); at k >= 2 A1 - A3 is the coupling term.
Predictor = exact conditionals of q (E_learn = 0), so differences are value-rule and E_fact effects.
Ties: lower position index wins. Natural logs. Prints KL(q||p_arm) and H(p_arm).
"""
import itertools
import numpy as np

L, V = 4, 3
X = list(itertools.product(range(V), repeat=L))


def marginals(q, z):
    """exact conditional marginals at state z (tuple with None for masked)."""
    w = np.array([q[i] if all(z[j] is None or z[j] == x[j] for j in range(L)) else 0.0
                  for i, x in enumerate(X)])
    w = w / w.sum()
    out = {}
    for j in range(L):
        if z[j] is None:
            m = np.zeros(V)
            for i, x in enumerate(X):
                m[x[j]] += w[i]
            out[j] = m
    return out


def sf_kernel(p, k):
    """exact SF commit kernel: dict (A tuple, values tuple) -> prob."""
    M = sorted(p)
    ker = {}
    for y in itertools.product(range(V), repeat=len(M)):
        pr = np.prod([p[j][y[t]] for t, j in enumerate(M)])
        if pr == 0:
            continue
        order = sorted(range(len(M)), key=lambda t: (-p[M[t]][y[t]], M[t]))
        sel = sorted(order[:k])
        A = tuple(M[t] for t in sel)
        vals = tuple(y[t] for t in sel)
        ker[(A, vals)] = ker.get((A, vals), 0.0) + pr
    return ker


def kernel(arm, p, k):
    M = sorted(p)
    if arm == "A4":
        order = sorted(M, key=lambda j: (-p[j].max(), j))
        A = tuple(sorted(order[:k]))
        return {(A, v): np.prod([p[j][v[t]] for t, j in enumerate(A)])
                for v in itertools.product(range(V), repeat=len(A))}
    sf = sf_kernel(p, k)
    if arm == "A1":
        return sf
    rho = {}
    for (A, v), pr in sf.items():
        rho[A] = rho.get(A, 0.0) + pr
    ker = {}
    for A, ra in rho.items():
        if arm == "A2":
            laws = [p[j] for j in A]
        else:  # A3: per-position conditional value law of SF given A
            laws = []
            for t, j in enumerate(A):
                m = np.zeros(V)
                for (B, v), pr in sf.items():
                    if B == A:
                        m[v[t]] += pr
                laws.append(m / m.sum())
        for v in itertools.product(range(V), repeat=len(A)):
            ker[(A, v)] = ra * np.prod([laws[t][v[t]] for t in range(len(A))])
    return ker


def output_law(q, arm, k):
    out = np.zeros(len(X))

    def rec(z, prob):
        if all(c is not None for c in z):
            out[X.index(tuple(z))] += prob
            return
        p = marginals(q, z)
        kk = min(k, len(p))
        for (A, v), pr in kernel(arm, p, kk).items():
            if pr <= 0:
                continue
            z2 = list(z)
            for t, j in enumerate(A):
                z2[j] = v[t]
            rec(tuple(z2), prob * pr)

    rec(tuple([None] * L), 1.0)
    return out


def kl(a, b):
    m = a > 0
    return float(np.sum(a[m] * (np.log(a[m]) - np.log(np.maximum(b[m], 1e-300)))))


def H(a):
    m = a > 0
    return float(-np.sum(a[m] * np.log(a[m])))


rng = np.random.default_rng(0)
rows = []
for seed in range(12):
    q = rng.dirichlet(np.ones(len(X)) * 0.3)
    for k in (1, 2):
        laws = {a: output_law(q, a, k) for a in ("A1", "A2", "A3", "A4")}
        r = {a: (kl(q, laws[a]), H(laws[a])) for a in laws}
        d13 = float(np.abs(laws["A1"] - laws["A3"]).max())
        rows.append((seed, k, r, d13, H(q)))
        print(f"seed {seed:2d} k={k} H(q)={H(q):.3f}  " + "  ".join(
            f"{a}: KL={r[a][0]:.3f} H={r[a][1]:.3f}" for a in r) + f"  max|A1-A3|={d13:.1e}")

k1 = [x for x in rows if x[1] == 1]
k2 = [x for x in rows if x[1] == 2]
print("\nk=1: max |p_A1 - p_A3| over seeds =", max(x[3] for x in k1), "(must be ~0, red-team F1)")
c = [x[2]["A1"][0] - x[2]["A3"][0] for x in k2]
s = [x[2]["A3"][0] - x[2]["A2"][0] for x in k2]
print(f"k=2: coupling KL(A1)-KL(A3): mean {np.mean(c):+.4f}, negative in {sum(v < 0 for v in c)}/{len(c)}")
print(f"k=2: sharpening KL(A3)-KL(A2): mean {np.mean(s):+.4f}, negative in {sum(v < 0 for v in s)}/{len(s)}")
ent_c = [x[2]["A1"][1] - x[2]["A3"][1] for x in k2]
print(f"k=2: entropy H(A1)-H(A3): mean {np.mean(ent_c):+.4f}, negative in {sum(v < 0 for v in ent_c)}/{len(ent_c)}")
