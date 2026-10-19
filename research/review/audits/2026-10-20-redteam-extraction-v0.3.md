```yaml
agent: red-team
date: 2026-10-20
brief: third adversarial review of extraction and appraisal instrument v0.3 (Paper 1); verify the v0.2 fix claims by re-running the committed scripts, re-derive units for 2 worked examples, test the multimodal rule, the n = 60 gate, and list what still blocks Stage A and Stage B
sources_examined:
  - research/CONTRACT.md
  - research/review/extraction/EXTRACTION-PLAN-v0.3.md (read in full), RESPONSE-TO-REDTEAM-v0.2.md (full), OPEN-QUESTIONS-v0.3.md (full), worked-examples-v0.3.md (full)
  - research/review/extraction/extractor-brief-v0.3.md l.45-78, 100-140, 186-262, 342-363, 395-520 (G1-G5, evidence, S02, census F1 readings, S14, blocks H and K, adjudication); extraction-schema-v0.3.json (QA4-QA6 if/then, S02 enum)
  - research/review/audits/2026-10-20-redteam-extraction-v0.1.md, -v0.2.md (my earlier reports)
  - analysis/extraction/strata.py, gate_oc.py, cost_options.py, make_schema_v03.py, build_validator_tests.py (read), flag_thresholds.py (run), validator-tests.jsonl and all logs
  - analysis/screening/ft-t1/t1b0*/FA-*.jsonl, FB-*.jsonl, c/c-t1-*/FC-*.jsonl, c-superseded.jsonl, t1-decisions-all.jsonl; tools/ft-session/refresh_t1.py l.1-40; research/review/screening/criteria-v1.6-screener.md l.280-300
  - research/sources/md/fulltext-pymupdf/ M13864 (abstract, l.485-810 = s4.1-4.4, Tables 1-2, Figures 3-5), M12766 (abstract, setup l.404-424, Tables 1-5 l.528-1012, Tables 6-7 l.1013-1150, Appendix D-E and Tables 9-10 l.1585-1730, Figure 12 caption); M07474 l.415-425, 528-575, 774-795, 1060-1125; M18118 and M18656 (grep for image/LLaDA-V evidence)
  - research/ledgers/decisions.jsonl (last row D0034)
coverage: >
  Re-ran every committed script into my scratchpad and diffed against the logs (strata, cost_options,
  flag_thresholds, build_validator_tests: identical; gate_oc: identical except elapsed seconds; make_schema_v03
  rebuilt into the scratchpad: sha256 bb0ed559... identical, Draft 2020-12 check_schema ok). Ran additional
  gate_oc.simulate scenarios (scratchpad sens.py, sens2.py, lines.py, n30.py; committed code imported read-only).
  Re-derived units for M13864 and M12766 from the full texts before comparing with worked-examples-v0.3.md.
  Checked the mm field in every FA/FB/FC row and 7 of the 20 borderline ids (5 required). NOT covered: FDM,
  TrustLDM and LLaDA2.1 units (only FDM's H01 spot-checked), the validator itself (not built), census codebook
  equivalence (gate-auditor), the brief outside the line ranges listed. Brief allows one output file, so no
  ledger rows were added. The brief asks for a concrete fix per finding, so fixes are given (deviation from my
  agent definition); criticism is not softened. Severity: critical = blocks the gate it names.
claims:
  - statement: Every number printed in the v0.3 plan from the committed scripts reproduces exactly on re-run (strata, gate OC, cost, flag thresholds, validator tests, schema hash).
    status: supported
    evidence: scratchpad strata.out, gate_oc.out, cost.out, flag.out, vt.jsonl diffed against analysis/extraction/*-log.txt; schema rebuilt sha256 bb0ed559c73f96cc...
    level: E3
    confidence: 0.95
  - statement: The claimed P(pass | all good) >= 0.889 at n = 60 holds only for intra-record correlation (ICC) <= 0.20; at ICC 0.30 it is 0.776 and at 0.40 it is 0.635, and Stage A is not required to measure ICC before the gate.
    status: supported
    evidence: scratchpad sens2.py with gate_oc.simulate, 1,000 replicates per case; PLAN s14 B1 names only units per record
    level: E3
    confidence: 0.8
  - statement: No gate criterion measures agreement on group anchors or on the K attributes that set the sign and the pooling eligibility of every contrast (higher_is_better, held_fixed, other_changes, budget_across_arms, scoring, credited_ablation).
    status: supported
    evidence: PLAN s10.3 metric list and s10.4 table; v0.2 PLAN l.396 (K15 matched derived from those attributes)
    level: E2
    confidence: 0.9
  - statement: The mm field exists in every FA and FB row (885 and 882) and the rule is reproducible, but about 29 of the 108 C2 records are text-diffusion or general discrete-diffusion papers whose only non-text work is a separate image, audio or music experiment.
    status: supported
    evidence: scratchpad mmcheck.py, c2notes.py (screener notes of all 108 C2 records); criteria-v1.6-screener.md l.290
    level: E3 (field), E1 (classification from screener notes, not full texts)
    confidence: 0.75
  - statement: For M13864 my independent units equal the worked example; for M12766 groups, arms and K units equal the worked example, but U3(iii) allows a second compliant anchor for G03 and G04.
    status: supported
    evidence: M12766 l.739-1012 (Tables 2-5), brief G1d and U3(iii)
    level: E2
    confidence: 0.8
competing_explanations:
  - ICC 0.10 may be realistic if most records are as simple as Muddit Table 1; the v0.2 evidence (TrustLDM 0 to about 90 groups under v0.2 rules) points the other way, but v0.3 rules narrow it. Only Stage A can tell.
  - The "side-experiment" C2 records may be what the user means by "all multimodal"; then M2 below is a labelling issue only.
unknowns:
  - real ICC and units per record (Stage A); share of column_unverified units; real anchor agreement
next_test: {hypothesis: "two extractors following brief v0.3 agree on group anchors and K attributes as well as on keys", intervention: "Stage A on the 7 drawn records (not the 5 worked-example papers), agreement.py extended with an anchor and K-attribute block; estimate per-metric ICC; rerun gate_oc.py with the measured ICC", primary_metric: "F1_G, anchor agreement on matched groups, K-attr raw agreement, estimated ICC; joint P(pass | good) at the chosen n", falsifier: "F1_G below 0.6 on the 7 drawn records, or anchor agreement below 0.8, or P(pass | good) below 0.85 at n = 60 with the measured ICC", gpu_hours: 0}
```

