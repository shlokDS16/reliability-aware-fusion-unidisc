"""Frozen analysis script (EXP-001 card v0.5, 9 item 11, 10.1-10.3): Lift, V-lift, dC/dB, completion increment, bootstrap, Holm,
outcome classes, reading conditions, guardrails. Run end-to-end on D0 pilot outputs with LABELS SCRAMBLED (captions permuted within
each arm), hashed, and its hash written into runs/EXP-001/arms/manifest.json before any D3 sample is scored.

Input: an .npz with, for each arm a in ARMS, arrays  img_<a> [n,d], cap_<a> [n,d], pre_<a> [n,d] (prefix-only text embeddings),
and optionally vs_<a>_m, vs_<a>_p1, vs_<a>_p2 (VLM scores matched / pi1 / pi2) [n]. All rows are seeds (same order in every arm).

  python analysis/EXP-001/frozen_analysis.py --input X.npz --scramble --out result.json     # label-scrambled freeze run
  python analysis/EXP-001/frozen_analysis.py --selftest                                      # synthetic end-to-end run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics as M

CONTRASTS = {"H-B1": ("DA", "J", "k0"), "Alt-J": ("Alt", "J", "k0"), "DA-J@k+": ("DA@k+", "J@k+", "k+"), "H-B1p": ("DA", "DA-low", "k0"),
             "H-B4": ("DA", "TFJ", "k0")}


def scramble(data: dict, arms, seed=20261014):
    """Permute caption (and prefix-only) embeddings within each arm: pairing labels destroyed, marginals kept."""
    g = np.random.default_rng(seed)
    out = dict(data)
    for a in arms:
        p = g.permutation(data[f"img_{a}"].shape[0])
        out[f"cap_{a}"] = data[f"cap_{a}"][p]
        out[f"pre_{a}"] = data[f"pre_{a}"][p]
    return out


def run(data: dict, arms, contrasts: dict, B: int = 10000, scr: bool = False, seed: int = 0) -> dict:
    if scr:
        data = scramble(data, arms)
    S = {a: M.sim_matrix(data[f"img_{a}"], data[f"cap_{a}"]) for a in arms}
    Sp = {a: M.sim_matrix(data[f"img_{a}"], data[f"pre_{a}"]) for a in arms}
    res = {"arms": {}, "contrasts": {}}
    for a in arms:
        res["arms"][a] = {"lift": float(M.lift(S[a]).mean()), "sd_psi": float(M.psi(S[a]).std(ddof=1)),
                          "prefix_only_lift": float(M.lift(Sp[a]).mean()),
                          "completion_increment": float(M.completion_increment(S[a], Sp[a]).mean()),
                          "mean_pairwise_cos_img": M.mean_pairwise_cos(data[f"img_{a}"]), "mean_pairwise_cos_cap": M.mean_pairwise_cos(data[f"cap_{a}"])}
    pvals = {}
    for name, (x, y, _) in contrasts.items():
        if x not in arms or y not in arms:
            pvals[name] = 1.0                       # a test that is not run enters Holm with p = 1
            continue
        th = M.paired_bootstrap(S[x], S[y], B=B, seed=seed + len(name))
        d = M.point_contrast(S[x], S[y])
        lo, hi = M.percentile_ci(th, 0.95)
        p = M.two_sided_p(th)
        pvals[name] = p
        thC = M.paired_bootstrap(S[x], S[y], B=B, seed=seed + 1 + len(name), which="C")
        thB = M.paired_bootstrap(S[x], S[y], B=B, seed=seed + 2 + len(name), which="B")
        res["contrasts"][name] = {"estimate": d, "ci95": [lo, hi], "p": p, "dC_ci95": list(M.percentile_ci(thC, 0.95)), "dB_neg100_ci95": list(M.percentile_ci(-100 * thB, 0.95))}
    primary = "H-B1"
    sec = {k: v for k, v in pvals.items() if k != primary}
    seq = M.fixed_sequence(pvals.get(primary, 1.0), sec)
    res["fixed_sequence"] = seq
    for name, c in res["contrasts"].items():
        padj = seq["primary"][0] if name == primary else seq["secondary"].get(name, (1.0, False))[0]
        c["outcome_class"] = M.outcome_class(c["estimate"], c["ci95"][0], c["ci95"][1], padj)
    if "DA" in arms and "J" in arms:
        vs = lambda a: M.vlift(data[f"vs_{a}_m"], data[f"vs_{a}_p1"], data[f"vs_{a}_p2"]) if f"vs_{a}_m" in data else None
        va, vj = vs("DA"), vs("J")
        vrep = None
        if va is not None and vj is not None:
            g = np.random.default_rng(seed + 99)
            d = va - vj
            vrep = np.array([d[g.integers(0, len(d), len(d))].mean() for _ in range(min(B, 10000))])
        res["reading_conditions"] = M.reading_conditions(S["DA"], S["J"], Sp["DA"], Sp["J"], vrep, B=min(B, 2000), seed=seed + 5)
    return res


def digest(res: dict) -> str:
    return hashlib.sha256(json.dumps(res, sort_keys=True, default=lambda o: float(o) if hasattr(o, "item") else str(o)).encode()).hexdigest()


def synthetic(n=80, d=24, arms=("J", "Alt", "DA", "DA-low", "TFJ"), effect=0.0, seed=1):
    g = np.random.default_rng(seed)
    z = g.standard_normal((n, d))
    out = {}
    for k, a in enumerate(arms):
        sig = 0.6 + (effect if a == "DA" else 0.0)
        img = z + 0.5 * g.standard_normal((n, d))
        cap = sig * z + g.standard_normal((n, d))
        pre = 0.3 * z + g.standard_normal((n, d))
        for nm, arr in (("img", img), ("cap", cap), ("pre", pre)):
            out[f"{nm}_{a}"] = arr / np.linalg.norm(arr, axis=1, keepdims=True)
        out[f"vs_{a}_m"] = np.clip(0.5 + 0.1 * g.standard_normal(n), 0, 1)
        out[f"vs_{a}_p1"] = np.clip(0.4 + 0.1 * g.standard_normal(n), 0, 1)
        out[f"vs_{a}_p2"] = np.clip(0.4 + 0.1 * g.standard_normal(n), 0, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--out")
    ap.add_argument("--scramble", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--B", type=int, default=10000)
    a = ap.parse_args()
    if a.selftest:
        arms = ("J", "Alt", "DA", "DA-low", "TFJ")
        res = run(synthetic(), arms, CONTRASTS, B=300, scr=True)
        print("selftest ok, sha256", digest(res))
        return
    z = np.load(a.input)
    data = {k: z[k] for k in z.files}
    arms = sorted({k.split("_", 1)[1] for k in data if k.startswith("img_")})
    res = run(data, arms, CONTRASTS, B=a.B, scr=a.scramble)
    res["sha256"] = digest(res)
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, default=lambda o: float(o) if hasattr(o, "item") else str(o)), encoding="utf8")
    print(res["sha256"])


if __name__ == "__main__":
    main()
