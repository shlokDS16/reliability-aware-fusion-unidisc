"""Family H, H3 go/no-go (SAP addendum A5, A5.5 and A5.5a). CPU only; no model, no GPU, no random numbers.

    python -m exp_p2.gate.h3_gonogo plan                                   # before H3: derived H3 folds file and the plan family file (both write-once, to be committed)
    python -m exp_p2.gate.h3_gonogo decide --h3-run P2-GATE-H3 [--now ISO]  # once, after H3: writes runs/P2-GATE-H3/family.json (write-once)

H3 is the 50-item `head` list of runs/P2-HARDNEG-ITEMS/folds_hardneg.json processed by the M4 stage (`run_gate_m4`, run id P2-GATE-H3) under the plan family (M3's three corruptions).
Per corruption c, from the H3 rows only: n_valid_c = items with Y(clean, none), Y(c, none), Y(c, gate0.05) all defined; F-_c = Y(clean, none) = 1 and Y(c, none) = 0; F+_c the reverse
(none arm only); G_c = #(Y(c, gate0.05) != Y(c, none)), unsigned. c is tested in H4 iff n_valid_c >= 45 and (a) F-_c > F+_c with the exact two-sided McNemar p of (6 F-_c, 6 F+_c) <= 0.05/3
and (b) G_c >= 3. H-R1 (rule code R1): G* >= 8; H-R2 (R2): 3 <= G* <= 7; H-NOGO (NO-GO): no corruption is tested. n for H4 is cut by the time rule of A5.12.
The module never forms b, c, the accuracy or any other signed quantity of GATE-M versus none: the gate arm is reduced to the unsigned indicator `yg != yn` at once and not used again."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import analysis_m4, artifacts, config, folds, stats        # noqa: E402

# ---- constants copied from SAP addendum A5 (A5.5, A5.5a, A5.12); none is invented here
N_STAR = 43                  # exact sign-test power 0.8 at theta 0.75 (SAP 4.6)
MIN_G = 3                    # (b) gate discordance of a tested corruption, of 50
R1_G = 8                     # H-R1 iff G* >= 8
SCALE_50_TO_300 = 6
ALPHA_STEP1 = 0.05 / 3       # Holm first step, m = 3
MIN_VALID = 45
H3_GID_RANGE = (6000, 6049)  # gid = 6000 + idx (build_hardneg_items.GID_OFFSET["head"])
IST = timezone(timedelta(hours=5, minutes=30))
FREEZE = datetime(2026, 10, 30, 18, 0, tzinfo=IST)
W_H3, A_H3, W_H4_300, W_H4_200, A_H4, MARGIN_H = 0.75, 0.5, 2.9, 1.8, 0.5, 2.0       # hours (A5.12)
TIME_CONSTANTS = dict(W_H3=W_H3, A_H3=A_H3, W_H4_300=W_H4_300, W_H4_200=W_H4_200, A_H4=A_H4, M=MARGIN_H)
A0 = analysis_m4.A0          # "gate0.05"
H4_FOLD_NAME = "folds_hardneg.json"
H3_FOLD_NAME = "folds_hardneg_h3.json"
HARDNEG_RUN, PLAN_RUN, H3_RUN = "P2-HARDNEG-ITEMS", "P2-GATE-H3-PLAN", "P2-GATE-H3"
SPEC = "SAP addendum A5, A5.5 and A5.5a"


def sha256_lf(path: Path) -> str:
    """SHA-256 with CRLF turned into LF (a checkout with core.autocrlf=true rewrites the committed bytes)."""
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def h3_start_deadline() -> datetime:
    """A5.12 rule 1: H3 starts iff t + W_H3 + A_H3 + W_H4(200) + A_H4 + M <= F, i.e. no later than F minus 5.55 h (Fri 30 Oct 12:27 IST)."""
    return FREEZE - timedelta(hours=W_H3 + A_H3 + W_H4_200 + A_H4 + MARGIN_H)


def code_commit() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def bound_p(f_minus: int, f_plus: int, scale: int = SCALE_50_TO_300) -> float:
    """Exact two-sided McNemar p of (b, c) = (k F-, k F+): the restore-clean power bound scaled from 50 items. The GO rule uses k = 6 (50 to 300 items, as written in A5.5); the
    descriptive bound at the n actually run uses k = n_H4 / 50 (6, or 4 at n = 200; A5.5a, C5-7)."""
    b, c = int(scale) * int(f_minus), int(scale) * int(f_plus)
    ya, yb = np.array([1] * b + [0] * c, float), np.array([0] * b + [1] * c, float)
    return float(stats.mcnemar_exact(ya, yb)["p"])


def n_after_time_rule(n_by_rule: int, now: datetime) -> tuple[int, str]:
    """A5.12 rule 2: 300 iff now + 2.9 + 0.5 + 2.0 h <= F; else 200 iff now + 1.8 + 0.5 + 2.0 h <= F; else 0. Only applies when the H3 rule allows H4 (n_by_rule > 0)."""
    if n_by_rule <= 0:
        return 0, "not tested (NO-GO)"
    if now + timedelta(hours=W_H4_300 + A_H4 + MARGIN_H) <= FREEZE:
        return 300, "ok"
    if now + timedelta(hours=W_H4_200 + A_H4 + MARGIN_H) <= FREEZE:
        return 200, "n=200 by time"
    return 0, "cut by time"


def parse_now(text: str | None) -> datetime:
    if not text:
        return datetime.now(IST)
    d = datetime.fromisoformat(text)
    return d.replace(tzinfo=IST) if d.tzinfo is None else d.astimezone(IST)


def evaluate(rows: list[dict], plan_family: list[dict]) -> dict:
    """Per corruption of the plan family: the unsigned H3 quantities and the tested flag (A5.5). `yg` is reduced to the unsigned indicator at once."""
    yc = analysis_m4._arm(rows, "clean", "none", "y")
    out = {}
    for f in plan_family:
        k, corr = f["key"], f["corruption"]
        yn = analysis_m4._arm(rows, k, "none", "y")
        yg = analysis_m4._arm(rows, k, A0, "y")
        ych = analysis_m4._arm(rows, k, "chg", "y")
        valid = np.isfinite(yc) & np.isfinite(yn) & np.isfinite(yg)
        disc = (yg != yn)[valid]                                             # the only use of yg: unsigned
        del yg
        n_valid = int(valid.sum())
        c1, n1 = yc[valid] > 0.5, yn[valid] > 0.5
        f_minus, f_plus = int((c1 & ~n1).sum()), int((~c1 & n1).sum())
        p = bound_p(f_minus, f_plus)
        headroom = bool(f_minus > f_plus and p <= ALPHA_STEP1)
        g = int(disc.sum())
        both = valid & np.isfinite(ych)
        chg_disc = int((ych[both] != yn[both]).sum())
        tested = bool(n_valid >= MIN_VALID and headroom and g >= MIN_G)
        why = []
        if n_valid < MIN_VALID:
            why.append(f"n_valid {n_valid} < {MIN_VALID}")
        if not headroom:
            why.append(f"no decision headroom (F- {f_minus}, F+ {f_plus}, bound p {p:.4g} > {ALPHA_STEP1:.5f} or F- <= F+)")
        if g < MIN_G:
            why.append(f"G {g} < {MIN_G}")
        out[corr] = dict(key=k, n_valid=n_valid, F_minus=f_minus, F_plus=f_plus, bound_b=SCALE_50_TO_300 * f_minus, bound_c=SCALE_50_TO_300 * f_plus, bound_p=p, headroom=headroom,
                         G=g, chg_discordance=chg_disc, tested=tested, reason="tested" if tested else "; ".join(why))
    return out


def rule_from(per: dict) -> tuple[str, str, int | None, list[str]]:
    """-> (rule code, h_rule, G*, tested corruptions in config.REALISTIC order)."""
    plus = [c for c in config.REALISTIC if c in per and per[c]["tested"]]
    if not plus:
        return "NO-GO", "H-NOGO", None, plus
    g_star = max(per[c]["G"] for c in plus)
    return ("R1", "H-R1", g_star, plus) if g_star >= R1_G else ("R2", "H-R2", g_star, plus)


def wilson_clean(rows: list[dict]) -> dict:
    yc = analysis_m4._arm(rows, "clean", "none", "y")
    ok = np.isfinite(yc)
    k, n = int((yc[ok] > 0.5).sum()), int(ok.sum())
    return dict(k=k, n=n, wilson95=list(stats.wilson_ci(k, n, 0.95)) if n else [float("nan")] * 2)


def g_max_headroom(per: dict) -> int | None:
    """A5.5a (C5-7): the largest G_c over corruptions with n_valid_c >= 45 that pass (a) (decision headroom); None if there is none. Used only by the H-NOGO sentence."""
    gs = [v["G"] for v in per.values() if v["n_valid"] >= MIN_VALID and v["headroom"]]
    return max(gs) if gs else None


def build_family_doc(rows: list[dict], plan: dict, now: datetime, inputs: dict, decide_record: dict | None = None) -> tuple[dict, bool]:
    """-> (family.json content, pilot_complete). Pilot incomplete = no corruption has n_valid >= 45 (rows missing or an H3 prefix that is too short): NO-GO, test_fold 0, status
    'not run (pilot incomplete)' (A5.5a: exit 2)."""
    per = evaluate(rows, plan["family"])
    complete = any(v["n_valid"] >= MIN_VALID for v in per.values())
    rule, h_rule, g_star, plus = rule_from(per) if complete else ("NO-GO", "H-NOGO", None, [])
    n_by_rule = 300 if rule in ("R1", "R2") else 0
    n_after, status = n_after_time_rule(n_by_rule, now)
    if not complete:
        status = "not run (pilot incomplete)"
    k = n_after // 50 if n_after > 0 else None                                 # descriptive only (C5-7): 6 at n = 300, 4 at n = 200, none when H4 is not run
    for v in per.values():
        v["bound_p_at_n"] = bound_p(v["F_minus"], v["F_plus"], k) if k else None
        v["projection_at_n"] = v["G"] * k if k else None
    by_corr = {f["corruption"]: f for f in plan["family"]}
    family = [dict(corruption=c, severity=by_corr[c]["severity"], key=by_corr[c]["key"], G_c=per[c]["G"], F_minus=per[c]["F_minus"], F_plus=per[c]["F_plus"]) for c in plus]
    excluded = [dict(corruption=c, reason=per[c]["reason"]) for c in config.REALISTIC if c in per and c not in plus]
    go = bool(plus and n_after > 0)
    doc = dict(endpoint="d", endpoint_note="H endpoint is Y; 'd' only satisfies run_gate_m4/analysis_m4 (S-Z secondary)", n_headroom_items=len(rows), family=family, excluded=excluded,
               n_rule=dict(rule=rule, h_rule=h_rule, test_fold=n_after, G_star=g_star, G_max_headroom=(g_max_headroom(per) if complete else None), N_star=N_STAR, min_G=MIN_G, r1_G=R1_G, scale_50_to_300=SCALE_50_TO_300, alpha_step1=0.016667,
                           min_valid=MIN_VALID, primary_endpoint="Y", primary_endpoint_code="Y", negative_reading_available=bool(n_after >= 240 and rule in ("R1", "R2")),
                           time_rule=dict(now=now.isoformat(), freeze=FREEZE.isoformat(), constants=dict(TIME_CONSTANTS), n_by_rule=n_by_rule, n_after_time=n_after, status=status)),
               go=go, downstream_claim_withdrawn=not go, per_corruption=per, clean_none_accuracy=wilson_clean(rows), inputs=inputs, spec=SPEC)
    if decide_record is not None:
        doc["decide_record"] = decide_record
    return doc, complete


# ------------------------------------------------------------------------------------------------ plan
def paths(runs: Path | None = None) -> dict[str, Path]:
    r = Path(runs) if runs is not None else Path(common.RUNS)
    return dict(m3=r / "P2-GATE-M3" / "family.json", h4_folds=r / HARDNEG_RUN / H4_FOLD_NAME, h3_folds=r / HARDNEG_RUN / H3_FOLD_NAME, plan=r / PLAN_RUN / "family.json")


def plan(runs: Path | None = None) -> dict:
    """Writes the derived H3 folds file and the plan family file. Raises FileNotFoundError / ValueError / artifacts.WriteOnceError; refuses to overwrite either file (checked before writing)."""
    p = paths(runs)
    for k in ("m3", "h4_folds"):
        if not p[k].exists():
            raise FileNotFoundError(f"{p[k]} missing")
    for k in ("h3_folds", "plan"):
        if p[k].exists():
            raise artifacts.WriteOnceError(f"{p[k]} already exists; it is write-once and committed")
    m3 = json.loads(p["m3"].read_text(encoding="utf8"))
    if m3.get("endpoint") != "d":
        raise ValueError(f"{p['m3']} does not record endpoint d")
    fam = [dict(corruption=f["corruption"], severity=f["severity"], key=f["key"]) for f in m3["family"]]
    if [f["corruption"] for f in fam] != list(config.REALISTIC):
        raise ValueError(f"M3 family {[f['corruption'] for f in fam]} is not the three corruptions {list(config.REALISTIC)} in order; the plan family is M3's three")
    hard = json.loads(p["h4_folds"].read_text(encoding="utf8"))
    head = hard["head"]
    if len(head) != 50 or [it["idx"] for it in head] != list(range(50)) or not all(H3_GID_RANGE[0] <= it["gid"] <= H3_GID_RANGE[1] for it in head):
        raise ValueError("folds_hardneg.json 'head' is not the 50 H3 items (idx 0-49, gid 6000-6049)")
    folds.save_folds(dict(cal=[], head=[], test=head, test_ext=[]), p["h3_folds"])
    doc = dict(endpoint="d", endpoint_note=m3.get("endpoint_note"), family=fam, excluded=[], n_rule=dict(rule="H3-pilot", test_fold=50, primary_endpoint="Y"), go=True, spec=SPEC,
               source=dict(m3_family_sha256=sha256_lf(p["m3"]), folds_hardneg_sha256=sha256_lf(p["h4_folds"])))
    p["plan"].parent.mkdir(parents=True, exist_ok=True)
    artifacts.write_once(p["plan"], json.dumps(doc, indent=1))
    return dict(h3_folds=str(p["h3_folds"]), plan_family=str(p["plan"]), h3_start_deadline=h3_start_deadline().isoformat())


# ------------------------------------------------------------------------------------------------ decide
def decide_deadline() -> datetime:
    """A5.5a (C5-7): if H3 has not completed by this time, `decide` is run then on the completed prefix: the rule-1 start bound (12:27) plus W_H3 = Fri 30 Oct 2026 13:12 IST."""
    return h3_start_deadline() + timedelta(hours=W_H3)


def last_row_time(items_path: Path) -> datetime | None:
    """Time of the last H3 row = the modification time of items.jsonl (the file is appended row by row; no row content is read for this)."""
    try:
        return datetime.fromtimestamp(Path(items_path).stat().st_mtime, IST)
    except OSError:
        return None


def decide(h3_run: str = H3_RUN, now: datetime | None = None, runs: Path | None = None, *, last_row: datetime | None = None, gap_reason: str | None = None) -> tuple[int, dict]:
    """-> (exit code, family.json content). 0 written; 2 pilot incomplete (file still written, NO-GO). Raises artifacts.WriteOnceError if the file exists.
    The clock, the last H3 row's time, the gap, the A5.5a deadline and `gap_reason` are recorded in `decide_record` (a gap above A_H3 = 0.5 h is logged with its reason)."""
    now = now or datetime.now(IST)
    p = paths(runs)
    r = Path(runs) if runs is not None else Path(common.RUNS)
    run_dir = r / h3_run
    out = run_dir / "family.json"
    if out.exists():
        raise artifacts.WriteOnceError(f"{out} already exists; it is write-once")
    plan_doc = json.loads(p["plan"].read_text(encoding="utf8"))
    hard = json.loads(p["h4_folds"].read_text(encoding="utf8"))
    head_ids = {int(it["image_id"]) for it in hard["head"]}
    rows, _ = analysis_m4.load_items(run_dir)
    for row in rows:
        if not (H3_GID_RANGE[0] <= int(row["gid"]) <= H3_GID_RANGE[1]) or int(row["image_id"]) not in head_ids:
            raise ValueError(f"row idx {row.get('idx')} (gid {row.get('gid')}, image {row.get('image_id')}) is not an H3 item of folds_hardneg.json")
    items_path = run_dir / "items.jsonl"
    inputs = dict(h3_run=h3_run, items_sha256=sha256_lf(items_path) if items_path.exists() else None, plan_family_sha256=sha256_lf(p["plan"]), folds_h3_sha256=sha256_lf(p["h3_folds"]), code_commit=code_commit())
    lr = last_row if last_row is not None else last_row_time(items_path)
    gap_h = (now - lr).total_seconds() / 3600.0 if lr is not None else None
    record = dict(now=now.isoformat(), last_h3_row_time=lr.isoformat() if lr is not None else None, gap_hours=gap_h, gap_over_A_H3=bool(gap_h is not None and gap_h > A_H3),
                  gap_reason=gap_reason, h3_rows=len(rows), h3_complete=bool(len(rows) >= 50), deadline=decide_deadline().isoformat(), after_deadline=bool(now > decide_deadline()),
                  decided_on_prefix=bool(len(rows) < 50))
    doc, complete = build_family_doc(rows, plan_doc, now, inputs, record)
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts.write_once(out, json.dumps(doc, indent=1))
    return (0 if complete else 2), doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    d = sub.add_parser("decide")
    d.add_argument("--h3-run", default=H3_RUN)
    d.add_argument("--now", default=None, help="ISO 8601 (naive = IST); for tests only, otherwise the system clock in IST is used and recorded")
    d.add_argument("--last-row-time", default=None, help="ISO 8601 (naive = IST); default: the modification time of items.jsonl")
    d.add_argument("--gap-reason", default=None, help="why `decide` ran more than 0.5 h after the last H3 row (logged in decide_record)")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "plan":
            res = plan()
            print(json.dumps(res, indent=1))
            return 0
        code, doc = decide(a.h3_run, parse_now(a.now), last_row=parse_now(a.last_row_time) if a.last_row_time else None, gap_reason=a.gap_reason)
    except (FileNotFoundError, ValueError, artifacts.WriteOnceError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    nr = doc["n_rule"]
    rec = doc["decide_record"]
    if rec["gap_over_A_H3"] and not rec["gap_reason"]:
        print("NOTE: decide ran more than 0.5 h after the last H3 row; record the reason (--gap-reason)", file=sys.stderr)
    print(json.dumps(dict(rule=nr["rule"], h_rule=nr["h_rule"], test_fold=nr["test_fold"], G_star=nr["G_star"], tested=[f["corruption"] for f in doc["family"]], status=nr["time_rule"]["status"]), indent=1))
    return code


if __name__ == "__main__":
    sys.exit(main())