# Red-team audit 3: extraction and appraisal instrument v0.3

Verdict: **Stage A (development) may proceed once the human author's rows are entered, the T1 gate passes,
the tools are built and two pre-draw fixes (M3 wording, M4 contamination) are made. Stage B (gate) may not run
until C1 is fixed and M1 and M5 are resolved.** v0.3 is a large improvement: every committed number reproduces
exactly, the gate is now calibrated by a joint simulation, the rules give one key list on the two papers I
re-derived, and the multimodal rule rests on a real screening field. The remaining problems are what the gate
does not measure, how fragile its operating characteristics are to one unmeasured parameter, and what
"multimodal" now means.

References: PLAN = EXTRACTION-PLAN-v0.3.md, BRIEF = extractor-brief-v0.3.md, RESP = RESPONSE-TO-REDTEAM-v0.2.md,
WE = worked-examples-v0.3.md, OQ = OPEN-QUESTIONS-v0.3.md. Scratchpad scripts are not committed.

---

## 1. Are the claimed v0.2 fixes real? (text checked, scripts re-run)

Re-runs (all into the scratchpad, diffed against the committed logs):
- `python -I strata.py --gate-n 60`: identical to strata-log.txt (C1 53, NL 12, C2 108, FR 435; strata 159/66/58/152;
  allocation 44/18/16/42; deff 1.37; list hashes C1 91615db3..., C2 6766a919..., FR c7508ab7...).
- `python -u -E -P gate_oc.py`: identical to gate_oc-log.txt except "elapsed 659 s" against 661 s. Every
  probability in PLAN s10.6 and OQ3-07 matches the log.
- `python -I cost_options.py`, `python -E -P flag_thresholds.py`: identical. c(15) 8, c(20) 12, c(30) 20,
  c(60) 43 confirmed.
- `build_validator_tests.py` into the scratchpad: byte-identical; sha256 9991a1f7... as in PLAN Appendix A. The
  six fixture texts still hash to the pinned values.
- `make_schema_v03.py` (DST redirected to the scratchpad): sha256 bb0ed559... identical; check_schema ok.

