# Claude, round 7: the table-level pilot you asked for, and what it does to H2

## What was done
Rules for the slack share were frozen and committed (interpolation in log T, first crossing on
non-monotone sweeps with an envelope variant, tolerance, edge cases, support and contradiction
thresholds) before any pilot table was read. A fixed-seed sample of 15 inference papers was
extracted by an agent that was not told the conjecture. A script computed everything.

## Results (15 papers, 143 extracted units)
- 6 papers claim only wall-clock gains; 9 claim a speed-up in forward passes or steps.
- Claim (a): of those 9, only 2 give a baseline step sweep of 3 or more levels reaching down to
  twice the method's own budget. 2 of 9 is below the pre-set one-third line.
- Claim (b): the slack share is computable in those 2 papers only, and it is 0.00 in both. In 12
  units the baseline never reaches the method's quality at any swept step count; 3 units are
  interpolated; 1 has the baseline sufficient at the method's budget. Example: baseline GSM8K
  accuracy 8.72, 12.43, 22.14, 44.81 at 8, 16, 32, 64 steps against the method's 45.26 at 16 steps.
  By the pre-set rule this contradicts (b), on n = 2.
- Claim (c): no paper varies generation length within a computable series.
- Stage-2 reading of 62 other papers: 92 percent of matched contrasts in one batch report no
  variance; a clean remasking on/off contrast exists in 1 to 2 papers; a real task-removal or
  shared-versus-decoupled contrast exists in 3 to 4 of the 8 unified multimodal papers sampled.
- Novelty audit: H2 novel at confidence 0.55 (closest: arXiv 2609.33947); H5 incremental
  (arXiv 2606.29228 already reports cross-study discrepancy for one cell).

## My reading
1. H2(b), "most reported acceleration is slack", is not supported and I withdraw it as a claim of
   the review. Two papers cannot refute it either: papers that publish a baseline sweep are
   plausibly the ones whose method survives it. Published tables cannot settle it in either
   direction, because 7 of 9 papers omit the comparison that would.
2. What the pilot does show is the omission itself. So I propose a different organising result,
   stated as a conjecture about the evidence base, not about the models:
   **Control-deficit conjecture.** For each major claim type in this literature there is one
   within-paper control without which the claim cannot be checked from the paper: a step-matched
   baseline sweep for a forward-pass speed-up; a task-removal or decoupled-pathway arm for
   synergy; an on/off arm at equal forward passes for remasking and other correctors; a
   compute-matched supervised arm for reinforcement-learning post-training; repeated runs for any
   gain under a stated size. Conjecture: (i) the share of claims that come with their required
   control is below one half for every claim type; (ii) the share does not rise with publication
   year or with peer-reviewed status; (iii) where the control is present, the claimed effect is
   smaller in the controlled comparison than in the headline comparison of the same paper.
3. (i) and (ii) are testable on the whole corpus with the quality appraisal the professor asked
   for, with two independent raters and agreement reported. (iii) is a within-paper paired
   comparison. None needs cross-paper pooling of scores.
4. The follow-up research article then supplies one missing control experimentally: baseline step
   sweeps at matched budgets on frozen checkpoints, which tests H2(b) properly.

Attack this. In particular: is "required control" definable without circularity, is (iii) just
regression to the mean or selective reporting, and is this a conjecture or merely an audit?
