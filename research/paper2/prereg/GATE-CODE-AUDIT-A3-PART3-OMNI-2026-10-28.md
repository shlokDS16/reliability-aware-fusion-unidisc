```yaml
agent: gate-auditor (auditor 3 of 3, Paper 2 GATE)
date: 2026-10-28
brief: Code audit of the Omni-Diffusion 8B 4-bit adapter and family R at commit f938ceab against SAP AD.7, AB.5, A3.5, A3b.4 (C3-4, C3-5), plus review and CPU run of the adapter checks A1 to A7 (OMNI-ADAPTER-CHECKS). CPU only; no code edited.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (AD.7 1025-1034, AB.5 1164-1169, A3.5 1266-1275, A3b.4 1360-1370, A3.8 / A3b.4 item 6 carve-out)
  - research/paper2/method/OMNI-ADAPTER-CHECKS-2026-10-28.md, research/paper2/method/IMPL-C-OMNI-2026-10-28.md, research/paper2/method/IMPL-E-INTEGRATION-2026-10-28.md (row 12)
  - exp_p2/omni/{__init__,layout,loader,scorer,checks,build}.py, exp_p2/run_omni_timing.py, exp_p2/run_gate_omni_r.py, exp_p2/gate/analysis_omni.py, exp_p2/gate/gate_driver.py (omni stages), exp_p2/gate/{runner,guards,watchdog,dcache,folds,corruptions,arms}.py, exp_p2/gate/pipeline.py (gate_scores), exp_p2/core.py (auroc, bootstrap_mean_ci)
  - tests/exp_p2/test_omni_{fakes,scorer,analysis,runners,stack}.py (read; run)
  - Pinned Omni-Diffusion source models/third_party/Omni-Diffusion @ c4f4625f84197a72d556ea00f10e5b2775524252 (git rev-parse confirms): omni_diffusion/models/dream/generation_utils.py 440-540, modeling_dream.py 24, 61, 634-701, 740-830, 1029-1083; modeling_sensevoice.py 8-15 (imports)
  - HF snapshot lijiang/Omni-Diffusion 2233ee1ae2aa2b63e00466197afdeea0ca9e0901 (tokenizer, config, model.safetensors.index.json; no weight file opened), showlab/magvitv2 5c3fa78f... (loaded on CPU for A3)
  - .venv-omni transformers 4.51.3 quantizers/{quantizer_bnb_4bit,base}.py, funasr 1.4.16 and bitsandbytes 0.50.2 present
  - runs/P2-GATE-FOLDS/folds.json (cal 300, head 100, test 300, test_ext 200)
coverage: >-
  Read in full: every file in the scope list. Run: the four CPU omni test files in the project python (32 passed), the five omni-stack tests in .venv-omni (5 PASS, per the one-liner of IMPL-C),
  tests/exp_p2 (464 passed, 22 skipped), the whole tests/ tree (685 passed, 31 skipped, 10 failed, 3 errors, all in tests/exp001, tests/extraction and tests/test_ex_validate.py, which do not import
  exp_p2.omni and were not investigated), plus seven auditor scratch scripts (scratchpad aud1..aud7: independent token facts, exhaustive id bijection, A4 mutations, A5 on synthetic models, call counts of
  from_pretrained, import order, real MAGVIT A3, token rule on the real folds, checkpoint key audit, GO-rule and wording probes). NOT covered: any GPU path (bitsandbytes NF4 kernels on sm_120, the
  quantised load itself, real memory, real time, real logits, A5 numbers); the 4-bit effect on logit quality; the M2/M4 logs that feed p_cal/p_test (M4 has not run); the P analysis; the run card (not yet
  written); GLM-4-Voice and funasr internals; tools/gpu_guard.py (pinned elsewhere).
  Audited code state: `git diff f938ceab HEAD -- exp_p2 tools tests` is empty (HEAD 750ce12e adds only the IMPL-E report); working tree clean for exp_p2/ and tools/. No M4 run directory and no Omni run directory exists yet, so the A3b.4 item 3 tightening window is still open.
claims:
  - statement: "The scorer's one-position logit shift is exactly the sampler's: out[:, i] = logits[:, i-1], position 0 reuses output 0, in both generation branches."
    status: supported
    evidence: "generation_utils.py:526 (CFG branch) and :531 (non-CFG branch) `logits = torch.cat([logits[:, :1], logits[:, :-1]], dim=1)` straight after forward_dream; layout.py:120-124 shift_right(s=1) is that expression; auditor scratch aud1: independent literal read-off written from the source line over the full vocabulary, sliced to the image columns, equals the scorer output with max abs difference 0.0 on a tiny real DreamModel; with the scorer's shift set to 0 or 2 check A4 fails (max diff 0.828)"
    level: E3 plus E4 (tiny real model, CPU)
    confidence: 0.95
  - statement: "The virtual-to-Omni id translation is injective on everything a row can contain, a bijection on the mask and on the 8,192 valid image codes, and is applied only at the model boundary."
    status: supported
    evidence: "layout.py:57-117, scorer.py:64-85 (table lookup inside logits_fn, raw_logits takes real ids); aud1: virtual 32001..40192 <-> 168072..176263 exhaustive, 32000 <-> 151666, 50 random rows round-trip, virtual 40193..48384 and the real mask/image ids refused as text; nothing stored on disk holds a virtual text id (arrays hold codes 0..8191, scores, flags; rows hold caption strings and counts; D cache is keyed by caption length only). The upper 8,192 columns of the UniDisc image slice [32001, 48385) have no Omni counterpart by design (-inf padding; a virtual id in them is refused, scorer.py:74-75)"
    level: E3 plus E4
    confidence: 0.9
  - statement: "The load path uses trust_remote_code=False, offline local snapshot paths, the audio-encoder stub, and a single from_pretrained call; no funasr model is built and nothing is installed."
    status: supported
    evidence: "loader.py:100 (AutoConfig trust_remote_code=False), :111-114 (no trust_remote_code in from_pretrained, local_files_only, use_safetensors), :74-80 (AudioEncoder patched in modeling_dream before construction; modeling_dream.py:763 is the only constructor call); aud3: PreTrainedModel.from_pretrained is called once by loader.load_model and twice by the repo's DreamModel.from_pretrained; importing both runners imports neither transformers nor huggingface_hub, so loader.offline_env() runs first and HF_HUB_OFFLINE is 1 in the hub constants; funasr is IMPORTED (modeling_sensevoice.py:8-15, module level) but no AutoModel/AudioEncoder is built; no pip/subprocess call in exp_p2/omni except `git rev-parse`"
    level: E3 plus E4 (tiny checkpoint, CPU)
    confidence: 0.9
  - statement: "The 4-bit plan quantises exactly the 196 decoder Linear layers (6,525,417,472 of 7,803,763,200 parameters) and leaves lm_head, embed_tokens, audio_projection and audio_model unquantised; every expected checkpoint tensor exists."
    status: supported
    evidence: "aud7: replace_with_bnb_linear on the real-size meta skeleton gives n_linear4bit 196, all in model.layers, plain Linear = lm_head and audio_projection.mlp.0/.2, audio_model 0 parameters, audio_projection 14,681,088 parameters; transformers 4.51.3 quantizer_bnb_4bit.py:298 and base.py:261-277 pass llm_int8_skip_modules to the same function; model state dict 343 keys, all present in model.safetensors.index.json; the 917 extra checkpoint keys are all model.audio_model.*; DreamModel defines no _keep_in_fp32_modules; config tie_word_embeddings False. The quantised load and kernel behaviour on the GPU are untested."
    level: E3 plus E4 (CPU)
    confidence: 0.85
  - statement: "Items 301..300+n_R are disjoint from the first 300 test items (P under R1) and from the calibration items; the Omni token rule excludes without replacement; on the real folds it excludes nothing."
    status: supported
    evidence: "run_gate_omni_r.py:143-154, build.py:139-170; aud scratch: test[300:450] and test[:300] share 0 image ids and 0 idx values, cal[:100] shares 0 with both; Omni tokenizer counts of 1,600 captions (cal, test, test_ext, c+ and c-) range 8..26, 0 outside 5-32, 0 special-token captions; tokens(INSTR + caption) = tokens(INSTR) + tokens(caption) and decode round trip hold for all 1,600"
    level: E4 (CPU, real tokenizer, real folds)
    confidence: 0.95
  - statement: "omni_gate implements the GO rule (a)-(e) with (b) as replaced by AB.5 item 1 and the n_R rule (150, else 120, else NO-GO); the GO rule can be passed by a self-check that contains only A1-A3."
    status: mixed
    evidence: "analysis_omni.py:103-135 matches AD.7/AB.5 (T(n) formula, 50 p_B added, 150 then 120, planned n); hand check T(150) = 0.3 x (1200 + 11250 + 400)/3600 = 1.0708 reproduced by selftest; but analysis_omni.py:120 reads only selfcheck.ids_equal and adapter.all_ok, and checks.summarize (checks.py:196-197) takes all_ok over whatever results are present; auditor probe aud6: omni_gate with a self-check holding only A1, A2, A3 returns go = True with (b) ok (finding M-2)"
    level: E4
    confidence: 0.9
  - statement: "omni_r produces the SAP wording under R1 and R2 but not under R3, and does not implement the A3b.4 item 9 reading of a wrong-direction rejection."
    status: contradicted
    evidence: "analysis_omni.py:208-216, 226-228; aud6: omni_r(rule='R3') returns 'directional replication on a second model, 4-bit quantised; ...' which A3b.4 item 7 says is not available under R3; a rejection with b < c (p_holm 0.0042) returns 'not replicated; inconclusive at this n' where A3b.4 item 9 says 'refutes the direction' (finding M-1)"
    level: E4
    confidence: 0.95
competing_explanations:
  - "A5 may fail or pass on the real model for reasons other than the shift (4-bit numerics, a mis-loaded layer). The checkpoint key audit removes one such cause (no randomly initialised tensor can arise from a missing key); the floors S-3 below remove the 'all shifts equally bad but one slightly less' reading."
  - "A passing positive control proves only non-chance on the code-level patch (A3b.4 item 5); it says nothing about the pixel path or the out-of-distribution masked caption."
unknowns:
  - "Whether bitsandbytes 0.50.2 NF4 kernels load and run on this stack (sm_120); real peak allocation and seconds per pass; real A5 numbers; whether the 4-bit logits can serve a likelihood detector."
  - "Whether M4's n_rows make the committed p_test an upper bound of Omni's per-condition passes (8 B passes per condition plus 2 lambda passes per item): true by construction if M4's rows count the text direction, TbV and lambda passes as IMPL-C says; not checkable before M4 runs."
next_test: {hypothesis: "the 4-bit adapter loads, passes A1-A7 and fits the memory cap", intervention: "gate_driver --stage omni-timing after the lead's decisions on T1-T3 and the conditions in section 5", primary_metric: "selfcheck.json adapter.all_ok with A1..A7 present and the sign-off conditions S-1..S-8 of section 5; median fwd_s of passes 6-20; max peak_alloc_mib", falsifier: "any condition of section 5 not met, a guard stop, or peak_alloc_mib > 7000", gpu_hours: "< 0.2 (IMPL-C estimate, E0)"}
```

