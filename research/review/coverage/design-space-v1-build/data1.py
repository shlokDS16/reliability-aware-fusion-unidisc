P=[]
def add(**k): P.append(k)
FO="primer-foundations.md"; SA="primer-samplers.md"; GA="primer-gaussian.md"; MM="primer-multimodal.md"
add(name="D3PM",arxiv="2107.03006",fam="general discrete (Markov matrices)",ev="primer",
 C1="General row-stochastic Q_t: uniform, absorbing, discretised Gaussian, embedding nearest-neighbour, MI schedule",
 C2="Independent per token, shared t; absorbing case is a reweighted MLM loss (weight 1/t for beta_t=1/(T-t+1), Eq 12)",
 C3="Logits of p~(x0|x_t); reverse kernel by mixture over x0 (Eq 4)",
 C4pos="Independent per-token kernel (random sets); k-step kernels (Sec 3.3)",C4val="Sampled from reverse kernel",C4steps="T=1000 (text)",C4joint="no",
 C5="None for absorbing; implicit for non-absorbing Q",mem="none",lev="L1 (k-step kernel), L6",fit="yes",missing="Non-absorbing Q have no committed set (Sec 2.3 applies)",
 src=FO+" 1.1 (D3PM Sec 3, A.2, A.3)",cls="",esel="na",ent="na",sweep="ns",swfix="na")
add(name="Campbell et al. (CTMC)",arxiv="2205.14987",fam="general discrete (CTMC)",ev="primer",
 C1="Factorised CTMC, R_t=beta(t)R_b: uniform, absorbing, Gaussian-like",
 C2="Independent per dimension; CTMC ELBO (Eq 13)",
 C3="Posterior p(x0|x) per dimension given whole state (Prop 1 Eq 11-12, Prop 3 Eq 17)",
 C4pos="Exact CTMC (one dimension per step) or tau-leaping (Poisson counts, all changes applied at end of leap)",C4val="Sampled",C4steps="not read (experiments not read)",C4joint="no",
 C5="Predictor-corrector R^c=R+R^ (Prop 4)",mem="none",lev="L1 (tau), L9",fit="yes",missing="",
 src=FO+" 1.2 (Sec 4.3, Prop 4)",cls="",esel="unclear",ent="unclear",sweep="ns",swfix="na")
add(name="SEDD",arxiv="2310.16834",fam="general discrete (CTMC, score)",ev="primer",
 C1="Absorbing or uniform CTMC, token-factorised",C2="Independent per token; weight from DWDSE (Eq 10)",
 C3="Concrete score ratio s_theta (Eq 12); absorbing postprocess scaling e^{sigma-bar}-1 (App C.2)",
 C4pos="Euler or Tweedie tau-leaping (Eq 17, 19): independent simultaneous token transitions",C4val="Sampled",C4steps="not read",C4joint="no",
 C5="None (absorbing); implicit (uniform)",mem="none",lev="L1, L6",fit="yes",missing="Ratio equals marginal times alpha/(1-alpha) only for erasure (RADD Thm 1); C3 already lists it",
 src=FO+" 1.3 (SEDD Sec 3, 4, App C.2)",cls="",esel="na",ent="na",sweep="ns",swfix="na")
add(name="MDLM",arxiv="2406.07524",fam="absorbing",ev="primer",
 C1="Interpolating erasure q=Cat(alpha x+(1-alpha)pi), pi=mask (Eq 6-8)",C2="Independent Bernoulli(alpha_t); weight alpha'/(1-alpha) (Eq 12)",
 C3="x_theta, SUBS: zero mass on mask, carry-over; time input optional (Eq 9, Table 12)",
 C4pos="Ancestral random sets from Eq 9; semi-AR blocks (Sec 4.2)",C4val="Sampled",C4steps="T=5k in speed table (Table 10); headline is a likelihood bound",C4joint="no",
 C5="None",mem="exact output cache when no token changed and no time input (Sec 4.1)",lev="L1, L4, L13",fit="yes",missing="",
 src=FO+" 1.4 (MDLM Sec 3-4)",cls="",esel="na",ent="na",sweep="ns",swfix="na")
