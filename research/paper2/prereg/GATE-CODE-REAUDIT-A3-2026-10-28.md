```yaml
agent: gate-auditor (delta re-audit of the three A3 code audits, Paper 2 GATE)
date: 2026-10-28
brief: Re-audit of the fixes for GATE-CODE-AUDIT-A3 part 1, part 2 and part 3 (Omni): round 3 (1051d01f, 9fae9b66) and engineer F (6a7e7d87); rule on engineer F's readings D1-D5 and on open item m1; frozen-file identity; no weakened guard; write the CPU adapter signature if every MAJOR is fixed. CPU only; no code edited.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/GATE-CODE-AUDIT-A3-PART1-2026-10-28.md, ...-PART2-2026-10-28.md, ...-PART3-OMNI-2026-10-28.md, LEAD-DECISIONS-2026-10-28-PM.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (AD.4 l.979, AD.12 l.1085, AB.7 l.1180-1186, AB.8 l.1194, A3.1 l.1217-1233, A3.2 l.1239-1248, A3.3 l.1250-1256, A3b.1 l.1329-1337, A3b.2 l.1339-1346, A3b.3 l.1348-1358, A3b.4 l.1360-1370, A3b.6 l.1399-1406, A3b.7 l.1408-1415)
  - research/paper2/method/IMPL-E-INTEGRATION-2026-10-28.md (Round 3, l.186-225), IMPL-F-AUDIT2-FIXES-2026-10-28.md (read in full)
  - "code at HEAD 8c9edf8c (exp_p2, tools and tests byte-identical to 6a7e7d87): exp_p2/gate/{ps_freeze,detect,analysis_m4,analysis_s2,analysis_foil,foil,mde,suite,analysis_omni,epred,runner,gate_driver,reinfill,pins,artifacts}.py, exp_p2/omni/{signing,build,checks}.py, exp_p2/{run_gate_m4,run_gate_epred_chunk,run_gate_s2,run_gate_s2_smoke,run_gate_foil,run_gate_suite,run_omni_timing,run_gate_omni_r}.py, tests/exp_p2/{conftest,test_gate_ps_freeze,test_gate_swap,test_omni_runners}.py (read); git diff f938ceab..HEAD of exp_p2, tools, tests (read, including every removed line)"
  - tests run (targeted, CPU, CUDA hidden): test_gate_ps_freeze, test_gate_s2, test_gate_foil, test_gate_suite, test_omni_analysis, test_omni_signing, test_omni_runners, test_gate_epred_fit, test_gate_m1_partial, test_gate_swap, test_gate_epred_chunk, test_gate_epred
coverage: >-
  Covered: every finding of the three audits, D1-D5, m1, frozen-file identity, the guard review of the whole delta, pins.require_clean. NOT covered: any GPU path (UniScorer, bitsandbytes, real peak memory, real seconds, CUDA multinomial), the five omni-stack tests that need .venv-omni
  (not re-run; the lead's full run decides), the full suite (the lead's), the S2 run card, card v4 and the pin (not yet written), the A1-A7 numbers on the real model. runs/P2-PROBE-02 was not opened (no item, no array). Nothing in runs/ was read except the committed
  runs/P2-GATE-FOIL/leak_check.json and pool.json (through the code's own check_pool, read-only) and runs/EXP-001 manifest (through pins.gpu_guard_pin).
claims:
  - statement: "All five MAJOR findings of part 2, both of part 1 and both of part 3 are fixed in code and by tests; none of the fixes weakens a guard, exit code, refusal rule or write-once rule."
    status: supported
    evidence: "section 1 table; git diff f938ceab..HEAD -- exp_p2 tools read including every removed line (section 4); targeted tests 247 passed, 102 s"
    level: E4
    confidence: 0.9
  - statement: "The five frozen files are byte-identical to f938ceab and the part 1 audit file is unedited since its only commit 07f5d56d."
    status: supported
    evidence: "git rev-parse f938ceab:<path> equals HEAD:<path> for all five (blobs in section 3); LF SHA-256 of the three E-pred files c89700db, 5c535a3b, 8d7528bb; checks.py 9e397f2a; gpu_guard 5ddf7d09; part 1 audit blob 41358180 at 07f5d56d and HEAD, git log shows one commit"
    level: E4
    confidence: 0.98
  - statement: "keep_best has no NaN guard and silently selects a NaN draw."
    status: supported
    evidence: "reinfill.py:102-104; auditor probe (scratchpad reaud/probe1.py): keep_best([-3, nan, -1, -1]) returns 1, the NaN draw; finite ties still return the lowest index"
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - "Whether a NaN or infinite chain log-likelihood can occur on the real network: torch.multinomial raises on NaN probabilities on CPU; the CUDA behaviour with a CUDA generator is untested by anyone (E0)."
  - "Whether UniScorer.L_I is 1024 on the real network: now asserted at run time (ps_freeze.assert_runtime), still not observed."
next_test: {hypothesis: "m1 is fixed as specified in section 2 and the lead's full run is green", intervention: "diff re-check of reinfill.py keep_best and its tests", primary_metric: "keep_best raises on any non-finite entry and returns the same index as before on finite input", falsifier: "any finite input whose result changes, or a NaN that is still selected", gpu_hours: 0}
```

