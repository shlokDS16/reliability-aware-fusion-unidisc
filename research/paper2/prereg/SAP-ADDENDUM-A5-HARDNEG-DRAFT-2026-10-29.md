```yaml
agent: statistician
date: 2026-10-29
brief: >
  DRAFT SAP addendum A5 for Paper 2 (GATE on UniDisc 1.4B): a new confirmatory family H on SugarCrepe hard negatives,
  added after the primary family P was analysed (label NEGATIVE). Pending Shlok's go/no-go; not binding; not committed.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/data/HARDNEG-FEASIBILITY-2026-10-29.md (full)
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (sections 1-11; Addendum 1 A1.1-A1.3; Addendum 2 A2.1-A2.5; AD.0-AD.15; AB.1-AB.10)
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md (header, r1-r3 table and notes, A4.0, A4.2.1-A4.2.6, A4.3.2, A4.4-A4.6)
  - research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md (sections 1-3, 7-9)
  - research/paper2/prereg/A2.3-AUDIT-PS-2026-10-29.md (full)
  - research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md (sections 0-5)
  - runs/P2-GATE-M4/analysis.json (primary, outcome, s_m, c1_test, completeness, parts of mechanism and calibration)
  - runs/P2-GATE-M3/family.json (n_rule only)
  - code read, no edit: exp_p2/run_gate_m4.py 55-110 and 180-230; exp_p2/run_gate_m3.py 42-55 (donor_for); exp_p2/gate/folds.py 84-160;
    exp_p2/gate/pipeline.py 25-50; exp_p2/gate/config.py 10-30; exp_p2/gate/foil.py 43-48; exp_p2/gate/analysis_m4.py (grep: main, folds_path)
  - runs/P2-GATE-S2/items.jsonl and driver.log (row count and chunk lines only, for the time rule; no S2 value read)
coverage: >
  Not read: any S2, FOIL, suite, M5-coherence or Tier-3 output file; E-dec/E-pred outputs; SAP Addenda A3, A3b in full (only as cited by A4 and
  the card); the SugarCrepe paper itself (facts here are the data-steward's, E2/E4 in the feasibility note). No SugarCrepe item has been scored
  by UniDisc. No GPU used. Power arithmetic: scratchpad script, reproduced in Appendix H.
claims:
  - statement: "The M3 sample-size proxy (changed-code discordance times kappa 0.5) overstated the realised GATE-M discordance on the P test fold by roughly an order of magnitude or more (predicted 47.5 discordant items in 500; realised 1, 0 and 4)."
    status: supported
    evidence: "runs/P2-GATE-M3/family.json n_rule (D_star 19, expected_discordant_500 47.5); runs/P2-GATE-M4/analysis.json primary.per_corruption n_d"
    level: E4
    confidence: 0.95
  - statement: "Exact conditional power 0.8 at the Holm first step (0.05/3) needs 43, 30, 17 discordant items for theta 0.75, 0.80, 0.90 (equal to SAP Table 4.2)."
    status: supported
    evidence: "Appendix H script and output (derived)"
    level: E4
    confidence: 0.95
  - statement: "The pinned M4 runner can run family H with two scoped flags and correct per-file item indices; its splice donor rule indexes items by idx in blocks of 300."
    status: supported
    evidence: "exp_p2/run_gate_m4.py:61-70, 92-102, 188-218; exp_p2/run_gate_m3.py:42-48"
    level: E3
    confidence: 0.85
competing_explanations: []
unknowns:
  - every H outcome (none exists); UniDisc's clean accuracy on SugarCrepe pairs; whether the gate flips any decision on hard negatives
  - whether UniDisc's training data contain COCO val2017 captions or images (U8)
  - Shlok's go/no-go and the decisions of A5.15
next_test: {hypothesis: "HJ/HN/HS of A5.4", intervention: "H3 pilot (50 items) then H4 (300 items) on the pinned M4 stage", primary_metric: "paired accuracy difference GATE-M minus none, exact McNemar, Holm m = 3", falsifier: "H-NOGO at H3, or no Holm rejection with b > c at H4", gpu_hours: "about 3.5 wall-h (H3 0.75, H4 2.9 at n = 300), estimate"}
```

# SAP Addendum A5 (DRAFT, 2026-10-29): family H, hard negatives (SugarCrepe) on new COCO images

> **DRAFT. Pending Shlok's go/no-go. Not approved, not signed, not committed, not binding.** Nothing below may be acted on (no code
> change, no item file, no GPU stage) until Shlok's own dated sentence approves it and the conditions of A5.0 are met. If Shlok says no,
> this file stays as a record of a proposal that was not adopted and family H does not exist.

Author: statistician. Written 2026-10-29 from about 10:10 IST. A separate file beside the SAP. **Precedence if adopted:** A5 > A4 > A3b >
A3 > A2b > A2 > A1 > SAP body, **only on the points listed here**. Family P, PS, S-M, S-Z, S-DN, S-D, S-D2, S-C, S2, B, R, E-dec, E-pred, the
suite, the outcome book of A4.2 and every earlier rule stand unchanged.

## A5.0 Status, what was known when this was written, binding conditions

