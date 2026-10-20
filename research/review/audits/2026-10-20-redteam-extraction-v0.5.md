```yaml
agent: red-team
date: 2026-10-20
brief: fifth adversarial review of extraction instrument v0.5 (Paper 1); verify the claimed fixes for v0.4 MA1-MA4 and minors by text and by re-running; attack M-sign report-only and its compensating controls, the per-metric gate sizing and the pre-fixed budget rule, brief_contamination_v05; list exactly what blocks Stage A and Stage B
sources_examined:
  - research/CONTRACT.md
  - research/review/audits/2026-10-20-redteam-extraction-v0.4.md (my previous report, full)
  - research/review/extraction/EXTRACTION-PLAN-v0.5.md (full), RESPONSE-TO-REDTEAM-v0.4.md (full), OPEN-QUESTIONS-v0.5.md (full)
  - research/review/extraction/extractor-brief-v0.5.md l.1-30, 50-90, 395-600 (G1-G6, block H, block K with KA1-KA4, adjudication paragraph); diff against v0.4
  - research/review/extraction/extraction-schema-v0.5.json (KA field descriptions; all non-description string values, by script)
  - research/review/extraction/EXTRACTION-PLAN-v0.4.md s9 (lookups) and s10.3 (grep); EXTRACTION-PLAN-v0.3.md s10.5
  - analysis/extraction/gate-config-v05.json, gate_rule_v05.py, gate_oc_v05.py, gate_bip_v05.py, gate_bip_v05_summary.py, brief_contamination_v05.py (read in full); make_brief_v05.py, make_schema_v05.py, mm_c2_nohit_v05.py (run); icc_check.icc_anova; bip-grid-v2.json; gate_bip_v05-results.json; all v0.5 logs
  - research/sources/md/fulltext-pymupdf/M08100.txt l.489-507 (one real table header); all 608 include texts by script
coverage: >
  Re-ran from the worktree root into my scratchpad and diffed against the committed logs: make_brief_v05 and
  make_schema_v05 (rebuilt in a scratch tree from the v0.4 files: sha256 d390f966... and b021c041..., identical to
  PLAN s10.8; check_schema ok), brief_contamination_v05 (byte-identical, exit 0), mm_c2_nohit_v05 (identical),
  gate_rule_v05 --reps 200 (identical apart from elapsed), gate_oc_v05 --calibrate (byte-identical), --table-a
  (identical apart from elapsed), --grid-out (grid sha256 64628119..., identical), gate_bip_v05 for scenarios
  H10 and "B30 G1 EB" with the committed seeds (identical to the log, every rule, n distribution and median
  bound). The other 25 B-IP scenarios were not re-run; their summary numbers in PLAN s10.6 and s2.8 were
  checked against gate_bip_v05_summary-log.txt and the results json. Hashes of config, grid, rule script, brief
  and schema equal PLAN s10.8. New scratch scripts (read-only imports of the committed modules; not committed):
  rt5/coupling.py, rt5/hiagree.py, rt5/select.py, rt5/bcgeneric.py, rt5/arrows.py with their .out files in the
  session scratchpad. NOT covered: the worked-example derivations; the 108 C2 full texts; ex_validate,
  agreement.py, draw_pilot.py and the lookups (not built). The brief allows one output file, so no ledger row
  was added. The brief asks for a fix per finding, so fixes are given (a deviation from my agent definition);
  the criticism is not softened. Severity: critical = blocks the stage it names outright; major = must be
  resolved before the stage named; minor = should be fixed, does not block.
claims:
  - statement: Every v0.5 number I checked reproduces on re-run (elapsed time aside); the brief, schema and grid rebuild byte-identically; the hashes in PLAN s10.8 are correct.
    status: supported
    evidence: scratchpad bc05.out, mm.out, rule.out, cal.out, grid.out, tableA.out, mk/, rt5/bip-sub.out against analysis/extraction/*-log.txt
    level: E3
    confidence: 0.95
  - statement: The product approximation ("reach") that the rule-selection criterion uses is biased low by 0.025-0.066 when the matched-group criteria have a higher ICC than F1_G, and high by 0.014 when F1_G has the higher ICC. With reach replaced by the simulated pass probability at n = 120, the plan's own pre-stated criterion selects P50, not P80.
    status: supported
    evidence: scratchpad rt5/coupling.out (2,000 fixed-n gates per cell), rt5/select.out (committed results json)
    level: E3 (simulation of the plan's E0 model)
    confidence: 0.85
  - statement: Under P80, an instrument whose agreement is above the good level on M-anchorG and M-pool (0.95) gets n = 120 in 0.88 of gates and the step-6 "target out of reach" statement in 0.67, while its P(pass) is 1.000.
    status: supported
    evidence: scratchpad rt5/hiagree.out (600 replicates per scenario)
    level: E3 (simulation of the plan's E0 model)
    confidence: 0.85
  - statement: Under KA1 a common DLM table layout yields a null sign that EC cannot fill, and 258 of the 608 include texts print no arrow and no higher/lower-is-better sentence anywhere.
    status: supported
    evidence: extractor-brief-v0.5.md l.508-521, l.588-593; M08100.txt l.491-507 ("(Score | TPF)"); scratchpad rt5/arrows.out
    level: E3 (count by script); the share of K units affected is unknown
    confidence: 0.75
  - statement: brief_contamination_v05 does not guarantee that the session text holds no drawable-paper string, but the v0.5 session text holds none that I can find.
    status: supported
    evidence: analysis/extraction/brief_contamination_v05.py l.15-17, 40-47, 81-82, 168-191; scratchpad rt5/bcgeneric.out
    level: E3
    confidence: 0.85
competing_explanations:
  - The sign gap (MJ1) may be small in practice if the lookup built from Stage A gives benchmark-default directions to most unmapped strings. The plan does not say it will, and s5.4 says the lookup equals the brief's list.
  - The bias in "reach" (MJ2) is conservative in every heterogeneous scenario the plan ran. It changes which rule the criterion picks, and it makes the step-6 statement fire falsely. It does not inflate false passes.
unknowns:
  - share of K units whose sign is null after KA1 and after the lookup; share routed to EC; EC sign accuracy
  - real per-metric agreement levels (above or at the good levels), real ICCs and unit counts (Stage A, then B1)
next_test: {hypothesis: "under brief v0.5 most K units get a non-null sign from KA1 or the lookup", intervention: "in Stage A, report for every K unit the KA1 step used (a, b, c), the lookup direction, and the final sign under a written derivation rule", primary_metric: "share of K units with final sign null, and share routed to EC", falsifier: "final-null share above 0.10 or EC-routed share above 0.30", gpu_hours: 0}
```

