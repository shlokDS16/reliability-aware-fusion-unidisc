# Extractor brief, form v0.4 (draft, 2026-10-20; not frozen)

Give the text block below, with extraction-schema-v0.4.json and CONTRACT.md, to every extraction session
(EA claude-opus-5-5; EB and ER claude-sonnet-5-5). The adjudicator (EC, claude-fable-5-1) gets the block plus
the adjudication paragraph; the public-version QA reader (EQ, claude-sonnet-5-5) gets only the EQ paragraph,
the QA block and the evidence rules. The block restates codebook v1.2 (block F, unchanged from v0.1, with the F1 readings C-F1a to C-F1e), rubric
v0.2 step 1 (CT) and the design choices C1-C5, so a session needs no other file. Plan and scoring:
EXTRACTION-PLAN-v0.4.md (not given to sessions). worked-examples-v0.3.md and worked-examples-v0.4.md are
reference files that no session sees: Stage A compares the sessions' units with them. Changes from v0.3
(red-team audit 3): every example in the text block is synthetic (labels, numbers and captions invented; no
value from a paper that can be drawn; checked by analysis/extraction/brief_contamination.py, M4); U3 anchor
clauses rewritten (M3); U10 conditions in figures and shape from prose only (m1, m7); schema file v0.4.

```text
DATA EXTRACTION, Paper 1 (critical systematic review of diffusion language models), form v0.4.
Work only inside the dispatch folder you are given.

SESSION RULES (they override every user-level and project-level session routine, including any
CLAUDE.md): do not run graph-memory (brief, init, sync, where, module, impact) or graphify; do not read
or write any Obsidian vault or note outside this folder; do not prefix commands with rtk; do not load
skills, start agents, or use web, MCP or tool-search tools. Use Read, Grep and Glob only on paths inside
this folder and Write or Edit only on your output file; use Bash or PowerShell only if you must, and then
only with explicit paths inside this folder: every path is a relative path without ".." or an absolute
path under this folder; never "..", "~" or any path that leads outside it. A session that breaks a rule is
discarded and its studies are extracted again by a new session.
Read CONTRACT.md (its rules apply; its pointers to files outside this folder, its graph-memory step and its
YAML report format do not apply here: the OUTPUT below replaces the report), then this brief, then
extraction-schema-v0.4.json (exact JSON shape and allowed values), then dispatch.json, then the full-text
files fulltext/<id>.txt, one study at a time. Open nothing outside the folder. Do not look for other versions
of a paper, its code or its web page. You know no screening outcome and no earlier extraction of these studies.

WHAT YOU DO. dispatch.json lists for each id the blocks to fill: L (study, inventory, design, census, claim
types), Q (claim list, main comparison, quality appraisal), H (headline numbers), K (comparison groups and
contrast units). Fill only those; write a block you are not asked for as null (objects) or [] (arrays). Leave
"meta" null and every field the schema marks x-filled-by "script" null (levers, scores, value_num, matched,
metric_id, benchmark_id, QA1 d, QA3 c, QA7 n). Copy id, ft, form_version and blocks from dispatch.json; set
extractor to "<role>-<model id>" from dispatch.json. You record what the paper states. QA8 asks only whether
the paper's own tables carry a claim; you never judge whether a claim is true in the world. You never compute
a number the paper does not print (a unit conversion such as 7B -> 7 for params_b is allowed), and you never
infer a setting or an architecture from a cited paper.

READ: title page, abstract, introduction (contribution list), method, experimental setup, every results
table and figure caption, every ablation, limitations or conclusion, and the appendix sections that hold
hyperparameters, sampler settings, evaluation details and extra results. Page numbers come from the
"=== page N ===" markers.

GENERAL RULES
G1 Own, focal, main results, focal configuration.
   (a) Own model or method: one the paper presents as its contribution ("we propose / introduce / present /
       develop / unveil / release", "ours", or the paper's method name). Earlier models of the same authors
       named as background are not own.
   (b) Focal model (method, system, theory papers): the first own model or method the abstract names. If it
       is a training-free method (training_free yes and credited type sampler-or-decoding, caching-or-system
       or guidance-or-constraint), the focal system is that method on the base model of the first own arm
       of the main-results table.
   (c) Analysis and benchmark papers: the diffusion model that is an arm in the most main-text results tables
       and figures; ties: the first of them named in the abstract; else the first in the main-results table.
   (d) Main-results table: the first table in the experiments or results section (not the introduction,
       background or method sections) that has an own arm (analysis/benchmark: a focal-model arm).
   (e) Focal configuration: the configuration the setup or hyperparameter section names as default for the
       main experiments; else the first own arm of the focal model in the main-results table (rows top to
       bottom, then columns left to right). Write focal_model and focal_config (synthetic example: "Table 2:
       Ours-L (k=4)").
   Study-level and design fields describe the focal model; S07 lists every own model (analysis and
   benchmark: every evaluated diffusion model).
G2 As printed: numbers, model names, metric names, benchmark names and settings are copied as printed. If the
   paper does not state a value, write "not_stated"; if a field cannot apply, use NA as the schema allows.
G3 Source order for a setting (census B-13): a caption or experiment-section statement for that experiment
   overrides a hyperparameter table, which overrides a method-level definition. Statements about baselines do
   not apply to the focal model. Settings stated only for training, RL rollouts, data generation,
   distillation or teacher sampling are not evaluation settings unless the evaluation section says they are.
G4 Doubt: for QA sub-items answer "unclear". For other fields choose the conservative value (not_stated, NS,
   "not stated", no). In both cases add the field id to "doubt" and say why in notes. Never guess.
G5 metric_kind: generated-sample (computed on outputs of a sampler run to completion: accuracy or pass rate of
   generated answers, BLEU/ROUGE of generated text, FID/CLIP/GenEval of generated images, MAUVE, generative
   perplexity scored by another model; a benchmark accuracy counts unless the paper says it is
   likelihood-scored); likelihood (perplexity, bits per token, NLL or ELBO under the model itself,
   likelihood-scored multiple choice); speed (time, latency, throughput, speed-up); steps (number of steps
   or function evaluations as an outcome); other (anything else: one-step masked-token accuracy, probe or
   detector scores, robustness scores not computed on generated outputs).
G6 Every example in this brief and in the schema is synthetic: labels, numbers and captions are invented and
   come from no paper. Do not look for them in your files.

EVIDENCE
E1 Every positive value of a field marked [Q] needs at least one evidence entry whose "cond" is the field id
   (S04, D07.rule, F2, QA3d, I2 ...), the claim id (CL2), or the unit or group id (H03, K07, G02). Sub-fields
   use a dot: S10.steps, S09.tokens, D07.blockwise. Every negative value of a [Q] field (no, not_stated, NS,
   "not stated", none) and every QA sub-item answered no or unclear needs a "searched" entry with the same id:
   id -> the sections and tables you read, e.g. {"F2": "§4.1, §5, App. C, Table 9"}. One rule, no exceptions.
E2 PROSE evidence ("evidence" array, ids E01, E02 ...): ONE contiguous passage of 6 to 40 words copied
   character for character from fulltext/<id>.txt, citations, footnote markers and page headers as they
   appear: no ellipsis, no omitted words, no brackets, no added or changed words; at least 3 of its words
   contain letters. Longer than 40 words: split into two entries with the same cond. If a negation or
   qualifier (not, no, without, w/o, only, frozen, except ...) is in the same sentence, include it: a quote
   with a negation word in the 6 words before it or a strong negation in the 3 words after it is rejected by
   the checking script. Do not use prose entries for table rows.
E3 TABLE and CELL evidence for every value taken from a table, and for settings read from a hyperparameter
   table. First describe each table once ("table_evidence", ids T01 ...): where ("Table 3"); page (of the
   header); orientation (rows: the arms are rows; columns: the arms are columns); header = a run of the
   header tokens exactly as they appear in the file; header_levels (1 or 2); columns = the leaf map: every
   column after the row-label column, left to right, including text columns such as "Arch", each leaf as
   printed, a two-level leaf written "<level 1> / <level 2>" (e.g. "Bench-A / Acc", "Base-Q / Score");
   column_roles = what header level 1 (and 2) names in the value columns: arm, second-factor, benchmark,
   metric or condition; row_groups = the labels of row groups in order, each a whole line of the file
   (e.g. "Bench-A", "Bench-B"), [] if none; row_group_role (benchmark, second-factor, condition, none);
   caption = 6-40 words starting with "Table n" or "Figure n".
   Then one CELL entry per quoted row ("cell_evidence", ids C01 ...): table (T id); page (of the row);
   row_label = every token of the row label as printed, over all its lines, up to the first cell,
   including "w/o", citations and markers (e.g. "Model-Z-7B (rate=2)"); row_group (as printed;
   '' only if the table has none); first_col; cells = a LIST with one element per table cell from first_col
   on, each exactly as printed (a cell may hold several tokens: "Hybrid scan"; two values on one line are
   two cells; "|" separators are not cells; write "" for a blank cell, and only when the row visibly has
   fewer cells than the map); occurrence = null unless the same label and cells occur twice inside the row
   group (then 1, 2 ...). Every row you cite needs an entry with first_col 1. Label plus cell tokens at most
   40 per entry; for a wide row add entries with the same row_label and a larger first_col. Synthetic
   example (lines "w/o planner head", "41.7", "44.9", "38.2" under the header "Variant S1 S2 S3"):
   table {"id": "T01", "where": "Table 3", "page": 7, "orientation": "rows", "header": "Variant S1 S2 S3",
   "header_levels": 1, "columns": ["S1", "S2", "S3"], "column_roles": ["condition"], "row_groups": [],
   "row_group_role": "none", "caption": "Table 3: Ablation of the planner head on three synthetic test
   splits."}; cell {"id": "C04", "cond": "K02", "table": "T01", "page": 7, "row_label": "w/o planner head",
   "row_group": "", "first_col": 1, "cells": ["41.7", "44.9", "38.2"], "occurrence": null}.
E4 A value points to its evidence: a cell value gives the cell id, col = the position of its cell in the row
   (counted from the first cell after the row label, "|" not counted; in E3's example 44.9 is col 2) and
   column_printed = the leaf of the column map at that position ("S2"); a prose value gives the prose id
   and, if the number occurs twice in the quote, value_occurrence. value_printed must equal that cell
   exactly. The script checks the column against the map, the row group against the unit's benchmark or
   second factor, and in a columns-oriented table the arm against the column's level-1 label.
E5 loc format for prose: "p.<page>, §<section>" or "p.<page>, abstract". Every entry is checked by script; a
   rejected entry is returned to you once.

BLOCK L, STUDY AND INVENTORY
S01 study_type (one): method (proposes a model, objective, sampler, training or inference method), theory
   (main contribution is a theorem or formal analysis; experiments only illustrate it), analysis (empirical
   study of existing models), benchmark (new benchmark, dataset or evaluation protocol), system (serving,
   kernel, hardware or software engineering that leaves the model's outputs unchanged). Ties: the first
   contribution the introduction lists decides.
S02 modality: text (all inputs and outputs of the paper's models are text or code, or non-language strings);
   text+image (image is the only non-text modality taken or generated); text+other (video, audio or speech,
   or 3D, with or without image). Robot actions, trajectories, molecules, graphs, tables and time series are
   not modalities here. [Q unless text]
S03 text_generator: diffusion (the diffusion component produces the text); autoregressive (text is generated
   autoregressively and the diffusion component generates another modality); both; none (no natural-language
   or code output). [Q]
S04 state_space of the focal model's diffusion component(s) (list; several only for analysis or benchmark
   papers): discrete-absorbing (mask or absorbing state: masked diffusion, block diffusion); discrete-uniform
   (uniform or other substitution noise, incl. mixtures of mask and substitution noise); discrete-flow
   (discrete flow-matching path); continuous-embedding (Gaussian noise on token embeddings, on the simplex or on
   logits); continuous-latent (Gaussian noise or a continuous flow on encoder latents, incl. image latents);
   hybrid (components in two or more of these spaces); not_stated. [Q: the sentence or equation that describes
   the corruption]
S05 task_families: every family in which the focal model has any reported result, each with generated_sample
   true if at least one of those results is a generated-sample metric (G5): language modelling (unconditional
   or prefix-conditioned text generation; perplexity, likelihood, MAUVE, diversity); reasoning (mathematics,
   logic, puzzles, planning: GSM8K, MATH, Countdown, Sudoku); code; understanding (answers about an input: VQA,
   captioning, multimodal benchmarks, text classification, NLI, knowledge multiple-choice, reading
   comprehension); text-to-image; editing (image or other-modality editing instructed by text); other
   (translation, summarisation, dialogue, instruction following, text infilling or editing, text-to-video,
   speech, 3D, molecules). Name the tasks put in other in task_other.
S06 primary_task_family: the family of the F1 headline task; NA when F1 is NA.
S07 models: name and parameter count as printed ("not_stated" if absent), params_b in billions (null if not
   stated). [Q per printed count]
S08 base_checkpoints: named pretrained models the paper loads; empty if trained from scratch. [Q if non-empty]
S09 training: training_free yes (the paper states no training), no, not_stated; stages from {pretraining,
   continued-pretraining, adaptation-from-ar, sft, rl, distillation, other}; data_named; tokens_printed,
   compute_printed as printed. [Q for training_free yes and each printed value (S09.tokens, S09.compute);
   else searched]
S10 main_sampler for the F1 setting: description, steps, NFE, generation length, tokens per step, each as
   printed or "not_stated". Do not compute NFE. [Q per printed value: S10.steps, S10.nfe, S10.gen_length,
   S10.tokens_per_step]
S12 venue_line_text: the venue statement printed in the file, copied exactly; "none" if absent.
S13 credited_component: text = the first contribution the introduction lists (abstract if no list), in a few
   words, or "NA"; type = model-or-architecture, objective-or-loss, training-recipe (data, stages, RL,
   distillation), sampler-or-decoding, caching-or-system, guidance-or-constraint, theory, benchmark-or-dataset,
   analysis-only, other. [Q]
S15 limitations.categories the paper states as its own limitations or weaknesses: compute-or-speed, scale,
   quality-gap (worse than a reference class of models), length-or-fixed-length, evaluation-scope, data,
   assumptions, safety-or-misuse, other; or ["none"]. [Q per category; searched for none]
S16 synergy_benchmark: present yes if the paper builds or uses a benchmark it presents as measuring whether
   understanding and generation help each other; name as printed. [Q if yes]
S17 focal_model and S18 focal_config: see G1.
I1-I5 inventory (yes or no, anywhere in the paper including the appendix): I1 a table or figure scores the
   focal model and a model the paper labels autoregressive on the same benchmark; I2 a table or figure varies a
   training choice of the focal model (pretraining recipe, AR initialisation, SFT, RL, distillation,
   objective, architecture); I3 a table or figure varies an inference setting of the focal model (steps or
   NFE, tokens per step, order, remasking, caching, block or parallel decoding, value rule or guidance,
   generation length); I4 a unified model is compared with a task or modality removed from training, or shared
   against decoupled pathways; I5 the focal model is compared with and without (or with a standard
   replacement of) its credited component. [Q if yes: the caption or sentence; searched if no]

BLOCK L, DESIGN SPACE (focal model and its F1 sampler; one generation = a sequence of commit steps on a state
of partly revealed or noised tokens plus optional memory). For each of D01-D11 and D15 also write provenance:
contributed (the paper introduces or changes this choice), inherited (taken unchanged from a named checkpoint
it loads; name it in inherited_from), inherited-from-cited-method (taken from a cited method or recipe
without loading its checkpoint; name the cited method in inherited_from), not_stated, NA. Code the value from the paper's own description; if the
paper describes nothing about an inherited choice, the value is not_stated and provenance inherited.
D01 c1_channel, one entry per generated modality: erasure (absorbing mask), symmetric (uniform substitution),
   erasure-symmetric-mixture, gaussian-embedding, gaussian-simplex-or-logit, gaussian-latent, flow-discrete,
   flow-continuous (incl. rectified flow), autoregressive (that modality is generated left to right without
   diffusion), other, not_stated. [Q per entry]
D02 c2_reveal (which positions are clean together in training, text or only modality):
   independent-shared-level (each position masked independently at one shared level t), block (independent
   level per block, clean prefix of blocks), any-order (prefixes of a random permutation), prefix
   (autoregressive), gaussian-shared-level, gaussian-mixed-conditioning (prefix, random or block conditioning
   masks with a shared noise level), other, not_stated. [Q]
D03 c2_multimodal: shared-level, clean-input-noised-output, modality-dropout, independent-per-modality,
   capped-noise, other, not_stated; NA for one modality. [Q]
D04 c3_predictor (network output): clean-marginals, concrete-score-or-ratio, x0-embedding-regression,
   posterior-mean-embedding, noise-or-velocity, probability-denoiser, other, not_stated. [Q]
D05 c3_self_conditioning: yes (previous prediction fed back as input), no, not_stated. [Q if yes]
D06 c3_head_layout: single-modality, shared-vocabulary-head, separate-heads, text-head-plus-continuous-head,
   other, not_stated. [Q unless single-modality]
D07 c4_position: rule = left-to-right, random (ancestral masked diffusion), confidence-ranked (confidence,
   margin or entropy ranking, fixed count per step), threshold-adaptive (positions above a threshold,
   variable count), fixed-order (a schedule not reading predictions), learned-planner, all-positions (every
   position updated each step: Gaussian or uniform channels), other, not_stated; blockwise = yes, no,
   not_stated. [Q: D07.rule, D07.blockwise]
D08 c4_joint_draw: independent, ar-head, copula, energy-or-verifier, speculative-verification, other,
   not_stated. [Q unless independent]
D09 c4_multimodal_schedule: joint, sequential, alternating, other, not_stated; NA for one modality. [Q]
D10 c5_revision (list): none, explicit-remasking-or-editing, corrector, implicit-channel, output-level, other,
   not_stated. [Q; searched for none]
D11 memory (list): none, self-conditioning, exact-cache (outputs unchanged), approximate-cache (can change
   outputs), planner-state, other, not_stated. [Q; searched for none]
D14 other_detail: say what each "other" in D01-D11 and D15 is.
D15 objective (training loss and weighting of the focal model): elbo-ce (masked or discrete diffusion ELBO,
   cross-entropy with the ELBO weighting), weighted-ce (cross-entropy with another stated weighting or none),
   score-entropy, mse-x0, mse-eps-or-velocity, flow-matching, other, not_stated; NA if the paper trains nothing
   and does not describe the loaded model's objective. [Q unless not_stated or NA]

BLOCK L, CENSUS (value rule and reporting of the headline result; codebook v1.2 consolidated; unchanged
from form v0.1 except that the F1 number becomes an H unit)
F1 headline. Generated-sample metric: computed on outputs of a sampler run to completion (not speed,
   throughput, perplexity or likelihood under the model, one-step masked-token accuracy, detector or probe
   scores); a benchmark accuracy counts unless the paper states it is likelihood-scored. In-scope task: one
   whose output the paper's diffusion component produces (text or code when the diffusion component
   generates text; otherwise that component's output, e.g. images); a synthetic token task only if the paper
   has no natural-language or code experiment. Rule: take the first in-scope generated-sample number for the
   paper's own method in the abstract, skipping speed-only and likelihood-only numbers and tasks the abstract
   names first that are out of scope; unified models: the first generation task the abstract names
   (text-to-image before understanding when both are named and both are in scope). If the abstract has none:
   the first main-text results table that reports the final method on the in-scope main task (appendix only
   if the main text has none; a figure only if no table exists), skipping tables that report only baselines;
   within it the metric the text quotes, else the first generated-sample column; the row the text quotes,
   else the default configuration named in the method or setup, else the first row of the final method. Only
   when a table has a plain and a guided or best-of variant of the final method and the text quotes none, take
   the best row. If the only in-scope table is an ablation, use the default configuration. Garbled cell: read
   prose that quotes the same cell; else unreadable. Make the chosen number an H unit with is_F1 true (origin
   abstract if it is an abstract number, else F1-table, F1-figure or F1-text) and write its id in F1_unit.
   F1_status: number; figure-only (curves only); unreadable; QL (only qualitative samples, no metric); NA (no
   generated-sample metric for the own method: theory only, or only likelihood bounds). Couplings: NA gives
   F2-F6 NA; QL gives F2 coded and F3-F6 NA; unreadable keeps F2-F6 coded.
   Readings of the F1 rule (form v0.3; checked against codebook v1.2 by the gate-auditor):
   C-F1a A table placed in the introduction, background or method section is not "the first main-text
         results table" when a table in the experiments or results section reports the final method.
   C-F1b "The first generation task the abstract names" is read in the sentences about the paper's own
         model; sentences about a field in general do not count. Text produced from an image input
         (captioning, VQA) is understanding.
   C-F1c In a table whose row groups are benchmarks, the benchmark is the one of the cell the text quotes
         first; else the first row group.
   C-F1d For a study with no method of its own, the studied (focal) model stands in for "the paper's own
         method". "The first generated-sample column" is the first value column of the first sub-table.
   C-F1e In a table whose arms are columns, read the rule's "row" as the arm's column and its "column" as
         the outcome row. An average over named benchmarks printed as a row or column is a valid F1 setting.
F2 value rule behind the F1 number, from the text (main text and appendix). Letters:
   A argmax or greedy commit (temperature 0, "deterministic"; a per-step argmax or projection inside the
     loop; the final rounding or nearest-embedding step of a continuous channel is not A: note it in F2_detail);
   T a stated temperature other than 1 (value in F2_detail; above 1 write "T>1"; annealing without a value
     is NS for the temperature part; "tuned per task" without values is NS for that part);
   P top-p, top-k or nucleus truncation;
   S values sampled and positions chosen by a score of the sampled value (confidence of the sampled token,
     MaskGIT-style, low-confidence remasking at temperature above 0), or confidence-ranked positions with a
     stated sampled token rule;
   C positions chosen by a confidence, margin, entropy or threshold score of the predicted distribution with
     the token rule not stated (if stated: A for argmax values, S for sampled values); a position order that
     does not read the predicted distribution is not a letter (write it in F2_detail);
   G any sampling-time change of the per-step distribution by an external score: classifier-free or
     classifier guidance, reward, value or constraint gradients, hard per-step constraints (grammar or validity
     masks), per-step rejection of a token by an external rule (scale or "hard" in F2_detail); rewards used
     only in training are not G;
   M the reported number is computed on outputs chosen among complete candidates by a score available at
     inference time without ground truth (likelihood, reward model, verifier, validity or syntax check, MBR,
     reranker, rejection of invalid outputs), beam, best-first or tree search (write "beam B" etc.), particle or
     SMC resampling (add G when weights include an external reward, classifier or constraint; own-likelihood
     weights only: write "SMC, own-likelihood weights"); oracle selection with ground truth (pass@k, best-of-N
     against references or hidden tests) is not M: write "oracle@N" and code the per-sample rule; if the text
     does not say whether the selecting score uses ground truth, code M and say so;
   U plain, only if all three are stated for the F1 setting: (1) the value distribution (temperature 1,
     "sampled from p_theta", ancestral or standard sampling, or a named sampler whose definition fixes these);
     (2) for samplers that choose positions, the position rule (random, scheduled, left-to-right, blockwise);
     (3) no truncation, guidance or selection, by an explicit statement or a sampler-settings list or
     hyperparameter table for the experiment that names none (such a list is read as complete). "Temperature
     1.0" alone is NS. Process-level samplers (tau-leaping, Euler CTMC, ODE integration) are U only with an
     explicit statement that no temperature, truncation or guidance is applied;
   NS the rule is not stated.
   What counts as stated: an experiment-section or caption statement, a hyperparameter table, or a
   method-level sampler definition when the experiment evaluates the method by name and the definition leaves
   no value parameter free. Background describing earlier samplers, theorems about a decoding rule, and a
   headline that merely matches a row of another table do not count; a blanket experimental sentence ("zero
   temperature for all experiments") does. Two conflicting statements at the same level: NS, quote both.
   Combining: list every stated letter in the order A T P S C G M joined by "+"; when the base token rule (the
   A, T, P, S, C or U part) is not stated, append "+NS" (e.g. "G+NS"); G or M without NS means the base rule
   is stated and otherwise plain. U never combines with a letter. A excludes S and T. Gaussian or embedding
   channels: code the per-step rule. Code the headline row only; list other variants in F2_detail.
   [Q for any letter or U; searched for NS]
F3 diversity reported: yes if the same table or figure as F1, or an item the text explicitly pairs with it
   (same model, sampler setting and task; same table or figure, or an appendix item the main text cites for
   that experiment), reports a diversity measure: entropy (unigram, sentence), distinct-n, self-BLEU, MAUVE,
   pass@k with k > 1, image recall, LPIPS diversity, Vendi, FID only when presented as diversity, or any
   metric computed over several samples of the same setting (or over the token distribution of the generated
   text) that changes with variety and is presented as diversity, entropy, repetition or coverage (unique or
   distinct ratios, repetition rates, clusters or modes, pairwise dissimilarity, uniqueness). Not: quality or
   fidelity scores, generative perplexity, novelty against training data, best-of-N reward, validity, CLIP
   score, Inception score. no otherwise; NA if F1 is NA or QL. [Q if yes]
F4 step sweep: yes if the paper's own method is reported at three or more settings that differ in denoising
   steps, NFE or tokens per step, on the F1 task (same benchmark or dataset, any generated-sample metric) and
   output length, with a step measure printed for each setting; settings may be fixed through a threshold,
   schedule or cache interval. partial: exactly two settings, or only an appendix figure without numbers.
   Not a sweep: step counts that change only with output length; throughput, latency or speed-up without a
   step measure; sweeps over particles, candidates, beam width, guidance strength, outer-loop iterations, or
   block size across separately trained models (a block-size sweep on one trained model counts). no
   otherwise; NA if F1 is NA or QL. [Q if yes or partial]
F5 value rule held fixed in the sweep: stated (an experiment-level sentence, caption or table entry says the
   rule is the same across the sweep, or a single stated rule with the text saying only the step count
   varies, or a blanket "all experiments" sentence that covers the sweep with no other sentence giving it a
   different rule); co-varied (the text or a table shows the rule differs between step settings; a procedure
   applied identically at every budget is not co-varied); not stated (incl. a method-level default without
   such a sentence); NA when F4 is no or NA. [Q if stated or co-varied]
F6 guidance held fixed in the sweep: as F5 for the guidance setting; NA when F4 is no or NA or F2 has no G.
   Multi-task sweeps: code the F1 task only.

BLOCK L, CLAIM TYPES
CT (abstract only; a type is asserted if the abstract states that advantage for the paper's own method or
   model, with or without a number; several can be yes; a paper with no method has all no):
   CT1 steps: fewer denoising or sampling steps, forward passes or function evaluations (not "efficient" or
       "fast" without steps);
   CT2 time: faster in time, a speed-up factor, higher throughput, lower latency (not fewer steps only);
   CT3 inference quality: better quality or accuracy from a technique applied at generation time without
       training (sampler, decoding or remasking rule, guidance, constrained decoding, "training-free");
   CT4 training quality: better quality or accuracy from anything that trains (new model, objective,
       fine-tuning, RL, distillation, architecture);
   CT5 unification: tasks, modalities or objectives help each other, or unifying them improves performance
       (not merely results on several tasks);
   CT6 versus autoregressive: matches, approaches, is competitive with or outperforms autoregressive models,
       as a class or a named model (not comparisons with diffusion models only).

BLOCK Q, CLAIMS LIST AND MAIN COMPARISON
CL every checkable claim: each sentence of the abstract, and each item of the introduction's contribution
   list, that states a number or a comparative direction for the paper's own method. For each: claim_id CL1,
   CL2 ... in order; source; types (CT codes, or "none"); has_number; h_units (the H units of its numbers);
   trace (ids of the cell or prose entries the status rests on); status:
   match (the claimed number appears in a table, figure or results text for the stated setting; trace it);
   direction (no number; the stated direction holds for every compared row of the table it refers to; trace it);
   partial (holds for some benchmarks or settings while the claim states no such restriction);
   unsupported (no table, figure or results text carries it);
   contradicted (the paper's own table shows the opposite for the stated setting);
   not-checkable (no number and no direction a table can test: "competitive", "strong", "comparable",
   "state-of-the-art" without a named comparator and metric).
   [Q per claim: the claim sentence, cond = CL id]
S14 main_comparison, anchored on the F1 unit: where = the table of the F1 unit's cell (an abstract F1 number:
   the table of its trace; no trace: the main-results table of G1d, basis "first-main-results-table");
   own_row = the F1 arm's label as printed; row_group = its row group or ''; baseline_row = (i) if that table
   has an arm the paper labels autoregressive (K-AR) and the abstract makes a CT6 claim or the study is an
   analysis or benchmark study, the first such arm in reading order; (ii) else the first other arm in
   reading order (same row group) with a value in the F1 column; basis "F1-table". F1_status NA, QL or
   figure-only, or no other arm: "NA". QA3-QA6 below refer to this table and these two rows ("the main
   comparison").

BLOCK Q, QUALITY APPRAISAL (answer yes, no or unclear for every sub-item listed; leave score null)
QA1 a: the paper gives a URL to code for its own method; b: it names a commit, tag, release version or an
    archive DOI for that code; c: release is only promised ("will be released") or on request. Leave d null.
QA2 a: the weights of every model in the main comparison's own row are released or are public checkpoints
    named with a source (link or hub id); b: the data the main comparison needs (evaluation benchmarks, and
    training data if the own row is a trained model) are public and named, or released; c: a missing part is
    only promised or on request.
QA3 a: prompts, templates or the few-shot setting of the main comparison are stated (yes also when the task has
    no prompt by design); b: steps or NFE and the generation length are stated for it; d: hardware is stated.
    Leave c null.
QA4 n: S14 is NA (then a and b null; answer c); a: the main comparison reports results of two or
    more runs; b: it states three or more; c: repeated runs are reported only for some other result. A run is
    an independent repetition with a different sampling seed, or a separately trained model; re-scoring the
    same samples or adding benchmarks is not a run.
QA5 n: S14 is NA (then a null; answer b); a: an interval, standard deviation or standard error with stated meaning, or a defined
    significance test, is given for the main comparison; b: such uncertainty only for other results, or the
    main comparison has a plus-minus whose meaning is not stated.
QA6 n: S14 is NA (then a-d null); a: parameter counts of both rows of the main comparison are stated; b: they
    are within a factor of two, or the paper states they are matched; c: an inference budget (steps, NFE,
    tokens or time) is stated for both; d: a training budget (tokens or compute) is stated for both trained
    arms, or stated as matched.
QA7 leave n null (computed from S13 type); a: a table or figure compares the focal model with and without the
    credited component (or with it replaced by a standard alternative); b: that comparison states, or its table
    shows, that everything else is held fixed (same model, data, budget); c: there is an ablation only of a
    different or a sub-component. Use cell evidence for ablation rows.
QA8 sub {}; it is computed from the CL statuses.
QA9 a: a section or paragraph presented as limitations (or future work that names a weakness); b: at least one
    failure case, negative result or setting where the method is worse is shown or described.
    For each QA item give loc ('' when every sub-item is no). [Q per yes, cond = QA<n><letter>, e.g. QA5a;
    searched for every no or unclear]

BLOCK H, HEADLINE NUMBERS (ids H01, H02 ... in order of appearance)
H-1 Every number in the abstract that reports an outcome of evaluating a model: a quality or accuracy score,
   a likelihood or perplexity, a speed (time, throughput, speed-up), a number of steps or evaluations reached,
   or a difference or ratio of such outcomes. One unit per number; the same number printed twice for the same
   statement is one unit. NOT units: parameter counts, data tokens, compute, numbers of benchmarks, tasks or
   languages, dates, and settings ("with <n> steps" goes in the setting of the number it qualifies).
H-2 If the census F1 number is not in the abstract, one more unit for it (origin F1-table, F1-figure or
   F1-text; value_printed "figure-only" or "unreadable" only here).
Fields: is_F1; origin; value_type (ratio if printed as a factor: x, times, -fold; difference if printed as a
gap: "by 2.5 points", "+1.5", "17% faster"; level otherwise); arm_role (own or baseline for a level; NA
otherwise); reference_printed (for a difference or ratio, the comparator as printed in the same sentence, or
"not stated"; '' for a level); model_printed; metric_printed; metric_kind (G5); higher_is_better;
benchmark_printed ("not stated" if none); split; task_family; value_printed (as printed); value_unit; scale
(fraction 0.463, percent 46.3 or "46.3%", points for a difference in points, raw, factor, other); setting (each
as printed for that number or "not_stated"); variance (kind none, sd, se, ci, range, plusminus-undefined, test,
other; value as printed; n_runs if stated); evidence_ref and col or value_occurrence (E4); column_printed
(the column-map leaf for a cell value, '' for prose); trace and trace_col (for an abstract number: the table
cell that prints the same number for the stated setting, the same also when the cell rounded to the abstract's
printed precision equals it (synthetic: a cell 13.47 for an abstract "13.5"); else null); loc {page, where}. [E2-E4]

BLOCK K, COMPARISON GROUPS AND CONTRAST UNITS (ids G01 ..., arms A1 ... within each group, K01 ...)
Terms: an arm is one row (or column, or figure series) that denotes one system configuration; own, focal
model, main-results table and focal configuration are as in G1.
U1 Go through every results table and figure in reading order (main text, then appendix), wherever it is
   placed. Never skip a table, row or group because it repeats an earlier one: a script removes duplicates.
U3 Anchor of a group in a method, system or theory paper: the first clause below that gives an arm. Write
   the clause's name in anchor_rule.
   focal-label: the arm whose label equals the focal configuration (ignore "(ours)", citations and spaces).
   other-own-model: if the table reports another own model or own method the abstract names, that model's
     arm in the focal configuration's setting, or its only arm.
   stated-default: for a factor group, the level the setup, caption or text names as default or baseline for
     THIS table or figure; a statement about another experiment, another model or another scale does not
     count.
   value-identity: the reference arm is the focal configuration's arm; for a group whose second-factor level
     is another own model, that model's arm in the focal setting. Look at EVERY results table before this
     one in reading order that contains the reference arm (whether or not it is the main-results table). A
     shared column is an outcome with the same benchmark, the same condition and the same metric (or a metric
     printed in only one of the two tables), with both values printed at the same scale (they differ by less
     than a factor of 2; synthetic: 0.45 against 45.2 is not the same scale, so that column is not shared).
     Two values are equal if they are equal after rounding to the coarser printed precision; "-" or a blank is
     not a value. A level qualifies if it equals the reference arm on at least one shared column and differs
     on none. Several qualify: the one equal on more shared columns, then the first in reading order.
   full-configuration: for a task-or-modality-removal or component-removal group, the one arm whose label
     marks no removal ("only", "w/o", "without", "no <X>", "-<X>"); a single-task, "only" or ablated arm is
     never the anchor while such an arm is present.
   first-own-arm: the first own arm in reading order whose label marks no removal (if every own arm marks
     one, the first own arm).
   Analysis and benchmark papers: the level stated as default for the factor ("unless otherwise specified"),
   else null with anchor_rule none.
U4 K-RQ2: a table or figure panel that has the anchor (analysis and benchmark papers: a diffusion arm) and at
   least one arm labelled autoregressive (U5) with a value in a common outcome column gives ONE group,
   factor_type model-class: arms = the anchor plus EVERY autoregressive-labelled arm, in reading order
   (analysis and benchmark papers: every diffusion arm and every autoregressive arm). Non-autoregressive
   baselines and other own variants are not arms of this group.
U5 K-AR: an arm is autoregressive for an output if the paper labels its generator of that output
   autoregressive, AR, next-token or left-to-right: in this table; through a marker or a column type its
   caption defines as autoregressive (then every arm with that marker or column type is AR); in another table of the paper
   that labels the same model (same label, or the same label plus one parenthesis) for the same output; or in
   the text. Write the place in ar_label_source. Judge per output: a model whose images come from discrete
   diffusion is not autoregressive in a text-to-image table even if its text is. Never infer from a cited
   paper or a model name. Unlabelled arms are not arms (say so in notes).
U6 K-F factor groups. (a) Arms that replace the credited component or the own method by another method on
   the same base model form ONE replacement group with the anchor, credited_ablation true; in training-free
   method papers other decoders are such arms, never "baselines". Arms that vary one parameter of the own
   method form one group per parameter (the anchor plus every arm that differs from it in that parameter
   only). An arm that differs from the anchor in two or more factors forms no group (note it). (b) Only the
   factor types of U8 form groups; model size or scale, resolution, amount of data, training steps,
   learning-rate style tuning, evaluation tools and prompt content do not. (c) Analysis and benchmark papers:
   factor groups from main-text tables and figures, for any diffusion model they vary; an appendix table or
   figure forms a group only if its factor type is in no main-text group of the record.
U7 Second factor: when a table varies another factor across column groups, row groups or figure series (base
   model, own model size, an own method shown as a series, a fixed setting at two or more values), make one
   group per level and write that level as printed in second_factor_printed (a row group, a level-1 column
   part or a legend entry). Conditions under which an outcome is measured (prompt contexts, target languages,
   attack types, task subsets) are not second factors: they go in condition_printed (U9).
U8 factor_type: model-class (U4 only); pretraining-recipe (pretraining data, schedule or stages); ar-
   initialisation; sft; rl; distillation; objective (loss, loss term or loss weighting); architecture;
   steps-or-nfe (number of steps or function evaluations set directly); tokens-per-step (tokens committed per
   step, set directly or by a confidence threshold that decides how many positions are committed; dose_unit
   threshold); order-rule (which masked positions are committed: random, left-to-right, confidence, margin or
   entropy ranking, search-based choice); remasking (re-masking or editing positions already committed);
   cache; block-or-parallel (block size, block or parallel decoding scheme); value-rule (temperature,
   truncation, argmax against sampling); guidance (guidance scale, reward or constraint guidance); gen-length;
   task-or-modality-removal; shared-vs-decoupled; component-removal (the credited component removed and no
   type above fits); other (any other inference-time setting: search width, pruning threshold, quantisation).
   rq_class is filled by the script from factor_type; leave it null.
U9 Contrast units: one K unit per outcome of a group = (benchmark, metric, condition) with values for at least
   two arms. condition_printed = the header parts above the value's column (rows orientation), or the row
   label and row group (columns orientation), that name neither the benchmark, the metric, an arm nor the
   second factor, joined from the top with " / " (synthetic: "Noisy / Long", "fr"); '' if none. Sub-scores of one
   benchmark (GenEval categories, MME sub-tasks, per-category accuracies): only the aggregate column (Overall,
   Avg., Average, Mean, Total, Score) if there is one, else every sub-score. Suite rule: if the table has more
   than 10 benchmark rows (or columns) and prints an average over them, record only that average
   (benchmark_printed as printed, e.g. "Average"); otherwise record every benchmark and never an average over
   benchmarks. Speed and step columns are their own units.
U10 Figures: a figure panel forms groups by U4, U6 and U7 when it plots an outcome against arms or factor
   levels. Values are "figure-only" (numbers printed inside a figure are not extracted); one K unit per
   (benchmark, metric) pair plotted. A condition (U9) never makes a separate unit or group in a figure,
   whether it is drawn as a series, as an x-axis category (an axis "C1 Score, C2 Score, C1 Time, C2 Time"
   gives two units: Score and Time) or as panels (panels that differ only in the condition are read as one
   panel). Series that are own methods or settings are second-factor levels (U7). Bar charts that compare
   only non-autoregressive models form no group. shape: code it only from a sentence of the text or the
   caption that states the trend on the primary metric; otherwise unclear (curves are not visible in the text
   file).
U11 Row labels: every line of the label up to the first cell (synthetic: "Model-Z-7B" on one line and
   "(rate=2)" on the next give "Model-Z-7B (rate=2)").
Not groups: comparisons among baselines only; the focal model against non-autoregressive baselines that are
not replacements of the credited component (those enter S14 only).
Group fields: factor_type, factor_printed, dose_unit (steps, nfe, tokens-per-step, threshold, cache-interval,
block-size, gen-length, guidance-scale, temperature, other, NA), where, page, source_kind, orientation (rows,
columns, figure), second_factor_printed, anchor_arm, anchor_rule, held_fixed (stated: the text, caption or
table states or shows that only the factor changes; co-varied: it shows something else changes with the
factor; not stated), other_changes ('' if none stated), budget_across_arms (inference budget: matched,
reported, not reported), shape (for a figure-only group, on the primary metric: monotone-up, monotone-down,
peaked, flat, unclear, from a stated sentence only (U10); else NA), evidence_refs. [Q for held_fixed stated or co-varied, non-empty
other_changes, budget matched: cond = group id]
Arm fields: label_printed (U11, or the column label, exactly as printed), role, generator, ar_label_source,
level_printed, level_num (number in dose_unit, else null), params_printed, train_tokens_printed,
shots_printed, scoring (generated, likelihood, not_stated), number_source (run-by-authors if the paper says it
ran the arm; copied-stated if it says the number is taken from a paper; a citation in the row label alone is
not_stated), steps_printed, gen_length_printed. [Q for printed per-arm values not in the value row: cond =
group id plus ".A2" etc., e.g. G03.A2]
K unit fields: group_id, benchmark_printed, metric_printed, condition_printed, metric_kind, higher_is_better,
scale, split, task_family, n_eval_printed (items or samples as printed, or not_stated), figure_only, values
(one per arm present: arm_id, value_printed, cell, col and column_printed, or prose and value_occurrence;
variance). A figure-only unit: figure_only true, every value_printed "figure-only", cell, col, prose null.
[E3, E4]

OUTPUT: one JSON object per study, on one line, UTF-8, appended to the output file named in dispatch.json as
soon as that study is done; every id exactly once; on resume skip ids already present. The object must
validate against extraction-schema-v0.4.json. Notes at most 60 words: the ambiguities you met and the rule you
applied.
FINAL MESSAGE: number of records written; for each id the counts of H units, groups, K units, prose entries and
table and cell entries; the ids in "doubt"; up to five gaps in these rules (rule and one sentence each). Never edit any
file except your output.
```

