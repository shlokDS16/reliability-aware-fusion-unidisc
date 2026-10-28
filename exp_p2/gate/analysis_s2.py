"""CPU analysis of S2 (SAP AD.5, AB.4, AD.11-AD.13). Reads runs/P2-GATE-S2/items.jsonl; writes analysis.json. No model.

    python -m exp_p2.gate.analysis_s2 --run-id P2-GATE-S2 [--n 300] [--allow-partial]

Family S2 (secondary, m = 2, own Holm, alpha 0.05): S2-patch and S2-splice, I-GATE versus I-RAND4 ("random-gate best-of-4 re-infill (G.1-inspired)"; never just 'G.1', AB.4 item 1), exact
two-sided McNemar on Y of the KEPT draw, supported only with b > c after Holm. Same items, same g_i, same sampler, same n_draw, same selection rule: only the LOCATION of the set differs.
Items with g_i = 0 are identical in both arms (concordant), stay in n and are counted. A hypothesis is tested only if the completed n >= 120 (AD.5), else it is descriptive only (p = 1 in
Holm); a cell that has no row (splice without an operating point) is not run: p = 1, the family keeps m = 2. The prefix rule of SAP 8.1 is checked against the planned list.

Printed beside every test in the same table (AB.4 item 2.ii), descriptive, no p-value: I-GATE versus NONE, versus M (GATE-M drop) and versus I-CHG (oracle); I-RAND4 versus NONE; the draw-level
contrasts (mean of the 4 draw Y values, and the all-four-correct indicator, I-GATE minus I-RAND4; AB.4 item 4); token-level agreement of the re-infilled codes with the original clean codes (the
renamed 'token recovery rate'; AB.4 item 5: not a restoration claim); recall and precision of G; the share of rows whose S2 recomputation of Y(NONE) / Y(M) differs from M4's stored value.
Claim limits applied in code (AB.4 item 2): no wording says that re-infill 'improves' verification; an S2 result that is not rejected is labelled inconclusive, never supportive;
I-GATE worse than I-RAND4 with the 95 percent paired interval excluding 0 is reported as refuting the location claim; if I-GATE is not better than NONE (interval not above 0) and the cell is not
rejected, `repair_helps_claim` is False. Seeds: seeds.seed_for('s2_family') for the tests, 's2_descriptive' for the intervals."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, core                                            # noqa: E402
from exp_p2.gate import report, seeds, stats                                 # noqa: E402
from exp_p2.gate.analysis_m4 import PartialRun, _records, corr_of, load_items   # noqa: E402

N_MIN = 120
CELLS = (("S2-patch", "patch"), ("S2-splice", "splice"))
COMPARATOR = "random-gate best-of-4 re-infill (G.1-inspired)"
WORDING = ("the flagged set was {rel} placed than a random set of equal size (best of 4 draws by own likelihood, caption masked, McNemar on Y of the kept draw); "
           "this is a statement about the location of the repaired set, not about restoration, fidelity or an improvement of verification over no repair")


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


def s2_family(df_s2, planned: list[dict] | None = None, n_boot: int = 10000, n_min: int = N_MIN) -> dict:
    """Family S2 (SAP AD.13): see the module docstring. `df_s2` = S2 rows (list of dicts as written by run_gate_s2, or a DataFrame of them); `planned` = the committed ordered list (prefix rule)."""
    rows = _records(df_s2)
    res = {}
    for label, corr in CELLS:
        key = _cond_key(rows, corr)
        if key is None:
            res[corr] = dict(label=label, key=None, tested=False, p=1.0, b=0, c=0, note="not run (no operating point or cell cut): p = 1 stays in the family, m = 2 (AD.5)")
            continue
        e = cell(rows, key, n_boot)
        e["label"] = label
        e["tested"] = bool(e["n_completed"] >= n_min)
        e["p_used"] = e["p"] if e["tested"] else 1.0
        if not e["tested"]:
            e["note"] = f"completed n {e['n_completed']} < {n_min}: descriptive only (AD.5); p = 1 in the Holm correction"
        res[corr] = e
    adj = stats.holm([res[c]["p_used"] if res[c].get("tested") else 1.0 for _, c in CELLS])
    for (label, c), p in zip(CELLS, adj):
        e = res[c]
        e["p_holm"] = p
        e["location_supported"] = bool(e.get("tested") and e["b"] > e["c"] and p < 0.05)
        if e.get("key") is None:
            e["reading"] = "not run"
            continue
        gm = e["desc"]["kept_draw_igate_minus_irand"]
        refuted = bool(e.get("tested") and np.isfinite(gm["hi"]) and gm["hi"] < 0)
        gn = e["desc"]["igate_vs_none"]
        not_better_than_none = bool(not (np.isfinite(gn["ci95"][0]) and gn["ci95"][0] > 0))
        e["location_refuted"] = refuted
        e["repair_helps_claim"] = bool(e["location_supported"] and not not_better_than_none)
        e["reading"] = "supported (location only)" if e["location_supported"] else ("refuted (I-GATE worse than I-RAND4, interval excludes 0)" if refuted else "inconclusive")
        e["sentence"] = WORDING.format(rel="better" if e["location_supported"] else ("worse" if refuted else "not shown to be better or worse"))
        if not e["location_supported"] and not_better_than_none:
            e["note_v"] = "I-GATE is not better than NONE (95 percent interval not above 0) and the cell is not rejected: there is no claim that repair helps (AB.4 item 2.v)"
    comp = None
    if planned is not None:
        done = {r["idx"] for r in rows}
        plan_idx = [p["idx"] for p in planned]
        k = len([i for i in plan_idx if i in done])
        comp = dict(planned_n=len(plan_idx), completed_n=k, prefix_ok=bool(done == set(plan_idx[:k])), below_80_percent=bool(plan_idx and k < 0.8 * len(plan_idx)))
    return dict(family="S2", holm_m=2, comparator=COMPARATOR, n_min=n_min, per_cell=res, completeness=comp, label="secondary family S2 (MUST experiment, not part of P); the claim-bearing cell is S2-splice (AD.5)",
                forbidden_wording=["improves verification", "restoration", "fidelity", "perceptual quality", "G.1 comparator (use: random-gate best-of-4 re-infill, G.1-inspired)"],
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
    res = s2_family(rows, planned, a.boot)
    res["meta"] = dict(seeds.meta(), allow_partial=bool(a.allow_partial), n_duplicates_removed=n_dup, plan=info)
    (run / "analysis.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf8")
    print(json.dumps({c: dict(label=e["label"], tested=e["tested"], b=e["b"], c=e["c"], p=e["p"], p_holm=e.get("p_holm"), reading=e.get("reading")) for c, e in res["per_cell"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
