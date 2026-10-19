```yaml
agent: red-team
date: 2026-10-20
brief: fourth adversarial review of extraction and appraisal instrument v0.4 (Paper 1); verify the v0.3 fix claims by text and by re-running the committed scripts; attack design B-IP and the Neyman ICC bound, brief_contamination.py and the four new gate criteria; list what still blocks Stage A and Stage B
sources_examined:
  - research/CONTRACT.md
  - research/review/extraction/EXTRACTION-PLAN-v0.4.md (full), RESPONSE-TO-REDTEAM-v0.3.md (full), OPEN-QUESTIONS-v0.4.md (full)
  - research/review/extraction/extractor-brief-v0.4.md l.1-140, 395-534 (G1-G6, evidence, blocks H and K); worked-examples-v0.4.md l.1-40, s2 (Muddit), s5 (LLaDA2.1 Table 4), s7
  - research/review/extraction/extraction-schema-v0.4.json (group, arm, k_unit definitions and required lists)
  - research/review/extraction/EXTRACTION-PLAN-v0.3.md s5.3 (U11, U13), s10.5; EXTRACTION-PLAN-v0.2.md field rows G13, G16, A10, K07, K15 (grep)
  - analysis/extraction/gate_oc_v04.py, gate_adaptive_v04.py, icc_check.py, brief_contamination.py, make_schema_v04.py (read in full); multimodal_options.py, cost_options_v04.py (run); all v0.4 logs
  - research/sources/md/fulltext-pymupdf/M08100.txt l.655-725, 885-935, 1040-1145 (Tables 1, 2, 4); all 608 include texts by script (5-gram scan)
  - research/review/audits/2026-10-20-redteam-extraction-v0.1.md, -v0.2.md, -v0.3.md (my earlier reports; v0.3 read in full)
  - git show --stat b315c28
coverage: >
  Re-ran every v0.4 script into my scratchpad and diffed against the committed logs (results in part 1). Ran 12
  extra scenarios of design B-IP and of fixed-n gates with per-metric ICC and skewed unit counts (scratchpad
  hetero.py; it imports gate_adaptive_v04.py, gate_oc_v04.py and icc_check.py read-only and reuses their data
  model, bootstrap and Neyman bound unchanged), and an independent 5-gram contamination scan of the session
  text (scratchpad shingle.py). Re-derived the LLaDA2.1 Table 4 anchors on the rows the worked example did not
  compare. NOT covered: re-derivation of FDM, TrustLDM and M13864 units; the brief outside the line ranges
  listed; the validator, agreement.py and draw_pilot.py (not built); the 108 C2 full texts. The brief allows one
  output file, so no ledger row was added. The brief asks for a fix per finding, so fixes are given (a
  deviation from my agent definition); the criticism is not softened. Severity: critical = blocks the stage
  it names outright; major = must be resolved before the stage named; minor = should be fixed, does not block.
claims:
  - statement: Every number printed in plan v0.4 s10.6 Tables A-E, s2.8 and s2.3 from the committed scripts reproduces on re-run (elapsed time aside), and the schema rebuild is byte-identical.
    status: supported
    evidence: scratchpad goc.out, gcal.out, gsplit.out, gad.out, icc.out, mm.out, cost.out, bc.out, schema-v04.json (sha256 caa6765f...) diffed against analysis/extraction/*-log.txt
    level: E3
    confidence: 0.95
  - statement: Within the plan's own data model (one ICC shared by every metric), design B-IP does not inflate false passes; P(pass | F1_G bad) is 0.050 with B-IP against 0.056 (fixed 60) and 0.045 (fixed 120).
    status: supported
    evidence: scratchpad H7.out (1,500 replicates), H8.out, H9.out, H12.out
    level: E3
    confidence: 0.8
  - statement: When the ICC differs between metrics, B-IP misses its 0.85 target. With M-sign and M-pool at ICC 0.5 and the rest at 0.10, P(pass | all good) is 0.787. With M-sign and M-pool at 0.6, M-anchorG at 0.3 and the rest at 0.10, it is 0.743. In that second case even a fixed n of 120 gives only 0.797, and the step-6 warning does not fire because the median U_N is 0.28.
    status: supported
    evidence: scratchpad H1.out (300 replicates), H10.out (400 replicates)
    level: E3 (simulation); the ICC values are E0
    confidence: 0.75
  - statement: The session text gives no coding rule for higher_is_better, for budget_across_arms = matched, for arm scoring, or for credited_ablation outside replacement groups, although three of the four new criteria measure agreement on exactly these fields.
    status: supported
    evidence: extractor-brief-v0.4.md l.6-7 ("a session needs no other file"), l.410, 461, 507-524; schema $defs group, arm, k_unit
    level: E2
    confidence: 0.85
  - statement: The v0.4 session text contains no string specific to a drawable include beyond the instrument's own ids and codebook terms. brief_contamination.py does not by itself guarantee this, because it checks only double-quoted spans and decimal numbers.
    status: supported
    evidence: analysis/extraction/brief_contamination.py l.43-44, 86-100; scratchpad shingle.py (22 shared 5-grams, all generic)
    level: E3
    confidence: 0.85
competing_explanations:
  - Real per-metric ICCs may be similar (for example if sign disagreements are rare and scattered). Then pooling by the mean is harmless and B-IP keeps its characteristics. Only Stage A and gate phase 1 can tell. The structural argument (the sign is set per metric and the K15 flag per group) points the other way.
  - Undefined fields may still agree highly if both models apply the same conventions (accuracy up, perplexity down). Then M-sign passes, but it measures shared model priors, not the instrument.
unknowns:
  - per-metric ICC, in particular for M-sign and M-pool; share of K units per group and per metric; agreement on budget_across_arms and credited_ablation under the current text
next_test: {hypothesis: "per-metric ICCs differ enough that a mean-pooled bound under-sizes the gate", intervention: "in Stage A, report per-metric ICC and U_N for all eight count metrics; rerun gate_oc_v04 --icc-json with the per-metric upper bounds at n 60, 90, 120", primary_metric: "joint P(pass | all good) at the per-metric bounds against the n B-IP would choose from the pooled mean", falsifier: "the per-metric run gives P >= 0.85 at the n chosen from the pooled mean", gpu_hours: 0}
```

