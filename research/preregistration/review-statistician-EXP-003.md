```yaml
agent: statistician
date: 2026-10-15
brief: One-round statistical review of preregistration card EXP-003 v0.1 (value-rule share of joint text-image consistency, UniDisc 1.4B).
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-003-value-rule-consistency.md (in full, v0.1)
  - runs/EXP-001/gates/verdict-pgv-rung2.json (n_samples 48, 294 nouns, m-s_sp -0.0208, 90 percent cluster interval [-0.125, 0.083], per-noun matched 0.350 / same-prefix 0.279 / cross 0.213)
  - analysis/stats/exp003_check.py and analysis/stats/exp003_check.log (written by this review; synthetic data only)
coverage: >
  Card read in full. Numbers in sections 4, 5, 6, 7 recomputed analytically and by simulation. NOT read: EXP-001 card, any
  EXP-001 per-sample data (not stored), UniDisc code, the decision ledger beyond what the card quotes. The simulation uses
  invented generative parameters (presence logits, discordant counts); it checks the estimator and the bootstrap, not the model.
claims:
  - statement: "Card arithmetic is correct: SE 0.0367, power 0.777 at true 0.10, P(null class | true 0) 0.718, P(null | 0.05) 0.381, n 213 for power 0.90 at sigma_d 0.45."
    status: supported
    evidence: analysis/stats/exp003_check.log (first block)
    level: E4
    confidence: 0.95
  - statement: "The ratio-of-sums statistic Lambda_d is unbiased in simulation (bias at most 0.002) and the percentile cluster bootstrap behaves acceptably at 150 prefixes even when G has 1 discordant noun per sample (90 percent coverage 0.885 to 0.897; 2-sided size at nominal 0.05 is 0.055 to 0.068; Monte Carlo SE about 0.011 to 0.016)."
    status: supported
    evidence: analysis/stats/exp003_check.log (simulation block; 400 replicates, B = 1000)
    level: E4 (synthetic)
    confidence: 0.7
  - statement: "sigma_d = 0.45 is a defensible planning value, but it has no empirical basis for this statistic and the power statements are conditional on it."
    status: mixed
    evidence: simulation sd of the paired per-prefix influence value 0.32 (4 discordant nouns per sample in both arms), 0.39 (2 vs 4), 0.52 (1 vs 3); card section 7
    level: E4 (synthetic)
    confidence: 0.6
  - statement: "As written, the card can produce an unfounded headline: a null on Delta1 (a difference of two links) is worded in section 10 as an absence of a link in G."
    status: supported
    evidence: card section 5 (null class defined on Delta1) against section 10 row 'Null Delta1'
    level: E2 (card text)
    confidence: 0.9
competing_explanations: []
unknowns: [actual discordant-noun counts per arm (the dominant driver of sigma_d); whether G's lower diversity shrinks them; true size of Lambda_d under P64]
next_test: {hypothesis: n/a, intervention: none, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Statistician review of EXP-003 v0.1

## Verdict

**NOT SIGNED. Eight minimal changes (below); with them the design is acceptable and I would sign on sight of v0.2.** Nothing here needs a new experiment. Items 1, 2, 3 and 5 are the ones that can produce a claim wider than the data; the rest are precision fixes.

## What I checked, and the answers to the designer's five questions

1. **sigma_d = 0.45 and n = 150.** Arithmetic is right (SE 0.0367; power 0.777 at true 0.10; n for 0.90 power is 213). The 0.30 per-arm SD is an assumption ("assumed to be about 0.30"): the 0.19 to 0.31 values come from the OR-rule m - s_sp, a per-sample binary statistic, not from a per-noun ratio. The EXP-001 gate (294 nouns in 48 samples, about 6 per sample) shows many noun instances per sample, which supports the planning value for plain sampling. My simulation (150 prefixes, two seeds, 1 to 4 discordant nouns per sample, image-level random effect) gives a paired SD of 0.32, 0.39 and 0.52 for (4 vs 4), (2 vs 4) and (1 vs 3) discordant nouns per sample in (G, P64). So 0.45 is inside the plausible range, and the dominant unknown is how many discordant nouns G leaves. Power at true 0.10 across sigma_d: 0.35 gives 0.94; 0.45 gives 0.78; 0.55 gives 0.61; 0.65 gives 0.47. P(null class | true 0) at sigma_d 0.55 is 0.44 and at 0.65 is 0.19. The statement "power 0.78" must therefore be printed as conditional on sigma_d = 0.45, with that sensitivity row. Stop rule 9.3 (stop only if the achieved MDE exceeds 0.20) is too lax: MDE 0.20 corresponds to sigma_d of about 0.87 and power about 0.3 at the MEI (change 5).
2. **Lambda_d as a ratio of sums, estimability.** Unbiased and well calibrated in simulation (above); the zero-denominator redraw is irrelevant at n of 120 to 150. Few discordant nouns costs precision, not validity: at 1 discordant noun per sample in G, P(null class | true 0) falls to 0.55 and P(reject | true 0.10) to 0.64 (log, row 'G very sparse'). That is a risk of an inconclusive result, which the card handles. The unhandled risk is interpretive (change 4): a null among the few nouns on which the two seeds differ is a statement about those nouns.
3. **Holm pair.** The fixed-sequence gate (Delta1 at 0.05, then Holm over {Delta2a, Delta2b} at 0.05) controls the family-wise error rate; keep it. Gaps: the hypotheses are stated as "at least +0.10" but tested against 0 (change 2); "null class at their Holm-adjusted levels" is undefined (change 6); the attribution rule W4 reads non-significance as absence (change 3).
4. **Null class at 90 percent.** Correct and not "looser": a 90 percent interval inside the margin is exactly two one-sided tests at 5 percent (TOST); a 95 percent interval would be TOST at 2.5 percent and would cut P(null | true 0) from 0.72 to roughly 0.5 at sigma_d 0.45. Keep 90 percent. Two caveats: the percentile interval's empirical size was 0.055 to 0.068 against 0.05, so require the BCa interval to agree before a null label (change 6); and the margin 0.10 is larger than the whole per-noun matched-minus-same-prefix gap seen in EXP-001 (0.04 and 0.07), so "null" cannot exclude a link as large as anything EXP-001 observed (change 1). A p-value or an equivalence test says nothing about practical importance or novelty; the margin is a choice (card says so) and the paper must carry it.
5. **Matched calls (G 65 vs P64 64) as primary.** Acceptable and fixed before data, provided it is described correctly. The card's claim that it makes "a null the stronger null" is wrong: if P64 itself carries a link (finer schedule), G - P64 can be null while G has a link; it is a stronger statement only about G exceeding a strong plain sampler (change 1). The exact identity Delta1 = Delta2a + Delta2b + (P32 - P64) is correct and reported, good.

## Required changes (minimal)

1. **Null wording versus null definition (section 5, section 10, 1.1).** The null class is on Delta1 = Lambda_d(G) - Lambda_d(P64). The Paper 1 sentence "Guidance does not create a completion-specific link ... within (-0.10, 0.10), not co-generation" is a claim about Lambda_d(G) itself. Either (a) restate it as "G does not differ from P64 by more than 0.10", or (b) add as a condition for that sentence that the 90 percent intervals of Lambda_d(G) and of Lambda_d(P64) both lie inside (-0.10, +0.10). Same for the positive row, "plain sampling at the same number of network calls does not": needs Lambda_d(P64) null or a count of its interval, not just Delta1 positive. Delete "(a null is) the stronger null" in section 2 point (2). State beside the margin that 0.10 exceeds the EXP-001 all-noun gap (0.04 to 0.07), so the paper's null reads "no link larger than 0.10 on the presence scale".
2. **Hypothesis versus test (section 5).** E3-H1, H2a, H2b are written "Delta >= +0.10" but tested two-sided against 0 and classed "positive" at p <= 0.05. Rewrite: tested against 0; the MEI is the power target and the equivalence margin; "at or above the MEI" is a point-estimate descriptor only (P(d >= 0.10 | true 0.10) is 0.50), never worded as "shown to be at least 0.10".
3. **Attribution wording (W4, section 10 row 1).** "Delta2b not positive" must read "not detected" unless Delta2b is itself in the null class; Holm second-step power at 0.10 is 0.68. "Accounts for the difference" is wrong unless Delta2a is close to Delta1: use "G minus O0 is positive (d, interval)" and report the three terms of the identity, including P32 - P64; no share-of-effect statement.
4. **Scope of any null (new wording rule W5).** Any null or "no link" statement carries the per-arm counts of discordant nouns and prefixes with at least one, and is worded "among nouns that one seed names and the other does not". If G's discordant count is below the guardrail (iii) 0.4 times P64's, the null is labelled "sparse" and, under W2, "not measurable" is available.
5. **Sample size and stop rule (section 7, 9.3).** (a) Print the power and P(null) statements as conditional on sigma_d = 0.45, with the sensitivity row (sigma_d 0.35, 0.45, 0.55, 0.65 gives power 0.94, 0.78, 0.61, 0.47). (b) Tighten 9.3 to an achieved MDE at 80 percent power above 0.15 (sigma_d,up about 0.66), or state in the card that for MDE between 0.10 and 0.20 the main stage runs and "inconclusive" is the expected outcome for a true effect near 0.10. (c) The pilot rule uses a chi-square factor for 16 clusters; add "the pilot SD is of the paired difference G minus P64 (covariance included), not the single-arm SD times sqrt 2", and note the factor assumes roughly normal influence values, which sparse counts violate.
6. **Equivalence mechanics (section 5, 7).** Define the null class for Delta2a and Delta2b: the unadjusted 90 percent interval, with the sentence that no family-wise claim is made about the Delta2 nulls (Holm governs only the "positive" and "reversed" classes). For all three contrasts, a null label additionally requires the BCa 90 percent interval to lie inside (-0.10, +0.10) (the card's sensitivity BCa becomes binding for nulls only). Reason: empirical size of the percentile interval 0.055 to 0.068.
7. **NC-1 pass rule (section 6).** "Interval contains 0" is passed by an imprecise control: at 48 clusters a bias of the size of the MEI is not excluded. Pass = 95 percent interval contains 0 and its half-width is at most 0.10. Add a sentence that NC-1 is run on plain-sampler images, so a bias specific to guided images is not controlled by it; this goes into W2's text.
8. **Reporting.** Add to the descriptive list the 95 percent intervals of Lambda_d for each arm separately (needed by change 1), and report the number of bootstrap redraws and B for each p-value near a threshold, as already planned.

## Not required but noted

- PC-1 as a gate has pass probability 0.75 at a true TF effect of 0.15 (I recomputed: SE 0.065, bar max(0.10, 0.107)); a 25 percent chance of downgrading every null to "not measurable" is a cost of the design, accepted.
- The Delta2a and Delta2b power assumes zero correlation between arms; positive correlation through shared prefixes only helps.
- Percentile bootstrap, B = 10,000, shared prefix indices across arms, and the R5 p-value rule are sound; no change.
- Simulation is synthetic (invented presence model) and covers only the estimator and the interval; it supports no statement about UniDisc. Seeded script: `analysis/stats/exp003_check.py`; log: `analysis/stats/exp003_check.log` (about 20 s on CPU).

## Signature

Statistician: **unsigned**, pending v0.2 with changes 1 to 8 (items 1 to 3, 5 and 6 are blocking; 4, 7 and 8 are wording/definition additions).

---

# v0.2 check (2026-10-15)

Read: card v0.2 (`git diff 01dabdb`, commits a0073e1, 8accefe). Simulation: `python analysis/stats/exp003_check.py v2` (log `analysis/stats/exp003_check_v2.log`; synthetic data, 150 prefixes, 300 replicates, B = 1000, seeded; Monte Carlo SE of a rate near 0.05 is about 0.013). It does not describe UniDisc; discordant counts are the driver and are unknown.

## (1) Does Lambda_b cancel additive image-level bias; is the cluster bootstrap right?

- **Cancellation: yes, exactly for additive bias, in expectation given the noun sets.** For an eligible prefix the two sides contribute (link + b0 - b1)/2 and (link + b1 - b0)/2; the noun-specific base rates cancel within each side because the same noun is scored on both images. Simulation of the red-team F-1 toy (seed noun count scales with the seed's image yes-bias, true link 0, bias on the logit scale, heterogeneous nouns): the instance-weighted Lambda_d, absolute, is +0.062 (coupling 1.0) and +0.129 (coupling 2.0), consistent with their +0.07 to +0.18; Lambda_b is -0.002 and 0.000. The Delta1 contrast cancels the Lambda_d bias only if both arms are coupled equally; G and P64 need not be, so keeping Lambda_b primary is right.
- **Residual: non-additive bias** (yes-rate interacting with noun class) is not cancelled; NC-2 is the right idea. Caveat: placebo nouns (nouns of another prefix, absent from both completions) have near-zero presence rates, so their slope under a logit-type bias is small and NC-2 under-detects a bias acting on real, plausible nouns. Report the placebo noun presence rate per arm beside Lambda_b^plac (not blocking).
- **Bootstrap.** Resampling prefixes with the eligibility flag carried inside each replicate (numerator sum over eligible, count of eligible recomputed) is the correct cluster scheme; the mean over eligible prefixes is a ratio estimator and was unbiased in simulation (bias at most 0.006). Percentile size at nominal 0.05: 0.043 to 0.067 in ordinary cases; 0.107 with 90 percent coverage 0.853 under extreme coupling 2.0 (coverage 0.86 at coupling 1.0, arm A only). Mildly anti-conservative; see fix 3.
- **Estimand sets.** The arm contrast uses prefixes eligible in both arms, so the pairwise sets differ between Delta1, Delta2a and Delta2b. The identity of 4.2 then holds exactly only on a common set; the card still says "exactly" (line 146). See fix 2.

## (2) Efficiency against Lambda_d (n = 150 prefixes; power at true Delta1 0.10, P(null) at true 0)

| scenario (discordant nouns per seed, G / P64) | excluded share | SE Lambda_b | SE Lambda_d | power Lambda_b | power Lambda_d | P(null) Lambda_b | P(null) Lambda_d |
|---|---|---|---|---|---|---|---|
| Poisson 4 / 4 | 0.07 | 0.029 | 0.025 | 0.93 | 0.95 | 0.93 | 0.98 |
| Poisson 2 / 4 | 0.28 | 0.040 | 0.031 | 0.74 | 0.92 | 0.65 | 0.89 |
| Poisson 1 / 3 | 0.64 | 0.059 to 0.066 | 0.039 to 0.046 | 0.33 | 0.68 | 0.06 | 0.60 |
| negative binomial (size 1.5) 3 / 3 | 0.57 | 0.049 to 0.052 | 0.030 to 0.031 | 0.56 | 0.93 | 0.29 | 0.89 |
| negative binomial (size 1.5) 1.5 / 3 | 0.73 | 0.071 to 0.072 | 0.037 to 0.040 | 0.31 | 0.76 | 0.02 | 0.71 |

Lambda_b costs a factor 1.2 to 1.8 in standard error, almost all through excluded prefixes (the price of cancelling the bias). The card's planning value (SE 0.0367, power 0.78, P(null | 0) 0.72) corresponds to about 2.5 Poisson discordant nouns per seed (sigma 0.45 on 150 prefixes); overdispersed counts, which real 0-to-32-token completions with 6 percent empty ones will be, give 0.64 to 0.87. **Expected excluded share: 10 to 30 percent if G keeps about 2 or more discordant nouns per seed; 55 to 75 percent if counts are 1 to 3 and overdispersed.** The empty-completion rate (0.06 in EXP-001) and G's expected lower diversity push toward the upper range. The pilot will show it, and the card's rule must use it (fix 1).

## (3) Do the null and wording changes meet my items 1 to 8?

- 1 null wording: met in sections 5 and 10 (per-arm 90 percent intervals, margin note, diversity floor, NC-2). Not met in one place: line 121 still reads "a null is the stronger null" (fix 4).
- 2 hypotheses tested against 0: met. 3 W4: met. 4 W5: met; add "eligible prefixes" to its scope sentence (fix 1). 6 null mechanics: met. 7 NC-1: met. 8 per-arm intervals: met.
- 5 sample size: partly. The conditional sentence is there, but the operating characteristics (SE 0.0367, MDE 0.119) are still the Lambda_d numbers, and 9.3 and n_req ignore eligibility. The pilot SD of the paired difference (5c) is met.

## Verdict: NOT YET SIGNED. Four minimal fixes, then SIGNED on a one-line confirmation, no new round

1. **Eligibility in the sample-size rule (section 7, 9.3, pilot firewall).** SE of Delta1 is sigma_el / sqrt(n x s), with s the share of prefixes eligible in both arms and sigma_el the SD of the paired L_p(G) - L_p(P64) over eligible prefixes. n_req, the MDE in 9.3 and the pilot output use s (the pilot already reports a share) and apply the 1.21 factor to sigma_el. Replace the stale "SE 0.0367 / MDE 0.119" by: valid only if the eligible prefixes carry sigma_el = 0.45 (about 2.5 Poisson discordant nouns per seed); simulated range SE 0.029 to 0.072, power at the MEI 0.93 to 0.31. Add to W5 "among prefixes in which both seeds have such nouns".
2. **Identity and sets (4.1, 4.2).** State that arm contrasts use the prefixes eligible in both arms and per-arm headline intervals each arm's own eligible set. Report the identity Delta1 = Delta2a + Delta2b + (P32 - P64) on the prefixes eligible in all four arms (descriptive) and drop "exactly" for the pairwise sets.
3. **Positive and reversed classes (section 5, W4).** A "positive" or "reversed" label also requires the BCa 95 percent interval to exclude 0 (the null class already requires BCa agreement); percentile size reached 0.07 to 0.11 in the coupled toys.
4. **Delete "and a null is the stronger null" (line 121).** Replace by: "a null of G minus P64 is a statement about the difference only; absolute statements follow section 10".

A p-value or an equivalence result still says nothing about practical importance; the 0.10 margin is a choice and larger than the EXP-001 gap, as the card now states.

Statistician: **unsigned until fixes 1 to 4 appear in v0.3.**
