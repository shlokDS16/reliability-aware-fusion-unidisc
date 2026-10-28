# OMNI-ADAPTER-CHECKS (SAP AB.5 item 1) - committed before the timing stage, UNSIGNED

Author of the adapter and of this list: implementer C (2026-10-28). **The author does not sign.** Per SAP AB.5 item 1 the three adapter checks are run and signed by the
**gate-auditor**; no Omni item enters family R before that signature. Code: `exp_p2/omni/checks.py` (docstring = the same list), run for real inside the timing stage
(`exp_p2/run_omni_timing.py`, result in `runs/P2-OMNI-TIMING/selfcheck.json` under `adapter`). Thresholds below are design choices written before any run (E0); the auditor may tighten them before signing.

| SAP check | ID | Where | Pass criterion |
|---|---|---|---|
| mask-id round trip | A1 | CPU + selfcheck | tokenizer `<\|mask\|>` = `config.mask_token_id` = 151666 = layout constant; `id -> token` = `<\|mask\|>`; virtual 32000 -> 151666 -> 32000 style round trip through the lookup table; ids 151666 and the 8192 image ids are refused as text tokens |
| mask-id round trip (range part) | A2 | CPU + selfcheck | `<\|image_k\|>` = 168072 + k for all 8192 k; 168072 + 8192 = `vocab_size` = `len(tokenizer)`; the id below 168072 is not an image token; a code >= 8192 in a row is refused |
| one-position logit shift, teacher-forcing identity (a) code path | A4 | CPU (tiny real `DreamModel`) + GPU (real) | the scorer's image-column logits equal exactly the literal sampler read-off `cat([l[:, :1], l[:, :-1]], 1)` of `generation_utils.py` applied to `forward_dream(inputs_embeds=...)`; the shift-0 read-off differs (not vacuous); padding columns are -inf. Tolerance 0 on CPU, 2e-2 on GPU |
| one-position logit shift (b) behaviour | A5 | GPU only | real rows, caption visible, 25 percent of image tokens masked, the SAME logits read off with shift 0, 1, 2: mean log-probability of the true code at shift 1 exceeds the best other shift by >= 1.0 nat AND top-1 accuracy at shift 1 exceeds that of both others (6 rows). Visible-token copy fractions are reported |
| audio-encoder stub inert | A6 | CPU (tiny real model) + GPU | `model.model.audio_model` is the stub, 0 parameters, 0 calls, no forward hook fired during a scorer forward, `audio_projection` keeps its parameters |
| extra: layout | A3 | CPU + selfcheck | hand-built row = training route (tokenizer on the assembled strings) = `apply_chat_template` prompt; `tokens(INSTR + caption) = tokens(INSTR) + tokens(caption)`; caption decode round trip; codes -> `<\|image_k\|>` strings -> ids -> codes exact; encode deterministic. MAGVIT PSNR is reported, not gated |
| extra: cached nulls | A7 | GPU | image null (caption and image fully masked) identical (1e-5) for two different (caption, codes) of equal caption length |

## What the auditor runs and signs

1. CPU, project python: `python -m pytest tests/exp_p2/test_omni_scorer.py tests/exp_p2/test_omni_analysis.py tests/exp_p2/test_omni_runners.py -q`.
2. CPU, omni venv (no pytest there): the one-line harness of the report (`tests/exp_p2/test_omni_stack.py`: real tokenizer, tiny real `DreamModel`, loader call path, quantisation plan).
3. Read `runs/P2-OMNI-TIMING/selfcheck.json`: `adapter.all_ok` true and every A-result inspected (A5 numbers in particular).
4. Write `runs/P2-OMNI-TIMING/adapter_signature.json`: `{"signed_by": "gate-auditor", "verdict": "PASS", "selfcheck_sha256": "<sha256 of selfcheck.json>", "date": "...", "notes": "..."}`. `analysis_omni gate` and
   `run_gate_omni_r` both refuse a signature whose hash does not match the current `selfcheck.json`.

Status on 2026-10-28: A1, A2, A3, A4, A6, A7 pass on CPU (fakes, real tokenizer, tiny real model); A5 and the GPU variants of A4/A6/A7 have **not** run (E0/E3 only). Nothing is signed.
