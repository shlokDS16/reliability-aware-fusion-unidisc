# Exploratory plan: baselines on the Study 2 fresh fold (written before any new number is computed)

Date: 2026-10-30, Paper 2 lead session. Approved by Shlok in chat ("Within prereg", "Yes, run it", "Now"). Committed before any
run or computation below; the commit hash of this file is the time stamp. Everything here is **exploratory**: no test, no
multiplicity claim, no selection, no change to any preregistered result, wording or decision. The fresh fold was already used for
the confirmatory test (families L, LG); these are additional looks at the same items and are labelled so in every place they appear.

## E1. Pixel denoiser before scoring (GPU)

- **Question:** on the fresh fold, how does a classical pixel-domain denoiser applied before UniDisc scoring compare with no
  weighting (NONE) and with the frozen LRF?
- **Denoiser:** exactly Study 1's preregistered S-DN arm: OpenCV `fastNlMeansDenoisingColored` with `exp_p2/gate/config.py`
  `DENOISE_PARAMS` (h = hColor = 25.5, windows 7 and 21), unchanged. No other setting is tried.
- **Items and conditions:** the 450 fresh-fold test items of family L (`runs/P2-LRF-FOLD`), the same true and wrong captions,
  and the same stored corruption seeds; conditions Gaussian noise sigma 0.1 and JPEG quality 10 (the two S-DN conditions).
- **Arms:** DN+NONE (unweighted sum on the denoised image) and DN+LRF (the frozen LRF, spec `runs/P2-LRF-FROZEN-LFIX`, unchanged,
  applied to the denoised image; LRF was trained without denoising, so this arm is out of its training distribution and is
  reported as such).
- **Reported:** accuracy of each arm; paired difference against NONE and against LRF on the undenoised image, with discordant
  counts b and c and a 95% paired percentile bootstrap interval (10,000 resamples, seed 0). No p-values.
- **Guards:** the GPU guard of the confirmatory runs (memory cap, slow rule, telemetry, explicit max chunks); Shlok present.
- **Whatever the result, it is reported** (main-paper table row and one sentence; details in the supplement).

## E2. Detector-free robust combiners on the fresh fold (CPU)

- MED (median of the per-token evidence), TM20 (20% trimmed mean) and TM-G (trimmed at the gate's flag count) computed from the
  stored per-token arrays `runs/P2-LRF-L1/arrays/item*.npz` (`<cond>_delta`, `<cond>_flag0.05`) for all four family-L
  conditions. Definitions exactly as in Study 1's Tier 3 (`exp_p2/gate/tier3_fusion.py`). Same reporting as E1.

## E3. Comparison table (existing numbers + E1 + E2)

- One table, fresh fold, n = 450, columns noise 0.1 / JPEG 10 / splice 128 / clean. Rows: NONE; simple unlearned weighting
  (A-UNL); robust combiners (E2); learned variants of the exploratory ablation (A-SF, A-LIN, A-S-BD, A-MIL); LRF; DN+NONE and
  DN+LRF (E1, noise and JPEG only). Sources: `research/paper2/tnnls/BASELINE-INVENTORY-2026-10-30.md`.
- Best and second best per column are marked as a descriptive reading; the caption states that only NONE and LRF were fixed
  before the fold was opened and that ranks among the other rows are post hoc.
- **Not in this table** (SAP Addendum A6.6 lines 208-215, 307-308): CLIP, SigLIP and the fresh-fold GATE-M arm. CLIP/SigLIP stay in
  their own unranked table (Table III), with no LRF number beside them.

## E4. Qualitative figure (no new experiment)

- Real images, with the selection rule fixed here: the first item in fold-file order (by `idx`) of each kind under Gaussian noise
  0.1: (i) both NONE and LRF correct, (ii) NONE wrong and LRF correct, (iii) NONE correct and LRF wrong. Showing (iii) is required.
- Panels per row: clean image, noisy image, per-token evidence map Delta_j, LRF weight map w_j, the two captions, and both verdicts.
- Caption: "descriptive, selected by a fixed rule; not evidence of reliability tracking".
