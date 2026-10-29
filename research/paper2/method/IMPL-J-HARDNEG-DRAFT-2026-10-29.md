```yaml
agent: python-expert
date: 2026-10-29
brief: DRAFT code for a hard-negative family H (SugarCrepe) in Paper 2 GATE; nothing merged, nothing run on the GPU
sources_examined:
  - research/paper2/data/HARDNEG-FEASIBILITY-2026-10-29.md (read in full)
  - exp_p2/run_gate_m4.py, exp_p2/run_gate_m3.py, exp_p2/gate/{folds,gate_driver,seeds,headroom,analysis_m4 (main only),config,data,runner (base_parser)}.py
  - tests/exp_p2/{test_gate_runners_fake,test_gate_integration,test_gate_runner}.py (patterns and helpers)
  - research/paper2/data/sugarcrepe-probe/*.json + SHA256SUMS.txt (parsed as JSON), runs/P2-GATE-FOLDS/folds.json, runs/P2-PROBE-0{1,2}/selection.json (image ids only)
coverage: >
  CPU only. No outcome (y, d, z, flips) of any run was read. The builder was dry-run once, to a scratch directory (not runs/), only to check the counts against the feasibility report.
  NOT done: no GPU stage, no tokenizer-vs-runtime comparison beyond folds.hf_token_counter, no committed items file, no prereg addendum, no change to headroom.py.
claims:
  - statement: Default behaviour of every existing stage is unchanged when the new options are absent.
    status: supported
    evidence: 36 new tests plus 224 existing tests pass (listed below); run config.json of M3/M4 gets no new keys unless an H option is given
    level: E4
    confidence: 0.9
  - statement: The builder reproduces the feasibility numbers on the real files (5,343 eligible rows; images per subset 595/367/556/156/440/651/355) and is deterministic.
    status: supported
    evidence: dry run to scratchpad, run twice, files byte-identical; sha1 of content 6cae72d56505c1eb
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - Whether H3 can produce a usable family.json with 50 items (see "Open decisions", item 1). This blocks the H3 -> H4 chain as specified.
next_test: {hypothesis: "n/a (code draft)", intervention: "lead go/no-go, then build and commit the items file, prereg addendum, then h3", primary_metric: "n/a", falsifier: "n/a", gpu_hours: "H3 about 0.2 (50 items, M3 passes only), H4 about 2.2 (feasibility report)"}
```

# IMPL-J: family H (hard negatives) code, DRAFT

Branch `worktree-agent-aef5385b66d6a3cbd`, one commit, base 6d539fc2. Frozen files untouched: `exp_p2/gate/epred_fit.py`, `theory.py`, `tests/exp_p2/test_gate_epred_fit.py`, `exp_p2/omni/checks.py`, `tools/gpu_guard.py`.

## 1. What changed (existing files, minimal diff)

| file | change |
|---|---|
| `exp_p2/run_gate_m3.py` | new `load_folds(n_tok_fn, folds_path=None)`; `get_items` / `make_ctx` take an optional `folds_path`; `main` has `--folds-path` (default None). An explicit path must exist and is never built. Config records `folds_path` and `folds_sha256` only when the option is given. |
| `exp_p2/run_gate_m4.py` | imports `load_folds` from `run_gate_m3`; `make_ctx` (was line 94) and `get_items` (was 215) call it, so the splice donor pool (line 101, `folds.test_items(f, 500)`) follows the same file; `main` has `--folds-path` and `--family-run` (default `P2-GATE-M3`). `load_prereqs(runs, family_run)` and `check_n_against_rule(n, runs, family_run)` read `runs/<family_run>/family.json`. |
| `exp_p2/gate/analysis_m4.py` | `--folds-path` (default None = `folds.folds_path()`); missing explicit file returns 2. (`--family-run` already existed.) |
| `exp_p2/gate/gate_driver.py` | `HARDNEG_FOLDS`; `STAGES` `h3` and `h4`; `STAGE_ARGS` for both (forwarded before `--extra`, so `--extra` can override). |
| `tests/exp_p2/test_gate_runner.py` | `test_stage_table_matches_the_modules_and_run_ids` now skips `h3`/`h4` (after asserting their module): they reuse the M3/M4 modules under other run ids and item counts, which that test could not allow. |

