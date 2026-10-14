```yaml
agent: paper-reader
date: 2026-10-14
brief: Primer chapter 2 (Gaussian, embedding, simplex and flow-matching branch of DLMs); check framework-v0 section 1 (C1-C5, unification claims) and the Gaussian/symmetric parts of section 2.
sources_examined:
  - arXiv:2205.14217v1   # Diffusion-LM (corpus AW0233)
  - arXiv:2211.15089v3   # CDCD (AW0227), 15 Dec 2022
  - arXiv:2305.18619v1   # Plaid (AW0175)
  - arXiv:2407.15595v2   # Discrete Flow Matching (AW0169)
  - arXiv:2506.10892v3   # Duo (AW0144)
  - arXiv:2503.09573v3   # Block Diffusion / BD3-LM (AW0003)
  - arXiv:2210.17432v2   # SSD-LM (AW0229), method section only
  - research/review/framework-v0.md (sections 1-3)
  - research/review/dossier/primer-foundations.md (sections 0, 0.1, 2e, 3)
  - research/review/dossier/primer-gaussian-check.py (own script, run output below)
coverage: |
  Text used: cached arXiv HTML in the MAIN checkout (research/sources/html/<id>.html) converted with markitdown to
  research/sources/md/<id>.md (Diffusion-LM, CDCD, Plaid, DFM, Duo, BD3-LM, SSD-LM; the md files for the first six
  were present or created in this run). Conversion keeps math as LaTeX alt text; some symbols are lost or garbled
  (Duo Eq. 11 prints phi with exp(-z^2); Plaid Sec 3.6 lost an inverse in the input rescaling). Versions as listed above.
  READ. Diffusion-LM: Sec 3.3, 4.1, 4.2, 5.1, 8, App A, B, C, E, F (Table 7). CDCD: Sec 2, 3.1-3.3, 4.1-4.5,
  6.1-6.4 (design decisions text, sampling), 7, App B.1-B.3. Plaid: Sec 2.1-2.4, 3.1-3.6, 4.1-4.2 (Table 1), 6 (Table 2,
  Sec 6.1-6.3 first paragraph), 8, App A-B (headings and B.1-B.4). DFM: Sec 2.1-2.4 (all, incl. Thm 2.2-2.4, Table 1),
  4 (text, Table 2), 5, App B (safe sampling, conditioning, NFE bound, scheduler change), App D, App E.8.
  Duo: Sec 2, 3.1-3.3, 4.1-4.2, 5.2, 7, App A.3-A.5, App C.7. BD3-LM: Sec 3.1-3.2, 4.1-4.3, 5.1-5.3, 7, 8, App B.5,
  C.4, C.5. SSD-LM: Sec 3 (3.1, 3.2) only.
  NOT READ. Experiments of Diffusion-LM (Sec 6-7), CDCD (6.5, 6.6), Plaid (Sec 5 scaling laws, 6.3 token guidance,
  7), DFM (App E proofs other than E.8, App F-I), Duo (Sec 5.1, App A.1-A.2, A.6, B, D), BD3-LM (Sec 6, App B.1-B.4, B.6-B.7),
  SSD-LM (Sec 4-6, App). Optional papers TESS (2305.08379), CANDI (2510.22510), Simplex Relaxation (2608.10615): NOT READ
  (md copies were produced but not opened beyond the corpus title/URL). No released code was inspected (all findings E2 at best).
claims:
  - statement: "Duo Eq. 10-11 (alpha_t = T(alpha~_t)) holds for the per-token argmax marginal of a VP Gaussian on K-dim one-hot vectors."
    status: supported
    evidence: primer-gaussian-check.py section A; quadrature = Monte Carlo (K=2,3,30) = closed form (K=2)
    level: E4
    confidence: 0.95
  - statement: "The argmax of a Gaussian trajectory is not the uniform-state Markov chain (Duo App A.3, Eq. 40)."
    status: supported
    evidence: check section B (given z_s a wrong class, P(z_t = clean token) 0.2855 vs 0.2291 for another wrong class; Markov-uniform kernel predicts equal)
    level: E4
    confidence: 0.9
  - statement: "framework-v0 section 2 corollary 3 'Gaussian: TC of the reverse step vanishes as the step shrinks' holds in a toy (per-step TC ~ delta^2)."
    status: supported
    evidence: check section C, log-log slope 2.16 (L=2, binary tokens, VE)
    level: E4 (toy only)
    confidence: 0.8
  - statement: "'Step size plays the role of parallelism' for Gaussian/uniform channels is stated or bounded in one of the six papers."
    status: unknown
    evidence: not found in the sections listed under coverage; nearest are DFM Eq. 20 / Def. 2.1 (o(h) per-step error) and BD3-LM App B.5
    level: E2
    confidence: 0.7
  - statement: "'Gaussian channels revise every position every step' is true as stated."
    status: mixed
    evidence: true for the state space of unconditioned positions; false for conditioning positions (CDCD Sec 4.1, DFM App B 'Conditioning', SSD-LM context); effective freezing below the identifiability noise level (CDCD Sec 6.1; check section D)
    level: E2/E4
    confidence: 0.8
competing_explanations:
  - "Duo's few-step advantage over distilled MDLM is attributed by the authors to self-correction (Sec 5.2); distillation method (DCD vs SDTT), entropy (5.6 vs 5.4) and the Greedy-Tail sampler are confounds not separated in the sections read."
unknowns:
  - "TESS, CANDI, Simplex Relaxation: nothing read."
  - "Whether any paper outside this set states the summed per-step TC for Gaussian/uniform channels (the review's novelty audit is another agent's task)."
  - "How many of CDCD's 200 Euler steps fall below the identifiability noise level (time-warped spacing is by entropy, not sigma)."
next_test: {hypothesis: "Revision rate per step (fraction of positions whose argmax decoding changes between consecutive steps) separates Gaussian/uniform samplers from masked samplers and falls to ~0 before the final step", intervention: "log per-step argmax-decoded sequences for Plaid/CDCD-style and Duo samplers at fixed NFE", primary_metric: "mean changed-position fraction per step vs step index", falsifier: "changed fraction stays above 1/L until the last step in the Gaussian samplers", gpu_hours: 2}
```

# Primer, chapter 2: the Gaussian, embedding, simplex and flow-matching branch

