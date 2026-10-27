"""CPU analysis of M4 (v2 sections 6, 7.1, 7.4, 5.3). Reads runs/P2-GATE-M4/items.jsonl and arrays/; writes analysis.json. No model.

    python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-M4 --family-run P2-GATE-M3 [--endpoint d]

Primary (7.1): per family member, exact two-sided McNemar of the image-direction accuracy y, arm gate0.05 (GATE-M) versus none, Holm over the family.
Mechanism controls (7.4): GATE-M versus the geometry-matched random gate and the scattered random gate (mean y over the 3 seeds per item), changed-code gate,
plain-B top-k, s3 top-k, denoised codes; reported as paired bootstrap CIs of the mean difference of y and of the z-score (the z endpoint is the key secondary).
Calibration (6): realised false-alarm proportion on the clean test condition for each alpha with a bootstrap CI over items; precision among flagged tokens and the
false-alarm proportion on the clean tokens of corrupted items, per condition. Prop. 4 plug-in check (5.3) per family member. Dropped-item counts per test."""
from __future__ import annotations

import argparse
import json
import re
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


def corr_of(key: str) -> str:
    return re.match(r"[a-z]+", key).group(0)


def _family_map(family) -> dict[str, str]:
    """corruption name -> condition key, from a list of keys or of family.json entries."""
    out = {}
    for f in family:
        key = f["key"] if isinstance(f, dict) else f
        out[corr_of(key)] = key
    return out


def primary(rows: list[dict], family) -> dict:
    """Family P (SAP 2.4): exactly m = 3 hypotheses, always (P1 JPEG, P2 noise, P3 splice). A corruption without an operating point is not tested, gets p = 1 and stays in
    the family. Supported only if at least one is rejected after Holm with b > c."""
    fm = _family_map(family)
    res = {}
    for label, corr in zip(("P1", "P2", "P3"), config.REALISTIC):
        if corr in fm:
            k = fm[corr]
            res[corr] = dict(stats.mcnemar_exact(_arm(rows, k, A0, "y"), _arm(rows, k, "none", "y")), label=label, key=k, tested=True,
                             acc_gate=float(np.nanmean(_arm(rows, k, A0, "y"))), acc_none=float(np.nanmean(_arm(rows, k, "none", "y"))))
        else:
            res[corr] = dict(label=label, key=None, tested=False, p=1.0, b=0, c=0)
    adj = stats.holm([res[c]["p"] for c in config.REALISTIC])
    for c, p in zip(config.REALISTIC, adj):
        res[c]["p_holm"] = p
        res[c]["gate_better"] = bool(res[c]["tested"] and res[c]["b"] > res[c]["c"] and p < 0.05)
    return dict(per_corruption=res, holm_m=3, claim_survives=bool(any(res[c]["gate_better"] for c in config.REALISTIC)),
                rule="SAP 2.4: m = 3 always; supported iff at least one rejection after Holm with b > c")


def s_dn(rows: list[dict], family) -> dict:
    """S-DN (Addendum 1 N2): GATE-M versus pixel-domain denoise, exact McNemar on Y, Holm over m = 2 (JPEG, noise). Splice has no denoise arm and is not in the family."""
    fm = _family_map(family)
    res = {}
    for corr in config.DENOISE_FOR:
        k = fm.get(corr)
        if k is not None and any(k + "_dn" in r["conds"] for r in rows):
            ya = _arm(rows, k, A0, "y")
            yb = np.array([r["conds"][k + "_dn"]["img"]["denoised"]["y"] if k + "_dn" in r["conds"] else np.nan for r in rows], float)
            res[corr] = dict(stats.mcnemar_exact(ya, yb), key=k, tested=True)
        else:
            res[corr] = dict(tested=False, p=1.0, b=0, c=0)
    adj = stats.holm([res[c]["p"] for c in config.DENOISE_FOR])
    for c, p in zip(config.DENOISE_FOR, adj):
        res[c]["p_holm"] = p
        res[c]["gate_better"] = bool(res[c]["tested"] and res[c]["b"] > res[c]["c"] and p < 0.05)
    return dict(per_corruption=res, holm_m=2)


