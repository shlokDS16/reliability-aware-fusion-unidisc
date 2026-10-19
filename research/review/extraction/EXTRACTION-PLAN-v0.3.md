```yaml
agent: method-architect
date: 2026-10-20
brief: revise the extraction and appraisal instrument from v0.2 to v0.3 after red-team audit 2 (Paper 1); recalibrate the gate, make unit keys and the validator unambiguous, replace the multimodal title regex, present the scope options; no extraction run, no sample drawn
sources_examined:
  - research/CONTRACT.md
  - research/review/extraction/EXTRACTION-PLAN-v0.2.md, extraction-schema-v0.2.json, extractor-brief-v0.2.md, OPEN-QUESTIONS-v0.2.md (read in full; unchanged)
  - research/review/audits/2026-10-20-redteam-extraction-v0.2.md (all 21 findings and 3 preconditions)
  - research/progress.md l.279-280 (user decisions 2026-10-16)
  - analysis/screening/ft-t1/t1-decisions-all.jsonl (sha256 962e3171e358a13b8983867a302053b78d98fdc3cf805083fefe4ed88532baaa; 882 rows, 608 include)
  - analysis/screening/ft-t1/t1b0*/FA-*.jsonl, FB-*.jsonl, c/c-t1-*/FC-*.jsonl, c-superseded.jsonl, t1-pending-B.jsonl (field mm); tools/ft-session/refresh_t1.py l.1-32 (which files are canonical)
  - research/review/screening/criteria-v1.6-screener.md l.270-305 (definition of mm)
  - research/review/corpus/new-records-2026-10-15-v2.jsonl (nid), subscription-records-2026-10-15.jsonl (id), research/review/screening/records.jsonl (sid): titles and abstracts of the 608 includes
  - research/review/coverage/census-codebook-v1.2.md l.20-80; research/review/census/harmonisation-notes.md l.40-60 (F1 for studies without an own method)
  - research/sources/md/fulltext-pymupdf/: M07474, M12766, M09530, M13864, M08100 (sections listed in worked-examples-v0.3.md), M03416 l.845-887; sizes and first 6,000 characters of all 608 include texts
  - analysis/extraction/working-v0.2/ (README, gate_oc.py, oc2.py; not reused)
coverage: >
  Read the inputs above in the parts listed. Not read: protocol.md (outside the brief), census codebook beyond
  l.20-80, ft_isolation_check internals, the remaining sections of the five test papers. Every count below
  comes from a script in analysis/extraction/ run on 2026-10-20 with its log beside it (Appendix A). Every
  token figure is inference (E0). No ledger row was added: the brief allows writes only in
  research/review/extraction/ and analysis/extraction/.
claims:
  - statement: Under the screening rule of s2.3, 108 of the 543 i1 = a T1 includes outside nonlang_only are multimodal (C2); frame R has 435 records; all 13 multimodal records the red-team found in v0.2's frame R are in C2.
    status: supported
    evidence: analysis/extraction/strata.py, log strata-log.txt
    level: E3
    confidence: 0.9
  - statement: At n = 60 (3 strata of 20) the gate rule of s10.4 passes an instrument at every good level with probability 0.974 (at least 0.889 in every sensitivity case) and with probability at most 0.071 when any one quantity is at its bad level (simulation; assumptions of s10.6).
    status: supported
    evidence: analysis/extraction/gate_oc.py, log gate_oc-log.txt (seed 20262000)
    level: E3
    confidence: 0.8
  - statement: Applied by hand to the red-team's five test papers, the v0.3 unit rules give one list of groups and units per paper; the remaining judgement is on attributes outside every key.
    status: supported
    evidence: research/review/extraction/worked-examples-v0.3.md
    level: E2
    confidence: 0.6
competing_explanations:
  - The worked examples were written by the author of the rules, who reads them as intended; two independent extractors may still diverge (Stage A measures it).
unknowns:
  - tokens per record, units per record and true agreement of every quantity (Stage A and the gate measure them)
  - which scope reading the user chooses (OQ3-01)
next_test: {hypothesis: "two extractors following brief v0.3 produce the same group and unit keys", intervention: "Stage A (12 records, 5 of them the worked-example papers), then the gate of s10 (60, stratified)", primary_metric: "F1_G and F1_K on Stage A against each other and against worked-examples-v0.3; then the joint gate rule of s10.4", falsifier: "F1_G below 0.6 on Stage A (red-team F-MA1 test), or any gate criterion missed after one re-gate", gpu_hours: 0}
```

# Extraction and quality-appraisal plan, form v0.3 (draft, 2026-10-20; not frozen)

Status: a specification. Nothing here is a result about any paper. No extraction has been run and no sample
has been drawn. v0.1 and v0.2 files stay as they are. Every finding of red-team audit 2 is answered in
`RESPONSE-TO-REDTEAM-v0.2.md`. Sections marked "unchanged" apply as written in EXTRACTION-PLAN-v0.2.md.

## 1. What changed from v0.2

1. Scope: the two readings the user's words allow are set side by side with costs; the plan does not choose
   (s2.1, OQ3-01; F-MA6).
2. Multimodal is derived from the T1 screeners' field mm by a committed script, not from a title regex
   (s2.3; F-MA5). C2 grows from 52 to 108; frame R shrinks from 491 to 435.
3. Unit rules U1-U14 settle the focal model, anchors, replacement against baselines, second factors,
   conditions, repeats, row labels and figures; keys hold no free strings and no judgement fields (s5;
   F-MA1, F-MA2). Worked examples on the red-team's five papers: worked-examples-v0.3.md.
4. Tables are described once (header, leaf-column map, roles, row groups); the validator checks columns,
   row groups, second factors and arms in columns-oriented tables; 35 unit tests are written as data (s6;
   F-MA4).
5. The gate is recalibrated: 15 criteria, each a lower bound against a numerically defined bad level;
   flags, kappas and AC1 are diagnostic; one joint simulation shows the operating characteristics; the gate
   grows to 60 records (s10; F-CR1, F-MA2, F-MA3).
6. One per-record cost table; G7 is a budget check against the total the user approves (s2.8; F-MA7).
7. S14 is anchored on the F1 unit; five readings of the census F1 rule are written out for the
   gate-auditor's equivalence check (s5.6, BRIEF census block).
8. One seed table with disjoint ranges (s2.10); preconditions for Stage A and Stage B as a checklist (s14).

