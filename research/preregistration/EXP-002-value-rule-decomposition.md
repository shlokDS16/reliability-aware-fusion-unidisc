```yaml
agent: experiment-designer
date: 2026-10-14
brief: Preregistration card EXP-002. Decompose the effect of sample-then-filter (SF) decoding at k >= 2 tokens per step into per-position sharpening and joint coupling, on frozen pretrained masked-diffusion text models (MDLM-OWT primary, LLaDA-8B-Instruct secondary), at matched forward passes and matched output entropy.
card:
  id: EXP-002
  version: v0.1
  status: draft, unsigned
  signatures: {statistician: none, red-team: none}
  frozen: false          # frozen when both sign; afterwards changes only as a new version with a change log (section 19)
  hypothesis_ledger_ids: to be assigned when the rows are added (H1, H1b, H2, H3, H4, H5); no ledger rows written by this draft
sources_examined:
  - research/CONTRACT.md
  - research/review/framework-v2.md (A, B, C [P1, P3], D [D4], E)
  - research/review/method/selection-term.md (T1.2, T2 [Prop. 4, Prop. 5], T9; T1.4/E_sel and E_tilt NOT used, withdrawn by D0011)
  - research/review/audits/2026-10-14-red-team-selection-term.md (F1, M1, M5, M7, block C; M6 for P1 wording)
  - research/review/dossier/prior-art-2605.12522-experiments.md (all)
  - research/review/dossier/prior-art-selection.md (P2 2609.34509 lines 207-230, caveat list lines 290-297)
  - analysis/framework/check_coupling_k2.py and .log (toy prior, supplied by the orchestrator, [V] toy only)
  - research/preregistration/EXP-001-crossmodal-unidisc.md (card format only)
  - research/ledgers/decisions.jsonl D0012 (download limit lifted; experiment order)
coverage: >
  Read in full at the sections named. NOT read: the MDLM, LLaDA, MaskGIT or 2605.12522 code (everything about
  their samplers is taken from the dossier files, E3 at the SHAs those files state, or from memory and
  marked [A]); the papers 2609.34509 and 2510.04525 beyond what the dossier states; runs/env-2026-10-14/setup.md
  does not exist yet (section 3 lists what it must supply). Nothing in this card has been run.
claims:
  - statement: "arXiv 2605.12522 compares SF with its resampled twin only at one token per step, on a 120M model trained from scratch, with no temperature sweep, no step sweep, no entropy-matched frontier and no tilted twin."
    status: supported
    evidence: research/review/dossier/prior-art-2605.12522-experiments.md Q2, Q3, Q6 (code @8bafc9e)
    level: E3
    confidence: 0.85
  - statement: "arXiv 2609.34509 compares SF (LCR) with a max-probability ranker (TPP) at one token per step on LLaDA-8B-Instruct with T in {0.6, 0.8, 1.0, 1.2}; no k >= 2, no resampled twin, no tilted twin."
    status: supported
    evidence: research/review/dossier/prior-art-selection.md P2 (lines 207-222)
    level: E2
    confidence: 0.8
  - statement: "At k = 1 the SF commit law equals a position-dependent state-only tilt; at k >= 2 the value law given the set is not a product."
    status: supported
    evidence: red-team block C (max diff 5.6e-17); check_coupling_k2.log (k = 1 max |A1 - A3| = 2.2e-16); selection-term.md Prop. 4 and T2.7 (max TC 0.0885 nats over 400 random states)
    level: E4 (toy)
    confidence: 0.9
  - statement: "Toy prior (L = 4, V = 3, 12 random q, exact conditional marginals), k = 2: sharpening KL(A3) - KL(A2) = +0.497 mean, positive in 12 of 12; coupling KL(A1) - KL(A3) = -0.016 mean, negative in 10 of 12; entropy H(A1) - H(A3) = -0.007 mean."
    status: supported
    evidence: analysis/framework/check_coupling_k2.log (summary lines)
    level: E4 (toy)
    confidence: 0.9
  - statement: "H1 to H5 of section 2."
    status: unknown
    evidence: none (predictions)
    level: E0
    confidence: 0.3
competing_explanations:
  - estimator error of the tilted twin A3 (quadrature or binning error manufactures a coupling effect)
  - SF's per-position effect is a state-dependent temperature, removed by entropy matching, so only noise remains
  - metric artifact (GPT-2 Large favours repetitive text at equal unigram entropy; unigram entropy matches while longer-range repetition differs)
  - interpolation artifact (curvature, sparse cells, calibration error)
  - visited-state shift (arms share a position law but not a state distribution, so contrasts are total kernel effects, not one-step effects)
  - precision artifact (32-bit categorical draws truncate and sharpen)
  - quantisation artifact on LLaDA-8B
unknowns: [section 3 list; the pilot sigma that sets n (section 9.6); whether MDLM-OWT reaches the reference entropy at all arms within the tau range]
next_test: {hypothesis: "H1 (coupling), H2 (decomposition)", intervention: "value rule at matched passes, positions and per-position marginals: A1 SF, A2 resampled twin, A3 tilted twin, A4 confidence rank-then-sample", primary_metric: "log GenPPL (GPT-2 Large) at the reference unigram entropy h*, contrast A3 minus A1", falsifier: "section 11", gpu_hours: "formulas in section 12; about 38 at n_B = 1000 and t_f = 7 ms [A] for the MDLM part"}
```

# EXP-002: value-rule decomposition of sample-then-filter at k >= 2 tokens per step (H1 to H5)

Tags: [S] source fact, [I] inference, [H] hypothesis, [A] assumption until the pilot or setup.md, [V] verified on a toy.
Nothing in this card has been run. Every number marked [A] is replaced by a pilot or setup estimate before
the card is frozen, and the replacement rule is stated next to it. Toy numbers are priors for direction and
size of effect only; they do not transfer to a 130M or 8B network.

## 0. Summary

One frozen checkpoint per model, no training. Unconditional text from MDLM-OWT (L = 1024), plain sampling
(no top-p, no guidance, no Gumbel noise on the ranking), exactly k committed positions per step with
T = L/k steps, k in {1, 2, 4, 8, 16}. Four arms share the forward pass, the tempered marginals and the tie
rule at every state: A1 SF; A2 its resampled twin; A3 its tilted twin (SF's position law and SF's
per-position value law given the set, values drawn independently); A4 confidence rank-then-sample. The
contrasts A2 - A3 (per-position sharpening), A3 - A1 (joint coupling, the new quantity) and A2 - A1 (total)
are read at a fixed output entropy h*, by interpolation along each arm's temperature curve, because a bare
comparison at one temperature mixes the entropy lost to sharpening with everything else. The single primary
endpoint is the GPT-2 Large log generative perplexity at h*, contrast G_cp(k) = Y(A3) - Y(A1). The design is
sized for a small coupling effect (0.03 log-GenPPL units) because the toy prior says coupling is small next to
sharpening and mostly beneficial. A second model (LLaDA-8B-Instruct, 4-bit, GSM8K) is a direction check with
a stated, large minimum detectable effect. Stages run in order of information per GPU-hour, with gates.

## 1. Claim contract

### 1.1 Claim, one sentence

On a frozen pretrained masked-diffusion text model at matched forward passes and matched output entropy,
the quality difference between sample-then-filter and its resampled twin splits exactly into a per-position
sharpening part (A2 - A3) and a joint coupling part (A3 - A1), and the coupling part is non-zero and grows
with the number of tokens committed per step.

### 1.2 Mechanism and definitions

[I from selection-term.md Prop. 4, Prop. 5, T2.7; V toy]. At one step with masked set M (N = |M|), tempered
marginals P_j, score g_j(v) = P_j(v) (primary), SF draws Y_j ~ P_j for every j in M, ranks by (g_j(Y_j) desc,
priority pi_j asc) and commits the top k. Its commit law kappa_SF(A, y) factors as

    kappa_SF(A, y | s, pi) = prod_{i in A} P_i(y_i) * W_A(m(y)),
    W_A(m) = prod_{j not in A} [F_j^<(m) + 1{pi_j > pi_{i*}} P_j(g_j = m)],   m = min_{i in A} g_i(y_i),

