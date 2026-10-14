# Integrating framework for the review, v1 (2026-10-14)

Supersedes `framework-v0.md` (kept unchanged as the historical record). v1 applies the corrections
of four full-text checks: `dossier/primer-foundations.md` (nine papers, absorbing channel),
`dossier/primer-samplers.md` (ten papers, sampler theory), `dossier/primer-gaussian.md` (six
papers, Gaussian, embedding and flow branch; edits G1 to G14) and `dossier/primer-multimodal.md`
(ten unified models at sections-read level plus one released sampler; edits M1 to M11). Every
edit is listed with its source in section 7. Tags: **[S]** source fact (location given in the
dossier cited), **[I]** our inference, **[H]** hypothesis, **[V]** verified here by exact
enumeration (script named). Status: orchestrator's formulation, E0 as a whole; the parts tagged
[S] are E2. Not yet done: formalisation of E_sel and E_fact^X by method-architect, a red-team
attack on the derivations, the coverage test, and a reading by the human authors.

The aim is unchanged: one framework that puts the literature in a single notation and makes its
trade-offs derivable, so that the taxonomy follows from the mathematics.

## 1. One object: generation as a commitment process

A sequence x = (x^1, ..., x^L), x^i in a vocabulary V (possibly a union of per-modality
vocabularies), is drawn from q. A generator in scope is specified by five choices. The sampler
runs on a **state** s_n = (z_n, m_n): the partially revealed or noised sequence z_n and an
optional memory m_n (self-conditioning input, cached activations, planner state). v0 had no
memory; G9 and M8 require it.

