---
agent: paper-reader
date: 2026-10-14
brief: Design-space table of 47 models and samplers in the framework-v1 notation (C1 to C5, lever rows L1 to L14), with a misfit list and counts of value rules and step sweeps. First coverage test of framework-v1.
sources_examined:
  - research/review/framework-v1.md (sections 1 and 3)
  - research/review/dossier/primer-foundations.md (sections 0, 1.1-1.9)
  - research/review/dossier/primer-samplers.md (section 2)
  - research/review/dossier/primer-gaussian.md (sections 1, 2, 3)
  - research/review/dossier/primer-multimodal.md (sections 1, 2, 3)
  - research/review/corpus/awesome-dlms@194aa6bd.jsonl (ID verification)
  - arXiv:2305.08379 v2, 2502.13917 v2, 2210.08933 v3, 2510.22510 v3, 2608.10615 v2, 2508.15487 v1, 2410.17891 v3, 2506.20639 v2, 2508.02193 v1, 2505.22618 v3, 2410.08709 v4, 2410.01949 v2, 2412.10193 v3, 2505.16839 v4, 2505.23606 v5, 2604.00007 v1, 2501.00289 v2, 2505.16990 v3
coverage: >
  Rows M01 to M29 are copied into the new notation from the four primers and were NOT re-read here
  (their evidence level is whatever the primer recorded; the primer's own not-read lists apply, for
  example LLaDA experiments, Campbell experiments, LaViDa-O A.3). Rows M30 to M47 (18 papers) were
  read here at section level only: method and sampling sections, the experiment-setup paragraphs
  that state steps, temperature, top-p and guidance, and the step-sweep tables or paragraphs. Per
  paper the sections read are in the 'evidence' column of the CSV. NOT read: results tables other
  than step sweeps, proofs and most appendices, related work, released code (no E3 anywhere in this
  file), the Dream 7B blog, Dream-Coder 7B, LLaDA-V, LLaDA 1.5 (converted or cached but unread).
  Reading was by keyword search plus targeted line ranges, so a statement 'not stated' means not
  found in the ranges read, not proved absent from the paper. Lever codes L1 to L14 are my numbering
  of the rows of framework-v1 section 3 in table order; the assignment of each model to levers is my
  inference from the described mechanism, not a statement by any paper.
claims:
  - statement: All 47 models can be placed in C1 to C5 and the lever rows; 36 fit without any new cell value and 11 fit partly; none is a clear no.
    status: supported
    evidence: design-space-v1.csv column 'fits'; misfit list (a)
    level: E2
    confidence: 0.6
  - statement: Of the 40 models whose headline numbers are sampler outputs, 29 use at least one E_sel-type rule (argmax, low temperature, top-p or top-k, sample-then-filter, guidance, or sequence-level selection), 2 control it by an entropy-matched frontier, 3 use plain sampled values, 6 do not state the value rule in the parts read.
    status: supported
    evidence: section (b); CSV columns 'value-rule classes' and 'headline uses E_sel-type rule'
    level: E2
    confidence: 0.6
  - statement: Only 5 of those 29 report entropy or a diversity measure next to the headline number.
    status: supported
    evidence: section (b), CSV column 'entropy or diversity reported'
    level: E2
    confidence: 0.55
  - statement: Of 29 models with a step or NFE sweep in the parts read, 10 have the value rule shown as fixed across the sweep, 2 vary it on purpose, 1 holds guidance fixed without stating the value rule, 16 do not say. Among the 14 models that use guidance, one (Show-o2) reports a step sweep with guidance fixed.
    status: supported
    evidence: section (c)
    level: E2
    confidence: 0.55
  - statement: Five features are not expressible in framework-v1 without an extension - edit channels with length change, stochastic memory, graded evidence at non-committed positions, joint-over-set predictors, sequence-level selection.
    status: supported
    evidence: section (a) items 1 to 5 with source locations
    level: E2
    confidence: 0.65
competing_explanations:
  - The 'fits' count is high partly because the C1 to C5 vocabulary was written to be inclusive and most cells accept free text; a stricter test (every cell filled from the paper, identity applies as stated) gives a lower fit rate. See 'what the test could and could not fail'.
  - The 29 of 40 E_sel count may overstate the effect on results: for 9 of the 29 the only E_sel-type element is classifier-free guidance, which is also a conditioning device, not necessarily a sharpening of the output law.
unknowns:
  - Value rule of Dream 7B, Seed Diffusion, LaViDa, MMaDA (position confidence computed on what), Lumina-DiMOO scale, BAGEL steps and scale, DFM Table 2 temperature.
  - Whether the 16 'not stated' sweeps held guidance and value rule fixed.
  - Step sweeps in the 17 primer-sourced rows marked 'ns' (not examined, so absence is not evidence).
next_test:
  hypothesis: A frozen-checkpoint comparison of rank-then-sample against sample-then-filter and argmax at matched steps shows the entropy drop and quality gain that P2 attributes to E_sel.
  intervention: One open checkpoint (LLaDA 8B or Dream 7B quantised, or a small MDLM), same prompts, positions chosen from marginals, values sampled / argmax / sample-then-filter, steps fixed, entropy and MAUVE or task score recorded.
  primary_metric: output entropy and task score at fixed steps per value rule
  falsifier: Entropy and score are the same across value rules within seed noise.
  gpu_hours: 2 to 6 (inference only, 12 GB with a small model); not run
---

# Design-space table v1: coverage test of framework-v1

Date 2026-10-14. Tags as in the framework: [S] source fact, [I] inference, [H] hypothesis. No number
here comes from a `runs/` directory because nothing was run; every number is either a count over the
table below (script `design-space-v1-build/gen.py`) or a quotation of a number reported by a paper.

## 0. How to read the table

- One row per model, 47 rows. M01 to M29 are copied from the primers (source column names the primer
  section); M30 to M47 are new. The CSV has the same rows plus more columns (version read, corpus
  record, evidence level, evidence sections, and the five classification columns used in (b) and (c)).
- Empty or 'not stated' means not found in what was read. It is never a guess.
- **Lever codes** (framework-v1 section 3, table order, my numbering): L1 fewer tokens per step or
  adaptive k; L2 choose weakly dependent sets (position order); L3 joint draw inside the set; L4
  block-wise generation; L5 modality-ordered or planned schedules; L6 training; L7 self-conditioning,
  learned schedules, time warping; L8 distillation into few steps; L9 revision (token level); L10
  output-level revision; L11 value rules (argmax, temperature, sample-then-filter); L12 guidance
  including modality dropout; L13 exact compute reuse; L14 lossy compute reuse.
- **fits**: yes = every choice of the model can be written with the cell values framework-v1 already
  names and the factorisation identity (or its section 2.3 replacement) is stated for it as written;
  partly = at least one cell needs a new value or the identity does not apply as written (the
  'missing' column says which); no = the model cannot be placed. No model was a no.
- Value-rule classes in the CSV: A argmax or greedy; T temperature below 1 or a temperature sweep;
  P top-p or top-k; S sample-then-filter (confidence of the sampled value); G guidance (CFG,
  classifier or reward gradient); M sequence-level selection (MBR, best-of-n).

## 1. The table

