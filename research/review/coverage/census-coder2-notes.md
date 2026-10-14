```yaml
agent: paper-reader (census coder 2)
date: 2026-10-14
brief: Code 47 papers independently against census-codebook-v1 as the second extractor; agreement with an earlier coding will be reported.
sources_examined:
  - research/CONTRACT.md
  - research/review/coverage/census-codebook-v1.md
  - cached paper text, main checkout research/sources/md/ (one file per arXiv ID listed below)
blinding: >
  Kept. Not opened: design-space-v1.md, design-space-v1.csv, design-space-v1-build/, census-recount-2026-10-14.md,
  research/review/dossier/*, framework-v2.md, progress/ledger files. One directory listing of
  research/review/coverage/ (file names only, no contents) was run by mistake while writing the CSV; it showed that
  the design-space and recount files exist. No file content from them was read.
coverage: >
  Per paper: abstract, every main-text results table or figure that reports the paper's own method,
  and the sampling/decoding/evaluation-setup passages (main text and appendix) found by keyword search
  (temperature, top-p/top-k, argmax/greedy, confidence/remasking, guidance/CFG, steps/NFE/timesteps,
  entropy/diversity/pass@k, MBR/best-of). Papers were NOT read end to end. Proofs, related work, training
  details, and qualitative-sample appendices were not read. Code repositories were not opened (codebook rule).
  Cached text is the reading source for all 47; no new downloads were made.
claims: []
competing_explanations: []
unknowns:
  - F0 is the version of the cached text, not necessarily the latest on 2026-10-14 (no network check made).
  - Five papers were cached as Exa copies without a version string (M02, M03, M04, M05, M06).
next_test: {}
```

# Census coder 2: notes

Output: `research/review/coverage/census-coder2.csv` (47 rows, columns as briefed). Policy and ambiguities below are recorded, not resolved; the codebook was not changed.

## Coverage by paper (what was read)

All rows: abstract plus the sections listed. "Samp." = sampling/decoding/eval-setup passages including appendix.

