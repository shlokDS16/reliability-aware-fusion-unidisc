# Response to red-team audit 4 of extraction form v0.4 (2026-10-20)

Audit: `research/review/audits/2026-10-20-redteam-extraction-v0.4.md` (0 critical, 4 major, 7 minor).
Revised files: EXTRACTION-PLAN-v0.5.md (PLAN; a delta on v0.4 with a section map), extractor-brief-v0.5.md
(BRIEF), extraction-schema-v0.5.json, OPEN-QUESTIONS-v0.5.md (OQ). New in `analysis/extraction/`:
gate-config-v05.json, bip-grid-v2.json, gate_oc_v05.py, gate_rule_v05.py, gate_bip_v05.py,
gate_bip_v05_summary.py, brief_contamination_v05.py, make_brief_v05.py, make_schema_v05.py, mm_c2_nohit_v05.py,
each with its log. v0.3 and v0.4 scripts and logs are unchanged, so every earlier number still reproduces.
Status words: **fixed** (the rule asked for is in the binding text, or the rejection test passes on the
artifact named), **partly** (what remains is named), **changed** (fixed by a different route than proposed,
with reasons), **routed** (a human decision, written up). Nothing is committed and no tool is built. All
probabilities are simulations of an E0 model.

## Major

**MA2. Three of the four new criteria measured fields the session text never defined. Fixed.**
- BRIEF block K, new attribute rules (built by make_brief_v05.py from v0.4):
  - KA1 higher_is_better: (a) a printed arrow or a stated direction for that metric, even against the list;
    (b) else a fixed convention list, identical to the metric lookup's direction column (PLAN s5.4); (c) else
    null, with the unit id in doubt. G4 does not reorder the steps; bold numbers, "best" arms and knowledge
    outside the list are excluded. One value per metric within a group. Synthetic examples for each step.
  - KA2 budget_across_arms: two items (steps or NFE; generation length; an autoregressive arm's steps are its
    length); matched, reported and not reported defined on them; wall time, FLOPs and training budget
    excluded; three synthetic examples.
  - KA3 scoring: tied to G5 (likelihood when the group's quality units are likelihood metrics or the paper
    states likelihood scoring for the arm; generated when a generated-sample unit exists; not_stated
    otherwise); mixed groups resolved; two synthetic examples.
  - KA4 credited_ablation: defined for every group type (removal and replacement true; parameter sweeps,
    sub-component removals, model-class groups and analysis/benchmark/theory papers false); three synthetic
    examples. credited_ablation is now in the group field list (it was missing).
- Schema v0.5 descriptions point the four fields to KA1-KA4 (make_schema_v05.py; check_schema ok; no field
  added).