# Gate-auditor, Paper 2 GATE, code audit A3 part 3: Omni-Diffusion adapter and family R (commit f938ceab)

## 1. Verdict

**PASS WITH FIXES.** No BLOCKER. Two MAJOR findings (M-1, M-2), both in CPU analysis code that runs **after** the GPU timing stage; neither can change what the timing stage measures. The adapter, loader, scorer, guard wiring and item selection meet every point (a) to (g) of the brief on the evidence a CPU can give. Under the brief's rule ("if PASS, write the signature") **I have not written `runs/P2-OMNI-ADAPTER/adapter_signature.json`**; it is written once M-1 and M-2 are fixed and I have re-run the two probes of section 6 (a ten-minute re-check). The real signature of AB.5 item 1 / A3b.4 item 1 (`runs/P2-OMNI-TIMING/adapter_signature.json`, hash-bound to `selfcheck.json`) is a separate, later act and is not given here.

Decisions the lead must take **before the timing stage starts** (the A3b.4 item 3 window is open: no M4 run directory and no Omni run directory exists as of 15:28 IST): accept or refuse the three tightenings T1-T3 of section 5, and do not pass `--skip-gpu-adapter-checks`.

## 2. Hashes (A3b.4 item 2)

| File | SHA-256 now | SAP value | Match |
|---|---|---|---|
| `research/paper2/method/OMNI-ADAPTER-CHECKS-2026-10-28.md` | 9b429e12df9d8aab6b569d83aeace75652eb78ee2d75454b6891d5bf435dbe55 (working tree = HEAD blob) | 9b429e12...dbe55 | yes |
| `exp_p2/omni/checks.py`, LF (git blob at HEAD, CR stripped) | 9e397f2a3dedcd4a8edf133214d30ed25ee9170ca80a089238435c2217f6c48f | 9e397f2a...c48f | yes |
| `exp_p2/omni/checks.py`, CRLF working tree | 4e196a1fcb2f222818ae70ebe73fd9d48f7a484257227060d53744691a85a5ee | 4e196a1f...a5ee | yes |