**Written after the primary result. This is the most important fact about family H.**
- P is analysed and committed (`runs/P2-GATE-M4/analysis.json`, commit `1028fb9a`): rule R2, n = 500, label **negative**. P1 JPEG b = 0,
  c = 1; P2 noise b = 0, c = 0; P3 splice b = 1, c = 3; Holm-adjusted p = 1.0 for all three; every 90 percent CI inside (-0.05, +0.05).
- PS was "not met" and the A2.3 audit found no defect (`A2.3-AUDIT-PS-2026-10-29.md`). Its section 4 (post hoc, descriptive) showed that
  token-level corruptions changed almost no binary decision (none-arm flips 5 and 9 of 500), and that the planned discordance 0.05 to 0.20
  (AD.4, ASSUMED) failed: realised GATE-M-vs-none discordance 0.008 and 0.026.
- Read by me before writing (beyond the files above): the P section, `outcome`, `s_m`, `c1_test`, `completeness`, and parts of
  `mechanism` and `calibration` of `analysis.json`; `family.json` `n_rule`; the one-line Tier-3 summary in `research/progress.md`
  HANDOFF 60. Not opened: S2, FOIL, suite, M5 and Tier-3 output files (S2: row count 37 and driver chunk lines only, at 10:07 IST).
- Family H was proposed **because** P showed almost no decision headroom on random negatives. It is therefore **not blind to the P outcome**
  in its motivation, its choice of negatives and its sample-size rule. It is blind to every H outcome: no SugarCrepe item has been scored.
- The design reuses P's corruptions, severities, threshold and arms unchanged, so no H design parameter was tuned on M4 values. The one rule
  that was shaped by M4 is the n-rule (A5.5), which replaces the changed-code proxy because M4 showed that proxy to be badly optimistic. That
  is disclosed (A5.14).

**Binding conditions (all before the first H3 item; none is met now).**
1. Shlok's dated sentence approving family H (A5.15 D-H1), plus his choices on D-H2 to D-H4 or the defaults stated there.
2. Red-team signature on this addendum (proposer is not validator). Any change after the signature is a dated row, before any H item.
3. The code delta of A5.11 written, tested, audited PASS by the gate-auditor, merged, and pinned by a dated card v4 row (A-6).
4. The item files, manifest and leak check of A5.2 committed, with the data-steward's L7 sign-off.
5. This file committed (with "DRAFT" removed and the approval row added) before items 1 to 4 are used.
If any condition is not met by the time rule of A5.12, family H is "not run" and appears only in the deviations box.

## A5.1 What family H is, and what it is not

- **Question.** The same contrast as P (GATE-M versus no gate, image direction, binary decision Y), at the same three corruptions and
  severities, on a different population of pairs: COCO val2017 images with a SugarCrepe positive caption and its LLM-written hard negative,
  instead of a random other caption.
- **Status.** A new, separately labelled **secondary confirmatory family** with its own alpha 0.05 and its own Holm correction (m = 3). Label
  everywhere: "family H (hard negatives), added after the primary result was known".
- **It cannot rescue or reinterpret P.** AB.1 extends to H word for word: under the P null, no clause drawn from H appears in the title,
  abstract, highlights, conclusion or the opening of Discussion 6.1 to explain, qualify or predict the P result. P stays the preregistered
  headline and its A4.2 sentences (label NEG) are used **whatever H shows**.
- **It is not a test of "P versus H".** P and H differ in negatives, in images, in the time of planning and in sample size. No statistic
  contrasts them, nothing is pooled, and no sentence says or implies that the gate helps "on hard negatives but not on random ones" or "when
  the task is hard" (D18 reading 1 also bars "when does input gating help" from those places).
- **It is not a replication of P** (different negatives) and not a SugarCrepe benchmark score (different protocol, stratified sample,
  corrupted images, likelihood decision).

## A5.2 Data: pool, sampling, order, exclusions, leak check

**Source.** The seven SugarCrepe data files at commit `0047054b243992f0fad63d6f64f7544862daf846`, as saved in
`research/paper2/data/sugarcrepe-probe/` with `SHA256SUMS.txt` (data-steward; MIT licence). The builder asserts the seven SHA-256 values
before reading.

**Eligible rows.** A row (image, positive, negative) is eligible iff (i) its image id, `int(filename.split('.')[0])`, is a COCO val2017 id present
in the local `val2017.zip`; (ii) the image is **not** in any of: `folds.json` cal, head, test, test_ext; the probe-1 and probe-2 id lists; the
M1 and M5 items; the FOIL pool (`runs/P2-GATE-FOIL/pool.json`, fit and test, all image ids; added to the feasibility note's list so that H and
B share no image); (iii) both captions have 5 to 32 tokens under the runtime tokenizer (fold rule, `config.TOK_RANGE`). The feasibility note
counts 5,343 rows on 1,132 images before the FOIL exclusion (E4 there; recomputed by the builder, which logs counts by reason).

