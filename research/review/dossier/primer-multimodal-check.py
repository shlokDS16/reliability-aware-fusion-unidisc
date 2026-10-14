"""Exact toy checks for primer-multimodal.md (Q6, P5). numpy only, seeds fixed.

A. Chain rule of total correlation over a modality partition:
   TC(x^A | z) = TC(text part | z) + TC(image part | z) + I(text part ; image part | z).
   Checked on random joint distributions (4 tokens, 2 per modality, vocabulary 3).
B. Budget accounting in a two-modality toy (binary tokens t1,t2 | i1,i2), all ordered
   partitions of the four tokens into two steps of two tokens (k = 2, NFE = 2 for all):
   KL(q || p_policy) == E_fact (exact predictor), split into within-text, within-image
   and cross-modal terms. Sweep: layout coupling (t1,i1 share a latent) and within-modality
   coupling.
C. Entropy bound TC(A|z) <= sum_i H(i|z) - max_i H(i|z): tokens a confidence rule would
   commit (low marginal entropy) have small TC whatever their modality.
"""
import itertools
import numpy as np

rng = np.random.default_rng(0)


def H(p):
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def marg(q, keep):
    axes = tuple(a for a in range(q.ndim) if a not in keep)
    return q.sum(axis=axes) if axes else q


def Hs(q, S):  # joint entropy of subset S (tuple of axes)
    if len(S) == 0:
        return 0.0
    return H(marg(q, tuple(S)).ravel())


def Hc(q, S, R):  # conditional entropy H(S | R) = H(S u R) - H(R)
    return Hs(q, tuple(sorted(set(S) | set(R)))) - Hs(q, tuple(sorted(R)))


def tc_cond(q, A, R):
    return sum(Hc(q, (i,), R) for i in A) - Hc(q, A, R)


def mi_cond(q, A1, A2, R):
    return Hc(q, A1, R) + Hc(q, A2, R) - Hc(q, tuple(A1) + tuple(A2), R)


# ---------------- A ----------------
maxerr = 0.0
for _ in range(200):
    q = rng.dirichlet(np.ones(81) * 0.3).reshape(3, 3, 3, 3)  # axes: t1,t2,i1,i2
    T, I = (0, 1), (2, 3)
    for R in [(), (0,), (2,), (0, 3)]:
        A = tuple(i for i in range(4) if i not in R)
        At = tuple(i for i in A if i in T)
        Ai = tuple(i for i in A if i in I)
        lhs = tc_cond(q, A, R)
        rhs = (tc_cond(q, At, R) if len(At) else 0.0) + (tc_cond(q, Ai, R) if len(Ai) else 0.0)
        if len(At) and len(Ai):
            rhs += mi_cond(q, At, Ai, R)
        maxerr = max(maxerr, abs(lhs - rhs))
print("A  chain rule TC = TC_text + TC_image + I(text;image | R): max abs error over 800 cases = %.2e" % maxerr)

# ---------------- B ----------------
def build_q(e_c, e_t, e_i):
    """L ~ Bern(.5); t1 = L ^ N(e_c); i1 = L ^ N(e_c)  (shared layout latent);
    t2 = t1 ^ N(e_t); i2 = i1 ^ N(e_i). Axes t1,t2,i1,i2."""
    q = np.zeros((2, 2, 2, 2))
    flip = lambda b, e: e if b else 1 - e
    for L, t1, i1, t2, i2 in itertools.product((0, 1), repeat=5):
        pr = 0.5 * flip(t1 ^ L, e_c) * flip(i1 ^ L, e_c) * flip(t2 ^ t1, e_t) * flip(i2 ^ i1, e_i)
        q[t1, t2, i1, i2] += pr
    return q


NAMES = ["t1", "t2", "i1", "i2"]
T, I = (0, 1), (2, 3)


def policy_stats(q, steps):
    """steps = (A1, A2). Returns E_fact total, within-text, within-image, cross, and KL(q||p)."""
    R = ()
    tot = wt = wi = cr = 0.0
    for A in steps:
        At = tuple(i for i in A if i in T)
        Ai = tuple(i for i in A if i in I)
        tot += tc_cond(q, A, R)
        wt += tc_cond(q, At, R) if len(At) > 1 else 0.0
        wi += tc_cond(q, Ai, R) if len(Ai) > 1 else 0.0
        cr += mi_cond(q, At, Ai, R) if (len(At) and len(Ai)) else 0.0
        R = tuple(sorted(set(R) | set(A)))
    # exact KL(q || p) for the sampler that draws each step's tokens independently from q(x_i | revealed)
    kl = 0.0
    for x in itertools.product((0, 1), repeat=4):
        px = q[x]
        if px == 0:
            continue
        logp = 0.0
        R = ()
        for A in steps:
            for i in A:
                num = marg(q, tuple(sorted(set(R) | {i})))
                den = marg(q, tuple(sorted(R))) if R else None
                idx_num = tuple(x[a] for a in sorted(set(R) | {i}))
                pn = num[idx_num]
                pd = den[tuple(x[a] for a in sorted(R))] if R else 1.0
                logp += np.log(pn / pd)
            R = tuple(sorted(set(R) | set(A)))
        kl += px * (np.log(px) - logp)
    return tot, wt, wi, cr, kl


pairs = list(itertools.combinations(range(4), 2))
ordered = []
for A1 in pairs:
    A2 = tuple(i for i in range(4) if i not in A1)
    ordered.append((A1, A2))

maxgap = 0.0
print("B  ordered partitions (step1 | step2); E_fact = within_text + within_image + cross; KL(q||p) from enumeration")
for (e_c, e_t, e_i) in [(0.05, 0.4, 0.4), (0.05, 0.1, 0.1), (0.3, 0.1, 0.1)]:
    q = build_q(e_c, e_t, e_i)
    print(f"   layout noise e_c={e_c}, within-text e_t={e_t}, within-image e_i={e_i}   (nats)")
    rows = []
    for st in ordered:
        tot, wt, wi, cr, kl = policy_stats(q, st)
        maxgap = max(maxgap, abs(tot - kl), abs(tot - (wt + wi + cr)))
        rows.append((tot, st, wt, wi, cr, kl))
    for tot, st, wt, wi, cr, kl in sorted(rows, key=lambda r: r[0]):
        lab = "{" + ",".join(NAMES[i] for i in st[0]) + "} | {" + ",".join(NAMES[i] for i in st[1]) + "}"
        print(f"     {lab:16s} E_fact={tot:.4f}  text={wt:.4f} image={wi:.4f} cross={cr:.4f}  KL={kl:.4f}")
print("B  max |E_fact - KL| and |E_fact - (text+image+cross)| over all rows = %.2e" % maxgap)

# ---------------- C ----------------
viol = 0
worst = 1e9
for _ in range(2000):
    q = rng.dirichlet(np.ones(81) * rng.choice([0.05, 0.3, 1.0])).reshape(3, 3, 3, 3)
    A = tuple(sorted(rng.choice(4, size=rng.integers(2, 5), replace=False)))
    hs = [Hs(q, (i,)) for i in A]
    tc = tc_cond(q, A, ())
    slack = (sum(hs) - max(hs)) - tc
    worst = min(worst, slack)
    if slack < -1e-12:
        viol += 1
print("C  TC <= sum H_i - max H_i on 2000 random sets: violations = %d, smallest slack = %.3e" % (viol, worst))
