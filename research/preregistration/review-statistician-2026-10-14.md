```yaml
agent: statistician
date: 2026-10-14
brief: Pre-outcome review of the statistical analysis plans of EXP-001 v0.1 (UniDisc cross-modal) and EXP-002 v0.1 (SF value-rule decomposition); verdict per card with required changes concrete enough to apply.
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-001-crossmodal-unidisc.md (v0.1, lines 1-625, read in full)
  - research/preregistration/EXP-002-value-rule-decomposition.md (v0.1, lines 1-785, read in full)
  - research/review/framework-v2.md (sections C and D)
  - analysis/framework/check_coupling_k2.log (summary lines)
  - analysis/stats/exp001_stats_check.py and .log (written for this review)
  - analysis/stats/exp002_stats_check.py and .log (written for this review)
coverage: >
  Both cards in full, with the statistical sections (EXP-001 sections 2, 6 gate, 7, 8.3-8.5, 10, 11;
  EXP-002 sections 2, 5.5, 7, 8, 9, 10, 11, 13.4) checked line by line. Not covered:
  runs/env-2026-10-14/setup.md does not exist at review time (the directory holds only
  logs/download_c1_c2.log and scripts/download_weights.py), so geometry, padding share, timings and pinned
  versions are unknown here. No model code and no model output exist; nothing in this review is an
  experimental result. Estimator validity (S_theta reveal-and-requery, the A3 quadrature) is the red-team's
  remit and is touched only where it affects inference. No GPU was used; no ledger rows were written; no
  card was edited.
claims:
  - statement: "EXP-001 10.4 arithmetic is correct: n = 337 at alpha 0.05 and 505 at alpha 0.05/7 (sigma_L = 4, rho_pair = 0, m = 1, power 0.90); powers 0.977/0.897, 0.885/0.682, 0.750/0.478 at sigma_L = 4, 5, 6 and n = 500."
    status: supported
    evidence: analysis/stats/exp001_stats_check.log, section "10.4"
    level: E4 (computation)
    confidence: 0.99
  - statement: "Under both cards' outcome rules ('positive' needs significance AND point estimate >= MEI), the probability of a 'positive' verdict when the true effect equals the MEI is 0.50, not the stated power (EXP-001: 0.977 is P(significant); EXP-002: 0.80 is P(significant))."
    status: supported
    evidence: exp001_stats_check.log "Decision-rule operating characteristics"; exp002_stats_check.log "9.5 outcome classes"
    level: E4 (computation)
    confidence: 0.97
  - statement: "EXP-001 H-A extension rule (extend 128 -> 512 once if the interval straddles 1.5, then decide at the same 95% level) raises the one-sided type I error of a 'positive' H-A verdict from 0.025 to 0.045."
    status: supported
    evidence: exp001_stats_check.log "H-A extension rule" (2,000,000 simulated two-look trials, information fraction 0.25)
    level: E4 (simulation)
    confidence: 0.95
  - statement: "EXP-001 H-C as written (Spearman over 16 pooled cells, unstratified permutation) declares 'supported' in 97 percent of simulated cases with no within-k association when M and Delta both shift between k0 and k+; a within-k stratified statistic holds 0.04-0.05."
    status: supported
    evidence: exp001_stats_check.log "H-C"
    level: E4 (simulation)
    confidence: 0.95
  - statement: "For the EXP-001 Lift endpoint, the per-seed SD of Lift_i understates the sampling SD of mean Lift because B_i enters every other seed's baseline; the influence value is 100 (C_i - 2 B_i). In a synthetic check: per-seed SD/sqrt(n) 0.264, influence SD/sqrt(n) 0.313, bootstrap SE 0.307, true SD 0.306."
    status: supported
    evidence: exp001_stats_check.log "Lift" (synthetic embeddings; magnitude depends on embedding geometry)
    level: E4 (synthetic)
    confidence: 0.75
  - statement: "EXP-002 9.6 constant is 12.788 for m = 4 (12.75 in the card comes from z rounded to 2.73); 12.110, 11.151, 9.505 for m = 3, 2, 1. Illustrative n_B become 889, 2274, 5116 (card 885, 2267, 5100)."
    status: supported
    evidence: exp002_stats_check.log "9.6 constant"
    level: E4 (computation)
    confidence: 0.99
  - statement: "EXP-002 H1b gatekeeping (H1b at full 0.025 after any F1 rejection) does not control FWER at 0.025 over {F1, H1b}: 0.036 when G_cp = (6, 0, 0, 6) SE units; putting H1b into F1's Holm family (m = 5) gives 0.025."
    status: supported
    evidence: exp002_stats_check.log "H1b"
    level: E4 (simulation)
    confidence: 0.95
  - statement: "EXP-002 N2 gate (TOST 90% CI of Y(A1) - Y(A3) inside +-0.05 at n_1 = 256, arms uncorrelated) passes an exactly null contrast with probability 0.46, 0.19, 0.00, 0.00 at sigma_y = 0.25, 0.30, 0.40, 0.50; it therefore stops stage B with high probability when nothing is wrong."
    status: supported
    evidence: exp002_stats_check.log "N2 gate"
    level: E4 (computation, sigma_y assumed)
    confidence: 0.85
  - statement: "EXP-002 linear interpolation at h* with a paired percentile bootstrap holds its level when A1 and A3 frontiers differ in slope (rejection 0.037 at nominal 0.05) but not when they differ in curvature (0.152 for curvature difference 6 per nat^2, bias 0.015 = kappa_diff x 0.05^2)."
    status: supported
    evidence: exp002_stats_check.log "IR1 decomposition"
    level: E4 (synthetic)
    confidence: 0.85
  - statement: "EXP-002 IR4 with beta_A treated as a fixed constant omits variance of the order 0.01-0.02 log-GenPPL units at |h* - E_cell| = 0.03-0.05 (n_A = 64), comparable to the per-arm SE at n_B = 1000."
    status: supported
    evidence: exp002_stats_check.log "IR4"
    level: E4 (computation, sigma_y and stage-A gaps assumed)
    confidence: 0.7
competing_explanations:
  - "All power and n statements depend on assumed variance components (sigma_L, sigma_y, sigma_h, rho_yh, beta, cross-arm correlations); the pilots replace them. The direction of the findings above does not depend on the values; the magnitudes do."
unknowns:
  - real sigma_d for DA - J (DA is not in the EXP-001 pilot; Alt - J is the proxy)
  - sigma_c for G_cp on MDLM-OWT; within-cell corr(Y_s, H_s); frontier slope and curvature near h*
  - share of padding in UniDisc text positions (changes the k grid and H-A2 counts)
  - whether MDLM A1/A3 reach h* inside Gamma_A
next_test: {hypothesis: "pilot variance components fall inside the ranges assumed here", intervention: "run EXP-001 D0 and EXP-002 S2 with the firewalled pilot scripts required below", primary_metric: "sigma_d,up (EXP-001, Alt - J at k0, full pipeline); sigma_c,up (EXP-002, max of jackknife and delta-method)", falsifier: "EXP-002: sigma_c,up > 0.6 gives MDE > 0.06 even at R1 within a 45 GPU-hour stage B, i.e. H1 cannot be decided at delta_cp = 0.03", gpu_hours: "as in the cards (EXP-001 stage 1; EXP-002 S2 about 0.5-1.0)"}
```

