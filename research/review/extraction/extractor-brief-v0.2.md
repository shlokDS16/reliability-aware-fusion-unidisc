# Extractor brief, form v0.2 (draft, 2026-10-20; not frozen)

Give the text block below, with extraction-schema-v0.2.json and CONTRACT.md, to every extraction session
(EA claude-opus-5-5; EB and ER claude-sonnet-5-5). The adjudicator (EC, claude-fable-5-1) gets the block plus
the adjudication paragraph; the public-version QA reader (EQ, claude-sonnet-5-5) gets only the EQ paragraph,
the QA block and the evidence rules. The block restates codebook v1.2 (block F, unchanged from v0.1), rubric
v0.2 step 1 (CT) and the design choices C1-C5, so a session needs no other file. Plan and scoring:
EXTRACTION-PLAN-v0.2.md (not given to sessions).

```text
DATA EXTRACTION, Paper 1 (critical systematic review of diffusion language models), form v0.2.
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
extraction-schema-v0.2.json (exact JSON shape and allowed values), then dispatch.json, then the full-text
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
G1 Focal model: the paper's own main model (the one the abstract names first) with its default
   configuration. For an analysis or benchmark paper: the first diffusion model named in the abstract, else
   the first diffusion row of the first results table. Write its name in focal_model. Study-level and design
   fields describe the focal model; S07 lists every own model (analysis and benchmark: every evaluated
   diffusion model).
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
E3 CELL evidence ("cell_evidence" array, ids C01, C02 ...) for every value taken from a table, and for
   settings read from a hyperparameter table. Fields: page (of the row); where ("Table 3"); row_label = the
   whole row label exactly as printed, including "w/o", citations and markers; first_col = position, counted
   from 1, of the first token you quote among the tokens that follow the row label in the file; cells = the
   tokens from first_col on, exactly as they appear in the file, separated by single spaces (a cell such as
   "-" or "Diffusion" is a token; two values on one line are two tokens); header = a run of the column-header
   tokens as they appear in the file; caption = 6-40 words of the caption starting with "Table n" or
   "Figure n"; occurrence = null unless the same label and cells occur twice on that page (then 1 or 2 ...).
   Row label plus cells at most 40 tokens: for a wide row add a second entry with the same row_label and a
   larger first_col. Example (text file lines "w/o diffusion denoising", "57.1", "58.4", "47.7"):
   {"id": "C04", "cond": "K02", "page": 7, "where": "Table 3", "row_label": "w/o diffusion denoising",
   "first_col": 1, "cells": "57.1 58.4 47.7", "header": "Method TF TB BA", "caption": "Table 3: Ablation
   results for DiffuseDef's accuracy under attack on AGNews datasets.", "occurrence": null}.
E4 A value points to its evidence: a cell value gives the cell id and col = the position of the value among the
   tokens after the row label (in E3's example 58.4 is col 2); a prose value gives the prose id and, if the
   number occurs twice in the quote, value_occurrence. value_printed must equal that token exactly.
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
S17 focal_model: see G1.
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
it loads; name it in inherited_from), not_stated, NA. Code the value from the paper's own description; if the
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
S14 main_comparison: where = the first table in reading order containing the focal model's default row and a
   baseline row on the metric of the first comparative claim of the abstract (the first CL from the abstract
   whose types are not "none"); own_row = the default row label as printed; baseline_row = the first row of
   the model or class the claim names (for "outperforms autoregressive models": the first row the paper labels
   autoregressive), else the first baseline row from the top; basis "first-comparative-claim". If the
   abstract has no comparative claim: the F1 table and its first baseline row, basis "F1-table". If no table
   has a baseline row: "NA". QA3-QA6 below refer to this table and these two rows ("the main comparison").

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
   languages, dates, and settings ("with 64 steps" goes in the setting of the number it qualifies).
H-2 If the census F1 number is not in the abstract, one more unit for it (origin F1-table, F1-figure or
   F1-text; value_printed "figure-only" or "unreadable" only here).
Fields: is_F1; origin; value_type (ratio if printed as a factor: x, times, -fold; difference if printed as a
gap: "by 7.56 points", "+3.2", "35% faster"; level otherwise); arm_role (own or baseline for a level; NA
otherwise); reference_printed (for a difference or ratio, the comparator as printed in the same sentence, or
"not stated"; '' for a level); model_printed; metric_printed; metric_kind (G5); higher_is_better;
benchmark_printed ("not stated" if none); split; task_family; value_printed (as printed); value_unit; scale
(fraction 0.61, percent 61.6 or "61.6%", points for a difference in points, raw, factor, other); setting (each
as printed for that number or "not_stated"); variance (kind none, sd, se, ci, range, plusminus-undefined, test,
other; value as printed; n_runs if stated); evidence_ref and col or value_occurrence (E4); column_printed
(column label for a cell value, '' for prose); trace and trace_col (for an abstract number: the table cell that
prints the same number for the stated setting, if you find it; else null); loc {page, where}. [E2-E4]

BLOCK K, COMPARISON GROUPS AND CONTRAST UNITS (ids G01 ..., arms A1 ... within each group, K01 ...)
Terms: an arm is one row (or column, or figure series) that denotes one system configuration; the anchor is
the focal model's default configuration (the row the text calls its method or "ours", or the default named in
the setup).
Go through the tables and figures in reading order (main text, then appendix). For each table or figure:
K-RQ2 If it scores the anchor and at least one arm the paper labels autoregressive for the scored output, on
   a common column: ONE group, rq_class RQ2-vs-ar, arms = the anchor plus EVERY row the paper labels
   autoregressive, in table order. Other baselines are not arms. Analysis or benchmark papers: arms = every
   diffusion row and every autoregressive row, anchor_arm null.
   K-AR: an arm is autoregressive if the paper's table, caption or text labels the generator of the scored
   output as autoregressive, AR, next-token or left-to-right. Judge unified models per output: a model whose
   images come from discrete diffusion is not autoregressive in a text-to-image table. Unlabelled arms: not
   arms of an RQ2 group (say so in notes). Never infer an architecture from a cited paper.
K-F Rows, columns or figure series that are variants of the focal model differing from its default in one
   stated factor: one group per factor, arms = the default (anchor) plus each variant. rq_class:
   RQ3-pretraining, RQ3-adaptation-from-ar, RQ3-sft, RQ3-rl, RQ3-distillation, RQ3-objective-or-architecture
   (a training choice); RQ4-steps (steps, NFE or tokens per step), RQ4-order, RQ4-remask, RQ4-cache,
   RQ4-parallel-or-block, RQ4-value-rule-or-guidance, RQ4-other-inference (an inference setting);
   RQ5-task-removal, RQ5-shared-vs-decoupled (a unified model with a task or modality removed from training, or
   shared against decoupled pathways); credited-other (an arm removes or replaces the credited component and
   no class above fits). Set credited_ablation true whenever an arm removes or replaces the credited component.
   A table varying two factors: one group per level of the second factor (second_factor_printed). A sweep:
   one group, every level an arm, dose_unit and level_num. Analysis or benchmark papers: factor groups for the
   focal model only.
Not groups: comparisons among baselines only; the focal model against non-autoregressive baselines; learning
rate, batch size or warm-up tuning unless presented as an ablation of the contribution; rows already recorded
from an earlier table (first appearance wins).
Group fields: factor_type, factor_printed, dose_unit (steps, nfe, tokens-per-step, threshold, cache-interval,
block-size, gen-length, guidance-scale, temperature, other, NA), where, page, source_kind, orientation (rows,
columns, figure), anchor_arm, held_fixed (stated: the text, caption or table states or shows that only the
factor changes; co-varied: it shows something else changes with the factor; not stated), other_changes ('' if
none stated), budget_across_arms (inference budget: matched, reported, not reported), shape (for a figure
without numbers, on the primary metric: monotone-up, monotone-down, peaked, flat, unclear; else NA),
evidence_refs. [Q for held_fixed stated or co-varied, non-empty other_changes, budget matched: cond = group id]
Arm fields: label_printed (the whole row label, or the column label, exactly as printed), role, generator,
level_printed, level_num (number in dose_unit, else null), params_printed, train_tokens_printed,
shots_printed, scoring (generated, likelihood, not_stated), number_source (run-by-authors if the paper says it
ran the arm; copied-stated if it says the number is taken from a paper; a citation in the row label alone is
not_stated), steps_printed, gen_length_printed. [Q for printed per-arm values not in the value row: cond =
group id plus ".A2" etc., e.g. G03.A2]
Contrast units: one K unit per outcome column of a group (a benchmark-and-metric column with values for at
least two arms). Sub-scores of one benchmark (GenEval categories, MME sub-tasks, per-category accuracies):
only the aggregate column (Overall, Avg., Average, Mean, Total, Score) if there is one, else every sub-score.
Distinct benchmarks: one unit each; skip an average-over-benchmarks column. Speed and step columns are their
own units. Fields: group_id, benchmark_printed, metric_printed, column_printed, metric_kind, higher_is_better,
scale, split, task_family, n_eval_printed (items or samples as printed, or not_stated), figure_only, values
(one per arm present: arm_id, value_printed, cell and col or prose and value_occurrence, variance). A figure
without numbers: figure_only true, every value_printed "figure-only", cell, col, prose null. [E3, E4]

OUTPUT: one JSON object per study, on one line, UTF-8, appended to the output file named in dispatch.json as
soon as that study is done; every id exactly once; on resume skip ids already present. The object must
validate against extraction-schema-v0.2.json. Notes at most 60 words: the ambiguities you met and the rule you
applied.
FINAL MESSAGE: number of records written; for each id the counts of H units, groups, K units, prose entries and
cell entries; the ids in "doubt"; up to five gaps in these rules (rule and one sentence each). Never edit any
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
