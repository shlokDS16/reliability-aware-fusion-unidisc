```yaml
agent: gate-auditor
date: 2026-10-29
brief: Spec-conformance audit of the Study 2 (LRF) code, branch worktree-agent-aec5b3a0e0fa71ebc at 70a06284, against SAP A6 r1 (941a260b), red-team C6-1..C6-11 and the "A6 r1 check", D0083, D0084
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md r1 (full)
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md lines 773-901 (C6-1..C6-11, "A6 r1 check")
  - research/ledgers/decisions.jsonl rows D0083, D0084
  - research/paper2/method/IMPL-K-A6-LRF-2026-10-29.md (audited worktree)
  - research/paper2/posthoc/LRF-FROZEN-2026-10-29.md section 3; runs/P2-LRF-FROZEN/spec.json (layout_caveat, code_sha256 only)
  - code at 70a06284: exp_p2/run_gate_m4.py, exp_p2/run_gate_lrf_rescore.py, exp_p2/gate/{build_lrf_fold,lrf_score,lrf_nrule,gate_driver}.py, analysis/paper2/lrf/{a6_analysis,baselines}.py,
    analysis_posthoc/learned_ceiling/{lrf.py,run.py lines 35-74,data.py lines 1-90}; exp_p2/gate/{pipeline.py 30-46,scores.py 23-44 and 82-100,dcache.py 63-85,folds.py 84-99,suite.py 33-128}, exp_p2/scoring.py 92-104,
    exp_p2/run_gate_m3.py 27-57, exp_p2/run_gate_s2.py 274-300; tests/exp_p2/test_gate_a6_options.py (full), test names of the other new test files
  - git diff b5b41d90..70a06284 and 8d1bee3a..70a06284 (exp_p2, tools, analysis_posthoc, tests)
coverage: >
  Every A6 code path listed in A6.11 and the brief's items (1)-(8). NOT opened (brief): any S2, H, FOIL-test or new-run output; runs/P2-LRF-FROZEN diagnostics/freeze_check/hpo contents.
  Not run: anything on the GPU (S2 was on it); the real-model invariance check (it is part of the re-score stage itself). The fold builder was not run on real data (implementer dry run only; not re-done).
claims:
  - statement: "With every A6 option absent, run_gate_m4 at 70a06284 gives byte-identical rows and arrays to run_gate_m4 at b5b41d90 and at 8d1bee3a (3 option sets x 3 fold shapes, each module building its own ctx), and every pre-existing driver stage is unchanged."
    status: supported
    evidence: "auditor test file (scratchpad) test_audit_byte_identity.py: 20 passed; implementer's parity test passes in the full suite"
    level: E4
    confidence: 0.9
  - statement: "Full test suite tests/exp_p2 at 70a06284: 779 passed, 5 skipped (none of the skips in the new A6 files), 346 s at BelowNormal priority."
    status: supported
    evidence: "scratchpad pytest_full.out; new A6 files alone 84 passed, 0 skipped"
    level: E4
    confidence: 0.95
  - statement: "The scorer stops (exit 2, nothing written) on a missing codebook, a missing DI_n013.npy, a config.json without the input hashes, a pins model mismatch, and NaN in B, D, tbv, nbr, tex, s3 or Delta; all-zero weights and infinite Delta raise NonFinite; a tie is wrong."
    status: supported
    evidence: "scratchpad nan_path_check.py output (real pinned codebook and DI_n013 copies, synthetic items)"
    level: E4
    confidence: 0.9
  - statement: "The retired model ca5c4e2f can be scored on any run by `lrf_score --frozen-dir runs/P2-LRF-FROZEN` without a pins file, and the meta then says pinned_externally true."
    status: supported
    evidence: "nan_path_check.py case all_present_no_pins_ca5c4e2f: exit 0, predictions written, meta pinned_externally true; lrf_score.py:98-110, 300-302"
    level: E4
    confidence: 0.95
  - statement: "No code on the branch performs the A6.2 step-4 re-freeze as specified: lrf.py --freeze (unchanged) reads runs/P2-GATE-M4/arrays, writes into runs/P2-LRF-FROZEN and computes and prints in-sample accuracy before any commit."
    status: supported
    evidence: "analysis_posthoc/learned_ceiling/lrf.py:32, 87-145; run.py:35-36"
    level: E3
    confidence: 0.95
competing_explanations:
  - "The implementer may have expected the lead to run the re-freeze by hand with edited constants; A6.2 step 4 and A6.11 item 6 require audited code, and a hand edit would change lrf.py's hash without an audit."
unknowns:
  - real-model invariance (exact 0) and positive control (<= 1e-5) results: not run yet (they run inside the re-score stage)
  - whether S2 or H item files add ids outside the union (not opened, by brief)
next_test: {hypothesis: "after fixes F1-F6 the A6 code conforms", intervention: "delta re-audit of the fix commit (same byte-identity file, failure-path script, new tests for the re-freeze, plan writer and cross-fit entry)", primary_metric: "all criteria met", falsifier: "any missing criterion", gpu_hours: 0}
```