Tags. [S] stated by the paper at the location given (E2: "the paper reports", never "is true"). [I] my inference from
cited equations. [H] hypothesis. [V] verified here by `research/review/dossier/primer-gaussian-check.py` (a toy or
algebra check, not a reproduction of any paper's experiment). "Not found" means I searched the text listed under coverage.

## 0. Bottom line

1. Framework-v0 C1 as written ("z = alpha_t e(x) + sigma_t eps") fits Diffusion-LM exactly (variance preserving, learned e), Duo (e = one-hot in R^K) and, after a rescaling, CDCD and Plaid (variance exploding: alpha = 1, sigma = t or sigma(t)). It does not fit SSD-LM without a nonlinear input map (softmax of the noisy logits), nor DFM, whose object is a source, a coupling and a probability path, not a noise level. Two parts of the wording must go: "signal level alpha_t falling from 1 to 0" (for VE it is constant 1; the right coordinate is SNR) and "Gaussian ... simplex" as one family.
2. C2 has no Gaussian counterpart in the "which positions are clean together" sense. All noised positions share one noise level; what varies is which positions are noised at all (conditioning masks: CDCD Sec 4.1, SSD-LM context, DFM C-coupling) and, implicitly, which tokens are separated first by embedding geometry (Plaid Sec 3.1). So the replacement for C2 is (conditioning law, shared noise level, embedding geometry).
3. "Gaussian channels revise every position every step" is true of the state space and false as a description of behaviour. Conditioning positions are pinned (three papers), and below an identifiability noise level the nearest-embedding decision cannot change. The claim should be restated and measured (revision rate per step), not asserted.
4. Corollary 3 (per-step total correlation vanishes as the step shrinks) is not stated in any of the six papers. It is true in a toy ([V]: per-step TC grows as delta^2.2, so the sum over a fixed horizon is linear in delta). But a Gaussian sampler still has a parallel commitment, namely the final rounding, whose factorisation error TC(x given z_0) is not a "step-size" term. Plaid's bound contains it explicitly (Eq. 3, term -log p(x given z_0), position-wise factorial). Framework-v0 omits it.
5. Duo's duality is a per-position, per-time marginal statement for a Gaussian on one-hot vectors (Eq. 10-13); trajectories are not mapped (App A.3, Eq. 40; [V]). It does not let one read a uniform-state budget off a Gaussian one. It supports one narrow statement: for K-dimensional one-hot Gaussians, the uniform-state signal level is alpha = T(alpha~) with T from Eq. 11 ([V]).
6. DFM does not need a sixth choice but needs C1 generalised to (source, coupling, path with scheduler) and C3 generalised to a set of posteriors; its corrector (Thm 2.4) is an explicit C5 mechanism for the masked source.
7. BD3-LM's bound is the C2 block-prefix law (sum over blocks of per-block masked-diffusion bounds, each conditioned on the clean prefix, Eq. 4, 6, 8) with two caveats: its trained objective is not the bound when clipped schedules are used (Sec 5.2), and its Appendix B.5 monotonicity argument contains an unjustified exchange of expectation and product. Its KV cache is exact across blocks, so across-block E_approx = 0; within a block nothing is cached except the "no token changed" reuse, which holds only for the absorbing channel.
8. Fourteen edits to framework-v0 are listed in Section 5.

## 1. Notation

Framework notation (framework-v0 Sec 1; primer-foundations Sec 0.1): sequence x = (x^1..x^L), vocabulary V of size K, state z_t, signal level alpha_t, time t in [0,1], t = 0 clean. Additional symbols for this chapter:

- Gaussian channel, general form: per noised position `z_t = a_t e(x) + s_t eps`, eps ~ N(0, I_d). VP: a_t^2 + s_t^2 = 1 (Diffusion-LM: a = sqrt(abar_t); Duo: a = alpha~_t; SSD-LM with eps scaled by K). VE: a_t = 1, s_t = sigma(t) (CDCD: s = t; Plaid: s^2 = sigma^2(t)). SNR(t) = a_t^2 / s_t^2. VE and VP are related by z_VP = z_VE / sqrt(1+sigma^2) with the same SNR.
- e(x): embedding. Learned jointly (Diffusion-LM, CDCD with L2 normalisation times sqrt(d), Plaid), fixed one-hot in R^K (Duo), fixed almost-one-hot ±K logits (SSD-LM, Eq. 5 there).
- Network input g(z_t): z_t rescaled (CDCD: 1/sqrt(t^2+1), Sec 6.1), or softmax(z_t) (SSD-LM Sec 3.1), or z_t itself.
- Reverse step: p_theta(z_s given z_t) = q(z_s given z_t, x~ = x_hat_theta(z_t)) (Plaid Eq. 2, Diffusion-LM App E): a Gaussian with diagonal covariance, hence a product over positions and dimensions.
- T(.) (Duo Eq. 11): the map from the Gaussian signal level alpha~ to the uniform-state signal level alpha, `T(a~) = K/(K-1) [ int phi(z - a~/sqrt(1-a~^2)) Phi(z)^(K-1) dz - 1/K ]`, with phi the standard normal density (Eq. 11 as printed has exp(-z^2); App A.3 Eq. 39 has exp(-z^2/2). [V] the latter matches Monte Carlo).
- DFM: source p, target q (data), coupling pi(x0, x1), path p_t(x^i given x0, x1) = sum_j kappa^{i,j}_t w^j (Eq. 7-8), probability velocity u_t (Eq. 12-13), posterior w_hat^j (Eq. 23). Note DFM's x1 is data and x0 is source, opposite to framework time direction only in naming; t = 0 source, t = 1 data.

## 2. Per-paper records

### 2.1 Diffusion-LM (2205.14217v1)
- Forward [S]. Embedding `Emb(w)` in R^d per word; `q_phi(x0 given w) = N(Emb(w), sigma0 I)` (Sec 4.1); then the standard chain `q(x_t given x_{t-1}) = N(sqrt(1-beta_t) x_{t-1}, beta_t I)` (Sec 3.3), equivalently `x_t = sqrt(abar_t) x0 + sqrt(1-abar_t) eps` (Sec 4.2 footnote 5). Embeddings are trained end to end through the reparameterisation trick (Sec 4.1). Fixed random or pretrained embeddings were "suboptimal" (Sec 4.1). T = 2000 steps, sequence length 64, d = 16 (E2E) or 128 (ROCStories), BERT-base denoiser (App B). Schedule `abar_t = 1 - sqrt(t/T + s)`, s = 1e-4, "sqrt" schedule (App A). Sampling skips to 200 steps for control (Sec 5.1, App C).
- Objective [S]. `L_vlb^e2e` (Eq. 2) with an extra rounding term `-log p_theta(w given x0)` and the entropy of q_phi; the practical objective replaces the per-step KL by a mean-squared error, `L_simple^e2e` (Sec 4.1, App E) and then by an x0-parameterised version `sum_t ||f_theta(x_t,t) - x0||^2` (Sec 4.2, App E); this is "no longer a valid lower bound" (Sec 3.3).
- C3 [S]. The network predicts x0 as a vector (MSE), plus a softmax rounding model `p_theta(w^i given x^i)`. Equivalence of the mu-, x0- and eps- parameterisations "up to scaling constants" is argued in App E for a fixed t.
- C4 [S]. Each step: `x_{t-1} = sqrt(abar) * Clamp(f_theta(x_t,t)) + sqrt(1-abar) eps` where Clamp maps every position to its nearest word embedding (Sec 4.2). Final: `argmax p_theta(w given x0)`. Note the text (Sec 4.2) and App E differ: the main text draws x_{t-1} from the forward marginal of the clamped estimate (ignoring x_t), App E says "sample x_{t-1} from q(x_{t-1} given f_theta, x_t)". Which one the released code uses was not checked.
- C5 [S/I]. Every position is re-estimated at each step. Control uses classifier gradient steps on x_{t-1} with a fluency term lambda log p(x_{t-1} given x_t) (Sec 5.1).
- Stated limitations [S]: higher perplexity, slower decoding, slower training convergence (Sec 8). Log-likelihood models are a different training procedure (one-hot input, softmax, continuous time, learned schedule; App F) with perplexity 2.28 vs 1.77 nats (E2E, Table 7); these likelihood models are the seed of Plaid.

### 2.2 CDCD (2211.15089v3)
- Forward [S]. Karras-style VE probability-flow ODE: f = 0, g(t) = sqrt(2t), `dx = -t grad log p_t(x) dt` (Eq. 5); t is the noise standard deviation. State: embedded noisy tokens `x = e + t eps`. Embeddings (d = 256, vocabulary 32000) are L2-normalised and scaled by sqrt(d) (Sec 6.1); noise range t in [1, 300] (Sec 6.1); the network input is rescaled by 1/sqrt(t^2+1).
- C2 [S]. A boolean conditioning mask m marks given (clean) versus noisy positions (Sec 4.1): prefix masks (uniform prefix length), fully random masks (uniform clean-count then random subset) or a 50/50 mix (Sec 6.1). Noisy positions all carry the same t. Conditioning tokens are zeroed in the noisy channel and supplied as clean embeddings; "clamping" them throughout sampling is described as inferior to training for conditioning (Sec 4.1).
- C3 [S]. The network outputs logits over the vocabulary and is trained with cross-entropy (Sec 3.1). Score interpolation: `s_hat = sum_i p(x0 = e_i given x,t) s(x,t given x0 = e_i)` (Eq. 6), which for the VE conditional score `(x0 - x)/t^2` (Eq. 7) is `(E[x0] - x)/t^2` (Eq. 8). The paper notes the CE and score-matching global optima coincide and that the weighting over t differs. Renormalisation (L2-normalising E[x0]) and clamping (nearest embedding) were "found to work less well" than plain interpolation overall: they "significantly reduce AR-NLL" but cut entropy (Sec 3.2, 6.3).
- Self-conditioning [S]: the input includes the previous step's predicted-embedding sequence p (Sec 4.3); it must therefore be a training-time choice (Sec 6.3).
- Time warping [S]. The noise-level distribution is learned so that the model's prediction entropy grows linearly in a "uniform time" u (Sec 3.3, Eq. 9); sampling steps are equally spaced in u (Sec 6.4 "Step spacing", "Time warping"). This makes schedule and step spacing a learned part of C1.
- C4 [S]. 200 Euler steps (Heun no better; "reasonable quality ... as few as 50"); one extra model call after the last step and `argmax` of the logits per position (nearest-embedding rounding "works equally well") (Sec 6.4 "Final prediction"). No sampling of tokens until then: "the sampling procedure only commits to specific tokens at the very end" (Sec 2.2).
- Temperature-like knobs [S] (Sec 6.4): score scaling, initial noise scale, logit truncation, classifier-free guidance. Score temperature gave "a strictly better trade-off" than manipulating p(x0 given x,t).
- C5. The ODE sampler is deterministic; positions are never pinned except by the conditioning mask. Whether tokens effectively freeze before the end: CDCD reports tokens are recoverable "with 100% accuracy even when noise with sigma = 1.0 is added" (Sec 6.1), so everything below sigma ~ 1 is a settled decision for their embeddings.
- Negative results [S] (App B): removing the time input "significantly hurt" (B.2); a Cox-Ingersoll-Ross simplex diffusion was abandoned because the corruption is "heavy-tailed" with frequent outliers that make a corrupted vector look like the wrong token even at very low noise (B.3). This is the only first-hand evidence in the set about a genuine simplex diffusion; SSD-LM and TESS are Gaussian on logits, not simplex diffusion.
- Stated limitation [S]: no handling of variable length yet (Sec 7), lower data efficiency and no caching versus AR (Sec 2.3).

### 2.3 Plaid (2305.18619v1)
- Forward [S]. VE chain with learned total noise `sigma^2(t)`: `q(z_0 given x) = N(Embed(x), sigma^2(0))`, `q(z_t given z_s) = N(z_s, sigma^2(t) - sigma^2(s))` (Eq. 1). Embeddings are learned jointly "without additional constraints" because the loss is a likelihood bound (Sec 3.1); d = 16 (Sec 3.6). `sigma^2(0)`, `sigma^2(1)` trained to maximise the bound, the interior schedule trained to minimise variance (Sec 2.4).
- Objective [S]. `-log p(x) <= KL(q(z_1 given x) || p(z_1)) + E_q[-log p(x given z_0)] + L_T` (Eq. 3), `L_T = sum_i E KL(q(z_{(i-1)/T} given z_{i/T}, x~) || p_theta(...))` (Eq. 4), continuous-time limit `L_inf = -1/2 E[SNR'(t) ||x - x_hat_theta(z_t)||^2]` (Eq. 5). Reverse step `p_theta(z_s given z_t) = q(z_s given z_t, x~ = x_hat_theta(z_t))` (Sec 2.2).
- C3 [S]. Categorical reparameterisation: `x_hat = W_Embed softmax(f_theta(z_t))` (Sec 3.2), i.e. the network outputs per-position logits (a posterior over tokens), and the denoiser is the posterior mean embedding. Output prior (the Gaussian log-density added to the logits, Sec 3.3), learned conditional likelihood `p(x_i given z_0)` through the same logits (Sec 3.4), self-conditioning (Sec 3.5). Table 1 (compute-matched ablation, OpenWebText2, NLL bound, 1.12e18 FLOPs): full 3.89; no learned embeddings 4.54; no categorical reparameterisation 4.25; no learned schedule 4.17; no self-conditioning 3.98; CDCD reimplementation 4.23.
- C4 [S]. Plaid 1B: ancestral sampling `p(z_{t-1/T} given z_t)`, T = 4096, then `argmax p_theta(x given z_0)`, with "score temperature" tau = 0.9 implemented as adding `(1-tau)/tau (x_hat - z_t)` to `x_hat` (Sec 6.2).
- C5. Implicit; no pinning except zero-shot control by token guidance (Sec 6.3, not read).
- Stated: still a "64x" compute-efficiency gap to autoregression (Sec 8); matches GPT-2 124M zero-shot (Table 2).

### 2.4 Discrete Flow Matching (2407.15595v2)
- C1 [S]. Source p and target q on [d]^N; training pairs from a coupling pi: independent (U-coupling, Eq. 3-4) or conditional (C-coupling, Eq. 5, partial masks `I * X1 + (1-I) * mask`). Path `p_t(x) = sum pi(x0,x1) prod_i p_t(x^i given x0,x1)` (Eq. 7), conditional path a scheduler-weighted mixture of delta masses and a uniform (Eq. 8-10). Eq. 9: `(1-kappa_t) delta_{x0} + kappa_t delta_{x1}` (with the mask source this is the erasure channel with alpha_t = 1 - kappa_t). Eq. 10 adds uniform noise `kappa^2_t p_u`: a hybrid of erasure and uniform channels not in framework C1.
- C2 [S]. Through the coupling: C-coupling with prefix mask of random length N0 uniform (App B "Conditioning"); at sampling the conditioning tokens are overwritten after every step.
- C3 [S]. The network predicts posteriors `w_hat^j_t(x^i given z)` (Eq. 23), trained with cross-entropy (Eq. 28; Prop. 2.5 says the minimiser is the posterior). In the experiments a single "probability denoiser" `p_{1|t}` is used. The velocity is an affine function of posteriors with time-dependent coefficients: general Eq. 22 (a, b from Thm 2.3); convex path Eq. 24: `u = kappa'_t/(1-kappa_t) (p_{1|t} - delta_z)`; noise-prediction form Eq. 25. Table 1 shows these have "identical form" to continuous flow matching velocities. For the mask source the posterior is time independent (E.8; stated in the paper as Prop. 3.1 of the text).
- C4 [S]. Euler step per token independently: `X^i_{t+h} ~ delta_{X^i_t} + h u^i_t(., X_t)` (Eq. 12, Alg. 1). Update is valid iff Eq. 13; arbitrary h can yield negative probabilities and need clamping, which "inject[s] further error ... that can accumulate" (App B "Safe sampling"); the adaptive step Eq. 29-31 keeps the "o(h) sampling error" at the price of more evaluations. Temperature via `log p / tau` (Eq. 34) and a temperature schedule (Eq. 36). For the mask source the NFE is bounded by N because the posterior is time independent (App B "NFE bound"). Experiments: NFE 256, 512, 1024 for the 150M model (Table 2).
- C5 [S]. Corrector sampling: `u_bar = alpha_t u_hat - beta_t u_check` (Eq. 26), with u_check the backward-time velocity (Eq. 25, 27; for an i.i.d. source it needs no posterior). Thm 2.4: for perfectly trained posteriors, alpha - beta = 1 gives a velocity generating p_t, and alpha - beta = 0 gives iterations converging to p_t. For the mask source the backward velocity moves unmasked tokens back to the mask, i.e. random remasking at rate beta_t kappa'/kappa [I]. Used only for the 1.7B models; scheduler `alpha_t = 1 + alpha t^a (1-t)^b` (App D).
- Parallel-factorisation statement [S]. Eq. 20: the product of per-token updates equals `p_t + h p_dot_t + o(h)`, i.e. the factorised step is exact to first order, with a remainder written as o(h) and no constant.
- Results [S]. Table 2 generative perplexity (GPT-2) at NFE 1024: 29.3 (path Eq. 9) and 28.1 (path Eq. 10), versus 40.5 (Lou et al.) and 43.0 (Campbell et al.); entropy 7.2 and 7.1. Entropy ≥ 6 is used as a diversity flag (Sec 4.1). No likelihoods are reported for the text models (Sec 4.1).

### 2.5 Duo, "The Diffusion Duality" (2506.10892v3)
- C1 [S]. Uniform-state discrete diffusion (USDM): `q_t(. given x; alpha_t) = Cat(alpha_t x + (1 - alpha_t) 1/K)` (Eq. 1), rate matrix `Q_t = alpha'_t/(K alpha_t) [11^T - K I]` (Eq. 3), reverse posterior Eq. 4. Gaussian diffusion on one-hot vectors: `q~_t = N(alpha~_t x, (1-alpha~_t^2) I_K)` (Eq. 7).
- Duality [S]. For `w_t ~ q~_t(. given x)` and `z_t = argmax(w_t)`: `z_t ~ Cat(T(alpha~_t) x + (1-T(alpha~_t)) 1/K)` (Eq. 10-11); the discretised marginal obeys the USDM linear ODE with `Q_t = -T'/(K T) [11^T - K I]` (Eq. 12); in pushforward notation `q_t(z_t given x; T(alpha~_t)) = [argmax]_* q~_t(w_t given x; alpha~_t)` (Eq. 13). Proof sketch: Sec 3.1 and App A.1-A.2 (A.1-A.2 not read).
- What it does not claim [S]. "While the marginals of the discretized latents evolve according to a Markovian Uniform-state discrete diffusion process, a discretized Gaussian diffusion trajectory might not follow a discrete diffusion process" (Sec 3.1; App A.3 shows the pushforward of the Gaussian kernel differs from the uniform kernel, Eq. 40). [V] below.
- Samplers and likelihoods [S]. Thm 3.1: a discrete reverse kernel `p_{s|t}` that preserves the pushforward of the Gaussian reverse marginals at all t (Eq. 14-15), obtained by integrating the Gaussian reverse kernel against the posterior of `w_t` given `z_t`; the same denoising network; App A.4 states a denoiser making the standard USDM ancestral kernel (Eq. 5) coincide with Eq. 15. Thm 3.2: `E log p_data^theta (discrete) >= E log p~_data^theta (Gaussian)` by data processing (App A.5). The discrete and Gaussian chains are "separate Markov processes with no transitions between them" (Sec 3.2).
- C2 [S]. Positions are independent given x, all with the same alpha_t (sequence level, Sec 3.3).
- C3 [S]. `x_theta: V^L x [0,1] -> Delta^L` posterior marginals; Rao-Blackwellised NELBO Eq. 17-18. During curriculum training the network sees `softmax(w_t/tau)` instead of `argmax(w_t)`; this is not a valid NELBO except as `tau -> 0, beta = 0, gamma = 1` (Sec 4.1.2); evaluation uses the discrete NELBO (Eq. 18). Training window restricts t (`alpha_t in [0.05, 0.95]`, App C.7 "introduces a slight bias").
- C4 [S]. Ancestral sampling of the product kernel `p_{s|t}(z_s^{1:L} given z_t^{1:L}) = prod_l q_{s|t}(z_s^l given z_t, x_theta^l)` (Sec 3.3); Greedy-Tail sampler (argmax in the last step) lowers entropy; steps T from 8 to 1024; Discrete Consistency Distillation along the Gaussian PF-ODE projected by argmax (Sec 4.2, Eq. 22-23; teacher is the current denoiser, not EMA). Reported: distilled Duo matches base Gen PPL in 16 steps versus 1024 (ancestral), and 8 steps with Greedy-Tail "but with slightly reduced sample diversity" (Fig. 4, Sec 5.2).
- C5 [S]. "USDMs permit continual token updates, while MDMs fix tokens once unmasked" (Sec 2.1); "USDMs are self-correcting" (Sec 5.2). The sections read give this as the authors' explanation of Duo beating distilled MDLM for T ≤ 32; no ablation isolating revision from distillation or entropy was seen.
- Limitations [S]: curriculum hyperparameters (tau, duration); "USDMs lag behind MDMs in perplexity, they outperform them in the few-step generation regime" (Sec 7).

### 2.6 BD3-LM, "Block Diffusion" (2503.09573v3)
- C1/C2 [S]. Likelihood factorises over blocks of L' tokens, `log p(x) = sum_b log p(x^b given x^{<b})` (Eq. 4); each conditional is a discrete diffusion over its block (Eq. 5). Masked BD3-LM (Sec 4.1): per-token erasure channel with linear schedule. NELBO `L_BD = sum_b L(x^b, x^{<b})` (Eq. 6), simplified `sum_b E_t E_q [alpha'_t/(1-alpha_t)] log p_theta(x^b given x_t^b, x^{<b})` (Eq. 8). Training (Alg. 1): every block b gets its own `t_b ~ U[0,1]`, the noisy block attends to its own block and to the clean earlier blocks; later blocks are not visible. So the reveal law seen by a block is: prefix of blocks fully clean, current block Bernoulli(alpha_{t_b}) per token.
- C3 [S]. One network outputs per-token logits for the clean block plus keys/values (Eq. 7).
- C4 [S]. One block at a time (Alg. 2); inside the block any diffusion sampler; reported T = 5K diffusion steps with the cached "first-hitting" sampler so that model calls per block do not exceed the block length (C.5); nucleus p = 0.9; 64-bit Gumbel noise (C.5, after Zheng et al.).
- C5 [S]. None: "once a token is unmasked, it is never remasked" (C.5).
- KV caching [S]. Block-causal attention lets keys and values of finished blocks be cached "similar to AR models" (Sec 3.2). In sampling a block costs T denoising passes over the noisy block plus one pass over the clean block to extend the cache (Alg. 2). Within a block, the output of the denoiser is reused when no token changed (C.5).
- Variance and schedules [S]. The NELBO is invariant to the schedule but its Monte-Carlo estimate is not (Sec 4.3); training with clipped ranges `1 - alpha_t ~ U[beta, omega]` (Sec 5.2) is, by their own account, a different weighting ("equivalent to a continuous schedule where the mask probability is approximately 0 before the specified range ..."). Evaluation uses the low-discrepancy sampler over the full range (C.4). For L' = 1 the objective equals the AR objective only if the forward process fully masks (Table 1: 25.56 with the standard schedule, 22.88 "tuned", equal to AR at 22.88).
- Tightness [S, with a flag]. App B.5 claims `-log p <= L_K <= L_{K+1}` (bound loosens with block size). The displayed derivation (Eq. 22-24) passes from `E_t[prod_i f_i(t)]` to `prod_i E_t[f_i(t)]`; the factors share the same t, so that step is not an identity. I did not re-derive the claim; the direction is plausible on the E_fact grounds of framework Sec 2 but the printed proof does not establish it [I, confidence ~0.7 that the proof step is unjustified as printed; the conversion could have mangled it].
- Perplexity table [S] (Table 3, LM1B, 65B tokens): AR 22.83; MDLM ≤ 31.78; BD3-LM L'=16 ≤ 30.60, L'=8 ≤ 29.83, L'=4 ≤ 28.23.
- Limitations [S]: training is more expensive (under 2x); blocks are sequential so speed and controllability follow AR for small blocks (Sec 7).

### 2.7 SSD-LM (2210.17432v2), method only
- C1 [S]. Almost-one-hot logits `w~_(i) = +K if w = V_(i) else -K` (Eq. 5); VP noise `w~_t = sqrt(abar_t) w~_0 + sqrt(1-abar_t) eps`, `eps ~ N(0, K^2 I)` (Eq. 7). The network input is `softmax(w~_t)` through a weighted embedding lookup (Sec 3.1).
- C2 [S]. Semi-autoregressive: random context length c, block of B tokens noised, clean context before it (Alg. 1).
- C3/C4 [S]. Logits output, CE loss (Eq. 8-9; L2 "did not work"). Each step projects the logits back to an almost-one-hot vector by greedy argmax, top-p sample or multi-hot (Eq. 11-13) and re-noises with fresh noise (Alg. 2 lines 4-6); final `argmax` of the last state. The greedy projection is flagged by the authors as analogous to Diffusion-LM's clamping.

## 3. Design-space table (framework notation)

| Paper | C1 channel and schedule | C2 reveal law (what replaces it) | C3 predictor | C4 token discretisation and steps | C5 revision |
|---|---|---|---|---|---|
| Diffusion-LM | VP Gaussian on learned Emb in R^d (d=16/128); sqrt schedule; T=2000 (App A, B) | none; one shared t; control by classifier gradients (Sec 5.1) | x0 vector, MSE (Sec 4.2); softmax rounding head | clamp to nearest embedding every step; final argmax of rounding model; 2000 or 200 steps (Sec 4.2, App C) | implicit (x_{t-1} re-drawn each step); no pinning |
| CDCD | VE, sigma = t in [1,300], unit-scale L2-normalised learned embeddings (d=256); time-warped (Sec 3.3, 6.1) | conditioning mask m: prefix / random / 50-50; one t for noisy positions; clean positions fixed (Sec 4.1, 6.1) | logits, CE; score by interpolation Eq. 6-8; self-conditioning input | deterministic Euler, 200 steps; extra call then argmax (Sec 6.4); no token drawn earlier | implicit via the ODE field; conditioning positions pinned |
| Plaid | VE, learned sigma^2(t) incl. endpoints, learned embeddings d=16 (Sec 2.1, 3.1) | none; truncation for length (Sec 3.6) | logits; x_hat = W softmax(f); output prior; learned p(x given z_0) | ancestral T=4096; argmax p(x given z_0); score temperature 0.9 (Sec 6.2) | implicit; token guidance for control (not read) |
| DFM | source p (mask or uniform), coupling pi, path of kappa-weighted deltas, scheduler kappa_t (Eq. 7-10) | via coupling: U- or C-coupling; random-length prefix pattern (Eq. 5, App B) | posteriors w_hat (CE, Eq. 23, 28); velocity Eq. 22/24/25; time-independent for mask source (E.8) | Euler tau-leap per token independently (Eq. 12, Alg. 1), NFE 256-1024 text; temperature Eq. 34 | none by default; corrector Eq. 26, Thm 2.4 (remasking for mask source [I]) |
| Duo | Gaussian on one-hot in R^K, VP; discrete marginal = USDM with alpha = T(alpha~) (Eq. 10-11); trained as USDM, curriculum with softmax(w/tau) | positionwise independent, same alpha_t | x_theta in Delta^L (Rao-Blackwellised NELBO Eq. 17-18) | USDM ancestral, product over tokens; Greedy-Tail last step; 8-1024 steps; DCD distillation | continual token updates by construction (Sec 2.1, 5.2) |
| BD3-LM | erasure, linear schedule (Sec 4.1) | block prefix: clean prefix blocks, independent t_b per block, later blocks absent (Alg. 1) | block logits + KV (Eq. 7) | block by block; T=5K per block with first-hitting; NFE ≤ L; nucleus 0.9 (C.5) | none (absorbing) |
| SSD-LM (method only) | VP on ±K logits, noise scale K; network sees softmax(z) | random context length c, B-token noisy block | logits, CE | greedy / top-p / multi-hot projection each step, re-noise; argmax at end | implicit within block; context pinned |

## 4. Answers Q2 to Q7

### Q2. Is "Gaussian channel" correctly z = alpha_t e(x) + sigma_t eps?
Verdict: correct as a family label for Diffusion-LM, CDCD, Plaid, Duo (and SSD-LM up to the input map); it breaks in six places.
1. VE versus VP. CDCD and Plaid are VE: a_t = 1 and s_t grows (CDCD Eq. 5, Sec 6.1; Plaid Eq. 1). Framework C1's "signal level alpha_t falling from 1 to 0" is false for them. The shared quantity is SNR(t) (Plaid Eq. 5 uses SNR'(t); Duo Eq. 8 uses nu(t)). [I]
2. Learned embeddings. In Diffusion-LM, CDCD and Plaid, e(.) is trained with the denoiser, so the channel is not fixed. Plaid argues a likelihood bound keeps this well posed (Sec 3.1); CDCD and Diffusion-LM need a fix (L2 normalisation, CDCD Sec 3.2; extra terms, Diffusion-LM Sec 4.1/App E) to avoid collapse or growth. Consequence [I]: in a learned-embedding model the budget terms depend on the embedding geometry, which the framework does not parameterise. Plaid states this itself: embeddings "determine the order in which different tokens get generated" (Sec 3.1).
3. Network input is not z. CDCD rescales to unit variance (Sec 6.1), SSD-LM feeds softmax(z) (Sec 3.1). SSD-LM's softmax of ±K-scaled logits is a many-to-one map of the state; [I] the "state" of the framework (what C3 conditions on) is g(z), not z.
4. Self-conditioning (CDCD Sec 4.3, Plaid Sec 3.5). The predictor sees (z_t, previous prediction). Then p_theta(x given z) is not a function of z alone and the "policy depends on z_n only" condition of the exact budget (framework Sec 2) fails for those samplers. [I] This is stale or carried computation and belongs with E_approx or as an explicit state augmentation; it is not a channel property.
5. Score interpolation and renormalisation (CDCD Sec 3.1-3.2). Plain interpolation gives the posterior-mean embedding, which is the correct C3 object. Renormalisation or clamping changes the effective score and "significantly reduce[s] AR-NLL" with lower entropy (Sec 6.3), i.e. it behaves like E_sel, not like a new channel. [S/I]
6. Time warping and learned schedules. CDCD's time warping (Sec 3.3) is chosen from the CE curve and also sets the step spacing; Plaid learns sigma^2(t) (Sec 2.4) and notes the bound is invariant to the schedule except at the endpoints. In CDCD (non-bound objective) the schedule matters for the objective; in Plaid it matters only for variance. So "alpha_t schedule" is a C1 item with a different status in each paper. [S/I]
Also: a genuine simplex diffusion (CIR process) was tried and abandoned by CDCD (App B.3); SSD-LM/TESS are Gaussian on logits. Framework C1's phrase "Gaussian on embeddings, logits or the simplex" should say "logits", not "simplex".
One more break not in the list above: MSE-trained x0 heads (Diffusion-LM) output E[e(x) given z], a linear image of the token marginals; with d much smaller than K (16 or 256 against 32000) that map is not injective, so [I] an x0-regression head does not preserve the marginals that framework C3 says the predictor outputs. CE-trained heads (CDCD, Plaid, SSD-LM, Duo, DFM) do.

### Q3. "Gaussian channels revise every position every step (implicit C5)"
Verdict: true of the state space, mixed as a description of the samplers.
- Pinned positions exist. CDCD: clean positions are fixed through sampling (Sec 4.1, 6.1). DFM: conditioning tokens are overwritten after every step (App B). SSD-LM: clean context and block-by-block decoding (Alg. 2). BD3-LM: finished blocks never change. [S]
- Clamping and projection do not pin. Diffusion-LM re-draws x_{t-1} from the clamped estimate with fresh noise (Sec 4.2); SSD-LM re-noises its projection (Alg. 2). A position's discrete decision is recomputed every step. [S] But these tricks commit a hard token every step, so the "uncertainty superposition" CDCD cites as the benefit of continuous states (Sec 2.2) is partially removed; CDCD itself found clamping and renormalisation worse (Sec 3.2, 6.3).
- Effective freezing. CDCD reports 100% token recovery at sigma = 1 for its trained embeddings (Sec 6.1). [V] Illustration with random, not learned, embeddings of the same size (V = 32000, d = 256, norm sqrt(d)): nearest-embedding accuracy 1.000 at sigma = 1, 0.445 at sigma = 4, 0.020 at sigma = 8 (check section D). So decisions are fixed long before t reaches 0 in the sense of the identifiability scale; how many of CDCD's equally-entropy-spaced steps lie below it was not measured. [H] The revision that matters happens at intermediate noise.
- Uniform-state (Duo). Revision is permitted by the posterior (Eq. 4), and the rate matrix (Eq. 3) makes the per-step probability of leaving the current value O(step size) [I]. The "self-correcting" explanation of the few-step advantage is the authors' (Sec 5.2).
Recommended replacement for C5's third instance: "no position is pinned by the channel; pinning comes from conditioning masks; the revision rate per step is a measurable property, expected to fall to ~0 before the last step".

### Q4. Corollary 3: a stated or bounded per-step joint-dependence error for Gaussian/uniform steps
Not found, in any of the six papers, as "the summed total-correlation term of the reverse step" or as "step size plays the role of parallelism". What each does state:
- Plaid Eq. 3-4: the exact sum of per-step KLs (x-conditional form) plus the rounding term. The reverse step is a product over positions and dimensions (diagonal Gaussian), so a joint-dependence error exists implicitly, but it is not named. The optimal reverse and forward processes coincide in the limit "sigma^2(0) -> 0, sigma^2(1) -> infinity, T -> infinity" (Sec 2.2, last sentence). That is the closest statement to "the per-step term vanishes as steps shrink".
- DFM Eq. 20 and Def. 2.1: the product of per-token updates matches `p_{t+h}` up to `o(h)`; App B repeats "o(h) sampling error". No constant, no total correlation, no summed form.
- Duo Sec 3.3: the USDM kernel is a product over tokens given z_t. Sec 5.2: "MDMs generate many tokens independently and cannot revise them, leading to incoherence at low NFEs". A qualitative explanation, no bound.
- BD3-LM App B.5: the NELBO loosens with block size (printed proof flagged in Section 2.6).
- Diffusion-LM, CDCD: nothing on joint dependence per step.
[V] What the toy supports (check section C): L = 2 binary tokens with positively dependent joint (0.4, 0.1, 0.1, 0.4), VE channel `z = e(x) + sigma eps`, embedding ±1, sigma_t = 1, reverse step `q(z_s given z_t, x) = N(a z_t + (1-a) e(x), v)`, `a = sigma_s^2/sigma_t^2`, `v = sigma_s^2 (1-a)`. Step size delta = 1 - a. Expected conditional total correlation `E_{z_t} I(z_s^1; z_s^2 given z_t)`: 5.6e-3 (delta 0.4), 1.1e-3 (0.2), 2.4e-4 (0.1), 5.7e-5 (0.05), 1.4e-5 (0.025); log-log slope 2.16. So per-step TC ∝ delta^2, the sum over ~1/delta steps ∝ delta, and it vanishes. The corollary is true in this toy; "plays the role of parallelism" is an analogy [I]: here TC measures dependence among latent coordinates after noise, not among tokens committed together.
Two corrections follow [I, with V for the identity]:
(a) The VLB step term of Plaid Eq. 4 is `E_x KL(q(z_s given z_t, x) || p_theta)`, which equals `KL(q(z_s given z_t) || p_theta) + I(x; z_s given z_t)` (check section E, exact to 1e-16). With a product-form `p_theta`, the first part is `TC(z_s given z_t) + sum of marginal KL`. So the framework's E_fact appears in the bound only after marginalising x, and the bound carries an extra information term. The framework text "an equality on path divergence and only a bound on the divergence of x" is consistent with this.
(b) A Gaussian sampler has a second parallel commitment: the rounding `p(x given z_0) = prod_i p(x^i given z_0)` (Plaid Sec 2.2, Eq. 3; CDCD argmax; Diffusion-LM argmax). Its factorisation error is `TC(x given z_0)`, a genuine E_fact with A = all L positions, small only when sigma_0 is small relative to embedding separation. Plaid Sec 3.4 trades this: a stronger rounding model allows a larger sigma^2(0).

### Q5. Duo: the Gaussian-to-uniform-state correspondence
Exact statement [S]. Take a position's clean token x (one-hot in R^K), Gaussian forward `w_t ~ N(alpha~_t x, (1 - alpha~_t^2) I_K)`, and `z_t = argmax(w_t)`. Then, for each fixed t, the distribution of z_t given x is `Cat(T(alpha~_t) x + (1 - T(alpha~_t)) 1/K)` with T from Eq. 11, and its time derivative obeys the USDM linear ODE with rate `-T'/(K T) (11^T - K I)` (Eq. 10-13). Assumptions: isotropic VP noise on K-dimensional one-hot vectors (so no learned or low-dimensional embedding), a single token (sequence level is the product of independent tokens, Sec 3.3), exact argmax. T depends on K and alpha~ only.
[V] (check section A): quadrature of Eq. 11 equals Monte Carlo for K = 2, 3, 30 at alpha~ = 0.2, 0.5, 0.85 (for example K = 30, alpha~ = 0.85: 0.33523 against 0.33554) and equals the closed form for K = 2. For K = 30522 (bert-base vocabulary), alpha = 0.05 and 0.95 correspond to alpha~ = 0.924 and 0.986, so most of the uniform-state range is spanned by Gaussian signal levels above 0.92; consistent with Sec 4.1.2 / App C.7 (K = 30000 and alpha~ in [0.85, 1] "nearly spans" [0,1]: T(0.85) = 0.0078 for K = 30000).
What it does not give.
1. Not trajectories: the pushforward of the Gaussian kernel differs from the uniform-state kernel (App A.3, Eq. 40). [V] (section B, K = 3): given the Gaussian chain with clean token 0 and an observed wrong class at the earlier time, the later argmax is class 0 with probability 0.2855 versus 0.2291 for the other wrong class; the Markov uniform-state kernel predicts equality (0.1969 each). So a Gaussian trajectory's argmax carries information on x beyond its current value.
2. Not reverse kernels: Thm 3.1's kernel (Eq. 15) integrates the Gaussian reverse kernel against the posterior of `w_t` given `z_t`; to build it one needs the Gaussian model. The Duo sampler itself uses the standard USDM kernel (Eq. 5).
3. Not budgets: Thm 3.2 compares likelihoods (discrete ≥ Gaussian) by data processing (App A.5). Nothing relates E_learn, TC or per-step errors of the two chains. [I] The comparison as printed sets a pmf `q_data` against a density `p~_data` on R^K; "Gaussian likelihood" of one-hot data is only meaningful through a smoothed or discretised reading that the proof (A.5) does not spell out. I did not find this resolved in the text read.
Answer to "can the uniform-state budget be read off the Gaussian one?": no. At most the signal-level coordinate can be converted (alpha = T(alpha~)). The statement "Gaussian and symmetric channels are two instances of one channel" holds only at the per-position marginal level and only for one-hot Gaussian noise, not for embedding Gaussians (Diffusion-LM, CDCD, Plaid).