| id | arXiv | version coded | read |
|---|---|---|---|
| M01 | 2107.03006 | v3 | abstract; Sec 5-6; Tables 1-3; Fig 2 |
| M02 | 2205.14987 | not stated (Exa copy) | abstract; Sec 6; Table 1; Fig 4; App H.2 |
| M03 | 2310.16834 | not stated (Exa copy) | abstract; Sec 5.1 unconditional generation; Fig 1; Table 5 text |
| M04 | 2406.07524 | not stated (Exa copy) | abstract; Sec 4.1-4.2; Table 5; App E.2 (Fig 2, Table 10) |
| M05 | 2406.04329 | not stated (Exa copy) | abstract; Sec 5 sampling paragraphs; Fig 2; App K (Fig 8, Table 6) |
| M06 | 2406.03736 | not stated (Exa copy) | abstract; Sec 4.2; App J.3-J.4 (Tables 3-4) |
| M07 | 2409.02908 | v6 | abstract; Sec 5-6; Table 2; Figs 7, 9, 10 captions and text |
| M08 | 2110.02037 | v2 | abstract; Sec 5; Tables 1-5 (all likelihood/compression) |
| M09 | 2502.09992 | v3 | abstract; Sec 2.4; Table 1; App A.2 (Alg 4-5), B.3-B.7 |
| M10 | 2202.04200 | v1 | abstract; Sec 3.2, 4.2, 4.4; Tables 1, 3; Fig 8 |
| M11 | 2503.00307 | v4 | abstract; Sec 5.1; Table 1; nucleus paragraph; image setup |
| M12 | 2505.24857 | v1 | abstract; Sec 3-4, 6.1; Fig 4 code; Table 1; App C.1 |
| M13 | 2205.14217 | v1 | abstract; Sec 4.2, 5, 6, 7.1; Tables 2, 5 |
| M14 | 2211.15089 | v3 | abstract; Sec 6.2-6.4; Tables 1-2; Final prediction paragraph |
| M15 | 2305.18619 | v1 | abstract; Sec 4.1, 5; Tables 1-4 |
| M16 | 2407.15595 | v2 | abstract; Sec 3-4; Tables 2-5; App G |
| M17 | 2506.10892 | v3 | abstract; Sec 3 sampling; Sec 5; Table 5; Fig 3-4 captions |
| M18 | 2503.09573 | v3 | abstract; Sec 6.2; Tables 6-7; App nucleus/64-bit/steps |
| M19 | 2210.17432 | v2 | abstract; Sec 3.2, 4.2; Tables 1, 4, 5 |
| M20 | 2408.12528 | v7 | abstract; Sec 3-4; Tables 2-3; App D, I |
| M21 | 2503.20853 | v1 | abstract; Sec 3.4, 4.1-4.2; Figs 4-5; Tables 1, 6; sampling algorithm |
| M22 | 2505.15809 | v2 | abstract; Table 2; sampling appendix (text and image) |
| M23 | 2511.09611 | v3 | abstract; Sec 4.2-4.3; Tables 2, 5, 10; sampling appendix |
| M24 | 2505.20147 | v3 | abstract; Sec 3.4; Table 1; Sec 4.2-4.3 |
| M25 | 2510.06308 | v1 | abstract; Sec 3 sampling; Table 3; Sec 7.1 |
| M26 | 2408.11039 | v1 | abstract; Sec 4.1-4.2; Table 3 |
| M27 | 2505.14683 | v3 | abstract; Sec 2; Tables 4-5 |
| M28 | 2506.15564 | v3 | abstract; Table 5; Sec 4.5 Table 11 |
| M29 | 2509.19244 | v3 | abstract; Sec 3.2; Table 2-3; App B.3, B.7 |
| M30 | 2305.08379 | v2 | abstract; Sec 4.4, 5.1, 6.3; Tables 1, 7; App C |
| M31 | 2502.13917 | v2 | abstract; Sec 3.1, 4.3-4.4; Table 3; Fig 3 |
| M32 | 2210.08933 | v3 | abstract; Sec 3-4; Table 1; Figs 3, 5, 6 text |
| M33 | 2510.22510 | v3 | abstract; Sec 5.3, 6; Figs 5-6; App D.1; sample captions |
| M34 | 2608.10615 | v2 | abstract; Sec 4.1-4.2; Table 1; App Tables 7-8 |
| M35 | 2508.15487 | v1 | abstract; Sec 5; Table 1; Sec 5.5.2 |
| M36 | 2410.17891 | v3 | abstract; Sec 3.4, 4.3; Table 1; Fig 3; App B-C |
| M37 | 2506.20639 | v2 | abstract; Sec 3-5; Tables 1-2; Figs 5-6; App B.2 |
| M38 | 2508.02193 | v1 | abstract; Sec 3.4, 4; Table 1; Fig 2 |
| M39 | 2505.22618 | v3 | abstract; Sec 3.3, 4; Table 1; Fig 5 |
| M40 | 2410.08709 | v4 | abstract; Sec 5.1; Tables 1-2; App F.1 |
| M41 | 2410.01949 | v2 | abstract; Sec 5.3, 6.1; Figs 3, 8 |
| M42 | 2412.10193 | v3 | abstract; Sec 5.2; Tables 4, 7 |
| M43 | 2505.16839 | v4 | abstract; Sec 1, 4.5; Table 3; App Table 6 |
| M44 | 2505.23606 | v5 | abstract; Sec 2.2, 3.1-3.4; Tables 1, 5 |
| M45 | 2604.00007 | v1 | abstract; Sec 4 remasking; Sec 6.2; Sec 7.2 |
| M46 | 2501.00289 | v2 | abstract; Sec 3.3, 4.3; Tables 2, 5 |
| M47 | 2505.16990 | v3 | abstract; Sec 2-3; Tables 1, 4; App evaluation details |

## Coding policy I applied (needed because the codebook leaves room)

