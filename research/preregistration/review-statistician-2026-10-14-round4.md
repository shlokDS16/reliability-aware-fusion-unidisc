```yaml
agent: statistician
date: 2026-10-14
brief: Signature round for EXP-001 v0.4. Checks (1) T1-T7 applied as intended, (2) recomputation of the new budget and n_conf arithmetic, (3) whether the new H-A source rule and its "source-limited" guard can bias the early/late ratio and whether the guard is adequate, (4) the declines in the change log.
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-001-crossmodal-unidisc.md v0.4 (change log v0.3-to-v0.4 lines 108-195; section 2 lines 308-336; 6 line 433; 7.4; 8.2-8.5; 8.7 G0 and G1; 10.3-10.5; 11; 12.1; 13 rows 667-672; 14 items 12 and 14)
  - research/preregistration/review-statistician-2026-10-14-round3.md (my T1-T7, r1-r8)
  - analysis/stats/round4_exp001_check.py and .log (written for this review)
coverage: >
  Read: the v0.4 change log in full and every card section it points to for T1-T7, r1-r8, the source rule, the guard, the
  budget and the declines. Not re-read: sections the change log marks as unchanged (1.3, 3, 5, 9, 15, appendices), PG-V
  criterion (d), the caption-end heuristic and PC-D' validity (the red-team's). No GPU used. No card or existing file
  edited. No ledger rows written.
claims:
  - statement: "Every v0.4 budget figure reproduces from the card's formulas: X = 193,978 / 207,546; 308,410 passes and 27.33 wall-clock hours at n = 596, t_b 0.129 s, duty 0.5; n_cap 826 (0.129 s), 1,000 (0.09 s), 593 (0.15 s), none at 0.17 s with wall(500) 33.67 h; n_conf 566 with the G5 fallback and P_rand regeneration; n_req 596 at sigma_d 5.66 (595 at 4 sqrt 2 = 5.657). Over a grid of t_b 0.05-0.40 s, five X and five n_req, the n_conf rule always returns a defined n >= 500 that is under 32 h whenever n_cap exists."
    status: supported
    evidence: analysis/stats/round4_exp001_check.log sections 1a, 1b
    level: E4 (recomputation)
    confidence: 0.97
  - statement: "Under the guard as written (label only when the early mean H_src is below half the late mean), a T->I dependence that is front-loaded relative to its source entropy (normalised ratio 1.75) is counted toward Negative with probability 0.52, 0.995, 0.73 and 0.14 at source-entropy drift h = 0.5, 0.6, 0.7 and 0.8. A rule keyed to R_Q2 counts it with probability 0.000 and still counts a true flat dependence (0.997-0.998)."
    status: supported
    evidence: round4_exp001_check.log section 2
    level: E4 (simulation; I proportional to H_src, cv 0.8, r 0.3 assumed)
    confidence: 0.8
  - statement: "Because the late probes pool only trajectories that still have a source, the pooled early/late ratio mixes populations. In a hardness model with late availability 0.5, it gives 1.28 or 2.81 for a true within-trajectory ratio of 1.75, and a false positive with probability 0.13 (nominal 0.025) for a true flat profile. The balanced panel recovers 1.74-1.76 and 1.00."
    status: supported
    evidence: round4_exp001_check.log section 3
    level: E4 (simulation; hardness model assumed, magnitudes illustrative)
    confidence: 0.7
competing_explanations:
  - "The magnitudes in claims 2 and 3 depend on assumed models (dependence proportional to source entropy; availability selected on hardness). The direction and the existence of the bias do not; D1 reports H_src, availability and mean w per probe and shows the real size."
unknowns: [late-probe source availability under conditions P and R; early/late H_src ratio; whether trajectories that keep a late source differ in dependence]
next_test: {hypothesis: "availability and H_src drift are small at k0", intervention: "D1 as registered (logs availability, H_src, w per probe)", primary_metric: "late availability; H_src early/late ratio; main minus balanced-panel ratio on D1", falsifier: "late availability below 0.8 or H_src ratio outside [0.8, 1.25]", gpu_hours: "none beyond the card"}
```

# Statistician review, round 4: EXP-001 v0.4 (signature round, pre-outcome)

Tags: [S] source fact with location; [I] inference; [C] computed here; [A] assumption. Nothing has run. Every number is a formula
result or an operating characteristic under stated assumptions.

Command (CPU, Python 3.14.3, numpy 2.4.2, scipy 1.17.1, about 40 s):

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python analysis/stats/round4_exp001_check.py > analysis/stats/round4_exp001_check.log

