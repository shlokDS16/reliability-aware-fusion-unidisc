```yaml
agent: red-team
date: 2026-10-14
brief: Round 3 signature check of EXP-001 v0.4 against my round-2 findings (R2-F1, R2-M1..M6, R2-m1..m4), the designer's four declines, and the new risk the designer flags (the plan-independent T->I source may bias the early/late ratio in either direction). Problems only, minimal fix each; verdict sign or a minimal list of fixes.
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/review-red-team-2026-10-14-round2.md (my round 2, in full)
  - analysis/framework/redteam_exp_001_pgv_commoncause.py (header) and .log (in full)
  - research/preregistration/EXP-001-crossmodal-unidisc.md v0.4 at commit 7bce081 (lines 1-734, in full)
  - analysis/framework/redteam_exp_001_source_rule.py and .log (written for this round; CPU only, synthetic, no model)
coverage: >
  v0.4 read in full: YAML header, change logs v0.3-to-v0.4 (A-G) and v0.2-to-v0.3, sections 0-17, Appendices A-B. The
  v0.3 text was not diffed line by line; the closure judgments rest on the v0.4 text and its change log. Not read:
  runs/env-2026-10-14/setup.md (the smoke-sample debris string is quoted from my round-2 review, which quoted setup.md
  2.1 (a)), the statistician's round-3 review and its script, tools/gpu_guard.py, the novelty audit, any UniDisc code.
  Statistical decision rules owned by the statistician (T1-T7, n_conf, Holm) are not re-attacked. No GPU used; no
  existing file edited; no ledger rows written.
claims:
  - statement: "Under the v0.4 source rule (argmax max-marginal over still-masked, non-state-pad tail positions <= L_c), the candidate set shrinks from about L_c positions early to 1-3 late, so the early source is the most predictable content token and the late source is whatever remains; in a synthetic tail model the noun share of the source is 0.01-0.13 at passes 2 and 6 and 0.10-0.58 at passes 26 and 30, under both confidence ranking and random positions."
    status: supported
    evidence: analysis/framework/redteam_exp_001_source_rule.log Part 1 (24 configurations, n = 5,000 each)
    level: E4 (synthetic, assumptions in the script header)
    confidence: 0.7
  - statement: "In the same model the 'source-limited' label (early mean H_src below half of late) fires in 0 of 24 configurations (H_src early/late 0.53-0.91), while at a true per-source front-loading of 1.75 the raw T->I ratio is below 1.5 in 7 of 8 configurations (0.38-1.27); R_Q2 recovers 1.75 only when dependence per nat is the same for nouns and function words, and gives 0.65-0.71 when nouns carry more per nat (H-A2's own premise)."
    status: supported
    evidence: analysis/framework/redteam_exp_001_source_rule.log Parts 1 and 3
    level: E4 (synthetic)
    confidence: 0.7
  - statement: "Under condition R, the probability that any still-masked tail position with index <= L_c exists at pass 30 is at most 0.59, 0.77 and 0.89 for L_c = 8, 12, 16 (exact hypergeometric, ignoring state-pad)."
    status: supported
    evidence: analysis/framework/redteam_exp_001_source_rule.log Part 2
    level: E4 (exact computation)
    confidence: 0.95
  - statement: "The caption-end rule 4.1b does not end a caption at debris that follows the completion without a sentence terminator, which is the pattern of the only observed debris sample; such debris enters the scored caption and is not counted in the debris share or PG-V criterion (d)."
    status: supported
    evidence: card 4.1b (definition of e), 4.4 (d), 14 item 16; smoke-sample string as quoted in review-red-team-2026-10-14-round2.md R2-M2
    level: E3 (rule text inspected; no generation)
    confidence: 0.8
competing_explanations:
  - "for R3-F1: real dependence per nat may not differ between nouns and function words, and early marginals of positions 2..L may be diffuse (alignment uncertainty), making the noun slot the most confident early source; the composition shift would then reverse sign, which the one-sided label also does not guard"
unknowns:
  - the realised POS composition, H_src and w of a* at passes 2, 6, 26, 30 (computable on the 48 PG-V J trajectories at no extra GPU cost)
  - whether completions end with a terminator before any debris (computable on the PG-V samples)
  - the D0 SE of the completion increment (the dynamic-range OC is [A] in the card)
next_test: {hypothesis: "the T->I source composition is stable across the H-A probes", intervention: "compute a* at passes 2, 6, 26, 30 on the 48 PG-V J trajectories from the baseline marginals the sampler already computes; tag the final token at a* by POS", primary_metric: "noun share of a* early minus late, and h = mean H_src(early) / mean H_src(late)", falsifier: "|noun-share difference| < 0.1 and h in [0.85, 1.18] (then R3-F1 is moot on this checkpoint)", gpu_hours: "0 beyond PG-V"}
```

