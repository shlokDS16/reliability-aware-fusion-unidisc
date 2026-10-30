"""Table I (family P only) and the positive-control table (family PS, "Positive control (pipeline check)"), Study 1 numbers only.
Table I: n, b, c, n_d, accuracies of both arms, net difference, 90/95/98.33% intervals, p and Holm p, preregistered decision, plus the exact
Clopper-Pearson 95% bound on the net change from runs/P2-PAPER-BOUNDS/p_exact_bounds.json (labelled "added at writing, descriptive").
Sources: runs/P2-GATE-M4/analysis.json primary.per_corruption.*, ps.per_corruption.*, outcome.label; runs/P2-PAPER-BOUNDS/p_exact_bounds.json.
Outputs: paper2-tnnls/tables/tab1_familyP.tex, tab_ps.tex. No estimate is bold: no test of these families rejected (bold rule: test rejected at its level)."""
from __future__ import annotations

import figstyle as S
from tablib import bold, iv, num, pv, row, write

A = S.jload("P2-GATE-M4/analysis.json")
BND = S.jload("P2-PAPER-BOUNDS/p_exact_bounds.json")
MP, MB = "runs/P2-GATE-M4/analysis.json", "runs/P2-PAPER-BOUNDS/p_exact_bounds.json"
assert A["outcome"]["label"] == "negative" and A["ps"]["positive_control"] == "not met"
assert BND["meta"]["label"].startswith("added at writing, descriptive")
HDR = ["Cell", "$n$", "Acc.\\ none", "Acc.\\ GATE-M", "$b$", "$c$", "$n_d$", "Net diff.", "$p$ ($p_{\\rm Holm}$)", "Preregistered decision"]
COLS = "@{}lrccrrrrll@{}"


def cell_rows(block, key, label, dec, with90, bound):
    r = block[key]
    assert not (r["p_holm"] < 0.05 and r["delta"] > 0)
    main = row([label, str(r["n"]), num(r["acc_b"]), num(r["acc_a"]), str(r["b"]), str(r["c"]), str(r["n_d"]), num(r["delta"]),
                f"{pv(r['p'])} ({pv(r['p_holm'])})", dec],
               [f"{MP} {'primary' if with90 else 'ps'}.per_corruption.{key}.{{n,acc_a,acc_b,b,c,n_d,delta,p,p_holm}}"])
    ivs = (f"90\\% {iv(*r['ci90'])};\\; " if with90 else "") + f"95\\% {iv(*r['ci95'])};\\; 98.33\\% {iv(*r['ci9833'])}"
    runs = [f"{MP} {'primary' if with90 else 'ps'}.per_corruption.{key}.{{ci90,ci95,ci9833}}"]
    if bound:
        b = BND["per_corruption"][key]
        assert (b["b"], b["c"], b["n_d"], b["n"]) == (r["b"], r["c"], r["n_d"], r["n"])
        ivs += f";\\; exact 95\\% bound on $|$net change$|$ {num(b['bound_abs_net_change_95'])} (added at writing, descriptive)"
        runs.append(f"{MB} per_corruption.{key}.{{bound_abs_net_change_95}}; meta.label")
    sub = row([r"\multicolumn{10}{l}{\footnotesize intervals: " + ivs + "}"], runs)
    return [main, sub]


# ---- Table I ---------------------------------------------------------------------------------------------------------------------------
P = A["primary"]["per_corruption"]
DEC_P = r"not rejected; 90\% interval inside $(-0.05,\,0.05)$"
blkP = []
for key, nm in (("jpeg", "P1: JPEG, quality 10"), ("noise", r"P2: noise, $\sigma=0.1$"), ("splice", "P3: splice, 128 px")):
    assert P[key]["equivalent_within_0p05"] is True
    blkP += cell_rows(P, key, nm, DEC_P, True, True)
write("tab1_familyP.tex", COLS, HDR, [blkP],
      preamble=["Family P only. Holm over three corruptions (m = 3); p: exact two-sided McNemar. The family label is negative (outcome.label); the abstract sentence is the preregistered one.",
                "Under noise b = c = 0: the bootstrap intervals are the single point zero (absence of discordant items, not a measured precision); the exact bound is the descriptive complement.",
                "Exact Clopper-Pearson bound: runs/P2-PAPER-BOUNDS/p_exact_bounds.json, 'added at writing, descriptive; not preregistered'; list it in the deviations box."])

# ---- positive control ---------------------------------------------------------------------------------------------------------------------
blkS = []
for key, nm in (("patch", r"PS1: patch, $8\times8$ codes"), ("swap", r"PS2: swap, 15\% of codes")):
    blkS += cell_rows(A["ps"]["per_corruption"], key, nm, "not rejected; positive control not met", False, False)
write("tab_ps.tex", COLS, HDR, [blkS],
      preamble=["Positive control (pipeline check) only: Holm over two (m = 2); never beside family P; no estimate bold (no rejection).",
                "runs/P2-GATE-M4/analysis.json ps.positive_control = 'not met' (asserted); the A2.3 audit found no defect (runs/P2-A23-AUDIT/a23_ps_audit.json)."])