SHA-256: script e0b19110fa317f72b7fa649d62ccd587ccbd2686c17c8459864dd12218fc6d10,
log 688fa1a188e4ea16c26f5e686bd41d94b4d14c693b83be5db999ca9c97dd3850.

## Verdict

**Not signed yet: 2 minimal required changes (U1, U2).** Both are rules about how the H-A T->I statistic is read. Neither
needs GPU time, a new arm or a new threshold. T1-T7 are all applied as I intended. The budget arithmetic is correct. The
declines are acceptable. I sign v0.4 once a dated entry, or v0.5, shows U1 and U2 applied (either option of U2). Nothing
else is needed from me.

## (1) T1-T7 as applied

| Item | Applied as intended | Where checked |
|---|---|---|
| T1 class rule, mean w | yes, verbatim. For the H-A source a* the content class always has mass > 0.5. The committed-set price uses the total, so the term is always defined | 8.2 step 2, 8.5 |
| T2 G0 criterion | yes, verbatim, with the reason stated | 8.7 G0 |
| T3 G1b on D2 | yes. The D2 consequence can only remove a positive. Pilot drops happen before D2. "Not measurable" if both early or both late probes are dropped | 8.7 G1 |
| T4 labels | yes, in 2, 7.4 and 13. DA - TFJ is stricter than I asked (the red-team's R2-M5 also needs DA - TFJ inside (-1, 1)). This only removes claims, so fine | 7.4, 13 |
| T5 condition-R table | yes. (i)-(iii) in 2; stop rule 7's "reproduces the null" defined (11.7); 14 item 12 and log E.2 carry the round-3 figures; trace-size rule in 8.3 | 2, 8.3, 11.7, 14 |
| T6 n_cap | yes. (a) X realised and sized with the 128 trace; (b) defined fallback to 500 with the orchestrator before D1; (c) log E.1; (d) four-member figures in 10.4 | 10.4, 12.1, log D/E |
| T7 | yes; plus r5 (exact convolution p-value) | 10.3 |
| r1-r8 | all adopted as described | log B |

## (2) Recomputed arithmetic (log sections 1a, 1b)

| Quantity | Card | Recomputed [C] | Agreement |
|---|---|---|---|
| X, 64-trajectory trace / 128 | 193,978 / 207,546 | 193,977.6 / 207,545.6 | exact |
| Pilot probe and gate passes; stage 2 | 28,928; 35,072 | 28,928; 35,072 | exact |
| D1 | 33,792 | 16,384 + 8,192 + 9,216 = 33,792 | exact |
| n_req at planning sigma_d | 596 | 596 at sigma_d 5.66; 595 at 4 sqrt 2 = 5.657 (rounding only) | yes |
| Passes at n = 596, trace 64 | 308,410 | 308,410 | exact |
| Compute / wall at 0.129 s, duty 0.5 | 13.7 / 27.3 h | 13.66 / 27.33 h | yes |
| Trace 128 at 596 | 321,978; 14.2 / 28.3 h | 321,978; 14.15 / 28.30 h | yes |
| Wall at 0.09 s (64 / 128) | 20.6 / 21.3 h | 20.64 / 21.32 h | yes |
| n = 500 wall at 0.129 s (64 / 128) | 25.8 / 26.8 h | 25.78 / 26.75 h | yes |
| n_cap, plan, 0.129 / 0.09 / 0.15 s | 826 / 1,000 / 593 | 826 / 1,000 / 593 | exact |
| t_b = 0.17 s | none; wall(500) 33.7 h | none; 33.67 h | yes |
| G5 fallback + P_rand at 0.129 s | n_conf 566; 596 would take 32.5 h | 566 (wall 32.00 h) | exact |
| MDE at 596 | 0.82 | 0.816 | yes |
| "The rule always returns a defined n, floor 500" | stated | 0 violations over t_b 0.05-0.40 s x 5 X x 5 n_req (log 1b); n_cap ceases to exist at t_b 0.160 s (plan) and 0.134 s (G5 + P_rand) | **yes** |

Further values [C], not in the card: G5 fallback alone at 0.129 s gives n_cap 584; P_rand alone gives 807.

## (3) The H-A source rule: can it bias the early/late ratio, and is the guard adequate?

The rule (2): a* is the most confident still-masked tail position with index <= L_c that is not state-pad. It is a function
of the state, it is plan-independent, and L_c is frozen from the disjoint PG-V pool. None of it uses an outcome. That
closes R2-F1's construct problem. It leaves two ways the early/late ratio can move without any change in the model's
dependence.

**(a) Source entropy drift: the guard is too narrow.** [I] I(a*; b_j | s) <= H(a* | s). Early, the most confident non-pad
candidate is plausibly an easy token, such as a function word. Late, it is one of the remaining hard positions. Then
h = H_src(early)/H_src(late) < 1, and the raw ratio is roughly the normalised ratio times h. The guard fires only at h < 0.5.
[C] If the T->I dependence is front-loaded relative to its source entropy (normalised ratio 1.75, n = 256, cv 0.8 [A]), the raw
ratio is weakly falsified and counted toward Negative/Drop-P5 with probability 0.52 at h = 0.5, 0.995 at 0.6, 0.73 at 0.7, 0.14 at
0.8 and 0.01 at 0.9 (log 2). In this range the guard never fires, except about half the time at h = 0.5. A rule keyed to the
normalised statistic counts none of these (0.000), and it still counts a truly flat dependence (0.997-0.998). The card also
does not say what "R_Q2 is the statistic that is read" decides.
The opposite drift (h > 1) inflates raw positives. [C] At a flat normalised ratio, P(raw lower limit >= 1.5) = 0.51 at h = 1.75.
The existing wording rule covers this: "in nats, under confidence ranking", and "beyond the entropy available" only with
R_Q and R_Q2. No change is needed there.

**(b) Source availability: an uncontrolled selection.** [I] A probe with no source carries no weight. Early probes almost
always have a source. A late probe has one only if a non-pad position <= L_c is still masked, which under confidence ranking
means a hard position remains. The pooled ratio therefore compares early values over (nearly) all trajectories with late
values over a selected subset. This is a composition difference, not a within-trajectory change. [C] In a hardness model
[A] with late availability 0.5, a true within-trajectory ratio of 1.75 yields a pooled ratio of 1.28 if the trajectories that keep
a late source are the high-dependence ones, and 2.81 if they are the low-dependence ones. A truly flat profile yields
P(lower 95 percent >= 1.5) = 0.13 against the nominal 0.025. The balanced panel (trajectories with a source at all four probes)
recovers 1.74-1.76 and 1.00 (log 3). Availability is a state property, so a rule based on it uses no outcome. The same
selection exists for I->T, where the late J_T can be empty. I accepted that in round 3 as an estimand. With the new source it
matters for T->I as well, and the check costs nothing.

**Guard in stop rule 11.2.** Its logic is right (a source-limited failure is not counted as a negative), but the trigger is
too narrow (a) and it ignores (b). U1 and U2 fix both.

## (4) Declines (change log F)

| Decline | Assessment |
|---|---|
| Not editing the v0.2-v0.3 log in place; section E supersedes | Accepted. E.1-E.5 state the corrections correctly |
| R2-m3 second option | No statistical implication (red-team item) |
| R2-M1: m - s_sp reported, not a gate | Accepted. With 24 clusters and SE about 0.08-0.10 [A], a gate would mostly measure noise. The logged phrase "no measurable co-generation dependence at this rung (24 prefixes)" is worded as absence of evidence, which is correct |
| R2-M3: threshold 2.0 on the completion increment, not >= 1.0 | Accepted as a feasibility choice (no contrast, disjoint D0, so no error-rate effect). The stated reason, "equal to v0.3's gate on the Lift scale", does not hold, because the increment is a smaller quantity than Lift. [C] At SE 0.5-0.7 [A], P(gate fails) is 0.76-0.84 at a true increment of 1.5 and 0.16-0.24 at 2.5 (log 4). A failure leads to P_rand and possibly "H-B untestable". Recommendation v1: print this OC in 6 |
| R2-M6: 128-trajectory trace only when D1 shows it reaches 1.30 | Accepted. Decided from D1 (independent of the trace). X is already sized with 128, so the cap stays conservative |
| e3 (n_D2 up to 512) | Accepted, as in round 3 |

## Required changes

**U1. Source-limited reading keyed to R_Q2 (2, 11.2).** Replace the H_src half-mean trigger with: "A T->I weak falsification
(97.5 percent upper limit < 1.5) or reversal (upper limit < 1.0) of the raw ratio counts toward the Negative and Drop-P5 classes
of 11.7 only if R_Q2,T->I is also weakly falsified (or reversed) by the same limits. Otherwise the T->I part is labelled
'source-limited' and reported with both ratios and the early/late H_src ratio. R_Q2 never turns a raw failure into a positive.
The positive route stays the raw ratio, with the wording rules of 2." Reason [C]: with drift h in 0.5-0.8 the current trigger
counts a dependence that is front-loaded relative to its source as negative with probability 0.14-0.995.

**U2. Source and receiver availability (2, 10.3).** Report, per direction and per late probe, the share of trajectories with
a source (T->I) or with a non-empty J_T (I->T), together with H-A1 recomputed on the **balanced panel** (trajectories with a
source or a non-empty J_T at all four probes), with its 95 percent interval. Choose one:
(a) the H-A1 part in direction d is positive only if both the pooled and the balanced-panel lower limits are >= 1.5, and a
weak falsification counts toward Negative only if both upper limits are < 1.5 (an intersection-union test, no alpha spent,
power lower when availability is low); or
(b) the balanced-panel ratio is the H-A1 decision statistic, with the pooled ratio reported. The E4/r3 projection uses the
chosen statistic.
Reason [C]: in the hardness model with late availability 0.5, the pooled ratio is 1.28 or 2.81 for a true 1.75, and it gives a 0.13
false-positive rate for a flat profile.

## Recommendation (optional)
- v1. In 6, print the dynamic-range gate's OC on the increment: P(fail) 0.76-0.84 at a true increment of 1.5, 0.50 at 2.0 and
  0.16-0.24 at 2.5 (SE 0.5-0.7 [A]). Replace the reason "equal to v0.3's gate on the Lift scale" with the actual reason for 2.0.

## Not checked
Construct validity of the source rule (whether a* tracks "content"), the caption-end heuristic, PC-D', PG-V (d) and the
s_sp interval: these are the red-team's. Every [A] value is replaced by D0 or D1.

---

## v0.5 check (appended 2026-10-14; card at commit 4809632, diff against 7bce081; the text above is unchanged)

Read: the v0.4-to-v0.5 change log; section 2 (a)-(g) of the composition-standardised statistic; 10.3 H-A1 and the E4
paragraph; the dynamic-range gate in 6. Script: `analysis/stats/round5_exp001_check.py`, log `round5_exp001_check.log`
(SHA-256 script d7b47ac29da326e84bc741726651f9090b3a879f31ab9ff7745f0afa898504f1, log 059af17ddb428f58fbc1a2e95345366015b7dab62e93808bb9bda80c40ccb844; about 5 min on CPU; [A] model: 3 strata, early and late compositions that
differ, cv about 0.8, late sources missing at random).

**U1 and U2: applied.** (e) is my U2 option (a). (f) is U1, tightened so that a negative also needs both standardised ratios
to fail.

**Standardised estimator and bootstrap.** Direct standardisation with fixed pooled weights is correct. Holding omega_s at its
full-sample value inside the replicates is also correct: the weights define the target composition, so they are part of the
estimand, not noise. [C] Size at a true ratio of 1.5 is at most 0.027 for each member and at most 0.007 for the pair. Three
points are under-specified, and the card should fix them in text (V1):
(i) for I->T the stratum mean has to be taken over receiving positions (I_hat_j^c of the positions in stratum s), not over the
probe-level S-bar, which mixes strata;
(ii) the complete-case member must use the same full-sample weights, so that both members target the same composition;
(iii) nothing is said about a stratum with no early or no late observation, in the full sample or in a replicate (strata
with omega_s < 0.10 are not covered by the thin-strata rule). [C] At 20 or more observations a replicate is empty about 0.05
percent of the time.

**Coherence of the intersection-union read with U1.** Coherent. The positive needs both lower limits >= 1.5. The negative needs
both upper limits < 1.5 and R_Q2 failing. The two regions are disjoint, and everything else is inconclusive. One loose end:
10.3 still defines weak falsification as "the 97.5 percent upper limit of any of the three ratios < 1.5", and reversal
likewise. For the H-A1 parts these must point to (f) (V1 iv).

**Power.** [C] At a true ratio of 1.75 the pair's power equals that of the complete-case member: 0.78, 0.57 and 0.27 at late source
availability 1.0, 0.8 and 0.5, against 0.79, 0.78 and 0.62 for the pooled standardised ratio alone. At a true ratio of 2.0 it is
0.99, 0.99 and 0.77. The raw ratio has power 0 here because composition confounds it by construction. Under these assumptions
the pair costs nothing at full availability, and it falls to about a third of the pooled figure at availability 0.5; my round-4
figures (0.46-0.61 for the balanced panel) fall in the same range. D1's projection on the pair (10.3) is the figure to quote.

**V1 (minimal fix, text only).** Add to 2 (c)-(f): "For I->T the stratum means are over receiving positions; for T->I over
sources. Both members of the pair use the full-sample pooled weights. Before estimation, strata with omega_s < 0.10 are merged
into 'other content'. A bootstrap replicate in which a stratum is empty at the early or the late probes is redrawn, and the
share of redrawn replicates is reported. For the H-A1 parts, 'weak falsification' and 'reversed' in 10.3 and 11.7 mean the
rule of (f) at the limits 1.5 and 1.0."

**Verdict: SIGNED on condition that V1 is applied as stated.** V1 changes no threshold, arm or cost, so the card needs no
further statistical review.
