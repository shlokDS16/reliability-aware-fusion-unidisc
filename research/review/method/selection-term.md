```yaml
agent: method-architect
date: 2026-10-14
brief: Formal treatment of E_sel (commitment-selection term) and E_fact^X (cross-modal factorisation term) of framework-v1, with checked statements, closed forms, estimators and a staged measurement spec
sources_examined:
  - research/CONTRACT.md
  - research/review/framework-v1.md (full)
  - research/review/dossier/primer-samplers.md (sections 0-8)
  - research/review/dossier/primer-samplers-check.py
  - analysis/framework/check_decomposition.py
  - research/review/dossier/primer-multimodal.md (sections 0, 1, 4, 5 Q4-Q5, 6)
  - research/review/dossier/primer-multimodal-check.py
  - arXiv 2604.00375 (cached md in the main checkout, research/sources/md/2604.00375.md): sections 2-3, App. C, App. H.1-H.2
coverage: >
  All T1-T10 items addressed. Every [V] statement is a PASS line in
  analysis/framework/check_selection.log (61 checks, 0 failures). Not covered: no paper other than
  2604.00375 was re-read; no proof of the k >= 2 per-state entropy inequality (numerical only);
  no proof that KL(r_N||p) is nondecreasing in N (numerical only); checkpoint names in T9 are E0
  (not verified, nothing downloaded); all magnitudes come from toy distributions and are not
  predictions for any model.
claims:
  - statement: For any one-step commit kernel, KL between data-driven and sampler path laws equals E_fact + E_learn + V, where V is a signed value term; for state-only marginal tilts (temperature, top-p, argmax, CFG) V = E_tilt = E_learn[p_tilde] - E_learn[p]; for joint draws V = -(E_fact + E_learn).
    status: supported
    evidence: derivation T1.3; check_selection.log T1.1, T1.1b, T1.3, T5.7
    level: E4
    confidence: 0.95
  - statement: For sample-then-filter (SF) the forward per-step value term is +infinity whenever a data-supported (position, value) pair is blocked by a competitor, so E_sel has no per-step forward decomposition; the output-level KL(q||p_SF) stays finite for full-support predictors.
    status: supported
    evidence: Prop. 2 and Lemma 3 (T1); log T3.12, T1.3b (32 of 32 configurations), T1.3c, T1.9, T5.1
    level: E4
    confidence: 0.9
  - statement: Canonical definition E_sel := KL(q||p_kappa) - KL(q||p_matchedRS), matched RS = same position law, values from p_theta; it is the KL-projection of the SF kernel onto rank-then-sample kernels, zero on RS, finite, signed, equal to KL(q||p_SF) with exact marginals at k = 1 (1.288 nats in the framework toy).
    status: supported
    evidence: T1.4; log T1.6, T1.7, T1.8, T3.11, T3.13
    level: E4
    confidence: 0.85
  - statement: Exact law of the SF commit for any k, tie rule and score; at k = 1 the committed value law is a monotone (majorising) reweighting of p_i, so every Renyi entropy falls; at k >= 2 selection couples the committed values.
    status: supported
    evidence: T2; log T2.1-T2.8
    level: E4
    confidence: 0.95
  - statement: Per-step model-only distortion D(s) = KL(kappa_SF||kappa_mRS) <= H(rho) <= log C(N,k); for iid marginals with random ties D <= KL_cont(N,k) = log C(N,k) - (N-k)(H_N - H_{N-k}), tight for diffuse vocabularies; summed over the sampler's own path it upper-bounds KL(p_SF||p_mRS).
    status: supported
    evidence: T3; log T3.1-T3.9, T3.14
    level: E4
    confidence: 0.9
  - statement: framework-v1 P2 premise (b) is false - a multi-step state-only sampler with exact marginals and sampled values can have output entropy far below H(q), with an unbounded gap at KL <= ln 2.
    status: contradicted
    evidence: T4(b) construction; log T4.3 (2.773 against 3.514 nats, closed forms match)
    level: E4
    confidence: 0.95
  - statement: SF output entropy is not always below matched-RS output entropy (per-state it is, at k = 1).
    status: mixed
    evidence: log T4.1 (per state, 3000 states) and T4.2 (counterexample 3.344 against 3.248); 40 of 40 random cases go the usual way
    level: E4
    confidence: 0.9
  - statement: E_sel of SF grows with the number of selection rounds while E_fact falls, giving an interior optimum in the number of steps in a toy.
    status: supported
    evidence: log T3.10c (iid, E_fact = 0), T3.15, T3.16 (Markov toy, SF KL 1.840, 1.025, 0.836, 1.535 for T = 1, 2, 3, 6)
    level: E4
    confidence: 0.7
  - statement: TC of a co-committed text-image set has two exact splits, symmetric (cross term X = I(a;b|s)) and text-first (cross term S = sum_j I(a;b_j|s)); S is estimable by reveal-and-requery with R extra passes per probed step; X - S and S - pairwise are not sign-definite.
    status: supported
    evidence: T6; log T6.1-T6.5
    level: E4
    confidence: 0.9
  - statement: framework-v1 2.1 memory sentence is right that the identity holds on the augmented path, wrong in "only when": equality for x holds iff E_q KL(Q(path|x)||P(path|x)) = 0; a deterministic augmented path is sufficient, not necessary; memory that is a function of the revealed path is not sufficient under a random policy.
    status: mixed
    evidence: T7; log T7.1-T7.5
    level: E4
    confidence: 0.9
competing_explanations:
  - The toy magnitudes (1.288 nats, quadratic growth, U-shape) come from small vocabularies with flat-ish marginals; real LM marginals are peaked, which shrinks D toward 0 (equality cases of T2). Size on a checkpoint is open.
  - Output-level entropy and GenPPL differences between SF and matched RS on a real model can come from the position law interacting with E_learn on visited states, not only from value selection; the matched-RS arm controls the position law but not trajectory divergence after the first step.
unknowns:
  - Whether H(SF step) <= H(matched-RS step) holds per state for k >= 2 (0 violations in 3000 random states; no proof).
  - Whether KL(r_N||p) is nondecreasing in N for every p (0 violations in 300 random p, N <= 64; no proof).
  - Magnitude of D, E_tilt and S on any real checkpoint.
next_test:
  hypothesis: On a frozen masked-diffusion LM, SF commits sharper values than its matched-RS twin at matched forward passes, the gap grows with the number of steps, and the summed self-distortion tracks it.
  intervention: four sampler arms (RS-random, RS-confidence, SF, matched RS = sample-select-resample) at T in {64, 256, 1024}, L = 1024, temperature 1, no top-p, float64 categorical draws.
  primary_metric: paired difference SF - mRS in unigram entropy and GenPPL per T, with the per-run self-distortion Delta logged
  falsifier: SF - mRS within the paired 95% bootstrap interval of zero at every T while Delta >= 0.1 nats per token (self-distortion not predictive), or Delta < 1e-3 nats per token at T = L (E_sel negligible on this checkpoint)
  gpu_hours: about 5 to 9 (estimate; to be replaced by a timed pilot)
```

