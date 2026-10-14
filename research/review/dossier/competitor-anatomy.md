# Competitor anatomy: how the two existing DLM surveys organise the field

Date: 2026-10-14. Agent: paper-reader. Purpose: decide whether `research/review/framework-v0.md` (commitment process, five design choices, error budget, lever-by-error-term taxonomy) is already present in the two closest surveys. This document does not judge whether the framework is good.

Tags: [F] = source fact with section number (paper reports it; E2 for "the survey says X", never for "X is true"); [I] = my inference; [U] = unknown.

## 0. Provenance and coverage

| | Survey 1 (S1) | Survey 2 (S2) |
|---|---|---|
| Title | Discrete Diffusion in Large Language and Multimodal Models: A Survey | A Survey on Diffusion Language Models |
| arXiv | 2506.13759 v5, stamp 19 Sep 2025 | 2508.10875 v3, 04 Jun 2026 |
| Authors | Yu, Li, Wang (NUS) | Li, Chen, Guo, Shen (MBZUAI VILA Lab) |
| Text read | `research/sources/md/arxiv-2506.13759v5.md`, lines 1-5466, all of it (two-column PDF conversion, some paragraphs out of order) | `research/sources/md/arxiv-2508.10875.md` (arXiv HTML, fetched once, HTTP 200), lines 1-1000 body read in full; bibliography (lines 972-1668) only counted and scanned for latest IDs. Taxonomy figure is blank in the HTML ("{forest}"), so it was taken from the v3 PDF text layer (`research/sources/pdfs/arxiv-2508.10875v3.pdf`, converted to `md/arxiv-2508.10875v3-pdf.md`, lines 345-480) |
| Length | 29 pages: main text pp.1-17, references pp.17-22, appendix pp.22-29 | 26 pages: body pp.1-20, references from p.21 |
| References | 175 (numbered 1-175, none missing) | 228 (numbered 1-228) |
| Literature cutoff | latest cited IDs 2508.20072, 2508.20095 (late Aug 2025) | latest cited IDs 2605.10938, 2605.11577; Fig. 2 caption says papers collected "by mid-May" 2026 |

Reading caveats: (1) S1 refs [164]-[175] (scaling laws, InstructGPT, Qwen, FlashAttention, DP, overfitting, Data-Juicer) have no in-text citation in the conversion, and Appendix F ends at F.III; [I] either the conversion lost a later future-directions passage or the survey lists uncited references; the PDF is not cached, so [U]. (2) S1 Sec. VII/VIII are in a different order in the intro text (VIII privacy, VII quantization) than in the headings. (3) I read S2 v3 only, not v1/v2.

## 1. Survey 1 (arXiv 2506.13759 v5)

### 1a. Section tree (to third level) with share
Share = characters of converted text, approximate (two-column interleaving blurs borders). Main text = 83.5k chars, appendix = 35.2k chars.