add(name="MD4",arxiv="2406.04329",fam="absorbing",ev="primer",
 C1="Erasure, alpha_t; GenMD4 state-dependent per-token schedule alpha_{t,i}=1-t^{w_i}",C2="Independent; weight alpha'/(1-alpha) (Eq 4-5)",
 C3="Mean parameterisation mu_theta=E[x0|x_t]; time-invariant allowed",
 C4pos="Ancestral random sets (Alg 2); cosine grid for a linearly trained model (Eq 6)",C4val="Sampled",C4steps="T=256 on ImageNet 64x64 (FID 70 to 17 as reported); headline likelihood",C4joint="no",
 C5="None",mem="none",lev="L1 (grid), L6",fit="yes",missing="Per-token learned schedule is inside C1 only if alpha may differ by position",
 src=FO+" 1.5 (MD4 Sec 3, App D)",cls="",esel="na",ent="na",sweep="ns",swfix="na")
add(name="RADD",arxiv="2406.03736",fam="absorbing",ev="primer",
 C1="Absorbing CTMC (Q=sigma Q^absorb)",C2="Independent; four equivalent losses (lambda-DCE, t-DCE, any-order, ...)",
 C3="Time-free conditional c_theta(x^UM) (Eq 3.3)",
 C4pos="Tweedie tau-leaping / ancestral",C4val="Sampled",C4steps="NFE n(1-(1-1/n)^l) with caching (Eq 3.4)",C4joint="no",
 C5="None",mem="exact cache of c_theta when x_t unchanged",lev="L13, L6",fit="yes",missing="",
 src=FO+" 1.6 (RADD Sec 3, Thm 1-2)",cls="",esel="na",ent="na",sweep="ns",swfix="na")
add(name="Zheng et al. (time-agnostic, first-hitting)",arxiv="2409.02908",fam="absorbing (sampler analysis)",ev="primer",
 C1="Erasure",C2="n-masked form, weight 1/n (Prop 3.1)",C3="Time-free mu_theta (Prop 3.2)",
 C4pos="First-hitting sampler: analytic hitting time, one uniformly chosen masked position per step (Alg 1)",
 C4val="Categorical via Gumbel-max; float32 truncation sharpens (Prop 5.2); 64-bit fix; temperature 0.8-1.0 swept (Fig 10)",C4steps="100-10000 (Fig 7)",C4joint="no",
 C5="None",mem="none",lev="L1, L11 (measured sharpening)",fit="yes",missing="",
 src=FO+" 1.7; "+SA+" 2.10",cls="T",esel="subject",ent="yes",sweep="yes",swfix="yes")
add(name="ARDM",arxiv="2110.02037",fam="absorbing (order-agnostic AR)",ev="primer",
 C1="Erasure, one position per step (T=D) or parallel groups",C2="Prefix of a uniformly random permutation; weight 1/(D-t+1)",
 C3="Per-position categoricals from f(m*x), no causal mask (Alg 1-2)",
 C4pos="Random permutation; k at once via state-independent DP partition (Eq 3-4)",C4val="Sampled",C4steps="at most D calls; DP-chosen schedule for a budget",C4joint="no",
 C5="None",mem="none",lev="L1, L6",fit="yes",missing="",
 src=FO+" 1.8 (ARDM Sec 3, 3.1)",cls="",esel="na",ent="na",sweep="ns",swfix="na")
add(name="LLaDA",arxiv="2502.09992",fam="absorbing",ev="primer",
 C1="Erasure, alpha_t=1-t",C2="Independent Bernoulli; weight 1/t (Eq 3); SFT keeps prompt clean",
 C3="Mask predictor, no causal mask, no time input (App A Eq 11)",
 C4pos="Low-confidence remasking: predict all masked, keep floor(L(1-s)) most confident (Alg 5); random remasking baseline (Alg 4); semi-AR blocks for instruct",
 C4val="argmax in both Alg 4 and 5 (greedy)",C4steps="1 token per step in the sampler ablation (length=steps=256, Table 9)",C4joint="no",
 C5="None",mem="none",lev="L2, L11, L4",fit="yes",missing="Experiments and step sweeps not read in the primer",
 src=FO+" 1.9; "+SA+" 2.9 (Alg 4-5, Table 9)",cls="A",esel="yes",ent="no",sweep="ns",swfix="na")
