"""CPU analysis of M4 (SAP sections 2-8 and Addendum 1; v2 sections 5.3, 6, 7). Reads runs/P2-GATE-M4/items.jsonl and arrays/; writes analysis.json. No model.

    python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-M4 --family-run P2-GATE-M3 [--endpoint d] [--allow-partial]

Tiers
  Family P (2.4)   exactly m = 3 (JPEG, noise, splice), p = 1 for a corruption without an operating point, supported only with b > c after Holm.
  S-M  (2.5)       GATE-M versus the geometry-matched random gate, SEED 1 (arm geo0) fixed in advance, exact McNemar, gatekept by P rejections, m = 3 (p = 1 elsewhere); the
                   other two seeds are separate replications with their own unadjusted p. K5 / K6 flags.
  S-Z  (2.5, A1.1) Wilcoxon on the evidence endpoint d (z* = 32 d), m = 3; z as sensitivity.     S-DN (A1.3 N2) GATE-M vs denoise, m = 2.
  S-D2 (A1.2)      q versus the frozen rival, m = 2.     S-C (2.5) GATE-M vs none on clean images, m = 1.
  PS   (AD.4)      positive control on the token-level corruptions: GATE-M versus none on patch (PS1) and swap (PS2), Holm m = 2, p = 1 for a cell that was not run (`ps_family`).
  Calibration (6)  Z_cal = (F - alpha) / (sigma_L sqrt(1/n_cal + 1/n_test)) at the three alphas, violation iff Z_cal > 2.13 (K4); item-clustered bootstrap CI; exploratory 2,000-split
                   replication; precision / FAP on clean tokens of corrupted items.
  Completeness (8.1) planned vs completed n, prefix check, covariates of missing vs completed, NaN/empty-R counts per arm, K7 (> 5 percent stops the analysis), worst-case sensitivity.
Every test carries b, c, n_d, n, both accuracies, (b-c)/n with 95 and 98.33 percent bootstrap CIs, Clopper-Pearson CI of theta, exact p and mid-p (report.report_test).
Seeds: SeedSequence(20261028) spawned by analysis name (seeds.py); the seed and numpy version are written into the output."""
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
from exp_p2.gate import c1 as c1mod, calibrate as cal, config, report, scores, seeds, stats, theory     # noqa: E402

A0 = f"gate{config.ALPHA_PRIMARY:g}"
Z_CAL_CRIT = 2.13           # z_{0.9833}: one-sided Bonferroni over three alpha levels (SAP section 6)
K7_FRACTION = 0.05


class PipelineDefect(RuntimeError):
    """K7: more than 5 percent NaN or empty-R in an arm; the analysis stops (SAP 8.5)."""


class PartialRun(RuntimeError):
    """SAP 8.2: the outcome analysis is not run before the planned fold is complete (unless --allow-partial)."""


def _arm(rows, cond, arm, field):
    return np.array([r["conds"][cond]["img"][arm][field] if cond in r["conds"] and arm in r["conds"][cond]["img"] else np.nan for r in rows], float)


def _mean_arm(rows, cond, arms_, field):
    return np.nanmean(np.stack([_arm(rows, cond, a, field) for a in arms_]), axis=0)


def paired_boot(a, b, n_boot=10000, seed=None) -> dict:
    d = np.asarray(a, float) - np.asarray(b, float)
    ok = np.isfinite(d)
    m, lo, hi = core.bootstrap_mean_ci(d[ok], n_boot, seed if seed is not None else seeds.seed_for("mechanism"))
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


def load_items(run_dir: Path) -> tuple[list[dict], int]:
    """Rows de-duplicated by item index (first complete row kept, SAP 8.1); returns (rows, number of duplicates removed)."""
    raw = common.read_jsonl(Path(run_dir) / "items.jsonl")
    seen, rows = set(), []
    for r in raw:
        if r["idx"] not in seen:
            seen.add(r["idx"])
            rows.append(r)
    return rows, len(raw) - len(rows)


# ------------------------------------------------------------------------------------------------ family P and the secondary families
def primary(rows: list[dict], family, n_boot=10000) -> dict:
    """Family P (SAP 2.4): exactly m = 3 hypotheses, always (P1 JPEG, P2 noise, P3 splice). A corruption without an operating point is not tested, gets p = 1 and stays in
    the family. Supported only if at least one is rejected after Holm with b > c."""
    fm = _family_map(family)
    res = {}
    for label, corr in zip(("P1", "P2", "P3"), config.REALISTIC):
        if corr in fm:
            k = fm[corr]
            res[corr] = dict(report.report_test(_arm(rows, k, A0, "y"), _arm(rows, k, "none", "y"), n_boot=n_boot, seed=seeds.seed_for("primary")), label=label, key=k, tested=True)
        else:
            res[corr] = dict(label=label, key=None, tested=False, p=1.0, b=0, c=0)
    adj = stats.holm([res[c]["p"] for c in config.REALISTIC])
    for c, p in zip(config.REALISTIC, adj):
        res[c]["p_holm"] = p
        res[c]["gate_better"] = bool(res[c]["tested"] and res[c]["b"] > res[c]["c"] and p < 0.05)
    return dict(per_corruption=res, holm_m=3, claim_survives=bool(any(res[c]["gate_better"] for c in config.REALISTIC)), tested=WORDING_Y,
                rule="SAP 2.4: m = 3 always; supported iff at least one rejection after Holm with b > c")


