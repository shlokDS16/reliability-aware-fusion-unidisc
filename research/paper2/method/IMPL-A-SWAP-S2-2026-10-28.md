```yaml
agent: lab-engineer (implementer A)
date: 2026-10-28
brief: Paper 2 GATE: swap condition in M4 (family PS, PS2) with ps_family; S2 re-infill (n = 300) with sampler, runner, analysis and figure stage. CPU only.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (AD.4 976-987, AD.5 988-1007, AD.11-AD.13, A2.5 860-868, AB.2-AB.9, AD.10 disclosure)
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (11.1 M4, 11.2 S2) and GATE-METHOD-SPEC-2026-10-28.md (Algorithm 6 lines 418-428, Prop. 6-7, 11 baselines)
  - exp_p2/{run_gate_m4,scoring,common,core,run_probe1}.py, exp_p2/gate/{runner,pipeline,corruptions,arms,seeds,analysis_m4,report,stats,evidence,scores,folds,config,headroom,gate_driver}.py
  - exp001/unidisc_net.py; models/third_party/unidisc/model_eval.py (_sample 2109-2455, _maskgit_update 3046-3117), checkout HEAD 3ee3e47a9e64bac2fdca59957726f14723371ced
  - runs/P2-PROBE-01/{items.jsonl,config.json}, runs/P2-M0-STAGE1/stage1.json, runs/P2-M0-STAGE2/{items.jsonl,chunks.jsonl}, probes/PROBE2-CRASH-DIAGNOSIS section 3 H4 line 38
coverage: >-
  Read in full: the SAP clauses above, Algorithm 6 and Props 6-7, the runner and M4 code. NOT read: runs/P2-PROBE-02 (nothing opened), the rest of the SAP (sections 1-8 outside the clauses named), UniDisc App. G.1 (not available here;
  the comparator keeps the name 'random-gate best-of-4 re-infill (G.1-inspired)'). Nothing was run on a GPU; no number below comes from a new run.
claims:
  - statement: "Swap is an M4 condition after patch (default --sanity patch,swap); no earlier condition's rows, arrays or seeds change when it is added; patch codes are bit-identical to the old formula."
    status: supported
    evidence: "tests/exp_p2/test_gate_swap.py (test_adding_swap_does_not_change_any_earlier_condition_nor_its_seeds, test_swap_stream_is_its_own_and_patch_is_bit_identical_to_the_old_formula), commit f58cd32c"
    level: E4
    confidence: 0.9
  - statement: "ps_family implements AD.4/AD.13: m = 2 with p = 1 fill, Holm, right-sign rule, met / partly met / not met, R3 via Wilcoxon on d."
    status: supported
    evidence: "tests/exp_p2/test_gate_swap.py (8 ps_* tests with known b, c)"
    level: E4
    confidence: 0.85
  - statement: "The S2 sampler follows SAP AD.5 (S_r = 16, fixed random order, unguided, caption masked, n_draw = 4, best-of-4 by own caption-masked likelihood) and re-masks in the network input; rows, masks, chain likelihood and draw independence are checked on a fake network."
    status: supported
    evidence: "tests/exp_p2/test_gate_s2.py (reinfill tests); GPU behaviour not run"
    level: E4 (CPU, fake network); E3 for the UniDisc code reading
    confidence: 0.8
  - statement: "S2 at n = 300 is about 3.9 GPU-h busy (upper bound, 386 rows per item), about 8 h wall at duty 0.5."
    status: unknown
    evidence: "ESTIMATE, section 5 below; per-row time measured in P2-PROBE-01, row count derived from the code, g_i >= 16 assumed"
    level: E1 (estimate)
    confidence: 0.6
competing_explanations: []
unknowns:
  - "Peak allocated memory of S2 on the GPU (design keeps it at the M4 batch level; not measured)"
  - "Distribution of g_i in M4 (decides the real pass count; 386 rows per item is the upper bound)"
  - "Whether the chain log-likelihood is what the SAP meant by 'own caption-masked likelihood' (section 6, item 3)"
next_test: {hypothesis: "S2 stays at or below M4's peak allocated memory", intervention: "S2 smoke on 3 items after M4 has 3 items (command in section 4)", primary_metric: "peak_gb and seconds per item in runs/P2-GATE-S2-SMOKE/items.jsonl", falsifier: "peak_gb above 8.3 or whole-GPU above 9,000 MiB", gpu_hours: 0.02}
```

