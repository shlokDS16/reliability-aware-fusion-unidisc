```yaml
agent: statistician
date: 2026-10-14
brief: Second-round statistical review of EXP-001 v0.2 and EXP-002 v0.2; per card a signing decision, an R-item application table, the minimal remaining required changes, and a note on EXP-002's reduced k-scope.
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/review-statistician-2026-10-14.md (round 1, in full)
  - research/preregistration/EXP-001-crossmodal-unidisc.md (v0.2, lines 1-515, in full)
  - research/preregistration/EXP-002-value-rule-decomposition.md (v0.2, lines 1-1091, in full)
  - analysis/stats/exp001_stats_check.py, analysis/stats/exp002_stats_check.py (round 1, section headers and helpers)
  - runs/env-2026-10-14/setup.md (grep only, lines 84 and 165)
  - analysis/stats/round2_stats_check.py and .log (written for this review)
coverage: >
  Both cards read in full, with the change logs checked item by item against round-1 R1-R12 of each card and
  against every item the designers flagged (EXP-001 change-log D (1)-(5) and the O1 decline; EXP-002 change-log
  items 7, 8, 13, 18, 27, 28, 30, 31 and the O4 decline). Not covered: timing.json (not needed; the card numbers
  were re-derived from the card's own inputs); the UniDisc and MDLM code; estimator validity beyond its effect on
  inference (red-team remit); novelty. No GPU used, no card or existing file edited, no ledger rows written.
claims:
  - statement: "EXP-001 NC-6' as written ('every CI contains 0 and |d| < 0.3' for 4 arm Lifts and 3 contrasts at n = 128) passes a correct pipeline with probability 0.12-0.63 under its exact null (sigma_L 2.5-4, arm correlation 0-0.6); a Bonferroni rule over the 7 statements without the point bound passes with 0.96."
    status: supported
    evidence: analysis/stats/round2_stats_check.log, section "EXP-001 NC-6'"
    level: E4 (simulation, sigma_L and correlations assumed)
    confidence: 0.9
  - statement: "EXP-001 G5 as written ('median relative difference > 0.3', 16 probe-trajectory values) fails an unbiased chunked draw with probability 0.17, 0.62, 0.92 when the per-estimate Monte Carlo relative SD is 0.25, 0.35, 0.5; a ratio of pooled means fails with 0.002, 0.022, 0.110."
    status: supported
    evidence: round2_stats_check.log, section "EXP-001 G5"
    level: E4 (simulation, Monte Carlo SD assumed)
    confidence: 0.85
  - statement: "EXP-001 H-A1 power at n = 256 (true ratio 1.75) is 0.935 only at cv 0.6; it is 0.55 at cv 1.0 and 0.28 at cv 1.5 (delta method, r = 0.3); with 30 percent zero values and cv 1.0 the simulated percentile bootstrap gives 0.25, at level 0.03."
    status: supported
    evidence: round2_stats_check.log, sections "EXP-001 H-A1"
    level: E4 (computation and simulation, cv assumed)
    confidence: 0.85
  - statement: "EXP-002 9.5 states P(H1 negative | G_cp = 0) = 0.80 at two k; at R2's sized SE (0.0090) it is 0.69 (95 percent rule) and 0.53 (97.5 percent); at R0 (M = 5) 0.68 and 0.50; at R1 0.72 and 0.55; at R3 P('practically 0 at k = 16') = 0.74."
    status: supported
    evidence: round2_stats_check.log, section "EXP-002 P(H1 negative ...)" (independent k; positive correlation between k raises these by at most 0.06 at rho 0.6)
    level: E4 (computation)
    confidence: 0.95
  - statement: "EXP-002 IR8 (iv) pooled WLS curvature screen has false-flag probability <= 0.006 and power >= 0.92 at a curvature difference of 6 per nat^2 for E spacing 0.10-0.20 nats per grid step and sigma_y 0.3-0.5; SE(kappa) is 0.4-1.1, below the card's own 1-2."
    status: supported
    evidence: round2_stats_check.log, section "EXP-002 IR8 (iv)"
    level: E4 (computation, cell placement and sigma_y assumed)
    confidence: 0.8
  - statement: "EXP-002 N2-Y at m = 3.29 SE has P(pass | exact null) = 0.90 at sigma_true = sigma_up, 0.73 at 1.2 sigma_up; it voids every G_cp conclusion on failure, so P(G_cp counted | G_cp = 0.03 at one k) <= 0.72, not 0.80."
    status: supported
    evidence: round2_stats_check.log, section "EXP-002 N2"
    level: E4 (computation)
    confidence: 0.9
  - statement: "EXP-002 12.5 affordable n_B and sigma maxima reproduce from the card's inputs (bf16 R2 2510 vs card 2509; R3 6502 vs 6504; fp32 rows exact); constants for M = 1-5 are correct."
    status: supported
    evidence: round2_stats_check.log, sections "EXP-002 constants" and "12.5 arithmetic"
    level: E4 (computation)
    confidence: 0.99
competing_explanations:
  - "All operating characteristics above depend on assumed variance components (sigma_L under the blind model, Monte Carlo SD of I_hat at R = 8, cv of the probe statistics, sigma_y, sigma_H, cross-tau correlation, E spacing per tau step). The directions do not depend on them; the magnitudes do. The pilots and D1 replace them."
unknowns:
  - per-trajectory cv and zero share of the committed-set I->T statistic at k0 (one text position per probe)
  - Monte Carlo SD of I_hat at R = 8 per probe (obtainable from the stored R = 4 halves)
  - sigma_L and arm correlation under the modality-blind model (NC-6')
  - EXP-002 sigma_H, the cross-tau correlation of H(A1) - H(A3) within s, and the k = 1 to k = 4/16 SD ratio
next_test: {hypothesis: "the assumed variance components above fall in the stated ranges", intervention: "EXP-001 D0 pilot and D1 profile; EXP-002 S2 pilot", primary_metric: "cv of window-pair S per direction (D1); MC SD from R = 4 halves; sigma_c,up (EXP-002)", falsifier: "D1 cv of committed-set I->T above 1.0, which leaves H-A1 below 0.55 power at n = 256", gpu_hours: "as in the cards (no new runs)"}
```

