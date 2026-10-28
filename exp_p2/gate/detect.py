"""Detection analysis of M1 / the CPU fallback (v2 sections 7.6, 11.4): per-item AUROC of every score against the changed-code map Z, per corruption, and the
paired bootstrap of q against the best cheap baseline. Works on probe-2 arrays alone (no q, no TbV: labelled exploratory) or with the M1 post-hoc arrays.

Probe-2 array keys (run_probe2.py): clean, and per corruption c in (swap, patch, jpeg, noise): c_s1, c_s2, c_s3, c_r_original, c_codes, c_z.
B (caption masked, same masks) = s1 - r_original.  q = B - D with D from run_gate_m1 (c_D).  Suspicions (higher = more suspicious):
  s1 -> -s1, s2 -> -s2, s3, r_original -> -r_original, plainB -> -B, q -> -(B - D), tbv -> -log p(observed | nothing masked), random (probe 2's own draw),
  tex (pixel patch variance), nbr (neighbour codebook distance), rarity (code rarity).
Items with fewer than 5 corrupted or 5 clean tokens are excluded for that corruption (as run_probe2) and counted.
Pixel baselines are regenerated deterministically on the CPU (probe 2's own seeds): jpeg q10 and noise sigma 0.1 on the preprocessed image; swap and patch have no pixel
image (texture = NaN, reported as not applicable)."""
from __future__ import annotations

import numpy as np

from exp_p2 import core
from exp_p2.gate import baselines, corruptions, seeds

P2_SEED = 20261028
P2_CORRS = ("swap", "patch", "jpeg", "noise")
CHEAP = ("tex", "nbr", "rarity", "s3", "plainB", "tbv", "tex_neg", "nbr_neg", "rarity_neg")
# candidates for 'best cheap baseline' (random and r_original are controls, not rivals). The *_neg entries are the same baselines with the opposite sign: the analysis
# gives the non-generative rivals the better of both orientations (a sign oracle), so q must beat even that; this is deliberately generous to the rivals.
GRID, PATCH_PX = 32, 16


def preprocess512(pil):
    """Copy of UniScorer.preprocess (centre square crop, bicubic to 512): needed to regenerate pixels without a model."""
    from PIL import Image
    w, h = pil.size
    s = min(w, h)
    l, t = (w - s) // 2, (h - s) // 2
    return pil.convert("RGB").crop((l, t, l + s, t + s)).resize((512, 512), Image.BICUBIC)


def regen_pixels(pil_raw, i: int, corr: str):
    """Observed pixels of probe 2 item i under `corr` as uint8 [512,512,3], or None for token-level corruptions."""
    if corr not in ("jpeg", "noise"):
        return None
    pil = preprocess512(pil_raw)
    ci = P2_CORRS.index(corr)
    if corr == "jpeg":
        img = corruptions.jpeg(pil, 10)
    else:
        img = corruptions.gaussian_noise(pil, 0.1, np.random.default_rng([P2_SEED, i, ci]))
    return np.asarray(img)


def suspicions(arr, corr: str, i: int, m1=None, extra: dict | None = None) -> dict[str, np.ndarray]:
    m = len(arr[f"{corr}_s1"])
    s1, r = np.asarray(arr[f"{corr}_s1"], np.float32), np.asarray(arr[f"{corr}_r_original"], np.float32)
    B = s1 - r
    ci = P2_CORRS.index(corr)
    out = dict(s1=-s1, s2=-np.asarray(arr[f"{corr}_s2"], np.float32), s3=np.asarray(arr[f"{corr}_s3"], np.float32), r_original=-r, plainB=-B,
               random=np.random.default_rng([P2_SEED, i, 50 + ci]).random(m))
    if m1 is not None and f"{corr}_D" in m1:
        out["q"] = -(B - np.asarray(m1[f"{corr}_D"], np.float32))
    if m1 is not None and f"{corr}_tbv" in m1:
        out["tbv"] = -np.asarray(m1[f"{corr}_tbv"], np.float32)
    if extra:
        out.update(extra)
    return out


def item_aurocs(sus: dict, z: np.ndarray, min_class: int = 5) -> dict:
    n_c, m = int(z.sum()), len(z)
    ok = min_class <= n_c <= m - min_class
    return {k: (core.auroc(v, z) if ok and not np.isnan(v).any() else float("nan")) for k, v in sus.items()} | {"_eligible": float(ok), "_n_corrupted": float(n_c)}