Commit of the code: **f58cd32c** (branch claude/frosty-clarke-209639). Whole suite: 312 passed, 17 skipped under the default python 3.14 with `CUDA_VISIBLE_DEVICES=""` and `--ignore=tests/exp_p2/test_omni_scorer.py` (that file is another agent's, untracked, and fails to collect with a SyntaxError). Before my change the suite had 209 passing tests; my two new files add 41.

## 1. What maps to which SAP clause

| Item | SAP / spec clause | Where |
|---|---|---|
| Swap condition in M4, parameters 15 percent uniform random codes (`config.SWAP_FRAC`), always tested | AD.4 PS2, A2.5, AB.7 item 2 | `exp_p2/run_gate_m4.py` (`SANITY_ALL`, `parse_sanity`, `build_conditions`, `--sanity`), `corruptions.token_rng`, `TOKEN_RNG_TAG` |
| Swap seeds | brief: new streams must not shift existing ones | corruption stream `[SEED_GATE, gid, 191]` (patch keeps 190, M3 100-125/150, M5 300, groups 99); swap appended after patch so condition indices, hence `arm_rng(seed, gid, ci, tag, rep)`, of every earlier condition are unchanged |
| Swap arms and rows | AD.4 (same fold, endpoint, test as P) | identical arm set to patch: none, gate0.05/0.01/0.10, geo0-2, scat0-2, topkB, topks3, chg; arrays `swap_*` |
| `ps_family(df)` | AD.4, AD.11, AD.13 | `analysis_m4.ps_family`, `descriptive_ps`; also called from `analysis_m4.run` (key `ps`) |
| Analysis seeds | AD.13 order, appending only | `seeds.ANALYSES` += `ps_family`, `s2_family`, `s2_descriptive` |
| S2 sampler | AD.5 (S_r = 16, fixed random order, n_draw = 4, caption masked, keep highest own caption-masked likelihood), v1 Algorithm 6 | `exp_p2/gate/reinfill.py` |
| I-GATE, I-RAND4, I-CHG, optional I-LEAK, NONE, M | AD.5 arms, AB.4 item 1 (name) | `exp_p2/run_gate_s2.py` (`process`, `_arm_sets`) |
| G read from M4, not recomputed | AD.5 "Gate" | `process` reads `<cond>_flag0.05`, `<cond>_codes`, `<cond>_z`, `clean_codes` from `runs/P2-GATE-M4/arrays` |
| Items = prefix of the ordered test list; M4's exclusions, not replaced | AD.5, AD.8, 8.1 | `plan_items` (same cut and exclusion logic as M4's `get_items`, token exclusions read from M4's `token_exclusions.json`) |
| Conditions: patch (PS1 parameters) and splice at its `family.json` operating point; no operating point means the cell is not run | AD.5 | `s2_conditions` |
| Y on all 1,024 repaired tokens, ties wrong; scored by gathering from the two caption-only tables | AD.5 "Endpoint" | `pipeline.caption_lambdas` (2 passes per item, shared by all arms), `pipeline.image_delta`, `evidence.evidence_from_delta` |
| Y of each of the 4 draws, kept draw, chain likelihoods | AB.4 item 4 | row fields `y_draws`, `d_draws`, `kept`, `logp` |
| Token-level agreement (renamed), recall, precision | AB.4 item 5, AD.5 | row fields `agree_changed`, `agree_set`, `recall`, `precision` |
| Family S2: I-GATE vs I-RAND4, exact McNemar on the kept draw, b > c, Holm m = 2, p = 1 fill, n >= 120, g_i = 0 stays in n and is counted | AD.5, AD.13, AD.8 | `analysis_s2.s2_family` |
| Descriptive in the same table, no p: I-GATE vs NONE, M, I-CHG; I-RAND4 vs NONE; draw-level accuracy; all-four-correct | AB.4 items 2.ii, 4 | `analysis_s2.cell` (`desc`) |
| Claim limits: refutation flag, no-repair flag, wording without "improves", forbidden words listed | AB.4 item 2, AD.5 "May not" | `analysis_s2.s2_family` (`location_refuted`, `repair_helps_claim`, `note_v`, `sentence`, `forbidden_wording`) |
| Figure subset: first 8 items with g_i >= 1 and first 4 harm cases, per corruption; panels clean, corrupted, G overlay, I-GATE, I-RAND4 (kept and draw 1), I-CHG; caption text | AD.5, AB.4 item 5 | `run_gate_s2.select_figure_items`, `process_fig`, `overlay`; `--figures` mode |
| `--stage s2` | brief | `gate_driver.STAGES["s2"]` (only edit to that file) |

## 2. Design choices that matter (and why)

**The sampler is Algorithm 6 as fixed by the SAP, not UniDisc's `_sample`.** UniDisc's entry point is `model._sample(..., x0=, x0_unmask=)` (`model_eval.py:2109`; `UniDiscNet.official_t2i` already drives it). It runs MaskGIT with an arccos schedule, confidence-ordered unmasking with Gumbel noise drawn from the global numpy RNG (`_maskgit_update`, lines 3046-3117), and in the demo configuration classifier-free guidance. AD.5 fixes S_r = 16, a fixed random order and an unguided sampler, and a draw has to be seedable per (item, arm, draw). So `reinfill.py` runs the network through the same `UniScorer.logits_fn` (same forward, same image-vocabulary fp32 log-softmax as scoring) and implements: positions of the set set to [MASK], caption masked, S_r steps with k_s = ceil(|U| / (S_r - s + 1)), the next k_s positions of a permutation drawn up front, sample from the softmax at temperature 1. This is in-network re-masking and re-infilling with the model's own conditional. Spec Algorithm 6 lists max-probability order as primary and random order as an ablation; the SAP is later and binding and says random, so random is used.

**Memory.** Rows of one arm are batched four per forward (the probe and M4 batch size). In each step the logits [rows, L, 48385] are sliced to the sampled positions at once and deleted before the next step (`del logits`). The main run never decodes an image. Two caption-only tables (64 MiB each) are held for the item. S2 does no VQ encode at all: clean and corrupted codes come from M4's arrays. The 8.2 GB probe peak is the first-call VQ workspace (PROBE2-CRASH-DIAGNOSIS H4); S2's scoring process never calls the VQ, and decoding is a separate process (`--figures`, run id `P2-GATE-S2-FIG`) on the preregistered subset only, after the S2 fold is complete (the harm-case rule uses outcomes, SAP 8.2). The runner logs `peak_gb` (`max_memory_allocated`, reset per item) and `seconds` in every row; I add `seconds_cond` and `n_rows`. Expected peak: the M4 level (about 4.1 GB). That is a design expectation, not a measurement.

**Guard stack.** Both modes go through `runner.run_items` exactly as M4 does: hold file, AC check before the load, `--mem-frac`, pins (`require_clean`), per-item guards, the 1 s watchdog with exit 76, soft deadline with exit 75, resume by row count. `tools/gpu_guard.py` is untouched. Under `gate_driver` the gpu_guard wrapper applies as for every stage.

**Prerequisites are checked before the model is touched** (`main` returns 2): family.json with endpoint d; M4 `token_exclusions.json` and folds.json; an M4 row and array for every S2 item with the keys S2 reads. Figure mode also refuses an incomplete S2 fold.

## 3. Rows and arrays

`runs/P2-GATE-S2/items.jsonl`, one row per item: `gid, image_id, caption, neg_caption, n_tok, n_tok_neg, n_rows, seconds, peak_gb (when CUDA), free_ram_gb`, and per condition `conds[cond]`: `g, n_changed, n_tp, recall, precision, m4_y {none, gate}, s2_y_matches_m4 {none, gate}, seconds_cond, arms`. `arms` has `none` and `m` (compact evidence) and for each re-infill arm `y` (kept draw), `d`, `mean`, `kept`, `y_draws[4]`, `d_draws[4]`, `logp[4]`, `n_steps`, `n_set`, `agree_changed`, `agree_set`, `agree_changed_mean`. Arrays `arrays/itemNNNN.npz`: `clean_codes`, `<cond>_codes`, `<cond>_z`, `<cond>_G`, `<cond>_codes_<arm>` [n_draw, 1024] int16, `<cond>_set_<arm>` bool, `<cond>_logp_<arm>`. The S2 directory is self-contained for the figure stage.

## 4. Commands for the GPU runs

All launched only with Shlok's go-ahead and the hold file cleared; nothing below was run.

M4 with swap (start a fresh run; do not resume a run begun before this commit, because `config.json` is written once and swap would appear mid-run). `--sanity patch,swap` is the default:
```
python -m exp_p2.gate.gate_driver --stage m4 --n 300 --extra "--tbv on"
```
Smoke for M4, 2 items: `python -m exp_p2.run_gate_m4 --run-id P2-GATE-M4-SMOKE --limit 2 --soft-minutes 3` (it needs M1-M3 outputs like the real run).

S2 smoke (after M4 holds at least 3 items; separate run id, `--n 3`, about 3 x 47 s of busy time if g_i >= 16):
```
python -m exp_p2.run_gate_s2 --run-id P2-GATE-S2-SMOKE --n 3 --limit 3 --soft-minutes 5
```
S2 (n = 300 is the default; about 40 to 45 chunks at the driver defaults, so raise `--max-chunks`):
```
python -m exp_p2.gate.gate_driver --stage s2 --n 300 --max-chunks 60
python -m exp_p2.gate.analysis_s2 --run-id P2-GATE-S2 --n 300            # CPU, after the fold is complete; writes runs/P2-GATE-S2/analysis.json
python -m exp_p2.gate.gate_driver --stage s2 --run-id P2-GATE-S2-FIG --n 300 --extra "--figures"      # GPU, after the table; about 24 items, 8 decodes per condition
```
Optional cuts inside S2: `--arms igate,irand` drops the oracle I-CHG; `--leak` adds the caption-visible demonstration (off by default; first to be cut). PS analysis needs no new command: `python -m exp_p2.gate.analysis_m4` now writes the `ps` block.

## 5. Time estimate for S2 at n = 300 (ESTIMATE, not a measurement)

- Per-row network time, measured: P2-PROBE-01, 300 items, median busy time 7.022 s per item; 58 forward rows per item (per caption 8 a8 + 8 a8null + afull + afull_null + 8 b8 + 2 b2 + 1 bfull = 29, two captions; true for captions of 8 or more tokens) gives 7.022 / 58 = 0.121 s per row at batch 4. M0 stage 2 (10 items) median 6.86 s gives 0.118. The spec's 0.15 s is the sensitivity case.
- Rows per item, derived from the code: 2 caption-only rows, plus per condition (patch, splice) 3 arms x 4 draws x min(g_i, 16) steps. For g_i >= 16: 2 + 2 x 3 x 64 = **386 rows**. Without I-CHG: 2 + 2 x 2 x 64 = **258 rows**. If g_i < 16 or 0, fewer; the real mean is unknown until M4 exists, so this is an upper bound.
- Busy time per item: 386 x 0.121 = 46.7 s (57.9 s at 0.15); 258 x 0.121 = 31.2 s (38.7 s).
- n = 300: 300 x 46.7 s = 14,019 s = **3.9 GPU-h busy** (4.8 at 0.15 s). Without I-CHG: 9,371 s = **2.6 GPU-h** (3.2 at 0.15). At n = 150 (the SAP text): 1.95 and 1.30 GPU-h.
- Wall time at duty 0.5: busy x 2 = about **7.8 h** (5.2 h without I-CHG), plus one model load per chunk (36 s measured in M0 stage 2, up to 111 s cold in stage 1) over about 40 to 45 chunks, so about 8.2 h. The spec's S2 line said 1.30 GPU-h for 208 passes at n = 150; n = 300 and the added I-CHG and second condition put it at roughly three times that.
- Swap in M4: +8 B rows per item (+1 with TbV), no encode, no text passes: 8 x 0.121 = 0.97 s per item, 300 items = 290 s = **0.08 GPU-h** (0.09 with TbV).
- Figure stage: about 24 items x (1 + 7 per condition) decodes, minutes.

## 6. Ambiguities in the SAP and how each was resolved (no preregistered rule was changed)

1. **n_S2.** AD.5 text says n_S2 = 150; Shlok approved 300 (brief). The code default is 300 and `CONFIG` records `n_sap_text = 150`. A dated addendum row changing the number is needed before S2 outcomes are read (AD.5 power figures assumed 150; the ">= 120 completed" rule is kept literally, it was written "mirroring 240 of 300"). The disclosure (AD.10 item list) should name this.
2. **Order rule.** Spec Algorithm 6 (max-probability primary) against SAP AD.5 (fixed random order). SAP followed.
3. **"Own caption-masked likelihood" for best-of-4.** Not defined further. Used: the chain log-likelihood of the draw, the sum of log pi_j(y_j) over the sampled tokens, computed with the caption masked in every step. It costs no extra pass and cannot see the caption. Alternatives (an extra full-mask pass over the repaired set, an ELBO) were not used. This favours draws with high-probability tokens; the draw-level and all-four contrasts of AB.4 item 4 are there to show it. If the lead means a different quantity, `keep_best` and the rows' `logp` field are the only places to change; the 4 draws' codes are saved, so a different selection can be recomputed on CPU only for scoring-independent rules.
4. **Two-way verification.** The brief says "score two-way verification as M4 scores its arms". The S2 endpoint in AD.5 is the image direction only, and AD.5 forbids any claim about the text direction or fusion, so no text-direction pass is run on repaired pairs. Y is the image-direction decision on all 1,024 repaired tokens.
5. **Swap text-direction arms.** AB.7 item 2 prices swap with text passes (about 0.2 GPU-h). AD.4 defines PS on the endpoint of P (Y or d), and patch has no text arms in M4 (`txt` is empty), so swap has none. If text arms for swap are wanted, that is new code and a changed pass count.
6. **"Draw 1 (not selected)" panel.** Draw 1 is draw index 0. If it is also the kept draw the file is named `..._draw1_is_selected` so that figure-smith can pick another draw or drop the panel; the choice is not made outcome-dependent here.
7. **I-LEAK uses 1 draw** (spec Prop. 7: "run once as a leakage control"); I-CHG uses 4 draws with the same selection rule (AD.5: "same sampler and selection").
8. **Y(NONE) and Y(M) in S2** are recomputed from S2's own two caption-only passes and compared with M4's stored values (`s2_y_matches_m4`); a difference would be a bf16 near-tie and is counted and printed, not corrected.

## 7. Untested, GPU-only paths

`torch.Generator(device="cuda")` with `torch.multinomial` on bf16-derived fp32 probabilities; the real `UniScorer.decode` and the VQ decoder's first-call transient; `peak_gb` under S2's batch-4 forward; the real distribution of g_i (it sets the pass count); `--figures` end to end with the real net; the full `gate_driver` loop for stage s2 (chunk count, `effective_n.json` for the figure run). The CPU tests use `FakeScorer` (real layout and vocabulary ranges, random network), so they establish indexing, masking, seeding, accounting and statistics, not model behaviour.

## 8. Concerns

1. S2 at n = 300 is about 3.9 GPU-h busy and about 8 h wall at duty 0.5 (estimate), roughly three times the spec's line; `--arms igate,irand` saves a third. AD.8 puts S2 last in the cut order.
2. `pins.require_clean` counts untracked files under `exp_p2/` as dirty. Other agents' untracked `exp_p2/omni/`, `exp_p2/gate/suite.py`, `exp_p2/run_gate_suite.py` will make the driver exit 11 until they are committed or `--allow-dirty` is passed. `tests/exp_p2/test_omni_scorer.py` (not mine) has a SyntaxError and breaks collection of the suite.
3. The existing test `test_m4_item_has_75_passes_and_all_arms` still passes only because a bare namespace without `sanity` keeps the pre-swap behaviour; production `main` defaults to `patch,swap`. If that test is meant to describe production, it should pass `sanity="patch"` explicitly or be updated to 84 passes (75 + 8 B + 1 TbV; file not mine).
4. Items 1 and 3 of section 6 need a lead decision or a dated addendum before S2 outcomes are read.
5. The M4 pass count of the spec (75 with TbV, 70 without) is for patch only; with swap it is 84 (78 without TbV) per item. `analysis_m4.py` and the M4 docstring were updated; the spec file was not touched.
