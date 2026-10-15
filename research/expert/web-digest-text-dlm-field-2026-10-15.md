# Web digest: text-only diffusion LMs, field map as of 2026-10-15

Condensed by the orchestrator from the report of a web-research subagent spawned for the dlm-expert
KB. Every ID was opened on arxiv.org/abs by that agent; evidence E1 (abstracts) throughout; dates are
v1 submission dates (do not infer dates from IDs). Flags: NEW = v1 2026-07-17 to 2026-10-15;
REC = 2026-04-01 to 2026-07-16. Lists are date-sorted samples, not exhaustive.

## 1. Discrete/masked foundations and families
- 2503.04482 GIDD (ICML 2025): general interpolating diffusion; masked is a special case; mask+uniform hybrid gives self-correction.
- 2509.01025 FlexMDM: insert-then-unmask, flexible length; retrofits LLaDA-8B (GSM8K 58 to 67 per abstract).
- 2506.09018 Edit Flows (NeurIPS 2025; proceedings title differs): CTMC with insert/delete/substitute.
- 2506.13579 DDOT (EMNLP): joint token and position denoising via OT coupling.
- 2609.20539 NEW: uniform and Gaussian diffusion sample in passes scaling with dual total correlation; provable parallelism separation among masked, uniform, Gaussian.
- 2608.25505 NEW: forward-KL error of any adaptive parallel policy equals expected conditional total correlation (exact identity); serial-depth bounds.
- 2610.07655 NEW: uniform discrete diffusion minimax optimal for small effective support. 2608.20635 NEW: minimax optimality of SEDD.
- 2609.35817 NEW LUDI: scaling uniform DLMs (loss fix, per-token time embeddings, few-step confidence sampling).
- 2610.01275 NEW: uniform-state DLMs (DUO, UDLM, uniform SEDD) revise 173-270 of 512 positions per step, cannot retain correct tokens; self-correction not realised.
- 2609.30977 NEW: time conditioning often unnecessary in uniform discrete diffusion.
- 2609.38066 NEW AlphaDLM: sequence-level alpha loss; factorisation alone is not the problem.
- 2606.19005 REC Sumi: first open uniform DLM pretrained from scratch at scale.
- 2606.25331 REC iLLaDA: 8B masked DLM from scratch, 12T tokens.
- 2606.00997 REC: in LLaDA-2.1 reveal order alone shifts target log-likelihood by up to 0.49 nats/token; learned conditionals are not a coherent joint; Var(log q_t) as a path diagnostic.
- 2607.01775 REC Set Diffusion (ICML 2026); 2605.00161 REC Consistent DLMs (ICML 2026); 2607.26504 NEW any-order interface is not any-order inference; 2608.30922 NEW CARVE (EMNLP 2026 Findings) variable-length expansion; 2610.12545 NEW AutoIndexer edit chains.
- Consensus: masked/absorbing is the default at scale; dependence among co-revealed tokens (total correlation) governs parallel error; variable length and editing are the missing capabilities.
- Disputes: uniform-noise self-correction (GIDD vs 2610.01275); factorisation as bottleneck (2603.00045 CoDD vs 2609.38066 vs sampler configuration 2609.33947); coherence of learned conditionals (2606.00997).

## 2. Continuous / embedding / latent / flow LMs
- 2510.22510 CANDI (hybrid); 2604.11748 REC LangFlow (embedding flow, claims to rival discrete); 2605.18530 REC RePlaid (20x compute gap vs AR; PPL bound 22.1 OWT); 2605.10938 REC ELF; 2605.06548 REC Cola DLM; 2605.07933 REC joint latent training; 2606.08810 REC decoder-basin mechanism; 2608.23551 NEW ConvergeFlow; 2609.29102 NEW ELF-REG math; 2610.02665 NEW Sigma 3B/8B continuous DLM competitive with masked DLMs and AR on math/code; 2610.13834 NEW design space (self-conditioning, DoubleCat); 2610.09416 NEW flow LMs reason more efficiently at matched steps (claim); 2610.00894 NEW Clock Diffusion (variable length, KV cache); 2609.04531 NEW PlaidQ code, few-step; 2610.19080 NEW RL for flow LMs; 2605.13681 REC bridge sampling; 2606.27617 REC masked language flow models.
- Consensus: small-scale gap to discrete largely closed; largest continuous model 8B vs 26B-30B masked; self-conditioning and decoder geometry decisive.
- Disputes: "rivals discrete" vs 20x compute gap (different protocols); reasoning advantage contested (2610.09416 vs 2609.29102).

