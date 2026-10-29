```yaml
agent: gate-auditor
date: 2026-10-29
brief: >
  Spec-conformance audit of the family H code (Paper 2, GATE) against SAP addendum A5 r1 and red-team conditions C5-1..C5-8.
  Audited branch worktree-agent-aef5385b66d6a3cbd at b2725e579da6950229be9a5289c72f96913a3b5d (merges claude/frosty-clarke-209639 at 2f62f1df);
  pinned reference 8d1bee3a (card v4 section 9 row A-5).
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md (r1, all sections)
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md lines 571-650 ("A5 signature", C5-1..C5-8)
  - research/paper2/method/IMPL-J-HARDNEG-DRAFT-2026-10-29.md (all; sections 6-7 ambiguities)
  - git diff 8d1bee3a b2725e57 -- exp_p2 tools tests (all 13 files); git diff 2f62f1df b2725e57 --name-only
  - exp_p2/gate/h3_gonogo.py, exp_p2/gate/h_strata.py, exp_p2/gate/build_hardneg_items.py (read in full)
  - exp_p2/run_gate_m4.py 44-104, 107-125, 186-235; exp_p2/run_gate_m3.py 24-110; exp_p2/gate/gate_driver.py 30-230;
    exp_p2/gate/analysis_m4.py 1-130, 241-290, 600-663; exp_p2/gate/report.py 18-37; exp_p2/gate/stats.py 10-33; exp_p2/gate/seeds.py;
    exp_p2/gate/folds.py 84-170; exp_p2/gate/artifacts.py 16-28; exp_p2/gate/runner.py 100-220 (prints only); exp_p2/common.py 77-90
  - tests/exp_p2/test_gate_h3_gonogo.py (1-125, 200-262, 376-423), test_gate_hardneg_items.py (240-257), test_gate_hardneg_runners.py (186-230), test_gate_h_strata.py (241-250); all test names
  - runs/P2-GATE-M3/family.json (n_rule, family corruptions and entry keys only)
coverage: >
  Code paths above at b2725e57. NOT opened: runs/P2-GATE-S2*, any M4 outcome (runs/P2-GATE-M4/items.jsonl, arrays, analysis.json content), any H3/H4 run
  (none exists). Image ids only were read from runs/P2-GATE-M1/items.jsonl, runs/P2-GATE-M5/items.jsonl (main worktree, via exclusion_ids) and
  runs/P2-GATE-FOIL/pool.json. NOT done: the C5-8 byte-identical regeneration of runs/P2-GATE-M4/analysis.json and the Tier-3/E-dec/E-pred outputs
  (a post-S2, post-merge step; out of this brief; see N-2).
claims:
  - statement: "With the new options absent, M2-M5, S2, FOIL, suite, Omni and E-pred stages take the same code path as at 8d1bee3a."
    status: supported
    evidence: "diff 8d1bee3a..b2725e57; full tests/exp_p2 run (691 passed, 5 skipped, 0 failed)"
    level: E4
    confidence: 0.9
  - statement: "h3_gonogo plan/decide implement A5.5a literally (constants, McNemar bound on 6F-/6F+, alpha 0.05/3, G >= 3, R1/R2/NO-GO, time bounds, write-once)."
    status: supported
    evidence: "exp_p2/gate/h3_gonogo.py:30-45, 65-81, 91-171, 180-248; three synthetic cases recomputed by hand (section 2)"
    level: E4
    confidence: 0.9
  - statement: "The builder is deterministic and reproduces content sha1 6cae72d56505c1eb; H items are disjoint from folds, probes, M1, M5 and the FOIL pool."
    status: supported
    evidence: "two scratch builds byte-identical; independent CPU check (section 5)"
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - "Whether analysis_m4 at b2725e57 regenerates runs/P2-GATE-M4/analysis.json byte-identically (C5-8): expected from the diff (E3), not run."
next_test: {hypothesis: "merged analysis_m4 reproduces committed P outputs", intervention: "C5-8 regeneration after S2 ends", primary_metric: "LF-normalised byte identity", falsifier: "any byte difference", gpu_hours: 0}
```

# Gate code audit: family H (hard negatives), 2026-10-29

