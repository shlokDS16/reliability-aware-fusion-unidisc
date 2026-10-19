```yaml
agent: method-architect
date: 2026-10-20
brief: data-extraction and quality-appraisal instrument for Paper 1, with a pilot plan (no extraction run)
sources_examined:
  - research/CONTRACT.md
  - research/review/protocol.md (s1, s3 'Version rated', s4, s5, s6, s7, s10 amendments D0020-D0032)
  - research/ledgers/decisions.jsonl (D0005-D0011, D0015, D0020, D0021, D0030, D0032, D0034)
  - git show 8c53fe9 (protocol diff of the suspension commit)
  - research/review/evaluability-rubric.md (v0.2); research/review/reliability/RESULTS.md
  - research/review/framework-v2.md; research/review/framework-v1.md s1 and s3 (C1-C5 and lever table)
  - research/review/coverage/census-codebook-v1.md, -v1.1.md, -v1.2.md (F1-F6)
  - paper/review/OUTLINE.md; paper/review/sections/05-rq-evidence.tex
  - analysis/screening/ft-t1/t1-decisions-all.jsonl (fields and counts only)
  - research/review/screening/criteria-v1.6-screener.md (s A, D, E, F)
  - tools/ft_dispatch.py; analysis/screening/quote_check.py; tools/ft_isolation_check.py
  - research/review/feasibility/stage2/summary-steps.md and one row of contrasts-steps.jsonl (unit format)
  - research/progress.md RESUME block and the 2026-10-16 user-decision line
coverage: >
  Read the sections listed. Not read: protocol s2-s3 search strings in full, PLAN.md beyond the gate
  table rows, the census adjudication notes, any paper's full text except one table of M00285 used to
  test that a table-row quote passes quote_check.py. No extraction was run and no sample was drawn.
claims:
  - statement: Hypotheses E1-E3 and the claim-evaluability theme are suspended (D0008) and stay suspended under D0009; the protocol text (s6) still carries them without a s10 amendment.
    status: supported
    evidence: decisions.jsonl D0008, D0009; protocol.md s6 and s10; OUTLINE.md row 2.10
    level: E2
    confidence: 0.95
  - statement: quote_check.py enforces the 6-word minimum but not the 40-word maximum, and verifies that a passage exists, not that a number belongs to the named row or column.
    status: supported
    evidence: analysis/screening/quote_check.py lines 57 (MIN_WORDS) and 132-161 (quote_status)
    level: E3
    confidence: 0.95
  - statement: A single linearised table row in the PyMuPDF text is often under 6 words, so a cell quote must extend into adjacent cells.
    status: supported
    evidence: scratchpad test on research/sources/md/fulltext-pymupdf/M00285.txt Table 1 ('OA-ARDM (ours) 250 1.43 ±0.001' -> too_short; extended passage -> found)
    level: E3
    confidence: 0.9
competing_explanations: []
unknowns:
  - extraction time and token cost per paper (the pilot measures them)
  - field-level agreement of every block (the pilot measures it)
next_test: {hypothesis: "two isolated extractors using form v0.1 reach the thresholds of s10.4 on 12 randomly drawn included studies", intervention: "pilot of s10", primary_metric: "pooled QA weighted kappa and unit-identification F1", falsifier: "any threshold of s10.4 missed after two revision rounds", gpu_hours: 0}
```

# Extraction and quality-appraisal plan, form v0.1 (draft, 2026-10-20; not frozen)

Status: a specification. Nothing here is a result. No extraction has been run and the pilot sample has
not been drawn. Every threshold below is fixed before any extraction row exists.

## 1. Purpose

Protocol s5 asks for one extraction form with fixed categories, from which every table in the paper is
generated; s6 asks for a quality appraisal (QA1 to QA9, QA10 recorded) of every included study. This
instrument does both in one record per study, so that:

- section 4 (design space) can count C1 to C5 over all included studies, not only the 47 purposive models
  (framework-v2 D1; OUTLINE s4);
- section 5 (evidence by RQ) gets its contrasts and comparability fields (RQ2 to RQ5) and its appraisal
  distributions (RQ6) (OUTLINE s5; 05-rq-evidence.tex says no verdict may be written before this exists);
- section 6 (census) can be extended from the random sample to all included records "through the
  extraction form ... a second independent extractor, agreement reported before reconciliation"
  (framework-v2 D2, E3), coded under codebook v1.2 as D0020 item 2 requires for the full-corpus round;
- supplement S4 (field-level agreement) and S6 (per-study extraction and appraisal tables) are produced
  by script from the records.

Population: the studies included at full text. Today that is the 608 includes of tranche T1
(`analysis/screening/ft-t1/t1-decisions-all.jsonl`: i1 = a 555, b 38, ab 15; nonlang_only 12); later
tranches (the 797 re-check frame candidates, if screened) join under the same form. How many of them get
the unit blocks is open question OQ-01.

## 2. Decisions this instrument relies on, and how it treats what was suspended

