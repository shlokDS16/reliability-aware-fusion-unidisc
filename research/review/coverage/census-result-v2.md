# Census of value rules and reporting, result v2: random sample (2026-10-15, corrected after gate audit)

Replaces v1 (`census-result-v1.md`, 47-model purposive sample) as the census evidence for
framework-v2 D2. v1 stays as the record. Decisions: D0015, D0019, D0020, D0021. Gate audit:
`review/audits/2026-10-15-gate-census-v2.md` (PASS WITH CORRECTIONS; C1-C12 applied in this version).

Sources of numbers. Agreement: `analysis/census/agreement_random.py`, logs
`analysis/census/agreement-random.log` and `agreement-random-excl-readfail.log`. Counts and
intervals: `analysis/census/summary_random.py`, log `analysis/census/summary-random.log`. Effect of
gap rulings: `analysis/census/gap_rulings.py`, log `analysis/census/gap-rulings.log`. Process
numbers: `review/census/census-order.csv` (ranks, pool), `review/census/fetch-status.json` (no-text
ranks), `review/census/coder-*.jsonl` (coders, read failures), `review/census/harmonisation-notes.md`
and `adjudication-notes-*.md` (adjudication counts), `review/coverage/census-codebook-v1.2.md`.

## Sample
Ranks 1 to 176 of `review/census/census-order.csv` (random order, seed 20261015, over the 1106
records of the census pool: records both title-and-abstract screeners passed to full text, include
or unclear for both, that have an arXiv ID; `tools/census_sample.py`). The stopping rule was coder
B's 150th eligible paper; coder B reached 151 at rank 176. Because the rule counted Codex read
failures as ineligible, the 150th eligible paper under final eligibility is at rank 157, so 19
extra ranks were coded; this does not bias the proportions. Ranks 23, 33, 90 and 144 have no full
text and are left out of every count.

## Process
1. Coder B: Codex for ranks 1-91 (86 rows; ranks 19 and 79 failed), then Claude Opus for ranks
   92-176 and 19, 79 (Codex usage limit, D0015). Coder A: Claude Sonnet, blind, all ranks.
   Brief: `review/census/CLAUDE-CODER-BRIEF.md`; codebook v1 as amended by v1.1.
2. Agreement before reconciliation, under v1.1 (172 ranks with text).
3. Codebook v1.2 (`census-codebook-v1.2.md`, B-1 to B-28) written by a separate adjudicator after
   both codings and the agreement. Its author read the coders' ambiguity reports
   (`review/census/coder-ambiguities-2026-10-15.md`), the disagreement list and the agreement log,
   but did not open the coders' row files or any paper. Two protocol-level items (B-4, B-6) entered
   as protocol section 10 amendments.
4. Adjudication under v1.2 by two adjudicators (ranks 1-88, 89-176), each checking the paper for
   every disputed cell; then one harmoniser fixed six readings across the halves
   (`review/census/harmonisation-notes.md`). Final rows: `review/census/census-random-final.jsonl`,
   each with the coders' values, the final value and the basis for every disputed or changed cell.
   The adjudicators and the harmoniser were not blind to the coders.

## Agreement before reconciliation (v1.1)

| Field | Raw | kappa | n |
|---|---|---|---|
| eligible (yes/no), all ranks with text | 0.87 | 0.05 | 172 |
| eligible, excluding 15 Codex read failures | 0.96 | 0.20 | 157 |
| non-plain value rule (yes/no/unknown; F2 = NA pooled with NS as unknown), both eligible | 0.81 | 0.65 | 149 |
| non-plain value rule, both determinable | 0.97 | 0.73 | 62 |
| value rule determinable (not NS or NA) | 0.83 | 0.65 | 149 |
| class A | 0.98 | 0.97 | 62 |
| class T | 0.97 | 0.87 | 62 |
| class P | 0.98 | 0.93 | 62 |
| class S | 0.92 | 0.40 | 62 |
| class G | 0.98 | 0.96 | 62 |
| class M | 0.97 | 0.82 | 62 |
| F3 diversity paired with headline | 0.93 | 0.83 | 149 |
| F4 step sweep | 0.83 | 0.72 | 149 |
| F5 rule held fixed stated | 0.83 | 0.70 | 149 |
| F6 | 0.97 | 0.68 | 149 (141 of the 149 pairs are NA/NA) |

Reading. Eligibility kappa is low at high raw agreement because nearly every record is eligible
(prevalence effect). 20 of the 22 eligibility disagreements were coder A yes, coder B no; 15 of
those 20 were Codex failing to read the paper (placeholder codes X8 in 12, X4 in 2, none in rank 84;
adjudicated from the paper, so these 15 ranks are in effect coded once plus adjudication).
Value-rule letters agree well except S (sample-then-filter), which v1.2 B-15 then split by adding C
(confidence-ranked or threshold unmasking with the token rule unstated). Raw disagreements:
`review/census/disagreements-random.csv` (158 field-level rows over 88 ranks).

## Result (final rows, v1.2)
Eligible 167 of 172 ranks with text (X1 4, X0 1). Of the eligible, 14 report no generated-sample
metric (F1 NA) and 1 shows samples only (F1 QL, rank 71). The value rule is counted on the 153
eligible rows with an F2 code (codebook v1.2 B-28: QL rows enter F2 only); F3 to F6 on the 152 with a
generated-sample metric.

