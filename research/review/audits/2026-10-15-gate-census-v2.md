```yaml
agent: gate-auditor
date: 2026-10-15
brief: Audit research/review/coverage/census-result-v2.md (random-sample value-rule census, Paper 1 contribution 2, framework-v2 D2)
sources_examined:
  - research/review/coverage/census-result-v2.md (commit d9b1dae)
  - analysis/census/agreement_random.py, summary_random.py and their three committed logs
  - research/review/census/coder-A-claude-r*.jsonl, coder-B.jsonl, coder-B-claude-*.jsonl, census-random-final*.jsonl, disagreements-random*.csv, census-order.csv, fetch-status.json
  - research/review/census/harmonisation-notes.md, adjudication-notes-r001-r088.md, adjudication-notes-r089-r176.md
  - research/review/coverage/census-codebook-v1.md (U definition), census-codebook-v1.2.md (disclosure, B-23 to B-28, item tags)
  - research/review/protocol.md section 10
  - tools/census_sample.py; research/review/screening/records.jsonl, screener-A, screener-B
  - research/ledgers/decisions.jsonl D0015, D0019, D0020; research/review/audits/2026-10-15-novelty-EXP-003.md sections 4-5
coverage: >
  Every number in census-result-v2.md was checked. Both scripts were rerun and diffed against the committed
  logs; all counts, kappas, denominators, the restoration sensitivity and the Wilson intervals were recomputed
  independently from the raw rows with separate code. The sample order was regenerated from the screening
  files. NOT covered: paper texts (research/sources/census-text in the main checkout) were not opened, so whether
  any coded cell is right about its paper was not checked; no clean-room clone (not a release gate).
claims:
  - statement: All agreement figures (15 table rows) reproduce from the raw coder rows
    status: supported
    evidence: rerun of agreement_random.py (log identical except the output file name) plus independent recomputation
    level: E4
    confidence: 0.98
  - statement: The final-row counts reproduce exactly as printed by summary_random.py
    status: supported
    evidence: rerun of summary_random.py (byte-identical to summary-random.log) plus independent recomputation
    level: E4
    confidence: 0.98
  - statement: The F2 denominator (152) follows the governing codebook
    status: contradicted
    evidence: codebook v1.2 B-28 "QL rows enter F2 only"; rank 71 is QL with F2 = T; adjudication notes (78 + 75) and harmonisation notes ("F2 denominator 153") both use 153
    level: E4
    confidence: 0.95
  - statement: The "agreed cells restored" sensitivity restores only cells where A == B
    status: supported (only A == B cells are restored) but incomplete (rank 128 half-restored; 42 of the 45 stated cells affect counts)
    evidence: independent comparison of raw coder rows against final rows and adjudication records
    level: E4
    confidence: 0.95
  - statement: The 15 Codex read-failure ranks are as listed
    status: supported (the text's "14 of those" is wrong; it is 15)
    evidence: coder-B.jsonl notes for ranks 1, 21, 24, 26, 34, 37, 42, 43, 59, 64, 82, 83, 84, 85, 87
    level: E4
    confidence: 0.99
competing_explanations: []
unknowns:
  - Whether the coded cells match the papers (no paper text was opened in this audit).
next_test: {hypothesis: corrected result file reproduces, intervention: apply the corrections listed and rerun summary_random.py, primary_metric: every number in the revised file equals a printed log line, falsifier: any mismatch, gpu_hours: 0}
```

# Gate audit: census result v2 (random sample), 2026-10-15

## Verdict: PASS WITH CORRECTIONS

The data and scripts hold up. Both scripts reproduce the committed logs exactly. Every count, kappa and
Wilson interval in the table matches an independent recomputation from the raw rows. The headline
proportion (0.961 [0.917, 0.982]) stays the same under every variant tested below. Six numbers or
statements in the file are still wrong or overstated. Two process deviations from the decision ledger
are undisclosed, and one disclosure that D0020 requires is missing. All of these can be fixed in the
text or with a ledger row; no recoding is needed. Corrections C1 to C10 must be applied, and C8 and C9
need an orchestrator decision row, before this file can feed the manuscript.

## 1. Reproduction

