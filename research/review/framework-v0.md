# Integrating framework for the review, v0 (2026-10-14)

Status: the orchestrator's formulation, **checked once against sources on 2026-10-14** by three
full-text reading agents (`dossier/competitor-anatomy.md`, `dossier/primer-foundations.md`,
`dossier/primer-samplers.md`) and by exact enumeration. Outcome: the organisation (five design
choices, an error budget used as a taxonomy) is absent from both existing surveys; the central
identity is correct but already published, so the review claims the synthesis and not the
theorem; three unification claims needed restrictions; two of five predictions were wrong or
contradicted and are corrected below. Still unchecked: the Gaussian family, the unified multimodal
models, and whether every corpus record can be placed. The human authors have not yet read it.

The aim is the thing ACM Computing Surveys' charter asks of a survey: one framework that puts the
whole literature in a single notation and makes its trade-offs derivable, so that the taxonomy is
a consequence of the mathematics and not a list of technique names.

## 1. One object: generation as a commitment process

A sequence is x = (x^1, ..., x^L) with x^i in a vocabulary V, drawn from the data distribution q.
A text or multimodal generator of any family in scope is specified by five choices.

| Choice | Meaning | Instances |
|---|---|---|
| **C1 Channel** | how partial information about a token is represented: a per-position state space Z and a corruption K_t(z^i given x^i) with signal level alpha_t falling from 1 to 0 | erasure (absorbing mask): z = x with probability alpha_t, else the mask symbol; symmetric (uniform): z = x with probability alpha_t, else uniform on V; Gaussian on embeddings, logits or the simplex: z = alpha_t e(x) + sigma_t eps |
| **C2 Reveal law** | which sets of positions are clean together during training | independent Bernoulli(alpha_t) per position (masked diffusion); prefixes (autoregression); prefixes of a random permutation (any-order autoregression); block prefix with Bernoulli inside the current block (block diffusion); per-modality laws (unified multimodal models) |
| **C3 Predictor** | what the network outputs | clean-token posterior marginals p_theta(x^i given z) for every position; equivalent parameterisations (ratio or concrete score, velocity of a probability path) |
| **C4 Commitment policy** | at sampling step n with state z_n: the set A_n of positions to commit, the value rule (sample at temperature tau, or argmax), and whether values within A_n are drawn independently or jointly | left to right, one token (autoregression); random sets (ancestral masked diffusion); confidence, entropy or margin ranked sets; learned planners; a coupling inside the set (autoregressive head, copula, energy model, verifier) |
| **C5 Revision** | whether a committed token can change later | never (plain absorbing); explicit remasking or token editing; implicit (symmetric and Gaussian channels revise every position at every step) |

Two derived quantities organise the cost side: **parallelism** k_n = size of A_n (tokens committed
per forward pass; autoregression has k = 1, a T-step sampler has mean k = L/T), and **compute
reuse** (how much of a forward pass is recomputed per step: caching).

Claimed consequences of C1 to C3 that the review would present as the unification (each must be
matched to its source):
(Corrected 2026-10-14 after the full-text check in `dossier/primer-foundations.md`; each verdict
there was "correct with a stated restriction".)
- With the erasure channel and marginal predictor, the continuous-time variational bound is a
  weighted masked cross-entropy (MD4, arXiv 2406.04329, Eq. 5; MDLM, 2406.07524, Eq. 13). The time
  variable can be removed; the weight is then 1/n for n masked positions and no longer depends on
  the schedule (Zheng et al., 2409.02908, Prop. 3.1), and the objective equals the any-order
  autoregressive one (RADD, 2406.03736, Thm 2; ARDM, 2110.02037, App. C). **Restriction:** the
  objectives coincide; the model classes do not, the any-order objective is a Jensen bound on a
  mixture whose conditionals need not be order-consistent, and the samplers coincide only in the
  exact event-driven limit (Zheng et al., Prop. 4.1). These results are nonparametric. The bound
  describes the infinite-step model: the gap to a finite-step parallel sampler is where E_fact lives.
- For the erasure channel, at masked positions, the ratio (concrete score) is the clean-token
  marginal times alpha/(1 - alpha) (RADD Thm 1; MD4 Prop. 1). An unconstrained ratio network can
  leave this set (MD4 App. H.3).
- The symmetric (uniform) channel keeps every position revisable, and it also changes the form of
  the bound and loses the time-free parameterisation and the any-order link. The Gaussian channel
  has **not yet been checked against sources** (not among the nine papers read).

