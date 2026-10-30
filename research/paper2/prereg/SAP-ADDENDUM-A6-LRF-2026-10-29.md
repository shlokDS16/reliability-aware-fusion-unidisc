```yaml
agent: statistician
date: 2026-10-29
brief: >
  SAP addendum A6 r1 for Paper 2 (IEEE TNNLS, D0081): Study 2, a confirmatory preregistration of learned reliability-aware
  evidence fusion (LRF, D0082) re-frozen at a fixed caption-slot length L_FIX = 13 (D0083), on a fresh COCO val2017 fold.
  r1 answers the red-team signature "A5.1 amendment and A6 signature" (C6-1 to C6-11). Not committed; the lead commits.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md section "A5.1 amendment and A6 signature" (commit 0ea9cf33), full
  - research/ledgers/decisions.jsonl rows D0081, D0082, D0083 (commit 5ff2c0d7)
  - research/paper2/posthoc/LRF-FROZEN-2026-10-29.md (bf2edd7c), full; runs/P2-LRF-FROZEN/spec.json (hash fields)
  - research/paper2/posthoc/LEARNED-CEILING-REPORT-2026-10-29.md, full
  - analysis_posthoc/learned_ceiling/data.py 1-110; exp_p2/run_gate_m4.py 108-165; exp_p2/run_gate_suite.py (grep); exp_p2/gate/suite.py 1-134
  - this file's draft (71c78306); SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md r1
  - sha256sum of runs/P2-GATE-M1/codebook.npy, runs/P2-GATE-DCACHE/DI_n013.npy, runs/P2-LRF-FROZEN/model.npz and the three
    analysis_posthoc/learned_ceiling/*.py files (2026-10-29, after 14:35 IST)
coverage: >
  Not read: diagnostics.json, hpo.json, freeze_check.json contents (numbers quoted from the frozen report only); the TNNLS design notes
  (SCER, CANAL) and their audit; any S2, FOIL, suite or H output. No re-scored or re-frozen output exists (D0083). No GPU used.
claims:
  - statement: "Under L_FIX the LRF features need only one D-cache file (DI_n013.npy) and the M1 codebook; both are untracked in git; their SHA-256 values are recorded here as the expected inputs."
    status: supported
    evidence: "LRF-FROZEN section 3 item 1; git ls-files (empty, red team); sha256sum run 2026-10-29"
    level: E4
    confidence: 0.9
  - statement: "With the exploratory planning values (pi_d 0.238, Delta_plan 0.05) the n-rule of A6.3 gives n_L = 533 (cap), power 0.74 at one-sided 0.05 and 0.63 at 0.025."
    status: supported
    evidence: "Appendix A6 (derived)"
    level: E4
    confidence: 0.9
competing_explanations:
  - "A positive L1 could still reflect a Gaussian-noise detector built into nbr and tbv rather than a general reliability weighting (red team (3) ii); A6 does not test this and its wording does not claim generality."
unknowns:
  - the re-frozen object (hash, out-of-sample behaviour); the cross-fitted effect at L_FIX; the discordance on fresh images
  - LRF novelty (no audit exists, red team K14)
next_test: {hypothesis: "L1: re-frozen LRF beats NONE on noise0.1 on the fresh fold", intervention: "re-score M4 at L_FIX, re-freeze, then the reduced M4 stage at L_FIX on n_L fresh images", primary_metric: "accuracy Y, exact one-sided McNemar", falsifier: "one-sided p > 0.05 or b <= c", gpu_hours: "re-score about 2.5 wall-h, L1 about 4.3, LG up to 2.25 (estimates)"}
```

# SAP Addendum A6 r1 (2026-10-29): Study 2, preregistered confirmation of learned reliability-aware evidence fusion (LRF)

Author: statistician. Draft written 2026-10-29 from 14:20 IST (commit 71c78306). Revision r1 written from about 14:50 IST, after D0083 (14:35:18)
and before any re-scored, re-frozen, H or fresh-fold output exists. Precedence: A6 > A5 > A4 > ... > SAP body, only on the points listed. The
A5.1 stop rule is amended once by "A5.1 amendment 1" (A5 r2), which admits Study 2 and nothing else.

## Revision r2 (2026-10-29; clarification only; gate-auditor S-1 in `GATE-CODE-AUDIT-A6-LRF-2026-10-29.md`; before any L item, no L data exists)

