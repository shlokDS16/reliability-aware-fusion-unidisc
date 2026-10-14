# Reliability of the claim-evaluability rubric: development rounds (2026-10-14)

Raters: A = Claude agent (sonnet), B = Codex (GPT) in fresh read-only sessions, one paper per call
(`codex-log.jsonl` in each round folder holds time, session and prompt hash). Both saw the same
rubric and the same extract (abstract, all captions, tables as text). Samples are fixed-seed,
stratified by README section and do not overlap. Thresholds were set before each round. Both
rounds are **rubric development**, not confirmatory evidence.

| | Round 1, rubric v0.1 | Round 2, rubric v0.2 |
|---|---|---|
| Design | one primary claim per paper; criterion met, partial, absent | six claim types each asserted or not; two yes/no items per type |
| Claim identification | type kappa 0.57 (raw 0.65) | asserted kappa **0.71** (raw 0.87), pooled over 240 cells |
| Criterion | weighted kappa 0.29 (n = 26) | items kappa 0.33 (n = 124); evaluable flag kappa **0.33** (n = 62) |
| Uncertainty reported | kappa 0.64 | kappa 0.60 |
| Verdict against the 0.60 line | failed | claim identification passed, criterion failed |

Round 2 by type, `asserted` kappa: steps 1.00, time 0.85, training quality 0.60, inference quality
0.53, versus autoregressive 0.53, unification 0.00 (Claude 0 yes, Codex 4). Evaluable agreement
where both asserted: steps 3 of 5, time 12 of 17, inference quality 3 of 5, training 13 of 20,
versus autoregressive 11 of 15.

Share of jointly asserted claims rated evaluable: Claude 0.44, Codex 0.34. This is a pilot signal
and not a prevalence estimate, because the raters disagree on which claims are evaluable.

## What the disagreements show
- Round 1: the raters often chose different claims from the same abstract. Fixed in v0.2.
- Round 2: Codex is systematically stricter (yes counts, Claude against Codex: inference-quality
  item a 5 against 1; versus-autoregressive item a 10 against 4; training item a 17 against 12).
- Truncated extracts are not the cause: 1 of 40 extracts was capped.
- Rater A's notes on wording: whether several baselines at one step count each satisfy "a baseline
  at two or more counts"; whether "competitive" asserts a quality gain; whether a speed advantage
  over autoregressive models asserts a claim against them; where pruning, safety and robustness
  methods belong; what "main results table" means when there are several.

## Agreed next steps (debate rounds 9 and 10)
1. A human author rates `round2/human-adjudication.csv` blind: 30 jointly asserted claims (all 20
   disagreements and 10 agreements, shuffled, no model answers shown). A second human rater on the
   same sheet would let human agreement be reported.
2. Rubric v0.3: every yes must cite table label, rows and columns; for the steps and time types
   the budgets are extracted as numbers and the item is computed by script. Wording fixes above.
3. v0.3 and its scoring rules are frozen, then validated on a fresh sample, blind to earlier
   rounds. Prevalence is published only for claim types that reach the preset reliability line;
   other types are reported descriptively and left out of hypothesis E1.
4. Final audit: dual rating, human adjudication of every disagreement, kappa before adjudication
   reported as measured.
