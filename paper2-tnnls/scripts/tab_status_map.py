"""Study 1 family STATUS map (SAP A4.2.5 item 6): one row per family in AD.11 order (then A5.13 for H, H-M), status text only, no estimate, no interval.
Statuses use the A4.2.5 vocabulary; every status is checked against the run file that carries it (assertions), so a changed run changes the build.
Order: research/paper2/prereg/SAP-GATE-2026-10-28.md AD.11 (P, S-M, S-Z, S-DN, S-D, S-D2, S-C, PS, S2, B, R, E, E-dec, suite and Tier 3) with E-pred beside E-dec
(AD.3) and H, H-M from SAP-ADDENDUM-A5 A5.13. Output: paper2-tnnls/tables/supp_status_map_study1.tex (replaces supp_study1_families.tex)."""
from __future__ import annotations

import pathlib

import figstyle as S
from tablib import row, write

M4 = S.jload("P2-GATE-M4/analysis.json")
S2 = S.jload("P2-GATE-S2/analysis.json")
FB = S.jload("P2-GATE-FOIL/analysis.json")
H3 = S.jload("P2-GATE-H3/family.json")
SU = S.jload("P2-GATE-SUITE/analysis.json")
EP = S.jload("P2-GATE-M4/epred_score.json")
ED = S.jload("P2-GATE-M4/edec.json")
MP = "runs/P2-GATE-M4/analysis.json"

# ---- checks that tie each status to its run file ----------------------------------------------------------------------------------
gated_empty = (M4["primary"]["claim_survives"] is False) and not any(v["tested"] for v in M4["s_m"]["per_corruption"].values())
assert gated_empty
assert all(v["tested"] for v in M4["s_z"]["per_corruption"].values()) and all(v["tested"] for v in M4["s_dn"]["per_corruption"].values())
assert all(v["tested"] for v in M4["s_d2"]["per_corruption"].values()) and M4["s_c"]["n"] == 500 and M4["ps"]["holm_m"] == 2
assert S2["completeness"]["completed_n"] == S2["completeness"]["planned_n"] >= S2["n_min"] and all(v["tested"] for v in S2["per_cell"].values())
assert FB["status"] == "tested" and FB["partial"] is False
assert not list(pathlib.Path(S.RUNS).glob("P2-GATE-OMNI*")) and not (S.RUNS / "P2-GATE-H4").exists()          # R and H4 have no run directory
assert H3["go"] is False and H3["n_rule"]["h_rule"] == "H-NOGO"
assert EP["formal_test"] is None and ED["n_cells"] >= 1

ROWS = [
    ("P", "GATE-M against no gate: JPEG, noise, splice", "run, formal", [f"{MP} primary.holm_m, completeness.completed_n"]),
    ("S-M", "GATE-M against the geometry-matched random gate", "not run (gatekept: P+ empty)", [f"{MP} s_m.per_corruption.*.tested (all false), primary.claim_survives (= false)"]),
    ("S-Z", "size-scaled evidence ratio, secondary endpoint", "run, formal", [f"{MP} s_z.per_corruption.*.tested"]),
    ("S-DN", "GATE-M against the denoised copy: JPEG, noise", "run, formal", [f"{MP} s_dn.per_corruption.*, holm_m"]),
    ("S-D", "detection of changed tokens against cheap scores (detection items)", "run, formal", ["runs/P2-GATE-M1/analysis.json label, n_items"]),
    ("S-D2", "the same contrast on the test items: JPEG, noise", "run, formal", [f"{MP} s_d2.per_corruption.*.tested"]),
    ("S-C", "GATE-M against no gate on clean images", "run, formal", [f"{MP} s_c.n, holm_m"]),
    ("PS", "positive control: patch, swap", "run, formal", [f"{MP} ps.holm_m, ps.positive_control"]),
    ("S2", "re-infill of the flagged set against random-gate best-of-4 re-infill", "run, formal", ["runs/P2-GATE-S2/analysis.json completeness.{completed_n,planned_n}, n_min, per_cell.*.tested"]),
    ("B", "one-word foil pairs: combination of both directions against the better single one", "run, formal", ["runs/P2-GATE-FOIL/analysis.json status, partial, n_test_completed"]),
    ("R", "GATE-M against no gate on the second backbone", "not run (gatekept: P+ empty)", [f"{MP} primary.claim_survives (= false); no runs/P2-GATE-OMNI* directory"]),
    ("E", "sign agreement of the withholding theory", "withdrawn (AB.3)", ["runs/P2-GATE-M4/epred_score.json formal_test (= null), formal_test_note"]),
    ("E-pred", "out-of-sample sign agreement, five cells", "run, descriptive", ["runs/P2-GATE-M4/epred_score.json cells, formal_test (= null)"]),
    ("E-dec", "three-part split of the accuracy lost to corruption", "run, descriptive", ["runs/P2-GATE-M4/edec.json n_cells, label"]),
    ("Suite, Tier 3", "other corruptions and detector-free combiners", "run, exploratory", ["runs/P2-GATE-SUITE/analysis.json; runs/P2-GATE-M4/tier3_fusion.json label"]),
    ("H", "GATE-M against no gate on hard-negative pairs", "headroom not met (H-NOGO); H4 not run", ["runs/P2-GATE-H3/family.json go (= false), n_rule.h_rule (= H-NOGO); no runs/P2-GATE-H4 directory"]),
    ("H-M", "GATE-M against the geometry-matched gate on the H corruptions", "not run (gatekept: H empty)", ["runs/P2-GATE-H3/family.json family (= [])"]),
]
assert H3["family"] == []
rows = [row([f, c, st], rr) for f, c, st, rr in ROWS]
write("supp_status_map_study1.tex", "@{}llp{0.30\\linewidth}@{}", ["Family", "Contrast", "Status"], [rows],
      preamble=["Study 1 family status map (A4.2.5 item 6): status only; no estimate and no interval anywhere in this table.",
                "A status other than 'run, formal' may be hatched or set in grey by the writer; the text is binding."], script="tab_status_map.py")