The tightenings proposed below are **not** applied to either file, so these hashes stand.

## 3. Criteria (a) to (g) of the brief

| | Criterion | Status | Evidence |
|---|---|---|---|
| a | Dream one-position shift exactly as the source | met | `generation_utils.py:526,531`; `layout.py:120-124`; scorer applies it once, in `to_virtual_logits` (`layout.py:133`). Independent literal read-off equals the scorer to 0.0 (aud1). Both CFG and non-CFG lines are identical. The scorer calls `forward_dream` (as the sampler does; it sets `attention_mask = None`, `modeling_dream.py:1050`) with `input_ids`, the sampler with `inputs_embeds = embed_tokens(x)`; identical embeddings, A4 compares both paths. |
| b | id translation a bijection, at the model boundary only | met | see claim 2. Bijection on mask + 8,192 codes; text/structure ids injective, process-local, never stored; padding columns refused. `table()` maps unallocated slots to 151643 and the padding range to 151666, which a row can never hold (`scorer.py:74` raises first). Minor: `VirtualMap.v` accepts a real id >= 176,264 (`layout.py:66-77`); the tokenizer cannot produce one (m-6). |
| c | trust_remote_code False, offline, no funasr/SenseVoice build, no pip | met | claim 3. Notes: `offline_env` uses `setdefault`, so a pre-set `HF_HUB_OFFLINE=0` would win (m-5); funasr is imported (module level in the repo) but never built. |
| d | 4-bit config quantises only the 196 decoder Linear layers | met on CPU | claim 4; `test_quantisation_plan_on_the_real_size_meta_skeleton` PASS. The realised quantisation on the GPU is not recorded by any file (m-4). |
| e | loader bypasses the double load | met | `loader.py:114` `super(DreamPreTrainedModel, DreamModel).from_pretrained`; call counts 1 (loader) versus 2 (repo) measured (aud3). The bypass skips the repo's `generation_config` assignment (`modeling_dream.py:687-700`); nothing in the adapter reads it. |
| f | timing and R stages go through the guard stack with the proposed flags, preload check, load/self-check watchdog | met, two gaps (m-1, m-2) | `gate_driver.py:54-56` OMNI_FLAGS = mem_frac 0.62, 9500, 9000, 1500, 7000, 2500 (equal to `build.PROPOSED`, `build.py:18`); `run_items` sets `set_per_process_memory_fraction` before the load (`runner.py:122-123`) and checks AC before the load (`:124`); `preload_check` (`build.py:63-71`, fail closed on the 99999 sentinel) runs before any CUDA context (`run_omni_timing.py:121-124`, `run_gate_omni_r.py:260-263`); the load watchdog (`build.py:84`) starts before the snapshot lookup, covers load and self-check with `first_item_active` ceiling 9,500, and is stopped only in `ctx_factory` (after the self-check); `OmniGuards.after_item` adds the 7,000 MiB peak-allocated rule per item (`build.py:28-36`; peak statistics reset per item at `runner.py:179`). Gaps: m-1 (a failed self-check does not stop a relaunch), m-2 (the load and self-check peak is recorded, not gated). |
| g | R items, exclusion, positive control, GO and n_R rules | met, with M-1 and M-2 | items: `run_gate_omni_r.py:143-154`, disjoint (E4 above); exclusion counted by reason, never replaced (`build.py:139-170`; a pair with c+ in range and c- out of range is counted once, under the c- reason, `:155-162`); positive control: `process_pos` patch 4 x 4 of 16 x 16, codes from the 8,192 vocabulary, labels `changed_code_gate`, B and z saved; `omni_positive_control` uses AUROC of -B (the sign probe 2 uses for B, `analyze_probe2.py:94`), lower 95 percent item-bootstrap bound > 0.5, write-once; the `test` stage refuses without `passed: true` (`run_gate_omni_r.py:84-88,115-119`); GO and n_R rule: see claim 6 and M-2. |

