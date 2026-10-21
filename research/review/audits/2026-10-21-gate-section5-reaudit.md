```yaml
agent: gate-auditor
date: 2026-10-21
brief: Re-audit of Section 5 (RQ evidence) and the related text after decision D0060 (commits acdad99..45032b7), against the gate audit and the red-team audit of 2026-10-21 (Paper 1, PRISMA review, ACM CSUR)
sources_examined:
  - research/review/audits/2026-10-21-gate-section5.md (22 findings); research/review/audits/2026-10-21-redteam-section5.md (1 fatal, 8 major, 7 minor)
  - research/ledgers/decisions.jsonl row D0060
  - analysis/extraction/d0052/rq_analysis.py (block "D0060", lines 465-704), rq-results.json key "D0060", rq-results.md, qa-table.jsonl, rq5-orientation.jsonl
  - analysis/extraction/d0052/agreement-8-texts/agreement-stage-a.json; EA/*, EC/* records (arm labels of the RQ5 synergy groups only)
  - paper/review/scripts/qa_tables.py, agreement_table.py; paper/review/tables/{qa-summary,qa-per-study,sensitivity,extraction-agreement,extraction-agreement-records}.tex
  - paper/review/sections/05-rq-evidence.tex (all), 02-method.tex 112-125, 159, 166-176; 10-limitations.tex 8, 13; 01-introduction.tex 43-46; 11-conclusion.tex 5-9; main.tex 68-76; supplement.tex 74, 215-233, 266-281
  - runs/EXP-003/analysis/confirmatory.json (now in this worktree); research/AUTHOR-CHECKS-2026-10-21.md
coverage: >
  Every finding of both audits was re-checked against the current files. Every number in the revised Section 5 and in the
  revised sentences of Sections 1, 2, 10, 11, the abstract and supplement S4/S6 was traced to rq-results.json D0060 or the
  file named in its src comment. Not covered: the rest of Section 2, Sections 3-4 and 6-9, citations, the PDF build, the
  RQ1 counts over 615 (unchanged since the gate audit, which verified them), and the 153-field count of the form.
claims:
  - statement: rq-results.json, rq-results.md and qa-table.jsonl are byte-identical to a fresh run of rq_analysis.py
    status: supported
    evidence: scratch copy with output paths redirected, run 2026-10-21; cmp equal for all three
    level: E4
    confidence: 0.99
  - statement: The five generated tables are byte-identical to what qa_tables.py and agreement_table.py write now
    status: supported
    evidence: scratch copies with OUT redirected; cmp equal for all five
    level: E4
    confidence: 0.99
  - statement: Each RQ2-RQ5 verdict in Section 5 follows mechanically from the D0060 thresholds applied to the included column
    status: supported
    evidence: rq-results.json D0060.verdicts.included; recomputed by hand from D0060.included (section "Verdict check")
    level: E4
    confidence: 0.97
  - statement: Every number in the revised Section 5 equals its source after rounding
    status: supported
    evidence: section "Number reconciliation"
    level: E4
    confidence: 0.95
  - statement: The reported agreement on "the study-level flags the verdicts use" (55 of 62) describes the reliability of the verdict inputs
    status: contradicted
    evidence: D0060.agreement_extra.study_level_flags; RQ3_anchor_better_majority agrees 0 of 2, RQ4_sweep_up_majority 2 of 3; 9 of the 14 flags are not verdict inputs (finding N1)
    level: E4
    confidence: 0.9
competing_explanations: []
unknowns:
  - Whether the 12 author checks (research/AUTHOR-CHECKS-2026-10-21.md, part 1) change QA1 or other per-study scores; the blind human check (part 2) has not been filled in.
next_test: {hypothesis: "RQ3 direction is reproducible across extractors", intervention: "report the RQ2-RQ4 direction-flag agreement separately (5 of 8 pairs; RQ3 0 of 2) and add the blind human check results when the user returns the sheet", primary_metric: "agreement on direction flags, with n", falsifier: "human-model agreement on Q3/Q4 below 0.7", gpu_hours: 0}
```