## 2. Scope (user decision of 2026-10-16)

### 2.1 The decision and the two readings it allows
`research/progress.md` l.279-280: "full-text screen ALL records, extract RQ data on a stratified sample + all
multimodal". It is not in the decision ledger (last row D0034). "RQ data" can be read two ways; the words
allow both, and the choice is the user's (OQ3-01):

| | **Option 1: light blocks on every include** | **Option 2: everything on the RQ sample only** |
|---|---|---|
| Reading of "RQ data" | the contrast data only RQ2-RQ5 use (block K) | every field the RQ syntheses use (blocks L, Q, H, K) |
| L + Q + H | all 608 includes | C1 + C2 + the frame-R sample (281) |
| K | C1 + C2 + the frame-R sample (281) | the same 281 |
| Other 327 includes | L + Q + H | screening data only |
| RQ1 counts | census over 608 | census over C1 + C2, weighted estimate over frame R |
| Census extension (D0011) | met | not met; variant 2+F (block F alone on the other 327) meets it |
| Appraisal "every included study" (protocol s6) | met | deviation (281 of 608) |
| Multimodal completion rule (s2.3) | applies | cannot apply (no light pass on the other records) |
| MIN tokens (s2.8) | 53.2M-89.3M | 38.0M-66.5M; 2+F 42.9M-74.7M |

### 2.2 Blocks by population
Block contents are unchanged from v0.2 s2.2 (L light: S01-S17 except S14, I1-I5, D01-D16, F1-F6, CT; Q: CL,
S14, QA1-QA9; H: abstract outcome numbers and the F1 number; K: groups, arms, contrast units; M: metadata
script). Populations follow the option chosen in s2.1. Under Option 1 the 12 nonlang_only includes get L, Q
and H, no K, in their own row (D0032 item 3); under Option 2 they get nothing beyond screening (OQ3-06).

### 2.3 Multimodal: the committed rule (fix for F-MA5)
`analysis/extraction/strata.py` (stdlib; `python -I`), in this order:
1. **C1** = T1 include with i1 in {b, ab}: **53**.
2. mm_final = the screening field mm ("text", "multimodal" = takes or generates a D4 modality: image, video,
   audio or speech, 3D; "other") of the adjudicator C row where C ruled the record and wrote mm; else the
   value screeners A and B agree on; else the one value written; else "split". Canonical files as in
   tools/ft-session/refresh_t1.py (FA-/FB-<batch>.jsonl, FC rows not in c-superseded.jsonl).
3. **C2** = i1 = a, nonlang_only false, mm_final "multimodal": **108**. A split text/multimodal record is C2
   if the keyword rule KW hits its title or abstract (KW: whole-word, case-insensitive list in strata.py:
   multimodal, vision, visual, image(s), video(s), audio, speech, VLM, MLLM, VQA, caption(ing), OCR, x-ray,
   ASR, omni, any-to-any, 3D and their spelled variants).
4. Overrides from `analysis/extraction/strata-overrides.jsonl` (absent now), applied last.
5. **Frame R** = the other i1 = a, non-nonlang_only includes: **435**; **NL** = 12.

Counts of mm_final over the 543 i1 = a records outside nonlang_only: text 410 (384 A=B, 26 C), multimodal 107 (101 A=B, 6 C),
other 17 (15 A=B, 2 C), split other/text 6, split multimodal/text 3. "Other" (molecules, actions, other
non-perceptual outputs) is not multimodal, matching S02.

Borderline ids for one human check (OQ3-04): B1 split, decided by KW: M02955 (C2), M18118, M18656 (frame
R); B2 mm "multimodal" with no keyword in title or abstract (15, all C2): M00285, M05642, M05663, M07324,
M09298, M09321, M10881, M12175, M13247, M14560, M14706, M14711, M16251, M16730, M18406; B3 mm text or other
with a keyword in the title (frame R): M13760, M15613. List hashes in strata-log.txt.

Records the red-team named: M06241, M08240, M09491, M19267, M13756, M04245, M15668, M10855, M16229, M09298,
M08804, M14667, M01397 are all C2 (mm "multimodal" by A and B or by C); M16622 (v0.2's "Revision" false
positive) and M13760 (speech-production model) are frame R (mm "text"); M15684 is C2 (mm "multimodal");
R0963 (Bernini, video; i1 = b) is C1. v0.2's regex rerun on full titles gives 53, not 52, because v0.2
lacked titles for the 15 U- and R-prefixed records (keyed by id and sid in other corpus files).

**Completion rule (Option 1 only):** after the light pass, an undrawn frame-R record whose S02 is text+image
or text+other gets block K in a completion session and enters the multimodal descriptive tables, not the
weighted estimates; the light-pass S02 against mm_final is reported as the rule's misclassification.

**Duplicate works (F-mi10):** strata.py lists 6 candidate pairs (prefix, word-Jaccard >= 0.7 or difflib ratio
>= 0.9): M03951/M16269, M07769/M16343, M09657/M15091, M14067/M14568, M14370/M14372, M16133/M16134. None is
applied until a human lists it in `duplicate-works.jsonl`; a confirmed second id is a report of the first
id's study and leaves the frames.

### 2.4 Frame R: strata, size, draw, weights
- Strata (from files that exist now): anonymous submission (`Anonymous [Aa]uthors?` in the first 6,000
  characters) x text size above the frame median (72,069 bytes). N_h: anon-long 159, anon-short 66,
  named-long 58, named-short 152.
- n = 120, proportional allocation by largest remainder: anon-long 44, anon-short 18, named-long 16,
  named-short 42; weights N_h / n_h 3.614, 3.667, 3.625, 3.619.
- Draw: per stratum h = 0..3 in the order above, `random.Random(20261400 + h).sample(sorted(ids_h), n_h)`
  (s2.10), Python 3.14.3, by `analysis/extraction/draw_rq_sample.py` after the preconditions of s14; frame
  sha256, per-stratum list sha256 and drawn ids go to a manifest and a ledger row before any K session.
- Records with block K in T1: C1 53 + C2 108 + 120 = **281** (plus completion records under Option 1).
  Kish design effect over C1 + C2 + sample 1.37 (effective n 204).
- Later tranches: same rules; seeds 20261500 + 10 x tranche + h.