def aggregate(per_item: list[dict], n_boot: int = 10000, seed=None) -> dict:
    """per_item: list of {corr: {score: auroc, _eligible, _n_corrupted}}. -> {corr: {score: dict(mean, lo, hi, n)}, _excluded: ...}."""
    seed = seed if seed is not None else seeds.seed_for("auroc")
    out: dict = {}
    for corr in P2_CORRS:
        rows = [p[corr] for p in per_item if corr in p]
        if not rows:
            continue
        names = sorted({k for r in rows for k in r if not k.startswith("_")})
        out[corr] = {n: dict(zip(("mean", "lo", "hi"), core.bootstrap_mean_ci(np.array([r.get(n, np.nan) for r in rows]), n_boot, seed)),
                             n=int(np.sum(~np.isnan([r.get(n, np.nan) for r in rows])))) for n in names}
        out[corr]["_n_items"] = len(rows)
        out[corr]["_n_excluded"] = int(sum(1 for r in rows if not r["_eligible"]))
    return out


def bootstrap_p(boot_means: np.ndarray) -> float:
    """Two-sided bootstrap p-value of H0: mean difference = 0, from bootstrap means of the difference: 2 * min(P(mean* <= 0), P(mean* >= 0)) with a +1 correction."""
    b = np.asarray(boot_means, float)
    k = min(int((b <= 0).sum()), int((b >= 0).sum()))
    return float(min(1.0, 2.0 * (k + 1) / (len(b) + 1)))


def _boot_diff(a: np.ndarray, b: np.ndarray, n_boot: int, seed: int):
    d = a - b
    d = d[~np.isnan(d)]
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n_boot, len(d)))
    return d, d[idx].mean(axis=1)


def candidate_means(rows, cheap=CHEAP, min_n=None) -> dict:
    """Mean per-item AUROC of every cheap candidate that has a finite value on at least one item. With `min_n` set (SAP A3b.12a item 1, partial M1 pool) a candidate is kept only if its count of
    finite values is at least `min_n`; `min_n=None` is the old behaviour."""
    cand = [c for c in cheap if any(not np.isnan(r.get(c, np.nan)) for r in rows)]
    if min_n is not None:
        cand = [c for c in cand if _n_finite(rows, c) >= min_n]
    return {c: float(np.nanmean([r.get(c, np.nan) for r in rows])) for c in cand}


def _n_finite(rows, c) -> int:
    return int(sum(1 for r in rows if not np.isnan(r.get(c, np.nan))))


def split_sign(name: str) -> tuple[str, int]:
    return (name[:-4], -1) if name.endswith("_neg") else (name, 1)