**One row per image, stratified, fixed seed (design, fixed now).** Seed `numpy.random.default_rng(numpy.random.SeedSequence(20261102))` (not used
elsewhere in `exp_p2` by grep, 2026-10-29).
1. Subsets are processed in ascending order of eligible-image count (computed by the builder; expected order from the feasibility note: swap_obj,
   add_att, replace_att, swap_att, replace_rel, replace_obj, add_obj). For each subset, permute its eligible images not yet taken (sorted by id,
   then permuted with the generator) and take the first **50**. Within a taken image the row is the **first eligible row of that subset in file
   order** (record order, not content; as AD.6 did for FOIL). Total 7 x 50 = 350 distinct images. If a subset has fewer than 50 untaken
   eligible images, it takes all it has and the shortfall is logged; no other subset fills it.
2. **Ordered list** of 350 by round-robin over the subsets in alphabetical order (add_att, add_obj, replace_att, replace_obj, replace_rel,
   swap_att, swap_obj), each turn taking the next item of that subset in its permuted order. Every prefix is therefore close to balanced.
3. **H3 (pilot) = positions 1 to 50; H4 (test) = positions 51 to 350** (300). Disjoint images by construction. A time-rule fallback to n = 200
   (A5.12) uses the first 200 of the H4 list; that cannot select items.
4. Item fields: `idx` = position **within its own file** (H3: 0 to 49; H4: 0 to 299; required by the splice donor rule, A5.11 item 4), `gid` =
   3000 + position in the 350 list (0 to 349; free range: folds use 0 to 2499, FOIL 4000 and 5000 upward), `image_id`, `caption` (SugarCrepe
   positive), `neg_caption` (its negative), `subset`, `sc_key` (row key in the file), `len_pos`, `len_neg` (runtime tokens).
5. A runtime token failure is excluded, counted and not replaced (A2.1 item 2); order kept. More than 10 percent of a file failing = stop.

**Leak check H-L0 to H-L8** (CPU, logged, before any GPU use; any failure stops H; mirrors AB.6):
H-L0 id normalisation documented (filename to integer); H-L1 H3 and H4 disjoint; H-L2 H ids disjoint from cal, head, test, test_ext; H-L3
disjoint from probe-1, probe-2, M1, M5 ids; H-L4 disjoint from the FOIL pool; H-L5 no image repeated; **H-L6 positive control**: the count of
SugarCrepe image ids (whole release) matching any excluded set must be > 0 (the feasibility note found 95 in cal and 83 in test); **H-L7** five
matched ids (first of cal, head, test, test_ext, probe) printed with the SugarCrepe filename and the COCO file name, checked by the data-steward,
not the script author; **H-L8** the checker fails on a synthetic pool sharing one id with cal (self-test). Counts by subset and by exclusion
reason are written to the log.

**Committed before H3:** `runs/P2-GATE-H/items_h3.json`, `items_h4.json` (folds format: key `test` holds the items; `cal`, `head`, `test_ext`
empty), `manifest.json` (source hashes, seed, eligibility counts, per-subset counts, SHA-256 of both item files), `leak_check.json` (ok true),
`h3_plan.json` (`{"rule": "H3-pilot", "test_fold": 50}`).

## A5.3 Corruptions, gate, calibration (reused; assumptions)

- **Corruptions and severities:** the `family.json` operating points unchanged: JPEG quality 10, Gaussian noise sigma 0.1, splice 128 px. No
  ladder, no new severity. Corruption seeds from the item's gid (SAP 8.3). Splice donors come from the same file's images (H3 from H3, H4
  from H4) by the unchanged `donor_for` rule.
- **Gate:** statistic q (u = -(B - D)), K = 8, caption masked, mask seed 20261029 with the item's gid, jitter rule unchanged. Threshold:
  `runs/P2-GATE-M2/threshold.json` at alpha 0.05 (tau = -0.0985 per the A2.3 audit), **reused, not refitted**. Alpha 0.01 and 0.10 stored as
  sensitivity, as in M4.
- **Why reuse is defensible.** B is computed with the caption masked and D depends on the caption only through the length of the true caption
  (`pipeline.gate_scores` passes `len(cap_tok)`), so the flags of an item are the same whichever negative is used. The negative enters only
  through Lambda^{c-}.
- **Assumption (stated as a limit): exchangeability.** The CRC statement "the expected flagged share of a clean pair's tokens is at most alpha"
  holds for H images only if a clean H pair is exchangeable with the 300 calibration pairs. SugarCrepe images are not a random draw from
  val2017 (they are the images whose captions survived LLM generation and adversarial filtering), so this is an assumption, not a fact.
- **Check (H-CAL, descriptive gate on the wording, no alpha):** SAP 6 items 1 to 4 on the clean H4 items (realised flagged share, item-clustered
  bootstrap CI, Z_cal with n_cal = 300 and n_test = completed H4 n, critical value 2.13). If Z_cal > 2.13 at any alpha, the paper does not make
  the CRC statement for H images and prints the realised clean flagged share beside every H result; **no threshold, K, alpha or item is changed**.

## A5.4 Endpoint, estimand, hypotheses, test

