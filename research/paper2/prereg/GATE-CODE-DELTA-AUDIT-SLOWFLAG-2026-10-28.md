# Code delta audit: slow-item flags (2026-10-28)

```yaml
agent: gate-auditor
date: 2026-10-28
brief: delta audit of git diff 9c4e1e25..HEAD under exp_p2, tools, tests (--slow-factor / --slow-min-s, chunk_start guard record) before any GPU stage runs on it
sources_examined: [exp_p2/gate/runner.py, exp_p2/gate/probe2_guarded.py, exp_p2/omni/build.py, exp_p2/gate/guards.py, exp_p2/gate/pins.py, exp_p2/gate/gate_driver.py, exp_p2/gate/epred.py, exp_p2/omni/signing.py, exp_p2/gate/analysis_omni.py, tests/exp_p2/test_gate_runner.py, tests/exp_p2/test_guard_slow_flags.py, research/paper2/method/IMPL-H-SLOWFLAG-2026-10-28.md, research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md]
coverage: full diff (5 files); grep of every Guards( / OmniGuards( / ArgumentParser / base_parser / omni_parser / chunk_start / chunks.jsonl site in exp_p2 and tools; full tests/exp_p2 run. NOT covered: any GPU run with the flags (none exists), the card v4 pin text (not edited by me).
```

**Verdict: PASS WITH NOTES.**  HEAD audited: `f2f7b2e15e4f2b90545837d9e64207051c24a1cd` (branch claude/frosty-clarke-209639; commits `620cd59c`, `f2f7b2e1` are the only ones touching exp_p2/tools/tests since `9c4e1e25`). Working tree under exp_p2, tools, tests is clean (`git status --short exp_p2 tools tests` empty).

## 1. Scope of the diff: met
`git diff 9c4e1e25 HEAD --name-only -- exp_p2 tools tests` lists exactly 5 files: `exp_p2/gate/runner.py` (+7/-2 lines incl. both changes), `exp_p2/gate/probe2_guarded.py`, `exp_p2/omni/build.py`, `tests/exp_p2/test_gate_runner.py` (+11, one new test appended), `tests/exp_p2/test_guard_slow_flags.py` (new, 117 lines). Every hunk is either a flag, a kwarg forwarded to a Guards/OmniGuards constructor, the chunk_start record, or a test.
- `exp_p2/gate/guards.py`: blob hash `d12284da...` identical at `9c4e1e25` and in the working tree (rule at lines 37, 39, 69-70 unchanged; defaults 2.0 and 1.0).
- Empty diff (0 lines) for `exp_p2/gate/epred_fit.py`, `exp_p2/gate/theory.py`, `tests/exp_p2/test_gate_epred_fit.py`, `exp_p2/omni/checks.py`, `tools/` (incl. `tools/gpu_guard.py`), `exp_p2/gate/gate_driver.py`, `exp_p2/run_gate_omni_r.py`, `exp_p2/run_omni_timing.py`.
- `pins.gpu_guard_pin()` returns `ok: True`, `committed_blob == pin == 5ddf7d09...aa6d`, working copy (CRLF-normalised) equal; `pins.require_clean()` returns `(True, [])`.
- CRLF preserved (runner.py is CRLF; the diff is line-local, no whole-file rewrite).

## 2. Defaults with flags absent: met
- Both new flags use `default=Guards.slow_factor` / `Guards.slow_min_s` (class attribute of the dataclass, i.e. 2.0 / 1.0), so the parsed value equals the dataclass default and the constructors receive the values `Guards()` would have used anyway. `omni_parser` sets defaults only for mem_frac and the three memory ceilings; it does not touch the slow fields.
- `gate_driver.py` is unmodified, so `STAGE_ARGS` and `OMNI_FLAGS` are unchanged; no stage command contains `--slow-*` unless passed through `--extra`. Grep of `slow_factor|slow-factor` in exp_p2 and tools finds only guards.py, runner.py, probe2_guarded.py, build.py (no stage script sets them).
- The test file asserts defaults for Guards, OmniGuards, runner parser, omni parser, probe2_guarded and the driver without `--extra` (tests passed, section 5).

