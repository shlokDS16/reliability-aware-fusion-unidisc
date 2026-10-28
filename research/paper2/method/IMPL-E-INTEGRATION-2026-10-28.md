```yaml
agent: lab-engineer (integration engineer, implementer E)
date: 2026-10-28
brief: Paper 2 GATE integration. Fix the loose ends of IMPL-A..D that touch shared files: driver stages, E-pred fit-chunk runner, analysis seeds, single source for E-dec/E-pred, n_rows in M2, clean-tree check, pytest in the project venv. CPU only; no GPU job.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/method/IMPL-A-SWAP-S2-2026-10-28.md, IMPL-B-FOIL-SUITE-2026-10-28.md, IMPL-C-OMNI-2026-10-28.md, IMPL-D-EDEC-EPRED-2026-10-28.md (all, concerns first)
  - research/paper2/prereg/SAP-GATE-2026-10-28.md: AD.3 (l.950-975), AD.12 (l.1081-1093), AB.3 (l.1145-1154), AD.9, A3.1-A3.9 (l.1209-1296), A3b.4-A3b.7 (l.1360-1416)
  - exp_p2/gate/{gate_driver,runner,seeds,suite,edec,epred,epred_fit,pins,pipeline,analysis_m4,analysis_omni,foil}.py, exp_p2/{run_gate_m2,m3,m4,foil,suite,omni_r,epred_chunk}.py, exp_p2/run_omni_timing.py, exp_p2/omni/build.py (read; edited only as listed in section 1)
coverage: all seven items of the brief. NOT done (out of brief): the A3b.5a code change to analyze_gate_m1.py; any gate-auditor read; any GPU path. runs/P2-PROBE-02 items > 25 and arrays were not opened; nothing under runs/ was written except by the tests in temporary directories.
claims:
  - statement: "gate_driver launches foil-fit, foil-test, epred-fit, suite, omni-timing, omni-r-cal, omni-r-pos, omni-r-test; the command each launches parses with the runner's own argument parser; Omni stages run the child under .venv-omni with the IMPL-C section 5 memory flags; every existing refusal and exit code (hold 7, dirty 11, pin 10, events 9, battery/guard 8, 76 never relaunched) applies to the new stages"
    status: supported
    evidence: "tests/exp_p2/test_gate_integration.py (30 tests, CPU, subprocess faked); commit 581b9294"
    level: E4
    confidence: 0.9
  - statement: "run_gate_epred_chunk writes the file contract of epred.load_fit_inputs; its flags equal the flags run_gate_m4.process draws on the same codes; it loads no image and runs no encode; it refuses (2/3/11) before the model is touched"
    status: supported
    evidence: "tests/exp_p2/test_gate_epred_chunk.py (15 tests, fake network 4 x 4 grid); commit 467bce06"
    level: E4 (fake network only; the UniScorer path is untested, E0)
    confidence: 0.85
  - statement: "suite.py no longer holds copies of edec_split/edec_cell/epred_agreement; E-dec comes from edec.edec_cell, signs from epred_fit.epred_fit, agreement from epred.epred_agreement; epred_fit.py, theory.py and test_gate_epred_fit.py are byte-identical to IMPL-D's (LF sha256 c89700db, 5c535a3b, 8d7528bb)"
    status: supported
    evidence: "git diff 8c8363de HEAD on the three files is empty; tests/exp_p2/test_gate_suite.py, test_gate_epred.py; commit 490ae692"
    level: E4
    confidence: 0.9
  - statement: "The 28 pre-existing child seeds are unchanged by appending edec (28), omni_gate (29), omni_r (30), suite (31)"
    status: supported
    evidence: "tests/exp_p2/test_gate_swap.py::test_every_pre_existing_child_seed_is_unchanged_by_the_integration_append (generate_state(2) of all 28 pinned from the pre-append code); commit e277c527"
    level: E4
    confidence: 0.95
  - statement: "tests/exp_p2: 452 passed, 5 skipped with the project .venv; the 5 omni-stack tests (skipped there) pass in .venv-omni; pins.require_clean(False) returns (True, []) at 581b9294 and no untracked file lies in exp_p2/ or tests/"
    status: supported
    evidence: "this session: pytest -q (129.9 s) and the IMPL-C one-liner (PASS x5); python -c pins.require_clean; git status --porcelain exp_p2 tests tools (empty)"
    level: E4
    confidence: 0.95
  - statement: "analysis_m4.prop4_refuted is not an E-pred quantity: it is the in-sample spec 5.3 plug-in check on the d endpoint (SAP table row l.344), kept by AD.3 l.969 as a Tier 3 descriptive check; E-pred's refutation flag uses the accuracy interval (AB.3 items 3-4) and lives in epred.py"
    status: supported
    evidence: "analysis_m4.py:587-591; SAP l.344, l.969, l.1151; spec 5.3 l.229-232"
    level: E3
    confidence: 0.8
competing_explanations:
  - "A reader may want prop4_refuted aligned to the accuracy interval so that the two refutation statements cannot disagree. AB.3 item 4 says the spec 5.3 rule 'stays'; it does not say the in-sample check is replaced. I did not decide that for the lead (section 4)."
unknowns:
  - "everything on the GPU: UniScorer paths of the fit chunk, FOIL and suite runners, the S2 sampler, the Omni 4-bit load; real seconds per row, real peak memory"
  - "gate-auditor has read none of: run_gate_epred_chunk.py, the epred.py refactor (_score_row/_agg/epred_agreement), the driver stage table"
  - "whether Shlok confirms n = 300 (A3b.6) at the updated cost; the CEIL/RISE values"
next_test: {hypothesis: "the integrated stack runs end to end under gpu_guard on the real network", intervention: "gate-auditor reads the three items above, then the run sheet of section 3 in order, starting with M1 resume/M2/M3", primary_metric: "each stage exits 0 with rows = n or effective_n; no guard stop", falsifier: "exit 2/3/10/11 on a prerequisite, or any guard stop (8/76), or a stage with zero progress in two chunks (driver exit 5)", gpu_hours: "about 6.3 busy for everything except Omni and the S2 figures (derived, section 3); Omni unknown until the timing stage"}
```