- **Endpoint:** Y = 1[mean over R of Delta_j > 0], Delta_j = Lambda^{c+}_j[v_j] - Lambda^{c-}_j[v_j], with c- the SugarCrepe negative. Ties and
  empty R count as wrong (SAP 2.1). Arms: none (R = all 1,024 image tokens of the corrupted image) and GATE-M (R = unflagged tokens, alpha 0.05).
- **Estimand:** for corruption c, Delta^H_c = Pr(Y^GM = 1) - Pr(Y^none = 1) over the population of SugarCrepe pairs on COCO val2017 images
  outside every project fold, **weighted equally over the seven subsets** (the design's 1/7 each, not SugarCrepe's own subset proportions), one
  model (UniDisc 1.4B), one corruption realisation per image, one mask seed.
- **Hypotheses (family H, m = 3 always):** HJ (JPEG q10), HN (noise 0.1), HS (splice 128): H0 marginal homogeneity of Y^GM and Y^none; two-sided.
  Direction that supports a gain: b > c.
- **Test:** exact two-sided McNemar on the discordant items (SAP 2.3 formula). **Holm over m = 3 at FWER 0.05**; a corruption not tested
  under A5.5 gets p = 1 and stays in the family. Under stratum heterogeneity the unstratified exact test is conservative (stated, not corrected).
- **Reported with every test** (as SAP 2.3): b, c, n_d, n, accuracy of both arms, net difference (b - c)/n with paired percentile bootstrap CIs at
  90, 95 and 98.33 percent (10,000 resamples, items resampled **within subset strata**), Clopper-Pearson CI of b/n_d, mid-p as sensitivity.
- **No endpoint switch.** There is no analogue of R3. A switch to the evidence ratio d is excluded because gating raises d by trimming whatever
  the corruption status (A4 R3-POS caveat; A2.3 audit section 4 showed large d headroom with almost no Y headroom), so a d result would not be a
  result about hard-negative decisions. If the binary endpoint has no headroom, H stops at H3 (A5.5).

## A5.5 H3: headroom stage and the n-rule (design; fixed now; read once)

**Why not the M3 rule.** M3 sized P from the changed-code gate's discordance D* with kappa = 0.5 (SAP 4.6). On the P test fold that proxy
predicted 47.5 discordant items in 500 (`family.json` `n_rule`), and GATE-M realised 1, 0 and 4 (`analysis.json`). For H the rule is therefore
built on the realised gate on separate items, which is allowed because no operating point is chosen on H3 (they are inherited) and the H4 items
are disjoint, so the H4 tests stay valid conditional on the decision. The departure from SAP 5 ("no gate flags on headroom items") is
deliberate and disclosed; SAP 5's reason (blind choice of operating points) does not arise here.

**Data:** the 50 H3 items, M4 stage unchanged (all arms, all conditions). Valid items: all of clean-none, corrupted-none and corrupted-GATE-M Y
defined. **Validity: n_valid >= 45**, else H3 fails and H is "not run (pilot incomplete)".

**Per corruption c, from H3 only:**
- F-_c = items with Y_clean^none = 1 and Y_c^none = 0 (corruption makes a right decision wrong); F+_c the reverse. None arm only.
- G_c = number of items whose Y differs between GATE-M and none under c (**unsigned**). The H3 script outputs G_c and **never** b, c separately,
  the GATE-M accuracy, or any signed GATE-M quantity (asserted in code and in its test).
- Also printed, descriptive: clean none-arm accuracy with Wilson CI; the changed-code-gate discordance (M3's D_c, for continuity); T1, T2 on d.

**Rule.**
- **Decision headroom for c (restoration bound reachable):** F-_c > F+_c and the exact McNemar p of (6 F-_c, 6 F+_c) is at most 0.05/3. This asks
  whether a gate that returned every item to its clean decision could reject at n = 300 at the Holm first step (the A2.3 audit's bound, scaled from
  50 to 300). Examples (derived): (2, 0) passes (p 0.0005); (3, 1) fails (p 0.023); (4, 1) passes (p 0.0014).
- **Gate discordance for c:** G_c >= 3. Reason (derived): 3 of 50 projects to 18 discordant items at n = 300, the smallest count at which a large
  effect (theta 0.90 needs 17) reaches power 0.8 at the Holm first step.
- **c is tested in H4 iff both hold.** Let H+ be that set and G* = max of G_c over H+.
  - **H-R1:** G* >= 8 (projects to >= 48 >= 43, powered for theta 0.75). n_H4 = 300.
  - **H-R2:** 3 <= G* <= 7 (projects to 18 to 42; powered only for theta of about 0.8 to 0.9). n_H4 = 300.
  - **H-NOGO:** H+ empty. H4 is not run; HJ, HN, HS get p = 1, label H-NOGO (A5.9).
- n_H4 is then cut by the time rule only (A5.12: 300, else 200, else not run). R1 and R2 do not change the test, only the printed power
  statement.
- **Output:** `runs/P2-GATE-H3/h_rule.json` (write-once: n_valid, per-corruption F-, F+, G, the bound p, tested flag, H+, G*, rule, time-rule
  inputs, n_H4), **committed before the first H4 item**. The H3 script runs once.

**Operating characteristics (derived, Appendix H).** For one corruption with true discordance pi_d, P(G >= 3 of 50) is 0.008 at pi_d 0.008 (about
the realised P rate), 0.32 at 0.04, 0.58 at 0.06, 0.89 at 0.10, 0.99 at 0.15. If hard negatives change nothing, H stops at H3 almost surely.

**HYP (E0), stated so that a GO is not misread.** M1 measured the gate's score near chance on JPEG and noise (mean per-item AUROC 0.561 and 0.503,
A4.2.4 bullet 4). On hard negatives item margins are expected to be smaller, so removing about 5 percent of tokens at random may flip decisions in
both directions. A GO therefore says that the gate changes decisions, not that it changes them for the better; theta is the open question, and H-M
(A5.7) is the control that separates detection from removal of an equally shaped random set.

