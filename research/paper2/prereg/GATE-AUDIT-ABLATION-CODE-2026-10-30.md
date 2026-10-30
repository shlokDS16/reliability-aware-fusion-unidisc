---
agent: gate-auditor
date: 2026-10-30
brief: Code audit of the exploratory Tier-3 ablation (Study 2, LRF) before any fresh-fold scoring; stage 1 commits 45f4a717 and 4efb4328 against ABLATION-PLAN-2026-10-30.md (commit 506818c7)
verdict: PASS WITH FIXES (0 FIT-PATH fixes; no refit needed; 1 required SCORE-PATH item that needs no code change; 5 optional SCORE-PATH items, each of which forces a re-pin, see S2)
sources_examined:
  - research/paper2/tnnls/ABLATION-PLAN-2026-10-30.md (all, incl. statistician check SC-1..SC-9 and "Changes applied")
  - analysis/paper2/lrf/ablation.py (all 986 lines), tests/analysis_lrf/test_ablation.py (all)
  - exp_p2/gate/lrf_score.py (all), exp_p2/gate/evidence.py lines 29-41, analysis/paper2/lrf/a6_analysis.py (header, analyse_lg, seed slots)
  - analysis_posthoc/learned_ceiling/{data.py, families.py, lrf.py, run.py lines 1-140}
  - runs/P2-LRF-ABL-FIT/{HASHES.json, R0.json, controls_design.json, variants.json, config.json, timing.json, */spec.json, */hpo.json, */model*.npz, A-SF/candidates.json}, runs/P2-LRF-ABL-FIT.stdout.log
  - runs/P2-LRF-FROZEN-LFIX/{spec.json, hpo.json}
  - metadata only of the fresh runs: runs/P2-LRF-{L1,LG}/{items.jsonl idx/conds keys, arrays_manifest.json keys, predictions.jsonl key names and per-condition counts, a6_analysis.json "n" fields}
coverage: >
  Code paths read in full. Commands run (CPU, CUDA_VISIBLE_DEVICES=""): pytest tests/analysis_lrf (31 passed, 32 s);
  verify_fit(require_git=True) on the committed fit dir; recomputation on the 500 design items of R0 (numpy weights of LRF-H seed 0 against the frozen model), of the KO-ALL design control,
  of the common-random-number draws and seeds of all 10 fitted objects, of A-SF's argmin, of a partial knockout against manual zeroing, and of LRF-H hpo-log parity with the frozen hpo.json.
  NOT done: no fresh-fold array opened (runs/P2-LRF-L1/arrays, runs/P2-LRF-LG/arrays untouched); no `score` or `analyse` run on real data; no refit; no clone-and-rebuild of the environment (that is the release-gate step 5, not a pre-score code audit).
claims:
  - statement: "The 22-variant list, partitions, seed keys and bootstrap slot in ablation.py equal the plan."
    status: supported
    evidence: "ablation.py lines 79-131; variants.json; recomputed seeds [316748921, 1886600088, 4159147987] = ss(4,99,0,0/1/2); cell children (35, 0..7)"
    level: E4
    confidence: 0.95
  - statement: "No fresh-fold item can enter fitting, tuning, standardisation or selection."
    status: supported
    evidence: "fit() reads only src/arrays after a digest check against the frozen spec (038ded07...8e90, recomputed equal); config.json src = runs\\P2-LRF-RESCORE"
    level: E4
    confidence: 0.95
  - statement: "The committed fit reproduces the frozen LRF and every fitted object is internally consistent."
    status: supported
    evidence: "R0.json (cfg equal, inner O1 diff 0.0, torch-vs-numpy max |dw| 5.3e-7); recomputed numpy |w_H - w_frozen| = 0.0 on 2,048,000 weights; hpo log of LRF-H identical to FROZEN-LFIX hpo.json"
    level: E4
    confidence: 0.95
  - statement: "Stage-1 frozen files match HASHES.json now."
    status: supported
    evidence: "verify_fit(require_git=True): OK; 68 listed files, none unlisted, none missing; HASHES.json tracked and clean; ablation.py sha 5b17ccb7fb06... equals the pinned value"
    level: E4
    confidence: 0.98
