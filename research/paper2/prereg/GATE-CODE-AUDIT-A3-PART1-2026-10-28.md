```yaml
agent: gate-auditor (1 of 3, Paper 2 GATE delta audit 623faaff..f938ceab, part 1)
date: 2026-10-28
brief: Delta audit of M4 swap and family PS, analysis seeds, the M1 chance-bar and partial-pool changes (A3b.5a, A3b.12a), E-dec / E-pred and the E-pred fit chunk (AB.3 audit and freeze), and the driver and guards. CPU only; no GPU; no code edited; no analysis run on real M1 data.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md: A2.5 (l.860), AD.2-AD.4, AD.12, AD.13 (l.922-1097), AB.1-AB.3, AB.7-AB.9 (l.1132-1198), A3.3, A3.6, A3.7, A3.8 (l.1250-1292), A3b.5, A3b.5a, A3b.7, A3b.12, A3b.12a (l.1372-1470)
  - research/paper2/method/IMPL-A-SWAP-S2, IMPL-D-EDEC-EPRED (read in full), IMPL-E-INTEGRATION (claims block) -2026-10-28.md; research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md l.210-242 (Prop. 4)
  - research/paper2/prereg/GATE-CODE-REAUDIT-2026-10-28.md (style/baseline, head only)
  - "code at f938ceab (identical to the worktree HEAD 750ce12e for exp_p2/, tools/, tests/; git diff f938ceab 750ce12e -- exp_p2 tools tests is empty): exp_p2/analyze_gate_m1.py, exp_p2/gate/{detect,analysis_m4,arms,corruptions,seeds,edec,epred_fit,epred,theory,gate_driver,runner,pins,hold}.py, exp_p2/{run_gate_m4,run_gate_m2,run_gate_epred_chunk,run_gate_m3}.py, exp_p2/core.py (token_swap), tools/gpu_guard.py (hash only)"
  - tests/exp_p2/{test_gate_m1_chancebar,test_gate_m1_partial,test_gate_swap,test_gate_epred_fit,test_gate_integration}.py (read), test names of the others
  - git object comparisons of 623faaff, f58cd32c, f938ceab (seeds.py, detect.py, analyze_gate_m1.py, gpu_guard.py)
coverage: >
  Covered: every part named in the brief. NOT covered (other auditors or out of scope): S2 re-infill (run_gate_s2, reinfill, analysis_s2), family B and the suite (foil, analysis_foil, suite, run_gate_foil, run_gate_suite), the Omni adapter and runners (omni/, analysis_omni, run_gate_omni_r, run_omni_timing) except that I
  looked at how the driver and the runners call runner.run_items and the guards; edec.py/epred.py CLI paths were read, not exercised on real arrays; any GPU behaviour (UniScorer path of the fit chunk, real seconds, real memory)
  is untestable here and is E0. I did not open runs/P2-PROBE-02 items or arrays (I listed the array file names only, to check the prefix is contiguous: 106 files, indices 0 to 105). No real-data analysis was run.
claims:
  - statement: "tests/exp_p2 passes at HEAD 750ce12e (code identical to f938ceab): 481 passed, 5 skipped (the 5 Omni-stack tests need .venv-omni), 152 s"
    status: supported
    evidence: ".venv python -m pytest tests/exp_p2 -q -x, run in this session (log in the session scratchpad); epred selftest and edec selftest CLI both all_ok true"
    level: E4
    confidence: 0.95
  - statement: "tools/gpu_guard.py is byte-identical to 623faaff"
    status: supported
    evidence: "git diff 623faaff HEAD -- tools/gpu_guard.py empty; git blob and LF SHA-256 equal at both commits (5ddf7d09f1ea830a6a1049b5958974c342cd37a2817e1063e1dbf797d855aa6d); pins.gpu_guard_pin() ok:true; the working copy is CRLF (raw dff4b96c...) as before, which pins.py normalises"
    level: E4
    confidence: 0.95
  - statement: "Analysis seeds: ANALYSES is an append-only extension (25 names at 623faaff, 28 at f58cd32c, 32 at f938ceab); the generate_state(2) of all 28 earlier children is unchanged; the PINNED_CHILD_STATES literal in test_gate_swap.py equals the states computed from the pre-append seeds.py"
    status: supported
    evidence: "I loaded seeds.py from 623faaff, f58cd32c (the pre-append commit) and f938ceab in a scratch script and compared generate_state(2) of every name and the test's literal dict: all identical; appended names edec 28, omni_gate 29, omni_r 30, suite 31 sit at their spawn_key positions. The pin is a literal taken from the pre-append code, so it is not tautological."
    level: E4
    confidence: 0.95
  - statement: "detect.py with min_n=None returns exactly the 623faaff results (candidate_means, paired_vs_best_cheap both branches, falsifier both branches, freeze_rivals, chance_bar, aggregate), including q absent and empty pools; analyze_gate_m1.run_analysis(min_n=None) returns identical values for every key the old one had (chance_bar differs only by the added note), with four added keys (pool, min_n, chance_bar_after_dry_run, chance_bar_both)"
    status: supported
    evidence: "scratch comparison of the old module (git show 623faaff) against the new on seeded synthetic pools of 30, 60, 120, 200 items with 15 percent NaN and with the synthetic probe-2 directories of the repo's own test helper; repr equality"
    level: E4
    confidence: 0.9
  - statement: "analyze_gate_m1.combine_chance_bars and run_analysis/main match A3b.5a items 1 to 6; detect.py and main match A3b.12a items 1 to 8"
    status: supported
    evidence: "line-by-line table in section 2; tests test_gate_m1_chancebar.py (all A3b.5a item 6 cases present) and test_gate_m1_partial.py (all A3b.12a item 8 cases present)"
    level: E3
    confidence: 0.9
  - statement: "EPRED-FIT-AUDIT: PASS for epred_fit.py, theory.py and test_gate_epred_fit.py at the committed blobs listed in section 4"
    status: supported
    evidence: "read in full; sign function checked against spec 5.3 and against a 4-million-token Monte-Carlo (max abs SNR difference 0.002, signs equal in 4 of 4 settings); closed-form test is independent of the code under test; fit self-test and 12 tests pass"
    level: E4
    confidence: 0.85
  - statement: "Two binding SAP items for the swap/PS condition are not implemented in code: ps_frozen.json (AD.4, AD.12 step 2, A3.3 item 1, AB.8) and the runtime patch-size assertion (AB.7 item 2, A3.3 item 3)"
    status: supported
    evidence: "grep ps_frozen over *.py and over IMPL-A and IMPL-E: no hit; run_gate_m4.py:97-98 derives the patch from sc.L_I without an assertion; CONFIG (run_gate_m4.py:40) and cfg (l.194) record the sanity names but no patch size, swap fraction or grid"
    level: E3
    confidence: 0.9
competing_explanations: []
unknowns:
  - "Whether UniScorer.L_I is 1024 at run time (static evidence only: scoring.py:67 comment, probe 2 used GRID 32, PATCH 8); the SAP asks for a runtime assertion, which does not exist (M-2)"
  - "Behaviour of the fit chunk on the real network (only the fake 4 x 4 network is tested)"
next_test: {hypothesis: "M-1 and M-2 are fixed and re-checked, then the fit chunk and M4 can start", intervention: "write ps_frozen.json writer and the assertion; gate-auditor re-reads the diff; run the chunk then epred fit under the freeze rules", primary_metric: "ps_frozen.json committed and the assertion green before the first M4 item", falsifier: "ps_frozen.json missing or committed after the first M4 item (AB.8 withdrawal condition)", gpu_hours: 0}
```

