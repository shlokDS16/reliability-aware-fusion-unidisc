# Census adjudication notes, ranks 1 to 88 (random sample)

Date: 2026-10-15. Adjudicator: Claude (Opus 5.5), not blind (read both coders' rows and notes).
Governing rules: codebook v1.2 (`research/review/coverage/census-codebook-v1.2.md`), with v1 and v1.1
where v1.2 is silent. Output: `census-random-final-r001-r088.jsonl` (88 rows, one per rank, keys as
specified; `adjudication` records A, B, final and basis for every disputed or changed field).
Agreement figures under v1.1 are not recomputed here (v1.2 disclosure).

Inputs: coder A rows (`coder-A-claude-r001-r040/r041-r080/r081-r120.jsonl`), coder B rows
(`coder-B.jsonl`, Codex; `coder-B-claude-gapfill.jsonl` for ranks 19 and 79), field-level
disagreements (`disagreements-random.csv`, 99 rows for ranks 1-88), and the paper texts in
`research/sources/census-text/`. F0_version was read from the `arXiv:<id>vN` line of each text file.

## Summary

- Rows written: 88. Eligible yes: 86. Eligible no: 0. NO_TEXT: 2 (ranks 23, 33; B-8).
- F1 = NA among eligible rows: 8 (ranks 27, 28, 36, 38, 52, 56, 83, 85); rank 6 is coded (see
  unsettled case 1).
  F1 = QL: 1 (rank 71). F1 = figure-only: 2 (ranks 3, 66).
- Final F2 classes among the 78 eligible rows with F1 coded: NS 26; A 13; C 7; P 4; S 4; T 4; U 3;
  T+P+S 3; G+NS 3; S+M 2; G+M+NS 2; T+M 2; P+S, T+P, A+T, P+G, A+G 1 each.
- Coder B (Codex) could not read the file for 15 ranks (1, 21, 24, 26, 34, 37, 42, 43, 59, 64, 82,
  83, 84, 85, 87); its X8/X4 codes there are tool-failure placeholders. Those rows were verified
  against the paper field by field, so they are effectively single-coded plus adjudication.

## Counts of adjudicated fields

All fields with an `adjudication` entry (175 field decisions over 88 rows). "A=B normalised" is a
vocabulary-only difference; "agreed cell changed" is a cell both coders agreed on that a v1.2
trigger in their own notes reopened.

| Field | n | A | B | neither | agreed cell changed | A=B normalised |
|---|---|---|---|---|---|---|
| eligible | 21 | 20 | 0 | 0 | 0 | 1 |
| F1_task | 16 | 7 | 6 | 3 | 0 | 0 |
| F1_metric | 3 | 2 | 1 | 0 | 0 | 0 |
| F1_value | 37 | 16 | 10 | 10 | 1 | 0 |
| F2_codes | 43 | 17 | 7 | 11 | 8 | 0 |
| F3 | 8 | 5 | 3 | 0 | 0 | 0 |
| F4 | 25 | 12 | 9 | 3 | 1 | 0 |
| F5 | 22 | 10 | 11 | 0 | 1 | 0 |
| total | 175 | 89 | 47 | 27 | 11 | 1 |

Of these, 39 decisions sit in the 15 rows where coder B failed to read the paper (A 28, B 6,
neither 5); B's "agreement" there is only with A's NA-by-coupling values.

Restricted to the 99 rows of `disagreements-random.csv` for ranks 1-88:

| Field (csv) | n | A | B | neither |
|---|---|---|---|---|
| eligible | 20 | 20 | 0 | 0 |
| nonplain (derived) | 17 | 8 | 9 | 0 |
| F2_codes | 25 | 12 | 4 | 9 |
| F3 | 7 | 5 | 2 | 0 |
| F4 | 16 | 8 | 8 | 0 |
| F5 | 14 | 6 | 8 | 0 |
| total | 99 | 59 | 31 | 9 |

All 20 eligibility disagreements went to A: 14 were B tool failures, and 6 were B's X7 on
inference/serving/drafter/detector/prompt-optimizer papers (27, 28, 36, 38, 39), which B-1 and B-2
make eligible. The csv lists no F1 disagreements; F1 task/value choices that differed substantively
were adjudicated as well and appear in the first table.

## v1.2 rules invoked (ranks)

- B-1 (inference, serving, systems eligible; F1 = NA when speed-only): 1, 15, 21, 24, 27, 28, 34, 38, 56, 84, 85.
- B-2 (detectors, attacks, probes, drafters, analyses; detector metrics give F1 = NA): 6, 19, 26, 36, 39, 52, 53, 83, 85.
- B-4 (unified models with AR text and diffusion component): 2, 35, 79.
- B-5 (diffusion experiment in an otherwise AR paper; latent diffusion decoded to text): 72, 79.
- B-8 (NO_TEXT): 23, 33.
- B-9 (F1 from the in-scope task; synthetic token tasks only if no NL experiment): 2, 3, 12, 48, 69, 79.
- B-10 (generated-sample metric; likelihood, speed, detector scores skipped): 6, 12, 15, 18, 30, 35, 36, 47, 54, 61, 82, 83, 85, 88.
- B-11 (table order, quoted metric/row, first row not best row, figure fallback): 3, 12, 18, 19, 32, 44, 45, 46, 49, 50, 51, 55, 60, 61, 66, 72, 73, 74, 77, 84.
- A-2 (abstract number first; abstract task order; T2I before understanding; best row only for plain vs guided): 2, 17, 31, 42, 45, 46, 63, 72.
- B-12 (cell read from the text; extraction issues): 37 (A's value was not in the row).
- B-13 (conflicting statements): considered at 34, not applied (statements govern different positions).
- B-14 (U vs NS; preliminaries/background do not count): 3, 5, 9, 46, 49, 62.
- B-15 (confidence-ranked or threshold unmasking: C, or A/S when the token rule is stated): 1, 5, 7, 9, 10, 12, 14, 20, 21, 35, 37, 43, 46, 51, 57, 61, 62, 69, 80, 81, 84.
- B-16 (training-only settings): 19, 74, 79.
- B-17 (candidate selection as M): 10 (and agreed M at 68).
- B-19 (particle/SMC resampling as M, +G for external reward): 17, 22, 41, 48.
- B-20 (G incl. hard constraints; omega=0 is no guidance): 58, 75.
- B-21 (+NS for unstated base rule; U never combines; A excludes S): 17, 22, 29, 41, 61, 72, 77.
- B-22 (unlisted diversity metrics): 44.
- B-23 (sweep needs a printed step measure; length-driven or speed-only excluded): 1, 21, 22, 32, 34, 35, 44, 60, 67, 78, 84, 87, 88.
- B-24 (sweep must be on the F1 task/setting; particles, passes, separately trained block sizes excluded): 3, 7, 9, 13, 16, 22, 32, 39, 60, 61, 64, 76, 82.
- B-25 (F5/F6 NA when F4 no): every row where F4 became no.
- B-26 (blanket all-experiments sentences make F5 stated): 34, 42, 84, 86.
- B-27/B-28 (vocabulary and couplings): all rows; e.g. "NS+G" to "G+NS" (77), "Yes" to "yes" (79).
- v1.1 items also used: A-1 (F3 pairing; FID/IS boilerplate) 14, 45, 63; A-4 (per-step projection) 40; A-6 (temperature) 34, 48, 87; A-9 (F5 stated) 18, 49, 87; A-10 (QL) 71.

## Cases v1.2 does not settle (call made, flagged)

1. Rank 6, also 76, 78, 88: analysis or benchmark papers with no generative method of their own.
   B-2 says F1 "follows B-10", so F1 was taken as the first generated-sample number in the abstract
   (rank 6: Nemotron accuracy +15.0 points under direct prompting; A's trace statistic U and B's NA
   both rejected). v1.2 should say whether such papers carry an F1 at all.
2. Ranks 5, 9, 46, 62: greedy/argmax stated only in a "Preliminaries"/"Background" section that
   describes generic dLLM (LLaDA-style) decoding, which the method then reuses. Read as B-14
   "background ... describing earlier samplers", so token rule unstated and C coded. Rank 9 was an
   agreed A cell reopened by coder A's own "borderline" note.
3. Rank 14: a sampling-time semantic-frequency (repetition-type) logit penalty. B-20 covers external
   scores and hard constraints but not count-based penalties; not coded as G, recorded in F2_detail.
4. Rank 18: the F1 table's columns are a step sweep; B-11 does not say which column. First column
   (32 NFE) taken. Same call implicitly at 49, 50, 51 (first column, not the best one).
5. Rank 29: a unified model that is eligible under both I1(a) and I1(b). B-9's "images from a
   text-eligible paper are out of scope" was not applied; all outputs of the unified model were
   treated as in scope and A-2's text-to-image-first order used.
6. Rank 34: argmax for confidence-gated early-exit positions and T=0.1 sampling for the remaining
   positions in the same step. B-21 ("A excludes S and T for the same step") assumes one mechanism;
   coded A+T.
7. Rank 44: Fig 4 reports outputs decoded at earlier steps of the inference trajectory; counted as a
   step sweep (both coders did). Rank 88's intermediate-step readouts were not counted, because the
   answers there are uncommitted predictions inside one run. B-23 should say whether truncated
   trajectories count as completed samples.
8. Rank 47: "evaluated ... with 128 Monte Carlo samples" implies likelihood scoring but does not
   state it; B-10 read literally, so the MMLU accuracy counts and Table 1 is F1.
9. Rank 51: a Gibbs corrector that resamples tokens whose probability is below 0.1 was treated as
   B-15 threshold selection with a sampled token (S). Both coders had NS.
10. Rank 54: PPL_u is never defined; read as perplexity under the model (reported across transfer
    corpora), so skipped under B-10 and MAUVE taken.
11. Rank 55: B-11's table-before-figure order makes an LLM-judge diversity comparison (Table 1) the
    headline, ahead of Pass@5 numbers that the text quotes from Fig 2.
12. Rank 69: the argmax statement covers only the Sudoku experiment; the in-scope F1 task (GSM8K,
    B-9) relies on the method-level Algorithm 1 (sampling), coded S.
13. Rank 76: B-24 extended to require the F1 model itself (closed-source Mercury) to be in the step
    sweep; the sweep covers other models and MBPP, so F4 = no (agreed yes reopened from A's note).
14. Rank 77: the text quotes two cells of the headline row (average, then GSM8K). B-11 does not rank
    quoted metrics; the earliest quotation (Sec 1, average 24.8) was taken.
15. Rank 83: watermark-robustness study on LLaDA outputs, attack run by AR rewriters. Eligible under
    B-2 (object of study is a DLM's outputs), X7 is the alternative; F1 = NA (detector metrics).
16. Rank 84: no accuracy table; multi-panel Fig 3. The panel the text quotes (MATH 43.6%) was used.
17. Rank 1: NFE changes caused by the score-penalty strength lambda were not treated as a step sweep
    (B-23 names thresholds, schedules and cache intervals only); the gamma budget sweep prints only
    speed-up. F4 = no.
18. Rank 3: an appendix "Decoding Method" paragraph (uniform decoding, greedy only for Countdown, no
    truncation named) was read as a complete settings list under B-14(3), giving U.

## Notable corrections of coder errors (not rule questions)

- Rank 32: A's 55.08 is the throughput cell; pass@1 is 61.94 (first SW-SetDLM row).
- Rank 37: A's 79.26 is not in the EchoChange row (26.18 / 30.86 / 77.40).
- Rank 7: B's argmax came from the speculative variant, not the headline MDM row.
- Rank 61: BBH is evaluated by conditional generation (LLaDA App B.6) and precedes GSM8K in Table 1.
- Rank 79: both coders took Janus-Pro (autoregressive) rows; B-9 requires the Lumina-DiMOO row.
