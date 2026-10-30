```yaml
agent: experiment-designer
date: 2026-10-28
brief: One preregistration card that freezes the MUST tier (M0-M5) of the GATE experiment before any M1-M5 GPU outcome exists. Summarises and points; derives nothing new except where marked "card addition".
card_id: PREREG-GATE-MUST-2026-10-28   # no hypotheses-ledger row added (brief: write only this file); see concerns
sources_examined:
  - research/CONTRACT.md
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (full)
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (lines 1-587 and 610-775: all of sections 1-11, Appendix A outputs, Addendum 1; the Appendix A power script body 588-609 not read)
  - research/paper2/prereg/GATE-CODE-AUDIT-2026-10-28.md (lines 1-206, full)
  - research/paper2/method/GATE-IMPLEMENTATION-NOTES-2026-10-28.md (full)
  - research/paper2/probes/PROBE2-CRASH-DIAGNOSIS-2026-10-28.md (full)
  - research/paper2/ideation/NOVELTY-REAUDIT-GATE-2026-10-28.md (lines 48-67 and 174-208: verdict, claim sentence, surviving sentence, must-not-claim list; the search log and difference matrix not read)
  - runs/P2-GATE-FOLDS/folds.json (SHA-256 recorded below; keys, sizes and meta read)
  - research/progress.md lines 3-9 (HANDOFF 51-53, for the probe-1 caption-only control and the hold state)
coverage: >
  The sources above were read as listed. NOT read: GATE-METHOD-SPEC v1 (spec v2 says v1 stays the reference for notation, context levels
  A-D and Props. 3, 6, 7), RED-TEAM-GATE-SPEC, any source code under exp_p2/ (only command-line flags were grepped to check that the
  commands below exist: gate_driver.py lines 33-57, run_gate_m1.py/m5.py and probe2_guarded.py docstrings, coherence_report.py), any
  run file other than folds.json and directory listings. Nothing was run on a GPU. One CPU test run was made (section 11).
claims:
  - statement: "Every outcome clause of the GATE claim is a hypothesis; no M1-M5 outcome exists."
    status: unknown
    evidence: "runs/ contains P2-PROBE-01 (300 items), P2-PROBE-02 (21 items, runs/P2-PROBE-02/items.jsonl has 21 lines), P2-GATE-CPU (CPU dry run), P2-GATE-FOLDS; no P2-GATE-M1..M5 or P2-M0-* directory (listing taken 2026-10-28)"
    level: E0
    confidence: 0.9
competing_explanations: [mask geometry rather than detection; texture or encoder instability rather than corruption; pixel-domain denoising does the same job; dilution of evidence without any gain from removal]
unknowns: [everything listed in section 15]
next_test: {hypothesis: "H-G, section 2", intervention: "M0 then M1-M5, section 12", primary_metric: "exact McNemar on Y, GATE-M vs none, Holm m=3", falsifier: "no Holm rejection with b>c in family P", gpu_hours: "2.61 estimate for MUST (spec 11.1), about +0.8 to 1 if the test fold is 500"}
```

# Preregistration card: GATE, MUST tier (M0-M5)

**Status: frozen at commit `3ab566476ac87c64e482dfc25e7f4ce2b4d5fd2b` (branch `claude/frosty-clarke-209639`, commit time 2026-10-28T02:20:25+05:30), before any M1-M5 GPU outcome.**
"Frozen at" refers to the code, tests, SAP, folds and sources listed in section 14. The card is binding only after `statistician` and `red-team` sign it
(section 16: both **not yet signed**); the commit that adds this card file is appended to the change log when it exists. After signing, a change is a new version with a
change log, never an edit.

**Precedence.** SAP Addendum 1 > SAP body > spec v2 > spec v1. This card summarises; if it disagrees with the SAP, the SAP wins and the disagreement is a card defect to fix by a new version.
Number provenance: every number below is copied with its location (file, section or line). "Estimate" is the spec's word for unmeasured GPU time. Anything marked **card addition** is new in this card
and needs the signers' agreement; there is one (C1, section 7).

---

## 1. Claim contract

