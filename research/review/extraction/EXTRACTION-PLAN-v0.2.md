```yaml
agent: method-architect
date: 2026-10-20
brief: revise the extraction and appraisal instrument from v0.1 to v0.2 after the red-team audit of 2026-10-20 (Paper 1); no extraction run, no sample drawn
sources_examined:
  - research/CONTRACT.md
  - research/review/extraction/EXTRACTION-PLAN.md, extraction-schema.json, extractor-brief.md, OPEN-QUESTIONS.md (v0.1, unchanged)
  - research/review/audits/2026-10-20-redteam-extraction-v0.1.md (all 38 findings)
  - research/review/protocol.md s1, s3 'Version rated', s4, s5, s6, s7, s10 (amendment headers)
  - research/ledgers/decisions.jsonl D0005-D0011, D0015, D0020, D0021, D0032, D0034
  - research/progress.md lines 260-275 (user decision 2026-10-16 at l.268-269)
  - research/review/framework-v2.md lines 120-145 (census status, lever table with merged value row)
  - analysis/screening/quote_check.py (read in full, not edited); tools/ft_model_check.py (header and role map)
  - analysis/screening/ft-t1/t1-decisions-all.jsonl (sha256 00b6247b9e50c82ee346b1c55955acbd82f5550bba3d1d930d9d610569ec2234; 885 rows, 608 include)
  - research/review/corpus/new-records-2026-10-15-v2.jsonl, subscription-records-2026-10-15.jsonl, title-resolution-records-2026-10-15.jsonl (titles, arxiv, year, venue fields of the 608 includes)
  - research/sources/md/fulltext-pymupdf/ (sizes and first 6,000 characters of the 608 include texts; M03416 lines 845-887; M12766 lines 520-600)
coverage: >
  Read the files above in the parts listed. Not read: census codebooks v1-v1.2 (block F text is carried over
  from the v0.1 brief unchanged; the equivalence check stays with gate-auditor), framework-v1 lever table
  (lever codes kept as in v0.1 with the value rows merged per framework-v2 item 3), criteria v1.6,
  ft_dispatch.py, ft_isolation_check.py internals. No paper was read in full. All counts below come from the
  scripts in Appendix A, run in the session scratchpad on 2026-10-20; they must be moved to analysis/extraction/
  with their logs before any of them is cited in the paper.
claims:
  - statement: In T1, 53 of 608 includes have i1 in {b, ab}; 52 further i1 = a includes (not nonlang_only) have a corpus title matching the multimodal regex of s2.3; 491 i1 = a includes remain in the random-sample frame; 12 are nonlang_only.
    status: supported
    evidence: Appendix A.1 on t1-decisions-all.jsonl sha256 00b6247b...; list sha256 values in s2.3
    level: E3
    confidence: 0.95
  - statement: Under the gate rule of s10.4, a block whose true raw agreement is 0.70 passes with probability 0.06-0.08 and one at 0.80 passes with probability 0.83-0.96 (n = 30, record ICC 0.10).
    status: supported
    evidence: simulation Appendix A.2 (seed 20261020, 2,000 replicates, 1,000 bootstrap resamples)
    level: E3
    confidence: 0.85
  - statement: The table-aware evidence rule of s6.3 accepts the M03416 Table 3 ablation row 'w/o diffusion denoising' that quote_check.py rejects as negation_before, and rejects the same cells under the wrong row label.
    status: supported
    evidence: prototype only, scratchpad prototype of s6.3 steps 1-3 and 7 on M03416.txt sha256 ae6f033f...; T01 pass, T02 cells_mismatch, T03 row_not_found, T04 negation_before; ex_validate.py itself does not exist yet
    level: E3
    confidence: 0.75
competing_explanations: []
unknowns:
  - tokens and hours per record (every cost figure in s2.8 is inference from the red-team's per-record estimates)
  - how many i1 = a includes are multimodal beyond the title regex (known only after the light pass)
  - true agreement of every block (the gate measures it)
next_test: {hypothesis: "form v0.2 is extracted reproducibly", intervention: "development stage (12) then gate (30, stratified) of s10", primary_metric: "lower 90 percent cluster-bootstrap bound of block raw agreement; unit identification F1", falsifier: "any gate criterion of s10.4 missed after one re-gate", gpu_hours: 0}
```

# Extraction and quality-appraisal plan, form v0.2 (draft, 2026-10-20; not frozen)

Status: a specification. Nothing here is a result about any paper. No extraction has been run and no
sample has been drawn. The v0.1 files stay as they are; every v0.1 red-team finding is answered in
`RESPONSE-TO-REDTEAM-v0.1.md`.

## 1. What changed from v0.1 (one line each)

1. Scope follows the user decision of 2026-10-16: light blocks, headline numbers and appraisal on every
   include; contrast data on all multimodal includes plus a stratified random sample (s2).
2. One generator per unit type; contrasts are comparison groups with arms, and a contrast unit is one
   group times one outcome column; value type, numeric levels, dose unit and group ids are fields (s5).
3. Table cells get their own evidence kind, checked by a new table-aware validator; prose quotes still go
   through quote_check.py unchanged, plus a 40-word cap (s6).
4. The pilot becomes a development stage (12, purposive) and a gate (30, stratified random) with
   lower-bound criteria whose operating characteristics are computed (s10).
5. QA sub-items take yes, no or unclear; scores are reported as bounds; anonymous submissions are
   appraised for QA1 and QA2 on the public version where one exists; QA8 is descriptive and gated (s7).
6. Design fields carry provenance (contributed or inherited); D12 levers are derived; D13 is dropped;
   an objective field is added (s4.3).
7. Every remaining protocol deviation is listed for a decision row (s13).

## 2. Scope (binding user decision of 2026-10-16)

### 2.1 The decision and its reading
`research/progress.md` line 268-269: "full-text screen ALL records, extract RQ data on a stratified sample
+ all multimodal". It is not yet in the decision ledger; s2.9 drafts the row. Reading used here:
- "RQ data" = the data that only the RQ2-RQ5 syntheses use: comparison groups, arms and contrast units
  (block K). These are the expensive part (red-team M17).
- Everything else the protocol requires per study is extracted on every included study: the study and
  design fields RQ1 counts need, the census fields D0011 extends to all includes, the headline numbers of
  protocol s5, and the appraisal of protocol s6 ("every included study").

### 2.2 Blocks by population

| Block | Content | Population | Why |
|---|---|---|---|
| L light | study S01-S17 except S14; inventory I1-I5; design D01-D16; census F1-F6; claim types CT | every include | RQ1 counts per class and year (protocol s1 "all included studies"); section 4 counts; census extension (D0011); inventory flags for s2.7 |
| Q appraisal | claim list CL; main comparison S14; QA1-QA9 | every include | protocol s6 "every included study"; RQ6 |
| H headline numbers | abstract outcome numbers and the F1 number | every include | protocol s5 "every reported headline number"; census F1; QA8 traces |
| K contrasts | comparison groups, arms, contrast units | the RQ sample of s2.4 | RQ2-RQ5 (user decision) |
| metadata M | dates, venue, affiliations, version, stratum, weight | every include | script (tools/ex_metadata.py, s11) |

The 12 nonlang_only includes get L, Q and H, no K, and are reported in their own row (D0032 item 3).

### 2.3 Multimodal: operational definition and counts (T1)
- **C1 (multimodal, certainty)**: i1 in {b, ab} in `t1-decisions-all.jsonl`: **53** of 608 (b 38, ab 15).
  These are the I1(b) unified models and the population of RQ5. List sha256 91615db39bc8c696....
- **C2 (multimodal language models, certainty)**: i1 = a, nonlang_only false, and the corpus title matches
  `multi-?modal|vision|visual|image|video|audio|speech|\bVLM|MLLM|\bVQA` (case-insensitive): **52**
  (diffusion VLMs and MLLMs, speech recognition, captioning, translation with images). List sha256
  b09306d34b5a4247.... A regex is a proxy; it is used because it is fixed before any extraction.
- **Completion rule**: after the light pass, every i1 = a include outside C1 and C2 whose light-pass S02 is
  text+image or text+other and that was not drawn into the sample gets block K in a completion session. These
  records enter the multimodal descriptive tables, not the weighted estimates (they are not a probability
  sample). The count is unknown until the light pass.
- Recommendation (open question OQ2-02): C1 and C2 both with certainty, because the user's words are "all
  multimodal" and C2 adds about 52 x 33k-53k = 1.7M-2.8M tokens. If the user reads "multimodal" as I1(b)
  only, C2 joins the random frame and the frame becomes 543.

