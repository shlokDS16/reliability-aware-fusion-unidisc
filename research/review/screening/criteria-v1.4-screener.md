# Full-text screening rules v1.4 (screener copy)

This is the normative rule text for full-text screening (Paper 1). It names no record and states no
earlier screening outcome. Screeners and the adjudicator work only inside the dispatch folder they
are given, which holds this file, CONTRACT.md and the full-text files (for the adjudicator, also the
two screener rows per record); they open nothing else and use no web access.

## A. Definitions

**D1 Text.** The test is the content of the output, not the tokens that carry it. Text is (a)
natural language: words or sentences of a human language, of any length (answers, labels written as
words, captions, transcripts, translations, OCR or scene-text strings, slot values, reasoning,
mathematical solutions written in words), or (b) source code: a program, query, markup or formal
proof in a programming, query, markup or proof language. Everything else is not text, whatever
tokenizer or vocabulary produces it, including: chemical or biological sequences (SMILES, SELFIES,
amino acids, nucleotides); board, grid or puzzle states and moves in game notation; numbers or
number sequences on their own; arithmetic expressions or equations without words (for example a
target-number puzzle answer); identifiers from a code system; robot actions, trajectories,
waypoints, progress or success signals (also when written with ordinary text-vocabulary tokens);
tags, class ids and span positions or boundaries from a task-specific output; embeddings and hidden
states as final outputs; pixels, including words drawn inside an image; audio or speech tokens;
tree, graph, table and symbolic-music encodings.

**D2 Diffusion component.** A component of the paper's own method (D3) that (i) is trained to
reverse a corruption applied at a range of corruption levels: masking or an absorbing state with a
masking rate that varies across training examples, uniform or other token-substitution noise, or
Gaussian noise on embeddings, simplex vectors or latent vectors; or is trained along a flow-matching
path (discrete or continuous, including rectified flow); and (ii) generates with more than one
denoising or integration step, or with a few-step or one-step sampler distilled from such a
component. A masked-language-model objective at one fixed rate with one-pass prediction is not a
diffusion component. "Diffusion" in the sense of spread (information, innovation, heat, particles),
cryptographic diffusion, graph diffusion kernels and diffusion imaging is not one.

**D3 Paper's own method.** What the paper contributes, as stated in its introduction: the model,
algorithm, system or analysis, with its ablations. If the stated contribution is an evaluation,
benchmark or analysis, the models it evaluates or analyses are its own method. Baselines compared
against a contribution are not.

**D4 Other modality (D0020 wording):** image, video, audio or speech, or 3D. Apply in order:
(1) Not other modalities, and this overrides (2): robot actions and trajectories, driving
waypoints, joint or end-effector commands, and outputs the paper generates as commands for a robot
or vehicle; molecules and proteins; cell profiles, graphs, tables, time series; 2D keypoints and 2D
trajectories. Humanoid case: a generated motion is an action if the paper's main results (results
tables and figures of the experiments section) evaluate it by execution on a robot or in a robot
simulator (success rate, tracking error on the robot); it is (2) if the main results evaluate it as
human motion (motion-quality or text-motion metrics on human motion data). A retargeting or robot
demonstration outside the main results does not make a human motion an action.
(2) "3D" is any output or input that the paper represents as three-dimensional geometry: 3D
coordinates, meshes, parametric 3D body or face models, point clouds, voxels, implicit fields, 3D
Gaussians, including 3D human pose and motion.
If a record reaches I1(b) only through 3D human pose or motion, set `body3d: true` and fill
`code_if_o1_no` with the code the record would get if pose and motion were not "3D" (apply R6,
then R9, ignoring pose and motion as a modality).

**D5 Existing text diffusion model.** A diffusion model (D2) that the paper did not create and that
the file states or shows generates text (D1): the file states that it was pretrained or trained on
natural-language text or code, or describes it as a diffusion (large) language model or LLM without
naming a non-language domain, or shows a text sample or a natural-language or code task result from
it. A model the file describes as a "language model" of a non-language domain (chemical, protein,
DNA, RNA, genomic, cell, music, time-series language model) is not one. A model the paper itself
pretrains on natural-language text or code is judged by R6 or R13(a), not by this definition.

