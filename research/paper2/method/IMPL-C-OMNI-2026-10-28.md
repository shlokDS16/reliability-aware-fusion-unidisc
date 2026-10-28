```yaml
agent: mdm-expert (implementer C)
date: 2026-10-28
brief: Omni-Diffusion 8B 4-bit adapter for GATE (family R), 20-pass timing/fit stage, gatekept family-R runner, omni_gate / omni_r analysis. CPU only; nothing ran on a GPU.
sources_examined:
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (AD.7 l.1025-1035, AB.5 l.1164-1170, AD.13 l.1095-1099, AD.8, AD.12)
  - research/paper2/team/OMNI-DIFFUSION-SETUP-2026-10-27.md (all, incl. the SenseVoice addendum)
  - research/paper2/debate/DECISION-R1-2026-10-28.md item 6
  - models/third_party/Omni-Diffusion @ c4f4625f84197a72d556ea00f10e5b2775524252 (read only): omni_diffusion/models/dream/{modeling_dream,generation_utils,configuration_dream}.py, data/dataset_qwen2.py, data/processor/image_processor.py, tokenizer_magvitv2.py, models/magvit/modeling_magvitv2.py, tools/inference.py
  - HF cache snapshots (read, not downloaded): lijiang/Omni-Diffusion 2233ee1ae2aa2b63e00466197afdeea0ca9e0901 (config.json, generation_config.json, added_tokens.json, tokenizer_config.json, model.safetensors.index.json), showlab/magvitv2 5c3fa78f8b3523347c5cd1a4c97f3c4e96f33d5d
  - exp_p2/scoring.py, exp_p2/gate/{runner,guards,watchdog,pipeline,scores,dcache,evidence,arms,calibrate,fit_threshold,analysis_m4,report,stats,folds,corruptions,headroom,seeds,artifacts,pins,hold}.py, exp_p2/run_gate_m{2,3,4}.py, tests/exp_p2/fake_gate.py
coverage: >
  Read in full: the SAP clauses above, the setup doc, the Dream model/generation files, the dataset formatting code, the gate stack. NOT read: GLM-4-Voice, funasr, the SenseVoice weights (stubbed), the
  rest of the SAP (only the clauses listed, plus grep for Holm/P_result). No weight file was opened; no GPU, no CUDA context was created by anything I ran (CUDA_VISIBLE_DEVICES="" throughout).
claims:
  - statement: The Omni sampler reads the distribution of the token at position i from the model output at position i-1 (Dream one-position shift); position 0 reuses output 0.
    status: supported
    evidence: omni_diffusion/models/dream/generation_utils.py `_sample`, lines `logits = torch.cat([logits[:, :1], logits[:, :-1]], dim=1)` (both the CFG and non-CFG branch); training uses the standard causal-LM loss (modeling_dream.py `forward` -> self.loss_function)
    level: E3
    confidence: 0.9
  - statement: Training masks only assistant (label) positions, so a masked caption (the SAP's B and D contexts) is outside the training distribution.
    status: supported
    evidence: omni_diffusion/data/dataset_qwen2.py:932-942 (final_masked_indices = masked_indices & labels_mask; user turn labels are IGNORE)
    level: E3
    confidence: 0.9
  - statement: DreamPreTrainedModel.from_pretrained loads the checkpoint twice (the first super() result is unpacked as a tuple and fails).
    status: supported
    evidence: modeling_dream.py:634-701; measured on a tiny checkpoint, CPU, 2026-10-28: PreTrainedModel.from_pretrained is called 2 times by DreamModel.from_pretrained
    level: E4
    confidence: 0.95
  - statement: With skip list (audio_model, audio_projection, lm_head, embed_tokens), transformers' own bnb conversion makes exactly the 196 decoder Linear layers (6.525 B of 7.804 B parameters) 4-bit and leaves lm_head and audio_projection.mlp.0/2 as plain Linear.
    status: supported
    evidence: loader.quantisation_plan on the real-size meta skeleton (tests/exp_p2/test_omni_stack.py::test_quantisation_plan_on_the_real_size_meta_skeleton), omni venv, CPU
    level: E4
    confidence: 0.95
  - statement: The scorer (virtual id space + shifted, restricted logits) equals the literal generation read-off on a tiny randomly initialised real DreamModel, and the gate stack runs unchanged on it.
    status: supported
    evidence: test_omni_stack.py (A4, A6, A7 on the tiny real model), test_omni_scorer.py (gate_scores, caption_lambdas, DCache on the fake)
    level: E4
    confidence: 0.85
  - statement: The 4-bit model fits in the 12 GB card with micro-batch 1 (about 6.3 GB allocated).
    status: unknown
    evidence: arithmetic estimate only (section 6); no weight was loaded
    level: E0
    confidence: 0.5
competing_explanations:
  - "A5 (shift behaviour) may fail on the real model for a reason other than the shift: caption-visible rows are in-distribution, so a failure points at the read-off or the 4-bit numerics, not at the OOD caption mask."
  - "The positive control can pass while B and D (caption masked) are OOD; it proves only that the pipeline is not at chance on the easiest corruption."
unknowns:
  - peak and steady GPU memory of the 4-bit model with bitsandbytes 0.50.2 kernels on sm_120; seconds per pass; whether bnb 4-bit loading works at all on this stack
  - A5 numbers; whether the 4-bit logits are good enough for a likelihood detector
  - how many Omni captions fall outside 5-32 tokens (the frozen counts are Llama-2 counts)
next_test: {hypothesis: "the 4-bit Omni adapter fits and runs the gate stack at a measurable cost", intervention: "run_omni_timing under gpu_guard with the section 5 settings", primary_metric: "median fwd_s of passes 6-20, peak allocated MiB, adapter checks A1-A7 ok", falsifier: "peak allocated > 7000 MiB, a guard stop, or any adapter check failing", gpu_hours: "< 0.2 (20 passes plus at most 12 check rows plus the load); the load itself is the long part"}
```