## A5.6 Power (derived; ASSUMED discordance; not a forecast)

Exact unconditional power at the Holm first step (0.05/3), n = 300 (n = 200 in brackets):

| pi_d | E[n_d] at 300 | theta 0.65 | 0.75 | 0.85 | 0.95 | MDE: theta_min, net Delta_min |
|---|---|---|---|---|---|---|
| 0.04 | 12 | 0.05 (0.03) | 0.17 (0.08) | 0.43 (0.22) | 0.80 (0.50) | 0.955, 0.036 (unreachable) |
| 0.06 | 18 | 0.08 (0.05) | 0.31 (0.17) | 0.69 (0.43) | 0.96 (0.80) | 0.885, 0.046 (0.950, 0.054) |
| 0.10 | 30 | 0.18 (0.09) | 0.59 (0.36) | 0.94 (0.75) | 1.00 (0.98) | 0.800, 0.060 (0.865, 0.073) |
| 0.15 | 45 | 0.31 (0.18) | 0.82 (0.59) | 0.99 (0.94) | 1.00 (1.00) | 0.745, 0.074 (0.800, 0.090) |
| 0.20 | 60 | 0.43 (0.26) | 0.93 (0.76) | 1.00 (0.99) | 1.00 (1.00) | 0.715, 0.086 (0.760, 0.104) |

Reading: n = 300 detects a net gain of about 0.06 if 10 percent of items are discordant and 80 percent of those favour the gate; n = 200 needs
about 0.07. The label H-NEG needs completed n >= 240 (A2.2), so it is **not available** under the n = 200 fallback; the 90 percent half-width at
n = 300 is about 0.030 at pi_d 0.10 and 0.042 at 0.20 (derived).

## A5.7 Secondary analyses inside H

| Name | What | Status |
|---|---|---|
| **H-M** mechanism | exact McNemar, GATE-M versus geometry-matched random gate, seed 1 (`geo0`, as S-M), per corruption | **formal, own Holm m = 3, gatekept**: tested only for corruptions rejected in H with b > c; others p = 1. Seeds 2 and 3 reported as replications, uncombined |
| H-C clean control | GATE-M versus none on clean H4 images: b, c, net difference, 95 percent CI, exact p | descriptive (p shown unadjusted, labelled exploratory) |
| H-CAL | A5.3 check | wording gate only |
| Clean accuracy | none-arm accuracy on clean H4 images, Wilson CI, beside M4's 0.880 (0.849 to 0.906) | descriptive; no trigger (no reference value exists for hard negatives) |
| **Length strata** | the add_obj and add_att negatives are longer by 4.5 and 2.5 tokens on average (feasibility note); every H test is repeated descriptively on LM = replace_obj, replace_att, replace_rel, swap_obj, swap_att (length-matched) and LA = add_obj, add_att | descriptive: b, c, net difference with 95 percent CI, exact p unadjusted, labelled exploratory |
| Per subset | the same, per subset (about 43 items each) | descriptive, CIs only |
| Decision headroom | clean versus corrupted none-arm flips, the restoration bound (A2.3 audit style) on H4 | descriptive |
| Patch and swap on H items | run because the M4 stage runs them (condition order fixed by `ps_frozen.json`) | descriptive only; **not** a positive-control family; AB.1(a) applies |
| Text direction, TbV, denoise arms, d, z | as in M4 | Tier 3, exploratory |

**Length rule (binding wording).** If any H rejection with b > c is reported and the LM estimate for that corruption has the opposite sign with a 95
percent CI excluding 0, every sentence about that rejection adds "not present on the length-matched subsets".

## A5.8 Missing items, peeking, seeds

- SAP 8.1 applies: complete case per analysis, committed order, prefix on interruption, no replacement, completed n < 240 stated with the MDE at the
  achieved n, worst-case sensitivity. K7 analogue: more than 5 percent NaN or empty R in an arm = stop and diagnose (no look at Y).
- SAP 8.2 applies: `analysis_h` is not run on H4 data until H4 is complete or the freeze arrives. The H3 script runs once, after H3.
- Analysis seed: `numpy.random.SeedSequence(20261028, spawn_key=(33,))` (A4.1.7 used key 32). The auditor confirms that no module uses key 33;
  if one does, the next free key is used and recorded in the pin row before H3. `seeds.py` is not edited.
