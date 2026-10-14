---
agent: paper-reader
date: 2026-10-14
brief: Sampling-theory chapter of the DLM primer, built from the primary papers, used to check and attribute framework-v0 section 2 (error budget) and section 4 (P1-P5)
sources_examined:
  - arXiv:2510.04767 (ParallelBench, v2 cached HTML)
  - arXiv:2602.00286 (Zhang et al., Generation Order and Parallel Decoding; fetched once from arxiv.org/html, v1)
  - arXiv:2502.09622 (Feng et al., v2 cached)
  - arXiv:2505.21400 (Li and Cai, NeurIPS 2025; fetched once from arxiv.org/html, v2; the ID was resolved by title search, it is not in the corpus)
  - arXiv:2502.06768 (Kim et al., v3 cached)
  - arXiv:2503.00307 (ReMDM, cached)
  - arXiv:2202.04200 (MaskGIT; fetched once, sampler section and ablation only)
  - arXiv:2502.09992 (LLaDA, sampling section, Alg. 4-5, App. B.4; cached)
  - arXiv:2409.02908 (Zheng et al., time-agnostic MDM, sections 3-6; cached)
  - arXiv:2505.24857 (Ben-Hamu et al., EB-sampler; cached)
  - extra, needed for (c) and (d): arXiv:2604.00375, 2606.12232, 2604.02718, 2605.10518, 2410.08709 (Di4C), 2507.15897 (ReDi; fetched once)
coverage: |
  Read in full or in the relevant range: every theorem, lemma, proposition and proof listed below, the sampler
  descriptions and the experiments cited. NOT read: the experiment sections of Feng, Kim, Zhang and Li-Cai beyond the
  tables cited; Feng Lemmas D.4-D.12 and E.2-E.9 (proof outline only); Li-Cai section 4.3 (proof of Theorem 2) beyond its
  first lines; Kim App. B.4 (hardness proof, conditional on a conjecture); the experiment sections of 2604.00375 and
  2606.12232 (abstract plus the passages cited); ReDi Theorem 1 proof. Fast-dLLM, Pynadath et al. 2025, Yoo-ReDi's
  follow-ups and Liu et al. 2025 (cited by 2605.10518) were not read. Cached copies are the latest versions the corpus
  held; the version numbers above are the ones read.
evidence_rule: "E2 = the paper's text read. 'The paper reports X' is never 'X is true'. [V] = verified here by exact enumeration (script and log beside this file)."
---

# Sampling theory of diffusion language models (primer chapter) and audit of framework-v0 section 2

Tags: **[S]** source fact with location, **[I]** inference, **[H]** hypothesis, **[V]** verified here.

## 0. Bottom line

1. [S] The central identity of framework-v0 section 2, KL(q||p) = sum over steps of (expected conditional total correlation of the co-committed tokens + marginal model error), is already published, including for state-dependent adaptive policies with equality for deterministic ones: Ben-Hamu et al. (EB-sampler, 2505.24857) Eq. 7 and App. A.1 Eq. 10-13. For fixed or data-independent random partitions it is in Feng et al. (Lemma D.2, D.3), ParallelBench (proof of Thm 1, Eq. 6-11), Li-Cai (Eq. 17 and 23) and Zhang et al. (Eq. 16, 18). Nothing in the displayed identity or its randomised-policy bound is new.
2. [V] The identity is correct as stated for state-dependent deterministic policies (residual 1e-16 on exact enumeration, learned marginals, sampled values) and the randomised bound holds. It fails, by a large margin, for sample-dependent selection (sample all masked positions, keep the most confident samples): with exact marginals and one token per step the KL was 1.29 nats and the entropy fell from 3.50 to 2.16 nats on a toy distribution. That is the E_sel term and it is not in the identity.
3. What the literature does not contain (not found, not "does not exist"): a formal statement of E_sel as a distortion of the output law relative to exact marginals; an E_approx term for caches; the global (summed) form of the identity for uniform or Gaussian channels (the per-step quantity TC(z_s|z_t) is defined in ReDi and IMDM, not summed into a KL budget); any measurement of cross-modal total correlation.
4. Two statements in framework-v0 are wrong or incomplete as written: P2 (a lower output entropy does not by itself indicate E_sel, because removing E_fact also lowers entropy) and the lever table (ordering also changes E_learn; Kim et al., Zhang et al., EB-sampler). P3's second clause is contradicted by ReMDM Table 1. Details in section 5.

## 1. Setting and notation used in this chapter

x = (x^1..x^L) ~ q. A sampler commits a set A_n of positions at step n, given the revealed state z_n (positions and values so far). With the erasure channel the state is a partially filled sequence. The predictor gives marginals p_theta(x^i | z_n) for every masked i. Sampling draws the tokens of A_n independently from these. Terms used by the papers: "mask size schedule" s_t (Li-Cai), "partition into T sets S_i" (ParallelBench), "blocks B_m" (Zhang), "ordered partition z and policy phi" (EB-sampler), "reverse process tau" (Feng). Conditional total correlation TC(Y|Z) = sum_j H(y_j|Z) - H(Y|Z) = KL(joint || product of marginals) (ParallelBench Eq. above (1); Zhang Eq. 15; EB-sampler Eq. 7 calls it "joint dependence error").