## B. Rules

- **R1 Records first judged on a title or a short abstract.** Screen the full text like any other.
  A document whose stated contribution is a survey, review, tutorial, position or perspective,
  including one that proposes a taxonomy or framework, with no new experiment or proof of its own,
  is X3; set `x3_scope: true` if it covers diffusion language models or unified multimodal diffusion
  models. A survey that runs its own experiments (e.g. a benchmark) is a primary study.
- **R2 Language.** X8 if the main body (method and results) is not in English, whatever the language
  of the title or abstract.
- **R3 Reports of one study.** Two records are one study if they share the method or benchmark name
  and at least one author, and one text is a revision, extension or published version of the other.
  Fill `dup_of` with the other record's id if your dispatch lists it; decide on the content of the
  file you were given. X5 is assigned later by script.
- **R4 Diffusion component (X0).** X0 if the paper's own method (D3) has no diffusion component (D2).
  Baselines do not count. A general method whose experiments include image, audio or video
  diffusion models has a diffusion component: continue with R9.
- **R5 Diffusion models only as baselines.** X0 by R4. Include if any results table applies the
  paper's own method to, or trains it as, a diffusion component (for example a drafter trained with a
  masked denoising objective over a range of masking rates).
- **R6 Text output (I1(a)).** I1(a) holds if a diffusion component (D2) of the paper's own method
  produces text (D1) as the final output of its generation path, in at least one result of the paper
  (table, figure or sample). Judge the decoded output, not the variable denoised: embeddings rounded
  to tokens, latents decoded to text (also by an autoregressive decoder) and token sequences all
  count when the result is text.
- **R7 Non-language domains.** Output whose content is not natural language or code (D1) is not
  text, whatever model produces it and however the paper names it, and such a result never meets
  R6. **Precedence between R7 and R14.** Census codebook v1.2, B-7, in full: "B-7 Scene text,
  OCR strings and captions [literal]. Words or sentences of a natural language count as
  natural-language text whatever their length or source (scene-text strings, OCR transcriptions,
  captions); code counts, as in the coder brief. Strings that are not language (SMILES, protein
  sequences, digit grids, abstract symbols) do not, except as tasks of a model that is eligible on
  other grounds. Reason: I1 sets no minimum length. (172)"
  Therefore R14 overrides R7 for non-language strings: if the paper generates with an existing text
  diffusion model (D5) and meets R14(a), (b) or (c), the record is included by R14 even when every
  output in the paper is a non-language string (chemical or biological sequences, board, grid or
  puzzle states and moves, numbers, equations, identifiers, tags, class ids, spans, tree, graph,
  table or symbolic-music encodings). The override does not cover actions, trajectories, waypoints
  or progress signals (R12 decides) or outputs in a D4 modality such as images or speech (R10, then
  R9 decide). R7 decides alone when the diffusion component is not an existing text diffusion model
  (for example one the paper trains from scratch on non-language content, or a protein or chemical
  "language model"): then the record is eligible only if R6 holds for some other result of the
  paper; otherwise go to R8, then R9.
- **R8 Theory and general methods.** Include only if R6 holds: a natural-language or code dataset,
  task or sample of the paper's own method appears in a result (main text or appendix). The title,
  the abstract or the model's name never decides. Otherwise R9.
