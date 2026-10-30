# Baseline inventory for Paper 2 (TNNLS), 2026-10-30

Read-only audit of committed run files. No GPU, no training, no new test. Every number below is quoted from a stored analysis file
(file:key given) or derived from stored per-item predictions by `analysis_posthoc/baseline_inventory_2026-10-30.py` (standard library only;
output `analysis_posthoc/baseline_inventory_2026-10-30.out.json`). The script asserts that each derived accuracy equals the stored number
wherever one exists (a6_analysis.json for NONE/LRF/GATE-M; ablation_analysis.json for all 24 weightings; analysis.json for the Study 1 arms).
All run paths are relative to the repository root. "Acc" is accuracy of the image-direction decision (ties wrong); no new interval is computed.

## 0. Four findings that change how the table can be written

1. **The preregistration forbids the table Shlok wants, as it stands.** `SAP-ADDENDUM-A6-LRF-2026-10-29.md` line 208-215 (A6.6): CLIP/SigLIP
   are "descriptive; no test; own table"; "No test against LRF, no ranking words, no column of LRF numbers inside that table". Line 171
   (A6.4): the fresh-fold GATE-M arm is "supplement-only, descriptive, without a guarantee". Line 307-308 (A6.12 must-not): "any comparison of
   LRF with GATE-M or with CLIP/SigLIP". Line 303: no figure or table holds both GATE-M and LRF numbers. The paper (`sections/study2.tex`,
   header lines 5-8) keeps that rule: Table III (CLIP/SigLIP) has no ranking and no LRF column. A single table with best/second best marked
   across NONE, GATE-M, LRF and the encoders needs a dated amendment (A6 r2 or a deviation row) disclosed in Methods. This is a decision for
   Shlok, not a data question.
2. **LRF is not the best row in most cells once the exploratory variants are on the same items.** On the fresh fold (n = 450) LRF is highest
   only on Gaussian noise (0.802; the B/D-only GAM `A-S-BD` is 0.800, difference -0.002, 95% interval -0.033 to 0.029). The linear logit on the
   same 35 features (`A-LIN`) is highest on JPEG (0.884 vs 0.864; difference +0.020, 0.004 to 0.038, unadjusted) and splice (0.931 vs 0.927);
   `A-S-BD` is highest on clean (0.922). On the noise cell, the 95% interval of variant minus NONE excludes 0 (positive) for A-LIN, A-S-BD, A-S-s3, A-S-tbv and A-MIL
   and contains 0 for the unlearned rank weight (`A-UNL`), the single-feature weight (`A-SF`), A-S-ltex, A-S-nbr and A-S-pos (`ablation_analysis.json:rows[*].cells.L1_noise0.1.vs_NONE.ci95`).
   The supportable message is "learned weighting beats the unweighted sum and simple unlearned weights", not "this functional form is the best". Source: section 1A.
3. **A pixel denoiser beat every weighting on Study 1's noise cell.** On the 500 Study 1 test items, NLM-denoised input + the unweighted rule
   reached 0.852 on noise 0.1 against 0.676 (none) and 0.778 (best cross-fitted learned weighting, exploratory). It has not been run on the
   fresh fold, so it is absent from any Study 2 comparison. A reviewer will ask. Source: section 1B and section 4.
4. **Selection and dependence.** Of the 21 variant rows only LRF was frozen before data; the others were specified and scored after the primary
   and Study 2 results (`ABLATION-PLAN-2026-10-30.md` line 6, 373). Any "best / second best" mark among variants is therefore a posteriori. The
   eight cells are not independent (the 300 LG images are the first 300 of the 450 L1 images: `runs/P2-LRF-ABL-SCORE/controls.json:lg_l1_image_overlap`),
   and the 336 ablation intervals are unadjusted (`ablation_analysis.json:mandatory_text_sc1`).

## 1. Inventory: every method with results on the same items

### 1A. Study 2 fresh fold (COCO val2017, 450 images; LG cells 300 images; one pass, same items for every row)

