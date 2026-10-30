```yaml
agent: gate-auditor
date: 2026-10-30
brief: Audit of Paper 2 Study 2 family LG (shot_noise3, impulse_noise3, speckle_noise3 vs NONE, Holm m = 3) against SAP addendum A6 (A6.0, A6.5, A6.8, A6.12) and card v4 section 9 (code pin 1871fe7d)
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/GATE-AUDIT-FAMILY-L-2026-10-30.md (method reused)
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md lines 58-68, 186-309 (A6.4, A6.5, A6.7, A6.8, A6.10, A6.11, A6.12)
  - research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md section 9 rows A-6 to A-8
  - git log (ISO times) and diffs for 1871fe7d, 98724fb8, 602261b5, 9fcb142d, a430b24d, 4a01f896
  - runs/P2-LRF-LG/{config,selfcheck,items.jsonl,chunks.jsonl,token_exclusions,arrays_manifest,arrays/*,predictions.jsonl,lrf_score_meta,a6_analysis,env-lock}; runs/P2-LRF-LG.driver.out and stdout-chunk05.log (tail only)
  - runs/P2-LRF-PLAN-LG/family.json; runs/P2-LRF-FOLD/folds_lrf.json; runs/P2-LRF-PINS/pins.json (via the scorer); runs/P2-LRF-L1/{a6_analysis,predictions}.json* (family_L comparison; unchanged since 4a01f896)
  - research/ledgers/experiments.jsonl X0005, X0006; research/paper2/CONFIRM-EVENING-2026-10-28.md lines 196-201
  - .venv imagecorruptions-1.1.2.dist-info/direct_url.json (read only)
coverage: >
  Not opened: runs/P2-LRF-BASELINES (per brief). No torch/CUDA use for audit work (CUDA_VISIBLE_DEVICES empty; the scorer imports torch for its own CPU checks, no GPU touched).
  Not re-verified: the frozen object itself (only its committed hash set via pins), the A6 code audit bodies, the imagecorruptions pixels (the shot/impulse/speckle
  corruption outputs are not regenerated here; the installed commit was read from direct_url.json after the run, not at run time), the L1 and baselines results beyond the
  family_L equality check. "No LG output was read before the run completed" rests on the ops log (lines 197-200) and stdout logs; it cannot be proven from git.
  Not done: clean-clone rebuild from a lock file (the env-lock.txt files are empty, see finding F3); this belongs to the release gate.
claims:
  - statement: "LG ran at the pinned code, after the L1 analysis commit, on the first 300 committed fold items in order, with the three severity-3 cells, selfcheck 0.99 passed, 300/300 rows and no guard stop"
    status: supported
    evidence: "git diff --quiet 1871fe7d 98724fb8 -- exp_p2 tools tests rc 0 (also vs HEAD rc 0); 4a01f896 23:58:29 < launch 00:00:05 < first chunk_start t=1793298642 (about 00:00:41); items.jsonl == folds_lrf.json test[0:300] by (image_id, gid), idx 0..299, gid 8000..8299; selfcheck image_tokens_frac_equal 0.99902"
    level: E4
    confidence: 0.95
  - statement: "Predictions and the A6 analysis regenerate byte-identically; positive control 1200/1200; all three LG cells are rejected with b > c under Holm m = 3; the all-three rule holds; family_L equals the L1 output"
    status: supported
    evidence: "scratch reruns (SHA-256 a4626d78... for predictions) and independent recomputation, sections 3 and 4"
    level: E4
    confidence: 0.95
  - statement: "X0006 and the ops-log line report the numbers correctly"
    status: supported
    evidence: "section 4 table"
    level: E4
    confidence: 0.97
competing_explanations: []
unknowns:
  - "Whether any LG accuracy was seen mid-run: not provable from git; the ops log and stdout logs contain only progress and resource figures"
  - "Whether the installed imagecorruptions at run time was c959e659: env-lock.txt is empty, so this rests on the venv's direct_url.json read after the run and on the unchanged venv"
next_test: {hypothesis: n/a (audit), intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Gate audit: Study 2 family LG (other noise types), 2026-10-30

## VERDICT: PASS WITH FIXES

No criterion is `missing` or `partly`. Every number in `runs/P2-LRF-LG/a6_analysis.json`, ledger X0006 and the ops-log line reproduces byte-for-byte and from an
independent recomputation. The fixes are administrative; none changes a number or a label. I did not edit `progress.md`, the ledgers or any run file (one report file only).
Ledger rows added: 0.

## 1. Run conditions (A6.0, A6.5, A6.10): PASS

| Criterion | Evidence | Status |
|---|---|---|
| Code at pin 1871fe7d | `git diff --quiet 1871fe7d 98724fb8 -- exp_p2 tools tests` exit 0; same against HEAD exit 0. `config.json` git_sha 4b7c1f8c (the pre-launch ops-log commit; code identical) | met |
| Started after the L1 analysis commit | 4a01f896 23:58:29 (L1 analysis), 6dc08b4d 23:58:58 (ledger), 4b7c1f8c 23:59:40; `driver.out` launch 00:00:05; first `chunk_start` t = 1793298642.6 (L1's first chunk was 1793289885.85 = 21:34:45, offset +8756.8 s = 00:00:41) | met |
| Order and clock (A6.10 item 5: after L1, by Mon 13:15) | LG launched about 2 min after L1 analysis, about 61 h before the bound; order depends on time only | met |
| Family file | `runs/P2-LRF-PLAN-LG/family.json`: `family` [], `test_fold` 300, rule "SAP A6 r1 A6.5: the first 300 items"; committed 693fbe46 (2026-10-29 21:16:50), before any L item | met |
| Items | `items.jsonl` 300 rows, idx 0..299 unique; (image_id, gid) of every row equals `folds_lrf.json` test[0:300] in order (gid 8000..8299); every row has conds clean, shot_noise3, impulse_noise3, speckle_noise3, `slot_len` 13, `n_rows` 42, `gate_layout` fixed | met |
| Cells and package | `config.json` `extra_cells` "shot_noise3,impulse_noise3,speckle_noise3"; `run_gate_m4.py` 46-48: cell index fixed by kind and severity, not by position; venv `imagecorruptions-1.1.2.dist-info/direct_url.json` commit c959e659c9713837d2acd7ce785a81202d4be799 = A6.5 line 200 and `suite.py` PACKAGE | met (see unknown) |
| Fold, codebook, DI, config | `config.json` folds_path runs/P2-LRF-FOLD/folds_lrf.json (sha a545a83e..., CRLF form, as in the family L report fix 3); caption_slot_len 13; codebook ff15b9b5...; DI_n013.npy f7744253...; both equal the A6.2 table | met |
| Self-check | `selfcheck.json`: ids_equal true, modality_equal true, `image_tokens_frac_equal` 0.99902 (>= 0.99); n_cap 14 | met |
| Completion | `chunks.jsonl`: 6 chunk_start, 5 soft_deadline, 1 complete, no guard-stop event; `driver.out`: chunk exits 75 x5 then 0, rows 0 -> 7 -> 75 -> 143 -> 210 -> 277 -> 300, COMPLETE 00:58:48; `token_exclusions.json` zero exclusions (and tracked, so family L fix 2 is applied) | met |
| Run before predictions before analysis before ledger | 98724fb8 00:59:31 -> 602261b5 00:59:55 -> 9fcb142d 00:59:57 -> a430b24d 01:00:27; pins fdfd8b97 22:42:54 precede all | met |

L1 outputs were not touched: `git diff --quiet 4a01f896 HEAD -- runs/P2-LRF-L1/a6_analysis.json runs/P2-LRF-L1/predictions.jsonl` exit 0.

## 2. Arrays: PASS

300 files in `runs/P2-LRF-LG/arrays/` re-hashed with SHA-256 against `arrays_manifest.json`: 0 mismatches; manifest names equal the files on disk (300 = 300).

## 3. Regeneration: PASS (byte-identical)

Scratch directory `C:\Users\ANONYMIZED\AppData\Local\Temp\claude\C--Users-ANONYMIZED-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\f9e01f26-3b7f-40af-a381-11d4b248c68b\scratchpad\auditLG\`.
- `python -m exp_p2.gate.lrf_score --run-id P2-LRF-LG --pins runs/P2-LRF-PINS/pins.json --n 300 --conds clean,shot_noise3,impulse_noise3,speckle_noise3 --crosscheck --out <scratch>/pred.jsonl`:
  rc 0; 1,200 lines; positive control n_checked 1200, ok true; `pins_verified` lists all eleven items; `cmp` identical to `runs/P2-LRF-LG/predictions.jsonl`; SHA-256
  a4626d783ce8f572a71f88afdffa09d14aa39d8ff8a046f449047b40146d33ef for both (equals `lrf_score_meta.json` `predictions_sha256`). The scorer wrote its meta to the scratch folder, not the repo.
- `python -m analysis.paper2.lrf.a6_analysis --l1 runs/P2-LRF-L1/predictions.jsonl --lg <scratch>/pred.jsonl --n-rule runs/P2-LRF-PLAN/n_rule.json --out <scratch>/a6.json`:
  `cmp` identical to `runs/P2-LRF-LG/a6_analysis.json` (L1 "confirmed", branch "A"). `git status` shows no tracked file changed by my runs.

## 4. Independent recomputation from raw predictions: PASS

My own code (stdlib exact binomial, numpy bootstrap with a different seed), reading only `predictions.jsonl`, y_lrf against y_none, one-sided exact McNemar, Holm over the three cells:

| Cell | b | c | n | acc LRF | acc NONE | net | one-sided p (mine) | Holm p (mine) | JSON Holm p | 95% CI mine / JSON | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| shot_noise3 | 43 | 15 | 300 | 0.7667 | 0.6733 | +0.0933 | 0.000153474 | 0.000460421 | 0.00046042 | +4.7 to +14.3 / same | rejected, b > c |
| speckle_noise3 | 32 | 14 | 300 | 0.7567 | 0.6967 | +0.0600 | 0.005675796 | 0.011351591 | 0.01135159 | +1.7 to +10.3 / same | rejected, b > c |
| impulse_noise3 | 35 | 20 | 300 | 0.7500 | 0.7000 | +0.0500 | 0.029032073 | 0.029032073 | 0.02903207 | 0.0 to +10.0 / same | rejected, b > c (Holm 0.029 <= 0.05) |

- All-three rule (every cell Holm <= 0.05 with b > c): true; `all_three_rejected_with_b_gt_c` true in the JSON; `harm` false in every cell; `n_cells_present` 3, `m_preregistered` 3.
- `family_L` in the LG output equals `family_L` in `runs/P2-LRF-L1/a6_analysis.json` (Python dict equality, true; L1 b 58, c 27, branch A unchanged).
- Ledger X0006 ("shot b 43 c 15 Holm p 0.00046; speckle b 32 c 14 Holm p 0.011; impulse b 35 c 20 Holm p 0.029 (n 300 each); family L identical to 4a01f896") and the ops-log line at
  CONFIRM-EVENING-2026-10-28.md line 200 (same figures, "all three LG cells rejected with b > c") match exactly. Both still say "Gate-auditor verdict pending" (fix F1).
- Facts the writer needs from the JSON: impulse two-sided p 0.0581 (`passes_two_sided_005` false; shot 0.0003 and speckle 0.0114 pass); impulse 95% CI lower bound is 0.0, so
  "the interval excludes zero" is false for impulse at 95% (the 90% CI is +1.0 to +9.0). Clean-to-corrupted drop of NONE (descriptive): shot 0.217, speckle 0.193, impulse 0.190.
  The `descriptive_gatem_vs_none` block (shot net +0.007, impulse +0.003, speckle 0.000) is supplement-only.

## 5. What the result binds (SAP-ADDENDUM-A6-LRF-2026-10-29.md line refs; branch A, L1 confirmed at p 0.00051)

Allowed:
- Results section only, "per cell, with Holm-adjusted p" (line 295), using the C6-11 wording (line 66; line 200-203). The exact phrase is
  **"other noise types (shot, impulse, speckle; imagecorruptions severity 3)"**. Since all three cells were rejected the sentence may name all three (line 204-205: with fewer than three
  rejections only the rejected types are named; not triggered here). Report n 300 per cell, b, c, accuracies, net with 95% CI, the exact one-sided p and Holm p, the
  preregistered one-sided alpha 0.05 (line 224), the family count of 17 with "no adjustment across families" (lines 226-228), and the severity-3 caveat that severity 3 is not matched to sigma 0.1
  (line 202-203).
- The C6-11 reading of the cells: shot and speckle are close relatives of Gaussian noise; impulse is the structurally different cell (line 201-202). This may be stated; it
  is context for the impulse result (net +5.0 points, Holm p 0.029), not a ranking.
- Descriptive extras already in the JSON (drop of NONE, Clopper-Pearson, mid-p), labelled descriptive.

Not allowed:
- LG in the title, abstract or highlights. Branch A title (line 276) has no LG; placement item 1 (lines 299-301) admits only Study 1's NEG sentence plus the L1 and L-NI sentences for Study 2;
  line 289-291 is the branch C no-rescue rule and does not license LG elsewhere under A. The abstract's scope {S} (lines 269-271) says "Gaussian noise at one severity"; do not widen it using LG.
- The word "generalises" in any form (line 204, 281, 307; "never used"), also "held-out noise family" (line 202, 309), "robust", "validated", "confirmed" beyond the stated tests (line 307-308).
- Pooling the three cells, or LG with L1/L3/L4 or folds, into one "across noise types" figure, mean or sentence (line 309). Report three cell rows.
- Any LRF versus GATE-M comparison from the `descriptive_gatem_vs_none` block, or any table holding both GATE-M results on M4 items and LRF numbers (lines 302-303, 308-309).
- A guarantee, "calibrated", or in-sample numbers as performance (line 308); a novelty claim (no novelty audit, A6.14 item 4).
- Reading the impulse cell as "clearly" positive: its 95% CI starts at 0.0 and it would not pass a two-sided 0.05 test. A6.12 gives no LG-specific wording for this, but branch B's
  wording for L1 (line 286) is the model; the writer should state the one-sided preregistered alpha and the two-sided p beside the impulse row.

## Fixes (all administrative; no number, label or branch changes)

- F1. Append a ledger row superseding X0006's "verdict pending" (do not edit X0006; family L did this with X0005), add an ops-log line recording this verdict, and tick the LG item in `research/progress.md` (not touched by me).
- F2. Writer notes in the deviations/results box: the impulse-cell points above (two-sided p 0.058, 95% CI lower bound 0.0); the A-8 residual (self-check under the deterministic backend, items under benchmark on, up to about 1.5% of tokens differing between processes) also applies to LG; imagecorruptions commit c959e659 is recorded from the venv, not at run time (see F3).
- F3. `runs/P2-LRF-LG/env-lock.txt` is 0 bytes, as are `runs/P2-LRF-L1/env-lock.txt`, `runs/P2-LRF-RESCORE/env-lock.txt`, `runs/P2-GATE-M4/env-lock.txt` and `runs/P2-GATE-M1/env-lock.txt` (the family L audit called L1's file "byte-identical" to the other two, which is true because all are empty; I did not flag it then). The environment is therefore not recorded by the runs. Capture `pip freeze` once from the venv into a committed file before the release gate so the lock-file rebuild (my procedure step 5) is possible; do not rewrite the empty files.
- F4. Keep "no LG output was read before the run was complete" worded "per the ops log" (as family L fix 5).