# Gate code audit: A6 r1 Study 2 (LRF) code at 70a06284

**Audited SHA:** `70a06284` (branch `worktree-agent-aec5b3a0e0fa71ebc`; merges `91f78475` and the audited family-H branch `b5b41d90`; `8d1bee3a` is an ancestor).
**Date:** 2026-10-29. **Auditor:** gate-auditor (no code edited, nothing committed, no ledger rows added).

## Verdict: FAIL (as a whole); the parts that exist are close to conformant

A gate with any `missing` criterion fails. Criterion (3), the re-freeze procedure, has no conforming code. Running the unchanged freeze would break A6.2 step 4: it would overwrite the retired object's directory and compute accuracy before the hash commit. The n-rule's cross-fit input and the plan files have no code either.

Everything else is met or nearly so:
- byte-identity with all options absent;
- the fixed-slot features, the fold builder and the extra cells;
- the non-finite rule, the analysis, the driver stages and the baseline script.

The fixes are short. A delta re-audit of the fix commit is enough; this full audit need not be repeated.

**Usable before the fixes?** The `lrf-rescore` stage itself is not blocked by F1, F2, F4 or F5. It needs F3 (enforce the check gate) and F6 (run id) first, and then a delta audit. Shlok's GPU go-ahead for it is still required (red-team R2).

## Criteria