# Gate-code audit A3, part 1 (delta 623faaff..f938ceab)

Audited commit: `f938ceab` (the worktree HEAD `750ce12e` differs only by the IMPL-E report; a later commit by part-2 audit adds one prereg file; `git diff f938ceab HEAD -- exp_p2 tools tests` is empty).
Proposer is not validator: I did not write any of this code. I changed no code.

## 0. Verdict

**PASS WITH FIXES.** No blocker. Two MAJOR items (M-1, M-2) concern the PS/swap condition and must be closed before the first M4 item; they do not touch M1, the seeds, E-dec or the E-pred fit.

| Part | Verdict |
|---|---|
| M1 changes (A3b.5a chance bar, A3b.12a partial pool) | PASS: matches the specification; default behaviour with `min_n=None` reproduced exactly. M1 analysis may proceed once the other conditions of A3b.5 item 10 hold ((a) committed, (c) closing row, (d) co-attestation or its stated absence); condition (b), the audited code change, is met by this note for the diff hashes in section 2 |
| Seeds | PASS |
| M4 swap and ps_family | PASS WITH FIXES (M-1, M-2) |
| E-dec | PASS |
| E-pred score side (`epred.py`) and chunk runner | PASS (minors) |
| **EPRED-FIT-AUDIT** | **PASS** (section 4) |
| Driver and guards | PASS |

