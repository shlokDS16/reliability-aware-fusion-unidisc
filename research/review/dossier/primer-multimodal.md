```yaml
agent: paper-reader
date: 2026-10-14
brief: Primer chapter 3 (unified multimodal discrete-diffusion and hybrid AR+diffusion models); place each model in framework-v0 C1-C5; collect every piece of evidence for or against P5.
sources_examined:
  - arXiv:2408.12528v7   # Show-o (Xie et al.), verified title and ID by fetching arxiv.org/html
  - arXiv:2503.20853v1   # UniDisc (AW0261)
  - arXiv:2505.15809v2   # MMaDA (AW0260), html v2
  - arXiv:2511.09611v3   # MMaDA-Parallel (AW0248)
  - arXiv:2505.20147v3   # FUDOKI (AW0256)
  - arXiv:2510.06308v1   # Lumina-DiMOO (AW0253)
  - arXiv:2408.11039v1   # Transfusion (Zhou et al.), verified
  - arXiv:2505.14683v3   # BAGEL, "Emerging Properties in Unified Multimodal Pretraining" (hybrid baseline named by Lumina-DiMOO, MMaDA-Parallel, LaViDa-O, Dynin-Omni), verified
  - arXiv:2506.15564v3   # Show-o2 (hybrid with flow head; has the only CFG x steps grid)
  - arXiv:2509.19244v3   # LaViDa-O (AW0252), targeted sections only (planning/reflection)
  - github.com/tyfeld/MMaDA-Parallel, file MMaDA-Parallel-A/generators/parallel_generator.py and inference.py, main as fetched 2026-10-14 (API-reported sha 5cf89786e1258c7ad2eb529be9453853f12098d5)
  - huggingface.co/api/models for tyfeld/MMaDA-Parallel-A, -M and aswerdlow/unidisc_interleaved (model cards, E1)
  - research/review/framework-v0.md (sec 1-4), dossier/primer-gaussian.md (sec 0, 5), feasibility/stage2/summary-remask-synergy.md
  - research/review/dossier/primer-multimodal-check.py (own script; output in sec 4 and 5)
coverage: |
  Text source: cached arXiv HTML converted with markitdown (md copies saved in the MAIN checkout research/sources/md/ for
  2503.20853, 2505.15809, 2505.20147, 2511.09611, 2510.06308, 2509.19244, 2505.16839(not opened), 2604.00007(not opened),
  2505.23606(not opened) and, newly fetched from arxiv.org/html, 2408.12528, 2408.11039, 2505.14683, 2506.15564; new html files in research/sources/html/).
  Conversion garbles some symbols (a minus sign shows as "?"); signs of CFG formulas were checked against the printed code or equation where possible.
  READ. Show-o: Sec 3 (all), 4.4, 4.6, App C, D, F, I (Table 4, 5, Fig. 11 caption and text). UniDisc: Sec 1, 3 (all), 4 (all), App A.1-A.2, B.1-B.5, C, F (Tables 3, 4), G.2, H (Tables 5-7), I (all), J; Fig. 5 and Fig. 22 viewed as images.
  MMaDA: Sec 1 (Table 1), 2.1, 2.2, 3, 4.1-4.2, 5.1-5.4 (Tables 2, 5, 6). MMaDA-Parallel: Sec 1, 3 (all), 4 (all), App A, B.2, D (not), E, F (reasoning-trace paragraph), H, I, J; Fig. 5 viewed as image.
  FUDOKI: Sec 2 (not), 3 (all), 4.1, 4.3, App C, F; grep for guidance (none found). Lumina-DiMOO: Sec 3.1-3.3, 4.4, 7.1-7.2 (Table 1, 2). Transfusion: Sec 3, 4.1-4.3 (Tables 3-8).
  BAGEL: Sec 2.1-2.4, 7.4. Show-o2: Sec 3.1-3.2, 4.4 (text), 4.5 (Table 11 and text). LaViDa-O: Sec 3 planning paragraph, A.7, B.5 (Tables 13-16).
  NOT READ. Muddit, LaViDa (2505.16839), Dynin-Omni (md produced for 2604.00007, 2505.23606, 2505.16839 but not opened). UniDisc Fig. 4, 13, 24 values (only captions and text); UniDisc code. MMaDA-Parallel-M generator (only the -A generator was read); MMaDA-Parallel Sec D (preliminaries), K. FUDOKI Fig. 5 values (figure only), App B, E. MMaDA Sec 2.3 (UniGRPO), 4.3-4.4 tables, 5.5. Lumina-DiMOO Sec 6 evaluation tables. BAGEL Sec 3-6, 7.1-7.3, 7.5, sampling-step and CFG values. Transfusion Sec 4.4-4.5. Show-o2 Sec 4.2-4.3. LaViDa-O all other sections. No weights were downloaded; nothing was run except the toy script.
  Evidence level: E2 for the sections listed (the papers were not read in full, so strictly E2-), E3 for the one code file at the stated sha, E1 for model cards, E4 for the toy script (algebra only).
claims:
  - statement: "No paper in the set measures cross-modal conditional dependence (or total correlation) per sampling step, or reports text-image consistency as a function of the sampling step."
    status: supported
    evidence: sections listed under coverage; nearest are UniDisc App I Fig. 24-25 (CFG logit distance by decoded fraction; CLIP by CFG-on steps), MMaDA-Parallel Fig. 5 (one example) and Sec 3.3
    level: E2
    confidence: 0.75
  - statement: "The only matched-looking contrast of joint against modality-sequential generation (MMaDA-Parallel Tables 3 and 10) favours joint on text-image alignment, but it is confounded and cannot test the cross-modal E_fact term."
    status: mixed
    evidence: MMaDA-Parallel Sec 4.3, Table 3, Table 10, App I; sequential variant trained with one modality noised at a time (Sec 4.3 RQ1)
    level: E2
    confidence: 0.8
  - statement: "The released MMaDA-Parallel-A sampler commits no image tokens in the first quarter of the text steps (image steps are placed at linspace(text_steps//4, text_steps-1, timesteps)), unlike the paper's description of parallel decoding at every denoising step."
    status: supported
    evidence: parallel_generator.py lines 156-160, 219-220 (sha above); inference/README defaults text_steps 128, timesteps 64
    level: E3
    confidence: 0.85
  - statement: "Cross-modal total correlation is an exact additive part of E_fact: TC(x^A | z) = TC(text part) + TC(image part) + I(text part; image part | z)."
    status: supported
    evidence: primer-multimodal-check.py section A, max error 1.3e-15 over 800 cases; section B identity E_fact = KL(q||p) to 6.6e-16
    level: E4 (toy)
    confidence: 0.95
  - statement: "Framework-v0 sec 3 claim that unified models enter 'with no new machinery' is not correct as stated: classifier-free guidance, per-modality loss weights and schedules, continuous image channels and output-level revision (planning, reflection) need explicit rows."
    status: contradicted
    evidence: sec 5 Q2 below (UniDisc Alg. 1 and Sec 3.3; MMaDA-Parallel Eq. 2; Transfusion Eq. 4; Show-o Eq. 12; LaViDa-O Tables 13, 16)
    level: E2
    confidence: 0.85
competing_explanations:
  - "MMaDA-Parallel's alignment gain for joint decoding can come from bidirectional information flow (the sequential text cannot see the image) and from different training, not from a lower cross-modal commitment cost."
  - "UniDisc's finding that image FID saturates by about 32 forward passes while text perplexity keeps improving can reflect within-modality dependence (text) rather than anything cross-modal."
unknowns:
  - "How MMaDA-Parallel's paper-reported 30 image steps and 128 text steps (App E) map onto forward passes; whether the paper's experiments used the quarter-step text head start that the released -A code has."
  - "Whether UniDisc's Fig. 5(c,d) sweep is conditional or unconditional joint generation (caption says only 'NFE')."
  - "Licence of the UniDisc checkpoints (HF card and GitHub API state none)."
next_test: {hypothesis: "P5a: per-step cross-modal conditional MI between co-committed text and image tokens is concentrated in early steps; P5b: at matched NFE a schedule that separates dependent pairs beats joint commitment by roughly the cross term", intervention: "frozen UniDisc 1.4B interleaved checkpoint; joint vs text-first vs image-first vs alternating commitment at matched NFE; per-step cross-modal CMI probe", primary_metric: "paired text-image consistency (CLIPScore or ITM) per sample, with per-modality entropy as E_sel control", falsifier: "joint is not worse than every modality-separated arm at any matched NFE in {16,32,64,128}, within a pre-registered margin, and the probe shows no early concentration", gpu_hours: 8}
```