| Check | Result |
|---|---|
| `python analysis/census/agreement_random.py --out audit-scratch-all.csv` vs `agreement-random.log` | identical except line 19, which names the output file |
| `... --exclude 1,21,24,26,34,37,42,43,59,64,82,83,84,85,87 --out audit-scratch-excl.csv` vs `agreement-random-excl-readfail.log` | identical except the output file name |
| scratch CSVs vs committed `disagreements-random.csv`, `disagreements-random-excl-readfail.csv` | byte-identical; scratch files moved out of the repo; `git status` clean |
| `python analysis/census/summary_random.py` vs `summary-random.log` | byte-identical |
| `tools/census_sample.py` population and seed, recomputed (no file written) | 1106 records (1453 records; both screeners not "exclude"; arXiv ID; every record has both decisions); shuffled order equals `census-order.csv` row for row |

## 2. Number-by-number table

Source codes: AL = agreement-random.log, AX = agreement-random-excl-readfail.log, SL = summary-random.log,
IR = independent recomputation from the raw or final rows (auditor code, this session).

### Sample and process

| Document value | Recomputed | Source | Match |
|---|---|---|---|
| ranks 1 to 176 | final file has ranks 1-176, 176 rows | SL, IR | yes |
| seed 20261015 | `SEED = 20261015`; order regenerates exactly | tools/census_sample.py, IR | yes |
| pool 1106 records | 1106 (1013 include/include, 63 unclear/include, 13 include/unclear, 17 unclear/unclear) | IR | yes |
| population definition (both screeners include or unclear, arXiv ID) | code matches (`!= "exclude"` for both; no record lacks a decision) | tools/census_sample.py, IR | yes |
| stopping rule: coder B's 150th eligible; reached 151 at rank 176 | B cumulative eligible: 150 at rank 175, 151 at rank 176 | IR | yes (see P2) |
| no text: ranks 23, 33, 90, 144 | fetch-status.json: text false for 23, 33, 90, 144 only (first 176) | fetch-status.json, IR | yes |
| Codex ranks 1-91, 86 rows, 19 and 79 failed | coder-B.jsonl: 86 rows, ranks 1-91 minus 19, 23, 33, 79, 90 (23, 33, 90 no text) | IR | yes |
| Opus ranks 92-176 plus 19, 79 | 87 rows (85 + gapfill 19, 79), no overlap with Codex | IR | yes |
| coder A all ranks, Claude Sonnet | 176 rows, `coder: A-claude-sonnet` | IR | yes |
| 172 ranks with text | 172 | AL, IR | yes |
| codebook v1.2 items B-1 to B-28 | B-1 to B-28 present | codebook v1.2 | yes |
| two adjudicators (1-88, 89-176) | two notes files, each with its own output half | adjudication notes | yes |
| harmoniser fixed six readings | six items in "Readings chosen"; 9 F1 cells changed in 3 rows; merged file differs from the halves in exactly those 9 cells | harmonisation-notes.md, IR | yes |
| every disputed cell has a basis | all 130 non-derived CSV cells have an `adjudication` entry | IR | yes |

### Agreement table (v1.1)

All rows match AL and IR to two decimals.

| Field | Doc raw / kappa / n | Recomputed (IR) | Match |
|---|---|---|---|
| eligible, all ranks with text | 0.87 / 0.05 / 172 | 0.8721 / 0.0545 / 172 | yes |
| eligible, excl. 15 read failures | 0.96 / 0.20 / 157 | 0.9554 / 0.2019 / 157 (AX) | yes |
| non-plain (yes/no/unknown), both eligible | 0.81 / 0.65 / 149 | 0.8121 / 0.6476 / 149 | yes (label, C10) |
| non-plain, both determinable | 0.97 / 0.73 / 62 | 0.9677 / 0.7339 / 62 | yes |
| value rule determinable | 0.83 / 0.65 / 149 | 0.8255 / 0.6516 / 149 | yes (label says "not NS"; script and data are "not NS or NA", C10) |
| class A | 0.98 / 0.97 / 62 | 0.9839 / 0.9671 | yes |
| class T | 0.97 / 0.87 / 62 | 0.9677 / 0.8703 | yes |
| class P | 0.98 / 0.93 / 62 | 0.9839 / 0.9319 | yes |
| class S | 0.92 / 0.40 / 62 | 0.9194 / 0.4015 | yes (D0020(4) post-fix value) |
| class G | 0.98 / 0.96 / 62 | 0.9839 / 0.9602 | yes |
| class M | 0.97 / 0.82 / 62 | 0.9677 / 0.8155 | yes |
| F3 | 0.93 / 0.83 / 149 | 0.9262 / 0.8255 | yes |
| F4 | 0.83 / 0.72 / 149 | 0.8322 / 0.7221 | yes |
| F5 | 0.83 / 0.70 / 149 | 0.8322 / 0.7023 | yes |
| F6 | 0.97 / 0.68 / 149 | 0.9732 / 0.6825 | yes (141 of 149 pairs are NA/NA; C10) |