## 1. Findings

### BLOCKER
None.

### MAJOR

**M-1. `ps_frozen.json` is required by the SAP and nothing creates it.**
SAP AD.4 ("their parameters are written into `ps_frozen.json` and `family.json` before the first M4 item"), AD.12 step 2 (`ps_frozen.json` committed before the script that reads the test rows), A3.3 item 1, and the AB.8 withdrawal condition ("`epred_frozen.json`, `ps_frozen.json` or `family.json` committed after the first M4 item exists"). Evidence: `grep -rn ps_frozen` over all `*.py` returns nothing; IMPL-A and IMPL-E do not mention it; `headroom.py` writes no patch/swap parameters into `family.json`; the M4 `CONFIG` (`exp_p2/run_gate_m4.py:40`) and the run config (`:194`) record only `sanity=["patch","swap"]`, not the 8 x 8 block, `SWAP_FRAC = 0.15`, the grid, the vocabulary size or the rng tags (`corruptions.TOKEN_RNG_TAG`).
Needed: a small writer (CPU, write-once, committed before the first M4 item) holding `config.PATCH`, the derived `ctx.patch`, `config.SWAP_FRAC`, grid 32, `IMG_VOCAB`, `TOKEN_RNG_TAG`, the code commit; or a dated row from the lead and the statistician that the M4 `config.json` plus the pinned commit stand in for it (that is a SAP change, not mine to make). If neither exists when M4 starts, the AB.8 withdrawal condition applies to PS.

**M-2. The runtime patch-size assertion (AB.7 item 2, A3.3 item 3) is not in the code.**
AB.7 item 2: "the gate-auditor confirms it by a runtime assertion before the first M4 item"; A3.3 item 3: "The patch size assertion (8) of AB.7 is still required at run time". `run_gate_m4.py:97-98` sets `grid=int(round(sc.L_I ** 0.5))` and `patch=max(2, grid // 4)` with no check against `config.PATCH`; the same derivation is in `run_gate_epred_chunk.py:156,159`. Static evidence is consistent (`scoring.py:67` says `L_I` is 1024 at 512 px; probe 2 used `GRID, PATCH = 32, 8`), but I cannot run the network and the SAP asks for a runtime check.
Needed: in both `make_ctx` functions `assert ctx.grid == 32 and ctx.patch == config.PATCH == 8` (refuse with the usual STOP line), plus a test.

### MINOR