| Date | Point | Ruling |
|---|---|---|
| 2026-10-29 | Branch of a **partial prefix** that rejects L1 with one-sided p <= 0.025 (A6.4 "rejection stands" vs A6.12, which listed only "partial and not rejected" under C) | **Branch B**, the stricter reading, as `a6_analysis.py` `branch_of` already implements. "Partial prefix" is A6.4's definition: completed n < 0.8 n_L. Such a result is "confirmed at the preregistered one-sided 0.05 level" with "partial prefix (n of n_L)", in Results only, with no title, abstract or highlight gain claim, whatever its p. Reason: the headline threshold of C6-5 was set for the planned fold; a fold cut short by the clock is a deviation from the plan, so it may not carry the headline. A completed n >= 0.8 n_L is not a partial prefix and follows A6.12 unchanged (it prints "n of n_L"). Holm m = 2 over L3 and L4 after L1 is as A6.4 states (family L has m = 3 in total); unchanged. Nothing else in A6 changes. |

## Revision r1 (red-team signature "A5.1 amendment and A6 signature", C6-1 to C6-11; D0083)

| Condition | Change in r1 | Where |
|---|---|---|
| C6-1 (K1, K2) | One object: the LRF re-frozen on M4 items re-scored at L_FIX = 13 (option (a), D0083, declared 14:35:18 before any re-frozen accuracy). Model ca5c4e2f is retired and never scored on fresh items. Re-freeze procedure, invariance gate and clock rule; no fallback to option (b) | A6.2, A6.10 |
| C6-2 (K3) | Hash set extended to `codebook.npy`, `DI_n013.npy` and the scoring entry point (expected values recorded); any non-finite feature, weight or margin is an error that stops the scorer, never a "wrong" decision | A6.2 |
| C6-3, K4 | L2 (LRF vs GATE-M) **removed**: it restated L1 (GATE-M = NONE on noise0.1 in M4). Family L is now L1 -> Holm{L3, L4} (m = 3, a tightening). GATE-M on the fresh fold is supplement-only, descriptive; no sentence compares LRF with GATE-M | A6.4, A6.12 |
| C6-4 (K5) | Study 1 is not LRF's motivation in any text; no problem/solution arrangement of sections, figures or tables; no LRF number beside GATE-M results; chronology once, in Methods | A6.1, A6.12 |
| C6-5 (K6) | Title, abstract or highlight gain claim needs one-sided p <= 0.025; 0.025 < p <= 0.05 is "confirmed at the preregistered one-sided 0.05 level" in Results only; L1 in the abstract brings L-NI into the abstract | A6.4, A6.12 |
| C6-6 (K7) | No rescue: after an L1 non-confirmation L3, L4, L-LEN, LG and L-NI appear only in Results beside the non-confirmation; branch titles fixed now; route and venue fixed before the first L item | A6.12 |
| C6-7 (K8) | Disclosure names every candidate considered (F1-F4, SEL, SCER, CANAL, Routes A and B) | A6.1, A6.13 |
| C6-8 (K9) | The re-frozen object has no out-of-sample estimate; in-sample and `freeze_check.json` numbers are never quoted as performance; the L_FIX cross-fit is exploratory, supplement only | A6.2, A6.3 |
| C6-9 | Commit order: A6 r1 and A5 r2 before the first H3 item; object, A6.0 item 6 statement and hashes before the fold build; fold build before the first L item | A6.0 |
| C6-10 (K12) | Fold exclusions are the union of image ids in every `runs/P2-*` items, selection and pool file at build time, plus all SugarCrepe images | A6.3 |
| C6-11 (K10, K11) | LG worded "other noise types (shot, impulse, speckle; imagecorruptions severity 3)"; L-NI states its margin was fixed after the M4 clean interval was seen | A6.4, A6.5, A6.12 |
| fresh-fold n | n_L set by a pre-written rule from the cross-fitted effect of the L_FIX protocol (shrunk by half), clamped to [400, 533]; 520 if the cross-fit is not committed in time | A6.3 |
| run order | S2 -> H3 -> H4 -> re-score M4 at L_FIX -> re-freeze (+ cross-fit) -> L1 -> LG -> baselines -> suite | A6.10 |

## A6.0 Binding conditions and commit order (C6-9; git order is the evidence)

1. **Before the first H3 item:** A6 r1 (this file) and A5 r2 ("A5.1 amendment 1") committed; the red-team conditions C6-1 to C6-11 recorded as dated
   ledger rows (the lead's). If an H3 item exists before both commits, the amendment is void and every Study 2 test is Tier 3 (CIs only; LRF never
   "confirmed"). After the first H3 item, A6 may only be tightened.
2. **Before the fold build:** the re-frozen object committed with its full hash set (A6.2), the invariance check and the re-score positive control
   passed, and the lead's dated statement of what was seen before LRF's configuration was chosen (including whether any S2, FOIL or H output was read).
3. **Before the first L item:** the fold, its manifest and leak check committed with the data-steward's L7 sign-off; the n-rule record (A6.3) committed;
   the code of A6.11 audited PASS and merged after S2 under A5's C5-8 discipline (byte-identical regeneration of the committed P, Tier-3, E-dec and E-pred
   outputs) with a dated card pin row; route and venue fixed by a dated row (C6-6); ANONYMIZED's GPU go-ahead in his words (attended or unattended).
