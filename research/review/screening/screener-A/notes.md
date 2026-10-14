```yaml
agent: general-purpose (acting as screener A)
date: 2026-10-14
brief: Title-and-abstract screening of 1453 records with criteria-v1.md, blind to screener B. PARTIAL RUN, stopped at a batch boundary near the token limit.
sources_examined: [research/review/screening/criteria-v1.md, research/review/screening/batches/batch-01.jsonl .. batch-06.jsonl]
coverage: batches 01-06 (R0001-R0600) screened from title and abstract only. Batches 07-15 (R0601-R1453) NOT screened; to be dispatched to a fresh screener. Nothing under screener-B/ was opened.
claims: []
competing_explanations: []
unknowns: [decisions for R0601-R1453]
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

## Counts (batches 01-06, 600 records)

| Batch | include | exclude | unclear |
|---|---|---|---|
| 01 | 56 | 31 | 13 |
| 02 | 57 | 34 | 9 |
| 03 | 69 | 22 | 9 |
| 04 | 73 | 19 | 8 |
| 05 | 92 | 6 | 2 |
| 06 | 74 | 15 | 11 |
| Total | 421 | 127 | 52 |

Exclusion codes: X0 = 15, X1 = 69, X2 = 30, X3 = 13, X4 = 0, X7 = 0, X8 = 0. Checks run: every file has one line per batch sid in batch order; every exclude has a code and no include/unclear has one; every reason is at most 15 words.

## Rules I applied to ambiguous cases (so the second screener's differences can be traced)

1. **X1 versus X2.** Non-text output with text explicitly named as a conditioning input (text-to-image, text-to-motion, text-to-speech, text-driven editing, language-conditioned robot actions) was coded X2. Non-text output with no text input mentioned (images, video, protein, molecule, graph, audio, 3D) was coded X1. The criteria give X1 and X2 overlapping scope, so another screener may code these differently while still agreeing on exclude.
2. **X8 (date) not used.** The date cannot be read from title and abstract, and outside knowledge was not allowed. Records that are clearly pre-2021 by common knowledge (R0001 to R0005, diffusion for images) were excluded as X1 instead.
3. **Unified-model exception (frozen LLM plus diffusion image generator).** Included when the abstract presents the system as unified understanding and generation (e.g. R0067 NExT-GPT, R0081 GPT4Video, R0227 MetaQueries, R0267 OpenUni, R0458 VUGEN), even if the LLM is frozen. Coded X2 or unclear when the abstract only describes a diffusion generator conditioned on a VLM without that framing (R0474 X2; R0556, R0052 unclear).
4. **Autoregressive-only or non-diffusion models that merely compare against diffusion LMs** were coded X0 (e.g. R0201, R0233, R0238, R0319, R0427, R0538, R0542, R0567, R0589). R0202 was left unclear because it analyses the diffusion LM conditional-generation gap.
5. **Discrete-diffusion theory papers with no text stated** (R0095, R0224, R0274, R0375, R0390, R0505, R0529, R0371, R0573) were marked unclear; theory papers that name diffusion language models explicitly (R0203, R0259, R0516, R0587) were included.
6. **Diffusion over non-text discrete sequences described as a "diffusion language model"** (SMILES, chemical formulas: R0069, R0098, R0157, R0348) were marked unclear; the same data without the language-model framing (R0187, R0182, R0308) and proteins (all) were coded X1.
7. **NLP tasks where diffusion produces spans, representations or labels rather than generated text** (R0043 NER, R0101 aspect extraction, R0107 triple extraction, R0036 extractive summarization, R0062 keyphrases, R0285 classification, R0090 text classification, R0185 topic model) were marked unclear. Tasks where diffusion decodes a text string (ASR, scene-text recognition, captioning, equation generation) were included.
8. **Semantic-ID recommendation and robot or driving trajectory models built on masked diffusion or discrete flow** (R0495, R0520, R0541, R0364, R0383, R0550, R0557, R0355) were marked unclear because the output is not natural-language text, although the backbones are often diffusion LMs.

## Criteria ambiguities met (criteria text not changed)

- I1 says "whose output includes natural-language text or code", which does not say whether a model whose text is only a classification label, a span, or a recognised string counts. See rule 7.
- X1 and X2 overlap for any non-text generation with a text prompt; the "exclude with one code" instruction does not say which wins.
- I4 and X8 cannot be applied from title and abstract for records whose dates are not in the abstract.
- "Unified model ... using a diffusion, masked-generative or discrete-flow component" does not say whether the diffusion part must be involved in the understanding-and-generation interface, or whether a diffusion image decoder attached to an autoregressive LLM qualifies (rule 3).
- "Primary study with a method, theory or empirical result" does not clearly cover software packages (R0575), a thesis evaluation (R0306, included), or dataset-free position-like pieces (R0584, included as analysis).
- The note on VAEs, GANs and flows says "X1 if non-text, else X4 only if there is no diffusion at all (use code X0)"; this is internally awkward, and I used X0 for text-capable models with no diffusion component.
- Possible duplicates in the screening set: R0343 and R0600 have the same abstract text apart from a link (both included). The set may need a dedup check.

## Concerns

- Run is partial (6 of 15 batches). Batches 07-15 remain.
- Unclear rate is 8.7% in this part; the share of unclear records in later batches is expected to be lower, since later records are mostly diffusion LLM work.
- Decisions on rules 1, 3 and 5 to 8 depend on judgement calls and are the most likely places for disagreement with screener B.
