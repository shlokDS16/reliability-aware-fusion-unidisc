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

1. SUPERSEDED by SAP A5 (section 6 below): `headroom.py` is not used for H (its MIN_NV = 90 cannot be met by 50 items); `h3_gonogo decide` writes `runs/P2-GATE-H3/family.json`.
2. SUPERSEDED by SAP A5.11 delta 1 (section 6 below): `h3` now runs `run_gate_m4` on the derived H3 file under the plan family. (`run_gate_m3 --folds-path` stays but H does not use it.)
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

## 6. Update 2026-10-29 (later): SAP addendum A5 final (b32e72a1), merged into this branch

Branch merged with `claude/frosty-clarke-209639` at b32e72a1 (contains A5 and the S2 fix 8d1bee3a, checked as an ancestor). The main worktree was not touched.

| item | change |
|---|---|
| `exp_p2/gate/h3_gonogo.py` (new) | `plan`: writes `folds_hardneg_h3.json` (`test` = the 50 `head` items verbatim) and `runs/P2-GATE-H3-PLAN/family.json` (M3's three corruptions, fields corruption/severity/key; `n_rule` = H3-pilot, test_fold 50; SHA-256 of M3's family.json and folds_hardneg.json, LF-normalised); refuses to overwrite either (checked before writing either); prints the H3 start deadline (computed: Fri 30 Oct 12:27 IST). `decide --h3-run P2-GATE-H3 [--now]`: rule of A5.5 (n_valid >= 45; (a) F- > F+ and exact McNemar p of (6 F-, 6 F+) <= 0.05/3; (b) G >= 3 unsigned), R1 for G* >= 8, R2 for 3 to 7, NO-GO if no corruption is tested; time rule of A5.12 with the named constants (W_H4_300 2.9, W_H4_200 1.8, A_H4 0.5, M 2.0 h, freeze 2026-10-30T18:00+05:30) giving test_fold 300 / 200 / 0; write-once `runs/P2-GATE-H3/family.json` in the schema of A5.5a; exit 2 (file still written, NO-GO, status "not run (pilot incomplete)") when no corruption has n_valid >= 45. `yg` is reduced to the unsigned `yg != yn` at once; no signed key in the output (tested). No random numbers. |
| `exp_p2/gate/h_strata.py` (new) | identity checks (A5.8: idx, gid 7000-7299, image_id and captions vs the `test` list, caption != neg_caption, no image shared with the M4 items, config `folds_sha256` equals the file's hash raw or LF-normalised); LM (replace_obj, replace_att, replace_rel, swap_obj, swap_att) and LA (add_obj, add_att) strata and per-subset tests (b, c, n, net, 95% CI, exact p unadjusted, labelled exploratory); stratified bootstrap (within the seven subsets) 95 and 90% CIs; none-arm clean-versus-corrupted flips with the restore-clean bound (descriptive); `length_rule` (clause "not present on the length-matched subsets" iff a rejection with b > c and an LM estimate of opposite sign with 95% CI excluding 0); `h_label` (A5.9: the seven labels plus "not run" statuses, M/G split per corruption, H-CAL clause flag from `K4_violation_evidence`); seeds `SeedSequence(20261028, spawn_key=(33,))`, one child per corruption in REALISTIC order (a corruption's stream does not depend on which others run); `seeds.py` untouched. Output `runs/P2-GATE-H4/h_strata.json`. |
| `exp_p2/gate/gate_driver.py` | `STAGES["h3"] = ("exp_p2.run_gate_m4", "P2-GATE-H3", 50)` with `--folds-path runs/P2-HARDNEG-ITEMS/folds_hardneg_h3.json --family-run P2-GATE-H3-PLAN`; `h4` unchanged (`folds_hardneg.json`, `--family-run P2-GATE-H3`). New constant `HARDNEG_FOLDS_H3`. |
| `exp_p2/run_gate_m4.py` | `check_n_against_rule` now refuses when the file's `test_fold` is 0 (any `--n`, 0 included). Before, `--n 0` would have matched a test_fold of 0 and `get_items` (which treats a falsy `--n` as "all items") would have run the whole fold. No effect when test_fold > 0. `analysis_m4` is unchanged. |
| tests | `test_gate_h3_gonogo.py` (25), `test_gate_h_strata.py` (16), `test_gate_hardneg_reduced_family.py` (4: M4 with splice only, jpeg + splice, and noise only passes the ps_frozen and `--denoise-for` checks and builds exactly the expected conditions; a differing `--denoise-for` is refused). `test_gate_hardneg_runners.py` and `test_gate_runner.py` updated for the new h3 mapping. |

Tests run (CPU, one process): the new and changed files above plus test_gate_hardneg_items, test_gate_runner, test_gate_runners_fake, test_gate_integration, test_gate_m4_analysis, test_gate_ps_freeze, test_gate_swap, test_gate_safety: 243 passed. test_gate_s2 was not run (S2 is on the GPU).

### Ambiguities in A5 and how they were resolved (for the auditor)
1. "H3 rows are missing or fewer than 45 rows are valid for every corruption" (A5.5a, exit 2): implemented as "no corruption has n_valid >= 45" (no rows, a short prefix, or heavy NaN). A corruption with n_valid < 45 while another has >= 45 is simply not tested, exit 0.
2. "Output identical for two inputs ... but different yg elsewhere": the `inputs` block holds the SHA-256 of the raw rows file, which differs between such inputs; the test compares everything except `inputs`.
3. `per_corruption` carries an extra `key` field; `family` entries carry `G_c, F_minus, F_plus` beside corruption, severity, key (the readers ignore extras).
4. Time rule when H3 is NO-GO: status "not tested (NO-GO)", test_fold 0, rule NO-GO. When the time cut gives 0 under R1 or R2, `rule` stays R1 or R2, test_fold is 0, `go` is false, status "cut by time"; `analysis_m4` is then not run.
5. `h_label`: "H-NOGO" needs rule NO-GO and an empty `family`; a pilot-incomplete file gives no label ("not run (pilot incomplete)", deviations box only), as A5.9 says.
6. A5.8 says the identity check asserts that no image is shared with the M4 items; when `runs/P2-GATE-M4/items.jsonl` is absent the check is recorded as `checked: false` instead of failing (the file is untracked here; it exists in the main worktree).
7. `ps_frozen.json` is read from the M3 run directory whatever `--family-run` is (unchanged code path).
