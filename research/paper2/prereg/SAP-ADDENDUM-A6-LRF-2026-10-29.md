```yaml
agent: statistician
date: 2026-10-29
brief: >
  DRAFT SAP addendum A6 for Paper 2 (retargeted to IEEE TNNLS, D0081): a confirmatory preregistration of learned
  reliability-aware evidence fusion (LRF, D0082) on a fresh COCO val2017 fold, written before any new data. Not committed;
  the lead commits after review; binding only under the conditions of A6.0.
sources_examined:
  - research/CONTRACT.md
  - research/ledgers/decisions.jsonl rows D0081, D0082
  - research/paper2/posthoc/LEARNED-CEILING-REPORT-2026-10-29.md (full); runs/P2-POSTHOC-LEARNED/ (file list only; numbers quoted from the report)
  - analysis_posthoc/learned_ceiling/data.py (feature construction, lines 1-110)
  - exp_p2/run_gate_m4.py 108-165 (conditions, stored arrays); exp_p2/run_gate_suite.py (grep: stored arrays); exp_p2/gate/suite.py 1-134
  - imagecorruptions at commit c959e659 in the project venv: get_corruption_names('common'/'all') (run 2026-10-29 14:19 IST)
  - Hugging Face model API for openai/clip-vit-large-patch14, google/siglip-so400m-patch14-384 (curl, 2026-10-29)
  - SAP-GATE-2026-10-28.md, SAP-ADDENDUM-A4, SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md r1, RED-TEAM-SIGNOFF "A5 signature" (as read for A5)
coverage: >
  NOT available: research/paper2/posthoc/LRF-FROZEN-2026-10-29.md and runs/P2-LRF-FROZEN/ do not exist at 14:20 IST (checked); every
  property of the frozen model below is a requirement on that file, not a fact about it. Not read: S2, FOIL, suite, H, Tier-3 or M5 output
  files; the learned-ceiling plan; the TNNLS design and Codex files. No GPU used.
claims:
  - statement: "No held-out imagecorruptions type can be scored by LRF without new code: the suite runner stores codes, z, delta, flag and u only, while LRF needs B, D, s3, tbv, tex and nbr per token."
    status: supported
    evidence: "exp_p2/run_gate_suite.py:107-121; analysis_posthoc/learned_ceiling/data.py:61-85; exp_p2/run_gate_m4.py:144-161"
    level: E3
    confidence: 0.9
  - statement: "At n = 520, pi_d 0.238, the exact one-sided McNemar at alpha 0.05 has power 0.73 for a net gain of 0.05 and 0.86 for 0.06; 630 items would be needed for 0.8 at 0.05."
    status: supported
    evidence: "Appendix A6 (derived; script and output hashes there)"
    level: E4
    confidence: 0.9
  - statement: "The imagecorruptions build installed in the venv offers gaussian, shot, impulse and speckle noise among 19 types."
    status: supported
    evidence: "venv run 2026-10-29 14:19 IST; installed commit c959e659c9713837d2acd7ce785a81202d4be799"
    level: E4
    confidence: 0.95
competing_explanations:
  - "The exploratory noise0.1 gain may be a property of the scores under that one corruption on the M4 images, or partly of the caption-length layout the features inherit from c+ (report, competing explanations); A6.7 tests the second."
unknowns:
  - the frozen model's hash, decision rule and any feature-level length fix (LRF-FROZEN, pending)
  - the discordance rate of LRF versus NONE on fresh images; the per-item time of the reduced M4 stage
  - whether S2 or FOIL outcomes had been seen by anyone who chose LRF's frozen configuration (the lead's statement is required, A6.1)
next_test: {hypothesis: "L1: frozen LRF beats NONE on noise0.1 on a fresh fold", intervention: "reduced M4 stage on 520 fresh images, frozen LRF scored on CPU", primary_metric: "accuracy Y, exact one-sided McNemar", falsifier: "one-sided p > 0.05 or b <= c", gpu_hours: "about 4.2 wall-h (L1) + up to 2.25 (LG), estimates"}
```

# SAP Addendum A6 (DRAFT, 2026-10-29): preregistered confirmation of learned reliability-aware evidence fusion (LRF) on a fresh fold

> **DRAFT for the lead's review.** Not committed, not signed, not binding. Nothing below may be acted on (no fold built, no code merged, no
> GPU stage) until the conditions of A6.0 are met.

