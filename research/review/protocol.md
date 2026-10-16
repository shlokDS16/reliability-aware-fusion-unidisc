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

- 2026-10-15 (D0027; screening-queue precision). Made before any screening decision on the records the searches found. **The strings S1' and S2'
  are replaced as the primary search by S1'' and S2'' below** (S1' and S2' with exclusions and extra requirements; every part is a subset of the same
  part of S1' / S2', so nothing is found that S1' / S2' would not find). S1 and S2 stay the second run on the subscription databases (D0026); S1' and S2'
  stay as the run for the three databases whose term budgets cannot hold S1'' / S2'' (IEEE Xplore, SpringerLink, ScienceDirect), S1'' / S2'' being applied
  locally to those exports. Eligibility (I1 to I4, X1 to X8, the amendments of 2026-10-15 under D0020 and D0026) is unchanged. No new database search was run.
  *Reason.* On what the databases returned for S1' and S2' (stratified sample of the screening queue, 40 titles per tier), an estimated 12% of the 6,376 queued
  records looked in scope; tiers T3 (only the broad branches B and C) and T5 (records that match no string locally) were 69% of the queue at about 2.5% in scope. The
  noise was diffusion of innovations and information, diffusion MRI, diffusion and heat equations, speech, music and time-series diffusion models, Stable
  Diffusion and generic generative-AI surveys.
  *Changes (round 4, precision only; counts in `corpus/string-revision-round4-2026-10-15.json` and report section 12).* (1) exclusion lists for the observed noise (diffusion of
  innovation, information, technology; social networks; diffusion MRI; diffusion, heat, fluid and wave equations, epidemics; microextraction; disc diffusion; Stable
  Diffusion; speech, music, motion, time-series and similar non-text outputs and a few technique words), each term kept only if it removed no seed entry; (2) in B and C
  `diffusion` must occur as a model (`diffusion model*`, `diffusion-based`, `denoising`, `using diffusion`, `flow matching`, ...), which removes the dissemination sense;
  (3) the no-context branch of A2 keeps `masked diffusion`, `discrete diffusion` and `discrete flow matching` only; with a language word, `discrete flow*` needs `diffusion` and
  `discrete state-space*` a diffusion, generative or flow-matching word; (4) `absorbing state` and `any-order` need a language-model, autoregressive, diffusion or masked word
  besides the language word; (5) in S2'' the branch M needs a language word and the VLA branch no longer accepts plain `diffusion-based`.
  *Language-word requirement as asked, and why it was relaxed.* Required alone in the no-context branch of A2 it gives 523/540 (seeds lost: 2509.13866, 2608.10615); in B it
  gives 520/540 (five NLP-task seeds lost); in C it removes only 110 records. The acceptance rule (525/540, MM28 28/28, R50 47/50) is not met by the first two, so the no-context
  branch is restricted by its own terms and the exclusion lists, and B and C by the diffusion-as-a-model requirement and the exclusion lists; the language word is required in M.
  *Recall* on title and abstract, tested locally on the seed entries: S1''/S2'' 525/540, MM28 28/28, random 50 47/50, equal to S1'/S2' (525/540,
  28/28, 47/50); the same 15 entries are not captured (listed in the report, 2.5). Of the 19,328 new records, 0 match S1''/S2'' and not S1'/S2'.
  *Precision*, measured on the same stratified real-result design as in D0026 with a new seed (20261019; 40 titles per tier of the 1,842 records that pass S1''/S2'';
  labels by the proposing agent, titles only, in-sample): 647 records look in scope (35.1%; stratified 95% interval about 470 to 830, 25% to 45%); in scope or unclear 939
  (51.0%); by tier T1 20/40, T2 3/40, T3 7/40, T4 2/40 in scope. Before round 4: 755 of 6,376 (11.8%). The queue falls by 71%;
  the count of in-scope-looking records is not different beyond the noise of 40-title strata. A check of 100 removed T1 to T4 records (stratified, drawn outside validation set V1): none looked in scope, 3 unclear.
  *S1'' and S2'' (verbatim; AND binds tighter than OR; a trailing `*` is a word-prefix wildcard; `NOT (...)` excludes any listed word; title, abstract and keywords; 2021-01-01 to the search date; English):*

  S1'' =
  ```
  (("diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms) AND NOT (mri OR fmri OR dmri OR "diffusion weighted" OR "diffusion tensor" OR "diffusion imaging" OR tractograph* OR "magnetic resonance" OR dti OR dwi OR "white matter" OR microextraction OR dllme)) OR ((("discrete diffusion" OR "masked diffusion" OR "discrete flow matching" OR ("discrete flow*" AND diffusion) OR ("discrete state-space*" AND (diffusion OR generative OR "flow matching"))) AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning) AND NOT (mri OR fmri OR dmri OR "diffusion weighted" OR "diffusion tensor" OR "diffusion imaging" OR tractograph* OR "magnetic resonance" OR dti OR dwi OR "white matter" OR "diffusion equation*" OR "reaction diffusion" OR "heat equation*" OR "heat transfer" OR thermal OR "fluid dynamic*" OR "fluid flow*" OR "fluid mechanic*" OR fluids OR porous OR "anomalous diffusion" OR "mass transfer" OR "gas diffusion" OR "partial differential equation*" OR "finite element*" OR "navier stokes" OR turbulen* OR "traveling wave*" OR wavefront* OR predator OR "life table*" OR dispersal OR oxide OR homogenization OR "mean curvature" OR smoluchowski OR kpp OR "diffusion system*" OR "diffusion epidemic*" OR "diffusion type equation*" OR epidemic* OR burgers OR microextraction OR dllme OR "disc diffusion" OR "disk diffusion" OR antimicrobial) AND NOT ("diffusion of innovation*" OR "innovation diffusion" OR "diffusion of technolog*" OR "technology diffusion" OR "diffusion of information" OR "information diffusion" OR "diffusion of knowledge" OR "rapid diffusion" OR "policy diffusion" OR "norm diffusion" OR "cultural diffusion" OR "social network*" OR twitter OR tweets)) OR (("masked diffusion" OR "discrete diffusion" OR "discrete flow matching") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation) AND NOT (mri OR fmri OR dmri OR "diffusion weighted" OR "diffusion tensor" OR "diffusion imaging" OR tractograph* OR "magnetic resonance" OR dti OR dwi OR "white matter" OR "diffusion equation*" OR "reaction diffusion" OR "heat equation*" OR "heat transfer" OR thermal OR "fluid dynamic*" OR "fluid flow*" OR "fluid mechanic*" OR fluids OR porous OR "anomalous diffusion" OR "mass transfer" OR "gas diffusion" OR "partial differential equation*" OR "finite element*" OR "navier stokes" OR turbulen* OR "traveling wave*" OR wavefront* OR predator OR "life table*" OR dispersal OR oxide OR homogenization OR "mean curvature" OR smoluchowski OR kpp OR "diffusion system*" OR "diffusion epidemic*" OR "diffusion type equation*" OR epidemic* OR burgers OR microextraction OR dllme OR "disc diffusion" OR "disk diffusion" OR antimicrobial) AND NOT ("diffusion of innovation*" OR "innovation diffusion" OR "diffusion of technolog*" OR "technology diffusion" OR "diffusion of information" OR "information diffusion" OR "diffusion of knowledge" OR "rapid diffusion" OR "policy diffusion" OR "norm diffusion" OR "cultural diffusion" OR "social network*" OR twitter OR tweets) AND NOT ("speech synthesis" OR "text to speech" OR tts OR vocoder* OR "voice conversion" OR "voice cloning" OR "speech generation" OR "audio generation" OR music OR singing OR waveform OR gesture* OR "talking head" OR dance OR "time series" OR "point cloud" OR "novel view" OR "video generation" OR "video to audio" OR "scene synthesis" OR "fault diagnosis" OR "anomaly detection" OR imputation OR precipitation OR "hand object" OR "motion generation"))) OR (("absorbing state" AND (language OR text OR token* OR "language model*") AND ("language model*" OR llm* OR "text generation" OR "language generation" OR "language modeling" OR autoregressive OR diffusion OR masked)) OR ("any-order" AND (language OR text OR token* OR "language model*") AND ("language model*" OR llm* OR "text generation" OR "language generation" OR "language modeling" OR autoregressive OR diffusion OR masked)) OR "non-autoregressive language model*" OR ("non-autoregressive" AND diffusion AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT ("speech synthesis" OR "text to speech" OR tts OR vocoder* OR "voice conversion" OR "voice cloning" OR "speech generation" OR "audio generation" OR music OR singing OR waveform OR gesture* OR "talking head" OR dance OR "time series" OR "point cloud" OR "novel view" OR "video generation" OR "video to audio" OR "scene synthesis" OR "fault diagnosis" OR "anomaly detection" OR imputation OR precipitation OR "hand object" OR "motion generation") AND NOT (mri OR fmri OR dmri OR "diffusion weighted" OR "diffusion tensor" OR "diffusion imaging" OR tractograph* OR "magnetic resonance" OR dti OR dwi OR "white matter" OR "diffusion equation*" OR "reaction diffusion" OR "heat equation*" OR "heat transfer" OR thermal OR "fluid dynamic*" OR "fluid flow*" OR "fluid mechanic*" OR fluids OR porous OR "anomalous diffusion" OR "mass transfer" OR "gas diffusion" OR "partial differential equation*" OR "finite element*" OR "navier stokes" OR turbulen* OR "traveling wave*" OR wavefront* OR predator OR "life table*" OR dispersal OR oxide OR homogenization OR "mean curvature" OR smoluchowski OR kpp OR "diffusion system*" OR "diffusion epidemic*" OR "diffusion type equation*" OR epidemic* OR burgers OR microextraction OR dllme OR "disc diffusion" OR "disk diffusion" OR antimicrobial) AND NOT ("diffusion of innovation*" OR "innovation diffusion" OR "diffusion of technolog*" OR "technology diffusion" OR "diffusion of information" OR "information diffusion" OR "diffusion of knowledge" OR "rapid diffusion" OR "policy diffusion" OR "norm diffusion" OR "cultural diffusion" OR "social network*" OR twitter OR tweets))) OR (diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") AND ("diffusion model*" OR "diffusion-based" OR "diffusion process*" OR "diffusion probabilistic" OR denoising OR "diffusion transformer*" OR "diffusion language" OR "discrete diffusion" OR "masked diffusion" OR "latent diffusion" OR "diffusion llm*" OR "diffusion decoding" OR "diffusion network*" OR "diffusion framework*" OR "diffusion paradigm*" OR "diffusion lm*" OR "diffusion mllm*" OR "diffusion bridge*" OR "diffusion generat*" OR "continuous diffusion" OR "diffusion step*" OR "diffusion objective*" OR "diffusion head*" OR "diffusion prior*" OR "reverse diffusion" OR "forward diffusion" OR "diffusion sampl*" OR "diffusion training" OR "diffusion refinement" OR "guided diffusion" OR "conditional diffusion" OR "diffusion augmentation" OR "embedding diffusion" OR "diffusion method*" OR "diffusion approach*" OR "diffusion technique*" OR "using diffusion" OR "via diffusion" OR "with diffusion" OR "through diffusion" OR "by diffusion" OR "diffusion for" OR "diffusion ar" OR "ar diffusion" OR "diffusion equipped" OR "diffusion directed" OR "diffusion supervision" OR "flow matching" OR "discrete flow*") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (mri OR fmri OR dmri OR "diffusion weighted" OR "diffusion tensor" OR "diffusion imaging" OR tractograph* OR "magnetic resonance" OR dti OR dwi OR "white matter" OR "diffusion equation*" OR "reaction diffusion" OR "heat equation*" OR "heat transfer" OR thermal OR "fluid dynamic*" OR "fluid flow*" OR "fluid mechanic*" OR fluids OR porous OR "anomalous diffusion" OR "mass transfer" OR "gas diffusion" OR "partial differential equation*" OR "finite element*" OR "navier stokes" OR turbulen* OR "traveling wave*" OR wavefront* OR predator OR "life table*" OR dispersal OR oxide OR homogenization OR "mean curvature" OR smoluchowski OR kpp OR "diffusion system*" OR "diffusion epidemic*" OR "diffusion type equation*" OR epidemic* OR burgers OR microextraction OR dllme OR "disc diffusion" OR "disk diffusion" OR antimicrobial) AND NOT ("diffusion of innovation*" OR "innovation diffusion" OR "diffusion of technolog*" OR "technology diffusion" OR "diffusion of information" OR "information diffusion" OR "diffusion of knowledge" OR "rapid diffusion" OR "policy diffusion" OR "norm diffusion" OR "cultural diffusion" OR "social network*" OR twitter OR tweets) AND NOT ("stable diffusion") AND NOT ("human motion" OR "motion generation" OR "motion synthesis" OR animation OR layout OR gan OR gans OR gesture* OR facial OR handwritten OR wireless OR "video diffusion" OR "image quality" OR "visual quality" OR "time series" OR "anomaly detection" OR music OR "speech synthesis" OR "text to speech" OR "voice conversion" OR "voice cloning" OR "scene text" OR "visual text" OR "text rendering" OR "autonomous driving" OR "driving scenario*" OR "driving simulation" OR robot* OR "internet of things" OR iot OR 6g OR tabular OR "image editing" OR "image synthesis" OR lora OR "low rank" OR quantiz* OR "preference optimization" OR "diffusion polic*" OR federated OR unlearning OR watermark* OR jailbreak* OR "retrieval augmented" OR "knowledge distillation" OR 3d OR "pose estimation" OR sketch OR cad)) OR (diffusion AND ("language model*" OR llm*) AND ("diffusion model*" OR "diffusion-based" OR "diffusion process*" OR "diffusion probabilistic" OR denoising OR "diffusion transformer*" OR "diffusion language" OR "discrete diffusion" OR "masked diffusion" OR "latent diffusion" OR "diffusion llm*" OR "diffusion decoding" OR "diffusion network*" OR "diffusion framework*" OR "diffusion paradigm*" OR "diffusion lm*" OR "diffusion mllm*" OR "diffusion bridge*" OR "diffusion generat*" OR "continuous diffusion" OR "diffusion step*" OR "diffusion objective*" OR "diffusion head*" OR "diffusion prior*" OR "reverse diffusion" OR "forward diffusion" OR "diffusion sampl*" OR "diffusion training" OR "diffusion refinement" OR "guided diffusion" OR "conditional diffusion" OR "diffusion augmentation" OR "embedding diffusion" OR "diffusion method*" OR "diffusion approach*" OR "diffusion technique*" OR "using diffusion" OR "via diffusion" OR "with diffusion" OR "through diffusion" OR "by diffusion" OR "diffusion for" OR "diffusion ar" OR "ar diffusion" OR "diffusion equipped" OR "diffusion directed" OR "diffusion supervision" OR "flow matching" OR "discrete flow*") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation) AND NOT (mri OR fmri OR dmri OR "diffusion weighted" OR "diffusion tensor" OR "diffusion imaging" OR tractograph* OR "magnetic resonance" OR dti OR dwi OR "white matter" OR "diffusion equation*" OR "reaction diffusion" OR "heat equation*" OR "heat transfer" OR thermal OR "fluid dynamic*" OR "fluid flow*" OR "fluid mechanic*" OR fluids OR porous OR "anomalous diffusion" OR "mass transfer" OR "gas diffusion" OR "partial differential equation*" OR "finite element*" OR "navier stokes" OR turbulen* OR "traveling wave*" OR wavefront* OR predator OR "life table*" OR dispersal OR oxide OR homogenization OR "mean curvature" OR smoluchowski OR kpp OR "diffusion system*" OR "diffusion epidemic*" OR "diffusion type equation*" OR epidemic* OR burgers OR microextraction OR dllme OR "disc diffusion" OR "disk diffusion" OR antimicrobial) AND NOT ("diffusion of innovation*" OR "innovation diffusion" OR "diffusion of technolog*" OR "technology diffusion" OR "diffusion of information" OR "information diffusion" OR "diffusion of knowledge" OR "rapid diffusion" OR "policy diffusion" OR "norm diffusion" OR "cultural diffusion" OR "social network*" OR twitter OR tweets) AND NOT ("stable diffusion") AND NOT ("human motion" OR "motion generation" OR "motion synthesis" OR animation OR layout OR gan OR gans OR gesture* OR facial OR handwritten OR wireless OR "video diffusion" OR "image quality" OR "visual quality" OR "time series" OR "anomaly detection" OR music OR "speech synthesis" OR "text to speech" OR "voice conversion" OR "voice cloning" OR "scene text" OR "visual text" OR "text rendering" OR "autonomous driving" OR "driving scenario*" OR "driving simulation" OR robot* OR "internet of things" OR iot OR 6g OR tabular OR "image editing" OR "image synthesis" OR lora OR "low rank" OR quantiz* OR "preference optimization" OR "diffusion polic*" OR federated OR unlearning OR watermark* OR jailbreak* OR "retrieval augmented" OR "knowledge distillation" OR 3d OR "pose estimation" OR sketch OR cad))
  ```
  S2'' =
  ```
  ((("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) AND (language OR llm* OR "language model*" OR mllm OR mllms OR "multimodal understanding" OR "multi-modal understanding" OR "visual understanding" OR "image understanding" OR "text generation" OR "language generation" OR "vision-language model*" OR vlm* OR "large multimodal model*" OR lmm*)) OR (("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms OR ("diffusion-based" AND ("diffusion vision language action" OR "diffusion vla" OR dvla))))
  ```
  Parts (S1'' = A1 OR A2 OR A3 OR B OR C; S2'' = M OR VLA) are in `subscription-search-sheet.md` and the report (12.2); the exclusion lists (R4_INNOV, R4_NET, R4_MRI, R4_PHYS, R4_PDE, R4_CHEM,
  R4_BIOMED, R4_STABLE, R4_NT, R4_NT_BC) and the requirement lists (R4_DS, R4_LMW, R4_A3_CTX) are held once in `tools/search_sources.py`.
  *Application to the queue (D0027 items 2 and 3).* S1'' and S2'' were applied locally to every one of the 6,376 queue records, T5 included: 1,842 pass
  (`corpus/screening-queue-final-2026-10-15.jsonl`; T1 1,084, T2 120, T3 512, T4 126, T5 0; 1,721 database, 121 snowball) and 4,534 are marked
  `auto_excluded` ('string filter, D0027'; `corpus/auto-excluded-2026-10-15.jsonl`; T1 213, T2 100, T3 1,709, T4 324, T5 2,188). For the flow diagram they are 'records marked as ineligible by
  automation tools', in addition to the 12,952 snowball records of D0026. 111 of them match the original strings S1 or S2 (non-text diffusion papers that S1 and S2 accept for lack of exclusions).
  *Validation of the automation filter (D0027 item 3).* Two random sets were drawn and written without screening them: V1, 200 of the 4,531 database records the filter excludes (seed 20261020);
  V2, 100 of the 2,107 snowball records excluded in D0026 on the title alone (seed 20261021); `screening/validation-autoexcl-2026-10-15.jsonl` (id, title, abstract, set). One screener screens them
  under the criteria of this protocol; the number of in-scope records lost is estimated with an interval. **Reversal:** if the estimate for the lost in-scope records exceeds about 2% of the in-scope records
  (D0027), the filter is relaxed and the excluded records are released to screening. Dual screening of the records that pass (D0026 item 5) follows, T1 and T2 first; it has not started.
