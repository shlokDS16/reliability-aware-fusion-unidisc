# Open questions for the human author: extraction and appraisal form v0.3 (2026-10-20)

Each item names the gap, the options with their cost where one applies, and where the plan uses the answer.
**Decision row** = needs a row in `research/ledgers/decisions.jsonl` (entered by the orchestrator) before the
stage named. The drafting agent decided none of them. Token figures are inference (E0) from the per-record
table of `analysis/extraction/cost_options.py` (log `cost_options-log.txt`); Stage A replaces them with
measurements. v0.2 items not repeated here stay open as written in OPEN-QUESTIONS-v0.2.md (list in part E).

## A. Scope (user decision of 2026-10-16)

**OQ3-01 Which reading of "extract RQ data on a stratified sample + all multimodal" (decision row, before
Stage A).** The user's words (research/progress.md l.279-280) fix where RQ data are extracted. They do not
say whether the light blocks (study fields, design, census, claim types, appraisal, headline numbers) are
"RQ data". Both readings are allowed by the words; the plan does not choose (plan s2.1).

| | Option 1 | Option 2 |
|---|---|---|
| What is extracted where | L + Q + H on all 608 includes; block K on all multimodal (C1 53 + C2 108) + a stratified sample of 120 from frame R (435) | every block (L, Q, H, K) on all multimodal + the sample (281 records) only; the other 327 includes keep their screening data only |
| RQ1 counts (class, year) | census over 608 | census over C1 + C2, weighted estimate over frame R |
| Census extension (D0011, block F on every include) | met | not met; variant 2+F (block F alone on the other 327, +4.9M-8.2M) meets it |
| Appraisal (protocol s6, "every included study") | met | deviation (281 of 608) |
| Multimodal definition | the screening rule now, plus the light-pass completion rule (S02) | the screening rule only (no light pass on the others) |
| MIN tokens | 53.2M-89.3M | 38.0M-66.5M (2+F: 42.9M-74.7M) |
| with block F double on the rest (REC) | 70.1M-113.9M | 45.8M-77.9M |
| with block F and QA double on the rest (FULL) | 89.8M-145.0M | 54.9M-92.2M |

Difference at MIN: 15.2M-22.8M. All rows include the pilot (Stage A 12 + gate 60: 12.7M-22.3M). The draft
scope row (plan s2.9) is worded as the user's choice with both options; it is not entered.

**OQ3-02 Package (decision row, with OQ3-01).** MIN (second reading on a stratified 10 percent only), REC
(plus block F double-extracted on every other record of the chosen option), FULL (plus a second QA rater).
Costs in the table above. v0.2 recommended REC under Option 1; that recommendation is withdrawn here because
the package depends on OQ3-01.

**OQ3-03 What "all multimodal" means (decision row, with OQ3-01).** Options: (a) C1 only (i1 in {b, ab}: 53);
(b) C1 plus C2 by the committed screening rule of `analysis/extraction/strata.py` (C2 = i1 = a, not
nonlang_only, and the T1 screeners' field mm = "multimodal": 108; v0.2's title regex gave 52 and missed the
13 records the red-team named, all now C2). Under Option 1, block K on C2 costs 108 x 40k-80k = 4.3M-8.6M;
under Option 2 C2 costs 108 x 78k-135k = 8.4M-14.6M. RQ5 uses C1 only in both.

