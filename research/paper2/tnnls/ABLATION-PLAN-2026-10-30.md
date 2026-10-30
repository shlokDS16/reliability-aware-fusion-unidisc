---
agent: ml-expert
date: 2026-10-30
brief: Exploratory Tier-3 ablation plan for Study 2 (LRF), SPEC.md section 6 (spec v2); written before any variant is scored on fresh-fold items
status: PLAN ONLY. Nothing below has been implemented or run. No variant has been fitted or scored. Statistician check required before commit (SPEC 6).
label (binding, verbatim in paper): "exploratory; added after the primary, family H and Study 2 results"
sources_examined:
  - paper2-tnnls/SPEC.md sections 0 (rules 1, 3, 5), 6, 7, 8
  - research/paper2/tnnls/REDTEAM-SPEC-2026-10-30.md R2, R4, "Hostile area-chair preview" (lines 233-260)
  - coordinator message 2026-10-30 (red-team re-check V2-2, binding conditions 1-5)
  - runs/P2-LRF-FROZEN-LFIX/{spec.json, hpo.json, selfcheck.json, HASHES.json}
  - analysis_posthoc/learned_ceiling/{data.py, families.py, lrf.py, run.py lines 25-135}
  - analysis/paper2/lrf/{refreeze.py, a6_analysis.py lines 25-118, baselines.py line 38}
  - exp_p2/gate/lrf_score.py lines 1-66 and function list; exp_p2/gate/seeds.py; exp_p2/gate/{h_strata.py, tier3_fusion.py} seed keys
  - runs/P2-POSTHOC-LEARNED/{timing_smoke.json, hpo/F*_fold*.json sec_total}
  - paper2-tnnls/scripts/fig4_study2_weights.py line 98 (feature-group partition used in the paper)
coverage: code paths above read; fresh-fold arrays NOT opened; design arrays NOT opened; no accuracy of anything computed.
---

# Study 2 exploratory ablation plan (Tier 3)

## 0. Status, scope and binding conditions

1. This plan fixes the **full variant list** (section 3) before anything is committed or scored. Every listed row is reported,
   whatever its result. No row is added, removed, merged or renamed after the first fresh-fold score is written; a defect is fixed by
   a rerun beside the first one (card v3 section 17 convention), and both are reported.
   **Rerun rule (SC-5):** a rerun is allowed only for (i) an exception or NonFinite stop, (ii) a control mismatch (section 6 item 5),
   (iii) a hash mismatch, (iv) a code bug shown by a unit test. It is never allowed because a result looks unexpected. Every rerun is
   reported with its reason. No output is read before the run is complete. **No promotion:** after the score stage the Study 2 object
   stays the frozen LRF, whatever the intervals show; no variant is selected and scored again on these fresh items (the fresh fold is
   spent; any confirmation would need new items and a new preregistration).
2. **No Study 1 object** appears anywhere in this plan, its code, its outputs or its text (C6-4; V2-2 item 2): no GATE-M, no gate
   flag, no conformal-risk-control threshold, no suspicion score u, no conformal p-value weight, no A4 Tier-3 comparator, no
   "hard versus soft" row or framing. The scorer never reads `y_gatem`, `m_gatem`, `<cond>_flag*` or any GATE field (it raises if
   asked). Features are named only by formula (SPEC rule 3).
3. **Fitting uses only the 500 design items** (`runs/P2-LRF-RESCORE/arrays`, digest
   `038ded07...8e90`, the arrays LRF was re-frozen on). Fresh-fold items (`runs/P2-LRF-L1/arrays`, 450 items;
   `runs/P2-LRF-LG/arrays`, 300 items) touch no fitting, tuning, selection, standardisation, knot placement or variant choice.
4. **Placement:** Results subsection V-G (one short subsection, one table) and supplement S-VII. Never in title, abstract, highlights,
   conclusion, contributions, cover letter, the response to reviewers (SC-8) or repository front matter (README top section, Zenodo description). Listed in the
   deviations box (SPEC 8: "Tier-3 ablation added at writing (section 6)").
5. **Inference:** intervals only. No p-value is computed, printed or stored. No variant is described as better or worse than LRF, or
   than NONE, in any claim; the text states where an interval lies (section 8).
6. **What the lead had seen when this plan was written (disclosure, goes into S-VII and the deviations box):** the fresh-fold L1 and
   LG results of the frozen LRF and NONE (`runs/P2-LRF-L1/a6_analysis.json`, `runs/P2-LRF-LG/a6_analysis.json`); the exploratory M4
   cross-fit of families F1-F4 (`runs/P2-POSTHOC-LEARNED/results.json`, old M4 layout); the frozen LRF's shape functions
   (Fig. 4). No ablation variant has ever been fitted at L_FIX or scored on any fresh item. (SC-8) The variant list was fixed after
   the lead had seen the fresh LRF and NONE results; no variant was fitted or scored before the list was committed.
7. **Fresh cells are dependent (statistician concern).** If the LG items are a prefix of the fresh fold (A6 line 161; not verified in
   the arrays), LG and L1 cells share images. The score stage records the image-id overlap between the L1 and LG item lists
   (`controls.json` `lg_l1_image_overlap`), and S-VII states it, with the sentence "the eight cells are not independent samples".

## 1. The question the ablation answers

Red team R4 and the area-chair preview: is the 35-feature logistic-GAM weighting needed, or would a simpler aggregation rule at the
same budget give the same fresh-image intervals, and does one group of features (in particular a noise-sensitive score such as nbr or
tbv) carry the L1 gain? Two complementary questions:

- **Sufficiency (refit):** does a weighting restricted to one feature source, or to one feature, or without hinge terms, or of a
  different pooling family (attention-MIL), fitted with the same protocol, budget and seeds on the same design items, reach an
  interval that overlaps LRF's on fresh images?
- **Reliance (no refit):** how much does the frozen LRF's fresh-image accuracy change when one feature group is set to its
  design-item mean?

Knockouts measure reliance of the frozen model (correlated groups cannot compensate without refit); single-source refits measure
sufficiency. Together they bracket "is it one detector". The words "sufficiency" and "reliance" in this section are planning labels
only; the paper names the blocks "single-source refits" and "knockouts" and uses none of the words barred in section 8 (SC-6 item 3). A leave-one-group-out refit was considered and excluded: it adds rows whose
reading is already bracketed by the two blocks above, at the cost of more intervals.