| Decision | What the instrument takes from it |
|---|---|
| D0005, D0006, D0007 | review of matched within-paper contrasts; cross-paper regression descriptive only; "meta-analysis" only if the s7 threshold is met. So the contrast unit (K) is the pooling unit and carries everything s7 needs. |
| D0008 | suspends hypotheses E1-E3 and the claim-evaluability organising theme. The instrument has **no evaluability field**, no rubric step-2 items (a/b per claim type), no rubric step-3 flag as a hypothesis input, and no computation of E1, E2 or E3. |
| D0009 | keeps them suspended; "quality appraisal becomes a descriptive component". QA1 to QA9 are scored descriptively and used only for distributions and sensitivity analysis (protocol s6: never to exclude). |
| D0011 | the census fields (value rule, entropy reported, sweep with value rule fixed) are to be added to the extraction form and extended to all included records with a second extractor: block F. |
| D0015, D0021 | both coders after Codex are Claude models; the instrument states model ids and treats two Claude models as weaker independence than two model families (reported as a limit). |
| D0020 (item 2) | codebook v1.2 governs the future full-corpus census coding; that round reports agreement under v1.2. Block F is a consolidation of v1, v1.1 and v1.2 and must equal v1.2 in effect (gate check in s11). |
| D0032 | the extractor harness copies the screening harness: isolated dispatch folders, session rules that waive user and project routines, isolation check after each session, contiguous 6-40-word quotes verified by script, model ids from the harness list, no fallback models. |
| D0034 | the T1 human validation was not done record by record; screening reliability is A-B agreement only. Consequence here: the plan does not assume human time for second reading or adjudication (OQ-05). |
| route line of `analysis/screening/c-run-log.jsonl` (2026-10-16, Route F) | claude-fable-5-1 runs in this harness and draws no extra spend; it is the recommended extraction adjudicator (OQ-05). |

