```yaml
agent: python-expert
date: 2026-10-28
brief: Implement the Tier-3 fusion comparators of Paper 2 / GATE (SAP Addendum A4 r1, section A4.1) as a CLI module with synthetic tests. Not run on any real data.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md (A4.1.1 to A4.1.11)
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md (A4 signature; C4-9, C4-10)
  - code read: exp_p2/run_gate_m4.py (process, build_conditions), exp_p2/run_gate_m2.py (process), exp_p2/gate/evidence.py, scores.py (suspicion_q), fit_threshold.py, calibrate.py, artifacts.py, seeds.py, pipeline.py (compact, image_delta), analysis_m4.py (load_items, primary, corr_of, SANITY_CONDS), report.py (report_test keys), foil.py (require_committed), runner.py (npz write)
  - structure only (keys, committed design values): runs/P2-GATE-M3/family.json (rule, family keys), runs/P2-GATE-M3/ps_frozen.json (params), runs/P2-GATE-M2/threshold.json
coverage: >
  runs/P2-GATE-M4/items.jsonl and runs/P2-GATE-M4/arrays were NOT opened (the worktree has no such files; the module also refuses before it opens them). No M2/M3/M4 outcome value
  was read. Tests use synthetic fixtures in a temporary directory and a temporary git repository only. The module has NOT been run on real data.
claims:
  - statement: "All 31 tests of tests/exp_p2/test_gate_comparators.py pass on CPU (about 16 s)"
    status: supported
    evidence: "python -m pytest tests/exp_p2/test_gate_comparators.py -q (31 passed)"
    level: E4
    confidence: 0.95
  - statement: "The module implements A4.1 as written; ambiguities are listed below, none resolved by inventing a parameter"
    status: supported
    evidence: "spec-to-code map below"
    level: E3
    confidence: 0.8
competing_explanations: []
unknowns:
  - behaviour on the real M4 arrays (never read)
  - whether the lead wants the file name tier3_fusion (spec) or comparators (brief)
next_test: {hypothesis: "none (implementation)", intervention: "gate-auditor delta check of the module against A4.1, then a dated pin row (C4-10)", primary_metric: "none", falsifier: "none", gpu_hours: 0}
```

# Implementation report: Tier-3 comparators (A4.1)

## Files (all new; no existing file under `exp_p2/`, `tools/` or `tests/` was modified)
- `exp_p2/gate/comparators.py` (module and CLI)
- `tests/exp_p2/test_gate_comparators.py` (31 tests, synthetic data only)
- this report

Not touched: `exp_p2/gate/seeds.py` (A4 r1: no append), `epred_fit.py`, `theory.py`, `tests/exp_p2/test_gate_epred_fit.py`, `exp_p2/omni/checks.py`, `tools/gpu_guard.py`, `analysis_m4.py`, `run_gate_m4.py`, `fit_threshold.py`. Reused without change: `analysis_m4.load_items / corr_of / SANITY_CONDS`, `evidence.evidence_from_delta`, `scores.suspicion_q`, `fit_threshold.suspicion_from_arrays`, `calibrate.ids_hash / Threshold`, `artifacts.write_once`, `common.RUNS / read_jsonl`, `seeds.ROOT_SEED`.

## CLI
`python -m exp_p2.gate.comparators run --run-id P2-GATE-M4 --cal-run P2-GATE-M2 [--family-run P2-GATE-M3]`. Exit 0 written; exit 2 refusal or write-once collision (reason on stderr); exit 3 consistency-gate failure (A4.1.3, stderr). Output `runs/<run-id>/comparators.json`, write-once through `artifacts.write_once` (force never passed), no timestamp or git SHA inside, so a recomputation is byte-identical. Printed on success: the path, the cells, the number of intervals and "no multiplicity adjustment (SAP 7)".

