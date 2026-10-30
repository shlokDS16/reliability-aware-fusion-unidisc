"""Main-text table "Families at a glance" (column width): two separate blocks, Study 1 and Study 2; family, what it tests in plain words,
and its STATUS only (D0102, amends D0096; red-team re-check R1). The status vocabulary is that of the supplement status map
(SAP A4.2.5 item 6): "run, formal", "not run (gatekept)", "headroom not met; H4 not run". No outcome word appears anywhere (no
"bounded null", "confirmed", "rejected", "not rejected", "shown"), no number, no interval and no cross-study row; outcomes are in each
study's Results. Every status is checked against the run file that carries it (assertions), so a changed run changes the build.
Sources: runs/P2-GATE-M4/analysis.json, runs/P2-GATE-M1/analysis.json, runs/P2-GATE-S2/analysis.json, runs/P2-GATE-FOIL/analysis.json,
runs/P2-GATE-H3/family.json, runs/P2-LRF-L1/a6_analysis.json, runs/P2-LRF-LG/a6_analysis.json.
Output: paper2-tnnls/tables/tab_families_glance.tex"""
from __future__ import annotations

import figstyle as S
from tablib import row, write

M4 = S.jload("P2-GATE-M4/analysis.json")
S2 = S.jload("P2-GATE-S2/analysis.json")
FB = S.jload("P2-GATE-FOIL/analysis.json")
H3 = S.jload("P2-GATE-H3/family.json")
L1 = S.jload("P2-LRF-L1/a6_analysis.json")
LG = S.jload("P2-LRF-LG/a6_analysis.json")
FL, FG = L1["family_L"], LG["family_LG"]["cells"]
assert FL == LG["family_L"]
MP = "runs/P2-GATE-M4/analysis.json"
RUN, GATED, H_STATUS = "run, formal", "not run (gatekept)", "headroom not met; H4 not run"

# ---- Study 1 statuses (checked against the run files; same rules as scripts/tab_status_map.py) ------------------------------------
assert M4["completeness"]["completed_n"] == 500                                         # P: run, formal
assert M4["s_c"]["n"] == 500 and M4["ps"]["holm_m"] == 2                               # S-C, PS: run, formal
assert all(v["tested"] for v in M4["s_d2"]["per_corruption"].values())                 # S-D2: run, formal
assert not any(v["tested"] for v in M4["s_m"]["per_corruption"].values())              # S-M: gatekept, not run
assert M4["primary"]["claim_survives"] is False
assert S2["completeness"]["completed_n"] == S2["completeness"]["planned_n"] and all(v["tested"] for v in S2["per_cell"].values())
assert FB["status"] == "tested" and FB["partial"] is False                             # B: run, formal
assert H3["go"] is False and H3["n_rule"]["h_rule"] == "H-NOGO"                        # H: headroom not met; H4 not run
assert not (S.RUNS / "P2-GATE-H4").exists()
S1 = [
    ("P", "GATE-M against no gate under JPEG, noise and splice", RUN, f"{MP} completeness.completed_n (= 500)"),
    ("S-C", "GATE-M against no gate on clean images", RUN, f"{MP} s_c.n"),
    ("PS", "pipeline check on patch and swap corruptions", RUN, f"{MP} ps.holm_m"),
    ("S-D, S-D2", "detection of changed tokens against cheap scores (detection and test items)", RUN,
     f"runs/P2-GATE-M1/analysis.json n_items; {MP} s_d2.per_corruption.*.tested"),
    ("S-M", "GATE-M against the geometry-matched random gate", GATED, f"{MP} s_m.per_corruption.*.tested (all false)"),
    ("S2", "re-infill of flagged tokens against random re-infill", RUN, "runs/P2-GATE-S2/analysis.json completeness, per_cell.*.tested"),
    ("B", "combination of both directions against the better single one (one-word foil pairs)", RUN,
     "runs/P2-GATE-FOIL/analysis.json status, partial"),
    ("H", "GATE-M against no gate on hard-negative pairs", H_STATUS, "runs/P2-GATE-H3/family.json go (= false), n_rule.h_rule; no runs/P2-GATE-H4"),
]
# ---- Study 2 statuses ---------------------------------------------------------------------------------------------------------------
for k in ("L1", "L3", "L4", "L-NI", "L-LEN"):
    assert FL[k]["n"] > 0, k                                                              # each test was run on the fresh fold
assert all(v["n"] == 300 for v in FG.values())
LP = "runs/P2-LRF-L1/a6_analysis.json"
LGP = "runs/P2-LRF-LG/a6_analysis.json"
S2R = [
    ("L1", "learned weights against the unweighted sum, Gaussian noise 0.1 (primary)", RUN, f"{LP} family_L.L1.n"),
    ("L3", "the same under JPEG quality 10", RUN, f"{LP} family_L.L3.n"),
    ("L4", "the same under a 128 px splice", RUN, f"{LP} family_L.L4.n"),
    ("L-NI", "clean images against the non-inferiority margin", RUN, f"{LP} family_L.L-NI.n"),
    ("L-LEN", "L1 with length-matched wrong captions", RUN, f"{LP} family_L.L-LEN.n"),
    ("LG", "the same under shot, impulse and speckle noise, severity 3 (three cells)", RUN, f"{LGP} family_LG.cells.*.n (= 300)"),
]
r1 = [row([f, w, d], [src]) for f, w, d, src in S1]
r2 = [row([f, w, d], [src]) for f, w, d, src in S2R]
mc = lambda t: r"\multicolumn{3}{@{}l}{\textit{" + t + "}}"
write("tab_families_glance.tex", "@{}lp{0.46\\columnwidth}l@{}", ["Family", "What it tests", "Status"],
      [[row([mc("Study 1")], ["block heading"])] + r1, [row([mc("Study 2")], ["block heading"])] + r2],
      preamble=["Status only (D0102): the status-map vocabulary, no outcome word, no number. Two separate blocks; no cross-study row.",
                "Outcomes are in each study's Results."],
      script="tab_glance.py")