unknowns:
  - "The score and analyse stages have never run on real arrays; a runtime exception on real data is possible (allowed by SC-5 (i)). Data formats were checked from metadata (manifest keys, predictions keys, cell counts 450 x 4 and 300 x 4) and agree with the code."
  - "Score wall-clock is unmeasured."
next_test: {hypothesis: "none", intervention: "apply the lead's ruling on S1/S2, then score once", primary_metric: "none", falsifier: "none", gpu_hours: 0}
---

# Gate audit: ablation code before fresh-fold scoring

## Verdict

**PASS WITH FIXES.** No defect touches a fitted object, so no refit is needed. One item is required before scoring (S1), and it is procedural (a command-line argument), not a code change. Items S3 to S6 are optional hardening of the score and analyse code. Each of them edits `ablation.py` and therefore changes the code hash that `verify_fit` compares with HASHES.json; see S2 for what the lead must rule before any such edit.

## Criterion table (brief items 1 to 7)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1a | 22 variants, order, 10 + 12 split, 9 fitted, 21 interval rows, K = 336 | met | `ablation.py` 111-125 (module asserts); `variants.json` order equals `A.VARIANTS`; plan section 3 compared name by name |
| 1b | Partitions S (14/5/5/4/4/3) and F (7/3/8/4/13) equal the plan tables, each covers the 35 features once | met | lines 79-108 against plan section 2; `check_partition` runs at import; unit test |
| 1c | Fit seeds: inner folds ss(1,99), configs ss(2,99,0), inner fits ss(3,99,0,ci,ii), final ss(4,99,0,0/1/2) | met | `successive_halving(..., 99, 0)` in `run.py`; `_seed(s)` = ss(4,99,0,s); recomputed 316748921 equals frozen `spec.json` seed; `spec.json` of all 10 objects carry the same three seeds; the 9 drawn configurations in each `hpo.json` equal a fresh `default_rng(ss(2,99,0))` draw of that family (A-LIN: ridge and lr as F1, knots 0 in all 9) |
| 1d | Bootstrap SeedSequence(20261028, spawn_key=(35,)), 8 children in the plan's cell order, one 10,000 x n matrix per cell, fresh generator from the child, same matrix for every row and both contrasts | met | lines 131-165; `CellBoot` is built once per cell in `analyse`; children (35,0..7); level (0.95,) only; `np.quantile` at 0.025/0.975. The plan's option (b) is used (precomputed matrix), not (a) |
| 1e | Variant definitions: A-LIN, A-S-*, A-SF (35 searches, argmin, first-in-order tie), A-MIL (gated attention, v zero-init, softmax, plan search space), A-UNL = 1 - rank_s3, knockouts set standardised features to 0 | met | families 263-359; recomputed A-SF argmin = `rad` = stored choice; a partial knockout (KO-S-nbr) equals manual zeroing to 8e-16; 9 A-MIL draws use the plan's {32,64,128}/{0,0.1,0.3}/log-uniform ranges |
| 2a | Fitting reads design items only | met | `fit()` verifies `arrays_digest` equal to `spec.rescored_arrays_digest` before loading (recomputed equal); refuses an existing out dir; `score()` never fits |
| 2b | Fit stores no accuracy, decision count or margin | met | `grep -c '"acc"'` = 0 in all `hpo.json` and `candidates.json`; `selfcheck.json` holds weights only; `controls_design.json` holds counts of differing decisions only |
| 2c | Unit tests | met | `python -m pytest -q tests/analysis_lrf`: 31 passed. Tests use synthetic arrays only; `test_real_r0_recorded_if_present` reads R0.json |
| 3 | No Study 1 object read | met, with two accepted contacts | grep of `ablation.py`: no `flag`, `gatem`, `deltaL`, `z`/`codes` read; `FieldGuard` allow-list (B, D, s3, tbv, tex, nbr, delta) serves every array access in fit and score and raises `GateFieldRefused` otherwise; a spy test covers the score path. Contacts: (i) `from exp_p2.gate import lrf_score` imports the `config` and `evidence` modules (GATE constants loaded, none used); (ii) `committed_rows` and `read_prediction_controls` json-load files whose rows hold GATE results; only `idx`, `conds` keys, `image_id` (and `idx, condition, y_none, y_lrf`) are retained. Both accepted, cannot be avoided with the plan's design |
| 4a | Decision and non-finite rule by import | met | `decide`, `arm_y`, `NonFinite`, `HashMismatch`, `raw_from_arrays`, `gam_f` imported from `exp_p2.gate.lrf_score`; non-finite raw/Delta stop in `raw_stack`; non-finite or all-zero weights stop in `decide` |
| 4b | Order: hash check, manifest check, load cells, controls.json, only then load variant models and weight; stop on control failure | met | `score()` lines 829-857; `compute_controls` writes `controls.json` then raises `ControlMismatch`; tests: controls exist before `compute_variant_predictions`, a flipped y_lrf or y_none leaves only controls.json and env-lock.txt |
| 4c | 336 intervals, every variant scored and reported, KO-ALL exact-equality control without interval, outputs and run dir | met | `INTERVAL_ROWS` (21) x 8 cells x 2 contrasts; K computed from the output and compared with `K_expected`; KO-ALL rows are scored (24 main + 21 seed-spread = 45 weightings) but absent from `rows`; `ko_all_control` block reports identical yes/no and counts; run dir `runs/P2-LRF-ABL-SCORE`, files as the plan lists plus `score_meta.json` |
| 4d | Analyse: estimand d = mean(y_v - y_r) = (b - c)/n, sign variant minus reference, paired percentile bootstrap, 95% only, unsorted, no flags, SC-1 text verbatim | met | `_contrast`, `analyse`; the SC-1 string in the code is word-for-word the plan's text (placeholders `{K}` and `{0.05 K}` are left unfilled in the JSON); unit test forbids flag/rank/p keys |
| 4e | Cell n equals the n of `a6_analysis.json` (SC-3) | partly | The check exists (`_expected_n`) and returns 450 x 4 and 300 x 4 on the real a6 files, equal to the committed row counts and manifest n, but it runs only if `--a6-l1` and `--a6-lg` are given; both default to None and the plan's section 7 command omits them. See S1 |
| 5 | R0 and design controls reproduce from committed files | met | see claims; R0 cfg and inner O1 identical, weights identical in numpy; KO-ALL design control recomputed: 0 differing decisions of 2000 item-conditions, weight spread 0.0 |
| 6 | Frozen files match HASHES.json now | met | see claims |
| 7 | Anything that lets the lead choose a variant by its fresh result | partly | No code path selects, ranks or re-fits after a score. Residual procedural routes are listed under "Selection risks" |

