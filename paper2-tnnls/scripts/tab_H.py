"""Family H, decision only, in its own small table (A5.9: Results and supplement only; never title, abstract, highlights, conclusion, cover letter).
Reads only the decision fields of runs/P2-GATE-H3/family.json (go, downstream_claim_withdrawn, n_rule.h_rule); no H3 item value is read or printed.
Output: paper2-tnnls/tables/tab_H.tex (drop the file if the writer places H in prose only)."""
from __future__ import annotations

import figstyle as S
from tablib import row, write

H = S.jload("P2-GATE-H3/family.json")
F = "runs/P2-GATE-H3/family.json"
assert H["go"] is False and H["n_rule"]["h_rule"] == "H-NOGO" and H["downstream_claim_withdrawn"] is True
write("tab_H.tex", "@{}ll@{}", ["Item", "Recorded decision"],
      [[row(["Preregistered decision rule", H["n_rule"]["h_rule"]], [f"{F} n_rule.h_rule"]),
        row(["Test performed", "no"], [f"{F} go (= false)"]),
        row(["Downstream claim", "withdrawn"], [f"{F} downstream_claim_withdrawn (= true)"])]],
      preamble=["decision fields only; no item value of the headroom run is shown (A5.9 placement)"])