### Reading paragraph

| Document value | Recomputed | Source | Match |
|---|---|---|---|
| 22 eligibility disagreements | 22 | CSV, IR | yes |
| 20 of 22 coder A yes, coder B no | 20 (A yes/B no), 2 (A no/B yes) | CSV, IR | yes |
| 14 of those were Codex read failures (X8/X4) | **15** read failures, all A yes/B no; codes X8 12, X4 2 (26, 42), **NA 1 (rank 84)** | coder-B.jsonl notes, IR | **no (C2)** |
| S weakest letter | S kappa 0.40, next lowest 0.82 | AL | yes |
| 158 field-level rows over 88 ranks | 158 rows, 88 distinct ranks | CSV, IR | yes |

### Result (final rows, v1.2)

| Document value | Recomputed (script) | Under codebook B-28 (QL row 71 in F2) | Source | Match |
|---|---|---|---|---|
| eligible 167 of 172 (X1 4, X0 1) | 167; X1 4, X0 1 | same | SL, IR | yes |
| 15 report no generated-sample metric (F1 NA) | F1_metric NA 15 = **14 F1 NA + 1 F1 QL (rank 71)** | 14 NA, 1 QL | SL, IR, harmonisation notes | **no (C1)** |
| denominator 152 | 152 | **153** (F2-derived rows); 152 for F3-F6 | SL, IR | **deviation (C1)** |
| non-plain or unstated 146/152 = 0.961 [0.917, 0.982] | same | 147/153 = 0.961 [0.917, 0.982] | SL, IR | yes as printed; C1 |
| stated non-plain 96/152 = 0.632 [0.553, 0.704] | same | 97/153 = 0.634 [0.555, 0.706] | SL, IR | yes as printed; C1 |
| U 6/152 | 6 | 6/153 | SL | yes; C1 |
| NS 50/152 | 50 | 50/153 | SL | yes; C1 |
| F3 28/152 = 0.184 [0.131, 0.253] | same | unchanged (QL rows have F3-F6 NA) | SL, IR | yes |
| F4 yes or partial 55/152 = 0.362 [0.290, 0.441] | 49 yes + 6 partial = 55 | unchanged | SL, IR | yes |
| F5 stated among sweeps 20/55 = 0.364 [0.249, 0.496] | 20 stated, 35 not stated | unchanged | SL, IR | yes |
| letters A 33, C 20, G 22, M 12, P 12, S 12, T 13 | same | T 14 (rank 71 is T) | SL, IR | yes as printed; C1 |
| 15 carry +NS | G+NS 11, G+M+NS 3, M+NS 1 = 15 | 15 | SL, IR | yes (12 if C8 restores 114, 120, 141) |

### Sensitivity column (agreed cells restored)

| Document value | Script | Complete restoration (rank 128 in, its agreed F3-F5; F2 S or NS) | Match |
|---|---|---|---|
| 146/152 = 0.961 [0.917, 0.982] | same | 147/153 = 0.961 [0.917, 0.982] (152 convention); 148/154 = 0.961 [0.918, 0.982] (B-28) | yes as printed; C3 |
| 85/152 = 0.559 [0.480, 0.636] | same | 85 or 86/153 (0.556 [0.476, 0.632] or 0.562 [0.483, 0.638]); B-28 only (rank 128 still out): 86/153 = 0.562 [0.483, 0.638] | yes as printed; C1, C3 |
| U 6/152 | 6 | 6 | yes |
| NS 61/152 | 61 | 61 or 62 | yes as printed |
| F3 28/152 | 28 | 28/153 | yes as printed |
| F4 60/152 = 0.395 [0.321, 0.474] | same | 61/153 = 0.399 [0.325, 0.478] | yes as printed; C3 |
| F5 20/60 = 0.333 [0.227, 0.459] | same | 21/61 = 0.344 [0.237, 0.470] | yes as printed; C3 |
| "undoes the 45 cells" | restores 43 recorded A == B cells: 42 that affect counts + F1_value at 155; F1_value at 44 and 172 not restored (recorded A and B strings differ) | n/a | **partly (C3)** |
| "mostly the new codes C and +NS" | of 45 reopened cells, 25 are F2; 20 of those 25 are new C (12) or new +NS (8); 20 of 45 overall | n/a | **no (C4)** |
| "under v1.2 triggers" | 3 of the 45 (114, 120, 141) have no trigger in the coders' notes; they were kept under harmonisation clause (b) | harmonisation-notes.md item 6 | **no (C8)** |
| headline does not move | 0.961 in every variant | IR | yes |