- Runtime identity check (analysis asserts): every H4 row's (gid, image_id, caption, neg_caption) equals the item file byte for byte; caption differs
  from neg_caption; gids in 3050 to 3349; no image id shared with `runs/P2-GATE-M4/items.jsonl`.

## A5.9 Labels and outcome book for H (fixed now; mechanical from `h_rule.json` and `analysis_h.json`)

| Label | Condition |
|---|---|
| **H-POS-M** | >= 1 Holm rejection with b > c; no harm rejection; H-M rejected for every such corruption |
| **H-POS-G** | >= 1 rejection with b > c; no harm rejection; H-M not rejected for at least one such corruption (split M / G per corruption as A4.2.1) |
| **H-MIXED** | >= 1 rejection with b > c and >= 1 harm rejection (Holm p < 0.05 with c > b) |
| **H-NEG** | no rejection; for every tested corruption the 90 percent CI lies inside (-0.05, +0.05); completed n >= 240 |
| **H-INC** | no rejection in either direction; not H-NEG |
| **H-HARM** | >= 1 harm rejection; none with b > c |
| **H-NOGO** | H3 rule: H+ empty |
| (status) | "not run (cut by time)", "not run (pilot incomplete)", "not run (not approved)": deviations box only |

**Mandatory prefix for every H sentence:** "In a separately labelled family added after the primary result was known (family H: SugarCrepe hard
negatives on {n} COCO images not used elsewhere; Holm over the same three corruptions), ..."

| Label | Results sentence (after the prefix); the abstract uses the same sentence if D-H2 = (a) |
|---|---|
| H-POS-M | "a gate built on the masked-likelihood score raised image-direction verification accuracy over no gate under {X} (net {D}, 95% CI {L} to {U}), beyond an equally shaped random mask. This family does not change the primary result." |
| H-POS-G | "a gate built on the masked-likelihood score raised image-direction verification accuracy over no gate under {X} (net {D}, 95% CI {L} to {U}), but not distinguishably from masking the same shape elsewhere. This family does not change the primary result." |
| H-MIXED | "verification accuracy with the gate rose under {X} ({D}, CI) and fell under {Y} ({D_Y}, CI). This family does not change the primary result." |
| H-NEG | "no improvement was detected; gains or losses larger than 0.05 are excluded under {X} (90% CI {L90} to {U90})." |
| H-INC | "no improvement was detected under {X}; the intervals ({L} to {U}) cannot exclude a gain or a loss of 0.05." |
| H-HARM | "GATE-M reduced verification accuracy under {X} (net {D}, 95% CI {L} to {U})." |
| H-NOGO | "the pre-written pilot rule found no corruption under which the gate changed enough decisions (at most {G*} of 50) [or: no corruption with decision headroom], so the family's test was not run." |

Each sentence carries n, n_d and, where the length rule triggers, its clause. H-POS sentences carry the H-CAL clause if Z_cal > 2.13.

**Placement (binding).**
1. **Title:** no H content under any label (title follows A4.2.3 for P, i.e. QT under NEG).
2. **Highlights:** no H content under any label (A4.2.2 item 6 forbids secondary gains; excluding H everywhere avoids choosing by outcome).
3. **Abstract:** decided by Shlok before H3 (D-H2): (a) the H sentence appears, after the P sentence and before the scope sentence, **under every
   H label including H-NOGO**; or (b) never. Default if he does not choose: (b). A "not run" status never appears in the abstract.
4. **Discussion 6.1 opening and Conclusion's first sentence:** P only. H may appear later in the conclusion with its prefix.
5. **Results:** own subsection "Family H (added after the primary result)" after the preregistered families, own table and figure; never on the P
   canvas (A4.2.5), never beside PS.
6. **Contribution list:** bullet 6 of A4.2.4 names H only by status ("run, formal", "run, descriptive", "not run"), with the prefix's post hoc label.

**Must-not (adds to A4.2.2 item 3 and novelty items 10 to 13).**
1. Any sentence that P was null because the negatives were easy, random or "lacked headroom", or that H "explains", "shows why", "reveals",
   "unmasks" or "confirms" anything about P (AB.1). The realised P discordance may be printed in the P table as a number, nothing more.
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

## A5.11 Code delta (specification only; not implemented here; audited and pinned before any H item)

1. **`--folds-path PATH`** in `exp_p2/run_gate_m4.py` `main`: passed as `path=` to `folds.ensure_folds` at make_ctx (line 94) and get_items (line
   215); `ctx.fold` (line 101, the splice donor pool) built from the same file. With `--folds-path`, the file **must already exist** and its SHA-256
   must equal the value in `runs/P2-GATE-H/manifest.json`; the runner refuses otherwise (ensure_folds would otherwise build and write a new folds
   file).
2. **`--n-rule PATH`** (default `runs/P2-GATE-M3/family.json`): `check_n_against_rule` (lines 61-70) reads `n_rule.test_fold` (or top-level
   `test_fold`) from this file. **Scoped to H:** a non-default `--n-rule` or any `--folds-path` is refused unless the run id starts with
   `P2-GATE-H` and both flags are given; `test_fold` 0 (H-NOGO or cut) refuses. The default path and the P behaviour are unchanged (test).