### 2.5 Precision (frame R, N = 435; strata-log.txt)
95 percent half-width of a study-level share, normal approximation with finite-population correction:

| n | whole frame | subgroup at 50 percent | at 30 percent | at 20 percent |
|---|---|---|---|---|
| 90 | 0.092 | 0.130 | 0.169 | 0.207 |
| **120** | **0.076** | **0.108** | **0.140** | **0.171** |
| 150 | 0.065 | 0.092 | 0.119 | 0.146 |

Frame-R cells for a class at 10-20 percent prevalence (caching, remasking, RL, distillation) have half-widths
near 0.17-0.25 before clustering; they are reported as descriptive unless the census columns (C1, C2) or the
targeted extension (s2.7) cover them (F-mi4).

### 2.6 Estimation (unchanged from v0.2 s2.6; C2 now 108)

### 2.7 Targeted extension for the pooling test (v0.2 s2.7, plus F-mi12)
Unchanged trigger. Records added by the extension, like completion records, form a census of their cell; they
enter the pooled analysis of that cell and the descriptive tables, never the weighted frame-R estimates.

### 2.8 Cost (one per-record table; fix for F-MA7)
`analysis/extraction/cost_options.py` (log cost_options-log.txt). Per record, thousand tokens, E0: EA-LQH
38-55; EA-K 40-80 (widened from 33-53: v0.3 records every qualifying table; the worked examples have 18-130 K
units per record); all blocks by one extractor 78-135; EC per adjudicated record 20-40; EQ 5-10; block F
second extraction plus EC on 30 percent 31-45; second QA rater plus EC on 30 percent 36-57; block F alone
15-25; gate record (EA + EB all blocks + EC) 176-310.

| Component | Option 1 | Option 2 |
|---|---|---|
| EA L+Q+H | 608: 23.1M-33.4M | 281: 10.7M-15.5M |
| EA K | 281: 11.2M-22.5M | 281: 11.2M-22.5M |
| ER 10 percent | 29 with K + 33 without: 3.5M-5.7M | 29: 2.3M-3.9M |
| EC on the ER records | 62: 1.2M-2.5M | 29: 0.6M-1.2M |
| EQ public versions | at most 287: 1.4M-2.9M | at most 118: 0.6M-1.2M |
| Pilot (Stage A 12 + gate 60) | 12.7M-22.3M | 12.7M-22.3M |
| **MIN** | **53.2M-89.3M** | **38.0M-66.5M** |
| REC (+ block F double on the rest) | 70.1M-113.9M | 45.8M-77.9M |
| FULL (+ block F and QA double on the rest) | 89.8M-145.0M | 54.9M-92.2M |
| a re-gate adds | 10.6M-18.6M | 10.6M-18.6M |

Variant 2+F: + 4.9M-8.2M. Sample size: each 30 records change Option 1 by 1.2M-2.4M and Option 2 by
2.3M-4.0M. Stage A replaces the per-record table with measured means before Stage B (s14 B1).

### 2.9 Draft decision row for the scope (for the orchestrator; not entered)
```json
{"id": "<next>", "ts": "<entry time>", "decision": "Paper 1 extraction scope, the user's choice between the two readings of the user decision of 2026-10-16 (research/progress.md l.279-280: 'full-text screen ALL records, extract RQ data on a stratified sample + all multimodal'): [Option 1: light blocks (study, inventory, design, census, claim types), appraisal and headline units on every include, contrast data (block K) on all multimodal + a stratified random sample of frame R | Option 2: every block on all multimodal + the stratified random sample only | Option 2+F: Option 2 plus block F on every other include]. Multimodal = C1 (i1 in {b, ab}) plus C2 (i1 = a, not nonlang_only, T1 screening field mm = multimodal) by analysis/extraction/strata.py at the commit and with the overrides file named here, both with certainty. Frame R sample: n = [120], strata anonymous submission x text size at the frame median, proportional allocation by largest remainder, seeds 20261400 + h, weights N_h / n_h. Package: [MIN | REC | FULL]. Budget ceiling for G7: [tokens]. nonlang_only includes: [L, Q, H, separate row | none].", "options": ["Option 1", "Option 2", "Option 2+F"], "evidence": "research/progress.md l.279-280; research/review/audits/2026-10-20-redteam-extraction-v0.2.md F-MA5, F-MA6, F-MA7; EXTRACTION-PLAN-v0.3.md s2; analysis/extraction/strata-log.txt and cost_options-log.txt (frame analysis/screening/ft-t1/t1-decisions-all.jsonl sha256 962e3171...)", "owner": "user", "reversal": "projected total above the approved budget after Stage A or the gate (fallback ladder s10.5), or the user changes the scope"}
```

### 2.10 Seed table (fix for F-mi3)
Python 3.14.3 is pinned in every manifest. Seeds are disjoint by purpose; none of them appears in v0.1 or v0.2
(retired unused: 20261105, 20261106, 20261111-20261117; the v0.2 simulations used 20261020 and 20261021).

| Purpose | Seed |
|---|---|
| Stage A draw (one generator over the pools of s10.2 in order) | 20261100 |
| Gate draw, stratum h = 0, 1, 2 | 20261200 + h |
| Re-gate draw | 20261300 + h |
| Frame-R sample, T1, stratum h = 0..3 | 20261400 + h |
| Later tranche t, stratum h | 20261500 + 10 t + h |
| ER 10 percent draw, part p (0 with K, 1 without) | 20261600 + p |
| EC labels X/Y (one generator over sorted ids) | 20261700 |
| Gate bootstrap | 20261800 |
| Production bootstraps (error rates, estimates) | 20261900 |
| gate_oc.py simulation, scenario s | 20262000 + s |
| Human gold subset (OQ2-10) | 20262100 |

## 3. Decisions the instrument relies on (unchanged from v0.2 s3)

## 4. Field table
Unchanged from v0.2 s4.1-s4.10 except the edits below, made by `analysis/extraction/make_schema_v03.py`
(extraction-schema-v0.3.json, sha256 bb0ed559c73f96ccfbb71a7476ecbe090580a600a753fa56c7dea89f05da2439; checked
with jsonschema Draft 2020-12 `check_schema` under `python -E -P`).