# Gate-code re-audit A3 (delta f938ceab..8c9edf8c), parts 1, 2 and 3

Audited commit: **8c9edf8c547d8e0a6cd111cd20187f3917b49ac4**. `git diff --stat 6a7e7d87 8c9edf8c -- exp_p2 tools tests` is empty (the later commits are reports only), so the code audited is the code at 6a7e7d87. Working tree: no tracked file is modified. I did not write this code and changed none of it.

## 0. Verdict

**PASS WITH FIXES.** Every MAJOR of the three audits is FIXED (9 of 9: part 1 M-1, M-2; part 2 M1 to M5; part 3 M-1, M-2). One small code change is **required before the S2 smoke and before the card v4 pin**: the NaN guard in `keep_best` (section 2, ruling R-m1). Nothing else blocks. The adapter CPU signature is written (section 5).

| Item | Result |
|---|---|
| Part 1 MAJOR M-1, M-2 | FIXED |
| Part 2 MAJOR M1-M5 | FIXED |
| Part 3 MAJOR M-1, M-2 | FIXED |
| Engineer F decisions D1-D5 | all consistent with the SAP (section 2) |
| m1 (`keep_best` NaN) | must be fixed before S2 (section 2) |
| Frozen files | byte-identical; part 1 audit file unedited (section 3) |
| Guards, exit codes, refusals, write-once | none weakened; five strengthened (section 4) |
| `pins.require_clean` | clean at HEAD (`(True, [])`); `gpu_guard_pin` ok true |
| Targeted tests | 247 passed (12 files, CPU) |

## 1. Finding -> status

### Part 1 (GATE-CODE-AUDIT-A3-PART1)

