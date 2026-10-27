"""CPU analysis of M4 (v2 sections 6, 7.1, 7.4, 5.3). Reads runs/P2-GATE-M4/items.jsonl and arrays/; writes analysis.json. No model.

    python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-M4 --family-run P2-GATE-M3

Primary (7.1): per family member, exact two-sided McNemar of the image-direction accuracy y, arm gate0.05 (GATE-M) versus none, Holm over the family.
Mechanism controls (7.4): GATE-M versus the geometry-matched random gate and the scattered random gate (mean y over the 3 seeds per item), changed-code gate,
plain-B top-k, s3 top-k, denoised codes; reported as paired bootstrap CIs of the mean difference of y and of the z-score (the z endpoint is the key secondary).
Calibration (6): realised false-alarm proportion on the clean test condition for each alpha with a bootstrap CI over items; precision among flagged tokens and the
false-alarm proportion on the clean tokens of corrupted items, per condition. Prop. 4 plug-in check (5.3) per family member. Dropped-item counts per test."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, core                                            # noqa: E402
from exp_p2.gate import config, stats, theory                               # noqa: E402

A0 = f"gate{config.ALPHA_PRIMARY:g}"


def _arm(rows, cond, arm, field):
    return np.array([r["conds"][cond]["img"][arm][field] if cond in r["conds"] and arm in r["conds"][cond]["img"] else np.nan for r in rows], float)


def _mean_arm(rows, cond, arms_, field):
    return np.nanmean(np.stack([_arm(rows, cond, a, field) for a in arms_]), axis=0)


def paired_boot(a, b, n_boot=10000, seed=0) -> dict:
    d = np.asarray(a, float) - np.asarray(b, float)
    ok = np.isfinite(d)
    m, lo, hi = core.bootstrap_mean_ci(d[ok], n_boot, seed)
    return dict(diff=m, lo=lo, hi=hi, n=int(ok.sum()), n_dropped=int((~ok).sum()))


def primary(rows: list[dict], family_keys: list[str]) -> dict:
    res = {k: dict(stats.mcnemar_exact(_arm(rows, k, A0, "y"), _arm(rows, k, "none", "y")), acc_gate=float(np.nanmean(_arm(rows, k, A0, "y"))),
                   acc_none=float(np.nanmean(_arm(rows, k, "none", "y")))) for k in family_keys}
    adj = stats.holm([res[k]["p"] for k in family_keys]) if family_keys else []
    for k, p in zip(family_keys, adj):
        res[k]["p_holm"] = p
        res[k]["gate_better"] = bool(res[k]["b"] > res[k]["c"] and p < 0.05)
    return dict(per_corruption=res, claim_survives=bool(any(res[k]["gate_better"] for k in family_keys)),
                rule="v2 7.1: claim withdrawn if no family member shows GATE-M > none at the Holm-adjusted 0.05 level")


def mechanism(rows: list[dict], key: str, n_boot=10000) -> dict:
    out = {}
    geo = [f"geo{r}" for r in range(config.N_GEO_SEEDS)]
    scat = [f"scat{r}" for r in range(config.N_GEO_SEEDS)]
    for field in ("y", "z", "d"):
        g = _arm(rows, key, A0, field)
        out[field] = {
            "gate_minus_none": paired_boot(g, _arm(rows, key, "none", field), n_boot),
            "gate_minus_geo": paired_boot(g, _mean_arm(rows, key, geo, field), n_boot),
            "gate_minus_scattered": paired_boot(g, _mean_arm(rows, key, scat, field), n_boot),
            "gate_minus_changed_code": paired_boot(g, _arm(rows, key, "chg", field), n_boot),
            "gate_minus_topkB": paired_boot(g, _arm(rows, key, "topkB", field), n_boot),
            "gate_minus_topks3": paired_boot(g, _arm(rows, key, "topks3", field), n_boot),
            "changed_code_minus_none": paired_boot(_arm(rows, key, "chg", field), _arm(rows, key, "none", field), n_boot),
        }
    out["denoise_minus_none"] = {f: paired_boot(_arm(rows, key + "_dn", "denoised", f), _arm(rows, key, "none", f), n_boot) for f in ("y", "z")} if any(key + "_dn" in r["conds"] for r in rows) else None
    out["gate_on_clean"] = {f: paired_boot(_arm(rows, "clean", A0, f), _arm(rows, "clean", "none", f), n_boot) for f in ("y", "z")}
    return out


def calibration(run: Path, rows: list[dict], family_keys: list[str], n_boot=10000) -> dict:
    out = dict(realised_fap_clean={}, per_condition={})
    cond_names = ["clean"] + family_keys + ["patch"]
    per_item = {c: [] for c in cond_names}
    for r in rows:
        arr = np.load(run / "arrays" / f"item{r['idx']:04d}.npz")
        for c in cond_names:
            per_item[c].append(dict(z=arr[f"{c}_z"], f={al: arr[f"{c}_flag{al:g}"] for al in config.ALPHAS}, delta=arr[f"{c}_delta"]))
    for al in config.ALPHAS:
        fap = np.array([x["f"][al].mean() for x in per_item["clean"]])
        m, lo, hi = core.bootstrap_mean_ci(fap, n_boot)
        out["realised_fap_clean"][f"{al:g}"] = dict(mean=m, lo=lo, hi=hi, alpha=al, n_items=len(fap), at_most_alpha_plus_se=bool(m <= al + 2 * fap.std(ddof=1) / np.sqrt(len(fap))))
    for c in cond_names[1:]:
        z = np.concatenate([x["z"] for x in per_item[c]])
        f = np.concatenate([x["f"][config.ALPHA_PRIMARY] for x in per_item[c]])
        d = np.concatenate([x["delta"] for x in per_item[c]])
        n_flag = int(f.sum())
        out["per_condition"][c] = dict(precision=float((f & z).sum() / n_flag) if n_flag else float("nan"), recall=float((f & z).sum() / z.sum()) if z.sum() else float("nan"),
                                       fap_on_clean_tokens=float((f & ~z).sum() / max(1, (~z).sum())), n_flagged=n_flag, n_corrupted=int(z.sum()),
                                       prop4=theory.plug_in_from_deltas(d, z, f))
    return out


def run(run_dir: Path, family_keys: list[str], n_boot=10000) -> dict:
    rows = common.read_jsonl(run_dir / "items.jsonl")
    res = dict(n_items=len(rows), family=family_keys, primary=primary(rows, family_keys), mechanism={k: mechanism(rows, k, n_boot) for k in family_keys + ["patch"]},
               calibration=calibration(run_dir, rows, family_keys, n_boot))
    for k in family_keys:                                                                               # Prop. 4 refutation check (5.3)
        obs = res["mechanism"][k]["z"]["gate_minus_none"]
        pred = res["calibration"]["per_condition"][k]["prop4"].get("predicted_helps")
        sig = obs["lo"] > 0 or obs["hi"] < 0
        res["calibration"]["per_condition"][k]["prop4_refuted"] = None if pred is None else bool(sig and ((obs["diff"] > 0) != pred))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-GATE-M4")
    ap.add_argument("--family-run", default="P2-GATE-M3")
    ap.add_argument("--boot", type=int, default=10000)
    a = ap.parse_args(argv)
    fam = json.loads((Path(common.RUNS) / a.family_run / "family.json").read_text(encoding="utf8"))["family"]
    res = run(Path(common.RUNS) / a.run_id, [f["key"] for f in fam], a.boot)
    (Path(common.RUNS) / a.run_id / "analysis.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf8")
    print(json.dumps(dict(n_items=res["n_items"], claim_survives=res["primary"]["claim_survives"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