# E_sel and E_fact^X: definitions, results, estimators

Tags: **[S]** source fact (location), **[I]** inference or derivation here, **[H]** hypothesis,
**[V]** verified by exact enumeration in `analysis/framework/check_selection.py` (check id in
brackets; log `analysis/framework/check_selection.log`). A [V] tag means "checked on toy
distributions", never "true of a model". Logs are natural.

**Summary.** (1) E_sel is well defined only relative to a reference policy. Even then, for
sample-then-filter (SF) it has **no per-step forward decomposition**: the per-step data-side term
is +infinity whenever SF blocks a data-supported (position, value) pair, which happened in
32 of 32 SF configurations tested. (2) The canonical reference is the **matched rank-then-sample
policy** (same position law, values drawn from the marginals). Define E_sel at the output level:
E_sel = KL(q||p_SF) - KL(q||p_mRS). It is finite, signed, zero on rank-then-sample, and equal to
the full 1.288 nats in the framework toy. (3) The measurable object is the reverse, model-only
**self-distortion** D(s) = KL(SF step law || matched-RS step law). It needs no extra forward
pass, is bounded by H(position law) <= log C(N,k), and summed along the sampler's own path it
bounds KL(p_SF||p_mRS). (4) Temperature, top-p, argmax and CFG do not look at sampled values. They
stay inside the published identity with a tilted predictor, and their cost is a separate term,
E_tilt. (5) framework-v1 P2 rests on a false premise: entropy below H(q) can come from E_fact
alone. (6) The cross-modal term has two exact splits. The measurable cross term is the text-first
S = sum_j I(text set; image token j | s), estimated with R extra forward passes per probed step.

---

## T1. Definitions and the decomposition

### T1.1 Setting

Erasure channel. The state is s_n = (z_n, m_n), with M_n the masked positions and N_n = |M_n|.
The predictor gives marginals p^i_n(v) = p_theta(x^i = v | s_n) for i in M_n. One step is a
**commit kernel** kappa(A, y | s): a law over a set A ⊆ M with |A| = k and values y in V^A. Any
randomness beyond s is fresh, independent of the unrevealed tokens given the revealed path. The
kernel has a **position law** rho_kappa(A|s) = sum_y kappa(A, y|s) and a **value law**
kappa(y|A, s) = kappa(A, y|s)/rho_kappa(A|s). The sampler's path law is
P_kappa = prod_n kappa(A_n, y_n | s_n), and p_kappa(x) is its output law. Write q_A = q(x^A | z_n)
and q^i = q(x^i | z_n).

### T1.2 The policies as kernels

- **RS (rank-then-sample)**: kappa = rho(A|s) prod_{i in A} p^i(y^i), with rho a function of s
  plus fresh noise. This covers random (ancestral) order, ranking by max_v p^i, top-1 minus top-2
  margin, entropy, EB-sampler thresholds, and planners that read s only.
- **V1, marginal tilts**: kappa = rho(A|s) prod p~^i(y^i), where p~^i = T_s(p^i) is a state-only
  transform: temperature p^(1/tau)/Z; top-p (keep the smallest set with mass >= pi and
  renormalise); argmax (tau -> 0); CFG p~ = softmax((1 + w) l_cond - w l_uncond), where l_uncond
  comes from a second forward pass on a reduced state (the condition or the other modality
  dropped). CFG costs one extra pass per step but is still a function of the state.
- **V2, sample-then-filter (SF)**: draw Y^j ~ p~^j independently for every j in M, score each draw
  with c_j = g_j(Y^j), keep the top k by (c_j, tie rule) and commit (A, Y^A). Typical scores are
  the sampled token's probability p^j(Y^j) (MaskGIT; LLaDA at temperature above 0, as
  framework-v1 2.4 states) or the sampled token's margin p^j(Y^j) - max_{u != Y^j} p^j(u). Entropy
  and top-1 minus top-2 margin of the marginal are state-only scores, so they are RS. This matches
  the Sample-then-Filter and Rank-then-Sample labels of 2604.00375 Table 1 [S].
- **V3, joint value rules**: kappa = rho ⊗ kappa_joint(y|A, s) with a non-product value law (AR
  head, copula, energy reweighting).
- **Matched RS of a kernel**: kappa° := rho_kappa ⊗ prod_{i in A} p^i. It is implementable at no
  extra cost by **sample, select, resample**: run SF's draw and selection to get A, then commit
  fresh draws Y'^A ~ prod_{i in A} p^i.

### T1.3 Theorem 1: path identity for an arbitrary kernel [I; V T1.1, T1.1b]

Let Q_kappa be the **data path law**: x ~ q; at each data state s_n(x), draw A_n ~ rho_kappa(.|s_n)
with fresh noise and reveal x^{A_n}. Then, in [0, +inf],

    KL(Q_kappa || P_kappa) = E_fact[rho] + E_learn[rho; p] + V[kappa],
    E_fact  = sum_n E_Q[ TC(q_{A_n}) ],
    E_learn = sum_n E_Q[ sum_{i in A_n} KL(q^i || p^i_n) ],
    V       = sum_n E_Q[ KL(q_{A_n} || kappa(.|A_n, s_n)) - KL(q_{A_n} || prod_{i in A_n} p^i_n) ].

