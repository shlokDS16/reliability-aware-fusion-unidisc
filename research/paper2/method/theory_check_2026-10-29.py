"""Numerical checks for research/paper2/method/THEORY-ADDENDUM-2026-10-29.md (CPU only, small Monte Carlo).

Every parameter value below is ILLUSTRATIVE (chosen to exercise the algebra), not an estimate from any run.
No file under runs/ is read. exp_p2/gate/theory.py is imported read-only, to check that the new formulas reduce to it.

Sections
  A  Proposition 1 (detectability limit): AUROC-TV bounds, sharpness, LR optimality, toy sequence model with
     Gibbs (law-invariant) corruption, changed-code label bound, cross-modal corollary.
  B  Proposition 2 (correlated-token SNR of hard gating): Lemma 1 by Monte Carlo, reduction to theory.py, closed form,
     frontier boundary and its direction, conditional-on-flags variant, large-m limit.
  C  Proposition 3 (soft weights): Lemma 2 by Monte Carlo, optimal weights (matched filter; non-negative with
     correlation = soft threshold), clean-pair efficiency of conformal p-value weights.
Run:  python research/paper2/method/theory_check_2026-10-29.py
"""
from __future__ import annotations

import itertools
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "exp_p2", "gate"))
import theory as T  # noqa: E402  (read-only import of the pinned module)

SEED = 20261029
FAILS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        FAILS.append(name)


# ----------------------------------------------------------------------------------------------------------------------
# helpers: exact AUROC for discrete laws, empirical AUROC with mid-ranks
# ----------------------------------------------------------------------------------------------------------------------
def auroc_discrete(scores: np.ndarray, q1: np.ndarray, q0: np.ndarray) -> float:
    """AUROC = P(f(X1) > f(X0)) + 0.5 P(=), X1 ~ q1, X0 ~ q0 independent, on a finite support."""
    gt = (scores[:, None] > scores[None, :]).astype(float)
    eq = (scores[:, None] == scores[None, :]).astype(float)
    return float(q1 @ (gt + 0.5 * eq) @ q0)


def exact_auroc_atoms(score: np.ndarray, w1: np.ndarray, w0: np.ndarray) -> float:
    """Exact mid-rank AUROC for weighted atoms: positives with weights w1, negatives with weights w0 (each normalised)."""
    w1 = w1 / w1.sum(); w0 = w0 / w0.sum()
    uniq, inv = np.unique(score, return_inverse=True)
    a1 = np.bincount(inv, w1, minlength=uniq.size); a0 = np.bincount(inv, w0, minlength=uniq.size)
    return float((a1 * (np.cumsum(a0) - a0)).sum() + 0.5 * (a1 * a0).sum())


