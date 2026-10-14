"""Sanity checks for research/review/dossier/primer-gaussian.md.

These are checks of algebra and of statements in the papers on toy cases. They are not
reproductions of any paper's experiment. Run: python primer-gaussian-check.py
Sections:
  A  Duo (2506.10892) Eq. 11: the argmax pushforward map T(alpha~), vs Monte Carlo and K=2 closed form
  B  Duo App. A.3 / Eq. 40: the argmax of a Gaussian trajectory is not the Markov uniform chain
  C  framework-v0 section 2, corollary 3: per-step total correlation of a Gaussian reverse step vs step size
  D  CDCD (2211.15089) section 6.1 setting: nearest-embedding identifiability vs noise level (random embeddings)
  E  identity E_x KL(q_x || p) = KL(q_bar || p) + I(x; z)  (Plaid Eq. 4 vs the marginalised step)
"""
import numpy as np
from scipy import integrate, stats
from scipy.special import log_ndtr

rng = np.random.default_rng(0)


# ---------------------------------------------------------------- A
def T_map(a, K):
    """Duo Eq. 11 with phi the standard normal pdf (the printed exp(-z^2) is a typo; see report)."""
    r = a / np.sqrt(1.0 - a * a)
    f = lambda z: np.exp(stats.norm.logpdf(z - r) + (K - 1) * log_ndtr(z))
    lo, hi = -12.0, 12.0 + r
    P, _ = integrate.quad(f, lo, hi, limit=400)
    return K / (K - 1) * (P - 1.0 / K)


def section_A():
    print("== A. Duo Eq. 11 ==")
    for K in (2, 3, 30):
        for a in (0.2, 0.5, 0.85):
            n = 400_000
            x = np.zeros((n, K)); x[:, 0] = 1.0
            w = a * x + np.sqrt(1 - a * a) * rng.standard_normal((n, K))
            P_mc = np.mean(w.argmax(1) == 0)
            T_mc = (K * P_mc - 1) / (K - 1)
            T_q = T_map(a, K)
            extra = ""
            if K == 2:
                P_cf = stats.norm.cdf(a / (np.sqrt(2) * np.sqrt(1 - a * a)))
                extra = f"  closed-form K=2 T={(2 * P_cf - 1):.5f}"
            print(f"K={K:>3} a~={a:.2f}  T quad={T_q:.5f}  T MC={T_mc:.5f}{extra}")
    print("endpoints for K=30: T(1e-6)=%.6f  T(0.999)=%.6f  (quadrature is unreliable as a~ -> 1 because the integrand becomes a narrow spike; not a property of Eq. 11)" % (T_map(1e-6, 30), T_map(0.999, 30)))
    # Duo sec 4.1.2 claim: for large K a short range of a~ covers most of [0,1]
    for K in (30_000,):
        print(f"K={K}: T(0.85)={T_map(0.85, K):.4f}  T(0.60)={T_map(0.60, K):.4f}  T(0.40)={T_map(0.40, K):.4f}")
    # invert T for a bert-base-uncased-sized vocabulary (K=30522): which alpha~ gives alpha=0.05 and 0.95?
    from scipy.optimize import brentq
    K = 30522
    a05 = brentq(lambda a: T_map(a, K) - 0.05, 0.5, 0.999)
    a95 = brentq(lambda a: T_map(a, K) - 0.95, 0.5, 0.999)
    print(f"K={K}: alpha~ with T=0.05 is {a05:.4f}; alpha~ with T=0.95 is {a95:.4f}")


# ---------------------------------------------------------------- B
def section_B():
    print("== B. argmax of a Gaussian trajectory vs the uniform-state Markov kernel (Duo Eq. 38, 40) ==")
    K = 3
    a_s, a_t = 0.6, 0.3  # alpha~ at the cleaner time s and the noisier time t
    n = 3_000_000
    x = np.zeros((n, K)); x[:, 0] = 1.0  # clean token = class 0
    w_s = a_s * x + np.sqrt(1 - a_s ** 2) * rng.standard_normal((n, K))
    c = a_t / a_s
    w_t = c * w_s + np.sqrt(1 - c * c) * rng.standard_normal((n, K))
    z_s, z_t = w_s.argmax(1), w_t.argmax(1)
    Ts, Tt = T_map(a_s, K), T_map(a_t, K)
    alpha_ts = Tt / Ts
    print(f"T(a_s)={Ts:.4f} T(a_t)={Tt:.4f}  alpha_(t|s)=T(a_t)/T(a_s)={alpha_ts:.4f}")
    # Markov uniform kernel predicts, for z_s = j (any j): P(z_t = i) = (1-alpha_ts)/K for i != j, and alpha_ts+(1-alpha_ts)/K for i=j
    pred_off = (1 - alpha_ts) / K
    pred_diag = alpha_ts + pred_off
    for j in (0, 1):
        m = z_s == j
        row = np.array([np.mean(z_t[m] == i) for i in range(K)])
        print(f"given x=0, z_s={j}: P(z_t=.) = {np.round(row, 4)}   Markov-uniform prediction: diag {pred_diag:.4f}, off-diag {pred_off:.4f}")
    # unconditional-on-x check of the pair marginal is not possible here (x fixed), which is the point: the dependence on x survives z_s.
    m = z_s == 1
    print("given z_s=1 (a wrong class): P(z_t=0) =", round(np.mean(z_t[m] == 0), 4), " P(z_t=2) =", round(np.mean(z_t[m] == 2), 4),
          "(equal under the Markov-uniform kernel)")


