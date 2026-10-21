```yaml
agent: gate-auditor
date: 2026-10-21
brief: Gate audit of the Section 5 text and related passages written or changed on 2026-10-21 (Paper 1, PRISMA review, ACM CSUR)
sources_examined:
  - analysis/extraction/d0052/rq-results.json, rq-results.md, qa-table.jsonl (rq_analysis.py, rerun into a scratch copy)
  - analysis/extraction/d0052/qa1-links.jsonl, qa1-owner-reads.jsonl, batch-log.jsonl, sample.json, seed-sample.json, gate-manifest.json, stage-a-manifest.json
  - analysis/extraction/d0052/agreement-8-texts/agreement-stage-a.json, per-record-stage-a.csv; analysis/extraction/agreement.py (F1 definition, line 636)
  - analysis/extraction/d0052/EC/*, EC-void/README.md
  - analysis/rq1/rq1-counts.json, rq1-includes.jsonl; analysis/screening/agreement-ft-t1.json
  - research/review/extraction/extraction-schema-v0.5.json, EXTRACTION-PLAN.md, extractor-brief-v0.5.md; research/review/evaluability-rubric.md
  - research/review/coverage/design-space-v1.csv, census-result-v2.md
  - runs/EXP-003/analysis/confirmatory.json (only present in worktree dlm-discovery-resume-ca3357)
coverage: >
  All of sections/05-rq-evidence.tex; 02-method.tex lines 109-125 (extraction) and 161-175 (departures);
  10-limitations.tex line 13; 11-conclusion.tex; main.tex abstract (line 75); 01-introduction.tex line 43;
  supplement.tex S4 (lines 216-233) and S6 (lines 268-284); the five generated tables. Not covered: the rest of
  Section 2, the census section, the EXP-003 section, citations, the PDF build. The "153 fields" of the form
  (02-method.tex:116) was not counted.
claims:
  - statement: The five generated tables are byte-identical to what qa_tables.py and agreement_table.py write now
    status: supported
    evidence: scratch regeneration (python -I, OUT redirected), diff equal for all five
    level: E4
    confidence: 0.99
  - statement: rq-results.json, rq-results.md and qa-table.jsonl are byte-identical to a fresh run of rq_analysis.py
    status: supported
    evidence: scratch rerun with outputs redirected, diff equal
    level: E4
    confidence: 0.99
  - statement: The RQ4 verdict "well supported for the direction" follows from the numbers under the Section 5 definitions
    status: contradicted
    evidence: rq-results.json RQ4 (variance_any 0.26, budget_reported_any 0.55); auditor recompute of sweep studies (findings 1)
    level: E4
    confidence: 0.9
  - statement: In three of the five signed RQ5 ablations the joint model is better
    status: contradicted
    evidence: arm labels of the synergy groups (finding 2)
    level: E4
    confidence: 0.85
competing_explanations: []
unknowns:
  - Whether the two M18816 Table 31 groups are meant as one comparison (anchors point opposite ways).
  - The sign convention for M15992 Table S7 is read from arm labels ("Main-table model" vs "Multi-task model"); the paper text was not opened.
next_test: {hypothesis: "RQ4 direction holds at study level", intervention: "add study-level majority-up and all-up rows (weighted) to rq_analysis.py and the S6 table", primary_metric: "weighted share of sweep studies with majority-up curves", falsifier: "share below 0.5 or interval covering 0.5", gpu_hours: 0}
```

# Gate audit: Section 5 (RQ evidence) and related text, 2026-10-21

## Verdict: FAIL

The generated tables and the analysis outputs reproduce exactly, and nearly every number in the text equals its
source. The gate still fails on criteria (3) and (4). The RQ4 verdict does not follow from the verdict definitions
in Section 5, and its direction claim rests on unit totals that Section 5 itself calls indicative. That claim is
repeated in the conclusion and the abstract. The RQ5 direction sentence misreads the script's sign convention. The
extractor-agreement counts in three places describe an F1 numerator as a count of matched groups. The Method's
stratum sizes differ from the weights the estimates use. All fixes are text or script edits; none needs new
extraction. A re-audit can be limited to findings 1 to 11.

Severity counts: 4 major, 7 moderate, 11 minor (22 findings).

## Criterion status