### 4.11 Edits
| Field | Change | Finding |
|---|---|---|
| R07 table_evidence (new) | one entry per cited table: where, page, orientation, header, header_levels, columns (leaf map), column_roles, row_groups, row_group_role, caption | F-MA4 |
| R02 cell entry | table id replaces where, header and caption; row_group added; cells is a list (one element per table cell, "" for a blank); occurrence counted inside the row group | F-MA4 |
| K05 | condition_printed replaces column_printed (U9) | F-MA1 |
| K13 values | column_printed per value (the leaf at col) | F-MA4 |
| K17 duplicate (Dv), G20 duplicate (Dv) | U12 flags | F-MA1 |
| G02 rq_class | filled by script from factor_type (U8) | F-MA1, F-MA2 |
| G19 anchor_rule (new) | which U3 clause gave the anchor | F-MA1 |
| A14 ar_label_source (new) | U5 place of the autoregressive label | F-MA1 |
| S14 | basis F1-table or first-main-results-table; row_group added (s5.6) | F-MA1, G5 |
| S17 | description per U2 | F-MA1 |
| S18 focal_config (new) | U2e | F-MA1 |
| D16 provenance | adds inherited-from-cited-method | F-mi13 |
| QA4-QA6 sub | if n = yes then a-d null; if n = no then a-d answered | F-mi5 |

Field count: 153 (v0.2 147 + R07, S18, G19, G20, A14, K17).

## 5. Units (fix for F-MA1 and F-MA2)

### 5.1 Principles (v0.2 s5.1, with two additions)
5. No key contains a judgement field (rq_class, factor_type, anchor, credited_ablation are attributes
measured on matched units). 6. Extractors never decide that something repeats; the script does (U12).

### 5.2 Headline numbers H
Generators H-1 and H-2 and value types as v0.2 s5.2. Changes: **key** (U14) = (origin, location): an abstract
number is located by the character offset of its token in the normalised text (from the prose entry and
value_occurrence); an F1-table unit by (where, row_group, normalised row_label, column leaf). value_printed is
out of the key; H attributes (value_type, arm_role, metric_kind) are compared on matched units (gate block
H-attr). **Trace**: a cell equals the abstract number if it does after rounding to the abstract's printed
precision (LLaDA2.1: "892" traces to 891.74).

### 5.3 Comparison groups (rules U1-U13; the brief's block K is the binding text)
- **U1 Reading order.** Every results table and figure, main text then appendix, wherever placed. Nothing is
  skipped for repeating an earlier table (v0.2's "first appearance wins" is deleted).
- **U2 Own, focal, main results, focal configuration.** (a) own = presented as the paper's contribution;
  earlier models of the same authors named as background are not own. (b) Focal model of method, system and
  theory papers = the first own model or method the abstract names; for a training-free method, that method
  on the base model of the first own arm of the main-results table. (c) Analysis and benchmark papers: the
  diffusion model that is an arm in the most main-text results tables and figures; ties: first named in the
  abstract; else first in the main-results table. (d) Main-results table = the first table in the
  experiments or results section with an own (focal) arm. (e) Focal configuration = the default named in the
  setup or hyperparameter section, else the first own arm of the main-results table (rows top-down, then
  columns left to right).
- **U3 Anchor.** The arm whose normalised label equals the focal configuration; else (i) another own model or
  own method of the abstract, in the focal setting or its only arm; (ii) the level named default or baseline
  for this experiment; (iii) the level whose printed values equal the focal configuration's printed values
  in an earlier main-results table on at least one shared column printed at the same scale and differ on
  none; (iv) the first own arm. Analysis and benchmark papers: the stated default level, else null.
  anchor_rule records the clause.
- **U4 K-RQ2.** One group per table or figure panel (and second-factor level) with the anchor (analysis and
  benchmark papers: a diffusion arm) and an autoregressive-labelled arm sharing an outcome column: arms =
  anchor plus every autoregressive-labelled arm (analysis/benchmark: every diffusion and every
  autoregressive arm).
- **U5 K-AR label sources.** This table; a marker the caption defines; another table of the paper labelling
  the same model (equal label, or equal plus one parenthesis) for the same output; the text. Per output; no
  inference from cited papers or names.
- **U6 K-F.** (a) Replacements of the credited component or own method on the same base model form one
  replacement group with the anchor (credited); parameter variants of the own method form one group per
  parameter; arms differing in two or more factors form no group. (b) Only U8 factor types form groups.
  (c) Analysis and benchmark papers: main-text factor groups for any diffusion model; an appendix item only
  for a factor type absent from the main text.
- **U7 Second factor.** One group per level (row group, level-1 column part or legend entry). Measurement
  conditions are not second factors.
- **U8 factor_type → rq_class (script).** model-class → RQ2-vs-ar; pretraining-recipe → RQ3-pretraining;
  ar-initialisation → RQ3-adaptation-from-ar; sft → RQ3-sft; rl → RQ3-rl; distillation → RQ3-distillation;
  objective, architecture → RQ3-objective-or-architecture; steps-or-nfe, tokens-per-step → RQ4-steps;
  order-rule → RQ4-order; remasking → RQ4-remask; cache → RQ4-cache; block-or-parallel →
  RQ4-parallel-or-block; value-rule, guidance → RQ4-value-rule-or-guidance; gen-length, other →
  RQ4-other-inference; task-or-modality-removal → RQ5-task-removal; shared-vs-decoupled →
  RQ5-shared-vs-decoupled; component-removal → credited-other. Definitions in the brief (U8).
- **U10 Figures.** Groups by U4, U6, U7 when a panel plots an outcome against arms or levels; values
  "figure-only" (data labels inside figures are not extracted); one unit per (benchmark, metric) plotted;
  condition series are not units; bar charts of non-autoregressive models only form no group.
- **U11 Labels.** Row label = every line up to the first cell. Key normalisation: quote_check.normalise,
  lower case, trailing citation with a year removed, "(ours)" and markers removed, all whitespace removed.
  Arms of two records match on equal labels, else on label-core (one label equals the other plus one
  trailing parenthesis), reported separately.
- **U12 De-duplication (script).** A contrast (benchmark_id, metric_id, condition, anchor value, arm value;
  for anchorless groups every pair of a diffusion arm with an autoregressive arm, or every pair of levels)
  equal to an earlier one in the same record is flagged duplicate and left out of contrast counts.
- **U13 Group key.** (where, normalised second_factor_printed) and arm-label Jaccard >= 0.5, one-to-one by
  highest Jaccard (ties: lower group id).
Figure-only groups count for RQ4 shape descriptions, never for pooling; F4 and RQ4-steps groups are counted
separately (unchanged).

### 5.4 Contrast units (U9)
One K unit per outcome of a group = (benchmark, metric, condition) with values for at least two arms. Key:
(matched group, benchmark_id, metric_id, normalised condition_printed, split). condition_printed = header
parts above the value's column (rows orientation) or row label and row group (columns orientation) naming
neither benchmark, metric, arm nor second factor, joined top-down with " / ". Sub-score rule unchanged.
**Suite rule (new, OQ3-10):** a table with more than 10 benchmark rows (or columns) and a printed average over
them gives only that average per group; otherwise every benchmark and never an average. Speed and step
columns are their own units.

### 5.5 Alignment (agreement and analysis)
Group match U13; K match within matched groups by the U9 key; value match within matched K units by arm
(U11); H match U14. A (cell, col) pair may carry values of two units only in different groups (unchanged).

### 5.6 Main comparison S14 (anchored on the F1 unit)
where = the table of the F1 unit's cell (an abstract F1 number: its trace's table; no trace: the
main-results table, basis first-main-results-table); own_row = the F1 arm; row_group; baseline_row = the
first autoregressive-labelled arm of that table if the abstract makes a CT6 claim or the study is an analysis
or benchmark study, else the first other arm in reading order (same row group) with a value in the F1 column.
NA if F1_status is NA, QL or figure-only, or no other arm exists. QA3-QA6 are scored on this pair. The F1
rule itself is census codebook v1.2 with the readings C-F1a to C-F1e written into the brief (OQ3-13).

