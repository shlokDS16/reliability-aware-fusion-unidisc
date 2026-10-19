# Response to the red-team audit of extraction form v0.1

Audit: `research/review/audits/2026-10-20-redteam-extraction-v0.1.md` (3 critical, 18 major, 17 minor, plus
the Item 4 list of deviations). Revised files: EXTRACTION-PLAN-v0.2.md (PLAN), extraction-schema-v0.2.json
(SCHEMA), extractor-brief-v0.2.md (BRIEF), OPEN-QUESTIONS-v0.2.md (OQ). Status: **fixed** (the instrument now
does what the finding asks, or an alternative that meets its rejection test), **partly fixed** (reason given),
**rejected** (reason given). "Fixed" is a statement about the specification; nothing has been run, and the gate
(PLAN s10) is the empirical test.

Counts: 34 fixed, 4 partly fixed (M5, M12, M13, m17), 0 rejected outright (two sub-proposals rejected with reasons: in C1 and M1).

## Critical

| # | Finding | Status | What changed (where) |
|---|---|---|---|
| C1 | quote_check cannot verify ablation rows; 40-word cap makes wide-table quotes impossible | **fixed** (by an alternative) | Table values get their own evidence kind (`cell_evidence`) with row_label, first_col, cells, header, caption; a new table-aware checker in tools/ex_validate.py matches the whole row label at a row start, then the quoted cells, then the value's column; 40-token cap on label plus cells, continuation entries for wide rows (PLAN s6.1, s6.3; SCHEMA $defs.cell). Prose quotes still pass through quote_check.py unchanged plus a 40-word cap and a numeric-only rejection (PLAN s6.2). Unit tests T01-T22 include the M03416 Table 3 cases and the synthetic 6-row, 7-column table (PLAN s6.6). A scratchpad prototype gave the expected statuses: T01 pass, T02 cells_mismatch, T03 row_not_found, T04 negation_before under quote_check, T14 cell pass while every prose start of at most 40 words fails. Sub-proposal rejected: a versioned quote_check v1.7 with a table-aware negation window. Reason: the brief forbids editing quote_check.py, and a separate evidence kind keeps the screening tool's 38 self-tests and behaviour untouched while checking more (row identity, column, page) than a widened window could. |
| C2 | H and K unit definitions not reproducible | **fixed** (in specification; unit identification is a gate criterion) | One generator per unit type (PLAN s5.1). H = abstract outcome numbers plus the F1 number, with value_type {level, difference, ratio, other}, arm_role, reference_printed; sizes are not units (s5.2; C2.1, C2.2). Contrasts are comparison groups with arms and an anchor; a contrast unit is one group x one outcome column, so one ablation on three benchmarks is one group_id with three units (s5.3-5.4; C2.6). Several AR baselines are levels of one RQ2 group; "autoregressive" is the paper's own label for the generator of the scored output, judged per output for unified models (K-AR; C2.4). Benchmark and analysis papers: focal model = the abstract's first-named diffusion model; RQ2 groups take every diffusion and AR row (C2.3). Keys use only located strings and controlled fields with a written normalisation and a Jaccard matching rule; factor_printed is in no key (s5.5; C2.5). The TrustLDM, Muddit and CONFLUX readings in the finding now each have one compliant reading. |
| C3 | Scope contradicts the user's decision of 2026-10-16 | **fixed** in the instrument; ledger entry pending | PLAN s2: light blocks, headline numbers and QA on every include; block K on C1 (i1 in {b, ab}, 53), C2 (multimodal titles among i1 = a, 52) and a stratified random sample of 120 of 491, with strata, allocation, seeds, weights, estimators, completion and targeted-extension rules, precision justification and costed options. Draft ledger row: PLAN s2.9 (the orchestrator enters it). Pilot strata follow the same population split (PLAN s10.3). |

## Major

