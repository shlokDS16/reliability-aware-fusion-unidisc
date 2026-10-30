"""Table I (Study 1, preregistered families P, S-C, PS, S-D, S-M, S2, B, H). Study 1 numbers only; no Study 2 number (SPEC rule 3).
Sources: runs/P2-GATE-M4/analysis.json (P, S-C, PS, S-M, S-D out-of-sample = s_d2), runs/P2-GATE-S2/analysis.json (S2),
runs/P2-GATE-FOIL/analysis.json (B; commit 10e6bc0f), runs/P2-GATE-H3/family.json (H: decision fields only, no H3 item value).
Output: paper2-tnnls/tables/supp_study1_families.tex (SUPPLEMENT overview of all Study 1 families; main text uses tab1_familyP, tab_ps, tab_detection, tab_H per spec v2.2)"""
from __future__ import annotations

import figstyle as S
from tablib import bold, iv, num, pv, row, write

M4 = S.jload("P2-GATE-M4/analysis.json")
S2 = S.jload("P2-GATE-S2/analysis.json")
FB = S.jload("P2-GATE-FOIL/analysis.json")
H = S.jload("P2-GATE-H3/family.json")
MP, M2, MF, MH = "runs/P2-GATE-M4/analysis.json", "runs/P2-GATE-S2/analysis.json", "runs/P2-GATE-FOIL/analysis.json", "runs/P2-GATE-H3/family.json"
PM = r"$\pm0.05$"

assert M4["outcome"]["label"] == "negative" and M4["primary"]["claim_survives"] is False
assert M4["ps"]["positive_control"] == "not met"
assert H["go"] is False and H["n_rule"]["h_rule"] == "H-NOGO" and H["downstream_claim_withdrawn"] is True
assert FB["combination_beat_best_single"] is False and S2["holm_m"] == 2

blocks = []
# ---- P --------------------------------------------------------------------------------------------------------------------------------
rows = []
for key, nm in (("jpeg", "JPEG, quality 10"), ("noise", r"Noise, $\sigma=0.1$"), ("splice", "Splice, 128 px")):
    r = M4["primary"]["per_corruption"][key]
    assert r["equivalent_within_0p05"] is True
    dec = f"not rejected, $p_{{\\rm Holm}}={pv(r['p_holm'])}$; 90\\% interval inside {PM}"
    rows.append(row(["P", nm, r"accuracy, GATE-M $-$ none", str(r["n"]), num(r["delta"]), iv(*r["ci90"]) + "$^{a}$", dec],
                    [f"{MP} primary.per_corruption.{key}.{{n,delta,ci90,p_holm,equivalent_within_0p05}}", f"{MP} outcome.label (= negative)"]))
blocks.append(rows)
# ---- S-C ------------------------------------------------------------------------------------------------------------------------------
r = M4["s_c"]
assert r["equivalent_within_0p05"] is True
blocks.append([row(["S-C", "Clean images", r"accuracy, GATE-M $-$ none", str(r["n"]), num(r["delta"]), iv(*r["ci90"]) + "$^{a}$",
                    f"not rejected, $p_{{\\rm Holm}}={pv(r['p_holm'])}$; 90\\% interval inside {PM}"],
                   [f"{MP} s_c.{{n,delta,ci90,p_holm,equivalent_within_0p05}}"])])
# ---- PS -------------------------------------------------------------------------------------------------------------------------------
rows = []
for key, nm in (("patch", r"Patch, $8\times8$ codes"), ("swap", r"Swap, 15\% of codes")):
    r = M4["ps"]["per_corruption"][key]
    rows.append(row(["PS", nm, r"accuracy, GATE-M $-$ none", str(r["n"]), num(r["delta"]), iv(*r["ci95"]),
                     f"not rejected, $p_{{\\rm Holm}}={pv(r['p_holm'])}$; positive control not met"],
                    [f"{MP} ps.per_corruption.{key}.{{n,delta,ci95,p_holm}}", f"{MP} ps.positive_control (= not met)"]))
blocks.append(rows)
# ---- S-D (out-of-sample, test items) -----------------------------------------------------------------------------------------------------
rows = []
for key, nm in (("jpeg", "JPEG, quality 10"), ("noise", r"Noise, $\sigma=0.1$")):
    r = M4["s_d2"]["per_corruption"][key]
    assert r["q_beats_frozen_rival"] is False and r["p_holm"] < 0.05 and r["diff_mean"] < 0
    rows.append(row(["S-D", nm, r"AUROC, $q$ $-$ frozen rival", str(r["n_eligible"]), bold(num(r["diff_mean"])), iv(*r["ci95"]),
                     bold(f"rejected, $p_{{\\rm Holm}}={pv(r['p_holm'])}$") + "; rival higher"],
                    [f"{MP} s_d2.per_corruption.{key}.{{n_eligible,diff_mean,ci95,p_holm,q_beats_frozen_rival}}"]))
blocks.append(rows)
# ---- S-M ------------------------------------------------------------------------------------------------------------------------------
sm = M4["s_m"]
assert not any(v["tested"] for v in sm["per_corruption"].values())
blocks.append([row(["S-M", "All three corruptions", r"accuracy, GATE-M $-$ random gate", "--", "--", "--",
                    "not tested: no primary rejection with $b>c$"],
                   [f"{MP} s_m.per_corruption.{{jpeg,noise,splice}}.tested (all false)"])])
# ---- S2 -------------------------------------------------------------------------------------------------------------------------------
rows = []
for key, nm in (("patch", r"Patch, $8\times8$ codes"), ("splice", "Splice, 128 px")):
    r = S2["per_cell"][key]
    rows.append(row(["S2", nm, r"accuracy, flagged set $-$ random-gate best-of-4 re-infill", str(r["n"]), num(r["delta"]), iv(*r["ci95"]),
                     f"{r['reading']}, $p_{{\\rm Holm}}={pv(r['p_holm'])}$"],
                    [f"{M2} per_cell.{key}.{{n,delta,ci95,p_holm,reading}}"]))
blocks.append(rows)
# ---- B --------------------------------------------------------------------------------------------------------------------------------
t = FB["test"]
blocks.append([row(["B", "Foil pairs, clean images", r"accuracy, two-way fusion $-$ text direction", str(t["n"]), num(t["delta"]), iv(*t["ci95"]),
                    f"not rejected, $p={pv(t['p'])}$; no gain over the text direction detected"],
                   [f"{MF} test.{{n,delta,ci95,p}}, combination_beat_best_single (= false), best_direction (= T)"])])
# ---- H (decision only) ------------------------------------------------------------------------------------------------------------------
blocks.append([row(["H", "Three corruptions", "decision fields only", "--", "--", "--", "H-NOGO: not tested; downstream claim withdrawn"],
                   [f"{MH} go (= false), n_rule.h_rule (= H-NOGO), downstream_claim_withdrawn (= true)"])])

write("supp_study1_families.tex", "@{}lllrcll@{}", ["Family", "Cell", "Contrast", "$n$", "Estimate", "Interval", "Preregistered decision"], blocks, script="tab1_study1.py",
      preamble=["requires booktabs; use inside table* or with \\small / adjustbox for the 7-column width",
                "footnote a: 90% percentile-bootstrap interval (the interval that carries the equivalence decision); all other intervals are 95%"])
