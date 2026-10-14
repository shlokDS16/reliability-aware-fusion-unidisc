```yaml
agent: statistician
date: 2026-10-14
brief: Third-round statistical review of EXP-001 v0.3 (the single preregistered experiment, D0013); signing decision, E1-E7 application table, minimal remaining required changes, recomputation of the designer's scratch-script numbers (pass totals, two Spearman critical values).
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-001-crossmodal-unidisc.md (v0.3, lines 1-601, in full)
  - research/preregistration/review-statistician-2026-10-14-round2.md (in full)
  - research/preregistration/review-statistician-2026-10-14.md (round 1; grep only, line 301 for the origin of 0.440)
  - research/preregistration/review-red-team-2026-10-14.md (EXP-001 part, lines 81-262)
  - analysis/stats/round2_stats_check.py (header and helpers); analysis/stats/exp001_stats_check.py (grep, lines 109-128)
  - analysis/stats/round3_exp001_check.py and .log (written for this review)
coverage: >
  The card was read in full. Checked: every v0.2-to-v0.3 change-log row that concerns statistics (C: E1-E7; B: X1-M1, M2, M3,
  M4, M5, M6, M7, M8, m1, m2 for their statistical side; D: the trims and the n_cap rule; F: condition R as a second H-A arm),
  and the seven items of change-log section E. Not covered: setup.md, timing.json, tools/gpu_guard.py, the UniDisc code,
  the novelty audit and the prior-art dossier. Also not covered: estimator validity beyond its effect on inference, which is
  the red-team's remit (raised only as concerns). No GPU used. No card or existing file edited. No ledger rows written.
claims:
  - statement: "The card's core pass total (about 287,000) and every stage row of 12.1 except the pilot line reproduce from the card's own per-trajectory formulas: 287,226 passes, 191,226 non-D3 passes, 10.29 compute-hours and 25.58 wall-clock hours at t_b = 0.129 s, 19.36 h at 0.09 s; NC-6' 196 blind passes per seed; PC-B 159.6 pass-equivalents per prompt."
    status: supported
    evidence: analysis/stats/round3_exp001_check.log sections 1a, 1b
    level: E4 (recomputation)
    confidence: 0.97
  - statement: "The pilot line 'about 31,000 probe and gate passes' cannot be re-derived because the card gives no formula; a reconstruction under stated assumptions gives 27,392."
    status: mixed
    evidence: round3_exp001_check.log section 1c
    level: E4 (recomputation, assumptions stated)
    confidence: 0.7
  - statement: "Single-stratum exact one-sided 5 percent Spearman critical value at n = 8 is 0.643 (P = 0.0481), as the card states. For the mean of two independent strata the exact critical value is 0.452 (P = 0.0479); the card's 0.440 / 0.4405 has P = 0.0528 (a discrete-quantile off-by-one step, inherited from my round-1 script)."
    status: mixed
    evidence: round3_exp001_check.log section 2 (full enumeration of 8! permutations and exact convolution)
    level: E4 (exact computation)
    confidence: 0.99
  - statement: "The n_cap rule has no admissible n when t_b exceeds 0.1317 s (2.1 percent above planning), or at t_b = 0.129 s when G5 falls back to g = 8 or f_ord = 2 (+54,272 passes, +3.9 wall-clock hours); at the card's planning sigma_d (5.66) n_req = 596 exceeds n_cap = 531."
    status: supported
    evidence: round3_exp001_check.log sections 1d, 3
    level: E4 (computation)
    confidence: 0.95
  - statement: "The condition-R arm (64 trajectories, lower 90 percent limit > 1.0) resolves a true ratio of 1.3 with probability 0.91-0.97 per direction at cv 0.5 but 0.44-0.55 at cv 1.0 (0.35 with 30 percent zero values, simulated); the ratio resolvable at power 0.8 is 1.20-1.25 at cv 0.5, 1.44-1.55 at cv 1.0."
    status: supported
    evidence: round3_exp001_check.log sections 4a, 4b, 8
    level: E4 (delta method and simulation; cv and correlation assumed)
    confidence: 0.85
  - statement: "The stratified T->I decomposition is an exact identity (max deviation 2.2e-16), but the stratified (4/4) and unstratified (8) totals differ in expectation at R = 8 (toy, w = 0.5: 0.567 vs 0.552, 6.6 combined SE; both 14-16 percent below exact I), so the G0 addition 'reproduces the unstratified total in expectation' can fail a correct implementation; at R = 256 both are within 0.7 percent of exact I. The content term is undefined when the content class has mass below 0.01 (no draws)."
    status: supported
    evidence: round3_exp001_check.log sections 6, 6b
    level: E4 (toy simulation)
    confidence: 0.9
  - statement: "PG-V's stated OC (about 0.9 / 0.5 / 0.05) is about right at the stated point when criteria (a) and (b) are slack (simulated 0.98 / 0.50-0.51 / 0.00-0.02), but P(pass) falls to 0.79-0.80 when the non-empty share is 0.65 or m is 0.55, because (a) and (b) then bind."
    status: supported
    evidence: round3_exp001_check.log section 5
    level: E4 (simulation, noun-genericity model assumed)
    confidence: 0.75
competing_explanations:
  - "All operating characteristics depend on assumed variance components (cv and early/late correlation of the per-trajectory H-A statistics, share of zero values, noun-genericity of PG-V captions). The directions of the findings do not depend on them; the magnitudes do. D0 and D1 replace them."
unknowns:
  - per-trajectory cv of the content-term T->I statistic and the pad-excluded I->T statistic, under confidence ranking (D1) and under random positions (no data before the condition-R trace)
  - distribution of w (pad/EOS mass of the committed text token) by probe; if it is near 1 at early probes, the T->I content term is near 0 there
  - measured t_b and wall-to-compute ratio under gpu_guard (decides whether n_cap exists)
next_test: {hypothesis: "the assumed cv values hold (H-A1 power 0.8 or more at n = 256; condition R resolves 1.3)", intervention: "D0 pilot and D1 profile as registered; the E4 projection extended to condition R (T5)", primary_metric: "cv of the early and late per-trajectory averages of the decision statistic, per direction; mean w per probe", falsifier: "D1 cv above 1.0 for I->T (condition R then resolves only ratios of about 1.45 or more)", gpu_hours: "none beyond the card"}
```

