```yaml
agent: experiment-designer
date: 2026-10-28
brief: Version 3 (final freeze) of the preregistration card for the MUST tier (M0-M5) of GATE. v1 (PREREG-GATE-MUST-2026-10-28.md) and v2 (PREREG-GATE-MUST-v2-2026-10-28.md) are unchanged on disk. v3 = v2 plus every amendment after v2 (code commits through 164a18a5, the red-team sign-off, the code re-audit), re-pinned SAP and folds, the corrected pre-launch check and the updated list of ANONYMIZED's decisions. All v2 content not listed in section 16 is carried over.
card_id: PREREG-GATE-MUST-v3-2026-10-28   # no hypotheses-ledger row added (brief: write only this file); see concerns
supersedes: PREREG-GATE-MUST-v2-2026-10-28 (v2) and PREREG-GATE-MUST-2026-10-28 (v1); both kept on disk
sources_examined:
  - research/CONTRACT.md
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (full)
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (v1 read lines 1-587 and 610-775: sections 1-11, Appendix A outputs, Addendum 1; v2 additionally read lines 776-883: Addendum 2 (2026-10-28, sign-off), full; the Appendix A power script body 588-609 not read)
  - research/paper2/prereg/PREREG-GATE-MUST-2026-10-28.md (v1, own)
  - code facts for the v2 rulings, grep-level only: exp_p2/gate/headroom.py lines 13, 75-84; exp_p2/run_gate_m4.py line 59; exp_p2/gate/analysis_m4.py (no occurrence of R3 or primary_endpoint); exp_p2/gate/folds.py line 117-120; git diff 3ab56647..HEAD for exp_p2, tools, tests, runs/P2-GATE-FOLDS
  - research/paper2/prereg/GATE-CODE-AUDIT-2026-10-28.md (lines 1-206, full)
  - research/paper2/method/GATE-IMPLEMENTATION-NOTES-2026-10-28.md (v1 full; v3 additionally sections 8, 9, 10 in full)
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md (full, 173 lines: SIGN WITH CONDITIONS, 0.6)
  - research/paper2/prereg/GATE-CODE-REAUDIT-2026-10-28.md (full, 134 lines: PASS WITH FIXES at 857673b0)
  - git: rev-parse HEAD, log, diff --stat 2ab42a6e HEAD for exp_p2, tools, tests, runs/P2-GATE-FOLDS; sha256sum of every pinned file; one CPU test run (section 14)
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
competing_explanations: [mask geometry rather than detection; texture or encoder instability rather than corruption; pixel-domain denoising does the same job; dilution of evidence without any gain from removal; variance trimming of d under R3; changed codes in flat low-evidence regions]
unknowns: [everything listed in section 15]
next_test: {hypothesis: "H-G, section 2", intervention: "M0 then M1-M5, section 12", primary_metric: "exact McNemar on Y, GATE-M vs none, Holm m=3", falsifier: "no Holm rejection with b>c in family P", gpu_hours: "2.61 estimate for MUST (spec 11.1), about +0.8 to 1 if the test fold is 500"}
```

# Preregistration card: GATE, MUST tier (M0-M5)

**Status (v3): frozen at commit `164a18a551d598c33fa3f51d97cc71ceceff06f4` (`git rev-parse HEAD`, 2026-10-28, branch `claude/frosty-clarke-209639`; "implementation notes, re-audit fixes W1, N1, N4"), before any M1-M5 GPU outcome.**
Code identity: this is the final code pin. The code changed after v2's pin `2ab42a6e` (34 files, +1246/-93 under `exp_p2/` and `tests/exp_p2/`; none under `tools/` or `runs/P2-GATE-FOLDS`); every commit is logged as an amendment row in section 16 (rows v3-1 to v3-12). `tools/gpu_guard.py` is untouched (its committed blob hashes to the EXP-001 manifest pin).
"Frozen at" refers to the code, tests, SAP, folds and sources listed in section 14. Sign-offs: the statistician **signed with changes** (SAP Addendum 2, incorporated in v2); the red-team **signed with conditions** (`RED-TEAM-SIGNOFF-2026-10-28.md`, confidence 0.6; conditions C1-C6 recorded in section 16 with status); the gate-auditor's re-audit is **PASS WITH FIXES** (`GATE-CODE-REAUDIT-2026-10-28.md`, at `857673b0`; W1, N1, N4 fixed in `a2dda400`). Open at the time of writing, stated here so nobody reads "frozen" as "ready": the gate-auditor's delta check of `a2dda400` and `164a18a5` is not on disk; red-team C3 (fallback), C4 (manuscript wording), C5 (JPEG denoiser) and C6 (M0 procedure) are open (section 16); the HOLD is still in place (D1). The commit that adds this card file is appended to the change log when it exists. After signing, a change is a new version with a change log, never an edit.

**Precedence.** SAP Addendum 2 > SAP Addendum 1 > SAP body > spec v2 > spec v1. This card summarises; if it disagrees with the SAP, the SAP wins and the disagreement is a card defect to fix by a new version.
Number provenance: every number below is copied with its location (file, section or line). "Estimate" is the spec's word for unmeasured GPU time. This card has no addition of its own that the SAP or the red-team sign-off has not ruled on.

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
6. Variance trimming, not corruption detection (red-team N2, added in v3): the evidence ratio d = mean/sd rises when tokens with extreme per-token evidence are removed, whatever their reason; random gates keep the moments of d roughly unchanged, so only plain-B top-k and s3 top-k (Tier 3, no p-value) can separate the two. Under rule R3 their counts are reported next to the P result.
7. Changed codes sit mostly in flat, low-evidence regions (red-team N3): a small headroom drop or an empty family (K1) or a null P may then reflect that, not gate failure; no arm separates the two (dry-run sign-flipped pixel variance, section 7).

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
| S-DN denoise | exact McNemar, GATE-M vs pixel-domain denoise (**a sigma-matched non-local-means denoiser**: OpenCV `fastNlMeansDenoisingColored` with h = hColor = 25.5 grey levels, windows 7 and 21, `config.DENOISE_PARAMS`; NOT library defaults, see row v3-9; on JPEG q10 this setting lowers PSNR by 1.69 dB, so S-DN on JPEG compares GATE-M with an aggressive denoiser that harms the image and favours GATE-M, open decision D17) | 2 | JPEG and noise only; splice has no denoise arm (A1.3 N2; supersedes m = 3) |
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
| **Positive control (known effect the pipeline must recover)** | (a) sanity corruptions patch and swap, **chance bar only (SAP A2.5, binding pass/fail)**: for plain-B and for q, the lower 95 percent bound of the mean per-item AUROC against the changed-code labels is above 0.5, on the M1 items (for q, the 200 items that have D). Patch and swap replace tokens by uniformly random codes, so a likelihood-based detector at chance indicates a pipeline defect (sign, indexing, layout), not a scientific result. Failure triggers the pipeline audit of C1 below; nothing is tuned. The AUROC level, its CI and the comparison with cheap rivals are descriptive, no threshold; the dry-run values 0.967 (patch) and 0.962 (swap) are exploratory, n = 21, and are not a target. The bar says nothing about JPEG, noise or splice and passing it is not evidence for the claim | AUROC lower bound > 0.5 | SAP A2.5 |
| Positive control | (b) the changed-code gate (removes exactly the corrupted sensors) must restore evidence on the headroom items: this is H2 of the headroom rule (T2 >= 2.0) | recovery | SAP 5 |
| Positive control | (c) **C1 (SAP A2.3, descriptive pipeline check, no alpha, tests nothing)**: the clean-pair none-arm accuracy (same statistic as probe-1 b_full: image direction, all 1024 tokens, deranged negative) with its Wilson 95 percent CI, reported as "the clean none-arm accuracy was X (95 percent CI a to b), against 0.843 (0.798 to 0.880) in probe 1" (253 of 300; SAP A.1). **Audit trigger:** the new Wilson interval does not overlap 0.798 to 0.880. Action: a pipeline audit against the unit tests (L1 to L10, tokenizer, VQ encode, layout). No rule, score, K, alpha, fold, rung or arm changes on the strength of C1; a defect found means the arm is rerun as an amended run beside the original (section 17). **Timing (three looks, none pooled, none used to tune):** (i) on the clean calibration items right after M2, before M3 or M4 are launched (the M2 none-arm already exists and no GATE-M-versus-none test uses that fold); (ii) on the clean headroom items after M3 (no GATE flag involved); (iii) on the clean test items only at the analysis step after the planned fold is complete (SAP 8.2). Not a power or equivalence statement; never worded as "validation of the pipeline". A value above 0.88 is not alarming by itself (restricted deranged negatives are if anything easier; probe 1 was an exploratory variant choice, SAP A6) | probe-1 numbers: SAP A.1; ruling: SAP A2.3 |
| Pipeline integrity | L10 layout-only check; unit tests L1-L8 (fake network); fold-token check against the runtime tokenizer | pass or the stage stops | notes sections 1, 5; audit M9 |