Author: statistician. Written 2026-10-29 from 14:20 IST. Precedence if adopted: A6 > A5 > A4 > ... > SAP body, only on the points listed here.
Family P, PS, the GATE secondaries, S2, B, E-dec, E-pred, the suite, family H (A5 r1) and every earlier rule stand unchanged, except for the
A5.1 stop rule, which A6 cannot override by itself (A6.0 item 1).

## A6.0 Binding conditions (all before the first L item; none is met now)

1. **Conflict with A5 (must be resolved first).** A5 r1 (C5-3) says: "H is the **last confirmatory family** added to Paper 2 after the P outcome.
   Any later post-P analysis has no alpha and no family". A6 adds confirmatory families after P. A6 is therefore **not admissible as written**
   unless a dated amendment of A5.1, signed by the red team, allows exactly one further preregistered study: a new method (LRF) on fresh data (A6.3),
   followed by no further confirmatory family. A5 also says its rules may only be tightened after the first H3 item, so **this amendment must be signed
   before the first H3 item**. If H3 starts first, or the red team refuses, A6's tests are reported as Tier 3 (CIs only, no alpha), and the
   paper may not call LRF "confirmed".
2. **The frozen object exists and is pinned** (A6.2): `runs/P2-LRF-FROZEN/` and `research/paper2/posthoc/LRF-FROZEN-2026-10-29.md` committed; a
   dated row in this file copies their SHA-256 values, the decision rule and any feature-level length fix. Until then A6 is a plan without an object.
3. Red-team signature on A6 (proposer is not validator); Shlok's go-ahead for the GPU stages (attended or unattended, in his words, as for H).
4. Code of A6.11 audited PASS by the gate-auditor; the merge follows A5's C5-8 discipline (after S2 has ended; committed P, Tier-3, E-dec and E-pred
   outputs regenerated byte-identically); a dated card v4 pin row.
5. The fold file, its manifest and its leak check (A6.3) committed with the data-steward's L7 sign-off.
6. The lead's dated statement on what was seen before the frozen configuration was chosen, including whether any S2, FOIL or H output had been read (A6.1).

## A6.1 Provenance (honest; binding wording in A6.12)

**LRF was designed after the primary result.** Before the LRF configuration was chosen, the following had been computed and committed and were
seen by the people who chose it (the lead and the senior-ML subagent; I cannot attest to what each read):
- family P, label **negative** (`runs/P2-GATE-M4/analysis.json`, 1028fb9a): P1 JPEG b 0, c 1; P2 noise b 0, c 0; P3 splice b 1, c 3; all Holm p 1.0;
- the GATE secondaries in the same file (S-M, S-Z, S-DN, S-D2, S-C), the mechanism arms, the calibration check, the clean-accuracy look;
- family PS "not met" and the A2.3 audit with its post hoc section 4 (few decisions changed by token-level corruptions);
- E-dec and E-pred (cd0174ac); the Tier-3 comparators of A4 Part 1 (758a11e7); M5 coherence (a451a92d);
- the learned-ceiling plan (d457d295) and its results (bdc87e4e): on the **same 500 M4 items**, the cross-fitted logistic-GAM (F1, chosen as SEL in
  5 of 5 folds) reached 0.778 against NONE 0.676 on noise0.1 (+0.102, 95% CI +0.060 to +0.144; b 85, c 34), +0.032 (+0.002 to +0.062) on jpeg10, 0.000
  on splice128, +0.004 on clean; the oracle arms; F2-F4; the detector AUROCs;
- the TNNLS design notes and their external review (SCER, CANAL; commits e2510e79, 3556df15), which I did not read.
- Unknown to me: whether any S2, FOIL or H output was seen (A6.0 item 6).

Consequences, all binding:
1. **The M4 items are LRF's training data.** Every LRF number on them, cross-fitted or not, is exploratory and is reported as such ("post hoc,
   exploratory", report section 5). The only confirmatory evidence for LRF is the fresh fold of A6.3.
2. **AB.1 still applies to P.** No sentence anywhere says or implies that GATE's null was caused by, explained by, or would have been avoided with
   LRF ("the gate failed because masked-likelihood detection targets changed codes", "hard gating discards useful evidence", "LRF fixes GATE"). The
   P null is reported as preregistered, with its A4.2 NEG sentences, whatever A6 shows.
3. LRF is a **new method** tested in its own preregistered study ("Study 2"), not a reanalysis or a rescue of P.

## A6.2 The tested object (frozen; one object; no retraining)

