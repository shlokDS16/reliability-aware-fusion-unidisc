"""Table II (Study 2 preregistered families L1, L3, L4, L-NI, L-LEN, LG x3). Study 2 numbers only; no GATE-M, CLIP or SigLIP number (SPEC rule 3, A6.12).
Sources: runs/P2-LRF-L1/a6_analysis.json (family_L), runs/P2-LRF-LG/a6_analysis.json (family_LG; its family_L is asserted equal to the L1 file's).
Output: paper2-tnnls/tables/tab2_study2.tex
Wording: "confirmed" only for L1; other rejections are "rejected" with the adjusted p; the L-NI row is a non-inferiority statement and carries no p
(superiority on clean images was not preregistered, GATE-AUDIT-FAMILY-L)."""
from __future__ import annotations

import figstyle as S
from tablib import bold, iv, num, pv, row, write

L1 = S.jload("P2-LRF-L1/a6_analysis.json")
LG = S.jload("P2-LRF-LG/a6_analysis.json")
assert L1["family_L"] == LG["family_L"]
FL, FG = L1["family_L"], LG["family_LG"]
assert FL["branch"]["branch"] == "A" and FL["L1"]["label"] == "confirmed" and FG["m_preregistered"] == 3
P1, PG = "runs/P2-LRF-L1/a6_analysis.json", "runs/P2-LRF-LG/a6_analysis.json"
KEYS = "{n,acc_a,acc_b,b,c,net,%s}"


def pcols(r, holm=True, ni=False):
    """one-sided, Holm (where the preregistration applies one), two-sided p of a row; L-NI carries a dagger: not its preregistered test."""
    if ni:                                             # lead 2026-10-30: no superiority p beside L-NI (red-team F12); its test is the 90% bound vs the margin
        return ["--", "--", "--"]
    return [pv(r["p_one"]), pv(r["p_holm"]) if holm and r.get("p_holm") is not None else "--", pv(r["p_two"])]


def cells(name, r, ci, p_text, dec, rej):
    net = num(r["net"], plus=False)
    net = bold(net) if rej else net
    return [name, str(r["n"]), num(r["acc_b"]), num(r["acc_a"]), str(r["b"]), str(r["c"]), net + " " + iv(*r[ci]) + ("$^{\\dagger}$" if ci == "ci90" else ""),
            *p_text, bold(dec) if rej else dec]


famL = []
r = FL["L1"]
famL.append(row(cells("L1: noise, $\\sigma=0.1$", r, "ci95", pcols(r, holm=False), "confirmed (one-sided)", True),
                [f"{P1} family_L.L1.{KEYS % 'ci95,p_one,label'}", f"{P1} branch.branch (= A)"]))
r = FL["L3"]
assert r["rejected"] is False
famL.append(row(cells("L3: JPEG, quality 10", r, "ci95", pcols(r), "not rejected", False),
                [f"{P1} family_L.L3.{KEYS % 'ci95,p_holm,rejected'}"]))
r = FL["L4"]
assert r["rejected"] is True
famL.append(row(cells("L4: splice, 128 px", r, "ci95", pcols(r), "rejected (Holm)", True),
                [f"{P1} family_L.L4.{KEYS % 'ci95,p_holm,rejected'}"]))
r = FL["L-NI"]
assert r["non_inferior"] is True and r["lower90"] > -r["margin"]
famL.append(row(cells("L-NI: clean images", r, "ci90", pcols(r, holm=False, ni=True), f"non-inferior (lower bound {num(r['lower90'])} above {num(-r['margin'], 2)})", False),
                [f"{P1} family_L.L-NI.{KEYS % 'ci90,lower90,margin,non_inferior'}"]))
r = FL["L-LEN"]
assert r["rejected"] is True
famL.append(row(cells("L-LEN: noise, length-matched negatives", r, "ci95", pcols(r, holm=False), "rejected (one-sided)", True),
                [f"{P1} family_L.L-LEN.{KEYS % 'ci95,p_one,rejected'} (n = 449: one item excluded)"]))

famG = []
for key, nm in (("shot_noise3", "LG: shot noise"), ("impulse_noise3", "LG: impulse noise"), ("speckle_noise3", "LG: speckle noise")):
    r = FG["cells"][key]
    assert r["rejected"] is True and r["net"] > 0
    famG.append(row(cells(nm, r, "ci95", pcols(r), "rejected (Holm, one-sided)", True),
                    [f"{PG} family_LG.cells.{key}.{KEYS % 'ci95,p_holm,rejected'}"]))

write("tab2_study2.tex", "@{}lrccrrlrrrl@{}",
      ["Hypothesis", "$n$", "Acc.\\ none", "Acc.\\ LRF", "$b$", "$c$", "Net (95\\% interval)", "$p$ one-sided", "$p$ Holm", "$p$ two-sided", "Preregistered decision"],
      [famL, famG],
      preamble=["requires booktabs; table* or adjustbox for the 9-column width",
                "p one-sided / p two-sided: exact McNemar p (run keys p_one, p_two); p Holm: key p_holm where the preregistration applies Holm (L3, L4 after the L1 gate; LG, m = 3), otherwise --",
                "L-NI: no p is printed; its preregistered test is the lower 90% bound against the margin, and superiority on clean images was not preregistered",
                "dagger: 90% interval (non-inferiority); every other interval 95% percentile bootstrap over items, 10000 resamples",
                "bold: the preregistered test of the row rejected its null at its preregistered level"],
      notes=[f"LG impulse row: two-sided p {FG['cells']['impulse_noise3']['p_two']:.3f} and 95% interval lower bound {FG['cells']['impulse_noise3']['ci95'][0]:.1f} must be stated beside it in the text (GATE-AUDIT-FAMILY-LG F2); run: runs/P2-LRF-LG/a6_analysis.json family_LG.cells.impulse_noise3.{{p_two,ci95}}"])