The one-line algebra behind everything (derived here, E2-consistent with EB-sampler Eq. 11-13): for any joint P over Y and any product Q = prod_j Q_j,

    KL(P || Q) = TC(P) + sum_j KL(P_j || Q_j).

Apply it per step under the chain rule along the realised path and sum.

## 2. What each paper proves (as stated), assumptions, proof technique

Order of the "assumptions" field: predictor (exact or learned) / order rule / value rule / divergence and direction.

### 2.1 ParallelBench (Kang et al., 2510.04767 v2), section 4 and App. A
- Thm 1 (Eq. 2): for T-step decoding with a partition Y = S_1 u ... u S_T, min over theta of KL(P_data || P_theta) >= L_T := sum_i E_{S<i ~ P_data}[C(S_i | X, S<i)], with equality when every committed token's conditional matches the data conditional. Remark 1: L_1 = C(Y|X), L_|Y| = 0.
- Thm 2 (App. A.2, Lemma 1 subadditivity of conditional TC): the optimal bound L*_T over partitions is non-increasing in T. Thm 3 (A.3): same for input-dependent partitions (partition may depend on X, not on revealed values).
- Assumptions: any (the bound is a minimum over theta; equality case = exact conditionals) / partition fixed in advance (Thm 1) or a function of X only (Thm 3); not a function of revealed values / values sampled from the factorised model / forward KL(P_data || P_theta).
- Technique: chain rule over the partition (Eq. 6-11), then the one-step bound KL >= TC from Huang et al. (2022) (Eq. 1, Eq. 12), then swap min and sum (Eq. 13-15). Monotonicity: split the last set in two and apply Lemma 1.
- [I] The paper's section 3 describes threshold (adaptive) unmasking as a decoder class, but Thm 1-3 do not cover it: the partition in Eq. 7 is state-independent. The exact two-term split is implicit in Eq. 11-12 but never written.

### 2.2 Zhang et al. (2602.00286 v1), sections 3-5 and App. A, C
- Lemma 4.1 (Eq. 7): for any order pi, KL(p_theta^pi || p_data) = sum_t E_{prefix ~ p_theta^pi}[eps_theta(prefix)], eps_theta(h) = KL(p_theta(.|h) || p_data(.|h)). Reverse direction, expectation under the model's own rollout.
- Assumption 4.2 (Eq. 10) and Eq. 11: local error bounded by alpha * conditional entropy + lambda * earlier error + b; this yields weights W_t = alpha(1+lambda)^(T-t) and the claim that Easy-First is "risk-averse" as lambda grows. A modelling assumption; the paper cites App. B for empirical support (not read).
- Eq. 16 (forward) and Eq. 18 (reverse): for a fixed block partition with the product proposal of the true conditionals, KL(p||p_B) = sum_m E_{x_Pm ~ p}[KL(p(x_Bm|x_Pm) || prod_i p(x_i|x_Pm))] ("forward TC") and KL(p_B||p) = sum_m E_{x_Pm ~ p_B}[reverse TC]. Equalities, proofs C.1 (Eq. 39-46).
- Prop 5.1 (Eq. 19): any accept-reject procedure producing an exact block sample from a product proposal needs in expectation at least exp(forward TC) proposals (proof C.2, standard rejection-sampling bound).
- Lemma C.1, Cor C.2, Lemma C.3: reverse KL is infinite under conditional support mismatch; reverse TC can be unbounded; one-sided bound between reverse KL and incoherence probability.
- Prop C.5 (Eq. 72): under Assumption C.4 (the remasking kernel puts mass outside the true support) reverse KL stays +inf for every finite number of iterations. [I] Conditional on an assumption that is stated for one remasking step; the extension "for any finite n" is asserted ("the same argument applies"), not shown.
- Assumptions: exact conditionals in section 5 (model error handled separately and only for sequential decoding in section 4) / fixed blocks, fixed order pi / values sampled / both KL directions (forward for information loss, reverse for sampling risk).
- The paper says its analysis is formal for AR-compatible masked diffusion and qualitative otherwise (section 2.2).