| # | Criterion (brief) | Status | Evidence (file:line at 70a06284) |
|---|---|---|---|
| 1 | All new options absent: every existing stage byte-identical to 8d1bee3a / b5b41d90 | **met** | Only `run_gate_m4.py` and `gate_driver.py` changed among existing modules (`git diff --name-status b5b41d90 70a06284 -- exp_p2`). Auditor re-check after the r1 edits: 20 tests pass. They compare `process()` rows and arrays with both base revisions, for 3 option sets and 3 fold shapes (M4 300+200, H 300, small), each module with its own ctx. `ctx.fold` (`run_gate_m4.py:166`) equals the old `test_items(f, 500)` for every fold file in use (folds.json 300+200; H 300+0). The driver tables, `default_n`, `build_cmd` and `resolve_max_chunks` (=12) are unchanged for every old stage. The default config gets no A6 keys (`run_gate_m4.py:320-322`). |
| 2 | Fixed caption slot (`--layout-fix/--caption-slot-len 13`) computes exactly A6 r1's caption-withheld features, with Delta unchanged; the invariance gate (tolerance 1e-6) is implemented | **partly** | **Features: met.**<br>- B, s3 and D come from `gate_scores(sc, gate_tok, ...)` (`run_gate_m4.py:217, 242`), and tbv from `sc.build(gate_tok, codes)` (`:254`), with `gate_tok = [0]*13`.<br>- Every one of these passes masks the caption: `scores.py:30` (`extra=cap`), `scores.py:95`, and D from the layout-only cache `DI_n013` (`pipeline.py:34`, `dcache.py:63-65`).<br>- Delta, tex and nbr are unchanged (`:228`, `:247-248`).<br>- Train/test parity: the auditor checked that the runner's slot features equal the re-score stage's for the same codes (pass).<br>- GATE-M at L_FIX is the default, which matches A6.4; `--gate-true-layout` stays an unused option.<br>**Gate: partly.**<br>- Invariance (c+, c- or PAD in the slot) and the positive control (true length vs stored M4, 1e-5) are computed on items 0-4 and written into the rows (`run_gate_lrf_rescore.py:101-109`).<br>- But nothing enforces them: the stage goes on through all 500 items, and nothing stops a re-freeze when `checks_ok` is false.<br>- The 1e-6 auditor path exists only as a comment (`:40`). |
| 3 | Re-score stage; re-freeze procedure and its clock rule (no re-frozen accuracy before the hash commit; object commit by Mon 09:00 IST); no fallback to ca5c4e2f | **missing** | **Re-score stage: met** apart from F3 and F6. It reads stored codes and does not re-encode. It copies codes, z, delta, tex and nbr, and re-scores B, s3, D and tbv at the fixed slot. Flags use the source condition index (`:81-112`). The input hashes go into `config.json` (`:154-157`).<br>**Re-freeze: no code.**<br>- `lrf.py --freeze` is unchanged (diff empty since 91f78475).<br>- It reads `run.ARR = runs/P2-GATE-M4/arrays` (`run.py:35`), not the re-scored arrays.<br>- It writes into `FROZEN = runs/P2-LRF-FROZEN` (`lrf.py:32`), overwriting the committed retired object.<br>- It writes `freeze_check.json` with `insample_accuracy` and prints it (`lrf.py:137-143`). That breaks A6.2 step 4 ("no accuracy ... computed or opened before its hash set is committed").<br>- Its spec text claims the true-caption layout (`lrf.py:121`).<br>**Clock rule:** not in code (no start bound for re-score, L1 or LG; no check that the object commit precedes T_RF or the fold commit). Acceptable as process, but see R1.<br>**Fallback:** no default points at ca5c4e2f (`lrf_score.py:37`), but nothing refuses it either. `--frozen-dir runs/P2-LRF-FROZEN` scores it with exit 0 (auditor check), and the docstring still names that directory (`lrf_score.py:3-5`). |
| 4 | Fresh-fold builder (disjoint from every pool; L0-L8; determinism), equal-length negative, extra cells shot/impulse/speckle severity 3 with a parity proof | **met** | **Fold builder:**<br>- Union exclusions come from every `runs/P2-*/**/{items.jsonl, selection.json, pool.json, folds*.json}` plus all SugarCrepe images (SHA-verified) and the FOIL pool (`build_lrf_fold.py:231-304`). The manifest lists every file (`:342`).<br>- Auditor scan of the main worktree's `runs/P2-*` (S2, H and LRF directories not opened): every image id in an undiscovered json/jsonl (FOIL leak/L7 files, CPU dry run, suite smoke, denoise_check config) is already in the discovered union (0 outside).<br>- Leak checks L0-L7 (`:136-187`), L8 injected-leak self-test (`:190-222`), refusal to overwrite (`:317`), seed stream `[SEED_GATE, 10]` (`:40`; tested unused elsewhere). Determinism and prefix property are tested (`test_gate_build_lrf_fold.py:60, 211`).<br>**Equal-length negative:** exact token count where possible, else the smallest difference; category-disjoint; recorded (`:58-73`). L-LEN exactness is re-derived from the runner's tokens in the scorer (`lrf_score.py:265-266`).<br>**Extra cells:** appended last, so no condition index moves; seed `corruption_seed(gid, 1000+10*type+sev)` (`run_gate_m4.py:46, 193`); no text passes (`:270`); package commit verified at load (`suite.py:73-82`). Parity proof: the same pixels through the family path and through the extra-cell path give equal arrays (12 keys), and existing cells are byte-identical with extras on (`test_gate_a6_options.py:171-198`). |
| 5 | LRF scorer: hash pins (frozen model, codebook ff15b9b5..., DI_n013 f7744253...); non-finite = error | **partly** | **Codebook and DI_n013: met.** Hashed on disk against the r1 constants and against the run's `config.json` (`lrf_score.py:55-58, 124-142`). data.py and families.py are pinned by default; lrf.py is pinned via spec.<br>**Non-finite: met.** Errors on raw features, engineered features, weights, Delta, DeltaL, score, margin and all-zero weights (`:150-191, 210-211`). CLI exit 2, nothing written (`:306-308`). Auditor failure-path script: 12 cases, all stop.<br>**Model hash: partly.**<br>- Without `--pins` the re-frozen `model.npz` is checked only against its own `spec.json` (same directory).<br>- `spec.json` itself is not hashed.<br>- The scoring entry-point hashes are recorded but not verified (`:145-146, 309`).<br>- `pinned_externally` is reported `true` whenever the default pins exist, even with no pins file (`:108, 300`). |
| 6 | A6 analysis: L1 one-sided exact McNemar; p <= 0.025 headline flag; secondaries and Holm; clean NI margin; branch labels A-D; no rescue | **met** (one item for the statistician, S-1) | Details:<br>- L1: exact one-sided test, rejected iff p <= 0.05 and b > c (`a6_analysis.py:104-116, 176-180`); `headline_p_le_0025` (`:179`).<br>- L3/L4: two-sided, Holm m = 2, gatekept by L1 (`:183-198`).<br>- L-NI: 90% paired bootstrap lower bound > -0.03, with the C6-11 margin note (`:200-205`).<br>- L-LEN: non-exact items excluded and counted (`:209-215`).<br>- LG: one-sided, Holm over the preregistered m = 3, absent cell = p 1, n < 240 descriptive, C6-11 wording (`:263-299, 309`).<br>- Branch from L1 only (`:150-159`); GATE-M is a descriptive supplement with no LRF number (`:224-231`).<br>- Seeds `SeedSequence(20261028, spawn_key=(34,))`, 10,000 resamples; byte-identical rerun tested. Self-test ok (size 0.040 and 0.042).<br>- No rescue: nothing but L1 sets the branch. Text placement is outside code. |
| 7 | Driver stages `lrf-rescore`, `lrf-l1`, `lrf-lg` | **met** (F6 on the run id) | `gate_driver.py:68-90, 117-126`:<br>- arguments as in A6.11 item 3, except `--tbv on` (ruling 3 below);<br>- `lrf-l1` n from the committed plan's `n_rule.test_fold`, and `run_gate_m4` refuses any other n;<br>- `lrf-lg` takes the first 300 items with an empty family plus three cells;<br>- explicit max-chunks for these stages only; existing refusals (hold, dirty tree, battery, event log, pin) apply.<br>Tests parse every launched command with the runner's own argparse. |
| 8 | CLIP/SigLIP script descriptive only and offline-forced | **met** | Hub switched off and `local_files_only` unless `--download-approved` (`baselines.py:146-174`). Pinned revisions (`:33-34`). Own table: accuracy and own clean-to-corrupted drop with bootstrap CI. No p-value and no LRF or UniDisc number (`:244-245`). Parity rule 0.98 (`:36`). Network blocked in the test (`test_gate_a6_r1.py:254`). There is no guard against running during a GPU stage (R5). |

