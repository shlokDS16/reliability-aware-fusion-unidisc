# Response to red-team audit 2 of extraction form v0.2 (2026-10-20)

Audit: `research/review/audits/2026-10-20-redteam-extraction-v0.2.md` (1 critical, 7 major, 13 minor, 3
blocking preconditions). Revised files: EXTRACTION-PLAN-v0.3.md (PLAN), extraction-schema-v0.3.json,
extractor-brief-v0.3.md (BRIEF), OPEN-QUESTIONS-v0.3.md (OQ), worked-examples-v0.3.md (WE); scripts and logs
in `analysis/extraction/` (strata.py, gate_oc.py, cost_options.py, flag_thresholds.py, make_schema_v03.py,
build_validator_tests.py, validator-tests.jsonl). The scripts are written but not committed (the brief
forbade commits); they are unreviewed until the next red-team pass. Status words: **fixed** (the finding's
rejection test now passes on the artifact named), **partly** (what remains is named), **rejected** (with the
reason). No finding is rejected outright; three fixes depart from the red-team's proposal and say why.

## Critical

**F-CR1 Gate fails a good instrument about 80 percent of the time. Fixed.**
- Good and bad levels are written per quantity (PLAN s10.4 table).
- G6 is diagnostic: flags trigger rule revision and production re-measurement, never FAIL. The flag line is
  calibrated at 0.85 with a false-flag rate of at most 0.01, as proposed: c(15) 8, c(20) 12, c(30) 20,
  c(60) 43 (`flag_thresholds.py`).
- G5 is one count over the gate: both the F1 unit and S14 identical. With S14 anchored on the F1 unit (s5.6),
  S14 identity mostly implies F1-unit identity, so two counts would test nearly the same thing twice. Line:
  43 of 60, the smallest count with P(pass | 0.60) <= 0.05.
- One committed simulation of every hard criterion together (`gate_oc.py`; three equal strata; record
  heterogeneity ICC 0.10; copula across metrics; negative-binomial unit counts; the same stratified cluster
  bootstrap as the gate). The result is in PLAN s10.6. A gate of 30 does not meet the target (0.670), so the gate
  is raised to 60 (3 x 20), as the fix allowed.
- Departure: the red-team suggested G5 at 22 of 30, or S14 and F1u on 45 records with L+Q only. A separate
  45-record L+Q sample adds a third reading stage; raising the gate to 60 records meets every criterion at
  once at a cost of 5.3M-9.3M more than n = 30 (OQ3-07 gives n = 45 as the cheaper option and its weakness).

## Major

**F-MA1 Unit keys not reproducible. Fixed in the specification; Stage A tests it.**
Rules U1-U14 (PLAN s5, BRIEF block K and G1) answer the eight sources of divergence:
(i) anchor without or with several defaults: U3's ordered clauses, ending in the first own arm, with
anchor_rule recorded; (ii) replacement against baselines in training-free papers: U6a (one replacement
group, credited); (iii) "already recorded": the clause is deleted (U1), duplicates are removed by script
(U12); (iv) column_printed in the K key: removed; the K key is (group, benchmark_id, metric_id,
condition_printed, split) with a written composition rule (U9); (v) focal model of analysis and benchmark
papers: U2c (the diffusion model in the most main-text results tables and figures); (vi) anchorless factor
groups: U3 benchmark clause (stated default, else null) and U6c (main text only unless the factor is absent);
(vii) row-label extent: U11 plus the validator's row-start and row-width checks (tests V26-V28); (viii)
rq_class: derived from factor_type by script and out of every key (U8, U13).
Departures: the red-team's "already recorded = same label and same values" is replaced by script
de-duplication on contrast values, because label equality fails on the M13864 case it was meant to fix
("Dream-v0-Instruct-7B" against "Dream-v0-Instruct-7B (rate=1)"). The group key keeps where and adds the
second-factor level beside the arm-label Jaccard, because FDM Table 2 has two groups per base model that
share every other key part.
WE gives one expected unit list per test paper: FDM 25 groups / 130 K units, Muddit 8 / 21, TrustLDM 9 / 32,
M13864 6 / 18, LLaDA2.1 10 / 66, with the remaining judgement only on attributes (factor_type) measured by
M-class. The rejection test (F1_G below 0.6 on Stage A) is kept as the falsifier.

**F-MA2 Two gate metrics are 1 by construction. Fixed.** rq_class is out of the group key (U13), so M-class is
measured on groups matched without it (gate line LB90 >= 0.65). value_printed is out of the H key: an H unit
is now located by its number token in the text, so H value agreement would still be trivial; it is replaced by
an H-attribute block (value_type, arm_role, metric_kind on matched H units) in G3, and M-val is computed on K
values only, where a value can sit in the wrong row, row group or column.

**F-MA3 Kappa criteria without bite. Fixed.** The namespaced pooled kappa and the AC1 switch are dropped from
the gate (implied by the raw-agreement bound, and unable to fire). Per-field kappa and AC1 are reported. The
QA criterion is the mean of the per-item linear-weighted kappas (QA1-QA7, QA9), not pooled; its line (lower
bound >= 0.45 for a bad level of 0.40) comes from the simulation, where the percentile bootstrap under-covers.
QA-score raw agreement is reported, not gated (it is a function of the sub-items, which G3 gates).

