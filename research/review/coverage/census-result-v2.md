# Census of value rules and reporting, result v2: random sample (2026-10-15)

Replaces v1 (`census-result-v1.md`, 47-model purposive sample) as the census evidence for
framework-v2 D2. v1 stays as the record. Decisions: D0015, D0019, D0020.
Every number below is printed by `analysis/census/agreement_random.py` (logs
`analysis/census/agreement-random.log`, `agreement-random-excl-readfail.log`) or
`analysis/census/summary_random.py` (log `analysis/census/summary-random.log`).

## Sample
Ranks 1 to 176 of `review/census/census-order.csv` (random order, seed 20261015, over the 1106
records of the census pool: records both title-and-abstract screeners passed to full text, include
or unclear for both, that have an arXiv ID; `tools/census_sample.py`). The stopping rule was coder
B's 150th eligible paper; coder B
reached 151 at rank 176. Ranks 23, 33, 90 and 144 have no full text and are left out of every count.

## Process
1. Coder B: Codex for ranks 1-91 (86 rows; ranks 19 and 79 failed), then Claude Opus for ranks
   92-176 and 19, 79 (Codex usage limit, D0015). Coder A: Claude Sonnet, blind, all ranks.
   Brief: `review/census/CLAUDE-CODER-BRIEF.md`; codebook v1 as amended by v1.1.
2. Agreement before reconciliation, under v1.1 (172 ranks with text).
3. Codebook v1.2 (`census-codebook-v1.2.md`, B-1 to B-28) written by a separate adjudicator after
   both codings and the agreement, from the coders' ambiguity reports
   (`review/census/coder-ambiguities-2026-10-15.md`) without opening row files or papers. Two
   protocol-level items (B-4, B-6) entered as protocol section 10 amendments.
4. Adjudication under v1.2 by two adjudicators (ranks 1-88, 89-176), each checking the paper for
   every disputed cell; then one harmoniser fixed six readings across the halves
   (`review/census/harmonisation-notes.md`). Final rows: `review/census/census-random-final.jsonl`,
   each with the coders' values, the final value and the basis for every disputed or changed cell.

## Agreement before reconciliation (v1.1)

| Field | Raw | kappa | n |
|---|---|---|---|
| eligible (yes/no), all ranks with text | 0.87 | 0.05 | 172 |
| eligible, excluding 15 Codex read failures | 0.96 | 0.20 | 157 |
| non-plain value rule (yes/no/unknown), both eligible | 0.81 | 0.65 | 149 |
| non-plain value rule, both determinable | 0.97 | 0.73 | 62 |
| value rule determinable (not NS) | 0.83 | 0.65 | 149 |
| class A | 0.98 | 0.97 | 62 |
| class T | 0.97 | 0.87 | 62 |
| class P | 0.98 | 0.93 | 62 |
| class S | 0.92 | 0.40 | 62 |
| class G | 0.98 | 0.96 | 62 |
| class M | 0.97 | 0.82 | 62 |
| F3 diversity paired with headline | 0.93 | 0.83 | 149 |
| F4 step sweep | 0.83 | 0.72 | 149 |
| F5 rule held fixed stated | 0.83 | 0.70 | 149 |
| F6 | 0.97 | 0.68 | 149 |

Reading. Eligibility kappa is low at high raw agreement because nearly every record is eligible
(prevalence effect); 20 of 22 eligibility disagreements were coder A yes, coder B no, and 14 of
those were Codex failing to read the paper (placeholder X8/X4 codes; adjudicated from the paper).
Value-rule letters agree well except S (sample-then-filter), which v1.2 B-15 then split by adding C
(confidence-ranked or threshold unmasking with the token rule unstated). Raw disagreements:
`review/census/disagreements-random.csv` (158 field-level rows over 88 ranks).

## Result (final rows, v1.2)
Eligible 167 of 172 ranks with text (X1 4, X0 1). Of the eligible, 15 report no generated-sample
metric (F1 NA); the reporting fields are computed on the other 152.

| Quantity | Final | Sensitivity: agreed cells restored |
|---|---|---|
| headline uses a non-plain value rule or does not state it | 146/152 = 0.961 [0.917, 0.982] | 146/152 = 0.961 [0.917, 0.982] |
| headline uses a stated non-plain value rule | 96/152 = 0.632 [0.553, 0.704] | 85/152 = 0.559 [0.480, 0.636] |
| plain sampling stated (U) | 6/152 | 6/152 |
| value rule not stated (NS) | 50/152 | 61/152 |
| diversity or entropy paired with the headline (F3) | 28/152 = 0.184 [0.131, 0.253] | 28/152 |
| step sweep reported (F4 yes or partial) | 55/152 = 0.362 [0.290, 0.441] | 60/152 = 0.395 [0.321, 0.474] |
| among sweeps, value rule stated as held fixed (F5) | 20/55 = 0.364 [0.249, 0.496] | 20/60 = 0.333 [0.227, 0.459] |

Intervals are 95 percent Wilson intervals that treat the ranks as a simple random sample of the
1106-record pool (the order is random; the sample is the first 176 ranks). Letters among the 152
(papers with each, a paper can have several): A 33, C 20, G 22, M 12, P 12, S 12, T 13; 15 carry
"+NS" (a stated letter with the base token rule unstated). The sensitivity column undoes the 45
cells both coders agreed on that adjudication changed under v1.2 triggers (mostly the new codes C
and +NS); the headline proportion does not move.

## What can be said (draft wording for Paper 1, to be checked by gate-auditor)
In a random sample of the census pool, 146 of 152 papers that report a generated-sample
headline (96 percent, 95 percent interval 92 to 98) either decode it with a value rule other than
plain sampling at temperature 1 or do not state the rule; 18 percent report diversity or entropy
for the headline setting; of the 55 that sweep the number of steps, 20 state that the value rule
was held fixed. Credit: the general point that reported quality depends on the sampling rule is
made for other metrics before (D0019); this census quantifies it for diffusion language models.

## Limits
- Coder B is two systems (Codex, then Claude Opus); coder A and the Claude part of coder B are
  both Claude models, so their agreement may overstate independent human agreement. No human coder
  has yet coded this sample (the professor's review requirements ask for reviewer agreement).
- Blindness incident (D0019): coder A's ranks 1-40 batch ran coder B's append script once and may
  have seen coder B's scratch rows for ranks 92-128, which it did not code.
- v1.2 was written after the agreement was computed; agreement is reported under v1.1.
- 15 rows carry F1 as a relative gain or ratio rather than a level (harmonisation reading 5).
- Reading 2 (process-level samplers with guidance coded G+NS) moves 4 rows between G and G+NS; it
  does not change the non-plain count.