# Statistician review of EXP-001 v0.1 and EXP-002 v0.1 (pre-outcome)

Tags: [S] source fact with location; [I] inference; [C] computed here (script and log named); [A] assumption.
No experiment has run. Every number below is a formula result or an operating characteristic of a
decision rule under stated assumptions, from `analysis/stats/exp001_stats_check.log` and
`analysis/stats/exp002_stats_check.log`. None is an experimental result.

Commands (both ran on CPU, Python 3.14.3, numpy 2.4.2, scipy 1.17.1):

    python analysis/stats/exp001_stats_check.py > analysis/stats/exp001_stats_check.log   # about 20 s
    python analysis/stats/exp002_stats_check.py > analysis/stats/exp002_stats_check.log   # about 90 s

## Verdicts

| Card | Verdict | Blocking items |
|---|---|---|
| EXP-001 v0.1 | **Sign with the required changes below** (12 items) | H-C pooled Spearman (R8), H-A extension without alpha spending (R7), pilot not firewalled (R1), sizing variance and an ambiguous rho rule (R2), primary and secondary families both at 0.05 without gatekeeping (R3) |
| EXP-002 v0.1 | **Sign with the required changes below** (12 items) | N2 gate fails under an exact null and conflicts with the firewall (R7), H1b gatekeeping does not control FWER (R3), beta_A not propagated in IR4 (R5), no curvature check on the interpolation (R8), pre-evaluation freeze of branches and families (R6), OC of the decision rules not stated (R2) |

Neither card needs a redesign. All required changes are edits to the analysis plan and can be made before
any data exist. I sign each card when its v0.1 to v0.2 change log shows every required item applied (or,
for items where I give options, one option applied). Recommended items are optional.

## Cross-cutting recommendation: alpha across the two experiments (S3)

**Recommendation: control error per experiment, not split across the two.** [I] EXP-001 and EXP-002 test
unrelated hypotheses on different models. Neither conclusion depends on the other, and Paper 1 does not
make a disjunctive claim ("at least one of the two predictions holds"). A Bonferroni split across
experiments would protect a claim nobody makes. Within each experiment, the family is the set of tests
that supports one stated claim:
- EXP-001: H-B (primary plus gatekept secondaries, FWER 0.05), H-A (one conjunctive claim, intersection-union
  at one-sided 0.025 per ratio), H-C (one test at one-sided 0.05). The card must state that these are three
  separately controlled claims (R11).
- EXP-002: F1 and F2 at 0.025 each (the card's own conservative choice; keeping it is fine).

**What the review should report, as the brief asks:** (a) the registered per-experiment results; (b) a
sensitivity in which every confirmatory level in both cards is halved (Bonferroni across the two
experiments: EXP-001 primary at 0.025, its Holm family at 0.025, H-A one-sided 0.0125 per ratio, H-C 0.025;
EXP-002 F1 and F2 at 0.0125 each), with a column saying which claims survive. Both are computable from the
same bootstrap output; no extra runs.

## Cross-cutting recommendation: fixed or sequential design (S4)

- EXP-001 H-B: **fixed** n_conf, set from the pilot's variance only (as the card intends, with R1 and R2).
- EXP-001 H-A: **fixed n = 256 at k0** (R7, option a). The card's one-shot extension is a two-look
  sequential design run at the fixed-design level. If the extension is kept, it needs the boundaries in R7(b).
- EXP-002: **fixed** (as written in 9.7; keep). A sequential design would need interim evaluator calls,
  which would break the firewall that is the card's strongest feature.

---

# EXP-001 v0.1: cross-modal dependence in UniDisc

## Findings by check

**S1 unit, pairing, common random numbers.** The unit is the seed i (section 4), and every arm uses the same i
with per-position float64 uniforms. Pairing is valid for any coupling: the paired bootstrap does not need
positive correlation, only that seeds are independent, which they are. Two gaps:
(i) the endpoint is not a mean of independent per-seed values. B_i averages over all other seeds of the same
arm, so seed j enters every B_i. The bootstrap with in-replicate baseline recomputation and same-seed partner
exclusion (10.1) handles this correctly: in a synthetic check the bootstrap SE was 0.307 against a true
sampling SD of 0.306 [C, exp001 log "Lift"]. The sample-size rule, however, uses the per-seed SD of Lift_i,
which gave 0.264 there (16 percent low). The correct per-seed influence value of mean Lift is
psi_i = 100 (C_i - 2 B_i) (Hajek projection of the off-diagonal mean), whose SD gave 0.313. R2 fixes the rule.
(ii) The pilot cannot measure rho_pair for DA - J because DA is not run on D0 (its window set M comes from D1).
Alt - J is the right conservative proxy: Alt differs from J in all 8 windows, DA in 4.

**S2 single estimand, gate, forking paths.** The primary estimand is single (DA - J at k0, mean Lift, paired,
condition P). DA's window set M comes from D1 S_theta, not from Lift, and is hashed before D3. That is a clean
separation. The dynamic-range gate uses only Lift(J) on D0, which is disjoint from D3, and no contrast, so it
cannot bias the D3 contrast's null distribution. But the gate is a fork in the estimand (P or P'), so the
primary must be named as "DA - J at k0 in the condition selected by the gate", and the gate statistic must be
pinned (R12). The pilot also produces Lift for Alt, TF, IF (at k0, and Alt at k+). Without a firewall these are
interim looks at confirmatory-family contrasts (Alt - J is family member 1): R1.

**S3 multiplicity.** The primary is at 0.05, and a 7-test Holm family runs separately at 0.05, so the H-B
claims together carry an FWER up to about 0.10. Test 6 (DA - J at k-) exists only if stage 5 runs, and stage 5
runs only when a stage-3 contrast is positive or reversed. That makes the family size outcome-dependent. The
"n > 1000" branch removes all secondary tests except H-B2. The outcome classes use unadjusted 95 percent
intervals even for family members. Fixes in R3 and R4.

**S4 power and sample size.** The formulas and numbers in 10.4 are correct [C]:

| sigma_L | n = 500 power at 0.05 | at 0.05/7 |
|---|---|---|
| 4 | 0.977 | 0.897 |
| 5 | 0.885 | 0.682 |
| 6 | 0.750 | 0.478 |