# Red-team audit 4: extraction and appraisal instrument v0.4

Verdict: **Stage A may proceed once the human author's rows are entered, the T1 gate passes and the tools are
built, provided MA2 (coding rules for the newly gated fields) is fixed first. Stage B may not proceed until MA1,
MA3 and MA4 are resolved.** No critical finding. v0.4 answers every v0.3 finding in substance. Every committed
number reproduces. The anchor clause now gives one reading on the two papers I checked. Within its own model,
B-IP controls false passes as claimed. The remaining problems sit in the parts of the gate design that the
simulation assumes away: one ICC shared by every metric, and a pinned decision function and budget. The other
problem is that the session text never defines the fields that three of the four new criteria measure.

References: PLAN = EXTRACTION-PLAN-v0.4.md, BRIEF = extractor-brief-v0.4.md, RESP = RESPONSE-TO-REDTEAM-v0.3.md,
WE = worked-examples-v0.4.md, OQ = OPEN-QUESTIONS-v0.4.md. Scratchpad scripts are not committed. Their path is
the session scratchpad named in my reply.

---

## 1. Re-runs and fix verification

Re-runs from the worktree root into the scratchpad, diffed against the committed logs:
- `python -I multimodal_options.py`, `python -I cost_options_v04.py`, `python -I brief_contamination.py`:
  byte-identical (exit code 0).
- `make_schema_v04.py` with DST redirected: sha256 caa6765f3549eb7c..., identical to PLAN s4; check_schema ok.
- `python -u -E -P icc_check.py`, `gate_oc_v04.py --calibrate`, `gate_oc_v04.py --split`: identical apart from
  the elapsed seconds.
- `gate_oc_v04.py` (full) and `gate_adaptive_v04.py --reps 400`: identical apart from the elapsed seconds (1,422 s and 1,449 s against 1,350 s and 1,322 s).
- Every number in PLAN s10.6 Tables A-E, s10.7, s2.8 and OQ4-07 matches the logs. I checked the derived
  shares too: "90 or more in 0.39 / 0.61 of cases" equals 0.22+0.05+0.04+0.08 and 0.28+0.11+0.07+0.15. The
  B-IP expected costs equal the linear gate cost times mean n.