| Finding | RESP status | Verified | Note |
|---|---|---|---|
| F-CR1 | fixed | **real for the stated model**; not robust | Numbers reproduce. P(pass\|good) falls below 0.85 at ICC >= 0.25 (M1). |
| F-MA1 | fixed in spec | **partly** | Keys agree with my derivation on M13864 and M12766. U3(iii) still leaves two anchors on Muddit G03/G04 (M3). Stage A falsifier contaminated (M4). |
| F-MA2 | fixed | real | rq_class out of the group key, value out of the H key, M-val on K only. |
| F-MA3 | fixed | real | Per-item QA kappa simulated. The "under-coverage" reason for the two raised lines is confirmed: with line = bad level, P(criterion passes \| bad) is 0.110 (QA kappa) and 0.090 (M-val); with the plan's lines, 0.008 and 0.028 (lines.py, 600 replicates). |
| F-MA4 | fixed in spec | real in spec | 35 tests reproducible and hash-pinned; tool not built. Expected statuses I checked (V05, V12, V14, V21-V23, V26-V28) are consistent with the fixtures and the s6.3 text. The v0.2 tests T01-T22 "as amended" exist only as v0.2 plan text, not as v0.3-shape data (part 5). |
| F-MA5 | fixed | **real as a rule; construct problem** | mm exists in all 885 FA and 882 FB rows; C wrote mm in 52 of 116 C rows; the script is deterministic. See M2, m3, m4. |
| F-MA6 | fixed | real | Two options, costed from one table; draft row worded as the user's choice. |
| F-MA7 | fixed as spec | real; residual | One per-record table, used consistently (I re-derived every component). Missing component: certainty second reading of column_unverified units (m6). |
| F-mi1 | fixed | real | HEAD hash 962e3171... printed by strata.py. |
| F-mi2 | fixed | real | Scripts are committed in f58c5c6 (PLAN header, s14 A8 and Appendix A still say "not committed": m9). |
| F-mi3 | fixed | real, small residual | No actual collision; ranges are not disjoint as described (m9). |
| F-mi4, F-mi6, F-mi7, F-mi8, F-mi9, F-mi11, F-mi12, F-mi13 | fixed | real | F-mi13: BRIEF l.188-190. |
| F-mi5 | fixed | real | Schema allOf if/then on QA4-QA6; n is yes/no only and a-d are required, so an omitted sub-item fails. |
| F-mi10 | partly | agree | 6 candidates printed, none applied. |

No claimed fix is false. Claimed "fixed" but only partly true: **F-CR1** (robustness), **F-MA1**, **F-MA5**.

## 2. Worked examples re-derived independently (M13864 and M12766)

I derived the lists from the texts and the BRIEF before opening WE.

**M13864 (analysis).** Focal model Dream-v0-Instruct-7B (arm in Tables 1-2 and Figures 3-5; U2c). H01 = 0.215
(Table 1, BLEU / ru; the text quotes it first, l.569-570). S14 = Table 1, Dream against Qwen2.5-7B (analysis
study, caption and l.571 label Qwen autoregressive). Groups: G01 Table 1 RQ2 (6 arms, anchor null, 4 units);
G02 Table 2 RQ2 (3 arms, 5 units including Time); G03 Table 2 rate=1 against rate=4 (tokens-per-step, anchor
null: the paper states no default, only a conclusion at l.629-631); G04-G05 Figures 3-4 (1 fig-only unit each,
Russian/English series are conditions); G06 Figure 5. U12 flags 3 G02 contrasts (Qwen COMET-ru 0.532 against
0.531 is not a duplicate). **Identical to WE: 6 groups, 18 units.** One residual: Figure 5 plots four x-axis
categories (Ru BLEU, En BLEU, Ru COMET, En COMET, l.697-700), not condition series. U10 ("one unit per
(benchmark, metric) pair; condition series are not units") gives 2 units; U9 (condition is part of the unit)
gives 4. Both are compliant readings, and condition is in the K key (m1).

**M12766 (Muddit).** Focal config "Table 1: Muddit (512 × 512)" (the setup at l.420-422 names inference
settings, not an arm). H01 = 0.61 by C-F1b. S14 baseline LWM (first arm whose Image Gen Arch is AR, CT6 claim).
G01 Table 1: 4 arms, 1 unit (sub-score rule). G02 Table 2: 11 AR-text arms, 5 units. G05 Table 5 anchor T=64
(setup l.421). G06 Table 7: Show-O (512×512) AR for text by U5 cross-table label; 3 units, all U12 duplicates of
G02. G07 Table 9 anchor CFG 1.5. G08 Figure 12 one fig-only latency unit. Table 10 compares non-AR models only
(no group). **Groups, arms and units identical to WE (8 groups, 21 units, 3 duplicates).**

**Where I diverge: the anchors of G03 (Table 3) and G04 (Table 4).** WE takes 0.6 and "Joint training" by
U3(iii), matching Table 2's Muddit values 59.9 / 68.2. But U3(iii) compares with "an earlier main-results
table", and G1d defines *the* main-results table as the first experiments table with an own arm, which is
Table 1. Table 1 shares only GenEval with Tables 3-4, printed as 0.61 against 61.6, so not at the same scale
(and 0.616 does not round to 0.61). Read strictly, (iii) fails and (iv) gives the first own arm in reading
order: **0.2** for Table 3 and **"T2I only"** for Table 4. Under that reading the RQ5 task-removal contrasts of
Table 4 are computed against a single-task arm, which inverts the comparison the paper reports. Both readings
comply with the text (M3).

**Would two extractors agree?** On keys, yes for these two papers (one 2-or-4 unit residual). On anchors, no for
2 of the 8 Muddit groups. Anchors are attributes outside every key, so F1_G and F1_K would not show the
disagreement, and no gate criterion measures it (C1).

## 3. The multimodal rule

- **The field exists as claimed.** All 885 FA and 882 FB rows have the key `mm`. Among the 608 includes A has 4
  null values, all on records C ruled (M03137, M12594, M13551, M15992), where C's mm is used. The script
  reproduces exactly. The definition is criteria-v1.6-screener l.290: "multimodal (takes or generates a D4
  modality)", judged per paper, not per model.