### 2.4 The random sample: frame, strata, size, seed, weights
- **Frame R**: i1 = a, nonlang_only false, not in C2: **491** records (list sha256 08e76b1b00a50884...).
- **Strata** (both fixed from files that exist now, so the draw needs no extraction):
  1. anonymous submission: regex `Anonymous [Aa]uthors?` in the first 6,000 characters of
     `research/sources/md/fulltext-pymupdf/<id>.txt` (the red-team's rule; 241 of 491);
  2. text size: file size in bytes above the frame median (73,857) or not.
  Counts: anon-long 166, anon-short 75, named-long 79, named-short 171. Why these two: anonymous
  submissions are the recent ICLR 2027 cycle (246 of the 606 corpus venue strings start "ICLR 2027
  Conference Subm") and carry the version confound of M5; size tracks the number of tables and therefore of
  contrasts. Stratification here buys balance on recency and length; estimates stay close to self-weighting.
- **Size: n = 120** from frame R, proportional allocation by largest remainder: named-short 42, anon-long 41,
  named-long 19, anon-short 18. Weights N_h / n_h: 4.071, 4.049, 4.158, 4.167.
- **Draw**: per stratum, `random.Random(20261113 + h).sample(sorted(ids_h), n_h)` with h = 0, 1, 2, 3 in the
  order anon-long, anon-short, named-long, named-short; ids sorted with Python's default string sort. Seeds
  20261111-20261120 were checked unused on 2026-10-20 (grep over the worktree excluding full texts: only
  v0.1's 20261105 and 20261106 appear, in EXTRACTION-PLAN.md; both are retired unused). The draw is made by
  `analysis/extraction/draw_rq_sample.py` (s11) after the T1 gate passes; the frame file's sha256, the
  sorted id lists' sha256 per stratum and the drawn ids go into a manifest and a ledger row before any K
  session is dispatched. The pilot ids are not removed from the frame (s10.6): the sample stays a
  probability sample.
- **Records with block K in T1**: C1 53 + C2 52 + 120 = **225**, plus the completion records.
- **Later tranches** (the 797 re-check frame candidates, if screened): same definitions; C1 and C2 with
  certainty; the frame-R part sampled at the same per-stratum fraction n_h / N_h with seed 20261113 + 10 x
  tranche number + h; weights computed per tranche and stratum.

### 2.5 Precision: why 120
The RQ2-RQ4 tables report study-level shares (for example, among studies with a diffusion-versus-AR
comparison, the share whose budgets are matched or reported; the share of studies with a credited ablation
that holds everything else fixed) and contrast-level shares clustered by study. The design is set at the
study level, the sampling unit. Normal-approximation 95 percent half-widths with finite-population
correction, worst case p = 0.5, frame N = 491 (Appendix A.3):

| n (frame R) | whole frame | subgroup at 50 percent prevalence | at 30 percent | at 20 percent |
|---|---|---|---|---|
| 90 | 0.093 | 0.132 | 0.171 | 0.210 |
| **120** | **0.078** | **0.110** | **0.142** | **0.175** |
| 150 | 0.067 | 0.094 | 0.122 | 0.150 |

Target: a share over the language-only frame within plus or minus 0.08, and a share within a subgroup
present in about half of the studies within plus or minus 0.11. 120 meets both; 90 misses both; 150 adds
30 x 33k-53k = 1.0M-1.6M tokens of EA for a gain of 0.011 to 0.016. Pooling C1, C2 and the sample into one
estimate over all 596 non-nonlang includes has a Kish design effect of 1.34 (effective n 168). RQ5 uses C1
only and has no sampling error (a census of the T1 C1 records).

### 2.6 Estimation
- Study-level shares: stratified estimator with weights M15 (1 in C1 and C2), variance from the stratified
  formula with finite-population correction and, as a check, a stratified cluster bootstrap over studies
  (4,000 resamples, seed recorded).
- Contrast-level shares: ratio estimators with studies as clusters, same weights.
- Reporting: every RQ2-RQ4 table has three columns (C1 census, C2 census, frame-R weighted estimate with its
  interval) and a pooled column only where the statistician's plan allows it. Counts in the paper are
  labelled as census counts or as weighted estimates.

### 2.7 Targeted extension for the pooling test (protocol s7)
Pooling needs at least 8 matched contrasts from at least 5 independent groups sharing task family and metric.
A sample can hide a cell that would meet it. Rule, applied by script before any effect value is inspected:
if C1, C2 and the sample together hold at least 4 matched contrasts from at least 3 independent groups in a
cell (rq_class x task family x metric_id), block K for that rq_class is extracted on every include whose
inventory flag for that class is yes (I1 for RQ2, I2 for RQ3, I3 for RQ4, I4 for RQ5, I5 for credited-other)
and that has no block K yet. The pooled analysis of that cell then uses a census of the cell. Every such
study gets the second reading protocol s5 requires. The trigger counts availability, not effects.

### 2.8 Cost of each option (subagent tokens; inference, not measured)
Per-record bases from the red-team audit (M17, Item 6), with this plan's splits marked:
- L + Q blocks on one record: 35k-50k (red-team option (b): 21M-30M over 608); H adds 3k-5k (this plan, E0).
- block K on one record: 33k-53k (red-team option (b): 5M-8M over about 150).
- full independent second extraction (ER): 66k-98k (red-team: 61 records, 4M-6M).
- QA second rater as its own session: 30k-45k (red-team). Block F second extraction alone: 25k-33k (screening
  calibration, red-team). Adjudication: about 3M for a 10 percent sample (red-team (b)); 15k-30k per
  record with F or QA disagreements (this plan, E0). Public-version QA session (s7.4): 5k-10k (this plan, E0).

| Component | Records | Tokens |
|---|---|---|
| 1 EA: L + Q + H on every include | 608 | 23.1M-33.4M |
| 2 EA: block K on the RQ sample (C1 + C2 + 120) | 225 | 7.4M-11.9M |
| 3 ER: 10 percent second reading, stratified (s8.2) | 62 (23 with K) | 3.0M-4.4M |
| 4 EC: adjudication of the 10 percent sample | 61 | 2.5M-3.5M |
| 5 EQ: QA1/QA2 on public versions of anonymous texts | at most 287 | 1.4M-2.9M |
| 6 Pilot: development 12 + gate 30, two extractors and EC | 42 | 6.7M-10.9M (a re-gate adds 4.8M-7.8M) |
| **MIN = 1-6** (user decision; deviations on D0011 and protocol s6 two raters) | | **44.2M-67.1M** |
| 7 + second extraction of block F on the other 546, with EC | 546 | +15.7M-22.4M |
| **REC = MIN + 7** (meets D0011) | | **59.9M-89.5M** |
| 8 instead of 7: second rater for F and QA on the other 546, one session each, with EC | 546 | +25.1M-40.8M |
| **FULL = MIN + 8** (meets D0011 and protocol s6) | | **69.3M-107.9M** |

Variants of component 2: C1 only with n = 120: 173 records, 5.7M-9.2M; C1 only with n = 90: 143 records,
4.7M-7.6M. For scale: T1 full-text screening was about 44M-58M (red-team). Wall time on the red-team's basis
(about one hour per three-record session, three sessions in parallel) is of the order of 70-90 hours for
component 1 alone; the gate measures it (s10.4 G7).
Recommendation: REC. The census extension is the paper's lead critical finding and D0011 asks for a second
extractor on it; a second QA rater on every study is the protocol's wording but costs 9M-18M more, and the
10 percent second reading gives the appraisal's weighted kappa. The choice is the user's (OQ2-01).

### 2.9 Draft ledger row for the scope decision (for the orchestrator to enter; not entered)
```json
{"id": "<next>", "ts": "<entry time>", "decision": "Paper 1 extraction scope, recording the user decision of 2026-10-16 (research/progress.md l.268-269): full-text screening of all records; on every included study the light blocks (study fields, inventory flags I1-I5, design C1-C5 with objective and provenance, census F1-F6, claim types), the headline-number units (abstract outcome numbers and the F1 number) and the quality appraisal (claim list, main comparison, QA1-QA9); RQ2-RQ5 contrast data (comparison groups, arms, contrast units) on every multimodal include, operationally C1 = i1 in {b, ab} (53 of 608 in T1) and C2 = i1 = a with a corpus title matching the multimodal regex of EXTRACTION-PLAN-v0.2 s2.3 (52), both with certainty, plus a stratified random sample of 120 of the 491 remaining language-only i1 = a includes (strata anonymous submission x text size, proportional allocation 42/41/19/18, seeds 20261113-20261116, weights N_h/n_h 4.05-4.17), plus the completion (s2.3) and targeted-extension (s2.7) rules; nonlang_only includes (12) get no contrast data and are reported separately. RQ2-RQ4 are reported as C1 and C2 census counts and weighted frame-R estimates; RQ5 from C1. Second reading: a stratified 10 percent sample (s8.2). [Option chosen: MIN / REC (block F double-extracted on every include) / FULL (block F and QA double on every include).]", "options": ["full form on every include (protocol s5 as written)", "light, appraisal and headline numbers on all; contrasts on multimodal plus a stratified sample (user 2026-10-16)", "whole form on a sample only"], "evidence": "research/progress.md lines 268-269; research/review/audits/2026-10-20-redteam-extraction-v0.1.md C3, M13, M17; EXTRACTION-PLAN-v0.2.md s2 (frame analysis/screening/ft-t1/t1-decisions-all.jsonl sha256 00b6247b9e50c82ee346b1c55955acbd82f5550bba3d1d930d9d610569ec2234; counts by the Appendix A scripts); precision: 95 percent half-width 0.078 for a study-level share over frame R, 0.110 within a subgroup at 50 percent prevalence", "owner": "user", "reversal": "gate cost per record above the s10.4 G7 ceiling (fallback ladder of s10.5), or the user changes the scope"}
```

## 3. Decisions the instrument relies on
Unchanged from v0.1 s2 (D0005-D0011, D0015, D0020, D0021, D0032, D0034, Route F), with three changes:
- D0011: block F is extended to every include; whether with a second extractor on every include is
  option 7 of s2.8 (decision row, s13 item 8).
- D0008/D0009: no evaluability field, no computation of hypotheses E1-E3; QA8 is descriptive and gated
  (s7.3); the H and K units make a headline-versus-controlled comparison possible, which needs its own
  decision row and stays descriptive while D0008 stands.
- Name clash: "hypotheses E1-E3" (protocol s6) versus "evidence level E0-E5" (CONTRACT); prose evidence
  ids are E01, E02 ... and cell evidence ids C01, C02 ... (no clash: two digits and a record scope).

## 4. Field table

Tier: **L**, **Q**, **H**, **K** = block (s2.2); **M** = metadata script; **Dv** = derived by
ex_validate.py. Evidence codes: **Q** a prose quote or a cell entry with cond = the field id is required
for a positive value (anything other than no, not_stated, NS, "not stated", none, unclear, NA, empty);
**S** a negative value needs a `searched` entry keyed by the same id (one rule for every Q-coded field and
every QA sub-item: R03); **-** no evidence. Sub-field conds use a dot: S10.steps, D07.rule, S09.tokens.

### 4.1 Metadata (M; extractor writes only M01, M04, M09, M10 and blocks, copied from dispatch.json)

| # | Field | Source | Used by |
|---|---|---|---|
| M01 | id | dispatch | all |
| M02 | bibliographic (title, authors, arXiv, DOI, OpenReview) | corpus record | sec 2, S6 |
| M03 | first_version_date + first_version_source | ex_metadata: arXiv v1; else OpenReview cdate; else Crossref issued (E1) | RQ1 per year, RQ6 by year |
| M04 | ft (full-text version string) | dispatch | protocol s3, S6 |
| M05 | venue_resolved + venue_name {journal, conference, workshop, preprint, under-review, unknown} | ex_metadata: Semantic Scholar, OpenAlex, DBLP, OpenReview (E1) | QA10, RQ6 |
| M06 | i1 | screening | strata, RQ5 |
| M07 | nonlang_only | screening | separate row |
| M08 | tranche | dispatch | flow diagram |
| M09 | extractor (role-model) | dispatch | agreement |
| M10 | form_version | dispatch | agreement |
| M11 | affiliations | OpenAlex or the public version; never an anonymous file (M5) | s7 independent groups |
| M12 | anonymous_version | regex of s7.4 on the screened file | QA1, QA2 version rule; RQ6 strata |
| M13 | public_version (id and date) | ex_metadata | s7.4 |
| M14 | stratum + in_unit_sample | draw manifest | weights, tables |
| M15 | weight N_h / n_h | draw manifest | estimates |
| M16 | family_id | script on S07, S08 and author overlap, confirmed by EC | s7 independence; duplicate works (m17) |

### 4.2 Study block S and inventory I (tier L, except S14 tier Q)

| # | Field | Values | Evidence | Used by |
|---|---|---|---|---|
| S01 | study_type | method, theory, analysis, benchmark, system | - (via S13) | RQ1, RQ6 strata, focal rule |
| S02 | modality | text, text+image, text+other | Q unless text | RQ1 (reported with M06, m10), C2 completion |
| S03 | text_generator | diffusion, autoregressive, both, none | Q | RQ1, sec 4 |
| S04 | state_space (list; several only for analysis/benchmark) | six protocol classes + not_stated | Q | RQ1 per class and year, sec 4 |
| S05 | task_families: list of {family, generated_sample} + task_other | protocol s5 seven families | - | RQ1, strata of RQ2-RQ5 |
| S06 | primary_task_family | as S05 or NA | - (equals the F1 unit's family; checked) | sec 6, s7 matching |
| S07 | models {name, params_printed, params_b} | as printed; params_b is a unit conversion | Q per printed size | RQ2 comparability, family_id |
| S08 | base_checkpoints | names as printed | Q if non-empty | provenance, family_id, s7 |
| S09 | training {training_free, stages, data_named, tokens_printed, compute_printed} | as v0.1 | Q for training_free yes and each printed value; S otherwise | RQ3, protocol s5, RQ6 strata |
| S10 | main_sampler {description, steps, nfe, gen_length, tokens_per_step} | as printed | Q per printed value (cond S10.steps ...) | RQ4, protocol s5, D12 |
| S12 | venue_line_text | as printed or none | - (string must occur in the file; checked) | QA10 |
| S13 | credited_component {text, type} | type: model-or-architecture, objective-or-loss, training-recipe, sampler-or-decoding, caching-or-system, guidance-or-constraint, theory, benchmark-or-dataset, analysis-only, other | Q | QA7 (n rule), K credited_ablation |
| S14 | main_comparison {where, page, own_row, baseline_row, basis} or NA (tier Q) | s5.6 | - (rows checked to occur on the page) | QA3-QA6 |
| S15 | limitations.categories | compute-or-speed, scale, quality-gap, length-or-fixed-length, evaluation-scope, data, assumptions, safety-or-misuse, other, none | Q per category; S for none | protocol s5 "limitations stated" (m14) |
| S16 | synergy_benchmark {present, name} | yes/no | Q if yes | RQ5 (m11) |
| S17 | focal_model | name | - | design block, K focal rule |
| I1-I5 | inventory flags | yes/no | Q if yes (cond I1 ...); S if no | s2.7 extension, population counts |

S11 (affiliations) moved to M11.

### 4.3 Design block D (tier L; the focal model and its F1 sampler)
D01-D11 and D14 keep the v0.1 values (brief block D). Changes:
- **D15 objective** {elbo-ce, weighted-ce, score-entropy, mse-x0, mse-eps-or-velocity, flow-matching, other,
  not_stated, NA}; Q unless not_stated or NA. Closes the RQ1 "objective" gap (M10).
- **D16 provenance** per field D01-D11 and D15: contributed (the paper introduces or changes the choice),
  inherited (taken unchanged from a named checkpoint it loads; inherited_from names it), not_stated, NA.
  Section 4 counts are given per study and per distinct model (S07 or S08 name, deduplicated by family_id),
  and "not stated" is never pooled with "inherited" (M6).
- **D12 levers: derived** (Dv) by this map, so no judgement field feeds Tab 7 (M16, m9):

| Lever | Derived when |
|---|---|
| L1 fewer tokens per step or adaptive count | D07.rule = threshold-adaptive, or S10.tokens_per_step printed and not "1" |
| L2 weakly dependent position sets | D07.rule in {confidence-ranked, threshold-adaptive, learned-planner, fixed-order} |
| L3 joint draw | D08 not in {independent, not_stated} |
| L4 block-wise | D07.blockwise = yes or D02 = block |
| L5 modality schedule | D09 in {sequential, alternating} |
| L6 training | S09.training_free = no |
| L7 self-conditioning, schedules | D05 = yes or D11 contains self-conditioning |
| L8 distillation | S09.stages contains distillation |
| L9 token-level revision | D10 contains explicit-remasking-or-editing or corrector |
| L10 output-level revision | D10 contains output-level |
| V value slot (L11 and L12 merged, framework-v2 item 3) | F2_codes contains any of A T P S C G M |
| L13 exact reuse | D11 contains exact-cache |
| L14 lossy reuse | D11 contains approximate-cache |

- **D13 design_fit dropped.** It was not the construct of the 47-model test (04-design-space.tex line 14),
  so no fit rate from the extraction is set beside 36/47.
- Analysis and benchmark studies: block D describes the focal model only (S17).

### 4.4 Census block F (tier L)
F1-F6 and F2d unchanged from v0.1 (brief block F, carried over word for word; equivalence with codebook v1.2
is a gate-auditor check, s11). The F1 number becomes an H unit (origin abstract, or F1-table / F1-figure /
F1-text), so F1 is recorded on every include.

### 4.5 Claims (CT tier L; CL tier Q)
- CT1-CT6 as v0.1 (abstract only). Published per type only where the type reaches kappa 0.60 in the 10
  percent second reading (OQ2-12; m12 of the red-team concerns definitions, fixed in the brief).
- CL list: {claim_id, source, types, has_number, status, h_units, trace}. Status adds **not-checkable**
  (no number and no direction a table can test: "competitive", "strong", "comparable" without a named
  comparator and metric). `trace` holds the cell or prose evidence ids the status rests on (s7.3).

### 4.6 Quality appraisal (tier Q): sub-items in s7.1; scores Dv.

### 4.7 Headline-number unit H (tier H; s5.2)

| # | Field | Values | Evidence |
|---|---|---|---|
| H01 | unit_id | H01, H02 ... | - |
| H02 | is_F1 | exactly one true when F1_status is number, figure-only or unreadable | - |
| H03 | origin | abstract, F1-table, F1-figure, F1-text | - |
| H04 | model_printed | as printed | in the quote |
| H05 | metric_printed | as printed | in the quote or caption |
| H06 | metric_kind | generated-sample, likelihood, speed, steps, other (defined in the brief) | - |
| H07 | higher_is_better | bool or null | - |
| H08 | benchmark_printed | as printed or "not stated" | - |
| H09 | split | as printed or not_stated | Q if printed |
| H10 | task_family | S05 families or not_stated | - |
| H11 | value_printed | as printed; "figure-only" or "unreadable" only for an F1 unit | value check (s6.2, s6.3) |
| H12 | value_num | Dv parse | - |
| H13 | value_unit | %, x, tokens/s ... | - |
| H14 | scale | fraction, percent, points, raw, factor, other | - |
| H15 | setting | steps, NFE, tokens per step, generation length, sampler, value rule, guidance, as printed | Q per printed value not in the value's own quote |
| H16 | variance | kind, value_printed, n_runs | Q if not none |
| H17 | evidence_ref + col + value_occurrence | E or C id | the value's evidence |
| H18 | column_printed | column label for a cell value | header check |
| H19 | trace + trace_col | C id of a table cell showing the same number (optional) | value check |
| H20 | value_type | level, difference, ratio, other | - |
| H21 | arm_role | own, baseline (levels); NA otherwise | - |
| H22 | reference_printed | comparator of a difference or ratio as printed, or "not stated" | in the quote |
| H23 | loc {page, where} | | - |
| H24 | metric_id, benchmark_id | Dv from the lookup tables (s11) | - |

### 4.8 Comparison group G and arm A (tier K; s5.3)

| # | Field | Values |
|---|---|---|
| G01 | group_id | G01 ... |
| G02 | rq_class | RQ2-vs-ar; RQ3-pretraining, -adaptation-from-ar, -sft, -rl, -distillation, -objective-or-architecture; RQ4-steps, -order, -remask, -cache, -parallel-or-block, -value-rule-or-guidance, -other-inference; RQ5-task-removal, -shared-vs-decoupled; credited-other (RQ5-synergy-benchmark removed: S16) |
| G03 | factor_type | controlled list (schema) |
| G04 | factor_printed | free text (not in any key) |
| G05 | dose_unit | steps, nfe, tokens-per-step, threshold, cache-interval, block-size, gen-length, guidance-scale, temperature, other, NA |
| G06 | where | "Table n" or "Figure n" as printed |
| G07 | page | from the page marker |
| G08 | source_kind | main-table, appendix-table, main-figure, appendix-figure |
| G09 | orientation | rows, columns, figure |
| G10 | second_factor_printed | level of a second factor held fixed in this group, or '' |
| G11 | anchor_arm | the default configuration's arm id; null for benchmark/analysis RQ2 groups |
| G12 | arms | list of arms (A01-A13), at least 2 |
| G13 | credited_ablation | true if an arm removes or replaces the credited component |
| G14 | held_fixed | stated, not stated, co-varied (Q if stated or co-varied) |
| G15 | other_changes | stated differences besides the factor, '' if none (Q if non-empty) |
| G16 | budget_across_arms | matched, reported, not reported (Q if matched) |
| G17 | shape | figure-only series: monotone-up, monotone-down, peaked, flat, unclear; NA otherwise |
| G18 | evidence_refs | caption and statements behind G13-G16 and arm fields |
| A01 | arm_id | A1, A2 ... within the group |
| A02 | label_printed | row label (rows) or column label (columns), exactly as printed |
| A03 | role | anchor, comparison |
| A04 | generator | diffusion, autoregressive, other, not_stated, by the paper's own label (s5.3 K-AR) |
| A05 | level_printed | factor value as printed |
| A06 | level_num | number in dose_unit, or null |
| A07 | params_printed | as printed or not_stated (Q if printed outside the value row) |
| A08 | train_tokens_printed | as printed or not_stated |
| A09 | shots_printed | as printed or not_stated |
| A10 | scoring | generated, likelihood, not_stated |
| A11 | number_source | run-by-authors, copied-stated, not_stated (a row-label citation alone is not_stated) |
| A12 | steps_printed | per arm, as printed |
| A13 | gen_length_printed | per arm, as printed |

### 4.9 Contrast unit K (tier K; s5.4)

| # | Field | Values |
|---|---|---|
| K01 | unit_id | K01 ... |
| K02 | group_id | the group |
| K03 | benchmark_printed | as printed |
| K04 | metric_printed | as printed |
| K05 | column_printed | column label (rows orientation) or value-row label (columns orientation) |
| K06 | metric_kind | as H06 |
| K07 | higher_is_better | bool or null |
| K08 | scale | as H14 |
| K09 | split | as printed or not_stated |
| K10 | task_family | S05 families |
| K11 | n_eval_printed | items or samples as printed, or not_stated (M9a) |
| K12 | figure_only | bool |
| K13 | values | per arm: arm_id, value_printed, cell + col or prose + value_occurrence, variance |
| K14 | value_num | Dv |
| K15 | matched | Dv: held_fixed = stated, other_changes = '', and for RQ2 also budget matched and all arms' scoring equal and stated |
| K16 | metric_id, benchmark_id | Dv |

### 4.10 Record level
R01 evidence (prose), R02 cell_evidence, R03 searched, R04 doubt (field ids answered with doubt),
R05 notes (at most 60 words), R06 blocks.

**Field count: 147** (M 16, S 16, I 5, D 15, F 7, CT and CL 2, QA 9, H 24, G 18, A 13, K 16, R 6;
sub-items and sub-fields counted inside their field; retired ids S11, D13 not counted).

## 5. Units

### 5.1 Principles (fix for C2)
1. One generator per unit type, applied in a fixed order. 2. A printed value is recorded once per
group; an abstract number is one H unit whatever else it appears in. 3. Every alignment key is built from
controlled fields or from strings the validator has located in the file. 4. Every unit has a value type;
every contrast has a group, arms with numeric levels where the factor is numeric, and one outcome column.

### 5.2 Headline numbers H (block H, every include)
- **Generator H-1 (abstract).** Each number in the abstract that reports an outcome of evaluating a model:
  a quality or accuracy score, a likelihood or perplexity, a speed (time, throughput, speed-up), a number of
  steps or function evaluations reached, or a difference or ratio of such outcomes. One unit per number. Not H
  units: sizes and resources (parameters, data tokens, compute, GPUs), counts (benchmarks, tasks, languages),
  dates, and settings ("with 64 steps" qualifies another number: it goes in that unit's setting). A number
  printed twice in the abstract for the same statement is one unit.
- **Generator H-2 (F1 fallback).** When the census F1 rule selects a number outside the abstract, one H unit
  with origin F1-table, F1-figure or F1-text (value "figure-only" or "unreadable" allowed only here).
- **Value type.** ratio if printed as a factor (x, times, -fold); difference if printed as a gap ("by 7.56
  points", "+3.2", "35% faster", "improves by 12%"); level otherwise. For a level, arm_role says whose value it
  is (own or baseline); for a difference or ratio, reference_printed gives the comparator as printed in the
  same sentence, or "not stated". Worked reading of the red-team's CONFLUX example: "improves MMLU by 7.56
  points" is one H unit, difference, scale points, reference as printed or "not stated"; "comparable FID (3.67
  versus 3.09)" is two H units, levels, own and baseline; "0.6B backbone" is not an H unit (it is S07).
- **Trace.** For each abstract number, the extractor records the table cell that prints the same number
  for the stated setting if it finds one (trace, trace_col). The CL status match rests on it.
- **Key.** (origin, normalised value_printed, metric_id); a second identical key in one record is
  disambiguated by order of appearance (m13).

### 5.3 Comparison groups G (block K, RQ sample)
Terms: an **arm** is one row (or column, or figure series) of a table or figure that denotes one system
configuration; the **anchor** is the focal model's default configuration (the row the text calls its method,
"ours", or the default named in the setup); a **factor** is what differs between arms.

**Generator: one pass over tables and figures in reading order (main text, then appendix).** For each
table or figure block T:
1. **K-RQ2.** If T scores the anchor and at least one arm that the paper labels autoregressive for the
   evaluated output (K-AR below) in a common column: one group, rq_class RQ2-vs-ar, arms = the anchor plus
   every AR-labelled row of T in table order. Non-AR baselines are not arms. **Several AR baselines are
   levels of one group** (red-team C2.4: "all AR rows as levels"); pairwise contrasts anchor-versus-each-AR
   are derived by script. Analysis and benchmark studies: arms = every diffusion row and every AR row of T,
   anchor null.
2. **K-F (factor groups).** Rows, columns or figure series of T that are variants of the focal model
   differing from its default in one stated factor: one group per factor, arms = the default plus each
   variant; rq_class from factor_type (RQ3 for training choices, RQ4 for inference settings, RQ5 for task or
   modality removal and shared-versus-decoupled pathways in a unified model; credited-other when an arm
   removes or replaces the credited component and no RQ class fits). A table that varies two factors gives one
   group per level of the second factor (second_factor_printed). A sweep is one group with every level as
   an arm (dose_unit, level_num). Analysis and benchmark studies: factor groups for the focal model only.
3. **Not groups:** comparisons among baselines only; the focal model against non-AR baselines (that is the
   main comparison of s5.6, not a contrast); optimisation hyperparameters (learning rate, batch size,
   warm-up) unless presented as an ablation of the contribution; rows already recorded in an earlier table
   (first appearance in reading order wins); synergy benchmarks (S16).

**K-AR (who counts as an autoregressive baseline).** An arm is autoregressive for the evaluated output if
the paper's table, caption or text labels the generator of the scored output as autoregressive, AR,
next-token or left-to-right. Unified models are judged per output: a model whose images come from discrete
diffusion (Show-o type) is not AR in a text-to-image table; its text is AR in a text table only if the paper
says so. An unlabelled arm gets generator not_stated and is not an arm of an RQ2 group (named in notes).
No architecture is inferred from a cited paper (brief G3).

**Figure-only series** are groups with figure_only units, values "figure-only", and shape coded on the
primary metric. They count for RQ4 shape descriptions, never for pooling. F4 (census sweep on the F1 task)
and RQ4-steps groups are counted separately and never reconciled (M8).

### 5.4 Contrast units K = group x outcome (block K)
One K unit per outcome column of a group: a (benchmark, metric) column with values for at least two arms.
- Sub-scores of one benchmark (GenEval categories, MME sub-tasks, per-category accuracies): only the
  benchmark's aggregate column (Overall, Avg., Average, Mean, Total, Score) if the table has one; else every
  sub-score column.
- Distinct benchmarks: one unit each. An average-over-benchmarks column is not recorded (derivable).
- Speed and step columns: their own units (metric_kind speed or steps).
- Scale as printed: the same benchmark printed as 0.61 in one table and 61.6 in another is fraction and
  percent (M9c).
- Each value names its arm and its evidence (cell id and token column, or a prose id).
One ablation scored on three benchmarks is one group with three K units sharing group_id (C2.6, M9b).

### 5.5 Alignment keys and de-duplication (for agreement and for the analysis)
- Label normalisation: quote_check.normalise, lower case, a trailing citation parenthesis containing a
  four-digit year removed (`\s*\([^()]*\d{4}[a-z]?\)$`), markers * † ‡ removed, spaces collapsed.
- **Group match** between two records: same where and rq_class, Jaccard of the normalised arm-label sets at
  least 0.5, one-to-one by highest Jaccard (ties: lower group_id).
- **K match**: matched groups, same benchmark_id and metric_id, same normalised column_printed.
- **Value match**: inside matched K units, by normalised arm label.
- **H match**: s5.2 key.
- A (cell, col) pair may carry values in two units only if they belong to different groups (the anchor row
  of an RQ2 group and of an ablation group); within one group the validator rejects a reused cell column.
- factor_printed, other_changes and the free-text part of S13 are in no key (C2.5).

### 5.6 Main comparison S14 (block Q; fix for M3)
A table-and-row pair, not a unit. where = the first table in reading order that contains the focal model's
default row and a baseline row on the metric of the first comparative claim of the abstract (the first CL
from the abstract whose types are not "none"); own_row = the default row label; baseline_row = the first row
of the model or class the claim names (for "outperforms autoregressive models", the first AR-labelled row),
else the first baseline row from the top. No comparative claim in the abstract: the F1 table and its first
baseline row (basis F1-table). No table with a baseline row: NA. QA3, QA4, QA5 and QA6 are all scored on
this table and row pair; QA3 is no longer anchored on "the main result".

### 5.7 Workload rule
Gate: median H units per record at most 10 and median K units at most 30 (s10.4 G7). Otherwise K is narrowed
to main-text tables plus appendix RQ4-steps sweeps and credited ablations, and the gate's K criteria are
recomputed on the narrowed definition before production.

## 6. Evidence rule and the table-aware validator (fix for C1, M11)

### 6.1 Two kinds of evidence
- **Prose** (`evidence`, ids E01 ...): one contiguous passage of 6-40 words from the screened text. Used for
  every text statement, abstract numbers, captions cited as statements, held_fixed statements.
- **Cell** (`cell_evidence`, ids C01 ...): a table row reference used for every value taken from a table,
  including settings in hyperparameter tables (cond S10.steps etc.) and QA7 ablation rows.
`evidence` keeps the exact shape quote_check.py reads, so `python analysis/screening/quote_check.py --rows
<output> --texts <dir>` runs unchanged on the prose entries. Cell entries have no `quote` key and live in a
separate array so quote_check never sees them. **quote_check.py is not edited.**

### 6.2 Prose checks (ex_validate.py)
For each prose entry: (P1) `quote_check.quote_status(quote, text) == "found"` (statuses passed through:
not_found, too_short, elided, negation_before, negation_after); (P2) word count, computed as quote_check
counts it (`len(normalise(quote).split())`), at most 40, else **too_long**; (P3) at least 3 tokens that
contain a letter, else **numeric_only** (the red-team's `0.61 0.98 0.72 0.54 0.82 0.19` case); (P4) for every
value that cites this entry (H17, K13 prose): value_printed occurs in normalise(quote) as a whole token by
the regex `(?<![\w.])` + re.escape(value) + `(?![\w]|\.\d)` (so 45.2 is not found in 45.21), exactly once or
at the position given by value_occurrence, else **value_not_in_quote** or **value_ambiguous**.

### 6.3 Cell checks (ex_validate.py; new code that imports quote_check.normalise)
Input: the cell entry, the record's text file, and every value that cites the entry.
1. **Pages.** Split the text into pages at lines matching `^=== page (\d+) ===$`. Page N = lines after
   its marker up to the next marker. A text without markers is one page 1 (and page checks are skipped with a
   warning **no_page_markers**).
2. **Tokens.** For page N, normalise each line separately with quote_check.normalise, join a line ending in
   a letter plus "-" with the next line if that one starts with a lower-case letter (line-end hyphenation),
   split on spaces, and keep for each token its line number and whether it is the first token of its line.
3. **Row match.** L = tokens of normalise(row_label), Cc = tokens of normalise(cells). A position p on page
   `page` matches if tokens[p : p+|L|] == L (exact string equality, case kept), and token p is line-initial
   or token p-1 is value-like, and tokens[p+|L|+first_col-1 : p+|L|+first_col-1+|Cc|] == Cc. Value-like:
   `^[-+−±]?(\d[\d.,]*|\.\d+)(%|x|×)?[↑↓*†‡]*$` or one of `- – — n/a N/A ✓ ✗ × *`.
   - zero matches: **row_not_found** if L matches nowhere at a valid start, else **cells_mismatch**;
   - one match: pass; several matches: pass only if `occurrence` = k selects the k-th (1-based, page order),
     else **ambiguous_row**.
4. **Length.** |L| + |Cc| at most 40, else **too_long** (the 40-word cap for cells). Wide rows: a second
   entry with the same row_label and a larger first_col covers later columns.
5. **Header.** normalise(header) must occur as a contiguous token run on page `page` or page `page`-1, else
   **header_not_found** (fail). For every value citing the entry, normalise(column_printed) must occur as a
   contiguous token run inside the header tokens, else **header_mismatch** (warning, counted: the share of
   units whose column could not be matched to a header token is reported, M11).
6. **Caption.** normalise(caption) found as a contiguous substring (whole words, as quote_check does) on page
   `page`, `page`-1 or `page`+1, 6-40 words, starting with "Table", "Tab.", "Figure" or "Fig."; else
   **caption_not_found** or **caption_length**. No negation window is applied to captions or cells:
   the arm identity is carried by row_label, which must be quoted whole, and by check 8.
7. **Value.** For each value citing the entry with column index j: first_col <= j < first_col + |Cc|, else
   **value_outside_cells**; the j-th token after the row label must equal value_printed exactly (after
   normalise), else **value_mismatch**.
8. **Label agreement.** H unit: loc.where equals the entry's where. K value in a rows group: the arm's
   label_printed, normalised, equals the entry's row_label, normalised, else **label_row_mismatch**. In a
   columns group, every value of the unit cites the same cell entry (the value row) and each arm's
   label_printed must be found in the header tokens, else **label_header_mismatch** (warning).
9. **Reuse.** The same (cell id, column) used by two values inside one group: **cell_reused** (fail).

Why a table rule instead of a wider prose window: the negation window of quote_check stops prose quotes
that drop a "not"; in a table the qualifier lives in the row label, and checks 3 and 8 force the full label to
be quoted and to equal the arm's label. A wrong row cannot pass check 3, a wrong column fails check 7 or is
caught by the second reader through header_mismatch.

### 6.4 Record-level checks (ex_validate.py)
Schema (jsonschema Draft 2020-12, extraction-schema-v0.2.json); blocks present match dispatch.json; every
Q-coded field or sub-field with a positive value has at least one prose or cell entry with that cond; every
negative value of a Q-coded field and every QA sub-item "no" or "unclear" has a `searched` key with the same
id (one rule, m1); F2 letter order and U/NS exclusivity; codebook v1.2 B-27 couplings (NA gives F2-F6 NA; QL
gives F3-F6 NA); exactly one is_F1 when F1_status is number, figure-only or unreadable, none otherwise;
F1_unit equals that unit's id; S06 equals the F1 unit's task family; S12 occurs in the file; S14 rows occur
on S14's page (row-match step 3 on labels only); QA4 n, QA5 n and QA6 n are yes exactly when S14 is NA; every
group has exactly one anchor arm unless it is an analysis/benchmark RQ2 group; every K unit's group exists and
every value's arm exists in that group; every CL trace and H trace id exists; notes at most 60 words (not EC).
Then fills Dv fields: value_num (parser: strip %, x, ×, thousands commas, trailing markers; unicode minus to
"-"; split "a±b" into value a and variance b; ranges and non-numbers give null), D12 levers (s4.3), QA scores
(s7.1), QA3c, QA7n, K matched, metric_id and benchmark_id from the lookup tables (unmapped strings to a queue
file for EC to extend the lookup under a new version), and M14/M15 from the draw manifest.

### 6.5 Interface
`python -I tools/ex_validate.py --rows <EX.jsonl> --texts <dir> --schema
research/review/extraction/extraction-schema-v0.2.json --lookups analysis/extraction/lookups/ [--manifest
<draw manifest>] [--out report.jsonl] [--fill-derived out.jsonl]` and `--self-test`.
Output: one JSON line per finding {id, extractor, check, ref (field, unit or evidence id), status, severity
(fail or warn), detail}; a summary line per record and a total on stdout. Exit 0 if no fail, 1 if any fail,
2 on a usage or schema-load error. A finding returned to the session once (s9); a fail still present goes to
EC with the field marked unverified.

### 6.6 Unit tests (`--self-test`; fixtures under tests/extraction/fixtures/)
Fixture F-M03416: the line `=== page 7 ===` followed by lines 845-887 of
`research/sources/md/fulltext-pymupdf/M03416.txt` (source file sha256
ae6f033f5823bee4160343ba0a77e3ab57c8861e831180306fa7e6ab405369cc; the full texts are not in git, so the
fixture is generated by a script that checks this hash, and the fixture's own hash is pinned in the test).
Header lines `Method`, `TF`, `TB`, `BA`; rows `DiffuseDef 84.5 86.0 84.6`, `w/o ensembling 64.2 65.8 54.9`,
`w/o diffusion denoising 57.1 58.4 47.7`, `w/o adv training 80.3 80.9 80.5`; caption starts
`Table 3: Ablation results for DiffuseDef’s accuracy`. Caption string used below: "Table 3: Ablation
results for DiffuseDef's accuracy under attack on AGNews datasets." Header string: "Method TF TB BA".

| Test | Input | Expected |
|---|---|---|
| T01 | cell page 7, row_label "w/o diffusion denoising", first_col 1, cells "57.1 58.4 47.7" | pass |
| T02 | as T01 with row_label "w/o ensembling" | cells_mismatch |
| T03 | as T01 with row_label "diffusion denoising" | row_not_found (label not at a valid row start) |
| T04 | prose entry "w/o diffusion denoising 57.1 58.4 47.7" (6 tokens) through quote_check.quote_status | negation_before (the earlier row label "w/o ensembling" is in the 6-word window; this is red-team C1 and documents why a cell kind exists); the 10-token prose starting at the first w/o row, "w/o ensembling 64.2 65.8 54.9 w/o diffusion denoising 57.1 58.4 47.7", gives found |
| T05 | H unit value "58.4", evidence C(T01), col 2 | pass; col 3: value_mismatch; col 4: value_outside_cells |
| T06 | K rows group, arms "DiffuseDef" (C: row DiffuseDef, cells "84.5 86.0 84.6") and "w/o diffusion denoising" (T01), column_printed "TF", col 1 | pass, header_match true |
| T07 | as T06 but the arm "DiffuseDef" cites the T01 entry | label_row_mismatch |
| T08 | T01 with page 8 | row_not_found (wrong page) |
| T09 | T01 with first_col 2, cells "58.4 47.7" | pass (continuation entry) |
| T10 | T01 with header "Method TF TB XX" | header_not_found |
| T11 | T06 with column_printed "AUA" | pass with header_mismatch warning |
| T12 | caption of T01 cut to "Table 3: Ablation results" (4 words) | caption_length |
| T13 | two values of one group citing (T01, col 1) | cell_reused |
| T14 | synthetic page: header "Model A B C D E F G", row "Ours" + 7 values, then six rows "w/o c1" ... "w/o c6" with 7 values each; cell row_label "w/o c5", cells = its 7 values | pass (9 tokens); the same row as prose gives negation_before for every start shorter than 40 words (the C1 regression) |
| T15 | synthetic page with the identical row "Ours 1.0 2.0" twice | ambiguous_row; with occurrence 2: pass |
| T16 | prose quote of 41 words found in a synthetic text | too_long |
| T17 | prose quote "0.61 0.98 0.72 0.54 0.82 0.19" found in a synthetic text | numeric_only |
| T18 | prose quote "the model reaches 45.21 accuracy on the test set" with value "45.2" | value_not_in_quote |
| T19 | prose quote containing "7.56" twice, value "7.56", value_occurrence null | value_ambiguous; with value_occurrence 2: pass |
| T20 | synthetic page where a label is split by line-end hyphenation "Diffu-" / "sion-LM 1.0 2.0" | row "Diffusion-LM", cells "1.0 2.0": pass |
| T21 | fixture F-M12766 (lines 520-600 of M12766.txt, sha256 c0051304cc6e543872e6da7a236efaa590ce6556ce76030a2716e5f2a1f273b0, page 8): row "PixArt-α (Chen et al., 2024b)", cells "- Diffusion 0.6 0.48 0.98 0.50 0.44 0.80 0.08 0.07"; value "0.98" col 5 | pass (two values on one line handled); column_printed "Single" found in header "Overall ↑Objects ↑Counting ↑Colors ↑Position ↑ Color ↑ Attribution Single Two" |
| T22 | quote_check.py --self-test | unchanged pass (regression guard: ex_validate must not alter quote_check) |
A throwaway prototype of steps 1-3 and 7 (scratchpad, 2026-10-20; not a deliverable) gave the expected
status for T01, T02, T03, T04, T05, T08, T09, T14, T15, T20 and T21, with quote_check.py imported read-only.
The other tests are untested. If the built tool gives a different status, the engineer reports it to the
orchestrator and does not change the test to fit.

### 6.7 What stays with the second reader
Column attribution when the header is scrambled (header_mismatch), the meaning of a value, and whether a row
is the default configuration. The gate measures value agreement on matched units (s10.4 G4).

## 7. Quality appraisal v0.2

### 7.1 Sub-items and scores
Sub-items take **yes, no or unclear**; every key in the schema is required (M4). Doubt goes to "unclear",
not to "no" (brief G4 changed for QA). Scores are computed twice: low (unclear read as no) and high (unclear
read as yes); the paper reports both, and any QA-based sensitivity analysis uses low with high as a check.

| Item | Sub-items | Score (each of low and high) |
|---|---|---|
| QA1 code | a own-code URL; b commit, tag, release or archive DOI named; c release only promised or on request; d dated link check (script) | 2 if a and (b or d); 1 if a or c; 0. Published only after d exists; until then the two-level QA1-text {link stated, promised only, none} (M4) |
| QA2 weights/data | a weights of every model behind the main comparison public with a named source; b data for it public and named; c missing part only promised | 2 if a and b; 1 if a or b or c; 0 |
| QA3 protocol | a prompts, templates or shots (or none by design); b steps or NFE and generation length; c value rule determinable (script: F2 not NS, NA, not ending +NS); d hardware | 4 yes: 2; 2-3: 1; 0-1: 0; all for the S14 table |
| QA4 variation | n S14 is NA; a two or more runs for S14; b three or more stated; c repeated runs only for another result | NA if n; 2 if b; 1 if a or c; 0 |
| QA5 uncertainty | n S14 is NA; a interval, SD, SE with stated meaning, or a defined test, for S14; b only elsewhere, or an undefined plus-minus on S14 | NA if n; 2 if a; 1 if b; 0 |
| QA6 budgets | n S14 is NA; a parameter counts of both S14 rows; b within 2x or stated matched; c inference budget of both; d training budget of both trained arms or stated matched | NA if n; 2 if a and c and (b or d); 1 if a or c or d; 0 |
| QA7 ablation | n script: S13 type in {theory, benchmark-or-dataset, analysis-only} (m5); a with/without or replaced comparison of the credited component; b everything else stated or shown fixed; c ablation only of another or a sub-component | NA if n; 2 if a and b; 1 if a or c; 0 |
| QA8 claims | from CL (s7.3) | NA if no checkable claim; 2 if every checkable claim is match or direction; 1 if at least one is and none contradicted; 0 otherwise |
| QA9 limitations | a limitations section or paragraph; b a failure case, negative result or worse setting | 2 if a and b; 1 if a or b; 0 |
A **run** (QA4, m4) is an independent repetition of the evaluation of one configuration with a different
sampling seed, or a separately trained model; re-scoring the same samples or adding benchmarks is not a run.
QA4 is narrowed to S14 (deviation, s13 item 12).

### 7.2 QA1 link check
One pass by the orchestrator (not by extractors, who have no web access), dated, logged as evidence level E1:
for every URL quoted under QA1a, HTTP status and whether a tag, release or commit is visible. Fills QA1d.

### 7.3 QA8 (fix for M2)
Statuses: match (the claimed number appears for the stated setting; trace required), direction (no number;
the stated direction holds for every compared row of the table the claim refers to; trace required),
partial, unsupported, contradicted, **not-checkable** (no number and no direction a table can test). The
brief's sentence "you never judge whether a claim is true" is replaced by: "QA8 asks only whether the paper's
own tables carry the claim; you never judge whether it is true in the world." QA8 is descriptive only (no
composite, no sensitivity rule) and is published only if the CL status kappa reaches 0.60 in the gate and in
the 10 percent second reading, computed over every claim either reader listed with "missing" as a category
for a claim the other reader did not list (s10.3 M-CL). Decision row: s13 item 13.

### 7.4 Version rule for anonymous submissions (fix for M5)
- M12 anonymous_version = true if the screened file matches `Anonymous [Aa]uthors?` in its first 6,000
  characters (287 of 608 in T1) or `Under review as a conference paper` in its first 2,000.
- For those records, tools/ex_metadata.py looks for the latest public de-anonymised version (arXiv by title,
  normalised title similarity at least 0.9 with an author check where available; or an accepted OpenReview
  camera-ready), logged at evidence level E1, and fetches it into its own folder.
- If found, an **EQ session** (claude-sonnet-5-5, isolated like every session) reads only that version's title
  page, footnotes and code, data and model availability statements and answers QA1 a-c and QA2 a-c with prose
  evidence from that file; these replace the anonymous-file answers, which are kept for a sensitivity table.
  Affiliations (M11) come from metadata or the public version, never from the anonymous file. EQ output
  rows have their own small shape (brief, EQ paragraph); ex_validate.py checks them with `--eq` (prose checks
  of s6.2 against the public-version file, required keys, searched rule).
- If none is found: QA1 and QA2 stay as read from the anonymous file, flagged anonymous-unresolved.
- RQ6 reports QA1 and QA2 by version class {named, anonymous-resolved, anonymous-unresolved}.

### 7.5 Study-type confounding (fix for M18)
RQ6 distributions are reported by S01 x training_free and by version class; comparisons by year and by venue
type are made within those strata (protocol amendment, s13 item 23).

## 8. Roles, second reading, adjudication, error rate

### 8.1 Roles
| Role | Model (Claude Code harness list) | Model-check alias (s9) |
|---|---|---|
| EA production extractor | claude-opus-5-5 | B |
| EB gate extractor; ER second reader | claude-sonnet-5-5 | A |
| EQ public-version QA reader | claude-sonnet-5-5 | A |
| EC adjudicator | claude-fable-5-1 (Route F; reconfirm no extra spend, OQ2-07) | C |
| human author | Shlok Kumar Goenka | rules EC's unresolved list; optional gold subset (s8.4) |
| gate-auditor | agent | signs the gate verdict (m16) |

### 8.2 Second reading (protocol s5)
Independent double extraction, blind (OQ-04 of v0.1 kept). Sample: a stratified 10 percent of each
tranche's includes, drawn with seed 20261115: 10 percent of the records with block K (23 of 225 in T1) and 10
percent of the others (39 of 383), `random.Random(20261115).sample(sorted(ids), ceil(0.10 * n))` per part.
ER fills the same blocks EA filled. Every study that enters a pooled estimate is also read by ER (reported
separately; not random). Option 7 or 8 of s2.8 adds ER on block F (and QA) for every other include.

### 8.3 Adjudication
EC sees the two records under neutral labels X and Y, assigned at random per study (seed 20261116 + record
index), never role names (m6). EC rules every differing field, unit and claim; for units found by one record
only it decides whether the rules require them; it records basis X, Y or neither and the splitting condition.

### 8.4 Error rate and its limit (fix for M12)
- Name in the paper: **disagreement-based error rate** (EA against the adjudicated value), with the
  statement that EA, ER and EC are all Claude models, so errors shared by EA and ER are invisible to it.
- Computation as v0.1 s8 on the ER sample: applicable (r, f) = at least one reader non-NA; enum and boolean
  fields exact after normalisation; set fields scored by Jaccard; units aligned by the s5.5 keys (omission,
  commission, value error, field error on matched units); cluster bootstrap over studies (2,000, seed
  recorded) for 95 percent intervals.
- **Human gold subset (optional, OQ2-10):** 6 records of the gate sample (2 per gate stratum, seeded), unit
  values and QA sub-items only, checked by the human author against the PDF, about 3 hours; estimates the
  error the model pair cannot see. If not done, the limitation is stated as D0034 states it for screening.

## 9. Isolation and post-session checks (D0032, M14)
As v0.1 s9, plus:
- dispatch.json lists for each id its blocks (L Q H, or L Q H K); nothing says why. The folder also holds
  the lookup-free brief and schema v0.2; EQ folders hold only the public-version file of each record.
- After every session: `python -I tools/ft_isolation_check.py <transcript> <folder>`;
  `python -I tools/ft_model_check.py --transcript <transcript> --role <alias>` with the alias of s8.1 (EA = B,
  EB/ER/EQ = A, EC = C; the tool's role map holds exactly these three model ids, so it is used unchanged);
  `python analysis/screening/quote_check.py --rows <output> --texts <folder>/fulltext`; `python -I
  tools/ex_validate.py ...`. A model mismatch discards the session's files (renamed DISCARDED-model-...) and
  the batch is rerun, as the T1 gate required. Each check's result goes in the dispatch log row.
- Batch sizes: block K records one per session if the text exceeds 133,280 bytes (the P90 of the 608 texts),
  else two; light-only records (L Q H) three per session up to 133,280 bytes, else one (M17).
- If ex_dispatch maps a role to a model other than the three in ft_model_check.py's map, ft_model_check needs
  a versioned extension first; that is a lab-engineer change outside this folder.

## 10. Pilot: development stage, then gate (fix for M1)

### 10.1 Preconditions
The T1 full-text gate passes (m7); the scope row (s2.9) and the rows of s13 marked "before the pilot" are
entered; tools of s11 pass their self-tests; the frame sha256 at draw time is recorded (the reference value
today is 00b6247b...; a different value at draw time is recorded, not a problem).

### 10.2 Stage A, development (n = 12, purposive; no pass or fail)
Pools and order (each draw `random.Random(20261111)` over the sorted pool, without replacement across pools):
4 from C1 (1 from i1 = ab, 3 from i1 = b); 2 from frame-R records whose corpus title matches
`benchmark|evaluat|analy[sz]|empirical|revisit|rethink|investigat|probing|understanding` (26 records); 2 from
frame R or C2 with text size above 133,280 bytes (52 records); 4 from frame R. EA and EB extract all blocks
(L Q H K) blind; EC adjudicates; the orchestrator and method-architect fix rules, examples and the
benchmark and metric lookups (s11). Stage A records are development material and are not reused.

### 10.3 Stage B, gate (n = 30, stratified random, fresh)
Strata (excluding Stage A ids; `random.Random(20261112 + h)`, h = 0, 1, 2): G-short 10 and G-long 10 from frame
R plus C2 (543 records, split at their median size, 72,648 bytes: 272 short, 271 long); G-mm 10 from C1. P(no
multimodal record) = 0 (v0.1: 0.331). EA and EB extract all blocks blind; isolation, model, quote and validator
checks per session; metrics computed by `analysis/extraction/agreement.py` before EC sees anything; then EC.

**Metric definitions** (applicable pair = at least one reader non-NA; an NA against a non-NA counts as
disagreement; NA-NA pairs are excluded, which removes the v0.1 inconsistency between s8 and s10.3):
- **M-raw(b)**, block raw agreement: blocks S (S01-S10, S13.type, S15, S16, I1-I5), D (D01-D11, D15, D16 entries),
  F (F1_status, F2_codes, F3-F6), QA-sub (every sub-item a reader writes), QA-score (nine low scores), CT
  (six). Credit per applicable pair: 1 for equal values, 0 otherwise; set-valued fields (S04, S05 families,
  S15, D01 as a set of modality:channel, D10, D11) get credit = Jaccard of the two sets (M16). M-raw(b) =
  sum of credits / number of applicable pairs, pooled over records.
- **Lower bound LB90**: 5th percentile of 4,000 stratified cluster-bootstrap resamples (records resampled with
  replacement within gate strata), seed 20261117.
- **M-kappa(b)**, namespaced pooled kappa: every category is renamed "field:value"; p_o = share of applicable
  pairs with equal values; p_e = sum over namespaced categories c of p_X(c) p_Y(c), where p_X(c) is the
  share of reader X's applicable values equal to c; kappa = (p_o - p_e) / (1 - p_e). Gwet's AC1 beside it;
  the mean of per-field kappas is reported, never gated (M1 "pooled kappa undefined").
- **QA weighted kappa**: linear-weighted Cohen's kappa on the low scores, pooled over QA1-QA9 (NA pairs
  excluded), with LB90.
- **Unit identification**: F1_H, F1_G (groups), F1_K = 2 |matched| / (|X units| + |Y units|), pooled over
  records, matching by s5.5, with LB90.
- **M-val**: share of matched values (H values and K values) with equal value_printed after normalisation,
  with LB90.
- **M-class**: rq_class agreement on matched groups (point).
- **M-S14**: S14 identical (same where, own_row and baseline_row after label normalisation), count of 30.
- **M-F1u**: F1 unit identical (same origin and same value cell or abstract sentence), count of 30.
- **M-CL**: Cohen's kappa of CL status over the union of claims, "missing" for a claim one reader did not list
  (claims matched by sentence identity of their prose evidence).
- **Per-field flags**: for each field with n_f >= 15 applicable pairs, flagged if agreements <= c(n_f), where
  c(n_f) is the largest c with P(X <= c | n_f, 0.90) <= 0.06 (table in Appendix A.2: 15:11, 16:11, 17:12,
  18:13, 19:14, 20:15, 21:16, 22:16, 23:17, 24:18, 25:19, 26:20, 27:21, 28:22, 29:22, 30:23). Fields with
  fewer than 15 pairs are "untested in the gate" and are judged on the production second reading.
- **Cost**: tokens per EA record from the session logs.

### 10.4 Decision rule (fixed before the gate; signed by gate-auditor)
**PASS iff every one of:**
- G1 evidence: validator first-pass acceptance at least 0.90 of entries for each extractor, and every entry
  accepted after one return.
- G2 schema: every record valid after one return.
- G3 blocks: for each of S, D, F, QA-sub, QA-score, CT: LB90(M-raw) >= 0.70, and M-kappa >= 0.60 (point;
  where one category exceeds 0.90 of values in a block, AC1 replaces kappa); QA weighted kappa >= 0.60
  (point).
- G4 units: LB90(F1_H) >= 0.70; LB90(F1_G) >= 0.60; LB90(F1_K) >= 0.60; LB90(M-val) >= 0.85; M-class >= 0.75.
- G5 anchors: M-S14 >= 23 of 30 and M-F1u >= 23 of 30 (23 is the smallest count whose one-sided 95 percent
  Clopper-Pearson lower bound reaches 0.60).
- G6 flags: in no block are more than a quarter of the judged fields flagged.
- G7 workload and cost: median EA tokens per gate record at most 120k and 90th percentile at most 200k; median
  H units at most 10 and K units at most 30 per record.
**Component decisions (not pass or fail of the form):** M-CL kappa >= 0.60 decides whether QA8 is published;
each CT type's kappa >= 0.60 decides whether that type is published.

### 10.5 Outcomes
- PASS: flagged fields are revised (text only) and re-measured on the production second reading; the form is
  frozen as v1.0 (git tag `extraction-v1`, sha256 of brief and schema in a decision row); production starts.
- FAIL on G1-G6: the failing blocks and every rule that touches them are revised; a fresh gate of 30 (seed
  20261114 + h, same strata, excluding all earlier pilot ids) re-tests **every** criterion. One re-gate at most.
  Blocks still failing become descriptive only (measured agreement disclosed, excluded from every verdict and
  pooled estimate) or are dropped; the user decides in a decision row.
- FAIL on G7 only: fallback ladder, each step brought to the user before production: (1) K narrowed by s5.7;
  (2) frame-R sample 120 to 90; (3) C2 moved to completion-only; (4) H limited to the F1 unit.
- Isolation or model-check failures are not gate failures: the session is discarded, rerun and logged.

### 10.6 Operating characteristics (Appendix A.2; simulation with record-level correlation, ICC 0.10)

| Rule | P(pass) by true value |
|---|---|
| G3 block LB90(raw) >= 0.70, n = 30 (20 + 10), fields per record 6-25 | 0.70: 0.06-0.08; 0.75: 0.40-0.56; 0.80: 0.83-0.96; 0.85: 0.99-1.00; 0.90: 1.00 (ICC 0.20, 10 fields: 0.80: 0.82) |
| same rule at n = 12 (for comparison) | 0.70: 0.10; 0.80: 0.66; 0.85: 0.91 |
| G4 LB90(F1_H) >= 0.70, about 6 units per record | 0.70: 0.07; 0.75: 0.41; 0.80: 0.89; 0.85: 1.00 |
| G4 LB90(F1_K) >= 0.60, about 5 units per record | 0.60: 0.06; 0.65: 0.29; 0.70: 0.71; 0.75: 0.96; 0.80: 1.00 |
| G4 LB90(F1_G) >= 0.60, about 3 groups per record | 0.60: 0.07; 0.70: 0.59; 0.75: 0.90; 0.80: 0.99 |
| G4 LB90(M-val) >= 0.85, 5-10 values per record | 0.85: 0.09; 0.90: 0.54-0.64; 0.93: 0.87-0.95; 0.95: 0.96-0.99 |
| G5 at least 23 of 30 | 0.60: 0.04; 0.70: 0.28; 0.75: 0.51; 0.80: 0.76; 0.85: 0.93; 0.90: 0.99 |
| per-field flag, n_f = 15, flag at <= 11 | false flag at 0.90: 0.056; detection at 0.65: 0.83, at 0.70: 0.70 |
Reading: an instrument at the levels the protocol's lines imply (blocks 0.85, H 0.85, groups and K 0.75, values
0.95, anchors 0.85) passes all criteria with probability about 0.7 if the criteria were independent (they are
positively correlated, so this is a lower estimate); one quantity at its failing level (blocks 0.70, H 0.70, K
0.60, values 0.85, anchors 0.60) gives at most 0.09. Cost: 60 extraction records plus 30 adjudications per gate
(s2.8 component 6).

## 11. Tools to build (lab-engineer; nothing in this folder is executable)

| Tool | Does |
|---|---|
| tools/ex_dispatch.py | dispatch folders as v0.1 s9, with blocks per id, model-check alias, size-based batching, log rows with check results |
| tools/ex_validate.py | s6.2-s6.6 and Dv filling; imports analysis/screening/quote_check.py read-only |
| tools/ex_metadata.py | M03, M05, M11, M12, M13 (arXiv API first-version date; Semantic Scholar, OpenAlex, DBLP, OpenReview venue and affiliations; public-version resolution and fetch; E1 log). The 15 U- and R-prefixed records and the 455 without an arXiv id in the corpus record use OpenReview cdate (389 corpus records carry an OpenReview id), DOI issue date or publisher date, with the source recorded (M03 first_version_source) |
| analysis/extraction/draw_pilot.py | s10.2 and s10.3 draws with manifest |
| analysis/extraction/draw_rq_sample.py | s2.4 draw, s8.2 ER draw, manifest with sha256 values and weights |
| analysis/extraction/agreement.py | s10.3 metrics, s8.4 error rates, alignment of s5.5, bootstrap |
| analysis/extraction/lookups/benchmark-ids-v1.csv, metric-ids-v1.csv | printed string -> id, built in Stage A, frozen with v1.0, extended only under a new version by EC with a log line (M9c) |
| analysis/extraction/strata.py, gate_oc.py | Appendix A scripts, committed with their logs |
| (gate check) gate-auditor | block F text equals codebook v1.2 B-9 to B-28 with v1 and v1.1 |

## 12. How the fields feed the paper
As v0.1 s4, with: section 4 counts per study and per distinct model with provenance (s4.3); RQ1 counts per
class and year from M03 over every include, modality reported with M06; RQ2-RQ4 tables with census and
weighted columns (s2.6); RQ5 from C1 groups (RQ5-*), S16, CT5 and CL; RQ6 from QA low and high scores by
S01 x training_free and version class; s7 pooling from K15 matched contrasts with metric_id, benchmark_id,
task family, n_eval and variance, groups defined by M11 and M16 under the statistician's rule (OQ-18 of v0.1);
section 6 census from block F on every include.

## 13. Protocol and ledger deviations that need a decision row
"Before the pilot" marks rows the gate depends on.

| # | Deviation or refinement | Protocol / ledger | When |
|---|---|---|---|
| 1 | Scope: contrast data on multimodal plus a stratified sample (s2) | s5 "per study"; user 2026-10-16 not in ledger | before the pilot (s2.9 draft) |
| 2 | Hypotheses E1-E3 and evaluability not implemented | s6 paragraph; D0008, D0009; no s10 amendment | before the pilot |
| 3 | Contrasts narrowed to RQ classes plus credited ablations; aggregate-column rule for sub-scores (s5.3-5.4) | s5 "every within-paper contrast" | before the pilot |
| 4 | Headline numbers = abstract outcome numbers plus the F1 number (s5.2) | s5 "every reported headline number" | before the pilot |
| 5 | QA from sub-items with yes/no/unclear, low and high scores, NA for QA4-QA8 (s7.1) | s6 0/1/2 | before the pilot |
| 6 | Second reading by independent double extraction on a stratified 10 percent | s5 "verified by a second reader" | before the pilot |
| 7 | Appraisal second rater on the 10 percent sample only (MIN, REC) | s6 "two raters as in section 4" | with row 1 |
| 8 | Census extension single-coded on 90 percent (MIN only) | D0011; framework-v2 item 2 | with row 1 |
| 9 | Model adjudicator (claude-fable-5-1) instead of a human resolving disagreements | s4 step 4 via s6 | before the pilot |
| 10 | No human validation sample for extraction or appraisal (unless the gold subset is done) | s4 step 3 via s6 | before production |
| 11 | QA1 "usable" from the text plus one dated link check; QA1 published two-level until then | s6 QA1 | before the pilot |
| 12 | QA3-QA6 anchored on S14; QA4 narrowed to S14; "run" defined | s6 QA3-QA6 | before the pilot |
| 13 | QA8 statuses reintroduce part of the suspended construct; descriptive only, gated on kappa 0.60 | D0008; s6 QA8 | before the pilot |
| 14 | Error rate defined against model adjudication ("disagreement-based") | s5 "field-level error rate" | before production |
| 15 | Anonymous submissions: QA1, QA2, affiliations from the public version (s7.4) | s3 "Version rated" | before the pilot |
| 16 | Extraction from the screened PyMuPDF text, not the latest arXiv version | s3 "Version rated" (v0.1 OQ-17) | before the pilot |
| 17 | CT1-CT6 published per type only where kappa >= 0.60, from a component of a rubric that failed its criterion | s6 evaluability; RESULTS.md | before production |
| 18 | nonlang_only includes: no contrast data, separate row | D0032 item 3 | with row 1 |
| 19 | Pilot replaced by development stage and gate with lower-bound criteria; gate signed by gate-auditor | v0.1 s10 (not protocol) | before the pilot |
| 20 | Multimodal defined as C1 plus C2 (title regex) plus completion | user 2026-10-16 wording | with row 1 |
| 21 | Task-family readings (captioning and knowledge MC under understanding; editing = non-text editing) and state-space edge cases (v0.1 OQ-08, OQ-09) | s5 fixed lists | before the pilot |
| 22 | D12 derived, D13 dropped, D15 objective and D16 provenance added | framework-v2 D1; s5 list | before the pilot |
| 23 | RQ6 by year and venue type only within S01 x training_free and version strata | s1 RQ6 "by year and venue type" | before production |
| 24 | "Independent groups" rule for pooling (M11, M16) | s7 | before any pooling |
| 25 | Targeted extension of block K for cells near the pooling threshold (s2.7) | s7 | with row 1 |
| 26 | Protocol freeze: form v1.0 frozen while the protocol is DRAFT v0.1 (v0.1 OQ-19) | protocol header freeze rule | before production |

## Appendix A. Scripts behind every count in this plan (scratchpad, 2026-10-20)
To be committed by lab-engineer as analysis/extraction/strata.py and gate_oc.py with logs. Summaries:

**A.1 strata.py** (Python 3.14, stdlib): reads t1-decisions-all.jsonl (decision = include); titles from the
three corpus files listed in the header, keyed by `nid` (first file wins); C1 = i1 in {b, ab}; NL =
nonlang_only; C2 = i1 = a, not NL, title matches the s2.3 regex; FR = the rest of i1 = a; size =
os.path.getsize of fulltext-pymupdf/<id>.txt; anonymous = regex `Anonymous [Aa]uthors?` in the first 6,000
characters; strata at the FR median size; proportional allocation by largest remainder; Stage A and gate pools.
Output on 2026-10-20: C1 53, NL 12, C2 52, FR 491 (sum 608); FR median 73,857; strata anon-long 166,
anon-short 75, named-long 79, named-short 171; total anonymous 287; R+C2 543, median 72,648; size > 133,280: 52
in R+C2; benchmark/analysis title pool 26; sha256 of newline-joined sorted ids: C1 91615db39bc8c69600064164d9478da544b76c1a13b7e1d09e9cb99ed8f8a80e, C2
b09306d34b5a4247431367d17e820763608a4a306d4f1ce088f576bb35312f73, NL
0bc9bf7d746ea841be7ea4319b74213602ebab460e3d57aa7deebfe62766b8e4, FR
08e76b1b00a5088446223916e98493513b3f968e212775629409627dc5a09f42.

**A.2 gate_oc.py** (numpy 2.4.2, scipy 1.17.1; seed 20261020; 2,000 replicates, 1,000 bootstrap resamples;
value-agreement rule in value_oc.py, seed 20261021): record agreement p_r ~ Beta with mean p and ICC rho
(alpha = p(1/rho - 1), beta = (1-p)(1/rho - 1)); agreements ~ Binomial(m, p_r); units: union units per record
~ Poisson(lambda), share found by both readers p_b = F1 / (2 - F1) with Beta record heterogeneity, the rest
split evenly between the readers; LB90 = 5th percentile of a stratified cluster bootstrap (strata 20 and 10);
binomial rules exact (Clopper-Pearson, scipy.stats). Results are those of s10.6 and the c(n_f) list of s10.3.

**A.3 precision**: half-width = 1.96 sqrt(p(1-p)/m (1 - (m-1)/(N-1))) with p = 0.5, m = n x prevalence, N =
491 x prevalence; Kish deff = n_tot sum(w^2) / (sum w)^2 with 120 weights of 491/120 and 105 weights of 1.