*Proof.* The path is the sequence (A_n, y_n). Q's increments are rho(A|s) q(y|A, s) and P's are
rho(A|s) kappa(y|A, s). The position factor is the same in both, so it cancels. The chain rule
gives KL = sum_n E_Q[KL(q_A || kappa_A)]. Adding and subtracting KL(q_A || prod p^i) and applying
KL(P || prod Q_j) = TC(P) + sum_j KL(P_j || Q_j) finishes the proof. ∎

The output law obeys KL(q||p_kappa) = KL(Q_kappa||P_kappa) - G[kappa], with
G[kappa] = E_q KL(Q(path|x) || P(path|x)) >= 0 [V T1.2]. G = 0 for deterministic state-only
policies [V T1.4]; G > 0 for randomised position laws [V T1.5].

Consequences.
- **V1 tilts**: V = E_tilt := E_learn[p~] - E_learn[p] = sum_n E_Q sum_{i in A_n}
  E_{q^i}[log p^i - log p~^i]. The identity is then the published one with p~ in place of p
  [V T5.7, E_tilt = +0.2145 for tau = 0.7]. E_tilt is +inf in the forward direction for argmax
  and for top-p whenever q puts mass outside the kept set [V T5.6].
- **V3 joint draws**: with kappa_joint = q_A, V = -(E_fact + E_learn) and the total is 0. So V is
  signed [V T1.3, 8 negative cases].
- **V2 SF, Proposition 2 (the forward per-step term is infinite).** At k = 1,
  kappa_SF(v | i, s) = p^i(v) Pi_i(p^i(v)) / rho(i), with Pi_i(c) the probability that every
  competitor loses to score c (T2). If some competitor j has every support value scoring at or
  above c = p^i(v), with ties lost, then Pi_i(c) = 0 and SF never commits (i, v), although
  p^i(v) > 0. If the data path reaches s with rho(i|s) > 0 and q(x^i = v | s) > 0, then V = +inf
  and G = +inf. In the framework toy, data paths of Q-mass 0.4265 meet a blocked pair [V T3.12].
  In other random q the mass is 0.38 (exact predictor) and 0.68 (perturbed) [V T5.1]. The forward
  path term was infinite in 32 of 32 SF configurations [V T1.3b]. **Per-step forward accounting
  of E_sel is therefore impossible for SF.** This is the clean negative the brief allowed for.
- **Lemma 3 (support).** Take any x and follow its own-score greedy order. At each state
  consistent with x, the event "every masked position draws its x-value" has probability
  prod_{j in M_n} p^j_n(x^j). On that event SF selects the top-k of x's values and commits them, so

      p_SF(x) >= prod_n prod_{j in M_n} p^j_n(x^j),
      KL(q||p_SF) <= E_q[ - sum_n sum_{j in M_n} log p^j_n(x^j) ] - H(q) < inf

  for full-support (softmax) predictors [V T1.9, T1.3c]. The bound charges cross-entropy for
  every still-masked position at every step, which is O(L^2) terms. That matches the roughly
  quadratic growth of the forward KL in the iid example (T3).

### T1.4 Definition of E_sel, and why the matched-RS reference is canonical

    E_sel[kappa] := KL(q || p_kappa) - KL(q || p_kappa°),
    KL(q || p_kappa) = E_fact[rho_kappa] + E_learn[rho_kappa; p] - G[kappa°] + E_sel[kappa].

The first three terms are the published identity (EB-sampler Eq. 7, App. A.1, randomised-policy
bound, via primer-samplers 2.5 [S]) applied to kappa°, which is an RS policy with a randomised
position law.

Properties: zero on the RS class; finite for full-support predictors (Lemma 3); signed (-0.741
for an over-dispersed model on peaked independent data [V T1.8]; positive in all 32 random SF
configurations, with E_sel values in the log). With exact marginals at k = 1, kappa°
reproduces q exactly, because its path increments are rho(i) q^i. Hence
E_sel = KL(q||p_SF) > 0 [V T1.6], which is 1.288 nats in the framework toy [V T3.11, T3.13].

Why this reference is canonical:
1. **It is the KL projection.** argmin over rho' of KL(kappa_SF || rho' ⊗ prod p) = rho_kappa,
   because KL(kappa || rho' ⊗ prod p) = KL(rho_kappa || rho') + E_rho KL(kappa(.|A) || prod p)
   [I; V T1.7]. It is the unique RS kernel closest to the sampler, and the minimum is D(s) of T3.
2. **No double counting.** "Which positions" is charged to E_fact and E_learn under the position
   law the sampler actually uses; "which values" is charged to E_sel only.
3. **It can be run.** Sample, select, resample uses the same forward passes. With RS-confidence as
   a third arm, the contrasts separate value selection (SF - mRS) from the position law
   (mRS - RS-conf).

Rejected references: (a) the "intended" RS ranking by max_v p, because it changes the position
law and so mixes E_fact and E_learn movement into E_sel; (b) the exact sampler, because E_sel
would then absorb everything; (c) a per-step forward definition, which is +inf (Proposition 2).

**Model-only companion (reverse direction).** The self-distortion is
Delta[kappa] := sum_n E_{P_kappa}[D(s_n)], with D(s) = KL(kappa(.|s) || kappa°(.|s)). The chain
rule on the sampler's own paths gives Delta = KL(P_kappa || P_kappa°) >= KL(p_kappa || p_kappa°)
[V T3.14: 0.996 = 0.996 >= 0.603 in the toy]. Delta is finite (T3) and needs only logits.
**Relation to E_sel: neither equal nor a bound in general.** It points the other way and is
averaged over different trajectories. In the toy E_sel = 1.288 > Delta = 0.996; in the iid
example E_sel grows about quadratically and Delta linearly (T3).

### T1.5 Taxonomy decision

Temperature, top-p, argmax and CFG (including modality-dropout guidance) **are not E_sel**. They
are V1 tilts: inside the identity, costed by E_tilt, a signed change in the E_learn slot. E_tilt
can be estimated from data and logits (T5) and is infinite in the forward direction for
truncations. CFG also changes what the predictor conditions on, and if the guided marginals rank
positions it changes rho, which moves E_fact and E_learn. LLaDA at temperature 0 (argmax value,
ranked by the argmax probability) is pure V1. Only value-dependent selection (V2) is E_sel. Joint
draws (V3) enter the same slot with a negative sign. The lever table needs three value-rule rows
(see the edits at the end).

---

## T2. Law of the committed (position, value) under SF

