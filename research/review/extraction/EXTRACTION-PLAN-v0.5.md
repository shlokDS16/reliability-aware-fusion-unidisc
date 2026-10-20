```yaml
agent: method-architect
date: 2026-10-20
brief: revise the extraction and appraisal instrument from v0.4 to v0.5 after red-team audit 4 (Paper 1); coding rules for the gated K attributes and a stronger contamination check (MA2), gate size from per-metric ICC bounds with a whole-procedure simulation over heterogeneous ICC (MA1), pinned and hashed decision inputs (MA3), a budget rule fixed before phase 1 (MA4), minors; no extraction run, no sample drawn
sources_examined:
  - research/CONTRACT.md
  - research/review/audits/2026-10-20-redteam-extraction-v0.4.md (all 11 findings) and its scripts hetero.py, shingle.py
  - research/review/extraction/EXTRACTION-PLAN-v0.4.md, OPEN-QUESTIONS-v0.4.md, RESPONSE-TO-REDTEAM-v0.3.md (head); extractor-brief-v0.4.md l.1-195, 380-560; extraction-schema-v0.4.json (fields higher_is_better, budget_across_arms, scoring, credited_ablation, held_fixed); EXTRACTION-PLAN-v0.3.md s10.4-s10.5
  - analysis/extraction/gate_oc_v04.py, gate_adaptive_v04.py, icc_check.py, brief_contamination.py, make_schema_v04.py, multimodal_options.py (read; unchanged) and their logs
  - all 608 include texts by script (brief_contamination_v05.py); the T1 screening files by script (mm_c2_nohit_v05.py)
coverage: >
  Every number below comes from a script in analysis/extraction/ run on 2026-10-20 with its log beside it
  (Appendix A). Not read: the worked-example papers (v0.4's lists stand; they hold keys and anchors, not the
  K attributes), the C2 full texts, protocol.md. Token figures are inference (E0). No ledger row was added:
  the brief allows writes only in research/review/extraction/ and analysis/extraction/.
claims:
  - statement: Under the v0.5 gate model, design B-IP with per-metric 80 percent Neyman bounds and the product rule (P80) passes an instrument at every good level with probability 0.884-0.983 over 12 scenarios (ICC common 0.05-0.30; the red-team's H1 0.922 and H10 0.884; six other patterns, five with ICC differing by metric), and an instrument with one quantity at its bad level with probability at most 0.074.
    status: supported
    evidence: analysis/extraction/gate_bip_v05.py, logs gate_bip_v05-log.txt and gate_bip_v05_summary-log.txt (1,000 replicates per scenario, R 1,000, seeds 20265500 + 10 s + c)
    level: E3 (simulation of an E0 model)
    confidence: 0.75
  - statement: The v0.4 sizing rule (Neyman bound of the mean ICC) gives P(pass | good) 0.819-0.846 in five of the eight non-common-ICC scenarios of the same run.
    status: supported
    evidence: gate_bip_v05_summary-log.txt rows HG, HP, H10, H1, H3 (rule V4)
    level: E3
    confidence: 0.75
  - statement: Counted over sign decisions, M-sign's intra-record correlation is not identifiable from 60 records; the per-metric 80 percent bound has median 0.60 (the grid maximum) when the true ICC is 0.10.
    status: supported
    evidence: gate_rule_v05-log.txt coverage table; gate_bip_v05-log.txt median U80 per metric
    level: E3
    confidence: 0.85
  - statement: The v0.5 session text holds none of the 17 known strings and no specific quoted span, number, number run or word 5-gram outside a reviewed allowlist; the same check finds one non-allowlisted 5-gram in v0.4.
    status: supported
    evidence: analysis/extraction/brief_contamination_v05.py, log brief_contamination_v05-log.txt (exit code 0)
    level: E3
    confidence: 0.9
competing_explanations:
  - Real per-metric ICCs and unit counts may differ from every scenario simulated; Stage A and B1 replace the unit counts, and the step-6 statement reports when the bounds say the target is out of reach.
unknowns:
  - real ICC per metric, units per record, agreement on the KA-coded fields (Stage A, then gate phase 1)
  - whether the human author keeps M-sign report-only (OQ5-02) and which n_cap the budget allows (OQ5-07)
next_test: {hypothesis: "two extractors following brief v0.5 agree on groups, anchors and K attributes at the good levels", intervention: "Stage A (12 records), then gate design B-IP v0.5 (rule P80)", primary_metric: "F1_G on the 7 drawn Stage A records; the 18-criterion rule of s10.4 at the n of s10.7", falsifier: "F1_G below 0.6 on the 7 drawn records, or any gated criterion missed after one re-gate", gpu_hours: 0}
```

# Extraction and quality-appraisal plan, form v0.5 (draft, 2026-10-20; not frozen)

Status: a specification. Nothing here is a result about any paper. No extraction has been run and no sample
has been drawn. Earlier versions stay as they are, and every v0.3 and v0.4 script and log is unchanged.
Every finding of red-team audit 4 is answered in `RESPONSE-TO-REDTEAM-v0.4.md`. **This file is a delta on
EXTRACTION-PLAN-v0.4.md**: a section not written here applies as written in v0.4 (and through it, v0.3 and
v0.2). Section map:

| Section | Binding text |
|---|---|
| s1 changes; s2.3 (mi6 addition); s2.8 cost; s2.10 seeds; s4 schema; s5.2 H key order; s5.4 lookup direction list; s10.2 Stage A; s10.3 metrics; s10.4 rule; s10.6 OC; s10.7 design B-IP v0.5; s10.8 pinned inputs; s11 tools; s13 rows 36-42; s14 checklist; Appendix A | this file |
| s2.1-s2.3 (options), s5.3, s10.5, s12, s13 rows 31-35 | v0.4 |
| s2.4-s2.7, s2.9, s5.1, s5.5-s5.7, s6-s9, s13 rows 1-30 | v0.3 (through v0.4) |
| field table, roles, isolation, QA rubric | v0.2 as amended by v0.3 |

## 1. What changed from v0.4

1. **Coding rules for the gated fields (MA2).** Brief v0.5 block K gains attribute rules KA1 (higher_is_better:
   printed direction, then a fixed convention list, then null), KA2 (budget_across_arms: two budget items,
   steps or NFE and generation length; matched, reported, not reported defined), KA3 (arm scoring tied to G5),
   KA4 (credited_ablation for every group type), each with a synthetic example; credited_ablation is added to
   the group field list. Schema v0.5 points the four fields to KA1-KA4 (s4).
2. **Contamination check (MA2, mi3).** `brief_contamination_v05.py` scans quoted spans in every quote style,
   decimals and integers, number runs, and every word 5-gram of the session text against the 608 include
   texts (ligatures and line-end hyphens normalised); a specific hit not on a reviewed allowlist fails the exit
   code. v0.5 passes; v0.4 fails on one caption 5-gram, which v0.5 rewords.
3. **Measurement level (MA1).** M-pool is counted over matched groups and M-sign over sign decisions
   ((matched group, metric key) pairs), the levels at which the two values are set; K-attr is the mean of four
   per-field agreements (mi2). M-anchorG matches arms one-to-one (mi1).
4. **M-sign becomes report-only (MA1, MA2).** At the decision level its ICC cannot be estimated from 60 records
   (bound at the grid maximum in most replicates even when the true ICC is 0.10), so any worst-case sizing
   rule would always demand n = 120 with a target it cannot certify. The sign is instead secured by process:
   KA1, three validator checks and EC review of every extractor-only or conflicting sign (s10.3). Keeping it
   gated is option (ii) of OQ5-02, with its numbers.
5. **Gate size from per-metric bounds (MA1).** At phase 1 a Neyman 80 percent bound is computed for each of
   20 ICC metrics; the gate size is the smallest grid n at which the product of the criteria's marginal pass
   probabilities, each at its own bound, reaches 0.85 (rule P80, s10.7). Whole procedure simulated with
   1,000 replicates per scenario and R = 1,000 as in production (mi5), over 12 good and 15 one-bad scenarios
   including the red-team's H1 and H10.
6. **Pinned decision inputs (MA3).** Every level, line, unit count, the n grid, the bound settings and seeds
   are in `gate-config-v05.json`; the marginal grid is `bip-grid-v2.json` (stamped with a model hash); the
   decision function is `gate_rule_v05.py`. agreement.py and the gate scripts take config and grid as
   inputs; the B2 row records all hashes (s10.8).
7. **Budget rule fixed before phase 1 (MA4).** n_cap is 120 unless the B2 row sets a lower grid value from the
   approved budget; the budget check uses the n_cap cost, not n_plan; gate-phase1 output is limited to bounds,
   P_hat(n) and n; record replacement and the re-gate exclusion are fixed (s10.7).
8. **Minors.** Lookup-fallback check on records outside Stage A (mi4); the 20 unchecked C2 ids added to the
   human check (mi6); stale and garbled text fixed, H-key match order and re-gate exclusion stated (mi7).

## 2. Scope

### 2.3 Addition (mi6)
The human check of OQ4-04 item 4 (now OQ5-04 item 4) also codes the 20 C2 records that are neither
side-experiment ids nor carry a multimodal benchmark or diffusion-LM name in the body
(`mm_c2_nohit_v05.py`, log `mm_c2_nohit_v05-log.txt`; C2 hash asserted equal to multimodal_options-log.txt):
M01397 M04245 M04407 M05954 M08275 M08783 M08804 M09403 M10855 M13342 M13470 M13774 M15668 M16116 M17332
U00130 U00134 U00173 U00398 U04330 (U04330 is also one of the three i1 a/ab records of item 2). This applies
under every option (a)-(d): under (b) they are checked to confirm the C2 label is not an artefact of the
screening field.