# Statistician review, round 2: EXP-001 v0.2 and EXP-002 v0.2 (pre-outcome)

Tags: [S] source fact with location; [I] inference; [C] computed here (script and log named); [A] assumption.
No experiment has run. Every number below is a formula result or an operating characteristic (OC) of a decision rule
under stated assumptions. None is an experimental result.

Command (CPU, Python 3.14.3, numpy 2.4.2, scipy 1.17.1, about 5 s):

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python analysis/stats/round2_stats_check.py > analysis/stats/round2_stats_check.log

The single-thread flag is needed: the first two attempts failed with `ArrayMemoryError` and `OpenBLAS error: Memory
allocation still failed` while free commit was about 0.5 GB (`FreeVirtualMemory 493564` KB). This is the
system-commit exhaustion described in setup.md section 0. It affects GPU runs too.

## Verdicts

| Card | Verdict | New required changes | Blocking items |
|---|---|---|---|
| EXP-001 v0.2 | **Sign with the listed changes** | 7 (E1-E7) | NC-6' pass rule fails a correct pipeline most of the time (E1); G5 fails an unbiased draw from Monte Carlo noise alone (E2); the R_Q companion is undefined for one-token committed sets (E3); the P_rand fork leaves sizing and condition R inconsistent (E5) |
| EXP-002 v0.2 | **Sign with the listed changes** | 6 (M1-M6) | wrong P(H1 negative) figures (M1); N5(b) is a flag in one section and a voiding condition in another (M3); a failed H4 TOST is read as a finding (M4); n_B is not pinned (M5); claim 1.1 promises growth in k that R2/R3 cannot test (M6) |

All R-items of round 1 were applied as intended, or modified acceptably (tables below). The remaining changes are
edits to the analysis plan; none needs new runs or a redesign. I sign each card when its v0.2 to v0.3 change log shows
every listed item applied (one option where I offer two). Recommendations are optional.

---

# EXP-001 v0.2

## R-item table

