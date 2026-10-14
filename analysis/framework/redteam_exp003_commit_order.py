"""Red-team EXP-003: CPU-only reconstruction of the official maskgit schedule and a crude Monte Carlo of
when the 32 tail tokens are committed relative to the 1024 image tokens.
Assumptions (stated, not measured here): -log p(sampled token) ~ Gamma(shape 2, mean = entropy); entropies from
runs/env-2026-10-14/setup.md 2.1 b (text 5.0, image 6.5 nats, one state). Entropy would change during decoding; this
is a sensitivity sketch, not evidence. Gumbel scale r_temp*t as in _maskgit_update (r_temp 4.5, t from 1 to ~0)."""
import math, numpy as np, sys

def adap_sche(seq_len, step):
    r = np.linspace(1, 0, step)
    v = np.arccos(r) / (math.pi * 0.5)
    s = np.round(v / v.sum() * seq_len)
    s[s == 0] = 1
    s[-1] += seq_len - s.sum()
    s[-1] = max(s[-1], 0)
    return s.astype(int)

def sim(steps, n_txt=32, n_img=1024, Ht=5.0, Hi=6.5, r_temp=4.5, reps=300, seed=0):
    rng = np.random.default_rng(seed)
    sch = adap_sche(n_txt + n_img, steps)
    tl = np.linspace(1, 1e-5, steps + 1)[:steps]
    res = []
    for _ in range(reps):
        masked = np.ones(n_txt + n_img, bool)
        is_t = np.arange(n_txt + n_img) < n_txt
        when = np.zeros(n_txt + n_img)
        for i in range(steps):
            k = min(sch[i], masked.sum())
            if k <= 0: continue
            nl = np.where(is_t, rng.gamma(2, Ht / 2, size=is_t.size), rng.gamma(2, Hi / 2, size=is_t.size))
            conf = -nl + r_temp * rng.gumbel(size=is_t.size) * tl[i]
            conf[~masked] = -np.inf
            idx = np.argpartition(-conf, k - 1)[:k]
            masked[idx] = False
            when[idx] = (i + 1) / steps
        # fraction of the tail committed before 25% of image tokens committed
        img_t = np.sort(when[~is_t]); t25 = img_t[int(0.25 * len(img_t))]
        res.append((when[is_t].mean(), when[~is_t].mean(), (when[is_t] < t25).mean(), (when[is_t] <= img_t[-1] * 0 + when[~is_t].min()).mean()))
    return np.array(res).mean(0)

if __name__ == "__main__":
    for st in (32, 50):
        s = adap_sche(1056, st)
        print("steps", st, "tokens per step first 6", s[:6].tolist(), "last 6", s[-6:].tolist(), "max", s.max(), "sum", s.sum())
    print("uniform P64 tokens per pass", 1056 / 64, " P32", 1056 / 32)
    for Ht, Hi in ((5.0, 6.5), (6.5, 6.5), (4.0, 7.0)):
        m = sim(32, Ht=Ht, Hi=Hi)
        print(f"Ht={Ht} Hi={Hi}: mean normalised commit time tail {m[0]:.3f} image {m[1]:.3f}; share of tail committed before 25% of image {m[2]:.3f}")
