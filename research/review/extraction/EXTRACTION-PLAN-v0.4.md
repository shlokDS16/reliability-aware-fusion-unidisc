```yaml
agent: method-architect
date: 2026-10-20
brief: revise the extraction and appraisal instrument from v0.3 to v0.4 after red-team audit 3 (Paper 1); gate anchors and the K attributes that set sign and poolability, make the gate robust to the intra-record correlation, one anchor reading, an uncontaminated brief, a match rule for unmapped strings, the multimodal construct as options, agreement.py specified; no extraction run, no sample drawn
sources_examined:
  - research/CONTRACT.md
  - research/review/audits/2026-10-20-redteam-extraction-v0.3.md (all 16 findings)
  - research/review/extraction/EXTRACTION-PLAN-v0.3.md, extractor-brief-v0.3.md, OPEN-QUESTIONS-v0.3.md, worked-examples-v0.3.md, RESPONSE-TO-REDTEAM-v0.2.md (read in full); extraction-schema-v0.3.json (descriptions, form_version, group fields); EXTRACTION-PLAN-v0.2.md (K15, G13, G16, A10 definitions; tool and lookup paths, grep only)
  - analysis/extraction/gate_oc.py, strata.py, cost_options.py, make_schema_v03.py (read; unchanged)
  - analysis/screening/ft-t1/t1-decisions-all.jsonl (sha256 962e3171...), FA-/FB-/FC- screener rows (fields mm, i1, nonlang_only, note)
  - research/sources/md/fulltext-pymupdf/: M12766 l.870-990 (Tables 2-5), M08100 l.720-765 and l.1027-1110 (Tables 2 and 4) and the Table 1 and 2 rows of seven benchmarks; all 608 include texts by script (brief_contamination.py, multimodal_options.py)
coverage: >
  Every number below comes from a script in analysis/extraction/ run on 2026-10-20, with its log beside it
  (Appendix A). Not read: the five worked-example papers beyond the lines listed (their v0.3 unit lists are
  kept as written), the 108 C2 records' full texts (the construct options use the red-team's screener-note
  reading, E1, plus a keyword search), protocol.md. Token figures are inference (E0). No ledger row was added:
  the brief allows writes only in research/review/extraction/ and analysis/extraction/.
claims:
  - statement: With the four new criteria (19 in all), a 60-record gate passes an instrument at every good level with probability 0.866 at ICC 0.10 and 0.660 at ICC 0.20; any one quantity at its bad level passes with probability at most 0.076.
    status: supported
    evidence: analysis/extraction/gate_oc_v04.py, log gate_oc_v04-log.txt sections A-B (seed 20263000)
    level: E3
    confidence: 0.8
  - statement: Design B-IP (60 records, ICC re-estimated on them, extension to at most 120) passes a good instrument with probability 0.860-0.935 for true ICC 0.05-0.30 and a one-bad instrument with probability at most 0.070.
    status: supported
    evidence: analysis/extraction/gate_adaptive_v04.py, log gate_adaptive_v04-log.txt (seed 20263950)
    level: E3
    confidence: 0.75
  - statement: The percentile bootstrap upper bound of the ICC from 12 Stage A records covers the true value in only 0.34-0.54 of cases at ICC 0.20-0.30; the Neyman bound covers in 0.81-0.89.
    status: supported
    evidence: analysis/extraction/icc_check.py, log icc_check-log.txt
    level: E3
    confidence: 0.85
  - statement: The session text of v0.4 (brief text blocks and schema descriptions) contains none of 17 strings taken from drawable papers that v0.3 contained, and no example string specific to 1-5 include texts other than the instrument's own field ids and codebook terms.
    status: supported
    evidence: analysis/extraction/brief_contamination.py, log brief_contamination-log.txt
    level: E3
    confidence: 0.9
  - statement: The v0.4 value-identity clause gives one anchor for Muddit Tables 3 and 4 (0.6; Joint training) and for both LLaDA2.1 Table 4 groups (w/o MBE).
    status: supported
    evidence: worked-examples-v0.4.md s2 and s5 (M12766 l.870-949; M08100 l.720-948, l.1046-1110)
    level: E2
    confidence: 0.8
competing_explanations:
  - The real ICC may be below 0.10, in which case n = 60 suffices and B-IP stops at 60; or above 0.30, in which case even 120 records leave P(pass | good) below 0.85 (0.769 at 0.40).
unknowns:
  - real ICC, units per record, agreement on the new K attributes (Stage A, then the gate's first 60 records)
  - which multimodal construct the human author chooses (OQ4-03)
next_test: {hypothesis: "two extractors following brief v0.4 agree on group anchors and K attributes as well as on keys", intervention: "Stage A (12 records; falsifier on the 7 drawn), then gate design B-IP", primary_metric: "F1_G on the 7 drawn Stage A records; the 19-criterion rule of s10.4 at the B-IP n", falsifier: "F1_G below 0.6 on the 7 drawn Stage A records, or any gate criterion missed after one re-gate", gpu_hours: 0}
```

# Extraction and quality-appraisal plan, form v0.4 (draft, 2026-10-20; not frozen)

Status: a specification. Nothing here is a result about any paper. No extraction has been run and no sample
has been drawn. Earlier versions stay as they are. Every finding of red-team audit 3 is answered in
`RESPONSE-TO-REDTEAM-v0.3.md`. **This file is a delta on EXTRACTION-PLAN-v0.3.md**: a section not written
here applies as written in v0.3 (and through it, v0.2). Section map:

| Section | Binding text |
|---|---|
| s1 changes; s2.3 multimodal; s2.8 cost additions; s2.10 seeds; s4 schema; s5.2 H key; s5.3 U3, U10; s5.4 K key; s10.2-s10.7 pilot and gate; s11 tools and agreement.py; s13 rows 31-35; s14 checklist; Appendix A | this file |
| s2.1, s2.2, s2.4-s2.7, s2.9, s5.1, s5.5-s5.7, s6, s7, s8, s9, s12, s13 rows 1-30 | v0.3 (seed numbers there are replaced by s2.10 here) |
| field table, roles, isolation, QA rubric | v0.2 as amended by v0.3 |

## 1. What changed from v0.3

1. **Gate (C1).** Four criteria added, each a lower bound against a numerical bad level: group-anchor
   agreement on matched groups (M-anchorG), sign agreement on matched K units (M-sign, higher_is_better),
   raw agreement on the K attributes that set poolability (K-attr: held_fixed, budget_across_arms,
   credited_ablation, arm scoring), and agreement of the derived pooling flag K15 matched (M-pool). 19
   criteria; the joint simulation is rerun (s10.4, s10.6).
2. **ICC (M1).** Stage A estimates the intra-record correlation with a calibrated (Neyman) upper bound; the
   gate re-estimates it on its first 60 records and extends to the size the rule needs, at most 120 (design
   B-IP, s10.7). P(pass | good) is shown over ICC 0.05-0.40 (s10.6).
3. **Anchors (M3).** U3 rewritten with named clauses; value-identity looks at every earlier results table
   holding the reference arm, with a numerical scale test; a full-configuration clause for removal groups.
4. **Brief (M4).** Every example the sessions see is synthetic; a committed script checks the brief and the
   schema against all 608 include texts. The Stage A falsifier is computed on the 7 drawn records only.
5. **Unmapped strings (M5).** K units whose benchmark or metric string is not in the frozen lookups match on
   the normalised printed string; the fallback share is reported (s5.4).
6. **Multimodal (M2).** The construct is an option list with counts from a committed script; the plan does
   not choose (s2.3, OQ4-03). The split and asymmetric records go to the human check (m3, m4).
7. **Minors.** Figure conditions (m1), H key by column index (m2), figure shape from prose only (m7),
   certainty second reading costed (m6), split gate design simulated and costed (m8), stale text and seed
   table fixed (m9), agreement.py in the Stage A tools with an exact specification (m10, s11.1).
8. **Found while revising.** schema v0.3 still had form_version const "0.2" (fixed: "0.4"); the v0.2-v0.3
   E3 example came from a drawable include (M03416), and v0.3's H example "by 7.56 points" occurs in one
   include (M13195): both replaced.

## 2. Scope

### 2.3 Multimodal: the v0.3 rule stays provisional; the construct is the human author's choice (M2, m3, m4)

The v0.3 rule (strata.py; C2 = i1 = a, not nonlang_only, screening field mm = "multimodal") is reproduced
exactly by `analysis/extraction/multimodal_options.py` (C1 53, NL 12, C2 108, FR 435; list hashes equal to
strata-log.txt). The red-team showed that mm measures "the paper contains any D4 experiment": about 29 of the
108 C2 records are text or general discrete-diffusion papers whose only image, audio or music work is a
separate model, while M18118 (LLaDA-V on MathVista) is in frame R. The options, with counts from
multimodal_options-log.txt (K records = C1 + C2 [+ C2b] + the frame-R sample of 120):

| Option | C1 | C2 | C2b | Frame R | K records | Block K, scope Option 1 | All blocks, scope Option 2 |
|---|---|---|---|---|---|---|---|
| (a) C1 only | 53 | 0 | 0 | 543 | 173 | 6.9M-13.8M | 13.5M-23.4M |
| (b) mm rule (v0.3) | 53 | 108 | 0 | 435 | 281 | 11.2M-22.5M | 21.9M-37.9M |
| (c) joint-model rule; side-experiment records to frame R | 53 | 80-89 | 0 | 454-463 | 253-262 | 10.1M-21.0M | 19.7M-35.4M |
| (d) joint-model rule; side-experiment records as a labelled census stratum C2b | 53 | 80-89 | 29 | 425-434 | 282-291 | 11.3M-23.3M | 22.0M-39.3M |

Joint-model rule: a D4 modality enters or leaves the same model that produces the text. Inputs are
provisional: the 29 side-experiment ids are the red-team's reading of the screener notes (E1); a keyword
cross-check finds a multimodal benchmark or diffusion-LM name in the body of 2 of these 29 (M13444, M18406)
and of 59 of the other 79 C2 records. Frame-R records that might be joint-model: M18118 confirmed (red-team,
E2) plus 9 candidates by a keyword in a table caption (M07165, M13735, M14023, M15097, M15613, M15736, M16249,
M17056, M17150; "ASR" in several may mean attack success rate, and M15613 is time-series captioning, not D4).
The C2 range 80-89 is 108 - 29 + 1 to 108 - 29 + 10. Under every option the C2 columns are labelled with the
rule that produced them ("C2 (mm rule)", "C2 (joint-model)").