n = 337 at 0.05 and 505 at 0.05/7 (sigma_L = 4, rho 0, power 0.90). sigma_L = 4 points is plausible for a
CLIP-based score [E0; no source read], but the pilot must replace it with the influence-based value (S1 (i)).
The pilot is restricted to variance and cost (10.5), which is right. It needs the firewall of R1. The
n_conf rule's clause "halved in its (1 - rho_pair) factor only if the pilot rho_pair interval lies above 0.3"
is ambiguous and unnecessary once sigma_d is estimated directly from paired differences (R2). The rule also
contradicts itself: min(1000, ...) can never "exceed 1000", yet the next sentence branches on it.

**S5 intervals and the H-A trace statistic.** The H-B interval (percentile paired bootstrap, B = 10,000,
baseline recomputed, BCa sensitivity) is appropriate, but no p-value is defined and Holm needs one (R5).
H-A1 (early/late ratio of means per direction, bootstrap over trajectories, lower limit at least 1.5) is a
sound statistic, and the brief's suggested "share in the first quarter" adds nothing beyond it as a decision
statistic. A within-trajectory label-permutation ("shuffled") null has expected ratio 1, which the 1.5 margin
already exceeds. The real gap is the reference. Raw S_theta can decline or rise over the trajectory for generic
reasons: entropy available to depend on falls as context grows, and confidence ranking defers high-entropy
tokens. The bound S_j <= H_j means a raw ratio of 1.5 may only restate the entropy profile. The card has the
right tool (Q = I/H, section 8.5) but uses it only for H-A2. Probe definition is also loose: pass 1 sits in
window 1, and under the default geometry pass 1 commits 2 text + 6 image tokens while every centre probe
(q = 3 of 6) commits 3 + 5 (floor rule of 5.1, computed by hand). The k at which H-A is decided is not stated.
For H-A2, committed sets hold about 3 text positions per probe, too few for per-sample type means. Fixes in R7.

**S6 stop rules, nulls, equivalence.** The null class ("95% interval inside (-m, m)") is a TOST at 0.025 per
side: valid and conservative. Under sigma_L = 4 and n = 500, P(null | d = 0) = 0.954 [C]. The H-B null across
k+, k0 and three contrasts is a conjunction, so intersection-union applies and no multiplicity adjustment is
needed. State that (R6). "max(TF, IF) - J null" and H-B2's max need the IUT form (R6). H-A "falsified in the
weak form if the upper limit of any ratio is < 1.5" is a disjunction over three ratios. P(false weak
falsification) is up to about 0.075 when all three true ratios equal 1.5. This is acceptable if stated (recommended item O6).

**S7 metric validity.** (a) Floor: the dynamic-range gate (Lift(J) >= 2 points) is the right kind of guard. At
n = 64 its SE is about 0.5-0.7 points [A, sigma_L 4-5.6], so a true Lift(J) of 2.5 fails the gate about 20
percent of the time (O1). (b) Ceiling: Ref-real lift bounds what is achievable. If Lift(J) is near 2-3 points,
an MEI of 1 point is a third to a half of the dynamic range. Report the primary also as a fraction of
Lift(Ref-real) - Lift(J) (descriptive, O2). (c) CLIP truncates at 77 BPE tokens while captions can reach 128
UniDisc text positions, so arms with longer captions are scored on a prefix. The length guardrail catches only
part of this (O3). (d) Guardrails mix population metrics (KID) with "0.2 pilot SD", which KID does not have
per sample. Define them (O4).

**S8 what a reviewer would call p-hacked.** As written: the H-A extension (alpha inflation 0.025 to 0.045), the
pooled H-C Spearman (can be "supported" by a between-k shift alone), the unfirewalled pilot, the
outcome-dependent family size, and claiming "positive" at the stated power when the rule's probability at the
MEI is 0.50. After R1 to R12, I see no remaining forking path: M from D1, n from variance, the gate from J alone,
disjoint seed pools, no exclusions, and analysis frozen before scoring.

## EXP-001 required changes (numbered; apply all)

**R1. Pilot firewall (10.5).** Add: "The D0 analysis script computes and writes only: per-arm SDs of the
influence values psi_i (R2), bootstrap SEs and correlations of paired contrasts, cost and memory figures,
noise floors, padding share, and the point estimate of Lift(J) with its bootstrap SE (for the dynamic-range
gate). It does not compute into any printed or saved field the mean Lift of Alt, TF, IF or Ref-T2I, or the mean
of any contrast. Its source is hashed in `runs/EXP-001/pilot/` before D0 is generated." (PC-A needs
Lift(Ref-real) and Lift(J) only. Keep the Ref-T2I ordering for stage 3c; see O5.)

**R2. Sizing variance and the n_conf rule (10.4).** Replace the rule with:
"sigma_d,up = sqrt(64) x (bootstrap SE of the paired contrast Alt - J at k0 on D0, full Lift pipeline with
in-replicate baseline recomputation, B = 10,000) x sqrt(63 / chi2_{0.20, 63}).
n_req = ceil(1.5 x ((1.96 + 1.2816) sigma_d,up / 1.0)^2). n_conf = min(1000, max(500, n_req)). If n_req > 1000,
n_conf = 1000, all tests still run, and the achieved MDE (1.96 + 1.2816) sigma_d,up / sqrt(1000) is reported."
Delete the rho_pair halving clause: sigma_d,up already contains the pairing. Delete "only the primary contrast
and H-B2 are run" (that branch changes the family size; see R3). sqrt(63 / chi2_{0.20,63}) is the one-sided
80 percent upper bound used in EXP-002, adopted for consistency. Reason: the per-seed SD of Lift_i understates
the SE (S1 (i)); a directly estimated paired SE needs no rho term; Alt - J is the conservative proxy for DA - J.

**R3. Multiplicity structure for H-B (10.2).** Replace the two bullets with:
"Fixed-sequence gatekeeping at FWER 0.05 for H-B. Step 1: H-B1 (DA - J at k0), two-sided 0.05. Step 2, only if
step 1 rejects: Holm at 0.05 over the six secondary tests (1) Alt - J at k0, (2) DA - J at k+, (3) DA - DA-low
at k0, (4) TF - J at k0, (5) IF - J at k0, (7) H-B2 by IUT (R6). If step 1 does not reject, the six are reported
with Holm-adjusted p-values and labelled exploratory. A test that is not run enters Holm with p = 1. DA - J at
k- moves out of the family into H-B3 (dose; estimation only), because stage 5 runs conditionally on stage-3
outcomes." Reason: total FWER for the H-B claims becomes 0.05 instead of up to 0.10, and the family no longer
depends on outcomes. (Option if the designer wants secondaries confirmatory whatever the primary result: one
Holm family over all 7 tests at 0.05, with the primary given no special status. Either is acceptable; state which.)

