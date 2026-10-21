```yaml
agent: red-team
date: 2026-10-21
brief: Hostile-but-fair ACM CSUR referee / area-editor audit of Paper 1 Section 5 (RQ evidence), method, limitations, conclusion, abstract, intro, supplement S4/S6, and the D0052 extraction data behind them.
sources_examined:
  - paper/review/sections/05-rq-evidence.tex
  - paper/review/sections/02-method.tex
  - paper/review/sections/10-limitations.tex
  - paper/review/sections/11-conclusion.tex
  - paper/review/sections/01-introduction.tex
  - paper/review/main.tex (abstract, lines 68-76)
  - paper/review/supplement.tex (PRISMA checklist rows, S4 lines 215-232, S6 lines 267-283)
  - paper/review/tables/{extraction-agreement,extraction-agreement-records,sensitivity,qa-summary,qa-per-study}.tex
  - analysis/extraction/d0052/rq-results.md, rq_analysis.py, batch-log.jsonl, sample.json
  - analysis/extraction/d0052/agreement-8-texts/agreement-stage-a.json
  - analysis/extraction/agreement.py (M-class, QA kappa, M-CL code paths only)
  - research/review/protocol.md section 1 table and section 7
  - research/ledgers/decisions.jsonl rows D0052-D0055
  - research/debates/2026-10-20-2026-10-20-paper1-significance/round-02-codex.md
coverage: >
  Read in full: Section 5, Section 2, Section 10, Section 11, Section 1, abstract, rq-results.md, rq_analysis.py.
  Supplement: PRISMA checklist rows 9-22, S4, S6 and their input tables. Not read: Sections 3, 4, 6, 7, 8, 9 in
  full (grep only), census files, EXTRACTION-PLAN beyond a grep for estimator terms, individual EA/EB/EC records
  beyond what the probe scripts compute. Re-analysis was run on a copy of rq_analysis.py with all writes redirected
  to the session scratchpad (scripts: <scratchpad>/rt/rqa_copy.py, probe.py ... probe4.py, where <scratchpad> =
  C:/Users/Shlok/AppData/Local/Temp/claude/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-334706/0839c9f4-4e83-4067-9eb8-6394e5c875ef/scratchpad);
  no repository file other than this report was written. No ledger rows added (brief: read-only except report).
claims:
  - statement: "Section 5 says every count describes the included studies and leaves out the seed corpus, but the estimator puts 0.648 of the weight on the seed stratum (N_h 1073.8 of 1657.8)."
    status: supported
    evidence: 05-rq-evidence.tex line 7; rq_analysis.py N_h; probe.py output 'seed weight 0.6477'
    level: E4
    confidence: 0.97
  - statement: "Within the domains that drive RQ2-RQ4, the seed stratum carries 0.55-0.74 of the weight (AR 0.699, AR-signed 0.738, inference 0.693, training 0.554, sweep 0.539)."
    status: supported
    evidence: probe.py 'domain n by stratum ... seed weight in domain'
    level: E4
    confidence: 0.95
  - statement: "RQ6 headline shares are driven by the seed stratum: share at score 2 overall vs update strata only: QA1 0.32 vs 0.17, QA4 0.10 vs 0.20, QA5 0.10 vs 0.22, QA7 0.53 vs 0.26; unsupported-claim share 0.05 vs 0.14 (seed 0/20)."
    status: supported
    evidence: probe4.py output
    level: E4
    confidence: 0.95
  - statement: "RQ2 'untested at matched budget' is contradicted: 3 of 35 studies (weighted 0.16 [0.05, 0.41]) contain at least one diffusion-AR comparison coded 'matched' (6 groups: M12879 x3, R1319 x1, R0214 x2); the only signed matched units (R0214, 2) favour AR."
    status: supported
    evidence: probe.py 'matched_any'; probe3.py 'MATCHED' lines
    level: E4
    confidence: 0.9
  - statement: "The reported upper bound 0.10 for 0/35 matched-in-all is the unweighted Wilson bound for n=35; the design-based Kish effective n is 18.6, giving about 0.17."
    status: supported
    evidence: rq_analysis.py est() (neff = den when p in {0,1}); probe.py 'AR n 35 Kish neff 18.6 ... 0.171'
    level: E4
    confidence: 0.9
  - statement: "122 of the 181 RQ4 sweep curves come from two studies (M15781: 62, M17249: 60); at study level about 10 of 19 sweep studies are majority-up."
    status: supported
    evidence: probe.py 'sweep' lines
    level: E4
    confidence: 0.9
  - statement: "Inter-extractor agreement on QA item scores was never computed by agreement.py (G3 QA kappa null, 0 pairs per item); claim-status agreement is kappa 0.44 (33 pairs); factor type of matched groups 23/36; none of the last two is in the main text."
    status: supported
    evidence: agreement-stage-a.json metrics 'G3 QA kappa', diagnostics 'M-CL', metrics 'G4 M-class'
    level: E4
    confidence: 0.95
  - statement: "RQ2 weighted direction shares (diffusion better 0.34 [0.16, 0.58], worse 0.56 [0.33, 0.77]) are omitted from Section 5, although the section promises share beside count."
    status: supported
    evidence: rq-results.md RQ2; 05-rq-evidence.tex lines 19 and 28
    level: E4
    confidence: 0.95
  - statement: "No update-stratum record at positions 21-27 was extracted before D0054 dropped them (no post hoc truncation)."
    status: supported
    evidence: batch-log.jsonl sessions ending before 2026-10-20T19:29 cover only positions 1-20
    level: E4
    confidence: 0.9
competing_explanations:
  - "Seed-vs-update differences in QA and RQ shares are partly real (older, well-known papers release code and ablate more) and partly instrument (page-less HTML, census eligibility rules, worst extractor agreement); the design cannot separate the two."
  - "Non-monotone sweep curves (RQ4) are measurement noise: zero tolerance, 74% of inference studies report no variation, and studies with more curves are more likely to show at least one wiggle."
  - "RQ2 'mixed' direction is an artefact of comparing the best diffusion arm against the best AR arm with no size or budget matching, so direction counts mostly reflect which baselines authors chose."
unknowns:
  - "Whether any of the 12 pending author-check items (commit 8f71757) changes a reported number."
  - "Human agreement for any screening or extraction decision (none recorded)."
next_test: {hypothesis: "Section 5 verdicts survive when the update strata (the PRISMA-included set) are the primary estimate and the seed stratum is reported separately, with design-based intervals", intervention: "re-run rq_analysis with est_in(UPD) as primary, seed as a separate column, QA items and direction variables added to the sensitivity table, intervals by within-stratum bootstrap", primary_metric: "verdict per RQ under pre-stated thresholds", falsifier: "any RQ verdict changes category between combined and update-only estimates", gpu_hours: 0}
```

