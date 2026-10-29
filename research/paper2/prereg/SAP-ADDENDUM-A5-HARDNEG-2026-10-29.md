```yaml
agent: statistician
date: 2026-10-29
brief: >
  SAP addendum A5 (final) for Paper 2 (GATE on UniDisc 1.4B): a new confirmatory family H on SugarCrepe hard negatives, added
  after the primary family P was analysed (label NEGATIVE). Approved by Shlok ("Yes, add it", D0080). Reconciled with the
  implementation draft at 336b31c6; specifies the H3 go/no-go module. No H data exists. Revision r1 answers the red-team
  A5 signature (conditions C5-1 to C5-8).
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md section "A5 signature" (r1; findings F1-F9, conditions C5-1 to C5-8)
  - research/paper2/prereg/SAP-ADDENDUM-A5-HARDNEG-DRAFT-2026-10-29.md (r0; committed by the lead as 86064e57)
  - research/paper2/CONFIRM-EVENING-2026-10-28.md section 14; research/ledgers/decisions.jsonl row D0080; commit 80b06c00
  - research/paper2/data/HARDNEG-FEASIBILITY-2026-10-29.md; research/paper2/prereg/SAP-GATE-2026-10-28.md (as listed in r0);
    SAP-ADDENDUM-A4-2026-10-28.md; PREREG-GATE-v4-2026-10-28.md; A2.3-AUDIT-PS-2026-10-29.md; NOVELTY-CHECK-INFFUS-2026-10-28.md
  - runs/P2-GATE-M4/analysis.json (P section and others, as r0); runs/P2-GATE-M3/family.json (full top level, not `rungs`)
  - worktree agent-aef5385b66d6a3cbd at 336b31c6: research/paper2/method/IMPL-J-HARDNEG-DRAFT-2026-10-29.md (full); diff 6d539fc2..336b31c6 of
    exp_p2/run_gate_m4.py, exp_p2/run_gate_m3.py, exp_p2/gate/gate_driver.py, exp_p2/gate/analysis_m4.py; exp_p2/gate/build_hardneg_items.py (grep);
    exp_p2/run_gate_m4.py 108-130 (build_conditions); exp_p2/gate/analysis_m4.py 46-118, 222-262, 606-660; exp_p2/gate/stats.py 10-13; exp_p2/gate/seeds.py 9-17
  - runs/P2-GATE-FOIL/pool.json and runs/P2-GATE-FOLDS/folds.json (image ids only)
coverage: >
  Not read: any S2, FOIL, suite, M5 or Tier-3 output; the new tests of 336b31c6 (only their description in IMPL-J); headroom.py (MIN_NV = 90 taken
  from IMPL-J and the coordinator). No GPU used. No SugarCrepe item has been scored by UniDisc.
claims:
  - statement: "The M3 sample-size proxy overstated the realised GATE-M discordance on the P test fold (predicted 47.5 discordant items in 500; realised 1, 0 and 4)."
    status: supported
    evidence: "runs/P2-GATE-M3/family.json n_rule; runs/P2-GATE-M4/analysis.json primary.per_corruption n_d"
    level: E4
    confidence: 0.95
  - statement: "analysis_m4 can analyse H4 unchanged if runs/P2-GATE-H3/family.json carries endpoint 'd', the tested corruptions in `family`, and n_rule.rule in {R1, R2, NO-GO} with n_rule.test_fold."
    status: supported
    evidence: "exp_p2/gate/analysis_m4.py:84-104 (primary: m = 3 over config.REALISTIC, p = 1 for absent corruptions), 222-262 (outcome_reading; N_MIN), 619-653 (main)"
    level: E3
    confidence: 0.85
  - statement: "Every image of the FOIL pool lies inside folds.json, so the builder's exclusions already keep H and family B disjoint."
    status: supported
    evidence: "CPU check 2026-10-29: 540 FOIL pool images, 0 outside cal/head/test/test_ext"
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - every H outcome; UniDisc's clean accuracy on SugarCrepe pairs; whether UniDisc's training data contain COCO val2017 captions or images (U8)
  - whether run_gate_m4 with a one- or two-corruption family and the frozen denoise_for passes its PS checks (a required test, A5.11)
next_test: {hypothesis: "HJ/HN/HS of A5.4", intervention: "H3 pilot (50 items, M4 stage) then H4 (300 items)", primary_metric: "paired accuracy difference GATE-M minus none, exact McNemar, Holm m = 3", falsifier: "H-NOGO at H3, or no Holm rejection with b > c at H4", gpu_hours: "about 3.7 wall-h (H3 0.75, H4 2.9 at n = 300), estimate"}
```

# SAP Addendum A5 (2026-10-29): family H, hard negatives (SugarCrepe) on new COCO images

Author: statistician. Final version of the draft r0 (`SAP-ADDENDUM-A5-HARDNEG-DRAFT-2026-10-29.md`, committed by the lead as `86064e57`, kept
unchanged). Written 2026-10-29 between Shlok's answer (10:23:21 IST) and the lead's commit `b32e72a1` (10:30:07 IST); the earlier
"from about 10:40 IST" was wrong (C5-5). Revision r1 written from 10:38 IST on 2026-10-29, before any H item. A separate file beside the SAP. **Precedence:** A5 > A4 > A3b > A3 > A2b > A2 > A1 > SAP body,
**only on the points listed here**. Family P, PS, S-M, S-Z, S-DN, S-D, S-D2, S-C, S2, B, R, E-dec, E-pred, the suite, the outcome book of A4.2 and
every earlier rule stand unchanged.

## Revision r1 (2026-10-29, red-team A5 signature, conditions C5-1 to C5-8; before any H item)

| Condition | Change in r1 | Where |
|---|---|---|
| C5-1 (F1) | One placement rule, stated once: H never in title, abstract, highlights, graphical abstract, significance statement, the Conclusion (all of it), the opening of 6.1, limitations, future work, cover letter or response text, captions other than H's own, README, Zenodo or repository text; the r0/final item "H may appear later in the conclusion" is struck | A5.1, A5.9 "Placement" |
| C5-2 (F2) | The disclosure paragraph lists everything computed and committed before H was designed and what the designer read; the motive clause about few changed decisions is removed; Must-not 1 governs Methods and the deviations box too | A5.14, A5.9 Must-not 1, A5.0 |
| C5-3 (F3) | Stop rule: H is the last confirmatory family added after the P outcome; any later post-P analysis is Tier 3, labelled and listed in the deviations box; placement rules and D-H2 may only be tightened after the first H3 item, and D-H2 cannot change once any H output exists | A5.1, A5.9 item 5, A5.15 |
| C5-4 (F4) | Length-matched (LM) and add_* (LA) counts are the primary description of every H result; a gain is stated without the length clause only if b_LM > c_LM and the LM 95 percent lower bound exceeds -D_H; harms symmetric | A5.7 |
| C5-5 (F5) | D-H2 and D-H4 restated as the lead's defaults under Shlok's veto; D-H3 unattended needs Shlok's words, else attended only; time of writing corrected; ledger rows for D-H2 to D-H4 are the lead's precondition | header, A5.0, A5.12, A5.15 |
| C5-6 (F6) | No person opens H3 rows, arrays, chunk outputs or logs before the H4 analysis is committed; signed H3 numbers are never reported if H4 is not analysed; `h3_gonogo` tests cover stdout, stderr and logs | A5.8, A5.5a, A5.16 |
| C5-7 (F7) | `decide` deadline defined; `G_max_headroom` defined for the H-NOGO sentence; the x4 bound recorded when n_H4 = 200 (the GO rule stays x6); per-corruption projections in the power statement | A5.5a, A5.9 |
| C5-8 (F9) | Merge only after S2 has ended and after a byte-identical regeneration of the committed P, Tier-3, E-dec and E-pred outputs from the merged code; the lead's precondition, recorded in pin row A-6 | A5.0, A5.11 |
| F8 (informational) | One corruption per H-POS sentence; clean-image control clause on every H-POS and H-MIXED sentence | A5.9, A5.16 |
| unchanged | H3 rule (a), (b), validity 45, R1/R2/NO-GO thresholds, time-rule constants and the bounds 12:27, 12:36, 13:42 IST (checked by the red team) | A5.5, A5.12 |