Cells: clean, Gaussian noise 0.1 (primary L1), JPEG q10, splice 128 (n = 450); then shot, impulse, speckle (severity 3) and clean-300 (n = 300).
LG clean is the clean accuracy on the first 300 items.

| Row | Family | noise0.1 | jpeg10 | splice128 | clean | LG shot | LG impulse | LG speckle | LG clean | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| NONE (unweighted sum) | no weighting | 0.733 | 0.849 | 0.896 | 0.887 | 0.673 | 0.700 | 0.697 | 0.890 | prereg reference |
| GATE-M (hard gate, fresh fold, L_FIX) | gating | 0.727 | 0.847 | 0.893 | 0.889 | 0.680* | 0.703* | 0.697* | 0.890* | descriptive, supplement-only (A6.4) |
| A-UNL (unlearned rank weight on s3) | unlearned weighting | 0.731 | 0.838 | 0.891 | 0.896 | 0.673 | 0.700 | 0.697 | 0.890 | exploratory |
| A-SF (one feature, chosen from 35) | single-feature weighting | 0.742 | 0.840 | 0.891 | 0.893 | 0.700 | 0.727 | 0.730 | 0.883 | exploratory |
| A-LIN (linear logit, 35 features) | learned weighting | 0.791 | 0.884 | 0.931 | 0.920 | 0.737 | 0.753 | 0.753 | 0.917 | exploratory |
| A-S-BD (GAM on B/D features only) | learned, single source | 0.800 | 0.871 | 0.911 | 0.922 | 0.773 | 0.793 | 0.773 | 0.920 | exploratory |
| A-S-s3 (uncertainty features only) | learned, single source | 0.769 | 0.853 | 0.889 | 0.893 | 0.750 | 0.743 | 0.757 | 0.893 | exploratory |
| A-S-tbv | learned, single source | 0.762 | 0.856 | 0.904 | 0.913 | 0.730 | 0.747 | 0.753 | 0.900 | exploratory |
| A-S-ltex (pixel texture) | learned, single source | 0.758 | 0.840 | 0.893 | 0.896 | 0.673 | 0.713 | 0.683 | 0.893 | exploratory |
| A-S-nbr (codebook neighbour) | learned, single source | 0.724 | 0.873 | 0.898 | 0.900 | 0.710 | 0.690 | 0.720 | 0.893 | exploratory |
| A-S-pos (grid position only) | learned, single source | 0.731 | 0.864 | 0.891 | 0.902 | 0.700 | 0.737 | 0.727 | 0.900 | exploratory |
| A-MIL (gated-attention-MIL style) | learned weighting (non-additive) | 0.793 | 0.838 | 0.851 | 0.864 | 0.760 | 0.763 | 0.780 | 0.857 | exploratory |
| **LRF (frozen, logistic GAM)** | learned weighting (proposed) | **0.802** | 0.864 | 0.927 | 0.918 | 0.767 | 0.750 | 0.757 | 0.913 | prereg (L1, L3, L4, L-NI, LG) |
| CLIP ViT-L/14 | external encoder | 1.000 | 0.998 | 0.996 | 0.998 | 1.000 | 0.997 | 1.000 | 0.997 | descriptive (A6.6), own table |
| SigLIP so400m | external encoder | 0.998 | 1.000 | 1.000 | 0.998 | 0.997 | 0.997 | 0.997 | 0.997 | descriptive (A6.6), own table |

Eleven further rows are knockouts of the frozen LRF (one feature group set to its design-item mean; `KO-S-*`, `KO-F-*`): they are ablations of
LRF, not baselines, and are not listed here (all eight cells in `ablation_analysis.json:rows`, supplement S-VII). One of them (`KO-S-nbr`,
neighbour-distance features set to the mean) reaches 0.842 on noise, above LRF's 0.802; the paper already says "above" for this row
(study2.tex, ablation paragraph). `A-UNL` has the same accuracy as NONE in all four LG cells although its decisions differ from NONE's on 12 to 20 items per cell
(derived by section E of the script: `OUT["A-UNL_vs_NONE_items_with_different_decision"]`).

