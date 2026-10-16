# Full-text screening rules v1.2 (screener copy)

This is the normative rule text for full-text screening (Paper 1). It names no record and states no
earlier screening outcome. The audit copy with examples and reasons is held by the orchestrator;
screeners do not open it, any other screening file, or anything under research/review/corpus/.

## A. Definitions

**D1 Text.** A token sequence in the vocabulary of a natural language or of a programming, query,
markup or proof language, produced by the model's own decoder or tokenizer (words, sub-words,
characters). The test is the vocabulary, not the task: a natural-language model that writes a
label, a code such as an ICD code, a chess move or a SMILES string in its text vocabulary produces
text. The following are not text: outputs of a task-specific head over a fixed set of classes
(tag sequences, class ids, start and end positions or boundaries of spans); special tokens added for
a task (progress, success, action tokens); embeddings and hidden states; pixels, including words
drawn inside an image; audio or speech tokens; and sequences of models whose vocabulary is a
non-language alphabet (amino acids, nucleotides, SMILES or SELFIES symbols, tree notations, board or
grid cells, symbolic music events, graph or table encodings).

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

**D4 Other modality (D0020 wording):** image, video, audio or speech, or 3D. "3D" is read as any
output or input that the paper represents as three-dimensional geometry: 3D coordinates, meshes,
parametric 3D body or face models, point clouds, voxels, implicit fields, 3D Gaussians, including 3D
human pose and motion. Not other modalities: 2D keypoints and 2D trajectories, robot actions and
trajectories, molecules and proteins (D0020), cell profiles, graphs, tables, time series. If a
record reaches I1(b) only through 3D human pose or motion, set `body3d: true`.

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
- **R7 Non-language domains.** A model whose vocabulary is a non-language alphabet (D1) does not
  produce text, however the paper names it. Go to R9.
- **R8 Theory and general methods.** Include only if R6 holds: a natural-language or code dataset,
  task or sample of the paper's own method appears in a result (main text or appendix). The title,
  the abstract or the model's name never decides. Otherwise R9.
- **R9 Non-text diffusion output: X1 or X2.** Apply in this order. (1) If the paper's own method
  generates text autoregressively and its diffusion component generates only robot actions,
  trajectories, molecules or another output outside D4: X1, `xsub: "ar-text+nontext"` (D0020).
  (2) X2 if text (D1), written by a person or by another component such as an LLM, is an input of the
  diffusion component (prompt, caption, instruction, plan, transcript, lyrics, source sentence,
  program). Class labels and category ids are not text inputs. (3) Otherwise X1.
  Set `xsub`: "t2x" (text-conditioned generator), "nlp-label" (NLP task with label, tag or span
  output), "pipeline" (LLM or VLM with a diffusion generator that fails R10), "ar-text+nontext",
  "theory-no-text" (R8), "nontext" (anything else).
- **R10 Unified models (I1(b)).** All three must hold:
  (b1) the model understands: it produces text (D1) from an input in a D4 modality, shown in the
  paper's own experiments or stated in the paper for the same weights the paper uses;
  (b2) it generates a D4 modality with a diffusion component (D2) or a masked-generative component
  (iterative masked-token prediction); text may be autoregressive;
  (b3) it is "one model (shared weights or one jointly trained system), not a pipeline of separately
  trained models" (D0020). Shared weights: understanding and generation run through at least one
  common set of trained parameters (a shared backbone; shared attention in a mixture of
  transformers). One jointly trained system: at least one training stage, in this paper or in the
  work that produced the weights it uses, updates parameters on the understanding side and on the
  generation side in one optimisation. A frozen understanding model whose output feeds a separately
  trained or newly trained generator is neither. A text interface is allowed if the system is
  jointly trained. Naming ("unified", "omni", "any-to-any") does not count.
  If any of b1-b3 fails, judge components separately: R6 for a diffusion component that writes text,
  else R9.
- **R11 Modalities.** Use D4. Set `body3d: true` when I1(b) rests on 3D human pose or motion only.
- **R12 Action, driving, navigation and world models.** Actions, trajectories, waypoints and progress
  or success tokens are neither text nor a D4 modality. Include only through R6 or R10 (for example,
  goal images generated by diffusion count for b2 if b1 and b3 hold). Otherwise R9.
- **R13 Non-generative use (encoders, embeddings, estimators, scorers, classifiers).** Applies when
  the paper's final model does not generate. Include if (a) the paper's own method trains a diffusion
  component on text at some stage (for example it performs the diffusion pretraining itself), (b) it
  reports results about a text diffusion model's likelihoods, internals, outputs or robustness, or
  (c) it compares a text diffusion backbone with a non-diffusion backbone. Otherwise: X7 if an
  existing text diffusion model is used unchanged as an instrument; X0 if an existing one is
  fine-tuned into a non-generative model (nothing in the paper generates by diffusion); R9 if the
  diffusion model is over non-text data.