| Quantity | Final | Sensitivity: cells both coders agreed on restored |
|---|---|---|
| headline uses a non-plain value rule or does not state it | 147/153 = 0.961 [0.917, 0.982] | 148/154 = 0.961 [0.918, 0.982] |
| headline uses a stated non-plain value rule | 97/153 = 0.634 [0.555, 0.706] | 86/154 = 0.558 [0.480, 0.634] |
| plain sampling stated (U) | 6/153 | 6/154 |
| value rule not stated (NS) | 50/153 | 62/154 |
| diversity or entropy paired with the headline (F3) | 28/152 = 0.184 [0.131, 0.253] | 28/153 = 0.183 [0.130, 0.252] |
| headline reported at two or more step settings (steps, NFE or tokens per step; F4 yes or partial) | 55/152 = 0.362 [0.290, 0.441] | 61/153 = 0.399 [0.325, 0.478] |
| among those, value rule stated as held fixed (F5) | 20/55 = 0.364 [0.249, 0.496] | 21/61 = 0.344 [0.237, 0.470] |

Intervals are 95 percent Wilson intervals that treat the ranks as a simple random sample of the
1106-record pool. Letters among the 153 (papers with each; a paper can have several): A 33, C 20,
G 22, M 12, P 12, S 12, T 14; 15 carry "+NS" (a stated letter with the base token rule unstated).

The sensitivity column restores every cell on which coder A and coder B agreed (after
normalisation, from the coder files) to the agreed value; this undoes the 42 count-relevant agreed
cells that adjudication reopened under v1.2 (the other 3 reopened cells are F1 values). Of the 45
reopened cells, 25 are F2 codes, and 20 of those 25 use the new v1.2 codes C or +NS. Rank 128,
eligible by agreement but X1 under B-3, re-enters the sensitivity with its agreed F3 to F5 and
its disputed F2 counted as NS. The headline proportion does not move.

### Effect of the v1.2 gap rulings (D0020(3); `gap-rulings.log`)
A ruling can lower "non-plain or not stated" only by turning a row into U, and "stated non-plain" by
at most the number of non-plain rows it decided. Rows decided per ruling (in the F2 denominator;
non-plain / NS / U): B-15 new code C, 40 (39 / 0 / 1); B-21 "+NS", 19 (18 / 1 / 0); B-24 sweep on
the F1 task, 18 (12 / 6 / 0; F4 yes or partial 1); B-10 benchmark accuracy as a generated-sample
metric, 15 (12 rows in F2; 7 / 5 / 0); B-9 F1 from the in-scope task, 14 (7 / 5 / 2); B-19 SMC as
M, 6 (6 / 0 / 0); B-13, B-17, 3 each; B-22, 1; B-18, 0. Eligibility rulings B-3, B-4, B-6, B-8 decided
2, 3, 3 and 4 ranks (123, 128, 154, 165, 169, 119 among them). The largest exposure is B-15: if C were
read as "not stated" rather than non-plain, "stated non-plain" would fall by at most 39, while
"non-plain or not stated" is unaffected.

## What can be said (draft wording for Paper 1)
In a random sample of the census pool, 147 of 153 papers that report a generated-sample headline
or samples (96 percent, 95 percent interval 92 to 98) either decode it with a value rule other than
plain sampling at temperature 1 or do not state the rule; 18 percent of the 152 with a metric report
diversity or entropy for the headline setting; of the 55 that report the headline at two or more
step settings (steps, NFE or tokens per step), 20 state that the value rule was held fixed.
Credit: that reported quality and fairness depend on the sampling or evaluation setting has been
argued for other metrics and model families before: OpenReview Gq4yt8pxRo (sampling-dependent
fairness in diffusion language models; abstract only, E1), arXiv 2606.29228 (Evaluation Illusion),
2606.20536 (FID Lottery) and 2607.24763 (CaRE) (`review/audits/2026-10-15-novelty-EXP-003.md`
sections 4-5; D0019). This census quantifies the reporting gap for diffusion language models.

## Limits
- Coder B is two systems (Codex, then Claude Opus); coder A, the Claude part of coder B, both
  adjudicators and the harmoniser are Claude models, so agreement may overstate independent human
  agreement. No human coder has yet coded this sample (the professor's review requirements ask
  for reviewer agreement). The 15 Codex read-failure ranks are in effect single-coded.
- Blindness incident (D0019): coder A's ranks 1-40 batch ran coder B's append script once and may
  have seen coder B's scratch rows for ranks 92-128, which it did not code.
- v1.2 was written after the agreement was computed; agreement is reported under v1.1.
- 15 rows carry F1 as a relative gain or ratio rather than a level (harmonisation reading 5).
- Harmonisation reading 2: ranks 91, 114, 120 and 141 (process-level samplers with guidance) stay
  G+NS; the alternative reading (B-14 replacing the v1.1 A-3 clause) would make them G. Neither
  reading changes a non-plain count. Keeping 114, 120 and 141 changed agreed cells without a
  trigger in the coders' notes (D0021).
- Census numbers are in `analysis/census/*.log`, not in a `runs/<exp-id>/` directory; the project
  rule is read as covering experiment numbers (D0021).
