---
agent: senior ML researcher (subagent of the Paper 2 lead)
date: 2026-10-29
brief: freeze LRF (logistic-GAM F1) on all 500 M4 items; feature and mechanism reading; caption-length / layout test (D0082)
sources_examined: [runs/P2-GATE-M4/arrays/item*.npz, runs/P2-GATE-M4/items.jsonl (n_tok, n_tok_neg only), runs/P2-GATE-DCACHE/DI_n*.npy, runs/P2-POSTHOC-LEARNED/ckpt/F1_fold*.npz, exp_p2/gate/scores.py, exp_p2/scoring.py:92-104]
coverage: CPU only, 4 threads; stored arrays only; no GPU re-scoring; S2 and FOIL outputs not opened
run: runs/P2-LRF-FROZEN/ (model.npz, spec.json, hpo.json, freeze_check.json, diagnostics.json, insample_weights.npz)
code: analysis_posthoc/learned_ceiling/lrf.py (freeze + inference), lrf_diag.py (diagnostics)
claims:
  - statement: "LRF is frozen: logistic-GAM, 35 features, 8 hinge knots per feature, ridge 0.00272, lr 0.0169, 40 epochs, seed 316748921, T 0.1697; model.npz sha256 ca5c4e2fc5c6635a051a7c3a11f7b9e555fe9f6e2ce329825a80cb9b4bca1e65; numpy inference equals the torch training path (max abs weight difference 3.4e-7)."
    status: supported
    evidence: runs/P2-LRF-FROZEN/spec.json, freeze_check.json
    level: E4
    confidence: 0.95
  - statement: "The caption-withheld features encode the true caption's token length (cross-validated R^2 0.41 from item summaries of the 7 raw scores; permutation null max 0.019 over 200 permutations)."
    status: supported
    evidence: diagnostics.json length_checks.encoding_r2_npos_from_item_feature_summaries
    level: E4
    confidence: 0.9
  - statement: "No sign that the noise0.1 gain uses the length: the cross-fitted gain is +0.096 (true caption shorter), +0.136 (equal length, 59 items, where no layout leak is possible) and +0.099 (true caption longer); gain vs length difference rho 0.013, permutation p 0.77; re-scoring D at the negative caption's length flips 1 of 500 noise0.1 decisions."
    status: supported
    evidence: diagnostics.json length_checks.crossfit_gain_vs_length.noise0.1, counterfactual_D_layout
    level: E4
    confidence: 0.75
  - statement: "On clean and splice128 the cross-fitted gain is positive when the true caption is longer and negative when it is shorter (difference 0.045 in both; permutation p 0.15 and 0.16), the direction a layout leak would produce; there is no net gain in either condition."
    status: mixed
    evidence: diagnostics.json length_checks.crossfit_gain_vs_length.clean, .splice128
    level: E4
    confidence: 0.5
competing_explanations:
  - "The clean/splice length pattern is noise (two of four conditions, neither below p 0.1, no net gain to explain)."
  - "B and tbv carry the layout too and could not be re-scored from stored data; the D counterfactual tests only one of three layout-dependent scores."
unknowns:
  - "Whether LRF's weights move when B and tbv are scored at a length-neutral layout (needs the GPU)."
next_test: {hypothesis: "LRF's noise0.1 gain over NONE survives a length-neutral layout and fresh items", intervention: "re-score M4 caption-withheld scores at L_FIX = 13, re-freeze F1 with the identical protocol, then score the fresh preregistered fold", primary_metric: "noise0.1 accuracy, LRF minus NONE (exact McNemar or CP label as preregistered)", falsifier: "no gain on the fresh fold", gpu_hours: "not estimated here"}
---

# LRF frozen model, feature reading and caption-length test

Status: post hoc model selection on the M4 test items (discovery set). Under D0082 a gain may be claimed only from a fresh,
preregistered fold. Nothing in this file is a confirmatory number. Every number is in `runs/P2-LRF-FROZEN/`.

## 1. Frozen model (task 1)

- **Procedure.** The same random search with successive halving as the learned-ceiling run (9 configurations; rungs of
  4, 13 and 40 epochs; 3 inner folds), run over all 500 items with seed key 99. The selected configuration was refitted
  once on all 500 items × 4 conditions (clean, jpeg10, noise0.1, splice128) with one fixed seed.
- **Selected configuration.** Knots 8, ridge 0.00272, lr 0.0169. Inner-CV O1 is 0.375, against 0.468 to 0.484 for NONE
  in the learned-ceiling folds. Wall time 241 s.
- **Artifacts (`runs/P2-LRF-FROZEN/`).**
  - `model.npz`: a [35], b, c [35, 8], knots [35, 8] on the standardised scale, mu and sd [35], and the feature names in order.
  - `spec.json`: the feature list and order, each feature's definition, preprocessing, objective, hyperparameters, seeds,
    T, the model sha256 and the code sha256s of data.py, families.py and lrf.py.
  - `hpo.json`: the per-rung log.