# IMPL-C: Omni-Diffusion adapter, timing stage and family R runner (2026-10-28)

Commits: `9cb25186` (adapter, runners, analysis, tests, adapter-check list) and `34714293` (load/self-check watchdog). This report is committed afterwards. Status of all code: **E3/E4 on CPU only; no GPU run exists.**
Existing suite with the new tests: `345 passed, 21 skipped` (system python 3.14 + pytest; the project `.venv` has no pytest installed, so I used `python -m pytest`; five of the skips are the omni-stack tests that need the omni venv).

## 1. What exists

| File | Role |
|---|---|
| `exp_p2/omni/layout.py` | pure torch/numpy: Omni constants, T2I row layout, `VirtualMap`, `shift_right`, `to_virtual_logits` |
| `exp_p2/omni/loader.py` | omni-venv loader: paths, audio stub, NF4 config, one-shot `from_pretrained`, MAGVIT, meta skeleton, `quantisation_plan`, versions |
| `exp_p2/omni/scorer.py` | `OmniScorer` with the `UniScorer` interface (`L_I, caption_ids, build, logits_fn, preprocess, encode, decode, selfcheck`) |
| `exp_p2/omni/checks.py` | adapter checks A1-A7 (for the gate-auditor) |
| `exp_p2/omni/build.py` | shared CLI flags, `OmniGuards` (peak-allocation rule), pre-load GPU check, production loader (with a load-time watchdog), env record, Omni token rule |
| `exp_p2/run_omni_timing.py` | the 20-pass timing and fit stage |
| `exp_p2/run_gate_omni_r.py` | family R: stages `cal`, `pos`, `test` |
| `exp_p2/gate/analysis_omni.py` | `omni_gate`, `omni_r`, `fit_omni_threshold`, `omni_positive_control`, CLI, `selftest` |
| `tests/exp_p2/test_omni_{fakes,scorer,analysis,runners,stack}.py` | 11 + 12 + 9 CPU tests in the project suite, 5 omni-venv tests (skip elsewhere) |
| `research/paper2/method/OMNI-ADAPTER-CHECKS-2026-10-28.md` | the committed, **unsigned** check list of AB.5 item 1 |