## 4. Findings

### BLOCKER
None.

### MAJOR

**M-1. `omni_r` emits wording the SAP forbids, and omits the A3b.4 readings.** `exp_p2/gate/analysis_omni.py:208-216` (wording) and `:226-228` (result record). (i) Under `rule="R3"` a rejection with b > c returns `WORDING_REPLICATED` ("directional replication on a second model, ...") although A3b.4 item 7 states that "directional replication" is not available under R3 and prescribes "the evidence-ratio effect found in P was / was not accompanied by an accuracy change on Omni". Auditor probe aud6: R1 and R3 return the identical sentence. (ii) A rejection with b < c_cnt (probe: p_holm 0.0042, b = 2, c = 14) returns "not replicated; inconclusive at this n"; A3b.4 item 9 says it "refutes the direction". (iii) The result record carries neither the confound list of A3b.4 item 8 nor the positive-control wording of item 5, which the SAP says go "with every R result". No test covers R3 (`tests/exp_p2/test_omni_analysis.py` uses R1 and R2 only). SAP: A3b.4 items 5, 7, 8, 9. **Fix before `analysis_omni r` is run, not before the timing stage:** branch the wording on `rule == "R3"`, add the b < c reading, add `confounds` and `positive_control_wording` fields, add an R3 test and a b < c test.

