"""Red-team EXP-003: can Lambda_d (EXP-003 section 4.1) be positive with ZERO noun-specific text-image link?
Toy model, CPU only. Each sample has a latent quality z (shared by its own text and its own image, independent across
seeds). Text richness (number of nouns drawn from a per-prefix vocabulary of V equiprobable nouns) rises with z; the
probability that the VLM says yes to ANY noun on the image (a detectability / yes-bias term) rises with z. A noun's
identity never influences the image. Lambda_d is computed exactly as the card defines it (ratio of sums over
discordant nouns, own minus sibling image)."""
import numpy as np
def lam(c_text, b_img, n=20000, V=25, base_nouns=3.0, a=-0.5, seed=1):
    rng = np.random.default_rng(seed); num = 0.0; den = 0
    for _ in range(n):
        z = rng.normal(size=2)
        k = [rng.poisson(base_nouns * np.exp(c_text * zz)) for zz in z]
        N = [set(rng.choice(V, size=min(kk, V), replace=False).tolist()) for kk in k]
        py = [1 / (1 + np.exp(-(a + b_img * zz))) for zz in z]
        for e in (0, 1):
            D = N[e] - N[1 - e]
            for _n in D:
                num += rng.binomial(1, py[e]) - rng.binomial(1, py[1 - e]); den += 1
    return num / den, den
if __name__ == "__main__":
    for c, b in ((0, 0), (0.5, 0), (0, 1.0), (0.3, 1.0), (0.5, 1.0), (0.5, 2.0)):
        L, d = lam(c, b); print(f"text-richness coupling {c}, image-detectability slope {b}: Lambda_d = {L:+.3f} ({d} discordant nouns)")
