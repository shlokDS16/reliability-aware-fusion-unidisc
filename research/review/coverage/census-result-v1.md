# Census of value rules and reporting, result v1 (2026-10-14)

Sample: the 47 models of `design-space-v1.md` (a purposive sample stratified by family, not the
systematic corpus). Extension to all included records is required before this is a review result
(framework-v2 D2). Codebook: `census-codebook-v1.md` (frozen before the second coding).

## Process
1. Coder 1 (paper-reader, before the codebook): `design-space-v1.csv`.
2. Coder 2 (paper-reader, blind to coder 1, under codebook v1): `census-coder2.csv`, notes
   `census-coder2-notes.md` (32 ambiguities, F1 policy A1).
3. Agreement before reconciliation (`analysis/census/agreement.py`, log `agreement.log`), with
   coder 1's fields mapped onto the codebook:

| Field | Raw agreement | Cohen's kappa | n |
|---|---|---|---|
| class A (argmax) | 0.77 | 0.43 | 26 |
| class T (temperature below 1) | 0.92 | 0.75 | 26 |
| class P (truncation) | 0.96 | 0.88 | 26 |
| class S (sample-then-filter) | 0.96 | 0.84 | 26 |
| class G (guidance) | 0.92 | 0.84 | 26 |
| class M (sequence-level selection) | 1.00 | 1.00 | 26 |
| non-plain value rule, rows both coded | 0.92 | 0.47 | 26 |
| value rule determinable (stated) | 0.72 | 0.35 | 47 |
| entropy or diversity reported | 0.81 | 0.56 | 36 |
| step sweep reported | 0.93 | 0.47 | 29 |

   Caveat: coder 1 did not use the codebook, so these kappas mix coder disagreement with
   definitional differences; the low value for "stated" mostly reflects coder 1 inferring
   defaults that the codebook forbids. A codebook-to-codebook agreement on the full corpus is
   still needed.
4. Adjudication by a third reader (`census-adjudication.csv`, 21 papers; notes with 10 proposed
   codebook amendments A-1 to A-10): `census-final.csv`. On the 15 disputed value-rule rows coder 2
   was right in 13 and coder 1 in 2; coder 2 also missed explicit text in 4 papers (M12, M45, M14,
   M22). Four F5 cells (M24, M30, M39, M40) remain unresolved and keep coder 2's value.

## Result (adjudicated; `analysis/census/summary.py`, log `summary.log`)

Of 47 papers, 45 report a headline generated-sample result (2 report likelihood only).

| Headline value rule | Papers | Entropy or diversity reported next to the headline |
|---|---|---|
| non-plain (argmax 6, truncation 6, guidance 9, temperature below 1 4, sample-then-filter 5, sequence-level 1; a paper can have several) | 25 | 7 |
| plain sampling at temperature 1, stated | 8 | 4 |
| not stated | 12 | 1 |

- 37 of 45 (82 percent) headlines either use a non-plain value rule or do not state one.
- 12 of 45 report entropy or diversity next to the headline.
- 37 report a step sweep; 10 of these state that the value rule was held fixed, 2 state that it
  co-varies, 25 do not say.
- 9 headlines use guidance; 2 state that guidance was fixed in the step sweep.

Reading: for most of these papers a reader cannot separate the contribution of the model from that
of the decoding rule, either because the rule sharpens the output without an accompanying
diversity measure or because the rule is not stated. With P2 withdrawn (framework-v2 C), even a
reported entropy would not settle attribution; it is a necessary, not a sufficient, report.
Whether a paper separates the two elsewhere (ablation, appendix, code) is not coded here.

## Before this goes into the review
- Apply or reject amendments A-1 to A-10 as codebook v1.1, dated, with reasons.
- Code the full included corpus with two independent coders under v1.1; report kappa before
  reconciliation per field; publish rows and adjudications.
- Resolve the four F5 cells.
