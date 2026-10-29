# WRITER-RESULTS-1: every number in the Paper 2 results pass, with its source

```yaml
agent: manuscript-writer
date: 2026-10-29
brief: Results, abstract, highlights, 6.1 opening and conclusion of Paper 2 for the preregistered NEGATIVE label of P (S2, B pending)
sources_examined:
  - runs/P2-GATE-M4/analysis.json
  - runs/P2-GATE-M4/edec.json
  - runs/P2-GATE-M4/epred_score.json
  - runs/P2-GATE-M4/tier3_fusion.json
  - runs/P2-GATE-M5/coherence.json
  - runs/P2-GATE-M5/mu_from_m4.json
  - runs/P2-GATE-M3/family.json
  - runs/P2-GATE-M3/c1_head.json
  - runs/P2-GATE-M2/threshold.json
  - runs/P2-GATE-M2/c1_cal.json
  - runs/P2-GATE-M1/analysis.json
coverage: >
  Every decimal number in the new or changed prose and tables of paper2/sections/results.tex, discussion.tex (Findings, limitation
  items changed), conclusion.tex, introduction.tex (contribution items 3 and 5) and the abstract and highlights of paper2/main.tex.
  Numbers that were already in the detection subsection before this pass (run P2-GATE-M1) are listed too. Not covered: method,
  protocol and appendix numbers that predate this pass.
claims:
  - statement: "Every decimal number in the new text matches a value in the table below at its printed precision (script check)."
    status: supported
    evidence: "scratchpad crosscheck.py over the five tex files; remaining unmatched tokens are design constants listed below"
    level: E4
    confidence: 0.9
```

**How the table was made.** A script (`registry.py`) reads each value from its file by its JSON key and writes this table, so the
values below are the files' own values at full precision. The paper rounds them: accuracies, net differences, AUROC and flag rates to
3 decimals; flagged shares and evidence-ratio differences to 4 decimals; $p$-values to 2 significant figures (0.625 kept exact);
exact intervals to 3 decimals. A script cross-check found every decimal in the new text in this table at its printed precision, except
the design constants listed next.

**Design constants and derived numbers (not run outputs).** 1.4B (model size, protocol); 0.05 (alpha and the SAP equivalence margin,
"five percentage points"); 0.01 and 0.10 (other alpha levels); 2.13 (violation bound; also `calibration.fap_check.critical_value`);
90, 95, 98.33 percent (interval levels; 98.33 = Holm level of the first step for m = 3); 2.5 and 97.5 (percentiles of the split
replication); 18 and 29 (bounds of rule R2, SAP); 1 024 tokens and 500 / 300 / 100 fold sizes (design; `n_items`, `n_cal`,
`n_headroom_items` confirm them); "about four percent" = 1 - rho(JPEG) = 1 - 0.9606 (derived); "more than nine in ten" = rho 0.961 and
0.928 (derived); coherence: 800 gaps = 100 items x 4 pairs x 2 contexts and 200 floor differences = 25 items x 4 x 2
(`exp_p2/gate/checks.py:64-90`; noise-floor rule `idx % 4 == 0` in `runs/P2-GATE-M5/config.json`); $D^\ast$ = max(19, 18, 2) = 19
(derived from `rungs.*.discordance_chg_vs_none.D_c`); 90 percent intervals "between -0.010 and 0.002" in the conclusion = the union of
the three `ci90` intervals.

**Wording sources.** NEG label sentences: SAP Addendum A4 r3, A4.2.3 (title QT, highlight 1, abstract sentence, 6.1 opening), A4.2.2
item 6 (highlight 2, "3 corruptions" form) and item 7 (scope); A4.2.4 (contribution items 3 and 5). Tier-3 readings: A4.1.10 r3 rule
(exact Clopper-Pearson discordant split; B for n_d < 10, MDD for n_d >= 10); `reading` and `counts_against` fields of
`tier3_fusion.json` agree with that rule and were used. E-pred: AB.3 (sentence copied from `epred_score.json` `P.sentence`).
PS: AB.1 item 1(a) ("pipeline defect suspected, audit triggered"). E-dec: AB.2 names; V < 0 with CI excluding 0 voids a detection
reading (JPEG cell).

## Every number and its source