| id | name | arXiv | family | C1 channel | C2 reveal law, weight | C3 predictor, head | C4 position rule | C4 value rule | C4 steps / tokens per step | C4 joint draw | C5 revision | memory m_n | levers | fits | missing | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M01 | D3PM | 2107.03006 | general discrete (Markov matrices) | General row-stochastic Q_t: uniform, absorbing, discretised Gaussian, embedding nearest-neighbour, MI schedule | Independent per token, shared t; absorbing case is a reweighted MLM loss (weight 1/t for beta_t=1/(T-t+1), Eq 12) | Logits of p~(x0/x_t); reverse kernel by mixture over x0 (Eq 4) | Independent per-token kernel (random sets); k-step kernels (Sec 3.3) | Sampled from reverse kernel | T=1000 (text) | no | None for absorbing; implicit for non-absorbing Q | none | L1 (k-step kernel), L6 | yes | Non-absorbing Q have no committed set (Sec 2.3 applies) | primer-foundations.md 1.1 (D3PM Sec 3, A.2, A.3) |
| M02 | Campbell et al. (CTMC) | 2205.14987 | general discrete (CTMC) | Factorised CTMC, R_t=beta(t)R_b: uniform, absorbing, Gaussian-like | Independent per dimension; CTMC ELBO (Eq 13) | Posterior p(x0/x) per dimension given whole state (Prop 1 Eq 11-12, Prop 3 Eq 17) | Exact CTMC (one dimension per step) or tau-leaping (Poisson counts, all changes applied at end of leap) | Sampled | not read (experiments not read) | no | Predictor-corrector R^c=R+R^ (Prop 4) | none | L1 (tau), L9 | yes |  | primer-foundations.md 1.2 (Sec 4.3, Prop 4) |
| M03 | SEDD | 2310.16834 | general discrete (CTMC, score) | Absorbing or uniform CTMC, token-factorised | Independent per token; weight from DWDSE (Eq 10) | Concrete score ratio s_theta (Eq 12); absorbing postprocess scaling e^{sigma-bar}-1 (App C.2) | Euler or Tweedie tau-leaping (Eq 17, 19): independent simultaneous token transitions | Sampled | not read | no | None (absorbing); implicit (uniform) | none | L1, L6 | yes | Ratio equals marginal times alpha/(1-alpha) only for erasure (RADD Thm 1); C3 already lists it | primer-foundations.md 1.3 (SEDD Sec 3, 4, App C.2) |
| M04 | MDLM | 2406.07524 | absorbing | Interpolating erasure q=Cat(alpha x+(1-alpha)pi), pi=mask (Eq 6-8) | Independent Bernoulli(alpha_t); weight alpha'/(1-alpha) (Eq 12) | x_theta, SUBS: zero mass on mask, carry-over; time input optional (Eq 9, Table 12) | Ancestral random sets from Eq 9; semi-AR blocks (Sec 4.2) | Sampled | T=5k in speed table (Table 10); headline is a likelihood bound | no | None | exact output cache when no token changed and no time input (Sec 4.1) | L1, L4, L13 | yes |  | primer-foundations.md 1.4 (MDLM Sec 3-4) |
| M05 | MD4 | 2406.04329 | absorbing | Erasure, alpha_t; GenMD4 state-dependent per-token schedule alpha_{t,i}=1-t^{w_i} | Independent; weight alpha'/(1-alpha) (Eq 4-5) | Mean parameterisation mu_theta=E[x0/x_t]; time-invariant allowed | Ancestral random sets (Alg 2); cosine grid for a linearly trained model (Eq 6) | Sampled | T=256 on ImageNet 64x64 (FID 70 to 17 as reported); headline likelihood | no | None | none | L1 (grid), L6 | yes | Per-token learned schedule is inside C1 only if alpha may differ by position | primer-foundations.md 1.5 (MD4 Sec 3, App D) |
| M06 | RADD | 2406.03736 | absorbing | Absorbing CTMC (Q=sigma Q^absorb) | Independent; four equivalent losses (lambda-DCE, t-DCE, any-order, ...) | Time-free conditional c_theta(x^UM) (Eq 3.3) | Tweedie tau-leaping / ancestral | Sampled | NFE n(1-(1-1/n)^l) with caching (Eq 3.4) | no | None | exact cache of c_theta when x_t unchanged | L13, L6 | yes |  | primer-foundations.md 1.6 (RADD Sec 3, Thm 1-2) |
| M07 | Zheng et al. (time-agnostic, first-hitting) | 2409.02908 | absorbing (sampler analysis) | Erasure | n-masked form, weight 1/n (Prop 3.1) | Time-free mu_theta (Prop 3.2) | First-hitting sampler: analytic hitting time, one uniformly chosen masked position per step (Alg 1) | Categorical via Gumbel-max; float32 truncation sharpens (Prop 5.2); 64-bit fix; temperature 0.8-1.0 swept (Fig 10) | 100-10000 (Fig 7) | no | None | none | L1, L11 (measured sharpening) | yes |  | primer-foundations.md 1.7; primer-samplers.md 2.10 |
| M08 | ARDM | 2110.02037 | absorbing (order-agnostic AR) | Erasure, one position per step (T=D) or parallel groups | Prefix of a uniformly random permutation; weight 1/(D-t+1) | Per-position categoricals from f(m*x), no causal mask (Alg 1-2) | Random permutation; k at once via state-independent DP partition (Eq 3-4) | Sampled | at most D calls; DP-chosen schedule for a budget | no | None | none | L1, L6 | yes |  | primer-foundations.md 1.8 (ARDM Sec 3, 3.1) |
| M09 | LLaDA | 2502.09992 | absorbing | Erasure, alpha_t=1-t | Independent Bernoulli; weight 1/t (Eq 3); SFT keeps prompt clean | Mask predictor, no causal mask, no time input (App A Eq 11) | Low-confidence remasking: predict all masked, keep floor(L(1-s)) most confident (Alg 5); random remasking baseline (Alg 4); semi-AR blocks for instruct | argmax in both Alg 4 and 5 (greedy) | 1 token per step in the sampler ablation (length=steps=256, Table 9) | no | None | none | L2, L11, L4 | yes | Experiments and step sweeps not read in the primer | primer-foundations.md 1.9; primer-samplers.md 2.9 (Alg 4-5, Table 9) |
| M10 | MaskGIT | 2202.04200 | sampler-only (image VQ tokens) | Erasure on VQ image tokens | Random mask ratio, mask-scheduling function gamma (cosine) | Per-position softmax over codebook | Predict all masked, sample a token each, keep most confident, remask rest by gamma | Sample then filter on the sampled token probability; randomised, temperature annealed in practice | 8-12 iterations optimum, cosine (Table 3, Fig 8) | no | None (kept tokens get confidence 1.0) | none | L11 (sample-then-filter), L1 | yes |  | primer-samplers.md 2.8 (MaskGIT Sec 3.2, 4.4) |
| M11 | ReMDM | 2503.00307 | sampler-only (remasking) | Erasure with remask posterior (sigma_t); same marginals as MDLM (Thm 3.1) | As MDLM | MDLM predictor | MDLM step plus corrector (Thm 4.1); sigma_t Bernoulli (state-independent) or confidence-weighted (ReMDM-conf) | Sampled, nucleus top-p 0.9 in text experiments | T=1024, 2048, 4096 (Table 1) | no | Remasking | none | L9, L11 (top-p) | yes |  | primer-samplers.md 2.7 (Thm 3.1, 4.1; Tables 1, 5) |
| M12 | EB-sampler | 2505.24857 | sampler-only (adaptive k) | Erasure (applied to LLaDA, Dream 7B) | As base model | Base model marginals | Sort by entropy; largest prefix with sum of entropies minus max entropy below gamma (Eq 2, 8, 9): adaptive k | argmax (zero temperature) in experiments; theory assumes sampled | NFE speed-up 2.05x-6.00x (Dream 7B MBPP, Table 1) | no | None | none | L1, L2 | yes |  | primer-samplers.md 2.5 (EB-sampler Sec 5, App A.1) |
| M13 | Diffusion-LM | 2205.14217 | Gaussian/embedding | VP Gaussian on learned embeddings (d=16/128), sqrt schedule, T=2000 | None; one shared t; control by classifier gradients (Sec 5.1) | x0 vector regression (MSE) plus softmax rounding head (Sec 4.2) | All positions updated every step; clamp to nearest embedding each step | argmax rounding (clamp each step, final argmax of rounding model) | 2000, or 200 for control (App C) | no (final rounding commits all L at once) | Implicit (x_{t-1} redrawn each step); no pinning | none | L11 (clamp), L12 (classifier gradient), L1 | yes | Needs the two-level C4 (G10) | primer-gaussian.md 3 table, 2.1 |
| M14 | CDCD | 2211.15089 | Gaussian/embedding | VE, sigma=t in [1,300], L2-normalised learned embeddings d=256, time-warped | Conditioning mask: prefix / random / 50-50; one t for noisy positions | Logits with CE; score interpolation Eq 6-8 | Deterministic Euler; all positions every step; no token drawn until the end | argmax of final extra call; score scaling, initial noise, logit truncation, CFG as knobs | 200 (as few as 50) | no (final rounding commits all L) | Implicit via ODE field; conditioning positions pinned | self-conditioning input (previous predicted-embedding sequence) | L7, L11, L12 | yes |  | primer-gaussian.md 3 table, 2.2 |
| M15 | Plaid | 2305.18619 | Gaussian/embedding | VE with learned sigma^2(t) incl. endpoints, learned embeddings d=16 | None; truncation for length | Logits; x_hat=W softmax(f); output prior; learned p(x/z0) | Ancestral, all positions every step | argmax p(x/z0) at end; score temperature 0.9 | T=4096 | no (final rounding) | Implicit; token guidance for control (not read) | self-conditioning (Sec 3.5) | L7, L11, L12 | yes |  | primer-gaussian.md 3 table, 2.3 |
| M16 | DFM (discrete flow matching) | 2407.15595 | flow (probability path) | Source p (mask or uniform), coupling, path of kappa-weighted deltas; Eq 10 adds uniform noise (erasure+uniform mixture) | Via coupling: U- or C-coupling, random-length prefix | Posterior w_hat, velocity affine in it (Eq 22-25); time-independent for mask source | Euler step per token independently (Eq 12, Alg 1) | Sampled; temperature Eq 34 and schedule Eq 36 available (setting for Table 2 not in primer) | NFE 256, 512, 1024 (Table 2) | no | Corrector u_bar=alpha u_hat-beta u_check (Eq 26), 1.7B models only | none | L1, L9 | yes |  | primer-gaussian.md 3 table, 2.4 |
| M17 | Duo | 2506.10892 | uniform | Uniform-state; Gaussian on one-hot with alpha=T(alpha~) per position | Positionwise independent, same alpha_t | x_theta in Delta^L posterior marginals (Eq 17-18) | USDM ancestral product over tokens; all positions revisable | Sampled; Greedy-Tail argmax in last step; DCD distillation | 8-1024 (distilled: 16 matches base at 1024; 8 with Greedy-Tail) | no | Continual token updates by construction (claim; not isolated from distillation or entropy) | none | L8, L9, L11 (Greedy-Tail) | yes |  | primer-gaussian.md 3 table, 2.5 |
| M18 | BD3-LM | 2503.09573 | block (semi-AR) | Erasure, linear schedule | Block prefix: clean prefix blocks, independent t_b per block, later blocks absent (Alg 1) | Block logits plus KV (Eq 7) | Block by block; first-hitting within block | Sampled; nucleus p=0.9; 64-bit Gumbel | T=5K per block, NFE at most block length (C.5) | no | None | exact cross-block KV cache; within-block output reuse | L4, L13 | yes | App B.5 tightness proof step flagged unjustified in primer | primer-gaussian.md 3 table, 2.6 |
| M19 | SSD-LM | 2210.17432 | Gaussian/embedding (logit simplex, block) | VP on almost-one-hot logits (+-K), noise scale K; network sees softmax | Random context length c, B-token noisy block, clean context | Logits, CE | Block-wise; all block positions every step | Projection each step: greedy argmax, top-p sample or multi-hot; final argmax | not in primer (TESS App B reports 10/100/1000) | no (final rounding) | Implicit within block; context pinned | none | L4, L11 | yes |  | primer-gaussian.md 3 table, 2.7 |
| M20 | Show-o | 2408.12528 | hybrid AR+diffusion (unified) | Text: AR (no channel); image: erasure on 8,192 LFQ codes | Text causal prefix; image mask ratio per time step; omni-attention | One shared vocabulary head (text + 8,192 image codes) | Text 1 token per pass AR; image MaskGIT confidence ranking, T steps | Sampled tokens ranked by own probability (sample-then-filter); CFG w=3 or 5 (App D Eq 12) | Image T=5/25/50, qualitative only (App I) | sequential across modalities | None for committed tokens | none | L11, L12, L5 (sequential) | yes |  | primer-multimodal.md 2.1, 3 table |
| M21 | UniDisc | 2503.20853 | unified multimodal (discrete) | Erasure on both modalities (Llama BPE; LFQ image tokens) | Independent Bernoulli over all positions, one t shared; whole-modality mask prob 0.1; weight floored by min-SNR (limit 5) | One joint-vocabulary head; invalid-token mask | One pool ranking text and image tokens together (Alg 2), or DDPM-style random sets | MaskGIT confidence with top-p and temperature; CFG w=1.5 (modality-dropout) | 24 in guidance tests; NFE sweep to 384 (Fig 5) | joint (same pass) | None | none | L11, L12, L5 | yes |  | primer-multimodal.md 2.2, 3 table |
| M22 | MMaDA | 2505.15809 | unified multimodal (discrete) | Erasure on LLaDA text tokens and 8,192-code MAGVIT-v2 | One t; weight 1/t; prompt clean in SFT | One shared head | Text semi-AR blocks of 64, low-confidence; image one block, cosine, low-confidence | Low-confidence remasking (value rule not stated); image CFG 3.5 | Text 512 steps for 1,024 tokens; image 50 (Table 6 sweep 1,024/50/15) | separate calls | None | none | L2, L4, L12 | yes |  | primer-multimodal.md 2.3, 3 table |
| M23 | MMaDA-Parallel | 2511.09611 | unified multimodal (discrete) | Erasure on both (MAGVIT-v2 or aMUSEd-VQ) | Input clean, output noised with one beta_t; per-modality weights (text 1/t, image 1) | One shared head | Dual schedulers: text linear semi-AR, image cosine global MaskGIT confidence | Confidence remasking; image CFG 3.5 (paper) or 4.0 (code) | Text 128 steps (2 per step); image 30 (paper) / 64 (README) | joint at every step (paper); code: no image tokens in first quarter | None | none | L5, L12 | yes | Paper and released sampler differ | primer-multimodal.md 2.4, 3 table |
| M24 | FUDOKI | 2505.20147 | flow (unified, metric path) | Metric-induced path softmax(-beta_t d(x,x1)) on embeddings; source uniform | One generated modality, other clean; shared t | Two heads (text 102,400; image 16,384 LlamaGen codes) | Euler CTMC; every position may change each step | Sampled; no CFG found; judge best-of-n as inference scaling (Sec 4.2) | 32 default; image step figure (Fig 5) | one modality per call | Implicit revision each step | none | L9 | partly | Metric-structured kernel is not in the C1 list (erasure, symmetric, mixtures, Gaussian); falls under D3PM general Q_t | primer-multimodal.md 2.5, 3 table |
| M25 | Lumina-DiMOO | 2510.06308 | unified multimodal (discrete) | Erasure on LLaDA text and 8,192 aMUSEd-VQ tokens | Random mask ratio over text and image positions | One head; sampling restricted to image-code subset | Image: one block cosine, top-k remasking; text semi-AR blocks of 256 | Top-k remasking; unconditional-token CFG, scale not found | Image 64; text 128 | separate calls | Self-GRPO (training only) | max-logit cache (lossy: K, V, logits of confident tokens) | L14, L12, L2 | yes |  | primer-multimodal.md 2.6, 3 table |
| M26 | Transfusion | 2408.11039 | hybrid AR+diffusion (continuous image) | Text: AR; image: Gaussian DDPM on continuous VAE patches | One noise level per image; causal over elements, bidirectional per image; 80/20 caption-first | LM head plus image decoder (noise prediction) | Text token by token; BOI switches to diffusion mode | CFG 5 (controlled) / 3 (ablations) | 250 image steps | sequential, no joint commit | Implicit revision of image | none | L12, L5 | partly | Continuous image channel has no committed set; E_fact^X undefined (placement only) | primer-multimodal.md 2.7, 3 table |
| M27 | BAGEL | 2505.14683 | hybrid AR+diffusion (continuous image) | Text: AR; image: rectified flow on FLUX-VAE latents | Generalised causal attention; independent noise per image (diffusion forcing) | Mixture-of-Transformers: text head, velocity regression | Thinking text first, then image | CFG by dropping text, ViT and clean-VAE tokens (0.1, 0.5, 0.1); scale and steps not read | not read | sequential | Implicit revision of image; thinking is output-level | none | L12, L5, L10 | partly | As Transfusion | primer-multimodal.md 2.8, 3 table |
| M28 | Show-o2 | 2506.15564 | hybrid AR+diffusion (continuous image) | Text: AR; image: flow matching on 3D-VAE latents | Omni-attention | Language head plus flow head | Text AR, then flow steps | CFG 2.5/5/7.5/10 | 25/50/100 (Table 11, CFG 7.5 fixed) | sequential | Implicit | none | L12 | partly | As Transfusion | primer-multimodal.md 2.9, 3 table |
| M29 | LaViDa-O | 2509.19244 | unified multimodal (discrete) | Erasure with modality-aware masking (A.3 not read) | Not read | Not read | Layout (object, box) text first, then image; reflection loop | not read | Reflection rounds N=1..20 (Table 16): 0.848 to 0.890, plateau near 12 | sequential (layout then image) | Output-level revision (reflection) | not read | L5, L10 | yes | Sampler internals not read | primer-multimodal.md 2.10 |
| M30 | TESS | 2305.08379 | Gaussian/embedding (logit simplex) | VP Gaussian on k-logit simplex (+-k, k=5), cosine schedule, noise N(0,k^2 I) (Eq 6-7) | None; one t for all positions; source text enters through the encoder | Logits with CE (Eq 8); RoBERTa encoder, fully non-autoregressive; input is E softmax(S_t) (Eq 6) | All positions every step; no committed set before the end | argmax projection to +-k each step, then re-noise (Eq 9-10) | T=1000 generation, 10 classification (trained T=5000); Table 7: 10/100/1000 | no (final rounding) | Implicit (all positions re-estimated) | self-conditioning: average of softmaxes, rho=0.5 train, 1 at inference (Eq 11-12) | L7, L11 (argmax projection), L1 | yes | Two-level C4 (G10) | TESS Sec 3 (Eq 6-12), Sec 4.4, Table 7, App B |
| M31 | TESS 2 | 2502.13917 | Gaussian/embedding (logit simplex), AR-adapted | As TESS (k=5 simplex, cosine), adapted from Mistral-7B | Training mixture: UL2 span infilling plus prefix completion; instruction tuning with prefix-LM only | Logits CE; label shifting (position i predicts token i+1); full bidirectional attention | All positions every step | argmax projection; optional reward-gradient guidance eta*grad on the logits each step (Eq 8) | 100 forward passes in speed test (Sec 5.4); Fig 3(b) sweep to 1000 | no (final rounding) | Implicit | self-conditioning as TESS | L6 (AR adaptation), L7, L11, L12 (reward gradient) | yes | Reward-gradient guidance edits the state, not the predictor; lever row L12 names CFG only | TESS 2 Sec 3.1-3.4, 4.4, 5.1, 5.4 |
| M32 | DiffuSeq | 2210.08933 | Gaussian/embedding (conditional seq2seq) | Gaussian on learned embeddings (d=128), sqrt schedule, T=2000; partial noising of the target half only | Conditioning mask: source clean, target noised; shared t; importance-sampled t | x0 regression (MSE on target part) plus rounding term | All target positions every step; anchoring function rounds to nearest embedding and resets the source part | Rounding/clamp each step; Minimum Bayes Risk selection over /S/=10 samples (negative BLEU) | T=2000 main; DDIM-style skipping to 1000 shown (Fig 6) | no (final rounding) | Implicit | none | L11 (clamp), L1, sequence-level selection (no lever row) | partly | MBR picks among whole samples: sequence-level selection is not in the lever table | DiffuSeq Sec 3 (Fig 2, Eq 3-4), Sec 4.1 impl. details, 4.3 |
| M33 | CANDI | 2510.22510 | hybrid channel (erasure + Gaussian) | Per position: clean anchor (Bernoulli(1-t), carry-over) or Gaussian-noised one-hot with sigma set from a target rank-degradation r*(t) (Eq 8-11) | Independent mask; masked-diffusion CE weight | Token posterior P(X0/X_t); score derived from E[X0/X_t] (Sec 5.2) | Each step: positions flipping to clean ~ Bernoulli((a(s)-a(t))/(1-a(t))), values sampled from the posterior; other positions follow the reverse PF-ODE (Sec 5.3) | Sampled; temperature swept 0.7-1.0 to trace entropy-perplexity frontier (App D.3); classifier-gradient guidance on the score | NFE up to 64 in headline (matches MDLM at 64); frontiers also at higher NFE | no | Clean anchors fixed; noisy positions stay soft until flipped | none (continuous residual is part of the state) | L1, L11 (frontier), L12 | partly | Non-committed positions carry graded evidence, not a blank mask: the erasure identity applies to the flips only, the ODE part needs the 2.3 term | CANDI Sec 5.1-5.3, Fig 7, App D.3 |
| M34 | Simplax (Simplex Relaxation) | 2608.10615 | uniform (with auxiliary simplex latent) | Uniform-state categorical z_t plus auxiliary Dirichlet variable w_t (concentration eta=0.01) (Sec 3.1) | Independent positions | Denoiser f(z_t,t) gives x_hat (z_t is the input in main results, Table 3); Rao-Blackwellised reverse-bridge objective (App E) | All positions every step | Sample z_s from the bridge, w-deterministic variant in main results; mode (z-deterministic) variants collapse entropy to 0.9-4.8; comparison at temperature closest to data entropy 5.44 | NFE 16, 128, 1024 (Tables 3-4) | no | Implicit (uniform channel) | w_t: stochastic simplex bridge state carried between steps | L9, L11 (matched entropy), state augmentation | partly | m_n here is a random latent with its own kernel, not a deterministic function of the revealed path (open item 6.1 memory claim) | Simplax Sec 3.3, 4.1, 4.4 (Tables 3-4), App A.3 (Table 7) |
| M35 | Dream 7B | 2508.15487 | AR-adapted absorbing | Erasure, alpha_t=1-t | Token-level reweighting CART: w(t,x_t,n)=1/2 sum_i 1[x_t^i not MASK] Geo(p,/n-i/-1) replaces 1/t (Sec 4.2) | Mask predictor initialised from Qwen2.5-7B; shift operation (hidden state i predicts token i+1) | Not stated in the paper (configurable decoding order via hyperparameters, Sec 5.5.3). DiffuCoder App B.2 reports Dream default = top negative-entropy remasking | Not stated in the paper. DiffuCoder App B.2 reports temperature 0.2 | Fig 7: timesteps 5-20 on Countdown beat Qwen2.5 7B; other tables not stated | no | Not stated | none | L6 (AR init, CART), L2 | yes | Sampler absent from the paper; blog not read | Dream Sec 3.2, 4.1-4.2, 5.5.2-5.5.3; DiffuCoder App B.2 for the default sampler |
| M36 | DiffuLLaMA | 2410.17891 | AR-adapted absorbing | Erasure (continuous time, Shi et al. form) | Weight 1/t; attention-mask annealing from causal to bidirectional; no time embedding | Shift operation (position i predicts i+1) on LLaMA-2 weights | Posterior jump: masked token takes the prediction with prob (a_s-a_t)/(1-a_t); conditional tasks: only high-probability tokens are denoised (rule detail not in Sec 3.4) | Unconditional: top-k 0.98 / top-p 0.9 (medium), 1.0 / 0.9 (small); conditional: high-probability filter | T=32 default (GSM8K); T=8 vs 32 in App C.5 | no | None (self-correction shown qualitatively, Table 6) | none | L6, L11, L1 | yes |  | DiffuLLaMA Sec 3.4, 4.2, App B.3 line on top-k/top-p, App C.1 |
| M37 | DiffuCoder | 2506.20639 | AR-adapted absorbing (RL) | Erasure, alpha_t=1-t | Standard weight; coupled-GRPO draws complementary mask pairs for the policy-gradient estimator (training estimator only) | Qwen2.5-Coder initialised, Dream architecture and inference implementation | Analysis: low-confidence remasking, steps=length=512; Dream default top negative-entropy; temperature changes generation order as well as tokens (Sec 4.3, 'AR-ness') | Evaluation: best over temperature set {0.2,0.3,0.4} (Table 2); pass@k analysis at 0.2-1.2; GRPO rollouts at 1.2 | 512 (=length); Fig 1c halves steps; rollouts 256 | no | None | none | L6 (RL), L2, L11 | yes | Position and value rules are coupled in practice (tempered confidence sets the order); lever table separates them | DiffuCoder Sec 4.1-4.3, Table 2, App B.1-B.2 |
| M38 | Seed Diffusion | 2508.02193 | AR-adapted absorbing + edit channel | Stage 1 (first 80% steps): erasure. Stage 2 (last 20%): edit channel (insert, delete, substitute), signal level by Levenshtein distance | Standard weight; constrained-order training on ELBO-selected model trajectories; on-policy training to shorten trajectories with a verifier | Mask logit set to -inf but no carry-over: unmasked tokens are re-predicted | Semi-AR blocks, parallel inside a block, KV cache for earlier blocks | Not stated | Not stated (headline is tokens per second) | no | Trained revision of all tokens (edit augmentation, no carry-over) | KV cache on finished blocks (lossy; authors saw no degradation) | L6, L8, L14, L4 | partly | Edit channel changes length (no position index); training on policy-selected trajectories; revision comes from training, not the channel | Seed Diffusion Sec 3.1 (Eq 1-4), 3.2, 3.3, 3.4, Remark 3.1 |
| M39 | Fast-dLLM | 2505.22618 | sampler-only (cache and adaptive k) | Erasure (applied to LLaDA, LLaDA-1.5, Dream, LLaDA-V) | Base model | Base model marginals | Block-wise (cache block 32); inside a block unmask all positions whose max-softmax confidence exceeds 0.9, at least the top one; or factor rule (n+1)(1-c_n)<f | Greedy implied (Thm 1 is about argmax); temperature not stated in the sections read | Adaptive; compared with fixed tokens per step on GSM8K (Fig 5, Fig 8) | no | None | approximate block-wise KV cache: PrefixCache, DualCache (Sec 3.2; the paper calls it approximate) | L1, L2, L14, L4 | yes |  | Fast-dLLM Sec 3.2, 3.3 (Thm 1), 4.1, 4.3 |
| M40 | Di4C | 2410.08709 | distillation (joint over positions) | Erasure teacher (SDTT-6/7 from MDLM); also Gaussian pixels, VQ masked | Distillation and consistency losses (Sec 3.3) | Mixture of products p(x_s/x_t)=E_lambda[prod_d p_d(x_s^d/x_t;lambda)], lambda~U(0,1) given as an extra input token (Sec 3.2, 5.3): a joint over the set, not marginals | Student denoiser in few steps | Ancestral sampling; draw lambda once, then independent positions (joint through lambda) | 8, 16, 32, 64, 128 (Fig 4) | yes (shared latent lambda) | None | none | L8, L3 | partly | C3 assumes marginals; here the head outputs a latent-mixture joint, which also is the joint-draw mechanism | Di4C Sec 3.2, 5.3 (Fig 4), F.3 |
| M41 | Discrete Copula Diffusion (DCD) | 2410.01949 | sampler-only (joint draw) | Absorbing (SEDD-medium); chunks of 8 tokens masked together in the sampler | Base model | Pair: SEDD marginals plus a GPT-2-small AR copula, combined by approximate I-projection (matrix scaling V) (Sec 4-5) | Committed tokens drawn autoregressively from p_hat(x^i/x_t+1, x^<i) proportional to the copula times exp(V) | Sampled directly; authors avoid nucleus because it affects generative perplexity (Sec 6.1) | DCD 2-32 steps; SEDD 2-256; DCD at 4 steps matches SEDD at 128 | yes (AR copula) | None | AR KV cache for the copula in the efficient variant | L3 | partly | C3 names one predictor; here two models with a projection step | DCD Sec 5.3 (Alg 1), 6.1, App G.1 |
| M42 | UDLM (Schiff et al., guidance) | 2412.10193 | uniform | Uniform-state, continuous time, improved bound (Sec 4) | Independent positions | Posterior x_theta; conditional and unconditional nets by condition dropout | All positions every step (ancestral) | Sampled; D-CFG: per-token p^gamma(z_s/y,z_t) p^(1-gamma)(z_s/z_t) normalised (Sec 3.1); D-CBG classifier-based (Sec 3.2) | T=128/256/512 on genomic (L=32768); QM9 Fig 6 (App E.3) | no | Implicit (uniform) | none | L12, L1, L9 | yes |  | UDLM Sec 3.1-3.2, 4, 5.2, App E.3 |
| M43 | LaViDa | 2505.16839 | unified multimodal (understanding only) | Erasure on answer tokens; image enters as continuous SigLIP features (no image generation) | Weight 1/t; complementary masking (two disjoint masks per sample); Prefix-DLM attention (prompt cannot see answer) | LLaDA-8B (default) or Dream-7B logits | Sample all, remask L*t_{i+1}; rule not stated beyond 'similar to LLaDa'; convex time-shift schedule alpha=1/3 (more tokens early) | Not stated | K in {32,24,16,8}, NFE 100% to 25% (Table 3b); at least one token per step | no | None | exact prefix KV cache, bought by Prefix-DLM (CIDEr 117.3 vs 121.0 uncached) | L13, L1, L6 | yes | Cache is exact only after changing the model class (training effect) | LaViDa Sec 3.2-3.3, 4.5, Table 3 |
| M44 | Muddit | 2505.23606 | unified multimodal (discrete) | Erasure on VQ image tokens and text tokens; one target modality per call | Independent; arccos-truncated mask ratio, cosine; loss weights image 1.0, text 0.3 (Sec 3.5) | One MM-DiT (init Meissonic), lightweight linear text head | Sampler S unmasks the fraction gamma_{t+1/T}-gamma_t of masked tokens per step; selection rule not stated in the sections read | CFG with negative condition (same operator for both modalities); App E: logits may be tempered or top-k filtered; scale 9.0 (T2I), 1.5 (I2T) | 64 default; Table 5 sweep, plateau near 32; text 16-32 (App E) | one modality per call | None | none | L12, L1 | yes |  | Muddit Sec 2.2.2-2.2.3, 3.1 (Meissonic defaults), Table 5, App D.1, E |
| M45 | Dynin-Omni | 2604.00007 | unified multimodal (discrete, omnimodal) | Erasure over joint vocabulary text + vision + speech | Independent Bernoulli(t), weight 1/t; conditioning tokens never masked | One shared head over joint vocabulary (MMaDA backbone) | Confidence-based remasking; text and speech block-wise, image one block fully parallel | Tokens are sampled, confidence is the max probability of the selected token (sample-then-filter); CFG 3.5 (generation), 2.5 (editing) | Image generation 16 steps (Table 6); editing 128; Fig 11 sweeps: GSM8K needs 512-1024, GenEval saturates 64-128 | one target modality per call | None | none | L2, L4, L11, L12 | yes |  | Dynin-Omni Sec 3.2.2, 6.4-6.5, 7.2 (Fig 11) |
| M46 | D-DiT (Dual Diffusion) | 2501.00289 | unified multimodal (flow image + masked text) | Text: erasure on T5 tokens; image: rectified flow on SD3-VAE latents | Other modality kept clean (its timestep set to 0); L = L_image + lambda_text L_text | MM-DiT with two branches: image velocity, text x0 logits; shared attention | One target modality per call: T2I Euler 28 steps; I2T ancestral posterior sampling; VQA infills the answer | T2I: CFG velocity re-weighting scale s; text: sampled | T2I 28; long text 256; Table 5 text-step sweep | one modality per call | Implicit for image; none for text | none | L12, L1 | partly | Continuous image channel has no committed set (as Transfusion) | D-DiT Sec 3.1-3.3, 4.1, 4.4 (Table 5) |
| M47 | Dimple | 2505.16990 | unified multimodal (understanding, AR-adapted) | Erasure on answer tokens; Dream backbone, Qwen2.5-VL vision encoder | Standard; training: AR alignment, AR instruction tuning, then diffusion tuning | Dream logits | MaskGIT-style top-K by confidence=max prob; 'Confident Decoding': all positions with confidence >= gamma, else the top one (Sec 3.2) | Headline Table 1: temperature 0, top-p 0.01, confident decoding disabled | Steps = response length (1 token per step); length chosen as best of {4,8,16} per benchmark | no | None | prefilling (not read) | L1, L2, L11 | yes | Best-of-three response length is chosen per benchmark on the evaluation set | Dimple Sec 3.2, S1.4 |

