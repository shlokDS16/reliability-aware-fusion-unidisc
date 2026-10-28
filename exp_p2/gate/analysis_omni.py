"""CPU analysis of the Omni family R (SAP AD.7, AB.5, AD.13). No model, no GPU.

    python -m exp_p2.gate.analysis_omni gate  --timing-run P2-OMNI-TIMING --m2-run P2-GATE-M2 --m4-run P2-GATE-M4 --n-plus K --time-left-h H [--guard-cap-mib X]    # -> omni_gate.json
    python -m exp_p2.gate.analysis_omni fit   --run-id P2-OMNI-R-CAL                                                                                   # -> threshold.json (alpha 0.05)
    python -m exp_p2.gate.analysis_omni pos   --run-id P2-OMNI-R-POS                                                                                   # -> pos_control.json
    python -m exp_p2.gate.analysis_omni r     --run-id P2-OMNI-R-TEST --p-result runs/P2-GATE-M4/analysis.json [--rule R1]                             # -> analysis.json
    python -m exp_p2.gate.analysis_omni selftest

Functions named in SAP AD.13: `omni_gate(timing_log, m2_log, m4_log, ...)` (the GO rule and the n_R rule) and `omni_r(df, P_result, ...)` (eligibility from P, one McNemar per corruption of
P+, Holm over m_R = |P+|). Seeds: the SAP's registry (`seeds.ANALYSES`) has no entries for these two names; until the owner of seeds.py appends them (appending leaves earlier children unchanged)
a name-derived SeedSequence is used and written into the output (`seed_note`)."""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, core                                            # noqa: E402
from exp_p2.gate import analysis_m4, artifacts, calibrate as cal, config, fit_threshold, report, seeds, stats     # noqa: E402

# ---- constants of the SAP (AD.7, AB.5), not tuned
T_MAX_H = 1.5                     # GO (d): T(n) <= 1.5 GPU-h
N_CHOICES = (150, 120)            # the size rule: 150 if (d) and (e) hold, else 120, else NO-GO
N_CAL_OMNI = 100                  # own calibration: the first 100 clean calibration items (slack 1/101)
N_POS_CONTROL = 50                # AB.5 item 2
N_FORMAL_MIN = 120                # completed n below this: descriptive only
WARMUP = 5
ALPHA_R = config.ALPHA_PRIMARY    # 0.05, B = 1
M2_ITEMISED_PASSES = 12           # run_gate_m2 docstring: 8 (B) + 2 (image direction) + 2 (text direction); used ONLY if the M2 rows carry no n_rows (flagged in the output)
WORDING_REPLICATED = "directional replication on a second model, 4-bit quantised; quantisation confounds a likelihood-based detector"
WORDING_NOT = "not replicated; inconclusive at this n"
WORDING_R2_TAIL = "; same test images as P, not independent items"


def _seed(name: str):
    if name in seeds.ANALYSES:
        return seeds.seed_for(name), None
    return np.random.SeedSequence([seeds.ROOT_SEED, zlib.crc32(name.encode())]), f"'{name}' is not in seeds.ANALYSES; name-derived SeedSequence([{seeds.ROOT_SEED}, crc32]) used (append the name to the registry)"


# ------------------------------------------------------------------------------------------------ the go/no-go
def p_plus(P_result: dict) -> list[str]:
    """P+ = corruptions of family P rejected after Holm with b > c (analysis_m4.primary: per_corruption[c]['gate_better']). Accepts the 'primary' dict or the whole analysis.json."""
    prim = P_result.get("primary", P_result)
    per = prim["per_corruption"]
    return [c for c in config.REALISTIC if per.get(c, {}).get("gate_better")]


