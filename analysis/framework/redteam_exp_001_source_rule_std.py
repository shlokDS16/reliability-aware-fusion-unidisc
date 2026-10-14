"""Red-team v0.5 paragraph check for EXP-001, CPU only, synthetic. No GPU, no model.

Question: does the v0.5 composition-standardised early/late ratio (card section 2 (b)-(f); strata object noun / other
content / function, fixed weights = pooled stratum shares over the four centre probes, thin-stratum rule, complete-case
pair, Negative only if both standardised ratios AND R_Q2 fail) remove the source-composition artefact of R3-F1 in the
synthetic tail model of redteam_exp_001_source_rule.py?

Model as in redteam_exp_001_source_rule.py, with a third token type. Positions 2..Lcomp: noun 0.25, other content
0.25, function 0.50 (position 1 is the noun slot). p_top: noun Beta(2,5), other Beta(3,3), function Beta(5,2).
kappa (within-content dependence per nat of source content entropy): "typed" noun 0.30, other 0.15, function 0.05;
"flat" 0.15 for all. Sharpening rates s: noun 0.7, other 0.5, function 0.3. Sources at post-caption positions are
excluded (card 2 (b)). Truth: every source's dependence per nat is multiplied by `front` at the early probes, so the
target of a valid statistic is `front` (1.0 = no front-loading, 1.75 = above the MEI of 1.5).
Observation noise: I_obs = I x lognormal with cv 0.8 (mean 1), independent per probe [A].
Large-sample point values from a pool of 12,000 trajectories; decision rates from 400 replicate studies of n = 256
trajectories drawn from the pool; a replicate's 95 percent limits are approximated by estimate -/+ 1.96 x the SD of
that statistic across replicates (a normal approximation to the card's percentile bootstrap).
"""
import numpy as np

rng = np.random.default_rng(20261015)
T, L_C, PASSES, PROBES = 32, 12, 32, (2, 6, 26, 30)
EARLY, LATE = (0, 1), (2, 3)
z = 1.0 / np.arange(1, 201) ** 1.1
z /= z.sum()
H_ZIPF = float(-(z * np.log(z)).sum())
SIG = np.sqrt(np.log(1 + 0.8 ** 2))


