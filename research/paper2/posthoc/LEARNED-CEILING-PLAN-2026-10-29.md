---
agent: senior ML researcher (subagent of the Paper 2 lead)
date: 2026-10-29
brief: post hoc plan, fixed before any M4 accuracy is computed, for the ceiling of learned reliability weighting
status: PLAN ONLY. Committed alone, before any code that produces an accuracy on M4 runs.
label: post hoc, exploratory, not preregistered. Confidence intervals only, no p-values. AB.1 applies in full.
---

# Ceiling of learned reliability weighting on the M4 test items (plan)

## 0. Question and what it cannot do

**Question.** Could *any* learned per-token reliability model that sees only caption-withheld features produce weights
$w_j\ge 0$ such that the decision $Y_w=\mathbb 1[\sum_j w_j\Delta_j>0]$ is more accurate than no gate (NONE) and than
GATE-M (GM, flag at $\alpha=0.05$) on jpeg10, noise0.1 and splice128? How does that compare with reference ceilings that
need no learning?

**What it cannot do (AB.1, A4.1.1, A4.1.10).** This analysis is post hoc, written after the P label (NEGATIVE,
`runs/P2-GATE-M4/analysis.json`) and the A2.3 audit were read. It can never rescue, explain or qualify the preregistered P
result. It never enters the title, abstract, highlights, conclusion or contribution list as a gain, under any outcome.
Placement: a supplement section, or its own Results subsection after the preregistered families, labelled
"post hoc, exploratory".

**What the author has seen (disclosure).** P label and P/GM/NONE accuracies; Tier-3 accuracies (`tier3_fusion.json`);
the mechanism block of `analysis.json` (changed-code arm minus NONE on jpeg10 is negative); the A2.3 audit; the stored
array keys and NaN counts of the features; the count of changed tokens in item 0 (jpeg10 1007, noise0.1 985,
splice128 243). No learned model has been fitted and no Delta-based quantity beyond the committed files has been computed.

## 1. Data

- Items: the 500 M4 test items, `runs/P2-GATE-M4/arrays/item*.npz`. Conditions: **clean, jpeg10, noise0.1, splice128**.
  The PS cells (patch, swap) are not used: `tex` is undefined there (no pixel image), they are positive controls that
  are never pooled with P cells (A4), and the A2.3 audit already reports their no-learning ceilings. Denoised copies
  (`*_dn`) are not used (no B, D or flags stored).
- Grid: 32 x 32, token index $j$ = row-major (`exp_p2/gate/config.py: GRID = 32`; `baselines.neighbour_codebook_distance`
  reshapes row-major).
- Not opened: anything under `runs/P2-GATE-S2*`, FOIL test outputs.

## 2. Feature set (evidence-separation rule)

Allowed inputs are caption-withheld. Per token $j$ of condition $c$ of item $i$:

| group | features |
|---|---|
| raw scores | $B_j$, $D_j$, $q_j=B_j-D_j$, $s3_j$, $tbv_j$ (log p of the observed code, image visible, caption masked: `scores.tbv_score_raw_logits`), $\log(1+tex_j)$, $nbr_j$ |
| position | row/31, col/31, distance from the grid centre |
| neighbourhood | 3x3 (self excluded, edge-aware) mean of $q$, $B$, $s3$, $tbv$, $\log(1+tex)$, $nbr$; 3x3 min of $q$; 5x5 mean of $q$ |
| item context | within-item percentile rank of $q$, $B$, $s3$, $tbv$; item mean and SD of $q$, $B$, $s3$, $tbv$, $\log(1+tex)$, $nbr$; within-item z-score of $q$ |
| codes | per-token families: through $D_j$ (position marginal at the observed code) and $nbr_j$ (codebook distance); the grid model also gets a learned 8-dim embedding of the code id (16,384 codes) |

**Excluded:** $\Delta$ and anything computed from it; $\Lambda^{c\pm}$; both captions and their token counts; $z$ (except
in the oracle arms of Section 6, which are labelled as such); condition identity (except the labelled condition-aware
variant); the GATE flags (a deterministic function of $q$ plus jitter, so redundant).

