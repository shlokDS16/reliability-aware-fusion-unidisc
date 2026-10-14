# Census codebook v1: value rules and reporting in headline results (2026-10-14)

Purpose: operational definitions for the census in framework-v2 section D2, so that two
extractors code the same papers independently and agreement can be reported before
reconciliation (Codex round 4; protocol section 5). Version 1 is frozen before the second coding
starts; any change after that is an amendment with a date and reason.

Unit: one paper (the primary arXiv version, latest version available on the coding date; record
the version). One row per paper.

## Fields

**F0 version read.** arXiv version string, e.g. v3.

**F1 headline result.** The first quantitative result for the paper's own main generative method
that appears in the abstract; if the abstract has none, the first row of the first main-text
results table that reports the paper's own method on its main task. Record: task, metric, value,
location (abstract, or table number). If the paper reports no generated-sample metric for its own
method (theory only, or only likelihood bounds such as perplexity from the ELBO), code F1 = NA
and F2 to F6 = NA.

**F2 value rule used for F1.** All that apply, from the paper's text (main text and appendix;
not code):
- A argmax or greedy commit (temperature 0, "deterministic");
- T temperature below 1 (state the value);
- P top-p, top-k or nucleus truncation;
- S sample-then-filter: values are sampled and positions chosen by a score of the sampled value
  (e.g. "confidence of the sampled token", MaskGIT-style, LLaDA "low-confidence remasking" at
  temperature above 0);
- G guidance: classifier-free, classifier or reward guidance at sampling time (state the scale);
- M sequence-level selection: best-of-N, minimum Bayes risk, reranking;
- U plain: ancestral or rank-then-sample with values sampled at temperature 1, no truncation,
  no guidance (code U only if the paper states these settings or states "standard ancestral
  sampling" for the reported numbers);
- NS not stated: the paper does not state the value rule for F1.
Gaussian or embedding channels: code the per-step rule; the final rounding (argmax or nearest
embedding) is recorded in a note, not as A.

**F3 entropy or diversity reported for F1.** Yes if the same table or figure as F1, or a table or
figure that the text explicitly pairs with F1, reports an entropy (unigram, sentence), distinct-n,
self-BLEU, MAUVE, or pass@k with k > 1 for the same setting. Otherwise No. NA if F1 is NA.

**F4 step sweep.** Yes if any table or figure reports the paper's own method at two or more step
counts (or tokens per step, or NFE) on a generated-sample metric. Partial if only two settings or
only in an appendix figure without numbers. No otherwise.

**F5 value rule held fixed in the sweep.** Stated: the text or caption states that the value rule
(temperature, truncation, selection rule) is the same across the sweep. Co-varied: the text states
that it changes with steps. Not stated. NA if F4 = No.

**F6 guidance held fixed in the sweep.** Stated / Co-varied / Not stated / NA (no guidance or no
sweep).

## Rules

- Code from the text only (main text and appendix). Do not open code repositories; a separate
  E3 pass may do so later.
- When the paper is ambiguous, choose the conservative code (NS or Not stated) and quote the
  sentence (at most 15 words) in a notes field.
- Record the location (section, table, figure) for every non-NA code.
- Do not consult any earlier coding of these papers in this repository.