| Finding | RESP status | Verified | Note |
|---|---|---|---|
| C1 anchors and K attributes not gated | fixed | **real as a gate rule; residuals** | Four criteria with calibrated lines (0.031-0.052 at the bad level, reproduced). But M-sign, budget "matched", scoring and part of credited_ablation have no coding rule in the session text (MA2). M-anchorG compares labels rather than matched arms (mi1). K-attr is diluted by scoring items (mi2). |
| M1 ICC fragility | fixed by B-IP | **real within the model; not robust to heterogeneous ICC** | Type I is controlled (my H7: 0.050 at 1,500 replicates). P(pass \| good) falls to 0.74-0.79 when ICC differs by metric (MA1). Decision function and budget not pinned (MA3, MA4). |
| M2 multimodal construct | options | real | Four options, counts reproduced. Residual mi6. |
| M3 U3 two anchors | fixed | **real** | Muddit Tables 3-4: one reading each under the new clause (WE s2 derivation checked against the scale test and "differs on none"). LLaDA2.1 Table 4: WE compared only 7 of 10 mini rows. I checked the other three (Spider 75.78 \| 7.98, AIME 2025 36.67 \| 6.34, IFEval 81.33 \| 1.83, M08100 l.1111-1131 against Table 2 l.890-928) and the flash Spider row (79.18 \| 8.74, l.661 and l.1111). All equal, so "w/o MBE" holds for both levels. |
| M4 contamination | fixed | **real in practice; script weaker than claimed** | 0 known strings; my 5-gram scan finds nothing specific (mi3). The falsifier is computed on the 7 drawn records (PLAN s10.2). |
| M5 unmapped strings | fixed | real as a rule | Primary key, raw fallback, lenient F1_K are specified. B5's check is circular (mi4). |
| m1, m2, m5, m7, m10 | fixed | real | BRIEF l.494-502; PLAN s5.2, s10.2, s11.1. m2 has an order-of-operations gap (mi7). |
| m3, m4 | routed | real | Six asymmetric and three split records are listed in the log and in OQ4-04. |
| m6, m8 | fixed | real | Costs reproduce; split design simulated (Table E reproduces). |
| m9 | fixed | **partly** | The seed ranges are now disjoint (I checked every offset in the three script headers). The text about commits is stale again: v0.4 is in b315c28 (mi7). |

No claimed fix is false. Two are only partly true: **M1** (robustness) and **C1** (definability of the gated
fields).

## 2. Design B-IP and the Neyman bound

**Is the procedure valid?**
- **The extension decision does not use criteria, but it is not independent of them.** U_N conditions on each
  metric's pooled mean p̄ (icc_check.py l.75). So n is a function of the point estimates of the eight count
  metrics as well as of their dispersion. A deterministic n rule fixed in advance still controls error if the
  whole procedure is simulated, and it is. I re-ran the type-I cases with more replicates (H7-H9, H12):

| Bad quantity (others good), ICC 0.10 | B-IP P(pass) | fixed 60 | fixed 120 | replicates |
|---|---|---|---|---|
| F1_G | 0.050 | 0.056 | 0.045 | 1,500 |
| M-val | 0.029 | 0.034 | 0.013 | 800 |
| F1_K | 0.041 | 0.052 | 0.046 | 800 |
| F1_K, unit counts NB shape 0.7 | 0.050 | 0.038 | 0.062 | 600 |

  B-IP lies inside or below the fixed-n range in every case, so none shows optional-stopping inflation. RESP's "does not inflate" holds within the model. The
  committed run (400 replicates, U_N with R = 200 against the 1,000 of production) could not have detected
  inflation below about 0.025 (mi5).
- **No peeking.** n is a deterministic function of the phase-1 data and a seed, so peeking cannot change n
  unless a discretionary step exists after phase 1. One does exist: the budget (MA4). The validator's
  first-pass acceptance (G1a, G1b) is visible to the operator during phase 1. s11.1 does not say whether
  gate-phase1 mode writes the match lists, or the per-metric p̄ inside the "ICC block".
- **"Re-estimate on 60, extend to at most 120" is free of optional-stopping bias for the pass/fail decision**
  in the sense above: the stopping rule is fixed, it is a function of the data, and the whole procedure is
  simulated. It is **not** free of model dependence. Table B, the grid that turns U_N into n, was computed with
  one ICC shared by all 19 criteria. U_N bounds the **mean** of eight per-metric ICCs (PLAN s10.7 step 3;
  icc_check.py `pooled` = nanmean). The joint pass probability is driven by the worst metrics, not by the mean.

**Heterogeneous ICC (scratchpad hetero.py; committed model, bootstrap and bound unchanged).**