| Criterion | Status | Evidence |
|---|---|---|
| Every number traced to its source | partly: all found; 5 found but described wrongly (findings 2, 3, 4, 7, 12) | table below |
| (1) Generated tables equal current script output | met | qa-summary, qa-per-study, sensitivity, extraction-agreement, extraction-agreement-records: identical on regeneration into the scratchpad; rq_analysis.py rerun gives identical rq-results.json/.md and qa-table.jsonl |
| (2) Strata, weights and frame consistent across sections | partly | 79 in frame, M18059 out, 19/20/20/20, 1,074 seed weight and 59 update studies agree everywhere; Method strata 53/272/271 do not match the weights 52/267/265 (finding 4); 05:7 says counts leave out the seed corpus (finding 5) |
| (3) Each verdict follows from its numbers under the stated definitions | partly | RQ2 and RQ3 follow; RQ4 does not (finding 1); RQ5 is borderline (finding 11); RQ6 uses a verdict outside the four defined (finding 18) |
| (4) No claim exceeds its evidence | partly | findings 1, 2, 6, 8, 9, 10 |

## Number reconciliation (scope text)

"=" means found and equal after rounding. Section 5 line numbers refer to sections/05-rq-evidence.tex.

| Location | Numbers | Source value | Status |
|---|---|---|---|
| 05:7 | 615; 80 | rq1-counts n 615; n_sampled 80 | = |
| 05:12 | 557, 41, 17; 12 | i1 {a 557, b 41, ab 17}; nonlang_only 12 (all I1(a)) | = |
| 05:13 | 410, 164, 28, 13 | mm text 410, multimodal 164, other 28, splits 3+2+2+6 | = |
| 05:14 | 449, 111, 55; 36, 12, 10 | year; i1_by_year | = |
| 05:15 | 246, 237, 394, 32 | rq_both; the RQ5 32 are all I1(b) 24 + ab 8 | = |
| 05:19 | 79; 19/20/20/20; 1,074; 52 | n_by_stratum; N_h S-seed 1073.85, G-mm 52 | = |
| 05:21 | 27; 0.55 to 0.81; 0.33 to 0.11 | rejected_at_final_pass 27; S0/S1 0.551/0.806, 0.327/0.113 | = |
| 05:23 | 42/79 0.70 [0.55, 0.81]; 18 (13 G-mm); 6; 15, 10, about 0.46; 12; 17 0.25 [0.14, 0.40]; 26; 28; 37; 9; 18 0.31 [0.19, 0.47] | RQ1 block | = except "28 only" (finding 12) |
| 05:27 | 35 0.46 [0.32, 0.61]; 0/35 upper 0.10; 31 0.84 [0.59, 0.95]; 7 0.20 [0.08, 0.43]; 3 | RQ2 | = |
| 05:28 | 32, 15, 14; 131/129/2; 7 of 10; 6 of 10; 10 0.15 [0.07, 0.29] | RQ2 | = |
| 05:33 | 33 0.35 [0.23, 0.50]; 22, 7, 6, 6, 3, 1; 20/27 0.74 [0.42, 0.92]; 289/113/16 | RQ3 | = |
| 05:34 | 6/33 0.33 [0.14, 0.59]; 9 0.31 [0.13, 0.57]; 4 | RQ3 | = |
| 05:39 | 47 0.75 [0.61, 0.85]; 18, 13, 11, 10, 10, 7, 5; 31 0.55 [0.38, 0.71]; 12 0.26 [0.14, 0.44] | RQ4 | = |
| 05:40 | 139/12/16/14 of 181; 10/19 0.62 [0.34, 0.84] | dose_shapes_units; any_nonmonotone_dose_curve | = |
| 05:45 | 20; 3; 0 benchmarks; 8; 2 and 1 (R0963); 5 signed; 3 vs 2 | RQ5 | counts =; meaning of "3 vs 2" wrong (finding 2) |
| 05:50 | QA1 17 0.32 [0.20, 0.48]; 17 of 19; QA2 4 0.11 [0.04, 0.25]; QA4 11/74 0.10 [0.05, 0.20]; QA5 10 0.10 [0.05, 0.20]; QA6 half; QA7 about half; QA9 0.70 [0.55, 0.81] | RQ6, low reading; qa1-links.jsonl | = except "17 of 19 code links" (finding 7) |
| 05:51 | 260; 64, 84, 49, 51, 12; 0 contradicted; 7/74 0.05 [0.01, 0.14]; 7/54 | claims_status (in-frame); claims_vs_tables_QA8 | = |
| 02:115 | 53, 272, 271 | gate-manifest sizes; weights use 52, 267, 265 | found but different (finding 4) |
| 02:115 | 12, 12, 7; 20 of 167; 1,106; 1,074 | stage-a 12; nonlang 12; R797 7; seed-sample.json | = |
| 02:118 | 8 of 80 | second_reader_ids 8 | = |
| 02:120 | 80; 44; 79; 42 of 44; 27 | batch-log: 44 EA batches, 42 with pass 2 (the 2 without had 0 rejected), model_ok and isolation all true | = |
| 02:121 | one voided session; 616/616; 75/76; 48/52; 72/245; 300/1,227 | EC-void ecx002b; agreement-stage-a metrics | values = ; last three described wrongly (finding 3) |
| 02:122 | 2026-10-21; 17 of 19; three cases | qa1-links (17 yes, 2 no-url); qa1-owner-reads 3 lines | "17 of 19" described wrongly (finding 7) |
| 02:170, 174 | 80 (60 + 20); 8; 79 | as above | = |
| 10:13 | kappa 0.894; 8 of 80; 72 of 245; 0.6; 27 | agreement-ft-t1 0.8939; falsifier true; sensitivity | 72 of 245 described wrongly (finding 3) |
| 11:5 | 47, 11; 147 of 153 | design-space-v1.csv 36 yes / 11 partly; census-result-v2.md:76 | = |
| 11:7 | 35 of 79; 10 of 19; 3 of 20; 11 of 74; 10 | rq-results.json | = |
| 11:9 | 0.180, 0.051, 0.126 | confirmatory.json arms.G 0.1797, P64 0.0505, delta1 0.1256 | = (file not in this worktree, finding 20) |
| main.tex:75 | 615; 80; 35; 3 of 20; 11 of 74; 147 of 153; 0.126 [0.076, 0.177] | as above; delta1 pct95 [0.0758, 0.1768] | = |
| 01:43 | 615; 47; 80 | as above | = |
| supplement S4/S6 | 4,000 resamples, 5th percentile, 0.6; 79; 59 | parameters bootstrap_B 4000, lb_quantile 0.05; n 79; update strata 59 | = |

