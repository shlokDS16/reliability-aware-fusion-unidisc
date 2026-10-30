```yaml
agent: gate-auditor
date: 2026-10-30
brief: >
  Red-team condition RS-12: audit runs/P2-LRF-BASELINES (89423704) and runs/P2-LRF-BASELINES-PARITY-L1 / -LG (2db50b5f)
  against SAP A6.6 before any CLIP or SigLIP number enters the Paper 2 main text.
sources_examined:
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md (A6.6, A6.12 baselines sentence, must-not list)
  - analysis/paper2/lrf/baselines.py (all 261 lines); tests/exp_p2/test_gate_a6_r1.py (lines 121-260)
  - runs/P2-LRF-BASELINES/{baselines.json,predictions.jsonl}, runs/P2-LRF-BASELINES.{stdout,stderr}.txt
  - runs/P2-LRF-BASELINES-PARITY-L1/ and -LG/ {baselines.json,predictions.jsonl,stdout.txt,stderr.txt,telemetry.csv}
  - runs/P2-LRF-FOLD/folds_lrf.json, runs/P2-LRF-L1/items.jsonl, runs/P2-LRF-LG/items.jsonl, runs/P2-LRF-PLAN/{family.json,n_rule.json}, runs/P2-LRF-PLAN-LG/family.json
  - research/paper2/CONFIRM-EVENING-2026-10-28.md section 18 (lines 186-205); C:/Users/ANONYMIZED/.cache/huggingface/hub (the two model snapshots)
  - paper2-tnnls/SPEC.md (Table III), research/paper2/tnnls/REDTEAM-SPEC-2026-10-30.md (RS-12)
coverage: >
  Read in full: baselines.py, the three baselines.json, all three predictions.jsonl (programmatically), the ops-log lines, the telemetry
  start lines. Re-ran tests/exp_p2/test_gate_a6_r1.py on CPU (20 passed). NOT done: regenerating the 5,400 scores (about 1 h CPU; the brief
  allows recomputing table() instead); re-running the UniDisc VQ parity (needs the GPU; not allowed here); hashing the model weights against the
  Hub (offline); verifying anything about the 02:05 move beyond what the files now show.
verdict: PASS WITH FIXES
claims:
  - statement: Code for all three runs is 1871fe7d; nothing in analysis/, exp_p2/ or tools/ changed between 1871fe7d and 89423704, 2db50b5f, 84be25c4 or the current HEAD.
    status: supported
    evidence: git diff --stat 1871fe7d <each> -- analysis exp_p2 tools is empty for all four; 1871fe7d is an ancestor of 89423704 and 2db50b5f; last commit touching those paths is 1871fe7d (2026-10-29 21:24); the baseline run began about 01:00 on 10-30.
    level: E4
    confidence: 0.95
  - statement: The main run scored exactly the first 450 fold items (clean, jpeg10, noise0.1, splice128) and the first 300 for shot_noise3, impulse_noise3, speckle_noise3, for both models.
    status: supported
    evidence: predictions.jsonl 5,400 rows = 2 x (4 x 450 + 3 x 300); per (model, condition) the (idx, gid, image_id) sequence equals fold[:450] or fold[:300] exactly; P2-LRF-L1/items.jsonl equals fold[:450] and P2-LRF-LG/items.jsonl equals fold[:300] on (idx, gid, image_id).
    level: E4
    confidence: 0.98
  - statement: Pixels are built as in the M4 stage.
    status: supported
    evidence: baselines.py condition_images uses suite.center_crop_512, corruptions.apply_pixel with rung_rng, run_gate_m3.donor_for on the whole 533-item fold, and suite.apply_corruption with suite.corruption_seed(gid, run_gate_m4.extra_cell_index(...)); test_regenerated_pixels_equal_the_m4_stage_pixels compares array-equal against run_gate_m4.build_conditions (stubbed images and a stubbed corruption package, so it tests the call and seed wiring, not the real package); the real-pipeline evidence is the VQ parity below.
    level: E4
    confidence: 0.85
  - statement: The pinned revisions were used and nothing was downloaded during the runs.
    status: supported
    evidence: MODELS in baselines.py carries both full revisions; baselines.json "models" records them; each HF cache directory holds only that one snapshot (32bd6428..., 9fdffc58...); every cached file has mtime 10-29 19:25 to 20:04, before every run; HFScorer calls force_offline() and from_pretrained(local_files_only=True) unless --download-approved, which the logged commands do not use. No hash of the weight files is recorded anywhere.
    level: E3
    confidence: 0.85
  - statement: Every number in the baselines.json table recomputes from predictions.jsonl.
    status: supported
    evidence: BL.table(rows, BL.baseline_rng(), 10000) equals the stored table exactly (dict equality after JSON round trip). Independently, accuracy, n and point drop for all 14 (model, condition) cells match to 1e-15; y == (s_pos > s_neg) in all 5,400 rows; no ties, no non-finite scores. The bootstrap seed is SeedSequence(20261028, spawn_key=(34,13)) as stated.
    level: E4
    confidence: 0.97
  - statement: Pixel parity passed for both condition sets.
    status: supported
    evidence: L1 parity: 20 item-conditions (items 0-4 x clean, jpeg10, noise0.1, splice128), min agreement 0.98926, mean 0.99663; LG parity: 20 (items 0-4 x clean, shot_noise3, impulse_noise3, speckle_noise3), min 0.98633, mean 0.99658; rule min >= 0.98 holds in both and ok=true. The items are fold[:5]. All seven conditions of Table III are covered, each on 5 items. The agreements themselves were not recomputed (GPU); they are read from baselines.json, whose min and ok fields are consistent with its own agreement list.
    level: E3
    confidence: 0.8
  - statement: The 5-item baseline rows in the parity runs equal the main run's rows for the same items.
    status: supported
    evidence: 80 rows (40 + 40): all present in the main run, gid and image_id equal, s_pos and s_neg differences exactly 0.0, y differences 0. Same pixels and models, deterministic on CPU.
    level: E4
    confidence: 0.97
competing_explanations:
  - "Parity agreement 0.986-0.999 on every item (never 1.000 except 2 of 40) is the known card A-8 residual (fresh tokenisation differs by up to about 1.5% of tokens between processes), not a pixel difference. A pixel mismatch (wrong seed) would be expected to cost far more than 1.4% on a noise cell. The control therefore detects gross pixel errors, not single-pixel ones, and the margin to 0.98 is 0.6 points on the worst cell."
unknowns:
  - "Whether the moved parity files are byte-identical to what the run wrote: not checkable (see item 6)."
  - "Weight-file hashes of the two models; the Hub was not contacted."
  - "CLIP/SigLIP cost: no timing was committed."
```

