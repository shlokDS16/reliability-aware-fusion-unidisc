# Feasibility inventory, stage 1: keyword signals (2026-10-13)

Source: `tools/table_inventory.py` over the 540 arXiv records of
`corpus/awesome-dlms@194aa6bd.jsonl`; arXiv HTML retrieved for 535. Raw output:
`feasibility/captions.jsonl`. **Evidence level E1**: a flag means a table or figure caption
matched a keyword pattern. It says where to read, not what the paper shows, and it does not yet
say whether a contrast is matched or reports variance.

| Signal (papers with at least one flagged caption) | Papers | Share of 535 |
|---|---|---|
| ablation or component contrast | 401 | 75% |
| sweep over denoising or sampling steps | 268 | 50% |
| comparison involving autoregressive models | 240 | 45% |
| remasking contrast | 53 | 10% |
| understanding-generation synergy or joint training | 18 | 3% |
| text mentions seeds, standard deviation or plus-minus | 330 | 62% |
| text mentions confidence intervals, error bars or significance | 110 | 21% |

By README section, step-sweep captions: Inference Optimization 99 of 164, Discrete DLMs 75 of 156,
Training Strategies 31 of 56, Continuous DLMs 28 of 51, Multimodal DLMs 17 of 28. Synergy captions:
9 of 28 multimodal papers, 18 in total.

Corpus by first-version year (arXiv metadata now complete for all 540): 2022 or earlier 19,
2023 39, 2024 46, 2025 193, 2026 243; 32 records are not on arXiv.

## What this suggests (to be confirmed by reading)

- **RQ4 (quality against steps) is the question most likely to support pooling.** Half the corpus
  has a step-sweep caption. A dose-response synthesis of within-paper step sweeps looks feasible,
  which is the evidence base the step-scaling candidate (CD in debate round 3) needs.
- **RQ5 (synergy) will probably not reach the pooling threshold inside this corpus.** 18 papers
  carry a synergy-type caption. Unified models that are not diffusion-based sit outside this list,
  so the database search decides this, but the expectation Codex stated in round 4 looks right.
- **RQ6 has a visible signal.** Intervals or significance are mentioned in about a fifth of
  papers, variation in about three fifths. The gap between the two is a candidate headline for the
  reporting audit once measured properly with the quality appraisal form.
- Remasking (53 papers) may support a small pooled contrast.

## Known weaknesses of this pass

- The "code repository" text flag fired on 534 of 535 pages and is discarded: it almost certainly
  matches links in the arXiv HTML page furniture, not the paper.
- The variance flag can fire on a passing mention of a random seed.
- Caption keywords miss contrasts described only in running text and over-count generic
  "effect of" captions.

## Stage 2 (next)

Stratified sample of 60 flagged papers (30 with step sweeps across model families, 15 remasking,
all 18 synergy papers less overlap): paper-reader extracts each sweep or contrast with outcome,
task, sampler, what was held fixed and whether variance is reported, then counts how many meet the
comparability rules in protocol section 7.