## Required fixes (before the stage each one gates)

- **F1 (scorer pins; before L1 scoring).**
  - `lrf_score` must refuse unless a pins file (the A6.0 item 2 row) gives `model_sha256`. It should also give `spec.json`'s sha, `lrf.py`'s sha and the entry-point shas, and all of them must be verified at start.
  - Refuse model sha `ca5c4e2fc5c6635a051a7c3a11f7b9e555fe9f6e2ce329825a80cb9b4bca1e65` explicitly (D0083), and refuse a spec whose layout field is not L_FIX = 13.
  - Set `pinned_externally` only when a pins file was given.
  - Fix the stale docstring (`lrf_score.py:3-5`).
  - Tests for each refusal.
- **F2 (re-freeze entry; before the re-freeze).** An audited entry, either a new module or `lrf.py` options (its hash then changes, which A6.2 allows "recorded in the row"). It must:
  - read the re-scored arrays directory;
  - write only `runs/P2-LRF-FROZEN-LFIX/` (model, spec, hpo), refuse to overwrite, and never touch `runs/P2-LRF-FROZEN`;
  - keep the protocol identical: same `successive_halving`, `inner_folds`, `ss` keys, `FROZEN_KEY` 99, F1 settings, refit on all 500 x 4;
  - compute and print **no accuracy**. The numpy-vs-torch weight self-check may stay; `insample_accuracy` and `none_accuracy` must not be computed until the hash commit exists;
  - record L_FIX = 13, the source run and the hashes of `run.py` and the re-scored arrays in the spec;
  - refuse unless the re-score rows of items 0-4 hold all 4 conditions with invariance 0 (or <= 1e-6 with an auditor row id given on the command line) and positive control <= 1e-5;
  - be shown by a parity test on fake arrays to produce the same model as `freeze()` with the paths swapped.