def s_z(rows: list[dict], family, endpoint: str = "d", n_boot: int = 10000) -> dict:
    """S-Z (Addendum 1 A1.1): Wilcoxon signed-rank on gate - none of the evidence endpoint (default d, reported as z* = sqrt(m) d), Holm over m = 3, plus the paired bootstrap CI of the
    mean difference. The other endpoint (z) is a sensitivity row. Items with a non-finite value are dropped per test and counted."""
    from scipy.stats import wilcoxon
    fm = _family_map(family)

    def one(k, ep):
        g, n = _arm(rows, k, A0, ep), _arm(rows, k, "none", ep)
        ok = np.isfinite(g) & np.isfinite(n)
        diff = (g - n)[ok]
        try:
            p = float(wilcoxon(diff).pvalue) if diff.size and np.any(diff != 0) else 1.0
        except ValueError:
            p = 1.0
        return dict(p=p, n=int(ok.sum()), n_dropped=int((~ok).sum()), ci=paired_boot(g, n, n_boot))

    out = {}
    for corr in config.REALISTIC:
        out[corr] = dict(tested=True, endpoint=endpoint, **one(fm[corr], endpoint), sensitivity_other_endpoint={("z" if endpoint == "d" else "d"): one(fm[corr], "z" if endpoint == "d" else "d")}) if corr in fm else dict(tested=False, p=1.0)
    adj = stats.holm([out[c]["p"] for c in config.REALISTIC])
    for c, p in zip(config.REALISTIC, adj):
        out[c]["p_holm"] = p
    return dict(per_corruption=out, holm_m=3, endpoint=endpoint, z_star_scale="z* = sqrt(m) * d")


def rival_suspicion(frozen: dict, arr, cond: str, codefreq) -> np.ndarray | None:
    """Suspicion of the frozen rival on one stored condition of an M4 item (None if its inputs were not stored). Sign applied."""
    base, sign = frozen["base"], frozen["sign"]
    if base == "plainB":
        v = -np.asarray(arr[f"{cond}_B"], np.float64)
    elif base == "s3":
        v = np.asarray(arr[f"{cond}_s3"], np.float64)
    elif base in ("tex", "nbr", "tbv"):
        key = f"{cond}_{base}"
        v = np.asarray(arr[key], np.float64) * (-1 if base == "tbv" else 1) if key in arr.files else None
    elif base == "rarity":
        v = None if codefreq is None else codefreq.rarity(np.asarray(arr[f"{cond}_codes"], np.int64))
    else:
        raise ValueError(base)
    if v is None or np.isnan(v).any():
        return None
    return sign * v


def s_d2(run_dir: Path, rows: list[dict], family, frozen: dict | None, codefreq=None, n_boot: int = 10000) -> dict:
    """S-D2 (Addendum 1 A1.2 rule 5): per-item AUROC of q minus that of the frozen rival (rival and sign fixed on M1) on the M4 test items at the M4 operating point of
    JPEG and of noise; paired bootstrap p, Holm over m = 2; a corruption with no operating point or no usable rival gets p = 1 and stays in m = 2."""
    from exp_p2.gate import detect
    fm = _family_map(family)
    res = {}
    for corr in ("jpeg", "noise"):
        fr = (frozen or {}).get(corr) or {}
        k = fm.get(corr)
        if k is None or not fr.get("available"):
            res[corr] = dict(tested=False, p=1.0, reason="no operating point" if k is None else "no frozen rival")
            continue
        qa, ra = [], []
        for r in rows:
            arr = np.load(run_dir / "arrays" / f"item{r['idx']:04d}.npz")
            z = np.asarray(arr[f"{k}_z"], bool)
            rv = rival_suspicion(fr, arr, k, codefreq)
            ok = 5 <= z.sum() <= len(z) - 5
            q = -(np.asarray(arr[f"{k}_B"], np.float64) - np.asarray(arr[f"{k}_D"], np.float64))
            qa.append(core.auroc(q, z) if ok else np.nan)
            ra.append(core.auroc(rv, z) if (ok and rv is not None) else np.nan)
        qa, ra = np.array(qa), np.array(ra)
        d = qa - ra
        d = d[~np.isnan(d)]
        if d.size < 2:
            res[corr] = dict(tested=False, p=1.0, reason="no eligible items", n_eligible=int(d.size))
            continue
        boots = d[np.random.default_rng(0).integers(0, d.size, size=(n_boot, d.size))].mean(axis=1)
        res[corr] = dict(tested=True, key=k, rival=fr["rival"], n_eligible=int(d.size), n_excluded=int(len(rows) - d.size), auroc_q=float(np.nanmean(qa)), auroc_rival=float(np.nanmean(ra)),
                         diff_mean=float(d.mean()), p=detect.bootstrap_p(boots), ci95=[float(np.quantile(boots, .025)), float(np.quantile(boots, .975))],
                         label="at the M4 rung " + k)
    adj = detect.holm_adjust({c: res[c]["p"] for c in res})
    for c in res:
        res[c]["p_holm"] = adj[c]
        res[c]["q_beats_frozen_rival"] = bool(res[c].get("tested") and res[c]["p_holm"] <= 0.05 and res[c]["diff_mean"] > 0)
    return dict(per_corruption=res, holm_m=2)


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