Sources, all `runs/`-relative:
- NONE and LRF, noise/JPEG/splice/clean: `P2-LRF-L1/a6_analysis.json:family_L.L1.{acc_b,acc_a}` (noise 0.7333/0.8022), `.L3` (jpeg10), `.L4` (splice128), `.L-NI` (clean).
  LG shot/impulse/speckle: `P2-LRF-LG/a6_analysis.json:family_LG.cells.<cell>.{acc_b,acc_a}`. LG clean: `P2-LRF-ABL-SCORE/ablation_analysis.json:references_accuracy.{NONE,LRF}.LG_clean`.
- GATE-M: four n = 450 cells `P2-LRF-L1/a6_analysis.json:family_L.supplement_gatem_vs_none.<cond>.acc_gatem`. Starred LG cells (and LG clean) are
  **derived** from `P2-LRF-LG/predictions.jsonl:y_gatem` by the script (section A of the script), because `family_LG` stores only b, c and net for GATE-M
  (`.descriptive_gatem_vs_none`).
- All A-* rows: `P2-LRF-ABL-SCORE/ablation_analysis.json:rows[id=<row>].cells.<cell>.acc` (each also carries `.vs_NONE.{d,ci95,b,c}` and `.vs_LRF.{d,ci95,b,c}`,
  paired percentile bootstrap, 10,000 resamples, 95%, marginal and unadjusted). Per-item decisions: `P2-LRF-ABL-SCORE/predictions_ablation.jsonl`.
  Cell n: `ablation_analysis.json:n_per_cell` (450 / 300). Three refit seeds: `ablation_analysis.json:seed_spread` (max range 0.030; seed 0 pre-fixed).
- CLIP, SigLIP: `P2-LRF-BASELINES/baselines.json:table.{clip,siglip}.<cond>.acc` (n 450 or 300); clean on the first 300 items: `P2-PAPER-TABLES/baselines_clean300.json:models.*.acc`.
  Their own clean-to-corrupted drops with 95% intervals are stored (`.drop`, `.drop_ci95`). Pixel parity: `P2-LRF-BASELINES-PARITY-L1/baselines.json:pixel_parity.min` 0.989, `-LG` 0.986 (threshold 0.98).
  Note `P2-LRF-BASELINES/baselines.json:pixel_parity` reads "not run" (stale field, superseded by the PARITY runs; documented in `tab3_baselines.tex`).
- Preregistered tests on the NONE-vs-LRF contrasts (intervals, p): `a6_analysis.json:family_L.*`, `family_LG.cells.*` (already in paper Table II, `tables/tab2_study2.tex`).
- Length-matched negatives (L-LEN, n = 449): NONE 0.708, LRF 0.784 (`a6_analysis.json:family_L.L-LEN.{acc_b,acc_a}`). NONE/LRF/GATE-M with length-matched negatives
  are in `P2-LRF-L1/predictions.jsonl:y_*_L`; GATE-M and weighting variants have no L-LEN accuracy in an analysis file.

### 1B. Study 1 test items (500 images; true-caption layout; different items and layout from 1A, never in one table with it)