- **F3 (invariance gate enforced; before the re-score starts).** The re-score stage stops (non-zero exit, no further items) when item 0-4 fails invariance (> 0) or the positive control (> 1e-5). Add a `--check` that reads the rows and returns pass or fail, used by F2. Test it.
- **F4 (cross-fit entry for the n-rule; before the n-rule record).**
  - A CPU entry with the learned-ceiling protocol (5 outer and 3 inner folds, the same seed keys and HPO), F1 only, reading the re-scored arrays and writing `runs/P2-LRF-CF-LFIX/results.json`: noise0.1 b, c, n, `delta_cf`, `pi_cf`, input hashes. Today `run.py:35-36` hard-codes the old arrays and would write into `runs/P2-POSTHOC-LEARNED`.
  - `lrf_nrule --cf-results` reads that file and records its sha; numbers are not typed by hand.
  - Until both exist and pass audit, only `lrf_nrule --not-committed` (n_L = 520) is usable.
- **F5 (plan files; before L1/LG).**
  - Code that writes `runs/P2-LRF-PLAN/family.json` (endpoint d, family copied from the committed `runs/P2-GATE-M3/family.json`, `n_rule.test_fold` = n_L read from the committed n-rule record) and `runs/P2-LRF-PLAN-LG/family.json` (endpoint d, empty family, test_fold 300).
  - It refuses to overwrite, and a test checks that n_L agrees between the n-rule record, the plan file and `a6_analysis --n-rule`.
  - Today these files are hand-written inputs that set both the conditions and n.
- **F6 (run id; before the re-score starts).** Use the SAP's name `runs/P2-LRF-RESCORE` (`run_gate_lrf_rescore.py:34`, `gate_driver.py:77`).

Smaller fixes (with the same commit):
- `a6_analysis` should refuse to run without `--n-rule` or `--n-l` instead of defaulting to 520 (`:35, 370`).
- Stale "A6 (DRAFT)" references: `run_gate_lrf_rescore.py:43` (written into `config.json`) and `build_lrf_fold.py:1`.
- "held-out noise cells" in the `a6_analysis.py:13` docstring (C6-11 wording).

## Recommended (not blocking)

- **R1.** Clock bounds in code, as `h3_gonogo` does for A5: refuse `lrf-rescore` after Mon 2 Nov 04:15 IST, `lrf-l1` after 11:12, `lrf-lg` after 13:15. `lrf-l1` should also refuse unless the object commit (model and spec tracked) is dated <= Mon 09:00 IST and precedes the fold commit.
- **R2.** Run the re-score and L1/LG self-checks under `run_gate_s2.deterministic_cudnn()`. The S2 diagnosis showed that the plain self-check varies by process (0.985 to 1.0); a spurious exit 2 costs clock time. This does not change any measurement path.
- **R3.** Pin `analysis_posthoc/learned_ceiling/run.py`, which supplies the HPO functions of the freeze, in the A6.0 item 2 hash set.
- **R4.** Add an explicit check of `config.json` `caption_slot_len == 13` in the scorer. Today it is implied by the DI_n013 hash match.
- **R5.** The baseline script should refuse while a `gate_driver` stage is running (A6.6 "never run during a GPU stage").

## Rulings on the implementer's four ambiguities

1. **Run directory name.** SAP A6.2 step 1 governs: `runs/P2-LRF-RESCORE`. The re-freeze row, the hash set and the disclosure will cite the SAP's name, and nothing argues for `P2-GATE-M4-LFIX`, which also sits inside the `P2-GATE-*` namespace of Study 1. This is fix F6.
2. **Holm m = 2 vs 3.** There is no conflict. A6.4 governs the procedure: L1 is the gatekeeper at 0.05, then Holm over {L3, L4} with m = 2. The "m = 3" in the r1 table, in A6.7 and in C6-3 counts the hypotheses in family L, which drops from 4 to 3 when L2 is removed. This serial gatekeeping keeps the family-wise error at 0.05. The code (`a6_analysis.py:190-196`) is correct, and no dated clarification is required.
   - **S-1 (does need the statistician).** The rule for a partial prefix that rejects with one-sided p <= 0.025 is not settled. A6.4 says "rejection stands"; A6.12 lists only "partial and not rejected" under C. The code puts such a result in branch B (`a6_analysis.py:155-158`), which is the stricter reading. The statistician must issue a dated clarification (A or B) before the first L item; until then the code's B stands as the safe default.