### 2.3 Feng et al. (2502.09622 v2), section 4 and App. C-E
- Assumption 4.1: every per-token conditional of the learned reverse model is within epsilon_learning in KL of the data reverse process, for all t and x_t.
- Thm 4.2 (Eq. 6): for an n-gram language q, any epsilon > 0, any L above O((n-1)/epsilon^(n+0.5)), there is a masking schedule with N = O((n-1)/epsilon^n) steps such that log TER(p) <= log TER(q) + epsilon_learning + 4 epsilon log|V|. TER = exp of per-token cross-entropy E_q[-log p(x)/|x|] (Eq. 4), so this is a bound on KL(q||p)/L.
- Thm 4.3: for any HMM q and any masking schedule, with epsilon_learning < O(delta/L) and enough steps, SER(p) <= delta (SER = probability mass outside the support of q, Eq. 5).
- Thm 4.4: there is an HMM over 16 symbols such that, for any reverse model satisfying Assumption 4.1 with epsilon_learning < 1/128 and any masking schedule, SER(p) > 1/2 when N = C L for a constant C (as printed; the surrounding text says steps must scale at least linearly in L, so "N <= C L" is probably intended). App. E.3 extends it to ReMDM.
- Assumptions: learned with uniform small KL / random masking schedule (positions drawn independently of the data) / values sampled / TER is forward KL up to the entropy of q; SER is a support-mass criterion.
- Technique: Lemma D.2 (Jensen over the random reverse process: KL(q||p) <= E_tau KL(q||p_tau)), Lemma D.3 (chain rule per step for a fixed tau), bound each step by counting dependent token pairs given the "separators" (n-1 consecutive already-sampled tokens), probabilistic bounds on the count (Lemma D.10, D.11, C.1). Thm 4.4: a constructed HMM with pairwise-dependent tokens in intervals; the probability that two dependent positions fall into the same step is bounded below (Lemma E.5).
- Note: Li-Cai (Section 3.1) says Feng's TER bound scales as ((n-1)/T)^(1/n) log|X| and is vacuous for realistic n; I read Feng's Thm 4.2 and it is consistent with that rate; I did not re-derive Li-Cai's "vacuous" threshold.

### 2.4 Li and Cai (2505.21400 v2, NeurIPS 2025), sections 2-4
- Setting: uniformly random mask sets with sizes s_1..s_T (sum = L) chosen in advance, independent of the data; product mask predictor; values sampled from it (Eq. 6).
- Def 1 / Eq. 7: epsilon_train = expected masked cross-entropy gap between the optimal predictor and the learned one, weighted so that tau = t has probability s_t/L.
- Thm 1 (Eq. 8): E_M[KL(p_X0 || p_{Y0|M})] <= ((2^ceil(log2 s_max) - 1)/L) * sum_i I(X^i; X^-i) + epsilon_train. Cor 1 (Eq. 9): balanced schedules give C_1 * (sum_i I)/T + epsilon_train, C_1 = T s_max / sum_t s_t. Eq. 11: the unconditional-law KL is at most E_M of the above, by convexity of -log (since p_Y0 = E_M[p_{Y0|M}]).
- Thm 2 (Eq. 12-13): refined multi-scale mutual-information upper bound, and a lower bound with factor s_max/(16 L) for some schedule with s_t of order s_max. The paper stresses the lower bound is not universal (s_1 = s_max, then s_t = 1 gives negligible error).
- Technique: (i) exact decoupling E_M[KL(p||p_{Y|M})] - E_M[KL(p||p_{Y*|M})] = epsilon_train (Eq. 17) with Y* run on the optimal predictor; (ii) E_M[KL(p||p_{Y*|M})] = sum_t E_M[KL(p(X.D_t | X.W_t) || product)] (Eq. 23); (iii) recursion eps(s_max) <= eps(ceil(s_max/2)) + (s_max/2L) sum_i I(X^i;X^-i) (Eq. 19) by splitting each revealed set in two halves, the chain rule for KL and I(X;Y|Z) + I(X;Z) = I(X;Y,Z) (Eq. 24-26); eps(1) = 0.
- Remark 1: unmasking by lowest conditional entropy is motivated through I(X;Y|Z) <= H(X|Z); the theorem is for random masks, so this is a heuristic, not a guarantee.
- Assumptions: learned (epsilon_train) or exact / random order, data-independent / values sampled / forward KL averaged over masks.

### 2.5 Ben-Hamu et al. (EB-sampler, 2505.24857; the version read is dated 24 Aug 2026), section 5 and App. A.1
- Setup (Eq. 5-6): any adaptive sampler phi(z_i | x^{z<i}, z<i) choosing the next set from the revealed state; p_phi(x,z) = prod_i [prod_{l in z_i} p_theta(x^l | x^{z<i})] phi(...); q_phi(x,z) = q(x) prod phi, hence sum_z q_phi(x,z) = q(x).
- Eq. 7 and App. A.1 Eq. 10-13: KL(q(x) || p_phi(x)) <= KL(q_phi(x,z) || p_phi(x,z)) = sum_i E_{q_phi}[ sum_{l in z_i} KL(q(x^l|x^{z<i}) || p_theta(x^l|x^{z<i})) (model error) + KL(q(x^{z_i}|x^{z<i}) || prod_l q(x^l|x^{z<i})) (joint dependence error) ]. The inequality is the ELBO/data-processing step; it is an equality when phi is deterministic (App. A.1, "KL divergence equality", Eq. 14-15).
- Eq. 8: joint dependence error <= sum_l H(q(x^l|.)) - max_l H(q(x^l|.)). Eq. 2 / Eq. 9: the EB rule picks the largest sorted prefix whose entropy sum minus entropy max stays below gamma.
- Assumptions: exact or learned predictor / adaptive, state-dependent, possibly randomised phi / values sampled from p_theta in the theory / forward KL.
- [S] The experiments use zero temperature ("temperature was unhelpful for LLaDa", section 6, Experimental setting), so the theory (sampled values) and the experiments (argmax values) differ; the effect of that on the decomposition is not discussed. Abstract: "roughly 2-3x" acceleration; Table 1 (Dream 7B, MBPP) shows 2.05x-6.00x NFE speed-ups depending on the evaluation scheme; the main text in the cached copy also says "22-44x", which conflicts with both (typo or extraction artefact, unresolved).