| Choice | Meaning | Instances |
|---|---|---|
| **C1 Channel** | per-position state space Z and corruption K_t(z^i given x^i), or more generally a probability path p_t(z given x_0, x_1) with a source and a coupling (G5) | **erasure** (absorbing mask): z = x with probability alpha_t, else the mask symbol; **symmetric** (uniform): P(z = x) = alpha_t + (1 - alpha_t)/K, else uniform (G5); **mixtures** of erasure and uniform noise (DFM Eq. 10); **Gaussian**: z = a_t e(x) + s_t eps, variance-preserving (a^2 + s^2 = 1) or variance-exploding (a = 1), embedding e learned or fixed, network input g(z) possibly nonlinear such as a softmax of logits (G2); a genuine simplex diffusion was tried and abandoned in CDCD App. B.3, so "Gaussian on embeddings or logits" replaces "or the simplex" (G4). **Per modality**: in unified models C1 may differ by modality; continuous image latents with a Gaussian or flow channel (Transfusion, BAGEL, Show-o2) have no committed set (M2). |
| | signal level | erasure and uniform: alpha_t from 1 to 0. Gaussian: SNR(t) = a^2/s^2 from large to 0 (or finite at t = 0). The common coordinate across families is the per-position posterior entropy (CDCD Sec. 3.3), or Duo's map T for a Gaussian on one-hot vectors (G3). |
| **C2 Reveal law** | which positions are clean together during training, with the objective's weight | independent Bernoulli(alpha_t) (masked diffusion); prefixes (autoregression); prefixes of a random permutation (any-order); **block**: independent t_b per block, clean prefix, later blocks absent, weight alpha'/(1 - alpha) per block, clipped schedules change the weight (BD3-LM; G7). **Gaussian counterpart**: conditioning law (prefix, random or mixed masks, CDCD Sec. 4.1; random context and block, SSD-LM Alg. 1; C-coupling, DFM), shared noise level, and the embedding geometry, which sets the order in which tokens become distinguishable (Plaid Sec. 3.1) (G6). **Multimodal**: a joint law over per-modality reveal sets: shared t (UniDisc Alg. 1; MMaDA Eq. 1), clean input with noised output (MMaDA Eq. 2; MMaDA-Parallel Eq. 1), whole-modality dropout (UniDisc), independent per-image levels (BAGEL), capped noise (Transfusion). Per-modality loss weights make the trained objective differ from the bound (M3). |
| **C3 Predictor** | what the network outputs, from the state s_n | clean-token posterior marginals p_theta(x^i given s_n); concrete-score and ratio parameterisations (equal to the marginal times alpha/(1 - alpha) on masked positions for the erasure channel); x_0 vector regression (Diffusion-LM; an MSE head with embedding dimension d much smaller than K does not retain the token marginals [I]); logits turned into a posterior-mean embedding (Plaid, CDCD); a posterior over K tokens (Duo); a probability denoiser with velocity as an affine map of it (DFM) (G8). **Self-conditioning** puts the previous prediction into m_n (G9). **Head layout** in unified models: one shared vocabulary head, separate text and image heads, or a text head plus a flow or noise head; sampling support may be restricted by modality (M4). |
| **C4 Commitment policy** | the set A_n of positions to commit, the value rule (sample at temperature tau, argmax, guided), and whether values in A_n are drawn independently or jointly | left to right, one token (AR); random sets (ancestral masked diffusion); confidence, entropy or margin ranked sets; learned planners; a coupling inside the set (AR head, copula, energy model, verifier). **Two levels for Gaussian and uniform channels**: every position is updated each step with no committed set, then discretisation: per-step projection or clamping with re-noising (Diffusion-LM, SSD-LM) and a **final rounding that commits all L positions at once** (CDCD, Plaid, Diffusion-LM) (G10). **Multimodal**: per-modality counts k_n^T and k_n^I, and whether both are non-zero in the same pass (joint), separated (sequential) or alternating; one confidence ranking over all modalities fixes k_n^T and k_n^I implicitly through each modality's confidence scale (UniDisc Alg. 2), per-modality schedulers fix them explicitly (MMaDA-Parallel Sec. 3.2) (M5, M11). |
| **C5 Revision** | whether a committed token can change later | never (plain absorbing); explicit remasking or token editing (ReMDM; DFM's corrector, the precise form for a mask source); **implicit but qualified** for symmetric and Gaussian channels: not pinned by the channel, pinned by conditioning masks, and effectively frozen below an identifiability noise level, so the per-step revision rate is an empirical quantity (G11; toy: nearest-embedding decoding 100 percent correct at sigma = 1, 44.5 percent at sigma = 4, random embeddings [V], `dossier/primer-gaussian-check.py`); **output-level revision** (planning, reflection loops over finished samples) in unified models (M7). |

Two derived quantities organise cost: **parallelism** k_n = |A_n| (AR: k = 1; a T-step sampler
has mean k = L/T), and **compute reuse** (how much of a forward pass is recomputed per step).

**Unification claims, with their restrictions** (from `primer-foundations.md`, unchanged from v0
except the Gaussian item):
- Erasure channel, marginal predictor: the continuous-time bound is a weighted masked
  cross-entropy (MD4 Eq. 5; MDLM Eq. 13); time can be removed, weight 1/n (Zheng et al. Prop.
  3.1); the objective equals the any-order AR objective (RADD Thm 2; ARDM App. C). Objectives
  coincide; model classes do not; samplers coincide only in the exact event-driven limit.
- Erasure channel: concrete score = clean marginal times alpha/(1 - alpha) on masked positions
  (RADD Thm 1; MD4 Prop. 1).
- Symmetric channel: every position stays revisable; the bound changes form and loses the
  time-free parameterisation and the any-order link.
- **Gaussian channel (new, G12):** a Gaussian on one-hot vectors and the uniform-state channel
  coincide per position and per time through Duo's map alpha = T(alpha~) (Duo Eq. 10 to 13;
  checked against Monte Carlo [V]); trajectories and reverse kernels do not coincide (Duo App.
  A.3, Eq. 40). Embedding Gaussians (Diffusion-LM, CDCD, Plaid) have no such map. So the
  uniform-state budget cannot be read off the Gaussian one.

## 2. The error budget