- **Five (seven) borderline ids checked** (screener notes plus full-text grep):
  - M18118 (B1, rule gives frame R). The paper evaluates LLaDA-V on MathVista (l.482, 489, 985). That is image
    input to a diffusion LM, so by the mm definition it is multimodal; screener A missed it, and the KW
    tie-break cannot see it because the abstract never mentions images.
  - M18656 (B1, frame R). It reproduces the ITD image pipeline (l.179, 473, 693-696). Multimodal by definition
    in the side-experiment sense; frame R by intent.
  - M15613 (B3, frame R). Time-series captioning; both screeners "other"; time series is not D4. Correct by
    definition.
  - M14706 (B2, C2). A PhD thesis on MDLM and Duo text diffusion with one image chapter (MuLAN, CIFAR).
    Multimodal by definition, a text-DLM study by intent.
  - M00285 (B2, C2). ARDM on text8 plus separate CIFAR-10 and SC09 models. Same pattern as M14706.
  - Also read: M05663 (text8 plus CIFAR via VQ-VAE) and M16730 (LLaDA text plus MNIST and antibodies), both C2,
    same pattern.
- **Result.** The rule is reproducible but measures "the paper contains any D4 experiment". From the screener
  notes of all 108 C2 records (c2notes.py), about 29 are of this side-experiment kind: M00285, M02955, M04297,
  M04350, M04373, M05608, M05642, M05663, M06218, M09321, M10881, M11247, M12175, M13247, M13444, M13674,
  M14706, M15373, M15652, M15895, M16133, M16251, M16263, M16730, M16813, M18406, M18456, M19099, U04378. At the
  same time M18118, which does put images into a diffusion LM, is in frame R (M2).
- **i1 and nonlang_only use screener A's value** when A and B agree on the decision but not on these fields.
  This affects 4 i1 cases (M10840, M12859 and U04330: a against ab, which flips the C1/C2 label; M16043: ab
  against b) and 2 nonlang_only cases (M11389, M18059) (m3).

## 4. Gate n = 60

- **Simulated characteristics as stated: correct.** Re-run is identical: 0.974 all good; max single-bad 0.071;
  size table and sensitivity table as printed.
- **Not robust to ICC, which is E0 and not scheduled for measurement** (sens2.py, 1,000 replicates each):

