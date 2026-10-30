"""Supplement table: every quantity SAP A6.4 lists under "Reported with every test" for L1, L3, L4, L-NI, L-LEN and the three LG cells:
b, c, n_d, n, both accuracies, net difference with 90% and 95% paired percentile-bootstrap intervals, Clopper-Pearson 95% interval of b/n_d, exact one- and
two-sided p, mid-p (one- and two-sided), plus Holm p where the plan applies one and the decision. Two lines per test (counts line, then the interval/p line).
Sources: runs/P2-LRF-L1/a6_analysis.json family_L.*; runs/P2-LRF-LG/a6_analysis.json family_LG.cells.* (its family_L equals the L1 file's).
Output: paper2-tnnls/tables/supp_tests_full_study2.tex. Bold = preregistered test rejected at its level; L-NI p values are not its preregistered test (dagger)."""
from __future__ import annotations

import figstyle as S
from tablib import bold, iv, num, pv, row, write

L1 = S.jload("P2-LRF-L1/a6_analysis.json")
LG = S.jload("P2-LRF-LG/a6_analysis.json")
assert L1["family_L"] == LG["family_L"]
FL, FG = L1["family_L"], LG["family_LG"]["cells"]
PL, PG = "runs/P2-LRF-L1/a6_analysis.json", "runs/P2-LRF-LG/a6_analysis.json"
HEAD = ["Test", "$n$", "$b$", "$c$", "$n_d$", "Acc.\\ none", "Acc.\\ LRF", "Net", "Decision"]
KEYS = "{n,b,c,n_d,acc_a,acc_b,net,ci90,ci95,cp95_b_over_nd,p_one,p_two,p_mid_one,p_mid_two,p_holm}"

TESTS = [
    ("L1: noise, $\\sigma=0.1$", FL["L1"], f"{PL} family_L.L1", "confirmed (one-sided)", True, False),
    ("L3: JPEG, quality 10", FL["L3"], f"{PL} family_L.L3", "not rejected", False, False),
    ("L4: splice, 128 px", FL["L4"], f"{PL} family_L.L4", "rejected (Holm)", True, False),
    ("L-NI: clean images", FL["L-NI"], f"{PL} family_L.L-NI", None, False, True),
    ("L-LEN: noise, length-matched", FL["L-LEN"], f"{PL} family_L.L-LEN", "rejected (one-sided)", True, False),
    ("LG: shot noise", FG["shot_noise3"], f"{PG} family_LG.cells.shot_noise3", "rejected (Holm, one-sided)", True, False),
    ("LG: impulse noise", FG["impulse_noise3"], f"{PG} family_LG.cells.impulse_noise3", "rejected (Holm, one-sided)", True, False),
    ("LG: speckle noise", FG["speckle_noise3"], f"{PG} family_LG.cells.speckle_noise3", "rejected (Holm, one-sided)", True, False),
]
rows = []
for name, r, src, dec, rej, ni in TESTS:
    if ni:
        assert r["non_inferior"] is True
        dec = f"non-inferior: lower 90\\% bound {num(r['lower90'])} above {num(-r['margin'], 2)}"
    d = "$^{\\ddagger}$" if ni else ""
    net = num(r["net"])
    main = row([name, str(r["n"]), str(r["b"]), str(r["c"]), str(r["n_d"]), num(r["acc_b"]), num(r["acc_a"]), bold(net) if rej else net,
                bold(dec) if rej else dec], [f"{src}.{KEYS}"])
    holm = pv(r["p_holm"]) if r.get("p_holm") is not None else "not applicable"
    cp = iv(*r["cp95_b_over_nd"])
    sub = row([r"\multicolumn{9}{l}{\footnotesize 90\% " + iv(*r["ci90"]) + r";\; 95\% " + iv(*r["ci95"]) + r";\; Clopper--Pearson 95\% of $b/n_d$ " + cp
               + r";\; exact $p$: one-sided " + pv(r["p_one"]) + d + ", two-sided " + pv(r["p_two"]) + d + r";\; mid-$p$: one-sided " + pv(r["p_mid_one"]) + d
               + ", two-sided " + pv(r["p_mid_two"]) + d + r";\; Holm $p$ " + holm + "}"], [f"{src}.{{ci90,ci95,cp95_b_over_nd,p_one,p_two,p_mid_one,p_mid_two,p_holm}}"])
    rows += [main, sub]
write("supp_tests_full_study2.tex", "@{}lrrrrccrl@{}", HEAD, [rows],
      preamble=["Every quantity of SAP A6.4 'Reported with every test'. Intervals: paired percentile bootstrap over items (10000 resamples); Holm p: L3, L4 after the L1 gate (m = 2 two-sided) and LG (m = 3 one-sided); not applicable elsewhere.",
                "double dagger (L-NI): p values against zero net change shown for completeness only; the preregistered L-NI test is the lower 90% bound against the margin; superiority on clean images was not preregistered.",
                "impulse-noise row: two-sided p and the 95% interval lower bound 0.0 are stated beside it in the text; no two-sided claim."], script="tab_tests_full.py")
