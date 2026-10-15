# Census codebook v1.2 (amendment of v1.1, 2026-10-15)

**Disclosure.** v1.2 was written on 2026-10-15, after both codings of the random sample (ranks 1
to 176 of `research/review/census/census-order.csv`) were complete and after agreement was computed
(`analysis/census/agreement-random.log`). Agreement is reported under v1.1, before reconciliation;
v1.2 does not change those figures and must not be used to recompute them. v1.2 governs
adjudication only: the adjudicator applies it to the 158 field-level disagreements in
`research/review/census/disagreements-random.csv`, and to an agreed cell only where the coders'
own notes or F2_detail show the trigger of a v1.2 rule (for example "confidence-ranked, token rule
unstated" under B-15); other agreed cells stand. The author of v1.2 read the protocol, v1, v1.1,
the coder brief, the ambiguity list (`coder-ambiguities-2026-10-15.md`), the disagreement list and
the agreement log, but not the coders' row files or any paper text. Rules are written per ambiguity
class; ranks in parentheses show only where a class was raised and do not decide those rows. Items
tagged [literal] apply text already in the protocol, v1 or v1.1; items tagged [gap] settle a
question those documents leave open. A count that moves because of a [gap] item is reported with
that item named. Whether v1.2 also governs any later coding round is not decided here; if it does,
that round's agreement is computed under v1.2.

v1 and v1.1 stay as the record. Fields and rules not mentioned are unchanged.

## Eligibility (protocol I1; exclusion codes)

**B-1 Inference, serving and systems papers [literal].** Eligible when the paper proposes or
evaluates an inference, decoding, caching, speculative, serving or hardware method for a diffusion
text model or an eligible unified model, even if it reports speed only. F1 = NA when no
generated-sample metric (B-10) of the paper's own method appears in the main text or appendix.
X7 is not used for these papers. Reason: I1 covers a paper that "proposes, analyses, evaluates or
benchmarks" such a model, and protocol section 5 lists "system" as a study type; X7 is for applications of an unchanged
model. (27, 28, 38, 56)

**B-2 Detectors, attacks, probes and scorers [literal].** Eligible when the object of study is a
diffusion text model's outputs, internals, robustness, privacy or likelihoods (detectors of its
hallucinations, attacks on it, membership inference, probes, attention analyses), or when the paper
proposes or adapts a diffusion text generator for any purpose (attacker, drafter, data generator).
X7 when an existing diffusion model is used unchanged as an instrument (feature extractor, ELBO or
likelihood scorer, paraphraser) for a question about something else and the paper reports no
finding about that model. F1 for eligible papers of this kind follows B-10, so detector AUROC,
probe accuracy and one-step token accuracy give F1 = NA. Reason: I1 includes "analyses", and X7 is
the protocol's own test for instrument use. (52, 83, 85, 104, 157, 162, 170)

**B-3 Theory and synthetic-token studies [gap].** Eligible when the model is defined over token
sequences and the abstract presents the result as being about language models or text or code
generation, including results shown only on synthetic token tasks. Not eligible (X1 under B-6) when
the abstract presents a generic state-space result and language appears only as a motivating
example in the introduction. Reason: I2 admits theory but I1 requires output that "includes
natural-language text"; the protocol does not say how to treat theory without a text experiment,
and the abstract is the most reproducible place to read what the paper claims to be about.
(128, 142, 158, 165)

**B-4 Unified models with autoregressive text and a diffusion or flow part [literal for the
component; gap for "unified" and "modality"].** Eligible under I1(b) when one model (a shared
backbone, or components trained or fine-tuned jointly and presented as one model) takes another
modality as input for understanding, generates text and that modality, and produces at least one
output with a diffusion, masked-generative or discrete-flow component; the text side may be
autoregressive. "Another modality" means image, video, audio including speech, or another
perceptual signal such as 3D shape. Not eligible: (i) pipelines of separately trained models
joined only at inference, which are judged component by component (the diffusion component then
needs I1(a), else X1); (ii) models whose diffusion or flow part generates robot actions,
trajectories, molecules or other non-perceptual outputs while text is autoregressive (X1 under
B-6). Reason: I1(b) asks for "a diffusion, masked-generative or discrete-flow component", not for
diffusion text; the protocol defines neither "unified" nor "modality", and its own lists (X1,
section 5 modality) name images, audio and video. (2, 35, 114, 119, 120, 123, 137, 150, 151, 154)