**M-2. GO rule (b) does not require A1 to A7 to be present; the debug flag can produce a GO-eligible self-check.** `analysis_omni.py:120` accepts `ids_equal` and `adapter.all_ok`; `checks.summarize` (`checks.py:196-197`) computes `all_ok` over the results given; `run_omni_timing.py:101` skips A4-A7 under `--skip-gpu-adapter-checks`, whose help text and the docstring at `:8` say "a timing result without them cannot reach GO". Auditor probe aud6: `omni_gate` returns `go: True`, (b) ok, for a self-check that holds only A1, A2, A3. The only barrier is the human signature, which AB.5 item 1 requires anyway; the code claim is false. SAP: AD.7 (b) as replaced by AB.5 item 1; A3b.4 item 1 (b). **Fix** (`analysis_omni.py`, not a hashed file, not a threshold): `chk_ok` additionally requires `{r["id"] for r in adapter["results"]} >= {"A1",...,"A7"}`; add a test. Until fixed, the lead must not use `--skip-gpu-adapter-checks`, and I will not sign a `selfcheck.json` lacking A1..A7 (S-1).

### MINOR

- **m-1. A failed self-check does not stop the next chunk.** `runner.py:136-143` writes `selfcheck.json` before testing it and returns exit 2; on the next launch `not (run / "selfcheck.json").exists()` is false, the self-check is skipped and the 20 passes run on an adapter already known to fail (the driver, `gate_driver.py:190-212`, treats exit 2 as one chunk without progress and relaunches once). The outcome is still NO-GO (`omni_gate` reads `ids_equal`), so this only burns GPU time, but it is a fail-open edge in a stage the lead wants fail-closed. Generic runner behaviour shared with the UniDisc stages. Suggest: the runner re-evaluates an existing `selfcheck.json` and refuses on a failed one, or the driver stops on exit 2.
- **m-2. Load and self-check peak allocation is recorded but not gated.** `run_omni_timing.py:112-113` stores `peak_alloc_mib_during_checks` (it also contains the load peak, since statistics are reset only per item); the 7,000 MiB rule fires only after an item (`build.py:28-36`), and GO (c) reads only per-pass peaks against `mem_frac x total = 7,581 MiB` (`analysis_omni.py:122-123`). A load/check peak between 7,000 and 7,581 MiB passes every code path. Covered by sign-off condition S-6 (T3).
- **m-3. `_cmd_gate` never passes `crash_events`** (`analysis_omni.py:243-244`), so the "no crash-log event" half of (a) is read only from `chunks.jsonl` events (`guard_stop`, `item_error`, `hold_stop`, `dirty_blocked`); `dirty_allowed` is not among them. The driver's own Windows-event-log refusal (exit 9) covers the normal path; a manual run or `--no-eventlog-check` does not. The run card should state the crash-event reading by hand.
- **m-4. No file records the realised quantisation or load warnings.** `omni_env.json` records versions, pins, allocation after load, but not the count of `Linear4bit` modules in the loaded model nor `loading_info`. The checkpoint key audit (aud7) shows no model tensor can be missing, so the risk is a silent non-quantised or partly quantised load. An unquantised load (about 15.6 GB) cannot fit the 7,581 MiB cap, so it would fail loudly; a partial one would show as `allocated_after_load_mib` outside 5,000-7,000 (S-7). Suggest recording the module count in `write_env`.
- **m-5. `HF_HUB_OFFLINE` is set with `setdefault`** (`loader.py:37`) and none of the documented commands exports it. I verified that in a fresh process it ends up 1 because nothing imports transformers or huggingface_hub before `offline_env()`, and every path is a local directory with `local_files_only=True`; a shell with `HF_HUB_OFFLINE=0` would still win. The run card should export `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`.
- **m-6. Small id-space edges.** `VirtualMap.v` accepts real ids >= 176,264 (`layout.py:66-77`); `table()` maps never-read slots to 151,643. Unreachable with this tokenizer (1,600 real captions: ids all < 151,643).
- **m-7. Report arithmetic.** IMPL-C section 5 states R pass counts of 1,950 to 3,900 for n_R = 150 (formula 2 + 8 x (1 + |P+|) per item); the formula gives 2,700 (|P+| = 1) to 5,100 (|P+| = 3). Prose only; `T_hours` in code is correct (p_test is the committed upper bound from M4, not this count). Also A3 on three real images reports MAGVIT reconstruction PSNR 18.0-18.7 dB (IMPL-C quotes 19-22 dB); reported, not gated; it does not enter the scores.
- **m-8. T(n) uses forward wall time only** (`fwd_s`); MAGVIT CPU encodes (about 0.5 s per condition) and the 0.5 duty sleep are outside t. The 2 x T(n) time rule (e) covers the duty; the encode share is under 5 minutes at n_R = 150. Interpretation noted, not a defect.

