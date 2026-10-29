"""Post hoc, exploratory: ceiling of learned reliability weighting on the M4 test items.

Plan: research/paper2/posthoc/LEARNED-CEILING-PLAN-2026-10-29.md (committed d457d295 before any result).
CPU only. Usage (from the repo root):
    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
      python -m analysis_posthoc.learned_ceiling.run --timing          # timing smoke only (no accuracy)
    ... python -m analysis_posthoc.learned_ceiling.run                 # full run (resumes from checkpoints)
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np  # noqa: E402
import scipy  # noqa: E402
import sklearn  # noqa: E402
import torch  # noqa: E402

from . import data, families as fam, stats  # noqa: E402

torch.set_num_threads(4)
ROOT_SEED = 20261029
REPO = Path(__file__).resolve().parents[2]
ARR = REPO / "runs" / "P2-GATE-M4" / "arrays"
OUT = REPO / "runs" / "P2-POSTHOC-LEARNED"
N_ITEMS, N_OUTER, N_INNER, ETA = 500, 5, 3, 3
N_BOOT = 10000
FINAL_SEEDS = {"F1": 1, "F2": 1, "F3": 3, "F4": 3}
LABEL = "post hoc, exploratory (not preregistered); CIs only, no p-values; cannot rescue, explain or qualify P (AB.1)"


def ss(*key) -> np.random.SeedSequence:
    return np.random.SeedSequence(ROOT_SEED, spawn_key=tuple(key))


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(OUT / "stdout.txt", "a", encoding="utf8") as f:
        f.write(line + "\n")


def make_families(n_cfg: dict, rmax: dict):
    return [fam.F1GAM("F1", rmax["F1"], n_cfg["F1"]), fam.F2GBT("F2", rmax["F2"], n_cfg["F2"]),
            fam.F3MLP("F3", rmax["F3"], n_cfg["F3"]), fam.F4Grid("F4", rmax["F4"], n_cfg["F4"])]


def outer_folds():
    perm = np.random.default_rng(ss(0)).permutation(N_ITEMS)
    return [np.sort(perm[k * 100:(k + 1) * 100]) for k in range(N_OUTER)]


def inner_folds(train: np.ndarray, k: int):
    perm = np.random.default_rng(ss(1, k)).permutation(train)
    return [np.sort(a) for a in np.array_split(perm, N_INNER)]


def rungs(rmax: int, n_cfg: int):
    n_r = 3 if n_cfg >= 9 else 3                       # 9 -> 3 -> 1 or 6 -> 2 -> 1
    return [max(1, int(round(rmax / ETA ** (n_r - 1 - r)))) for r in range(n_r)]


def successive_halving(ctx, family, train, k, fi):
    rng = np.random.default_rng(ss(2, k, fi))
    cfgs = [family.sample(rng) for _ in range(family.n_configs)]
    inner = inner_folds(train, k)
    alive, hlog = list(range(len(cfgs))), []
    res = rungs(family.rmax, family.n_configs)
    scores = {}
    for ri, r in enumerate(res):
        scores = {}
        for ci in alive:
            fold_scores, fold_acc = [], []
            for ii, val in enumerate(inner):
                tr = np.setdiff1d(train, val)
                seed = int(ss(3, k, fi, ci, ii).generate_state(1)[0])
                t0 = time.time()
                model = family.fit(ctx, cfgs[ci], tr, r, seed)
                w = family.weights(ctx, model, val)
                T = fam.temperature(ctx.delta[tr])
                fold_scores.append(fam.o1_criterion(w, ctx.delta[val], T))
                fold_acc.append(float(((w * ctx.delta[val]).sum(-1) > 0).mean()))
                hlog.append(dict(rung=ri, resource=r, cfg=ci, inner_fold=ii, o1=fold_scores[-1], acc=fold_acc[-1], sec=round(time.time() - t0, 2)))
            scores[ci] = float(np.mean(fold_scores))
        keep = max(1, int(np.ceil(len(alive) / ETA))) if ri < len(res) - 1 else 1
        alive = sorted(alive, key=lambda c: scores[c])[:keep]
    best = alive[0]
    return cfgs[best], scores[best], dict(configs=cfgs, rungs=res, log=hlog, best=best, best_score=scores[best])


def decisions(w, delta):
    s = (w * delta).sum(-1)
    return s > 0, (w.sum(-1) <= 0)


def run_family_fold(ctx, family, fi, k, test, train):
    ck = OUT / "ckpt" / f"{family.name}_fold{k}.npz"
    if ck.exists():
        return
    t0 = time.time()
    cfg, score, hl = successive_halving(ctx, family, train, k, fi)
    ys, ws = [], []
    for s in range(FINAL_SEEDS[family.name]):
        seed = int(ss(4, k, fi, s).generate_state(1)[0])
        model = family.fit(ctx, cfg, train, family.rmax, seed)
        w = family.weights(ctx, model, test)
        ws.append(w)
        ys.append(decisions(w, ctx.delta[test])[0])
    wbar = np.mean(ws, 0)
    y, empty = decisions(wbar, ctx.delta[test])
    extra = {}
    if family.name == "F2":                     # labelled variants with F2's selected configuration (plan Section 6)
        for kind in ("cond", "z"):
            v = fam.F2GBT(f"F2+{kind}", family.rmax, 1, extra=kind)
            mv = v.fit(ctx, cfg, train, family.rmax, int(ss(5, k, kind == "z").generate_state(1)[0]))
            wv = v.weights(ctx, mv, test)
            extra[f"y_{kind}"], extra[f"empty_{kind}"] = decisions(wv, ctx.delta[test])
    np.savez_compressed(ck, test=test, y=y, empty=empty, y_seeds=np.array(ys), inner_score=score, **extra)
    (OUT / "hpo").mkdir(exist_ok=True)
    hl.update(family=family.name, outer_fold=k, selected_cfg=cfg, final_seeds=FINAL_SEEDS[family.name], sec_total=round(time.time() - t0, 1))
    (OUT / "hpo" / f"{family.name}_fold{k}.json").write_text(json.dumps(hl, indent=1), encoding="utf8")
    log(f"{family.name} fold {k}: inner O1 {score:.4f}, cfg {cfg}, {time.time() - t0:.0f}s")


def run_reference_fold(ctx, k, test, train):
    ck = OUT / "ckpt" / f"REF_fold{k}.npz"
    if ck.exists():
        return
    out = {}
    # ZSNR: two-class matched filter per corruption from training-fold moments
    w = np.ones((len(test), 4, data.M), np.float32)
    moments = {}
    for c in range(1, 4):
        d_tr, z_tr = ctx.delta[train][:, c], ctx.z[train][:, c]
        mom = {}
        for zz in (0, 1):
            v = d_tr[z_tr == bool(zz)]
            mom[zz] = (float(v.mean()), float(v.var())) if v.size > 1 else (0.0, 1.0)
        moments[data.COND[c]] = mom
        zt = ctx.z[test][:, c]
        for zz in (0, 1):
            w[:, c][zt == bool(zz)] = max(mom[zz][0], 0.0) / max(mom[zz][1], 1e-8)
    out["y_zsnr"], out["empty_zsnr"] = decisions(w, ctx.delta[test])
    # detector (secondary) and its soft gate
    clf = fam.fit_detector(ctx, train, int(ss(6, k).generate_state(1)[0]))
    p = fam.detector_proba(ctx, clf, test)
    out["y_det"], out["empty_det"] = decisions(1.0 - p, ctx.delta[test])
    out["p_det"] = p.astype(np.float16)
    np.savez_compressed(ck, test=test, **out)
    (OUT / "hpo" / f"REF_fold{k}.json").write_text(json.dumps(dict(zsnr_moments=moments, detector_n_iter=int(clf.n_iter_)), indent=1), encoding="utf8")
    log(f"REF fold {k} done")


def per_item_auroc(score, z):
    """Mean per-item AUROC (items with both classes) and item list of AUROCs. score, z: [n, M]."""
    from scipy.stats import rankdata
    vals = []
    for s, y in zip(score, z):
        n1 = int(y.sum())
        n0 = y.size - n1
        if n1 == 0 or n0 == 0:
            vals.append(np.nan)
            continue
        r = rankdata(s)
        vals.append((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))
    return np.array(vals)


def env_info():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    except Exception:
        head = None
    return dict(python=sys.version, platform=platform.platform(), numpy=np.__version__, scipy=scipy.__version__, sklearn=sklearn.__version__,
                torch=torch.__version__, torch_threads=torch.get_num_threads(), cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"),
                omp=os.environ.get("OMP_NUM_THREADS"), mkl=os.environ.get("MKL_NUM_THREADS"), git_head=head, optuna="not used (venv has no pip; venv not modified during S2)")


def build_ctx():
    t0 = time.time()
    d = data.load(ARR, N_ITEMS)
    X = data.engineer(d["raw"])
    mask = data.token_subsample(ss(7), d["delta"].shape, 0.25)
    log(f"data loaded: X {X.shape} {X.nbytes / 1e9:.2f} GB in {time.time() - t0:.0f}s")
    return SimpleNamespace(X=X, delta=d["delta"], z=d["z"], gm=d["gm"], codes=d["codes"], mask=mask, raw=d["raw"])


def timing(ctx, fams):
    folds = outer_folds()
    train = np.setdiff1d(np.arange(N_ITEMS), folds[0])
    val = inner_folds(train, 0)[0]
    tr = np.setdiff1d(train, val)
    out = {}
    for f in fams:
        t0 = time.time()
        m = f.fit(ctx, f.sample(np.random.default_rng(ss(9))), tr, f.rmax, 1)
        t1 = time.time()
        f.weights(ctx, m, val)
        t2 = time.time()
        sh_units = sum(n * r for n, r in zip([f.n_configs, int(np.ceil(f.n_configs / 3)), 1], [1 / 9, 1 / 3, 1]))
        per_fold = (t2 - t0) * N_INNER * sh_units + (t1 - t0) * 1.5 * FINAL_SEEDS[f.name]
        out[f.name] = dict(fit_sec=round(t1 - t0, 1), predict_sec=round(t2 - t1, 1), rmax=f.rmax, n_configs=f.n_configs,
                           projected_min_per_outer_fold=round(per_fold / 60, 1), projected_min_total=round(per_fold * N_OUTER / 60, 1))
        log(f"timing {f.name}: {out[f.name]}")
    out["projected_min_all"] = round(sum(v["projected_min_total"] for v in out.values()), 1)
    out["note"] = "fit at the maximum resource on inner-training items of outer fold 0 / inner fold 0; no accuracy computed"
    (OUT / "timing_smoke.json").write_text(json.dumps(out, indent=1), encoding="utf8")
    return out


def analyse(ctx, fams):
    folds = outer_folds()
    N = N_ITEMS
    Y = {}
    # no-learning arms
    Y["NONE"] = ctx.delta.mean(-1) > 0
    keep = ~ctx.gm
    s = (ctx.delta * keep).sum(-1)
    Y["GM"] = s > 0
    Y["CHG"] = (ctx.delta * ~ctx.z).sum(-1) > 0
    Y["RESTORE-CLEAN"] = np.repeat(Y["NONE"][:, :1], 4, 1)
    Y["UNRESTRICTED"] = ctx.delta.max(-1) > 0
    empties = {"GM": int((keep.sum(-1) == 0).sum()), "CHG": (~ctx.z).sum(-1) == 0}
    # checks against committed files
    t3 = json.loads((REPO / "runs/P2-GATE-M4/tier3_fusion.json").read_text())
    an = json.loads((REPO / "runs/P2-GATE-M4/analysis.json").read_text())
    checks = {}
    for c, name in enumerate(data.COND):
        cell = t3["clean"] if name == "clean" else t3["cells"][name]
        for arm in ("NONE", "GM"):
            mine, ref = float(Y[arm][:, c].mean()), cell["arms"][arm]["acc"]
            checks[f"{name}/{arm}"] = dict(recomputed=mine, tier3=ref, match=abs(mine - ref) < 1e-9)
        if name != "clean":
            ref = an["mechanism"][name]["y"]["changed_code_minus_none"]["diff"]
            mine = float(Y["CHG"][:, c].mean() - Y["NONE"][:, c].mean())
            checks[f"{name}/CHG-minus-NONE"] = dict(recomputed=mine, analysis_json=ref, match=abs(mine - ref) < 1e-9)
    if not all(v["match"] for v in checks.values()):
        (OUT / "checks_FAILED.json").write_text(json.dumps(checks, indent=1))
        raise SystemExit("reference check failed; see checks_FAILED.json")
    # learned arms
    inner = {}
    seeds_acc = {}
    n_empty = {}
    for f in fams:
        y = np.zeros((N, 4), bool)
        e = np.zeros((N, 4), bool)
        ysd = []
        for k in range(N_OUTER):
            z = np.load(OUT / "ckpt" / f"{f.name}_fold{k}.npz")
            y[z["test"]], e[z["test"]] = z["y"], z["empty"]
            inner.setdefault(f.name, []).append(float(z["inner_score"]))
            ysd.append((z["test"], z["y_seeds"]))
            if f.name == "F2":
                for kind in ("cond", "z"):
                    Y.setdefault(f"F2+{kind}", np.zeros((N, 4), bool))[z["test"]] = z[f"y_{kind}"]
        Y[f.name], n_empty[f.name] = y, int(e.sum())
        if FINAL_SEEDS[f.name] > 1:
            per_seed = np.zeros((FINAL_SEEDS[f.name], N, 4), bool)
            for test, ys in ysd:
                per_seed[:, test] = ys
            seeds_acc[f.name] = {name: [float(a) for a in per_seed[:, :, c].mean(1)] for c, name in enumerate(data.COND)}
    sel = np.zeros((N, 4), bool)
    sel_choice = []
    for k in range(N_OUTER):
        best = min(fams, key=lambda f: inner[f.name][k]).name
        sel_choice.append(best)
        sel[folds[k]] = Y[best][folds[k]]
    Y["SEL"] = sel
    zsnr, det, pdet = np.zeros((N, 4), bool), np.zeros((N, 4), bool), np.zeros((N, 4, data.M), np.float32)
    for k in range(N_OUTER):
        z = np.load(OUT / "ckpt" / f"REF_fold{k}.npz")
        zsnr[z["test"]], det[z["test"]], pdet[z["test"]] = z["y_zsnr"], z["y_det"], z["p_det"].astype(np.float32)
    Y["ZSNR"], Y["DET"] = zsnr, det
    # statistics
    boot = np.random.default_rng(ss(8)).integers(0, N, (N_BOOT, N)).astype(np.int32)
    arms_learned = ["SEL", "F1", "F2", "F3", "F4", "F2+cond", "DET"]
    arms_oracle = ["F2+z", "ZSNR", "CHG", "RESTORE-CLEAN", "UNRESTRICTED"]
    res = {}
    n_int = 0
    for c, name in enumerate(data.COND):
        cell = {"accuracy": {}, "vs_NONE": {}, "vs_GM": {}}
        for arm, y in Y.items():
            k_ = int(y[:, c].sum())
            cell["accuracy"][arm] = dict(acc=k_ / N, wilson95=stats.wilson(k_, N))
        for arm in arms_learned + arms_oracle + ["GM"]:
            if name == "clean" and arm in ("RESTORE-CLEAN", "CHG", "ZSNR"):
                continue
            if arm != "GM":
                cell["vs_GM"][arm] = stats.contrast(Y[arm][:, c], Y["GM"][:, c], boot)
                n_int += 1
            cell["vs_NONE"][arm] = stats.contrast(Y[arm][:, c], Y["NONE"][:, c], boot)
            n_int += 1
        res[name] = cell
    # secondary detector table
    det_tab = {}
    u = -ctx.raw["q"]
    for c in range(1, 4):
        name = data.COND[c]
        a_det = per_item_auroc(pdet[:, c], ctx.z[:, c])
        a_q = per_item_auroc(u[:, c], ctx.z[:, c])
        ok = ~np.isnan(a_det) & ~np.isnan(a_q)
        bi = boot[:, :]
        def bci(v):
            vv = v[ok]
            idx = np.random.default_rng(ss(8, c)).integers(0, vv.size, (N_BOOT, vv.size))
            m = vv[idx].mean(1)
            return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]
        det_tab[name] = dict(n_items_both_classes=int(ok.sum()), auroc_detector=float(a_det[ok].mean()), auroc_detector_ci95=bci(a_det),
                             auroc_u=float(a_q[ok].mean()), auroc_u_ci95=bci(a_q), diff=float((a_det[ok] - a_q[ok]).mean()),
                             diff_ci95=bci(a_det - a_q), mean_share_changed=float(ctx.z[:, c].mean()))
    results = dict(label=LABEL, plan="research/paper2/posthoc/LEARNED-CEILING-PLAN-2026-10-29.md (commit d457d295)",
                   n_items=N, conditions=list(data.COND), features=data.feature_names(), checks=checks,
                   arms=dict(learned=arms_learned, oracle_or_reference=arms_oracle + ["NONE", "GM"],
                             definitions={"SEL": "per outer fold, the family with the lowest inner-CV O1 criterion",
                                          "F2+cond": "F2 with condition one-hot (knows the corruption type); F2's selected cfg",
                                          "F2+z": "ORACLE: F2 with condition one-hot and true z; F2's selected cfg",
                                          "DET": "weight 1 - p_hat(z) from the learned detector (secondary)",
                                          "ZSNR": "ORACLE: two-class matched filter max(mu_cz,0)/var_cz from training-fold moments, true z and corruption type",
                                          "CHG": "changed-code drop w = 1 - z (oracle)", "RESTORE-CLEAN": "the clean decision of the same item",
                                          "UNRESTRICTED": "vacuous: share of items with max_j Delta_j > 0"}),
                   sel_choice=sel_choice, inner_o1=inner, seed_spread=seeds_acc, n_empty=n_empty,
                   n_empty_reference=dict(GM=empties["GM"], CHG={data.COND[c]: int(empties["CHG"][:, c].sum()) for c in range(4)}),
                   results=res, detector_secondary=dict(caveat="K2 label circularity (D0074): z is defined after a VQ re-encode; descriptive only, no claim", table=det_tab),
                   multiplicity=dict(n_intervals=n_int, statement="no multiplicity adjustment; no p-values"),
                   bootstrap=dict(n=N_BOOT, interval="percentile 2.5/97.5, item resampling, one index matrix for all contrasts"),
                   timing=json.loads((OUT / "timing_smoke.json").read_text()) if (OUT / "timing_smoke.json").exists() else None,
                   families={f.name: dict(rmax=f.rmax, n_configs=f.n_configs, rungs=rungs(f.rmax, f.n_configs), final_seeds=FINAL_SEEDS[f.name]) for f in fams})
    (OUT / "results.json").write_text(json.dumps(results, indent=1), encoding="utf8")
    log("results.json written")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing", action="store_true")
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--budget", default=None, help="json file with n_configs/rmax overrides (written after the timing smoke)")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ckpt").mkdir(exist_ok=True)
    (OUT / "hpo").mkdir(exist_ok=True)
    n_cfg = dict(F1=9, F2=9, F3=9, F4=9)
    rmax = dict(F1=40, F2=450, F3=30, F4=30)
    if a.budget:
        b = json.loads(Path(a.budget).read_text())
        n_cfg.update(b.get("n_configs", {}))
        rmax.update(b.get("rmax", {}))
    (OUT / "env.json").write_text(json.dumps(dict(env_info(), n_configs=n_cfg, rmax=rmax), indent=1), encoding="utf8")
    fams = make_families(n_cfg, rmax)
    ctx = build_ctx()
    if a.timing:
        timing(ctx, fams)
        return
    if not a.analyse_only:
        folds = outer_folds()
        for k, test in enumerate(folds):
            train = np.setdiff1d(np.arange(N_ITEMS), test)
            run_reference_fold(ctx, k, test, train)
            for fi, f in enumerate(fams):
                run_family_fold(ctx, f, fi, k, test, train)
    analyse(ctx, fams)


if __name__ == "__main__":
    main()