# Gate re-audit: Section 5 (RQ evidence) after D0060, 2026-10-21

## Verdict: PASS WITH FIXES

The revision answers the substance of both audits. The included studies are now the primary population and the seed
stratum sits in its own column. Intervals come from a stratified bootstrap with an exact bound for zero cells. The
verdict thresholds are stated once, and the code applies them exactly as stated. RQ4 and RQ5 are restated as "mixed",
the RQ5 signs are oriented by arm, unit totals are gone and agreement is reported as matched counts. All analysis
outputs and all five tables regenerate byte-identically. Every number in the revised Section 5 equals its source.

Of the 38 earlier findings, 29 are fixed or no longer apply, 6 are partly fixed and 3 are not fixed. The revision
brings in 8 new problems (N1, N3-N6, N8-N10; N2 and N7 restate residuals of M4 and M8). All are text fixes except M6, which needs the user. Open findings by severity:

- **Major: 1.** Red-team M6. The blind human check is prepared but not yet done, and prompts and raw outputs are not
  released. This is a submission-level item, not a Section 5 text item, and only the user can close it.
- **Moderate: 1.** N1: the pooled flag agreement hides that the RQ3 direction flag agrees in 0 of 2 pairs.
- **Minor: 15.**

No gate criterion is `missing`. Criterion 4 is `partly`, because of N1 and minors N2 to N8.

The Section 5 gate can be ticked once N1 and the text minors below are applied. Those fixes can be checked by diff and
need no new analysis. M6 must stay open on the submission gate. This re-audit does not waive it.

## Criterion status

| Criterion | Status | Evidence |
|---|---|---|
| (1) Generated tables and analysis outputs equal current script output | met | Scratch rerun of rq_analysis.py (numpy needed, so run without -I from the scratchpad): rq-results.json, rq-results.md and qa-table.jsonl identical. qa_tables.py and agreement_table.py: all five .tex identical |
| (2) Strata, weights and frame consistent across sections | met | 02-method.tex:115 now gives 53/272/271 → 52/267/265 (584), 59 sampled, M18059 out. This matches 05:19 and D0060.N_by_stratum |
| (3) Each verdict follows from its numbers under the stated thresholds | met | See "Verdict check" |
| (4) No claim exceeds its evidence | partly | N1 (moderate); N2 to N8 and residuals of G8, M7, M8 (minor) |

## Verdict check (task 3)

Thresholds (05-rq-evidence.tex:21 = D0060 = rq_analysis.py verdict(), lines 638-662) are:
- **untested:** fewer than 5 studies with a signed direction;
- **mixed:** the larger directional share is below 2/3;
- **weakly supported:** the larger share is at least 2/3 and the control share is below 0.5;
- **well supported:** otherwise.

Inputs below are from the included column.

| RQ | n signed | Larger directional share | Control share | Mechanical verdict | Text | Match |
|---|---|---|---|---|---|---|
| RQ2 | 22 | worse 0.461 (better 0.452) | 0.06 | mixed | 05:29 mixed | yes |
| RQ3 | 24 | anchor better 0.789 | 0.118 | weakly supported | 05:35 weakly supported | yes |
| RQ4 | 15 (sweeps) | up-majority 0.609 (down 0.09) | 0.076 | mixed | 05:41 mixed | yes |
| RQ5 | 5 | joint worse 0.60 (better 0.40) | 0.0 | mixed | 05:47 mixed | yes |

Sensitivity claim at 05:21: without rejected records the verdicts are M/W/M/U, with RQ5 at 4 signed studies; with
extractor B's records they are M/W/M/M. This matches D0060.verdicts and the last row of tables/sensitivity.tex.

Two notes do not change any verdict:
- RQ3 sits above 2/3 only at the point estimate (interval 0.59 to 0.95).
- RQ5 is exactly at the n = 5 boundary. The text discloses this.