4. If any of these is missing at the clock bounds of A6.10, Study 2 is "not run" and appears only in the deviations box.

## A6.1 Provenance (internal record; the public text is A6.13)

LRF was designed after Study 1's primary result. Before its configuration was chosen, the following had been computed, committed and seen by the
people who chose it (the lead and the senior-ML subagent; I cannot attest to what each read): family P (label negative; P1 b 0, c 1; P2 b 0, c 0;
P3 b 1, c 3; Holm p 1.0), the GATE secondaries, mechanism, calibration and clean-accuracy records; PS "not met" and the A2.3 audit; E-dec and E-pred;
the A4 Tier-3 comparators; M5 coherence; the learned-ceiling plan and results on the same 500 M4 items (four families F1-F4 compared, SEL chose F1
in 5 of 5 folds; noise0.1 +0.102, CI +0.060 to +0.144); the first freeze (ca5c4e2f) and its caption-length test. Also considered and not pursued:
two other method designs (SCER, CANAL; novelty audit `research/paper2/tnnls/NOVELTY-AUDIT-SCER-CANAL-2026-10-29.md`) and Routes A and B (D0082).
Unknown to me: whether any S2, FOIL or H output was seen (A6.0 item 2).

Binding consequences:
1. The M4 items are LRF's design and training data. Every LRF number on them (cross-fitted, in-sample or re-frozen) is "post hoc, exploratory",
   appears only in the supplement's exploratory section, and never beside GATE-M results (C6-4).