def paired_vs_best_cheap(per_item: list[dict], corr: str, target: str = "q", cheap=CHEAP, n_boot: int = 10000, seed=None, reselect: bool = False, min_n=None) -> dict:
    """Per-item AUROC of `target` minus that of the cheap rival with the highest mean AUROC on this corruption (sign included: a sign oracle; SAP A1.2 rule 2); paired bootstrap
    over items: two-sided bootstrap p, percentile CIs at 95 and 97.5 percent. reselect=True re-selects the rival inside every bootstrap resample (stricter sensitivity).
    min_n (SAP A3b.12a items 1 and 3; None = old behaviour): only candidates with at least min_n finite values are eligible, and if fewer than min_n items have a finite value for BOTH the target and the
    selected rival (in the reselect branch also: fewer than min_n items finite for the target and every eligible candidate) the result is dict(corr, available=False, reason="n < min_n", n=count)."""
    seed = seed if seed is not None else seeds.seed_for("detection_contrast")
    rows = [p[corr] for p in per_item if corr in p]
    means = candidate_means(rows, cheap, min_n) if rows else {}
    if not rows or not means or not any(not np.isnan(r.get(target, np.nan)) for r in rows):
        if min_n is not None and rows and not means:
            return dict(corr=corr, available=False, reason=f"no candidate with n >= {min_n}", n=0)
        return dict(corr=corr, available=False)
    best = max(means, key=means.get)
    a = np.array([r.get(target, np.nan) for r in rows])
    M = {c: np.array([r.get(c, np.nan) for r in rows]) for c in means}
    if min_n is not None:
        n_pair = int((~np.isnan(a) & ~np.isnan(M[best])).sum())
        if reselect:
            n_pair = min(n_pair, int((~np.isnan(a) & ~np.any(np.isnan(np.stack([M[c] for c in M])), axis=0)).sum()))
        if n_pair < min_n:
            return dict(corr=corr, available=False, reason=f"n < {min_n}", n=n_pair)
    if not reselect:
        d, boots = _boot_diff(a, M[best], n_boot, seed)
        diff = float(d.mean())
    else:
        names = list(M)
        ok = ~np.isnan(a) & ~np.any(np.isnan(np.stack([M[c] for c in names])), axis=0)
        A, R = a[ok], np.stack([M[c][ok] for c in names])
        rng = np.random.default_rng(seed)
        idx = rng.integers(0, len(A), size=(n_boot, len(A)))
        rb = R[:, idx].mean(axis=2)                                   # [candidates, B]: mean AUROC of each rival in each resample
        pick = rb.argmax(axis=0)
        boots = A[idx].mean(axis=1) - rb[pick, np.arange(n_boot)]
        diff = float(A.mean() - R[names.index(best)].mean())
    ci95 = (float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)))
    ci975 = (float(np.quantile(boots, 0.0125)), float(np.quantile(boots, 0.9875)))
    base, sign = split_sign(best)
    return dict(corr=corr, available=True, target=target, best_cheap=best, rival_base=base, rival_sign=sign, cheap_means=means, diff_mean=diff, p=bootstrap_p(boots),
                ci95=list(ci95), ci975=list(ci975), diff_lo=ci95[0], diff_hi=ci95[1], excludes_zero=bool(ci95[0] > 0 or ci95[1] < 0), reselect=reselect, n_items=int(len(rows)))


def holm_adjust(pvals: dict) -> dict:
    from exp_p2.gate import stats
    keys = list(pvals)
    return dict(zip(keys, stats.holm([pvals[k] for k in keys])))


def falsifier(per_item: list[dict], target: str = "q", n_boot: int = 10000, seed=None, reselect: bool = False, min_n=None) -> dict:
    """SAP 2.5 / A1.2: S-D over JPEG q10 and noise 0.10, Holm over m = 2. 'q beats the best cheap baseline' on a corruption iff the Holm-adjusted p <= 0.05 with a positive mean
    difference; the falsifier (spec 7.6) is met if that holds for neither corruption (a significant difference on the negative side therefore also meets it). A corruption
    without q gets p = 1 and stays in m = 2.
    min_n (SAP A3b.12a item 4; None = old behaviour, `falsified = not wins`): with min_n set, `falsified` is False if `wins` is non-empty, True if both corruptions are available (n >= min_n for
    the target and the rival) and `wins` is empty, and None ("not evaluated", neither met nor unmet) otherwise; min_n and n per corruption are returned."""
    res = {c: paired_vs_best_cheap(per_item, c, target, n_boot=n_boot, seed=seed, reselect=reselect, min_n=min_n) for c in ("jpeg", "noise")}
    if not any(r.get("available") for r in res.values()):
        out = dict(per_corruption=res, falsified=None, note="needs q (M1 post-hoc arrays) and a cheap baseline on jpeg and noise")
        if min_n is not None:
            out.update(min_n=min_n, n={c: _n_of(r) for c, r in res.items()}, note="not evaluated: n below min_n, or no q / no eligible rival")
        return out
    adj = holm_adjust({c: (r["p"] if r.get("available") else 1.0) for c, r in res.items()})
    for c, r in res.items():
        r["p_holm"] = adj[c]
    wins = [c for c, r in res.items() if r.get("available") and r["p_holm"] <= 0.05 and r["diff_mean"] > 0]
    worse = [c for c, r in res.items() if r.get("available") and r["p_holm"] <= 0.05 and r["diff_mean"] < 0]
    out = dict(per_corruption=res, falsified=bool(not wins), q_significantly_better_on=wins, q_significantly_worse_on=worse, holm_m=2, reselect=reselect,
               rule="SAP 2.5/A1.2: Holm over m = 2; falsifier met when q beats the best cheap rival (sign oracle) on neither JPEG nor noise")
    if min_n is not None:
        both = all(r.get("available") for r in res.values())
        out.update(falsified=(False if wins else (True if both else None)), min_n=min_n, n={c: _n_of(r) for c, r in res.items()})
        if out["falsified"] is None:
            out["note"] = "not evaluated: n below min_n"
        out["rule"] += "; partial pool (SAP A3b.12 rule 5): met only if both corruptions are evaluated (n >= min_n) and neither has a win, 'not evaluated' (None) otherwise"
    return out