def pass_counts(m2_log: list[dict], m4_log: list[dict], *, K: int = config.K, p_cal: float | None = None, p_test: float | None = None) -> dict:
    """Per-item pass counts of the UniDisc runs, read from the logs (SAP AD.7: 'as logged in the M2 and M4 runs; no new count is invented').
    p_cal  = median `n_rows` of the M2 item rows (12 expected: B 8 + image direction 2 + text direction 2). If no M2 row carries `n_rows` the itemised 12 of run_gate_m2 is used and flagged.
    p_test = median over M4 items of n_rows / (number of GATED conditions in the row = conditions whose kind is not 'denoise'). This is an UPPER BOUND of the none + GATE-M arms that Omni
             needs per gated condition (M4 n_rows also counts the text direction, TbV and the lambda passes); a rule-(d) failure caused by it is reported as such. Explicit overrides
             must be committed in the run card and are recorded here.
    p_B    = K (plain B of the positive control: K complementary passes per item)."""
    out = dict(K=K, p_B=K)
    m2 = [r["n_rows"] for r in m2_log if "n_rows" in r]
    if p_cal is not None:
        out.update(p_cal=float(p_cal), p_cal_source="explicit override (run card)")
    elif m2 and len(m2) == len(m2_log):
        out.update(p_cal=float(np.median(m2)), p_cal_source="median n_rows of the M2 rows")
    else:
        out.update(p_cal=float(M2_ITEMISED_PASSES), p_cal_source="run_gate_m2 docstring itemisation (the M2 rows carry no n_rows)")
    if p_test is not None:
        out.update(p_test=float(p_test), p_test_source="explicit override (run card)")
    else:
        per = []
        for r in m4_log:
            if "n_rows" not in r:
                continue
            ng = sum(1 for c in r.get("conds", {}).values() if c.get("kind") != "denoise")
            if ng:
                per.append(r["n_rows"] / ng)
        if per:
            out.update(p_test=float(np.median(per)), p_test_source="median of M4 n_rows / gated conditions (upper bound, see docstring)")
        else:
            out.update(p_test=None, p_test_source="no M4 row with n_rows: cannot be derived")
    return out


def timing_t(timing_log: list[dict], n_passes: int = 20, warmup: int = WARMUP) -> dict:
    """t = median wall seconds of passes 6 to 20 (rows in index order; the first five are warm-up)."""
    rows = sorted((r for r in timing_log if "fwd_s" in r), key=lambda r: r["idx"])
    fwd = [float(r["fwd_s"]) for r in rows]
    used = fwd[warmup:n_passes]
    return dict(n_rows=len(rows), t_seconds=float(np.median(used)) if used else None, n_used=len(used), complete=bool(len(rows) >= n_passes and len(used) == n_passes - warmup),
                first=fwd[:3], median_all=float(np.median(fwd)) if fwd else None, max=max(fwd) if fwd else None)


def T_hours(t: float, n: int, n_plus: int, pc: dict, n_cal: int = N_CAL_OMNI, n_pos: int = N_POS_CONTROL) -> float:
    """T(n) = t x [100 p_cal + n p_test (1 + |P+|) + 50 p_B] / 3600 GPU-h (SAP AD.7 plus the AB.5 item 2 cost of the positive control)."""
    return float(t * (n_cal * pc["p_cal"] + n * pc["p_test"] * (1 + n_plus) + n_pos * pc["p_B"]) / 3600.0)


def _cond(ok: bool, **kw) -> dict:
    return dict(ok=bool(ok), **kw)