- **m-1 (`detect.py:156,193-194`)**: `falsifier(...)["n"]` per corruption comes from `_n_of`, which reads `n_items` = `len(rows)` (the pool size) for an available entry, not the paired finite count that the floor tests. A3b.12 rule 6 asks for "n per corruption". Return `n_pair` in the available dict when `min_n` is set. The floor itself is applied correctly.
- **m-2 (`analyze_gate_m1.py` main, `min_n=MIN_N_PARTIAL if closed`)**: with both flags given and a complete pool (k = n_q = 200), the analysis still runs with the floor, although A3b.12 rule 1 says the 200-item behaviour stands unchanged. Results coincide when every candidate has at least 100 finite values; only extra fields (`n_pool`, `all_n`, `min_n`) appear. Pass `min_n=None` when `complete`.
- **m-3 (`analysis_m4.py` `ps_family` docstring and `on_not_met`)**: both repeat the superseded AD.4 clause ("bars the sentence 'the gate works where detection is easy'" when not met). AB.1 item 1(a) bars that sentence whether PS is met or not, and allows PS to be used only for "pipeline not broken" / "pipeline defect suspected". Wording in output text only; add the AB.1 sentence to `label`.
- **m-4 (`descriptive_ps`)**: T1 and T2 are computed on the M4 test items (the headroom items have no PS deltas in M3), and `D` (AD.4 "T1, T2 and D are computed and printed") is not printed. Descriptive only; label the fold.
- **m-5 (`run_gate_m4.py:79-85`, `run_gate_epred_chunk.py:55-69`)**: `parse_sanity` allows `--sanity swap`; then swap's condition index, hence its jitter stream, differs from the full run, and the E-pred chunk's `condition_indices` (built from its own `--sanity` and `config.DENOISE_FOR`) could disagree with M4's. Forbid dropping patch while keeping swap, or have the chunk read the M4 `sanity` and `denoise_for` from one place.
- **m-6 (`epred.py:440-449,387-390`)**: `epred fit --audit-record` is optional (the chunk requires it), the record is hashed but not checked for the current fit-code hashes, and the chunk's own `config.json` `fit_code` hashes are stored as an input hash but not compared with the hashes at freeze. If the fit code were edited between the chunk and the freeze, nothing would flag it automatically. `run_gate_epred_chunk.py` is also not part of `FIT_CODE_FILES`, so its own hash is recorded only through the pinned commit. Suggest: refuse in `fit` if the chunk's `config.json` `fit_code` differs from the current hashes; record the chunk's hash.
- **m-7 (`config.py:15`)**: `SANITY = ("patch",)` is stale and unused (grep shows no reader); remove or update to avoid a reader taking it as the PS cell list.
- **m-8 (observation, pre-existing design)**: `analysis_m4.run` computes P, the secondary families, PS and calibration in one pass into one `analysis.json`, so AD.12 step 3 ("Family P alone ... output committed before step 4") is procedural, not enforced. The lead should commit the P section before reading PS; no wording may change after later steps.
- **m-9 (observation)**: `analysis_m4.prop4_refuted` (in-sample, on d) and `epred.py`'s refutation flag (accuracy interval, AB.3 item 4) can disagree; IMPL-E raised it. The lead should say which one the paper reports.
- **m-10 (driver, observation for the Omni auditor)**: Omni stages use a 25 min first chunk (default 5), and a missing `OMNI_PY` would raise `FileNotFoundError` inside the driver before a log line. Chunk length is operational (A3.8). No guard value is lowered.

## 2. M1 changes against A3b.5a and A3b.12a

Diff hashes (SHA-256 of `git diff 623faaff f938ceab -- <file>`; blobs at f938ceab): `exp_p2/analyze_gate_m1.py` diff `172c16dd0a7cc4775c39042da30f3cf62c9a5dadeb061d9b8b22f1ac16e60c94`, blob `b8be4429c5c9a0cc4dcd14d59b96600df19b33b5`; `exp_p2/gate/detect.py` diff `1249fcaf0b0b2b53c7910a4b0c0eb59b59a5fa44258c7bcce9817dfdf5a620fc`, blob `1a49ae4b209b0e4cc7f4325a53a4feb9359202fa`; both files together `0a08d6ce6166a1dfb18ff29087956d329ebc0a84d64b0fed80f09c2926fb8170`. Tests: `test_gate_m1_chancebar.py` blob `98095dbf055ba47cd37074de4ffed9194cb829b5`, `test_gate_m1_partial.py` blob `639a89b952bd4ce62564aa71e97429433592c319`.

