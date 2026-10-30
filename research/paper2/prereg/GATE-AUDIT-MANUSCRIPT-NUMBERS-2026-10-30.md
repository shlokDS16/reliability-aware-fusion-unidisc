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