**Proposition 4 [I; V T2.1, 300 states with exact ties, both scores, random priorities].**
Let F_j^<(c) = sum_u p~^j(u) 1[g_j(u) < c], F_j^<=(c) likewise with <=, and let pi be the tie
priority (a lower value wins). Then at k = 1:

    kappa_SF(i, v | s) = p~^i(v) * prod_{j != i, pi(j) < pi(i)} F_j^<(g_i(v)) * prod_{j != i, pi(j) > pi(i)} F_j^<=(g_i(v)).

For general k, with m = min_{i in A} g_i(y^i) and i* the lowest-priority element of A attaining m:

    kappa_SF(A, y | s) = prod_{i in A} p~^i(y^i) * prod_{j not in A} [ F_j^<(m) + 1{pi(j) > pi(i*)} P_j(g_j = m) ].

With continuous logits, ties have probability 0 and Pi_i(c) = prod_{j != i} F_j(c).

**Proposition 5 (sharpening) [I; V T2.2, T2.3].** At k = 1, with score p^i(Y^i) and tau = 1:
kappa_i(v) = p^i(v) Pi_i(p^i(v)) / rho(i), and Pi_i is nondecreasing. The likelihood ratio
kappa_i/p^i is therefore nondecreasing in p^i(v), so kappa_i majorises p^i (by Chebyshev's sum
inequality on the sorted partial sums), and every Renyi entropy falls: H_a(kappa_i) <= H_a(p^i).
The margin-of-sampled-token score is also monotone in p^i(v), so the same holds for it. With a
tempered draw and an untempered score, kappa_i ∝ p~^i Pi_i(p^i): the tilt and the sharpening
compose.

**At k >= 2 the committed values are coupled** through the minimum score, so kappa(y|A) is not a
product (max TC 0.0885 nats over 400 random states [V T2.7]). Selection creates dependence inside
the set that has nothing to do with q.

**Equality with RS.** kappa_SF = kappa° at s if and only if, for every A with rho(A) > 0, the
selection weight is constant on the support of the product on A. At k = 1 this means Pi_i is
constant on {g_i(v) : p^i(v) > 0}. Sufficient cases [V T2.4-T2.6]: one masked position; k = N;
p^i flat on its support (uniform predictions included, where the tie rule alone selects, which
is state-only); no competitor score lies between min_v g_i(v) and max_v g_i(v); one-hot
marginals (a perfect denoiser on deterministic data).

**Limits.**
- (a) **Many positions, identical marginals** (random ties): the committed value has the
  max-of-N law in score order, r_N(v) = (F(v) + p(v))^N - F(v)^N with F(v) = p{u : p(u) < p(v)}
  [V T2.8]. P(commit the mode) = 1 - (1 - p_max)^N, and KL(r_N||p) rises to -log p_max
  [V T2.9, T3.8: nondecreasing and <= -log p_max for 300 random p, N <= 64; no proof]. SF
  therefore interpolates between RS (N = 1) and confidence-ranked argmax (N -> infinity) [I].
- (b) **Large vocabulary, diffuse marginals** (p_max -> 0): the per-step distortion tends to the
  continuous value

      KL_cont(N, k) = log C(N, k) - (N - k)(H_N - H_{N-k})     (H_n harmonic numbers; k = 1: log N - 1 + 1/N).

  *Proof.* With U_j iid uniform and the top-k set A, U_A given A has density C(N,k) m^(N-k),
  where m ~ Beta(N - k + 1, k) and E log m = -(H_N - H_{N-k}). Discrete tokens are quantile bins
  in score order, so by data processing D <= KL_cont for any marginal under random ties. ∎
  Verified within 0.1 percent at V = 150 (k <= 2) and V = 60 (k = 3), and as a bound for 300
  random p [V T3.6, T3.7]. The k = 1 case is the best-of-N law with the token's own probability
  as the reward.

---

## T3. Size

**Universal per-step bound [I; V T3.1, T3.2].** D(s) <= H(rho(.|s)) <= log C(N, k).
*Proof.* Let Y ~ prod_{j in M} p^j (plus tie noise U), with A a function of (Y, U). Then
KL(law(Y_A | A = a) || prod_{i in a} p^i) <= KL(law(Y, U | A = a) || law(Y, U)) = log 1/rho(a),
by projection and conditioning on an event. Averaging over a gives D <= H(rho). ∎ At k = 1 this
sharpens to D = H(rho) + E_kappa[log Pi_I(p^I(Y))], with log Pi <= 0 [I].

**iid closed forms [V T3.3-T3.9].** At k = 1 with random ties, D = KL(r_N||p) <=
min(log N - 1 + 1/N, -log p_max). With index ties, D >= KL(r_N||p), because the position-value
coupling adds. Over a whole k = 1 run on N iid positions (V = 3, p = (0.45, 0.35, 0.20)):

| N | KL(q‖p_SF) = E_sel | KL(p_SF‖q) | Δ = Σ_m KL(r_m‖p) | fine-V value log N! − N + H_N |
|---|---|---|---|---|
| 8 | 6.334 | 2.840 | 3.801 | 5.322 |
| 16 | 29.33 | 8.325 | 10.12 | 18.05 |
| 32 | 120.0 | 20.24 | 22.89 | 53.62 |
| 64 | 472.7 | 44.93 | 48.45 | 145.9 |

E_sel grows about quadratically (472.7/120.0 = 3.94). Delta grows at most linearly, with
per-token value <= -log p_max = 0.799 [V T3.10, T3.10b].

**Steps at fixed length [V T3.10c, T3.15, T3.16].** On iid data (E_fact = 0, L = 24), SF's
forward KL rises as k falls: 0, 2.38, 6.46, 10.35, 17.41, 23.83, 35.55, 67.44 for
T = 1, 2, 3, 4, 6, 8, 12, 24 steps. In a Markov toy (L = 6, flip 0.1, exact marginals), the
RS-confidence error falls 1.840, 0.568, 0.137, 0 as T = 1, 2, 3, 6. SF's error is **U-shaped**,
1.840, 1.025, 0.836, 1.535, and E_sel is +0.451, +0.652, +1.535 at T = 2, 3, 6. E_fact falls
with the number of steps and E_sel of SF rises with it, so there is an interior optimum. MaskGIT
reports an iteration sweet spot (Table 3, Fig. 8, via primer-samplers 2.8 [S]); our toy is
consistent with that but is not a test of MaskGIT.

