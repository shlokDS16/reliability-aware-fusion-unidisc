# Integrity diff: Mask-DiFuser presentation pass (2026-10-30)

Scope: `paper2-tnnls/` main paper (anonymous `main.pdf` and author `main_camera.pdf`, both 15 pages) and supplement (21 pages). No preregistered number, verdict word or binding sentence was changed. Old text is in git history (HEAD). Build: `bash build.sh`, 0 undefined references, all fonts embedded, 0 empty column regions. One `Overfull \vbox` of 6.5 pt is reported by the output routine on the float page 11 (a float page with the Fig. 6 figure, Table III and Fig. 7); the rendered page shows no overlap.

## A. Moves (statements unchanged)

| What | From | To |
|---|---|---|
| Fig. 6(b) partial-dependence curves (one row of six now) | main Fig. 6(b) | supplement Fig. S (label `sfig:pd`), S-IV, `scripts/fig4_study2_weights.py` writes `figures/fig4b_pd_curves.pdf` |
| Fig. 6(c) token-weight maps | main Fig. 6(c) | dropped from the paper (the real-image figure replaces it); arrays stay in `runs/P2-PAPER-FIGS/fig4_token_weights.npz` |
| Correlated-token proposition (former Proposition 2, eqs. varcorr, snrcorr), its proof sketch, the paragraph after it, and the frontier figure (former Fig. 3) | main Sec. IV-A | supplement S-II, "Withholding With Exchangeably Correlated Tokens" (`sprop:snrcorr`, `seq:varcorr`, `seq:snrcorr`, `sfig:frontier`); the proof subsection follows it; statement text identical except cross-references (Lemma 1 and eqs. mean, var, snr stay in the main paper and are cited through xr-hyper) |
| Token-detection figure (former Fig. 5) and the sentences on the one-pass score, the frozen rival differences, and the detection-item comparison | main Sec. IV-C "Token detection" | supplement S-II "Token Detection" (`sfig:detection`, `stab:detection`) |
| Full comparison table with intervals | new | supplement S-VII (`stab:compare`, `tables/tab_baselines_full.tex`) |

SPEC section 0 rule 4 (Proposition 2 in the main text) is overridden by the lead's instruction for this pass; a comment in `sections/study1.tex` records it.

## B. Changed or new sentences (main paper)

### Introduction (`sections/introduction.tex`, contribution list)
1. Old: "raises the signal-to-noise ratio of an additive evidence sum. The condition is stated as an approximation because image tokens are dependent, and it is extended to exchangeably correlated tokens (\cref{prop:snrcorr}); it is linked to no result (Sec. IV-A)."
   New: "raises the signal-to-noise ratio of an additive evidence sum; it is an approximation because image tokens are dependent, is extended to exchangeably correlated tokens in supplement S-II, and is linked to no result (Sec. IV-A)."
2. Old: "...so the preregistered falsifier for the score was met (\cref{fig:detection})." New: "(supplement S-II)."
3. Old: "We check the clean false-alarm statement on held-out clean test pairs. Re-infilling of the flagged tokens and the score-level combination of the two directions on foil captions were run as formal tests."
   New: "The clean false-alarm statement was checked on held-out clean test pairs, and re-infilling of the flagged tokens and the score-level combination of the two directions on foil captions were run as formal tests." (same content, two sentences merged)
4. Old: "Learned reliability-aware fusion (LRF) is a logistic generalised additive model that maps 35 ... fitted on 500 design images, frozen, and pinned by SHA-256 before any test image was selected."
   New: "Learned reliability-aware fusion (LRF), a logistic generalised additive model that maps 35 ... , was fitted on 500 design images, frozen, and pinned by SHA-256 before any test image was selected."
5. Old: "(0.03 in accuracy; 90% interval of the net change 0.009 to 0.053); the margin was fixed after an exploratory clean interval had been seen."
   New: "(0.03 in accuracy; 90% interval of the net change 0.009 to 0.053; margin fixed after an exploratory clean interval had been seen)."