# Statistician review, round 3: EXP-001 v0.3 (pre-outcome)

Tags: [S] source fact with location; [I] inference; [C] computed here (script and log named); [A] assumption.
No experiment has run. Every number below is a formula result, an exact enumeration, or an operating characteristic (OC)
of a decision rule under stated assumptions. None is an experimental result.

Command (CPU, Python 3.14.3, numpy 2.4.2, scipy 1.17.1, about 21 s):

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python analysis/stats/round3_exp001_check.py > analysis/stats/round3_exp001_check.log

SHA-256 at the time of writing: script `7a6d1b7b…5273255bb`, log `cfcbfb9e…4aaae04` (full hashes: `sha256sum analysis/stats/round3_exp001_check.*`).

## Verdict

**Sign with the listed changes: 7 new required changes (T1-T7).** All are edits to text or to the analysis plan. None needs
new runs or a redesign, and none adds GPU time. Every round-2 item (E1-E7) is applied or resolved by scope. I sign v0.3
when the v0.3-to-v0.4 change log shows T1-T7 applied (where I offer options, either one). Recommendations r1-r8 are
optional.

## E-table (round 2 items)

| E | Applied | Check |
|---|---|---|
| E1 NC-6' | yes | 8.8: seven exact-null statements, 99.29 percent intervals (0.05/7), reported-not-gating bound, scored before D3, failure blocks D3 scoring. TFJ replaces TF: the null stays exact because the blind wrapper masks the prefix on the image side (6, 8.7 G2), so image and caption are independent given the seed. P(pass) >= 0.95 follows from Bonferroni whatever the arm correlations, given nominal coverage. [C] Blind-pass accounting 196 per seed (J 64, Alt 32, DA 48, TFJ 52) reproduces exactly (log 1a) |
| E2 G5 | yes | 8.7 verbatim. The g = 8 fallback cost is not in the n_cap formula (T6a) |
| E3 R_Q pooled sums | yes | 2 H-A1-Q, 8.5; uses the content term for T->I, which is consistent with H-A1 |
| E4 power from D1 | yes | 10.3, with I->T probes on 64 D1 trajectories (8.3). e3 declined, with an orchestrator option to extend D2 to 512 trajectories; sizing from independent data before D2, so acceptable. See r3 for how to project the ratio-of-sums statistic |
| E5 P_rand fork | yes | (a) 6 regenerates J and Alt on D0 under P_rand and sizes under it; (b) 6 makes condition R = condition P; (c) scope sentence in 2, gate outcomes logged together. Second trigger (PG-1 condition-P leg) has the same target. Concern 3 below |
| E6 H-B2 | yes, by scope | H-B2 is now an exploratory, conditional, unadjusted IUT statement in no family. My E6 wording was needed only while H-B2 sat in Holm. Accepted |
| E7 labels, tier | yes | (a) 5.1 and 10.2 list Jd, J-global, TFJ - J, TF, IF as exploratory; (b) the 1,024-px tier is withdrawn, so the item is moot |
| e1, e2, e4 | yes | G4 prints agreement only; PG-1 guided leg paired; post-caption share now a rule (X1-M2) |
| e3 | declined | Accepted (budget). The orchestrator option in 10.3 is sound |

