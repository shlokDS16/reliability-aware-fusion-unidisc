# Paper 2 (IEEE TNNLS) figure and table captions, draft v2 (figure-smith, 2026-10-30; spec v2.2)

Rebuild everything (CPU only, no GPU): `"<repo>/.venv/Scripts/python.exe" paper2-tnnls/scripts/build_all.py`.
Figures: vector PDF in `paper2-tnnls/figures/` (STIX General, TrueType embedded, no Type 3, 8 pt text at final width) plus a 300 dpi PNG preview (inspection only).
Tables: complete `tabular` environments (booktabs) in `paper2-tnnls/tables/`, a `% run: <file> <keys>` comment before every row. Insert with `\input{tables/<file>}` inside `\begin{table}` (or `table*` for the wide ones); IEEE puts the caption above the tabular.
Bold convention (state once in the paper): a cell is bold only when its preregistered test rejected at its preregistered level; no underline; no ranking.
Colour identity: Study 1 blue, circles; Study 2 bluish green, diamonds; Fig. 1 and Fig. 2 neutral. Greyscale: every series also differs by marker, line style or fill.
Numbers in captions are design constants only (n, margins, resamples); every estimate is read from the files named in each caption at build time.
No figure or table holds both Study 1 and Study 2 numbers. Wording avoids the spec's must-not list (checked by grep of this file).

| Item | File | Study | Width |
|---|---|---|---|
| Fig. 1 | `figures/fig1_measurement.pdf` | shared measurement only | two-column |
| Fig. 2 | `figures/fig2_theory.pdf` | 1 (Method) | column |
| Fig. 3 | `figures/fig3_study1_P.pdf` | 1 | column |
| Fig. 4 | `figures/fig4_study2_weights.pdf` | 2 (Method) | two-column |
| Fig. 5 | `figures/fig5_study2_results.pdf` | 2 | two-column |
| Table I | `tables/tab1_familyP.tex` | 1 | table* |
| Positive control | `tables/tab_ps.tex` | 1 | table* |
| Detection | `tables/tab_detection.tex` | 1 | table* |
| Family H | `tables/tab_H.tex` | 1 (optional) | column |
| Cost (Study 1) | `tables/tab4_cost_study1.tex` | 1 | column |
| Table II | `tables/tab2_study2.tex` | 2 | table* |
| Table III | `tables/tab3_baselines.tex` | 2 (reference encoders) | column or table* |
| Features | `tables/tab_features.tex` | 2 | table* |
| Cost (Study 2) | `tables/tab4_cost_study2.tex` | 2 | column |
| Families at a glance | `tables/tab_families_glance.tex` | 1 and 2, separate blocks | column |
| Status map | `tables/supp_status_map_study1.tex` | 1 (supplement) | column |
| All tests, Study 2 | `tables/supp_tests_full_study2.tex` | 2 (supplement) | table* |

---

## Fig. 1 `figures/fig1_measurement.pdf` (two-column, 7.16 in)  -- label `fig:measurement`
**Fig. 1.** Image-text verification by per-token evidence in a masked diffusion model (conceptual drawing; no data). An image, which may be damaged by noise, JPEG compression or a spliced region before it is tokenised, is converted to image tokens (reddish purple: tokens whose code is changed by the damage). With the image tokens masked and each candidate caption visible, the model gives a per-token evidence $\Delta_j$, the log-probability ratio of the observed image token under the true and under a wrong caption (blue: $\Delta_j>0$; orange: $\Delta_j<0$). The evidence is summed without weights, $S=\sum_j\Delta_j$, and the true caption is chosen if $S>0$. The token pattern is a fixed schematic, not a measurement. Source: script `paper2-tnnls/scripts/fig1_measurement.py`; definitions in Section III.

## Fig. 2 `figures/fig2_theory.pdf` (column width, 3.5 in)  -- label `fig:frontier`
**Fig. 2.** Model figure, no data: when withholding tokens raises the signal-to-noise ratio of the evidence sum under correlated tokens (theory under stated assumptions, not validated on UniDisc). For a clean-token withholding probability $\phi_0$ and a corrupted-token withholding probability $\phi_1$, with $\mu_c=0$ and $\gamma_{01}=0$, Proposition (`prop:snrcorr`) gives the curves $\phi_1=b(\phi_0;G,\chi)$ above which withholding raises $\mathbb{E}S/\sqrt{\mathrm{Var}\,S}$ (shaded; the shade deepens where more curves lie below). Curves: $G=(\rho m-1)\gamma_1=0$ (independent tokens, Eq. (snr)), 1, 4 and 16, drawn for the display value $\chi=\rho\sigma_c^2/[(1-\rho)(\sigma^2+\mu^2)]=1$; a larger $G$ lowers the curve toward the diagonal $\phi_1=\phi_0$ (random withholding). Grey region: every rule with $\phi_1\le\phi_0$ lowers the ratio when $\gamma_{01}\ge0$. A curve ends where it reaches $\phi_1=1$ or has no root. The curves were checked against the ratio computed directly from Eqs. (mean) and (varcorr) on a grid before drawing (0 mismatches in 6 730 points; script output). The ratio is that of the sum; accuracy follows from it only for jointly Gaussian terms. Source: `research/paper2/method/THEORY-ADDENDUM-2026-10-29.md` R1.4 and R1.8; script `paper2-tnnls/scripts/fig2_theory.py`.