## 2. The error budget (the theoretical spine)

Take the erasure channel, a marginal predictor p_theta, and a commitment policy that chooses A_n
as a function of the current state z_n only, drawing values independently from the marginals.
Because the sets A_1, A_2, ... partition the positions and each is determined by what has already
been revealed, the chain rule along the realised path gives q(x) = prod_n q(x^{A_n} given z_n),
and the sampler's law is p(x) = prod_n prod_{i in A_n} p_theta(x^i given z_n). Hence

    KL(q || p) = sum_n E_q [ TC( x^{A_n} given z_n ) ]                                  (E_fact)
               + sum_n E_q [ sum_{i in A_n} KL( q(x^i given z_n) || p_theta(x^i given z_n) ) ]   (E_learn)

where TC is the conditional total correlation of the tokens committed together, and the
expectations run over data-driven trajectories under the policy. For a randomised policy whose
randomness is independent of the unrevealed tokens, the right-hand side is an upper bound
(convexity). Corollaries:

1. k = 1 for every step gives E_fact = 0 for any order: autoregression and one-token-per-step
   masked diffusion pay only E_learn. **Parallel commitment is the only source of E_fact.**
2. E_fact depends on the policy only through which tokens are committed together in which
   context. A good policy commits together tokens that are nearly conditionally independent.
3. For symmetric and Gaussian channels the same term appears as the total correlation of the
   reverse step, TC(z_s given z_t), which vanishes as the step shrinks: step size plays the role
   of parallelism.

**Attribution (from `dossier/primer-samplers.md`, 2026-10-14). The two-term identity is published
and is not ours.** Random orders: ARDM (arXiv 2110.02037) Eq. 3 and 4. State-dependent adaptive
policies, with equality for deterministic ones: the entropy-bounded sampler paper of Ben-Hamu et
al. (2505.24857) Eq. 7 and App. A.1. Fixed or random partitions: Feng et al. Lemma D.3,
ParallelBench (2510.04767) Thm 1 proof, Li and Cai Eq. 17 and 23, Zhang et al. Eq. 16 and 18. The
bound for randomised policies is also known (Li and Cai Eq. 11; Feng Lemma D.2). Per-step total
correlation of a reverse step is defined in ReDi Eq. 5 and IMDM Eq. 6; the summed statement for
uniform or Gaussian channels was not found, and for those channels it is an equality on path
divergence and only a bound on the divergence of x. **Not found in the literature read:** the
selection and stale-computation terms as parts of one budget, and the explicit condition "the
policy depends on z_n only" together with what happens when it is violated. The review may claim
the synthesis and the taxonomy, and must cite the sources above for the identity.

Two further terms complete the budget:
- **E_sel, commitment-selection bias.** If the policy decides what to keep after seeing sampled
  values (sample every masked position, keep the most confident samples), or commits the argmax,
  the committed values no longer follow the marginals: the output distribution is sharpened in a
  position-dependent way. This lowers entropy and can improve likelihood-based fluency metrics
  without improving the model.
- **E_approx, stale computation.** Caching and other reuse replace p_theta(. given z_n) by an
  approximation computed from an earlier state.

Revision (C5) removes nothing from the budget by itself: with exact marginals and no parallelism
there is nothing to repair. It is a **corrector**: it spends extra forward passes to undo errors
already made through E_fact, E_learn or E_sel.

## 3. The taxonomy that follows

Every method is placed by **which term of the budget it changes and what it pays**.

| Lever | Lowers | Pays | Families in the corpus (to be populated from extraction) |
|---|---|---|---|
| fewer tokens per step, adaptive k (commit only while predicted dependence is low) | E_fact | forward passes | step schedules, confidence or entropy thresholds, entropy-bounded samplers |
| choose weakly dependent sets | E_fact | planner cost | spacing rules, learned planners, order policies |
| joint draw inside the set | E_fact | a second model or head | autoregressive heads, copulas, energy reweighting, speculative verification |
| block-wise generation | E_fact across blocks | loses global parallelism | semi-autoregressive and block diffusion |
| training (objective, scale, fine-tuning, reinforcement learning) | E_learn | training compute | training strategies |
| distillation into few steps | moves E_fact into the model class | training compute; the student must represent joint structure | consistency and distillation methods |
| revision | repairs realised E_fact, E_learn, E_sel | forward passes | remasking, correctors, token editing, symmetric-state samplers |
| temperature and selection rules | trades E_sel for sample quality | diversity | confidence remasking, argmax decoding, low temperature |
| compute reuse | nothing in the budget; adds E_approx | wall-clock only | key-value caching, kernels |