## Findings

### Major

1. **RQ4 verdict does not follow, and the direction claim rests on unit totals.**
   - Location: 05-rq-evidence.tex:41. The same claim is carried into 11-conclusion.tex:7 and main.tex:75.
   - Text: "Verdict: well supported for the direction, weakly supported for its size. More compute usually buys quality". In the conclusion, "More inference compute usually improves quality"; in the abstract, "more inference compute usually, but not always, improves quality".
   - Source, definitions: Section 5 defines "well supported" as comparisons that point the same way AND hold budgets AND report variation (05:20). For inference contrasts the budget is reported in 0.55 [0.38, 0.71] and variation in 0.26 [0.14, 0.44] (rq-results.json RQ4).
   - Source, unit totals: the 139 of 181 "up" curves are unit totals, which 05:20 says are only indicative. Two studies supply 122 of the 181 curves and 106 of the 139 "up" curves: M15781 has 62 (56 up) and M17249 has 60 (50 up).
   - Source, study level (auditor recompute with rq_analysis.py's own est(); not in rq-results.json): of the 19 sweep studies, 6 are up throughout (weighted 0.31 [0.11, 0.61]) and 10 have a majority of curves up (weighted 0.42 [0.19, 0.69]). Three studies have only falling or peaked curves (M12879, M13196, M18735).
   - Fix: add study-level "majority up" and "all up" estimates to rq_analysis.py and the S6 sensitivity table. Restate the verdict under the stated definitions as "weakly supported" (or "mixed"), and name the two dominant studies. Drop "for its size", since no size is estimated. Change the conclusion and abstract to match, for example "more compute improves quality in some sweeps but not in about half of the studies that sweep it".

2. **The RQ5 direction sentence misreads the sign convention.**
   - Location: 05-rq-evidence.tex:45.
   - Text: "in three the paper's full (joint) model is better on most units and in two it is worse".
   - Source: the script's sign is anchor against comparison (rq_analysis.py direction(); anchor from U3), and the anchor is not always the joint arm:
     - M15992 Table S7: the anchor is "Main-table model" and the comparison is "Multi-task model". "+" means the multi-task (joint) variant is worse.
     - M19293 Table 7: the anchor is "Generation-based (P+G)" and the comparison is "Generation-language (P+G+L)". "-" means the fuller joint model is better.
     - M18816 Table 31: the anchor is "Couple" (decoupled) in G12 and "Blend" (shared) in G13, both mostly "+". Decoupled wins for LaTtE-Flow and shared wins for Vanilla.
     - M13884: joint model against a cascade, "+".
     - M03633: full model worse, "-".
   - Read by arm, the tally is: the joint or shared arm is better in 2 studies (M13884, M19293), worse in 2 (M15992, M03633), and split in 1 (M18816).
   - Fix: restate as "two favour the joint or shared arm, two the reduced or decoupled arm, and one splits by model". Better still, orient RQ5 signs by a joint-arm flag in the script rather than by the anchor. The verdict wording "point both ways" survives.

3. **Agreement counts are F1 numerators, not counts of matched items.**
   - Locations: 02-method.tex:121, 10-limitations.tex:13, tables/extraction-agreement.tex:13-15, scripts/agreement_table.py:38 (column header "Agreed / compared"), supplement.tex:228 (caption "matched over the union"), and the per-record table columns.
   - Text: "48 of 52 headline numbers ... 72 of 245 groups and 300 of 1,227 units found by both"; in the limitations, "72 of 245 groups found by both".
   - Source: agreement.py:636 stores the F1 metric as [2 x matched, n_A + n_B]. The matched counts are therefore:

     | Measure | Matched | Listed by A and B together | Distinct (union) | F1 |
     |---|---|---|---|---|
     | Groups | 36 | 245 | 209 | 0.29 |
     | Units | 150 | 1,227 | 1,077 | 0.24 |
     | Headline units | 24 | 52 | 28 | 0.92 |

     The 36 matched groups are confirmed by M-class 23/36 and M-anchorG 34/36. Per record, for example, M08783 "10/13" is 5 matched of 13 listed (5 of 8 in the union), not "matched over the union".
   - Fix: report "36 groups found by both of the 245 the two extractors listed (F1 0.29)", and likewise for units (150) and headline units (24). In agreement_table.py, print "2 x matched / listed" or the matched count and F1 explicitly. Correct the S4 caption.

4. **The Method's stratum sizes differ from the weights, and stratum re-membership is not disclosed.**
   - Location: 02-method.tex:115, compared with 05-rq-evidence.tex:19.
   - Text: "unified multimodal studies (I1(b), 53), ... a shorter (272) and a longer (271) stratum ... Twelve records ... are left out of these strata". Section 5 then says "a stratum of 20 that stands for 52 unified studies".
   - Source: gate-manifest sizes are 53/272/271, taken before the stage-a exclusion and before D0059. rq_analysis.py recomputes membership with the D0059 field resolutions:
     - G-mm grows from 53 to 55 (M12859 and U04330 move in);
     - G-short falls from 272 to 271 (U04330 moves out);
     - G-long falls from 271 to 270 (M12859 and M18059 out, M11389 in).
     It then drops the stage-a ids (3/4/5), giving N_h = 52/267/265 (rq-results.json N_by_stratum).
   - Fix: state the weights used (52, 267, 265 and about 1,074), say that the 12 stage-a records are inside the 53/272/271, and say that D0059 moved three records between strata and one (M18059) out of the frame. Also write "I1(b) or both" for the unified stratum (see finding 22).

### Moderate

5. **The scope sentence contradicts the seed stratum.**
   - Location: 05-rq-evidence.tex:7.
   - Text: "Every count describes the included studies, which lean towards recent work and leave out the seed corpus".
   - Source: the sample-based statements include a seed stratum of 20 that carries 1,073.8 of the frame weight of 1,657.8 (0.65) (rq-results.json N_frame).
   - Fix: limit the sentence to the 615-study counts, and say that the sample shares cover the 584 update-stratum studies plus an estimated 1,074 eligible seed studies.

6. **"No verdict changes" rests partly on estimates the S6 table does not contain.**
   - Location: 05-rq-evidence.tex:21.
   - Text: "No verdict changes when the estimates are recomputed without the seed stratum, without the 27 records ..., or with the second extractor's records".
   - Source: the sensitivity block has 12 rows. None of them covers the RQ2 or RQ3 direction, the RQ4 study-level direction, RQ5, or the QA items.
   - Auditor recompute: RQ2 better/worse is 12/22 0.45 against 8/22 0.46 without the seed stratum, and 11/21 0.39 against 8/21 0.57 without rejected records, so it stays split. RQ3 anchor-better is 18/24 0.79, 13/18 0.71 and 18/26 0.66 in the three variants, so it is stable. RQ4 majority-up is 9/15 0.61 without the seed stratum, 4/9 0.43 without rejected records and 10/18 0.48 with extractor B.
   - Fix: add these rows, and QA4, QA5 and QA9 at score 2, to the HEAD set in rq_analysis.py and to the S6 table, or narrow the sentence to the estimates the table contains.

7. **The QA1 link check is misdescribed.**
   - Locations: 05-rq-evidence.tex:50 and 02-method.tex:122 (src comment).
   - Text: "17 of the 19 code links the extractors found resolved".
   - Source: qa1-links.jsonl has 19 rows: d = "yes" for 17 and "no-url" for 2 (M03633 and R0188, where no own-code URL is printed). No link failed.
   - Fix: "of the 19 studies that say code is released, 17 print an own-code URL that resolved on 2026-10-21 and 2 print none".

8. **"Proposed recipe" overstates what the anchor is.**
   - Location: 05-rq-evidence.tex:33. The same reading appears in 11-conclusion.tex:7 ("point the proposers' way").
   - Text: "The proposed recipe is better on most of its units in 20 of the 27 studies".
   - Source: the RQ3 sign is anchor against the rest. Of the 140 signed training groups, 43 take their anchor by the "first-own-arm" rule (98 of 418 units), and 4 studies have signed training contrasts only through such anchors (auditor recompute).
   - Fix: "the paper's anchor configuration (its focal or default setting; the first own arm where neither is stated)". Alternatively, report the estimate restricted to focal-label, stated-default and value-identity anchors.

9. **The abstract claim-type fields are reported without their reliability caveat.**
   - Locations: 05-rq-evidence.tex:28 (CT6, 10/79) and :45 (CT5, 3/20), compared with the departure at 02-method.tex:171.
   - Source: CT1-CT6 come from step 1 of the claim-evaluability rubric (evaluability-rubric.md:22-27). In the reliability round CT5 had kappa 0.00 and was flagged for a pilot (EXTRACTION-PLAN.md:91, OQ-03); that pilot was not run (D0051). Departure 7 says "nothing from [the extension] is reported".
   - Fix: say in Section 2 that the abstract claim types are kept descriptively, that CT5 failed reliability in the earlier round, and that the RQ5 claim count therefore carries that caveat. Reconcile this with departure 7.

10. **The RQ2 matched-budget statement omits the studies that match at least once.**
    - Location: 05-rq-evidence.tex:27 and :29.
    - Text: "None of the 35 matches the compute budget ... in every such comparison"; the verdict says "untested at matched budget".
    - Source (auditor recompute): 3 of 35 studies have at least one diffusion-autoregressive comparison at a matched budget (weighted 0.16 [0.05, 0.41]), 6 of 133 such groups. Of all groups, 99 have the budget "not reported", 28 "reported" and 6 "matched".
    - Fix: add "three match it in at least one comparison (6 of 133 comparisons)". The verdict "almost never at a stated common budget" then follows. "Untested" should read "essentially untested".

11. **The RQ5 verdict "untested" does not fit the stated definition, and its last sentence repeats itself.**
    - Location: 05-rq-evidence.tex:46.
    - Source: "untested" is defined as "when almost no study makes the comparison", but 8 of 20 unified studies contain a synergy ablation and 5 give signed units. The repeated clause is "measured on no purpose-built benchmark ... and no sampled study measures it on a benchmark designed for it".
    - Fix: "untested on a purpose-built benchmark; mixed in the five signed ablations", or extend the definition. Delete the repeated clause.

### Minor

12. 05-rq-evidence.tex:23. "28 only through an implicit channel" is wrong: revision is multi-valued, and 24 records are implicit-channel only (1 also has explicit remasking and a corrector, 3 also "other"). Fix: "24 only through an implicit channel".
13. 05-rq-evidence.tex:50. The QA figures are the low reading, but the text does not say so. The high reading differs for QA2 (0.18 [0.09, 0.33]) and QA7 (0.67 [0.52, 0.79]). Fix: add "(low reading; Table ...)".
14. 05-rq-evidence.tex:28. The section promises weighted shares beside counts, but the RQ2 direction gives counts only. Source: better 0.34 [0.16, 0.58], worse 0.56 [0.33, 0.77]. Fix: add both. "Split" still holds, since the intervals overlap.
15. 05-rq-evidence.tex:28. "matches or beats" is narrower than CT6 as defined: "matches, approaches, is competitive with or outperforms" (evaluability-rubric.md:27). Fix: "matches, approaches or beats".
16. 05-rq-evidence.tex:41. "the census shows that the setting behind a headline number is often not stated": the census codes the value rule, not the step count or parallelism. Fix: "the value rule behind a headline number".
17. 05-rq-evidence.tex:40. "14 move both ways": the "other" shape also includes flat curves (monotone() returns "other" for all-equal values). Fix: "14 are flat or move both ways".
18. 05-rq-evidence.tex:52. The RQ6 verdict ("reproducible in part and statistically weak") is not one of the four defined verdicts, yet 02-method.tex:125 says each RQ gets one of them. Fix: state that RQ6 is described rather than graded, or map it to a defined verdict.
19. 01-introduction.tex:43. "The census ... adds an independent random sample of the seed corpus" is inaccurate: the extraction's seed stratum is drawn from the census sample (seed-sample.json), so the two are not independent. Fix: drop "independent", or say "a random sample of the seed corpus, from which the extraction's seed stratum is drawn".
20. 11-conclusion.tex:9 (src). runs/EXP-003/analysis/confirmatory.json does not exist in this worktree; it is only in .claude/worktrees/dlm-discovery-resume-ca3357. The numbers match that file. Fix: bring the file into this worktree, or point the src at the archived copy.
21. main.tex:75. The census count "147 of 153" has no \aud tag in the compiled abstract, but the abstract's own comment (main.tex:69) and the conclusion (11:5) keep the tag until the census is re-verified. Fix: add \aud, or remove it everywhere once the census audit closes.
22. 02-method.tex:115 and 05-rq-evidence.tex:12. Two eligibility-basis labels are inexact. The unified stratum is labelled "I1(b)" but includes I1(a)-and-(b) records. The "557 ... (criterion I1(a))" category is I1(a) only, exclusive of the 17 "both". Fix: write "I1(b) or both" and "I1(a) only".

## Method of this audit
- Read-only. Scripts were copied to the session scratchpad with their output paths redirected and run with `python -I`, and their outputs were compared with diff. `git status` shows no changes to tracked files.
- No GPU and no downloads were used. No ledger rows were added, and progress.md was not edited, because the brief makes the worktree read-only except for this report. The orchestrator should untick or leave unticked the Section 5 gate in research/progress.md.
- Not consulted: research/review/audits/2026-10-21-redteam-section5.md (untracked; not read, to keep this verdict independent).

## State audited (concurrency note)
- This audit covers rq_analysis.py as committed (HEAD 8f71757; the scratch copy was taken at 05:54 and has no
  D0060 block) and rq-results.json written at 05:48. A fresh run of that script reproduces rq-results.json exactly.
- During the audit, another session changed the working tree: rq_analysis.py at 06:03 (adds a "D0060" block: update
  strata as the primary estimand, bootstrap intervals, verdict thresholds) and research/ledgers/decisions.jsonl
  (D0060, 06:01). Neither change had been rerun into rq-results.json or into Section 5 by the time of this audit.
- Once D0060 is applied, every Section 5 share and interval will change. This verdict and these findings apply to the
  text as it stands, and the re-audit must run against the new rq-results.json. Findings 1 to 4, 7, 8, 12 and 22 do
  not depend on the estimand, so they still need fixing.