## Changes r0 -> final

| # | r0 (draft) | final | Reason |
|---|---|---|---|
| 1 | DRAFT, pending Shlok | approved; D-H answers recorded with sources (A5.15); "DRAFT" removed | D0080, 80b06c00 |
| 2 | builder `exp_p2/gate/h_items.py`, files under `runs/P2-GATE-H/`, seed 20261102, round-robin order, H3 = list positions 1-50, gids 3000-3349 | the implemented builder `exp_p2/gate/build_hardneg_items.py` and its file `runs/P2-HARDNEG-ITEMS/folds_hardneg.json` (`head` = H3, `test` = H4); seed `[SEED_GATE, 9]`; per-subset quotas H3 7 x 6 + 8, H4 43 x 6 + 42 (which subset gets 8 or 42 drawn by the seed); scarcest subset first; a seeded shuffle orders each fold; gids 6000 + idx (H3), 7000 + idx (H4) | statistically equivalent (stratified, one row per image, fixed seed, built before any score); the code exists and is tested |
| 3 | exclude the FOIL pool explicitly | no extra exclusion; H-L4 stays as an assertion | 0 FOIL images outside the folds (claim 3) |
| 4 | H3 runs the M4 stage (implicit) | **H3 must run `run_gate_m4`**, not `run_gate_m3` as at 336b31c6, on a derived file whose `test` list is the H3 items, with a plan family file (n = 50) | rule (b) needs GATE-M decisions; M3 rows have no gate fields; `headroom.py` (MIN_NV = 90) cannot serve n = 50 and is not used |
| 5 | `--n-rule PATH` flag scoped to run ids `P2-GATE-H*` | the implemented `--family-run` (n check against `runs/<family_run>/family.json`, never skipped) | no bypass exists; the guard stays on |
| 6 | H3 output `h_rule.json` | **`exp_p2/gate/h3_gonogo.py`** writes `runs/P2-GATE-H3/family.json` in the schema `run_gate_m4` and `analysis_m4` read (A5.5a) | coordinator; implemented chain |
| 7 | all three corruptions run in H4 | `family` lists only the corruptions that pass H3; H4 runs only their conditions (plus patch and swap); `analysis_m4.primary` gives the others p = 1 with m = 3 | same mechanism as P (SAP 2.4) |
| 8 | analysis: separate `analysis_h.py` or options; CIs bootstrapped within subset strata | `analysis_m4` reused unchanged (`--family-run P2-GATE-H3 --folds-path ...`), unstratified paired bootstrap with its own seeds; new `exp_p2/gate/h_strata.py` adds length strata, subsets, the stratified bootstrap as sensitivity, identity checks and the H label | reuse of audited code; strata are descriptive |
| 9 | H3 descriptive T1, T2 on d | dropped; clean accuracy and changed-code discordance kept | d headroom is known to be uninformative for Y (A2.3 audit section 4); not needed |
| 10 | time constants | unchanged; H3 start bound corrected in r0 already to Fri 12:27 IST | arithmetic |

## A5.0 Status, what was known when this was written, binding conditions

**Written after the primary result. This is the most important fact about family H.**
- P is analysed and committed (`runs/P2-GATE-M4/analysis.json`, commit `1028fb9a`): rule R2, n = 500, label **negative**. P1 JPEG b = 0, c = 1;
  P2 noise b = 0, c = 0; P3 splice b = 1, c = 3; Holm-adjusted p = 1.0 for all three; every 90 percent CI inside (-0.05, +0.05).
- PS was "not met" and the A2.3 audit found no defect. Its section 4 (post hoc, descriptive) showed that token-level corruptions changed almost no
  binary decision (none-arm flips 5 and 9 of 500), and that the planned discordance 0.05 to 0.20 (AD.4, ASSUMED) failed: realised 0.008 and 0.026.
- Read by me before r0: the P section, `outcome`, `s_m`, `c1_test`, `completeness`, and parts of `mechanism` and `calibration` of
  `analysis.json`; `family.json`; the one-line Tier-3 summary in `research/progress.md` HANDOFF 60. Not opened: S2, FOIL, suite, M5 and Tier-3
  output files (S2: row count and driver chunk lines only). For the final: the implementation diff and report (no outcome in them).
- Family H was proposed **because** P showed almost no decision headroom on random negatives (internal record only; in any paper text Must-not 1
  governs and this motive is not stated, A5.14). It is **not blind to the P outcome** in its motivation, its choice of negatives and its sample-size rule. It is blind to every H outcome: no SugarCrepe item has been scored.
- The design reuses P's corruptions, severities, threshold and arms unchanged, so no H design parameter was tuned on M4 values. The one rule shaped
  by M4 is the n-rule (A5.5), which replaces the changed-code proxy because M4 showed that proxy to be badly optimistic. Disclosed (A5.14).

**Approval (recorded).** Shlok, 2026-10-29 10:23 IST, verbatim: **"Yes, add it"** (`research/paper2/CONFIRM-EVENING-2026-10-28.md` section 14;
`research/ledgers/decisions.jsonl` D0080; commit `80b06c00`). The D-H answers are in A5.15.

**Binding conditions still open (all before the first H3 item).**
1. Red-team signature: given **with conditions C5-1 to C5-8** (`RED-TEAM-SIGNOFF-2026-10-28.md`, "A5 signature"); it binds when the conditions are
   recorded as dated rows before the first H3 item. This r1 meets C5-1 to C5-4, C5-6 and C5-7 in text; C5-5 and C5-8 are the lead's (items 5, 2).
