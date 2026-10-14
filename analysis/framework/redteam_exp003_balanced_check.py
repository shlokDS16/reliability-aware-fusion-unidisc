"""Red-team EXP-003 v0.2 check (CPU only). Re-runs the quality-coupling toy with the v0.2 seed-balanced link Lambda_b
and the placebo-noun control (NC-2). Nouns have a per-noun detectability d_n; a sample has latent quality z shared by its
own text (richness, and which nouns are mentioned) and its own image (yes-probability). Scenarios:
 add  : yes-prob = sigmoid(a + b z)                       (additive image-level bias, as v0.1 toy)
 inter: yes-prob = sigmoid(a + b z + c z d_n), and quality shifts which nouns are mentioned (non-additive)
 link : additive scenario plus a true noun-specific boost l when the noun is in the own text
Statistics: Lambda_d (v0.1 ratio), Lambda_b (v0.2), Lambda_b_plac (placebo nouns from the discordant set of the next prefix,
same counts, absent from both completions' keys)."""
import numpy as np
rng = np.random.default_rng(7)
V = 60; d = rng.normal(size=V)
sig = lambda x: 1 / (1 + np.exp(-x))
def run(n, c_text, b, c_int=0.0, g=0.0, l=0.0, a=-0.5, vp=25):
    Ls = []; Lp = []; num = den = 0.0
    data = []
    for p in range(n):
        vocab = rng.choice(V, vp, replace=False)
        z = rng.normal(size=2)
        N = []
        for e in range(2):
            k = min(rng.poisson(3 * np.exp(c_text * z[e])), vp)
            w = np.exp(g * z[e] * d[vocab]); w /= w.sum()
            N.append(set(rng.choice(vocab, size=k, replace=False, p=w).tolist()))
        data.append((z, N))
    def y(n_, zz, own):  # n_ noun id
        return rng.binomial(1, sig(a + b * zz + c_int * zz * d[n_] + (l if own else 0)))
    D = [(N[0] - N[1], N[1] - N[0]) for z, N in data]
    for p, (z, N) in enumerate(data):
        for e in range(2):
            for n_ in D[p][e]:
                num += y(n_, z[e], True) - y(n_, z[1 - e], False); den += 1
        if D[p][0] and D[p][1]:
            t = []
            for e in range(2):
                t.append(np.mean([y(n_, z[e], True) - y(n_, z[1 - e], False) for n_ in D[p][e]]))
            Ls.append(0.5 * (t[0] + t[1]))
            q = (p + 1) % n
            pool = sorted((D[q][0] | D[q][1]) - N[0] - N[1])
            t = []
            for e in range(2):
                m = len(D[p][e]); pick = rng.choice(pool, size=min(m, len(pool)), replace=False) if pool else []
                t.append(np.mean([y(n_, z[e], False) - y(n_, z[1 - e], False) for n_ in pick]) if len(pick) else np.nan)
            if not np.isnan(t).any(): Lp.append(0.5 * (t[0] + t[1]))
    se = lambda x: np.std(x) / np.sqrt(len(x))
    return num / den, np.mean(Ls), se(Ls), len(Ls), np.mean(Lp), se(Lp)
if __name__ == "__main__":
    sc = {"no coupling":dict(c_text=0,b=0), "add c=.5 b=1":dict(c_text=.5,b=1), "add c=.5 b=2":dict(c_text=.5,b=2),
          "inter b=1 cint=1 g=.5":dict(c_text=.5,b=1,c_int=1.0,g=.5), "inter b=1 cint=2 g=1":dict(c_text=.5,b=1,c_int=2.0,g=1.0),
          "inter b=0 cint=2 g=1":dict(c_text=.5,b=0,c_int=2.0,g=1.0),
          "true link .15, add c=.5 b=1":dict(c_text=.5,b=1,l=.6)}
    for k, v in sc.items():
        ld, lb, s, ne, lp, sp = run(12000, **v)
        print(f"{k:32s} Lambda_d {ld:+.3f} | Lambda_b {lb:+.3f} (se {s:.3f}, eligible {ne}) | placebo {lp:+.3f} (se {sp:.3f})")