| Section | Pages | Share of main |
|---|---|---|
| I Introduction | 1-2 | 7.5% |
| II Mathematical Formulations: II.A Discrete Diffusion Model and Transition Matrix; II.B Simplified Masked Diffusion Model; II.C Continuous Time Discrete Denoising Models; II.D Concrete Score; II.E Discrete Flow Matching | 3-6 | 20% |
| III Modeling Language Diffusion: III.A Block Diffusion; III.B Flexible-Length Masked Diffusion; III.C Partial Masking; III.D Diffusion with Optimal Transport Position Coupling | 6-7 | 3% (text is split across columns; true share about 5%) |
| IV Representative Models: IV.A models around 1B; IV.B Large Diffusion Language Models (B.1 DIFFUSION-LLMs, B.2 LLaDA series, B.3 DiffuGPT and DiffuLLaMA, B.4 DiffuCoder, B.5 DREAM series, B.6 TESS 2, B.7 Seed Diffusion); IV.C Large Diffusion Multimodal Models (C.1 Dimple, C.2 LaViDa, C.3 LLaDA-V); IV.D Large Unified Model (D.1 MMaDA, D.2 FUDOKI, D.3 Muddit) | 7-9 | 22% |
| V Training Techniques: V.A Challenges (A.1 low corpus utilization, A.2 random sampling of time index); V.B Initialization; V.C Complementary Masking; V.D Masking Scheduling (D.1 uniform, D.2 token-wise, D.3 block-wise); V.E Reweighting; V.F Distillation through Dimensional Correlations; V.G Reinforcement Learning | 9-11 | 12% |
| VI Inference Techniques: VI.A Unmasking (A.1 discrete-time: (a) random, (b) metric-based, (c) selection policies); VI.B Remasking (B.1 general masked diffusion, B.2 Wide-In Narrow-Out); VI.C Prefilling and Caching; VI.D Guidance; VI.E Sampling (E.1 temporal self-consistency, E.2 particle Gibbs, E.3 early stopping); VI.F Context Length Extension; VI.G Sparse Computation; VI.H Response Length Control | 11-15 | 23% |
| VII Quantization | 15 | 1% |
| VIII Privacy and Safety | 15-16 | 2.4% |
| IX Applications: A language; B reasoning; C vision and multimodal; D robotics and driving; E graph and structured prediction; F biology and drug discovery | 16-17 | 7.5% |
| X Conclusion | 17 | 1% |
| Appendix A Mathematical Formulations (A.I more transition matrices; A.II RDM; A.III concrete score: III.1 losses (a) CSM (b) DWDSE (c) TCSM, III.2 connection with CE, III.3 time independency) | 22-25 | 33% of appendix |
| Appendix B (B.I Block Diffusion; B.II FlexMDM; B.III DDOT) | 25 | 12% |
| Appendix C (C.I scheduling; C.II distillation; C.III train-test input discrepancy; C.IV RL: UniGRPO, VRPO, SDPO, wd1, DCoLT) | 25-27 | 24% |
| Appendix D (D.I continuous-time unmask and remask; D.II guidance: CFG, classifier, reward, energy-based) | 28 | 18.5% |
| Appendix E Quantization (DLLMQuant) | 28-29 | 6% |
| Appendix F Future Directions (F.I Infrastructure; F.II Inference Efficiency; F.III Security and Privacy) | 29 | 7% |

[F] The inference section is the largest single block of the main text together with models (IV) and mathematics (II); there is no evaluation section and no comparison table.

### 1b. Taxonomy
[F] There is no taxonomy figure separate from the outline. Fig. 2 is a tree that mirrors the section list: root "Discrete Diffusion (M)LLMs"; branches Mathematical Formulations (Sec. II), Modeling Language Diffusion (III), Representative Models (IV), Training Techniques (V), Inference Techniques (VI), Quantization (VII), Privacy and Safety (VIII), Applications (IX). Leaves are paper names.
- Fig. 2 leaf groups: Training = Initialization, Complementary Masking, Masking Scheduling, Reweighting, Distillation, Training-Testing Input Discrepancy, Reinforcement Learning. Inference = Unmasking (metrics: confidence, margin, entropy; EB-Sampler; PC-Sampler; confident decoding; block-wise; DUS; continuous-time), Remasking, Prefilling and Caching, Guidance, Sampling, Context Length Extension, Sparse Computation, Response Length Control.
- Fig. 1 (timeline) is the only model-level classification: columns "Models ≤1B", "Language Models", "Multimodal Models", "Unified Models", by year 2021-2025, closed-source models underlined.
- Fig. 3 compares autoregressive and discrete-diffusion models along four items: architecture (attention mask), inference (left-to-right one token versus mask-then-denoise multi-token), training (weighted CE on masked tokens versus CE on all tokens), layer-wise information flow.
- Axes by which models are classified: [I] one axis, scale and modality scope (≤1B / large language / large multimodal / unified). Methods are classified only by the section they were filed under (technique type). No axis is a design choice of the model.