### Q6. Does DFM's probability-path view fit C1 to C3?
Partly. It fits after generalisation, and it contributes elements that framework-v0 lacks.
- C1: DFM's object is (source p, coupling pi, path). The erasure channel is Eq. 9 with a mask source; the symmetric channel is a uniform source (Sec 2.2 case (ii)) or the `kappa^2 p_u` term (Eq. 10). Eq. 10 with a mask source is a mixture of the two, not in framework C1. Schedule is kappa_t, and the experiments find it "pivotal" (Sec 4, App D: a square-function-like cubic best for text). Framework C1 should read "a path (source, coupling, scheduler)".
- C2: realised through the coupling. U-coupling is independent, C-coupling uses a random mask pattern I (Eq. 5; random-length prefix in App B). So C2 is a property of pi. [S/I]
- C3: the network predicts posteriors (Eq. 23, Prop. 2.5). Velocity is an affine function of the posteriors with time-dependent coefficients (Eq. 22; Eq. 24 for the convex path). So "velocity of a probability path" is equivalent to the posterior parameterisation for these path families, with a scalar coefficient `kappa'/(1-kappa)` and a `-delta_z` term; for the general mixture family of Eq. 8 several posteriors are needed. This confirms and extends foundations Claim 2 (erasure) to a family. [S]
- C4: Eq. 12 is tau-leaping with independent per-token draws and step size h; its validity condition (Eq. 13, App B Eq. 29-31) ties the maximal step to the schedule. [S]
- C5: new explicit element, the forward-backward velocity corrector (Eq. 26, Thm 2.4). It is Campbell's predictor-corrector in DFM's notation, restricted to perfectly trained posteriors. [S]
So DFM needs no new numbered choice; it needs C1 and C3 generalised and a pointer that C5's "explicit remasking" has a precise form (Eq. 26).

