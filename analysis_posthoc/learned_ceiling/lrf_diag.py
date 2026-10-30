"""Diagnostics for the frozen LRF model (CPU only): feature reading, mechanism, and the caption-length / layout checks.

    python -m analysis_posthoc.learned_ceiling.lrf_diag      -> runs/P2-LRF-FROZEN/diagnostics.json

Everything here is descriptive. In-sample quantities use the frozen model (trained on these 500 items) and are optimistic;
the length test on decision gains uses the cross-fitted F1 decisions of runs/P2-POSTHOC-LEARNED/ckpt (honest out-of-fold).
Permutation p-values are diagnostics for the layout question only (not claims about LRF).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from . import data
from .lrf import FROZEN, REPO, gam_f, load_frozen, weights_from_raw
from .run import ARR, N_ITEMS, outer_folds

DCACHE = REPO / "runs" / "P2-GATE-DCACHE"
N_PERM = 10000
GROUPS = {"raw": ["B", "D", "q", "s3", "tbv", "ltex", "nbr"], "position": ["row", "col", "rad"],
          "neighbourhood": ["nb3mean_q", "nb3mean_B", "nb3mean_s3", "nb3mean_tbv", "nb3mean_ltex", "nb3mean_nbr", "nb3min_q", "nb5mean_q"],
          "rank": ["rank_q", "rank_B", "rank_s3", "rank_tbv"],
          "item": [f"itemmean_{k}" for k in data.ITEM_STATS] + [f"itemsd_{k}" for k in data.ITEM_STATS] + ["itemz_q"]}


def perm_p(stat_fn, x, y, rng, n=N_PERM):
    obs = stat_fn(x, y)
    null = np.array([stat_fn(x, rng.permutation(y)) for _ in range(n)])
    return float(obs), float((np.sum(np.abs(null) >= abs(obs)) + 1) / (n + 1))


def rho(x, y):
    return float(spearmanr(x, y).statistic)


def main():
    fz = load_frozen()
    names = data.feature_names()
    d = data.load(ARR, N_ITEMS)
    X = data.engineer(d["raw"])
    delta, z = d["delta"], d["z"]
    W = weights_from_raw(fz, d["raw"])
    Y = (W * delta).sum(-1) > 0
    Y0 = delta.mean(-1) > 0
    out = {"label": "descriptive; in-sample unless stated; frozen model trained on these items"}

    # ---- 1. feature reading: per-feature contribution g_k on a token subsample
    rng = np.random.default_rng(20261029)
    sub = rng.integers(0, data.M, 64)
    Xs = ((X[:, :, sub] - fz["mu"]) / fz["sd"]).astype(np.float64)              # [500, 4, 64, F]
    a, c, kn = fz["a"], fz["c"], fz["knots"]
    G = a * Xs + np.einsum("...fk,fk->...f", np.maximum(Xs[..., None] - kn, 0.0), c)   # [500, 4, 64, F]
    feat = {}
    for k, nm in enumerate(names):
        g = G[..., k]
        qs = np.quantile(X[:, :, sub, k], [0.05, 0.25, 0.5, 0.75, 0.95])
        xs = (qs - fz["mu"][k]) / fz["sd"][k]
        gq = a[k] * xs + (np.maximum(xs[:, None] - kn[k], 0) * c[k]).sum(-1)
        feat[nm] = dict(contrib_sd=float(g.std()), contrib_sd_by_cond={cn: float(g[:, ci].std()) for ci, cn in enumerate(data.COND)},
                        mean_shift_vs_clean={cn: float(g[:, ci].mean() - g[:, 0].mean()) for ci, cn in enumerate(data.COND)},
                        x_quantiles_5_25_50_75_95=[float(v) for v in qs], g_at_quantiles=[float(v - gq[2]) for v in gq])
    order = sorted(names, key=lambda n: -feat[n]["contrib_sd"])
    out["features_ranked_by_contribution_sd"] = order
    out["feature_shapes"] = feat
    out["intercept"] = float(fz["b"])

    # group occlusion: set a group's standardised inputs to 0 (training mean), in-sample accuracy
    occl = {}
    for gname, cols in GROUPS.items():
        idx = [names.index(cn) for cn in cols]
        acc = {}
        for ci, cn in enumerate(data.COND):
            Wc = np.empty((N_ITEMS, data.M))
            for s in range(0, N_ITEMS, 20):
                xs_ = ((X[s:s + 20, ci] - fz["mu"]) / fz["sd"]).astype(np.float64)
                xs_[..., idx] = 0.0
                Wc[s:s + 20] = 1 / (1 + np.exp(-gam_f(fz, xs_)))
            acc[cn] = float(((Wc * delta[:, ci]).sum(-1) > 0).mean())
        occl[gname] = acc
    out["group_occlusion_insample_accuracy"] = occl
    out["insample_accuracy"] = {cn: float(Y[:, ci].mean()) for ci, cn in enumerate(data.COND)}
    out["none_accuracy"] = {cn: float(Y0[:, ci].mean()) for ci, cn in enumerate(data.COND)}

    # ---- 2. mechanism: weight quintiles (pooled tokens, per condition) vs Delta and z
    mech = {}
    for ci, cn in enumerate(data.COND):
        w, dl, zz = W[:, ci].ravel(), delta[:, ci].ravel(), z[:, ci].ravel()
        edges = np.quantile(w, [0.2, 0.4, 0.6, 0.8])
        qi = np.digitize(w, edges)
        rows = []
        for b in range(5):
            m = qi == b
            rows.append(dict(w_mean=float(w[m].mean()), delta_mean=float(dl[m].mean()), delta_sd=float(dl[m].std()),
                             snr=float(dl[m].mean() / dl[m].std()), share_z=float(zz[m].mean())))
        # same-position clean evidence: does w track where the clean image carried evidence?
        dclean = delta[:, 0].ravel()
        mech[cn] = dict(w_mean=float(w.mean()), w_sd=float(w.std()), share_w_below_0p2=float((w < 0.2).mean()),
                        rho_w_q=rho(w[::7], d["raw"]["q"][:, ci].ravel()[::7]), rho_w_z=rho(w[::7], zz[::7]) if zz.any() and not zz.all() else None,
                        rho_w_delta=rho(w[::7], dl[::7]), rho_w_clean_delta_same_pos=rho(w[::7], dclean[::7]),
                        within_item_rho_w_delta_mean=float(np.nanmean([rho(W[i, ci], delta[i, ci]) for i in range(0, N_ITEMS, 5)])),
                        quintiles=rows)
    out["mechanism"] = mech

    # ---- 3. caption length / layout checks
    rows = [json.loads(l) for l in open(REPO / "runs/P2-GATE-M4/items.jsonl", encoding="utf8")]
    n_pos = np.array([r["n_tok"] for r in rows])
    n_neg = np.array([r["n_tok_neg"] for r in rows])
    dlen = n_pos - n_neg
    prng = np.random.default_rng(7)
    L = {"n_items": N_ITEMS, "n_equal_length": int((dlen == 0).sum()), "n_pos_longer": int((dlen > 0).sum()), "n_neg_longer": int((dlen < 0).sum())}
    # 3a. do caption-withheld features encode the true length? (item means of raw scores -> n_pos, 5-fold ridge, permutation)
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import cross_val_predict
    Z = np.concatenate([np.stack([d["raw"][k].mean(-1) for k in data.RAW], -1).reshape(N_ITEMS, -1),
                        np.stack([d["raw"][k].std(-1) for k in data.RAW], -1).reshape(N_ITEMS, -1)], 1)
    Z = (Z - Z.mean(0)) / Z.std(0)
    def r2(Zm, y):
        p = cross_val_predict(RidgeCV(alphas=np.logspace(-3, 3, 13)), Zm, y, cv=5)
        return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    r2_obs = float(r2(Z, n_pos))
    null = [r2(Z, prng.permutation(n_pos)) for _ in range(200)]
    L["encoding_r2_npos_from_item_feature_summaries"] = dict(r2_cv=r2_obs, perm_null_max=float(np.max(null)), perm_p=float((np.sum(np.array(null) >= r2_obs) + 1) / 201), n_perm=200)
    # 3b. do weights depend on length? item-mean weight vs n_pos and vs dlen
    wl = {}
    for ci, cn in enumerate(data.COND):
        wm = W[:, ci].mean(-1)
        r1, p1 = perm_p(rho, wm, n_pos, prng, 2000)
        r2_, p2 = perm_p(rho, wm, dlen, prng, 2000)
        wl[cn] = dict(rho_itemmeanw_npos=r1, perm_p_npos=p1, rho_itemmeanw_dlen=r2_, perm_p_dlen=p2)
    L["weights_vs_length"] = wl
    # 3c. decision gain (cross-fitted F1 minus NONE) vs length difference
    Ycf = np.zeros((N_ITEMS, 4), bool)
    for k in range(5):
        zf = np.load(REPO / "runs/P2-POSTHOC-LEARNED/ckpt" / f"F1_fold{k}.npz")
        Ycf[zf["test"]] = zf["y"]
    gain = {}
    for ci, cn in enumerate(data.COND):
        g = Ycf[:, ci].astype(int) - Y0[:, ci].astype(int)
        strata = {}
        for nm, m in (("neg_longer", dlen < 0), ("equal", dlen == 0), ("pos_longer", dlen > 0)):
            strata[nm] = dict(n=int(m.sum()), acc_none=float(Y0[m, ci].mean()), acc_lrf_crossfit=float(Ycf[m, ci].mean()),
                              gain=float(g[m].mean()), b=int((g[m] == 1).sum()), c=int((g[m] == -1).sum()))
        r_, p_ = perm_p(rho, g, dlen, prng)
        diff_fn = lambda gg, dd: gg[dd > 0].mean() - gg[dd < 0].mean()
        dobs, dp = perm_p(diff_fn, g, dlen, prng)
        acc_none_vs_dlen = rho(Y0[:, ci].astype(int), dlen)
        gain[cn] = dict(strata=strata, rho_gain_dlen=r_, perm_p_rho=p_, gain_pos_longer_minus_neg_longer=dobs, perm_p_diff=dp,
                        rho_none_correct_dlen=acc_none_vs_dlen)
    L["crossfit_gain_vs_length"] = gain
    # 3d. counterfactual D: rescore D at the NEGATIVE caption's layout length (from the D cache), keep B, tbv; frozen model
    raw_cf = {k: v.copy() for k, v in d["raw"].items()}
    for n in np.unique(n_neg):
        DI = np.load(DCACHE / f"DI_n{n:03d}.npy", mmap_mode="r")
        for i in np.where(n_neg == n)[0]:
            for ci in range(4):
                raw_cf["D"][i, ci] = DI[np.arange(data.M), d["codes"][i, ci]]
    raw_cf["q"] = raw_cf["B"] - raw_cf["D"]
    Wcf = weights_from_raw(fz, raw_cf)
    Ycf_d = (Wcf * delta).sum(-1) > 0
    raw_sym = {k: v.copy() for k, v in d["raw"].items()}
    raw_sym["D"] = 0.5 * (d["raw"]["D"] + raw_cf["D"])
    raw_sym["q"] = raw_sym["B"] - raw_sym["D"]
    Ysym = (weights_from_raw(fz, raw_sym) * delta).sum(-1) > 0
    L["counterfactual_D_layout"] = {cn: dict(acc_factual=float(Y[:, ci].mean()), acc_D_at_neg_length=float(Ycf_d[:, ci].mean()),
                                             acc_D_symmetric=float(Ysym[:, ci].mean()),
                                             flips_neg=int((Y[:, ci] != Ycf_d[:, ci]).sum()), flips_sym=int((Y[:, ci] != Ysym[:, ci]).sum()),
                                             flips_neg_unequal_items_only=int(((Y[:, ci] != Ycf_d[:, ci]) & (dlen != 0)).sum()),
                                             mean_abs_w_change=float(np.abs(W[:, ci] - Wcf[:, ci]).mean()))
                                    for ci, cn in enumerate(data.COND)}
    L["note"] = ("Only D can be re-scored at the other layout from stored data (D cache keyed by caption length); B and tbv also carry the "
                 "true-length layout and cannot be re-scored without the GPU. On the 59 equal-length items the layout is identical under either "
                 "caption, so no layout leak is possible there.")
    out["length_checks"] = L
    # ---- 4. no-training rules: keep the top fraction f of tokens within each item by a caption-withheld score (every f reported)
    rules = {}
    for sname in ("q", "B", "tbv"):
        s = d["raw"][sname]
        r = np.argsort(np.argsort(-s, axis=-1), axis=-1)               # 0 = highest score
        for f in (0.05, 0.1, 0.2, 0.3, 0.5):
            keep = r < int(round(f * data.M))
            Yk = (delta * keep).sum(-1) > 0
            rules[f"top{int(f * 100)}_{sname}"] = {cn: float(Yk[:, ci].mean()) for ci, cn in enumerate(data.COND)}
    out["topk_rules_accuracy"] = rules
    (FROZEN / "diagnostics.json").write_text(json.dumps(out, indent=1), encoding="utf8")
    print(json.dumps({k: out[k] for k in ("features_ranked_by_contribution_sd", "group_occlusion_insample_accuracy", "insample_accuracy")}, indent=1))
    print(json.dumps(out["length_checks"], indent=1))
    print(json.dumps({cn: {k: v for k, v in m.items() if k != "quintiles"} | {"q": [(round(r["w_mean"], 2), round(r["delta_mean"], 3), round(r["snr"], 3), round(r["share_z"], 2)) for r in m["quintiles"]]} for cn, m in out["mechanism"].items()}, indent=1))


if __name__ == "__main__":
    main()
