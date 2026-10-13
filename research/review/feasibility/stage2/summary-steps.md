# Stage-2 inventory, step-sweep stratum (2026-10-13)

Saved by the orchestrator from the paper-reader's hand-back (the agent's own write of this file was
blocked). Data: `contrasts-steps.jsonl`, 623 rows from 29 of 30 sampled papers (AW0031 has none).
Evidence level E2 for "the paper reports X" only. Rows are series (model x method x task x metric),
so row counts overstate independence: AW0077 alone gives 82 poolable step rows, AW0052 gives 38.

## Counts by question

| Question | Total | Matched | Poolable | Variance printed | Papers with rows | Papers with a poolable row |
|---|---|---|---|---|---|---|
| RQ4-steps | 317 | 290 | 206 | 32 | 17 | 9 |
| RQ4-remask | 13 | 10 | 9 | 1 | 6 | 2 |
| RQ4-other-inference | 215 | 184 | 178 | 27 | 18 | 11 |
| RQ3-training | 63 | 56 | 56 | 0 | 12 | 9 |
| RQ5-synergy | 3 | 3 | 3 | 0 | 2 | 2 |
| RQ2-vs-AR | 0 | 0 | 0 | 0 | 0 | 0 (not recorded, see limits) |

No table gives a defined standard deviation or interval. Two papers print a plus-minus or
"3 tests" without definition; everything else is a single run.

## RQ4-steps

- 206 poolable rows are about 100 distinct (paper, table, task, model) series from 9 papers:
  AW0045, AW0052, AW0074, AW0077, AW0239, AW0437, AW0441, AW0460, AW0461.
- Task families: language modelling 84 rows (generative perplexity or NLL), reasoning 48, code 22,
  other 52 (image, speech, JSON mode, runtime).
- The "step" axis is not one thing: step count in 7 papers, tokens unmasked per step in AW0441,
  an adaptive tolerance with realised forward passes in AW0460.
- Tokens revealed per step can be computed for 167 of 206 rows (8 papers).
- **Common outcome across 5 papers is borderline.** Loose reading (an accuracy-type metric on a
  reasoning or code benchmark): 5 papers, 62 rows. Strict reading (GSM8K accuracy against a free
  sweep of steps): 3 papers, 4 with GSM-Symbolic. The loose set mixes LLaDA and Dream variants,
  lengths of 128, 256 and 512, samplers, and three step axes. Independence of groups not checked.
- The mechanical "poolable" flag is generous: it includes runtime outcomes (AW0074), image metrics
  (AW0077), adaptive configurations chosen at equal quality (AW0460) and an upper bound over three
  tests (AW0045). The honest base for a steps synthesis in this sample is about 4 papers.

## Things found while reading that matter for the conjectures

- **Quality is not monotone in steps.** AW0437 (arXiv 2509.23924), Table 5, GSM8K, length 256,
  LLaDA-8B-Instruct, steps 1, 2, 4, 8, 16, 32, 64, 128, 256 give accuracy 3.11, 3.49, 3.94, 12.74,
  36.85, 42.46, 34.34, 34.87, 22.97. The peak is at 32 steps. AW0239 is also best at 32 and worse
  at 64. Any rule that interpolates "the fewest baseline steps reaching quality q" must define what
  it does on a non-monotone sweep.
- **A paper disagrees with itself.** AW0437 Table 1 labels values as S = 64 and 128 that Tables 4
  to 7 list at S = 128 and 256, for several series. This is the kind of claim-versus-table check
  the quality appraisal (QA8) is for.
- Second worked example for hand-checking: AW0461 (arXiv 2505.23061), Table 6, GSM-Symbolic,
  Dream-7B, length 128, steps 16, 32, 64, 128: unconstrained accuracy 6, 18, 28, 31.

## Why rows were not poolable (160 rows)

1. Only two levels: 95 rows. 2. Numbers only in a figure: 53 rows (no value was read off a
figure). 3. Not matched: 69 rows (several knobs change together, or reproduced and copied baseline
numbers are mixed). 4. Levels are not a free sweep (adaptive or multi-knob grids). 5. Outcome is a
cost or diagnostic, not a task metric.

## Limits

Method-against-baseline and model-against-model comparisons were not recorded (only each paper's
own sweep rows), so this pass says nothing yet about the slack conjecture H2 or about RQ2. Several
metric labels and model names are inferred and noted per row. One generation length is assumed.