The code's control flag ("any group reports a budget AND any group reports variation") is looser than the wording
"report both its budget and its run-to-run variation". No verdict depends on it, since no control share is near 0.5.

## Status of earlier findings (task 1)

### Gate audit (2026-10-21-gate-section5.md)

| # | Sev. | Status | Where |
|---|---|---|---|
| 1 RQ4 verdict and direction rest on unit totals | major | fixed | 05:40-41 (study level: 9/15 majority-up, 5/15 all-up, verdict mixed); 11:7; main.tex:75 |
| 2 RQ5 sign convention | major | fixed | rq5-orientation.jsonl, rq_analysis.py:506-518. The auditor checked all 11 orientation rows against the arm labels in the EA/EC records and found them consistent. Text at 05:45 |
| 3 F1 numerators described as matched counts | major | fixed | 02:121, 05:20, 10:13, S4 prose at supplement.tex:218, per-record caption at :228, tables/extraction-agreement.tex (36/245/209; 150/1227/1077; 24/52/28). Per-record matched sums reproduce 36 and 150 |
| 4 Method stratum sizes differ from weights | major | fixed | 02:115 |
| 5 Scope sentence contradicts seed stratum | moderate | fixed | 05:7 (residual at 10:8, see N4) |
| 6 "No verdict changes" not backed by S6 | moderate | fixed | tables/sensitivity.tex now has the direction rows, QA1-QA9 and a verdict row; 05:21 |
| 7 QA1 link check misdescribed | moderate | fixed | 05:51, 02:122 |
| 8 "Proposed recipe" overstates the anchor | moderate | partly fixed | 05:33 fixed (anchor defined). 05:35 ("the configurations the papers put forward") and 11:7 ("Training choices the papers put forward") remain. The auditor's restricted estimate without first-own-arm anchors is 15/20 (0.77 [0.53, 0.96]), so the direction holds and this is wording only. Now minor |
| 9 Claim-type reliability caveat | moderate | fixed | 05:46, 02:125, 02:171 (departure 7 reconciled) |
| 10 RQ2 matched-at-least-once omitted | moderate | fixed | 05:27 (1/25, 0.06 [0.00, 0.20]); 05:29; 11:7 "almost untested" |
| 11 RQ5 "untested" vs definition; repeated clause | moderate | fixed | 05:47 (mixed under the thresholds); clause removed |
| 12 "28 only through an implicit channel" | minor | no longer applies | sentence removed; 05:23 rewritten on the included column |
| 13 QA reading not named | minor | fixed | 05:51 ("score 2 on the low reading"; QA7 high 0.46) |
| 14 RQ2 weighted direction shares missing | minor | fixed | 05:28 |
| 15 "matches or beats" | minor | fixed | 05:28 |
| 16 "setting behind a headline number" | minor | fixed | 05:41 ("value rule") |
| 17 "move both ways" includes flat curves | minor | no longer applies | monotone() still files flat curves as "other" (rq_analysis.py:302-305). The only flat curve in the included sweeps (M14293 G51) is in a study that also has a peaked curve, so the study-level statement at 05:40 holds. The same 7 studies are flagged with the 1 % tolerance |
| 18 RQ6 verdict outside the four | minor | fixed | 05:21, 02:125, 01:43 |
| 19 "independent" census sample | minor | fixed | 01:43 |
| 20 confirmatory.json not in worktree | minor | fixed | runs/EXP-003/analysis/confirmatory.json present. G 0.1797, P64 0.0505, delta1 0.1256 [0.0758, 0.1768] match 11:9 and main.tex:75 |
| 21 \aud missing on abstract census count | minor | not fixed | main.tex:75 "147 of 153" still has no \aud, while 11:5 keeps it |
| 22 Eligibility-basis labels | minor | fixed | 02:115 ("I1(b) or both", "I1(a)-only"); 05:12 reads exclusively with "and 17 through both"; 05:14 |

### Red-team audit (2026-10-21-redteam-section5.md)

