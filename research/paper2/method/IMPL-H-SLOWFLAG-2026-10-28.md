# IMPL-H: --slow-factor / --slow-min-s CLI flags (2026-10-28)

Implementer note. Evidence level for the claims below: E4 (tests run here, CPU only). Nothing was run on the GPU.

## Change
The slow-item guard rule (`exp_p2/gate/guards.py`: an item stops the run if `busy_s >= slow_min_s` and `busy_s > slow_factor * median(earlier items of the chunk)`) is now configurable from the command line.
`guards.py` is untouched: defaults stay `slow_factor = 2.0`, `slow_min_s = 1.0`, and the rule logic is unchanged. Each new flag defaults to the dataclass field (`Guards.slow_factor`, `Guards.slow_min_s`).

| File | Lines (after change) | What |
|---|---|---|
| `exp_p2/gate/runner.py` | 38-39 (flags in `base_parser`), 51 (`guards_from_args` kwargs) | `--slow-factor`, `--slow-min-s`; passed to `Guards(...)` |
| `exp_p2/gate/probe2_guarded.py` | 58-59 (flags in `run_guarded`'s own argparse), 83 (`Guards(...)` kwargs) | same |
| `exp_p2/omni/build.py` | 82 (`omni_guards_from_args` kwargs) | passes `a.slow_factor`, `a.slow_min_s` to `OmniGuards(...)` |
| `tests/exp_p2/test_guard_slow_flags.py` | new | 11 tests (below) |

## Parsers covered
- `runner.base_parser` -> `runner.guards_from_args`: used by run_gate_m1, m2, m3, m4, m5, s2, foil, suite, epred_chunk (all call `guards_from_args(a)`).
- `omni.build.omni_parser` is built on `runner.base_parser`, so it inherits the two flags; `omni_guards_from_args` now forwards them. Used by `run_gate_omni_r.py` (cal, pos, test) and `run_omni_timing.py`. Neither of these two files needed an edit: they construct no `Guards` themselves (their `cfg` dicts only record memory limits; the slow fields are deliberately not added to `cfg`, to keep the recorded config of resumed runs unchanged).
- `probe2_guarded.run_guarded`: its own argparse (the two flags are added there).
- `OmniGuards` is a dataclass subclass of `Guards`, so it inherits both fields (checked: `OmniGuards().slow_factor == 2.0`, `slow_min_s == 1.0`; `OmniGuards.after_item` calls `super().after_item`).
- `gate_driver.py`: `OMNI_FLAGS` not changed. `--extra` is `shlex.split` and appended to the stage command after `STAGE_ARGS`, so `--extra "--slow-factor 3 --slow-min-s 2"` reaches the stage parsers unchanged (tested for m2, omni-timing, omni-r-cal).
- `watchdog.py` has no slow-item rule (only memory/rise/AC), so it is not affected.

The task text named `run_gate_omni_r.py:~270` and `run_omni_timing.py:~135`; the grep hits there are `cfg` dict entries (`max_rise_mib=a.max_rise_mib`), not argparse or constructor sites.

## Line endings
The three source files use CRLF; the edits preserve CRLF (done with a script that writes `\r\n`).

## Tests run (CPU, python 3.14 with torch, no GPU touched)
- `tests/exp_p2/test_guard_slow_flags.py`: defaults 2.0/1.0 (Guards, OmniGuards, runner parser, omni parser, probe2_guarded, driver without `--extra`); flags parse and reach the `Guards`/`OmniGuards` object for each parser; with `slow_factor=3, slow_min_s=2` a 3.0 s item after a 1.4 s median does not trip and a 5.0 s item does; the default rule does trip on the 3.0 s item; probe2 end to end on the fake CUDA (exit 0 for 3.0 s, exit 76 `slow_item` for 5.0 s); driver `--extra` passthrough.
  - Note on the numbers: the median used is 1.4 s, not 1.5 s. With a 1.5 s median a 3.0 s item equals 2.0x and does not trip the strict `>` default, so 1.4 s is needed to reproduce a default-rule stop at 3.0 s.
- Related suites run together with it: `test_gate_safety.py`, `test_gate_integration.py`, `test_gate_runner.py`, `test_omni_runners.py`, `test_omni_stack.py`, `test_gate_runners_fake.py`, `test_gate_epred_chunk.py`.
- Result: 111 passed, 5 skipped (first group, including the new file); 46 passed (second group). The 5 skips are `test_omni_stack.py:34` ("omni stack not available here: ModuleNotFoundError"), present before this change.
- The full suite was NOT run (per the brief).

## Not verified
- No real GPU stage was launched with the flags; the argparse and constructor path is covered only by the CPU tests above.
- `run_gate_omni_r.py` / `run_omni_timing.py` were exercised through the argument-parse step (driver tests) and the existing fake-stack runner tests, not through an end-to-end slow-item trip.
- The new test file imports the `env` fixture and `_guarded`/`Cuda` helpers from `test_gate_safety.py` and `driver`/`_capture`/`_parse_with_the_runner` from `test_gate_integration.py`; a change to those helpers will affect it.
- The flags are not written into any run `config.json`, so a stage run with relaxed values is not distinguishable from a default run in the recorded config; the lead should note the flag values in the ledger (not verified that the driver log records the command line).