## 2. Selection of the new rows

Family balance of the 47 rows (script count, family label as in the CSV): unified multimodal discrete
10 and hybrid AR+diffusion (Show-o, Transfusion, BAGEL, Show-o2) 4, plus FUDOKI counted under flow
(15 multimodal in all, 32 percent); Gaussian/embedding or logit simplex 7, absorbing 6 (including
Zheng et al.), sampler-only 5, general discrete 3, uniform 3, AR-adapted absorbing 3 plus 1 with an
edit channel, flow 2, block 1, hybrid channel 1, distillation 1. The multimodal share is higher than
the brief's balance rule suggests because the multimodal primer supplied 10 rows at no reading cost.

Read and added (18): TESS (AW0221), TESS 2 (AW0207), DiffuSeq (AW0230), CANDI (AW0200), Simplex
Relaxation = Simplax (AW0022), Dream 7B (arXiv paper, not in the corpus), DiffuLLaMA (AW0165),
DiffuCoder (AW0306), Seed Diffusion (AW0135), Fast-dLLM (AW0004), Di4C (AW0467), UDLM / Schiff et
al. (not in the corpus), LaViDa (AW0257), Muddit (AW0255), Dynin-Omni (AW0244), D-DiT (not in the
corpus), Dimple (AW0258), and Discrete Copula Diffusion (AW0167), which is not on the brief's list.
IDs verified: all corpus IDs by grep of the jsonl; the three not in the corpus (Dream 7B
2508.15487, UDLM 2412.10193, D-DiT 2501.00289) by the title on their arxiv.org/html page. Show-o
(2408.12528) is also absent from the corpus, which matters for the corpus's multimodal recall, not
for this table.