## 2. Feature partitions (by formula; fixed now)

The 35 features are `data.feature_names()` in the order of `runs/P2-LRF-FROZEN-LFIX/spec.json`.

**Partition S (source score; used for refits and knockouts).** Each feature is assigned to the raw caption-withheld score it is
computed from:

| Group | Formula of the raw score | Features (count) |
|---|---|---|
| S-BD | B (log p of the observed code, caption masked, K complementary masks), D (same, all image tokens masked), q = B - D | B, D, q, nb3mean_q, nb3mean_B, nb3min_q, nb5mean_q, rank_q, rank_B, itemmean_q, itemmean_B, itemsd_q, itemsd_B, itemz_q (14) |
| S-s3 | s3 = 1 - max_c p(c), same pass as B | s3, nb3mean_s3, rank_s3, itemmean_s3, itemsd_s3 (5) |
| S-tbv | tbv = log p(observed code), image visible, caption masked | tbv, nb3mean_tbv, rank_tbv, itemmean_tbv, itemsd_tbv (5) |
| S-ltex | ltex = log1p(max(patch texture, 0)), pixel domain | ltex, nb3mean_ltex, itemmean_ltex, itemsd_ltex (4) |
| S-nbr | nbr = distance of the code embedding to its grid neighbours' codes | nbr, nb3mean_nbr, itemmean_nbr, itemsd_nbr (4) |
| S-pos | grid position | row, col, rad (3) |

Total 35. In the paper the groups are named by these formulas only; S-BD is "features computed from B and D", never by any role.

**Partition F (formula type; knockouts only; the partition of Fig. 4 and the feature-group table):** token score (B, D, q, s3, tbv,
ltex, nbr; 7), position (3), neighbourhood (nb3mean_*, nb3min_q, nb5mean_q; 8), rank (4), item-level (itemmean_*, itemsd_*,
itemz_q; 13). Partition F is not used for refits: an item-level-only weighting is constant over the tokens of an item except for
itemz_q, so its decision is almost NONE's by construction and its refit would be uninformative.

## 3. The full variant list (fixed; 22 variants = 10 in block 3a (9 fitted + A-UNL) + 12 knockouts, plus the references NONE and LRF; every one reported)

References (already defined; not refitted): **NONE** (w_j = 1) and **LRF** (frozen, `runs/P2-LRF-FROZEN-LFIX`, model
`db7fdb4e...0f37`).

### 3a. Fitted and unlearned variants (design items only; 10 = 9 fitted + A-UNL)