- **Inference (CPU, no model download).**
  `lrf.load_frozen()` checks the sha256 and the feature order. `lrf.infer_item(fz, np.load(itemNNNN.npz), cond)` returns
  the 1024 weights, the score $\sum_j w_j\Delta_j$, the weighted-mean margin and the decision. Steps: `raw_from_npz` ->
  `data.engineer` (per item and condition, with no cross-item statistic) -> $(X-\mu)/sd$ -> GAM -> sigmoid.
- **Self-check.** On 20 items × 4 conditions the numpy path equals the torch training path (max abs difference 3.4e-7).
- **In-sample accuracy (optimistic; for the record only).** clean 0.900, jpeg10 0.860, noise0.1 0.788, splice128 0.892.
  NONE: 0.880, 0.838, 0.676, 0.876. The honest out-of-fold numbers remain those of the learned-ceiling report (noise0.1
  0.778).

## 2. What the model uses (in-sample, descriptive)

**Weights are sparse.** The intercept is -2.61. The share of tokens with $w<0.2$ is 0.87 (clean), 0.78 (jpeg10), 0.99
(noise0.1) and 0.87 (splice128). Only the top weight quintile carries real weight (mean 0.42 clean, 0.70 jpeg10). LRF is
therefore a smooth selection of roughly the top fifth of tokens, not a mild re-weighting. Because the decision is
scale-free, the very small absolute weights on noise0.1 (mean 0.0075) still give a relative ranking.

**Largest contributions** (SD of each shape function over tokens). Shapes are given from the 5th to the 95th percentile,
relative to the median:

| feature | shape | effect on weight |
|---|---|---|
| `nbr` (mean codebook distance to the 8 neighbours) | +1.77 to -3.00 | locally homogeneous codes weighted up, codes unlike their neighbours down |
| `itemsd_nbr` | -0.35 to +2.19 | items with heterogeneous code maps are weighted more selectively |
| `rank_B` (within-item rank of the own-context likelihood) | -1.15 to +1.81 | up |
| `rank_s3` | +0.74 to -1.38 | tokens the network predicts confidently weighted up |
| `tbv` | -0.64 to +1.58 | up |
| texture SD and neighbourhood texture | | up |
| `rad` | +1.09 to -0.97 | central tokens weighted up |
| neighbourhood and item means of q (`nb3mean_q`, `nb3min_q`, `itemmean_q`) | | down: given its own rank, a token surrounded by high-q tokens is weighted less |

Collinearity among the 35 features (raw, neighbourhood and item versions of the same score) means single shape
functions are not uniquely identified. Read the groups, not single coefficients.

**Group occlusion** (a group's standardised inputs set to the training mean; in-sample accuracy on noise0.1, full model
0.788):

| group removed | noise0.1 accuracy |
|---|---|
| neighbourhood | 0.740 |
| rank | 0.746 |
| position | 0.768 |
| item statistics | 0.784 |
| raw scores | 0.804 |

On jpeg10, removing the neighbourhood group drops accuracy to 0.772 (full model 0.860). Spatial context (neighbourhood
summaries) and within-item ranks carry the gain; the raw scores alone do not.

**Mechanism (in-sample).**
- The weights track evidence quality, not corruption labels. In every condition, tokens in higher weight quintiles have
  a higher mean $\Delta$ and a higher per-token SNR. On noise0.1 SNR rises from 0.064 in the lowest quintile to 0.259 in
  the highest; on clean from 0.153 to 0.388.
- Spearman rho of $w$ with q is 0.50 to 0.56; with $z$ it is -0.01 to -0.05.
- Simple rules do not reproduce the learned gain. Keeping the top 5 to 50 percent of tokens by q gives noise0.1
  0.652-0.680, which is NONE level. By B it gives 0.684-0.702, and by tbv 0.716-0.748, below the cross-fitted 0.778 even
  after picking the best of 15 rules. The learned combination of local code homogeneity, own-context rank, confidence and
  centrality is what matters.

**Honest reading.**
- Gaussian pixel noise re-encodes about 93 percent of codes, so "corrupted or not" carries no information.
- LRF instead finds the tokens whose caption evidence survives. They sit in central, locally homogeneous regions, where
  the network predicts the observed code confidently from the rest of the image. In those regions the re-encoded codes
  stay semantically close to the clean ones.
- This makes LRF an evidence-quality selector. It is not a corruption detector, and it is closer to "keep the
  self-consistent, homogeneous tokens" than to GATE's "drop the 5 percent least self-consistent".
- The same rule gives no net gain on clean, jpeg10 or splice128 out of fold. On splice128 and clean there is little
  headroom (NONE 0.876 and 0.880, clean bound 0.880).
- This reading is in-sample and correlational. A causal test would re-score a fresh fold with the frozen model and ablate
  the neighbourhood group as a preregistered secondary.

## 3. Caption-length / layout test (task 2)

**Why it matters.** `scoring.build` puts `len(cap_tok)` caption slots before the image (`exp_p2/scoring.py:96-104`). B,
D, s3 and tbv mask the caption content, but `cap_tok` is the true caption's. The scores therefore carry the true
caption's length, and the image positions are shifted by it. Lengths: 8-29 tokens, median 13. 59 items have
equal-length captions, the true caption is longer in 223 and the negative caption in 218.

