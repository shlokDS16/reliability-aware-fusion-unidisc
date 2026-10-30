"""LRF (learned reliability-aware evidence fusion): freeze the logistic-GAM (F1) on all 500 M4 items, and CPU inference.

Freeze (decision D0082; CPU only):
    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 python -m analysis_posthoc.learned_ceiling.lrf --freeze
Inference on one stored item (no GPU, no model download):
    from analysis_posthoc.learned_ceiling.lrf import load_frozen, infer_item
    fz = load_frozen(); out = infer_item(fz, np.load(".../item0000.npz"), "noise0.1")   # -> weights [1024], decision, margin

Hyperparameters are chosen by the same random search with successive halving and 3 inner folds as the learned-ceiling run
(9 configurations, rungs 4 / 13 / 40 epochs), here on all 500 items (no outer fold); the selected configuration is refitted
once on all 500 items with one fixed seed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402
import torch  # noqa: E402

from . import data, families as fam  # noqa: E402

torch.set_num_threads(4)
REPO = Path(__file__).resolve().parents[2]
FROZEN = REPO / "runs" / "P2-LRF-FROZEN"
FROZEN_KEY = 99                        # seed-spawn key for the frozen fit (outer folds used 0..4)
CODE_FILES = ("data.py", "families.py", "lrf.py")


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- inference (one item, one condition)
def raw_from_npz(d, cond: str) -> dict:
    """The 7 raw caption-withheld scores of one condition, exactly as data.load builds them. Shapes [1, 1, 1024]."""
    B, D = d[f"{cond}_B"].astype(np.float32), d[f"{cond}_D"].astype(np.float32)
    raw = dict(B=B, D=D, q=B - D, s3=d[f"{cond}_s3"].astype(np.float32), tbv=d[f"{cond}_tbv"].astype(np.float32),
               ltex=np.log1p(np.maximum(d[f"{cond}_tex"], 0)).astype(np.float32), nbr=d[f"{cond}_nbr"].astype(np.float32))
    return {k: v.reshape(1, 1, -1) for k, v in raw.items()}


def gam_f(fz: dict, Xs: np.ndarray) -> np.ndarray:
    """f = b + sum_k a_k x_k + sum_km c_km relu(x_k - t_km) on standardised features Xs [..., F]."""
    f = Xs @ fz["a"] + fz["b"]
    if fz["knots"].shape[1]:
        f = f + np.einsum("...fk,fk->...", np.maximum(Xs[..., None] - fz["knots"], 0.0), fz["c"])
    return f


def weights_from_raw(fz: dict, raw: dict) -> np.ndarray:
    X = data.engineer(raw)
    out = np.empty(X.shape[:-1])
    for s in range(0, X.shape[0], 10):                      # chunks of 10 items keep the hinge expansion small
        Xs = ((X[s:s + 10] - fz["mu"]) / fz["sd"]).astype(np.float64)
        out[s:s + 10] = 1.0 / (1.0 + np.exp(-gam_f(fz, Xs)))
    return out


def infer_item(fz: dict, d, cond: str, delta: np.ndarray | None = None) -> dict:
    """Weights for one stored item and condition; with Delta (stored `<cond>_delta` by default) also the decision."""
    w = weights_from_raw(fz, raw_from_npz(d, cond))[0, 0]
    delta = d[f"{cond}_delta"] if delta is None else delta
    s = float((w * delta).sum())
    return dict(w=w, score=s, margin=s / float(w.sum()), decision=bool(s > 0))


def load_frozen(path: Path = FROZEN) -> dict:
    spec = json.loads((path / "spec.json").read_text())
    if sha256(path / "model.npz") != spec["model_sha256"]:
        raise ValueError("model.npz does not match the sha256 in spec.json")
    z = np.load(path / "model.npz")
    if list(z["feature_names"]) != spec["features"]:
        raise ValueError("feature order mismatch")
    return {k: z[k].astype(np.float64) for k in ("a", "b", "c", "knots", "mu", "sd")} | dict(spec=spec)


# ---------------------------------------------------------------- freeze
def freeze():
    from .run import ARR, N_ITEMS, ss, successive_halving, inner_folds  # noqa: F401
    FROZEN.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    d = data.load(ARR, N_ITEMS)
    from types import SimpleNamespace
    ctx = SimpleNamespace(X=data.engineer(d["raw"]), delta=d["delta"], z=d["z"], gm=d["gm"], codes=d["codes"],
                          mask=data.token_subsample(ss(7), d["delta"].shape, 0.25))
    allit = np.arange(N_ITEMS)
    f1 = fam.F1GAM("F1", 40, 9)
    cfg, score, hl = successive_halving(ctx, f1, allit, FROZEN_KEY, 0)
    seed = int(ss(4, FROZEN_KEY, 0, 0).generate_state(1)[0])
    model = f1.fit(ctx, cfg, allit, f1.rmax, seed)
    net = model["net"]
    arrays = dict(a=net.a.detach().numpy(), b=net.b.detach().numpy(), c=net.c.detach().numpy(), knots=net.knots.numpy(),
                  mu=model["mu"], sd=model["sd"], feature_names=np.array(data.feature_names()))
    np.savez(FROZEN / "model.npz", **arrays)
    T = fam.temperature(ctx.delta)
    spec = dict(name="LRF (learned reliability-aware evidence fusion), frozen logistic-GAM F1",
                decision="D0082", status="frozen 2026-10-29; trained on all 500 M4 test items (discovery set); confirm only on fresh items",
                family="F1 logistic-GAM: w_j = sigmoid(b + sum_k a_k x_k + sum_k sum_m c_km relu(x_k - t_km)), x standardised",
                objective="item-level O1: mean softplus(-M/T), M = sum_j w_j Delta_j / sum_j w_j, + ridge * (|a|^2 + |c|^2); AdamW (wd 0), mini-batch 32 item-conditions",
                training_conditions=list(data.COND), n_items=N_ITEMS, T=T, selected_cfg=cfg, inner_cv_o1=score, epochs=f1.rmax, seed=seed,
                hpo=dict(method="random search + synchronous successive halving, eta 3, 9 configs, 3 inner folds over all 500 items",
                         seed_keys=dict(configs=[2, FROZEN_KEY, 0], inner_folds=[1, FROZEN_KEY], final_fit=[4, FROZEN_KEY, 0, 0]), root_seed=20261029),
                features=data.feature_names(), n_features=len(data.feature_names()),
                preprocessing="raw_from_npz -> data.engineer (per item and condition, no cross-item statistics) -> (X - mu) / sd with the stored mu, sd",
                feature_definitions={"B": "<cond>_B", "D": "<cond>_D", "q": "B - D (float32)", "s3": "<cond>_s3", "tbv": "<cond>_tbv",
                                     "ltex": "log1p(max(<cond>_tex, 0))", "nbr": "<cond>_nbr",
                                     "row/col/rad": "row-major 32x32 grid position /31; distance from centre",
                                     "nb3mean_*": "3x3 mean excluding self, edge-aware", "nb3min_q": "3x3 min of q excluding self",
                                     "nb5mean_q": "5x5 mean of q excluding self", "rank_*": "within-item percentile rank",
                                     "itemmean_*/itemsd_*": "item-condition mean / SD over 1024 tokens", "itemz_q": "(q - item mean) / (item SD + 1e-6)"},
                inputs_never_used=["Delta", "Lambda", "captions", "z", "GATE flags", "condition identity"],
                layout_caveat="B, D, tbv were scored with the caption slots masked at the length of the TRUE caption (see LRF-FROZEN report, length check)",
                inference="analysis_posthoc.learned_ceiling.lrf.infer_item(load_frozen(), np.load(item.npz), cond)",
                code_sha256={f: sha256(Path(__file__).parent / f) for f in CODE_FILES},
                model_sha256=sha256(FROZEN / "model.npz"), torch=torch.__version__, numpy=np.__version__)
    (FROZEN / "spec.json").write_text(json.dumps(spec, indent=1), encoding="utf8")
    (FROZEN / "hpo.json").write_text(json.dumps(hl, indent=1), encoding="utf8")
    # self-check: the numpy inference path equals the torch training path on 20 items x 4 conditions
    fz = load_frozen()
    chk = np.arange(0, N_ITEMS, 25)
    w_torch = f1.weights(ctx, model, chk)
    maxdiff = 0.0
    for j, i in enumerate(chk):
        dd = np.load(ARR / f"item{i:04d}.npz")
        for c, name in enumerate(data.COND):
            maxdiff = max(maxdiff, float(np.abs(infer_item(fz, dd, name)["w"] - w_torch[j, c]).max()))
    # in-sample (descriptive, optimistic) accuracies and weights for the reading
    W = weights_from_raw(fz, d["raw"])
    Y = (W * d["delta"]).sum(-1) > 0
    np.savez_compressed(FROZEN / "insample_weights.npz", w=W.astype(np.float16))
    out = dict(selfcheck_max_abs_diff_numpy_vs_torch=maxdiff, insample_accuracy={n: float(Y[:, c].mean()) for c, n in enumerate(data.COND)},
               none_accuracy={n: float((d["delta"][:, c].mean(-1) > 0).mean()) for c, n in enumerate(data.COND)}, sec=round(time.time() - t0, 1))
    (FROZEN / "freeze_check.json").write_text(json.dumps(out, indent=1), encoding="utf8")
    print(json.dumps(dict(cfg=cfg, inner_o1=score, **out), indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true")
    if ap.parse_args().freeze:
        freeze()