3. **`--tbv on` vs `auto`.** `--tbv on` is accepted. In the main worktree `auto` resolves to on: `runs/P2-GATE-M1/tbv_verdict.json` is tracked, with `copy_suspected` false, and `run_gate_m4.py` `tbv_enabled` reads it. So the outputs are identical. `on` also fails closed where the verdict is missing, whereas `auto` would drop a required LRF input silently and the scorer would stop only after hours on the GPU. The lead records the reading in the pin row; no SAP change is needed.
4. **Missing cross-fit code for delta_cf / pi_cf.** Before the n-rule runs, the following must exist, be audited and be committed:
   - the F4 entry point;
   - its `results.json` for noise0.1: b, c, n = 500, `delta_cf` = (b - c)/500 for F1 (= SEL, since only F1 is fitted) against NONE, `pi_cf` = (b + c)/500, plus input hashes;
   - `lrf_nrule --cf-results` reading it.

   Hand-typed `--delta-cf/--pi-cf` values are not acceptable for the record. If the results file is not committed by Mon 2 Nov 10:00 IST, the rule's own fallback applies (`--not-committed`, n_L = 520), and that path already exists and is tested. A one-line statistician note that "SEL minus NONE" means F1 minus NONE under F1-only is advisable but not blocking.

## Checks run (commands and artifacts)

- **Full suite.** In the audited worktree: `..\..\..\.venv\Scripts\python.exe -m pytest tests/exp_p2 -q -p no:cacheprovider`, at BelowNormal process priority. Result: **779 passed, 5 skipped, 346 s**. Logs: `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\pytest_full.out`. The new A6 files alone (`-rs`): 84 passed, 0 skipped. The run stayed under 7 minutes, so the whole suite was run, not a sample.
- **Auditor byte-identity and parity tests.** `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\audit_a6\test_audit_byte_identity.py`: 20 passed (75 s).
- **Scorer failure paths.** `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\audit_a6\nan_path_check.py`. It uses synthetic items, the ca5c4e2f object only as a weight container, and copies of the pinned `codebook.npy` and `DI_n013.npy`; it writes only in the scratchpad.
- **Exclusion coverage.** `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\audit_a6\exclusion_scan.py`. It skips S2, H3, H4, HARDNEG and LRF directories.
- **Hashes (sha256).** The blobs of `data.py`, `families.py` and `lrf.py` at 70a06284 equal the A6.2 table (14421ffb, 1c49827d, 03ed472e). The CRLF checkout differs in raw bytes; the scorer accepts LF-normalised files and has a test for it. The main worktree's `codebook.npy` (ff15b9b5...), `DI_n013.npy` (f7744253...) and `P2-LRF-FROZEN/model.npz` (ca5c4e2f...) match.
- **n-rule power.** It reproduces Appendix A6: 0.730 and 0.863 at n 520; at n 533, 0.74 and 0.63 at Delta 0.05 and 0.87 and 0.79 at 0.06. The rule clamps correctly: Delta 0.102 gives 533; Delta 0.30 with pi 0.40 gives 400; Delta <= 0.02 gives 533.

---

## Delta F1-F6 (2026-10-29, 16:58 IST): PASS WITH FIXES at `fe1fce2c`

**Audited SHA:** `fe1fce2c` (branch `worktree-agent-aec5b3a0e0fa71ebc`, clean tree; merges `704042f5`, SAP A6 r2). Scope: `git diff 70a06284 fe1fce2c -- exp_p2 tools tests analysis` (14 files; nothing under `tools/` or `analysis_posthoc/` changed), checked against F1-F6 above, SAP A6 r1 + r2 and the implementer's addendum 3 (`research/paper2/method/IMPL-K-A6-LRF-2026-10-29.md` lines 156-175). No S2, H or new-run output was opened. No code edited, nothing committed, no ledger rows added.

**Verdict.** No criterion is `missing`; two are `partly`. The code may be used for each stage only after the fix that gates that stage (D1 before `lrf-rescore`, D2 before `crossfit`) has landed. A narrow gate-auditor check of each fix is enough (the scratch test below, inverted, plus a refusal test for D2); a full re-audit is not needed.