| # | Sev. | Status | Where |
|---|---|---|---|
| F1 Population misstated; seed dominates | fatal | fixed | 05:7, 05:19, 02:115, 10:13, 01:43, main.tex:75. Included column primary, seed apart, combined only in S6 (residual at 10:8, see N4) |
| M1 RQ2 matched-budget contradicted; zero-cell interval | major | fixed | 05:27 (matched_any 1/25; exact bound on Kish n 18.6 gives 0.18, rq_analysis.py:610-614); 05:29 |
| M2 RQ4 verdict violates own rules | major | fixed | 05:40-41 (study-level; 1 % tolerance row; "stops improving" reworded) |
| M3 Verdicts post hoc, no thresholds, inconsistently applied | major | fixed | 05:21 thresholds, labelled post hoc (also 02:173); applied mechanically (verified above); RQ1/RQ6 ungraded; S6 carries the direction and QA rows |
| M4 Extraction reliability overstated | major | partly fixed | Factor type 23/36, claim status kappa 0.44, QA items 65/72 and flags 55/62 are now in 05:20, 02:121, 10:13 and the S4 table. But the pooled flag figure hides the verdict-driving direction flags (N1), and 616/616 comes from 4 of the 8 studies, which 05:20 and 02:121 do not say (N2) |
| M5 Interval method | major | partly fixed | Stratified percentile bootstrap, exact Kish bound for zero/full cells, and disclosure as chosen after extraction (02:115, 02:175). Residual (minor): Kish n is not reported beside the domains (it is only in rq-results.json D0060.kish_n_included). Percentile lower limits of 0.00 for non-zero counts (05:27 1/25 [0.00, 0.20], 3/25 [0.00, 0.37]; 05:34 3/27 [0.00, 0.26]) are not attainable values and come from domains of 3-10 studies per stratum. There is no finite-population correction for G-mm (20 of 52) |
| M6 AI-only screening/extraction validity | major | partly fixed | Wording fixed (02:159, main.tex:75 "no screening or extraction decision was made independently by a human"). The blind 12-study human check is prepared (research/HUMAN-CHECK-2026-10-21.xlsx; AUTHOR-CHECKS part 2) but not filled in. Prompts and raw outputs are still a todo (supplement.tex:74). Open; needs the user |
| M7 Cross-section inconsistencies | major | partly fixed | QA7 0.26 vs RQ3 0.28 now agree; RQ2 weighted shares given; unit totals dropped; abstract sample wording fixed. Residual (minor): QA6 "budgets of both arms" 0.40 (05:51) next to RQ2 "a budget not reported" 0.93 (05:27) is not reconciled (different constructs, but no sentence says so) |
| M8 RQ5 generalisation | major | partly fixed | 05:45 scoped to the 20 sampled, with an upper bound of 0.17 for the 52. Residual (minor): 11:7 "no study uses a benchmark built for the question" is unscoped. The 32 screener RQ5 tags (05:15) against 8/20 ablations are not reconciled |
| m1 "copied" overclaims | minor | fixed | 05:27 "state that they copied" |
| m2 Best-vs-best direction uninterpretable | minor | fixed | 05:28 |
| m3 Seed records outside the census pool | minor | fixed | 10:13 |
| m4 Promised protocol outputs missing | minor | fixed | 02:175 |
| m5 Intro feasibility numbers from another sample | minor | not fixed | 01:45-46 unchanged ("A feasibility pass over sampled papers ...") |
| m6 Pending author-check items | minor | not fixed | 02:122 says the reported values are the adjudicator's, but nothing names which numbers could change. AUTHOR-CHECKS items 1-9 touch QA scores and QA1 |
| m7 Census replication not independent | minor | no longer applies | Not reported anywhere in Section 5 or the supplement (grep) |

## Number reconciliation (task 2)

All sources are rq-results.json D0060.included unless named otherwise. "=" means equal after rounding.