## Fig. 3 `figures/fig3_study1_P.pdf` (column width)  -- label `fig:p_result`
**Fig. 3.** Study 1, family P: net accuracy change of GATE-M against no gate under each corruption (P1 JPEG quality 10, P2 Gaussian noise with standard deviation 0.1, P3 splice of 128 px), $n=500$ items each. Open circle: net change (GATE-M minus none); thick bar: 90% and thin bar: 95% paired percentile-bootstrap interval over items (10 000 resamples); solid line at 0; dashed lines: the $\pm0.05$ margin. Under P2 no item was discordant, so the interval is the single point zero and records the absence of discordant items, not a measured precision. The 90% interval lies inside the margin for every corruption; the family label is negative. One model (UniDisc, 1.4B parameters), one severity per corruption, COCO image-caption pairs with a random other caption as the negative. Source: `runs/P2-GATE-M4/analysis.json`, keys `primary.per_corruption.{jpeg,noise,splice}.{label,delta,ci90,ci95}`, `outcome.label`; script `paper2-tnnls/scripts/fig3_study1_P.py`.

## Fig. 4 `figures/fig4_study2_weights.pdf` (two-column, 7.16 in)  -- label `fig:lrf_weights`
**Fig. 4.** Study 2, the frozen weight model. Descriptive; not evidence that the weights track corruption; no accuracy and no correctness mark on this figure. (a) Partial dependence of the token weight $w=\sigma(f(x))$ on the six of 35 features with the largest learned effect range (range of $w$ over the plotted domain), with every other standardised feature at its mean 0; the horizontal axes are in original feature units ($\mu+\mathrm{sd}\cdot x$). Each curve runs from the lowest to the highest of the eight knots of its feature (the $1/9$ to $8/9$ quantiles of the standardised design-token features); grey ticks mark the knots. Line colour and style give the feature group named in the key (group names and notation as in the feature-group table). (b) Token-weight maps on the $32\times32$ token grid for the same three fold items (the three at the top of the fold file, selected by position, not by outcome), each clean (left) and under Gaussian noise with standard deviation 0.1 (right), on one colour scale (square-root) shared by all six maps. Source: `runs/P2-LRF-FROZEN-LFIX/{model.npz,spec.json}` (keys `a`, `b`, `c`, `knots`, `mu`, `sd`, `feature_names`), `runs/P2-LRF-L1/arrays/item000{0,1,2}.npz` (sha256 checked against `arrays_manifest.json`), evaluated with `analysis_posthoc.learned_ceiling.lrf.load_frozen` and `infer_item`; computed values and the script hash are in `runs/P2-PAPER-FIGS/` (`fig4_pd_curves.json`, `fig4_token_weights.npz`, `fig4_meta.json`); script `paper2-tnnls/scripts/fig4_study2_weights.py`.

## Fig. 5 `figures/fig5_study2_results.pdf` (two-column)  -- label `fig:lrf_results`
**Fig. 5.** Study 2 results on the preregistered fresh fold, family L: net accuracy change of the frozen learned reliability-aware fusion, with minus without reliability weights, $n=450$. (a) Diamond: net change; bar: 95% paired percentile-bootstrap interval over items (10 000 resamples). L1 (Gaussian noise with standard deviation 0.1; primary, shaded; exact one-sided McNemar $p$, preregistered one-sided level 0.05); L3 (JPEG quality 10) and L4 (splice, 128 px): Holm-adjusted two-sided exact McNemar $p$. (b) L-NI (clean images), own panel: net change with its 90% interval and the non-inferiority margin $-0.03$ (dashed line), fixed after an exploratory clean interval had been seen. No adjustment across families. The further noise types (LG) are reported in Table II only. Source: `runs/P2-LRF-L1/a6_analysis.json`, keys `family_L.{L1,L3,L4,L-NI}.{net,ci95,ci90,p_one,p_holm,margin}`; script `paper2-tnnls/scripts/fig5_study2_results.py`.

---