New: `exp_p2/gate/build_hardneg_items.py`, `tests/exp_p2/test_gate_hardneg_items.py` (19 tests), `tests/exp_p2/test_gate_hardneg_runners.py` (17 tests).

### n-rule (item 2), design choice
`--family-run <run id>` instead of a bypass. In H4 the rule `n == family.json n_rule.test_fold` is still enforced, but against `runs/P2-GATE-H3/family.json`. The same `--family-run` also supplies the corruption family and the endpoint-d check (`load_prereqs`), so the family H4 runs is the one the analysis (`analysis_m4 --family-run P2-GATE-H3`) will read; M3's family cannot be used by mistake with H3's n-rule or the reverse. M4 default is byte-for-byte the old path. The M2 threshold, `ps_frozen.json` and `detection_frozen.json` are reused unchanged (feasibility report section 4.6).

## 2. Builder: `python -m exp_p2.gate.build_hardneg_items [--out PATH] [--slow]`

Writes `runs/P2-HARDNEG-ITEMS/folds_hardneg.json` (refuses to overwrite; SHA-256 of the seven SugarCrepe files is verified first, LF-normalised because `core.autocrlf=true` rewrites the checked-out bytes). Schema = `folds.json`: `head` = H3 (50), `test` = H4 (300), `cal` and `test_ext` empty, so `pipeline.check_fold_tokens`, `folds.test_items` and the splice-donor pool work unchanged. Per item: `idx, gid, image_id, caption, n_tok, neg_caption` (as folds.json) plus `n_tok_neg, tok_diff (= n_tok_neg - n_tok), subset, neg_source`.

Rule: one row per image; drop images in folds.json (cal, head, test, test_ext), probe 1+2 `selection.json` (both required, else error), and `runs/P2-GATE-M1|M5/items.jsonl` if present; both captions 5-32 tokens (`folds.hf_token_counter`); positive != negative; quotas H4 43,43,43,43,43,43,42 (the 42 and the order drawn by the seed) and H3 7 x 6 + 8; subsets filled scarcest first (swap_obj), images a seeded permutation, no image in two subsets, H3 and H4 disjoint; final order of each fold is a seeded shuffle (a partial run stays spread over subsets).

Seed: local constant `SELECT_SEED = [config.SEED_GATE, 9]` (streams 7 and 8 are used by folds.py). Not appended to `seeds.ANALYSES`: appending is technically safe for earlier children, but position 32 is reserved for `tier3_fusion` (`tier3_fusion.SEED_SPAWN_KEY = (32,)`, A4.1.7), so an append would move that child. gids: H3 6000 + idx, H4 7000 + idx (folds use 0-2499, family B 4000-5999).

Dry run on the real files (scratch output, not committed): rows 7,511; in an existing pool 2,156; token rule 12; same caption 0; eligible 5,343 rows (= the feasibility report); eligible images 595/367/556/156/440/651/355; excluded images 1,394 (cal 300, head 100, test 300, test_ext 200, probe 494 as counted per source); H4 per subset 43 x 6 and swap_att 42; H3 7 x 6 and add_att 8; mean `tok_diff` in H4: add_obj 3.95, add_att 2.63, replace_obj 0.65, others 0.0-0.4. Run twice: identical bytes, content sha1 `6cae72d56505c1eb`. In this worktree M1/M5 `items.jsonl` do not exist (untracked), so they were reported as `missing_optional`; they are covered by the probe and fold lists by construction, but build in the main worktree so that they are read if present. `save_folds` writes with the platform newline, so the file's byte hash differs between Windows and git's LF blob: record the committed (LF) blob hash, as for folds.json.

## 3. Open decisions for the lead

