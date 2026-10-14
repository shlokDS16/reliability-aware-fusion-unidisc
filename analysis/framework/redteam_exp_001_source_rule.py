"""Red-team round 3 check for EXP-001 v0.4, CPU only, synthetic. No GPU, no model.

Question: does the v0.4 plan-independent T->I source rule (a* = still-masked tail position with index <= L_c, not
state-pad, largest max_v p1_j(v); card section 2) produce an early/late ratio that reflects WHICH token it picks rather
than how the model's dependence changes with time, and do the "source-limited" label (early mean H_src below half of
the late mean) and R_Q2 catch it?

Synthetic tail model (all [A]): 32 tail positions; completion length Lcomp ~ U{6..12}; L_c = 12. Position 1 is the
open noun slot; positions 2..Lcomp are nouns with probability 0.25, otherwise function/other words. The two positions
before the caption end carry an uncertain pad mass w ~ U(0.10, 0.45) (the model is unsure where the caption ends);
position Lcomp+1 has w ~ U(0.30, 0.70); later positions w = 0.95 (state-pad). 80 percent of the pad mass sits on id 0,
so a position's max_v p1_j(v) = max(0.8 w, (1 - w) p_top). Content class: top token p_top (nouns Beta(2,5), function
words Beta(5,2) or Beta(2,2) in variant "fw_uncertain"), the rest over a Zipf(200, 1.1) tail.
Within-content dependence of the image on a source a: I_c = (1 - w) kappa_type H_content(a), i.e. a fixed fraction of
the source's content entropy; H_src = (1 - w) H_content (card section 2, R_Q2). Receivers are not modelled: every
receiver shares the source, so the per-position mean scales with I_c, and R_Q2 with I_c / H_src when H_src binds.

Scenarios:
  static   - marginals do not change over the trajectory (no dynamics at any fixed position; true ratio 1 everywhere)
  sharpen  - content marginals sharpen as the image is committed: residual mass (1 - p_top) shrinks by (1 - s t / 32),
             s = 0.7 nouns, 0.3 function words; dependence per unit of entropy is constant (kappa fixed), so the
             per-entropy truth is 1 and the nats truth at a fixed position is H(early) / H(late) > 1
kappa: "typed" (noun 0.30, function 0.05: H-A2's own premise, nouns carry more information per nat) or "flat" (0.15).
Position rules: P (confidence ranking: commit the masked text position with the largest max-marginal, 1 per pass at k0)
and R (uniformly random order). Probes at passes 2, 6 (early) and 26, 30 (late); state = passes 1..p-1 committed.
Statistics as in the card: raw ratio of pooled means of I_c (probes with a source only), R_Q2 = ratio of
[sum I_c / sum H_src], source-limited label iff mean H_src(early) < 0.5 mean H_src(late).
Part 2: exact source availability under condition R (hypergeometric, ignoring state-pad, i.e. an upper bound).
Part 3: the guard gap, arithmetic.
"""
import numpy as np
from math import comb

rng = np.random.default_rng(20261014)
T, L_C, PASSES, PROBES = 32, 12, 32, (2, 6, 26, 30)

z = 1.0 / np.arange(1, 201) ** 1.1
z /= z.sum()
H_ZIPF = float(-(z * np.log(z)).sum())


