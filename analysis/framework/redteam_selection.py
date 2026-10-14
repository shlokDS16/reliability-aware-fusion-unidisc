"""Red-team checks against research/review/method/selection-term.md (2026-10-14).

    python analysis/framework/redteam_selection.py > analysis/framework/redteam_selection.log

Reuses the kernels of check_selection.py (imported, not modified). numpy only, natural logs.
Each block prints the numbers quoted in research/review/audits/2026-10-14-red-team-selection-term.md.
"""
from __future__ import annotations

import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_selection as cs  # noqa: E402
from check_selection import (Data, make_pred, k_sf, k_rs, k_matched, pos_law, out_law, paths_P,  # noqa: E402
                             kld, ent, masked, reveal, rho_conf, rho_uniform, rho_fixed, budget,
                             self_distortion, sf_closed, iid_sf_count_law, iid_count_kls, r_max, klv,
                             kl_cont)


def out_law_dp(ker, L):
    """output law by a forward pass over states (cost linear in the number of states, not paths)."""
    w = {(-1,) * L: 1.0}
    out = {}
    for nm in range(L, 0, -1):
        layer = {z: a for z, a in w.items() if sum(v < 0 for v in z) == nm}
        for z, a in layer.items():
            for (A, y), b in ker(z).items():
                z2 = reveal(z, A, y)
                if masked(z2):
                    w[z2] = w.get(z2, 0.0) + a * b
                else:
                    out[z2] = out.get(z2, 0.0) + a * b
    return out


def hdr(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


def configs():
    """the 16 (q, predictor) pairs of check_selection T1 (seeds 0-3, noise 0 / 0.5)."""
    for seed in range(4):
        L, V = (4, 3) if seed < 2 else (3, 3)
        qq = np.random.default_rng(100 + seed).dirichlet(np.ones(V ** L) * 0.4).reshape((V,) * L)
        Dd = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(V), repeat=L)}
        for noise in (0.0, 0.5):
            p = make_pred(Dd, noise, seed=7 + seed)
            yield seed, noise, L, V, qq, Dd, qd, p


def score_fn(p, score):
    def sc(z, j, v):
        m = p(z, j)
        if score == "prob":
            return m[v]
        return m[v] - np.delete(m, v).max()
    return sc


# ----------------------------------------------------------------------------- A. data-scored path law
def data_scored_KL(qd, ker, p, L, k, score="prob"):
    """Q': x ~ q, then at each data state commit the top-k masked positions ranked by the SF score of
    the DATA value x^j (ties by index, the same rule as k_sf). Deterministic given x, so
    Q'(path) = q(x). Returns KL(Q'||P_SF) on paths, and the number of x with P_SF(path*(x)) = 0."""
    sc = score_fn(p, score)
    tot = 0.0
    zero = 0
    for x, qx in qd.items():
        if qx <= 0:
            continue
        z = (-1,) * L
        lp = 0.0
        while masked(z):
            M = masked(z)
            order = sorted(M, key=lambda j: (-sc(z, j, x[j]), j))
            A = tuple(sorted(order[:min(k, len(M))]))
            y = tuple(x[a] for a in A)
            a = ker(z).get((A, y), 0.0)
            if a <= 0:
                zero += 1
                lp = -math.inf
                break
            lp += math.log(a)
            z = reveal(z, A, y)
        tot += qx * (math.log(qx) - lp)
    return tot, zero