**Inherited caveat.** $B$, $D$ and $tbv$ were computed with the caption positions masked but laid out at the length of
$c^+$ (as for the gate itself). The layout length is therefore present in every caption-withheld score; this is the
method's own definition of caption-withheld and is disclosed, not repaired.

## 3. Weight model and decision

$w_j=\sigma(f(x_j))\in(0,1)$ for the differentiable families and $w_j\ge0$ for the GBT plug-in (Section 4). The decision is
$Y_w=\mathbb 1[\sum_j w_j\Delta_j>0]$. Because $w$ never depends on which caption is called $c^+$, swapping the captions
flips the sign of $\sum_j w_j\Delta_j$, so $Y_w$ is an honest accuracy for an order-blind verifier. The class $w\in(0,1)$
contains NONE (constant $w$) and every hard gate, GM included (limits of $\sigma$). Weights are non-negative by design:
the question is about reliability weighting, not about learning to reverse a token's evidence.

## 4. Training objectives (justification)

**O1, item-level (logistic, GAM; MLP; grid model).** For each training item-condition, margin
$M=\sum_j w_j\Delta_j/\sum_j w_j$ (the weighted mean; invariant to the scale of $w$, on the scale of $\Delta$), loss
$\mathrm{softplus}(-M/T)$ averaged over item-conditions, plus the family's regulariser. $T$ is fixed per training set as
the median $|M_{\rm NONE}|$ over its item-conditions (no fitted temperature). Reason: it targets the decision itself; the
logistic surrogate is classification-calibrated for the 0-1 loss of $\mathrm{sign}(M)$; a fixed $T$ keeps losses
comparable across families and folds. A token-level target such as $z$ would train a detector, not a weighting, and is
the secondary analysis only.

**O2, token-level SNR plug-in (gradient-boosted trees).** Proposition (SNR) in `paper2/sections/method.tex`: for
$S=\sum_j w_j\Delta_j$ with independent terms of mean $\mu_j$ and variance $\sigma_j^2$, $E S/\mathrm{sd}\,S$ is maximised
by $w_j\propto\mu_j/\sigma_j^2$, and under Gaussianity $P(S>0)=\Phi$ of that ratio. GBT fits this matched filter with two
`HistGradientBoostingRegressor`s: $\hat\mu(x)$ for $\Delta_j$ (squared error) and $\hat v(x)$ for the squared in-sample
residual (Poisson loss, positive target); $w_j=\max(\hat\mu(x_j),0)/\max(\hat v(x_j),10^{-4})$. Token-level fits allow a
fixed 25 percent token subsample per item-condition (seeded) for speed; item margins always use all 1024 tokens.
Known limits: tokens are correlated (the $\gamma$ terms of the correlated-SNR proposition), and in-sample residuals
understate the variance roughly uniformly. Plain `sklearn` GBT has no item-level custom loss; O2 is the justified
token-level route, and HPO for O2 still uses the item-level criterion of Section 5.

## 5. Model families and search spaces

| family | model | hyperparameters (sampling) | SH resource |
|---|---|---|---|
| F1 logistic-GAM | $f=b+\sum_k g_k(x_k)$, each $g_k$ a linear spline on hinge basis at training quantiles; O1; Adam full batch | knots {0 (linear), 4, 8}; ridge $\lambda$ log-U[1e-5, 1e-1]; lr log-U[3e-3, 3e-2] | epochs, max 300 |
| F2 GBT SNR | two `HistGradientBoostingRegressor` (O2) | learning_rate log-U[0.02, 0.2]; max_leaf_nodes {15, 31, 63}; min_samples_leaf {100, 400, 1600}; l2_regularization log-U[1e-3, 10] | trees, max 450 |
| F3 MLP | per-token MLP, 2 hidden layers, ReLU; O1; Adam, mini-batches of 32 item-conditions | width {32, 64, 128}; dropout {0, 0.1, 0.3}; weight decay log-U[1e-6, 1e-2]; lr log-U[3e-4, 3e-3] | epochs, max 30 |
| F4 grid set/attention | per-token embedding (features + code embedding + learned position embedding) -> two residual 3x3 conv layers (local context) -> 4x4 mean-pool to 64 patch tokens + 1 item token -> 2 transformer encoder layers, 4 heads (global context) -> patch and item context broadcast back to tokens -> MLP head; O1 | width d {16, 32, 48}; dropout {0, 0.1, 0.2}; weight decay log-U[1e-5, 1e-2]; lr log-U[3e-4, 3e-3] | epochs, max 30 |

