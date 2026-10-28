```yaml
agent: gate-auditor (auditor 2 of 3, Paper 2 GATE)
date: 2026-10-28
brief: Code audit of S2 re-infill, family B (FOIL) and the imagecorruptions suite at commit f938ceab against SAP AD.5, AD.6, AD.9, AB.4, AB.6, AB.8, A3.1, A3.2, A3.4, A3b.1 to A3b.3, A3b.6, A3b.7. CPU only; code not edited.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (AD.5 988-1006, AD.6 1008-1023, AD.9 1043-1051, AB.3 1145-1153, AB.4 1155-1162, AB.6 1171-1178, AB.8 1189-1194, A3.1 1217-1237, A3.2 1239-1248, A3.4 1257-1264, A3b.1 1329-1337, A3b.2 1339-1346, A3b.3 1348-1358, A3b.6 1399-1406, A3b.7 1408-1415)
  - exp_p2/gate/reinfill.py, exp_p2/run_gate_s2.py, exp_p2/gate/analysis_s2.py, exp_p2/gate/gate_driver.py, exp_p2/gate/runner.py, exp_p2/gate/arms.py, exp_p2/gate/pipeline.py, exp_p2/gate/evidence.py, exp_p2/gate/report.py, exp_p2/scoring.py (build, logits_fn), exp_p2/run_gate_m4.py (lines 120-177: the keys S2 reads)
  - exp_p2/gate/foil.py, exp_p2/gate/analysis_foil.py, exp_p2/run_gate_foil.py, exp_p2/gate/fusion.py, exp_p2/gate/data.py, runs/P2-GATE-FOIL/{manifest,pool,leak_check}.json
  - exp_p2/gate/suite.py, exp_p2/run_gate_suite.py, runs/P2-SUITE-SMOKE/{smoke.json,pip-freeze-after.txt}, .venv imagecorruptions-1.1.2.dist-info/direct_url.json
  - tests/exp_p2/test_gate_s2.py, test_gate_foil.py, test_gate_suite.py (read), whole tests/exp_p2 (run)
  - research/paper2/method/IMPL-A-SWAP-S2, IMPL-B-FOIL-SUITE, IMPL-E-INTEGRATION (2026-10-28); research/paper2/related/FOIL-L7-SIGNOFF-2026-10-28.md (first 90 lines); research/paper2/CONFIRM-EVENING-2026-10-28.md (lines 60-85)
coverage: >-
  Read in full: reinfill.py, run_gate_s2.py, analysis_s2.py, foil.py, analysis_foil.py, run_gate_foil.py, suite.py, run_gate_suite.py, gate_driver.py, runner.py. NOT covered: the three
  unrelated-to-scope audited modules (edec.py, epred.py, epred_fit.py) beyond their call signatures and the single-source test; no GPU path (nothing was run on a GPU; behaviour on the real network, real
  peak_gb, torch.multinomial on CUDA with a CUDA generator are untested by anyone); S2 run card (not yet written); SAP text outside the clauses listed; runs/P2-PROBE-02 was not opened (data.probe_image_ids reads
  only selection.json and I did not open it); the FOIL data file was read only through the code's own SHA-256 check and check_pool (read-only). The part-1 audit (Omni, M-stages, E-pred) is another auditor's.
  Audited code state: exp_p2/ and tools/ are byte-identical between f938ceab and HEAD 750ce12e (git diff empty), working tree clean for exp_p2/ and tools/.
claims:
  - statement: "S2 re-infill is true in-network re-masking: flagged image positions are set to the mask id in the network input, the caption is masked in every step, and the network's own image-vocabulary conditional is sampled and written back before the next step; evidence-dropping is not used for the I-* arms."
    status: supported
    evidence: "reinfill.py:80-97 (x[:, cap]=MASK_ID, x[j, img[perm]]=MASK_ID, f(x), x[j,pos]=y+IMG_OFFSET); tests/exp_p2/test_gate_s2.py::test_rows_mask_exactly_the_remaining_set_and_the_caption_and_nothing_else (481 passed)"
    level: E3 (code read) plus E4 on a fake network
    confidence: 0.9
  - statement: "keep_best implements 'highest chain log-likelihood, ties to the lowest draw index' (A3.2 item 1 (c))."
    status: supported
    evidence: "reinfill.py:102-104 (np.argmax returns the first maximum); test_gate_s2.py:122-124; run_gate_s2.py:185 uses it for every arm but ileak; my scratch test (scratchpad/aud/test_aud_s2.py::test_keep_best_nan_and_ties) passes"
    level: E4
    confidence: 0.95
  - statement: "I-RAND4 has equal gate size item by item, a new uniformly random set per draw, independent of G."
    status: supported
    evidence: "run_gate_s2.py:139-140 (scattered_gate(g, m, rng) with g = |G|, rep = draw index); test_gate_s2.py::test_irand_sets_have_gate_size_are_new_per_draw_and_ignore_the_gate_content"
    level: E4
    confidence: 0.9
  - statement: "Arm random streams are indexed by the fixed ARM_ID and COND_INDEX, so dropping I-CHG (or the splice cell) changes no draw of I-GATE or I-RAND4 (A3b.2 item 6)."
    status: supported
    evidence: "run_gate_s2.py:46-48, 133-147; one-item test written by the auditor, process() with arms igate,irand,ichg against igate,irand on 3 items x 2 conditions: rows (json-compared, NaN-safe) and the codes/set/logp arrays of igate and irand are bit-identical (scratchpad/aud/test_aud_s2.py::test_ichg_cut_leaves_igate_irand_bit_identical, passed). The repository has no such test."
    level: E4
    confidence: 0.9
  - statement: "Both the kept-draw contrast (exact McNemar, Holm m = 2) and the draw-level and all-four-correct contrasts (paired bootstrap, 10,000 resamples, stream s2_descriptive, no p) are computed and printed in the same cell record."
    status: supported
    evidence: "analysis_s2.py:80-104; test_gate_s2.py::test_s2_draw_level_and_all_four_contrasts_use_the_four_draws"
    level: E4
    confidence: 0.9
  - statement: "analysis_s2 implements the A3b.1 item 2 and item 3 wording rules (location-claim eligibility depends on the draw-level interval)."
    status: contradicted
    evidence: "analysis_s2.py:127-138 (location_supported uses only the kept-draw p; no eligibility flag; refuted uses only the kept-draw interval; WORDING at 35-37 says 'better placed' without the draw-level condition)"
    level: E3
    confidence: 0.95
  - statement: "Figures are decoded only in the separate --figures stage, after the S2 fold is complete; the scoring stage never decodes; per-row peak_gb is logged; no full-vocabulary logits are held across steps."
    status: supported
    evidence: "run_gate_s2.py:295-302 (refuses an incomplete fold), 237-270 (process_fig); process() has no decode call; runner.py:179-190 (reset_peak_memory_stats before, max_memory_allocated into row['peak_gb']); reinfill.py:86-96 (slice to image vocab, del lp/y/logits each step)"
    level: E3 plus E4 (fake network); GPU memory itself unmeasured
    confidence: 0.85
  - statement: "FOIL pairing uses annotations[].id, captions are lower-cased with white space collapsed on both sides, the pool is the first 300 eligible pairs (240 fit), and the committed pool passes L0 to L8; the checker stops (LeakCheckFailed, runner exit 2) on every injected leak and is not vacuous."
    status: supported
    evidence: "foil.py:137-169, 262-354; runs/P2-GATE-FOIL/pool.json (240 fit, 300 test, all lower case, 300 distinct pair ids and image ids, 0 identical pairs; pool sha256 edc3b227...3616); foil.check_pool() re-run read-only by the auditor: ok True, L6 counts cal 240 / head 75 / test 238 / test_ext 159 / probe 383, selftest ok with 7 known-bad cases caught; run_gate_foil.py:38-54, 114-118"
    level: E4
    confidence: 0.9
  - statement: "The fusion endpoint follows AD.6 (LDA weights on the fit pairs, best direction by fit accuracy with ties to text, rule (i) fit >= 100, rule (ii) ceiling >= 0.95 stops the test stage, exact McNemar, b > c_cnt, completed n >= 120 else descriptive); the test stage refuses unless fusion_frozen.json is committed with status ok."
    status: supported
    evidence: "foil.py:368-419; run_gate_foil.py:47-52; test_gate_foil.py (fit_b1 status rules, tie to text, descriptive below 120, runner refusal)"
    level: E4
    confidence: 0.9
  - statement: "For the preregistered outcomes not_estimable and untestable_at_ceiling the CPU analysis records p = 1 and the A3.4 item 3 wording."
    status: contradicted
    evidence: "analysis_foil.py:87-88 raises FileNotFoundError('no test rows') before fusion_b1 can return its p = 1 record; reproduced in scratchpad/aud/test_aud_foil.py (status untestable_at_ceiling, analysis.json not written). The existing test (test_gate_foil.py:387-394) writes 5 test rows that the real runner would never produce."
    level: E4
    confidence: 0.95
  - statement: "The recorded sensitivity at the first 150 positions (S2: first 150 items; B: first 150 pool positions) exists in the analysis code."
    status: contradicted
    evidence: "grep for sensitivity / [:150] in analysis_s2.py, analysis_foil.py, foil.py, run_gate_s2.py: no hit other than the N_SAP_TEXT constant"
    level: E3
    confidence: 0.95
  - statement: "The suite is exploratory only, uses the audited edec/epred functions, applies the four types at severities 2 and 4, and the installed package is the pinned commit."
    status: supported
    evidence: "suite.py:29, 206-231 (edec_mod.edec_cell, epred.epred_agreement, epred_fit.epred_fit; no p-value kept; 'Tier 3, exploratory' label); test_gate_suite.py::test_the_suite_calls_the_audited_edec_and_epred_not_copies and ::test_installed_package_is_the_pinned_commit; .venv imagecorruptions-1.1.2.dist-info/direct_url.json commit_id c959e659c9713837d2acd7ce785a81202d4be799; runs/P2-SUITE-SMOKE/smoke.json (40 calls, all deterministic, 0 types dropped)"
    level: E4
    confidence: 0.9
competing_explanations: []
unknowns:
  - "Behaviour of reinfill on the real UniDisc network (torch.multinomial with a CUDA generator, peak_gb at batch 4, real g_i distribution): never run."
  - "Whether the S2 run card, the pinned commit of card v4 and Shlok's n = 300 confirmation row (A3b.6) exist: none was visible at audit time (CONFIRM-EVENING item 9 is a question, not an answer)."
  - "Content of edec.py, epred.py and epred_fit.py (audited by part 1, not by me); I checked only that the suite calls them."
next_test: {hypothesis: "after the MAJOR fixes the S2 and B analyses emit only wording the SAP allows", intervention: "diff re-check of analysis_s2.py, analysis_foil.py, foil.py plus tests on synthetic tables", primary_metric: "each finding M1 to M5 closed with file:line", falsifier: "any analysis output sentence that claims location, fusion or repair outside the A3b rules", gpu_hours: 0}
```

