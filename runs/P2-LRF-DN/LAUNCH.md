# P2-LRF-DN launch note (E1, exploratory; plan: research/paper2/tnnls/EXPLORATORY-PLAN-BASELINES-2026-10-30.md)

Written 2026-10-30 by lab-engineer. Nothing in this directory has been run on a GPU. Not committed; the lead commits, then launches with Shlok present.

## What was built (all new or additive; no pinned file touched)
- `exp_p2/run_gate_lrf_dn.py`: thin entry point around the pinned L1 runner `exp_p2/run_gate_m4.py` (its hash is re-checked by a test against `runs/P2-LRF-PINS/pins.json`; unchanged).
  `--denoise none` (default) calls `run_gate_m4.main` and patches nothing. `--denoise nlm-sdn` builds the conditions `jpeg10_nlm` and `noise0.1_nlm` only: the same corruption call and seed as L1
  (`rung_rng(gid, corr, rung)`), then `corruptions.denoise` (OpenCV fastNlMeansDenoisingColored, `config.DENOISE_PARAMS`: h = hColor = 25.5, windows 7 and 21, unchanged; this is Study 1's S-DN arm), then encode.
  Each is scored as a full pixel condition (B, D, s3, tbv, tex, nbr, flags, delta, deltaL at the fixed slot 13), so the pinned `lrf_score` scores it exactly as it scored L1. It also stores
  `<cond>_nlm_codes_corr` (codes of the corrupted, not denoised image) to compare with L1's `<cond>_codes`.
  It refuses (exit 2, before the model is touched) unless the L1 flags are given and the run id is not an existing run.
- `exp_p2/gate/gate_driver.py`: new stage `lrf-dn` (run id `P2-LRF-DN`, n 450 from the n-rule, L1 flags plus `--denoise nlm-sdn`, default max chunks 24). Other stages unchanged (tests).
- `analysis/paper2/lrf/e1_denoise.py` writes `runs/P2-LRF-DN/dn_analysis.json`. Schema as `runs/P2-LRF-E2/combiners.json`: `cells.<cond>.n`, `cells.<cond>.arms."DN+NONE"` and `"DN+LRF"` with `acc`, `vs_NONE`, `vs_LRF`
  (each `{diff, ci95, b, c}`); also reference arms NONE and LRF, `vs_DN_NONE`, `length_matched`, `corruption_reproduction`.
- `exp_p2/gate/lrf_dn_cpu_dryrun.py` (CPU stub dry run) and `tests/exp_p2/test_lrf_dn.py` (14 tests).

## Pre-launch
The driver refuses a dirty tree under exp_p2/ or tools/ (exit 11), so: (1) commit the files above; (2) hold files absent, AC power, GPU idle (the driver checks), Shlok present, other paper sessions told.

## GPU command (PowerShell, from the repository root; same guard flags as the L1 run)
```
& "C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe" -m exp_p2.gate.gate_driver --stage lrf-dn --run-id P2-LRF-DN --n 450 --max-chunks 24 --extra "--slow-factor 3 --slow-min-s 2 --max-used-first-mib 11000 --max-used-mib 11000 --max-rise-mib 4500 --mem-frac 0.75"
```
Chunks: the first 5 minutes, later ones 15 minutes, duty 0.5, `gpu_guard` telemetry every second to `runs/P2-LRF-DN/telemetry-chunkNN.csv`, resumable, stdout in `stdout-chunkNN.log`, progress in `driver.log`.
Tail the logs, do not paste them. The runner refuses any `--n` other than the n-rule's 450, so the smoke run is the first chunk itself (5 minutes): watch it, and stop the driver there if anything looks wrong.

## Expected on completion
- `items.jsonl`: 450 rows, conditions `jpeg10_nlm` and `noise0.1_nlm`, about 21 network rows per item (L1 had 67); `selfcheck.json` passes.
- `arrays/item0000..`: 450 files. `config.json` records `denoise: nlm-sdn`, the denoiser parameters, OpenCV version, and the codebook and D-cache hashes.

## After the run (CPU)
```
.venv\Scripts\python.exe -m exp_p2.gate.lrf_score --run-id P2-LRF-DN --pins runs\P2-LRF-PINS\pins.json --conds noise0.1_nlm,jpeg10_nlm    (900 prediction lines, lrf_score_meta.json)
.venv\Scripts\python.exe -m analysis.paper2.lrf.e1_denoise                                                                              (runs\P2-LRF-DN\dn_analysis.json)
```
`corruption_reproduction.token_equal_fraction` in the analysis should be about 1.0 (same seed gives the same corrupted image as L1); report it either way.

## Timings
- Measured on this CPU (`runs/P2-LRF-DN-CPUDRY/dryrun_report.json`): OpenCV NLM 0.24 s per 512 x 512 image (4 calls, 0.21 to 0.27 s); a stub-network item (2 conditions, 21 network rows) 1.0 to 2.5 s. The stub says nothing about GPU speed.
- From L1 (`runs/P2-LRF-L1/items.jsonl`): 450 items, mean 8.26 s busy per item (median 7.98, 95th percentile 9.55, max 16.1; 67 network rows each), 1.03 h busy, 2.4 h wall (duty 0.5, 12 chunks, model load 23 to 100 s per chunk). Peak allocated 8.2 GB, telemetry maximum 6.5 GiB.
- Estimate for this run (not measured on the GPU): 21 rows instead of 67 gives 8.26 x 21 / 67 = 2.6 s, plus 2 x 0.24 s NLM, about 3.1 s busy per item if cost scales with network rows. L1's per-item time is very flat (7.7 to 9.5 s), so part
  of it may be fixed overhead; the pessimistic bound is no saving at all, 8.3 s.
  Wall = 450 x 2 x busy plus about 1.7 min per chunk (L1: 2.4 h wall against 2.06 h from the duty cycle alone, over 12 chunks). Expected about 1.0 h (3.1 s per item), pessimistic 2.4 h (8.3 s per item); under 2 h if busy is below 6.6 s per item.
  GPU memory should stay below L1's (2 conditions instead of 4, no text-direction passes); the guards are the same.