### 2.8 Cost additions (gate component; E0)
Gate record cost 176k-310k tokens (cost_options_v04-log.txt). Under design B-IP v0.5 (rule P80) the expected
gate component is mean n × that cost (gate_bip_v05-log.txt): **16.0M-28.2M** at ICC 0.05 (mean n 91.0),
**17.5M-30.8M** at 0.10 (99.4), 20.2M-35.6M at 0.20 (114.8), 21.0M-37.0M at 0.30 (119.3); in the
heterogeneous scenarios 16.9M-37.1M. The maximum, which the budget check uses (s10.7 step 1), is the n = 120
cost **21.1M-37.2M**. v0.4's expected 12.5M-22.0M at ICC 0.10 came from a design that the v0.5 model shows
under-sized when the ICC differs between metrics. The mi4 lookup check (s10.2) adds 5 single-session K
extractions, about 0.2M-0.4M (5 × EA K-block cost 40k-80k, cost_options_v04 inputs; E0).

### 2.10 Seed table (replaces v0.4 s2.10)
Python 3.14.3 pinned. Unchanged from v0.4 except the rows marked new.

| Purpose | Seed |
|---|---|
| Stage A draw | 20261100 |
| Gate draw, stratum h = 0, 1, 2 (one ordered list of 40 per stratum) | 20261200 + h |
| Re-gate draw | 20261300 + h |
| Frame-R sample, T1, stratum h = 0..3 | 20261400 + h |
| Later tranche t = 1..9, stratum h | 20261500 + 10 t + h |
| ER draw, part p | 20261600 + p |
| EC labels X/Y | 20261700 |
| Gate bootstrap | 20261800 |
| Production bootstraps | 20261900 |
| gate_oc.py (v0.3), historical | 20262000-20262999 |
| gate_oc_v04.py, gate_adaptive_v04.py, historical | 20263000-20263999 |
| icc_check.py simulation | 20264000-20264899 |
| Per-metric Neyman bounds: Stage A / gate phase 1 / re-gate phase 1 | 20264900 / 20264901 / 20264902 |
| **new** gate_oc_v05.py simulations (calibrate 0-99, table A 100-199, grid 200-399, --icc-json 400-449) | 20265000-20265499 |
| **new** gate_bip_v05.py (20265500 + 10 × scenario + chunk) | 20265500-20265899 |
| **new** gate_rule_v05.py self-tests and coverage | 20265900-20265999 |
| Human gold subset | 20266100 |
| **new** mi4 lookup-check draw (5 frame-R ids, s10.2) | 20266200 |
| agreement.py self-tests | 20267000 |

## 4. Schema v0.5 (`make_schema_v05.py`; extraction-schema-v0.5.json, sha256 b021c041c26cf5482b22876ba68e8fcec331d0cd9e8e6ba33387bcb0ca0bbc1c; Draft 2020-12 check_schema ok)

form_version const "0.5"; descriptions of higher_is_better (H and K units), budget_across_arms, scoring and
credited_ablation point to KA1-KA4. No field added or removed (property entries 351 before and after; the
plan's field count stays 153).

## 5. Units

### 5.2 H key: order of matching (mi7)
agreement.py matches H units in two passes inside each (where, row group, row label) key: (1) pairs whose
cells are both column-verified by the validator (s6.3 item 9) match on the leaf position col, one-to-one in
reading order; (2) every unit left unmatched is then keyed by the U11-normalised leaf parts of
column_printed and matched one-to-one. Column-verified is a property of each reader's cell, read from the
validator report before any matching.

### 5.4 Metric lookup and the sign (MA2)
The lookup's alias list and higher_is_better column are exactly KA1(b): higher is better for accuracy (acc,
acc.), exact match (EM), pass@k, BLEU, ROUGE-L, CIDEr, CLIP score, tokens per second (TPS), tokens per forward
(TPF), speed-up; lower for perplexity (PPL), NLL, bits per token, FID, latency, number of steps, NFE. A metric
id added from Stage A gets a direction only if its direction is not paper-dependent; otherwise null. The
brief and the lookup are hashed together in the B2 row, so the two lists cannot drift apart.

## 10. Pilot and gate

### 10.2 Stage A (additions to v0.4 s10.2)
- Sessions get brief v0.5 and schema v0.5 (A12: brief_contamination_v05.py exit code 0 on the frozen files).
- agreement.py reports, for every ICC metric of the config (20: s10.7), the ANOVA ICC and the per-metric
  Neyman 80 and 50 percent bounds (gate_rule_v05.neyman_upper, seed 20264900), on the 12 records and on the 7
  drawn, plus the v0.4 pooled value for comparison. These are reported only: no gate size is fixed from them
  (s10.7 step 1).
- Per-field agreement of KA1-KA4 is reported with the share of null against value, so the red-team's MA2
  rejection test (M-sign below 0.90, or budget_across_arms or credited_ablation below 0.70 with mostly null
  against value) is computed.
