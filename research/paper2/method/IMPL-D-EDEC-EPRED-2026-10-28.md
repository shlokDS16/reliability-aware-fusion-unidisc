```yaml
agent: lab-engineer (implementer D)
date: 2026-10-28
brief: CPU analysis code for E-dec (AD.2, AB.2) and E-pred (AD.3 as demoted by AB.3) so that the E-pred fit can be audited and frozen before the first M4 item
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (AD.1-AD.15 lines 922-1117, AB.1-AB.9 lines 1132-1198)
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (5.3, Prop. 4, lines 216-239)
  - exp_p2/gate/theory.py, headroom.py, seeds.py, stats.py, report.py, analysis_m4.py, run_gate_m3.py, run_gate_m4.py, folds.py, config.py, corruptions.py, arms.py, evidence.py, pipeline.py, runner.py, artifacts.py, pins.py, suite.py (read only; none edited)
  - tests/exp_p2/test_gate_m4_analysis.py (helper `build`), test_gate_swap.py (seed-order test)
coverage: all code paths named in the brief read. NOT read, by instruction or because they do not exist yet: runs/P2-PROBE-02 (nothing opened), any M3/M4/fit-chunk output (none exists), UniDisc code.
  No real-data run was made. Nothing under runs/ was written except temporary rehearsal directories in the scratchpad.
claims:
  - statement: "edec(df_cells) implements AD.2 with the AB.2 names: T = U + R + V asserted to 1e-9 item by item and in every bootstrap resample, joint paired bootstrap (10,000), 95 percent for all cells and 98.33 percent for P cells, shares only if the lower 95 percent bound of tau_T exceeds 0"
    status: supported
    evidence: "tests/exp_p2/test_gate_edec.py, 17 tests green (pytest, this checkout, 2026-10-28); full suite tests/exp_p2: 405 passed, 5 skipped"
    level: E4
    confidence: 0.9
  - statement: "epred_fit / sign function / epred_score implement AB.3 (descriptive: A of K_eval with Clopper-Pearson separately for P and PS cells, o_c and o_c*, rival rules, spec 5.3 refutation flag, no p-value, no test); a fit CLI writes a write-once epred_frozen.json with fit-code hashes and input hashes"
    status: supported
    evidence: "tests/exp_p2/test_gate_epred_fit.py (12 tests), tests/exp_p2/test_gate_epred.py (14 tests), synthetic data only"
    level: E4
    confidence: 0.85
  - statement: "No E-pred or E-dec number from real data exists yet"
    status: supported
    evidence: "no runs/P2-GATE-M3, -M4 or -EPRED-FIT output on disk at the time of writing"
    level: E4
    confidence: 1.0
competing_explanations: []
unknowns:
  - "the fit chunk (GATE flags and PS-cell deltas on the 100 headroom items) has no runner yet; the file contract it must meet is in section 3"
  - "gate-auditor check of epred_fit.py, theory.py and test_gate_epred_fit.py has not happened"
next_test: {hypothesis: n/a (analysis code), intervention: gate-auditor reads epred_fit.py then the fit chunk runs, primary_metric: n/a, falsifier: any test in section 6 failing on the committed code, gpu_hours: 0.17 for the fit chunk (ASSUMED in AD.3, not measured)}
```

# Implementer D: E-dec and E-pred analysis code

Status: code, tests and CLIs written and committed (SHAs in the reply). CPU only. Full suite `tests/exp_p2`: 405 passed, 5 skipped (pytest from the scratchpad `pytest_shim`, because the project `.venv` has no pytest; `test_omni_scorer.py` collected fine, nothing ignored).

## 1. Files

| File | Role |
|---|---|
| `exp_p2/gate/edec.py` | E-dec: row builder, split, identity assertion, bootstrap, shares rule, CLI `run` / `selftest` |
| `exp_p2/gate/epred_fit.py` | **Frozen fit code**: `sign_of_gating`, vectorised sign, `epred_fit`, `reachability`, fit self-test, `seed_fingerprint` |
| `exp_p2/gate/epred.py` | Loading the fit fold, `epred_score`, observed cells from M4 rows, hashing, git checks, write-once, CLI `fit` / `score` / `selftest`; re-exports `epred_fit`, `sign_of_gating`, `reachability` so `epred.epred_fit(...)` works as AD.13 names it |
| `tests/exp_p2/test_gate_edec.py` | 17 tests |
| `tests/exp_p2/test_gate_epred_fit.py` | 12 tests; part of the hashed fit code; imports nothing from other test files |
| `tests/exp_p2/test_gate_epred.py` | 14 tests: scoring, freeze, hashes, CLI order and refusals |