### 2.6 Kim et al. (Train for the Worst, Plan for the Best, 2502.06768 v3)
- Prop 2.1 (Eq. 1): the MDM loss is a weighted sum over all infilling masks M of the per-mask cross-entropy; equals the any-order autoregressive loss (App. E.1, building on Zheng et al. 2024 Prop 3.1).
- Prop 3.3 (Example 3.2, sparse-predicate L&O distributions): under the 1RSB cavity prediction (Conjecture B.13), with probability Omega_k(1) over masking, no polynomial-time algorithm solves the resulting masked-token subproblem for masking fractions in the stated window. Also Prop B.2 (sparse parity) and B.5 (random slab).
- Section 4: adaptive inference by an "ordering oracle" (Top probability, Top probability margin) selects the position, not the value (section 4.1). Table 1 (L&O-NAE-SAT, N=25..100): 78.06..62.84% vanilla against 93.76..88.91% adaptive. Table 2 (Sudoku): MDM vanilla 6.88%, top probability 18.51%, top margin 89.49%. Table 3 (Zebra): 76.9, 98.5, 98.3%. For text they report generative perplexity and sample entropy "to ensure similar diversity" (section 4.2).
- Assumptions: exact (idealised, Prop 2.1) / learned (hardness of subproblems the learned model faces) / random order in training, state-based position oracle at inference / the text specifies the position rule, not the value rule, for adaptive inference (value rule not verified) / no divergence statement; conditional hardness.
- Technique: reduction of masked-token prediction to planted CSP and a conjectured computational threshold from statistical physics.
- No error decomposition. Relevant here because it shows that an order policy changes which subproblems the model is evaluated on (an E_learn effect at one token per step).

### 2.7 ReMDM (Wang et al., 2503.00307)
- Thm 3.1: with posterior Eq. 6, q_sigma(z_t|x) has the same marginals as ordinary masked diffusion. NELBO Eq. 9: each term increases monotonically in sigma_t, so the MDLM bound (sigma = 0) is tighter than ReMDM's.
- Thm 4.1: Eq. 6 equals an MDLM predictor step followed by a corrector step (Eq. 11). Prop 4.2: the forward-backward corrector is the case sigma_t = (alpha_s - alpha_t)/alpha_t. Prop 4.3: the DFM corrector converts with sigma_t = beta_t (alpha_s - alpha_t)/alpha_t. Prop 4.4: ReMDM is strictly more general (constant-alpha windows).
- Assumptions: algebraic results are exact; the NELBO is for learned x_theta / per-token remask with Bernoulli sigma_t (state-independent), or confidence-weighted sigma per token ("ReMDM-conf", state-dependent) / values sampled; text experiments use nucleus sampling top-p = 0.9 and float64 / ELBO (forward-KL type) only; no sampler-error theorem.
- Technique: DDIM-style non-Markovian posterior with matched marginals and matrix algebra.
- Reported numbers relevant later: Table 1 (OWT, 5000 samples, MAUVE) and Table 5 (App. E.2.2); see P2, P3.

### 2.8 MaskGIT (Chang et al., 2202.04200), section 3.2 and 4.4
- No theorem. Sampler (section 3.2): predict all masked locations, sample a token at each, use the probability of the sampled token as its confidence (unmasked positions get 1.0), keep the most confident, re-mask the rest per a mask-scheduling function gamma (cosine default); "in practice" the re-masking is randomised with temperature annealing for diversity.
- Table 3 / Fig. 8: FID against iterations T has a sweet spot (cosine: 8 to 12 iterations); the authors hypothesise that too many iterations discourage keeping less confident predictions, "which worsens the token diversity"; no diversity measurement is given.
- [I] This is the earliest source I read that uses sample-then-filter selection (confidence of the sampled value).

