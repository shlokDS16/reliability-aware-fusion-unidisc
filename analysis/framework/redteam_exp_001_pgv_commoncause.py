"""Red-team round 2 check for EXP-001 v0.3 PG-V (4.4), CPU only, synthetic.

Question: can PG-V pass when the generated completion and the generated image share NO dependence beyond the observed
prefix, i.e. completion nouns and image objects are drawn independently given the prefix (common cause only)?

Model: 48 seeds, each with its own prefix (as in pool PG). Each prefix k has, for each of n_slots open noun slots
(object slot, scene slot), a prefix-conditional distribution over candidates: top candidate with probability p_top, the
rest spread over C - 1 alternatives. The completion draws one noun per slot; the image independently draws one object per
slot from the SAME prefix-conditional law (conditional independence given the prefix). Candidate sets of different
prefixes overlap with probability `overlap` per candidate (generic nouns such as man, table, street). A perfect checker
answers yes iff the noun is in the image. presence = at least one completion noun found (the card's rule).
m = matched rate, s = mean over 4 derangements, gate = (m >= 0.50) and (m - s >= 0.25) (criterion (a) assumed met).
Also reported: the same-prefix shuffle s_sp (partner = another seed with the SAME prefix), which is the rate under
conditional independence and so isolates co-generation dependence.
"""
import numpy as np

rng = np.random.default_rng(2026)
n, C, reps = 48, 6, 1500


def run(p_top, n_slots, overlap, dep):
    """dep = probability that the image copies the completion's choice per slot (0 = common cause only)."""
    passes, ms, ss, ssp = 0, [], [], []
    for _ in range(reps):
        # candidate ids per prefix and slot; generic overlap via a shared pool
        cand = rng.integers(0, 10_000, size=(n, n_slots, C))
        shared = rng.random((n, n_slots, C)) < overlap
        cand = np.where(shared, rng.integers(0, 20, size=(n, n_slots, C)), cand)
        probs = np.full(C, (1 - p_top) / (C - 1))
        probs[0] = p_top

        def draw():
            idx = np.array([[rng.choice(C, p=probs) for _ in range(n_slots)] for _ in range(n)])
            return np.take_along_axis(cand, idx[..., None], 2)[..., 0]

        noun = draw()
        img = draw()
        copy = rng.random((n, n_slots)) < dep
        img = np.where(copy, noun, img)
        img2 = draw()  # a second image from the same prefix (same-prefix partner), same dependence rule on its own caption
        pres = lambda nn, ii: np.array([np.isin(nn[i], ii[i]).any() for i in range(n)])
        m = pres(noun, img).mean()
        s = np.mean([pres(noun, img[np.roll(np.arange(n), r)]).mean() for r in (1, 7, 13, 29)])
        s_sp = pres(noun, img2).mean()
        ms.append(m); ss.append(s); ssp.append(s_sp)
        passes += (m >= 0.5) and (m - s >= 0.25)
    return np.mean(ms), np.mean(ss), np.mean(ssp), passes / reps


print("p_top slots overlap dep |  m      s      s_same_prefix  P(PG-V passes)")
for p_top, slots, ov, dep in [(0.5, 1, 0.1, 0.0), (0.6, 2, 0.1, 0.0), (0.7, 2, 0.2, 0.0), (0.8, 1, 0.1, 0.0),
                              (0.4, 2, 0.1, 0.0), (0.4, 2, 0.1, 0.5), (0.6, 2, 0.1, 0.5)]:
    m, s, ssp, pp = run(p_top, slots, ov, dep)
    print(f" {p_top:.1f}   {slots}     {ov:.1f}   {dep:.1f} | {m:.3f}  {s:.3f}  {ssp:.3f}          {pp:.3f}")