def _wilcoxon_gate_vs_none(rows, key: str, endpoint: str, n_boot: int, seed) -> dict:
    from scipy.stats import wilcoxon
    g, n = _arm(rows, key, A0, endpoint), _arm(rows, key, "none", endpoint)
    ok = np.isfinite(g) & np.isfinite(n)
    diff = (g - n)[ok]
    try:
        p = float(wilcoxon(diff).pvalue) if diff.size and np.any(diff != 0) else 1.0
    except ValueError:
        p = 1.0
    m, lo, hi = core.bootstrap_mean_ci(diff, n_boot, seed) if diff.size else (float("nan"),) * 3
    ci9833 = [float(np.quantile(diff[np.random.default_rng(seed).integers(0, diff.size, size=(n_boot, diff.size))].mean(axis=1), q)) for q in (0.00835, 0.99165)] if diff.size > 1 else [float("nan")] * 2
    return dict(p=p, n=int(ok.sum()), n_dropped=int((~ok).sum()), mean_diff=float(m), ci95=[lo, hi], ci9833=ci9833, median_diff=float(np.median(diff)) if diff.size else float("nan"))


def primary_d(rows: list[dict], family, n_boot=10000) -> dict:
    """Family P under rule R3 (SAP 4.6, Addendum 2 A2.2): the primary endpoint becomes the paired change of the evidence d (z* = 32 d), Wilcoxon signed-rank on gate - none, same labels
    P1-P3 and m = 3, a corruption without an operating point is not tested (p = 1, stays in m = 3). Rejection counts toward the claim only with a POSITIVE mean difference. Y moves to
    secondary. The outcome label 'negative' is unavailable under R3 (the +/-0.05 margin is defined for accuracy, not for d)."""
    fm = _family_map(family)
    res = {}
    for label, corr in zip(("P1", "P2", "P3"), config.REALISTIC):
        if corr in fm:
            res[corr] = dict(_wilcoxon_gate_vs_none(rows, fm[corr], "d", n_boot, seeds.seed_for("primary")), label=label, key=fm[corr], tested=True, endpoint="d")
        else:
            res[corr] = dict(label=label, key=None, tested=False, p=1.0)
    adj = stats.holm([res[c]["p"] for c in config.REALISTIC])
    for c, p in zip(config.REALISTIC, adj):
        res[c]["p_holm"] = p
        res[c]["gate_better"] = bool(res[c]["tested"] and res[c]["mean_diff"] > 0 and p < 0.05)
    return dict(per_corruption=res, holm_m=3, endpoint="d", rule="R3", claim_survives=bool(any(res[c]["gate_better"] for c in config.REALISTIC)), negative_available=False,
                tested=WORDING_D, z_star_scale="z* = sqrt(m) * d", note="R3 (SAP 4.6): primary = Wilcoxon on the paired change of d; Y is secondary; the 'negative' reading is unavailable", caveat=CAVEAT_D)


NEGATIVE_MARGIN, N_MIN = 0.05, 240

# Wording is part of the result (red team N2 / C2): every printed or recorded label says exactly what was tested.
WORDING_Y = "higher matching accuracy (McNemar on Y)"
WORDING_D = "higher per-item mean/sd evidence ratio d (R3 primary)"
CAVEAT_D = ("d = mean/sd of the per-token evidence over the retained tokens can rise by trimming heavy-tailed tokens, whatever their reason; the geometry-matched and scattered random gates "
            "keep the moments of d roughly unchanged, so they do not separate detecting corruption from trimming heavy tails. The controls that could (plain-B top-k, s3 top-k) are Tier 3, "
            "reported beside the P result, with no p-value (red team N2).")
CAVEAT_SM_R3 = "S-M under R3 is an accuracy McNemar with too few discordant items to say anything: stated as uninformative in advance (red team N2)."

SANITY_CONDS = ("patch", "swap")           # family PS (SAP AD.4): PS1 patch, PS2 swap; the order is the Holm label order, p = 1 for a cell that was not run


def sanity_present(rows: list[dict]) -> list[str]:
    """The token-level sanity conditions that are in the rows (a run made before swap existed has patch only)."""
    return [c for c in SANITY_CONDS if any(c in r["conds"] for r in rows)]


def _records(df) -> list[dict]:
    """Rows as a list of dicts from a list of dicts or a pandas DataFrame (SAP AD.13 writes `df`)."""
    if hasattr(df, "to_dict") and hasattr(df, "columns"):
        return df.to_dict("records")
    return list(df)


