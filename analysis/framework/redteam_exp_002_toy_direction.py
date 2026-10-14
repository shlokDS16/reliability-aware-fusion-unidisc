"""Red-team check for EXP-002 v0.2 (no GPU): does the toy prior's sign for coupling transfer to the card's metric?

The toy (check_coupling_k2.py) scores arms by forward KL(q || p_arm). The card's endpoint is log GenPPL, a sample-side
cross-entropy E_{x ~ p_arm}[-log q_eval(x)] read at matched output entropy. With a perfect evaluator (q_eval = q) and
H(p_arm) held fixed, that equals H + KL(p_arm || q): the REVERSE divergence. This script recomputes the toy's
12 priors with a temperature on the marginals (score = tempered probability of the draw, as in the card's 5.1), finds
per arm the tau at which H(p_arm) equals H(q) (data-defined reference entropy, as the card's h*), and reports the
coupling contrast in both directions:  G_cp = metric(A3) - metric(A1)  (positive = SF better, the card's convention).
Same toy as the card's prior: L = 4, V = 3, Dirichlet(0.3) q, exact conditional marginals, k = 2. Natural logs.
"""
import itertools
import numpy as np

L, V = 4, 3
X = list(itertools.product(range(V), repeat=L))
XI = {x: i for i, x in enumerate(X)}


def marginals(q, z):
    w = np.array([q[i] if all(z[j] is None or z[j] == x[j] for j in range(L)) else 0.0 for i, x in enumerate(X)])
    w = w / w.sum()
    out = {}
    for j in range(L):
        if z[j] is None:
            m = np.zeros(V)
            for i, x in enumerate(X):
                m[x[j]] += w[i]
            out[j] = m
    return out


def temper(m, tau):
    a = m ** (1.0 / tau)
    return a / a.sum()


def sf_kernel(p, k):
    M = sorted(p)
    ker = {}
    for y in itertools.product(range(V), repeat=len(M)):
        pr = np.prod([p[j][y[t]] for t, j in enumerate(M)])
        if pr == 0:
            continue
        order = sorted(range(len(M)), key=lambda t: (-p[M[t]][y[t]], M[t]))
        sel = sorted(order[:k])
        A = tuple(M[t] for t in sel)
        ker[(A, tuple(y[t] for t in sel))] = ker.get((A, tuple(y[t] for t in sel)), 0.0) + pr
    return ker


def kernel(arm, p, k):
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
        else:
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


def output_law(q, arm, k, tau, cache):
    out = np.zeros(len(X))

    def rec(z, prob):
        if all(c is not None for c in z):
            out[XI[tuple(z)]] += prob
            return
        if z not in cache:
            cache[z] = marginals(q, z)
        p = {j: temper(m, tau) for j, m in cache[z].items()}
        for (A, v), pr in kernel(arm, p, min(k, len(p))).items():
            if pr <= 0:
                continue
            z2 = list(z)
            for t, j in enumerate(A):
                z2[j] = v[t]
            rec(tuple(z2), prob * pr)

    rec(tuple([None] * L), 1.0)
    return out


def H(a):
    m = a > 0
    return float(-np.sum(a[m] * np.log(a[m])))


def kl(a, b):
    m = a > 0
    return float(np.sum(a[m] * (np.log(a[m]) - np.log(np.maximum(b[m], 1e-300)))))


def match_tau(q, arm, k, target, cache):
    lo, hi = 0.3, 6.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if H(output_law(q, arm, k, mid, cache)) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


rng = np.random.default_rng(0)  # same seed and draws as check_coupling_k2.py
rows = []
for seed in range(12):
    q = rng.dirichlet(np.ones(len(X)) * 0.3)
    cache = {}
    hq = H(q)
    res = {}
    for arm in ("A1", "A2", "A3"):
        t = match_tau(q, arm, 2, hq, cache)
        p = output_law(q, arm, 2, t, cache)
        p1 = output_law(q, arm, 2, 1.0, cache)
        res[arm] = dict(tau=t, H=H(p), fwd=kl(q, p), rev=kl(p, q), fwd1=kl(q, p1), rev1=kl(p1, q), H1=H(p1))
    rows.append(res)
    print(f"seed {seed:2d} H(q)={hq:.3f} tau*: A1 {res['A1']['tau']:.3f} A2 {res['A2']['tau']:.3f} A3 {res['A3']['tau']:.3f} | "
          f"matched: fwdKL A1 {res['A1']['fwd']:.4f} A3 {res['A3']['fwd']:.4f}  revKL A1 {res['A1']['rev']:.4f} A3 {res['A3']['rev']:.4f}")


def summ(name, f):
    v = np.array([f(r) for r in rows])
    print(f"{name}: mean {v.mean():+.4f}, positive (SF better) in {int((v > 0).sum())}/12, range [{v.min():+.4f}, {v.max():+.4f}]")


print("\nG_cp = metric(A3) - metric(A1); positive = SF's coupling helps (card convention)")
summ("tau = 1,   forward KL(q||p)  [the card's prior]", lambda r: r["A3"]["fwd1"] - r["A1"]["fwd1"])
summ("tau = 1,   reverse KL(p||q)  [GenPPL direction]", lambda r: r["A3"]["rev1"] - r["A1"]["rev1"])
summ("matched H, forward KL(q||p)", lambda r: r["A3"]["fwd"] - r["A1"]["fwd"])
summ("matched H, reverse KL(p||q)  [the card's estimand with a perfect evaluator]", lambda r: r["A3"]["rev"] - r["A1"]["rev"])
summ("matched H, sharpening G_sh = rev(A2) - rev(A3)", lambda r: r["A2"]["rev"] - r["A3"]["rev"])
summ("matched H, |tau*(A1) - tau*(A3)|", lambda r: abs(r["A1"]["tau"] - r["A3"]["tau"]))