def omni_gate(timing_log: list[dict], m2_log: list[dict], m4_log: list[dict], *, n_plus: int, time_left_h: float | None, adapter_signature: dict | None = None,
              selfcheck: dict | None = None, guard_cap_mib: float | None = None, chunk_events: list[dict] | None = None, crash_events: list | None = None,
              p_cal: float | None = None, p_test: float | None = None, n_passes: int = 20) -> dict:
    """GO rule of AD.7 with rule (b) as replaced by AB.5 item 1. GO iff (a) and (b) and (c) hold and the n-rule yields n_R in {150, 120}.
    (a) the model loaded and 20 passes finished with no guard stop, item error, hold stop or crash-log event, all log-probabilities finite;
    (b) the adapter checks were run AND signed by the gate-auditor (signature verdict PASS naming this self-check) and the self-check records all of them ok;
    (c) peak allocated GPU memory of every pass is within the guard cap in force (guard_cap_mib = mem_frac x device memory, from omni_env.json);
    (d) T(n) <= 1.5 GPU-h;   (e) time left before the results freeze >= 2 T(n).      n_R = 150 if (d) and (e) at 150, else 120 if they hold at 120, else NO-GO."""
    if n_plus <= 0:
        return dict(go=False, status="not_run", reason="P+ is empty: family R is not run, not even the timing stage (AD.7)", n_R=None)
    events = chunk_events or []
    bad_events = [e for e in events if e.get("event") in ("guard_stop", "item_error", "hold_stop", "dirty_blocked")]
    tt = timing_t(timing_log, n_passes)
    rows = [r for r in timing_log if "fwd_s" in r]
    finite = all(r.get("finite", True) for r in rows)
    conds = {"a": _cond(tt["complete"] and not bad_events and not crash_events and finite, n_rows=tt["n_rows"], guard_or_error_events=bad_events[:3], crash_events=list(crash_events or [])[:3], all_finite=finite)}
    sig_ok = bool(adapter_signature and adapter_signature.get("signed_by") == "gate-auditor" and adapter_signature.get("verdict") == "PASS")
    chk_ok = bool(selfcheck and selfcheck.get("ids_equal") and selfcheck.get("adapter", {}).get("all_ok"))
    conds["b"] = _cond(sig_ok and chk_ok, signature_ok=sig_ok, selfcheck_all_ok=chk_ok, failed=(selfcheck or {}).get("adapter", {}).get("failed"))
    peaks = [float(r["peak_alloc_mib"]) if "peak_alloc_mib" in r else float(r["peak_gb"]) * 1e9 / 2 ** 20 for r in rows if ("peak_alloc_mib" in r or "peak_gb" in r)]
    conds["c"] = _cond(bool(peaks) and guard_cap_mib is not None and max(peaks) <= guard_cap_mib, max_peak_alloc_mib=max(peaks) if peaks else None, guard_cap_mib=guard_cap_mib)
    pc = pass_counts(m2_log, m4_log, p_cal=p_cal, p_test=p_test)
    T, de = {}, {}
    if tt["t_seconds"] is not None and pc["p_test"] is not None:
        for n in N_CHOICES:
            T[n] = T_hours(tt["t_seconds"], n, n_plus, pc)
            de[n] = dict(d=bool(T[n] <= T_MAX_H), e=bool(time_left_h is not None and time_left_h >= 2 * T[n]), T_h=T[n])
    n_R = next((n for n in N_CHOICES if n in de and de[n]["d"] and de[n]["e"]), None)
    conds["d"] = _cond(any(v["d"] for v in de.values()), per_n={str(n): v["d"] for n, v in de.items()}, limit_h=T_MAX_H)
    conds["e"] = _cond(any(v["e"] for v in de.values()), per_n={str(n): v["e"] for n, v in de.items()}, time_left_h=time_left_h)
    go = bool(conds["a"]["ok"] and conds["b"]["ok"] and conds["c"]["ok"] and n_R is not None)
    return dict(go=go, status="GO" if go else "NO-GO", n_R=n_R if go else None, n_plus=n_plus, timing=tt, pass_counts=pc, T_hours={str(k): v for k, v in T.items()}, conditions=conds,
                formula="T(n) = t x [100 p_cal + n p_test (1+|P+|) + 50 p_B] / 3600", wording_if_no_go="R is 'not run / incomplete' in the deviations box; no other model is substituted; no shrinking below n = 120 (AD.7)")


# ------------------------------------------------------------------------------------------------ calibration and positive control (CPU, after the GPU stages)
def fit_omni_threshold(run_dir: Path, *, force: bool = False) -> dict:
    """CRC at alpha 0.05 (B = 1) on the Omni calibration items of run_dir (the first 100 clean items minus the Omni token exclusions). Statistic q = -(B - D). Write-once threshold.json."""
    run = Path(run_dir)
    rows = sorted(common.read_jsonl(run / "items.jsonl"), key=lambda r: r["idx"])
    if not rows:
        raise FileNotFoundError(f"{run}/items.jsonl has no rows")
    U, ids = [], []
    for r in rows:
        arr = np.load(run / "arrays" / f"item{r['idx']:04d}.npz")
        U.append(fit_threshold.suspicion_from_arrays(arr, "q"))
        ids.append(r["gid"])
    res = fit_threshold.fit_from_arrays(U, ids, "q", alphas=(ALPHA_R,))
    res.update(model="Omni-Diffusion 8B NF4", own_calibration=True, n_planned=N_CAL_OMNI, wording=res["wording"] + " (Omni model, 4-bit; own calibration; slack 1/(n+1))")
    out = run / "threshold.json"
    artifacts.write_once(out, json.dumps(res, indent=1), force)
    return res