1. **H3 cannot yield a family.json at n = 50 as `headroom.py` stands.** `headroom.MIN_NV = 90` (rung passes only with n_v >= 90) is a module constant; with 50 items no rung can pass, so `family` is empty and the rule is NO-GO. Options: (a) H3 is a pilot only and H4 keeps `--family-run P2-GATE-M3` (drop the H3 family arg from `STAGE_ARGS["h4"]`; the n-rule then stays M3's, 300 only if M3 chose R1/R3: M3's file says R2 = 500, which the 300-item H4 would refuse, so a family-H-specific rule is still needed); (b) add a registered `--min-nv` to headroom.py (a prereg change I did not make); (c) hand-written H3 family.json (not recommended: it bypasses the blind rule). I did not change `headroom.py`.
2. **h3 maps to `run_gate_m3`, not `run_gate_m4`.** The brief said both stages map to run_gate_m4. A headroom stage needs M3 rows (`rungs`, no gate fields; `headroom.assert_blind`) and reads the `head` list, which is what `run_gate_m3` writes; `run_gate_m4` rows carry gate fields and cannot feed `headroom.py`. If you meant a 50-item M4 pilot instead, change `STAGES["h3"]` and `STAGE_ARGS["h3"]` only (the `--folds-path` option exists on both).
3. **Calibration exchangeability** (feasibility report section 5): the M2 threshold is reused; SugarCrepe images are not a random val2017 draw. State as a limit in the addendum.
4. The prereg addendum, the committed items file with SHA-256, and the SAP-style leak check (L0-L8) on the final pool are still to be done before any GPU use. `driver.gates_ok`, hold files, dirty-tree refusal and the gpu_guard pin apply to `h3`/`h4` as to any stage.
5. Commit trailer: the brief asked for "Claude Opus 5.5"; this work was done by Sonnet 5.5. The trailer is as requested.

## 4. Order of use (after go)

```
python -m exp_p2.gate.build_hardneg_items                      # CPU; commit runs/P2-HARDNEG-ITEMS/folds_hardneg.json + addendum
python -m exp_p2.gate.gate_driver --stage h3                    # 50 head items, run_gate_m3 --folds-path ...
python -m exp_p2.gate.headroom --run-id P2-GATE-H3 --endpoint d # see open decision 1; commit family.json
python -m exp_p2.gate.gate_driver --stage h4                    # 300 test items, run_gate_m4 --folds-path ... --family-run P2-GATE-H3
python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-H4 --family-run P2-GATE-H3 --folds-path runs/P2-HARDNEG-ITEMS/folds_hardneg.json
```

## 5. Tests run (CPU only, one process at a time)

- New: `tests/exp_p2/test_gate_hardneg_items.py`, `tests/exp_p2/test_gate_hardneg_runners.py`: 36 passed. They cover: defaults unchanged (parser defaults, `ensure_folds` called with no path, no H keys in the default run config, old stages launch without the new flags); `--folds-path` loading (H items with their own negatives, explicit missing path never built, M3 `head` list, refusal before the model is touched, analysis_m4); n-rule against H3's family file (no bypass: wrong n refused, missing file stops, M3's R2 still refuses 300, family and endpoint from the same run); end-to-end `main` up to the loop; driver stages (table, commands parse with the runners' real parsers, `--extra` override); builder (disjointness from every pool, one row per image, determinism and input-order independence, different seed differs, stratification 42/43 and 7/8, scarcest-first, too-small pool raises, token rule on both captions, `tok_diff`, schema and `token_check`, committed SugarCrepe hashes and counts 7,511 / 1,560, exclusion list, overwrite refusal).
- Existing, affected: test_gate_runners_fake, test_gate_integration, test_gate_m4_analysis, test_gate_runner, test_gate_swap, test_gate_ps_freeze, test_gate_data (143 passed + 1 failure fixed by the one-line test edit above, then 17 passed); test_gate_safety, test_gate_epred, test_gate_epred_fit, test_gate_analysis (94 passed); test_gate_epred_chunk, test_gate_m1_partial, test_gate_s2, test_gate_tier3_fusion, test_guard_slow_flags, test_omni_signing (130 passed).