| R | Applied | Comment |
|---|---|---|
| R1 pilot firewall | yes | 10.5 as required, plus Lift(Ref-real) for PC-A (fine). Note: G4 on the pilot computes the H-A1 early/late ratio on 16 trajectories. No allowed pilot change touches H-A, so this is harmless; printing only the R = 8 vs R = 32 agreement would be cleaner (recommendation e1) |
| R2 sizing rule | partly | Rule applied verbatim. Two gaps created by v0.2: under the P_rand fork the sizing SE comes from condition P while the primary runs under P_rand (E5a); the 1,024-px tier fixes n_conf = 250 outside the rule (E7b) |
| R3 gatekeeping | yes | Option "fixed sequence" chosen and written correctly; tests not run enter with p = 1; DA - J at k- moved to H-B3 |
| R4 classes and OC | yes | Second option (positive = significant; "at or above the MEI" label); OC table and wording correct |
| R5 p-values and MC precision | yes | |
| R6 IUT for maxima | yes | H-B2 as IUT; p = larger one-sided p for H0: d >= 1.0 is the correct IUT p-value. Section 2 still states H-B2 by unadjusted 95 percent limits while 10.2 puts it in Holm (E6) |
| R7 H-A rules | partly | (a), (b), (c), (e) applied; probes adapted correctly to the new geometry (passes 2, 6 vs 26, 30; pass 1 separate). (d) applied as I wrote it, but with one committed text token per probe at k0 my per-trajectory form sum I / sum H becomes 0/0 whenever that token has H(mbar) < 0.05 (E3). The power figure 0.935 (0.82 for the conjunction) rests on cv 0.6, which is implausible for a one-position statistic (E4) |
| R8 H-C stratified | yes | Including the 0.15 bound condition |
| R9 freeze before scoring | yes | |
| R10 PC-A units | yes | |
| R11 error control | yes | |
| R12 gate | yes | Statistic pinned, estimand named, logged before D1, OC stated. The new fork target has consequences (E5) |

O1 decline: **accepted.** The fork now leads to a valid alternative condition, not to "untestable", so a false fail
(about 0.20 at a true Lift(J) of 2.5 [A]) costs scope (a random-position primary is less relevant to practitioners),
not the experiment. The point-estimate gate is simpler and no contrast enters it.

## The flagged items

**(1) Chunked I->T draw (g = 4), probe schedule, D1/D2 split.**
- [I] The chunked draw estimates the mutual information under an approximate law of b. Within a chunk, tokens are drawn
  from the product of marginals. The bias direction is unknown, as the card says. For H-A1 only a bias that differs
  between early and late probes matters, because a proportional bias cancels in the ratio. G5 is the right check, but as
  written it fails without any bias. [C] With 16 probe-trajectory values and per-estimate Monte Carlo relative SD
  c = 0.25, 0.35, 0.5 (plausible for a plug-in MI at R = 8 on one text position [A]), P(median |relative difference| > 0.3
  | no bias) = 0.17, 0.62, 0.92. A ratio of pooled means gives 0.002, 0.022, 0.110 (log "EXP-001 G5"). G5 also does not
  say which probes it uses, so it may never look at the early/late contrast it must protect. If I->T is declared
  "chunk-dependent", the card drops it from H-A1 but says nothing about H-A2, which is an I->T quantity. Fix: E2.
- D1/D2 split: sound. D1 (profile, DA windows, H-C predictor) and D2 (H-A confirmation) are disjoint. D2 is fixed and no
  pilot-based change can touch H-A, so seeing the D1 traces is not an interim look that can change D2's analysis. The
  card should not pool D1 into H-A after the fact. "Decided once at n = 256" (11.2) already says so.
- H-A1 power under the new geometry: at k0 the committed text set is one token per probe. S^{I->T} is therefore the MI
  of a single, confidence-selected position. This value is often near zero (pad or EOS chosen early) and otherwise
  heavy-tailed. [C] P(lower 95 percent limit >= 1.5 | true ratio 1.75) at n = 256 is 0.935 at cv 0.6, 0.74 at 0.8, 0.55
  at 1.0 and 0.28 at 1.5. In simulation (gamma values with 30 percent zeros, cv 1.0) it is 0.25. The percentile bootstrap
  stays near level (0.028-0.032 against 0.025) in every case. So the risk is "inconclusive", not a false positive.
  The card's stated 0.935/0.82 must be labelled as an assumption and replaced by a D1-based figure before D2 (E4).

**(2) The R12 fork changed from nucleus 0.9 to P_rand.** No contrast enters the gate, and D0 is disjoint from D1 to D3,
so the fork cannot bias the primary's null distribution. Accepted. It creates three inconsistencies (E5):
(a) R2 sizes n_conf from Alt - J on D0 under P, but if P_rand is selected the primary runs under P_rand. Only J is
regenerated, so the sizing SE belongs to the wrong condition. (b) Condition R (section 6) *is* P_rand, so under the fork
the robustness condition repeats the primary. The stop-rule-7 clause "condition R reproduces the null for H-A" then
means nothing. (c) The fork moves H-A too (D2 runs under the selected condition), but the H-A wording in section 2
names only "plain sampling at temperature 1". The PG-2 prefix fork has the same naming issue.

**(3) Matching rule, Jd, NC-6'.**
- Matching rule: the primary estimand stays well defined (DA vs J at matched N and matched per-window budgets). The
  unmatched tokens per pass are an interpretation issue that DA - DA-low (Holm member 3) and Jd address. Accepted.