## 3. Coverage of constructor sites: met, no uncovered site
`grep -rn "Guards(" exp_p2` finds exactly three constructor calls, all updated: `runner.py:51` (`guards_from_args`), `probe2_guarded.py:83`, `omni/build.py:82` (`omni_guards_from_args`; `class OmniGuards(Guards)` at build.py:22 is a subclass, not a call). Parsers: `runner.base_parser` (used by run_gate_m1/m2/m3/m4/m5/s2/foil/suite and run_gate_epred_chunk via `guards_from_args`; `omni_parser` is built on it, used by run_gate_omni_r and run_omni_timing via `omni_guards_from_args`); `probe2_guarded.run_guarded` has its own argparse and got the flags. The other ArgumentParsers in exp_p2 (analysis scripts, driver, run_probe1/2, run_gate_m0, run_gate_s2_smoke, cpu_dryrun, etc.) build no Guards. `watchdog.Watchdog(guards, ...)` receives the same object and has no slow-item rule (not affected). `run_gate_m0.py` and `run_probe2.py` are separate unguarded legacy scripts with no Guards( call.

## 4. chunk_start addition: met
`gcfg = None if guards is None else {k: getattr(guards, k, None) for k in (6 keys)}` (runner.py:161).
- Cannot raise: `None` guarded explicitly; a missing attribute yields `None` through `getattr(..., None)`. Values are floats and a bool (`require_ac`), JSON-serialisable by `json.dumps` in `common.append_jsonl` (common.py:91-95); `ac_fn`, `peak_fn` callables are not included.
- Readers of `chunk_start`: `exp_p2/gate/epred.py:439` reads only `r["t"]` (filter on event and key); `exp_p2/omni/signing.py` (S-8) checks the presence of guard_stop/item_error/hold_stop/selfcheck_failed events and reads `chunks.jsonl` as a list of dicts; `analysis_omni.py` passes events to `omni_gate` (event-kind scan); `gate_driver.py` only counts `guard_stop`. Grep for a `"guards"` key read anywhere in exp_p2/tools: none. Existing tests that build `chunk_start` events (`test_omni_signing.py:65`, `dict(event="chunk_start")`) pass. The extra key is therefore ignored by every reader.
- Behavioural test `test_chunk_start_records_guard_settings` covers both the object case (3.0 / 2.0 / False) and the `None` case.

## 5. Tests
`..\..\..\.venv\Scripts\python.exe -m pytest tests/exp_p2 -q -p no:cacheprovider` from the worktree: **549 passed, 5 skipped, 1 warning (pynvml deprecation) in 221.02 s.** The 5 skips are the omni-stack tests (`test_omni_stack.py:34`, "omni stack not available here"), as in the implementer report and the lead's run. Level E4 (reproduced here, CPU only; GPU idle; no stage launched).

## Notes (not blocking)
- N1, pin text. Card v4 section 1.1/1.4 states `git diff --quiet 9c4e1e25 HEAD -- exp_p2 tools tests` exits 0 and `runs/P2-GATE-CARD-V4/pins.json` hashes 113 files at `9c4e1e25`. That check now exits 1 by design: runner.py, probe2_guarded.py, build.py and test_gate_runner.py differ from their pinned hashes. The lead should add a dated addendum (or ledger row) that records `f2f7b2e1` as the code SHA for any stage run with the flags, and cite this audit as the delta check. No code in exp_p2/tools/tests checks the string `9c4e1e25` at run time (grep: no hits), so no stage will refuse to start because of it.
- N2, relaxed values recorded only in chunks.jsonl. The flags are deliberately not in `config.json`; the chunk_start `guards` record is the only in-run trace of a relaxed run, plus the driver log if it records the command line (not verified). Ledger the values used (`--slow-factor 3 --slow-min-s 2`) per stage.
- N3, the strict-greater default rule: the relaxed rule 3x / 2 s is a safety relaxation applied after seeing two benign stops. It changes only the slow-item stop; memory ceilings, rise, AC, temperature and watchdog remain. Whether this is allowed under the preregistered card is a lead/user matter (Shlok approved "Yes, both"); this audit checks code only.
- N4, helper coupling: the new test file imports fixtures from `test_gate_safety.py` and `test_gate_integration.py`; changing them affects it.
- No end-to-end GPU run with the flags exists (E3/E4 on CPU only).

## Verdict
All five checks met. No `missing` criterion. **PASS WITH NOTES** at `f2f7b2e15e4f2b90545837d9e64207051c24a1cd`; GPU stages may run on this SHA with or without the flags once N1 is recorded.
