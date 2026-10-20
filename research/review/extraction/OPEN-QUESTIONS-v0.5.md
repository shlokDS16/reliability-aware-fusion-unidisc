# Open questions for the human author: extraction and appraisal form v0.5 (2026-10-20)

Each item names the gap, the options with their numbers, and where the plan uses the answer. **Decision row**
= needs a row in `research/ledgers/decisions.jsonl` (entered by the orchestrator) before the stage named.
The drafting agent decided none of them. Token figures are inference (E0); every probability is a simulation
of an E0 model (logs in `analysis/extraction/`). Items of OPEN-QUESTIONS-v0.4.md not repeated here stay open as
written there (part E).

## A. Scope

**OQ5-04 Human check before any draw (about 1.5-2.5 hours; replaces OQ4-04).** As OQ4-04 items 1-4, and item
4 now also covers the 20 C2 records that are neither side-experiment ids nor carry a multimodal benchmark or
diffusion-LM name in the body (red-team mi6; `mm_c2_nohit_v05-log.txt`): M01397 M04245 M04407 M05954 M08275
M08783 M08804 M09403 M10855 M13342 M13470 M13774 M15668 M16116 M17332 U00130 U00134 U00173 U00398 U04330.
These 20 are checked under every option of OQ4-03 (each coded joint-model, side-experiment or text).

## B. Gate

**OQ5-02 Sign agreement: report-only or gated (decision row, before Stage B).** Counted over sign decisions
(the level at which the sign is set), M-sign's intra-record correlation cannot be estimated from 60 records:
its 80 percent bound sits at the grid maximum 0.60 in most gates even when the true value is 0.10
(`gate_rule_v05-log.txt`). Its pass probability at the good level is 0.82 at n 60 and 0.76-0.95 at n 120.

| Option | What it does | P(pass, all good) | Gate size |
|---|---|---|---|
| (i) report-only (plan v0.5 s10.3) | sign set by KA1; the validator rejects arrow conflicts and inconsistent signs; every sign that rests on the extractor alone or conflicts with the lookup goes to EC in every record | B-IP v0.5: 0.884-0.983 over 12 scenarios | mean n 91-120 |
| (ii) gated, levels 0.97 / 0.90 | as v0.4, counted over sign decisions | fixed n 120: 0.944 (ICC 0.10), 0.871 (0.20), 0.778 (0.30), 0.707 (H1), 0.645 (H10); product approximation | 120 in nearly every gate; the target cannot be certified |

Recommendation: (i). Under (ii) the gate's size and verdict would be driven by one criterion the gate cannot
measure; under (i) the sign is checked record by record against the paper's arrows and the lookup.

**OQ5-07 Gate design and budget (decision row, before Stage B; replaces OQ4-07).** Design B-IP v0.5: 60
records, per-metric bounds on them, extension to the smallest grid n whose product of marginal pass
probabilities reaches 0.85, at most n_cap. Rules simulated on the same replicates (`gate_bip_v05_summary-log.txt`):

| Rule | P(pass, all good), 12 scenarios | Largest P(pass, one bad) | Mean n (ICC 0.10) | Expected gate cost at ICC 0.10 | Warning when 0.85 is out of reach |
|---|---|---|---|---|---|
| P80 (binding: chosen by the criterion fixed before the run) | 0.884-0.983 | 0.074 | 99.4 | 17.5M-30.8M | P(step 6) 0.81-0.85 in H10, HG, G30 |
| P50 (median bounds) | 0.876-0.945 | 0.069 | 73.8 | 13.0M-22.9M | 0.23-0.38 in the same scenarios |
| X80 (largest bound, common grid) | 0.885-0.995 | 0.075 | 118.2 | 20.8M-36.6M | none (fixed 120 in practice) |
| V4 (v0.4 rule, for reference) | 0.819-0.927 | 0.070 | 72.6 | 12.8M-22.5M | none |

Also decide **n_cap** (red-team MA4): approve the budget at n_cap = 120 (gate component up to 21.1M-37.2M), or
set n_cap to the largest grid n whose upper cost fits (105: 32.6M; 90: 27.9M; 72: 22.3M). With n_cap 90 the
common-ICC grid gives P(pass | good) at n 90 of 0.988 (ICC 0.05), 0.960 (0.10), 0.899 (0.20), 0.793 (0.30);
a capped design must be re-simulated (gate_bip_v05.py with the capped config) before the B2 row. The cap
cannot change after phase 1 starts.

**OQ5-08 Gate levels (decision row, before Stage B; replaces OQ4-08).** As OQ4-08, with v0.5 changes: M-pool
over matched groups (0.85 / 0.70, line 0.71, P(passes | bad) 0.049); K-attr as the mean of four fields (0.85 /
0.70, line 0.71, 0.029); credited_ablation alone printed with line 0.71 (report-only; gating it as a 20th
criterion lowers P(pass | good) at n 60, ICC 0.10 from 0.854 to 0.799). G1 EA/EB lines sit at the bad level
0.85, where the criterion passes a bad G1 in 0.071-0.075 of gates (`gate_oc_v05-tableA-log.txt`); this is the
largest one-bad value of the design (0.074). Raising G1's line to 0.86 would need a calibration run and a
rerun of the grid and of gate_bip_v05.py. Any level change reruns s10.6 before the B2 row.

## C. Unit rules

**OQ5-13 Attribute rules KA1-KA4 (row 36, before Stage A).** Brief v0.5 block K:
- KA1 higher_is_better: printed arrow or statement; else a fixed convention list (identical to the metric
  lookup); else null with doubt. Never from bold numbers or from knowledge outside the list.
- KA2 budget_across_arms: items = steps or NFE, and generation length; an autoregressive arm's steps are its
  length; matched = both stated and equal for every arm (or stated as the same); reported = steps stated for
  every arm, not matched; not reported = steps missing for an arm. Wall time and FLOPs are not budget items.
- KA3 scoring: likelihood when the group's quality units are likelihood metrics or the paper says so; else
  generated when a generated-sample unit exists; else not_stated.
- KA4 credited_ablation: true for removal or replacement of the credited component; false for parameter
  sweeps, sub-component removals, model-class groups and analysis, benchmark or theory papers.
Approve or amend. The KA2 choice that matters most: for diffusion against autoregressive groups, "matched"
requires the diffusion arm's steps to equal the generation length, so many such groups will be "reported" and
leave RQ2 pooling (K15).

## D. Process

**OQ5-16 Red-team review of v0.5 (plan s14 A6).** Parts to attack first: M-sign as report-only and its
process guarantee (s10.3), the product rule and its grid (s10.7, bip-grid-v2.json), the selection criterion of
s10.6, the 5-gram allowlist (brief_contamination_v05.py), KA2's treatment of autoregressive arms.

**OQ5-17 Commit.** The v0.5 files, eight scripts, config, grid, results and logs are written but not committed.

## E. Still open
From v0.4: OQ4-03 multimodal construct; OQ4-10 anchor clauses; OQ4-11 figure conditions; OQ4-12 unmapped
strings. From v0.3: OQ3-01, OQ3-02, OQ3-05, OQ3-06, OQ3-09 (budget ceiling: the gate component is now up to
21.1M-37.2M at n_cap 120), OQ3-10 to OQ3-16. From v0.2: OQ2-07 to OQ2-12, OQ2-15 to OQ2-23 as listed in
OPEN-QUESTIONS-v0.3.md part E.