def h_content(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -p * np.log(p) - (1 - p) * np.log(1 - p) + (1 - p) * H_ZIPF


def make_traj(fw_uncertain):
    L = int(rng.integers(6, 13))
    w = np.full(T, 0.95)
    w[:L] = 0.02
    w[max(L - 2, 1):L] = rng.uniform(0.10, 0.45, size=L - max(L - 2, 1))
    w[L] = rng.uniform(0.30, 0.70)
    noun = np.zeros(T, bool)
    noun[0] = True
    noun[1:L] = rng.random(L - 1) < 0.25
    p_top = np.where(noun, rng.beta(2, 5, T), rng.beta(2, 2, T) if fw_uncertain else rng.beta(5, 2, T))
    p_top[L + 1:] = 0.5  # irrelevant: state-pad positions are never sources
    boundary = w >= 0.10
    boundary[L + 1:] = False
    return L, w, noun, p_top, boundary


def run(scenario, kappa_mode, rule, fw_uncertain=False, n=5000, front=1.0):
    acc = {p: dict(avail=0, I=0.0, H=0.0, noun=0, bnd=0) for p in PROBES}
    for _ in range(n):
        L, w, noun, p0, bnd = make_traj(fw_uncertain)
        kap = np.where(noun, 0.30, 0.05) if kappa_mode == "typed" else np.full(T, 0.15)
        masked = np.ones(T, bool)
        order = rng.permutation(T) if rule == "R" else None
        for t in range(1, PASSES + 1):
            if scenario == "sharpen":
                s = np.where(noun, 0.7, 0.3)
                p = 1 - (1 - p0) * (1 - s * (t - 1) / PASSES)
            else:
                p = p0
            if t in PROBES:
                cand = masked.copy()
                cand[L_C:] = False
                cand &= w < 0.5
                if cand.any():
                    mm = np.maximum(0.8 * w, (1 - w) * p)
                    mm = np.where(cand, mm, -1.0)
                    a = int(np.argmax(mm))  # ties: lowest index
                    hs = (1 - w[a]) * h_content(p[a])
                    f = front if t in (2, 6) else 1.0
                    rec = acc[t]
                    rec["avail"] += 1
                    rec["I"] += f * kap[a] * hs
                    rec["H"] += hs
                    rec["noun"] += int(noun[a])
                    rec["bnd"] += int(bnd[a])
            # commit one text token
            if rule == "R":
                j = next(k for k in order if masked[k])
            else:
                mm_all = np.where(masked, np.maximum(0.8 * w, (1 - w) * p), -1.0)
                j = int(np.argmax(mm_all))
            masked[j] = False
    out = {}
    for t in PROBES:
        r = acc[t]
        k = max(r["avail"], 1)
        out[t] = (r["avail"] / n, r["noun"] / k, r["bnd"] / k, r["H"] / k, r["I"] / k)
    e = [out[2], out[6]]
    l = [out[26], out[30]]
    # pooled over probes with a source (weights = availability)
    def pooled(rows, idx):
        num = sum(rw[0] * rw[idx] for rw in rows)
        den = sum(rw[0] for rw in rows)
        return num / den
    raw = pooled(e, 4) / pooled(l, 4)
    hratio = pooled(e, 3) / pooled(l, 3)
    rq2 = (pooled(e, 4) / pooled(e, 3)) / (pooled(l, 4) / pooled(l, 3))
    return out, raw, hratio, rq2


print(f"H_ZIPF = {H_ZIPF:.3f} nats; L_c = {L_C}")
print("Part 1. Source composition and ratios (n = 5,000 synthetic trajectories per row)")
hdr = "scenario kappa  rule fw_unc front | per probe p: avail noun_share boundary_share mean_H_src | raw  H_src(e/l) R_Q2 label"
print(hdr)
for scen in ("static", "sharpen"):
    for kap in ("typed", "flat"):
        for rule in ("P", "R"):
            for fwu in (False, True):
                for front in (1.0, 1.75):
                    if fwu and front != 1.0:
                        continue
                    out, raw, hr, rq2 = run(scen, kap, rule, fwu, front=front)
                    per = " ".join(f"p{t}:{o[0]:.2f}/{o[1]:.2f}/{o[2]:.2f}/{o[3]:.2f}" for t, o in out.items())
                    lab = "source-limited" if hr < 0.5 else "-"
                    print(f"{scen:8s} {kap:5s} {rule:4s} {str(fwu):6s} {front:4.2f} | {per} | {raw:.2f} {hr:.2f} {rq2:.2f} {lab}")

print()
print("Part 2. Condition R: P(at least one still-masked tail position with index <= L_c) at a probe, exact")
print("hypergeometric over a uniformly random commit order, 1 text token per pass at k0, ignoring state-pad (upper bound)")
for lc in (8, 12, 16):
    row = []
    for p in PROBES:
        m = T - (p - 1)
        p_none = comb(T - lc, m) / comb(T, m) if m <= T - lc else 0.0
        row.append(f"pass {p} (masked {m}): {1 - p_none:.3f}")
    print(f"L_c = {lc:2d}: " + "; ".join(row))

print()
print("Part 3. Guard gap: if I_c scales with H_src, raw ratio = rho_true x h, h = H_src(early)/H_src(late).")
print("Label fires only for h < 0.5. Range of h with raw < 1.5 (weak-falsification region) and no label:")
for rho in (1.5, 1.75, 2.0, 2.5, 3.0):
    hi = 1.5 / rho
    print(f"rho_true = {rho:4.2f}: h in [0.50, {hi:.3f}) -> raw in [{0.5 * rho:.2f}, 1.50), no source-limited label"
          if hi > 0.5 else f"rho_true = {rho:4.2f}: no gap")