| Clause | Code | Result |
|---|---|---|
| A3b.5a 1: `MIN_N_CHANCE_BAR = 100` next to `DRY_RUN_N, N_M1`; A3b.12a: `MIN_N_PARTIAL = 100` defined once and reused | `analyze_gate_m1.py:26-28` | met |
| A3b.5a 2: pure function, ignores `passes`/`failed` of inputs; fixed cell list; decided_pass / decided_fail / undecided; missing key and `cb_late` None undecided; cell fail if either pool decided_fail, pass if both decided_pass | `_cell_status`, `combine_chance_bars` | met. One unreachable difference: `lower95 is None` is "undecided" where the text would say decided_fail; `chance_bar` never returns an available cell with `lower95` None |
| A3b.5a 3: returned fields (`verdict`, `passes` True/False/None, `failed`, `audit_trigger`, `min_n`, `n_all`, `n_late`, `complete`, per cell `all`, `late`, `n_all_cell`, `n_late_cell`, `status_all`, `status_late`, `result`, `audit_flag_point_estimate`, `rule` naming A3b.5) | `combine_chance_bars` return (cells under `per_score`) | met |
| A3b.5a 4: (a) contiguous-prefix assertion with both lists printed; (b) `pool` entry with `n_items`, `n_late`, `last_idx`, `complete`, `item_idx_sha256` of the JSON list; (c) `note` on `chance_bar` and `chance_bar_after_dry_run`; (d) label unchanged | `run_analysis` | met (a: raises ValueError before any array is loaded). The 106 current array files are 0 to 105, contiguous |
| A3b.5a 5: `main` prints verdict, per-cell n for both pools, `min_n`, the UNDECIDED text "UNDECIDED: n below 100 in at least one cell-pool; not a pass", old "incomplete" branch replaced | `main` | met |
| A3b.5a 6: tests (n parameter, k = 106 undecided, 200/179 passed, 100 vs 99, decided failure dominates, fail-in-all/undecided-in-late, q below floor, `cb_late` None, missing key, non-prefix raises) | `test_gate_m1_chancebar.py` | all present and not tautological (cells built from n and lower95; one test makes the input `passes` fields lie) |
| A3b.12a 1: `candidate_means(rows, cheap, min_n=None)` | `detect.py:101-107` | met |
| A3b.12a 2: `freeze_rivals(..., min_n=None)` unavailable entry text, `n_items` = finite count of the rival, `n_pool`, `all_n` | `detect.py:221-239` | met (adds `min_n` to the entry) |
| A3b.12a 3: `paired_vs_best_cheap(..., min_n)` unavailable below floor in both branches | `detect.py:118-156` | met (the reselect floor uses the items finite for the target and every eligible candidate, which is the set the branch really uses). See m-1 for `n` |
| A3b.12a 4: `falsifier(..., min_n)` False if wins, True if both available and no wins, None otherwise; `min_n` and `n` returned; default keeps `falsified = not wins` | `detect.py:165-194` | met except m-1 |
| A3b.12a 5: `run_analysis(min_n)` passes it to `paired_vs_best_cheap`, both `falsifier` calls, the late-pool `falsifier`, `freeze_rivals`; `main` has `--closed-k`, `--closed-nq`, `run_analysis(min_n=MIN_N_PARTIAL if closed)` | `analyze_gate_m1.py` | met (m-2 for the complete-and-flagged case) |
| A3b.12a 6: write when complete or closed_partial; mismatch prints both counts and returns 2 without writing; partial content adds `partial`, `closed_k`, `closed_nq`, `min_n`, `source`; "NOT written" message names the flags; one flag alone returns 2 | `main` | met. The mismatch check runs before `analysis.json` and the freeze are written (a mismatch writes nothing; the analysis is computed first, in memory) |
| A3b.12a 7: `frozen_meta` in `analysis.json` and in the S-D2 label | `analysis_m4.py` `frozen_label`, `s_d2`, `run`, `main` | met; S-D2 keeps p = 1 and m = 2 for an unavailable entry and says why |
| A3b.12a 8: tests | `test_gate_m1_partial.py` | all cases present (120 items with flags writes a partial file without q; 99 items all unavailable; mismatch returns 2 and writes nothing; 120 without flags writes nothing; falsifier cases; 99-finite candidate not selected; write-once) |