- **R9 Non-text diffusion output: X1 or X2.** Apply in this order; the first step that applies gives
  the code. (1) If the paper's own method generates text autoregressively and its diffusion
  component generates only robot actions, trajectories, molecules or another output outside D4: X1,
  `xsub: "ar-text+nontext"` (D0020), also when the text or instruction conditions that component.
  (2) X2 if the paper states, in any section or the appendix, that text (D1) conditions the
  diffusion component, by any path: directly, through a text encoder, or through an LLM, VLM or
  MLLM (frozen or trained), whether the text was written by a person or by another component
  (prompt, caption, instruction, plan, transcript, lyrics, source sentence, program). Text plus
  other conditions is still X2. Class labels and category ids are not text. (3) Otherwise X1,
  including when the paper does not state that text reaches the diffusion component.
  Set `xsub` (first that applies): "ar-text+nontext" (step 1); "nlp-label" (NLP task whose output
  is labels, tags or spans); "pipeline" (an LLM, VLM or MLLM is part of the system and R10 failed);
  "t2x" (text-conditioned generator with a text encoder only); "theory-no-text" (R8);
  "nontext" (anything else).
- **R10 Unified models (I1(b)).** Decide b1-b3 from statements in the screened file only (text,
  figures, tables, appendix); do not use knowledge of the cited works. All three must hold:
  (b1) the model understands: the file shows it producing text (D1) from an input in a D4 modality
  in the paper's own experiments, or states that the weights the paper uses do so;
  (b2) it generates a D4 modality with a diffusion component (D2) or a masked-generative component
  (iterative masked-token prediction); text may be autoregressive;
  (b3) it is "one model (shared weights or one jointly trained system), not a pipeline of separately
  trained models" (D0020). b3 holds if the file states either
  (i) shared weights: understanding and generation run through at least one common set of
  parameters that, as the file states, was trained for generation as well as for understanding, in
  this paper or for the weights used (one backbone or transformer trained for both; shared attention
  in a mixture of transformers; a statement that one backbone or transformer both understands and
  generates counts, unless the file says that backbone is frozen while another component is trained
  for generation), or
  (ii) joint training: a training stage (of this paper, or described in the file for the weights
  used) updates parameters on the understanding side and on the generation side in one optimisation.
  **Sides.** A trained parameter is on the understanding side only if the understanding output of
  b1 (text from the D4 input) is computed with it. Hence: LoRA or other adapters inside the
  understanding model count on the understanding side only if the file reports or states that
  understanding runs with those adapters active; adapters the file confines to generation, or for
  which it states nothing about understanding, count on the generation side. Learnable query
  tokens, connectors, projectors and decoders count on the generation side, also when the queries
  pass through the understanding model. An understanding model that is frozen in every stage the
  file describes is not a common set of parameters for (i), because it was not trained for
  generation. So a frozen understanding model with trained query tokens, a trained connector,
  generation-only adapters or a trained decoder has neither (i) nor (ii), and b3 fails.
  A text interface is allowed if (ii) holds. If the file states neither (i) nor (ii), b3 fails.
  Naming ("unified", "omni", "any-to-any") does not count.
  If any of b1-b3 fails, judge components separately: R6 for a diffusion component that writes text,
  else R9.
- **R11 Modalities.** Use D4 in its order. Set `body3d: true` and `code_if_o1_no` when I1(b) rests
  on 3D human pose or motion only.
- **R12 Action, driving, navigation and world models.** By D1 and D4(1), actions, trajectories,
  waypoints, joint commands and progress or success signals are never text and never a D4 modality,
  whatever tokens encode them. Include only through R6 (the diffusion component also writes text,
  such as answers or reasoning), R10 (for example, goal images generated by diffusion count for b2
  if b1 and b3 hold). R14's precedence over R7 does not apply to actions. Otherwise R9.
- **R13 Non-generative use (encoders, embeddings, estimators, scorers, classifiers).** Applies when
  the paper's final model does not generate. Include if (a) the paper's own method trains a diffusion
  component on text at some stage (for example it performs the diffusion pretraining itself), (b) it
  reports results about a text diffusion model's likelihoods, internals, outputs or robustness, or
  (c) it compares a text diffusion backbone with a non-diffusion backbone. Otherwise: X7 if an
  existing text diffusion model is used unchanged as an instrument; X0 if an existing one is
  fine-tuned into a non-generative model (nothing in the paper generates by diffusion); R9 if the
  diffusion model is over non-text data.
