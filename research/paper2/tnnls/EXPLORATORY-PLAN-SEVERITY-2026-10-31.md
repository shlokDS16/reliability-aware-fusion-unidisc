# Exploratory plan: Gaussian-noise severity sweep of the frozen LRF (2026-10-31)

Written by the Paper 2 lead before any computation; committed before the code audit and before the GPU run. Source of the request:
the professor's comments R2 and Q2 (`PROFESSOR-REVIEW-2026-10-31.md`), triage item E1 (`PROFESSOR-REVIEW-TRIAGE-2026-10-31.md`,
GO). EXPLORATORY: added after the preregistered Study 2 result; intervals only, no p-value, no test, no multiplicity claim.
Nothing here changes Study 2's confirmatory reading (noise 0.1, frozen LRF 0.802 vs NONE 0.733).

## Question
On the Study 2 fresh fold, how do the frozen LRF and the unweighted sum (NONE) behave when the Gaussian noise level moves away
from the level LRF was fitted on (sigma 0.1)? In particular: does LRF lose its gain, or harm, at a milder (0.05) or a stronger
(0.2, 0.3) level?

## Data and arms
- Items: the 450 fresh-fold items of `runs/P2-LRF-FOLD/folds_lrf.json` (the n-rule's n_L, `runs/P2-LRF-PLAN/family.json`), the same
  items as `runs/P2-LRF-L1`.
- Conditions: `noise0.05`, `noise0.2`, `noise0.3` (Gaussian, `corruptions.gaussian_noise`, pixel values in [0, 1], clipped).
- Noise draws: common random numbers. Every level uses the noise0.1 stream of L1, `rung_rng(gid, "noise", 0)`, so the noise field
  of an item is the same standard-normal draw scaled by sigma (numpy `Generator.normal(0, sigma)` = sigma x the same standard
  normal for one seed). Differences between levels are then severity, not a new draw. (Study 1's ladder rung 0.2 used another
  stream; no fresh-fold 0.2 result exists, so nothing is compared across streams.)
- Positive control, not a gate: the sigma 0.1 image is rebuilt with the same call and encoded only (no network pass); its codes are
  compared with L1's stored `noise0.1_codes` and the agreement is reported.
- Arms per level: NONE = `y_none` (unweighted sum of per-token evidence), LRF = `y_lrf` (frozen weights,
  `runs/P2-LRF-PINS/pins.json`, unchanged, scored by `exp_p2.gate.lrf_score`). References from L1: clean and noise0.1 (NONE and
  LRF of the same items).
- Everything else is the L1 setting: fixed caption slot 13, length-matched negative (`--neg-len`), TbV on, no sanity or denoised
  copies, same K, D-cache and codebook. The pinned L1 runner `exp_p2/run_gate_m4.py` is not edited; a thin entry point
  (`exp_p2/run_gate_lrf_sev.py`, pattern of `run_gate_lrf_dn.py`) swaps the condition builder for the call only.

## Reporting (fixed now)
- Per level: accuracy of NONE and LRF; paired difference LRF minus NONE, (b - c) / n with discordant counts b, c; 95 percent paired
  percentile bootstrap interval (10,000 item resamples, one index matrix per level from `numpy.random.SeedSequence(0)`, as
  `analysis/paper2/lrf/e1_denoise.py`).
- Gain curve: gain(sigma) = LRF - NONE at sigma in {0 (clean, L1), 0.05, 0.1 (L1), 0.2, 0.3}; and gain(sigma) - gain(clean), with a
  paired bootstrap interval over the same items (this also gives the difference-in-differences of triage item F7 at sigma 0.1).
- Length-matched negative (`y_*_L`) reported alongside when every row has it.
- Wording: descriptive. A level where the LRF-minus-NONE interval lies below 0 is reported as a harm in the main text, whatever
  the other levels show. A level where the interval includes 0 is "no clear difference", never "no effect".
- Where: Table IV (or supplement S-VII if the page cap forbids), one main-text sentence in V-H, deviations item 9.

## Compute and guards
- Per item 30 network rows (3 conditions x (8 B + 1 TbV) + 2 caption-visible + 1 length-matched negative) against 21 for
  `P2-LRF-DN`; expected about 30-40 min busy, about 1-1.5 h wall at duty 0.5.
- Gate-auditor code audit before the GPU. GPU through `exp_p2.gate.gate_driver --stage lrf-sev` with the guard flags
  `--slow-factor 3 --slow-min-s 2 --max-used-first-mib 11000 --max-used-mib 11000 --max-rise-mib 4500 --mem-frac 0.75` and an
  explicit `--max-chunks`. Per-item arrays stay untracked with a SHA-256 manifest.
- Stop rules: any guard abort, a positive-control agreement below 0.99 of tokens, or a non-finite score stops the run; the
  stop is reported, nothing is re-run silently.