## The items the designer flagged

### (1) Per-position, pad-excluded H-A1 statistic (2, 8.5)

- [I] The definition is sound. S-bar is the ratio of pooled sums (sum of I_hat^c over trajectories and probes, divided by the
  sum of |J_d|). Empty probes therefore carry no 0/0. A percentile bootstrap over trajectories, with early and late probes
  resampled together, is the right cluster bootstrap. For T->I, |J_I| is fixed per probe (992, 864, 224, 96 at passes 2, 6, 26, 30
  [C, log 7]), so the pooled mean equals the equally weighted mean of per-trajectory per-position means. For I->T, |J_T| varies
  with the pad-class exclusion, so trajectories with more non-pad masked positions get more weight. That is a valid estimand
  (the mean over positions), and Paper 1 should say so in one clause.
- [C] The I->T late probes pool at most 7 and 3 masked text positions per trajectory (passes 26, 30): at most 2,560 positions in
  D2 and 640 in condition R. The I->T late denominator is therefore the noisy part. The E4 projection decides how noisy.
- The T->I content term has a definitional gap (T1), and the meaning of a reported quantity needs a fix (T1).
- The pad-class rule for I->T uses mbar_j. mbar_j is computed from the same requery draws as the statistic, so it is not
  strictly a state-time quantity. Inference stays valid, because the bootstrap resamples the whole per-trajectory procedure.
  The selection of near-threshold positions is noisy, though, and those positions are the ones where the image decides
  termination. Using p1_j (the baseline pass, a function of the state) is cleaner (r1).