| Finding | SAP clause | Status | Evidence |
|---|---|---|---|
| **M-1** `ps_frozen.json` | AD.4 (l.979), AD.12 step 2 (l.1085), A3.3 item 1 (l.1253), AB.8 (l.1194) | **FIXED** | New `exp_p2/gate/ps_freeze.py`: `params()` (l.39-46: grid 32, 1,024 tokens, patch 8, 6.25 percent, `SWAP_FRAC` 0.15, 154 positions, vocab 16,384, `TOKEN_RNG_TAG` 190/191, `SEED_GATE`, condition order, `denoise_for`, alphas), `write` write-once through `artifacts.write_once` (l.63-66; `--force` keeps the old file and logs an amendment), `check` (l.73-89) raises if missing, if any frozen parameter differs from the code, or if the file is not tracked and unmodified in git. `run_gate_m4.py:195-200,201` refuses (exit 2, before the model) without it whenever a PS condition is requested and refuses a `--denoise-for` different from the frozen list; `run_gate_epred_chunk.py:90-93` refuses (exit 2) too, and takes `denoise_for` from the file (l.164). Run `config.json` records `ps_params`, `ps_frozen_sha256`, `ps_frozen_code_commit` (m4 l.204-205; chunk l.212). Tests: `test_gate_ps_freeze.py` (write-once, changed parameter, uncommitted, CLI, both refusals), `test_gate_swap.py` (main returns 2 without the file) |
| **M-2** runtime patch-size assertion | AB.7 item 2 (l.1182), A3.3 item 3 (l.1255) | **FIXED** | `ps_freeze.assert_runtime` (l.92-95) raises `PsGeometryError("STOP: token grid ...")` unless `(grid, patch) == EXPECTED_GEOMETRY`, whose production value is `(config.GRID, config.PATCH)` = (32, 8) (test l.69-75 sets it back explicitly and asserts 32/8). Called in `make_ctx` of M4 (`run_gate_m4.py:100`) and of the chunk (`run_gate_epred_chunk.py:161`) right after the scorer reports `L_I`, before the first item. `tests/exp_p2/conftest.py` sets (4, 2) only for the fake 4 x 4 network; `test_m4_make_ctx_asserts_the_geometry` and `test_the_chunk_asserts_the_geometry_...` show both refuse the fake map under (32, 8). Still not observed on the real network (E0 until the first M4 chunk) |
| m-1 `falsifier["n"]` | A3b.12 rule 6 | **FIXED** | `detect.py:155-158` adds `n_pair` when `min_n` is set; `_n_of` (l.196-197) reads it first; `min_n=None` results unchanged (key absent). Test in `test_gate_m1_partial.py` |
| m-2 pass `min_n=None` when the pool is complete | A3b.12 rule 1 | NOT FIXED (not requested; harmless) | `analyze_gate_m1.py` is not in the delta. Results coincide whenever every candidate has at least 100 finite values; only extra fields appear. Leave, or fix with the next M1 edit |
| m-3 PS wording | AB.1 item 1(a) | **FIXED** | `analysis_m4.py` `ps_family` docstring, `label`, `on_not_met` now carry the AB.1 sentence; the "barred" clause is gone |
| m-4 `descriptive_ps` T1/T2/D fold label, D printed | AD.4 | NOT FIXED (descriptive only) | not in the delta |
| m-5 `--sanity swap` without patch | A3.3 item 1 (condition index) | **FIXED** | `run_gate_m4.parse_sanity` l.85-86 refuses; the chunk reuses it; tests `test_swap_without_patch_is_not_allowed...` and the chunk-index test (patch 6, swap 7) |
| m-6 chunk fit-code hashes vs the freeze | AB.3 item 5 | **FIXED** | `epred.chunk_code_mismatch` and the check in `cmd_fit` (refuses, exit 2, unless `--skip-git-checks`); the chunk runner's hash is recorded in `epred_frozen.json` inputs. The diff of `epred.py` is purely additive; the definitions of o_c, o_c*, A, K_eval, the Clopper-Pearson interval and the rival rules are untouched |
| m-7, m-8, m-9, m-10 | observations | NOT requested | m-8 (commit the P section before reading PS) and m-9 (which refutation flag the paper reports) remain the lead's decisions |
| EPRED-FIT-AUDIT conditions (iii), (iv) | part 1 section 4 | **met** | (iii) M-2 is in the chunk; (iv) m-6 is in `fit`. The chunk runner changed after the part 1 review (blob `f0853fb9` to `452455e9`; LF SHA-256 `c644c094b151178db850bab78154f68d99d3e2f88b0066e50040d859fd226a71`); I read that delta (ps_freeze check, geometry assertion, `denoise_for` from the frozen file, config fields): no defect. The audit record itself and the three frozen files are unchanged |

### Part 2 (GATE-CODE-AUDIT-A3-PART2)