| Row | Family | clean | jpeg10 | noise0.1 | splice128 | Status | Source (file:key) |
|---|---|---|---|---|---|---|---|
| NONE | no gate | 0.880 | 0.838 | 0.676 | 0.876 | prereg (P: Holm m=3) | `P2-GATE-M4/analysis.json:primary.per_corruption.{jpeg,noise,splice}.acc_b`; clean `s_c.acc_b` |
| GATE-M (alpha 0.05) | gating | 0.882 | 0.836 | 0.676 | 0.872 | prereg (P; S-C) | same, `.acc_a`; `s_c.acc_a` |
| GATE-M alpha 0.01 / 0.1 | gating (operating point) | 0.878 / 0.876 | 0.838 / 0.838 | 0.676 / 0.680 | 0.878 / 0.880 | exploratory | derived: `P2-GATE-M4/items.jsonl:conds.<c>.img.gate0.01/gate0.1.y` |
| Geometry-matched random gate (seed 0) | matched control | 0.878 | 0.838 | 0.676 | 0.874 | S-M (gatekept; not run formally) | derived: `...img.geo0.y` |
| Scattered random gate (seed 0) | matched control | 0.884 | 0.836 | 0.676 | 0.876 | exploratory | derived: `...img.scat0.y` |
| Plain-B top-k gate | alternative gate | 0.880 | 0.836 | 0.678 | 0.880 | exploratory | derived: `...img.topkB.y`; differences `analysis.json:mechanism.<c>.y.gate_minus_topkB` |
| Uncertainty top-k gate | alternative gate | 0.880 | 0.836 | 0.676 | 0.878 | exploratory | derived: `...img.topks3.y` |
| Changed-code oracle gate | oracle (uses labels) | = NONE | 0.754 | 0.746 | 0.880 | exploratory | derived `...img.chg.y`; = `P2-POSTHOC-LEARNED/results.json:results.<c>.accuracy.CHG.acc` |
| Pixel denoise (OpenCV NLM) + unweighted | pixel preprocessing | n/a | 0.844 | **0.852** | n/a | prereg (S-DN, Holm m=2, secondary) | `P2-GATE-M4/analysis.json:s_dn.per_corruption.{jpeg,noise}.acc_b` |
| Median of Delta (MED) | robust combiner | 0.852 | 0.804 | 0.678 | 0.840 | Tier 3, exploratory | `P2-GATE-M4/tier3_fusion.json:cells.<c>.arms.MED.acc`; clean `clean.arms.MED.acc` |
| Trimmed mean at gate flag count (TM-G) | robust combiner | 0.874 | 0.834 | 0.676 | 0.866 | Tier 3 | `...arms.TM-G.acc` |
| 20% trimmed mean (TM20) | robust combiner | 0.854 | 0.816 | 0.682 | 0.846 | Tier 3 | `...arms.TM20.acc` |
| SOFT-G (discount flagged tokens) | soft gate | 0.880 | 0.838 | 0.676 | 0.876 | Tier 3 | `...arms.SOFT-G.acc` |
| SOFT-A (conformal-p weight on every token) | learned-free weighting | 0.884 | 0.838 | 0.676 | 0.880 | Tier 3 | `...arms.SOFT-A.acc` |
| Cross-fitted logistic GAM (F1 = SEL) | learned weighting | 0.884 | 0.870 | 0.778 | 0.876 | post hoc, exploratory | `P2-POSTHOC-LEARNED/results.json:results.<c>.accuracy.F1.acc` |
| GBT SNR plug-in (F2) / F2+cond | learned weighting | 0.864 / 0.862 | 0.826 / 0.824 | 0.724 / 0.734 | 0.870 / 0.876 | post hoc | `...accuracy.F2.acc`, `F2+cond.acc` |
| Per-token MLP (F3, 3 seeds) | learned weighting | 0.852 | 0.822 | 0.774 | 0.842 | post hoc | `...accuracy.F3.acc` |
| Grid conv+transformer (F4, 3 seeds) | learned weighting | 0.814 | 0.766 | 0.672 | 0.766 | post hoc | `...accuracy.F4.acc` |
| Detector weight 1 - p_hat(z) (DET) | learned detector | 0.880 | 0.790 | 0.712 | 0.868 | post hoc | `...accuracy.DET.acc` |
| ZSNR / F2+z (label-aware oracles) | oracle | 0.880 / 0.862 | 0.834 / 0.838 | 0.680 / 0.730 | 0.872 / 0.866 | post hoc | `...accuracy.ZSNR.acc`, `F2+z.acc` |
| RESTORE-CLEAN / UNRESTRICTED | bounds | 0.880 / 1.000 | 0.880 / 1.000 | 0.880 / 1.000 | 0.880 / 1.000 | post hoc | `...accuracy.RESTORE-CLEAN.acc`, `UNRESTRICTED.acc` |

