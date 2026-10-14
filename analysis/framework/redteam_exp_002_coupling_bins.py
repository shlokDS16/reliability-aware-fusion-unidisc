"""Red-team check for EXP-002 v0.2 (no GPU). Two questions.

Q1. How large is SF's joint value coupling given the selected set when the competitor set is large (N up to
    1024), compared with the toy prior (N <= 4)? Measured as the pairwise mutual information between two
    members of A under the exact Prop. 4 law kappa(y | A) ∝ prod_{i in A} P_i(y_i) W_A(min_i g_i(y_i)),
    W_A(m) = prod_{l not in A} P(g_l < m). For k = 2 this pairwise MI equals TC_A.
Q2. Does the card's recommended A3 recipe (2048 log-spaced bins on [1e-12, 1], 5.3) have a blind spot?
    The top regular bin is [10^(-12/2048), 1) = [0.98660, 1): every score in it is lumped. Compare the
    per-position conditional law kappa_i(. | A) computed with exact scores and with binned scores (three
    within-bin conventions), report mean TV (the card's eps_3) and the signed shift in E[log P_i(y)] under
    kappa_i, and show what the card's bins ladder (1024 / 2048 / 4096 bins, N5(a)) reports.

Synthetic rows (V = 256 tokens per row, not a real model) in four regimes (REGIMES below): diffuse
(early-trajectory-like), same (every row the same law, like the all-mask state), mid (some confident rows) and
late (most rows near-deterministic). Score g = probability of the drawn token (tau = 1). Natural logs.
This is evidence about the estimator and the regime only (synthetic, E4 toy); it is not a statement about MDLM.
"""
import numpy as np

rng = np.random.default_rng(20261014)
V = 256


REGIMES = {
    # name: (sigma range, fraction of boosted rows, boost range, identical rows)
    "late": ((0.5, 4.0), 0.7, (4, 14), False),     # many near-deterministic rows
    "mid": ((0.5, 4.0), 0.2, (1, 4), False),       # some confident rows, moderate boosts
    "diffuse": ((0.5, 2.0), 0.0, (0, 0), False),   # early-trajectory-like, top prob about 0.02-0.2
    "same": ((1.5, 1.5), 0.0, (0, 0), True),       # all-mask-like: every row has the same law
}


def make_rows(N, regime):
    (s0, s1), f_det, (b0, b1), same = REGIMES[regime]
    if same:
        z = np.tile(rng.standard_normal(V) * s0, (N, 1))
    else:
        sig = rng.uniform(s0, s1, size=N)
        z = rng.standard_normal((N, V)) * sig[:, None]
    det = rng.random(N) < f_det
    top = rng.integers(0, V, size=N)
    z[np.arange(N)[det], top[det]] += rng.uniform(b0, b1, size=det.sum())
    z -= z.max(1, keepdims=True)
    P = np.exp(z)
    return P / P.sum(1, keepdims=True)


def sf_select(P, k):
    N = P.shape[0]
    cdf = np.cumsum(P, 1)
    u = rng.random(N)
    y = np.minimum((cdf < u[:, None]).sum(1), V - 1)
    g = P[np.arange(N), y]
    return np.sort(np.argsort(-g, kind="stable")[:k])


# ---------- score transforms: exact, or binned (bin index as the score; within-bin handled by `conv`) ----------
def bin_index(x, nbins):
    x = np.asarray(x, float)
    b = np.floor((np.log10(np.clip(x, 1e-300, None)) + 12.0) * nbins / 12.0)
    b = np.clip(b, 0, nbins - 1)
    b = np.where(x >= 1 - 1e-12, nbins, b)  # top tie class
    return b


class Rows:
    """per-row sorted scores and cumulative masses, for F_l(c) = P(g_l < c) (+ w * P(g_l == c))."""

    def __init__(self, P, nbins=None):
        self.S = P if nbins is None else bin_index(P, nbins)
        self.P = P
        o = np.argsort(self.S, 1, kind="stable")
        self.s = np.take_along_axis(self.S, o, 1)
        self.m = np.take_along_axis(P, o, 1)
        self.c = np.concatenate([np.zeros((P.shape[0], 1)), np.cumsum(self.m, 1)], 1)

    def F(self, rows, x, w_eq):
        """mass of score < x plus w_eq * mass of score == x, for each row in rows and each x."""
        out = np.empty((len(rows), len(x)))
        for t, l in enumerate(rows):
            lo = np.searchsorted(self.s[l], x, side="left")
            if w_eq == 0.0:
                out[t] = self.c[l, lo]
            else:
                hi = np.searchsorted(self.s[l], x, side="right")
                out[t] = self.c[l, lo] + w_eq * (self.c[l, hi] - self.c[l, lo])
        return out