- **R14 Applications and systems that generate with an existing text diffusion model (D5) or
  unified model.** Include if (a) the paper trains or fine-tunes it as a generator, changes its
  sampler, decoding, caching, schedule, remasking or guidance, or proposes an inference, serving or
  hardware method for it (non-generative fine-tuning is R13, not (a)); (b) a results table compares
  it with another generator (autoregressive or diffusion) on the same task and data; or (c) a
  results table varies a diffusion-specific setting (steps, unmasking order, remasking, block
  length). This holds also when its outputs in the paper are only non-language strings (R7
  precedence; not actions, R12, and not D4-modality outputs, R10 and R9); record i1 "a". Otherwise
  X7. A with-versus-without ablation of the whole module is neither (b) nor (c).

## C. Codes, in the order applied (one code per excluded record: the first that applies)

| Order | Code | Meaning |
|---|---|---|
| 1 | X8 | first public version outside 2021-01-01 to the source's search date (filled by script from metadata), or body not in English (R2) |
| 2 | X3 | secondary study (R1) |
| 3 | X5 | another report of a study retained in the review (script, from `dup_of`; R3) |
| 4 | X4 | no method, theory or empirical result: abstract-only publication, poster, slides, demo, blog, editorial |
| 5 | X0 | no diffusion component in the paper's own method (R4, R5, R13) |
| 6 | X1 | non-text diffusion output, not I1(b), and R9 gives X1 (step 1 or step 3) |
| 7 | X2 | non-text diffusion output, not I1(b), and R9 gives X2 (step 2) |
| 8 | X7 | an eligible model used unchanged with no model-level finding (R13, R14) |

X1 and X2 are not decided by this table but by R9, in R9's own order: step 1 gives X1 even when text
conditions the action or molecule component, and outside step 1 X2 needs a stated text condition.
The table order is the census B-8 reporting order. A file marked "not retrieved" is not screened;
it is reported as a report not retrieved (X6) before eligibility.

## D. Doubt and adjudication

If after the required sections and the appendix you cannot settle a condition, set
`"decision": "adjudicate"` and name the condition in `note`. Never resolve doubt by excluding.
Every "adjudicate" and every disagreement between the two screeners goes first to a blind
adjudicator (Screener C, model fixed in section F), who sees only this file, CONTRACT.md, the full
text and the two screeners' rows, and then to the human author as protocol s4 requires.
Every C session is logged when it ends, whatever its outcome (complete, failed, discarded, rerun),
and every logged session is reported. A C session is rerun only for a technical failure or a failed
isolation check, never because of its rulings, and the rerun uses the same model and queue.

## E. Screener brief (give with this file to Screener A, claude-sonnet-5-5, and Screener B, claude-opus-5-5)