# Red-team audit: Section 5 (evidence by research question) and its supports

Note on brief vs. agent rule: the red-team definition forbids proposing fixes; the orchestrator's brief explicitly asks
for a concrete fix per finding and a cheapest credible fix. I follow the brief. Severities were assigned before any
fix was considered and are not softened by it.

Counts: **1 fatal, 8 major, 7 minor.**

## Most damaging objection (one sentence)

The RQ2-RQ6 answers are presented as describing the 615 included studies "which leave out the seed corpus", but the
estimator gives 65 % of the weight (55-74 % within the RQ2-RQ4 domains) to 20 seed papers that never passed the
review's own full-text screening, were read from page-less HTML under different eligibility rules, and have the worst
extractor agreement; several headline shares change by a factor of two or more without them.

---

## FATAL

### F1. The synthesised population is not the population the paper says it is; the seed stratum dominates every weighted share
- **Source facts.** 05-rq-evidence.tex line 7: "Every count describes the included studies, which ... leave out the
  seed corpus". 10-limitations.tex line 8: "Every count in Section 5 describes the included studies, not the field".
  Abstract: "615 studies are included, and a stratified sample of 80 is extracted" (reads as a sample of the 615).
  02-method.tex line 115: the fourth stratum is 20 census-eligible seed papers standing for an estimated 1,074 seed
  studies, eligibility judged under census rules (not criteria v1.6), texts from arXiv HTML with no page numbers.
  02-method.tex line 107: those seed records are "outside the screened set".