def h_content(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -p * np.log(p) - (1 - p) * np.log(1 - p) + (1 - p) * H_ZIPF


def make_traj():
    L = int(rng.integers(6, 13))
    w = np.full(T, 0.95)
    w[:L] = 0.02
    w[max(L - 2, 1):L] = rng.uniform(0.10, 0.45, size=L - max(L - 2, 1))
    w[L] = rng.uniform(0.30, 0.70)
    typ = np.full(T, 2)
    typ[1:L] = rng.choice(3, size=L - 1, p=[0.25, 0.25, 0.50])
    typ[0] = 0
    a = np.array([2, 3, 5])[typ]
    b = np.array([5, 3, 2])[typ]
    p_top = rng.beta(a, b)
    return L, w, typ, p_top


def pool(scenario, rule, n):
    """Per trajectory and probe: avail (bool), type, H_src, base I per kappa unit (I/kappa)."""
    av = np.zeros((n, 4), bool)
    ty = np.full((n, 4), -1)
    hs = np.zeros((n, 4))
    for i in range(n):
        L, w, typ, p0 = make_traj()
        s = np.array([0.7, 0.5, 0.3])[typ]
        masked = np.ones(T, bool)
        order = rng.permutation(T) if rule == "R" else None
        for t in range(1, PASSES + 1):
            p = 1 - (1 - p0) * (1 - s * (t - 1) / PASSES) if scenario == "sharpen" else p0
            if t in PROBES:
                k = PROBES.index(t)
                cand = masked.copy()
                cand[L_C:] = False
                cand &= w < 0.5
                if cand.any():
                    mm = np.where(cand, np.maximum(0.8 * w, (1 - w) * p), -1.0)
                    a = int(np.argmax(mm))
                    if a < L:  # post-caption sources excluded from the strata
                        av[i, k] = True
                        ty[i, k] = typ[a]
                        hs[i, k] = (1 - w[a]) * h_content(p[a])
            if rule == "R":
                j = next(q for q in order if masked[q])
            else:
                j = int(np.argmax(np.where(masked, np.maximum(0.8 * w, (1 - w) * p), -1.0)))
            masked[j] = False
    return av, ty, hs


def stats(av, ty, I, hs, complete_case=False):
    if complete_case:
        keep = av.all(axis=1)
        av, ty, I, hs = av[keep], ty[keep], I[keep], hs[keep]
    obs = av.sum()
    omega = np.array([(ty[av] == s).sum() / max(obs, 1) for s in range(3)])
    thin = False
    num = den = 0.0
    for s in range(3):
        e = av[:, EARLY] & (ty[:, EARLY] == s)
        l = av[:, LATE] & (ty[:, LATE] == s)
        ne, nl = e.sum(), l.sum()
        if omega[s] >= 0.10 and (ne < 20 or nl < 20):
            thin = True
        if ne > 0 and nl > 0:
            num += omega[s] * I[:, EARLY][e].mean()
            den += omega[s] * I[:, LATE][l].mean()
    std = num / den if den > 0 else np.nan
    ae, al = av[:, EARLY], av[:, LATE]
    raw = I[:, EARLY][ae].mean() / I[:, LATE][al].mean()
    rq2 = (I[:, EARLY][ae].sum() / hs[:, EARLY][ae].sum()) / (I[:, LATE][al].sum() / hs[:, LATE][al].sum())
    return std, raw, rq2, thin


def run(scenario, kappa_mode, rule, front, base):
    av, ty, hs = base
    kap = {"typed": np.array([0.30, 0.15, 0.05]), "flat": np.array([0.15, 0.15, 0.15])}[kappa_mode]
    k_arr = np.where(ty >= 0, kap[np.clip(ty, 0, 2)], 0.0)
    mult = np.array([front, front, 1.0, 1.0])
    I_true = k_arr * hs * mult
    noise = rng.lognormal(-SIG ** 2 / 2, SIG, size=I_true.shape)
    I = I_true * noise
    big = stats(av, ty, I_true, hs)
    big_cc = stats(av, ty, I_true, hs, complete_case=True)
    n_e = av[:, EARLY].sum()
    nounshare = lambda cols: (ty[:, cols][av[:, cols]] == 0).mean()
    h = hs[:, EARLY][av[:, EARLY]].mean() / hs[:, LATE][av[:, LATE]].mean()
    reps = []
    N = av.shape[0]
    for _ in range(400):
        idx = rng.integers(0, N, 256)
        r1 = stats(av[idx], ty[idx], I[idx], hs[idx])
        r2 = stats(av[idx], ty[idx], I[idx], hs[idx], complete_case=True)
        reps.append((r1[0], r2[0], r1[2], r1[3] or r2[3]))
    reps = np.array(reps, dtype=float)
    sd = np.nanstd(reps[:, :3], axis=0)
    est = reps[:, :3]
    lo, hi = est - 1.96 * sd, est + 1.96 * sd
    thin = reps[:, 3] > 0
    support = (~thin) & (lo[:, 0] >= 1.5) & (lo[:, 1] >= 1.5)
    negative = (~thin) & (hi[:, 0] < 1.5) & (hi[:, 1] < 1.5) & (hi[:, 2] < 1.5)
    return (nounshare(list(EARLY)), nounshare(list(LATE)), h, big[1], big[0], big_cc[0], big[2],
            thin.mean(), support.mean(), negative.mean())


print(f"H_ZIPF = {H_ZIPF:.3f}; L_c = {L_C}; noise cv 0.8; pool 12,000; 400 studies of n = 256")
print("scen    kappa rule front | noun_e noun_l  h    | raw   std   std_cc RQ2  (large sample) | P(thin) P(support) P(Negative)")
for scen in ("static", "sharpen"):
    for rule in ("P", "R"):
        base = pool(scen, rule, 12000)
        for kap in ("typed", "flat"):
            for front in (1.0, 1.75):
                r = run(scen, kap, rule, front, base)
                print(f"{scen:7s} {kap:5s} {rule:4s} {front:4.2f}  | {r[0]:.3f}  {r[1]:.3f}  {r[2]:.2f} | "
                      f"{r[3]:.2f}  {r[4]:.2f}  {r[5]:.2f}   {r[6]:.2f}                 | {r[7]:.2f}    {r[8]:.2f}       {r[9]:.2f}")
