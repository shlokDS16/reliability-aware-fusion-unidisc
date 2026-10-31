# Code audit: severity sweep (lrf-sev), 2026-10-31

Auditor: gate-auditor (read-only; no GPU, no driver launch, no code edited). Code under audit: commit 6bb9bb2c. Plan: `research/paper2/tnnls/EXPLORATORY-PLAN-SEVERITY-2026-10-31.md` (commit 3bd115b1).
Reference pattern: `exp_p2/run_gate_lrf_dn.py`, `analysis/paper2/lrf/e1_denoise.py`, `tests/exp_p2/test_lrf_dn.py`.

## Verdict: PASS WITH FIXES

No finding changes what the run computes or what the pinned scorer will read. Two cheap fixes (F1, F2) should be made before the GPU launch because the plan makes promises the code does not keep. The rest are optional.

## Evidence run
- `pytest -q tests/exp_p2/test_lrf_sev.py tests/exp_p2/test_lrf_dn.py`: 25 passed.
- `pytest -q tests/exp_p2 -k "driver or default_n or max_chunks"`: 22 passed.
- Pinned entry points, LF-normalised SHA-256 recomputed by me, compared with `runs/P2-LRF-PINS/pins.json`: `exp_p2/run_gate_m4.py` e2d9a5ee..., `exp_p2/gate/lrf_score.py` 63f70961..., `exp_p2/run_gate_lrf_rescore.py` ff34c2b6...: all three equal the pins. (The sev test `test_unchanged_pinned_runner` checks only run_gate_m4; I checked the other two by hand.) `git diff 6bb9bb2c --stat` for exp_p2, analysis, tests: empty, so the audited tree is the working tree.
- The pinned scorer was run on L1 with a scratchpad `--out` (`--run-id P2-LRF-L1 --conds clean,noise0.1 --n 3`): pins verified, 6 lines, positive control ok. Nothing was written under `runs/`.

## Check 1: code vs plan (met)
- Levels `SIGMAS = (0.05, 0.2, 0.3)`: `exp_p2/run_gate_lrf_sev.py:35`. Condition names `noise0.05/noise0.2/noise0.3` come from `corruption_key` (`:42-43`, `corruptions.py:89-93`, `:g` formatting).
- Stream: `noisy()` `:53-55` calls `corruptions.apply_pixel("noise", sigma, pil, m4.rung_rng(gid, "noise", ref_rung()), None)`. `ref_rung()` `:46-50` asserts that 0.1 is ladder rung 0 (`config.LADDERS["noise"] = (0.10, 0.20)`), so the stream is `default_rng([SEED_GATE, gid, 100+10*idx("noise")+0])`, identical to the call in `run_gate_m4.build_conditions` (m4:183). `gaussian_noise` draws `rng.normal(0, sigma)`; common-random-number scaling is tested (`test_common_random_numbers_scale_one_standard_normal`, `test_levels_use_the_l1_noise_stream`).
- Positive control: `:64` encodes the sigma 0.1 image (encode only, no pass), `:75` stores `noise0.1_codes_crn` int16; test compares it with L1's `noise0.1_codes` array path.
- L1 flags: `check_flags` `:112-120` reuses `dn.check_flags` (tbv on, sanity "", denoise-for "", layout-fix 13, family-run P2-LRF-PLAN, neg-len, folds-path present, no extra-cells/gate-true-layout) and `build_conditions_sev` `:59-60` raises unless tbv, slot 13 and neg_len are on in ctx. `m4.check_n_against_rule` still enforces n.
- Protected ids: `:38` = dn list + `P2-LRF-DN`; but see F3.
- Text-direction passes: `extra=True` (`:68`) makes `process` skip them (m4:270); `cr["txt"]` is `{}` (tested). Network rows per item: 3 x (8 B + 1 TbV) + 2 caption + 1 length-matched negative = 30, as the plan says.
- Hook install and restore is the DN pattern; restore on error tested; `--sweep none` calls `m4.main` untouched (tested). Run config records sweep, sigmas, stream (`:80-83`, tested).

## Check 2: will the pinned scorer run without error (met)
`lrf_score` needs per condition `B, D, s3, tbv, tex, nbr, delta, flag0.05` (lrf_score:47) plus `deltaL` when present; `process` writes all of them for any non-denoise condition with `--tbv on` (m4:231-259), and `deltaL` with `--neg-len` (m4:233). The positive control reads `r["conds"][c]["img"]["none"]["y"]` and `["gate0.05"]["y"]`, which `process` stores for every pixel condition (m4:263). Row conds are keyed by the same strings as `--conds noise0.05,noise0.2,noise0.3`. Note that `score_run` silently skips a condition absent from a row (`absent` set, lrf_score:281), so a misnamed condition would give zero lines rather than an error. I found no misnaming; the name test in `test_flag_on_item_has_the_three_levels_and_the_positive_control` covers it. `verify_run_inputs` needs `codebook_sha256` and `dcache_di_sha256` in the run's `config.json`; `m4.main` records them whenever `--layout-fix` is given (m4:320-321), and the sev `run_items` wrapper only adds keys. Features use only arrays (no flags), so the changed condition index (F4) does not enter LRF.