def ps_family(df, rule: str = "R1", family=None, n_boot: int = 10000) -> dict:
    """Family PS (SAP AD.4, AD.11, AD.13): positive control on the token-level corruptions. PS1 = GATE-M versus none on patch, PS2 = on swap. m = 2 ALWAYS: a cell that is not in the rows
    (not run, or its code not audited, AB.7 item 2) is not tested, gets p = 1 and stays in the Holm correction. Fold, endpoint and test are those of P in force: R1/R2 exact two-sided McNemar on
    Y, R3 Wilcoxon signed-rank on d; Holm thresholds 0.025 and 0.05 (alpha 0.05 for the family). Reading: `met` iff both are rejected with the right sign (b > c, or a positive mean d difference
    under R3), `partly met` iff one, `not met` otherwise (not met triggers the pipeline audit of A2.3 and bars the sentence 'the gate works where detection is easy'; nothing is tuned).
    Descriptive, no p: the realised discordance n_d (low power is possible if the patch as coded changes few decisions), the headroom statistics T1, T2 on the evidence endpoint d (SAP 5 definition,
    clean - none and changed-code - none), and the difference of the paired accuracy differences (PS cell minus each P cell present in `family`), paired bootstrap over items."""
    rows = _records(df)
    fm = _family_map(family) if family is not None else {}
    res = {}
    sd = seeds.seed_for("ps_family")
    for label, name in zip(("PS1", "PS2"), SANITY_CONDS):
        if any(name in r["conds"] for r in rows):
            if rule == "R3":
                e = dict(_wilcoxon_gate_vs_none(rows, name, "d", n_boot, sd), tested=True, endpoint="d")
                e["right_sign"] = bool(e["mean_diff"] > 0)
            else:
                e = dict(report.report_test(_arm(rows, name, A0, "y"), _arm(rows, name, "none", "y"), n_boot=n_boot, seed=sd), tested=True, endpoint="Y")
                e["right_sign"] = bool(e["b"] > e["c"])
            e.update(label=label, key=name, desc=descriptive_ps(rows, name, fm, n_boot, sd))
        else:
            e = dict(label=label, key=name, tested=False, p=1.0, b=0, c=0, right_sign=False, note="not run: p = 1 stays in the family (SAP AD.4, m = 2 always)")
        res[name] = e
    adj = stats.holm([res[c]["p"] for c in SANITY_CONDS])
    for c, p in zip(SANITY_CONDS, adj):
        res[c]["p_holm"] = p
        res[c]["gate_better"] = bool(res[c]["tested"] and res[c]["right_sign"] and p < 0.05)
    n_rej = sum(res[c]["gate_better"] for c in SANITY_CONDS)
    reading = {2: "met", 1: "partly met", 0: "not met"}[n_rej]
    return dict(per_corruption=res, holm_m=2, rule=rule, endpoint="d (Wilcoxon)" if rule == "R3" else "Y (exact McNemar)", n_rejected_right_sign=n_rej, positive_control=reading,
                label="secondary family PS, positive control; no headline claim; not evidence for JPEG, noise or splice (SAP AD.4)",
                on_not_met="pipeline audit of A2.3 (nothing tuned); the sentence 'the gate works where detection is easy' is barred" if n_rej < 2 else None,
                chance_bar_note="the A2.5 chance bar (lower 95 percent AUROC bound above 0.5, M1 items, 200 and 179) stays the only pre-registered pass/fail on detection for these two corruptions")


def descriptive_ps(rows: list[dict], name: str, fm: dict, n_boot: int, seed) -> dict:
    """Descriptive numbers printed beside a PS test (no p-value): share of discordant items, none-arm accuracy, headroom statistics, difference of paired accuracy differences."""
    from exp_p2.gate import headroom
    out = {}
    g, n = _arm(rows, name, A0, "y"), _arm(rows, name, "none", "y")
    ok = np.isfinite(g) & np.isfinite(n)
    out["share_discordant"] = float((g[ok] != n[ok]).mean()) if ok.any() else float("nan")
    out["acc_none"] = float(n[ok].mean()) if ok.any() else float("nan")
    has_clean = any("clean" in r["conds"] for r in rows)
    out["acc_clean_none"] = float(np.nanmean(_arm(rows, "clean", "none", "y"))) if has_clean else float("nan")
    if has_clean and any("chg" in r["conds"][name]["img"] for r in rows if name in r["conds"]):
        clean, none, chg = _arm(rows, "clean", "none", "d"), _arm(rows, name, "none", "d"), _arm(rows, name, "chg", "d")
        okd = np.isfinite(clean) & np.isfinite(none) & np.isfinite(chg)
        out["headroom_T1_clean_minus_none"] = headroom.paired_t(clean, none, okd)
        out["headroom_T2_changed_code_minus_none"] = headroom.paired_t(chg, none, okd)
    out["mean_n_changed"] = float(np.mean([r["conds"][name]["n_changed"] for r in rows if name in r["conds"]]))
    out["ps_minus_P_cell_accuracy_difference"] = {key: paired_boot(g - n, _arm(rows, key, A0, "y") - _arm(rows, key, "none", "y"), n_boot, seed) for key in fm.values()}
    return out


def wording(rule: str) -> str:
    return WORDING_D if rule == "R3" else WORDING_Y


def outcome_reading(prim: dict, rule: str, family, n_operating_points: int | None = None) -> dict:
    """SAP A2.2 three-way reading. positive = at least one P rejection after Holm with the right sign. negative = no P rejection AND for EVERY corruption with an operating point the
    90 percent paired-bootstrap CI of the net accuracy difference lies inside (-0.05, +0.05) AND completed n >= 240 for it; unavailable under R3 (and under NO-GO). inconclusive =
    everything else (including K1, n < 240, any CI wider than the margin)."""
    fm = _family_map(family)
    n_op = len(fm) if n_operating_points is None else n_operating_points
    w = wording(rule)
    if prim["claim_survives"]:
        pos = [c for c in config.REALISTIC if prim["per_corruption"][c]["gate_better"]]
        tail = ("; this tests the evidence ratio d only, not matching accuracy, and a rise in d can come from trimming heavy-tailed tokens" if rule == "R3"
                else "; attributing the gain to detection needs S-M")
        return dict(label="positive", corruptions=pos, rule=rule, reasons=[], tested=w,
                    sentence=f"GATE-M had a {w} than no gate on " + ", ".join(pos) + " (one model, one severity per corruption)" + tail)
    reasons = []
    if rule == "R3":
        reasons.append("rule R3: the negative reading is not available (the margin is defined for accuracy, not for d)")
    if rule == "NO-GO" or n_op == 0:
        reasons.append("K1: no corruption has an operating point")
    if rule in ("R1", "R2") and n_op:
        for c in config.REALISTIC:
            if c not in fm:
                continue
            e = prim["per_corruption"][c]
            ci = e.get("ci90")
            if e.get("n", 0) < N_MIN:
                reasons.append(f"{c}: completed n {e.get('n', 0)} < {N_MIN}")
            if ci is None or not (ci[0] > -NEGATIVE_MARGIN and ci[1] < NEGATIVE_MARGIN):
                reasons.append(f"{c}: 90 percent CI {ci} is not inside (-0.05, 0.05)")
    if not reasons:
        return dict(label="negative", rule=rule, reasons=[], tested=w, sentence="no higher matching accuracy (McNemar on Y) was detected; a gain larger than 0.05 is excluded and a loss larger than 0.05 is excluded (90 percent CI inside (-0.05, 0.05) for every corruption with an operating point). This is not 'GATE-M has no effect'")
    if rule == "R3":
        return dict(label="inconclusive", rule=rule, reasons=reasons, tested=w, sentence="no higher per-item mean/sd evidence ratio d (R3 primary) was detected; this tested d, not matching accuracy. Not 'GATE-M has no effect'")
    return dict(label="inconclusive", rule=rule, reasons=reasons, tested=w, sentence="no higher matching accuracy (McNemar on Y) was detected; the data are compatible with a net accuracy change as wide as the reported 95 percent CI. Not 'GATE-M has no effect'")