Kept verbatim: "Each item was delivered regardless of the outcome", the "preregistered test excludes ..." sentence, the AUROC sentences (0.961, 0.955, 0.561, 0.503), the one-pass and falsifier sentences, the family H status sentence, the scope sentence of item 3, the "Scope of this paper" paragraph. The list is only about 3 lines shorter: its items are quotations of the binding contribution bullets (A4.2.4 bullets 1-6, A6.12 scope), so further compression would change binding wording.

### Section IV (`sections/study1.tex`)
6. Lemma 1 proof. Old: "The condition is \cref{prop:snrcorr} below at zero correlation." New: "The condition is the case of zero correlation of the extension in supplement S-II."
7. "Correlated tokens" paragraph. Old: statement and proof sketch of Proposition 2, then "\Cref{fig:frontier} draws the frontier... The ratio in Proposition 2 is the SNR of the sum. If jointly Gaussian... Assumption (b) is an approximation for this gate... With correlation the ratio no longer grows like sqrt m... E-pred does not use Proposition 2, and the proposition is not used to interpret E-pred or any other result."
   New (5 sentences): "Neighbouring image tokens are correlated, so (eq. var) is an approximation. Supplement S-II states and proves an extension of Lemma 1 to exchangeably correlated tokens and draws its frontier; it is theory under stated assumptions and is not evaluated on the model. The ratio in Lemma 1 is the signal-to-noise ratio of the sum. If the per-token terms are jointly Gaussian, [unchanged]. E-pred does not use the extension, and the extension is not used to interpret E-pred or any other result."
   The two sentences "Assumption (b) is an approximation ..." and "With correlation the ratio no longer grows like sqrt m ..." moved unchanged to the supplement (after the proposition).
8. "Token detection" paragraph. Old: five sentences with Fig. 5 references, the one-pass TbV sentence, and "q minus the rival was -0.198 (-0.211 to -0.186) under JPEG and -0.258 (-0.267 to -0.250) under noise (Holm-adjusted p=0.0004)"; "On the detection items, where the rival and its sign were selected, q also lies below it (same-item selection; Fig. 5(b))."
   New: sentence 1 without the figure reference ("... near chance on JPEG and Gaussian noise (AUROC with intervals in supplement S-II)"); "In the preregistered comparison with the best cheap rival (the pixel variance of a token's patch, sign reversed, frozen and re-scored on the test items) the score was below the rival under JPEG and under noise (Holm-adjusted p=0.0004; values, the comparison on the detection items, and the one-pass comparison in supplement S-II)." Kept verbatim: "The preregistered falsifier for the score was therefore met, and this paper makes no claim that the score detects corrupted codes more accurately than cheap methods." and the label-circularity sentence. The one-pass sentence, the -0.198/-0.258 numbers and the detection-item sentence are in supplement S-II unchanged.

### Section V (`sections/study2.tex`)
9. "(a)" removed from the pointer to Fig. 6 ("seven groups of Fig. 6 (formulas in supplement S-IV)").
10. Old: "Fig. 6 draws the model and shows the learned shapes and three example weight maps." New: "Fig. 6 draws the model; the learned shapes of the six features with the largest effect range are in supplement S-IV, and Fig. 8 shows three fresh-fold items." (Fig. numbers are automatic.)
11. Fig. 6 caption: panels (b) and (c) text removed; "(a) Schematic" became "(schematic; no data; fixed weight grid)".
12. V-D opener. Old: "Table II gives every preregistered test and Fig. 7 the family-L intervals; each family is at its own level..." New: "Fig. 7 shows the net change and its interval for each family-L hypothesis and Table II gives every preregistered test; each family is at its own level..." (figure first; no verdict word touched).
13. New paragraph after the L1/L-NI results (qualitative figure): "Fig. (qualitative) shows three of these items under noise, one of each kind and chosen by a rule fixed beforehand: both rules correct, only LRF correct, and only the unweighted rule correct. Items of these three kinds were 303, 58, and 27 of the 450, so the rows are examples, not a sample. The maps are descriptive and do not show that the weights track reliability or corruption."
14. New figure caption (qualitative): selection rule, the counts 303, 58, 27, the colour-scale description, "Descriptive; not evidence that the weights track reliability or corruption", and the COCO val2017 image ids 335177, 520324, 224724 with the licence note.
15. Algorithm 1 (decision rule of the frozen LRF) after Eq. (lrf-decision): restates the pinned specification, no added step. New sentence: "...with a tie counted as wrong; Algorithm 1 lists the steps of the frozen rule."
16. New subsection V-H "Comparison With Alternative Aggregation Rules (Exploratory)" with Table IV (`tables/tab_baselines.tex`) and its notes; text quoted in the file. Placeholder `% DN-SENTENCE` marks where the lead adds one sentence after the denoiser run; the "Denoise" rows print "pending".

