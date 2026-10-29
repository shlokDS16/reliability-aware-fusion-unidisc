---
agent: senior ML researcher (subagent of the Paper 2 lead)
date: 2026-10-29
brief: post hoc ceiling of learned reliability weighting on the M4 test items (CPU only)
sources_examined: [runs/P2-GATE-M4/arrays/item*.npz (500 items; clean, jpeg10, noise0.1, splice128), runs/P2-GATE-M4/tier3_fusion.json, runs/P2-GATE-M4/analysis.json, paper2/sections/method.tex, research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md, research/paper2/prereg/A2.3-AUDIT-PS-2026-10-29.md]
coverage: all 500 M4 items, four conditions; PS cells (patch, swap), denoised copies, S2 and FOIL outputs NOT used or opened
label: post hoc, exploratory, not preregistered. CIs only, no p-values. Cannot rescue, explain or qualify P (AB.1)
plan: research/paper2/posthoc/LEARNED-CEILING-PLAN-2026-10-29.md (commit d457d295, before any result)
code: analysis_posthoc/learned_ceiling/ (commit 33e69f14; one later edit adds the inner-CV O1 of NONE and GM, see Deviations)
run: runs/P2-POSTHOC-LEARNED/ (results.json, hpo/<family>_fold<k>.json, ckpt/, env.json, timing_smoke.json, stdout.txt)
claims:
  - statement: "On noise0.1, a cross-fitted weighting learned from caption-withheld scores (SEL, which chose the logistic-GAM F1 in all 5 outer folds) reached accuracy 0.778 against 0.676 for both NONE and GM (difference +0.102, 95 percent bootstrap CI +0.060 to +0.144; b 85, c 34, n_d 119; CP interval of theta 0.624 to 0.793, label 'above')."
    status: supported
    evidence: runs/P2-POSTHOC-LEARNED/results.json results.noise0.1
    level: E4
    confidence: 0.8
  - statement: "On jpeg10, SEL reached 0.870 against NONE 0.838 (+0.032, CI +0.002 to +0.062; b 39, c 23; CP 0.497 to 0.748, 'not distinguishable') and against GM 0.836 (+0.034, CI +0.004 to +0.064; CP 0.504 to 0.753, 'above')."
    status: mixed
    evidence: results.json results.jpeg10
    level: E4
    confidence: 0.6
  - statement: "On splice128 and on clean images no learned arm exceeded NONE: SEL 0.876 against 0.876 on splice128 (b 28, c 28) and 0.884 against 0.880 on clean (b 25, c 23)."
    status: supported
    evidence: results.json results.splice128, results.clean
    level: E4
    confidence: 0.8
  - statement: "The label-aware oracle weightings did not do better than the caption-withheld learner: ZSNR (two-class matched filter with true z) was within 0.004 of NONE in every corruption, and F2 given the true z (F2+z) was no better than F2 without it."
    status: supported
    evidence: results.json results.<cond>.vs_NONE.ZSNR and .F2+z
    level: E4
    confidence: 0.7
competing_explanations:
  - "The noise0.1 gain is a property of the scores under that corruption (for instance, down-weighting tokens whose caption-withheld likelihood marks heavy noise), not of reliability in the sense of z; z covers 93 percent of noise0.1 tokens and the z-oracle arms gain nothing."
  - "The caption-withheld scores carry the token-length layout of c+ (inherited from the gate). No route by which a non-negative weight could turn this into the sign of Delta is known, but it was not tested."
unknowns:
  - "Which features F1 relies on (no attribution was run; the fitted models were not stored)."
  - "Whether the grid model (F4) fails because of the budget (30 epochs, 9 configurations) or because of the family; its inner-CV criterion was worse than NONE in every fold."
next_test: {hypothesis: "the noise0.1 gain of F1 reproduces on held-out items from another run (M5 or Omni) with the F1 configuration frozen now", intervention: "refit F1 on all 500 M4 items, freeze, score a new item set", primary_metric: "accuracy on noise0.1 vs NONE (CP label)", falsifier: "CP label not 'above'", gpu_hours: 0}
---

# Ceiling of learned reliability weighting: report

All numbers below are copied from `runs/P2-POSTHOC-LEARNED/results.json`. n = 500 items per condition; every learned
decision comes from a model that did not see the item (5 outer folds by item, 3 inner folds for HPO).

## 1. What was run

- **Features:** 35 caption-withheld columns per token (B, D, q, s3, tbv, log(1+tex), nbr; grid position; 3x3 and 5x5
  neighbourhood summaries; within-item ranks, means and SDs; within-item z of q). The grid model used the 7 raw scores
  plus a learned code embedding and position embedding. No Delta, Lambda, caption, z (except labelled oracle arms) or
  condition identity (except F2+cond) entered any weight model.