| Scenario: ICC by metric, every quantity good | B-IP P(pass) | median U_N | mean n | fixed 60 | fixed 120 | replicates |
|---|---|---|---|---|---|---|
| all 0.10 (plan, Table D) | 0.915 | | 70.9 | 0.852 | 0.991 | 400 / 1,000 |
| H1: M-sign, M-pool 0.5; others 0.10 | **0.787** | 0.22 | 98.4 | 0.580 | 0.860 | 300 |
| H10: M-sign, M-pool 0.6; M-anchorG 0.3; others 0.10 | **0.743** | 0.28 | 111.6 | 0.505 | **0.797** | 400 |
| H2: F1_G 0.40; others 0.10 | 0.917 | 0.16 | 84.4 | 0.760 | 0.973 | 300 |
| H3: M-anchorG 0.40; others 0.05 | 0.867 | 0.12 | 68.9 | 0.813 | 0.950 | 300 |
| H6: L/Q/H and G1 criteria 0.40; count metrics 0.05 | 0.880 | 0.06 | 61.3 | 0.890 | 1.000 | 300 |
| H11: all 0.10, unit counts NB shape 0.7 | 0.863 | 0.12 | 71.9 | 0.780 | 0.973 | 400 |

Type I under heterogeneity (H4, H5: M-sign and M-pool at ICC 0.5). With M-sign bad, P(M-sign passes) is 0.120
at fixed n = 60: the percentile bootstrap under-covers a skewed proportion near 1. It is 0.070 under B-IP and
0.050 at n = 120. With M-pool bad: 0.047, 0.037 and 0.043. B-IP saves M-sign's type I here only because the
other metrics push n up. With the other metrics at ICC 0.05, n would stay near 60.

Why M-sign and M-pool are the plausible high-ICC metrics (inference, E0): higher_is_better is a property of the
metric, and the K units of a group often share one metric. A single convention difference ("TPF": null against
true) therefore flips every unit of that metric in the record. K15 matched is derived from group-level fields
(held_fixed, other_changes, budget) and is copied to every K unit of the group. The simulation draws both as
binomial over K units with the common ICC (gate_oc_v04.py l.142-145; icc_check.py l.111).

**Is a simpler design as good?** Within the model, B-IP dominates the fixed sizes on the cost-power trade-off.
At ICC 0.05-0.10, fixed n = 90 has more power (0.989, 0.976) but costs 15.8M-27.9M for certain. B-IP's mean n
is 61-71. The split design loses power on L/Q/H (Table E reproduces). So the design choice is defensible. The
defect is the summary statistic that drives it (MA1).

**The Neyman bound** is implemented correctly as a one-sided test inversion: it takes the largest θ with
P_θ(pooled ≤ observed) ≥ 0.20, and coverage of 0.81-0.89 reproduces. That coverage holds under the same
Beta-binomial model with one θ shared by all metrics. It is calibrated for the mean ICC and says nothing about
the largest one. R = 200 in the B-IP simulation against 1,000 in production makes the simulated U_N slightly
larger: "largest θ that passes" picks up Monte Carlo noise upward, so the simulated n is slightly too large
and the simulated P(pass | good) slightly optimistic (mi5).

## 3. brief_contamination.py: does it guarantee a clean brief?