- **Verified here (E4).** Seed weight 1073.8 / 1657.8 = 0.648 of the frame. Seed share of domain weight: AR 0.699,
  AR-signed 0.738, inference 0.693, training 0.554, sweeps 0.539. Overall vs update-strata-only:

  | estimate | combined (paper) | update strata only | seed only |
  |---|---|---|---|
  | QA1 at 2 (code) | 0.32 | 0.17 | 0.40 |
  | QA4 at 2 (repeated runs) | 0.10 | 0.20 | 0.05 |
  | QA5 at 2 (uncertainty) | 0.10 | 0.22 | 0.05 |
  | QA7 at 2 (credited ablation) | 0.53 | 0.26 | 0.67 |
  | any unsupported claim | 0.05 | 0.14 | 0.00 (0/20) |
  | RQ3 held fixed stated (all) | 0.33 | 0.11 | - |
  | RQ4 budget reported (any) | 0.55 | 0.81 | - |
  | RQ4 non-monotone sweep | 0.62 | 0.47 | - |
  | RQ2 diffusion worse (majority) | 0.56 | 0.46 | 0.60 |

- **Why fatal.** For a PRISMA review the studies synthesised must be the studies in the flow diagram, or the
  difference must be explicit and the estimand stated. Here the text states the opposite of what the estimator does.
  The dominant stratum is also the weakest measurement: different eligibility rules, no page anchors for the
  "cite a page for every value" rule, and the two worst double-read records (R0171 groups 0/24, R0588 4/126;
  R0588 extractor A validator acceptance 90/136). The RQ6 verdict ("statistically weak") is driven by
  the seed stratum's 1/20 on QA4/QA5; the update strata show double the rate.
- **Cheapest alternative explanation for the positive results.** The combined shares are the result of a weighting
  choice made on 2026-10-20 (D0054) after the update-strata design (D0052), not a property of the included literature.
- **What would force rejection.** A referee recomputes update-only shares (as above) and finds the abstract and RQ6
  verdict describe a population that is two-thirds unscreened records.
- **Fix (no new extraction).** Re-run rq_analysis with the update strata (the included set) as the primary estimate
  and the seed stratum as a separate, labelled column ("census-eligible seed papers, not screened under v1.6");
  drop or demote the combined share to a clearly named "combined frame" estimate. Rewrite Section 5 line 7, line 19,
  Limitations line 8 and the abstract sentence so that the population of each number is named. Add the seed
  stratum's eligibility/text/agreement differences to Limitations "Screening, extraction and protocol".

## MAJOR

### M1. RQ2 "untested at matched budget" is contradicted by unreported data, and its interval ignores the design
- **Facts.** Section 5 line 27 reports only `ar_budget_matched_all` (0/35, "upper bound 0.10"); line 29 verdict
  "untested at matched budget ... the comparison is almost never made at a stated common budget"; Conclusion line 7
  and abstract repeat it. rq_analysis.py computes no "matched in any comparison" variable.
- **Verified (E4).** `matched_any` = 3/35, weighted 0.16 [0.05, 0.41]; 6 groups coded matched (M12879 G18, G21, G44;
  R1319 G22; R0214 G12, G13). The only signed matched units (R0214, 2 units) favour AR. The "all" definition is
  mechanically near-impossible for studies with many AR groups (two studies have 17 and 22). The 0.10 bound is
  Wilson at n=35 because est() falls back to the unweighted n when p=0; Kish effective n for this domain is 18.6,
  bound about 0.17.
- **Rejecting result.** Any referee who opens the records finds matched comparisons the paper says do not exist.
- **Fix.** Report matched_any and what the six matched groups show; verdict wording "rarely tested at a matched
  budget (3 of 35; the two signed matched units favour AR)"; replace the zero-cell interval by a design-based one.

### M2. RQ4 "well supported for the direction" violates the paper's own rules
- **Facts.** Line 20 defines "well supported" as same direction AND budgets held AND variation reported; RQ4 has
  variation in 12/47 (0.26) and budget in 31/47. Line 20 also says unit totals are "indicative" and conclusions rest
  on study-level statements; the direction verdict rests on 139 of 181 curves.