def logW(R, nonmem, x, w_eq):
    F = R.F(nonmem, x, w_eq)
    with np.errstate(divide="ignore"):
        return np.log(F).sum(0)


def h_func(R, nonmem, others, xq, w_eq):
    """h(x) = E[W(min(x, M))], M = min score over `others` (each drawn from its own P). Returns log h at xq."""
    if len(others) == 0:
        return logW(R, nonmem, xq, w_eq)
    atoms = np.unique(R.S[others].ravel())
    # survival of M at atoms: P(M >= c) = prod_l P(g_l >= c)
    surv = np.exp(np.log(np.clip(1.0 - R.F(others, atoms, 0.0), 1e-300, None)).sum(0))
    pm = surv - np.append(surv[1:], 0.0)  # P(M == atom)
    lw_at = logW(R, nonmem, atoms, w_eq)
    lw_q = logW(R, nonmem, xq, w_eq)
    surv_q = np.exp(np.log(np.clip(1.0 - R.F(others, xq, 0.0), 1e-300, None)).sum(0))  # P(M >= x)
    L0 = max(lw_at.max(), lw_q.max())
    term_below = np.cumsum(pm * np.exp(lw_at - L0))
    idx = np.searchsorted(atoms, xq, side="left")
    below = np.where(idx > 0, term_below[np.maximum(idx - 1, 0)], 0.0)
    h = surv_q * np.exp(lw_q - L0) + below
    with np.errstate(divide="ignore"):
        return np.log(h) + L0


def member_law(R, A, i, nonmem, w_eq):
    others = [l for l in A if l != i]
    lh = h_func(R, nonmem, others, R.S[i], w_eq)
    lw = np.log(np.clip(R.P[i], 1e-300, None)) + lh
    lw -= lw[np.isfinite(lw)].max()
    w = np.where(np.isfinite(lw), np.exp(lw), 0.0)
    return w / w.sum()


def pair_mi(R, A, i, j, nonmem):
    others = [l for l in A if l not in (i, j)]
    xi, xj = R.S[i], R.S[j]
    mn = np.minimum(xi[:, None], xj[None, :])
    u, inv = np.unique(mn.ravel(), return_inverse=True)
    lh = h_func(R, nonmem, others, u, 0.0)[inv].reshape(mn.shape)
    lj = np.log(R.P[i])[:, None] + np.log(R.P[j])[None, :] + lh
    lj -= lj[np.isfinite(lj)].max()
    J = np.where(np.isfinite(lj), np.exp(lj), 0.0)
    J /= J.sum()
    a, b = J.sum(1), J.sum(0)
    ab = np.outer(a, b)
    m = (J > 1e-300) & (ab > 1e-300)
    return float((J[m] * (np.log(J[m]) - np.log(ab[m]))).sum())


def tv(p, q):
    return 0.5 * float(np.abs(p - q).sum())


print("Q1  pairwise MI (nats) between two members of the SF-selected set, exact Prop. 4 law, V = 256")
print("    N     k   regime    mean pairwise MI   max      sum over pairs (proxy for TC_A, mean)")
Q1_CASES = [(4, 2, r) for r in ("diffuse", "same", "mid")] + [(32, 2, r) for r in ("diffuse", "same", "mid")] +            [(1024, 2, r) for r in ("diffuse", "same", "mid", "late")] + [(1024, 8, r) for r in ("diffuse", "same", "mid")] +            [(1024, 16, r) for r in ("diffuse", "same", "mid", "late")]
for N, k, f in Q1_CASES:
    vals, tots = [], []
    nstates = 6 if N >= 512 else 12
    for _ in range(nstates):
        P = make_rows(N, f)
        A = list(sf_select(P, k))
        nonmem = [l for l in range(N) if l not in A]
        R = Rows(P)
        pairs = [(A[a], A[b]) for a in range(k) for b in range(a + 1, k)]
        if len(pairs) > 6:
            pairs = [pairs[t] for t in rng.choice(len(pairs), 6, replace=False)]
        mis = [pair_mi(R, A, i, j, nonmem) for i, j in pairs]
        vals += mis
        tots.append(np.mean(mis) * k * (k - 1) / 2)
    print(f"  {N:5d} {k:4d}   {f:8s}  {np.mean(vals):.2e}        {np.max(vals):.2e}   {np.mean(tots):.2e}")