Unified multimodal models enter with no new machinery: the sequence mixes modalities, each
modality has its own C1 and C2 (erasure for both; autoregressive text with masked or continuous
image tokens; and so on), and E_fact now includes **cross-modal** total correlation when tokens of
two modalities are committed in the same step.

## 4. What the framework predicts (candidates for the review's stated open propositions)

P1. Gains from E_fact levers grow with tokens per step and vanish as k approaches 1; gains from
    E_learn levers do not depend on k. A method's step sweep therefore identifies which term it changed.
P2. A metric improvement that comes with lower output entropy at fixed steps indicates E_sel, not
    a lower E_fact or E_learn.
P3. Revision cannot help at k = 1 with sampled (not argmax) values beyond what E_learn allows, and
    its benefit per forward pass falls below that of simply using more steps once E_fact is small.
P4. Caching changes time per forward pass but not the curve of quality against forward passes,
    except through E_approx.
P5. In unified models, committing image and text tokens in parallel is costly exactly where the
    cross-modal conditional dependence is high (early steps for layout and object words).

These are derived expectations, not findings. Each is checkable against within-paper step sweeps
and, properly, by reruns on frozen checkpoints (Paper 2).

**Status after the source check (2026-10-14):**
- P1: supported in theory, with a caveat: the order also changes E_learn (Kim et al.; Zhang et
  al.; Ben-Hamu et al.), so a step sweep does not cleanly separate the two terms.
- P2: **wrong as worded.** A product of exact marginals has higher entropy than the data (also
  visible in our toy check: 4.21 nats against 3.96), so lowering E_fact lowers entropy too.
  Corrected form: output entropy **below a reference entropy** (data, or the many-step sampler)
  indicates E_sel. Measured for argmax and low temperature (Zheng et al. Table 2 and Fig. 10;
  ReMDM Table 5; the identity generative perplexity = divergence + entropy); for
  confidence-of-sampled-token selection it is only hypothesised in the literature, with an entropy
  cap in arXiv 2604.00375. A clean measurement of that distortion was not found.
- P3: second clause **contradicted** (ReMDM Table 1: plain masked diffusion stays flat while
  remasking keeps improving up to 4096 steps); first clause not testable as worded. To be rewritten.
- P4: true by construction; not a prediction.
- P5: open; no evidence found either way. This is the candidate conjecture for the multimodal
  part and for Paper 2.

## 4b. Numerical check done (2026-10-14)

`analysis/framework/check_decomposition.py`, exact enumeration, vocabulary 3, length 4, two tokens
per step, five random data distributions, exact and perturbed predictors (10 cases):
- Deterministic state-dependent policy: KL(q || p) equals E_fact + E_learn in every case, largest
  absolute gap 2.6e-16. With an exact predictor E_learn is zero and the whole divergence is E_fact.
- Uniformly random policy: KL is below the bound in every case (for example 0.182 against 0.244),
  as convexity predicts.
- Sample-dependent selection (keep the sampled tokens with the highest own probability) gives
  lower output entropy than the state-dependent policy with the same predictor in every case
  (for example 3.85 against 4.21 nats, data 3.96), which is the selection-bias term.
This confirms the algebra on toy distributions. It says nothing about attribution, novelty, or
behaviour of large models.

## 5. What must be checked before any of this is used

1. **Correctness.** Re-derive section 2 independently; test it numerically on small synthetic
   distributions (exact enumeration); find the precise conditions (state-dependent against
   sample-dependent policies, randomised policies).
2. **Attribution.** For every statement in sections 1 and 2, the paper that first proved it, with
   theorem number. Parts of the decomposition are known results; the review must credit them and
   claim only the synthesis.
3. **Novelty of the organisation.** Full read of arXiv 2508.10875 (latest version) and 2506.13759
   v5: do they already organise the field by a commitment process, an error decomposition, a
   design-space table in one notation, or a lever-by-error-term taxonomy?
4. **Coverage.** Can every one of the 572 seed records be placed in the tables of sections 1 and
   3? Records that fit nowhere show where the framework is incomplete.
