```yaml
agent: lab-engineer (implementer B)
date: 2026-10-28
brief: Paper 2 GATE. (1) Family B FOIL-COCO hard negatives at n = 300; (2) imagecorruptions exploratory suite (install, 5-image CPU smoke, runner, cell analysis); (3) 179-item variant of the patch/swap chance bar. CPU only; no GPU job started.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (AD.2, AD.3, AD.6, AD.8, AD.9, AB.3, AB.6, AB.7, AB.8, AB.9)
  - research/paper2/related/DATA-CHECK-FOIL-CORRUPTIONS-2026-10-28.md
  - exp_p2/gate/{data,fusion,hardneg,pipeline,runner,config,folds,corruptions,evidence,arms,stats,report,seeds,artifacts,pins,theory,calibrate,dcache,detect}.py, exp_p2/{run_gate_m2,run_gate_m4,run_gate_m5,analyze_gate_m1}.py (read only)
  - runs/P2-GATE-FOLDS/folds.json; runs/P2-PROBE-01/items.jsonl and runs/P2-M0-STAGE2/items.jsonl (timings only); runs/P2-PROBE-01|02/selection.json (image ids only, through data.probe_image_ids)
  - the FOIL test file (all 198,960 records), SHA-256 verified
  - imagecorruptions c959e659c9713837d2acd7ce785a81202d4be799: corruptions.py and __init__.py as installed
coverage: all three pieces built and tested on CPU. NOT covered: any GPU path (encode, real logits, memory, timing of the new runners), the data-steward hand check of L7, the audited epred_fit (does not exist yet), the FOIL file revision (July 2017 vs Oct 2018).
claims:
  - statement: "FOIL pairs have a real pair key: `annotations[].id` is shared by the original and its foil (99,480 ids, each exactly one original and one foil, on one image). The data-steward's 'no pair key' (which looked at foil_id) is superseded."
    status: supported
    evidence: "foil.build_pairs asserts it on the whole file; test_real_file_hash_and_pair_key; runs/P2-GATE-FOIL/pool.json build_stats"
    level: E4
    confidence: 0.95
  - statement: "The leak check L0 to L8 passes on the committed pool; the positive control matched ids in all five groups (cal 240, head 75, test 238, test_ext 159, probe 383) so the check is not vacuous; the checker fails on every injected leak"
    status: supported
    evidence: "runs/P2-GATE-FOIL/leak_check.json; python -m exp_p2.gate.foil selftest; tests/exp_p2/test_gate_foil.py"
    level: E4
    confidence: 0.9
  - statement: "All 300 planned test pairs are on images of folds.json test/test_ext (the P test list), so B and P are dependent in their data (allowed by AD.6, separate families)"
    status: supported
    evidence: "runs/P2-GATE-FOIL/pool.json counts.n_test_in_P_test_fold = 300; 238 + 159 = 397 eligible images are in test/test_ext, more than the 300 needed"
    level: E4
    confidence: 0.95
  - statement: "imagecorruptions at commit c959e659c9 imports and runs on Python 3.12 / Windows with scikit-image 0.26.0; all 8 suite cells run on 512 x 512 uint8 images, are byte-deterministic given the seed, and fog and impulse_noise differ across seeds"
    status: supported
    evidence: "runs/P2-SUITE-SMOKE/smoke.json (40 calls, 5 images x 8 cells; mean 0.026 s per call, max 0.049 s)"
    level: E4
    confidence: 0.9
  - statement: "impulse_noise is NOT reproducible from np.random.seed alone with scikit-image >= 0.19 (fresh default_rng per call); suite.apply_corruption makes it so by passing rng=default_rng(seed) to skimage.util.random_noise for the duration of the call"
    status: supported
    evidence: "tests/exp_p2/test_gate_suite.py::test_impulse_noise_would_not_be_reproducible_without_the_seeding_wrapper and test_same_seed_same_pixels_and_random_types_vary_with_the_seed"
    level: E4
    confidence: 0.9
  - statement: "The patch/swap chance bar now passes only if the lower 95 percent bound exceeds 0.5 on all items and on items with index >= 21"
    status: supported
    evidence: "exp_p2/analyze_gate_m1.py combine_chance_bars; tests/exp_p2/test_gate_m1_chancebar.py (synthetic data only)"
    level: E4 (code)
    confidence: 0.9
  - statement: "Whole-suite CPU test run is green: tests/exp_p2 gives 341 passed, 4 skipped (99 s) with the project .venv and the pytest shim, after my last commit. An earlier run (329 passed, 114 s) had to ignore tests/exp_p2/test_omni_scorer.py, another implementer's then in-progress file with a SyntaxError at line 17"
    status: supported
    evidence: "command in section 3; output of this session (not stored in runs/)"
    level: E4 (code), not a research result
    confidence: 0.85
competing_explanations: []
unknowns:
  - "whether the FOIL file is the Oct 2018 revision (info block says July 2017)"
  - "GPU timing, memory and the fake-network-untested paths listed in section 6"
  - "data-steward sign-off of the L7 hand-check sample (AB.6 requires it; this report cannot give it)"
next_test: {hypothesis: "B1: fusing the two directions (Fisher LDA) beats the better single direction on FOIL-COCO pairs, clean images, UniDisc", intervention: "run the fit stage, freeze, run the test stage", primary_metric: "exact two-sided McNemar of Y_fus against Y_best, alpha 0.05, m = 1, b > c_cnt, completed n >= 120", falsifier: "no rejection with b > c_cnt (this is not a 'negative' at these n)", gpu_hours: 0.12-0.13 busy (about 15-20 minutes wall at duty 0.5), derived in section 4}
```