## 3. Samplers and decoding
- Anchors: 2505.22618 Fast-dLLM; 2505.15781 dKV-Cache; 2506.06295 dLLM-Cache (ICML 2026); 2510.14973 adaptive KV recomputation; 2506.00413 APD; 2509.26488 dParallel; 2509.25188 learnable parallel decoding; 2602.08676 LLaDA2.1 token editing.
- Remasking/order/commitment: 2604.18738 REC token-to-mask refinement; 2605.26436 REC targeted remasking; 2606.17175 REC self-generated error training; 2609.34509 NEW diversity loss from low-confidence remasking, top-probability position selection avoids it; 2609.39859 NEW Fork-dLLM defers high-entropy fork positions; 2610.08833 NEW CoDR; 2610.05125 NEW BayesER; 2607.04469 REC joint token commitment vs conditional total correlation; 2608.05687 NEW answer-first order costs GSM8K accuracy.
- Adaptive parallel: 2604.08302 REC DMax; 2606.02955 REC Fast-dLLM++ (contests homogeneous-confidence assumption); 2606.15805 REC mean-field parallel decoding; 2609.26249 NEW PACE-dLLM elastic blocks; 2609.36452 NEW confidence alone does not determine safe joint commitment.
- Caching/serving: 2606.07571 REC shared-prefix KV; 2607.16339 REC LaCache exact; 2609.17573 NEW GroupKV; 2609.26796 NEW Flash-dLLM; 2609.11998 NEW constant-size block cache; 2610.06996 NEW mask-guided KV eviction.
- Speculative: 2604.05250 REC DualDiffusion; 2605.14305 REC factorisation-error-free via speculation; 2605.15609 REC PSD; 2606.02544 REC SimSD; 2606.11552 REC left-to-right speculation; 2603.25702 S2D2; 2608.27514 NEW trajectory-level; 2609.04010 NEW diffusion-augmented LLMs (lossless AR-preserving).
- Few-step/distillation: 2607.03788 REC tensor-train joint; 2609.06324 NEW coupled-noise one-step block; 2609.15903 NEW Discrete Beckmann Transport; 2610.12879 NEW Seq-Drifting; 2609.33947 NEW sampler sharpening without retraining beats 1024-step quality at 16 steps.
- Theory: 2609.21960 NEW tau-leaping schedules; 2607.00773 REC parallel-in-time tau-leaping; 2605.09303 REC order collapse as non-conservative field.
- Consensus: mutual inconsistency of co-committed tokens is the core failure; marginal confidence insufficient; block diffusion plus exact caching is the serving substrate.
- Disputes: arbitrary order (2601.15165 flexibility trap vs 2609.34509 remasking rule); few-step gap from models vs sampler configuration (2609.33947); 2606.00997 and 2609.33947 imply perplexity can mislead.
- Open: common benchmark of quality, tokens per forward and throughput (2608.23807 NEW is a serving analysis of LLaDA-8B-Instruct, not a benchmark).

