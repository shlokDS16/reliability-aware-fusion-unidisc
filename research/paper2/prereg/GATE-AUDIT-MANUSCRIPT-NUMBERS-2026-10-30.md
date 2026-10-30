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

---

# Closure re-check of F1 and N6 (after 7e874e76), 2026-10-30

Method: PDFs read with `pdftotext -layout` (`paper2-tnnls/main.pdf`, `paper2-tnnls/supplement/supplement.pdf` at the working tree, rebuilt 12:32 after the coordinator's final rewording of item 18); the 2185a70f PDFs taken with `git show 2185a70f:<pdf>`; diff of 7e874e76 against 2185a70f read. Nothing was edited.

## F1: CLOSED

- Search of both current PDFs for "former", "Moved from", "moved from", "moved to", "previously": no hit of the editing-history kind. The old supplement had five (S-I and S-IV headings "Moved From the Main Paper", the family P table footnote "Moved from the main paper (A4.2.5 ...)", and three "former main ..." entries in S-VIII, plus item 18). The current text has none of them. The only remaining word "moved" in the main PDF is in the disclosure list item (3) of the appendix: "its table moved to the supplement". It was already there at 2185a70f, states where the table is (it is not a reference to a former layout) and is not the F1 pattern; noted as optional wording, not a blocker. Other "moved" hits in the supplement (row A-1 "moved the code pin", "parity files were moved unchanged") are record-of-event statements about runs.
- Subsection headings now read "Protocol Details of Study 1 (Main Paper, Sections IV-A and IV-B)" and "Weight-Model Search ... (Main Paper, Section V-B)": they name the section the detail belongs to.
- S-VIII sources list pointers re-read against the PDF: "Family P table (Table S5)" (Table S5 = full test of family P, line 299); "Table S10 (positive control)" (S10 = positive-control table, line 386); "Feature groups (Fig. 6(a) of the main paper)" with full table in the S-IV feature table; "Figure S1 (item-level margins, descriptive)" (Fig. S1 caption: n = 450 items, descriptive). Each names the right table or figure.
- Item 18 of the S-I deviation list now reads: "The time-input table, planned for an appendix of the main paper, is reported in this supplement instead." Accurate: Table S4 (S-I section E, "Time Input of the Released Configuration") holds the evidence, and the main paper has no time-input table (main text only states the finding in Section III and defers to the supplement). It keeps the deviation disclosed and has no former-layout wording. The intermediate wording ("reported in this supplement only") was superseded and is not in the PDF.
- Family P table footnote now reads "The main paper shows the P-only summary figure; this table holds the full family P record, including the 98.33% interval." Accurate (Fig. 4 main paper; Table S5 carries the 98.33% interval). The deleted "A4.2.5" token is the only number-like token that left the supplement (see item 3).

## N6: CLOSED (as a count recomputed from the fold files; see the limit below)

- `runs/P2-PAPER-TABLES/negatives_check.json`: study1 500/500/500, 0 fallback; study2 533/533/533, 0 fallback.
- Independent recount (scratch script, `python -I`): `runs/P2-GATE-FOLDS/folds.json` test (300) + test_ext (200) = 500 items, `neg_restricted` True for 500, False for 0; `runs/P2-LRF-FOLD/folds_lrf.json` test = 533 items, `neg_restricted` True for 533; the length-matched negative `neg_len_restricted` also True for 533 (matches "both wrong captions"). SHA-256 of both files equals the value in the check file (450edb54...f311 and a545a83e...1de).
- Structural check of the fold files: for all 500 and all 533 items the negative's `neg_idx` points to a different item whose `image_id` and `caption` equal `neg_image_id` and `neg_caption`, and the negative caption differs from the true caption (0 violations).
- Rule semantics: `exp_p2/gate/folds.py` `assign_negatives` sets `neg_restricted` True only when the candidate pool is non-empty under "no shared annotated COCO category" (`not (cats[i] & cats[j])`), otherwise False (fallback). So True for every item is the category-disjoint statement. The COCO instance-annotation file is not on disk here, so I did not re-derive category sets from raw annotations; the evidence is the flag written by the code at fold build (E3/E4: recorded run output, not a re-derivation from annotations).
- `% run:` comments: `study1.tex` (line after "The 494 image ids ...") cites `negatives_check.json:study1.{n_items (= 500), n_category_disjoint (= 500), n_fallback (= 0)}`; `study2.tex` cites `study2.{n_items (= 533), n_category_disjoint (= 533), n_fallback (= 0)}`. Both keys exist with those values.
- Printed claims: abstract, IV-C (Study 1 text, "shares no annotated COCO category"), VI-C and Conclusion ("category-disjoint negatives") are now backed by these keys; the Study 2 text claim already had `folds_lrf.json:test[*].neg_restricted`.

## Item 3: no printed number changed: CONFIRMED

Multiset of number tokens (regex `\d+(?:[.,]\d+)*`) in `pdftotext -layout` output, 2185a70f PDFs against the current ones: main PDF identical (only old: none; only new: none). Supplement: only old = {"4.2.5": 1} (the plan-section label inside the deleted "Moved from the main paper (A4.2.5 ...)" footnote), only new = none. No result number was added, dropped or changed.

## Verdict

F1 CLOSED. N6 CLOSED (count and flag recomputed; category sets not re-derived from raw COCO annotations, which are not on disk). Number tokens: unchanged. Blockers from this re-check: none. Optional: the phrase "its table moved to the supplement" in the main appendix item (3) could read "its table is in the supplement" for consistency. Ledger rows added: 0. Not committed.

---

# Incremental audit 3, 2026-10-31: HEAD 175efa89 (Mask-DiFuser presentation pass) against the audited state at 7e874e76

Scope: new qualitative figure (`figures/fig_qualitative.*`, `scripts/fig_qualitative.py`, `runs/P2-PAPER-FIGS/fig_qualitative.json`), new exploratory Table IV and its supplement version (`tables/tab_baselines.tex`, `tab_baselines_full.tex`, `scripts/tab_baselines.py`), Algorithm 1, every number added or moved in `sections/*.tex` and `supplement/supplement.tex` (diff HEAD~1..HEAD plus the integrity diff `paper2-tnnls/drafts/integrity-diff-mask-difuser-pass.md`), and cross-references after Proposition 2, Fig. 3 and Fig. 5 moved to the supplement. The "Denoise" rows (pending) were skipped as instructed. PDFs at HEAD: `main.pdf` 15 pp., `main_camera.pdf` 15 pp., `supplement.pdf` 21 pp.; each PDF is newer than every `.tex` it builds from. Nothing was edited.

**Verdict: PASS WITH FIXES.** No value mismatch anywhere in scope. One wording item that the gate set earlier as required (F1), one layout item (F2), one note (F3).

## What was checked and how

| Item | Method | Result |
|---|---|---|
| Table IV compact (10 rows x 4 columns) and full table (40 accuracies, 36 differences with both interval ends) | Independent script (scratch `a3/tabcheck.py`, `python -I`) re-read `runs/P2-LRF-L1/a6_analysis.json` (family_L acc_b, acc_a, net, ci95), `runs/P2-LRF-ABL-SCORE/ablation_analysis.json` (rows[A-UNL, A-SF, A-LIN, A-S-BD, A-MIL].cells.L1_*.{acc, vs_NONE.d, vs_NONE.ci95}) and `runs/P2-LRF-E2/combiners.json` (cells.*.arms.{MED, TM20, TM-G}.{acc, vs_NONE.diff, ci95}); rounded half-up to 3 decimals; parsed the printed `.tex` cells (sign, accuracy, both interval ends, bold, underline) | 0 differences; each printed difference also equals variant accuracy minus NONE accuracy to 1e-9 in all 36 cells; the text of `main.pdf` Table IV equals the `.tex` |
| Marked best and second best | Ranked by integer correct count (acc x 450, distinct values) over all 10 rows | Noise: LRF 361 (best, bold), A-S-BD 360 (second, underlined). JPEG: A-LIN 398, A-S-BD 392. Splice: A-LIN 419, LRF 417. Clean: A-S-BD 415, A-LIN 414. All eight marks printed in both tables are the correct ones; no tie occurs |
| "The median, the trimmed mean, and the trimmed-at-gate-count mean had lower accuracy than no weighting in every condition" | 12 accuracy pairs (MED 0.716/0.829/0.864/0.862, TM20 0.716/0.827/0.873/0.869, TM-G 0.727/0.842/0.887/0.884, against NONE 0.733/0.849/0.896/0.887) | true for all 12 |
| V-H prose numbers (0.802; 0.002 and 0.011 lower, intervals contain 0; 0.884 vs 0.864, difference 0.020 [0.004, 0.038]; 0.931 vs 0.927; 0.922 vs 0.918) | `ablation_analysis.json` vs_LRF: A-S-BD noise d -0.0022 [-0.0333, 0.0289]; A-LIN noise d -0.0111 [-0.0311, 0.0089]; A-LIN JPEG d 0.0200 [0.0044, 0.0378], acc 0.8844; A-LIN splice acc 0.9311; A-S-BD clean acc 0.9222; LRF 0.8022, 0.8644, 0.9267, 0.9178 from `a6_analysis.json` | all agree; each sentence carries a `% run:` comment naming the right file and keys |
| Number-token multiset of the prose (comments stripped), HEAD~1 against HEAD, all section files and the supplement (scratch `a3/numdiff.py`) | `study1.tex` loses the six detection numbers, 0.0004, 492, 497 (moved verbatim to supplement S-II.E); `study2.tex` gains exactly the V-H numbers above plus 303, 58, 27, the three COCO ids and the Algorithm 1 constants; no other section file changes a number token | no unreviewed number |
| Moved detection values (-0.198 [-0.211, -0.186], -0.258 [-0.267, -0.250], Holm p = 0.0004, 492 and 497 items) | `runs/P2-GATE-M4/analysis.json` s_d2.per_corruption: diff_mean -0.19811 / -0.25818, ci95 [-0.21072, -0.18562] / [-0.26677, -0.24966], p_holm 0.00040, n_eligible 492 / 497, rival tex_neg | agree |
| Shortened main-text detection paragraph ("the score was below the rival under JPEG and under noise (Holm-adjusted p=0.0004)") | same keys: both differences negative, both p_holm 0.0004 | agrees; the falsifier sentence is verbatim |
| Algorithm 1 constants | `runs/P2-LRF-FROZEN-LFIX/spec.json`: n_features 35, caption_slot_len 13, model_sha256 `db7fdb4e9f...`, family F1 logistic GAM with hinge basis, standardisation `(X - mu)/sd`; m = 1 024 = the 32 x 32 grid | agree; the algorithm adds no step beyond eq. (lrf-decision) |
| V-H design description | "500 design items": spec `n_items` 500; four rules without a fitted weight = A-UNL, MED, TM20, TM-G; TM-G definition in `combiners.json` (k = g // 2 per tail, g = flag0.05 count) matches "half the gate flagged per tail"; A-UNL = `1 - rank(s3)` (ablation plan row A-UNL); A-S-BD is the GAM on the 14 S-BD columns (groups B and D) | agree |

## Qualitative figure (E4 rule)

- `runs/P2-LRF-L1/predictions.jsonl` (1 800 rows: 450 per condition for clean, jpeg10, noise0.1, splice128; condition noise0.1 has 450 distinct idx). Rule applied independently, in idx order, on the primary-negative fields `y_none` and `y_lrf`:
  - kind (i) both correct: 303 items, first idx 0 (gid 8000, COCO 335177);
  - kind (ii) NONE wrong, LRF correct: 58 items, first idx 1 (gid 8001, COCO 520324);
  - kind (iii) NONE correct, LRF wrong: 27 items, first idx 8 (gid 8008, COCO 224724).
  These equal `fig_qualitative.json` items[*] (kind, idx, gid, image id, `n_items_of_this_kind_in_fold`) and the counts printed in the text and caption (303, 58, 27). Counts 58 and 27 are also b and c of L1 in `a6_analysis.json`. The eight stored fields of each shown item (`y_none`, `y_lrf`, `m_none`, `m_lrf`, `y_none_L`, `y_lrf_L`, `w_sum`, `w_mean`) equal the predictions row exactly. Kind (iii) is shown, as the plan requires.
- The rendered figure was read: row labels "unweighted correct; LRF correct", "unweighted wrong; LRF correct", "unweighted correct; LRF wrong"; sums +358.3 / +3.37, -215.9 / +0.30, +19.3 / -0.67 equal `sum_delta` and `sum_w_delta` (358.274, 3.373; -215.892, 0.304; 19.256, -0.667) and every sign agrees with the printed verdict (positive sum is correct, ties wrong); image ids and fold indices 0, 1, 8 as in the file; the Delta colour bar clip of 1.9 equals 1.927 (99th percentile of |Delta|), weight bar top 0.8 against vmax 0.8465.
- Caption sentences (descriptive; not evidence of reliability tracking; COCO val2017 licence) agree with the plan text and the JSON `attribution`.
- Not re-run: pixel regeneration and the VQ-token parity check (GPU; the JSON itself says "NOT run"); the figure was read, not rebuilt.

## Cross-references and pointers

- Numbering at HEAD from the PDFs: main Fig. 1 measurement, 2 gate method, 3 family P, 4 weight schematic, 5 family-L results, 6 qualitative, 7 ablation; Tables I glance, II Study 2, III reference encoders, IV exploratory comparison; Algorithm 1. Every main-text pointer read in the PDF text is correct ("Fig. 4 draws the model ... Fig. 6 shows three fresh-fold items", "Fig. 5 shows the net change ... Table II", "Fig. 7 shows every variant", "Table IV", "CLIP and SigLIP ... Table III", "Algorithm 1"). No "Proposition 2" remains; "Proposition 1" and "Fig. 2(b),(c)" are unchanged and right.
- "??": 0 in `main.pdf`, 0 in `main_camera.pdf`, 0 in `supplement.pdf` (pdftotext).
- Supplement numbering: Fig. S1 detection (S-II.E), S2 frontier (S-II.M), S3 item-level margins (S-IV.B), S4 partial dependence (S-IV.D); Table S11 detection values, Table S30 full comparison. In-supplement pointers and the S-VIII list use these numbers consistently.
- Supplement pointers to the main paper: "Fig. 3 of the main paper" (family P), "Fig. 4 of the main paper" (feature groups, twice), "Table II of the main paper" (b, c), "Table IV of the main paper" (S30), "Section IV-A" (proposition notation), "Section V-B" (weight-model search): each correct. The `M-` references to Lemma 1 and eqs. (8) to (10) of the main paper print correctly.
- Main-paper pointers to the supplement that are new or changed: "supplement S-II" (extension, frontier, detection values: land in S-II.M and S-II.E), "supplement S-IV" (learned shapes: S-IV.D), "supplement S-VII" (comparison with intervals: the label sits in S-VII; see F2). All land on the right section.
- Old `\cref{prop:snrcorr}`, `fig:frontier`, `fig:detection` occur only in `sections/appendix.tex`, which `main.tex` does not input (comment at `main.tex` line 125), so nothing dangles.

## Findings

| ID | Location | Printed | Status |
|---|---|---|---|
| F1 | `supplement.pdf`: S-IV.D "Figure S4 (moved from the main paper) shows ..."; S-VII disclosure "the frozen LRF's shape functions (moved from the main paper, Fig. S4)"; S-VIII "Figure S2 (theory, no data; moved from the main paper)" and "Figure S1 (token detection, moved from the main paper; ...)". In `supplement.tex`: `\Cref{sfig:pd} (moved from the main paper)`, `(moved from the main paper, \cref{sfig:pd})`, `(theory, no data; moved from the main paper)`, `(token detection, moved from the main paper; ...)` | edit-history wording | The pattern of the earlier finding F1 (closed at 7e874e76: a reviewer never saw the earlier layout) is back in four printed places. Not a number error. Delete the parentheticals or say "shown here". TeX comments that say "Moved from ..." are not printed and are fine. The earlier audit listed this as required, so the gate does not tick until it is fixed |
| F2 | `supplement.pdf` page 20: Table S30 (label `stab:compare`, belongs to S-VII) is printed after the S-VIII heading and list; main-text pointers say "supplement S-VII" | float placement | Layout only; found by its number S30, which the S-VII text and the S-VIII list cite. Optional: a float barrier before S-VIII. Table S29 sits on the same pages |
| F3 (note) | Table IV noise column and the V-H "highest accuracy" sentences | LRF 361 vs A-S-BD 360 correct items; splice LRF 417 second | Marks are correct but one item apart; the caption already calls them descriptive and post hoc. When the "pending" DN rows are filled, `marks()` ranks over every row with a number, so bold and underline can move; the V-H sentences and the `% DN-SENTENCE` must then be re-checked against the final table. Also `figures/fig4_study2_weights.png` is modified and `figures/fig4b_pd_curves.png` is untracked in the working tree; the PDF builds use the PDF figures, so no printed value is affected, but commit or discard them for consistency |

## Required before the gate can tick

F1 (remove the four printed "moved from the main paper" parentheticals). F2 optional; F3 conditional on the DN rows. No value mismatch exists in the new figure, Table IV (main and supplement), Algorithm 1, the prose of `sections/*.tex` or the supplement. Ledger rows added: 0. Not committed.



# Incremental audit 4, 2026-10-31: HEAD 87bc6970 against 927ec942 (red-team fixes F1-F15, denoiser E1 integration, page-fit cuts)

Verdict: **PASS WITH FIXES.** Every new or changed number matches its run file and key. Three printed defects (none a value mismatch) need a fix before the gate ticks: A1, A2, A3. Audit-3 finding F1 is still open (A4). Method: `git diff 927ec942..HEAD` for `sections/`, `supplement/supplement.tex`, `tables/`, `scripts/`; Python scripts reading the JSON files named below; `pdftotext` of the three PDFs; page 12 of `main.pdf` rendered and read.

## Numbers recomputed (all match)

- Table IV (`tab_baselines.tex`) and its supplement twin (`tab_baselines_full.tex`): every accuracy, difference and interval re-read from `runs/P2-LRF-L1/a6_analysis.json` (family_L acc_b, acc_a, net, ci95), `runs/P2-LRF-ABL-SCORE/ablation_analysis.json` (rows[id].cells.<L1 cell>.acc, vs_NONE.d, ci95; the NONE and LRF references equal the a6 values), `runs/P2-LRF-E2/combiners.json` (MED, TM20) and `runs/P2-LRF-DN/dn_analysis.json` (DN+NONE, DN+LRF; noise0.1 and jpeg10 only). 0 mismatches. The TM-G row is gone from both tables (D0108).
- Italic marks, by integer correct items (acc x 450): noise DN+LRF 385 (next DN+NONE 380, LRF 361); JPEG A-LIN 398 (next A-S-BD 392); splice A-LIN 419 (next LRF 417); clean A-S-BD 415 (next A-LIN 414). The printed italics (read on the rendered page 12) are exactly these four cells; there is no bold or underline. The earlier F3 condition (marks move when DN rows are filled) is resolved: DN+LRF now takes the noise mark, and V-H no longer ranks.
- V-H denoiser sentence and supplement S-VII paragraph against `dn_analysis.json`: noise 0.733, 0.802, 0.844, 0.856; DN+NONE vs NONE 0.111 [0.067, 0.156], b/c 80/30; vs LRF 0.042 [0.002, 0.082], 53/34; DN+LRF vs LRF 0.053 [0.011, 0.096], 61/37; DN+LRF vs DN+NONE 0.011 [-0.020, 0.044], 30/25. JPEG 0.849, 0.864, 0.853, 0.813; vs LRF -0.011 [-0.044, 0.024], 29/34 and -0.051 [-0.089, -0.013], 29/52; vs NONE 0.004 [-0.031, 0.038] and -0.036 [-0.078, 0.004]; DN+LRF vs DN+NONE -0.040 [-0.069, -0.011], 13/31. The accuracies also equal the counts of `y_none`/`y_lrf` in `runs/P2-LRF-DN/predictions.jsonl` (900 rows; noise 380 and 385, JPEG 384 and 366 of 450).
- VI-B reading 6, VI-C denoiser sentence, "Six inexpensive alternative readings" (six enumerated): consistent with the same values.
- VI-C linear-logit sentence: A-LIN 0.7911, 0.8844, 0.9311, 0.9200 against LRF 0.8022, 0.8644, 0.9267, 0.9178 gives "at or above LRF in three of four" (noise below); `vs_NONE.ci95` excludes 0 in all four (noise 0.058 [0.020, 0.096]; JPEG 0.036 [0.007, 0.064]; splice 0.036 [0.011, 0.062]; clean 0.033 [0.009, 0.060]); the preregistered JPEG test of LRF: `family_L.L3` net 0.016, ci95 [-0.013, 0.044], p_holm 0.38 (no difference detected).
- F1 rival AUROC (IV-C4): `runs/P2-GATE-M1/analysis.json` table.jpeg/noise tex_neg 0.7558 [0.7429, 0.7676] and 0.7681 [0.7597, 0.7765]; q 0.5613 [0.5473, 0.5750] and 0.5028 [0.4925, 0.5134]; `paired_q_vs_best_cheap` (rival tex, sign -1) -0.1945 [-0.2141, -0.1748] and -0.2653 [-0.2782, -0.2527]. All printed to three decimals correctly. Note: the AUROCs use n = 197 and 198 items, the paired contrast n_items = 200; the text prints no n, so no error.
- Qualitative figure sentence: counts both-correct 303, only-LRF 58, only-unweighted 27, both wrong 62 (sum 450) recomputed from `runs/P2-LRF-L1/predictions.jsonl`, condition noise0.1. Licence text for image ids 335177, 520324, 224724 equals `runs/P2-PAPER-FIGS/fig_qualitative_licences.json` (licence names and Flickr URLs).
- Algorithm 1: n_features 35, caption_slot_len 13, Q = 8 knots (selected_cfg.knots), model SHA-256 prefix db7fdb4e, layout and preprocessing strings agree with `runs/P2-LRF-FROZEN-LFIX/spec.json`.

## "99.8% / 99.7% token-code match"

Stored where: `runs/P2-LRF-DN/dn_analysis.json` cells.noise0.1 and cells.jpeg10 `.corruption_reproduction` (token_equal_fraction 0.99797 and 0.99727; items_all_tokens_equal 69 and 73), computed by `corruption_check()` in `analysis/paper2/lrf/e1_denoise.py` (line 98): VQ codes of the regenerated corrupted-but-not-denoised image (`<cond>_nlm_codes_corr` in the DN arrays) against `<cond>_codes` of the L1 arrays. I re-ran that comparison independently from the 450 array pairs: 0.9979709 and 0.9972656, 69 and 73. Printed 99.8, 99.7, 69, 73 are correct, and the sentence says the match was not exact. The arrays are untracked (SHA-256 manifest committed), as for the other runs.

## Deviations box: empty lock file, environment record predates the run

Confirmed. `runs/P2-LRF-DN/env-lock.txt` is 0 bytes (written 2026-10-30 23:58:47; the L1 and LG lock files are 0 bytes too). `runs/P2-ENV/pip-freeze-2026-10-30.txt` (3302 bytes) was committed in b44fd0b5 at 2026-10-30 01:07:39, about 23 hours before the run. Wording note only: that commit says the file was regenerated from `importlib.metadata` because `pip freeze` was empty, so "pip freeze" is a file name, not the command.

## E1 plan before the run (git times, +0530)

83ac79f8 plan (`EXPLORATORY-PLAN-BASELINES-2026-10-30.md`, "written before any computation"; E1 fixes the denoiser, h = hColor = 25.5, windows 7 and 21, "no other setting is tried", the arms, 450 items, bootstrap 10,000, seed 0) 2026-10-30 23:31:10 -> ce8ab86a run code and tests 23:45:51 (LAUNCH.md 23:45:03) -> run start (config.json, env-lock.txt) 23:58:47 -> predictions.jsonl 2026-10-31 00:56:44 -> 456a30a7 results commit 00:57:48. The plan precedes the run by 27 minutes. `config.json` records the same parameters as the plan.

## Other checks

- "??": 0 in `main.pdf` (15 pp), 0 in `main_camera.pdf` (15 pp), 0 in `supplement.pdf` (21 pp). PDFs are newer than the `.tex` files they build from.
- Pointers: main "supplement S-II" (proof, extension), "S-VII" (comparison, denoise paragraph, Table S30), "S-VIII" (colour scales and licences) all land on those sections in `supplement.pdf`. The main paper's "Section V-H, Table IV", "Fig. 6", "Section VI-C" resolve. The `\cref{stab:compare}` in the denoise paragraph prints "Table S30".
- Cuts: numbers removed from `sections/`, `supplement.tex` and the tables were extracted from the diff and searched in the text of the new main and supplement PDFs. The only value with no remaining citation anywhere is the TM-G row of Table IV (0.727, 0.842, 0.887, 0.884; differences from NONE such as -0.007 [-0.016, 0.000]); its removal is ruling D0108 and the values remain in `runs/P2-LRF-E2/combiners.json`. The "LRF 0.802 highest; additive 0.002 and linear logit 0.011 lower" sentence is gone from V-H, but the values stay in S-VII's ablation table. The pixel-parity pointer removed from the Table III note remains in S-I (item on `pixel_parity: not run`). Nothing else is orphaned (the other regex hits were table-formatting false alarms).

## Findings

| ID | Location | Printed | Status |
|---|---|---|---|
| A1 | `supplement.tex` lines 296-298, S-I item 13 (`supplement.pdf` p. 5) | "plan E1 in olinkurlresearch/paper2/tnnls/EXPLORATORY-PLAN-BASELINES-2026-10-30.md, commit exttt83ac79f8" | The source holds a literal newline before `olinkurl` and a tab before `exttt`: the `\n` of `\nolinkurl` and the `\t` of `\texttt` were collapsed when the line was written (the heredoc backslash problem of the memory note). The printed sentence is garbled and the plan path is not a link. Fix: restore `\nolinkurl{...}` and `\texttt{83ac79f8}` with Edit. Not a number error |
| A2 | `sections/study2.tex` lines 325-326 (Table IV note, main PDF p. 12; the same words are in the caption draft of `scripts/tab_baselines.py` and `tables/tab_baselines.tex`) | "4 of the 10 learned refits of the exploratory ablation are shown ... all 10 are in supplement S-VII" | Count is wrong. `ablation_analysis.json` block 3a has 10 variants: nine learned (A-LIN, A-S-BD, A-S-s3, A-S-tbv, A-S-ltex, A-S-nbr, A-S-pos, A-SF, A-MIL; supplement S-VII "Variants") and one unlearned (A-UNL). The table shows four learned refits plus the unlearned rank weight. Fix: "4 of the 9 learned refits (and the unlearned rank weight) ... all 10 variants are in supplement S-VII". Ruling D0110 itself says "10", so its wording needs the same correction |
| A3 | `supplement.tex` lines 299-300 (S-I item 13, printed as "item 3") | "the environment record of item 3 is dated before that run" | The environment-record item is item 4 in the printed S-I list ("4) The environment lock files of the design-run, re-score, L1, and LG stages are empty ..."); item 3 is "Row A-9 (pin 84be25c4) changed one test only". Fix: "item 4" or drop the number |
| A4 | `supplement.tex` lines 1194, 1279, 1440, 1452 | "(moved from the main paper)" in four printed places | Audit-3 finding F1 is still open at HEAD; the gate does not tick until it is removed |
| A5 (note) | `scripts/fig4_study2_weights.py` | the committed script now writes `runs/P2-PAPER-FIGS/fig4_meta_2026-10-31.json`, but that file does not exist | The script edit (F15) was not run after the change, so the trace file the docstring promises is absent. The printed figure is unchanged (no `fig4_study2_weights.pdf` diff since 927ec942), so no printed value is affected. Run the script once or note it. `fig4_study2_weights.png` (modified) and `fig4b_pd_curves.png` (untracked) are still in the working tree, as in audit 3 |

## Required before the gate can tick

A1 (garbled S-I item 13), A2 (9 learned refits, not 10), A3 (item 4, not 3), A4 (the four "moved from the main paper" parentheticals). A5 optional. No value mismatch exists in Table IV (main and supplement), the V-H, VI-B, VI-C, deviations and S-VII denoiser text, Algorithm 1, the rival-AUROC sentence, the qualitative-figure counts or the licences. Ledger rows added: 0. Not committed; the gate is not ticked in `progress.md`.