# Red-team audit 5: extraction instrument v0.5

Verdict: **no critical finding. Stage A may proceed once the human author's rows are entered, the T1 gate
passes and the tools are built. Stage A's report must include the sign-coverage counts of MJ1. Stage B may not
proceed until MJ1, MJ2 and MJ3 are resolved and B1-B6 are met.**

v0.5 answers every v0.4 finding in substance, and every number I re-ran matches its log. The per-metric sizing
fixes the under-sizing that MA1 showed. The decision function is pinned and hashed. The budget rule is fixed
before phase 1. The remaining problems are of three kinds:
1. The sign that the review pools is now secured "by process", but the process has no stated final-sign rule
   and no measured accuracy, and it leaves a common table layout unsigned (MJ1).
2. The rule-selection step rests on a biased approximation (MJ2).
3. The sizing rule penalises an instrument that does better than the good level (MJ3).

References: PLAN = EXTRACTION-PLAN-v0.5.md, BRIEF = extractor-brief-v0.5.md, RESP = RESPONSE-TO-REDTEAM-v0.4.md,
OQ = OPEN-QUESTIONS-v0.5.md. Scratch paths are relative to the session scratchpad named in my reply.

---

## 1. Re-runs and fix verification

All re-runs were from the worktree root, with output to the scratchpad. Every one matches (details in coverage
above). I also checked the derived figures:
- PLAN s2.8 costs: mean n × 176k-310k, for example 99.4 → 17.5M-30.8M. The heterogeneous range 16.9M-37.1M runs
  from H6 (96.3) to H10 (119.7).
- The OQ5-07 cap costs: 105 × 310k = 32.6M.
- "8 of the 15 one-bad values below X80, at most +0.007 above" (my count from the summary log: 8, maximum
  +0.007 for M-pool).
- V4 at 0.819-0.846 in HG, HP, H10, H1 and H3.

