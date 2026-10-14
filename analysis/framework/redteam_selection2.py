"""Red-team checks, part 2 (searches). Reuses check_selection.py and redteam_selection.py.

    python analysis/framework/redteam_selection2.py > analysis/framework/redteam_selection2.log
"""
from __future__ import annotations

import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_selection import (Data, make_pred, k_sf, k_rs, k_matched, pos_law, kld, ent, rho_conf,  # noqa: E402
                             rho_uniform, rho_fixed, budget, sf_closed, kl_cont)
from redteam_selection import out_law_dp, rho_expscore, hdr  # noqa: E402


def tempered_pred(D, beta, noise=0.0, seed=0):
    """model = exact conditional marginal raised to beta (beta < 1 over-dispersed, > 1 under-dispersed),
    optionally with the log-normal state-seeded tilt of check_selection.make_pred."""
    base = make_pred(D, noise, seed)
    cache = {}

    def p(z, i):
        key = (z, i)
        if key not in cache:
            m = base(z, i) ** beta
            cache[key] = m / m.sum()
        return cache[key]
    return p


def search_sign():
    hdr("S1. Can E_sel change sign with the RS reference? (mRS, RS-conf, RS-E(score), RS-unif)")
    rng = np.random.default_rng(11)
    flips = []
    neg_exact = []
    n = 0
    for t in range(240):
        L, V = (3, 3) if t % 2 else (4, 2)
        conc = [0.1, 0.4, 1.0][t % 3]
        qq = rng.dirichlet(np.ones(V ** L) * conc).reshape((V,) * L)
        D = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(V), repeat=L)}
        beta = [0.4, 0.7, 1.0, 1.5][(t // 3) % 4]
        noise = [0.0, 0.3][(t // 12) % 2]
        p = tempered_pred(D, beta, noise, seed=t)
        for k in (1, 2):
            sf = k_sf(p, k, V)
            kl_sf = kld(qd, out_law_dp(sf, L))
            refs = {"mRS": k_matched(sf, p, V), "RS-conf": k_rs(p, rho_conf(p, k), V),
                    "RS-E": k_rs(p, rho_expscore(p, k), V), "RS-unif": k_rs(p, rho_uniform(k), V)}
            es = {nm: kl_sf - kld(qd, out_law_dp(r, L)) for nm, r in refs.items()}
            n += 1
            if max(es.values()) > 1e-6 and min(es.values()) < -1e-6:
                flips.append((t, L, V, k, beta, noise, {a: round(b, 4) for a, b in es.items()}))
            if beta == 1.0 and noise == 0.0 and es["mRS"] < -1e-9:
                neg_exact.append((t, L, V, k, es["mRS"]))
    print(f"  configs: {n}; sign flips across references: {len(flips)}")
    for f in flips[:8]:
        print("   ", f)
    print(f"  exact model (beta=1, noise=0) with E_sel[mRS] < 0: {len(neg_exact)}")
    for f in neg_exact[:5]:
        print("   ", f)


def search_exact_negative():
    hdr("S2. Exact marginals, k >= 2: can SF's in-set coupling REDUCE KL below matched RS (E_sel < 0 with E_learn = 0)?")
    rng = np.random.default_rng(5)
    best = (0.0, None)
    n = 0
    for t in range(400):
        L, V = [(3, 3), (4, 2), (4, 3)][t % 3]
        conc = [0.05, 0.2, 1.0][(t // 3) % 3]
        qq = rng.dirichlet(np.ones(V ** L) * conc).reshape((V,) * L)
        D = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(V), repeat=L)}
        p = make_pred(D, 0.0)
        for k in range(2, L):
            sf = k_sf(p, k, V)
            e = kld(qd, out_law_dp(sf, L)) - kld(qd, out_law_dp(k_matched(sf, p, V), L))
            n += 1
            if e < best[0]:
                best = (e, (t, L, V, k, conc))
    print(f"  {n} (q, k) pairs; most negative E_sel[mRS] = {best[0]:+.5f} at {best[1]}")
    # hand-built: positively coupled modes. x1 = x2 = x3 with prob 1 - e, else iid uniform
    for e in (0.0, 0.1, 0.3):
        V, L = 3, 3
        qq = np.full((V,) * L, e / V ** L)
        for v in range(V):
            qq[v, v, v] += (1 - e) * [0.5, 0.3, 0.2][v]
        D = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(V), repeat=L)}
        p = make_pred(D, 0.0)
        sf = k_sf(p, 2, V)
        a, b = kld(qd, out_law_dp(sf, L)), kld(qd, out_law_dp(k_matched(sf, p, V), L))
        print(f"  copy chain e={e}: KL(q||p_SF k=2)={a:.5f}  KL(q||p_mRS)={b:.5f}  E_sel={a - b:+.5f}")


def search_T4a_generic():
    hdr("S3. T4(a): is there a GENERIC (tie-free) q with exact marginals where H(p_SF) > H(p_mRS) at the output?")
    rng = np.random.default_rng(9)
    # perturb the report's construction itself (q, not the predictor), so the predictor stays exact
    base = np.zeros((3, 3, 3, 3))
    for x1 in (0, 1):
        for x2 in range(3):
            for x3 in range(3):
                for x4 in range(3):
                    base[x1, x2, x3, x4] = 0.7 / 27 if x1 == 0 else (0.3 / 3 if (x3 == 0 and x4 == 0) else 0.0)
    hits = 0
    for t in range(200):
        sc = [1e-3, 1e-2, 5e-2][t % 3]
        qq = base * np.exp(rng.normal(0, sc, base.shape)) + (base == 0) * rng.uniform(0, sc * 1e-2, base.shape)
        qq /= qq.sum()
        D = Data(qq)
        p = make_pred(D, 0.0)
        s = k_sf(p, 1, 3)
        hs = ent(list(out_law_dp(s, 4).values()))
        hm = ent(list(out_law_dp(k_matched(s, p, 3), 4).values()))
        hits += hs > hm + 1e-9
    print(f"  perturbed constructions (multiplicative noise 1e-3/1e-2/5e-2 on q): H(p_SF) > H(p_mRS) in {hits} of 200")
    # broad random search over structured q: x1 gates the entropy of the rest
    hits = 0
    found = None
    for t in range(600):
        V = 3
        a = rng.dirichlet(np.ones(V) * 0.7)
        hi = rng.dirichlet(np.ones(V ** 3) * 5.0).reshape((V,) * 3)        # high-entropy future
        lo = rng.dirichlet(np.ones(V ** 3) * 0.05).reshape((V,) * 3)       # low-entropy future
        g = rng.integers(0, V)
        qq = np.stack([a[v] * (hi if v != g else lo) for v in range(V)])
        qq = qq / qq.sum()
        D = Data(qq)
        p = make_pred(D, 0.0)
        s = k_sf(p, 1, V)
        hs = ent(list(out_law_dp(s, 4).values()))
        hm = ent(list(out_law_dp(k_matched(s, p, V), 4).values()))
        if hs > hm + 1e-9:
            hits += 1
            if found is None:
                found = (t, hs, hm)
    print(f"  random gated q (600): H(p_SF) > H(p_mRS) in {hits}; first {found}")


def p2_fixed_steps():
    hdr("S4. P2 at FIXED steps (T=2): two partitions of the T4(b) data, exact marginals, sampled values")
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
    D = Data(qb)
    p = make_pred(D, 0.0)
    qd = {x: float(qb[x]) for x in itertools.product(range(4), repeat=4) if qb[x] > 0}
    print(f"  H(q) = {ent(qb):.5f}")
    for lab, parts in (("{x1,x3},{x2,x4}", [(0, 2), (1, 3)]), ("{x1,x4},{x2,x3}", [(0, 3), (1, 2)]),
                       ("{x3,x4},{x1,x2}", [(2, 3), (0, 1)]), ("{x1,x2},{x3,x4}", [(0, 1), (2, 3)])):
        kr = k_rs(p, rho_fixed(parts), 4)
        lw = out_law_dp(kr, 4)
        f, l, _ = budget(D, p, kr, 4)
        print(f"  T=2 {lab:18s} KL={kld(qd, lw):.5f}  E_fact={f:.5f}  E_learn={l:.1e}  H(p)={ent(list(lw.values())):.5f}")


def kl_cont_k1():
    hdr("S5. KL_cont bound with non-identical marginals, k = 1 only, random ties")
    rng = np.random.default_rng(4)
    viol = 0
    worst = (0, None)
    for t in range(3000):
        N = int(rng.integers(2, 5))
        V = int(rng.integers(2, 5))
        laws = [rng.dirichlet(np.ones(V) * rng.choice([0.1, 0.3, 1.0, 5.0])) for _ in range(N)]
        agg = {}
        perms = list(itertools.permutations(range(N)))
        for pr in perms:
            for key, a in sf_closed(laws, laws, 1, list(pr)).items():
                agg[key] = agg.get(key, 0.0) + a / len(perms)
        rho = pos_law(agg)
        Dv = sum(a * math.log(a / (rho[A] * math.prod(laws[i][v] for i, v in zip(A, y)))) for (A, y), a in agg.items() if a > 0)
        if Dv > kl_cont(N, 1) + 1e-10:
            viol += 1
            if Dv - kl_cont(N, 1) > worst[0]:
                worst = (Dv - kl_cont(N, 1), (N, V, Dv, kl_cont(N, 1), [np.round(l, 3).tolist() for l in laws]))
    print(f"  k=1 violations: {viol} of 3000; worst {worst[1]}")


def exact_negative_detail():
    hdr("S6. The most negative exact-marginal case of S2, re-derived under three tie rules")
    rng = np.random.default_rng(5)
    for t in range(400):
        L, V = [(3, 3), (4, 2), (4, 3)][t % 3]
        conc = [0.05, 0.2, 1.0][(t // 3) % 3]
        qq = rng.dirichlet(np.ones(V ** L) * conc).reshape((V,) * L)
        if t == 389:
            break
    D = Data(qq)
    qd = {x: float(qq[x]) for x in itertools.product(range(V), repeat=L)}
    for lab, p, tie in (("exact, index ties", make_pred(D, 0.0), "index"),
                        ("exact, random ties", make_pred(D, 0.0), "random"),
                        ("1e-4 jitter", make_pred(D, 1e-4, seed=1), "index")):
        for k in (2, 3):
            sf = k_sf(p, k, V, tie=tie)
            m = k_matched(sf, p, V)
            a, b = kld(qd, out_law_dp(sf, L)), kld(qd, out_law_dp(m, L))
            c = kld(qd, out_law_dp(k_rs(p, rho_conf(p, k), V), L))
            print(f"  L={L} V={V} k={k} {lab:18s} KL_SF={a:.5f}  KL_mRS={b:.5f}  E_sel[mRS]={a - b:+.5f}  KL_RSconf={c:.5f}  E_sel[RS-conf]={a - c:+.5f}")


def main():
    search_sign()
    search_exact_negative()
    search_T4a_generic()
    p2_fixed_steps()
    kl_cont_k1()
    exact_negative_detail()


if __name__ == "__main__":
    main()