add(name="MaskGIT",arxiv="2202.04200",fam="sampler-only (image VQ tokens)",ev="primer",
 C1="Erasure on VQ image tokens",C2="Random mask ratio, mask-scheduling function gamma (cosine)",C3="Per-position softmax over codebook",
 C4pos="Predict all masked, sample a token each, keep most confident, remask rest by gamma",C4val="Sample then filter on the sampled token probability; randomised, temperature annealed in practice",
 C4steps="8-12 iterations optimum, cosine (Table 3, Fig 8)",C4joint="no",C5="None (kept tokens get confidence 1.0)",mem="none",lev="L11 (sample-then-filter), L1",fit="yes",missing="",
 src=SA+" 2.8 (MaskGIT Sec 3.2, 4.4)",cls="S;T",esel="yes",ent="no",sweep="yes",swfix="not stated")
add(name="ReMDM",arxiv="2503.00307",fam="sampler-only (remasking)",ev="primer",
 C1="Erasure with remask posterior (sigma_t); same marginals as MDLM (Thm 3.1)",C2="As MDLM",C3="MDLM predictor",
 C4pos="MDLM step plus corrector (Thm 4.1); sigma_t Bernoulli (state-independent) or confidence-weighted (ReMDM-conf)",C4val="Sampled, nucleus top-p 0.9 in text experiments",
 C4steps="T=1024, 2048, 4096 (Table 1)",C4joint="no",C5="Remasking",mem="none",lev="L9, L11 (top-p)",fit="yes",missing="",
 src=SA+" 2.7 (Thm 3.1, 4.1; Tables 1, 5)",cls="P",esel="yes",ent="yes",sweep="yes",swfix="yes")
add(name="EB-sampler",arxiv="2505.24857",fam="sampler-only (adaptive k)",ev="primer",
 C1="Erasure (applied to LLaDA, Dream 7B)",C2="As base model",C3="Base model marginals",
 C4pos="Sort by entropy; largest prefix with sum of entropies minus max entropy below gamma (Eq 2, 8, 9): adaptive k",C4val="argmax (zero temperature) in experiments; theory assumes sampled",
 C4steps="NFE speed-up 2.05x-6.00x (Dream 7B MBPP, Table 1)",C4joint="no",C5="None",mem="none",lev="L1, L2",fit="yes",missing="",
 src=SA+" 2.5 (EB-sampler Sec 5, App A.1)",cls="A",esel="yes",ent="no",sweep="yes",swfix="yes")
add(name="Diffusion-LM",arxiv="2205.14217",fam="Gaussian/embedding",ev="primer",
 C1="VP Gaussian on learned embeddings (d=16/128), sqrt schedule, T=2000",C2="None; one shared t; control by classifier gradients (Sec 5.1)",
 C3="x0 vector regression (MSE) plus softmax rounding head (Sec 4.2)",
 C4pos="All positions updated every step; clamp to nearest embedding each step",C4val="argmax rounding (clamp each step, final argmax of rounding model)",C4steps="2000, or 200 for control (App C)",C4joint="no (final rounding commits all L at once)",
 C5="Implicit (x_{t-1} redrawn each step); no pinning",mem="none",lev="L11 (clamp), L12 (classifier gradient), L1",fit="yes",missing="Needs the two-level C4 (G10)",
 src=GA+" 3 table, 2.1",cls="A;G",esel="yes",ent="no",sweep="ns",swfix="na")
add(name="CDCD",arxiv="2211.15089",fam="Gaussian/embedding",ev="primer",
 C1="VE, sigma=t in [1,300], L2-normalised learned embeddings d=256, time-warped",C2="Conditioning mask: prefix / random / 50-50; one t for noisy positions",
 C3="Logits with CE; score interpolation Eq 6-8",
 C4pos="Deterministic Euler; all positions every step; no token drawn until the end",C4val="argmax of final extra call; score scaling, initial noise, logit truncation, CFG as knobs",C4steps="200 (as few as 50)",C4joint="no (final rounding commits all L)",
 C5="Implicit via ODE field; conditioning positions pinned",mem="self-conditioning input (previous predicted-embedding sequence)",lev="L7, L11, L12",fit="yes",missing="",
 src=GA+" 3 table, 2.2",cls="A",esel="yes",ent="yes",sweep="partial",swfix="not stated")