| # | Used in | Value (full precision) | Source file | JSON key |
|---|---|---|---|---|
| 1 | P table/abstract | 500 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.n` |
| 2 | P table/abstract | 0.838 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.acc_b` |
| 3 | P table/abstract | 0.836 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.acc_a` |
| 4 | P table/abstract | 0 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.b` |
| 5 | P table/abstract | 1 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.c` |
| 6 | P table/abstract | 1 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.n_d` |
| 7 | P table/abstract | -0.002 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.delta` |
| 8 | P table/abstract | [-0.006, 0] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.ci90` |
| 9 | P table/abstract | [-0.006, 0] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.ci95` |
| 10 | P table/abstract | [-0.008, 0] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.ci9833` |
| 11 | P table/abstract | 1 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.p` |
| 12 | P table/abstract | 1 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.p_holm` |
| 13 | P table/abstract | [0, 0.975] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.theta_cp95` |
| 14 | P table/abstract | True | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.jpeg.equivalent_within_0p05` |
| 15 | P table/abstract | 500 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.n` |
| 16 | P table/abstract | 0.676 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.acc_b` |
| 17 | P table/abstract | 0.676 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.acc_a` |
| 18 | P table/abstract | 0 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.b` |
| 19 | P table/abstract | 0 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.c` |
| 20 | P table/abstract | 0 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.n_d` |
| 21 | P table/abstract | 0 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.delta` |
| 22 | P table/abstract | [0, 0] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.ci90` |
| 23 | P table/abstract | [0, 0] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.ci95` |
| 24 | P table/abstract | [0, 0] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.ci9833` |
| 25 | P table/abstract | 1 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.p` |
| 26 | P table/abstract | 1 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.p_holm` |
| 27 | P table/abstract | [nan, nan] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.theta_cp95` |
| 28 | P table/abstract | True | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.noise.equivalent_within_0p05` |
| 29 | P table/abstract | 500 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.n` |
| 30 | P table/abstract | 0.876 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.acc_b` |
| 31 | P table/abstract | 0.872 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.acc_a` |
| 32 | P table/abstract | 1 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.b` |
| 33 | P table/abstract | 3 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.c` |
| 34 | P table/abstract | 4 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.n_d` |
| 35 | P table/abstract | -0.004 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.delta` |
| 36 | P table/abstract | [-0.01, 0.002] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.ci90` |
| 37 | P table/abstract | [-0.012, 0.004] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.ci95` |
| 38 | P table/abstract | [-0.014, 0.004] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.ci9833` |
| 39 | P table/abstract | 0.625 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.p` |
| 40 | P table/abstract | 1 | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.p_holm` |
| 41 | P table/abstract | [0.00630946, 0.80588] | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.theta_cp95` |
| 42 | P table/abstract | True | `runs/P2-GATE-M4/analysis.json` | `primary.per_corruption.splice.equivalent_within_0p05` |
| 43 | P | 3 | `runs/P2-GATE-M4/analysis.json` | `primary.holm_m` |
| 44 | P | negative | `runs/P2-GATE-M4/analysis.json` | `outcome.label` |
| 45 | P | R2 | `runs/P2-GATE-M4/analysis.json` | `rule` |
| 46 | P | 500 | `runs/P2-GATE-M4/analysis.json` | `n_items` |
| 47 | P | 500 | `runs/P2-GATE-M4/analysis.json` | `completeness.completed_n` |
| 48 | P | 0 | `runs/P2-GATE-M4/analysis.json` | `completeness.n_excluded_token_rule` |
| 49 | P | False | `runs/P2-GATE-M4/analysis.json` | `completeness.K7` |
| 50 | headroom table | 99 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg10.n_v` |
| 51 | headroom table | 6.02902 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg10.T1` |
| 52 | headroom table | 3.29973 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg10.T2` |
| 53 | headroom table | True | `runs/P2-GATE-M3/family.json` | `rungs.jpeg10.passes` |
| 54 | headroom table | 986.7 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg10.mean_n_changed` |
| 55 | headroom table | 0.06 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg10.acc_drop_binary` |
| 56 | headroom table | 19 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg10.discordance_chg_vs_none.D_c` |
| 57 | headroom (z sensitivity) | -6.56406 | `runs/P2-GATE-M3/family.json` | `sensitivity_other_endpoint.z.jpeg10.T2` |
| 58 | headroom table | 95 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg5.n_v` |
| 59 | headroom table | 5.15903 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg5.T1` |
| 60 | headroom table | 1.53819 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg5.T2` |
| 61 | headroom table | False | `runs/P2-GATE-M3/family.json` | `rungs.jpeg5.passes` |
| 62 | headroom table | 1010.49 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg5.mean_n_changed` |
| 63 | headroom table | 0.04 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg5.acc_drop_binary` |
| 64 | headroom table | 26 | `runs/P2-GATE-M3/family.json` | `rungs.jpeg5.discordance_chg_vs_none.D_c` |
| 65 | headroom (z sensitivity) | -6.74606 | `runs/P2-GATE-M3/family.json` | `sensitivity_other_endpoint.z.jpeg5.T2` |
| 66 | headroom table | 100 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.1.n_v` |
| 67 | headroom table | 4.20356 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.1.T1` |
| 68 | headroom table | 4.38402 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.1.T2` |
| 69 | headroom table | True | `runs/P2-GATE-M3/family.json` | `rungs.noise0.1.passes` |
| 70 | headroom table | 949.37 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.1.mean_n_changed` |
| 71 | headroom table | 0.14 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.1.acc_drop_binary` |
| 72 | headroom table | 18 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.1.discordance_chg_vs_none.D_c` |
| 73 | headroom (z sensitivity) | -3.92448 | `runs/P2-GATE-M3/family.json` | `sensitivity_other_endpoint.z.noise0.1.T2` |
| 74 | headroom table | 100 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.2.n_v` |
| 75 | headroom table | 3.79105 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.2.T1` |
| 76 | headroom table | 4.27232 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.2.T2` |
| 77 | headroom table | True | `runs/P2-GATE-M3/family.json` | `rungs.noise0.2.passes` |
| 78 | headroom table | 998.36 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.2.mean_n_changed` |
| 79 | headroom table | 0.22 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.2.acc_drop_binary` |
| 80 | headroom table | 19 | `runs/P2-GATE-M3/family.json` | `rungs.noise0.2.discordance_chg_vs_none.D_c` |
| 81 | headroom (z sensitivity) | -2.86497 | `runs/P2-GATE-M3/family.json` | `sensitivity_other_endpoint.z.noise0.2.T2` |
| 82 | headroom table | 100 | `runs/P2-GATE-M3/family.json` | `rungs.splice128.n_v` |
| 83 | headroom table | 5.32531 | `runs/P2-GATE-M3/family.json` | `rungs.splice128.T1` |
| 84 | headroom table | 4.04772 | `runs/P2-GATE-M3/family.json` | `rungs.splice128.T2` |
| 85 | headroom table | True | `runs/P2-GATE-M3/family.json` | `rungs.splice128.passes` |
| 86 | headroom table | 237.19 | `runs/P2-GATE-M3/family.json` | `rungs.splice128.mean_n_changed` |
| 87 | headroom table | 0.01 | `runs/P2-GATE-M3/family.json` | `rungs.splice128.acc_drop_binary` |
| 88 | headroom table | 2 | `runs/P2-GATE-M3/family.json` | `rungs.splice128.discordance_chg_vs_none.D_c` |
| 89 | headroom (z sensitivity) | -3.54596 | `runs/P2-GATE-M3/family.json` | `sensitivity_other_endpoint.z.splice128.T2` |
| 90 | headroom table | 100 | `runs/P2-GATE-M3/family.json` | `rungs.splice192.n_v` |
| 91 | headroom table | 7.93074 | `runs/P2-GATE-M3/family.json` | `rungs.splice192.T1` |
| 92 | headroom table | 7.33532 | `runs/P2-GATE-M3/family.json` | `rungs.splice192.T2` |
| 93 | headroom table | True | `runs/P2-GATE-M3/family.json` | `rungs.splice192.passes` |
| 94 | headroom table | 387.65 | `runs/P2-GATE-M3/family.json` | `rungs.splice192.mean_n_changed` |
| 95 | headroom table | 0.03 | `runs/P2-GATE-M3/family.json` | `rungs.splice192.acc_drop_binary` |
| 96 | headroom table | 3 | `runs/P2-GATE-M3/family.json` | `rungs.splice192.discordance_chg_vs_none.D_c` |
| 97 | headroom (z sensitivity) | -0.0899216 | `runs/P2-GATE-M3/family.json` | `sensitivity_other_endpoint.z.splice192.T2` |
| 98 | headroom | 19 | `runs/P2-GATE-M3/family.json` | `n_rule.D_star` |
| 99 | headroom | R2 | `runs/P2-GATE-M3/family.json` | `n_rule.rule` |
| 100 | headroom | 500 | `runs/P2-GATE-M3/family.json` | `n_rule.test_fold` |
| 101 | headroom | 100 | `runs/P2-GATE-M3/family.json` | `n_headroom_items` |
| 102 | mechanism table (Y) | 1.11022e-19 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_geo.diff` |
| 103 | mechanism table (Y) | -0.002 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_geo.lo` |
| 104 | mechanism table (Y) | 0.002 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_geo.hi` |
| 105 | mechanism table (Y) | -0.002 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_scattered.diff` |
| 106 | mechanism table (Y) | -0.00733333 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_scattered.lo` |
| 107 | mechanism table (Y) | 0.00133333 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_scattered.hi` |
| 108 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_topkB.diff` |
| 109 | mechanism table (Y) | -0.006 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_topkB.lo` |
| 110 | mechanism table (Y) | 0.006 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_topkB.hi` |
| 111 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_topks3.diff` |
| 112 | mechanism table (Y) | -0.008 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_topks3.lo` |
| 113 | mechanism table (Y) | 0.008 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_topks3.hi` |
| 114 | mechanism table (Y) | 0.082 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_changed_code.diff` |
| 115 | mechanism table (Y) | 0.044 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_changed_code.lo` |
| 116 | mechanism table (Y) | 0.12 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.gate_minus_changed_code.hi` |
| 117 | mechanism table (Y) | -0.084 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.changed_code_minus_none.diff` |
| 118 | mechanism table (Y) | -0.122 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.changed_code_minus_none.lo` |
| 119 | mechanism table (Y) | -0.046 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.y.changed_code_minus_none.hi` |
| 120 | mechanism text (d) | 0.00910521 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_geo.diff` |
| 121 | mechanism text (d) | 0.0078457 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_geo.lo` |
| 122 | mechanism text (d) | 0.0103813 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_geo.hi` |
| 123 | mechanism text (d) | 0.000818615 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_topkB.diff` |
| 124 | mechanism text (d) | 0.000102214 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_topkB.lo` |
| 125 | mechanism text (d) | 0.00154173 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_topkB.hi` |
| 126 | mechanism text (d) | 0.00508064 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_topks3.diff` |
| 127 | mechanism text (d) | 0.00353588 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_topks3.lo` |
| 128 | mechanism text (d) | 0.00669346 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_topks3.hi` |
| 129 | mechanism table (Y) | 0.000666667 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_geo.diff` |
| 130 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_geo.lo` |
| 131 | mechanism table (Y) | 0.002 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_geo.hi` |
| 132 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_scattered.diff` |
| 133 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_scattered.lo` |
| 134 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_scattered.hi` |
| 135 | mechanism table (Y) | -0.002 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_topkB.diff` |
| 136 | mechanism table (Y) | -0.006 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_topkB.lo` |
| 137 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_topkB.hi` |
| 138 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_topks3.diff` |
| 139 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_topks3.lo` |
| 140 | mechanism table (Y) | 0 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_topks3.hi` |
| 141 | mechanism table (Y) | -0.07 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_changed_code.diff` |
| 142 | mechanism table (Y) | -0.104 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_changed_code.lo` |
| 143 | mechanism table (Y) | -0.036 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.gate_minus_changed_code.hi` |
| 144 | mechanism table (Y) | 0.07 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.changed_code_minus_none.diff` |
| 145 | mechanism table (Y) | 0.036 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.changed_code_minus_none.lo` |
| 146 | mechanism table (Y) | 0.104 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.y.changed_code_minus_none.hi` |
| 147 | mechanism text (d) | 0.00397759 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_geo.diff` |
| 148 | mechanism text (d) | 0.00302813 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_geo.lo` |
| 149 | mechanism text (d) | 0.00491727 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_geo.hi` |
| 150 | mechanism text (d) | 0.000300601 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_topkB.diff` |
| 151 | mechanism text (d) | -0.000107784 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_topkB.lo` |
| 152 | mechanism text (d) | 0.000712177 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_topkB.hi` |
| 153 | mechanism text (d) | 0.00328297 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_topks3.diff` |
| 154 | mechanism text (d) | 0.00218845 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_topks3.lo` |
| 155 | mechanism text (d) | 0.00436042 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_topks3.hi` |
| 156 | mechanism table (Y) | -0.000666667 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_geo.diff` |
| 157 | mechanism table (Y) | -0.00866667 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_geo.lo` |
| 158 | mechanism table (Y) | 0.00733333 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_geo.hi` |
| 159 | mechanism table (Y) | -0.004 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_scattered.diff` |
| 160 | mechanism table (Y) | -0.0113333 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_scattered.lo` |
| 161 | mechanism table (Y) | 0.002 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_scattered.hi` |
| 162 | mechanism table (Y) | -0.008 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_topkB.diff` |
| 163 | mechanism table (Y) | -0.016 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_topkB.lo` |
| 164 | mechanism table (Y) | -0.002 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_topkB.hi` |
| 165 | mechanism table (Y) | -0.006 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_topks3.diff` |
| 166 | mechanism table (Y) | -0.016 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_topks3.lo` |
| 167 | mechanism table (Y) | 0.002 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_topks3.hi` |
| 168 | mechanism table (Y) | -0.008 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_changed_code.diff` |
| 169 | mechanism table (Y) | -0.022 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_changed_code.lo` |
| 170 | mechanism table (Y) | 0.006 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.gate_minus_changed_code.hi` |
| 171 | mechanism table (Y) | 0.004 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.changed_code_minus_none.diff` |
| 172 | mechanism table (Y) | -0.01 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.changed_code_minus_none.lo` |
| 173 | mechanism table (Y) | 0.018 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.y.changed_code_minus_none.hi` |
| 174 | mechanism text (d) | 0.00813022 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_geo.diff` |
| 175 | mechanism text (d) | 0.00708122 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_geo.lo` |
| 176 | mechanism text (d) | 0.00917121 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_geo.hi` |
| 177 | mechanism text (d) | 0.000513101 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_topkB.diff` |
| 178 | mechanism text (d) | -8.96323e-05 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_topkB.lo` |
| 179 | mechanism text (d) | 0.00110896 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_topkB.hi` |
| 180 | mechanism text (d) | 0.00450026 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_topks3.diff` |
| 181 | mechanism text (d) | 0.00325618 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_topks3.lo` |
| 182 | mechanism text (d) | 0.00573405 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_topks3.hi` |
| 183 | S-M | False | `runs/P2-GATE-M4/analysis.json` | `s_m.per_corruption.jpeg.tested` |
| 184 | S-M | False | `runs/P2-GATE-M4/analysis.json` | `s_m.per_corruption.noise.tested` |
| 185 | S-M | False | `runs/P2-GATE-M4/analysis.json` | `s_m.per_corruption.splice.tested` |
| 186 | S-Z | 0.00896755 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.jpeg.ci.diff` |
| 187 | S-Z | 0.00781283 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.jpeg.ci.lo` |
| 188 | S-Z | 0.0101501 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.jpeg.ci.hi` |
| 189 | S-Z | 1.92623e-39 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.jpeg.p_holm` |
| 190 | S-Z z sensitivity | 0.0562324 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.jpeg.sensitivity_other_endpoint.z.ci.diff` |
| 191 | S-Z z sensitivity | 0.0246979 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.jpeg.sensitivity_other_endpoint.z.ci.lo` |
| 192 | S-Z z sensitivity | 0.087205 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.jpeg.sensitivity_other_endpoint.z.ci.hi` |
| 193 | S-Z z sensitivity | 0.000247781 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.jpeg.sensitivity_other_endpoint.z.p` |
| 194 | S-Z | 0.00381095 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.noise.ci.diff` |
| 195 | S-Z | 0.00296042 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.noise.ci.lo` |
| 196 | S-Z | 0.00468118 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.noise.ci.hi` |
| 197 | S-Z | 8.47485e-16 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.noise.p_holm` |
| 198 | S-Z z sensitivity | 0.01105 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.noise.sensitivity_other_endpoint.z.ci.diff` |
| 199 | S-Z z sensitivity | -0.0115101 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.noise.sensitivity_other_endpoint.z.ci.lo` |
| 200 | S-Z z sensitivity | 0.0342127 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.noise.sensitivity_other_endpoint.z.ci.hi` |
| 201 | S-Z z sensitivity | 0.350143 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.noise.sensitivity_other_endpoint.z.p` |
| 202 | S-Z | 0.00780449 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.splice.ci.diff` |
| 203 | S-Z | 0.00687933 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.splice.ci.lo` |
| 204 | S-Z | 0.00874662 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.splice.ci.hi` |
| 205 | S-Z | 2.88053e-43 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.splice.p_holm` |
| 206 | S-Z z sensitivity | 0.0415447 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.splice.sensitivity_other_endpoint.z.ci.diff` |
| 207 | S-Z z sensitivity | 0.0172402 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.splice.sensitivity_other_endpoint.z.ci.lo` |
| 208 | S-Z z sensitivity | 0.0662735 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.splice.sensitivity_other_endpoint.z.ci.hi` |
| 209 | S-Z z sensitivity | 0.00118591 | `runs/P2-GATE-M4/analysis.json` | `s_z.per_corruption.splice.sensitivity_other_endpoint.z.p` |
| 210 | S-Z clean z | 0.0581107 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.gate_on_clean.z.diff` |
| 211 | S-Z clean z | 0.031511 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.gate_on_clean.z.lo` |
| 212 | S-Z clean z | 0.0845743 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.gate_on_clean.z.hi` |
| 213 | S-DN | 0.836 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.jpeg.acc_a` |
| 214 | S-DN | 0.844 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.jpeg.acc_b` |
| 215 | S-DN | 38 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.jpeg.b` |
| 216 | S-DN | 42 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.jpeg.c` |
| 217 | S-DN | -0.008 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.jpeg.delta` |
| 218 | S-DN | [-0.042, 0.026] | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.jpeg.ci95` |
| 219 | S-DN | 0.737554 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.jpeg.p_holm` |
| 220 | S-DN | 0.676 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.noise.acc_a` |
| 221 | S-DN | 0.852 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.noise.acc_b` |
| 222 | S-DN | 34 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.noise.b` |
| 223 | S-DN | 122 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.noise.c` |
| 224 | S-DN | -0.176 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.noise.delta` |
| 225 | S-DN | [-0.224, -0.13] | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.noise.ci95` |
| 226 | S-DN | 1.54283e-12 | `runs/P2-GATE-M4/analysis.json` | `s_dn.per_corruption.noise.p_holm` |
| 227 | S-C | 0.882 | `runs/P2-GATE-M4/analysis.json` | `s_c.acc_a` |
| 228 | S-C | 0.88 | `runs/P2-GATE-M4/analysis.json` | `s_c.acc_b` |
| 229 | S-C | 2 | `runs/P2-GATE-M4/analysis.json` | `s_c.b` |
| 230 | S-C | 1 | `runs/P2-GATE-M4/analysis.json` | `s_c.c` |
| 231 | S-C | 0.002 | `runs/P2-GATE-M4/analysis.json` | `s_c.delta` |
| 232 | S-C | [-0.004, 0.01] | `runs/P2-GATE-M4/analysis.json` | `s_c.ci95` |
| 233 | S-C | 1 | `runs/P2-GATE-M4/analysis.json` | `s_c.p` |
| 234 | C1 test | 0.88 | `runs/P2-GATE-M4/analysis.json` | `c1_test.accuracy` |
| 235 | C1 test | [0.84858, 0.905625] | `runs/P2-GATE-M4/analysis.json` | `c1_test.wilson95` |
| 236 | C1 test | 500 | `runs/P2-GATE-M4/analysis.json` | `c1_test.n` |
| 237 | C1 probe1 | 0.843333 | `runs/P2-GATE-M4/analysis.json` | `c1_test.probe1.accuracy` |
| 238 | C1 probe1 | [0.798, 0.88] | `runs/P2-GATE-M4/analysis.json` | `c1_test.probe1.wilson95` |
| 239 | C1 cal | 0.88 | `runs/P2-GATE-M2/c1_cal.json` | `accuracy` |
| 240 | C1 cal | [0.838342, 0.912049] | `runs/P2-GATE-M2/c1_cal.json` | `wilson95` |
| 241 | C1 head | 0.86 | `runs/P2-GATE-M3/c1_head.json` | `accuracy` |
| 242 | C1 head | [0.778628, 0.914737] | `runs/P2-GATE-M3/c1_head.json` | `wilson95` |
| 243 | calibration table | 0.00641602 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.01.F` |
| 244 | calibration table | [0.00614839, 0.0066875] | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.01.ci_bootstrap` |
| 245 | calibration table | -16.125 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.01.Z_cal` |
| 246 | calibration table | False | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.01.violation` |
| 247 | calibration table | 300 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.01.n_cal` |
| 248 | calibration table | 500 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.01.n_test` |
| 249 | calibration (threshold) | 0.00669922 | `runs/P2-GATE-M2/threshold.json` | `thresholds.0.01.r_hat` |
| 250 | calibration table | 0.045623 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.05.F` |
| 251 | calibration table | [0.0442402, 0.0470371] | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.05.ci_bootstrap` |
| 252 | calibration table | -3.59264 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.05.Z_cal` |
| 253 | calibration table | False | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.05.violation` |
| 254 | calibration table | 300 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.05.n_cal` |
| 255 | calibration table | 500 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.05.n_test` |
| 256 | calibration (threshold) | 0.0468327 | `runs/P2-GATE-M2/threshold.json` | `thresholds.0.05.r_hat` |
| 257 | calibration table | 0.0956484 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.1.F` |
| 258 | calibration table | [0.0928085, 0.0985059] | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.1.ci_bootstrap` |
| 259 | calibration table | -1.76259 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.1.Z_cal` |
| 260 | calibration table | False | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.1.violation` |
| 261 | calibration table | 300 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.1.n_cal` |
| 262 | calibration table | 500 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.per_alpha.0.1.n_test` |
| 263 | calibration (threshold) | 0.0969987 | `runs/P2-GATE-M2/threshold.json` | `thresholds.0.1.r_hat` |
| 264 | calibration | 2.13 | `runs/P2-GATE-M4/analysis.json` | `calibration.fap_check.critical_value` |
| 265 | calibration split replication | 2000 | `runs/P2-GATE-M4/analysis.json` | `calibration.split_replication.reps` |
| 266 | calibration split replication | -0.00313016 | `runs/P2-GATE-M4/analysis.json` | `calibration.split_replication.mean_F_minus_alpha` |
| 267 | calibration split replication | -0.0055061 | `runs/P2-GATE-M4/analysis.json` | `calibration.split_replication.q025` |
| 268 | calibration split replication | -0.000624902 | `runs/P2-GATE-M4/analysis.json` | `calibration.split_replication.q975` |
| 269 | flag table | 0.975679 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.precision` |
| 270 | flag table | 0.0612549 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.recall` |
| 271 | flag table | 0.0372631 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.fap_on_clean_tokens` |
| 272 | flag table | 0.960637 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.rho` |
| 273 | flag table | 0.922106 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.precision` |
| 274 | flag table | 0.032879 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.recall` |
| 275 | flag table | 0.0359262 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.fap_on_clean_tokens` |
| 276 | flag table | 0.928238 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.rho` |
| 277 | flag table | 0.248053 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.precision` |
| 278 | flag table | 0.0490872 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.recall` |
| 279 | flag table | 0.0436471 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.fap_on_clean_tokens` |
| 280 | flag table | 0.226797 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.rho` |
| 281 | flag table | 0.497678 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.patch.precision` |
| 282 | flag table | 0.750211 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.patch.recall` |
| 283 | flag table | 0.0504791 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.patch.fap_on_clean_tokens` |
| 284 | flag table | 0.062498 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.patch.prop4.rho` |
| 285 | flag table | 0.630805 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.swap.precision` |
| 286 | flag table | 0.858946 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.swap.recall` |
| 287 | flag table | 0.088986 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.swap.fap_on_clean_tokens` |
| 288 | flag table | 0.150389 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.swap.prop4.rho` |
| 289 | PS table | 500 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.n` |
| 290 | PS table | 0.87 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.acc_b` |
| 291 | PS table | 0.87 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.acc_a` |
| 292 | PS table | 2 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.b` |
| 293 | PS table | 2 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.c` |
| 294 | PS table | 4 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.n_d` |
| 295 | PS table | 0 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.delta` |
| 296 | PS table | [-0.008, 0.008] | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.ci95` |
| 297 | PS table | [-0.01, 0.01] | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.ci9833` |
| 298 | PS table | 1 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.p` |
| 299 | PS table | 1 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.p_holm` |
| 300 | PS table | [0.067586, 0.932414] | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.theta_cp95` |
| 301 | PS table | False | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.right_sign` |
| 302 | PS table | 500 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.n` |
| 303 | PS table | 0.87 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.acc_b` |
| 304 | PS table | 0.876 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.acc_a` |
| 305 | PS table | 8 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.b` |
| 306 | PS table | 5 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.c` |
| 307 | PS table | 13 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.n_d` |
| 308 | PS table | 0.006 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.delta` |
| 309 | PS table | [-0.008, 0.02] | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.ci95` |
| 310 | PS table | [-0.012, 0.024] | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.ci9833` |
| 311 | PS table | 0.581055 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.p` |
| 312 | PS table | 1 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.p_holm` |
| 313 | PS table | [0.315778, 0.861421] | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.theta_cp95` |
| 314 | PS table | True | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.right_sign` |
| 315 | PS | not met | `runs/P2-GATE-M4/analysis.json` | `ps.positive_control` |
| 316 | PS | 0 | `runs/P2-GATE-M4/analysis.json` | `ps.n_rejected_right_sign` |
| 317 | PS | 0.88 | `runs/P2-GATE-M4/analysis.json` | `c1_test.accuracy` |
| 318 | S-D2 | 0.560913 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.jpeg.auroc_q` |
| 319 | S-D2 | 0.759019 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.jpeg.auroc_rival` |
| 320 | S-D2 | -0.198106 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.jpeg.diff_mean` |
| 321 | S-D2 | [-0.210721, -0.18562] | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.jpeg.ci95` |
| 322 | S-D2 | 0.00039996 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.jpeg.p_holm` |
| 323 | S-D2 | 492 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.jpeg.n_eligible` |
| 324 | S-D2 | 8 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.jpeg.n_excluded` |
| 325 | S-D2 | tex_neg | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.jpeg.rival` |
| 326 | S-D2 | 0.509302 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.noise.auroc_q` |
| 327 | S-D2 | 0.767478 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.noise.auroc_rival` |
| 328 | S-D2 | -0.258175 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.noise.diff_mean` |
| 329 | S-D2 | [-0.266771, -0.249662] | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.noise.ci95` |
| 330 | S-D2 | 0.00039996 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.noise.p_holm` |
| 331 | S-D2 | 497 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.noise.n_eligible` |
| 332 | S-D2 | 3 | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.noise.n_excluded` |
| 333 | S-D2 | tex_neg | `runs/P2-GATE-M4/analysis.json` | `s_d2.per_corruption.noise.rival` |
| 334 | S-D (M1) | 0.96107 | `runs/P2-GATE-M1/analysis.json` | `table.patch.q.mean` |
| 335 | S-D (M1) | 0.958797 | `runs/P2-GATE-M1/analysis.json` | `table.patch.q.lo` |
| 336 | S-D (M1) | 0.963297 | `runs/P2-GATE-M1/analysis.json` | `table.patch.q.hi` |
| 337 | S-D (M1) | 200 | `runs/P2-GATE-M1/analysis.json` | `table.patch.q.n` |
| 338 | S-D (M1) | 0.964411 | `runs/P2-GATE-M1/analysis.json` | `table.patch.plainB.mean` |
| 339 | S-D (M1) | 0.962359 | `runs/P2-GATE-M1/analysis.json` | `table.patch.plainB.lo` |
| 340 | S-D (M1) | 0.966416 | `runs/P2-GATE-M1/analysis.json` | `table.patch.plainB.hi` |
| 341 | S-D (M1) | 200 | `runs/P2-GATE-M1/analysis.json` | `table.patch.plainB.n` |
| 342 | S-D (M1) | 0.854005 | `runs/P2-GATE-M1/analysis.json` | `table.patch.tbv.mean` |
| 343 | S-D (M1) | 0.84702 | `runs/P2-GATE-M1/analysis.json` | `table.patch.tbv.lo` |
| 344 | S-D (M1) | 0.860776 | `runs/P2-GATE-M1/analysis.json` | `table.patch.tbv.hi` |
| 345 | S-D (M1) | 200 | `runs/P2-GATE-M1/analysis.json` | `table.patch.tbv.n` |
| 346 | S-D (M1) | 0.78627 | `runs/P2-GATE-M1/analysis.json` | `table.patch.nbr.mean` |
| 347 | S-D (M1) | 0.777817 | `runs/P2-GATE-M1/analysis.json` | `table.patch.nbr.lo` |
| 348 | S-D (M1) | 0.794582 | `runs/P2-GATE-M1/analysis.json` | `table.patch.nbr.hi` |
| 349 | S-D (M1) | 200 | `runs/P2-GATE-M1/analysis.json` | `table.patch.nbr.n` |
| 350 | S-D (M1) | 0.95451 | `runs/P2-GATE-M1/analysis.json` | `table.swap.q.mean` |
| 351 | S-D (M1) | 0.952049 | `runs/P2-GATE-M1/analysis.json` | `table.swap.q.lo` |
| 352 | S-D (M1) | 0.956982 | `runs/P2-GATE-M1/analysis.json` | `table.swap.q.hi` |
| 353 | S-D (M1) | 200 | `runs/P2-GATE-M1/analysis.json` | `table.swap.q.n` |
| 354 | S-D (M1) | 0.959775 | `runs/P2-GATE-M1/analysis.json` | `table.swap.plainB.mean` |
| 355 | S-D (M1) | 0.957503 | `runs/P2-GATE-M1/analysis.json` | `table.swap.plainB.lo` |
| 356 | S-D (M1) | 0.962036 | `runs/P2-GATE-M1/analysis.json` | `table.swap.plainB.hi` |
| 357 | S-D (M1) | 200 | `runs/P2-GATE-M1/analysis.json` | `table.swap.plainB.n` |
| 358 | S-D (M1) | 0.858844 | `runs/P2-GATE-M1/analysis.json` | `table.swap.tbv.mean` |
| 359 | S-D (M1) | 0.853931 | `runs/P2-GATE-M1/analysis.json` | `table.swap.tbv.lo` |
| 360 | S-D (M1) | 0.863624 | `runs/P2-GATE-M1/analysis.json` | `table.swap.tbv.hi` |
| 361 | S-D (M1) | 200 | `runs/P2-GATE-M1/analysis.json` | `table.swap.tbv.n` |
| 362 | S-D (M1) | 0.740788 | `runs/P2-GATE-M1/analysis.json` | `table.swap.nbr.mean` |
| 363 | S-D (M1) | 0.733518 | `runs/P2-GATE-M1/analysis.json` | `table.swap.nbr.lo` |
| 364 | S-D (M1) | 0.747967 | `runs/P2-GATE-M1/analysis.json` | `table.swap.nbr.hi` |
| 365 | S-D (M1) | 200 | `runs/P2-GATE-M1/analysis.json` | `table.swap.nbr.n` |
| 366 | S-D (M1) | 0.561263 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.q.mean` |
| 367 | S-D (M1) | 0.547311 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.q.lo` |
| 368 | S-D (M1) | 0.574956 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.q.hi` |
| 369 | S-D (M1) | 197 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.q.n` |
| 370 | S-D (M1) | 0.560495 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.plainB.mean` |
| 371 | S-D (M1) | 0.545587 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.plainB.lo` |
| 372 | S-D (M1) | 0.574781 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.plainB.hi` |
| 373 | S-D (M1) | 197 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.plainB.n` |
| 374 | S-D (M1) | 0.581041 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.tbv.mean` |
| 375 | S-D (M1) | 0.569002 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.tbv.lo` |
| 376 | S-D (M1) | 0.592934 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.tbv.hi` |
| 377 | S-D (M1) | 197 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.tbv.n` |
| 378 | S-D (M1) | 0.44406 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.nbr.mean` |
| 379 | S-D (M1) | 0.431244 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.nbr.lo` |
| 380 | S-D (M1) | 0.457526 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.nbr.hi` |
| 381 | S-D (M1) | 197 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.nbr.n` |
| 382 | S-D (M1) | 0.502809 | `runs/P2-GATE-M1/analysis.json` | `table.noise.q.mean` |
| 383 | S-D (M1) | 0.492508 | `runs/P2-GATE-M1/analysis.json` | `table.noise.q.lo` |
| 384 | S-D (M1) | 0.513391 | `runs/P2-GATE-M1/analysis.json` | `table.noise.q.hi` |
| 385 | S-D (M1) | 198 | `runs/P2-GATE-M1/analysis.json` | `table.noise.q.n` |
| 386 | S-D (M1) | 0.510812 | `runs/P2-GATE-M1/analysis.json` | `table.noise.plainB.mean` |
| 387 | S-D (M1) | 0.500601 | `runs/P2-GATE-M1/analysis.json` | `table.noise.plainB.lo` |
| 388 | S-D (M1) | 0.521426 | `runs/P2-GATE-M1/analysis.json` | `table.noise.plainB.hi` |
| 389 | S-D (M1) | 198 | `runs/P2-GATE-M1/analysis.json` | `table.noise.plainB.n` |
| 390 | S-D (M1) | 0.607361 | `runs/P2-GATE-M1/analysis.json` | `table.noise.tbv.mean` |
| 391 | S-D (M1) | 0.59721 | `runs/P2-GATE-M1/analysis.json` | `table.noise.tbv.lo` |
| 392 | S-D (M1) | 0.617751 | `runs/P2-GATE-M1/analysis.json` | `table.noise.tbv.hi` |
| 393 | S-D (M1) | 198 | `runs/P2-GATE-M1/analysis.json` | `table.noise.tbv.n` |
| 394 | S-D (M1) | 0.353727 | `runs/P2-GATE-M1/analysis.json` | `table.noise.nbr.mean` |
| 395 | S-D (M1) | 0.34367 | `runs/P2-GATE-M1/analysis.json` | `table.noise.nbr.lo` |
| 396 | S-D (M1) | 0.364075 | `runs/P2-GATE-M1/analysis.json` | `table.noise.nbr.hi` |
| 397 | S-D (M1) | 198 | `runs/P2-GATE-M1/analysis.json` | `table.noise.nbr.n` |
| 398 | S-D (M1) rival | 0.755779 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.tex_neg.mean` |
| 399 | S-D (M1) rival | 0.742946 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.tex_neg.lo` |
| 400 | S-D (M1) rival | 0.767621 | `runs/P2-GATE-M1/analysis.json` | `table.jpeg.tex_neg.hi` |
| 401 | S-D (M1) falsifier | -0.194516 | `runs/P2-GATE-M1/analysis.json` | `falsifier.per_corruption.jpeg.diff_mean` |
| 402 | S-D (M1) falsifier | [-0.214091, -0.174808] | `runs/P2-GATE-M1/analysis.json` | `falsifier.per_corruption.jpeg.ci95` |
| 403 | S-D (M1) falsifier | 0.00039996 | `runs/P2-GATE-M1/analysis.json` | `falsifier.per_corruption.jpeg.p_holm` |
| 404 | S-D (M1) rival | 0.768114 | `runs/P2-GATE-M1/analysis.json` | `table.noise.tex_neg.mean` |
| 405 | S-D (M1) rival | 0.759728 | `runs/P2-GATE-M1/analysis.json` | `table.noise.tex_neg.lo` |
| 406 | S-D (M1) rival | 0.776481 | `runs/P2-GATE-M1/analysis.json` | `table.noise.tex_neg.hi` |
| 407 | S-D (M1) falsifier | -0.265305 | `runs/P2-GATE-M1/analysis.json` | `falsifier.per_corruption.noise.diff_mean` |
| 408 | S-D (M1) falsifier | [-0.278221, -0.252673] | `runs/P2-GATE-M1/analysis.json` | `falsifier.per_corruption.noise.ci95` |
| 409 | S-D (M1) falsifier | 0.00039996 | `runs/P2-GATE-M1/analysis.json` | `falsifier.per_corruption.noise.p_holm` |
| 410 | S-D (M1) q-plainB | -0.00334091 | `runs/P2-GATE-M1/analysis.json` | `paired_q_vs_best_cheap.patch.diff_mean` |
| 411 | S-D (M1) q-plainB | [-0.00415044, -0.00256559] | `runs/P2-GATE-M1/analysis.json` | `paired_q_vs_best_cheap.patch.ci95` |
| 412 | S-D (M1) q-plainB | -0.00526575 | `runs/P2-GATE-M1/analysis.json` | `paired_q_vs_best_cheap.swap.diff_mean` |
| 413 | S-D (M1) q-plainB | [-0.0058387, -0.00474353] | `runs/P2-GATE-M1/analysis.json` | `paired_q_vs_best_cheap.swap.ci95` |
| 414 | S-D (M1) | 179 | `runs/P2-GATE-M1/analysis.json` | `falsifier_excluding_dry_run_items.n_items` |
| 415 | E-dec | 498 | `runs/P2-GATE-M4/edec.json` | `cells.P1.n_complete` |
| 416 | E-dec table (accuracy) | 0.0441767 | `runs/P2-GATE-M4/edec.json` | `cells.P1.accuracy_scale.tau.T.mean` |
| 417 | E-dec table (accuracy) | [0.0180723, 0.0702811] | `runs/P2-GATE-M4/edec.json` | `cells.P1.accuracy_scale.tau.T.ci95` |
| 418 | E-dec text (d) | 0.0611951 | `runs/P2-GATE-M4/edec.json` | `cells.P1.d_scale.tau.T.mean` |
| 419 | E-dec text (d) | [0.0476081, 0.0747345] | `runs/P2-GATE-M4/edec.json` | `cells.P1.d_scale.tau.T.ci95` |
| 420 | E-dec table (accuracy) | 0.124498 | `runs/P2-GATE-M4/edec.json` | `cells.P1.accuracy_scale.tau.U.mean` |
| 421 | E-dec table (accuracy) | [0.0883534, 0.160643] | `runs/P2-GATE-M4/edec.json` | `cells.P1.accuracy_scale.tau.U.ci95` |
| 422 | E-dec text (d) | -0.0209199 | `runs/P2-GATE-M4/edec.json` | `cells.P1.d_scale.tau.U.mean` |
| 423 | E-dec text (d) | [-0.0604196, 0.0147865] | `runs/P2-GATE-M4/edec.json` | `cells.P1.d_scale.tau.U.ci95` |
| 424 | E-dec table (accuracy) | -0.00200803 | `runs/P2-GATE-M4/edec.json` | `cells.P1.accuracy_scale.tau.R.mean` |
| 425 | E-dec table (accuracy) | [-0.0060241, 0] | `runs/P2-GATE-M4/edec.json` | `cells.P1.accuracy_scale.tau.R.ci95` |
| 426 | E-dec text (d) | 0.0089597 | `runs/P2-GATE-M4/edec.json` | `cells.P1.d_scale.tau.R.mean` |
| 427 | E-dec text (d) | [0.00780672, 0.0101397] | `runs/P2-GATE-M4/edec.json` | `cells.P1.d_scale.tau.R.ci95` |
| 428 | E-dec table (accuracy) | -0.0783133 | `runs/P2-GATE-M4/edec.json` | `cells.P1.accuracy_scale.tau.V.mean` |
| 429 | E-dec table (accuracy) | [-0.116466, -0.0401606] | `runs/P2-GATE-M4/edec.json` | `cells.P1.accuracy_scale.tau.V.ci95` |
| 430 | E-dec text (d) | 0.0731553 | `runs/P2-GATE-M4/edec.json` | `cells.P1.d_scale.tau.V.mean` |
| 431 | E-dec text (d) | [0.0354857, 0.114886] | `runs/P2-GATE-M4/edec.json` | `cells.P1.d_scale.tau.V.ci95` |
| 432 | E-dec | 500 | `runs/P2-GATE-M4/edec.json` | `cells.P2.n_complete` |
| 433 | E-dec table (accuracy) | 0.204 | `runs/P2-GATE-M4/edec.json` | `cells.P2.accuracy_scale.tau.T.mean` |
| 434 | E-dec table (accuracy) | [0.166, 0.244] | `runs/P2-GATE-M4/edec.json` | `cells.P2.accuracy_scale.tau.T.ci95` |
| 435 | E-dec text (d) | 0.119353 | `runs/P2-GATE-M4/edec.json` | `cells.P2.d_scale.tau.T.mean` |
| 436 | E-dec text (d) | [0.0985222, 0.141123] | `runs/P2-GATE-M4/edec.json` | `cells.P2.d_scale.tau.T.ci95` |
| 437 | E-dec table (accuracy) | 0.134 | `runs/P2-GATE-M4/edec.json` | `cells.P2.accuracy_scale.tau.U.mean` |
| 438 | E-dec table (accuracy) | [0.098, 0.172] | `runs/P2-GATE-M4/edec.json` | `cells.P2.accuracy_scale.tau.U.ci95` |
| 439 | E-dec text (d) | 0.0328592 | `runs/P2-GATE-M4/edec.json` | `cells.P2.d_scale.tau.U.mean` |
| 440 | E-dec text (d) | [-0.00568931, 0.0783742] | `runs/P2-GATE-M4/edec.json` | `cells.P2.d_scale.tau.U.ci95` |
| 441 | E-dec table (accuracy) | 0 | `runs/P2-GATE-M4/edec.json` | `cells.P2.accuracy_scale.tau.R.mean` |
| 442 | E-dec table (accuracy) | [0, 0] | `runs/P2-GATE-M4/edec.json` | `cells.P2.accuracy_scale.tau.R.ci95` |
| 443 | E-dec text (d) | 0.00381095 | `runs/P2-GATE-M4/edec.json` | `cells.P2.d_scale.tau.R.mean` |
| 444 | E-dec text (d) | [0.00297125, 0.00468317] | `runs/P2-GATE-M4/edec.json` | `cells.P2.d_scale.tau.R.ci95` |
| 445 | E-dec table (accuracy) | 0.07 | `runs/P2-GATE-M4/edec.json` | `cells.P2.accuracy_scale.tau.V.mean` |
| 446 | E-dec table (accuracy) | [0.036, 0.106] | `runs/P2-GATE-M4/edec.json` | `cells.P2.accuracy_scale.tau.V.ci95` |
| 447 | E-dec text (d) | 0.0826829 | `runs/P2-GATE-M4/edec.json` | `cells.P2.d_scale.tau.V.mean` |
| 448 | E-dec text (d) | [0.0421056, 0.116458] | `runs/P2-GATE-M4/edec.json` | `cells.P2.d_scale.tau.V.ci95` |
| 449 | E-dec | 500 | `runs/P2-GATE-M4/edec.json` | `cells.P3.n_complete` |
| 450 | E-dec table (accuracy) | 0.004 | `runs/P2-GATE-M4/edec.json` | `cells.P3.accuracy_scale.tau.T.mean` |
| 451 | E-dec table (accuracy) | [-0.006, 0.014] | `runs/P2-GATE-M4/edec.json` | `cells.P3.accuracy_scale.tau.T.ci95` |
| 452 | E-dec text (d) | 0.0203212 | `runs/P2-GATE-M4/edec.json` | `cells.P3.d_scale.tau.T.mean` |
| 453 | E-dec text (d) | [0.017166, 0.0234977] | `runs/P2-GATE-M4/edec.json` | `cells.P3.d_scale.tau.T.ci95` |
| 454 | E-dec table (accuracy) | 0 | `runs/P2-GATE-M4/edec.json` | `cells.P3.accuracy_scale.tau.U.mean` |
| 455 | E-dec table (accuracy) | [-0.016, 0.016] | `runs/P2-GATE-M4/edec.json` | `cells.P3.accuracy_scale.tau.U.ci95` |
| 456 | E-dec text (d) | -0.00532351 | `runs/P2-GATE-M4/edec.json` | `cells.P3.d_scale.tau.U.mean` |
| 457 | E-dec text (d) | [-0.00916455, -0.00149374] | `runs/P2-GATE-M4/edec.json` | `cells.P3.d_scale.tau.U.ci95` |
| 458 | E-dec table (accuracy) | -0.004 | `runs/P2-GATE-M4/edec.json` | `cells.P3.accuracy_scale.tau.R.mean` |
| 459 | E-dec table (accuracy) | [-0.012, 0.004] | `runs/P2-GATE-M4/edec.json` | `cells.P3.accuracy_scale.tau.R.ci95` |
| 460 | E-dec text (d) | 0.00780449 | `runs/P2-GATE-M4/edec.json` | `cells.P3.d_scale.tau.R.mean` |
| 461 | E-dec text (d) | [0.00686975, 0.00878039] | `runs/P2-GATE-M4/edec.json` | `cells.P3.d_scale.tau.R.ci95` |
| 462 | E-dec table (accuracy) | 0.008 | `runs/P2-GATE-M4/edec.json` | `cells.P3.accuracy_scale.tau.V.mean` |
| 463 | E-dec table (accuracy) | [-0.006, 0.024] | `runs/P2-GATE-M4/edec.json` | `cells.P3.accuracy_scale.tau.V.ci95` |
| 464 | E-dec text (d) | 0.0178402 | `runs/P2-GATE-M4/edec.json` | `cells.P3.d_scale.tau.V.mean` |
| 465 | E-dec text (d) | [0.0136375, 0.0219454] | `runs/P2-GATE-M4/edec.json` | `cells.P3.d_scale.tau.V.ci95` |
| 466 | E-dec PS text (accuracy) | 0.01 | `runs/P2-GATE-M4/edec.json` | `cells.PS1.accuracy_scale.tau.T.mean` |
| 467 | E-dec PS text (accuracy) | [0.002, 0.02] | `runs/P2-GATE-M4/edec.json` | `cells.PS1.accuracy_scale.tau.T.ci95` |
| 468 | E-dec PS text (accuracy) | 0.006 | `runs/P2-GATE-M4/edec.json` | `cells.PS1.accuracy_scale.tau.U.mean` |
| 469 | E-dec PS text (accuracy) | [-0.006, 0.018] | `runs/P2-GATE-M4/edec.json` | `cells.PS1.accuracy_scale.tau.U.ci95` |
| 470 | E-dec PS text (accuracy) | 0 | `runs/P2-GATE-M4/edec.json` | `cells.PS1.accuracy_scale.tau.R.mean` |
| 471 | E-dec PS text (accuracy) | [-0.008, 0.008] | `runs/P2-GATE-M4/edec.json` | `cells.PS1.accuracy_scale.tau.R.ci95` |
| 472 | E-dec PS text (accuracy) | 0.004 | `runs/P2-GATE-M4/edec.json` | `cells.PS1.accuracy_scale.tau.V.mean` |
| 473 | E-dec PS text (accuracy) | [0, 0.01] | `runs/P2-GATE-M4/edec.json` | `cells.PS1.accuracy_scale.tau.V.ci95` |
| 474 | E-dec PS text (accuracy) | 0.01 | `runs/P2-GATE-M4/edec.json` | `cells.PS2.accuracy_scale.tau.T.mean` |
| 475 | E-dec PS text (accuracy) | [-0.002, 0.022] | `runs/P2-GATE-M4/edec.json` | `cells.PS2.accuracy_scale.tau.T.ci95` |
| 476 | E-dec PS text (accuracy) | 0.004 | `runs/P2-GATE-M4/edec.json` | `cells.PS2.accuracy_scale.tau.U.mean` |
| 477 | E-dec PS text (accuracy) | [-0.004, 0.012] | `runs/P2-GATE-M4/edec.json` | `cells.PS2.accuracy_scale.tau.U.ci95` |
| 478 | E-dec PS text (accuracy) | 0.006 | `runs/P2-GATE-M4/edec.json` | `cells.PS2.accuracy_scale.tau.R.mean` |
| 479 | E-dec PS text (accuracy) | [-0.008, 0.02] | `runs/P2-GATE-M4/edec.json` | `cells.PS2.accuracy_scale.tau.R.ci95` |
| 480 | E-dec PS text (accuracy) | 0 | `runs/P2-GATE-M4/edec.json` | `cells.PS2.accuracy_scale.tau.V.mean` |
| 481 | E-dec PS text (accuracy) | [-0.006, 0.006] | `runs/P2-GATE-M4/edec.json` | `cells.PS2.accuracy_scale.tau.V.ci95` |
| 482 | E-pred table | - | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.s_text` |
| 483 | E-pred table | -1 | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.o` |
| 484 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.o_star` |
| 485 | E-pred table | 0 | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.b` |
| 486 | E-pred table | 1 | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.c_cnt` |
| 487 | E-pred table | -0.002 | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.net_difference` |
| 488 | E-pred table | [-0.006, 0] | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.ci95` |
| 489 | E-pred table | True | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.agree` |
| 490 | E-pred table | 1 | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.stability_share_same_sign` |
| 491 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.P1.excluded_reason` |
| 492 | E-pred table | - | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.s_text` |
| 493 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.o` |
| 494 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.o_star` |
| 495 | E-pred table | 0 | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.b` |
| 496 | E-pred table | 0 | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.c_cnt` |
| 497 | E-pred table | 0 | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.net_difference` |
| 498 | E-pred table | [0, 0] | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.ci95` |
| 499 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.agree` |
| 500 | E-pred table | 1 | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.stability_share_same_sign` |
| 501 | E-pred table | b = c_cnt: no observed sign (counted, excluded) | `runs/P2-GATE-M4/epred_score.json` | `cells.P2.excluded_reason` |
| 502 | E-pred table | - | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.s_text` |
| 503 | E-pred table | -1 | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.o` |
| 504 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.o_star` |
| 505 | E-pred table | 1 | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.b` |
| 506 | E-pred table | 3 | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.c_cnt` |
| 507 | E-pred table | -0.004 | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.net_difference` |
| 508 | E-pred table | [-0.012, 0.004] | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.ci95` |
| 509 | E-pred table | True | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.agree` |
| 510 | E-pred table | 1 | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.stability_share_same_sign` |
| 511 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.P3.excluded_reason` |
| 512 | E-pred table | - | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.s_text` |
| 513 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.o` |
| 514 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.o_star` |
| 515 | E-pred table | 2 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.b` |
| 516 | E-pred table | 2 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.c_cnt` |
| 517 | E-pred table | 0 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.net_difference` |
| 518 | E-pred table | [-0.008, 0.008] | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.ci95` |
| 519 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.agree` |
| 520 | E-pred table | 0.9757 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.stability_share_same_sign` |
| 521 | E-pred table | b = c_cnt: no observed sign (counted, excluded) | `runs/P2-GATE-M4/epred_score.json` | `cells.PS1.excluded_reason` |
| 522 | E-pred table | - | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.s_text` |
| 523 | E-pred table | 1 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.o` |
| 524 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.o_star` |
| 525 | E-pred table | 8 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.b` |
| 526 | E-pred table | 5 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.c_cnt` |
| 527 | E-pred table | 0.006 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.net_difference` |
| 528 | E-pred table | [-0.008, 0.02] | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.ci95` |
| 529 | E-pred table | False | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.agree` |
| 530 | E-pred table | 0.5175 | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.stability_share_same_sign` |
| 531 | E-pred table | None | `runs/P2-GATE-M4/epred_score.json` | `cells.PS2.excluded_reason` |
| 532 | E-pred | 2 | `runs/P2-GATE-M4/epred_score.json` | `P.A` |
| 533 | E-pred | 2 | `runs/P2-GATE-M4/epred_score.json` | `P.K_eval` |
| 534 | E-pred | [0.158114, 1] | `runs/P2-GATE-M4/epred_score.json` | `P.cp95` |
| 535 | E-pred rivals | 0 | `runs/P2-GATE-M4/epred_score.json` | `P.rivals.always +.A` |
| 536 | E-pred rivals | 2 | `runs/P2-GATE-M4/epred_score.json` | `P.rivals.- for P cells, + for PS cells.A` |
| 537 | E-pred | 0 | `runs/P2-GATE-M4/epred_score.json` | `PS.A` |
| 538 | E-pred | 1 | `runs/P2-GATE-M4/epred_score.json` | `PS.K_eval` |
| 539 | E-pred | [0, 0.975] | `runs/P2-GATE-M4/epred_score.json` | `PS.cp95` |
| 540 | E-pred rivals | 1 | `runs/P2-GATE-M4/epred_score.json` | `PS.rivals.always +.A` |
| 541 | E-pred rivals | 1 | `runs/P2-GATE-M4/epred_score.json` | `PS.rivals.- for P cells, + for PS cells.A` |
| 542 | E-pred | [] | `runs/P2-GATE-M4/epred_score.json` | `refutation_rule_met_for_cells` |
| 543 | E-pred plug-in (M4) | 0.960637 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.rho` |
| 544 | E-pred plug-in (M4) | 0.212845 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.mu` |
| 545 | E-pred plug-in (M4) | 0.501084 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.sigma2` |
| 546 | E-pred plug-in (M4) | 0.168605 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.mu_c` |
| 547 | E-pred plug-in (M4) | 0.556196 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.sigma2_c` |
| 548 | E-pred plug-in (M4) | 0.0372631 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.alpha_obs` |
| 549 | E-pred plug-in (M4) | 0.0612549 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.beta_obs` |
| 550 | E-pred plug-in (M4) | 0.928238 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.rho` |
| 551 | E-pred plug-in (M4) | 0.181532 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.mu` |
| 552 | E-pred plug-in (M4) | 0.431466 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.sigma2` |
| 553 | E-pred plug-in (M4) | 0.0991737 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.mu_c` |
| 554 | E-pred plug-in (M4) | 0.455725 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.sigma2_c` |
| 555 | E-pred plug-in (M4) | 0.0359262 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.alpha_obs` |
| 556 | E-pred plug-in (M4) | 0.032879 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.beta_obs` |
| 557 | E-pred plug-in (M4) | 0.226797 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.rho` |
| 558 | E-pred plug-in (M4) | 0.202365 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.mu` |
| 559 | E-pred plug-in (M4) | 0.510341 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.sigma2` |
| 560 | E-pred plug-in (M4) | 0.131942 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.mu_c` |
| 561 | E-pred plug-in (M4) | 0.492013 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.sigma2_c` |
| 562 | E-pred plug-in (M4) | 0.0436471 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.alpha_obs` |
| 563 | E-pred plug-in (M4) | 0.0490872 | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.beta_obs` |
| 564 | Tier 3 | 72 | `runs/P2-GATE-M4/tier3_fusion.json` | `multiplicity.n_intervals` |
| 565 | Tier 3 | -0.0984687 | `runs/P2-GATE-M4/tier3_fusion.json` | `inputs.tau` |
| 566 | Tier 3 | 307200 | `runs/P2-GATE-M4/tier3_fusion.json` | `inputs.n_cal_tokens` |
| 567 | Tier 3 | 61.758 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.mean_flagged` |
| 568 | Tier 3 table | 0.838 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.arms.NONE.acc` |
| 569 | Tier 3 table | 0.836 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.arms.GM.acc` |
| 570 | Tier 3 table | 0.804 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.arms.MED.acc` |
| 571 | Tier 3 table | 0.834 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.arms.TM-G.acc` |
| 572 | Tier 3 table | 0.816 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.arms.TM20.acc` |
| 573 | Tier 3 table | 0.838 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.arms.SOFT-G.acc` |
| 574 | Tier 3 table | 0.838 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.arms.SOFT-A.acc` |
| 575 | Tier 3 table/text | 4 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.b` |
| 576 | Tier 3 table/text | 20 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.c` |
| 577 | Tier 3 table/text | 24 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.n_d` |
| 578 | Tier 3 table/text | -0.032 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.diff` |
| 579 | Tier 3 table/text | [-0.052, -0.014] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.ci95` |
| 580 | Tier 3 table/text | [0.0473536, 0.373842] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.theta_ci95_exact` |
| 581 | Tier 3 table/text | 0.0705808 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.discordance_bound_B` |
| 582 | Tier 3 table/text | 0.0269539 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.mdd` |
| 583 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.mdd_used` |
| 584 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.reading` |
| 585 | Tier 3 table/text | gate_higher | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_GM.counts_against` |
| 586 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.b` |
| 587 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.c` |
| 588 | Tier 3 table/text | 5 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.n_d` |
| 589 | Tier 3 table/text | -0.002 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.diff` |
| 590 | Tier 3 table/text | [-0.01, 0.006] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.ci95` |
| 591 | Tier 3 table/text | [0.052745, 0.853367] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.theta_ci95_exact` |
| 592 | Tier 3 table/text | 0.0231814 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.discordance_bound_B` |
| 593 | Tier 3 table/text | 0.0125449 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.mdd` |
| 594 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.mdd_used` |
| 595 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.reading` |
| 596 | Tier 3 table/text | finding_against_added_value | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_GM.counts_against` |
| 597 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.b` |
| 598 | Tier 3 table/text | 12 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.c` |
| 599 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.n_d` |
| 600 | Tier 3 table/text | -0.02 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.diff` |
| 601 | Tier 3 table/text | [-0.034, -0.006] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.ci95` |
| 602 | Tier 3 table/text | [0.0177945, 0.428129] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.theta_ci95_exact` |
| 603 | Tier 3 table/text | 0.0465333 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.discordance_bound_B` |
| 604 | Tier 3 table/text | 0.0207248 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.mdd` |
| 605 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.mdd_used` |
| 606 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.reading` |
| 607 | Tier 3 table/text | gate_higher | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_GM.counts_against` |
| 608 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.b` |
| 609 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.c` |
| 610 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.n_d` |
| 611 | Tier 3 table/text | 0.002 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.diff` |
| 612 | Tier 3 table/text | [0, 0.006] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.ci95` |
| 613 | Tier 3 table/text | [0.025, 1] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.theta_ci95_exact` |
| 614 | Tier 3 table/text | 0.0110925 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.discordance_bound_B` |
| 615 | Tier 3 table/text | 0.00564556 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.mdd` |
| 616 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.mdd_used` |
| 617 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.reading` |
| 618 | Tier 3 table/text | discarding_and_discounting_not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_GM.counts_against` |
| 619 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.b` |
| 620 | Tier 3 table/text | 7 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.c` |
| 621 | Tier 3 table/text | 15 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.n_d` |
| 622 | Tier 3 table/text | 0.002 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.diff` |
| 623 | Tier 3 table/text | [-0.014, 0.018] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.ci95` |
| 624 | Tier 3 table/text | [0.265861, 0.787333] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.theta_ci95_exact` |
| 625 | Tier 3 table/text | 0.0489982 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.discordance_bound_B` |
| 626 | Tier 3 table/text | 0.0219876 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.mdd` |
| 627 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.mdd_used` |
| 628 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.reading` |
| 629 | Tier 3 table/text | discarding_and_weighting_not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_GM.counts_against` |
| 630 | Tier 3 table/text | 4 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.b` |
| 631 | Tier 3 table/text | 21 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.c` |
| 632 | Tier 3 table/text | 25 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.n_d` |
| 633 | Tier 3 table/text | -0.034 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.diff` |
| 634 | Tier 3 table/text | [-0.054, -0.016] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.ci95` |
| 635 | Tier 3 table/text | [0.0453795, 0.360828] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.theta_ci95_exact` |
| 636 | Tier 3 table/text | 0.0729276 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.discordance_bound_B` |
| 637 | Tier 3 table/text | 0.0275167 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.mdd` |
| 638 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.mdd_used` |
| 639 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.MED_minus_NONE.reading` |
| 640 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.b` |
| 641 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.c` |
| 642 | Tier 3 table/text | 4 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.n_d` |
| 643 | Tier 3 table/text | -0.004 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.diff` |
| 644 | Tier 3 table/text | [-0.012, 0.004] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.ci95` |
| 645 | Tier 3 table/text | [0.00630946, 0.80588] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.theta_ci95_exact` |
| 646 | Tier 3 table/text | 0.0203556 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.discordance_bound_B` |
| 647 | Tier 3 table/text | 0.0111761 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.mdd` |
| 648 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.mdd_used` |
| 649 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM-G_minus_NONE.reading` |
| 650 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.b` |
| 651 | Tier 3 table/text | 13 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.c` |
| 652 | Tier 3 table/text | 15 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.n_d` |
| 653 | Tier 3 table/text | -0.022 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.diff` |
| 654 | Tier 3 table/text | [-0.038, -0.008] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.ci95` |
| 655 | Tier 3 table/text | [0.0165759, 0.404603] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.theta_ci95_exact` |
| 656 | Tier 3 table/text | 0.0489982 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.discordance_bound_B` |
| 657 | Tier 3 table/text | 0.0213733 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.mdd` |
| 658 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.mdd_used` |
| 659 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.TM20_minus_NONE.reading` |
| 660 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.b` |
| 661 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.c` |
| 662 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.n_d` |
| 663 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.diff` |
| 664 | Tier 3 table/text | [0, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.ci95` |
| 665 | Tier 3 table/text | [nan, nan] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.theta_ci95_exact` |
| 666 | Tier 3 table/text | 0.00735061 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.discordance_bound_B` |
| 667 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.mdd` |
| 668 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.mdd_used` |
| 669 | Tier 3 table/text | identical | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-G_minus_NONE.reading` |
| 670 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.b` |
| 671 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.c` |
| 672 | Tier 3 table/text | 16 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.n_d` |
| 673 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.diff` |
| 674 | Tier 3 table/text | [-0.016, 0.016] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.ci95` |
| 675 | Tier 3 table/text | [0.24651, 0.75349] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.theta_ci95_exact` |
| 676 | Tier 3 table/text | 0.0514468 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.discordance_bound_B` |
| 677 | Tier 3 table/text | 0.0227675 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.mdd` |
| 678 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.mdd_used` |
| 679 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.contrasts.SOFT-A_minus_NONE.reading` |
| 680 | Tier 3 d control | 0.0334578 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.contrasts.TM-G_minus_GM.mean_diff` |
| 681 | Tier 3 d control | [0.0279218, 0.0389502] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.contrasts.TM-G_minus_GM.ci95` |
| 682 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.contrasts.TM-G_minus_GM.reading` |
| 683 | Tier 3 d control | 0.259078 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.contrasts.TM20_minus_GM.mean_diff` |
| 684 | Tier 3 d control | [0.225416, 0.292436] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.contrasts.TM20_minus_GM.ci95` |
| 685 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.contrasts.TM20_minus_GM.reading` |
| 686 | Tier 3 d control | 0.230496 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.per_arm.NONE.mean_d` |
| 687 | Tier 3 d control | 0.239463 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.per_arm.GM.mean_d` |
| 688 | Tier 3 d control | 0.272921 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.per_arm.TM-G.mean_d` |
| 689 | Tier 3 d control | 0.498541 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.jpeg10.d_control.per_arm.TM20.mean_d` |
| 690 | Tier 3 | 33.892 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.mean_flagged` |
| 691 | Tier 3 table | 0.676 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.arms.NONE.acc` |
| 692 | Tier 3 table | 0.676 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.arms.GM.acc` |
| 693 | Tier 3 table | 0.678 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.arms.MED.acc` |
| 694 | Tier 3 table | 0.676 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.arms.TM-G.acc` |
| 695 | Tier 3 table | 0.682 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.arms.TM20.acc` |
| 696 | Tier 3 table | 0.676 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.arms.SOFT-G.acc` |
| 697 | Tier 3 table | 0.676 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.arms.SOFT-A.acc` |
| 698 | Tier 3 table/text | 10 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.b` |
| 699 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.c` |
| 700 | Tier 3 table/text | 19 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.n_d` |
| 701 | Tier 3 table/text | 0.002 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.diff` |
| 702 | Tier 3 table/text | [-0.016, 0.02] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.ci95` |
| 703 | Tier 3 table/text | [0.288643, 0.755525] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.theta_ci95_exact` |
| 704 | Tier 3 table/text | 0.0587073 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.discordance_bound_B` |
| 705 | Tier 3 table/text | 0.0246876 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.mdd` |
| 706 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.mdd_used` |
| 707 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.reading` |
| 708 | Tier 3 table/text | finding_against_added_value | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_GM.counts_against` |
| 709 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.b` |
| 710 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.c` |
| 711 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.n_d` |
| 712 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.diff` |
| 713 | Tier 3 table/text | [-0.006, 0.006] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.ci95` |
| 714 | Tier 3 table/text | [0.0125791, 0.987421] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.theta_ci95_exact` |
| 715 | Tier 3 table/text | 0.0143741 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.discordance_bound_B` |
| 716 | Tier 3 table/text | 0.00806729 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.mdd` |
| 717 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.mdd_used` |
| 718 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.reading` |
| 719 | Tier 3 table/text | finding_against_added_value | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_GM.counts_against` |
| 720 | Tier 3 table/text | 6 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.b` |
| 721 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.c` |
| 722 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.n_d` |
| 723 | Tier 3 table/text | 0.006 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.diff` |
| 724 | Tier 3 table/text | [-0.006, 0.018] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.ci95` |
| 725 | Tier 3 table/text | [0.299295, 0.925145] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.theta_ci95_exact` |
| 726 | Tier 3 table/text | 0.0338937 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.discordance_bound_B` |
| 727 | Tier 3 table/text | 0.016993 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.mdd` |
| 728 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.mdd_used` |
| 729 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.reading` |
| 730 | Tier 3 table/text | finding_against_added_value | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_GM.counts_against` |
| 731 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.b` |
| 732 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.c` |
| 733 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.n_d` |
| 734 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.diff` |
| 735 | Tier 3 table/text | [0, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.ci95` |
| 736 | Tier 3 table/text | [nan, nan] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.theta_ci95_exact` |
| 737 | Tier 3 table/text | 0.00735061 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.discordance_bound_B` |
| 738 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.mdd` |
| 739 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.mdd_used` |
| 740 | Tier 3 table/text | identical | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.reading` |
| 741 | Tier 3 table/text | discarding_and_discounting_not_distinguishable_identical | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_GM.counts_against` |
| 742 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.b` |
| 743 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.c` |
| 744 | Tier 3 table/text | 18 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.n_d` |
| 745 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.diff` |
| 746 | Tier 3 table/text | [-0.016, 0.016] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.ci95` |
| 747 | Tier 3 table/text | [0.260191, 0.739809] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.theta_ci95_exact` |
| 748 | Tier 3 table/text | 0.0563002 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.discordance_bound_B` |
| 749 | Tier 3 table/text | 0.0239513 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.mdd` |
| 750 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.mdd_used` |
| 751 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.reading` |
| 752 | Tier 3 table/text | discarding_and_weighting_not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_GM.counts_against` |
| 753 | Tier 3 table/text | 10 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.b` |
| 754 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.c` |
| 755 | Tier 3 table/text | 19 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.n_d` |
| 756 | Tier 3 table/text | 0.002 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.diff` |
| 757 | Tier 3 table/text | [-0.016, 0.02] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.ci95` |
| 758 | Tier 3 table/text | [0.288643, 0.755525] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.theta_ci95_exact` |
| 759 | Tier 3 table/text | 0.0587073 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.discordance_bound_B` |
| 760 | Tier 3 table/text | 0.0246876 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.mdd` |
| 761 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.mdd_used` |
| 762 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.MED_minus_NONE.reading` |
| 763 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.b` |
| 764 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.c` |
| 765 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.n_d` |
| 766 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.diff` |
| 767 | Tier 3 table/text | [-0.006, 0.006] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.ci95` |
| 768 | Tier 3 table/text | [0.0125791, 0.987421] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.theta_ci95_exact` |
| 769 | Tier 3 table/text | 0.0143741 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.discordance_bound_B` |
| 770 | Tier 3 table/text | 0.00806729 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.mdd` |
| 771 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.mdd_used` |
| 772 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM-G_minus_NONE.reading` |
| 773 | Tier 3 table/text | 6 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.b` |
| 774 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.c` |
| 775 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.n_d` |
| 776 | Tier 3 table/text | 0.006 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.diff` |
| 777 | Tier 3 table/text | [-0.006, 0.018] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.ci95` |
| 778 | Tier 3 table/text | [0.299295, 0.925145] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.theta_ci95_exact` |
| 779 | Tier 3 table/text | 0.0338937 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.discordance_bound_B` |
| 780 | Tier 3 table/text | 0.016993 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.mdd` |
| 781 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.mdd_used` |
| 782 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.TM20_minus_NONE.reading` |
| 783 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.b` |
| 784 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.c` |
| 785 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.n_d` |
| 786 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.diff` |
| 787 | Tier 3 table/text | [0, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.ci95` |
| 788 | Tier 3 table/text | [nan, nan] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.theta_ci95_exact` |
| 789 | Tier 3 table/text | 0.00735061 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.discordance_bound_B` |
| 790 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.mdd` |
| 791 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.mdd_used` |
| 792 | Tier 3 table/text | identical | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-G_minus_NONE.reading` |
| 793 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.b` |
| 794 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.c` |
| 795 | Tier 3 table/text | 18 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.n_d` |
| 796 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.diff` |
| 797 | Tier 3 table/text | [-0.016, 0.016] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.ci95` |
| 798 | Tier 3 table/text | [0.260191, 0.739809] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.theta_ci95_exact` |
| 799 | Tier 3 table/text | 0.0563002 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.discordance_bound_B` |
| 800 | Tier 3 table/text | 0.0239513 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.mdd` |
| 801 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.mdd_used` |
| 802 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.contrasts.SOFT-A_minus_NONE.reading` |
| 803 | Tier 3 d control | 0.0178473 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.contrasts.TM-G_minus_GM.mean_diff` |
| 804 | Tier 3 d control | [0.0138953, 0.0217777] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.contrasts.TM-G_minus_GM.ci95` |
| 805 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.contrasts.TM-G_minus_GM.reading` |
| 806 | Tier 3 d control | 0.19503 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.contrasts.TM20_minus_GM.mean_diff` |
| 807 | Tier 3 d control | [0.152529, 0.236842] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.contrasts.TM20_minus_GM.ci95` |
| 808 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.contrasts.TM20_minus_GM.reading` |
| 809 | Tier 3 d control | 0.16988 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.per_arm.NONE.mean_d` |
| 810 | Tier 3 d control | 0.173691 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.per_arm.GM.mean_d` |
| 811 | Tier 3 d control | 0.191538 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.per_arm.TM-G.mean_d` |
| 812 | Tier 3 d control | 0.36872 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.noise0.1.d_control.per_arm.TM20.mean_d` |
| 813 | Tier 3 | 45.958 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.mean_flagged` |
| 814 | Tier 3 table | 0.876 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.arms.NONE.acc` |
| 815 | Tier 3 table | 0.872 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.arms.GM.acc` |
| 816 | Tier 3 table | 0.84 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.arms.MED.acc` |
| 817 | Tier 3 table | 0.866 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.arms.TM-G.acc` |
| 818 | Tier 3 table | 0.846 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.arms.TM20.acc` |
| 819 | Tier 3 table | 0.876 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.arms.SOFT-G.acc` |
| 820 | Tier 3 table | 0.88 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.arms.SOFT-A.acc` |
| 821 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.b` |
| 822 | Tier 3 table/text | 17 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.c` |
| 823 | Tier 3 table/text | 18 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.n_d` |
| 824 | Tier 3 table/text | -0.032 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.diff` |
| 825 | Tier 3 table/text | [-0.05, -0.016] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.ci95` |
| 826 | Tier 3 table/text | [0.00140556, 0.272944] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.theta_ci95_exact` |
| 827 | Tier 3 table/text | 0.0563002 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.discordance_bound_B` |
| 828 | Tier 3 table/text | 0.0237792 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.mdd` |
| 829 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.mdd_used` |
| 830 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.reading` |
| 831 | Tier 3 table/text | gate_higher | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_GM.counts_against` |
| 832 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.b` |
| 833 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.c` |
| 834 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.n_d` |
| 835 | Tier 3 table/text | -0.006 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.diff` |
| 836 | Tier 3 table/text | [-0.014, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.ci95` |
| 837 | Tier 3 table/text | [0, 0.707598] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.theta_ci95_exact` |
| 838 | Tier 3 table/text | 0.0174337 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.discordance_bound_B` |
| 839 | Tier 3 table/text | 0.00980068 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.mdd` |
| 840 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.mdd_used` |
| 841 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.reading` |
| 842 | Tier 3 table/text | finding_against_added_value | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_GM.counts_against` |
| 843 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.b` |
| 844 | Tier 3 table/text | 13 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.c` |
| 845 | Tier 3 table/text | 13 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.n_d` |
| 846 | Tier 3 table/text | -0.026 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.diff` |
| 847 | Tier 3 table/text | [-0.04, -0.014] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.ci95` |
| 848 | Tier 3 table/text | [0, 0.247053] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.theta_ci95_exact` |
| 849 | Tier 3 table/text | 0.0440504 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.discordance_bound_B` |
| 850 | Tier 3 table/text | 0.0200889 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.mdd` |
| 851 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.mdd_used` |
| 852 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.reading` |
| 853 | Tier 3 table/text | gate_higher | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_GM.counts_against` |
| 854 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.b` |
| 855 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.c` |
| 856 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.n_d` |
| 857 | Tier 3 table/text | 0.004 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.diff` |
| 858 | Tier 3 table/text | [0, 0.01] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.ci95` |
| 859 | Tier 3 table/text | [0.158114, 1] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.theta_ci95_exact` |
| 860 | Tier 3 table/text | 0.0143741 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.discordance_bound_B` |
| 861 | Tier 3 table/text | 0.00795157 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.mdd` |
| 862 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.mdd_used` |
| 863 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.reading` |
| 864 | Tier 3 table/text | discarding_and_discounting_not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_GM.counts_against` |
| 865 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.b` |
| 866 | Tier 3 table/text | 4 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.c` |
| 867 | Tier 3 table/text | 12 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.n_d` |
| 868 | Tier 3 table/text | 0.008 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.diff` |
| 869 | Tier 3 table/text | [-0.006, 0.022] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.ci95` |
| 870 | Tier 3 table/text | [0.348876, 0.900754] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.theta_ci95_exact` |
| 871 | Tier 3 table/text | 0.0415476 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.discordance_bound_B` |
| 872 | Tier 3 table/text | 0.019628 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.mdd` |
| 873 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.mdd_used` |
| 874 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.reading` |
| 875 | Tier 3 table/text | discarding_and_weighting_not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_GM.counts_against` |
| 876 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.b` |
| 877 | Tier 3 table/text | 19 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.c` |
| 878 | Tier 3 table/text | 20 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.n_d` |
| 879 | Tier 3 table/text | -0.036 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.diff` |
| 880 | Tier 3 table/text | [-0.054, -0.02] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.ci95` |
| 881 | Tier 3 table/text | [0.00126509, 0.248733] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.theta_ci95_exact` |
| 882 | Tier 3 table/text | 0.0611026 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.discordance_bound_B` |
| 883 | Tier 3 table/text | 0.0248311 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.mdd` |
| 884 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.mdd_used` |
| 885 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.MED_minus_NONE.reading` |
| 886 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.b` |
| 887 | Tier 3 table/text | 5 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.c` |
| 888 | Tier 3 table/text | 5 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.n_d` |
| 889 | Tier 3 table/text | -0.01 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.diff` |
| 890 | Tier 3 table/text | [-0.02, -0.002] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.ci95` |
| 891 | Tier 3 table/text | [0, 0.521824] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.theta_ci95_exact` |
| 892 | Tier 3 table/text | 0.0231814 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.discordance_bound_B` |
| 893 | Tier 3 table/text | 0.012458 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.mdd` |
| 894 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.mdd_used` |
| 895 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM-G_minus_NONE.reading` |
| 896 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.b` |
| 897 | Tier 3 table/text | 15 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.c` |
| 898 | Tier 3 table/text | 15 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.n_d` |
| 899 | Tier 3 table/text | -0.03 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.diff` |
| 900 | Tier 3 table/text | [-0.046, -0.016] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.ci95` |
| 901 | Tier 3 table/text | [0, 0.218019] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.theta_ci95_exact` |
| 902 | Tier 3 table/text | 0.0489982 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.discordance_bound_B` |
| 903 | Tier 3 table/text | 0.0213015 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.mdd` |
| 904 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.mdd_used` |
| 905 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.TM20_minus_NONE.reading` |
| 906 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.b` |
| 907 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.c` |
| 908 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.n_d` |
| 909 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.diff` |
| 910 | Tier 3 table/text | [-0.006, 0.006] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.ci95` |
| 911 | Tier 3 table/text | [0.0125791, 0.987421] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.theta_ci95_exact` |
| 912 | Tier 3 table/text | 0.0143741 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.discordance_bound_B` |
| 913 | Tier 3 table/text | 0.00797331 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.mdd` |
| 914 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.mdd_used` |
| 915 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-G_minus_NONE.reading` |
| 916 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.b` |
| 917 | Tier 3 table/text | 6 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.c` |
| 918 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.n_d` |
| 919 | Tier 3 table/text | 0.004 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.diff` |
| 920 | Tier 3 table/text | [-0.01, 0.02] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.ci95` |
| 921 | Tier 3 table/text | [0.288609, 0.823389] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.theta_ci95_exact` |
| 922 | Tier 3 table/text | 0.0465333 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.discordance_bound_B` |
| 923 | Tier 3 table/text | 0.0212953 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.mdd` |
| 924 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.mdd_used` |
| 925 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.contrasts.SOFT-A_minus_NONE.reading` |
| 926 | Tier 3 d control | 0.0312643 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.contrasts.TM-G_minus_GM.mean_diff` |
| 927 | Tier 3 d control | [0.0272282, 0.0352149] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.contrasts.TM-G_minus_GM.ci95` |
| 928 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.contrasts.TM-G_minus_GM.reading` |
| 929 | Tier 3 d control | 0.302807 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.contrasts.TM20_minus_GM.mean_diff` |
| 930 | Tier 3 d control | [0.270077, 0.333911] | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.contrasts.TM20_minus_GM.ci95` |
| 931 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.contrasts.TM20_minus_GM.reading` |
| 932 | Tier 3 d control | 0.268912 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.per_arm.NONE.mean_d` |
| 933 | Tier 3 d control | 0.276716 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.per_arm.GM.mean_d` |
| 934 | Tier 3 d control | 0.307981 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.per_arm.TM-G.mean_d` |
| 935 | Tier 3 d control | 0.579524 | `runs/P2-GATE-M4/tier3_fusion.json` | `cells.splice128.d_control.per_arm.TM20.mean_d` |
| 936 | Tier 3 | 96.472 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.mean_flagged` |
| 937 | Tier 3 table | 0.87 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.arms.NONE.acc` |
| 938 | Tier 3 table | 0.87 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.arms.GM.acc` |
| 939 | Tier 3 table | 0.846 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.arms.MED.acc` |
| 940 | Tier 3 table | 0.858 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.arms.TM-G.acc` |
| 941 | Tier 3 table | 0.846 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.arms.TM20.acc` |
| 942 | Tier 3 table | 0.87 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.arms.SOFT-G.acc` |
| 943 | Tier 3 table | 0.88 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.arms.SOFT-A.acc` |
| 944 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.b` |
| 945 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.c` |
| 946 | Tier 3 table/text | 16 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.n_d` |
| 947 | Tier 3 table/text | -0.024 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.diff` |
| 948 | Tier 3 table/text | [-0.04, -0.01] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.ci95` |
| 949 | Tier 3 table/text | [0.0155136, 0.383476] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.theta_ci95_exact` |
| 950 | Tier 3 table/text | 0.0514468 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.discordance_bound_B` |
| 951 | Tier 3 table/text | 0.0221489 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.mdd` |
| 952 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.mdd_used` |
| 953 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_GM.reading` |
| 954 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.b` |
| 955 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.c` |
| 956 | Tier 3 table/text | 10 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.n_d` |
| 957 | Tier 3 table/text | -0.012 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.diff` |
| 958 | Tier 3 table/text | [-0.024, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.ci95` |
| 959 | Tier 3 table/text | [0.0252107, 0.556095] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.theta_ci95_exact` |
| 960 | Tier 3 table/text | 0.0364724 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.discordance_bound_B` |
| 961 | Tier 3 table/text | 0.0175518 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.mdd` |
| 962 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.mdd_used` |
| 963 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_GM.reading` |
| 964 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.b` |
| 965 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.c` |
| 966 | Tier 3 table/text | 16 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.n_d` |
| 967 | Tier 3 table/text | -0.024 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.diff` |
| 968 | Tier 3 table/text | [-0.04, -0.00995] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.ci95` |
| 969 | Tier 3 table/text | [0.0155136, 0.383476] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.theta_ci95_exact` |
| 970 | Tier 3 table/text | 0.0514468 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.discordance_bound_B` |
| 971 | Tier 3 table/text | 0.0221018 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.mdd` |
| 972 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.mdd_used` |
| 973 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_GM.reading` |
| 974 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.b` |
| 975 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.c` |
| 976 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.n_d` |
| 977 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.diff` |
| 978 | Tier 3 table/text | [0, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.ci95` |
| 979 | Tier 3 table/text | [nan, nan] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.theta_ci95_exact` |
| 980 | Tier 3 table/text | 0.00735061 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.discordance_bound_B` |
| 981 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.mdd` |
| 982 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.mdd_used` |
| 983 | Tier 3 table/text | identical | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_GM.reading` |
| 984 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.b` |
| 985 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.c` |
| 986 | Tier 3 table/text | 11 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.n_d` |
| 987 | Tier 3 table/text | 0.01 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.diff` |
| 988 | Tier 3 table/text | [-0.002, 0.024] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.ci95` |
| 989 | Tier 3 table/text | [0.390257, 0.939782] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.theta_ci95_exact` |
| 990 | Tier 3 table/text | 0.0390226 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.discordance_bound_B` |
| 991 | Tier 3 table/text | 0.0183962 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.mdd` |
| 992 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.mdd_used` |
| 993 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_GM.reading` |
| 994 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.b` |
| 995 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.c` |
| 996 | Tier 3 table/text | 16 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.n_d` |
| 997 | Tier 3 table/text | -0.024 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.diff` |
| 998 | Tier 3 table/text | [-0.04, -0.01] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.ci95` |
| 999 | Tier 3 table/text | [0.0155136, 0.383476] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.theta_ci95_exact` |
| 1000 | Tier 3 table/text | 0.0514468 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.discordance_bound_B` |
| 1001 | Tier 3 table/text | 0.0221859 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.mdd` |
| 1002 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.mdd_used` |
| 1003 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.MED_minus_NONE.reading` |
| 1004 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.b` |
| 1005 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.c` |
| 1006 | Tier 3 table/text | 10 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.n_d` |
| 1007 | Tier 3 table/text | -0.012 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.diff` |
| 1008 | Tier 3 table/text | [-0.024, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.ci95` |
| 1009 | Tier 3 table/text | [0.0252107, 0.556095] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.theta_ci95_exact` |
| 1010 | Tier 3 table/text | 0.0364724 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.discordance_bound_B` |
| 1011 | Tier 3 table/text | 0.0174955 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.mdd` |
| 1012 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.mdd_used` |
| 1013 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM-G_minus_NONE.reading` |
| 1014 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.b` |
| 1015 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.c` |
| 1016 | Tier 3 table/text | 16 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.n_d` |
| 1017 | Tier 3 table/text | -0.024 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.diff` |
| 1018 | Tier 3 table/text | [-0.04, -0.01] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.ci95` |
| 1019 | Tier 3 table/text | [0.0155136, 0.383476] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.theta_ci95_exact` |
| 1020 | Tier 3 table/text | 0.0514468 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.discordance_bound_B` |
| 1021 | Tier 3 table/text | 0.022151 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.mdd` |
| 1022 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.mdd_used` |
| 1023 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.TM20_minus_NONE.reading` |
| 1024 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.b` |
| 1025 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.c` |
| 1026 | Tier 3 table/text | 4 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.n_d` |
| 1027 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.diff` |
| 1028 | Tier 3 table/text | [-0.008, 0.008] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.ci95` |
| 1029 | Tier 3 table/text | [0.067586, 0.932414] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.theta_ci95_exact` |
| 1030 | Tier 3 table/text | 0.0203556 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.discordance_bound_B` |
| 1031 | Tier 3 table/text | 0.0112037 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.mdd` |
| 1032 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.mdd_used` |
| 1033 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-G_minus_NONE.reading` |
| 1034 | Tier 3 table/text | 10 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.b` |
| 1035 | Tier 3 table/text | 5 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.c` |
| 1036 | Tier 3 table/text | 15 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.n_d` |
| 1037 | Tier 3 table/text | 0.01 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.diff` |
| 1038 | Tier 3 table/text | [-0.004, 0.026] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.ci95` |
| 1039 | Tier 3 table/text | [0.383804, 0.881759] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.theta_ci95_exact` |
| 1040 | Tier 3 table/text | 0.0489982 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.discordance_bound_B` |
| 1041 | Tier 3 table/text | 0.0214981 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.mdd` |
| 1042 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.mdd_used` |
| 1043 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.contrasts.SOFT-A_minus_NONE.reading` |
| 1044 | Tier 3 d control | 0.0498889 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.contrasts.TM-G_minus_GM.mean_diff` |
| 1045 | Tier 3 d control | [0.0433531, 0.0563216] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.contrasts.TM-G_minus_GM.ci95` |
| 1046 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.contrasts.TM-G_minus_GM.reading` |
| 1047 | Tier 3 d control | 0.29113 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.contrasts.TM20_minus_GM.mean_diff` |
| 1048 | Tier 3 d control | [0.259975, 0.32095] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.contrasts.TM20_minus_GM.ci95` |
| 1049 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.contrasts.TM20_minus_GM.reading` |
| 1050 | Tier 3 d control | 0.2705 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.per_arm.NONE.mean_d` |
| 1051 | Tier 3 d control | 0.292579 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.per_arm.GM.mean_d` |
| 1052 | Tier 3 d control | 0.342468 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.per_arm.TM-G.mean_d` |
| 1053 | Tier 3 d control | 0.58371 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.patch.d_control.per_arm.TM20.mean_d` |
| 1054 | Tier 3 | 209.694 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.mean_flagged` |
| 1055 | Tier 3 table | 0.87 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.arms.NONE.acc` |
| 1056 | Tier 3 table | 0.876 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.arms.GM.acc` |
| 1057 | Tier 3 table | 0.838 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.arms.MED.acc` |
| 1058 | Tier 3 table | 0.852 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.arms.TM-G.acc` |
| 1059 | Tier 3 table | 0.846 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.arms.TM20.acc` |
| 1060 | Tier 3 table | 0.878 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.arms.SOFT-G.acc` |
| 1061 | Tier 3 table | 0.892 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.arms.SOFT-A.acc` |
| 1062 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.b` |
| 1063 | Tier 3 table/text | 20 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.c` |
| 1064 | Tier 3 table/text | 21 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.n_d` |
| 1065 | Tier 3 table/text | -0.038 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.diff` |
| 1066 | Tier 3 table/text | [-0.056, -0.02] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.ci95` |
| 1067 | Tier 3 table/text | [0.00120488, 0.23816] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.theta_ci95_exact` |
| 1068 | Tier 3 table/text | 0.0634869 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.discordance_bound_B` |
| 1069 | Tier 3 table/text | 0.0251848 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.mdd` |
| 1070 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.mdd_used` |
| 1071 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_GM.reading` |
| 1072 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.b` |
| 1073 | Tier 3 table/text | 13 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.c` |
| 1074 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.n_d` |
| 1075 | Tier 3 table/text | -0.024 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.diff` |
| 1076 | Tier 3 table/text | [-0.04, -0.01] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.ci95` |
| 1077 | Tier 3 table/text | [0.00180678, 0.338684] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.theta_ci95_exact` |
| 1078 | Tier 3 table/text | 0.0465333 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.discordance_bound_B` |
| 1079 | Tier 3 table/text | 0.0206532 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.mdd` |
| 1080 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.mdd_used` |
| 1081 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_GM.reading` |
| 1082 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.b` |
| 1083 | Tier 3 table/text | 15 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.c` |
| 1084 | Tier 3 table/text | 15 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.n_d` |
| 1085 | Tier 3 table/text | -0.03 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.diff` |
| 1086 | Tier 3 table/text | [-0.046, -0.016] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.ci95` |
| 1087 | Tier 3 table/text | [0, 0.218019] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.theta_ci95_exact` |
| 1088 | Tier 3 table/text | 0.0489982 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.discordance_bound_B` |
| 1089 | Tier 3 table/text | 0.0213059 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.mdd` |
| 1090 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.mdd_used` |
| 1091 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_GM.reading` |
| 1092 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.b` |
| 1093 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.c` |
| 1094 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.n_d` |
| 1095 | Tier 3 table/text | 0.002 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.diff` |
| 1096 | Tier 3 table/text | [-0.004, 0.01] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.ci95` |
| 1097 | Tier 3 table/text | [0.0942993, 0.991596] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.theta_ci95_exact` |
| 1098 | Tier 3 table/text | 0.0174337 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.discordance_bound_B` |
| 1099 | Tier 3 table/text | 0.00985246 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.mdd` |
| 1100 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.mdd_used` |
| 1101 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_GM.reading` |
| 1102 | Tier 3 table/text | 10 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.b` |
| 1103 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.c` |
| 1104 | Tier 3 table/text | 12 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.n_d` |
| 1105 | Tier 3 table/text | 0.016 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.diff` |
| 1106 | Tier 3 table/text | [0.00395, 0.03] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.ci95` |
| 1107 | Tier 3 table/text | [0.515862, 0.979137] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.theta_ci95_exact` |
| 1108 | Tier 3 table/text | 0.0415476 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.discordance_bound_B` |
| 1109 | Tier 3 table/text | 0.0192527 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.mdd` |
| 1110 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.mdd_used` |
| 1111 | Tier 3 table/text | above | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_GM.reading` |
| 1112 | Tier 3 table/text | 2 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.b` |
| 1113 | Tier 3 table/text | 18 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.c` |
| 1114 | Tier 3 table/text | 20 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.n_d` |
| 1115 | Tier 3 table/text | -0.032 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.diff` |
| 1116 | Tier 3 table/text | [-0.05, -0.016] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.ci95` |
| 1117 | Tier 3 table/text | [0.0123485, 0.316983] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.theta_ci95_exact` |
| 1118 | Tier 3 table/text | 0.0611026 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.discordance_bound_B` |
| 1119 | Tier 3 table/text | 0.0246451 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.mdd` |
| 1120 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.mdd_used` |
| 1121 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.MED_minus_NONE.reading` |
| 1122 | Tier 3 table/text | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.b` |
| 1123 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.c` |
| 1124 | Tier 3 table/text | 9 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.n_d` |
| 1125 | Tier 3 table/text | -0.018 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.diff` |
| 1126 | Tier 3 table/text | [-0.03, -0.008] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.ci95` |
| 1127 | Tier 3 table/text | [0, 0.336267] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.theta_ci95_exact` |
| 1128 | Tier 3 table/text | 0.0338937 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.discordance_bound_B` |
| 1129 | Tier 3 table/text | 0.0165889 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.mdd` |
| 1130 | Tier 3 table/text | False | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.mdd_used` |
| 1131 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM-G_minus_NONE.reading` |
| 1132 | Tier 3 table/text | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.b` |
| 1133 | Tier 3 table/text | 13 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.c` |
| 1134 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.n_d` |
| 1135 | Tier 3 table/text | -0.024 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.diff` |
| 1136 | Tier 3 table/text | [-0.04, -0.01] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.ci95` |
| 1137 | Tier 3 table/text | [0.00180678, 0.338684] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.theta_ci95_exact` |
| 1138 | Tier 3 table/text | 0.0465333 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.discordance_bound_B` |
| 1139 | Tier 3 table/text | 0.0207539 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.mdd` |
| 1140 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.mdd_used` |
| 1141 | Tier 3 table/text | below | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.TM20_minus_NONE.reading` |
| 1142 | Tier 3 table/text | 8 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.b` |
| 1143 | Tier 3 table/text | 4 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.c` |
| 1144 | Tier 3 table/text | 12 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.n_d` |
| 1145 | Tier 3 table/text | 0.008 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.diff` |
| 1146 | Tier 3 table/text | [-0.006, 0.022] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.ci95` |
| 1147 | Tier 3 table/text | [0.348876, 0.900754] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.theta_ci95_exact` |
| 1148 | Tier 3 table/text | 0.0415476 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.discordance_bound_B` |
| 1149 | Tier 3 table/text | 0.0193334 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.mdd` |
| 1150 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.mdd_used` |
| 1151 | Tier 3 table/text | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-G_minus_NONE.reading` |
| 1152 | Tier 3 table/text | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.b` |
| 1153 | Tier 3 table/text | 3 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.c` |
| 1154 | Tier 3 table/text | 17 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.n_d` |
| 1155 | Tier 3 table/text | 0.022 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.diff` |
| 1156 | Tier 3 table/text | [0.006, 0.038] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.ci95` |
| 1157 | Tier 3 table/text | [0.565682, 0.962015] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.theta_ci95_exact` |
| 1158 | Tier 3 table/text | 0.0538804 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.discordance_bound_B` |
| 1159 | Tier 3 table/text | 0.0226737 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.mdd` |
| 1160 | Tier 3 table/text | True | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.mdd_used` |
| 1161 | Tier 3 table/text | above | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.contrasts.SOFT-A_minus_NONE.reading` |
| 1162 | Tier 3 d control | 0.0798082 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.contrasts.TM-G_minus_GM.mean_diff` |
| 1163 | Tier 3 d control | [0.067375, 0.0925509] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.contrasts.TM-G_minus_GM.ci95` |
| 1164 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.contrasts.TM-G_minus_GM.reading` |
| 1165 | Tier 3 d control | 0.232671 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.contrasts.TM20_minus_GM.mean_diff` |
| 1166 | Tier 3 d control | [0.204215, 0.261054] | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.contrasts.TM20_minus_GM.ci95` |
| 1167 | Tier 3 d control | above | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.contrasts.TM20_minus_GM.reading` |
| 1168 | Tier 3 d control | 0.245901 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.per_arm.NONE.mean_d` |
| 1169 | Tier 3 d control | 0.300456 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.per_arm.GM.mean_d` |
| 1170 | Tier 3 d control | 0.380264 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.per_arm.TM-G.mean_d` |
| 1171 | Tier 3 d control | 0.533127 | `runs/P2-GATE-M4/tier3_fusion.json` | `ps_cells.swap.d_control.per_arm.TM20.mean_d` |
| 1172 | Tier 3 | 46.718 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.mean_flagged` |
| 1173 | Tier 3 table | 0.88 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.arms.NONE.acc` |
| 1174 | Tier 3 table | 0.882 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.arms.GM.acc` |
| 1175 | Tier 3 table | 0.852 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.arms.MED.acc` |
| 1176 | Tier 3 table | 0.874 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.arms.TM-G.acc` |
| 1177 | Tier 3 table | 0.854 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.arms.TM20.acc` |
| 1178 | Tier 3 table | 0.88 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.arms.SOFT-G.acc` |
| 1179 | Tier 3 table | 0.884 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.arms.SOFT-A.acc` |
| 1180 | Tier 3 table | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.b` |
| 1181 | Tier 3 table | 16 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.c` |
| 1182 | Tier 3 table | 17 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.n_d` |
| 1183 | Tier 3 table | -0.03 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.diff` |
| 1184 | Tier 3 table | [-0.046, -0.014] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.ci95` |
| 1185 | Tier 3 table | [0.00148817, 0.286889] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.theta_ci95_exact` |
| 1186 | Tier 3 table | 0.0538804 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.discordance_bound_B` |
| 1187 | Tier 3 table | 0.0229591 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.mdd` |
| 1188 | Tier 3 table | True | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.mdd_used` |
| 1189 | Tier 3 table | below | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.MED_minus_GM.reading` |
| 1190 | Tier 3 table | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.b` |
| 1191 | Tier 3 table | 5 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.c` |
| 1192 | Tier 3 table | 6 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.n_d` |
| 1193 | Tier 3 table | -0.008 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.diff` |
| 1194 | Tier 3 table | [-0.018, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.ci95` |
| 1195 | Tier 3 table | [0.00421074, 0.641235] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.theta_ci95_exact` |
| 1196 | Tier 3 table | 0.0259349 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.discordance_bound_B` |
| 1197 | Tier 3 table | 0.0137269 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.mdd` |
| 1198 | Tier 3 table | False | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.mdd_used` |
| 1199 | Tier 3 table | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM-G_minus_GM.reading` |
| 1200 | Tier 3 table | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.b` |
| 1201 | Tier 3 table | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.c` |
| 1202 | Tier 3 table | 14 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.n_d` |
| 1203 | Tier 3 table | -0.028 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.diff` |
| 1204 | Tier 3 table | [-0.044, -0.014] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.ci95` |
| 1205 | Tier 3 table | [0, 0.231636] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.theta_ci95_exact` |
| 1206 | Tier 3 table | 0.0465333 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.discordance_bound_B` |
| 1207 | Tier 3 table | 0.020577 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.mdd` |
| 1208 | Tier 3 table | True | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.mdd_used` |
| 1209 | Tier 3 table | below | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.TM20_minus_GM.reading` |
| 1210 | Tier 3 table | 0 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.b` |
| 1211 | Tier 3 table | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.c` |
| 1212 | Tier 3 table | 1 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.n_d` |
| 1213 | Tier 3 table | -0.002 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.diff` |
| 1214 | Tier 3 table | [-0.006, 0] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.ci95` |
| 1215 | Tier 3 table | [0, 0.975] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.theta_ci95_exact` |
| 1216 | Tier 3 table | 0.0110925 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.discordance_bound_B` |
| 1217 | Tier 3 table | 0.00566703 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.mdd` |
| 1218 | Tier 3 table | False | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.mdd_used` |
| 1219 | Tier 3 table | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-G_minus_GM.reading` |
| 1220 | Tier 3 table | 6 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.b` |
| 1221 | Tier 3 table | 5 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.c` |
| 1222 | Tier 3 table | 11 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.n_d` |
| 1223 | Tier 3 table | 0.002 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.diff` |
| 1224 | Tier 3 table | [-0.012, 0.014] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.ci95` |
| 1225 | Tier 3 table | [0.233794, 0.832512] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.theta_ci95_exact` |
| 1226 | Tier 3 table | 0.0390226 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.discordance_bound_B` |
| 1227 | Tier 3 table | 0.0186631 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.mdd` |
| 1228 | Tier 3 table | True | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.mdd_used` |
| 1229 | Tier 3 table | not_distinguishable | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.contrasts.SOFT-A_minus_GM.reading` |
| 1230 | Tier 3 d control | 0.0334176 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.d_control.contrasts.TM-G_minus_GM.mean_diff` |
| 1231 | Tier 3 d control | [0.0292129, 0.0375602] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.d_control.contrasts.TM-G_minus_GM.ci95` |
| 1232 | Tier 3 d control | 0.323682 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.d_control.contrasts.TM20_minus_GM.mean_diff` |
| 1233 | Tier 3 d control | [0.291085, 0.355746] | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.d_control.contrasts.TM20_minus_GM.ci95` |
| 1234 | M5 | 0.0711491 | `runs/P2-GATE-M5/coherence.json` | `median_abs_gap` |
| 1235 | M5 | 0 | `runs/P2-GATE-M5/coherence.json` | `p95_abs_noise_floor` |
| 1236 | M5 | 800 | `runs/P2-GATE-M5/coherence.json` | `n_gaps` |
| 1237 | M5 | 200 | `runs/P2-GATE-M5/coherence.json` | `n_floor` |
| 1238 | M5 | 0.19884 | `runs/P2-GATE-M5/coherence.json` | `mu` |
| 1239 | M5 | False | `runs/P2-GATE-M5/coherence.json` | `coherent_within_noise` |
| 1240 | M5 | False | `runs/P2-GATE-M5/coherence.json` | `incoherent_at_evidence_scale` |
| 1241 | M5 | 0.253085 | `runs/P2-GATE-M5/coherence.json` | `by_kind.adjacent_h` |
| 1242 | M5 | 0.246322 | `runs/P2-GATE-M5/coherence.json` | `by_kind.adjacent_v` |
| 1243 | M5 | 0.031749 | `runs/P2-GATE-M5/coherence.json` | `by_kind.far` |
| 1244 | M5 | [0.0703425, 0.0735241] | `runs/P2-GATE-M5/coherence.json` | `by_context_median_abs` |
| 1245 | M5 mu | 0.19884 | `runs/P2-GATE-M5/mu_from_m4.json` | `mu_item_mean` |
| 1246 | M5 mu | 500 | `runs/P2-GATE-M5/mu_from_m4.json` | `n_items` |
| 1247 | S-DN text (denoised minus none) | 0.006 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.denoise_minus_none.y.diff` |
| 1248 | S-DN text (denoised minus none) | -0.03 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.denoise_minus_none.y.lo` |
| 1249 | S-DN text (denoised minus none) | 0.04 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.denoise_minus_none.y.hi` |
| 1250 | S-DN text (denoised minus none) | 0.176 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.denoise_minus_none.y.diff` |
| 1251 | S-DN text (denoised minus none) | 0.13 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.denoise_minus_none.y.lo` |
| 1252 | S-DN text (denoised minus none) | 0.222 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.denoise_minus_none.y.hi` |
| 1253 | PS text | 0.87 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.desc.acc_none` |
| 1254 | PS text | 0.88 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.patch.desc.acc_clean_none` |
| 1255 | PS text | 0.87 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.desc.acc_none` |
| 1256 | PS text | 0.88 | `runs/P2-GATE-M4/analysis.json` | `ps.per_corruption.swap.desc.acc_clean_none` |
| 1257 | conventions | 10000 | `runs/P2-GATE-M4/analysis.json` | `meta.bootstrap_resamples` |
| 1258 | conventions | percentile | `runs/P2-GATE-M4/analysis.json` | `meta.interval` |
| 1259 | P completeness | 500 | `runs/P2-GATE-M4/analysis.json` | `completeness.planned_n` |
| 1260 | Tier 3 d control (clean) | 0.289233 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.d_control.per_arm.NONE.mean_d` |
| 1261 | Tier 3 d control (clean) | 0.29817 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.d_control.per_arm.GM.mean_d` |
| 1262 | Tier 3 d control (clean) | 0.331588 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.d_control.per_arm.TM-G.mean_d` |
| 1263 | Tier 3 d control (clean) | 0.621852 | `runs/P2-GATE-M4/tier3_fusion.json` | `clean.d_control.per_arm.TM20.mean_d` |
| 1264 | E-pred d-scale note | False | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4.predicted_helps` |
| 1265 | E-pred d-scale note | True | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.jpeg10.prop4_refuted` |
| 1266 | E-pred d-scale note | 0.0078287 | `runs/P2-GATE-M4/analysis.json` | `mechanism.jpeg10.d.gate_minus_none.lo` |
| 1267 | E-pred d-scale note | False | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4.predicted_helps` |
| 1268 | E-pred d-scale note | True | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.noise0.1.prop4_refuted` |
| 1269 | E-pred d-scale note | 0.00296848 | `runs/P2-GATE-M4/analysis.json` | `mechanism.noise0.1.d.gate_minus_none.lo` |
| 1270 | E-pred d-scale note | False | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4.predicted_helps` |
| 1271 | E-pred d-scale note | True | `runs/P2-GATE-M4/analysis.json` | `calibration.per_condition.splice128.prop4_refuted` |
| 1272 | E-pred d-scale note | 0.00687367 | `runs/P2-GATE-M4/analysis.json` | `mechanism.splice128.d.gate_minus_none.lo` |
| 1273 | E-pred order | 1793209194 | `runs/P2-GATE-M4/epred_score.json` | `order_check.frozen_commit_time` |
| 1274 | E-pred order | 1.79321e+09 | `runs/P2-GATE-M4/epred_score.json` | `order_check.first_m4_chunk_start` |

## Notes for the auditor

1. `analysis.json` `calibration.per_condition.<P cell>.prop4_refuted` is `true` for all three P cells. It is computed on the evidence
   ratio d (`analysis_m4.py:597-602` uses `mechanism[k][endpoint]` with endpoint d), whereas AB.3 item 3 fixes the observed sign on Y;
   `epred_score.json` (the AB.3 module) has `refutation_rule_met_for_cells: []`. The paper follows `epred_score.json` and reports the
   d-scale disagreement descriptively in the E-pred subsection, without the word "refuted".
2. Family S-M tested nothing (gatekept by P; `s_m.per_corruption.*.tested = false`); the Y-scale mechanism contrasts in Table
   tab:res_mech are the Tier-3 `mechanism.*` paired bootstrap intervals (no p-value), with random gates averaged over three seeds
   (`analysis_m4.py:392-411`).
3. PS `positive_control = "not met"`: the paper uses the AB.1 wording and leaves an AUTHOR/RESULT placeholder for the audit outcome.
4. Coherence (M5): neither pre-stated reading applies (`coherent_within_noise = false`, `incoherent_at_evidence_scale = false`; noise
   floor p95 = 0.0). The adjacent-pair medians (0.253, 0.246) exceed mu (0.199); reported as descriptive, not as a reading.
5. No number from S2 (`runs/P2-GATE-S2`), FOIL (`runs/P2-GATE-FOIL*`), Omni or the suite is used; R is reported as not run (P+ empty).