- [I] The I->T statistic has no counterpart of the T->I length/termination split. A receiving content-class position whose
  pad mass is between 0.01 and 0.5 still carries "does the caption end here" information. A chain-rule split of each KL into
  the class-indicator part and the within-class part is computable from the stored arrays at no GPU cost (r2; validity is
  the red-team's call).

### (2) Stratified T->I estimator (8.2)

- [C] between + within-pad + within-content equals the direct stratified total to 2.2e-16 (log 6). The mixture
  w mbar_P + (1-w) mbar_C is the correct stratified estimate of mbar. Equal 4/4 allocation keeps it unbiased for mbar
  whatever w is.
- [C] Finite-R behaviour on a toy (log 6, 6b). At R = 8 all terms are plug-in biased. Within-content is biased low (0.239 against
  0.358 at w = 0.5). Between is biased high (0.223 against 0.175), because mbar_P and mbar_C from 4 draws each scatter around
  the mixture. Some content dependence is therefore reported as between-class at R = 8. This is conservative for the H-A1
  T->I content term. G4 (R = 8 against 32) is the right check.
- [C] The G0 addition "reproduces the unstratified total in expectation" is not true at finite R. At w = 0.5 the two totals
  differ by 6.6 combined standard errors at R = 8 (0.567 against 0.552), and both are 14-16 percent below the exact I. At R = 256
  both are within 0.7 percent of it. As written, the gate can fail a correct implementation (T2).
- The rule "if one class has mass below 0.01 all 8 come from the other class" leaves within-content with no draws exactly
  when w > 0.99. Under confidence ranking that may be most early probes (the committed text token is a confident pad/EOS
  slot). The H-A1 T->I statistic is then undefined there (T1). Also, "the share of draws in the pad class per probe" (8.5) is
  4/8 by design and says nothing. The informative quantity is the mean w per probe (T1).

### (3) Holm family of four and the reading conditions (10.2, 7.4)

- [I] Fixed sequence (H-B1 at 0.05) followed by Holm at 0.05 over {Alt - J k0, DA - J k+, DA - DA-low, DA - TFJ} controls the
  FWER at 0.05. If H-B1 is a true null, nothing can be rejected without rejecting it. If H-B1 is false, the FWER is that of
  Holm over the four. "Not run enters with p = 1" is correct. The OC table of 10.2 reproduces (n = 500, sigma_L 4).
- [I] R-a, R-b and R-c combined with H-B1 form an intersection-union test. The conjunctive claim "improves text-image
  consistency" has level at most 0.05 (H-B1 and R-a/R-b one-sided 0.025, R-c one-sided 0.05), so no alpha is spent. Correct.
- What fails is the wording on failure. 7.4 and 13 turn a failed condition into a positive mechanism claim:
  "baseline-driven" / "through the shuffled baseline (diversity)", "changes how well the image follows the observed
  prefix", "changes CLIP lift only", and "showing the window's text earlier explains the gain" when DA - TFJ is not positive.
  Each of these is absence of evidence read as evidence. 10.2 itself states the right principle ("not confirmed", not
  "absent"). This is the same defect as EXP-002 M4 in round 2 (T4).

### (4) PG-V thresholds and OC (4.4)

- The thresholds are feasibility choices. No contrast enters, and PG-V uses a disjoint pool and J only, so it cannot bias
  any test. Accepted.
- [C] Simulated OC with n = 48, 4 derangements, and per-caption noun genericity Beta(mean s/q, concentration 4) [A] (log 5):

| non-empty share q | m | m - s | P(pass) | binding criterion |
|---|---|---|---|---|
| 0.75-1.0 | 0.65-0.75 | 0.40 | 0.97-0.99 | none |
| 0.65 | 0.65 | 0.40 | 0.79 | (a) share >= 0.60 |
| 0.75-1.0 (0.65) | 0.55 | 0.40 | 0.80 (0.73) | (b) m >= 0.50 |
| any | 0.55-0.75 | 0.30 | 0.66-0.87 | (c) |
| any | any | 0.25 | 0.45-0.51 | (c) |
| any | any | 0.10 | 0.00-0.02 | (c) |

  The card's "about 0.9 / 0.5 / 0.05" is right at its stated point, if slightly pessimistic. The SD of m - s is 0.03-0.08,
  not 0.09, because matched and shuffled presence share the caption's nouns. The card's sentence hides that (a) and (b)
  bind near their thresholds (r4). Terminal false stop over the two-rung ladder: 0.003, 0.04 or 0.16 if each adequate rung
  passes with 0.95, 0.8 or 0.6.
- [C] PC-F: P(pass) >= 0.99 at m_real 0.85 and s_real <= 0.30, but 0.79 at s_real 0.40 and 0.71 at (0.75, 0.30). Generic
  COCO nouns ("man", "table") may push s_real toward 0.4 (r4).

### (5) NC-6' with TFJ and blind-pass accounting (8.8): see the E1 row. Correct.

### (6) n_cap rule (10.4, 12.1)

- [C] The arithmetic is correct. wall(n) = 2[(191,000 + 192 n) t_b / 3600 + 2.5] <= 26 gives n_cap = 531 at t_b = 0.129 s and
  1,000 at 0.09 s (log 1d). n_cap depends only on cost measurements, so it cannot bias any test.
- Three gaps (T6):
  (a) X = 191,000 is the plan before the pilot's decisions. [C] A G5 fallback to g = 8, or f_ord = 2, adds 54,272 passes
  (+1.94 compute-hours, +3.9 wall-clock hours at 0.129 s). With either, no n in [500, 1000] meets 26 h.
  (b) [C] At t_b > 0.1317 s (2.1 percent above planning) the admissible set is empty and the rule is undefined. Under
  throttling at a 50 percent duty cycle this is likely, not remote (14 item 13 says the same in words).
  (c) [C] Change log D says "at t_b = 0.129 s the cap is about 530, so the n_req rule rarely exceeds the 500 floor". This is
  wrong. n_req > 500 whenever the pilot sigma_d > 5.19 (chi2 factor 1.0861). At the card's own planning value sigma_d = 5.66,
  n_req = 596, so n_conf = n_cap = 531 and the achieved MDE is 0.87 point (log 3).
- (d) [C] 10.4 still quotes the seven-member family: "505 at 0.05/7", "power 0.897" and "Holm-level n about 680". With four
  members the smallest Holm level is 0.0125. Then n(0.90, sigma_L 4) = 457, and power at n = 500 is 0.927, 0.747, 0.555 for
  sigma_L 4, 5, 6 (at n = 530: 0.942, 0.776, 0.585). The influence-SD Holm-level n is about 620 (T6d).

### (7) G1b per-probe rule (8.7)

- The pilot rule is sound: per probe, per direction, probe-level means, the floor measured on the same positions, and
  decided before D2. Dropping a probe as "floor unmeasured" is a pre-D2 decision, so it is acceptable. If both early probes
  or both late probes of a direction are dropped, that direction has no ratio. The card should say so (T3).
- The D2 re-measurement (first 32 D2 trajectories) has no stated consequence. Any post hoc use of it on the confirmatory
  sample, such as dropping a probe or voiding a direction after seeing H-A1, is a forking path. The rule must be fixed now
  (T3).

### (8) Condition R as a registered second arm of H-A (2, 6, 14 item 12)

- [C] "Resolves a ratio of about 1.3 or more at cv about 0.5" holds. Per direction, P(lower 90 percent > 1.0 | 1.3) is 0.91-0.97
  (r 0-0.3), and 0.94 for both directions together. It does not hold at cv 1.0: 0.44-0.55 per direction, 0.30 for both, and 0.35
  with 30 percent zero values (simulated percentile bootstrap, level 0.047-0.061). The ratio resolvable at power 0.8 is 1.20-1.25
  at cv 0.5, 1.32-1.39 at 0.75, 1.44-1.55 at 1.0 and 1.74-1.93 at 1.5 (log 4a, 4b, 8). The I->T arm is the weak one. Under random
  positions, the 7 and 3 masked text positions at passes 26 and 30 are a random subset, mostly post-caption, so few survive
  the pad-class exclusion.
- [C] The "sampler-specific" reading (random ratio upper 90 percent < 1.25) fires with probability 0.92 at a true random ratio
  of 1.0 when cv is 0.5, and 0.45 when cv is 1.0.
- The readings in 2 are not exhaustive, and they conflict with the position-free rule two sentences earlier.
  (i) Position-free wording needs "same side of 1.0 and lower 90 percent > 1.0". The two-way reading needs "both ratios >= 1.5
  (random lower 90 percent > 1.0)", and it does not say whether ">= 1.5" is a point estimate or a limit.
  (ii) A random-position ratio with point estimate 1.3 and lower limit 1.1 matches no reading.
  (iii) "Random-position ratio above the confidence ratio" is decided by point estimates.
  (iv) Stop rule 7's "condition R reproduces the null for H-A" is undefined.
  These are fixed by one table (T5).

## Recomputed numbers from the designer's scratch script

| Number (card location) | Card | Recomputed [C] | Agreement |
|---|---|---|---|
| Core passes (D, 12.1) | about 287,000 | 287,226 (stage 2 taken at the card's 40,000) | yes (0.08 percent) |
| D1 (12.1) | 29,696 | 12,288 + 8,192 + 9,216 = 29,696 | exact |
| D2 (12.1) | 55,552 | 49,152 + 5,120 + 1,280 = 55,552 | exact |
| Condition-R trace | 13,568 | 13,568 | exact |
| NC-6' | 25,088 (196 per seed) | 25,088; J 64, Alt 32, DA 48, TFJ 52 from the plan generator | exact |
| D3 | 108,000 | 96,000 + 12,000 | exact |
| PC-B | about 15,000 (159.6 per prompt) | 15,321.6; 159.6 = 3 x (21 + 3 x 2.2) + 24 x 2.2 + 24 | yes |
| Pilot probe and gate passes | about 31,000 | 27,392 under my assumptions (log 1c); no formula in the card | not verifiable (r7) |
| Non-D3 passes in wall(n) | 191,000 | 191,226 | yes |
| Compute / wall at 0.129 s | 12.8 / 25.6 h | 12.79 / 25.58 h | yes |
| Compute / wall at 0.09 s | 9.7 / 19.3 h | 9.68 / 19.36 h | yes |
| n_cap at 0.129 / 0.09 s | about 530 / 1,000 | 531 / 1,000 (clipped from 1,193) | yes |
| Single-stratum Spearman critical value, n = 8 | 0.643, P = 0.048 | 0.6429, P = 0.04809 (exact over 40,320 permutations) | **yes** |
| rho_strat critical value (mean of two strata) | 0.440 (simulated 0.4405) | **0.4524, P = 0.04792** (exact convolution); P(>= 0.4405) = 0.05284 | **no** (T7) |

Not counted anywhere: PG-V + D-ref, 96 x 32 = 3,072 passes = 0.11 h at 0.129 s. Stage 1's "about 0.8 h" is 0.7 (guided) +
0.1 (P leg), so these passes are missing. The amount is negligible.

The 0.440 is my own round-1 error (`exp001_stats_check.py` line 126 used `np.quantile(..., 0.95)`). On a discrete null that
returns the 95th percentile, 0.4405, whose upper tail is 0.0528. The level-0.05 critical value is the next support point,
0.4524. The H-C decision is unaffected: support needs rho_strat >= 0.5 and permutation p <= 0.05, and P(rho_strat >= 0.5 | null)
= 0.0314 (exact). So the 0.5 bound binds, and the effective level of H-C with two strata is 0.031. With one stratum, 0.643 binds
(P(rho >= 0.5) = 0.108).

## New required changes (minimal)

**T1. T->I content term when a class is nearly empty (8.2 step 2, 8.5).** Replace "if one class has mass below 0.01 all 8 come
from the other class and that class's weight is carried as its true tiny value" with: "4 draws from each class whenever both
classes have float64 mass >= 1e-6. If a class has mass < 1e-6, its within-class and between-class contributions are set to 0
(bounded by mass x ln 16,384 < 1e-5 nats per position, the bf16-floor scale), and the share of such probes is reported per
probe pass." In 8.5, replace "the share of draws in the pad class per probe" (4/8 by design) with "the mean and the
distribution of w per probe". Cost: none (8 draws either way).

**T2. G0 criterion for the stratified estimator (8.7 G0, "Added").** Replace "reproduces the unstratified total in expectation"
with: "on a toy with known I, the stratified total (128 draws per class) and the unstratified total (R = 256) each lie within
1 percent of the exact I, and at R = 8 both lie below it." Reason [C]: at R = 8 the two estimators have different plug-in
biases (6.6 combined SE apart on a toy), so the current wording can fail a correct implementation.

**T3. G1b on D2 and dropped probes (8.7 G1).** Add: "The D2 re-measurement never drops, adds or replaces a probe. If an H-A1
probe fails the 20x rule on D2 in direction d, H-A1 in direction d is not reported as positive; it is labelled 'floor-limited
at pass p'. A pilot-dropped probe ('floor unmeasured') is dropped before D2; if both early or both late probes of a direction
are dropped, that direction is 'not measurable', and H-A1 is decided by the IUT over the remaining parts with that limit
stated." (A floor that rises with entropy can make a floor-limited trace look front-loaded, X1-M4, so the D2 consequence
must only be able to remove a positive.)

**T4. Labels after a failed reading condition (2, 7.4, 13).** A failed condition gives "not shown". A positive alternative
label needs its own interval:
- R-a fails: "matched-driven not shown". "Baseline-driven" or 13's "through the shuffled baseline (diversity), not through
  higher matched similarity" is used only if the 95 percent interval of the baseline-term contrast -100 dB excludes 0 and
  that of 100 dC contains 0.
- R-b fails: "completion-driven not shown". "Changes how well the image follows the observed prefix" is used only if the
  prefix-only lift contrast has a 95 percent lower limit > 0.
- R-c fails: "not confirmed by the VLM score (achieved MDE x)". Drop 7.4's "changes CLIP lift only". 13's wording is already
  right.
- DA - TFJ not positive: "showing the window's text earlier explains the gain" only if TFJ - J has a 95 percent lower limit
  > 0 (exploratory, flagged); otherwise "mechanism not resolved".
These remain wording rules and spend no alpha.

**T5. One decision table for condition R (2 wording rule, 11.7, 14 item 12).** Replace the two-way reading with:
"Per direction d, with L_R and U_R the 90 percent percentile-bootstrap limits of the H-A1 statistic on the 64 random-position
trajectories, and applied only where H-A1 is positive under confidence ranking: (i) L_R > 1.0: 'front-loaded under both position
rules tested' (the >= 1.5 magnitude is claimed for confidence ranking only, unless L_R >= 1.5); (ii) L_R <= 1.0 and U_R < 1.25:
'front-loading in direction d follows the confidence rule'; (iii) otherwise 'not distinguishable at 64 trajectories'.
Position-free wording for H-A needs (i) in both directions. Always reported: the ratio of ratios (confidence over random) with
an unpaired bootstrap 90 percent interval, and S-bar(confidence)/S-bar(random) at each probe. Stop rule 7's 'condition R
reproduces the null' means the condition-R 97.5 percent upper limit is below 1.5 in each direction where H-A was weakly
falsified." In 14 item 12 and change-log F, replace "about 1.3 at cv about 0.5" with: "the ratio resolvable at power 0.8
is 1.20-1.25 at cv 0.5, about 1.45-1.55 at cv 1.0 [C, round 3]. The E4 step logs this value for the D1 cv of each direction.
D1 runs under confidence ranking, so this is an approximation."

**T6. n_cap rule and sizing text (10.4, 12.1, change log D).**
(a) In wall(n), X is the realised non-D3 pass count after the pilot's decisions (G5 granularity and f_ord, the G1b probe dtype
with t_f, the P_rand regeneration), not the fixed 191,000.
(b) "If wall(500) > 26 h, n_conf = 500, and the projected overrun goes to the orchestrator before D1 starts, not as a mid-run
budget stop."
(c) Replace change-log D's "the n_req rule rarely exceeds the 500 floor" with: "n_req exceeds 500 whenever the pilot sigma_d
exceeds 5.19. At the planning value 5.66, n_req = 596 and n_conf = n_cap (about 531), with achieved MDE 0.87 point."
(d) Update the four-member figures in 10.4: "n = 337 at alpha = 0.05 and 457 at 0.0125 (the smallest Holm level with four
members); at n = 500 power 0.977 and 0.927 (sigma_L 4), 0.885 and 0.747 (5), 0.750 and 0.555 (6); Holm-level n under the
influence SD about 620."