add(name="Plaid",arxiv="2305.18619",fam="Gaussian/embedding",ev="primer",
 C1="VE with learned sigma^2(t) incl. endpoints, learned embeddings d=16",C2="None; truncation for length",
 C3="Logits; x_hat=W softmax(f); output prior; learned p(x|z0)",
 C4pos="Ancestral, all positions every step",C4val="argmax p(x|z0) at end; score temperature 0.9",C4steps="T=4096",C4joint="no (final rounding)",
 C5="Implicit; token guidance for control (not read)",mem="self-conditioning (Sec 3.5)",lev="L7, L11, L12",fit="yes",missing="",
 src=GA+" 3 table, 2.3",cls="A;T",esel="yes",ent="unclear",sweep="ns",swfix="na")
add(name="DFM (discrete flow matching)",arxiv="2407.15595",fam="flow (probability path)",ev="primer",
 C1="Source p (mask or uniform), coupling, path of kappa-weighted deltas; Eq 10 adds uniform noise (erasure+uniform mixture)",C2="Via coupling: U- or C-coupling, random-length prefix",
 C3="Posterior w_hat, velocity affine in it (Eq 22-25); time-independent for mask source",
 C4pos="Euler step per token independently (Eq 12, Alg 1)",C4val="Sampled; temperature Eq 34 and schedule Eq 36 available (setting for Table 2 not in primer)",C4steps="NFE 256, 512, 1024 (Table 2)",C4joint="no",
 C5="Corrector u_bar=alpha u_hat-beta u_check (Eq 26), 1.7B models only",mem="none",lev="L1, L9",fit="yes",missing="",
 src=GA+" 3 table, 2.4",cls="",esel="unclear",ent="yes",sweep="yes",swfix="not stated")
add(name="Duo",arxiv="2506.10892",fam="uniform",ev="primer",
 C1="Uniform-state; Gaussian on one-hot with alpha=T(alpha~) per position",C2="Positionwise independent, same alpha_t",C3="x_theta in Delta^L posterior marginals (Eq 17-18)",
 C4pos="USDM ancestral product over tokens; all positions revisable",C4val="Sampled; Greedy-Tail argmax in last step; DCD distillation",C4steps="8-1024 (distilled: 16 matches base at 1024; 8 with Greedy-Tail)",C4joint="no",
 C5="Continual token updates by construction (claim; not isolated from distillation or entropy)",mem="none",lev="L8, L9, L11 (Greedy-Tail)",fit="yes",missing="",
 src=GA+" 3 table, 2.5",cls="A",esel="yes",ent="yes",sweep="yes",swfix="yes")
add(name="BD3-LM",arxiv="2503.09573",fam="block (semi-AR)",ev="primer",
 C1="Erasure, linear schedule",C2="Block prefix: clean prefix blocks, independent t_b per block, later blocks absent (Alg 1)",C3="Block logits plus KV (Eq 7)",
 C4pos="Block by block; first-hitting within block",C4val="Sampled; nucleus p=0.9; 64-bit Gumbel",C4steps="T=5K per block, NFE at most block length (C.5)",C4joint="no",
 C5="None",mem="exact cross-block KV cache; within-block output reuse",lev="L4, L13",fit="yes",missing="App B.5 tightness proof step flagged unjustified in primer",
 src=GA+" 3 table, 2.6",cls="P",esel="yes",ent="unclear",sweep="ns",swfix="na")
add(name="SSD-LM",arxiv="2210.17432",fam="Gaussian/embedding (logit simplex, block)",ev="primer",
 C1="VP on almost-one-hot logits (+-K), noise scale K; network sees softmax",C2="Random context length c, B-token noisy block, clean context",C3="Logits, CE",
 C4pos="Block-wise; all block positions every step",C4val="Projection each step: greedy argmax, top-p sample or multi-hot; final argmax",C4steps="not in primer (TESS App B reports 10/100/1000)",C4joint="no (final rounding)",
 C5="Implicit within block; context pinned",mem="none",lev="L4, L11",fit="yes",missing="",
 src=GA+" 3 table, 2.7",cls="A;P",esel="yes",ent="unclear",sweep="ns",swfix="na")