- Jd and J-global are not pass-matched and appear in no family. The card never says their contrasts are exploratory (E7a).
- **NC-6' as written does not work.** Under the blind model, caption and image are independent given the seed
  (separate uniforms, no cross-modal input). E[Lift] = 0 is therefore exact in every arm, and every contrast is exactly 0.
  It is a good exact null. The pass rule, though, requires every one of about 7 intervals to contain 0 *and* every
  |estimate| < 0.3 point at n = 128, where a contrast's SE is about 0.2-0.5 point. [C] P(pass | exact null) is 0.12-0.63
  over sigma_L 2.5-4 and arm correlation 0-0.6 (0.05-0.40 if "every contrast" means all 6 pairs). The card does not say
  what happens on failure or when NC-6' is scored relative to D3. Fix: E1.
- I2 (bitwise identity) is a deterministic pipeline check. No statistics needed.

**(4) H-C predictor M from D1.** Accepted. M (from D1) is independent of the Sep arms (from D3), so the within-k window
permutation stays valid even though stage 4 runs conditionally on stage-3 outcomes (D3 events cannot change M's
distribution). P_w is constant within k, so it is irrelevant to a within-k Spearman (harmless). Noise in M from 128 (k0)
and 64 (k+) trajectories attenuates rho_strat, which is conservative. Using D1 for both DA's windows and H-C's M couples
the two claims' interpretation, not their error rates.

**(5) Pre-pilot gates PG-1, PG-2.** Feasibility gates with no arm contrast. They cannot bias any test. Accepted, with OCs:
- [C] PG-1 as written (32 captions at 512 px against 16 at 1,024 px, unpaired; [A] SD of raw score 3, of Lift_i 4, lift 8):
  P(pass) = 0.92 when 512 px is truly as good, 0.67 at a 1-point raw deficit with a lift ratio of 0.9, 0.25 at the
  thresholds. Run on the same 32 captions at both resolutions and paired (rho 0.5 [A]), the figures are 0.99 and 0.87, for
  about 0.3 GPU-hours more. A false fail drops the experiment to 256 px or to the reduced 1,024-px tier (n_conf 250, power
  0.80, controls dropped). Recommendation e2.
- [C] PG-2: P(>= 12 of 16) = 0.98, 0.80, 0.63, 0.45 at true rates 0.9, 0.8, 0.75, 0.7. Acceptable for a feasibility gate;
  the fallback prefix is logged before D0.

## EXP-001 new required changes

**E1. NC-6' pass rule, timing and consequence (8.8, 11).** Replace the required result with: "Seven statements, each with
an exact null by construction: Lift = 0 in arms J, Alt, DA, TF, and DA - J = Alt - J = TF - J = 0. NC-6' passes if every
two-sided 99.29 percent bootstrap interval (0.05/7) contains 0. Reported, not gating: the 90 percent intervals and the
achieved equivalence bound max_j(|estimate_j| + 1.645 SE_j) over the three contrasts. Paper 1 states that schedule
artefacts above this bound are excluded at n = 128. NC-6' is scored before any D3 sample is scored. If it fails, D3 is not
scored until the cause is diagnosed (a new card version)." [C] P(pass | exact null) = 0.96 for every sigma and
correlation tried. The median achieved bound is about 0.7-1.2 points at SE 0.31-0.50, so NC-6' excludes artefacts of
roughly MEI size, not smaller. State that.

**E2. G5 statistic, probes and fallbacks (8.7).** Replace with: "On 16 trajectories, at the probes of passes 2 and 30, the
I->T estimate for g = 4, g = 8 and g = 32 (exact). Statistic per probe: ratio of means over trajectories, S(g)/S(32).
Registered g = 4 if both per-probe ratios lie in [0.77, 1.30] and the early/late ratio of means with g = 4 is within
25 percent of that with g = 32; else g = 8 under the same rule (cost per probe R (k_T + 8) = 72 passes, D2 +1.5 GPU-hours,
stated); else I->T is 'chunk-dependent'. In that case H-A1 is decided on T->I alone, H-A2 is reported descriptively, and
the H-A claim is worded 'T->I only'. The Monte Carlo SD of each estimate (from the two R = 4 halves) is reported with
G5." Cost: 16 x 2 x 8 x 32 passes for g = 32, about 0.3 GPU-hours.