print("\nQ2  A3 recipe: exact-score kappa_i(.|A) against binned (2048 log bins on [1e-12,1]); top regular bin is "
      f"[{10 ** (-12 / 2048):.5f}, 1)")
print("    within-bin convention w_eq: 0 = same-bin competitor counts as not below; 0.5 = half; 1 = below")
print("    N     k  regime   w_eq   mean TV (eps_3)  p95 TV    mean signed d E[log P_i]   share of members with max prob in top bin")
for N, k, f in [(1024, 2, "diffuse"), (1024, 16, "diffuse"), (1024, 16, "same"), (1024, 16, "mid"), (512, 16, "late")]:
    for w_eq in (0.0, 0.5, 1.0):
        tvs, dls, topshare = [], [], []
        for _ in range(4):
            P = make_rows(N, f)
            A = list(sf_select(P, k))
            nonmem = [l for l in range(N) if l not in A]
            Re, Rb = Rows(P), Rows(P, nbins=2048)
            for i in A:
                ke = member_law(Re, A, i, nonmem, 0.0)
                kb = member_law(Rb, A, i, nonmem, w_eq)
                tvs.append(tv(ke, kb))
                lp = np.log(P[i])
                dls.append(float((kb - ke) @ lp))
            topshare.append(np.mean([P[i].max() >= 10 ** (-12 / 2048) for i in A]))
        print(f"  {N:5d} {k:4d}  {f:8s} {w_eq:.1f}     {np.mean(tvs):.4f}        {np.percentile(tvs, 95):.4f}"
              f"      {np.mean(dls):+.4f}                  {np.mean(topshare):.2f}")

print("\nQ2b bins ladder (N5(a) analogue): TV between 1024-bin and 4096-bin laws vs TV of 2048-bin law to exact")
for N, k, f in [(1024, 16, "diffuse"), (1024, 16, "same"), (1024, 16, "mid")]:
    lad, ex = [], []
    for _ in range(4):
        P = make_rows(N, f)
        A = list(sf_select(P, k))
        nonmem = [l for l in range(N) if l not in A]
        Re = Rows(P)
        R1, R2, R4 = Rows(P, 1024), Rows(P, 2048), Rows(P, 4096)
        for i in A:
            k1 = member_law(R1, A, i, nonmem, 0.5)
            k2 = member_law(R2, A, i, nonmem, 0.5)
            k4 = member_law(R4, A, i, nonmem, 0.5)
            ke = member_law(Re, A, i, nonmem, 0.0)
            lad.append(tv(k1, k4))
            ex.append(tv(k2, ke))
    print(f"  N={N} k={k} regime={f}: ladder TV(1024 vs 4096 bins) mean {np.mean(lad):.4f} p95 {np.percentile(lad, 95):.4f};"
          f"  TV(2048 bins vs exact) mean {np.mean(ex):.4f} p95 {np.percentile(ex, 95):.4f}")


print("\nQ1b where the coupling lives: small N / k (the last steps of a trajectory); also the per-position sharpening")
print("    N     k   N/k  regime    mean pairwise MI  sum over pairs   mean H(P_i)  mean H(kappa_i | A)")
for k in (8, 16):
    for mult in (2, 3, 4, 8, 32):
        N = k * mult
        for reg in ("diffuse", "same", "mid"):
            vals, tots, hp, hk = [], [], [], []
            for _ in range(6):
                P = make_rows(N, reg)
                A = list(sf_select(P, k))
                nonmem = [l for l in range(N) if l not in A]
                R = Rows(P)
                pairs = [(A[a], A[b]) for a in range(k) for b in range(a + 1, k)]
                pairs = [pairs[t] for t in rng.choice(len(pairs), 4, replace=False)]
                mis = [pair_mi(R, A, i, j, nonmem) for i, j in pairs]
                vals += mis
                tots.append(np.mean(mis) * k * (k - 1) / 2)
                for i in A[:4]:
                    kl_ = member_law(R, A, i, nonmem, 0.0)
                    hp.append(-(P[i] * np.log(P[i])).sum())
                    m = kl_ > 0
                    hk.append(-(kl_[m] * np.log(kl_[m])).sum())
            print(f"  {N:5d} {k:4d} {mult:4d}  {reg:8s}  {np.mean(vals):.2e}          {np.mean(tots):.2e}        "
                  f"{np.mean(hp):.3f}        {np.mean(hk):.3f}")