- **mi4 lookup check.** After the lookups are seeded from Stage A and before the B2 row, 5 frame-R ids drawn
  with seed 20266200 (excluding Stage A ids and every id on the gate's ordered lists, which B4 draws first)
  are extracted once by one EA session (block K only). The share of their K units with a raw key part is
  reported. Above 0.05, the lookups are revised once (aliases added from those 5 records) and the share is
  recomputed on them; the revision is a pre-gate change, recorded in the B5 hashes.

### 10.3 Stage B metrics (changes to v0.4 s10.3)
- **M-anchorG (mi1).** Per matched group (U13): each reader's anchor_arm id is mapped through the one-to-one
  arm match of that group (U11 label, then label-core, one-to-one by reading order). Credit 1 when both are
  null, or both map to the same matched arm pair; an anchor whose arm is unmatched, or two arms sharing one
  key, counts as disagreement. The share of null-null pairs is reported beside the value.
- **M-pool (MA1).** Over matched groups, not K units: agreement of each reader's derived K15 matched flag
  (held_fixed stated, other_changes '', and for RQ2 budget_across_arms matched and every arm's scoring equal
  and stated). The K-unit-weighted value is reported as a diagnostic.
- **K-attr (mi2).** The mean of four per-field agreements, each pooled separately: held_fixed,
  budget_across_arms, credited_ablation (matched groups) and scoring (matched arms). Line 0.71
  (gate_oc_v05-calibrate-log.txt: P(passes | bad) 0.029 at n 60, ICC 0.10). credited_ablation alone is a
  report-only line (0.71; P(passes | bad) 0.045): a single bad field leaves K-attr passing (gate_oc_v05-tableA-log.txt:
  joint P 0.845-0.856 with one field at 0.70), so the per-field lines are printed in the verdict and a field
  below its line is a flagged field (v0.3 s10.5 PASS branch: revised and re-measured in production).
- **M-sign (MA1, MA2): report-only.** Counted over sign decisions, the (matched group, metric key) pairs both
  readers have, null against value counted as disagreement, null-null excluded; line 0.92 printed, not gated
  (calibrated: P(passes | bad 0.90) 0.030 at n 60). Reason: gate_rule_v05-log.txt shows its per-metric bound
  at the grid maximum (median 0.60) when the true ICC is 0.10, 0.30 or 0.50, and its marginal pass
  probability at the good level is 0.82 at n 60 and 0.76-0.95 at n 120 (bip-grid-v2.json). The sign is
  secured instead by: (1) KA1; (2) ex_validate rejects (returned once, E5) a K unit whose column_printed
  carries an arrow that contradicts its higher_is_better, and units of one group with the same metric key and
  different values; (3) every K unit whose final sign rests on an extractor value alone (metric unmapped or
  lookup direction null) or conflicts with the lookup direction goes to EC, in every record, single- or
  double-extracted; the share is reported in each production verdict.
- Diagnostics added: per-field agreement inside K-attr with its own LB90; null-null share of M-anchorG;
  K-unit-weighted M-pool; M-sign with its LB90; share of sign values that came from KA1 step (a), (b), (c).

### 10.4 Decision rule (replaces v0.4 s10.4; fixed before the gate; signed by gate-auditor)
**PASS iff every one of the 18 gated criteria holds** on the n records that s10.7 sets. Levels, lines and the
G5 counts are as v0.4 s10.4 except:

| Criterion | Change | Good | Bad | Line |
|---|---|---|---|---|
| G3 K-attr | mean of four per-field agreements | 0.85 | 0.70 | LB90 >= 0.71 |
| G4 M-anchorG | arms matched one-to-one (mi1) | 0.85 | 0.70 | LB90 >= 0.71 |
| G4 M-pool | over matched groups | 0.85 | 0.70 | LB90 >= 0.71 |
| G4 M-sign | over sign decisions; **report-only** | 0.97 | 0.90 | 0.92 (printed) |
| D credited_ablation alone | report-only | 0.85 | 0.70 | 0.71 (printed) |

The machine-readable table is `gate-config-v05.json` (criteria block); the B2 row cites its hash. The human
author approves or changes every level there (OQ5-08); any change reruns s10.6 before the B2 row.

### 10.6 Operating characteristics (v0.5 model; all inputs E0)
Model as v0.4 s10.6 with the measurement levels of s10.3: M-sign over sign decisions (per record
min(matched K units, c + Poisson(0.6 c)), c = matched groups, at least 1), M-pool and the three group fields
of K-attr over matched groups, scoring over matched arms (2 per matched group + Poisson(1.2 per group));
every criterion has its own ICC. Scripts gate_oc_v05.py (fixed n), gate_rule_v05.py (bounds and rule),
gate_bip_v05.py (whole procedure).

**Table A. Fixed n = 60, ICC 0.10, 2,000 simulated gates (gate_oc_v05-tableA-log.txt).** P(pass | every
quantity good) **0.854** (MC s.e. 0.008); lowest marginals M-anchorG 0.934, M-pool 0.936, F1_G 0.985,
M-class 0.993 (report-only M-sign 0.801). One gated quantity bad: 0.009-0.066 (largest G1 EB). Sensitivity:
OMEGA 0.5 0.926; NB shape 0.7 0.785.

**Table B. Common-ICC grid (bip-grid-v2.json, 2,000 per cell; gate_oc_v05-grid-log.txt).** Joint P(pass | good):

| ICC | n 60 | 72 | 90 | 105 | 120 |
|---|---|---|---|---|---|
| 0.05 | 0.911 | 0.953 | 0.988 | 0.993 | 0.997 |
| 0.10 | 0.864 | 0.920 | 0.960 | 0.984 | 0.993 |
| 0.20 | 0.713 | 0.814 | 0.899 | 0.945 | 0.973 |
| 0.30 | 0.517 | 0.659 | 0.793 | 0.871 | 0.922 |
| 0.40 | 0.372 | 0.507 | 0.658 | 0.741 | 0.832 |
| 0.60 | 0.166 | 0.267 | 0.406 | 0.530 | 0.638 |

The product of the 18 gated marginals differs from the simulated joint by -0.011 to +0.006 over the 55 cells:
the independence approximation the product rule uses is accurate within the model.

**Table C. Per-metric Neyman 80 percent bound on 60 phase-1 records (gate_rule_v05-log.txt, 200 replicates
per cell).** U median [10%, 90%] and coverage P(true <= U):

| Metric | true 0.10 | true 0.30 | true 0.50 |
|---|---|---|---|
| M-sign (sign decisions) | 0.60 [0.28, 0.60], 1.00 | 0.60 [0.48, 0.60], 0.98 | 0.60 [0.60, 0.60], 0.97 |
| M-anchorG / M-pool (matched groups) | 0.24 [0.12, 0.48], 0.99 | 0.46 [0.24, 0.60], 0.81 | 0.60 [0.40, 0.60], 0.83 |
| F1_G (union groups) | 0.16 [0.06, 0.26], 0.77 | 0.38 [0.24, 0.50], 0.79 | 0.58 [0.46, 0.60], 0.81 |
| M-val | 0.14 [0.08, 0.26], 0.81 | 0.46 [0.28, 0.60], 0.87 | 0.60 [0.52, 0.60], 0.93 |

The bound covers at about its nominal level where the metric has enough units, and is uninformative for
M-sign. The bisection search equals the full scan in 0.79 of 24 test data sets and differs by one grid step
(0.02) otherwise (MC noise; both are Monte Carlo).

**Table D. Design B-IP v0.5, whole procedure (gate_bip_v05-log.txt; 1,000 replicates per scenario; summary
in gate_bip_v05_summary-log.txt).** P(pass | every quantity good) [MC s.e. about 0.005-0.012] and mean n by
sizing rule; reach = product of the marginals at the scenario's true ICC vector at n = 120 (the most any rule
capped at 120 can give):