- 2026-10-16 (D0032; full-text screening criteria v1.6: research/review/screening/criteria-v1.6-screener.md
  normative, criteria-v1.6.md audit copy; v1.1-v1.5 superseded after red-team audits of 2026-10-16).
  Written after the title/abstract decisions had been recorded and seen, before any full text was
  screened and before the freeze rule was applied. I1-I4 are unchanged; the following codes and
  readings govern full-text screening, each justified from the protocol text, D0020 or census
  codebook v1.2.
  (1) Code X0: no diffusion component in the paper's own method. One code per excluded record, first
  applicable in the order X8, X3, X5, X4, X0, X1, X2, X7 (census B-8). X1 and X2 are decided in this
  order: X1 for a model with autoregressive text whose diffusion component generates actions,
  molecules or other outputs outside the I1(b) list (D0020), also when text conditions that
  component; otherwise X2 if the paper states that text conditions the non-text diffusion component
  by any path; otherwise X1. Reports not retrieved (X6) are reported before eligibility.
  (2) Diffusion component: trained to reverse a corruption applied over a range of corruption levels,
  or along a discrete or continuous flow-matching path, and generating in more than one step or by a
  sampler distilled from such a component.
  (3) I1(a): the diffusion component produces text, read by content: natural-language words or
  sentences, or source code; chemical and biological sequences, game and puzzle states, formulas and
  equations without words, identifiers, actions and other non-language content are not text whatever
  tokens carry them; naming never decides. Following census B-7 ("except as tasks of a model that is
  eligible on other grounds"), a paper that trains further, fine-tunes, re-samples or compares a
  text-pretrained diffusion model (weights it loads, or weights it pretrains to generate
  natural-language text or code) is eligible even when its outputs in the paper are only non-language strings; such records
  are reported separately. A published recipe trained from random initialisation only on non-language
  content is not such a model; masked-diffusion puzzle or reasoning papers of that kind are therefore
  excluded unless they report a text result. The exception does not extend to actions, trajectories
  or outputs in another modality; 3D human pose, motion and other 3D geometry are decided by the "3D"
  reading in (4), whatever encoding carries them.
  (4) I1(b): D0020 verbatim, decided from statements in the screened file only. A trained parameter
  counts on the understanding side only if the understanding output is computed with it; a frozen
  understanding model with trained query tokens, connector, generation-only adapters or decoder is a
  pipeline. "3D" is read literally (3D geometry, including 3D human pose and motion), with exclusions
  taking precedence: D0020's (robot actions, molecules), census B-4(ii)'s (trajectories and other
  non-perceptual outputs), and those added by these criteria (waypoints, joint or end-effector
  commands, outputs generated as robot or vehicle commands, proteins, cell profiles, graphs, tables,
  time series, 2D keypoints and trajectories); a human motion is an action only if the paper's main
  results evaluate it by robot execution. Whether pose and motion count is open item O1 for the
  authors, and each such record also carries the code it would get if not.
  (5) I3: the language of the main body decides.
  (6) Decisions are include, exclude or adjudicate. Screener A is claude-sonnet-5-5 and screener B
  claude-opus-5-5 (Claude Code harness model list, 2026-10-16), with no fallback models. Adjudication
  route, fixed before the first full-text row of Screener A or B is written. Route F: adjudicator C is
  claude-fable-5-1, used only if both hold: (1) the user has approved in writing any usage-credit spend
  that claude-fable-5-1 draws on the user's plan, or has confirmed that it draws none; (2) a test
  session of claude-fable-5-1, started from the Claude Code harness with that model id, runs.
  Otherwise Route H: there is no model adjudicator; every disagreement between A and B and every
  "adjudicate" row goes straight to the human author, who is not told why a record is in the queue,
  and every count that would use C's rulings is computed from the A/B agreement rows plus the human
  author's decisions. The user decides (1); the orchestrator runs (2) and writes the route, the
  outcome of (1) and (2) and the date as the first line of analysis/screening/c-run-log.jsonl before
  the first full-text row of A or B. The route is not changed after that line, except that if
  claude-fable-5-1 later cannot be run, the rest of C's queue goes to the human author, logged in the
  same file. No other model is ever C. Every adjudicator session is logged and reported; each human
  adjudication session logs an attestation of blindness and the files opened. In every tranche of
  the full-text set the human validation records are screened before the human author sees any
  screener or adjudicator row of that tranche. Screener and
  adjudicator sessions run in uniquely named dispatch folders, under session rules that waive the
  user-level and project routines, with an isolation check after each session. Evidence quotes are
  contiguous passages of 6 to 40 words verified by script. A human screens a random 15 percent (at
  least 100) of the full-text set, and a screener below kappa 0.70 against the human triggers revision
  and rerun (s4 step 3), and then resolves the final set (s4 step 4).
  (7) Title/abstract decisions are not re-opened. A declared, scripted query selected 797 of 5,282
  title/abstract exclusions in classes where these readings are more inclusive; this is above the
  cap of 150 first stated in criteria v1.2 (ta_recheck_select.py CAP = 150), which was written
  together with the script that counted the candidates. A frozen random sample of 100 (seed
  20261016) is screened at full text, blind to its sample status, and reported in its own PRISMA
  box. If at least 1 sampled record is included, all 797 are screened. Tolerable loss 13 records (2
  percent of about 650 in-scope records that pass the automation filter, D0027 and D0029); trigger
  probability 0.42, 0.66, 0.83, 0.89 at 4, 8, 13, 16 true flips; at zero sampled inclusions the exact
  one-sided 95 percent upper bound for the frame is 22 records. A supplementary regex query on
  text-DLM terms (class C8) selects 32 further exclusions outside the frame, all screened at full
  text; 14 records of the frame meet the same query outside the sample and are screened only if the
  reversal fires. Queues screened later at title/abstract get their own frame and the same design.