def block_A():
    hdr("A. Proposition 2 depends on the choice of data path law: data-scored Q' gives a FINITE forward path KL")
    print("  config                               KL(q||p_SF)  KL(Q_kappa||P_SF)  KL(Q'||P_SF)  G'=path-out  #x with P(path*)=0")
    allfinite = True
    for seed, noise, L, V, qq, Dd, qd, p in configs():
        for name, k, score, tau in (("SF k=1", 1, "prob", 1.0), ("SF k=2", 2, "prob", 1.0),
                                    ("SF k=1 margin", 1, "margin", 1.0), ("SF k=1 tau=0.7", 1, "prob", 0.7)):
            ker = k_sf(p, k, V, tau=tau, score=score)
            klo = kld(qd, out_law(ker, L))
            klQ, z0 = data_scored_KL(qd, ker, p, L, k, score)
            allfinite &= math.isfinite(klQ) and z0 == 0 and klQ >= klo - 1e-12
            print(f"  L={L} seed={seed} noise={noise} {name:15s}  {klo:9.5f}      inf (report)      {klQ:9.5f}   {klQ - klo:9.5f}   {z0}")
    # framework toy
    q0 = np.random.default_rng(0).dirichlet(np.ones(81) * 0.35).reshape((3,) * 4)
    D0 = Data(q0)
    pe = make_pred(D0, 0.0)
    sf = k_sf(pe, 1, 3)
    qd0 = {x: float(q0[x]) for x in itertools.product(range(3), repeat=4)}
    klo = kld(qd0, out_law(sf, 4))
    klQ, z0 = data_scored_KL(qd0, sf, pe, 4, 1)
    print(f"  framework toy (1.288 nats): KL(q||p_SF)={klo:.6f}  KL(Q'||P_SF)={klQ:.6f}  G'={klQ - klo:.6f}  blocked x: {z0}")
    print(f"  RESULT: forward path KL under the data-scored path law finite in every SF config: {allfinite}")


# ----------------------------------------------------------------------------- B. blocking vs vocabulary size
def block_B():
    hdr("B. Is 'blocked (position, value) pair' (Prop. 2) a small-vocabulary artefact? exact model, k=1, continuous scores")
    rng = np.random.default_rng(7)
    print("  V      N   logit sd  P(data pair blocked)   E[forward per-step value term] (finite part, nats)  max over states")
    for V in (3, 10, 100, 1000, 10000):
        for N in (8, 64):
            for sd in (1.0, 3.0):
                pb_list, vt_list = [], []
                for rep in range(20 if V <= 1000 else 6):
                    lg = rng.normal(0, sd, (N, V))
                    P = np.exp(lg - lg.max(1, keepdims=True))
                    P /= P.sum(1, keepdims=True)
                    S = np.sort(P, axis=1)
                    C = np.concatenate([np.zeros((N, 1)), np.cumsum(S, axis=1)], axis=1)
                    # F_j(c) = mass of values with p < c, evaluated at every c = P[i, v]
                    tot = np.zeros((N, V))
                    diag = np.zeros((N, V))
                    for j in range(N):
                        idx = np.searchsorted(S[j], P, side="left")
                        F = C[j][idx]
                        with np.errstate(divide="ignore"):
                            lf = np.log(F)
                        tot += lf
                        diag[j] = lf[j]
                    with np.errstate(invalid="ignore"):
                        logPi = np.where(np.isinf(diag) & np.isinf(tot), -np.inf, tot - diag)
                    # a -inf in tot coming only from j = i itself must not block i: recompute those rows exactly
                    for i in range(N):
                        bad = np.isneginf(logPi[i]) & np.isneginf(diag[i])
                        if bad.any():
                            acc = np.zeros(bad.sum())
                            for j in range(N):
                                if j == i:
                                    continue
                                idx = np.searchsorted(S[j], P[i][bad], side="left")
                                with np.errstate(divide="ignore"):
                                    acc += np.log(C[j][idx])
                            logPi[i][bad] = acc
                    Pi = np.exp(logPi)
                    rho = (P * Pi).sum(1)
                    rho = rho / rho.sum()   # continuous scores: sums to 1 up to float error
                    blocked = (Pi == 0)
                    pb = float((rho[:, None] * P * blocked).sum())
                    with np.errstate(divide="ignore", invalid="ignore"):
                        term = np.where(blocked, 0.0, P * (np.log(rho)[:, None] - logPi))
                    vt = float((rho * term.sum(1)).sum())
                    pb_list.append(pb)
                    vt_list.append(vt)
                print(f"  {V:6d} {N:4d}  {sd:4.1f}      {np.mean(pb_list):.3e}            {np.mean(vt_list):10.4f}   {np.max(vt_list):10.4f}")