### 2.9 LLaDA (Nie et al., 2502.09992), section 2.4, Alg. 4-5, App. B.4
- Reverse step: predict all masked tokens, re-mask a fraction s/t. "In principle" re-masking should be random; LLaDA uses low-confidence re-masking, following MaskGIT, "inspired by the annealing tricks" of AR sampling.
- Alg. 4 and Alg. 5 both set r_0 = argmax (comment: "we employ greedy sampling"), and in Alg. 5 the confidence is the probability of that argmax. So the random-remasking baseline is also argmax; the comparison isolates position choice, not value choice.
- Table 9 (LLaDA 8B Base, length = steps = 256, pure diffusion): random re-masking BBH 32.1, GSM8K 21.3, Math 9.2, HumanEval 11.6, MBPP 21.0; low-confidence 45.0, 70.0, 30.3, 32.9, 40.2. The authors "hypothesize" the gain comes from reduced diversity; no entropy or diversity measure is reported.
- One-token-per-step in the sampler ablation ("In all settings, one token is generated per sampling step", App. B.4).

### 2.10 Zheng et al. (Masked Diffusion Models are Secretly Time-Agnostic Masked Models..., 2409.02908), sections 3-6
- Prop 3.1 (ELBO via number of masked tokens), Prop 3.2 (optimal time-independent parameterisation), Prop 4.1 (analytic sampling of the first-hitting time; the "first-hitting sampler"), Prop 5.2 (Eq. 12): closed-form categorical law under truncated-Gumbel sampling with maximum M: pi'_n = pi_n * sum_{i<=n} beta(i), beta >= 0, which amplifies larger probabilities (like lowering temperature) and, in the full sampler, makes unmasking rates depend on the network output.
- Measurements: Fig. 7 (64 samples, steps 100-10000 on OWT-trained AR/SEDD/MDLM): with 32-bit sampling generative perplexity falls with steps but entropy falls too. Table 2 (8 samples, 2048 steps): 32-bit GenPPL 31.24, entropy 5.17; 64-bit 126.11, 5.66; 64-bit with manual truncation 28.64, 5.12. After the fix (Fig. 9) entropy returns to 5.60-5.70 and the MDMs' true GenPPL is "around 100", worse than AR (<40). Fig. 10: temperature in [0.8, 1.0] trades GenPPL against entropy.
- Assumptions: exact sampler analysis for Props; empirical elsewhere / random order / sampled values via Gumbel-max / metrics are GenPPL and entropy, not KL.
- [S] Main relevance: the cleanest published demonstration that a sharpening of the sampler (here from a numerical bug) lowers GenPPL and entropy together and can reverse conclusions about model quality.

## 3. The chapter in six statements (what the primary papers together establish)

1. [S] Parallel commitment has a price that is an exact function of the data: per step, the KL from the true joint of the committed block to the product of its marginals (the conditional total correlation). One token per step costs zero (ParallelBench Remark 1; Li-Cai eps(1) = 0). One step for the whole sequence costs the full TC (ParallelBench Remark 1; Huang et al. 2022 as cited).
2. [S] With a random, data-independent order the total price is bounded by s_max/L times the summed token-to-rest mutual information (Li-Cai Thm 1), with a matching lower bound for some schedules (Thm 2); error therefore decays like 1/T for balanced schedules. Different metrics change the story: in Feng et al. TER (cross-entropy) is fine with a number of steps independent of L for n-gram data (Thm 4.2) while sequence-level correctness (SER) needs steps linear in L for a constructed HMM (Thm 4.4).
3. [S] Learned-model error adds, it does not multiply, in the random-order case: epsilon_train enters Li-Cai Thm 1 additively and exactly (Eq. 17). Under adaptive orders the model error is evaluated on the states the policy visits, which differ from the uniform-mask states the model was trained on (Kim et al. Prop 2.1 versus section 4; Zhang Lemma 4.1; EB-sampler section 3.1). [I] There is no theorem that the additive form survives with the same epsilon_train under an adaptive policy.
4. [S] The order is a lever on both terms. Adaptive confidence, margin or entropy rankings improve results at one token per step (Kim Tables 1-3; LLaDA Table 9; EB-sampler Fig. 2). Those gains are explained as avoiding hard subproblems (E_learn), not as reducing dependence.
5. [S] Value rules matter separately from position rules: argmax commitment and keep-the-most-confident-sample selection lower entropy and GenPPL (section 5, P2). The sampled-value theory of items 1-4 does not cover them.
6. [S] Revision does not repair factorisation error in general: Zhang Prop C.5 (under a stated assumption), Feng App. E.3 (the SER lower bound holds for ReMDM too). Empirically it raises MAUVE a lot in the T >= L regime (ReMDM Table 1).

## 4. Verdicts on framework-v0 section 2