### 1c. Mathematical content
[F] Written out: D3PM forward chain, transition matrices (uniform, absorbing; also hybrid, discretised Gaussian, band-diagonal, embedding-based, Sec. II.A and Appendix A.I), x0-parameterised reverse, VLB plus auxiliary CE (Eqs. 1-12); masked diffusion with alpha_t and its weighted-CE loss in discrete and continuous time (II.B, Eqs. 13-17); CTMC rates, tau-leaping, predictor-corrector (II.C, Eqs. 18-21); concrete score and reverse rate (II.D, Eqs. 22-23; Appendix A.III Eqs. 66-81: CSM, DWDSE score entropy, TCSM); discrete flow matching path and velocity (II.E, Eqs. 24-32); RDM routing variables (A.II); block diffusion likelihood (A.B.I Eqs. 82-85); FlexMDM (A.B.II); DDOT (A.B.III); schedules (V.D, A.C.I); remasking with sigma_t (VI.B.1 Eq. 48) and DFM remask velocity (A.D.I.2 Eq. 110); guidance (A.D.II); RL objectives (A.C.IV).
- One notation across families: [I] partly. Inside discrete diffusion, the transition matrix Q_t covers uniform, absorbing, Gaussian, band, embedding and linear-plus-absorbing channels, and DFM gives a path-and-velocity view. Autoregression, block diffusion and any-order models are not placed in that notation; block diffusion has its own Eq. 82-84. Continuous embedding or simplex diffusion (TESS, Plaid) is named in IV.A but not formulated. The "Gaussian" channel in A.I is a discretised ordinal kernel, not a Gaussian on embeddings.
- Equivalence statements [F]: (1) D3PM "unifies various paradigms such as BERT, autoregressive models, and masked language models" (II.A) with no derivation. (2) DiffuGPT/DiffuLLaMA "establish theoretical connections" between AR next-token prediction and diffusion denoising (IV.B.3), with the logit shift operation as the operational form (V.B); no formula. (3) Ratio versus marginal: the concrete score in absorbing diffusion equals a time-dependent scalar times the clean-data conditional (A.III.3, Eqs. 80-81, RADD), and a CE loss on the posterior fits the concrete score (A.III.2, Eqs. 76-79). (4) TCSM score-based and distribution-based losses are equivalent under a choice of divergences (A.III.1(c), Eq. 73). (5) Parallel confidence decoding versus sequential confidence decoding: "equivalence between the parallel decoding using confidence and sequential decoding using confidence" (VI.A.1(b), credited to Fast-dLLM; cited, not derived). Not found: any statement that masked diffusion equals any-order autoregression (the phrase "any-order" appears only in a reference title and as "any-order property" of FlexMDM, A.B.II). Continuous versus discrete: no equivalence stated (a "Discrete Flow Matching" view is given but not linked to Gaussian diffusion).
- Independence assumptions [F]: classifier guidance "assumes intra-block independence" (A.D.II.2, Eq. 114); Di4C consistency loss captures "multi-dimensional correlations without assuming independence" (A.C.II). Neither is connected to a sampling-error expression.

### 1d. Inference and training organisation
- Inference [F]: a flat list of technique types (VI.A-H). Unmasking is split into discrete-time (random; metric-based with confidence, margin, entropy, EB-Sampler set-entropy metric Eq. 42, PC-Sampler Eq. 43; selection policies: top-s_t, confident decoding with threshold gamma Eq. 44, block-wise, DUS Eqs. 45-47) and continuous-time (flow-matching jump process, A.D.I.1). The set of positions to commit is therefore described, but as "which and how many tokens to unmask" (VI.A) with no stated criterion for why. Remasking (VI.B) is separate. Caching (VI.C) is separate. Guidance (VI.D) is "post-processing on the predicted logits". Sampling (VI.E) holds temporal voting, particle Gibbs and early stopping. The VI intro says inference techniques "affect both performance and efficiency", typically a trade-off.
- Training [F]: challenge-led (V.A names two problems), then technique types (V.B-V.G). Reveal-law material appears as techniques: block-wise SFT mask rule (V.D.3: clean prefix, Bernoulli-masked active block, hidden suffix), complementary masking (V.C), partial masking (III.C), block diffusion (III.A).

