"""Check the mixture-reference estimator of the model's cross-modal dependence (framework-v2 C, P5).

Setting: at a sampler state s, a masked model gives (i) a joint over a text set a, p(a|s), (ii) image
marginals after revealing a, p(b|s,a), and (iii) a one-pass image marginal p1(b|s) that need not equal
mean_a p(b|s,a) (marginal inconsistency, red-team M10 block J).

Model dependence: I_theta = sum_a p(a|s) KL(p(b|s,a) || mbar), mbar = sum_a p(a|s) p(b|s,a).
Naive estimator (one-pass reference): E_a KL(p(b|s,a) || p1) = I_theta + KL(mbar || p1).
Mixture estimator with R samples: (1/R) sum_r KL(p(b|s,a_r) || mbar_R), mbar_R = mean_r p(b|s,a_r).

Checks: (A) the naive identity exactly; (B) the red-team block-J case (no dependence, shifted
marginal) gives naive 0.081 and mixture 0; (C) mixture estimator converges to I_theta and its
finite-R bias is negative (plug-in), over random models. Natural logs.
"""
import numpy as np

rng = np.random.default_rng(0)


def kl(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    m = p > 0
    return float(np.sum(p[m] * (np.log(p[m]) - np.log(q[m]))))


def exact(pa, pb_a, p1):
    mbar = pa @ pb_a
    mi = sum(pa[i] * kl(pb_a[i], mbar) for i in range(len(pa)))
    naive = sum(pa[i] * kl(pb_a[i], p1) for i in range(len(pa)))
    return mi, naive, kl(mbar, p1)


def mixture_est(pa, pb_a, R, reps):
    out = []
    for _ in range(reps):
        idx = rng.choice(len(pa), size=R, p=pa)
        rows = pb_a[idx]
        mR = rows.mean(0)
        out.append(np.mean([kl(r, mR) for r in rows]))
    return float(np.mean(out)), float(np.std(out) / np.sqrt(reps))


fails = 0
# (A) identity naive = I + KL(mbar || p1) on random models
worst = 0.0
for _ in range(2000):
    na, nb = rng.integers(2, 6), rng.integers(2, 6)
    pa = rng.dirichlet(np.ones(na))
    pb_a = rng.dirichlet(np.ones(nb), size=na)
    p1 = rng.dirichlet(np.ones(nb))
    mi, naive, inc = exact(pa, pb_a, p1)
    worst = max(worst, abs(naive - (mi + inc)))
print(f"A  naive = I_theta + KL(mbar||p1): max abs error over 2000 random models = {worst:.2e}")
fails += worst > 1e-12

# (B) red-team block J: image marginal independent of text, but shifted once any text is revealed
pa = np.array([0.5, 0.5])
pb_a = np.array([[0.6, 0.2, 0.2], [0.6, 0.2, 0.2]])
p1 = np.array([0.4, 0.3, 0.3])
mi, naive, inc = exact(pa, pb_a, p1)
m_est, _ = mixture_est(pa, pb_a, R=8, reps=200)
print(f"B  zero dependence, shifted marginal: I_theta = {mi:.5f}, naive = {naive:.5f}, "
      f"mixture (R=8) = {m_est:.5f}")
fails += not (abs(mi) < 1e-12 and abs(naive - 0.08109) < 1e-4 and abs(m_est) < 1e-12)

# (C) convergence and sign of the finite-R bias
neg_bias = 0
rows_out = []
for t in range(40):
    na, nb = rng.integers(2, 6), rng.integers(2, 6)
    pa = rng.dirichlet(np.ones(na))
    pb_a = rng.dirichlet(np.ones(nb) * 0.7, size=na)
    mi, _, _ = exact(pa, pb_a, rng.dirichlet(np.ones(nb)))
    res = [mixture_est(pa, pb_a, R, reps=400) for R in (4, 16, 64)]
    ests = [e for e, _ in res]
    # bias is negative in expectation (E H(mbar_R) <= H(mbar), concavity); allow 3 standard errors of MC noise
    neg_bias += all(e <= mi + 3 * se + 1e-9 for e, se in res)
    rows_out.append((mi, *ests))
rel64 = np.median([abs(r[3] - r[0]) / max(r[0], 1e-9) for r in rows_out])
print(f"C  40 random models: finite-R estimate <= I_theta at R = 4, 16, 64 (within 3 MC standard errors) in {neg_bias}/40; "
      f"median relative error at R = 64 = {rel64:.3f}")
for r in rows_out[:5]:
    print(f"   I_theta={r[0]:.4f}  R=4:{r[1]:.4f}  R=16:{r[2]:.4f}  R=64:{r[3]:.4f}")
fails += neg_bias < 40 or rel64 > 0.1

print("SUMMARY: failures =", fails)