**R4. Outcome classes and their operating characteristics (10.2).** (a) For family members, "positive" and
"reversed" require the Holm-adjusted p-value <= 0.05 (not the unadjusted interval); unadjusted 95% intervals
are still reported. (b) Add the operating-characteristics table [C, n = 500, sigma_L = 4, rho 0]:

| true d (points) | P(lo > 0) | P("positive": lo > 0 and d_hat >= 1) | P("null") |
|---|---|---|---|
| 0.0 | 0.024 | 0.000 | 0.954 |
| 0.5 | 0.507 | 0.024 | 0.506 |
| 1.0 | 0.976 | 0.501 | 0.026 |
| 1.25 | 0.999 | 0.839 | 0.002 |
| 1.5 | 1.000 | 0.976 | 0.000 |

(c) Then either keep the rule and write "power 0.977" as "P(significant) = 0.977; P(positive at the MEI) = 0.50,
P(positive) >= 0.84 for d >= 1.25", or redefine the classes as "positive" = lo > 0, with the label "at or above
the MEI" added when d_hat >= 1. I recommend the second. It keeps the hypothesis (direction) and its practical
qualifier separate.

**R5. p-values and Monte Carlo precision (10.1).** Add: "Two-sided p for a paired contrast:
p = 2 min{(1 + #{theta* <= 0})/(B + 1), (1 + #{theta* >= 0})/(B + 1)}, capped at 1, from the same bootstrap that
gives the interval. If any p lies within 2 sqrt(p(1-p)/B) of the Holm threshold it is compared with, that
bootstrap is rerun once with B = 100,000 and a fixed seed recorded in the manifest, and the B = 100,000 value
is used." For H-A, H-C as in 10.3.

**R6. Max contrasts by intersection-union (2, 10.2, 11.3).** Replace "max(Lift(TF), Lift(IF)) - Lift(Alt)
< 1.0" with: "H-B2 holds if both one-sided 95 percent upper limits, of TF - Alt and of IF - Alt, are below 1.0
point (intersection-union test at 0.05; no adjustment for the conjunction)". In stop rule 3 replace
"max(TF, IF) - J is null" with "TF - J and IF - J are both null". Add a sentence: "Null verdicts that are
conjunctions over contrasts or k are intersection-union tests and need no multiplicity adjustment." [C] A
percentile bootstrap of the max has rejection 0.003 against the IUT's 0.010 at the H0 boundary: valid but
conservative and, more to the point, not specified.

**R7. H-A decision rules (2, 8.3, 10.3, 11.2).**
(a) Sample size: "D2 = 256 trajectories at k0, fixed; no extension." [C] SE(ln ratio) = 0.0444 at n = 256
(cv 0.6, r 0.3 [A]); P(lower limit >= 1.5) = 0.935 at a true ratio of 1.75 and 0.025 at 1.5. Cost: 128 more
trajectories x 624 passes. If the designer keeps the extension instead, the two-look rule must be: at 128,
"positive" only if the one-sided z for ln(ratio/1.5) is >= 4.33 (Lan-DeMets O'Brien-Fleming spending,
alpha_1 = 7.4e-6); weak falsification at 128 as written (binding futility); at 512, "positive" if z >= 1.957.
[C] The card's rule (1.96 at both looks) has one-sided type I error 0.045 against a nominal 0.025.
(b) Probes: "H-A1 numerator = centre probes of windows 1 and 2 (passes 3 and 9 at k0 in the default geometry);
denominator = centre probes of windows 7 and 8 (passes 39 and 45). Pass 1 is reported separately because its
committed set differs in composition (2 text + 6 image against 3 + 5 under the default geometry). Per
trajectory, average the probes in each window pair, then take the ratio of the means over trajectories."
(c) "H-A is decided at k0 only; k+ is descriptive."
(d) Entropy-normalised companion, registered now: "R_Q,d = mean over trajectories of sum_{j in committed
set} I_hat_j / sum_j H(mbar_j) at early probes, divided by the same at late probes. Wording rule: a raw H-A1
lower limit >= 1.5 supports 'cross-modal dependence in nats is front-loaded'. The claim 'front-loaded beyond the
entropy available' needs R_Q,d lower limit >= 1.0 in both directions as well. Otherwise Paper 1 says the trace
follows the entropy profile." This is the pre-specified null reference the brief asks for. A
shuffled/permuted-window null has expectation 1 and adds nothing beyond the 1.5 margin.
(e) H-A2: "computed on all still-masked text positions (the all-masked-position version) at the early centre
probes, pooled ratio of means: (sum of Q over object positions / their count) / (sum of Q over function-word
positions / their count), bootstrap over trajectories. Report, by type, the share of positions excluded by
H(mbar) < 0.05."

**R8. H-C must be stratified by k (10.3).** Replace "Spearman rho over 16 cells, one-sided permutation test
(cell labels permuted)" with: "rho_strat = mean of the within-k Spearman correlations of (M_{w,k}, Delta_{w,k})
over w = 1..8, for k in {k0, k+}; one-sided permutation test permuting windows within each k separately
(100,000 draws); supported if rho_strat >= 0.5 and p <= 0.05." [C] One-sided 5 percent critical value of
rho_strat = 0.440 (the pooled-16 value is 0.421, matching the card's "about 0.43"). Reason [C]: with no
within-k association, a between-k shift of 3 SD in both M and Delta gives a median pooled rho of 0.71 and a
false "supported" in 97 percent of cases. The shift is expected because P_w and S differ between k0 and k+,
and all Delta at one k share the same J estimate. rho_strat stays at 0.043-0.048. In 10.4 replace the SE(Delta_w)
formula with "bootstrap SE of Delta_w projected from the pilot Alt - J SE" and note that
stop rule 4's bound 0.15 needs rho_pair >= 0.65 at n = 500 or >= 0.30 at n = 1000 (by the card's own formula,
computed by hand).

**R9. Freeze analysis before scoring (9, 15).** Add to section 9: "11. Before any D3 caption or image is scored,
`analysis/EXP-001/` (Lift, bootstrap, Holm, classes, H-A, H-C) is run end-to-end on D0 pilot outputs with labels
scrambled, hashed, and its hash written into `runs/EXP-001/arms/manifest.json` with the hashes of all D3
token files. CLIP scoring of D3 runs once."

**R10. PC-A comparisons across different units (8.8).** Add: "Comparisons between cells with different units
(Ref-real and Ref-T2I over COCO items, J over seeds) use an unpaired bootstrap, resampling each cell
independently with its baseline recomputed."

**R11. Statement of error control (10.2).** Add: "Error control is per claim. H-B: FWER 0.05 by R3. H-A: one
conjunctive claim (H-A1 both directions and H-A2, intersection-union, one-sided 0.025 per ratio). H-C: one-sided
0.05. No Bonferroni across EXP-001 and EXP-002. The review also reports the claims that survive with every
level halved."

**R12. Dynamic-range gate (6).** Make precise: "Gate statistic = point estimate of Lift(J) on D0, k0, full
pipeline. If < 2.0 points, J (only) is regenerated on D0 under P' and the same statistic is recomputed. The primary
estimand is then 'DA - J at k0 under the condition the gate selects' (P or P'). The choice is logged before D1
starts." Add the operating characteristic: SE about 0.5-0.7 points at n = 64 [A], so a true Lift(J) of 2.5
fails the gate about 20 percent of the time.

## EXP-001 recommended changes (optional)

- O1. Decide the gate on the upper 80 percent bootstrap bound of Lift(J) rather than the point estimate. This
  lowers false "untestable" verdicts at the cost of occasionally running on a low-range checkpoint.
- O2. Report the primary contrast also as a share of the gap Lift(Ref-real) - Lift(J) (descriptive) so that
  readers can judge the ceiling.
- O3. Report, per arm, the fraction of captions truncated at 77 CLIP tokens. Add a guardrail: the truncation
  rate of DA within 5 percentage points of J's.
- O4. Define each guardrail on point estimates with an explicit statistic. For KID use the SD of the subset
  KID estimates (the KID protocol's own subsets) in place of "pilot SD".
- O5. PC-A: require Lift(Ref-real) > 0 and Lift(Ref-real) > Lift(J), each with an interval excluding 0. Make the
  Ref-T2I > J ordering descriptive. It is not a known effect, and as a hard gate it can stop the experiment for
  reasons unrelated to the endpoint.
- O6. Weak falsification of H-A1 over two directions is a disjunction. Use 97.5 percent upper limits, or state
  that P(false weak falsification) reaches about 0.05 when both ratios equal 1.5.
- O7. VQA secondary: use the same 250 seed indices in every arm so that VQA contrasts are paired.
- O8. Sensitivity for the primary: an arm-swap randomization test (swap DA and J samples within seed,
  recompute both baselines, 10,000 draws). It is exact under the sharp null that the pair is exchangeable,
  which is stronger than equal marginal laws. Report it, do not decide on it.

## EXP-001 power notes

- [C] 10.4 numbers verified (table in S4). The decision-rule table in R4 is the one to quote.
- [I] The sigma used for sizing must be the influence-based SD (R2). In the synthetic check the naive per-seed
  SD was about 16 percent low. If that holds on real data, the required n rises by about 35 percent: at
  sigma_L = 4 the Holm-level n of 505 becomes about 680, still within the 1000 cap.
- [C] H-A1: P(lower limit >= 1.5) at n = 128, 256, 512 for a true ratio of 1.75 is 0.690, 0.935, 0.998 per ratio.
  With two directions plus H-A2 required jointly, n = 128 gives roughly 0.69^3 = 0.33 if independent, which is why
  R7(a) fixes n = 256 (about 0.82).
- [I] H-C is likely underpowered. With 8 cells per stratum, and Delta noise of order 0.15-0.18 points against
  window effects that may be well under 1 point, P(rho_strat >= 0.5 and p <= 0.05) is low unless the spread of
  true Delta_w is at least about 3 SE. Stop rule 4 already makes H-C conditional; keep it conditional and accept
  "not tested at this budget" as the likely outcome.

---

# EXP-002 v0.1: value-rule decomposition at k >= 2

## Findings by check

**S1 unit, pairing, CRN.** The unit is the sample index s. All cells (arms, tau_lo and tau_hi, all k) share s,
and the bootstrap resamples s jointly for every cell (9.3). That is the right structure: it carries every
cross-cell correlation, positive or zero, into the interval, and Holm is valid under any dependence across k.
Y_s is one number per sequence (the mean NLL over 1023 predictions), so there is no within-sequence clustering
to handle. Two notes. (i) 5.5 keys `draw` as "N uniforms" per (s, step). If these are indexed by masked-row
order, the CRN alignment breaks as soon as arms' masked sets differ. Keying by absolute position keeps
uniforms aligned across arms and can raise cross-arm correlation materially (O2). (ii) The k = 1 block uses
s in [0, n), the same indices as stage B. Correlation through shared step-0 uniforms is negligible, but disjoint
pools are cleaner for gate data (O5).

**S2 single estimand; IR1-IR5; forking paths; entropy-curve geometry.**
- The confirmatory estimands are well defined: G_cp(k) for F1 and Delta2(k) for F2, each at the data-defined h*,
  which is frozen before any model output. Stage A uses entropies only, so calibration cannot leak Y. The IR
  branch is a function of stage-B entropies, which are computable from tokens without the evaluator. So the
  branch, the estimable set of k and each family's m can all be frozen before evaluation. The card does not
  yet say so (R6).
- **Slope differences are harmless; curvature differences are not.** [C] With A1 and A3 frontiers of
  different slope but equal value at h*, the paired percentile bootstrap rejects at 0.037 (nominal 0.05). With
  different curvature (kappa 0 vs 6 per nat^2) it rejects at 0.152, because linear interpolation across
  h* +- 0.05 has bias kappa (h* - E_lo)(E_hi - h*) = 0.015 per unit kappa difference of 6. For G_cp the two
  frontiers are expected to be close (A1 and A3 share positions and nearly the entropy, H4), so the risk is
  modest. For G_sh, G_tot and Delta2, which compare arms at very different tau, it is larger. IR8 does not
  check curvature (R8).
- **Calibration uncertainty.** Not propagating stage-A uncertainty is correct when the frontier is linear
  between the cells, as the card argues (7.3). With curvature, cell placement moves the bias, which is a further
  reason for R8.
- **IR4.** beta_A is a nuisance slope estimated from stage-A quality and treated as a constant. [C] At
  n_A = 64 and stage-A cells 0.15 nats apart, SE(beta_A) is about 0.41. At |h* - E_cell| = 0.05 this omits
  SD of about 0.02 from the interval, against a per-arm SE of about 0.01 at n_B = 1000. The selection of
  "local" cells is also unspecified (R5).
- **Arms that do not reach h*.** IR5 (NE) and the calibration gate (stop, regrid before stage B, entropy only)
  are the right handling and keep Y out of the decision. SF sharpens strongly (toy at k = 1: H 1.9 against 3.4
  [S, check_coupling_k2.log seed 0]), so A1 and A3 may need tau above 1.5 to reach a data-level entropy. That is
  a plausible regrid trigger. Reporting NE as a result is honest.
- **IR6** (flag at > 5 percent X/S replicates, NE at > 5 percent NE replicates): fine. Make the per-(arm, k)
  verdict part of the pre-evaluation freeze (R6).

**S3 multiplicity.** F1 (4 x G_cp, Holm, 0.025) and F2 (4 x Delta2, Holm, 0.025) with Bonferroni between them is
valid. The H1b gate is not: [C] testing H1b at the full 0.025 once F1 has any rejection gives an FWER over {F1, H1b}
of 0.036 when G_cp = (6, 0, 0, 6) SE units. The slope is truly 0 there and two F1 nulls are true (R3). The H2
interpretation table (section 2) reads G_sh classes, but G_sh is exploratory (9.4), so cells of that table cannot
be confirmatory statements (R10).

**S4 power and sample size.**
- **Derivation of 12.75.** n_B = ceil((z_{1 - alpha_F/(2m)} + z_{1-beta})^2 sigma^2 / delta^2) is the
  normal-approximation sample size for a two-sided test at the Bonferroni level alpha_F/m (Holm's first step,
  the worst case for any single true effect), with alpha_F = 0.025, m = 4 and power 1 - beta = 0.80:
  z_{1-0.003125} = 2.7344, z_{0.80} = 0.8416, (2.7344 + 0.8416)^2 = **12.788** [C]. The card's 12.75 uses z
  rounded to 2.73. m = 3, 2, 1 give 12.110, 11.151, 9.505. sigma is the SD of the per-sample influence values of
  the full G_cp estimator (SE = sigma / sqrt(n_B)), which is the right quantity because it contains all four
  cells and every cross-cell correlation.
- **Corrected illustrations** (m = 4): sigma_up = 0.25, 0.40, 0.60 give n_B = 889, 2274, 5116 (card 885, 2267,
  5100). The pilot bound factor is sqrt(31 / chi2_{0.20,31}) = sqrt(31 / 24.255) = 1.1305.
- **Plausibility of sigma_c** [C, analytic, components assumed]. By the delta method, the per-sample influence
  of Y(h*) for one arm is (1-w)(y_lo - beta h_lo) + w(y_hi - beta h_hi). The matched-entropy estimator is an
  entropy-adjusted mean, so sigma_psi^2 = sigma_y^2 + beta^2 sigma_h^2 - 2 beta rho_yh sigma_y sigma_h:

  | sigma_y | beta | sigma_h | rho_yh | rho_tau | rho_arm | sigma_psi | sigma_c | n_B (m = 4, sigma_up = 1.13 sigma_c) |
  |---|---|---|---|---|---|---|---|---|
  | 0.30 | 3 | 0.10 | 0.5 | 0.3 | 0.1 | 0.300 | 0.324 | 1913 |
  | 0.35 | 3 | 0.12 | 0.5 | 0.3 | 0.1 | 0.355 | 0.384 | 2680 |
  | 0.35 | 5 | 0.12 | 0.3 | 0.3 | 0.1 | 0.597 | 0.646 | 7575 |
  | 0.50 | 3 | 0.15 | 0.3 | 0.5 | 0.0 | 0.563 | 0.690 | 8649 |
  | 0.35 | 3 | 0.12 | 0.5 | 0.3 | 0.5 | 0.355 | 0.286 | 1489 |

  The synthetic IR simulation agrees with the formula's scale (implied sigma_c 0.41 for the second row's
  components, with bootstrap SE 0.0127 against a true SD of 0.0130 at n = 1000) [C]. [I] sigma_c is probably in
  0.3-0.7. At the card's [A] costs the stage B budget affords (45 of the proposed 60 GPU-hours, after about 15
  for the other stages) n_B = 1897 (R0), 3771 (R1), 9486 (R2) [C, card constants]. The ladder will most likely
  land on R1 or R2. delta_cp = 0.03 is resolvable at 80 percent power only if sigma_c is near or below 0.4.
- **Pilot is variance-only** (9.6, 9.7): yes, and the firewall is good. Two gaps. (i) The pilot cells
  (tau 0.9-1.1) may not bracket h* for A1 and A3, so the jackknife sigma_c would come from IR4 extrapolation.
  That estimator has a different variance from the stage-B IR1 estimator (no two-cell averaging, plus beta
  noise) (R4). (ii) No sigma is computed for Delta2, so F2's power is unstated. [C] At the n sized for F1, F2's
  power at delta = 0.05 is about 0.76 if arms are uncorrelated (Var(Delta2) about 3 x Var(G_cp)).
- **Sequential or fixed:** fixed. Keep 9.7.

**S5 intervals.** The resampling unit (s), B = 10,000, the percentile interval, the full estimator recomputed per
replicate (IR branches included) and the p-value formula are all appropriate. [C] In the synthetic check
(n = 1000, 600 replicates) the percentile p rejected at 0.052 under the null with equal frontiers. Add a Monte
Carlo precision rule near Holm thresholds (0.00625 for the first step): R9 below and O3.

**S6 stop rules, nulls, equivalence.** "Practically 0" is a TOST via the 97.5 percent interval, and "H1 negative"
needs it at every estimable k: a conjunction, so intersection-union at 95 percent would suffice. 97.5 percent is
valid but conservative. [C] At the sized n with G_cp = 0 at all k, P(H1 negative) = 0.448 (97.5 percent, 4 k)
against 0.639 (95 percent). At R2's own sized n (SE 0.0090, two k) it is 0.53 against 0.69 [hand computation from the same formulas]. The most likely outcome under a true zero
coupling at R0 is "H1 negative" by a small margin over "inconclusive". The card should say so (R2, O1).
"Underpowered gives MDE, not null" (11.2 and 14) is correct.

**S7 metric validity threats.**
- GenPPL evaluator bias: domain overlap (GPT-2 Large on WebText, MDLM on OWT) shifts absolute GenPPL and largely
  cancels in a paired contrast. The threat that does not cancel is evaluator-sampler alignment: SF commits
  tokens MDLM finds likely, and GPT-2 may share those preferences, so sharpened arms can score better at equal
  unigram entropy. The second-evaluator sign check (8.3) is the right control. Define "disagree" (O7).
- EOS: OWT packing puts EOS tokens inside generated 1024-token sequences, and GPT-2 then predicts across
  document boundaries. If arms differ in EOS rate this biases Y. Add a sensitivity with context reset at EOS
  (O8).
- Unigram entropy as the matching scalar: C3 and the 4-gram repetition guard are stated. The guard is a
  point-estimate rule. Fine as a qualifier.
- LLaDA 4-bit: every arm shares the same quantised weights, so contrasts are internally valid for that model.
  Transfer to the full-precision model is not claimed (13.5). The sanity gate (A5 within 10 points of the
  published figure on 40 train problems) is noisy: [I] SE of accuracy is about 0.07 at n = 40, p about 0.7, so a
  true match fails the gate about 17 percent of the time; train-split difficulty also differs from test (O9).
  13.4's first MDE: (1.96 + 0.8416) x 0.46 / sqrt(200) = 0.091, not 0.11 as stated (0.11 matches 90 percent power).
  Minor (O9).

**S8 what a reviewer would call p-hacked.** The card is strong here: data-defined h*, entropy-only calibration,
evaluator invoked once after all token files are hashed, no extension, ladder by variance and cost only, sign
registered and tested two-sided, downgrade-only guards. Remaining exposures: (i) the H1b gate (R3); (ii) H2
table cells stated from exploratory G_sh classes (R10); (iii) the decision rule's real probability at the MEI
(R2); (iv) no written rule that branches, estimable k and m are frozen before evaluation (R6); (v) N2 in its
current form forces either an evaluator call before stage B, which breaks 9.7, or a gate that fails at random
(R7).

## EXP-002 required changes (numbered; apply all)

**R1. Exact constants (9.6).** Replace "12.75" and "12.1" with values computed in code by
`scipy.stats.norm.ppf`: "constant(m) = (z_{1-0.025/(2m)} + z_{0.80})^2 = 12.788, 12.110, 11.151, 9.505 for
m = 4, 3, 2, 1". Correct the illustration to "n_B = 889, 2274, 5116".

**R2. Operating characteristics of the outcome classes (9.5).** Add the table [C, SE at the m = 4 sized n,
SE = 0.0084]:

| true G_cp | P(significant at the Bonferroni level) | P("clearly +/-") | P("practically 0"), 97.5% CI | same, 95% CI |
|---|---|---|---|---|
| 0.000 | 0.006 | 0.000 | 0.819 | 0.895 |
| 0.015 | 0.171 | 0.037 | 0.325 | 0.431 |
| 0.030 | 0.800 | 0.500 | 0.012 | 0.025 |
| 0.040 | 0.979 | 0.884 | 0.000 | 0.001 |
| 0.050 | 0.999 | 0.992 | 0.000 | 0.000 |

Then do one of: (a, recommended) redefine "clearly + / -" as "Holm-adjusted p below the family level (sign by
G)", with the qualifier "at or above delta" attached when |G| >= delta, so that H1 ("non-zero") is tested at the
stated power and the size qualifier is reported separately; or (b) keep the rule and state "P(clearly + | G_cp =
delta_cp) = 0.50; the design has 0.80 probability of a 'clearly' verdict only at G_cp of about 0.037". Also state
P(H1 negative | G_cp = 0 at all k) = 0.45 at R0 (0.53 at R2's sized n) under the current 97.5 percent rule.

**R3. H1b multiplicity (9.4).** Replace "H1b is tested at level 0.025 only if F1 rejects at least one
hypothesis" with: "H1b (slope of G_cp on log2 k, two-sided, sign rule as in 2) is a fifth member of F1, and Holm
runs over the five tests at 0.025." [C] FWER 0.025 for this option against 0.036 for the current rule. Alternative
(also valid): test H1b only if all estimable F1 hypotheses are rejected. Specify the slope estimator: "OLS of the
per-k G_cp estimates on log2 k with equal weights, recomputed in every bootstrap replicate over the estimable k
frozen under R6."

**R4. How sigma_c is computed in the pilot (9.6).** Add: "sigma_c = max(sigma_jack, sigma_delta). sigma_jack is
as written. sigma_delta is the delta-method value of the stage-B IR1 estimator at w = 0.5, computed from pilot
components:
sigma_delta^2 = 0.5 (1 + rho_tau) c' Sigma c, with Sigma_ab = rho_ab sigma_psi,a sigma_psi,b over arms
(A1, A2, A3), rho_aa = 1, and c = (-1, 0, 1) for G_cp, c = (-1, -1, 2) for Delta2;
sigma_psi,a^2 = sigma_y,a^2 + beta^2 sigma_h,a^2 - 2 beta rho_yh,a sigma_y,a sigma_h,a;
beta = the pilot slope dY/dE pooled over arms at that k; rho_tau = the correlation of psi between adjacent-tau
pilot cells of one arm at the same s (pooled over arms); rho_ab = the correlation of psi between arms a and b
in the same-tau pilot cells. Take the larger of k = 4 and k = 16, then sigma_up = sigma_c x 1.1305 as written."
The pilot also reports sigma_c for Delta2 by both routes and prints F2's achieved power next to F1's before the
ladder is chosen. Nothing in this computation prints a mean of Y or a contrast mean (9.7). Reason: if the pilot
cells do not bracket h* (likely for A1 and A3 at tau 0.9-1.1), the jackknife comes from IR4 extrapolation,
whose variance differs from that of the stage-B estimator. [C] The formula reproduces the analytic table in
S4 (row 2: sigma_c = 0.384), and the synthetic IR simulation agrees with it in scale.

**R5. IR4 slope, defined and propagated (7.4).** Replace the IR4 text after "beta_A" with: "beta_A = OLS slope
of the stage-A cell mean Y on cell mean E over the three stage-A cells of that (arm, k) whose E is closest to h*.
In every bootstrap replicate, stage-A samples are resampled independently (their own index set, stage-A seeds)
and beta_A is recomputed, so its uncertainty enters the interval. If the three cells span less than 0.10 nats of
E, the (arm, k) is NE." Reason [C]: an omitted SD of about 0.02 at 0.05 nats, against a per-arm SE of about 0.01.

**R6. Pre-evaluation freeze (9.7).** Add: "After all stage-B and k = 1 token files exist and before the evaluator
runs, `analysis/EXP-002/freeze.py` computes from entropies alone, and writes into `manifest.json` with hashes:
the IR branch of the point estimate for every (arm, k); the IR6 replicate shares of X, S and NE (these need only
entropies); the estimable set of k; m for F1 (including H1b) and F2; and the hashes of `interp.py`,
`bootstrap.py`, `placebo.py` and `genppl.py`. None of these can change after evaluation."

**R7. N2: split, resize, and resolve the firewall conflict (10, 11.1 item 4).** Currently N2 needs GenPPL of the
k = 1 block before stage B, while 9.7 forbids the evaluator before all stage-B files exist. At n_1 = 256 it also
passes an exact null with probability 0.46, 0.19, 0.00, 0.00 at sigma_y = 0.25, 0.30, 0.40, 0.50 [C].
Replace N2 by:
- "N2-H (gates stage B; no evaluator): TOST 90 percent interval of H(A1) - H(A3) inside +-0.03 at k = 1,
  tau = 1.0."
- "N2-Y (gates inference, evaluated with stage B in the single evaluation run): TOST 90 percent interval of
  Y(A1) - Y(A3) inside +-0.05. If it fails, F-control applies to all G_cp conclusions."
- "n_1 = min(1024, max(256, ceil(2 (1 - rho_hat) (z_0.95 + z_0.95)^2 max(sigma_up,Y^2 / 0.05^2,
  sigma_up,H^2 / 0.03^2)))) from the pilot. If the cap binds, the margins are widened to the values at which
  P(pass | exact null) = 0.90 at n_1 = 1024, and the achieved margins are stated."