### Section VI (`sections/discussion.tex`)
17. Old: "which Fig. 6 cannot separate" New: "which the learned weight shapes (supplement S-IV) cannot separate".
18. Old: "No ablation was preregistered; Sec. V-G is exploratory." New: "No ablation and no comparison with other aggregation rules was preregistered; Sec. V-G and V-H are exploratory."
19. Old (deviation 9): "The exploratory ablation was added at writing." New: "The exploratory ablation and the exploratory comparison with alternative aggregation rules (Sec. V-H; plan committed before any value was computed) were added at writing."

## C. Supplement changes
S1. S-II: new subsection "Withholding With Exchangeably Correlated Tokens (Main Paper, Section IV-A)" holding the moved statement, proof sketch, remarks and frontier figure; the proof subsection now refers to the local equations; the symbol-crosswalk row for Proposition 2 of the theory addendum points to it; "the main paper's frontier" now cites the local figure.
S2. S-II: detection subsection retitled "Token Detection: Per-Item AUROC, the One-Pass Score, and the Rival", with the detection figure and the three moved sentences.
S3. S-IV: partial-dependence figure (`sfig:pd`); disclosure sentence of S-VII: "(main paper, Fig. 6)" became "(moved from the main paper, Fig. S)" (the shape functions the plan's author had seen; fact unchanged).
S4. S-VII: full comparison table (`stab:compare`).
S5. S-VIII sources list: entries for the schematic and PD figure, qualitative figure, Algorithm 1, comparison tables, frontier and detection figures.

## D. Numbers added or newly printed in prose or captions (all from files, none typed into a table)

| Number | Where | Source |
|---|---|---|
| 303, 58, 27 (items of the three kinds among 450) | Sec. V-D text, qualitative caption | `runs/P2-PAPER-FIGS/fig_qualitative.json` items[*].n_items_of_this_kind_in_fold |
| 335177, 520324, 224724 (COCO val2017 image ids) | qualitative caption | same file, items[*].coco_val2017_image_id |
| 0.802 (LRF noise accuracy; already in the paper), 0.002 and 0.011 (A-S-BD and A-LIN minus LRF, noise; intervals contain 0) | Sec. V-H | `runs/P2-LRF-ABL-SCORE/ablation_analysis.json` rows[A-S-BD, A-LIN].cells.L1_noise0.1.vs_LRF.{d,ci95}: -0.0022, -0.0111 |
| 0.884 vs 0.864; difference 0.020 [0.004, 0.038] (A-LIN, JPEG) | Sec. V-H | same file, rows[A-LIN].cells.L1_jpeg10 (acc 0.8844; vs_LRF d 0.02, ci95 [0.004, 0.038]); LRF 0.864 from `runs/P2-LRF-L1/a6_analysis.json` family_L.L3.acc_a |
| 0.931 vs 0.927 (A-LIN, splice) | Sec. V-H | same file, rows[A-LIN].cells.L1_splice128.acc (0.9311); LRF family_L.L4.acc_a |
| 0.922 vs 0.918 (A-S-BD, clean) | Sec. V-H | same file, rows[A-S-BD].cells.L1_clean.acc (0.9222); LRF family_L.L-NI.acc_a |
| Table IV (14 values per column) | Sec. V-H | `tables/tab_baselines.tex` from `scripts/tab_baselines.py` (a6_analysis, ablation_analysis, `runs/P2-LRF-E2/combiners.json`); the DN rows print "pending" |
| Algorithm 1 constants (m = 1024, 35 features, 13 padding tokens, SHA-256 db7fdb4e) | Sec. V-B | `runs/P2-LRF-FROZEN-LFIX/spec.json` (n_features, caption_slot_len, model_sha256) |

Claim "MED, TM20 and TM-G had lower accuracy than no weighting in every condition": read off the printed Table IV cells (point accuracies, 12 comparisons), not a test.

## E. Checks
- Must-not word scan of `main.pdf` text: no hits other than citation titles and "superiority on clean images was not a preregistered hypothesis" (existing). "screening", "independent" (for audits), "robust" in prose: none new.
- Anonymous build: no author names in `main.pdf`; AI statement only in the Acknowledgment.
- Figure scripts: `scripts/fig4_study2_weights.py` rewritten (schematic only; PD curves as a separate figure) and re-run; it rewrote `runs/P2-PAPER-FIGS/fig4_meta.json` (purpose, script sha); PD curve values unchanged.

## Red-team fixes (2026-10-31; red-team report `research/paper2/tnnls/REDTEAM-MASKDIFUSER-PASS-2026-10-30.md`; rulings D0107-D0110)

Build after the fixes: `main.pdf` 15 pages, `main_camera.pdf` 15 pages, 0 undefined references, 0 overfull boxes above 2 pt (the 6.5 pt overfull vbox on float page 11 that was already present at HEAD
175efa89 is gone: the ablation figure is now set at 0.96 of the column width), all fonts embedded.

| Finding | Change | Files |
|---|---|---|
| F1 (D0107) | One sentence in IV-C4: the M1 rival (patch variance, sign -1) AUROC 0.756 [0.743, 0.768] (JPEG) and 0.768 [0.760, 0.776] (noise) against the score's 0.561 [0.547, 0.575] and 0.503 [0.493, 0.513]; paired difference -0.195 [-0.214, -0.175] and -0.265 [-0.278, -0.253]; same-item selection favours the rival. Source `runs/P2-GATE-M1/analysis.json` (table.{jpeg,noise}, paired_q_vs_best_cheap). | `sections/study1.tex` |
| F2 (D0108) | TM-G row removed from `scripts/tab_baselines.py` (the file `combiners.json` is still read for MED and TM20) and both tables regenerated; no "gate" clause in Table IV, its footnote or V-H; median and 20% trimmed mean defined by formula; denoiser described as "non-local-means denoising before scoring (setting fixed in advance)"; CLIP/SigLIP/Table III pointer and the hard-gate-arm sentence deleted; "Study 1 setting" deleted. | `scripts/tab_baselines.py`, `tables/tab_baselines*.tex`, `sections/study2.tex`, supplement `stab:compare` caption |
| F3 (D0109) | No bold or underline in Table IV (both versions); italics mark the highest value per column (ties share); no second-best mark. Caption: marks descriptive, one sample, not a test; only the unweighted rule and LRF fixed before the fold was opened. The "highest accuracy" sentences of V-H are value statements (0.802 / 0.800 / 0.791 under noise; 0.884 vs 0.864 under JPEG with interval; 0.931 vs 0.927 under splice; 0.922 vs 0.918 clean). | same |
| F4 | `SPEC.md`: "SPEC v2.3 (2026-10-31)" note at the top listing D0107-D0110. A gate-auditor verdict on the overrides is still the lead's step. | `SPEC.md` |
| F5 (D0110) | Table IV caption: "4 of the 10 learned refits of the exploratory ablation are shown, chosen after the fold was scored; all 10 are in supplement S-VII." | `sections/study2.tex` |
| F6 (D0110) | VI-C (Limitations): the linear logit on the same 35 features was at or above LRF in three of four conditions and above the unweighted rule with a 95% interval excluding zero in all four, including JPEG (0.036 [0.007, 0.064]), where LRF's preregistered test detected no difference. Numbers from `runs/P2-LRF-ABL-SCORE/ablation_analysis.json` (A-LIN cells) and `runs/P2-LRF-L1/a6_analysis.json` (L3). "Similar range" deleted from V-H. | `sections/discussion.tex`, `sections/study2.tex` |
| F10 | New `runs/P2-PAPER-FIGS/fig_qualitative_licences.json` (licences and Flickr URLs, checked against the COCO val2017 caption file's `licenses` and `flickr_url` fields: identical to the lead's values); supplement S-VIII credits the images ("Images: COCO val2017 (Lin et al., 2014; cited in the main paper), Flickr, licences as listed; the noisy panels are modified") with the three licences and URLs; the figure caption cites `lin2014coco` and points to S-VIII. `fig_qualitative.json` untouched. | `runs/P2-PAPER-FIGS/fig_qualitative_licences.json`, `supplement/supplement.tex`, `sections/study2.tex` |
| F11 | Algorithm 1: first step computes the seven token scores (caption slot of 13 padding tokens) and the item-level aggregates; then per-token evidence, features and weights; knots defined as the Q = 8 stored knots of each feature (`spec.json`); output states the chosen caption (c+ if the weighted sum is positive, else c-; a tie counts as wrong). Matches `runs/P2-LRF-FROZEN-LFIX/spec.json` (layout, caption_slot_len, selected_cfg.knots, preprocessing). | `sections/study2.tex` |
| F12 | Plain method names in Table IV (those of Fig. 7: "Unlearned rank weight", "Single feature (selected)", "Linear logit, 35 features", "Additive, from B and D only", "Attention pooling (MIL style)", "Unweighted sum"); no A-UNL, A-SF, A-LIN, A-S-BD, A-MIL or s_3 in the PDF text. The two DN row labels now read "Denoise, then unweighted sum" and "Denoise, then LRF" (labels only; the "pending" values and the `% DN-SENTENCE` placeholder are untouched). | `scripts/tab_baselines.py` |
| F13 | Contribution 1 reworded: the closed-form condition is "stated" in Section IV and "proved in supplement S-II". No theory statement altered. | `sections/introduction.tex` |
| F14 | Qualitative paragraph and caption: both-wrong items (62 of 450; 303 + 58 + 27 + 62 = 450, from `runs/P2-LRF-L1/predictions.jsonl`, condition noise0.1) stated; "three of these items" replaced by "three items ... one of each of three kinds"; the rule is "fixed before the figure was made, after the confirmatory result"; Study 2 deviation (9) now lists the qualitative figure and Table IV as at-writing exploratory additions. | `sections/study2.tex`, `sections/discussion.tex` |
| F15 | `runs/P2-PAPER-FIGS/fig4_meta.json` restored to its content at 175efa89^ (`git show 175efa89^:...`); `scripts/fig4_study2_weights.py` now writes `fig4_meta_2026-10-31.json`. The script was not re-run, so that file does not exist yet and the figure files are unchanged. | `runs/P2-PAPER-FIGS/fig4_meta.json`, `scripts/fig4_study2_weights.py` |

Not done here (outside this brief): F7 (DN rows, the caption sentence that LRF was not trained on denoised images, a sixth reading in VI-B, the empty `env-lock.txt` note), F8 (DOCX, Word PDFs and the submission package are not rebuilt), F9 (the authors').
Layout trims to keep both builds at 15 pages: shorter ablation, qualitative and Table IV notes; "see the text for how a knockout interval is read" removed from the ablation caption.
Every new number in prose carries a `% run:` comment at its sentence.