All fitted variants use LRF's protocol unchanged except the stated difference: inputs `data.engineer` on the design arrays;
standardisation on the design items (restricted to the variant's columns); objective O1 = mean softplus(-M/T), M = sum_j w_j Delta_j /
sum_j w_j, T = median |NONE margin| over the training item-conditions; AdamW, mini-batch 32 item-conditions; all 4 training
conditions pooled (condition identity never an input); random search with synchronous successive halving, eta 3, 9 configurations,
rungs 4 / 13 / 40 epochs, 3 inner folds over all 500 design items, selection by mean inner-fold O1 (never accuracy; inner accuracies
are not stored, as in refreeze.py); refit on all 500 items with one seed.

| ID | Variant | Weight model | Search space | Why it is in the list |
|---|---|---|---|---|
| A-LIN | Linear logistic weight, 35 features | w_j = sigmoid(b + a^T x_j) (F1 with knots = 0) | the same 9 draws as LRF (knots, ridge, lr), knots overridden to 0; ridge and lr as drawn | Is the hinge (non-linear) part of the GAM needed? |
| A-S-BD | GAM on S-BD only | F1 on the 14 S-BD columns | LRF's 9 draws | Sufficiency of one source |
| A-S-s3 | GAM on S-s3 only | F1 on 5 columns | LRF's 9 draws | Sufficiency of one source |
| A-S-tbv | GAM on S-tbv only | F1 on 5 columns | LRF's 9 draws | R4's named candidate (tbv) |
| A-S-ltex | GAM on S-ltex only | F1 on 4 columns | LRF's 9 draws | Sufficiency of one source (pixel domain) |
| A-S-nbr | GAM on S-nbr only | F1 on 4 columns | LRF's 9 draws | R4's named candidate (nbr) |
| A-S-pos | GAM on S-pos only | F1 on 3 columns | LRF's 9 draws | Position prior only (no image content) |
| A-SF | Single-feature weight | F1 on one column; the column is chosen among the 35 by the inner-fold O1 of its own successive-halving run (ties: first in feature order) | LRF's 9 draws per column | The area chair's "single-feature weight", with the feature chosen on design items only. Its selection budget is 35 times LRF's (stated in S-VII) |
| A-MIL | Attention-weighted pooling in the style of gated attention MIL (Ilse et al., ICML 2018, arXiv 1802.04712; the paper says "in the style of", never "the attention-MIL baseline") | h_j = ReLU(W1 x_j + b1) (width d), dropout; e_j = v^T (tanh(V h_j) * sigmoid(U h_j)) (V, U: d x d); w_j = softmax over the 1024 tokens of the item-condition; v zero-initialised so training starts at NONE | d in {32, 64, 128}; dropout in {0, 0.1, 0.3}; weight decay log-uniform [1e-6, 1e-2]; lr log-uniform [3e-4, 3e-3] (the F3 space of the learned-ceiling plan); 9 configurations, rungs 4 / 13 / 40 | The area chair's "attention-MIL pooling baseline". It pools the per-token evidence Delta_j with learned attention over the same 35 caption-withheld features (an adaptation, not the original method: the instance classifier is the fixed evidence Delta_j and the bag label is replaced by the O1 objective, because no weight model may see Delta, the caption or the condition). Since M is scale-invariant, softmax weights enter O1 exactly as LRF's weights do |
| A-UNL | Unlearned rank weight on s3 (no fitting) | w_j = 1 - rank_s3_j, where rank_s3 is the LRF input feature "within-item percentile rank of s3" (data._rank) | none | The area chair's "unlearned reliability weight". The score s3 = 1 - max_c p(c) is an LRF input defined by formula; it is not the B - D statistic or any quantity derived from it. The direction (higher predictive confidence, larger weight) and the rank transform are fixed here by principle (scale-free, monotone, bounded in [0, 1]). The plan's author had seen the frozen LRF's shape functions (section 0 item 6); that the direction was not read from Fig. 4 is the author's account and cannot be verified; it was not read from any accuracy (SC-6 item 6) |

Notes. (i) A-UNL gives weight 0 to the single token of rank 1; sum_j w_j > 0 always. (ii) Single-feature variants on each of the 7
raw scores were considered and replaced by the source groups (S) plus A-SF: a raw score alone omits its item-level and neighbourhood
statistics, which is where an item-level noise detector would sit. (iii) An MLP weight (F3) is not repeated: it was in the exploratory
M4 cross-fit, and A-MIL covers the non-additive inductive bias.

### 3b. Knockouts of the frozen LRF (no refit; 12)

For a group G, the frozen LRF is evaluated with every standardised feature in G set to 0 (that is, to its design-item mean under the
stored mu, sd) after `data.engineer` and standardisation; all other features, a, b, c, knots unchanged. Rows: KO-S-BD, KO-S-s3,
KO-S-tbv, KO-S-ltex, KO-S-nbr, KO-S-pos (partition S; 6); KO-F-token, KO-F-position, KO-F-neighbourhood, KO-F-rank, KO-F-item
(partition F; 5); **KO-ALL** (all 35 set to 0; weights constant within an item, so its decisions must equal NONE's exactly). KO-ALL
stays in the list but is an exact-equality control with **no interval** (SC-2): S-VII reports it as a control line (decisions
identical: yes/no; count of differing items; pass rule in section 6 item 5). Its contrast against LRF would re-estimate the
preregistered LRF-vs-NONE contrast with other resamples and is not computed.

### 3c. Seed-spread refits (descriptive; S-VII only)

LRF's frozen object has one fit seed, and so does each refitted variant. To show the size of refit-seed variation beside the
between-variant intervals, each of the 9 fitted variants **and an LRF refit by the same harness** are refitted with two extra final seeds
(section 5 keys), with the configuration selected by the seed-0 search, and scored once. Reported (SC-7), per fitted variant, per
harness LRF refit and per cell: all three accuracies (seed 0 and the two extra seeds), their mean, standard deviation and range. Seed
0 is the pre-fixed seed (the one LRF used, `ss(4, 99, 0, 0)`), not the best of three; S-VII says so. S-VII also states that the extra
seeds repeat the final fit but not the configuration search or the choice of design items, so they understate refit variation. Never
an interval, never used to discount a difference, never instead of the seed-0 row; the LRF refits are labelled "seed-spread refits,
not the frozen LRF". These are not variants and do not enter V-G's table. (SC-4) S-VII also records the number of fresh items on
which the harness LRF refit at seed 0 decides differently from the frozen LRF (descriptive; R0 checks weights on design items only).

## 4. Endpoints (fresh fold only)

Cells (8): L1 clean, jpeg10, noise0.1, splice128 (n = 450 each); LG clean, shot_noise3, impulse_noise3, speckle_noise3 (n = 300
each). Primary negative only (`<cond>_delta`); the length-matched negative (`<cond>_deltaL`) is not used.

Estimand (SC-1): for variant v, reference r (NONE or frozen LRF) and cell c, d = mean over the cell's items of (y_v - y_r), y in
{0, 1}, ties wrong; this equals (b - c)/n for the cell. Sign: variant minus reference; positive favours the variant. Interval: paired
percentile bootstrap, 10,000 item resamples, 95% level only (`np.quantile` at 0.025 and 0.975). The interval covers item sampling only
(not refit-seed variation, not design-item sampling).

Per variant v (21 interval rows: the 22 variants except KO-ALL) and cell: accuracy; d against NONE; d against the frozen LRF; each with
its 95% interval; the discordant counts b and c (descriptive). An interval that is exactly [0, 0] (b = c = 0) is printed as computed,
with its b and c, and counted in K. The cell n is taken from the data and must equal the n of `a6_analysis.json` for that cell's
LRF-vs-NONE contrast (same exclusions); S-VII prints n per cell. For the LRF row, accuracy only; its interval against NONE is the one of the preregistered Study 2 table
(`a6_analysis.json`) and is not recomputed here, so the paper never carries two intervals for the same contrast.

Count: K = 21 rows x 8 cells x 2 contrasts = **336** intervals (SC-2); K is read from the output. Mandatory S-VII text (SC-1,
verbatim with K filled in):

> "Each interval is a marginal 95% interval. {K} intervals were computed from the same images (variants x cells x two contrasts); they
> are positively dependent and no familywise or false-discovery adjustment was made. If every true difference were zero, about 5% of
> them (about {0.05 K}) would still exclude zero, and the count of intervals that exclude zero is not a calibrated tally because of the
> dependence. An interval that excludes zero is therefore a descriptive observation, not a finding; patterns across rows and cells are
> described, single intervals are not claims. The intervals cover item sampling only: refit-seed variation and design-item sampling are
> not in them."

No binomial statement about the count, and no Holm or other adjustment is applied or implied. Planning arithmetic only (SC-9; not a
result, not for the paper): with about 12% discordant items at n = 450 the 95% half-width of d is about 1.96 sqrt(0.12 / 450) = 0.03;
the observed LRF-vs-NONE discordance (85/450 in L1 noise0.1, 46 to 58 of 300 in the LG cells) puts the half-width at about 0.05 in the
LG cells for a variant that differs from LRF as much as LRF differs from NONE. So differences below about 3 points in L1 and about 5
points in the LG cells are not resolvable (planning values only, not for the paper). Wherever an interval contains zero, the text
says "an interval that contains zero does not show that the difference is zero" (SC-6 item 1).

No row or column is dropped from V-G; S-VII holds every interval (SC-5).

Main-text table (V-G): rows = the 22 variants plus NONE and LRF (24); columns = accuracy and net difference against LRF [95% interval] in the cells of the
preregistered Study 2 tests (L1 noise0.1, L1 clean, L1 jpeg10, L1 splice128, LG shot, LG impulse, LG speckle), NONE as an accuracy
row, KO-ALL as a control line without interval. LG clean, all intervals against NONE, discordant counts and the seed-spread values go
to S-VII. No bold, no underline, no ranking, no sorting by result (row order is the order of section 3). Mandatory V-G caption
clauses: "differences are variant minus reference; positive favours the variant" (SC-6 item 2) and "each row is one refit seed with
the configuration chosen by the design-item search; the intervals cover item sampling only" (SC-7).

### Seed slot

Bootstrap: `numpy.random.SeedSequence(20261028, spawn_key=(35,))` spawned into 8 children in the fixed cell order L1_clean,
L1_jpeg10, L1_noise0.1, L1_splice128, LG_clean, LG_shot_noise3, LG_impulse_noise3, LG_speckle_noise3. One child per cell draws one
10,000 x n index matrix, used for every row and both contrasts in that cell (common resamples; no slot depends on the variant list).
Implementation (SC-3): `a6_analysis.boot_ci` draws its own indices inside each call, so it is not called with a shared generator.
Either (a) a wrapper re-creates `np.random.default_rng(<cell child>)` for every call (identical stream, hence identical indices for
the same n), or (b) a new function takes the precomputed index matrix; `levels=(0.95,)`. A unit test checks that two calls in one cell
use identical indices and that the NONE and LRF contrasts of one variant use the same indices. `ablation_analysis.json` `meta` pins
the root, spawn key, child keys (35, 0..7), cell order and numpy version, as `a6_analysis` does.
Checked unused on 2026-10-30: under root 20261028, (32,) is tier3_fusion, (33,) h_strata, (34,) a6_analysis with children (34, 0..13)
(baselines.py uses (34, 13)); seeds.py spawns children 0..31 by position; a repository search for spawn key 35 found only array-shape
tuples `(35,)` in `paper2-tnnls/scripts/fig4_study2_weights.py:45` and `tests/exp_p2/test_gate_lrf_score.py:82`, no seed use.

## 5. Fitting seeds and determinism

All fits use the learned-ceiling stream `SeedSequence(20261029, spawn_key=...)` (`run.ss`) with LRF's keys, so every variant sees
the same inner folds, the same configuration draws (where the space is shared) and the same fit seeds as LRF (common random numbers):
inner folds `ss(1, 99)`; configuration draws `ss(2, 99, 0)`; inner fits `ss(3, 99, 0, ci, ii)`; final fit `ss(4, 99, 0, 0)` =
316748921 (verified to equal spec.json `seed`); seed-spread refits `ss(4, 99, 0, 1)` and `ss(4, 99, 0, 2)`. A-MIL uses the same keys
with its own `sample()`. CPU only (`CUDA_VISIBLE_DEVICES=""`), torch and BLAS at 4 threads, as the re-freeze.

## 6. Leakage controls and stop rules

1. **R0 harness reproduction (before anything else):** the ablation harness, run with all 35 features and the F1 space, must
   reproduce the frozen LRF: same selected configuration and inner O1 as spec.json, and max |w_harness - w_frozen| <= 1e-5 over the
   design items x 4 conditions (the numpy-versus-torch self-check was 3.8e-7). Failure: stop, audit, nothing is scored. An R0
   failure never changes section 3 (SC-5).
2. Fit stage reads only `runs/P2-LRF-RESCORE/arrays` and verifies its digest against spec.json `rescored_arrays_digest` before
   loading. It computes and stores no accuracy, decision count or margin on design items (O1 only, as refreeze.py).
3. Freeze: each variant writes `runs/P2-LRF-ABL-FIT/<ID>/{model.npz, spec.json, hpo.json}`; `runs/P2-LRF-ABL-FIT/HASHES.json` lists
   SHA-256 of every model.npz and spec.json, of the ablation code, of the pinned learned-ceiling files (unchanged; must equal
   spec.json `code_sha256`) and the variant list of section 3. HASHES.json is committed (code pin recorded) **before** the score stage.
4. Score stage refuses unless HASHES.json is tracked and unmodified in git and every hash matches; reads only the fresh arrays and
   `predictions.jsonl` (fields y_none, y_lrf only, for the positive controls); reuses `lrf_score`'s decision rule verbatim:
   Y = 1[sum_j w_j Delta_j > 0], tie = wrong, any non-finite feature, weight, score or margin raises NonFinite and stops (never a
   wrong decision).
5. **Positive controls on fresh items, run first (SC-4):** the score stage computes and writes `controls.json` before it computes any
   variant weighting: recomputed NONE equals `y_none`; LRF recomputed by the ablation scorer equals `y_lrf`; KO-ALL equals NONE. Pass
   rule: identical decisions on every item and cell. For KO-ALL only, a difference is allowed on items with
   |sum_j Delta_j| <= 1e-9 x sum_j |Delta_j| (float rounding of a sum that is zero in exact arithmetic), counted and printed in
   controls.json. Any other mismatch halts with no variant output on disk.
6. Runs once. No variant is refitted, retuned or re-selected after any fresh score exists (rerun rule and no-promotion rule: section 0
   item 1). Fresh arrays are verified against `arrays_manifest.json` before reading. The `analyse` stage writes `ablation_analysis.json`
   in section 3 row order, with no sorting, no ranking and no "interval above/below zero" flag (SC-5).

## 7. Code and run plan (not implemented)

- Module `analysis/paper2/lrf/ablation.py` (outside pinned `exp_p2/` and without editing the hash-pinned
  `analysis_posthoc/learned_ceiling/*`), subcommands `fit`, `score`, `analyse`. It imports `data`, `families`, `run.successive_halving`
  and subclasses `families.TorchFamily`: `GAMCols(cols)` (uses the existing `cols` hook), `GAMLin` (F1 sampling, knots forced 0),
  `AttnMIL` (own training loop identical to `_train_o1` except the weight transform is a softmax over tokens). Bootstrap: a wrapper
  around `a6_analysis.boot_ci` that re-creates the cell's generator per call, or a new function on a shared index matrix (section 4,
  SC-3). Decision and non-finite rules imported from `exp_p2.gate.lrf_score` (`decide`).
- Tests `tests/analysis_lrf/test_ablation.py` on synthetic arrays only (no real design or fresh arrays): partition covers 35 features
  exactly once; KO-ALL equals NONE; GAMLin with knots 0 equals F1 knots 0; AttnMIL with zero v equals NONE; scorer refuses on hash
  mismatch, on a GATE field request and on non-finite input; seed slot children fixed; common resamples (two calls in one cell, and
  the NONE and LRF contrasts of one variant, use identical indices); controls.json written before any variant weighting and a control
  mismatch leaves no variant output; KO-ALL float-tie tolerance; R0 logic on a toy model.
- Run directories: `runs/P2-LRF-ABL-FIT` (fit, R0, seed-spread refits, HASHES.json), `runs/P2-LRF-ABL-SCORE` (predictions_ablation.jsonl
  one line per item x cell x weighting with y and margin; controls.json; ablation_analysis.json; env-lock.txt written before the run;
  stdout log with wall-clock per stage).

Commands (Git Bash; venv Python; CPU):

```bash
PY="C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv/Scripts/python.exe"
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
"$PY" -m pip freeze > runs/P2-LRF-ABL-FIT/env-lock.txt
"$PY" -m analysis.paper2.lrf.ablation fit --src runs/P2-LRF-RESCORE --frozen runs/P2-LRF-FROZEN-LFIX --out runs/P2-LRF-ABL-FIT
# commit runs/P2-LRF-ABL-FIT/{HASHES.json, */spec.json, */hpo.json, R0.json} and the code; record the pin
"$PY" -m analysis.paper2.lrf.ablation score --fit runs/P2-LRF-ABL-FIT --l1 runs/P2-LRF-L1 --lg runs/P2-LRF-LG --out runs/P2-LRF-ABL-SCORE
"$PY" -m analysis.paper2.lrf.ablation analyse --score runs/P2-LRF-ABL-SCORE
```

### CPU estimate (from measured logs; 4 threads)

| Stage | Measured basis | Estimate |
|---|---|---|
| Load + engineer + R0 (full LRF protocol) | `P2-LRF-FROZEN-LFIX/selfcheck.json` sec 189.6 (whole re-freeze; HPO log sum 155.0 s over 39 fits) | 3-4 min |
| A-LIN | knots-0 fits at rung 4 took 0.74-0.87 s vs 2.4-3.1 s with knots (hpo.json) | <= 3 min |
| A-S-* (6) | each a subset of LRF's 35 columns, so at most LRF's cost | <= 19 min (bound 6 x 190 s) |
| A-SF (35 searches) | 345 epoch-units per search (27x4 + 9x13 + 3x40); 35-feature knots-0 rate about 0.2 s per epoch-unit | <= 40-45 min |
| A-MIL | F3 MLP learned-ceiling folds: sec_total 460, 576, 647, 672, 1509 s (400 items, rmax 30, 3 final seeds); scale x1.25 items, x1.33 epochs | about 18 min (median), <= 42 min |
| Seed-spread refits (10 objects x 2 seeds) | final GAM fit on 500 items about 25 s; A-MIL final fit a few minutes | <= 15 min |
| Score + analyse (24 weightings + 20 seed-spread, 750 items x 4 conditions; 336 intervals) | not measured (lrf_score logs no timing); numpy GAM inference in chunks of 10 items | <= 20 min (unmeasured bound) |
| **Total** | | **about 1.5 h typical, <= 2.5 h worst case; no GPU** |

## 8. Wording the paper may use (V-G and S-VII), per outcome pattern

Every V-G sentence opens with or sits under the label "exploratory; added after the primary, family H and Study 2 results". All
numbers come from `runs/P2-LRF-ABL-SCORE/ablation_analysis.json` with `% run:` comments. No sentence uses any word of SPEC rule 5
(including "outperform", "better than", "beats", "competitive", "robust", "generalises", "validated", "confirmed", "explains",
"accounts for", "is consistent with", "predicts", "equivalent", "as good as") and no sentence names a Study 1 object. Also barred in
the paper (SC-6 item 3): "reliance", "relies", "carry", "carries", "sufficiency", "sufficient", "needed", "necessary", "drives",
"responsible for", "powered", "equality". Blocks are named "single-source refits" and "knockouts". Every V-G caption states the sign:
"differences are variant minus reference; positive favours the variant". Every knockout description carries the sentence: "Setting a
group to its mean gives inputs that the model did not see together in fitting; an interval away from zero shows that the frozen
model's decisions depend on those inputs, not that the group alone detects anything."

| Pattern (L1 noise0.1 unless stated) | Permitted wording |
|---|---|
| A single-source variant A-S-g: interval against LRF contains 0 | "Weighting by the features computed from g alone gave an accuracy of x; its paired difference from the frozen LRF was d [lo, hi], an interval that contains zero. An interval that contains zero does not show that the difference is zero." |
| Every single-source variant: interval against LRF lies below 0 | "For each single-source weighting, the 95% interval of the paired difference from the frozen LRF lay below zero (Table N)." |
| Some below, some containing 0 | Name each group in each class; no summary adjective. |
| A-SF | "The single-feature weight (feature f, chosen from 35 candidate features by the inner-fold objective on the design items, a selection budget 35 times that of the frozen LRF; the selection used no fresh item) had a paired difference from LRF of d [lo, hi]." The bracketed clause is mandatory (SC-8). |
| A-LIN | "Removing the hinge terms (a linear logit on the same 35 features) gave a paired difference from LRF of d [lo, hi]." |
| A-MIL | "Attention-weighted pooling in the style of gated attention MIL (Ilse et al., 2018), fitted with the same objective, design items and tuning budget, had a paired difference from LRF of d [lo, hi]." |
| A-UNL | "The unlearned rank weight on s3 had a paired difference from NONE of d1 [lo, hi] and from LRF of d2 [lo, hi]; the direction and the rank transform were fixed by the plan's author, who had seen the frozen LRF's shape functions; they were not read from an accuracy." |
| Any contrast against NONE (S-VII only; SC-6 item 5) | "The paired difference from no weighting was d [lo, hi]." |
| Any variant: interval against LRF lies above 0 | Reported with the same sentence form as above ("lay above zero"), plus: "This comparison was added after the Study 2 results and is not a test." No adjective; never in Discussion as a recommendation. |
| Knockouts: one group's knockout interval (vs LRF) clearly away from 0, others contain 0 | "The change in the frozen model's accuracy when the g features are set to their design-item mean was d [lo, hi]; for every other group the interval contained zero." Followed by the knockout sentence above. Not "the gain comes from g", not "LRF relies on g to detect noise". |
| Knockouts: several groups away from 0 | List each with its interval, in section 3 order. |
| Knockouts: none away from 0 | "No single-group knockout moved the frozen LRF's accuracy by an amount its interval could separate from zero." |
| Knockout vs refit disagree (e.g., KO-S-nbr away from 0 but A-S-nbr far below LRF) | "A knockout changes the inputs of the frozen model; a single-source refit fits a new weighting on one group. The two blocks differ for g." No reconciling mechanism claimed. |
| Other cells (clean, jpeg10, splice128, LG) | Only in the same descriptive form, cell by cell, never pooled ("across corruptions" banned). |
| Seed spread | "Across the three refit seeds, the range of fresh-fold accuracy was at most r in every variant and cell (S-VII lists each)." r is the maximum range over variants and cells. Seed 0 is the pre-fixed seed, not the best of three. Never used to discount a difference. |

Mandatory S-VII sentences: the label; the disclosure of section 0 items 6 and 7 (including SC-8's sentence that the list was fixed
after the fresh LRF and NONE results were seen, and the LG-L1 image overlap); the SC-1 paragraph of section 4 with K = 336; "no
ablation was preregistered"; the A-SF selection-budget clause; n per cell; the SC-7 seed statements (seed 0 pre-fixed; extra seeds
repeat only the final fit, so they understate refit variation); the KO-ALL control line ("KO-ALL reproduced NONE on every item" only if
it did, else the count of differing items); the number of fresh items on which the harness LRF refit differs from the frozen LRF; "an
interval that contains zero does not show that the difference is zero".