# Primer, chapter 3: unified multimodal discrete-diffusion and hybrid AR+diffusion models

Tags. [S] stated by the paper at the location given (E2: "the paper reports", never "is true"). [I] my inference. [H] hypothesis. [V] verified here by `research/review/dossier/primer-multimodal-check.py`, which is an algebra check on toy distributions and says nothing about any paper's model. "Not found" means I searched the text listed under coverage.

## 0. Bottom line

1. **P5 has no direct evidence either way.** No paper in the set measures cross-modal conditional dependence per step, or reports text-image consistency against step. Nothing varies the number of joint steps while measuring a cross-modal quantity (sec 4).
2. **The one matched-looking contrast goes the opposite way on its metric and cannot test P5.** MMaDA-Parallel Table 10: fully parallel 71.0 / 63.2 / 59.8 (text align / image align / output align) against semi-parallel (text first for half the steps) 68.3 / 60.7 / 57.5 and sequential text-then-image 64.2 / 56.5 / 54.1. Confounds: the sequential text cannot see the image (so the contrast measures the value of bidirectional flow, a benefit, not the cost term), training differs, one run, GPT-4.1 judge, no interval (sec 4, rows B1-B3).
3. **The released MMaDA-Parallel-A code is not "parallel at every step".** Image commits are scheduled only from `text_steps // 4` onward [E3], so the first quarter of forward passes commits text only. The paper's text says text and image are decoded jointly at every step (Sec 3.2, Fig. 3b). Whether the paper's numbers used this schedule is unknown.
4. **The premise of P5 (cross-modal dependence is front-loaded) has weak indirect support, from guidance.** UniDisc App I: the L2 distance between conditional and unconditional logits shrinks as more tokens are decoded (Fig. 24, values not read), and applying CFG only on steps 1-3 of 24 gives CLIP 0.301 against 0.312 for all steps and 0.283 for steps 22-24 (Fig. 25, text). Guidance in UniDisc drops a whole modality, so this is a measurement of how much the other modality's information matters per step. It does not measure the cost of committing together.
5. **P5 as worded is close to an identity and should be rewritten.** [V] E_fact splits exactly into within-text, within-image and cross-modal parts, and the cross-modal part is the conditional mutual information I(text tokens; image tokens | z) of the pair committed together. "Costly where cross-modal dependence is high" follows from the identity. The empirical content is (a) where in the trajectory the cross-modal CMI sits and how big it is next to the within-modality terms, and (b) which schedules avoid it. The toy also shows the trap: a modality-sequential schedule at the same k removes the cross term and pays within-modality total correlation instead, and can be worse than an interleaved schedule (sec 4, toy rows).
6. **"No new machinery" (framework-v0 sec 3) fails in four places:** guidance, per-modality loss weights and schedules, continuous image channels in hybrids, and output-level revision (planning, reflection). Eleven edits are in sec 6.
7. **Cheapest P5 test:** frozen UniDisc 1.4B interleaved checkpoint (5.63 GB file, licence not stated), joint against text-first against image-first against alternating commitment at matched forward passes, with a per-step cross-modal CMI probe. About 8 GPU-hours, not run (sec 5, Q5).

## 1. Notation

Framework-v0 sec 1 (C1-C5, E_fact, E_learn, E_sel, E_approx) and primer-gaussian sec 1. Additional symbols.

- Sequence x = (x_T, x_I): text tokens x_T (positions T) and image tokens x_I (positions I). Committed set at step n: A_n = A_n^T ∪ A_n^I. z_n = revealed state.
- Cross-modal term at step n: X_n = I( x^{A_n^T} ; x^{A_n^I} | z_n ), conditional mutual information of the text and image tokens committed in the same step.
- Decomposition [V, primer-multimodal-check.py section A]: TC(x^{A_n} | z_n) = TC(x^{A_n^T} | z_n) + TC(x^{A_n^I} | z_n) + X_n. Hence E_fact = E_fact^T + E_fact^I + E_fact^X with E_fact^X = Σ_n E_q[X_n]. Defined only for discrete (committed) modalities.
- k_n^T, k_n^I: tokens of each modality committed at step n. Joint pass: both modalities' logits come from one forward call (true of all discrete models here), committed jointly if k_n^T > 0 and k_n^I > 0.
- Guidance: logits ℓ_w = (1 + w) ℓ_cond − w ℓ_uncond (Show-o App D Eq. 12; the MMaDA-Parallel code writes cond + w (cond − uncond), the same thing).
- Version tags are in the YAML. "As printed" marks equations whose symbols were damaged in conversion.

## 2. Per-model records

Each record: what it is [S], then the C1-C5 placement, then P5-relevant items. Locations are section, table or figure of the version read.

### 2.1 Show-o (2408.12528v7)
- Architecture [S Sec 3.1-3.2]: Phi-1.5 LLM; one unified vocabulary of text tokens plus 8,192 new image tokens from a MAGVIT-v2 lookup-free quantiser (256 px gives 16x16 tokens; 512 px variant used for generation results, Sec 4.3). "Omni-attention": causal for text, full for image tokens; image tokens see preceding text (T2I); text sees all preceding image tokens (understanding).
- Objectives [S Sec 3.2, Eq. 1-3]: next-token prediction on text, MaskGIT-style mask-token prediction on image tokens at a random ratio set by a time step, loss only on masked tokens; L = L_MTP + α L_NTP. Null-text replacement for CFG.
- Sampling [S App D, Eq. 12-13]: image: all-mask start, T steps, conditional and unconditional logits mixed with scale w, sampled tokens ranked by their own probability, lowest re-masked by the schedule γ; already unmasked tokens get confidence 1.0 (never re-masked). Text: autoregressive, one token per pass. Understanding: text AR after the image.
- Step and guidance evidence [S App I, Fig. 11]: qualitative only. "With just five steps" a rough image; 25 steps adheres to the prompt; 50 more detailed; CFG w of 3 and 5 compared with none. No metric sweep.
- Mixed-modality generation [S Sec 4.4]: interleaved text and keyframes, each segment AR over segments, image segment by diffusion. Sequential by construction.
- C5 none for committed tokens. The confidence ranking of sampled values is an E_sel mechanism (framework-v0 sec 2).