### 2.1 The factorisation identity (published; we cite, not claim)

Erasure channel, marginal predictor, policy with **A_n a function of the state s_n plus fresh
noise independent of x given the state**, values in A_n drawn independently from the
marginals. Along the realised path, q(x) = prod_n q(x^{A_n} given s_n) and
p(x) = prod_n prod_{i in A_n} p_theta(x^i given s_n). For any joint P and product Q,
KL(P || Q) = TC(P) + sum_j KL(P_j || Q_j). Hence

    KL(q || p) = sum_n E [ TC( x^{A_n} given s_n ) ]                                      (E_fact)
               + sum_n E [ sum_{i in A_n} KL( q(x^i given s_n) || p_theta(x^i given s_n) ) ]   (E_learn)

with expectations over data-driven trajectories under the policy. Equality for deterministic
policies; an upper bound for randomised ones (convexity, or data processing on the path).
**E_learn is model error on the states the policy visits**, not a policy-free constant: an
ordering policy moves it (Kim et al.; Zhang et al. Lemma 4.1; EB-sampler Sec. 3.1).
[V] residual 2.6e-16 over 10 cases (`analysis/framework/check_decomposition.py`); 1e-16 at
k = 1, 2, 3 (`dossier/primer-samplers-check.log`).

**Attribution.** Adaptive state-dependent policies, equality for deterministic ones: Ben-Hamu
et al., EB-sampler (2505.24857) Eq. 7, App. A.1 Eq. 10 to 15. Random orders: ARDM (2110.02037)
Eq. 3 to 4; Li and Cai (2505.21400) Eq. 11, 17, 23. Fixed partitions: ParallelBench
(2510.04767) Thm 1 and proof Eq. 6 to 11; Feng et al. (2502.09622) Lemmas D.2, D.3; Zhang et
al. (2602.00286) Eq. 16, 18 (both KL directions). With a memory m_n the identity holds on the
augmented path; it is an equality for x only when m_n is a deterministic function of the
revealed path [I, to be checked by method-architect].

Corollaries. (1) k = 1 at every step gives E_fact = 0 for any order: parallel commitment is the
only source of E_fact under the erasure channel. (2) E_fact depends on the policy only through
which tokens are committed together in which state. (3) Monotone in T for optimal partitions
(ParallelBench Thms 2 and 3), decaying like 1/T for balanced random schedules (Li and Cai Thms
1 and 2).

### 2.2 The cross-modal split (new; ours as a statement, elementary as algebra)

When A_n contains tokens of two discrete modalities, by the chain rule for total correlation

    TC(x^{A_n} given s_n) = TC(text part given s_n) + TC(image part given s_n)
                            + I(text part ; image part given s_n),

so E_fact = E_fact^T + E_fact^I + **E_fact^X**, where E_fact^X is the summed conditional mutual
information of co-committed text and image tokens (M6). [V] maximum error 1.3e-15 over 800
cases; on the full sampler, E_fact equals KL and the three-part sum to 6.6e-16
(`dossier/primer-multimodal-check.py`, parts A and B). The toy also shows that a
modality-sequential schedule at the same k removes E_fact^X and pays within-modality total
correlation instead, and can be worse than an interleaved schedule (0.508 to 0.728 nats
against 0.007 to 0.228). Bound used by confidence rules: TC <= sum_i H(x^i given s) -
max_i H(x^i given s) (part C, no violations in 2000 random sets). E_fact^X exists only for
co-committed tokens of two discrete modalities; continuous image channels contribute through
their own reverse-step term (2.3). Not found in any paper read: a measurement of E_fact^X or of
any cross-modal quantity per step.

### 2.3 Symmetric and Gaussian channels (rewritten, G13)