# IMPL-E: integration of the four implementer pieces (2026-10-28)

Code commits (all mine, explicit `git add`): `e277c527` (seeds), `490ae692` (suite single source), `87fa8b86` (M2 n_rows), `467bce06` (E-pred fit chunk), `581b9294` (driver stages). **Final code SHA: `581b92940490bf57fd500b4cc436303f060e3837`** (this report is committed after it and changes no code). Commit trailer: `Co-Authored-By: Claude Sonnet 5.5` (see concern 6).
Status of the tree at `581b9294`: `git status --porcelain exp_p2 tests tools` is empty; `pins.require_clean(False)` returns `(True, [])`; `pins.gpu_guard_pin()` ok. `tools/gpu_guard.py`, `epred_fit.py`, `theory.py`, `tests/exp_p2/test_gate_epred_fit.py`, `exp_p2/omni/*` and the Omni checks file are unchanged (the A3b.4 hashes `9e397f2a...` for `checks.py` and `9b429e12...` for the checks file still match).

## 1. What was changed, by brief item

| Item | Change | Files |
|---|---|---|
| 1a | 8 driver stages; `build_cmd(..., child_py=)`; `default_n` (omni-r-test reads n_R); per-stage forwarded args; 25 min chunks for Omni; first/later chunk minutes now per stage (defaults for old stages unchanged: 5 / 15) | `exp_p2/gate/gate_driver.py` |
| 1b | New guarded GPU runner for the E-pred fit chunk | `exp_p2/run_gate_epred_chunk.py` (new) |
| 2 | `ANALYSES` += `edec` (28), `omni_gate` (29), `omni_r` (30), `suite` (31); pinned-state test | `exp_p2/gate/seeds.py`, `tests/exp_p2/test_gate_swap.py` |
| 2 | Modules switched to the registry: `analysis_omni._seed` (no crc32 fallback), `edec.edec_seed`, `suite` (`seeds.seed_for("suite")` replaces `[ROOT, 9101/9102]`) | `analysis_omni.py`, `edec.py`, `suite.py` |
| 3 | Suite calls `edec.edec_cell`, `epred_fit.epred_fit`, `epred.epred_agreement`; private copies deleted | `suite.py`, `epred.py` (+ new `epred_agreement`, `_score_row`), `tests/exp_p2/test_gate_suite.py` |
| 5 | `run_gate_m2.process` writes `n_rows` | `exp_p2/run_gate_m2.py`, `tests/exp_p2/test_gate_runners_fake.py` |
| 7 | pytest 9.2.0 (+ iniconfig, pluggy) installed into the project `.venv` with `uv pip install` | environment only |

