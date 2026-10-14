---
agent: repro-engineer
date: 2026-10-14
brief: Gate G4 for EXP-002 - validate the local MDLM-OWT setup (flash_attn shim, precision) and reproduce MDLM's published OpenWebText likelihood bound
note: written by the orchestrator from the agent's returned text (the harness refused the agent's Write); headline number recomputed independently by the orchestrator from t3_batches_seed1_v2_bs8.jsonl (PPL 22.935, gap -0.50%, bootstrap 95% 22.85-23.01, 400 resamples)
sources_examined: [runs/env-2026-10-14/setup.md, timing.json, mdlm repo @c112c526d193436838c98d81455ee51f90309470, remdm repo @f830d659fb98d9b2c79ff71bfa12d578312b688a, HF kuleshov-group/mdlm-owt @d0958fa851335ece6c15260ce0025f030673c0fb, arXiv 2406.07524v2 (Table 2 live; Tables 11/12 cached, E1), arXiv 2503.00307v4 (Table 1, cached), flash-attention v2.5.6 (6c9e60de) rotary sources]
coverage: T1-T4 complete; T3 on the full held-out set (110,473 sequences). Real flash-attn kernels never run (no Windows wheel).
claims:
  - statement: the PyTorch flash_attn shim matches float64 references to round-off
    status: supported
    evidence: t1a_shim_unit_v2.json (116 cases)
    level: E4
    confidence: 0.95
  - statement: full MDLM forward agrees across three independent attention paths to 6e-5 in fp32
    status: supported
    evidence: t1b_full_forward.json
    level: E4
    confidence: 0.9
  - statement: the setup note's bf16-vs-fp32 disagreement (top-1 0.785) is a dropout artifact (train mode)
    status: supported
    evidence: t2_engineer_exact_train.json vs t2_engineer_exact_eval.json
    level: E4
    confidence: 0.95
  - statement: MDLM's OWT perplexity bound is reproduced within 2 percent
    status: supported
    evidence: t3_ppl_seed1_v2_bs8.json, t3_batches_seed1_v2_bs8.jsonl
    level: E4
    confidence: 0.85
  - statement: generative perplexity and entropy are compatible with ReMDM Table 1 (MDLM, nucleus, T = 1024)
    status: supported
    evidence: t4_genppl_*.json (n = 16)
    level: E4
    confidence: 0.6