Features are standardised with training-set statistics (per outer and inner training set). F4 sees the raw-score,
position and code inputs and builds neighbourhood and item context itself; F1 to F3 get the engineered table of
Section 2.

## 6. Arms

Learned (cross-fitted, all corruption-agnostic, trained on the four conditions pooled):
F1, F2, F3, F4, and **SEL**, the nested selection: in each outer fold, the family with the lowest inner-CV O1 criterion at
its final rung supplies that fold's predictions. **SEL is the headline learned ceiling**; the maximum over F1-F4 on the
test folds is reported but labelled "optimistic by selection".

Variants using F2's selected hyperparameters per outer fold (no separate HPO):
- F2+cond: condition one-hot added (knows the corruption type).
- F2+z (oracle): $z_j$ and the condition one-hot added: a learned weighting with perfect detection. Oracle, labelled.
- DET: weight $1-\hat p(z_j)$ from the learned detector of Section 9 (detector-based soft gate).

No learning:
- NONE ($w\equiv1$) and GM ($w=1-\text{flag}_{0.05}$), recomputed from the stored arrays and checked against
  `tier3_fusion.json` (NONE/GM accuracies must match exactly; a mismatch stops the analysis).
- RESTORE-CLEAN: the clean decision of the same item (the bound for any gate that returns the clean decision; a learned
  weighting is not bounded by it, because it can also re-weight clean images).
- CHG: changed-code drop $w=1-z$ (checked against `analysis.json` mechanism `changed_code_minus_none`).
- ZSNR (oracle weighting bound): $w_j=\max(\hat\mu_{c,z_j},0)/\hat\sigma^2_{c,z_j}$, the two-class matched filter that
  knows the corruption type $c$ and each token's $z_j$ but not the test item's $\Delta$; moments from the outer training
  folds (cross-fitted). On clean images it equals NONE.
- UNRESTRICTED (vacuous bound, reported to show why the oracle must be restricted): the share of items with
  $\max_j\Delta_j>0$, which any per-item non-negative weighting that may look at $\Delta$ reaches.

## 7. Cross-fitting and HPO

- **Outer:** 5 folds over the 500 items (seeded permutation, 100 items each); all four conditions of an item stay in one
  fold. Every reported learned decision for an item comes from the model whose training never saw that item.
- **Inner:** 3 folds over the outer training items (seeded per outer fold).
- **HPO method:** random search with synchronous successive halving (eta = 3; 9 configurations; rungs at 1/9, 1/3 and 1 of
  the maximum resource; 9 -> 3 -> 1). At every rung a configuration's score is the mean inner-validation O1 criterion
  over the 3 inner folds. Optuna is not used: the venv has no pip, and modifying the venv while the pinned GPU stage S2
  runs on it is avoided. Random search with SH is the fallback the brief allows; it is a weaker sampler than TPE with
  pruning, which is disclosed.
- **Criterion (all families):** inner-validation mean of $\mathrm{softplus}(-M/T)$ with $T$ from the inner-training
  NONE margins, pooled over the four conditions. Inner accuracy is logged, not used.
- **Final fit:** the selected configuration is refitted on all outer-training items at the full resource. Seeds: F3 and
  F4 are refitted with 3 seeds and the decision uses the mean weight (seed ensemble); per-seed test accuracies are logged
  as the seed spread. F1 (zero init, full batch) and F2 (no subsampling inside the trees) are deterministic given the data
  and the token subsample, refitted once.
- **Seeds:** root seed 20261029; outer split, inner splits, configuration sampling, token subsample and torch init are
  derived from it with `numpy.random.SeedSequence` spawn keys recorded in `results.json`.

## 8. Metrics, intervals, labels