**The [V] toy decomposed [V T3.11-T3.14].** KL(q||p_SF) = 1.288069. E_fact = E_learn = 0 and
KL(q||p_mRS) = 4e-16, so **all 1.288 nats are E_sel**. The forward path term is +inf (blocked
Q-mass 0.4265). The reverse is Delta = 0.996 >= KL(p_SF||q) = 0.603, inside the bound
log 4! = 3.178.

**Answer to "vanish, bounded or grow".** E_sel vanishes only in the equality cases (N = 1, k = N,
flat or one-hot marginals) and goes to 0 as k -> N. Per step, the reverse distortion is bounded:
by log C(N, k) in general, and by -log p_max for iid marginals at k = 1. E_sel grows with the
number of competitors N, with the number of selection rounds T at fixed L, and, in the forward
direction, about quadratically in L in the iid example. Vocabulary matters through the shape of
the marginals: diffuse marginals approach KL_cont, peaked ones give little. The size on a real
checkpoint is open (T9).

---

## T4. Entropy

**(a) Output entropy under SF <= under matched RS.**
- Per state at k = 1: **true**. H(kappa) = H(rho) + sum_i rho(i) H(kappa_i) <= H(rho) +
  sum_i rho(i) H(p^i) = H(kappa°), by Proposition 5 [I; V T4.1, 3000 states].
- Per state at k = 2: no violation in 3000 random states, but no proof [V search only].
- At the output: **false**. Counterexample [V T4.2]: x1 in {0,1} with probability 0.7/0.3, x2
  uniform, x3 and x4 uniform if x1 = 0 and both 0 otherwise. With exact marginals at k = 1,
  H(p_SF) = 3.344 > H(p_mRS) = H(q) = 3.248. Sharpening x1 toward 0 steers the sampler into
  higher-entropy futures. In 40 random q, SF was lower in all 40, so a lower entropy is typical
  but not guaranteed.

**(b) Multi-step state-only policy with exact marginals has H(p) >= H(q): false.**
Counterexample [V T4.3; closed forms match to 5 decimals]. Take x1, x2 in {0,1} with
P(x1 = x2) = 1 - eps. Given x1 = x2, x3 and x4 are iid uniform on V' values; otherwise
x3 = x4 = 0. Commit {x1, x2}, then {x3, x4}. Then H(p) = 2 ln 2 + ln V' and
H(q) = ln 2 + h(eps) + 2(1 - eps) ln V', while KL(q||p) = E_fact = ln 2 - h(eps). At eps = 0.1
and V' = 4: H(p) = 2.773 < H(q) = 3.514, KL = 0.368. The deficit
h(eps) - ln 2 + (1 - 2 eps) ln V' **grows without bound** in V' while KL stays below ln 2.

What survives: the one-shot product has entropy >= H(q) [V T4.4]; at k = 1 with exact marginals,
H = H(q); a deterministic RS sampler has H(p) = sum_n E_P[sum_{i in A_n} H(p^i_n)] exactly,
because its path is a function of x [I], which is computable from logits. The failure needs
structure: none of 300 random q with a fixed 2+2 partition showed it [V]. The mechanism is that
the product draw visits states that are rare under q and have lower conditional entropy.
**Consequence: P2's diagnostic, as stated against H(q), falls.**

---

## T5. Estimators from model outputs

| Quantity | Formula | Needs | Status |
|---|---|---|---|
| Self-distortion Δ (reverse) | Σ_n D(s_n) on the sampler's own trajectories; k = 1: D = Σ_i Σ_v p^i(v) Π_i log Π_i + H(ρ), ρ(i) = Σ_v p^i(v) Π_i(p^i(v)) | logits only, 0 extra passes | exact per state [V T5.2]; MC = exact (1.0303 ± 0.0008 vs 1.0304; per-path sd 0.110) [V T5.3]; bounds Δ ≥ KL(p_SF‖p_mRS) |
| Entropy deficit on own states (k = 1) | Σ_n Σ_i ρ(i) [H(p^i) − H(κ_i)] ≥ 0 | logits only | from T4.1 [I] |
| E_tilt (V1) | per data token, log p^i(x^i) − log p~^i(x^i) on data-driven trajectories | data + 1 pass per step (2 with CFG) | exact identity [V T5.7]; +inf for argmax or top-p if any data token is cut [V T5.6] |
| Argmax | D = Σ_{i∈A} −log max p^i; with a deterministic ρ, Σ D = −log p_RS(x*) exactly | logits | [V T5.5] |
| Temperature | D = Σ_{i∈A} KL(p~^i‖p^i), closed form | logits | [I] |
| Forward per-step SF term | log ρ(i) − log Π_i(p^i(x^i)) | data + logits | **unusable**: +inf with probability 0.38 to 0.68 in the toys [V T5.1] |
| E_sel (output level) | KL(q‖p_SF) − KL(q‖p_mRS) | sampler output likelihoods (marginalise over paths) | not computable from logits; measure the SF − mRS contrast externally (T9) |

**Computing D at k = 1 for N masked positions and vocabulary V.**
1. Sort each row of p ascending and take prefix sums, so F_j(c) = mass strictly below c:
   O(N V log V).
2. Evaluate log F_j on a log-spaced grid of G thresholds and sum over j: O(N G log V).
3. log Pi_i(c) = (grid sum at c) - log F_i(c). Because F_j is monotone, the neighbouring grid
   points give exact lower and upper brackets. Track the count of j with F_j = 0 separately.
4. Restrict v to the top-K values of each row. The tail is bracketed by the tail mass, because
   F_j(c) is exact when c exceeds j's K-th largest probability and is otherwise within the tail
   mass [V T5.4].

No extra forward passes are needed; memory is O(N V).

**For k >= 2:** a lower bound is D >= sum_i P(i in A) KL(kappa_i^(1) || p^i), from
KL(P || prod Q) >= sum KL(P_i || Q_i). Each kappa_i^(1)(v) ∝ p^i(v) P(#{j != i : c_j > p^i(v)}
<= k - 1), a Poisson-binomial tail computed on the grid in O(N G k). The upper bound is
log C(N, k), and KL_cont(N, k) is the diffuse-vocabulary reference.