| v0.4 finding | RESP status | Verified | Note |
|---|---|---|---|
| MA1 sizing from the mean ICC | fixed | **real** | P80 reaches 0.884-0.983 in the 12 scenarios (H10 and B30 G1 EB re-run identically). M-pool is modelled over groups and M-sign over sign decisions (gate_oc_v05.py l.158-167). New problems in the replacement design: MJ2, MJ3. |
| MA2 undefined gated fields | fixed | **partly** | KA1-KA4 are in BRIEF l.507-554 with synthetic examples, and the schema points to them. KA2-KA4 are determinate apart from mn3. KA1 is determinate, but it gives null for common layouts, and nothing downstream defines the final sign (MJ1). |
| MA3 decision function not pinned | fixed | **real** | Config, grid (model-hash stamped, checked in gate_bip_v05.py l.141) and rule script are hashed. agreement.py is not built, so its `--expect-config` refusal is unverified. |
| MA4 budget gap | fixed | **real, one hole** | n_cap is fixed in the B2 row, the budget is checked at the n_cap cost, and the phase-1 output is restricted. Hole: the list length leaves no spare ids for the replacement rule (mn1). |
| mi1 M-anchorG via labels | fixed | real (text) | PLAN s10.3; self-tests specified, not built. |
| mi2 K-attr diluted | partly | real | Mean of four fields. A single bad field still passes the gate in 0.845-0.856 of gates (tableA log), so credited_ablation is report-only plus a flag. Declared. |
| mi3 contamination script | fixed | **partly** | Much stronger, but it does not guarantee absence (mn4). |
| mi4 circular fallback check | fixed | real | 5 frame-R ids, seed 20266200. Order issue (mn5). |
| mi5 simulation ≠ production | fixed | real | R = 1,000, 1,000 replicates. The wording is now "not detected at s.e. about 0.007". |
| mi6 C2 construct | fixed | real | The 20 ids and the id-list hash reproduce. |
| mi7 stale text | fixed | real | A8 cites b315c28 and 5d781cc. The cost line is repaired. The H-key order and the re-gate exclusion are stated. |

## 2. M-sign report-only: is it defensible, and are the controls enough?

**The argument given is not the real reason.** PLAN s10.3 and OQ5-02 justify report-only by "ICC not
identifiable at the decision level". That is true: the median bound is 0.60 at every true value, because the
ANOVA estimator returns 0 when every record agrees perfectly (icc_check.py l.50-53). But the gated M-sign fails
for another reason: there are few sign decisions per record (about c + Poisson(0.6c)), and the line (0.92) sits
close to the good level (0.97). Its marginal pass probability is 0.864 at **ICC 0.02**, n 60 (bip-grid-v2.json),
where clustering plays almost no part. So the gate cannot measure the sign at any n it can afford. That is a
legitimate reason to stop gating it. It is also a reason why the replacement controls must carry the whole load.

**Report-only is defensible only if the extractor's value never sets the final sign without a check.** The
plan comes close to this (s10.3 item 3), but four gaps remain:
1. **No final-sign rule.** Nowhere does the text say which value the synthesis uses. It does not say "the
   lookup direction when the metric is mapped and the direction is non-null; else the EC value; else unsigned
   and excluded from signed pooling". Item 3 implies the lookup is the reference, but it does not say whether
   extractor null against lookup value counts as a "conflict".
2. **KA1 leaves a common layout unsigned, and EC cannot fix it.** KA1(b) is a closed list. KA1(c) gives null
   for anything else, and BRIEF l.518-519 forbids directions taken "from your own knowledge of a metric that is
   not in the list". EC writes final values "under the rules above" (BRIEF l.590-593), so EC also writes null.
   - Example: in M08100 Table 1 (l.491-507) the metric is printed as "(Score | TPF)". TPF is true under (b).
     "Score" has no arrow, no statement and is not on the list, so it is null.
   - Columns headed by benchmark names alone, and GenEval, MAUVE or "Overall" columns, fall the same way.
     metric_printed has no rule for a table that prints no metric name.
   - 258 of the 608 include texts contain neither an arrow character nor a higher/lower-is-better sentence
     anywhere (rt5/arrows.out). In those papers every sign depends on the list.
   - M-sign excludes null-null pairs (PLAN l.193-194), so it is blind to this loss.
3. **s5.4 contradicts itself.** It says the lookup's direction column is "exactly KA1(b)", then says that metric
   ids added from Stage A get a direction when it is not paper-dependent. Once one such id exists, the brief
   and the lookup disagree. Hashing both in the B2 row does not make them equal.
4. **Nothing happens when M-sign is low, and the final-sign accuracy is never measured.** credited_ablation's
   report-only line has a consequence ("flagged field", s10.3). M-sign's 0.92 line has none, and the v0.3
   per-field flag (P ≤ 0.01 under 0.85) is far too loose for a 0.97 target. The EC's sign decisions and the
   lookup's directions are not compared with anything (B6, the human gold subset, is undecided). The EC
   sign-review load is not in the s2.8 cost.