2. The code of A5.11 (implementation draft 336b31c6 plus the deltas listed there) tested and audited PASS by the gate-auditor, the audit including a
   **byte-identical regeneration of `runs/P2-GATE-M4/analysis.json` and of every committed Tier-3, E-dec and E-pred output** from the merged code;
   merged **only after S2 (rows 8 and 9) has ended**; pinned by a dated card v4 row (A-6) that records both (C5-8; lead's precondition).
3. `folds_hardneg.json`, the derived H3 file, the plan family file and the leak-check record of A5.2 committed, with the data-steward's H-L7 sign-off.
4. This file committed by the lead before items 2 and 3 are used.
5. Shlok's own words (dated ledger rows) on D-H2 and D-H4, or a dated row that they stand as the lead's defaults under his veto; and either his words
   approving **unattended** H runs or a dated row that H3 and H4 run attended only (C5-5; lead's precondition; A5.15).
If any condition is not met by the time rule of A5.12, family H is "not run" and appears only in the deviations box.

## A5.1 What family H is, and what it is not

- **Question.** The same contrast as P (GATE-M versus no gate, image direction, binary decision Y), at the same three corruptions and severities,
  on a different population of pairs: COCO val2017 images with a SugarCrepe positive caption and its LLM-written hard negative, instead of a random
  other caption.
- **Status.** A new, separately labelled **secondary confirmatory family** with its own alpha 0.05 and its own Holm correction (m = 3). Label
  everywhere: "family H (hard negatives), added after the primary result was known".
- **It cannot rescue or reinterpret P.** AB.1 extends to H word for word, and beyond AB.1 **H does not appear at all** in the places listed in the
  single placement rule of A5.9 (title, abstract, highlights, Conclusion, the opening of 6.1 and the others listed there). P stays the preregistered
  headline and its A4.2 sentences (label NEG) are used **whatever H shows**.
- **It is not a test of "P versus H".** P and H differ in negatives, images, time of planning and sample size. No statistic contrasts them, nothing
  is pooled, and no sentence says or implies that the gate helps "on hard negatives but not on random ones" or "when the task is hard" (D18 reading 1
  also bars "when does input gating help" from those places).
- **It is not a replication of P** and not a SugarCrepe benchmark score (different protocol, stratified sample, corrupted images, likelihood decision).
- **Stop rule (C5-3).** H is the **last confirmatory family** added to Paper 2 after the P outcome. Any later post-P analysis has no alpha and no
  family: it is Tier 3 exploratory, labelled "added after the primary and family H results", and listed in the deviations box. The placement rule of
  A5.9 and D-H2 may only be **tightened** after the first H3 item, never loosened, and D-H2 cannot change once any H output exists (including
  `runs/P2-GATE-H3/family.json`).

## A5.2 Data: pool, sampling, order, exclusions, leak check

**Source.** The seven SugarCrepe data files at commit `0047054b243992f0fad63d6f64f7544862daf846`, saved in `research/paper2/data/sugarcrepe-probe/`
with `SHA256SUMS.txt` (MIT licence). The builder verifies the seven SHA-256 values (LF-normalised) before reading.

**Builder (implemented):** `python -m exp_p2.gate.build_hardneg_items` writes `runs/P2-HARDNEG-ITEMS/folds_hardneg.json` (refuses to overwrite),
run in the **main worktree** so that the M1 and M5 `items.jsonl` files are read (IMPL-J section 2).
- **Eligible rows:** image id `int(filename.split('.')[0])`; image not in `folds.json` cal, head, test, test_ext, the probe-1 and probe-2
  `selection.json` lists, or the M1 and M5 items; both captions 5 to 32 tokens (`folds.hf_token_counter`, the fold rule); positive differs from
  negative. The FOIL pool needs no extra exclusion (claim 3). Dry run (IMPL-J, scratch output): 5,343 eligible rows, equal to the feasibility note.
- **Sampling (design, fixed by the code at the audited pin):** one row per image; subsets filled scarcest first; within a subset a seeded permutation
  of images; no image in two subsets; seed `[config.SEED_GATE, 9]` (`SELECT_SEED`; streams 7 and 8 are used by `folds.py`). Quotas: **H3 = `head`, 50
  items, 7 per subset and 8 in one subset; H4 = `test`, 300 items, 43 per subset and 42 in one subset**; the subsets that get 8 and 42 are drawn by the
  seed (dry run: add_att 8, swap_att 42). Each fold is put in a seeded shuffled order, so an interrupted run leaves a prefix spread over subsets. H3
  and H4 are disjoint images.
- **Item fields:** `idx` (0-based within its fold: H3 0-49, H4 0-299; required by the splice donor rule), `gid` = 6000 + idx (H3), 7000 + idx (H4)
  (folds use 0-2499, family B 4000 and 5000 upward), `image_id`, `caption` (SugarCrepe positive), `n_tok`, `neg_caption` (its negative),
  `n_tok_neg`, `tok_diff`, `subset`, `neg_source`.
- A runtime token failure is excluded, counted and not replaced (A2.1 item 2); order kept. More than 10 percent of a fold failing = stop.

**Derived H3 file (new, CPU, A5.5a `plan`):** `runs/P2-HARDNEG-ITEMS/folds_hardneg_h3.json` = `{"cal": [], "head": [], "test": <the head list of
folds_hardneg.json, verbatim>, "test_ext": []}`, so that `run_gate_m4` (which reads `test`) processes the H3 items, and the splice donor pool is the
H3 items themselves (donor_for: other items of the same block of 300 by idx).

**Leak check H-L0 to H-L8** (CPU, logged, before any GPU use; any failure stops H; mirrors AB.6). The builder's `folds.check_folds` covers H-L1, H-L2,
H-L3 and H-L5; the remaining items are added to the builder's report or a test (A5.11): H-L0 id normalisation documented; H-L1 H3 and H4 disjoint;
H-L2 disjoint from cal, head, test, test_ext; H-L3 disjoint from probe-1, probe-2, M1, M5 ids; H-L4 disjoint from the FOIL pool (assertion; 0 expected);
H-L5 no image repeated; **H-L6 positive control**: the count of SugarCrepe image ids (whole release) that match any excluded set must be > 0 (the
dry run counts 2,156 rows in an existing pool); **H-L7** five matched ids (first of cal, head, test, test_ext, probe) printed with the SugarCrepe
filename and the COCO file name, checked by the data-steward, not the script author; **H-L8** a test in which a synthetic pool sharing one id with cal
makes the builder fail.

**Committed before H3:** `folds_hardneg.json` (record the committed LF blob hash, as for `folds.json`), `folds_hardneg_h3.json`,
`runs/P2-GATE-H3-PLAN/family.json` (A5.5a), and the leak-check record.

## A5.3 Corruptions, gate, calibration (reused; assumptions)

- **Corruptions and severities:** the `runs/P2-GATE-M3/family.json` operating points unchanged: JPEG quality 10, Gaussian noise sigma 0.1, splice 128
  px. No ladder, no new severity. Corruption seeds from the item's gid (`rung_rng(gid, corr, rung)`, `run_gate_m4.py:116`), so they do not depend on
  which other corruptions are run. Splice donors from the same fold's images.
- **Gate:** statistic q (u = -(B - D)), K = 8, caption masked, mask seed 20261029 with the item's gid, jitter rule unchanged. Threshold:
  `runs/P2-GATE-M2/threshold.json` at alpha 0.05 (tau = -0.0985 per the A2.3 audit), **reused, not refitted**; alpha 0.01 and 0.10 stored as
  sensitivity.
- **Why reuse is defensible.** B is computed with the caption masked and D depends on the caption only through the true caption's length
  (`pipeline.gate_scores` passes `len(cap_tok)`), so an item's flags are the same whichever negative is used. The negative enters only through
  Lambda^{c-}.
- **Assumption (a limit): exchangeability.** The CRC statement "the expected flagged share of a clean pair's tokens is at most alpha" holds for H
  images only if a clean H pair is exchangeable with the 300 calibration pairs. SugarCrepe images are not a random draw from val2017.
- **Check (H-CAL, a gate on wording, no alpha):** the `calibration` section of `analysis_m4` on the clean H4 items (SAP 6 items 1 to 4; Z_cal, critical
  value 2.13). If Z_cal > 2.13 at any alpha, the paper does not make the CRC statement for H images and prints the realised clean flagged share beside
  every H result; **no threshold, K, alpha or item is changed**.

## A5.4 Endpoint, estimand, hypotheses, test

- **Endpoint:** Y = 1[mean over R of Delta_j > 0], Delta_j = Lambda^{c+}_j[v_j] - Lambda^{c-}_j[v_j], c- the SugarCrepe negative. Ties and empty R
  count as wrong. Arms: none (all 1,024 image tokens of the corrupted image) and GATE-M (unflagged tokens, alpha 0.05; arm key `gate0.05`).
- **Estimand:** for corruption c, Delta^H_c = Pr(Y^GM = 1) - Pr(Y^none = 1) over SugarCrepe pairs on COCO val2017 images outside every project fold,
  **weighted about equally over the seven subsets** (the design's quotas, not SugarCrepe's own subset proportions), one model (UniDisc 1.4B), one
  corruption realisation per image, one mask seed.
- **Hypotheses (family H, m = 3 always):** HJ (JPEG q10), HN (noise 0.1), HS (splice 128) = the P1, P2, P3 slots of `analysis_m4.primary`. H0 marginal
  homogeneity; two-sided; a gain needs b > c.
- **Test:** exact two-sided McNemar (SAP 2.3). **Holm over m = 3 at FWER 0.05**; a corruption that fails the H3 rule is not run in H4, gets p = 1 and
  stays in the family (`analysis_m4.primary`, lines 84-104). Under stratum heterogeneity the unstratified exact test is conservative (stated).
- **Reported with every test** (as SAP 2.3, computed by `analysis_m4`): b, c, n_d, n, accuracy of both arms, net difference with paired percentile
  bootstrap CIs at 90, 95 and 98.33 percent (10,000 resamples, unstratified, `analysis_m4`'s seeds), Clopper-Pearson CI of b/n_d, mid-p. The
  within-subset (stratified) bootstrap CI is a sensitivity in `h_strata.json`.
- **No endpoint switch.** No analogue of R3: a switch to d is excluded (gating raises d by trimming whatever the corruption status). If Y has no
  headroom, H stops at H3.

## A5.5 H3: headroom stage and the n-rule (design; fixed now; read once)

**Why not the M3 rule.** M3 sized P from the changed-code gate's discordance with kappa = 0.5 (SAP 4.6). On the P test fold that proxy predicted 47.5
discordant items in 500, and GATE-M realised 1, 0 and 4. For H the rule uses the realised gate on separate items. This is allowed because no
operating point is chosen on H3 (they are inherited) and the H4 items are disjoint, so the H4 tests stay valid conditional on the decision. The
departure from SAP 5 ("no gate flags on headroom items") is deliberate and disclosed; SAP 5's reason (blind choice of operating points) does not arise.
`headroom.py` is not used (its MIN_NV = 90 cannot be met by 50 items, and it reads M3-stage rows without gate fields).

**Data:** the 50 H3 items, processed by the **M4 stage** (`run_gate_m4`, all arms and conditions, run id `P2-GATE-H3`). Arms read: clean/none,
c/none, c/gate0.05, c/chg. **Validity per corruption:** n_valid_c = items with all of Y(clean, none), Y(c, none), Y(c, gate0.05) defined; n_valid_c
>= 45, else c is not tested.

**Per corruption c (H3 only):**
- F-_c = items with Y(clean, none) = 1 and Y(c, none) = 0; F+_c the reverse. None arm only.
- G_c = number of items with Y(c, gate0.05) != Y(c, none) (**unsigned**). The module never computes or writes b, c of GATE-M versus none
  separately, the GATE-M accuracy, or any signed GATE-M quantity.
- Descriptive only: clean none-arm accuracy with Wilson CI; the changed-code-gate discordance with none (unsigned).

**Rule.**
- **(a) Decision headroom (restore-clean power at n = 300):** F-_c > F+_c **and** the exact two-sided McNemar p of (b = 6 F-_c, c = 6 F+_c) is at most
  0.05/3. A gate that returned every item to its clean decision could then reject at n = 300 at the Holm first step (the A2.3 audit's bound, scaled
  from 50 to 300). Examples (derived): (2, 0) passes (p 0.0005); (3, 1) fails (p 0.023); (4, 1) passes (p 0.0014).
- **(b) Gate discordance:** G_c >= 3. Reason (derived): 3 of 50 projects to 18 discordant items at n = 300, the smallest count at which a large effect
  (theta 0.90 needs 17) reaches power 0.8 at the Holm first step.
- **c is tested in H4 iff n_valid_c >= 45 and (a) and (b).** H+ = that set; G* = max of G_c over H+.
  - **H-R1** (code `R1`): G* >= 8 (projects to >= 48 >= 43, powered for theta 0.75); n by the time rule.
  - **H-R2** (code `R2`): 3 <= G* <= 7 (projects to 18 to 42; powered only for theta of about 0.8 to 0.9); n by the time rule.
  - **H-NOGO** (code `NO-GO`): H+ empty. H4 is not run; HJ, HN, HS get p = 1; label H-NOGO (A5.9).
- **n_H4 (time rule, A5.12):** 300, else 200, else 0 (cut by time). R1 and R2 change only the printed power statement, not the test.

**Operating characteristics (derived, Appendix H).** For one corruption with true discordance pi_d, P(G >= 3 of 50) is 0.008 at pi_d 0.008 (about the
realised P rate), 0.32 at 0.04, 0.58 at 0.06, 0.89 at 0.10, 0.99 at 0.15. If hard negatives change nothing, H stops at H3 almost surely.

**HYP (E0), so that a GO is not misread.** M1 measured the gate's score near chance on JPEG and noise (mean per-item AUROC 0.561 and 0.503, A4.2.4
bullet 4). On hard negatives item margins are expected to be smaller, so removing about 5 percent of tokens at random may flip decisions in both
directions. A GO says that the gate changes decisions, not that it changes them for the better; theta is the open question, and H-M (A5.7) separates
detection from removal of an equally shaped random set.

### A5.5a The H3 go/no-go module (exact specification; CPU only; the lead's engineer implements, the gate-auditor audits)

**`exp_p2/gate/h3_gonogo.py`**, two subcommands, stdlib + numpy; imports `exp_p2.gate.analysis_m4.load_items` and `_arm`, `exp_p2.gate.stats.mcnemar_exact`
(or the same exact formula), `exp_p2.gate.config.REALISTIC`; no model, no GPU, no random numbers.

**1. `python -m exp_p2.gate.h3_gonogo plan`** (before H3; committed):
- reads `runs/P2-GATE-M3/family.json` and `runs/P2-HARDNEG-ITEMS/folds_hardneg.json`;
- writes `runs/P2-HARDNEG-ITEMS/folds_hardneg_h3.json` (A5.2) and **`runs/P2-GATE-H3-PLAN/family.json`** =
  `{"endpoint": "d", "endpoint_note": <M3's>, "family": <M3's three entries, fields corruption, severity, key only>, "excluded": [],
  "n_rule": {"rule": "H3-pilot", "test_fold": 50, "primary_endpoint": "Y"}, "go": true, "spec": "SAP addendum A5, A5.5a", "source": {"m3_family_sha256": ...,
  "folds_hardneg_sha256": ...}}`;
- refuses to overwrite either file; prints the H3 start deadline of A5.12 (Fri 30 Oct 12:27 IST).

**2. `python -m exp_p2.gate.h3_gonogo decide --h3-run P2-GATE-H3 [--now ISO8601]`** (once). **Deadline (C5-7):** it is the first CPU step after the H3
driver reports completion, run within A_H3 = 0.5 h of the last H3 row's timestamp; if H3 has not completed by **Fri 30 Oct 13:12 IST** (the rule-1 start
bound 12:27 plus W_H3), it is run then on the completed prefix (the n_valid >= 45 condition applies). `--now` only for tests; otherwise the system clock
in IST, recorded with the last H3 row's time and the gap (a gap above 0.5 h is logged with its reason). The clock can only lower n, never by outcome.
- loads H3 rows with `load_items` (first complete row per idx); asserts every row's gid is in 6000-6049 and its image id is in the `head` list of
  `folds_hardneg.json`;
- per c in REALISTIC (key from the plan file): `yc = _arm(rows, "clean", "none", "y")`, `yn = _arm(rows, key, "none", "y")`, `yg = _arm(rows, key, "gate0.05", "y")`;
  valid = all finite; **`disc = (yg != yn)[valid]` is formed at once and `yg` is not used again**; computes n_valid, F-, F+, bound_p =
  exact McNemar p of (6 F-, 6 F+), headroom = (F- > F+ and bound_p <= 0.05/3), G = disc.sum(), tested = (n_valid >= 45 and headroom and G >= 3), reason text;
- H+, G*, rule code (`R1` if G* >= 8, `R2` if 3 <= G* <= 7, `NO-GO` if H+ empty), the time rule of A5.12 with the named constants
  (W_H4_300 = 2.9, W_H4_200 = 1.8, A_H4 = 0.5, M = 2.0 h; FREEZE = 2026-10-30T18:00+05:30);
- `G_max_headroom` = the largest G_c over corruptions with n_valid_c >= 45 that pass (a) (null if none): used only by the H-NOGO sentence;
- descriptive, no rule effect (C5-7): `bound_p_at_n` = exact McNemar p of (k F-_c, k F+_c) with k = n_H4 / 50 (6 or 4), and `projection_at_n` =
  G_c x k for every corruption; the printed power statement uses these per-corruption projections at the n actually run, not G* alone. The GO rule
  itself stays at x6 (signed as written);
- writes **`runs/P2-GATE-H3/family.json`** (write-once; refuses to overwrite) with exactly:

```
{"endpoint": "d", "endpoint_note": "H endpoint is Y; 'd' only satisfies run_gate_m4/analysis_m4 (S-Z secondary)",
 "n_headroom_items": <rows>, "family": [<plan entries for c in H+, each plus G_c, F_minus, F_plus>],
 "excluded": [{"corruption": c, "reason": ...} for c not in H+],
 "n_rule": {"rule": "R1"|"R2"|"NO-GO", "h_rule": "H-R1"|"H-R2"|"H-NOGO", "test_fold": 300|200|0, "G_star": int|null, "G_max_headroom": int|null, "N_star": 43,
            "min_G": 3, "r1_G": 8, "scale_50_to_300": 6, "alpha_step1": 0.016667, "min_valid": 45, "primary_endpoint": "Y",
            "primary_endpoint_code": "Y", "negative_reading_available": <test_fold >= 240 and rule in (R1, R2)>,
            "time_rule": {"now": ..., "freeze": ..., "constants": {...}, "n_by_rule": 300|0, "n_after_time": 300|200|0,
                          "status": "ok"|"n=200 by time"|"cut by time"|"not tested (NO-GO)"}},
 "go": <H+ non-empty and test_fold > 0>, "downstream_claim_withdrawn": <not go>,
 "per_corruption": {c: {"n_valid", "F_minus", "F_plus", "bound_b", "bound_c", "bound_p", "bound_p_at_n", "headroom", "G", "projection_at_n", "chg_discordance", "tested", "reason"}},
 "clean_none_accuracy": {"k", "n", "wilson95"},
 "inputs": {"h3_run": "P2-GATE-H3", "items_sha256", "plan_family_sha256", "folds_h3_sha256", "code_commit"},
 "spec": "SAP addendum A5, A5.5 and A5.5a"}
```

- exit 0 with the file written; exit 2 if H3 rows are missing or fewer than 45 rows are valid for every corruption (then it still writes the file with
  rule `NO-GO`, h_rule `H-NOGO`, status "not run (pilot incomplete)", test_fold 0).
- **H4 then reads it:** `run_gate_m4 --family-run P2-GATE-H3` takes the corruption family from `family` and refuses unless `--n` equals `n_rule.test_fold`
  (so test_fold 0 always refuses); `analysis_m4 --family-run P2-GATE-H3` takes `rule` (R1/R2), `test_fold` and `family`; N_MIN = 240 makes H-NEG
  unavailable at n = 200 automatically.

**Tests (CPU, `tests/exp_p2/test_gate_h3_gonogo.py`):** synthetic rows reproduce each branch (R1, R2, NO-GO, pilot incomplete, time cut, n = 200);
the bound examples (2,0), (3,1), (4,1); the output JSON contains no key `b`, `c`, `acc_gate`, `gate_accuracy` or any signed gate value; the output is
identical for two inputs with equal none arms and equal `yg != yn` indicators but different `yg` values elsewhere (non-valid items); **captured stdout,
stderr and any log the module writes contain no signed gate quantity (no b, c, accuracy or count by direction), and the gate-auditor reads the code for
any print or log of a `yg`-derived value other than the unsigned count (C5-6)**; write-once
refusal for both files; `run_gate_m4.check_n_against_rule` accepts the written file with the matching n and refuses n = 300 when test_fold is 200 or 0;
`analysis_m4.main`'s family-file parsing accepts the written file (rule R1/R2).

## A5.6 Power (derived; ASSUMED discordance; not a forecast)

Exact unconditional power at the Holm first step (0.05/3), n = 300 (n = 200 in brackets):

| pi_d | E[n_d] at 300 | theta 0.65 | 0.75 | 0.85 | 0.95 | MDE: theta_min, net Delta_min |
|---|---|---|---|---|---|---|
| 0.04 | 12 | 0.05 (0.03) | 0.17 (0.08) | 0.43 (0.22) | 0.80 (0.50) | 0.955, 0.036 (unreachable) |
| 0.06 | 18 | 0.08 (0.05) | 0.31 (0.17) | 0.69 (0.43) | 0.96 (0.80) | 0.885, 0.046 (0.950, 0.054) |
| 0.10 | 30 | 0.18 (0.09) | 0.59 (0.36) | 0.94 (0.75) | 1.00 (0.98) | 0.800, 0.060 (0.865, 0.073) |
| 0.15 | 45 | 0.31 (0.18) | 0.82 (0.59) | 0.99 (0.94) | 1.00 (1.00) | 0.745, 0.074 (0.800, 0.090) |
| 0.20 | 60 | 0.43 (0.26) | 0.93 (0.76) | 1.00 (0.99) | 1.00 (1.00) | 0.715, 0.086 (0.760, 0.104) |

Reading: n = 300 detects a net gain of about 0.06 if 10 percent of items are discordant and 80 percent of those favour the gate; n = 200 needs about
0.07. H-NEG needs completed n >= 240 (A2.2), so it is **not available** under the n = 200 fallback; the 90 percent half-width at n = 300 is about
0.030 at pi_d 0.10 and 0.042 at 0.20 (derived).

## A5.7 Secondary analyses inside H

| Name | What | Status |
|---|---|---|
| **H-M** mechanism | `analysis_m4`'s `s_m` on H4: exact McNemar, GATE-M versus geometry-matched random gate, seed 1 (`geo0`) | **formal, own Holm m = 3, gatekept**: tested only for corruptions rejected in H with b > c; others p = 1. Seeds 2 and 3 replications, uncombined |
| H-C clean control | `analysis_m4`'s `s_c` on clean H4 images | descriptive (p shown unadjusted, labelled exploratory); not a family |
| H-CAL | A5.3 check (`analysis_m4` `calibration`) | wording gate only |
| Clean accuracy | none-arm accuracy on clean H4 images, Wilson CI, beside M4's 0.880 (0.849 to 0.906) | descriptive; `analysis_m4`'s C1 audit trigger (probe-1 reference) does not apply to H and is not read as a trigger |
| Other `analysis_m4` sections on H4 (`ps`, `s_z`, `s_dn`, `s_d2`, `mechanism`, E-dec-like splits) | as computed | descriptive only; the `ps` "positive control" reading is not used for H (PS is not re-tested); AB.1(a) applies |
| **Length strata** (`h_strata.py`) | add_obj and add_att negatives are longer (dry run mean tok_diff 3.95 and 2.63; about 86 of 300 items); every H test repeated on LM = replace_obj, replace_att, replace_rel, swap_obj, swap_att and LA = add_obj, add_att | **primary description of every H result** (r1): n, n_d, b, c, net difference with 95 percent CI for LM and LA, printed beside every H test, rejected or not; exact p unadjusted, labelled exploratory; no test |
| Per subset (`h_strata.py`) | the same per subset (about 43 items each) | descriptive, CIs only |
| Stratified bootstrap (`h_strata.py`) | 95 and 90 percent CIs of each H net difference, items resampled within subsets | sensitivity |
| Decision headroom (`h_strata.py`) | clean versus corrupted none-arm flips on H4 and the restore-clean bound | descriptive |
| Text direction, TbV, denoise arms, d, z | as in M4 | Tier 3, exploratory |

**Length rule (binding wording; r1, C5-4).** For every corruption with an H rejection with b > c (net D_H > 0), the LM and LA counts appear in the
same sentence or table row. The gain is stated **without** a length clause only if, on the length-matched subsets, b_LM > c_LM **and** the lower 95
percent bound of the LM net difference is above -D_H (the LM data exclude an opposite effect as large as the H estimate). Otherwise the sentence adds
"the gain was not shown on the length-matched subsets (b = {b_LM}, c = {c_LM}); it may be carried by the longer negatives of add_obj and add_att",
and the label carries the suffix "(length-mismatched)". A harm rejection gets the same rule with the signs reversed. The rule reads only counts and an
interval printed for every result, so it cannot be applied selectively.

## A5.8 Missing items, peeking, seeds, identity checks

- SAP 8.1 applies: complete case per analysis, committed order, prefix on interruption, no replacement, completed n < 240 stated with the MDE at the
  achieved n, worst-case sensitivity (`analysis_m4` `completeness`). K7 analogue: more than 5 percent NaN or empty R in an arm = stop and diagnose.
- SAP 8.2 applies: `analysis_m4` and `h_strata` are not run on H4 data until H4 is complete or the freeze arrives. `h3_gonogo decide` runs once and is
  the only reader of H3 rows.
- **H3 firewall (r1, C5-6; binding).** No person opens `runs/P2-GATE-H3/items.jsonl`, its arrays, the per-chunk stdout logs, `driver.log` beyond row
  counts and chunk start/stop lines, or the driver `.out`/`.err` files, before the H4 analysis is committed; committing the directory with git without
  displaying its content is allowed. **If H4 is never analysed** (H-NOGO, cut by time, pilot incomplete), **no signed H3 number is ever reported**
  anywhere; only the go/no-go inputs written by `h3_gonogo` appear (n_valid, F-, F+, the bounds, unsigned G, `G_max_headroom`, clean none-arm accuracy,
  changed-code discordance). If H4 is analysed, signed H3 numbers may appear only in the H supplement as "pilot, descriptive", never in a test or claim.
  A breach withdraws the red-team signature.
- Seeds: `analysis_m4` uses its own seeds (as for P; different data). `h_strata` uses `numpy.random.SeedSequence(20261028, spawn_key=(33,))` (A4.1.7
  used 32); the auditor confirms that no module uses key 33 (else the next free key, recorded in the pin row). `seeds.py` is not edited.
  `h3_gonogo` draws no random numbers.
- Identity checks (`h_strata` asserts): every H4 row's idx, gid (7000-7299) and image_id equal the `test` list of `folds_hardneg.json`, and its
  caption fields where stored; caption differs from neg_caption in the items file; no image id shared with `runs/P2-GATE-M4/items.jsonl`; the
  run's `config.json` `folds_sha256` equals the committed file's hash.

## A5.9 Labels and outcome book for H (fixed now; mechanical from `runs/P2-GATE-H3/family.json`, `runs/P2-GATE-H4/analysis.json`, `h_strata.json`)

| Label | Condition |
|---|---|
| **H-POS-M** | >= 1 Holm rejection with b > c; no harm rejection; H-M rejected for every such corruption |
| **H-POS-G** | >= 1 rejection with b > c; no harm rejection; H-M not rejected for at least one such corruption (split M / G per corruption as A4.2.1) |
| **H-MIXED** | >= 1 rejection with b > c and >= 1 harm rejection (Holm p < 0.05 with c > b) |
| **H-NEG** | `analysis_m4` outcome label "negative" (no rejection; every tested corruption's 90 percent CI inside (-0.05, +0.05); completed n >= 240) |
| **H-INC** | no rejection in either direction; not H-NEG |
| **H-HARM** | >= 1 harm rejection; none with b > c |
| **H-NOGO** | H3 rule: H+ empty |
| (status) | "not run (cut by time)", "not run (pilot incomplete)": deviations box only |

`h_strata.py` computes the label from these fields (function `h_label`, unit-tested on synthetic inputs).

**Mandatory prefix for every H sentence:** "In a separately labelled family added after the primary result was known (family H: SugarCrepe hard
negatives on {n} COCO images not used elsewhere; Holm over the same three corruptions), ..."

| Label | Results sentence (after the prefix) |
|---|---|
| H-POS-M | "a gate built on the masked-likelihood score raised image-direction verification accuracy over no gate under {X} (net {D}, 95% CI {L} to {U}), beyond an equally shaped random mask. This family does not change the primary result." |
| H-POS-G | "a gate built on the masked-likelihood score raised image-direction verification accuracy over no gate under {X} (net {D}, 95% CI {L} to {U}), but not distinguishably from masking the same shape elsewhere. This family does not change the primary result." |
| H-MIXED | "verification accuracy with the gate rose under {X} ({D}, CI) and fell under {Y} ({D_Y}, CI). This family does not change the primary result." |
| H-NEG | "no improvement was detected; gains or losses larger than 0.05 are excluded under {X} (90% CI {L90} to {U90})." |
| H-INC | "no improvement was detected under {X}; the intervals ({L} to {U}) cannot exclude a gain or a loss of 0.05." |
| H-HARM | "GATE-M reduced verification accuracy under {X} (net {D}, 95% CI {L} to {U})." |
| H-NOGO | (i) if `G_max_headroom` is null: "the pre-written pilot rule found no corruption with decision headroom on 50 pilot images, so the family's test was not run." (ii) otherwise: "the pre-written pilot rule found that the gate changed at most {G_max_headroom} of 50 decisions under any corruption with decision headroom (3 were required), so the family's test was not run." |

Each sentence carries n, n_d, the LM and LA counts and, where the length rule triggers, its clause. H-POS sentences carry the H-CAL clause if
Z_cal > 2.13. **{X} is one corruption per sentence** (no pooled {X}; with two rejected corruptions, two sentences; C4r-1). Every H-POS and H-MIXED
sentence also carries the clean-image control: if the 95 percent CI of the H-C net difference (GATE-M minus none on clean H4 images) contains D_H,
it adds "a gain of similar size on clean images is not excluded, so the gain is not shown to be specific to the corruption".

**Placement (binding; the single placement rule for H; r1, C5-1; replaces the r0/final list, whose item 4 is struck).** "H content" means any H
result, label, number, status or interpretation, including H-NOGO and "not run".
1. **Never:** the title; the abstract (D-H2); the highlights; the graphical abstract; any statement of significance or impact; the **Conclusion section,
   all of it**; the opening of Discussion 6.1; the limitations and future-work paragraphs; the cover letter and any response-to-reviewers text that
   summarises the findings; the caption of any figure or table other than H's own; the README, the Zenodo record description and any repository
   text (these may document H's code, files and commands as procedure, with no H result).
2. **Only here:** the Results subsection "Family H (added after the primary result)" after the preregistered families, with its own table and figure
   (own captions, with the prefix); one Discussion paragraph after the opening of 6.1, headed with the prefix, containing no sentence about P; the
   supplement section for H; the deviations box and the family status map (status only).
3. In every allowed place: the mandatory prefix, no clause linking H and P (AB.1), Must-not 1 to 7; never on the P canvas (A4.2.5), never beside PS.
4. **Contribution list:** bullet 6 of A4.2.4 names H only by status ("run, formal", "run, descriptive", "not run") with the post hoc label, no result.
5. This rule may be tightened, never loosened, after the first H3 item (A5.1 stop rule). A5.1's AB.1 sentence and this list are one rule; where any
   other text of A5 seems to allow more, this list governs.

**Must-not (adds to A4.2.2 item 3 and novelty items 10 to 13).**
1. Any sentence that P was null because the negatives were easy, random or "lacked headroom", or that H "explains", "shows why", "reveals", "unmasks"
   or "confirms" anything about P (AB.1). The realised P discordance may be printed in the P table as a number, nothing more. **This applies in Methods
   and the deviations box too (r1, C5-2):** the motive of H is stated only as "to test the same contrast on a different population of image-caption
   pairs" (A5.14); no sentence says that the preregistered task changed few decisions as a reason for adding H.
2. "The gate helps on hard negatives but not on random negatives", "harder tasks", "when the task is hard", or any P-versus-H contrast.
3. "Compositional" understanding or reasoning of UniDisc or of the gate; "SugarCrepe score", "state of the art", or any comparison with published
   SugarCrepe numbers of other models.
4. "First" for anything about hard negatives or masked diffusion models.
5. Pooled, combined or meta-analytic statistics of P and H; the words "replication" or "generalises" for H.
6. "Robust", "improves", "repair" in any title or highlight from H.
7. H-NOGO worded as "the gate has no effect on hard negatives" (H4 was not run).

## A5.10 Contamination and benchmark caveats (printed beside H)

- U8 extends to H: SugarCrepe positives are original COCO val2017 captions of their images (feasibility note: all 7,511 match after whitespace
  normalisation) and the images are COCO val2017. Whether UniDisc saw them in training is unmeasured. A memorised positive can raise the none-arm
  level; the GATE-M-versus-none contrast is paired within the item, which limits but does not remove the effect. The negatives are new LLM text.
- SugarCrepe filtered negatives against text-only models, not against UniDisc; residual text-only cues are possible.
- Same image and positive recur across subsets; one row per image is used, so the item, not the row, is the unit.
- H images are a selected subset of val2017 (A5.3 exchangeability).

## A5.11 Code: what exists, what must change, audit and pin

**Exists (implementation draft, branch `worktree-agent-aef5385b66d6a3cbd`, commit `336b31c6`, report `IMPL-J-HARDNEG-DRAFT-2026-10-29.md`):**
`--folds-path` in `run_gate_m3`, `run_gate_m4`, `analysis_m4` (explicit file must exist, never built; hash recorded in the run config);
`--family-run` in `run_gate_m4` (corruption family, endpoint check and n check from `runs/<family_run>/family.json`; the check cannot be skipped);
`build_hardneg_items.py`; driver stages `h3`, `h4`; 36 new tests; defaults of every existing stage unchanged (IMPL-J, E4 there; not re-run by me).

**Must change before the audit (deltas to 336b31c6):**
1. `exp_p2/gate/gate_driver.py`: `STAGES["h3"] = ("exp_p2.run_gate_m4", "P2-GATE-H3", 50)` and `STAGE_ARGS["h3"] = ["--folds-path",
   "runs/P2-HARDNEG-ITEMS/folds_hardneg_h3.json", "--family-run", "P2-GATE-H3-PLAN"]` (the H3 stage runs the M4 stage on the H3 items; `run_gate_m3`
   rows have no gate fields). `STAGES["h4"]` and its args are unchanged (`--family-run P2-GATE-H3`). The `run_gate_m3` `--folds-path` option stays but is
   not used by H.
2. New `exp_p2/gate/h3_gonogo.py` and its tests (A5.5a).
3. New `exp_p2/gate/h_strata.py` and its tests (A5.7, A5.8, A5.9 `h_label`).
4. A test that `run_gate_m4` builds conditions and passes its `ps_frozen` and `--denoise-for` checks with a one- and a two-corruption family (e.g.
   splice only; JPEG and splice): `build_conditions` loops over `ctx.family` and adds a denoised copy only for family corruptions in `denoise_for`
   (`run_gate_m4.py:113-122`), so this is expected to hold (E3); the test makes it E4.
5. H-L6, H-L7 output and the H-L8 injected-leak test in the builder, if not already covered (IMPL-J lists disjointness tests but not an injected
   cal-id failure).
6. The `test_gate_runner` skip for `h3`/`h4` is updated to the new module of `h3`.

**Order (binding):** code and tests in the isolated branch -> gate-auditor delta audit PASS, **including a byte-identical regeneration of
`runs/P2-GATE-M4/analysis.json` and of every committed Tier-3, E-dec and E-pred output from the merged code** -> merge **only after S2 (rows 8 and 9)
has ended** -> card v4 row A-6 (new pin; records both; the pre-launch check reads it) (C5-8) -> builder run in the main worktree and commit of
`folds_hardneg.json` -> `h3_gonogo plan` and commit of its two files -> data-steward H-L7 sign-off -> red-team conditions C5-1 to C5-8 and the A5.0
item 5 rows recorded as dated rows -> H3. No scoring path, threshold, frozen file or `tools/gpu_guard.py` changes. A failed audit means H is
not run.

**Commands (after the pin):**
```
PY -m exp_p2.gate.build_hardneg_items                                   # CPU, main worktree; commit
PY -m exp_p2.gate.h3_gonogo plan                                        # CPU; commit both files
DRV --stage h3 --extra "<MEM>"                                          # 50 items, run_gate_m4, P2-GATE-H3
PY -m exp_p2.gate.h3_gonogo decide --h3-run P2-GATE-H3                  # CPU, once; commit runs/P2-GATE-H3/family.json at once
DRV --stage h4 --n <n_rule.test_fold> --extra "<MEM>"                   # only if test_fold > 0
PY -m exp_p2.gate.analysis_m4 --run-id P2-GATE-H4 --family-run P2-GATE-H3 --folds-path runs/P2-HARDNEG-ITEMS/folds_hardneg.json   # commit at once
PY -m exp_p2.gate.h_strata --run-id P2-GATE-H4 --folds-path runs/P2-HARDNEG-ITEMS/folds_hardneg.json                              # commit
```
(`DRV`, `PY`, `MEM` as card v4 section 3; `--tbv auto`, `--denoise-for` and `--sanity` at their defaults, i.e. as M4; the exact driver syntax for `--n`
is confirmed by the auditor.)

## A5.12 Run order, time rule, cut order (time only; AB.9 extended)

**Place.** After S2 (rows 8 and 9) has ended or been stopped by its own rules, **before the suite (row 16)**. H never interrupts S2 and never runs beside
another GPU job. Reason: H is a formal family, the suite is Tier 3 and first in the AD.8 cut order. FOIL has run (FOIL-first, HANDOFF 60); Omni rows
are not run (P+ empty, AD.7).

**Cut order (first cut first):** suite, **H4, H3**, Omni R and Omni timing (not run in any case), FOIL, S2 last.

**Time rule (named constants; freeze F = Fri 30 Oct 2026 18:00 IST, fixed; a moved freeze never enters).** From M4's 26.8 s per item including chunk
restarts (feasibility note): W_H3 = 0.75 h, A_H3 = 0.5 h, W_H4(300) = 2.9 h, W_H4(200) = 1.8 h, A_H4 = 0.5 h, margin M = 2.0 h (as A4.3.2).
1. **H3 starts** iff t_now + W_H3 + A_H3 + W_H4(200) + A_H4 + M <= F, i.e. **no later than Fri 30 Oct 12:27 IST** (5.55 h before F). Logged by the lead.
2. **n_H4**, computed by `h3_gonogo decide` before the first H4 item: 300 iff t_now + 2.9 + 0.5 + 2.0 <= F (by **Fri 12:36**); else 200 iff t_now + 1.8
   + 0.5 + 2.0 <= F (by **Fri 13:42**); else 0, "not run (cut by time)".
3. A guard stop or crash during H3 or H4 halts everything until Shlok returns (card v4 section 3). On relaunch: an H3 not yet decided re-checks rule 1
   (if it fails, `decide` is run on the H3 prefix and applies the n_valid >= 45 condition); an H4 already started continues its committed list and is cut
   at the freeze as a prefix (SAP 8.1).
4. The only outcome dependence of H is the H3 rule on H3's own unsigned counts. Nothing about H depends on P, PS, S2, B, E-dec, E-pred, Tier 3 or the
   suite, and no H value may change their order, cuts or wording. Each decision is logged with its time.

GPU: H3 and H4 run under the approved guards and the card's memory flags, the parallel sessions told before the job starts, and the pre-launch check
at the new pin; **unattended only with Shlok's words on unattended H runs, otherwise attended** (D-H3, A5.0 item 5, A5.15).

## A5.13 Multiplicity map and analysis order (adds to AD.11, AD.12)

| Family | Contrast | m | Alpha | Test | Status |
|---|---|---|---|---|---|
| H | GATE-M vs none on SugarCrepe pairs: JPEG, noise, splice | 3 | 0.05 | exact McNemar, Holm | secondary, added after the P result |
| H-M | GATE-M vs geometry-matched random gate (seed 1), for corruptions rejected in H with b > c | 3 (gatekept) | 0.05 | exact McNemar, Holm | secondary |

Test families rise from 11 to 13; if all were null and independent (they are not), the chance of at least one family-level rejection would be 0.487
(derived, 1 - 0.95^13). The paper prints the count with "no multiplicity adjustment across families (SAP 7, AD.11)" and names the family of every claim.
The other `analysis_m4` sections computed on H4 (S-Z, S-DN, S-D2, S-C, PS) are **not** families for H. **AD.12 gains step 8a:** H after B (step 7) and
before Tier 3 (step 9): `runs/P2-GATE-H3/family.json` at H3; `analysis.json` and `h_strata.json` of `P2-GATE-H4` committed at once.

## A5.14 Disclosure paragraph (Methods and deviations box; substance binding, wording editable)

"Family H was added on 29 October 2026, after the following had been computed and committed: the primary family (label negative) with its
secondary families and mechanism arms (S-M, S-Z, S-DN, S-D2, S-C), the calibration check and the clean-accuracy look; the positive-control family
PS and the pipeline audit it triggered (no defect found); the decomposition and sign-agreement analyses (E-dec, E-pred); and the exploratory
comparators (Tier 3). Of these, the analyst who designed family H read the primary family, S-M, the completeness and clean-accuracy records, parts
of the mechanism and calibration sections, the positive-control audit, and a one-line summary of the Tier-3 result; the E-dec and E-pred outputs
had been committed but were not opened by that analyst. Family H tests the same contrast on a different population of image-caption pairs
(SugarCrepe hard negatives on COCO images used nowhere else in this study). It was specified in SAP addendum A5 (draft 86064e57; final b32e72a1;
revision r1 {sha}) before any hard-negative item was scored, approved by the first author (decision D0080), signed with conditions by the red team
and implemented in audited code (pin {sha}). It reuses the primary family's corruptions, severities, threshold and arms. Its sample-size rule uses
the gate's own unsigned discordance on 50 separate pilot images, because the primary family's sample-size proxy had predicted 47.5 discordant items
in 500 against 1, 0 and 4 observed. Family H is the last confirmatory family added after the primary result; it has its own Holm correction, cannot
change the primary result, and is reported whatever its outcome, including 'not run'."

Governing rule: Must-not 1 (A5.9) applies to this paragraph; no other sentence of the paper gives a motive for H. The {sha} fields are the lead's.

## A5.15 Decisions (answered)

Source: Shlok, 2026-10-29 10:23:21 IST, "Yes, add it" (D0080, commit 80b06c00), answering a question that named the family, its place (after S2,
before the suite) and "P stays the preregistered headline". CONFIRM-EVENING section 14 records the other three as the lead's reading ("since he
gave no other instruction"). **Corrected status (r1, C5-5):**
- **D-H1 = go**: Shlok's answer.
- **D-H2 = H never in the abstract** (and the rest of A5.9's placement rule): the lead's default, standing unless Shlok vetoes it before the first H3
  item; afterwards it can only be tightened (A5.1 stop rule).
- **D-H3 = GPU under the approved guards**: unattended H runs need Shlok's own words about H before H3 runs unattended; without them H3 and H4 run
  attended only (A5.0 item 5).
- **D-H4 = patch and swap kept** in the H stages (same code path as M4; descriptive only on H): the lead's default, standing unless Shlok vetoes it
  before the first H3 item.
Dated ledger rows for D-H2 to D-H4 are the lead's (A5.0 item 5); until they exist, no document calls them Shlok's answers.

## A5.16 Assumptions and concerns (statistician)

1. H is post hoc relative to P. Its value is a separately labelled test fixed before its own data on a new population, not evidence about P.
2. Hard negatives raise the chance that removing any 5 percent of tokens flips decisions, in both directions. A GO at H3 or a large n_d at H4 is not a
   gain; theta and H-M decide. On JPEG and noise H-POS-G is a more plausible positive than H-POS-M.
3. The pilot has 50 items; the rule can stop H when pi_d is about 0.04 to 0.06 although n = 300 would have had some power for large theta. Accepted for time.
4. Exchangeability of H images with the calibration fold is an assumption; H-CAL can show a violation, not prove exchangeability.
5. The estimand weights subsets about equally; it is neither SugarCrepe's natural mixture nor COCO's.
6. The H3 stage reads signed GATE-M decisions into its run directory; only the module's unsigned output is used. Keeping H3 rows closed until the H4
   analysis is committed is an honour rule (as the M1 firewall was); its scope, and the rule that signed H3 numbers are never reported when H4 is not
   analysed, are fixed in A5.8 (C5-6).
9. By the addendum's own figures H-NOGO and H-INC are the likely outcomes (P(GO) 0.32 at pi_d 0.04, power 0.31 at pi_d 0.06, theta 0.75), and the
   paper then carries 13 unadjusted test families (red team F8). The cheapest readings of a positive (trimming of thin-margin items, a memorised
   positive) are addressed only partly: H-M by shape, the clean-control clause of A5.9 by the clean images, U8 not at all.
7. All GPU-hour figures are estimates from M4; the time rule uses named constants so that no one improvises.
8. A p-value says nothing about novelty or practical importance; H does not change the novelty verdict (0.50, incremental).

## A5.17 Amendment log rows (for the lead)

| Date | Change | Reason | Before/after outcome data? |
|---|---|---|---|
| 2026-10-29 | Addendum A5 draft r0 (86064e57) | after P's NEGATIVE result and the A2.3 audit of PS | after P, PS, S-M, E-dec, E-pred, Tier-3 outcomes; before any H item |
| 2026-10-29 | Addendum A5 final: approval D0080 recorded (D-H1 go, D-H2 never in abstract, D-H3 approved guards, D-H4 keep patch/swap); reconciled with implementation 336b31c6 (builder, `--folds-path`, `--family-run`); H3 runs the M4 stage via `h3_gonogo plan` files; H3 go/no-go module `h3_gonogo decide` writes `runs/P2-GATE-H3/family.json` (R1/R2/NO-GO, test_fold 300/200/0); `family` lists tested corruptions only; analysis by `analysis_m4` plus `h_strata`; changes table r0 -> final | Shlok's approval; coordinator's reconciliation brief | **after** P, PS, S-M, E-dec, E-pred and Tier-3 outcomes; **before** any H item; no H data exists |
| 2026-10-29 | A5 revision r1: single placement rule (C5-1); full disclosure list, motive clause removed, Must-not 1 in Methods (C5-2); stop rule, placement and D-H2 only tightened (C5-3); LM/LA counts as primary description and a length rule that can fire (C5-4); D-H2 to D-H4 restated, unattended H runs need Shlok's words, time of writing corrected (C5-5); H3 firewall and no signed H3 numbers without an H4 analysis (C5-6); `decide` deadline, `G_max_headroom`, x4 bound recorded (C5-7); merge after S2 with byte-identical regeneration (C5-8) | red-team A5 signature (WITH CONDITIONS) | before any H item; no H data exists |

---

## Appendix H. Power and rule arithmetic (CPU, stdlib only)

Unchanged from r0. Script `a5_power.py` (SHA-256 `a3d36ce7cb44d8fd22b32ec2075a388078f28d624a6ffc8496594a964703de81`), output `a5_power_output.txt`
(SHA-256 `102141db6637ebad0e57c02cc861b430ff549545b5edf60596504db6dba794b4`); committed by the lead with r0 as
`runs/P2-GATE-A5/a5_power.py` and `runs/P2-GATE-A5/a5_power_output.txt` (86064e57); the auditor checks both hashes (LF convention). Method: exact
two-sided McNemar conditional on n_d; n_d ~ Bin(n, pi_d), b | n_d ~ Bin(n_d, theta); rejection counted in the favourable direction at alpha' = 0.05/3;
MDE on a 0.005 grid of theta.

```
required n_d (power 0.8, Holm step 1): theta 0.65 122 | 0.70 72 | 0.75 43 | 0.80 30 | 0.85 23 | 0.90 17 | 0.95 11
smallest b with c = 0 that rejects at Holm step 1: n_d 7 -> 7; n_d 8 -> 8
MDE n 300: pi_d 0.04 theta 0.955 Delta 0.036 | 0.06 0.885 0.046 | 0.10 0.800 0.060 | 0.15 0.745 0.074 | 0.20 0.715 0.086 | 0.30 0.675 0.105
MDE n 200: pi_d 0.04 unreachable | 0.06 0.950 0.054 | 0.10 0.865 0.073 | 0.15 0.800 0.090 | 0.20 0.760 0.104 | 0.30 0.715 0.129
P(G >= 3 of 50): pi_d 0.002 0.000 | 0.008 0.008 | 0.02 0.078 | 0.04 0.323 | 0.06 0.584 | 0.10 0.888 | 0.15 0.986 | 0.20 0.999
P(G >= 8 of 50): pi_d 0.06 0.009 | 0.10 0.122 | 0.15 0.481 | 0.20 0.810
P(F- >= 2 of 50): q 0.01 0.089 | 0.02 0.264 | 0.04 0.600 | 0.08 0.917
restoration bound at n = 300: (12, 0) p 0.00049; (6, 0) p 0.0312
90% half-width 1.645 sqrt(pi_d/n): n 300: 0.021, 0.030, 0.042, 0.052 at pi_d 0.05, 0.10, 0.20, 0.30
1 - 0.95^11 = 0.431; 1 - 0.95^13 = 0.487
```
Bound examples checked with the same exact formula on 2026-10-29: (18, 6) p 0.0227; (24, 6) p 0.00143; (12, 0) p 0.00049.