I split the E-pred module in two (a third test file follows) so that AB.3 item 5 ("fit code ... not edited afterwards") does not freeze the score stage: after the first real M4 rows arrive the score/CLI code will probably need a fix, and with one file that fix would invalidate the frozen hash. `FIT_CODE_FILES = (exp_p2/gate/epred_fit.py, exp_p2/gate/theory.py, tests/exp_p2/test_gate_epred_fit.py)`. `seeds.py` is **not** hashed (other families append names to it): its contribution is recorded as `seed_fingerprint` (root seed, the analysis names up to `prop4_plugin`, first four words of that child state); appending later names leaves it unchanged (tested).
SHA-256 (LF-normalised) of the three fit-code files at the time of writing, before the auditor reads them: `epred_fit.py` c89700db..., `theory.py` 5c535a3b..., `test_gate_epred_fit.py` 8d7528bb... (full values are written into `epred_frozen.json` by the fit CLI; they will change if the auditor asks for edits).

## 2. Clause-to-code map

| Clause | Where |
|---|---|
| AD.2 T, U, R, V on d, arms clean/none/chg/GM | `edec.split_parts`, `edec.edec_split`; GM = arm `gate0.05` (`edec.A0`), clean = `conds["clean"]["img"]["none"]` (`cells_from_m4_rows`) |
| AD.2 identity to 1e-9, self-test | `edec.assert_identity` (raises `IdentityError`, an `AssertionError`), checked per item, per resample (`_estimate`); test `test_identity_*`, `test_the_assertion_trips_*`; `edec.selftest` |
| AD.2 accuracy-scale companion | `edec_split(..., y=...)`, `accuracy_scale` block, same complete-case items and the same bootstrap index matrix |
| AD.2 cells P1-P3, PS1, PS2; absent cells counted | `edec.cell_keys`, `cells_from_m4_rows` (reason strings), `edec()` output `absent` |
| AD.2 complete case, counted | `edec_split`: `n_complete`, `n_dropped_incomplete`, `n_nonfinite_by_arm` |
| AD.2 bootstrap, 10,000, joint, 95 / 98.33 for P cells | `edec._estimate` (percentile rule identical to `report._pct`); 98.33 only if `cell in P_CELLS` |
| AD.2 shares only if lower 95 percent bound of tau_T > 0 | `edec._shares` (adds a numeric guard tau_T > 1e-6) |
| AB.1/AB.2 wording: label, names, no causal clause | `edec.NAMES`, `edec.LABEL`, output `limits`; no p-value anywhere in the output (tested) |
| AD.12 order: E-dec after P and PS | CLI `edec run` refuses (exit 3) if `runs/<M4>/analysis.json` does not exist |
| AD.3 cells, fit fold = headroom, assert disjoint from test | `epred.check_fit_fold_disjoint` (head vs test, test_ext and cal by image id; M3 rows subset of head); test with an injected shared id |
| AD.3 fit inputs, pooled token level, classes from Z | `epred_fit.epred_fit` (point estimates through `theory.plug_in_from_deltas`, ddof=1; cross-checked against the sufficient statistics used by the bootstrap) |
| AD.3 prediction s_c = sign(SNR_after - SNR_before), independent of m | `epred_fit.sign_of_gating` (calls `theory.snr`, m = 1; tested against the mu_c = 0 closed form and for m-independence) |
| AD.3 stability share, never changes s_c | `epred_fit.epred_fit` -> `stability`; resamples headroom ITEMS, seed `prop4_plugin` |
| AD.3 / AB.3 item 5 `epred_frozen.json` write-once, hashes inside | `epred.cmd_fit`, `build_frozen`, `write_once_exclusive` (hard link, no `--force` exists) |
| AB.3 item 5 frozen before the first M4 item | `fit` refuses (exit 3) if `runs/<M4>/items.jsonl` is non-empty; `score` refuses if the frozen file's git commit time is later than the first M4 `chunk_start` (`chunks.jsonl`) or if it was never committed |
| AB.3 item 5 fit code committed and audited first | `fit` refuses (exit 11) if `git status --porcelain` shows the fit-code files or `family.json` as modified/untracked (`--allow-dirty` records them in the file); `--audit-record PATH` writes the auditor record's SHA-256 into the file |
| AB.3 item 1 family E withdrawn: no test, no p-value | `epred_score` returns `formal_test: None`; no key `p` anywhere (tested) |
| AB.3 item 2 A of K_eval, CP 95 percent, P and PS separate, never pooled, rivals | `epred._agg`, `RIVALS` ("always +", "- for P cells, + for PS cells"), PS group labelled foregone |
| AB.3 item 3 o_c = sign(b - c_cnt) on Y under every n-rule; o_c* only where the 95 percent interval excludes 0; b = c has no sign (counted, excluded) | `epred.epred_score`, `_o_star`; `observed_cells_from_rows` reads Y from the M4 rows whatever the rule |
| AB.3 item 4 wording; spec 5.3 refutation rule stays | `ALLOWED_WORDING`; `refutation_rule_met_for_cells` |
| AD.13 self-test "E-pred reachability (K = 4 never rejects)" | `epred_fit.reachability`, test `test_reachability_K5_can_reject_K4_never_can` (min p 0.03125 at K = 5, 0.0625 at K = 4, none for K <= 4); printed under `reachability_of_withdrawn_test` as a derived note |