def omni_positive_control(run_dir: Path, *, n_boot: int = 10000, force: bool = False, write: bool = True) -> dict:
    """AB.5 item 2: mean per-item AUROC of plain-B (suspicion = -B) against the changed-code labels under the code-level patch corruption; the lower 95 percent item-bootstrap bound must
    exceed 0.5. Pass proves only that the pipeline is not at chance on the easiest corruption."""
    run = Path(run_dir)
    rows = sorted(common.read_jsonl(run / "items.jsonl"), key=lambda r: r["idx"])
    au = []
    for r in rows:
        arr = np.load(run / "arrays" / f"item{r['idx']:04d}.npz")
        au.append(core.auroc(-np.asarray(arr["B"], np.float64), np.asarray(arr["z"], bool)))
    au = np.asarray(au, float)
    ss, note = _seed("omni_r")
    m, lo, hi = core.bootstrap_mean_ci(au, n_boot, ss, alpha=0.05)
    res = dict(n_items=int(len(rows)), n_finite=int(np.isfinite(au).sum()), mean_auroc=m, ci95=[lo, hi], lower_bound=lo, passed=bool(np.isfinite(lo) and lo > 0.5), per_item_auroc_quantiles=[float(q) for q in np.nanquantile(au, [0.1, 0.5, 0.9])] if np.isfinite(au).any() else None,
               rule="lower 95 percent item-bootstrap bound of the mean per-item AUROC of plain-B against changed-code labels (patch, code level) must exceed 0.5 (AB.5 item 2)",
               on_fail="R is 'pipeline defect: not run'; no R item is scored; nothing is tuned", seed_note=note)
    if write:
        artifacts.write_once(run / "pos_control.json", json.dumps(res, indent=1), force)
    return res


# ------------------------------------------------------------------------------------------------ the test
def _y(rows, cond, arm):
    return analysis_m4._arm(rows, cond, arm, "y")


def omni_r(df, P_result: dict, *, rule: str = "R1", family=None, pos_control: dict | None = None, n_boot: int = 10000) -> dict:
    """Family R (SAP AD.7): for each corruption c in P+, exact two-sided McNemar of GATE-M (alpha 0.05, own Omni calibration) versus none on the image-direction Y, Holm over m_R = |P+|,
    alpha 0.05, own family. Completed n below 120: descriptive only. No pooling with UniDisc, no heterogeneity estimate. 'Generalises' is not allowed, 'negative' is not available.
    df: list of dicts or DataFrame of Omni item rows (conds[key].img[arm].y, conds[key].gate['0.05'])."""
    rows = analysis_m4._records(df)
    plus = p_plus(P_result)
    if not plus:
        return dict(status="not_run", reason="P+ is empty (AD.7)", p_plus=[], wording=None)
    if pos_control is not None and not pos_control.get("passed"):
        return dict(status="pipeline_defect", reason="positive control failed (AB.5 item 2): R is 'pipeline defect: not run'", p_plus=plus, pos_control=pos_control, wording=None)
    fam = family if family is not None else sorted({k for r in rows for k in r["conds"] if k != "clean"})
    fm = analysis_m4._family_map(fam)
    A0 = analysis_m4.A0
    n_done = len(rows)
    ss, note = _seed("omni_r")
    res = {}
    for c in plus:
        if c not in fm:
            res[c] = dict(tested=False, p=1.0, b=0, c=0, note="no rows for this corruption (it was not run); p = 1 stays in the family")
            continue
        k = fm[c]
        res[c] = dict(report.report_test(_y(rows, k, A0), _y(rows, k, "none"), n_boot=n_boot, seed=ss), tested=True, key=k)
    adj = stats.holm([res[c]["p"] for c in plus])
    for c, p in zip(plus, adj):
        res[c]["p_holm"] = p
        res[c]["replicated"] = bool(res[c]["tested"] and res[c]["b"] > res[c]["c"] and p < 0.05)
    formal = n_done >= N_FORMAL_MIN
    any_rep = any(res[c]["replicated"] for c in plus)
    tail = WORDING_R2_TAIL if rule == "R2" else ""
    if not formal:
        wording = f"descriptive only (completed n = {n_done} < {N_FORMAL_MIN}); no test is reported as a result"
    elif any_rep:
        wording = WORDING_REPLICATED + tail
    else:
        wording = WORDING_NOT + tail
    desc = {}
    for c in plus:
        if c not in fm:
            continue
        k = fm[c]
        acc_clean, acc_c = np.nanmean(_y(rows, "clean", "none")), np.nanmean(_y(rows, k, "none"))
        fl = [r["conds"]["clean"]["gate"][f"{ALPHA_R:g}"]["n_flag"] / r["conds"]["clean"].get("n_tokens", 256) for r in rows if "clean" in r["conds"]]
        desc[c] = dict(none_acc_clean=float(acc_clean), none_acc_corrupted=float(acc_c), none_accuracy_drop=float(acc_clean - acc_c), drop_paired_boot=analysis_m4.paired_boot(_y(rows, "clean", "none"), _y(rows, k, "none"), n_boot, seed=ss),
                       flagged_share_on_clean_test_items=float(np.mean(fl)) if fl else None)
    return dict(status="analysed", p_plus=plus, holm_m=len(plus), per_corruption=res, completed_n=n_done, formal=bool(formal), rule=rule, alpha=0.05,
                replicated_any=bool(formal and any_rep), wording=wording, descriptive=desc, pos_control=pos_control, seed_note=note,
                forbidden="no 'generalises'; no 'negative'; no pooling or heterogeneity estimate with UniDisc; a failed R does not weaken P (AD.7)")