def auroc_empirical(score: np.ndarray, label: np.ndarray) -> float:
    from scipy.stats import rankdata
    r = rankdata(score)  # mid-ranks
    n1 = int(label.sum()); n0 = label.size - n1
    return float((r[label.astype(bool)].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


# ======================================================================================================================
# A. Proposition 1
# ======================================================================================================================
def section_A() -> None:
    print("\n=== A. Proposition 1: detectability limit ===")
    rng = np.random.default_rng(SEED)

    # A1: bounds 1/2 + v/2 <= sup_f AUROC = AUROC(LR) <= 1/2 + v - v^2/2, and |AUROC(f) - 1/2| <= v - v^2/2 for all f
    worst_up, worst_lr, worst_lo = -1.0, -1.0, -1.0
    for _ in range(3000):
        k = int(rng.integers(2, 8))
        q1 = rng.dirichlet(np.full(k, rng.uniform(0.2, 3)))
        q0 = rng.dirichlet(np.full(k, rng.uniform(0.2, 3)))
        v = 0.5 * np.abs(q1 - q0).sum()
        ub = 0.5 + v - v * v / 2
        lr = np.log(q1 + 1e-300) - np.log(q0 + 1e-300)
        a_lr = auroc_discrete(lr, q1, q0)
        for _r in range(5):
            f = rng.integers(0, 4, size=k).astype(float) if _r % 2 else rng.normal(size=k)
            a = auroc_discrete(f, q1, q0)
            worst_up = max(worst_up, abs(a - 0.5) - (v - v * v / 2))
            worst_lr = max(worst_lr, a - a_lr)
        worst_lo = max(worst_lo, (0.5 + v / 2) - a_lr)
        worst_up = max(worst_up, abs(a_lr - 0.5) - (v - v * v / 2))
    check("A1 |AUROC(f)-1/2| <= v - v^2/2 for random laws and scores", worst_up <= 1e-12, f"max excess {worst_up:.2e}")
    check("A1 AUROC(LR) >= AUROC(f) (LR is AUROC-optimal)", worst_lr <= 1e-12, f"max excess {worst_lr:.2e}")
    check("A1 AUROC(LR) >= 1/2 + v/2", worst_lo <= 1e-12, f"max shortfall {worst_lo:.2e}")

    # A2: sharpness, three-point example q1 = (0, 1-v, v), q0 = (v, 1-v, 0), score = identity
    errs = []
    for v in np.linspace(0.0, 1.0, 11):
        q1 = np.array([0.0, 1 - v, v]); q0 = np.array([v, 1 - v, 0.0])
        errs.append(abs(auroc_discrete(np.array([0.0, 1.0, 2.0]), q1, q0) - (0.5 + v - v * v / 2)))
    check("A2 bound attained by the three-point example", max(errs) < 1e-12, f"max |err| {max(errs):.1e}")

    # A3: toy within-modality model. Caption c in {0,1}; image v = Markov chain of length L over V codes, law depends on c.
    V, L = 3, 8
    shape = (V,) * L
    P_c = []
    for c in range(2):
        init = rng.dirichlet(np.ones(V) * 2)
        Tm = rng.dirichlet(np.ones(V) * (0.6 if c == 0 else 1.5), size=V)
        Tm = 0.5 * Tm + 0.5 * np.roll(np.eye(V), c + 1, axis=1)  # caption changes the dominant transition
        Tm /= Tm.sum(1, keepdims=True)
        p = np.zeros(shape)
        for seq in itertools.product(range(V), repeat=L):
            pr = init[seq[0]]
            for a_, b_ in zip(seq[:-1], seq[1:]):
                pr *= Tm[a_, b_]
            p[seq] = pr
        P_c.append(p)
    P_c = np.stack(P_c)            # (2, V^L) joint given caption
    P_a = 0.5 * P_c[0] + 0.5 * P_c[1]  # image marginal (caption withheld): the law that within-modality scores see
    flatP = P_a.reshape(-1)
    pw = V ** np.arange(L - 1, -1, -1)  # base-V place values, position 0 most significant

    def full_cond(table: np.ndarray) -> np.ndarray:
        """table: joint over V^L. Returns cond[idx, j, y] = P(x_j = y | x_{-j}) for the sequence idx."""
        flat = table.reshape(-1)
        n = flat.size
        idx = np.arange(n)
        digits = (idx[:, None] // pw[None, :]) % V
        out = np.empty((n, L, V))
        for j in range(L):
            base = idx - digits[:, j] * pw[j]
            vals = np.stack([flat[base + y * pw[j]] for y in range(V)], 1)
            out[:, j, :] = vals / vals.sum(1, keepdims=True)
        return out, digits

    condA, digits = full_cond(P_a)
    # position marginal D and a K=2 group-context conditional B for two fixed partitions
    marg = np.stack([P_a.sum(axis=tuple(k for k in range(L) if k != j)) for j in range(L)])  # (L, V)
    parts = [np.array([0, 1, 0, 1, 0, 1, 0, 1]), np.array([0, 0, 1, 1, 1, 0, 0, 1])]
    logB = np.empty((2, flatP.size, L))
    for pi, part in enumerate(parts):
        for j in range(L):
            grp = [k for k in range(L) if part[k] == part[j] and k != j]
            pm = P_a.sum(axis=tuple(grp), keepdims=True) if grp else P_a
            cond = pm / pm.sum(axis=j, keepdims=True)
            logB[pi, :, j] = np.log(np.broadcast_to(cond, shape).reshape(-1))
    logD = np.log(marg)

    n_items = 40000
    idx0 = rng.choice(flatP.size, size=n_items, p=flatP / flatP.sum())

    def gibbs(idx: np.ndarray, hits: np.ndarray, cond: np.ndarray) -> np.ndarray:
        """Sequential single-site Gibbs updates at the hit positions, from the full conditionals of a law. Law-invariant."""
        idx = idx.copy()
        for j in range(L):
            sel = np.where(hits[:, j])[0]
            if sel.size == 0:
                continue
            pj = cond[idx[sel], j, :]
            u = rng.random(sel.size)[:, None]
            y = (u > np.cumsum(pj, 1)).sum(1)
            y = np.minimum(y, V - 1)
            d = (idx[sel] // pw[j]) % V
            idx[sel] = idx[sel] - d * pw[j] + y * pw[j]
        return idx

    def scores_of(idx: np.ndarray, part_id: np.ndarray) -> dict:
        dg = (idx[:, None] // pw[None, :]) % V
        lb_full = np.log(np.take_along_axis(condA[idx], dg[:, :, None], 2)[:, :, 0])
        lb_grp = logB[part_id[:, None], idx[:, None], np.arange(L)[None, :]]
        ld = logD[np.arange(L)[None, :], dg]
        return {"B_full (K=m)": lb_full, "B_grp (K=2)": lb_grp, "q=B_grp-D": lb_grp - ld,
                "u=-q": -(lb_grp - ld), "-B_grp": -lb_grp, "D": ld,
                "random": rng.random(idx.shape[0] * L).reshape(idx.shape[0], L)}

    h = 0.25
    hits = rng.random((n_items, L)) < h          # P(j in H) = h for every j, independent of content
    part_id = rng.integers(0, 2, n_items)        # partition independent of content and of H
    idx_g = gibbs(idx0, hits, condA)
    S = scores_of(idx_g, part_id)
    se = 1.0 / math.sqrt(12 * hits.sum() * (~hits).sum() / (hits.sum() + (~hits).sum()))  # ~ s.e. of AUROC at 1/2
    print(f"  toy: V={V}, L={L}, items={n_items}, hit rate h={h}; AUROC s.e. at 1/2 approx {se:.4f}")
    devs = {}
    for k_, s in S.items():
        devs[k_] = auroc_empirical(s.reshape(-1), hits.reshape(-1).astype(int)) - 0.5
    print("  Gibbs (law-invariant) corruption, hit label, pooled AUROC - 1/2: " + ", ".join(f"{k_} {v_:+.4f}" for k_, v_ in devs.items()))
    check("A3 every within-modality score has pooled AUROC 1/2 (within 4 s.e.) under law-invariant corruption",
          max(abs(v_) for v_ in devs.values()) < 4 * se, f"max |dev| {max(abs(v_) for v_ in devs.values()):.4f}")
    # per-item mean AUROC has expectation 1/2 (items with at least one hit and one non-hit)
    keep = (hits.sum(1) > 0) & (hits.sum(1) < L)
    s_it = S["u=-q"][keep]; z_it = hits[keep]
    from scipy.stats import rankdata
    r = np.apply_along_axis(rankdata, 1, s_it)
    n1 = z_it.sum(1); n0 = L - n1
    a_item = ((r * z_it).sum(1) - n1 * (n1 + 1) / 2) / (n1 * n0)
    m_it, se_it = a_item.mean(), a_item.std(ddof=1) / math.sqrt(a_item.size)
    check("A3 per-item mean AUROC of u has expectation 1/2", abs(m_it - 0.5) < 4 * se_it, f"{m_it:.4f} +/- {se_it:.4f}")

    # positive control: uniform replacement at the same hit set
    idx_u = idx0.copy()
    for j in range(L):
        sel = np.where(hits[:, j])[0]
        d = (idx_u[sel] // pw[j]) % V
        idx_u[sel] = idx_u[sel] - d * pw[j] + rng.integers(0, V, sel.size) * pw[j]
    Su = scores_of(idx_u, part_id)
    au = {k_: auroc_empirical(Su[k_].reshape(-1), hits.reshape(-1).astype(int)) for k_ in ("-B_grp", "u=-q", "random")}
    print("  uniform replacement (off-manifold), hit label, pooled AUROC: " + ", ".join(f"{k_} {v_:.4f}" for k_, v_ in au.items()))
    check("A3 positive control: uniform replacement is detected (AUROC of -B well above 1/2)", au["-B_grp"] - 0.5 > 10 * se)

    # A4: changed-code label under single-site resampling from the full conditional (Gibbs with one hit per item).
    # Exact pooled laws over (j, x): Q1 = P(x) (1 - pi_j(x)) / (L (1 - sbar)), Q0 = P(x) ((1-hh) + hh pi_j(x)) / (L (1-hh+hh sbar)),
    # with hh = 1/L the per-position hit probability, pi_j(x) = P(x_j | x_{-j}).
    pi = np.take_along_axis(condA, digits[:, :, None], 2)[:, :, 0]      # (V^L, L)
    pr = flatP[:, None] / flatP.sum()
    s_pos = (condA ** 2).sum(2)                                           # collision probability per (x, j)
    sbar = float((pr * s_pos).sum() / L)
    hh = 1.0 / L
    Q1 = (pr * (1 - pi)) / (L * (1 - sbar)); Q0 = (pr * ((1 - hh) + hh * pi)) / (L * (1 - hh + hh * sbar))
    vv = 0.5 * np.abs(Q1 - Q0).sum()
    bound = sbar / (1 - sbar) + hh * sbar / (1 - hh + hh * sbar)
    print(f"  changed-code label, single-site resample: mean collision prob sbar={sbar:.4f}, exact TV={vv:.4f}, bound={bound:.4f}")
    check("A4 exact TV <= sbar/(1-sbar) + h sbar/(1-h+h sbar)", vv <= bound + 1e-12)
    # exact AUROC of the LR score, which is monotone decreasing in pi: score = -pi
    flat_s = -pi.reshape(-1); q1f = Q1.reshape(-1); q0f = Q0.reshape(-1)
    order = np.argsort(flat_s)
    s_sorted = flat_s[order]; q1s = q1f[order]; q0s = q0f[order]
    uniq, inv = np.unique(s_sorted, return_inverse=True)
    q1u = np.bincount(inv, q1s); q0u = np.bincount(inv, q0s)
    a_lr = float((q1u * (np.cumsum(q0u) - q0u)).sum() + 0.5 * (q1u * q0u).sum())
    print(f"  exact AUROC of the LR score (-pi_j(x_j | x_-j)) = {a_lr:.4f}; limits [1/2 + v/2, 1/2 + v - v^2/2] = [{0.5 + vv / 2:.4f}, {0.5 + vv - vv * vv / 2:.4f}]")
    check("A4 exact AUROC(LR) within the two-sided bound of Prop. 1(a,b)", 0.5 + vv / 2 - 1e-12 <= a_lr <= 0.5 + vv - vv * vv / 2 + 1e-12)
    # Monte Carlo of the same construction
    one = rng.integers(0, L, n_items)
    hits1 = np.zeros((n_items, L), bool); hits1[np.arange(n_items), one] = True
    idx_1 = gibbs(idx0, hits1, condA)
    dg0 = (idx0[:, None] // pw[None, :]) % V; dg1 = (idx_1[:, None] // pw[None, :]) % V
    changed = (dg0 != dg1)
    s_mc = -np.take_along_axis(condA[idx_1], dg1[:, :, None], 2)[:, :, 0]
    a_mc = auroc_empirical(s_mc.reshape(-1), changed.reshape(-1).astype(int))
    se1 = 1.0 / math.sqrt(12 * changed.sum())
    check("A4 Monte Carlo AUROC(-pi) under changed label matches the exact value", abs(a_mc - a_lr) < 4 * se1 + 0.002, f"MC {a_mc:.4f} vs exact {a_lr:.4f}")
    a_hit = auroc_empirical(s_mc.reshape(-1), hits1.reshape(-1).astype(int))
    check("A4 same corruption, hit label: AUROC 1/2", abs(a_hit - 0.5) < 4 / math.sqrt(12 * n_items), f"{a_hit:.4f}")

    # A6 (r1, red-team M2): exact TV under the changed-code label (the triangle step is tight), and the context alone detects
    T_ = float((pr * np.abs(pi - sbar)).sum() / L)
    tv_exact_formula = 0.5 * T_ * (1 / (1 - sbar) + hh / (1 - hh + hh * sbar))
    check("A6 changed-code label: TV = (1/2) E sum pi|pi - sbar| [1/(1-sbar) + h/(1-h+h sbar)] (exact)", abs(tv_exact_formula - vv) < 1e-12,
          f"{tv_exact_formula:.6f} vs enumerated {vv:.6f}")
    a_ctx = exact_auroc_atoms(-s_pos.reshape(-1), Q1.reshape(-1), Q0.reshape(-1))
    print(f"  changed-code label: context-only score -s(o) (never reads the token value) has exact pooled AUROC {a_ctx:.4f} (toy)")
    check("A6 under the changed-code label the context law depends on Z: a context-only score has AUROC > 1/2", a_ctx > 0.5 + 1e-3)

    # A5: cross-modal corollary. Items (c, v) from the joint; corruption = caption-blind Gibbs w.r.t. the image marginal P_a.
    caps = rng.integers(0, 2, n_items)
    flat_c = P_c.reshape(2, -1)
    cdf0 = np.cumsum(flat_c[0] / flat_c[0].sum()); cdf1 = np.cumsum(flat_c[1] / flat_c[1].sum())
    uu = rng.random(n_items)
    idx_c = np.where(caps == 0, np.searchsorted(cdf0, uu), np.searchsorted(cdf1, uu))
    idx_c = np.minimum(idx_c, flatP.size - 1)
    hits2 = rng.random((n_items, L)) < h
    idx_c2 = gibbs(idx_c, hits2, condA)          # P_a-invariant, caption-blind
    S2 = scores_of(idx_c2, part_id)
    dev2 = max(abs(auroc_empirical(S2[k_].reshape(-1), hits2.reshape(-1).astype(int)) - 0.5) for k_ in ("u=-q", "-B_grp", "B_full (K=m)"))
    check("A5 within-modality scores blind to caption-blind (P_a-invariant) corruption", dev2 < 4 * se, f"max |AUROC-1/2| {dev2:.4f}")
    # cross-modal per-token evidence Delta_j = log p(v_j | c+) - log p(v_j | c-), image fully masked (position marginals given caption)
    margc = np.stack([[P_c[c].sum(axis=tuple(k for k in range(L) if k != j)) / P_c[c].sum() for j in range(L)] for c in (0, 1)])  # (2, L, V)
    dgc = (idx_c2[:, None] // pw[None, :]) % V
    lp_pos = np.log(margc[caps[:, None], np.arange(L)[None, :], dgc])
    lp_neg = np.log(margc[1 - caps[:, None], np.arange(L)[None, :], dgc])
    delta = lp_pos - lp_neg
    m_clean, m_hit = delta[~hits2].mean(), delta[hits2].mean()
    se_d = delta[hits2].std() / math.sqrt(hits2.sum())
    print(f"  per-token caption-blind Gibbs: cross-modal evidence mean on unhit tokens {m_clean:+.4f}, on hit tokens {m_hit:+.4f} (s.e. {se_d:.4f});"
          " small here because the unhit neighbours still carry the caption")
    # information only (no check): the size of the per-token damage is a property of this toy, not of the corollary
    # item-level version: with probability 1/2 the whole image is replaced by an independent draw from P_a (law-invariant)
    hit_item = rng.random(n_items) < 0.5
    uu2 = rng.random(n_items)
    cdfA = np.cumsum(flatP / flatP.sum())
    idx_c3 = np.where(hit_item, np.minimum(np.searchsorted(cdfA, uu2), flatP.size - 1), idx_c)
    S3 = scores_of(idx_c3, part_id)
    lab3 = np.repeat(hit_item[:, None], L, 1)
    dev3 = max(abs(auroc_empirical(S3[k_].reshape(-1), lab3.reshape(-1).astype(int)) - 0.5) for k_ in ("u=-q", "-B_grp", "B_full (K=m)"))
    se3 = 1.0 / math.sqrt(12 * n_items * L / 4) * math.sqrt(L)  # inflate for within-item clustering
    dg3 = (idx_c3[:, None] // pw[None, :]) % V
    d3 = (np.log(margc[caps[:, None], np.arange(L)[None, :], dg3]) - np.log(margc[1 - caps[:, None], np.arange(L)[None, :], dg3]))
    print(f"  item-level independent redraw from P_a: max |AUROC-1/2| of within-modality scores {dev3:.4f};"
          f" cross-modal evidence mean on clean items {d3[~hit_item].mean():+.4f}, on hit items {d3[hit_item].mean():+.4f}")
    check("A5 item-level law-invariant redraw: within-modality scores at 1/2", dev3 < 4 * se3, f"{dev3:.4f} vs 4 s.e. {4 * se3:.4f}")
    check("A5 item-level law-invariant redraw: cross-modal evidence on hit items falls to about 0",
          abs(d3[hit_item].mean()) < 0.01 and d3[~hit_item].mean() > 0.05)
    # a cross-modal score (uses the caption, forbidden by the evidence-separation rule) does see it
    condC = [full_cond(P_c[c])[0] for c in (0, 1)]
    lfc = np.where(caps[:, None] == 0,
                   np.log(np.take_along_axis(condC[0][idx_c2], dgc[:, :, None], 2)[:, :, 0]),
                   np.log(np.take_along_axis(condC[1][idx_c2], dgc[:, :, None], 2)[:, :, 0]))
    lfa = np.log(np.take_along_axis(condA[idx_c2], dgc[:, :, None], 2)[:, :, 0])
    a_x = auroc_empirical(-(lfc - lfa).reshape(-1), hits2.reshape(-1).astype(int))
    print(f"  cross-modal suspicion -(log p(v_j|v_-j,c) - log p(v_j|v_-j)) pooled AUROC {a_x:.4f}")
    check("A5 a caption-using score detects what within-modality scores cannot", a_x - 0.5 > 10 * se)


# ======================================================================================================================
# B. Proposition 2: correlated-token SNR of hard gating
# ======================================================================================================================
def mean_var_corr(m0, m1, phi0, phi1, mu, s2, muc, s2c, g0, g1, g01):
    """Lemma 1 (flags independent of Delta and of each other; exchangeable evidence correlation)."""
    k0, k1 = 1 - phi0, 1 - phi1
    s, sc = math.sqrt(s2), math.sqrt(s2c)
    e = m0 * k0 * mu + m1 * k1 * muc
    v = (m0 * k0 * (s2 + phi0 * mu ** 2) + m1 * k1 * (s2c + phi1 * muc ** 2)
         + m0 * (m0 - 1) * k0 ** 2 * g0 * s2 + m1 * (m1 - 1) * k1 ** 2 * g1 * s2c + 2 * m0 * m1 * k0 * k1 * g01 * s * sc)
    return e, v


def mean_var_corr_cond(m0, m1, phi0, phi1, mu, s2, muc, s2c, g0, g1, g01):
    """Remark 2.4: conditional on the flags, evaluated at the expected kept counts n0 = k0 m0, n1 = k1 m1."""
    n0, n1 = (1 - phi0) * m0, (1 - phi1) * m1
    s, sc = math.sqrt(s2), math.sqrt(s2c)
    e = n0 * mu + n1 * muc
    v = n0 * s2 * (1 + (n0 - 1) * g0) + n1 * s2c * (1 + (n1 - 1) * g1) + 2 * n0 * n1 * g01 * s * sc
    return e, v


def closed_form_lhs_rhs(m, rho, phi0, phi1, mu, s2, s2c, g1, g01):
    """Prop. 2(b), mu_c = 0: returns LHS - RHS (per token, i.e. divided by m)."""
    s, sc = math.sqrt(s2), math.sqrt(s2c)
    lhs = (rho * s2c * ((phi1 - 2 * phi0 + phi0 ** 2) + (rho * m - 1) * g1 * (phi1 - phi0) * (2 - phi0 - phi1))
           + 2 * rho * (1 - rho) * m * g01 * s * sc * (1 - phi0) * (phi1 - phi0))
    rhs = (1 - rho) * phi0 * (1 - phi0) * (s2 + mu ** 2)
    return lhs - rhs


def boundary(phi0, kappa, G):
    """Prop. 2(c): smallest phi1 at which hard gating raises the SNR (mu_c = 0, gamma_01 = 0). G = (rho m - 1) gamma_1."""
    a = phi0 * (1 - phi0)
    if G == 0:
        x = a * (1 + 1 / kappa)
    else:
        bq = 1 + 2 * G * (1 - phi0)
        disc = bq * bq - 4 * G * a * (1 + 1 / kappa)
        if disc < 0:
            return float("nan")
        x = (bq - math.sqrt(disc)) / (2 * G)
    return phi0 + x if phi0 + x <= 1 else float("nan")


def section_B() -> None:
    print("\n=== B. Proposition 2: correlated-token SNR of hard gating ===")
    rng = np.random.default_rng(SEED + 1)

    # B1 Lemma 1 by Monte Carlo (Gaussian common-factor construction)
    m0, m1 = 30, 10
    mu, s2, muc, s2c = 0.3, 1.0, -0.1, 2.25
    g0, g1, lam = 0.1, 0.3, 0.5
    g01 = lam * math.sqrt(g0 * g1)
    phi0, phi1 = 0.1, 0.6
    R = 400000
    F0 = rng.normal(size=R); F1 = lam * F0 + math.sqrt(1 - lam ** 2) * rng.normal(size=R)
    d0 = mu + math.sqrt(s2) * (math.sqrt(g0) * F0[:, None] + math.sqrt(1 - g0) * rng.normal(size=(R, m0)))
    d1 = muc + math.sqrt(s2c) * (math.sqrt(g1) * F1[:, None] + math.sqrt(1 - g1) * rng.normal(size=(R, m1)))
    I0 = rng.random((R, m0)) > phi0; I1 = rng.random((R, m1)) > phi1
    Ssum = (I0 * d0).sum(1) + (I1 * d1).sum(1)
    e, v = mean_var_corr(m0, m1, phi0, phi1, mu, s2, muc, s2c, g0, g1, g01)
    se_e = math.sqrt(v / R); se_v = v * math.sqrt(2 / R)
    check("B1 Lemma 1 mean (Monte Carlo)", abs(Ssum.mean() - e) < 4 * se_e, f"MC {Ssum.mean():.4f} vs {e:.4f}")
    check("B1 Lemma 1 variance (Monte Carlo)", abs(Ssum.var() - v) < 4 * se_v, f"MC {Ssum.var():.3f} vs {v:.3f}")
    del d0, d1, I0, I1

    # B2 reduction to theory.mean_var and to theory.special_case_inequality at zero correlation
    md, mm = 0.0, 0
    for _ in range(20000):
        m = int(rng.integers(10, 2000)); rho = rng.uniform(0.01, 0.99)
        m1_ = rho * m; m0_ = m - m1_
        p0, p1 = rng.uniform(0, 0.5), rng.uniform(0, 1)
        mu_, s2_, muc_, s2c_ = rng.normal(0, 1), rng.uniform(0.1, 3), rng.normal(0, 1), rng.uniform(0.1, 3)
        e1, v1 = mean_var_corr(m0_, m1_, p0, p1, mu_, s2_, muc_, s2c_, 0, 0, 0)
        e2, v2 = T.mean_var(m, rho, p0, p1, mu_, s2_, muc_, s2c_)
        md = max(md, abs(e1 - e2) / (1 + abs(e2)), abs(v1 - v2) / (1 + v2))
        lhs = closed_form_lhs_rhs(m, rho, p0, p1, mu_, s2_, s2c_, 0, 0)
        if abs(lhs) > 1e-9:
            mm += int((lhs > 0) != T.special_case_inequality(rho, p0, p1, mu_, s2_, s2c_))
    check("B2 Lemma 1 at gamma=0 equals theory.mean_var", md < 1e-9, f"max rel diff {md:.1e}")
    check("B2 closed form at gamma=0 equals theory.special_case_inequality", mm == 0, f"{mm} mismatches in 20000")

    # B3 closed form (mu_c = 0) agrees with the direct SNR comparison (same Lemma-1 code: an algebra check, not a check of Lemma 1;
    # PSD is not enforced for every draw; r1 adds the symbolic check D3)
    mism, n_eval = 0, 0
    for _ in range(40000):
        m = int(rng.integers(20, 3000)); rho = rng.uniform(0.01, 0.6)
        m1_ = rho * m; m0_ = m - m1_
        p0, p1 = rng.uniform(0, 0.4), rng.uniform(0, 1)
        mu_ = abs(rng.normal(0, 0.5)) + 1e-3; s2_, s2c_ = rng.uniform(0.2, 3), rng.uniform(0.2, 3)
        g0_, g1_ = rng.uniform(-0.5, 1) / max(m0_ - 1, 1) * rng.choice([1, 50]), rng.uniform(-0.5, 1) / max(m1_ - 1, 1) * rng.choice([1, 50])
        g0_, g1_ = min(g0_, 0.9), min(g1_, 0.9)
        lim = math.sqrt(max((1 + (m0_ - 1) * g0_) * (1 + (m1_ - 1) * g1_), 0) / (m0_ * m1_))
        g01_ = rng.uniform(-1, 1) * min(lim, math.sqrt(max(g0_, 0) * max(g1_, 0)) if g0_ > 0 and g1_ > 0 else lim)
        eg, vg = mean_var_corr(m0_, m1_, p0, p1, mu_, s2_, 0.0, s2c_, g0_, g1_, g01_)
        e0, v0 = mean_var_corr(m0_, m1_, 0, 0, mu_, s2_, 0.0, s2c_, g0_, g1_, g01_)
        if vg <= 0 or v0 <= 0 or eg <= 0:
            continue
        direct = eg / math.sqrt(vg) - e0 / math.sqrt(v0)
        cf = closed_form_lhs_rhs(m, rho, p0, p1, mu_, s2_, s2c_, g1_, g01_)
        if abs(direct) < 1e-10 or abs(cf) < 1e-10:
            continue
        n_eval += 1
        mism += int((direct > 0) != (cf > 0))
    check("B3 closed form (mu_c=0) has the sign of the direct SNR change (algebra, shared code)", mism == 0, f"{mism} mismatches in {n_eval}")

    # B4 frontier: closed-form boundary vs bisection on the direct comparison; direction of the shift (ILLUSTRATIVE values)
    m, rho, mu_, s2_, s2c_ = 1024, 0.10, 0.10, 1.0, 1.0
    kappa = rho * s2c_ / ((1 - rho) * (s2_ + mu_ ** 2))
    print(f"  ILLUSTRATIVE frontier (not estimates): m={m}, rho={rho}, mu={mu_}, sigma2=sigma2_c=1, gamma_01=0, chi (red-team kappa)={kappa:.4f}")
    print("  phi0   " + "  ".join(f"g1={g:<7}" for g in (0, 1e-4, 1e-3, 1e-2, 5e-2)))
    worst, mono_ok = 0.0, True
    for p0 in (0.01, 0.05, 0.10, 0.20):
        row = []
        for g in (0, 1e-4, 1e-3, 1e-2, 5e-2):
            b = boundary(p0, kappa, (rho * m - 1) * g)
            lo, hi = p0, 1.0

            def helps(p1):
                eg, vg = mean_var_corr(m - rho * m, rho * m, p0, p1, mu_, s2_, 0.0, s2c_, 0.0, g, 0.0)
                e0, v0 = mean_var_corr(m - rho * m, rho * m, 0, 0, mu_, s2_, 0.0, s2c_, 0.0, g, 0.0)
                return eg / math.sqrt(vg) > e0 / math.sqrt(v0)
            if helps(hi - 1e-12):
                for _ in range(80):
                    mid = 0.5 * (lo + hi)
                    lo, hi = (lo, mid) if helps(mid) else (mid, hi)
                if not math.isnan(b):
                    worst = max(worst, abs(b - hi))
            row.append(b)
        mono_ok &= all((math.isnan(a) or math.isnan(c)) or c <= a + 1e-12 for a, c in zip(row, row[1:]))
        mono_ok &= all(math.isnan(x) or x > p0 for x in row)
        print(f"  {p0:<5}  " + "  ".join(f"{x:<10.4f}" if not math.isnan(x) else f"{'none':<10}" for x in row))
    check("B4 closed-form boundary equals bisection on the direct SNR comparison", worst < 1e-8, f"max |diff| {worst:.1e}")
    check("B4 boundary decreases with gamma_1 and stays above the diagonal phi1 = phi0", mono_ok)
    b_big = boundary(0.05, kappa, 1e7)
    check("B4 boundary tends to the diagonal as (rho m - 1) gamma_1 grows", abs(b_big - 0.05) < 1e-4, f"b(0.05) = {b_big:.6f}")
    # gamma_0 drops out when mu_c = 0
    eg1, vg1 = mean_var_corr(900, 100, 0.05, 0.4, 0.1, 1, 0, 1, 0.0, 0.01, 0.0); e01, v01 = mean_var_corr(900, 100, 0, 0, 0.1, 1, 0, 1, 0.0, 0.01, 0.0)
    eg2, vg2 = mean_var_corr(900, 100, 0.05, 0.4, 0.1, 1, 0, 1, 0.2, 0.01, 0.0); e02, v02 = mean_var_corr(900, 100, 0, 0, 0.1, 1, 0, 1, 0.2, 0.01, 0.0)
    d1 = (1 - 0.05) ** 2 * v01 - vg1; d2 = (1 - 0.05) ** 2 * v02 - vg2
    check("B4 gamma_0 does not enter k0^2 Var S_0 - Var S_g when mu_c = 0", abs(d1 - d2) < 1e-8 * abs(d1), f"{d1:.6f} vs {d2:.6f}")
    # random gate phi1 = phi0 lowers the SNR (every correlation term vanishes on the diagonal); here gamma_01 = 0.01
    ok = all(closed_form_lhs_rhs(1024, 0.1, p, p, 0.1, 1, 1, g, 0.01) < 0 for p in (0.01, 0.05, 0.2) for g in (0, 0.01, 0.1))
    check("B4 a random gate (phi1 = phi0) lowers the SNR (grid of gamma_1, gamma_01 = 0.01)", ok)

    # B5 large-m limit and the conditional-on-flags variant (Remark 2.4), with accuracy P(S > 0) by Monte Carlo (ILLUSTRATIVE)
    m0_, m1_ = 900.0, 100.0
    p0, p1, mu_, s2_, muc_, s2c_, g0_, g1_, g01_ = 0.05, 0.5, 0.05, 1.0, 0.0, 1.0, 0.02, 0.05, 0.01
    eL, vL = mean_var_corr(m0_ * 1e4, m1_ * 1e4, p0, p1, mu_, s2_, muc_, s2c_, g0_, g1_, g01_)
    a_, b_ = 0.9 * (1 - p0), 0.1 * (1 - p1)
    lim = (a_ * mu_ + b_ * muc_) / math.sqrt(a_ ** 2 * g0_ * s2_ + b_ ** 2 * g1_ * s2c_ + 2 * a_ * b_ * g01_ * math.sqrt(s2_ * s2c_))
    check("B5 large-m limit of the SNR depends only on the retained shares", abs(eL / math.sqrt(vL) - lim) < 1e-3 * lim, f"{eL / math.sqrt(vL):.5f} vs {lim:.5f}")
    # optimal retained-mass ratio r* = (mu_c A - mu B) / (mu C - mu_c B) of the large-m limit (A = g0 s2, B = g01 s sc, C = g1 s2c)
    worst_r = 0.0
    for _ in range(2000):
        A_, C_ = rng.uniform(0.01, 1), rng.uniform(0.01, 1)
        B_ = rng.uniform(-0.99, 0.99) * math.sqrt(A_ * C_)
        mu1, mu2 = rng.uniform(0.05, 1), rng.normal(0, 0.5)
        rs = (mu2 * A_ - mu1 * B_) / (mu1 * C_ - mu2 * B_)
        grid = np.linspace(rs - 5, rs + 5, 200001)
        gfun = (mu1 + grid * mu2) ** 2 / (A_ + 2 * grid * B_ + grid ** 2 * C_)
        g_rs = (mu1 + rs * mu2) ** 2 / (A_ + 2 * rs * B_ + rs ** 2 * C_)
        worst_r = max(worst_r, (gfun.max() - g_rs) / g_rs)
    check("B5 r* maximises the large-m SNR^2 over the retained-mass ratio", worst_r < 1e-12, f"max rel excess of grid max over g(r*) {worst_r:.1e}")
    # B6 (Remark 2.6): exchangeable covariance keeps the equal-weight sum Fisher/NP-optimal for a common mean shift
    worst6 = 0.0
    for g in (-0.0009, 0.0, 0.01, 0.3, 0.9):
        Sg = (1 - g) * np.eye(1000) + g * np.ones((1000, 1000))
        x = np.linalg.solve(Sg, np.ones(1000))
        worst6 = max(worst6, x.std() / x.mean())
    check("B6 Sherman-Morrison only: exchangeable Sigma^{-1} 1 is proportional to 1 (not an NP statement about the image)", worst6 < 1e-10, f"max cv {worst6:.1e}")
    # conditional closed form = unconditional + m0 k0 phi0 (mu^2 + g0 s2) + m1 k1 phi1 (muc^2 + g1 s2c) on the variance side
    eg, vg = mean_var_corr(m0_, m1_, p0, p1, mu_, s2_, muc_, s2c_, g0_, g1_, g01_)
    ec, vc = mean_var_corr_cond(m0_, m1_, p0, p1, mu_, s2_, muc_, s2c_, g0_, g1_, g01_)
    gap = vg - vc - (m0_ * (1 - p0) * p0 * (mu_ ** 2 + g0_ * s2_) + m1_ * (1 - p1) * p1 * (muc_ ** 2 + g1_ * s2c_))
    check("B7 (Remark 2.4) Var_uncond - Var_cond = m0 k0 phi0 (mu^2 + g0 s2) + m1 k1 phi1 (muc^2 + g1 s2c)", abs(gap) < 1e-8 * vg, f"gap {gap:.2e}")
    # accuracy with Gaussian shared factors, EXACT (r1): given retained counts (N0, N1), S is normal with the conditional variance
    # of Remark 2.4, so P(S > 0) = sum over binomial (N0, N1) of Phi(E/sd). Replaces the r0 Monte Carlo table (red-team M5/R6).
    from scipy.stats import binom
    mm0, mm1, mu_t, g0t, g1t = 360, 40, 0.05, 0.01, 0.05
    print("  ILLUSTRATIVE accuracy, Gaussian shared factors, exact (m0=360, m1=40, mu=0.05, sigma2=sigma2_c=1, mu_c=0, g0=0.01, g1=0.05, g01=0):")
    print("    phi0  phi1   P(S>0) exact   Phi(SNR_uncond)  sign agrees with 'none' row")
    base = None
    n0 = np.arange(mm0 + 1)[:, None]; n1 = np.arange(mm1 + 1)[None, :]
    agree = True
    for (q0, q1) in ((0.0, 0.0), (0.05, 0.05), (0.05, 0.5), (0.05, 0.9), (0.2, 0.9)):
        pm = binom.pmf(n0, mm0, 1 - q0) * binom.pmf(n1, mm1, 1 - q1)
        v = n0 * (1 + (n0 - 1) * g0t) + n1 * (1 + (n1 - 1) * g1t)
        with np.errstate(divide="ignore", invalid="ignore"):
            pr = np.where(v > 0, norm.cdf(n0 * mu_t / np.sqrt(np.where(v > 0, v, 1))), 0.0)
        acc = float((pm * pr).sum())
        eu, vu = mean_var_corr(mm0, mm1, q0, q1, mu_t, 1, 0, 1, g0t, g1t, 0)
        ph = float(norm.cdf(eu / math.sqrt(vu)))
        if base is None:
            base = (acc, ph); tag = "-"
        else:
            same = np.sign(acc - base[0]) == np.sign(ph - base[1]); agree &= bool(same); tag = str(bool(same))
        print(f"    {q0:<5} {q1:<5}  {acc:.6f}       {ph:.6f}         {tag}")
    check("B8 Gaussian shared factors: sign of the accuracy change equals sign of the Phi(SNR) change (illustrative rows)", agree)


# ======================================================================================================================
# C. Proposition 3: soft weights
# ======================================================================================================================
def section_C() -> None:
    print("\n=== C. Proposition 3: reliability weights ===")
    rng = np.random.default_rng(SEED + 3)

    # C1 Lemma 2 by Monte Carlo: weights Beta-distributed per class, independent of Delta, exchangeable evidence correlation
    m0, m1 = 30, 10
    mu, s2, muc, s2c, g0, g1, lam = 0.3, 1.0, -0.1, 2.25, 0.1, 0.3, 0.5
    g01 = lam * math.sqrt(g0 * g1)
    a0, b0, a1, b1 = 4.0, 1.0, 1.0, 3.0
    wb0, wb1 = a0 / (a0 + b0), a1 / (a1 + b1)
    w20 = wb0 * (a0 + 1) / (a0 + b0 + 1); w21 = wb1 * (a1 + 1) / (a1 + b1 + 1)
    R = 400000
    F0 = rng.normal(size=R); F1 = lam * F0 + math.sqrt(1 - lam ** 2) * rng.normal(size=R)
    d0 = mu + math.sqrt(s2) * (math.sqrt(g0) * F0[:, None] + math.sqrt(1 - g0) * rng.normal(size=(R, m0)))
    d1 = muc + math.sqrt(s2c) * (math.sqrt(g1) * F1[:, None] + math.sqrt(1 - g1) * rng.normal(size=(R, m1)))
    W0 = rng.beta(a0, b0, (R, m0)); W1 = rng.beta(a1, b1, (R, m1))
    Sw = (W0 * d0).sum(1) + (W1 * d1).sum(1)
    s, sc = math.sqrt(s2), math.sqrt(s2c)
    e = m0 * wb0 * mu + m1 * wb1 * muc
    v = (m0 * (w20 * (s2 + mu ** 2) - wb0 ** 2 * mu ** 2) + m1 * (w21 * (s2c + muc ** 2) - wb1 ** 2 * muc ** 2)
         + m0 * (m0 - 1) * wb0 ** 2 * g0 * s2 + m1 * (m1 - 1) * wb1 ** 2 * g1 * s2c + 2 * m0 * m1 * wb0 * wb1 * g01 * s * sc)
    check("C1 Lemma 2 mean (Monte Carlo)", abs(Sw.mean() - e) < 4 * math.sqrt(v / R), f"MC {Sw.mean():.4f} vs {e:.4f}")
    check("C1 Lemma 2 variance (Monte Carlo)", abs(Sw.var() - v) < 4 * v * math.sqrt(2 / R), f"MC {Sw.var():.3f} vs {v:.3f}")
    # hard gate as the special case w = I: Lemma 2 reduces to Lemma 1
    e2, v2 = mean_var_corr(m0, m1, 0.2, 0.7, mu, s2, muc, s2c, g0, g1, g01)
    k0, k1 = 0.8, 0.3
    v3 = (m0 * (k0 * (s2 + mu ** 2) - k0 ** 2 * mu ** 2) + m1 * (k1 * (s2c + muc ** 2) - k1 ** 2 * muc ** 2)
          + m0 * (m0 - 1) * k0 ** 2 * g0 * s2 + m1 * (m1 - 1) * k1 ** 2 * g1 * s2c + 2 * m0 * m1 * k0 * k1 * g01 * s * sc)
    check("C1 Lemma 2 with w = I equals Lemma 1", abs(v3 - v2) < 1e-9 * v2)
    del d0, d1, W0, W1

    # C2 optimal weights. Tokens with conditional means mu_j = mu(u_j) and variances sig2_j; covariance D + gamma sigma2 11^T.
    def snr(w, mvec, Sig):
        return float(w @ mvec / math.sqrt(w @ Sig @ w))

    def fixed_point_weights(mvec, dvec, cg):
        """w_j = (mu_j - xi)_+ / d_j with xi = cg * sum_k (mu_k - xi)_+ / d_k (cg = gamma sigma^2)."""
        lo, hi = 0.0, float(mvec.max())
        for _ in range(200):
            xi = 0.5 * (lo + hi)
            rhs = cg * (np.clip(mvec - xi, 0, None) / dvec).sum()
            lo, hi = (xi, hi) if rhs > xi else (lo, xi)
        xi = 0.5 * (lo + hi)
        return np.clip(mvec - xi, 0, None) / dvec, xi

    worst_unc, worst_nn, xis = 0.0, 0.0, []
    for trial in range(30):
        n = 60
        sig2 = 1.0
        pi1 = rng.beta(0.5, 2.0, n)                  # posterior corruption probability of each token (ILLUSTRATIVE)
        mu_c = rng.uniform(-0.05, 0.05)
        mu_t = 0.2
        mvec = (1 - pi1) * mu_t + pi1 * mu_c
        s2u = sig2 + pi1 * (1 - pi1) * (mu_t - mu_c) ** 2
        g = [0.0, 0.002, 0.02, 0.1][trial % 4]
        dvec = s2u - g * sig2
        Sig = np.diag(dvec) + g * sig2 * np.ones((n, n))
        # unconstrained optimum Sigma^{-1} mu vs matched filter at gamma = 0
        w_opt = np.linalg.solve(Sig, mvec)
        if g == 0.0:
            w_mf = mvec / s2u
            res0 = minimize(lambda w: -snr(w, mvec, Sig), x0=rng.random(n) + 0.1, method="BFGS", options=dict(gtol=1e-10, maxiter=20000))
            worst_unc = max(worst_unc, 1 - snr(w_mf, mvec, Sig) / snr(res0.x, mvec, Sig))
        # non-negative optimum by L-BFGS-B on 0.5 w'Sig w - w'mu, w >= 0
        res = minimize(lambda w: 0.5 * w @ Sig @ w - w @ mvec, x0=np.full(n, 0.1), jac=lambda w: Sig @ w - mvec,
                       bounds=[(0, None)] * n, method="L-BFGS-B", options=dict(ftol=1e-15, gtol=1e-12, maxiter=5000))
        w_fp, xi = fixed_point_weights(mvec, dvec, g * sig2)
        xis.append((g, xi, int((w_fp == 0).sum())))
        worst_nn = max(worst_nn, abs(snr(res.x, mvec, Sig) - snr(w_fp, mvec, Sig)) / snr(res.x, mvec, Sig))
    check("C2 gamma=0: matched filter mu(u)/sigma^2(u) attains the SNR found by a generic optimiser (BFGS)", worst_unc < 1e-6, f"max rel loss {worst_unc:.1e}")
    check("C2 w >= 0 with exchangeable correlation: soft-threshold fixed point equals the QP optimum", worst_nn < 1e-6, f"max rel diff {worst_nn:.1e}")
    by_g = {}
    for g, xi, nz in xis:
        by_g.setdefault(g, []).append((xi, nz))
    print("  ILLUSTRATIVE (n=60 tokens): gamma -> mean threshold xi, mean number of tokens given weight 0")
    for g in sorted(by_g):
        print(f"    gamma={g:<6} xi={np.mean([a for a, _ in by_g[g]]):.4f}  zero-weight tokens={np.mean([b for _, b in by_g[g]]):.1f}")
    check("C2 threshold xi is 0 at gamma=0 and increases with gamma", by_g[0.0][0][0] < 1e-12 and
          np.mean([a for a, _ in by_g[0.002]]) < np.mean([a for a, _ in by_g[0.02]]) < np.mean([a for a, _ in by_g[0.1]]))

    # C3 clean-pair efficiency of conformal p-value weights (SOFT-A) and of the hard gate, conditional on weights
    for N in (10, 1000, 10 ** 6):
        grid = np.arange(1, N + 2) / (N + 1)
        nu = (grid ** 2).mean() / grid.mean() ** 2
        check(f"C3 nu = E w^2 / (E w)^2 on the p-value grid equals 2(2N+3)/(3(N+2)), N={N}",
              abs(nu - 2 * (2 * N + 3) / (3 * (N + 2))) < 1e-10)
    mtok = 1024
    print("  clean-pair SNR^2 ratio (weights / none), conditional on weights, uniform p-value weights, by gamma_0:")
    for g in (0.0, 0.001, 0.01, 0.1):
        w = rng.permutation(np.arange(1, mtok + 1) / (mtok + 1))   # exact uniform grid, as a clean item would see
        Sig = (1 - g) * np.eye(mtok) + g * np.ones((mtok, mtok))
        direct = (w.sum() ** 2 / (w @ Sig @ w)) / (mtok ** 2 / (np.ones(mtok) @ Sig @ np.ones(mtok)))
        nu = mtok * (w @ w) / w.sum() ** 2
        formula = ((1 - g) + g * mtok) / ((1 - g) * nu + g * mtok)
        print(f"    gamma_0={g:<6} direct {direct:.5f}  formula {formula:.5f}")
        if abs(direct - formula) > 1e-9:
            FAILS.append(f"C3 clean-pair ratio gamma={g}")
    check("C3 clean-pair efficiency formula [(1-g)+g m]/[(1-g) nu + g m] matches the quadratic form", not any(f.startswith("C3 clean") for f in FAILS))


# ======================================================================================================================
# D. Revision r1 (2026-10-29): checks for every claim changed after the red-team review
# ======================================================================================================================
def section_D() -> None:
    print("\n=== D. Revision r1 checks ===")
    rng = np.random.default_rng(SEED + 4)

    # D1 (M1): pooled vs per-item AUROC. f = token value, O empty. Item A: corrupted {1}, clean {0}; item B: corrupted {0,0}, clean {1,0}.
    sc_ = np.array([1.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    a_pool = exact_auroc_atoms(sc_, np.r_[np.ones(3), np.zeros(3)], np.r_[np.zeros(3), np.ones(3)])

    def item_auc(c, k):
        return float(np.mean([1.0 if a > b else 0.5 if a == b else 0.0 for a in c for b in k]))
    a_item = 0.5 * (item_auc([1], [0]) + item_auc([0, 0], [1, 0]))
    print(f"  pooled class laws equal (TV = 0): pooled AUROC {a_pool:.3f}; per-item mean AUROC {a_item:.3f}")
    check("D1 Prop. 1 bounds the pooled AUROC only: TV = 0 with per-item mean AUROC != 1/2",
          abs(a_pool - 0.5) < 1e-12 and abs(a_item - 0.625) < 1e-12)

    # D3 (Prop. 2(b)): symbolic identity, independent of the shared numeric code
    import sympy as sp
    m, r, p0, p1, mu, s, sc = sp.symbols("m rho phi0 phi1 mu sigma sigma_c", real=True)
    g0, g1, g01 = sp.symbols("gamma0 gamma1 gamma01", real=True)
    m0, m1 = (1 - r) * m, r * m
    k0, k1 = 1 - p0, 1 - p1
    Vg = (m0 * k0 * (s**2 + p0 * mu**2) + m1 * k1 * sc**2 + m0 * (m0 - 1) * k0**2 * g0 * s**2
          + m1 * (m1 - 1) * k1**2 * g1 * sc**2 + 2 * m0 * m1 * k0 * k1 * g01 * s * sc)
    V0 = Vg.subs({p0: 0, p1: 0})
    lhs = (r * sc**2 * ((p1 - 2 * p0 + p0**2) + (r * m - 1) * g1 * (p1 - p0) * (2 - p0 - p1))
           + 2 * r * (1 - r) * m * g01 * s * sc * (1 - p0) * (p1 - p0))
    rhs = (1 - r) * p0 * (1 - p0) * (s**2 + mu**2)
    resid = sp.simplify(sp.expand((k0**2 * V0 - Vg) / m - (lhs - rhs)))
    check("D3 sympy: (k0^2 V0 - Vg)/m - [LHS - RHS of (2.5)] == 0", resid == 0, f"residual {resid}")
    # Lemma 1 itself by Monte Carlo at a second point with gamma_01 < 0 (B1 used one point)
    R = 300000; mA, mB = 20, 8; gA, gB, lam = 0.2, 0.1, -0.6
    F0 = rng.normal(size=R); F1 = lam * F0 + math.sqrt(1 - lam**2) * rng.normal(size=R)
    dA = 0.2 + (math.sqrt(gA) * F0[:, None] + math.sqrt(1 - gA) * rng.normal(size=(R, mA)))
    dB = 0.1 + 1.3 * (math.sqrt(gB) * F1[:, None] + math.sqrt(1 - gB) * rng.normal(size=(R, mB)))
    Ss = ((rng.random((R, mA)) > 0.2) * dA).sum(1) + ((rng.random((R, mB)) > 0.7) * dB).sum(1)
    e_, v_ = mean_var_corr(mA, mB, 0.2, 0.7, 0.2, 1.0, 0.1, 1.69, gA, gB, lam * math.sqrt(gA * gB))
    check("D3 Lemma 1 by Monte Carlo at a second point (gamma_01 < 0)",
          abs(Ss.mean() - e_) < 4 * math.sqrt(v_ / R) and abs(Ss.var() - v_) < 4 * v_ * math.sqrt(2 / R),
          f"mean {Ss.mean():.4f} vs {e_:.4f}; var {Ss.var():.3f} vs {v_:.3f}")
    del dA, dB

    # D4 (m1): negative gamma_01 opens a helping region BELOW the diagonal; negative gamma_1 alone cannot
    M0, M1 = 900, 100
    G0, G1, G01 = 0.05, 0.05, -0.045
    Sig = np.zeros((M0 + M1, M0 + M1))
    Sig[:M0, :M0] = G0; Sig[M0:, M0:] = G1; Sig[:M0, M0:] = G01; Sig[M0:, :M0] = G01
    np.fill_diagonal(Sig, 1.0)
    lam_min = float(np.linalg.eigvalsh(Sig).min())
    e_n, v_n = mean_var_corr(M0, M1, 0, 0, 0.1, 1, 0, 1, G0, G1, G01)
    e_g, v_g = mean_var_corr(M0, M1, 0.3, 0.0, 0.1, 1, 0, 1, G0, G1, G01)
    print(f"  gamma_01 = -0.045 (min eigenvalue {lam_min:.4f}): SNR none {e_n / math.sqrt(v_n):.4f}, "
          f"gate (phi0, phi1) = (0.3, 0) {e_g / math.sqrt(v_g):.4f}")
    check("D4 with gamma_01 < 0 a gate that flags only clean tokens can raise the SNR (PSD example)",
          lam_min > 0 and e_g / math.sqrt(v_g) > e_n / math.sqrt(v_n))
    bad = 0
    for _ in range(20000):
        mm = int(rng.integers(20, 3000)); rr = rng.uniform(0.01, 0.6); m1_ = rr * mm
        g1_ = rng.uniform(-1, 0) / max(m1_ - 1, 1)
        a0 = rng.uniform(0.001, 0.9); a1 = rng.uniform(0, a0)
        if closed_form_lhs_rhs(mm, rr, a0, a1, rng.uniform(0, 1), rng.uniform(0.1, 3), rng.uniform(0.1, 3), g1_, rng.uniform(0, 0.01)) > 0:
            bad += 1
    check("D4 with gamma_1 in [-1/(m1-1), 0] and gamma_01 >= 0 no gate at or below the diagonal raises the SNR", bad == 0, f"{bad} of 20000")

    # D5 (M5): non-Gaussian shared component: the SNR rises while the accuracy falls (exact given counts and factor)
    from scipy.stats import binom
    mu5, M0, M1 = 0.05, 900, 100
    p_rare, g1_target = 0.02, 0.074
    Lf = math.sqrt(g1_target / p_rare)   # F1 = 0 w.p. 0.98, +/-Lf w.p. 0.01 each; corrupted total variance 1
    se2 = 1.0 - g1_target                # idiosyncratic variance of a corrupted token

    def acc_exact(q0, q1):
        n0 = np.arange(M0 + 1)[:, None]; n1 = np.arange(M1 + 1)[None, :]
        pm = binom.pmf(n0, M0, 1 - q0) * binom.pmf(n1, M1, 1 - q1)
        tot = 0.0
        for f, pf in ((0.0, 1 - p_rare), (Lf, p_rare / 2), (-Lf, p_rare / 2)):
            v = n0 * 1.0 + n1 * se2
            mean = n0 * mu5 + n1 * f
            with np.errstate(divide="ignore", invalid="ignore"):
                pr = np.where(v > 0, norm.cdf(mean / np.sqrt(np.where(v > 0, v, 1))), 0.0)
            tot += pf * float((pm * pr).sum())
        return tot
    e0_, v0_ = mean_var_corr(M0, M1, 0, 0, mu5, 1, 0, 1, 0, g1_target, 0)
    eg_, vg_ = mean_var_corr(M0, M1, 0.1, 0.5, mu5, 1, 0, 1, 0, g1_target, 0)
    a0_, ag_ = acc_exact(0, 0), acc_exact(0.1, 0.5)
    print(f"  rare non-Gaussian shared factor (gamma_1 = {g1_target}): SNR {e0_ / math.sqrt(v0_):.3f} -> {eg_ / math.sqrt(vg_):.3f}; "
          f"exact accuracy {a0_:.4f} -> {ag_:.4f}")
    check("D5 non-Gaussian correlation: gating raises the SNR of S but lowers P(S > 0)",
          eg_ / math.sqrt(vg_) > e0_ / math.sqrt(v0_) and ag_ < a0_)

    # D6 (m6): Prop. 3(a) corrected: a hard gate is optimal iff (mu(u))_+ / sigma^2(u) takes at most one non-zero value
    mu_t, mu_c = 0.2, 0.0
    pi1 = np.array([0.3] * 30 + [1.0] * 10)
    mvec = (1 - pi1) * mu_t + pi1 * mu_c; s2u = 1.0 + pi1 * (1 - pi1) * (mu_t - mu_c) ** 2
    Sg = np.diag(s2u)
    res = minimize(lambda w: 0.5 * w @ Sg @ w - w @ mvec, x0=np.full(40, 0.1), jac=lambda w: Sg @ w - mvec,
                   bounds=[(0, None)] * 40, method="L-BFGS-B", options=dict(ftol=1e-15, gtol=1e-12))
    w = res.x
    two_valued = bool(np.allclose(w[:30], w[0], rtol=1e-6) and np.allclose(w[30:], 0, atol=1e-9) and w[0] > 0)
    print(f"  pi_1 in {{0.3, 1}}, mu_c = 0: optimal weights {w[0]:.4f} (pi_1 = 0.3) and {w[30:].max():.1e} (pi_1 = 1): a 0/1 gate with no oracle")
    check("D6 hard gate optimal without an oracle when mu(u)_+/sigma^2(u) has one non-zero value", two_valued)
    pi1b = np.array([0.1] * 20 + [0.5] * 20)
    mvb = (1 - pi1b) * mu_t; s2b = 1.0 + pi1b * (1 - pi1b) * mu_t ** 2
    wb = mvb / s2b
    check("D6 with two distinct non-zero values of mu(u)/sigma^2(u) the optimum is not a 0/1 gate", abs(wb[0] / wb[-1] - 1) > 0.1)

    # D7 (m6): xi = 0 for every gamma if all mu(u_k) <= 0
    mneg = -np.abs(rng.normal(0.1, 0.05, 30)); dd = np.full(30, 0.9)
    lo, hi = 0.0, 1.0
    for _ in range(100):
        xi = 0.5 * (lo + hi); rhs_ = 0.1 * (np.clip(mneg - xi, 0, None) / dd).sum()
        lo, hi = (xi, hi) if rhs_ > xi else (lo, xi)
    check("D7 xi = 0 at gamma > 0 when every mu(u_k) <= 0", 0.5 * (lo + hi) < 1e-12)

    # D8 (m2): the large-m g(r) has two critical points: r = -mu/mu_c (global minimum, g = 0) and r*
    worst = 0.0
    for _ in range(500):
        A_, C_ = rng.uniform(0.01, 1), rng.uniform(0.01, 1); B_ = rng.uniform(-0.99, 0.99) * math.sqrt(A_ * C_)
        mu1, mu2 = rng.uniform(0.05, 1), rng.normal(0, 0.5)
        rz = -mu1 / mu2

        def g(x):
            return (mu1 + x * mu2) ** 2 / (A_ + 2 * x * B_ + x * x * C_)
        h = 1e-6
        worst = max(worst, abs((g(rz + h) - g(rz - h)) / (2 * h)), g(rz))
    check("D8 r = -mu/mu_c is a critical point with g = 0 (second critical point besides r*)", worst < 1e-6, f"max |g'|, g {worst:.1e}")


if __name__ == "__main__":
    print(f"theory_check_2026-10-29.py  seed={SEED}  numpy={np.__version__}")
    section_A()
    section_B()
    section_C()
    section_D()
    print(f"\nSUMMARY: {'ALL CHECKS PASSED' if not FAILS else 'FAILED: ' + '; '.join(FAILS)}")