### 2.2 UniDisc (2503.20853v1)
- Architecture [S Sec 3.3, App B.1]: bidirectional decoder-only transformer, 2D RoPE for image tokens, 1D RoPE for text, learned modality embeddings. Image tokens by lookup-free quantisation at downsample 16 (256 image tokens at 256 px; 1024 at 512 px for the 1.4B model), text by the Llama tokenizer (128 text tokens); default sequence 384.
- Training [S Sec 3.2-3.3, Alg. 1, Eq. 3]: absorbing mask, one t per sample and the same alpha_t for both modalities (Alg. 1 line 9), loss alpha'/(1 − alpha) log p on masked positions, weight floored by a min-SNR rule (limit 5). With probability 0.1 all tokens of one random modality are set to mask (Alg. 1 lines 11-15): this is both CFG training and the only place where states "one modality fully masked, other partly revealed" are sampled in training.
- Sampling [S Sec 3.4, Alg. 2, Fig. 5]: MaskGIT confidence ranking (with top-p and temperature) or DDPM-style random sets. Alg. 2 ranks all positions of the joint sequence in one pool: text and image tokens are committed in the same forward pass. Chosen: confidence-based.
- Step evidence [S Fig. 5 (c), (d), viewed as image; values read by eye, approximate]: image FID against NFE is flat near 20 from about 32 NFE to 384 NFE (MaskGIT variants) and falls from about 70 to 150 at 1-2 NFE; generated-text GPT-2 perplexity keeps falling to roughly 64-128 NFE (MaskGIT+nucleus about 66 at 8 NFE, about 23 at 32, about 19 at 64, about 16 at 384; DDPM-style 220 to 40). NFE = 384 is one token per pass. Sec 4.2 text: image generation saturates near 32 NFE, text benefits from more steps with diminishing returns.
- Guidance [S Sec 3.3, App I]: w = 1.5 chosen for UniDisc (Fig. 4 sweeps w), 0.5 for the AR baseline; AR benefits less. Fig. 25: CFG only on steps 1-3 of 24 gives CLIP 0.301, steps 12-14 0.293, steps 22-24 0.283, all 24 steps 0.312. Fig. 24 (caption): L2 distance between unconditional and conditional logits on still-masked tokens decreases as sampling proceeds, and is larger for UniDisc than for the same network decoded left to right. Formula printed with "+" (conversion), sign not trusted.
- Joint-generation analysis [S App G.2, Fig. 21-22, figure only]: the authors ask whether UniDisc generates background first, or text before image, or everything at once; they report that it generates all concepts at once in proportion to their area and shows no positional bias. The text-versus-image ordering is not separately quantified in the text.
- Ablations [S App F, Tables 3, 4]: giving token modality and setting invalid tokens to −inf: 94.7 against 93.8 validation perplexity (small); no Softmin-SNR 109.6 and neither 111.2; discrete time 13.8 FID against 11.4.
- Hardware and size [S]: 115M/340M ablation models, 1.4B large model (Sec 4.4).

### 2.3 MMaDA (2505.15809v2)
- Architecture [S Sec 2.1, 4.1]: initialised from LLaDA-8B-Instruct, text by the LLaDA tokenizer, image by the Show-o MAGVIT-v2 quantiser (codebook 8,192, f = 16, 512 px gives 1,024 tokens). One mask predictor, one cross-entropy with weight 1/t (Eq. 1). SFT masks only the response, prompt kept clean (Eq. 2).
- Sampling [S Sec 3]: text: LLaDA semi-autoregressive blocks of 64, length 1,024, 512 steps (2 tokens per step, lowest-confidence), linear schedule. Image: one block, cosine schedule, low-confidence remasking, 50 steps, CFG scale 3.5, 1,024 tokens. The paper's own Table 1 labels MMaDA vision and language samplers as separate; MMaDA-Parallel states MMaDA "decoding remains sequential across modalities" (Sec 3.2).
- Step sweep [S Sec 5.4, Table 6]: image CLIP 32.8 / 32.0 / 31.7 at 1,024 / 50 / 15 steps; understanding CLIP-based metric 35.5 / 36.1 / 35.4 at 1,024 / 512 / 256; text MMLU 66.9 / 66.3 / 65.7 at 1,024 / 512 / 256. Each modality is generated in its own call. Guidance level for the sweep not stated.
- Synergy [S Sec 5.3, Fig. 6]: qualitative training curves; already covered by the stage-2 synergy summary and the three papers the brief says to cite.

### 2.4 MMaDA-Parallel (2511.09611v3)
- Architecture [S Sec 3.2, 4.1, App H]: starts from MMaDA-MixCoT (LLaDA-8B, MAGVIT-v2); an A variant on Lumina-DiMOO with aMUSEd-VQ exists (HF card). Sequence `<task><soi>[img]<eoi><bos>[text]<eos>` for input, then output image and output text; input kept clean, output noised with one beta_t.
- Objective [S Eq. 1-2, Table 9]: timestep-reweighted CE with per-modality weights, w_text(t) = 1/t and w_img = 1 (default); "both 1/t" gives output align 56.3, "both 1" 57.0, default 59.8.
- Sampling [S Sec 3.2, App E, H]: one forward pass gives logits for all text and image tokens. Two schedulers: text linear reveal with semi-AR confidence decoding (256 tokens, blocks of 64, 128 steps, 2 per step), image cosine reveal with global MaskGIT confidence (1,024 tokens, 30 steps). CFG scale 3.5 for image, 0 for text; 10 percent text and 10 percent image dropped in training. How 30 image steps sit inside 128 text steps is not stated in the paper.
- Code [E3, MMaDA-Parallel-A, sha above]: `generate_ti2ti` runs `text_steps` forward passes; text commits every pass; image commits only at `image_generation_step_indices = linspace(text_steps//4, text_steps-1, timesteps).round()` (lines 156-160, 219-220); the cosine image mask ratio is computed from `(step+1)/text_steps` not from the image step index (line 318); image logits use cond + w (cond − uncond), `cfg_img` 4.0 default in the function and README; `cfg_scale` (lines 286-287: guidance of the image logits against a text-dropped branch, not guidance of text tokens, which use the conditional logits only) is 0 in the README example and 2.5 default in `inference.py`. README example: text_steps 128, timesteps 64.
- Evidence rows: sec 4 (B1-B3, C1, D1-D2).
- Limitations stated [S App J]: limited base data; "our current sampling and training strategies are not yet fully unified across modalities".
- Internal inconsistencies noted [I]: Sec 4.3 text cites "Table 4" for parallel against sequential (it is Table 3) and "Table 10" for reweighting (it is Table 9). Table 3 sequential output align 48.9 equals the Show-o* (tuned) value in Table 2; Table 3 parallel row equals Table 2 "w/o Para-RL"; Table 10 parallel row equals the post-ParaRL model, so Tables 3 and 10 compare at different training stages and the sequential rows (48.9 and 54.1) are not reconciled.

### 2.5 FUDOKI (2505.20147v3)
- Channel [S Sec 3.1, Eq. 4-5]: not masking. Metric-induced probability path p_t(x | x1) = softmax(−β_t d(x, x1)) with d the L2 distance between normalised token embeddings, kinetic-optimal velocity. Source at t = 0 uniform. β_t = c (t/(1−t))^a with c = 3, a = 0.9 (Sec 4.1).
- Architecture [S Sec 3.2]: Janus-1.5B backbone, full attention, logit shift by one position, no time embedding. Text vocabulary 102,400; generation images by the LlamaGen quantiser, vocabulary 16,384 (576 tokens, 384 px); understanding images enter as SigLIP features (input only). Two output heads, text and image, chosen by the target modality.
- Training and use [S Sec 3.3]: one target modality per example (image for T2I, text for I2T), the other is the clean condition. So no joint text-image generation. 13M examples, about 43,000 GPU hours.
- Sampling [S Sec 3.4, 4.1]: Euler CTMC solver, 32 steps default; each position changes with probability 1 − exp(−hλ), so tokens can be revised at every step (Fig. 3). Response length 500 text tokens fixed in advance (App F).
- Step evidence [S Sec 4.3, Fig. 5 right, figure only]: GenEval quality improves and stabilises, speed falls, as steps rise. Image only.
- Guidance: not mentioned in the cached text (search for "classifier", "guidance", "CFG" returned nothing). Inference scaling by judge-model best-of-n (Sec 4.2) is an E_sel mechanism.