- The **only** object tested is the model in `runs/P2-LRF-FROZEN/`, identified by the SHA-256 of (a) the fitted parameter file, (b) the feature code
  (`analysis_posthoc/learned_ceiling/data.py` or its frozen copy, blob hash), (c) the scoring code, (d) the decision rule. A6.11's scorer refuses to
  run if any hash differs.
- **Decision rule** (the form the report describes; the frozen report's exact definition binds and is copied here by the A6.0 item 2 row): per-token
  non-negative weights w_j from caption-withheld features; Y_LRF = 1[sum_j w_j Delta_j > 0]; ties and an all-zero weight vector count as wrong.
- **No retraining, recalibration, threshold change, feature change, ensembling or model selection after the first L item exists.** No item of the
  fresh fold is used to fit anything. A defect found after the first L item is handled as in card v3 section 17 (rerun beside the original, both
  reported), never by refitting.
- LRF has **no conformal guarantee**; no sentence attributes GATE's CRC false-alarm statement to LRF.

## A6.3 Fresh fold (builder, exclusions, size)

**Builder (new code, A6.11):** `python -m exp_p2.gate.build_lrf_fold` writes `runs/P2-LRF-FOLD/folds_lrf.json` (folds schema: `test` = the ordered
list; `cal`, `head`, `test_ext` empty), `manifest.json` and `leak_check.json`; refuses to overwrite.
- **Universe:** COCO val2017 images in the local `val2017.zip` with instance annotations.
- **Excluded images:** `folds.json` cal, head, test, test_ext; probe-1 and probe-2 `selection.json`; M1 and M5 items; the FOIL pool (`runs/P2-GATE-FOIL/pool.json`,
  fit and test); **every image in the SugarCrepe release** (the seven pinned JSONs, 1,560 images; this covers the H pool whether or not the H fold
  file exists yet; a mild selection, stated). Built in the main worktree so that M1/M5 files are read.
- **Positive caption c+:** one caption per image, chosen uniformly (seeded) among its captions with 5 to 32 tokens (`folds.hf_token_counter`); images
  with none are excluded and counted.
- **Primary negative c-:** the M4 rule, reusing the `folds.py` derangement function unchanged with the L list as one block (a caption of another
  item whose image shares no annotated COCO category; fallback as in `folds.py`).
- **Length-matched negative c-_L (A6.7):** among the c+ captions of other items whose images share no annotated category, uniformly (seeded) one with
  **the same token count as c+**; if none exists, one with the smallest absolute difference (recorded per item).
- **Order and ids:** seeded permutation; `idx` 0 to 519; `gid` = 8000 + idx (folds 0-2499, FOIL 4000+, H 6000/7000; the builder asserts no collision).
  Seed `[config.SEED_GATE, 10]` (folds use 7 and 8, H uses 9; the auditor confirms 10 is unused).
- **Leak check L0-L8** as AB.6: disjointness from every excluded set; **L6 positive control** (count of universe images that match an excluded set
  must be > 0); **L7** five matched ids checked by the data-steward; **L8** injected-leak self-test.

**Size n_L = 520 (decision, derived in Appendix A6).**
- Exploratory effect on noise0.1: +0.102 with discordance pi_d = 119/500 = 0.238 (theta 0.714).
- **Winner's-curse shrinkage:** the planning effect is **Delta_plan = 0.05**, half the exploratory point estimate (the usual replication heuristic),
  and below its lower 95% bound (0.060). Reasons for shrinking: noise0.1 was the best of three corruptions, the configuration was chosen after seeing
  cross-fitted results on the same items, and the fresh fold is a new image sample. The discordance rate is kept at 0.238 (less exposed to selection;
  sensitivity below).
- Required n for power 0.8 at Delta_plan (exact one-sided McNemar, alpha 0.05): **630**; budget cap: 4 h at 27 s per item = **533**. n_L = 520 (3.9 h at
  27 s), leaving about 0.1 h of the cap for the extra negative pass.
- Power at n = 520 (one-sided alpha 0.05 / 0.025): Delta 0.04: 0.56 / 0.43; **0.05: 0.73 / 0.62**; 0.06: 0.86 / 0.78; 0.08: 0.98 / 0.96; 0.102: 1.00 / 1.00.
  Sensitivity to pi_d at Delta 0.05 / 0.06: 0.15: 0.89 / 0.97; 0.20: 0.80 / 0.91; 0.30: 0.64 / 0.78.
- **Honest summary:** n_L = 520 detects the exploratory effect almost surely, but has about a one-in-four chance of missing an effect half its size.
  A non-confirmation is therefore not evidence of no effect (A6.12).

## A6.4 Endpoints, hypotheses, tests (Study 2, family L)

Per item and condition: Y_arm = 1[decision correct] for arms NONE (all 1,024 tokens), GATE-M (unflagged tokens, M2 threshold at alpha 0.05, unchanged)
and LRF (A6.2). Conditions are those of the M4 stage at the P operating points: clean, jpeg10, noise0.1, splice128. Estimand: paired accuracy
difference on the fresh-fold population (random COCO val2017 images outside every project set, the M4 negative rule), one model (UniDisc 1.4B),
one corruption realisation per image, one mask seed.

**Family L (FWER 0.05, fixed sequence, then Holm):**
1. **L1 (primary):** LRF versus NONE on noise0.1. H0: Pr(Y_LRF = 1) <= Pr(Y_NONE = 1). **Exact one-sided McNemar at alpha 0.05**, confirmed iff
   one-sided p <= 0.05 with b > c.
2. **L2 (key secondary, tested only if L1 is confirmed):** LRF versus GATE-M on noise0.1, exact one-sided McNemar at alpha 0.05.
3. **L3, L4 (tested only if L2 is rejected):** LRF versus NONE on jpeg10 (L3) and splice128 (L4), exact **two-sided** McNemar, Holm over m = 2 at 0.05
   (two-sided so that a harm can be declared).
Fixed-sequence testing controls the FWER over L1 to L4 at 0.05; a hypothesis not reached is "not tested (gatekept)" and is reported descriptively.

**Why one-sided for L1 and L2 (decision).** The direction was fixed by the exploratory result before any fresh item exists, and a harm on noise0.1
would not support any claim the paper could make, so the confirmatory question is one-directional. The price: the false-positive rate is that of a
two-sided 0.10 test. Mitigation, binding: every L1/L2 report states "one-sided, preregistered" and also whether one-sided p <= 0.025 ("would also pass a
two-sided 0.05 test"); a harm on noise0.1 is visible in the two-sided 95% CI printed beside it.

**Separate family L-NI (clean no-harm; m = 1; tested regardless of L1).** H0: Delta_clean <= -0.03 against H1: Delta_clean > -0.03 (LRF minus NONE on
clean images). Non-inferiority is shown iff the lower bound of the two-sided 90% paired percentile bootstrap CI (10,000 resamples) exceeds -0.03
(one-sided alpha 0.05; the same machinery as A2.2). **Margin 0.03, fixed now:** at most three accuracy points lost on clean images, about half the
planning gain on noise. Power at a true difference of 0 (normal approximation, clean discordance 0.096 from the exploratory run): 0.71 (margin 0.02:
0.43; 0.04: 0.90). Failing to show non-inferiority reads "a clean-image loss of up to three points is not excluded", not "LRF harms clean images".

**Reported with every test:** b, c, n_d, n, both accuracies, net difference with paired percentile bootstrap CIs at 90 and 95%, Clopper-Pearson CI of
b/n_d, exact p (one- and two-sided), mid-p as sensitivity.

**Missing items and peeking:** SAP 8.1 and 8.2 apply (complete case, committed order, prefix on interruption, no replacement, no analysis before the
planned fold is complete or the run deadline). If the completed n is below 416 (80% of 520), L1 is still computed, labelled "partial prefix (n of 520)";
a rejection stands, a non-rejection reads "inconclusive (partial)", not "not confirmed".

## A6.5 Generalisation family LG (held-out noise types; decided now: Holm-tested)

- **Availability (checked):** the installed imagecorruptions (commit c959e659) offers gaussian_noise, shot_noise, impulse_noise and speckle_noise among
  19 types. **None can be scored by LRF without new code:** the suite runner stores codes, z, delta, flag and u only, while LRF needs B, D, s3, tbv,
  tex and nbr (claim 1). A6.11 item 4 specifies the minimal addition; if it is not audited in time, LG is "not run".
- **Cells (fixed now, by kind, not by outcome):** shot_noise, impulse_noise, speckle_noise, each at **severity 3** of the package's 1-5 scale (the
  middle level; no data on any of them exists for LRF). gaussian_noise is excluded because LRF was fitted on Gaussian noise (not held out). No cell is
  dropped or replaced for its result; a type absent at run time is dropped and counted.
- **Items:** the first **300** items of the L fold (prefix; same images as L1).
- **Test:** LRF versus NONE per cell, exact **one-sided** McNemar (direction as L1), **Holm over m = 3 at 0.05**; own family, not gatekept by L1 (a
  failure of L1 does not stop LG from being reported). Completed n < 240: descriptive only. Power (derived; one-sided 0.05/3 at the first Holm step,
  n = 300): pi_d 0.20: net gain 0.06 -> 0.54, 0.08 -> 0.82, 0.10 -> 0.96; pi_d 0.10: 0.06 -> 0.87.
- Also printed (descriptive): GATE-M versus NONE per cell; the clean-to-corrupted drop of NONE per cell.

## A6.6 Industry baselines CLIP and SigLIP (descriptive only; no test against LRF)

- **Models (ids and revisions verified on the Hugging Face API, 2026-10-29):** `openai/clip-vit-large-patch14` at revision
  `32bd64288804d66eefd0ccbe215aa642df71cc41`; `google/siglip-so400m-patch14-384` at revision `9fdffc58afc957d1a03a25b10dba0329ab15c2a3` (Apache-2.0).
  Neither is cached locally; download sizes were not checked (the lead confirms before download). Loaded through `transformers` with the model's
  own processor, pinned revisions, fp32 on CPU or fp16 on GPU (recorded).
- **Items and images:** the same 520 items, conditions clean, jpeg10, noise0.1, splice128 (and the LG cells if LG ran). The corrupted images are
  **regenerated** with the M4 stage's own functions and seeds (`corruptions.apply_pixel` with `rung_rng(gid, corr, rung)`, `donor_for` on the L fold;
  `suite.apply_corruption` with its item-derived seed for LG) on the 512-px image UniDisc sees, then passed to each model's processor.
  **Pixel-parity positive control:** on 5 items, re-encode the regenerated images with UniDisc's VQ and compare with the stored codes; agreement of at
  least 0.98 per image is required (encoder non-determinism up to about 1.5%, card row A-5); otherwise the baselines are labelled "pixel parity not shown".