add(name="Show-o",arxiv="2408.12528",fam="hybrid AR+diffusion (unified)",ev="primer",
 C1="Text: AR (no channel); image: erasure on 8,192 LFQ codes",C2="Text causal prefix; image mask ratio per time step; omni-attention",C3="One shared vocabulary head (text + 8,192 image codes)",
 C4pos="Text 1 token per pass AR; image MaskGIT confidence ranking, T steps",C4val="Sampled tokens ranked by own probability (sample-then-filter); CFG w=3 or 5 (App D Eq 12)",C4steps="Image T=5/25/50, qualitative only (App I)",C4joint="sequential across modalities",
 C5="None for committed tokens",mem="none",lev="L11, L12, L5 (sequential)",fit="yes",missing="",
 src=MM+" 2.1, 3 table",cls="S;G",esel="yes",ent="no",sweep="qual",swfix="not stated")
add(name="UniDisc",arxiv="2503.20853",fam="unified multimodal (discrete)",ev="primer",
 C1="Erasure on both modalities (Llama BPE; LFQ image tokens)",C2="Independent Bernoulli over all positions, one t shared; whole-modality mask prob 0.1; weight floored by min-SNR (limit 5)",C3="One joint-vocabulary head; invalid-token mask",
 C4pos="One pool ranking text and image tokens together (Alg 2), or DDPM-style random sets",C4val="MaskGIT confidence with top-p and temperature; CFG w=1.5 (modality-dropout)",C4steps="24 in guidance tests; NFE sweep to 384 (Fig 5)",C4joint="joint (same pass)",
 C5="None",mem="none",lev="L11, L12, L5",fit="yes",missing="",
 src=MM+" 2.2, 3 table",cls="S;P;T;G",esel="yes",ent="no",sweep="yes",swfix="not stated")
add(name="MMaDA",arxiv="2505.15809",fam="unified multimodal (discrete)",ev="primer",
 C1="Erasure on LLaDA text tokens and 8,192-code MAGVIT-v2",C2="One t; weight 1/t; prompt clean in SFT",C3="One shared head",
 C4pos="Text semi-AR blocks of 64, low-confidence; image one block, cosine, low-confidence",C4val="Low-confidence remasking (value rule not stated); image CFG 3.5",C4steps="Text 512 steps for 1,024 tokens; image 50 (Table 6 sweep 1,024/50/15)",C4joint="separate calls",
 C5="None",mem="none",lev="L2, L4, L12",fit="yes",missing="",
 src=MM+" 2.3, 3 table",cls="G",esel="yes",ent="no",sweep="yes",swfix="not stated")
add(name="MMaDA-Parallel",arxiv="2511.09611",fam="unified multimodal (discrete)",ev="primer",
 C1="Erasure on both (MAGVIT-v2 or aMUSEd-VQ)",C2="Input clean, output noised with one beta_t; per-modality weights (text 1/t, image 1)",C3="One shared head",
 C4pos="Dual schedulers: text linear semi-AR, image cosine global MaskGIT confidence",C4val="Confidence remasking; image CFG 3.5 (paper) or 4.0 (code)",C4steps="Text 128 steps (2 per step); image 30 (paper) / 64 (README)",C4joint="joint at every step (paper); code: no image tokens in first quarter",
 C5="None",mem="none",lev="L5, L12",fit="yes",missing="Paper and released sampler differ",
 src=MM+" 2.4, 3 table",cls="G",esel="yes",ent="no",sweep="ns",swfix="na")
add(name="FUDOKI",arxiv="2505.20147",fam="flow (unified, metric path)",ev="primer",
 C1="Metric-induced path softmax(-beta_t d(x,x1)) on embeddings; source uniform",C2="One generated modality, other clean; shared t",C3="Two heads (text 102,400; image 16,384 LlamaGen codes)",
 C4pos="Euler CTMC; every position may change each step",C4val="Sampled; no CFG found; judge best-of-n as inference scaling (Sec 4.2)",C4steps="32 default; image step figure (Fig 5)",C4joint="one modality per call",
 C5="Implicit revision each step",mem="none",lev="L9",fit="partly",missing="Metric-structured kernel is not in the C1 list (erasure, symmetric, mixtures, Gaussian); falls under D3PM general Q_t",
 src=MM+" 2.5, 3 table",cls="M",esel="no",ent="no",sweep="yes",swfix="yes")