Added outside the list, and why: DCD, because without it the lever row L3 (joint draw inside the set)
would have no occupant from a paper whose method I could read; Di4C alone gives a head that draws
jointly through a latent.

Dropped, and why:
- LLaDA 1.5 (2505.19223, AW0147): preference optimisation of LLaDA (L6) with the LLaDA sampler;
  it would repeat the LLaDA row. Cached, not read.
- Dream-Coder 7B (2509.01142, AW0130): same family and sampler as Dream 7B and DiffuCoder.
  Converted to markdown in the main checkout, not read.
- LLaDA-V (2505.16933, AW0259): visual instruction tuning on LLaDA; Dimple covers the understanding
  branch and adds a sampler (confident decoding). Fast-dLLM evaluates LLaDA-V, which gives a cache
  and threshold point for it. Converted, not read.
- Esoteric Language Models (2506.01928, AW0146): not on the list; the best candidate for a second
  hybrid AR+diffusion text row (exact KV cache). Converted, not read. Recommended for the next pass.

## 3. (a) Misfit list

No model was a clear no. Eleven are 'partly'. The items below are the features that do not fit as
framework-v1 is written, each with the smallest extension I can see or a recommendation to exclude.
Items 1 to 5 correspond to the 'partly' rows; items 6 to 9 are refinements where the row is marked
'yes' but the framework text should change.

