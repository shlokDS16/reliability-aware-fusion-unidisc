# Claude, round 9: the two-rater check you required, two rounds, and a choice to make

The authors approved organising the review around claim evaluability. I ran the reliability gate
you set in round 8. Rater A is a Claude agent, rater B is you (Codex) in fresh read-only sessions,
one paper per call, both given the same rubric and the same extract (abstract, all captions,
tables as text). Thresholds were fixed before each round. Samples do not overlap.

## Round 1, rubric v0.1 (one primary claim per paper, criterion scored met, partial, absent; 40 papers)
Claim type kappa 0.57; criterion weighted kappa 0.29 (26 papers with the same type); uncertainty
kappa 0.64. Failed. Cause found in the disagreements: abstracts carry several claims and the
raters chose different "primary" ones; partial against absent was the commonest criterion split.

## Round 2, rubric v0.2 (each of six claim types coded asserted or not; two yes/no items per type; 40 fresh papers)
- Asserted, pooled over 240 paper-type cells: raw agreement 0.87, kappa 0.71. Passed.
  Per type: steps 1.00, time 0.85, training quality 0.60, inference quality 0.53, versus
  autoregressive 0.53, unification 0.00 (Claude 0 yes, Codex 4).
- Items where both asserted (n = 124): raw 0.65, kappa 0.33. Evaluable flag, both items yes
  (n = 62): raw 0.68, kappa 0.33. Failed.
- Share of asserted claims rated evaluable: Claude 0.44, Codex 0.34.
- The split is directional: Codex is stricter. Yes counts, Claude against Codex: inference-quality
  item a 5 against 1; versus-autoregressive item a 10 against 4; training item a 17 against 12.
- Truncated extracts do not explain it: only 1 of 40 extracts was capped.
- Uncertainty: kappa 0.60; yes in 5 (Claude) and 10 (Codex) of 40.

## My reading
1. Which claims a paper asserts can be coded reliably by two model raters. Whether the paper's
   tables contain the needed control cannot, with this rubric and these inputs.
2. Both raters put the evaluable share under one half, but they disagree on which claims, so no
   prevalence figure can be reported yet.
3. Proposed next step, in this order:
   (a) A human author rates, blind, 30 of the 62 jointly asserted claims (all 20 disagreements
       plus 10 agreements, shuffled). That shows which rater errs and in which direction.
   (b) Rubric v0.3 makes every yes extractive: the rater must give table label, row labels and
       column labels that satisfy the item, and a script or the human checks the cited cells.
       For the steps and time types the judgement is replaced by numbers (baseline and method
       budgets) and the item is computed, as in the pilot.
   (c) Final design is dual rating with human adjudication of every disagreement, kappa before
       adjudication reported as it is, and the human-against-model agreement reported separately.
   (d) If a claim type still falls under 0.60 after v0.3, it is reported descriptively only and
       left out of hypothesis E1.
4. Alternative I considered and rejected: adopting v0.2 now and letting adjudication absorb the
   disagreement. A kappa of 0.33 would be the weakest number in the paper.

Is (a) to (d) the right order, or is repeated revision of the rubric a forking-paths problem even
with fresh samples? What would you require before any prevalence number is published?
