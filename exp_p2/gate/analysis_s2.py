"""CPU analysis of S2 (SAP AD.5, AB.4, AD.11-AD.13). Reads runs/P2-GATE-S2/items.jsonl; writes analysis.json. No model.

    python -m exp_p2.gate.analysis_s2 --run-id P2-GATE-S2 [--n 300] [--allow-partial]

Family S2 (secondary, m = 2, own Holm, alpha 0.05): S2-patch and S2-splice, I-GATE versus I-RAND4 ("random-gate best-of-4 re-infill"; the string 'G.1' is not used in titles, abstract, highlights, figure
titles or the S2 table header, A3b.2 item 1), exact
two-sided McNemar on Y of the KEPT draw, supported only with b > c after Holm. Same items, same g_i, same sampler, same n_draw, same selection rule: only the LOCATION of the set differs.
Items with g_i = 0 are identical in both arms (concordant), stay in n and are counted. A hypothesis is tested only if the completed n >= 120 (AD.5), else it is descriptive only (p = 1 in
Holm); a cell that has no row (splice without an operating point) is not run: p = 1, the family keeps m = 2. The prefix rule of SAP 8.1 is checked against the planned list.

Printed beside every test in the same table (AB.4 item 2.ii), descriptive, no p-value: I-GATE versus NONE, versus M (GATE-M drop) and versus I-CHG (oracle); I-RAND4 versus NONE; the draw-level
contrasts (mean of the 4 draw Y values, and the all-four-correct indicator, I-GATE minus I-RAND4; AB.4 item 4); token-level agreement of the re-infilled codes with the original clean codes (the
renamed 'token recovery rate'; AB.4 item 5: not a restoration claim); recall and precision of G; the share of rows whose S2 recomputation of Y(NONE) / Y(M) differs from M4's stored value.
Claim limits applied in code (AB.4 item 2, A3b.1, A3b.2): no wording says that re-infill 'improves' verification; an S2 result that is not rejected is labelled inconclusive, never supportive;
a kept-draw rejection is `location_claim_eligible` only if the draw-level 95 percent CI also excludes 0 on the same side (A3b.1 item 2), otherwise only the no-location-claim sentence is emitted;
I-GATE below I-RAND4 with the 95 percent interval of the kept-draw OR the draw-level contrast excluding 0 is reported as refuting the location claim for this sampler (A3b.1 item 3); the A3b.1
item 4 disclosure sentence and the A3b.2 item 4 note are written into every cell; if I-GATE is not better than NONE (interval not above 0) and the cell is not rejected, `repair_helps_claim` is False.
Recorded sensitivity (A3.1 item 3): the same test on the first 150 list items, labelled and outside the Holm set, only if the completed n is at least 150; a completed n of 120 to 239 is labelled
'partial prefix (under 80 percent of plan)' with the minimum detectable effect of the A3 power table (A3.1 item 2, A3b.6 item 5).
Seeds: seeds.seed_for('s2_family') for the tests, 's2_descriptive' for the intervals."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, core                                            # noqa: E402
from exp_p2.gate import mde, report, seeds, stats                           # noqa: E402
from exp_p2.gate.analysis_m4 import PartialRun, _records, corr_of, load_items   # noqa: E402

N_MIN = 120
N_SENS = 150                      # A3.1 item 3: the recorded sensitivity is the first 150 items of the list
N_NOMINAL = 300                   # A3.1 item 1: planned n; 80 percent of it is the partial-prefix limit (A3.1 item 2: completed n 120 to 239)
HOLM_M = 2
ALPHA_PRIME = 0.05 / HOLM_M       # per-test threshold of the A3.1 power table for S2
CELLS = (("S2-patch", "patch"), ("S2-splice", "splice"))
COMPARATOR = "random-gate best-of-4 re-infill"          # A3b.2 item 1: the S2 table header and every title-like string; "G.1" is not used there
SAMPLER_NOTE = "the sampler differs from UniDisc's in order, schedule and guidance"           # A3b.2 item 1: the clause that must follow any mention of App. G.1 in running text
DISCLOSURE = ("In I-GATE the four draws share one position set; in I-RAND4 each draw has its own random set; best-of-4 by chain log-likelihood therefore selects over position sets as well as noise in "
              "I-RAND4 and over noise only in I-GATE; the direction of the net bias is not established.")                                                     # A3b.1 item 4, verbatim
NOTE_RAND_WORSE = ("re-infilling clean positions with caption-masked prior samples destroys real caption evidence, so I-RAND4 may be worse than NONE, and the contrast then indexes in part how many "
                   "clean tokens each set touches (AB.4 item 2, A3b.2 item 4)")
SENT_MAY_CLAIM = ("with this plain random-order re-infill, repairing the set GATE-M flagged gives higher image-direction verification accuracy than repairing equal-size random sets, "
                  "best of four by chain log-likelihood, caption masked")                                                                                      # A3b.2 item 3
SENT_NO_LOCATION = ("under best-of-4 selection by chain log-likelihood, repairing the GATE-M set gave higher image-direction verification accuracy than repairing equal-size random sets")   # A3b.1 item 2
SENT_ELIGIBLE = (SENT_MAY_CLAIM + "; the kept-draw rejection is location-claim-eligible because the draw-level 95 percent interval also excludes 0 on the same side; "
                 "the claim is about this sampler and these positions only")
SENT_REFUTED = "the location claim is refuted for this sampler (it is not a statement about UniDisc's own re-infill)"                                          # A3b.1 item 3
SENT_NO_EVIDENCE = "no evidence that the flagged set is better placed than a random one under this sampler"                                                      # A3b.2 item 5
MAY_NOT_CLAIM = ["anything about UniDisc's own re-infill", "re-masking as a mechanism", "the gate's detection (a flagged set that scores better may simply contain fewer clean, evidence-bearing tokens)",
                 "that location does not matter if S2 is inconclusive", "a causal clause in the title, abstract, highlights or conclusion (AB.1 item 2)"]       # A3b.2 item 3 and AB.1 item 2


def _cond_key(rows: list[dict], corr: str) -> str | None:
    for r in rows:
        for k in r["conds"]:
            if corr_of(k) == corr:
                return k
    return None


def _col(rows, cond, arm, field):
    return np.array([r["conds"][cond]["arms"][arm][field] if cond in r["conds"] and arm in r["conds"][cond]["arms"] and field in r["conds"][cond]["arms"][arm] else np.nan for r in rows], float)


def _draw_mean(rows, cond, arm):
    return np.array([np.mean(r["conds"][cond]["arms"][arm]["y_draws"]) if cond in r["conds"] and arm in r["conds"][cond]["arms"] else np.nan for r in rows], float)


def _all_four(rows, cond, arm):
    return np.array([float(np.all(np.asarray(r["conds"][cond]["arms"][arm]["y_draws"]) == 1)) if cond in r["conds"] and arm in r["conds"][cond]["arms"] else np.nan for r in rows], float)


def _boot(a, b, n_boot, seed) -> dict:
    d = np.asarray(a, float) - np.asarray(b, float)
    ok = np.isfinite(d)
    if ok.sum() < 2:
        return dict(diff=float("nan"), lo=float("nan"), hi=float("nan"), n=int(ok.sum()))
    m, lo, hi = core.bootstrap_mean_ci(d[ok], n_boot, seed)
    return dict(diff=m, lo=lo, hi=hi, n=int(ok.sum()), n_dropped=int((~ok).sum()))


def _no_p(rep: dict) -> dict:
    """A descriptive contrast: the McNemar counts and the interval, without p-values (AB.4: no p enters a claim here)."""
    keep = ("b", "c", "n_d", "n", "acc_a", "acc_b", "delta", "ci95", "theta")
    return {k: rep[k] for k in keep if k in rep}


def _mean_or_nan(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return float(x.mean()) if x.size else float("nan")


def cell(rows: list[dict], key: str, n_boot: int) -> dict:
    sd_t, sd_d = seeds.seed_for("s2_family"), seeds.seed_for("s2_descriptive")
    yg, yr = _col(rows, key, "igate", "y"), _col(rows, key, "irand", "y")
    rep = report.report_test(yg, yr, n_boot=n_boot, seed=sd_t)
    g = np.array([r["conds"][key]["g"] if key in r["conds"] else -1 for r in rows], float)
    g0 = g == 0
    n_g0_discordant = int((g0 & (yg != yr)).sum())
    desc = dict(
        igate_vs_none=_no_p(report.report_test(yg, _col(rows, key, "none", "y"), n_boot=n_boot, seed=sd_d)),
        igate_vs_m=_no_p(report.report_test(yg, _col(rows, key, "m", "y"), n_boot=n_boot, seed=sd_d)),
        irand_vs_none=_no_p(report.report_test(yr, _col(rows, key, "none", "y"), n_boot=n_boot, seed=sd_d)),
        igate_vs_ichg=_no_p(report.report_test(yg, _col(rows, key, "ichg", "y"), n_boot=n_boot, seed=sd_d)) if np.isfinite(_col(rows, key, "ichg", "y")).any() else None,
        draw_level_accuracy_igate_minus_irand=_boot(_draw_mean(rows, key, "igate"), _draw_mean(rows, key, "irand"), n_boot, sd_d),
        all_four_correct_igate_minus_irand=_boot(_all_four(rows, key, "igate"), _all_four(rows, key, "irand"), n_boot, sd_d),
        kept_draw_igate_minus_irand=_boot(yg, yr, n_boot, sd_d),
        token_agreement_with_clean_codes=dict(
            **{f"{a}_{f}": _mean_or_nan(_col(rows, key, a, f)) for a in ("igate", "irand", "ichg") for f in ("agree_changed", "agree_set")},
            note="descriptive; share of truly changed tokens (agree_changed) or of re-infilled positions (agree_set) whose code equals the original clean code; not restoration (AB.4 item 5)"),
        gate_recall_mean=_mean_or_nan([r["conds"][key]["recall"] for r in rows if key in r["conds"]]),
        gate_precision_mean_over_g_ge_1=_mean_or_nan([r["conds"][key]["precision"] for r in rows if key in r["conds"] and r["conds"][key]["g"] >= 1]),
        s2_y_differs_from_m4=dict(none=int(sum(not r["conds"][key]["s2_y_matches_m4"]["none"] for r in rows if key in r["conds"])),
                                  gate=int(sum(not r["conds"][key]["s2_y_matches_m4"]["gate"] for r in rows if key in r["conds"])),
                                  note="S2 recomputes Y(NONE) and Y(M) from its own two caption-only passes; a difference from M4's stored value is a bf16 near-tie, counted"),
    )
    return dict(rep, key=key, n_completed=rep["n"], n_g0=int(g0.sum()), n_g0_discordant=n_g0_discordant, mean_g=_mean_or_nan(g[g >= 0]), desc=desc)


def sensitivity_first150(rows: list[dict], key: str, plan_idx: list[int] | None, n_boot: int, n_completed: int, primary_rejects: bool | None) -> dict:
    """Recorded sensitivity (A3.1 item 3): the same exact McNemar of I-GATE against I-RAND4 on the first 150 items of the list (a nested prefix of the primary; no item is chosen). It exists only if the
    completed n is at least 150, is printed beside the primary and is labelled 'sensitivity (SAP n = 150), not confirmatory, not in the Holm set'. It can neither reject nor rescue the family hypothesis.
    `sens_rejects` is the favourable-direction rejection at the Holm-m = 2 threshold of the A3.1 table (p * 2 < 0.05 with b > c): an operational reading used only to say whether the two analyses disagree
    ('the conclusion is sensitive to n'); it enters no Holm set and no claim."""
    label = "sensitivity (SAP n = 150), not confirmatory, not in the Holm set"
    if n_completed < N_SENS:
        return dict(exists=False, label=label, reason=f"completed n {n_completed} < {N_SENS}: the sensitivity exists only if the completed n is at least {N_SENS} (A3.1 item 3)")
    if plan_idx is not None:
        first = set(plan_idx[:N_SENS])
        sub = [r for r in rows if r["idx"] in first]
    else:
        sub = rows[:N_SENS]
    sd = seeds.seed_for("s2_descriptive")
    rep = report.report_test(_col(sub, key, "igate", "y"), _col(sub, key, "irand", "y"), n_boot=n_boot, seed=sd)
    rejects = bool(rep["b"] > rep["c"] and rep["p"] * HOLM_M < 0.05)
    out = dict(exists=True, label=label, n_positions=N_SENS, n_completed_in_prefix=int(rep["n"]), b=rep["b"], c=rep["c"], n_d=rep["n_d"], p=rep["p"], delta=rep["delta"], ci95=rep["ci95"],
               sens_rejects=rejects, primary_rejects=primary_rejects,
               mde_at_this_n=mde.mde_table(int(rep["n"]), ALPHA_PRIME)["by_pi_d"])
    if primary_rejects is not None:
        out["sensitive_to_n"] = bool(rejects != primary_rejects)
        if out["sensitive_to_n"]:
            out["statement"] = "the primary and the sensitivity are on opposite sides of rejection: both are shown and the conclusion is sensitive to n (A3.1 item 3)"
    return out


def partial_prefix(n_completed: int, n_nominal: int, fold_complete: bool) -> dict | None:
    """A3.1 item 2 / A3b.6 item 5: a completed n from 120 to 239 (below 80 percent of the plan) of an unfinished plan is labelled 'partial prefix (under 80 percent of plan)' and printed with the
    minimum detectable effect of the A3 power table for that n. A prefix-based result is never described as an n = 300 result."""
    if fold_complete or n_completed < N_MIN or n_completed >= 0.8 * n_nominal:
        return None
    return dict(label="partial prefix (under 80 percent of plan)", completed_n=int(n_completed), planned_n=int(n_nominal),
                mde=mde.mde_table(int(n_completed), ALPHA_PRIME),
                note=f"a prefix-based result is not described as an n = {n_nominal} result (A3b.6 item 5)")


def s2_family(df_s2, planned: list[dict] | None = None, n_boot: int = 10000, n_min: int = N_MIN, n_nominal: int = N_NOMINAL) -> dict:
    """Family S2 (SAP AD.13): see the module docstring. `df_s2` = S2 rows (list of dicts as written by run_gate_s2, or a DataFrame of them); `planned` = the committed ordered list (prefix rule);
    `n_nominal` = the planned n (300 under A3.1; 150 if Shlok declines, A3b.6 item 4)."""
    rows = _records(df_s2)
    comp = None
    plan_idx = None
    if planned is not None:
        done = {r["idx"] for r in rows}
        plan_idx = [p["idx"] for p in planned]
        k = len([i for i in plan_idx if i in done])
        comp = dict(planned_n=len(plan_idx), completed_n=k, prefix_ok=bool(done == set(plan_idx[:k])), below_80_percent=bool(plan_idx and k < 0.8 * len(plan_idx)))
    prefix_broken = bool(comp is not None and not comp["prefix_ok"])                      # SAP 8.1: a gap in the prefix makes the cells descriptive (the runner cannot produce one)
    fold_complete = bool(comp is not None and comp["completed_n"] >= comp["planned_n"])
    res = {}
    for label, corr in CELLS:
        key = _cond_key(rows, corr)
        if key is None:
            res[corr] = dict(label=label, key=None, tested=False, p=1.0, b=0, c=0, note="not run (no operating point or cell cut): p = 1 stays in the family, m = 2 (AD.5)")
            continue
        e = cell(rows, key, n_boot)
        e["label"] = label
        e["tested"] = bool(e["n_completed"] >= n_min and not prefix_broken)
        e["p_used"] = e["p"] if e["tested"] else 1.0
        if prefix_broken:
            e["note"] = "the completed items are not a prefix of the planned list (SAP 8.1): descriptive only; p = 1 in the Holm correction"
        elif not e["tested"]:
            e["note"] = f"completed n {e['n_completed']} < {n_min}: descriptive only (AD.5); p = 1 in the Holm correction"
        res[corr] = e
    adj = stats.holm([res[c]["p_used"] if res[c].get("tested") else 1.0 for _, c in CELLS])
    for (label, c), p in zip(CELLS, adj):
        e = res[c]
        e["p_holm"] = p
        e["kept_draw_rejects"] = bool(e.get("tested") and e["b"] > e["c"] and p < 0.05)                      # Holm-adjusted, b > c_cnt, favourable tail
        if e.get("key") is None:
            e["location_claim_eligible"] = e["location_supported"] = False
            e["reading"] = "not run"
            continue
        gm, dl = e["desc"]["kept_draw_igate_minus_irand"], e["desc"]["draw_level_accuracy_igate_minus_irand"]
        # A3b.1 item 2: location-claim-eligible only if the draw-level 95 percent CI excludes 0 on the same side as the kept-draw rejection
        eligible = bool(e["kept_draw_rejects"] and np.isfinite(dl["lo"]) and dl["lo"] > 0)
        # A3b.1 item 3: refuted if I-GATE is below I-RAND4 with a 95 percent CI excluding 0 on the kept-draw OR the draw-level contrast
        refuted = bool(e.get("tested") and ((np.isfinite(gm["hi"]) and gm["hi"] < 0) or (np.isfinite(dl["hi"]) and dl["hi"] < 0)))
        gn = e["desc"]["igate_vs_none"]
        not_better_than_none = bool(not (np.isfinite(gn["ci95"][0]) and gn["ci95"][0] > 0))
        e["location_claim_eligible"] = eligible
        e["location_supported"] = eligible                                    # kept for the callers of the old name: it now means eligibility, never the kept-draw rejection alone
        e["location_refuted"] = refuted
        e["draw_level_excludes_0_same_side"] = bool(np.isfinite(dl["lo"]) and dl["lo"] > 0)
        e["repair_helps_claim"] = bool(eligible and not not_better_than_none)
        if refuted:
            e["reading"] = "refuted (I-GATE below I-RAND4, 95 percent interval of the kept-draw or the draw-level contrast excludes 0)"
            e["sentence"] = SENT_REFUTED
        elif eligible:
            e["reading"] = "supported (location only)"
            e["sentence"] = SENT_ELIGIBLE
        elif e["kept_draw_rejects"]:
            e["reading"] = "kept-draw contrast rejected; draw-level interval does not exclude 0 on the same side: no location claim"
            e["sentence"] = SENT_NO_LOCATION
        else:
            e["reading"] = "inconclusive"
            e["sentence"] = SENT_NO_EVIDENCE
        if not eligible and not refuted and e["kept_draw_rejects"]:
            e["note_location"] = ("A3b.1 item 2: no sentence says or implies that the flagged set is better placed, that location matters, or that the gate finds where repair is needed")
        if not e["kept_draw_rejects"] and not_better_than_none:
            e["note_v"] = "I-GATE is not better than NONE (95 percent interval not above 0) and the cell is not rejected: there is no claim that repair helps (AB.4 item 2.v)"
        e["table_note"] = [DISCLOSURE, "Re-infilling clean positions with caption-masked prior samples destroys real caption evidence, so I-RAND4 may be worse than NONE, and the contrast then indexes in part "
                           "how many clean tokens each set touches.", "Kept draw = highest chain log-likelihood, caption masked (A3.2 item 1 (b))."]
        e["may_not_claim"] = MAY_NOT_CLAIM
        e["partial_prefix"] = partial_prefix(e["n_completed"], n_nominal, fold_complete) if e.get("tested") else None
        e["sensitivity_first150"] = sensitivity_first150(rows, e["key"], plan_idx, n_boot, e["n_completed"], e["kept_draw_rejects"] if e.get("tested") else None)
    return dict(family="S2", holm_m=HOLM_M, comparator=COMPARATOR, sampler_note=SAMPLER_NOTE, disclosure=DISCLOSURE, note_rand_worse_than_none=NOTE_RAND_WORSE, n_min=n_min, n_nominal=n_nominal,
                per_cell=res, completeness=comp,
                label="secondary family S2 (MUST experiment, not part of P); the claim-bearing cell is S2-splice (AD.5)",
                forbidden_wording=["improves verification", "restoration", "fidelity", "perceptual quality",
                                   "the string 'G.1' in the title, abstract, highlights, figure titles or the S2 table header (A3b.2 item 1); use: random-gate best-of-4 re-infill",
                                   "a location claim from a kept-draw rejection whose draw-level interval does not exclude 0 on the same side (A3b.1 item 2)",
                                   "describing a prefix-based result as an n = 300 result (A3b.6 item 5)"],
                seed_info=seeds.meta())



def selftest() -> dict:
    """Holm with p = 1 fill, the exact-McNemar counts on a constructed table, g_i = 0 concordance and the n >= 120 rule, on synthetic rows with known outcomes."""
    def row(i, g, yg, yr, yn=0):
        arm = lambda y: dict(y=y, d=0.0, kept=0, y_draws=[y] * 4, logp=[0.0] * 4, n_steps=1, n_set=g, agree_changed=0.5, agree_set=0.5, agree_changed_mean=0.5)
        return dict(idx=i, conds={"patch": dict(g=g, n_changed=4, n_tp=g, recall=1.0, precision=1.0, s2_y_matches_m4=dict(none=True, gate=True),
                                                arms=dict(none=dict(y=yn, d=0.0), m=dict(y=yn, d=0.0), igate=arm(yg), irand=arm(yr), ichg=arm(yg)))})
    rows = [row(i, 5, 1, 0) for i in range(30)] + [row(30 + i, 5, 0, 1) for i in range(2)] + [row(32 + i, 0, 1, 1) for i in range(100)]
    out = s2_family(rows, n_boot=300)
    e = out["per_cell"]["patch"]
    holm = stats.holm([e["p"], 1.0])
    ok = bool((e["b"], e["c"], e["n_g0"], e["n_g0_discordant"], e["n_completed"]) == (30, 2, 100, 0, 132) and np.isclose(e["p_holm"], holm[0]) and e["location_supported"]
              and out["per_cell"]["splice"]["p"] == 1.0 and not out["per_cell"]["splice"]["location_supported"])
    small = s2_family(rows[:30], n_boot=300)["per_cell"]["patch"]
    return dict(holm_fill_ok=ok, below_n_min_is_descriptive=bool(not small["tested"] and small["p_used"] == 1.0), all_ok=bool(ok and not small["tested"]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-GATE-S2")
    ap.add_argument("--m4-run", default="P2-GATE-M4")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--allow-partial", action="store_true", help="analyse an incomplete fold (logged in the output; SAP 8.2 otherwise forbids it)")
    ap.add_argument("--skip-selftest", action="store_true")
    a = ap.parse_args(argv)
    if not a.skip_selftest:
        st = selftest()
        if not st["all_ok"]:
            print("SELFTEST FAILED:", st, file=sys.stderr)
            return 2
    from exp_p2 import run_gate_s2
    try:
        planned, info = run_gate_s2.plan_items(a.n, Path(common.RUNS), a.m4_run)
    except (FileNotFoundError, ValueError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    run = Path(common.RUNS) / a.run_id
    rows, n_dup = load_items(run)
    eff = run / "effective_n.json"
    n_plan = len(planned) if not eff.exists() else min(len(planned), json.loads(eff.read_text(encoding="utf8"))["effective"])
    try:
        if len(rows) < n_plan and not a.allow_partial:
            raise PartialRun(f"{len(rows)} of {n_plan} planned S2 items completed; the outcome analysis waits for the planned fold or the freeze (SAP 8.2); --allow-partial overrides and is logged")
    except PartialRun as e:
        print("STOP:", e, file=sys.stderr)
        return 3
    res = s2_family(rows, planned, a.boot, n_nominal=a.n)
    res["meta"] = dict(seeds.meta(), allow_partial=bool(a.allow_partial), n_duplicates_removed=n_dup, plan=info)
    (run / "analysis.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf8")
    print(json.dumps({c: dict(label=e["label"], tested=e["tested"], b=e["b"], c=e["c"], p=e["p"], p_holm=e.get("p_holm"), reading=e.get("reading"), location_claim_eligible=e.get("location_claim_eligible")) for c, e in res["per_cell"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