[C] n_1 needed for P(pass) = 0.90 on Y: 542, 780, 1386, 2165 at sigma_y = 0.25-0.50; on H: 241, 542, 962 at
sigma_H = 0.10, 0.15, 0.20. P1 (entropy only) stays a pre-stage-B gate.

**R8. Curvature sensitivity with a flag rule (7.4 IR8).** Add IR8 (iv): "After evaluation, fit
Y = a + b (E - h*) + kappa (E - h*)^2 per (arm, k) to the stage-A cells with |E - h*| <= 0.3 (at least 4 cells).
The implied interpolation bias is kappa_hat (h* - E_lo)(E_hi - h*). If the bias difference between the two arms of
a confirmatory contrast exceeds delta/3 in absolute value (0.01 for G_cp, 0.017 for Delta2), that contrast is
flagged 'interpolation-sensitive' and its claim carries the flag." [C] Slope differences alone keep the level;
a curvature difference of 2 gives a rejection rate of 0.062 and of 6 gives 0.15-0.19. Design alternative (see O4):
bracket at h* +- 0.025, which cuts the bias fourfold at no variance cost while the cell gap stays well above
SE(E).

**R9. Placebo N4 definition (9.8, 10).** Specify: "The pass criterion applies to the rejection rate pooled over
all stage-B (arm, k) pairs (pass band [0.02, 0.09]). Each placebo uses a random pairing of the two halves'
indices and the paired bootstrap over pairs." [C] Applied per pair with all 12 required to pass, a valid test
passes only 0.876 of the time; pooled, it passes essentially always and still fails a test whose true level
is 0.10. Add the Monte Carlo precision rule: "if a confirmatory p is within 2 sqrt(p(1-p)/B) of its Holm
threshold, rerun that bootstrap with B = 100,000 and a fixed recorded seed."