add(name="Lumina-DiMOO",arxiv="2510.06308",fam="unified multimodal (discrete)",ev="primer",
 C1="Erasure on LLaDA text and 8,192 aMUSEd-VQ tokens",C2="Random mask ratio over text and image positions",C3="One head; sampling restricted to image-code subset",
 C4pos="Image: one block cosine, top-k remasking; text semi-AR blocks of 256",C4val="Top-k remasking; unconditional-token CFG, scale not found",C4steps="Image 64; text 128",C4joint="separate calls",
 C5="Self-GRPO (training only)",mem="max-logit cache (lossy: K, V, logits of confident tokens)",lev="L14, L12, L2",fit="yes",missing="",
 src=MM+" 2.6, 3 table",cls="G",esel="yes",ent="no",sweep="ns",swfix="na")
add(name="Transfusion",arxiv="2408.11039",fam="hybrid AR+diffusion (continuous image)",ev="primer",
 C1="Text: AR; image: Gaussian DDPM on continuous VAE patches",C2="One noise level per image; causal over elements, bidirectional per image; 80/20 caption-first",C3="LM head plus image decoder (noise prediction)",
 C4pos="Text token by token; BOI switches to diffusion mode",C4val="CFG 5 (controlled) / 3 (ablations)",C4steps="250 image steps",C4joint="sequential, no joint commit",
 C5="Implicit revision of image",mem="none",lev="L12, L5",fit="partly",missing="Continuous image channel has no committed set; E_fact^X undefined (placement only)",
 src=MM+" 2.7, 3 table",cls="G",esel="yes",ent="no",sweep="ns",swfix="na")
add(name="BAGEL",arxiv="2505.14683",fam="hybrid AR+diffusion (continuous image)",ev="primer",
 C1="Text: AR; image: rectified flow on FLUX-VAE latents",C2="Generalised causal attention; independent noise per image (diffusion forcing)",C3="Mixture-of-Transformers: text head, velocity regression",
 C4pos="Thinking text first, then image",C4val="CFG by dropping text, ViT and clean-VAE tokens (0.1, 0.5, 0.1); scale and steps not read",C4steps="not read",C4joint="sequential",
 C5="Implicit revision of image; thinking is output-level",mem="none",lev="L12, L5, L10",fit="partly",missing="As Transfusion",
 src=MM+" 2.8, 3 table",cls="G",esel="yes",ent="no",sweep="ns",swfix="na")
add(name="Show-o2",arxiv="2506.15564",fam="hybrid AR+diffusion (continuous image)",ev="primer",
 C1="Text: AR; image: flow matching on 3D-VAE latents",C2="Omni-attention",C3="Language head plus flow head",
 C4pos="Text AR, then flow steps",C4val="CFG 2.5/5/7.5/10",C4steps="25/50/100 (Table 11, CFG 7.5 fixed)",C4joint="sequential",
 C5="Implicit",mem="none",lev="L12",fit="partly",missing="As Transfusion",
 src=MM+" 2.9, 3 table",cls="G",esel="yes",ent="no",sweep="yes",swfix="guidance fixed, value rule not stated")
add(name="LaViDa-O",arxiv="2509.19244",fam="unified multimodal (discrete)",ev="primer (targeted)",
 C1="Erasure with modality-aware masking (A.3 not read)",C2="Not read",C3="Not read",
 C4pos="Layout (object, box) text first, then image; reflection loop",C4val="not read",C4steps="Reflection rounds N=1..20 (Table 16): 0.848 to 0.890, plateau near 12",C4joint="sequential (layout then image)",
 C5="Output-level revision (reflection)",mem="not read",lev="L5, L10",fit="yes",missing="Sampler internals not read",
 src=MM+" 2.10",cls="",esel="unclear",ent="no",sweep="ns",swfix="na")