P1. F1 is the first quantitative result for the paper's own method that is a generated-sample metric. If the abstract's first number is a speed, a speedup or a likelihood/perplexity bound, I skipped it (recorded in the notes field) and took the first main-text table (or figure when no main-text table exists) that reports a generated-sample metric for the own method. F1 = NA only when no generated-sample metric exists anywhere (M08 ARDM, M15 Plaid).
P2. For unified models whose text side is autoregressive (Show-o, BAGEL, Show-o2) I used the first table where the diffusion/flow component produces the metric. For unified models that decode text by masked diffusion (MMaDA, LaViDa-O, Dynin-Omni) I used the first table, which is an understanding table.
P3. "NS" whenever the text does not state the value rule for the F1 numbers, including process-level samplers (CTMC tau-leaping, Euler ODE) with no stated temperature. "U" only with an explicit statement (ancestral sampling, "no temperature scaling", "no annealing", "directly from the models") that covers the reported setting.
P4. Gaussian, simplex and embedding channels: per-step rule only; final rounding left in notes (A10).
P5. F4 "Yes" for any main-text table or figure at two or more step/NFE counts on a generated-sample metric; "Partial" only for appendix-figure-only or two-setting cases. A step sweep in which the swept quantity is a confidence threshold (EB-sampler, Fast-dLLM, Dimple) counts as a step/NFE sweep.
P6. F5 is "NA" when F4 is "No" or "NA", otherwise Stated / Co-varied / Not stated. F6 is "NA" when no guidance is coded for the F1 setting.

## Codebook ambiguities met (recorded, not resolved)