These channels have no committed set before the final step. The joint-dependence term is then
the per-step TC(z_s given z_t) of the reverse kernel. Three corrections to v0's corollary 3:
(a) the chain rule gives an equality only for the KL between path measures; for the law of x it
is an upper bound (data processing), as in EB-sampler Eq. 10; in a variational bound the step
terms are x-conditional and carry an extra I(x; z_s given z_t). (b) "Vanishes as the step
shrinks" holds as N goes to infinity; in a two-token Gaussian toy the per-step term scales as
step^2.16, so the sum scales roughly linearly in the step [V, `primer-gaussian-check.py`];
Di4C (2410.08709) Thm 1 gives an O(1/N) total-variation bound with a matching Omega(1/N)
example, so the worst case is no better than 1/N. (c) Gaussian samplers add a **final parallel
commitment** of all L positions at rounding, with its own TC(x given z_0). The per-step
quantity is defined in ReDi (2507.15897) Eq. 5 and IMDM (2605.10518) Eq. 6; the summed
statement was not found in Diffusion-LM, CDCD, Plaid, DFM, Duo or BD3-LM; the nearest are Plaid
Eq. 3 to 4 and DFM Eq. 20 (o(h)).

### 2.4 E_sel, commitment-selection bias (the term not found in the literature read)

The identity requires that A_n and the value rule not look at the values being committed. Three
common rules break this:
- **sample-then-filter**: sample every masked position, keep the most confident samples
  (MaskGIT; LLaDA at temperature above 0);
- **argmax or low temperature**: commit the mode instead of a sample;
- **guidance**: classifier-free guidance, including modality dropout, replaces the marginal by a
  sharpened and re-conditioned one (M8; UniDisc applies it per step, App. I).
Rank-then-sample rules (positions chosen from the marginals in s_n, values sampled) stay inside
the identity and pay no E_sel. Define E_sel as the divergence between the law the sampler
actually produces and the law the same policy would produce with sampled values. [V] one toy,
exact marginals, k = 1, keep the single most confident sample: KL(q || p) = 1.288 nats,
entropy 2.163 against H(q) = 3.505; the state-only policy gives 3e-16 (`primer-samplers-check.log`).
Measured in the literature for argmax and temperature (Zheng et al. Table 2, Fig. 10, Prop. 5.2;
ReMDM Table 5); hypothesised but not measured for sample-then-filter (MaskGIT, LLaDA); an
entropy cap for hard gating exists (2604.00375 Prop. 2), which is not a distortion theorem
against exact marginals. Gaussian-channel analogues: clamping, renormalisation, score or logit
temperature, Greedy-Tail (G10). **Formal statement pending: method-architect (section 6).**

### 2.5 E_approx, stale computation, and memory

Lossy caches replace p_theta(. given s_n) by an approximation computed from an earlier state.
Exact reuse adds nothing: block-causal attention makes cross-block KV caching exact in BD3-LM,
and within-block reuse is exact only for the absorbing channel (G14a). Lossy instances:
Fast-dLLM-type caches (not read in full), Lumina-DiMOO's ML-Cache (M8d). Self-conditioning is a
trained memory, not staleness; it belongs in m_n and in E_learn on augmented states (G9) [I].

### 2.6 Revision as a corrector

Revision removes nothing from the budget by itself. It spends forward passes to undo realised
errors from E_fact, E_learn or E_sel. Two published limits: no general guarantee that
remasking repairs factorisation error (Zhang et al. Prop. C.5, under a stated assumption), and
the sequence-error lower bound survives ReMDM (Feng et al. App. E.3).

## 3. The taxonomy that follows

Every method is placed by the term it changes and what it pays.