Cautions for 1B:
- n = 500 for every row (E-dec drops 2 items for the `chg` arm in JPEG only: `P2-GATE-M4/edec.json:cells.P1.n_complete` = 498; the derived `chg` accuracy above uses all 500 stored decisions and equals the learned-ceiling file).
- The post hoc learned-weighting rows (F1 to F4, DET, oracles) are cross-fitted (5 outer, 3 inner folds, `P2-POSTHOC-LEARNED/results.json:protocol`), but were computed
  **before the caption-slot fix**: their caption-withheld features carry the true caption's length (`research/paper2/posthoc/LRF-FROZEN-2026-10-29.md:15`;
  `SAP-ADDENDUM-A6...md:318`, D0083). Only F1 was redone at L_FIX = 13 and only as a number for the sample-size rule
  (`P2-LRF-CF-LFIX/results.json`: net 0.116, b 86, c 28; label "never quoted as performance"). Do not put F1 to F4 in a main-paper comparison table.
- Study 1's NONE/GATE-M/Tier-3 numbers are at the true-caption layout; Study 2's are at L_FIX. The two item sets differ (500 design/test items vs 450 fresh items), so
  1A and 1B must never share columns.
- E-dec (`P2-GATE-M4/edec.json`) and E-pred (`epred_score.json`) are descriptive decompositions and sign agreement, not methods; no accuracy of an alternative method beyond the `chg` arm above.
  S-D/S-D2 are detection AUROCs, not verification accuracy.

### 1C. Other stored comparisons (different item sets or tasks; not for the proposed table)

| Set | Methods and accuracy | Source |
|---|---|---|
| Suite (8 pixel-corruption cells, n = 100 each) | clean 0.80; per cell NONE / GATE-M / changed-code oracle (e.g. impulse_noise2 0.60 / 0.61 / 0.64; fog4 0.81 / 0.80 / 0.72) | `P2-GATE-SUITE/analysis.json:cells.<cell>.{acc_clean,acc_none,acc_gm,acc_chg}` (exploratory, AD.9; `SAP-GATE-2026-10-28.md:1050`) |
| S2 re-infill (patch, splice128; n = 300) | I-GATE 0.877 / 0.877, I-RAND4 0.867 / 0.880, NONE 0.873 / 0.880 | `P2-GATE-S2/analysis.json:per_cell.{patch,splice}.desc.{igate_vs_none,irand_vs_none}.{acc_a,acc_b}` |
| FOIL-COCO one-word foil pairs (n = 298, clean) | text direction 0.879, image direction 0.654, fusion (LDA) 0.876, Stouffer 0.846 | `P2-GATE-FOIL/analysis.json:descriptive.{acc_text_alone,acc_image_alone,acc_lda,acc_stouffer_unfitted}`, `test.{acc_a,acc_b}` |
| H3 hard negatives (50 headroom items) | NONE clean 32/50; no corruption had decision headroom; H4 not run | `P2-GATE-H3/family.json:clean_none_accuracy`, `go` (false) |

**Count.** On the fresh fold: 13 methods with accuracy in all eight cells (NONE, GATE-M, LRF and 10 alternative weightings), 2 external encoders
in seven conditions plus clean-300, and 11 knockouts. On the Study 1 items: 25 rows in four conditions (the table in 1B). Alternative-method
accuracy on any other items is limited to the suite (three methods), S2 (three), and FOIL (four scores).

## 2. Preregistered versus exploratory