**E3. R_Q,d as a ratio of pooled sums (2, 10.3).** Replace "mean over trajectories of sum_j I_hat_j / sum_j H(mbar_j)" with
"(sum over trajectories and early probes of sum_j I_hat_j) / (sum over the same of sum_j H(mbar_j)), divided by the same
at late probes, over committed positions with H(mbar_j) >= 0.05 nats. The share of excluded committed positions is
reported per direction and window". Reason: at k0 the I->T committed set is one position, so the per-trajectory ratio is
0/0 whenever that position is excluded. (This corrects my own R7(d) wording, which assumed several text tokens per pass.)

**E4. H-A power stated from D1, before D2 (10.3).** Add: "The power figures above assume cv 0.6 [A]. After D1 and before D2,
the cv of the window-pair averages (early, late) and their correlation are computed from D1 at k0 for each direction and
for H-A2. The projected P(lower limit >= 1.5 | ratio 1.75) per part and for the conjunction at n = 256 is logged. Paper 1
quotes this figure, not 0.935." Optional extension of the same rule (recommendation e3): n_D2 = min(512, max(256, n_req)),
n_req from the D1 cv for 0.90 per part, used only if the core path stays within 25 GPU-hours (about +2.1 h at n_D2 = 512,
t_b = 0.129 s). This is sizing from independent data before D2, not an extension.

**E5. Consequences of the P_rand fork (4, 6, 10.4, 10.5, 2, 13).**
(a) "If the gate selects P_rand, Alt at k0 is also regenerated on D0 under P_rand (2,048 passes), and R2's sigma_d,up uses
the Alt - J SE under P_rand."
(b) "If P_rand is the primary condition, the robustness condition R becomes condition P (confidence ranking), with the same
arms, n and trace. Stop rule 7's 'condition R' refers to that condition."
(c) "Every claim (H-A, H-B, H-C) is stated 'on UniDisc 1.4B at the resolution PG-1 selects, with the prompt PG-2 selects,
under the position rule the dynamic-range gate selects'. The three gate outcomes are logged together before D1."

**E6. H-B2 wording (2, 11).** Section 2: "H-B2 (confirmatory only if step 1 of 10.2 rejects): holds if its Holm-adjusted IUT
p-value is <= 0.05. The statement 'both one-sided 95 percent upper limits below 1.0' is its unadjusted form, reported as
exploratory."

**E7. Labels and the 1,024-px tier (5.1, 10.2, 4).** (a) "Contrasts involving Jd or J-global are exploratory (unadjusted
95 percent intervals, in no family)." (b) "In the 1,024-px tier n_conf = 250 is fixed by budget. The R2 rule is still
computed from the pilot, and n_req, the achieved MDE at 250 and the 10.2 OC table at n = 250 are logged before D3."

## EXP-001 recommendations (optional)
- e1. In the pilot, G4 prints only the R = 8 vs R = 32 agreement, not the ratio itself.
- e2. PG-1 on the same 32 captions at both resolutions, criteria on paired differences (+0.3 GPU-hours; OC above).
- e3. The n_D2 sizing option in E4.
- e4. Committed-set I->T at k0 may consist mostly of pad/EOS positions early (confidence ranking). Report the share of
  committed text positions that are post-caption at each probe, beside H-A1 I->T.

---

# EXP-002 v0.2

## R-item table

| R | Applied | Comment |
|---|---|---|
| R1 constants | yes | [C] 13.313, 12.788, 12.110, 11.151, 9.505 and every n_B illustration reproduce (log "EXP-002 constants") |
| R2 classes and OC | partly | Option (a) adopted; table correct for M = 4. The P(H1 negative) sentence uses wrong numbers for two k and attributes them to me (M1) |
| R3 H1b in F1 | yes | Fifth member; tested only at three or more k (sensible: at two k the slope is a difference). Slope weights in 9.6 checked |
| R4 sigma_c in pilot | yes | sigma_delta, Delta2 and slope versions written correctly |
| R5 IR4 slope | yes | |
| R6 freeze | yes | Now also prints the OC table for the realised SE and the detectable slope. Good |
| R7 N2 | modified, accepted | Split and firewall resolved as required. The cap of 300 (150 fp32) instead of 1,024 is a cost decision; accepted with the margin widening and the demotion rule. Two consequences must be stated (M2) |
| R8 curvature | modified, accepted | Pooled WLS fit with stage-B cells. [C] Better than required: false flag <= 0.006, power >= 0.92 at a curvature difference of 6 |
| R9 placebo, MC precision | yes | |
| R10 H2 table status | yes | |
| R11 error control | yes | |
| R12 pooled slopes | yes | |