**Variance.** Each D(s) lies in [0, log C(N, k)], so the per-path spread is bounded; in the toy
the per-path sd is 0.110 against a mean of 1.030.

---

## T6. E_fact^X: cross-modal term

Let a = x^{A^T} (the text tokens of the set) and b = x^{A^I} (the image tokens). Two exact splits
hold [I; V T6.1, max error 1.3e-15 over 500 random q]:

    TC(A|s) = TC(a|s) + TC(b|s) + X,          X = I(a; b | s)                 (symmetric)
    TC(A|s) = TC(a|s) + S + TC(b | a, s),     S = sum_{j in A^I} I(a; b_j | s)  (text first)

*Proof of the second.* Expand H(b|a) and add and subtract sum_j H(b_j | a). ∎
Hence X - S = TC(b|a,s) - TC(b|s), which takes either sign (X > S in 388 of 500 random q
[V T6.2]). If the image tokens are conditionally independent given the text, X <= S
[I; V T6.3]. The pairwise sum P = sum_{i,j} I(a_i; b_j | s) satisfies P <= S when the text tokens
are mutually independent given s, because I(a; b_j) = sum_i I(a_i; b_j, a_{<i}) >= sum_i I(a_i; b_j)
[I; V T6.4]. In general P - S also takes either sign (S < P in 58 of 500).

**Estimator (reveal and requery).**

    S^ = (1/R) sum_r sum_{j in A^I} KL( p_theta(b_j | s, a^(r)) || p_theta(b_j | s) ),

with analytic KL over the vocabulary, so the variance comes only from a. One requery returns
every image marginal, so the cost is **R extra forward passes per probed step, whatever k_I is**.
The image-first S_{I->T} costs another R. Under an exact model with a drawn from the joint
q(a|s), S^ is unbiased for S [V T6.5]. Drawing the joint needs k_T sequential passes. Drawing a
from the product of marginals, which is what the sampler commits, costs nothing but is biased by
at most ||f||_inf sqrt(TC(a|s)/2) (Pinsker) [I]; in the toy, 0.6057 against 0.6152 with
TC(a|s) = 0.003 [V print]. The pairwise P needs k_T R passes and the symmetric X needs sequential
reveals inside b, so neither is practical at scale. **Recommend S_{T->I} and S_{I->T}.**

**When p_theta is not exact.** The estimator returns the model's S_theta: how much the model would
move its image marginals had it seen the co-committed text. This is the model's own price of
co-commitment. It equals S if the model is exact. In general S_theta^{T->I} and S_theta^{I->T} need
not satisfy the symmetric relation, and the disagreement diagnoses conditional inconsistency.

What S_theta still tells us:
- S_theta near 0 means the model sees no reason to sequence the two modalities.
- A front-loaded S_theta supports the P5a premise under the model.
- It does not certify q's S, and it is measured on sampler states, not data states (as with
  E_learn). P5b's cost claim still needs the matched joint-against-sequential contrast.

---

## T7. Memory

**Proposition [I; V T7.1].** With s_n = (z_n, m_n), suppose the memory update
m_{n+1} ~ mu(. | s_n, A_n, y_n, fresh noise) is the same mechanism under Q and P. Then

    KL(Q_aug || P_aug) = E_fact + E_learn,   with E_learn terms KL( q(x^i | z_n) || p_theta(x^i | z_n, m_n) ).

The q side conditions on z_n only. This is valid because the memory and the policy noise are
independent of the unrevealed tokens given the revealed path. For x,
KL(q||p) = KL(Q_aug||P_aug) - G with G = E_q KL(Q(path|x) || P(path|x)), and equality holds iff
G = 0.

| Case | Result |
|---|---|
| Deterministic rho, memory a function of the revealed path | equality for x [V T7.2] |
| Random rho, memory a function of the revealed path | strict inequality, gap 0.143 [V T7.3] |
| Fresh random memory used by the predictor | strict inequality, gap 0.089 [V T7.4] |
| Fresh random memory ignored by the predictor and the policy | equality [V T7.5] |

**Correction to framework-v1 2.1:** the identity holds on the augmented path, as stated. "Only
when" is too strong, and "a function of the revealed path" is not enough on its own. Equality
for x holds when the augmented path (positions, values, memory) is almost surely a deterministic
function of x, which is sufficient, not necessary; otherwise the identity is an upper bound with
gap G. Self-conditioning, whose memory is the previous prediction, is deterministic, so with a
deterministic order the identity is exact.

---

## T8. Exact checks

Command (from the worktree root, numpy only, about 15 s):

    python analysis/framework/check_selection.py > analysis/framework/check_selection.log

Log: `analysis/framework/check_selection.log`, 61 checks, **0 failures** ("ALL CHECKS PASSED").

The checks enumerate L = 3 to 6 positions with V = 2 to 4 values. They use many random q (Dirichlet
0.05 to 1.0), exact predictors and perturbed ones (state-seeded log-normal tilt, sd 0.3 to 0.5),
index and random tie rules, k = 1 to N, and probability and margin scores. Check ids map to
sections as follows:
- T2: T2.1-T2.9
- T3: T3.1-T3.16
- T1: T1.1-T1.9
- T4: T4.1-T4.4
- T5: T5.1-T5.7
- T6: T6.1-T6.5
- T7: T7.1-T7.5

The framework toy (primer-samplers-check C) is reproduced exactly (1.288069). The script follows
the conventions of `check_decomposition.py` and `primer-samplers-check.py`: index tie-breaking,
-1 for a mask, exact recursion over states.

---

## T9. Staged measurement spec (Paper 2), frozen checkpoint, 12 GB GPU

**Checkpoint candidates.** All are E0 and unverified; nothing has been downloaded.
- (1) MDLM trained on OpenWebText, about 130M parameters, L = 1024, GPT-2 tokenizer. My
  recollection of the Hugging Face id is `kuleshov-group/mdlm-owt`; verify it. It is the model
  family used for the GenPPL and entropy results of Zheng et al. and ReMDM (primer-samplers 2.7,
  2.10 [S]). It fits easily in 12 GB.
- (2) LLaDA-8B: 16 GB in bf16 by arithmetic, so it needs 4-bit loading and a download above
  5 GB, which requires the user's yes.