| Comparison | Status | Where stated |
|---|---|---|
| LRF vs NONE, noise (L1, one-sided McNemar 0.05; headline needs p <= 0.025) | confirmatory | `SAP-ADDENDUM-A6-LRF-2026-10-29.md:174` and C6-5 (A6.4) |
| LRF vs NONE, JPEG (L3), splice (L4): Holm m=2, two-sided; only if L1 confirmed | confirmatory | A6 line 175-176 |
| LRF vs NONE clean, non-inferiority margin 0.03 (L-NI) | confirmatory (margin set after an exploratory clean interval was seen) | A6 line 181-185 |
| LRF vs NONE with length-matched negatives (L-LEN) | confirmatory | A6 line 186 |
| LRF vs NONE, shot / impulse / speckle severity 3 (LG, Holm m=3, one-sided) | confirmatory | A6 line 192, A6.5 line 198-206 |
| GATE-M on the fresh fold (descriptive arm) | descriptive, supplement-only, no guarantee, no comparison with LRF | A6 line 171, 303, 307-308 |
| CLIP ViT-L/14 and SigLIP so400m | descriptive, own table, no test, no ranking words, no LRF column | A6.6 line 208-215; A6 line 296 (wording), 307-308 |
| Ablation weightings A-* and knockouts KO-* (21 variants, 336 intervals) | exploratory; added after the primary, family H and Study 2 results; no Holm | `ABLATION-PLAN-2026-10-30.md:6,39,373`; `ablation_analysis.json:meta.label` |
| Study 1: GATE-M vs none (P, Holm m=3), S-C clean, PS positive control, S-DN denoise (m=2), S-D/S-D2, S2, B | confirmatory or formal secondary (P is the only headline family) | `SAP-GATE-2026-10-28.md:107-108, 133-137, 976, 1068-1072`; S-DN m=2 per the addendum row at line 746 |
| Study 1: Tier-3 combiners (MED, TM-G, TM20, SOFT-G, SOFT-A) | exploratory; intervals only, no p-value, no multiplicity statement | `SAP-ADDENDUM-A4-2026-10-28.md:131`; `SAP-GATE-2026-10-28.md:332-333` |
| Study 1: pixel suite (8 cells) | exploratory | `SAP-GATE-2026-10-28.md:1050, 1076` |
| Study 1: cross-fitted learned weightings F1 to F4, DET, oracles | post hoc, exploratory; cannot rescue, explain or qualify P | `research/paper2/posthoc/LEARNED-CEILING-REPORT-2026-10-29.md:6` |
| Study 1: E-dec, E-pred | descriptive; E withdrawn (no test) | `P2-GATE-M4/epred_score.json:formal_test_note`; `edec.json:label` |

Study 2 is the last confirmatory study (A5 r2, `SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md:63`); anything added now is Tier 3.

## 3. Proposed single "comparison with baselines" table (about one column)

Scope: fresh fold, Study 2 only, n = 450, four conditions. LG cells (n = 300, three noise types) go to the supplement with the same rows (section 1A holds the numbers;
`tables/supp_ablation_vsLRF_LG.tex` already exists). Do not pool conditions or put Study 1 rows beside these (A6 line 303, 308).
Marks: **bold** = best, _italic_ = second best among the eight same-evidence rows (NONE, GATE-M, A-UNL, A-SF, A-LIN, A-S-BD, A-MIL, LRF), ties share the mark; computed by the script
(`OUT["proposed_table_rows"]`). Encoders are set apart and unranked.

| Method (same evidence Delta_j, same rule) | Noise 0.1 (primary) | JPEG q10 | Splice 128 | Clean | Status |
|---|---|---|---|---|---|
| Unweighted sum (NONE) | 0.733 | 0.849 | 0.896 | 0.887 | P |
| Hard gate GATE-M (Study 1 method) | 0.727 | 0.847 | 0.893 | 0.889 | D |
| Unlearned rank weight (A-UNL) | 0.731 | 0.838 | 0.891 | 0.896 | E |
| Single learned feature (A-SF) | 0.742 | 0.840 | 0.891 | 0.893 | E |
| Linear logit, 35 features (A-LIN) | 0.791 | **0.884** | **0.931** | _0.920_ | E |
| GAM, B/D features only (A-S-BD) | _0.800_ | _0.871_ | 0.911 | **0.922** | E |
| Attention-MIL pooling (A-MIL) | 0.793 | 0.838 | 0.851 | 0.864 | E |
| **LRF (frozen before data)** | **0.802** | 0.864 | _0.927_ | 0.918 | P |
| *External encoders, not ranked, not like-for-like* | | | | | |
| CLIP ViT-L/14 | 1.000 | 0.998 | 0.996 | 0.998 | D |
| SigLIP so400m | 0.998 | 1.000 | 1.000 | 0.998 | D |