with i* the member of A that attains m and has the lowest tie priority, F_j^<(c) = sum_v P_j(v) 1[g_j(v) < c]
(Prop. 4, exact to 3e-16 on enumerations). Consequences:
- position law rho(A) = sum_y kappa_SF(A, y);
- value law given the set kappa(y | A) is NOT a product for k >= 2, because every member's value is
  conditioned on the common minimum score m (max total correlation 0.0885 nats per step over 400 random
  toy states, T2.7);
- per-position value laws given the set kappa_i(v | A) = sum_{y: y_i = v} kappa(y | A) are sharpened
  relative to P_i (Prop. 5 majorisation at k = 1; the same direction is expected for k >= 2 [H]);
- at k = 1 the set has one element and kappa_SF equals rho(i) kappa_i(v), a position-dependent state-only
  tilt (red-team F1, block C).

Arms (all use the same marginals, the same tie rule, one forward pass per step, k committed tokens per step):

| Arm | Positions | Values |
|---|---|---|
| A1 SF | top-k of SF's own draw by score | SF's own draw at those positions |
| A2 resampled twin | as A1 (same draw, same tie priorities) | fresh independent draws from P_i at the selected positions |
| A3 tilted twin | as A1 | independent draws from kappa_i(. given A), the per-position marginal of SF's value law given the set |
| A4 confidence rank-then-sample | top-k by max_v P_j(v) | independent draws from P_i |
| A5 (LLaDA only) | as A4 | argmax (the practitioner default, tau -> 0) |

Because A3 is the product of the per-position marginals of kappa(. | A) with SF's own position law, it is
the KL projection of SF's commit kernel onto kernels with the same position law and a product value law
given the set [I: argmin over products nu of KL(kappa(. | A) || nu) is the product of marginals]. Hence
(sign convention: Y = log GenPPL, lower is better; every G is "A-side quality gain", positive = better):

    G_tot(k) = Y(A2) - Y(A1)          total value-rule effect of SF over plain sampling
    G_sh(k)  = Y(A2) - Y(A3)          per-position sharpening given the set
    G_cp(k)  = Y(A3) - Y(A1)          joint coupling (the new quantity)
    G_tot = G_sh + G_cp               (identity of the estimands; the split is defined relative to A3, see 1.5)

All Y are read at the same output entropy h* (section 7). At k = 1, G_cp = 0 in law (A1 and A3 have the same
law), so G_tot = G_sh there.

### 1.3 Closest methods and the exact distinction

- arXiv 2605.12522 (Zhang et al.) [E3 via dossier]: SF versus its resampled twin ("bias elimination") at
  k = 1 only, N = block length 2, 8, 32, one 120M LLaMA-architecture model trained from scratch on a
  5000-type vocabulary, temperature fixed at 1.0 by code default, no intervals, metrics are n-gram entropy,
  embedding-based coherence and diversity, and a self cross-entropy. Distinction: k >= 2 at matched passes,
  a temperature sweep with an entropy-matched read, the tilted twin (absent from their paper and code), a
  pretrained 130M model with a 50k vocabulary and an external evaluator, paired intervals.
- arXiv 2609.34509 (Jeon et al.) [E2 via dossier]: SF (LCR) versus max-probability ranker (TPP), one token per
  step, LLaDA-8B-Instruct, T in {0.6, 0.8, 1.0, 1.2}, GSM8K and HumanEval. Distinction: same as above; the
  position-rule contrast A2 versus A4 here is a secondary replication at k >= 2 with a matched-entropy read.
- Hayakawa et al. 2510.04525 [E2 via dossier]: noised SF approaches a tilted sampler when N >> k^2 |S|^(1/tau).
  Used for the secondary noise condition S-N (6.4), not claimed.
- Beirami et al. 2401.01879 and the iid k = 1 best-of-N law: the k = 1 analogue; not claimed.
- Zheng et al. (float32 Gumbel truncation sharpens) [S via primer]: the reason for float64 draws (6.1).
- Our own Prop. 4 (k >= 2 SF law) is a derived formula, not an experimental result; the experiment tests
  what its coupling does to quality on a real network, which the toy cannot say.

Novelty on the evidence read: the four-arm comparison at k >= 2 with a tilted twin and an entropy-matched read
is not run in 2605.12522 or 2609.34509 (E3 and E2). A concurrent paper could exist; the novelty-auditor should
re-check before the card is frozen [A].

### 1.4 Competing explanations and their controls

| # | Explanation for a non-zero G_cp or G_sh | Control or analysis |
|---|---|---|
| C1 | A3 estimator error (binning, truncation) manufactures coupling | T-A3-1 to T-A3-4, N1, N2, convergence ladder (5.3, 10) |
| C2 | SF's sharpening is a state-dependent temperature | entropy matching removes the global part; G_sh at h* tests what is left |
| C3 | Metric artifact: equal unigram entropy, different longer-range repetition | distinct-n and 4-gram repetition guard (8.2, 11.3); second evaluator on bracketing cells |
| C4 | Interpolation artifact | two cells straddling h* (7.3); sensitivity IR8; placebo split-half N4 |
| C5 | Visited states differ across arms | stated, not removed: contrasts are kernel effects on the output, not one-step effects (1.5) |
| C6 | Precision artifact | float64 draws and tables in every arm (6.1); TF32 off |
| C7 | Tie-rule artifact at saturated rows | random priorities in every arm (6.2); toy N3 |
| C8 | Quantisation (LLaDA only) | stated threat (13.5); MDLM is fp32 and primary |
| C9 | Evaluator domain bias (GPT-2 Large was trained on WebText, close to OWT) | second evaluator on bracketing cells (8.3) |

### 1.5 What is NOT claimed

No size of V, E_fact, E_learn, G, E_sel or E_tilt on any model (D0011 withdrew E_sel and E_tilt as new terms
and the red-team showed the SF-versus-tilt split is not canonical, M1). The coupling/sharpening split is defined
relative to the intermediate twin A3; another twin (for instance one fitted to SF's inclusion-conditional
value law, or a global-temperature twin) would give another split. The experiment measures output-quality
contrasts of samplers on two checkpoints, not KL. No claim about the data law q, other checkpoints, other
vocabularies, guided sampling, top-p, or revision samplers. The U-shape in the number of steps is not claimed
(M5). The step sweep is not read as identifying E_learn or E_fact (P1, M6); k is a design factor here.

## 2. Hypotheses (falsifiable; direction and minimum effect of interest)

Notation: Y = log GenPPL at h*; k in K = {2, 4, 8, 16} for the confirmatory family (K may be reduced by the
ladder of 9.6); delta_cp = 0.03, delta_sh = 0.05, delta_tot = 0.05 (log-GenPPL units, about 3 and 5 percent
relative perplexity; design choices [A], not derived from literature; reasons in 9.6).

**H1 (primary; coupling).** On MDLM-OWT, G_cp(k) is non-zero. Directional prediction (registered, tested
two-sided): G_cp(k) > 0, i.e. SF's joint value coupling lowers log GenPPL at matched entropy relative to its
independent-values twin, as the toy suggests (coupling lowers KL by 0.016 against sharpening raising it by
0.497 at k = 2, [V] toy, L = 4, V = 3). Minimum effect of interest |G_cp| >= 0.03 at some k in K.
- **H1b (growth).** The slope beta of G_cp(k) on log2 k over the estimable k has the same sign as G_cp(16) and
  its interval excludes 0. Tested only if H1 is supported at some k (gatekeeping).

**H2 (decomposition; which part carries the matched-entropy gain).** Let Delta2(k) = G_cp(k) - G_sh(k)
= 2 Y(A3) - Y(A1) - Y(A2). Two-sided test at each k in K. Interpretation table (a = G_sh, b = G_cp, signs
classed in 11.1 as + (clearly positive), 0 (practically zero), - (clearly negative), ? (undecided)):