## Spec-to-code map
| Spec | Code |
|---|---|
| A4.1.1 label, no p-value, no multiplicity | `LABEL`, `multiplicity` field (count of intervals + the SAP 7 sentence); no scipy import, no test call (AST test); test scans every output key for p-value names |
| A4.1.2 data, cells, complete case | `load_cell`, `_complete_case` (npz holds `<cell>_delta` with 1,024 finite values, `<cell>_flag0.05`, finite `<cell>_B`, `<cell>_D`); one item set per cell for all arms; exclusions counted with reason and idx; `run` builds cells: `clean`, family keys of `family.json` (P cells), `patch`/`swap` (PS cells, own `ps_cells` block with the pipeline-check note); denoised copies and the text direction listed under `not_computed` |
| A4.1.3 consistency gate | `consistency_problems` (y equal, mean within 1e-9 for NONE and GM against stored `img.none`, `img["gate0.05"]`; g_i against `gate["0.05"].n_flag`); runs over every item of every cell before anything is computed; any mismatch raises `ConsistencyError` |
| A4.1.4 arms | `item_margins`: NONE, GM, MED (`numpy.median`), TM-G (k = floor(g/2) per tail), TM20 (k = floor(0.20 m) = 204), SOFT-G, SOFT-A; sorting in float64; k = 0 uses the plain mean in original order (TM-G with g <= 1 is NONE bit for bit); ties and empty sets give Y = 0 and are counted (`n_ties`, `n_empty`) |
| A4.1.5 weights | `CalPool` (S_cal, P_cal from `searchsorted`; `weights_g`, `weights_a`); pool built by `build_cal_pool` from the M2 `items.jsonl` + `arrays` (clean pairs), asserting `calibrate.ids_hash` equals `threshold.json` `ids_hash`, u^cal by `fit_threshold.suspicion_from_arrays(arr, "q")` unjittered, equal token counts asserted; SHA-256 of every M2 npz and of `threshold.json` written to the output (the "otherwise" branch of the freeze clause) |
| A4.1.6 decision rule and metric | `cell_results`, `accuracy_contrasts`: n, both accuracies, b, c, n_d, (b-c)/n, 95 percent interval, MDD for every contrast; the R3 note is written when `analysis.json` rule is R3 |
| A4.1.7 contrasts, intervals, seeds | `accuracy_contrasts` (MED, TM-G, TM20, SOFT-G, SOFT-A minus GM and minus NONE; GM minus NONE is quoted from `analysis.json`, p-values not copied); `index_matrix` (`default_rng(child).integers(0, n, (10000, n))`, one per cell, shared by all arms and contrasts); `bootstrap_interval` (`numpy.quantile` 0.025 / 0.975 default method; MDD = 2.801585 x SD ddof 1); `cell_seed_sequence` (`SeedSequence(20261028, spawn_key=(32,))` spawned into the 6 slots clean, jpeg, noise, splice, patch, swap; the slot of a cell is fixed by name, so an absent cell does not move another); the output states it is the documented fallback |
| A4.1.8 trimming control on d | `retained_d`, `d_control` (NONE, GM, TM-G, TM20; contrasts TM-G minus GM and TM20 minus GM; same index matrix; drops counted; MDD) |
| A4.1.9 order | `require_committed` runs first in `run` (before `items.jsonl` or any array is opened; tested): `analysis.json` must exist, be git-tracked and have no staged or unstaged change, and hold `primary.per_corruption`; output write-once |
| A4.1.10 reading | `reading` (above / below / not_distinguishable), `counts_against` for MED, TM-G, TM20 (above = against the method; not distinguishable = against added value only if MDD <= 0.05, else "uninformative at this n") and SOFT-G, SOFT-A (above = against discarding; not distinguishable = discarding and discounting / weighting not distinguishable), emitted only for "minus GM" on P cells; the limits (a) to (d) are written into the output (`limits`) |
| A4.1.11 self-tests | all listed self-tests are in the test file (see below) |

## Tests (tests/exp_p2/test_gate_comparators.py)
Arms on hand-computed fixtures (m = 8: median 1.5, TM20 7/6, TM-G 1.25 at g = 4 and g = 5, GM 12/7; weights on a 10-token calibration pool: S(tau)=0.3, w^G = 1, 2/3, 1/3, 0, 1; w^A = 2/11, 1, 6/11, 8/11; SOFT-G = 5/2); NONE and GM equal `evidence_from_delta`; TM-G with g <= 1 equals NONE exactly; trimmed mean with 511 per tail equals MED at m = 1024; TM20 removes 204 per tail; SOFT-G with no flags equals NONE and with S_cal(tau) = 0 equals GM; weight ranges and monotonicity; ties and empty sets (also at cell level, counts); consistency gate passes, and stops on an injected y, mean (beyond 1e-9), n_flag or missing summary, and at CLI level (exit 3, no output file); refusal (no analysis.json, untracked, staged only, modified after commit, no P section) and that no M4 or M2 rows are read before the refusal; refusal on item-count, family or calibration-hash mismatch; write-once; bootstrap determinism by seed and slot, seed slots equal the spawn child 32, slot independence when a cell is absent; MDD on a known SD (hand-computed idx matrix); three-way reading and `counts_against`; d control by hand incl. drops; incomplete-case exclusions with reasons; full CLI end to end; byte-identical recomputation; no p-value key in the output and no test function imported or called.
Not run: the full suite (CPU shared with the running GPU stage). No existing test was run, since no existing file changed.