| Location | Numbers in text | Source | Status |
|---|---|---|---|
| 05:19 | 59; 584; 19/20/20; 265, 267, 52; B 4,000 | n_primary 59, N_primary 584, n_by_stratum, N_by_stratum, bootstrap | = |
| 05:20 | 616/616, 75/76; 65/72; 55/62; 245, 36, F1 0.29; 23/36 | agreement-stage-a.json M-val, M-sign, F1_G 72/245; agreement_extra | = (see N1, N2) |
| 05:23 | 27/59 0.59 [0.45, 0.73]; 17, 13; 9, 5, 22, 9; 12 0.24 [0.12, 0.38]; 16; 25, 5; 11 0.24 [0.12, 0.38] | RQ1_* rows (continuous-latent G-mm 13/20) | = |
| 05:27 | 25 0.40 [0.26, 0.54]; 1 0.06 [0.00, 0.20]; 0, 0.18; 23 0.93 [0.79, 1.00]; 5 0.20 [0.03, 0.40]; 3 0.18 [0.00, 0.37] | RQ2_has_ar, matched_any, matched_all, budget_not_reported_any, copied_stated_any, variance_any | = (the matched study is M12879) |
| 05:28 | 22; 12, 8; 0.45 [0.21, 0.71], 0.46 [0.21, 0.71]; 7/59 0.15 [0.05, 0.26]; seed 10/20, 6/10 | RQ2_signed, better/worse_majority, abstract_claim; seed column | = |
| 05:33 | 27 0.44 [0.31, 0.58]; 18/24 0.79 [0.59, 0.95]; 3 | RQ3_has_training, anchor_better/worse_majority | = |
| 05:34 | 3 0.11 [0.00, 0.26]; 7 0.28 [0.10, 0.49]; 4 0.17 [0.01, 0.35]; 3 0.12 | RQ3_held_fixed_all, credited_ablation_any, variance_any, control | = |
| 05:39 | 31 0.65 [0.53, 0.78]; 14, 9, 7; 24 0.81 [0.66, 0.94]; 8 0.29 [0.14, 0.46] | RQ4_has_inference; R.RQ4.by_factor update strata summed (steps 8+2+4, guidance 4+2+3, tokens/step 4+1+2); budget_reported_any; variance_any | = |
| 05:40 | 15; 9 0.61 [0.34, 0.87]; 5 0.37 [0.12, 0.64]; 7 0.47 [0.20, 0.72]; 7 of 13; two studies supply most curves | RQ4_has_sweep, sweep_up_majority, sweep_all_up, any_nonmonotone, tol1pct; sweep_curves_by_study M15781 62 + M17249 60 of 170 | = (same 7 studies under the tolerance) |
| 05:41 | 0.61 | as above | = |
| 05:45 | 20 of 52; 3; 0, bound 0.17; 8; 2 of 3; 5; 2 and 3 | RQ5_claim, benchmark (Kish n 20 gives 0.168), has_ablation; R.RQ5.claim_and_group 2; RQ5_signed, joint_better/worse_majority | = |
| 05:51 | QA1 9/59 0.17 [0.07, 0.29]; 19, 17, 2; QA2 1, 0.02 [0.00, 0.07]; QA4 10/54 0.20 [0.09, 0.33]; QA5 9 0.22 [0.10, 0.35]; QA6 0.40 [0.25, 0.55]; QA7 0.26 [0.14, 0.41], high 0.46; QA9 0.60 [0.46, 0.74]; seed 0.40, 0.67, 0.05 | QA*_low_eq2 / high_eq2; qa1-links.jsonl | = |
| 05:52 | 260; 64, 84, 49, 51, 12; 7/54 0.14 [0.04, 0.26]; seed 0/20; kappa 0.44, 33 | R.RQ6.claims_status (79 studies, both columns); claims_any_unsupported; agreement_extra.claim_status | = (see N5) |
| 02:115 | 53, 272, 271; 12; 7; 52, 267, 265; 584; 59; 4,000; 1,106, 167, 1,074 | gate-manifest; N_by_stratum; seed-sample.json | = |
| 02:121 | 616/616; 75/76; 65/72; 55/62; 36 of 245, F1 0.29; 150 of 1,227, F1 0.24; 24 of 28, F1 0.92; kappa 0.44 | agreement-stage-a.json; agreement_extra | = (see N2, N3) |
| 02:122 | 19, 17, 2 | qa1-links.jsonl | = |
| 10:13 | 36 of 245, F1 0.29, 0.6; kappa 0.44; 62 flags, 8 studies; 27; 1,106 | as above; sensitivity.rejected_at_final_pass 27 | = |
| 11:7 | 25 of 59; one; 9 of 15; 7; five, two, three; 10 of 54; 9 | D0060.included | = (see N6, N7) |
| 11:9 | 0.180, 0.051, 0.126 | confirmatory.json arms.G.lambda_b, arms.P64.lambda_b, confirmatory.delta1.d | = |
| main.tex:75 | 615; 59; 20; 25; one; 9 of 15; five, two, three; 10 of 54; 147 of 153; 0.126 [0.076, 0.177] | as above; delta1.pct95 | = (see N6; G21) |
| 01:43 | 615; 47; 59; 20 | as above | = |
| Tables | qa-summary.tex; sensitivity.tex; extraction-agreement(.records).tex | D0060; agreement-stage-a.json | = (regenerated, byte-identical) |