1. **Edit channel with length change (Seed Diffusion, stage 2).** [S] Sec 3.1 Eq 3-4: corruption by
   insertions, deletions and substitutions, signal level by Levenshtein distance, applied in the last
   20 percent of training; Remark 3.1: no carry-over, so unmasked tokens are re-predicted and can
   change. C1 assumes a per-position state; with insertion and deletion there is no position index to
   attach the state to, and the committed-set identity (2.1) is undefined. Minimal extension: C5
   gains the value 'learned revision by edit augmentation' (revision is a joint property of training
   augmentation and sampler, not of the channel), and C1 gets a marked exclusion: length-changing
   channels are outside the scope of the identity. Recommendation: exclude from E_fact accounting,
   keep in the taxonomy under L9.
2. **Stochastic memory (Simplax).** [S] Sec 3.1, 3.3: the state carries an auxiliary Dirichlet
   variable w_t beside the categorical z_t; the sampler draws it or replaces it by its conditional
   mean (the 'w-deterministic' variant used for the main results, Sec 4.1). framework-v1 section 2.1
   says the identity holds on the augmented path and is an equality for x only if m_n is a
   deterministic function of the revealed path; here m_n is a random latent with its own kernel
   (except in the w-deterministic variant, where it is a function of z and the prediction). Minimal
   extension: allow m_n to be a latent chain with a kernel, and state the identity as a path-measure
   statement on (z, m) with an upper bound for x. This sharpens open item 6.1.
