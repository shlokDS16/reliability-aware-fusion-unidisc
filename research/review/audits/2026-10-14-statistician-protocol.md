# Statistician review of protocol sections 4 to 7 (2026-10-14)

Saved by the orchestrator from the statistician agent's hand-back. Numbers were recomputed by the
agent: `analysis/reliability/round2_intervals.py`, output `round2_output.txt` (seed 20261014,
10,000 paper-cluster bootstrap resamples, percentile intervals).

## 1. Round-2 agreement with intervals (40 papers)
| Quantity | Estimate | 95% interval |
|---|---|---|
| Kappa, asserted, pooled over 240 cells | 0.71 | 0.59 to 0.81 |
| Kappa, evaluable flag, 62 jointly asserted claims | 0.33 | 0.03 to 0.59 |
| Asserted kappa by type: time | 0.85 | 0.66 to 1.00 |
| training quality | 0.60 | 0.37 to 0.83 |
| inference quality | 0.53 | 0.14 to 0.83 |
| versus autoregressive | 0.53 | 0.31 to 0.75 |
| steps | 1.00 | degenerate (5 claims) |
| unification | 0.00 | not meaningful (0 against 4) |
| Evaluable share, Claude | 0.44 | 0.30 to 0.57 |
| Evaluable share, Codex | 0.34 | 0.21 to 0.48 |
| Paired difference (bias) | 0.10 | -0.05 to 0.24; McNemar exact p = 0.26 |
| PABAK | 0.35 | 0.06 to 0.63 |

Reading: "criterion failed" is supported. "Claim identification passed" is **not established**:
the lower bound is 0.59. Per-type rows cannot support pass or fail. The strictness gap between
raters is suggestive, not shown. Prevalence is not what deflates kappa; the disagreement is real.

## 2. Clustering
Pooling cells within a paper violates independence (design effect about 1.35 to 1.42). Use the
paper-level cluster bootstrap; in the full corpus cluster on research group. The unweighted mean
of per-type kappas is 0.59 against the pooled 0.71; the estimand must be named.

## 3. Sample size
To show a lower bound above 0.60 when true kappa is 0.75: about 170 to 210 independent claims for
80 percent power; with clustering about 250 claims, roughly **160 papers**. No feasible round can
establish per-type reliability for steps or inference quality (5 jointly asserted claims per 40
papers). **The 30 human-rated claims cannot establish kappa, prevalence or human-human
reliability**: they are enriched for disagreements, use rubric v0.2 and come from the development
set. They can only show which rater the human tends to side with.

## 4. Prevalence with imperfect raters
Design-based two-phase estimator: strata from dual ratings (both evaluable, both not, discordant);
a human rates all discordant claims plus random subsamples of the agreement strata; weighted
estimate with Jeffreys interval and cluster inflation. A second human on about 20 percent.
For 300 claims in a type: about 97 discordant plus 19 to 35 agreement claims to rate by hand.

## 5. Hypotheses
- **E1**: testable per type only where claims are plentiful (about 206 to 275 for versus
  autoregressive, time and training quality in a 550-paper corpus; about 69 for steps and
  inference quality; none for unification). Needs Holm correction or a stated conjunction rule.
  80 percent power against 0.50 needs 63 claims if the true share is 0.30, 259 at 0.40, 725 at 0.44.
- **E2**: both clauses are equivalence or non-inferiority claims; a non-significant trend is not
  evidence. Needs about 300 claims per group; year and peer-review status are confounded; margin
  arbitrary. Feasible only pooled.
- **E3**: not testable as written (terms undefined), and biased by selection: headline numbers are
  best cases, so "smaller under control" is expected with no confounding at all. Treat as
  descriptive unless 70 or more qualifying papers exist.

## 6. Wording that promises more than the analysis delivers
Protocol section 6 still describes rubric v0.1; "pre-registered" is used though nothing is
registered and thresholds are unspecified; gates act on point estimates; "verified" for a 10
percent extraction check; section 7's pooling rule, heterogeneity statistics at 8 contrasts,
standardisation and verdict labels are not operationalised. Pilot wording should be counts only:
2 of 9 has interval 0.03 to 0.60 and spans both the support and the contradiction line; "not
supported" rests on 2 papers.