## 7. Data, folds, seeds

- **Model and data.** UniDisc 1.4B (pretrained, not trained here); COCO val2017 images and captions (5-32 caption tokens), instances_val2017 annotations (U4) for deranged-negative restriction and hard negatives; LlamaGen VQ-16 tokenizer at 512 px, 1024 image tokens (32 x 32 grid). Contamination (U8: COCO val2017 in UniDisc or LlamaGen-VQ training data) is an unknown and a stated limitation (spec yaml, 11.2 S6).
- **Folds.** `runs/P2-GATE-FOLDS/folds.json`, tracked since commit `b18129f9`. **SHA-256 `450edb543779de7ee5e6a52422fd6507ef52f15ba3b956a8b05c2e561620f311`** (computed 2026-10-28 with `sha256sum`). Internal `meta.sha1` `3dfed9ee90b340a9`; meta: seed 20261029, sizes [300, 100, 500], test_base 300, tok_range [5, 32], n_excluded 494, annotations_used true. Keys: `cal` 300, `head` 100, `test` 300, `test_ext` 200 (test = ordered 500-list, entries 1-300 base, 301-500 extension). Audit (E4, CPU): 900 distinct ids, zero overlap with the 494 probe ids (300 probe-1 + 200 probe-2 - 6 shared), negatives inside their own block, caption tokens 8-31 (`GATE-CODE-AUDIT` section 2). Property test: test300 == test500[:300] including negatives (`test_gate_data.py:180`).
  **Real-tokenizer exclusion rule (SAP A2.1 item 2, design, before any score exists):** M2 to M5 compare the frozen token counts with the runtime `UniScorer.caption_ids`. An item whose real token count falls outside 5 to 32 is **excluded from every analysis, counted and not replaced**; the order of the remaining ids is unchanged, so the prefix property is kept as far as possible. The exclusion depends on caption text only, not on any score. If more than 10 percent of any one fold fails the check, stop and report a fold-construction defect; no refolding without a new card version. **Code state (v3): implemented in commit `f16dda8c` (`folds.token_check`, `pipeline.check_fold_tokens`): out-of-range items are excluded, counted, not replaced, order unchanged; more than 10 percent of one fold excluded (or a systematic in-range count mismatch above 10 percent) raises `FoldDefect` (stop and report; the report is on disk first); the runner writes `effective_n.json` and `token_exclusions.json`, which the driver, `fit_threshold`, `headroom` and the completeness report use. The gate-auditor ran it: 10 of 100 allowed, 11 of 100 a defect (re-audit section 2).**
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
v3 changes to the safety wiring (re-audit W1 and N4, commit `a2dda400`): the 1.5 GB rise rule is armed only after the first item of a chunk has completed, with a fresh baseline (`Guards.rise_armed`, shared with the 1 s watchdog), so the model load and the first item are held only by the absolute ceilings (10,000 MiB), AC and gpu_guard's temperature; the stored 5 s telemetry shows 4 to 6 GB steps at those moments (re-audit W1) that would otherwise have tripped exit 76 on a healthy run. The driver refuses to launch (exit 10) if `tools/gpu_guard.py` does not match the EXP-001 manifest pin (the committed blob, or its CRLF-normalised working copy). Still operator-enforced: throttle-reason and nvidia-smi NA/slow rules; M0 stage 1 has no watchdog (re-audit N6); the event-log check since the driver started, not since the last crash (re-audit N3). The later-item ceiling of 9,000 MiB remains a proposal (D3).

Operator preconditions (diagnosis section 4, items 1-2): original AC adapter on a stable outlet, no `Power source change` (System Id 105) in the last 30 minutes, ANONYMIZED present, Ollama, Codex/ChatGPT app, Chrome, NVIDIA Overlay and the NVIDIA app closed, `nvidia-smi` showing no compute process and under 700 MiB used. No unattended or overnight GPU run (spec 11.5).

## 12. What is reported if the primary result is null

The paper's claim is already worded as a measurement, so a null changes content, not framing (SAP 9). Required whatever happens: the full P table with all three hypotheses (those without an operating point shown as "failed headroom at both rungs" with T1 and T2), b, c, n_d, (b - c)/n with 95 and 98.33 percent CIs, exact p and Holm-adjusted p. Allowed wording (SAP 9 table):

| Outcome | Allowed wording |
|---|---|
| P rejects with b > c and S-M rejects for the same corruption | "GATE-M improved image-direction verification over no gate on X, beyond what an equally shaped random mask gives" (scope: one model, one corruption, one severity) |
| P rejects, S-M does not | "improvement, but not distinguishable from masking the same shape elsewhere" |
| P rejects with c > b | "GATE-M reduced verification accuracy" |
| P does not reject | "no improvement was detected; the data are compatible with a net accuracy change between L and U (95 percent CI)". Never "GATE-M has no effect". If the 90 percent CI lies inside (-0.05, +0.05), "an improvement larger than 0.05 is excluded" (claimable only when realised discordance is low) |