### Q7. Block diffusion: C2 block prefix law, C4, KV caching
- Likelihood versus C2. BD3-LM's NELBO (Eq. 6, 8) is the sum over blocks of per-block masked-diffusion bounds, each with the clean prefix as context: exactly "block prefix with Bernoulli inside the current block". Differences to record: (i) the weighting is the masked-diffusion weight `alpha'_t/(1-alpha_t)` per block, not 1/n (Zheng et al.) and not necessarily uniform over t in training (clipped schedules, Sec 5.2 change the weight; evaluation uses the unclipped bound, C.4); (ii) later blocks are absent rather than masked; (iii) the number of denoising steps per block is a sampler choice, so the bound describes the infinite-step model per block, consistent with framework Sec 1 caveat "bound describes the infinite-step model". For L' = 1, equality with the AR NLL needs a fully masking forward process (Sec 4.2, Table 1: 25.56 versus 22.88).
- C4. Policy within a block is any diffusion sampler; reported setting is T = 5K steps with the first-hitting trick (C.5), so each token is committed by an independent draw at its unmasking time. Across blocks the policy is deterministic and sequential: cross-block E_fact = 0, within-block E_fact present. That matches framework Sec 3 ("block-wise generation lowers E_fact across blocks") and B.5's direction (loosens with block size), subject to the proof caveat.
- KV caching and E_approx. Cross-block caching is exact: clean blocks are encoded with block-causal attention, so their keys and values depend only on the clean prefix, in training (Alg. 1, pass over the full clean x) and in sampling (Alg. 2). E_approx = 0 for that part. Cost: one extra pass per block to extend the cache. Within the block, the only reuse is "skip the pass if no token changed" (C.5), exact for the absorbing channel and unavailable when the state changes every step ([I], consistent with foundations 2e item 5). Contrast CDCD's remark that diffusion models need "a full forward pass across the entire sequence at each step" (Sec 2.3). Nothing in BD3-LM measures an approximate-cache error.
- Also: BD3-LM, unlike SSD-LM, has a tractable likelihood and bounded model calls (Sec 7 comparison).

## 5. Required edits to framework-v0 (Q8)

Numbered; source locations in brackets. I did not edit framework-v0.md.

1. Preamble, "Still unchecked: the Gaussian family". Replace by: checked against six primary papers on 2026-10-14 (this dossier); still unchecked: unified multimodal models, TESS, CANDI, Simplex Relaxation. [this report, coverage]
2. Sec 1, C1, Gaussian instance. Replace "z = alpha_t e(x) + sigma_t eps" by "z = a_t e(x) + s_t eps (VP: a^2 + s^2 = 1; VE: a = 1), e learned or fixed, network input g(z) possibly nonlinear (softmax of logits)". [Diffusion-LM Sec 4.2; CDCD Eq. 5, Sec 6.1; Plaid Eq. 1; SSD-LM Eq. 5-7, Sec 3.1; Duo Eq. 7]
3. Sec 1, C1 definition "signal level alpha_t falling from 1 to 0". State: for Gaussian channels the level is SNR(t) = a^2/s^2 from large to 0 (or finite at t = 0), and the cross-family coordinate must be stated: per-position posterior entropy (CDCD Sec 3.3) or Duo's T map for one-hot Gaussian. [Plaid Eq. 5; CDCD Sec 3.3; Duo Eq. 11]
4. Sec 1, C1: replace "Gaussian on embeddings, logits or the simplex" by "Gaussian on embeddings or logits"; add a note that a genuine simplex diffusion (CIR) was tried and abandoned. [CDCD App B.3]
5. Sec 1, C1: add the hybrid and path form: "path p_t(. given x0,x1) with source and coupling; includes mixtures of erasure and uniform noise (DFM Eq. 10)". Fix the symmetric row to P(z = x) = alpha_t + (1 - alpha_t)/K (already in foundations, Other corrections item 1). [DFM Eq. 7-10; Duo Eq. 1]
6. Sec 1, C2: add the Gaussian counterpart: (conditioning law, shared noise level, embedding geometry). Cite CDCD Sec 4.1 (prefix, random, mixed masks), SSD-LM Alg. 1 (random context and block), DFM Eq. 5/App B (C-coupling), Plaid Sec 3.1 (geometry sets the order tokens become distinguishable).
7. Sec 1, C2, block row: write "(law, weight)" for BD3-LM: independent t_b per block, clean prefix, later blocks absent; objective weight alpha'/(1-alpha) per block; clipped schedules change the weight. [BD3-LM Eq. 4-8, Alg. 1, Sec 5.2, C.4]
8. Sec 1, C3: add the list of outputs actually used: x0 vector regression (Diffusion-LM), logits turned into a posterior-mean embedding (Plaid Sec 3.2; CDCD Eq. 6-8), logits on almost-one-hot states (SSD-LM), posterior over K tokens (Duo), probability denoiser and general posteriors with velocity as an affine map (DFM Eq. 22-24). Add the caveat that an MSE x0 head with d much less than K does not retain the token marginals. [I; Diffusion-LM Sec 4.2; Plaid Sec 3.2]
9. Sec 1, C3 and Sec 2: add self-conditioning as state augmentation (predictor input includes the previous prediction), which violates "policy depends on z_n only" and belongs under E_approx or an explicit memory term. [CDCD Sec 4.3; Plaid Sec 3.5; [I]]
10. Sec 1, C4: for Gaussian and uniform channels C4 acts at two levels: per-step update of all positions (no committed set) and discretisation: per-step projection or clamp with re-noising (Diffusion-LM Sec 4.2; SSD-LM Eq. 11-13) and a final rounding that commits all L positions at once (CDCD Sec 6.4; Plaid Sec 6.2; Diffusion-LM Sec 4.2). Add that entropy-lowering knobs (clamping, renormalisation, score or logit temperature, Greedy-Tail) are E_sel analogues. [CDCD Sec 3.2, 6.3, 6.4; Plaid Sec 6.2; Duo Sec 3.3; DFM Eq. 34]
11. Sec 1, C5: replace "implicit (symmetric and Gaussian channels revise every position at every step)" by "implicit but qualified: not pinned by the channel, pinned by conditioning masks, effectively frozen below an identifiability noise level; measure the per-step revision rate". Add DFM's explicit corrector as the precise form of "remasking" for the mask source. [CDCD Sec 4.1, 6.1; DFM App B, Eq. 26, Thm 2.4; check section D]
12. Sec 1, unification claims: replace "The Gaussian channel has not yet been checked" by: Gaussian-on-one-hot and uniform-state channels coincide per position and per time through Duo Eq. 10-13 (alpha = T(alpha~)); trajectories and reverse kernels do not coincide (App A.3, Eq. 40); embedding Gaussians have no such map. [Duo Sec 3.1, App A.3; check sections A, B]
13. Sec 2, corollary 3. Rewrite: "For symmetric and Gaussian channels the per-step joint-dependence term is TC(z_s given z_t) in the x-marginalised path divergence; in a variational bound the step terms are x-conditional and carry an extra I(x; z_s given z_t). In a toy the per-step term scales as the square of the step size. In addition Gaussian samplers have a final parallel commitment with its own TC(x given z_0)." Attribution sentence: "the summed statement was not found in Diffusion-LM, CDCD, Plaid, DFM, Duo or BD3-LM; the nearest statements are Plaid Eq. 3-4 (sum of exact per-step KLs and the rounding term) and DFM Eq. 20 (o(h))." [check sections C, E; Plaid Eq. 3-4; DFM Eq. 20]
14. Sec 3 table: (a) block-wise row: add "cross-block KV cache is exact (block-causal attention), so E_approx = 0 there; within-block reuse is exact only for the absorbing channel" [BD3-LM Sec 3.2, Alg. 2, C.5]; (b) revision row: add DFM corrector and Duo's USDM as families and note Duo's few-step claim is empirical, confounded with distillation and entropy [Duo Sec 5.2, Fig. 4]; (c) add a row "self-conditioning, learned noise schedules, time warping (Gaussian models)": levers on E_learn or E_approx rather than on E_fact [CDCD Sec 3.3, 4.3; Plaid Sec 2.4, 3.5].

## 6. Disagreements, gaps and limitations

Disagreements and inconsistencies among the sources [S unless marked].
1. CDCD found clamping/renormalisation worse than plain interpolation "unlike Li et al., who found that clamping improved their results" (CDCD Sec 3.2); Diffusion-LM treats clamping as a rounding fix (Sec 4.2). The two disagree on one design choice; no common benchmark.
2. Plaid reimplemented CDCD and reports 4.23 NLL bound against its own 3.89 (Table 1), noting CDCD was not designed as a likelihood model and there was no public code; this is a reimplementation, E2 only for the statement that the authors report it.
3. Duo reports its distilled model beating distilled MDLM at low NFE but losing at high NFE, and a lower entropy for MDLM (5.4 vs 5.6) (Sec 5.2).
4. Diffusion-LM Sec 4.2 and App E describe the clamped sampling step differently (re-draw from the forward marginal versus sample from the posterior given x_t).
5. Duo Eq. 11 prints phi with exp(-z^2); Eq. 39 uses exp(-z^2/2). Typo in one place; [V] the latter is right.
6. BD3-LM B.5 proof step (Section 2.6) and Duo Thm 3.2 setup (Section Q5) are not rigorous as printed [I].

Stated limitations. Diffusion-LM: perplexity, decoding speed, training speed (Sec 8). CDCD: variable length, data efficiency, no AR-style caching (Sec 2.3, 7). Plaid: 64x compute gap (Sec 8). DFM: sampling efficiency below its continuous counterpart (Sec 5). Duo: curriculum hyperparameters; lags MDMs in perplexity (Sec 7). BD3-LM: training cost, sequential blocks (Sec 7).
Unstated limitations found. (i) Most Gaussian papers report generative perplexity or AR-NLL with entropy (CDCD Sec 6.2, DFM Sec 4.1, Duo Sec 5.2); only Plaid reports likelihood bounds for a Gaussian model, so comparison across branches mixes metric types (E_sel can move generative perplexity, framework Sec 2). (ii) No paper isolates revision from other changes. (iii) Learned-embedding models change the channel while training. (iv) Self-conditioning breaks the Markov state.

## 7. Provenance and reproducibility

Command (from `research/review/dossier/`): `python primer-gaussian-check.py` (numpy 2.4.2, scipy 1.17.1; about 8 s; seeds fixed, `default_rng(0)`). Output summary (full text re-obtained by running the command):
```
A  K=2  a~=0.20/0.50/0.85  T quad 0.11477/0.31691/0.74612  T MC 0.11434/0.31727/0.74825  closed form = quad
   K=3  T quad 0.08893/0.25962/0.68738  MC 0.08940/0.25728/0.68782
   K=30 T quad 0.01703/0.06465/0.33523  MC 0.01732/0.06474/0.33554
   K=30000: T(0.85)=0.0078; K=30522: T=0.05 at a~=0.9238, T=0.95 at a~=0.9856