## Adjudication paragraph (EC only; append to the block above)

```text
ADJUDICATION. Your folder also holds two records for each study (records-<id>.jsonl), labelled X and Y. The
labels are assigned at random per study and say nothing about who wrote them; you know no other outcome. For
each field, unit, group, arm, value and claim on which X and Y differ, read the full text yourself and write
the final value under the rules above, with evidence as in E1-E5. Units and groups found by only one record:
decide whether the rules require them. Benchmark or metric strings that the lookup tables in your folder do
not map: list them in your final message with the id you propose. Write one final record per study with
"extractor": "EC-<model id>". In notes (no word limit for you) write one line per ruled item: the field, unit
or group, the basis "X", "Y" or "neither", and the condition that split them. Items you cannot settle from the
text: keep the conservative value (QA: unclear) and list them in your final message for the human author.
```

## Public-version QA paragraph (EQ only; with the QA block and E1, E2, E5)

```text
PUBLIC-VERSION QA. Your folder holds, for each study, one public version of a paper whose screened copy was
an anonymous submission (fulltext/<id>.txt). Read only its title page, footnotes, and any statement about code,
data or model availability (search for github, huggingface, code, release, available, weights, checkpoint).
Answer QA1 a, b, c and QA2 a, b, c as in the QA block, with prose evidence from this file, cond QA1a etc.
Output one JSON object per study on one line: {"id", "extractor": "EQ-<model id>", "public_version": as in
dispatch.json, "QA1": {"a","b","c"}, "QA2": {"a","b","c"}, "evidence": [...], "searched": {...}, "notes"}.
Nothing else.
```