def _n_of(r: dict) -> int:
    return int(r.get("n_items", r.get("n", 0)) or 0)


def chance_bar(per_item: list[dict], scores=("plainB", "q"), corrs=("patch", "swap"), n_boot: int = 10000, seed=None) -> dict:
    """Positive control (a) of the card / SAP A2.5, binding pass/fail: on the sanity corruptions patch and swap (uniform random codes, so a likelihood-based detector must beat chance), the
    lower 95 percent bound of the mean per-item AUROC against the changed-code labels is above 0.5 for plain-B and for q (q only on items that have D). The level and the comparison
    with the cheap rivals are descriptive. A failure triggers the pipeline audit of C1; nothing is tuned. Passing says nothing about JPEG, noise or splice."""
    seed = seed if seed is not None else seeds.seed_for("auroc")
    out, results = {}, []
    for corr in corrs:
        rows = [p[corr] for p in per_item if corr in p]
        for sc in scores:
            v = np.array([r.get(sc, np.nan) for r in rows], float)
            v = v[~np.isnan(v)]
            key = f"{corr}/{sc}"
            if v.size < 2:
                out[key] = dict(available=False, n=int(v.size), passes=None)
                results.append(None)
                continue
            m, lo, hi = core.bootstrap_mean_ci(v, n_boot, seed)
            out[key] = dict(available=True, n=int(v.size), mean=m, lower95=lo, upper95=hi, passes=bool(lo > 0.5))
            results.append(bool(lo > 0.5))
    failed = any(r is False for r in results)
    return dict(per_score=out, passes=(False if failed else (None if (None in results or not results) else True)), failed=bool(failed), audit_trigger=bool(failed), n_unavailable=int(sum(r is None for r in results)),
                rule="SAP A2.5: lower 95 percent bound of the mean per-item AUROC > 0.5 for plain-B and q on patch and swap (descriptive level); failure = pipeline audit, nothing tuned")


def freeze_rivals(per_item: list[dict], corrs=("jpeg", "noise"), cheap=CHEAP, min_n=None) -> dict:
    """detection_frozen.json content (SAP A1.2 rule 5): per corruption the selected rival, its base name, sign and mean AUROC on the M1 items. Frozen after M1 and before M3/M4,
    tested on the M4 test items (family S-D2). Rarity for S-D2 uses the calibration codefreq (A1.3 N11), recorded here.
    min_n (SAP A3b.12a item 2; None = old behaviour, entry unchanged): only candidates with at least min_n finite per-item AUROCs on the corruption are eligible; with none the entry is
    dict(available=False, reason="no candidate with n >= min_n", n_pool=len(rows)); otherwise n_items = the finite count of the selected rival, n_pool = len(rows), all_n = finite count per candidate."""
    out = {}
    for c in corrs:
        rows = [p[c] for p in per_item if c in p]
        m = candidate_means(rows, cheap, min_n) if rows else {}
        if not m:
            out[c] = dict(available=False) if min_n is None else dict(available=False, reason=f"no candidate with n >= {min_n}", n_pool=len(rows))
            continue
        best = max(m, key=m.get)
        base, sign = split_sign(best)
        out[c] = dict(available=True, rival=best, base=base, sign=sign, mean_auroc=m[best], n_items=len(rows), all_means=m, label=(baselines.TBV_LABEL if base == "tbv" else None),
                      rarity_source="runs/P2-GATE-M2/codefreq.npy (calibration clean codes)" if base == "rarity" else None)
        if min_n is not None:
            out[c].update(n_items=_n_finite(rows, best), n_pool=len(rows), all_n={k: _n_finite(rows, k) for k in m}, min_n=min_n)
    return out