**Audited SHA:** `b2725e579da6950229be9a5289c72f96913a3b5d` (branch `worktree-agent-aef5385b66d6a3cbd`). Ancestors checked: 8d1bee3a and 2f62f1df.
Branch-only changes against 2f62f1df: the 13 code/test files below plus the IMPL-J report; nothing else.

## Verdict: PASS WITH FIXES

The code implements A5.5a, A5.7 (r1 length rule), A5.8 and A5.9 as written, and leaves the default behaviour of every existing stage unchanged.
Two small fixes are required before the pin row A-6 (FX-1, FX-2). Neither changes a rule, a constant or an existing stage. The C5-8 regeneration
is still outstanding (N-2). It is the lead's precondition after S2 has ended, and this verdict does not cover it.

| Fix | Severity | What | Where |
|---|---|---|---|
| **FX-1** | minor, before H3 | H-L4 (disjoint from the FOIL pool, "assertion; 0 expected", A5.2) is in neither the builder, its report nor a test. The property holds: 540 FOIL pool images, 0 outside the folds, 0 overlap with the 350 H items (section 5). Fix: add an H-L4 assertion and count to `build_hardneg_items.main`'s report or a test. Alternatively, the lead's committed leak-check record can carry this audit's independent count. | `exp_p2/gate/build_hardneg_items.py:216-247` |
| **FX-2** | minor, before H3 | `decide` records `now` and `last_h3_row_time`, but not whether they came from the system clock or from `--now` / `--last-row-time`. A5.5a says "`--now` only for tests; otherwise the system clock ... recorded". As written, an override is indistinguishable from the clock afterwards (red-team F7 discretion). Fix: add `now_source` ("system" or "--now"), the actual system clock at decide time, and `last_row_source` ("mtime" or "--last-row-time") to `decide_record`. | `exp_p2/gate/h3_gonogo.py:221-248, 257-266` |

## 1. Existing stages unchanged when the new options are absent (item 1)

| Point | Finding | Evidence |
|---|---|---|
| `run_gate_m3` | `load_folds(fn, None)` calls `folds.ensure_folds(fn)`, as before. `get_items` and `make_ctx` get an optional `folds_path=None`. The config gains keys only if `--folds-path` is given. | `exp_p2/run_gate_m3.py:27-44, 95-97`. The only other importer is `run_gate_omni_r.py:38` (`rung_rng`, `donor_for`, both unchanged). **met** |
| `run_gate_m4` default folds path | `make_ctx` and `get_items` call `load_folds(..., None)`, which is `ensure_folds` as before. The splice donor pool is `folds.test_items(f, 500)`, unchanged. | `exp_p2/run_gate_m4.py:96-97, 104, 225`. **met** |
| `load_prereqs` / `check_n_against_rule` | `family_run` defaults to `M3_RUN`. The `--family-run` default is `P2-GATE-M3`. The other importer, `run_gate_epred_chunk.py:82`, calls `load_prereqs(runs)` and so gets the default. | `run_gate_m4.py:44-59, 62-72, 193, 196-198`. **met** |
| Added refusal of `test_fold <= 0` | It refuses every `--n` when the family file's `test_fold` is 0. Without it, `--n 0` would have equalled 0, and `get_items` reads a falsy `--n` as "all items". The committed M3 rule is R2 with test_fold 500 (read from `runs/P2-GATE-M3/family.json`), so P is not affected. **Judgement: correct and needed** (A5.5a: "test_fold 0 always refuses"). | `run_gate_m4.py:67-68`. **met** |
| run config | New keys are added only if `--folds-path` is given or `--family-run` is not M3. | `run_gate_m4.py:213-215`. **met** |
| `analysis_m4` | The only change is in `main`: `--folds-path` (default None, which is `folds.folds_path()` as before; an explicit file that is missing returns 2). No function imported by `edec`, `epred`, `tier3_fusion`, `analysis_s2` or `analysis_omni` changed. | `exp_p2/gate/analysis_m4.py:611, 641-645`. **met** (E3; byte regeneration is N-2) |
| `gate_driver` STAGE table | Only `h3` and `h4` are added (`STAGES.update`, `STAGE_ARGS.update`). Every other entry is byte-identical; the `MAX_TEMP_DEFAULT` line changed in comment whitespace only. `default_n` is unchanged. `--n` is the driver's flag (`gate_driver.py:112, 127`), so `DRV --stage h4 --n <test_fold>` is the right syntax. | `gate_driver.py:63-67`. **met** |
| Seeds | `seeds.py` is unchanged; its `ANALYSES` table has 32 entries (positions 0-31). `tier3_fusion` uses spawn key (32,) and `h_strata` uses (33,). No other module uses key 33: `analysis_posthoc/learned_ceiling/run.py:33,44` uses root 20261029, a different root. The builder's stream `[SEED_GATE, 9]` is used by no other module. H gids 6000-6049 and 7000-7299 are disjoint from the folds (0-2499) and family B (4000, 5000). DCache is keyed by (kind, caption length), not by gid. | grep over `exp_p2 tools analysis_posthoc`. **met** |
| `test_gate_runner` skip | It skips `h3`/`h4` only after asserting that their module is `run_gate_m4` (A5.11 item 6). | `tests/exp_p2/test_gate_runner.py:198-200`. **met** |

