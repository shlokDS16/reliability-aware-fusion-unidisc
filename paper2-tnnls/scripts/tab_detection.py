"""Detection table (Study 1, family S-D, 200 detection items): per-item AUROC against changed-code labels, with 95% percentile-bootstrap interval, for
the gate's score q, the one-pass TbV score (non-finetuned) and the best cheap rival with its sign, plus the paired difference q minus rival.
Source: runs/P2-GATE-M1/analysis.json: table.<corr>.{q,tbv,<rival>}.{mean,lo,hi,n}; paired_q_vs_best_cheap.<corr>.{best_cheap,rival_sign,diff_mean,ci95,p_holm}.
The rival was chosen on these data among its two orientations (sign oracle), so rival values are optimistic. Bold: Holm-adjusted p below 0.05 (preregistered
falsifier family, JPEG and noise only). Output: paper2-tnnls/tables/tab_detection.tex. No claim that q detects better than any rival."""
from __future__ import annotations

import figstyle as S
from tablib import bold, iv, num, pv, row, write

A = S.jload("P2-GATE-M1/analysis.json")
P = A["paired_q_vs_best_cheap"]
F = "runs/P2-GATE-M1/analysis.json"
NAMES = {"tex": "patch texture", "tex_neg": "patch texture", "plainB": "plain $B$"}
BASE = {"tex_neg": "tex", "plainB": "plainB"}
rows = []
for corr, nm in (("patch", r"Patch, $8\times8$ codes"), ("swap", r"Swap, 15\% of codes"), ("jpeg", "JPEG, quality 10"), ("noise", r"Noise, $\sigma=0.1$")):
    t, pr = A["table"][corr], P[corr]
    rv = pr["best_cheap"]
    sign = "$-$" if pr["rival_sign"] < 0 else "$+$"
    q, tb, rr = t["q"], t["tbv"], t[rv]
    assert q["n"] == tb["n"] == rr["n"]
    sig = pr.get("p_holm") is not None and pr["p_holm"] < 0.05
    diff = f"{num(pr['diff_mean'])} {iv(*pr['ci95'])}"
    rows.append(row([nm, str(q["n"]), f"{num(q['mean'])} {iv(q['lo'], q['hi'])}", f"{num(tb['mean'])} {iv(tb['lo'], tb['hi'])}",
                     f"{NAMES[rv]} ({sign}): {num(rr['mean'])} {iv(rr['lo'], rr['hi'])}", bold(diff) if sig else diff],
                    [f"{F} table.{corr}.{{q,tbv,{rv}}}.{{mean,lo,hi,n}}; paired_q_vs_best_cheap.{corr}.{{best_cheap,rival_sign,diff_mean,ci95,p_holm}}"]))
write("tab_detection.tex", "@{}lrllll@{}",
      ["Corruption", "Items", "$q$ (AUROC)", "TbV score, one pass (AUROC)", "Best cheap rival, sign (AUROC)", "$q$ minus rival"], [rows],
      preamble=["AUROC against changed-code labels per item; 95% percentile bootstrap over items (10000 resamples); rival and its sign chosen on these data (sign oracle): rival values optimistic.",
                "bold: Holm-adjusted p < 0.05 of the paired contrast (JPEG, noise); no claim about detection relative to any rival."])