### 5.7 Workload
The worked examples give 18-130 K units per record. The v0.2 median ceilings (H 10, K 30) become inputs of
the budget check (G7): if the projected total exceeds the approved budget, step 1 of the fallback ladder
narrows K to main-text tables plus appendix RQ4-steps sweeps and credited ablations. A per-record cap is
OQ3-15.

## 6. Evidence and the table-aware validator (fix for F-MA4)

### 6.1 Three kinds of evidence
Prose (`evidence`, E01 ...) as v0.2; tables (`table_evidence`, T01 ...); cells (`cell_evidence`, C01 ...)
pointing to a table. quote_check.py is not edited and never sees table or cell entries.

### 6.2 Prose checks (unchanged from v0.2 s6.2)

### 6.3 Table and cell checks (ex_validate.py; imports quote_check.normalise)
Tokenisation of a page: **N1** quote_check.normalise per line; **N2** a line ending in a letter or digit plus
"-" is joined with the next line's first token in two forms, hyphen kept and hyphen dropped, and a label or
header part matches if either form does (as quote_check's de-hyphenated fallback, F-mi8); **N3** a token is
split at ")" or "]" followed by a letter or digit, and at the arrows ↑ ↓ (arrows dropped from header
tokens); **N4** tokens equal to "|" are dropped; **N5** header tokens are compared without enclosing
parentheses; **N6** a line holding only an integer among the last three lines before a page marker is a
footer and is dropped. Value-like token: `^[-+−±]?(\d[\d.,]*|\.\d+)(%|x|×)?[↑↓*†‡]*$` or one of
`- – — n/a N/A ✓ ✗ ×`.

Table entry checks: **header_not_found** (fail) if the header's tokens are not a contiguous run on the page
or the page before; **caption_not_found / caption_length** as v0.2; **map_not_in_header** (fail) if some part
of some leaf does not occur in the header tokens; **column_order_mismatch** (fail, single-level header) if
the leaves do not occur in header order; for a two-level header, order is checked on the bottom-level
parts, and a failure is the warning **column_order_unverified**; **row_group_not_found** (fail) if a declared
row group is not a whole line between the header and the rows that cite it.

Cell entry checks, in order:
1. **row_group_missing** (fail): the table declares row groups and the cell's row_group is ''. The row is
   searched only inside its row-group segment (from the row group's line to the next declared row group's
   line, or the page end).
2. **Row match** (v0.2 step 3 on the segment, with cells joined by spaces and "" elements skipped):
   row_not_found, cells_mismatch, ambiguous_row (occurrence counted inside the segment).
3. **row_start_missing** (fail): no entry of this (table, row_group, row_label, occurrence) has first_col 1.
4. **Row completeness**: the row is complete when, after the last element of the union of its entries, the
   next token is not value-like and begins a line (or the page ends).
5. **row_width_mismatch** (fail): a complete row without "" elements whose element count differs from the
   number of leaves.
6. **too_long** as v0.2 (label tokens plus cell tokens at most 40 per entry).
For each value citing a cell with position col:
7. **value_outside_cells / value_mismatch** (fail) as v0.2, with col counted over elements.
8. **column_mismatch** (fail): column_printed differs from columns[col] (always checked: a value must sit
   under the leaf its own record names).
9. **Column verified** when the row is complete, has no "" element and the table has no column-order failure
   or warning; otherwise **column_unverified** (warning): the unit goes to the second reader with certainty
   and the share of such units is reported.
10. **rowgroup_benchmark_mismatch** (fail): row_group_role benchmark and the unit's benchmark_printed differs
    from the row group. **second_factor_mismatch** (fail): the group's second_factor_printed differs from
    the row group (row_group_role second-factor) or from the level-1 part of columns[col] (column role
    second-factor). **benchmark_column_mismatch / metric_column_mismatch / condition_mismatch** (fail): the
    unit's benchmark, metric or condition differs from the corresponding part of columns[col] or of the row
    label and row group, by column_roles and orientation.
11. **label_row_mismatch** (fail, rows orientation): the arm's label differs from row_label (U11
    normalisation). **arm_column_mismatch** (fail, columns orientation): the arm's label differs from the
    level-1 part (or the whole single-level leaf) of columns[col].
12. **cell_reused** (fail) as v0.2.
Why columns can now fail: a value's column is fixed twice, by its position in a row whose length is checked
against the leaf map and by the leaf name the record gives; the map itself is checked against the header
(membership always, order where the header is single-level). What stays with the second reader: rows with
blanks and two-level headers whose order cannot be confirmed (column_unverified), and the meaning of a value.

