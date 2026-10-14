# Primer, chapter 1: foundations of discrete diffusion language models

Date: 2026-10-14. Evidence level of the per-paper records: E2 ("the paper reports X", never "X is true").
Statements marked DERIVED are mine, re-derived from the cited equations; the identities among them were
checked on a toy distribution (`research/review/dossier/primer-foundations-checks.py`, L=3, K=3; this is a
sanity check of algebra, not a reproduction of any paper's result). Statements marked INFERENCE are not
stated by any of the nine papers. "Not found" means I searched the text I read and did not locate it.

## 0. Sources, versions, coverage

| # | Paper | arXiv ID (verified) | Text used | Read (sections and appendices) | Not read |
|---|---|---|---|---|---|
| 1 | D3PM, Austin et al. | 2107.03006 (in corpus, AW0001) | cached HTML v3, `research/sources/md/2107.03006.md` | 2, 3, 4, 5 (tables), A.2.2, A.3, A.5 | A.4, A.6-A.8, B, images |
| 2 | Campbell et al. | 2205.14987 (not in corpus; abs page checked via Exa) | PDF text via Exa, `research/sources/md/arxiv-2205.14987-exa.md` | 2, 3, 4, 5, B.5 (assumptions), C.1, D, G | proofs of Prop 1-4, App E-F, experiments |
| 3 | SEDD, Lou et al. | 2310.16834 (not in corpus; abs page checked) | `arxiv-2310.16834-exa.md` | 2, 3, 4, 5.2 table, 6, proofs of Prop 3.2, 3.3, Thm 3.4, 3.6, 4.1, 4.2, C.2 | experiments beyond Table 1, App B, D |
| 4 | MDLM, Sahoo et al. | 2406.07524 (not in corpus; abs page checked) | `arxiv-2406.07524-exa.md` | 2.2, 3, 4, 6, B.2, C.3-C.5, E.2, E.5 | A, B.1, C.1-C.2, E.1, experiments |
| 5 | MD4, Shi et al. | 2406.04329 (v4 per abs page; not in corpus) | `arxiv-2406.04329-exa.md` | 1-6, C, D, E, H.1-H.3 | I (state-dependent derivations), J, K |
| 6 | RADD, Ou et al. | 2406.03736 (not in corpus; abs page checked) | `arxiv-2406.03736-exa.md` | 1-3, 5 (concurrent works), B, C, E, H | D (samplers, partly), J.4 "Sampling as any-order autoregressive models" (heading seen, body not read) |
| 7 | Zheng et al. (time-agnostic) | 2409.02908 (in corpus) | cached HTML, `2409.02908.md` | 2, 3, 4, 5.1, 5.3, 6.1, C.1, C.2, D | B (related work), G-J |
| 8 | ARDM, Hoogeboom et al. | 2110.02037 (not in corpus; abs page checked) | arxiv.org/html v2 via Exa, `arxiv-2110.02037-exa.md` | 2, 3, 3.1, 4, 6, B.1, C | 3.2 (depth upscaling), A, D, experiments |
| 9 | LLaDA, Nie et al. | 2502.09992 (in corpus) | cached HTML, `2502.09992.md` | 2.1-2.4, A.1, A.2 | experiments, B |

Conclusion/limitations sections of papers 3-9 were also read (used in Section 5).

Resolution note. The corpus contains papers 1, 7, 9 only. Papers 2-6 and 8 were searched in
`awesome-dlms@194aa6bd.jsonl` by title and keyword and are absent; the IDs above were verified by fetching the
arXiv abstract pages (title and authors matched). The corpus does hold a different paper, 2507.07586 ("...Secretly
Models the Bayesian Posterior"); it is not RADD and was not used. Exa-returned PDF text carries no version
stamp, so versions of papers 2, 3, 4, 6 are unpinned (E2 caveat). Equation numbers below follow the text I read.

## 0.1 Unified notation

- Vocabulary V, |V| = K; mask symbol m not in V (the "erasure" or absorbing symbol). Clean sequence
  x = (x^1..x^L) in V^L. Corrupted state z_t in (V u {m})^L. Time t in [0,1]; t = 0 clean, t = 1 fully corrupted.
- Signal level alpha_t in [0,1], strictly decreasing, alpha_0 = 1, alpha_1 = 0 unless stated; lambda_t = 1 - alpha_t
  (per-position mask probability). alpha'_t = d alpha_t / dt < 0.
- Erasure channel (absorbing): per position, independently,
  `q(z_t^i | x^i) = Cat( alpha_t e_{x^i} + (1 - alpha_t) e_m )`; for s < t, `q(z_t^i | z_s^i) = Cat(alpha_{t|s} e_{z_s^i} + (1-alpha_{t|s}) e_m)`, alpha_{t|s} = alpha_t / alpha_s.
  Posterior (MDLM Eq 8; MD4 App C Eq 17; Zheng Eq 2): for s < t,
  `q(z_s^i | z_t, x) = delta_{z_t^i}` if z_t^i != m; `= ((1-alpha_s) e_m + (alpha_s - alpha_t) e_{x^i}) / (1 - alpha_t)` if z_t^i = m.
- Symmetric (uniform) channel: `q(z_t^i | x^i) = Cat( alpha_t e_{x^i} + (1 - alpha_t) (1/K) 1 )` (MDLM Eq 6 with pi uniform; D3PM uniform with
  Qbar_t = alpha I + (1-alpha) 11^T/K). Note P(z = x) = alpha_t + (1-alpha_t)/K.
- Unmasked set U(z), unmasked tokens z^U, masked set M(z), n(z) = |M(z)|. Data conditional p_0(x^i | x^S).
- Predictor: mu_theta^i(z_t, t) in simplex over V, zero mass on m, equal to e_{z^i} if z^i != m ("SUBS" in MDLM).
  Time-free version mu_theta^i(z). Cross-entropy of a masked position: `-log mu_theta^i(z_t,t)[x^i]`.
- CTMC: rate R_t(a,b) from a to b (row convention). SEDD writes the transpose (columns sum to zero). Absorbing rate
  matrix Q_t = sigma(t) Q^absorb, sigma-bar(t) = int_0^t sigma, and alpha_t = exp(-sigma-bar(t)).
- Concrete score at z: s_t(z)_{(i,v)} = p_t(z with position i set to v) / p_t(z).
- Weight forms of the same absorbing bound (Section 2a): in t, `w(t) = -alpha'_t/(1-alpha_t) = d/dt log(1-alpha_t)`;
  in lambda, `dlambda/lambda`; in the number n of masked positions, `1/n`.

Symbol dictionary: D3PM x_t, Qbar_t, alpha-bar_t = prod(1-beta_s) -> z_t, alpha_t. Campbell x, x_0, R_t -> z_t, x, R_t.
SEDD x_t, s_theta(x,t)_y, sigma-bar -> z_t, concrete score, sigma-bar. MDLM z_t, x_theta -> same. MD4 x_t, mu_theta
-> z_t, mu_theta. RADD x_t^UM, c_theta / q_theta, lambda -> z^U, mu_theta (time-free), lambda. Zheng x_n, mu_bar -> z with n masks.
ARDM sigma, L_t, alpha(t) -> sigma, per-step loss, alpha_t. LLaDA t is the mask probability, i.e. LLaDA's t = lambda_t = 1 - alpha_t (linear schedule alpha_t = 1 - t).

## 1. Per-paper records

### 1.1 D3PM (2107.03006)
- Forward. Finite state space K, row-stochastic [Q_t]_ij = q(x_t = j | x_{t-1} = i); `q(x_t | x_{t-1}) = Cat(x_t; p = x_{t-1} Q_t)` (Eq 2);
  `q(x_t | x_0) = Cat(x_t; x_0 Qbar_t)`, `Qbar_t = Q_1 Q_2 ... Q_t`; posterior `q(x_{t-1} | x_t, x_0) = Cat(x_{t-1}; (x_t Q_t^T (.) x_0 Qbar_{t-1}) / (x_0 Qbar_t x_t^T))` (Eq 3).
  Factorised over tokens. Instances (Sec 3.1, App A.2): uniform `Q_t = (1-beta_t) I + (beta_t/K) 11^T`; absorbing (App A.2.2 Eq 7:
  1 if i=j=m; 1-beta_t if i=j!=m; beta_t if j=m, i!=m); discretised Gaussian; embedding-NN; a mutual-information schedule
  (Sec 3.2, A.7), which for absorbing reduces to beta_t = 1/(T-t+1).
- Predicts. Logits of `p~_theta(x~_0 | x_t)`; reverse kernel `p_theta(x_{t-1} | x_t) ∝ sum_{x~_0} q(x_{t-1}, x_t | x~_0) p~_theta(x~_0 | x_t)` (Eq 4);
  the same form gives a k-step kernel p_theta(x_{t-k} | x_t) (Sec 3.3).
- Objective. `L_vb = E_q(x_0)[ KL(q(x_T|x_0) || p(x_T)) + sum_{t=2}^T E_q(x_t|x_0) KL(q(x_{t-1}|x_t,x_0) || p_theta(x_{t-1}|x_t)) - E_q(x_1|x_0) log p_theta(x_0|x_1) ]` (Eq 1),
  "a variational upper bound on the negative log-likelihood" (Sec 2). Training objective actually used: `L_lambda = L_vb + lambda E[-log p~_theta(x_0|x_t)]` (Eq 5).
  Bound condition: standard ELBO; requires tractable q(x_t|x_0) and q(x_{t-1}|x_t,x_0) (criteria 1 and 2, Sec 2).
- Absorbing case (App A.3). With the x_0-parameterisation, `KL[q(x_{t-1}|x_t,x_0) || p_theta(x_{t-1}|x_t)] = -[beta_t prod_{s<t}(1-beta_s)] sum_{i: [x_t]_i = m} log p~_theta([x_0]_i | x_t) + C`;
  for beta_t = 1/(T-t+1) the weight is 1/t and the full objective is `-E[ sum_{t=1}^T (1/t) E_{q(x_t|x_0)} sum_{i masked} log p_theta([x_0]_i | x_t) ]` (Eq 12). Compared with the MLM loss (Eq 11: exactly k masked,
  weight 1/k): Eq 12 is "not exactly identical" because masks are Bernoulli, so k is a mixture of binomials (Eq 13-14, "very close to uniform").
  Claim: any absorbing D3PM is a reweighted MLM loss.
- Sampler. Ancestral over T steps (T = 1000 in text experiments), or k steps at a time via the x_0-parameterisation.
- Relations stated (Sec 4). BERT is a one-step D3PM (mixture of uniform and absorbing Q; `L_vb - L_T = L_BERT`). Autoregressive models are diffusion models: deterministic
  left-to-right masking `q([x_t]_i | x_0) = [x_0]_i if i < N-t else [MASK]`, recast on the product space [0..N] x V; per-step KL is the AR cross-entropy. Generative MLMs reduce to a reweighted
  absorbing objective. Abstract: generalises multinomial diffusion of Hoogeboom et al. 2021.
- Continuous time. App A.5 Theorem 1 (sketch proof) gives the matrix-exponential form of a CTMC; no continuous-time ELBO is derived here.
- Result reported (Sec 5, text8 Table 1): D3PM uniform 1.61 +/- 0.02 bits/char vs absorbing 1.45 +/- 0.02 at 1000 steps; LM1B: "uniform diffusion performs significantly worse".

### 1.2 Campbell et al. (2205.14987)
- Forward. CTMC with rate R_t: `q_{t|t-dt}(x | x~) = delta_{x,x~} + R_t(x~, x) dt + o(dt)` (Eq 9); `R_t = beta(t) R_b` with analytic q_{t|0} by eigendecomposition (Eq 15);
  factorised over D dimensions (Prop 3, Eq 16): each transition changes exactly one dimension. Choices: uniform `R_b = 11^T - S Id`, absorbing, spatially-biased Gaussian-like.
- Reverse and predictor. Prop 1 Eq 11: `R^_t(x, x~) = R_t(x~, x) sum_{x_0} [q_{t|0}(x~|x_0)/q_{t|0}(x|x_0)] q_{0|t}(x_0|x)`, x != x~. The network predicts `p^theta_{0|t}(x_0 | x)` and plugs it in (Eq 12).
  Multi-dimension (Prop 3, Eq 17): the factor is `q_{0|t}(x_0^d | x^{1:D})`, a per-dimension posterior given the whole state.
- Objective. Prop 2, Eq 13: `L_CT(theta) = T E_{t~U(0,T), q_t(x), r_t(x~|x)} [ {sum_{x' != x} R^theta_t(x, x')} - Z^t(x) log R^theta_t(x~, x) ] + C`,
  with Z^t(x) = sum_{x'!=x} R_t(x,x'), r_t(x~|x) = (1-delta) R_t(x,x~)/Z^t(x). Stated as "an upper bound on the negative model log-likelihood". Two proofs in B.2 (stochastic-process proof; limit of discrete-time ELBO).
  Optional auxiliary `L_ll` (Eq 196, 199). App D Prop 9: minimising the unweighted denoising cross-entropy minimises an upper bound on the negative discrete-time ELBO, i.e. a looser bound.
- Sampler. Exact CTMC (Gillespie, one dimension per step) or tau-leaping (Poisson counts with mean tau * R^; all changes applied at the end of the leap), plus predictor-corrector with `R^c = R + R^` (Prop 4).
  Sec 4.3: exact simulation changes one dimension per step; larger tau is a way to modulate the "autoregressiveness" of the model.
- Error bound. Thm 1, Eq 19: total variation `<= 3MT + {(|R| S D C1)^2 + (1/2) C2 (M + C1 S D |R|)} tau T + 2 exp{-T log^2 2 / (t_mix log 4D)}`, under Assumptions 1-3 (App B.5):
  strictly positive p_data; `q_t(x)/q_t(y) <= C1` for Hamming-neighbours; a Lipschitz-type condition C2 on R^. The text says the bound is not expected to be tight.
- Relations stated. Sec 5: all earlier discrete-diffusion work (D3PM etc.) trains and samples in discrete time; App G shows the discrete-time multi-dimensional reverse kernel makes an implicit approximation:
  Eq 241 replaces `q_{0|k+1}(x_0^d | x_k^{1:d-1}, x_{k+1}^{1:D})` by `p^theta_{0|k+1}(x_0^d | x_{k+1}^{1:D})`, "can never match the true kernel" for finite K. Of ARDM ([7] there): it uses a masking forward
  process with an order-agnostic autoregressive reading and notes the continuous-time absorbing view "but do not utilize" it in training or sampling.
- INFERENCE (not stated by the paper). Assumption 2 (bounded neighbour ratio) plausibly fails for the absorbing process, whose neighbour ratio is alpha_t/(1-alpha_t) * p_0(.|.) and is unbounded as t -> 0; so Thm 1 may not cover the absorbing case without modification.

### 1.3 SEDD (2310.16834)
- Forward. `dp_t/dt = Q_t p_t` (Eq 1), columns of Q_t sum to zero, `Q_t = sigma(t) Q`; token-level factorisation, sequence rate nonzero only at Hamming distance 1 (Eq 11); `p_{t|0}^tok(.|x) = x-th column of exp(sigma-bar(t) Q^tok)` (Eq 14).
  Q^uniform = 11^T - N I (Eq 15); Q^absorb has -1 on the diagonal and a last row of ones (Eq 16; transposed relative to row-convention papers).
- Predicts. The concrete score: `s_theta(x_1..x_i..x_d, t)_{i, x^i_hat} ≈ p_t(x_1..x^i_hat..x_d)/p_t(x_1..x_i..x_d)` (Eq 12); network takes the noise level. Implementation postprocess: exponentiate, and for absorbing "scaling by e^{sigma-bar}-1 helps" (App C.2).
- Objective. Score entropy (Def 3.1, Eq 5): `E_{x~p} sum_{y!=x} w_xy ( s_theta(x)_y - [p(y)/p(x)] log s_theta(x)_y + K(p(y)/p(x)) )`, K(a) = a(log a - 1); minimiser s = p(y)/p(x) (Prop 3.2, needs full support, w_xy > 0, infinite data and capacity).
  Denoising form DSE (Thm 3.4, Eq 7). Likelihood (Def 3.5, Thm 3.6): `-log p_0^theta(x_0) <= L_DWDSE(x_0) + KL(p_{T|0}(.|x_0) || p_base)` (Eq 9) with
  `L_DWDSE = int_0^T E_{x_t~p_{t|0}} sum_{y != x_t} Q_t(x_t, y) ( s_theta(x_t,t)_y - [p_{t|0}(y|x_0)/p_{t|0}(x_t|x_0)] log s_theta(x_t,t)_y + K(p_{t|0}(y|x_0)/p_{t|0}(x_t|x_0)) ) dt` (Eq 10).
  Proof sketch (App A): data-processing inequality then Dynkin's formula (Hanson 2007; Campbell et al.); "path measure KL". Holds for any positive s_theta (the model is the CTMC with rates s_theta Q).
- Sampler. Euler / tau-leaping (Eq 17); Tweedie tau-leaping (Eq 19-20), Thm 4.1 (discrete Tweedie: p_{0|t} from the full ratio vector) and Thm 4.2: given perfectly learned scores, Eq 19 minimises KL to the true reverse over all tau-leaping
  strategies (independent simultaneous token transitions). Conditioning by Bayes: scores of the conditional equal scores of the joint (Eq 22).
- Relations stated (Sec 2.2, 3.2, 6). Mean prediction (D3PM, Campbell) "recovers the ratios in a roundabout way (Thm 4.2)", is "inherently harder", and its objective "breaks down in continuous time and must be approximated"
  (see Section 4 below: contradicted for the absorbing case by MD4 and MDLM). DWDSE can be derived from Benton et al. 2022; its implicit version coincides with Campbell's likelihood loss (Remark after Thm 3.6).
- Result reported (Table 1, small, zero-shot perplexity bounds): SEDD Absorb 50.92 / 41.84 / 114.24 / 40.62 / 79.29 vs SEDD Uniform 65.40 / 50.27 / 140.12 / 49.60 / 101.37 (LAMBADA / WikiText2 / PTB / WikiText103 / 1BW).

### 1.4 MDLM (2406.07524)
- Forward. Interpolating family `q(z_t | x) = Cat(z_t; alpha_t x + (1-alpha_t) pi)` (Eq 6), alpha strictly decreasing, alpha_0 ≈ 1, alpha_1 ≈ 0; general posterior Eq 7; masking is pi = m (Eq 8, Sec 3.2.1). Independent across positions (Sec 3.5).
- Predicts. x_theta(z_t, t) approximating x, SUBS parameterisation (Eq 9, Sec 3.2.3): zero mass on m ("zero masking probabilities") and copy of unmasked inputs ("carry-over unmasking"). Time input may be omitted (Sec 3.2.2; Table 12: PPL 23.21 with vs 23.05 without time conditioning, OWT).
  Reverse kernel `p_theta(z_s | z_t) = q(z_s | z_t, x = x_theta(z_t, t))` (Eq 9).
- Objective. Discrete time (Eq 10): `L_diffusion = sum_i E_q[ ((alpha_{t(i)} - alpha_{s(i)})/(1 - alpha_{t(i)})) log <x_theta(z_{t(i)}), x> ]` (Rao-Blackwellised; the unsimplified form is Eq 11).
  Continuous time (Eq 12): `L^inf_NELBO = E_q int_0^1 [alpha'_t/(1-alpha_t)] log <x_theta(z_t,t), x> dt`; sequences (Eq 13) sum over positions: "the weighted average of masked language modeling (MLM) losses".
  Schedule invariance (Sec 3.4, E.1.1): with gamma = log(1-alpha_t), `L = -E int_{gamma=-inf}^{0} log <x_theta(z_gamma, gamma), x> dgamma`. Derivation of the limit in B.2 (Eq 46-49): reconstruction term 0 by carry-over, prior KL 0.
  Monotone tightening with T: asserted by analogy ("Following a similar argument", citing Campbell) in Sec 3.4; I did not find a separate proof.
- Sampler. Ancestral from Eq 9 with finite T; if the network has no time input, a step that changes no token reuses the cached output (Sec 4.1; Table 10: 40.1 vs 70.3 min at T = 5k). Semi-autoregressive blocks (Sec 4.2).
- Relations stated. Sec 6: masked diffusion is "a strict subset of D3PM"; compatible with CTMC: forward rate `R_t = (alpha'_t/alpha_t)(I - 1 m^T)`, reverse rate Eq 14 `-[alpha'_t/(1-alpha_t)] y'^T [x_theta(y,t) - m] <y,m>`; concrete score (App C.3, Eq 73-78): `s_theta(z_t = m)_{y != m} = [alpha_t/(1-alpha_t)] <x_theta, y>`; and the SEDD NELBO is rederived by CTMC (C.2) and shown to reduce to Eq 12 (C.5, Eq 85-89).
  Concurrent: Shi et al. and Ou et al. derive a similar objective; Ou et al. use a time-independent denoiser. Connection to BERT/MLM is explicit; connection to any-order autoregression: not found in MDLM.

### 1.5 MD4 (2406.04329)
- Forward. Discrete time Q_i = (1-beta_i) I + beta_i 1 e_m^T; continuous limit `Qbar(t) = alpha_t I + (1-alpha_t) 1 e_m^T`, `alpha_t = exp(-int_0^t beta(s) ds)` (Eq 1); `Qbar(s,t) = (alpha_t/alpha_s) I + (1 - alpha_t/alpha_s) 1 e_m^T`. Posterior: `q(x_s | x_t, x_0) = Cat(x_s; Rbar^{x_0}(t,s)^T x_t)`, `Rbar^{x_0}(t,s) = I + ((alpha_s - alpha_t)/(1-alpha_t)) e_m (x_0 - e_m)^T`.
- Predicts. Mean parameterisation mu_theta(x_t, t) = E[x_0 | x_t] (Eq 2-3), softmax over V when x_t = m, copy otherwise; "we can select a time-invariant parametrization" citing Ou et al.
- Objective. ELBO with `KL(q(x_s|x_t,x_0) || p_theta(x_s|x_t)) = -((alpha_s - alpha_t)/(1-alpha_t)) delta_{x_t,m} x_0^T log mu_theta(x_t,t)` (App D Eq 19); limit
  `L_inf = int_{t(1)}^1 [alpha'_t/(1-alpha_t)] E_{q(x_t|x_0)}[ delta_{x_t,m} x_0^T log mu_theta(x_t,t) ] dt` (Eq 4); sequences (Eq 5)
  `L^(N)_inf = int_0^1 [alpha'_t/(1-alpha_t)] E[ sum_{n: x_t^n = m} (x_0^n)^T log mu_theta^n(x_t,t) ] dt`. Reconstruction term -> 0 as t(1) -> 0; prior KL 0 if alpha_1 = 0, else alpha_1 log m with a modified prior (App E).
  Main text: L_T "is lower bounded by the corresponding continuous integral" so the continuous ELBO is tighter than any finite T; App D shows only the limit (no monotonicity proof found). Log-SNR form: only the endpoint SNR values matter.
- Sampler. Ancestral discrete-time reverse (Alg 2); cosine grid `t(i) = cos((pi/2)(1 - i/T))` for models trained with a linear schedule (Eq 6) because fewer tokens are unmasked in conflict early (FID 70 -> 17 at T = 256 on ImageNet 64x64, as reported).
- Relations stated (Sec 5, App H). CTMC: rates `Q(t) = beta(t)(1 e_m^T - I)`, `R^{x_0}(t) = -[alpha'_t/(1-alpha_t)] e_m (x_0 - e_m)^T` (Eq 7-8); Lemma 2 (Eq 20) and Prop 3 (Eq 21) rewrite L_inf in rate form, recovering Campbell's first term; Campbell's loss needs N network evaluations or a doubly stochastic estimate (H.2).
  Score: Prop 1 (Eq 9) `s(m,t)_j = q_t(j)/q_t(m) = [alpha_t/(1-alpha_t)] E[x_0 | x_t = m]^T e_j`, `sum_{j!=m} s(m,t)_j = alpha_t/(1-alpha_t)`; the score entropy loss with `s_theta = [alpha/(1-alpha)] mu_theta` recovers Eq 4 (H.3, Eq 22-27); in SEDD the score "is not constrained" to satisfy this, so "the learned reverse model might be incompatible with the forward process".
  Any-order autoregression: informal (Sec 5): unmasking times are i.i.d. with CDF 1-alpha_t, so the order is uniform; credited to Hoogeboom et al. App C; Ou et al. clarify the ELBO link independently. GenMD4: state-dependent schedule alpha_{t,i} = 1 - t^{w_i}, loss Eq 12.

### 1.6 RADD (2406.03736)
- Forward. CTMC with `Q_t = sigma(t) Q^absorb` (Eq 2.9), `p_{t|0}(x_t | x_0) = e^{-sigma-bar(t)}` if x_t = x_0, `1 - e^{-sigma-bar(t)}` if x_t = M (Lemma 1, Eq B.1); independent across d dimensions.
- Predicts. Time-independent conditional `c_theta(x_t)[i, v] = q_theta(v | x_t^UM) ≈ p_0(v | x_t^UM)` (Eq 3.3), x_t^UM = the unmasked tokens of x_t; SEDD architecture with the time input removed, softmax output.
- Key theorem (Thm 1, proof App B). For `x_t^i = [M]`, `x^_t^i != [M]`:
  `p_t(x_t^1..x^_t^i..x_t^d) / p_t(x_t^1..x_t^i..x_t^d) = [e^{-sigma-bar(t)} / (1 - e^{-sigma-bar(t)})] * p_0(x^_t^i | x_t^UM)`.
  Proof route: Prop 1 (Eq B.13) `p_t(x_t) = (1-e^{-sigma-bar})^{d_1} (e^{-sigma-bar})^{d_2} p_0(x_t^UM)` (d_1 masked, d_2 unmasked), then divide. Explains SEDD's "scaling trick" (Eq 3.2).
- Objective. DSE (Eq 2.11) -> `L_{t-DCE}^T(x_0) = int_0^T E_{x_t~p_{t|0}}[ sum_{x_t^i = M} -(sigma(t) e^{-sigma-bar}/(1-e^{-sigma-bar})) log( (e^{-sigma-bar}/(1-e^{-sigma-bar})) q_theta(x_0^i | x_t^UM) ) ] dt` (Eq 3.5) -> `L_{lambda-DCE}(x_0) = int_0^1 (1/lambda) E_{x_lambda}[ sum_{x_lambda^i = M} -log q_theta(x_0^i | x_lambda^UM) ] d lambda` (Eq 3.6, lambda = 1 - e^{-sigma-bar(t)}) -> `L_AO(x_0) = E_{pi~U} sum_{l=1}^d -log q_theta(x_0^{pi(l)} | x_0^{pi(<l)}; pi)` (Eq 2.16).
  Thm 2: "equivalent ... when the final total noise level sigma-bar(T) -> +infinity". Proof (App C): C.1 terms C.1 + C.3 combine to a constant that integrates to 0 (`int_0^1 log((1-lambda)/lambda) d lambda = 0`, Eq C.6); C.2 same for the change of variable (Eq C.9); C.3 expand over k masked positions,
  Beta integral `int_0^1 lambda^{k-1}(1-lambda)^{d-k} d lambda = (k-1)!(d-k)!/d!` (Eq C.15-C.17), giving `sum_{k=1}^d (1/k) E_{x~ U(k masked)}[ sum_{masked} -log q_theta ]` (C.18) which equals the AO form (C.19-C.20). The paper stresses that the AO conditionals are "inconsistent in general" across orders, so L_AO is an ensemble of orders.
  Bound status: DSE is "an upper bound of the negative log-likelihood with an unknown gap" (Sec 2.1).
- Sampler. Caching of c_theta when x_t is unchanged: expected NFE `n(1 - (1 - 1/n)^l)` for n steps and length l (Eq 3.4, Tweedie tau-leaping, log-linear schedule); Euler and Tweedie tau-leaping equivalent under log-linear schedule (D.4); ancestral mean-prediction sampler equals Tweedie tau-leaping (Eq E.2).
- Relations stated (Sec 5, App E, H). Shi et al.'s Prop 1 "resembles" Thm 1 but keeps a t-dependent conditional expectation; MDLM's time-conditioning ablation "lacking a theoretical foundation" and keeps the time-input layers set to zero; Austin et al. described the AO link without a rigorous proof ("it is not exactly identical"); Hoogeboom et al. proved ARM = ELBO of absorbing diffusion directly; RADD claims an alternative proof and four equivalent losses. Mean parameterisation: `p_{0|t}^i(x_0^i | x_t) = p_0(x_0^i | x_t^UM)` for masked i (Eq E.1).

### 1.7 Zheng et al., "time-agnostic" (2409.02908)
- Forward and model. Same as MD4/MDLM: Eq 1-4 (alpha_0 ≈ 1, alpha_1 ≈ 0), sequence factorisation, continuous-time NELBO (Eq 5, 6): `L^(L)_inf = int_0^1 [alpha'_t/(1-alpha_t)] E_{q_{t|0}}[ sum_{l: x_t^(l) = m} e_{x_0^(l)}^T log mu_theta^(l)(x_t, t) ] dt`, attributed ("it is proven") to MD4 and MDLM.
- Prop 3.1 (Eq 7-8, proof C.1 Eq 15-17). Assuming alpha_0 = 1, alpha_1 = 0:
  `L^(L)_inf = - sum_{n=1}^L E_{q~(x_n|x_0)} [ (1/n) sum_{l: x_n^(l) = m} e_{x_0^(l)}^T log mu_bar_theta^(l)(x_n) ]`, `log mu_bar_theta(x_n) = E_{alpha_n ~ Beta(L-n+1, n)} [ log mu_theta(x_n, alpha^{-1}(alpha_n)) ]`,
  where q~(x_n | x_0) masks exactly n positions uniformly. A time-conditioned network is thus a (log-)ensemble over times; with no time input mu_bar = mu.
- Prop 3.2 (Eq 9, proof C.2 Eq 18-22). The minimiser of the NELBO is `mu_{theta*}^(l)(x, t) = E_{q~_{0|N(x)}(x_0|x)}[ e_{x_0^(l)} ]`, N(x) = number of masks; it does not depend on t. Extension: any positive weights w_n on the n-form give the same minimiser (so e.g. MaskGIT-style losses are surrogates).
- Sampler. Ancestral Eq 10; first-hitting sampler (Sec 4.2, Prop 4.1, Eq 11, Alg 1): `tau_{n-1} = alpha^{-1}(1 - u_n^{1/n} (1 - alpha(tau_n)))`, u_n ~ U(0,1), then unmask one uniformly chosen masked position from Cat(mu_n^(l)); "theoretically equivalent" to simulating the continuous-time reverse chain. Parallel decoding is called an approximation method (Sec 4.3).
  Sec 5: Gumbel-based categorical sampling in float32 truncates the Gumbel maximum; Prop 5.2 (Eq 12) shows the induced distribution amplifies larger probabilities ("similar to lowering the temperature") and gives unequal unmasking probabilities across positions; reported effect: generative perplexity of MDMs drops while entropy falls; after a 64-bit fix the entropy is back to about 5.60-5.70 and MDM generative perplexity is about 100 against under 40 for the AR counterpart (as reported, Sec 6.1).
- Relation to SEDD (App D.3). Absorbing SEDD equals MDM in forward process (`alpha_t = e^{-sigma-bar(t)}`, Eq 51), parameterisation (`s_theta(x,t) = [alpha_t/(1-alpha_t)] mu_theta(x,t)`, Eq 56, from `s_t(m)_x = [alpha_t/(1-alpha_t)] p_0(x)`, Eq 55), objective (L_DWDSE with this substitution equals Eq 5, Eq 57-59, T = 1) and sampler (Euler = Tweedie tau-leaping only for the linear schedule alpha_t = 1 - t, D.3.2).
  The text states that single-token equivalence implies the multi-token case "as the factorization approach ... ensures" it; no multi-token proof is given there (RADD Thm 1 supplies one).

### 1.8 ARDM (2110.02037)
- Model class. Order-agnostic autoregression (Uria et al. 2014): `log p(x) >= E_{sigma~U(S_D)} sum_{t=1}^D log p(x_{sigma(t)} | x_{sigma(<t)})` (Eq 2), a Jensen bound on `log E_sigma p(x | sigma)`.
- Predicts. One network f producing categorical parameters for all positions from a masked input `f(m (.) x)`, m = (sigma < t); positions in sigma(>= t) are scored (Alg 1-2). No causal masking needed.
- Objective. `log p(x) >= E_{t~U(1..D)}[ D * L_t ]`, `L_t = (1/(D-t+1)) E_sigma sum_{k in sigma(>= t)} log p(x_k | x_{sigma(<t)})` (Sec 3). Each L_t is "a BERT-like training objective" with exactly D-t+1 tokens masked; the weight 1/(D-t+1) appears explicitly; OA-ARDM = D BERTs with that reweighting.
- Sampler. Draw sigma ~ U(S_D), unmask one position per step (Alg 1), at most D network calls. Parallelisation (Sec 3.1): for k variables from step t, `E_sigma[log p(x_{sigma(t+k)} | x_{sigma(<t)})] = E_sigma[log p(x_{sigma(t)} | x_{sigma(<t)})] = L_t` (Eq 3), so generating k tokens at once contributes `k * L_t` instead of `sum_{i=1}^k L_{t+i}`, and `L_t <= L_{t+1}` for a calibrated model (Eq 4: "assumption that model is well-calibrated"); a dynamic program (Watson et al. 2021) picks the parallel schedule for a step budget.
- Relation to absorbing diffusion. Abstract: ARDMs "encompass" order-agnostic ARMs and absorbing diffusion, "special cases of ARDMs under mild assumptions". App C: independent absorbing processes with few steps decay several dimensions at once, forcing the reverse model to treat them as an independent factorisation ("loss in modelling performance"); ARDM models the "fixed absorbing process" (exactly one dimension per step, T = D); AO-ARDMs are "equivalent to a continuous-time absorbing" model. The derivation is introduced with "We claim" and rests on: transition times tau_i i.i.d. with CDF 1 - alpha(t); x(0) independent of the tau_i given x(t); KL(q(tau)||p(tau)) = 0; the order of decay is uniform.
  The text notes that conditioning on "sigma" is what turns an order-less set into a masked vector.

### 1.9 LLaDA, objective and sampler only (2502.09992)
- Forward. Linear: `q_{t|0}(x_t^i | x_0^i) = 1 - t` (x_t^i = x_0^i), `t` (x_t^i = M) (App A Eq 8); i.e. alpha_t = 1 - t.
- Predicts. A mask predictor p_theta(. | x_t), Transformer without causal mask, no time input (App A Eq 11: `q_{0|t}(x_s^i | x_t) = p_data(x_0^i | x_t^UM)`, "as proven in [Ou et al.]").
- Objective. Eq 3: `L(theta) = -E_{t, x_0, x_t}[ (1/t) sum_{i=1}^L 1[x_t^i = M] log p_theta(x_0^i | x_t) ]`, t ~ U[0,1]; claimed "proven to be an upper bound on the negative log-likelihood" (Eq 4; the proof is cited to Shi, Sahoo, Ou, not given). SFT conditional version Eq 5 with the prompt left unmasked. Algorithm 1 divides by an extra `1/L` (implementation scaling).
  Likelihood-evaluation form Eq 6/14: `-E_{l, r_0, r_l}[ (L/l) sum_i 1[r_l^i = M] log p_theta(r_0^i | p_0, r_l) ]`, l ~ U{1..L}, exactly l positions masked ("lower variance"); "equivalent in expectation" to Bernoulli masking (cites Ou).
- Sampler. Remasking reverse step from t to s: predict all masked tokens, remask a fraction s/t. Alg 4 "random remasking": line 4 takes `argmax` of p_theta ("greedy sampling"). Alg 5 "low-confidence remasking" (the default): argmax values, then remask the lowest-confidence ones so that floor(L(1-s)) stay unmasked. Text: "In principle, the remasking strategy should be purely random"; the low-confidence rule is a departure motivated by annealing practice in LLMs.
- Relations stated. Eq 15 (App A.2): AO-ARM objective; "It can be further proved that" it is equivalent to Eq 12, no proof given. MaskGIT "misses the 1/t term" and "lacks a theoretical link to maximum likelihood".

## 2. Synthesis in one notation

### 2a. Continuous-time bound for absorbing diffusion as a weighted masked cross-entropy

Statement A (assembled from MD4 Eq 2-5 and App D, MDLM Eq 8-13 and B.2, Zheng Eq 3-6; equivalent to SEDD Thm 3.6 under the constraint of 2d).
Let the channel be the erasure channel of Section 0.1 with a common alpha_t for all positions and tokens, alpha_0 = 1, alpha_1 = 0. Let the model be
`p_theta(z_s | z_t) = prod_i q(z_s^i | z_t^i, x^i <- mu_theta^i(z_t, t))` with mu_theta zero on m and copying unmasked tokens, and let p_theta(x) be the marginal at t = 0 of this reverse chain
in the limit of infinitely many steps, started from the all-mask state. Then
```
-log p_theta(x)  <=  L_inf(x) = int_0^1  w(t)  E_{z_t ~ q(.|x)} [ sum_{i : z_t^i = m}  -log mu_theta^i(z_t,t)[x^i] ]  dt ,    w(t) = -alpha'_t / (1 - alpha_t) .
```
Same weight in other coordinates: `= int_0^1 (dlambda/lambda) E_{mask each position w.p. lambda}[ sum_masked CE ]`; `= sum_{n=1}^L (1/n) E_{S: n masked, uniform}[ sum_{masked} CE ]` for a time-free mu (Zheng Prop 3.1; RADD Eq C.17). For the linear schedule alpha_t = 1 - t the weight is 1/t (LLaDA Eq 3).
Locations: MD4 Eq 5 (identical up to sign convention: `alpha'/(1-alpha) * log mu` is `w * (-log mu)`); MDLM Eq 13; Zheng Eq 6; LLaDA Eq 3 for alpha_t = 1 - t.

Where the pieces come from. (i) Per-step KL collapses to a masked cross-entropy because unmasked tokens cannot move and the clean token is never m: `KL = -((alpha_s - alpha_t)/(1 - alpha_t)) 1[z_t = m] x^T log mu_theta` (MD4 App D Eq 19; MDLM Eq 10 vs the unsimplified Eq 11). (ii) Divide by (t - s) and let s -> t: `-alpha'_t/(1-alpha_t)` (MD4 App D; MDLM B.2 Eq 46). (iii) Reconstruction term 0 (carry-over: MDLM Eq 48; MD4 App D: `-(1-alpha_{t(1)}) log m -> 0`). (iv) Prior term 0 if alpha_1 = 0 (MD4 App D); if alpha_1 > 0, MD4 App E uses a modified prior with KL = alpha_1 log m.

Assumptions needed, each from the cited text: common schedule across positions and token values (a state-dependent schedule changes the loss to MD4 Eq 12); factorised reverse kernel (MD4 footnote: the true reverse transition factorises in the continuous-time limit); SUBS properties (MDLM Sec 3.2.3: without them the bound is the messier Eq 11 and the network must learn them); alpha monotone and invertible.
Schedule invariance: with lambda or gamma = log(1 - alpha) as the integration variable the integrand has unit weight, so alpha_t affects the bound only through its endpoints (MD4 Sec 3 log-SNR form; MDLM Sec 3.4, E.1.1). The schedule matters for the variance of a Monte Carlo estimate over t and for the sampler grid (MD4 Sec 4).

Bound versus equality.
- Bound: a variational (ELBO) bound in the usual sense; the gap is the KL between the path measure of the forward chain conditioned on x and the path measure of the model reverse chain (INFERENCE: stated for SEDD's path-measure proof, Eq 26-27, not as a theorem for the masked form).
- The bound is for the infinite-step model. For a T-step model the matching bound is `L_T >= L_inf` (MD4 Sec 3; D3PM Eq 1 in discrete time), and the T-step sampler's distribution is a different distribution from p_theta(x) above. So `L_inf` does not bound the likelihood of a finite-step parallel sampler; the difference `L_T - L_inf` is where parallel-factorisation error enters (INFERENCE; supported by ARDM App C, Campbell App G, Zheng Sec 4.3).
- Tightness at the optimum: Zheng Prop 3.2 gives `mu_{theta*} = E[x_0 | z_t]`; at that point the reverse kernel equals the true time reversal of the forward chain, so the model is exact (INFERENCE from the standard argument; no theorem in the nine states "E_data[L_inf] = entropy of the data").
- Unconditional on text length: the bound is for a fixed length L (Zheng Sec 4.2 sampler draws a fixed-length sequence; MDLM Sec 4.2 states that Shi and Ou are "restricted to sample sequences of a fixed length").
- Training with other positive weights w_n (Zheng Prop 3.2) or no weight (MaskGIT) is a surrogate with the same minimiser in the nonparametric limit, not a bound; Campbell App D Prop 9 shows the unweighted denoising cross-entropy is an upper bound on a negative ELBO (looser).
- D3PM discrete-time version (Eq 12) has weights 1/t with Bernoulli masking at discrete times; it is "not exactly identical" to uniform-k MLM (D3PM Eq 13-14) because k is a mixture of binomials.

Number check (DERIVED, verified): with the linear schedule, uniform t gives a *uniform* count of masked positions: `int_0^1 C(L,k) lambda^k (1-lambda)^{L-k} d lambda = 1/(L+1)` for each k. For other schedules the count law under uniform t is not uniform, and the weight w(t) compensates (invariance above). So "reveal law" alone does not determine the objective: the pair (law, weight) does.

### 2b. Removing the time variable

Four distinct statements, with different proofs and conditions:

B1 (objective, exact). The time integral can be done in closed form against the binomial count: `L_inf = sum_{n=1}^L (1/n) E[...]` with the network replaced by the Beta-ensemble mu_bar (Zheng Prop 3.1, Eq 7-8). Needs alpha_0 = 1, alpha_1 = 0. For a time-free network no ensemble is needed. RADD obtains the same with lambda as variable (Thm 2 route, Eq C.15-C.18) and needs sigma-bar(T) = infinity.
Consequence: with a time-conditioned network the NELBO uses the log-average mu_bar (Zheng Eq 8) while the sampler evaluates the network at sampled times (an arithmetic mixture); by Jensen the log-average CE is at least the CE of the arithmetic mixture (INFERENCE; Zheng only calls it "an ensemble").

B2 (optimal predictor). The minimiser of the NELBO is `E[x_0^{(l)} | x_t]` and it depends on x_t only through the unmasked tokens: Zheng Prop 3.2 (Eq 9, 20-22, via `q_{0|t}(x_0|x_t) = q~_{0|N(x_t)}(x_0|x_t)`); RADD Prop 1 (Eq B.13) and Eq E.1: `p_{0|t}^i(x_0^i | x_t) = p_0(x_0^i | x_t^UM)`; MD4 Sec 3 (citing Ou et al.); LLaDA App A Eq 11 (citing Ou et al.). MDLM does not prove it; it omits time and reports Table 12.
Assumptions (DERIVED from the proofs): the corruption is erasure with a common alpha_t; the observed unmasked tokens are uncorrupted, so the mask pattern is observed; the mask pattern is independent of x given t; nonparametric optimum.
Fails for: (i) state-dependent schedules (MD4 GenMD4, Eq 11-12): the masking probability depends on the token value, so the mask pattern is informative about x_0 and the posterior depends on t (INFERENCE; MD4 does not claim time-freeness for GenMD4); (ii) the symmetric channel (Section 2e).

B3 (network without a time input is lossless). Follows from B2 only in the nonparametric limit; MDLM Table 12 (23.21 vs 23.05 PPL) is the empirical support, and Zheng Sec 4.1 footnote reports no degradation for time-dependent networks with caching, so the time input is not needed for caching either.

B4 (sampler). The positions that unmask in any interval are independent of the network: each masked token unmasks at rate `-alpha'_t/(1-alpha_t)` regardless of mu_theta (Zheng Sec 4.2 "insight" 1 and 2; consistent with MD4 Eq 8, MDLM Eq 84). Consequences: (i) caching when no token changes (RADD Eq 3.4; MDLM Sec 4.1); (ii) first-hitting sampling (Zheng Prop 4.1), which removes empty steps and, with a time-free mu, removes t entirely (token-by-token decoding in uniformly random order).
Caveat: time-removal is a statement about the network input, not about the loss. The loss still integrates over t with weight w(t) (or equivalently over n with 1/n).

### 2c. Equivalence with any-order autoregression: what is and is not equivalent

Objective (proved, with conditions). For a time-free conditional model q_theta(x^i | x^S) with S the unmasked set,
`L_AO(x) = E_{pi~U} sum_{l=1}^L -log q_theta(x^{pi(l)} | x^{pi(<l)})`
equals `L_inf` of Statement A: RADD Thm 2 (chain DSE = t-DCE = lambda-DCE = L_AO, App C), requires sigma-bar(T) -> infinity and conditionals depending only on the unmasked set (not on pi or t); ARDM App C Eq (VLB) gives the same identity from the continuous absorbing process (stated as a claim; the argument is the uniform order of decay times plus KL(q(tau)||p(tau)) = 0); Zheng Prop 3.1 gives the n-form `L * E_{n~U{1..L}} (1/n) E[...]` which is ARDM's `D * E_t L_t`; MD4 Sec 5 states it informally and credits ARDM App C and Ou et al.; LLaDA Eq 15 asserts it without proof.
Identity used: `sum_k (1/k) E_{|M|=k, uniform}[ sum_{i in M} ell_i(S) ] = E_pi sum_l ell_{pi(l)}(pi(<l))` for any set-indexed losses ell (DERIVED; checked numerically on a toy joint, `primer-foundations-checks.py`, 2.6702 vs 2.6702).

Not equivalent (each with its reference):
1. Likelihood semantics. L_AO is a Jensen bound on `log E_sigma p(x | sigma)` (ARDM Eq 2); conditionals for different sets S are not required to be consistent with one joint (RADD after Thm 2: `q_theta(x_0; pi)` is "inconsistent in general"; the model is an ensemble of orders). The exact NLL of that mixture is given by neither objective. Autoregression has a single order and an exact likelihood.
2. Sampler. The diffusion sampler equals an AO-AR sampler (uniformly random order, token drawn from the conditional given the revealed set) only for exact event-driven simulation of the continuous-time reverse chain: the first-hitting sampler (Zheng Prop 4.1) or T -> infinity ancestral sampling. With finitely many steps several positions unmask per step with independent draws; that is not AO-AR sampling and carries a factorisation cost (ARDM App C, Eq 3-4 and the dynamic-programming schedule; Campbell App G; Zheng Sec 4.3 "approximation method"; MD4 Sec 4 "conflicts"). ARDM's per-step accounting (`k L_t` vs `sum L_{t+i}`) quantifies it for random orders.
3. Model class and architecture. AR uses a causal mask and one order, giving all conditionals in one pass; AO-AR/masked diffusion uses a bidirectional network with mask inputs, one pattern per pass (ARDM: no causal masking; LLaDA Sec 2.2: no causal mask). Time-conditioned networks add a log-ensemble over times (Zheng Prop 3.1).
4. Autoregression inside the diffusion picture. D3PM Sec 4 realises AR as absorbing diffusion with a deterministic, left-to-right, non-independent forward process (product-space recast). That is a different forward process from the independent-masking channel, not just a different reveal law applied to the same channel.
5. Gradient noise. The three weights (t-form, lambda-form, n-form with exactly n masks) have the same expectation but different variance (LLaDA App A.2: Eq 12 vs Eq 14; Zheng Sec 3.3 low-discrepancy sampler).
6. Length. Masked diffusion and AO-AR in these papers generate a fixed length L (MDLM Sec 4.2; Zheng Sec 4.2); LLaDA treats length as a hyperparameter and removes tokens after EOS.

Expected-cost identity (DERIVED, checked numerically): for exact conditionals and uniform orders, `k L_t - sum_{i=0}^{k-1} L_{t+i}` (ARDM's cost of generating k tokens in parallel) equals `E_sigma TC(x_{sigma(t..t+k-1)} | x_{sigma(<t)})`, the conditional total correlation (0.052089 vs 0.052089 on the toy joint). So ARDM Eq 3-4 already contain the framework's E_fact for random orders (Section 3 below).

### 2d. Ratio (concrete score) versus clean-marginal parameterisation

Statement D (absorbing channel, Q_t = sigma(t) Q^absorb, alpha_t = e^{-sigma-bar(t)}). For a masked position i and v != m:
`s_t(z_t)_{(i,v)} = p_t(z_t^{i<-v}) / p_t(z_t) = [alpha_t / (1 - alpha_t)] * p_0(x^i = v | z_t^U)`.
Proof: RADD Prop 1 Eq B.13 and Thm 1. Single-token versions: MD4 Prop 1 Eq 9 (H.3 proof via Bayes), Zheng Eq 55, MDLM Eq 73 (for a model with SUBS). Other rows (MDLM Eq 74-77): `s(m)_m = 1`; for z^i != m, `s_{m} = (1-alpha_t)/alpha_t`, `s_{z^i} = 1`, other entries 0. Row constraint `sum_{v != m} s_t(m)_v = alpha_t/(1-alpha_t)` (MD4 Eq 9, 27). Hence the map between `s` and `mu` is `s = [alpha_t/(1-alpha_t)] mu`, linear and invertible given t: for the true score the two parameterisations carry the same information.
Training equivalence: substituting `s_theta = [alpha/(1-alpha)] mu_theta` into DWDSE (SEDD Eq 10) gives MD4 Eq 4 exactly: MD4 H.3 Eq 22-27; Zheng D.3.1 Eq 57-59 (uses `sum_x mu_theta(m,t)_x = 1` and `I(a,0) = a`); MDLM C.5 Eq 85-89; RADD C.1. Sampler equivalence: Tweedie tau-leaping equals the mean-parameterised ancestral step (RADD E.2); Euler equals it only for the linear schedule (Zheng D.3.2; RADD D.4).
Restrictions (each is a place where the framework's sentence needs a qualifier):
1. Erasure channel only; position-independent, token-independent schedule; Hamming-1 neighbours; entries at masked positions (the rest are trivial or zero).
2. Sequence-level proof is RADD Thm 1; MD4 Prop 1, Zheng and MDLM prove the single-token case (Zheng states the sequence case follows from factorisation; MDLM C.3 treats one token).
3. A learned SEDD network is unconstrained: nothing forces `sum_v s_theta(m)_v = alpha/(1-alpha)`; MD4 H.3 says this can make the learned reverse model incompatible with the forward process, and SEDD's own scaling trick (App C.2) is explained by RADD Thm 1. So "same information" is exact for the true score and for a constrained network, not for an arbitrary SEDD network.
4. The "marginal" is p_0(x^i | z^U): one position given the unmasked tokens, with the other masked positions summed out. It is not the unconditional marginal.
5. The scalar `alpha_t/(1-alpha_t)` is the odds of a position being unmasked (the SNR of MD4's log-SNR coordinate).

### 2e. How uniform (symmetric) discrete diffusion differs

Facts in the papers: D3PM Sec 3.1 and A.2.1 (uniform `Q_t = (1-beta_t) I + (beta_t/K) 11^T`, stationary distribution uniform; reverse via Eq 4); MDLM Eq 6-7 (general pi, posterior with full support); Campbell Sec 4.1 (uniform rate `11^T - S Id`) and Prop 3 (posterior given the whole state); SEDD Eq 15 and Table 1 (SEDD Uniform worse than SEDD Absorb in every column quoted above); D3PM Table 1 (text8 1.61 vs 1.45 bits/char) and LM1B (uniform "significantly worse"); ARDM (absorbing is the best-performing discrete diffusion for text, citing D3PM). Everything below in "Differences" is DERIVED or INFERENCE unless a reference is given.

Differences:
1. Revisability (by construction). The posterior `q(z_s^i | z_t, x)` of the uniform channel puts mass on every token (MDLM Eq 7 with pi uniform), so the reverse step can change any position at any step; the absorbing posterior is the identity on unmasked positions (MDLM Eq 8). No carry-over or zero-mask structure exists, so MDLM's SUBS simplification does not apply.
2. No cross-entropy collapse. The per-step KL keeps terms on all K categories (the unsimplified form, MDLM Eq 11, is the template); the continuous-time bounds are the general CTMC ones, Campbell Eq 13 and SEDD Eq 10, which hold for any rate matrix. The MD4/MDLM masked cross-entropy with weight w(t) is specific to the erasure channel.
3. Ratio versus posterior. From Campbell Eq 12 and the uniform marginal `q_{t|0}(j|x_0) = a delta_{j,x_0} + b`, a = alpha_t, b = (1-alpha_t)/K, the ratio for a Hamming-1 neighbour (u -> v, u != v) at one position is
   `s = [b/(a+b)] P(u) + [(a+b)/b] P(v) + 1 - P(u) - P(v)`, with P(.) = q(x_0^i = . | z_t),
   an affine function of two posterior entries, not a scalar multiple of one (checked by enumeration on a single token: 0.84449 vs 0.84449). Contrast with the erasure channel, `[alpha/(1-alpha)] P(v)`. Here P conditions on the whole z_t, as in Campbell Eq 17.
4. Time cannot be dropped (INFERENCE). RADD's argument depends on the mask pattern being observed and independent of x. In the uniform channel a token equal to u can be uncorrupted or noise with probability depending on t, so the posterior depends on alpha_t; D3PM, Campbell and SEDD condition on t in all uniform experiments. No paper in the nine proves or claims a time-free result for the uniform channel.
5. No exact any-order autoregressive reading and no first-hitting sampler (INFERENCE). Both arguments rest on each position changing at most once; here a position can change many times, so the caching bound `n(1-(1-1/n)^l)` (RADD, which rests on "once a token transitions from M to unmasked it remains unchanged") and the at-most-L-calls argument do not carry over. ARDM's equivalence is stated only for absorbing diffusion.
6. Parallelism cost. The independent-draw error appears as in the erasure case (Campbell Thm 1 and App G are written for general rates and are the nearest reference), with step size playing the role of tokens per step; SEDD Thm 4.2 gives the optimal tau-leaping step given perfect scores. The Campbell assumption of bounded neighbour ratio is natural for uniform and doubtful for absorbing (INFERENCE).
7. Sampling temperature. Zheng Sec 5 concerns Gumbel categorical sampling in masked diffusion codebases; SEDD's own uniform-vs-absorb generative-perplexity comparison is in its App D (not read).
Gaussian or embedding-space diffusion: none of the nine papers treats continuous embeddings, logits or the simplex (D3PM's discretised Gaussian is a *discrete* transition matrix on ordinal data). Statements about those channels remain at E0 here.

## 3. Verdicts on the three claims at the end of framework-v0.md section 1

### Claim 1. "Masked diffusion reduces to a weighted masked cross-entropy; time can be removed leaving an expectation over the number of masked positions; this equals the any-order autoregressive objective. So masked diffusion, any-order autoregression and autoregression differ in C2 only."
Verdict: CORRECT WITH A STATED RESTRICTION, except that the final sentence is too strong.
- First clause is correct: MD4 Eq 5, MDLM Eq 13, Zheng Eq 6; conditions in 2a (common schedule, alpha_1 = 0, SUBS structure, infinite-step model).
- "weight determined by the schedule": true in the t-coordinate, w(t) = -alpha'_t/(1-alpha_t). After time is removed the weight is 1/n and does not depend on the schedule at all (Zheng Eq 7; RADD Eq C.17); the schedule only changes variance and the sampling grid (MD4 Sec 3-4; MDLM Sec 3.4).
- Time removal and equality with the AO-AR objective: RADD Thm 2 (needs sigma-bar(T) -> infinity, conditionals depending on the unmasked set only); Zheng Prop 3.1; ARDM App C.
- Restriction on "differ in C2 only": the training objective is shared, but the AO-AR objective is a Jensen bound on a mixture with order-inconsistent conditionals (RADD after Thm 2; ARDM Eq 2), the samplers coincide only in the exact event-driven limit (Zheng Prop 4.1), and the model class differs (causal single-order network vs bidirectional mask network). Autoregression as a special case of the same *forward process* needs D3PM's deterministic non-factorised process (D3PM Sec 4). The framework should say: same objective, same exact-limit sampler, different C2 and different model class.
- Also: C2 as defined ("which sets are clean together") does not fix the objective; (law, weight) does (2a number check; MaskGIT/Zheng Prop 3.2).

### Claim 2. "Ratio and marginal parameterisations of the erasure channel carry the same information: the ratio is the clean-token marginal times a schedule-dependent scalar."
Verdict: CORRECT WITH A STATED RESTRICTION.
- Exact statement and proof: RADD Thm 1 (sequence level); MD4 Prop 1 Eq 9, Zheng Eq 55-56, MDLM Eq 73 (single token). Scalar = alpha_t/(1-alpha_t); "marginal" = p_0(x^i | unmasked tokens).
- Restrictions: erasure channel only; masked positions and Hamming-1 neighbours; common schedule; exact only for the true score or a network constrained to `sum_v s(m)_v = alpha/(1-alpha)` (MD4 Eq 27, H.3). An unconstrained SEDD network can leave the forward-compatible set; RADD explains SEDD's scaling trick as the missing constraint.
- Not true for the symmetric channel (2e item 3: affine in two posterior entries).

### Claim 3. "Gaussian and symmetric channels differ from erasure in C5: every position stays revisable, and commitment happens only at the final rounding or as probability mass concentrates."
Verdict: CORRECT WITH A STATED RESTRICTION (symmetric part verified; Gaussian part not verifiable from these nine).
- Symmetric: every position can change at every step because the reverse posterior has full support (D3PM Eq 3-4; MDLM Eq 7; Campbell Prop 3 uniform rate). Verified.
- Gaussian/embedding/simplex: not treated by any of the nine; E0. "Final rounding" has meaning only for continuous states; in the uniform channel the state is always a token and no rounding occurs.
- "Differ in C5" is incomplete: the symmetric channel also changes C1 (what the state reveals: no mask flag, so the model cannot tell which tokens are corrupted), C3 (the posterior depends on t, 2e item 4), the form of the bound (2e item 2), and removes the time-free parameterisation, the AO-AR equivalence and the first-hitting/caching sampler (2e item 5). Revision in the erasure channel is available only by adding remasking, which is not part of the reverse of the forward chain (LLaDA Sec 2.4: random remasking is the principled rule; its default low-confidence rule is a departure).

### Other corrections to framework-v0 sections 1-2 found during reading
1. Section 1, C1: the symmetric channel is `alpha_t x + (1 - alpha_t) uniform`, so the probability of the clean token is alpha_t + (1-alpha_t)/K (MDLM Eq 6; D3PM A.2.1), not alpha_t.
2. Section 1, C3: "ratio or concrete score" equivalence is erasure-only (Claim 2). "Velocity of a probability path" is not treated by the nine: unverified.
3. Section 1, C5 table row "never (plain absorbing)": correct for committed tokens. LLaDA's remasking acts on tokens *predicted in the current step*; Alg 4 and 5 both take the argmax (Alg 4 line 4: "greedy sampling"), so the LLaDA sampler is not a sample of p_theta even with random remasking. That is E_sel (Section 2 of the framework), not C5.
4. Section 2, E_fact attribution. The identity `E_fact = E[TC(x^{A_n} | z_n)]` is, for random orders, ARDM Eq 3-4 (the cost `k L_t` vs `sum L_{t+i}`), and I verified it equals the conditional total correlation (2c). Nearby results: Campbell Thm 1 (TV bound with a tau-leaping term growing with step size and dimension) and App G (the discrete-time multi-dimensional kernel silently assumes independence), SEDD Thm 4.2 (factorised draw is KL-optimal among tau-leaping strategies given perfect scores), Zheng Sec 4.3 (parallel decoding is an approximation), MD4 Sec 4 (conflicting tokens in one step). Not found in any of the nine: the name "total correlation", or a decomposition covering state-dependent (adaptive) policies. Algebra check on the chain rule: for an A_n that is a function of z_n only and independent draws, `KL(q||p) = sum_n E[TC] + sum_n sum_{i in A_n} E[KL]` is an exact equality (DERIVED); for randomised A_n independent of unrevealed tokens it is an upper bound by convexity of KL (DERIVED). The independent novelty audit is another agent's task.
5. Section 2, E_sel sources: Zheng Prop 5.2 (truncated Gumbel is equivalent to lowering the temperature and gives position-dependent unmasking), MD4 Sec 4 (generative perplexity "can be misleadingly reduced by lowering sample diversity"), SEDD Sec 5.3.1 (generative perplexity "can easily be hacked", wording from the text I read), LLaDA Alg 4/5 (greedy).
6. Section 2, "Revision removes nothing from the budget by itself": consistent with Campbell Prop 4 (predictor-corrector with rate R + R^) as the only corrector in the nine. Not otherwise tested.

## 4. Disagreements and gaps among the nine papers

1. SEDD (Sec 2.2) says the mean-parameterised objective "breaks down in continuous time". MD4 Eq 4 and MDLM Eq 12 give a tractable continuous-time mean-parameterised objective for the absorbing case, and show it equals the score-entropy objective under the constraint of 2d. SEDD's statement is therefore limited to non-absorbing or unsimplified settings.
2. SEDD's learned score is unconstrained; MD4 H.3 argues it can be incompatible with the forward process. RADD Thm 1 supplies the missing constraint. Empirical size of the effect: not extracted.
3. MDLM drops time empirically (Table 12) without proof; Zheng and RADD prove optimality of a time-free predictor; RADD notes MDLM's approach "lack[s] a theoretical foundation" and keeps the time-input layers.
4. Single-token versus sequence statements: MD4 Prop 1, MDLM C.3 and Zheng D.3 are single-token (Zheng asserts extension); RADD Thm 1 is the sequence-level statement.
5. MD4 and MDLM claim the continuous-time ELBO is tighter than any finite-T bound; neither proves monotonicity (MD4 App D shows the limit; MDLM Sec 3.4 cites Campbell).
6. ARDM App C is a derivation introduced with "We claim"; RADD calls its own proof rigorous and says Austin et al. did not prove the link. MD4 credits ARDM App C and Ou et al.
7. LLaDA states the upper bound (Eq 4) and the AO-ARM equivalence without proof, citing MD4, MDLM, RADD.
8. D3PM and SEDD report uniform worse than absorbing; no paper in the nine isolates why beyond the structural points in 2e.

## 5. Stated and unstated limitations

Stated by the papers. D3PM: no continuous-time ELBO (my reading of A.5; no limitations section read). Campbell: the bound is not expected to be tight and its constants are impractical to compute; Assumption 3 holds only approximately (Sec 4.5, B.5). SEDD: "still a large gap with modern large language models" (Sec 6). MDLM: no limitations stated in its conclusion (Sec 7). MD4: masked diffusion is not yet competitive with AR on text8; GenMD4 can overfit, transfers worse zero-shot, and inference with a state-dependent schedule is harder (Sec 8). RADD: trained at GPT-2 scale only; "can only generate full-length outputs" (Sec 6); the DSE bound has "an unknown gap" (Sec 2.1). Zheng: its text experiments may favour AR models; masked models may be the better practical choice (Sec 7); batched caching loses its NFE bound (Sec 4.1). ARDM: a gap to single-order autoregression remains; discrete variables only; optimised for likelihood, not sample quality (Sec 6). LLaDA: generation length is a user hyperparameter; AR comparison limited to under 10^23 FLOPs; no KV cache; sampling algorithms "remain preliminary"; no reinforcement-learning alignment (Sec 5).
Unstated (mine). (i) The bounds are for the infinite-step model; practical samplers are finite-step and mostly argmax or low-temperature (Section 2a). (ii) Time-free and AO-AR equivalences are nonparametric-optimum statements; finite networks only approximate. (iii) State-dependent masking and non-absorbing channels fall outside the time-free and AO-AR results. (iv) Fixed-length assumption. (v) Exa-sourced texts are unversioned.

## 6. Provenance and reproducibility

- Local texts: `research/sources/md/2107.03006.md`, `2409.02908.md`, `2502.09992.md` (from cached HTML via markitdown); `research/sources/md/arxiv-<id>-exa.md` for 2205.14987, 2310.16834, 2406.07524, 2406.04329, 2406.03736, 2110.02037 (Exa fetch of the PDFs; ARDM from arxiv.org/html v2). Each fetch was made once; no HTTP 429 occurred.
- Numerical checks: `research/review/dossier/primer-foundations-checks.py` (toy L=3, K=3 joint): masked-CE vs AO-AR identity (2.6702319881912624 vs 2.670231988191262); Beta integral and uniform count under the linear schedule (1/(L+1)); uniform-channel affine ratio formula (0.8444886955722792 vs 0.844488695572279); absorbing ratio (0.03435210334969329 both); ARDM parallel cost equals conditional total correlation (0.05208933622800993 vs 0.052089336228009785).
- Ledger rows: none added (the brief did not request any).