## TABLE I `tables/tab1_familyP.tex` (Study 1, family P only)
Family P: GATE-M against no gate on the 500 test items
(Note: $b$: items GATE-M answers correctly and the ungated rule incorrectly; $c$: the reverse; $n_d=b+c$; net difference $=(b-c)/n$. Intervals: paired percentile bootstrap over items (10 000 resamples) at 90% (the level of the preregistered decision), 95% and 98.33% (the Holm level of the smallest-p step). $p$: exact two-sided McNemar; $p_{\rm Holm}$: Holm over the three corruptions. The exact Clopper-Pearson 95% bound on the absolute net change was added at writing and is descriptive, not preregistered. Under P2 the bootstrap intervals are the single point zero because no item was discordant. No estimate is bold: no test rejected. The family label is negative. Source: `runs/P2-GATE-M4/analysis.json` (`primary.per_corruption.*`, `outcome.label`); `runs/P2-PAPER-BOUNDS/p_exact_bounds.json`.)

## TABLE (Study 1) `tables/tab_ps.tex`
Positive control (pipeline check): GATE-M against no gate on the sanity corruptions
(Note: columns as in Table I; Holm over two; 95% and 98.33% intervals; never read beside family P; the control was not met and the plan's audit found no defect. Source: `runs/P2-GATE-M4/analysis.json` `ps.per_corruption.*`, `ps.positive_control`; `runs/P2-A23-AUDIT/a23_ps_audit.json`.)

## TABLE (Study 1) `tables/tab_detection.tex`
Detection of changed image tokens on the 200 detection items: AUROC per item
(Note: Mean per-item AUROC against changed-code labels with 95% percentile-bootstrap intervals over items (10 000 resamples). $q$: the within-modality masked score of the method; TbV score: the one-pass observed-position score of the non-finetuned model; rival: the best of the nine cheap scores in either orientation, chosen on these data (sign oracle), so rival values are optimistic; its sign is shown. Last column: paired difference $q$ minus rival; bold: Holm-adjusted $p<0.05$ (JPEG and noise). No claim is made about detection relative to the cheap rivals. Source: `runs/P2-GATE-M1/analysis.json`, keys `table.<corruption>.{q,tbv,<rival>}`, `paired_q_vs_best_cheap.<corruption>`.)

## TABLE (Study 1, optional) `tables/tab_H.tex`
Family H: recorded decision
(Note: Decision fields only; results placement per the preregistration. Source: `runs/P2-GATE-H3/family.json`, keys `n_rule.h_rule`, `go`, `downstream_claim_withdrawn`.)

## TABLE (Study 1) `tables/tab4_cost_study1.tex`
Cost per item of the main-test stage
(Note: One laptop GPU (RTX 5070 Ti Laptop, 12 GB). Network rows per item: median (range); compute time: median (quartiles) of the runner's busy time per item, excluding duty-cycle pauses; peak GPU memory: maximum over items of `torch.cuda.max_memory_allocated`. All arms of the stage are computed in one pass and share its network rows, so per-arm rows and time are not measured separately. Source: `runs/P2-GATE-M4/items.jsonl`, fields `n_rows`, `seconds`, `peak_gb`.)

## TABLE II `tables/tab2_study2.tex` (Study 2)
Study 2 preregistered families on the fresh fold: accuracy without and with learned reliability-aware fusion (LRF), discordant counts, $p$ values and decisions
(Note: $b$: items LRF answers correctly and the unweighted rule incorrectly; $c$: the reverse; net $=(b-c)/n$. Intervals: 95% paired percentile bootstrap over items, except $^{\dagger}$ (L-NI): 90%, with margin $-0.03$ fixed after an exploratory clean interval had been seen. $p$ one-sided and two-sided: exact McNemar; $p$ Holm: Holm-adjusted where the plan applies Holm (L3 and L4 after the L1 gate, two-sided; LG over its three cells, one-sided), otherwise a dash. $^{\ddagger}$ L-NI: the $p$ values against zero net change are shown for completeness only; the preregistered L-NI test is the lower 90% bound against the margin, and superiority on clean images was not preregistered. L-LEN: length-matched negative captions (449 items; one excluded for a length mismatch). LG: other noise types at severity 3, $n=300$ each, reported as three separate rows; for the impulse-noise row the 95% interval starts at 0.0 and the two-sided $p$ is 0.058. No adjustment across families. Bold: null rejected at the preregistered level; "confirmed" is used for L1 only. Source: `runs/P2-LRF-L1/a6_analysis.json` `family_L.*`; `runs/P2-LRF-LG/a6_analysis.json` `family_LG.cells.*`.)

## TABLE III `tables/tab3_baselines.tex` (Study 2 reference encoders)
Reference accuracy of CLIP ViT-L/14 and SigLIP so400m per condition
(Note: For reference only: different models trained on different data; no test and no comparison is made. Drop: clean minus corrupted accuracy of the same model on the same items, with a paired percentile-bootstrap 95% interval; decision rule: image-text score of the true caption above that of the wrong caption, ties wrong. Images are regenerated with the runner's corruption functions and seeds. The row "Clean images, same 300 items" is the clean accuracy on the 300 items on which the severity-3 cells were scored, computed at writing from the stored per-item predictions (`runs/P2-PAPER-TABLES/baselines_clean300.json`, descriptive). Cost per item was not measured: no baseline run recorded a timing. Pixel parity: five items re-encoded by the UniDisc tokeniser agree with the stored codes on at least the stated share of tokens (threshold 0.98) for each condition set; the two parity runs `runs/P2-LRF-BASELINES-PARITY-L1` and `runs/P2-LRF-BASELINES-PARITY-LG` supersede the field `pixel_parity: not run` in `runs/P2-LRF-BASELINES/baselines.json`, which records only that the main run was made without the parity option. Nearly every cell is at or next to its ceiling and most intervals are a single point; no reading beyond the stated accuracies is drawn. Source: `runs/P2-LRF-BASELINES/baselines.json` `table.{clip,siglip}.*`; the two parity `baselines.json` files, `pixel_parity.{min,threshold}`.)

## TABLE (Study 2) `tables/tab_features.tex`
Input features of the frozen weight model, by group and formula
(Note: 35 features in seven groups; names, order and counts as in `runs/P2-LRF-FROZEN-LFIX/spec.json` (`features`) and `analysis_posthoc/learned_ceiling/data.py`. $B_j$, $D_j$ and the pass quantities are defined with the notation of Section III. Source of the formulas: `analysis_posthoc/learned_ceiling/data.py`, functions `feature_names` and `engineer`.)

## TABLE (Study 2) `tables/tab4_cost_study2.tex`
Cost per item of the fresh-fold stages
(Note: As for the Study 1 cost table. NONE is the only reference measured. The weights and decision of the fusion are evaluated on stored arrays on the CPU; no timing was recorded: not measured. Source: `runs/P2-LRF-L1/items.jsonl`, `runs/P2-LRF-LG/items.jsonl`.)

## FAMILIES AT A GLANCE `tables/tab_families_glance.tex` (main text, column width)
Families at a glance: what each preregistered family tests and its recorded decision
(Note: Status only; no result is quoted. Study 1 and Study 2 are separate preregistered studies. Source of every decision word: the run files named in the `% run:` comments of the table.)

## Supplement `tables/supp_status_map_study1.tex` (Study 1 family status map, A4.2.5 item 6)
Study 1 family status map
(Note: One row per family in the order of the multiplicity map; status only, no estimate and no interval. Source: the run files named in the `% run:` comments of the table.)

## Supplement `tables/supp_tests_full_study2.tex` (Study 2, every quantity reported with every test, SAP A6.4)
Study 2: all quantities reported with every test
(Note: $n$, $b$, $c$, $n_d$, both accuracies, net difference with paired percentile-bootstrap 90% and 95% intervals (10 000 resamples), Clopper-Pearson 95% interval of $b/n_d$, exact one- and two-sided $p$, mid-$p$ (one- and two-sided), Holm $p$ where the plan applies one, and the decision. $^{\ddagger}$ L-NI: $p$ values against zero net change are shown for completeness; its preregistered test is the lower 90% bound against the margin. Source: `runs/P2-LRF-L1/a6_analysis.json` `family_L.*`; `runs/P2-LRF-LG/a6_analysis.json` `family_LG.cells.*`.)

---

## Visual check log (Read of each 300 dpi PNG, 2026-10-30)
- Fig. 1: first render overlapped the caption strips with the token grid and the strip label ran off the top; strips and label moved, canvas heightened; the decision box now has a one-line reading under it. Legend swatches match the cells. Smallest text 8 pt.
- Fig. 2: right-hand labels clipped in the first render; axes narrowed. Curves legible in greyscale (solid, long dash, dash, dots). Boundary check 6 730 points, 0 mismatches.
- Fig. 3: now only rows P1-P3 (labels from the run), intervals, the 0 line and the margins; the discordant counts and the band were removed (nothing else on the canvas). Noise row is a point.
- Fig. 4: panel (a) first overflowed the right edge; fixed. Group tag of `nbr` corrected to "token score" (the first version tagged it as neighbourhood). Panel (b) now shows clean and noisy maps of the same three items on one scale; the clean maps carry visibly larger weights than the noisy ones, which the caption does not interpret ("descriptive; not evidence that the weights track corruption").
- Fig. 5: family L only; L-NI in its own panel with the margin line; panel (b) axis label shortened to avoid clipping.
- Not yet checked: appearance inside the typeset page; `check_column_gaps.py` is for the full PDF.