| Scenario (ICC) | reach | P80 (binding) | P50 | X80 | V4 (v0.4 rule) |
|---|---|---|---|---|---|
| G05 all 0.05 | 0.997 | **0.975**, n 91.0 | 0.920, 67.4 | 0.993, 114.4 | 0.910, 63.8 |
| G10 all 0.10 | 0.993 | **0.969**, 99.4 | 0.924, 73.8 | 0.991, 118.2 | 0.927, 72.6 |
| G20 all 0.20 | 0.973 | **0.946**, 114.8 | 0.898, 95.3 | 0.961, 120.0 | 0.894, 94.6 |
| G30 all 0.30 | 0.924 | **0.904**, 119.3 | 0.877, 110.9 | 0.906, 120.0 | 0.877, 111.6 |
| H1: M-sign, M-pool 0.5; others 0.10 | 0.906 | **0.922**, 118.1 | 0.902, 107.9 | 0.922, 119.9 | 0.839, 94.1 |
| H10: M-sign, M-pool 0.6; M-anchorG 0.3; others 0.10 | 0.850 | **0.884**, 119.7 | 0.876, 116.4 | 0.885, 120.0 | 0.833, 104.2 |
| H2: F1_G 0.40; others 0.10 | 0.974 | **0.968**, 108.9 | 0.919, 88.9 | 0.977, 119.9 | 0.897, 84.5 |
| H3: M-anchorG 0.40; others 0.05 | 0.936 | **0.963**, 113.7 | 0.926, 94.9 | 0.969, 119.4 | 0.846, 73.2 |
| H6: L/Q/H and G1 0.40; others 0.05 | 0.997 | **0.983**, 96.3 | 0.945, 73.7 | 0.995, 114.5 | 0.891, 64.3 |
| N07: all 0.10, NB shape 0.7 | 0.993* | **0.956**, 100.5 | 0.884, 74.0 | 0.989, 118.4 | 0.883, 73.7 |
| HG: M-anchorG, M-pool, M-class 0.40; others 0.10 | 0.863 | **0.887**, 119.3 | 0.883, 113.1 | 0.890, 120.0 | 0.819, 99.5 |
| HP: M-pool 0.50; others 0.05 | 0.906 | **0.935**, 117.6 | 0.921, 106.4 | 0.941, 119.8 | 0.824, 77.4 |