## 9. Deviations box entry (SPEC 8)

"Tier-3 ablation (exploratory; added after the primary, family H and Study 2 results): plan research/paper2/tnnls/ABLATION-PLAN-2026-10-30.md
committed <SHA> before any variant was scored on fresh items; variants fitted only on the 500 design items; every variant reported;
intervals only."

claims:
  - statement: "Spawn key (35,) under root 20261028 is unused by any analysis seed in the repository."
    status: supported
    evidence: "repo search 2026-10-30 (sections 4); a6_analysis.py:32, h_strata.py:29, tier3_fusion.py:45, seeds.py ANALYSES"
    level: E3
    confidence: 0.9
  - statement: "LRF's final-fit seed key ss(4, 99, 0, 0) gives 316748921, equal to spec.json seed."
    status: supported
    evidence: "python SeedSequence(20261029, spawn_key=(4,99,0,0)).generate_state(1) run 2026-10-30; runs/P2-LRF-FROZEN-LFIX/spec.json"
    level: E3
    confidence: 0.99
unknowns:
  - "Scoring-stage wall clock is not measured (bound only)."
  - "Whether the harness reproduces the frozen model to 1e-5 (R0) is untested until the fit stage runs."
next_test: {hypothesis: "none (exploratory)", intervention: "statistician check of this plan, commit, implement, R0, fit, commit hashes, score once", primary_metric: "none (intervals only)", falsifier: "none", gpu_hours: 0}