- (3) UniDisc 1.4B interleaved, `aswerdlow/unidisc_interleaved` (E1, primer-multimodal Q5):
  5.63 GB, which also requires the user's yes.

**Algorithm 1, SF-STEP-STATS** (input: probability matrix P of shape N x V, k, grid G, top-K;
output: rho, D or bounds on it, entropy deficit). Lines:
1. Sort the rows of P and take prefix sums.
2. Compute log F_j on the grid, with zero counts tracked.
3. Sum over j.
4. For each i and each top-K value v, bracket log Pi_i(p^i(v)).
5. rho(i) = sum_v p^i(v) Pi_i, with the tail bracket.
6. D = sum p Pi log Pi + H(rho) at k = 1; at k > 1, the Poisson-binomial lower bound and
   log C(N, k).
7. Entropy deficit = sum_i rho(i) [H(p^i) - H(kappa_i)].

Cost O(N V log V + N G log V + N K), 0 forward passes. Acceptance test: it must match
`sf_closed` of check_selection.py to 1e-9 on random N <= 5, V <= 6.

**Algorithm 2, STEP(arm)**, using Algorithm 1 for logging. The arms are:
- RS-rand: uniform k positions, values sampled.
- RS-conf: top-k by max_v p, values sampled.
- SF: draw all masked positions, take the top-k by the sampled-token probability, commit the
  draws.
- mRS: as SF to select A, then fresh draws at A.
- V1 controls: RS-conf with tau = 0.9, and RS-conf with argmax.

All arms make one forward pass per step. Categorical draws must be in float64, because 32-bit
Gumbel draws truncate and sharpen (Zheng et al. Table 2, via primer [S]). Use common random
numbers: SF and mRS share the selection draw.

**Algorithm 3, RUN.** For each arm, each T in {64, 256, 1024} (k = L/T), and n = 256 seeds:
generate unconditionally and log per step k, N, D, the entropy deficit,
sum_{i in A} H(p^i) and sum_{i in A} -log p^i(committed). Per sample, compute Delta, the path
entropy, unigram entropy, and GenPPL under an external AR model (GPT-2 Large, as in the
literature, E0). MAUVE against OWT is optional.

**Algorithm 4, DATA-TILT.** On 256 OWT validation sequences, run data-driven trajectories with
RS-conf rho and accumulate log p - log p~ for tau = 0.9 (E_tilt). Argmax is reported as infinite
if any data token is not the argmax.

**Algorithm 5, XMODAL-PROBE (stage D, after the user's approval).** For UniDisc joint generation
with N = 32 steps, at every 4th step draw R = 4 text sets from the marginals, requery, and compute
S^_{T->I}; repeat for S^_{I->T}; use 128 samples. Extra passes: 2R per probed step.

**Ablation map (what each contrast removes, and what theory predicts).**
- SF - mRS removes value dependence; it predicts E_sel, typically lower entropy and lower GenPPL,
  with the gap growing with T. The sign is not guaranteed (T4a).
- mRS - RS-conf removes the randomised position law; it predicts only E_fact and E_learn
  movement and no E_sel.
- RS-conf - RS-rand isolates the position rule (Kim et al. type E_learn effects).
- Tilt arms - RS-conf measure E_tilt, which can be estimated from data (Algorithm 4).

**Predictions [H], to be preregistered.**
- H1: Delta(SF) > 0, increasing in T, below the sum of log C(N_n, k_n), and far below the
  diffuse-vocabulary curve because LM marginals are peaked.
- H2: SF - mRS gives lower unigram entropy and lower GenPPL, with the gap growing in T.
- H3: at T = L, |mRS - RS-conf| < |SF - mRS| on both metrics.
- H4: Delta tracks the entropy gap SF - mRS (Spearman > 0 across arms and T).
- H5: SF's quality-against-T curve has an interior optimum while RS-conf's is monotone (the
  Markov toy, T3).

**Falsifiers.**
- F1: SF - mRS lies within the paired 95% bootstrap interval of zero at every T while Delta is
  at least 0.1 nats per token. Then the self-distortion is not predictive.
- F2: Delta is below 1e-3 nats per token at T = L. Then E_sel is negligible on this checkpoint,
  and the E_sel shares in P2 and P3 are moot for it.
- F3: |mRS - RS-conf| > |SF - mRS| at T = L. Then SF's effect runs through the position law, not
  value selection.

**Cost (estimate, unmeasured).** 6 arms x (64 + 256 + 1024) steps x 256 samples = 2.06M
sequence passes at L = 1024. Assuming batch 32 at 0.15 to 0.3 s per batched pass on the laptop
GPU, that is about 3 to 5.5 h, plus Algorithm 1 overhead (sorting N x 50257 per step). Total about
5 to 9 GPU-hours. GenPPL on 4,608 samples adds about 0.2 h. Stage B0 times 10 samples at T = 64
before the full run. Stage D: about 8,192 extra passes, under 1 GPU-hour (estimate).

---

## T10. Attribution and novelty

| Result | Closest statement in the files read | Ours is |
|---|---|---|
| Theorem 1, path identity for any kernel with the value term V | EB-sampler Eq. 7, App. A.1 (state-dependent φ, values from p_θ) [S via primer] | a corollary (chain rule); the general-kernel form was not found in the files read |
| V1 tilts inside the identity, E_tilt | Zheng et al. Fig. 10, Prop. 5.2 (temperature and truncated-Gumbel sharpening measured or derived) [S via primer] | a corollary; the classification was not found |
| Proposition 2: forward per-step E_sel infinite for SF | none | not found in the files read |
| Lemma 3, support and O(L²) bound | none | not found; elementary |
| Matched RS as the canonical reference, its KL projection, sample-select-resample | 2604.00375 Table 1 names SF against RS informally [S] | not found in the files read |
| Proposition 4, law of the SF commit; Proposition 5, majorisation | MaskGIT and LLaDA describe the rule only [S via primer]; Zheng Prop. 5.2 gives a different sharpening mechanism (precision) | not found; the majorisation-to-entropy step is standard (Schur concavity) |
| iid k = 1 law and KL(r_N‖p) ≤ log N − 1 + 1/N | order statistics; I recall a best-of-n alignment bound with this value (outside the files read, E0, verify before citing) | likely a restatement for k = 1; KL_cont(N, k) for general k not found |
| D ≤ H(ρ) ≤ log C(N, k) | none | not found; elementary |
| U-shape (E_fact falls, E_sel rises with T) | MaskGIT sweet spot (Table 3, Fig. 8) with a diversity hypothesis [S via primer] | not found as a mechanism; toy only |
| T4(b) counterexample | framework-v1 P2 (our own text) | new against our own claim; elementary |
| 2604.00375 Prop. 1, 2 | Prop. 2: H(X) ≤ L h_V(δ) for a (1 − δ)-gated decoder; the proof (App. H.2) assumes committed tokens are conditionally independent with the commit distribution's law [S, read] | different: an absolute entropy cap from the gate threshold, with no reference sampler and no distortion relative to the marginals. Its independence step does not hold for SF at k ≥ 2 (T2.7), and its "commit distribution" would have to be κ_i, not p^i, for SF. Our results give the SF law, the distortion against matched RS, and signs and counterexamples. Theirs bounds what any gated sampler can reach |
| T6 splits, S and the requery estimator | UniDisc Fig. 24 (distance between conditional and unconditional logits, whole-modality drop) [S via primer]; IMDM Eq. 6 (model-dependent TC) [S via primer]; primer-multimodal Q5 sketch (internal) | splits are the chain rule (textbook); a per-step cross-modal measurement was not found |
| T7 | EB-sampler Eq. 10 (data processing) [S via primer] | a corollary; the "only when" counterexample is elementary |

---

## What framework-v1 must change (numbered edits)

1. **2.1, memory sentence.** Replace with: "With a memory m_n updated by the same mechanism on
   data and sampler paths, the identity holds with equality on the augmented path, with E_learn
   evaluated as KL(q(x^i|z_n) || p_theta(x^i|z_n, m_n)). For x it is an equality iff
   E_q KL(Q(path|x) || P(path|x)) = 0. That holds when the augmented path is a deterministic
   function of x (deterministic policy, memory computed from the revealed path), and otherwise
   the identity is an upper bound." [V T7]
2. **2.1, "Equality for deterministic policies".** Add "...and memory that is deterministic
   given the revealed path".
3. **2.4, opening list.** Remove "argmax or low temperature" and "guidance" from the rules that
   break the identity. They are state-only tilts, exact inside it with p~ in place of p. Only
   value-dependent selection (sample-then-filter, sampled-token margin) breaks the precondition.
   [T1.2, T1.5]
4. **2.4, definition.** Replace "Define E_sel as the divergence between..." with the T1.4
   definition, E_sel = KL(q||p_kappa) - KL(q||p_kappa°) with kappa° the matched RS (same position
   law, values from p_theta), and the split KL(q||p) = E_fact + E_learn - G° + E_sel. Add:
   "E_sel has no per-step forward form for sample-then-filter (the per-step term is +inf
   whenever a data-supported pair is blocked) [V]; the measurable companion is the model-only
   self-distortion Delta = sum_n E_P KL(SF step || matched-RS step) <= sum_n log C(N_n, k_n),
   which bounds KL(p_SF||p_mRS)."