**B-5 Autoregressive studies with a diffusion experiment, and what counts as a diffusion component
[literal].** Eligible when any results table or figure, main text or appendix, reports the paper's
own method applied to a diffusion text model or an eligible unified model ("evaluates" in I1);
F1 then follows B-9. Latent diffusion whose latents are decoded to text, including by an
autoregressive decoder, is I1(a). A "diffusion-style", denoising or iterative-refinement operator
inside an autoregressive model is X0 unless some output is produced by a learned reverse of a stated
corruption process (masking, uniform noise, or Gaussian noise on embeddings, simplex or latents), by
discrete flow matching, or by masked-generative iterative decoding. Reason: I1 sets no minimum share
of experiments, and X0 needs a test that does not rest on the paper's wording. (79, 125, 169)

**B-6 Reading of X1 in the census [gap].** X1 = diffusion only for non-text outputs: images,
audio, video, robot actions, molecules, proteins, graphs or abstract states, with no text produced
by diffusion and no eligible unified model. Reason: the protocol's X1 names images, audio and video
only and has no code for other non-text domains; widening X1 keeps one code per record without a new
code. The widening needs a protocol section 10 amendment before the protocol is frozen.

**B-7 Scene text, OCR strings and captions [literal].** Words or sentences of a natural language
count as natural-language text whatever their length or source (scene-text strings, OCR
transcriptions, captions); code counts, as in the coder brief. Strings that are not language
(SMILES, protein sequences, digit grids, abstract symbols) do not, except as tasks of a model that
is eligible on other grounds. Reason: I1 sets no minimum length. (172)

**B-8 Exclusion code order and missing text [gap].** One code per excluded row: the first that
applies in the order X8, X3, X5, X4, X0, X1, X2, X7. X0 (no diffusion, masked-generative or
discrete-flow component) is the coder brief's code for failing I1 on that ground. Rows without
text: eligible NA, exclusion_code NO_TEXT, all F fields NA. X6 is not used, because the census made
no eGateway attempt. Reason: the protocol asks for one code per record but gives no order.

## F1 headline

**B-9 F1 comes from an in-scope task [gap].** The F1 task must be one whose output is produced by
the component that makes the paper eligible: for I1(a), text or code generated by the diffusion
text model; for papers eligible only under I1(b), the output of the diffusion, masked-generative or
discrete-flow component. Apply A-2's order among in-scope tasks only, skipping out-of-scope tasks the
abstract names first (images from a text-eligible paper, molecules, toy tasks). A synthetic token
task is in scope only when the paper has no natural-language or code experiment. A-2's abstract
order still overrides table order. Reason: the census describes value rules in the population I1
defines; an out-of-scope headline describes a different population. (12, 42, 79, 116, 145, 150,
153, 154, 159, 172)

**B-10 Generated-sample metric [literal].** A metric computed on outputs produced by running a
sampler to completion. Not generated-sample: speed, throughput, perplexity or likelihood under the
model, one-step masked-token accuracy, detector or probe scores. A benchmark accuracy counts as
generated-sample unless the paper states that it is likelihood-scored (options ranked by
likelihood). Reason: A-2 skips "likelihood-only" numbers, and coders cannot check a scoring mode the
paper does not state. (82, 149)

**B-11 No in-scope number in the abstract [literal, with one conflict settled].** Use the first
main-text results table that reports the paper's final method on the in-scope main task (B-9);
appendix tables only if the main text has none; a figure only if no such table exists. Skip tables
that report only baselines or unmodified models. Within the table: the metric the text quotes, else
the first generated-sample metric column; the row the text quotes, else the configuration the method
or setup section names as default, else the first row of the final method (v1). A-2's best-row rule
applies only when the table has a plain and a guided or best-of variant of the final method. If the
only in-scope table is an ablation, use the default configuration's row or column. Reason: v1 says
"first row" and A-2 says "best row"; this order removes the conflict. (19, 99, 145, 163, 166, 168,
172)

**B-12 Missing or garbled cells [literal].** Do not change table, row or column because of the
extraction. Read the cell from the arXiv PDF or HTML of the same version (the paper's own text, as
v1 allows); if still unreadable, take the number from prose that quotes the same cell; else
F1_value = unreadable, and F2 to F6 are coded for the chosen row as usual. Reason: the F1 choice
must not depend on the quality of the text extraction. (34, 36, 37, 40, 161, 166)

## F2 value rule

**B-13 Conflicting statements [gap].** A caption or experiment-section statement for the F1
experiment overrides a hyperparameter table, which overrides a method-level definition. Statements
about baselines or other models in the same table do not apply to the paper's own method. Two
conflicting statements at the same level: NS, both quoted. Reason: A-3 lists the sources but not
their order. (34)