## 3. Exact commands

Interpreter: `C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe` (`PY`), working directory the worktree root.

**Fit (after M3, `family.json` committed, fit chunk finished, fit code committed and audited, before the first M4 item):**
```
PY -m exp_p2.gate.epred fit --run-id P2-GATE-M3 --fit-run P2-GATE-EPRED-FIT --audit-record <gate-auditor record>
```
writes `runs/P2-GATE-EPRED-FIT/epred_frozen.json` (exit 0). Exit 2 on a missing input, self-test failure or an existing frozen file; exit 3 if an M4 item exists; exit 11 on uncommitted fit code or `family.json`. Raises on overlap of headroom and test ids and on a partial fit chunk. Options: `--boot 10000` (default), `--min-items` (default `effective_n.json` of M3, else 100), `--folds`, `--runs-dir`.
Then commit `runs/P2-GATE-EPRED-FIT/epred_frozen.json` before M4 starts.

**Input contract the fit chunk must meet** (no runner exists; I did not write one): `runs/P2-GATE-EPRED-FIT/items.jsonl` (a row with `idx` per finished headroom item, written after the arrays) and `arrays/item{idx:04d}.npz` for every M3 item, with
- `{key}_flag` bool[1024] for each P cell with an operating point (key = the `family.json` key, e.g. `jpeg10`): GATE-M flags, alpha 0.05, frozen M2 threshold, mask seed 20261029, on the M3 rung codes `{key}_codes` (already in the M3 arrays; no re-encoding is needed);
- for PS1/PS2: `patch_codes`, `patch_delta`, `patch_flag` (and the same for `swap`), where codes come from `corruptions.apply_token(name, clean, corruptions.token_rng(config.SEED_GATE, gid, name), grid=32, patch=8, swap_frac=config.SWAP_FRAC, vocab=IMG_VOCAB)` with the headroom `gid` (as M4 does) and `delta = Lambda^{c+}[codes] - Lambda^{c-}[codes]` (`pipeline.image_delta`). M3 stored no PS deltas, so this chunk needs 2 caption passes per item plus 8 B-passes per cell, as AD.3 prices it.
A PS cell with no `{name}_flag` in any item is absent and counted (so a PS2 whose code is not audited is simply "not run"); a cell with flags for only some items is an error.

**Score (after M4 and `python -m exp_p2.gate.analysis_m4 ...` has written `analysis.json`, AD.12 step 5):**
```
PY -m exp_p2.gate.epred score --frozen runs/P2-GATE-EPRED-FIT/epred_frozen.json --run-id P2-GATE-M4 --family-run P2-GATE-M3
```
writes `runs/P2-GATE-M4/epred_score.json`. It refuses (exit 2) if the fit-code hashes or the seed fingerprint differ from the frozen file, and (exit 3) if `analysis.json` is missing or the frozen file was committed after the first M4 chunk start. `--ignore-code-mismatch` exists for diagnosis; the output then says `fit_code_matches_frozen: false`.

**E-dec (AD.12 step 5, after PS):**
```
PY -m exp_p2.gate.edec run --run-id P2-GATE-M4 --family-run P2-GATE-M3
```
writes `runs/P2-GATE-M4/edec.json` (exit 3 if `analysis.json` is missing). `selftest` subcommands exist on both modules: `PY -m exp_p2.gate.edec selftest`, `PY -m exp_p2.gate.epred selftest`.

