# Stage-2 inventory, remasking and synergy strata (2026-10-13)

Saved by the orchestrator from the paper-reader's hand-back (the agent's own write of this file was
blocked). Data: `contrasts-remask-synergy.jsonl`, 423 rows, all 32 sampled papers. Evidence level
E1: only the extracts (abstract plus flagged tables) were read, so unflagged tables were not seen
and nothing was taken from figures.

## Counts by question

| Question | Rows | Matched | Poolable by rule | Variance reported | Papers with a poolable row | Families (poolable) |
|---|---|---|---|---|---|---|
| RQ4-steps | 28 | 24 | 24 | 1 | 5 | 16 (12) |
| RQ4-remask | 60 | 49 | 49 | 0 | 7 | 23 (12) |
| RQ4-other-inference | 265 | 254 | 254 | 19 | 13 | 64 (53) |
| RQ3-training | 33 | 28 | 28 | 12 | 7 | 23 (18) |
| RQ5-synergy | 17 | 15 | 15 | 0 | 4 | 11 (9) |
| RQ2-vs-AR | 6 | 0 | 0 | 0 | 0 | 3 (0) |

Of 377 rule-poolable rows, 348 (92 percent) report no variance. Only one table gives a defined
interval (AW0337 Table 8, five seeds, 95 percent t interval).

## Remasking: the outcome is shared, the contrast is not

Accuracy on GSM8K, MATH500, HumanEval or MBPP appears in 28 rows from 5 papers, but each paper
varies a different thing (on/off, threshold sweep, selection rule, verification design). **Only
AW0399 (Prism, arXiv 2602.01842, Table 4) is a clean remasking on/off contrast**; AW0391 Table 2
is arguably a second. A pooled "effect of remasking" would rest on one or two papers. The four
central remasking papers in the sample (AW0438 RemeDi, AW0372, AW0346, AW0382) report their main
comparisons only in figures, so this is probably an undercount of what exists but an accurate
count of what can be extracted as numbers.

Hand-check example: AW0399 Table 4, GSM8K, LLaDA-8B, K = 2, 4, 8. With SVF: no remasking 73.11,
73.41, 84.09 against full 74.24, 75.30, 85.30. Without SVF: neither 69.09, 69.39, 82.12 against
random pruning 70.68, 70.98, 81.59 (the K = 8 pair reverses sign).

## Synergy: four papers, mixed direction, no shared outcome

Of the 17 "synergy" papers, 9 are not unified understanding-and-generation papers at all (keyword
matches on "joint"). Of the 8 that are, 3 contain a real task-removal or shared-versus-decoupled
contrast (AW0255 Muddit, AW0252, AW0249), 1 is borderline (AW0248), 1 asserts synergy with only a
qualitative figure (AW0260), and 3 neither claim nor test it. Best overlap of outcome: GenEval in
2 papers. Direction in the printed numbers is mixed and none has an interval: AW0255 Table 4 joint
training gives GenEval 61.6 against 59.3 (higher), CIDEr 59.9 against 60.1 and VQAv2 68.2 against
69.1 (lower). The pooling threshold (8 contrasts, 5 groups) is not met.

## Why contrasts were not poolable (46 rows)

Figure only 34; cross-model leaderboard with no matched twin 7; match unverifiable 3; descriptive
statistic 2. Caveats on rows the rule passes: no variance (348), method comparisons that bundle
several changes (about 75), default chosen on the same table (about 29).

## Limits

Independence of research groups not assessed. Some tables recorded for a subset of columns. Task
or model inferred from matching numbers in a few cases, flagged per row.