Default behaviour: `detect.py` at `min_n=None` and `run_analysis(min_n=None)` reproduce the 623faaff results (claim 4 above). Nothing under `runs/` was read. Per A3b.5 item 10 the first real run of `analyze_gate_m1` on items 26 onward still waits for the closing row, the commit of the addendum, and the co-attestation or its stated absence.

## 3. Other parts

**M4 swap, PS family, seeds (AD.4, A2.5, AB.7, A3.3).**
- Swap is `core.token_swap` (round(0.15 x 1024) = 154 positions replaced by uniform codes), own stream `[SEED_GATE, gid, 191]`; patch keeps 190 and is bit-identical to the old formula (test). The tag does not collide with `[SEED_GATE, gid, 99/100-125/150]` or the 5-element arm streams.
- Swap is appended after patch in `build_conditions`; every earlier condition index and arm seed is unchanged (test compares every earlier condition row and array with and without swap). No text arms for swap (A3.3 item 2); pass count 78 without TbV (70 + 8), 84 with. `ARM_TAG` 1-5 unchanged, 6-11 new and unique.
- `ps_family`: m = 2 always, p = 1 for a cell not in the rows, same fold/endpoint/test as P (R1/R2 exact McNemar on Y, R3 Wilcoxon on d with positive mean), Holm via `stats.holm`, rejection `p_holm < 0.05` with the right sign (same as P), reading met / partly met / not met. Calibration, mechanism and K4 treat patch and swap without touching the clean-only K4 check. A run made before swap existed still analyses (test).
- A3.3 item 1 asks for a fresh M4 run: `runs/P2-GATE-M4` does not exist. M-1, M-2 and m-3 to m-5 above.

**E-dec (AD.2, AB.2).** `T = d_clean - d_none`, `U = d_clean - d_chg`, `R = d_GM - d_none`, `V = d_chg - d_GM`; the identity is asserted to 1e-9 item by item and in every resample; items are resampled jointly (one index matrix for d and Y); 95 percent for all cells, additionally 98.33 percent for P cells (quantiles 0.00835/0.99165, as `analysis_m4`); shares only if the lower 95 percent bound of tau_T is above 0 (plus a numeric guard 1e-6, disclosed); complete case on four finite d values, counted by arm; absent cells counted; AB.2 names; no p-value anywhere; runs only after `analysis.json` exists (AD.12). Seed is the appended `edec` child (position 28, equal to the fallback of A3.7). Same row population as P (`analysis_m4.load_items`). PASS.

**E-pred score side (`epred.py`, AB.3 items 1 to 4, A3.6 items 2 and 4).** No test, no p-value (`formal_test: None`); o_c = sign(b - c_cnt) on Y whatever the n-rule; o_c* only where the 95 percent interval excludes 0; ties/undefined signs and b = c excluded and counted; A of K_eval with Clopper-Pearson separately for P and PS (PS labelled foregone), never with the suite; rival rules as AB.3 item 2; refutation flag on o_c*; `score` refuses if the fit-code hashes or the seed fingerprint differ, if `analysis.json` is missing, or if the frozen file was committed after the first M4 `chunk_start` (verified that the runner writes `event="chunk_start"` with `t`). `fit` refuses when an M4 item exists, when the fit code or `family.json` is uncommitted (exit 11), on overlap of head/test/cal ids, and on a partial fit chunk; the frozen file is written by hard link, so it is write-once with no force flag.