# ------------------------------------------------------------------------------------------------ CLI
def _rows(run: str) -> list[dict]:
    return common.read_jsonl(Path(common.RUNS) / run / "items.jsonl")


def _cmd_gate(a) -> int:
    runs = Path(common.RUNS)
    tdir = runs / a.timing_run
    sel = json.loads((tdir / "selfcheck.json").read_text(encoding="utf8")) if (tdir / "selfcheck.json").exists() else None
    sig = json.loads((tdir / "adapter_signature.json").read_text(encoding="utf8")) if (tdir / "adapter_signature.json").exists() else None
    env = json.loads((tdir / "omni_env.json").read_text(encoding="utf8")) if (tdir / "omni_env.json").exists() else {}
    cap = a.guard_cap_mib if a.guard_cap_mib is not None else env.get("guard_cap_mib")
    res = omni_gate(_rows(a.timing_run), _rows(a.m2_run), _rows(a.m4_run), n_plus=a.n_plus, time_left_h=a.time_left_h, adapter_signature=sig, selfcheck=sel, guard_cap_mib=cap,
                    chunk_events=common.read_jsonl(tdir / "chunks.jsonl"), p_cal=a.p_cal, p_test=a.p_test)
    res["signature_binds_selfcheck"] = bool(sig and sel and sig.get("selfcheck_sha256") == _sha(tdir / "selfcheck.json"))
    if sig and not res["signature_binds_selfcheck"] and res.get("conditions"):
        res["conditions"]["b"]["ok"] = False
        res["conditions"]["b"]["signature_does_not_match_selfcheck_sha256"] = True
        res["go"], res["status"], res["n_R"] = False, "NO-GO", None
    artifacts.write_once(tdir / "omni_gate.json", json.dumps(res, indent=1, default=str), a.force)
    print(json.dumps({k: res.get(k) for k in ("go", "status", "n_R", "T_hours")}, indent=1))
    return 0


def _sha(path: Path) -> str | None:
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).exists() else None


