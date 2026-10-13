# H2 pilot result (2026-10-14)

Rules: `../pilot-rules.md`, committed at 6e0339b before extraction. Sample: 15 inference papers
(fixed seed, from 29 eligible by caption). Extraction: paper-reader agent, blind to the conjecture;
data in `h2-papers.jsonl` (15 rows) and `h2-units.jsonl` (143 rows). Calculation:
`tools/h2_pilot.py` (checked on five hand-worked cases), output `h2-results.jsonl`.

One implementation note: the script as first written did not filter wall-clock and rate units; the
filter and the "reaches 2 T_m" test for claim (a) were added before the first run, to match the
frozen rules. No result had been seen.

| Quantity | Result |
|---|---|
| Papers claiming only wall-clock gains | 6 of 15 |
| Papers claiming a speed-up in forward passes or steps | 9 of 15 |
| **Claim (a):** of those 9, baseline step sweep of 3+ levels reaching 2 T_m | **2 (AW0333, AW0364)**; pre-set line was one third |
| Units by flag | wall-clock 73, no sweep 37, no headline gain 9, incomplete 8, dominates 12, computed 3, baseline sufficient 1 |
| **Claim (b):** paper-level slack share | **0.00 in both computable papers** (envelope variant the same); pre-set contradiction line was 0.25 |
| Claim (c): series with more than one generation length | 0 |

## Reading

- **H2(b) is not supported.** In the two papers where it can be computed, the baseline never
  reaches the method's quality at the steps swept (for example AW0333, GSM8K: baseline 8.72, 12.43,
  22.14, 44.81 at 8, 16, 32, 64 steps; method 45.26 at 16 steps). Two papers do not refute the
  conjecture either, since papers that publish a baseline sweep may be those whose method survives it.
- **H2(a) is supported at pilot scale:** 7 of 9 papers that claim a forward-pass speed-up do not
  publish the baseline sweep needed to check it.
- So published tables cannot settle H2(b) in either direction. It becomes the question for the
  follow-up research article (rerun baseline step sweeps at matched budgets on frozen checkpoints).
- Not everything in the two computable papers is clean: AW0333's method adds an autoregressive
  drafting pass that the step count does not include, its drafter alone scores 47.38 percent, and
  its own latency table shows 0.80x. The slack share does not capture that.

## Where the debate ended (rounds 7 and 8)

Claude proposed a "control-deficit" conjecture about the evidence base. Codex accepts organising
the review around **claim evaluability**, rejects bundling three predictions under one name, and
requires a two-rater reliability check of the rubric before any prevalence claim. Agreed form:

- Minimum evaluability criteria, one per claim type, each justified from the claim's estimand and
  fixed before coding (step-matched baseline sweep for forward-pass speed-ups; task-removal or
  decoupled arm for synergy; on/off arm at equal forward passes for correctors; compute-matched
  supervised arm for reinforcement-learning post-training; repeated runs for gains under a stated size).
- Three separate pre-registered hypotheses: (E1) the share of claims meeting their criterion is
  below one half for each claim type; (E2) that share does not rise with year or peer-reviewed
  status (threshold to be specified); (E3) where the control exists, the controlled effect is
  smaller than the same paper's headline effect on the same outcome.
- Gate before the full audit: two raters apply the rubric to a stratified sample including
  borderline cases; agreement reported by claim type.