(*grid made with NB shape 1.5; approximate.) P80 rows can exceed reach because reach is a product
approximation and the procedure's n is 120 in most of those replicates. n distribution under P80 (share of
60/72/90/105/120): G05 0.02/0.26/0.42/0.18/0.12; G10 0.00/0.09/0.42/0.22/0.26; G20 0.00/0.00/0.07/0.19/0.73;
H1 0.00/0.00/0.03/0.06/0.91; H10 0.00/0.00/0.00/0.01/0.99. P(step-6 statement) under P80: 0.02 (G05), 0.06
(G10), 0.39 (G20), 0.84 (G30), 0.36 (H1), 0.81 (H10), 0.85 (HG).

One quantity bad, others good (P(pass) under P80; 1,000 replicates, MC s.e. about 0.007): at ICC 0.10, F1_G
0.061, M-anchorG 0.040, M-pool 0.043, K-attr 0.017, M-class 0.061, G1 EB 0.051, F1_K 0.060, M-val 0.026; M-pool
bad under H1 0.051, under H10 0.048, under HP 0.053; M-anchorG bad under H10 0.037; at ICC 0.30, F1_G 0.059,
M-anchorG 0.044, G1 EB **0.074**. The largest (G1 EB, ICC 0.30, n about 120) matches G1's own fixed-n
behaviour at its line, which sits at the bad level (Table A: P(G1 EB passes | bad) 0.075 at n 60): it is a
line property of G1, not optional stopping (OQ5-08 offers line 0.86). No inflation of false passes by the
size choice is detected at MC s.e. about 0.007: every P80 one-bad value is at most 0.007 above the rule X80
(n = 120 in nearly every replicate) on the same replicates, and 8 of the 15 are below it.

**Choice of rule (criterion fixed before the run).** Among P80, P50 and X80: keep the rules with P(pass |
good) >= 0.85 - 2 MC s.e. in every scenario whose reach is >= 0.85, P(step 6) >= 0.80 in every scenario whose
reach is below 0.85, and max P(pass | one bad) <= 0.08; select the smallest mean n over the good scenarios.
P80 meets it (mean n 109.9); X80 meets it (118.7); P50 fails it only on H10, whose reach is 0.850 by the
product approximation (just below 0.85 in floating point), where its step-6 rate is 0.37 although its P(pass)
is 0.876 (mean n 93.6, max one-bad 0.069). **P80 is binding.** P50 is a cheaper option for the human author
(OQ5-07), at about 16 fewer records (2.9M-5.1M) on average and a weaker warning when the target is out of
reach.

**M-sign gated instead (OQ5-02 option ii), product approximation at the true ICC vector:** n 60: 0.705 at
ICC 0.10; n 120: 0.961 (ICC 0.05), 0.944 (0.10), 0.871 (0.20), 0.778 (0.30), 0.707 (H1), 0.645 (H10). Because
M-sign's bound is uninformative, a worst-case rule would set n = 120 in nearly every gate and could never
certify the target.

### 10.7 Design B-IP v0.5 (replaces v0.4 s10.7; MA1, MA3, MA4)
All inputs are the declared files of s10.8. No step after phase 1 needs a human choice.
1. **Budget (MA4), before Stage B.** The G7 projection uses the n_cap gate cost: 21.1M-37.2M for n_cap = 120.
   The B2 row either approves the budget at n_cap = 120, or sets n_cap to the largest grid n in {60, 72, 90,
   105} whose upper gate cost (n × 310k) fits the approved budget; n_cap is written into the config copy that
   the B2 row hashes and never changes afterwards. If the projected total at n_cap exceeds the budget, the
   fallback ladder of v0.3 s10.5 is applied before Stage B, on that cost. Stage A's bounds (s10.2) are
   reported in the B2 row but set nothing.
2. **Phase 1.** draw_pilot.py draws one ordered list of 40 ids per stratum (seed 20261200 + h). Positions 1-20
   per stratum are extracted, validated and adjudication-blind as in v0.3 s10.3. A record whose sessions fail
   twice (isolation, model check or schema; v0.3 s10.5) is replaced by the next unused id of its stratum's
   list, and the replacement is logged; no other replacement is allowed.
3. **Bounds.** agreement.py --mode gate-phase1 computes, on the 60 phase-1 records only, the per-record (x, m)
   of each of the 20 ICC metrics in the config's order and their Neyman 80 percent bounds U_m
   (gate_rule_v05.phase1_bounds: R 1,000, grid 0.02-0.60, bisection, one Generator with seed 20264901).
4. **Set n.** theta_c = max of U_m over the criterion's icc_from list; P_hat(n) = product over the 18 gated
   criteria of the grid marginal at theta_c; n = the smallest grid n <= n_cap with P_hat(n) >= 0.85
   (gate_rule_v05.n_product). If none, n = n_cap and the step-6 statement is due. If n > 60, positions 21 to
   n/3 per stratum are extracted under the same brief, schema, lookups and checks.
5. **What phase 1 may show (MA4).** gate-phase1 mode writes only: the 20 U_m values, P_hat(n) for each grid
   n, n, the step-6 flag, input hashes and seeds. It writes no match list, no per-metric mean, no agreement
   value and no validator acceptance rate. ex_validate's per-entry returns go to the sessions (E5) and to a
   log that no person or agent summarises before step 6.