---

# Statistician check (2026-10-30)

agent: statistician
verdict: **APPROVE WITH CHANGES.** The plan may be committed once changes SC-1 to SC-9 are written into it (text edits and code requirements; no
variant is added, removed or renamed, so section 3 stands). Nothing was scored or fitted by this check. Confidence 0.8.
Read: this plan in full; SPEC.md sections 0 (rules 3, 5) and 6; red-team V2-2; `exp_p2/gate/seeds.py`; `analysis/paper2/lrf/a6_analysis.py` (slots, `boot_ci`);
`runs/P2-LRF-FROZEN-LFIX/spec.json` (feature names); `runs/P2-LRF-L1/a6_analysis.json`, `runs/P2-LRF-LG/a6_analysis.json` (cell n, discordance);
a repository-wide grep for `spawn_key`, `SeedSequence`, `ss(`. Not read: fresh arrays, design arrays, the learned-ceiling `families.py` internals.

## What was verified (source facts)

| Check | Result | Evidence |
|---|---|---|
| Counts | 22 = 10 (3a) + 12 (3b), excluding NONE and LRF; 22 x 8 x 2 = 352 | plan sections 3, 4 |
| Feature partitions S and F each cover the 35 features exactly once | yes (14+5+5+4+4+3; 7+3+8+4+13) | compared with `spec.json` `features` (35 names) |
| Seed slot `SeedSequence(20261028, spawn_key=(35,))` unused | yes. `seeds.ANALYSES` has 32 names, so `spawn(32)` takes (0,)..(31,); (32,) tier3_fusion; (33,) h_strata; (34,) a6_analysis with children (34, 0..13), baselines (34, 13). No file uses a key starting with 35. The learned-ceiling stream is a different root (20261029). | `seeds.py`, `tier3_fusion.py:45`, `h_strata.py:29`, `a6_analysis.py:32`, `baselines.py:74`, `run.py:43` |
| Refit keys `ss(4, 99, 0, 1)` and `ss(4, 99, 0, 2)` unused | yes: `run.py:115` uses `ss(4, k, fi, s)` with outer folds k = 0..4; `lrf.py` uses `ss(4, 99, 0, 0)` only | grep |
| Cell n | L1 cells 450 each; LG cells 300 each (impulse, shot, speckle) | `a6_analysis.json` files |
| Study 1 objects | none in the variant list; S-BD is a feature source named by formula (SPEC rule 3); no hard-gate or threshold row | plan sections 0, 2, 3 |
| Fitting data | design arrays only; fresh arrays enter at the score stage only | plan sections 0 item 3, 6 |