### 1e. Multimodal and unified models
[F] IV.C (Dimple, LaViDa, LLaDA-V: vision encoder plus projector plus dLLM) and IV.D (MMaDA, FUDOKI, Muddit; UniDisc in IV.A). Multimodal-specific methods: complementary masking (V.C, LaViDa), AR-then-diffusion (V.B, Dimple), UniGRPO (V.G, A.C.IV.1), prefilling in dMLLMs (VI.C), applications in IX.C. FUDOKI is described as two output heads, one per modality (IV.D.2). No treatment of per-modality corruption laws as a design variable, and no discussion of committing tokens of different modalities in the same step.

### 1f. Evaluation
[F] No evaluation section, no results table, no benchmark list. Quantitative statements are isolated speedups (up to 10x in the abstract, 1.5-7x or 2-7x from prefilling, about 10x from caching at update interval 2-8; Abstract, IV.C.1, VI.C). No comparison of protocols and no critique of evaluation practice. The only related text is Appendix F.I, which says standardised infrastructure would promote fair comparisons.

### 1g. Open problems (Appendix F)
- F.I Infrastructure: no standardised modular training frameworks or open pretrained models for dLLMs.
- F.II Inference efficiency: efficient attention, multi-scale tokens, progressive distillation, adaptive step schedules, INT8/INT4 inference.
- F.III Security and privacy: memorisation and leakage, misuse, and moderation difficulty because content only appears at the final denoised text.
- [U] possible further items lost in conversion (see section 0).

### 1h. References and cutoff
175 references; cutoff late August 2025; v5 stamped 19 Sep 2025.

## 2. Survey 2 (arXiv 2508.10875 v3)

### 2a. Section tree (to third level) with share
Share = characters of body text (112k chars), approximate.

| Section | Pages (PDF) | Share |
|---|---|---|
| Abstract, I Introduction (incl. Fig. 1 timeline, Fig. 2 trend, Fig. 3 taxonomy, advantages list) | 1-4 | 12% |
| II Paradigms of Diffusion Language Models: II-A Preliminaries (A1 masked LMs, A2 autoregressive LMs, A3 other paradigms: seq2seq, permutation LMs); II-B Continuous DLMs (Table I, Fig. 4); II-C Discrete DLMs; II-D Hybrid AR-Diffusion | 3-9 | 28% (6.6 + 10.2 + 7.8 + 3.7) |
| III DLMs: Pre-training and Post-training: III-A Pre-training and SFT; III-B Post-training for Reasoning (B1 DoT and DCoLT; B2 policy gradient; B3 preference optimisation; Table II) | 9-11 | 16.5% |
| IV Inference Strategies: IV-A Parallel Decoding; IV-B Unmasking/Remasking; IV-C Guidance; IV-D Efficient Inference (KV cache, feature cache, step distillation) | 12-14 | 10% |
| V Multimodal and Unified Approaches (LLaDA family, LaViDa, LaViDa-O, MMaDA, MMaDA-Parallel, Dimple, D-DiT, UniDisc, Fudoki, Muddit, Lumina-DiMOO) | 14-16 | 12% |
| VI Performance Study (Fig. 6) | 16 | 3% |
| VII Applications: VII-A conventional NLP; VII-B code; VII-C biology and science; VII-D robotics | 17-18 | 9.6% |
| VIII Challenges and Future Directions: VIII-A Major Challenges (1-4); VIII-B Future Directions | 19-20 | 7% |
| IX Conclusion | 20 | 1% |

[F] The inference section is short (about 10%); the paradigm survey and post-training dominate. Reasoning RL occupies more text than all inference methods.