- Contamination check strengthened as asked (also mi3): `brief_contamination_v05.py` scans every quoted span
  (double, single, backtick, curly), decimals, integers of two or more digits, number runs within 300
  characters, and every word 5-gram of the session text (quoted and unquoted) against all 608 include texts,
  with ligatures and line-end hyphens normalised; a specific hit (1-5 texts) not on the reviewed allowlist
  fails the exit code. Allowlist: instrument ids by pattern, six codebook or JSON strings, 22 5-grams (16 of
  function words only, 6 of the codebook's own rule wording), each with its reason in the script and printed
  in the log. Result: v0.5 exit 0 (0 known strings, 0 non-allowlisted hits; all KA examples synthetic); the
  same check on v0.4 finds one non-allowlisted 5-gram ("table 3 ablation of the", from the E3 caption), which
  v0.5 rewords. My scan reproduces your 22 shared 5-grams on v0.4 exactly.
- Departure: M-sign is now report-only (MA1 below); KA1 still governs the field and the sign is secured by
  validator rejections and EC routing (PLAN s10.3). Your rejection test is computed in Stage A (PLAN s10.2:
  per-field agreement with the share of null against value).

**MA1. Gate size came from the mean ICC; the joint pass probability depends on the worst metrics. Fixed, with
one change of route (M-sign).**
- Measurement level first, as asked. In gate_oc_v05.py M-pool is counted over matched groups (a group-level
  flag) and M-sign over sign decisions ((matched group, metric key) pairs); K-attr is the mean of four
  per-field agreements (mi2). PLAN s10.3 defines the criteria at the same levels, so the simulation and the
  rule now measure the same thing.
- What that shows: at the decision level, M-sign is the weakest criterion by far (marginal 0.801 at n 60,
  ICC 0.10; 0.759-0.951 at n 120 over ICC 0.60-0.10; bip-grid-v2.json) and its ICC is not identifiable from
  60 records: the per-metric 80 percent bound has median 0.60, the grid maximum, at true ICC 0.10, 0.30 and
  0.50 (gate_rule_v05-log.txt Table C). Any worst-case-per-metric rule that includes it sets n = 120 in
  nearly every gate and still cannot certify 0.85 (with M-sign gated, fixed n 120 gives 0.707 under H1 and
  0.645 under H10, product approximation). M-sign is therefore report-only; the sign is set by KA1 and
  checked record by record (arrow conflicts and inconsistent signs rejected by ex_validate; every
  extractor-only or lookup-conflicting sign to EC in every record). Keeping it gated is OQ5-02 option (ii).
- Sizing rule (PLAN s10.7): per-metric Neyman 80 percent bounds for 20 ICC metrics (every ratio, F1 and
  matched-group criterion and the four K-attr fields) on the 60 phase-1 records; theta_c per criterion = the
  largest bound among the metrics it depends on; n = smallest grid n with the product of the 18 gated
  marginals at their theta_c >= 0.85, else n_cap with the step-6 statement. The product approximation is
  within -0.011 to +0.006 of the simulated joint over the 55 grid cells. The step-6 statement now fires on
  any metric (it is the product falling short, whatever metric causes it).
- Whole procedure simulated (gate_bip_v05.py, 1,000 replicates per scenario, R 1,000 as in production), 12
  good and 15 one-bad scenarios including your H1 and H10, NB shape 0.7, and the case you named where the
  other metrics sit at 0.05 (HP). Four rules on the same replicates; the binding rule P80 was selected by a
  criterion written before the run (PLAN s10.6). P80: P(pass | all good) 0.884-0.983 over all 12 scenarios
  (H1 0.922, H10 0.884, HG 0.887, HP 0.935); max P(pass | one bad) 0.074. The v0.4 rule on the same data:
  0.819-0.846 in HG, HP, H10, H1 and H3, confirming your finding.
- Cost: mean n 91.0 (ICC 0.05) to 119.7 (H10); expected gate component 17.5M-30.8M at ICC 0.10 instead of
  v0.4's 12.5M-22.0M. A cheaper rule (P50, mean n 73.8 at ICC 0.10, P(pass | good) 0.876-0.945) is offered in
  OQ5-07; it failed the pre-stated criterion only through a weak step-6 warning in H10.
- Rejection test status: "a rerun with per-metric upper bounds gives P(pass | good) < 0.85 at the n B-IP chose"
  no longer applies to the binding rule, which sets n from those bounds; in the simulation no good scenario
  falls below 0.884.

**MA3. The decision function was not pinned. Fixed.**
- `gate-config-v05.json` holds every level, line, report-only flag, icc_from list, the n grid, n_cap, target,
  bound settings (conf 0.80, R 1,000, theta grid 0.02-0.60, bisection, minimum 5 records), seeds, bootstrap
  settings, the unit-count model and the gate-record cost. gate_oc_v05.py, gate_rule_v05.py and
  gate_bip_v05.py read it (`--config`); no unit count is in a script, so B1's rerun with Stage A's counts is
  a config copy (PLAN s10.8), not a script edit.
- `bip-grid-v2.json` (per-criterion marginal and joint P over theta × n) is written by a committed run and
  stamped with a model hash of the config; gate_bip_v05.py and agreement.py refuse a grid whose model hash
  differs. No script reads a log any more.
- `gate_rule_v05.py` is the reference decision function (bounds, theta assignment, product rule) with
  self-tests, including n_cap and the step-6 flag. agreement.py gains `--config`, `--grid`, `--expect-config`
  (PLAN s11).
- The B2 row text lists config, model, grid, rule-script, brief, schema and lookup hashes, n_cap, R, theta
  grid, search, seeds and bootstrap B (PLAN s10.8). Current hashes are in PLAN s10.8.

**MA4. No rule for phase 1 demanding more than the approved budget. Fixed.**
- Decided now (PLAN s10.7 step 1): the B2 row approves the budget at n_cap = 120 (21.1M-37.2M), or sets
  n_cap to the largest grid n whose upper gate cost fits the approved budget. n_cap is written into the
  hashed config before phase 1 and never changes. If the rule demands more than n_cap, n = n_cap and the
  verdict states P_hat(n_cap) (step-6 statement); the 18-criterion rule is applied unchanged. No human choice
  remains between phase 1 and the decision.
- The fallback ladder is decided on the n_cap cost, not on n_plan; Stage A's bounds set nothing.
- gate-phase1 output is limited to the 20 bounds, P_hat(n) per grid n, n, the step-6 flag, hashes and seeds:
  no match list, no per-metric mean, no agreement value, no acceptance rate (PLAN s10.7 step 5).
- Also fixed: replacement of a record whose sessions fail twice (next unused id of its stratum), and the
  re-gate exclusion (mi7).

## Minor

- **mi1 M-anchorG compared labels. Fixed.** Anchors are mapped through the one-to-one arm match; unmatched
  anchors and shared keys score 0 unless both map to one matched pair; null-null share reported (PLAN s10.3,
  agreement.py self-tests in s11).
- **mi2 K-attr dominated by scoring items. Fixed.** K-attr is the mean of four per-field rates, simulated over
  matched groups and matched arms (line 0.71; P(passes | bad) 0.029). Residual stated in PLAN s10.3: one bad
  field still leaves K-attr passing (joint P 0.845-0.856 with one field at 0.70), so credited_ablation alone
  is printed against line 0.71 and any field below its line is flagged; gating it separately is in OQ5-08
  (P(pass | good) at n 60 falls from 0.854 to 0.799). **Partly** in that sense.
- **mi3 contamination script weaker than claimed. Fixed** (MA2 above).
- **mi4 circular fallback check. Fixed.** 5 frame-R ids outside Stage A and the gate lists (seed 20266200),
  extracted once before B2; share reported; one lookup revision allowed above 0.05 (PLAN s10.2).
- **mi5 simulation not the production procedure. Fixed.** R = 1,000 per bound evaluation as in production,
  1,000 replicates for every one-bad row; the statement is "no inflation detected at MC s.e. about 0.007"
  (P80 one-bad values at most 0.007 above X80 on the same replicates). The simulated gate bootstrap stays at
  B = 500 against production 4,000 (as in v0.3-v0.4). The bound search is now bisection in both production and
  simulation, so the two use the same function.
- **mi6 construct check covered only flagged records. Fixed.** The 20 ids are listed (mm_c2_nohit_v05.py) and
  added to the human check under every option (OQ5-04). My v0.4 claim that your random-20 test was
  "subsumed" was wrong.
- **mi7 stale text. Fixed.** v0.4 is in b315c28 and the review in 5d781cc (PLAN s14 A8); the garbled cost
  line is replaced (PLAN s2.8); the H-key match order is stated (PLAN s5.2); the re-gate excludes all 120
  listed ids, used or not, plus Stage A and mi4 ids (PLAN s10.7 step 8).

## What still blocks

Stage A: human rows (A2, A3 with row 36 and OQ5-13, A5 with the 20 mi6 ids, A10), A1 T1 gate, A4 block-F
check, A6 red-team review of v0.5, A7 tools (ex_validate with the sign checks, agreement.py, draw_pilot.py,
fixtures, lookups), A11 we-expected.jsonl. MA2 is no longer a blocker.

Stage B: B1 (Stage A unit counts into a config copy, grid v3, B-IP rerun, mi4 check), B2 row (rule, OQ5-02,
levels, n_cap and budget, hashes), B3-B6.