- A1. "First quantitative result in the abstract ... first row of the first main-text results table" does not say what to do when that number is a speedup (M07, M10, M12, M39, M38, M43 abstract), a likelihood perplexity or bits/dim (M03, M05, M06, M17), or when the first table is likelihood-only or a task-accuracy table with mixed likelihood/generation evaluation (M01, M04, M09, M16, M18, M35, M36). Also unclear when there is no main-text table (M21, M33, M36, M41: figures only). Policy P1 applied; a different reading changes F1 and can change F2 to F6 for these rows.
- A2. F4 "generated-sample metric": D3PM reports perplexity at several inference-step counts (Table 2, Fig 2) but it is an ELBO-based test-set number. Coded F4 = No.
- A3. F2 "U" versus "NS" for process-level samplers (CTMC tau-leaping in M02, Euler CTMC in M24, analytical sampling in M40). The sampler is stochastic by construction but no sentence states temperature 1 or no truncation. Coded NS.
- A4. M04 (MDLM): "U" rests on the section title "Efficient Ancestral Sampling" and on SAR decoding being built on it; Table 5 does not restate temperature.
- A5. Numerical precision of the Gumbel/categorical sampler (fp32 truncation lowers effective temperature) is a value-rule factor per M07 but is not in the F2 list. M06, M07, M16, M17, M18 state fp64. I did not add a code for it. M07 and M06 show the metric changes materially with it.
- A6. M09 (LLaDA): "low-confidence remasking" with greedy argmax confidence is coded A, not S, because the algorithm text says greedy and the codebook's S requires a sampled value (temperature above 0).
- A7. F3 list is text-oriented. Image-diversity metrics (Precision/Recall, CAS in M10) are not listed. Coded Yes because the paper itself calls them sample-diversity metrics.
- A8. Whether a remasking-schedule hyperparameter (M11: eta_cap and loop settings differ between the T>=L and T<L blocks of Table 1) counts as part of "value rule" for F5. Coded Stated on the basis of top-p 0.9 for all models.
- A9. M12: "greedy sampling" in the text describes the order criterion; the value-commit function is an abstract sample_fn. Coded NS.
- A10. Continuous channels: M13 (guidance by gradient updates, G), M14 (probability-flow ODE with stated defaults, U), M30 (noise term dropped, deterministic, coded A as an interpretation), M31 (argmax-projected prediction per step, A), M32 (MBR, M). No codebook rule maps these cleanly. M14 coded U on the strength of stated defaults score temperature 1.0, guidance 1.0, p 1.0.
- A11. M15 (Plaid) has a human pairwise preference study of loss weightings (Sec 4.1) but no generated-sample metric for the headline model. Coded NA.
- A12. M17 (Duo): Table 5 sampler is inferred to be ancestral (values match the ancestral entries in the sample-figure captions); Greedy-Tail (argmax on the last step) is a separate sampler in Fig 4.
- A13. M18 (BD3-LM): NFE in Table 7 differs between L=1024 and L=2048 because of length; not treated as a step sweep.
- A14. M19 (SSD-LM): the reported rows are the top-3 of a grid ranked by MAUVE, with top-p and T varying together; F4 coded Partial (two T values in the table), F5 Not stated.
- A15. M20 (Show-o): CFG scale and step count used for the FID in Table 2 are not stated in the text read.
- A16. M21 (UniDisc): Algorithm lists top-p and temperature annealing but no values; codes P and T assigned from the listing. If the codebook intends only stated values, this row would be S+G.
- A17. M22 (MMaDA) and M29 (LaViDa-O): which table is "the main task" for a unified model. See P2.
- A18. M23: Table 5 "sampling steps s" is the number of reward steps used in ParaRL training, not a decoding sweep. Coded F4 = No.
- A19. M25 (Lumina-DiMOO): text says "sample its value with the highest probability"; coded A.
- A20. Four models in the list use continuous diffusion or flow for images (M26 Transfusion, M27 BAGEL, M28 Show-o2, M46 D-DiT). The codebook is written for discrete value rules; I coded G or NS.
- A21. F6 "Stated" requires a sentence or caption; M28 and M42 have constant CFG values only in table rows or captions. Coded Stated for M42 (caption) and M28 (rows). Note M42 F5 is Not stated (no sentence on temperature or truncation in the sweep).
- A22. M33 (CANDI) and M34 (Simplax) choose a temperature per method and NFE by an entropy-matching rule. Coded F5 Co-varied. M34's range (0.84 to 1.12) includes values above 1, so "T temperature below 1" is not clearly met; coded T because a non-unit temperature is the rule.
- A23. M35 (Dream): whether Table 1 rows are likelihood- or generation-evaluated is not stated.
- A24. M36: the phrase "temperature of top-k to 0.98" is ambiguous (temperature versus k).
- A25. M37 (DiffuCoder): Table 1 and 2 numbers use the best temperature from {0.2, 0.3, 0.4} per model, so the reported value includes a per-model temperature choice on the benchmark.
- A26. M39 (Fast-dLLM): confidence is the maximum softmax probability, which suggests argmax commit; the experiments never say it. Coded NS.
- A27. M42 (UDLM): F4 Yes on two step counts in the main text (T=128, 1024) plus appendix datasets; under a strict reading it is Partial.
- A28. M43 (LaViDa): the abstract's +4.1 CIDEr and 1.92x speedup are not reproduced by Table 3(a) (differences +5.5 at 100% NFE, +3.0 at 50%).
- A29. M44 (Muddit): the sampler function S is never specified; only schedule, steps and CFG.
- A30. M45 (Dynin-Omni): "maximum predicted probability of the selected token" does not say whether the selected token is argmax or sampled. Coded NS.
- A31. M47 (Dimple): temperature 0 and top-p 0.01 are both stated; coded A+P, though top-p 0.01 is redundant under temperature 0. The Table 4 sweep uses confident decoding, which Table 1 disabled.
- A32. F0: the codebook asks for the latest version on the coding date; I recorded the cached version and made no network check. Five Exa copies carry no version string.

## Observations that bear on the earlier-coding comparison (data, not conclusions)

- Counts of my codes: F2 NS 14, U 8, NA 2; F3 Yes 15, No 30, NA 2; F4 Yes 32, Partial 3, No 10, NA 2; F5 Co-varied 2 (M33, M34), Stated 8, Not stated 25, NA 12; F6 Stated 2, Not stated 3, NA 42.
- Rows most exposed to A1 (policy-dependent F1): M03, M04, M05, M06, M07, M09, M10, M12, M16, M17, M18, M21, M33, M35, M36, M38, M39, M41, M43, M47.
- Rows where a different reading of one sentence flips F2: M04 (U vs NS), M14 (U vs NS), M21 (S+P+T+G vs S+G), M30 (A vs NS), M39 (NS vs A), M45 (NS vs A or S), M02, M24, M40 (NS vs U).