## Changes (exact; apply before commit)

**SC-1. Interval method and a familywise caveat (section 4; mandatory S-VII text).**
Estimand: for variant v, reference r (NONE or frozen LRF), cell c: d = mean over the cell's items of (y_v - y_r), y in {0,1}, ties wrong; this is
(b - c)/n for the cell. Interval: paired percentile bootstrap, 10,000 item resamples, 95% level only, `np.quantile` at 0.025 and 0.975. The interval
covers item sampling only (see SC-7). Replace the sentence "S-VII states this count and that, with no true differences, about 5% ..." by:

> "Each interval is a marginal 95% interval. {K} intervals were computed from the same images (variants x cells x two contrasts); they are positively
> dependent and no familywise or false-discovery adjustment was made. If every true difference were zero, about 5% of them (about {0.05 K}) would
> still exclude zero, and the count of intervals that exclude zero is not a calibrated tally because of the dependence. An interval that excludes zero
> is therefore a descriptive observation, not a finding; patterns across rows and cells are described, single intervals are not claims. The intervals
> cover item sampling only: refit-seed variation and design-item sampling are not in them."

K is read from the output (see SC-2). The expectation 0.05 K holds under dependence; the distribution of the count does not, which is why no binomial
statement is made. No Holm or other adjustment is applied or implied (everything not preregistered is exploratory).