### Wilson intervals (check e)

Recomputed with z = 1.959964 and the standard Wilson formula. All eight printed intervals match to three
decimals: 146/152, 96/152, 85/152, 28/152, 55/152, 20/55, 60/152, 20/60. The rounded draft wording
"96 percent, 95 percent interval 92 to 98" matches 0.961 [0.917, 0.982].

### Draft wording paragraph (check f)

| Claim | Check | Status |
|---|---|---|
| 146 of 152 ... 96 percent, 92 to 98 | matches SL | supported as printed (147 of 153 under B-28, C1) |
| "other than plain sampling at temperature 1 or do not state the rule" | U in v1 = values sampled at temperature 1, no truncation, no guidance, stated | supported |
| 18 percent report diversity or entropy | 28/152 = 0.184 | supported |
| "of the 55 that sweep the number of steps, 20 state ... held fixed" | 55 = F4 yes 49 + partial 6; B-23 counts steps, NFE or tokens per step, and partial = exactly two settings | numbers supported; wording broader than the code (C7) |
| Credit "(D0019)" | D0019 requires "a further instance of sampling-dependent evaluation (OpenReview Gq4yt8pxRo), not a first statement; credit list as in the report"; the report's section 4 item 6 lists Gq4yt8pxRo, Evaluation Illusion 2606.29228, FID Lottery 2606.20536, CaRE 2607.24763 | **credit not stated; only a ledger ID (C6)** |
| "quantifies it for diffusion language models" | does not claim a first statement | acceptable |

## 3. Script checks

**(a) agreement_random.py.** Cohen's kappa is computed correctly: observed agreement, chance agreement from
the product of marginals over the union of categories, and (po - pe) / (1 - pe). `letters()` splits on "+",
so the D0020(4) bug (G+NS read as containing S) is fixed. `elig()` maps Y/yes/N/no, and no unmapped value
survives the NO_TEXT filter. `norm()` lower-cases F3 to F6. Rows with coder value "S+U", "NS+G" and so on
give the correct derived class. The disagreement CSV compares raw F2 strings, but no order-only difference
occurs, so the 158 count is unaffected. Hand spot-check of 10 ranks (2, 3, 5, 19, 50, 79, 92, 120, 151, 170):
in every case the raw A and B values and the CSV rows (or their absence) agree with the script's treatment.
One labelling issue: in the 149 both-eligible rows, F2 = NA (no metric) occurs 10 times for A and 12 for B.
These are pooled with NS as "unknown" and as "not determinable", and they inflate F3 to F6 agreement through
NA/NA pairs (F6: 141 of 149). See C10.

**(b) summary_random.py denominators.** "Sweeps = F4 yes or partial" is implemented correctly. The F2 to F6
denominator is "eligible and F1_metric not NA". By codebook B-28 (which says "F1_metric NA when QL"), that
filter wrongly drops QL rows from F2. Only rank 71 is affected. The unused variable `met` tests
`F1_task == "ql"` where it should test `F1_value == "QL"`; this looks like an abandoned attempt at the B-28
rule. The log line "F1 NA: 15" counts F1_metric NA, so it includes the QL row.

