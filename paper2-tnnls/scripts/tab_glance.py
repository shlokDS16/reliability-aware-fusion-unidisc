"""Main-text table "Families at a glance" (column width): two blocks, Study 1 and Study 2; family, what it tests in plain words, the preregistered decision
word only. No result number, no interval, no cross-study row. The decision word of every row is derived from its run file by an explicit rule (asserted):
Study 1: P 'bounded null' (outcome.label negative); PS/S-C/S2/B 'not rejected'; S-D 'rejected (Holm)' for both corruptions; S-M, H 'not run'.
Study 2: L1 'confirmed' (label); L3 'not rejected'; L4, LG cells 'rejected (Holm)'; L-NI 'shown' (label); L-LEN 'rejected'.
Sources: runs/P2-GATE-M4/analysis.json, runs/P2-GATE-S2/analysis.json, runs/P2-GATE-FOIL/analysis.json, runs/P2-GATE-H3/family.json,
runs/P2-LRF-L1/a6_analysis.json, runs/P2-LRF-LG/a6_analysis.json. Output: paper2-tnnls/tables/tab_families_glance.tex"""
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


def holm_rejects(d):                                    # S-D2 rows: Holm-adjusted p below the preregistered 0.05
    return all(v["p_holm"] < 0.05 for v in d.values())


# ---- Study 1 decision words (rules asserted) ---------------------------------------------------------------------------------------
assert M4["outcome"]["label"] == "negative"
assert not any(v["p_holm"] < 0.05 for v in M4["ps"]["per_corruption"].values())
assert M4["s_c"]["p_holm"] >= 0.05
assert holm_rejects(M4["s_d2"]["per_corruption"])
assert not any(v["p_holm"] < 0.05 for v in S2["per_cell"].values())
assert FB["test"]["p"] >= 0.05
assert not any(v["tested"] for v in M4["s_m"]["per_corruption"].values()) and H3["go"] is False
S1 = [
    ("P", "GATE-M against no gate under JPEG, noise and splice", "bounded null", f"{MP} outcome.label (= negative)"),
    ("S-C", "GATE-M against no gate on clean images", "not rejected", f"{MP} s_c.p_holm"),
    ("PS", "pipeline check on patch and swap corruptions", "not rejected", f"{MP} ps.per_corruption.*.p_holm"),
    ("S-D", "detection of changed tokens against a frozen cheap score", "rejected (Holm)", f"{MP} s_d2.per_corruption.*.p_holm"),
    ("S-M", "GATE-M against a random gate of equal size", "not run", f"{MP} s_m.per_corruption.*.tested (all false)"),
    ("S2", "re-infill of flagged tokens against random re-infill", "not rejected", "runs/P2-GATE-S2/analysis.json per_cell.*.p_holm"),
    ("B", "combination of both directions against the better single one", "not rejected", "runs/P2-GATE-FOIL/analysis.json test.p"),
    ("H", "GATE-M against no gate on hard-negative pairs", "not run", "runs/P2-GATE-H3/family.json go (= false)"),
]
# ---- Study 2 decision words ---------------------------------------------------------------------------------------------------------------
assert FL["L1"]["label"] == "confirmed" and FL["L-NI"]["label"] == "shown" and FL["L-LEN"]["label"] == "rejected"
assert FL["L3"]["rejected"] is False and FL["L4"]["rejected"] is True and all(v["rejected"] for v in FG.values())
LP = "runs/P2-LRF-L1/a6_analysis.json"
S2R = [
    ("L1", "learned weights against the unweighted sum, Gaussian noise 0.1 (primary)", "confirmed", f"{LP} family_L.L1.label"),
    ("L3", "the same under JPEG quality 10", "not rejected", f"{LP} family_L.L3.rejected"),
    ("L4", "the same under a 128 px splice", "rejected (Holm)", f"{LP} family_L.L4.{{rejected,p_holm}}"),
    ("L-NI", "loss on clean images no larger than the margin", "shown", f"{LP} family_L.L-NI.label"),
    ("L-LEN", "L1 with length-matched wrong captions", "rejected", f"{LP} family_L.L-LEN.label"),
    ("LG shot", "the same under shot noise, severity 3", "rejected (Holm)", "runs/P2-LRF-LG/a6_analysis.json family_LG.cells.shot_noise3.{rejected,p_holm}"),
    ("LG impulse", "the same under impulse noise, severity 3", "rejected (Holm)", "runs/P2-LRF-LG/a6_analysis.json family_LG.cells.impulse_noise3.{rejected,p_holm}"),
    ("LG speckle", "the same under speckle noise, severity 3", "rejected (Holm)", "runs/P2-LRF-LG/a6_analysis.json family_LG.cells.speckle_noise3.{rejected,p_holm}"),
]
r1 = [row([f, w, d], [src]) for f, w, d, src in S1]
r2 = [row([f, w, d], [src]) for f, w, d, src in S2R]
mc = lambda t: r"\multicolumn{3}{@{}l}{\textit{" + t + "}}"
write("tab_families_glance.tex", "@{}lp{0.50\\columnwidth}l@{}", ["Family", "What it tests", "Decision"],
      [[row([mc("Study 1")], ["block heading"])] + r1, [row([mc("Study 2")], ["block heading"])] + r2],
      preamble=["Status only: the preregistered decision word of each family, no number. No cross-study row; the two blocks are independent preregistered studies.",
                "'bounded null' = the negative label of family P (changes beyond the margin excluded); 'shown' = the non-inferiority statement of L-NI."])