No existing file was edited (`tools/gpu_guard.py` untouched).

### Key design decision: a virtual id space
`exp_p2/gate/scores.py` imports `MASK_ID=32000, IMG_LO=32001, IMG_HI=48385, TEXT_*` by name and slices logits with them; I may not edit it. `OmniScorer` therefore speaks the UniDisc id space to the gate code and translates at the model boundary: virtual ids -> Omni ids (lookup table; text/structure tokens get process-local virtual ids in [0, 32000), mask 32000 -> 151666, image 32001+k -> 168072+k) and Omni logits -> virtual logits (Omni image columns 168072..176263 land in virtual columns 32001..40192; columns 40193..48384 and everything else are -inf, so the restricted log-softmax is the conditional over the 8192 valid codes; Dream's shift is applied here). `pipeline.gate_scores`, `caption_lambdas`, `image_delta`, `DCache`, `evidence`, `arms`, `calibrate`, `fit_threshold.fit_from_arrays` run **unchanged** (tested). Nothing on disk holds a virtual text id. The text direction is unsupported (`text_logits=False`); family R is image direction only.

Layout (verified against the training route and `apply_chat_template`, CPU, real tokenizer and MAGVIT on 3 COCO images; check A3 `ok: true`):
`<|im_start|>user\nGenerate an image based on the provided text description.\n{caption}<|im_end|>\n<|im_start|>assistant\n<|begin_of_image|>{256 codes}<|end_of_image|><|im_end|>\n` (291 tokens for a 13-token caption). 256 px, 16x16 grid, L_I = 256, codebook 8192 (`dataset_qwen2.py:759-766`, `tools/inference.py` T2I 260 tokens).

## 2. SAP clause mapping

| SAP | Implementation |
|---|---|
| AD.7 eligibility: R only if P+ non-empty, never outside P+ | `analysis_omni.p_plus`; `omni_gate(n_plus=0)` -> `not_run`; `run_gate_omni_r.load_family_plus` refuses an empty P+ and runs only the (corruption, severity) of P+ from `family.json` |
| AD.7 timing stage, 20 passes, t = median of passes 6-20 | `run_omni_timing.py` (20 items, `fwd_s` = CUDA-synchronised forward wall time, batch 1); `analysis_omni.timing_t` |
| AD.7 T(n) = t x [100 p_cal + n p_test (1+\|P+\|)] / 3600 | `analysis_omni.T_hours` plus the AB.5 item 2 cost `+ 50 p_B` (p_B = K = 8) |
| AD.7 GO (a)..(e), n_R rule | `analysis_omni.omni_gate` (conditions reported separately; n_R = 150 if (d),(e) hold, else 120, else NO-GO; hand-computed cases in `selftest` and tests) |
| AD.7 NO-GO: "not run / incomplete", no substitute, no n < 120 | `omni_gate` text; `run_gate_omni_r.load_gate` refuses to start on NO-GO |
| AD.7 own calibration: CRC alpha 0.05, B = 1, first 100 clean items (slack 1/101) | stage `cal` (8 passes + cached null per item), `analysis_omni.fit_omni_threshold` (alpha 0.05 only, write-once) |
| AD.7 test: first n_R items, arms none and GATE-M, image direction, McNemar per c in P+, Holm m_R = \|P+\|, own alpha | stage `test` (arms `none`, `gate0.05`, conditions `clean` + each P+ corruption), `analysis_omni.omni_r` (reuses `report.report_test`, `stats.holm`) |
| AD.7 completed n < 120 descriptive only; wording; no "generalises", no "negative", no pooling | `omni_r`: `formal` flag, `WORDING_REPLICATED / WORDING_NOT`, `forbidden` field |
| AD.7 reported descriptively: none-arm accuracy drop, flagged share on clean items | `omni_r.descriptive` |
| AB.5.1 adapter checks written before the timing stage, run and signed by the gate-auditor | `OMNI-ADAPTER-CHECKS-2026-10-28.md` + `checks.py`; `run_gate_omni_r` and `analysis_omni gate` require `adapter_signature.json` (signed_by gate-auditor, PASS, `selfcheck_sha256` matching the current `selfcheck.json`) |
| AB.5.2 positive control, first 50 R items, patch, code level, plain-B AUROC lower 95 percent bound > 0.5, cost added to T(n) | stage `pos`, `analysis_omni.omni_positive_control` (`pos_control.json`); `test` stage refuses without `passed: true`; `omni_r` returns `pipeline_defect` if given a failed control |
| AB.5.3 items = positions 301..300+n_R of the ordered test list, calibration = first 100, token rule 5-32 with exclusion | `get_items` (`folds.test_items(f, 500)[300:300+n_R]`), `build.omni_token_filter` (Omni tokenizer, c+ and c-, counted by reason, never replaced) |
| AB.5.4 wording incl. R2 tail "same test images" | `omni_r(rule="R2")` |
| AD.12 order: R after P | `omni_r` needs P's analysis; runner needs `runs/P2-GATE-M4/analysis.json` |

## 3. Source facts about Omni that shaped the code (E3 unless noted)
- Shift: `generation_utils.py` `_sample`, `torch.cat([logits[:, :1], logits[:, :-1]], dim=1)` after `forward_dream` (also in the CFG branch).
- `forward_dream` sets `attention_mask = None` internally and the SDPA layer then builds an all-ones mask: bidirectional attention, positions 0..L-1 (`modeling_dream.py` 1029-1050, 423-520). The scorer calls `forward_dream(input_ids=..., attention_mask=None, use_cache=False)`.
- Mask id 151666 in `config.json`, tokenizer `<|mask|>`, `dataset_qwen2.py:938`; `generation_config.json` has `mask_token_id: null` (how the sampler resolves it is not clear from the files; the adapter does not use the sampler).
- The audio encoder is built unconditionally (`modeling_dream.py:763`) and is only used when `audios` is given (`:793-806`).
- Training masks only response tokens (see claims). User turn never masked.
- `tools/inference.py` uses no system message for T2I (`default_system_message = []`) and `flash_attention_2` (unneeded: `DreamSdpaAttention` is hard-coded).

## 4. Adapter checks for the auditor
See `research/paper2/method/OMNI-ADAPTER-CHECKS-2026-10-28.md` (A1 mask id, A2 image range, A3 layout/round trips, A4 shift code path identity, A5 shift behaviour on the real model, A6 inert audio stub, A7 cached-null validity). The three SAP checks map to: mask-id round trip = A1+A2; one-position shift by a teacher-forcing identity = A4 (exact identity against the literal sampler line, CPU on a tiny real `DreamModel`, GPU on the real model) **and** A5 (behavioural: the same logits read off with shift 0/1/2; shift 1 must win by >= 1.0 nat and in top-1; thresholds are my design choices, flagged E0); inert stub = A6.
CPU status: A1, A2, A3 (real tokenizer + real MAGVIT, 3 images), A4, A6, A7 (tiny real model) pass; A5 and the GPU variants have not run.

Commands for the auditor: `python -m pytest tests/exp_p2/test_omni_scorer.py tests/exp_p2/test_omni_analysis.py tests/exp_p2/test_omni_runners.py -q` (system python), and for the omni-venv tests (no pytest there):
```
cd "<W>"; $env:CUDA_VISIBLE_DEVICES=""; $env:HF_HUB_OFFLINE="1"
& "<ROOT>\.venv-omni\Scripts\python.exe" -c "import sys,traceback; sys.path[:0]=['tests/exp_p2','.']; import test_omni_stack as t; [(getattr(t,n)(), print('PASS',n)) for n in sorted(dir(t)) if n.startswith('test_')]"
```
(`W` = `C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\frosty-clarke-209639`, `ROOT` = `C:\Users\Shlok\Downloads\Multi-Modality Language model`.)

## 5. Exact GPU commands (nothing below has been run; each needs Shlok's go-ahead and the committed clean tree the runners demand)
PowerShell, from `W`. `$py = "$ROOT\.venv\Scripts\python.exe"` runs `gpu_guard.py` (as `gate_driver` does); `$om = "$ROOT\.venv-omni\Scripts\python.exe"` runs the stage.

**Timing and fit stage** (20 passes; extra rows for the checks: A5 6, A4 3, A6 1, A7 2):
```
& $py tools\gpu_guard.py --log runs\P2-OMNI-TIMING\telemetry-chunk00.csv --max-temp 80 --max-minutes 25 --every 1 -- $om -m exp_p2.run_omni_timing --resume --soft-minutes 22 --duty 0.5 --mem-frac 0.62 --max-used-first-mib 9500 --max-used-mib 9000 --max-rise-mib 1500 --max-peak-alloc-mib 7000 --max-used-before-load-mib 2500
```
Exit codes: 0 done, 75 relaunch the same command (new `telemetry-chunkNN.csv`), 76 guard stop (a person decides), 2 self-check failed, 7 hold, 11 dirty tree. Output: `runs/P2-OMNI-TIMING/{items.jsonl, selfcheck.json, omni_env.json, chunks.jsonl, omni_token_exclusions.json}`.
Then (CPU): the gate-auditor reviews `selfcheck.json` and writes `adapter_signature.json`; then
`python -m exp_p2.gate.analysis_omni gate --n-plus <|P+|> --time-left-h <H to the freeze>` -> `runs/P2-OMNI-TIMING/omni_gate.json` (go, n_R, T(n), each condition a-e). `--p-cal/--p-test` overrides only if committed in the run card.

**Family R** (only if `omni_gate.json` says GO; each stage is the same command with `--stage`, and is resumable):
```
& $py tools\gpu_guard.py --log runs\P2-OMNI-R-CAL\telemetry-chunk00.csv --max-temp 80 --max-minutes 25 --every 1 -- $om -m exp_p2.run_gate_omni_r --stage cal --resume --soft-minutes 22 --duty 0.5 --mem-frac 0.62 --max-used-first-mib 9500 --max-used-mib 9000 --max-rise-mib 1500 --max-peak-alloc-mib 7000 --max-used-before-load-mib 2500
& $om -m exp_p2.gate.analysis_omni fit --run-id P2-OMNI-R-CAL
& $py tools\gpu_guard.py --log runs\P2-OMNI-R-POS\telemetry-chunk00.csv --max-temp 80 --max-minutes 25 --every 1 -- $om -m exp_p2.run_gate_omni_r --stage pos --resume --soft-minutes 22 --duty 0.5 --mem-frac 0.62 --max-used-first-mib 9500 --max-used-mib 9000 --max-rise-mib 1500 --max-peak-alloc-mib 7000 --max-used-before-load-mib 2500
& $om -m exp_p2.gate.analysis_omni pos --run-id P2-OMNI-R-POS          # exit 3 = positive control failed: R is 'pipeline defect: not run'
& $py tools\gpu_guard.py --log runs\P2-OMNI-R-TEST\telemetry-chunk00.csv --max-temp 80 --max-minutes 25 --every 1 -- $om -m exp_p2.run_gate_omni_r --stage test --resume --soft-minutes 22 --duty 0.5 --mem-frac 0.62 --max-used-first-mib 9500 --max-used-mib 9000 --max-rise-mib 1500 --max-peak-alloc-mib 7000 --max-used-before-load-mib 2500      # add --corrupt-at 256 only if the lead decides so (A1)
& $om -m exp_p2.gate.analysis_omni r --run-id P2-OMNI-R-TEST          # -> analysis.json (omni_r)
```
Relaunch a stage with the same command after exit 75 (use `telemetry-chunk01.csv`, ...). Exit 76 = a guard stopped it: a person decides.

Pass counts (arithmetic, not a forecast): cal 100 x 8 B passes + at most 28 cached nulls; pos 50 x 8; test n_R x (2 + 8 x (1 + \|P+\|)) = for n_R 150: 1,950 (\|P+\|=1) to 3,900 (\|P+\|=3).

`gate_driver` cannot launch these as is (see concerns).

## 6. Memory: proposed settings (all estimates UNVERIFIED; the timing stage exists to measure them)
Arithmetic from the meta skeleton: NF4 weights 6.525 B x 0.5 B = 3.263 GB + fp32 absmax (block 64) 0.408 GB = 3.67 GB; bf16 rest (embed 0.632 B, lm_head 0.632 B, audio_projection 14.7 M, norms/biases) 1.278 B x 2 B = 2.56 GB. **Weights about 6.23 GB = 5,940 MiB.** Per-forward extras at 291 tokens, micro-batch 1: logits 291 x 176,264 bf16 = 103 MB, virtual copy 28 MB, largest bnb dequantisation temporary (MLP) 136 MB, activations tens of MB: **peak allocated about 6.3-6.4 GB (6,000-6,100 MiB)**. MAGVIT stays on CPU (-0.4 GB). Whole-GPU adds the CUDA context (assumed 0.4-0.6 GB, not measured here) and other processes. The setup doc's "about 6.5 GB" agrees; neither is measured.
Proposed (defaults of `omni_parser`; all CLI flags):
- `--mem-frac 0.62` (7,581 MiB of 12,227 MiB: an OOM in this process, not a full card, if the estimate is wrong);
- `--max-peak-alloc-mib 7000` (new guard rule: stop, exit 76, if an item's peak allocated exceeds it; ~900 MiB above the estimate);
- `--max-used-first-mib 9500`, `--max-used-mib 9000`, `--max-rise-mib 1500` (the generic whole-GPU rules; first-item ceiling 500 MiB below the stack default 10,000, so >= 2.7 GB stay free);
- `--max-used-before-load-mib 2500` (new: nvidia-smi before any CUDA context; refuses to load if other processes already hold more, so that the 6 GB of weights do not land on top of another job; the 2,500 figure is my choice, not measured);
- `--micro-bs 1` (the gate code asks for batches of 4; the scorer splits them; raise only after the timing stage shows headroom);
- the load and self-check are covered by a watchdog with the same rules (the runner's own watchdog starts after them).
The timing rows log `peak_alloc_mib`, `peak_reserved_mib`, whole-GPU `gpu_used_mib` per pass, and `omni_env.json` records allocated/reserved after load and the cap. If steady whole-GPU use approaches 9,000 MiB, the stage stops by itself; the lead should treat that as a NO-GO by condition (c), not raise the ceiling.

## 7. What is untested until the GPU
bitsandbytes 0.50.2 NF4 kernels on sm_120 and the full `from_pretrained` quantised load with the 917 unexpected audio tensors (the same call path was run unquantised on a tiny checkpoint, CPU: unexpected keys ignored, stub in place); real memory and time; A5 and the GPU numerics of A4/A6/A7; `production_loader` end to end (incl. the load watchdog), `build.write_env` GPU fields, `preload_check` against real nvidia-smi; the effect of 4-bit on logits quality; real Omni token-length exclusion rates; Windows `uv` venv has no pip, so `env-lock.txt` of a run is empty (see `omni_env.json` and `.venv-omni\freeze-2026-10-27.txt`). The runner exit paths were exercised only with fake scorers and `guards=None`.

## 8. Ambiguities and how I resolved them
- **A1 Where the pixel corruptions act.** SAP: "no UniDisc threshold or operating point transfers except the pixel-level corruption parameters of each c in P+". Default `--corrupt-at 512`: same 512 px image, same seeds and splice donor as P, then tokenised at 256 px (identical corrupted pixels; but JPEG/noise are attenuated by the downsample and the effective per-token strength is weaker than in P). `--corrupt-at 256` applies the same parameters at Omni's native resolution (splice 128/192 px then covers 25/56 percent of the image). Recorded in each row and the run config. **Lead to confirm before the `test` stage.**
- **A2 p_cal and p_test "as logged".** M2 rows carry no `n_rows` (only M4 rows do). `pass_counts` uses the median M2 `n_rows` if present, else the itemised 12 of the M2 docstring, flagged; p_test = median M4 `n_rows` / gated conditions per item (75/5 = 15 for a 3-corruption family), an **upper bound** (it includes the text direction, TbV and lambda passes); it can only cause a spurious NO-GO, never a spurious GO. Overrides must be committed in the run card. Cheapest fix on the owners' side: add `row["n_rows"]` in `run_gate_m2.process`.
- **A3 "teacher-forcing identity".** Read as two checks (A4 exact code-path identity; A5 behavioural, shift 1 versus 0 and 2 on the same logits). A5's margin (1.0 nat) and top-1 rule are design choices written before any run.
- **A4 Token rule with a different tokenizer.** The frozen folds count Llama-2 tokens. `pipeline.check_fold_tokens` would raise `FoldDefect` at more than 10 percent mismatch, so it is not used; the Omni rule excludes by Omni count (c+ and c-), counts by reason, never replaces; the planned n_R may therefore shrink (the runner's `effective_n.json` mechanism), and the SAP's "completed n < 120: descriptive" applies. Calibration uses the first 100 calibration items minus exclusions (n_cal can be below 100).
- **A5 Caption masked is out of distribution for Omni** (training never masks the user turn). B and D are implemented as the SAP defines them; only the positive control can reveal a broken pipeline, and a pass proves only non-chance on patch. Any R rejection is "directional replication ... quantisation confounds a likelihood-based detector", as the SAP words it; I would add the OOD caveat to the paper text.
- **A6 Image resolution.** 256 px (16 x 16 tokens) because Omni generates and was trained on 256 px assistant images; the patch is 4 x 4 (6.25 percent, as 8 x 8 of 32 x 32). Passes are cheaper per row than UniDisc's 1,024-token rows, so T(n) from UniDisc pass counts times Omni seconds per row is conservative on length and optimistic on the 8B size (the measured t covers both).
- **A7 Which time is "t".** The forward wall time (`fwd_s`, CUDA-synchronised), not the row `seconds` (which includes the CPU encode and 1 s sensors).
- **A8 Two-stage image preprocessing.** Clean and corrupted images go through crop-512 then resize-256; the repo's own path is one-stage. Measured on 8 COCO images (explore script, CPU): only about 60 percent of codes agree between the two paths (LFQ sign flips). Both arms of every comparison use the same path, which is what the changed-code labels need; Omni's absolute fidelity to its own tokenisation is slightly changed (decode PSNR 19-22 dB on 3 images, reported by A3, not gated).
- **A9 Positive control items.** The same first 50 R items and the patch seeds of P (`[SEED_GATE, gid, 190]`) with the 8192-code vocabulary; plain-B has no threshold, so it does not depend on the Omni calibration, but the stage order cal -> pos -> test is enforced.
- **A10 P+ under R3.** `p_plus` reads `gate_better` from the analysis' `primary` block; under R3 that block is the d-endpoint test, under R1/R2 the Y test. AD.7 says "P rejected after Holm with b > c"; the lead should confirm that under R3 the d-based rejection defines P+ (R still uses McNemar on Y).

## 9. Concerns (outside my files)
1. `exp_p2/gate/gate_driver.py` needs a stage entry that can launch another interpreter: `STAGES` maps only module names and `build_cmd` hard-codes `common.GEN_PY`. Needed: (`exp_p2.run_omni_timing`, `P2-OMNI-TIMING`, 20) and (`exp_p2.run_gate_omni_r`, per-stage run id and n) with `.venv-omni\Scripts\python.exe` as the child interpreter; the R stages also need `--stage` passed through `--extra`. Until then use the section 5 commands (they carry the same guards except the driver's event-log and pin checks).
2. `exp_p2/gate/seeds.py` `ANALYSES` has no `omni_gate` / `omni_r` (SAP AD.13 lists them): append them (appending keeps earlier seeds); until then a name-derived SeedSequence is used and written as `seed_note`.
3. `run_gate_m2.process` should write `n_rows` (see A2), otherwise `omni_gate` falls back to the documented 12 and flags it.
4. The P-side corruption parameters for R are read from `runs/P2-GATE-M3/family.json` and P+ from `runs/P2-GATE-M4/analysis.json`; if `analysis_m4.main` writes the result elsewhere, `--p-result` and `load_family_plus` need the real path.
5. I did not run the gate-auditor's role: nothing is signed, and `omni_gate` cannot reach GO without the signature file.