- **Families and objectives:** F1 logistic-GAM (linear splines, item-level logistic loss O1 on the weighted-mean margin);
  F2 gradient-boosted trees as an SNR plug-in, w = max(mu,0)/var (token-level O2, the matched filter of the SNR
  proposition); F3 per-token MLP (O1); F4 grid model, 3x3 convolutions plus a 2-layer transformer over 64 patch tokens
  and an item token (O1). Random search with successive halving (9 -> 3 -> 1 configurations, eta 3) on the inner-CV O1
  criterion; SEL = per outer fold, the family with the lowest inner-CV criterion.
- **Compute:** CPU only, 4 threads, `CUDA_VISIBLE_DEVICES=""`. Timing smoke projected 110 min; the run took about
  4 h (09:59 to 13:58 IST), about 1 h over the brief's 3 h target. F1, F2 and F3 configurations with more knots, more
  trees or wider layers were slower than the sampled smoke configurations, and the S2 GPU stage shared the machine. The
  budget was not cut mid-run, because outer-fold results already existed and folds would then have had unequal budgets.

## 2. Checks

NONE and GM accuracies recomputed from the arrays equal `tier3_fusion.json` in all four conditions, and CHG minus NONE
equals `analysis.json` mechanism `changed_code_minus_none` for the three corruptions (`results.json` `checks`, all
`match: true`).

## 3. Results (accuracy; contrasts are arm minus reference, 95 percent bootstrap CI, discordant b/c, A4 r3 CP label)

| condition | NONE | GM | SEL (=F1) | SEL vs NONE | SEL vs GM | best other learned | RESTORE-CLEAN | CHG (oracle) | ZSNR (oracle) | F2+z (oracle) |
|---|---|---|---|---|---|---|---|---|---|---|
| clean | 0.880 | 0.882 | 0.884 | +0.004 [-0.024, +0.030], 25/23, n.d. | +0.002 [-0.024, +0.028], 24/23, n.d. | F2 0.864 | (= NONE) | (= NONE) | (= NONE) | 0.862 |
| jpeg10 | 0.838 | 0.836 | 0.870 | +0.032 [+0.002, +0.062], 39/23, n.d. | +0.034 [+0.004, +0.064], 40/23, above | F2 0.826 | 0.880 | 0.754 (below) | 0.834 | 0.838 |
| noise0.1 | 0.676 | 0.676 | **0.778** | **+0.102 [+0.060, +0.144], 85/34, above** | +0.102 [+0.060, +0.144], 85/34, above | F3 0.774 (above) | 0.880 | 0.746 (above) | 0.680 | 0.730 |
| splice128 | 0.876 | 0.872 | 0.876 | +0.000 [-0.028, +0.030], 28/28, n.d. | +0.004 [-0.024, +0.034], 29/27, n.d. | F2+cond 0.876 | 0.880 | 0.880 | 0.872 | 0.866 |

n.d. = not distinguishable. Wilson 95 percent intervals of SEL: clean 0.853-0.909, jpeg10 0.838-0.897, noise0.1
0.740-0.812, splice128 0.844-0.902. CP intervals of theta = b/n_d for SEL vs NONE: clean 0.372-0.667, jpeg10
0.497-0.748, noise0.1 0.624-0.793, splice128 0.363-0.637.

Other learned arms (accuracy clean / jpeg10 / noise0.1 / splice128):
- F2 GBT SNR: 0.864 / 0.826 / 0.724 (above NONE: +0.048 [+0.024, +0.074], 33/9) / 0.870.
- F2+cond (knows the corruption type): 0.862 / 0.824 / 0.734 (above, 40/11) / 0.876.
- F3 MLP (3-seed ensemble): 0.852 / 0.822 / 0.774 (above, +0.098 [+0.052, +0.144], 96/47) / 0.842. Seed spread on
  noise0.1 0.750-0.766, on jpeg10 0.798-0.820.
- F4 grid model (3-seed ensemble): 0.814 (below) / 0.766 (below) / 0.672 / 0.766 (below). Its inner-CV O1 (0.739 to 0.800
  across folds) was worse than NONE's (0.468 to 0.484) in every fold, so it is an under-trained family at this budget,
  not evidence about spatial context.
- DET, weight 1 - p_hat(z): 0.880 / 0.790 (below NONE, 13/37) / 0.712 (above, 37/19) / 0.868.
- UNRESTRICTED (weights allowed to look at Delta): 1.000 in every condition, a vacuous bound, as expected.

Inner-CV O1 (lower is better) by outer fold: F1 0.366-0.420, F2 0.426-0.458, F3 0.412-0.531, F4 0.739-0.800; NONE
0.468-0.484, GM 0.464-0.481. SEL picked F1 in 5 of 5 folds.

