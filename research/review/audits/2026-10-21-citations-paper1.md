# Citation gate, Paper 1 main text (2026-10-21)

Agent: citation-validator (subagent of session 0839c9f4). The agent could not write a report file, so this file holds
its final message as returned, followed by the orchestrator's action log.

Counts (68 main.bbl entries): ok 39 | metadata error 17 | partial 10 | unsupported claim 1 | not found 1 | retracted 0.
Gate as returned: FAIL (1 not found, 1 unsupported).

Method (agent): arXiv API for 63 records (title, authors, year, comments, withdrawal flags); Crossref for DOIs and for
published versions (19 hits) and update-to/updated-by (none); abstracts for all arXiv entries; WebFetch of arXiv HTML
for specific claims (model summaries of page text, some pages read in part). Not covered: bib entries outside
main.bbl, supplement-only citations, code-level claims.

Problems returned (paths relative to paper/review/):
- P1 06-census.tex:102, openreview:Gq4yt8pxRo not found (anonymous submission under review): delete the clause.
- P2 03-notation.tex:43, arXiv:2505.15809 (MMaDA) does not support "one shared level": cite UniDisc only.
- P3 01-introduction.tex:62, arXiv:2401.01879 is best-of-n KL and win-rate bounds, not a one-token law; arXiv:2605.12522
  "law of a one-token commit with heterogeneous competitors" not located.
- P4 07-error-budget.tex:23, arXiv:2603.22248 gives an entropy-threshold bound whose proof uses an MI decomposition.
- P5 07-error-budget.tex:23, arXiv:2502.09622: chain-rule decomposition of the total-error bound.
- P6 03-notation.tex:46, arXiv:2407.15595 supports corrector re-masking, not token editing.
- P7 07-error-budget.tex:26, arXiv:2410.08709 TV O(1/N) is for the product model.
- P8 03-notation.tex:41, symmetric channel: MDLM (arXiv:2406.07524) models masking only; cite D3PM only.
- P9 08-open-problems.tex:44, MMaDA-Parallel numbers are in Appendix I, Table 10; "one run" and "no interval" not
  found; the released-sampler statement is a code claim not checked.
- P10 01-introduction.tex:23, arXiv:2509.24435 is titled a survey and says it was conducted through a systematic review.
- P11 01-introduction.tex:18, "shown in figures without pooling or intervals" not confirmed for arXiv:2508.10875.
- P12 07-error-budget.tex:23, Li and Cai bound the mutual-information analogue.
- P13 note: arXiv:2505.24857 calls its Eq. 8 term joint mutual information.
- P14 references.bib: 19 published versions with DOIs and TMLR 2026 for arXiv:2510.04525 (no DOI).
- P15 no retractions or withdrawals.
- P16 not verified: arXiv:2511.09611 code claim; MD4 Eq. 5 and MDLM Eq. 13; arXiv:2110.02037 Eq. 3-4; figures of
  arXiv:2508.10875; last 12k characters of arXiv:2506.13759; arXiv:2605.12522 "nearest arm ranks by entropy".

## Orchestrator action log (2026-10-21)
- P1-P12 applied with the agent's replacement wording (P3b reworded to "the majorisation argument for a one-token
  commit and the sample--select--resample fix"; P9: numbers kept with their appendix location, "one run" and "no
  interval" deleted, the code statement marked as an unverified code reading). P13 not applied (terminology note).
- P14 applied to 20 entries (19 DOIs plus TMLR venue); TCSVT year set to 2026, vol. 36(4), pp. 5621-5641 from
  Crossref (issued 2026-04). BibTeX now warns only about missing publisher, address and page fields.
- P16 items remain unverified and are listed as open for the final read-through.