5. **2.4, toy sentence.** Add the decomposition: all 1.288 nats are E_sel (E_fact = E_learn = 0,
   KL(q||p_mRS) = 4e-16); the self-distortion is 0.996 >= KL(p_SF||q) = 0.603 [V T3.11-T3.14].
6. **2.4, new paragraph.** Add the SF commit law and sharpening (Propositions 4 and 5), the
   coupling at k >= 2, the bounds D <= H(rho) <= log C(N,k) and KL_cont, and "E_sel of SF grows
   with the number of selection rounds while E_fact falls; toy optimum at an interior T" [V T3].
7. **2.4, 2604.00375 sentence.** Make it precise: "Prop. 2 caps output entropy for gated decoders
   assuming committed tokens follow the commit distribution independently; it is not a statement
   about distortion relative to the marginals and does not cover sample-then-filter's value
   law."
8. **2.2.** Add the text-first split TC = TC(a) + S + TC(b|a) and name S as the measurable cross
   term, estimated by reveal and requery (R passes per probed step), with the caveats that it
   measures the model's S_theta on sampler states and that X - S is not sign-definite [V T6].
9. **P2.** Delete "This is exact for a one-shot product ... open item for method-architect (6.1)"
   and the implication "improvement with entropy below the reference indicates E_sel". Replace
   with: "Entropy below H(q) can come from E_fact alone, with an unbounded deficit at
   KL <= ln 2 [V T4.3]. SF's entropy is below that of its matched-RS twin at every state (k = 1)
   but not always at the output [V T4.1, T4.2]. Diagnose E_sel by the SF - mRS contrast at
   matched passes and by the self-distortion Delta, not by entropy against a reference."
10. **P3.** Replace "The E_sel share is diagnosable: it comes with entropy below the reference"
    with the contrast-based diagnosis of edit 9. Reclassify ReMDM's top-p 0.9 as a V1 tilt
    (E_tilt), not E_sel.
11. **P1.** Add: "the gain that remains at k = 1 estimates the E_learn part only for state-only
    rules with sampled values and fixed tilts; under sample-then-filter E_sel is largest at
    k = 1."
12. **Lever table.** Split the value-rules row into:
    - marginal tilts (temperature, top-p, argmax, CFG): signed E_tilt, +inf forward for
      truncations, costs diversity and, for CFG, one extra pass per step;
    - value-dependent selection (sample-then-filter): E_sel, grows with steps, no extra passes;
    - joint draws: keep the existing row, noting that they enter the same slot with a negative
      sign.

    Move "guidance, including modality dropout" to the tilt row, keeping its re-conditioning
    note.
13. **C4 (section 1).** Name the four value-rule classes (RS, V1 tilt, V2 selection, V3 joint)
    and the matched-RS construction.
14. **Section 5.** Under "Claim", add the E_sel definition with its reference and the
    per-step-impossibility result. Under "Cannot claim yet", keep the size of E_sel, E_tilt and
    S on any checkpoint.
15. **Section 6.** Mark open item 1 done, pending red-team. Add two open items: proof of the
    per-state entropy inequality at k >= 2, and monotonicity of KL(r_N||p) in N.