**R10. H2 table status (2, 11.2).** Add: "F2's confirmatory content is the sign of Delta2(k) only. Rows of the
interpretation table that need a G_sh class (0, +, -) are exploratory, because G_sh is not in a confirmatory
family. Paper 1 words them as 'consistent with'." Alternative: add the four G_sh(k) tests to F2 (Holm, m = 8, 0.025).

**R11. Error-control statement.** Add to 9.4: "Error control is per experiment. No split with EXP-001. The review
also reports which claims survive with F1 and F2 at 0.0125."

**R12. Pilot output, tightened (9.6).** "Local slopes dY/dE" are printed pooled over arms (one slope per k), not
per arm. Per-arm slopes enter R4's computation without being printed. This removes the last arm-level quality
information from the pilot output.

## EXP-002 recommended changes (optional)

- O1. Use the 95 percent interval (intersection-union, no adjustment) for the conjunctive "H1 negative"
  verdict. P(H1 negative | G = 0) rises from 0.45 to 0.64 at R0 (0.53 to 0.69 at R2). Keep 97.5 percent for per-k "practically 0"
  statements in the H2 table.
- O2. Key `draw`, `prio`, `res` and `tilt` uniforms by (s, tag, step, absolute position), L per step. This raises
  cross-arm correlation (rho_arm in the sigma_c table: 0.1 to 0.5 cuts n_B from 2680 to 1489 in row 2 versus
  row 5). The pilot measures it.