### (a) The identity KL(q||p) = sum of expected conditional TC + marginal model error
- **Published; not new.** Strongest match: EB-sampler Eq. 7 with proof in App. A.1 Eq. 10-13 (their Sections 4 and 5 name the same two terms: model error and joint dependence error). It is stated for a general adaptive, state-dependent, possibly randomised policy phi; the quantity bounded is KL on (x, z) jointly, which upper-bounds the KL on x (their Eq. 10), with equality for deterministic phi (App. A.1 Eq. 14-15). The identity holds with the expectation taken under data-driven trajectories q_phi, as in our statement.
- Random or fixed order, exact marginals plus separate learned term: Li-Cai Eq. 17 (exact split into epsilon_train and the exact-marginal KL) and Eq. 23 (sum of KL to product of marginals, i.e. conditional TC). Fixed partitions: ParallelBench Thm 1 (inequality form, equality condition stated) and proof Eq. 6-11; Feng Lemma D.3; Zhang Eq. 16 and 18 (forward and reverse).
- Generality summary: equality for fixed partitions (ParallelBench, Feng, Zhang, Li-Cai per realisation); equality for deterministic state-dependent policies (EB-sampler); upper bound for randomised policies (EB-sampler Eq. 10; Li-Cai Eq. 11; Feng Lemma D.2).
- **What in our statement is not in the literature I read:** (i) the explicit requirement that A_n depend on z_n only (before values within A_n are drawn) and the contrast with sample-dependent selection. EB-sampler's phi(z_i | x^{z<i}, z<i) encodes the requirement but does not discuss its violation; 2604.00375 Table 1 draws the Sample-then-Filter versus Rank-then-Sample distinction informally. (ii) the E_sel term. (iii) the E_approx term. (iv) corollary 3 (see (d)). The synthesis in section 1 of framework-v0 is a presentation choice, not a result.
- [V] Exact check (research/review/dossier/primer-samplers-check.log): L = 4, V = 3, learned marginals = true marginals times a random state-dependent tilt, state-dependent deterministic policy (rank by true-marginal max probability), k = 1, 2, 3: KL(q||p) = 0.296465, 0.543795, 0.564322 and E_fact + E_learn equals these to 1e-16. E_fact = 0 at k = 1.
- Precision to add when citing: the identity is exact for the law of x only for deterministic policies; the E_learn term is a function of the policy (states visited), so "marginal model-error term" is not policy-independent.

### (b) Randomised policies: upper bound by convexity
- **Correct and known.** Li-Cai Eq. 11 and the sentence after it; Feng Lemma D.2 (Jensen on log(1/p)); EB-sampler Eq. 10 (ELBO/data-processing, covers randomisation inside phi).
- Refine the condition: the randomness must be fresh noise independent of the data x given the revealed state (equivalently a seed fixed in advance). Our wording, "randomness independent of the unrevealed tokens", is slightly looser than needed and slightly different. Independence from revealed values is not required, since those enter through the state.
- [V] Mixture of six random pair-order policies: KL(q||mixture) = 0.371 <= mean KL = 0.601.
- It is a bound, generally strict; equality for deterministic policies.

