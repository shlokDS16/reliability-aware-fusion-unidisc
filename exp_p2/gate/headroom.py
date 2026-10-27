"""Headroom check (v2 section 7.3, Alg. 9) with the SAP's numeric rule (SAP section 5) and sample-size rule (SAP 4.6), as amended by Addendum 1. CPU only.

    python -m exp_p2.gate.headroom --run-id P2-GATE-M3 [--endpoint d]          # d is the default; family.json records "endpoint": "d"

Endpoint (Addendum 1 A1.1): the size-normalised evidence d = mean/sd, reported as z* = sqrt(m) * d = 32 d for m = 1024. For arms that use all tokens z* equals z; the changed-code gate
uses fewer tokens, and z (which carries sqrt(|R|)) would charge it a cost that the primary endpoint Y already pays. The decision uses d only; the z-based verdict is logged per rung as a
sensitivity row and never changes the family.
Rung passes iff n_v >= 90 and T1 >= 2.0 and T2 >= 2.0 (SAP 5), with u_i = e_clean - e_cor, v_i = e_chg - e_cor over the n_v items whose three endpoint values are finite and
T = mean / (sd / sqrt(n_v)). The ladder is walked in order (JPEG 10, 5; noise 0.10, 0.20; splice 128, 192); the first passing rung is the operating point. GATE's flags are never read
(asserted). Sample-size rule (SAP 4.6): D_c = number of items whose Y differs between the changed-code gate and none (either direction), D* = max over corruptions with an operating point,
N* = 43 (exact sign-test power 0.8, theta 0.75, Holm step 1), kappa = 0.5:
  R1 if kappa * 3 * D* >= N*  -> test fold 300, primary endpoint Y;   R2 else if kappa * 5 * D* >= N* -> test fold 500, endpoint Y;
  R3 else -> test fold 300 and the primary endpoint becomes the paired evidence change (d, Wilcoxon); no operating point at all -> NO-GO.
family.json must be committed before the first M4 item is scored."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import artifacts, config, corruptions, stats                          # noqa: E402

N_STAR, KAPPA, MIN_NV, T_MIN = 43, 0.5, 90, 2.0      # SAP 4.6 and 5 (design, fixed)
SCALE_BASE, SCALE_EXT = 300, 500
Z_SCALE_NOTE = "z* = sqrt(m) * d"


def assert_blind(rows: list[dict]) -> None:
    """The headroom analysis must not read any gate-flag field (SAP 5): fail loudly if a row carries one."""
    bad = [k for r in rows for k in list(r) + [kk for rg in r.get("rungs", {}).values() for kk in rg] if ("gate" in k.lower() or "flag" in k.lower())]
    assert not bad, f"M3 rows must not contain gate fields: {sorted(set(bad))}"


def _col(rows, getter):
    return np.array([getter(r) for r in rows], float)


def paired_t(a: np.ndarray, b: np.ndarray, items_ok: np.ndarray) -> dict:
    d = (a - b)[items_ok]
    n = int(d.size)
    if n < 2:
        return dict(n=n, mean=float(d.mean()) if n else float("nan"), sd=float("nan"), t=float("nan"))
    sd = float(d.std(ddof=1))
    return dict(n=n, mean=float(d.mean()), sd=sd, t=float(d.mean() / (sd / np.sqrt(n))) if sd > 0 else float("nan"))


def evaluate_rung(rows: list[dict], key: str, endpoint: str = "d") -> dict:
    clean = _col(rows, lambda r: r["clean"][endpoint])
    none = _col(rows, lambda r: r["rungs"][key]["none"][endpoint])
    chg = _col(rows, lambda r: r["rungs"][key]["chg"][endpoint])
    ok = np.isfinite(clean) & np.isfinite(none) & np.isfinite(chg)
    n_v = int(ok.sum())
    h1, h2 = paired_t(clean, none, ok), paired_t(chg, none, ok)
    p1 = bool(n_v >= MIN_NV and h1["t"] >= T_MIN)
    p2 = bool(n_v >= MIN_NV and h2["t"] >= T_MIN)
    y_none = _col(rows, lambda r: r["rungs"][key]["none"]["y"])
    y_chg = _col(rows, lambda r: r["rungs"][key]["chg"]["y"])
    y_clean = _col(rows, lambda r: r["clean"]["y"])
    mc = stats.mcnemar_exact(y_chg, y_none)
    scale = float(np.sqrt(np.nanmedian(_col(rows, lambda r: r["clean"]["n"])))) if endpoint == "d" else 1.0
    return dict(key=key, endpoint=endpoint, n_v=n_v, n_missing=len(rows) - n_v, H1=h1, H2=h2, T1=h1["t"], T2=h2["t"], H1_pass=p1, H2_pass=p2, passes=bool(p1 and p2),
                z_star_scale=scale, mean_drop_z_star=h1["mean"] * scale, mean_gain_z_star=h2["mean"] * scale,
                discordance_chg_vs_none=dict(mc, D_c=mc["n_discordant"]), acc_drop_binary=float(np.nanmean(y_clean) - np.nanmean(y_none)),
                mean_n_changed=float(np.mean(_col(rows, lambda r: r["rungs"][key]["n_changed"]))))


def sample_size_rule(D_star: int | None, n_headroom: int, kappa: float = KAPPA, n_star: int = N_STAR) -> dict:
    """SAP 4.6 R1/R2/R3. Counts scale from the headroom fold to 300 and 500 test items."""
    if D_star is None:
        return dict(rule="NO-GO", test_fold=300, primary_endpoint="none (downstream claim withdrawn)", D_star=None, N_star=n_star, kappa=kappa)
    s3, s5 = SCALE_BASE / n_headroom, SCALE_EXT / n_headroom
    base = dict(D_star=D_star, N_star=n_star, kappa=kappa, expected_discordant_300=kappa * s3 * D_star, expected_discordant_500=kappa * s5 * D_star)
    if kappa * s3 * D_star >= n_star:
        return dict(base, rule="R1", test_fold=300, primary_endpoint="Y")
    if kappa * s5 * D_star >= n_star:
        return dict(base, rule="R2", test_fold=500, primary_endpoint="Y")
    return dict(base, rule="R3", test_fold=300, primary_endpoint="paired evidence change d (z*), Wilcoxon; Y becomes secondary")


def decide(rows: list[dict], endpoint: str = "d") -> dict:
    """family.json content. `rows` are M3 item rows."""
    assert_blind(rows)
    sens = "z" if endpoint == "d" else "d"
    family, excluded, rungs, sensitivity = [], [], {}, {}
    for corr in config.REALISTIC:
        chosen = None
        for sev in config.LADDERS[corr]:
            key = corruptions.corruption_key(corr, sev)
            ev = evaluate_rung(rows, key, endpoint)
            rungs[key] = ev
            sensitivity[key] = {k: v for k, v in evaluate_rung(rows, key, sens).items() if k in ("endpoint", "n_v", "T1", "T2", "H1_pass", "H2_pass", "passes")}
            if ev["passes"] and chosen is None:
                chosen = (sev, ev)
        if chosen:
            family.append(dict(corruption=corr, severity=chosen[0], key=corruptions.corruption_key(corr, chosen[0]), D_c=chosen[1]["discordance_chg_vs_none"]["D_c"]))
        else:
            excluded.append(dict(corruption=corr, reason="no rung passed n_v >= 90, T1 >= 2 and T2 >= 2", rungs=[corruptions.corruption_key(corr, s) for s in config.LADDERS[corr]]))
    D_star = max((f["D_c"] for f in family), default=None)
    rule = sample_size_rule(D_star, len(rows))
    return dict(endpoint=endpoint, endpoint_note=Z_SCALE_NOTE, n_headroom_items=len(rows), family=family, excluded=excluded, rungs=rungs,
                sensitivity_other_endpoint={sens: sensitivity}, n_rule=rule, go=bool(family), downstream_claim_withdrawn=not family,
                spec="SAP-GATE-2026-10-28 sections 4.6, 5 and Addendum 1 A1.1; spec v2 Alg. 9")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-GATE-M3")
    ap.add_argument("--endpoint", choices=["d", "z"], default="d", help="d is the SAP endpoint (Addendum 1); z is a sensitivity analysis only")
    ap.add_argument("--out", default="family.json")
    ap.add_argument("--min-items", type=int, default=config.N_HEAD)
    ap.add_argument("--force", action="store_true", help="overwrite an existing family.json (it is write-once; the old file is kept and an amendment is logged)")
    a = ap.parse_args(argv)
    run = Path(common.RUNS) / a.run_id
    rows = common.read_jsonl(run / "items.jsonl")
    if len(rows) < a.min_items:
        print(f"only {len(rows)} headroom items in {run}; the rule needs the full {a.min_items}", file=sys.stderr)
        return 2
    res = decide(rows, a.endpoint)
    try:
        artifacts.write_once(run / a.out, json.dumps(res, indent=1), a.force)
    except artifacts.WriteOnceError as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    print(json.dumps(dict(endpoint=res["endpoint"], family=[f["key"] for f in res["family"]], excluded=[e["corruption"] for e in res["excluded"]], n_rule=res["n_rule"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