| Fix | Status | Evidence (file:line at fe1fce2c) |
|---|---|---|
| F1 scorer pins | **met** | `--pins` is required and must give `model_sha256` (`lrf_score.py:324-328`). Retired `ca5c4e2f` refused with or without pins (`:61, 93-94`). A spec with `caption_slot_len` != 13 is refused (`:97`). The optional pin keys are each verified when given: `spec_sha256`, `code_sha256`, `scoring_code_sha256`, `entry_points`, `decision_rule` (`:114-133`). `pinned_externally` is true only if the model hash was verified (`:135`); the meta lists `pins_verified`. Docstring and default `--frozen-dir` now name `P2-LRF-FROZEN-LFIX` (`:3-14, 41`). Auditor check on the real committed `runs/P2-LRF-FROZEN` (main worktree): refused by `load_frozen` without pins and with the retired hash pinned; the CLI without `--pins` exits 2. |
| F2 re-freeze entry | **met** | `analysis/paper2/lrf/refreeze.py`. It reads only `--src` (default `P2-LRF-RESCORE`) and writes a new `P2-LRF-FROZEN-LFIX`. It refuses an existing output, the retired directory and any path inside the source (`:58-70`), and refuses unless `check_rows` passes and all 500 arrays exist. The protocol calls the unchanged `run.successive_halving`, `ss(7)` mask, `FROZEN_KEY` 99, F1GAM(40, 9) and final seed `ss(4,99,0,0)` (`:80-86`), the same calls as `lrf.freeze()` (`lrf.py:87-104`). The parity test against `lrf.freeze()` with the paths swapped passes (`test_gate_a6_fixes.py:153`). No `insample_accuracy`, `none_accuracy`, `freeze_check.json` or `insample_weights.npz`; the `acc` entries are popped from the HPO log (`:91-92`). The printed line holds hashes and the numpy-vs-torch weight difference only (`:121`). The spec records L_FIX, the source run, the arrays digest, the rescore config sha and the shas of data/families/lrf/run.py and of refreeze.py (`:104-107`). |
| F3 gate enforced | **partly** | Met in part:<br>- `ChecksFailed` is raised before the failing item writes a row or arrays (`run_gate_lrf_rescore.py:146-150`), and the runner logs `item_error` and re-raises, so the chunk exits non-zero (`runner.py:199-201`).<br>- `--check` and `check_rows` behave as specified (`:80-109, 210-213`), with 1e-6 only under `--auditor-row`.<br>**Gap (D1):** the failure is not sticky. `gate_driver` relaunches after any non-guard, non-hold exit and stops only after two chunks without progress (`gate_driver.py:230-252`). The relaunch re-runs the failing item. If the check passes on retry (arithmetic non-determinism), the stage completes, and `check_rows` (which reads only `items.jsonl`) reports ok even though a `ChecksFailed` event is on record. Auditor test `audit_a6/test_delta_f3_retry.py`: chunk 0 raised at item 2; the relaunch returned 0 with 6 rows and `check_rows` ok. A6.2 step 3 says a larger difference "stops Study 2", so this breaks it. |
| F4 cross-fit + n-rule | **partly** | The protocol is conformant:<br>- `crossfit.folds(500)` equals `run.outer_folds()` (tested), fi = 0 as in the learned-ceiling `main`, the checkpoints come from the unchanged `run.run_family_fold`, and `run.OUT` and `N_ITEMS` are restored in `finally` (`crossfit.py:59-70`).<br>- NONE is `delta.mean(-1) > 0`, as in `run.analyse`. b, c, `delta_cf` = (b-c)/n and `pi_cf` = (b+c)/n are for noise0.1 only (`:71-76`), with input hashes and refusal to overwrite `results.json`.<br>- `lrf_nrule --cf-results` reads the file, checks `delta_cf` and `pi_cf` against b, c, n, and records its sha. `--out` with hand-typed values is refused (`lrf_nrule.py:53-65, 88-90`); `--not-committed` gives 520.<br>**Gap (D2):** A6.10 places the cross-fit after the object commit, and the cross-fit computes the L_FIX protocol's out-of-fold accuracy contrast on M4. Nothing stops it from running before `P2-LRF-FROZEN-LFIX` is committed, and an early run leaves no git trace (git order is A6.0's evidence). |
| F5 plan files | **met** | `exp_p2/gate/lrf_plan.py`. L1 plan: endpoint d, the M3 family, which must equal P's three operating points in order (`:36-41`; the committed `runs/P2-GATE-M3/family.json` matches), and `test_fold` = n_L from the n-rule record (400-533). LG plan: an empty family with `test_fold` 300. It refuses to overwrite (`:66-69`), records input shas, and `check_consistent` ties n_L across the n-rule record, the plan, the driver and `a6_analysis --n-rule` (tested). `run_gate_m4.load_prereqs`/`check_n_against_rule` read exactly `endpoint`, `family[].corruption/severity` and `n_rule.test_fold`. |
| F6 run id | **met** | `P2-LRF-RESCORE` in `run_gate_lrf_rescore.py:34` and `gate_driver.py:77`. `git grep M4-LFIX fe1fce2c -- exp_p2 analysis tools tests analysis_posthoc` finds only the negative assertion in the test. |
| Smaller fixes | **met** (one cosmetic) | `a6_analysis` refuses without `--n-rule`/`--n-l` (`:370-372`), and "DRAFT" is removed. The LG docstring now repeats itself: "(shot, impulse, speckle; severity 3) (shot, impulse, speckle at severity 3)" (`a6_analysis.py:13`). |
| Byte-identity, all new options absent | **met** | `run_gate_m4.py` is unchanged since 70a06284. The predecessor's 20 checks were re-run at fe1fce2c (rows and arrays against b5b41d90 and 8d1bee3a, 3 option sets x 3 fold shapes, the driver tables of every old stage, runner/re-score feature parity): **20 passed**. |