| Lever | Lowers | Pays | Families |
|---|---|---|---|
| fewer tokens per step, adaptive k | E_fact | forward passes | step schedules, confidence or entropy thresholds, EB-sampler |
| choose weakly dependent sets (position order) | E_fact; **also moves E_learn** (visited states) | planner cost | spacing rules, learned planners, order policies |
| joint draw inside the set | E_fact | a second model or head | AR heads, copulas, energy reweighting, speculative verification |
| block-wise generation | E_fact across blocks | global parallelism; cross-block cache exact | semi-AR and block diffusion |
| modality-ordered or planned schedules (M8b) | E_fact^X | forward passes and within-modality TC | text first, layout first (LaViDa-O Table 13; MMaDA-Parallel Table 10) |
| training (objective, scale, fine-tuning, RL) | E_learn | training compute | training strategies |
| self-conditioning, learned schedules, time warping (G14c) | E_learn (Gaussian models) | training compute | CDCD, Plaid |
| distillation into few steps | moves E_fact into the model class | training; the student must represent joint structure | consistency and distillation |
| revision (token level) | repairs realised errors | forward passes | remasking, DFM corrector, token editing, Duo's uniform-state sampler (few-step claim empirical, confounded with distillation and entropy, G14b) |
| output-level revision (M8c) | repairs finished samples | full generations | reflection loops (plateau near 12 rounds, LaViDa-O Table 16) |
| **value rules: argmax, temperature, sample-then-filter** | trade E_sel against sample quality | diversity | low temperature, confidence-of-sample selection |
| **guidance, including modality dropout** (M8a) | E_sel-like sharpening; also re-conditions across modalities | diversity; one extra pass per step | CFG in unified models |
| exact compute reuse | nothing | wall-clock only | KV caching where exact |
| lossy compute reuse | nothing; adds E_approx | wall-clock only | approximate caches, ML-Cache |

Position choice and value choice are separate rows (v0 merged them). Unified multimodal models
need four additions, not "no new machinery" (M7): guidance, per-modality weights and schedules,
continuous image channels in hybrids, and output-level revision; E_fact gains E_fact^X only for
co-committed tokens of two discrete modalities.

## 4. Propositions (rewritten from the primers)

Each is a derived expectation (E0), stated so that a within-paper sweep or a rerun on a frozen
checkpoint can refute it.

**P1 (identification by tokens per step).** For a position lever compared with its base
sampler at matched forward passes, with sampled values at temperature 1 and guidance fixed, the
gain is the sum of an E_fact part that goes to zero as k goes to 1 and an E_learn part from the
changed visited states. **The gain that remains at k = 1 estimates the E_learn part; its growth
with k estimates the E_fact part.** Supported in theory (Li and Cai Thms 1 and 2; ParallelBench
Remark 1; Kim et al. Tables 1 to 3 show gains at k = 1). Caveat: step sweeps in the unified
models do not hold guidance fixed, except Show-o2 Table 11.

**P2 (diagnosing E_sel).** Lowering E_fact moves output entropy down toward the reference from
above. This is exact for a one-shot product of exact marginals (entropy H(q) + TC) and held in
every toy case (4.21 against 3.96 nats [V]); for a multi-step sampler the per-step entropies are
averaged over the sampler's own trajectories, not the data's, so the general statement is an
open item for method-architect (6.1) [I]. **An improvement at
fixed steps that comes with output entropy below the reference (data, or the many-step sampler
with sampled values) indicates E_sel or mode-seeking E_learn, not lower E_fact.** Evidence
consistent with it: ReMDM Table 5; Zheng et al. Table 2; GenPPL = KL + entropy (2604.02718
Sec. 4). Unmeasured: sample-then-filter against rank-then-sample on one checkpoint.

**P3 (where revision gains come from).** When T >= L, so that further steps cannot lower
E_fact, a revision sampler's gain over its base at matched forward passes comes through E_learn
on visited states or through E_sel. **The E_sel share is diagnosable: it comes with entropy
below the reference; with nucleus truncation off and entropy at the reference, what remains is
E_learn repair.** Replaces v0's P3, whose second clause ReMDM Table 1 contradicts (MDLM flat at
0.042, 0.037, 0.035 MAUVE for T = 1024, 2048, 4096; ReMDM 0.403, 0.610, 0.656). Note ReMDM's
entropy falls 5.38, 5.30, 5.20 with T (data 5.44) under top-p 0.9, consistent with a partial
E_sel share [I].