No, but the v0.4 brief is clean in practice.
- What it checks (l.43-44, 51-70): double-quoted spans of 3-80 characters and decimal numbers inside the
  ```` ```text ```` blocks and the schema descriptions (single quotes converted). Not checked: integers;
  unquoted phrases and labels; backtick, curly or single-quoted spans in the brief; co-occurrence of numbers
  that are each generic (a copied table row of common numbers passes); hyphenation and ligature variants in
  the PyMuPDF texts.
- The exit code is 0 whenever the 17 KNOWN strings are absent (l.100), whatever the number of "specific"
  hits. PLAN s14 A12 ("no new specific string") is therefore not enforced by the script.
- My independent check (scratchpad shingle.py): 9,112 word 5-grams of the session text against all 608
  include texts. 22 are shared, all generic English ("does not say whether the", "within a factor of two",
  "table 3 ablation of the"). No include line holds the synthetic number runs (41.7/44.9/38.2, 45.2/46.3).
  The real model and benchmark names in the text block are generic vocabulary only (BLEU, FID, GSM8K,
  GenEval, MME). I found no contamination.

## 4. The four new criteria: definable, measurable, correctly simulated?

| Criterion | Definable from the session text? | Measurable by agreement.py as specified? | Simulated as it behaves? |
|---|---|---|---|
| M-anchorG | Yes (U3 clauses) | Partly: anchor labels compared by U11 equality or label-core, not through the one-to-one arm match; null-null credited (mi1) | Yes, on matched groups |
| M-sign | **No** rule for higher_is_better anywhere in BRIEF (l.410, 521 list the field only) (MA2) | Yes | **No**: units clustered by metric, simulated as independent binomials at the common ICC (MA1) |
| K-attr | held_fixed yes (l.509-510). budget "matched" undefined. scoring undefined (G5 defines metric_kind, not arm scoring). credited_ablation defined only for replacement groups (l.461), and G13's "removes or replaces" is in the v0.2 plan, not in the brief (MA2) | Yes, but pooling lets scoring items dominate (mi2) | Partly: item count NB(18), independent of matched groups and arms |
| M-pool | Derived from the fields above, so it inherits their gaps | Yes | **No**: a group-level flag copied to K units, simulated as unit-level binomial (MA1) |

## 5. What still blocks Stage A and Stage B (beyond the human author's decision rows and the T1 gate)

**Stage A**
1. **MA2**: coding rules for higher_is_better, budget_across_arms = matched, arm scoring and credited_ablation
   in the brief's text block, with synthetic examples. Then rerun brief_contamination.py (A12).
2. A4: gate-auditor check of block F and C-F1a to C-F1e (agent work, not done).
3. A5: human check OQ4-04 (human item; add mi6's 20 records if option c or d is chosen).
4. A7: none of ex_dispatch.py, ex_validate.py (35 cases plus T01-T22 rewritten as v0.3-shape data), the
   fixture generator, draw_pilot.py, agreement.py with its self-tests, or the lookup skeletons is built.
5. A11: `analysis/extraction/we-expected.jsonl` does not exist.
6. A10: adjudicator route (human item). A8 is met by b315c28, but the files still say otherwise (mi7).
7. Before Stage A, so that Stage A measures what B-IP needs: agreement.py must report the **per-metric** ICC and
   per-metric U_N (it already computes per-metric ICC, PLAN l.230-233), not only the pooled value (MA1).

**Stage B**
1. **MA1**: the n rule must use the per-metric ICC vector (or the largest per-metric bound), and the joint
   simulation must model M-sign at the metric level and M-pool at the group level. Rerun before the B2 row.
2. **MA3**: freeze the grid and the U_N settings (R, θ grid, seed) as a hashed file read by agreement.py.
   Give gate_oc_v04.py a unit-count input so that B1's rerun does not mean editing the committed script.
3. **MA4**: approve the budget for n = 120 in the B2 row, or fix the rule that applies when the extension
   exceeds the budget. Specify that gate-phase1 mode writes no match lists and no per-metric p̄.
4. mi4: check the fallback share on records that did not seed the lookups.
5. B3, B4, B6 as listed in PLAN s14.

---

## Findings

### Major

**MA1. B-IP sizes the gate from the mean of eight per-metric ICCs, but the joint pass probability is set by the
worst metrics. Under plausible heterogeneity the design misses its 0.85 target, and the step-6 warning stays
silent.**

Evidence:
- PLAN s10.7 step 3 ("pooled ICC of the eight count metrics"); icc_check.py l.56-58 (`pooled` = nanmean) and
  l.79-85 (the bound simulates one θ for every metric); Table B and gate_adaptive_v04.py l.43-63 use one ICC for
  all 19 criteria.
- Part 2 table: P(pass | all good) 0.787 (H1) and 0.743 (H10). In H10 even n = 120 gives 0.797, while the median
  U_N is 0.28 < 0.30, so step 6 does not report that the target is out of reach.
- M-sign at ICC 0.5 with n = 60: P(criterion passes | bad) = 0.120 (H4).
- M-sign and M-pool are simulated as unit-level binomials, although their values are fixed per metric and per
  group (gate_oc_v04.py l.142-145).

Rejection test: in Stage A or gate phase 1, any per-metric ICC estimate above 0.30 while the pooled U_N is at or
below 0.20; or a rerun of gate_oc_v04.py with the per-metric upper bounds that gives P(pass | good) below 0.85 at
the n B-IP chose.

Fix: at phase 1, compute U_N per metric. Set n as the smallest grid n at which the **joint** simulation with that
per-metric ICC vector (gate_oc_v04 `--icc-json`, extended to the grid of n) reaches 0.85. Simpler and
conservative: use the largest per-metric U_N in the existing grid. Simulate M-sign over distinct metrics per
record and M-pool over matched groups (weighted by their K units). Trigger step 6 on any metric. Re-simulate the
whole procedure, including the H1 and H10 cases, before the B2 row.

**MA2. Three of the four new criteria measure agreement on fields that the session text never defines.**

Evidence:
- BRIEF l.6-7: the block is written "so a session needs no other file".
- higher_is_better: listed as a field at l.410 and l.521; no rule (arrow, caption, convention, null when
  unstated?) anywhere in BRIEF v0.2-v0.4 (grep). Schema: boolean or null, required.
- budget_across_arms: "inference budget: matched, reported, not reported" (l.511-512), with no definition of
  matched (equal steps? equal NFE? equal tokens? wall time?).
- arm scoring: generated, likelihood, not_stated (l.517), with no rule. G5 defines metric_kind, which is a
  different field.
- credited_ablation: set true only for replacement groups (l.461). The definition "true if an arm removes or
  replaces the credited component" exists only in EXTRACTION-PLAN-v0.2 G13 (l.358), which sessions never see.
  So removal groups are undefined.
- M-sign counts null against value as disagreement (PLAN l.243). Under G2/G4 one extractor writes null when the
  paper prints no arrow, while another applies the usual convention. M-sign then measures model priors.

Rejection test: in Stage A, M-sign below 0.90, or per-field agreement on budget_across_arms or credited_ablation
below 0.70, with most disagreements of the form null against value or convention against convention.

Fix: before Stage A, add to block K: (a) higher_is_better = true or false from an arrow or a statement in the
caption, header or text, else from a fixed synthetic list of conventions (accuracy, pass@k, BLEU, CIDEr up;
perplexity, NLL, FID, latency, steps down), else null. Or declare it script-filled from the metric lookup and
drop M-sign. (b) budget matched = every arm's steps or NFE and generation length printed and equal (define
which). (c) arm scoring with a rule tied to G5. (d) credited_ablation = true when an arm removes or replaces the
credited component (S13), false otherwise. Rerun brief_contamination.py.

**MA3. B-IP's decision function is not pinned.**

Evidence:
- s11.1 lists agreement.py's inputs (records, manifest, lookups, validator report, worked examples; l.411-418)
  but no Table B grid, although gate-phase1 mode must output n (l.446).
- icc_check.read_grid reads section B of `gate_oc_v04-log.txt`, a log file.
- B1 asks for a rerun "with Stage A's unit counts" (l.485), but unit counts are constants in gate_oc_v04.py
  (Q, l.40-60) with no command-line input. The `--icc-json` mode produces no section B (l.215-226).
- B2 and B5 hash the brief, schema and lookups, but not the grid, R, the θ grid or the B-IP seed.

Rejection test: at B2, no hashed grid file and no agreement.py `--grid` input exist; or the grid that B-IP uses
differs from the one the B2 row names.

Fix: write the grid (ICC × n → P) as `analysis/extraction/bip-grid-v1.json` from a committed run. Give
gate_oc_v04.py a `--counts-json` input. Add `--grid` to agreement.py. Hash the grid, R = 1,000, the θ grid and
seed 20264901 in the B2 row.

**MA4. The budget is approved at n_plan, but phase 1 can demand up to 120. No rule covers the gap, so a human
decision can fall after the phase-1 data exist.**

Evidence:
- PLAN s10.7 step 1: G7's budget projection uses n_plan from Stage A's U_N.
- Step 4 can then require any n up to 120, and nothing says what happens if that exceeds the approved budget.
- Table C: n_plan = 60 in 0.24-0.45 of cases at true ICC 0.05-0.10, while B-IP extends in 0.09-0.60 of
  cases (Table D).
- The reverse also happens: n_plan = 120 or none in 0.22 of cases at true ICC 0.10. That triggers the v0.3
  fallback ladder (narrowing K, cutting the frame-R sample) on the strength of a 12-record bound.
- During phase 1 the operator sees validator acceptance (G1a, G1b), and s11.1 does not exclude match lists or
  per-metric p̄ from gate-phase1 output.

Rejection test: a B2 row whose approved budget is below the n = 120 gate cost (21.1M-37.2M, s2.8) without a
pre-stated rule for that case.

Fix: the B2 row approves the budget at n = 120, or states in advance what happens if it is exceeded (for
example, that n is capped at the largest affordable grid value and P(pass | good) at that n is reported). Base
the ladder decision on the n = 120 cost, not on n_plan. In gate-phase1 mode, write only per-metric ICC, U_N and
n.

### Minor

- **mi1. M-anchorG compares labels, not matched arms.** PLAN l.240-242: credit when "the arms match by U11
  (equal normalised label, else label-core)". U11 removes "(ours)" and markers (v0.3 l.296-299), so a baseline
  "LLaDA" and an own "LLaDA (Ours)" in one training-free replacement group get the same key. Label-core equates
  "Ours" with "Ours (w/o X)". An anchor disagreement between such arms then scores as agreement. Null-null pairs
  (analysis and benchmark papers) earn credit without any judgement. Fix: map each reader's anchor_arm id
  through the one-to-one arm match inside the matched group. When two arms of a group share a key, count it as
  a disagreement unless both anchors map to the same matched pair. Report the null-null share.
- **mi2. K-attr is dominated by scoring items.** Items are three per matched group plus one per matched arm
  (PLAN l.245-246). Scoring is almost always "generated". Example: one group with 5 arms, group-level
  agreement 0.5 and scoring agreement 1.0 give K-attr = (1.5 + 5) / 8 = 0.81. M-pool covers held_fixed and
  budget through K15, but credited_ablation (QA7, RQ4) is gated only here. The simulation draws K-attr's item
  count as NB(18), independent of matched groups. Fix: define K-attr as the mean of the per-field agreements
  (or gate credited_ablation separately), and simulate its count from matched groups and arms.
- **mi3. brief_contamination.py is weaker than "guarantees".** See part 3. Fix: add the 5-gram scan with an
  allowlist (instrument ids, codebook terms), return non-zero on any non-allowlisted specific string, and scan
  backtick and curly-quoted spans.
- **mi4. The B5 fallback-share check is circular.** The lookups are seeded from the Stage A records (PLAN
  l.211-212), so their fallback share on Stage A is near 0 by construction. Fix: measure it on includes outside
  Stage A and the gate list (for example, 5 frame-R records extracted once by a single session), or report the
  phase-1 share before step 4 under a rule fixed in advance.
- **mi5. The B-IP simulation is not the production procedure and is under-powered for its claim.** It uses
  R = 200 per grid point against 1,000 in production, and 400 replicates (MC s.e. about 0.012). My 1,500-replicate
  F1_G case supports the claim (0.050). Fix: rerun Table D with R = 1,000 and at least 1,000 replicates for the
  one-bad rows. State "no inflation detected at s.e. x" instead of "does not inflate".
- **mi6. The C2 construct check covers only the flagged records.** OQ4-04 item 4 codes the 29 side-experiment
  ids and the 10 frame-R candidates. Among the other 79 C2 records, 20 have no multimodal benchmark or
  diffusion-LM name in the body (multimodal_options-log.txt). They are assumed joint-model but never checked,
  so RESP's claim that my v0.3 rejection test (a random 20 of 108) is "subsumed" is not true. Fix: add these 20
  to item 4.
- **mi7. Stale or imprecise text.**
  - PLAN header, s14 A8 and Appendix A, RESP l.11 and OQ4-17 say v0.4 is not committed. It is in b315c28.
  - PLAN l.393-394 is garbled ("... 20.9M-36.8M (mean n 118.8); 10.8M-19.0M at ICC 0.05 at ICC 0.30").
  - PLAN s5.2 keys an H unit by column index "when the validator marks both readers' cells column-verified".
    That property belongs to a pair, which exists only after matching. The order (index match among verified
    cells first, then leaf parts) is unstated.
  - The re-gate's "excluding every earlier pilot id" does not say whether unused positions 21-40 of the phase-1
    ordered lists are excluded.

---

Counts: critical 0, major 4, minor 7. Stage A may proceed once the human author's rows are entered, the T1 gate
passes and the tools are built, provided MA2 is fixed first. Stage B may proceed only after MA1, MA3 and MA4 are
resolved. Most important remaining fix: set the B-IP gate size from the per-metric ICC (the largest bound, or
the joint simulation at the per-metric vector) rather than the mean, and model M-sign and M-pool at the level at
which they actually vary (MA1).