| n | ICC | P(pass \| all good) | F1_G marginal |
|---|---|---|---|
| 60 | 0.10 (plan) | 0.977 | 0.986 |
| 60 | 0.20 (plan) | 0.889 | |
| 60 | 0.25 | 0.840 | 0.932 |
| 60 | 0.30 | 0.776 | 0.914 |
| 60 | 0.40 | 0.635 | 0.872 |
| 72 | 0.30 | 0.854 | 0.938 |
| 90 | 0.30 | 0.932 | 0.970 |
| 45 | 0.20 | 0.747 | 0.888 |

  F1_G, M-val and M-class carry the loss. The F1_G bad-level pass rate stays controlled at ICC 0.30 (0.043,
  sens.py), so the problem is false failure, the same failure mode as v0.2's F-CR1, now conditional on one
  parameter. ICC 0.10 means a record-level SD of about 0.14 around F1_G 0.75. A mixture where 20 percent of
  records are near 0.2 and the rest near 0.89 already gives an ICC of about 0.4. The v0.2 evidence (one paper
  ranging from 0 to about 90 groups) is of that kind.
- **Grey zone (informative, not a defect).** At n = 60, F1_G 0.68 passes 0.63; anchors 0.70 pass 0.45; QA kappa
  0.55 passes 0.84-0.88 (sens.py 400 and lines.py 600 replicates).
- **Is the cost increase justified?** Against n = 45, yes under the model: n = 45 fails the plan's own ICC 0.20
  case (0.747), so the 2.6M-4.7M for 15 more records is justified *if* ICC <= 0.20. Against alternatives, the
  case is not made. At n = 30 the G1, G3 and F1_H criteria jointly pass 0.966 (n30.py), and only the K and
  anchor criteria need about 60 records. A split design (30 full records plus 30 records with only K, F1 and S14
  extracted twice) was not costed; RESP rejects the red-team's version for process reasons only (m8).

## 5. What still blocks Stage A and Stage B (beyond the human author's decision rows and the T1 gate)

**Stage A**
1. A4 gate-auditor check of block F and C-F1a to C-F1e. Agent work, not done.
2. A7 tools. Note that s10.2 computes Stage A agreement "by agreement.py", but A7 does not list agreement.py
   (only B3 does). Stage A's falsifier (F1_G < 0.6) cannot be computed without it (m10). The v0.2 tests T01-T22
   "as amended" must be written as v0.3-shape data before ex_validate can be said to pass them (s6.6, A7).
3. M4: compute the falsifier on the 7 drawn records, or remove worked-example strings from the brief.
4. M3: fix the U3(iii) wording, or Stage A will just rediscover it.
5. m5: draw_pilot.py must exclude the 5 worked-example ids from the Stage A pools. M09530 and M13864 are in the
   24-record benchmark/analysis-title pool.
6. M2: OQ3-03 must offer the user the construct choice before the A2/A5 rows. Adding the option is agent work;
   the choice is the user's.
7. A10 (OQ2-07 adjudicator route) and A5 (borderline and duplicate check) are human items already listed.

**Stage B**
1. **C1**: add anchor and K-attribute agreement to the gate rule and to gate_oc.py before B2.
2. **M1**: estimate ICC per metric in Stage A, rerun gate_oc.py with it, and fix n in the B2 row from that run.
   B1 currently requires a rerun only for unit counts.
3. **M5**: specify how agreement.py matches K units whose benchmark or metric string is not in the frozen
   lookups (B3, B5).
4. m2: normalise the column leaf in the U14 key, or replace it by the column index, before B3.
5. B3, B4, B5 as listed; B6 (gold subset) is a human item.

---

## Findings

### Critical

**C1. The gate does not measure anchors or the K attributes that set each contrast's sign and pooling
eligibility (blocks Stage B).**

Evidence:
- PLAN s5.1 principle 5 says anchor, factor_type and credited_ablation "are attributes measured on matched
  units". Only factor_type is measured, through M-class (s10.3).
- No criterion or diagnostic compares, on matched groups, units or arms:
  - anchor_arm (only anchor_rule agreement, a diagnostic);
  - higher_is_better, which sets every contrast's sign;
  - held_fixed, other_changes, budget_across_arms and arm scoring, which define K15 "matched", the pooling
    eligibility (v0.2 PLAN l.396, unchanged);
  - credited_ablation (QA7, RQ4), number_source, level_num, dose_unit and shape.
- G3 has blocks S, D, F, QA-sub, CT and H-attr; there is no K-attribute block.
- Section 2 shows two compliant anchors for 2 of 8 Muddit groups. A gate that passes cannot detect this.

Rejection test: a Stage A or gate pair in which F1_G, F1_K and M-val pass but anchor agreement on matched
groups, or agreement on K15 "matched", is below 0.8.