B  K=3, a~_s=0.6, a~_t=0.3: alpha_(t|s)=0.4092; given z_s=wrong class 1: P(z_t=0)=0.2855, P(z_t=2)=0.2291
C  delta 0.4/0.2/0.1/0.05/0.025 -> E I(z_s^1;z_s^2|z_t) 5.62e-3/1.08e-3/2.40e-4/5.67e-5/1.38e-5; slope 2.16
D  random unit-scale embeddings V=32000 d=256: sigma 1/4/8/12/16/24 -> accuracy 1.000/0.445/0.020/0.003/0/0
E  E_x KL(q_x||p) = KL(qbar||p) + I(x;z): difference -1.7e-16
```
Caveats. B uses one Gaussian pair, not a proof; C uses L = 2 binary tokens and 600 sampled z_t with a 161-point grid (grid error not bounded; slope is consistent across five step sizes); D uses random embeddings and nearest-neighbour decoding with a flat prior, not CDCD's learned embeddings or posterior. Quadrature of Eq. 11 is unreliable for alpha~ very close to 1 (narrow integrand); I used alpha~ ≤ 0.999.
Source handling. HTML cached by earlier sessions (timestamps 2026-10-13); converted by markitdown; math symbols occasionally dropped. No code inspected. No ledger rows added. No existing file edited; new files: this report and `primer-gaussian-check.py`; new markdown conversions in the main checkout's `research/sources/md/` (2210.17432, 2305.08379, 2510.22510, 2608.10615 converted but TESS, CANDI, Simplex Relaxation unread).