# ----------------------------------------------------------------------------- C. SF k=1 is a state-only tilt in law
def block_C():
    hdr("C. SF at k=1 has the SAME kernel as a V1 'marginal tilt' sampler (positions ~ rho_SF(.|s), values ~ kappa_i(.|s))")
    q0 = np.random.default_rng(0).dirichlet(np.ones(81) * 0.35).reshape((3,) * 4)
    D0 = Data(q0)
    qd0 = {x: float(q0[x]) for x in itertools.product(range(3), repeat=4)}
    for noise in (0.0, 0.4):
        pe = make_pred(D0, noise, seed=3)
        sf = k_sf(pe, 1, 3)
        cache = {}

        def v1(z):
            # rank-then-sample with a state-only tilt: draw i ~ rho(.|z) with fresh noise, then v ~ ptilde_i(.|z),
            # where ptilde_i = p_i * Pi_i(p_i) / rho(i) is computed from the marginals in z only (Prop. 4)
            if z in cache:
                return cache[z]
            M = masked(z)
            laws = [pe(z, i) for i in M]
            kd = sf_closed(laws, laws, 1)                 # closed form uses only the marginals at z
            rho = {}
            for (A, y), a in kd.items():
                rho[A] = rho.get(A, 0.0) + a
            out = {}
            for A, r in rho.items():
                til = np.zeros(3)
                for (B, y), a in kd.items():
                    if B == A:
                        til[y[0]] += a / r
                out[((M[A[0]],), None)] = None
                for v in range(3):
                    if til[v] > 0:
                        out[((M[A[0]],), (v,))] = r * til[v]
            out = {key: val for key, val in out.items() if key[1] is not None}
            cache[z] = out
            return out
        l1, l2 = out_law(sf, 4), out_law(v1, 4)
        diff = max(abs(l1.get(x, 0) - l2.get(x, 0)) for x in set(l1) | set(l2))
        # forward 'E_tilt' of this tilt on data paths with position law rho: inf iff some data value has ptilde = 0
        f, l, s = budget(D0, pe, v1, 3)
        print(f"  noise={noise}: max |p_SF(x) - p_V1(x)| = {diff:.1e};  KL(q||p_SF) = {kld(qd0, l1):.6f};"
              f"  forward per-step tilt term E_tilt of the V1 twin = {s}")


# ----------------------------------------------------------------------------- D. reference dependence of E_sel
def rho_expscore(p, k):
    """deterministic RS: rank by the expected SF score E_{Y~p_i}[p_i(Y)] = sum_v p_i(v)^2, ties by index."""
    def r(z):
        M = masked(z)
        s = sorted(M, key=lambda i: (-(p(z, i) ** 2).sum(), i))
        return {tuple(sorted(s[:min(k, len(M))])): 1.0}
    return r


def block_D():
    hdr("D. E_sel := KL(q||p_SF) - KL(q||p_ref) under four defensible RS references (same k, same passes)")
    print("  config                         KL_SF    E_sel[mRS]  E_sel[RS-conf]  E_sel[RS-E(score)]  E_sel[RS-unif]  E_sel[mRS tilted]")
    flips = 0
    spreads = []
    n = 0
    for seed, noise, L, V, qq, Dd, qd, p in configs():
        for name, k, tau in (("SF k=1", 1, 1.0), ("SF k=2", 2, 1.0), ("SF k=1 tau=0.7", 1, 0.7)):
            ker = k_sf(p, k, V, tau=tau)
            kl_sf = kld(qd, out_law(ker, L))
            tr = (lambda m, t=tau: (m ** (1 / t)) / (m ** (1 / t)).sum())
            refs = {
                "mRS": k_matched(ker, p, V),
                "RS-conf": k_rs(p, rho_conf(p, k), V),
                "RS-E": k_rs(p, rho_expscore(p, k), V),
                "RS-unif": k_rs(p, rho_uniform(k), V),
                "mRS-tilt": k_rs(p, lambda z: pos_law(ker(z)), V, transform=None if tau == 1.0 else tr),
            }
            es = {nm: kl_sf - kld(qd, out_law(r, L)) for nm, r in refs.items()}
            sgn = {np.sign(round(v, 9)) for nm, v in es.items() if nm != "mRS-tilt"}
            flips += len(sgn) > 1
            vals = [es[nm] for nm in ("mRS", "RS-conf", "RS-E", "RS-unif")]
            spreads.append(max(vals) - min(vals))
            n += 1
            print(f"  L={L} s={seed} n={noise} {name:15s} {kl_sf:7.4f}   {es['mRS']:+8.4f}    {es['RS-conf']:+8.4f}       {es['RS-E']:+8.4f}         {es['RS-unif']:+8.4f}       {es['mRS-tilt']:+8.4f}")
    print(f"  sign of E_sel differs across the four RS references in {flips} of {n} configs;"
          f" median spread {np.median(spreads):.3f} nats, max spread {max(spreads):.3f}")