### 2.6 Lumina-DiMOO (2510.06308v1)
- Architecture [S Sec 3.2]: LLaDA-Base unchanged; vocabulary = 126,345 text tokens + 8,192 aMUSEd-VQ image tokens + specials (`<IMAGE>`, `<end-of-line>`, `<uncondition>` for CFG). One masked CE over text and image positions at a random mask ratio (Eq. 1-3). Initialisation from LLaDA is necessary: from scratch fails (Sec 7.2, qualitative).
- Sampling [S Sec 3.3.1, 7.1]: image: one block, probabilities restricted to the image-token subset (K' = 8,192) before confidence is computed, cosine schedule, 64 steps for 1,024 px; text (understanding): semi-AR blocks, block 256, 128 steps, early stop on `</answer>`. Generation is one modality per call.
- Acceleration [S Sec 3.3.2, 7.1]: max-logit cache reuses K, V and logits of high-confidence tokens, lossy; speed-up 2.05x (T2I) and 1.87x (understanding), GPU memory 38.9 to 45.9 GB at 1,024 px. This is E_approx by construction. The paper warns that cutting steps too far "will introduce compounding decoding error" (Sec 3.3.2).
- Self-GRPO [S Sec 4.4]: samples image trajectories and answers questions about them; rewards = number of correct answers; log-likelihoods at selected timesteps only.
- Guidance scale and step sweeps: not found in the cached v1 text.

### 2.7 Transfusion (2408.11039v1), hybrid baseline 1
- Architecture [S Sec 3]: one transformer for discrete text tokens and continuous VAE latent patches; text embeddings and LM head, image patch encoder/decoder linear or U-Net; attention causal over the sequence and bidirectional within each image.
- Objective [S Eq. 4]: L = L_LM + λ L_DDPM with λ = 5 (Sec 4.1). Image diffusion noise added before patchification; downstream tokens condition on the noised image in training (Sec 3).
- Inference [S Sec 3, 4.1]: LM mode token by token, BOI switches to diffusion mode, 250 steps (trained on 1,000 timesteps), then EOI. CFG 5 in the controlled comparison, 3 in ablations, tuned per benchmark at large scale.
- Ordering [S Sec 4.3.4]: 80 percent caption-first (image conditions on caption), 20 percent image-first. Limiting noise to t ≤ 500 when the image precedes its caption: CIDEr 25.4 to 29.4 (0.76B) and 33.7 to 35.2 (7B), other metrics within 1 percent (Table 8). This is a modality-ordering ablation, but of training noise, not sampling.
- Text and image are never in the same commit step; across modalities it is strictly sequential.

### 2.8 BAGEL (2505.14683v3), hybrid baseline 2 (named by Lumina-DiMOO, MMaDA-Parallel, LaViDa-O, Dynin-Omni)
- Architecture [S Sec 2.1-2.4]: Qwen2.5-initialised Mixture-of-Transformers (two experts, understanding and generation, shared self-attention at every layer); text by next-token prediction, visual generation by rectified flow on FLUX-VAE latents (16 channels, 8x downsample, 2x2 patches), SigLIP2 ViT tokens for understanding; generalised causal attention (causal text, bidirectional per image split; clean VAE and ViT tokens kept as context, diffusion forcing across images).
- Guidance [S Sec 2.3]: CFG by dropping text, ViT and clean-VAE tokens with probabilities 0.1, 0.5, 0.1. Scale and step count not read.
- Thinking, text before image [S Sec 7.4]: WISE 0.70 with chain of thought, +0.18 over without; IntelligentBench edit 44.9 to 55.3; RISEBench 6.1 to 11.9; KRIS-Bench 56.21 to 60.18. Reasoning text is generated first, then the image.
- Contrasting reading [S MMaDA-Parallel Table 1]: re-run by the MMaDA-Parallel authors on ParaBench editing, Bagel's thinking lowers the score in Causal (−2.9) and Spatial (−4.8), the two categories with the lowest text quality and output alignment (46.2, 45.2). Five categories, no interval; attributes the loss to sequential error propagation.

### 2.9 Show-o2 (2506.15564v3), read for design and the CFG-by-steps grid only
- Architecture [S Sec 3.1]: 3D causal VAE latents, dual-path unified visual representation (semantic layers from SigLIP plus low-level projector), a language head (autoregressive text) and a flow head (velocity, flow matching), omni-attention. L = α L_NTP + L_FM (Eq. 4); x_t = t x_1 + (1 − t) x_0 (Eq. 1).
- Table 11 [S Sec 4.5, 1.5B]: CFG 2.5 / 5 / 7.5 / 10 at 50 steps: GenEval 0.65 / 0.71 / 0.71 / 0.71, DPG 81.6 / 83.9 / 84.8 / 85.0. At CFG 7.5: steps 25 / 50 / 100: GenEval 0.71 / 0.71 / 0.73, DPG 84.6 / 84.8 / 84.7. Image only, no variance. The only step sweep at fixed guidance among these papers.

### 2.10 LaViDa-O (2509.19244v3), targeted
- Planning [S Sec 3, A.7, B.5, Table 13]: before the image, the model generates a layout as (object, bounding box) pairs, then the image, via modality-aware masking (A.3, not read). GenEval overall 0.77 to 0.85; position 0.65 to 0.84, two-object 0.85 to 0.94, attribution 0.58 to 0.68. Reflection (generate, self-critique, regenerate): overall 0.89 (Table 13); by rounds N (Table 16): N = 1 (planning only) 0.848, N = 2 0.864, N = 4 0.875, N = 8 0.882, N = 12 0.890, N = 16 0.886, N = 20 0.886. In the main-text table the planning rows are 8B+2.4B against 4B+2.4B for the baseline row, so model size also differs there; Table 13 itself does not state sizes.
- This is layout-first, text-form commitment before image tokens: a modality-ordered schedule, and an output-level revision loop.

## 3. Design-space table (framework notation)

Columns: C1 channel per modality (text | image); C2 reveal law and attention; C3 heads and vocabulary; C4 per-modality steps, schedule, joint or sequential; C5 revision. "Same pass" means text and image tokens are both committed within one forward pass.

| Model | C1 text | C1 image | C2 / attention | C3 | C4 steps and schedule; commitment across modalities | C5 and guidance |
|---|---|---|---|---|---|---|
| Show-o | AR, Phi-1.5 vocabulary | erasure on 8,192-code LFQ tokens | text causal prefix; image mask ratio per time step; full attn within image, image sees preceding text | one shared vocabulary (text + 8,192), one head | text 1 token/pass AR; image T = 5/25/50 qualitative, MaskGIT confidence; **sequential** (text then image or image then text; interleaved over segments) | none; guidance w = 3, 5 (Eq. 12) |
| UniDisc | erasure, Llama BPE | erasure on LFQ tokens (256 or 1,024) | independent Bernoulli(alpha_t) over all positions, one t shared by both modalities; one modality fully masked with prob 0.1; full bidirectional | one joint-vocabulary head; invalid-token mask | joint pool ranking, 24 steps in guidance tests, NFE sweep to 384; **same pass, joint** | none; modality-dropout CFG, w = 1.5 |
| MMaDA | erasure (LLaDA tokenizer) | erasure on 8,192-code MAGVIT-v2 (1,024 tokens) | one t; 1/t weight; prompt clean in SFT | one shared head | text semi-AR blocks of 64, 512 steps for 1,024 tokens; image 50 steps cosine, one block; **separate calls** | low-confidence remasking only; image CFG 3.5 |
| MMaDA-Parallel | erasure | erasure on MAGVIT-v2 (M) or aMUSEd-VQ (A) | input clean, output noised with one beta_t; per-modality loss weights (1/t text, 1 image) | one shared head | dual schedulers: text linear semi-AR (128 steps), image cosine (30 steps in paper, 64 in README); paper: **same pass, joint at every step**; code (-A): text-only first quarter, then joint | confidence remasking; image CFG 3.5 (paper), 4.0 (code) |
| FUDOKI | metric-path DFM (embedding-distance softmax), source uniform, vocab 102,400 | same path on 16,384-code LlamaGen tokens | path with shared t; one generated modality, other clean; full attention, logit shift, no time embedding | **two heads** (text, image) chosen by target | Euler CTMC, 32 steps; **one modality per call** | implicit revision at every step; no CFG found |
| Lumina-DiMOO | erasure (126,345 LLaDA tokens) | erasure on 8,192 aMUSEd-VQ tokens | random mask ratio over text and image positions; bidirectional | one head; **sampling restricted to image subset** for image generation | image 64 steps cosine one block; text blocks of 256, 128 steps; **separate calls** | top-k remasking; max-logit cache (E_approx); `<uncondition>` CFG, scale not found |
| Transfusion | AR LM | **Gaussian** DDPM on continuous VAE patches | per image one noise level; causal over elements, bidirectional per image; 80/20 caption-first | text LM head; image linear or U-Net decoder (noise prediction) | text token by token, then 250 diffusion steps for the image; **sequential, no joint commit** | implicit revision of image (Gaussian); CFG 5 / 3 |
| BAGEL | AR (Qwen2.5) | **rectified flow** on FLUX-VAE latents (+ SigLIP2 for understanding) | generalised causal attention; independent noise per image (diffusion forcing) | MoT: two experts; text head, velocity regression | text (thinking) then image; **sequential** | implicit revision of image; CFG by token dropout |
| Show-o2 | AR | **flow matching** on 3D-VAE latents, dual-path features | omni-attention | language head + flow head | text AR then flow steps 25/50/100; **sequential** | implicit; CFG 2.5-10 |

Row counts by commitment: joint in the same pass: UniDisc (all steps) and MMaDA-Parallel (paper; code after a text head start); separate or sequential: all others. Interleaved across segments: Show-o and Show-o2 (mixed-modality generation), BAGEL, LaViDa-O (planning, reflection).

## 4. P5 evidence table and verdict

Rows are every table, figure or ablation in the papers read that varies steps for joint text-image generation (a), joint against sequential or ordered generation (b), which modality is unmasked first (c), or cross-modal attention or dependence during sampling (d). "Verdict" is relative to P5 (joint commitment costs where cross-modal dependence is high; early steps; layout and object words).

| # | Paper, location | Kind | Setup and what was held fixed | Numbers | Verdict on P5 |
|---|---|---|---|---|---|
| A1 | UniDisc Fig. 5(c), 5(d), Sec 4.2 | (a) | Joint 384-token sequence (256 image + 128 text), a single NFE budget for both modalities, three samplers; 115M-340M model, DataComp1B; figure values read by eye | image FID about 20 for NFE 32 to 384, about 70-150 at 1-2; text GPT-2 PPL (MaskGIT+nucleus) about 66, 23, 19, 16 at NFE 8, 32, 64, 384 | cannot speak: marginal metrics per modality, k varies for both modalities together, nothing cross-modal measured. Suggestive only that the high-k penalty differs by modality, which points to within-modality dependence |
| A2 | MMaDA Table 6, Sec 5.4 | (a) | Each modality in its own call | image CLIP 32.8/32.0/31.7 at 1,024/50/15 steps; text MMLU 66.9/66.3/65.7 at 1,024/512/256 | cannot speak: not joint |
| A3 | Show-o2 Table 11 | (a) | Image only, CFG 7.5, 1.5B | GenEval 0.71/0.71/0.73 at 25/50/100 steps | cannot speak: single modality |
| A4 | FUDOKI Fig. 5 (right), Show-o Fig. 11 | (a) | Image only | figure only / qualitative | cannot speak |
| B1 | MMaDA-Parallel Table 3, Sec 4.3 RQ1 | (b) | Parallel (the main model, pre-ParaRL) against a sequential baseline "that generates text before images", trained with noise on one modality at a time; ParaBench, GPT-4.1 judge, single run | Text Align 70.6 vs 70.4, Image Align 56.1 vs 58.2, Output Align 48.9 vs 51.5 (sequential vs parallel) | does not support the cost claim on this metric (parallel is not worse); cannot test P5: the sequential arm differs in training and in conditioning, so the net of benefit and cost is measured. Direction opposes a large cross-modal cost |
| B2 | MMaDA-Parallel Table 8 and Table 7 (App B.2) | (b) | "MMaDA (Sequential)" against MMaDA-Parallel, image-only benchmarks | GenEval overall 0.68 vs 0.71 (position 0.34 vs 0.40, colour-attribute 0.37 vs 0.47); RISEBench overall 5.5 vs 5.75 percent | same as B1 (image quality improves with joint training and decoding); no interval; sequential model differs in training |
| B3 | MMaDA-Parallel Table 10, App I | (b),(c) | Decoding strategy at the final (post-ParaRL) model: sequential text then image; semi-parallel (reasoning text for the first half of timesteps, then interleaved); fully parallel | Text/Image/Output Align: 64.2/56.5/54.1; 68.3/60.7/57.5; 71.0/63.2/59.8 | the graded ordering (more text-first means lower alignment) is the closest thing to a test of "which modality first" and goes against text-first. Not matched in forward passes (not stated), not clear whether the same weights were used for all three, single run. The authors' explanation, quoted as theirs, is that early image steps establish coarse layouts and "excessive initial text may even bias attention" (unmeasured) |
| B4 | MMaDA-Parallel Table 1, Sec 3.1 (Bagel re-run) | (b),(c) | Bagel with and without thinking on ParaBench editing, five categories | delta with thinking: Temporal +3.3, General +2.5, Causal −2.9, Knowledge +2.3, Spatial −4.8; output align lowest (46.2, 45.2) in the two negatives | sequential text-first can hurt when the text is poor; not a P5 test (different model, no joint arm) |
| B5 | BAGEL Sec 7.4 | (c) | Text-first thinking against none | WISE +0.18 (to 0.70); KRIS 56.21 to 60.18 | text-first helps on knowledge tasks; cannot test P5 (no joint arm) |
| B6 | LaViDa-O Table 13, 16 (App B.5) | (c) | Layout (bbox text) first, then image, against direct image; GenEval | position 0.65 to 0.84; overall 0.77 to 0.85; reflection rounds N = 1..20 0.848 to 0.890 | layout-first helps the layout-critical categories. Consistent with layout dependence being large and early and with committing it separately, but extra forward passes and trained planner confound; baseline is image-only, not joint. Cannot isolate P5 |
| B7 | Transfusion Table 8 (Sec 4.3.4) | (c) | Image before caption (20 percent of data), noise capped at t ≤ 500 | CIDEr 25.4 to 29.4 (0.76B) | ordering in training, not in sampling; cannot speak |
| B8 | UniDisc App B.4 | (b) | Joint inpainting against an AR model fine-tuned for it | figure only | not read as numbers; cannot speak |
| C1 | MMaDA-Parallel Sec 3.3, Fig. 5 | (d) | One example, "change the blue shirt to a vibrant rainbow color": the colour words appear in text and the corresponding image regions emerge between steps 4/11 and 5/11 | qualitative | consistent with co-emergence of cross-modal dependent tokens at the same step; a single hand-picked case; the confidence rule commits peaked tokens, whose total correlation is small (sec 5, toy C), so co-emergence does not by itself show a cost |
| C2 | MMaDA-Parallel Sec 3.3 (ParaRL), Tables 4, 5 | (d) | CLIP text-image alignment reward on intermediate trajectory states; output-level against trajectory-level RL | Output Align 53.6 (output RL) vs 59.8 (ParaRL); s = 2/3/4 sampled steps: 53.6/59.8/58.7 | shows intermediate states carry usable alignment signal (the authors say partially decoded text is semantically meaningful). The alignment is used as a reward, not reported as a function of step. A training-side result |
| C3 | UniDisc App I Fig. 24-25, Sec 4.1 | (d) | Conditional against unconditional logits (other modality masked) by fraction decoded; CFG applied only on selected steps (24 total) | L2 distance decreases with decoding; CLIP 0.301 (steps 1-3), 0.293 (12-14), 0.283 (22-24), 0.312 (all) | supports the premise that cross-modal conditioning matters most early; no no-guidance row in the table, and guidance changes marginals, so it is not a cost-of-co-commit measurement |
| C4 | UniDisc App G.2, Fig. 21-22 | (d) | Segmentation of the final image against decoding time | "generates all concepts at once", positionally invariant; figure only | descriptive; says nothing about cross-modal timing |
| C5 | MMaDA-Parallel code (-A) lines 156-160, 219-220 | (c) E3 | Released sampler schedule | image steps from text_steps//4 | the released "parallel" sampler includes a text head start (a partial modality ordering); shows the authors' own default is not fully joint |
| D1 | UniDisc Sec 4.1-4.2 (no-CFG reference) | context | AR and UniDisc similar at w = 0, gap opens with guidance | Fig. 4, values not read | guidance, not commitment, is the stated source of the UniDisc advantage |

Separate question: does any paper measure or discuss cross-modal dependence per step? [S] Discussed: MMaDA-Parallel Sec 3.3 (concept emergence, one example), App I (early image steps "establish coarse scene layouts", unmeasured), UniDisc Fig. 24-25 and App G.2 (CFG distance, concept timing). Measured as a per-step cross-modal quantity: none found. Attention maps over time: none found in the sections read.

### Toy: cross-modal total correlation in the budget (joint against sequential commitment)

Command (from `research/review/dossier/`): `python primer-multimodal-check.py` (numpy; about 2 s; seed 0). Output, abbreviated:

```
A  chain rule TC = TC_text + TC_image + I(text;image | R): max abs error over 800 cases = 1.33e-15
B  four binary tokens t1,t2 (text), i1,i2 (image); t1 and i1 share a latent L with flip noise e_c; t2 = t1^noise(e_t); i2 = i1^noise(e_i);
   all 6 ordered partitions into two steps of two tokens (k = 2, NFE = 2 for all); E_fact in nats, KL(q||p) by enumeration
   e_c=0.05 e_t=0.4 e_i=0.4 (weak within-modality coupling):
     {t1,i2}|{t2,i1} 0.0132 (all cross)   {i1,i2}|{t1,t2} 0.0271 (text 0.0070, image 0.0201)   {t2,i2}|{t1,i1} 0.3539   {t1,i1}|{t2,i2} 0.3792 (all cross)
   e_c=0.05 e_t=0.1 e_i=0.1 (strong within-modality coupling):
     {t2,i2}|{t1,i1} 0.2057   {t1,i2}|{t2,i1} 0.2279   {t1,i1}|{t2,i2} 0.3792   {t1,t2}|{i1,i2} 0.5083 (text 0.3681, image 0.1402, cross 0)
   e_c=0.3 e_t=0.1 e_i=0.1 (weak layout coupling, strong within-modality coupling):
     {t2,i2}|{t1,i1} 0.0069   {t1,i1}|{t2,i2} 0.0129   {t1,t2}|{i1,i2} 0.7279 (cross 0)
B  max |E_fact - KL| and |E_fact - (text+image+cross)| over all rows = 6.59e-16
C  TC <= sum H_i - max H_i on 2000 random sets: violations = 0, smallest slack = 7.187e-02
```

What it shows [V, toy only]. (i) The identity: sampling-path KL equals E_fact, and E_fact is exactly within-text plus within-image plus cross. (ii) With a strong shared layout latent, committing the layout pair {t1, i1} in one step costs 0.379 nats, all of it cross-modal, against 0.013 to 0.23 for schedules that split that pair: the "joint commit costs where cross-modal dependence is high" statement is true by construction. (iii) The modality-sequential schedule {t1,t2}|{i1,i2} has zero cross term but pays within-modality total correlation, 0.508 and 0.728 in the strong-coupling rows, and loses to schedules that interleave modalities (0.206 to 0.228; 0.007). At equal k, "separate the modalities" is therefore not the right policy; "separate the dependent pairs" is. (iv) C bounds total correlation by the marginal entropies, so a confidence rule that commits peaked tokens commits low-TC sets in either modality; co-emergence of a colour word and its image region (C1) is expected if both marginals are peaked and says nothing about cost. This toy has binary tokens and an exact predictor; it demonstrates accounting, not behaviour of any model.

### Verdict on P5

- Premise (cross-modal dependence is front-loaded, layout and object words): weak, indirect support (C3, B6, C1, authors' unmeasured statement in B3). Evidence level E2, 3 sources, all single-run figures or tables without variance.
- Consequence (parallel commitment of the two modalities costs where that dependence is high): **untested**. The only joint-against-sequential contrast (B1-B3) measures the net of benefit and cost; it points toward joint decoding being at least as good on alignment, which does not contradict the identity but shows the cost is not the dominant term in that setting, or is offset by the benefit of bidirectional context.
- No paper contradicts P5 and no paper supports it directly. "Not found" stands for the quantity that P5 is about.

## 5. Answers to Q2, Q4, Q5

### Q2. Do the unified models fit C1-C5 with "no new machinery"?

They fit the five-choice table. They do not fit the sentence "no new machinery" in framework-v0 sec 3. Places where something extra is needed.

1. **Classifier-free guidance by modality dropout** [S UniDisc Alg. 1 lines 11-15 and Sec 3.3; MMaDA-Parallel App H; BAGEL Sec 2.3; Show-o Eq. 12 and Sec 3.2]. Guidance replaces p_θ by a sharpened distribution p_w ∝ p_cond^(1+w) / p_uncond^w. The budget identity holds with p_w in place of p_θ, but then E_learn is measured against a target that was deliberately changed, and the output entropy falls. It is E_sel-like (an entropy-lowering distortion of the marginals) but acts on marginals before commitment, not on which sampled values are kept. It also edits the cross-modal channel itself: the unconditional branch removes the other modality. Needs its own row (sec 6 edit 8).
2. **Per-modality loss weights.** UniDisc floors the 1/t-type weight at 5 (Sec 3.3); MMaDA-Parallel uses w_text = 1/t and w_img = 1 (Eq. 2; Table 9: both 1/t 56.3, both 1 57.0, default 59.8 output align); Transfusion λ = 5 (Eq. 4); Show-o and Show-o2 α. Once the weights are chosen for training stability the objective is no longer the ELBO the framework's C2 and C3 identity refers to (same remark as the clipped schedules in primer-gaussian sec 0 item 7). It is a lever on E_learn.
3. **Joint law over per-modality noise levels.** Shared t across modalities (UniDisc Alg. 1 line 9; MMaDA Eq. 1); input clean, output noised (MMaDA Eq. 2, MMaDA-Parallel Eq. 1); one modality fully masked (UniDisc Alg. 1); independent noise per image (BAGEL diffusion forcing); noise capped at t ≤ 500 when the image precedes its caption (Transfusion Sec 4.3.4). C2 needs to read "joint law over (reveal sets of each modality)", not a product of per-modality laws.
4. **Mixed discrete and continuous channels** (Transfusion, BAGEL, Show-o2). The image part is Gaussian or flow with a velocity or noise head; there is no committed set A_n for it, every image position updates at every step, and no E_fact in the sense of sec 2 for that part (it is the per-step TC(z_s | z_t) of the Gaussian chapter plus the final decoder). Text is committed at k = 1 before the image starts, so the cross-modal step-level term is zero by construction; the image conditions on clean text, the text never conditions on a partly denoised image except across interleaved segments. The cross-modal commitment term of P5 exists only among the all-discrete models (UniDisc, MMaDA-Parallel) and, for a different reason, FUDOKI if it were run jointly (it is not).
5. **Different schedulers per modality inside one pass** (MMaDA-Parallel text linear semi-AR, image cosine; MMaDA and Lumina-DiMOO use them in separate calls). Fits C4, but then k_n = k_n^T + k_n^I and the budget has the three-way split of sec 1 [V].
6. **Vocabulary masking and separate heads** (FUDOKI two heads; Lumina-DiMOO restricts probabilities to the 8,192 image codes before ranking; UniDisc −inf for invalid tokens, small effect, Table 3). Fits C3 as a support constraint; changes the confidence scale used by the ranking [I].
7. **Output-level revision and planning** (LaViDa-O planning and reflection; Self-GRPO). Revision at the level of whole samples: spend further forward passes to repair a finished output (Table 16 plateau near N = 12 at 0.890). A new lever row, distinct from token-level C5.
8. **Caching** (Lumina-DiMOO max-logit cache): standard E_approx.
9. **Metric-induced paths with a logit shift** (FUDOKI): covered by the generalisation in primer-gaussian sec 5 edits 5 and 8.

### Q4. Does guidance enter the budget as E_sel? Where is it set, and are step sweeps at fixed guidance?

Short answer: it enters as an E_sel-like term (marginal sharpening), and it needs its own row because it also modifies the cross-modal conditioning. Table of where each paper sets it.

| Paper | Guidance setting [S] | Step sweep at fixed guidance? |
|---|---|---|
| Show-o | w = 3, 5 vs none, qualitative (App I, Fig. 11); Eq. 12 | qualitative steps 5/25/50; guidance for that panel not stated |
| UniDisc | w = 1.5 (UniDisc), 0.5 (AR) (App I); Fig. 4 sweeps w | NFE sweep (Fig. 5) guidance not stated in text; CFG-on-selected-steps test at 24 steps (Fig. 25) |
| MMaDA | image 3.5 (Sec 3) | Table 6 steps 1,024/50/15, guidance not stated for the sweep |
| MMaDA-Parallel | image 3.5, text 0 (App H); code: image 4.0 | no sampling-step sweep reported |
| FUDOKI | none found | Fig. 5 right, image only, figure |
| Lumina-DiMOO | `<uncondition>` token (Table 1); scale not found in v1 text | no |
| Transfusion | 5 controlled, 3 ablations, tuned per benchmark (Sec 4.1) | steps fixed at 250 |
| BAGEL | drop probabilities 0.1/0.5/0.1 (Sec 2.3); scale not read | not read |
| Show-o2 | Table 11 grid | yes: CFG 7.5 with steps 25/50/100 (0.71/0.71/0.73 GenEval) |

Only Show-o2 reports a step sweep at fixed guidance, and only for image quality. Consequence for P1 and P2 (framework sec 4): step sweeps in these papers confound E_fact with guidance unless the scale is stated; UniDisc's finding that guidance matters on steps 1-3 and barely on 22-24 (Fig. 25) says guidance is itself step-dependent, so a step sweep that moves the number of early steps also moves how much guidance is applied.

### Q5. Cheapest test of P5 on a frozen open checkpoint (inference only, 12 GB). Not run.

**Checkpoint.** `aswerdlow/unidisc_interleaved` (Hugging Face; arXiv 2503.20853; GitHub alexanderswerdlow/unidisc). File `unidisc_interleaved.pt` 5.63 GB plus `vq_ds16_t2i.pt` 0.29 GB; 1.4B-parameter model per the paper (Sec 4.4), so the file is consistent with fp32 weights (about 2.8 GB in bf16, by my arithmetic, not checked). **Licence: none stated** in the HF API metadata or the model-card text, and the GitHub API license field is null (E1: cards and API only; no weights or code downloaded, nothing run). Fits 12 GB for inference by my estimate (unverified); the 384-token or 1,024-token sequence is small.

Plan B, heavier: `tyfeld/MMaDA-Parallel-M` (HF tag license:mit, 8.08B parameters, four safetensors shards 4.93 + 4.93 + 5.00 + 1.30 GB, about 16 GB; does not fit 12 GB without 8-bit or 4-bit loading, untested). Its released sampler (-A shown) already exposes `text_steps` and `timesteps`, so modality ordering is a few lines. Use as a cross-check only.

**Why UniDisc.** All-discrete, absorbing mask, one shared t for both modalities in training and joint generation of text and image from nothing is native (Sec 3.4, Alg. 2), so cross-modal dependence is maximal and the commitment schedule is a free sampler choice.

**Intervention.** Joint unconditional generation of a (caption, image) pair from the all-mask state, fixed total number of forward passes N and fixed total tokens per pass (L_T + L_I)/N, five arms:
- J joint: one global confidence ranking over text and image tokens (UniDisc default, Alg. 2);
- T text first: first N/2 passes commit text only (same k), then image only conditioned on the clean text;
- I image first: the reverse;
- Alt alternate: odd passes text, even passes image (interleaved, each modality at the same overall k);
- R joint with random sets (Alg. 2 DDPM-style) as a control for confidence selection.
N in {16, 32, 64, 128}; guidance off (w = 0) to keep E_sel and cross-modal conditioning out of it; temperature and nucleus fixed identically across arms.

**Primary metric.** Paired per-sample text-image consistency, CLIPScore (or an image-text-matching score) between the generated caption and the generated image, same random seeds across arms, n = 500 pairs per cell, paired bootstrap interval on the difference J − T and J − Alt. Secondary: image FID against a held-out DataComp1B subset, text GPT-2 perplexity, and per-modality token entropy of each arm (a drop in entropy for an arm marks E_sel, framework P2 corrected form). Mechanism probe (optional, one extra pass per step in arm J): estimate X_n by committing the image set sampled from its marginals, re-running the pass, and taking the mean KL from the text marginals before to after; averaged over samples this estimates I(text set; image set | z_n) up to the usual conditional-independence-of-draws error. Plot X_n by step.

**Falsifier (to be written into a prediction file before running).** P5b is falsified if, for every N in the set, the lower end of the paired interval of J − min(T, I, Alt) on consistency lies above a pre-registered margin (about 1 CLIPScore point) of zero, i.e. joint commitment is not worse than the best modality-separated arm at matched passes. P5a is falsified if the probe's X_n is flat or rises with step (no early concentration) across 500 samples.

**Risks to read before spending GPU.** (1) Arms T and I put the model in states (one modality fully clean, the other fully masked) that appear in training only through the 10 percent modality-drop in Alg. 1, so a loss for T or I is confounded with off-support E_learn; arm Alt keeps both modalities partly revealed and is the control for that. (2) The cross-modal term and the within-modality terms trade off at fixed k (toy rows), so a win for Alt over J is not a win for "separate the modalities". (3) CLIP-type consistency is a coarse metric and can be dominated by the image. Estimated 6 to 10 GPU-hours for four N values by five arms by 500 pairs at 1.4B parameters; an estimate, not measured.

## 6. Required edits to framework-v0 (not applied)

Numbered; source locations in brackets.

1. Preamble, "Still unchecked: ... the unified multimodal models". Replace by: checked against ten primary papers on 2026-10-14 at sections-read level (E2-) and one released sampler (E3); Muddit, LaViDa, Dynin-Omni not read. [this report, coverage]
2. Sec 1, C1 (instances row): add "per-modality C1 may differ; continuous image latents with Gaussian or flow channel (Transfusion Sec 3, BAGEL Sec 2, Show-o2 Eq. 1) have no committed set; the multimodal commitment budget applies only to modalities with erasure-type channels (UniDisc, MMaDA, MMaDA-Parallel, Lumina-DiMOO)". [Transfusion Eq. 4; BAGEL Sec 2.1-2.2; Show-o2 Sec 3.1]
3. Sec 1, C2: replace "per-modality laws (unified multimodal models)" by "a joint law over the per-modality reveal sets: shared t for all positions (UniDisc Alg. 1 line 9; MMaDA Eq. 1), clean input / noised output (MMaDA Eq. 2; MMaDA-Parallel Eq. 1), whole-modality dropout (UniDisc Alg. 1 lines 11-15), independent per-image levels (BAGEL Sec 2.3), capped noise (Transfusion Sec 4.3.4)". Add "per-modality loss weights (MMaDA-Parallel Eq. 2, Table 9; UniDisc Sec 3.3; Transfusion Eq. 4) make the trained objective differ from the bound". [as cited]
4. Sec 1, C3: add "head layout: one shared vocabulary head (UniDisc, MMaDA, Show-o, Lumina-DiMOO), separate text and image heads (FUDOKI Sec 3.2), text LM head plus flow or noise head (Transfusion, BAGEL, Show-o2); modality-restricted sampling support (Lumina-DiMOO Sec 3.3.1, step 2; UniDisc Table 3)". [as cited]
5. Sec 1, C4: add the multimodal columns "k_n^T and k_n^I; whether both are nonzero in the same pass (joint) or separated (sequential, interleaved); schedulers per modality (MMaDA-Parallel Sec 3.2, App E; MMaDA Sec 3)". Add the design-space table of sec 3 here. Note the paper-code discrepancy for MMaDA-Parallel. [this report sec 3; parallel_generator.py lines 156-160, 219-220]
6. Sec 2, after the two-term identity: add "for sequences with two or more discrete modalities, TC(x^{A_n} | z_n) = TC_text + TC_image + I(text part; image part | z_n), so E_fact = E_fact^T + E_fact^I + E_fact^X; E_fact^X is the sum over steps of the conditional mutual information of co-committed text and image tokens". Mark [V, toy]. Add: TC ≤ Σ_i H(x^i | z) − max_i H(x^i | z), so a confidence rule commits low-TC sets within or across modalities (toy C). [primer-multimodal-check.py A, B, C]
7. Sec 3, final paragraph ("no new machinery"): replace by "Unified multimodal models enter with four additions to the table: guidance, per-modality weights and schedules, continuous image channels in hybrids, and output-level revision (planning, reflection); E_fact gains the cross-modal term X_n only for co-committed tokens of two discrete modalities". [sec 5 Q2]
8. Sec 3, lever table: add rows. (a) "classifier-free guidance, including modality dropout: sharpens marginals (E_sel-like), also edits the cross-modal conditioning; pays diversity; step-dependent (UniDisc Fig. 25)". (b) "modality-ordered or planned schedules (text first, layout first): can lower E_fact^X; pay forward passes and within-modality TC (toy B); LaViDa-O Table 13, MMaDA-Parallel Table 10". (c) "output-level revision (reflection loops): repairs finished samples; plateau near 12 rounds in LaViDa-O Table 16". (d) "lossy cache (Lumina-DiMOO ML-Cache): E_approx". [as cited]
9. Sec 4, P5 wording. Replace by two statements. P5a: "In an all-discrete unified model with a joint reveal law, the per-step conditional mutual information between co-committed text and image tokens, X_n, is concentrated in early steps and on layout and object tokens, and is large next to the within-modality terms there." P5b: "At matched forward passes and matched tokens per pass, a schedule that separates dependent pairs (including across modalities) has lower E_fact than joint commitment by about E_fact^X; a modality-sequential schedule removes E_fact^X but pays within-modality total correlation and need not beat joint or alternating schedules." [toy B; sec 5 Q5]
10. Sec 4, status line for P5. Replace "open; no evidence found either way" by: "open. Premise (front-loaded cross-modal dependence): weak indirect support (UniDisc App I Fig. 24-25; LaViDa-O Table 13; MMaDA-Parallel Fig. 5, one example). Consequence (cost of co-commitment): untested; the only contrast (MMaDA-Parallel Tables 3, 10) favours joint decoding on alignment but is confounded by conditioning and training; the released MMaDA-Parallel-A sampler is not fully parallel. No paper measures a cross-modal quantity per step." [sec 4]
11. Sec 2, E_sel paragraph: add "a single confidence ranking over several modalities implicitly fixes k_n^T and k_n^I through the confidence scales of each modality (UniDisc Alg. 2); per-modality schedulers fix them explicitly (MMaDA-Parallel Sec 3.2). Either choice is a hidden policy variable in step sweeps." [I; UniDisc Alg. 2; MMaDA-Parallel Sec 3.2]

Also for sec 4 P1/P2 (not P5): step sweeps in these papers do not hold guidance fixed, except Show-o2 Table 11 (sec 5 Q4). Add this caveat to P1.

## 7. Gaps and limitations

Stated by the papers. UniDisc: AR is 13.2x more training-efficient in their IsoFLOP fit (Fig. 3, Sec 4.2); KV-cached AR has higher throughput at large batch (App J). MMaDA-Parallel: limited base data, sampling and training not fully unified across modalities (App J). FUDOKI: fixed length before sampling, weak on complex text rendering (App F). Lumina-DiMOO: ML-Cache raises memory (Sec 7.1). Show-o: failure cases in App K (not read).

Unstated, found here. (i) No paper reports a per-step cross-modal quantity, and the two papers that decode text and image jointly (UniDisc, MMaDA-Parallel) report no variance across seeds or samples for the relevant contrasts. (ii) The one joint-versus-sequential contrast changes training and conditioning together with the decoding order. (iii) The MMaDA-Parallel paper and released sampler differ on whether decoding is parallel from step 0; which one produced Tables 3 and 10 is unknown. (iv) UniDisc's NFE sweep gives one NFE budget to both modalities, so per-modality k is confounded with total k. (v) Judge-based metrics (GPT-4.1 in MMaDA-Parallel, GenEval detectors) were not checked for sensitivity. (vi) Guidance is stated for few step sweeps.

Not covered (see YAML coverage): Muddit, LaViDa, Dynin-Omni, most evaluation tables, UniDisc code, MMaDA-Parallel-M code, BAGEL steps and CFG values, UniDisc Fig. 4, 13, 24 values. Figure values from UniDisc Fig. 5 are read by eye and approximate. The synergy question was not touched, per the brief; the stage-2 summary (Muddit Table 4 joint training GenEval 61.6 against 59.3, CIDEr 59.9 against 60.1, VQAv2 68.2 against 69.1) is cited, not redone.

Provenance. Command (from `research/review/dossier/`): `python primer-multimodal-check.py`. Scratch files (generator source, model JSON, figures) are in the session scratchpad and not in the repo. New source copies: `research/sources/html/` and `research/sources/md/` in the main checkout for 2408.12528, 2408.11039, 2505.14683, 2506.15564 (fetched 2026-10-14) and md conversions of the cached html for the others.