## 2. `h3_gonogo` against A5.5a (item 2)

| Spec item | Code | Status |
|---|---|---|
| Constants: N* 43, min G 3, R1 G 8, x6, alpha 0.05/3, min valid 45, gid 6000-6049, freeze 2026-10-30 18:00 IST, W_H3 0.75, A_H3 0.5, W_H4 2.9/1.8, A_H4 0.5, M 2.0 | `h3_gonogo.py:30-40` | met |
| Imports `analysis_m4.load_items`, `_arm`, `stats.mcnemar_exact`, `config.REALISTIC`; no model; no RNG | `:26-27, 69-70, 93-99, 126`; no rng anywhere | met |
| `plan`: reads M3 family and folds_hardneg; writes `folds_hardneg_h3.json` = {cal [], head [], test = head verbatim, test_ext []} and the plan family (M3's three entries with corruption, severity and key only; n_rule H3-pilot, test_fold 50, primary Y; go true; source hashes); refuses to overwrite either file (both checked before either is written); prints the start deadline 12:27 | `:180-204, 262-265`; deadline `:53-55` = 18:00 - 5.55 h = 12:27 | met (the `spec` string reads "A5.5 and A5.5a", not "A5.5a"; cosmetic, N-1) |
| `decide`: rows via `load_items`; every gid in 6000-6049 and image id in `head` | `:234-237` | met |
| valid = all of yc, yn, yg finite; `disc = (yg != yn)[valid]` formed at once; `del yg` | `:100-102` | met |
| F-, F+ (none arm), `bound_p` = exact McNemar of (6F-, 6F+), headroom = F- > F+ and p <= 0.05/3, G = sum(disc), tested = n_valid >= 45 and headroom and G >= 3 | `:103-111, 65-70` | met. F-/F+ are counted on the valid set, which is the natural reading of "validity per corruption" |
| H+, G*, R1 if G* >= 8, R2 if 3-7, NO-GO if H+ is empty | `:124-130` | met |
| `G_max_headroom` (n_valid >= 45 and (a)), null if none | `:140-143, 165` | met |
| `bound_p_at_n` with k = n_H4/50 (6 or 4) and `projection_at_n` = G x k, null when H4 is not run; the GO rule stays at x6 | `:156-159` | met |
| Time rule: 300 iff now + 5.4 h <= F (12:36), 200 iff now + 4.3 h <= F (13:42), else 0; status strings; the rule cuts n only by clock | `:73-81` | met (tests cover 12:36/12:37/13:42/13:43) |
| `decide` deadline 13:12 = 12:27 + W_H3, recorded with the last row time, the gap and `gap_over_A_H3` | `:208-210, 240-244` | met; see FX-2 on override provenance |
| Output schema (`endpoint`, `endpoint_note`, `n_headroom_items`, `family` = H+ entries + G_c, F_minus, F_plus, `excluded`, the full `n_rule` with `time_rule`, `go`, `downstream_claim_withdrawn`, `per_corruption`, `clean_none_accuracy`, `inputs`, `spec`) | `:161-168` | met; extra keys `per_corruption[c].key` and top-level `decide_record` (accepted, section 7) |
| Exit 2 and file still written (NO-GO, H-NOGO, status "not run (pilot incomplete)", test_fold 0) if rows are missing or no corruption has n_valid >= 45 | `:150-155, 248`. A missing items.jsonl gives `read_jsonl` -> [] -> n_valid 0, so the file is written with exit 2 | met |
| Write-once | `:229-230, 247` (`artifacts.write_once`, no force) | met |
| Readers: `run_gate_m4 --family-run P2-GATE-H3` takes `family` and refuses `--n != test_fold` (0 always refused); `analysis_m4` takes rule, test_fold and family; N_MIN 240 disables H-NEG at n = 200 | `run_gate_m4.py:44-72`; `analysis_m4.py:84-104, 241-249, 638-647` | met |

**Hand recomputation (synthetic rows, my own generator: `scratchpad/hand_cases.py`; exact McNemar by hand with math.comb).**
- **Case A** (09:00). jpeg F-=3, F+=0, G=9: bound (18, 0) gives p = 2/2^18 = 7.63e-6. splice F-=2, F+=0, G=4: (12, 0) gives p = 2/4096 = 0.000488. noise 0/0/0 gives p = 1.
  Hand result: H+ = {jpeg, splice}, G* = 9, R1, n = 300, G_max_headroom 9, projections 54 and 24. **Code: identical** (exit 0, R1/H-R1, test_fold 300, family [jpeg, splice]).
- **Case B** (13:00). jpeg (3,1), G 5: (18,6) gives p = 2 x 190051/2^24 = 0.02266 > 0.01667, so no headroom. noise (4,1), G 2: (24,6) gives p = 2 x 768212/2^30 = 0.00143, so headroom but G < 3.
  splice (1,1): p = 1. Hand result: H+ empty, NO-GO, test_fold 0, G_max_headroom = 2 (sentence ii). **Code: identical** (status "not tested (NO-GO)", bound_p_at_n null).
- **Case C** (13:00). jpeg (4,1), G 7: (24,6) gives p = 0.00143 and passes. Hand result: R2, G* 7, n = 200 ("n=200 by time"). The x4 bound (16,4) gives 2 x 6196/2^20 = 0.01182, and the projection is 7 x 4 = 28. **Code: identical**.

## 3. H3 firewall (item 3)

- **No signed H3 value leaves `decide`.** `yg` is used only in `valid` (finiteness) and `disc` (unsigned), then deleted (`h3_gonogo.py:98-102`). The written file holds n_valid, the none-arm F-/F+, the bound, the unsigned G, the unsigned changed-code discordance (`:109-110`), the clean none-arm accuracy and hashes. No b, c, accuracy or direction of GATE-M versus none is written. stdout prints only rule, h_rule, test_fold, the unsigned G*, the tested list and the status (`:274`). stderr carries only STOP messages (idx/gid/image id) and the gap note (`:236-237, 268, 273`). There is no logging call. Tests: `test_the_output_contains_no_signed_gate_quantity`, `test_output_depends_on_the_gate_arm_only_through_the_unsigned_indicator`, `test_stdout_stderr_and_logs_carry_no_signed_gate_quantity`, `test_decide_reads_only_the_items_file_of_the_h3_run`. **met**.
- `h_strata.run` reads only `family.json` of the H3 directory (`h_strata.py:230`; tested by recording file reads, `test_h_strata_run_reads_no_h3_row_log_or_array`). **met**.
- The driver console during an attended H3 shows only row counts, chunk launch/exit and STOP lines (`gate_driver.py:134-224`). The child's stdout, including `selfcheck`, goes to `stdout-chunkNN.log`, which A5.8 forbids opening. `refusal_reason` echoes only a STOP line. The remaining firewall is procedural (A5.8), as the SAP states.

## 4. `h_strata` length rule (item 4)

- LM = replace_obj, replace_att, replace_rel, swap_obj, swap_att and LA = add_obj, add_att (`h_strata.py:30-31`). b, c, n, n_d, net and 95% CI are returned for **every** corruption, rejected or not (`:147-170`).
- Gain: no clause only if `b_LM > c_LM` **and** `LM ci95[0] > -D_H`. Otherwise the r1 clause is added verbatim and the label gets the suffix "(length-mismatched)" (`:163-165, 222-223`). Harm uses the signs reversed (`:166-168`). D_H is `analysis_m4`'s `delta` = (b - c)/n (`report.py:26`). **met**.
- It fires for an add_*-carried effect whenever b_LM <= c_LM, or when the LM lower bound does not exclude -D_H, including the same-sign case (`test_the_clause_fires_for_an_effect_carried_by_the_add_items_even_with_the_same_sign_in_lm`). **met** (r1 text implemented literally. Residual, spec-level: a small positive LM estimate whose CI excludes -D_H passes without the clause; N-6).
- Clean control: the s_c `ci95` and `delta` keys exist (`analysis_m4.py:283-287`, `report.py:26-31`). **met**. Label logic (A5.9): H-POS-M/G by S-M `rejected`, H-MIXED, H-HARM, H-NEG from analysis_m4's "negative", H-INC, H-NOGO only with rule NO-GO and empty family, pilot incomplete and cut by time give no label (`:192-224`). **met**. Identity checks (A5.8) `:53-87`; seed key 33 `:29, 42-44`. **met**.

## 5. Builder (item 5)

| Check | Result | Evidence |
|---|---|---|
| SHA-256 of the 7 SugarCrepe files verified (LF) before reading | met | `build_hardneg_items.py:53-65, 228-231` |
| Exclusions: folds cal/head/test/test_ext, probe 1+2 (required), M1/M5 items (if present) | met | `:79-115`. Main worktree: M1 200 and M5 100 ids, **0 beyond folds+probes**, so a main-worktree build equals the scratch build |
| Disjointness (independent check, main-worktree exclusion set incl. M1, M5) | 0 overlap; H3 ∩ H4 = 0; 350 unique images | `scratchpad/check_items.py` |
| H-L4 FOIL pool | 540 ids, 0 outside the folds, 0 overlap with H. **Not asserted in code** | FX-1 |
| One row per image; no image in two subsets | met | `:178-191` (`taken`); 350 unique of 350 |
| 5-32 tokens, both captions; pos != neg | met; re-tokenised with `folds.hf_token_counter`: all n_tok/n_tok_neg match, all in 5-32; tok_diff consistent | `:137-160` |
| Each item is a genuine SugarCrepe (subset, image, positive, negative) row | met (all 350) | check script |
| Stratification | H3 7 x 6 + add_att 8; H4 43 x 6 + swap_att 42; scarcest first; seeded shuffle of the final order | `:163-194`; matches A5.2 dry run |
| Determinism; hash 6cae72d56505c1eb | **No committed items file exists** (`runs/P2-HARDNEG-ITEMS` absent in both worktrees). Two scratch builds from b2725e57 are **byte-identical**, content sha1 **6cae72d56505c1eb** (reproduced). Scratch file LF SHA-256 535e0ec961b6b952d3e3e8e4fbd71a96d8f73c7a2581a84f546a0bf57469d0de (for information; the lead records the committed LF blob hash) | `scratchpad/build1`, `build2` |
| idx/gid | H3 idx 0-49, gid 6000+idx; H4 idx 0-299, gid 7000+idx | met |
| H-L6 | main stops if 0; real value 2,156 rows | `:118-121, 239-242` |
| H-L7 | samples printed (cal 11511, head 885, test 1490, test_ext 5060, probe 1761) for the data-steward. `coco_file` is formatted from the id, not looked up, so the steward must open the COCO image (N-4) | `:124-134` |
| H-L8 | injected leak (broken filter, excluded ids reach `build`) makes `folds.check_folds` raise; with the real filter the build succeeds | `tests/exp_p2/test_gate_hardneg_items.py:243-251`; met (relies on `assert`, N-5) |

## 6. Frozen files (item 6)

`git diff --stat 8d1bee3a b2725e57` is empty for `exp_p2/gate/epred_fit.py`, `theory.py`, `tests/exp_p2/test_gate_epred_fit.py`, `exp_p2/omni/checks.py`, `tools/gpu_guard.py`,
`seeds.py`, `stats.py`, `config.py`, `folds.py`, `pipeline.py`, `runner.py`, `headroom.py`, `exp_p2/scoring.py`, and `runs/P2-GATE-M1..M4`, `runs/P2-GATE-FOLDS`. **met**.

## 7. Tests (item 7) and implementer ambiguities

**Tests:** run in the audited worktree with `.venv\Scripts\python.exe -m pytest tests/exp_p2 -q -p no:cacheprovider` at BELOW_NORMAL priority (wrapper `scratchpad/lowprio.py`), full suite:
**691 passed, 5 skipped, 0 failed in 382.7 s** (log `scratchpad/pytest_full.log`). The 5 skips are data-availability skips in pre-existing files (test_gate_data, denoise, foil, safety, suite). The new and affected files alone: 120 passed in 17.8 s, none skipped.
(Scratchpad = `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad`.)

**Ambiguities (IMPL-J section 6):**
1. Exit 2 means "no corruption has n_valid >= 45". **Accepted**: this is the literal reading of "fewer than 45 rows are valid for every corruption".
2. The invariance test excludes `inputs` (the raw-row hash). **Accepted**: the hash must differ.
3. Extra `key` in `per_corruption`; G_c/F_minus/F_plus in `family`. **Accepted**: the latter is required by A5.5a. Readers use only corruption, severity and key (`run_gate_m4.py:58`, `analysis_m4.py:63-69`).
4. Time cut under R1/R2: rule kept, test_fold 0, go false, "cut by time". **Accepted**: this matches the schema, and `run_gate_m4` refuses test_fold 0.
5. H-NOGO needs rule NO-GO and an empty family; pilot incomplete gives no label. **Accepted** (A5.9 status row).
6. The M4 overlap check is recorded `checked: false` if the M4 items file is absent. **Accepted**: the file exists in the main worktree, and disjointness from folds.test is established by the builder and section 5. Fail-closed would be stricter (optional).
7. `ps_frozen.json` is read from M3 whatever `--family-run` is. **Accepted**: unchanged path, and the PS parameters are global.

**Ambiguities (IMPL-J section 7, r1):**
1. Top-level `decide_record` beyond the "exact" schema. **Accepted**: A5.5a requires the clock, the last-row time and the gap to be recorded, and the schema has no slot for them. FX-2 adds provenance.
2. The last row time is the items.jsonl mtime. **Accepted** (no row content read). It is overridable, which is why FX-2 requires the source to be recorded.
3. D_H is the point estimate `delta`. **Accepted**: the r1 text compares the LM lower bound with -D_H.
4. The suffix is added if the clause fires for any rejected corruption, with a per-corruption list. **Accepted**: sentences are per corruption (A5.9).
5. `bound_p_at_n` is null at n_H4 = 0. **Accepted**.

## Non-blocking notes

- **N-1** The plan file's `spec` reads "SAP addendum A5, A5.5 and A5.5a" where A5.5a writes "SAP addendum A5, A5.5a". Cosmetic; no reader uses it.
- **N-2 (C5-8, open).** The byte-identical regeneration of `runs/P2-GATE-M4/analysis.json` and of the committed Tier-3, E-dec and E-pred outputs was **not** run (after S2, from the merged code; lead's precondition for pin row A-6). Static expectation: identical, because only `analysis_m4.main`'s folds path changed and its default is the same (E3). Practical note: `analysis_m4.main` overwrites `analysis.json` in place with platform newlines, so compare LF-normalised (or run `git diff --exit-code` under autocrlf) and run it on a copy if possible.
- **N-3 (out of scope).** SAP Appendix H gives the SHA-256 of `runs/P2-GATE-A5/a5_power_output.txt` as `102141db…`. That is the hash of the **CRLF** bytes; the committed LF bytes hash to `8601dce25883a16507fec3ac4fcac241a88e66e5b271ef76284173a11ef4a32b`. The content is the same apart from line endings. `a5_power.py` matches (`a3d36ce7…`).
- **N-4** H-L7's `coco_file` is derived from the id. The data-steward must open the actual COCO file and the SugarCrepe row.
- **N-5** `folds.check_folds` (H-L1/2/3/5, H-L8) uses `assert`. Run the builder without `python -O`. This is a pre-existing pattern.
- **N-6** The length rule is implemented literally. Its residual weakness (a small same-sign LM estimate passes) is in the spec, not the code.

## Gate bookkeeping

Not ticked in `research/progress.md`: the brief asked only for this file. No ledger rows were added, and nothing was committed. Code was not edited.