# ----------------------------------------------------------------------------- E. ties: T4.2 and T3.16
def k_sf_perturbed(Dd, V, eps, seed):
    p = make_pred(Dd, eps, seed=seed)
    return p


def block_E():
    hdr("E. Tie sensitivity of T4.2 (SF entropy above mRS) and T3.16 (U-shape)")
    # T4.2 construction
    qc = np.zeros((3, 3, 3, 3))
    pa = 0.7
    for x1 in (0, 1):
        for x2 in range(3):
            for x3 in range(3):
                for x4 in range(3):
                    if x1 == 0:
                        qc[x1, x2, x3, x4] = pa * (1 / 3) * (1 / 9)
                    else:
                        qc[x1, x2, x3, x4] = (1 - pa) * (1 / 3) * (1.0 if (x3 == 0 and x4 == 0) else 0.0)
    Dc = Data(qc)
    for label, p, tie in (("exact, index ties (report)", make_pred(Dc, 0.0), "index"),
                          ("exact, random ties", make_pred(Dc, 0.0), "random"),
                          ("ties broken by 1e-4 log-normal jitter", make_pred(Dc, 1e-4, seed=1), "index"),
                          ("ties broken by 1e-4 jitter, seed 2", make_pred(Dc, 1e-4, seed=2), "index")):
        s = k_sf(p, 1, 3, tie=tie)
        m = k_matched(s, p, 3)
        hs, hm = ent(list(out_law(s, 4).values())), ent(list(out_law(m, 4).values()))
        print(f"  T4.2 [{label:38s}] H(p_SF)={hs:.5f}  H(p_mRS)={hm:.5f}  SF higher: {hs > hm + 1e-9}")
    # U-shape
    print("  U-shape of KL(q||p_SF) in T (Markov chain, V=2); columns: L, flip, start P(x1=0), predictor, ties, KL at T=1..L, interior min?")
    for L in (6, 8):
        Ts = [t for t in range(1, L + 1) if L % t == 0]
        for flip in ((0.05, 0.1, 0.2, 0.3) if L == 6 else (0.1, 0.2)):
            for p0 in ((0.5, 0.7) if L == 6 else (0.5,)):
                q = np.zeros((2,) * L)
                for x in itertools.product((0, 1), repeat=L):
                    pr = p0 if x[0] == 0 else 1 - p0
                    for a, b in zip(x[:-1], x[1:]):
                        pr *= flip if a != b else 1 - flip
                    q[x] = pr
                Dm = Data(q)
                qd = {x: float(q[x]) for x in itertools.product((0, 1), repeat=L)}
                variants = [("exact", make_pred(Dm, 0.0), "index")]
                if L == 6 and flip == 0.1:
                    variants.append(("exact", make_pred(Dm, 0.0), "random"))
                variants.append(("jitter 1e-4", make_pred(Dm, 1e-4, seed=5), "index"))
                variants.append(("noisy 0.3", make_pred(Dm, 0.3, seed=5), "index"))
                for lab, p, tie in variants:
                    kls = []
                    for T in Ts:
                        k = L // T
                        kls.append(kld(qd, out_law_dp(k_sf(p, k, 2, tie=tie), L)))
                    interior = min(kls[1:-1]) < min(kls[0], kls[-1]) if len(kls) > 2 else False
                    argm = Ts[int(np.argmin(kls))]
                    print(f"    L={L} flip={flip:.2f} p0={p0} {lab:11s} {tie:6s} " + " ".join(f"{v:7.4f}" for v in kls)
                          + f"   argmin T={argm}  interior={interior}")


