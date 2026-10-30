---
agent: gate-auditor
date: 2026-10-30
brief: Number reconciliation of the Paper 2 (IEEE TNNLS) manuscript and supplement against runs/ files, commit 258281c8
sources_examined: [paper2-tnnls/main.tex, paper2-tnnls/sections/*.tex (appendix.tex not input), paper2-tnnls/tables/*.tex, paper2-tnnls/supplement/supplement.tex (as committed at 258281c8), paper2-tnnls/scripts/fig*.py, tab*.py, figures fig3 and fig5 (png), pdftotext of main.pdf and supplement.pdf, runs/P2-GATE-M1..M5, P2-GATE-FOLDS, P2-GATE-S2, P2-GATE-FOIL, P2-GATE-H3, P2-GATE-SUITE, P2-A23-AUDIT, P2-PAPER-BOUNDS, P2-PAPER-TABLES, P2-LRF-PLAN, P2-LRF-FOLD, P2-LRF-FROZEN-LFIX, P2-LRF-L1 (a6_analysis.json, predictions.jsonl, items.jsonl), P2-LRF-LG, P2-LRF-BASELINES, P2-LRF-BASELINES-PARITY-L1/-LG, P2-UNIDISC-KEYCHECK, SAP-ADDENDUM-A6 A6.7]
coverage: every printed number of the abstract, sections I-VII, Tables I-V, Figs 3 and 5, and the supplement outside S-VII; see "Not covered"
verdict: PASS WITH FIXES
---

# Verdict: PASS WITH FIXES

No printed value disagrees with its run file. One wording sentence contradicts a table (M1). The rest are rounding, provenance and
convention items. Nothing was edited; the manuscript is untouched. Ledger rows added: 0.

## Method and rounding rules

- Source files were opened, not summaries. Rule used: accuracies, nets and interval ends to 3 decimals (round half up on the stored
  float); p-values to 4 decimals if p < 0.001, else 3 decimals (this is `pfmt` in `fig5_study2_results.py`, and Table IV and the text
  follow it); AUROC to 3 decimals; calibration shares to 4 decimals; CP bounds to 3 decimals.
- Recomputed from stored data, not just read: all b, c, accuracies and nets of L1, L3, L4, L-NI, L-LEN, the three LG cells and the
  fresh-fold GATE-M arm from `runs/P2-LRF-L1/predictions.jsonl` and `runs/P2-LRF-LG/predictions.jsonl` (file SHA-256 equals the
  `meta` hashes `e919776c...` and `a4626d78...`); every exact McNemar p (one- and two-sided) of Tables I and IV, PS, S2, B, S-C from
  (b, c); Holm adjustments of L, LG, P and S2; 1 - 0.95^17 = 0.5819; the L1 and L-NI bootstrap intervals (independent seed, within
  one grid step); the SHA-256 of `analysis.json` against `p_exact_bounds.json:meta.source_sha256` (equal); all 35 feature names by group
  (7, 3, 8, 4, 6, 6, 1).
- Table numbering in the PDF: I = family P, II = detection, III = features, IV = Study 2 families, V = reference encoders. The brief's
  "Table II" and "Table III" correspond to Tables IV and V.

## Counts

| Item | Count |
|---|---|
| Printed values checked, main paper (abstract, text, Tables I-V, Figs 3 and 5, captions) | about 330 |
| Printed values checked, supplement outside S-VII | about 330 |
| Value mismatches against the run file | 0 |
| Rounding inconsistencies (same quantity printed with different decimals) | 1 (M2) |
| Claims contradicted by a table or run file (wording) | 1 (M1) |
| Numbers with no `% run:` comment in body prose (results) | 0 |
| Constants or caption numbers with no `% run:` comment (traceable elsewhere) | see M8, M9 |
| `% run:` comments pointing to a missing file | 0 (every `runs/`, `research/`, `exp_p2/` path exists) |
| `% run:` comments citing a file that does not hold the stated number | 2 (M6, M7) |
| Cited run files that exist but are untracked | 1 (M5) |
| `\todo` live at 258281c8 | 6 (list below) |

## Findings (mismatches, missing or weak sources)

| ID | Location | Printed value / wording | Source | Status |
|---|---|---|---|---|
| M1 | `sections/study1.tex` "Exploratory analyses" (first sentence after the Tier-3 comment); `supplement.tex` S-II Tier-3 paragraph, first sentence | "On the realistic corruptions no detector-free combiner gave higher verification accuracy than the hard gate." | `runs/P2-GATE-M4/tier3_fusion.json:cells.noise0.1.contrasts.MED_minus_GM.diff = +0.002` (acc 0.678 vs GM 0.676) and `TM20_minus_GM.diff = +0.006` (acc 0.682); the supplement's own Table S-Tier-3 prints both | WORDING CONTRADICTED by the table. Under noise two detector-free combiners have higher point accuracy than GATE-M (CIs contain 0; readings "not distinguishable"). Needs "no detector-free combiner was detectably above the hard gate" or similar. Fix required. |
| M2 | `sections/study2.tex` Results, L3 sentence | "Holm-adjusted p=0.38" | `a6_analysis.json:family_L.L3.p_holm = 0.38169`; Table IV and Fig. 5 print 0.382 | Rounding inconsistency (2 vs 3 decimals; text vs table and figure). Fix: print 0.382. |
| M3 | `sections/study2.tex` L4 sentence; `discussion.tex` (v) | "Holm-adjusted p is 0.049, a margin of 0.001 below the 0.05 level" | `family_L.L4.p_holm = 0.048613` (true gap 0.0014) | Consistent with the printed 0.049 only. Not a mismatch; optional: "about 0.001". |
| M4 | `sections/study1.tex` Table II caption "on the 200 Detection Items" and text "On the 200 detection items" | Items column shows 197 (JPEG) and 198 (noise) | `runs/P2-GATE-M1/analysis.json:table.jpeg.q.n = 197, table.noise.q.n = 198` (n_items = 200) | Unexplained n difference. Add a clause that items with an undefined per-item AUROC are dropped, or reword the caption. |
| M5 | `tables/tab4_cost_study1.tex`, `study1.tex` Cost paragraph (84 rows, 11.2 s, 8.2 GB) | values correct (recomputed: median 84, quartiles 10.95/11.21/11.51 s, max 8.205 GB) | `runs/P2-GATE-M4/items.jsonl` exists (7.7 MB) but is untracked (`git ls-files` empty); L1 and LG `items.jsonl` are tracked | Source not in the repository. Value OK locally. Commit it or state it is untracked in the deviations list. |
| M6 | `study1.tex` PS audit comment | "unit tests 584 passed, 5 skipped, 0 failed" attributed to `runs/P2-A23-AUDIT/a23_ps_audit.json` | The JSON holds the 0 mismatches (all keys zero, six conditions) but not the test count; the count is in `research/paper2/prereg/A2.3-AUDIT-PS-2026-10-29.md` line 75 | Value correct; comment cites the wrong file for it. |
| M7 | `setting.tex` and `study2.tex` comments for "17 families, 0.58" | cites `a6_analysis.json:multiplicity_note` | That note says only "no multiplicity adjustment across families..."; the 17 and 0.58 are in `SAP-ADDENDUM-A6-LRF-2026-10-29.md` line 226 (also cited). My count of Table S-Families: P, PS, S2, B, R, six rows S-M/S-Z/S-DN/S-D/S-D2/S-C, H, H-M, L, L-NI, L-LEN, LG = 17. | Value correct; the JSON key does not hold it. |
| M8 | `setting.tex` lines 54-55 (JPEG quality 10, sigma 0.1, 128 x 128); `study1.tex` protocol (100 headroom items, 15 %, 240 items, 10 000 resamples, 98.33 %) and captions of Figs 3, 4, 5, Table I, Table V | no `% run:` comment | Traceable: `P2-GATE-M3/family.json:family[*].severity`, `P2-GATE-M4/analysis.json:meta.bootstrap_resamples = 10000` and `ci9833`, `P2-GATE-M4/config.json:ps_params` (patch 8, swap_frac 0.15, grid 32, 1024 tokens, vocab 16384), `P2-GATE-FOLDS/folds.json`, SAP A2.2 (240). "512 px" has no `runs/` key; it rests on `research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md` line 249. | Convention gap (constants), not a value error. |
| M9 | `supplement.tex` S-II tables (headroom, calibration, flags, equal-size gates, E-dec, E-pred, Tier-3, Tier-3 PS) and S-I deviation list | The tables give the file and keys in a "Source:" caption, not `% run:` comments; deviation numbers (162 files, 106/114 rows, 334 of 500, 21-item dry run, 1.5 %, 5.0 GB vs 2 to 4 GB) have no run comment | All table values verified (below). 162 is in `research/paper2/data/L7-SIGNOFF-LRF-FOLD-2026-10-29.md` and the family-L audit; 106 and 334 in PREREG-GATE-v4 and SAP; "5.0 GB vs 2 to 4 GB" I could not locate in any file searched; "up to about 1.5 %" is a round-up of the observed 1.1 to 1.4 % token disagreement (0.98828, 0.98926, 0.98633) | Convention gap; one operational number (5.0 GB) has no located source. |
| M10 | `declaration.tex` "Claude Opus 5.5, Sonnet 5.5, Haiku 5.5" | no source | Codex name `gpt-6-luna` verified in `research/paper2/tnnls/codex/SESSION.txt`; the Claude versions have no record | Covered by the open AUTHOR todo. |
| M11 | `study2.tex` fold paragraph "2 449 eligible ... after the exclusions (2 526 images)" | both values match `P2-LRF-FOLD/manifest.json:meta.n_excluded = 2526` and `meta.universe.n_eligible_images = 2449` | 5000 - 2449 = 2551 = 2503 (excluded pools) + 48 (no instance annotation); 2526 is the size of the union of excluded ids, 23 of which are outside the 5000 captioned images | Values correct; the arithmetic is not reproducible from the printed numbers. Optional clarification. |
| M12 | Abstract and intro, "Each negative is a random other caption" | wording | Study 1: wrong caption shares no COCO category with the true image; Study 2: preregistered derangement rule, plus a length-matched second negative | Non-numeric; wording is loose but defined in Sections III-D and IV-B. |

## Binding wording spots (task item 3)

| Spot | Where printed | Value in run file | Status |
|---|---|---|---|
| L1 sentence: 0.733 to 0.802, net 0.069, 95 % 0.029 to 0.109, p = 0.0005, one-sided alpha 0.05 | abstract, intro item 8, V-D, Table IV, Fig. 5, Conclusion | acc 0.7333 / 0.8022, net 0.06889, ci95 [0.02889, 0.10889], p_one 0.00050811, alpha 0.05, b 58, c 27, n 450 | met, identical in all six places; Table IV two-sided 0.001 (0.001016) |
| L-NI interval of the net change 0.009 to 0.053; margin -0.03 fixed after an exploratory clean interval | abstract, intro, V-D, Table IV (dagger), Fig. 5b, Conclusion | ci90 [0.008889, 0.053333], net 0.03111, acc 0.8867 / 0.9178, margin 0.03, margin_note present | met; labelled as 90 %, "of the net change" (fallback F4) |
| L-LEN | abstract ("including with length-matched negatives"), V-D, Table IV | n 449, 0.7082 / 0.7840, net 0.0757, ci95 [0.0334, 0.1203], p_one 0.000437, p_two 0.000874, b 67, c 33, 1 excluded | met |
| LG three p-values incl. impulse | V-D, Table IV | shot p_one 0.000153 / holm 0.000460 / two 0.000307; speckle 0.00568 / 0.01135 / 0.01135; impulse 0.02903 / 0.02903 / 0.05806, ci95 [0.0, 0.1] | met: impulse two-sided 0.058 and lower bound 0.0 printed beside the cell in text, Table IV (row and trailing comment) and Discussion; "no two-sided claim" stated |
| L4 Holm 0.049 | V-D, Table IV, Fig. 5, Discussion (v), Limitations | p_holm 0.048613, p_one 0.012153, p_two 0.024307 | met (see M3) |
| 17 families and 0.58 | III-E, V-D, supplement S-I | SAP A6.7: 17; 1 - 0.95^17 = 0.5819 | met (see M7) |
| NEG triples | abstract, intro item 3, IV-C, Discussion, Conclusion, Table I, Fig. 3, supplement overview | jpeg delta -0.002 ci90 [-0.006, 0.0]; noise 0.0 [0.0, 0.0]; splice -0.004 [-0.010, 0.002]; n 500; outcome.label negative; equivalent_within_0p05 true | met, identical everywhere |
| Exact bounds | Table I rows, Deviation (8) | `P2-PAPER-BOUNDS`: 0.011092, 0.007351, 0.020356 printed 0.011, 0.007, 0.020 | met |

## Consistency checks (task item 2) and what was verified

- Abstract vs Results vs Table IV vs Fig. 5 vs Conclusion: identical to the stated rounding. Fig. 5 values read from the png (p = 0.0005, 0.382, 0.049; axes and margin line) agree with the script and JSON.
- Study 1: Table I vs Fig. 3 (same JSON keys; the png shows the same intervals) vs abstract: identical. Acc. none / Acc. GATE-M orientation checked (in `analysis.json`, acc_a = gate, acc_b = none for P; the reverse for L, where acc_a = LRF; the printed columns follow this correctly).
- Table V vs `baselines.json:table.*`: all 14 cell accuracies, drops and intervals match; clean-300 row matches `baselines_clean300.json` (0.997); pixel parity 0.989 and 0.986, threshold 0.98 match.
- Table II (detection): all 4 rows x 5 cells with intervals match `analysis.json:table.*` and `paired_q_vs_best_cheap.*` (e.g. JPEG diff -0.1945 prints -0.195).
- Tables III (features) and the full feature table: counts equal `spec.json:features` by group; spec constants T 0.1697 -> 0.170, Q 8, ridge 0.002718 -> 0.0027, lr 0.016851 -> 0.0169, epochs 40, slot 13, 35 features, SH rungs 4/13/40, 9 configs; hashes of S-I Table pins2 equal `HASHES.json`; Table pins1 hashes equal `P2-GATE-CARD-V4/pins.json`; all pinned commit ids exist in git except the UniDisc repository commit (external).
- Supplement S-II: headroom table, calibration table (F_cal from `thresholds.*.r_hat`), flags table, equal-size gate table (18 intervals), S-Z and S-DN values, E-dec, E-pred, coherence, suite (8 cells), S2 detail, B detail, Tier-3 and Tier-3-PS tables (45 rows x acc, b/c, n_d, diff, intervals, exact, bound, reading), 72 intervals, length strata, LG drops, fresh-fold GATE-M arm, sample-size rule, Study 2 cost tables: all match.
- Provenance commits 941a260b (2026-10-29 14:40), 24d36a8a (21:00:13), 4be79be8 (21:01:03) exist, with the order claimed (object frozen before the fold).

## `\todo` list at commit 258281c8 (6)

1. `sections/study2.tex` line 239: `[RESULT: exploratory ablation ...]`.
2. `sections/declaration.tex` line 11: `[AUTHOR: exact repository URL and archive DOI]` (non-anonymous build only; not visible in the anonymous PDF).
3. `sections/declaration.tex` line 24: `[AUTHOR: confirm the list of systems and versions ...]`.
4. `sections/declaration.tex` line 37: `[AUTHOR: confirm the level-of-use sentence ...]`.
5. `supplement.tex` line 227: `[AUTHOR: confirm the wording of the record of 29 October 2026 ~00:10 IST ... D0076-D0077]`.
6. `supplement.tex` line 1048: `[RESULT: exploratory ablation in full ...]`.

The anonymous PDF shows 3 of the main-paper todos (1, 3, 4) and 2 in the supplement. `main.tex` and the `.tex` macro definition lines are not counted. At HEAD b508e292 (committed while this audit ran) items 1, 5 and 6 are replaced by text; items 2, 3, 4 remain.

## Not covered

- The exploratory ablation (study2.tex subsection V-G and supplement S-VII, `tables/supp_ablation_*.tex`, `scripts/tab_ablation.py`): its numbers come from `runs/P2-LRF-ABL-SCORE`, which the brief excluded. The working tree and HEAD (b508e292) moved past 258281c8 during the audit; those edits are unaudited and need their own number pass.
- `sections/appendix.tex` is not input (record only). The UniDisc repository commit and code lines in the time-input table (S-I) are external and were not re-read. The 584 unit tests were not re-run. Per-item arrays (untracked) were not opened; only the committed predictions and items files.
- Bootstrap intervals were reproduced only for L1 and L-NI (seed not identical, same to one grid step); all other intervals were checked against the stored JSON, not regenerated.
- The release-stage clean-clone rebuild (procedure step 5) was not part of this brief.

## Required before the gate can tick

- Fix M1 (binding claim contradicted by Table S-Tier-3).
- Fix M2 (one rounding). M4 and M5 should be fixed or disclosed. M6 to M12 are provenance and convention items; none changes a number.

---

# Incremental audit, 2026-10-30: HEAD 9268e34b against audited 258281c8

Scope: `git diff 258281c8 9268e34b` for `paper2-tnnls/sections`, `tables`, `supplement`, `figures/CAPTIONS.md`, plus the changed figure and table scripts.
Verdict: **PASS WITH FIXES** (no value mismatch in any ablation, test-table or status table; one stale number in the supplement and one set of dangling pointers; details below).
Ledger rows added: 0. Same rounding rules as above. Nothing was edited.

## What was re-checked and how

| Item | Method | Result |
|---|---|---|
| Ablation tables `supp_ablation_vsLRF_L1`, `_vsLRF_LG`, `_vsNONE`, `_seeds` (21 variant rows, 8 cells, references NONE and LRF, 10 seed rows) | A parser (scratch `abl_check.py`) read every printed number from the .tex and compared it to `runs/P2-LRF-ABL-SCORE/ablation_analysis.json` (acc, d, ci95 vs LRF and vs NONE, seed accuracies, mean, SD, range); tolerance 0.0005 | 1 672 values compared, 0 mismatches |
| Main text V-G (study2.tex) | Each quoted difference and interval compared to the JSON and to the table row | all match: A-LIN -0.011 [-0.031, 0.009]; A-S-BD -0.002 [-0.033, 0.029]; A-S-s3 -0.033 [-0.071, 0.004]; A-MIL -0.009 [-0.044, 0.027]; KO-S-BD -0.053 [-0.082, -0.027]; KO-S-nbr 0.040 [0.013, 0.069]; KO-F-neighbourhood -0.062 [-0.096, -0.031]; seed range max 0.030; K = 336 |
| V-G and S-VII classification sentences | Recomputed from the JSON over all rows | exact: on L1 noise the upper bound is below 0 for A-S-tbv, A-S-ltex, A-S-nbr, A-S-pos, A-SF, A-UNL (and KO-S-BD, KO-F-neighbourhood); the lower bound is above 0 only for KO-S-nbr; the other 12 rows contain 0; the "other cells above zero" list is complete (A-LIN JPEG, A-S-BD impulse, KO-S-s3 JPEG; no other cell of any row has a lower bound above 0); KO-S-pos and KO-F-position cells are identical |
| Plan-level facts in S-VII | JSON, `controls.json`, `score_meta.json`, `P2-LRF-ABL-FIT/A-SF/spec.json`, `variants.json` | 3 000 item-cells = 4 x 450 + 4 x 300; 0 mismatches for NONE, LRF and KO-ALL; harness LRF at seed 0 decides every item as the frozen LRF (all eight cells 0); A-SF feature `rad`, selection budget "35 searches (35 times the frozen LRF's)"; seed 0 is `ss(4,99,0,0)`, `seed0_is_prefixed` true; predictions file SHA-256 `5c57ffac...` equals `meta.predictions_sha256`, 135 000 lines; 5 % of 336 = 16.8 ("about 17"); source feature counts 14, 5, 5, 4, 4, 3 sum to 35 (from the `spec.json` names) |
| `supp_tests_full_study2.tex` (all A6.4 quantities) | Parser against `a6_analysis.json` (family_L) and `family_LG.cells.*`: n, b, c, n_d, both accuracies, net, 90 % and 95 % intervals, Clopper-Pearson of b/n_d, exact one- and two-sided p, mid-p one- and two-sided, Holm p | 141 values, 0 mismatches. The impulse row keeps two-sided 0.058, lower bound 0.000, and prints mid-p two-sided 0.044 (below 0.05, printed, not hidden) |
| `supp_status_map_study1.tex` (status words) | Run files: s_m tested all false; no `runs/P2-GATE-OMNI*` or `runs/P2-GATE-H4*` directory; H3 `family = []` and `go = false`; `epred_score.formal_test = null`; E-pred five cells (P1 to P3, PS1, PS2); edec `n_cells = 5`, label descriptive; suite and Tier-3 labels exploratory; FOIL `status = tested`, `partial = false` | all status words agree with the run files |
| `tab_families_glance.tex` (decision words) | JSON: P label negative; S-C and PS p_holm 1; S-D2 p_holm 0.0004; S2 p_holm 0.5 and 1.0; B p = 1.0; H go = false; L1 confirmed; L3 not rejected; L4 rejected (Holm); L-NI label shown; L-LEN rejected; three LG cells rejected (Holm) | all 16 rows agree |
| M1 fix (Tier-3 sentence) | `tier3_fusion.json`: noise GM 0.676, MED 0.678, TM20 0.682, readings not distinguishable; JPEG and splice MED and TM20 readings "below" | fixed correctly in study1.tex and supplement S-II; M1 closed |
| M2 fix | "Holm-adjusted p = 0.382" now matches Table IV and Fig. 5 | closed |
| M4 fix | caption "Detection Items", Items column note, text "about 200", comment `table.{jpeg,noise}.q.n = 197, 198` | closed |
| M5 | `runs/P2-GATE-M4/items.jsonl` and `env-lock.txt` now tracked (commit bfebb3ac) | closed (but see N4) |
| M6, M7 pointer fixes | study1.tex cites `A2.3-AUDIT-PS-2026-10-29.md` line 75 for the 584 tests; setting.tex and study2.tex cite SAP A6.7 for 17 families and 0.5819 | closed |
| 5.2 GB | `runs/P2-ENV/hf_cache_sizes.json:total_gb_decimal = 5.229` (CLIP 1.714 + SigLIP 3.515) matches discussion.tex "5.2 GB" | main paper correct; supplement not updated (N1) |
| New wording facts | `folds_lrf.json:test[*].neg_restricted` true for 533 of 533 and `neg_len_restricted` true for 533 of 533; `manifest.json:length_matching.n_unrestricted = 0`; `spec.json:training_conditions` = clean, jpeg10, noise0.1, splice128 (shot, impulse, speckle were not training conditions); M1 and M4 `env-lock.txt` are 0 bytes; D0076 at 00:12 IST = 18:42 UTC and delegation about 00:10 IST = 18:40 UTC (the S-I conversion is correct) | all correct |
| Changed figure and scripts | Fig. 4 png viewed: no result numbers, only feature axes and weight maps; Figs 3 and 5 unchanged | no number issue |
| Abstract, introduction and conclusion changes | L-NI interval 0.009 to 0.053 added in intro and conclusion matches `ci90`; the abstract's negative sentence changed to "a random caption of an image sharing no annotated object category" (see N6); 247-word count recorded in the source comment, not recounted | numbers match |
| Path scan of every `runs/`, `research/`, `exp_p2/` path in the changed files | all exist; tracked except `runs/P2-GATE-M1/env-lock.txt` (0 bytes, untracked) and the intentionally absent `runs/P2-GATE-H4` | see N4 |

## New findings

| ID | Location | Printed | Source | Status |
|---|---|---|---|---|
| N1 | `supplement.tex` S-I Study 2 deviation 9 (line 289 at 9268e34b) | "The download of the reference encoders was 5.0 GB against 2 to 4 GB quoted to the first author." | `runs/P2-ENV/hf_cache_sizes.json:total_gb_decimal = 5.229`; discussion.tex deviation 6 now says 5.2 GB | MISMATCH between supplement (5.0) and main paper (5.2). Fix: 5.2 GB. This also supplies the source that M9 could not locate. |
| N2 | discussion.tex line 77; setting.tex line 100; study1.tex line 289; study2.tex line 117; supplement S-I lines 114 and 231 | "scripted and agent-run audits (see the Declaration)" and similar, six places | `declaration.tex` was replaced by the interim language-and-grammar text (D0101); it no longer names agent-run audits, roles or sections | Dangling pointer: six places send the reader to a Declaration that no longer says it. Restore an audit sentence in the Declaration or state the audit nature at each place (supplement S-I "Audits" does state it). Not a number. |
| N3 | study1.tex line 218 | "Table tab:glance lists every family with its status." | `tab_families_glance.tex` has 16 rows (Study 1: P, S-C, PS, S-D, S-M, S2, B, H; Study 2: L1, L3, L4, L-NI, L-LEN, three LG cells). Missing: R, H-M, S-Z, S-DN, S-D2 and the E and Tier-3 groups; the full map is `supp_status_map_study1.tex` | Wording overstates; "17 families" cannot be recovered from the glance table. Fix: "the main families" or also point to the supplement map. |
| N4 | discussion.tex deviation 9 comment | cites `runs/P2-GATE-M1/env-lock.txt` | file exists (0 bytes) but is untracked; the M4 counterpart was committed in bfebb3ac | Minor provenance gap. |
| N5 | headers of `supp_status_map_study1.tex`, `tab_families_glance.tex`, `supp_tests_full_study2.tex` | "generated by scripts/supp_status_map_study1.py", "tab_families_glance.py", "supp_tests_full_study2.py" | actual scripts are `tab_status_map.py`, `tab_glance.py`, `tab_tests_full.py` | Generator names in the headers do not exist. Fix the header strings in the scripts. |
| N6 | abstract, study1.tex, conclusion, discussion ("category-disjoint negatives", D0097) | "a random caption of an image sharing no annotated COCO category" for Study 1 | Verified for Study 2 (533 of 533, both wrong captions). For Study 1 the rule is in the code (`assign_negatives`) and plan; I did not re-derive category disjointness of the M2 to M4 folds from a run key | Not verified from a run file for Study 1; cite a key or verify against the fold annotations. |

Open from the first audit: M3 (L4 "0.001 below", true gap 0.0014, consistent with printed 0.049), M8 (constant-only comment gaps in setting.tex and captions), M9 convention (supplement S-II tables use "Source:" captions). M10 and M12 are closed by the Declaration and negatives-wording changes; M11 is clarified in the text ("2 526 image ids, some outside the captioned set").

## `\todo` at 9268e34b

One, in the non-anonymous build only: `declaration.tex` line 12 `[AUTHOR: exact repository URL and archive DOI]` (a mention on line 6 is a comment). None is visible in the anonymous PDF. The ablation RESULT, Declaration confirmation and delegation-record todos are gone.

## Required before the gate can tick

N1 (value), N2 (dangling audit disclosure), N3 (wording). N4 to N6 are provenance and header fixes.

---

# Incremental audit 2, 2026-10-30: HEAD fd191fdd against 9268e34b

Scope: new figures `fig_gate_method` (Fig. 2), `fig_detection` (Fig. 5), `fig_margins` (supplement), `fig_ablation` (Fig. 8), the redesigned `fig4_study2_weights` (Fig. 6) and the changed `fig5_study2_results` (Fig. 7); their captions; the tables moved to the supplement; the language review's edits (rounds 1 and 2); cross-references; the abstract. PDFs at HEAD: main 15 pp., supplement 18 pp., 0 "??" in either text extract; the working tree is clean against HEAD.
Verdict: **PASS WITH FIXES** (no number mismatch; the earlier findings N1 to N5 are closed; one residual pointer item F1 and one unchanged provenance note N6).
Ledger rows added: 0. Nothing was edited.

## What was checked and how

| Item | Method | Result |
|---|---|---|
| Plotted values of the four new figures | `runs/P2-PAPER-FIGS/fig_detection.json`, `fig_gate_method.json`, `fig_margins.json`, `fig_ablation.json` compared by script (scratch `figjson_check.py`) with `P2-GATE-M1/analysis.json` (q, TbV, rival means and intervals, paired differences), `P2-GATE-M4/analysis.json` (`calibration.fap_check.per_alpha.*` F, bootstrap interval, Z; `split_replication`; `s_d2`), `P2-LRF-L1/a6_analysis.json` (b, c, n of L1 and L-NI), `P2-LRF-ABL-SCORE/ablation_analysis.json` (acc, d, ci95 of all 21 rows on the L1 noise cell) | 0 differences. 48 detection values, 3 calibration points plus the split replication, margins counts (b + c + both correct + both wrong = 450 in both cells: 58, 27, 303, 62 and 27, 13, 386, 24), 21 ablation rows |
| PNGs read | Figs 2, 5, 6, 7, 8 and the supplement margin figure were viewed. Visible numbers: Fig. 2 n_cal = 300, alpha 0.01/0.05/0.10, share and share-minus-alpha points (-0.0036, -0.0044, -0.0044) and the open re-split marker (-0.0031); Fig. 5 n = 200, 200, 197, 198 and the signs and AUROC positions of q, TbV and the rival, open diamonds at about -0.198 and -0.258; Fig. 6(a) group counts 7, 3, 8, 4, 6, 6, 1 = 35, `db7fdb4e` and the sum limit 8; Fig. 7 p = 0.0005, 0.382, 0.049, margin -0.03; Fig. 8 row order and signs; margin figure b = 58, c = 27, b = 27, c = 13 | all agree with the run files |
| Fig. 6(b) | `fig4_meta.json`: shown features rank_B, nb3mean_ltex, tbv, itemsd_ltex, itemsd_nbr, nbr (ranges 0.349, 0.179, 0.171, 0.170, 0.168, 0.100; the next is rad at 0.089), items 0, 1, 2 in file order | matches the caption "six of 35 with the largest effect range", "first three items by position" |
| Captions (Figs 2 to 8, supplement margin figure) | Every number against the sources above: n_cal 300, 500 test pairs, 10 000 resamples, 2 000 re-splits (`reps = 2000`), 492 and 497 items, Holm p = 0.0004, n = 450, margin -0.03, 90 % and 95 % intervals | all correct |
| Abstract | Whitespace word count 248 (limit 250). All numbers equal the source abstract of the first audit, except that the clause "at the preregistered one-sided level 0.05" was dropped (the ruled overflow valve R8/F1, language report round 2); the one-sided level 0.05 stays in V-D ("preregistered one-sided $\alpha=0.05$") | PASS; the numbers 0.733, 0.802, 0.069, 0.029, 0.109, 0.0005, 0.009, 0.053, 0.002/0.006/0.004/0.010, 500, 450, 1.4 billion are unchanged |
| Language-review number changes (`drafts/integrity-diff-language.md`) | Independent multiset of number tokens in prose of every section file, 9268e34b vs HEAD (scratch `numdiff.py`) | Differences are exactly the intended ones: abstract lost 0.05 (R8/F1); B2 "three percentage points (0.03 in accuracy)" gained 0.03 in introduction, V-D and conclusion (equals `family_L.L-NI.margin = 0.03`); B15 "sigma = 0.10" to 0.1; B16 merged 0.05 clause; B22 and B23 p-values written out (speckle 0.006, 0.011, 0.011; impulse "both 0.029", two-sided 0.058) equal the JSON (0.00568, 0.01135, 0.01135; 0.02903, 0.02903, 0.05806); calibration statistic and flagged-share numbers moved from the Results text to Fig. 2 and S-II (they still appear in S-II Tables S-cal and S-flags: -3.59, 2.13, 0.036 to 0.044, 0.089); detection numbers moved into Fig. 5 (the introduction still gives 0.961, 0.955, 0.561, 0.503); ablation interval numbers moved from the text into Fig. 8 and S-VII (1 672 table values were already verified at 9268e34b) |
| M1 and N1 to N5 | Re-read at HEAD | N1 closed (supplement now says 5.2 GB); N2 closed (no "see the Declaration" remains; the text says "automated audits run in the authors' own pipeline (not independent reviews)"); N3 closed (the glance table is status only, restored to the status-map wording "not run (gatekept: P+ empty)", "headroom not met; H4 not run"; the sentence "lists every family" is gone); N4 closed (`runs/P2-GATE-M1/env-lock.txt` tracked, commit 39062dcf); N5 closed (the three table headers now name `tab_status_map.py`, `tab_glance.py`, `tab_tests_full.py`, which exist); the Tier-3 sentence of M1 in the main text now reads that the median and trimmed-mean combiners are reported in S-II, no contradicted claim |
| Glance and status words after the rewording | Decision words re-derived from the run files at 9268e34b are unchanged; the new "run, formal" statuses for L1, L3, L4, L-NI, L-LEN, LG and S-D/S-D2 merge match `n` and `tested` fields | agree |
| Notation changes (language review and notation pass) | tau_j to v_j (patch pixel variance), the feature score q_j to r_j in the feature tables, the pair length n to ell in III-A, "gatekept" to "conditional on" in the Study 1 text | consistent between Fig. 6(b) titles, the main feature text, S-IV feature table and the supplement; the detection score keeps q_j = -u_j; the feature code names (`q`, `nb3mean_q`) in S-IV tables are the code names |

## Cross-references (no dangling Table, Fig. or section pointer in the printed text)

- Numbering at HEAD (from `main.aux`): Fig. 1 measurement, Fig. 2 gate method, Fig. 3 frontier, Fig. 4 family P, Fig. 5 detection, Fig. 6 weights, Fig. 7 Study 2 results, Fig. 8 ablation; Table I glance, Table II Study 2, Table III reference encoders. Every `\cref` in main and supplement resolves (0 "??" in both PDFs).
- Hard-coded section pointers in main prose to the supplement all land on the right section: S-I (pins, plans, deviations, time input, protocol details), S-II (family P table, headroom, calibration and flags, PS table, detection values, equal-size gates, denoising, E-dec and E-pred, suite, Tier-3, cost, proof of Proposition 2), S-III (family H), S-IV (full tests with mid-p, margin figure, n rule, feature table, weight-model search), S-VI (reference encoders and pixel parity), S-VII (ablation). Checked one by one for 41 pointers.
- Supplement pointers to main figures and tables, from the PDF text: "Fig. 4 of the main paper" (family P intervals), "Fig. 5" (detection values), "Fig. 3" (frontier in the proof), "Fig. 6(a)" (feature groups), "Fig. 6" (shape functions), "Table II" (counts b and c), and the sources list: Fig. 1, 2, 3, 4, 5, 6, 7, 8, Table II and Table III. Each is the figure or table it names.
- Section pointers "Section IV-C", "Sections IV-A and IV-B", "Section V-A", "Section V-B", "Section III" in the supplement are correct for the HEAD section numbering.

## Findings

| ID | Location | Printed | Status |
|---|---|---|---|
| F1 | `supplement.tex` sources list (S-VIII, lines 1305, 1309, 1318, 1329 at HEAD): "Family P table (Table S5; former main Table I)", "positive control (former main Table II)", "Feature groups (... former main feature table)", "item-level margins (... former main ...)"; and the printed footnote "Moved from the main paper" under the family P table | "former main Table I", "former main Table II" | Dangling for a reviewer: the main paper now has Table I = glance and Table II = Study 2 families, and the earlier layout was never seen by the reader. Remove the "former main ..." and "moved from the main paper" phrases. Not a number error. |
| N6 (unchanged) | "category-disjoint negatives" for Study 1 (abstract, IV-C, Conclusion, VI-C) | Verified from `folds_lrf.json` for Study 2 (533 of 533, both wrong captions); for Study 1 the rule is documented in `exp_p2/gate/folds.py` line 7 and the protocol text, but no run key carries it | E3 (code reading), not E4. Cite a key or verify against the fold annotations if the claim is to be stated as measured. |

## `\todo` at fd191fdd

`declaration.tex` was reduced earlier; `main.tex` now carries one camera-ready-only `\todo{AUTHOR: corresponding author, as for Paper 1}` in the non-anonymous author block, plus the repository URL and archive DOI todo in `declaration.tex` (non-anonymous build only). None is visible in the anonymous PDF.

## Required before the gate can tick

F1 (remove "former main Table ..." phrases). N6 is a provenance wording note, not a number defect. No value mismatch exists in the abstract, text, tables, figures or supplement at fd191fdd within the scope audited.