Before any draw, one human check (OQ4-04) settles: the 29 side-experiment ids and the 10 frame-R candidates
(if option c or d is chosen); the 3 split text/multimodal records that v0.3 decided by keyword (M02955,
M18118, M18656: m4, now read from the full text, the keyword rule is retired); the 6 includes where screeners
A and B agreed on the decision but not on i1 or nonlang_only, for which the decisions file carries A's value
(M10840, M12859, U04330: i1 a against ab, which moves them between C2/frame R and C1; M16043: ab against b;
M11389, M18059: nonlang_only; m3). The outcome goes to `analysis/extraction/mm-construct.jsonl` and
`strata-overrides.jsonl`; multimodal_options.py and strata.py then use it.

### 2.8 Cost additions (`cost_options_v04.py`, log cost_options_v04-log.txt; E0)
v0.3's table stands, plus:
- **m6** certainty second reading of column_unverified units on the 252 K records read once, share
  0.10-0.30 of their K units (E0; Stage A measures it): **1.5M-9.1M**, under both scope options.
- **Gate size** (s10.7): the gate component is 10.6M-18.6M at n 60; 12.7M-22.3M at 72; 15.8M-27.9M at 90;
  18.5M-32.5M at 105; 21.1M-37.2M at 120. Under design B-IP the expected cost follows the distribution of n
  in s10.6 Table D.
- **m8 split design** (30 full gate records + 30 K-only records): 8.9M-16.2M (1.7M-2.4M less than n 60);
  with K criteria on 90 (30 full + 60 K-only): 12.5M-23.1M. Its operating characteristics are in s10.6
  Table E; it is not recommended.

### 2.10 Seed table (replaces v0.3 s2.10; m9)
Python 3.14.3 pinned. Ranges are disjoint by purpose; inside the simulation block each scenario has its own
offset (listed in the script headers).

