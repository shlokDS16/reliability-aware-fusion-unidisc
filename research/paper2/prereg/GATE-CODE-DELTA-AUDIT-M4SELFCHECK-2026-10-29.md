# Gate-code delta audit: run_gate_m4 self-check under deterministic cuDNN (2026-10-29 21:40 IST)

Auditor: gate-auditor (did not write the code). CPU only; no GPU, no outcome file opened (no items.jsonl, arrays, analysis outputs).
Delta: `git diff 725a1b5a 1871fe7d -- exp_p2 tools tests` = `exp_p2/run_gate_m4.py` (+6/-1) and `tests/exp_p2/test_gate_a6_options.py` (+40). Code pin under audit: 725a1b5a (card `PREREG-GATE-v4-2026-10-28.md` row A-6).

## 1. Scope: met
- The only production change is inside `main()`'s `selfcheck` closure, `exp_p2/run_gate_m4.py:328-334`: the unchanged expression `sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])` now runs in `with deterministic_cudnn():`, imported lazily inside the closure (line 332).
- `load` (323-325), `get_items` (336+), `make_ctx_factory` (150+), `process`, the `runner.run_items` call, argument defaults and cfg construction are outside the hunk (the diff has a single hunk, @@ -326). Behaviour of every other stage is unchanged; the closure is only reached through `runner.run_items` `selfcheck=`.
- The 0.99 rule `runner.selfcheck_passed` (`exp_p2/gate/runner.py:73-75`) is not in the diff. Nothing under `exp_p2/gate/` or `tools/` changed.

## 2. Items do not run under deterministic cuDNN: met, with one residual
- `deterministic_cudnn` (`exp_p2/run_gate_s2.py:275-295`) is a `contextlib.contextmanager`: it saves `(benchmark, deterministic)`, sets `(False, True)`, and restores the saved values in `finally` (also on exception). The new test checks both the normal and the raising path.
- Order in `runner.run_items` (`runner.py:145-160`): `load()` (UniDisc build sets benchmark on) -> `get_items` -> self-check (only if `selfcheck.json` is absent) -> `make_ctx` -> `_loop` -> `process`. All items, and `make_ctx` (which includes `checks.l10_once`, `run_gate_m4.py:158`), therefore run after the flags are restored, with UniDisc's own settings (benchmark on), as M4 did. L1 items thus use the same backend settings as M4, whose arrays trained the frozen LRF object.
- Why this matters: unlike S2, `run_gate_m4.process` encodes fresh images with the VQ encoder. If the flags stayed deterministic, the L1 clean codes would come from a different convolution-algorithm path than the M4 codes the LRF was fitted on (the S2 diag reports a 1.4% shift in codes from changing TF32 precision, and that benchmark off differs from the benchmark-on path is the same class of effect). Restoring keeps the L1 feature path identical to M4's.
- Residual risks, stated honestly:
  a) `get_items` runs before the self-check but only calls `sc.caption_ids` (tokenizer, text) and writes JSON (`pipeline.check_fold_tokens`, `pipeline.py:82-93`); no convolution runs before the self-check, and with benchmark off the self-check itself adds no entries to the benchmark algorithm cache, so nothing it does can be reused by items. `l10_once` and the items run later in benchmark mode and choose their own algorithms.
  b) The self-check now certifies the layout/tokeniser agreement under the deterministic backend, not under the backend the items use. Under benchmark mode a fresh tokenisation can still differ by up to about 1.5% of image tokens between processes (card row A-5 disclosure; M4 passed at 1.0 in its own process: `runs/P2-GATE-M4/selfcheck.json` image_tokens_frac_equal 1.0). That variability is pre-existing, identical for M4, and is not introduced or hidden by this delta, but the L1 `selfcheck.json` will record deterministic-backend values; the write-up should say so and repeat the A-5 disclosure for L1.
  c) A pass of this check does not prove L1 item codes equal M4's stored codes; that was never claimed.

## 3. Lazy import of run_gate_s2: met
- No circular import: `run_gate_s2.py` top level imports (lines 22-37) are `__future__`, contextlib, json, sys, time, pathlib, types, numpy, `exp_p2.common`, `exp_p2.gate.{arms,config,evidence,folds,pipeline,reinfill,runner}`; none of these names `run_gate_m4` (grep over those modules and `common.py`: no match). `analysis_s2.py:275` imports run_gate_s2 lazily and is not on this path.
- Import side effects: `sys.path.insert(0, ROOT)` (same line m4 already executes, line 27), then constants and a `CONFIG` dict (lines 39-51+); the only top-level statement with effect is the `__main__` guard at 365. No torch flag, file or env change at import. The import happens only when the self-check closure runs. `exp_p2/run_gate_lrf_rescore.py:91` already uses the same lazy import.

## 4. Test: met
- New test `test_m4_selfcheck_runs_under_deterministic_cudnn_and_restores_the_flags` (`tests/exp_p2/test_gate_a6_options.py:309-346`): captures the closure that `m4.main` hands to `runner.run_items`, asserts `process is m4.process`, flags seen inside are `(False, True)`, flags afterwards `(True, False)` on both pass and exception, `selfcheck_passed` accepts 1.0 and rejects 0.98828125.
- On 725a1b5a (scratch export in the session scratchpad via `git archive 725a1b5a exp_p2 tests exp001`, only the new test file copied in): FAILS with `assert [(True, False)] == [(False, True)]` (line 339). On the tree (1871fe7d): passes.
- `python -m pytest -q tests/exp_p2/test_gate_a6_options.py tests/exp_p2/test_s2_selfcheck_deterministic.py tests/exp_p2/test_gate_runner.py tests/exp_p2/test_gate_runners_fake.py`: 53 passed, 1 warning (pynvml deprecation). I did not run the full suite (not asked).

## 5. Frozen files: met
`git diff --name-only 725a1b5a 1871fe7d` outside research/ and runs/: exactly `exp_p2/run_gate_m4.py` and `tests/exp_p2/test_gate_a6_options.py`. The rest of the stat is research notes, ledgers, progress and run records (non-code).

## 6. Regeneration check (C5-8 style): not needed
The analysis code (`analysis_m4`, edec, epred, tier3_fusion) is not touched, nor is `process`; the delta only wraps a GPU self-check closure that no analysis path calls and that returns the same dict type. No committed analysis output can change. State this in the new card row instead of re-running.

## Findings / fixes (documentation, not code)
- F1 (must do before the next L1 launch): the card has no row for this delta. The new test docstring says "Card row A-8" but the card ends at A-7 (row A-7 is the family H preconditions). The pre-launch check `git diff --quiet 725a1b5a HEAD -- exp_p2 tools tests` will now fail by design. Add row A-8 (date/time, pin 725a1b5a -> the merge commit containing 1871fe7d, diff SHA-256 prefix, "only the self-check closure of run_gate_m4 changed, 0.99 rule and items unchanged, no regeneration needed because no analysis path changed", failed attempts kept as `runs/P2-LRF-L1.try1` and `.try2`, residual 2b above) before the L1 stage starts. The lead edits the card; I have not.
- F2: the commit message says PENDING audit; this file is the audit. Gate-driver LG (`lrf-lg`, also run_gate_m4) will inherit the same fix; no extra change needed.

VERDICT: PASS WITH FIXES: add card row A-8 (pin move to the commit holding 1871fe7d, wording as in F1, disclosing residual 2b) before launching L1; no code change required.
