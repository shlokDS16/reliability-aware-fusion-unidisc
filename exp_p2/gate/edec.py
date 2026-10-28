"""E-dec (SAP Addendum A2 AD.2, names of Addendum A2b AB.2, wording limits AB.1): the corruption loss split into three parts. Secondary, descriptive, estimation only.
CPU only; no model; it reads the M4 per-item rows (`runs/P2-GATE-M4/items.jsonl`) and writes `edec.json`.

    python -m exp_p2.gate.edec run --run-id P2-GATE-M4 --family-run P2-GATE-M3 [--boot 10000] [--out runs/P2-GATE-M4/edec.json]
    python -m exp_p2.gate.edec selftest

Per item i and cell c (P1 to P3 at their operating points, PS1 patch, PS2 swap), on the size-free evidence d (A1.1) and arms clean, none, chg (changed-code gate) and GM (GATE-M, alpha 0.05):
    T_i = d_clean - d_none     total corruption loss
    U_i = d_clean - d_chg      residual loss under the oracle gate     (AD.2 "treatment part"; renamed by AB.2)
    R_i = d_GM - d_none        realised recovery by GATE-M
    V_i = d_chg - d_GM         gap to the oracle gate                  (AD.2 "detection part"; renamed by AB.2; negative if GATE-M beats the oracle)
    T_i = U_i + R_i + V_i      identity by algebra; asserted to 1e-9 item by item and in every bootstrap resample.
Companion on the accuracy scale with the same split (A = mean Y): A_clean - A_none = (A_clean - A_chg) + (A_GM - A_none) + (A_chg - A_GM), on the SAME complete-case items.
Complete case: an item enters a cell only if all four d are finite (|R| >= 2 and sd > 0 in each arm); the numbers dropped, and by which arm, are counted. A cell without arms is absent and counted.
Interval: paired percentile bootstrap over items, 10,000 resamples, items resampled jointly (T, U, R, V of d and of Y share one index matrix, so the identity holds in every resample); 95 percent for
every cell and, additionally, 98.33 percent for the P cells. Shares U/T, R/T, V/T are reported only if the lower 95 percent bound of tau_T exceeds 0 (and tau_T is not numerically zero).
Label: secondary, descriptive. No test, no p-value, no multiplicity statement, not a family. No causal clause (AB.1): no text may say GATE-M "failed because of detection" or use E-dec to
explain a P result; the words "treatment" and "detection" are not used for U and V in the abstract, highlights or conclusion (AB.2). U and V are relative to the changed-code label, which is an
encoder-instability label, not an evidence oracle (AD.2 limits)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2.gate import config, seeds                                       # noqa: E402

CELLS = ("P1", "P2", "P3", "PS1", "PS2")
P_CELLS = ("P1", "P2", "P3")
PS_CELLS = ("PS1", "PS2")
P_CORRUPTION = dict(zip(P_CELLS, config.REALISTIC))                          # P1 jpeg, P2 noise, P3 splice (Holm label order of family P)
PS_KEY = {"PS1": "patch", "PS2": "swap"}
ARMS = ("clean", "none", "chg", "gm")
A0 = f"gate{config.ALPHA_PRIMARY:g}"
N_BOOT = 10000
IDENTITY_TOL = 1e-9
T_NUMERIC_ZERO = 1e-6                                                         # "a ratio with a denominator near zero is not reported": numeric guard on tau_T (d units); the rule is the CI bound
NAMES = dict(T="total corruption loss", U="residual loss under the oracle gate", R="realised recovery by GATE-M", V="gap to the oracle gate")
LABEL = "secondary, descriptive; no hypothesis test, no p-value, no multiplicity statement, not a family (AD.2, AB.2); no causal clause (AB.1)"
EDEC_SEED_NAME, EDEC_SEED_POSITION = "edec", 28            # position 28 = the first name after s2_descriptive (index 27) in seeds.ANALYSES; see edec_seed()


class IdentityError(AssertionError):
    """T = U + R + V failed: the arms were mislabelled or the arithmetic changed (SAP AD.2: the script asserts it to 1e-9)."""


def edec_seed() -> np.random.SeedSequence:
    """The bootstrap seed: the child of `seeds.ANALYSES` named "edec" (appended 2026-10-28 at spawn position 28, the value this module computed before the append; asserted by the tests)."""
    return seeds.seed_for(EDEC_SEED_NAME)


# ------------------------------------------------------------------------------------------------ rows -> long cell records
def _records(df) -> list[dict]:
    if hasattr(df, "to_dict") and hasattr(df, "columns"):
        return df.to_dict("records")
    return list(df)


def corr_of(key: str) -> str:
    return re.match(r"[a-z]+", key).group(0)


def cell_keys(family) -> dict[str, str | None]:
    """cell label -> M4 condition key (None = no operating point). `family` is a list of family.json entries or condition keys."""
    fm = {}
    for f in family:
        key = f["key"] if isinstance(f, dict) else f
        fm[corr_of(key)] = key
    out = {c: fm.get(P_CORRUPTION[c]) for c in P_CELLS}
    out.update({c: PS_KEY[c] for c in PS_CELLS})
    return out


def _arm_ev(row: dict, cond: str, arm: str):
    return row.get("conds", {}).get(cond, {}).get("img", {}).get(arm)


def cells_from_m4_rows(rows: list[dict], family) -> tuple[list[dict], dict]:
    """M4 item rows (de-duplicated by idx by the caller) -> (long records, absent). One record per (item, cell) with y_/d_ of clean, none, chg, gm. `absent` maps a cell to the reason it has no
    arms (P cell without an operating point; PS cell not in the rows). An item with no clean condition cannot enter any cell."""
    keys = cell_keys(family)
    recs, absent = [], {}
    for cell in CELLS:
        key = keys[cell]
        if key is None:
            absent[cell] = "no operating point in family.json (p = 1, counted)"
            continue
        if not any(key in r.get("conds", {}) for r in rows):
            absent[cell] = f"condition {key!r} not in the M4 rows (not run)"
            continue
        for r in rows:
            if key not in r.get("conds", {}):
                continue
            ev = {"clean": _arm_ev(r, "clean", "none"), "none": _arm_ev(r, key, "none"), "chg": _arm_ev(r, key, "chg"), "gm": _arm_ev(r, key, A0)}
            rec = dict(cell=cell, key=key, idx=r["idx"])
            for a, e in ev.items():
                rec[f"d_{a}"] = float(e["d"]) if e is not None and e.get("d") is not None else float("nan")
                rec[f"y_{a}"] = float(e["y"]) if e is not None and e.get("y") is not None else float("nan")
            recs.append(rec)
    return recs, absent


# ------------------------------------------------------------------------------------------------ the split and its bootstrap
def split_parts(clean, none, chg, gm) -> dict:
    """T, U, R, V from four arrays of one quantity (d or Y). No filtering here."""
    c, n, g, m = (np.asarray(x, float) for x in (clean, none, chg, gm))
    return dict(T=c - n, U=c - g, R=m - n, V=g - m)


def assert_identity(parts: dict, tol: float = IDENTITY_TOL) -> float:
    """Item by item (or resample by resample): max |T - (U + R + V)| must be <= tol. Returns the maximum; raises IdentityError otherwise."""
    if parts["T"].size == 0:
        return 0.0
    err = float(np.max(np.abs(parts["T"] - (parts["U"] + parts["R"] + parts["V"]))))
    if not err <= tol:
        raise IdentityError(f"E-dec identity T = U + R + V violated: max abs error {err:.3g} > {tol:g}")
    return err


def edec_split(d_clean, d_none, d_chg, d_gm, *, y=None) -> dict:
    """Complete-case split on d, and the same items on Y if `y` = (y_clean, y_none, y_chg, y_gm) is given. Returns the parts, `ok` (complete-case mask), n, n_dropped and the per-arm count of
    non-finite d among the dropped items."""
    d = [np.asarray(x, float) for x in (d_clean, d_none, d_chg, d_gm)]
    fin = [np.isfinite(x) for x in d]
    ok = np.all(fin, axis=0)
    out = dict(ok=ok, n=int(ok.sum()), n_dropped=int((~ok).sum()), n_nonfinite_by_arm={a: int((~f).sum()) for a, f in zip(ARMS, fin)})
    out["d"] = split_parts(*(x[ok] for x in d))
    out["identity_max_abs_error_items"] = assert_identity(out["d"])
    if y is not None:
        yy = [np.asarray(x, float)[ok] for x in y]
        if not all(np.all(np.isfinite(x)) for x in yy):
            raise ValueError("Y is not finite on a complete-case item (Y is stored for every arm; the rows are defective)")
        out["y"] = split_parts(*yy)
        out["identity_max_abs_error_items_y"] = assert_identity(out["y"])
    return out


def _q(boots: np.ndarray, level: float) -> list[float]:
    a = (100 - level) / 2
    return [float(np.quantile(boots, a / 100)), float(np.quantile(boots, 1 - a / 100))]


def _estimate(parts: dict, idx: np.ndarray | None, levels: tuple[float, ...]) -> tuple[dict, bool | None]:
    """Means with percentile intervals; the same `idx` (n_boot x n) for every part keeps the identity in each resample (checked)."""
    n = parts["T"].size
    est = {k: dict(mean=float(v.mean()) if n else float("nan")) for k, v in parts.items()}
    key = lambda lv: "ci95" if lv == 95.0 else "ci9833"
    if idx is None or n < 2:
        for k in parts:
            for lv in levels:
                est[k][key(lv)] = [float("nan")] * 2
        return est, None
    boots = {k: v[idx].mean(axis=1) for k, v in parts.items()}
    ok = bool(np.max(np.abs(boots["T"] - (boots["U"] + boots["R"] + boots["V"]))) <= IDENTITY_TOL)
    if not ok:
        raise IdentityError("E-dec identity violated in a bootstrap resample")
    for k in parts:
        for lv in levels:
            est[k][key(lv)] = _q(boots[k], lv)
    return est, ok


def _shares(est: dict) -> dict | str:
    """Shares U/T, R/T, V/T of the point estimates; only if the lower 95 percent bound of tau_T exceeds 0 (AD.2), else the string 'undefined'. They sum to 1 by the identity."""
    lo = est["T"]["ci95"][0]
    tm = est["T"]["mean"]
    if np.isfinite(lo) and lo > 0 and tm > T_NUMERIC_ZERO:
        return {k: float(est[k]["mean"] / tm) for k in ("U", "R", "V")}
    return "undefined (lower 95 percent bound of tau_T does not exceed 0, or tau_T is numerically zero)"


def edec_cell(cell: str, d_arms, y_arms=None, *, n_boot: int = N_BOOT, seed=None) -> dict:
    """E-dec for one cell. d_arms = (d_clean, d_none, d_chg, d_gm) per item; y_arms the same for Y."""
    sp = edec_split(*d_arms, y=y_arms)
    levels = (95.0, 98.33) if cell in P_CELLS else (95.0,)
    n = sp["n"]
    idx = np.random.default_rng(seed if seed is not None else edec_seed()).integers(0, n, size=(n_boot, n)) if n >= 2 else None
    est_d, ok_d = _estimate(sp["d"], idx, levels)
    res = dict(cell=cell, n_complete=n, n_dropped_incomplete=sp["n_dropped"], n_nonfinite_by_arm=sp["n_nonfinite_by_arm"], names=NAMES,
               d_scale=dict(tau=est_d, shares=_shares(est_d), identity_max_abs_error_items=sp["identity_max_abs_error_items"], identity_in_all_resamples=ok_d,
                            note="d = mean/sd of the per-token evidence, z* = 32 d"))
    if "y" in sp:
        est_y, ok_y = _estimate(sp["y"], idx, levels)
        res["accuracy_scale"] = dict(tau=est_y, shares=_shares(est_y), identity_max_abs_error_items=sp["identity_max_abs_error_items_y"], identity_in_all_resamples=ok_y,
                                     note="A = mean Y on the same complete-case items; tau_T = A_clean - A_none")
    res["interval"] = dict(kind="paired percentile bootstrap over items, items resampled jointly", n_boot=n_boot, levels=list(levels))
    return res


def edec(df_cells, *, n_boot: int = N_BOOT, seed=None, absent: dict | None = None) -> dict:
    """SAP AD.13 `edec(df_cells)`. `df_cells`: a DataFrame or list of dicts, one line per (item, cell), columns cell, idx, d_clean, d_none, d_chg, d_gm and y_clean, y_none, y_chg, y_gm
    (see `cells_from_m4_rows`). Cells of CELLS that have no line are absent and counted (`absent` may carry the reason). Identity assertion and shares rule inside."""
    recs = _records(df_cells)
    by = {}
    for r in recs:
        by.setdefault(r["cell"], []).append(r)
    unknown = sorted(set(by) - set(CELLS))
    if unknown:
        raise ValueError(f"unknown E-dec cell(s) {unknown}; allowed {CELLS}")
    sd = seed if seed is not None else edec_seed()
    cells, gone = {}, dict(absent or {})
    for cell in CELLS:
        lst = sorted(by.get(cell, []), key=lambda r: r["idx"])
        if not lst:
            gone.setdefault(cell, "no arms (cell absent)")
            continue
        idxs = [r["idx"] for r in lst]
        if len(set(idxs)) != len(idxs):
            raise ValueError(f"duplicate item index in cell {cell}")
        d_arms = tuple(np.array([r[f"d_{a}"] for r in lst], float) for a in ARMS)
        y_arms = tuple(np.array([r[f"y_{a}"] for r in lst], float) for a in ARMS) if all(f"y_{a}" in lst[0] for a in ARMS) else None
        cells[cell] = dict(edec_cell(cell, d_arms, y_arms, n_boot=n_boot, seed=sd), n_items_in_cell=len(lst))
    return dict(cells=cells, absent={c: gone.get(c, "no arms (cell absent)") for c in CELLS if c not in cells}, n_cells=len(cells), n_absent=len(CELLS) - len(cells), label=LABEL,
                limits=("U and V are relative to the changed-code label (encoder-instability label, not an evidence oracle). U contains a composition effect: the removed positions carry different "
                        "evidence from the rest. V mixes false alarms, misses, variance trimming and gate shape; V < 0 with a CI excluding 0 voids any detection reading (AB.2). No causal clause."),
                meta=dict(seeds.meta(), seed_name=EDEC_SEED_NAME, seed_spawn_position=EDEC_SEED_POSITION if EDEC_SEED_NAME not in seeds.ANALYSES else seeds.ANALYSES.index(EDEC_SEED_NAME)))


# ------------------------------------------------------------------------------------------------ self-test (AD.13: T = U + R + V on random data)
def selftest(seed: int = 3) -> dict:
    """Synthetic checks: the identity item by item and in every resample on random data, the assertion trips on a broken split, the shares rule, complete-case counting, the 98.33 percent
    interval for P cells only. Cheap; used by the CLI before real data are read."""
    rng = np.random.default_rng(seed)
    n = 120
    d = [rng.normal(m, 0.3, n) for m in (0.5, 0.2, 0.4, 0.35)]
    y = [(rng.random(n) < p).astype(float) for p in (0.85, 0.6, 0.8, 0.75)]
    res = edec_cell("P1", d, y, n_boot=500, seed=11)
    ident_ok = res["d_scale"]["identity_in_all_resamples"] and res["accuracy_scale"]["identity_in_all_resamples"] and res["d_scale"]["identity_max_abs_error_items"] <= IDENTITY_TOL
    sp = split_parts(*d)
    sp["V"] = sp["V"] + 1e-3
    try:
        assert_identity(sp)
        trips = False
    except IdentityError:
        trips = True
    null = edec_cell("PS1", [rng.normal(0.3, 0.3, n)] * 2 + [rng.normal(0.3, 0.3, n)] * 2, None, n_boot=500, seed=11)
    shares_rule = bool(isinstance(res["d_scale"]["shares"], dict) and isinstance(null["d_scale"]["shares"], str))
    dd = [x.copy() for x in d]
    dd[2][:5] = np.nan
    miss = edec_cell("P2", dd, None, n_boot=200, seed=1)
    count_ok = bool(miss["n_complete"] == n - 5 and miss["n_dropped_incomplete"] == 5 and miss["n_nonfinite_by_arm"]["chg"] == 5)
    levels_ok = bool("ci9833" in res["d_scale"]["tau"]["T"] and "ci9833" not in null["d_scale"]["tau"]["T"])
    out = dict(identity_ok=bool(ident_ok), assertion_trips_on_broken_split=trips, shares_rule_ok=shares_rule, complete_case_count_ok=count_ok, ci9833_only_for_P_cells=levels_ok)
    out["all_ok"] = bool(all(out.values()))
    return out


# ------------------------------------------------------------------------------------------------ CLI
def run_edec(run_dir: Path, family, *, n_boot: int = N_BOOT) -> dict:
    from exp_p2.gate import analysis_m4
    rows, n_dup = analysis_m4.load_items(Path(run_dir))
    recs, absent = cells_from_m4_rows(rows, family)
    res = edec(recs, n_boot=n_boot, absent=absent)
    res["n_items"] = len(rows)
    res["n_duplicates_removed"] = n_dup
    return res


def main(argv=None) -> int:
    from exp_p2 import common
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="E-dec on the M4 rows (SAP AD.12 step 5: after family P and PS have been analysed and analysis.json exists)")
    r.add_argument("--run-id", default="P2-GATE-M4")
    r.add_argument("--family-run", default="P2-GATE-M3")
    r.add_argument("--runs-dir", default=str(common.RUNS))
    r.add_argument("--boot", type=int, default=N_BOOT)
    r.add_argument("--out", default=None)
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        st = selftest()
        print(json.dumps(st))
        return 0 if st["all_ok"] else 2
    st = selftest()
    if not st["all_ok"]:
        print("SELFTEST FAILED:", st, file=sys.stderr)
        return 2
    runs = Path(a.runs_dir)
    run_dir = runs / a.run_id
    if not (run_dir / "analysis.json").exists():
        print(f"{run_dir / 'analysis.json'} missing: E-dec follows family P and PS in the order of analysis (SAP AD.12 step 5)", file=sys.stderr)
        return 3
    fam = json.loads((runs / a.family_run / "family.json").read_text(encoding="utf8"))
    res = run_edec(run_dir, fam["family"], n_boot=a.boot)
    meta = json.loads((run_dir / "analysis.json").read_text(encoding="utf8")).get("meta", {})
    res["allow_partial_in_analysis_json"] = meta.get("allow_partial")
    res["selftest"] = st
    out = Path(a.out) if a.out else run_dir / "edec.json"
    out.write_text(json.dumps(res, indent=1, default=float, allow_nan=True), encoding="utf8")
    print(json.dumps(dict(out=str(out), cells=list(res["cells"]), absent=res["absent"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