**T7. Spearman critical value (10.3).** Replace "One-sided 5 percent critical value of rho_strat = 0.440 [...] 0.4405" with
"0.452 (exact: P(rho_strat >= 0.452) = 0.048 under independent within-k permutation; 0.440 has P = 0.053) [C, round 3]. The
support rule rho_strat >= 0.5 binds (P = 0.031 under the null)."

## Recommendations (optional)

- r1. Define the I->T pad-class exclusion by p1_j (baseline pass, state-determined) and report the mbar-based version as a
  sensitivity analysis.
- r2. Report, beside H-A1 I->T, the chain-rule split of each receiving KL into the pad/content indicator part and the
  within-class part (stored arrays, no GPU).
- r3. Project E4 power on the decision statistic itself: the delta method for a ratio of ratios of sums, with the
  per-trajectory numerator-denominator covariance (|J_T| varies for I->T), or resampling of D1 trajectories to n = 256.
- r4. Replace PG-V's OC sentence with the table above (state that (a) and (b) bind near their thresholds), and add PC-F's OC
  (0.79 at m_real 0.85, s_real 0.40).
- r5. H-C p-value by exact convolution of the two n = 8 null distributions (no Monte Carlo error; script section 2 shows how).
- r6. Rename the core 12.1 row "4b condition-R trace". "Stage 4b" means the conditional TF/IF stage in 11 and in the change log.
- r7. Give the formula for the pilot's "about 31,000" probe and gate passes.
- r8. NC-6' intervals at 99.29 percent leave about 36 bootstrap replicates per tail at B = 10,000. Use B = 50,000 (CPU only).

## Concerns outside the brief (validity; for the red-team and orchestrator)

1. Under confidence ranking the early committed text token is plausibly a confident pad/EOS slot (w near 1). The H-A1 T->I
   content term is then near 0 early and the T->I ratio describes which token the rule commits. D1's mean w per probe (T1)
   will show this before D2.
2. Condition R's I->T ratio rests on a few non-pad positions at passes 26 and 30. Sampler-free wording for I->T will
   probably be "not distinguishable" (T5 makes that an honest label).
3. If P_rand becomes primary because PG-1's condition-P leg found degenerate 512-px images, condition R = condition P, so
   the second H-A arm runs on the condition known to degenerate. The reading should carry that label.
4. Budget: t_b only 2.1 percent above planning, or any G5/f_ord fallback, pushes the core past 26 h (T6). Paper-relevant power
   then rests on n = 500.

## What is NOT checked here
Estimator validity on the real network, prefix-task construct validity, the plan generator's code, gpu_guard and setup
facts are the red-team's and lab-engineer's. Every [A] value above is a placeholder that D0 or D1 replaces. This review
signs an analysis plan, not results.