### 6.4 Record-level checks (v0.2 s6.4, with these changes)
S14 rows checked on S14's page inside its row group; exactly one anchor per group unless anchor_rule is
"none" (analysis or benchmark groups); every value with "figure-only" belongs to a unit with figure_only true
and then needs no cell or prose (F-mi9); "unreadable" (F1 units only) needs a cell entry that locates the row
and has no value check; QA4-QA6 nulls follow the schema's if/then (F-mi5); every cell's table exists; the
script fills rq_class from factor_type, U12 duplicate flags, and the v0.2 derived fields.

### 6.5 Interface (v0.2 s6.5, schema v0.3)

### 6.6 Unit tests (fix for F-MA4: test cases as data)
`analysis/extraction/validator-tests.jsonl` (35 cases, sha256 in Appendix A; built by
build_validator_tests.py). Each case gives the fixture (a line range of a screened text pinned by sha256, or
an inline synthetic page), the table entry, the cell entries, the values citing them and the expected status
per check. Coverage: the red-team's wrong cells accepted by v0.2, (a) V02-V03, (b) V05, V09-V10, (c)
V12-V13, V15-V16, (d) V17-V18, V20, (e) V21, V23; its correct cells rejected or warned, V07 (glued label), V08
(glued arrows), V22 (hyphen-split header); label extent V26-V28; blanks V24-V25; page footer V35; hyphen
forms V29-V30; figure-only V31-V32; v0.2 T13 and T15 kept as V34 and V33. v0.2 tests T01-T22 stay in force
with the v0.3 entry shape, except T11 (column_printed "AUA"): now column_mismatch (fail), not a warning
(V04). If the built tool gives another status, the engineer reports it and does not edit the test.

### 6.7 What stays with the second reader (see 6.3, end)

## 7. Quality appraisal (unchanged from v0.2 s7 except)
QA3-QA6 are scored on S14 as defined in s5.6 (decision row s13 row 12, OQ3-14); QA4-QA6 nulls are enforced
by the schema.

## 8. Roles, second reading, adjudication, error rate (unchanged from v0.2 s8 except)
Seeds from s2.10 (ER draw 20261600 + p; EC labels 20261700); the ER sample is drawn from the records the
chosen option extracts. Gold subset (OQ2-10): 6 of the 60 gate records, 2 per stratum, seed 20262100.

## 9. Isolation and post-session checks (unchanged from v0.2 s9; schema v0.3 in the dispatch folder)

## 10. Pilot: development stage, then gate

### 10.1 Preconditions: s14.

### 10.2 Stage A, development (n = 12; no pass or fail)
The five worked-example papers (M07474, M12766, M09530, M13864, M08100; expected lists in
worked-examples-v0.3.md, which no session sees) plus 7 drawn with `random.Random(20261100)` over sorted pools
in this order, without replacement across pools: 2 from C1 (1 i1 = ab, 1 i1 = b), 2 from C2, 1 from the
frame-R benchmark/analysis-title pool (24), 1 from frame R + C2 above 133,280 bytes (52), 1 from frame R. EA
and EB extract all blocks blind; EC adjudicates; agreement of EA and EB with each other and with the worked
examples is computed by agreement.py. Rules, examples and lookups are revised; the cost table and gate_oc.py
inputs are updated from Stage A means (s14 B1). Stage A records are not reused.

### 10.3 Stage B, gate (n = 60, stratified random, fresh)
Strata (excluding Stage A ids; `random.Random(20261200 + h)`): G-short 20 and G-long 20 from frame R + C2
(543 records, split at the median size 72,648 bytes: 272 and 271), G-mm 20 from C1 (53). EA and EB extract
all blocks blind; isolation, model, quote and validator checks per session; metrics by agreement.py before
EC sees anything; then EC.

**Metric definitions** (applicable pair = at least one reader non-NA; NA against non-NA is a disagreement;
NA-NA pairs are excluded):
- **M-raw(b)** for blocks S (S01-S10, S13.type, S15, S16, S17, S18, I1-I5), D (D01-D11, D15, D16 entries), F
  (F1_status, F2_codes, F3-F6), QA-sub (every sub-item written), CT (six), **H-attr** (value_type, arm_role,
  metric_kind on matched H units): credit 1 for equal values, Jaccard for set-valued fields (S04, S05, S15,
  D01, D10, D11); sum of credits over applicable pairs, pooled over records.
- **LB90**: 5th percentile of 4,000 stratified cluster-bootstrap resamples (records resampled within gate
  strata), seed 20261800.
- **QA kappa**: per item (QA1-QA7, QA9), linear-weighted Cohen's kappa on the low scores over records with
  both scores non-NA (an item with fewer than 10 such records is left out of the mean and reported); the
  mean over items; LB90 by the same bootstrap, items recomputed in each resample.
- **F1_H, F1_G, F1_K** = 2 |matched| / (|X units| + |Y units|), pooled, matching by U14, U13 and U9.
- **M-val**: share of matched K values (U11 arm match) with equal value_printed after normalisation.
- **M-class**: share of matched groups with equal derived rq_class.
- **M-anchor**: share of records whose F1 unit (origin and location, U14) and S14 (where, row_group,
  own_row, baseline_row, U11 normalisation) are both identical.
- **G1 acceptance**: per extractor, share of evidence entries (prose, table, cell) accepted by the validator
  at first pass.
- **Diagnostics (reported, never gating):** per-field kappa and Gwet's AC1; per-field flags for
  binary-credit fields with n_f >= 15, flagged at agreements <= c(n_f) with P(X <= c | n_f, 0.85) <= 0.01
  (flag_thresholds.py: c(15) 8, c(20) 12, c(25) 16, c(30) 20, c(40) 27, c(45) 31, c(50) 35, c(60) 43);
  Jaccard-credited fields with bootstrap intervals (F-mi6); QA-score raw agreement; column_unverified share;
  label-core match share; anchor_rule agreement; **M-CL** kappa of claim status over the union of claims with
  "missing" for a claim one reader did not list, claims matched when their prose quotes overlap by at least
  half of the shorter quote's tokens in the normalised text (F-mi7), which decides whether QA8 is published;
  each CT type's kappa, which decides whether that type is published.

### 10.4 Decision rule (fixed before the gate; signed by gate-auditor)
**PASS iff every one of the 15 criteria holds:**