# ---------------------------------------------------------------- C
def mutual_info_2d(weights, e, delta, v, grid=161, span=6.0):
    """I(u1;u2) for u_i = delta*e(x_i) + sqrt(v)*eps_i, (x1,x2) ~ weights (2x2). e = (e0,e1)."""
    s = np.sqrt(v)
    lo = delta * min(e) - span * s
    hi = delta * max(e) + span * s
    g = np.linspace(lo, hi, grid)
    dg = g[1] - g[0]
    # component densities along each axis for each token value
    d = np.stack([stats.norm.pdf(g, delta * e[k], s) for k in range(2)])  # (2, grid)
    joint = np.zeros((grid, grid))
    for a in range(2):
        for b in range(2):
            joint += weights[a, b] * np.outer(d[a], d[b])
    m1 = joint.sum(1) * dg
    m2 = joint.sum(0) * dg
    with np.errstate(divide="ignore", invalid="ignore"):
        integrand = np.where(joint > 1e-300, joint * (np.log(joint) - np.log(np.outer(m1, m2))), 0.0)
    return integrand.sum() * dg * dg


def section_C():
    print("== C. per-step total correlation of a Gaussian (VE) reverse step, L=2 binary tokens ==")
    P = np.array([[0.4, 0.1], [0.1, 0.4]])  # data joint, tokens positively dependent
    e = (-1.0, 1.0)
    sig_t = 1.0
    nz = 600
    # sample z_t from the marginal q_t
    idx = rng.choice(4, size=nz, p=P.ravel())
    x1, x2 = idx // 2, idx % 2
    z1 = np.array(e)[x1] + sig_t * rng.standard_normal(nz)
    z2 = np.array(e)[x2] + sig_t * rng.standard_normal(nz)
    deltas = [0.4, 0.2, 0.1, 0.05, 0.025]
    res = []
    for dlt in deltas:
        a = 1 - dlt
        sig_s2 = a * sig_t ** 2
        v = sig_s2 * (1 - a)  # posterior variance of z_s given z_t, x
        tot = 0.0
        for k in range(nz):
            # posterior q(x | z_t): likelihood N(z_t^i; e(x_i), sig_t^2), prior P
            l1 = stats.norm.pdf(z1[k], np.array(e), sig_t)
            l2 = stats.norm.pdf(z2[k], np.array(e), sig_t)
            w = P * np.outer(l1, l2)
            w /= w.sum()
            tot += mutual_info_2d(w, e, dlt, v)
        res.append(tot / nz)
        print(f"delta=1-a={dlt:<6} E_zt[ I(z_s^1; z_s^2 | z_t) ] = {res[-1]:.3e}   per-step/delta^2 = {res[-1] / dlt ** 2:.3f}")
    sl = np.polyfit(np.log(deltas), np.log(res), 1)[0]
    print(f"log-log slope of per-step TC against step size delta: {sl:.2f}  (2 means per-step TC ~ delta^2, summed over ~1/delta steps ~ delta)")


# ---------------------------------------------------------------- D
def section_D():
    print("== D. CDCD-like identifiability of a token from a noisy unit-scale embedding (random embeddings, NOT learned) ==")
    V, d = 32_000, 256
    E = rng.standard_normal((V, d)).astype(np.float32)
    E *= (np.sqrt(d) / np.linalg.norm(E, axis=1, keepdims=True))  # L2-normalise then scale by sqrt(d), as CDCD 6.1
    n = 400
    ids = rng.integers(0, V, n)
    for sigma in (1, 4, 8, 12, 16, 24):
        z = E[ids] + sigma * rng.standard_normal((n, d)).astype(np.float32)
        # nearest embedding in Euclidean distance = argmax of z.e - |e|^2/2, |e|^2 constant here
        pred = (z @ E.T).argmax(1)
        print(f"sigma={sigma:>2}  nearest-embedding accuracy = {np.mean(pred == ids):.3f}")


# ---------------------------------------------------------------- E
def section_E():
    print("== E. identity  E_x KL(q_x || p) = KL(qbar || p) + I(x; z)  ==")
    nx, nz = 5, 7
    px = rng.dirichlet(np.ones(nx))
    q = rng.dirichlet(np.ones(nz), size=nx)  # q(z | x)
    p = rng.dirichlet(np.ones(nz))
    lhs = sum(px[i] * np.sum(q[i] * np.log(q[i] / p)) for i in range(nx))
    qbar = px @ q
    kl = np.sum(qbar * np.log(qbar / p))
    mi = sum(px[i] * np.sum(q[i] * np.log(q[i] / qbar)) for i in range(nx))
    print(f"lhs={lhs:.12f}  rhs={kl + mi:.12f}  diff={lhs - kl - mi:.2e}")


if __name__ == "__main__":
    section_A()
    section_B()
    section_C()
    section_D()
    section_E()