**Fit chunk runner (`run_gate_epred_chunk.py`, AD.3, AB.3 items 5-6, npz contract of IMPL-D section 3).** Read in full. Flags use the same recipe as `run_gate_m4.process` (same `item_groups` with the 20261029 seed, same `gate_scores`, same `cal.jitter` stream with the M4 condition index, same `tau` of alpha 0.05); P-cell codes and Delta come from the M3 arrays (`clean`, `{key}_codes`, `{key}_delta` are stored by `run_gate_m3.process`); PS codes use `token_rng(SEED_GATE, gid, name)` as M4; output keys match `epred.load_fit_inputs` (`{key}_flag`; `{patch,swap}_{codes,delta,flag}`); no image is loaded and no encode runs; refusals before the model is touched: missing/uncommitted `family.json` (2), M3 incomplete (2), audit record missing (2), M4 item or frozen file present (3), dirty fit code (11). Goes through `runner.run_items` with guards and watchdog. Tested on the fake network only (UniScorer path E0). See m-5, m-6.

**Driver and guards.** `gate_driver.py` keeps, for every stage including the eight new ones: hold-file check before launch and before every chunk (`hold.active_holds`), `pins.require_clean` (exit 11), the `gpu_guard.py` pin (exit 10), the Windows event-log check (exit 9, fail closed), the AC check (exit 8), guard-stop never relaunched, the three-temperature-stop and two-no-progress rules, `--allow-dirty` forwarding. `runner.py`, `pins.py`, `hold.py`, `guards.py`, `watchdog.py` and `tools/gpu_guard.py` are unchanged in the delta (empty `git diff --stat`). Every `run_gate_*` and the Omni runners call `runner.run_items` with `guards`, `watchdog_factory=runner.default_watchdog` and `allow_dirty`. Refusal reasons: `REFUSAL_EXITS = (2, 3, 10, 11)`, `refusal_reason` reads the last `STOP` line (else the last line) of the chunk log, never raises, and changes no stop rule (tests `test_a_refusal_exit_writes_the_reason...`, `test_the_reason_falls_back...`). The relaxed assertions in `test_gate_runner.py::test_stage_table_matches_the_modules_and_run_ids` are covered per stage by `test_gate_integration.py` (run ids, commands, hold/dirty/pin/battery/events for each new stage). `run_gate_m2.py` adds only `n_rows` (as M4 does). Nothing weakens a guard. See m-10.

## 4. EPRED-FIT-AUDIT

**EPRED-FIT-AUDIT: PASS**

Audited content = the committed blobs below (the repository stores LF; the working tree here is CRLF for two of the files because `core.autocrlf` is true, so the raw working-tree SHA-256 differs; `epred.fit_code_hashes` records both, and `score` compares the LF value). Working tree equals HEAD (no uncommitted change).