The ex_validate arrow check covers less than KA1(a) (mn2). Taken together, these points make MJ1 below.

## 3. Per-metric sizing and the pre-fixed rules

**Valid within the model.** The bound is a correct one-sided inversion per metric. theta_c takes the maximum
over the metrics each criterion depends on. The type-I picture holds: max 0.074, the G1 EB line property,
re-run identically. I found no step between phase 1 and the decision that needs a human choice. n_cap, the
target, the grid, R, the theta grid, the bisection, the seeds and the output restriction are all declared.

**Problems:**
- **"Reach" is biased, and the selection rests on it (MJ2).** The grid marginal of a matched-group criterion at
  theta was simulated with F1_G at the same theta. F1_G's ICC sets how lumpy the matched-group counts are. In
  the heterogeneous scenarios F1_G stays at 0.10, so the true M-pool marginal is higher than the grid says:
  - H10, n 120: 0.899 against 0.874; joint 0.875 against reach 0.850.
  - HG: 0.894 against 0.863.
  - HP: 0.934 against 0.906.
  - The reverse case, F1_G 0.6 with the others at 0.05, at n 90: joint 0.862 against reach 0.876 (rt5/coupling.out).

  The plan's "accurate within -0.011 to +0.006" holds only on the common-ICC grid, where this coupling cannot
  show. The selection criterion puts H10 in the "unreachable" class because its reach is 0.8499 ("just below
  0.85 in floating point"). With reach taken as the simulated pass probability at n = 120 (X80: 0.885), H10 is
  reachable, P50 meets every condition, and P50 is selected: mean n 93.6 against 109.9 (rt5/select.out). The
  plan therefore tells the human author (OQ5-07) that P50 "failed the pre-stated criterion". That statement is
  an artefact of the bias.

  Two further points:
  - The claim that the criterion was "written before the run" has no artifact. v0.5 is uncommitted;
    gate_bip_v05_summary.py (06:02) and the plan (06:08) post-date the results (06:01). Its one-bad bound of
    0.08 sits just above the observed 0.069-0.075. The config (05:15) does pre-declare the product rule at
    conf 0.80, which supports P80 as the declared design, but not the selection claim.
  - The same bias makes the step-6 statement ("no grid n reaches 0.85") fire in 0.81 of H10 gates and 0.85 of
    HG gates, although the target is reached at n 120 (0.875-0.894). Step 7 hands that statement to the human
    author after a FAIL.
- **Ceiling penalty (MJ3).** P_c is read at the criterion's **good** level, whatever the observed level. The ANOVA
  estimate collapses toward 0 near perfect agreement, and the Neyman bound then goes to the grid maximum.
  Results from rt5/hiagree.out (600 replicates per scenario; ICC 0.10; others good):

| Scenario | P80 mean n | share n = 120 | P(step 6) | P(pass) |
|---|---|---|---|---|
| G10 (control) | 100.7 | 0.26 | 0.07 | 0.975 |
| M-class 0.97 | 106.4 | 0.35 | 0.10 | 0.983 |
| M-anchorG, M-pool 0.95 | 117.7 | 0.88 | 0.67 | 1.000 |
| M-class, M-anchorG, M-pool 0.97 | 119.8 | 0.99 | 0.95 | 1.000 |
| K-attr fields 0.97 | 100.9 | 0.26 | 0.06 | 0.975 |

  A better instrument costs the full n_cap, and the verdict says that the target is out of reach. This is the
  same mechanism that removed M-sign, now on gated criteria. Table D's means and costs, and the meaning of the
  step-6 flag, hold only when every quantity sits exactly at its good level.
- **The budget rule is fixed, but the list it draws from is too short (mn1).**

## 4. brief_contamination_v05: does it guarantee no drawable-paper strings?

No, but v0.5 is clean in practice.
- Exit 0 means that every hit found in 1-5 include texts is on an allowlist that the author curates. It does
  not mean that no hit exists. The allowlist grew after the v0.5 run ("of every arm in this", found only in
  M14075). Several 5-grams are labelled "function words only" although they are not ("model stands in for the",
  "in this family is a").
- Strings found in more than 5 include texts pass unseen. The log does not list them. A phrase or number that a
  drawable paper shares with five or more other includes, such as a widely quoted result, would pass. I listed
  them (rt5/bcgeneric.out): 80 generic spans or numbers and 1 generic 5-gram ("the number of sampling steps",
  44 texts). All are synthetic numbers that recur by chance, or codebook vocabulary. Nothing is
  paper-specific.
- Only the schema's description strings are scanned. The other string values (1 title, 5 const, 16 pattern,
  250 enum) are codebook ids, which I checked. dispatch.json, the EC lookup files and the validator return
  messages are session inputs that are not scanned.

