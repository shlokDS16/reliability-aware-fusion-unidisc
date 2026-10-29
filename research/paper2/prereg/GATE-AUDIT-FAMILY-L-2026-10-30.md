```yaml
agent: gate-auditor
date: 2026-10-30
brief: Audit of Paper 2 Study 2 family L (L1, L3, L4, L-NI, L-LEN) against SAP addendum A6 r1/r2 (A6.0, A6.2, A6.3, A6.4, A6.8, A6.12) and card v4 section 9 rows A-7, A-8 (code pin 1871fe7d)
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md (full, with r2 clarification table line 48-50)
  - research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md rows A-6, A-7, A-8 (lines 247-249)
  - git log of the branch (ISO timestamps) and git blobs at 24d36a8a, 1871fe7d, HEAD
  - runs/P2-LRF-PINS/pins.json; runs/P2-LRF-FROZEN-LFIX/HASHES.json; runs/P2-LRF-PLAN/{n_rule,family}.json; runs/P2-LRF-CF-LFIX/results.json (b, c only)
  - runs/P2-LRF-FOLD/{folds_lrf,manifest,builder_report}.json; runs/P2-LRF-L1/{config,selfcheck,items.jsonl,chunks.jsonl,arrays_manifest,arrays/*,predictions.jsonl,lrf_score_meta,a6_analysis}.json*; runs/P2-LRF-L1.try1/.try2 (listing and chunks only); runs/P2-LRF-L1.driver.out
  - research/ledgers/decisions.jsonl D0085, D0087-D0089; research/ledgers/experiments.jsonl X0004; research/paper2/CONFIRM-EVENING-2026-10-28.md section 18 (last lines)
  - research/paper2/prereg/GATE-CODE-AUDIT-A6-LRF-2026-10-29.md (verdict lines), GATE-CODE-DELTA-AUDIT-M4SELFCHECK-2026-10-29.md (verdict line)
  - exp_p2/gate/lrf_score.py 255-420 (CLI and write path)
coverage: >
  Not opened: anything under runs/P2-LRF-LG/ (GPU job running); no torch/CUDA import (CUDA_VISIBLE_DEVICES empty; the scorer and analysis import numpy only).
  Not re-verified: the data-steward L7 content (sign-off file exists, committed 41d9da2f 21:06:42); the freeze itself (only its committed hash set); the
  A6 code audit bodies beyond their verdict lines; LG, baselines, the S2 or H results. "No L output was read before the run completed" rests on the ops
  log (section 18: the 22:41 check reports progress and resource figures only) and cannot be proven from git.
claims:
  - statement: "Commit order meets A6.0 items 1-3: every precondition was committed before the first L1 item"
    status: supported
    evidence: "git log timestamps below; first L1 chunk_start 21:34:45 (chunks.jsonl t=1793289885.85), launch 21:34:03 (driver.out), items rows 0->4 at 21:35:59"
    level: E4
    confidence: 0.95
  - statement: "L1 ran at the pinned code, on the committed fold's first 450 items in order, with a passing 0.99 self-check"
    status: supported
    evidence: "git diff --quiet 1871fe7d 6bc1650f -- exp_p2 tools tests exit 0 (also vs HEAD); items == folds_lrf.json test[0:450] by (image_id, gid), idx 0..449"
    level: E4
    confidence: 0.95
  - statement: "Predictions and A6 analysis regenerate byte-identically; the family-L numbers, labels and branch A are correct"
    status: supported
    evidence: "scratch reruns and independent recomputation, sections 5 and 6"
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - "Whether any L1 accuracy was seen mid-run: not provable from git; ops log says progress and resource figures only"
next_test: {hypothesis: n/a (audit), intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Gate audit: Study 2 family L (L1, L3, L4, L-NI, L-LEN), 2026-10-30

## VERDICT: PASS WITH FIXES

No criterion is `missing` or `partly` against A6.0, A6.2, A6.3, A6.4, A6.8 or card rows A-7/A-8. All numbers in `a6_analysis.json`, ledger X0004 and the
ops-log line reproduce. The fixes are administrative (bookkeeping and wording notes), none changes a number or the branch. Branch A stands.
I did not edit `progress.md`, the ledgers, or any run file (brief: one report file only). Ledger rows added: 0.

## 1. Commit order (A6.0): PASS

| A6.0 requirement | Commit (author time, IST 2026-10-29) | Before first L1 item (21:34:45 first chunk start; 21:35:59 first rows)? |
|---|---|---|
| Item 1: A6 r1, A5 r2, C6-1..C6-11 dated row | 941a260b, 704042f5 (per D0087); D0087 row 19:01:18 (5e6380b1), before first H3 item | yes |
| Item 2: re-frozen object + hash set + gate pass + lead statement | 24d36a8a 21:00:13 (HASHES.json, D0088); gate on first 5 items fd836522 19:30:44 | yes (and before the fold build) |
| Item 3: fold + manifest + leak check | 4be79be8 21:01:03; L7 sign-off 41d9da2f 21:06:42 (file `research/paper2/data/L7-SIGNOFF-LRF-FOLD-2026-10-29.md` exists) | yes |
| n-rule (cross-fit, then record, plan) | 4a7a8c3d 21:16:21 (cross-fit, before the Mon 2 Nov 10:00 bound); 693fbe46 21:16:50 (n_rule.json, family.json, D0089) | yes |
| A6.11 code audited PASS, merged after S2, dated pin row | audit PASS at bfae5c35 (GATE-CODE-AUDIT-A6-LRF, "Delta D1-D2 ... PASS"); card row A-6 (pin 725a1b5a, 18:02) | yes |
| Route/venue fixed, Shlok's GPU go-ahead | D0089 (Route C, IEEE TNNLS); D0085 "Yes, unattended (Recommended)" | yes |
| Card A-8 pin 725a1b5a -> 1871fe7d | 1871fe7d 21:24:02 (code); 34df4228 21:33:12 and e169282a 21:33:46 (A-8 row, time corrected); delta audit PASS WITH FIXES, fix = the A-8 row | yes (about 1 minute before launch at 21:34:03) |
| Pins (scorer) before predictions | fdfd8b97 22:42:54 (pins.json); predictions 0d580242 23:58:17 | yes |
| Predictions before analysis | 0d580242 23:58:17 -> 4a01f896 23:58:29 | yes |
| Run files before predictions | 6bc1650f 23:57:42 (L1 complete 23:56:49) | yes |
| Ledger last | 6dc08b4d 23:58:58 (X0004) | yes |

Attempts try1 (21:19) and try2 (21:21) stopped at the self-check before any item: `runs/P2-LRF-L1.try1` and `.try2` hold no `items.jsonl`
(try1 `chunks.jsonl` has only `selfcheck_failed_earlier`). No L1 outcome data existed when the code pin moved.

Notes (non-blocking):
- `pins.json` (22:42) was written after L1 had started (200/450 items done), so A6.0 item 2 is met by `HASHES.json`/D0088 at 21:00, not by the pins
  file. The pins file adds only the scorer inputs; every value in it equals `HASHES.json`/`spec.json` (section 4) or is the A-8 entry point. Say this
  in the deviations box rather than "pins committed before L1 started".
- A-8 residual (card row A-8, text): the self-check certifies the layout under the deterministic cuDNN backend, not the backend the items used
  (benchmark on, as in M4); fresh image tokenisation can differ by up to about 1.5% of tokens between processes. Keep this in Limitations.

## 2. L1 ran at the pinned code and on the right items: PASS

- `git diff --quiet 1871fe7d 6bc1650f -- exp_p2 tools tests`: exit 0. The same diff against current HEAD is also empty (so the LG launch at 4b7c1f8c is at the same code).
  `config.json` `git_sha` e169282a (the A-8 commit; code identical to 1871fe7d). `env-lock.txt` is byte-identical to `.try2/env-lock.txt` and to
  `runs/P2-LRF-RESCORE/env-lock.txt`.
- `config.json`: `n_items` 450, `caption_slot_len` 13, `neg_len` true, `folds_path` runs/P2-LRF-FOLD/folds_lrf.json, `family_run` P2-LRF-PLAN,
  `codebook_sha256` ff15b9b5... and `dcache_di_sha256` f7744253... equal the A6.2 table.
- n: `n_rule.json` n_L = 450; `family.json` test_fold = 450; `items.jsonl` has 450 unique rows, idx 0..449. Independent comparison: the (image_id, gid) of the rows
  equals `folds_lrf.json` `test[0:450]` in order (gid 8000..8449). Fold has 533 items; the prefix rule holds.
- n-rule recomputed by my own exact-power code: pi_cf = 0.228, Delta_plan = 0.058; power at n 440 = 0.7942, 450 = 0.8029 (one-sided 0.05), so n_req = 450;
  at 0.025: 0.7044 (matches `power_at_n_L`). cf_b 86, cf_c 28 equals `runs/P2-LRF-CF-LFIX/results.json` b, c; (86-28)/500 = 0.116, (86+28)/500 = 0.228.
- `selfcheck.json`: ids_equal true, modality_equal true, `image_tokens_frac_equal` 0.99902 >= 0.99. Passes.
- Run integrity: `chunks.jsonl` 12 `chunk_start`, 11 `soft_deadline`, 1 `complete`; `driver.out` chunk exits 75 x11 (soft deadline) then 0; no guard-stop event.
  Completion 23:56:49, 450/450.

## 3. Arrays: PASS

All 450 `runs/P2-LRF-L1/arrays/itemNNNN.npz` re-hashed with SHA-256 against `arrays_manifest.json`: 0 mismatches; manifest names = files on disk (450 = 450).

## 4. Pins equal the frozen object; scorer meta: PASS

- `pins.json` `model_sha256` db7fdb4e..., `spec_sha256` 9d196d71..., `data.py` 14421ffb..., `families.py` 1c49827d..., `lrf.py` 03ed472e..., `run.py` 01c8dba6...,
  codebook ff15b9b5..., DI f7744253... all equal `HASHES.json` `new`/`pinned_vs_A6.2_table` and the A6.2 table (lines 130-134).
- Entry-point hashes differ in form only, and I reconciled them. `HASHES.json` stores the working-tree (CRLF) hashes; `pins.json` stores LF git-blob hashes
  (the file says "LF-normalised"). Verified: `lrf_score.py` blob at 24d36a8a = 63f70961... = pins; CRLF form 50ff6754... = HASHES; `run_gate_lrf_rescore.py` blob
  ff34c2b6... = pins, CRLF form 6dbea421... = HASHES; `run_gate_m4.py` blob at 24d36a8a CRLF form ebfa3e18... = HASHES, and blob at 1871fe7d = e2d9a5ee... = pins.
  `git diff 24d36a8a 1871fe7d -- exp_p2 tools tests analysis analysis_posthoc` touches only `run_gate_m4.py` (+7/-1) and one test (+40): exactly the A-8 delta.
- `lrf_score_meta.json`: `pins_verified` lists model, spec, four code hashes, scoring code, three entry points, decision rule; `positive_control` n_checked 1800, ok true;
  `crosscheck_max_abs_w_diff` 0.0; `n_lines` 1800; `conds_absent_in_rows` empty; `n_items_skipped_no_arrays` 0.

## 5. Regeneration: PASS (byte-identical)

Scratch dir `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\f9e01f26-3b7f-40af-a381-11d4b248c68b\scratchpad\audit\`.
- `python -m exp_p2.gate.lrf_score --run-id P2-LRF-L1 --pins runs/P2-LRF-PINS/pins.json --crosscheck --out <scratch>/pred.jsonl`: rc 0; `cmp` identical to the committed
  `predictions.jsonl`; SHA-256 e919776c351596d175211a8a3ca215e6f6a892d608cf9a049df8f2d81c0d305f for both. The scratch `lrf_score_meta.json` equals the committed one except `run_dir`.
- `python -m analysis.paper2.lrf.a6_analysis --l1 runs/P2-LRF-L1/predictions.jsonl --n-rule runs/P2-LRF-PLAN/n_rule.json --out <scratch>/a6.json`: `cmp` identical to `a6_analysis.json`
  (L1 "confirmed", branch "A").
- Not done: a clean-clone rebuild from the lock file (the step-5 release check in my procedure). The arrays are untracked, so a clone cannot reproduce predictions without them; this belongs to the release gate, not this one.

## 6. Independent recomputation from raw predictions: PASS

My own code (stdlib exact binomial, numpy bootstrap with a different seed), reading only `predictions.jsonl`:

| Test | b | c | n | acc LRF | acc NONE | net | exact p (mine) | a6_analysis.json | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| L1 noise0.1, one-sided | 58 | 27 | 450 | 0.8022 | 0.7333 | +0.0689 | 0.000508110 | 0.000508110 | confirmed; 95% CI +0.0289 to +0.1089 (mine +0.0289 to +0.1089); one-sided p <= 0.025 and b > c |
| L3 jpeg10, two-sided | 27 | 20 | 450 | 0.8644 | 0.8489 | +0.0156 | 0.381693 | 0.381693 (Holm 0.381693) | not rejected |
| L4 splice128, two-sided | 24 | 10 | 450 | 0.9267 | 0.8956 | +0.0311 | 0.024307 | 0.024307 (Holm 0.048613) | rejected at Holm m = 2 (0.0486 <= 0.05) |
| L-NI clean | 27 | 13 | 450 | 0.9178 | 0.8867 | +0.0311 | (descriptive) | lower90 +0.0089 | 90% percentile CI lower bound mine +0.0089 > -0.03: non-inferior |
| L-LEN noise0.1, y_lrf_L vs y_none_L | 67 | 33 | 449 | 0.7840 | 0.7082 | +0.0757 | 0.000437 | 0.000437 | rejected, b > c; one item (idx 137, c-_L one token shorter) excluded and counted |

Holm m = 2 was applied over {L3, L4} after the L1 gatekeeper, sorted by p: L4 x2 = 0.0486, L3 max(0.0486, x1) = 0.3817. Branch: A6.12 line 276 requires L1 confirmed at one-sided
p <= 0.025 at a completed (n 450 = n_L, i.e. >= 0.8 n_L, not a partial prefix; r2 table line 50 not triggered) fold; 0.000508 qualifies. Branch A is correct.
No condition has a negative net (jpeg10, splice128, clean, noise0.1 all >= 0; `harm` false in every block). All three sources agree: `a6_analysis.json`, ledger X0004
("L1 confirmed (b 58, c 27, n 450, one-sided p 0.00051, branch A); L3 jpeg10 not rejected (Holm p 0.38); L4 splice128 rejected (Holm p 0.049); L-NI shown (lower90 +0.009 vs margin -0.03); L-LEN rejected (n 449)")
and the CONFIRM-EVENING section 18 line "2026-10-29 23:58 IST: L1 COMPLETE ... L1 confirmed, branch A (noise0.1 b 58, c 27, one-sided p 0.00051); L3 not rejected, L4 rejected at Holm 0.049, L-NI shown, L-LEN rejected (4a01f896)".
Length strata in the JSON (descriptive): shorter 184 (net +0.038), equal 43 (+0.140), longer 223 (+0.081); longer-minus-shorter +0.043, 95% CI -0.038 to +0.123.

## 7. What the result now binds (SAP-ADDENDUM-A6-LRF-2026-10-29.md line refs)

Allowed under branch A (the "may" list):
- Title: the branch A title at line 276 and no other. It must not use "robust", "generalises", "first", "state of the art" and must not name gating, GATE or Study 1's result (line 281).
- Scope sentence `{S}` (lines 270-271) with `{n}` = 450 (not 520, not 533) and "Gaussian noise at one severity".
- Abstract (line 299-300): Study 1's A4.2 NEG sentence unchanged, plus the L1 sentence and the L-NI sentence; no sentence links the two studies. Highlights may carry an LRF gain (line 300-301, "only in branch A").
- L1 results sentence (lines 284-287): accuracy 0.733 to 0.802, net +6.9 points, 95% CI +2.9 to +10.9, "exact one-sided McNemar p = 0.00051; preregistered one-sided alpha 0.05", plus {S}.
- L-LEN clause (lines 186-190): L-LEN was rejected with b > c, so "including with length-matched negatives" is permitted (n 449, one item excluded and counted); the descriptive strata may be reported (line 189-190).
- L-NI sentence (lines 293-294): lower 90% bound +0.9 points exceeds -3 points, so the "lost no more than three points (90% CI ...)" form applies, and the text must state that the margin was fixed after an exploratory clean interval had been seen (line 183-184, C6-11, `margin_note` in the JSON).
- L3/L4 (line 295, Results): jpeg10 "no difference detected" with its CI (net +1.6 points, 95% CI -1.3 to +4.4; Holm p 0.38); splice128 "raised" with CI (net +3.1 points, 95% CI +0.7 to +5.8; Holm-adjusted p = 0.049, i.e. a margin of 0.001 under 0.05 and 0.024 unadjusted two-sided). The harm sentence is mandatory wherever the L1 gain appears (line 295): here no condition showed a reduction, and that sentence should say so with the CIs.

Not allowed (the "must-not" list):
- Any L3, L4 or "across corruptions" claim in title, abstract or highlights: placement item 1 (line 299-300) admits only the L1 and L-NI sentences for Study 2; "pooling corruptions, LG cells or folds" is forbidden (line 310). Do not pool jpeg10, splice128 and noise0.1 into one "robustness" statement.
- "Confirmed", "validated" or "generalises" without the matching test (line 307-308). LG is not yet run; its wording must be "other noise types (shot, impulse, speckle; imagecorruptions severity 3)" and "generalises" is never used (lines 200-205, 297).
- Any comparison of LRF with GATE-M or with CLIP/SigLIP, and any figure or table containing both GATE-M results on M4 items and LRF numbers (lines 308-309, 302-303). The `supplement_gatem_vs_none` block in `a6_analysis.json` is supplement-only, descriptive.
- A guarantee or "calibrated" for LRF; quoting in-sample or `freeze_check.json` numbers as performance (line 308); novelty claims, since no novelty audit exists (A6.14 item 4, line 329).
- Any link from Study 1 to LRF as motivation or answer (A6.1 consequences, lines 91-98; placement item 2, lines 301-302); chronology only once, in Methods (A6.13, lines 311-322).
- A "no multiplicity adjustment across families" statement with the family count of 17 (lines 226-228) must accompany the family-L claims.
- Reading note (mine, not in A6): L-NI is a non-inferiority test. The clean-image net is +3.1 points (90% CI +0.9 to +5.3), but superiority on clean images was not preregistered, so it should not appear as a gain claim; the template's "lost no more than three points" wording is the tested statement.

## Fixes (all administrative; no number, label or branch changes)

1. Append a ledger row (do not edit X0004) and an ops-log line recording this verdict, since X0004 still says "Gate-auditor verdict pending"; tick the family-L item in `research/progress.md` (I did not touch it).
2. `runs/P2-LRF-L1/token_exclusions.json` (88 bytes, zero exclusions) is untracked, as is `arrays/` by design. Commit the file, or state in the run record why it is not.
3. Hash form: `config.json` and `manifest.json` give the fold SHA-256 a545a83e... of the working-tree CRLF file; the committed LF blob hashes to 2f0e401c... (same content, line endings differ; core.autocrlf true). Likewise HASHES.json holds CRLF-form entry-point hashes and pins.json LF-form hashes. Add one sentence to the reproducibility notes so a Linux checkout is not read as a mismatch.
4. Deviations box and Limitations: (a) pins.json was written at 22:42 while L1 was at about 200/450 (values copied from the 21:00 commit); (b) A-8 residual on the self-check backend; (c) the data-steward's note that 162 other `runs/P2-*` JSON files outside the C6-10 classes were not opened (ops log 21:06) and that neg/mismatch ids are covered only through earlier folds; (d) D0088 records that the lead saw the S2 table, the FOIL B result and the H3 rule code before the re-freeze (A6.0 item 2 statement); A6.13's disclosure text does not mention this, and the writer should decide whether to add it.
5. The L1 closing sentence "no L output was read before its run was complete" is supported by the ops log only. Keep it worded as "per the ops log".