Per condition (clean, jpeg10, noise0.1, splice128) and arm: accuracy with Wilson 95 percent CI. For each learned arm and
each reference arm, contrasts **vs NONE** and **vs GM**: paired accuracy difference with a 95 percent percentile bootstrap
CI (10,000 item resamples, fixed seed), discordant counts $b$ (arm right, reference wrong), $c$, $n_d$, and the exact
Clopper-Pearson 95 percent interval of $\theta=b/n_d$. Direction label as in A4 r3: "identical" if $n_d=0$; "above" iff
the CP lower limit $>0.5$; "below" iff the CP upper limit $<0.5$; otherwise "not distinguishable" with $n_d$ stated.
**No p-value is computed.** No multiplicity adjustment; the number of intervals is printed. Every label is descriptive.

**Reading of "ceiling".** A learned arm "exceeds NONE / GM" on a corruption only if its direction label is "above"; a
gain that also appears on clean images is described as general re-weighting, not as reliability under corruption.

## 9. Secondary: learned corruption detector (descriptive only)

`HistGradientBoostingClassifier` for $z_j$ on the Section 2 features, pooled over the four conditions (clean tokens have
$z=0$), outer cross-fitted, fixed hyperparameters (learning_rate 0.1, max_leaf_nodes 31, early stopping on a 10 percent
validation split, 25 percent token subsample), no HPO. Reported per corruption: mean per-item AUROC (items with both
classes) of $\hat p(z)$ and of the gate's suspicion $u=-q$, with item-bootstrap 95 percent CIs. **K2 caveat (D0074):** $z$
is defined after a VQ re-encode, so on jpeg10 and noise0.1 nearly every token changes and $z$ partly encodes where the
re-encode moves codes, which texture predicts; a detector that wins on $z$ is not thereby a better reliability score
(label circularity). No claim, no label.

## 10. Compute, budget and stop rules

- CPU only: `CUDA_VISIBLE_DEVICES=""`; `torch.set_num_threads(4)`; `OMP_NUM_THREADS`, `MKL_NUM_THREADS`,
  `OPENBLAS_NUM_THREADS` = 4; sklearn GBT uses OpenMP (4 threads). RAM target below 4 GB (the full table is about
  2.05 M token rows x 34 float32 columns, about 0.3 GB).
- Wall-clock budget: about 3 hours. **Timing smoke** before any accuracy: one fit per family at its maximum resource on
  the inner-training items of outer fold 0, inner fold 0; only seconds are recorded. If the projected total exceeds 2.5
  hours, the slowest family's configurations drop from 9 to 6 (rungs 6 -> 2 -> 1), then its maximum resource is cut by
  a third, until the projection fits; the change is written to `results.json` and the report before outer-test
  accuracies exist.
- The run writes a checkpoint per outer fold and family, so a stop loses at most one fold-family.
- Outputs: `runs/P2-POSTHOC-LEARNED/` (`results.json`, `hpo/<family>_fold<k>.json` per-rung logs, `env.json` with
  versions, `timing_smoke.json`, `stdout.log`). Code: `analysis_posthoc/learned_ceiling/`. Nothing under `exp_p2/` or
  `tools/` changes.
- Report: `research/paper2/posthoc/LEARNED-CEILING-REPORT-2026-10-29.md`, every number from `results.json`.

## 11. What may be said (fixed now, before results)

- Allowed (supplement or own Results subsection, "post hoc, exploratory"): the per-corruption accuracy of SEL and of each
  family against NONE and GM with CIs and labels; the no-learning ceilings; whether the oracle arms (ZSNR, F2+z) leave
  room that the caption-withheld learners do not reach.
- Not allowed under any outcome: any statement that a learned weighting "fixes", "rescues" or "would have made GATE work";
  any link to the P null as its cause or explanation; any title, abstract, highlight, conclusion or contribution-list
  sentence; calling a learned arm "our method"; detector AUROC wins worded as better reliability (K2).
- If SEL is "above" NONE on a corruption, the sentence is: "In a post hoc, exploratory analysis, a weighting learned from
  caption-withheld scores on cross-fitted items reached {acc} on {corruption} against {acc_none} without a gate
  (difference {d}, 95 percent CI {lo} to {hi}; n_d = {n_d})", followed by whether the same arm moved clean accuracy.
- If no learned arm is "above": "No learned caption-withheld weighting among the four families exceeded the no-gate
  decision on any realistic corruption (post hoc, exploratory; Table S{k})", with the oracle arms beside it.