## New problems introduced by the revision (task 4)

**N1 (moderate). The pooled flag agreement is labelled as the verdict inputs and hides the one that disagrees.**
- Locations: 05:20 ("55 of 62 of the study-level flags the verdicts use"), 02:121, 10:13, and the S4 table row "Study-level flags behind the verdicts (14 flags)".
- Source: rq_analysis.py:672-679 and D0060.agreement_extra.study_level_flags.
- Of the 14 flags, 9 are domain or descriptive flags that the verdict rule never reads: has_ar, matched_any, budget_not_reported_any, has_training, held_fixed_all, has_inference, budget_reported_any, variance_any, claims_any_unsupported. Four of these agree 8 of 8 or 5 of 5 and carry the pooled share.
- The verdict rule reads the direction flags, the control flags and the RQ5 joint flags:
  - direction flags agree in 5 of 8 pairs: RQ2 better 3/3, **RQ3 anchor-better 0/2**, RQ4 up-majority 2/3;
  - control flags (auditor recompute) agree RQ2 3/3, RQ3 1/2, RQ4 sweep 2/3;
  - the RQ5 joint flags have no double-read pair.
- The RQ3 verdict is robust to swapping in extractor B (17/24, 0.73, still W). The S6 table shows that. The reliability sentence still reads as stronger than the evidence.
- Fix: relabel the row as "study-level flags (14, of which 3 direction flags)". In 05:20 and 02:121, add "the direction flags behind the RQ2-RQ4 verdicts agree in 5 of 8 pairs (RQ3: 0 of 2)".

**N2 (minor). The value agreement is attributed to all eight studies.**
- Location: 05:20 ("On the eight studies ... the values (616 of 616)") and 02:121.
- Source: M-val uses 4 records (agreement-stage-a.json records_used 4). S4 at supplement.tex:218 says so, but the main text does not.
- Fix: add "(from the 4 studies where both found units with values)".

**N3 (minor). Mixed denominators in one sentence.**
- Location: 02:121. Groups and units are given against the sum of the two lists ("36 of 245", "150 of 1,227"), but headline numbers are given against the union ("24 of 28"). 05:20 and 10:13 use the sum.
- Fix: use one basis, for example "36 groups found by both, of 209 distinct" (and 1,077 for units), or "24 of the 52 listed" for headline numbers. The S4 table already shows both.

**N4 (minor). The limitations still say every count describes the included studies.**
- Location: 10:8 ("Every count in Section~\ref{sec:rq} describes the included studies, not the field").
- Section 5 now reports seed-column numbers: 05:28 (10/20, 6/10), 05:51 (0.40, 0.67, 0.05) and 05:52 (0/20).
- Fix: "Every count in Section 5 describes the included studies or, where labelled, the seed corpus; none describes the field."