**Remark (was P4).** Exact caching leaves the quality-against-forward-passes curve unchanged by
construction. Lossy caching shifts it by E_approx, measurable as the divergence between cached
and uncached per-step marginals on the same states. Not a prediction.

**P5a (premise, multimodal).** In an all-discrete unified model with a joint reveal law, the
per-step cross-modal conditional mutual information between co-committed text and image
tokens, X_n, is concentrated in early steps and on layout and object tokens, and is large next
to the within-modality terms there. Evidence: weak and indirect. UniDisc App. I: the distance
between conditional and unconditional logits shrinks as tokens are decoded (Fig. 24), and
guidance on steps 1 to 3 of 24 gives CLIP 0.301 against 0.312 for all steps and 0.283 for steps
22 to 24 (Fig. 25); LaViDa-O Table 13; one MMaDA-Parallel example.

**P5b (consequence, multimodal).** At matched forward passes and matched tokens per pass, a
schedule that separates dependent pairs, including across modalities, has lower E_fact than
joint commitment by about E_fact^X; a modality-sequential schedule removes E_fact^X but pays
within-modality total correlation and need not beat joint or alternating schedules. Evidence:
untested. The only joint-against-sequential contrast (MMaDA-Parallel Tables 3 and 10: output
alignment 59.8 parallel, 57.5 semi-parallel, 54.1 sequential) is confounded: the sequential
text cannot see the image, training differs, one run, a GPT-4.1 judge, no interval; and the
released MMaDA-Parallel-A sampler commits no image tokens in the first quarter of steps
(`parallel_generator.py` lines 156 to 160 and 219 to 220, E3), unlike the paper's text.

## 5. What the review can claim, and what it cannot

- Claim: the five-choice design space, the budget used as a taxonomy, the separation of
  position rules from value rules, E_sel and E_approx as named terms, the cross-modal split,
  and propositions P1 to P5b as stated open questions with the evidence each needs.
- Cite, not claim: the factorisation identity and its randomised bound (2.1); the per-step TC
  for uniform channels (ReDi, IMDM); the any-order and concrete-score equivalences.
- Cannot claim yet: any size of E_sel or E_fact^X on a real checkpoint; anything about the
  hybrids' continuous channels beyond their placement.

## 6. Open work, in order

1. method-architect: formal statement of E_sel (law of committed values under sample-then-filter
   with k kept out of the sampled set; argmax; guidance), its relation to the identity, a bound
   or closed form in a tractable case, and an estimator; formal statement and estimator of
   E_fact^X per step. Check the memory claim in 2.1.
2. red-team: attack 2.1 to 2.4 and P1 to P5b.
3. Coverage test: a design-space table of about 40 major models on C1 to C5 and the lever table.
4. PDF checks of BD3-LM App. B.5 and Duo Thm 3.2 (flagged in `primer-gaussian.md` sec. 6).
5. Human authors read this file.

## 7. Change log from v0

Gaussian primer edits G1 to G14 (`dossier/primer-gaussian.md` sec. 5) and multimodal edits M1
to M11 (`dossier/primer-multimodal.md` sec. 6), all applied: G1 and M1 status line; G2 to G5
C1; G6, G7, M3 C2; G8, G9, M4 C3; G10, M5, M11 C4; G11, M7 C5; G12 unification; G13 section
2.3; G14 and M8 lever table; M2 per-modality channels; M6 section 2.2; M9 and M10 P5a and P5b.
From `dossier/primer-samplers.md` sec. 6: the state condition with fresh noise, "model error on
visited states", position and value rows separated, P2 and P3 reworded, P1 order proviso, P4
moved to a remark. New in v1 and not from any primer: the memory component m_n of the state and
the claim that the identity holds on the augmented path ([I], open item 6.1); the identification
reading of P1 (gain at k = 1 against growth with k); the entropy diagnosis in P3.