**One-sentence claim (the novelty re-audit's surviving sentence, `NOVELTY-REAUDIT-GATE-2026-10-28.md` lines 187-188, copied):**
"On a pretrained unified text-image masked diffusion model, with no finetuning, we score each input token by its masked likelihood in its own modality with the other modality withheld, set the flag threshold by conformal risk control on clean pairs so that the expected false-alarm proportion on clean inputs is at most alpha, and measure whether re-masking or re-infilling the flagged tokens preserves two-way cross-modal verification under image-token and caption corruption."
Spec v2 section 2.1 states the same claim with "UniDisc 1.4B" and "re-masking (or re-infilling)". In the MUST tier only the image-token corruption and re-masking (marginalise) are run; caption corruption (S1) and re-infilling (S2) are SHOULD and **not frozen here** (section 13).

**Mechanism** (spec v2 section 5, re-audit section 1): an absorbing-state denoiser gives p(x_j | partial context) for any mask pattern, so masking a gated token marginalises it (Prop. 1, a standard property, not a contribution); conformal risk control sets the threshold (Prop. 5, CRC applied, not a contribution); the evidence-separation rule keeps cross-modal terms out of the gate score.

**Closest methods and the exact distinction** (spec v2 section 2.4; content E1 in this project, re-audit E2-partial):
- Trust but Verify (arXiv 2610.22380): text-only 170M model, finetuned, scores the observed token at its unmasked position, hand-annealed threshold. GATE: pretrained unified model, no finetune, mask-then-score within modality with the other modality withheld, two modalities.
- Gomes et al. (2504.01225): CRC with masking scores for caption word errors, calibrated on labelled foil data. GATE: calibration on clean pairs, token losses nested in items, generative within-modality score, image-token gate.
- CO2Jump (2607.13188): remasks the sampler's own generated tokens with cross-modal confidence. GATE: input tokens, evidence-separation rule.
- UniDisc App. G.1: random mask, re-infill, best of n (S2, not MUST).
The delta that survives is narrow (re-audit verdict "incremental", confidence 0.50) and only as a measurement paper (re-audit line 189). The nine must-not-claim items of re-audit lines 191-200 / spec 2.2 apply to every sentence written from these runs.

**Competing explanations (to be separated by the controls of section 6):**
1. Mask geometry, not detection (red team M5): a mask of the same shape elsewhere gives the same effect. Control: geometry-matched random gate.
2. Texture or encoder instability, not corruption (red team M4): cheap non-generative detectors do as well as q on the changed-code labels. Control: S-D, S-D2. Disclosure: in the 21-item dry run a sign-flipped pixel-variance baseline beat plain-B (section 8).
3. Pixel-domain denoising does the same job more cheaply (red team M4b). Control: S-DN.
4. The independent-token model of Prop. 4 is wrong, so removal helps (or not) for a reason other than the predicted SNR change. Check: Prop. 4 plug-in (Tier 3).
5. The model is not coherent across mask patterns, so marginalisation by masking is not the right treatment. Check: Alg. 12 (M5).

## 2. Hypotheses

- **H-G (headline, family P).** On UniDisc 1.4B with COCO val2017 images as tokenised by LlamaGen VQ-16, GATE-M (image tokens flagged by the frozen gate removed from the set R) gives higher paired correctness of the image-direction verification statistic than no gate, for at least one of: JPEG, Gaussian noise, pixel splice, each at the rung chosen by the headroom rule (SAP 2.2, 2.4).
  H0 per corruption: equal marginal accuracy, Pr(Y^GM=1, Y^none=0) = Pr(Y^GM=0, Y^none=1).
- **H-cal.** The calibrated threshold gives realised false-alarm proportion on clean test items consistent with at most alpha (SAP 6; a pass is "no evidence of violation", never "validated").
- **H-det.** q (= B - D, the gate statistic) detects changed codes better than the best cheap baseline on JPEG q10 and noise 0.10 (SAP 2.5 S-D; spec 7.6).
- **H-mech.** Where H-G holds, the effect exceeds that of a random mask of the same shape (S-M).
- **H-coh.** The model is coherent across mask patterns within numerical noise (Alg. 12; reported, it conditions how Props. 1 and 6 are described).

Predictions stated in advance (spec 5.1, 7.4): masking should help most for sanity corruptions (patch, swap) and least, possibly not at all, for JPEG and noise; GATE on clean images should cost a little and never gain (Prop. 4, rho = 0); M >= I (Prop. 6, S2, not run in MUST). The spec's own confidence that GATE-M beats no gate is 0.35 (spec yaml, SAP yaml).

## 3. Primary endpoint and test

| Item | Fixed value | Location |
|---|---|---|
| Unit | one test image with its true caption c+ and its fixed deranged negative c- (probe-1 protocol; same c- for every arm and corruption) | SAP 2.1 |
| Statistic | Delta_j = Lambda^{c+}_j[v_j] - Lambda^{c-}_j[v_j], image direction, one caption-only pass per caption; Y = 1[mean over R of Delta_j > 0]; ties and empty R count as wrong (Y = 0) | SAP 2.1; spec Alg. 5' |
| Arms | none: R = all 1024 image tokens of the corrupted image. GATE-M: R = tokens not flagged by the frozen gate (q, K = 8 complementary masks, caption masked, pooled CRC at alpha = 0.05, jitter) | SAP 2.1; spec 4.1, 6 |
| Primary endpoint | paired correctness Y, GATE-M versus none, per corruption in family P | SAP 2.2 |
| Test | exact two-sided McNemar on discordant items: p = min{1, 2 Pr(Bin(n_d, 1/2) <= min(b, c))}; b = GATE-M right and none wrong | SAP 2.3 |
| Family P | exactly three hypotheses, always: P1 JPEG, P2 Gaussian noise, P3 pixel splice, at the headroom-selected rung. A corruption with no operating point is not tested, gets p = 1, and stays in the family (m = 3). Holm step-down at FWER 0.05: 0.05/3, 0.05/2, 0.05 | SAP 2.4 (departs from spec 7.1 "at most 3"; SAP wins) |
| Support for the claim | at least one P-hypothesis rejected after Holm **with b > c**. A rejection with c > b is reported as "GATE-M worse than none" and does not count | SAP 2.3, 2.4 |
| Effect size reported with every test | b, c, n_d, n, both accuracies, (b - c)/n with paired percentile bootstrap CI (10,000 resamples) at 95 and 98.33 percent, Clopper-Pearson CI of theta = b/n_d, mid-p as sensitivity only | SAP 2.3 |
| Practically meaningful effect | the design MDE at n = 300 with pi_d = 0.10 (ASSUMED): net accuracy gain +0.053 unadjusted (16 net items), +0.060 at the Holm first step (18 net items), needing about 80 percent of discordant items to favour GATE-M. Over pi_d in [0.04, 0.30] the Holm-level MDE is 0.036 to 0.105 | SAP 4.3 |
| Equivalence margin (null case) | +/-0.05 net accuracy, 90 percent paired-bootstrap CI | SAP 7 (last row), 9 |

Estimand: paired accuracy difference for one 1.4B model, one corruption realisation per image, one mask seed, "clean" = COCO as tokenised (SAP 1; spec 6).
The sanity corruptions (patch, swap) are not in P; they are exploratory (SAP 2.4).

## 4. Secondary and exploratory analyses with their families

Tier 2 (confirmatory-secondary, each its own Holm, none shares alpha with P, none can rescue a failed P, none may be a headline in the abstract; SAP 2.5, A1.2, A1.3):

| Family | Test | m | Notes |
|---|---|---|---|
| S-M mechanism | exact McNemar, GATE-M vs geometry-matched random gate, **seed 1** (code name `geo0`) | 3 | gatekept: only corruptions rejected in P with b > c; others p = 1, m stays 3. Seeds 2 and 3 are unadjusted replications. K5, K6 flags |
| S-Z evidence | Wilcoxon signed-rank on the paired change of the size-normalised evidence d (reported as z* = 32 d), two-sided; paired bootstrap CI of the mean | 3 | endpoint d, not z (Addendum A1.1); z reported as sensitivity. Items with |R| < 2 or sd = 0 are missing for this family and counted |
| S-DN denoise | exact McNemar, GATE-M vs pixel-domain denoise (OpenCV `fastNlMeansDenoisingColored`, library defaults) | 2 | JPEG and noise only; splice has no denoise arm (A1.3 N2; supersedes m = 3) |
| S-D detection | per-item AUROC of q minus per-item AUROC of the best cheap rival, paired bootstrap over items, two-sided p | 2 | JPEG q10 and noise 0.10 on the 200 probe-2 items. Rival = the highest mean AUROC among: patch texture (+/-), neighbour codebook distance (+/-), code rarity (+/-), s3, plain-B, Trust-but-Verify-style score if U7 allows; random and r_original excluded. Sign included (sign oracle, generous to the rival). Items with < 5 corrupted or < 5 clean tokens excluded and counted. Two sensitivities: rival re-selected inside each resample; items 21-199 only (179 items) |
| S-D2 out-of-sample detection | same contrast with the rival and sign frozen in `detection_frozen.json` after M1, tested on the M4 test items at the M4 operating points | 2 | no operating point = p = 1, m stays 2; rarity uses `runs/P2-GATE-M2/codefreq.npy` |
| S-C clean control | exact McNemar, GATE-M vs none on clean test images | 1 | unadjusted; predicted small loss (spec 7.4) |

Tier 3 (exploratory; descriptive intervals only; no p enters a claim; each labelled "exploratory"; SAP 7): token-level AUROCs of q, plain-B, s3, r_original, texture, neighbour distance, code rarity, Trust-but-Verify-style, random against changed-code labels; the graded label Z^big; severity sweeps and sanity corruptions (patch, swap); other gating arms (plain-B top-k, s3 top-k, scattered random, geo seeds 2-3, changed-code gate, denoise + GATE-M) vs GATE-M with McNemar counts; text-direction conditioning arms (marginalise, impute, none; statistic = mean per-token PMI); two-way fusion (analysed only if the best single direction has clean-test accuracy below 0.95, otherwise stated untestable); the Prop. 4 plug-in check and its pre-stated refutation (spec 5.3); the Alg. 12 coherence test; sensitivities (alpha 0.01 and 0.10, mid-p, 20 other jitter seeds, drop counts); frozen-rival top-k gate (A1.2 rule 6, only if per-token Delta is stored); hard-negative results (selected subset, yield 74 and 76 percent, A1.3 N12). The calibration diagnostics of SAP 6 (realised FAP, Z_cal, precision, FAP on clean tokens of corrupted items, spatial map, 2,000-split replication) are reported with equal prominence to the main result.

## 5. Arms

Image-direction arms (all reuse the two caption-only passes per item; spec Alg. 5', 4.3, 7.4):
none; GATE-M; geometry-matched random gate (Alg. 10: GATE's own mask translated by a random non-zero torus shift; 3 seeds); scattered random gate (3 seeds); changed-code gate (labels from the corruption; the upper bound for sanity corruptions only, not for JPEG/noise); plain-B top-k and s3 top-k (equal size to GATE-M's mask); pixel-domain denoise (JPEG, noise); GATE on clean images.
Corruption conditions in M4: clean, the headroom-selected rungs of JPEG / noise / splice (at most 3), patch (sanity), denoised copies (JPEG, noise).
Text-direction conditioning arms (exploratory): none, GATE-M, geometry seed 1, changed-code, for the three realistic corruptions; clean with none and GATE-on-clean (spec 11.1 M4 row; A1.3 N8: not run for patch or denoised copies).

## 6. Controls and negative controls

| Role | Control | Expected | Location |
|---|---|---|---|
| Mechanism control | geometry-matched random gate (3 seeds); S-M with seed 1 | if GATE-M works by detection, GATE-M > G^geo. K5: S-M not rejected for a P-rejected corruption means "not attributable to detection beyond mask geometry". K6: |b - c| <= 2 vs G^geo on every P-rejected corruption, same wording | SAP 2.5, 8.5 |
| Mechanism control | scattered random gate (3 seeds) | removes sensors at random; leaves d unchanged in expectation | spec 7.4 |
| **Negative control (effect must vanish)** | GATE on clean images (rho = 0), S-C | small loss, never a gain (Prop. 4) | spec 7.4; SAP 2.5 |
| Negative control | r_original (cancellation control, v1 Prop. 3) | AUROC near 0.5; dry-run values 0.495/0.506/0.453/0.504 for swap/patch/jpeg/noise (n = 21, exploratory) | spec 4.2; notes section 5 |
| Negative control (data) | probe-1 caption-only control accuracy 0.497 (deranged negatives; no image information) | chance | `research/progress.md` HANDOFF 51 |
| **Positive control (known effect the pipeline must recover)** | (a) sanity corruptions patch and swap: model-based detection must be high. Dry run plain-B AUROC 0.967 (patch), 0.962 (swap), n = 21, exploratory; **no numeric pass threshold exists in the sources** | high AUROC | notes section 5 |
| Positive control | (b) the changed-code gate (removes exactly the corrupted sensors) must restore evidence on the headroom items: this is H2 of the headroom rule (T2 >= 2.0) | recovery | SAP 5 |
| Positive control | (c) clean-image pipeline recovery, **card addition C1**: the none-arm accuracy on the clean test images, reported with a Wilson 95 percent CI beside probe 1's 0.8433 (253 of 300), Wilson 0.798 to 0.880 (SAP A.1). Descriptive; if the new interval does not overlap 0.798-0.880 a pipeline audit against the unit tests precedes any interpretation; no rule, score, K, alpha or fold changes. Needs signers' agreement | probe-1 numbers: SAP A.1 |
| Pipeline integrity | L10 layout-only check; unit tests L1-L8 (fake network); fold-token check against the runtime tokenizer | pass or the stage stops | notes sections 1, 5; audit M9 |

## 7. Data, folds, seeds

- **Model and data.** UniDisc 1.4B (pretrained, not trained here); COCO val2017 images and captions (5-32 caption tokens), instances_val2017 annotations (U4) for deranged-negative restriction and hard negatives; LlamaGen VQ-16 tokenizer at 512 px, 1024 image tokens (32 x 32 grid). Contamination (U8: COCO val2017 in UniDisc or LlamaGen-VQ training data) is an unknown and a stated limitation (spec yaml, 11.2 S6).
- **Folds.** `runs/P2-GATE-FOLDS/folds.json`, tracked since commit `b18129f9`. **SHA-256 `450edb543779de7ee5e6a52422fd6507ef52f15ba3b956a8b05c2e561620f311`** (computed 2026-10-28 with `sha256sum`). Internal `meta.sha1` `3dfed9ee90b340a9`; meta: seed 20261029, sizes [300, 100, 500], test_base 300, tok_range [5, 32], n_excluded 494, annotations_used true. Keys: `cal` 300, `head` 100, `test` 300, `test_ext` 200 (test = ordered 500-list, entries 1-300 base, 301-500 extension). Audit (E4, CPU): 900 distinct ids, zero overlap with the 494 probe ids (300 probe-1 + 200 probe-2 - 6 shared), negatives inside their own block, caption tokens 8-31 (`GATE-CODE-AUDIT` section 2). Property test: test300 == test500[:300] including negatives (`test_gate_data.py:180`).
  Fold roles: calibration 300 (threshold, fusion weights, rarity table, Alg. 12); headroom 100 (operating points, sample-size rule; **no GATE flag computed**); test 300 (500 if rule R2); detection (M1) uses the 200 probe-2 items.
- **Seeds.** Mask partitions: `SEED_GATE = 20261029`, per-item key = fold offset (cal 0, head 1000, test 2000) + index; M1 reuses probe 2's own seeds (notes N6). Analysis: `numpy.random.SeedSequence(20261028)` spawned by analysis name, 10,000 bootstrap resamples everywhere, percentile intervals, seed and NumPy version in every output (SAP 8.4). Random gates: seeds 1, 2, 3; confirmatory seed 1 only. Jitter: seeded from the item id; primary one seed; 20 others as sensitivity. Corruption seeds (noise draw, splice donor and location) derive from the item id. No training seeds exist (SAP 8.3).
  Not in the intervals (stated limitation): mask-seed and corruption-seed variance.
- **Dry-run disclosure** (SAP A1.2): the first 21 probe-2 items were analysed on CPU before the SAP addendum (`runs/P2-GATE-CPU/m1_fallback/analysis.json`, exploratory, no q): mean per-item AUROC vs changed-code labels, JPEG plain-B 0.543, sign-flipped pixel variance 0.756; noise plain-B 0.515, sign-flipped pixel variance 0.774. So no sign of the pixel-variance baseline can be claimed fixed blind. M1 new items are 21 to 199 (179 items).

## 8. Detection falsifier and rules around it (SAP A1.2, spec 7.6)

Falsifier met for a corruption if q does not beat the best cheap rival at Holm-adjusted p <= 0.05 with a positive difference (or the rival is above q); met on both JPEG and noise = **K2**.
Pre-stated consequences of K2: the paper may not say q detects corrupted codes better than cheap methods or present model-based detection as a contribution of that comparison; the rival, its sign and its AUROC with CI are reported in the main text; the downstream test in P still runs and a pass is worded "a gate built on q helps"; the rival's win is reported as the red team's label-circularity concern, not as evidence that texture explains the corruption effect. The paper states in the same sentence that the comparator is chosen on the data (a sign oracle over about nine candidates), which biases q minus rival downward.

## 9. Headroom go/no-go and sample-size rule (SAP 4.6, 5, A1.1; spec 7.3)

- **Data.** 100 headroom items, no GATE flag read or computed (the script asserts absence).
- **Endpoint.** The size-normalised evidence d (z* = sqrt(m) d = 32 d). Run as `python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d`; `family.json` must record `"endpoint": "d"`, otherwise it is invalid for this SAP and M4 refuses it.
- **Rung passes iff** n_v >= 90 **and** T1 >= 2.0 **and** T2 >= 2.0, where T1 = paired t of (clean - corrupted-none), T2 = paired t of (changed-code gate - corrupted-none), over the n_v items with all three values finite.
- **Ladders** (walk in order; first passing rung is the operating point): JPEG quality 10 then 5; Gaussian noise sigma 0.10 then 0.20; splice a 128x128-pixel region from another COCO image at a random location, then 192x192. No other rung, no other criterion.
- **GO** iff at least one corruption has an operating point. **NO-GO**: M4 still runs for detection, calibration and the clean control; the downstream claim (H-G) is withdrawn (K1); the paper reports measurement only.
- **Sample-size rule** (decided on headroom items before any test item is scored): D_c = number of headroom items whose Y differs between the changed-code gate and none; D* = max over corruptions with an operating point; N* = 43 (exact, theta 0.75, Holm first step); kappa = 0.5 (ASSUMED). **R1** D* >= 29: test fold = first 300 ids, endpoint Y. **R2** 18 <= D* < 29: first 500 ids, endpoint Y. **R3** D* < 18: first 300 ids, primary endpoint becomes the paired change of d (Wilcoxon, family P keeps labels P1-P3 and m = 3; Y moves to secondary). The decision, D_c, D* and the rule outcome go into `family.json`, committed before the first test item is scored. `run_gate_m4 --n` is checked against the rule (audit M3, fixed).
- Rung-pass behaviour under no true effect: each of T1, T2 passes with probability 0.024; at true standardised effect 0.1/0.2/0.3/0.4/0.5 it passes with probability 0.16/0.50/0.84/0.98/1.00 (SAP A.2). The rule excludes corruptions whose true drop is below about 0.2 sigma_d, an intended bias toward a smaller family.

## 10. Sample size and power (SAP 4; derived under ASSUMED A1-A4, not results)

Base fold n = 300, extension to 500 by rule R2. Required discordant count for exact power 0.8 at theta 0.75: 35 (alpha' 0.05), 42 (0.025), 43 (0.0167) (SAP Table A; the spec's normal-approximation 29 and 39 are optimistic). Power at n = 300 for (pi_d, theta) = (0.10, 0.75): 0.744 at 0.05 and 0.592 at 0.0167; (0.13, 0.75): 0.865 / 0.748; (0.15, 0.70): 0.737 / 0.577; (0.20, 0.65): 0.604 / 0.427 (SAP A.2). Smallest n for (0.10, 0.75): 340 (0.05), 430 (0.0167); n = 500 does not cover (0.10, 0.70), which needs 685 (SAP 4.4). Secondary z/d change MDE: 0.162 sigma_d (n = 300, alpha' 0.05), 0.188 (0.0167), 0.126/0.145 at n = 500 (SAP 4.7). Detection (n = 200 items): MDE of the mean paired AUROC difference 0.198 sigma_diff (alpha 0.05), 0.218 (0.025); no per-item AUROC spread exists, so S-D is not formally powered (SAP concern 4).
Missing items: complete-case per analysis; a crash leaves a prefix in list order, no replacements, no reordering; if completed base-fold n < 240 the paper states the fold is under 80 percent complete, prints the MDE at the achieved n, and "not rejected" is not read as evidence against GATE-M; worst-case missing-item sensitivity reported (SAP 8.1). No interim peeking: the analysis scripts that compute Y, b, c, p or d-differences are not run on M4 data until the planned fold is complete or the freeze (SAP 8.2).

## 11. Stop and kill rules

### 11a. Scientific (SAP 8.5; spec 11.5)
| Rule | Trigger | Action |
|---|---|---|
| K1 headroom | no corruption has an operating point | H-G withdrawn; M4 runs for detection, calibration, clean control only |
| K2 detection | S-D falsifier met on both JPEG and noise (section 8) | no claim that q beats cheap baselines; M4 continues as a measurement |
| K3 primary | no Holm rejection in P with b > c | "GATE-M improves verification" withdrawn; section 12 null reporting applies |
| K4 calibration | Z_cal > 2.13 at any of alpha 0.01, 0.05, 0.10 (z_0.9833; SAP 6) | stop the claim of a working guarantee until a bug audit against the unit tests ends; no change to score, K, alpha or fold; any rerun is an amended run beside the original |
| K5 mechanism | S-M not rejected for a P-rejected corruption | "not attributable to detection beyond mask geometry" |
| K6 geometry | \|b - c\| <= 2 vs G^geo on every P-rejected corruption | same wording as K5 |
| K7 pipeline | more than 5 percent NaN or empty R in an arm | stop and diagnose from logs and unit tests (no look at Y), report, rerun the arm as amended |
Also: M1 falsifier met on JPEG and noise -> continue M4 only as a measurement of a negative result; M3 empty family -> skip the downstream claim (spec 11.5). No futility stopping inside M4, no early stopping for success, no new items after seeing results. Test-set results never choose hyperparameters or wording; score, K = 8, alpha, fold sizes, rungs and the arms are fixed (spec 4.1).

### 11b. Safety (crash diagnosis section 5; guards in `exp_p2/gate/guards.py`, `watchdog.py`; audit section 4)
Cause of the two crashes is a hypothesis (H1/H2: nvlddmkm driver fault on idle-to-boost ramps, aggravated by AC flapping; about 50 percent, diagnosis section 1). No code can remove a driver fault.
Abort immediately and do not retry the same stage until reviewed (diagnosis section 5):
- whole-GPU used above 9,000 MiB (10,000 MiB during the first item) or a rise of more than 1.5 GB between consecutive 1 s samples;
- GPU temperature at or above 75 C (diagnosis abort list) or throttle reason other than 0x0/0x4;
- AC lost, or a Power source change event;
- `nvidia-smi` slower than 3 s or returning NA/empty;
- an item taking more than 2x the stage median;
- any new LiveKernelEvent 117, nvlddmkm 153, Display 4101 in the System or Application log.
Implemented in code (notes section 7; audit-fix commits 5cee34a9, 8704dd2f): HOLD files checked at start, every chunk and before every item; guard abort exit **76**, never relaunched (driver exits 8); soft deadline exit 75 (relaunch allowed); event-log check between chunks, exit 9 on a hit or unreadable log (fail closed); AC check before the model load; 1 s watchdog thread ending the process with 76; `gpu_guard.py --every 1 --max-temp 80`; resumable loop. **Not enforced in code** (operator watches): the throttle-reason rule and the nvidia-smi NA/slow rule; the event-log check does not stop hand-launched M0 stages (it prints a summary); direct `python -m exp_p2.run_gate_m*` bypasses `gpu_guard` (notes section 7, audit section 4). The code's temperature limit is 80 C; the diagnosis lists both 75 and 80 (audit M10): a decision for ANONYMIZED (section 15).
Decision rule (diagnosis section 5): a crash at M0 stage 2 (probe 1 control) means environment (H1/H2/H3): **no GPU job until the driver is reinstalled and power is fixed (ANONYMIZED's call)**. A crash at stage 3 but not 2 means H4/H5, bisect by corruption (stage 4, `--only` switch, not built). Any abort or crash at any M0 stage: GPU stays on hold, go to the CPU-only fallback of spec 11.4 (feasibility and measurement note; not an Information Fusion research article; ANONYMIZED decides between that note and a later deadline). A guard abort counts as a crash for the missing-data rule (A1.3 N14).
Operator preconditions (diagnosis section 4, items 1-2): original AC adapter on a stable outlet, no `Power source change` (System Id 105) in the last 30 minutes, ANONYMIZED present, Ollama, Codex/ChatGPT app, Chrome, NVIDIA Overlay and the NVIDIA app closed, `nvidia-smi` showing no compute process and under 700 MiB used. No unattended or overnight GPU run (spec 11.5).

## 12. What is reported if the primary result is null

The paper's claim is already worded as a measurement, so a null changes content, not framing (SAP 9). Required whatever happens: the full P table with all three hypotheses (those without an operating point shown as "failed headroom at both rungs" with T1 and T2), b, c, n_d, (b - c)/n with 95 and 98.33 percent CIs, exact p and Holm-adjusted p. Allowed wording (SAP 9 table):

| Outcome | Allowed wording |
|---|---|
| P rejects with b > c and S-M rejects for the same corruption | "GATE-M improved image-direction verification over no gate on X, beyond what an equally shaped random mask gives" (scope: one model, one corruption, one severity) |
| P rejects, S-M does not | "improvement, but not distinguishable from masking the same shape elsewhere" |
| P rejects with c > b | "GATE-M reduced verification accuracy" |
| P does not reject | "no improvement was detected; the data are compatible with a net accuracy change between L and U (95 percent CI)". Never "GATE-M has no effect". If the 90 percent CI lies inside (-0.05, +0.05), "an improvement larger than 0.05 is excluded" (claimable only when realised discordance is low) |

Card reading of the three-way outcome (derived from SAP 9, no new threshold): **positive** = at least one P rejection with b > c after Holm; **negative** = no rejection and the 90 percent CI inside (-0.05, +0.05) at completed n >= 240; **inconclusive** = no rejection with a wider CI, or completed n < 240, or K7, or NO-GO (K1).
For a null also reported (Tier 2/3, labelled): realised n_d and the sensitivity statement "with this n_d only theta >= theta* would have been detectable" (not an observed power); S-Z result; the Prop. 4 plug-in check (does the independent-token model predict the null?); S-D and S-D2; the calibration check; the headroom table (did corruptions harm verification at all?); the coherence test. A p-value says nothing about novelty or importance (SAP 9).
Fallback if the GPU stays on hold past Thursday noon: spec 11.4 (CPU-only note: unit tests, synthetic CRC study, partial probe-2 AUROCs on 20 complete items labelled exploratory, cheap-baseline fractions, probe-1 reanalysis).

## 13. Not frozen by this card

SHOULD tier S1 (caption typos), S2 (re-infill sampler, not built), S3 (hard negatives, runner not built), S4 (denoise + GATE-M), S5 (K ablations), S6 (contamination read) and COULD (E7 Omni-Diffusion 8B, T2I grid, Mondrian, iterated gate, fp32 head) are outside this card (spec 11.2, 11.3; notes section 4). Running any of them needs an addendum before the first item. They cannot enter family P or any Tier 2 family.

## 14. What "frozen" covers (commit and hashes)

| Artifact | Path | Pin |
|---|---|---|
| Code, tests, tools | `exp_p2/`, `tools/`, `tests/exp_p2/` | commit `3ab566476ac87c64e482dfc25e7f4ce2b4d5fd2b` (`git rev-parse HEAD` on 2026-10-28). Working tree has no tracked modification; untracked: `.codex/agents/*`, `research/paper2/MORNING-2026-10-28.md`, `research/sources/code_*`, `runs/P2-SMOKE-02/` (none part of MUST) |
| Folds | `runs/P2-GATE-FOLDS/folds.json` | SHA-256 `450edb543779de7ee5e6a52422fd6507ef52f15ba3b956a8b05c2e561620f311` |
| SAP + Addendum 1 | `research/paper2/prereg/SAP-GATE-2026-10-28.md` | SHA-256 `9c8ad868b6154dfce336a800fb703f4a4b06a476646f67492142a126fd14fec6` |
| Spec v2 | `research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md` | SHA-256 `04470bef4e5211b442bb276dd4c8f4adc03627688bc559d5c64819f63c933a9b` |
| Implementation notes | `research/paper2/method/GATE-IMPLEMENTATION-NOTES-2026-10-28.md` | SHA-256 `fcd933aefd658ffe5de6eb64189d40e0e7554e3245343029511505868a0e91ef` |
| Code audit | `research/paper2/prereg/GATE-CODE-AUDIT-2026-10-28.md` | SHA-256 `32be9321e0d3f0902942514fa78c7ca121d83222651323decc264c8955efbe9c` |
| Crash diagnosis | `research/paper2/probes/PROBE2-CRASH-DIAGNOSIS-2026-10-28.md` | SHA-256 `286b91877205b29bbed6fd26d1e9cd53d612a13c9f889d3231ccb156d9936d07` |
| Novelty re-audit | `research/paper2/ideation/NOVELTY-REAUDIT-GATE-2026-10-28.md` | SHA-256 `c4acd02ae65ee8c97906cae53598a97defc1b3b3f477dce3afc028fd42d2f604` |

Test state at the freeze commit (E4, CPU, `CUDA_VISIBLE_DEVICES` empty, `python -m pytest tests/exp_p2 -q`, run by this agent 2026-10-28, output not stored in `runs/`): 170 tests (the notes section 7 say 166 after the MIN commit; the difference is not itemised here). **First full run: 169 passed, 1 failed (`test_gate_safety.py::test_ac_is_checked_before_the_model_load`); the same test passed alone; two further full runs: 170 passed.** The cause is undiagnosed (the test injects its own AC function, so the real machine's AC state or the watchdog thread is the first suspect; unverified). It must be understood before the first GPU launch (section 15, D9).
Pre-launch check, to run before each stage: `git diff --quiet 3ab566476ac87c64e482dfc25e7f4ce2b4d5fd2b HEAD -- exp_p2 tools tests runs/P2-GATE-FOLDS` must exit 0, and `sha256sum runs/P2-GATE-FOLDS/folds.json` must equal the value above. A non-zero result means the code changed after the freeze: stop and write an amendment (section 17).

## 15. Decisions that remain ANONYMIZED's (not made by this card)

| # | Decision | What the sources say | Source |
|---|---|---|---|
| D1 | **Release of the HOLD.** Delete `runs/P2-PROBE-02/HOLD.txt` only after ANONYMIZED says so and the cause is fixed. Every runner and the driver refuse to start while it exists (also `runs/GATE-HOLD.txt`, `runs/<run>/HOLD.txt`). Also his call: NVIDIA driver reinstall if M0 stage 2 crashes | HOLD text; diagnosis decision rule | `runs/P2-PROBE-02/HOLD.txt`; diagnosis section 5 |
| D2 | **Memory cap.** Runners default `--mem-frac 0.75` (about 9,170 MiB for PyTorch). The diagnosis proposes 0.60 (about 7.2 GiB), which is below the 8.2 GB first-item peak measured at batch 4. The 0.75 cap did not prevent crash 2 | needs an explicit yes | notes section 2; audit M2 |
| D3 | **Guard thresholds** (all CLI flags, defaults are proposals): whole-GPU 9,000 MiB, 10,000 MiB first item, rise 1,500 MiB, slow item 2x median, temperature 80 C (code) vs 75 C (diagnosis abort list), busy threshold 2,500 MiB (`driver.py:22`) vs the diagnosis' "under 700 MiB", chunk lengths 5 then 15 min vs "four clean 5-minute chunks before lengthening" | needs an explicit yes; record the chosen values as a change-log row before M0 | notes N14; audit M2, M10 |
| D4 | **Second mask-seed check** (SAP 8.3, 50 headroom items, 8 passes each, exploratory; needs the orchestrator). Note: it computes GATE flags on headroom items, which the blind rule of SAP 5 forbids before the operating points exist. If approved it may run only after `family.json` is committed, in its own run directory that the headroom script never reads | recommended by the statistician, not in MUST | SAP 8.3, 5 |
| D5 | **Deadline date.** The spec's timeline assumes GPU released Wed 28 Oct daytime, results frozen Fri 30 Oct 12:00, submission package Sat 31 / Sun 1; the SAP forbids outcome analysis before the planned fold is complete or "the freeze (spec: Fri 2026-10-30 12:00)". The spec's U9 notes the coordinator wrote "Fri 31 Oct / Sat 1 Nov". If the GPU stays on hold past Thursday noon the honest options are the CPU note or a later deadline | ANONYMIZED's decision | spec 11.5, U9, 11.4; SAP 8.2 |
| D6 | **Test fold 500 (rule R2)** costs about +0.8 GPU-h (spec 9) or about +1 GPU-h (SAP yaml), estimates. SAP concern 1 calls R2 the likely outcome | automatic by rule if D* in [18, 29); the time budget is his | SAP 4.6, 11 |
| D7 | **SHOULD/COULD tier** (section 13) and E7 | not frozen; each needs an addendum | spec 11.2-11.3 |
| D8 | **Unattended or overnight GPU runs**: not planned; the crash protocol assumes ANONYMIZED present | his call | spec 11.5 |
| D9 | **The one failing test** (section 14) and whether to accept the code as frozen before it is diagnosed; also the audit asked for a re-audit after F1-F6 and no re-audit file is on disk | gate-auditor re-audit | audit lines 205; this card section 14 |
| D10 | **Hand-launched M0 stages** have only an informational event-log check; the throttle and nvidia-smi-NA rules are operator-enforced. Accept, or have `gpu_guard.py` extended (a project tool, outside the audited package) | his call | notes section 7 "Not fixed"; audit M1 |
| D11 | **Optional system changes** (admin, driver level): lock the SM clock range with `nvidia-smi -lgc`, WinDbg `!analyze -v` of the two minidumps | not done by any agent | diagnosis section 4 items 3-4 |
| D12 | **Hard-negative audit**: a reviewer-agent pass on headroom and test hard negatives (not automated) and an optional 50-item human spot check; the exploratory S3 depends on it | his time | spec Alg. 11 step 4; notes section 2 |
| D13 | **TbV-style baseline**: `--tbv` on M1 and `--tbv auto` or `on` on M4 follow U7 (`tbv_verdict.json`); if the logits at unmasked positions copy the input the baseline is reported "not applicable" | automatic, but the flag choice at M4 is made after M1 | notes section 2; spec 4.2 |

## 16. Sign-off and change log

| Role | Signed | Date | Notes |
|---|---|---|---|
| experiment-designer | card written | 2026-10-28 | this file |
| statistician | **not yet** | | must confirm section 3, 4, 9, 10 against the SAP and accept or reject card addition C1 (section 6) |
| red-team | **not yet** | | must attack sections 1, 6, 8, 11 and the card reading of outcomes (section 12) |
| gate-auditor | no verdict on this card | | the code audit (`GATE-CODE-AUDIT`, PASS WITH FIXES) pre-dates the fixes; re-audit not on disk |

| Version | Date | Change | Before/after outcome data | Card commit |
|---|---|---|---|---|
| v1 | 2026-10-28 | initial card | before any M1-M5 outcome | to be appended after commit |

## 17. Amendment rule

A change to any frozen item (code at the pinned commit, folds, SAP, operating rules, thresholds D2/D3 once recorded) creates a new card version with a dated change-log row stating the reason and whether it was made before or after outcome data exist. Choosing D2/D3/D4/D5 values is not a change to the science; it is recorded as a log row before M0. A bug fix to code after the pinned commit is allowed only if (i) a unit test pins it, (ii) the fix is committed with its SHA in the log, (iii) it does not touch an analysis path that has already produced a number, and (iv) any outcome already produced under the old code is reported beside the rerun. Reruns are amended runs, never replacements.

---

## 18. Exact command sequence M0-M5

All from the worktree root. `PY` = `C:\Users\ANONYMIZED\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe`. Source: notes section 2 (commands were **not executed** by anyone; flags checked to exist by grep). Item-time GPU estimates from spec 11.1 (wall time about 2x at duty 0.5). A stage proceeds only if the previous stage's artifact is committed and its pass criterion holds. Commit SHA of the code for the whole sequence: `3ab566476ac87c64e482dfc25e7f4ce2b4d5fd2b`.

**Step 0. Preconditions (no GPU).** Pre-launch check of section 14; operator preconditions of section 11b; ANONYMIZED's decisions D1-D3 recorded; folds hash checked.

**M0. Crash-diagnosis stages (0.05 GPU-h, 10 + 5 items).**
```
:: stage 0 (CPU)
set CUDA_VISIBLE_DEVICES=
python -m pytest tests/exp_p2
:: stage 1: load, one batch-4 forward, 5 min idle (refuses while any hold file exists)
PY tools/gpu_guard.py --log runs/P2-M0-STAGE1/telemetry.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.run_gate_m0 --run-id P2-M0-STAGE1 --idle-minutes 5
:: stage 2: probe 1 control, 10 NEW items (run_probe1 unchanged inside gate.probe1_guarded)
PY tools/gpu_guard.py --log runs/P2-M0-STAGE2/telemetry.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.gate.probe1_guarded --run-id P2-M0-STAGE2 --n 10 --limit 10 --soft-minutes 10
:: stage 3: probe 2 items 21-25 (run_probe2 unchanged inside gate.probe2_guarded)
PY tools/gpu_guard.py --log runs/P2-PROBE-02/telemetry-m0s3.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.gate.probe2_guarded --run-id P2-PROBE-02 --n 200 --resume --limit 5 --soft-minutes 10
```
Pass: stage 0 all tests pass (see D9); stages 1-3 end without any abort rule of section 11b; stage 3: 5 items and memory plateau within 1 GB of stage 2 (diagnosis section 5 table). Fail: section 11b decision rule. Source edits to `run_probe2.py` proposed by the diagnosis are NOT made (they would change probe 2).

**M1. Detection (0.52 + 0.04 GPU-h, 179 new items + 200 post hoc).**
```
PY -m exp_p2.gate.gate_driver --stage p2                          :: completes probe 2 items 21-199, unchanged code under new guards
PY -m exp_p2.gate.gate_driver --stage m1 --extra "--tbv"          :: D at stored codes (<= 28 null passes) + TbV-style pass on the 4 corrupted images
python -m exp_p2.analyze_gate_m1 --probe-run P2-PROBE-02 --m1-run P2-GATE-M1      :: CPU: AUROC table, S-D, falsifier, tbv_verdict.json, detection_frozen.json
```
Commit `detection_frozen.json` (written only if all 200 items have all four `_D` arrays; write-once, `--force` logs an amendment) **before M3 or M4**; M3 and M4 refuse to start without it. The 21 dry-run items are included in the 200; the 179-item sensitivity is run (SAP A1.2).

**M2. Calibration fold (0.23 GPU-h, 300 items, 12 passes + 1 encode each).**
```
PY -m exp_p2.gate.gate_driver --stage m2          :: checks caption token counts against the frozen folds.json (folds_check.json); no new folds are built
python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2      :: CPU: threshold.json (requires eps0_resolvable True), codefreq.npy
```
Commit `threshold.json` before M4 (write-once).

**M3. Headroom (0.20 GPU-h, 100 items, 2 passes + 7 encodes each).**
```
PY -m exp_p2.gate.gate_driver --stage m3
python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d
```
Commit `family.json` (endpoint d, operating points, D_c, D*, rule R1/R2/R3 or NO-GO, T1/T2, n_v) **before the first M4 item**; write-once.

**M4. Main test (1.44 GPU-h at 300 items; about +0.8 to 1 at 500; 75 passes + 6 encodes per item, 70 passes without TbV).**
```
PY -m exp_p2.gate.gate_driver --stage m4 --extra "--tbv auto"      :: add --n 500 when family.json says R2; refuses to start without threshold.json, family.json, detection_frozen.json
python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-M4 --family-run P2-GATE-M3      :: CPU; endpoint d by default; refuses a partial fold unless --allow-partial (logged)
```
(`--extra "--tbv on"` instead of `auto` only if `tbv_verdict.json` allows; the notes list both.) The analysis is run once, after the fold is complete or at the freeze (SAP 8.2).

**M5. Coherence test (0.13 GPU-h, 100 calibration items, 24 passes each + 24 on every fourth item).**
```
PY -m exp_p2.gate.gate_driver --stage m5
python -m exp_p2.gate.coherence_report --run-id P2-GATE-M5 --mu <clean mean per-token paired evidence from M4>
```
Total item time 2.61 GPU-h (estimate; spec 11.1: 0.05 + 0.56 + 0.23 + 0.20 + 1.44 + 0.13), 3.9 with a 50 percent contingency, limit about 6. Per-row time 0.15 s and VQ encode at most 1 s are unmeasured assumptions to be measured in M0.
CPU only, any time: `python -m exp_p2.gate.cpu_dryrun`; unit tests; analysis `selftest()` (runs before the real analysis).

---

## 19. Concerns for the orchestrator

1. The card is signed by nobody but its author; the "frozen at commit" claim is true for the code and documents (section 14) but the card itself becomes binding only after statistician and red-team sign.
2. One of 170 tests failed in the first full run at the freeze commit (passed alone and in two reruns); cause undiagnosed (D9).
3. SAP 8.3's recommended second-seed check conflicts with the blind-headroom rule unless run after `family.json` is committed (D4).
4. Card addition C1 (clean-image recovery check) and the three-way outcome reading of section 12 are the only content not copied from the sources.
5. No `hypotheses` ledger row and no `research/prereg/<hyp-id>.md` copy were written (brief: write only this file; the contract path differs from the requested one).