**F-MA4 Validator does not verify columns, arms in columns groups or row groups. Fixed in the specification
(the tool is not built).** PLAN s6.3: tables are described once (header, leaf-column map, column roles, row
groups and their role); cells are lists with one element per table cell; checks map_not_in_header,
column_order_mismatch (single-level headers), column_mismatch, row_width_mismatch, row_start_missing,
row_group_missing, rowgroup_benchmark_mismatch, second_factor_mismatch, benchmark/metric/condition
mismatches and arm_column_mismatch; rows that cannot be aligned (incomplete rows, declared blanks, two-level
headers whose order cannot be confirmed) get column_unverified and go to the second reader with certainty.
Tokenisation N1-N6 removes the three false rejections the red-team found (glued label, glued arrows,
hyphen-split header) and the page-footer number. Tests as data: `analysis/extraction/validator-tests.jsonl`,
35 cases, including the red-team's cases (a) V02-V03, (b) V05, V09-V10, (c) V12-V13, V15-V16, (d) V17-V18,
V20, (e) V21, V23, the false rejections V07, V08, V22, and the label-extent case V26-V27. Fixtures are line
ranges of the screened texts pinned by sha256.

**F-MA5 C2 title regex misclassifies. Fixed (rule); the borderline list needs one human check.** The red-team
read T1 as recording only i1 and nonlang_only. The decisions file does, but every T1 screener row also carries
the field `mm` ("text", "multimodal", "other"; criteria v1.6 screener brief), coded by both screeners and by
the adjudicator. `strata.py` derives multimodal from it: C2 = i1 = a, not nonlang_only, mm "multimodal" (the
adjudicator's value where it ruled, else the agreed A and B value), and only for split records the
word-bounded keyword list over title and abstract. C2 is 108 (v0.2 regex: 52; the regex run on full titles
gives 53, because v0.2 had no titles for the 15 U- and R-prefixed records). All 13 misses the red-team named
are C2 (mm "multimodal" by both screeners or the adjudicator); M16622 and M13760 are frame R (mm "text");
M15684 is C2 (mm "multimodal"); R0963 (Bernini, video) is C1. The 20 borderline ids and the 6 duplicate-work
candidates are printed for one human check (OQ3-04). The red-team's preferred two-phase draw (multimodal by
the light-pass S02) is possible only under scope Option 1 and stays there as the completion rule; under
Option 2 there is no light pass on non-sampled records, so the draw must rest on screening data.

**F-MA6 Scope reading not confirmed. Fixed.** PLAN s2.1 and OQ3-01 present the two readings the user's words
allow (light blocks on all includes, or on the sample and all multimodal only) with costs from one table; the
plan does not choose. The draft row (s2.9) is worded as the user's choice and lists both options.

**F-MA7 Cost: G7 does not protect the budget; bases inconsistent. Fixed as specification (figures remain
E0).** One per-record table (`cost_options.py`) is used for every component (EC 20k-40k per adjudicated
record everywhere; component 4 counts the same 62 ER records as component 3; the second-rater option sums its
parts). The K base is widened to 40k-80k because v0.3 records every qualifying table (WE: 18-130 units per
record). G7 is a budget check against the total the user approves, from Stage A and Stage B means, not a
median ceiling, and its failure triggers the fallback ladder, not FAIL.

## Minor

| Finding | Status | Where |
|---|---|---|
| F-mi1 decisions hash | fixed | PLAN header cites sha256 962e3171... (882 rows, 608 includes); strata.py prints it |
| F-mi2 scripts not in the repository | fixed (written, commit pending) | analysis/extraction/strata.py with strata-log.txt; gate_oc.py with gate_oc-log.txt; cost_options.py; flag_thresholds.py |
| F-mi3 seed collisions | fixed | PLAN s2.10: one table, disjoint blocks per purpose (2026 11 00 to 2026 21 00); Python 3.14.3 pinned |
| F-mi4 precision of class-specific cells | fixed | PLAN s2.5: such frame-R cells are descriptive unless census columns or the targeted extension cover them |
| F-mi5 ynun nulls not tied to n | fixed | schema v0.3: if/then on QA4-QA6 (n yes: a-d null; n no: a-d answered) |
| F-mi6 flags undefined for Jaccard fields | fixed | flags only for binary-credit fields; set fields reported with bootstrap intervals (PLAN s10.3) |
| F-mi7 claim matching by sentence identity | fixed | M-CL matches claims whose prose quotes overlap by at least half of the shorter quote's tokens in the normalised text (PLAN s10.3) |
| F-mi8 hyphen handling differs | fixed | N2 accepts both the hyphen-kept and the de-hyphenated join, as quote_check does (V29, V30) |
| F-mi9 figure-only and unreadable values not exempt | fixed | PLAN s6.4: no value checks for "figure-only" in a figure_only unit; "unreadable" needs a cell entry locating the row, no value check (V31, V32) |
| F-mi10 duplicate works in the frame | partly | strata.py lists 6 candidate pairs (including the three named); a pair is applied only after a human confirms it (OQ3-04) |
| F-mi11 pending T1 records change the allocation | fixed | the draft row carries the allocation rule (largest remainder, proportional), not the numbers |
| F-mi12 targeted-extension records in estimates | fixed | same rule as completion records: census of the cell, outside the weighted frame-R estimates (PLAN s2.7) |
| F-mi13 provenance for cited recipes | fixed | inherited-from-cited-method (schema prov; BRIEF design block) |

## Claimed v0.1 fixes the audit found partial

| v0.1 | Audit | v0.3 |
|---|---|---|
| C2 unit keys | partly | F-MA1 above |
| C3 scope | partly | F-MA6 above |
| M4 QA sub-items | partly | F-mi5 above |
| M11 column attribution | not real | F-MA4 above |
| M17 cost | partly | F-MA7 above |
| m3 figure-only values | partly | F-mi9 above |

## Blocking preconditions (process; not in this agent's power)
1. T1 gate FAIL (re-audit 1, l.47): open; PLAN s14 A1.
2. No decision row of PLAN s13 entered (last ledger row D0034): open; PLAN s14 A2-A3, B2.
3. Tools of s11 not built: open; PLAN s14 A4-A5, B3-B4 list what Stage A and Stage B each need.