| File | SHA-256 (LF, = committed blob content = `sha256_lf` in `epred_frozen.json`) | SHA-256 raw working tree (CRLF) | git blob |
|---|---|---|---|
| `exp_p2/gate/epred_fit.py` | `c89700dbc3ba4da61f4f8ae681a5775d05e54cbbf3a86d05650e4151d5d29abc` | `a23e97ac0ff95cfd9054f4533fb6212f1faaa080ca99152db5c8c48a7a106c52` | `8685835a9c3b3cfd377ce944c33e37a71ea716ea` |
| `exp_p2/gate/theory.py` | `5c535a3bda759e0bc3ef7b888b8a773ce2d0cf077c2b515661fda0a9ae00ab46` | same (LF) | `4d2b550016e4563eb3506eaf5ccfda4b6b168748` |
| `tests/exp_p2/test_gate_epred_fit.py` | `8d7528bbb37b9f125f80c37d13baadfcee01f347343910861c6fa355cabad25f` | `904363204aeeaa99c38010530fed4cbd3d0caeba97d60b3c3d99572e77eadca8` | `db2c9db62250ed538aba52262841422046690d68` |
| `exp_p2/run_gate_epred_chunk.py` (reviewed; not in `FIT_CODE_FILES`, so not frozen in the file) | `45a1c0c5a0d24ede7e4adfa4819e433ee96371ca0cac26c6df37e05e8410cc3d` | same (LF) | `f0853fb9bd63e9b7b9e0fd4752b7a6a08bf13f75` |

What the PASS covers and why:
1. The sign function implements spec 5.3 (general form with mu_c not 0): `theory.mean_var` equals the E S and Var S of the spec line by line; `sign_of_gating` takes the sign of SNR_after - SNR_before with m = 1 (m cancels); ties within 1e-12 and non-finite or non-positive-variance inputs give no sign, counted. A Monte-Carlo of 4 million tokens at four parameter settings gave SNR values within 0.002 of the formula (the small gap is the between-class term of a random-class simulation, which the fixed-class model of the spec does not have) and identical signs.
2. The fit follows AD.3 with the AB.3 demotion: classes from the changed-code labels, point estimates pooled over the headroom items at token level (ddof = 1), alpha_obs and beta_obs from the flags, stability share over 10,000 item-level resamples with the existing `prop4_plugin` seed that never changes s_c, cells absent and counted, no test, no p-value. The vectorised bootstrap sign equals the scalar sign (tested). The closed-form test uses `theory.special_case_inequality`, which the code under test does not call.
3. `theory.py` is unchanged since its only commit (`5b295ee4`, before this delta) and is shared with `analysis_m4.calibration`; it is frozen from this audit onward (A3.6 item 2, A3b.7 item 3).
4. The 12 fit tests, `epred.selftest` and `edec.selftest` pass here.

Conditions of the PASS: (i) the three frozen files are not edited after this audit; any edit needs a new audit and, after the first M4 item, a dated addendum (A3.6 item 2); (ii) this audit note is the `--audit-record` for the chunk and `epred fit`: it must be committed before the chunk runs and not edited afterwards, because its SHA-256 goes into `config.json` and `epred_frozen.json`; (iii) M-2 should be fixed in `run_gate_epred_chunk.py` (which is not a frozen file) before the chunk runs, so the chunk's patch size is asserted too; (iv) the lead decides on m-6 (a check that the chunk ran with the same fit-code hashes as the freeze) before the chunk runs.
The chunk runner itself is reviewed and has no blocking defect; its GPU path is untested.

## 5. Seeds table

| Commit | Names | Notes |
|---|---|---|
| 623faaff | 25 (`load_items` ... `denoise_check`) | baseline |
| f58cd32c | 28 (+ `ps_family`, `s2_family`, `s2_descriptive`) | the states in `PINNED_CHILD_STATES` were taken here |
| f938ceab | 32 (+ `edec` 28, `omni_gate` 29, `omni_r` 30, `suite` 31) | `generate_state(2)` of the first 28 equal across the three commits (scratch script, section "claims"); A3.7's append-only check met; `seed_for` spawns by index, so appending cannot move an earlier child |

## 6. Not done / for the lead

- I did not run anything on real M1 data, did not open any item or array, and did not exercise any GPU path.
- The attribution trailer: the brief asks for `Claude Opus 5.5`; this agent is Sonnet 5.5 and the session attribution rule says to sign with the model that wrote the commit, so the commit carries `Claude Sonnet 5.5`.
- No ledger rows were added (the brief names none).