| # | Finding | Status | What changed (where) |
|---|---|---|---|
| M1 | Pilot of 12 cannot run the stop rule | **fixed** | Development stage of 12 (purposive, as the red-team proposed: 4 multimodal, 2 benchmark or analysis by title, 2 top size decile, 4 random) with no pass or fail, then a gate of 30 (10 short and 10 long i1 = a, 10 multimodal), P(no multimodal) = 0 (PLAN s10.2-10.3). Every metric is defined, including NA handling (NA-NA excluded, NA vs value = disagreement) and the namespaced pooled kappa formula. Decision rule on lower 90 percent stratified cluster-bootstrap bounds; per-field flags only for fields with at least 15 applicable pairs, with an exact threshold table; a re-gate re-tests every criterion (s10.4-10.5). Operating characteristics simulated with record-level correlation (s10.6; Appendix A.2). Sub-proposal rejected: weighting gate statistics by stratum (27.75 and 5.3). Reason: the gate measures the instrument's reliability across record types, not a population quantity; per-stratum figures are reported beside the pooled ones. |
| M2 | QA8 reintroduces the failed construct with a lower bar | **fixed** | Status not-checkable added; CL kappa computed over every claim either reader listed with "missing" as a category, threshold 0.60, deciding whether QA8 is published at all; QA8 descriptive only; the "never judge" sentence rescoped to "true in the world" (PLAN s7.3; BRIEF WHAT YOU DO and CL; OQ2-11; PLAN s13 row 13). |
| M3 | Main comparison ambiguous, drives four QA items | **fixed** | S14 is a table and row pair with a written rule; QA3-QA6 all anchored on it; S14 agreement is its own gate metric (M-S14, at least 23 of 30) (PLAN s5.6, s10.3-10.4; SCHEMA study.main_comparison). |
| M4 | Tie rule and schema bias QA downward | **fixed** | Sub-items yes/no/unclear, every key required by the schema (a missing key fails validation; checked on a synthetic record); doubt goes to unclear; scores reported as low and high bounds; QA1 published two-level until the dated link check exists (PLAN s7.1-7.2; SCHEMA qa). |
| M5 | 47 percent anonymous submissions confound QA1, QA2, S11 | **partly fixed** | M12 anonymous_version by rule; public-version lookup and fetch; EQ sessions answer QA1 and QA2 from the public version; affiliations from metadata only (S11 moved to M11); RQ6 by version class (PLAN s7.4; OQ2-08). Partly because records without a public version stay appraised from the anonymous text (flagged anonymous-unresolved and reported separately); no rule can remove that residue. |
| M6 | Design block mixes "not stated" with "not this paper's choice" | **fixed** | Provenance per design field {contributed, inherited, not_stated, NA} with inherited_from; section 4 counts per study and per distinct model; focal-model rule for analysis and benchmark papers; D13 dropped and never set beside 36/47 (PLAN s4.3; BRIEF G1, block D). |
| M7 | RQ2 comparability fields missing | **fixed** | Per-arm params, training tokens, shots, scoring {generated, likelihood, not_stated}, number_source {run-by-authors, copied-stated, not_stated} with the row-label-citation rule, per-arm steps and generation length (PLAN s4.8 A01-A13; SCHEMA $defs.arm). K matched requires equal stated scoring for RQ2 (K15). |
| M8 | RQ4 dose-response cannot be built | **fixed** | level_num, dose_unit, per-arm gen_length and steps, figure shape code; F4 and RQ4-steps counted separately (PLAN s4.8, s5.3). |
| M9 | Inputs for s7 pooling absent | **fixed** | n_eval_printed per unit; group_id; frozen benchmark and metric lookup tables (ids derived by script, extractors write printed strings); scale field (PLAN s4.9, s5.4, s11). |
| M10 | RQ1 objective missing; task-family definition contradicts itself | **fixed** | D15 objective; S05 over all results with a generated_sample flag per family (PLAN s4.2-4.3; SCHEMA study.task_families, design.objective). |
| M11 | Number evidence does not fix the cell | **fixed** | Whole-token value check for prose; for cells the value must be the j-th token after the located row label, the row label must equal the arm's label, the column label is checked against the header and the share of header mismatches is reported (PLAN s6.2-6.3). Numbers-only prose rejected (T17). |
| M12 | "Error rate" is model disagreement | **partly fixed** | Named "disagreement-based error rate" with the stated limit (PLAN s8.4); optional human gold subset of 6 gate records (about 3 hours). Partly because the gold subset depends on the human author's time (OQ2-10; D0034 precedent). |
| M13 | Census extension single-coded for 90 percent, against D0011 | **partly fixed** | Option 7 (block F double on every include, 15.7M-22.4M) is costed and recommended (package REC); MIN keeps it single-coded with a decision row (PLAN s2.8, s13 row 8; OQ2-01). Partly because the choice is the user's. |
| M14 | Fallback-model check missing from the harness | **fixed** | ft_model_check.py runs after every session through the role alias map (EA = B, EB/ER/EQ = A, EC = C; the tool's map holds exactly these three model ids, so it is used unchanged); mismatch discards and reruns (PLAN s9, s8.1). |
| M15 | Metadata the RQs need has no source | **fixed** (specified, not built) | tools/ex_metadata.py: arXiv first-version date, OpenReview cdate for the many records without an arXiv id in the corpus record (455 of 606 corpus records have none; 389 have an OpenReview id), Crossref or publisher dates, venue from Semantic Scholar, OpenAlex, DBLP, OpenReview; E1 log; rule for U- and R-prefixed records (PLAN s4.1, s11). |
| M16 | Main-table fields lack a reliability gate | **fixed** (modified) | D12 levers derived by a written map (no judgement); S13 coded to a type list; set-valued fields enter block raw agreement with Jaccard credit, so they are gated through G3 instead of a separate Jaccard line (PLAN s4.3, s10.3). |
| M17 | Workload not costed | **fixed** (estimates remain inference) | Costed options and components (PLAN s2.8); token ceiling and workload limits in the gate (G7: median 120k and P90 200k per full-form record; median H 10, K 30) with a fallback ladder (s10.4-10.5); size-based batching (s9). The red-team's example ceiling (median above 80k) is replaced by 120k because a gate record carries every block including K, which the red-team's own per-record estimate puts at 60k-100k. |
| M18 | RQ6 confounded by study type | **fixed** | RQ6 by S01 x training_free and version class; year and venue comparisons within strata; decision row (PLAN s7.5, s13 row 23). |

## Minor

| # | Finding | Status | Where |
|---|---|---|---|
| m1 | Three `searched` rules | fixed | one rule: every negative value of a Q-coded field and every QA "no" or "unclear", key = the cond id (PLAN s4, s6.4; BRIEF E1; SCHEMA searched.propertyNames) |
| m2 | cond pattern excludes QA6n, QA7n; no sub-field conds | fixed | SCHEMA $defs.cond allows QA<n>n and dotted sub-fields (S10.steps, D07.rule, G03.A2) |
| m3 | figure-only F1 has no H literal | fixed | value_printed "figure-only" or "unreadable" allowed for F1 units (PLAN s5.2; BRIEF H-2) |
| m4 | QA4 narrowed; "run" undefined | fixed | run defined; narrowing listed (PLAN s7.1, s13 row 12) |
| m5 | QA7 n rule inconsistent | fixed | QA7 n derived from S13 type {theory, benchmark-or-dataset, analysis-only} (PLAN s7.1) |
| m6 | EC sees role labels | fixed | neutral X and Y, random per study (PLAN s8.3; BRIEF adjudication) |
| m7 | Frame not final | fixed | draw only after the T1 gate passes; frame sha256 recorded at draw time (PLAN s10.1, s2.4) |
| m8 | Pilot records mix form versions | fixed | pilot records are not reused; production re-extracts any drawn record (PLAN s2.4, s10.2) |
| m9 | D12 rows not aligned with framework-v2 | fixed | value rows merged into one V row (PLAN s4.3; SCHEMA design.levers) |
| m10 | S02 mixes understanding-only VLMs with unified models | fixed | modality reported with M06 (i1); C1 and C2 separate in every table (PLAN s4.2, s12) |
| m11 | Synergy benchmark coded as a contrast | fixed | moved to study field S16; rq_class removed (PLAN s4.2, s4.8) |
| m12 | metric_kind undefined in the brief | fixed | BRIEF G5 |
| m13 | Abstract H keys collide | fixed | key includes value_printed and order of appearance (PLAN s5.2) |
| m14 | "Limitations stated" not captured | fixed | S15 limitation categories (PLAN s4.2) |
| m15 | params_b conflicts with "never compute" | fixed | unit conversion allowed (BRIEF WHAT YOU DO, S07) |
| m16 | Human author signs the pilot verdict | fixed | gate-auditor signs (PLAN s8.1, s10.4) |
| m17 | No link between records of the same work | partly fixed | M16 family_id by script on S07, S08 and author overlap, confirmed by EC (PLAN s4.1). Partly because isolated extractors cannot see other records, so the link is made after extraction, not by the extractor |

## Item 4: deviations missing from v0.1 PLAN s12

| # | Deviation named by the red-team | Where in PLAN s13 |
|---|---|---|
| 1 | Census extension single-coded on 90 percent | row 8 (with the scope row) |
| 2 | Model adjudicator; no human validation sample for appraisal | rows 9, 10 |
| 3 | QA1 "usable" from text, link check deferred | row 11 |
| 4 | QA4 narrowed to the main comparison | row 12 |
| 5 | QA8 statuses reintroduce the suspended criterion | row 13 |
| 6 | Error rate against model adjudication | row 14 |
| 7 | Anonymous-submission texts appraised as fetched | row 15 |
| 8 | CT1-CT6 from a rubric that failed its criterion | row 17 |
| 9 | Scope against the user's instruction, not in the ledger | row 1 (draft row in s2.9) |
PLAN s13 lists 26 rows in all, including the seven of v0.1 s12.

## Items 6 and 7 (summaries)
Item 6 (cost): answered by PLAN s2.8 using the red-team's per-record estimates. Item 7 (what would make the data
unusable): each named cause has a field or rule: value type (H20), duplicates (s5.1, s5.5), group ids and
numeric levels (G01, A06), free-string metrics (lookups, K16), inherited versus not stated (D16), version
dependence (M12, s7.4), tie rule (unclear, bounds), year and venue metadata (M03, M05).

## Not addressed here (outside this brief)
Block F against codebook v1.2 (gate-auditor, PLAN s11); isolation wording against ft_isolation_check.py; whether
t1-decisions-all.jsonl already reflects the t1b081 rerun (the draw records the frame hash at draw time).