3. **Graded evidence at non-committed positions (CANDI; related DFM Eq 10).** [S] Sec 5.1: a position
   is either a clean anchor (carry-over) or a Gaussian-noised one-hot whose noise is set from a
   target rank-degradation r*(t). The committed set is the set of flips, but non-flipped positions are
   not blank: the denoiser sees their noisy values, and they evolve by the reverse PF-ODE (Sec 5.3).
   The erasure identity covers the flips conditional on the continuous residual; the continuous part
   needs the per-step term of 2.3. Minimal extension: C1 'mixture' entry should say 'per-position
   mixture of committed and graded states' and 2.1 should be stated conditional on the continuous
   residual.
4. **Predictors that output a joint over a set, not marginals (Di4C, DCD).** [S] Di4C Sec 3.2: mixture
   of products with a latent lambda given as an input token; DCD Sec 4-5: the diffusion marginals
   are combined with an autoregressive copula by an approximate I-projection. C3 lists marginals,
   ratios, x0 vectors and posterior means; none of these is a joint. Joint draw (C4) is then a
   property of C3 here. Minimal extension: C3 gets 'joint predictor over any subset: latent-mixture
   head, copula, AR head', and the lever row L3 keeps its wording. Both papers fit L3 and L8 once
   this is added.
5. **Sequence-level selection (DiffuSeq, FUDOKI; also a verifier in Seed Diffusion).** [S] DiffuSeq
   Sec 3 (Training and Inference Methods) and 4.1: Minimum Bayes Risk over |S|=10 samples; FUDOKI
   Sec 4.2 (primer): best-of-n by a judge model. L10 covers revision of finished samples; choosing
   among independent finished samples is neither revision nor a token-level value rule. It tilts the
   output law toward the utility and lowers output entropy, so P2's diagnosis applies. Minimal
   extension: a lever row 'sequence-level selection (MBR, best-of-n, verifier)' lowering a sequence
   analogue of E_sel, paid in samples.