**Evaluability.** Rubric v0.2 passed claim identification (asserted kappa 0.71, pooled over 240 cells)
and failed the criterion (evaluable-flag kappa 0.33, n = 62) in a development round
(`reliability/RESULTS.md`). The instrument keeps only what passed and what the protocol needs on its own
terms: the six claim types asserted in the abstract (field CT, rubric v0.2 step 1, recorded descriptively
because protocol s5 asks for "claims made in the abstract"), and a claim-to-table agreement status per
checkable claim, which is QA8 (protocol s6), not evaluability. CT5 (unification) had kappa 0.00 in that
round; it is kept but flagged for the pilot (OQ-03). Two cautions:
1. QA8 asks a question close to the failed criterion (does the paper's own table carry the claim). It is
   therefore built from per-claim observable statuses and gets its own pilot threshold (s10.4 P7).
2. The H and K units would allow a headline-versus-controlled comparison like hypothesis E3. Nothing in
   this plan computes it; any such analysis needs a new decision row, and while D0008 stands it can only be
   descriptive (OQ-02).
Name clash: "E1-E3" in protocol s6 are hypotheses; "E0-E5" in CONTRACT.md are evidence levels. This
document writes "hypotheses E1-E3" for the first and "evidence level E2" for the second.

## 3. Field table

Evidence rule codes: **Q** a verbatim quote (6-40 contiguous words, `cond` = the field id) is required
when the value is positive (anything other than no, not_stated, NS, not stated, none, NA, empty);
**S** when the value is negative, an entry in `searched` names the sections read; **L** location only;
**Dv** derived by script (extractor leaves null); **Md** filled by script from corpus or screening files;
**-** no evidence (judgement recorded through another field's quote, named in the row).
"Used by" names the RQ, QA item, paper section (sec) or supplement table (S) that consumes the field.

### 3.1 Metadata (filled by script; the extractor never writes these except M01, M04, M09, M10 copied from dispatch)

| # | Field | Type | Allowed values | Used by | Evidence |
|---|---|---|---|---|---|
| M01 | id | string | record id from dispatch.json | all | Md |
| M02 | meta.bibliographic | object | title, authors, arXiv id, DOI, OpenReview id | sec 2, S6 | Md (corpus records) |
| M03 | meta.first_version_date | date | YYYY-MM-DD | RQ1 counts per year, RQ6 by year | Md |
| M04 | ft | string | full-text version string from dispatch | protocol s3 version rated, S6 | Md |
| M05 | meta.venue_resolved | enum | journal, conference, workshop, preprint, unknown | QA10, RQ6 by venue type | Md (published-version resolution, protocol s3) |
| M06 | meta.i1 | enum | a, b, ab | RQ5 population, sec 4 | Md (screening) |
| M07 | meta.nonlang_only | bool | | reported separately (D0032 item 3) | Md (screening) |
| M08 | meta.tranche | string | T1, ... | flow diagram, S6 | Md |
| M09 | extractor | string | EA/EB/ER/EC-model id | S4 agreement | Md (dispatch) |
| M10 | form_version | string | 0.1 | S4 | Md (dispatch) |

### 3.2 Study block S

| # | Field | Type | Allowed values | Used by | Evidence |
|---|---|---|---|---|---|
| S01 | study.study_type | enum, one | method, theory, analysis, benchmark, system | RQ1, RQ6 strata, QA7 NA rule | - (via S13 quote) |
| S02 | study.modality | enum, one | text, text+image, text+other | RQ1, RQ5, sec 4 | Q if not text |
| S03 | study.text_generator | enum | diffusion, autoregressive, both, none | RQ1 (I1(b) models with AR text), sec 4 | Q |
| S04 | study.state_space | enum list (one, except analysis/benchmark) | discrete-absorbing, discrete-uniform, discrete-flow, continuous-embedding, continuous-latent, hybrid | RQ1 counts per class and year, sec 4 | Q |
| S05 | study.task_families (+ task_other) | enum list | language modelling, reasoning, code, understanding, text-to-image, editing, other | RQ1, RQ2-RQ5 strata | - (units carry them) |
| S06 | study.primary_task_family | enum | as S05, or NA | sec 6 strata, s7 matching | - (must equal the F1 unit's task_family; checked by script) |
| S07 | study.models | list of {name, params_printed, params_b} | number as printed; billions | RQ2 comparability, protocol s5 model size | Q per printed size |
| S08 | study.base_checkpoints | string list | names as printed | s7 independence, RQ3, sec 4 | Q if non-empty |
| S09 | study.training | object: training_free {yes,no,not_stated}; stages {pretraining, continued-pretraining, adaptation-from-ar, sft, rl, distillation, other}; data_named; tokens_printed; compute_printed | as printed or not_stated | RQ3, protocol s5 data and compute, QA6d | Q for training_free yes and for printed tokens or compute; S otherwise |
| S10 | study.main_sampler | object: description, steps_printed, nfe_printed, gen_length_printed, tokens_per_step_printed | as printed or not_stated | RQ4, protocol s5 sampler and NFE, QA3b | Q for each printed value |
| S11 | study.affiliations | string list | as on the title page | s7 "independent groups" | - |
| S12 | study.venue_line_text | string | printed venue line or none | QA10 (with M05) | - (script checks the string occurs in the file) |
| S13 | study.credited_component | string | first listed contribution, or NA | QA7, S01 | Q |
| S14 | study.main_comparison | string | a unit id, or NA | QA4, QA5, QA6 | - (pointer; rule in s5.3) |

### 3.3 Design block D (choices C1-C5, framework-v1 s1 with framework-v2 corrections)

| # | Field | Type | Allowed values | Used by | Evidence |
|---|---|---|---|---|---|
| D01 | design.c1_channel | list of {modality, channel} | modality: text, image, video, audio, 3d, other; channel: erasure, symmetric, erasure-symmetric-mixture, gaussian-embedding, gaussian-simplex-or-logit, gaussian-latent, flow-discrete, flow-continuous, autoregressive, other, not_stated | sec 4 C1 counts, RQ1 | Q per entry |
| D02 | design.c2_reveal | enum | independent-shared-level, block, any-order, prefix, gaussian-shared-level, gaussian-mixed-conditioning, other, not_stated | sec 4 C2 | Q |
| D03 | design.c2_multimodal | enum | shared-level, clean-input-noised-output, modality-dropout, independent-per-modality, capped-noise, other, not_stated, NA | sec 4 C2, RQ5 | Q |
| D04 | design.c3_predictor | enum | clean-marginals, concrete-score-or-ratio, x0-embedding-regression, posterior-mean-embedding, noise-or-velocity, probability-denoiser, other, not_stated | sec 4 C3 | Q |
| D05 | design.c3_self_conditioning | enum | yes, no, not_stated | sec 4 C3, lever L7 | Q if yes |
| D06 | design.c3_head_layout | enum | single-modality, shared-vocabulary-head, separate-heads, text-head-plus-continuous-head, other, not_stated | sec 4 C3, RQ5 | Q unless single-modality |
| D07 | design.c4_position | {rule, blockwise} | rule: left-to-right, random, confidence-ranked, threshold-adaptive, fixed-order, learned-planner, all-positions, other, not_stated; blockwise: yes, no, not_stated | sec 4 C4, RQ4, sec 6 (F2 letter C) | Q |
| D08 | design.c4_joint_draw | enum | independent, ar-head, copula, energy-or-verifier, speculative-verification, other, not_stated | sec 4 C4, lever L3 | Q unless independent by default of the named sampler |
| D09 | design.c4_multimodal_schedule | enum | joint, sequential, alternating, other, not_stated, NA | sec 4 C4, RQ5, open problem P5b | Q |
| D10 | design.c5_revision | enum list | none, explicit-remasking-or-editing, corrector, implicit-channel, output-level, other, not_stated | sec 4 C5, RQ4 remasking | Q; S for none |
| D11 | design.memory | enum list | none, self-conditioning, exact-cache, approximate-cache, planner-state, other, not_stated | sec 4, sec 7 (E_approx), RQ4 caching | Q; S for none |
| D12 | design.levers | enum list | L1-L14 (framework-v1 s3 rows, listed in the brief) | sec 7 lever table (Tab 7) | - (judgement from D01-D11) |
| D13 | design.design_fit | enum | yes, partly | sec 4 misfit paragraph | Dv (yes if no D01-D11 value is other) |
| D14 | design.other_detail | string | text for every "other" | sec 4 limits of the framework | - |

### 3.4 Census block F (codebook v1.2; definitions consolidated in the extractor brief)

| # | Field | Type | Allowed values | Used by | Evidence |
|---|---|---|---|---|---|
| F1 | census.F1_status + F1_unit | enum + unit id | number, figure-only, unreadable, QL, NA; unit id or NA | sec 6, S06 | via the F1 unit's quotes |
| F2 | census.F2_codes | string | letters A T P S C G M in order joined by "+", optional "+NS"; or U, NS, NA | sec 6, QA3c, sec 7 value slot | Q for any letter or U; S for NS |
| F2d | census.F2_detail | string | temperature, "T>1", scale or "hard", "oracle@N", beam width, final rounding, position rule, variants | sec 6 | - (inside F2 quote) |
| F3 | census.F3 | enum | yes, no, NA | sec 6 | Q if yes |
| F4 | census.F4 | enum | yes, partial, no, NA | sec 6, RQ4 | Q if yes or partial |
| F5 | census.F5 | enum | stated, not stated, co-varied, NA | sec 6, RQ4 (P1 reading) | Q if stated or co-varied |
| F6 | census.F6 | enum | stated, not stated, co-varied, NA | sec 6 | Q if stated or co-varied |

### 3.5 Claims

| # | Field | Type | Allowed values | Used by | Evidence |
|---|---|---|---|---|---|
| CT | claims.CT | six yes/no | CT1 steps, CT2 time, CT3 inference quality, CT4 training quality, CT5 unification, CT6 versus autoregressive (rubric v0.2 step 1) | protocol s5 "claims made in the abstract"; descriptive counts in sec 5; RQ5 (CT5), RQ2 (CT6) | - (abstract; CL quotes) |
| CL | claims.list | list of {claim_id, source, types, has_number, status, units} | source: abstract, introduction; status: match, direction, partial, unsupported, contradicted | QA8 | Q per claim (cond = CL n) |

### 3.6 Quality appraisal (sub-items by the extractor; scores by script, rules in s6)

| # | Field | Sub-items (yes/no) | Used by | Evidence |
|---|---|---|---|---|
| QA1 | code released and usable | a URL to own code; b commit, tag, release or archive DOI named; c release only promised or on request; d link check (separate web pass) | RQ6, sensitivity | Q for a, b, c |
| QA2 | weights or data available | a weights of every model behind the main result public with a named source; b data for the main result public or released; c missing part only promised | RQ6 | Q for each yes |
| QA3 | protocol specified | a prompts, templates or shot setting (or none by design); b steps or NFE and generation length; c value rule determinable (Dv from F2); d hardware | RQ6, RQ4 | Q for a, b, d |
| QA4 | variation reported | a two or more runs for the main comparison; b three or more stated; c repeated runs only for another result | RQ6, s7 variance input | Q for each yes |
| QA5 | uncertainty quantified | a defined interval, SD, SE or test for the main comparison; b only elsewhere, or undefined plus-minus | RQ6, s7 | Q for each yes |
| QA6 | matched or reported budgets | n no baseline in the main comparison; a parameter counts of all arms; b within 2x or stated matched; c inference budget of all arms; d training budget of all trained arms or stated matched | RQ6, RQ2 comparability | Q for each yes |
| QA7 | ablation isolates the credited component | n no credited component; a with/without comparison of it; b all else stated or shown fixed; c ablation only of another or a sub-component | RQ6, RQ3 | Q for a, b, c (and the K unit with credited_ablation true) |
| QA8 | claims agree with own tables | computed from CL statuses | RQ6 | via CL quotes |
| QA9 | limitations and failure cases | a limitations section or paragraph; b a failure case, negative result or worse setting shown or described | RQ6 | Q for each yes; S for no |
| (QA10) | peer-review status, recorded not scored | S12 venue_line_text plus M05 | RQ6 strata | as S12 and M05 |

### 3.7 Headline-number unit H (one row per reported number)

| # | Field | Type | Allowed values | Used by | Evidence |
|---|---|---|---|---|---|
| H01 | unit_id | string | U01, U02, ... in order of appearance | all | - |
| H02 | unit_type | const | H | | - |
| H03 | is_F1 | bool | exactly one H unit true when F1_status is number, figure-only or unreadable | sec 6 | - |
| H04 | source_kind | enum | abstract, main-table, figure, text | sec 5, QA8 | - |
| H05 | model | string | row label as printed | sec 5 | in the quote |
| H06 | own_method | bool | | sec 5, RQ2 | - |
| H07 | metric | string | as printed | sec 5, s7 matching | in the quote or caption quote |
| H08 | metric_kind | enum | generated-sample, likelihood, speed, other (codebook v1.2 B-10) | sec 6 F1 rule, s7 | - |
| H09 | higher_is_better | bool or null | | s7 effect sign | - |
| H10 | dataset | string | benchmark name as printed | s7 matching, RQ2 | caption quote |
| H11 | split | string | as printed or not_stated | protocol s5 split | Q if printed |
| H12 | task_family | enum | as S05 | s7 matching | - |
| H13 | value_printed | string | exactly as printed, unit symbols kept | all numbers | Q: must occur inside a quote with cond = unit id (script check) |
| H14 | value_num | number or null | parsed from H13 | s7 | Dv check (script re-parses H13) |
| H15 | value_unit | string | %, x, tokens/s, ... | s7 | - |
| H16 | setting | object: steps, NFE, tokens per step, generation length, sampler, value rule, guidance, each as printed or not_stated | RQ4, s7 budget matching, protocol s5 "sampler/steps" | Q for each printed value not inside the cell quote |
| H17 | params_printed | string | as printed or not_stated | RQ2 | Q if printed |
| H18 | variance | {kind, value_printed, n_runs} | kind: none, sd, se, ci, range, plusminus-undefined, test, other | QA4, QA5, s7 | Q if not none |
| H19 | loc | {page, where, row, column} | page from the "=== page N ===" marker | audit, second reader | L |

### 3.8 Contrast unit K (one row per within-paper contrast or sweep series); shares H01, H02 (value K), H07-H12, H05 (as base model), H16, H18, H19

| # | Field | Type | Allowed values | Used by | Evidence |
|---|---|---|---|---|---|
| K01 | rq_class | enum | RQ2-vs-ar; RQ3-pretraining, RQ3-adaptation-from-ar, RQ3-sft, RQ3-rl, RQ3-distillation, RQ3-objective-or-architecture; RQ4-steps, RQ4-order, RQ4-remask, RQ4-cache, RQ4-parallel-or-block, RQ4-value-rule-or-guidance, RQ4-other-inference; RQ5-task-removal, RQ5-shared-vs-decoupled, RQ5-synergy-benchmark; credited-other | RQ2-RQ5 synthesis, s7 pooling groups | - |
| K02 | credited_ablation | bool | | QA7 | - |
| K03 | factor | string | what changes between arms | RQ3, RQ4 | in the caption or row quote |
| K04 | levels | string list, at least 2 | arm labels or levels as printed, table order | RQ4 dose-response | in quotes |
| K05 | values_printed | string list aligned with K04 | exactly as printed | s7 effect | Q: every value inside a quote with cond = unit id |
| K06 | values_num | number list | parsed | s7 | Dv check |
| K07 | held_fixed | enum | stated, not stated, co-varied | s7 "matched", QA7b, RQ4 P1 | Q if stated or co-varied |
| K08 | other_changes | string | stated differences besides the factor, '' if none stated | s7 matched | Q if non-empty |
| K09 | budget_across_arms | enum | matched, reported, not reported | RQ2, RQ4, QA6 | Q if matched |
| K10 | arm_params_printed | string list aligned with K04 | per-arm parameter counts as printed | RQ2 comparability | Q per printed count |
| K11 | ar_baseline_source | enum | run-by-authors, copied-from-citation, not stated, NA | RQ2 comparability | Q unless not stated or NA |
| K12 | matched | bool | Dv: held_fixed = stated and other_changes = '' | s7 pooling eligibility | Dv |

### 3.9 Record-level

| # | Field | Type | Used by | Evidence |
|---|---|---|---|---|
| R01 | evidence | list of {cond, quote, loc} | quote_check.py; second reader | the quotes themselves |
| R02 | searched | map field id -> sections read | second reader, adjudicator | - |
| R03 | notes | string, at most 60 words | gaps in the rules | - |

Field count: M 10, S 14, D 14, F 7, CT and CL 2, QA 9, H 19, K-only 12, record-level 3: **90 fields**
(sub-items and setting sub-fields are counted inside their field).

## 4. How the fields feed the paper

| Paper item | Fields | Rule |
|---|---|---|
| sec 4 design-space counts, Fig 3, Tab 4 long form S5 | S04, D01-D14, M03, M06 | counts per C value and per year over all extracted records; the 47-model table stays as the pilot (OUTLINE s4 caveat) |
| sec 5 RQ1 | S01-S06, D01, M03 | counts per class and year (protocol s1) |
| sec 5 RQ2 comparability table | K units with rq_class RQ2-vs-ar: K04, K05, K09, K10, K11, H16, H10, H07; QA6 | one row per contrast; pooled only where task family, metric and budget match (protocol s1) |
| sec 5 RQ3 | K units RQ3-*, S09, K07, K08, K12 | matched-contrast synthesis |
| sec 5 RQ4 dose-response | K units RQ4-*, especially RQ4-steps series (K04/K05 levels and values, H16), F4, F5 | P1: only the k = 1 point of a sweep identifies (framework-v2 C); F5 records whether the value rule was held fixed |
| sec 5 RQ5 | M06 in {b, ab}, K units RQ5-*, CT5, CL with CT5, D03, D06, D09 | census of synergy claims against the ablation that supports them |
| sec 5 RQ6, supplement S6 | QA1-QA9 scores, M05, S12, M03 | distributions by year and venue type; sensitivity with and without studies scoring 0 on QA3-QA6 (exact rule set by the statistician before analysis) |
| s7 pooling test | K units with K12 = true, H12/K task_family, H07 metric, S11 groups, H18 variance | at least 8 matched contrasts from at least 5 independent groups sharing task family and metric |
| sec 6 census extension | F1-F6, F1 unit (H07, H08, H13, H19), D07 | under codebook v1.2; agreement before reconciliation reported (D0020 item 2) |
| sec 2 methods, S4 | M09, M10, agreement outputs of s8 and s10 | field-level error rate, agreement tables, disagreement list |

## 5. Units: headline numbers and within-paper contrasts

### 5.1 Headline numbers (unit H): what counts

Protocol s5 asks for "every reported headline number with metric, dataset, split, protocol notes". A
headline number is, for this form:
1. every quantitative result in the abstract (any metric, any model, speed and size included), one unit
   per number; and
2. in each main results table, the cells of the paper's final method in its default configuration, one
   unit per (benchmark x metric) cell. A main results table is the first main-text table that reports the
   final method on an in-scope task (codebook v1.2 B-9 and B-11 order); a paper with several in-scope task
   families has one main results table per family. Baseline rows are not H units; comparisons with them are
   K units (RQ2-vs-ar or credited-other) when they qualify under 5.2.
3. Exactly one H unit is marked is_F1, chosen by the census F1 rule (brief, block F).
No cap is set. The pilot reports units per paper; if the median exceeds 40 H units the definition is revised
(s10.4 P8).

### 5.2 Within-paper contrasts (unit K): what counts

Protocol s5 asks for "every within-paper contrast (what changed, what was held fixed, both values,
variance if given)". This form records every contrast that falls in an RQ2-RQ5 class of K01, plus every
ablation of the credited component (rq_class credited-other if it fits no RQ class). Pure tuning of
optimisation hyperparameters (learning rate, batch size, warm-up) that the paper does not present as an
ablation of its contribution is not recorded. This narrows "every" and is flagged as OQ-06.

One K unit = one series: one table or figure block, one factor, one metric, one dataset, one base model,
two or more levels with their values (the stage-2 inventory format, `feasibility/stage2/contrasts-steps.jsonl`).
A table that varies two factors gives one series per level of the other factor. RQ2-vs-ar units have the
arms "diffusion model" and "autoregressive baseline" as levels, with K10 per-arm parameter counts and K11
the baseline's source. Figure-only series are recorded with values_printed "figure-only" for every level
and values_num null; they count for RQ4 shape descriptions, not for pooling.

`matched` (K12) is derived: held_fixed stated and no other change stated. Pooling eligibility (s7) further
needs the same task family and metric across studies, which the analysis script checks.

### 5.3 Main comparison (used by QA4, QA5, QA6)

The main comparison is the comparison behind the first comparative claim in the abstract (CL1 if its
types include anything but "none"); if the abstract makes none, the F1 unit's table comparing the final
method with the first baseline row. The extractor records its unit id in S14 (a K unit; if the main
comparison is between the own method and a baseline that is not otherwise a K unit, the extractor creates a
K unit with rq_class credited-other or RQ2-vs-ar). S14 = NA when the study has no comparison (theory).

### 5.4 Evidence for numbers

Every unit carries at least one quote with cond = its unit id that contains each of its printed values
(H13 or every entry of K05), and, for table or figure units, one quote of the caption or header that names
the metric or dataset (at least 6 words). PyMuPDF writes one table cell per line; a single row is often
under 6 words (tested on M00285 Table 1), so the cell quote is extended into neighbouring cells as they
appear in the file, and `loc` names the table, row label and column label. quote_check.py then verifies
that the passage exists; it cannot verify that the value belongs to the named row and column, which is
what the second reader checks.

## 6. Quality appraisal: scoring rules and anchors

The extractor answers sub-items (yes or no) from the full text only; a script computes the score. This
follows the lesson of rubric v0.2 (items observable in the text replaced composite judgements) and keeps
the protocol's 0 (absent), 1 (partial), 2 (met). "NA" is added for QA6 and QA7 where the item cannot apply
(OQ-12). Every yes needs a quote with cond = QA<n><letter>; every no where an appendix could hold the
answer needs a `searched` entry.

| Item | 2 (met) | 1 (partial) | 0 (absent) | NA | Score rule from sub-items |
|---|---|---|---|---|---|
| QA1 code | URL to the paper's own code and an identifiable commit, tag, release or archived DOI | URL without an identifiable version, or release only promised or on request | no code statement | - | 2 if a and (b or d); 1 if a or c; else 0. d is null until a separate web link check runs (OQ-11); the score is reported with and without d |
| QA2 weights or data | every checkpoint behind the main result is public with a named source and the data for the main result are public or released | one of the two, or the missing part only promised | neither | - | 2 if a and b; 1 if a or b or c; else 0 |
| QA3 protocol | prompts or shot setting, steps or NFE with generation length, a determinable value rule, and hardware, all stated for the main result | two or three of the four | at most one | - | count of a, b, c, d that are yes: 4 gives 2; 2-3 give 1; 0-1 give 0. c = yes unless F2 is NS, NA or ends in +NS |
| QA4 variation | three or more runs, seeds or sample sets stated for the main comparison | two runs, or several with the count unstated, or repeated runs only for another result | single run or nothing stated | - | 2 if b; 1 if a or c; else 0 |
| QA5 uncertainty | interval, SD or SE with stated meaning, or a defined significance test, for the main comparison | uncertainty only for other results, or an undefined plus-minus on the main comparison | none | - | 2 if a; 1 if b; else 0 |
| QA6 budgets | parameter counts of all arms and inference budget of all arms stated, and parameters within 2x (or stated matched) or training budgets stated for all trained arms | at least one of: all parameter counts, all inference budgets, all training budgets | none of them | main comparison has no baseline (n) | NA if n; 2 if a and c and (b or d); 1 if a or c or d; else 0 |
| QA7 ablation | a with/without (or replaced-by-standard) comparison of the credited component with everything else stated or shown fixed | such a comparison without the fixed-everything-else statement, or an ablation only of another or a sub-component | no ablation | no credited component: theory, benchmark or analysis studies (n) | NA if n; 2 if a and b; 1 if a or c; else 0 |
| QA8 claims vs tables | every checkable claim (abstract plus introduction contribution list) has status match or direction | at least one match or direction, others partial or unsupported, none contradicted | any contradicted, or none match or direction | no checkable claim | from CL statuses as stated |
| QA9 limitations | a limitations section or paragraph and at least one failure case or worse setting | one of the two | neither | - | 2 if a and b; 1 if a or b; else 0 |

Claim statuses (CL): **match** the number in the claim appears in a table, figure or text result of the
paper for the stated setting; **direction** the claim has no number and the stated direction holds for
every compared row of the table the claim refers to; **partial** it holds for some benchmarks or settings
while the claim is stated without that restriction; **unsupported** no table, figure or results text of the
paper carries it; **contradicted** the paper's own table shows the opposite for the stated setting.

QA10 is recorded, not scored: S12 (what the file says) and M05 (the resolved published version).

Protocol s6 also says "Appraisal by two raters as in section 4, weighted kappa reported", which is more
than s5's 10 percent second reading. This conflict is OQ-14; s7 below implements the recommendation.

## 7. Roles, second reading and adjudication

| Role | Model (Claude Code harness list) | What it does |
|---|---|---|
| EA extractor | claude-opus-5-5 | extracts every included study under the frozen form |
| ER second reader | claude-sonnet-5-5 | extracts independently, blind to EA, on (i) a seeded random 10 percent of included studies per tranche and (ii) every study that enters a pooled estimate (protocol s5); under the OQ-14 recommendation also the QA block of every included study |
| EC adjudicator | claude-fable-5-1 (Route F precedent; OQ-05) | sees the form, the full text and both records; rules each disagreeing field; records basis EA, ER or neither |
| human author | Shlok Kumar Goenka | rules what EC marks as unresolved; signs off the pilot verdict |

Independent double extraction is used, not verification of EA's record by ER, because a reader who sees
the first record anchors on it (OQ-04). The 10 percent sample: `random.Random(<seed>).sample(sorted(ids),
ceil(0.10 * n))` over the tranche's include ids, seed fixed in the dispatch log before EA's first row of
that tranche. Studies entering a pooled estimate are known only after extraction, so their second reading
follows the pooling decision; they are reported separately because they are not a random sample.

## 8. Field-level error rate (protocol s5)

For a study r in the random verification sample V and an applicable field f (the final value is not NA by
a coupling rule, or either reader gave a non-NA value), e(r,f) = 1 if EA's value differs from the final
(adjudicated) value, else 0.

- **Scalar and enum fields:** exact equality after normalisation (case, whitespace, list order for sets).
  Error rate per block = sum e / number of applicable (r, f), with a 95 percent interval from a cluster
  bootstrap over studies (2,000 resamples, seed recorded), because fields of one paper are correlated.
- **Free-text fields** (S09 data_named, S10 description, S13, K03, K08, F2d, D14): reported as agreement
  of the derived category only where one exists; otherwise excluded from the error rate and listed.
- **Units:** units are aligned across readers by a key: H (where, row, column, metric, dataset), K (where,
  K01, metric, dataset, model, K03 normalised). Omission rate = final units missing from EA / final units;
  commission rate = EA units not in the final set / EA units; value error rate = matched units whose H13 or
  any K05 entry differs from the final value / matched units; field error rate on matched units as above.
- **QA:** error rate on scores and on sub-items; linear-weighted kappa between EA and ER on scores before
  adjudication, pooled over QA1-QA9 and per item.
- **Census F:** agreement before reconciliation in the format of `analysis/census/agreement-random.log`
  (D0020 item 1), under v1.2.
The error rate is computed on V only; the pooled-estimate studies get their own table.

## 9. Isolation rules for extractor sessions (copied from the screening harness, D0032)

- Each session runs in a uniquely named dispatch folder `<role>-<batch>-<uuid4>` built by a script modelled
  on `tools/ft_dispatch.py`. The folder holds only CONTRACT.md, extractor-brief.md, extraction-schema.json,
  `fulltext/<id>.txt` (the same PyMuPDF text the screeners read), and dispatch.json (ids in a seeded
  shuffle, output file name `EX<role>-<batch>.jsonl`, the ft version string, form version and SHA-256 of the
  brief and schema). For EC also both records. Nothing says why a study is in the batch; no screening row,
  no i1, no census row from earlier rounds is copied in.
- Session rules (they override every user-level and project-level routine): file tools only on paths
  inside the folder; Write or Edit only on the output file; no graph-memory, graphify, Obsidian, rtk,
  skills, agents, web, MCP or tool search; Bash or PowerShell only if unavoidable and only with paths inside
  the folder. A session that breaks a rule is discarded and its batch re-extracted by a new session.
- After each session: `python tools/ft_isolation_check.py <transcript.jsonl> <dispatch folder>` (unchanged;
  it is not specific to screening) and `python analysis/screening/quote_check.py --rows <output> --texts
  <dispatch>/fulltext` (unchanged; it reads `id` and `evidence[].quote`). A quote not accepted is returned
  to the session once; a field still unsupported goes to EC with its value marked unverified.
- Batch size: 3 studies per session (full texts plus the record fit comfortably; screening used 10 records
  but extraction reads every table). At most 3 agents at once (project rule).
- Every session (complete, failed, discarded, rerun) is logged with basename, role, model, ids SHA-256 and
  files SHA-256, as `research/review/fulltext/dispatch-log.jsonl` does for screening.

## 10. Pilot

### 10.1 Sample
A seeded simple random sample of **12** included records from tranche T1.
- Frame: every row of `analysis/screening/ft-t1/t1-decisions-all.jsonl` with `"decision": "include"`
  (608 rows when this plan was written), ids sorted with Python's default string sort.
- Draw: `random.Random(20261105).sample(sorted_ids, 12)`; the drawn ids are then ordered by the dispatch
  shuffle, not by draw order.
- Seed 20261105 was checked unused on 2026-10-20 (grep over analysis/, tools/, research/ for
  20261022-20261031 and 20261100-20261109 found it absent; 20261022-20261029 are taken).
- Before drawing, the SHA-256 of the newline-joined sorted id list and the frame file's SHA-256 are written
  to the pilot manifest; the draw is made by a committed script, not by hand. Not drawn by this plan.
- No redraw for composition. With 53 of 608 includes having i1 b or ab, about one pilot in three contains no
  multimodal study; whether to add a supplementary multimodal draw is OQ-16.

### 10.2 Procedure
1. red-team reviews this plan, the schema and the brief (agent rule: derivation to red-team before
   implementation); fixes go into v0.2 before the pilot if any.
2. lab-engineer builds the four tools of s11 and tests them on a synthetic record.
3. Two independent extractors, EA (claude-opus-5-5) and EB (claude-sonnet-5-5), each extract all 12 in
   four sessions of 3, blind to each other, under s9.
4. Isolation and quote checks per session; schema validation per record.
5. Agreement metrics (10.3) computed by script before any adjudication; then EC adjudicates; then each
   extractor's error rate against the adjudicated record is computed.
6. Wall time and tokens per study recorded from the session logs.

### 10.3 Field-level agreement metrics
- Enum and boolean fields (S01-S04, S06, D01-D11 values, F1_status, F2-F6, CT, H/K enums on matched units):
  raw agreement and Cohen's kappa pooled within each block, Gwet's AC1 beside kappa where prevalence is
  skewed; per-field raw agreement out of 12.
- Set-valued fields (S05, D10, D11, D12, S09 stages): mean Jaccard per record.
- Strings as printed (S07 params, S10, H13, K05): exact match after whitespace normalisation.
- QA: linear-weighted kappa on scores pooled over QA1-QA9 (12 x 9 pairs); per-item raw agreement out of 12;
  sub-item raw agreement.
- Units: identification F1 = 2 |matched| / (|EA units| + |EB units|), separately for H and K; then field
  agreement on matched units.
- Census: F1 unit chosen identically (same table, row, column); F2 exact string agreement.
- Claims: CT pooled kappa over 72 cells; CL status agreement on claims both listed.
- Evidence: first-pass quote acceptance rate; schema validity rate.
Bootstrap intervals over studies are reported with every pooled figure; with n = 12 they are wide, and the
pilot is development evidence, not the agreement the paper reports (that comes from the production 10
percent sample).

### 10.4 Stop and revise rule (fixed before the pilot)
Pass requires all of:
- P1 quotes: at least 95 percent accepted on first check; every quote accepted after one return.
- P2 schema: every record validates after one return.
- P3 study and design categorical fields: pooled kappa at least 0.70 (protocol s4 line) and pooled raw
  agreement at least 0.80; no single field below 8 of 12.
- P4 QA: pooled linear-weighted kappa at least 0.60 (protocol s6 line); no item below 8 of 12 on score.
- P5 census: F1 unit identical in at least 9 of 12; F2 string identical in at least 9 of 12.
- P6 units: identification F1 at least 0.80 for H and 0.70 for K; value exact agreement on matched units at
  least 0.95; K01 agreement at least 0.80 and K07 at least 0.70 on matched K units.
- P7 claims: CT pooled kappa at least 0.60 (rubric v0.2 preset); CL status agreement at least 0.70.
- P8 workload: median H units per study at most 40 (else 5.1 is narrowed).
Outcome:
- All pass: form frozen as v1.0 (git tag `extraction-v1`, SHA-256 of brief and schema in a decision row);
  production starts. Pilot studies keep their adjudicated records.
- Any fail: only the failing fields or rules are revised (v0.2), then a fresh pilot of 12 drawn with
  `random.Random(20261106).sample(sorted(ids minus the first 12), 12)`. At most two revision rounds.
- Still failing after round two: the field is either dropped or kept as descriptive with its measured
  agreement disclosed and excluded from every verdict and pooled estimate; the human author decides and a
  decision row records it (as the rubric v0.2 outcome was handled).
- Isolation failures are not pilot failures: the session is discarded and rerun, and logged.
- If the measured cost per study, times the number of studies the OQ-01 scope implies, exceeds what the
  weekly budget allows, the orchestrator brings the scope back to the user before production.

## 11. Tools to build (lab-engineer; none exist yet; nothing in this folder is executable)

| Tool | Modelled on | Does |
|---|---|---|
| tools/ex_dispatch.py | tools/ft_dispatch.py | builds the s9 dispatch folder; logs to research/review/fulltext/dispatch-log.jsonl with role E* |
| tools/ex_validate.py | new | JSON Schema validation; checks quote_check.py does not do: each quote at most 40 words, every H13 / K05 value inside a quote of its unit, a quote for every Q field with a positive value, a `searched` entry for every S field with a negative value, F2 letter order, couplings of codebook v1.2 B-27, exactly one is_F1, S06 equal to the F1 unit's family, S12 occurring in the file; fills Dv fields (D13, K12, QA3c, QA scores, value_num re-parse) |
| analysis/extraction/draw_pilot.py | tools/census_sample.py pattern | the s10.1 draw and manifest |
| analysis/extraction/agreement.py | analysis/census/agreement_random.py | s8 and s10.3 metrics, unit alignment, bootstrap |
| (gate check) | gate-auditor | block F of the brief is equivalent to codebook v1.2 B-9 to B-28 with v1 and v1.1; any difference is a deviation |

## 12. Deviations and refinements that need a decision row

1. Hypotheses E1-E3 and the evaluability paragraph of protocol s6 are not implemented (D0008, D0009);
   protocol s10 has no amendment recording this (OQ-02).
2. Contrasts narrowed from "every" to RQ classes plus credited ablations (OQ-06); headline numbers defined
   (5.1, OQ-07).
3. QA scored from sub-items with NA for QA6 and QA7 (OQ-12, OQ-13).
4. Independent double extraction instead of verification by the second reader (OQ-04).
5. Extraction scope: protocol s5 "per study" against the user's 2026-10-16 instruction (OQ-01).
6. QA dual rating on all studies or on 10 percent (OQ-14).
7. Extraction from the screened PyMuPDF file rather than "the latest arXiv version" (protocol s3) where they
   differ (OQ-17).