Status: P = preregistered; E = exploratory (added after the results, 21 variants scored, unadjusted); D = descriptive (A6.4, A6.6). Cell sources are in section 1A
(`a6_analysis.json` for NONE, LRF, GATE-M; `ablation_analysis.json:rows[id].cells.<cell>.acc` for A-*; `baselines.json:table.<model>.<cond>.acc` for the encoders).
Where an interval is wanted per cell, `vs_NONE` and `vs_LRF` are stored for every A-* row (`ablation_analysis.json`); for the main-text table the cleanest addition
is one extra column "LRF minus row (95% interval)" for the noise cell only, from `.cells.L1_noise0.1.vs_LRF` (A-LIN -0.011 [-0.031, 0.009]; A-S-BD -0.002 [-0.033, 0.029]; A-MIL -0.009 [-0.044, 0.027];
A-SF -0.060 [-0.096, -0.024]; A-UNL -0.071 [-0.111, -0.031]; NONE and GATE-M: `a6_analysis.json:family_L.L1` and `supplement_gatem_vs_none`).

Required footnote (honest reading): "Only NONE and LRF were fixed before the data. Rows marked E were specified and scored after the preregistered results; marks show the order of the accuracies in this sample,
not a test; eight cells share images and intervals are unadjusted." With this table the discussion sentence is: learned weights beat the unweighted sum and simple unlearned or single-feature
weights; a linear logit or a B/D-only GAM on the same features does about as well, so the evidence supports learning a weight, not the particular form of LRF.

**How to present CLIP and SigLIP (one sentence).** "CLIP ViT-L/14 and SigLIP so400m are external contrastive encoders pretrained on far larger image-text corpora than UniDisc's
and score 0.996 to 1.000 in every condition, i.e. at the ceiling of these items, so they bound what a verifier can reach here but are not a like-for-like competitor of a rule applied to
UniDisc's own token evidence, and they are shown below the rule, unranked and untested." Add the existing caveat that their pretraining overlap with COCO val2017 was not checked
(unchecked per the audit; CLIP's training set size of 400 million pairs is from Radford et al. 2021; SigLIP's WebLI size not verified).

**Two ways to write it (decision for Shlok).**
- Option A, within the SAP: keep Table III as is (encoders alone), add the table above without the GATE-M row and without the encoder rows, status E for all variants. No amendment.
- Option B, one combined table as drawn: requires an amendment row recording that A6.4 / A6.6 / A6.12 are lifted for descriptive purposes, dated before the table is built and stated in Methods once.
  The tests and the confirmatory sentences stay unchanged; no ranking word may enter the encoder rows. The writer's rule in the header of `sections/study2.tex` (line 6, "no comparison of LRF with any other method")
  and Table III's caption ("no test and no comparison are made") would need to be revised in the same step.
I recommend Option B only if the amendment is disclosed in the paper; otherwise Option A.

## 4. Baselines a reviewer would expect and are missing

All need a go-ahead from Shlok for GPU use (memory `laptop-gpu-crashes`: 8 crashes, no unattended runs, memory cap and telemetry, other sessions share the GPU). The project CLAUDE.md line
"downloads above 5 GB need the user's yes" is superseded for model checkpoints by the 2026-10-14 instruction (memory `dlm-downloads-and-context`); I would still ask before any checkpoint above 5 GB.
Time estimates below are rough, unmeasured scalings; the previous CLIP+SigLIP pass (5,400 scored rows, including image regeneration and model download) finished in at most about one hour
(file times only: `runs/P2-LRF-BASELINES.stderr.txt` 01:01, `baselines.json` 01:59; no timing is recorded).