6. **Gradient and reward guidance (TESS 2, Diffusion-LM, CANDI, UDLM D-CBG).** [S] TESS 2 Sec 3.4 Eq 8
   adds eta times the reward gradient to the logits at every step; CANDI Sec 5.3 adds a classifier
   gradient to the score. Row L12 names CFG and modality dropout only. For Gaussian and logit-simplex
   channels the guidance edits the state, not the marginals. Extension: rename L12 'guidance (CFG,
   classifier gradient, reward gradient)' and add the observation that TESS 2 Sec 4.4 reports a
   gain of about 3 AlpacaEval points at eta=0.25 and degenerate output (mostly dashes) at much larger
   values, i.e. E_sel-like sharpening with a failure mode.
7. **Position rule reads sampled or tempered values (MaskGIT, Show-o, UniDisc, Dynin-Omni, DiffuCoder).**
   [S] MaskGIT and Dynin-Omni (Sec 3.2.2) score confidence by the probability of the sampled token;
   DiffuCoder Sec 4.3 reports that temperature changes the order of generation as well as the tokens,
   and Table 2 selects the best of three temperatures. framework-v1 already separates position and
   value rows, but practice often couples them. Extension: add a boolean column 'position rule reads
   the sampled values' to the C4 description; it is what separates E_sel from the identity.
8. **Exact cache bought by changing the model (LaViDa Prefix-DLM, BD3-LM).** [S] LaViDa Sec 3.3 and
   Table 3a: the prefix cache is exact because prompt and image tokens cannot see the answer; CIDEr
   is 117.3 against 121.0 for the uncached full-attention model at NFE 100 percent. Section 2.5 says
   exact reuse adds nothing; the attention-mask route does change E_learn. Extension: L13 should say
   'exact by construction, with an E_learn cost when exactness comes from a restricted attention
   mask'.
9. **Metric-structured kernels (FUDOKI; D3PM nearest-neighbour and discretised Gaussian Q_t).** C1
   lists erasure, symmetric, mixtures, Gaussian. A softmax of embedding distance (FUDOKI, primer 2.5)
   is none of these. Extension: add 'structured transition matrix' to C1 and place it with the
   symmetric channels in 2.3.

Not misfits, noted so they are not rediscovered: the shift operation of Dream 7B, DiffuLLaMA and
TESS 2 (position i predicts token i+1) only relabels the marginals; complementary masks (LaViDa Sec
3.2, DiffuCoder coupled-GRPO) change the estimator, not the reveal law's marginal; CART in Dream 7B
(Sec 4.2) is a state-dependent objective weight and fits the 'weight if non-standard' clause; the
continuous image channels of Transfusion, BAGEL, Show-o2 and D-DiT are already stated in
framework-v1 as placement only.

**What the test could and could not fail.** Cells are free text and the five choices are broad, so
'fits' is a weak test. The sharper results are the 'not stated' cells: the position-rule and
value-rule columns could not be filled from the papers read for Dream 7B, Seed Diffusion, LaViDa,
Campbell et al. and DFM Table 2 (and, for the value rule only, MMaDA and Lumina-DiMOO), and the
lever table has no occupant for sequence-level selection. L3 (joint draw) is occupied by two rows
only, both from this pass; L10 by two. [I]

## 4. (b) Value rules in the headline results

Counts over the 47 rows (CSV columns 'value-rule classes' and 'headline uses E_sel-type rule').
Six rows have a likelihood bound as the headline (D3PM, SEDD, MDLM, MD4, RADD, ARDM) and are excluded,
and Zheng et al. is excluded as the paper whose subject is the sharpening. That leaves 40.