## 5. What blocks Stage A and Stage B

**Stage A (development, 12 records)**, beyond the human author's decision rows (A2, A3 with rows 34-36 and
OQ5-13, A10):
1. A1: T1 full-text gate PASS. The audits folder holds re-audit 1 (FAIL) and no later pass.
2. A4: gate-auditor check of block F and C-F1a to C-F1e. There is no audit file.
3. A5: human check OQ5-04 including the 20 mi6 ids. mm-construct.jsonl, strata-overrides.jsonl and
   duplicate-works.jsonl do not exist.
4. A7: none of ex_dispatch.py, ex_validate.py (with the v0.5 sign checks and their four cases), the fixture
   generator, draw_pilot.py, the extraction agreement.py or the lookup CSVs exists. analysis/census/agreement.py
   is a different tool.
5. A11: we-expected.jsonl does not exist, and it holds no KA attributes, so KA1-KA4 have no reference values in
   Stage A.
6. A9: tools/ft_isolation_check.py and tools/ft_model_check.py exist; "passing" was not verified here.
7. OQ5-17: commit v0.5 so that the frozen hashes of A12 refer to a committed state.
8. Condition from MJ1: agreement.py stage-a mode must report, per K unit, the KA1 step, the lookup direction and
   the final sign under a written rule. It must also report the final-null share and the EC-routed share. The
   current s10.2 reports only per-field agreement with null-against-value, which is blind to null-null.

**Stage B (gate)**: MJ1, MJ2 and MJ3 resolved, then B1 (Stage A counts, grid v3, re-runs that are wide enough to
re-apply the selection criterion: mn5), B2 (rule, OQ5-02, levels, n_cap, hashes; signed), B3, B4 (with spare ids:
mn1), B5 and B6. B6 is also where the sign accuracy of MJ1 gets measured.

---

## Findings

### Major

**MJ1. The sign that the review pools has no stated derivation and no measured accuracy, and KA1 leaves a
common table layout unsigned.** (Before Stage B; Stage A must measure it.)

Evidence: part 2. The key points:
- BRIEF l.508-521: KA1 has a closed list and forbids outside knowledge.
- BRIEF l.590-593: EC is bound by the same rules.
- PLAN s5.4 l.155-159 contradicts itself.
- PLAN s10.3 l.192-201 has no final-sign rule and no consequence for M-sign below its line.
- M08100 l.501-507 prints "(Score | TPF)", which gives "Score" a null sign.
- 258 of 608 includes have no direction cue at all (rt5/arrows.out).
- M-sign excludes null-null pairs.
- The gated M-sign marginal is 0.864 at ICC 0.02, n 60, so "ICC non-identifiable" is not what makes it fail.

Rejection test: in Stage A, the share of K units with final sign null above 0.10, or the EC-routed share above
0.30 with no EC cost line; or, at B6, final-sign agreement with the human gold subset below 0.97.

Fix:
- Write the final-sign derivation into PLAN s10.3: lookup direction when mapped and non-null; else EC under KA1;
  else unsigned, excluded from signed pooling, share reported.
- Keep one direction list that the brief and the lookup both use. Either let KA1(b) admit the lookup's
  benchmark-default entries (hashed), or define metric_printed for tables that print no metric name.
- Give M-sign below 0.92 a pre-stated consequence (flagged field: KA1 revised and re-measured).
- Measure final-sign accuracy against the human gold subset. Cost the EC sign review in s2.8.

**MJ2. The rule-selection step and the step-6 statement rest on a product approximation that is biased in
exactly the heterogeneous scenarios they target. Corrected, the plan's own criterion selects P50.** (Before the
B2 row.)

Evidence: part 3.
- rt5/coupling.out: grid-product bias of -0.025 to -0.066 in H10, HG and HP at n 90 and 120, and +0.014 in F60
  at n 90. In each case the gap is carried by the matched-group marginals.
- rt5/select.out: with reach = X80's P(pass), P80, P50 and X80 all meet the criterion, and P50 has the smallest
  mean n.