| Criterion | Quantity | Good | Bad | Line |
|---|---|---|---|---|
| G1a, G1b | first-pass acceptance, EA and EB | 0.95 | 0.85 | LB90 >= 0.85 |
| G3 S, D, F, QA-sub, CT, H-attr | block raw agreement (6 criteria) | 0.85 | 0.70 | LB90 >= 0.70 |
| G3 QA kappa | mean per-item linear-weighted kappa | 0.70 | 0.40 | LB90 >= 0.45 |
| G4 F1_H | headline-unit identification | 0.85 | 0.70 | LB90 >= 0.70 |
| G4 F1_G | group identification | 0.75 | 0.60 | LB90 >= 0.60 |
| G4 F1_K | contrast-unit identification | 0.75 | 0.60 | LB90 >= 0.60 |
| G4 M-val | K value agreement on matched units | 0.95 | 0.85 | LB90 >= 0.86 |
| G4 M-class | rq_class agreement on matched groups | 0.85 | 0.65 | LB90 >= 0.65 |
| G5 anchors | F1 unit and S14 both identical | 0.85 | 0.60 | at least 43 of 60 |

"Good" is the level at which a quantity is fit for the analyses it feeds; "bad" the level at which it is
not. Two lines sit above the bad level because the percentile cluster bootstrap under-covers there (s10.6).
Removed from v0.2 (F-MA2, F-MA3): the namespaced pooled kappa and its AC1 switch (implied by G3), M-val over
H values (trivial), G6 flags (diagnostic), G2 schema validity (a process requirement: an invalid record after
one return is rerun, like an isolation failure), and G7 as a quality criterion.
**G7 budget check (not a pass or fail of the form):** the projected total, from Stage A and Stage B means per
component and the counts of the chosen option (cost_options.py), must not exceed the budget the user approves
in the scope row; otherwise the fallback ladder of s10.5.

### 10.5 Outcomes
- PASS: flagged fields are revised (text only) and re-measured on the production second reading; the form is
  frozen as v1.0 (git tag extraction-v1, sha256 of brief, schema and lookups in a decision row); production.
- FAIL: the failing criteria's blocks and every rule touching them are revised; a fresh gate of 60 (seeds
  20261300 + h, same strata, excluding every earlier pilot id) re-tests every criterion. One re-gate at most.
  What still fails becomes descriptive only (agreement disclosed, excluded from every verdict and pooled
  estimate) or is dropped; the user decides in a decision row.
- G7 over budget: fallback ladder, each step brought to the user: (1) K narrowed (s5.7); (2) frame-R sample
  120 to 90; (3) C2 moved to completion-only (Option 1) or to the frame (Option 2); (4) H limited to the F1
  unit.
- Isolation, model-check or schema failures are not gate failures: the session is discarded and rerun.

### 10.6 Operating characteristics (gate_oc.py, log gate_oc-log.txt)
Model: per record and metric, agreement drawn from a Beta distribution with the quantity's mean and
intra-record correlation (ICC) 0.10; record effects of different metrics joined by a Gaussian copula with
weight OMEGA (0 = independent, the conservative case for P(pass | good)); units per record Poisson (H 4,
entries 60, H attributes 9) or negative binomial with shape 1.5 (groups 3, K units 8, K values 15); QA scores
0-2 with stated marginals, each rater correct with probability sqrt(kappa) per record, else a draw from the
marginal (so the population weighted kappa equals the target); the same stratified cluster bootstrap (500
resamples per simulated gate) as s10.3; 2,000 simulated gates per scenario. All inputs are assumptions (E0)
and are replaced by Stage A values where Stage A measures them.

**Design n = 60 (3 x 20), ICC 0.10, OMEGA 0, 2,000 simulated gates per scenario; G5 line 43 of 60.**

| Scenario | P(gate passes) | P(that criterion passes) |
|---|---|---|
| every quantity good | **0.974** (MC s.e. 0.004) | lowest marginal: F1_G 0.986, M-class 0.994 |
| G1 acceptance EA bad / EB bad | 0.063 / 0.071 | 0.066 / 0.073 |
| block S / D / F / QA-sub / CT / H-attr bad | 0.058 / 0.066 / 0.066 / 0.062 / 0.065 / 0.061 | 0.059 / 0.067 / 0.067 / 0.065 / 0.066 / 0.061 |
| QA kappa bad (0.40) | 0.009 | 0.009 |
| F1_H / F1_G / F1_K bad | 0.067 / 0.053 / 0.058 | 0.067 / 0.055 / 0.059 |
| M-val bad (0.85) | 0.043 | 0.044 |
| M-class bad (0.65) | 0.070 | 0.073 |
| anchors bad (0.60) | 0.042 | 0.043 |
| every quantity bad | 0.000 | |

**Gate size** (1,000 per scenario; the right column is the largest pass rate over seven single-bad scenarios:
F1_G, F1_K, anchors, block F, QA kappa, M-class, M-val):

| n | P(pass, all good) | max P(pass, one bad) | G5 line |
|---|---|---|---|
| 30 | 0.670 | 0.074 | 23 |
| 36 | 0.808 | 0.062 | 27 |
| 45 | 0.915 | 0.080 | 33 |
| 54 | 0.950 | 0.059 | 39 |
| 60 | 0.973 | 0.067 | 43 |
| 72 | 0.984 | 0.067 | 51 |

**Sensitivity at n = 60** (1,000 per scenario): P(pass, all good) / P(pass, F1_G bad): baseline 0.977 /
0.045; OMEGA 0.5 0.985 / 0.060; ICC 0.20 0.889 / 0.055; ICC 0.20 and OMEGA 0.5 0.925 / 0.054; fewer units
(groups 2, K 5, H 3, values 10 per record) 0.928 / 0.058; more skewed unit counts (shape 0.7) 0.949 / 0.063.

Reading: at n = 60 an instrument at every good level passes with probability 0.974 and stays at or above
0.889 in every sensitivity case run; with any one quantity at its bad level and every other good, the gate
passes with probability at most 0.071 (G1 acceptance of EB). n = 45 meets the 0.85 target at the baseline
(0.915) but its sensitivity cases were not run in the committed log; n = 30 (0.670) and n = 36 (0.808) do
not meet it. The target of the red-team's fix (P(pass | good) >= 0.85, P(pass | one bad) <= 0.10) holds at
n = 60 under every assumption tried; it is a statement about the model above, not about the papers.