def run(run_dir: Path, family, n_boot=10000, endpoint: str = "d", frozen: dict | None = None, codefreq=None) -> dict:
    """family: list of family.json entries (or of condition keys). endpoint: 'd' (SAP default, Addendum 1) or 'z'."""
    rows = common.read_jsonl(run_dir / "items.jsonl")
    fm = _family_map(family)
    keys = list(fm.values())
    res = dict(n_items=len(rows), family=keys, endpoint=endpoint, primary=primary(rows, family), s_dn=s_dn(rows, family), s_z=s_z(rows, family, endpoint, n_boot),
               s_d2=s_d2(run_dir, rows, family, frozen, codefreq, n_boot), mechanism={k: mechanism(rows, k, n_boot) for k in keys + ["patch"]},
               calibration=calibration(run_dir, rows, keys, n_boot))
    for k in keys:                                                                                      # Prop. 4 refutation check (5.3)
        obs = res["mechanism"][k][endpoint]["gate_minus_none"]
        pred = res["calibration"]["per_condition"][k]["prop4"].get("predicted_helps")
        sig = obs["lo"] > 0 or obs["hi"] < 0
        res["calibration"]["per_condition"][k]["prop4_refuted"] = None if pred is None else bool(sig and ((obs["diff"] > 0) != pred))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-GATE-M4")
    ap.add_argument("--family-run", default="P2-GATE-M3")
    ap.add_argument("--endpoint", choices=["d", "z"], default="d", help="S-Z endpoint; d is the SAP default (Addendum 1), z only as sensitivity")
    ap.add_argument("--frozen", default=str(Path(common.RUNS) / "P2-GATE-M1" / "detection_frozen.json"))
    ap.add_argument("--codefreq", default=str(Path(common.RUNS) / "P2-GATE-M2" / "codefreq.npy"))
    ap.add_argument("--boot", type=int, default=10000)
    a = ap.parse_args(argv)
    fam = json.loads((Path(common.RUNS) / a.family_run / "family.json").read_text(encoding="utf8"))
    if fam.get("endpoint") != "d":
        print("family.json does not record endpoint d: invalid for the SAP", file=sys.stderr)
        return 2
    from exp_p2.gate import baselines
    fp, cp = Path(a.frozen), Path(a.codefreq)
    frozen = json.loads(fp.read_text(encoding="utf8"))["frozen"] if fp.exists() else None
    codefreq = baselines.CodeFreq(np.load(cp)) if cp.exists() else None
    res = run(Path(common.RUNS) / a.run_id, fam["family"], a.boot, a.endpoint, frozen, codefreq)
    (Path(common.RUNS) / a.run_id / "analysis.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf8")
    print(json.dumps(dict(n_items=res["n_items"], claim_survives=res["primary"]["claim_survives"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
