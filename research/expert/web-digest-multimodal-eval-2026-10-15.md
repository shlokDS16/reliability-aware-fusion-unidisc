# Web digest: unified multimodal discrete diffusion, evaluation pitfalls, surveys, checkpoints (2026-10-15)

Condensed by the orchestrator from the report of a web-research subagent spawned for the dlm-expert
KB. Every arXiv ID was opened on arxiv.org/abs by that agent; E1 (abstract) unless marked; E2 only
for 2610.15227 (HTML sections) and the survey scans. NEW = v1 2026-07-17 to 2026-10-15; REC =
2026-04-01 to 2026-07-16. Coverage good but not provably exhaustive (arXiv API rate limits).

## A0. Closest to the project's questions (per-step cross-modal dependence, joint vs sequential, CFG)
- 2610.15227 NEW "Understanding Unified VLMs: From Attention Probing to Guidance Tuning" [E1+E2 partial]: per-head CFG-branch activation difference averaged over steps, on Muddit (masked diffusion, 32 steps) and Janus-1.3B (AR), T2I and I2T separately; stable condition-responsive head subset; for Muddit I2T the head ranking degrades over steps; HeadTuned-CFG lowers FID. Measures guidance response per direction, NOT joint text-image commitment or inter-modal dependence. Bearing on EXP-003 novelty (D0019): does not anticipate it; cite as related per-step CFG analysis.
- 2608.01821 NEW DAVET: demand for visual evidence is step-dependent (LLaDA-V, LaViDa); understanding-side; no formal estimator in the abstract.
- 2609.34772 NEW DynaHall: per-step answer tendency in 5 diffusion VLMs; unsupported answers preferred before the answer position is unmasked; PGS steering. Model for per-step commitment measurement (I2T only).
- 2609.05525 NEW DIVA (EMNLP 2026 main): cross-step conditional propagation of visual semantics in discrete diffusion VLMs.
- 2607.13188 CO2Jump (known): joint vs sequential reference.
- Not found: a dedicated study of CFG effects on joint text-image consistency in unified discrete diffusion; any per-step text-image mutual-information estimator.

## A1. Unified discrete-diffusion and discrete-flow models
2604.20796 REC LLaDA2.0-Uni (SigLIP-VQ tokens, MoE block masked diffusion, diffusion decoder); 2603.06577 Omni-Diffusion (ICML 2026; any-to-any mask-based discrete diffusion, text/speech/image; v2 2026-07-03); 2610.10990 NEW Omni-Diffusion-Distill; 2610.00576 NEW Gestalt (interplay tokens); 2609.03796 NEW LLaDA-Image (6B DiT + frozen LLaDA2.0-Mini; hybrid); 2602.12221 UniDFlow (discrete flow, LoRA adapters); 2601.04056 CoM-DAD; 2512.14008 Sparse-LaViDa (CVPR 2026 per web search); 2606.04264 REC UniCanvas; 2505.16933 LLaDA-V (base of many 2026 dVLM papers).

## A2. Training, RL and decoding order for multimodal masked diffusion
2607.08056 REC GRPO-trained unmasking-order controller (logits alone insufficient for order); 2606.14792 REC RL for visual-textual thinking with local visual edits; 2605.16842 REC Sketch Then Paint hierarchical RL; 2609.11315 NEW routing by reasoning need (Findings EMNLP 2026); 2608.26641 NEW information-guided frontier decoding (Findings EMNLP 2026); 2609.32781 NEW CT-OPD; 2609.25131 NEW LEDFlow (9.4 percent of Sudoku cells right at an intermediate step but wrong at the end).

## A3. Hybrid and other unified models
2607.05722 REC Nemotron-Labs-Diffusion (tri-mode AR/diffusion/self-speculation, text-only); 2607.03461 REC WorldBagel (BAGEL application); 2605.15792 REC generation as visual thought helps understanding (CVPR 2026 Findings; synergy evidence vs known 2609.01607); 2610.16500 NEW self-verifier capture in unified generators (self-reward rises while measured quality falls).

## A4-A5. Other modalities and VLA
2606.04939 REC UAT (continuous audio + masked text); 2609.35407 NEW BiMoGen motion-text masked diffusion (NeurIPS 2026); 2605.29591 REC Mind-Omni; 2608.00011 REC DLLM-TTS; 2607.25948 NEW MODUS (any-to-any, not diffusion). VLA: 2609.13053 NEW Dynin-Robotics; 2610.04009 NEW SUAVE; 2606.23623 REC dVLA-RL.