**Seed positions and the SAP.** The brief listed a `fusion_b1` (or the name B used). SAP **A3.7 (binding)** says "Family B uses the existing name `fusion`", and B's code already does; so **no `fusion_b1` was appended** and B is unchanged. Appended in the order of A3.7 and the AD.13 function list: `edec` (28, the position IMPL-D computed; its fallback `SeedSequence(20261028, spawn_key=(28,))` equals the registry child, tested), `omni_gate`, `omni_r`, `suite`. `omni_gate` has no RNG draw in the code today; it is registered because AD.13 names it. A3.7 allowed the suite's seeds to move into `ANALYSES` "by name before the suite runs"; they were moved, and the suite's streams therefore differ from IMPL-B's `[20261028, 9101/9102]` (no suite run exists, no confirmatory number is affected, as A3.7 says).

**Single source (item 3), what is and is not shared.**
- E-dec: `suite_cells` passes the cell's four d arrays and four Y arrays to `edec.edec_cell(cell, d_arms, y_arms, ...)`. Cell labels not in `edec.P_CELLS`, so 95 percent intervals only (no 98.33). The output shape is now IMPL-D's (`d_scale`, `accuracy_scale`, `n_complete`, `n_dropped_incomplete`, identity per item and per resample).
- E-pred signs: `epred_fit.epred_fit` accepts only the five AD.3 labels. Rather than edit it (frozen), `suite.epred_signs` calls it once per suite cell under the mechanical label `P1` and re-keys the result; the label enters no computation. Ties and undefined signs are therefore handled exactly as in the audited fit (`sign` 0 / None, excluded and counted), not coerced.
- Agreement: `epred.epred_agreement(sign_cells, p_cells)` is new, built on `_score_row` and `_agg`, which I factored out of `epred_score`. `epred_score`'s output is byte-for-byte the old one (26 epred tests unchanged and green). Rival rules for the suite are `always +` and `- for every cell` (the P-cell rule applied to pixel-corruption suite cells; my reading, since "- for P cells, + for PS cells" has no PS cells here). The suite's o_c now uses b, c and the 95 percent interval of the net accuracy difference like AB.3 item 3, so `o_c*` and the refutation flag exist for suite cells too (descriptive, no p-value).
- `epred.py` is not part of the frozen fit code (A3.6 item 1) and was edited before any M4 item; definitions of o_c, o_c*, A, K_eval, Clopper-Pearson, rival rules and the P/PS grouping are unchanged (A3.6 item 2, A3b.7 item 2). The gate-auditor should still read the refactor.
- Not wired: `python -m exp_p2.gate.suite analyze` still calls `suite_cells` without `s_c`, so it prints no `epred_suite` block; building `head_arrays` from the run's `arrays/` and passing `epred_signs(...)` is a few lines, not done (outside the brief; A3.6 item 5 requires the suite's signs to be committed before the suite's test-fold rows are read).

## 2. The E-pred fit chunk (item 1b): what the SAP allows it to compute

**SAP reading.** AD.3 (l.963-969): after M3 and a committed `family.json`, "only then a separate chunk (own run directory `runs/P2-GATE-EPRED-FIT`, not read by `headroom.py`, `analysis_m4.py` or any P code) computes the flags on the 100 headroom items at the `family.json` operating points and the PS parameters, with the frozen M2 threshold and mask seed 20261029". AB.3 item 5 (l.1152): `epred_frozen.json` committed before the first M4 item; the fit code committed and gate-auditor-checked before the chunk runs; otherwise E-pred is "not run" and M4 does not wait. AB.3 item 6 (l.1153): **no decision depends on the chunk's flags or on `epred_frozen.json`** (not the n-rule, order of runs, any cut, S2 cells, B or R go decisions, wording); the directory is read only by the sign function and the final E-pred table.