## 11. Tools to build (lab-engineer; nothing here is built)
As v0.2 s11, with: ex_validate.py implementing s6.2-s6.4 with N1-N6 and passing validator-tests.jsonl;
agreement.py implementing s10.3 with the U-keys; draw_pilot.py for s10.2-s10.3 with the s2.10 seeds;
draw_rq_sample.py reading strata.py's frames; a fixture generator that checks the text hashes. Committed
scripts already written (Appendix A): strata.py, gate_oc.py, cost_options.py, flag_thresholds.py,
make_schema_v03.py, build_validator_tests.py.

## 12. How the fields feed the paper (unchanged from v0.2 s12; RQ2-RQ4 columns C1 census, C2 census, frame-R
weighted estimate; under Option 2 RQ1 also gets the weighted column)

## 13. Protocol and ledger deviations that need a decision row
v0.2 s13 rows 1-26 stand, with these changes: row 1 (scope) is the user's choice between the options of
s2.1; row 3 adds the suite rule (s5.4) and the replacement rule for training-free papers (U6a); row 12
anchors QA3-QA6 on S14 of s5.6; row 19 the gate is 60 records with the s10.4 rule; row 20 multimodal is the
screening rule of s2.3. New rows:

| # | Deviation or refinement | Protocol / ledger | When |
|---|---|---|---|
| 27 | Readings C-F1a to C-F1e of the census F1 rule | census codebook v1.2 | before Stage A (gate-auditor check) |
| 28 | Numbers printed inside figures are not extracted (U10) | s5 "every reported headline number" | before Stage A |
| 29 | Option 2 only: appraisal and light blocks on 281 of 608 includes | s5, s6 "every included study"; D0011 | with row 1 |
| 30 | Duplicate works removed from the frames after a human check | PRISMA study count | before the draw |

"Before Stage A" replaces v0.2's "before the pilot" for rows 2, 3, 4, 5, 9, 11, 12, 13, 15, 16, 21, 22; row 19
is "before Stage B".

## 14. Preconditions checklist
None of these is met on 2026-10-20 unless marked.

**Stage A (development, 12 records)**
- [ ] A1 T1 full-text gate PASS signed by gate-auditor (re-audit 1, 2026-10-20: FAIL; blockers need the human author).
- [ ] A2 Scope decision row entered from the user's answer to OQ3-01, OQ3-02, OQ3-03, OQ3-06, with the budget ceiling (OQ3-09).
- [ ] A3 Decision rows of s13 marked "before Stage A": rows 2, 3 (with the suite rule, OQ3-10, and U6a, OQ3-11), 4, 5, 9, 11, 12 (S14 basis, OQ3-14), 13, 15, 16, 21, 22, 27, 28.
- [ ] A4 gate-auditor: block F text equals codebook v1.2 B-9 to B-28; readings C-F1a to C-F1e consistent with codebook v1.2 and the harmonisation notes (OQ3-13).
- [ ] A5 Human check of the 20 borderline ids and the 6 duplicate candidates (OQ3-04); strata-overrides.jsonl and duplicate-works.jsonl written; strata.py rerun; frame hashes recorded.
- [ ] A6 Red-team review of v0.3 with no open critical finding (agent rule: red-team before lab-engineer; OQ3-17).
- [ ] A7 Tools: ex_dispatch.py (blocks per id, model-check alias, size batching); ex_validate.py passing all 35 cases of validator-tests.jsonl, the v0.2 T01-T22 as amended, and `quote_check.py --self-test` unchanged; fixture generator with hash checks; draw_pilot.py (Stage A); lookup CSV skeletons.
- [ ] A8 Scripts and logs in analysis/extraction/ and the v0.3 files committed by the orchestrator (written 2026-10-20, not committed).
- [ ] A9 ft_isolation_check.py and ft_model_check.py unchanged and passing; role map holds the three model ids of s8.1 (v0.2 s9).
- [ ] A10 Adjudicator route reconfirmed (OQ2-07).

**Stage B (gate, 60 records)**
- [ ] B1 Stage A complete; rules, examples and lookups revised; cost_options.py's per-record table replaced by Stage A means; gate_oc.py rerun with Stage A's units per record if they are below its assumptions.
- [ ] B2 Gate decision row: n (OQ3-07), the s10.4 table (OQ3-08), the re-gate rule, signed by gate-auditor before the first gate record.
- [ ] B3 agreement.py implementing s10.3 (U-keys, bootstrap seed 20261800), with self-tests on synthetic record pairs whose metrics are known.
- [ ] B4 draw_pilot.py Stage B draw (seeds 20261200 + h), excluding Stage A ids; manifest with frame and list hashes.
- [ ] B5 Brief, schema and lookups hashed in the gate row; no edits until the verdict.
- [ ] B6 Decision on the human gold subset (OQ2-10).

**Production (for completeness):** gate PASS signed; form v1.0 tagged; draw_rq_sample.py manifest and ledger
row; ER draw; public-version fetch (OQ2-08) before EQ sessions.

## Appendix A. Scripts and logs (analysis/extraction/, written 2026-10-20, not committed)
| Script | Run | Output |
|---|---|---|
| strata.py | `python -I analysis/extraction/strata.py --gate-n 60` | strata-log.txt: counts, borderline ids, named records, duplicate candidates, strata, allocation, precision, pools, list hashes |
| gate_oc.py | `python -u -E -P analysis/extraction/gate_oc.py` | gate_oc-log.txt (s10.6) |
| cost_options.py | `python -I analysis/extraction/cost_options.py` | cost_options-log.txt (s2.8) |
| flag_thresholds.py | `python -E -P analysis/extraction/flag_thresholds.py` | flag_thresholds-log.txt (s10.3) |
| make_schema_v03.py | `python -I analysis/extraction/make_schema_v03.py` | extraction-schema-v0.3.json |
| build_validator_tests.py | `python -I analysis/extraction/build_validator_tests.py analysis/extraction/validator-tests.jsonl` | validator-tests.jsonl (sha256 9991a1f7e60de3852c0948c95fff0561c9b071ba8afda09f96b9f88d4a12e2d2) |

`python -I` disables the user site-packages where numpy, scipy and jsonschema are installed on this machine;
the scripts that need them run with `python -E -P` (environment variables ignored, script directory not on
sys.path), which keeps the protection -I is used for.

List hashes (strata-log.txt): C1 91615db39bc8c696..., C2 6766a919f8e11c23..., NL 0bc9bf7d746ea841...,
FR c7508ab7876e83d4... (full values in the log).