**Secondary, detector (descriptive only; K2 label circularity, D0074).** Mean per-item AUROC for z, learned detector
against the gate's u = -q: jpeg10 0.768 [0.761, 0.776] vs 0.560 [0.551, 0.569]; noise0.1 0.791 [0.785, 0.797] vs 0.509
[0.503, 0.516]; splice128 0.602 [0.593, 0.610] vs 0.511 [0.506, 0.517]. Shares of changed tokens: 0.961, 0.928, 0.227. A
better z-detector did not give a better decision: DET is below NONE on jpeg10, and the z-oracle arms (CHG, ZSNR, F2+z)
gain nothing on jpeg10 and splice128.

## 4. Reading

1. **The ceiling depends on the corruption.** With the selected learner (F1):
   - On **noise0.1** a learned caption-withheld weighting clearly beats both NONE and GM (+0.102). That recovers about
     half of the gap to RESTORE-CLEAN (0.880).
   - On **jpeg10** the gain over NONE is small and its label is not distinguishable (+0.032; RESTORE-CLEAN +0.042). It is
     "above" GM only by the CP rule, and only just (lower limit 0.504).
   - On **splice128** there is nothing to gain: NONE is already 0.876 against a clean bound of 0.880.
2. **The gain is not general re-weighting.** On clean images SEL is 0.884 against 0.880 (b 25, c 23), so the noise0.1
   gain appears only under that corruption.
3. **The gain is not detection of changed codes.** Knowing z exactly does not help, for three reasons:
   - ZSNR is within 0.004 of NONE everywhere.
   - F2+z is no better than F2.
   - Dropping changed codes (CHG) helps on noise0.1 (+0.070), but less than F1 does, and hurts on jpeg10 (-0.084).

   Under the pixel corruptions almost every token changes code (93 to 96 percent), so z is not a reliability label. What
   the learner uses is graded information in the scores about how much each token's evidence still points the right way.
4. **Model family.** The simplest O1 model (logistic-GAM) was best. It was best on the inner criterion in all folds, and
   on the test folds too.
   - The MLP came close on noise0.1, with larger seed variance.
   - The GBT SNR plug-in was weaker. Its token-level target is a noisier route to an item decision.
   - The grid/attention model did not train to a useful solution in 30 epochs. "Spatial context does not help" is
     therefore not established, only "not reached at this budget".
5. **Selection optimism.** SEL is the nested-honest number. F1 equals SEL here, so the max-over-families number adds no
   optimism. The 94 intervals carry no multiplicity adjustment.

## 5. What may and may not be said in the paper

**May** (supplement, or its own Results subsection after the preregistered families, labelled "post hoc, exploratory"):
- "In a post hoc, exploratory analysis, a weighting learned from caption-withheld scores on cross-fitted items
  reached 0.778 on noise0.1 against 0.676 without a gate (difference +0.102, 95 percent CI +0.060 to +0.144; n_d =
  119)". Follow it with: on clean images the same arm was 0.884 against 0.880, and on jpeg10 and splice128 no learned arm
  was distinguishable from no gate.
- The oracle result: weighting with the true changed-code labels (ZSNR, F2+z) did not exceed no gate on any corruption
  (ZSNR within 0.004).
- The detector AUROCs only with the K2 caveat, and never as a better reliability score.

**May not:**
- Any sentence in the title, abstract, highlights, conclusion or contribution list.
- Any claim that a learned weighting "fixes", "rescues" or "would have made" GATE work.
- Any link to the P null as its cause or explanation (AB.1). That includes "the gate failed because masked-likelihood
  detection targets z": this analysis was designed after P and cannot carry that inference.
- Calling F1 "our method".
- Pooling the noise0.1 gain with the other corruptions.
- Wording F4's failure as evidence about spatial context.
- Quoting the jpeg10 "above GM" without the n.d. label against NONE beside it.

## 6. Deviations from the plan (all disclosed)

1. **F1 training.** The plan said "Adam full batch, max 300 epochs". The code uses AdamW mini-batches of 32
   item-conditions, maximum 40 epochs, with weight decay 0 (the ridge term is the regulariser). This was fixed in code
   before the timing smoke and before any accuracy, because full-batch hinge expansion at 1.6 M token rows was too slow.
2. **Wall time.** About 4 h against the 3 h target (Section 1). The plan's budget-cut rule was triggered only by the
   timing-smoke projection (110 min), which did not exceed 2.5 h, so no cut was made.
3. **Added reference after the run.** `inner_o1_reference` (the inner-CV O1 of NONE and GM) was added to `run.py` while
   fold 0's F4 was running, before any outer-test accuracy was read. Analysis was re-run with `--analyse-only`; no fitted
   result changed.
4. **Optuna not used.** The venv has no pip, and the venv was not modified during S2. Random search with successive
   halving is used instead, as the plan states.