**Ruling on `inner_cv_o1` (A6.2 step 4): allowed.**
- Step 4 bars "accuracy of the re-frozen model". `inner_cv_o1` is the mean O1 surrogate loss of the selected configuration on inner validation folds. It is neither an accuracy nor a quantity of the re-frozen (all-items) model.
- It is the protocol's own selection criterion (`run.py:90-97`). Step 4 requires that protocol "unchanged", and the first freeze recorded the same field.
- `refreeze.py` does not print it.
- Conditions:
  - it and the per-config `o1` in `hpo.json` are never quoted as performance (C6-8);
  - the A6.0 item 2 row cites hashes only;
  - the object commit is unconditional (only the A6.10 clock can stop it).

**Required fixes (small; code only):**
- **D1 (F3; before `lrf-rescore` starts).** Make a check failure terminal.
  - `check_rows` must return not ok if the run's `chunks.jsonl` has any `item_error` naming `ChecksFailed`.
  - The stage must refuse to start or resume a run with such an event, with an exit in `REFUSAL_EXITS`, so the driver stops after the "no progress" rule instead of retrying.
  - A re-run is a new run id beside the original (card v3 section 17).
  - Test: `test_delta_f3_retry.py` with its final assertion inverted.
- **D2 (F4; before `crossfit` runs).** `crossfit` must refuse unless `runs/P2-LRF-FROZEN-LFIX/model.npz` and `spec.json` are tracked at HEAD and match the working files, and it must record that commit SHA in `results.json`. Test the refusal.

**Recommended (not blocking):**
- `--auditor-row` should be validated against an existing dated ledger row and copied into the re-freeze spec. Today any string is accepted, and the spec keeps only `inv_tol`.
- `crossfit` should write its input digest into the output at start and refuse stale `ckpt/` files from another source. Today it resumes any existing `F1_fold*.npz`.
- `from_cf_results` should also check `protocol.family == "F1"`, `n == 500` and `inputs.source_run == "P2-LRF-RESCORE"`.
- The scorer should require `spec_sha256` and `entry_points` in the pins file, not only verify them when present.
- Fix the duplicated LG docstring.
- **R2 carries more weight now.** A6.2 step 3 names deterministic cuDNN for the invariance check, and no code on this path sets it (no `cudnn`/`deterministic` in `run_gate_lrf_rescore.py`, `runner.py`, `scoring.py`). With D1 a transient difference becomes a Study 2 stop, so run the stage under `run_gate_s2.deterministic_cudnn()`.

**Checks run:**
- **Full suite.** `tests/exp_p2` at fe1fce2c, BelowNormal priority: **799 passed, 5 skipped** (`test_omni_stack.py`, module not available, as before), 438 s. That is just over the 7-minute guide; the whole suite was run, not a sample. Log: `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\pytest_full_delta.out`.
- **Auditor tests.** `...\scratchpad\audit_a6\test_audit_byte_identity.py` (20 passed) and `...\scratchpad\audit_a6\test_delta_f3_retry.py` (it passes, which demonstrates the gap): 21 passed in 70 s. Log: `...\scratchpad\delta_audit_scratch.out`.
- **Retired-object refusal.** A CLI and `load_frozen` check on the main worktree's `runs/P2-LRF-FROZEN` (hash comparison only; no item scored).