# ----------------------------------------------------------------------------- F. T4(b) kills the P2 diagnostic, not only its premise
def block_F():
    hdr("F. T4(b) data: the lever 'more steps' lowers KL through E_fact only and moves entropy ACROSS H(q) downwards")
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
    qdb = {x: float(qb[x]) for x in itertools.product(range(4), repeat=4) if qb[x] > 0}
    print(f"  H(q) = {ent(qb):.5f}")
    for lab, rho in (("T=1 one-shot product", rho_fixed([(0, 1, 2, 3)])),
                     ("T=2 {x1,x2},{x3,x4}", rho_fixed([(0, 1), (2, 3)])),
                     ("T=3 {x1,x2},{x3},{x4}", rho_fixed([(0, 1), (2,), (3,)])),
                     ("T=4 left to right", rho_fixed([(0,), (1,), (2,), (3,)]))):
        kr = k_rs(pb, rho, 4)
        lw = out_law(kr, 4)
        f, l, _ = budget(Db, pb, kr, 4)
        print(f"  {lab:24s} KL(q||p)={kld(qdb, lw):.5f}  E_fact={f:.5f}  E_learn={l:.1e}  H(p)={ent(list(lw.values())):.5f}")


# ----------------------------------------------------------------------------- G. self-distortion small, E_sel large (F2)
def block_G():
    hdr("G. Falsifier F2 ('Delta < 1e-3 nats/token => E_sel negligible'): iid data, exact marginals, SF k=1 (E_sel = KL(q||p_SF))")
    print("  p                      N    Delta/token   E_sel/token   ratio")
    for p in (np.array([0.45, 0.35, 0.20]), np.array([0.99, 0.006, 0.004]), np.array([0.999, 0.0006, 0.0004])):
        for N in (16, 32, 64, 128):
            logd = iid_sf_count_law(p, N, [1] * N)
            fwd, rev = iid_count_kls(p, N, logd)
            selfd = sum(klv(r_max(p, m), p) for m in range(1, N + 1))
            print(f"  {str(np.round(p, 4)):22s} {N:4d}   {selfd / N:.3e}    {fwd / N:.3e}    {fwd / max(selfd, 1e-300):8.2f}")


# ----------------------------------------------------------------------------- H. KL_cont bound for non-identical marginals
def block_H():
    hdr("H. Is D <= KL_cont(N,k) for NON-identical marginals under random ties (T2 limit (b) says 'any marginal')?")
    rng = np.random.default_rng(3)
    viol = 0
    worst = (0.0, None)
    tried = 0
    for trial in range(3000):
        N = int(rng.integers(2, 5))
        V = int(rng.integers(2, 5))
        k = 1 if N == 2 else int(rng.integers(1, 3))
        laws = [rng.dirichlet(np.ones(V) * rng.choice([0.1, 0.3, 1.0, 5.0])) for _ in range(N)]
        agg = {}
        perms = list(itertools.permutations(range(N)))
        for pr in perms:
            for key, a in sf_closed(laws, laws, k, list(pr)).items():
                agg[key] = agg.get(key, 0.0) + a / len(perms)
        rho = pos_law(agg)
        Dv = sum(a * math.log(a / (rho[A] * math.prod(laws[i][v] for i, v in zip(A, y)))) for (A, y), a in agg.items() if a > 0)
        tried += 1
        if Dv > kl_cont(N, k) + 1e-10:
            viol += 1
            if Dv - kl_cont(N, k) > worst[0]:
                worst = (Dv - kl_cont(N, k), (N, k, [np.round(l, 3).tolist() for l in laws], Dv, kl_cont(N, k)))
    print(f"  violations: {viol} of {tried}")
    if worst[1]:
        N, k, laws, Dv, kc = worst[1]
        print(f"  worst: N={N} k={k} D={Dv:.5f} > KL_cont={kc:.5f}; marginals {laws}")
    # a two-position hand case
    laws = [np.array([0.5, 0.5]), np.array([0.98, 0.02])]
    agg = {}
    for pr in ((0, 1), (1, 0)):
        for key, a in sf_closed(laws, laws, 1, list(pr)).items():
            agg[key] = agg.get(key, 0.0) + a / 2
    rho = pos_law(agg)
    Dv = sum(a * math.log(a / (rho[A] * math.prod(laws[i][v] for i, v in zip(A, y)))) for (A, y), a in agg.items())
    print(f"  hand case p1=(0.5,0.5), p2=(0.98,0.02): D={Dv:.5f}, KL_cont(2,1)={kl_cont(2, 1):.5f}")