def s_m(rows: list[dict], family, prim: dict, n_boot=10000) -> dict:
    """S-M: exact McNemar GATE-M versus the geometry-matched random gate, seed 1 (arm geo0), gatekept by P (only corruptions with gate_better are tested, the others get p = 1 and stay
    in m = 3). Seeds 2 and 3 (geo1, geo2) are replications, each with its own unadjusted p, never combined. K5: for a P-rejected corruption S-M is not rejected. K6: |b - c| <= 2 on
    every P-rejected corruption."""
    fm = _family_map(family)
    res = {}
    for corr in config.REALISTIC:
        if corr in fm and prim["per_corruption"][corr]["gate_better"]:
            k = fm[corr]
            r = report.report_test(_arm(rows, k, A0, "y"), _arm(rows, k, "geo0", "y"), n_boot=n_boot, seed=seeds.seed_for("s_m"))
            r.update(tested=True, key=k, replications={s: report.report_test(_arm(rows, k, A0, "y"), _arm(rows, k, s, "y"), n_boot=n_boot, seed=seeds.seed_for("s_m")) for s in ("geo1", "geo2")})
            res[corr] = r
        else:
            res[corr] = dict(tested=False, p=1.0, b=0, c=0)
    adj = stats.holm([res[c]["p"] for c in config.REALISTIC])
    for c, p in zip(config.REALISTIC, adj):
        res[c]["p_holm"] = p
        res[c]["rejected"] = bool(res[c]["tested"] and p < 0.05 and res[c]["b"] > res[c]["c"])
    rejected_p = [c for c in config.REALISTIC if prim["per_corruption"][c]["gate_better"]]
    k5 = [c for c in rejected_p if not res[c]["rejected"]]
    k6 = bool(rejected_p) and all(abs(res[c]["b"] - res[c]["c"]) <= 2 for c in rejected_p)
    return dict(per_corruption=res, holm_m=3, seed_confirmatory="geo0 (seed 1)", K5_not_attributable_to_detection=k5 if rejected_p else None, K6_geometry_equals_gate=k6 if rejected_p else None)


def s_c(rows: list[dict], n_boot=10000) -> dict:
    """S-C clean control: exact McNemar GATE-M versus none on the clean test images, m = 1, unadjusted; a predicted small loss (spec 7.4)."""
    r = report.report_test(_arm(rows, "clean", A0, "y"), _arm(rows, "clean", "none", "y"), n_boot=n_boot, seed=seeds.seed_for("s_c"))
    r.update(holm_m=1, p_holm=r["p"], gate_worse=bool(r["c"] > r["b"] and r["p"] < 0.05), gate_better=bool(r["b"] > r["c"] and r["p"] < 0.05))
    return r


def s_dn(rows: list[dict], family, n_boot=10000) -> dict:
    """S-DN (Addendum 1 N2): GATE-M versus pixel-domain denoise, exact McNemar on Y, Holm over m = 2 (JPEG, noise). Splice has no denoise arm and is not in the family."""
    fm = _family_map(family)
    res = {}
    for corr in config.DENOISE_FOR:
        k = fm.get(corr)
        if k is not None and any(k + "_dn" in r["conds"] for r in rows):
            ya = _arm(rows, k, A0, "y")
            yb = np.array([r["conds"][k + "_dn"]["img"]["denoised"]["y"] if k + "_dn" in r["conds"] else np.nan for r in rows], float)
            res[corr] = dict(report.report_test(ya, yb, n_boot=n_boot, seed=seeds.seed_for("s_dn")), key=k, tested=True)
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
    fm = _family_map(family)

    def one(k, ep):
        w = _wilcoxon_gate_vs_none(rows, k, ep, n_boot, seeds.seed_for("s_z"))
        return dict(p=w["p"], n=w["n"], n_dropped=w["n_dropped"], ci=paired_boot(_arm(rows, k, A0, ep), _arm(rows, k, "none", ep), n_boot, seeds.seed_for("s_z")))

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


def frozen_label(frozen_meta: dict | None) -> str:
    """Label of every S-D2 number (SAP A3b.12 rule 6): which pool the rival was frozen on."""
    m = frozen_meta or {}
    if m.get("partial"):
        return f"rival frozen on the completed prefix of k = {m.get('closed_k')} items (not 200); n_q = {m.get('closed_nq')}; floor n >= {m.get('min_n')} per candidate"
    return "rival frozen on the complete M1 set (200 items)"