- **Decision:** Y = 1[s(image, c+) > s(image, c-)], s = the model's image-text score (CLIP: cosine of normalised embeddings; SigLIP: the pairwise logit,
  monotone in the cosine, so the same decision); ties wrong.
- **Reported (descriptive, no p-value):** accuracy per model and condition, the clean-to-corrupted drop with a paired bootstrap CI, beside the drops of
  UniDisc NONE and LRF. **No test of LRF against CLIP or SigLIP** (decision): they are different models with different training data and a different
  decision statistic, so a test would compare systems, not methods. Wording: "for reference, ...", never "LRF is more robust than CLIP".
  Contamination: whether these models saw COCO is not known; stated.
- Run on CPU or between GPU stages, **never during a GPU stage** (CPU load stopped M2 twice through the slow-item guard).

## A6.7 Caption-length control

- **Concern** (report, competing explanation 2): the caption-withheld features (B, D) carry the token-length layout of c+, so the weights can depend on
  the true caption's length, which together with the negative's length is information about which caption is true.
- **Control 1 (binding as part of the frozen object):** any feature-level fix specified in LRF-FROZEN (A6.0 item 2 row) is part of the object tested.
- **Control 2 (design; family L-LEN, m = 1):** every L item also carries the length-matched negative c-_L (A6.3). With c+ and c-_L of equal length, the
  length of c+ carries no information about which caption is true. The runner computes Lambda for c-_L (one extra pass per item; Delta for c-_L is a gather
  at the stored codes, no extra pass) and stores Delta_L for every condition; the frozen weights are unchanged (they never see a negative).
  **Test:** LRF versus NONE on noise0.1 with c-_L, exact one-sided McNemar at alpha 0.05 (own family, not gatekept). Items whose closest c-_L differs in
  length are excluded from this test and counted.