### 2b. Taxonomy (Fig. 3, from the PDF text layer, v3)
[F] Fig. 3 is a left-to-right tree titled "Taxonomy of Diffusion Language Models" with four trunks, each annotated with section numbers.
- Paradigms (Sec. 2): Continuous Space Models (Diffusion-LM, SED, LATENTOPS, Diffuseq, CDCD, Difformer, LD4LG, GENIE, InfoDiffusion, EDDPMs, SMOOTHIE, TESS, TESS 2, LDEBM, LangFlow, ELF, BitLM, FMLM, Cola-DLM); Discrete Space Models (D3PM, DiffusionBERT, LLaDA, RDMs, MD4, MDLM, Diffusion-LLM, Diffusion-NAT, Plaid, SEDD, RADD, DFM, DDPD, MGDM, Diffu-LLaMA, Dream-7B, GIDD, LongLLaDA, Seed Diffusion, LLaDA-MoE, LLaDA2.0); Hybrid DLMs (SSD-LM, AR-DIFFUSION, BD3-LM, CtrlDiff, SpecDiff, SDAR, TiDAR, SDLM, NBDiff, Efficient-DLM, I-DLM, ReFusion, CARD).
- Training Strategies (Sec. 3): Pre-training (from scratch; adapting from AR models; adapting from image diffusion models) and Post-training (DoT, DCoLT; policy gradient; preference optimisation).
- Inference and Optimization (Sec. 4): Parallel Decoding; Unmasking/Remasking; Guidance; Efficiency Techniques (KV cache, feature cache, distillation, pruning).
- Multimodal and Applications (Sec. 5, 7): Multimodal DLMs; Conventional NLP; Code Generation; Computational Biology; Robotics.
- Axes [I]: (1) diffusion space (continuous / discrete / hybrid with AR) for models; (2) training stage (pre-training source, post-training objective); (3) inference goal. The only axis that classifies models is the space axis.
- Other figures: Fig. 1 timeline (continuous / discrete / multimodal DLMs); Fig. 4 training and inference procedure of AR, discrete, continuous and block-diffusion models; Fig. 5 six inference strategies (a parallel decoding, b unmasking and remasking, c classifier-free guidance, d KV cache, e feature cache, f step distillation); Fig. 6 benchmark scatter; Fig. 7 generation under different step counts.
- Tables [F]: Table I "Summary of diffusion language models, configurations, and their design choices": columns Model | Parameters | Diffusion type | Task | Training data; 36 rows (D3PM to BitLM). Table II "post-training methods for DLMs' reasoning": columns Method | Algorithm Type | Core Goal | Key Technical Innovation | Model Type; 13 rows (DoT, DCoLT, SEPO, diffu-GRPO, coupled-GRPO, UniGRPO, VRPO, IGPO, wd1, SAPO, SPG, BGPO, JustGRPO).

### 2c. Mathematical content
[F] Written out: MLM loss (Eq. 1), NSP (2), AR factorisation and loss (3-4), permutation LM (5) in II-A; continuous forward chain, closed-form marginal, regression objective (6-9) in II-B; D3PM marginal with cumulative Q (unnumbered) and LLaDA masked-CE loss (10) in II-C; block-diffusion loss (11) in II-D; SEPO objective (12) in III-B2; classifier-free guidance (13) in IV-C.
- One notation across families: [I] no. Each family is given in its own symbols, and indices change meaning between equations (subscript i is a position in Eqs. 1 and 3 but x_t is a timestep in Eq. 6; Eq. 10 uses a superscript for position). Families are placed side by side, not specified by shared choices.
- Equivalence statements [F]: RADD "formally unifies the training objectives of absorbing discrete diffusion and any-order autoregressive models" (II-C), with the concrete-score-as-conditional-times-scalar statement in the same paragraph (the ratio and marginal link); masked DLMs with block-wise decoding "can be seen as instances of hybrid AR-diffusion modeling" (II-D); the any-order denoising objective is credited for data reuse (VI). Permutation LMs are contrasted, not equated, with DLMs (II-A3). Continuous and discrete are separate paradigms; LangFlow is said to connect embedding-space DLMs with flow matching via a Bregman divergence (II-B). No derivations.

### 2d. Inference and training organisation
- Inference [F]: IV opens with three goals: quality (unmasking and remasking), control (guidance), efficiency (KV/feature cache, step distillation). Then IV-A parallel decoding (Fast-dLLM threshold, APD, SlowFast, SpecDiff, Dimple, Learn2PD, dParallel), IV-B unmasking/remasking (ReMDM; "one of the most critical inference levers"), IV-C guidance (CFG Eq. 13, FreeCache, DINGO), IV-D efficient inference, split into "lowering the per-step computational overhead" (KV cache, feature cache) and "reducing the total number of diffusion sampling steps" (step distillation). Di4C is placed under step distillation as "explicitly distilling inter-token correlations".
- Training [F]: III-A (initialise from AR or image-diffusion models; scaling-law remarks; SFT; complementary masking; train-inference discrepancy) and III-B (reasoning post-training by RL family, Table II).