## 5. Adapter checks: CPU result and exact GPU pass condition

CPU runs: `tests/exp_p2/test_omni_{scorer,analysis,runners,fakes}.py` 32 passed; `test_omni_stack.py` in `.venv-omni`: 5 PASS (tokenizer layout, tiny real DreamModel A4/A6/A7, micro-batch, quantisation plan, loader call path). Auditor additions: A1/A2 on the real tokenizer (aud4), A3 with the **real** MAGVIT on 3 COCO images (aud4), A4 mutations (aud1), A5 on six synthetic worlds (aud2), key audit (aud7).

| ID | CPU result (auditor-run) | What the GPU `selfcheck.json` must show |
|---|---|---|
| A1 mask id | PASS. tokenizer `<|mask|>` 151666 = config 151666 = layout constant; id->token `<|mask|>`; virtual 32000, 32001, 32006 -> 151666, 168072, 168077; 151666, 168072, 176263 refused as text. Exhaustive 8,192-code table check added (aud1). | `adapter.results[A1].ok` true; `tokenizer_mask == config_mask == layout_const == 151666`; `text_ids_refused == 3`. (Same code as CPU; real config object.) |
| A2 image range | PASS. all 8,192 names `<|image_k|>` = 168072 + k; 176264 = vocab_size = len(tokenizer); id 168071 is `<|audio_16383|>`; padding virtual id refused. | `A2.ok` true, `all_8192_names_match` true, `vocab_size == len_tokenizer == 176264`, `padding_columns_refused` true. |
| A3 layout | PASS with the real tokenizer and the real MAGVIT (3 images, 3 captions; PSNR 18.68, 18.25, 18.00 dB, reported). Extra: concatenation and decode round trip hold for 1,600 real captions. | `A3.ok` true with `n_images == 3`; top-level `ids_equal`, `layout_ids_equal`, `modality_equal`, `mask_row_roundtrip` true, `image_tokens_frac_equal` 1.0, `chat_template_prompt_equal` true. |
| A4 shift code path | PASS at tolerance 0 on a tiny real DreamModel (CPU float32). Non-vacuous: scorer shift 0 or 2 gives max diff 0.828 and A4 fails; independent literal read-off agrees to 0.0. Limit: reference and scorer share the id table, so A4 does not test the translation (A1/A3 and the exhaustive check do). | `A4.ok` true; `max_abs_diff_vs_generation_readoff <= 0.02` (code `atol`; 0.0 expected, both sides use the same kernels on the same row; bf16 spacing is 0.0078 at |logit| 1, so 0.02 still separates a wrong shift, which gives O(1)); `max_abs_diff_vs_shift0 > 0`; `padding_columns_all_minus_inf` true. |
| A5 shift behaviour | Code logic validated on six synthetic worlds (aud2): passes only when the model's output at i carries token i+1 (margin 11.9 nats, top-1 1.0 at s = 1); fails for s = 0, s = 2, s = -1, copy-the-input, and random logits (margins -11.9, -12.0, 0.01, -2.2, -0.01). No unit test of A5 existed before. Not runnable on CPU with a trained model. | `A5.ok` true, `n_rows == 6`, `n_masked_tokens == 384`, `margin_observed >= 1.0`, `top1(s=1) > max(top1(s=0), top1(s=2))` **and** floors T1: `mean_logp(s=1) >= -8.011` (uniform over 8,192 codes is -9.011) and `top1(s=1) >= 0.005`. All three shifts' numbers are read, not only the verdict. |
| A6 stub inert | PASS on the tiny real model: `audio_model` is the stub, 0 parameters, 0 calls, no forward hook fired, `audio_projection` keeps parameters. Real-size skeleton: audio_model 0 parameters, audio_projection 14,681,088. | `A6.ok` true; `audio_model_is_stub` true; `stub_params == 0`; `stub_calls == 0`; `forward_hook_fired` false; `audio_projection_params == 14681088`. |
| A7 cached nulls | PASS on the tiny real model (identical nulls, difference 0). | `A7.ok` true; `max_abs_diff_image_null <= 1e-5` (0.0 expected, identical input rows, batch 1); `n_passes == 2`. |