- O3. Report BCa intervals and Wald intervals with the bootstrap SE as sensitivities for every confirmatory
  contrast.
- O4. Bracket h* +- 0.025 instead of +- 0.05. [I] The variance of the IR1 estimate at w = 0.5 does not depend on
  the gap while the gap is large against SE(E) (about 0.004-0.006 at n_B >= 1000 for sigma_h 0.12-0.2), and the
  curvature bias falls fourfold. The cost is more IR3 extrapolation flags if stage-A placement is off. Check the
  placement error from stage A before choosing.
- O5. Use a disjoint index pool for the k = 1 block.
- O6. H4 needs a test: "TOST 90 percent interval of H(A1) - H(A3) inside +-0.05 on the stage-A tau = 1.0 cells
  (n_A = 64), per k >= 2".
- O7. Second evaluator: "disagree" = point estimates of opposite sign. Report its interval too.
- O8. GenPPL sensitivity with the context reset at each EOS, and the EOS rate per arm.
- O9. LLaDA: raise the sanity-gate sample to 100 train problems or widen the margin to 15 points; correct 13.4's
  first MDE to 0.09 (80 percent power, two-sided 0.05) or say the figure is at 90 percent power; reword
  "if all intervals contain 0 and exceed the stated MDE" as "if an interval contains 0 and its half-width
  exceeds the MDE".