| Purpose | Seed |
|---|---|
| Stage A draw | 20261100 |
| Gate draw, stratum h = 0, 1, 2 (one ordered list of 40 per stratum, drawn at once; phase 1 = positions 1-20, an extension takes the next positions) | 20261200 + h |
| Re-gate draw (same procedure) | 20261300 + h |
| Frame-R sample, T1, stratum h = 0..3 | 20261400 + h |
| Later tranche t = 1..9, stratum h (at most 20261593) | 20261500 + 10 t + h |
| ER draw, part p | 20261600 + p |
| EC labels X/Y | 20261700 |
| Gate bootstrap | 20261800 |
| Production bootstraps | 20261900 |
| gate_oc.py (v0.3) simulation, historical; not reused | 20262000-20262999 |
| gate_oc_v04.py and gate_adaptive_v04.py simulations | 20263000-20263999 |
| icc_check.py simulation | 20264000-20264899 |
| Neyman ICC bound: Stage A / gate phase 1 / re-gate phase 1 | 20264900 / 20264901 / 20264902 |
| Human gold subset (OQ2-10; v0.3's 20262100 lay inside the v0.3 simulation range) | 20266100 |
| agreement.py self-tests | 20267000 |

## 4. Schema v0.4 (`make_schema_v04.py`; extraction-schema-v0.4.json, sha256 caa6765f3549eb7c6e17cafe82c2b999402c246eff29a0df761eb8ca89f83840; Draft 2020-12 check_schema ok)

| Field | Change | Finding |
|---|---|---|
| form_version | const "0.4" (v0.3 schema still said "0.2") | found |
| G19 anchor_rule | enum adds full-configuration (U3) | M3 |
| S18 focal_config, cell `cells`, A level_printed | examples replaced by synthetic ones | M4 |
| G shape | trend only from a stated sentence; else unclear | m7 |

Field count unchanged (153). No field is added: the new gate criteria use existing fields (G13
credited_ablation, G15 held_fixed, G16 budget_across_arms, G19 anchor_arm, A10 scoring, K07 higher_is_better,
K15 matched).

## 5. Units

### 5.2 H key (m2)
An F1-table H unit is keyed by (where, U11-normalised row_group, U11-normalised row_label, col), col being
the value's position in the leaf map, when the validator marks both readers' cells column-verified (s6.3
item 9). Otherwise col is replaced by the leaf parts of column_printed, split at " / " and each part
U11-normalised. Abstract units keep (origin, character offset). The leaf string itself is never a key part.

### 5.3 Rules changed

**U3 Anchor (M3; binding text: brief v0.4 block K).** Clauses in order, each named in anchor_rule:
focal-label; other-own-model; stated-default (for this table or figure only); **value-identity**: the
reference arm is the focal configuration's arm, or, for a group whose second-factor level is another own
model, that model's arm in the focal setting; every results table before this one that contains the
reference arm is used, main-results table or not; a column is shared when benchmark and condition are equal,
the metric is equal or printed in only one of the two tables, and the two values are within a factor of 2
(the scale test); values are equal after rounding to the coarser printed precision; "-" and blanks are not
values; a level qualifies when it equals the reference arm on at least one shared column and differs on
none; ties: more equal columns, then reading order; **full-configuration**: in a task-or-modality-removal or
component-removal group, the one arm whose label marks no removal; **first-own-arm**: the first own arm whose
label marks no removal. Analysis and benchmark papers: stated default, else null. On Muddit (M12766) this
gives 0.6 for Table 3 and Joint training for Table 4, one reading each; on LLaDA2.1 (M08100) Table 4 it gives
w/o MBE for both levels (worked-examples-v0.4.md s2, s5).

**U10 Figures (m1, m7).** A condition never splits units or groups in a figure, whether it is a series, an
x-axis category or a panel; one unit per (benchmark, metric). shape is coded only from a sentence of the text
or caption that states the trend, else unclear; agreement.py reports the share of figure-only groups and of
shape unclear.

### 5.4 K key with unmapped strings (M5)
The K key stays (matched group, benchmark key, metric key, normalised condition_printed, split). A string's
key is its id in the frozen lookup (`analysis/extraction/lookups/benchmark-ids-v1.csv`, `metric-ids-v1.csv`)
when its normalised form is listed there, else `raw:` + its normalised form. Normalisation of benchmark and
metric strings: quote_check.normalise, lower case, arrows and enclosing parentheses removed (as N3, N5), a
trailing citation with a year removed, all whitespace removed. A mapped and an unmapped string never match.
agreement.py reports (a) the share of K units (matched and unmatched, both readers) with at least one raw key
part, (b) F1_K and M-val restricted to units whose keys are fully mapped, (c) a lenient F1_K in which two raw
strings also match when their normalised forms are equal after removing every non-alphanumeric character or
one equals the other plus a trailing version or split token. The gate criterion uses the primary key; (a),
(b), (c) are reported in the verdict. Rejection test kept from the red-team: a fallback share above 0.05 of
gate K units is reported as a lookup defect of B5. Lookups are seeded from the Stage A records and from a
fixed alias list of metric spellings (accuracy, acc, acc., exact match, EM, pass@1, BLEU, ROUGE-L, CIDEr, FID,
CLIP score, perplexity, PPL, NLL, bits per token, tokens per second, TPS, TPF, latency, speed-up, NFE, steps),
each with a higher_is_better column used by the sign cross-check (s10.3).

## 10. Pilot: development stage, then gate

### 10.2 Stage A, development (n = 12; no pass or fail)
As v0.3, with these changes:
- **Draw (m5).** draw_pilot.py excludes the five worked-example ids (M07474, M12766, M09530, M13864, M08100)
  from every pool before drawing the 7 records (two of them, M09530 and M13864, sit in the 24-record
  benchmark/analysis-title pool).
- **Brief (M4).** Sessions get brief v0.4 and schema v0.4, whose examples are synthetic
  (brief_contamination.py: v0.3 held 17 strings from drawable papers; v0.4 none).
- **Falsifier (M4).** F1_G below 0.6 is computed on the **7 drawn records only**. The 5 worked-example
  records are reported separately, against worked-examples-v0.4.md, and the red-team's contamination test is
  reported: F1_G on the 7 drawn more than 0.15 below F1_G on the 5.
- **Expected lists as data.** Before Stage A, the method-architect writes the worked-example group and unit
  lists as `analysis/extraction/we-expected.jsonl` (keys and anchors only) so agreement.py can compare.
- **ICC (M1).** agreement.py estimates, for each of the eight count metrics (F1_G and F1_K on the Jaccard
  scale, M-val, K-attr, M-class, M-anchorG, M-sign, M-pool), the one-way ANOVA ICC on the 12 records, their
  mean (pooled ICC) and the Neyman 80 percent upper bound U_N (icc_check.py defines both and is the reference
  implementation; seed 20264900). Stage A's U_N sets the **planned** gate size for the budget check
  (n(U_N) from s10.6 Table B) and is reported with the 7-record value; it does not fix the gate size, which
  design B-IP re-estimates on 60 gate records (s10.7).
- Lookups, rules, cost table and gate_oc_v04.py inputs are revised from Stage A means as in v0.3.

### 10.3 Stage B metrics (additions to v0.3 s10.3)
Applicable pairs, NA handling and the bootstrap are as in v0.3. New:
- **M-anchorG**: over matched groups (U13), credit 1 when both anchor_arm are null, or both non-null and the
  arms match by U11 (equal normalised label, else label-core); null against non-null is 0. Pooled over groups;
  per-record numerators and denominators for the bootstrap.
- **M-sign**: over matched K units, credit 1 when higher_is_better is equal; null against a value is 0;
  null-null pairs are excluded. Computed on the extractors' values, before the script's lookup cross-check.
- **K-attr**: raw agreement over applicable pairs of held_fixed, budget_across_arms and credited_ablation per
  matched group, and scoring per matched arm (U11 arm match inside matched groups); pooled.
- **M-pool**: over matched K units, agreement of K15 matched, each reader's flag derived by script from that
  reader's own group and arm fields (held_fixed stated, other_changes '', and for RQ2 budget matched and every
  arm's scoring equal and stated).
- Diagnostics added: per-field agreement inside K-attr; fallback shares of s5.4; share of figure-only groups
  and of shape unclear; per-metric and pooled ICC with U_N (gate phase 1 and the full gate).

### 10.4 Decision rule (fixed before the gate; signed by gate-auditor)
**PASS iff every one of the 19 criteria holds** on the n records that design B-IP sets:

| Criterion | Quantity | Good | Bad | Line |
|---|---|---|---|---|
| G1a, G1b | first-pass acceptance, EA and EB | 0.95 | 0.85 | LB90 >= 0.85 |
| G3 S, D, F, QA-sub, CT, H-attr | block raw agreement (6 criteria) | 0.85 | 0.70 | LB90 >= 0.70 |
| **G3 K-attr** | held_fixed, budget_across_arms, credited_ablation, scoring | 0.85 | 0.70 | LB90 >= 0.71 |
| G3 QA kappa | mean per-item linear-weighted kappa | 0.70 | 0.40 | LB90 >= 0.45 |
| G4 F1_H | headline-unit identification | 0.85 | 0.70 | LB90 >= 0.70 |
| G4 F1_G | group identification | 0.75 | 0.60 | LB90 >= 0.60 |
| G4 F1_K | contrast-unit identification | 0.75 | 0.60 | LB90 >= 0.60 |
| G4 M-val | K value agreement on matched units | 0.95 | 0.85 | LB90 >= 0.86 |
| G4 M-class | rq_class on matched groups | 0.85 | 0.65 | LB90 >= 0.65 |
| **G4 M-anchorG** | anchor arm on matched groups | 0.85 | 0.70 | LB90 >= 0.71 |
| **G4 M-sign** | higher_is_better on matched K units | 0.97 | 0.90 | LB90 >= 0.91 |
| **G4 M-pool** | derived K15 matched on matched K units | 0.85 | 0.70 | LB90 >= 0.71 |
| G5 anchors | F1 unit and S14 both identical | 0.85 | 0.60 | count >= c(n): 43 of 60, 51 of 72, 63 of 90, 72 of 105, 82 of 120 |

The four new lines sit 0.01 above their bad level because, at the bad level, the percentile cluster bootstrap
passes the criterion in 0.087-0.100 of simulated gates; at the lines chosen, in 0.031-0.052
(gate_oc_v04-calibrate-log.txt). M-sign's levels (good 0.97, bad 0.90) are stricter than the other
attribute levels because a sign disagreement reverses a contrast; the human author approves or changes every
level in the B2 row (OQ4-08). G7 (budget check) and outcomes are as v0.3 s10.4-s10.5; a re-gate repeats design
B-IP with seeds 20261300 + h and 20264902.

### 10.6 Operating characteristics (gate_oc_v04.py, log gate_oc_v04-log.txt; gate_adaptive_v04.py)
Model as v0.3 s10.6 (Beta record effects with intra-record correlation ICC, Gaussian copula weight OMEGA 0,
Poisson or negative-binomial unit counts, the gate's stratified cluster bootstrap with 500 resamples per
simulated gate). New quantities: K-attr ratio with negative-binomial mean 18 items per record; M-anchorG and
M-class on the record's matched groups; M-sign and M-pool on its matched K units. All inputs E0.

**Table A. Fixed n = 60, ICC 0.10, 2,000 simulated gates per scenario (G5 line 43).**

| Scenario | P(gate passes) | P(that criterion passes) |
|---|---|---|
| every quantity good | **0.866** (MC s.e. 0.008) | lowest marginals: M-anchorG 0.930, M-sign 0.960, F1_G 0.983, M-pool 0.992 |
| G1 EA / EB bad | 0.055 / 0.076 | 0.065 / 0.086 |
| S / D / F / QA-sub / CT / H-attr bad | 0.059 / 0.051 / 0.066 / 0.059 / 0.061 / 0.057 | 0.070 / 0.059 / 0.073 / 0.066 / 0.070 / 0.067 |
| K-attr bad | 0.030 | 0.033 |
| QA kappa bad | 0.009 | 0.011 |
| F1_H / F1_G / F1_K bad | 0.056 / 0.044 / 0.056 | 0.065 / 0.051 / 0.065 |
| M-val / M-class bad | 0.032 / 0.058 | 0.036 / 0.068 |
| M-anchorG / M-sign / M-pool bad | 0.044 / 0.040 / 0.040 | 0.049 / 0.044 / 0.045 |
| G5 anchors bad | 0.036 | 0.041 |
| every quantity bad | 0.000 | |

Sensitivity at n = 60, ICC 0.10 (1,000 each): OMEGA 0.5 0.917; unit counts more skewed (NB shape 0.7) 0.777.

**Table B. P(pass | every quantity good) for fixed n, ICC common to every metric (1,000 each).**

| ICC | n 60 | 72 | 90 | 105 | 120 |
|---|---|---|---|---|---|
| 0.05 | 0.930 | 0.973 | 0.989 | 0.993 | 1.000 |
| 0.10 | 0.852 | 0.923 | 0.976 | 0.983 | 0.991 |
| 0.15 | 0.779 | 0.849 | 0.938 | 0.962 | 0.982 |
| 0.20 | 0.660 | 0.783 | 0.881 | 0.918 | 0.954 |
| 0.25 | 0.566 | 0.667 | 0.834 | 0.885 | 0.914 |
| 0.30 | 0.486 | 0.616 | 0.754 | 0.814 | 0.867 |
| 0.40 | 0.298 | 0.438 | 0.585 | 0.709 | 0.769 |

Smallest n with P >= 0.85: 60 for ICC <= 0.10, 90 for 0.15-0.20, 105 for 0.25, 120 for 0.30, none for 0.40.
Largest P(pass | one of the nine weakest quantities bad): n 60 ICC 0.30 0.042; n 90 ICC 0.10 0.074; n 90 ICC
0.30 0.055; n 120 ICC 0.30 0.056. With the four new criteria, a fixed 60-record gate meets the 0.85 target
only if the ICC is at most about 0.10 (v0.3's 15 criteria: 0.889 at ICC 0.20).

**Table C. What 12 Stage A records say about the ICC (icc_check.py, 300 replicates per cell).** Pooled
estimate median [10%, 90%] and coverage P(true <= bound) of the two upper bounds:

| True ICC | Pooled estimate | U_B (percentile bootstrap) median, coverage | U_N (Neyman) median [90th percentile], coverage |
|---|---|---|---|
| 0.05 | 0.08 [0.03, 0.17] | 0.12, 0.90 | 0.12 [0.28], 0.81 |
| 0.10 | 0.11 [0.05, 0.21] | 0.14, 0.75 | 0.18 [0.34], 0.85 |
| 0.20 | 0.18 [0.11, 0.27] | 0.21, 0.54 | 0.32 [0.50], 0.88 |
| 0.30 | 0.25 [0.15, 0.35] | 0.27, 0.34 | 0.44 [0.60], 0.88 |

(With 7 records: U_N coverage 0.81-0.89, U_B 0.23-0.84; log rows k = 7.)

The record-level percentile bootstrap (red-team's proposal) under-covers once the ICC is 0.10 or more; the
Neyman bound is calibrated (coverage 0.81-0.89) but wide. Mapped through Table B, Stage A's U_N would set n
as follows (share of replicates):

| True ICC | n 60 | 72 | 90 | 105 | 120 | none <= 120 |
|---|---|---|---|---|---|---|
| 0.05 | 0.45 | 0.16 | 0.22 | 0.05 | 0.04 | 0.08 |
| 0.10 | 0.24 | 0.15 | 0.28 | 0.11 | 0.07 | 0.15 |
| 0.20 | 0.03 | 0.04 | 0.17 | 0.13 | 0.13 | 0.51 |
| 0.30 | 0.00 | 0.00 | 0.04 | 0.05 | 0.05 | 0.86 |

So a gate size fixed from Stage A alone would be 90 or more in 0.39 of cases at a true ICC of 0.05 and in
0.61 at 0.10, and would exceed 120 in 0.15 (ICC 0.10) to 0.51 (ICC 0.20) of cases. This is why the gate re-estimates the ICC on
its own first 60 records (s10.7).

**Table D. Design B-IP (gate_adaptive_v04.py, 400 replicates per scenario; U_N with 200 simulations per grid
point, production 1,000).**

| True ICC | P(pass, all good) | n 60 | 72 | 90 | 105 | 120 | mean n |
|---|---|---|---|---|---|---|---|
| 0.05 | 0.935 | 0.91 | 0.09 | 0.01 | 0.00 | 0.00 | 61.2 |
| 0.10 | 0.915 | 0.40 | 0.41 | 0.19 | 0.01 | 0.00 | 70.9 |
| 0.15 | 0.912 | 0.04 | 0.20 | 0.65 | 0.09 | 0.03 | 87.4 |
| 0.20 | 0.910 | 0.00 | 0.03 | 0.49 | 0.32 | 0.16 | 99.2 |
| 0.30 | 0.860 | 0.00 | 0.00 | 0.01 | 0.07 | 0.93 | 118.8 |

One quantity bad, others good (P(pass); mean n): at ICC 0.10, F1_G 0.060, M-anchorG 0.035, M-sign 0.035,
M-class 0.050, G1 EB 0.062; at ICC 0.30, 0.050, 0.043, 0.040, 0.058, 0.070. Re-estimating the ICC on the
gate's own records does not inflate false passes above the fixed-n levels of Table A (largest 0.070 against
0.076); MC s.e. about 0.012 at 400 replicates.

**Table E. Split designs (m8; gate_oc_v04-split-log.txt and log section D, 1,000 each).** L/Q/H criteria on
30 records:

| K criteria and G5 on | ICC 0.10 | ICC 0.20 | ICC 0.30 | Largest P(pass, one of 8 quantities bad) |
|---|---|---|---|---|
| 60 (30 full + 30 K-only records) | 0.817 | 0.569 | 0.350 | 0.072 (block F, ICC 0.10) |
| 90 (30 full + 60 K-only records) | 0.936 | 0.755 | 0.484 | 0.082 (block F, ICC 0.10) |

(Log section D repeats the 60-record split with other seeds: 0.826, 0.579, 0.354.) Fixed full gates for
comparison (Table B): n 60 0.852 / 0.660 / 0.486; n 90 0.976 / 0.881 / 0.754.

The split design loses robustness in the L/Q/H criteria as soon as the ICC rises, and saves at most 2.4M; it
is not recommended (OQ4-07 lists it).

### 10.7 The ICC rule (M1): design B-IP
1. **Plan.** After Stage A, agreement.py gives the pooled ICC and U_N (12 records). The budget projection of
   G7 uses n_plan = the smallest n in Table B with P >= 0.85 at U_N (120 if none). If the projected total
   exceeds the approved budget, the fallback ladder of v0.3 s10.5 applies before Stage B.
2. **Phase 1.** draw_pilot.py draws, per stratum, one ordered list of 40 ids (seed 20261200 + h). The first 20
   per stratum (60) are extracted, validated and adjudication-blind as in v0.3 s10.3.
3. **Re-estimate.** agreement.py computes the pooled ICC of the eight count metrics on the 60 records and U_N
   (seed 20264901). It reports nothing else to anyone until step 5: no criterion is computed at this step.
4. **Set n.** n = the smallest n in {60, 72, 90, 105, 120} with P(pass | all good) >= 0.85 at ICC U_N
   (Table B, linear interpolation in ICC); n = 120 if none. If n > 60, the next n/3 - 20 ids per stratum are
   extracted under the same brief, schema, lookups and checks.
5. **Decide.** The s10.4 rule is applied once, to all n records, with the G5 line c(n). PASS, FAIL and re-gate
   as v0.3 s10.5.
6. **Above the modelled range.** If U_N at phase 1 exceeds 0.30, the verdict states that P(pass | good) at the
   estimated ICC is below 0.85 (Table B: 0.769 at ICC 0.40 with n 120); a FAIL is still a FAIL, and the human
   author decides in the verdict row whether the re-gate keeps n = 120 or first revises the rules aimed at the
   metric with the largest ICC.
What B-IP costs: Table D gives the distribution of n; with the gate-record range of s2.8 the expected gate
cost is 12.5M-22.0M (mean n 70.9) at ICC 0.10 and 20.9M-36.8M (mean n 118.8); 10.8M-19.0M at ICC 0.05 at ICC 0.30.

## 11. Tools to build (lab-engineer; nothing here is built)
As v0.3 s11, with agreement.py moved into the Stage A list (m10) and specified below; draw_pilot.py draws the
Stage A pools without the five worked-example ids and the gate as one ordered list of 40 per stratum;
lookup CSVs gain a higher_is_better column for metrics. Committed scripts written for v0.4 (Appendix A):
gate_oc_v04.py, gate_adaptive_v04.py, icc_check.py, multimodal_options.py, cost_options_v04.py,
make_schema_v04.py, brief_contamination.py.

### 11.1 agreement.py (exact specification)
**Place and run.** `analysis/extraction/agreement.py`, `python -E -P` (numpy). One deterministic run:
```
python -E -P analysis/extraction/agreement.py --mode {stage-a|gate-phase1|gate} --x <EA.jsonl> --y <EB.jsonl>
  --manifest <draw manifest .json> --lookups analysis/extraction/lookups/ --validator <ex_validate report .jsonl>
  --out <dir> [--we analysis/extraction/we-expected.jsonl] [--boot-seed 20261800] [--icc-seed 20264900|20264901]
  [--self-test]
```
**Inputs.** (1) Two record files, one JSON object per id (schema v0.4), each record already through
ex_validate (Dv fields filled: rq_class, duplicate flags, K15 matched; metric_id and benchmark_id when mapped).
(2) The draw manifest: ids, stratum per id, the ordered gate list, frame and list hashes; agreement.py refuses
records whose ids are not in it, and in gate-phase1 mode uses only phase-1 ids. (3) Lookups (benchmark and
metric CSVs: printed normalised string, id, higher_is_better for metrics), frozen and hashed. (4) The validator
report (per entry: accepted at first pass yes/no; per cell value: column verified or unverified). (5) In
stage-a mode, the worked-example expected lists. Missing or mismatched input: stop with an error, write no
output.

**Normalisation and matching** (one module, imported by ex_validate where the two share rules):
U11 label normalisation and label-core (quote_check.normalise imported read-only); benchmark and metric keys
of s5.4; H match by U14 as amended in s5.2; group match by U13 (where, normalised second_factor_printed; arm
label Jaccard >= 0.5; one-to-one by highest Jaccard, ties to the lower group id); K match by the U9 key inside
matched groups; arm match by U11 inside matched groups; claim match for M-CL by v0.3 s10.3. Every match list
is written out (matched pairs, X-only, Y-only), per record.

**Metrics.** Every quantity of v0.3 s10.3 and of s10.3 above, each stored as per-record numerator and
denominator (QA kappa: per-record joint score counts per item):
G1a, G1b; M-raw for blocks S, D, F, QA-sub, CT, H-attr and K-attr (Jaccard credit for set-valued fields as
v0.3); QA kappa (mean of per-item linear-weighted kappas, items with fewer than 10 paired records left out and
listed); F1_H, F1_G, F1_K = 2 |matched| / (|X| + |Y|); M-val; M-class; M-anchorG; M-sign; M-pool; G5 count.
Point value = pooled numerator / pooled denominator. LB90 = 5th percentile over 4,000 stratified cluster
bootstrap resamples (records resampled with replacement within gate strata; Stage A: within its pools), seed
--boot-seed, one index matrix shared by all metrics; QA kappa items recomputed inside each resample.
Diagnostics: per-field kappa and Gwet's AC1, per-field flags (flag_thresholds.py lines), Jaccard-field
intervals, QA-score raw agreement, column_unverified share, label-core match share, anchor_rule agreement,
M-CL and per-CT-type kappa, fallback shares and lenient F1_K (s5.4), figure-only and shape-unclear shares,
unit counts per record.
**ICC.** For the eight count metrics: per-record x_r and m_r (F1_G and F1_K: matched and union units), the
ANOVA ICC, the pooled mean, and U_N, exactly as icc_check.py (`icc_anova`, `upper80_neyman` with R = 1,000,
grid 0.02-0.60, seed --icc-seed). Stage A also reports the 7-drawn-record values.
**Outputs** (in --out): `agreement-<mode>.json` (per metric: point, LB90, pooled numerator and denominator,
records used; ICC block; input sha256 values; tool version; seeds); `per-record-<mode>.csv` (one row per
record and metric: numerator, denominator); `matches-<mode>.jsonl` (match lists for EC, written only after
the metrics); in gate mode `verdict-table.md` (each criterion of s10.4 with its line, LB90 and pass/fail, the
G5 count against c(n), and the s5.4 reports); in gate-phase1 mode only the ICC block and n (no criterion);
in stage-a mode `we-comparison.md` (each extractor against worked-examples-v0.4: F1_G, F1_K, anchor agreement)
and the falsifier on the 7 drawn records with the 5 reported separately; a run log with the command line.
**Self-tests (--self-test, seed 20267000), all must pass before Stage A:** identical X and Y give every
agreement 1 and every F1 1; one group removed from Y gives the hand-computed F1_G; a swapped anchor in one
matched group gives the hand-computed M-anchorG; a flipped higher_is_better gives M-sign below 1 by one unit;
null against value counts as disagreement and null-null is excluded; label-core matching of "Model (x)"
against "Model"; an unmapped benchmark string equal in both records matches as raw, a mapped against an
unmapped string does not; a set field credits the Jaccard value; the stratified bootstrap is reproducible
with the same seed; icc_anova reproduces icc_check.py's self-tests; G5 count against c(n) for n 60 and 90.

## 13. Protocol and ledger deviations (additions to v0.3 s13)

| # | Deviation or refinement | Protocol / ledger | When |
|---|---|---|---|
| 31 | Gate has 19 criteria including anchors and K attributes (s10.4) | gate row | before Stage B |
| 32 | Gate design B-IP: n set from the ICC of the first 60 gate records, at most 120 (s10.7) | gate row | before Stage B |
| 33 | Multimodal construct (one of options a-d, s2.3) | scope row | before any draw |
| 34 | Unmapped benchmark and metric strings match on normalised printed strings (s5.4) | lookups M9c | before Stage A |
| 35 | Condition never splits figure units; figure shape only from stated sentences (U10) | s5 | before Stage A |

## 14. Preconditions checklist (replaces v0.3 s14)
None is met on 2026-10-20 unless marked.

**Stage A (development, 12 records)**
- [ ] A1 T1 full-text gate PASS signed by gate-auditor.
- [ ] A2 Scope decision row from OQ3-01, OQ3-02, OQ3-06, OQ3-09 and the multimodal construct OQ4-03.
- [ ] A3 Decision rows of v0.3 s13 marked "before Stage A", plus rows 34 and 35.
- [ ] A4 gate-auditor check of block F and C-F1a to C-F1e (OQ3-13).
- [ ] A5 Human check (OQ4-04): 3 split records, 6 asymmetric i1/nonlang_only records, 6 duplicate candidates, the borderline ids of v0.3, and (options c, d) the 29 side-experiment ids and 10 frame-R candidates; mm-construct.jsonl, strata-overrides.jsonl, duplicate-works.jsonl written; strata.py and multimodal_options.py rerun; hashes recorded.
- [ ] A6 Red-team review of v0.4 with no open critical finding.
- [ ] A7 Tools: ex_dispatch.py; ex_validate.py passing the 35 cases of validator-tests.jsonl, the v0.2 tests T01-T22 rewritten as v0.3-shape data, and `quote_check.py --self-test`; fixture generator; draw_pilot.py (Stage A, excluding the five worked-example ids); **agreement.py (s11.1) passing its self-tests**; lookup CSV skeletons with the metric alias list of s5.4.
- [ ] A8 v0.4 files and scripts committed by the orchestrator (v0.3 scripts are in f58c5c6; v0.4 written 2026-10-20, not committed).
- [ ] A9 ft_isolation_check.py and ft_model_check.py unchanged and passing.
- [ ] A10 Adjudicator route reconfirmed (OQ2-07).
- [ ] A11 worked-examples lists as data (we-expected.jsonl, method-architect).
- [ ] A12 brief_contamination.py rerun on the frozen brief and schema: no KNOWN string, no new specific string.

**Stage B (gate)**
- [ ] B1 Stage A complete; rules, lookups and cost table revised from Stage A means; gate_oc_v04.py rerun with Stage A's unit counts, and with `--icc-json` at Stage A's per-metric values; n_plan and the projected budget reported (s10.7 step 1).
- [ ] B2 Gate decision row: design B-IP (or the human author's alternative from OQ4-07), the s10.4 table with levels approved (OQ4-08), the re-gate rule; signed by gate-auditor.
- [ ] B3 agreement.py gate and gate-phase1 modes tested on synthetic pairs (s11.1).
- [ ] B4 draw_pilot.py gate draw: 40 ordered ids per stratum, excluding Stage A ids; manifest.
- [ ] B5 Brief, schema and lookups hashed in the gate row; fallback share of s5.4 checked on Stage A records.
- [ ] B6 Human gold subset decision (OQ2-10; seed 20266100).

## Appendix A. Scripts and logs (analysis/extraction/, written 2026-10-20, not committed)
v0.3 scripts and logs are unchanged and committed in f58c5c6 (the v0.3 plan header, s14 A8 and Appendix A
said "not committed": stale, m9).

| Script | Run | Log |
|---|---|---|
| gate_oc_v04.py | `python -u -E -P analysis/extraction/gate_oc_v04.py` ; `--calibrate` ; `--split` | gate_oc_v04-log.txt, gate_oc_v04-calibrate-log.txt, gate_oc_v04-split-log.txt |
| gate_adaptive_v04.py | `python -u -E -P analysis/extraction/gate_adaptive_v04.py --reps 400` | gate_adaptive_v04-log.txt |
| icc_check.py | `python -u -E -P analysis/extraction/icc_check.py` | icc_check-log.txt |
| multimodal_options.py | `python -I analysis/extraction/multimodal_options.py` | multimodal_options-log.txt |
| cost_options_v04.py | `python -I analysis/extraction/cost_options_v04.py` | cost_options_v04-log.txt |
| make_schema_v04.py | `python -E -P analysis/extraction/make_schema_v04.py` | make_schema_v04-log.txt |
| brief_contamination.py | `python -I analysis/extraction/brief_contamination.py` | brief_contamination-log.txt |

gate_adaptive_v04.py and icc_check.py read section B of gate_oc_v04-log.txt; run gate_oc_v04.py first.
gate_adaptive_v04.py imports gate_oc_v04.py and icc_check.py by explicit file path (no sys.path change).