# Implementer B: FOIL-COCO family B, the imagecorruptions suite, the 179-item chance bar

Commits (all mine, explicit `git add` of my own paths): `b8605b8b` (chance bar), `c9d7fec4` (family B), `4e4d637e` (suite), `c538676a` (freeze/analyze refuse an empty run). The report commit follows.

## 1. What was built

| Piece | Files (all new unless marked) |
|---|---|
| Family B | `exp_p2/gate/foil.py` (data access, `build_pairs`, `foil_pool`, `foil_leak_check`, `selftest`, `fit_b1`, `fusion_b1`, `require_committed`), `exp_p2/run_gate_foil.py` (GPU runner, never executed), `exp_p2/gate/analysis_foil.py` (CPU freeze and analysis), `tests/exp_p2/test_gate_foil.py` (40 tests), `runs/P2-GATE-FOIL/{manifest,pool,leak_check}.json` |
| Suite | `exp_p2/gate/suite.py` (cells, seeded application, smoke, `suite_cells`, E-dec, E-pred agreement), `exp_p2/run_gate_suite.py` (GPU runner, never executed), `tests/exp_p2/test_gate_suite.py` (31 tests), `runs/P2-SUITE-SMOKE/{smoke.json,pip-freeze-before.txt,pip-freeze-after.txt}` |
| Chance bar | `exp_p2/analyze_gate_m1.py` (edited: `combine_chance_bars`, keys `chance_bar_after_dry_run`, `chance_bar_both`; `chance_bar` keeps its old meaning), `tests/exp_p2/test_gate_m1_chancebar.py` (9 tests, synthetic data only) |

No other existing file was edited. `exp_p2/gate/data.py` needed no change (the FOIL path lives in `foil.py`).

## 2. SAP clause mapping