# Gate audit: CLIP/SigLIP baselines and pixel parity (A6.6, RS-12)

**Verdict: PASS WITH FIXES.** The numbers in `runs/P2-LRF-BASELINES/baselines.json` are reproducible from `predictions.jsonl`, the items and conditions are the
preregistered ones, the code is the pinned code, and the parity positive control passed under the A6.6 rule (every checked image >= 0.98). Table III may be
built, subject to the fixes below. No criterion is `missing`; two criteria are `partly` (item 6, item 7 cost), which is why the verdict is not a plain PASS.

## Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Code at 1871fe7d for all runs | met | No diff in analysis/ exp_p2/ tools/ between 1871fe7d and 89423704, 2db50b5f, 84be25c4, HEAD (empty `git diff --stat`). Working tree of the three run directories is clean against HEAD. Pre-launch check of the main run is stated in the ops log as "code = 1871fe7d"; for the parity runs also; the LG run used `git diff --quiet`, the baseline line does not say how it was verified (minor). |
| 2 | Items = first 450 (first 300 for LG cells); conditions; pixels as M4 | met | See claims 2 and 3. The main run used `--family-run P2-LRF-PLAN` (family jpeg10, noise0.1, splice128, endpoint d; n_L = 450 in `P2-LRF-PLAN/n_rule.json`). The LG parity run used `--family-run P2-LRF-PLAN-LG` (empty family, n 300), which is why it covers clean plus the three cells only. |
| 3 | Pinned revisions, no download | met (E3) | See claim 4. Note the HF cache has no `refs/` directory and no `blobs`; the snapshots were written directly under the full revision names, so a revision other than the pinned one cannot be loaded offline. The stderr of the main run shows only the pynvml warning. |
| 4 | Table recomputation | met | See claim 5. Byte-identical regeneration of the 1-hour CPU scoring was not done (allowed by the brief). |
| 5 | Parity | met | See claims 6 and 7. |
| 6 | Moved files | partly | No hash of the files as written exists in the ops log, commit messages or any run file (grep of the ops log and the run directories). The originals no longer exist (`runs/env-2026-10-14/smoke_unidisc/runs/` is gone). What supports integrity: (a) 2db50b5f committed the files at their final paths with stdout, stderr and telemetry, mtimes 02:02-02:03 equal to the run times; (b) the telemetry "start" lines record the exact commands and "child exited 0"; (c) the parity runs' `predictions.jsonl` agree to the last bit with the main run for the same items, so those files were not altered in content; (d) the `baselines.json` agreement lists are self-consistent (min, ok, counts). The agreement values themselves have no independent check. Hashes as of this audit are given below so they can be recorded now. |
| 7 | A6.6 sentence and caption rules; cost | partly | Rules below. No committed timing exists for CLIP/SigLIP. |