- **Verified (E4).** 122 of 181 curves come from two studies (M15781 62, M17249 60); study-level majority-up is about
  10 of 19 sweep studies. The non-monotone classifier (rq_analysis.monotone) has zero tolerance, so a 0.01 dip counts;
  plateaus are classified "up", so the sentence "quality stops improving or falls" misdescribes the measure. The
  "about half" study share is 0.62 combined, 0.47 update-only, 5/9 without rejected records.
- **Cheapest alternative.** Noise plus multiplicity: studies with more curves are more likely to show one wiggle.
- **Fix.** Study-level direction count; verdict "weakly supported" under the paper's own definition; tolerance
  sensitivity (e.g. dips within 1 % relative ignored) computed from existing records; reword "stops improving".

### M3. Verdict definitions are post hoc, unoperationalised, and applied inconsistently
- Disclosed as departure 9, but: RQ5 is "untested" while 8 of 20 studies make the comparison and their directions
  split (that is "mixed" by line 20's definition); RQ2 uses a compound verdict outside the vocabulary; RQ6's verdict
  ("reproducible in part and statistically weak") is not one of the four; RQ1 has no verdict although the
  introduction (line 43) says every question gets one; RQ4 as M2. Because no thresholds exist ("almost no",
  "rarely"), the claim "No verdict changes" under sensitivity (line 21) cannot be falsified, and the sensitivity
  table omits every direction variable (RQ2 better/worse, RQ3 anchor-better) and every QA item, which are the
  inputs of the RQ2, RQ3 and RQ6 verdicts.
- **Rejecting result.** A referee applies the stated definitions and gets a different verdict for RQ4 and RQ5.
- **Fix.** State numeric thresholds once (labelled post hoc), apply them mechanically to every RQ including RQ1 and
  RQ6, add direction and QA variables to Table S-sens, and only then keep the "no verdict changes" sentence.

### M4. Extraction reliability is overstated and selectively reported
- **Facts and verification.** "Values agree 616 of 616" is computed on 4 of 8 studies and only on units both
  extractors found (24 % of the union, F1_K 300/1227). Main text omits: factor type of matched groups 23/36 (0.64),
  which decides whether a group counts as AR, training or inference and therefore the RQ2-RQ4 domains; claim-status
  agreement kappa 0.44 (AC1 0.46, 33 pairs), which underlies the 260-claim paragraph and QA8 (not reported anywhere,
  including S4); QA item-score agreement never computed by agreement.py ("G3 QA kappa" null, 0 pairs; my recomputation
  from EA vs EB records: 65/72 item scores agree, QA2 and QA8 6/8). Several QA sub-items have kappa near zero (QA2b
  0.0, QA6d 0.0, QA2a 0.25, QA3b 0.29). Study-level agreement on verdict-driving flags is measured on 2-5 studies
  (RQ3 anchor-better: EA vs EB 0/2; RQ4 budget 4/5). 27 of 80 records still carry a validator rejection.
- **Consequence.** The statement "study-level statements are the ones we draw conclusions from" implies they are
  reliable; there is no evidence that they are, and the extractor swap (S3) can only move 8 of 79 records.
- **Fix.** Add factor-type, claim-status kappa, QA-item agreement and study-level flag agreement (with n) to S4 and
  one sentence in Section 2; delete "almost always" framing; say plainly that study-level reliability is unmeasured.

### M5. The interval method is anti-conservative and was not pre-specified
- est(): Wilson on an effective n derived from a variance that treats estimated domain sizes as known; normal z
  rather than design degrees of freedom despite 4 strata of about 20 and one weight of 0.65; zero/one cells use an
  ad hoc p = 0.5/n, and when the estimate is 0 or 1 the effective n is set to the unweighted denominator. N_h for the
  seed is itself an estimate (1,106 x 167/172) treated as fixed. Kish effective n: all 42.2, inference 30.0, AR 18.6,
  training 16.4, sweeps 11.3. EXTRACTION-PLAN-v0.5 contains no estimator or interval rule (grep), so the method was
  chosen after data.
- **Fix.** Within-stratum bootstrap (or Korn-Graubard Clopper-Pearson with df = n - H) re-run on existing records;
  report Kish n beside each domain; disclose the estimator as chosen after extraction.

### M6. AI-only screening and extraction: disclosure is mostly adequate, validity is not
- Disclosure strengths: Table tab:ai, abstract sentence, limitations paragraph on correlated same-family errors.
- What a CSUR referee will still demand before acceptance: (a) a recorded human check; the protocol's own rule
  (human screens 15 %, each model kappa >= 0.70 against the human) was not met, and no extraction value was ever
  checked by a human; (b) the sentence "Human checks recorded: two of the authors read the T1 screening validation
  sample" (02-method line 159) lists a check with no recorded decisions under the heading of recorded checks;
  a referee will read it as window-dressing; (c) full screener, extractor, validator and adjudicator prompts,
  model identifiers with dates, and raw outputs in the supplement (S4 lists metrics only; supplement line 74 still a
  todo); (d) the human role is "confirming a model reading" in every instance (4 screening records, 9 field
  conflicts, 3 QA1 cases, 12 pending author-check items whose values are currently the adjudicator's); (e) the
  manuscript itself was drafted by Claude agents, which invites an editor question on author accountability.
- **Fix by tomorrow (human time, not an extraction run).** The first author records yes/no on the 6-8 verdict-driving
  study-level flags for a random 12-16 of the 79 studies against the PDFs, reports agreement with n, and the
  "human checks recorded" sentence is rewritten to say that no per-record human decisions exist for screening.
  Release prompts and raw outputs.

### M7. Cross-section inconsistencies on the same constructs
- QA7 "credited component ablated in about half" (Section 5 line 50, 0.53) vs RQ3 "9 of 33 ablate the component
  they credit" (0.31) and the abstract "rarely isolated"; update-only QA7 is 0.26. Not reconciled.
- QA6 "budgets of both arms reported in half of the frame" vs RQ2 "31 of 35 (0.84) have an AR comparison with a
  budget not reported"; G-mm has 0/20 at QA6 = 2.
- RQ2 weighted direction shares (better 0.34, worse 0.56) omitted, contrary to line 19's promise of share beside
  count; the weighted reading leans "worse", the text reports only the raw 15 vs 14.
- Unit totals "131 better, 129 worse" are given although line 20 calls unit totals indicative; three studies
  (R0171 43, M12879 36, M13884 27) supply 106 of 262 units, and R0171 has 0/24 group agreement.
- Abstract "a stratified sample of 80 [of 615]" vs Method "60 included studies and 20 eligible seed studies".
- Fix: one reconciling sentence per pair, the missing shares, drop unit totals from RQ2 or flag their concentration.

### M8. RQ5 generalisation and frame
- Abstract and Conclusion: synergy "measured on no benchmark built for it". Data: 0/20 sampled from a stratum of 52;
  with finite-population correction a few purpose-built benchmarks among the 32 unsampled cannot be excluded.
  Screening fields mark RQ5 evidence (ablation, benchmark or claim) for 32 included studies, against 3 claims and
  8 ablations among 20 sampled; not reconciled. RQ5 uses only the T1 unified stratum; the flagship unified diffusion
  models (MMaDA named in Section 2) sit in the unscreened seed set.
- Fix: scope the sentence to "in the sampled 20 of 52 unified included studies", give the upper bound, reconcile
  with the 32 screener tags, and keep "mixed" (see M3).

## MINOR

- m1. "Seven take the AR numbers from another paper rather than running the baseline" (line 27): the variable counts
  only stated copies (`copied-stated`); unstated copies count as run. Wording overclaims; say "state that they copied".
- m2. RQ2 direction compares the best diffusion arm with the best AR arm per unit, with no parameter or budget
  matching; the paper should say the direction count is uninterpretable as a model comparison, not only "split".
- m3. The seed stratum frame covers only seed records both title-abstract screeners passed and that have an arXiv
  id (1,106 of 1,243 passes); the remainder is outside every stratum and is not mentioned in Limitations.
- m4. Protocol section 1 promised a protocol-comparability table (RQ2), dose-response curves (RQ4) and RQ6
  distributions by year and venue type; none is delivered, and the departures list does not say so.
- m5. Introduction lines 45-46 quote feasibility numbers (4 poolable synergy papers, 377 contrasts, 92 % without
  variance) from an older, different sample beside Section 5's sample without saying they are different samples.
- m6. The 12 pending author-check items (commit 8f71757) may change reported values; Section 2 line 122 says the
  reported values are the adjudicator's, but no sentence says which numbers are provisional.
- m7. rq-results.json computes a census "replication" (74/76) on the extraction sample; the seed stratum is a
  subsample of the census sample, so it is not independent. It is not reported now; it must not be added as a
  replication.

Checked and not a finding: no update-stratum record at positions 21-27 was extracted before D0054 cut the strata to
20 (batch-log.jsonl; sessions before 2026-10-20T19:29 cover positions 1-20 only).

---

## Referee report as a sceptical CSUR reviewer would write it

**Summary.** A PRISMA 2020 review of diffusion language models and unified multimodal diffusion models: about 80,000
records identified, 615 included after an AI-only screen frozen before the seed corpus was assessed; RQ1 answered
from screening fields, RQ2-RQ6 from a stratified sample of 80 (79 in frame) extracted by one LLM with a second LLM on
8; plus a design-space notation, a value-rule census, an error-budget taxonomy and one preregistered measurement.

**Strengths.** Unusually complete provenance (source path per number, ledgers, scripts); departures are listed
honestly, including the post hoc verdict definitions and the absence of human validation; a sensitivity table exists;
the core RQ2 observation (AR comparisons almost never budget-matched, variation rarely reported) is plausible and
useful; the AI-use table is more explicit than most.

**Weaknesses.** (1) The estimand of RQ2-RQ6 is undefined in the text and contradicted by the estimator (F1).
(2) Verdicts are post hoc, threshold-free and violate their own definitions for RQ4 and RQ5 (M2, M3). (3) Extraction
reliability rests on 8 studies, with group segmentation F1 0.29, factor-type agreement 0.64 and claim-status kappa
0.44, the last two not in the main text, and QA agreement uncomputed (M4). (4) Intervals ignore the design (M5).
(5) No human ever made a recorded screening or extraction decision (M6). (6) Key comparison-level claims are not
supported by the data as stated (M1, M7, M8).

**Questions to authors.** What population do the weighted shares estimate, and why is a stratum not screened under
v1.6 two-thirds of it? What do the six budget-matched AR comparisons show? What study-level direction does RQ4 have?
What is inter-extractor agreement on QA item scores and on the study-level flags behind each verdict, with n?

**Score.** Major revision bordering on reject (CSUR scale); a NeurIPS-style score would be 4/10 (borderline reject).
**Confidence.** 4/5 (verified against the analysis records, not against the PDFs).

**The one analysis whose absence would cause rejection.** Update-strata-only (included-set) estimates, with
design-based intervals, as the primary RQ2-RQ6 results, plus a recorded human check of the verdict-driving
study-level flags on a random subset. Without both, a referee cannot tell whether the verdicts describe the included
literature or the weighting and the extractor.

## Cheapest credible fix achievable by tomorrow (no new extraction runs)
1. Re-run rq_analysis.py (script change only) with update strata primary, seed as a separate column, design-based
   intervals, matched_any for RQ2, study-level direction for RQ4, and QA items plus direction variables in the
   sensitivity table.
2. Rewrite Section 5 lines 7, 19-21, 27-29, 41, 46, 50; Limitations line 8; abstract and conclusion sentences on RQ2,
   RQ4 and RQ5, so that each number names its population and each verdict follows a stated threshold.
3. Add factor-type agreement, claim-status kappa, QA-item and study-level flag agreement (with n) to S4 and one line
   in Section 2.
4. First author records a blind yes/no check of the verdict-driving flags on a random 12-16 studies (human time
   only) and reports agreement; reword the "human checks recorded" sentence.