### 2e. Multimodal and unified models
[F] Sec. V: understanding models (LLaDA-V, LaViDa, LaViDa-O, Dimple) and unified models (MMaDA, MMaDA-Parallel, D-DiT, UniDisc, Fudoki, Muddit, Lumina-DiMOO), plus Table I "Task" column marking Multimodal and Multimodal Unified. D-DiT is described as continuous diffusion for images plus masked discrete diffusion for text with a summed loss (V), so per-modality corruption differences are visible in the text of one model. MMaDA-Parallel lets text and images "interact bidirectionally at every denoising step" with a cross-modal consistency RL reward (V). VII-D has UD-VLA (image and action tokens denoised together). VIII-B lists "Multimodal Unified Reasoning" as a gap. No statement about dependence between modalities when committed in the same step.

### 2f. Evaluation (Sec. VI)
[F] A scatter of eight benchmarks against parameter count, AR versus DLM: GenEval overall, MME, GQA (caption writes "CQA"), HellaSwag, PIQA, HumanEval, GSM8K, MMMU. Text adds GPQA and MATH claims. Data "primarily taken from original publications", with substitutes from later works. Conclusion: DLMs generally competitive, stronger on math and science benchmarks. No table of numbers, no matching of decoding budget, steps, block length or shots, and no critique of evaluation practice. The only step sweep is the qualitative Fig. 7 (LLaDA 128 tokens, MMaDA 256 tokens; coherent only at 1 or 2 tokens per step).

### 2g. Open problems (Sec. VIII)
- VIII-A.1 Parallelism-performance trade-off: independent sampling of positions ("Parallel Decoding Curse"), illustrated by an ABABAB/BABABA toy and Fig. 7.
- VIII-A.2 Infrastructure: no native framework support and no vLLM-like serving.
- VIII-A.3 Long-sequence and dynamic-length generation: fixed canvas, 4,096 context limit, O(N^2) per step and O(N^3) overall without caching.
- VIII-A.4 Scalability: DLMs not scaled beyond roughly 7-8B (a few larger, e.g. LLaDA2.0).
- VIII-B Future directions: training efficiency; quantisation and binarisation; pruning and distillation; multimodal unified reasoning; DLM-based agents.
- Mismatch [F]: intro says the challenges include reasoning and agent capability; Sec. VIII-A does not list them as challenges.

### 2h. References and cutoff
228 references; cutoff mid-May 2026.

## 3. Verdicts on the six framework-v0 elements

Scale: full / partly / none. Quotes are the closest passages.