def s_d2(run_dir: Path, rows: list[dict], family, frozen: dict | None, codefreq=None, n_boot: int = 10000, frozen_meta: dict | None = None) -> dict:
    """S-D2 (Addendum 1 A1.2 rule 5): per-item AUROC of q minus that of the frozen rival (rival and sign fixed on M1) on the M4 test items at the M4 operating point of
    JPEG and of noise; paired bootstrap p, Holm over m = 2; a corruption with no operating point or no usable rival gets p = 1 and stays in m = 2."""
    from exp_p2.gate import detect
    fm = _family_map(family)
    res = {}
    for corr in ("jpeg", "noise"):
        fr = (frozen or {}).get(corr) or {}
        k = fm.get(corr)
        if k is None or not fr.get("available"):
            res[corr] = dict(tested=False, p=1.0, reason="no operating point" if k is None else ("no frozen rival" + (f": {fr['reason']}" if fr.get("reason") else "")))
            continue
        qa, ra = [], []
        for r in rows:
            arr = np.load(Path(run_dir) / "arrays" / f"item{r['idx']:04d}.npz")
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
        boots = d[np.random.default_rng(seeds.seed_for("s_d2")).integers(0, d.size, size=(n_boot, d.size))].mean(axis=1)
        res[corr] = dict(tested=True, key=k, rival=fr["rival"], rival_n_items=fr.get("n_items"), n_eligible=int(d.size), n_excluded=int(len(rows) - d.size), auroc_q=float(np.nanmean(qa)), auroc_rival=float(np.nanmean(ra)),
                         diff_mean=float(d.mean()), p=detect.bootstrap_p(boots), ci95=[float(np.quantile(boots, .025)), float(np.quantile(boots, .975))],
                         ci9833=[float(np.quantile(boots, .00835)), float(np.quantile(boots, .99165))], label="at the M4 rung " + k)
    adj = detect.holm_adjust({c: res[c]["p"] for c in res})
    for c in res:
        res[c]["p_holm"] = adj[c]
        res[c]["q_beats_frozen_rival"] = bool(res[c].get("tested") and res[c]["p_holm"] <= 0.05 and res[c]["diff_mean"] > 0)
    return dict(per_corruption=res, holm_m=2, rival_frozen_label=frozen_label(frozen_meta))


def mechanism(rows: list[dict], key: str, n_boot=10000) -> dict:
    """Exploratory (Tier 3) paired bootstrap contrasts; no p-value enters a claim."""
    out = {}
    geo = [f"geo{r}" for r in range(config.N_GEO_SEEDS)]
    scat = [f"scat{r}" for r in range(config.N_GEO_SEEDS)]
    sd = seeds.seed_for("mechanism")
    for field in ("y", "z", "d"):
        g = _arm(rows, key, A0, field)
        out[field] = {
            "gate_minus_none": paired_boot(g, _arm(rows, key, "none", field), n_boot, sd),
            "gate_minus_geo": paired_boot(g, _mean_arm(rows, key, geo, field), n_boot, sd),
            "gate_minus_scattered": paired_boot(g, _mean_arm(rows, key, scat, field), n_boot, sd),
            "gate_minus_changed_code": paired_boot(g, _arm(rows, key, "chg", field), n_boot, sd),
            "gate_minus_topkB": paired_boot(g, _arm(rows, key, "topkB", field), n_boot, sd),
            "gate_minus_topks3": paired_boot(g, _arm(rows, key, "topks3", field), n_boot, sd),
            "changed_code_minus_none": paired_boot(_arm(rows, key, "chg", field), _arm(rows, key, "none", field), n_boot, sd),
        }
    out["denoise_minus_none"] = {f: paired_boot(_arm(rows, key + "_dn", "denoised", f), _arm(rows, key, "none", f), n_boot, sd) for f in ("y", "z")} if any(key + "_dn" in r["conds"] for r in rows) else None
    out["gate_on_clean"] = {f: paired_boot(_arm(rows, "clean", A0, f), _arm(rows, "clean", "none", f), n_boot, sd) for f in ("y", "z")}
    return out


# ------------------------------------------------------------------------------------------------ calibration check (SAP 6)
def pooled_sd(a: np.ndarray, b: np.ndarray | None) -> float:
    a = np.asarray(a, float)
    if b is None or len(b) < 2:
        return float(a.std(ddof=1))
    b = np.asarray(b, float)
    return float(np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2)))


def z_cal(F: float, alpha: float, sigma_L: float, n_cal: int, n_test: int) -> float:
    """Z_cal = (F - alpha) / (sigma_L sqrt(1/n_cal + 1/n_test)); the standard error contains the calibration-fold noise because the CRC statement is marginal over the draw."""
    return float((F - alpha) / (sigma_L * np.sqrt(1.0 / n_cal + 1.0 / n_test))) if sigma_L > 0 else float("nan")


def fap_check(test_L: dict, cal_L: dict | None, n_cal: int, n_boot=10000) -> dict:
    """test_L / cal_L: alpha -> per-item false-alarm proportions L_i on the clean test (calibration) items. Violation (K4) iff Z_cal > 2.13 at any alpha."""
    out, viol = {}, []
    for al, L in test_L.items():
        L = np.asarray(L, float)
        n_test = len(L)
        sig = pooled_sd(L, None if cal_L is None else cal_L.get(al))
        F = float(L.mean())
        z = z_cal(F, al, sig, n_cal, n_test)
        m, lo, hi = core.bootstrap_mean_ci(L, n_boot, seeds.seed_for("fap_check"))
        out[f"{al:g}"] = dict(alpha=al, F=F, sigma_L=sig, sigma_source="calibration + test items" if cal_L is not None else "test items only", n_cal=n_cal, n_test=n_test, Z_cal=z,
                              violation=bool(z > Z_CAL_CRIT), ci_bootstrap=[lo, hi], se_analytic=float(L.std(ddof=1) / np.sqrt(n_test)))
        viol.append(bool(z > Z_CAL_CRIT))
    return dict(per_alpha=out, K4_violation_evidence=bool(any(viol)), critical_value=Z_CAL_CRIT,
                wording="A pass is 'no evidence of violation', never 'validated'.")


