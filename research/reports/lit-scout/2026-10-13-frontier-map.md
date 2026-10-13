# Frontier map, first pass (2026-10-13)

Source: Exa Agent run `agent_run_ad0e26e25f8140f5ad8ad63e3590591f`, effort medium, 12 searches,
0.10 USD. **Evidence level E1 for every line**: titles and IDs were retrieved by the agent, none
has been read in full here. Each must pass lit-scout canonicalisation and paper-reader before use.

| # | Question | Crowding | Closest work returned | Open according to the sweep |
|---|---|---|---|---|
| 1 | Parallel-unmasking factorisation error, theory | crowded | NeurIPS 2025 "Breaking the AR's Sampling Bottleneck"; ParallelBench 2510.04767; "Breaking the Factorization Barrier" 2603.00045; "Factorization-Error-Free DDLM" 2605.14305 | joint theorem and benchmark tying dependence error, adaptive schedule and wall-clock |
| 2 | Early commitment, remasking | moderate | ReMDM 2503.00307; RemeDi 2509.23653; CoDR 2610.08833 (this month) | optimal correction policy for long reasoning and multimodal outputs |
| 3 | Confidence calibration during denoising | crowded | 2508.13021; 2512.21336; 2605.14570; CoDR 2610.08833 | proper scoring protocol linking token confidence to sequence correctness |
| 4 | RL likelihood estimators | **saturated** | d1 2504.12216; wd1 2507.08838; GDPO (ICLR 2026); MaskGRPO 2510.02880; ESPO 2512.03759; DiFFPO 2510.02212 | compute-matched comparison; little room for a newcomer |
| 5 | Causal evidence for understanding-generation synergy in unified multimodal diffusion | **sparse** | "Reversing the Flow" (CVPR 2026 Findings, not discrete diffusion); UniDisc 2503.20853; MMaDA 2505.15809; FUDOKI (NeurIPS 2025). Also to read: the ECCV 2026 transferability paper named in the blueprint | interventions on shared representations or modality pathways that separate synergy from interference |
| 6 | Mechanistic interpretability of DLMs | **sparse** | DLM-Scope 2602.05859 (SAEs on Dream-7B, LLaDA-8B); "Induction in Both Directions" 2607.15893; "Steering Without Breaking" 2605.10971; "Subliminal Clocks" 2607.01774 | causal account of token commitment and hidden decoding order; nothing on multimodal DLMs |
| 7 | Memorisation, membership inference, hallucination | moderate | extraction via infilling 2605.24173; MIA 2601.20125, 2609.00873, JUMP 2607.16207; hallucination detection 2604.26139 | multimodal extraction and hallucination; effect of remasking and quantisation |
| 8 | Evaluation validity | crowded | "Is Your Diffusion Sampler Actually Correct?" 2602.19619; 2602.00286; survey 2508.10875 | standard sampler-matched protocol with seeds and intervals |

Checkpoints returned (to verify on the Hub): `s-sahoo/duo` (about 130M), `kuleshov-group/mdlm-owt`,
`louaaron/sedd-small`, `Dream-org/Dream-v0-Instruct-7B`, `GSAI-ML/LLaDA-8B-Instruct`,
`Gen-Verse/MMaDA-8B-Base` (the three large ones need 4-bit loading on 12 GB).

## Orchestrator reading (E0, not yet audited)

Rows 5 and 6 are the thin part of the map and both can be studied on frozen checkpoints, which is
what this GPU allows. Candidate directions for Gate 2:

- **T1 (lead).** Is the "synergy" in a unified multimodal diffusion model causally mediated by
  shared internal features? Activation patching and feature ablation between the image-generation
  and visual-question-answering pathways of MMaDA-8B (and one more unified model if weights load),
  with text-only DLMs as negative controls. Decisive pilot: does ablating the top-k
  generation-critical directions hurt understanding more than ablating k random directions of equal norm?
- **T2 (backup).** Do unified multimodal DLMs memorise and regurgitate training images or captions
  under infilling, and does remasking or quantisation change the rate? Extends row 7 to multimodal.
- **T3 (watch only).** Commitment dynamics and remasking: active and fast-moving, high scoop risk.

Not pursued: new RL objectives (row 4), a new sampler or cache (rows 1, 3, Gemini's proposal).