## A6. Consensus, disputes, open questions
- Consensus: backbones moving to discrete tokens with block/masked diffusion for both modalities; commitment order matters more than logits; visual conditioning is not uniform across steps.
- Disputes: generation helps understanding (2605.15792) vs synergy conditional (2609.01607); where hallucination is decided (2609.34772 vs 2609.01318); fully discrete vs hybrid; shared-weights self-reward can degrade quality (2610.16500).
- Open: no per-step text-image dependence estimator in joint generation; no study of guidance scale on joint consistency (as opposed to FID); joint vs sequential evaluated only on bespoke corpora.

## B. Evaluation practice and pitfalls
- 2409.02908 (ICLR 2025): reduced-precision Gumbel sampling lowers effective temperature and flatters generative perplexity.
- 2606.08417 REC Hacking Generative Perplexity (ICML 2026 workshop): zero-parameter samplers reach SOTA gen-PPL; use distributional metrics.
- 2609.33947 NEW: few-step gap largely sampler configuration; GroupEval separates quality and across-output diversity; a 1.5-4.7x perplexity gain gave no quality gain.
- 2606.12232 REC re-evaluating confidence remasking: benefit setting-dependent; worsens diversity collapse under non-greedy decoding.
- 2604.13413 REC dataset-level metrics attenuate non-determinism (guidance scale, steps, Monte Carlo, batch, hardware, precision); Factor Variance Attribution.
- 2604.00375 REC low-confidence remasking raises Pass@1, constrains entropy, hurts Pass@k.
- 2610.17590 NEW compute gap 3.0x to 12.8x, protocol-dependent.
- 2606.14620 REC DiffusionGemma commits in large simultaneous batches; apparent order depends on analysis granularity.
- 2609.01318 NEW reliability challenges in diffusion VLMs (EMNLP 2026 main): reversed yes-bias, first-step length prior.
- 2607.29079 NEW accelerated dMLLM outputs drift from unaccelerated; speedups need an output-agreement check.
- 2610.00499 NEW output length and step count are poor inference-cost proxies.
- 2610.15667 NEW masking rate as an evaluation axis. 2603.22075 controlled AR vs MDLM (TinyStories scale).
- Consensus: gen-PPL needs an entropy or diversity companion; match sampler configuration, block length and precision, not only hardware; check output agreement for speedups. Open: no judge-sensitivity study; no reporting standard for unified-model T2I metrics.

## C. Surveys new in the window (not previously known)
- 2609.14421 NEW information-theoretic view of multimodal learning (170 works; stated search protocol, no PRISMA).
- 2607.13431 REC (v2 2026-08-25) discrete diffusion models, tokenization to generation (no PRISMA).
- 2608.20743 NEW multimodal speculative decoding with diffusion drafters, survey plus empirical diagnosis (no PRISMA).
- Add to the review's survey-landscape comparison.

## D. Checkpoints (Hugging Face API, 2026-10-15; fit in 12 GB not checked)
UniDisc aswerdlow/unidisc_interleaved (5.63 GB, licence not stated); MMaDA-8B-Base and -MixCoT (8.08B, MIT); MMaDA-Parallel-M/-A via tyfeld/ (about 8B, MIT); Lumina-DiMOO (8.08B, Apache-2.0); Muddit MeissonFlow/Muddit (Apache-2.0; 4.23 GB transformer); Show-o (5.79 GB; Apache-2.0/MIT tags differ); FUDOKI LucasJinWang/FUDOKI (2.09B F32, Apache-2.0); LaViDa-O (11.09B, adobe-research licence); LLaDA-8B-Instruct and LLaDA-1.5 (8.02B, MIT); LLaDA-MoE-7B-A1B (7.36B, Apache-2.0); Dream-v0-Instruct-7B (7.62B, Apache-2.0); MDLM-OWT, Duo, BD3-LM, sedd-noeos (169.6M, Apache-2.0); NVIDIA SDLLM 1.7B family (MDLM, Duo, AR, EsoLM; CC BY-NC 4.0; paper 2602.15014); Open-Dcoder-0.5B-MDLM (630M, MIT); Nemotron-Labs-Diffusion-3B; LLaDA2.1/2.2-mini (about 16B, Apache-2.0); DiffusionGemma 26B-A4B (Apache-2.0).
- For Paper 2 on a 12 GB GPU: the 1.7B SDLLM family (non-commercial licence) and 0.17B OWT models fit comfortably; FUDOKI (2.1B) and Muddit are the smallest unified models; 8B models need quantisation.

## Unconfirmed (do not cite)
2609.38485, 2607.25527, 2609.35767, 2610.07887, 2605.08029, 2605.20316, 2609.19878, 2507.22920 (revision date), 2510.04146, 2601.07568, DecoCal (ACL 2026), the "Top 10 Open Challenges" perspective paper, the FP32 to FP64 gen-PPL numbers.
