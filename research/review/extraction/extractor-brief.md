# Extractor brief, form v0.1 (draft, 2026-10-20; not frozen)

Give the text block below, with this file, extraction-schema.json and CONTRACT.md, to every extraction
session (EA extractor claude-opus-5-5, EB pilot extractor claude-sonnet-5-5, ER second reader
claude-sonnet-5-5; model ids from the Claude Code harness list). The adjudicator (EC) gets the same block
plus the paragraph at the end. The block is self-contained: it restates the census rules of codebook v1.2
(with v1 and v1.1), rubric v0.2 step 1 and the design-space choices C1-C5, so the session needs no other
file. Plan, field table and scoring: EXTRACTION-PLAN.md (not given to sessions).

```text
DATA EXTRACTION, Paper 1 (critical systematic review of diffusion language models), form v0.1.
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
extraction-schema.json (exact JSON shape and allowed values), then dispatch.json, then the full-text files
fulltext/<id>.txt, one study at a time. Open nothing outside the folder. Do not look for other versions of a
paper, its code or its web page. You know no screening outcome and no earlier extraction of these studies.

WHAT YOU DO. For each study, fill one record: blocks study, design, census, claims, qa, units, evidence,
searched, notes. Leave "meta" null and every field the schema marks x-filled-by "script" null (design_fit,
matched, QA scores, QA3 sub-item c, QA1 sub-item d). Copy id, ft and form_version from dispatch.json; set
extractor to "<role>-<model id>" from dispatch.json. You record what the paper states. You never judge
whether a claim is true, never compute a number the paper does not print, and never infer a setting from a
cited paper.

READ: title page, abstract, introduction (contribution list), method, experimental setup, every results
table and figure caption, every ablation, limitations or conclusion, and the appendix sections that hold
hyperparameters, sampler settings, evaluation details and extra results. Page numbers come from the
"=== page N ===" markers.

GENERAL RULES
G1 Paper's own method: what the paper contributes as stated in its introduction (model, algorithm, system or
   analysis, with its ablations). For an evaluation, benchmark or analysis paper, the models it evaluates are
   its own method. Baselines are not.
G2 As printed: numbers, model names, metric names, dataset names and settings are copied as printed. If the
   paper does not state a value, write "not_stated"; if a field cannot apply, use NA as the schema allows.
G3 Source order for a setting (census B-13): a caption or experiment-section statement for that experiment
   overrides a hyperparameter table, which overrides a method-level definition. Statements about baselines do
   not apply to the paper's own method. Settings stated only for training, RL rollouts, data generation,
   distillation or teacher sampling are not evaluation settings unless the evaluation section says they are.
G4 Doubt: choose the conservative value (not_stated, NS, "not stated", no) and say why in notes. Never guess.
G5 Several models of the paper's own: study-level fields describe the final, main model (the one the
   abstract names first); analysis and benchmark papers list every evaluated model where a field is a list.

EVIDENCE
E1 Every positive value of a field marked Q below needs at least one entry in "evidence" with "cond" equal
   to the field id (S04, D07, F2, QA3d ...), the claim id (CL2) or the unit id (U07). Every negative value
   (no, not_stated, NS, "not stated", none) of a field marked Q needs an entry in "searched": field id ->
   the sections and tables you read, e.g. {"F2": "§4.1, §5, App. C, Table 9"}.
E2 Each quote is ONE contiguous passage of 6 to 40 words copied character for character from
   fulltext/<id>.txt, citations, footnote markers and page headers as they appear: no ellipsis, no omitted
   words, no brackets, no added or changed words. Longer than 40 words: split into two entries with the same
   cond. If a negation or qualifier (not, no, without, w/o, only, frozen, except ...) is in the same sentence
   or the same table row label, include it: a quote with a negation word in the 6 words before it or a strong
   negation in the 3 words after it is rejected by the checking script.
E3 Numbers. For a unit, every printed value of the unit (value_printed, or every entry of values_printed)
   must appear inside a quote whose cond is that unit id. The text file has one table cell per line, so a
   single row is often fewer than 6 words: extend the quote into the neighbouring cells exactly as they
   appear in the file (for example "D3PM-absorbing 256 1.47 OA-ARDM (ours) 250 1.43 ±0.001"), and name
   table, row label and column label in loc and in the unit's loc object. For table and figure units add a
   second quote with the same cond: the caption or header passage (6 or more words) that names the metric or
   the dataset. For abstract units one quote (the sentence) is enough.
E4 loc format: "p.<page>, §<section>" for text; "p.<page>, Table n, row <label>, column <label>" for cells.
   Quotes are checked by script; a quote not accepted is returned to you once.

BLOCK S, STUDY
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
   autoregressively and the diffusion component generates another modality); both (the paper's own model
   generates text both ways); none (no natural-language or code output in the paper). [Q]
S04 state_space of the diffusion component(s) of the paper's own method (list; one value unless the study
   analyses several models): discrete-absorbing (discrete tokens corrupted to a mask or absorbing state:
   masked diffusion, block diffusion); discrete-uniform (discrete tokens corrupted by uniform or other
   substitution noise, including mixtures of mask and substitution noise); discrete-flow (trained along a
   discrete flow-matching path); continuous-embedding (Gaussian noise on token embeddings, on the simplex or
   on logits); continuous-latent (Gaussian noise or a continuous flow on latents of an encoder, including
   image latents); hybrid (diffusion components in two or more of these spaces, e.g. masked text tokens and
   continuous image latents). [Q: the sentence or equation description of the corruption process]
S05 task_families: every family in which the paper's own method has a generated-sample result:
   language modelling (unconditional or prefix-conditioned text generation scored by perplexity,
   likelihood, MAUVE, diversity); reasoning (mathematics, logic, puzzles, planning, multi-step problem
   solving: GSM8K, MATH, Countdown, Sudoku); code (program synthesis, completion, infilling); understanding
   (answers about an input: visual question answering, image captioning, multimodal benchmarks, text
   classification, natural-language inference, knowledge multiple-choice, reading comprehension);
   text-to-image; editing (image or other-modality editing instructed by text); other (anything else:
   translation, summarisation, dialogue, instruction following, text infilling or editing, text-to-video,
   speech, 3D, molecules). Name the tasks put in other in task_other.
S06 primary_task_family: the family of the F1 headline task; NA when F1 is NA.
S07 models: each of the paper's own models, name and parameter count as printed ("not_stated" if absent),
   params_b in billions (null if not stated). [Q per printed count]
S08 base_checkpoints: named pretrained models the paper loads (e.g. a released diffusion LLM it fine-tunes
   or samples from); empty if trained from scratch. [Q if non-empty]
S09 training: training_free yes (the paper states no training), no, not_stated; stages from {pretraining,
   continued-pretraining, adaptation-from-ar (initialised from an autoregressive model), sft, rl,
   distillation, other}; data_named (datasets of the paper's own training, '' if training-free); tokens and
   compute as printed. [Q for training_free yes and for printed tokens or compute; else searched]
S10 main_sampler for the F1 setting: description, steps, NFE, generation length, tokens per step, each as
   printed or "not_stated". Do not compute NFE. [Q for each printed value]
S11 affiliations: institutions on the title page, as printed.
S12 venue_line_text: the venue statement printed in the file (e.g. "Published as a conference paper at ...",
   journal name and volume), copied exactly; "none" if absent.
S13 credited_component: the first contribution the introduction lists (abstract if there is no list), in
   a few words; NA for theory, benchmark and analysis studies with no new component. [Q]
S14 main_comparison: unit id of the main comparison: the comparison behind the first comparative claim in
   the abstract; if none, the F1 unit's table comparing the final method with the first baseline row. If
   that comparison is not otherwise a K unit, create one (rq_class RQ2-vs-ar if the baseline is
   autoregressive, else credited-other). NA if the study compares nothing.

BLOCK D, DESIGN SPACE (the paper's own main model and its F1 sampler; one generation = a sequence of
commit steps on a state s_n of partly revealed or noised tokens plus optional memory)
D01 c1_channel, one entry per generated modality: erasure (absorbing mask), symmetric (uniform
   substitution), erasure-symmetric-mixture, gaussian-embedding, gaussian-simplex-or-logit, gaussian-latent,
   flow-discrete, flow-continuous (incl. rectified flow), autoregressive (that modality is generated left to
   right without diffusion), other, not_stated. [Q per entry]
D02 c2_reveal (which positions are clean together in training, text or only modality):
   independent-shared-level (each position masked independently at one shared level t),
   block (independent level per block, clean prefix of blocks), any-order (prefixes of a random permutation),
   prefix (autoregressive), gaussian-shared-level (one noise level for all positions), gaussian-mixed-
   conditioning (prefix, random or block conditioning masks with a shared noise level), other, not_stated. [Q]
D03 c2_multimodal: shared-level (one level across modalities), clean-input-noised-output, modality-dropout,
   independent-per-modality (separate levels), capped-noise, other, not_stated; NA for one modality. [Q]
D04 c3_predictor (network output): clean-marginals (posterior over clean tokens per position),
   concrete-score-or-ratio, x0-embedding-regression, posterior-mean-embedding (logits turned into an expected
   embedding), noise-or-velocity (continuous noise or velocity prediction), probability-denoiser (discrete
   flow matching probability denoiser), other, not_stated. [Q]
D05 c3_self_conditioning: yes (previous prediction fed back as input), no, not_stated. [Q if yes]
D06 c3_head_layout: single-modality, shared-vocabulary-head (one head over all modalities' tokens),
   separate-heads, text-head-plus-continuous-head (text logits plus a flow or noise head), other,
   not_stated. [Q unless single-modality]
D07 c4_position: rule = left-to-right (one token at a time), random (ancestral masked diffusion), confidence-
   ranked (confidence, margin or entropy ranking of predicted distributions, fixed count per step),
   threshold-adaptive (positions above a confidence threshold, variable count), fixed-order (a schedule not
   reading predictions), learned-planner, all-positions (every position updated each step, no committed set:
   Gaussian or uniform channels), other, not_stated; blockwise = yes (semi-autoregressive blocks), no,
   not_stated. [Q]
D08 c4_joint_draw (values inside one step drawn): independent, ar-head, copula, energy-or-verifier,
   speculative-verification, other, not_stated. [Q unless independent]
D09 c4_multimodal_schedule: joint (both modalities committed in the same pass), sequential (one modality
   finished first), alternating, other, not_stated; NA for one modality. [Q]
D10 c5_revision (can a committed token change later; list): none, explicit-remasking-or-editing, corrector
   (predictor-corrector step), implicit-channel (uniform or Gaussian channels leave every position
   revisable), output-level (reflection or refinement loops over finished samples), other, not_stated.
   [Q; searched for none]
D11 memory (list): none, self-conditioning, exact-cache (KV or feature cache that leaves outputs unchanged),
   approximate-cache (reuse that can change outputs), planner-state, other, not_stated. [Q; searched for none]
D12 levers the paper's own method uses (list): L1 fewer tokens per step or adaptive count; L2 choice of
   weakly dependent position sets (ordering rules, planners); L3 joint draw inside a step; L4 block-wise
   generation; L5 modality-ordered or planned schedules; L6 training (objective, scale, fine-tuning, RL);
   L7 self-conditioning, learned schedules, time warping; L8 distillation into few steps; L9 token-level
   revision; L10 output-level revision; L11 value rules (argmax, temperature, sample-then-filter);
   L12 guidance (incl. modality dropout); L13 exact compute reuse; L14 lossy compute reuse.
D14 other_detail: say what each "other" in D01-D11 is.

BLOCK F, CENSUS (value rule and reporting of the headline result; codebook v1.2 consolidated)
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
   prose that quotes the same cell; else unreadable. Make the chosen number an H unit with is_F1 true.
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

CLAIMS
CT (judge from the abstract only; a type is asserted if the abstract states that advantage for the paper's
   own method or model, with or without a number; several can be yes; a paper with no method has all no):
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
CL list: every checkable claim, i.e. each sentence of the abstract, and each item of the introduction's
   contribution list, that states a number or a comparative direction for the paper's own method. For each:
   claim_id CL1, CL2 ... in order; source; types (CT codes, or "none"); has_number; units = the unit ids that
   carry it (create H or K units as needed); status:
   match (the claimed number appears in a table, figure or results text for the stated setting);
   direction (no number; the stated direction holds for every compared row of the table it refers to);
   partial (holds for some benchmarks or settings while the claim states no such restriction);
   unsupported (no table, figure or results text carries it);
   contradicted (the paper's own table shows the opposite for the stated setting).
   [Q per claim: the claim sentence, cond = CL id]

BLOCK QA (answer yes or no per sub-item from the full text; leave score null; "main comparison" = S14)
QA1 a: the paper gives a URL to code for its own method; b: it names a commit, tag, release version or an
    archive DOI for that code; c: release is only promised ("will be released") or on request. Leave d null.
QA2 a: the weights of every model behind the main result are released or are public checkpoints named with
    a source (link or hub id); b: the data the main result needs (evaluation benchmarks, and training data if
    the main result is a trained model) are public and named, or released; c: a missing part is only
    promised or on request.
QA3 a: prompts, templates or the few-shot setting are stated (yes also when the task has no prompt by
    design, e.g. unconditional generation); b: steps or NFE and the generation length are stated for the main
    result; d: hardware is stated. Leave c null (computed from F2).
QA4 a: the main comparison reports results of two or more runs, seeds or sample sets; b: it states three or
    more; c: repeated runs are reported only for some other result.
QA5 a: an interval, standard deviation or standard error with stated meaning, or a defined significance
    test, is given for the main comparison; b: such uncertainty is given only for other results, or the main
    comparison has a plus-minus whose meaning is not stated.
QA6 n: the main comparison has no baseline (then leave a-d null); a: parameter counts of the own model and of
    every baseline in it are stated; b: they are within a factor of two, or the paper states they are matched;
    c: an inference budget (steps, NFE, tokens or time) is stated for every arm; d: a training budget (tokens or
    compute) is stated for every trained arm, or stated as matched.
QA7 n: there is no credited component (S13 is NA) (then leave a-c null); a: a table or figure compares the
    method with and without the credited component (or with it replaced by a standard alternative); b: that
    comparison states, or its table shows, that everything else is held fixed (same model, data, budget);
    c: there is an ablation only of a different or a sub-component. Mark the K unit of that comparison
    credited_ablation true.
QA8 sub empty ({}); it is computed from CL statuses.
QA9 a: a section or paragraph presented as limitations (or future work that names a weakness of the
    method); b: at least one failure case, negative result or setting where the method is worse is shown or
    described.
    For each QA item give loc ('' when every sub-item is no). [Q per yes, cond = QA<n><letter>, e.g. QA5a;
    searched for each no that an appendix could have answered]

UNITS (unit ids U01, U02 ... in order of appearance; the schema gives every field)
H, headline number: (1) every quantitative result in the abstract, any metric and model, one unit per
   number; (2) in each main results table (the first main-text table reporting the final method on an
   in-scope task; one per in-scope task family), every cell of the final method's default row, one unit per
   benchmark x metric. Baseline rows are not H units. Fields: is_F1, source_kind, model (row label),
   own_method, metric, metric_kind (generated-sample, likelihood, speed, other), higher_is_better, dataset,
   split, task_family, value_printed (as printed), value_num, value_unit, setting (steps, NFE, tokens per step,
   generation length, sampler, value rule, guidance, each as printed for that number or "not_stated"),
   params_printed, variance (kind none, sd, se, ci, range, plusminus-undefined, test, other; value as printed;
   n_runs if stated), loc. [E3]
K, within-paper contrast: one unit per series = one table or figure block, one factor, one metric, one
   dataset, one base model, two or more levels with their printed values (a two-factor table gives one series
   per level of the other factor). Record a contrast only if it falls in one of these classes, or if it
   removes or replaces the credited component (credited-other):
   RQ2-vs-ar: the diffusion model against an autoregressive baseline on the same task in the paper's own
     table (levels: the two arms; arm_params_printed per arm; ar_baseline_source run-by-authors,
     copied-from-citation, or not stated);
   RQ3-pretraining, RQ3-adaptation-from-ar, RQ3-sft, RQ3-rl, RQ3-distillation, RQ3-objective-or-architecture:
     a training choice changed;
   RQ4-steps (steps, NFE or tokens per step), RQ4-order (unmasking order), RQ4-remask, RQ4-cache,
     RQ4-parallel-or-block, RQ4-value-rule-or-guidance, RQ4-other-inference: an inference setting changed;
   RQ5-task-removal, RQ5-shared-vs-decoupled, RQ5-synergy-benchmark: in a unified model, a task or modality
     removed from training, shared against decoupled pathways, or a benchmark built to measure synergy.
   Do not record tuning of learning rate, batch size or warm-up unless the paper presents it as an ablation of
   its contribution. Fields: rq_class, credited_ablation, factor, levels, values_printed (aligned; write
   "figure-only" for every level of a figure without numbers), values_num, metric, metric_kind,
   higher_is_better, dataset, split, task_family, model, held_fixed (stated: the text, caption or table states
   or shows that only the factor changes; co-varied: it shows something else changes with the factor; not
   stated), other_changes (what else the paper says changes, '' if none stated), budget_across_arms
   (matched, reported, not reported), arm_params_printed, ar_baseline_source (NA unless RQ2-vs-ar), setting,
   variance, loc. [E3; Q also for held_fixed stated or co-varied, non-empty other_changes, budget matched,
   printed arm parameters, and the baseline source unless not stated or NA]

OUTPUT: one JSON object per study, on one line, UTF-8, appended to the output file named in dispatch.json
as soon as that study is done; every id exactly once; on resume skip ids already present. The object must
validate against extraction-schema.json. Keep notes to at most 60 words: the ambiguities you met and the
rule you applied.
FINAL MESSAGE: number of records written; for each id the counts of H units, K units and evidence entries;
fields you answered with doubt (id and field); up to five gaps in these rules (rule and one sentence each).
Never edit any file except your output.
```

## Adjudicator paragraph (EC only; append to the block above)

```text
ADJUDICATION. Your folder also holds the records of two extractors for each study (records-<id>.jsonl).
You are not told which extractor is which beyond their role labels, and you know no other outcome. For each
field, unit and claim on which the two records differ, read the full text yourself and write the final value
under the rules above, with evidence as in E1-E4. Units: decide for each unit found by only one record
whether the rules require it; for units in both, rule each differing field. Write one final record per study
with "extractor": "EC-<model id>". In notes (the 60-word limit does not apply to you) write one line per
ruled item: field or unit, basis "EA", "EB"/"ER" or "neither", and the condition that split them. Items you cannot settle from the text: keep
the conservative value and list them in your final message for the human author.
```
