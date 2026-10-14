"""Red-team checks for EXP-001 v0.2 (no GPU, synthetic; evidence about the estimator and the endpoint, not about UniDisc).

Part 1. Numerical floor of the mixture estimator against marginal entropy.
  A requery that reveals a token carrying NO information still changes the network input, so bf16 arithmetic perturbs
  the returned image marginal. Model: logits l (V = 16,384 image codes, entropy set by a logit scale); requery r returns
  bf16(log_softmax(l + d_r)), d_r iid N(0, s^2) per code (s calibrated so that two requeries differ by mean TV 0.002 to
  0.016, the range of setup.md 2.1's bf16-vs-fp32 TV), exponentiated and renormalised in float64 as the card does (6).
  The plug-in mixture estimate I_hat over R = 8 requeries is then pure floor. Reported per position and summed over a
  committed image set of 32 positions, as a function of H(mbar). The card's G1b compares ONE median floor with "5 percent
  of the smallest S_theta value used in any comparison" (8.7), not a floor per entropy level.
Part 2. Matched-minus-shuffled lift against content diversity at FIXED pair consistency.
  Synthetic embeddings: topic vectors around a common direction (concentration c sets diversity); image and caption of a
  pair share the topic with probability a (consistency); a fixed modality offset puts cross-modal cosines near CLIP's scale.
  Shows how much the card's Lift moves when diversity changes but a does not, next to the change in mean pairwise image
  cosine, which is what guardrail (ii) bounds at 0.05 (7.2).
"""
import numpy as np

rng = np.random.default_rng(7)


def to_bf16(x):
    x = np.ascontiguousarray(x, dtype=np.float32)
    b = x.view(np.uint32).astype(np.uint64)
    lsb = (b >> 16) & 1
    b = ((b + 0x7FFF + lsb) & 0xFFFF0000).astype(np.uint32)
    return b.view(np.float32)


def log_softmax(z):
    z = z - z.max()
    return z - np.log(np.exp(z).sum())


def kl(p, q):
    m = p > 0
    return float((p[m] * (np.log(p[m]) - np.log(q[m]))).sum())


V, R = 16384, 8
print("Part 1: pure numerical floor of the mixture estimator (no dependence by construction)")
print("  s       scale   H(mbar)  TV(two requeries)  I_hat per position   x 32 positions (committed set)")
for s in (0.005, 0.01, 0.02):
    for scale in (0.5, 1.5, 3.0, 5.0):
        Ihs, Hs, tvs = [], [], []
        for _ in range(6):
            l = rng.standard_normal(V) * scale
            ms = []
            for r in range(R):
                lp = to_bf16(log_softmax(l + rng.standard_normal(V) * s)).astype(np.float64)
                p = np.exp(lp)
                ms.append(p / p.sum())
            ms = np.array(ms)
            mbar = ms.mean(0)
            Ihs.append(np.mean([kl(m, mbar) for m in ms]))
            Hs.append(-(mbar * np.log(mbar)).sum())
            tvs.append(0.5 * np.abs(ms[0] - ms[1]).sum())
        print(f"  {s:.3f}   {scale:4.1f}   {np.mean(Hs):6.2f}     {np.mean(tvs):.4f}            {np.mean(Ihs):.2e}"
              f"           {32 * np.mean(Ihs):.2e}")

print("\nPart 2: lift (100 x cosine) at fixed pair consistency a, varying topic diversity (concentration c)")
d, n = 256, 500
gap = rng.standard_normal(d)
gap /= np.linalg.norm(gap)
mu = rng.standard_normal(d)
mu /= np.linalg.norm(mu)


def cell(a, c, n=n):
    topics = mu[None, :] * c + rng.standard_normal((n, d)) / np.sqrt(d)
    topics /= np.linalg.norm(topics, axis=1, keepdims=True)
    same = rng.random(n) < a
    other = topics[rng.permutation(n)]
    t_txt = np.where(same[:, None], topics, other)
    eI = 0.6 * topics + 0.6 * gap + rng.standard_normal((n, d)) * 0.9 / np.sqrt(d)
    eT = 0.6 * t_txt - 0.6 * gap + rng.standard_normal((n, d)) * 0.9 / np.sqrt(d)
    eI /= np.linalg.norm(eI, axis=1, keepdims=True)
    eT /= np.linalg.norm(eT, axis=1, keepdims=True)
    S = eI @ eT.T
    C = np.diag(S)
    off = (S.sum(1) - C) / (n - 1)
    offc = (S.sum(0) - C) / (n - 1)
    lift = 100 * (C - 0.5 * (off + offc))
    G = eI @ eI.T
    pairI = (G.sum() - n) / (n * (n - 1))
    return lift.mean(), 100 * C.mean(), pairI


print("  a     c     Lift    raw matched (100 C)   mean pairwise image cosine")
base = None
for a, c in [(0.6, 1.0), (0.6, 0.9), (0.6, 0.8), (0.55, 0.8), (0.55, 0.7), (0.5, 0.6)]:
    res = np.mean([cell(a, c) for _ in range(20)], axis=0)
    if base is None:
        base = res
    print(f"  {a:.2f}  {c:.2f}  {res[0]:6.2f}   {res[1]:6.2f}                 {res[2]:.3f}    "
          f"(vs first row: dLift {res[0] - base[0]:+.2f}, d image cosine {res[2] - base[2]:+.3f})")
