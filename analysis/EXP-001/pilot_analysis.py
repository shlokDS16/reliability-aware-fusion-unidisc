"""D0 pilot analysis script (EXP-001 card v0.5, section 10.5 firewall; dynamic-range gate input of section 6). Hashed in
runs/EXP-001/pilot/ BEFORE D0 is generated. NOT RUN in this implementation phase (no D0 data exists).

It computes and writes ONLY: per-arm SDs of the influence values psi_i, the bootstrap SE of Alt - J (an SE, never the contrast mean),
the paired correlation rho_pair of the influence values, J-only descriptive quantities (Lift(J), prefix-only lift of J, J's mean
completion increment Lift(full) - Lift(prefix-only) with its bootstrap SE: the dynamic-range gate statistic of section 6),
Lift(Ref-real) for PC-A, and sigma_d,up / n_req of rule 10.4. It never computes or saves the mean Lift of Alt or of any contrast, nor a
mean of any V-lift contrast.

Input npz: img_J, cap_J, pre_J, img_Alt, cap_Alt (embeddings [n, d]); optional ref_img, ref_cap (Ref-real).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics as M


def sigma_d_up(se_alt_minus_j: float, n: int = 64) -> float:
    """10.4: sigma_d,up = sqrt(64) x SE x sqrt(63 / chi2_{0.20, 63}) (the 20th percentile of chi-square with 63 df)."""
    return float(np.sqrt(64) * se_alt_minus_j * np.sqrt(63 / stats.chi2.ppf(0.20, 63)))


def n_req(s_up: float) -> int:
    """10.4: n_req = ceil(1.5 x ((1.96 + 1.2816) sigma_d,up / 1.0)^2)."""
    return int(np.ceil(1.5 * ((1.96 + 1.2816) * s_up / 1.0) ** 2))


def run(d: dict, B: int = 10000, seed: int = 0) -> dict:
    SJ = M.sim_matrix(d["img_J"], d["cap_J"])
    SJp = M.sim_matrix(d["img_J"], d["pre_J"])
    SA = M.sim_matrix(d["img_Alt"], d["cap_Alt"])
    out = {"n": int(SJ.shape[0])}
    psi_J, psi_A = M.psi(SJ), M.psi(SA)
    out["sd_psi_J"], out["sd_psi_Alt"] = float(psi_J.std(ddof=1)), float(psi_A.std(ddof=1))
    out["rho_pair_psi"] = float(np.corrcoef(psi_J, psi_A)[0, 1])
    th = M.paired_bootstrap(SA, SJ, B=B, seed=seed)
    out["bootstrap_se_Alt_minus_J"] = float(th.std(ddof=1))              # the SE only; the contrast mean is not computed or saved
    s_up = sigma_d_up(out["bootstrap_se_Alt_minus_J"])
    out["sigma_d_up"], out["n_req"] = s_up, n_req(s_up)
    out["lift_J"], out["prefix_only_lift_J"] = float(M.lift(SJ).mean()), float(M.lift(SJp).mean())
    inc = M.completion_increment(SJ, SJp)
    rng = np.random.default_rng(seed + 1)
    reps = np.array([inc[rng.integers(0, len(inc), len(inc))].mean() for _ in range(B)])
    out["dynamic_range_gate"] = {"completion_increment_J": float(inc.mean()), "bootstrap_se": float(reps.std(ddof=1)),
                                 "threshold_points": 1.0, "below_threshold_fork_to_P_rand": bool(inc.mean() < 1.0),
                                 "note": "between 1.0 and 2.0 the run proceeds under P and Paper 1 states the MEI share of the movable range"}
    if "ref_img" in d:
        out["lift_ref_real"] = float(M.lift(M.sim_matrix(d["ref_img"], d["ref_cap"])).mean())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--B", type=int, default=10000)
    a = ap.parse_args()
    z = np.load(a.input)
    res = run({k: z[k] for k in z.files}, a.B)
    Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