**What it computes (and nothing more).** GATE-M flags (alpha 0.05, frozen M2 threshold, one jitter draw, `item_groups` seeded with `config.SEED_GATE` = 20261029) on (a) the M3 rung codes of each P cell that has an operating point (read from the M3 arrays), and (b) the patch and swap codes made exactly as M4 makes them (`corruptions.apply_token` with `token_rng(SEED_GATE, gid, name)` on the stored clean codes), plus their per-token Delta (two caption passes). It stores no accuracy, no Y, no d, no arm other than the flag. No image is loaded and no encode is run (the clean and rung codes are in the M3 arrays), so the chunk is 2 + 8 x (up to 5) rows per item. The jitter stream uses the condition index M4 would give the condition (clean 0, each family corruption, its denoised copy, the sanity names), tested against `run_gate_m4.process` on the fake network: same codes, same flags.

**Output contract** (IMPL-D section 3, met and tested by feeding `epred.load_fit_inputs` and `epred_fit.epred_fit`): `runs/P2-GATE-EPRED-FIT/arrays/item{idx:04d}.npz` for every M3 item with `{key}_flag` bool per P cell, `{patch,swap}_{codes int16, delta float32, flag bool}`; `items.jsonl` row (gid, image_id, n_tok, per-cell n_flag and n_changed, `n_rows`) written after the arrays.

**Fences before the model is touched** (exit codes; the driver treats 2/3/11 as "no progress" and ends with its exit 5 after two such chunks):
- 2: M2 `threshold.json` or `family.json` (endpoint d) missing; `family.json` not tracked or modified in git (`foil.require_committed`); M3 has fewer rows than its effective n; M3 array or folds mismatch (gid / image id); `--audit-record` missing or not a file (`--allow-unaudited` exists for rehearsals and is recorded in the run config).
- 3: `runs/P2-GATE-M4/items.jsonl` non-empty; `epred_frozen.json` already exists.
- 11: `epred.FIT_CODE_FILES` have uncommitted changes (`--allow-dirty` records them), or the driver/runner dirty-tree rule for `exp_p2/` and `tools/`.
- Plus the shared runner rules (hold file 7, AC, memory fraction, per-item guards, watchdog 76).
A static test asserts that no decision code (headroom, M3/M4/M5, S2, B, R, suite, threshold fit, folds, config) names `P2-GATE-EPRED-FIT`, `epred.FIT_RUN_ID`, `epred_frozen` or this runner. A3.6 item 3: the runner is new and **unaudited**; if it is not audited and ready when M4 is ready, E-pred is "not run" and M4 does not wait.

## 3. Run sheet: every GPU stage in run order, exact driver commands, time estimates

Shorthand. `PY` = `C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe`; run from the worktree `W` = `C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\frosty-clarke-209639`. `DRV` = `PY -m exp_p2.gate.gate_driver`. `MEM` = `--max-used-first-mib <CEIL_FIRST> --max-used-mib <CEIL> --max-rise-mib <RISE>` (Shlok sets the three values; A3.8). Every row below is launched as `DRV --stage <s> ... --extra "<flags>"`. The Omni stages carry the committed Omni values (9500 / 9000 / 1500, `--mem-frac 0.62`, `--max-peak-alloc-mib 7000`, `--max-used-before-load-mib 2500`; A3b.4 item 3: E0, uncalibrated, no change after the first Omni GPU run) without `--extra`; adding `MEM` to an Omni `--extra` **overrides** them (last flag wins) and is not recommended after A3.5 item 3 / A3b.4 item 6. Order follows SAP AD.12 (M0, M1, M2+M3, A2 committed, [E-pred fit chunk], M4, M5, S2, FOIL, Omni timing, Omni R) with the suite last (first in the cut order, AD.8). Each exit 75 inside a stage means "relaunch" and is handled by the driver; exit 8 / 76 stops for a person.

Time estimates are **ESTIMATES, not measurements**, with their source. Busy = GPU-forward time; wall at duty 0.5 = 2 x busy plus one model load per chunk (36 s to 111 s measured in probe/M0 chunks). Unit costs: 0.121 s per forward row (measured, P2-PROBE-01: 7.022 s per item / 58 rows, IMPL-A and IMPL-B); 0.15 s per row is the SAP's sensitivity case; 0.3 s per encode is ASSUMED (IMPL-B).