| Missing baseline | Why a reviewer asks | Cost (12 GB laptop GPU) | Download | Notes |
|---|---|---|---|---|
| Median and trimmed-mean combiners (MED, TM20, TM-G) on the **fresh fold** | detector-free robust aggregation is the obvious alternative to learned weights; already on Study 1 items (Tier 3) | **CPU only**, minutes: needs `*_delta` and `*_flag0.05` in `runs/P2-LRF-L1/arrays/item*.npz` (verified present: keys `<cond>_delta`, `<cond>_flag0.05`) | none | Exploratory, would be a new Tier-3 row; SOFT-A/SOFT-G also need the M2 calibration (`P2-GATE-M2`) and a score array, unverified. Needs the `.venv` python (system python lacks numpy). |
| Pixel denoise + unweighted (and + LRF) on the fresh fold | on Study 1 the denoiser reached 0.852 vs 0.676 on noise 0.1 (S-DN) | GPU. Scaling the Study 2 cost (median 8.0 s per item for four conditions, `P2-LRF-L1/items.jsonl`): about 2 conditions x 450 items x ~2 s, roughly 30 min, unmeasured | none | Denoiser harms JPEG at that setting; report both. Changes the story: a defence outside the model beats weighting on noise. |
| BLIP-2 ITM (Li et al., ICML 2023, arXiv 2301.12597) | image-text matching verifier, standard next to CLIP | ~5,400 image-caption pairs (2,700 items x 2 captions), plus image regeneration with the stored seeds: ~10-20 min if ~50-100 ms per pair (guess) | ITM ViT-g checkpoint size not verified; likely a few GB, check the model card | Same decision rule as CLIP (s(c+) > s(c-)); needs the pixel-parity check again (existing script `analysis/paper2/lrf/baselines.py`). Pretraining overlap with COCO is a standing risk (BLIP-2 uses COCO in pretraining; verify before use). |
| VQAScore (Lin et al., ECCV 2024, arXiv 2404.01291), a likelihood-based verifier | strongest recent "likelihood of Yes" verifier; nearest in spirit to the paper's likelihood rule | The 11B CLIP-FlanT5 variant does not fit 12 GB in fp16 (about 22 GB); a smaller variant (about 3B, 6-7 GB fp16) may; ~0.2-0.5 s per pair, 20-45 min (guess) | The large checkpoint exceeds 5 GB (sizes unverified; check the model card) | Ask before download. COCO overlap needs checking. |
| Autoregressive VLM caption likelihood (a small Qwen2-VL / LLaVA class model, P(c+ \| image) vs P(c- \| image)) | the closest like-for-like "likelihood verifier" outside masked diffusion | 2B-class in fp16 ~4-5 GB weights; ~0.1-0.3 s per pair, 10-30 min (guess) | around 4-5 GB (unverified) | Length-normalise both captions (the L-LEN issue applies). |
| Diffusion-classifier verifier (Li et al. 2023, Clark and Jaini 2023, already cited in `sections/introduction.tex:30`) | the original generative-classifier baseline | Stable Diffusion scale: hours (many noise levels per pair), likely > 2 h for 5,400 pairs | about 4-5 GB (unverified) | Optional; I would not run it for TNNLS. |
| Blind baselines (caption-only prior, length) | to bound the shortcut risk | CPU, cheap | none | L-LEN and A-S-pos already cover length and position. |

Two further gaps that are not baselines: (i) LRF has no independent second model or dataset (the paper states one model, one severity per noise type); (ii) the fresh fold has no
head-to-head with the retired first freeze (`ca5c4e2f`, exploratory object, never scored on fresh items by design).

## 5. Reproduction

```
python -I analysis_posthoc/baseline_inventory_2026-10-30.py        # stdlib only; asserts derived == stored
```
Output: `analysis_posthoc/baseline_inventory_2026-10-30.out.json` (sections `fresh_fold`, `ablation_accuracy_crosschecked`, `study1_test_items_M4`, `proposed_table_rows`).
Not verified here: the exact wording of every paper table line (I read `study2.tex`, `tab3_baselines.tex` and the supplement S-II line 522-529 only); SOFT-G / SOFT-A feasibility on the fresh fold;
model sizes and training-set overlap for the missing baselines.