def cal_losses(m2_dir: Path, thr_json: dict, alpha: float) -> np.ndarray | None:
    """Per-item false-alarm proportions of the calibration items at tau_hat with the calibration jitter (re-created from the stored seed): the same draws as fit_threshold."""
    arr_dir = Path(m2_dir) / "arrays"
    if not arr_dir.exists():
        return None
    rows = sorted(common.read_jsonl(Path(m2_dir) / "items.jsonl"), key=lambda r: r["idx"])
    t = thr_json["thresholds"][f"{alpha:g}"]
    tau = cal.Threshold.from_json(t).tau
    rng = np.random.default_rng(thr_json["seed"])
    out = []
    for r in rows:
        a = np.load(arr_dir / f"item{r['idx']:04d}.npz")
        u = scores.suspicion_q(a["B"], a["D"])
        out.append(float(np.mean(cal.jitter(u, thr_json["eps0"], rng) > tau)))
    return np.array(out)


def split_replication(U_cal: list, U_test: list, alpha: float, reps: int = 2000, seed=None) -> dict:
    """Exploratory marginal check (SAP 6 step 5): pool the calibration and the clean test suspicions, draw random n_cal/n_test splits, refit tau on each calibration part and report
    the mean and the 2.5-97.5 percent range of F - alpha over the held-out parts (descriptive only; splits overlap, no p-value)."""
    pool = list(U_cal) + list(U_test)
    n_cal = len(U_cal)
    rng = np.random.default_rng(seed if seed is not None else seeds.seed_for("split_replication"))
    diffs = []
    for _ in range(reps):
        perm = rng.permutation(len(pool))
        c = [pool[i] for i in perm[:n_cal]]
        t = [pool[i] for i in perm[n_cal:]]
        thr = cal.fit_threshold(c, alpha, cal.eps0_from(c), int(rng.integers(2**31)))
        diffs.append(float(np.mean([cal.flag(u, thr, rng).mean() for u in t])) - alpha)
    d = np.array(diffs)
    return dict(alpha=alpha, reps=reps, mean_F_minus_alpha=float(d.mean()), q025=float(np.quantile(d, .025)), q975=float(np.quantile(d, .975)), label="exploratory; descriptive only")


def calibration(run: Path, rows: list[dict], family_keys: list[str], n_boot=10000, *, m2_dir: Path | None = None, split_reps: int = 0) -> dict:
    out = dict(per_condition={})
    cond_names = ["clean"] + family_keys + (sanity_present(rows) or ["patch"])
    per_item = {c: [] for c in cond_names}
    for r in rows:
        arr = np.load(run / "arrays" / f"item{r['idx']:04d}.npz")
        for c in cond_names:
            per_item[c].append(dict(z=arr[f"{c}_z"], f={al: arr[f"{c}_flag{al:g}"] for al in config.ALPHAS}, delta=arr[f"{c}_delta"], B=arr[f"{c}_B"], D=arr[f"{c}_D"]))
    test_L = {al: np.array([x["f"][al].mean() for x in per_item["clean"]]) for al in config.ALPHAS}
    thr_json, cal_L, n_cal = None, None, None
    if m2_dir is not None and (Path(m2_dir) / "threshold.json").exists():
        thr_json = json.loads((Path(m2_dir) / "threshold.json").read_text(encoding="utf8"))
        n_cal = int(thr_json["n_cal"])
        cals = {al: cal_losses(m2_dir, thr_json, al) for al in config.ALPHAS}
        cal_L = cals if all(v is not None for v in cals.values()) else None
    out["fap_check"] = fap_check(test_L, cal_L, n_cal or config.N_CAL, n_boot)
    out["realised_fap_clean"] = {k: dict(mean=v["F"], lo=v["ci_bootstrap"][0], hi=v["ci_bootstrap"][1], alpha=v["alpha"], n_items=v["n_test"]) for k, v in out["fap_check"]["per_alpha"].items()}
    if split_reps and m2_dir is not None and thr_json is not None and cal_L is not None:
        U_cal = []
        for r in sorted(common.read_jsonl(Path(m2_dir) / "items.jsonl"), key=lambda r: r["idx"]):
            a = np.load(Path(m2_dir) / "arrays" / f"item{r['idx']:04d}.npz")
            U_cal.append(scores.suspicion_q(a["B"], a["D"]))
        U_test = [scores.suspicion_q(x["B"], x["D"]) for x in per_item["clean"]]
        out["split_replication"] = split_replication(U_cal, U_test, config.ALPHA_PRIMARY, split_reps)
    for c in cond_names[1:]:
        z = np.concatenate([x["z"] for x in per_item[c]])
        f = np.concatenate([x["f"][config.ALPHA_PRIMARY] for x in per_item[c]])
        d = np.concatenate([x["delta"] for x in per_item[c]])
        n_flag = int(f.sum())
        out["per_condition"][c] = dict(precision=float((f & z).sum() / n_flag) if n_flag else float("nan"), recall=float((f & z).sum() / z.sum()) if z.sum() else float("nan"),
                                       fap_on_clean_tokens=float((f & ~z).sum() / max(1, (~z).sum())), n_flagged=n_flag, n_corrupted=int(z.sum()),
                                       prop4=theory.plug_in_from_deltas(d, z, f))
    return out