## Ambiguities (most literal reading implemented; none resolved by inventing a parameter)
1. **Names.** A4.1.11 names `exp_p2/gate/tier3_fusion.py`, CLI `--run-id --family-run --cal-run`, output `tier3_fusion.json`, test `test_tier3_fusion.py`. The brief asks for `comparators.py`, `comparators run --run-id --cal-run`, `comparators.json`, `test_gate_comparators.py`; the brief was followed. `--family-run` (default `P2-GATE-M3`) is an optional extra so the spec's family source is reachable; the requested call works with defaults. The lead should reconcile the file name with SAP A4.1.9 ("tier3_fusion.json") and the A4.1.11 pin row.
2. **"Committed".** Implemented as git-tracked and clean in the repository that contains the file (same test as `foil.require_committed`, but repository found from the file). It checks that `analysis.json` has a `primary.per_corruption`; it cannot check "P section committed before step 4/5" order.
3. **Extra consistency checks** not named in A4.1: `len(items.jsonl rows) == analysis.json n_items` ("exactly those analysis_m4 analysed") and `family.json` keys equal `analysis.json` `family`. Either mismatch refuses. Remove if unwanted.
4. **Cells.** P cells come from `family.json`; PS cells from `ps_frozen.json` `params.sanity_order` (falls back to `("patch","swap")` if the file is absent) intersected with the conditions present in the rows; absent ones are listed in `not_run_ps_cells`. The seed slot of a P cell is its `corruption` field in `family.json`.
5. **GM minus NONE.** Quoted from `analysis.json` for P cells only (`primary`, or `secondary_y` under R3); p-values are not copied. Not given for the clean and PS cells (not named in the spec; the clean-cell cost of each combiner is read from its minus-GM and minus-NONE contrasts).
6. **d control with dropped items.** The spec says the "same index matrix" and that items are "dropped and counted". Implemented: the matrix is the cell's own (over all complete-case items) and the drop is applied inside each resample (valid-weighted mean of the resampled items); a resample with no valid item is NaN and counted (`n_undefined_resamples`). SE for the MDD is the ddof-1 SD of the finite resamples.
7. **TM-G with g = m** (all flagged, m even): k = m/2, empty retained set, Y = 0, counted as empty. Also TM-G with k > 0 sorts in float64 and averages `sorted[k:m-k]`; k = 0 is the plain mean.
8. **Consistency failure** is reported on stderr (first 10 mismatches) with exit 3; no file is written, so the write-once output is not consumed. The spec says "reported as a pipeline discrepancy" without a file.
9. **`counts_against`** (A4.1.10) is emitted for "minus GM" on P cells only; the "below" reading is labelled `gate_higher`; the MDD <= 0.05 comparison is inclusive. A4.1.10's exact sentence wording is left to the writer; the output holds the mechanical label.
10. **Pre-frozen weight file.** `runs/P2-GATE-M2/soft_weight_frozen.npz` (A4.1.5 preferred freeze) is not read or written; the pool is always recomputed from the M2 arrays with their SHA-256 recorded (the spec's fallback). M4 was already running, so the preferred freeze point has passed.
11. **Threshold.** tau is read through `calibrate.Threshold.from_json` (float64, "inf" strings decoded); calibration u is the float32 `suspicion_q` promoted exactly to float64 before `searchsorted`, and the test token u is the unjittered float32 `suspicion_q(B, D)` promoted the same way.
12. **Bootstrap size** 10,000 is a constant, not a CLI option (tests pass a smaller `n_boot` to functions only).
13. **Token count** 1,024 is the constant `M_TOKENS`; functions take `m` so tests can use small vectors; TM20's k is floor(0.20 m).

## Notes for the lead
- C4-10: both new files are inside the card's pre-launch scope (`exp_p2`, `tests`). The commit on this branch is not merged or pushed; merging requires the dated pin row and the gate-auditor delta check before the module runs. `seeds.py` is unchanged.
- The module has not been run on M4. First real run: after `analysis.json` (with P) is committed and steps 4 and 5 are done, as A4.1.9 orders.