## The main run's `pixel_parity` field

`baselines.json` says `"pixel_parity": "not run: baselines are labelled \"pixel parity not shown\""`. That was true when it was written (the parity step
ran at 02:01-02:03, after the main run at 01:59), and the file is committed, so it cannot be edited. It is not a contradiction; it is a stale field. The
reconciliation is documentary: the parity record is the pair of directories `P2-LRF-BASELINES-PARITY-L1` and `-LG` (commit 2db50b5f). The paper must cite those
two directories, not the field in the main file, and the deviations box should list "baselines.json records pixel parity as not run; the control ran
afterwards in two directories (2db50b5f)". A reader opening only the main file would otherwise conclude the A6.6 fallback applies.

## Recomputed numbers (descriptive; nothing here is a test)

Accuracy (n) and paired clean-to-corrupted drop (clean minus corrupted accuracy, 95% percentile bootstrap, 10,000 resamples), all matching `baselines.json`:

| Condition | n | CLIP acc | CLIP drop [CI] | b / c | SigLIP acc | SigLIP drop [CI] | b / c |
|---|---|---|---|---|---|---|---|
| clean | 450 | 0.9978 | | | 0.9978 | | |
| jpeg10 | 450 | 0.9978 | 0 [0, 0] | 0 / 0 | 1.0000 | -0.0022 [-0.0067, 0] | 0 / 1 |
| noise0.1 | 450 | 1.0000 | -0.0022 [-0.0067, 0] | 0 / 1 | 0.9978 | 0 [0, 0] | 0 / 0 |
| splice128 | 450 | 0.9956 | 0.0022 [0, 0.0067] | 1 / 0 | 1.0000 | -0.0022 [-0.0067, 0] | 0 / 1 |
| shot_noise3 | 300 | 1.0000 | -0.0033 [-0.01, 0] | 0 / 1 | 0.9967 | 0 [0, 0] | 0 / 0 |
| impulse_noise3 | 300 | 0.9967 | 0 [0, 0] | 0 / 0 | 0.9967 | 0 [0, 0] | 0 / 0 |
| speckle_noise3 | 300 | 1.0000 | -0.0033 [-0.01, 0] | 0 / 1 | 0.9967 | 0 [0, 0] | 0 / 0 |

(b = clean right and corrupted wrong; c = clean wrong and corrupted right; my counts from predictions.jsonl, not stored in baselines.json.)
Clean errors: CLIP wrong at idx 8, SigLIP wrong at idx 13 (both inside the first 300). Clean accuracy on the first 300 items is 0.99667 for both models, so
the three 300-item cells are compared with a clean accuracy of 0.9978 (n 450) in the table, which is not the clean accuracy of the same 300 items; the drop
column is paired and correct, the accuracy column is not like for like. Neither CLIP nor SigLIP caption exceeds the text limit (max 28 and 29 tokens against 77 and 64; no truncation).

Observations the writer must respect: the baselines are at ceiling (0.9956 to 1.0000), at most one discordant pair per cell, so every CI is a degenerate
interval of 0 and +-1/450 or 1/300 steps and the "drop" is 0 to 3 items. No inference about corruption robustness of the encoders follows; the table shows
that the matching task is almost solved by the encoders, which is what the red-team R1 sentence already says.

## A6.6 sentence and caption rules for Table III

Exact sentence (A6.12, Baselines bullet): "For reference, CLIP ViT-L/14 and SigLIP so400m, different models trained on different data, reached ... (own table)."
No comparison word. Rules binding on Table III and its text (A6.6, A6.12 must-not, RS-10):
- Own table: accuracy per model and per condition including clean, with the paired bootstrap CI of each model's own clean-to-corrupted drop. No test, no p-value,
  no ranking, no bold by rank, no column or row of LRF or UniDisc numbers, no LRF-to-baseline comparison anywhere ("any comparison of LRF with ... CLIP/SigLIP" is on the must-not list).