# ------------------------------------------------------------------------------------------------ completeness (SAP 8.1) and K7
def completeness_report(rows: list[dict], planned: list[dict], family, n_dup: int = 0, excluded_idx=()) -> dict:
    """planned is the committed ordered list; items excluded by the real-tokenizer rule (SAP A2.1 item 2: excluded, counted, not replaced) are removed from it and counted separately."""
    fm = _family_map(family)
    excl = sorted(set(excluded_idx) & {p["idx"] for p in planned})
    planned = [p for p in planned if p["idx"] not in set(excl)]
    done_idx = {r["idx"] for r in rows}
    plan_idx = [p["idx"] for p in planned]
    missing = [p for p in planned if p["idx"] not in done_idx]
    comp = [p for p in planned if p["idx"] in done_idx]
    k = len(comp)
    prefix = bool(done_idx == set(plan_idx[:k]))
    arms_checked = {}
    k7 = []
    for corr, key in fm.items():
        for arm in ("none", A0):
            vals = _arm(rows, key, arm, "d")
            ns = _arm(rows, key, arm, "n")
            bad = int((~np.isfinite(vals) | (ns == 0)).sum())
            arms_checked[f"{key}/{arm}"] = dict(n=len(rows), n_nan_or_empty=bad, fraction=bad / max(1, len(rows)))
            if rows and bad / len(rows) > K7_FRACTION:
                k7.append(f"{key}/{arm}")
    cov = lambda items, f: float(np.mean([f(p) for p in items])) if items else float("nan")
    worst = {}
    for corr, key in fm.items():
        b = int(((_arm(rows, key, A0, "y") == 1) & (_arm(rows, key, "none", "y") == 0)).sum())
        c = int(((_arm(rows, key, A0, "y") == 0) & (_arm(rows, key, "none", "y") == 1)).sum())
        worst[corr] = dict(p_observed=stats.mcnemar_exact([1] * b + [0] * c + [0], [0] * b + [1] * c + [0])["p"] if (b + c) else 1.0,
                           p_worst_case_all_missing_favour_none=stats.mcnemar_exact([1] * b + [0] * (c + len(missing)), [0] * b + [1] * (c + len(missing)))["p"] if (b + c + len(missing)) else 1.0)
    return dict(planned_n=len(planned), n_excluded_token_rule=len(excl), excluded_idx=excl, planned_before_exclusion=len(planned) + len(excl), completed_n=k, n_missing=len(missing), n_duplicates_removed=n_dup, prefix_ok=prefix, below_80_percent=bool(len(planned) and k < 0.8 * len(planned)),
                covariates=dict(mean_n_tok_completed=cov(comp, lambda p: p.get("n_tok", float("nan"))), mean_n_tok_missing=cov(missing, lambda p: p.get("n_tok", float("nan"))),
                                mean_order_completed=cov(comp, lambda p: p["idx"]), mean_order_missing=cov(missing, lambda p: p["idx"])),
                arms=arms_checked, K7_arms_over_5_percent=k7, K7=bool(k7), worst_case_first_holm_step=worst,
                note="No correction for missingness is applied; 'not rejected' on a fold below 80 percent complete is not read as evidence against GATE-M.")


# ------------------------------------------------------------------------------------------------ selftest (SAP 10)
def selftest(n_sim: int = 20000, seed: int = 1) -> dict:
    """Synthetic checks that must pass before real data are analysed: exact McNemar size at most nominal (n = 300, pi_d = 0.1), Holm hand case with m = 3 and p = 1 fill-in, CRC
    expected loss at most alpha on exchangeable synthetic losses, bootstrap CI covers a known difference."""
    rng = np.random.default_rng(seed)
    nd = rng.binomial(300, 0.1, n_sim)
    b = rng.binomial(nd, 0.5)
    table = {(n, k): stats.mcnemar_exact([1] * k + [0] * (n - k), [0] * k + [1] * (n - k))["p"] for n in range(0, 61) for k in range(0, n + 1)}
    rej = np.mean([table[(int(n), int(min(k, n - k)))] <= 0.05 if n <= 60 else False for n, k in zip(nd, b)])
    holm = stats.holm([0.001, 1.0, 1.0])
    L = [np.mean([cal.flag(rng.standard_t(5, 30) + np.linspace(-1, 1, 30), thr, rng).mean() for _ in range(1)]) for thr in
         [cal.fit_threshold([rng.standard_t(5, 30) + np.linspace(-1, 1, 30) for _ in range(100)], 0.05, 1e-6, int(rng.integers(2**31))) for _ in range(300)]]
    x = rng.normal(0.3, 1.0, 400)
    m, lo, hi = core.bootstrap_mean_ci(x, 2000, 5)
    res = dict(mcnemar_size=float(rej), mcnemar_size_ok=bool(rej <= 0.05), holm_ok=bool(np.allclose(holm, [0.003, 1.0, 1.0])),
               crc_mean_loss=float(np.mean(L)), crc_ok=bool(np.mean(L) <= 0.05 + 3 * np.std(L, ddof=1) / np.sqrt(len(L))), boot_ok=bool(lo <= 0.3 <= hi))
    res["all_ok"] = bool(res["mcnemar_size_ok"] and res["holm_ok"] and res["crc_ok"] and res["boot_ok"])
    return res