| Finding | SAP clause | Status | Evidence |
|---|---|---|---|
| **M1** S2 wording | A3b.1 items 2-4, A3b.2 items 3-5 | **FIXED** | `analysis_s2.py:196-231`: `kept_draw_rejects` (tested, b > c, Holm p < 0.05) is separate from `location_claim_eligible` (that AND draw-level 95 percent lower bound > 0, l.203); `location_supported` is now only an alias of eligibility (l.209). Refuted if the kept-draw OR the draw-level 95 percent upper bound < 0 (l.205). Sentences are constants: `SENT_ELIGIBLE` (A3b.2 item 3 sentence plus the eligibility clause), `SENT_NO_LOCATION` (A3b.1 item 2, verbatim), `SENT_REFUTED` (A3b.1 item 3), `SENT_NO_EVIDENCE` (A3b.2 item 5). `DISCLOSURE` is the A3b.1 item 4 sentence verbatim, in every cell's `table_note` with the A3b.2 item 4 note and the kept-draw definition; `may_not_claim` per cell. Auditor probe: kept-draw rejection with draw-level difference 0 gives eligible False and the no-location sentence; a clean case gives eligible True |
| **M2** sensitivity at 150, partial-prefix label with MDE | A3.1 items 2-3, A3b.3 item 8, A3b.6 item 5 | **FIXED** | S2: `sensitivity_first150` (l.128-151) on the first 150 planned list items (planned order, not file order), only if completed n >= 150, label "sensitivity (SAP n = 150), not confirmatory, not in the Holm set", b, c, p, CI, MDE, `sensitive_to_n` statement; `partial_prefix` (l.154-161). B: `foil._sensitivity_first150` (l.443) keyed on pool position, tested if overall completed n >= 120, own count printed, label as A3b.3 item 8, "coincides with the primary" when the prefix covers fewer than 150 positions; `_partial_prefix` (l.435). New `mde.py`: I re-ran it, and it reproduces the A3.1 table (n = 300: 0.057 at alpha' 0.025, 0.053 at 0.05; n = 150: 0.079 and 0.074; n = 120: 0.087; n = 240: 0.064; unreachable at pi_d 0.05, n = 150) |
| **M3** `analysis_foil analyze` on not_estimable / untestable_at_ceiling | AD.6 rules (i), (ii); A3.4 item 3; A3b.3 item 5 | **FIXED** | `analysis_foil.py:103-107` branches on `frozen["fit"]["status"] != "ok"` before any test row is read, calls `foil.fusion_b1` with an empty matrix: p = 1, `tested` False, `WORDING_CEILING` (A3.4 item 3 verbatim) or `WORDING_NOT_ESTIMABLE`; stray test rows are ignored and counted. The new tests reproduce the auditor's `FileNotFoundError` on the pre-fix code (IMPL-F, run against `git archive` of f938ceab) |
| **M4** family B wording | A3b.3 items 1, 2, 3, 6, 7 | **FIXED** | `supports_fusion_helps` and "supports 'fusion helps'" are gone (grep over `exp_p2` finds neither); `WORDING_REJECT` (foil.py:403) is the A3b.3 item 6 sentence plus the mix sentence plus the weights sentence; `WORDING_NOT_REJECT` carries the MDE; `B_LIMITS` (l.413) carries the text-only-cue risk, the fit/test mix, the three label-noise statements, the fit-pairs-unjudged statement, no exclusion/reweighting, and the attainable-gain cap with "the sign of any bias on Delta_B is not established". No "up to" in `foil.py` or `analysis_foil.py`. Numbers checked by the engineer against `l7_out.json` and `pool.json` and by a test (`test_the_caveat_numbers_match_the_committed_artifacts`) |
| **M5** S2 smoke firewall | A3.2 item 2, A3b.7 item 4 | **FIXED** (honour rule remains) | `run_gate_s2_smoke.py`: own run id (refuses `P2-GATE-S2`, `P2-GATE-S2-FIG`, `--figures`), the item function is wrapped so only `{"n_rows"}` leaves it and the arrays are dropped; stdout of the real loop is redirected to a sink; the script prints and stores exactly `peak_gb`, `seconds`, `n_rows`. I read the runner: the only other keys a row gets are `idx`, `seconds`, `free_ram_gb`, `peak_gb`; `chunks.jsonl` and `selfcheck.json` hold no Y. Not executed on a GPU by anyone |
| m1 `keep_best` NaN | A3.2 item 1 (c) | **NOT FIXED: required before S2** | section 2, R-m1 |
| m2 "G.1" strings | A3b.2 item 1 | **FIXED** | `COMPARATOR = "random-gate best-of-4 re-infill"` (analysis_s2.py:43), `run_gate_s2.CONFIG["comparator"]` without "G.1-inspired"; grep finds "G.1" only in the rule text of `forbidden_wording`, `SAMPLER_NOTE` and comments |
| m3 suite E-pred block from the CLI | AD.9 | **FIXED** | `suite.analyze_run` (l.248) reads the headroom arrays, calls the audited `epred_fit` and `epred_agreement`; "produced: False" with a reason when no array exists |
| m4 pinned commit at run time | A3b.7 item 1 | **FIXED** | `suite.installed_commit` (l.60) reads `direct_url.json`; `verify_pinned_commit` (l.73) raises `PinnedCommitMismatch` (an `ImportError`, so the runner exits 2); `load_package` calls it; config records the commit read from the metadata |
| m5 I-CHG cut test | A3b.2 item 6 | **FIXED** | `test_minor_m5_the_ichg_cut_leaves_igate_and_irand_bit_identical` |
| m6 prefix rule | SAP 8.1 | **FIXED for S2**, not for B | `analysis_s2.py:175,185-188`: a gap in the prefix makes the cells descriptive (p = 1). B: the exclusion list is not in the rows; the runner writes in list order and stops at the first failure, so a gap cannot arise. Leave |
| m7 leak_check rewrite | pre-GPU evidence | **FIXED** | `run_gate_foil.check_prereqs` writes `runs/<run-id>/leak_check.json`, compares the deterministic part with the committed one and stops (exit 2) on a difference; `foil.py check` writes `leak_check_recheck.json`; `analyze` refuses a changed pool. I re-ran `check_pool` read-only: ok True and `comparable_leak_check` equals the committed file's |
| m8 NaN correlation | - | **FIXED** (guarded in `fit_b1`, None instead of NaN) | foil.py:369-390 |

### Part 3 (GATE-CODE-AUDIT-A3-PART3-OMNI)

| Finding | SAP clause | Status | Evidence |
|---|---|---|---|
| **M-1** `omni_r` wording | A3b.4 items 5, 7, 8, 9 | **FIXED** | `analysis_omni.py:39-62,234-262`: under R3 "the evidence-ratio effect found in P was / was not accompanied by an accuracy change on Omni"; `directional_replication_available` False, `replicated_any` None; a rejection with b < c_cnt sets `refutes_direction` and appends the item 9 sentence; every record carries `confounds` (six items) and `positive_control_wording` (item 5 sentence plus its extension); `forbidden` adds the R3 and "independently verified" rules. R3 and b < c tests exist. Observation, not a defect: when a refutation is present the R1/R2 string still begins "not replicated; inconclusive at this n", which sits oddly beside "refutes the direction"; both phrases are the SAP's (item 9) |
| **M-2** GO rule (b) needs A1..A7 | AD.7 (b) as replaced by AB.5 item 1; A3b.4 item 1 | **FIXED** | `selfcheck_ok` (analysis_omni.py:54-62): `ids_equal`, `adapter.all_ok`, ids exactly A1..A7 once each, all ok; `omni_gate` (b) uses it and T1, and lists `checks_present` / `checks_missing`; `run_gate_omni_r.require_signature` applies it too (l.76-78), so no later stage runs on a failed or partial self-check even with a signature. Auditor probe: A1-A3 only returns False; A1-A7 True; a duplicate A1 False |
| m-1 failed self-check does not stop the next chunk | - | **FIXED** | `runner.py:133-141` (and `selfcheck_passed`, l.71): a failed `selfcheck.json` from an earlier chunk returns exit 2 before the model is loaded and logs `selfcheck_failed_earlier`; same predicate as at write time |
| m-2 / T3 load and check peak not gated | AD.7 (c), A3b.4 item 6 | **FIXED** | `run_omni_timing.py:113-119`: `peak_gate` recorded; above 7,000 MiB `ids_equal` is set False and a `guard_stop` event is appended, so the driver ends with its guard exit and does not relaunch (`gate_driver.py:197-200`) |
| m-3 `_cmd_gate` crash events | - | NOT requested | the run card states the crash-event reading by hand (lead decision 2) |
| m-4 realised quantisation | - | **FIXED** | `build.realised_quantisation`; `selfcheck.json["quantisation"]`; checked by `signing.quantisation_check` |
| m-5 `HF_HUB_OFFLINE` | - | **FIXED** | `gate_driver.STAGE_ENV` assigns `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` in the child environment of the four Omni stages (l.58, 189) |
| m-6, m-7, m-8 | - | NOT requested | prose or interpretation |
| T1, T2, T3 | lead decision 2 | **accepted and implemented** | T1: `signing.t1_check` (floors -8.011 and 0.005 on `per_shift["1"]`, the key layout I read from `checks.py:161`), also required inside `omni_gate` (b). T2: `build.t2_record` in `omni_env.json["t2"]`, read by `signing.t2_check`. T3: above. `checks.py` and the checks file are unchanged (hashes in section 3). Disclosure: A3b.4 item 3 words a tightening as "a dated commit that changes the hashes"; the lead applied T1-T3 outside `checks.py`, so the recorded hashes stand and nothing is loosened. I accept that reading and ask that the deviations box state it |

## 2. Rulings

**D1 `location_supported` kept as an alias that now means eligibility: consistent.** It is stricter than before; no caller can read a kept-draw rejection as a location claim (A3b.1 item 2). The selftest and tests were updated for the stricter meaning.

**D2 "partial prefix" applies when 120 <= completed n < 0.8 x `--n` and the fold is not complete: consistent.** At `--n 300` this is exactly the A3.1 item 2 range, 120 to 239. A completed list of 298 is not "under 80 percent of plan", so labelling it would make the label false; at `--n 150` (A3b.6 item 4) a completed n of 120 to 150 is at least 80 percent of the plan, so the label correctly never appears. The only literal reading that would label a full-plan result is incoherent with the label's own words. The run card must pass the same `--n` to `analysis_s2` as to the run.

**D3 the sensitivity's "rejection" is the favourable-direction rejection at p x m < 0.05 (S2 m = 2, B m = 1): consistent.** The SAP says "opposite sides of rejection" without defining a threshold for a result that is outside the Holm set; the A3.1 table's per-test threshold for S2 is alpha' = 0.025, which is this. It can over-flag "sensitive to n" (the larger-p cell of the primary Holm may reject at p < 0.05 where the sensitivity needs p < 0.025) and never under-flag; it enters no Holm set and no claim. Disclose it once in the run card.

**D4 B sensitivity "covers fewer than 150 positions" means max completed pool position + 1 < 150: consistent with A3b.3 item 8.** In the edge case where position 149 is excluded or unfinished the sensitivity set equals the primary set, so showing it separately would add nothing.

**D5 a kept-draw rejection whose draw-level interval lies wholly below 0 is read as "refuted" and the kept-draw sentence is not emitted: consistent, and required.** A3b.1 item 2 would allow the no-location sentence when the draw-level CI "lies on the other side", but item 3 says that when the draw-level contrast has its 95 percent CI excluding 0 below, "the statement 'repairing the flagged set beats repairing random sets' is not available". The no-location sentence says that repairing the GATE-M set gave higher accuracy, which is the same statement. Item 3 therefore governs, and `kept_draw_rejects` stays visible in the record, so nothing is hidden.

**R-m1 (`keep_best` has no NaN guard, `exp_p2/gate/reinfill.py:102-104`): it must be fixed before the S2 smoke and before the card v4 pin.** My probe shows `keep_best([-3, nan, -1, -1])` returns the NaN draw (`np.argmax` treats NaN as the maximum); the selection rule of A3.2 item 1 (c) is therefore not total, and a silent arbitrary choice inside a preregistered selection rule is not acceptable even if it is improbable (the chain sum is of fp32 log-probabilities of sampled tokens, finite by construction unless the logits themselves are inf or NaN, and `torch.multinomial` raises on NaN probabilities on CPU; the CUDA path is untested). The file is part of the commit A3b.7 item 1 pins, and an edit after the pin or after a first S2 item needs a dated amendment row. The fix is five lines, CPU, and changes no row format.

Required behaviour (and nothing else):
1. In `keep_best(logp)`: convert to float64 as now; if the array is empty, or **any** entry is non-finite (NaN, +inf or -inf), **raise** a dedicated exception (suggest `class NonFiniteChainLikelihood(ValueError)`), naming the offending draw indices. Do not select, do not default to index 0, do not use `np.nanargmax`, do not drop the draw.
2. Otherwise return `int(np.argmax(logp))`, exactly as now: the highest chain log-likelihood, exact ties to the lowest draw index. For every finite input the result must equal the current result, so the PASSED tie rule (KEEP_BEST-CHECK: PASS in part 2) is unchanged; the existing assertions `keep_best([-3,-1,-2,-1]) == 1` and `keep_best([-2,-2,-2,-2]) == 0` stay as they are.
3. Tests: NaN, +inf and -inf each raise; a finite input with ties still returns the lowest index; a property check over random finite arrays compares against the old expression.
4. Consequence, accepted: the exception escapes `process`, the runner records an `item_error` event with the traceback and re-raises (`runner.py:196-198`), the item is not written, and the driver stops after two chunks without progress. This is the intended outcome (the kept-draw statistic is undefined for that item, and SAP 8.1 does not allow skipping it silently); the lead then records a dated decision row. Engineer F's concern that the guard "makes an item un-completable on resume" describes exactly this stop, which is the correct response and which the lead can resolve by a row, whereas silent selection cannot be detected afterwards. `I-GATE-LEAK` (`kept = 0`, no `keep_best` call) is unaffected.

## 3. Frozen files and the E-pred audit record (task 4)

| File | Blob at f938ceab | Blob at HEAD | LF SHA-256 (working tree) | Result |
|---|---|---|---|---|
| `exp_p2/gate/epred_fit.py` | 8685835a9c3b3cfd377ce944c33e37a71ea716ea | same | c89700dbc3ba4da61f4f8ae681a5775d05e54cbbf3a86d05650e4151d5d29abc | identical |
| `exp_p2/gate/theory.py` | 4d2b550016e4563eb3506eaf5ccfda4b6b168748 | same | 5c535a3bda759e0bc3ef7b888b8a773ce2d0cf077c2b515661fda0a9ae00ab46 | identical |
| `tests/exp_p2/test_gate_epred_fit.py` | db2c9db62250ed538aba52262841422046690d68 | same | 8d7528bbb37b9f125f80c37d13baadfcee01f347343910861c6fa355cabad25f | identical |
| `exp_p2/omni/checks.py` | e657b799441457e6f25f4ec453cf796ea37d8544 | same | 9e397f2a3dedcd4a8edf133214d30ed25ee9170ca80a089238435c2217f6c48f (CRLF raw 4e196a1f...a5ee) | identical; matches SAP A3b.4 item 2 |
| `tools/gpu_guard.py` | f3f57623b30922b58fee5131f9f7f627f1534f25 | same | 5ddf7d09f1ea830a6a1049b5958974c342cd37a2817e1063e1dbf797d855aa6d | identical; `pins.gpu_guard_pin()["ok"]` True |
| `research/paper2/method/OMNI-ADAPTER-CHECKS-2026-10-28.md` | c217de65... | same | 9b429e12df9d8aab6b569d83aeace75652eb78ee2d75454b6891d5bf435dbe55 | identical |
| `GATE-CODE-AUDIT-A3-PART1-2026-10-28.md` (the E-pred `--audit-record`) | 4135818076ebf9734616899d118516bffa45eeea at 07f5d56d | same | 26145a2a6b918536a1b5eb13fbb09e0f20241332b57f3505bdd95b158d234c61 | unedited; `git log` shows its single commit 07f5d56d. (`git diff f938ceab HEAD` on it shows 180 insertions only because it was added after f938ceab) |

`FIT_CODE_FILES` in `epred.py` is exactly the first three files, so the changes to `epred.py` (additive, m-6) and to `run_gate_epred_chunk.py` do not touch the frozen fit code. The part 1 audit file must stay unedited: its hash goes into `config.json` and `epred_frozen.json`. This re-audit is a new file and does not replace it as the audit record.

## 4. Guards, exit codes, refusals, write-once (task 5)

I read every removed line of `git diff f938ceab..HEAD -- exp_p2 tools tests`. The removed lines are: superseded wording strings, the old `supports_fusion_helps` key and its tests, the old unconditional leak-check rewrite, the old analysis tail now moved into branches, and tests updated to the new keys and the stricter self-check shape. No guard threshold, exit code, refusal or write-once check is removed or loosened. Additions that tighten: `ps_frozen.json` refusal in M4 and the chunk (exit 2); the geometry assertion; `--sanity swap` without patch refused; `--denoise-for` must equal the frozen list; `epred fit` refuses on a fit-code mismatch (exit 2); a failed earlier self-check refuses before the model loads (exit 2); GO rule (b) needs A1..A7 and T1; `require_signature` re-checks the self-check; load-plus-check peak above 7,000 MiB sets a guard stop (never relaunched); `HF_HUB_OFFLINE=1` assigned for Omni stages; `PinnedCommitMismatch` stops the suite; the FOIL runner stops if the start-up leak check differs from the committed one. `tools/gpu_guard.py`, `pins.py`, `hold.py`, `guards.py`, `watchdog.py` are not in the diff. `ps_frozen.json` is write-once (`artifacts.write_once`; `--force` keeps the old file and logs an amendment). `pins.require_clean(False, label="audit")` at HEAD returns `(True, [])`; `git status --porcelain -- exp_p2 tools` is empty.

## 5. Adapter signature (task 6)

All MAJORs are FIXED, so `runs/P2-OMNI-ADAPTER/adapter_signature.json` is written: audited commit, the checks-file hashes, T1-T3 accepted per the lead decisions, `gpu_checks_pending: true`, `selfcheck_sha256: null`, verdict "CODE-AUDIT PASS (CPU only); GPU adapter checks pending". It is deliberately **not** the signature that `omni_gate` and `run_gate_omni_r.require_signature` read (`runs/P2-OMNI-TIMING/adapter_signature.json`, hash-bound to `selfcheck.json`, written only after the GPU timing stage and my reading of S-1..S-8). Nothing in the code can mistake one for the other. By A3b.4 item 1 no document may say the adapter was "independently verified".

## 6. What the lead must still do (not findings of the code)

1. Fix R-m1 before the S2 smoke and before the card v4 pin; I re-check the diff (ten minutes, CPU).
2. Run sheet: `python -m exp_p2.gate.ps_freeze write` and commit `runs/P2-GATE-M3/ps_frozen.json` after `family.json` and before the fit chunk and the first M4 item (IMPL-E round 3). AD.4 and A3.3 item 1 say the swap parameters go into `ps_frozen.json` **and** `family.json`; `family.json` is written by the headroom stage for the P cells and holds no PS parameters. I read AD.12 step 2 (which names only `ps_frozen.json`) as the binding artifact; if you want the literal reading, add a one-line dated row saying `ps_frozen.json` stands for both.
3. Take the card v4 pin only after R-m1 is committed (A3b.7 item 1) and `pins.require_clean` is re-run; the SHA in this note is the audited one, not the pin.
4. Deviations box: T1-T3 applied outside `checks.py` (section 1, Part 3 row); D3 operational reading; the S2 smoke firewall is an honour rule; adapter checks "executed by the implementer's code and reviewed, not executed, by the auditor".
5. Still pending and unrelated to code: ANONYMIZED's n = 300 row (A3b.6), the M1 closing row and co-attestation, the S2 run card with the sampler specification, `HF_HUB_OFFLINE` is now in the driver but the run card should state it. `research/progress.md` is the lead's file; I did not edit it. The full suite and the five `.venv-omni` tests are the lead's run; I ran 12 targeted files (247 passed).

## 7. Independence

I wrote none of the audited code, changed no file under `exp_p2/`, `tests/`, `tools/` or the frozen files, and opened no item or array of `runs/P2-PROBE-02/`. My only new artifacts are this note, the CPU signature file, and a scratch probe in the session scratchpad (`reaud/probe1.py`, not in the repository).

## 8. m1 re-check (appended after commit 9c4e1e25)

**Verdict: R-m1 FIXED. Final verdict stays PASS (the one required fix of section 2 is closed). Final audited SHA: 9c4e1e25cb0d1a77b78410e1613098d8c6ba1085.**

- Diff 8c9edf8c..9c4e1e25 under `exp_p2/`, `tools/`, `tests/` is two files only: `exp_p2/gate/reinfill.py` (+12/-2) and `tests/exp_p2/test_gate_s2.py` (+8). `git status --porcelain -- exp_p2 tools` is empty. The frozen files of section 3 are not in the diff.
- `keep_best` (reinfill.py): converts to float64, raises `NonFiniteDrawError(ValueError)` if `np.all(np.isfinite(a))` is false (NaN, +inf, -inf each covered by the new test), otherwise returns `int(np.argmax(a))` exactly as before. Finite behaviour and the tie rule (first maximum, lowest index) are unchanged; the existing tie assertions are untouched. It does not use `nanargmax`, does not drop a draw and does not default to 0, as specified.
- Stop path: `run_gate_s2.py:185` calls `keep_best` inside `process`; `runner.py:195` runs `process(sc, it, ctx)` inside a `try`, and `runner.py:196-198` catches `Exception`, appends an `item_error` row (idx, repr, traceback) to `chunks.jsonl` and re-raises. The item row and arrays are written only after `process` returns (l.206-213), so the item is not committed. The prerequisite `try/except (FileNotFoundError, ValueError)` in `run_gate_s2.main` (l.286-313) ends before `run_items`, so the ValueError is not swallowed there; the chunk dies, and the driver, which sees no progress, stops after two such chunks (`gate_driver.py` fails >= 2, exit 5).
- `tests/exp_p2/test_gate_s2.py`: 40 passed (re-run here, CPU).
- Still required of the lead: take the card v4 pin at or after 9c4e1e25 and re-run `pins.require_clean` at the pin.