| a = G_sh | b = G_cp | Meaning for SF at matched entropy |
|---|---|---|
| 0 | + | The gain is joint coupling; the per-position effect is a temperature (removed by matching) |
| + | 0 | The gain is state-dependent per-position sharpening beyond a global temperature; coupling negligible |
| + | + | Both; Delta2 says which is larger |
| 0 | 0 | SF at matched entropy equals plain sampling at another temperature: the fixed-tau gain is the entropy loss |
| any | - or a - | A component harms quality at matched entropy |
| + and - (or - and +) with G_tot = 0 | | Cancellation: total null hides two non-zero parts |

The a-priori expectation (not a test condition): at fixed tau (secondary S5) sharpening dominates mechanically
because it lowers entropy; at matched entropy the toy gives no prediction for log GenPPL (its metric is KL).
H2 is therefore registered two-sided with no predicted winner.

**H3 (position rule, secondary).** G_pos(k) = Y(A4) - Y(A2): at matched entropy SF's position law ranks no
better or worse than max-probability ranking (two-sided; k in {4, 16}). Replicates the 2609.34509 contrast
at k >= 2.

**H4 (twin validity, secondary).** |H(A1) - H(A3)| <= 0.05 nats (mean per-sequence unigram entropy) at
tau = 1, k >= 2: the tilted twin reproduces SF's entropy deficit, as in the toy (-0.007 on 3.4). Also
H(A1) < H(A2) at tau = 1 for every k (SF sharpens; positive control P1). If H4 fails with T-A3 passed, coupling
changes diversity, which is itself a result.

**H5 (LLaDA direction, secondary, exploratory).** On LLaDA-8B-Instruct (4-bit), GSM8K accuracy contrasts have
the same sign pattern as H1/H2 at k in {4, 16}; the design can only detect effects of about 10 points
(13.4), so H5 is an estimation target with intervals, not a test with a power claim.

**Kernel-level mechanism readout (no decision rule).** The per-step coupling content
TC_A = sum_i H(kappa_i(. | A)) - H(kappa(. | A)) of the committed set, estimated on real states (S1) and logged
in A3 runs, is predicted to be positive, below 0.1 nats per step, and increasing in k. It is a mediator
readout; its relation to G_cp is descriptive.

Directions are stated; each test is two-sided so that a reversed result is detected.

## 3. To be filled from runs/env-2026-10-14/setup.md

The card does not depend on these values, but freezing requires each one filled (as a pre-freeze amendment, 19).