6. **Decide.** The s10.4 rule is applied once, to all n records, with G5's c(n). PASS, FAIL and re-gate as
   v0.3 s10.5.
7. **Step-6 statement.** When step 4 found no n with P_hat >= 0.85, the verdict states P_hat(n_cap) and the
   criteria with the largest theta_c. A FAIL is a FAIL; the human author decides in the verdict row (after
   the decision) whether the re-gate keeps n_cap or first revises the rules aimed at those criteria.
8. **Re-gate (mi7).** Same procedure with seeds 20261300 + h and 20264902; its draw excludes the Stage A ids,
   the mi4 ids and all 120 ids of the first gate's ordered lists, used or not.

### 10.8 Pinned inputs (MA3)
| File | Role | sha256 (2026-10-20) |
|---|---|---|
| analysis/extraction/gate-config-v05.json | levels, lines, report-only flags, icc_from, n grid, n_cap, target, bound settings, seeds, unit-count model, gate-record cost | fb14fd2906cf8fce136e27199dca70864ea3d2fd7458a483ff8d2426fb7135e8 |
| analysis/extraction/bip-grid-v2.json | per-criterion marginal and joint P(pass \| good) over theta (0.02-0.60) × n; stamped with the model hash 1328a75a... of the config | 64628119cb826689c512d30ab9c7d439e8c9f417275045bf94a99b8893c18635 |
| analysis/extraction/gate_rule_v05.py | bounds, theta assignment, product rule (reference for agreement.py) | 8dea739cf98838cd7f40eb9d24e4839ea06b2374555ba2f09c11ed97f08639c2 |
| research/review/extraction/extractor-brief-v0.5.md | session text | d390f9664ca63d33cba5d939f3bb57c9780839d304c15dd9d06eb453a3c81c9b |
| research/review/extraction/extraction-schema-v0.5.json | record shape | b021c041c26cf5482b22876ba68e8fcec331d0cd9e8e6ba33387bcb0ca0bbc1c |

B1 writes Stage A's unit counts into a copy, `gate-config-v05-stageA.json` (size and units blocks only),
reruns `gate_oc_v05.py --config <copy> --grid-out analysis/extraction/bip-grid-v3.json` and
`gate_bip_v05.py --config <copy> --grid <v3>` for G10, H1, H10 and the one-bad rows, and the B2 row cites
those hashes. The B2 row text lists: config sha256, model sha256, grid sha256, gate_rule_v05.py sha256, brief,
schema and lookup sha256, n_cap, R 1,000, theta grid 0.02-0.60 step 0.02, bisection, seeds 20261200 + h,
20264901, 20261800, bootstrap B 4,000. agreement.py refuses a grid whose model hash differs from the
config's, and a config whose hash differs from the one in its --expect-config argument.

## 11. Tools to build (lab-engineer; nothing here is built)
As v0.4 s11 and s11.1, with these changes:
- **agreement.py** gains `--config` and `--grid` (required in gate-phase1 and gate modes) and
  `--expect-config <sha256>`; imports gate_rule_v05.py by path, or reproduces it and passes its self-tests
  1-2 plus a fixture comparison of phase1_bounds on a stored (x, m) set; computes M-anchorG, M-pool, K-attr,
  M-sign and the report-only lines as s10.3; gate-phase1 output as s10.7 step 5; stage-a mode reports the
  per-metric bounds of s10.2. Self-tests added: a mapped anchor that falls on an unmatched arm scores 0; two
  arms sharing a label key score 0 unless both anchors map to one matched pair; K-attr equals the mean of the
  four field rates on a hand case; M-pool on a two-group record weights groups, not units.
- **ex_validate.py** adds the two sign rejections of s10.3 (arrow in column_printed against
  higher_is_better; one group and metric key with two values) and the EC routing list for sign values that
  rest on the extractor alone or conflict with the lookup; validator-tests.jsonl gets four cases for them.
- **draw_pilot.py** draws the gate lists first, then the 5 mi4 ids (seed 20266200) excluding Stage A and
  gate-list ids.
- Committed scripts written for v0.5 (Appendix A): gate_oc_v05.py, gate_rule_v05.py, gate_bip_v05.py,
  gate_bip_v05_summary.py, brief_contamination_v05.py, make_brief_v05.py, make_schema_v05.py,
  mm_c2_nohit_v05.py, and the config and grid files.

## 13. Protocol and ledger deviations (additions to v0.4 s13)

| # | Deviation or refinement | Protocol / ledger | When |
|---|---|---|---|
| 36 | Attribute rules KA1-KA4; credited_ablation in the group field list | s5 / brief | before Stage A |
| 37 | M-sign report-only; sign secured by KA1, validator rejections and EC routing (s10.3) | gate row | before Stage B |
| 38 | M-pool over matched groups; K-attr as the mean of four fields; M-anchorG through the arm match | gate row | before Stage B |
| 39 | Gate size from per-metric Neyman bounds, product rule P80, n_cap (s10.7) | gate row | before Stage B |
| 40 | Budget check at the n_cap cost; n_cap fixed in the B2 row (MA4) | scope / gate row | before Stage B |
| 41 | Lookup-fallback check on 5 frame-R records (mi4) | lookups M9c | before B2 |
| 42 | 20 more C2 ids in the human construct check (mi6) | scope row | before any draw |