# ------------------------------------------------------------------------------------------------ driver
def run(run_dir: Path, family, n_boot=10000, endpoint: str = "d", frozen: dict | None = None, codefreq=None, *, planned: list[dict] | None = None, m2_dir: Path | None = None,
        split_reps: int = 0, allow_partial: bool = False, rule: str = "R1", excluded_idx=(), frozen_meta: dict | None = None) -> dict:
    """frozen_meta: the partial / closed_k / closed_nq / min_n fields of detection_frozen.json (SAP A3b.12a item 7), copied into analysis.json and used in the S-D2 label.
    family: list of family.json entries (or of condition keys). endpoint: 'd' (SAP default, Addendum 1) or 'z'. planned: the committed ordered list of test items (SAP 8.1/8.2)."""
    run_dir = Path(run_dir)
    rows, n_dup = load_items(run_dir)
    fm = _family_map(family)
    keys = list(fm.values())
    comp = completeness_report(rows, planned, family, n_dup, excluded_idx) if planned is not None else None
    if comp is not None:
        if comp["K7"]:
            raise PipelineDefect(f"K7: more than 5 percent NaN or empty-R in {comp['K7_arms_over_5_percent']}; stop and diagnose (no look at Y)")
        if comp["completed_n"] < comp["planned_n"] and not allow_partial:
            raise PartialRun(f"{comp['completed_n']} of {comp['planned_n']} planned items completed; the outcome analysis waits for the planned fold or the freeze (SAP 8.2); --allow-partial overrides and is logged")
    y_family = primary(rows, family, n_boot)                       # McNemar on Y: primary under R1/R2, secondary under R3
    prim = primary_d(rows, family, n_boot) if rule == "R3" else y_family
    caveats = [CAVEAT_D] if (rule == "R3" or endpoint == "d") else []
    if rule == "R3":
        caveats.append(CAVEAT_SM_R3)
    res = dict(meta=dict(seeds.meta(), allow_partial=bool(allow_partial)), tested_by_primary=wording(rule), caveats=caveats, rule=rule, primary_endpoint="d (z*), Wilcoxon" if rule == "R3" else "Y, exact McNemar",
               negative_available=bool(rule in ("R1", "R2")), n_items=len(rows), family=keys, endpoint=endpoint, completeness=comp, primary=prim,
               secondary_y=(dict(y_family, label="secondary under R3") if rule == "R3" else None), outcome=outcome_reading(prim, rule, family), s_m=s_m(rows, family, prim, n_boot),
               c1_test=c1mod.c1(c1mod.ys_from_rows(rows, "test"), "test (look 3, analysis step)"), s_c=s_c(rows, n_boot), s_dn=s_dn(rows, family, n_boot), s_z=s_z(rows, family, endpoint, n_boot), s_d2=s_d2(run_dir, rows, family, frozen, codefreq, n_boot, frozen_meta), frozen_meta=frozen_meta,
               ps=ps_family(rows, rule, family, n_boot), mechanism={k: mechanism(rows, k, n_boot) for k in keys + (sanity_present(rows) or ["patch"])}, calibration=calibration(run_dir, rows, keys, n_boot, m2_dir=m2_dir, split_reps=split_reps))
    if rule == "R3":
        res["s_m"]["uninformative_under_R3"] = True                                                  # stated in advance (red team N2)
        res["s_z"]["duplicate_of_primary_under_R3"] = True
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
    ap.add_argument("--m2-run", default="P2-GATE-M2")
    ap.add_argument("--endpoint", choices=["d", "z"], default="d", help="S-Z endpoint; d is the SAP default (Addendum 1), z only as sensitivity")
    ap.add_argument("--frozen", default=str(Path(common.RUNS) / "P2-GATE-M1" / "detection_frozen.json"))
    ap.add_argument("--codefreq", default=str(Path(common.RUNS) / "P2-GATE-M2" / "codefreq.npy"))
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--split-reps", type=int, default=2000, help="exploratory 300/300 split replication of the CRC check (0 = skip)")
    ap.add_argument("--allow-partial", action="store_true", help="run on an incomplete fold (logged in the output; SAP 8.2 otherwise forbids it)")
    ap.add_argument("--skip-selftest", action="store_true")
    ap.add_argument("--rule", choices=["R1", "R2", "R3", "NO-GO"], default=None, help="default: the rule recorded in family.json (n_rule.rule)")
    a = ap.parse_args(argv)
    fam = json.loads((Path(common.RUNS) / a.family_run / "family.json").read_text(encoding="utf8"))
    if fam.get("endpoint") != "d":
        print("family.json does not record endpoint d: invalid for the SAP", file=sys.stderr)
        return 2
    fp = Path(a.frozen)
    if not fp.exists():
        print(f"{fp} missing: detection_frozen.json must be committed before M3/M4 (SAP A1.2 rule 5)", file=sys.stderr)
        return 2
    if not a.skip_selftest:
        st = selftest()
        if not st["all_ok"]:
            print("SELFTEST FAILED:", st, file=sys.stderr)
            return 2
    from exp_p2.gate import baselines, folds
    cp = Path(a.codefreq)
    fdoc = json.loads(fp.read_text(encoding="utf8"))
    frozen = fdoc["frozen"]
    frozen_meta = {k: fdoc.get(k) for k in ("partial", "closed_k", "closed_nq", "min_n")}
    codefreq = baselines.CodeFreq(np.load(cp)) if cp.exists() else None
    test_fold = int(fam.get("n_rule", {}).get("test_fold", 300))
    planned = folds.test_items(json.loads(folds.folds_path().read_text(encoding="utf8")), test_fold if test_fold > 300 else None)[:test_fold]
    try:
        rule = fam.get("n_rule", {}).get("rule", "R1")
        if a.rule and a.rule != rule:
            print(f"--rule {a.rule} contradicts family.json ({rule}); the rule is fixed by the committed family.json", file=sys.stderr)
            return 2
        xp = Path(common.RUNS) / a.run_id / "token_exclusions.json"
        ex = json.loads(xp.read_text(encoding="utf8"))["excluded"] if xp.exists() else {}
        res = run(Path(common.RUNS) / a.run_id, fam["family"], a.boot, a.endpoint, frozen, codefreq, planned=planned, m2_dir=Path(common.RUNS) / a.m2_run,
                  split_reps=a.split_reps, allow_partial=a.allow_partial, rule=rule, excluded_idx=list(ex.get("test", [])) + list(ex.get("test_ext", [])), frozen_meta=frozen_meta)
    except (PartialRun, PipelineDefect) as e:
        print("STOP:", e, file=sys.stderr)
        return 3
    (Path(common.RUNS) / a.run_id / "analysis.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf8")
    print(json.dumps(dict(n_items=res["n_items"], claim_survives=res["primary"]["claim_survives"], K4=res["calibration"]["fap_check"]["K4_violation_evidence"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