O4 decline: **accepted.** [I] With stage-A placement error about 0.015-0.025 nats (cell-mean SE at n_A = 64 for sigma_H
0.1-0.2 [A]), a +-0.025 bracket would leave h* outside the realised [E_lo, E_hi] in roughly 10-20 percent of (arm, k),
against well under 1 percent at +-0.05. The curvature screen (item 8) covers the bias that O4 targeted, and covers it
well (below).

## The flagged items

**Item 7 (N2, capped n_1, widened margins, demotion).** Accepted, with two required statements (M2).
- [C] P(pass | exact null) = 0.90 holds only at sigma_true = sigma_up. It is 0.73 at 1.2 sigma_up and 0.42 at
  1.5 sigma_up. sigma_up for k = 1 rests on an [A] allowance of 1.2 over k = 4/16 (item 30).
- [C] Demotion fires at raw pilot SD_Y > 0.274 (bf16, n_1 = 300) or > 0.194 (fp32, n_1 = 150), and SD_H > 0.165 / 0.116.
  With sigma_y in 0.25-0.5 [round 1], N2-Y will probably be "reported only" in the fp32 branch and often in bf16.
- [C] At the planning margins N2-Y passes a true A3 artefact of 0.03 (the size of delta_cp) with probability 0.57-0.83.
  It is a gross-failure check, as the card says. [I] At k = 1 the A3 recipe's law of the minimum of the other k - 1
  members (5.3 step 4) is trivial, so N2 does not test the k >= 2 machinery at sequence level at all. Protection at the
  delta scale rests on T-A3-2, N1 and N5(a), all state-level.
- When N2-Y is not demoted and fails, every G_cp conclusion is voided. A correct pipeline fails it with probability 0.10,
  independently of stage B (different samples). So P(G_cp counted | G_cp = 0.03 at one k) <= 0.80 x 0.90 = 0.72 before
  the other guards. The card states 0.80 (M2).

**Item 8 (curvature fitted on stage-A plus stage-B cells).** Accepted. [C] With the two stage-B cells (n_B about 2,500)
pinning level and slope at h*, SE(kappa) is 0.4-1.1 per nat^2 and SD(b_theta) 0.002-0.004 for E spacings of 0.10-0.20 nats
per grid step and sigma_y 0.3-0.5 [A]. P(flag | equal curvature) <= 0.006; P(flag | curvature difference 6) = 0.92-0.996
(log "EXP-002 IR8 (iv)"). The card's own "SE of the order 1 to 2" is pessimistic. Two notes: the flag is computed after
evaluation from primary data, which is acceptable because it can only downgrade; and the quadratic is fitted over +-0.3
nats, so a frontier with a local kink is not screened (stated limit).

**Item 13 (95 percent intervals in the "H1 negative" conjunction).** The rule is correct: intersection-union with each
TOST at 0.025 per side, the level of F1. The quoted probabilities are wrong for the rung that will run. [C] At the sized SE,
independent k:

| Rung | k | SE | P(H1 negative \| 0), 95% | 97.5% | card |
|---|---|---|---|---|---|
| R0 | 4 | 0.0082 | 0.68 | 0.50 | 0.64 / 0.45 |
| R1 | 3 | 0.0084 | 0.72 | 0.55 | none |
| R2 | 2 | 0.0090 | 0.69 | 0.53 | 0.80 / 0.67 |
| R3 | 1 | 0.0097 | 0.74 ("practically 0 at k = 16") | 0.60 | none |

If the true sigma equals the pilot point estimate (sigma_up / 1.13), the 95 percent figures are 0.87-0.89. A correlation of
0.6 between k raises them by at most 0.06. The card's two-k figures are 0.895^2 and 0.819^2, computed at the M = 4 SE.
Also note: per-k "practically 0" in the H2 table uses 97.5 percent, so H1 negative (95 percent) can coexist with per-k
class "?". That is a valid but confusing result; one sentence in 11.2 should say it.

**Item 18 (H4 pooled over five taus).** The pooled TOST is valid: the bootstrap over s carries the cross-tau correlation.
Its power depends on that correlation, which common random numbers keyed by s make positive. [C] P(pass | true 0) is 0.99
at sigma_H 0.15 with no cross-tau correlation, 0.57 at correlation 0.5 and 0.32 at 0.8 (a single cell: 0.19). The real
problem is the reading of failure. 2 (H4), 11.3 (F-H2-twin) and 14 treat "H4 (i) fails" as evidence that "coupling
changes diversity". A failed equivalence test is absence of evidence of equivalence, not evidence of a difference (M4).