2. **AB.1 extends to Study 2 word for word.** No sentence, section order, figure or table presents Study 1 as the motivation of LRF or LRF as the
   answer to Study 1 ("hard gating discards useful evidence", "LRF fixes the gate", "the gate failed because it targets changed codes"). The superseded
   phrases "GATE study as motivation/analysis" (CONFIRM section 16, D0082) are not used in any paper text (C6-4; the lead's dated row). Study 1 keeps
   its A4.2 NEG sentences under every Study 2 outcome.
3. LRF's motivation in the paper is stated on its own terms (reliability-weighted combination of per-token evidence), with no reference to Study 1's result.

## A6.2 The tested object: LRF at L_FIX = 13 (one object; frozen; no retraining)

**Object (C6-1 option (a), D0083).** The logistic-GAM LRF re-frozen with the **unchanged** protocol of LRF-FROZEN section 1 (same feature list and
order, knots, HPO search, seed keys, objective, refit on all 500 M4 items x 4 conditions) on M4 arrays whose caption-withheld scores are re-scored at a
fixed caption-slot length: B and s3 (`scores.image_B`), D (the D cache) and tbv (`scores.tbv_score_raw_logits`) computed on `sc.build([PAD] * 13, codes)`,
D from `DI_n013.npy`. Lambda and Delta are unchanged (caption visible at its own length). tex and nbr do not depend on the layout and are reused.
Model `ca5c4e2f...` is retired as an exploratory object and is **never scored on fresh items**.

**Re-freeze procedure (fixed now; outcome-blind):**
1. **Re-score (GPU):** a new entry point outside the pinned `exp_p2/` while S2 runs (or a dated pin row after S2) reads each M4 item's **stored codes**
   for clean, jpeg10, noise0.1 and splice128 (no image re-encoding) and writes `runs/P2-LRF-RESCORE/arrays/itemNNNN.npz` with `{cond}_B`, `_s3`, `_D`,
   `_tbv` at L_FIX, other fields copied unchanged.
2. **Positive control (before step 3):** on 5 items x 4 conditions, the same entry point run at each item's **true** caption length reproduces the
   stored M4 B, s3, D and tbv (max abs diff at most 1e-5; tolerance set now for GPU arithmetic). Failure: audit, fix, rerun; nothing is fitted.
3. **Invariance check:** on 5 items x 4 conditions, B, D, s3 and tbv at L_FIX are identical when the sequence is built from the c+ tokens, the c- tokens
   or PAD (max abs diff 0, deterministic cuDNN as card row A-5). If exact equality fails only by arithmetic non-determinism, the gate-auditor may
   accept max abs diff at most 1e-6 by a dated row **before any re-frozen output exists**; any larger difference stops Study 2.
4. **Re-freeze:** `lrf.py --freeze` unchanged, on the re-scored arrays, output `runs/P2-LRF-FROZEN-LFIX/` (model, spec, hpo). **No accuracy of the
   re-frozen model is computed or opened before its hash set is committed**; any M4 accuracy computed afterwards is exploratory and never quoted as
   performance (C6-8). The re-frozen object has **no out-of-sample estimate**.
5. **Cross-fit at L_FIX (for the n-rule only, A6.3):** the learned-ceiling cross-fit protocol (same 5 outer and 3 inner folds, seeds and HPO), family F1
   only, on the re-scored arrays; output `runs/P2-LRF-CF-LFIX/results.json`. Its numbers are exploratory, supplement only, and **cannot stop, delay or
   change Study 2** except through the n-rule.

**Hash set (C6-2), verified by the scorer at start in the checkout that runs:**

| Item | Expected SHA-256 (raw bytes) |
|---|---|
| re-frozen `model.npz` (and `spec.json`) | to be written by the A6.0 item 2 row |
| `analysis_posthoc/learned_ceiling/data.py` | `14421ffb1061947a8408406750e8417282188efeccf07cac3142179fed9f429b` (as frozen; any change is a new object) |
| `analysis_posthoc/learned_ceiling/families.py` | `1c49827d723ea17017f84ba283fcfa681bf24e10c0a0e7d62b6a83064f850a7e` |
| `analysis_posthoc/learned_ceiling/lrf.py` | `03ed472e1a3cd8bb2dc41f4a59d7b48f1561cd883012ac4434e08a5c37b9d6ec` (or the re-freeze version, recorded in the row) |
| `runs/P2-GATE-M1/codebook.npy` (nbr; untracked) | `ff15b9b5b362dc80f8a18f6e852e6e99478c0e8885646735ed16d1d80e3ae50b` |
| `runs/P2-GATE-DCACHE/DI_n013.npy` (D at L_FIX; untracked) | `f7744253a1b997b8b9f28d9b91348e8371f1ea1e3564f6c8bfc2f10aa5b42176` |
| the L_FIX scoring entry points (re-score and fresh-fold runner option) and `lrf_score.py` | recorded in the pin row |

The GPU runner records the codebook and `DI_n013.npy` hashes in each run's `config.json`; the scorer compares them with this table.

**Decision rule:** Y_LRF = 1[sum_j w_j Delta_j > 0], w_j >= 0 the frozen weights (`lrf.infer_item`); ties wrong. **Non-finite rule (C6-2):** any
non-finite feature, weight, score or margin raises an error and stops the scorer; it is never counted as a wrong decision. The cause is fixed as a
pipeline defect (card v3 section 17: rerun beside the original, both reported); nothing is refitted. The gate-auditor tests this path (missing
codebook, missing `DI_n013.npy`, an injected NaN).

**After the first L item:** no retraining, recalibration, feature or threshold change, ensembling or re-freeze, for any reason.

## A6.3 Fresh fold and n

**Builder** `python -m exp_p2.gate.build_lrf_fold` (new code) writes `runs/P2-LRF-FOLD/folds_lrf.json` (folds schema, `test` = an ordered list of
**533** items), `manifest.json` and `leak_check.json`; refuses to overwrite; run in the main worktree after the object commit (A6.0 item 2).
- **Exclusions (C6-10):** the **union** of image ids in every `runs/P2-*/items.jsonl`, every `selection.json` and every pool file present at build time
  (including `folds.json` cal, head, test, test_ext, probe-1 and probe-2, M1, M5, S2, FOIL, the suite and its smoke, H if present), plus **all images in
  the SugarCrepe release** (seven pinned JSONs, 1,560 images). The manifest lists every file read and its count; the data-steward's L7 record states the union.
- c+ (one seeded caption per image, 5-32 tokens), primary negative c- (the `folds.py` derangement rule, the list as one block), length-matched negative
  c-_L (seeded, same token count as c+, else the smallest difference, recorded), seeded order, `idx` 0-532, `gid` 8000 + idx, seed `[SEED_GATE, 10]`,
  leak check L0-L8 (L6 positive control, L7 steward check, L8 injected leak): as in the draft.

**n-rule (fixed now; clock-bounded).** n_L is a **prefix** of the 533-list, so the choice cannot select items.
- Inputs: the cross-fitted noise0.1 result of the L_FIX protocol (A6.2 step 5): Delta_cf (SEL minus NONE) and pi_cf = (b + c) / 500.
- Delta_plan = Delta_cf / 2 (winner's-curse shrinkage by half, as in the draft). If Delta_cf <= 0.02, n_L = 533.
- Otherwise n_req = the smallest n on a step-10 grid with exact one-sided McNemar power >= 0.8 at alpha 0.05 for (pi_cf, Delta_plan); **n_L = min(533,
  max(400, n_req))**. 533 is the budget cap (4 h at 27 s per item); 400 keeps the LG prefix (300) and L-NI meaningful.
- If `runs/P2-LRF-CF-LFIX/results.json` is not committed by **Mon 2 Nov 10:00 IST**, n_L = 520 (the draft's value).
- The rule's output (inputs, n_req, n_L, power at one-sided 0.05 and 0.025) is committed before the first L item. With the draft's exploratory values
  (pi_d 0.238, Delta 0.102) the rule gives n_L = 533: power 0.74 at Delta 0.05 (0.63 at 0.025), 0.87 at 0.06 (0.79) (Appendix A6).

## A6.4 Endpoints, families, tests

Arms on the fresh fold: NONE (all 1,024 tokens) and LRF (A6.2), image direction, conditions clean, jpeg10, noise0.1, splice128 at the P operating
points; all caption-withheld scores at L_FIX. Estimand: paired accuracy difference on random COCO val2017 images outside every project set, M4
negative rule, one model, one corruption realisation per image, one mask seed. The GATE-M arm is computed by the runner (at L_FIX, with the M2
threshold, which was calibrated at the true-caption layout) and is **supplement-only, descriptive, without a guarantee**.

**Family L (FWER 0.05; fixed sequence then Holm; m = 3):**
1. **L1 (primary):** LRF vs NONE on noise0.1, exact **one-sided** McNemar at alpha 0.05, "confirmed" iff one-sided p <= 0.05 and b > c.
2. **L3, L4 (tested only if L1 is confirmed):** LRF vs NONE on jpeg10 and splice128, exact two-sided McNemar, Holm m = 2 at 0.05.
(L2 of the draft is removed, C6-3/K4.)

**Headline threshold (C6-5).** A gain claim in the title, abstract or highlights requires L1 one-sided **p <= 0.025** (equivalent to two-sided 0.05).
With 0.025 < p <= 0.05 the result is "confirmed at the preregistered one-sided 0.05 level" in Results only. Reason, printed: Study 2 is the paper's
second headline attempt after Study 1's null; two headlines at one-sided 0.05 give about 0.0975 chance of a false positive under a global null (red team, derived).

**L-NI (m = 1; tested regardless of L1):** clean images, H0 Delta_clean <= -0.03; non-inferior iff the lower bound of the two-sided 90% paired bootstrap
CI exceeds -0.03. **The margin was fixed after the M4 clean interval (-0.024 to +0.030) and the in-sample clean accuracy had been seen** (C6-11; stated
with the result). Power at a true difference of 0: 0.71 (derived).

**L-LEN (m = 1):** LRF vs NONE on noise0.1 with c-_L, exact one-sided McNemar at 0.05; items whose c-_L differs in length excluded and counted. Under
L_FIX the length channel is closed by construction; L-LEN checks robustness to a different negative-length distribution. Wording gate: a confirmed L1
carries "including with length-matched negatives" only if L-LEN is rejected with b > c; otherwise "the gain was not shown with length-matched negatives
(b, c, CI)". Also reported (descriptive; frozen report step 5): the L1 gain by length stratum (true caption shorter, equal, longer) and the
longer-minus-shorter difference with a 95% CI.

**LG (Holm m = 3; one-sided 0.05; own family):** see A6.5.

**Reported with every test:** b, c, n_d, n, both accuracies, net difference with 90 and 95% paired percentile bootstrap CIs, Clopper-Pearson CI of
b/n_d, exact one- and two-sided p, mid-p. Missing items: SAP 8.1/8.2; completed n < 0.8 n_L: rejection stands with "partial prefix (n of n_L)",
non-rejection is "inconclusive (partial)".

## A6.5 Family LG: other noise types

- Cells (fixed by kind): shot_noise, impulse_noise, speckle_noise at imagecorruptions **severity 3** (installed commit c959e659), on the first 300 items
  of the fold, caption-withheld scores at L_FIX. Worded **"other noise types (shot, impulse, speckle; imagecorruptions severity 3)"**, never "held-out
  noise family" (C6-11): shot and speckle noise are close relatives of Gaussian noise, impulse noise is the structurally different cell, and severity 3
  is not matched to sigma 0.1.
- LRF vs NONE per cell, exact one-sided McNemar, Holm m = 3 at 0.05; completed n < 240 descriptive. "Generalises" is never used; with fewer than three
  rejections the sentence names the rejected types only.
- Needs new code (the suite runner does not store LRF features): A6.11 item 4. Not audited in time: LG "not run".

## A6.6 Industry baselines (descriptive; no test; own table)

`openai/clip-vit-large-patch14` at revision `32bd64288804d66eefd0ccbe215aa642df71cc41` and `google/siglip-so400m-patch14-384` at revision
`9fdffc58afc957d1a03a25b10dba0329ab15c2a3` (Hugging Face API, 2026-10-29; sizes to be confirmed by the lead before download). Same n_L items; images
regenerated with the runner's functions and seeds; pixel-parity positive control (5 items re-encoded by UniDisc's VQ, agreement >= 0.98, else no
baseline number in the main text). Decision 1[s(image, c+) > s(image, c-)], ties wrong. Reported in **their own table**: accuracy per model and
condition, including clean, with paired bootstrap CIs for each model's own clean-to-corrupted drop. No test against LRF, no ranking words, no column
of LRF numbers inside that table; never run during a GPU stage.

## A6.7 Multiplicity

| Family | Hypotheses | m | Alpha | Test |
|---|---|---|---|---|
| L | L1 noise0.1 -> Holm{L3 jpeg10, L4 splice128} | 3 | 0.05 | exact McNemar (L1 one-sided; L3, L4 two-sided) |
| L-NI | clean, margin 0.03 | 1 | 0.05 one-sided | bootstrap bound |
| L-LEN | noise0.1, length-matched negatives | 1 | 0.05 one-sided | exact McNemar |
| LG | shot, impulse, speckle (severity 3) | 3 | 0.05 one-sided | exact McNemar, Holm |

Family count of the paper: 17 (P, the GATE secondaries, PS, S2, B, R, H, H-M, L, L-NI, L-LEN, LG as in AD.11, A5.13 and amendment item 4); 1 - 0.95^17
= 0.58 under a global null with independence, printed with "no adjustment across families". Removing L2 reduces the hypotheses in L from 4 to 3
(a tightening of amendment item 4); the family count is unchanged.

## A6.8 Analysis (CPU; from predictions files)

`lrf_score.py` (hash checks, non-finite rule) writes `runs/P2-LRF-L1/predictions.jsonl` and `runs/P2-LRF-LG/predictions.jsonl`; it recomputes Y_NONE
from the arrays and asserts equality with the runner's rows. `analysis/paper2/lrf/a6_analysis.py` reads only predictions files; seeds
`SeedSequence(20261028, spawn_key=(34,))`; 10,000 resamples; byte-identical reruns. No output is read before its run is complete.

## A6.9 (removed in r1; the draft's caption-length section is now part of A6.2 and A6.4)

## A6.10 Run order, clock rules, cut order

**Order (amendment item 5 with D0083's preparation stages):** S2 -> H3 -> H4 -> **re-score M4 at L_FIX (GPU) -> invariance check and positive control
-> re-freeze -> object commit -> cross-fit (CPU, GPU idle) -> fold build -> n-rule commit** -> L1 -> LG -> baselines -> suite. Order, starts and cuts
depend only on time and audited-code readiness (AB.9); no stage is started, delayed, cut, repeated or extended because of another stage's outcome; a
missed H bound is final.

**Clock rules (all IST; F2 = Mon 2 Nov 2026 18:00, fixed).** Constants (estimates): W_RS = 2.5 h (500 items x 4 conditions x 9 passes), W_CHK = 0.25 h,
W_RF = 0.25 h (241 s measured for the first freeze), A = 0.5 h per commit step, W_CF = 1.5 h, W_L1 = 4.3 h (533 x 27 s plus cache and the extra
negative pass), W_LG = 2.25 h, W_BASE = 1.5 h, margin M = 2.0 h before F2 (1.0 h before an intermediate bound).
1. **Re-score starts** iff t_now + W_RS + W_CHK + W_RF + A + 1.0 <= T_RF, with **T_RF = Mon 2 Nov 09:00 IST**, i.e. by Mon 04:15.
2. **The re-frozen object commit must exist by T_RF (Mon 09:00).** Otherwise Study 2 is "not run": there is **no fallback** to model ca5c4e2f or to
   option (b) (D0083 retired it).
3. **Cross-fit** committed by Mon 10:00, else n_L = 520 (A6.3).
4. **L1 starts** iff t_now + W_L1 + A + M <= F2, i.e. by **Mon 11:12**; else Study 2 is "not run".
5. **LG starts** after L1 by **Mon 13:15**; **baselines** by **Mon 15:00** (no GPU stage running).
6. **Cut order (first cut first):** LG, baselines, suite, H4, H3 (A5), L1. S2 has priority and is expected to end Thu.

## A6.11 Code (specification; audited before use)

1. Re-score entry point and its positive-control and invariance tests (A6.2 steps 1-3).
2. `build_lrf_fold.py` (533-list, union exclusions, L0-L8) and the n-rule script (A6.3).
3. Fresh-fold runner: `run_gate_m4` with `--folds-path`, `--family-run P2-LRF-PLAN` (test_fold = n_L), `--sanity ""`, `--denoise-for ""`, `--tbv auto`,
   plus two new options: `--layout-fix 13` (B, s3, D, tbv at L_FIX; Lambda unchanged; default off, P path unchanged by test) and `--neg-len` (Lambda for
   c-_L, `{cond}_deltaL`).
4. LG option (imagecorruptions cells as pixel conditions with the LRF arrays; parity test against the ordinary path).
5. `lrf_score.py` (hash set of A6.2; non-finite rule; tests for missing codebook, missing `DI_n013.npy`, injected NaN), `a6_analysis.py`, `baselines.py`.
6. Branch -> tests -> gate-auditor PASS (with the C5-8 byte-identical regeneration) -> merge after S2 -> pin row.

## A6.12 Outcome wording, branch titles and placement (fixed now)

Scope `{S}`: "in one pretrained unified masked diffusion model (UniDisc, 1.4B parameters), on {n} COCO val2017 images not used to design or fit the
method, with Gaussian noise at one severity".

**Branch titles (C6-6), chosen mechanically from L1:**

| Branch | Condition | Title |
|---|---|---|
| A | L1 confirmed with one-sided p <= 0.025 | "Learned reliability-aware fusion of token evidence raised image-text verification accuracy under Gaussian noise in a unified masked diffusion model: a preregistered confirmation in UniDisc" |
| B | L1 confirmed with 0.025 < p <= 0.05 | "Reliability-aware fusion of token evidence for image-text verification in a unified masked diffusion model: two preregistered studies in UniDisc" |
| C | L1 not confirmed, or partial and not rejected | "Does learned reliability weighting help image-text verification under image corruption? Two preregistered studies in a unified masked diffusion model (UniDisc)" |
| D | Study 2 not run | A4.2.3's question title for Study 1 (QT) |

No title names gating, GATE or Study 1's result, and none uses "robust", "generalises", "first" or "state of the art".

**Sentences (Results; abstract only as allowed below):**
- **L1 confirmed:** "On a fresh preregistered fold, the frozen LRF raised image-direction verification accuracy under Gaussian noise (sigma 0.1)
  from {A0} to {A1} without reliability weighting ... (net {D}, 95% CI {L} to {U}; exact one-sided McNemar p = {p}; preregistered one-sided alpha 0.05)."
  Branch B adds "confirmed at the preregistered one-sided 0.05 level; it would not pass a two-sided 0.05 test". Plus the L-LEN clause, the L-NI
  sentence and {S}.
- **L1 not confirmed:** "The frozen LRF did not confirm on the fresh preregistered fold: net {D} (95% CI {L} to {U}), one-sided p = {p}. The exploratory
  gain on the design items is therefore not confirmed." L3 and L4 "not tested (gatekept)". **No rescue (C6-6):** L-LEN, LG and L-NI appear only in
  Results, in the same paragraph as this sentence, never in the title, abstract, highlights, conclusion or cover letter; no refit, other model, subgroup,
  corruption, LG cell or route switch is offered as a substitute; no "trend", no "underpowered so supportive".
- **L3/L4** (per corruption): raised / reduced (harm sentence mandatory wherever the L1 gain appears) / no difference detected, each with its CI.
- **L-NI:** "On clean images LRF lost no more than three points (90% CI {L90} to {U90}); the margin was fixed after an exploratory clean interval had
  been seen." / "A clean-image loss of up to three points is not excluded (90% CI ...)."
- **LG:** per cell, with Holm-adjusted p, using the C6-11 wording.
- **Baselines:** "For reference, CLIP ViT-L/14 and SigLIP so400m, different models trained on different data, reached ... (own table)." No comparison word.

**Placement (C6-4, C6-5).**
1. **Abstract:** Study 1's preregistered sentence (A4.2 NEG) under every branch. Study 2: branch A gives the L1 sentence and the L-NI sentence; branch B
   gives "a preregistered confirmation study of a learned weighting found {D} (one-sided p = {p}), which does not meet our threshold for a headline claim";
   branch C gives "did not confirm"; no sentence links the two studies. Highlights: an LRF gain only in branch A.
2. Studies 1 and 2 are presented as two separate preregistered studies. Neither section uses the other's result as motivation, explanation or contrast.
   No figure or table contains both GATE-M results on M4 items and LRF numbers; the fresh-fold GATE-M arm is supplement-only.
3. The chronology appears once, in Methods (A6.13); M4-item LRF numbers only in the supplement's exploratory section.
4. Family H keeps A5.9's placement rule.

**Must-not (adds to A4.2.2, A5.9).** Any LRF-to-Study-1 link in any text; "confirmed", "validated" or "generalises" without the matching test; a
guarantee or "calibrated" for LRF; quoting in-sample or `freeze_check.json` numbers as performance; any comparison of LRF with GATE-M or with
CLIP/SigLIP; pooling corruptions, LG cells or folds; "held-out noise family".

## A6.13 Disclosure (Methods, once; amendment item 7 with C6-7's names; wording editable, substance binding)

"Study 2 was added after Study 1 had been analysed (primary result negative), when the target venue changed. The method it tests (LRF) was designed
post hoc on Study 1's 500 test items. Before the design, Study 1's primary and secondary results, its positive-control audit, its exploratory
comparators and an exploratory learned-weighting analysis had all been seen. In that analysis four learned-weighting families (a logistic generalised
additive model, gradient-boosted trees, a multilayer perceptron and a grid model) were compared and the logistic generalised additive model was
selected by inner cross-validation; two other method designs (SCER, CANAL) and two other project routes were considered and not pursued. A first
freeze was found to read the true caption's length through the layout of its inputs; the method was therefore re-scored and re-frozen at a fixed
caption-slot length, a choice declared before any re-frozen result existed. The configuration was frozen (SHA-256 {model}, commit {c}) before any
Study 2 image was selected. Study 2 was preregistered (Addendum A6 r1, commit {c}) with a rule that no further confirmatory study would be added. All
LRF numbers on Study 1's items are post hoc and exploratory. Study 2 tests a different method on different images and does not bear on Study 1's
conclusion." No other sentence of the paper gives Study 1's result as a reason for LRF.

## A6.14 Assumptions and concerns (statistician)

1. The re-frozen object has no out-of-sample estimate; the L_FIX cross-fit estimates the procedure, not the object, and only sets n.
2. The re-score adds about 2.5 GPU-h before L1 on a laptop with eight crashes on record; T_RF (Mon 09:00) is the binding clock.
3. Power is about 0.74 (one-sided 0.05) and 0.63 (headline 0.025) at half the exploratory effect; branch B or C is plausible even if LRF works.
4. LRF's novelty is unaudited (K14); the paper may not claim novelty until an audit exists.
5. The fresh-fold GATE-M arm runs at L_FIX with a threshold calibrated at the true layout; it carries no guarantee and is supplement-only.
6. The firewall statements (who read what) remain statements, not attestations.
7. A p-value says nothing about novelty or practical importance.

## A6.15 Amendment log rows (for the lead)

| Date | Change | Reason | Before/after outcome data? |
|---|---|---|---|
| 2026-10-29 | A6 draft (71c78306) | D0081, D0082 | after Study 1 and the learned-ceiling results; before any Study 2 item |
| 2026-10-29 | A6 r1: object = LRF re-frozen at L_FIX 13 (D0083) with re-score, positive control, invariance gate, clock T_RF Mon 09:00, no fallback; hash set incl. codebook and DI_n013, non-finite = error; L2 removed (m 3); no Study 1/LRF problem-solution framing; headline needs one-sided p <= 0.025; no rescue, branch titles fixed; disclosure names all candidates; no out-of-sample claim for the object; union exclusions; LG and L-NI wording; n-rule from the L_FIX cross-fit, clamped [400, 533]; run order with re-score and re-freeze | red-team C6-1 to C6-11 (0ea9cf33), D0083 (5ff2c0d7) | after D0083; before any re-scored, re-frozen, H or Study 2 output |

---

## Appendix A6. Power arithmetic (CPU, stdlib only; unchanged from the draft, plus the n = 533 row)

Script `a6_power.py` (SHA-256 `18c79d8ba7f76f6f9899449c693041e78ee756433b26ae8db5943a38d7f6b0ae`), output `a6_power_output.txt` (SHA-256
`1f6035099b680eb6ad322a1d6cdef91fb587189f25b4966f02bdfc6ae97b8477`) and `a6_power_lg.txt` in the session scratchpad
`C:\Users\ANONYMIZED\AppData\Local\Temp\claude\C--Users-ANONYMIZED-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\`;
the lead copies them to `runs/P2-LRF-A6/`. The n-rule script of A6.11 item 2 reuses `power1` from this file. The red team reproduced the n = 520 values
(0.730 at Delta 0.05, 0.863 at 0.06).

```
exploratory: pi_d 0.238, theta 0.714, Delta 0.102; budget 4 h at 27 s -> 533 items
n 520: D .04 0.56/0.43 | .05 0.73/0.62 | .06 0.86/0.78 | .08 0.98/0.96 | .102 1.00/1.00   (one-sided alpha .05/.025)
n 533: D .04 0.57/0.44 | .05 0.74/0.63 | .06 0.87/0.79 | .08 0.98/0.96 | .102 1.00/1.00
smallest n with power 0.8 at D 0.05, pi_d 0.238: alpha .05 -> 630 (so the rule gives the cap, 533)
pi_d sensitivity, n 520, D .05/.06: 0.15 0.89/0.97 | 0.20 0.80/0.91 | 0.238 0.73/0.86 | 0.30 0.64/0.78
clean NI (pi_d 0.096, true 0, n 520): margin .02 0.43 | .03 0.71 | .04 0.90
LG n 300, one-sided 0.05/3: pi_d .20: D .06 0.54, .08 0.82, .10 0.96
```