## Check 3: analysis vs plan reporting (met, with F5, F6)
`analysis/paper2/lrf/e1_severity.py`: levels 0/0.05/0.1/0.2/0.3 (`:30`, 0 and 0.1 from L1); NONE = `y_none`, LRF = `y_lrf`; sign LRF minus NONE, (b - c)/n with b, c (`:58-61`); 95 percent percentile bootstrap, 10,000 resamples, `SeedSequence(0)` via `T3.index_matrix` (`:51`), `numpy.quantile` 0.025/0.975 (`:37`); gain minus clean gain = mean of (d - g0) with a paired interval on the same index matrix (`:62-63`), which also gives the F7 difference-in-differences at 0.1; length-matched `_L` block when every row has it (`:94-95`); items matched by idx with gid and image_id checks and identical item sets across levels (`:42-48`), so a partial sweep run raises against L1's 450. Known-number and mismatch tests pass.

## Check 4: existing stages and runs (met)
`git diff 3bd115b1 HEAD` touches exactly: new `run_gate_lrf_sev.py`, new analysis and test files, and 7 lines of `gate_driver.py` (new `STAGES["lrf-sev"]`, `STAGE_ARGS["lrf-sev"]`, `"lrf-sev": 20` added to `STAGE_MAX_CHUNKS` with the other values unchanged, `"lrf-sev"` added to the `default_n` tuple). `test_driver_stage_lrf_sev_reuses_the_l1_flags_and_leaves_other_stages_alone` confirms. `runs/P2-LRF-SEV` does not exist yet. The uncommitted `runs/P2-PROBE-02` modifications in git status are not from this change.

## Check 5: pinned hashes (met)
See Evidence run. All three pinned entry points hash to the pins; scoring-code hash equals `scoring_code_sha256`.

## Findings and fixes

F1 (medium, fix before launch): the plan's stop rule "a positive-control agreement below 0.99 of tokens stops the run" is not implemented anywhere. `process_sev` only stores `noise0.1_codes_crn` (`run_gate_lrf_sev.py:75`) and `corruption_check` (`e1_severity.py:68-81`) returns a fraction but no verdict, and nothing reads it before the numbers go to a table. Fix: in `corruption_check` add `passes=token_equal_fraction >= 0.99` and make `main` print a STOP line and exit 2 (still writing the JSON) when it is False or `checked` is False; and amend the plan's stop-rule sentence to say the check is run after the chunks, not during them (or add an in-run check in `process_sev` that loads `runs/P2-LRF-L1/arrays/item{idx:04d}.npz` and raises below 0.99; that needs no edit to the pinned runner).

F2 (low-medium, fix before launch): `analyse` does not assert the item count. Fix: require `n == 450` (the n_L of `runs/P2-LRF-PLAN/family.json`) or record `n` against the family record, and require that `runs/P2-LRF-SEV/lrf_score_meta.json` lists `pins_verified` with model, scoring code and entry points before reading predictions.

F3 (low): `check_flags` is a blacklist (`run_gate_lrf_sev.py:38, 118`). Any other existing run id (for example `P2-LRF-PLAN`, `P2-LRF-FOLD`, `P2-LRF-FROZEN-LFIX`, `P2-GATE-M5`, `P2-GATE-S2`) is accepted, and the stage module would write into it. The driver fixes the id, but `--run-id` can be overridden. Fix: replace by a whitelist, `a.run_id != RUN_ID` -> error; same for `--folds-path` (must equal `runs/P2-LRF-FOLD/folds_lrf.json`, now only required to be present, inherited from `run_gate_lrf_dn.py:135`).

F4 (informational): the sweep conditions have condition indices 0, 1, 2 (L1's noise0.1 has index 2), so the gate-flag jitter stream (`arms.arm_rng(SEED_GATE, gid, ci, ...)`, m4:243) and the geo/scattered arms differ from L1's at the same sigma. This does not affect `y_none` or `y_lrf` (features B, D, s3, tbv, tex, nbr, delta do not use flags). It does mean `y_gatem` of a sweep level is not comparable with L1's. Fix: one sentence in the plan or deviations item 9 that GATE-M is not reported for the sweep.

F5 (wording, low): the plan says "one index matrix per level from SeedSequence(0)"; the code uses one matrix shared by all levels (`e1_severity.py:50-52`). With equal n the two are numerically identical (same seed, same shape). Fix: change the plan sentence to "one index matrix (SeedSequence(0)) shared by all levels and contrasts", as the script header already says.

F6 (cosmetic): `gate_driver.py:7` stage list does not name `lrf-dn` or `lrf-sev`. Fix: add them. The `test_unchanged_pinned_runner` test checks only `run_gate_m4.py`; extend it to the other two entry points and `scoring_code_sha256`.

No finding is a `missing` criterion. Gate effect: none (this is a code audit before an exploratory run, not a gate in FRAMEWORK section 7); `progress.md` not edited.
