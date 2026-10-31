# Flickr30K transfer test (SAP Addendum A7) integrated into the TNNLS manuscript, 2026-10-31

Agent: manuscript-writer. Nothing committed. Acknowledgment and AI wording untouched. All paths under `paper2-tnnls/` unless stated.

## Build result
- `prepare_bib.py` then `build.sh`: main.pdf 13 pages (was 12; cap 15), supplement.pdf 11 pages, author version 13 pages.
- Undefined references or citations: 0 in main.log, supplement.log, main_camera.log. Overfull boxes above 2 pt: none printed. All fonts embedded. Column-gap check: 0 of 13 pages.
- Abstract (non-comment text of `sections/abstract.tex`): **249 words** (was 249).
- Cover letter recompiled: 1 page. The PDFs in `SUBMISSION-PACKAGE/` (01, 02, 03) are NOT refreshed; only `source/cover_letter.pdf` was rebuilt.

## Changes (file:line after edit)
1. `sections/study2.tex:245-299` new subsection "Transfer to a Second Dataset (Preregistered)" (`sec:study2-f30k`), after the LG results and before Reference Encoders; table `tab:f30k` at 273-283 (includes `tables/tab_f30k.tex`). Design, leak check, exclusions, the three results, descriptive clean-versus-noise remark (descriptive only, no test).
2. `tables/tab_f30k.tex` (generated) and `scripts/tab_f30k.py` (new; reads only `runs/P2-LRF-F30K/f30k_analysis.json`; run with `python -E`, as `-I` hides the script folder). A6 tables unchanged.
3. `sections/abstract.tex:10-35` no numbers; second test on Flickr30K added; last sentence now "one model, two datasets, and one tested noise level". Cuts: dropped "which scores every image token given a caption", "at one level", and merged the denoiser and linear-logit sentences.
4. `sections/introduction.tex:68-72` (contribution 3), `:78` and `:81-82` (scope).
5. `sections/conclusion.tex:15-22`.
6. `sections/discussion.tex:16` (reading the result), `:32-35` (limitations: two datasets, one model; clean-versus-noise descriptive), `:48-49` (no third dataset; negative kinds), `:61` (negatives per dataset), `:87-90` deviation (13).
7. `sections/setting.tex:69` (Flickr30K named), `:82-88` multiplicity and Bonferroni, `:92-98` preregistration paragraph (third-party timestamp for A7 only; COCO tests keep "no third-party timestamp"; the 30 October push sentence now says "tests on COCO").
8. `sections/declaration.tex:27-28` data availability: Flickr30K added, not redistributed.
9. `references.bib:279-288` new entry `young2014flickr30k`, verified against Crossref 2026-10-31 (TACL vol. 2, pp. 67-78, Dec 2014, authors Young, Lai, Hodosh, Hockenmaier, DOI 10.1162/tacl_a_00166). `references-ieee.bib` regenerated.
10. `supplement/supplement.tex:100` (seven families, 0.30), `:118-120` families table (F1, F-NI, F-LEN), `:130-141` new subsection S-I "Addendum A7" (commits 76b85e44 and c79d3ed3, HF dataset revision, licence note, predictions SHA-256), `:205-206` deviation, `:596` sources entry for the table.
11. `SUBMISSION-PACKAGE/source/cover_letter.tex:28` one sentence added; "and the paper states these limits" dropped to stay on one page.

## Every new number and its source
All from `runs/P2-LRF-F30K/f30k_analysis.json` unless stated.
| Value in text | Source key |
|---|---|
| n 872, floor 800 | n_scored, min_scored, underpowered (false) |
| F1: 0.693 to 0.792, net 0.100, 95% CI [0.072, 0.128], b 128, c 41, p 6.4e-12 | F1.acc_none, acc_lrf, net, ci95, b, c, p_one (6.440556e-12); label confirmed; headline_gain_claim_allowed true |
| F-LEN: 0.683 to 0.771, net 0.087, [0.058, 0.116], b 125, c 49, p 3.8e-9, 0 exclusions | F_LEN.* ; n_excluded_length_mismatch 0 |
| F-NI: 0.841 to 0.868, net 0.028, 90% [0.009, 0.046], lower bound 0.009 > -0.03, b 60, c 36 | F_NI.acc_none, acc_lrf, net, ci90, lower90, margin, b, c, non_inferior |
| clean gain 0.028 versus noise gain 0.100 (descriptive) | descriptive.gain_on_clean, gain_on_noise0.1 |
| 1000 test images, 128 excluded (caption length), 0 undecodable, 0 near-duplicate, 0 no-negative; 872 kept | `runs/P2-LRF-F30K-FOLD/builder_report.json` n_test_split, n_excluded_a/b/c/d_*, n_kept |
| dHash threshold 4, smallest kept distance 6 | `runs/P2-LRF-F30K-FOLD/leak_check.json` checks F2 detail.threshold, min_distance_kept |
| length-matched wrong caption has exact token count for all 872 | builder_report.json length_matching.n_exact |
| seven families, 1 - 0.95^7 = 0.30 | SAP A6.7 (4 families) + A7.4 (3); 0.3017 |
| Bonferroni 0.05/20 = 0.0025; p_L1 = 0.0005 (0.000508), p_F1 = 6.4e-12 | 17 families (A6.7) + 3; `runs/P2-LRF-L1/a6_analysis.json` family_L.L1.p_one; F1.p_one |
| commits 76b85e44 (A7), c79d3ed3 (amendment d) | git log |
| HF revision 2b239bef..., predictions SHA-256 82f0a248... | builder_report.json dataset.revision; f30k_analysis.json inputs.predictions_sha256 |

## Points for the lead
- The Bonferroni sentence: p_L1 x 20 = 0.0102 and p_F1 x 20 = 1.3e-10; the text states the comparison with 0.0025, not the adjusted values.
- "Pushed to the hosting service before its data were downloaded" rests on the lead's statement (no run file); the comment in `setting.tex:97` says so. No service name appears.
- Licence wording in the supplement (dataset card has no licence field; homepage: non-commercial research and education, Flickr Terms of Use, authors do not own the copyright) is taken from `builder_report.json` licence, which records a WebFetch summary, not a primary reading. Verify before submission.
- "Karpathy split" is named without a citation (no bib entry exists and none was invented); add a Karpathy and Fei-Fei entry if wanted.
- The word "first" appears only as "first caption" (dataset field); no priority claim. No "robust", "generalises", "state of the art", CLIP/SigLIP or gate-study wording was added.
- Study2.tex line 192-193 (L1 paragraph) still says COCO only, correctly, since it describes L1.
- In the abstract, "non-inferior on both datasets" uses the margin fixed after an exploratory COCO clean interval; F-NI reused that margin, so the caveat still applies and is kept.
- Table II prints F-NI without a p, as for L-NI; it is shrunk to the column width like Table III.