**Item 27 (stage A for the rung's k only; A3 on five taus).** Accepted. Every decision is entropy-only and taken before any
Y exists. A3 keeps at least four cells within +-0.3 nats for IR4 and the curvature screen. The extension rule handles a
shifted A3 curve. The rung becomes irreversible once stage A runs; that is consistent with 9.6.

**Item 28 (N5 split).** Accepted. N5(a) is a state-level gate with no contrast. N5(b) has a sensible double criterion.
[C] If the A3 bins-doubled run stays tightly coupled to the stage-B A3 cell through shared uniforms (paired SD 0.05-0.1),
it has no false flags and full power at 0.03. If the trajectories decorrelate (paired SD 0.42), the false flag rate is
0.05 and power at 0.03 only 0.37. The inconsistency must be fixed: table 10 calls N5(b) descriptive with a flag, while 11.2
"counts" a G_cp only if N5(b) "did not fail" (M3).

**Item 30 (N2 sizing variance from the pilot's tau = 1.0 cells at k in {4, 16}).** Accepted. The k = 1 SD is an
extrapolation covered by an [A] factor of 1.2. Recommendation r1 replaces it with a measurement at no cost.

**Item 31 (ladder with M counting H1b).** Accepted: the rung is chosen from variance and cost only, M is correct per rung,
and [C] the 12.5 table reproduces from the card's inputs (bf16 R2 2,510 vs 2,509; R3 6,502 vs 6,504; rounding of inputs).
One ambiguity: 9.6 sizes n_B = n_B(R) (the power-0.80 n), but the 12.5 worked plan uses the *affordable* n_B (2,509 at
R2). At sigma_up = 0.30 under R2 these differ by a factor of 2.2 (1,116 vs 2,509), and so does the outcome distribution
(M5).

## EXP-002 new required changes

**M1. Correct the P(H1 negative) figures (9.5, change-log item 13).** Replace the sentence with: "If G_cp = 0 at every
estimable k, P(H1 negative) with the 95 percent rule at the sized SE is 0.68 (R0), 0.72 (R1), 0.69 (R2), independent k
(0.50, 0.55, 0.53 with 97.5 percent); about 0.87-0.89 if the true sigma equals the pilot point estimate. At R3, P('practically 0
at k = 16' | 0) = 0.74. The freeze step prints the value for the realised SE and K_R." Add: "H1 negative uses 95 percent
intervals and the per-k H2 classes use 97.5 percent, so H1 negative can coexist with per-k class '?'."

**M2. What N2 costs and what it excludes (10, 11.2, 14).** Choose one:
(a) keep m = 3.29 SE and add to 9.5: "When N2-Y gates (not demoted), a correct pipeline loses all G_cp conclusions with
probability 0.10, so P(G_cp counted | G_cp = 0.03 at one k) <= 0.72"; or
(b) set m = 3.886 sigma_up sqrt(2/n_1) for N2-Y (P(pass | null) = 0.975; 0.78 then), with the demotion threshold unchanged.
In both cases add to 14: "N2 excludes, at k = 1 only, A3 sequence-level artefacts larger than the achieved m_H and m_Y (or
was demoted). It does not exercise the k >= 2 part of the A3 recipe. The protection at the scale of delta_cp is state-level
(T-A3-2, N1, N5(a))." The achieved margins or the demotion are reported next to every G_cp claim.

**M3. N5(b) is a flag (10, 11.2).** Delete "and N5(b)" from the counting condition in 11.2. Keep "numerically sensitive" as
a flag carried by the claim, consistent with table 10. Add its OC: "false flag about 0.05 and power about 0.37 at a
true difference of 0.03 if the bins-doubled trajectories decorrelate from the stage-B A3 cell (paired SD 0.42 [A]); no false
flags and full power if they stay coupled (paired SD <= 0.1). The realised paired SD is reported."

**M4. Three-way H4 (i) outcome (2 H4, 11.3 F-H2-twin, 14).** Replace the failure reading with: "H4 (i) is *equivalent* if the
90 percent interval lies inside +-0.05; *different* if the 95 percent interval excludes 0 and the estimate is outside
+-0.05; otherwise *not established*. F-H2-twin and the statement 'coupling changes diversity' apply only to *different*.
*Not established* is reported with its interval, and the decomposition carries the flag 'twin equivalence not shown'."
The pilot also prints the projected P(equivalent | 0) from SD_H and the realised cross-tau correlation of H(A1) - H(A3)
within s. Reason [C]: at sigma_H 0.15 and cross-tau correlation 0.5-0.8 a true zero difference fails the TOST with
probability 0.43-0.68.

**M5. Pin n_B (9.6, 12.5).** State one rule. Either "n_B = n_B(R), the sized n, with any remaining plan budget going to S7"
or "n_B = the affordable n_B at the chosen rung (the full 36-hour plan), never below n_B(R)". I recommend the second: it
costs no extra GPU time within the plan, raises P(H1 negative | 0) toward 0.87, and shrinks the MDE. The 12.5 worked plan
must match the rule.

**M6. Claim scope by rung (1.1, 0, 14).** Claim 1.1 says the coupling part "grows with the number of tokens committed per
step", which only R0 and R1 can test. Replace with: "... and the coupling part is non-zero at the k that run (R0, R1: and
grows with k, H1b; R2: at k in {8, 16}, i.e. 128 and 64 forward passes for L = 1024; R3: at k = 16 only). Growth in k is
not claimed at R2 or R3." Make the same change in the summary (section 0).

## EXP-002 recommendations (optional)
- r1. Run the 96 A2 sequences of the k = 1 block first. Set sigma_up,Y and sigma_up,H for N2 as the larger of the
  pilot-based value and the A2 k = 1 SD times sqrt(95 / chi2_{0.20,95}). No A1/A3 contrast is involved. This replaces the
  1.2 allowance with a measurement.
- r2. The freeze step prints the IR8 (iv) false-flag rate and power at a curvature difference of 6 for the realised cell
  placement and pilot sigma_y.
- r3. For N2-H (gates stage B), consider m = 3.605 SE (P(pass | null) = 0.95). The pre-stage-B false-stop probability
  (N2-H 0.10, N1 <= 0.05) is about 0.15 as written.

## Note on scope: is a k in {8, 16} (or k = 16 alone) experiment worth running?

**Yes for R2, conditionally for R3, provided the card and Paper 1 state the scope as in M6.**

[S] The MDLM repository's default sampler uses 128 steps at L = 1024 (setup.md line 165, "repo defaults (`ddpm_cache`,
128 steps)"). [I] So k = 8 has the same number of forward passes as the repo default, and k = 16 (64 passes) is the next
halving, the regime where practitioners use parallel decoding. Prop. 4 and the kernel readout predict coupling (TC_A) to
increase with k, so the largest k is where an effect is most likely to show. The question the review raises is whether
treating sample-then-filter as a state-dependent tilt at k >= 2 matters for output quality. That question is answered for
the practical regime, at full design power (0.80 at delta_cp = 0.03 per k). Every outcome is reportable: a supported
G_cp shows the tilt reading fails in practice; H1 negative at both k (probability 0.69 at the sized n, up to about 0.87
with M5's second option, under a true zero) bounds the effect at practical parallelism; "inconclusive" comes with an MDE.

What R2 cannot deliver: no dose-response (H1b untested), no statement about k = 2 or 4 (the toy prior's k = 2 is not
tested), and no "k >= 2" wording. Monotone growth of coupling in k is a hypothesis. A null at k = 16 suggests, but does
not show, a null at smaller k; Paper 1 may say "predicted smaller at smaller k, not tested".

R3 (k = 16 only, the likely fp32 outcome) spends about 36 GPU-hours on one contrast. "H1 negative" cannot be declared,
only "practically 0 at k = 16" (probability 0.74 under a true zero). It still answers whether the coupling matters at
the largest practical k. Whether that is worth the budget is the orchestrator's call; it is statistically sound.

Wording the card should carry (M6 plus 14): "On MDLM-OWT (170M), plain sampling, precision branch X, GPT-2 Large log
GenPPL at the held-out unigram entropy h*, at k in {8, 16} (128 and 64 forward passes for 1024 tokens): G_cp(8) = ...,
G_cp(16) = ... with 95 percent intervals; no statement about smaller k or about growth in k." Never "at k >= 2", never
"grows with parallelism".

---

## Concerns outside the brief
- System commit was exhausted during this review (CPU numpy allocations of 2 MB failed). GPU runs of both cards gate on
  it (setup.md 0); rebooting before the pilots would remove a source of unplanned retries.
- EXP-001: the D0-sized sigma_d is for Alt - J; DA - J may be more strongly paired (shared windows), so n_conf is
  conservative, which is acceptable.
- EXP-002 N2 at k = 1 does not test the k >= 2 part of A3 at sequence level. This is a red-team matter (validity), noted in M2 only for wording.

## Note on what is NOT checked here
The A3 recipe's correctness, the S_theta estimator on a real network, chunk bias direction, wiring of the arms and the
CLIP/GPT-2 pipelines are the red-team's and lab-engineer's. Every [A] value above is a placeholder that the pilots or D1
replace. This review signs analysis plans, not results.
