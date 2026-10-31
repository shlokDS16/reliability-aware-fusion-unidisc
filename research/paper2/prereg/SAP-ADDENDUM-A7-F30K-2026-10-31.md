# SAP Addendum A7: preregistered transfer test of the frozen LRF to a second dataset (Flickr30K), 2026-10-31

Written by the Paper 2 lead before any Flickr30K image or caption was downloaded, before any code for this test exists, and before any
outcome; committed before the data step. Reason: the supervisor's comment of 2026-10-31 ("additional validation across ... datasets")
and the red-team closure (AC 5/10, "one dataset"). This is a NEW confirmatory test of the SAME frozen object; it changes nothing in
Addendum A6, its families or its results.

## A7.1 Object and question
- Object: the frozen LRF exactly as pinned in `runs/P2-LRF-PINS/pins.json` (model `runs/P2-LRF-FROZEN-LFIX/model.npz`, scorer
  `exp_p2/gate/lrf_score.py`, decision rule sum_j w_j Delta_j > 0, tie wrong). No refit, no recalibration, no feature change.
- Question: does the frozen weighting, fitted on COCO design images, raise image-direction verification accuracy under Gaussian noise
  (sigma 0.1) on images from another dataset that it never saw?

## A7.2 Data (fixed now)
- Flickr30K (Young et al., TACL 2014) images and captions, test split of the standard Karpathy split (1,000 images), taken from the
  Hugging Face dataset `nlphuji/flickr30k` (annotation file with a split column; the lead checks the licence terms before use: research
  use only, images not redistributed; the repository stores image identifiers, never images).
- Items: every test-split image, in ascending order of file name, minus exclusions decided before scoring: (a) the file does not decode;
  (b) a perceptual-hash (dHash, 64 bit) Hamming distance <= 4 to any of the 500 COCO design images or the 450 COCO fold images (possible
  duplicates, since COCO images also come from Flickr); (c) no admissible negative exists. Every exclusion is listed with its reason.
- True caption: the first caption of the image (caption index 0). Wrong caption: caption index 0 of another test image chosen by a
  seeded generator (numpy default_rng([2026, 1031, idx])), redrawn until the two captions share no content word (lower-case alphabetic
  words of three or more letters, minus a fixed English stop-word list written into the builder before any draw). Length-matched wrong
  caption (for F-LEN): caption index 0 of another test image with exactly the same UniDisc caption token count and no shared content word,
  chosen by the same generator; if none exists, the nearest token count, with the difference recorded.
- Item ids: gid = 9000 + idx (disjoint from COCO gids), so the noise stream rung_rng(gid, "noise", 0) is new for every image.

## A7.3 Conditions and run
- Conditions: clean and Gaussian noise sigma 0.1 (`corruptions.gaussian_noise`, the L1 call). Everything else as the L1 run: fixed
  caption slot 13, length-matched negative stored (`--neg-len`), TbV on, no sanity or denoised copies, same K, D-cache and codebook.
- Images are read from a local copy of the Flickr30K test images through a thin loader (the pinned runner `exp_p2/run_gate_m4.py` is
  not edited). Run id `P2-LRF-F30K`; GPU guard flags as the L1 run; per-item arrays untracked with a SHA-256 manifest.
- Code audit by the gate-auditor before the GPU; the supervisor-approved GPU rule applies (the first author's go-ahead before launch).

## A7.4 Hypotheses and tests (fixed now)
- **F1 (primary, one hypothesis):** LRF against the unweighted sum under noise sigma 0.1, exact one-sided McNemar test (H1: b > c) at
  alpha 0.05. "Confirmed" if and only if p <= 0.05 and b > c. A gain claim in the title or abstract needs p <= 0.025 (as C6-5).
- **F-NI (one hypothesis):** non-inferiority on clean images, margin -0.03 (the A6 margin), read from the lower bound of the 90%
  paired percentile bootstrap interval of the net accuracy change (10,000 resamples, SeedSequence(0)).
- **F-LEN (one hypothesis, secondary):** F1 repeated with the length-matched wrong captions, items whose length-matched caption still
  differs in length excluded and counted; exact one-sided McNemar at 0.05.
- Each of the three is its own family at its own level; no adjustment across families. Reported with net change, discordant counts,
  95% paired bootstrap interval, p.
- Also reported, descriptive: accuracies of both rules in both conditions; the gain on clean images.

## A7.5 Wording and placement (fixed now; no rescue)
- F1 confirmed: "On a second dataset, the frozen weighting, unchanged, raised accuracy under Gaussian noise (preregistered one-sided
  test)" in Results and abstract (abstract without numbers), plus F-NI and F-LEN as they come out.
- F1 not confirmed: "On a second dataset the frozen weighting did not confirm (net D, 95% CI, one-sided p)" in Results AND in the
  abstract; no subgroup, other noise level, refit or other dataset is offered as a substitute; no "trend".
- No comparison of LRF with CLIP/SigLIP (A6.6) and no link to the earlier gate study (C6-4) in any sentence about this test.
- Whatever the outcome, the run is reported once; it is never repeated with other items, captions or seeds.

## A7.6 Stop rules
- A guard abort, a failed self-check or a non-finite score stops the run; the stop is reported, nothing is re-run silently.
- Fewer than 800 scored items after exclusions: the test is reported as "underpowered (n of 1,000)" with its result, no headline claim.

## Amendment A7.2(d) (2026-10-31, before any image was scored; after the builder found the conflict)
The pinned runner applies the SAP A2.1 caption-length rule (5 to 32 UniDisc tokens) at run time and stops a fold in which more than 10
percent of items break it. 128 of the 1,000 first captions of the Flickr30K test split are longer than 32 tokens, so the fold as written
would stop before item 0. Added exclusion (d): items whose true caption is outside 5 to 32 tokens are excluded at build time, the same
rule the COCO folds obey; wrong and length-matched captions are drawn only from captions inside the range. Dry-run count before this
amendment: 872 kept (a 0, b 0, c 0, d 128), above the 800 floor of A7.6. Nothing else changes. Builder report:
research/paper2/tnnls/F30K-BUILD-REPORT-2026-10-31.md; the as-written build is kept as runs/P2-LRF-F30K-FOLD.as-written/ for the record.
