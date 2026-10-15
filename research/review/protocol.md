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

**Version rated.** Screening, extraction and appraisal use the latest arXiv version available on
the retrieval date (HTML retrieved 2026-10-13 for the seed corpus), because that is the version
all raters can open. The published version of each included study is resolved separately
(Semantic Scholar, Crossref, OpenAlex, DBLP) and recorded with its venue and DOI; the bibliography
cites the published version where one exists. Differences between a preprint and its published
version are a stated limitation; paywalled published versions are obtained through the authors'
institutional access when a pooled estimate or a quoted number depends on them.

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
(Entries below.)
- 2026-10-15 (D0020; census codebook v1.2 B-4, B-6). Eligibility I1(b): "unified" means one model
  (shared weights or one jointly trained system), not a pipeline of separately trained models;
  "another modality" means image, video, audio or speech, or 3D. A unified model whose text is
  autoregressive and whose diffusion or flow component generates one of these is eligible. Robot
  actions, molecules and other non-text domains with autoregressive text are X1. X1 is widened
  from "non-text diffusion only" to every diffusion model whose diffusion component produces no
  natural-language text or code and is not covered by I1(b). Made after the random-sample census
  coding; applies to adjudication of that sample and to all later coding.

- 2026-10-15 (D0026; the pilot criterion of section 3 was not met). Made before any screening decision on the records the
  searches found, and before the freeze rule of this file's header is applied. **Strings S1 and S2 are replaced as the primary
  search by the revised strings S1' and S2' below; S1 and S2 stay in the logs and are run a second time on the subscription
  databases.** Eligibility (I1 to I4, X1 to X8, and the amendment of 2026-10-15 under D0020 above) is unchanged.
  *Reason.* On the free sources the original strings retrieved 27 of the 28 'Multimodal DLMs' seed records, 41 of
  the random 50 others and 470 of the 540 seed entries with an arXiv ID (539 distinct IDs); every one of the
  70 entries not retrieved fails S1 and S2 on its own title and abstract, so the strings, not the sources, limit
  recall. The revision follows the pilot rule of section 3 (missed records are used to revise the strings): the vocabulary comes from
  the abstracts of the missed entries (`dLLM`, `diffusion-based LLM`, `large language diffusion model`; `discrete diffusion` or
  `masked diffusion` without a language word; diffusion drafters for speculative decoding; continuous and latent diffusion language
  models; text-generation and NLP-task diffusion models; vision-language-action models with discrete diffusion). Three rounds were
  run and are recorded in `corpus/string-revision-2026-10-15.json` and the report `corpus/search-v2-report-2026-10-15.md`.
  *Recall* on title and abstract, tested locally on the seed entries: S1/S2 453/540, MM28 26/28, random 50
  40/50; S1'/S2' 525/540, MM28 28/28, random 50 47/50. The 15 entries not captured are
  listed with reasons in the report; those in the random 50 are two image-generation foundation papers (DDPM-type, no text) and
  one protein-design paper, all outside I1 (X1). *Precision proxy*, first estimate: of a random 200 (seed 20261017) of the
  539 records of the 14,794 collected earlier that S1'/S2' add, 67 look in scope from the title, 46 are unclear and 87
  are not (labels by the proposing agent, titles only). Second estimate, on what the databases actually returned (stratified
  sample of the screening queue, 40 per tier, seed 20261018): an estimated 12% of the 6,376 queued records look in scope
  and 18% in scope or unclear; the broad branches B and C and the records a database returned that match no string locally carry most of the noise
  (table in the report, 2.4). Apart from writing five abbreviations as exact tokens after the first database run (below), the strings were not changed after
  the three local rounds, because D0026 allowed three; the queue carries a tier per record so that screening can be ordered or sampled by tier.
  *S1' and S2' (verbatim; AND binds tighter than OR; a trailing `*` is a word-prefix wildcard; `NOT (...)` excludes any listed word;
  title, abstract and keywords; 2021-01-01 to the search date; English):*

  S1' =
  ```
  ("diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms) OR ((("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) OR (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation))) OR (("absorbing state" AND (language OR text OR token* OR "language model*")) OR ("any-order" AND (language OR text OR token* OR "language model*")) OR "non-autoregressive language model*" OR ("non-autoregressive" AND diffusion AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*))) OR (diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) OR (diffusion AND ("language model*" OR llm*) AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation))
  ```
  S2' =
  ```
  (("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) OR (("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms))
  ```
  The biochemical exclusion (`protein*`, `molecul*`, ..., `recommend*`) and the visual exclusion (`image*`, `video*`, ...) implement X1
  and apply only where no language word is required (the second branch of A2) or in the broad branches (A3 with
  non-autoregressive, B, C); a paper with a language word in the abstract is not removed by them in A2. Search terms such as `named
  entity` and `sentiment` in B reach NLP-task diffusion papers that Awesome-DLMs lists under Applications; whether they meet I1 (output
  includes natural-language text) or fall under X2 or X7 is decided at full text, not by the search. Each source was run part by part
  (A1, A2, A3, B, C; M, VLA); the union of the parts is the string; the adapted forms are in `search-log.jsonl`. `dllm`, `dllms`, `dmllm`,
  `dmllms`, `dvlm`, `dvlms`, `vla`, `vlas`, `mllm`, `mllms` are exact tokens, not prefixes (`dllm*` matched DLLME, dispersive liquid-liquid
  microextraction). In arXiv wildcard terms were written as stem forms because arXiv switches stemming off for a wildcard term.
  *Consequences (D0026).* Sources rerun with S1'/S2': arXiv, Semantic Scholar bulk, OpenReview (search by term, boolean string applied locally),
  ACL Anthology (local); OpenAlex partly (free daily credits exhausted: S1' parts A1 and A2 incomplete, A3, B, C, M, VLA not run; resume command in
  the report); DBLP not searched; the six subscription databases wait for the user (`subscription-search-sheet.md`: S1'/S2' first, S1/S2 second
  run). Snowball records enter title-and-abstract screening only if their title and abstract match S1, S2, S1' or S2'; the others
  (12,952) are reported in the flow diagram as records marked ineligible by an automation tool (string filter, D0026).