- **R14 Applications and systems that generate with an existing text diffusion model or unified
  model.** Include if (a) the paper trains or fine-tunes it as a generator, changes its sampler,
  decoding, caching, schedule, remasking or guidance, or proposes an inference, serving or hardware
  method for it (non-generative fine-tuning is R13, not (a)); (b) a results table compares it with
  another generator (autoregressive or diffusion) on the same task and data; or (c) a results table
  varies a diffusion-specific setting (steps, unmasking order, remasking, block length). Otherwise
  X7. A with-versus-without ablation of the whole module is neither (b) nor (c).

## C. Codes, in the order applied (one code per excluded record: the first that applies)

| Order | Code | Meaning |
|---|---|---|
| 1 | X8 | first public version outside 2021-01-01 to the source's search date (filled by script from metadata), or body not in English (R2) |
| 2 | X3 | secondary study (R1) |
| 3 | X5 | another report of a study retained in the review (script, from `dup_of`; R3) |
| 4 | X4 | no method, theory or empirical result: abstract-only publication, poster, slides, demo, blog, editorial |
| 5 | X0 | no diffusion component in the paper's own method (R4, R5, R13) |
| 6 | X1 | non-text diffusion output, not I1(b), and not X2 (R9) |
| 7 | X2 | non-text diffusion output with text as an input of the diffusion component (R9) |
| 8 | X7 | an eligible model used unchanged with no model-level finding (R13, R14) |

X1 and X2 are disjoint by R9, so their order changes no code. A file marked "not retrieved" is not
screened; it is reported as a report not retrieved (X6) before eligibility.

## D. Doubt

If after the required sections and the appendix you cannot settle a condition, set
`"decision": "adjudicate"` and name the condition in `note`. Never resolve doubt by excluding.
The human author adjudicates every "adjudicate" and every disagreement between screeners.

## E. Screener brief (give with this file to Screener A, Claude Sonnet, and Screener B, Claude Opus)

```text
FULL-TEXT SCREENING, Paper 1, rules v1.2. Read research/CONTRACT.md, then this file only
(research/review/screening/criteria-v1.2-screener.md). Screen the full-text files your dispatch
gives, one per record. Do not open any other screening file, decision file, ledger, audit or
anything under research/review/corpus/. Do not look for other versions of a paper.
READ: title, abstract, introduction (contributions), method, experiments (every results table,
figure caption and ablation), conclusion and limitations. Appendix only to settle R6/R8 (a text
result), R10 b1-b3, R13/R14 (what was changed or varied), or D1 (output format).
DECIDE include, exclude or adjudicate (section D). Codes in section C order; stop at the first
that applies. Then eligibility: I1(a) by R6 (with R7, R8, R13, R14); I1(b) by R10 (with R11, R12).
Not eligible: X1 or X2 by R9, with xsub. Eligible: X7 only by R13 or R14. Else include.
R3: put the other record's id in dup_of when your dispatch lists a possible duplicate.
R5: a drafter or component trained with a diffusion objective (D2) makes the paper eligible.
EVIDENCE: one entry per condition that decided the record, each a verbatim quote of at most 40
words copied from the file, with its location "p.<pdf page>, §<section>" or "§<heading>, Table n":
 include I1(a): D2 and R6; include I1(b): b1, b2, b3; R13/R14 include: the (a), (b) or (c) met;
 exclusion: the condition of the code. Quotes are string-matched against the file by script;
 a quote not found is returned to you once, then the record goes to adjudication.
RQ TAGS (include or adjudicate): "RQ1" and "RQ6" always; add, with the table or figure id in rq_loc:
 "RQ2" own results table with an autoregressive baseline on the same task;
 "RQ3" within-paper contrast of a training choice (pretraining recipe, SFT, RL, distillation);
 "RQ4" within-paper contrast of an inference setting (steps, unmasking order, remasking, caching,
       parallel or block decoding);
 "RQ5" I1(b) and (a task-removal or shared-vs-decoupled ablation, a synergy benchmark, or a claim
       that understanding and generation help each other).
mm: "text" (text only), "multimodal" (takes or generates a D4 modality), "other" (other non-text
inputs or outputs, no D4 modality); null if excluded. body3d: true or false. i1: "a", "b", "ab", "".
OUTPUT: one JSON object per record, one line, UTF-8, appended in chunks of at most 10 to the file
your dispatch names; every id exactly once; on resume skip ids already present:
{"id": "<id>", "decision": "include|exclude|adjudicate", "code": "<X8|X3|X5|X4|X0|X1|X2|X7 or ''>",
 "xsub": "<R9 value or ''>", "rules": ["R10", "R11"], "i1": "b",
 "evidence": [{"cond": "b1", "quote": "<verbatim>", "loc": "p.6, §4.2"}],
 "rq": ["RQ1", "RQ5", "RQ6"], "rq_loc": {"RQ5": "Table 4"}, "mm": "multimodal", "body3d": false,
 "x3_scope": false, "dup_of": "", "ft": "<version string from dispatch>", "note": "<= 20 words",
 "screener": "FA-<model id and version>" | "FB-<model id and version>"}
FINAL MESSAGE: counts by decision, code and xsub; ids sent to adjudication with the condition;
up to five gaps in the rules (rule and one sentence each). Never edit any file except your output.
```