- O10. Interpret Delta2 as "coupling larger than sharpening" only when both G_cp and G_sh are classed +. Otherwise
  report |G_cp| - |G_sh| descriptively.
- O11. Define the "pooled-adjacent-violators mass" of P4 and the calibration gate: the sum over tau of
  |raw cell mean E - isotonic fit|, in nats.

## EXP-002 power notes

- [C] Constants and corrected n_B in R1. MDE at n_B = 1000 by sigma_c (80 percent power, worst-case Holm
  level): sigma_c 0.25 gives 0.028 (m = 4) to 0.024 (m = 1); 0.40 gives 0.045 to 0.039; 0.60 gives 0.068 to
  0.059.
- [C, card constants] Stage-B GPU-hours per unit n_B: R0 0.0237, R1 0.0119, R2 0.0047, R3 0.0018. At 45
  GPU-hours for stage B: n_B = 1897, 3771, 9486, 25042.
- [I] Expect the ladder to stop at R1 or R2 unless sigma_c <= 0.35. Under R2 (k in {8, 16}) the toy prior's only
  data point (k = 2) is not tested. That is acceptable because the toy prior does not transfer anyway (card,
  section header). Paper 1 must not describe the k-range as "k >= 2" in that case.
- [C] F2 power at delta = 0.05 at F1's n is about 0.76 with uncorrelated arms. R4 makes it pilot-based.
- [C] If sigma_c,up implies R3's MDE > 0.10 at the cap, stop rule 2 stops before stage A. At 25,042 affordable
  n_B (R3) that happens only if sigma_c,up exceeds about 5, so in practice stop rule 2 will not fire on variance
  alone.

---

## Note on what is NOT checked here
The A3 quadrature, the S_theta estimator's validity on a real network, and the arms' wiring are the red-team's
and lab-engineer's. Novelty is the novelty-auditor's. Every [A] component variance above is a placeholder that the
pilots replace. This review signs analysis plans, not results.