**Three-way outcome reading (SAP A2.2, binding; a reading of SAP 9, not a new test):**
- **positive** = at least one P-hypothesis rejected after Holm with b > c. It supports only "GATE-M improves image-direction verification over no gate on that corruption". Attributing the gain to detection needs S-M (SAP 9 table); positive does not imply it.
- **negative** = no P rejection **and**, for **every** corruption that has an operating point, the 90 percent paired-bootstrap CI of the net accuracy difference lies inside (-0.05, +0.05), **and** completed n >= 240 for that corruption. A corruption without an operating point contributes no evidence for a negative. The intersection over corruptions needs no multiplicity correction. **Under rule R3 (primary endpoint switched to d) the label negative is not available**; only positive or inconclusive (the margin is defined for accuracy, not for d).
- **inconclusive** = everything else: no rejection with any CI wider than the margin, completed n < 240, K7, K1.
- Printed sentence when negative: the SAP 9 table's "an improvement larger than 0.05 is excluded", plus "and a loss larger than 0.05 is excluded" when both bounds hold. Never "GATE-M has no effect". The margin 0.05 is the design MDE (SAP 4.3), fixed before outcomes.
- **Rule R3 wording (red-team C2, commit 21067fe7; binding):** under R3 the primary tests the per-item evidence ratio d = mean/sd, not verification accuracy. The printed positive sentence says that GATE-M "increased the evidence ratio d" and says nothing about verification or matching accuracy; the caveat that trimming heavy-tailed tokens can raise d is recorded whenever d is reported; S-M under R3 is uninformative in advance (an accuracy McNemar with too few discordant items) and is marked so in the output; the Y results move to `secondary_y`. The R3 output contains neither "verification" nor "improved" (test-pinned on the whole JSON). The normal route words its label "higher matching accuracy (McNemar on Y)".
- Reachability: the 90 percent half-width is about 1.645 times sqrt(discordance rate / n) (0.030 at 10 percent, 0.043 at 20 percent, n = 300; SAP A2.2, derived), so negative is reachable only when realised discordance is below about 25 percent; above that a null is labelled inconclusive, which is the honest label.
**Expected status of H-G, stated before M0 (red-team C3, N3, N4).** Spec v2 5.1 (Prop. 1') predicts masking helps most for patch and swap and least, possibly not at all, for JPEG and noise; family P is JPEG, noise and splice, while patch and swap are sanity corruptions outside P (section 3). The spec's own confidence that GATE-M beats no gate is 0.35 (spec yaml, SAP yaml). The 21-item dry run (exploratory, no q) has plain-B AUROC 0.543 (JPEG) and 0.515 (noise) against sign-flipped pixel variance 0.756 and 0.774. The red-team's judgement (RED-TEAM-SIGNOFF lines 53-57, not measured) is a probability of about 0.20 of a defensible submission by Fri 30 / Sat 31 Oct, a positive claim for GATE being about 0.05 to 0.08 of that, and roughly even odds that the GPU path fails or is delayed beyond feasibility; the SAP's own scenario map gives power 0.19 to 0.36 at n = 300 (Holm) unless the gate removes about 80 to 90 percent of the corruption noise (SAP 4.5). **The most probable labelled outcome is therefore inconclusive or a null (red-team judgement, N4).** The card is built to report that; the fallback if K1, K2 or K3 occurs, or if the GPU stays on hold, is a decision for ANONYMIZED (D5, D18) and is not made here.

For a null also reported (Tier 2/3, labelled): realised n_d and the sensitivity statement "with this n_d only theta >= theta* would have been detectable" (not an observed power); S-Z result; the Prop. 4 plug-in check (does the independent-token model predict the null?); S-D and S-D2; the calibration check; the headroom table (did corruptions harm verification at all?); the coherence test. A p-value says nothing about novelty or importance (SAP 9).
Fallback if the GPU stays on hold past Thursday noon: spec 11.4 (CPU-only note: unit tests, synthetic CRC study, partial probe-2 AUROCs on 20 complete items labelled exploratory, cheap-baseline fractions, probe-1 reanalysis).

## 13. Not frozen by this card

SHOULD tier S1 (caption typos), S2 (re-infill sampler, not built), S3 (hard negatives, runner not built), S4 (denoise + GATE-M), S5 (K ablations), S6 (contamination read) and COULD (E7 Omni-Diffusion 8B, T2I grid, Mondrian, iterated gate, fp32 head) are outside this card (spec 11.2, 11.3; notes section 4). Running any of them needs an addendum before the first item. They cannot enter family P or any Tier 2 family.
**Manuscript scope (red-team C4, binding from this card).** The MUST tier contains no fusion result and does not exercise network re-masking: the primary endpoint drops terms from a sum computed from a caption-only pass. Title, abstract and highlights therefore make no claim about fusion, marginalisation versus imputation, re-infilling or caption corruption unless an addendum adds those runs (S1, S2, S3) before the first item of the run concerned; otherwise the paper states that they were not tested. Two-way fusion is analysed only if the best single direction is below 0.95 on the clean test items, which on the deranged negatives is unlikely (text direction 0.990 in probe 1); the paper then says fusion is untestable at that ceiling (SAP 7).

## 14. What "frozen" covers (commit and hashes)

| Artifact | Path | Pin |
|---|---|---|
| Code, tests, tools | `exp_p2/`, `tools/`, `tests/exp_p2/` | commit `164a18a551d598c33fa3f51d97cc71ceceff06f4` (`git rev-parse HEAD`, 2026-10-28). Tracked working tree unmodified at the time of writing; untracked: `.codex/agents/*`, `research/paper2/MORNING-2026-10-28.md`, `research/sources/code_*`, `runs/P2-SMOKE-02/` (none part of MUST). Delta from v2's pin `2ab42a6e`: 34 files, +1246/-93, all in `exp_p2/` and `tests/exp_p2/` (rows v3-1 to v3-12) |
| gpu_guard | `tools/gpu_guard.py` (committed blob, `git show HEAD:tools/gpu_guard.py`) | SHA-256 `5ddf7d09f1ea830a6a1049b5958974c342cd37a2817e1063e1dbf797d855aa6d` = `runs/EXP-001/gates/manifest.json` `gpu_guard.sha256` (recomputed). The CRLF checkout of this worktree hashes differently (`dff4b96c...` per the re-audit) without a content change: hash the committed blob |
| Folds | `runs/P2-GATE-FOLDS/folds.json` | SHA-256 `450edb543779de7ee5e6a52422fd6507ef52f15ba3b956a8b05c2e561620f311` (recomputed 2026-10-28 at 164a18a5; unchanged since v1) |
| SAP + Addendum 1 + Addendum 2 | `research/paper2/prereg/SAP-GATE-2026-10-28.md` | **SHA-256 `b4e0bf575dfc2524c0f9d3d5c6b5f52e3185088a94ced8c75f092104ed396c47`** (recomputed at 164a18a5; unchanged since v2). Addendum-1 pin `9c8ad868b6154dfce336a800fb703f4a4b06a476646f67492142a126fd14fec6` (774 lines) kept for history |
| Spec v2 | `research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md` | SHA-256 `04470bef4e5211b442bb276dd4c8f4adc03627688bc559d5c64819f63c933a9b` (unchanged; its parameter "library defaults" for the denoiser is superseded by row v3-9) |
| Implementation notes | `research/paper2/method/GATE-IMPLEMENTATION-NOTES-2026-10-28.md` | SHA-256 `da722737bb6a91dc5504135ecf3a0b397948735032ce843e7c0f14b69e92fc5f` (changed since v2: sections 8-10 added) |
| Code audit (first) | `research/paper2/prereg/GATE-CODE-AUDIT-2026-10-28.md` | SHA-256 `32be9321e0d3f0902942514fa78c7ca121d83222651323decc264c8955efbe9c` |
| Code re-audit | `research/paper2/prereg/GATE-CODE-REAUDIT-2026-10-28.md` | SHA-256 `0f30f635cf9862bdc42c95a53a73983ab9a7cb03918cb60104fbed0bcce4e658` (verdict PASS WITH FIXES at `857673b0`) |
| Red-team sign-off | `research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md` | SHA-256 `e1be2d29b51190669defe1cd915f6081dd730369638f2f359fbd33e62dc702fb` (SIGN WITH CONDITIONS) |
| Denoise check | `runs/P2-GATE-CPU/denoise_check/summary.json` | SHA-256 `f797f9f60be07128d10249b20382ffad1c81edd8b4ec471752c74f8f8fc18fdd` |
| Crash diagnosis | `research/paper2/probes/PROBE2-CRASH-DIAGNOSIS-2026-10-28.md` | SHA-256 `286b91877205b29bbed6fd26d1e9cd53d612a13c9f889d3231ccb156d9936d07` |
| Novelty re-audit | `research/paper2/ideation/NOVELTY-REAUDIT-GATE-2026-10-28.md` | SHA-256 `c4acd02ae65ee8c97906cae53598a97defc1b3b3f477dce3afc028fd42d2f604` |

**Test record (CPU, `CUDA_VISIBLE_DEVICES` empty, `python -m pytest tests/exp_p2 -q`).**
- At `164a18a5`: **202 passed in 10 of 10 runs by the lead** (coordinator's report; not stored in `runs/`). This agent ran the suite once for v3: **202 passed in 65.70 s** (2026-10-28, output not stored).
- Earlier record, for the history: at v1's pin `3ab56647` one full run in four failed (`test_gate_safety.py::test_ac_is_checked_before_the_model_load`); fixed in `66957955` (`slow_factor=1e9`, the slow-item rule tripped on the microsecond timing of the fake items). The gate-auditor ran 194 passed three times at `857673b0` (re-audit claim 1). **One earlier failure appeared once in 14 full-suite runs and did not recur in the following 13; the failing test was not captured and the cause is unreproduced** (notes section 10). It is disclosed, not explained.
- Not covered by any test: every real-GPU path (UniScorer layout, VQ encode, real logits, the watchdog's real kill, the memory-fraction call, `peak_gb`; `runner._cuda` is mocked) and the TbV-score on the real model (the SUBS bypass was verified by reading the UniDisc source, E3, not by running).

**Pre-launch check, to run before each stage** (all four must pass; any failure means the code or a pinned input changed after the freeze: stop and write an amendment, section 17):
```
git diff --quiet 164a18a551d598c33fa3f51d97cc71ceceff06f4 HEAD -- exp_p2 tools tests runs/P2-GATE-FOLDS       :: exit 0
sha256sum runs/P2-GATE-FOLDS/folds.json                          :: 450edb543779de7ee5e6a52422fd6507ef52f15ba3b956a8b05c2e561620f311
sha256sum research/paper2/prereg/SAP-GATE-2026-10-28.md         :: b4e0bf575dfc2524c0f9d3d5c6b5f52e3185088a94ced8c75f092104ed396c47
git show HEAD:tools/gpu_guard.py | sha256sum                    :: 5ddf7d09f1ea830a6a1049b5958974c342cd37a2817e1063e1dbf797d855aa6d
```
Result of this check, run by this agent on 2026-10-28 at HEAD `164a18a5` (this card file was already present as an untracked file; the diff covers only `exp_p2`, `tools`, `tests` and the folds): **PASS on all four.** `git rev-parse HEAD` = `164a18a551d598c33fa3f51d97cc71ceceff06f4`; `git diff --quiet 164a18a5 HEAD -- exp_p2 tools tests runs/P2-GATE-FOLDS` exit 0; folds SHA-256 `450edb54...f311` equal; SAP SHA-256 `b4e0bf57...6c47` equal; gpu_guard committed blob `5ddf7d09...aa6d` equal. Tracked working tree had no modification. The check must be repeated at each stage launch, after this card's own commit (which touches only `research/`, so the diff stays at exit 0).

## 15. Decisions that remain ANONYMIZED's (not made by this card)

| # | Decision | What the sources say | Source |
|---|---|---|---|
| D1 | **Release of the HOLD.** Delete `runs/P2-PROBE-02/HOLD.txt` only after ANONYMIZED says so and the cause is fixed. Every runner and the driver refuse to start while it exists (also `runs/GATE-HOLD.txt`, `runs/<run>/HOLD.txt`). Also his call: NVIDIA driver reinstall if M0 stage 2 crashes | HOLD text; diagnosis decision rule | `runs/P2-PROBE-02/HOLD.txt`; diagnosis section 5 |
| D2 | **Memory cap (re-audit M2).** Runners default `--mem-frac 0.75` (about 9,170 MiB for PyTorch). The diagnosis proposes 0.60 (about 7.2 GiB), below the 8.2 GB first-item peak measured at batch 4. The 0.75 cap did not prevent crash 2. Needs an explicit yes, recorded as a change-log row before M0 (red-team C6) | needs an explicit yes | notes section 2; re-audit M2 |
| D3 | **Guard thresholds and the M10 chunk rule** (all CLI flags; defaults are proposals): whole-GPU 9,000 MiB later items, 10,000 MiB first item, rise 1,500 MiB (now armed after the first item, W1), slow item 2x median, temperature 80 C (code) vs 75 C (diagnosis abort list), busy threshold 2,500 MiB (`driver.py`, `MEM_BUSY_MIB`) vs the diagnosis' "under 700 MiB", **chunk lengths 5 then 15 min vs the diagnosis' "four clean 5-minute chunks before lengthening" (M10, open, unchanged)**. Set `--first-chunk-min` / `--chunk-min` and check `nvidia-smi` by hand, or accept | needs an explicit yes; record the chosen values as a change-log row before M0 | notes N14; re-audit M2, M10 |
| D4 | **Second mask-seed check** (SAP 8.3; still needs the orchestrator's and ANONYMIZED's yes; SAP A2.4 fixes only the order and the seed). If approved, binding order: (1) M3 and the CPU headroom script run and `family.json` is committed (write-once); (2) only then may the check run, in its own run directory (proposed `runs/P2-GATE-SEEDCHK`), writing nothing into `runs/P2-GATE-M3` and not read by `headroom.py`, `analysis_m4.py` or any family-P code; (3) same 50 headroom items (first 50 in fold order), corruptions at their `family.json` operating points, the frozen threshold, second mask-partition seed **20261030** (first seed 20261029, per-item keys unchanged), B only (8 passes per corrupted image), no other new pass type; (4) runs **after M4** unless GPU time is idle, never delays M4, skipped on any crash or abort of the day; (5) output descriptive and exploratory only: share of items with identical Y(GATE-M) under the two seeds, b and c against none with seed 2, Jaccard overlap of the flagged sets, spread of the flagged fraction; no p-value, no change to any rule, rung, family or result wording. Code for it is not built | not in MUST | SAP 8.3, A2.4 |
| D5 | **Deadline date.** The spec's timeline assumes GPU released Wed 28 Oct daytime, results frozen Fri 30 Oct 12:00, submission package Sat 31 / Sun 1; the SAP forbids outcome analysis before the planned fold is complete or "the freeze (spec: Fri 2026-10-30 12:00)". The spec's U9 notes the coordinator wrote "Fri 31 Oct / Sat 1 Nov". If the GPU stays on hold past Thursday noon the honest options are the CPU note or a later deadline | ANONYMIZED's decision | spec 11.5, U9, 11.4; SAP 8.2 |
| D6 | **Test fold 500 (rule R2)** costs about +0.8 GPU-h (spec 9) or about +1 GPU-h (SAP yaml), estimates. SAP concern 1 calls R2 the likely outcome | automatic by rule if D* in [18, 29); the time budget is his | SAP 4.6, 11 |
| D7 | **SHOULD/COULD tier** (section 13) and E7 | not frozen; each needs an addendum | spec 11.2-11.3 |
| D8 | **Unattended or overnight GPU runs**: not planned; the crash protocol assumes ANONYMIZED present | his call | spec 11.5 |
| D9 | **Code audit status.** First audit PASS WITH FIXES (F1-F6, M1-M12 fixed except M2, M10, M1 residual, which are decisions or operator rules); re-audit at `857673b0` PASS WITH FIXES (W1 MAJOR, N1, N4, N5 fixed or recorded in `a2dda400` and this card). **Open: the short delta check of `a2dda400` and `164a18a5` that the re-audit asks for ("any later code commit needs a short delta check") is not on disk.** The audit's cited F7 and F8 have no finding text (F8, R3 routing, is fixed in `a1ac5f01`; row v3-2) | gate-auditor delta check | re-audit last paragraph; audit lines 73, 80 |
| D10 | **Hand-launched M0 stages** have only an informational event-log check; the throttle and nvidia-smi-NA rules are operator-enforced. Accept, or have `gpu_guard.py` extended (a project tool, outside the audited package) | his call | notes section 7 "Not fixed"; audit M1 |
| D11 | **Optional system changes** (admin, driver level): lock the SM clock range with `nvidia-smi -lgc`, WinDbg `!analyze -v` of the two minidumps | not done by any agent | diagnosis section 4 items 3-4 |
| D12 | **Hard-negative audit**: a reviewer-agent pass on headroom and test hard negatives (not automated) and an optional 50-item human spot check; the exploratory S3 depends on it | his time | spec Alg. 11 step 4; notes section 2 |
| D13 | **TbV-score (non-finetuned) baseline** (renamed from "TbV-style"): computed from the raw backbone logits, never the SUBS output; an all-zero result is rejected as a SUBS-style output. `--tbv` on M1 and `--tbv auto` or `on` on M4 follow `tbv_verdict.json`; the choice at M4 is made after M1. The caption-observed variant and the TbV-rule variant at a matched edit budget are not built and need a dated amendment first | automatic, flag choice at M4 after M1 | notes sections 8; spec 4.2 |
| D14 | closed in v3 (real-tokenizer exclusion rule implemented, `f16dda8c`; section 7, row v3-3) | closed | notes section 8 |
| D15 | closed in v3 (R3 routing implemented, `a1ac5f01`; row v3-2) | closed | notes section 8; re-audit section 2 |
| D16 | closed in v3 as code (C1 `gate/c1.py`, chance bar `detect.chance_bar`, `e6e1c902` / `f16dda8c`; rows v3-4, v3-5), read by the gate-auditor and found to match; their behaviour on real data is untested | closed | re-audit section 2 |
| D17 | **JPEG denoiser setting (open, red-team C5 / re-audit N5).** The spec requires ONE denoiser setting for all corruptions. The sigma-matched setting (h = hColor = 25.5) acts on noise 0.10 (PSNR 20.41 to 25.75 dB, +5.34 dB, 95 percent CI 4.15 to 6.49, 71 percent of the noise power removed) but on JPEG q10 it lowers PSNR from 26.82 to 25.13 dB (-1.69 dB) and SSIM from 0.761 to 0.674 (library default +0.22 dB; h = 10 +0.27 dB). No sigma exists to match for JPEG, so a different a-priori setting is not available without a new rule. Options: (a) keep the setting and word S-DN on JPEG as "against an aggressive denoiser that harms the image" (what this card does now); (b) a per-corruption setting by a new dated rule before M4; (c) drop S-DN on JPEG. The setting was chosen after one exploratory evaluation of three candidates on 20 images (disclosed; no later adjustment) | ANONYMIZED's decision, before M4 | `runs/P2-GATE-CPU/denoise_check/summary.json`; notes section 9; re-audit N5 |
| D18 | **Fallback decided now (red-team C3).** What happens if K1 (no operating point), K2, K3 occurs, or the GPU stays on hold or aborts at M0: the CPU-only feasibility note of spec 11.4 (not an Information Fusion research article), a later deadline, or something else. The red-team asks that this be decided before M0, not at Thursday noon. Not decided by this card | ANONYMIZED's decision, before M0 | red-team N3, N10, C3; spec 11.4 |
| D19 | **N3 disclosure and what is allowed to change.** Family P is JPEG, noise and splice, where Prop. 1' predicts the least benefit (patch and swap, where it predicts the most, are outside P); the 21-item dry run points the same way. Any change to the score, K, alpha, folds, rungs, arms, family or rival rule that is made after that 21-item dry run (seen 2026-10-28 before Addendum 1) and is not a new card version must be disclosed in the paper; this card lists those changes as rows v3-1 to v3-12 and Addendum 1-2. A change after the first M2 outcome that is not a new card version is a ground for the red-team to withdraw the signature | accept the disclosure; no change is planned | red-team N3, section 4; SAP A1.2 |

## 16. Sign-off and change log

| Role | Verdict | Date | Notes |
|---|---|---|---|
| experiment-designer | v1, v2, v3 written | 2026-10-28 | this file |
| statistician | **SIGNED OFF WITH CHANGES** (SAP Addendum 2, lines 779-883) | 2026-10-28 | all changes incorporated in v2; condition (ii) "gate-auditor confirms the n-rule code" met for the rule and the `--n` routing (row v2-9) and for R3 routing (re-audit section 2, "Matches") |
| red-team | **SIGN WITH CONDITIONS, confidence 0.6** (`RED-TEAM-SIGNOFF-2026-10-28.md`) | 2026-10-28 | conditions C1-C6 below. Signature does not say the method works. Withdrawal grounds (its section 4): any change to score, K, alpha, folds, rungs or arms after the first M2 outcome that is not a new card version; analysis of M4 data before the planned fold is complete, or a headroom decision that reads a GATE flag; a card sentence attributing a P result to detection without S-M, or any "validation" wording for C1 |
| gate-auditor | **PASS WITH FIXES** at `857673b0` (`GATE-CODE-REAUDIT-2026-10-28.md`) | 2026-10-28 | no blocker; all F1-F6 and M-findings fixed except M2, M10, M1 residual (decisions or operator rules); W1 MAJOR, N1, N4 fixed in `a2dda400`; N5 and W3 handled by this card (row v3-9); delta check of `a2dda400` / `164a18a5` not on disk |

**Red-team conditions (RED-TEAM-SIGNOFF section 3), status at the freeze commit `164a18a5`:**

| Cond. | Requirement | Status | Evidence |
|---|---|---|---|
| C1 | Card pins the final SHA; each post-pin commit logged under the amendment rule; pre-launch check exits 0; gate-auditor's re-audit of those commits on disk | **Met except the delta check.** Pin = `164a18a5`; commits logged as rows v3-1 to v3-12; pre-launch check run and passing (section 14); re-audit on disk covers code through `857673b0`, not `a2dda400` or `164a18a5` (D9) | section 14; re-audit last paragraph |
| C2 | R3 positive sentence says d, not verification; S-M under R3 stated uninformative in advance; variance trimming a competing explanation with plain-B top-k beside the P result | **Met in code and card.** Code: commit `21067fe7`, test-pinned, gate-auditor "Matches" (re-audit section 2). Card: section 12 (R3 wording, expected status), section 1 (competing explanations 6-7). Plain-B top-k exists as a Tier 3 arm; that its counts are printed beside P under R3 is a card rule from the red-team's resolution text, not verified in the analysis output | notes section 9; re-audit section 2 |
| C3 | Card states the expected status of H-G before M0; ANONYMIZED's D5 (fallback and deadline) recorded | **Card statement made** (section 12, "Expected status of H-G"); **ANONYMIZED's decision open** (D5, D18) | section 12; section 15 |
| C4 | Title, abstract and highlights make no fusion, marginalisation-vs-imputation or caption-corruption claim unless an addendum adds those runs | **Rule recorded** (section 13, "Manuscript scope"); enforced at manuscript stage, so open until a manuscript exists | section 13 |
| C5 | Denoise-arm strength check on CPU, or the weaker wording | **Met for noise and for the wording; JPEG open.** `runs/P2-GATE-CPU/denoise_check/` (20 COCO images): noise 0.10 +5.34 dB (library default +0.015 dB, 0.34 percent of the noise power); JPEG q10 -1.69 dB. Wording changed to "sigma-matched non-local-means denoiser" (section 4, row v3-9). The JPEG over-smoothing is an open decision for ANONYMIZED (D17) | notes section 9; re-audit N5 |
| C6 | M0 run exactly as the diagnosis' staged plan, ANONYMIZED present, AC and Id-105 checks, D2/D3 values logged as a change-log row before M0; no hand launch bypassing gpu_guard | **Open** (procedure at M0; section 11b, section 18 commands all go through `tools/gpu_guard.py`; D2, D3 not yet decided; HOLD in place) | section 11b, 18; section 15 |

Version history (rows v1 to v2-9 are copied unchanged from v2 and stay true as history; where a v3 row supersedes one, it says so):

| Version | Date | Change | Reason | Before/after outcome data | Card commit |
|---|---|---|---|---|---|
| v1 | 2026-10-28 | initial card, frozen at code commit 3ab56647 | | before any M1-M5 outcome | 66957955 |
| v2-1 | 2026-10-28 | **SAP pin**: section 14 pins the SAP at `b4e0bf575dfc2524c0f9d3d5c6b5f52e3185088a94ced8c75f092104ed396c47` (after Addendum 2; recomputed here with sha256sum); `9c8ad868...` kept as the Addendum-1 pin | SAP A2.1 item 1; bookkeeping, no test changes | before | to be appended |
| v2-2 | 2026-10-28 | **Real-tokenizer rule**: an item with a runtime caption token count outside 5-32 is excluded from every analysis, counted, not replaced; order unchanged; stop and report if more than 10 percent of any fold fails; no refolding without a new card version. The code does not implement it yet (D14) | SAP A2.1 item 2 | before | to be appended |
| v2-3 | 2026-10-28 | **C1 ruling**: descriptive, no alpha; sentence form fixed; Wilson-CI non-overlap with 0.798-0.880 is an audit trigger only (no rule, score, K, alpha, fold, rung or arm changes; a defect gives an amended rerun); **timing changed**: first look on the clean calibration items right after M2 (before M3/M4), second on the headroom items after M3, third on the test items only at the analysis step after the planned fold is complete; looks are not pooled. v1's "card addition" status removed (now an SAP ruling) | SAP A2.3 | before | to be appended |
| v2-4 | 2026-10-28 | **Outcome reading** (section 12): positive supports only the improvement claim; negative requires no P rejection AND, for every corruption with an operating point, 90 percent CI inside (-0.05, +0.05) AND completed n >= 240 for that corruption; corruptions without an operating point give no evidence for negative; **not available under R3** (only positive or inconclusive); inconclusive = everything else; printed sentence adds the loss bound when both bounds hold; reachability note | SAP A2.2 (replaces v1's looser reading) | before | to be appended |
| v2-5 | 2026-10-28 | **Second-seed check order** (D4): after `family.json` is committed, own run directory, same first 50 headroom items, second mask seed 20261030, B passes only, runs after M4, never delays M4, descriptive only, still subject to ANONYMIZED's and the orchestrator's yes | SAP A2.4 | before | to be appended |
| v2-6 | 2026-10-28 | **Patch/swap positive control** reduced to a chance bar: lower 95 percent bound of the mean per-item AUROC above 0.5 for plain-B and q on M1 items; level descriptive; the dry-run 0.96-0.97 is not a target; failure triggers the C1 audit | SAP A2.5 (replaces v1's "no numeric threshold exists") | before | to be appended |
| v2-7 | 2026-10-28 | **Code freeze commit** moved from `3ab566476ac87c64e482dfc25e7f4ce2b4d5fd2b` to `2ab42a6ee3bc099c9bed2b7286b504fdcc8d4488` (HEAD). Between them the only change in `exp_p2/`, `tools/`, `tests/`, `runs/P2-GATE-FOLDS` is `tests/exp_p2/test_gate_safety.py` (+2/-2, commit 66957955). Folds SHA-256 unchanged (`450edb54...f311`, recomputed) | HEAD advanced by the test fix, the bibliography commit and the SAP addendum | before | to be appended |
| v2-8 | 2026-10-28 | **Flaky AC test fixed** (commit 66957955: `slow_factor=1e9` in `test_ac_is_checked_before_the_model_load`, because the slow-item rule tripped on the microsecond timing of the fake items). Coordinator reports 170 passed in 8 of 8 full runs (not re-run by this agent). v1 concern 2 and the test part of D9 closed | v1 D9 | before | to be appended |
| v2-9 | 2026-10-28 | **Gate-auditor n-rule verification recorded.** `GATE-CODE-AUDIT-2026-10-28.md` criteria table row 1c: "n-rule N*=43, kappa 0.5, D* over passing corruptions, 3x and 5x scaling, R3 : met (rule), partly (R3 routing, see F8)", evidence `headroom.py:74-84`, `stats.py:68-73`; the audit's own text recomputed N* = 43 and the boundaries (0.5 x 3 x 29 = 43.5 >= 43, 0.5 x 3 x 28 = 42 < 43; 0.5 x 5 x 18 = 45, 0.5 x 5 x 17 = 42.5). **F8 was not fixed in the later commits**: the audit file defines findings F1-F6 and M1-M12 only (the text of F7 and F8 does not exist although rows 1c and 2 cite them); the notes' "Code-audit fixes" table (section 7) lists nothing for R3 routing; the code at HEAD still has no R3 branch in the analysis (D15). Only the `--n` check against the rule (audit M3, commit 8704dd2f) was added. SAP A2.6 condition (ii) is met for the rule and its `--n` routing, not for R3 routing | SAP A2.6; coordinator request | before | to be appended |
| v3-1 | 2026-10-28 | **Code pin** moved from `2ab42a6ee3bc099c9bed2b7286b504fdcc8d4488` to `164a18a551d598c33fa3f51d97cc71ceceff06f4`; SAP SHA-256 (`b4e0bf57...6c47`) and folds SHA-256 (`450edb54...f311`) recomputed and unchanged; pre-launch check rewritten (section 14) and passing; gpu_guard committed-blob hash added | red-team C1; re-audit W2 | before | to be appended |
| v3-2 | 2026-10-28 | **R3 routing** (v2 D15, audit "F8"), commit `a1ac5f01`: `family.json` records `primary_endpoint_code` and `negative_reading_available`; under R3 the primary is a Wilcoxon signed-rank on gate minus none of d, labels P1-P3, m = 3 always, p = 1 for a corruption without an operating point, rejection counts only with a positive mean difference; Y moves to `secondary_y`; S-M gatekept by the active primary; `outcome_reading` implements SAP A2.2 (negative never printed under R3 or NO-GO). Tests added in `test_gate_m4_analysis.py`. Gate-auditor ran synthetic cases and found it matches the SAP. Supersedes v2-9's statement that the code had no R3 branch | SAP 4.6, A2.2 | before | to be appended |
| v3-3 | 2026-10-28 | **D14 exclusion rule** implemented, commit `f16dda8c` (section 7). Supersedes v2-2's "code does not implement it yet" | SAP A2.1 item 2 | before | to be appended |
| v3-4 | 2026-10-28 | **C1** implemented (`gate/c1.py`, `stats.wilson_ci`, first committed in `f16dda8c`, wired in `e6e1c902`): Wilson 95 percent CI against 253/300 (reproduces 0.7979 to 0.8801), trigger = non-overlap (a value above the interval also sets `above_interval`, read by the operator; SAP: not alarming by itself), only the A2.3 sentence is produced, looks (i) `python -m exp_p2.gate.c1 --look cal` after M2 and (ii) `--look head` after M3, each recorded once; look (iii) inside `analysis_m4`. Re-audit N1 (fixed in `a2dda400`): `--look test` refuses (exit 2, nothing written) unless the M4 fold is complete (expected n = the n-rule test fold, 300 if absent, minus token exclusions) | SAP A2.3; re-audit N1 | before | to be appended |
| v3-5 | 2026-10-28 | **Chance bar** implemented (`detect.chance_bar` in the `analyze_gate_m1` output, `e6e1c902`): lower 95 percent bootstrap bound of the mean per-item AUROC above 0.5 for plain-B and for q on patch and swap; `passes` is None while q is missing; failure triggers the audit only; level and rival comparison descriptive | SAP A2.5 | before | to be appended |
| v3-6 | 2026-10-28 | **U7 raw-logit TbV path and rename**, commit `8f897235`: our TbV pass was already on the raw backbone logits (`UniScorer.logits_fn` with `return_logits=True`, before UniDisc's `_subs_parameterization`; re-audit read model.py 780-788 and scoring.py:111, E3); renamed `scores.tbv_score_raw_logits` (old name kept as an alias); the label "TbV-score (non-finetuned)" is carried in M1 rows, the verdict file, the analysis labels and the frozen file; an all-zero result is rejected; AST test that no other `forward(` call in `exp_p2` reads the SUBS output. The caption-observed and TbV-rule variants are NOT built (they would need a dated amendment). Replaces the spec's "TbV-style" wording and the v1 premise that U7 might make the baseline inapplicable | Trust but Verify full read (commit 5fb225e9); re-audit | before | to be appended |
| v3-7 | 2026-10-28 | **R3 labels** (red-team C2), commit `21067fe7`: every printed or recorded label says what was tested (R3: "higher per-item mean/sd evidence ratio d"; normal route: "higher matching accuracy, McNemar on Y"); the R3 output contains neither "verification" nor "improved" (test-pinned); `caveats` (d-trimming; S-M uninformative under R3) recorded; S-M under R3 marked `uninformative_under_R3` | red-team N2 | before | to be appended |
| v3-8 | 2026-10-28 | **Red-team sign-off recorded** (`RED-TEAM-SIGNOFF-2026-10-28.md`, SIGN WITH CONDITIONS, 0.6); conditions C1-C6 with status in the table above; new expected-status paragraph (section 12), manuscript-scope rule (section 13), competing explanations 6-7 (section 1) | red-team C2, C3, C4 | before | to be appended |
| v3-9 | 2026-10-28 | **C5 denoiser**, commit `857673b0` (`gate/denoise_check.py`, `imgmetrics.py`, `runs/P2-GATE-CPU/denoise_check/`): spec v2 4.3's "library defaults" is superseded by the sigma-matched setting h = hColor = 25.5 (`config.DENOISE_PARAMS`, windows 7 and 21; rule of thumb from scikit-image's `denoise_nl_means` documentation, not a grid). Measured on 20 COCO images: noise 0.10 PSNR 20.41 to 25.75 dB (+5.34 dB, CI 4.15 to 6.49; library default 20.43, +0.015 dB, 0.34 percent of the noise power removed; h = 10 reported, not chosen, 24.23 dB); **JPEG q10 PSNR 26.82 to 25.13 dB (-1.69 dB), SSIM 0.761 to 0.674**. Disclosure: three candidates evaluated once on these 20 images before the setting was written down; no later adjustment. The JPEG over-smoothing is an open decision for ANONYMIZED (D17); until decided S-DN on JPEG is worded "against an aggressive denoiser that harms the image". Re-audit N5 confirms the numbers from `summary.json` | red-team C5 / N6; re-audit N5, W3 | before | to be appended |
| v3-10 | 2026-10-28 | **Code re-audit recorded**: `GATE-CODE-REAUDIT-2026-10-28.md`, PASS WITH FIXES at `857673b0`, no blocker, suite 194 passed x3 there; all of F1-F6 and M-findings fixed except decisions M2 (D2), M10 (D3) and the M1 residual (D10) | red-team C1 | before | to be appended |
| v3-11 | 2026-10-28 | **Re-audit fixes in `a2dda400`**: W1 (rise rule armed only after the first item; section 11b), N1 (`c1 --look test` refuses on a partial fold; v3-4), N4 (`gate/pins.py`; driver exit 10 on a gpu_guard pin mismatch; `tools/gpu_guard.py` not edited); notes sections 9-10 in `164a18a5`. All with unit tests; none touches a scored analysis path (W1 changes when the guard may stop a run; N1 and N4 change what may start) | re-audit W1, N1, N4 | before | to be appended |
| v3-12 | 2026-10-28 | **Test record**: 202 passed in 10 of 10 lead runs at `164a18a5` (+ one run by the card writer, 65.70 s); one earlier unreproduced failure (1 in 14 runs, test not captured) disclosed in section 14; supersedes v2-8's "8 of 8" | coordinator; notes section 10 | before | to be appended |

## 17. Amendment rule

A change to any frozen item (code at the pinned commit, folds, SAP, operating rules, thresholds D2/D3 once recorded) creates a new card version with a dated change-log row stating the reason and whether it was made before or after outcome data exist. Choosing D2/D3/D4/D5 values is not a change to the science; it is recorded as a log row before M0. A bug fix to code after the pinned commit is allowed only if (i) a unit test pins it, (ii) the fix is committed with its SHA in the log, (iii) it does not touch an analysis path that has already produced a number, and (iv) any outcome already produced under the old code is reported beside the rerun. Reruns are amended runs, never replacements. In v3 the post-v2 code commits (rows v3-2 to v3-11) satisfy conditions (i) and (ii) (unit-tested, SHAs logged) and (iii) (no analysis path had produced a number); condition (iv) is vacuous because no outcome exists.

---

## 18. Exact command sequence M0-M5

All from the worktree root. `PY` = `C:\Users\ANONYMIZED\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe`. Source: notes section 2 (commands were **not executed** by anyone; flags checked to exist by grep). Item-time GPU estimates from spec 11.1 (wall time about 2x at duty 0.5). A stage proceeds only if the previous stage's artifact is committed and its pass criterion holds. Commit SHA of the code for the whole sequence: `164a18a551d598c33fa3f51d97cc71ceceff06f4` (v2: `2ab42a6e`; v1: `3ab56647`; differences in section 16).

**Step 0. Preconditions (no GPU).** Pre-launch check of section 14 (four commands, all must pass); operator preconditions of section 11b; ANONYMIZED's decisions D1-D3 recorded as a change-log row (red-team C6), D17 and D18 answered before M4 / M0 respectively. The driver additionally refuses (exit 10) if `tools/gpu_guard.py` does not match its pin.

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
Right after M2 (CPU, before M3 or M4 is launched): C1 look 1 on the clean calibration items (none-arm accuracy with Wilson 95 percent CI against 0.798-0.880; trigger = non-overlap, action = pipeline audit only) and, from the M1 data, the chance-bar check on patch and swap (section 6). Run `python -m exp_p2.gate.c1 --look cal` for C1 look 1. Items outside 5-32 runtime tokens: rule v2-2, implemented (row v3-3), `FoldDefect` if more than 10 percent of a fold; the report is on disk first.

**M3. Headroom (0.20 GPU-h, 100 items, 2 passes + 7 encodes each).**
```
PY -m exp_p2.gate.gate_driver --stage m3
python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d
```
C1 look 2: `python -m exp_p2.gate.c1 --look head` (clean headroom items, no GATE flag involved). Commit `family.json` (endpoint d, operating points, D_c, D*, rule R1/R2/R3 or NO-GO, T1/T2, n_v) **before the first M4 item**; write-once.

**M4. Main test (1.44 GPU-h at 300 items; about +0.8 to 1 at 500; 75 passes + 6 encodes per item, 70 passes without TbV).**
```
PY -m exp_p2.gate.gate_driver --stage m4 --extra "--tbv auto"      :: add --n 500 when family.json says R2; refuses to start without threshold.json, family.json, detection_frozen.json
python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-M4 --family-run P2-GATE-M3      :: CPU; endpoint d by default; refuses a partial fold unless --allow-partial (logged)
```
(`--extra "--tbv on"` instead of `auto` only if `tbv_verdict.json` allows; the notes list both.) The analysis is run once, after the fold is complete or at the freeze (SAP 8.2). C1 look 3 (clean test items) is part of that analysis. Under rule R3 the code routes the primary to the Wilcoxon on d (row v3-2) and words it as d (row v3-7); the outcome label "negative" is not available under R3. The TbV baseline is the "TbV-score (non-finetuned)" on raw logits (row v3-6).

**M5. Coherence test (0.13 GPU-h, 100 calibration items, 24 passes each + 24 on every fourth item).**
```
PY -m exp_p2.gate.gate_driver --stage m5
python -m exp_p2.gate.coherence_report --run-id P2-GATE-M5 --mu <clean mean per-token paired evidence from M4>
```
Optional, after M4 and only with ANONYMIZED's and the orchestrator's yes (D4): the second mask-seed check, `runs/P2-GATE-SEEDCHK`, seed 20261030, first 50 headroom items; code not built.
Total item time 2.61 GPU-h (estimate; spec 11.1: 0.05 + 0.56 + 0.23 + 0.20 + 1.44 + 0.13), 3.9 with a 50 percent contingency, limit about 6. Per-row time 0.15 s and VQ encode at most 1 s are unmeasured assumptions to be measured in M0.
CPU only, any time: `python -m exp_p2.gate.cpu_dryrun`; unit tests; analysis `selftest()` (runs before the real analysis).

---

## 19. Concerns for the orchestrator

1. "Frozen" is not "ready": the gate-auditor's delta check of `a2dda400` / `164a18a5` is not on disk (D9); red-team C3 (D5 and D18), C4, C5 (D17) and C6 (D2, D3, M0 procedure) are open; the HOLD is in place (D1).
2. The most probable labelled outcome is inconclusive or a null (red-team N4; section 12). If ANONYMIZED wants a different fallback than the CPU note, decide before M0 (D18).
3. The JPEG denoiser setting makes JPEG images worse (-1.69 dB); S-DN on JPEG favours GATE-M until D17 is answered.
4. The cause of the earlier unreproduced test failure (1 in 14 runs) is unknown; the real-GPU paths, including the watchdog kill and the TbV-score on the real model, remain untested by construction.
5. Plain-B top-k counts beside the R3 result are a red-team resolution condition that I did not find verified in the analysis output.
6. No `hypotheses` ledger row and no `research/prereg/<hyp-id>.md` copy were written (brief: write only this file).

## Amendment A1 (2026-10-28 ~09:00 IST, before any M0-M5 GPU outcome)
Code moves from 164a18a5 to **623faaff**. The changes are safety and procedure only; no measurement, scoring or analysis code
changed:
- The gpu_guard pin check (delta audit N4) now needs both the committed blob to match the pin and the CRLF-normalised working
  copy to equal the blob, so an uncommitted edit fails. tools/gpu_guard.py is unchanged.
- Runners, probe wrappers, run_gate_m0 and gate_driver refuse to start (exit 11) when exp_p2/ or tools/ has uncommitted
  changes. `--allow-dirty` overrides and is recorded in the run config.
- The slow-item guard now also needs an absolute floor of 1 s, because it tripped on sub-millisecond test timings; this explains
  the earlier unreproduced test failure. Real items take about 7-10 s. This is a guard-threshold change and belongs to decision
  D3 for ANONYMIZED.
Tests: 209 passed, twice, at 623faaff (lab engineer). The lead's pre-launch check must now pin 623faaff. A gate-auditor delta
check of 164a18a5..623faaff is still to do before M0.