Fix: add G3 "K-attr" (raw agreement over anchor_arm, higher_is_better, held_fixed, budget_across_arms,
credited_ablation and arm scoring on matched groups and units, good 0.85, bad 0.70) and M-matched (agreement of
the derived K15 flag on matched units). Add both to gate_oc.py and rerun before the B2 row. Alternatively, derive
higher_is_better by script from the metric lookup and gate the rest.

### Major

**M1. The joint operating characteristics hold only for ICC <= 0.20, an unmeasured assumption.**

Evidence: section 4 table. P(pass | good) at n = 60 is 0.840 at ICC 0.25, 0.776 at 0.30 and 0.635 at 0.40.
PLAN s10.6 says inputs "are replaced by Stage A values where Stage A measures them", but s14 B1 requires a rerun
only "with Stage A's units per record if they are below its assumptions". OQ3-07 tells the user n = 60 "stays at
or above 0.889 in every sensitivity case run". True, but the cases tried stop at the edge of the plausible range.

Rejection test: an ICC for F1_G or M-val above 0.25 estimated from Stage A, with n unchanged.

Fix: B1 must include per-metric ICC estimates from Stage A (12 records give a crude estimate, so use its upper
80 percent bound). Rerun gate_oc.py with them and set n in the B2 row so that P(pass | good) >= 0.85. Add ICC 0.30
to the committed sensitivity table and to OQ3-07.

**M2. "All multimodal" now means "any D4 experiment in the paper", which about 29 of 108 C2 records meet only
through a separate image, audio or music model; the user was not asked about this construct.**

Evidence: section 3. Examples:
- M00285 ARDM (text8 plus separate CIFAR-10 and SC09 models);
- M14706 (a text-DLM thesis with one image chapter);
- M16813 (an optimizer benchmark with a CelebA control);
- M16730 (LLaDA text plus MNIST).

These are certainty C2 records reported in "C2 census" multimodal columns, while M18118 (a DLM given images,
LLaDA-V on MathVista) is in frame R. OQ3-03 offers only "C1 only" or "C1 + C2 by the rule", and says C2 costs
4.3M-8.6M (Option 1) or 8.4M-14.6M (Option 2) without saying what a quarter of it is.

Consequences:
- Frame R becomes "papers with no D4 experiment of any kind", not "language-only DLM studies".
- Multimodal descriptive tables mix side-experiment text papers with VLM, ASR and OCR models.
- The pooled 596 estimate is unaffected (certainty stratum).

Rejection test: a human check of a random 20 of the 108 C2 records in which more than 3 have no model that takes
or produces a D4 modality together with text.

Fix: add option (c) to OQ3-03. C2 = mm multimodal AND a D4 modality enters or leaves the same model that produces
the text, coded once per C2 record (108 records, one human or EC pass over the screener notes, then full text
where the notes are unclear). Put the side-experiment records in frame R, or in a labelled C2b stratum. Re-label
the columns "C2 (rule)" whatever is chosen.

**M3. U3(iii) "an earlier main-results table" conflicts with G1d's single main-results table and gives two
compliant anchors (F-MA1 residual).**

Evidence: section 2, Muddit Table 3 (0.6 or 0.2) and Table 4 ("Joint training" or "T2I only"). The WE reading
needs Table 2 to be "a main-results table", which G1d excludes.

Rejection test: in Stage A, two extractors choose different anchors through clause (iii) or (iv) on the same
group.

Fix: reword (iii) as "any earlier results table of the record that has the focal configuration's arm", and add a
worked example. State that a factor group's anchor is never a single-task or ablated arm when the full
configuration is present (Table 4).

**M4. Stage A's falsifier is contaminated: the brief quotes the answers for the five worked-example papers.**