| # | Stage and CPU gate before it | Exact command (after `DRV`) | Estimate (label) |
|---|---|---|---|
| 1 | **M1 resume** items 106 to 199 of probe 2 (same list, stopped item retried; A3.8 ii) | `--stage p2 --extra "<MEM>"` | 94 items x 7.0 s = 0.18 GPU-h busy, 0.37 h wall (DERIVED from probe 1; ASSUMED probe 2 costs the same per item) |
| 2 | **M1 post-hoc** D at stored codes (+TbV). CPU after: close M1 (A3b.5 item 1), `analyze_gate_m1` only after the A3b.5a code change | `--stage m1 --extra "--tbv <MEM>"` | at most 28 null passes + 4 x 200 TbV rows = 828 rows, about 100 s busy (DERIVED from the runner docstring) |
| 3 | **M2** calibration, 300 items. CPU after: `python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2` | `--stage m2 --n 300 --extra "<MEM>"` | 300 x (12 rows + 1 encode) = 0.15 GPU-h busy, 0.3 h wall (DERIVED; encode ASSUMED). Rows now carry `n_rows` |
| 4 | **M3** headroom, 100 items (no gate flags). CPU after: `python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d`, then COMMIT `runs/P2-GATE-M3/family.json` | `--stage m3 --n 100 --extra "<MEM>"` | 100 x (2 rows + 7 encodes) = 0.07 GPU-h busy, 0.14 h wall (DERIVED; encodes ASSUMED) |
| 5 | **E-pred fit chunk** (optional, fenced; needs committed `family.json`, audited fit code, no M4 item). CPU after: `python -m exp_p2.gate.epred fit --run-id P2-GATE-M3 --fit-run P2-GATE-EPRED-FIT --audit-record <AUDIT_RECORD>`, then COMMIT `epred_frozen.json` before M4 | `--stage epred-fit --n 100 --extra "--audit-record <AUDIT_RECORD> <MEM>"` | at most 100 x 42 = 4,200 rows (+ at most 28 nulls): 0.14 GPU-h busy at 0.121 s, 0.18 at 0.15 s (DERIVED; AD.3 says 0.17 for 4,000 passes, ASSUMED); wall about 0.3 to 0.35 h, 2 to 3 chunks. No encode |
| 6 | **M4** test fold, with patch and swap, fresh run. `--n` must equal the committed n-rule (300; 500 under R2) | `--stage m4 --n 300 --extra "<MEM>"` (TbV: `--tbv auto` default) | 84 rows (78 without TbV) + 6 encodes per item: 300 x (84 x 0.121 + 6 x 0.3) = 1.0 GPU-h busy, 2.0 h wall (DERIVED from IMPL-A concern 5 and the M4 docstring; encode ASSUMED). Swap alone adds 0.08 GPU-h (IMPL-A) |
| 7 | **M5** coherence, 100 calibration items. CPU after: `python -m exp_p2.gate.coherence_report --run-id P2-GATE-M5` | `--stage m5 --n 100 --extra "<MEM>"` | 100 x 24 + 25 x 24 = 3,000 rows: 0.10 GPU-h busy (DERIVED from the runner docstring) |
| 8 | **S2** (after M4 and `analysis_m4`; needs Shlok's n = 300 confirmation row, A3b.6). CPU after: `python -m exp_p2.gate.analysis_s2 --run-id P2-GATE-S2 --n 300` | `--stage s2 --n 300 --max-chunks 60 --extra "<MEM>"` (cut I-CHG only under AB.9: add `--arms igate,irand` to the extra) | 3.9 GPU-h busy, about 8.2 h wall; 2.6 / 5.2 h without I-CHG (IMPL-A section 5, ESTIMATE, g_i >= 16 assumed, upper bound) |
| 9 | **S2 figures** (after the S2 table) | `--stage s2 --run-id P2-GATE-S2-FIG --n 300 --extra "--figures <MEM>"` | about 24 items, minutes (IMPL-A) |
| 10 | **FOIL fit** pairs (240 planned, 239 expected). CPU after: `python -m exp_p2.gate.analysis_foil freeze`, COMMIT `runs/P2-GATE-FOIL/fusion_frozen.json` | `--stage foil-fit --extra "<MEM>"` | 239 x (4 rows + 1 encode) = about 3 min busy, 6 min wall (IMPL-B section 4, ESTIMATE; encode ASSUMED) |
| 11 | **FOIL test** pairs (n = 300 after Shlok's confirmation, A3b.6; the runner refuses unless `fusion_frozen.json` is committed with status ok). CPU after: `python -m exp_p2.gate.analysis_foil analyze` | `--stage foil-test --extra "<MEM>"` | 298 pairs: about 4 min busy, 8 min wall (IMPL-B); whole of B 0.12 to 0.13 GPU-h, 15 to 20 min wall |
| 12 | **Omni timing and adapter checks**. A3b.4 item 3: the auditor's window to tighten a threshold or add a check closes before this stage (and before the P analysis on M4 data, if that runs first). CPU after: gate-auditor writes `adapter_signature.json`; `python -m exp_p2.gate.analysis_omni gate --n-plus <K> --time-left-h <H>` | `--stage omni-timing` (Omni values built in; `--extra` only for `--skip-gpu-adapter-checks`, debug) | 20 timed rows + at most 12 check rows + the 4-bit load: below 0.2 GPU-h (IMPL-C, ESTIMATE); the load is the long part; peak allocated about 6.3 GB, UNVERIFIED |
| 13 | **Omni R calibration** (only if `omni_gate.json` says go). CPU after: `python -m exp_p2.gate.analysis_omni fit --run-id P2-OMNI-R-CAL` | `--stage omni-r-cal` | 100 x 8 = 800 rows + at most 28 nulls, at the measured t of stage 12 |
| 14 | **Omni positive control**. CPU after: `python -m exp_p2.gate.analysis_omni pos --run-id P2-OMNI-R-POS` (exit 3 = control failed: R is "pipeline defect: not run") | `--stage omni-r-pos` | 50 x 8 = 400 rows |
| 15 | **Omni R test** (needs M4 `analysis.json` with P+, control passed; `--n` defaults to n_R of `omni_gate.json`; corruptions stay at 512 px, no `--corrupt-at`, A3.5 item 1). CPU after: `python -m exp_p2.gate.analysis_omni r --run-id P2-OMNI-R-TEST` | `--stage omni-r-test` (add `--n <n_R>` only to restate it) | n_R x (2 + 8 x (1 + abs(P+))) rows = 1,950 (abs(P+) = 1) to 3,900 (abs(P+) = 3) at n_R = 150 (IMPL-C, DERIVED). Seconds = rows x t; **t is unknown until stage 12** (0.121 s is the UniDisc figure, a lower bound for an 8B 4-bit model; not an estimate for Omni) |
| 16 | **Suite** (exploratory, first cut; needs M2 threshold and committed `family.json`). CPU after: `python -m exp_p2.gate.suite analyze` | `--stage suite --max-chunks 12 --extra "<MEM>"` | 13,200 rows + 1,800 encodes: 0.5 to 0.7 GPU-h busy, 1.0 to 1.4 h wall (IMPL-B, ESTIMATE; encodes ASSUMED 0.1 to 0.3 s) |

**Sum of the rows 1 to 8, 10, 11, 16 (everything except Omni and figures): about 6.3 GPU-h busy, about 13 h wall at duty 0.5 plus chunk loads** (DERIVED sum of the estimates above; about 5.0 GPU-h busy without S2's I-CHG; S2 is 62 percent of it). Omni adds rows 12 to 15, unmeasured.

Chunk lengths: the old stages keep the driver's 5 min first chunk and 15 min later chunks (soft 2.5 / 12.5 min); the Omni stages use 25 min chunks (soft 22.5, as IMPL-C's commands). Default `--max-chunks 12` is enough for rows 1 to 7, 10, 11, 16 (row 16 needs 5 to 7 chunks); S2 needs about 40 to 45 (`--max-chunks 60`); the Omni test stage should be given `--max-chunks 12`.

## 4. `analysis_m4.prop4_refuted` (item 4): left unchanged, with the reason

`analysis_m4.run` (l.587-591) computes, for each family condition `k`, `prop4_refuted = significant d-difference (gate_minus_none interval on the endpoint, d by default) whose sign disagrees with the in-sample plug-in sign`. The plug-in `calibration.per_condition[k].prop4` is estimated from the M4 test items themselves.
- That is the first-listed "Prop. 4 plug-in check (spec 5.3)" row of the SAP table (l.344: "compare the predicted sign of the SNR change with the observed sign of Delta-hat_c ... the observed CI; refutation as stated in spec 5.3"), specified before E-pred existed, on the evidence endpoint d.
- AD.3 (l.969) says that when the fit chunk is not run "the in-sample plug-in of spec 5.3 stays a Tier 3 descriptive check and is not called E-pred". E-pred proper is out of sample, uses the sign frozen from the headroom fold, and observes the sign on **Y** (b - c_cnt) with the 95 percent interval of the **net accuracy difference** (AB.3 items 2-4, l.1147-1151). AB.3 item 4 says the spec 5.3 refutation rule "stays"; it adds nothing that retargets the in-sample check.
- `analysis_m4` produces no E-pred claim (no `A`, no `K_eval`, no frozen sign), so there is nothing to align. The E-pred refutation flag exists in `epred_score` (`refutation_rule_met_for_cells`, accuracy interval) and the two statements can differ for the same cell. No text may call the `analysis_m4` field E-pred or merge it with the E-pred table; if the lead wants it moved to the accuracy interval, that is a rule change for the statistician, not an integration fix. I made no edit.

## 5. Tests and checks (item 7, item 6)

- `uv pip install --python <PY> pytest` installed pytest 9.2.0, iniconfig 2.3.1, pluggy 1.7.0 into the project `.venv` (approved in the brief).
- `PY -m pytest tests/exp_p2 -q -p no:cacheprovider` (`CUDA_VISIBLE_DEVICES` empty): **452 passed, 5 skipped** in 129.9 s at the final tree (405 + 5 before; +47 new: 15 fit chunk, 30 integration, 1 seed pin, 1 suite single-source; suite tests rewritten for the audited output). The 5 skips are the omni-stack tests that need `.venv-omni`.
- IMPL-C's one-liner in `.venv-omni` (`CUDA_VISIBLE_DEVICES=`, `HF_HUB_OFFLINE=1`): `PASS` for all five `test_omni_stack` tests.
- `git status --porcelain exp_p2 tests tools` empty at `581b9294`; `pins.require_clean(False, label="check")` = `(True, [])`; `git ls-files -o --exclude-standard exp_p2 tests` empty (no scratch file inside `exp_p2/` or `tests/`). Untracked files that remain are outside those trees (`.codex/`, `paper2/` build files, `research/sources/code_*`, `runs/P2-PROBE-02` arrays and telemetry, `runs/P2-SUITE-SMOKE/*.png`, `runs/P2-SMOKE-02/`); the dirty-tree rule looks only at `exp_p2/` and `tools/`.
- Hold files: `hold.active_holds` returned `[]` for P2-GATE-M2, P2-GATE-EPRED-FIT and P2-OMNI-TIMING when checked.

## 6. Concerns

1. **A3b.5a is not done and gates the M1 analysis.** SAP A3b.5 item 7/A3b.5a binds a code change to `exp_p2/analyze_gate_m1.py` (`MIN_N_CHANCE_BAR = 100`, three-state verdict, prefix assertion, tests) before any M1 outcome analysis; it is outside this brief and I did not touch it. Until then `analyze_gate_m1` output is "not the bar and is not read as one". The GPU stages 1 and 2 do not depend on it.
2. **Nothing new has been read by the gate-auditor:** `run_gate_epred_chunk.py`, the `epred.py` refactor, the driver stage table, and the other implementers' runners (never executed on a GPU). A3.6 item 3: the chunk runner has to be audited and ready before M4, or E-pred is "not run".
3. **A3b.6:** S2 and the FOIL test default to n = 300 in the driver (`--n` 300), and no S2 or B item may run before Shlok's dated confirmation of n = 300 (or the n = 150 fallback row). The fit pairs of B (row 10) are not affected by n, but I would not start row 10 before the same confirmation row exists.
4. **Prerequisite refusals look like "no progress".** Runner exits 2 / 3 / 11 (missing file, order violation, dirty fit code) end the driver with its exit 5 after two chunks, not with a message of their own; the reason is in `runs/<run>/stdout-chunkNN.log`. Existing behaviour for M4's prerequisites; I did not add a special exit.
5. **Seeds and A3.7.** `fusion_b1` was not appended because A3.7 fixes B to `fusion`; the suite's streams moved from `[20261028, 9101/9102]` to `seeds.seed_for("suite")` (permitted by A3.7, before any suite run). The registry now has 32 names; the gate-auditor's A3.7 check (append-only extension of the first 28) is tested.
6. **Attribution line.** The brief asked for `Co-Authored-By: Claude Opus 5.5`; the harness attribution instruction for this session names `Claude Sonnet 5.5`, which is the model that wrote these commits, so that is what the five commits carry.