### (c) Selection bias: sampled-confidence selection or argmax sharpens the output and lowers entropy
- **Partly established, partly hypothesised; the clean formal statement is not found.**
- Argmax / low temperature: measured. Zheng et al. Fig. 10 (temperature 0.8-1.0 trades GenPPL for entropy), Table 2, Prop 5.2 (closed form for the truncated-Gumbel mechanism); ReMDM App. E.2.2 Table 5 (OWT, T = L = 1024, 5000 samples): eta_cap 0.008 / 0.05 / 0.2 gives MAUVE 0.36 / 0.25 / 0.02, GenPPL 27.7 / 12.9 / 3.1, entropy 5.32 / 4.93 / 2.43, and a "love love love" sample with GenPPL 1.5 (App. F.1). ReMDM and Zheng measure sentence or unigram entropy and an external-model GenPPL (evaluator not checked).
- Identity linking the metrics: Generative Frontiers (2604.02718), section 4: GenPPL is the cross-entropy to a reference, equal to KL plus entropy of the generator; it cites Pynadath et al. 2025 (not read) for small entropy changes reversing rankings. This is the formal reason entropy loss lowers GenPPL without a better model.
- Sample-then-filter confidence selection (MaskGIT; LLaDA at temperature > 0): MaskGIT and LLaDA state a diversity-loss hypothesis without measuring it (sections 2.8, 2.9). Indirect measurements by pass@k: 2606.12232 Takeaway 3 (WINO remasking at non-greedy decoding "exacerbates the diversity collapse" of confidence unmasking; pass@1 gain about 2.6% at tau = 0.8, about 0.7% at pass@64); 2604.00375 abstract and section 3 (low-confidence remasking improves pass@1, limits pass@k). Formal: 2604.00375 Prop 1 (GenPPL under self-scoring bounded by exp(h_V(delta)) for a (1-delta)-gated decoder) and Prop 2 (H(X) <= L h_V(delta)). [I] Prop 2 is an entropy cap for hard gating, not a distortion theorem relative to exact marginals; it does not separate position choice from value choice; and it assumes the gate holds at every commit.
- **Not found:** an experiment that separates rank-then-sample (position chosen by the model's marginal, values sampled; no E_sel by the identity) from sample-then-filter (value-dependent) on the same checkpoint with entropy or KL measured; a measurement of KL/entropy distortion against exact marginals. [V] Toy exact value: sample all masked positions, keep the single most confident sample, exact marginals, k = 1: KL(q||p) = 1.288 nats, entropy 2.163 against H(q) = 3.505, whereas the state-only policy gives KL 3e-16 (log lines C). One toy, one seed: it proves the term can be non-zero and large, not its size in practice.
- LLaDA and EB-sampler experiments run argmax or temperature 0 (LLaDA Alg. 4-5; EB-sampler section 6), so their reported gains include an E_sel component that their stated theory (sampled values) does not account for. [I]

### (d) Corollary 3: the same term as TC of the reverse step for uniform and Gaussian channels
- **Per-step quantity stated; the global corollary not found.** The conditional TC of one reverse step, TC(X_s|X_t) = E_{x_t} KL(p(X_s|x_t) || prod_i p(X_s^i|x_t)), is defined as the factorisation error of discrete flow and diffusion models in ReDi (2507.15897, Eq. 5; source distribution uniform allowed) and, with a model-dependent version TC_theta that includes marginal error, in IMDM (2605.10518, Eq. 6, citing Yoo 2025, Hayakawa 2025, Liu 2025; Theorem 4.1 gives a lower bound for the masked case: TC_theta >= max_ij p(e_ij) I(z_s^i; z_s^j | rest)). Di4C (2410.08709, Hayakawa et al.) does not use TC: Theorem 1 gives a total-variation O(1/N) bound for product-form denoisers under factorised forward processes (including discretised Gaussian) with a Omega(1/N) example for |S| = D = 2 (Theorem 1 and Appendix C.3). I did not find a statement that the sampler's KL equals the sum of per-step TCs plus marginal errors for uniform or Gaussian channels, nor any Gaussian-channel TC statement. Liu et al. 2025 and Yoo-ReDi proofs were not read beyond what is cited here.
- [I] Correctness caveat for our corollary 3: for these channels the state path z_{1:N} is not determined by x, so the chain rule gives equality only for the KL of path measures; the KL of the x-marginal is bounded above by it (data processing), as in EB-sampler's Eq. 10. "Vanishes as the step shrinks" holds only as N goes to infinity, and the Di4C lower-bound example shows the worst case does not do better than 1/N (in TV).

### (e) P1 to P5 (section 4 of framework-v0)
- **P1 (E_fact levers grow with tokens per step, vanish at k = 1; E_learn levers independent of k): supported in theory, with a proviso; the "independent of k" half is false for order levers.** Theory: Li-Cai Thm 1-2 (E_fact scales with s_max/L), ParallelBench Remark 1 (zero at k = 1), epsilon_train additive and schedule-independent for random order (Li-Cai Eq. 17). Empirics: EB-sampler Fig. 3 (accuracy falls as top-k grows for confidence, entropy and margin; figure not inspected numerically), Table 1 2.05-6.0x NFE saving at equal pass@1. Proviso: an order policy changes the states on which E_learn is measured (Zhang Lemma 4.1; Kim Tables 1-3 at one token per step; EB-sampler section 3.1), so "E_learn levers" are not k-independent when the lever is the order. Verdict: already shown (theory E2), step-sweep identification of the lever is open.
- **P2 (metric improvement with lower output entropy at fixed steps indicates E_sel): contradicted as an implication; true in a corrected form.** Product of exact marginals has entropy sum_j H(X_j) = H(X) + TC, higher than the data's. [V] perfectly correlated pair over 3 symbols: H(q) = 1.0986, H(product) = 2.1972 (log line D). So reducing E_fact lowers entropy toward H(q). Corrected form: an improvement accompanied by entropy below the reference (data or an AR baseline) points to E_sel (or mode-seeking E_learn), not to E_fact. Evidence for the corrected form: ReMDM Table 5, Zheng Table 2, Generative Frontiers identity, LLaDA Table 9 hypothesis. Note ReMDM Table 1 also shows entropy falling with T for ReMDM (5.38, 5.30, 5.20; data 5.44) together with a rising MAUVE, with nucleus top-p 0.9 in use; AR at 5.22 under the same nucleus setting.
- **P3 (revision cannot help at k = 1 with sampled values beyond what E_learn allows; its benefit per forward pass falls below that of more steps once E_fact is small): the second clause is contradicted in the one setting measured; the first clause is not testable as worded.** ReMDM Table 1 (OWT, L = 1024, 5000 samples, MAUVE, nucleus top-p 0.9): MDLM at T = 1024 / 2048 / 4096 gives 0.042 / 0.037 / 0.035 (more steps do not help once about one token is unmasked per step), ReMDM gives 0.403 / 0.610 / 0.656, AR 0.760, at the same T. When E_fact is already about zero, "more steps" cannot lower it, so the clause as written compares a lever with nothing; the observed ReMDM gain must come through E_learn or E_sel, which is what the first clause allows, so the first clause cannot be falsified by it. Seeds and intervals not found in the sections read; MAUVE only; one dataset. Related: Zhang Prop C.5 (remasking offers no guarantee), Feng App. E.3 (SER lower bound survives ReMDM), 2606.12232 (WINO adds little beyond confidence unmasking at standard block lengths). Verdict: contradicted in part; reformulate before use.
- **P4 (caching changes time per pass but not quality-against-passes, except through E_approx): definitional; consistent with what I read, not independently tested.** Exact caching (reuse when no token changed) leaves the law unchanged: Zheng et al. Fig. 9 includes MDLM "with and without the caching strategy", Feng App. B.3 says their results are unaffected (numbers not read). Approximate caches: 2607.29079 (abstract only, E1) reports content drift in accelerated dMLLMs attributed to stale visual and generated-text states, with a monotonic speed-agreement frontier as the cache refresh interval shortens, and no effect of confidence-threshold tuning at 1.05-1.25 committed tokens per step. Fast-dLLM's cache claim ("negligible performance drop", abstract) not read in full. Verdict: open as an empirical claim; as stated it holds by construction.
- **P5 (cross-modal TC costs most where cross-modal dependence is high, early steps for layout and object words): open; no direct evidence found.** Nothing I read measures cross-modal conditional TC. Abstract-level only (E1): 2607.08056 says logits alone do not determine a good generation order for text-to-image and multimodal understanding; Di4C section 5.2 shows dimensional correlation matters for masked image modelling on VQ tokens (single modality, not read in detail). Verdict: open.

## 5. Other published error decompositions for DLM sampling, with different terms
1. Li-Cai: epsilon_train (masked-CE excess) + schedule-weighted summed mutual information (Thm 1, 2). No entropy, no state dependence.
2. Feng et al.: epsilon_learning + a dependency-counting term for n-gram or HMM data (Thm 4.2, 4.4); metrics TER and SER.
3. Zhang et al.: order-sensitivity term (rollout-weighted local KL, entropy-dominated assumption, Eq. 7-11) + parallelisation bias in two directions (forward TC, reverse TC, Eq. 16, 18) + verification cost exp(TC) (Prop 5.1) + an incoherence probability (Eq. 14).
4. Kim et al.: per-masking-problem decomposition of the training loss (Prop 2.1) with imbalanced difficulty across subproblems (section 3.3); this is a decomposition of E_learn by subproblem.
5. Generative Frontiers (2604.02718): GenPPL = KL + entropy, a decomposition of the metric rather than the sampler.
6. IMDM (2605.10518): channel-level floor, TC_theta bounded below by weighted conditional MI for a deterministic single mask state; the floor depends on C1, which framework-v0 treats as a free choice.
7. Di4C: total-variation per-step bound O(eps^2) summing to O(1/N), tight for a 2 x 2 example.

## 6. Corrections and additions recommended for framework-v0
- Section 2: cite EB-sampler for the adaptive decomposition, Li-Cai and Feng for the random-order version, Zhang for both KL directions. State the condition "A_n is a function of z_n (plus independent noise)". Replace "marginal model-error term" by "model error on the states the policy visits".
- Section 2, E_sel: restrict to sample-dependent selection and argmax; record that rank-then-sample position policies are inside the identity. Credit 2604.00375 Table 1 for the sample-then-filter vocabulary; the toy numbers above are [V], one seed.
- Section 3 lever table: add that ordering levers also move E_learn; move "temperature and selection rules" out of the same row as "confidence remasking" (position choice versus value choice).
- Section 4: reword P2 and P3 as above; P1 add the order proviso; mark P4 as definitional; P5 as open.
- Add to the unknowns: whether the additive epsilon_train structure survives adaptive policies (no theorem found); how large E_sel is on a real checkpoint with exact decoding as reference; a cross-modal TC estimator.

## 7. Competing explanations and unknowns
- Competing explanation for LLaDA Table 9: gains from position order reducing E_learn (avoiding hard subproblems, per Kim et al.) rather than reduced diversity; both samplers use argmax, so value sharpening is common to both arms. The LLaDA authors' hypothesis (diversity reduction) is untested in that paper.
- Competing explanation for ReMDM's MAUVE gains: entropy loss under nucleus sampling and repetition rather than a better distribution; MAUVE punishes both low-entropy and mismatch, which is why the authors prefer it, but entropy still falls 5.38 to 5.20 with T.
- Unknown: Fast-dLLM, Pynadath et al. 2025, Liu et al. 2025, Yoo-ReDi's proof, Zhang App. B, Feng E.2 proof details, seeds and confidence intervals in all tables cited.
- Unknown: whether Zhang et al.'s Assumption 4.2 holds beyond their arithmetic tasks.

## 8. Files
- Check script: `C:\Users\Shlok\Downloads\Multi-Modality Language model\research\review\dossier\primer-samplers-check.py`; log: `...\primer-samplers-check.log`.
- Converted sources: `research/sources/md/<id>.md` for 2510.04767, 2602.00286, 2502.09622, 2505.21400, 2502.06768, 2503.00307, 2202.04200, 2502.09992, 2409.02908, 2505.24857, 2604.00375, 2606.12232, 2604.02718, 2605.10518, 2410.08709, 2507.15897; new HTML in `research/sources/html/` for 2602.00286, 2505.21400, 2202.04200, 2507.15897.