```text
FULL-TEXT SCREENING, Paper 1, rules v1.4. Work only inside the dispatch folder you are given.
Read CONTRACT.md there (its rules apply; its pointers to files outside this folder, its graph-memory
step and its YAML report format do not apply here: the OUTPUT below replaces the report), then
criteria-v1.4-screener.md there, then the full-text files, one per record. Open nothing outside the
folder; no web access; do not look for other versions of a paper.
READ: title, abstract, introduction (contributions), method, experiments (every results table,
figure caption and ablation), conclusion and limitations. Appendix only to settle R6/R8 (a text
result), R10 b1-b3, R13/R14 (what was changed or varied), D1 (output format) or D5.
DECIDE include, exclude or adjudicate (section D). Codes in section C order; stop at the first
that applies. Then eligibility: I1(a) by R6 (with R7, R8, R13, R14; R14 overrides R7); I1(b) by
R10 (with R11, R12). Not eligible: X1 or X2 by R9 in its order, with xsub. Eligible: X7 only by R13
or R14. Else include.
R3: put the other record's id in dup_of when your dispatch lists a possible duplicate.
R5: a drafter or component trained with a diffusion objective (D2) makes the paper eligible.
EVIDENCE: at least one entry per condition that decided the record. Each quote is ONE contiguous
passage of at most 40 words, copied character for character from the file: no ellipsis, no
omitted words, no brackets, no added or changed words. If a negation (not, no, never, without...)
comes just before the passage, start the quote with it. If the deciding statement is split, give
two entries for the same condition. Location: "p.<pdf page>, §<section>" or "§<heading>, Table n".
 include I1(a): D2 and R6; include by R14: D5 and the (a), (b) or (c) met; include I1(b): b1, b2,
 b3 (for b3 also the statement that places trained parameters on each side); R13 include: the
 (a), (b) or (c) met; exclusion: the condition of the code.
 Quotes are checked by script (contiguous match, whole words, no preceding negation); a quote not
 accepted is returned to you once, then the record goes to adjudication.
RQ TAGS (include or adjudicate): "RQ1" and "RQ6" always; add, with the table or figure id in rq_loc:
 "RQ2" own results table with an autoregressive baseline on the same task;
 "RQ3" within-paper contrast of a training choice (pretraining recipe, SFT, RL, distillation);
 "RQ4" within-paper contrast of an inference setting (steps, unmasking order, remasking, caching,
       parallel or block decoding);
 "RQ5" I1(b) and (a task-removal or shared-vs-decoupled ablation, a synergy benchmark, or a claim
       that understanding and generation help each other).
mm: "text" (text only), "multimodal" (takes or generates a D4 modality), "other" (other non-text
inputs or outputs, no D4 modality); null if excluded. i1: "a", "b", "ab", "".
body3d: true if I1(b) rests only on 3D human pose or motion; then code_if_o1_no = the code the record
would get with pose and motion not counted as 3D (R6, then R9); else body3d false, code_if_o1_no "".
OUTPUT: one JSON object per record, one line, UTF-8, appended in chunks of at most 10 to the file
your dispatch names; every id exactly once; on resume skip ids already present:
{"id": "<id>", "decision": "include|exclude|adjudicate", "code": "<X8|X3|X5|X4|X0|X1|X2|X7 or ''>",
 "xsub": "<R9 value or ''>", "rules": ["R10", "R11"], "i1": "b",
 "evidence": [{"cond": "b1", "quote": "<verbatim, contiguous>", "loc": "p.6, §4.2"}],
 "rq": ["RQ1", "RQ5", "RQ6"], "rq_loc": {"RQ5": "Table 4"}, "mm": "multimodal", "body3d": false,
 "code_if_o1_no": "", "x3_scope": false, "dup_of": "", "ft": "<version string from dispatch>", "note": "<= 20 words",
 "screener": "FA-claude-sonnet-5-5" | "FB-claude-opus-5-5"}
FINAL MESSAGE: counts by decision, code and xsub; ids sent to adjudication with the condition;
up to five gaps in the rules (rule and one sentence each). Never edit any file except your output.
```

## F. Adjudicator brief (Screener C: claude-fable-5-1, fixed in v1.4; not the model of A or B)

C is claude-fable-5-1 in a fresh session for every queue. If claude-fable-5-1 cannot be run, this
is established and logged before the first full-text row of Screener A or B is written, and C is
then claude-haiku-5-5; the model is not changed after that point.

```text
FULL-TEXT ADJUDICATION, Paper 1, rules v1.4. Work only inside the dispatch folder you are given:
CONTRACT.md (as in the screener brief), criteria-v1.4-screener.md, the full-text files and the rows
of Screeners A and B for the records in your queue. Open nothing else; no web access. You are not
told why a record is in your queue beyond the two rows, and you know no earlier screening outcome.
For each record: read the sections the screener brief names, apply the rules yourself, then decide
include or exclude (no "adjudicate"), with code, xsub, rules, evidence (contiguous verbatim quotes
with locations, as in the screener brief, at least one per deciding condition), body3d and
code_if_o1_no, in the screener row format with "screener": "FC-<C's model id from section F>". Add "basis":
"A", "B" or "neither" (whose reading you followed) and one sentence in note on the condition that
split them.
FINAL MESSAGE: counts by decision and code; the conditions that split A and B most often.
```