**(c) Restoration.** `restored()` only ever restores cells where coder A equals coder B. I checked every
restored cell against the raw coder rows and found no false restore. The record's A/B for 27, 28, 36, 38
and 39 eligibility reads "no (X7)" against a raw "no"; this does not matter because those cells are
disputed. The restoration is incomplete in two ways:
1. Rank 128. Eligible and exclusion code are restored to the agreed yes/NA. The cells set to NA by the
   B-27 coupling are not restored: F1 (each coder had one), and F3 no, F4 yes, F5 stated, all three agreed
   but missing from `adjudication`. The row therefore counts as eligible but drops out of the
   denominator. This is why the log shows eligible 169 with F1 NA 17. Rank 165 is restored correctly,
   because both coders had F1 = NA.
2. Of the 45 reopened cells, 3 are F1 values. Two of them (44, 172) are not restored because the recorded
   A and B strings differ. Counts are unaffected, but "undoes the 45 cells" is not what the code does.

**(d) Read failures.** All 15 listed ranks are Codex rows whose `notes` report a file or tool access
failure, and coder A coded all of them eligible. Exclusion codes: X8 at 1, 21, 24, 34, 37, 43, 59, 64, 82,
83, 85 and 87; X4 at 26 and 42; NA at 84. No other Codex row reports a read failure. The other 5 Codex
"no" rows are X7 (27, 28, 36, 38, 39), with substantive reasons.

**(e) Wilson.** Correct (section 2).

**(f) Draft wording.** See the table above and corrections C1, C6 and C7.

## 4. Required corrections (exact fixes)

**C1 (denominator, B-28).** In "Result", replace "Of the eligible, 15 report no generated-sample metric
(F1 NA); the reporting fields are computed on the other 152." with one of the two options below.
(i) Preferred, because it follows the governing rule and the adjudicators' and harmoniser's own tallies
of 153: change `summary_random.py` so that F2-derived quantities include rows with `F1_value == "QL"`
while F3 to F6 keep excluding them, and remove the dead `met` line. Rerun, and then update the file:
"14 report no generated-sample metric (F1 NA) and 1 shows samples only (QL, rank 71); value-rule
quantities are on 153, reporting fields F3 to F6 on 152". Headline 147/153 = 0.961 [0.917, 0.982]; stated
non-plain 97/153 = 0.634 [0.555, 0.706]; U 6/153; NS 50/153; T 14; sensitivity stated non-plain
86/153 = 0.562 [0.483, 0.638], NS 61/153. Draft wording: "147 of 153".
(ii) Keep 152, but write "14 report no generated-sample metric and 1 (rank 71) only shows samples (QL);
both are left out, a deviation from codebook B-28, which keeps QL rows in F2", and log that deviation as
a decision row.

**C2.** Reading paragraph: change "14 of those were Codex failing to read the paper (placeholder X8/X4
codes ...)" to "15 of those were Codex failing to read the paper (placeholder X8 or X4 codes, or none at
rank 84; adjudicated from the paper)".

**C3 (sensitivity scope).** Either extend `restored()` so that rank 128 re-enters with the coders' agreed
F3/F4/F5 and either coder's F1 and F2, reporting the F2 = S and F2 = NS variants, or add this sentence:
"Rank 128 (both coders eligible, adjudicated X1) is restored to eligible but stays out of the denominator,
because its F1 and F2 were disputed and never adjudicated; including it gives F4 61/153 = 0.399
[0.325, 0.478], F5 21/61 = 0.344 [0.237, 0.470], headline 147/153 = 0.961, stated non-plain 85 or
86/153." In either case, replace "undoes the 45 cells" with "undoes the 42 count-relevant cells among the
45 agreed cells that adjudication reopened (the other 3 are F1 values)".

**C4.** Replace "(mostly the new codes C and +NS)" with "(25 are F2 codes, 20 of them the new C or +NS;
the rest are F4, F5, F6, eligibility, exclusion and F1 cells)". 11 of those changes (NS to C at 10 ranks,
NS to S at 51) account for the whole drop from 96 to 85 in stated non-plain.

**C5 (provenance sentence).** "Every number below is printed by ..." is false for several numbers: 1106,
86 rows, ranks 19/79, 20 of 22, 15 read failures, 88 ranks in the CSV, 45 cells, six readings, 15 gain
rows and 4 rows (reading 2). Replace it with "Counts and intervals are printed by ...; process counts
come from the named files (census-order.csv, coder rows, disagreements-random.csv,
harmonisation-notes.md)".