- The caption should state: models and pinned revisions (32bd6428..., 9fdffc58...); decision rule 1[s(image, c+) > s(image, c-)] with ties wrong (none occurred); CLIP cosine,
  SigLIP pairwise logit; same first 450 items (300 for the three imagecorruptions severity-3 cells) as Study 2 and the same regenerated pixels; n per cell; "descriptive only";
  and the pixel-parity result: "pixel parity shown: the UniDisc VQ re-encoding of the regenerated images agreed with the stored codes on at least 98.6% of tokens (5 items per
  condition set, 40 item-conditions; threshold 98%)". Cite both parity directories.
- Not allowed: "outperform", "competitive", "better than", "beats", "robust", "generalises"; the word "almost solve" is already approved in the spec only in the Limitations sentence.
- The deviation clauses to carry: field "pixel_parity: not run" in the main file, parity in separate directories, moved files (below).

## Cost (spec: "their cost" inside Table III)

No committed timing for CLIP or SigLIP: `predictions.jsonl` has no per-row seconds, `baselines.json` has no timing key, and the main run has no telemetry file. All that exists is
the stderr file's mtime (01:01) and the stdout file's mtime (01:59) and the ops log ("launched 01:00", "complete 01:59", working set 5.6 GB), i.e. about one hour of wall-clock on the
laptop CPU while the pixels, both models and the imagecorruptions cells were computed together, and the parity runs' 66 s and 71 s that are dominated by loading UniDisc.
That is a log-derived upper bound for a combined job, not a per-item cost, and it is not comparable with the 27 s per item of the UniDisc scorer (GPU). The cost therefore cannot be
stated as a measured number. Options for the lead: state "cost not measured" in Table III; or run a new, separately named timing run (not a rerun of this one) and cite it.
Do not write a per-item figure derived from 3,600 s / 2,700 images.

## Fixes (none touches a committed run)

1. Table III caption and the deviations box must cite the two parity directories and explain the stale `pixel_parity: "not run"` field in `runs/P2-LRF-BASELINES/baselines.json` (above).
2. Record the SHA-256 of the six moved or written files now, in the ops log, labelled "as of 2026-10-30 audit, not as written" (working-tree CRLF hashes, 16-character prefixes; git blob hashes are LF-normalised, per the ops-log hash convention):
   `P2-LRF-BASELINES/baselines.json` 5c64138becc758db; `.../predictions.jsonl` 9fad81f500c21078; `PARITY-L1/baselines.json` c51de285f608b883; `PARITY-L1/predictions.jsonl` ef8ed1c4a456d028; `PARITY-LG/baselines.json` 6903ef5c53be2072; `PARITY-LG/predictions.jsonl` 71ce56aef5b0d01d.
   Add the deviations-box item "parity outputs first written to a wrong directory by UniDisc's cwd change and moved unchanged; no hash taken before the move".
3. Table III accuracy column: for the three 300-item cells print the clean accuracy of the same 300 items (0.9967 for both models) or mark that the clean row is n 450; do not leave a 450-item clean beside 300-item cells.
4. Cost: write "not measured" or run a named timing run; no number from the ops-log wall-clock.
5. State the ceiling: at most one discordant pair per cell, degenerate CIs; no sentence reads the drops as robustness of the encoders.
6. Weight provenance: record the SHA-256 of the two `model.safetensors` files (local CPU job, no network) in the ops log, since only the revision names are recorded.
7. Ledger row and `progress.md`: add a ledger row for this verdict (suggest ledger X, next id after X0007); tick RS-12 in the REDTEAM-SPEC status table (line 321) and the Table III gate in `paper2-tnnls/SPEC.md`. I did not do these; I never fix what I audit, and the ledger id is the lead's.

## Residual risks (not blocking)

- Parity is a 5-item control: it shows the regenerated pixels reproduce the stored UniDisc tokens within the A-8 tokenisation residual, not that all 450 items were built identically. The wiring is also covered by the array-equal test against `build_conditions`, which uses stubs.
- The worst parity cell (LG, item 0 clean, 0.98633) sits 0.6 points above the threshold; a stricter reading would be uncomfortable, but A6.6 fixes 0.98 and the rule is met.
- The check that the baseline run began on clean code is the ops-log statement "code = 1871fe7d"; git cannot prove the working tree at 01:00 (the paths are unchanged since 21:24 the evening before, which makes a dirty tree unlikely).