**SC-2. KO-ALL is a control, not a row of intervals.** KO-ALL vs NONE is an exact-equality control (SC-4) with no interval. KO-ALL vs LRF would be the
preregistered LRF-vs-NONE contrast negated, re-estimated with other resamples, which breaks the plan's own rule that the paper carries one interval
per contrast. Report KO-ALL in S-VII as a control line (decisions identical: yes/no, count of differing items). The interval count becomes
21 x 8 x 2 = **336** (K = 336, about 17 expected to exclude zero). Section 3's list still has KO-ALL; only its reporting changes. Any interval that is
exactly [0, 0] (b = c = 0 for a knockout or variant) is printed as computed with its b and c, and is counted in K.

**SC-3. Common resamples must be implemented as stated; `boot_ci` does not do it as written.** `a6_analysis.boot_ci(diff, rng, ...)` draws its own
index matrix inside the call, in chunks of 1000. It does not accept a shared matrix. The plan's "one 10,000 x n matrix per cell, used for every row and
both contrasts" therefore needs either (a) a wrapper that re-creates `np.random.default_rng(<cell child>)` for every call (identical stream, hence
identical indices when n is the same), or (b) a new function taking a precomputed index matrix. Requirements: the cell's n is taken from the data and must
equal the n of `a6_analysis.json` for the LRF-vs-NONE contrast in that cell (same exclusions); use `levels=(0.95,)`; a unit test that two
calls in one cell use identical indices, and that the NONE contrast and the LRF contrast of one variant use the same indices. Pin the child keys
(35, 0..7) in `ablation_analysis.json` `meta` (root, spawn key, cell order, numpy version), as `a6_analysis` does.