# Red-team review of EXP-001 v0.4, round 3 (signature check, pre-compute)

Tags: [S] source fact with location; [I] inference; [C] computed here (script and log named, CPU only); [A] assumption.
Nothing in this card has run. As in rounds 1 and 2, the brief asks for a minimal fix per finding and I give one.

Counts: **fatal 1, major 3, minor 4.** Verdict at the end: **not signed; sign after the four required fixes listed.**

Disclosure: the v0.4 source rule is the rule I proposed as the minimal fix for R2-F1 ("the still-masked text position
with the highest max-marginal among non-pad-class positions in the completion region"). R3-F1 below is a flaw in that
fix. The designer implemented it faithfully and flagged the risk (14 item 14); the fault is in the proposal.

## Part 1. Closure of the round-2 findings

| Round 2 | Status in v0.4 | Reason |
|---|---|---|
| R2-F1 source is the plan's committed token | **closed as stated; replaced by R3-F1** | Source no longer depends on the plan; w < 0.5 by construction removes the near-zero early term; 1.1 no longer links "concentrated early" to the DA windows; the registered falsifier (class of the committed token at passes 2, 6) is logged at PG-V. The replacement rule has its own construction bias (R3-F1) |
| R2-M1 PG-V common cause | closed | s_sp with a 90 percent cluster interval, cross-prefix derangements never pair equal prefixes, a logged line before D1. Decline of a gate criterion accepted (Part 2). Residual wording gap in R3-m3 |
| R2-M2 debris after the completion | **partly closed** | Caption-end rule 4.1b, debris share, criterion (d), untruncated sensitivity. The rule cannot see debris that follows the completion without a terminator, the pattern of the only observed sample (R3-M1) |
| R2-M3 dynamic-range gate | **partly closed** | Statistic now the completion increment, as asked. The threshold was raised to 2.0 with the P_rand fork as consequence, which turns a small-but-live range into "H-B untestable" (R3-M2) |
| R2-M4 completion-level positive control | closed | PC-D' at passes 1-2 on 16 trajectories, 10 x floor, failure before D1. Draw specification ambiguous (R3-m2) |
| R2-M5 TFJ wording | closed | 7.4 and 13 wording rule applied (95 percent, stricter than asked); Jd - J beside it. One residual overclaim in the top row of 13 (R3-m3) |
| R2-M6 condition-R precision | closed | Projection from D1, conditional 128-trajectory trace inside the sizing X, "not distinguishable" registered as the expected label otherwise. Projection is optimistic at pass 30 (R3-m1) |
| R2-m1 scope | closed | Scope sentence in 2; eligible share reported (3 item 8, 4.2) |
| R2-m2 OR-rule inflation | closed | Per-noun rates reported (4.4) |
| R2-m3 G1b fallback | closed | Same-side fallback only; decline of the re-reveal option accepted (Part 2) |
| R2-m4 increment length | closed | R-b read only as a contrast (7.1) |
| R2-F1, I->T analogue (reporting only in round 2) | **reopened as R3-M3** | Reported as asked, but with no decision consequence; in light of R3-F1 the same composition path to "Negative" exists for I->T and no guard covers it |

## Part 2. The designer's declines (change log F)

| Decline | Judgment | Reason |
|---|---|---|
| R2-M1: m - s_sp reported, not a gate criterion | **accepted** | My round-2 fix said it need not stop the run. Under conditional independence given the prefix m - s_sp has expectation 0 exactly (exchangeable seeds), so the reported interval is a valid test; 24 clusters give low power and PC-D' carries the H-A stop. Missing wording consequence for H-B is minor (R3-m3) |
| R2-M3: threshold 2.0 points instead of >= 1.0 | **not accepted** | "Stricter" is not safer here: a fail does not stop a dead endpoint, it switches the primary condition and, if repeated, declares H-B untestable. See R3-M2 |
| R2-m3: re-reveal under changed batch composition not applied | **accepted** | That option is G1a, already measured; the same-side fallback was the substantive fix |
| R2-M6: trace at 128 only if D1 shows it resolves <= 1.30 | **accepted** | It is one of the two options my fix offered; the 128 trace is already inside the sizing X, so the budget is safe either way. The projection's optimism is R3-m1 |

## Part 3. Findings on v0.4, ranked

### Fatal

**R3-F1. The plan-independent T->I source replaces one construction bias with another. Argmax over a candidate set that
shrinks from about L_c positions to 1-3 picks the most predictable content token early and whatever remains late, so the
early/late ratio compares source types, not times. The "source-limited" guard does not engage in the regime where this
matters, R_Q2 corrects entropy but not type, and condition R uses the same rule, so the path to "Negative" and "Drop P5"
of 11.7 is open as it was under R2-F1.** Location: 2 (T->I source, H-A1, H-A1-Q2, source-limited reading), 8.2 step 2,
8.3, 10.3, 11.2, 11.7, 14 item 14.
- Chain. (1) [S, card 2] a* = argmax of max_v p1_j(v) over still-masked, non-state-pad tail positions with index <= L_c.
  At passes 2 and 6 almost all L_c positions are candidates; at k0 one text token is committed per pass, so at passes 26
  and 30 only 7 and 3 text positions are masked, of which typically 1-3 are candidates. (2) [I] A maximum over many
  candidates is the most predictable token in the window, a function word, article or punctuation in a caption; a
  maximum over the few leftovers is the leftover itself. This is an order-statistic property of the rule, not of the
  sampler, so it holds under confidence ranking and under random positions. (3) [I] H-A2's own premise is that nouns
  carry more image information per nat than function words. If so, the early T->I term is computed from low-information
  sources and the late term from high-information ones, whatever the model's dependence does over time.
- [C] `redteam_exp_001_source_rule.log`, synthetic tail model, all assumptions in the script header (L_c = 12; noun slot
  plus 25 percent nouns; uncertain pad mass at the caption boundary; I_c = (1 - w) kappa H_content of the source):
  - Noun share of a*: 0.01-0.13 at passes 2 and 6, 0.10-0.58 at passes 26 and 30 (confidence ranking) and 0.15-0.37
    (random positions), across 24 configurations including marginals that sharpen as the image is committed.
  - H_src(early) / H_src(late) = 0.53-0.91. The label (threshold 0.5) **fires in 0 of 24 configurations.**
  - At a true per-source front-loading of 1.75 (every source's dependence 1.75 times higher early), the raw T->I ratio is
    **0.42, 0.38, 0.64, 0.49** with noun-heavier dependence per nat ("typed"), and **1.12, 0.93, 1.59, 1.27** with equal
    dependence per nat ("flat") (rows: static P, static R, sharpen P, sharpen R). 7 of 8 point estimates are below 1.5,
    the weak-falsification region of 10.3, with no label.
  - R_Q2 returns exactly 1.75 in the "flat" rows and **0.65-0.71** in the "typed" rows: it corrects the entropy of the
    source, not its type.
  - Part 3 (arithmetic): if the term scales with H_src, raw = rho_true x h. The label fires only for h < 0.5; for
    rho_true = 1.75 any h in [0.50, 0.857) gives raw in [0.88, 1.50) with no label. The threshold 0.5 sits below the
    range the order statistic produces.
- The decision path. Raw T->I weak falsification (97.5 percent upper limit < 1.5) with no label is "Negative" in 11.7.
  Condition R uses the identical source rule (2, 6), so its ratio carries the same composition shift (synthetic raw 0.38
  and 0.49 typed, 0.93 and 1.27 flat at a true 1.75) and its 97.5 percent upper limit can also fall below 1.5. With a
  null H-B that is "Drop P5 from the open problems", the outcome R2-F1 was rated fatal for. Where the label does fire, 11.2
  says the result does not count "until R_Q2 has been read" and defines nothing after that: no threshold (1.0 or 1.5) and
  no class. The guard is also one-sided: if early marginals at positions 2..L are diffuse (alignment uncertainty) and the
  noun slot is the most confident early candidate, the shift reverses, inflating a positive "in nats" claim, and nothing
  guards that direction.
- Why fatal and not major: identical structure to R2-F1 (a definitional property of the source rule biases the H-A1 T->I
  ratio and feeds the stop rule that removes P5), the guard the card offers does not engage at the magnitudes the rule
  produces, and the independent check (condition R) shares the rule. The fix is a rule change with no GPU cost.
- What forces rejection of this finding: on the 48 PG-V J trajectories (or on D1), the noun share of a* at passes 2 and
  6 differs from that at passes 26 and 30 by less than 0.1 in absolute value **and** h lies in [0.85, 1.18].
- Minimal fix (cost-neutral, frozen before PG-V because the logging runs there):
  1. Log for a* at every H-A probe of PG-V J, D1 and D2: tail index, final decoded token, its POS on the final caption
     (noun or not, 4.1b typing), post-caption flag, w, H_src. Report the early and late noun shares and h with D0.
  2. Replace the one-sided label with a two-sided **composition guard** per direction: if h is outside [0.85, 1.18]
     (1.5 / 1.75 and its reciprocal) or the early-minus-late noun share of a* differs by more than 0.2, the T->I H-A1
     ratio is "source-composition-limited": reported with R_Q2 and the noun / non-noun split, but it cannot be positive,
     weakly falsified or reversed, and in 11.7 it counts as "inconclusive" (keep P5 open), never as "Negative" or toward
     "Drop P5". This removes the undefined "until R_Q2 has been read" clause.
  3. In 11.7 "condition R reproduces the null" counts only for a direction whose condition-R trace also passes the
     composition guard.

### Major

**R3-M1. The caption-end rule cannot see debris that follows the completion without a sentence terminator, which is the
pattern of the only observed debris sample. Such debris is scored as caption, the debris share reads 0, PG-V (d)
passes, and 14 item 16's claim that "a caption that is mostly debris is a PG-V (d) failure" is false for it.** Location:
4.1b, 4.4 (d), 2 (L_c), 7.1, 14 item 16.
- [S, card 4.1b] e = min(e0, e1, 33), with e1 the first terminator (".", "!", "?", newline) after the first alphanumeric
  token. [S, card 3 item 1c, and setup.md 2.1 (a) as quoted in my round-2 R2-M2] after "a photo of a red bicycle leaning
  against a brick wall" (no terminator) the free tail read "(c) photoshiko shui copyright (c) 1 2 3 / 02 a / 12 3 / 15 a"
  (no terminator; "(", ")", "/" and digits are not terminators). Under the prefix task the analogous output "bicycle
  leaning against a brick wall (c) photoshiko ..." has e = e0 or 33: the whole string is the completion.
- Consequences [I]: (i) CLIP lift and V-lift score the watermark channel again (X1-F1) on exactly the samples where it is
  present; the untruncated sensitivity is then identical to the primary and shows nothing. (ii) Debris share = 0 and (d)
  passes, so (d) measures only debris that is already truncated, the harmless part. (iii) Completion length becomes up to
  32, so L_c = 16 (the cap), and a* can land on formulaic debris tokens, which are confident and non-pad: the T->I H-A
  source would then measure the image's dependence on watermark text, and R2-F1's logged falsifier (the plan's committed
  token) would not show it. (iv) Debris positions inside the "caption" are I->T receivers and are typed for H-A2.
- What forces rejection: on the PG-V J samples, no completion contains a token from the debris pattern set below before
  its caption end.
- Minimal fix: add e2 = the smallest index i > f whose decoded piece contains "(", ")", "©", "/", "|", "@", "http", "www"
  or ".com", equals "copyright" or "stock", or is digits only; e = min(e0, e1, e2, 33). PG-V reports the share of
  samples ended by e2. Correct 14 item 16 accordingly. The list is frozen before PG-V with the other lists (Appendix B).

**R3-M2. Gating the completion increment at 2.0 points with the P_rand fork as consequence turns a live but small
movable range into a condition switch or "H-B untestable", and the remedy does not target the trigger.** Location: 6
(dynamic-range gate), change log F, 10.5.
- The gate exists to catch a dead completion (round 2: "can no longer detect a dead endpoint"). P_rand is the right
  remedy for a dead completion caused by deterministic confidence ranking. It is not a remedy for a completion that is
  alive but adds 1-2 points over a prefix that carries most of the CLIP content: P_rand does not change what the prefix
  contributes.
- [C, from the card's own [A] SE of 0.5-0.7 points at n = 64, normal approximation] true increment 1.5 (1.5 MEI):
  P(fail) = 0.76-0.84 under P; the same truth under P_rand fails again with similar probability, so "H-B declared
  untestable" has probability of roughly 0.6-0.8 (higher if the two estimates are correlated, as they share prefixes).
  True increment 2.0: the primary condition is a coin flip between P and P_rand (P(fail) = 0.5). The card's OC line is
  "[A, not re-derived for the increment]".
- What forces rejection: the D0 increment estimate of J is above 3.0 points with SE <= 0.5 (then 2.0 is never close).
- Minimal fix: fork threshold 1.0 point (the MEI: below it no MEI-sized contrast is possible, above it the completion is
  live). Keep 2.0 as a reporting flag only: "movable range below 2 MEI; the primary is sized against at least half of
  it".

**R3-M3. The I->T source is still the plan's committed image set, its composition shifts with the same order-statistic
logic, and nothing guards it; the claim sentence implies both directions are plan-independent.** Location: 1.1, 0, 2
(H-A1-Q2: for I->T H_src is "an upper bound, so min is H(mbar_j) in practice"), 8.1.
- [S, card 2] For I->T, R_Q2 reduces to R_Q, so the "source side" normalisation does nothing; the mean marginal entropy
  per committed code is reported (my round-2 request) but has no decision consequence. [I] Early, the 32 committed codes
  are the most confident of about 1,000 (plausibly uniform background); late, the most confident of about 100-220
  leftovers. H-A1 needs both directions, so an I->T weak falsification from source composition is "Negative" in 11.7.
- [S, card 1.1] "(H-A, measured from a source that does not depend on the commit plan)" covers both directions; only
  T->I is plan-independent (section 0 says so correctly).
- What forces rejection: the mean per-code marginal entropy of the committed image set at passes 2 and 6 is within
  [0.85, 1.18] of that at passes 26 and 30 on D1.
- Minimal fix: apply R3-F1's composition guard to I->T with h = the ratio of mean per-code marginal entropy of the
  committed image set (early over late), same band, same "inconclusive" routing in 11.7. Change 1.1 to "T->I measured
  from a plan-independent source".

### Minor

**R3-m1. The condition-R size projection overstates late-probe precision.** [C] Part 2 of the log: under random
positions the chance that any tail position <= L_c is still masked at pass 30 is at most 0.59 (L_c 8), 0.77 (12), 0.89
(16), before the state-pad exclusion (0.65 in the synthetic model at L_c 12). D1 runs under confidence ranking, where
hard completion positions stay masked late, so its availability is higher. Fix: in the 8.3 projection, thin the
resampled late-probe trajectories by the hypergeometric availability for the frozen L_c.

**R3-m2. PC-D' draw specification is ambiguous and the control is weak.** "R = 8 draws from its content-class marginal
(stratified as in 8.2 when the pad class has mass >= 1e-6)" reads as both 8 content draws and 4 + 4. Also, at passes
1-2 with the image fully masked, revealing the noun slot will clear 10 x a bf16 floor almost surely; PC-D' rules out
only a dead task, and it uses a different source from a*. Fix: state "8 content-class draws, within-content term";
state in 8.8 that PC-D' is a liveness check, not a test of a*.

**R3-m3. Two wording gaps in section 13.** (a) Top row: "by avoiding T->I co-commitment (DA - TFJ positive) rather than
by showing text earlier". A positive DA - TFJ shows a benefit beyond text-earlier; it does not show text-earlier
contributes nothing (TFJ - J may also be positive). Fix: "beyond showing text earlier". (b) No row for a logged "no
measurable co-generation dependence" (m - s_sp lower limit <= 0) together with a positive H-B1: the mechanism wording
of the top row would then be unsupported. Fix: one row, "positive schedule effect without measurable co-generation
dependence at PG-V; mechanism not claimed".

**R3-m4. max_v p1_j(v) is taken over the whole text vocabulary, pad ids included.** A position with w just below 0.5
has max-marginal up to about 0.5 from its pad mass alone and can win; its content weight 1 - w is then only just above
0.5 and its content class is "what if the caption continued here". In the synthetic model such boundary positions are
0.04-0.20 of early sources and up to 0.59 at pass 30 (log Part 1, boundary_share). Fix: take the max over the content
class (ids not in P) for the source rule; report the boundary share with the R3-F1 log.

## Part 4. Answers to the brief

- **Is each R2 item closed?** Table in Part 1: R2-F1 closed as stated but replaced by R3-F1; R2-M2 and R2-M3 partly
  closed; all others closed; the I->T analogue of R2-F1 reopened as R3-M3.
- **Declines.** R2-M1 non-gate, R2-m3 re-reveal and the conditional 128 trace are accepted. The 2.0-point gate is not
  (R3-M2).
- **Does R_Q2, the "source-limited" label and guard 11.2 handle the new source-rule risk?** No. In the synthetic model the
  label never fires (h 0.53-0.91 against a 0.5 threshold), the raw ratio at a true 1.75 falls to 0.38-1.27 in 7 of 8
  configurations, R_Q2 corrects only when dependence per nat does not depend on token type (contrary to H-A2), 11.2
  leaves the post-R_Q2 decision undefined, the guard is one-sided, and condition R shares the rule so it cannot
  disconfirm the artefact. These results rest on a synthetic tail model; the falsifier in R3-F1 settles it on PG-V data
  at no GPU cost.

## Verdict: **not signed; sign after four required fixes**

Required, none needs GPU or changes the budget:
1. R3-F1: a* logging (tail index, token, POS, post-caption flag, w, H_src) at PG-V, D1 and D2; two-sided composition guard
   (h in [0.85, 1.18], noun-share difference <= 0.2) replacing the 0.5 label, with "inconclusive" routing in 11.7; the
   condition-R "reproduces the null" clause conditional on the same guard. Frozen before PG-V.
2. R3-M1: e2 debris pattern in the caption-end rule; e2 share reported at PG-V; 14 item 16 corrected. Frozen before
   PG-V.
3. R3-M2: dynamic-range fork at 1.0 point; 2.0 as a reporting flag. Before D0 analysis.
4. R3-M3: the composition guard for I->T on per-code entropy; 1.1 wording. Before D2.

Minors R3-m1 to R3-m4 can go in the same version. Once 1-4 are in, the red-team signs without another full round; a
check of the changed paragraphs is enough.

## Script and log written for this round (CPU only, no GPU, no model)
`analysis/framework/redteam_exp_001_source_rule.py` -> `.log`, run with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 <repo-root>/.venv/Scripts/python.exe analysis/framework/redteam_exp_001_source_rule.py`
(about 28 s).