Tests: `set PYTHONPATH=<scratchpad>\pytest_shim` then `PY -m pytest tests/exp_p2 -q`.

## 4. Ambiguities and the reading I took

1. **AD.3 formal test versus AB.3.** AB.3 item 1 withdraws family E: no test, p-value or alpha. I implemented no p-value. The AD.13 self-test "K = 4 never rejects" is kept as `reachability()` (a derived fact about the withdrawn test), used in the self-test and printed as a labelled note. Not a result.
2. **Tie and undefined signs.** A tie (|SNR difference| <= 1e-12, e.g. a gate that flags nothing) or an undefined sign (a class with fewer than 2 tokens, or a non-positive variance) gives `sign` 0 or None. The cell is excluded from K_eval and counted, with the reason; it is never coerced to + or -. SAP is silent.
3. **m.** The sign is computed with m = 1 (E and Var are both proportional to m). `theory.plug_in_from_deltas` uses m = pooled token count; the code asserts that both agree on the sign.
4. **Stability.** AD.3 says "10,000 headroom-item bootstrap resamples": I resample items, recompute the pooled inputs from per-item sufficient statistics, and count signs. Undefined and tie resamples count as "not the same sign". Seed: existing name `prop4_plugin` (position 19), so no new child seed.
5. **o_c\* interval.** AB.3 item 3 says "95 percent paired-bootstrap interval of the net accuracy difference". I use `report.report_test` with the seed of the cell's own family (`primary` for P cells, `ps_family` for PS cells), on the same arrays, so the interval equals the one `analysis_m4` prints for that test when `--boot` is the same. It is computed from the rows (not from `analysis.json`) because under R3 `analysis.json` holds Wilcoxon results for P and PS without b, c.
6. **Refutation rule.** AB.3 item 4 keeps the spec 5.3 rule but now tied to the accuracy interval (o_c\*). `analysis_m4.run` still computes a separate `prop4_refuted` against the **d** difference; the two can differ. I did not edit `analysis_m4`.
7. **E-dec shares.** The rule (lower 95 percent bound of tau_T > 0) is applied on each scale separately (accuracy scale uses its own tau_T). I added a numeric guard tau_T > 1e-6 for "denominator near zero", a constant the SAP does not give. No interval is given for shares (the SAP gives none).
8. **E-dec bootstrap seed.** Needs a child that does not exist: name `edec`, position 28 (the first after `s2_descriptive`, index 27). `edec.edec_seed()` uses `seeds.seed_for("edec")` if the name is ever appended; otherwise `SeedSequence(20261028, spawn_key=(28,))`, which is exactly what appending would give. I did not touch `seeds.py` because `test_gate_swap.py` asserts the tail of `ANALYSES` equals `("ps_family", "s2_family", "s2_descriptive")`.
9. **Complete case for Y.** Items are chosen on the four d values; Y must then be finite (it always is in M4 rows); if not, `edec_split` raises (rows defective) rather than silently dropping.
10. **Cell labels.** P1 = jpeg, P2 = noise, P3 = splice (order of `config.REALISTIC`), PS1 = patch, PS2 = swap, as `analysis_m4`.
11. **Group reporting.** AB.3 gives K <= 3 for P and PS "labelled foregone", never pooled with suite cells. No pooled P+PS figure is produced; the E-pred `score` output has `P` and `PS` blocks only.

## 5. Concerns for the orchestrator

1. **Fit chunk has no owner.** Section 3 gives the file contract. Until a runner exists and has run, E-pred is "not run" (AB.3 item 5 time-only rule).
2. **Hash scope.** Any edit to `epred_fit.py`, `theory.py` or `test_gate_epred_fit.py` after the freeze makes `score` refuse. `theory.py` is shared with `analysis_m4` and `suite.py`; do not edit it after the freeze.
3. **`exp_p2/gate/suite.py` has its own copies** (`edec_split`, `edec_cell`, `epred_signs`, `epred_agreement`, seeds `[ROOT, 9101/9102]`, pooled sign without tie handling). They are implementer B's, I did not edit them. For a claim-bearing number the audited functions here should replace them (its own docstring says so).
4. **New seed name** `edec` at position 28 (section 4, item 8); appending it needs the `test_gate_swap.py` assertion updated by whoever owns it.
5. **pytest is not in the project `.venv`**; I used the scratchpad shim (`<scratchpad>\pytest_shim` on `PYTHONPATH`). Anyone running the suite elsewhere needs the same.