**B-14 U versus NS: how much must be stated [literal, A-3 made item by item].** U needs, for the
F1 setting and through any A-3 route: (1) the value distribution (temperature 1, "sampled from
p_theta", ancestral or standard sampling, or a named sampler whose definition fixes these); (2) for
samplers that choose positions, the position rule (random, scheduled, left-to-right or blockwise);
(3) no truncation, guidance or selection, shown by an explicit statement or by a sampler-settings
list or hyperparameter table for the experiment that names none (such a list is read as complete).
"Temperature 1.0" alone, without (2) and (3), is NS. A method-level definition counts under A-3(b)
when the experiment evaluates the method by name and the definition leaves no value parameter
free; background or preliminaries describing earlier samplers do not count. A headline that matches
a row of another table is an inference, not a statement. A temperature described as tuned or chosen
per task without values is NS for the temperature part (A-6). Reason: makes "states" in A-3
checkable. (9, 92, 93, 107, 108, 112, 129, 132, 139, 154)

**B-15 Confidence-ranked or threshold unmasking without a token rule: new letter C [gap].**
Positions chosen by a confidence, margin, entropy or threshold score of the model's predicted
distribution ("low-confidence remasking", confidence-based or threshold-based parallel unmasking),
with the token rule not stated: code C. If the token rule is stated, code A (argmax value) or S
(sampled value, temperature in T) instead. C is non-plain. A planner that uses the denoiser's own
token probabilities (self-planning) is scored the same way. A position order that does not read the
predicted distribution (random, fixed order, a separate planner that does not read it) is not a
value-rule letter; record it in F2_detail. Reason: both resolutions (A and S) are non-plain, so NS
would undercount non-plain headlines while A or S would assert a rule the paper does not state; the
framework (framework-v2 D item 4) treats the confidence-ranked sampler as its own case.
(57, 110, 122, 134, 139, 140, 148, 154, 164)

**B-16 Training-only settings [literal].** Settings stated only for training rollouts, RL
sampling, data generation, distillation or teacher sampling are not the evaluation value rule. Code
NS for the part they would fill unless the evaluation section says the same settings are used.
Reason: A-3 asks for the rule behind the reported numbers. (19, 79)

**B-17 Best-of-N and filtering as M [gap].** M when the reported number is computed on outputs
chosen among complete candidates by a score available at inference time without ground truth (model
likelihood, reward model, verifier, validity or syntax check, MBR, reranker), including rejection of
invalid outputs before the metric is computed. Not M: oracle metrics that use the evaluation's
ground truth over N samples (pass@k, best-of-N against references or hidden tests); write
"oracle@N" in F2_detail and code the per-sample rule. If the text does not say whether the
selecting score uses ground truth, code M and note it. Reason: M describes the sampler; an oracle
metric describes the evaluation, and pass@k is already handled by F3. (111, 125)

**B-18 Beam, best-first and tree search [gap].** M, with "beam B", "best-first" or "tree search"
in F2_detail; the token rule inside each candidate is coded as usual. Reason: these keep and return
candidates chosen by a sequence score, which is the selection M names. (132)

**B-19 Particle and SMC resampling [gap].** Resampling among particles is M. When the weights or
potentials include an external reward, classifier or constraint, add G. Weights from the model's
own likelihood ratios only: M, with "SMC, own-likelihood weights" in F2_detail so these rows can be
split out later. Reason: resampling selects among candidates; an external potential tilts the
target as reward guidance does. (17, 22, 48, 116)

**B-20 Reward and constraint steering as G [literal widening of v1 G].** G covers any
sampling-time change to the per-step distribution or update by an external score: classifier-free
and classifier guidance, reward or value gradients, constraint gradients, and hard constraints
(grammar or validity masks applied per step). Record the scale, or "hard", in F2_detail. Rewards
used only in training are not G. Per-step rejection of a token by an external rule is G; rejection
of a whole output is M (B-17). Reason: v1 already lists reward guidance, and a hard constraint is a
reward at infinite scale. (138, 156, 163, 166)

**B-21 Combining letters, and G or M with an unstated token rule [gap].** List every stated
letter. When the base token rule (the A, T, P, S, C or U part) is not stated, append NS: "G+NS",
"M+NS". G or M without NS means the base rule is stated and otherwise plain (U is absorbed). U never
combines with a letter. A excludes S and T for the same step (temperature 0 is A); conflicting
statements go to B-13. Reason: separates "guided, base rule unknown" from "guided, otherwise
plain". (34, 77, 91, 166)

## F3 diversity

**B-22 Diversity metrics not on the v1.1 list [gap].** An unlisted metric counts when it is
computed over several samples of the same setting, or over the token distribution of the
generated text, changes with the variety among outputs, and is presented by the paper as diversity,
entropy, repetition or coverage: unique or distinct ratios, repetition rates, number of clusters or
modes, pairwise dissimilarity among samples (BLEU, edit or embedding distance), uniqueness of
generated strings or molecules, Vendi. Not counted: quality or fidelity scores, generative
perplexity, novelty against training data, best-of-N reward, validity. A-1's pairing rule still
applies. Reason: a criterion classifies new metric names the same way for both coders; a closed list
does not. (44)

## F4 to F6 step sweeps

**B-23 Adaptive step counts [literal, A-8 made precise].** A sweep is the paper's own method at
two or more settings that differ in denoising steps, NFE or tokens per step, on the same task and
output length, with a step measure printed for each setting (steps, NFE, tokens per step or average
decoding steps) and a generated-sample metric. The setting may be fixed directly or through a
threshold, schedule or cache interval. Not a sweep: step counts that change only because output
length changes; figures that print throughput, latency or speed-up without a step measure. Exactly
two settings is partial (A-8). Reason: RQ4 needs quality against steps; length-driven NFE is not a
step choice, and speed is not a step count. (60, 84, 86, 89, 96, 97, 98, 109)

**B-24 Sweeps on another task or axis [gap].** The sweep must be on the F1 task (same benchmark
or dataset, any generated-sample metric); A-8's multi-task clause applies to every paper with more
than one benchmark. Sweeps over particles, candidates, beam width, guidance strength or guidance
compute, outer-loop iterations, or block size across separately trained models are not step sweeps:
F4 = no unless another sweep qualifies, with the sweep noted. A block-size sweep on one trained model
counts if B-23 holds. Reason: F5 and F6 ask about the F1 setting, and on other axes the width or the
model changes together with the steps. (7, 16, 17, 22, 39, 82, 152, 166)

**B-25 "co-varied" as an F5 or F6 value [literal].** Kept from v1. Used only when the text or a
table shows that the value rule (F5) or guidance setting (F6) differs between step settings of the
sweep, for example greedy at one setting and sampling at another. A selection or guidance procedure
applied identically at every budget is not co-varied; code stated or not stated under A-9. F5 and F6
are coded when F4 is yes or partial. F5 = NA when F4 is no or NA. F6 = NA when F4 is no or NA or
F2 has no G. Reason: v1 defines co-varied as a stated change, and coders also used it for procedures
that only scale with the budget. (99, 166, 172, 175, 176)

**B-26 Blanket "all experiments" sentences [literal, A-9 applied].** An experiment-level sentence
covering all experiments ("greedy decoding in all experiments", "CFG scale 4 throughout") makes F5,
or F6, stated when the sweep is among the experiments it covers and no other sentence gives the sweep
a different rule. A method-level default stays not stated (A-9). Reason: such a sentence states the
rule for every row of the sweep, which is what A-9 asks. (84, 86, 96, 97, 98, 109)

## Vocabulary and missing data

**B-27 Values for the merged file.** Lower case for eligible and F3 to F6; upper case for F2
letters and exclusion codes.

| Field | Allowed values | Normalise from |
|---|---|---|
| eligible | yes, no, NA | Y, y, Yes, true to yes; N, n, No, false to no; NA only with NO_TEXT |
| exclusion_code | NA (eligible yes); X0, X1, X2, X3, X4, X5, X7, X8 (eligible no); NO_TEXT (eligible NA) | "" or "none" on an eligible row to NA |
| F0_version | vN, NA | |
| F1_task, F1_metric, F1_location | free text; NA when F1_value is NA; F1_metric NA when QL | |
| F1_value | number as printed (with unit), figure-only, unreadable, QL, NA | "curves only" to figure-only |
| F2_codes | letters from A T P S C G M in that order joined by "+", optionally ending "+NS"; or exactly U, NS or NA | reorder letters; "NS+G" to "G+NS"; "U+G" to "G" |
| F2_detail | free text: temperature value or "T>1", scale or "hard", "oracle@N", beam width, final rounding (A-4), variants (A-5) | |
| F3 | yes, no, NA | |
| F4 | yes, partial, no, NA | |
| F5, F6 | stated, not stated, co-varied, NA | "Co-varied", "covaried" to co-varied |

Couplings: eligible no or NA gives F0 to F6 = NA; F1 = NA gives F2 to F6 = NA; F1 = QL gives F2
coded and F3 to F6 = NA; F5 and F6 as in B-25. Parse F2_codes by splitting on "+", not by
searching for letters, because the tokens NS and NA contain the letters S and A.

**B-28 Missing data and denominators.** NO_TEXT rows leave every denominator and are reported as
missing. Excluded rows leave the F denominators. F1 = NA rows are counted and reported but leave the
F2 to F6 denominators; QL rows enter F2 only. NS is a reported category, not missing data. An
unreadable F1 value keeps the row in F2 to F6. Derived classes for reporting: non-plain = yes if
F2_codes contains any of A, T, P, S, C, G, M (with or without +NS), no if U, unknown if NS or NA;
base rule determinable = no if F2_codes is NS or ends in +NS.