**Results** (`diagnostics.json` `length_checks`):
1. **The features encode the true length.** Ridge on item means and SDs of the 7 raw scores predicts `n_tok` with
   cross-validated R² 0.41. The permutation-null maximum is 0.019 (200 permutations, p = 1/201, the smallest attainable).
   The leak path exists in principle.
2. **Weights barely track length.**
   - Item-mean weight vs `n_tok`: Spearman rho 0.001 (clean), 0.014 (jpeg10), 0.098 (noise0.1, permutation p 0.03,
     1 of 8 tests) and -0.013 (splice128).
   - Item-mean weight vs the length difference: |rho| at most 0.058, all p ≥ 0.23.
3. **Decision gain vs length difference** (cross-fitted F1, honest). Gain is LRF minus NONE.

   | condition | true caption shorter | equal length | true caption longer | rho with length difference | permutation p |
   |---|---|---|---|---|---|
   | noise0.1 | +0.096 (39/18) | +0.136 (10/2) | +0.099 (36/14) | 0.013 | 0.77 |
   | jpeg10 | +0.028 | +0.034 | +0.036 | | p(diff) 0.82 |
   | clean | -0.018 (9/13) | 0.000 | +0.027 (14/8) | | p(diff) 0.15 |
   | splice128 | -0.023 (10/15) | 0.000 | +0.022 (16/11) | | p(diff) 0.16 |

   The noise0.1 gain is flat across strata and present in the leak-free equal-length stratum. Clean and splice128 show
   the leak-shaped pattern, with no net gain and no significance.
4. **Counterfactual D.** D was re-scored at the negative caption's length from the D cache, with B and tbv unchanged, and
   fed to the frozen model. Mean |Δw| is 0.0004-0.0018. Decisions flip on 0 (clean), 0 (jpeg10), 1 (noise0.1) and 1
   (splice128) of 500 items. With the symmetric average of both layouts: 0 flips.

**Reading.** In the stored data there is no evidence that LRF's noise0.1 gain comes from the layout length. But the
features demonstrably carry the true caption's length. The two other layout-dependent scores (B, tbv) could not be
re-scored. Clean and splice128 show a weak pattern in the leak's direction. As frozen, LRF is not order-blind by
construction.

**Recommendation: a length-neutral layout (a scoring change) is needed for the confirmatory run.** A stratified analysis
alone does not suffice. It can bound a leak, but it cannot turn a method that reads the true caption's length into a
deployable one. Specification:

1. **Layout.** Every caption-withheld score (B and s3 from `scores.image_B`, D from the D cache, tbv from
   `scores.tbv_score_raw_logits`) is computed on `sc.build([PAD] * L_FIX, codes)` with **L_FIX = 13**, the M4 median
   true-caption length. These passes mask the caption, so slot content is irrelevant; only the count changes. D then
   comes from `DI_n013.npy`, which already exists. $\Lambda^{c\pm}$ and Delta are unchanged (caption visible, their own
   lengths).
2. **Invariance check (L10-style, before any outcome).** On 5 items × 4 conditions, B, D, s3 and tbv are identical when
   the sequence is built from the c+ tokens, the c- tokens or PAD, all at L_FIX (max abs diff 0).
3. **Re-freeze.** Re-score the 500 M4 items (4 conditions; B, s3 and tbv passes; no Lambda passes) at L_FIX on the GPU.
   Re-run `lrf.py --freeze` unchanged (same seed keys, HPO and protocol). Record the new model sha256 before the fresh
   fold is scored. The current model (sha ca5c4e2f...) stays as the record of the M4-layout fit and is not used for
   confirmation.
4. **Code location.** New entry points outside the pinned `exp_p2/` and `tools/` while S2 runs, or a dated pin row
   after S2. No edit to the scoring code the S2 pin covers.
5. **Preregistered secondary (cheap insurance).** On the fresh fold, report the LRF-minus-NONE gain by length stratum
   (true shorter, equal, true longer). Report the difference between the true-longer and true-shorter strata with a 95
   percent CI. Any reading beyond that is descriptive.

If the GPU budget rules out step 3, the fallback is the current layout with step 5 as a **co-primary** sensitivity
analysis. Under the fallback, the claim must then be worded "with caption-withheld scores laid out at the true caption's
length". That is weaker, and a reviewer can fairly call it non-deployable.

## 4. Concerns for the lead

- M4 was the preregistered P test set and is now LRF's training set. Every LRF number from M4 is post hoc; the fresh fold
  must be items never scored before.
- The learned-ceiling report's "may not" list was written under AB.1 for M4-derived numbers. It still binds every
  M4-derived LRF sentence; only fresh-fold results can carry a method claim, and none may be framed as explaining the P
  null.
- The only robust out-of-fold gain was on noise0.1; jpeg10 was not distinguishable from NONE and splice128 showed none.
  A confirmatory plan that pools corruptions, or makes jpeg10 primary, is likely underpowered.