# Gate-code audit, part 2: S2 re-infill, family B (FOIL), imagecorruptions suite

Commit under audit: **f938ceab** (exp_p2/ and tools/ unchanged at HEAD 750ce12e). Tests: `tests/exp_p2` with the project `.venv`: **481 passed, 5 skipped** (the five skips are the omni-stack tests that need `.venv-omni`, IMPL-E section 5), 160 s. Two scratch test files of mine (not committed, not in the repository) are in `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\aud\` (test_aud_s2.py, test_aud_foil.py).

KEEP_BEST-CHECK: PASS

## Verdict: PASS WITH FIXES

No BLOCKER. All three GPU runners are correct against the SAP clauses I could check on a fake network, and nothing found would corrupt the data they write. Five MAJOR findings concern the CPU analysis modules (wording, sensitivity, one crash). They must be fixed **before the card v4 pin** (A3b.7 item 1: an edit after the pin needs a dated row), and I re-check the diff before the first family item (AB.8: a family whose code is not matched by then is "not run"). Fixing them needs no GPU and changes no row format the runners write.

Preconditions outside the code that this verdict does not waive: (a) A3b.6 item 3, no S2 or B item before Shlok's explicit confirmation of n = 300 at the updated cost is a dated row; at audit time `CONFIRM-EVENING-2026-10-28.md` item 9 is still a question and no code gate enforces it (run_gate_s2.py and run_gate_foil.py default to 300); (b) the S2 run card with the sampler specification (A3b.2 item 2); (c) the I-CHG cut, if any, decided before the first S2 item (A3b.2 item 6).

## 1. Criteria table (S2)

| Criterion | Status | Evidence |
|---|---|---|
| True in-network re-masking, not evidence-dropping | met | reinfill.py:80-97: caption set to MASK_ID (line 81), flagged positions set to MASK_ID (83), forward pass (86), image-vocab fp32 log-softmax, `torch.multinomial` with a per-draw generator, token written back (91-94), k_s = ceil(\|U\|/(S_r-s+1)) per step. The test records every input row and checks that exactly the remaining set and the caption are masked. NONE and M are gathers (run_gate_s2.py:171-172) as AD.5 says |
| Tie rule | met | reinfill.py:104 `int(np.argmax(...))` returns the first maximum; test lines 122-124 |
| Auditor check of `keep_best` (A3.2 item 1 (c)) | **met**, see MINOR m1 | KEEP_BEST-CHECK: PASS |
| Equal gate size for I-RAND4 | met | run_gate_s2.py:139-140; test_gate_s2.py:138-154; reinfill.py:64 asserts one size per call |
| Arm seed streams indexed by fixed ARM_ID | met | run_gate_s2.py:46 `ARM_ID`, 48 `COND_INDEX` (patch 0, splice 1, so a cut cell moves nothing), 145-146; ORDER_TAG distinct tags 6/8/9/10, set tag 7, sample tag 11 (arms.py:58). Bit-identical with and without I-CHG: my one-item test (3 items, both conditions) passed. The repository's tests check seed distinctness only; see m5 |
| Draw-level and kept-draw contrasts both computed | met (computation); wording not (M1) | analysis_s2.py:92-94 |
| Figures only in `--figures`, after the fold | met | run_gate_s2.py:295-302 raises unless every planned row exists; `process()` never decodes; figure subset rule uses no outcome for "first 8", outcomes only for harm cases (206-214), as AD.5 allows after the fold |
| Memory hygiene | met on the code read; GPU unmeasured | slice and delete per step (reinfill.py:86-96); the transient is one [4, L, 48385] bf16 tensor; `peak_gb` per row from `max_memory_allocated` reset per item (runner.py:179-190); figure stage calls `_free_gpu()` |
| Y on all 1,024 repaired tokens, ties wrong, gathered from the two caption-only tables | met | run_gate_s2.py:158, 184; evidence.py:41 `y = mean > 0` |
| G read from M4, never recomputed; keys match M4 | met | S2 reads `<cond>_flag0.05`, `_codes`, `_z`, `clean_codes` and `img[...]["none"/"gate0.05"]["y"]`; run_gate_m4.py:140, 153, 162, 169 write exactly these |
| Descriptive references beside every test (I-GATE vs NONE, M, I-CHG; I-RAND4 vs NONE), no p | met | analysis_s2.py:88-91, `_no_p` |
| Smoke whose Y values are not read (A3.2 item 2, A3b.7 item 4) | **partly** | No script exists that prints only `peak_gb`, `seconds`, `n_rows` (see M5). IMPL-A's smoke command writes Y into items.jsonl |
| A3b.1 items 1 to 4 (draw-level beside every kept-draw result; eligibility; opposite direction; disclosure sentence) | **partly** | Item 1 met (same record). Items 2 to 4 missing (M1) |
| A3b.2 item 1 (no "G.1" in the S2 header) | partly | m2 |
| A3.1 item 3 / A3b.6 item 5 (sensitivity at 150; partial-prefix label with MDE) | **missing** | M2 |

## 2. Criteria table (family B)

| Criterion | Status | Evidence |
|---|---|---|
| Lower-casing on both sides | met | foil.py:137-140 `norm_caption`, applied to c+ and c- in `build_pairs` (164); the c+ and c- of all 540 pool pairs are lower case (checked) |
| Pairing by `annotations[].id` | met | foil.py:143-169 asserts for the whole file that every id is exactly one original plus one foil on one image; pair = first record of the image; matches the steward's independent check (FOIL-L7-SIGNOFF claim 1) |
| L0 to L8 actually stop on failure | met | `foil_leak_check` raises `LeakCheckFailed` (foil.py:312-314); `check_pool` runs `selftest()` first and raises if the checker misses a known leak (459-461); run_gate_foil.py:114-118 turns it into exit 2 before the model loads. I re-ran `check_pool()` read-only: ok, L6 counts non-zero in all five groups (a missing probe `selection.json` would make `probe_image_ids` return an empty set, but L6 then fails, so that is not silent) |
| n = 300 primary | met | pool.json: 300 test, 240 fit, 298 and 239 after the pool-time token rule; 238 + 62 on P test-fold images (disclosed) |
| First 150 pool positions as the sensitivity (A3b.3 item 8) | **missing** | M2 |
| Fusion endpoint | met | foil.py:368-419 |
| Ceiling rule (ii) exactly as written | met | foil.py:384 `best_acc >= 0.95`; status `untestable_at_ceiling`; run_gate_foil.py:51-52 refuses the test stage; |
| Ceiling case recorded as p = 1 with the A3.4 item 3 wording | **missing** | M3 |
| Untriggered-case wording (A3b.3 item 6) and the required limits | **missing** | M4 |
| fusion_frozen.json committed before the test stage | met | `require_committed` (foil.py:423-434), called at run_gate_foil.py:49; tested on a temporary repository |
| Analysis uses the committed weights, refuses a partial fold | met | analysis_foil.py:81-92 |

## 3. Criteria table (suite)

| Criterion | Status | Evidence |
|---|---|---|
| Exploratory only, no claim language in outputs | met | suite.py:220 strips p, p_mid, ci9833, ci90, equivalence flag; output label (227) "Tier 3, exploratory. No p-value enters a claim"; grep for support/improve/reject/claim finds only that label |
| Audited edec/epred, single source | met | suite.py:29 imports the modules; 209-224 call `edec_mod.edec_cell`; 230 `epred.epred_agreement`; 201 `epred_fit.epred_fit`; the single-source test passes |
| Pinned commit c959e659c9713837d2acd7ce785a81202d4be799 | met (declared and installed); not verified at run time, m4 | direct_url.json in the venv carries that exact commit_id; pip-freeze-after.txt shows the git URL at the commit; suite.py:33 declares it |
| 4 types x severities 2 and 4, a missing type dropped not replaced | met | suite.py:35-37, 68-72; run_gate_suite.py:87-91 records `suite_types.json` |
| Items: 100 headroom + first 100 test, seed from item id | met | run_gate_suite.py:62-69; suite.py:50-52 |
| Corruption determinism incl. impulse_noise | met | suite.py:75-91 (seeded wrapper); smoke.json: 40 calls, all deterministic, random types vary with seed |
| Memory | met on the code read | run_gate_suite.py:112 frees the corrupted image after its encode |
| E-pred sign agreement over the 8 cells (AD.9) | partly | the library function exists; the CLI never calls it (m3) |

## 4. Findings

### MAJOR (fix before the card v4 pin; I re-check the diff)

**M1. analysis_s2 does not implement A3b.1 items 2 to 4 (C3-1).**
`analysis_s2.py:127-138`: `location_supported` is `tested and b > c and p_holm < 0.05` only. A3b.1 item 2 makes a kept-draw rejection "location-claim-eligible" only if the draw-level 95 percent CI excludes 0 on the same side, and otherwise permits only the sentence "under best-of-4 selection by chain log-likelihood, repairing the GATE-M set gave higher image-direction verification accuracy than repairing equal-size random sets" with no location claim. The code has no eligibility flag, and `WORDING` (lines 35-37) / `e["sentence"]` (138) says "the flagged set was better placed than a random set of equal size" for every supported cell. Item 3 (opposite direction): `location_refuted` (132) looks only at the kept-draw interval, not at "kept-draw or draw-level". Item 4: the disclosure sentence ("In I-GATE the four draws share one position set; in I-RAND4 each draw has its own random set; ...") appears nowhere in the output. The A3b.2 items 3 and 4 sentences (the one S2 may claim; the I-RAND4-may-be-worse-than-NONE note) are not emitted either. Fix: add `location_claim_eligible` (kept-draw rejected, b > c, and `draw_level... ci95[0] > 0`), choose the sentence by it, make `location_refuted` use either interval, and emit the disclosure and the A3b.2 item 3 and 4 sentences. Closes: A3b.1 items 2 to 4, A3b.2 items 3 and 4.

**M2. Sensitivity prefix and partial-prefix labelling are not implemented (A3.1 items 2 and 3; A3b.3 item 8; A3b.6 item 5).**
No code computes the exact McNemar, b, c_cnt and CI on the first 150 items (S2) or the first 150 pool positions (B), labelled "sensitivity (SAP n = 150), not confirmatory, not in the Holm set", nor the "sensitive to n" statement. `analysis_s2.completeness` (146) only sets `below_80_percent`; the label "partial prefix (under 80 percent of plan)" with the MDE of the A3 power table for the completed n (completed 120 to 239) is not printed for S2 or B. For B the sensitivity must be keyed on pool position (`idx` is in every row, runner.py:188) and exist only if the prefix covers 150 positions. Fix in analysis_s2.py and analysis_foil.py/foil.fusion_b1.

**M3. `analysis_foil analyze` crashes on the preregistered outcomes not_estimable and untestable_at_ceiling (AD.6 rules (i) and (ii); A3.4 item 3; A3b.3 item 5).**
`analysis_foil.py:87-88` raises `FileNotFoundError("no test rows ...")` when the test run has no rows, which is exactly the situation after the runner refuses the test stage (run_gate_foil.py:51-52). `foil.fusion_b1` already has the p = 1 branch (foil.py:404-406) but is never reached. Reproduced: a fit with the text direction at accuracy 1.0 gives status `untestable_at_ceiling`; `analyze` raises and writes no analysis.json (scratchpad/aud/test_aud_foil.py). The existing test passes only because it writes 5 test rows. Impact: the "ceiling" outcome, which A3.4 item 3 calls a legitimate result, would have no p = 1 record and no required wording ("the best single direction met the preregistered ceiling on the fit pairs; text-only cues are not excluded as a cause"); the status exists only in fusion_frozen.json. Fix: branch on `frozen["fit"]["status"] != "ok"` before reading test rows; write analysis.json with p = 1, the status and that wording.

**M4. Family B output wording conflicts with A3b.3 item 6 and omits the required caveats (C3-3).**
`foil.py:414` (`wording`: "supports 'fusion helps' (...)") and the key `supports_fusion_helps` (412) are the sentence A3b.3 item 6 forbids in spirit ("In no case does a sentence say that FOIL tests, shows or supports fusion of image and text evidence"); the rejecting case must read "the combination of the two UniDisc scores beat the better single score on these FOIL pairs; part of the gain may come from text-only cues; no text-only baseline was run" followed by the fit/test mix numbers (ball to racket 11 of 300 against 1 of 240; a/an 15 of 300 against 7 of 240) and "the combination weights were fitted on the same negative type but not the same mix of negatives"; the non-rejecting case must carry "minimum detectable net gain at the achieved n is ...". `analysis_foil.py:97-100` `limits` lacks the text-only-cue risk, the mix difference, the three label-noise numbers of A3b.3 item 2 and the attainable-gain cap of item 7. AD.6/A3.4 item 3 allow the phrase "supports 'fusion helps' only with b > c_cnt" as a rule, so the rule logic is right; the emitted sentences need replacing. The `reason` string at foil.py:405 also lacks the ceiling wording (see M3).

**M5. The S2 smoke has no firewall script (A3.2 item 2; A3b.7 item 4).**
The condition is a script that prints only `peak_gb`, `seconds`, `n_rows` and nothing else, recorded in the run card. None exists. IMPL-A's command (`python -m exp_p2.run_gate_s2 --run-id P2-GATE-S2-SMOKE --n 3 --limit 3`) writes the Y values and arm records into items.jsonl and arrays where anyone can read them. Either write the script (and have it checked) before any smoke, or do not run the smoke. This does not block the S2 run itself.

### MINOR

**m1. `keep_best` has no NaN guard** (reinfill.py:104). `np.argmax` treats NaN as the maximum, so a NaN chain log-likelihood would silently select that draw. NaN is not expected (finite bf16 logits, fp32 log-softmax), but a `np.isfinite` assertion would make the A3.2 rule total.

**m2. "G.1" strings superseded by A3b.2 item 1 remain.** `analysis_s2.py:34` `COMPARATOR = "random-gate best-of-4 re-infill (G.1-inspired)"` goes into analysis.json (`comparator`); `run_gate_s2.py:51` writes the same into each run's config.json; `forbidden_wording` (analysis_s2.py:148) tells readers to write "G.1-inspired"; test_gate_s2.py:381 asserts the old string. A3b.2 item 1 allows "G.1" only in running text followed by "the sampler differs from UniDisc's in order, schedule and guidance". Rename before the pin (the config string is part of the pinned commit).

**m3. Suite: the E-pred block cannot be produced from the CLI.** `suite.py:256` calls `suite_cells(df, fold="test", n_boot=...)` with no `s_c`; `epred_signs` (190-203) is never called by `analyze`, and no code reads the headroom arrays into it. AD.9 lists the 8-cell sign agreement among the outputs. Exploratory and first to be cut, so MINOR, but wiring it after outcomes exist would be an unlogged post-hoc edit; wire it (or declare it "not produced") before the pin.

**m4. Suite: pinned commit is declared, not verified at run time.** `_versions()` records `imagecorruptions 1.1.2`, the same string as the broken PyPI release; `suite_types.json` and config.json carry the commit only as the constant `PACKAGE["commit"]`. The install is correct today (direct_url.json), and a test asserts it, but a run on a different interpreter would record the pinned commit regardless. Read `direct_url.json` in `load_package()` and assert equality.

**m5. The repository has no test for the I-CHG cut (A3b.2 item 6).** The condition says "one-item test ... as part of the pre-family code match". I ran it (passed, see claims); add it to test_gate_s2.py so the pinned commit carries it.

**m6. `analysis_s2` does not enforce the prefix rule** (analysis_s2.py:118, 146): `completeness.prefix_ok` is computed but `tested` depends only on `n_completed >= 120`. The runner writes strictly in list order and stops at the first failure, so a gap cannot arise in normal operation (8.1); an assertion would make it explicit. Same for `analysis_foil.analyze`.

**m7. run_gate_foil rewrites the committed `runs/P2-GATE-FOIL/leak_check.json` at every chunk** (run_gate_foil.py:45). The pre-GPU committed evidence is overwritten by a log with a new timestamp (the file is tracked; the tree becomes dirty under `runs/`, which the dirty-tree guard does not watch). Write the per-chunk log into the run directory instead. Also `analysis_foil.analyze` does not compare `frozen["pool_sha256"]` with the current pool.

**m8. RuntimeWarning "invalid value encountered in divide"** from `np.corrcoef` in `fit_b1` on constant margins (test_best_direction_tie_goes_to_text). `stouffer_r` becomes NaN in that degenerate case, which would then be written to fusion_frozen.json; harmless for the confirmatory path (LDA only), but guard it.

## 5. What was not checked

GPU behaviour of every runner; the S2 run card and card v4; the part-1 modules; the SAP clauses outside those listed; whether the 5 skipped tests pass in `.venv-omni` (IMPL-E reports a PASS, not re-run here).

## 6. Statement on independence

I did not write this code. I changed no file under `exp_p2/`, `tests/`, `tools/` or `runs/`. The two scratch tests live outside the repository. I did not open `runs/P2-PROBE-02/` or any array.
