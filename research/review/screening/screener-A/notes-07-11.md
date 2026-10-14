```yaml
agent: general-purpose (acting as screener A, continuation instance)
date: 2026-10-14
brief: Title-and-abstract screening of batches 07-11 (R0601-R1100) with criteria-v1.md, following the rules in screener-A/notes.md, blind to screener B.
sources_examined: [research/CONTRACT.md, research/review/screening/criteria-v1.md, research/review/screening/screener-A/notes.md, screener-A/batch-01.jsonl, screener-A/batch-05.jsonl, batches/batch-01.jsonl, batches/batch-05.jsonl, batches/batch-07.jsonl .. batch-11.jsonl]
coverage: batches 07-11 (R0601-R1100) screened from title and abstract only; the visible abstract was cut at 1100 characters in the first reading, and the remainder was read for records where the cut text could change the decision (R0645, R0683, R0703, R0857, R0874, R0878, R0969, R0970, R0974, R1070, R1065, R1083, R1087, R1097). Batches 12-15 not screened. Nothing under screener-B/ or any file outside the brief was opened.
claims: []
competing_explanations: []
unknowns: [decisions for R1101-R1453]
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

## Batches 07-11

Every line was decided by reading the record. A helper script only converted my per-record decisions (kept in the scratchpad as sid|decision|code|reason text) into JSONL and checked: one line per input sid in batch order, an exclude has a code and no other decision has one, every reason has at most 15 words.

### Counts (500 records)

| Batch | include | exclude | unclear |
|---|---|---|---|
| 07 (R0601-R0700) | 86 | 9 | 5 |
| 08 (R0701-R0800) | 71 | 14 | 15 |
| 09 (R0801-R0900) | 78 | 14 | 8 |
| 10 (R0901-R1000) | 78 | 14 | 8 |
| 11 (R1001-R1100) | 83 | 10 | 7 |
| Total | 396 | 61 | 43 |

Exclusion codes: X0 = 5, X1 = 32, X2 = 17, X3 = 7, X4 = 0, X7 = 0, X8 = 0. Unclear rate is 8.6%, similar to batches 01-06 (8.7%).

Unclear records, by batch:
- 07: R0607, R0611, R0634, R0645, R0697
- 08: R0705, R0708, R0710, R0712, R0719, R0731, R0733, R0734, R0746, R0774, R0779, R0784, R0795, R0796, R0797
- 09: R0808, R0811, R0816, R0826, R0834, R0845, R0855, R0894
- 10: R0915, R0924, R0939, R0950, R0965, R0969, R0975, R0993
- 11: R1011, R1035, R1051, R1065, R1070, R1082, R1097

### How the earlier rules were applied

Rule numbers refer to `notes.md`.
- Rule 1 (X1 versus X2): non-text output with text named as an input (text-to-image, text-to-speech, text-to-motion, text-guided editing, language-driven control) is X2; non-text output without a named text input (video, single-cell, EEG, protein, DNA, CAD, anomaly detection, pose, compression) is X1. Examples: R0801, R0803, R0815, R0910, R0966, R1050, R1057 are X2; R0720, R0804, R0869, R0905, R1013 are X1.
- Rule 3 (frozen LLM plus diffusion decoder framed as unified understanding and generation): included, for example R0727, R0763, R0769, R0843, R0882, R0884, R0885, R0995, R1072, R1073. Without that framing: X2 (R0693, R0963, R0917).
- Rule 4 (autoregressive or non-diffusion models): X0 for R0748, R0902, R1033, R1045, R1093. R0902 is a unified model built on autoregressive normalizing flows, which the criteria do not list as a diffusion, masked-generative or discrete-flow component.
- Rule 5 (discrete-diffusion theory with no text stated): unclear (R0634, R0731, R0795, R0797, R0950, R0965, R1011, R1082). Theory papers that state language models or report text results were included (R0683, R0726, R0800, R0981, R0982).
- Rule 6 (non-text sequences with "language model" framing): molecules, material tokens and GPS segments with diffusion-LM framing are unclear (R0816, R0845, R0855, R0915). Protein, DNA, antibody and CAD data without that framing are X1 (R0747, R0767, R0876, R0891, R0983, R0883, R0887).
- Rule 7 (output is a label, span, score or mask, not generated text): unclear for R0705 and R0894 (retrieval and reranking), R0834 (prompt-pruning mask), R0924 (evaluation score), R0939 (cell masks), R0993 (action labels and timestamps), R0811 (activation signals). Recognised or transcribed strings were included (R0665 handwritten math, R0985 lip-reading transcripts, R0715 OCR, R0776 text content in scene-text restoration).
- Rule 8 (robot, driving, trajectory and action models on masked diffusion): unclear (R0708, R0808, R0915, R1035).

### Judgement calls beyond notes.md (most likely places for disagreement with screener B)

1. Applications that use a diffusion LM as a component without changing it, where a model-level finding is unclear (X7 versus include): marked unclear for R0697 (hallucination detection by reconstruction), R0710 (adversarial training samples), R0719 (prompt optimisation), R0834. Included when the abstract proposes a decoding, training or attack method specific to the diffusion LM or reports model-level findings: R1061, R1016, R0951, R1052, R0878.
2. Software and framework papers: R0734 (dLLM library) and R0826 (DARE post-training framework) are unclear (primary-study status). R1051 (a serving system for composite models, with diffusion heads only one case) is unclear. Serving and inference-system papers specific to diffusion LLMs (R0643, R0959, R1055, R1080, R1099) were included as system methods with measured results.
3. Any-order autoregressive models that inherit diffusion flexibility (R0607, R0712) are unclear, not X0, because the abstracts frame them as replacements for masked diffusion.
4. Unified-model records whose diffusion part is only image generation for a text-to-image task: R0774 (text-to-image acceleration for diffusion LLMs) and R0796 (training-free image editing with diffusion LLMs) are unclear because text may be only a condition; R0779 (acceleration of "native unified models") is unclear because the abstract does not name a diffusion component.
5. Puzzle and non-linguistic reasoning tasks on masked diffusion: R0784 (Sudoku, Countdown) and R1097 (Sudoku, QM9) are unclear; R0870 and R0986 name masked diffusion language models explicitly and were included.
6. R1011 and R1070 are unclear because the abstract does not say the sequences are text.
7. R0898 has no abstract. The title says "Comparative Survey", so I coded X3 from the title. A reader who treats a missing abstract as grounds for unclear would disagree; the full text would settle it.
8. R0822 (a technical note on evaluating diffusion LMs) was included because it contains a derivation and proposed metrics, not coded as a position paper.
9. R0746 (LLM quantisation that names diffusion LLMs as a target) is unclear because the abstract does not say diffusion LLMs were evaluated.

### Possible duplicates in the screening set

- R0931 and R0713 have the same title and abstract text ("Discrete Stochastic Localization for Non-autoregressive Generation"); both included. Deduplication appears to have missed this pair (same pattern as R0343 and R0600 in batches 01-06).
- R0734 ("dLLM: Simple Diffusion Language Modeling") and R0826 ("DARE") are distinct records. R0953 and R0899 are distinct as well.

### Criteria ambiguities met (criteria text not changed)

- The same ambiguities listed in `notes.md` came up again: X1 versus X2 overlap; no rule for records whose output is a label, mask or score (rule 7); no rule for software or serving-system papers; and no rule for records that use a diffusion LM as an unchanged component but also propose a method around it (X7 wording turns on "no model-level finding", which an abstract rarely settles).
- I4 (date) was not used for any decision; no record in these batches is clearly pre-2021.

### Concerns

- Decisions in judgement calls 1 to 4 are the most likely places for disagreement with screener B; the unclear list above is the intended hand-off to full-text screening for those.
- Abstracts were read to 1100 characters in the first pass; where the truncated remainder could matter the full text of the abstract was read (listed under coverage). Other records were decided on the first 1100 characters plus the title.
