# Response to red-team audit 3 of extraction form v0.3 (2026-10-20)

Audit: `research/review/audits/2026-10-20-redteam-extraction-v0.3.md` (1 critical, 5 major, 10 minor).
Revised files: EXTRACTION-PLAN-v0.4.md (PLAN; a delta on v0.3 with a section map), extractor-brief-v0.4.md
(BRIEF), extraction-schema-v0.4.json, OPEN-QUESTIONS-v0.4.md (OQ), worked-examples-v0.4.md (WE; reference
file, never given to sessions). New scripts and logs in `analysis/extraction/`: gate_oc_v04.py,
gate_adaptive_v04.py, icc_check.py, multimodal_options.py, cost_options_v04.py, make_schema_v04.py,
brief_contamination.py. v0.3 scripts and logs are unchanged, so every v0.3 number still reproduces. Status
words: **fixed** (the rejection test now passes on the artifact named, or the rule the fix asked for is in
the binding text), **partly** (what remains is named), **options** (the human author's choice, written up),
**rejected** (with reason). Nothing is committed and no tool is built.

## Critical

**C1. The gate does not measure anchors or the K attributes that set sign and poolability. Fixed.**
- Four criteria in PLAN s10.4, each a lower bound against a numerical bad level, defined in s10.3:
  M-anchorG (anchor arm on matched groups; null-null agrees, null against non-null does not), M-sign
  (higher_is_better on matched K units), K-attr (held_fixed, budget_across_arms, credited_ablation per matched
  group, scoring per matched arm) and M-pool (each reader's derived K15 matched flag on matched K units).
- Departure from the proposal: higher_is_better gets its own criterion with stricter levels (good 0.97, bad
  0.90) instead of being pooled into K-attr, because one sign disagreement reverses a contrast and a pooled
  rate would hide it. The red-team's alternative (derive the sign from the metric lookup) is used as a
  cross-check after agreement is measured: M-sign is computed on the extractors' values; the lookup's
  direction column then flags conflicts for EC.
- Lines: the four sit at 0.71, 0.71, 0.91, 0.71, because at the bad level the percentile cluster bootstrap
  passes in 0.087-0.100 of simulated gates (gate_oc_v04-calibrate-log.txt).
- Joint characteristics rerun with all 19 criteria (gate_oc_v04-log.txt, PLAN s10.6 Table A): at n 60, ICC
  0.10, P(pass | all good) 0.866; any one quantity bad, at most 0.076; each new criterion bad alone 0.030-0.044.
- Rejection test (anchor or K15 agreement below 0.8 while F1_G, F1_K and M-val pass): such a gate now fails
  M-anchorG or M-pool whenever their lower bound falls below 0.71.

## Major

**M1. The operating characteristics hold only for ICC <= 0.20. Fixed by design B-IP; the size depends on data.**
- The red-team's numbers reproduce in kind with 19 criteria and are worse: a fixed 60-record gate passes a
  good instrument with probability 0.852 at ICC 0.10, 0.660 at 0.20, 0.486 at 0.30 (PLAN s10.6 Table B, now
  ICC 0.05-0.40 and n 60-120, including ICC 0.30 as asked).
- Stage A estimates the ICC (PLAN s10.2): per metric, pooled over eight count metrics, with an upper bound.
  The proposed bound (upper 80 percent of a record bootstrap) was tested before use and **under-covers**:
  with 12 records it covers the true ICC in 0.54 of cases at ICC 0.20 and 0.34 at 0.30 (icc_check-log.txt).
  The plan uses a Neyman bound by parametric simulation instead (coverage 0.81-0.89).
- Even the calibrated bound is wide with 12 records: mapped through Table B it would fix n >= 90 in 0.61 of
  cases at a true ICC of 0.10, and n > 120 in 0.15 (PLAN s10.6). Fixing n from Stage A alone is therefore
  costly. The rule the brief asked for ("what happens if the ICC is above the value the gate assumes") is
  design B-IP (PLAN s10.7): Stage A's bound sets the planned size for the budget; the gate draws 60 records,
  re-estimates the ICC on them without computing any criterion, extends to the smallest n in {60, 72, 90,
  105, 120} that gives P(pass | good) >= 0.85 at the bound, and applies the rule once to all n records.
- Simulated as a whole procedure (gate_adaptive_v04-log.txt, PLAN s10.6 Table D): P(pass | all good) 0.935, 0.915, 0.912, 0.910, 0.860 at true ICC 0.05, 0.10, 0.15, 0.20, 0.30, with mean final n 61, 71, 87, 99, 119; P(pass | one of five weak quantities bad) at most 0.070 at ICC 0.10 and 0.30, no higher than the fixed-n gate (0.076). The re-estimation does not inflate false passes in this model.
- Above ICC about 0.30 even 120 records give less than 0.85 (0.769 at 0.40); s10.7 step 6 makes the verdict
  say so and leaves the next step to the human author.
- Rejection test (ICC above 0.25 estimated in Stage A with n unchanged): n is no longer fixed in advance.

**M2. "All multimodal" means "any D4 experiment". Options written up; not chosen.** OQ4-03 and PLAN s2.3 give
four options with counts from `multimodal_options.py`: (a) C1 only: C2 0, frame R 543; (b) the v0.3 rule:
C2 108, frame R 435; (c) joint-model rule with side-experiment papers in frame R: C2 80-89, frame R 454-463;
(d) joint-model rule with a labelled C2b census of 29: C2 80-89, frame R 425-434; with K records and token
ranges for both scope options. The 29 side-experiment ids are the red-team's (E1); a keyword cross-check
finds multimodal benchmark or diffusion-LM names in 2 of them against 59 of the other 79 C2 records. Frame-R
candidates: M18118 confirmed plus 9 keyword candidates. Columns are relabelled by rule under every option.
The red-team's rejection test (human check of 20 random C2 records) is subsumed by OQ4-04 item 4 if option
(c) or (d) is chosen.

**M3. U3(iii) gives two compliant anchors. Fixed.** BRIEF block K U3 now names its clauses; value-identity uses
every earlier results table containing the reference arm (the focal configuration's arm, or for a
second-factor level that is another own model, that model's arm in the focal setting), a numerical scale
test (values within a factor of 2), equality after rounding to the coarser precision, "-" not a value, and a
tie rule; a full-configuration clause keeps single-task, "only" and "w/o" arms from anchoring removal groups.
WE s2 derives one anchor each for Muddit Table 3 (0.6) and Table 4 (Joint training) from M12766 l.870-949;
WE s5 does the same for both LLaDA2.1 Table 4 levels (w/o MBE; the mini level now uses the mini reference arm,
equal on seven benchmarks, l.720-948 and l.1046-1110). The worked example the fix asked for is in WE, not in
the brief (M4). schema v0.4 adds full-configuration to anchor_rule.

**M4. Stage A's falsifier is contaminated. Fixed (both parts of the proposed fix).**
- Every example in the brief's text blocks and in the schema descriptions is synthetic. A committed check
  (`brief_contamination.py`, log brief_contamination-log.txt) searches every quoted example and decimal
  number in the session text in all 608 include texts. v0.3: 17 known strings from drawable papers, 18
  strings found in 1-5 include texts. v0.4: 0 known strings; the 10 strings still found in 1-5 texts are the
  instrument's own field ids and JSON fragments (C04, K02, QA1, T01) and codebook terms (T>1, beam B, not
  stated, tuned per task), unchanged since v0.1.
- The check found two contaminations the audit did not list: the E3 table example came from M03416
  (DiffuseDef, a frame-R include) and the H example "by 7.56 points" occurs only in M13195. Both replaced.
  Schema v0.3's descriptions also carried "Table 2: FDM (K=2)", "Discrete Diff.", "w/o remasking" and
  "LLaMA-3 8B"; replaced.
- PLAN s10.2: the falsifier F1_G < 0.6 is computed on the 7 drawn Stage A records only; the 5 worked-example
  records are reported separately with the red-team's contamination test (drawn more than 0.15 below).

**M5. No match rule for K units with unmapped strings. Fixed.** PLAN s5.4: key part = lookup id if listed,
else "raw:" + normalised string (normalisation defined); mapped never matches unmapped; reported: fallback
share, F1_K and M-val on fully mapped units, a lenient F1_K. The gate uses the primary key. Lookups are seeded
from Stage A and a fixed metric alias list. agreement.py self-tests include the raw-match cases (s11.1).
Rejection test (fallback share above 0.05) is reported in the verdict and checked on Stage A records before
the gate (s14 B5).

## Minor

| Finding | Status | Where |
|---|---|---|
| m1 figure axis categories | fixed | BRIEF U10: a condition never splits figure units (series, x-axis category or panel); synthetic example; WE s4 G06 (2 units) |
| m2 free string in the H key | fixed | PLAN s5.2: column index when both cells are column-verified, else U11-normalised leaf parts |
| m3 asymmetric source for i1 and nonlang_only | fixed (routed) | multimodal_options.py lists the 6 records; OQ4-04 item 2 |
| m4 keyword tie-break contradicts mm | fixed | keyword rule retired for split records; full-text check (OQ4-04 item 1) |
| m5 Stage A pools can redraw worked-example papers | fixed | PLAN s10.2 and s11: draw_pilot.py excludes the 5 ids |
| m6 certainty second reading not costed | fixed | cost_options_v04.py: 1.5M-9.1M (share 0.10-0.30, E0) |
| m7 figure groups and shape from text files | fixed | BRIEF U10 and group fields: shape only from a stated sentence; agreement.py reports figure-only and shape-unclear shares |
| m8 gate-size alternatives not costed | fixed | split design simulated (PLAN s10.6 Table E) and costed (s2.8); not recommended, listed in OQ4-07 |
| m9 stale text and seed ranges | fixed | PLAN s1, Appendix A (scripts are in f58c5c6); seed table s2.10 with disjoint ranges, tranche t <= 9, gold subset moved to 20266100, simulation offsets listed in script headers |
| m10 agreement.py missing from Stage A | fixed | PLAN s11.1 exact specification; s14 A7 |

## Also changed (not in the audit)
- schema v0.3 carried form_version const "0.2"; v0.4 has "0.4".
- In the split-design run, gate_oc_v04.py's first seed choice overlapped its calibration seeds; fixed before
  the committed log was written (offsets listed in the script header).