# ----------------------------------------------------------------------------- I. P1 identification (Codex objection 2)
def block_I():
    hdr("I. P1: does the gain at k=1 equal the E_learn part of the gain at k>1? two deterministic RS position rules")
    print("  q-seed noise  k  T   [conf] E_fact  E_learn  KL   | [L-to-R] E_fact  E_learn  KL   | dE_learn(k)  dE_fact(k)  gain(k)")
    bad = 0
    tot = 0
    for qs in range(6):
        L, V = 4, 3
        qq = np.random.default_rng(400 + qs).dirichlet(np.ones(V ** L) * 0.4).reshape((V,) * L)
        Dd = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(V), repeat=L)}
        for noise in (0.3, 0.6):
            p = make_pred(Dd, noise, seed=qs + 11)
            rows = {}
            for k in (1, 2):
                a = k_rs(p, rho_conf(p, k), V)
                lr = rho_fixed([tuple(range(i, min(i + k, L))) for i in range(0, L, k)])
                b = k_rs(p, lr, V)
                fa, la, _ = budget(Dd, p, a, V)
                fb, lb, _ = budget(Dd, p, b, V)
                ka, kb = kld(qd, out_law(a, L)), kld(qd, out_law(b, L))
                rows[k] = (fa, la, ka, fb, lb, kb)
                print(f"  {qs:5d}  {noise:4.1f}  {k}  {L // k}   {fa:7.4f} {la:7.4f} {ka:7.4f} |      {fb:7.4f} {lb:7.4f} {kb:7.4f} |"
                      f"  {lb - la:+8.4f}   {fb - fa:+8.4f}   {kb - ka:+8.4f}")
            dl1 = rows[1][4] - rows[1][1]
            dl2 = rows[2][4] - rows[2][1]
            tot += 1
            if abs(dl2 - dl1) > 0.25 * max(abs(dl1), 1e-3) or np.sign(dl1) != np.sign(dl2):
                bad += 1
    print(f"  dE_learn at k=2 differs from the k=1 gain by more than 25 % (or in sign) in {bad} of {tot} cases")


# ----------------------------------------------------------------------------- J. requery estimator under an inconsistent model
def block_J():
    hdr("J. Reveal-and-requery S^ under a marginally inconsistent model: S^ > 0 with zero model dependence")
    u = np.array([0.4, 0.3, 0.3])          # p_theta(b_j | s): image marginal before the text is revealed
    r = np.array([0.6, 0.2, 0.2])          # p_theta(b_j | s, a): the same for EVERY text a (no dependence on a)
    print(f"  model's I(a; b_j) = 0 by construction; S^ = KL(r||u) per image token = {klv(r, u):.5f} nats; x k_I image tokens")
    # consistent model with dependence for comparison: mixture of conditionals equals the marginal
    print("  (S^ = I_theta(a;b_j) + KL(mean_a p(b_j|s,a) || p(b_j|s)); the second term is the inconsistency bias)")


# ----------------------------------------------------------------------------- K. G > 0 for randomised position laws?
def block_K():
    hdr("K. 'G > 0 for randomised position laws' (Theorem 1 text): uniform random order, k=1")
    for noise in (0.0, 0.4):
        qq = np.random.default_rng(5).dirichlet(np.ones(81) * 0.4).reshape((3,) * 4)
        Dd = Data(qq)
        qd = {x: float(qq[x]) for x in itertools.product(range(3), repeat=4)}
        p = make_pred(Dd, noise, seed=3)
        ker = k_rs(p, rho_uniform(1), 3)
        PP = paths_P(ker, 4)
        QQ = cs.paths_Q(Dd, lambda z: pos_law(ker(z)), 4, 3)
        print(f"  noise={noise}: path KL={kld(QQ, PP):.6f}  output KL={kld(qd, cs.marg_x(PP, 4)):.6f}  G={kld(QQ, PP) - kld(qd, cs.marg_x(PP, 4)):.2e}")


def main():
    block_A()
    block_B()
    block_C()
    block_D()
    block_E()
    block_F()
    block_G()
    block_H()
    block_I()
    block_J()
    block_K()


if __name__ == "__main__":
    main()