- gate_bip_v05_summary-log.txt: P(step 6) under P80 is 0.81 in H10 and 0.85 in HG, where the n-120 pass
  probability is 0.885 and 0.890.
- The claim "criterion fixed before the run" has no artifact that predates the results.

Rejection test: any B2 row that cites "P50 failed the pre-stated criterion", or that cites the reach column as
"the most any rule capped at 120 can give".

Fix:
- Compute reach by simulating the gate at n_cap at each scenario's true ICC vector, not by the product.
- Re-apply the criterion, and record P80 against P50 as a reasoned decision in OQ5-07.
- Make the matched-group marginals conditional on F1_G's bound (a two-dimensional grid), or reword step 6 as
  "the conservative product bound is below the target" rather than "out of reach".
- Commit any selection criterion before the run it judges.

**MJ3. Rule P80 penalises an instrument that agrees better than the good level: n goes to n_cap and the step-6
statement fires.** (Before the B2 row.)

Evidence: part 3 table (rt5/hiagree.out). The mechanism is icc_check.icc_anova l.50-53, plus P_c being read at
the good level (gate_rule_v05.py n_product; gate_oc_v05 grid built at M.levels()). Table C already shows the
same collapse for M-sign.

Rejection test: in Stage A, any gated matched-group criterion whose agreement estimate on the 12 records is
above 0.93, which means phase 1 will probably return its bound at 0.60.

Fix:
- Add above-good scenarios to Table D, and state the mean n and P(step 6) for them in s2.8 and OQ5-07.
- Then either evaluate P_c on a (theta × level) grid at a level fixed by a pre-stated rule from phase 1 (for
  example the phase-1 lower bound clipped to [bad, good]), with type I re-simulated, or accept the cost
  explicitly and reword step 6 as in MJ2.

### Minor

- **mn1. The ordered lists leave no spare ids.**
  - Evidence: config per_stratum_list 40 = n_cap / 3. PLAN s10.7 step 2 replaces a twice-failed record "by the
    next unused id of its stratum's list", and step 4 extracts "positions 21 to n/3".
  - At n = 120 no unused id remains. A phase-1 replacement takes position 21, which the extension then
    re-uses. The re-gate excludes all 120 listed ids.
  - Fix: draw 40 + k ids per stratum, with the spare positions reserved for replacement and named in the
    config, or state that the extension skips ids already used as replacements.
- **mn2. The arrow check is narrower than KA1(a).**
  - ex_validate checks arrows only in column_printed (the leaf; PLAN s10.3 item 2). KA1(a) also accepts row
    labels, legends, upper header levels and caption or text sentences. H units from abstract prose have no
    column_printed.
  - Fix: check the full column path, the row label and the caption for arrows, and route a direction sentence
    the validator cannot parse to EC.
- **mn3. KA2 item (1) is "steps or NFE".**
  - When the two differ (classifier-free guidance doubling the evaluations per step, caching, speculative or
    early-exit schemes), two readers can apply the rule correctly and still code matched and reported.
  - Fix: name which item takes precedence (NFE when stated, else steps), with a synthetic example.
- **mn4. brief_contamination_v05 overstates what it certifies** (part 4).
  - Fix: print the generic hits in the log. Lower the generic threshold, or check generic multi-token spans
    against the drawable set separately. Correct the allowlist labels. Freeze the allowlist (hashed) before the
    check that it serves. Scan dispatch.json and the EC lookup files.
- **mn5. The B1 re-run is too narrow, and the checklist order conflicts.**
  - PLAN s10.8 re-runs only G10, H1, H10 and the one-bad rows with Stage A's counts, but the selection criterion
    needs all 12 good scenarios. Nothing says what happens if the re-run puts P80 below 0.85 − 2 s.e.
  - B1 requires the mi4 check to be done. The mi4 draw requires the B4 gate draw first (PLAN s10.2, s11).
  - Fix: re-run the full scenario set at B1 and pre-state the action. Order the checklist so that B4's draw
    comes before the mi4 check, with no person looking at the gate ids.

---

Counts: critical 0, major 3, minor 5. Stage A: GO once the human author's rows are entered, the T1 gate passes
and the tools are built (with the MJ1 sign-coverage counts in stage-a mode). Stage B: NO-GO until MJ1-MJ3 and
B1-B6 are met. Most important remaining fix: write and measure the final-sign pipeline (derivation rule, one
shared direction list, a consequence for low M-sign, accuracy against the gold subset), because the review pools
signed contrasts and the gate no longer measures the sign (MJ1).