- **Wording gate:** if L1 is confirmed, the claim says "including with length-matched negatives" only if L-LEN is rejected with b > c. Otherwise it adds
  "the gain was not shown with length-matched negatives (b, c, CI), so a caption-length channel is not excluded". If the code for c-_L is not audited in
  time, L-LEN is "not run" and the clause "a caption-length channel was not tested on fresh data" is mandatory.

## A6.8 Multiplicity map (adds to AD.11 and A5.13)

| Family | Contrast | m | Alpha | Test | Status |
|---|---|---|---|---|---|
| L | L1 noise0.1 LRF vs NONE -> L2 LRF vs GATE-M -> Holm{L3 jpeg10, L4 splice128} | 4, fixed sequence | 0.05 | exact McNemar (L1, L2 one-sided; L3, L4 two-sided) | Study 2, primary |
| L-NI | clean, LRF vs NONE, margin 0.03 | 1 | 0.05 one-sided | bootstrap CI bound | Study 2 |
| L-LEN | noise0.1 with length-matched negatives | 1 | 0.05 one-sided | exact McNemar | Study 2, control |
| LG | shot, impulse, speckle noise (severity 3) | 3 | 0.05 one-sided | exact McNemar, Holm | Study 2, generalisation |

Study 2 has four families, each at its own 0.05; the headline of Study 2 comes only from L1. With A5's 13, the paper has 17 test families; under a
global null with independence (they are not independent) the chance of at least one family-level rejection is 0.58 (derived, 1 - 0.95^17). Printed
with "no multiplicity adjustment across families" and the family of every claim.

