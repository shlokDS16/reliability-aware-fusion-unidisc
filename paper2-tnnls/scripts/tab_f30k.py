"""Table of the preregistered transfer test on Flickr30K (SAP Addendum A7: F1, F-NI, F-LEN). Source: runs/P2-LRF-F30K/f30k_analysis.json only.
Output: paper2-tnnls/tables/tab_f30k.tex
Wording (A7.5): "confirmed" for F1 and F-LEN as labelled in the analysis file; F-NI is a non-inferiority statement and carries no p (superiority on clean
images was not preregistered). No comparison with any other method, no link to any other study."""
from __future__ import annotations

import math

import figstyle as S
from tablib import bold, iv, num, row, write

A = S.jload("P2-LRF-F30K/f30k_analysis.json")
assert A["complete"] is True and A["n_scored"] == 872 and A["n_test_split"] == 1000
F1, FN, FL = A["F1"], A["F_NI"], A["F_LEN"]
assert F1["label"] == "confirmed" and F1["headline_gain_claim_allowed"] is True
assert FL["label"] == "confirmed" and FL["n_excluded_length_mismatch"] == 0
assert FN["non_inferior"] is True and FN["lower90"] > FN["margin"]
P = "runs/P2-LRF-F30K/f30k_analysis.json"
KEYS = "{n,acc_none,acc_lrf,b,c,net,%s}"


def pexp(p: float) -> str:
    """One-sided exact p in scientific notation, two significant digits."""
    m, e = f"{p:.1e}".split("e")
    return f"${m}\\times10^{{{int(e)}}}$"


def cells(name, r, ci, p_text, dec, rej):
    net = num(r["net"], plus=False)
    net = bold(net) if rej else net
    return [name, num(r["acc_none"]), num(r["acc_lrf"]), str(r["b"]), str(r["c"]),
            net + " " + iv(*r[ci]) + ("$^{\\dagger}$" if ci == "ci90" else ""), p_text, bold(dec) if rej else dec]


blk = [
    row(cells("F1: noise, $\\sigma=0.1$", F1, "ci95", pexp(F1["p_one"]), "confirmed", True),
        [f"{P} F1.{KEYS % 'ci95,p_one,label'}; n = 872 for all rows"]),
    row(cells("F-NI: clean images", FN, "ci90", "--", "non-inferior", False),
        [f"{P} F_NI.{KEYS % 'ci90,lower90,margin,non_inferior'} (lower90 = {FN['lower90']:.4f} > margin = {FN['margin']})"]),
    row(cells("F-LEN: noise, length-matched", FL, "ci95", pexp(FL["p_one"]), "confirmed", True),
        [f"{P} F_LEN.{KEYS % 'ci95,p_one,label'}; n_excluded_length_mismatch = 0"]),
]
assert all(math.isfinite(x["p_one"]) for x in (F1, FL))

write("tab_f30k.tex", "@{}lccrrlcl@{}",
      ["Hypothesis", "Acc.\\ none", "Acc.\\ LRF", "$b$", "$c$", "Net (95\\% interval)", "$p$ one-sided", "Decision"],
      [blk],
      preamble=["requires booktabs; resizebox to the column width",
                "p one-sided: exact McNemar (key p_one); F-NI prints no p (its preregistered test is the lower 90% bound against the margin)",
                "dagger: 90% interval (non-inferiority); every other interval 95% paired percentile bootstrap over items, 10000 resamples, SeedSequence(0)",
                "bold: the preregistered test of the row rejected its null at its preregistered level"],
      script="tab_f30k.py")