| Headline uses an E_sel-type rule | Models | Which |
|---|---|---|
| yes | 29 of 40 | see classes below |
| controlled by an entropy-matched frontier | 2 | CANDI (temperature 0.7 to 1.0 swept, Fig 7, App D.3); Simplax (temperature closest to data entropy 5.44, Sec 4.4; mode-based variants shown to collapse entropy to 0.9 to 4.8, Table 4) |
| no (plain sampled values) | 3 | Di4C, DCD (explicitly 'sample directly', Sec 6.1), FUDOKI default (its best-of-n variant is class M) |
| not stated in the parts read | 6 | Campbell et al., DFM Table 2, LaViDa-O, Dream 7B, Seed Diffusion, LaViDa |

Within the 29 (a model can be in several classes):
- argmax, greedy or low temperature (A or T): 15 - LLaDA, MaskGIT, EB-sampler, Diffusion-LM, CDCD,
  Plaid, Duo (Greedy-Tail), SSD-LM, UniDisc, TESS, TESS 2, DiffuSeq, DiffuCoder, Fast-dLLM
  (greedy inferred from Thm 1 and a max-probability confidence), Dimple (temperature 0, top-p 0.01).
- top-p or top-k (P): 5 - ReMDM (0.9), BD3-LM (0.9), SSD-LM, UniDisc, DiffuLLaMA (0.9 and top-k 0.98 or 1.0).
- sample-then-filter (S): 4 - MaskGIT, Show-o, UniDisc, Dynin-Omni (confidence is the probability of
  the selected sampled token, Sec 3.2.2).
- guidance (G): 14 - 9 of them have guidance as the only E_sel-type element (MMaDA, MMaDA-Parallel,
  Lumina-DiMOO, Transfusion, BAGEL, Show-o2, UDLM, Muddit, D-DiT).
- sequence-level selection (M): 2 - DiffuSeq (MBR, 10 samples), FUDOKI (judge best-of-n, optional).

Further observations [S unless marked]:
- Only 5 of the 29 report entropy or a diversity measure next to the headline: ReMDM (Table 5),
  CDCD, Duo, TESS 2, DiffuSeq. For the other 24 an E_sel component cannot be diagnosed from the paper
  (P2 needs entropy).
- Evaluation choices that act like selection and are stated in the papers: Dimple picks the best of
  response lengths 4, 8, 16 per benchmark (App S1.4); DiffuCoder reports the best of temperatures
  0.2, 0.3, 0.4 (Table 2) and states that RL moves the optimum from 0.2 to 0.3 or 0.4 (Sec 5);
  Dream's default sampler is, per DiffuCoder App B.2, top negative-entropy remasking at temperature
  0.2, while the Dream paper itself does not state it.
- Direct evidence that the rule moves the number, from papers in this table: Simplax Table 4, the
  fully deterministic sampler gives generative perplexity 14.7 to 14.8 at entropy 0.91 at every NFE,
  and the z-deterministic one 20.8 at entropy 1.07 (NFE 16), against 56.2 to 105.1 at entropy about
  5.4 for the stochastic sampler (the paper flags the low-entropy rows with a dagger); CANDI App D.3: past 128
  NFE the frontiers of MDLM, Duo and CANDI barely move and 'the effect of more steps can be achieved
  with a simple grid search' over temperature; TESS 2 Sec 5.1: AlpacaEval falls after 500 steps
  because repetition rises, perplexity falling with diversity.
- These counts are lower bounds on the use of E_sel-type rules: six rows are 'not stated', and for
  MMaDA and Lumina-DiMOO the position rule is confidence-based but the value rule is not stated, so
  they are counted only for guidance.

## 5. (c) Step sweeps with guidance and value rule held fixed

Of 47 rows, 29 report a step or NFE sweep in the parts read (25 table or figure, 3 partial, 1
qualitative only); 17 are 'ns' (not examined, so no inference), 1 has none (Seed Diffusion).

| Sweep and what is held fixed | Models |
|---|---|
| value rule shown fixed (10) | Zheng et al. (a fixed, now-corrected float32 sampler across 100 to 10000 steps, Fig 7), ReMDM (top-p 0.9, T=1024 to 4096), EB-sampler (argmax), Duo (ancestral, with and without Greedy-Tail as separate curves), FUDOKI (no CFG found), TESS (argmax, no guidance), Fast-dLLM (greedy, no CFG), Di4C (ancestral), DCD (direct sampling), D-DiT (text branch, no guidance on that path) |
| guidance fixed, value rule not stated (1) | Show-o2 (Table 11: CFG 7.5, steps 25, 50, 100) |
| value rule varied on purpose (2) | CANDI (temperature swept at each NFE), Simplax (temperature matched to data entropy at each NFE) |
| sweep reported, fixedness not stated (16) | MaskGIT, CDCD, DFM, Show-o (qualitative), UniDisc, MMaDA, TESS 2, DiffuSeq, Dream 7B, DiffuLLaMA, DiffuCoder, UDLM (App E.3), LaViDa, Muddit, Dynin-Omni, Dimple |

Reading: only 1 of the 14 models that use guidance reports a step sweep with guidance held fixed
(Show-o2); the D-DiT sweep is on the text branch, where no guidance is applied. For the unified
discrete models (UniDisc, MMaDA, Muddit, Dynin-Omni) the guidance level in the sweep is not stated.
This agrees with framework-v1 P1's caveat. Of the 10 with the value rule shown fixed, 8 are text
papers (Zheng et al., ReMDM, EB-sampler, Duo, TESS, Fast-dLLM, Di4C, DCD) and 2 are image or
multimodal (FUDOKI, D-DiT); nine of the ten have no guidance in the model at all, so 'guidance
fixed' is vacuous there. [I] The identification reading of P1 (gain at k=1 versus growth with k)
therefore has a clean within-paper test in a handful of text papers only, and in no multimodal
paper with guidance. Where a paper varies temperature jointly it reports that the frontiers
coincide across step counts: CANDI App D.3 (Fig 14) says that past 128 NFE more steps do not widen
the entropy-perplexity frontier of MDLM, Duo or CANDI. Simplax instead shows perplexity falling with
NFE at matched entropy (Table 4: 106.0, 75.1, 60.7 for the w-deterministic sampler at NFE 16, 128,
1024). Both are P2-relevant and they point in different directions.

## 6. Sources saved and versions

New markdown conversions in the main checkout `research/sources/md/` (all below 250 KB): 2502.13917
(v2), 2210.08933 (v3), 2410.17891 (v3), 2506.20639 (v2), 2509.01142 (v1, unread), 2508.02193 (v1),
2505.22618 (v3), 2410.01949 (v2), 2505.16990 (v3), 2505.16933 (v2, unread), 2506.01928 (v5, unread),
2508.15487 (v1), 2501.00289 (v2), 2412.10193 (v3). Three arXiv HTML pages were fetched once into
`research/sources/html/`: 2508.15487, 2501.00289, 2412.10193 (about 1.7 MB in total). Already cached
and used: 2305.08379 (v2), 2510.22510 (v3), 2608.10615 (v2), 2410.08709 (v4), 2505.16839 (v4),
2505.23606 (v5), 2604.00007 (v1). The conversion is from HTML with markitdown, so equations are
LaTeX text and a few characters are damaged; numbers were read from tables and sentences, not from
equations, except where a section and equation are named.

Build files for the table (data and generator) are in `design-space-v1-build/` next to this file;
`python gen.py <path-prefix>` regenerates the CSV and the counts quoted above.

No ledger rows were added.