3. `exp_p2/gate/analysis_m4.py:640` gets the same `--folds-path` and `--n-rule` for the planned items, or a separate `analysis_h.py` imports
   its test, Holm and bootstrap functions unchanged and adds: labels HJ/HN/HS, H-M gatekeeping, strata within-subset bootstrap, length and subset
   tables, H-CAL, A5.8 identity checks, A5.9 label; output `runs/P2-GATE-H4/analysis_h.json`.
4. **Item indices:** `donor_for` (`run_gate_m3.py:45-47`) takes donors from `ctx.fold` by `idx` in blocks of 300, so `idx` must run from 0 within
   each file (A5.2 item 4); a test asserts a non-empty donor pool for every H3 and H4 item and that no donor is the item itself.
5. New CPU modules: `exp_p2/gate/h_items.py` (builder, A5.2, leak check H-L0 to H-L8) and `exp_p2/gate/h_headroom.py` (A5.5; asserts no signed
   GATE-M output; takes `--time-left-h` and writes `n_H4` by A5.12).
6. Tests: builder determinism (same bytes twice), counts, disjointness, round-robin balance of every prefix, H-L8 injected leak, the scoped flag
   refusals, the unchanged P path (`--n 500` still required for P2-GATE-M4), the H3 output assertion, Holm m = 3 with p = 1 fill, label table on
   synthetic inputs.
7. **Order:** code and tests in an isolated branch -> gate-auditor delta audit PASS -> merge -> card v4 row A-6 (new pin; pre-launch check reads it)
   -> builder run and commit of A5.2 files -> data-steward H-L7 sign-off -> H3. No scoring path, threshold, frozen file or `tools/gpu_guard.py`
   changes. A failed audit means H is not run.

## A5.12 Run order, time rule, cut order (time only; AB.9 extended)

**Place.** After S2 (rows 8 and 9) has ended or been stopped by its own rules, **before the suite (row 16)**. H never interrupts S2 and never
runs beside another GPU job. Reason for before the suite: H is a formal family, the suite is Tier 3 and is first in the AD.8 cut order. FOIL has
run (FOIL-first, HANDOFF 60); Omni rows are not run (P+ empty, AD.7).

**Cut order after adoption (first cut first):** suite, **H4, H3**, Omni R and Omni timing (not run in any case), FOIL, S2 last.

**Time rule (named constants; freeze F = Fri 30 Oct 2026 18:00 IST, fixed; a moved freeze never enters).** Wall-hour estimates from M4's 26.8 s per
item including chunk restarts (feasibility note): W_H3 = 0.75 h (50 items plus on-demand null-cache lengths), A_H3 = 0.5 h (H3 script, commit),
W_H4(300) = 2.9 h (upper end of 2.0 to 2.6 plus 0.25 cache), W_H4(200) = 1.8 h, A_H4 = 0.5 h, margin M = 2.0 h (as A4.3.2).
1. **H3 starts** iff t_now + W_H3 + A_H3 + W_H4(200) + A_H4 + M <= F, i.e. **no later than Fri 30 Oct 12:27 IST** (5.55 h before F).
2. **n_H4**, decided by `h_headroom` when `h_rule.json` is written, before the first H4 item: 300 iff t_now + 2.9 + 0.5 + 2.0 <= F (by **Fri
   12:36**); else 200 iff t_now + 1.8 + 0.5 + 2.0 <= F (by **Fri 13:42**); else H4 "not run (cut by time)".
3. A guard stop or crash during H3 or H4 halts everything until Shlok returns (card v4 section 3); on relaunch the same rules are re-evaluated with
   the new t_now; an H4 already started continues its committed list and is cut at the freeze as a prefix (SAP 8.1).
4. The only outcome dependence of H is the H3 rule on H3's own unsigned counts. Nothing about H depends on P, PS, S2, B, E-dec, E-pred, Tier 3 or
   the suite, and no H value may change their order, cuts or wording. Each decision is logged with its time.

GPU preconditions as for every stage: Shlok's go-ahead for the GPU run itself, the card's memory flags and guards, the parallel sessions told
before the job starts, and the pre-launch check at the new pin.

## A5.13 Multiplicity map and analysis order (adds to AD.11, AD.12)

| Family | Contrast | m | Alpha | Test | Status |
|---|---|---|---|---|---|
| H | GATE-M vs none on SugarCrepe pairs: JPEG, noise, splice | 3 | 0.05 | exact McNemar, Holm | secondary, added after the P result |
| H-M | GATE-M vs geometry-matched random gate (seed 1), for corruptions rejected in H with b > c | 3 (gatekept) | 0.05 | exact McNemar, Holm | secondary |

Test families rise from 11 to 13; if all were null and independent (they are not), the chance of at least one family-level rejection would be
0.487 (derived, 1 - 0.95^13). The paper prints this count with "no multiplicity adjustment across families (SAP 7, AD.11)" and names the family of
every claim. **AD.12 gains step 8a:** H after B (step 7) and before Tier 3 (step 9); `h_rule.json` at H3, `analysis_h.json` committed at once.

## A5.14 Disclosure paragraph (Methods and deviations box; substance binding, wording editable)