### Auditor sign-off conditions for the real signature (written now, before any GPU output; they never loosen anything in the checks file)

Signature `runs/P2-OMNI-TIMING/adapter_signature.json` will be written only if **all** hold in the `selfcheck.json` and run directory I am given, and I will state which of them I verified:

- **S-1** `adapter.results` contains exactly the ids A1..A7 once each, all `ok` true, `adapter.all_ok` true, `ids_equal` true (the M-2 gap closed by hand if the code is not yet fixed).
- **S-2** The A-conditions in the table above, read from the file.
- **S-3 (T1, tightening of A5, window open)** `mean_logp(s=1) >= -8.011` and `top1(s=1) >= 0.005`, in addition to the committed margin 1.0 nat and the top-1 ordering. Reason: the committed rule is purely relative, so a model with garbage logits that happens to favour s = 1 by one nat over two worse shifts would pass; a mis-initialised or mis-quantised model must not.
- **S-4 (T2)** `omni_env.json`: `pins_match` all true (omni_sha c4f4625f..., snapshot 2233ee1a..., magvit 5c3fa78f...), `skip_modules` = the four names, transformers 4.51.3, bitsandbytes 0.50.2, `mem_frac` 0.62, `guard_cap_mib` about 7,581.
- **S-5** `stdout-chunk00.log` of the first chunk (not a file the code writes beyond the driver's capture) contains the "not used when initializing" notice for `model.audio_model.*` keys **and no** "newly initialized" / "not initialized from the model checkpoint" notice (the CPU key audit says there is nothing to initialise; this is the GPU-side confirmation).
- **S-6 (T3)** `peak_alloc_mib_during_checks <= 7000` (load plus self-check peak held to the same figure as the per-item rule; estimate 6,000-6,100, E0) and every timing row `peak_alloc_mib <= 7000`, `finite` true.
- **S-7** `allocated_after_load_mib` within 5,000-7,000 (estimate 5,940, E0, used as a sanity band for a partial or missing quantisation, not as a GO rule).
- **S-8** No `guard_stop`, `item_error`, `hold_stop` event in `chunks.jsonl`; a self-check that failed in an earlier chunk (m-1) voids the run.

T1-T3 are tightenings, not new checks in the hashed files. A3b.4 item 3 allows a tightening "in a dated commit that changes the hashes"; I am recording them as signing criteria in this dated audit commit instead, which leaves both hashes unchanged. **If the lead reads A3b.4 item 3 as requiring the change inside `checks.py`, the implementer must commit it before the timing stage and replace the two hashes in the run card and the ledger; I would then re-run section 5 against the new files.** I have not loosened any threshold.

## 6. What converts this to PASS, and what remains pending

1. M-1 and M-2 fixed (CPU, small), with the tests named above; the lead re-runs `python -m pytest tests/exp_p2 -q` and I re-run the two probes (aud6) and the section 5 conditions list. Both are post-timing code, so the timing stage need not wait for M-1; M-2 should be fixed before it so that the machine-read GO cannot be reached with skipped checks.
2. The lead decides T1-T3 before the timing stage and says so in the run card; the run card exports `HF_HUB_OFFLINE=1`, does not use `--skip-gpu-adapter-checks`, and records the crash-event reading (m-3).
3. After the GPU timing stage: I read `selfcheck.json`, `omni_env.json`, `chunks.jsonl`, the first-chunk stdout log against S-1..S-8 and then write the hash-bound signature. `gpu_checks_pending` is true until then. By A3b.4 item 1 the deviations box says "adapter checks executed by the implementer's code and reviewed, not executed, by the auditor", and no document says the adapter was "independently verified".

## 7. Limits of this audit (what a pass does not mean)

- Nothing here says the 4-bit model loads, fits, is fast enough, or that its logits carry signal. Every GPU property is an E0 estimate until the timing stage.
- The CPU evidence for the shift is the source line (E3), an identity on a randomly initialised tiny model (E4) and the logic of A5 on synthetic worlds (E4); the empirical truth of the shift on the trained model is exactly what A5 measures on the GPU.
- Masked-caption contexts are out of distribution for Omni (A3.5 item 7); the positive control proves non-chance on the code-level patch only (A3b.4 item 5).
- The 10 failures and 3 errors in the full tests/ tree (tests/exp001, tests/extraction, tests/test_ex_validate.py) are outside this scope and were not investigated; tests/exp_p2 is fully green (464 passed, 22 skipped).