## 4. Training, scaling, AR-to-diffusion, block, MoE, long context
- Anchors: 2410.18514 scaling masked diffusion (16x gap); 2507.15857 diffusion beats AR when data-constrained; 2509.24389 LLaDA-MoE; 2512.15745 LLaDA2.0 100B; 2510.06303 SDAR; 2509.26328 Fast-dLLM v2; 2511.08923 TiDAR; 2506.17298 Mercury; 2506.14429 LongLLaDA (AAAI 2026).
- 2610.17590 NEW: compute gap 12.8x with exact decoding-order likelihood; block training plus encoder-decoder lowers it to 7.8x (block 32), 4.6x (8), 3.0x (4); about 1,700 models.
- 2608.03457 NEW LLaDA MoE v2: MoE dLLM scaling laws; 30B-A3B from scratch on 23.5T tokens.
- 2608.00146 NEW DiffusionGemma technical report: open-weight, from Gemma 4 MoE (3.8B active, 25.2B total), 256-token blocks, about 20 tokens per forward, about 1,500 tokens/s on one H100.
- 2606.14620 REC: measured commit order of DiffusionGemma 26B is "neither parallel nor sequential".
- 2606.01024 REC DSL-LLaDA; 2609.20751 NEW dQwen3.5 (hybrid attention/RNN to DLM); 2610.02657 NEW conversion recipes differ by about 3 orders of magnitude in data; 2610.08108 NEW re-injecting AR post-training weights; 2606.06712 REC on-policy distillation conversion; 2605.06885 REC representation alignment; 2606.29215 REC multi-block decoding; 2609.19242 NEW block parallelism for long-context training; 2605.19726 REC block sparse attention; 2610.17868 NEW Prefilling-dLLM v2; 2604.20796 REC LLaDA2.0-Uni (multimodal).
- Consensus: frontier moved to block/semi-AR, MoE, AR-to-diffusion conversion; compute-gap estimates are protocol-dependent.

## 5. Reasoning and RL
- Anchors: 2402.07754 Diffusion of Thoughts; 2504.12216 d1; 2507.08838 wd1 (ICLR 2026); 2510.09541 SPG (ICLR 2026); 2505.19223 LLaDA 1.5 VRPO; 2506.20639 DiffuCoder; 2509.06949 TraceRL; 2509.10396 IGPO; 2603.06743 GRPO reward collapse; 2603.01563 LFPO; 2602.06462 DiSPO.
- REC: 2605.10218 relative score policy optimisation; 2605.25638 RLDF; 2605.29398 GDSD; 2606.04396 trajectory-aware RL; 2606.08501 reward/state alignment; 2606.13795 DiPOD double drift; 2607.00208 SLIM-RL; 2607.15200 mask-aware policy gradients (COLM 2026; GSM8K 87.1, MBPP 53.4); 2607.14522 continuous-time RL.
- NEW: 2607.16872 trace-based on-policy distillation; 2609.13060 CanvasAnneal; 2609.35472 PRM guidance loses at fixed forward-pass budget; 2610.00661 StepRS-GRPO; 2610.17266 PACT; 2610.19271 outcome-routed distillation plus RL; 2610.19080 RL for flow LMs.
- Consensus: sequence likelihood intractable, all methods use surrogates; instability and reward collapse common; step-level credit assignment is the frontier.
- Disputes: trajectory-aware vs random masking; ELBO vs likelihood-free; order as a policy action; compute-fair test-time guidance.

## 6. Surveys and analyses (last 90 days)
- No new surveys beyond 2607.12829 and 2609.04778 (already known). Analyses: 2608.23807 NEW serving characterisation; 2610.19855 NEW energy of discrete diffusion vs AR; 2606.19475 REC "Diffusion Language Models: An Experimental Analysis" (not previously in the project's lists).

## Top developments since 2026-07-16 for the review
1. 2610.17590 compute gap 3.0x to 12.8x, protocol-dependent.
2. 2608.00146 DiffusionGemma open-weight MoE DLM.
3. 2608.03457 LLaDA MoE v2 scaling laws, 30B-A3B from scratch.
4. 2609.20539 provable parallelism separation masked/uniform/Gaussian.
5. 2608.25505 exact error identity for adaptive parallel sampling (conditional total correlation): directly relevant to the review's error budget (credit).
6. 2609.33947 few-step gap largely sampler configuration: a confound for every few-step comparison (supports the census point).
7. 2610.01275 uniform-state DLMs do not retain tokens; with 2609.34509 and 2609.39859 reframing the flexibility trap as a decoding-rule issue.
8. 2610.02665 Sigma and 2610.09416, 2610.13834: continuous DLMs at 3B/8B.

## Unconfirmed (do not cite)
Gemini Diffusion (no report ID); RND1 (no arXiv ID); 2610.04875, 2609.35362, 2609.33301, 2610.14162 (listing only); 2605.22586 (generic tutorial).