"Family H was added on {date} after the primary family had been analysed (label negative) and after the positive-control audit had shown that
the preregistered task changed few binary decisions. It was specified in SAP addendum A5 (commit {sha}) before any hard-negative item was scored,
approved by {Shlok's row}, signed by the red team and implemented in audited code (pin {sha}). It reuses the primary family's corruptions,
severities, threshold and arms; its sample-size rule uses the gate's own discordance on 50 separate pilot images because the primary family's
proxy (changed-code discordance with kappa 0.5) had predicted 47.5 discordant items in 500 against 1, 0 and 4 observed. Family H has its own
Holm correction, cannot change the primary result, and is reported whatever its outcome, including 'not run'."

## A5.15 Decisions for Shlok (needed before anything in this file is used)

- **D-H1** Go or no-go on family H. Cost (estimates): GPU about 3.5 wall-h on Thu evening or Fri morning after S2 (H3 0.75 h, H4 2.9 h); CPU
  agent work for the code delta, builder, tests, audit and red-team signature before Fri 12:27 IST. What it can deliver: a formal test of the same
  contrast on harder pairs; most likely outcomes are H-NOGO or H-INC (A5.5, A5.6). What it cannot deliver: any change to P or to the title.
- **D-H2** Abstract rule (A5.9 item 3): (a) the H sentence under every H label, or (b) never. Default (b).
- **D-H3** GPU go-ahead for H3 and H4 under the usual guards, and whether they may run unattended (overnight) if S2 ends late.
- **D-H4** Keep patch and swap in the H stage (default, same code path as M4, about 20 percent of the GPU time) or drop them (allowed only if
  decided before H3; recorded; they are at the end of the condition list, so the other conditions' seeds do not change, E3 from the runner's
  condition order, to be confirmed by the auditor).

## A5.16 Assumptions and concerns (statistician)

1. H is post hoc relative to P. Its value is a separately labelled, preregistered-before-data test on a new population, not evidence about P.
2. Hard negatives raise the chance that removal of any 5 percent of tokens flips decisions, in both directions. A GO at H3 or a large n_d at H4 is
   not a gain; theta and H-M decide. On JPEG and noise the gate's score was near chance in M1, so H-POS-G (gain not distinguishable from a random
   same-shape mask) is a more plausible positive than H-POS-M there.
3. The pilot has 50 items; the rule's operating characteristics (A5.5) show it can stop H when pi_d is about 0.04 to 0.06 although n = 300 would
   have had some power for large theta. This is accepted for time.
4. The exchangeability of H images with the calibration fold is an assumption; H-CAL can show a violation, not prove exchangeability.
5. The estimand weights subsets equally; it is not SugarCrepe's natural mixture and not COCO's.
6. All GPU-hour figures are estimates from M4; the time rule uses named constants so that no one improvises.
7. A p-value says nothing about novelty or practical importance; H does not change the novelty verdict (0.50, incremental).

## A5.17 Amendment log row (for the lead, only if adopted)

| Date | Change | Reason | Before/after outcome data? |
|---|---|---|---|
| 2026-10-29 | Addendum A5: new family H (SugarCrepe hard negatives, m = 3) and H-M (m = 3, gatekept); pool, stratified one-row-per-image sampling, H3 pilot 50 and H4 300; H3 rule on the realised gate's unsigned discordance and the restoration bound, with NO-GO; calibration reused with an exchangeability check; length strata; outcome book and placement rules; AB.1 extended to H; code delta scoped to H; time rule (H3 by Fri 12:27 IST) and cut order (suite, H4, H3, ...) | after P's NEGATIVE result and the A2.3 audit of PS, to test the same contrast where decisions have more headroom | **after** P, PS, S-M, E-dec, E-pred and Tier-3 outcomes (P and PS read by the author; Tier-3 one-line summary seen); **before** any H item; DRAFT until Shlok's approval row |

---

## Appendix H. Power and rule arithmetic (CPU, stdlib only)

Script: `a5_power.py` (SHA-256 `a3d36ce7cb44d8fd22b32ec2075a388078f28d624a6ffc8496594a964703de81`), output `a5_power_output.txt` (SHA-256
`102141db6637ebad0e57c02cc861b430ff549545b5edf60596504db6dba794b4`), both in the session scratchpad
`C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\`.
If A5 is adopted, the lead copies the script to `analysis/paper2/gate/a5_power.py`, reruns it into `runs/P2-GATE-A5/a5_power_output.txt` and
checks the two hashes. Method: exact two-sided McNemar conditional on n_d; n_d ~ Bin(n, pi_d), b | n_d ~ Bin(n_d, theta); rejection counted in the
favourable direction at alpha' = 0.05/3; MDE on a 0.005 grid of theta.

Key output lines:
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
The restoration-bound examples (3, 1) -> (18, 6), p 0.023, and (4, 1) -> (24, 6), p 0.0014, in A5.5 are hand arithmetic with the same exact
formula (2 x P(Bin(24, 0.5) <= 6) and 2 x P(Bin(30, 0.5) <= 6)); the auditor rechecks them with the script's `mcnemar_p`.