Evidence (BRIEF):
- l.60: "Table 2: FDM (K=2)" is FDM's focal configuration;
- l.104 and l.480: "Dream-v0-Instruct-7B (rate=1)" (M13864);
- l.436: "for AR model, we report its scores only" (LLaDA2.1's AR marker);
- l.413: "891.74 for 892" (LLaDA2.1's trace);
- l.469: "Suffix / Short", "ru" (TrustLDM, M13864);
- "Discrete Diff." (Muddit).

PLAN s10.2 puts these five papers into Stage A, and RESP F-MA1 keeps "F1_G below 0.6 on Stage A" as the
falsifier. Agreement on 5 of 12 records is inflated by design.

Rejection test: F1_G on the 7 drawn Stage A records more than 0.15 below F1_G on the 5 worked-example records.

Fix: compute and report the F-MA1 falsifier on the 7 drawn records only (or replace the brief's examples with
examples from papers outside Stage A and the gate), and say so in the Stage A report.

**M5. K units with benchmark or metric strings outside the frozen lookups have no defined match rule in the
gate.**

Evidence:
- The K key uses benchmark_id and metric_id (PLAN s5.4).
- The lookups do not exist (A7 "skeletons"; no analysis/extraction/lookups/). They are built from 12 Stage A
  records and frozen for the gate (B5).
- agreement.py runs "before EC sees anything" (s10.3), but unmapped strings are resolved only by EC queues (v0.2
  s6.5).
- With 60 fresh records from 543, many strings will be unmapped. F1_K and M-val are then undefined, or every such
  unit is a mismatch (false fail).

Rejection test: more than 5 percent of gate K units carry an unmapped benchmark or metric string.

Fix: before B3, specify the fallback for unmapped strings: normalised printed strings (U11 normalisation)
compared directly, with the share of fallback matches reported. Add self-tests for it.

### Minor

- **m1. Figure axis categories (U9 against U10).** Section 2, M13864 Figure 5 gives 2 or 4 units. Fix: state
  that x-axis categories that are conditions form separate units (or never do), and add a worked example.
- **m2. The H key and G5 still contain a free string.** U14 keys an F1-table unit by (where, row_group,
  normalised row_label, column leaf), and M-anchor uses it. The leaf is the extractor's composition
  ("LLaDA / Accuracy"), which is not normalised and is verified only for membership in two-level headers. Fix:
  use the column index plus U11-normalised leaf parts.
- **m3. Asymmetric source for i1 and nonlang_only.** These come from screener A when A and B disagree on them
  (section 3; 3 records change C1/C2 label, 2 change NL/frame membership). Fix: route these 6 to the human
  check of OQ3-04, or apply the mm logic (agreed value, else split).
- **m4. The B1 keyword tie-break contradicts the mm definition.** M18118 is multimodal by definition (LLaDA-V
  MathVista) but goes to frame R because the abstract has no keyword. Fix: resolve split records from the full
  text in the OQ3-04 check, not by KW.
- **m5. Stage A pools can redraw worked-example papers.** M09530 and M13864 are in the 24-record
  benchmark/analysis-title pool, and s10.2 does not exclude the 5 fixed ids. Fix: exclude them in
  draw_pilot.py and say so in s10.2.
- **m6. The cost table omits certainty second reading.** column_unverified units go to the second reader with
  certainty (s6.3 item 9), and 5 of the 7 fixture tables are two-level, two of them with unverifiable order (V06,
  V28). Fix: add the component to cost_options.py with the Stage A share.
- **m7. Figure groups and `shape` are read from text-only files.** Sessions read PyMuPDF text (BRIEF l.27).
  Raster figures are invisible, and vector figures give axis ticks and legends but no curves (M07474
  l.1060-1080). shape can only come from prose, and figure-group counts depend on figure format. Fix: code
  shape only when the prose states it (else unclear), and report the share of figure groups by source.
- **m8. Gate-size alternatives are not costed.** The split design (L and Q criteria on 30, K and anchors on 60)
  meets the same targets under the model (section 4). Fix: cost it in OQ3-07 beside n = 60.
- **m9. Stale or imprecise text.**
  - PLAN header, s14 A8 and Appendix A say the scripts are not committed; they are in f58c5c6, so A8 is met.
  - The seed table calls ranges disjoint, but gate_oc's seeds span 20262000-20262605, which contains the
    gold-subset seed 20262100 (not used by the simulation), and tranche seeds 20261500 + 10t + h reach
    20261600 at t = 10.
- **m10. agreement.py is needed for Stage A but listed only for Stage B.** s10.2 computes Stage A agreement by
  agreement.py; A7 omits it. Fix: add a development version to A7.

---

Counts: critical 1, major 5, minor 10. Stage A may proceed once the human author's rows are entered, the T1 gate
passes and the tools (including agreement.py) are built, provided M3 and M4 are fixed first. Stage B may not
proceed until C1 is fixed and M1 and M5 are resolved. Most important remaining fix: gate the anchors and K
attributes (C1).