def selftest(seed: int = 3) -> dict:
    """Synthetic checks of the GO rule and the n rule (hand-computed: p_cal 12, p_test 75 / 3 gated conditions = 25, p_B 8)."""
    base = [dict(idx=i, fwd_s=(5.0 if i < 5 else 0.3), peak_alloc_mib=6400.0, finite=True) for i in range(20)]
    m2 = [dict(idx=i, n_rows=12) for i in range(10)]
    m4 = [dict(idx=i, n_rows=75, conds={"clean": {"kind": "clean"}, "jpeg10": {"kind": "pixel"}, "jpeg10_dn": {"kind": "denoise"}, "patch": {"kind": "token"}}) for i in range(10)]
    sig = dict(signed_by="gate-auditor", verdict="PASS")
    sel = dict(ids_equal=True, adapter=dict(all_ok=True, failed=[]))
    kw = dict(adapter_signature=sig, selfcheck=sel, guard_cap_mib=7500.0)
    g = omni_gate(base, m2, m4, n_plus=2, time_left_h=10.0, **kw)                                                       # T(150) = 0.3 (1200 + 11250 + 400) / 3600 = 1.071
    g120 = omni_gate([dict(r, fwd_s=(5.0 if r["idx"] < 5 else 0.6)) for r in base], m2, m4, n_plus=1, time_left_h=10.0, **kw)   # 0.6 x 9100 / 3600 = 1.517 > 1.5; n = 120: 1.267
    gno = omni_gate([dict(r, fwd_s=(5.0 if r["idx"] < 5 else 1.0)) for r in base], m2, m4, n_plus=1, time_left_h=10.0, **kw)    # n = 120: 2.11 > 1.5
    gtime = omni_gate(base, m2, m4, n_plus=2, time_left_h=2.0, **kw)                                                    # 2 T(150) = 2.14 > 2.0, 2 T(120) = 1.89 <= 2.0
    return dict(go_150=bool(g["go"] and g["n_R"] == 150 and abs(g["T_hours"]["150"] - 1.0708333) < 1e-6), n120=g120["n_R"], nogo_slow=bool(not gno["go"] and gno["n_R"] is None), time_rule_n=gtime["n_R"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gate")
    g.add_argument("--timing-run", default="P2-OMNI-TIMING")
    g.add_argument("--m2-run", default="P2-GATE-M2")
    g.add_argument("--m4-run", default="P2-GATE-M4")
    g.add_argument("--n-plus", type=int, required=True)
    g.add_argument("--time-left-h", type=float, required=True)
    g.add_argument("--guard-cap-mib", type=float, default=None)
    g.add_argument("--p-cal", type=float, default=None)
    g.add_argument("--p-test", type=float, default=None)
    g.add_argument("--force", action="store_true")
    for name in ("fit", "pos"):
        s = sub.add_parser(name)
        s.add_argument("--run-id", required=True)
        s.add_argument("--force", action="store_true")
    r = sub.add_parser("r")
    r.add_argument("--run-id", default="P2-OMNI-R-TEST")
    r.add_argument("--p-result", default=None, help="analysis.json of the M4 run (default runs/P2-GATE-M4/analysis.json)")
    r.add_argument("--family-run", default="P2-GATE-M3")
    r.add_argument("--pos-run", default="P2-OMNI-R-POS")
    r.add_argument("--rule", default=None)
    r.add_argument("--force", action="store_true")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    runs = Path(common.RUNS)
    if a.cmd == "gate":
        return _cmd_gate(a)
    if a.cmd == "fit":
        res = fit_omni_threshold(runs / a.run_id, force=a.force)
        print(json.dumps({k: res[k] for k in ("n_cal", "eps0", "ids_hash")} | {k: v["tau"] for k, v in res["thresholds"].items()}, indent=1))
        return 0
    if a.cmd == "pos":
        res = omni_positive_control(runs / a.run_id, force=a.force)
        print(json.dumps({k: res[k] for k in ("n_items", "mean_auroc", "lower_bound", "passed")}, indent=1))
        return 0 if res["passed"] else 3
    if a.cmd == "selftest":
        print(json.dumps(selftest(), indent=1))
        return 0
    prim_path = Path(a.p_result) if a.p_result else runs / "P2-GATE-M4" / "analysis.json"
    P = json.loads(prim_path.read_text(encoding="utf8"))
    fam = json.loads((runs / a.family_run / "family.json").read_text(encoding="utf8"))
    pos = json.loads((runs / a.pos_run / "pos_control.json").read_text(encoding="utf8")) if (runs / a.pos_run / "pos_control.json").exists() else None
    rows, _ = analysis_m4.load_items(runs / a.run_id)
    nr = fam.get("n_rule", "R1")
    res = omni_r(rows, P, rule=a.rule or P.get("rule") or (nr.get("rule", "R1") if isinstance(nr, dict) else str(nr)), family=[f["key"] for f in fam["family"]], pos_control=pos)
    artifacts.write_once(runs / a.run_id / "analysis.json", json.dumps(res, indent=1, default=str), a.force)
    print(json.dumps({k: res.get(k) for k in ("status", "p_plus", "completed_n", "formal", "wording")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