**C6 (credit, D0019).** Replace "(D0019)" with the sources: "made for other metrics before, for example
for bias metrics in text diffusion language models (Sampling-dependent fairness, OpenReview Gq4yt8pxRo),
and in Evaluation Illusion (2606.29228), FID Lottery (2606.20536) and CaRE (2607.24763)". Keep "this
census quantifies it" and do not call it a first statement. The novelty report holds Gq4yt8pxRo at E1
(abstract only), so the paper may not attribute anything to it beyond its abstract.

**C7.** In the draft wording, change "of the 55 that sweep the number of steps" to "of the 55 that report
the headline metric at two or more step settings (steps, NFE or tokens per step)".

**C8 (D0020(5) deviation, needs a decision row).** D0020(5) and the v1.2 disclosure say agreed cells
change only on a v1.2 trigger in a coder's own notes. Harmonisation item 6 clause (b) added a second route
and kept three agreed G cells as G+NS with no note trigger (114, 120, 141). The auditor cannot waive this.
Either the orchestrator or the user logs a decision that amends D0020(5) and the file says so, or the
three cells go back to G. Effect: +NS goes from 15 to 12; non-plain, letters and every proportion stay the
same. The file's "under v1.2 triggers" also needs to say "42 under a trigger in the coders' notes, 3 under
harmonisation clause (b)".

**C9 (D0020(3) disclosure missing).** D0020(3) says "the gap rulings B-10, B-19 and B-24 are disclosed
with their effect on counts". The v1.2 disclosure adds "A count that moves because of a [gap] item is
reported with that item named". The result file names none of these. Add a short paragraph or table that
gives, for B-10, B-19 and B-24 and for every other [gap] item that decided a final cell (B-3, B-6, B-8,
B-9, B-13, B-15, B-17, B-18, B-21, B-22), the ranks it decided (already listed in the two adjudication
notes) and how much each headline count moves. Note that D0020 calls B-10 a gap ruling while the codebook
tags it [literal]; say which tag applies.

**C10 (agreement labels).** Change the row "value rule determinable (not NS)" to "(not NS or NA)". Add one
sentence: "In the 149 both-eligible rows, F2 = NA (no generated-sample metric) is pooled with NS as
unknown (10 rows for coder A, 12 for coder B); F3 to F6 agreement includes NA pairs (F6: 141 of 149)".

**C11 (process wording).** In Process step 3, "from the coders' ambiguity reports without opening row
files or papers" leaves out inputs that the codebook itself lists. Change it to "from the coders'
ambiguity reports, the disagreement list and the agreement log, without opening row files or papers".
The disagreement list holds coder values for the disputed cells.

**C12 (limits wording).** Change "Reading 2 ... moves 4 rows between G and G+NS" to "Reading 2 keeps 91,
114, 120 and 141 at G+NS; the alternative reading would make them G (+NS 15 to 11); the non-plain count
does not change".

## 5. Process concerns (no change to the verdict)

- P1. Every coder after Codex, both adjudicators and the harmoniser are Claude models, and the
  adjudicators and harmoniser were not blind. The file discloses that no human has coded this sample. The
  professor's review requirements ask for reviewer agreement, so the paper cannot claim human-level
  reliability.
- P2. The stopping rule counted coder B's raw eligibility, which includes the 15 Codex read failures as
  "no". Under final eligibility the 150th eligible paper falls at rank 157. The sample is still the first
  176 ranks of a random order, so the proportions are not biased. The sample is still 19 ranks larger
  than intended, and the stopping time depended on a tool failure. Worth one sentence in the limits.
- P3. The 15 read-failure ranks are effectively single-coded by coder A plus the adjudicator.
- P4. `research/review/protocol.md` section 10 still reads "None yet." above the 2026-10-15 amendment.
- P5. CLAUDE.md says "No number in any document unless it is in a runs/<exp-id>/ directory". The census
  numbers live in `analysis/census/*.log`, not under `runs/`. Either the orchestrator records that
  analysis logs count as a run directory for the review, or the logs are copied into a run directory.
- P6. The label "stated non-plain value rule" (96) includes 20 C rows and 15 +NS rows whose base token
  rule is unstated. This is correct under B-28 (C is a stated selection rule), but the paper should define
  it where the number first appears.
- P7. No progress.md checkbox exists for this audit, so nothing was ticked. No ledger rows were added.