**SC-4. Controls run first, before any variant row exists.** The score stage computes and writes `controls.json` (recomputed NONE = `y_none`; the
scorer's LRF = `y_lrf`; KO-ALL = NONE) before computing any variant weighting; a mismatch halts with no variant output on disk. KO-ALL equality is
exact except where float rounding can flip the sign of a sum that is zero in exact arithmetic. Pass rule: identical decisions on every item and cell; a
difference is permitted only on items with |sum_j Delta_j| <= 1e-9 x sum_j |Delta_j|, counted and printed in controls.json; any other difference halts.
Also record, in S-VII, the number of fresh items on which the harness-refit LRF (seed-spread, seed 0) decides differently from the frozen LRF
(descriptive; R0 only checks weights on design items).

**SC-5. Mechanical definition of a rerun (section 0 item 1 and section 6 item 6).** "A defect is fixed by a rerun beside the first" applies only to
(i) an exception or NonFinite stop, (ii) a control mismatch, (iii) a hash mismatch, (iv) a code bug shown by a unit test. It never applies because a
result looks unexpected. Every rerun is reported with its reason. The `analyse` stage writes `ablation_analysis.json` in the section 3 row order, with no
sorting, no ranking, no "interval above/below zero" flag; and, as for A6, no output is read before the run is complete. After the score stage no
variant is promoted: the Study 2 object stays the frozen LRF whatever the intervals show, and no selected variant is scored again on these fresh items
(the fresh fold is spent; any confirmation would need new items and a new preregistration). Add this paragraph to section 0. Add to section 6 item 1:
"an R0 failure never changes section 3". Add to section 4: "no row or column is dropped from V-G; S-VII holds every interval".

**SC-6. Wording (section 8) against SPEC rule 5.** Fixes:
1. Delete "The ablation was not powered to show equality" (a power claim without a power calculation, and "equality" invites the barred
   "equivalent"). Replace by: "An interval that contains zero does not show that the difference is zero." Also in the S-VII mandatory text.
2. State the sign once in every V-G caption: "differences are variant minus reference; positive favours the variant".
3. In the paper, the words "reliance", "relies", "carry", "carries", "sufficiency", "sufficient", "needed", "necessary", "drives" and "responsible for" are
   not used (section 1 headings are planning labels only). Blocks are named "single-source refits" and "knockouts". A knockout row is described as
   "the change in the frozen model's accuracy when the g features are set to their design-item mean". Add the sentence: "Setting a group to its mean gives
   inputs that the model did not see together in fitting; an interval away from zero shows that the frozen model's decisions depend on those inputs, not that
   the group alone detects anything." (This keeps the knockout row from becoming a claim about what the weights track, F12.)
4. Seed-spread sentence: replace "changed fresh-fold accuracy by at most r" by "Across the three refit seeds, the range of fresh-fold accuracy was at most
   r in every variant and cell (S-VII lists each)." r is the maximum over variants and cells and is defined that way.
5. Add the template for contrasts against NONE (S-VII only): "The paired difference from no weighting was d [lo, hi]."
6. For A-UNL add: "the direction and the rank transform were fixed by the plan's author, who had seen the frozen LRF's shape functions
   (section 0 item 6); they were not read from an accuracy". The plan asserts the direction was not read from Fig. 4; that cannot be
   verified, so it is stated as the author's account.

**SC-7. Seed-spread refits (section 3c) and the single-seed rows (V-G caption).** Report for each fitted variant and the harness LRF refit all three
accuracies per cell (seed 0, plus the two extra seeds), their mean and standard deviation, and the range. Seed 0 is the pre-fixed seed (the one LRF
used, `ss(4, 99, 0, 0)`), not the best of three; say so (selection rule). The V-G caption adds: "each row is one refit seed with the configuration
chosen by the design-item search; the intervals cover item sampling only". State in S-VII that the extra seeds repeat the final fit but not the
configuration search or the choice of design items, so they understate refit variation. Never an interval, never used to discount a difference (as planned).

**SC-8. Disclosure and selection budget.** Keep section 0 item 6. Add: the variant list was fixed after the lead had seen the fresh LRF and NONE
results; no variant was fitted or scored before the list was committed. A-SF sentence (mandatory): "chosen from 35 candidate features by the inner-fold
objective on the design items, a selection budget 35 times that of the frozen LRF; the selection used no fresh item." Write the cell n used per cell
(from the data) in S-VII. Add "the response to reviewers" to the section 0 item 4 exclusion list.

**SC-9. Planning arithmetic (section 4, not for the paper).** "About 12% discordant, half-width about 0.03" is the L1 clean/jpeg/splice scale. Observed
LRF-vs-NONE discordance is 85/450 in L1 noise and 46 to 58 of 300 in the LG cells, where the half-width is about 0.05 for a variant that differs from
LRF as much as LRF differs from NONE. Replace "differences below about 3 points cannot be resolved" by "about 3 points in L1 and about 5 points in the LG
cells (planning values only, not for the paper)". Not a requirement on any analysis.

## Items checked and passed without change

- **Estimands and pairing.** Paired item-level net differences against NONE and against the frozen LRF; common resamples (once SC-3 is done); the LRF-vs-NONE
  interval is not recomputed (the preregistered one stands). Point estimates are additive across the two contrasts; intervals are not, and the paper
  does not subtract intervals.
- **R0 reproduction control.** Same configuration and inner objective as `spec.json`, max |w difference| <= 1e-5 against a 3.8e-7 self-check. Adequate.
- **Leakage.** Fitting, standardisation, token subsample, configuration choice and A-SF's feature choice use the 500 design items only; hash file
  committed and verified before the score stage; fresh arrays checked against the manifest; non-finite values stop the run. No fresh item enters any choice.
- **Seed slot.** Free; see the table. The learned-ceiling keys for the extra seeds are free.
- **No Study 1 object.** Passed (no gate flag, no threshold row, no "hard versus soft" framing, scorer refuses GATE fields).
- **Placement.** Section 0 item 4 lists title, abstract, highlights, conclusion, contributions, cover letter, README top section and Zenodo description (V2-2 (e)).
- **Outcome-wording table.** After SC-6 it contains none of the SPEC rule 5 words ("better than", "outperform", "beats", "competitive", "robust",
  "generalises", "validated", "confirmed", "explains", "accounts for", "is consistent with", "predicts", "equivalent", "as good as", "trend", "across
  corruptions"). The knockout pattern correctly bars "the gain comes from g".

## How the lead could still pick a variant by its fresh result, and the block

1. A rerun justified by an unexpected result: blocked by SC-5.
2. Reordering or subsetting the V-G table after seeing intervals: row order is section 3, the cell list is fixed in section 4; SC-5 makes "no row or column dropped" explicit.
3. Promoting a variant whose interval lies above zero: blocked by SC-5 (LRF stays the object) and by the existing sentence "this comparison ... is not a test".
4. Choosing seeds: seed 0 is pre-fixed (SC-7).
5. Choosing which of the 336 intervals to quote: SC-1 forbids single-interval claims; the paper quotes the table or the per-class sentences of section 8.

## Concerns

- A-MIL: the plan calls it the "closest faithful adaptation" of Ilse et al. The instance classifier is the fixed evidence Delta_j and the bag label is
  replaced by the O1 objective, so the paper should say "attention-weighted pooling in the style of gated attention MIL (Ilse et al., 2018)", not
  "the attention-MIL baseline". Wording only; the arXiv 1802.04712 citation was not re-verified by this check.
- LG cells and L1 cells come from the same fresh images if LG is a prefix of the fresh fold (A6 line 161; not verified in the arrays), so the 8 cells are dependent too.
- With the observed discordance, differences below about 3 to 5 points are not separable, so any "no difference from LRF" reading is only "interval contains zero".

---

# Changes applied (ml-expert, 2026-10-30, after the statistician check)

The 22-variant list of section 3 is unchanged. The statistician section above is kept as the record. Nothing was implemented, fitted or scored.

- SC-1: estimand, sign, 95% percentile method and the mandatory familywise/dependence paragraph (section 4).
- SC-2: KO-ALL is an exact-equality control with no interval (section 3b); K = 21 x 8 x 2 = 336 (sections 4, 7); [0, 0] intervals printed and counted.
- SC-3: shared per-cell resamples via a per-call generator wrapper or a precomputed index matrix, levels (0.95,), unit test, seed meta pinned (section 4 seed slot; section 7).
- SC-4: controls.json written before any variant weighting; KO-ALL float-tie tolerance 1e-9 x sum |Delta|; any other mismatch halts (section 6 item 5); harness-refit-vs-frozen LRF disagreement count reported (section 3c).
- SC-5: mechanical rerun rule, "LRF stays the object, no promotion", fresh fold spent (section 0 item 1); "an R0 failure never changes section 3" (section 6 item 1); unsorted, flag-free analysis output (section 6 item 6); no row or column dropped (section 4).
- SC-6: "not powered to show equality" removed; zero-interval sentence; sign stated in captions; reliance/carry/sufficiency and related words barred in the paper; knockout sentence; NONE-contrast template; A-UNL direction as the author's account (sections 1, 3a, 8).
- SC-7: all three seed accuracies with mean, SD and range; seed 0 pre-fixed, not best; extra seeds understate refit variation; V-G caption clause (sections 3c, 4, 8).
- SC-8: list-fixed-after-results disclosure (section 0 item 6); mandatory A-SF budget clause (section 8); n per cell in S-VII (section 4); response to reviewers added to the exclusion list (section 0 item 4).
- SC-9: planning half-widths about 3 points (L1) and about 5 points (LG), planning values only (section 4).
- Concerns: A-MIL called "in the style of" gated attention MIL (Ilse et al.) (sections 3a, 8); LG-L1 image overlap recorded and disclosed, "the eight cells are not independent samples" (section 0 item 7).