## Required fix

**S1 (SCORE-PATH, procedural, no code change).** Run the analyse stage as
`python -m analysis.paper2.lrf.ablation analyse --score runs/P2-LRF-ABL-SCORE --a6-l1 runs/P2-LRF-L1/a6_analysis.json --a6-lg runs/P2-LRF-LG/a6_analysis.json`,
not as the plan's section 7 command. Without the two flags the plan's SC-3 requirement ("cell n must equal the n of `a6_analysis.json`") is silently skipped. The check was exercised here on the real a6 files: it yields 450 for the four L1 cells and 300 for the four LG cells. A code alternative (make the paths default and mandatory) is S3 below.

## Optional SCORE-PATH fixes (none touches a fitted object)

**S2 (ruling needed, applies to every code edit below).** `verify_fit` compares `analysis/paper2/lrf/ablation.py` with the SHA recorded in HASHES.json at fit time (5b17ccb7fb06...). Any edit to the file, including the score and analyse functions, makes `score` refuse with HashMismatch. If the lead wants any of S3 to S7, a documented re-pin is required before scoring: keep the `files` section of HASHES.json unchanged, record the fit-time hash as `code_at_fit_time`, record the new hash, show by `git diff 45f4a717 -- analysis/paper2/lrf/ablation.py` that only score/analyse/verify functions changed (no line of the family, fit, export or partition code), and commit before the score stage. Because `verify_fit` itself is in the file, the re-pin edit to the verifier is a self-reference that only the lead's ruling can settle. The cheapest compliant path is to make no code edit and apply S1 on the command line.