## 14. Preconditions checklist (replaces v0.4 s14)
None is met on 2026-10-20 unless marked.

**Stage A (development, 12 records)**
- [ ] A1 T1 full-text gate PASS signed by gate-auditor.
- [ ] A2 Scope decision row (OQ3-01, OQ3-02, OQ3-06, OQ3-09, OQ4-03).
- [ ] A3 Decision rows of v0.3 s13 marked "before Stage A", rows 34-35 (v0.4) and 36 (KA rules, OQ5-13).
- [ ] A4 gate-auditor check of block F and C-F1a to C-F1e.
- [ ] A5 Human check OQ5-04 (with the 20 mi6 ids); mm-construct.jsonl, strata-overrides.jsonl, duplicate-works.jsonl; strata.py and multimodal_options.py rerun; hashes recorded.
- [ ] A6 Red-team review of v0.5 with no open critical finding.
- [ ] A7 Tools: ex_dispatch.py; ex_validate.py with the v0.5 sign checks and their four cases, the 35 cases of validator-tests.jsonl and T01-T22 as v0.3-shape data, `quote_check.py --self-test`; fixture generator; draw_pilot.py; agreement.py (s11.1 as amended in s11) passing its self-tests; lookup CSV skeletons with the KA1(b) list and direction column.
- [x] A8 v0.4 files and scripts committed (b315c28); the red-team review of v0.4 committed (5d781cc). v0.5 files written 2026-10-20, not committed.
- [ ] A9 ft_isolation_check.py and ft_model_check.py unchanged and passing.
- [ ] A10 Adjudicator route reconfirmed (OQ2-07).
- [ ] A11 we-expected.jsonl (method-architect).
- [ ] A12 brief_contamination_v05.py exit code 0 on the frozen brief and schema (met for the files of s10.8; rerun after any edit).

**Stage B (gate)**
- [ ] B1 Stage A complete; rules, lookups and cost table revised from Stage A means; gate-config-v05-stageA.json written; grid v3 and the B-IP rerun of s10.8; mi4 lookup check done (s10.2).
- [ ] B2 Gate decision row: rule P80 (or the human author's choice from OQ5-07), M-sign status (OQ5-02), levels (OQ5-08), n_cap and budget (MA4), the hashes of s10.8; signed by gate-auditor.
- [ ] B3 agreement.py gate and gate-phase1 modes tested on synthetic pairs, including the phase-1 output restriction of s10.7 step 5.
- [ ] B4 draw_pilot.py gate draw (40 ordered ids per stratum, excluding Stage A ids), then the mi4 draw; manifest.
- [ ] B5 Brief, schema, lookups, config and grid hashed in the gate row.
- [ ] B6 Human gold subset decision (OQ2-10; seed 20266100).

## Appendix A. Scripts and logs (analysis/extraction/, written 2026-10-20, not committed)
v0.3 and v0.4 scripts and logs are unchanged (v0.4 in b315c28). Scripts that use numpy run with
`python -u -E -P`; the others with `python -I`.

| Script | Run | Log or output |
|---|---|---|
| make_brief_v05.py | `python -I analysis/extraction/make_brief_v05.py` | make_brief_v05-log.txt; extractor-brief-v0.5.md |
| make_schema_v05.py | `python -E -P analysis/extraction/make_schema_v05.py` | make_schema_v05-log.txt; extraction-schema-v0.5.json |
| brief_contamination_v05.py | `python -I analysis/extraction/brief_contamination_v05.py` (exit 0) | brief_contamination_v05-log.txt |
| gate_oc_v05.py | `--calibrate --sims 2000 --workers 12`; `--table-a --workers 4`; `--grid-out analysis/extraction/bip-grid-v2.json --sims 2000 --workers 14` | gate_oc_v05-calibrate-log.txt, gate_oc_v05-tableA-log.txt, gate_oc_v05-grid-log.txt, bip-grid-v2.json |
| gate_rule_v05.py | `python -u -E -P analysis/extraction/gate_rule_v05.py --reps 200` | gate_rule_v05-log.txt |
| gate_bip_v05.py | `python -u -E -P analysis/extraction/gate_bip_v05.py --reps 1000 --chunks 4 --workers 18` (2,374 s) | gate_bip_v05-log.txt, gate_bip_v05-results.json |
| gate_bip_v05_summary.py | `python -E -P analysis/extraction/gate_bip_v05_summary.py` | gate_bip_v05_summary-log.txt |
| mm_c2_nohit_v05.py | `python -I analysis/extraction/mm_c2_nohit_v05.py` | mm_c2_nohit_v05-log.txt |

Order: make_brief_v05, make_schema_v05, brief_contamination_v05; gate_oc_v05 (grid before gate_bip_v05);
gate_rule_v05; gate_bip_v05; gate_bip_v05_summary. Results of gate_oc_v05 and gate_bip_v05 do not depend on
--workers (one seed per task).