| # | Element | Survey 1 | Survey 2 |
|---|---|---|---|
| i | Single specification of all families by a small set of design choices (channel, reveal law, predictor, commitment policy, revision) | **Partly.** Channel (C1) is specified in one notation for uniform, absorbing, hybrid, ordinal and embedding transitions (II.A, A.I) and as a probability path with scheduler (II.E); predictor variants (x0, ratio, velocity) appear in II.A, II.D, II.E; revision appears as remasking Eq. 48 (VI.B.1) and remask velocity Eq. 110 (A.D.I.2). Reveal law (C2) and commitment policy (C4) appear only as filed techniques (V.D.3, III.A, VI.A). No spec; AR, block and continuous Gaussian families are outside the notation. | **Partly, thin.** Only one coarse axis: continuous / discrete / hybrid AR-diffusion (II intro, Fig. 3 Paradigms). Unmasking/remasking is in IV, separately. No shared notation (2c). |
| ii | Design-space table placing many models in one notation | **None.** No comparison table of any kind; Fig. 1 is a timeline and Fig. 2 an outline. | **Partly, thin.** Table I lists 36 models, but its columns (parameters, diffusion type, task, training data) are metadata; only "Diffusion type" is a design choice. Caption says "design choices". Table II compares post-training methods by algorithm type, goal, innovation, model type. |
| iii | Sampling-error decomposition: commit-several-tokens term (total correlation or mutual information), model-error term, others | **None.** Closest: EB-Sampler set-entropy metric given as Eq. 42 with no error interpretation (VI.A.1(b)); Di4C "capturing multi-dimensional correlations without assuming independence" (A.C.II); intra-block independence assumption in guidance (A.D.II.2). No decomposition, no bound. | **Partly (first term only, qualitative).** VIII-A.1 identifies that parallel prediction samples positions independently, "failing to account for dependencies among positions", with a toy example and Fig. 7. Also DUS "minimize an upper bound on joint entropy gain" (VII-B, one sentence). No formula, no model-error term, no decomposition, not tied to a KL. |
| iv | Classification of inference methods by the error term they reduce | **None.** Methods are listed by technique type (VI.A-H). | **None.** Nearest: goal split in IV intro (quality / control / efficiency) and IV-D split (cost per step versus number of steps). Goals are not error terms; the two efficiency routes (cache, distillation) are named, but parallel decoding sits apart in IV-A. |
| v | Caching as cost-only, distinct from methods that change quality at fixed forward passes | **Partly.** VI.C states that for AR models caching is lossless while for dLLMs it is "not theoretically lossless", because bidirectional attention changes cached states; reports small degradation at short refresh intervals. RADD time-independence permits exact reuse of network outputs and fewer NFEs (A.III.3). Not framed as a quality-versus-passes invariance and not contrasted with quality-changing methods. | **Partly.** Efficiency is a separate goal from quality (IV intro); cache described as lowering "per-step computational overhead" versus distillation lowering step count (IV-D), with accuracy loss figures (e.g. under 1% for DualCache). No statement that caching leaves the quality-versus-passes curve unchanged, and no definition of an approximation term. |
| vi | Cross-modal dependence in parallel commitment for unified models | **None.** IV.D describes architectures (two heads in FUDOKI, shared token space in MMaDA, Muddit). | **None.** Adjacent: MMaDA-Parallel cross-modal consistency RL (V), UD-VLA joint denoising (VII-D), Fig. 7 showing the parallelism-quality trade-off in MMaDA (text), and "Multimodal Unified Reasoning" gap (VIII-B). No analysis of dependence across modalities within a step. |

Bottom line [I]: neither survey contains the framework as an organising principle. Pieces present: S1 has the most mathematics (channel family, concrete-score/marginal link, remasking and DFM correctors) and a partial caching-is-approximate remark; S2 has the only explicit statement of the parallel-decoding independence problem, an explicit link between masked diffusion and any-order autoregression (credited to RADD), a goal-level split of inference, and the only model table. Not present in either: a commitment-process definition, the TC/model-error decomposition, a lever-by-error-term taxonomy, caching as a formally cost-only class, cross-modal total correlation. Neither survey uses the terms total correlation or mutual information.

## 4. Pointers for the attribution step (names only; I did not read these papers)

Items the surveys cite where pieces of framework-v0 may already be proved or measured, to be checked by the attribution and novelty agents: EB-Sampler (S1 [60]); DUS dilated schedule (S1 [62]; S2 [156]); Di4C distillation through dimensional correlations (S1 [54]; S2 [123]); Fast-dLLM parallel-versus-sequential confidence analysis (S1 [67]; S2 [45]); RADD (S1 [28]; S2 [74]); "Train for the worst, plan for the best" on token ordering (S1 [59]); ReMDM remasking (S1 [63]; S2 [47]); GIDD (S1 [24]; S2 [78]); Campbell et al. continuous-time framework (S1 [25]); DDPD planner and denoiser (S2 [76]); Learn2PD and dParallel (S2 [109], [110]).

## 5. Unknowns and cautions

- [U] S1 Appendix F may be incomplete in the conversion (section 0).
- [U] S2 v1/v2 contents (an earlier version may have differed); only v3 read.
- [U] S2 body text of Sec. IV could cite error analyses only in the bibliography titles; I did not read bibliography entries beyond counting and latest IDs.
- A verdict of "none" means the element was not found by a full read of the converted body text. The S2 HTML math was read through its LaTeX alt text; equation numbering is from the HTML.