- **S3 (SCORE-PATH).** Make the a6 paths default to the two run directories and mandatory in `analyse` (S1 in code).
- **S4 (SCORE-PATH).** `analyse` copies `predictions_sha256` from `score_meta.json` instead of recomputing it from `predictions_ablation.jsonl`; recompute and compare, and record the sha of `ablation.py`. As written an edited predictions file would not be detected.
- **S5 (SCORE-PATH).** `score()` creates the out dir and writes `env-lock.txt` before `verify_fit`. After a hash-mismatch stop (a rerun the plan allows, SC-5 (iii)) the next `score` refuses with "the score stage runs once". Create the dir after verification, or rerun with another `--out`.
- **S6 (SCORE-PATH).** `verify_fit` does not compare `fz["hashes"]["model_sha256"]` with `HASHES["frozen"]["model_sha256"]` (db7fdb4e... is recorded but not checked). The LRF control against `y_lrf` would catch a wrong frozen model, so this is hardening only. The same holds for `exp_p2/gate/evidence.py` and `exp_p2/common.py`, which `arm_y` and `committed_rows` depend on and which are not in the code pin; the NONE control covers evidence.py.
- **S7 (SCORE-PATH, wording of an output).** (a) `mandatory_text_sc1` is stored with `{K}` and `{0.05 K}` unfilled; the plan says "verbatim with K filled in". (b) The SC-4 statistic "items on which the harness LRF refit at seed 0 decides differently from the frozen LRF" will be 0 by construction: the committed LRF-H seed-0 model reproduces the frozen weights exactly in numpy (max |dw| 0.0). S-VII must say so; the informative refit variation is in LRF-H seeds 1 and 2 (mean |dw| 0.043 and 0.043, correlation 0.90 and 0.86 with the frozen weights on 100 design items, maximum single-token difference near 1.0). The analyse stage reports their accuracies (seed spread) but no disagreement count for them; adding one is optional and descriptive.

## FIT-PATH fixes

None. R0, parity of the 9 configuration draws, seeds, columns, A-SF argmin, hashes and the numpy-versus-torch self-checks (at most 6.3e-7) all agree with the plan.

## Selection risks (item 7), none closed by code

1. Deleting `runs/P2-LRF-ABL-SCORE` and rerunning `score`, or running `fit --resume` after removing a variant's spec.json (which also rewrites env-lock.txt, variants.json, timing.json and HASHES.json), are code-possible. The first is blocked only by SC-5; the second is caught by `score` refusing a modified HASHES.json unless that file is recommitted. Procedural control: any rerun must be logged with its SC-5 reason in the decision ledger before it is made.
2. `predictions_ablation.jsonl` is readable after `score`; SC-5 says no output is read before `analyse` completes. No code prevents it. `score` and `analyse` print no accuracy (only counts, K, n), which is correct.
3. V-G cell and row selection after seeing intervals is excluded by the plan (section 3 row order, section 4 cell list); the analysis writes all rows in plan order with no flags.
4. A-SF chose `rad` (a position feature) with inner O1 0.4419 on the design items. The choice is frozen in `A-SF/spec.json` and HASHES.json and the selection used no fresh item.

## Notes for the writing stage (not defects)

- The fit stage's torch-versus-numpy self-check compares 20 design items; the score stage uses numpy only, which the unit tests tie to `lrf_score.weights` to 1e-12.
- Seed-spread refits of the LRF differ visibly from the frozen weights (S7 (b)); V-G rows are single-seed fits, as SC-7 already requires the caption to say.
- The plan lists predictions.jsonl as the only extra file the scorer reads; the code also reads `items.jsonl` (idx, conds, image_id) for committed order and the image-overlap line. Needed for section 0 item 7; record it in S-VII's data list.

## Files

- This report: `C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\frosty-clarke-209639\research\paper2\prereg\GATE-AUDIT-ABLATION-CODE-2026-10-30.md`
- Nothing committed; no progress.md gate ticked (this is a pre-score code audit, not a numbered gate in FRAMEWORK section 7); no ledger row added.
