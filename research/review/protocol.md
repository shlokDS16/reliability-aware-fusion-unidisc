# Review protocol (DRAFT v0.1, 2026-10-13; not frozen)

Follows PRISMA 2020 for reporting and Kitchenham and Charters (2007) for systematic reviews in
computing. Built to meet the professor's requirements of 2026-10-13: exact search dates and
database-specific strings, screening process, full-text exclusion reasons, reviewer agreement,
a quality appraisal of every included study, tables with consistent categories, and research
questions answered from evidence. The emphasis is a **critical** review: each section judges how
well claims are supported, it does not only describe them.

Freeze rule: this file is frozen (git tag `protocol-v1`) after statistician and red-team sign it
and before any screening decision is recorded. Later changes are listed in section 10.

## 1. Research questions (each gets its own results subsection, evidence table and verdict)

| ID | Question | Evidence used | Synthesis |
|---|---|---|---|
| RQ1 | Which formulations of diffusion language models and unified multimodal diffusion models exist, and what separates them (state space, forward process, objective, parameterisation, sampler)? | all included studies | taxonomy in one notation; counts per class and year |
| RQ2 | How do these models compare with autoregressive models, and under which protocols were the comparisons made? | studies reporting a comparison with an autoregressive baseline | protocol-comparability table; pooled only where task, metric and budget match |
| RQ3 | What do training strategies contribute (pretraining recipe, instruction or reasoning fine-tuning, reinforcement-learning post-training, distillation)? | within-paper ablations | matched-contrast synthesis |
| RQ4 | How does inference trade quality against compute (denoising steps, unmasking order, remasking, caching, parallel decoding)? | within-paper step sweeps and on/off contrasts | dose-response curves; matched-contrast synthesis |
| RQ5 | In unified multimodal models, what evidence supports, limits or contradicts understanding-generation synergy? | task-removal and shared-versus-decoupled ablations; synergy benchmarks | census of claims against the ablation that supports them; pooled only if enough contrasts |
| RQ6 | How rigorous is the evidence base (reporting, reproducibility, statistics, agreement between a paper's claims and its own tables)? | quality appraisal of every included study | appraisal table, distributions by year and venue type |

## 2. Eligibility

Include a record if all hold: (I1) it proposes, analyses, evaluates or benchmarks a diffusion model
whose output includes natural-language text, in discrete or continuous state space, or a unified
model that both understands and generates across text and at least one other modality using a
diffusion, masked-generative or discrete-flow component; (I2) primary study with a method,
theory or empirical result; (I3) full text available in English; (I4) first public version between
2021-01-01 and the search date.

Full-text exclusion reasons (one code per excluded record, reported as counts in the flow diagram):

| Code | Reason |
|---|---|
| X1 | diffusion for images, audio or video only, with no text generation or unified understanding |
| X2 | text is used only as a conditioning input |
| X3 | secondary study (survey, tutorial, position); kept in a separate list for positioning |
| X4 | no method, theory or empirical result (abstract-only, demo, blog) |
| X5 | duplicate or superseded version of an included record |
| X6 | full text unavailable after eGateway attempt |
| X7 | application paper that uses an existing model unchanged and reports no model-level finding |
| X8 | outside the date window or not in English |

## 3. Information sources and search strings

Every search is logged in `corpus/search-log.jsonl` with database, exact string, filters, date and
time of execution, number of hits, and the export file with its SHA-256. Strings are adapted to
each database's syntax; the adapted form is what is logged and printed in the supplement.

| Source | Access | Run by |
|---|---|---|
| Awesome-DLMs curated list, commit 194aa6bd (2026-10-02) | public | done 2026-10-13: 572 records |
| arXiv (cs.CL, cs.LG, cs.CV, cs.AI, stat.ML) | API | agent |
| OpenReview (ICLR, NeurIPS, ICML, TMLR) | API | agent |
| ACL Anthology | public | agent |
| Semantic Scholar, OpenAlex, DBLP | API | agent |
| Scopus, Web of Science | VIT eGateway | **user** (export CSV or RIS) |
| IEEE Xplore, ACM Digital Library, SpringerLink, ScienceDirect | VIT eGateway | **user** |
| Backward and forward citation snowballing from included studies | APIs | agent |

Core strings (title, abstract, keywords):

- **S1, language:** ("diffusion language model*" OR "discrete diffusion" OR "masked diffusion" OR
  "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR
  "diffusion large language model*" OR "text diffusion" OR "non-autoregressive" AND diffusion)
  AND (language OR text OR token* OR "language model*")
- **S2, unified multimodal:** ("unified multimodal" OR "unified understanding and generation" OR
  "understanding and generation" OR "any-to-any") AND (diffusion OR "masked generative" OR
  "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")

Filters: 2021-01-01 to search date; English. Pilot: both strings must retrieve all 28 records of
the Awesome-DLMs "Multimodal DLMs" section and a random 50 of its other records; missed records
are used to revise the strings before the logged run.

## 4. Selection process and reviewer agreement

1. Deduplicate on arXiv ID, DOI, OpenReview ID, then normalised title.
2. **Title and abstract screening** by two independent screeners with the same written criteria:
   screener A (Claude agent, fixed prompt, version recorded) and screener B (Codex, GPT, fixed
   prompt, version recorded). Neither sees the other's decision.
3. **Human validation.** A human author independently screens a random 15 percent sample
   (at least 100 records). Reported: Cohen's kappa for A against B, and for each against the human,
   with the confusion tables. If either machine screener has kappa below 0.70 against the human,
   its criteria prompt is revised and the whole stage is rerun.
4. Disagreements between A and B are resolved by a human author; the count is reported.
5. **Full-text screening** repeats steps 2 to 4 and assigns an exclusion code from section 2.
6. PRISMA 2020 flow diagram generated from the logs by script.

The use of language models as screeners is described in the Methods section in full, as ACM's
authorship policy requires. They are not presented as human reviewers.

## 5. Data extraction (one form, fixed categories)

Per study: bibliographic (IDs, first-version date, venue status); **study type** {method, theory,
analysis, benchmark, system}; **modality** {text, text+image, text+other}; **state space**
{discrete-absorbing, discrete-uniform, discrete-flow, continuous-embedding, continuous-latent,
hybrid}; **task family** {language modelling, reasoning, code, understanding, text-to-image,
editing, other}; model size; training data and compute; sampler and number of function
evaluations; every reported headline number with **metric, dataset, split, protocol notes**;
every within-paper contrast (what changed, what was held fixed, both values, variance if given);
claims made in the abstract; limitations stated. All tables in the paper are generated from these
fields, so categories, metrics and modalities are identical across tables.

Extraction is done by one agent and verified by a second reader on a random 10 percent sample plus
every study that enters a pooled estimate; the field-level error rate is reported.

## 6. Quality appraisal (every included study; table in the supplement, summary in the paper)

Scored 0 (absent), 1 (partial), 2 (met), with the evidence location recorded:

| Item | Criterion |
|---|---|
| QA1 | code released and usable (repository exists, commit or release identifiable) |
| QA2 | model weights or data needed to reproduce the main result available |
| QA3 | evaluation protocol fully specified (prompts, decoding steps, sampler, hardware) |
| QA4 | variation reported (multiple seeds or runs) |
| QA5 | uncertainty quantified (intervals or tests) for the main comparison |
| QA6 | baselines compared at matched or reported compute and parameter budget |
| QA7 | an ablation isolates the component the paper credits |
| QA8 | abstract and introduction claims agree with the paper's own tables |
| QA9 | limitations and failure cases stated |
| QA10 | peer-review status (recorded, not scored) |

**Claim evaluability (added 2026-10-14, direction approved by the authors).** In addition to
QA1 to QA9, each study's primary claim is typed and scored against its minimum evaluability
criterion with `evaluability-rubric.md`. This carries three pre-registered hypotheses, analysed
separately: (E1) for each scored claim type, fewer than half of claims meet their criterion;
(E2) the share meeting it does not rise by more than 10 percentage points from the earliest to the
latest publication-year tercile, nor differ by more than 10 points between peer-reviewed and
preprint-only studies; (E3) in studies that report both a headline comparison and a controlled
comparison on the same outcome, the controlled effect is smaller in more than half of them.
The rubric is adopted only if two independent raters reach kappa of at least 0.60 on claim type
and weighted kappa of at least 0.60 on the criterion in the reliability sample
(`reliability/`, 40 papers); otherwise it is revised and retested on a fresh sample.

Appraisal by two raters as in section 4, weighted kappa reported. Scores are never used to exclude
a study; they are used for sensitivity analysis (results with and without low-scoring studies).

## 7. Synthesis

- Narrative synthesis structured by RQ, each ending with a verdict: well supported, mixed,
  weakly supported, or untested, with the counts behind it.
- **Quantitative synthesis is conditional.** A question is pooled only if at least 8 matched
  within-paper contrasts from at least 5 independent groups share task family and metric. Effect
  measure: paired difference in the paper's metric, standardised within benchmark; random-effects
  model with study as the cluster; heterogeneity (tau squared, I squared) and prediction interval
  reported; small-study and reporting bias examined by funnel asymmetry where at least 10 contrasts
  exist. If no question meets the threshold, the paper is titled a systematic review without
  "meta-analysis" and reports vote counts with their limits.
- Feasibility inventory (before freezing): count candidate contrasts and step sweeps per question
  on the 28 multimodal records plus a stratified sample of 40 others.

## 8. Positioning against existing reviews (kept in a separate table)

Closest: "Discrete Diffusion in Large Language and Multimodal Models: A Survey" (arXiv 2506.13759,
v5 dated 19 Sep 2025) and "A Survey on Diffusion Language Models" (arXiv 2508.10875). Neither text
contains a search protocol, research questions, a quality appraisal or pooled estimates (term
search of the v5 full text on 2026-10-13: zero hits for PRISMA, inclusion criteria, research
question, quality assessment). The full landscape is in `survey-landscape.md`.

## 9. Open decisions for the authors

1. Title, decided 2026-10-13 under the authors' delegation (D0007): **"Diffusion Language Models
   and Unified Multimodal Generation: A Critical Systematic Review of Discrete and Continuous
   Approaches"**. It names discrete diffusion as the professor asked, matches eligibility rule I1
   (both state spaces), and separates the paper from arXiv 2506.13759, whose abstract describes a
   "systematic survey" of discrete diffusion language and multimodal models but has no protocol.
   "and Meta-Analysis" is added back only if section 7's pooling threshold is met.
   The conjecture is presented in its own section with a "status and scope" paragraph, on the
   pattern of the Artificial Intelligence Review sample (its Sect. 8.1): what is conjectured, what
   published evidence bears on it, what would refute it, and that the experimental test is a
   separate follow-up article.
2. Who is the human screener for the validation sample (about 100 abstracts, 2 to 3 hours).
3. Whether to register the protocol publicly (OSF) before screening; it strengthens the paper.

## 10. Amendments
None yet.