| # | Needed | Why it matters | Default used for the numbers in this card |
|---|---|---|---|
| 1 | MDLM-OWT: Hugging Face id and revision, weight hash, licence, parameter count, tokenizer, L, vocabulary size and [MASK] id, whether the net takes a time/noise input and what the official sampler feeds, SUBS (carry-over, mask-logit removal) handling | arms, time input rule | [A] about 130M parameters, GPT-2 tokenizer, L = 1024; time input if present: t_n = N_n / L in every arm |
| 2 | MDLM official sampler code path and SHA (random positions? caching? float64 sampling? top-p default) | confound with arms; precision | [A] ancestral random-order sampler; our arms replace its position and value rules |
| 3 | Forward seconds per sequence at batch B in fp32 (TF32 off) and bf16; peak memory; largest B for the float64 tables | t_f, B, precision | t_f = 7 ms per sequence-pass [A] (4.7 to 9.4 ms from selection-term.md T9's assumed 0.15 to 0.3 s per batch of 32) |
| 4 | LLaDA-8B-Instruct: revision, weights hash, quantisation backend and bits that run on this GPU and OS, weight size, forward seconds per sequence at batch B, released generate code SHA (block length, steps, remasking, scoring, Gumbel/float64, mask id, EOS handling, chat template) | section 13, validity of A1 as "the released sampler" | [A] 4-bit NF4, block length 32, gen length 256, confidence scored with the untempered softmax of the drawn token |
| 5 | GPT-2 Large package and weight hash, fp32 forward seconds per 1024-token sequence, a second evaluator (a different family, fits 12 GB) with hash | endpoint, C9 | t_G = 30 ms [A] |
| 6 | mauve-text version, featurizer id, all non-default arguments | secondary endpoint | pin by hash; record every argument |
| 7 | OWT held-out split: how MDLM's pipeline builds it, chunking/wrapping rule, three disjoint slices of 2048+ chunks (pilot, h* and anchors, MAUVE reference) | h*, MAUVE | draw by seed 20261014, sorted by chunk id |
| 8 | GSM8K train and test files and hashes; extraction script | section 13 | train for pilot, test for main |
| 9 | torch version; float64 CUDA uniform generation; counter-based (Philox) generator keyed by (seed, sample, tag, step); determinism of float64 cumsum/searchsorted across batch sizes | CRN, reproducibility | assumed available |
| 10 | The MaskGIT noise schedule actually used by google-research/maskgit @1db2359 | condition S-N | eta_n = 4.5 (1 - (n+1)/T), zero at the last step (framework-v2 B); verify |

## 4. Models, data, seeds

- **Primary: MDLM-OWT**, L = 1024, unconditional, all positions masked at the start, T = L/k steps, exactly k
  positions committed per step (N_n = L - n k). EOS tokens are ordinary tokens. Forward in fp32 with TF32 off.
- **Secondary: LLaDA-8B-Instruct**, 4-bit (section 13).
- **Reference text.** Three disjoint slices of the held-out OWT chunks: V0 (pilot), V1 (h* and the GenPPL data
  anchor, 2048 chunks), V2 (MAUVE reference, size max(n_B, 2048)). Data-defined constants (h*, anchors) are
  computed from V1 once, before any model output exists, and written to `runs/EXP-002/constants.json` with a hash.
- **Seeds.** Sample index s selects a counter-based key. Pilot s in [2,000,000, ...), stage A s in
  [1,000,000, ...), stage B and the k = 1 block s in [0, n). Streams per (s, step): `draw`, `prio`, `res`,
  `tilt` (section 5.5). No seed is chosen after seeing outputs.
- **No test-set tuning.** tau grid, k set, h*, margins, tolerances and the ladder are fixed by this card, the
  pilot (variance and cost only, firewall in 9.7) and data-defined constants. GSM8K pilot problems come from
  the train split; main problems from the test split.

## 5. Arms and the step procedure

### 5.1 Common step (all arms; per sample; step n; N masked; k_eff = min(k, N))

```
l      <- logits at masked rows, float64, [MASK] column removed       # N x V
P      <- softmax(l / tau)                                              # tempered marginals, float64
Q      <- P  (primary)  |  softmax(l) (condition S-U, untempered score)
cdf    <- cumsum(P, dim=1); cdf[:, -1] <- 1.0
u      <- U_draw[n]  (N uniforms, float64, open interval (0,1))
y_j    <- searchsorted(cdf_j, u_j)           # inverse-CDF draw for every masked j
g_j    <- Q_j[y_j]                           # score of the drawn token
pi     <- U_prio[n]  (N uniforms)            # tie priorities, fresh each step, shared by all arms
rank   <- stable sort by (g desc, pi asc)    # total order, no ties
A      <- first k_eff of rank
```
Last step (N = k_eff): every arm commits all remaining positions; A1, A2, A3 coincide in law there
(Prop. 4 equality case N = k), so the code may shortcut.

### 5.2 Arms

- **A1 SF.** commit y[A].
- **A2 resampled twin.** commit searchsorted(cdf_i, U_res[n][i]) for i in A (fresh uniforms, same P).
- **A3 tilted twin.** for i in A commit a draw from kappa_i(. | A) (5.3), using U_tilt[n][i]. Positions A are
  exactly A1's.
- **A4 confidence rank-then-sample.** A4 positions = first k_eff of the order by (max_v P_j(v) desc, pi asc);
  commit y[A4] (the same `draw` uniforms, so identical to an independent sample from P at those positions).
- **A5 (LLaDA only).** positions as A4 with max_v of the untempered softmax; commit argmax_v.

### 5.3 A3: target law, numerical specification, acceptance tests

**Target.** kappa_i(v | A, s, pi) = sum over y with y_i = v of kappa(y | A), where kappa(y | A) is the
Prop. 4 law of 1.2 normalised over y, evaluated with the tempered marginals and the active score. Everything
needed (the marginals of all N masked rows, the score laws, the priorities, the set A) is known without
another forward pass. The committed values of A3 are independent across members given A by construction.

**Why this is computed, not sampled by Monte Carlo.** [I] The event "the selected set equals A" has
probability rho(A), of order 1/C(N, k) or smaller (about 2e-6 on average for N = 1024, k = 2); replicate or
rejection Monte Carlo cannot condition on it. The per-position conditional marginal has to come from the
closed form, with randomness only in the final categorical draw, which is exact for the computed law.
[This replaces the Monte Carlo estimator suggested in the brief; see 17.]

**Recommended recipe (engineering latitude; the law and tests below are frozen, the recipe is not).**
1. Score axis: 2048 log-spaced bins on [1e-12, 1], plus one top bin for scores within 1e-12 of 1 treated as a
   tie class resolved by priority.
2. For each masked row j, a score histogram of tempered mass h_j[b] = sum_v P_j(v) 1[g_j(v) in bin b]
   (scatter-add, O(N V)); F_j^<(bin b) = prefix sum of h_j below b.
3. W_A as a function of the bin of the minimum member score, as a product over rows not in A of
   [F_j^< + tie term], computed in the log domain.
4. For each member i, the law of the minimum score of the other k - 1 members from their survival functions
   S_l(c) = P(g_l >= c); kappa_i(v | A) is proportional to P_i(v) * E[W_A(min(g_i(v), m_{-i}))], a one-dimensional
   cumulative integral on the grid.
5. Draw v by inverse CDF in the token order of row i with the `tilt` uniform.
6. If a state-wise exact reference is needed, the same computation with the sorted exact token scores
   (selection-term.md T9 Algorithm 1, O(N V log V)) replaces the bins.
An importance-sampling implementation (candidate k-tuples from truncated product proposals, exact weights W_A,
independent resampling of candidate rows per position) is allowed if it passes the same tests and reports
its effective sample size (at least 200 at the S1 states).

**Error specification.** Define eps_3 = mean over selected positions of TV(kappa_hat_i, kappa_i), where
kappa_i is the exact-token-score reference. Requirements at the S1 states: mean eps_3 <= 0.005 and 95th
percentile <= 0.02. Doubling the number of score bins must change the pilot G_cp point estimates by less than
0.01. [I] No worst-case bound on the path law is available: the per-step TV compounds over L = 1024 committed
tokens, so the per-step bound is vacuous at sequence level. The safeguards are the tests below, the entropy
equivalence H4, and the convergence ladder in 10 (N5).

**Acceptance tests (all before any main data; failure stops the run).**
- T-A3-1 (exact, toy). On 200 random states with N <= 6, V <= 6, k in {1, 2, 3}, tie-free marginals, the
  production A3 per-position conditional laws equal the enumeration oracle `kernel("A3")` of
  `analysis/framework/check_coupling_k2.py` to 1e-9 (exact token-score grid), and A1-conditional marginals
  equal A3's to 1e-9. Production code uses random priorities; compare tie-free states only, and test the
  tie case separately against an oracle that averages over priorities.
- T-A3-2 (binned, real vocabulary). On 64 real MDLM states (N in {1024, 512, 128, 32}, k in {2, 16}), the
  recipe's kappa_hat_i against the exact-score reference meets the error specification.
- T-A3-3 (sampling). On the toy, 2e6 draws of the production A3 sampler: per-position marginals pass a
  chi-square test against the oracle (Bonferroni over positions, alpha 0.05); the within-set Pearson
  correlation of committed scores is 0 within Monte Carlo error for A3 and clearly non-zero for A1 on a
  state where the oracle total correlation is above 0.02 nats.
- T-A3-4 (reproduce the prior). The production arms, driven through the exact enumeration harness at
  L = 4, V = 3 with the 12 q of `check_coupling_k2.py`, reproduce its summary: k = 1 max |p_A1 - p_A3| <= 1e-12;
  k = 2 sharpening KL(A3) - KL(A2) positive in 12 of 12; coupling mean within 0.002 of -0.0164.

### 5.4 What is matched across arms

| Item | Value |
|---|---|
| forward passes per sequence | T = L/k, identical for A1 to A4 |
| tokens committed per step | exactly k (min with N) |
| marginals | the same tempered P at the arm's own state |
| tau | identical function applied to every arm (a cell is an (arm, tau) pair; entropy matching moves tau per arm, 7) |
| score | tempered probability of the drawn token (primary); untempered in S-U |
| tie rule | fresh iid priorities per step, same stream in every arm |
| precision | float64 softmax, cdf, tables and draws; fp32 network |
| noise on the ranking | none (primary) |
| time input to the network | same function of N_n in every arm |
| per-sample random numbers | common random numbers (5.5) |

### 5.5 Common random numbers

Counter-based generator (Philox or equivalent) keyed by (master seed, sample index s, tag, step n), float64
uniforms with 53 bits. Tags: `draw` (N uniforms), `prio` (N uniforms), `res` (k uniforms), `tilt` (k uniforms).
Every arm consumes `draw` and `prio` identically in shape, so at step 0 (the all-masked state) A1, A2, A3 select
the same set and A1, A4 draw the same values; A2 and A3 differ from A1 only through `res` and `tilt`. Arms
diverge afterwards because they visit different states, so the coupling decays along the trajectory. The
benefit is partial and unquantified; the design does not rely on it for validity (the paired bootstrap is valid
with any positive or zero correlation). The pilot measures the realised correlation (9.6).

## 6. Value rule fixed across arms

6.1 **Float64.** The softmax at temperature tau, the cumulative sums, all tables and all uniforms are float64.
A float32 control is not run (it would reintroduce the known truncation artefact); a 32-bit unit test in S0
confirms that float32 Gumbel draws sharpen on a toy, as a check that the float64 path matters [H].
6.2 **Tie rule.** Fresh iid U(0,1) priority per masked position per step; the lower priority value wins ties
in every arm (SF, A4, A3's W_A). Saturated rows (probability 1.0 in float64) tie exactly, so the rule is
exercised; a left-to-right tie rule is not used because it would add a position bias that differs between
SF and A4.
6.3 **No top-p, no top-k, no guidance, no Gumbel noise on the ranking.** Temperature is the only value-rule
parameter and is applied to the marginals before any arm acts.
6.4 **Secondary conditions (run only after the main stages, section 12).**
- **S-N (MaskGIT-style noise).** Ranking key log g_j + eta_n G_j with G_j iid standard Gumbel (float64) and
  eta_n = 4.5 (1 - (n+1)/T), zero at the last step [A, item 10 of section 3]. Arms A1, A2, A4 only, k in
  {4, 16}; A3 under noise needs the noise inside kappa and is not specified here. Purpose: does noise close
  the A1 versus A2 gap (Hayakawa et al.)? Descriptive.
- **S-U (untempered score).** Score Q = softmax(l) while draws use tau. This is the released LLaDA and
  2605.12522 code path (untempered score of a tempered draw) [S, dossier]. Arms A1, A2, A3, A4, k in {4, 16}.
  Purpose: robustness of the decomposition to the scoring convention. Descriptive.

## 7. Sweeps and entropy matching (primary analysis)

### 7.1 Definitions

Entropy of a sequence: H_s = - sum_v (c_v / L) ln (c_v / L), c_v the count of GPT-2 token v among the L = 1024
generated tokens (natural log); cell entropy E = mean over samples. Reference entropy h* = mean H over the
2048 held-out chunks of V1 (data-defined; frozen before any model sample exists). Quality Y_s = mean negative
log-likelihood per predicted token of the sequence under GPT-2 Large (8.1); cell Y = mean over samples.

### 7.2 Stage A, calibration (entropy only)

For arms A1, A2, A3 (and A4 at k in {4, 16}), each k in K, tau in Gamma_A = {0.6, 0.7, 0.8, 0.9, 1.0, 1.1,
1.2, 1.35, 1.5}, n_A = 64 samples per cell (independent seeds). Only token files and entropies are produced;
the evaluator is not invoked (firewall, 9.7). Isotonic regression of E on tau per (arm, k); tau_lo and tau_hi are
the values at which the fitted curve equals h* - 0.05 and h* + 0.05 (linear interpolation of the fitted curve
in tau). If the target is outside the fitted range the (arm, k) is "unreachable" (NE) and is reported as a
result. The k = 1 block uses Gamma = {0.8, 0.9, 1.0, 1.1, 1.2}, n_A1 = 32.

### 7.3 Stage B, confirmatory cells

For every (arm, k): two cells at tau_lo and tau_hi from stage A, n_B samples each, independent seeds from
stage A, common sample index across all cells (section 5.5). The calibration constants (tau_lo, tau_hi) are
design constants in the inference; calibration uncertainty is not propagated because the realised entropies
of stage B enter the interpolation.

### 7.4 Interpolation rule (fixed now)

For one (arm, k), with stage-B cell means (E_lo, Y_lo) at tau_lo and (E_hi, Y_hi) at tau_hi:
- IR1 If E_lo <= h* <= E_hi: Y(h*) = Y_lo + (h* - E_lo)/(E_hi - E_lo) * (Y_hi - Y_lo).
- IR2 If E_lo > E_hi (inversion from noise): pool the two cells into one cell (mean of E, mean of Y) and use IR4.
- IR3 If h* lies outside [E_lo, E_hi] by at most 0.05 nats: linear extrapolation with the same line, flagged X.
- IR4 If |E_hi - E_lo| < 0.02 nats or after IR2: Y(h*) = Y_cell + beta_A (h* - E_cell), beta_A the local slope
  dY/dE from the stage-A cells with GenPPL computed after stage B (fixed constant), flagged S.
- IR5 If h* lies outside by more than 0.05 nats: not estimable (NE).
- IR6 The bootstrap (9.3) recomputes IR1 to IR5 in every replicate; a contrast is flagged if more than 5 percent
  of replicates are X or S, and not estimable if more than 5 percent are NE.
- IR7 No monotone smoothing of Y; no use of stage-A quality in the primary estimate.
- IR8 Sensitivity (reported, not decision rules): (i) h* moved to h* - 0.10 and h* + 0.10 (needs the extra
  extrapolation allowance, so flagged); (ii) interpolation linear in tau instead of E; (iii) the fixed-tau
  contrasts of 7.5.

### 7.5 Fixed-tau comparison (secondary S5)

At tau = 1.0 and k in {2, 4, 8, 16}: contrasts G_tot, G_sh, G_cp of Y and of E on the stage-B-sized samples
of the cell (arm, tau = 1.0), run as additional cells in stage A with n_A (descriptive) and with n_B if the
budget allows (12.5). It shows where each arm sits on its frontier at the usual temperature and gives the
sharpening-by-entropy read (H4, P1). Not corrected for multiplicity; reported as descriptive.

### 7.6 Frontiers (descriptive)

Stage-A entropy against tau per arm and k, and (after stage B) the quality-against-entropy points of all cells,
plotted per k. No test.

## 8. Endpoints

### 8.1 Primary (one): log GenPPL at the reference entropy

Y(arm, k) of 7.1 and 7.4. GenPPL protocol (own implementation, pinned; absolute values are not comparable with
published MDLM numbers, which retokenise): the 1024 generated token ids are fed directly to GPT-2 Large
(`gpt2-large`, fp32, context 1024, no BOS prepended, no stride); the negative log-likelihood is averaged over
predictions of positions 2 to 1024 (1023 predictions), giving Y_s in nats per token; GenPPL = exp(Y). Code in
`analysis/EXP-002/genppl.py`, git SHA recorded; package versions and weight hash from setup.md item 5.
The primary estimands are G_cp(k) for k in K (H1) and Delta2(k) (H2).

### 8.2 Secondary

- S1 distinct-n (n = 2, 3, 4): unique n-grams over total n-grams per sequence, mean over samples;
  expected regression for A1 and A4 at fixed tau.
- S2 4-gram repetition rate: fraction of 4-gram positions whose 4-gram occurs at least twice in the sequence.
- S3 unigram entropy E itself at fixed tau (sharpening readout; expected regression A1 < A2, A4 < A2).
- S4 MAUVE against V2 at the stage-B cells (mauve-text pinned, GPT-2 Large features, equal n per cell, all
  arguments recorded), interpolated at h* by IR1 to IR5. A population metric with a noisy estimate at
  n_B near 1000; bootstrap by sequences with 200 replicates; exploratory.
- S5 fixed-tau contrasts (7.5).
- S6 kernel-level coupling content TC_A per step, entropy deficit of committed values, and committed-score
  summaries (S1 stage and A3 runs).
- S7 wall-clock and overhead factors omega of each arm.
- S8 position-rule contrast G_pos(k) (H3).
- S9 the S-N and S-U conditions (6.4).

### 8.3 Metric guards and the second evaluator

If a primary contrast favours an arm while that arm's 4-gram repetition rate at h* exceeds its comparator's by
more than 0.02 (absolute), the result is reported as "quality gain with longer-range repetition" and is not
counted as unambiguous support (11.2). The second evaluator (setup.md item 5, a different model family) is
run on the stage-B cells for k in {4, 16}; if its sign for G_cp(k) disagrees with GPT-2 Large's, the
corresponding finding is downgraded to "evaluator dependent".

## 9. Statistics

### 9.1 Unit and design

Unit: a generated sequence, indexed by sample index s (MDLM); problem (LLaDA, 13). Paired design: all cells of
all arms share sample indices and the common random numbers of 5.5; the n_B indices are the resampling unit.
Within an (arm, k, tau) cell the n_B sequences are independent given the model.

### 9.2 Estimands

Per (arm, k): Y(arm, k) from IR1 to IR5. Contrasts: G_tot, G_sh, G_cp, Delta2 as in 1.2 and 2, G_pos for H3.
At k = 1 only G_tot (= G_sh) and the controls are computed; G_cp(1) is a control, not a test.

### 9.3 Interval and p-value

Paired bootstrap over sample indices, B = 10,000 replicates, the same resampled index set applied to every cell,
the full estimator (cell means, IR1 to IR5, contrasts) recomputed per replicate. Intervals: percentile.
Two-sided p-value: p = 2 min{ (1 + #{theta* <= 0}) / (B + 1), (1 + #{theta* >= 0}) / (B + 1) }, capped at 1.
Replicates in which a needed Y(arm, k) is NE count as missing and trigger IR6. MAUVE uses 200 replicates with
bootstrap over sequences within each generated set.

### 9.4 Multiplicity

Two confirmatory families, each with family-wise error 0.025 (Bonferroni across the two, total 0.05):
- F1: H1, the four tests G_cp(k) = 0, k in K, Holm within the family. H1b is tested at level 0.025 only if F1
  rejects at least one hypothesis (serial gatekeeping).
- F2: H2, the four tests Delta2(k) = 0, Holm within the family.
G_sh(k), G_tot(k), G_pos(k), fixed-tau contrasts and secondary metrics are descriptive: unadjusted 95%
intervals plus Holm-adjusted p within each four-test group, labelled exploratory. LLaDA (13) and the secondary
conditions are not part of the confirmatory budget.

### 9.5 Outcome classes per hypothesis test (used in 11)

For a contrast with estimate G, margin delta (delta_cp = 0.03, delta_sh = delta_tot = delta_Delta2 = 0.05):
- clearly + / clearly - : Holm-adjusted p below the family level and |G| >= delta (sign by G);
- practically 0 : the 97.5 percent bootstrap interval lies inside (-delta, delta) (two one-sided tests at
  0.0125 each, covering the Bonferroni over the four k);
- undecided (?) : anything else.

### 9.6 Sample size and the pilot [A until the pilot]

Pilot (variance and cost only): n_p = 32 samples per cell, arms A1, A2, A3, k in {4, 16}, tau in {0.9, 1.0,
1.1}, indices disjoint from main. The pilot outputs only: seconds per pass and per step for each arm (omega),
memory, per-cell SD of Y_s and of H_s, their within-cell correlation, cross-arm correlations of Y_s and H_s
under common random numbers, local slopes dY/dE, and sigma_c, the leave-one-out jackknife standard deviation
of the per-sample influence values of G_cp(k) under the full estimator (IR1 to IR5) applied to the pilot
cells nearest in entropy to h* (IR4 allowed). It prints no cell mean of Y and no contrast mean (9.7).

    sigma_up = sigma_c * sqrt( (n_p - 1) / chi2_{0.20, n_p - 1} )                (one-sided 80 percent upper bound)
    n_B(R)   = ceil( (z_{1 - 0.025/(2 m_R)} + z_{0.80})^2 * sigma_up^2 / delta_cp^2 )

with m_R the number of k in the reduction R of the ladder below (z_{1 - 0.025/(2*4)} = 2.73 for m = 4,
z_{0.80} = 0.8416, so the squared sum is 12.75 for m = 4 and 12.1 for m = 3, whose z is 2.64). Illustration only [A]:
sigma_up = 0.25, 0.40, 0.60 gives n_B = 885, 2267, 5100 for m = 4. The minimum detectable effect at a cap
n_cap is MDE = (z + z_{0.80}) sigma_up / sqrt(n_cap).

**Ladder (decided from the pilot, before stage A, logged).** Let H_cap be the approved stage-B budget
(proposal 60 GPU-hours for the whole MDLM programme, to be approved by the orchestrator [A]).
- R0: K = {2, 4, 8, 16}, m = 4, cost proportional to 960.
- R1: K = {4, 8, 16}, m = 3, cost proportional to 448.
- R2: K = {8, 16}, m = 2, cost proportional to 192.
- R3: K = {16}, m = 1, cost proportional to 64 (H1b untestable).
Choose the first R with H_B(n_B(R), R) <= H_cap (12.2). If even R3 exceeds H_cap, run R3 at the n that the cap
allows and state the MDE; the outcome is then "underpowered for delta_cp unless MDE <= delta_cp". The
choice of R cannot depend on any quality contrast (9.7).

delta_cp = 0.03 is the smallest effect a reader can interpret (3 percent perplexity) and that the ladder can
plausibly resolve; it is a design choice [A], not a literature value. delta_sh = delta_tot = 0.05 reflect
that sharpening effects are expected to be larger. The toy ratio of coupling to sharpening (0.016 to 0.497, KL
at fixed entropy loss) motivates sizing for the small effect; it does not predict the real ratio.

### 9.7 Firewall and no peeking

The pilot analysis script and the stage-A script are written so that they do not compute or print Y or any
contrast of Y. The evaluator is invoked on stage-B (and k = 1 block) token files only after all of them are
generated, hashed and listed in `runs/EXP-002/manifest.json`. No interim test, no sequential stopping, no
extension of n after seeing quality. Evaluation runs once. Stage-A token files are evaluated only in the final analysis (for beta_A and the frontier plots), never before the stage-B and k = 1 evaluations are complete.

### 9.8 Placebo (N4)

Within each (arm, k) stage-B cell pair, randomly split the n_B indices into two halves, treat the halves as
two "arms" (same arm label), and run the full estimator and bootstrap for 200 random splits. The rejection
rate at 0.05 two-sided must be in [0.02, 0.09]; the interval coverage of 0 is reported. Costs no GPU.

## 10. Controls

Negative controls (the effect must vanish) and positive controls (a known effect must be recovered). All are
gates in 11.

| ID | Type | Setup | Pass criterion | Protects |
|---|---|---|---|---|
| N1 | negative | k = 1: A1 versus A3 commit law. Exact on the toy (max difference); on real MDLM states with N in {8, 16, 32} from k = 1 trajectories, 2e5 rounds each, 32 states, chi-square on pooled joint (position, value) cells | toy <= 1e-12; real: no rejection at Bonferroni alpha 0.05/32 | A3 machinery at k = 1 |
| N2 | negative | generation level: A1, A3, A2 at k = 1, tau = 1.0, n_1 = 256, paired | TOST 90% interval of Y(A1) - Y(A3) inside +-0.05 and of H(A1) - H(A3) inside +-0.03 | A3 at sequence scale |
| N3 | negative | state-independent toy models (L = 64, V = 32): flat marginals; one-hot marginals. Prop. 4 equality cases: A1, A2, A3 are equal in law for any k | all pairwise two-sample tests on token histograms and on pair statistics, 20,000 sequences per arm, alpha 0.01 with Bonferroni, no rejection; the one-hot case exact | tie rule, pipeline, no spurious G |
| N4 | negative | placebo split-half (9.8) | rejection rate in [0.02, 0.09] | bootstrap and interpolation false positives |
| N5 | negative/diagnostic | convergence ladder: A3 recomputed with half and with double the score bins on the pilot cells (k in {4, 16}) | G_cp point estimates change by < 0.01 each | A3 numerical error |
| P1 | positive | MDLM-OWT, k = 1, tau = 1.0: SF sharpens, so H(A1) < H(A2) (the 2605.12522 direction at k = 1), n_1 = 256 | difference negative with 95% interval excluding 0 | float64 draws, score definition, arm wiring |
| P2 | positive | toy with peaked heterogeneous independent state-independent marginals (Dirichlet 0.3, L = 64, k in {4, 16}), exact within-set total correlation from Prop. 4 | A1 minus A3 pair statistic matches the exact value within Monte Carlo error; A3 is 0 | coupling is detectable by the statistic when present |
| P3 | positive | evaluator: GenPPL of held-out chunks (V1) versus the same chunks with tokens shuffled within sequence; MAUVE of V1 against V2 versus shuffled | GenPPL(shuffled) / GenPPL(data) >= 3; MAUVE data vs data above 0.9 at n = 2048 vs 2048; shuffled below 0.1 | evaluator wiring |
| P4 | positive | stage A: E is increasing in tau for each (arm, k) up to noise; GenPPL rises with E in stage B | pooled-adjacent-violators mass < 0.05 nats; slope dY/dE > 0 | interpolation is meaningful |
| P5 | positive | T-A3-4 reproduction of the toy prior | as in 5.3 | arms implemented as in the prior |

Note on the brief's wording: the coupling contrast vanishes for "exact independent toy marginals" only in the
Prop. 4 equality cases (flat on the support, one-hot, N = k, or no competitor score between a position's
extreme scores). With peaked heterogeneous independent marginals SF still couples committed values (and
sharpens), which is what P2 uses as a positive control; N3 uses the cases where the equality holds.

## 11. Stop rules, outcome classes and falsifiers

Staging is by information per GPU-hour (12). Each stage ends in a written verdict file; the next stage runs only
if its precondition holds.

### 11.1 Stop rules

1. **S0/S1 gate.** If any of T-A3-1 to T-A3-4, N1, N3, P2, P5 fails, stop; no stage after S1 runs; the failure
   is logged and the orchestrator is told. P3 failing stops the evaluator-dependent stages only.
2. **Pilot gate and ladder.** 9.6. If sigma_up implies that R3 at the cap has MDE > 0.10, stop before stage A and
   report the design as not decidable at this budget (a result about the budget, not about SF).
3. **Calibration gate (stage A).** If for A1, A2 or A3 at some k in R the target h* is unreachable in Gamma_A,
   or the entropy curve is non-monotone with pooled-adjacent-violator mass above 0.05 nats, stop, issue card
   v0.2 with a changed grid (before any stage-B data), and continue. For A4, unreachable is reported, not a stop.
4. **Control gates at scale.** N2 and P1 failing stops stage B (the k = 1 block precedes it, 12).
5. **Budget.** If cumulative GPU time in a stage exceeds 1.5 times its pre-run estimate, stop and ask the
   orchestrator. An A3 overhead above 6 forward passes per step triggers the reduced-score-bin variant only if
   T-A3-2 and N5 still pass; otherwise R3.
6. **Numerical.** NaN or Inf in logits or tables, or |cdf[:, -1] - 1| above 1e-9 before clamping, stops the run.
7. **No peeking, no extension** (9.7).

### 11.2 Outcome classes for the primary family (MDLM-OWT, k in R, estimable k only)

Let supported_k = "G_cp(k) clearly + or clearly -" (9.5) and not repetition-flagged (8.3).
- **H1 positive (beneficial)**: at least one k with G_cp(k) clearly + (and the second-evaluator sign agrees at
  k in {4, 16} where run). **H1 positive (harmful)**: clearly -. Sign is part of the finding.
- **H1b positive**: the F1 gate opened and the slope interval excludes 0 with the sign of G_cp at the largest k.
- **H1 negative (practical zero)**: G_cp(k) practically 0 at every estimable k in R (at least two k, including
  the largest), then the claim of a practically relevant coupling effect is falsified on this model at
  delta_cp = 0.03. A non-zero effect below 0.03 is not excluded.
- **H1 inconclusive**: otherwise, including the "underpowered" outcomes of 9.6.
- **H2** outcome per k from the table of section 2 using the classes of 9.5; reported with Delta2.

### 11.3 Falsifiers

- F-H1: all estimable G_cp(k) practically 0 (above). 
- F-H1b: G_cp(k) clearly non-zero at k >= 4 but the slope interval includes 0 or has the opposite sign: growth
  with k is falsified, coupling is not monotone.
- F-H2-twin: the decomposition is not interpretable if H4 fails with N5 passing (A3 is not an entropy-equivalent
  twin); then G_sh and G_cp are reported but the split is called twin-dependent in addition to 1.5.
- F-mechanism: the kernel-level TC_A is below 1e-3 nats per step at all k >= 2 on real states while G_cp is
  clearly non-zero. Then the effect is not explained by the mechanism and competing explanation C1 or C5 is
  raised (a check on the estimator and on visited-state shift).
- F-control: any N or P gate failing means no inference about SF from that stage.

### 11.4 What each outcome means for the claim and the review

See 14. In all cases the claim is restricted to MDLM-OWT (and LLaDA-8B 4-bit for H5), GPT-2 Large, plain
sampling, the tau range and the k set that ran.

## 12. Run order and compute budget (12 GB laptop GPU)

Order is by information per GPU-hour: analytic and toy checks, a frozen-checkpoint step-level measurement, a
pilot, controls at k = 1, calibration, the confirmatory cells, secondary conditions, then LLaDA.

| Stage | Content | Precondition | GPU-hours (formula; value at the defaults) |
|---|---|---|---|
| S0 | analytic and toy: T-A3-1, T-A3-3, T-A3-4, N1 (toy), N3, P2, P5, float32 sharpening unit test; evaluator checks P3 (needs GPT-2 only) | none | CPU; 0 to 0.2 for P3 |
| S1 | frozen-checkpoint step-level: 64 sequences generated by A2 at tau = 1.0 for each k in K give states at fractions {0, 0.1, 0.25, 0.5, 0.75, 0.9} of the steps; T-A3-2, N1 (real states), TC_A, committed-score summaries, entropy deficit per step | S0 pass | H_S1 = [64 * Sum_k P(k) * w2 * T_F] + n_states * t_tab / 3600; about 0.3 |
| S2 | pilot (9.6) | S1 pass | H_P = n_p * |Gamma_p| * (w1 + w2 + w3) * Sum_{k in {4,16}} P(k) * T_F + eval; about 0.5 (allow 1.0) |
| S3 | k = 1 controls: A1, A2, A3 at tau = 1.0, n_1 = 256 (N2, P1) | S2 pass | H_3 = n_1 * 1024 * (w1 + w2 + w3) * T_F; about 3.0 |
| S4 | stage A calibration, entropy only | S3 pass | H_A = T_F * [ n_A * (|Gamma_A| * (w1+w2+w3) * Sum_{k in K} P(k) + |Gamma_A| * w4 * Sum_{k in {4,16}} P(k)) + n_A1 * 5 * (w1 + w2) * 1024 ]; about 7.7 |
| S5 | stage B confirmatory cells | S4 pass | H_B = T_F * n_B * [ 2 * (w1+w2+w3) * Sum_{k in R} P(k) + 2 * w4 * Sum_{k in {4,16}} P(k) ] + k = 1 matched cells T_F * n_1 * 2 * (w1+w2) * 1024; about 23.7 + 2.7 at n_B = 1000, n_1 = 256 |
| S6 | evaluation: GenPPL, MAUVE features, second evaluator | S5 generated and hashed | H_E = N_seq * t_G / 3600 (* 2 for the second evaluator on k in {4,16}); about 0.5 |
| S7 | secondary conditions S-U and S-N, plus fixed-tau cells of 7.5 at n_B | S5 analysed | about 8 at n_B/2 per cell |
| S8 | LLaDA (13) | download approved (D0012: no size limit) and S1 pass | H_LL (13.6); about 4 to 16 |

Symbols: P(k) = L/k forward passes per sequence; T_F = t_f / 3600 hours per sequence-pass; w_a the overhead
factor of arm a (1 plus sampler overhead as a fraction of one forward pass), measured in S2. Assumed [A]:
t_f = 7 ms, w1 = 1.3, w2 = 1.32, w3 = 3.3, w4 = 1.3, so w1 + w2 + w3 = 5.92; n_A = 64; |Gamma_A| = 9;
Sum_{k in K} P(k) = 960; Sum_{k in {4,16}} P(k) = 320; t_G = 30 ms. Worked values at t_f = 7 ms, n_B = 1000,
n_1 = 256, R0: S1 0.3 + S2 0.5 to 1.0 + S3 3.0 + S4 7.7 + S5 26.4 + S6 0.5 = 38 to 39 GPU-hours for the main
MDLM programme, 26 to 51 over the assumed range of t_f (4.7 to 9.4 ms); S7 about 8 more; S8 as in 13.6.
Stage B scales as 0.0237 GPU-hours per unit n_B at these defaults (R0); the ladder reduces the factor 960 to
448, 192 or 64 and multiplies the per-n cost accordingly. All of this is unmeasured until S2.

## 13. LLaDA-8B-Instruct secondary (H5; exploratory, direction check)

13.1 **Model and decoding.** LLaDA-8B-Instruct, 4-bit quantised (backend and bits from setup.md item 4; [A]
NF4 with bf16 compute), chat template, no guidance, GSM8K, generation length 256, semi-autoregressive blocks of
the released length (32 [A]); the competitor set of SF is the masked positions of the current block (N <= 32),
k tokens per step, steps per block = 32/k. k in {4, 16} for arms A1 to A4; k = 1 only for N1/N2-type controls
on a few problems. A5 (argmax at A4 positions) at tau -> 0 is the reference practitioners use.
13.2 **Scoring convention.** Primary here follows the released code: the score is the untempered softmax
probability of the drawn token (condition S-U above), draws at tau, because that is what practitioners run.
This differs from the MDLM primary (tempered score); both are stated. The tempered score is a sensitivity run
if budget allows. [A until setup.md item 4 is checked against the released code.]
13.3 **Temperatures and endpoint.** tau in {0.5, 1.0} for A1 to A4 (two points are not enough for
interpolation; the matched-entropy read is exploratory only where the entropy ranges overlap, using the entropy
of the generated answer tokens and h*_LL = entropy of A2 at tau = 0.5, k = 4 on pilot problems). Endpoint: GSM8K
final-answer exact match by a pinned extraction script unit-tested on the gold solutions; unit = problem
(mean over attempts); n_att attempts per problem per cell. pass@k and HumanEval are not in this card (deferred
to a later version; cost and code-execution safety).
13.4 **Power.** For a paired accuracy difference with per-problem SD s_d, MDE = (z + 0.8416) s_d / sqrt(n_prob).
With n_att = 1, s_d near 0.46 [A], n_prob = 200 gives MDE about 0.11 (11 points); with n_att = 4 and
E[p_i(1 - p_i)] near 0.1 [A], s_d near 0.22 and n_prob = 300 gives about 0.04. The full test set (1319
problems, n_att = 4) would give about 0.02 but costs 70 to 280 GPU-hours and is not planned. Consequence: the
design cannot test H1 at 2 points and can detect only large effects (the total effect A1 versus A2, or A5
versus A1). The result is reported as intervals; if all intervals contain 0 and exceed the stated MDE, H5 is
"undecided at this n", not "no effect".
13.5 **Threats.** Quantisation noise perturbs the marginals and may change the size of every effect; the 4-bit
model is not the model of the LLaDA paper. Sanity gate: A5 accuracy on 40 train problems is within 10 points
of the published figure for the full-precision model, the figure and its page to be recorded by the
lab-engineer [A]. The scoring convention of 13.2 differs from MDLM's. Semi-autoregressive blocks cap the
competitor set at 32, so coupling is strong (k = 16 of 32) but the regime differs from MDLM's N up to 1024.
13.6 **Compute.** H_LL = T_LL * n_prob * n_att * [ (w1' + w2' + w3') * |tau| + w4' * |tau| + w5' ] *
Sum_{k in {4,16}} (256 / k), with w' the overhead factors on a pass that is two to three orders slower than the
sampler step (w' about 1.02 to 1.05 [A]) and T_LL = t_LL / 3600, t_LL the per-sequence-pass seconds at batch B
from setup.md [A: 0.1 to 0.4 s]. Pass-equivalents per attempt are about 9.2 * 80 = 736; for n_prob = 200,
n_att = 1 that is 147k pass-equivalents, 4 to 16 GPU-hours.
13.7 **Stop.** LLaDA runs only after S1 passes; if the sanity gate of 13.5 fails, only the controls run.

## 14. What the review (Paper 1) states under each outcome

Statements are restricted to the checkpoint, evaluator, sampling convention, k set and tau range tested.
Until this card is signed and run, the four-arm measurement stays an open problem with the evidence it needs
(framework-v2 D4 item 4, and the check of 2605.12522 is done: it covers k = 1 only, 2605.12522 experiments
file). The review credits 2605.12522 for the resample fix and the k = 1 comparison.

| Outcome (MDLM-OWT, 130M, plain sampling) | Paper 1 states |
|---|---|
| H1 positive beneficial, H1b positive | SF at k >= 2 carries a measurable joint coupling that improves log GenPPL at matched entropy, growing with k (numbers with intervals); "SF equals a state-dependent tilt" holds in law at k = 1 only; sampler comparisons at k >= 2 cannot treat SF as a tilt |
| H1 positive beneficial, H1b not | A coupling effect is present at some k without a monotone dose pattern; reported as such; no growth claim |
| H1 positive harmful | SF's coupling hurts quality at matched entropy; practitioners' k >= 2 SF decoding pays a cost that a tilted or resampled sampler avoids at the same passes |
| H1 negative (practically zero) and G_sh 0 | At matched entropy SF is indistinguishable from plain sampling at another temperature on this model within the stated margin; reported entropy gains at unmatched temperature are the entropy loss |
| H1 negative and G_sh + | SF's per-position tilt helps beyond a global temperature; coupling is below the margin; a position-dependent tilt suffices on this model |
| H1 inconclusive | The decomposition is stated with its design, the achieved MDE and the intervals; the question remains open; no inference about SF |
| H2: coupling larger than sharpening (Delta2 > 0) / smaller (Delta2 < 0) | The share of the matched-entropy gain assigned to coupling versus sharpening, with the statement that the split is relative to the twin A3 (1.5) |
| H3 | The SF position law against max-probability ranking at k >= 2, at matched entropy, replicating or contradicting the k = 1 result of 2609.34509 |
| H4 fails with N5 passing | Coupling changes diversity on this model; the entropy-deficit read of SF alone does not identify it |
| H5 | Direction on a second model with the stated MDE; no claim if undecided |
| Any gate fails | The estimator is not established on a real network; the review keeps the proposal and the toy verification only and reports the failed gate |
| Underpowered (MDE > 0.03 at the cap) | The review reports the interval and the MDE, not a null |

In every case the review reports the cost of the measurement, that G_cp is a quality contrast and not a KL or
a budget term, and that the split is twin-dependent and checkpoint-specific. It does not state any size of V,
E_fact, E_learn or E_sel.

## 15. Risks the red-team should attack first

1. A3 correctness at N = 1024 with binned scores; the claim "tilted twin" rests on the quadrature (T-A3-2,
   N5); an error here appears as coupling.
2. Entropy matching at one scalar (unigram entropy) can hide longer-range repetition differences; guards 8.3
   catch only part of it.
3. Power: delta_cp = 0.03 may be below what the budget resolves; the ladder trades coverage over k for n.
4. The split depends on A3 (1.5, red-team M1 analogue); a different twin gives a different split.
5. Visited-state shift: contrasts are kernel effects on outputs; common random numbers help only early in each
   trajectory.
6. GenPPL under GPT-2 Large is a weak proxy of quality and shares domain with OWT.
7. Stage A is an entropy-only calibration with a data-defined h*; if MDLM-OWT's entropy curve near h* is flat in
   tau, the cells will not be well placed (IR4 fallback).
8. The tempered-score convention differs from the released LLaDA code; S-U is a descriptive condition only.
9. LLaDA quantisation and its large MDE.
10. Draw-level independence in A3 is across members within a step; across steps it is the sampler's own chain.

## 16. Deliverables of the run

`runs/EXP-002/{constants,s1,pilot,k1,stageA,stageB,eval,conditions,llada}/` each with config, seeds, git SHA of
the code, per-sample token files, per-step logs (N, k, committed scores, entropy of committed marginals, TC_A
in A3 runs), hashes, `manifest.json`, and a verdict file per stage; `analysis/EXP-002/` with `genppl.py`,
`interp.py` (IR1 to IR5), `bootstrap.py`, `placebo.py`, scripts that regenerate every table. Ledger rows
(hypotheses H1 to H5; experiment EXP-002) are added only after both signatures, by the orchestrator.

## 17. Deviations from the brief (read by the orchestrator)

- A3 is computed from the exact Prop. 4 closed form on a score grid (deterministic quadrature, error =
  discretisation, specified by eps_3 and the convergence ladder), not estimated by replicate Monte Carlo with a
  stated M, because conditioning on a specific selected set is infeasible by Monte Carlo (5.3). Monte Carlo
  only enters the final categorical draw. An importance-sampling implementation is allowed if it passes the
  same tests (reports ESS in place of M).
- "Exact-independent toy marginals => the coupling contrast vanishes" is corrected: it vanishes only in the
  Prop. 4 equality cases (N3); peaked heterogeneous independent marginals are a positive control (P2).
- The brief's grid-wide interpolation is implemented as calibrate-then-measure: stage A locates tau for entropy
  h* ± 0.05 (entropy only), stage B measures quality at two cells that straddle h*. Same estimand, about an order
  of magnitude fewer expensive cells.
- Sized for a small coupling effect (delta_cp = 0.03) per the orchestrator's toy prior, with a pre-stated ladder
  rather than an assumed n.
- LLaDA is a direction check with a stated large MDE; HumanEval and pass@k are deferred.
- h* is data-defined (the held-out OWT unigram entropy), not the output entropy of any arm.

## 18. Sign-off

| Role | Check | Status |
|---|---|---|
| statistician | sections 7.4, 9, 11.2: interpolation rule, bootstrap, families and levels, outcome classes, sample-size rule and ladder, firewall | unsigned |
| red-team | sections 1.4, 5.3, 10, 15: A3 correctness, controls, confounds, twin-dependence | unsigned |
| lab-engineer | section 3 filled, S0 and S1 pass, overhead factors and t_f measured | pending |
| novelty-auditor | recheck of concurrent work before freezing (1.3) | pending |
| gate-auditor | stage verdicts against this card | pending |

## 19. Change log

- v0.1 (2026-10-14): first draft by experiment-designer; nothing frozen. Pre-freeze amendments allowed:
  filling section 3, the pilot-derived n_B and ladder choice (9.6), package pins, the tau grid if stage A
  shows h* unreachable (11.1 item 3), the MaskGIT noise schedule (section 3 item 10). Any other change after
  signing creates v0.2 with a dated entry here.