## A6.9 Analysis (CPU; recomputed from predictions files)

- `exp_p2/gate/lrf_score.py` (A6.11) writes `runs/P2-LRF-L1/predictions.jsonl` (per item and condition: idx, gid, image_id, condition, Y and margin for
  NONE, GATE-M and LRF, and for c-_L) and `runs/P2-LRF-LG/predictions.jsonl`. It recomputes Y_NONE and Y_GATE-M from the arrays and asserts equality with
  the runner's rows (positive control).
- `analysis/paper2/lrf/a6_analysis.py` reads only the predictions files and writes `runs/P2-LRF-L1/a6_analysis.json` (and LG, L-LEN, L-NI blocks):
  seeds `numpy.random.SeedSequence(20261028, spawn_key=(34,))` (33 is h_strata's; the auditor confirms), 10,000 resamples, percentile intervals;
  reruns byte-identical. Self-test: exact McNemar size on simulated nulls, the fixed-sequence logic, the L-NI bound on synthetic data.
- Order: L1 complete -> `lrf_score` -> `a6_analysis` -> commit at once; LG after its run; baselines last. No analysis output is read before its run is complete.

## A6.10 Run order, time rule, cut order

**Run deadline F2 = Mon 2 Nov 2026 18:00 IST** (fixed; a moved deadline never enters). Constants (estimates): W_L1 = 4.2 h (520 x 27 s plus 0.25 h
null-cache lengths and the extra negative pass), W_LG = 2.25 h (300 x 27 s; an upper bound, the stage has fewer conditions), W_BASE = 1.5 h (CPU), A = 0.5 h
analysis and commit per stage, margin M = 2.0 h (as A4.3.2).
1. **L1 starts** iff t_now + W_L1 + A + M <= F2, i.e. no later than **Mon 2 Nov 11:18 IST**; else L1 is "not run" and LRF is unconfirmed.
2. **LG starts** after L1, iff t_now + W_LG + A + M <= F2, i.e. no later than **Mon 2 Nov 13:15 IST**.
3. **Baselines** run after the GPU stages (or between them with the GPU idle), iff t_now + W_BASE + A + 1.0 <= F2 (by Mon 15:00 IST).
4. **Cut order (first cut first):** LG, baselines, the suite, H4, H3 (A5), then L1. S2 has priority over all and is expected to have ended; FOIL has run.
5. **Recommended run order (earliest deadline first; outcome-blind):** S2 -> H3/H4 (A5's start bound is Fri 30 Oct 12:27 IST) -> L1 -> LG -> baselines
   -> suite. The order is the lead's; it may depend only on time, readiness of audited code and the pre-written criteria (AB.9), never on any outcome.
6. GPU stages run under the card's guards and memory flags, the parallel sessions told first; unattended only with Shlok's words (A6.0 item 3). A guard
   stop or crash halts everything until Shlok returns; on relaunch the rules above are re-evaluated with the new t_now; a started stage continues its
   committed list and is cut at F2 as a prefix.

## A6.11 Code (specification; the lead's engineer implements; audited before any L item)

1. `exp_p2/gate/build_lrf_fold.py` and tests (A6.3; determinism, exclusions incl. SugarCrepe and FOIL, L6 to L8, gid range, length-matching statistics).
2. The A5 code (`--folds-path`, `--family-run`) is reused. A plan family file `runs/P2-LRF-PLAN/family.json` (P's three operating points, endpoint "d",
   `n_rule.test_fold` 520) makes `run_gate_m4`'s n check pass. L1 runs `run_gate_m4 --folds-path runs/P2-LRF-FOLD/folds_lrf.json --family-run P2-LRF-PLAN
   --n 520 --sanity "" --denoise-for "" --tbv auto` (no patch, swap or denoised copies; the auditor confirms `--sanity ""` is accepted and that tbv arrays
   are written, since LRF needs them).
3. **New runner option** `--neg-len`: reads the item field `neg_caption_len`, computes its Lambda (one pass) and stores `{cond}_deltaL`; default off;
   P's path unchanged (test).
4. **LG stage:** a minimal option of `run_gate_m4` (e.g. `--extra-cells shot_noise3,impulse_noise3,speckle_noise3`) that adds imagecorruptions cells as
   pixel conditions through `suite.apply_corruption` with the suite's item-derived seed, storing exactly the arrays of a pixel condition (codes, z,
   delta, B, D, s3, tex, nbr, tbv, flags). **Parity test:** on two items, the arrays of a condition produced through this path equal those of the
   ordinary path for the same pixel image.
5. `exp_p2/gate/lrf_score.py` (hash checks of A6.2; features by the frozen feature code; refuses on any mismatch) and `analysis/paper2/lrf/a6_analysis.py`.
6. `analysis/paper2/lrf/baselines.py` (A6.6; pinned revisions; pixel-parity check).
7. Order: branch -> tests -> gate-auditor PASS (including the byte-identical regeneration of committed P outputs, as C5-8) -> merge after S2 ->
   pin row -> fold build and commit -> plan file commit -> L1.

## A6.12 Outcome wording (fixed now; every result, including a null)

Scope sentence `{S}`: "in one pretrained unified masked diffusion model (UniDisc, 1.4B parameters), on {n} COCO val2017 images not used to design or
fit the method, at one severity per corruption".

| Result | Sentence |
|---|---|
| **L1 confirmed** | "On a fresh preregistered fold, the frozen LRF raised image-direction verification accuracy under Gaussian noise (sigma 0.1) from {A0} to {A1} (net {D}, 95% CI {L} to {U}; exact one-sided McNemar p = {p}, preregistered one-sided alpha 0.05{; it would also pass a two-sided 0.05 test})." + L-LEN clause (A6.7) + L-NI sentence + {S}. |
| **L1 not confirmed** | "The frozen LRF did not confirm on the fresh preregistered fold: net {D} (95% CI {L} to {U}), one-sided p = {p}. The exploratory gain on the design items (+0.102) is therefore not confirmed." L2-L4 are "not tested (gatekept)" and shown descriptively. **No rescue:** no refit, no other model, no subgroup, no other corruption or LG cell promoted to the headline, no "trend", no "underpowered so supportive". The title may not claim that LRF improves anything. |
| L1 partial (n < 416) | rejection: as "confirmed" with "partial prefix (n of 520)"; non-rejection: "inconclusive (partial prefix)". |
| L2 rejected | "LRF also exceeded the masked-likelihood gate (GATE-M) on noise0.1 ({D}, CI)." Not rejected: "LRF was not shown to exceed GATE-M on noise0.1." |
| L3/L4 | per corruption: rejected with b > c: "LRF also raised accuracy under {X} ({D}, CI)"; with c > b: "LRF reduced accuracy under {X} ({D}, CI)"; not rejected: "no difference was detected under {X} ({D}, CI)". |
| L-NI shown / not shown | "On clean images LRF lost no more than three points (90% CI {L90} to {U90})." / "A clean-image loss of up to three points is not excluded (90% CI {L90} to {U90})." |
| LG | per cell, with the Holm-adjusted p: "under {type} (held out, severity 3) LRF raised accuracy ({D}, CI)" / "no difference was detected" / "LRF reduced accuracy". Never "LRF generalises to unseen noise" unless all three cells are rejected with b > c; with one or two, "under {types}" only. |
| Baselines | "For reference, CLIP ViT-L/14 and SigLIP so400m lost {x} and {y} accuracy points under noise0.1 on the same images, against {z} for UniDisc without a gate and {w} with LRF (descriptive; different models and training data)." |

**Must-not (adds to A4.2.2 item 3 and A5.9).**
1. Any link between LRF and the P null (A6.1 item 2), in any section, caption, cover letter, README or repository text.
2. "Confirmed", "validated" or "generalises" for anything that did not pass its own preregistered test; M4-item numbers called anything but "post hoc, exploratory".
3. A guarantee or "calibrated" for LRF (it has no conformal guarantee).
4. "Robust" for LRF beyond the corruptions and severities whose tests were rejected with b > c; "state of the art"; "first".
5. Any test or ranking claim of LRF against CLIP or SigLIP.
6. Pooling noise0.1 with other corruptions or LG cells; pooling the fresh fold with the M4 items.

**Placement:** the P result keeps its preregistered sentence in the abstract and Results under every A6 outcome. A title or abstract sentence about
LRF follows the table above; under "L1 not confirmed" the title is a question or names the study without a gain claim. Family H keeps A5.9's
placement rule (never in title, abstract, highlights or conclusion) unchanged.

## A6.13 Assumptions and concerns (statistician)

1. **A5 stop-rule conflict** (A6.0 item 1) is the first thing to resolve; A6 is not admissible without the amendment, and the amendment is only possible
   before the first H3 item.
2. The shrunk planning effect (0.05) is a heuristic; the true fresh-fold effect could be smaller (the training items were the ones on which the method was
   chosen) or the discordance rate different. At n = 520 the power is 0.73 at 0.05 and 0.86 at 0.06; a null is likely to be inconclusive rather than negative.
3. One-sided alpha 0.05 for L1 and L2 is a deliberate trade for power; reviewers may prefer 0.025 (power 0.62 at 0.05). The report gives both.
4. LRF's features include tbv, texture and neighbour distance; any change in those code paths after the freeze changes the object (hash checks).
5. The fresh fold excludes all SugarCrepe images, a mild non-random restriction of val2017.
6. The frozen report does not exist yet; A6 cannot be signed until its hashes and decision rule are copied in.
7. GPU stability (eight crashes on record) and the shared GPU make the time rule the most likely cause of "not run".
8. A p-value says nothing about novelty or practical importance; a confirmed L1 shows that one frozen weighting raised accuracy under one corruption in one model.

## A6.14 Amendment log row (for the lead)

| Date | Change | Reason | Before/after outcome data? |
|---|---|---|---|
| 2026-10-29 | Addendum A6 (DRAFT): Study 2, confirmatory test of frozen LRF on a fresh fold (n 520); families L (fixed sequence), L-NI (margin 0.03), L-LEN, LG (Holm 3); CLIP and SigLIP descriptive; time rule against Mon 2 Nov 18:00 IST; outcome wording; requires an A5 stop-rule amendment before the first H3 item | D0081, D0082 | **after** P, PS, GATE secondaries, E-dec, E-pred, Tier-3, M5 and the learned-ceiling results on the M4 items; **before** any fresh-fold item, before the frozen model is committed |

---

## Appendix A6. Power arithmetic (CPU, stdlib only)

Script `a6_power.py` (SHA-256 `18c79d8ba7f76f6f9899449c693041e78ee756433b26ae8db5943a38d7f6b0ae`), output `a6_power_output.txt` (SHA-256
`1f6035099b680eb6ad322a1d6cdef91fb587189f25b4966f02bdfc6ae97b8477`) and the LG addendum `a6_power_lg.txt`, in the session scratchpad
`C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\`;
the lead copies them to `runs/P2-LRF-A6/` and checks the hashes. Method: n_d ~ Bin(n, pi_d), b | n_d ~ Bin(n_d, theta), theta = 0.5 + Delta / (2 pi_d);
rejection iff the exact one-sided p = P(Bin(n_d, 0.5) >= b) <= alpha.

```
exploratory: pi_d 0.238, theta 0.714, Delta 0.102; budget 4 h at 27 s -> 533 items
n 500: D .04 0.54/0.41 | .05 0.71/0.60 | .06 0.85/0.76 | .08 0.98/0.95 | .102 1.00/1.00   (one-sided alpha .05/.025)
n 520: D .04 0.56/0.43 | .05 0.73/0.62 | .06 0.86/0.78 | .08 0.98/0.96 | .102 1.00/1.00
n 600: D .04 0.61/0.49 | .05 0.79/0.68 | .06 0.90/0.84
pi_d sensitivity, n 520, D .05/.06: 0.15 0.89/0.97 | 0.20 0.80/0.91 | 0.238 0.73/0.86 | 0.30 0.64/0.78
smallest n with power 0.8 at D 0.05: alpha .05 -> 630; alpha .025 -> 780
clean NI (normal approx., pi_d 0.096, true 0, n 520, se 0.0136): margin .02 0.43 | .03 0.71 | .04 0.90 | .05 0.98
LG n 300, one-sided 0.05/3: pi_d .10: D .04 0.46, .06 0.87 | pi_d .20: .04 0.24, .06 0.54, .08 0.82, .10 0.96 | pi_d .30: .06 0.37, .08 0.62, .10 0.83
1 - 0.95^17 = 0.582 (hand arithmetic, same formula as A5.13)
```