unknowns: [real flash-attn kernels; which checkpoint produced the paper's table (HF card 33B tokens vs paper 262B for 1M steps); parquet row order]
next_test: {hypothesis: the -0.5 percent residual is document-order or batch-stratification noise, intervention: batch 16 plus a second seed on the same documents, then a second 100k-document block, primary_metric: PPL bound spread, falsifier: spread below 0.1 percent while the gap persists, gpu_hours: 1.5}
---

# G4: MDLM-OWT validation and reproduction

**Verdict: REPRODUCED.** PPL bound 22.935 (bootstrap 95% 22.861-23.007) against the paper's 23.05
(Table 11/12, T = infinity, no time conditioning, which is the released checkpoint): gap -0.50%
(interval -0.82% to -0.19%). Against Table 2's 23.21 (time-conditioned): -1.19%.
**Recommended precision for any MDLM experiment: fp32 everywhere, autocast off, TF32 off, model in
eval mode.**

## T1. Shim correctness
flash-attn 2.5.6 (MDLM's pin) rotates q, k in the NeoX half-split layout; its triton kernel converts
to fp32, computes, and stores once in the input dtype. References independent of the shim: (R1)
float64 complex product; (R2) flash-attn's own apply_rotary_emb_torch retyped from v2.5.6; (R3) an
explicit Python loop (validates R1, R2; difference 0.0); (R4) the MDLM repo's un-fused rotary on
its Rotary cache (difference 0.0). Attention against an explicit float64 softmax, causal and
non-causal, through flash_attn_func, qkvpacked and varlen_qkvpacked as dit.py calls them. 116 cases
over shapes (1,1024,12,64), (2,257,12,64), (3,64,4,32), (1,7,1,16), (4,128,12,64), (8,1024,12,64),
rotary dims 64/32/16, fp32 and fp64, CPU and CUDA.
- Rotary: fp32 max abs 8.3e-7 (elementwise relative 8.9e-6); fp64 1.8e-15.
- Attention: fp32 2.1e-5 (CPU) / 1.8e-5 (CUDA); fp64 2.8e-14.
- Full forward (4 real sequences, 50% masked), shim vs explicit float64 path vs SDPA-MATH: fp32 max
  logit difference 5.8e-5 to 8.4e-5 (mean 3.5e-6, logit rms 4.2, top-1 agreement 1.0); bf16 max
  0.375-0.5, mean 0.017, top-1 >= 0.986.
- Shim v1 -> v2: only change is bf16/fp16 rotary computed in fp32 with one rounding (v1 rms error
  4.70e-3 vs 3.31e-3 for the kernel semantics, 31% of elements off by 1-2 bf16 steps). v2 is
  bit-identical to the single-rounding emulation; fp32 and fp64 unchanged; effect on ELBO -7e-5
  nats. v1 kept in scripts/shim_v1/. All later numbers use v2.

## T2. Precision
Cause of the setup note's 0.785 top-1 agreement: `restore_model_and_sample()` ends with
`backbone.train()` and the smoke script computed marginals without `.eval()`. Re-running the note's
own functions in train mode gives 0.749 / 0.309 nats (two identical bf16 calls agree only 0.777);
in eval mode 0.977 / 0.085. **Call .eval() after every sample.** setup.md section 3.2 and the
ordered_unmask test were run in train mode and should not be cited.

Eval-mode decomposition against a float64 copy (32 validation sequences, 50% masked, 16,310 masked
positions, truth mean entropy 2.57 nats):

| Variant | Top-1 agree | Mean abs entropy error (renormalised) | KL | Max abs prob error | Row sums |
|---|---|---|---|---|---|
| A official bf16 | 0.9777 | 0.0671 (0.0205) | 5.2e-4 | 0.131 | 0.893-1.109 |
| C = A with logits cast to fp32 before logsumexp | 0.9777 | 0.0205 | 5.2e-4 | 0.129 | 1 |
| B bf16 blocks, fp32 output layer and normalisation | 0.9913 | 0.0139 | 2.4e-4 | 0.117 | 1 |
| G attention in fp32 | as A | | | | |
| D v1 rotary | 0.9781 | 0.0670 (0.0208) | | | |
| E fp32 everywhere | 1.0000 | 1e-5 | 0 | 3e-5 | 1 |

The bf16 autocast trunk costs about 2% top-1 near-ties; the rest of the official error is bf16
rounding of the normalised log-probabilities; attention precision and the rotary shim do not
matter. Paired ELBO (2000 sequences, identical t and masks): A -0.14% against fp32-all, C +0.06%,
B +0.03%. Timing at L = 1024: bf16 0.026 s (batch 1) / 0.100 s (batch 8); fp32 0.034 / 0.271 s
(peak 1.10 / 3.99 GB). Never use the repo's bf16 `_subs_parameterization` for probabilities (row
sums up to 1.11). The checkpoint was trained in bf16, so fp32 is a more exact evaluation of the same
weights, not a different model.

## T3. Reproduction
Paper values: Table 2 (live arXiv v2) MDLM <= 23.21 (time-conditioned); Table 12 (cached, E1)
23.21 with and 23.05 without time conditioning; Table 11 T = infinity 23.05. The checkpoint has
time_conditioning = false, and the repo's eval script uses that checkpoint, so the reference is
23.05. Protocol: GPT-2 tokenizer, EOS-separated documents wrapped to 1024, last 100k documents held
out, PPL = exp(mean ELBO per token), continuous-time loglinear schedule, antithetic t. Run: official
Diffusion hf_dit, dataloader and `Diffusion._loss` under bf16 autocast, five resumable 15-minute
guarded chunks; data = last 100,000 rows of shard 79 of Skylion007/openwebtext (SHA-256
80f15bb3...6ae2 matches the Hub); 110,473 sequences, 113,124,352 tokens. Result 22.935 (bootstrap
95% 22.861-23.007); precision-matched fp32 estimate about 22.97 (-0.36%). Deviations: single shard
with assumed row order; batch 8, not 16; no Lightning Trainer (same metric); per-batch RNG reseed;
one seed; library versions (Lightning 2.6.6 vs 2.2.1, transformers 4.49 vs 4.38.2, torch 2.11). The
-0.5% residual is unexplained (document order, antithetic stratification by batch size, bf16
rounding bias of -0.14%, checkpoint provenance).

## T4. Generative check (indicative, 16 samples)
Official sampler ddpm_cache, 1000 steps, no nucleus, fp32 Gumbel, seed 1: GPT-2 Large gen-PPL 47.8
(bootstrap 42.4-53.5), entropy 5.34 (sd 0.16); no published number for this exact setting.
ReMDM-repo sampler (mdlm), 1024 steps, nucleus 0.9, fp64 Gumbel: 56.3 (48.3-65.3), entropy 5.51
(sd 0.15), against ReMDM Table 1 MDLM (nucleus) T = 1024: 51.3 / 5.46 (5000 samples; data 14.8 /
5.44). Compatible within the wide n = 16 interval.

## Telemetry and process notes
Guarded stages: max 78 C, mean 63.8 W over 1,395 samples, single peak 183 W, no temperature stop.
Several short runs were not under gpu_guard (t1a about 1 minute each, official-MDLM T4 about 8
minutes, one killed by a reboot); outputs kept. Python children exit with 0xC0000409 at interpreter
teardown after writing results; `scripts/run_stage.sh` treats a stage as done when its result file
exists.