**OQ3-04 Human check of the rule's borderline ids and of duplicate works (before any draw; about 1 hour).**
strata.py prints 20 borderline ids: B1 split screeners, decided by the keyword rule (M02955 C2; M18118,
M18656 frame R); B2 mm "multimodal" with no keyword in title or abstract (15: M00285, M05642, M05663, M07324,
M09298, M09321, M10881, M12175, M13247, M14560, M14706, M14711, M16251, M16730, M18406); B3 mm text or other
with a keyword in the title (M13760, M15613). And 6 duplicate-work candidates (M03951/M16269, M07769/M16343,
M09657/M15091, M14067/M14568, M14370/M14372, M16133/M16134). Please confirm or override: overrides go to
`analysis/extraction/strata-overrides.jsonl`, confirmed duplicates to `duplicate-works.jsonl` (the second id
is then a report of the first id's study and leaves the frames). Nothing is applied until these files exist.

**OQ3-05 Sample size from frame R.** Frame R is now 435 (v0.2: 491). 95 percent half-widths of a study-level
share (strata.py): n 90: 0.092 whole frame, 0.130 in a subgroup at 50 percent; n 120: 0.076, 0.108; n 150:
0.065, 0.092. Each 30 records cost 1.2M-2.4M under Option 1 and 2.3M-4.0M under Option 2. Class-specific
cells at 10-20 percent prevalence stay descriptive unless the census columns or the targeted extension cover
them (red-team F-mi4). Recommendation unchanged: 120.

**OQ3-06 nonlang_only includes (12).** Option 1: L, Q and H, no K, separate row. Option 2: no extraction
(not multimodal, not in frame R). Please confirm which applies with OQ3-01.

## B. Gate

**OQ3-07 Gate size (decision row, before Stage B).** The joint simulation (`gate_oc.py`, log
`gate_oc-log.txt`) gives, with every quantity at its good level: n 30: 0.670; 36: 0.808; 45: 0.915; 54:
0.950; 60: 0.973; 72: 0.984, and at most 0.080 when any one of the seven weakest quantities is at its bad
level. n 60 stays at or above 0.889 in every sensitivity case run (higher intra-record correlation, fewer
units per record, more skewed unit counts; plan s10.6). n 45 meets the 0.85 target at the baseline, but its
sensitivity cases were not run in the committed log, and the baseline margin is small. Each 15 gate records
cost 2.6M-4.7M. Recommendation: 60 (or ask for the n = 45 sensitivity run before deciding).

**OQ3-08 Gate rule, good and bad levels (decision row, before Stage B; frozen before the first gate record).**
Plan s10.4: 15 criteria, each "lower 90 percent bound at or above the bad level" (QA kappa: at or above 0.45;
value agreement: at or above 0.86), anchors identical in at least 43 of 60; per-field flags, kappa, AC1 and
QA-score raw agreement reported but not gating; schema validity is a process requirement. Please approve or
change the good and bad levels in the s10.4 table now; they cannot change after the gate row is entered.

**OQ3-09 Budget ceiling for G7 (decision row, with OQ3-01).** v0.3 makes G7 a budget check: the projected
total from Stage A and Stage B means must not exceed the budget you approve with the scope row. Please give
that number (for example the MIN or REC total of the chosen option, or a fixed ceiling).

## C. Unit rules

**OQ3-10 Suite rule (decision row, with s13 row 3).** A group whose table has more than 10 benchmark rows and
prints an average over them records only the average (LLaDA2.1: 1 instead of 33 RQ2 units per table). It
narrows protocol s5 further. Options: approve; or record every benchmark (workload of technical reports grows
by an order of magnitude); or a different threshold.

**OQ3-11 Training-free method papers.** Other decoders on the same base model become one replacement group
with credited_ablation true, never baselines (U6a; red-team fix). It counts them in RQ4 and QA7. Approve.

**OQ3-12 Figures.** Numbers printed inside figures (data labels) are not extracted; figure groups are
figure-only (U10). Approve, or allow data labels with a figure evidence kind (needs a validator design).

**OQ3-13 F1 readings C-F1a to C-F1e (gate-auditor check, before Stage A).** The five readings in the brief's
census block resolve the red-team's F1 ambiguities. They must be checked against census codebook v1.2 and the
harmonisation notes; if any changes a census coding of the 176-rank sample, it needs a codebook version and a
note in the census section.

**OQ3-14 S14 anchored on the F1 unit (decision row, with s13 row 12).** QA3-QA6 are scored on the F1 table and
a baseline chosen by rule, not on the first comparative claim (v0.2). This makes the main comparison
reproducible (gate G5) but moves it away from claims that name a comparator. Approve or keep v0.2's basis.

**OQ3-15 Long-tail K workload.** The worked examples give 18 to 130 K units per record (FDM 130). The workload
rule (plan s5.7) acts on the median (30). Options: (a) keep; (b) add a per-record cap, for example the first
40 K units in reading order, main text first, with the rest listed as uncounted; (c) decide after Stage A.
Recommendation: (c).

## D. Process

**OQ3-16 The T1 gate.** Gate re-audit 1 (2026-10-20) is FAIL with every remaining blocker needing the human
author; Stage A cannot be drawn before a pass (plan s14 A1). The three T1 records pending screener B (M13184,
M15873, M17195) are classified by the same rules if they become includes; the draft row carries the
allocation rule, not the numbers.

**OQ3-17 Red-team review of v0.3 before Stage A.** The agent definition requires the derivation to go to
red-team before lab-engineer builds the tools. The validator tests (35 cases) and the rules U1-U14 are the
parts to attack first.

## E. Still open from v0.2 (unchanged)
OQ2-07 adjudicator route (reconfirm no extra spend for claude-fable-5-1); OQ2-08 public versions of
anonymous submissions (fetch and EQ session; at most 287 records under Option 1, 118 under Option 2); OQ2-09
QA1 link check; OQ2-10 human gold subset (now 6 of the 60 gate records, 2 per stratum, seed 20262100);
OQ2-11 QA8 status; OQ2-12 CT publication rule; OQ2-15 lookups; OQ2-16 aggregate-column rule; OQ2-17 second
model family; OQ2-18 protocol freeze; OQ2-19 independent groups for pooling; OQ2-20 census test-retest;
OQ2-21 task families and state spaces; OQ2-22 one study type; OQ2-23 version extracted. v0.2's OQ2-01 to
OQ2-06, OQ2-13 and OQ2-14 are replaced by OQ3-01 to OQ3-09.