### AD.6 / AB.6 (family B)
- **Data and manifest.** The test JSON was verified (SHA-256 `7b37ab2a...4642`, 45,080,997 B) and copied to `C:\Users\Shlok\.cache\dlm_dl\coco\foil\foilv1.0_test_2017.json`. That directory is the COCO cache, outside the repository, so it cannot be committed and needs no ignore rule. `runs/P2-GATE-FOIL/manifest.json` records the SHA-256, source URL, licence (CC BY 4.0, steward E1) and that the file is not in git. `foil.load_foil` re-verifies the hash on every load.
- **Pairs.** One per image, the first record in file order (`build_pairs`). The partner is the record with the same `id` (see ambiguity A1). Captions are lower-cased with white space collapsed on both sides (case leak). Whole-file facts asserted: 198,960 records, 99,480 ids, 32,150 images, first record is an original for all 32,150 images, 32,076 pairs differ in exactly one word, 0 pairs identical after normalisation.
- **Pool (`foil_pool`).** Test: eligible = image in COCO val2017 and not in folds `cal`, `head`, nor the probe-1/probe-2 id lists; order = folds `test` then `test_ext` in stored order, then the rest by `default_rng(20261031).permutation` of the sorted ids; first **300** (Shlok's n). Fit: FOIL pairs on folds `cal` images, cal order, at most 300 (240 exist). Counts (L5): 32,150 candidate images; excluded 28,187 not in val2017, 240 in cal, 75 in head, 383 in probe lists; 3,265 eligible (238 in `test`, 159 in `test_ext`, 2,868 from the permutation). Pool SHA-256 (ids, captions, idx, gid, exclusion marks) `edc3b227baf940eb9b665369097866a28bbd628ad7ac893ad0813dd9b74a3616`; committed before any GPU use.
- **Caption rule.** `apply_token_rule` marks (does not drop, does not replace) pairs with c+ or c- outside 5 to 32 tokens; at pool time with the Llama-2 tokenizer (1 fit and 2 test pairs, all "both out of range"), again at run time with `sc.caption_ids` (the runner writes `token_exclusions.json`, and records any pool/runtime disagreement). idx and gid are positions in the planned list, so an exclusion shifts nothing.
- **Leak check.** `foil_leak_check` runs L1 to L5 and the positive control: L0 (all ids through `normalise_image_id`; whole-file id/file-name agreement: 32,150 of 32,150; pool ids in val2017), L6 (matched counts cal 240, head 75, test 238, test_ext 159, probe 383, each must be > 0, else "leak check vacuous"), L7 (first matched id of each of the five groups with raw FOIL name and COCO member name, member existence checked in `val2017.zip`), L8 (`selftest()`: a synthetic pool sharing one id with cal must fail; also head, probe, repeated, fit-outside-cal, fit/test overlap, and an id-format mismatch that must stop as vacuous). Any failure raises `LeakCheckFailed` and the runner exits 2 before the model is touched. `selftest()` is run inside `check_pool` every time.
- **Rules before any B-test item.** (i) fit pairs >= 100 else `not_estimable` (p = 1); (ii) best single direction accuracy >= 0.95 on the fit pairs else `untestable_at_ceiling` (p = 1, test pairs not run: the runner refuses the test stage); (iii) `fusion_frozen.json` must be tracked and unmodified in git (`require_committed`) before the test stage starts.
- **Fusion (`fit_b1`, `fusion_b1`).** Margins per pair: T = pmi(c+) - pmi(c-) (text direction, 2 passes), I = mean over the 1,024 tokens of Delta_j (image direction, 2 passes), both on the clean image, nothing gated. LDA weights `fusion.lda_weights` on the fit pairs, unfitted Stouffer weights (descriptive, reported first), best single direction by fit accuracy (tie to text). Y_fus = 1[w.(T,I) > 0], Y_best the sign of the best direction's margin, ties count wrong. Test: `report.report_test` (exact two-sided McNemar, effect size, paired percentile bootstrap, theta); `supports_fusion_helps` only with p < 0.05, b > c_cnt and completed n >= 120; below 120 the status is `descriptive_n_below_120`. `analysis_foil analyze` uses the committed weights, not a refit (it records whether a refit agrees), and refuses a partial test run unless `--allow-partial` (SAP 8.2).
- **What is not claimed.** The output carries the limits: not a corruption test; P and B dependent in data; c+ likely in UniDisc's training data (U8); label "negative" not available; case leak and unverified file revision.

### AD.9 / AB.8 (suite, exploratory)
- Types and severities exactly as fixed: pixelate, defocus_blur, fog, impulse_noise at severities 2 and 4 (8 cells, order fixed in `suite.CELLS`); a type absent under its name is dropped, not replaced (`available_types`, recorded in `suite_types.json`). Items: head[:100] then test[:100] (positions 0 to 199; token exclusion without replacement). Corruption seed from the item id: `SeedSequence([20261029, gid, cell index, 8001])`.
- Arms none, GATE-M (alpha 0.05, frozen M2 threshold, one jitter draw) and chg. `suite_cells(df, fold="test")` gives per cell b, c_cnt, n_d, net difference with a 95 percent paired-bootstrap CI, accuracies, flag precision/recall, the E-dec split (identity T = U + R + V asserted per item and in every resample; shares only if the lower 95 percent bound of tau_T exceeds 0; AB.2 names), and, if plug-in signs are supplied, the E-pred sign agreement over the evaluable cells with a Clopper-Pearson interval. **No p-value is printed or stored** (the exact-McNemar p, mid-p, 98.33 and 90 percent intervals are stripped), and the output is labelled Tier 3 / researcher choice (AB.8). Suite agreement is a separate block (`epred_suite`) and is never pooled with AD.3.
- The runner requires `runs/P2-GATE-M2/threshold.json` and a committed `runs/P2-GATE-M3/family.json` (operating points fixed before any gate flag exists on a headroom item); it does not read `family.json`'s contents and does not depend on M4.

### AB.7 item 3 (chance bar)
`analyze_gate_m1.run_analysis` computes `detect.chance_bar` on all items (key `chance_bar`, unchanged) and on the items with probe-2 index >= 21 (`chance_bar_after_dry_run`), and `combine_chance_bars` gives `chance_bar_both`: failed if either pool failed, passed only if both passed, otherwise undecided (None). `main` prints the combined verdict with both lower bounds. Tests cover pass, fail in the late pool only, fail in the full pool only, missing q, no late pool, and that the late pool is defined by item index, not position. Seeded bootstraps use the existing `seeds.seed_for("auroc")` default. **Not run on real data.**

## 3. Commands

GPU (none run by me). All through the pinned `tools/gpu_guard.py` and the runner guards (hold file, AC, memory/rise/slow-item rules, 1 s watchdog, cap 0.75; `peak_gb` = `torch.cuda.max_memory_allocated`, reset per item, and `seconds` are logged in every row by `runner._loop`). Each is a chunk, resumable; relaunch on exit code 75.

```
PY = C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe
:: family B, stage 1 (fit pairs, 239 expected)
PY tools\gpu_guard.py --log runs\P2-GATE-FOIL-FIT\telemetry-chunk00.csv --max-temp 80 --max-minutes 15 --every 1 -- PY -m exp_p2.run_gate_foil --stage fit --resume --duty 0.5 --soft-minutes 12.5
:: CPU: freeze, then COMMIT runs\P2-GATE-FOIL\fusion_frozen.json
PY -m exp_p2.gate.analysis_foil freeze
:: family B, stage 2 (test pairs, 298 expected); refuses unless fusion_frozen.json is committed with status ok
PY tools\gpu_guard.py --log runs\P2-GATE-FOIL-TEST\telemetry-chunk00.csv --max-temp 80 --max-minutes 15 --every 1 -- PY -m exp_p2.run_gate_foil --stage test --resume --duty 0.5 --soft-minutes 12.5
PY -m exp_p2.gate.analysis_foil analyze
:: suite (200 items; needs M2 threshold.json and committed M3 family.json)
PY tools\gpu_guard.py --log runs\P2-GATE-SUITE\telemetry-chunk00.csv --max-temp 80 --max-minutes 15 --every 1 -- PY -m exp_p2.run_gate_suite --resume --duty 0.5 --soft-minutes 12.5
PY -m exp_p2.gate.suite analyze
```
The telemetry directory must exist or the guard must create it (as `gate_driver.build_cmd` relies on); `gate_driver.STAGES` has no entry for these three (I did not edit it; see concern 3).

CPU (run by me):
```
set CUDA_VISIBLE_DEVICES=
PY -m exp_p2.gate.foil build-pool          # wrote the manifest, pool.json, leak_check.json (39 s)
PY -m exp_p2.gate.foil selftest            # L8 and the other known-bad cases: ok
PY -m exp_p2.gate.suite smoke --n 5        # 40 calls, all checks true
set PYTHONPATH=<scratchpad>\pytest_shim
PY -m pytest tests/exp_p2 -q                -> 341 passed, 4 skipped in 99 s (earlier run: 329 passed with test_omni_scorer.py ignored, it did not parse at that moment)
```

## 4. Time estimates (labelled; arithmetic shown)

Measured inputs: `runs/P2-PROBE-01/items.jsonl` (300 items; `seconds` is busy time, the driver sleeps an equal time at duty 0.5): median 7.022 s per item, 90th percentile 8.618 s; one stalled item took 635 s (stall, not typical); `runs/P2-M0-STAGE2` (10 items): median 6.862 s. Every probe-1 item logs `n_passes` = 29 + 29 = **58** (all 300 rows). So **0.121 s per pass (7.022 / 58)**, which already includes the per-item encode and decode, so it is an upper bound on the pure forward time. Model load per chunk: 19 to 137 s in probe-1 chunks (`load_s`), 36 s in M0 stage 2. The SAP's assumed 0.15 s per pass is used as the second figure. Peak memory in the measured runs: 4.04 to 4.05 GB median, 8.20 GB once (probe-1).

**FOIL, n = 300 test.** Pairs: 239 fit + 298 test = 537 (after the pool-time token rule). Passes per pair: 4 (image direction 2, text direction 2; nothing gated) plus up to 28 one-off text-null passes if the D^T cache lacks a length. Per-pair encode and image decode: **ASSUMED** 0.3 s (not measured separately).
- Passes: 537 x 4 = 2,148; at 0.121 s = 260 s; at 0.15 s = 322 s.
- Encode and decode: 537 x 0.3 = 161 s (ASSUMED).
- Busy: 421 to 483 s = **7.0 to 8.1 min = 0.12 to 0.13 GPU-h**.
- Wall at duty 0.5: 2 x busy = 14 to 16 min, plus two model loads (about 1 min each): **about 15 to 20 minutes**; each stage fits in one 12.5-minute chunk (fit 239 pairs: about 3 min busy, 6 min wall; test 298: about 4 min busy, 8 min wall).

**Suite.** Items 200 (fewer only by token exclusions). Passes per item: 2 caption passes shared by all cells (they do not depend on the codes, as in M4) + 8 cells x 8 B-passes = **66** (the SAP's 8 B + 2 caption per cell would be 80; sharing saves 14). Total 200 x 66 = 13,200 passes (the SAP's 16,000).
- At 0.121 s: 1,597 s = 26.6 min; at 0.15 s: 1,980 s = 33.0 min.
- Encodes: 200 x 9 = 1,800 at an ASSUMED 0.1 to 0.3 s = 3.0 to 9.0 min. CPU corruptions: 200 x 8 x 0.026 s (measured, smoke) = 42 s.
- Busy: 30 to 43 min = **0.5 to 0.7 GPU-h** (SAP: 0.67). Wall at duty 0.5: **1.0 to 1.4 h**, plus about 1 minute load per chunk (about 5 to 7 chunks).

Neither number includes interruptions or a crash; the memory behaviour of the new runners is unmeasured (section 6).

## 5. Install record (imagecorruptions)

Shlok approved the install from the GitHub commit. Resolved full SHA of `c959e659c9`: **c959e659c9713837d2acd7ce785a81202d4be799** (GitHub API, commit of 2025-05-06). Deviations from the brief, with reasons:
1. The project `.venv` has no `pip` (it is a `uv` venv; `python -m pip` fails with "No module named pip"). I used `uv pip install --python <venv python> ...`, the equivalent.
2. A dry run of the full install showed it would add `opencv-python` 5.0.0.93 next to the already installed `opencv-python-headless` 5.0.0.93 (both provide `cv2`; overwriting one by the other is a corrupted install). So: `uv pip install --no-deps "git+https://github.com/bethgelab/imagecorruptions@c959e659c9713837d2acd7ce785a81202d4be799"` and then `uv pip install numba==0.68.1 scikit-image==0.26.0`. Nothing already installed changed (diff of `uv pip freeze` before and after in `runs/P2-SUITE-SMOKE/pip-freeze-*.txt`: 7 packages added, none changed).
Added: imagecorruptions 1.1.2 (from the commit), numba 0.68.1, llvmlite 0.50.0, scikit-image 0.26.0, imageio 2.38.1, lazy-loader 0.6, tifffile 2026.10.15. Present and used: numpy 2.5.2, scipy 1.18.1, opencv-python-headless 5.0.0.93, pillow 12.3.0, setuptools 78.1.0 (provides `pkg_resources`). `scipy.ndimage.interpolation` imports without error on scipy 1.18.1 (the steward's open question); the import takes 1.2 s.

## 6. Untested paths, ambiguities and how they were resolved

**Untested (no GPU, fake network only):**
- The real `UniScorer` paths of both runners: `encode` on corrupted images, real logits, the layout self-check, `peak_gb`, the 12 GB behaviour, `checks.l10_once`, and the real `dcache` text-null fill. The runner item functions are tested on the fake network for pass counts (FOIL 4; suite 66), outputs, determinism and resume.
- `python -m exp_p2.run_gate_foil` and `run_gate_suite` end to end past the prerequisite checks. I ran only the CPU prerequisite paths: `--stage test` stops with "fusion_frozen.json missing", the suite stops with "threshold.json missing", `analysis_foil freeze` stops with "no fit rows".
- `foil.require_committed` against the real repository (tested on a temporary git repository).
- A real E-pred: see A5.

**Ambiguities and resolutions:**
- **A1 pair key.** The steward wrote that the file has no pair key (`foil_id` is unique). `annotations[].id` is shared by the original and its foil; I verified it on the whole file and use it, with the one-word replacement relation as a diagnostic only. Without it the pairing would have rested on text.
- **A2 exclusion versus "the first n".** AD.6 says the pool is the first n eligible pairs and that out-of-range captions are excluded, not replaced. I take the first 300 by the id rule, then mark exclusions (completed n = 298 test, 239 fit at pool time), never refilling. Completed n >= 120 keeps the test confirmatory.
- **A3 n = 300 and dependence.** AD.6 planned 150; Shlok approved 300. All 300 are P test-fold images (397 are eligible there), so B and P share images. AD.6 allows this; the limits string says so. The power figures in AD.6 are for n = 150 and were not recomputed.
- **A4 two stages.** AD.6 fits on cal pairs and tests on another set, freezing weights before any test pair. I implemented them as two runs (`P2-GATE-FOIL-FIT`, `P2-GATE-FOIL-TEST`) with the freeze in between, and the runner enforces rules (i) to (iii).
- **A5 E-pred for the suite.** `epred_fit` (AB.3: audited, frozen, blob hash in `epred_frozen.json`) is not in the tree. For the suite block I used `theory.plug_in_from_deltas` (existing, read-only) pooled over the headroom items, labelled suite-local. A claim-bearing E-pred must use the audited function, and the suite's s_c must not be read before it exists.
- **A6 suite pass count.** The SAP counts 8 B + 2 caption passes per cell; the caption passes do not depend on the codes, so they are done once per item (66, not 80). This is a saving, not a protocol change (same quantities as M4's Lambda gather).
- **A7 seeding.** `np.random.seed` alone does not make impulse_noise reproducible; the wrapper described under claims does. The caller's global RNG state and `skimage.util.random_noise` are restored after every call (tested).
- **A8 seed names.** `seeds.ANALYSES` has no entries for B1 and the suite; B1 uses `seeds.seed_for("fusion")` (exists, fits), the suite uses `SeedSequence([20261028, 9101 or 9102])`. I did not edit `seeds.py`.
- **A9 L6 strictness.** AB.6 says the count must be > 0. I require > 0 in each of the five groups (cal, head, test, test_ext, probe), since L7 needs one matched id from each. With 79 percent overlap this costs nothing; a zero in a group stops B.
- **A10 L7 sign-off.** The script prints the five matched ids and verifies that the COCO member exists in the zip; the data-steward's hand check is recorded as NOT done (`L7_status`). AB.6 and AB.8 require it before B runs; the code cannot enforce it.
- **A11 headroom flags.** The suite computes gate flags on headroom items (E-pred fit fold). It requires a committed `family.json` first, writes to its own run directory, and no headroom code reads it. AB.3 item 6 (no decision depends on those flags) applies and is the lead's to respect.

## 7. Blinding and scope statement (M1 firewall)

Nothing under `runs/P2-PROBE-02/` was opened except `selection.json` through `data.probe_image_ids` (image ids, as `folds.py` itself does); I did not open `items.jsonl`, any `arrays/` file, or any M1 output, and `analyze_gate_m1` was exercised only on synthetic directories in a temporary path. Timings come from `runs/P2-PROBE-01/items.jsonl` and `runs/P2-M0-STAGE2/items.jsonl` (probe 1 and M0 stage 2, not M1). The suite smoke test used five head-fold images (pixels only, no model scores). No GPU job was started, `tools/gpu_guard.py` and the hold file were not touched, and `CUDA_VISIBLE_DEVICES` was empty for everything I ran.