**N5 (minor). The claim totals are pooled over both columns and are unit totals.**
- Location: 05:52 ("Of 260 claims ... 64 ... 12"). R.RQ6.claims_status counts claims over all 79 in-frame studies, included and seed together, unweighted.
- This conflicts with D0060 ("seed a separate column") and with 05:20 ("Unit totals are therefore not used"). The paragraph does call the counts indicative.
- Fix: give them for the 59 included studies (seed apart), or say "pooled over both columns, unweighted".

**N6 (minor). The abstract and conclusion drop "in at least one comparison".**
- Locations: main.tex:75 ("one of them at a matched compute budget") and 11:7 ("one of them at a matched budget").
- M12879 matches the budget in some of its AR comparisons, not all (05:27 says this correctly).
- Fix: "one of them, in at least one comparison, at a matched budget".

**N7 (minor). The conclusion generalises the benchmark finding.**
- Location: 11:7 ("no study uses a benchmark built for the question"). This is the residual of M8.
- Fix: "none of the 20 sampled unified studies".

**N8 (minor). The rejected-record count is not that of the included column.**
- Location: 05:21 ("when the 27 records the validator still rejected are left out").
- 22 of the 27 are in the included column (59 → 37), and 5 are seed records.
- Fix: "the 22 included records ...", or "the rejected records (22 of the 59)".

**N9 (minor). The S4 caption describes a column the table no longer has.**
- Location: supplement.tex:220. The caption explains "Lower bound: the 5th percentile of a bootstrap ...", but the regenerated tables/extraction-agreement.tex has no lower-bound column. The commit removed it.
- The S6 sensitivity table (supplement.tex:278-280) also lost its \caption and \label. It is now a bare longtable, which gives no table number for the "Supplement S6" references.
- Fix: rewrite the S4 caption; give S6 a caption and label.

**N10 (minor). M18816 splits by base model.**
- Location: 05:45 counts M18816 as "joint worse" on 5 of 8 pooled units.
- By base model, decoupled wins for LaTtE-Flow (G12, G16) and shared wins for Vanilla (G13, G17).
- The verdict is "mixed" either way: 2/5 or 2/4 with a split study. One clause would prevent a referee from reading 2-to-3 as a lean.
- Fix: "(one of the three splits by base model)".

Residual minors carried from the earlier audits are not repeated here: G8, G21, M5, M7, M8 in its Section 5 part, m5 and m6. See the tables above.

## Open findings, summary

| Severity | Count | Items |
|---|---|---|
| Major | 1 | M6 (human check pending; prompts and raw outputs). Submission-level; needs the user |
| Moderate | 1 | N1 |
| Minor | 15 | G8 residual, G21, M4 residual (= N2), M5 residual, M7 residual, M8 residual (= N7), m5, m6, N3, N4, N5, N6, N8, N9, N10 |

## Method of this audit
- **Read-only.** rq_analysis.py, qa_tables.py and agreement_table.py were copied to the session scratchpad (`.../scratchpad/reaudit/scripts`). Their output paths were redirected to `.../scratchpad/reaudit/out`; ROOT still pointed at the worktree for inputs. Outputs were compared with cmp.
- **Diagnostics.** Two diagnostic copies (rq_diag.py, rq_diag2.py) appended read-only checks. These covered:
  - the shapes and flat curves per sweep study;
  - the nonmonotone sets with and without tolerance;
  - the RQ5 signs per study;
  - the RQ3 estimate without first-own-arm anchors;
  - QA-pair NA counts (1 NA-NA pair of 72);
  - the per-flag agreement for direction and control flags.
- **No changes to the worktree.** `git status` shows no change to tracked files; the untracked .codex file predates this audit. No GPU, no downloads, no ledger rows. progress.md was not edited, because the brief limits writes to this report. The orchestrator should tick the Section 5 gate only after N1 and the minor text fixes are applied, and keep M6 open on the submission gate.
