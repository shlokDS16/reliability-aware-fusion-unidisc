```yaml
agent: experiment-designer
date: 2026-10-14
brief: Preregistration card EXP-002, version 0.2. Decompose the effect of sample-then-filter (SF) decoding at k >= 2 tokens per step into per-position sharpening and joint coupling, on frozen pretrained masked-diffusion text models (MDLM-OWT primary, LLaDA-8B-Instruct secondary), at matched forward passes and matched output entropy. v0.2 applies the statistician's review (2026-10-14) and the measured setup facts.
card:
  id: EXP-002
  version: v0.2
  status: draft, unsigned
  signatures: {statistician: none, red-team: none}
  frozen: false          # frozen when both sign; afterwards changes only as a new version with a change log (section 19)
  hypothesis_ledger_ids: to be assigned when the rows are added (H1, H1b, H2, H3, H4, H5); no ledger rows written by this draft
  supersedes: v0.1 (text preserved in git at commit f719a61)
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-002-value-rule-decomposition.md (v0.1, read in full)
  - research/preregistration/review-statistician-2026-10-14.md (EXP-002 section: 12 required changes R1-R12, recommended O1-O11, power notes, S1-S8; EXP-001 sections not used)
  - analysis/stats/exp002_stats_check.py and .log (the statistician's computations; constants, operating characteristics, N2 power, IR4, H1b, N4)
  - runs/env-2026-10-14/setup.md (sections 0, 1, 3, 4) and runs/env-2026-10-14/timing.json (mdlm block)
  - analysis/framework/check_coupling_k2.log (toy prior; summary lines and per-seed lines)
  - research/review/framework-v2.md, research/review/method/selection-term.md, research/review/audits/2026-10-14-red-team-selection-term.md, research/review/dossier/prior-art-2605.12522-experiments.md, research/review/dossier/prior-art-selection.md (as read for v0.1; not re-read for v0.2, claims below that cite them are carried over)
  - research/ledgers/decisions.jsonl D0012 (as read for v0.1)
coverage: >
  v0.1 sources: read in full at the sections named in v0.1. For v0.2 the statistician review and setup.md
  were read in full, timing.json in full, the toy log in its summary and per-seed lines. NOT read: the MDLM,
  LLaDA, MaskGIT or 2605.12522 code (everything about samplers comes from the dossier files, from setup.md
  (which reports E3 reading of the MDLM sampler at SHA c112c52), or is marked [A]); runs/G4-mdlm-repro-2026-10-14/report.md
  does not exist yet (runs/ holds only env-2026-10-14), so gate G4 is open; no LLaDA number exists (download
  still running, setup.md section 4); setup.md has no OWT held-out split, no MDLM weight hash, no MAUVE or
  second-evaluator pin, no Philox/float64 RNG test (section 3 marks each). Cost figures in section 12 are
  arithmetic on measured forward times and assumed sampler overheads; nothing in this card has been run
  beyond the setup smoke tests.
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
  - statement: "Toy prior (L = 4, V = 3, 12 random q, exact conditional marginals), k = 2: sharpening KL(A3) - KL(A2) = +0.497 mean, positive in 12 of 12 (the log's own label 'negative in 0/12' counts the opposite sign); coupling KL(A1) - KL(A3) = -0.016 mean, negative in 10 of 12; entropy H(A1) - H(A3) = -0.007 mean."
    status: supported
    evidence: analysis/framework/check_coupling_k2.log (summary lines)
    level: E4 (toy)
    confidence: 0.9
  - statement: "MDLM-OWT backbone forward at L = 1024 costs 0.0790 s at batch 8 (9.9 ms per sequence-pass) and 0.325 s at batch 32 (10.2 ms) in the shipped bf16 autocast path; 15.8 ms at batch 1; the fp32 (autocast off) marginals cost 34.5 ms at batch 1. The official sampler returns bf16 probabilities whose masked-row sums range 0.926 to 1.070; bf16 and fp32 marginals agree on top-1 at 0.785 of masked positions with mean entropy difference 0.32 nats on a 50 percent masked state."
    status: supported
    evidence: runs/env-2026-10-14/timing.json (mdlm.forward_L1024, mdlm.marginals_fp32_vs_bf16); setup.md 3.1, 3.2
    level: E4
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
  - precision artifact (32-bit categorical draws truncate and sharpen; bf16 logits of the network are quantised and the bf16 and fp32 marginals differ materially)
  - quantisation artifact on LLaDA-8B
  - evaluator-sampler alignment (GPT-2 prefers tokens MDLM finds likely) and EOS-boundary effects in GenPPL
unknowns: [gate G4 verdict and the precision branch (4.2); the pilot sigma that sets the ladder rung and n (9.6); the sampler overhead s_a, especially A3 (12.2); whether MDLM-OWT reaches the reference entropy at all arms within the tau range; section 3 items marked open]
next_test: {hypothesis: "H1 (coupling), H2 (decomposition)", intervention: "value rule at matched passes, positions and per-position marginals: A1 SF, A2 resampled twin, A3 tilted twin, A4 confidence rank-then-sample", primary_metric: "log GenPPL (GPT-2 Large) at the reference unigram entropy h*, contrast A3 minus A1", falsifier: "section 11", gpu_hours: "MDLM part: plan 36 GPU-hours, hard cap 40 (section 12); bf16 branch expected to land on rung R2 (k in {8, 16}) when sigma_c <= 0.40, fp32 branch on R3 (k = 16) when sigma_c <= 0.49"}
```

# Change log v0.1 to v0.2 (read this first)

v0.1 is preserved in git history at commit f719a61 (`git show f719a61:research/preregistration/EXP-002-value-rule-decomposition.md`).
Source codes: **R n / O n** = the statistician's required change n / recommended change n in
`review-statistician-2026-10-14.md` (EXP-002 part); **B n** = item n of the orchestrator's v0.2 brief; **F** = a measured
setup fact (`runs/env-2026-10-14/`); **D** = a change the designer initiated, listed so the statistician can re-check it.

| # | Source | Where in v0.2 | Change |
|---|---|---|---|
| 1 | R1, B5 | 9.6 | Constants computed with `scipy.stats.norm.ppf`: constant(M) = (z_{1-0.025/(2M)} + z_{0.80})^2 = 13.313, 12.788 (use 12.79), 11.151, 9.505 for M = 5, 4, 2, 1 tests in F1's Holm family (M = 3 gives 12.110). Illustrations: n_B = 889, 2274, 5116 at M = 4 for sigma_up = 0.25, 0.40, 0.60 (v0.1: 885, 2267, 5100). M now counts H1b (change 3). |
| 2 | R2, B3 | 9.5, 11.2, 14 | "Clearly +/-" no longer needs |G| >= margin. A contrast is **supported** when its Holm-adjusted p is below the family level (sign by G), with the qualifier "at or above margin" attached separately. P(supported \| G = delta_cp) = 0.80 is then the stated power; P(supported and at or above margin \| G = delta_cp) = 0.50 is stated beside it. Operating-characteristics table added (statistician's numbers, SE at the M = 4 sized n). Option (a) of R2 chosen. |
| 3 | R3, B1 | 2, 9.4, 11.2 | H1b is the fifth member of F1; Holm over M = |K_R| + 1 tests at 0.025 (K_R = estimable k). Gatekeeping removed. Slope estimator: OLS of the per-k G_cp estimates on log2 k, equal weights, recomputed in every bootstrap replicate over the k frozen in change 8. H1b is tested only when |K_R| >= 3 (at two k the slope is a difference with half the power; it is then reported, not tested). |
| 4 | R4 | 9.6 | Pilot sigma_c = max(sigma_jack, sigma_delta); sigma_delta formula and its inputs written out; same for Delta2 and for the slope; F2 power printed before the ladder is chosen. |
| 5 | R5, B4 | 7.4 IR4 | beta_A defined (OLS on the three stage-A cells nearest h*), stage-A samples resampled independently in every bootstrap replicate, NE if the three cells span < 0.10 nats. The slope uncertainty now enters the interval. |
| 6 | R6 | 9.7 | `freeze.py` runs after all token files exist and before the evaluator: IR branch per (arm, k), IR6 replicate shares, estimable set, M for F1 and F2, hashes of the analysis scripts, written into `manifest.json`. |
| 7 | R7, B1 | 10 (N2-H, N2-Y), 11.1, 12 | N2 split: **N2-H** (entropy only, gates stage B) and **N2-Y** (GenPPL, evaluated in the single evaluation run, gates inference). n_1 from the pilot by the statistician's formula, **capped by a 6-GPU-hour budget for the k = 1 block** (n_1,max = 300 bf16, 150 fp32) instead of 1024; margins widened to the value with P(pass \| exact null) = 0.90 at the capped n_1 and stated before the block; demotion rule if the widened margin is too wide to mean anything. **Disagreement with the cap of 1024:** 1024 samples of two arms at k = 1 cost 19 GPU-hours (bf16, 1024 * 1024 * (c_1 + c_3), section 12); it would take half the programme to test a control. |
| 8 | R8, B4 | 7.4 IR8 (iv) | Curvature check added with the flag "interpolation-sensitive" when the implied bias of a confirmatory contrast exceeds delta/3. **Modified (D6):** fitted by weighted least squares on the stage-A cells with \|E - h*\| <= 0.3 pooled with the two stage-B cells, because stage A has n_A = 64 and A3 has five cells. |
| 9 | R9 | 9.8 (N4), 9.3 | Placebo criterion applies to the rejection rate pooled over all stage-B (arm, k) pairs (band [0.02, 0.09]); random pairing of the two halves; bootstrap over pairs. Monte Carlo precision rule: a p-value within 2 sqrt(p(1-p)/B) of its Holm threshold is recomputed with B = 100,000 and a recorded seed. |
| 10 | R10 | 2 (H2), 11.2 | F2's confirmatory content is the sign of Delta2(k). Rows of the H2 table that need a G_sh class are exploratory and worded "consistent with". |
| 11 | R11 | 9.4 | Error control is per experiment; no split with EXP-001. The review also reports which claims survive with F1 and F2 at 0.0125. |
| 12 | R12 | 9.6 | Pilot prints slopes pooled over arms, one per k; per-arm slopes enter sigma_delta without being printed. |
| 13 | O1 | 9.5, 11.2 | Adopted: the conjunctive "H1 negative" verdict uses 95 percent intervals (intersection-union at 0.025 per claim, same level as F1). P(H1 negative \| G_cp = 0 at all estimable k) = 0.64 at four k and 0.80 at two k [C, statistician]. Per-k "practically 0" statements in the H2 table keep 97.5 percent. |
| 14 | O2 | 5.1, 5.5 | Adopted: uniforms keyed by (seed, s, tag, step, absolute position), L per step, so arms stay aligned when masked sets differ. |
| 15 | O3 | 9.3 | Adopted: BCa interval and Wald interval with the bootstrap SE reported for every confirmatory contrast (sensitivities). |
| 16 | O4 | 7.3 | **Not adopted.** Brackets stay at h* +- 0.05. Reason: stage A (entropy, n_A = 64) places tau with error of the order 0.02 to 0.03 nats, which is large against a +- 0.025 bracket and would raise the share of extrapolated (X) estimates; the curvature risk is handled by change 8 instead. Revisit if the stage-A placement error turns out below 0.01. |
| 17 | O5 | 4 | Adopted: the k = 1 block uses its own index pool s in [3,000,000, ...). |
| 18 | O6 | 2 (H4), 10 | Adopted, modified (D5): H4 is a TOST (90 percent, +-0.05) on H(A1) - H(A3) **pooled over the five stage-A taus that A3 shares with A1**, per k, because a single (tau, k) cell at n_A = 64 passes an exact null only about half of the time. |
| 19 | O7, O8 | 8.3, 8.2 | Adopted: second evaluator "disagrees" = point estimates of opposite sign (interval reported too); GenPPL sensitivity with the context reset at each EOS for A1 and A3 cells, and the EOS rate per arm. |
| 20 | O9 | 13.4, 13.5 | Adopted: first MDE corrected to 0.091; sanity gate on 100 train problems; "undecided" wording changed to "an interval contains 0 and its half-width exceeds the MDE". |
| 21 | O10 | 2 (H2) | Adopted: Delta2 read as "coupling larger than sharpening" only when G_cp and G_sh are both classed +; otherwise \|G_cp\| - \|G_sh\| is descriptive. |
| 22 | O11 | 7.2, 10 (P4) | Adopted: pooled-adjacent-violators mass = sum over tau of \|raw cell mean E - isotonic fit\|, in nats. |
| 23 | F, B2 | 3, 4.2, 12 | **Measured t_f replaces the assumed 7 ms.** Backbone-only forward (we do our own float64 softmax, so the repo's SUBS log-softmax is skipped): 9.9 ms per sequence-pass at batch 8 (bf16), 10.2 ms at batch 32, 15.8 ms at batch 1. **Batch size 8** (best per-sequence time with 2 GB peak, leaving room for the float64 tables). fp32: 34.5 ms (batch 1, measured; batch 8 not measured, used as the upper bound). |
| 24 | F, B2 | 4.2 | **Precision gate PG** (before S0): branch P-bf16 or P-fp32 chosen from the G4 report only, never from EXP-002 data; both branches and their costs stated. |
| 25 | B3 | 4.1, 11.1 | **Gate G4**: no stage of EXP-002 runs until `runs/G4-mdlm-repro-2026-10-14/report.md` says reproduced, or the gap is diagnosed and the orchestrator has logged acceptance. G4 is currently open (the report does not exist). |
| 26 | B4, F | 12 | Budget recomputed from the measured numbers; hard cap 40 GPU-hours for the MDLM part (plan 36, reserve 4); ladder costed per rung and per precision branch; drop order stated. |
| 27 | D1 | 7.2, 12 | **Stage A reduced** (cost, entropy only): runs only for the k of the chosen rung (the ladder is decided before stage A already); A3 runs on **five** grid taus chosen from A1's entropy curve instead of nine; k = 1 stage-A calibration removed (not needed: the k = 1 controls run at tau = 1.0). |
| 28 | D2 | 5.3, 10 (N5) | **N5 reformulated.** v0.1's "G_cp changes by < 0.01 when bins double, on the pilot cells" prints contrast information in the pilot (breaks the firewall) and cannot be resolved at n_p = 32 (paired SE of a Y difference about 0.05). Now: (a) a state-level gate in S1 (TV between bin variants), and (b) one sequence-level sensitivity run at the evaluation (A3 with 2x bins at the largest k, n = 512), descriptive, with a flag. |
| 29 | D3 | 12 | k = 1 matched-entropy cells (G_tot(1)) moved from S5 to S7 (cost 4.4 GPU-hours bf16); P1 needs A2 at k = 1 only for 96 samples. |
| 30 | D4 | 9.6 | N2 sizing variances come from the pilot's tau = 1.0 cells at k in {4, 16} (A1, A3), inflated by an allowance, not from a separate k = 1 pilot (saves 0.4 to 1.0 GPU-hours). |
| 31 | D7 | 9.6 | Ladder rule uses the measured costs of S0-S2 and the sized n_B; first rung whose total plan fits 36 GPU-hours. R0 is kept in the table but is affordable only if sigma_c <= 0.14 (bf16). |
| 32 | D8 | 10 (P3b) | New plumbing control P3b: our `genppl.py` against the repo's own `compute_generative_perplexity` on 64 official-sampler samples. |
| 33 | F | 3 | Section 3 filled where setup.md answers it (MDLM revision, vocabulary, mask id, no time input, sampler defaults, GPT-2 Large revision, torch/transformers pins); open items marked. |
| 34 | F | 15 | New risks: system commit exhaustion (setup.md 0.1), bf16 versus fp32 marginal gap, flash_attn shim not tested for equivalence, bf16 logits create exactly tied token scores. |

Items for the statistician to look at again: 7 (capped n_1 and widened margins), 8 (pooled curvature fit), 18 (H4 form), 27 and 28
(stage A and N5), 30 (N2 variance proxy), 31 (ladder rule with M), 13 (95 percent intervals in the H1-negative conjunction).

---

# EXP-002: value-rule decomposition of sample-then-filter at k >= 2 tokens per step (H1 to H5)

Tags: [S] source fact, [I] inference, [H] hypothesis, [A] assumption until the pilot or setup.md, [V] verified on a toy,
[C] computed (statistician's script or arithmetic on stated inputs), [F] measured in `runs/env-2026-10-14/`.
Nothing in this card has been run beyond the environment smoke tests. Every number marked [A] is replaced by a pilot or
setup estimate before the card is frozen, and the replacement rule is stated next to it. Toy numbers are priors for
direction and size of effect only; they do not transfer to a 170M or 8B network.

## 0. Summary

One frozen checkpoint per model, no training. Unconditional text from MDLM-OWT (L = 1024), plain sampling (no top-p, no
guidance, no Gumbel noise on the ranking), exactly k committed positions per step with T = L/k steps. Four arms share the
forward pass, the tempered marginals and the tie rule at every state: A1 SF; A2 its resampled twin; A3 its tilted twin
(SF's position law and SF's per-position value law given the set, values drawn independently); A4 confidence
rank-then-sample. The contrasts A2 - A3 (per-position sharpening), A3 - A1 (joint coupling, the new quantity) and A2 - A1
(total) are read at a fixed output entropy h*, by interpolation along each arm's temperature curve, because a bare
comparison at one temperature mixes the entropy lost to sharpening with everything else. The single primary endpoint is
the GPT-2 Large log generative perplexity at h*, contrast G_cp(k) = Y(A3) - Y(A1). The design is sized for a small
coupling effect (0.03 log-GenPPL units) because the toy prior says coupling is small next to sharpening and mostly
beneficial. With the measured forward times, 40 GPU-hours cannot cover k in {2, 4, 8, 16} at that size; a pre-stated
ladder, decided from the pilot variance before any quality is seen, trades the number of k for the sample size (expected:
k in {8, 16} in the bf16 branch, k = 16 in the fp32 branch). Two gates precede everything: G4 (the checkpoint reproduces)
and PG (which precision the network runs in). A second model (LLaDA-8B-Instruct, 4-bit, GSM8K) is a direction check with a
stated, large minimum detectable effect. Stages run in order of information per GPU-hour, with gates.

## 1. Claim contract

### 1.1 Claim, one sentence

On a frozen pretrained masked-diffusion text model at matched forward passes and matched output entropy, the quality
difference between sample-then-filter and its resampled twin splits exactly into a per-position sharpening part
(A2 - A3) and a joint coupling part (A3 - A1), and the coupling part is non-zero and grows with the number of tokens
committed per step.

### 1.2 Mechanism and definitions

[I from selection-term.md Prop. 4, Prop. 5, T2.7; V toy]. At one step with masked set M (N = |M|), tempered marginals P_j,
score g_j(v) = P_j(v) (primary), SF draws Y_j ~ P_j for every j in M, ranks by (g_j(Y_j) desc, priority pi_j asc) and
commits the top k. Its commit law kappa_SF(A, y) factors as

    kappa_SF(A, y | s, pi) = prod_{i in A} P_i(y_i) * W_A(m(y)),
    W_A(m) = prod_{j not in A} [F_j^<(m) + 1{pi_j > pi_{i*}} P_j(g_j = m)],   m = min_{i in A} g_i(y_i),

with i* the member of A that attains m and has the lowest tie priority, F_j^<(c) = sum_v P_j(v) 1[g_j(v) < c]
(Prop. 4, exact to 3e-16 on enumerations). Consequences:
- position law rho(A) = sum_y kappa_SF(A, y);
- value law given the set kappa(y | A) is NOT a product for k >= 2, because every member's value is conditioned on the
  common minimum score m (max total correlation 0.0885 nats per step over 400 random toy states, T2.7);
- per-position value laws given the set kappa_i(v | A) = sum_{y: y_i = v} kappa(y | A) are sharpened relative to P_i
  (Prop. 5 majorisation at k = 1; the same direction is expected for k >= 2 [H]);
- at k = 1 the set has one element and kappa_SF equals rho(i) kappa_i(v), a position-dependent state-only tilt
  (red-team F1, block C).

Arms (all use the same marginals, the same tie rule, one forward pass per step, k committed tokens per step):

| Arm | Positions | Values |
|---|---|---|
| A1 SF | top-k of SF's own draw by score | SF's own draw at those positions |
| A2 resampled twin | as A1 (same draw, same tie priorities) | fresh independent draws from P_i at the selected positions |
| A3 tilted twin | as A1 | independent draws from kappa_i(. given A), the per-position marginal of SF's value law given the set |
| A4 confidence rank-then-sample | top-k by max_v P_j(v) | independent draws from P_i |
| A5 (LLaDA only) | as A4 | argmax (the practitioner default, tau -> 0) |

Because A3 is the product of the per-position marginals of kappa(. | A) with SF's own position law, it is the KL
projection of SF's commit kernel onto kernels with the same position law and a product value law given the set
[I: argmin over products nu of KL(kappa(. | A) || nu) is the product of marginals]. Hence (sign convention: Y = log GenPPL,
lower is better; every G is "A-side quality gain", positive = better):

    G_tot(k) = Y(A2) - Y(A1)          total value-rule effect of SF over plain sampling
    G_sh(k)  = Y(A2) - Y(A3)          per-position sharpening given the set
    G_cp(k)  = Y(A3) - Y(A1)          joint coupling (the new quantity)
    G_tot = G_sh + G_cp               (identity of the estimands; the split is defined relative to A3, see 1.5)

All Y are read at the same output entropy h* (section 7). At k = 1, G_cp = 0 in law (A1 and A3 have the same law), so
G_tot = G_sh there.

### 1.3 Closest methods and the exact distinction

- arXiv 2605.12522 (Zhang et al.) [E3 via dossier]: SF versus its resampled twin ("bias elimination") at k = 1 only,
  N = block length 2, 8, 32, one 120M LLaMA-architecture model trained from scratch on a 5000-type vocabulary, temperature
  fixed at 1.0 by code default, no intervals, metrics are n-gram entropy, embedding-based coherence and diversity, and a
  self cross-entropy. Distinction: k >= 2 at matched passes, a temperature sweep with an entropy-matched read, the tilted
  twin (absent from their paper and code), a pretrained 170M model with a 50k vocabulary and an external evaluator, paired
  intervals.
- arXiv 2609.34509 (Jeon et al.) [E2 via dossier]: SF (LCR) versus max-probability ranker (TPP), one token per step,
  LLaDA-8B-Instruct, T in {0.6, 0.8, 1.0, 1.2}, GSM8K and HumanEval. Distinction: same as above; the position-rule
  contrast A2 versus A4 here is a secondary replication at k >= 2 with a matched-entropy read.
- Hayakawa et al. 2510.04525 [E2 via dossier]: noised SF approaches a tilted sampler when N >> k^2 |S|^(1/tau). Used for
  the secondary noise condition S-N (6.4), not claimed.
- Beirami et al. 2401.01879 and the iid k = 1 best-of-N law: the k = 1 analogue; not claimed.
- Zheng et al. (float32 Gumbel truncation sharpens) [S via primer]: the reason for float64 draws (6.1).
- Our own Prop. 4 (k >= 2 SF law) is a derived formula, not an experimental result; the experiment tests what its coupling
  does to quality on a real network, which the toy cannot say.

Novelty on the evidence read: the four-arm comparison at k >= 2 with a tilted twin and an entropy-matched read is not run
in 2605.12522 or 2609.34509 (E3 and E2). A concurrent paper could exist; the novelty-auditor should re-check before the
card is frozen [A].

### 1.4 Competing explanations and their controls

| # | Explanation for a non-zero G_cp or G_sh | Control or analysis |
|---|---|---|
| C1 | A3 estimator error (binning, truncation) manufactures coupling | T-A3-1 to T-A3-4, N1, N2, N5 (5.3, 10) |
| C2 | SF's sharpening is a state-dependent temperature | entropy matching removes the global part; G_sh at h* tests what is left |
| C3 | Metric artifact: equal unigram entropy, different longer-range repetition | distinct-n and 4-gram repetition guard (8.2, 8.3); second evaluator on bracketing cells |
| C4 | Interpolation artifact | two cells straddling h* (7.3); curvature check IR8 (iv); sensitivity IR8; placebo N4 |
| C5 | Visited states differ across arms | stated, not removed: contrasts are kernel effects on the output, not one-step effects (1.5) |
| C6 | Precision artifact | float64 draws and tables in every arm (6.1); TF32 off; precision gate PG (4.2); S1-b precision comparison |
| C7 | Tie-rule artifact at saturated rows | random priorities in every arm (6.2); toy N3 |
| C8 | Quantisation (LLaDA only) | stated threat (13.5); MDLM is the primary |
| C9 | Evaluator domain bias and evaluator-sampler alignment (GPT-2 Large was trained on WebText, close to OWT) | second evaluator on bracketing cells (8.3) |
| C10 | EOS tokens inside the 1024-token sequence make GPT-2 predict across document boundaries | EOS rate per arm; context-reset sensitivity for A1 and A3 (8.3) |

### 1.5 What is NOT claimed

No size of V, E_fact, E_learn, G, E_sel or E_tilt on any model (D0011 withdrew E_sel and E_tilt as new terms and the
red-team showed the SF-versus-tilt split is not canonical, M1). The coupling/sharpening split is defined relative to the
intermediate twin A3; another twin (for instance one fitted to SF's inclusion-conditional value law, or a global-temperature
twin) would give another split. The experiment measures output-quality contrasts of samplers on two checkpoints, not KL.
No claim about the data law q, other checkpoints, other vocabularies, guided sampling, top-p, or revision samplers. The
U-shape in the number of steps is not claimed (M5). The step sweep is not read as identifying E_learn or E_fact (P1, M6);
k is a design factor here. If the ladder lands on rung R2 or R3 (section 9.6), no statement is made about k below the
smallest k that ran, and Paper 1 must not describe the k-range as "k >= 2".

## 2. Hypotheses (falsifiable; direction and minimum effect of interest)

Notation: Y = log GenPPL at h*; K_R = the set of k that is estimable under the chosen ladder rung R (9.6, 9.7), a subset of
{2, 4, 8, 16}; delta_cp = 0.03, delta_sh = 0.05, delta_Delta2 = 0.05 (log-GenPPL units, about 3 and 5 percent relative
perplexity; design choices [A], not derived from literature; reasons in 9.6).

**H1 (primary; coupling).** On MDLM-OWT, G_cp(k) is non-zero. Directional prediction (registered, tested two-sided):
G_cp(k) > 0, i.e. SF's joint value coupling lowers log GenPPL at matched entropy relative to its independent-values twin,
as the toy suggests (coupling lowers KL by 0.016 against sharpening raising it by 0.497 at k = 2, [V] toy, L = 4, V = 3).
Test: G_cp(k) = 0 for each k in K_R (member of F1). Minimum effect of interest |G_cp| >= 0.03: it is the size the design
is powered for (80 percent power for rejecting at the Holm first-step level when |G_cp| = 0.03 at one k), and it is a
qualifier on the verdict, not a condition for it (9.5).
- **H1b (growth).** The slope beta of G_cp(k) on log2 k (OLS, equal weights, over K_R) has the same sign as G_cp at the
  largest k in K_R. Test: beta = 0, two-sided, the fifth member of F1 (Holm over all members at 0.025). Tested only when
  |K_R| >= 3; at two k it is reported as an estimate (the difference of the two G_cp over one doubling) with its interval.
  No margin is registered for beta; the freeze step (9.7) prints the slope that the sized n detects with 80 percent power
  (about 0.02 per doubling at M = 4 if the correlation between the G_cp influence values at different k is about 0.1 [I]).

**H2 (decomposition; which part carries the matched-entropy gain).** Let Delta2(k) = G_cp(k) - G_sh(k)
= 2 Y(A3) - Y(A1) - Y(A2). Two-sided test at each k in K_R (F2). Confirmatory content of F2 is the sign and size class of
Delta2(k) only. The interpretation table below combines Delta2 with the classes of G_sh and G_cp; G_sh is not in a
confirmatory family (9.4), so every cell of the table that needs a G_sh class is exploratory and is worded in Paper 1 as
"consistent with". Classes (11.2): + (supported positive), 0 (practically zero, 97.5 percent interval inside the margin),
- (supported negative), ? (undecided).

| a = G_sh | b = G_cp | Meaning for SF at matched entropy |
|---|---|---|
| 0 | + | The gain is joint coupling; the per-position effect is a temperature (removed by matching) |
| + | 0 | The gain is state-dependent per-position sharpening beyond a global temperature; coupling negligible |
| + | + | Both; Delta2 says which is larger (only when both are classed +; otherwise \|G_cp\| - \|G_sh\| is descriptive) |
| 0 | 0 | SF at matched entropy equals plain sampling at another temperature: the fixed-tau gain is the entropy loss |
| any | - or a - | A component harms quality at matched entropy |
| + and - (or - and +) with G_tot = 0 | | Cancellation: total null hides two non-zero parts |

The a-priori expectation (not a test condition): at fixed tau (secondary S5) sharpening dominates mechanically because it
lowers entropy; at matched entropy the toy gives no prediction for log GenPPL (its metric is KL). H2 is therefore
registered two-sided with no predicted winner.

**H3 (position rule, secondary).** G_pos(k) = Y(A4) - Y(A2): at matched entropy SF's position law ranks no better or worse
than max-probability ranking (two-sided; k in {4, 16} intersected with K_R). Replicates the 2609.34509 contrast at k >= 2.

**H4 (twin validity, secondary).** (i) |H(A1) - H(A3)| <= 0.05 nats (mean per-sequence unigram entropy), as a TOST (90
percent interval inside +-0.05) on the paired-by-index difference pooled over the five stage-A taus that A3 shares with
A1, per k in K_R (bootstrap over sample indices); the toy gives -0.007 on 3.4 at tau = 1. (ii) H(A1) < H(A2) at tau = 1.0
for every k in K_R (95 percent interval excludes 0), from the stage-A cells at tau = 1.0 (positive control P1 at k = 1 is
the gating version). If (i) fails with N5(a) passed, coupling changes diversity, which is itself a result.

**H5 (LLaDA direction, secondary, exploratory).** On LLaDA-8B-Instruct (4-bit), GSM8K accuracy contrasts have the same sign
pattern as H1/H2 at k in {4, 16}; the design can only detect effects of about 10 points (13.4), so H5 is an estimation
target with intervals, not a test with a power claim.

**Kernel-level mechanism readout (no decision rule).** The per-step coupling content TC_A = sum_i H(kappa_i(. | A)) -
H(kappa(. | A)) of the committed set, estimated on real states (S1) and logged in A3 runs, is predicted to be positive,
below 0.1 nats per step, and increasing in k. It is a mediator readout; its relation to G_cp is descriptive.

Directions are stated; each test is two-sided so that a reversed result is detected.

## 3. Setup facts (from runs/env-2026-10-14/setup.md and timing.json, 2026-10-14)

Status column: **filled** = answered by setup.md or timing.json (source named); **open** = not answered, must be filled
before freezing (pre-freeze amendment, 19). The numbers in 9.6 and 12 use the filled values.

| # | Needed | Status | Value or what is missing |
|---|---|---|---|
| 1 | MDLM-OWT identity | filled (hash open) | HF `kuleshov-group/mdlm-owt`, revision `d0958fa851335ece6c15260ce0025f030673c0fb`, Apache-2.0 [setup.md 1]; 169,627,218 parameters (12 blocks, width 768, 12 heads), context 1024, vocabulary 50,258 = GPT-2 (50,257) + mask id 50257, **no time conditioning** (`time_conditioning=false`, sigma ignored; the same network input in every arm by construction), SUBS: mask logit gets -1e6, observed rows become one-hot [setup.md 3.1, 3.2]. Weight SHA-256 not recorded: open. |
| 2 | MDLM official sampler | filled | repo `kuleshov-group/mdlm` @ `c112c526d193436838c98d81455ee51f90309470`; `ddpm_cache`, 128 steps default, `noise_removal=true` (final argmax pass), fp32 Gumbel-max via `torch.rand_like`, random commit order, no temperature, no top-p, no guidance; ReMDM uses fp64 Gumbel and nucleus 0.9 (read only) [setup.md 3.3, 3.4, E3]. Our arms replace its position and value rules; arms use no cache (every step changes the state). |
| 3 | Forward timing, L = 1024 | filled (fp32 at batch 8 open) | bf16 (shipped autocast): backbone only 0.0158 s (batch 1), 0.0790 s (batch 8), 0.325 s (batch 32); full forward with SUBS 0.0210, 0.0894, 0.407 s; peak 1.08, 1.86 (backbone) / 2.34 (full), 4.52 / 7.28 GB. fp32 autocast off, batch 1 only: 0.0345 s, peak 1.41 GB. 1000-step official sample 18.2 s; 128-step 3.5 s [timing.json, mdlm]. |
| 4 | LLaDA-8B-Instruct | open | revision `08b83a6feb34df1a6011b80c3c00c7563e963b07`, MIT, six shards, 16.04 GB; download not finished, nothing loaded, no timing, no quantisation backend tested (bitsandbytes 0.50.2 has a Windows wheel) [setup.md 4]. Released generate code SHA and its settings: open. |
| 5 | GPT-2 Large and second evaluator | partly filled | `openai-community/gpt2-large` revision `32b71b12589c2f8d625668d2335a01cac3249519`, weights SHA matches the LFS oid, MIT [setup.md 1]. fp32 forward time per 1024-token sequence: not measured separately (one sample incl. load 4.5 to 5.4 s); planning value t_G = 0.10 s [A: 1.6 TFLOP per sequence at about 15 TFLOPS], **measured in S0**. Second evaluator (different family, fits 12 GB): open. |
| 6 | mauve-text | open | version, featurizer, arguments: pin by hash, record every argument. |
| 7 | OWT held-out split | open | how MDLM's pipeline builds it, chunking/wrapping rule; three disjoint slices V0, V1, V2 of 2048+ chunks each; draw by seed 20261014, sorted by chunk id. |
| 8 | GSM8K files and extraction script | open | train for pilot, test for main. |
| 9 | Software and RNG | partly filled | Python 3.12.14, torch 2.11.0+cu130, transformers 4.49.0, CUDA 13.0, driver 595.71, sm_120, `env-lock.txt` [setup.md 1]. Shims: pure-PyTorch `flash_attn` stand-in (equivalence to flash-attn not tested), stubbed `mamba_ssm`/`causal_conv1d`. Float64 CUDA uniforms from a counter-based generator keyed by (seed, s, tag, step, position) and batch-size-independence of float64 cumsum/searchsorted: open, tested in S0. |
| 10 | MaskGIT noise schedule (condition S-N) | open | eta_n = 4.5 (1 - (n+1)/T), zero at the last step (framework-v2 B); UniDisc's `maskgit` uses log p + r_temp * Gumbel * t with r_temp 4.5 and t from 1 to 0 [setup.md 2.4]; verify against google-research/maskgit @1db2359. |
| 11 | Environment hazard | filled | System commit was almost exhausted by other sessions; CUDA memory is charged to it; an OOM with free VRAM reported is a commit failure; free commit swings between about 1 and 17 GB; `scripts/common.py::wait_commit` gates heavy stages [setup.md 0, item 1]. Rule in 11.1 item 8. |

## 4. Models, data, seeds, gates

- **Primary: MDLM-OWT**, L = 1024, unconditional, all positions masked at the start, T = L/k steps, exactly k positions
  committed per step (N_n = L - n k). EOS tokens are ordinary tokens. Generation batch **B = 8** sequences per forward (best
  per-sequence time, 9.9 ms in bf16, with a 2 GB peak; B = 32 is 10.2 ms and 4.5 GB; B = 1 is 15.8 ms). The float64 tables are
  built one sequence (or one block of at most 256 masked rows) at a time. The last batch is padded with copies of the final
  index so that every forward has B = 8 (bf16 results are not assumed bit-identical across batch compositions).
  The network input is the backbone logits at the masked rows with the mask column (id 50257) removed; the repo's SUBS
  log-softmax is not used.
- **Secondary: LLaDA-8B-Instruct**, 4-bit (section 13).
- **Reference text.** Three disjoint slices of the held-out OWT chunks: V0 (pilot), V1 (h* and the GenPPL data anchor, 2048
  chunks), V2 (MAUVE reference, size max(n_B, 2048)). Data-defined constants (h*, anchors) are computed from V1 once, before
  any model output exists, and written to `runs/EXP-002/constants.json` with a hash.
- **Seeds.** Sample index s selects a counter-based key. Pilot s in [2,000,000, ...), stage A s in [1,000,000, ...), stage B
  s in [0, n_B), the k = 1 block s in [3,000,000, ...) (its own pool). Streams per (s, step, absolute position): `draw`,
  `prio`, `res`, `tilt` (5.5). No seed is chosen after seeing outputs.
- **No test-set tuning.** tau grid, k set, h*, margins, tolerances and the ladder are fixed by this card, the pilot (variance
  and cost only, firewall in 9.7) and data-defined constants. GSM8K pilot problems come from the train split; main problems
  from the test split.
- **GPU-hours** in this card are wall-clock hours of GPU-resident jobs including retries and failed runs.

### 4.1 Gate G4: the checkpoint reproduces

No stage of EXP-002 starts (S0 to S8, toy tests included), and no GPU-hour of this card is spent, until
`runs/G4-mdlm-repro-2026-10-14/report.md` exists and states either (a) **reproduced**, or (b) **not reproduced, the gap is
diagnosed**, together with the orchestrator's logged acceptance of the diagnosed gap (the decisions-ledger id is copied into
`runs/EXP-002/precision.json`). An undiagnosed gap, or no report, stops EXP-002. What the card needs from the report:
the verdict; the protocol (sampler, steps, evaluator) and the published reference value with its location; the measured
value with an interval; a recommendation on precision (shipped bf16 autocast or fp32, with the evidence); a statement on
whether the pure-PyTorch `flash_attn` shim is numerically equivalent (setup.md 3.5 says it is not tested); and the cause of
the bf16-versus-fp32 marginal gap (top-1 agreement 0.785, mean entropy difference 0.32 nats, row sums 0.926 to 1.070 in the
repo's bf16 probabilities, setup.md 3.2). **Status at v0.2: open** (the report does not exist).

### 4.2 Precision gate PG (after G4, before S0)

The precision of the network is chosen once, from the G4 report only, and written to `runs/EXP-002/precision.json`
(branch, autocast flag, logits dtype, the G4 section it rests on). It cannot depend on any EXP-002 quantity. The float64
softmax, tables and draws are the same in both branches (6.1).

| G4 report says | Branch | Network path | t_f per sequence-pass [F] | Consequence |
|---|---|---|---|---|
| bf16 reproduces (fp32 either also does or is not needed) | **P-bf16** (planning default: the checkpoint was trained in bf16 mixed precision, setup.md 3.2) | shipped autocast; backbone logits (bf16) at masked rows cast to float64, mask column dropped, softmax in float64 (never the repo's bf16 log-softmax) | 9.9 ms at B = 8 | expected rung R2 if sigma_c <= 0.40 (12.5) |
| bf16 distorts and fp32 reproduces (the gap is a precision effect) | **P-fp32** | every autocast in blocks and head disabled (as `mdlm_smoke.marginals_fp32`), TF32 off, logits in fp32 cast to float64 | 34.5 ms (B = 1 measured; B = 8 not measured, used as the upper bound) | 3.5 times the forward cost; expected rung R3 (k = 16 only) if sigma_c <= 0.49; R2 only if sigma_c <= 0.27; H1b untestable |
| neither reproduces, cause unknown | none | | | G4 not passed: stop (4.1) |

Under P-bf16 the logits are quantised to 8 mantissa bits (spacing 0.06 to 0.12 near logit 10 to 20); arms share the same
quantised logits at the same state, so contrasts are internal to the bf16 model, but exactly tied token scores occur;
Prop. 4 handles atoms through its tie term and both A3 recipes must too (5.3). S1-b (below) measures how much the
precision changes the quantities that matter.

## 5. Arms and the step procedure

### 5.1 Common step (all arms; per sample; step n; N masked; k_eff = min(k, N))

```
l      <- backbone logits at masked rows, cast to float64, [MASK] column removed       # N x V, V = 50257
P      <- softmax(l / tau)                                              # tempered marginals, float64
Q      <- P  (primary)  |  softmax(l) (condition S-U, untempered score)
cdf    <- cumsum(P, dim=1); cdf[:, -1] <- 1.0
u      <- U_draw[n][masked positions]  (float64, open interval (0,1), keyed by absolute position)
y_j    <- searchsorted(cdf_j, u_j)           # inverse-CDF draw for every masked j
g_j    <- Q_j[y_j]                           # score of the drawn token
pi     <- U_prio[n][masked positions]        # tie priorities, fresh each step, shared by all arms
rank   <- stable sort by (g desc, pi asc)    # total order, no ties
A      <- first k_eff of rank
```
Last step (N = k_eff): every arm commits all remaining positions; A1, A2, A3 coincide in law there (Prop. 4 equality case
N = k), so the code may shortcut.

### 5.2 Arms

- **A1 SF.** commit y[A].
- **A2 resampled twin.** commit searchsorted(cdf_i, U_res[n][i]) for i in A (fresh uniforms, same P).
- **A3 tilted twin.** for i in A commit a draw from kappa_i(. | A) (5.3), using U_tilt[n][i]. Positions A are exactly A1's.
- **A4 confidence rank-then-sample.** A4 positions = first k_eff of the order by (max_v P_j(v) desc, pi_j asc); commit y[A4]
  (the same `draw` uniforms, so identical to an independent sample from P at those positions).
- **A5 (LLaDA only).** positions as A4 with max_v of the untempered softmax; commit argmax_v.

### 5.3 A3: target law, numerical specification, acceptance tests

**Target.** kappa_i(v | A, s, pi) = sum over y with y_i = v of kappa(y | A), where kappa(y | A) is the Prop. 4 law of 1.2
normalised over y, evaluated with the tempered marginals and the active score. Everything needed (the marginals of all N
masked rows, the score laws, the priorities, the set A) is known without another forward pass. The committed values of A3
are independent across members given A by construction.

**Why this is computed, not sampled by Monte Carlo.** [I] The event "the selected set equals A" has probability rho(A), of
order 1/C(N, k) or smaller (about 2e-6 on average for N = 1024, k = 2); replicate or rejection Monte Carlo cannot condition
on it. The per-position conditional marginal has to come from the closed form, with randomness only in the final
categorical draw, which is exact for the computed law. [This replaces the Monte Carlo estimator suggested in the brief; see 17.]

**Recommended recipe (engineering latitude; the law and tests below are frozen, the recipe is not).**
1. Score axis: 2048 log-spaced bins on [1e-12, 1], plus one top bin for scores within 1e-12 of 1 treated as a tie class
   resolved by priority. Exactly tied token scores (bf16 logits, saturated rows) are atoms and enter through the tie term.
2. For each masked row j, a score histogram of tempered mass h_j[b] = sum_v P_j(v) 1[g_j(v) in bin b] (scatter-add,
   O(N V)); F_j^<(bin b) = prefix sum of h_j below b.
3. W_A as a function of the bin of the minimum member score, as a product over rows not in A of [F_j^< + tie term],
   computed in the log domain.
4. For each member i, the law of the minimum score of the other k - 1 members from their survival functions
   S_l(c) = P(g_l >= c); kappa_i(v | A) is proportional to P_i(v) * E[W_A(min(g_i(v), m_{-i}))], a one-dimensional
   cumulative integral on the grid.
5. Draw v by inverse CDF in the token order of row i with the `tilt` uniform.
6. If a state-wise exact reference is needed, the same computation with the sorted exact token scores (selection-term.md
   T9 Algorithm 1, O(N V log V)) replaces the bins.
An importance-sampling implementation (candidate k-tuples from truncated product proposals, exact weights W_A, independent
resampling of candidate rows per position) is allowed if it passes the same tests and reports its effective sample size
(at least 200 at the S1 states).

**Error specification.** Define eps_3 = mean over selected positions of TV(kappa_hat_i, kappa_i), where kappa_i is the
exact-token-score reference. Requirements at the S1 states: mean eps_3 <= 0.005 and 95th percentile <= 0.02. [I] No
worst-case bound on the path law is available: the per-step TV compounds over L = 1024 committed tokens, so the per-step
bound is vacuous at sequence level. The safeguards are the tests below, H4, and N5.

**Acceptance tests (all before any main data; failure stops the run).**
- T-A3-1 (exact, toy). On 200 random states with N <= 6, V <= 6, k in {1, 2, 3}, tie-free marginals, the production A3
  per-position conditional laws equal the enumeration oracle `kernel("A3")` of `analysis/framework/check_coupling_k2.py` to
  1e-9 (exact token-score grid), and A1-conditional marginals equal A3's to 1e-9. Production code uses random priorities;
  compare tie-free states only, and test the tie case separately against an oracle that averages over priorities.
- T-A3-2 (binned, real vocabulary). On 64 real MDLM states (N in {1024, 512, 128, 32}, k in {2, 16}), the recipe's
  kappa_hat_i against the exact-score reference meets the error specification.
- N5(a) (bins ladder, state level; replaces the v0.1 sequence-level N5). On the same 64 states the recipe is run with half
  and with double the number of bins: mean over selected positions of TV between the two variants is <= 0.002 and its 95th
  percentile <= 0.01.
- T-A3-3 (sampling). On the toy, 2e6 draws of the production A3 sampler: per-position marginals pass a chi-square test
  against the oracle (Bonferroni over positions, alpha 0.05); the within-set Pearson correlation of committed scores is 0
  within Monte Carlo error for A3 and clearly non-zero for A1 on a state where the oracle total correlation is above 0.02
  nats.
- T-A3-4 (reproduce the prior). The production arms, driven through the exact enumeration harness at L = 4, V = 3 with the
  12 q of `check_coupling_k2.py`, reproduce its summary: k = 1 max |p_A1 - p_A3| <= 1e-12; k = 2 sharpening
  KL(A3) - KL(A2) positive in 12 of 12; coupling mean within 0.002 of -0.0164.

### 5.4 What is matched across arms

| Item | Value |
|---|---|
| forward passes per sequence | T = L/k, identical for A1 to A4 |
| tokens committed per step | exactly k (min with N) |
| marginals | the same tempered P at the arm's own state |
| tau | identical function applied to every arm (a cell is an (arm, tau) pair; entropy matching moves tau per arm, 7) |
| score | tempered probability of the drawn token (primary); untempered in S-U |
| tie rule | fresh iid priorities per step, same stream in every arm |
| precision | network per PG (4.2); float64 softmax, cdf, tables and draws in every arm |
| noise on the ranking | none (primary) |
| network input | none beyond the masked state (no time conditioning) |
| batch | B = 8 in every arm |
| per-sample random numbers | common random numbers (5.5) |

### 5.5 Common random numbers

Counter-based generator (Philox or equivalent) keyed by (master seed, sample index s, tag, step n, absolute position j),
float64 uniforms with 53 bits. Tags: `draw`, `prio`, `res`, `tilt`, each one uniform per absolute position per step (L per
step; positions that are not masked or not selected simply do not use theirs). Because the key is the absolute position,
the uniform that an arm uses at position j is the same in every arm whatever the masked set. Every arm consumes `draw` and
`prio` identically, so at step 0 (the all-masked state) A1, A2, A3 select the same set and A1, A4 draw the same values; A2
and A3 differ from A1 only through `res` and `tilt`. Arms diverge afterwards because they visit different states, so the
coupling decays along the trajectory. The benefit is partial and unquantified; the design does not rely on it for validity
(the paired bootstrap is valid with any positive or zero correlation). The pilot measures the realised correlation (9.6).

## 6. Value rule fixed across arms

6.1 **Float64.** The softmax at temperature tau, the cumulative sums, all tables and all uniforms are float64. A float32
control is not run (it would reintroduce the known truncation artefact); a 32-bit unit test in S0 confirms that float32
Gumbel draws sharpen on a toy, as a check that the float64 path matters [H]. The network precision is a separate matter
(4.2).
6.2 **Tie rule.** Fresh iid U(0,1) priority per masked position per step; the lower priority value wins ties in every arm
(SF, A4, A3's W_A). Saturated rows (probability 1.0 in float64) tie exactly, so the rule is exercised; a left-to-right tie
rule is not used because it would add a position bias that differs between SF and A4.
6.3 **No top-p, no top-k, no guidance, no Gumbel noise on the ranking.** Temperature is the only value-rule parameter and is
applied to the marginals before any arm acts.
6.4 **Secondary conditions (run only after the main stages, S7).**
- **S-N (MaskGIT-style noise).** Ranking key log g_j + eta_n G_j with G_j iid standard Gumbel (float64) and
  eta_n = 4.5 (1 - (n+1)/T), zero at the last step [A, item 10 of section 3]. Arms A1, A2, A4 only, k in {4, 16}; A3 under
  noise needs the noise inside kappa and is not specified here. Purpose: does noise close the A1 versus A2 gap (Hayakawa et
  al.)? Descriptive, fixed tau = 1.0.
- **S-U (untempered score).** Score Q = softmax(l) while draws use tau. This is the released LLaDA and 2605.12522 code path
  (untempered score of a tempered draw) [S, dossier]. Arms A1, A2, A3, A4, k in {4, 16}, fixed tau = 1.0. Purpose:
  robustness of the decomposition to the scoring convention. Descriptive.

## 7. Sweeps and entropy matching (primary analysis)

### 7.1 Definitions

Entropy of a sequence: H_s = - sum_v (c_v / L) ln (c_v / L), c_v the count of GPT-2 token v among the L = 1024 generated
tokens (natural log); cell entropy E = mean over samples. Reference entropy h* = mean H over the 2048 held-out chunks of V1
(data-defined; frozen before any model sample exists). Quality Y_s = mean negative log-likelihood per predicted token of the
sequence under GPT-2 Large (8.1); cell Y = mean over samples.

### 7.2 Stage A, calibration (entropy only)

Stage A runs only for the k in the chosen rung R (the rung is decided before stage A, 9.6). n_A = 64 samples per cell
(independent seeds, pool of 4).
- **A1, A2** (and **A4** for k in {4, 16} intersected with R): every tau in Gamma_A = {0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2,
  1.35, 1.5}. Isotonic regression of E on tau per (arm, k); tau_lo and tau_hi are the values at which the fitted curve
  equals h* - 0.05 and h* + 0.05 (linear interpolation of the fitted curve in tau).
- **A3** runs after A1's curve exists, on five consecutive values of Gamma_A: let t* be the grid value whose A1 isotonic
  entropy is nearest h* (ties to the lower tau); A3's taus are t* and its two neighbours on each side (shifted inward at the
  ends of the grid). The same five taus are A1's, so A1 and A3 are paired by index at those taus (H4, IR8 (iv)). A3's own
  isotonic fit of E on tau gives its tau_lo and tau_hi. If A3's fitted range does not contain h* +- 0.05, one extension of up
  to four further grid values on the missing side is run (reserve item in 12.5).
- If the target is outside the fitted range the (arm, k) is "unreachable" (NE) and is reported as a result.
- The pooled-adjacent-violators mass of an (arm, k) is the sum over tau of |raw cell mean E - isotonic fit|, in nats (O11).
Only token files and entropies are produced; the evaluator is not invoked (firewall, 9.7). There is no k = 1 calibration
(the k = 1 controls run at tau = 1.0; the k = 1 matched-entropy cells are in S7).

### 7.3 Stage B, confirmatory cells

For every (arm, k) of the rung: two cells at tau_lo and tau_hi from stage A, n_B samples each, independent seeds from stage
A, common sample index across all cells (5.5). The calibration constants (tau_lo, tau_hi) are design constants in the
inference; calibration uncertainty is not propagated because the realised entropies of stage B enter the interpolation. The
bracket stays at h* +- 0.05 (change-log item 16).

### 7.4 Interpolation rule (fixed now)

For one (arm, k), with stage-B cell means (E_lo, Y_lo) at tau_lo and (E_hi, Y_hi) at tau_hi:
- IR1 If E_lo <= h* <= E_hi: Y(h*) = Y_lo + (h* - E_lo)/(E_hi - E_lo) * (Y_hi - Y_lo).
- IR2 If E_lo > E_hi (inversion from noise): pool the two cells into one cell (mean of E, mean of Y) and use IR4.
- IR3 If h* lies outside [E_lo, E_hi] by at most 0.05 nats: linear extrapolation with the same line, flagged X.
- IR4 If |E_hi - E_lo| < 0.02 nats or after IR2: Y(h*) = Y_cell + beta_A (h* - E_cell). beta_A is the ordinary least
  squares slope of the stage-A cell mean Y on the stage-A cell mean E over the three stage-A cells of that (arm, k) whose E is
  closest to h*. In every bootstrap replicate the stage-A samples are resampled independently (their own index set, stage-A
  seeds) and beta_A is recomputed, so its uncertainty enters the interval. If those three cells span less than 0.10 nats of
  E, the (arm, k) is NE. Flagged S. (Stage-A Y exists only after the single evaluation run, 9.7.)
- IR5 If h* lies outside by more than 0.05 nats: not estimable (NE).
- IR6 The bootstrap (9.3) recomputes IR1 to IR5 in every replicate; a contrast is flagged if more than 5 percent of
  replicates are X or S, and not estimable if more than 5 percent are NE. The branches depend on entropies only, so the
  shares are computed at the pre-evaluation freeze (9.7).
- IR7 No monotone smoothing of Y; no use of stage-A quality in the primary estimate except through beta_A in IR4.
- IR8 Sensitivities (reported; (iv) carries a flag, none changes the decision rules): (i) h* moved to h* - 0.10 and
  h* + 0.10 (needs the extra extrapolation allowance, so flagged); (ii) interpolation linear in tau instead of E; (iii) the
  fixed-tau contrasts of 7.5; (iv) **curvature**: after evaluation, per (arm, k), fit Y = a + b (E - h*) + kappa (E - h*)^2 by
  weighted least squares (weights = cell n) to the stage-A cells with |E - h*| <= 0.3 together with the two stage-B cells
  (at least four stage-A cells are required; A3 has five). The implied interpolation bias of the arm is
  kappa_hat (h* - E_lo)(E_hi - h*). For a confirmatory contrast theta = sum_a c_a Y_a the bias is
  b_theta = sum_a c_a kappa_hat_a (h* - E_lo,a)(E_hi,a - h*); if |b_theta| > delta_theta / 3 (0.010 for G_cp, 0.0167 for
  Delta2) the contrast carries the flag "interpolation-sensitive" and so does the claim made from it. [C, statistician:
  slope differences alone keep the level (0.037); a curvature difference of 6 per nat^2 gives a rejection rate of 0.15 and a
  bias of 0.015.] With stage-A cell means at n_A = 64 the estimate of kappa is coarse (standard error of the order 1 to 2
  per nat^2); the flag is a screen, not a correction.

### 7.5 Fixed-tau comparison (secondary S5)

At tau = 1.0 and k in K_R: contrasts G_tot, G_sh, G_cp of Y and of E from the stage-A cells (arm, tau = 1.0) at n_A = 64
(A3 only if tau = 1.0 is among its five taus; else interpolated in E from its cells, flagged), evaluated in the single
evaluation run. It shows where each arm sits on its frontier at the usual temperature and gives the sharpening-by-entropy
read (H4 (ii), P1). Not corrected for multiplicity; descriptive. New cells at n_B are not planned (S7 only if budget remains).

### 7.6 Frontiers (descriptive)

Stage-A entropy against tau per arm and k, and (after evaluation) the quality-against-entropy points of all cells, plotted
per k. No test.

## 8. Endpoints

### 8.1 Primary (one): log GenPPL at the reference entropy

Y(arm, k) of 7.1 and 7.4. GenPPL protocol (own implementation, pinned; absolute values are not comparable with published
MDLM numbers, which retokenise and truncate after the first EOS, setup.md 3.1): the 1024 generated token ids are fed
directly to GPT-2 Large (`gpt2-large`, revision in section 3, fp32, context 1024, no BOS prepended, no stride); the
negative log-likelihood is averaged over predictions of positions 2 to 1024 (1023 predictions), giving Y_s in nats per
token; GenPPL = exp(Y). Code in `analysis/EXP-002/genppl.py`, git SHA recorded. The primary estimands are G_cp(k) for k in
K_R (H1) and Delta2(k) (H2).

### 8.2 Secondary

- S1 distinct-n (n = 2, 3, 4): unique n-grams over total n-grams per sequence, mean over samples; expected regression for A1
  and A4 at fixed tau.
- S2 4-gram repetition rate: fraction of 4-gram positions whose 4-gram occurs at least twice in the sequence.
- S3 unigram entropy E itself at fixed tau (sharpening readout; expected regression A1 < A2, A4 < A2).
- S4 MAUVE against V2 at the stage-B cells (mauve-text pinned, GPT-2 Large features, equal n per cell, all arguments
  recorded), interpolated at h* by IR1 to IR5. A population metric with a noisy estimate; bootstrap by sequences with 200
  replicates; exploratory.
- S5 fixed-tau contrasts (7.5).
- S6 kernel-level coupling content TC_A per step, entropy deficit of committed values, and committed-score summaries (S1
  stage and A3 runs).
- S7 wall-clock and overhead of each arm.
- S8 position-rule contrast G_pos(k) (H3).
- S9 the S-N and S-U conditions (6.4).
- S10 EOS rate per arm (fraction of generated tokens equal to the EOS id) and the context-reset GenPPL (O8): GPT-2 Large run
  on each EOS-delimited segment separately, for the A1 and A3 stage-B cells; the primary contrast recomputed with it.
- S11 numerical-sensitivity run of N5(b) (10).

### 8.3 Metric guards and the second evaluator

If a primary contrast favours an arm while that arm's 4-gram repetition rate at h* exceeds its comparator's by more than 0.02
(absolute), the result is reported as "quality gain with longer-range repetition" and is not counted as unambiguous support
(11.2). The second evaluator (section 3 item 5, a different model family) is run on the stage-B cells for k in {4, 16}
intersected with K_R; if its point estimate of G_cp(k) has the opposite sign to GPT-2 Large's, the corresponding finding is
downgraded to "evaluator dependent" (its interval is reported too). If the EOS-reset primary contrast (S10) has the opposite
sign to the primary at the largest k, the finding carries the flag "EOS-sensitive".

## 9. Statistics

### 9.1 Unit and design

Unit: a generated sequence, indexed by sample index s (MDLM); problem (LLaDA, 13). Paired design: all cells of all arms share
sample indices and the common random numbers of 5.5; the n_B indices are the resampling unit. Within an (arm, k, tau) cell
the n_B sequences are independent given the model. Y_s is one number per sequence, so there is no within-sequence clustering.

### 9.2 Estimands

Per (arm, k): Y(arm, k) from IR1 to IR5. Contrasts: G_tot, G_sh, G_cp, Delta2 as in 1.2 and 2, G_pos for H3, and the slope
beta of H1b. At k = 1 only the controls are computed (G_cp(1) is a control, not a test).

### 9.3 Interval and p-value

Paired bootstrap over sample indices, B = 10,000 replicates, the same resampled index set applied to every cell, the full
estimator (cell means, IR1 to IR5, contrasts, the slope) recomputed per replicate. Intervals: percentile; BCa and a Wald
interval with the bootstrap SE are reported as sensitivities for every confirmatory contrast (O3). Two-sided p-value:
p = 2 min{ (1 + #{theta* <= 0}) / (B + 1), (1 + #{theta* >= 0}) / (B + 1) }, capped at 1. Replicates in which a needed
Y(arm, k) is NE count as missing and trigger IR6. **Monte Carlo precision rule:** if a confirmatory p-value lies within
2 sqrt(p (1 - p) / B) of the Holm threshold it is compared with, that bootstrap is rerun once with B = 100,000 and a seed
recorded in the manifest, and the B = 100,000 value is used. MAUVE uses 200 replicates with bootstrap over sequences within
each generated set.

### 9.4 Multiplicity and error control

Error control is **per experiment**: EXP-002 is not split against EXP-001 (their claims are unrelated and Paper 1 makes no
disjunctive claim over them). Two confirmatory families, each with family-wise error 0.025 (Bonferroni across the two,
total 0.05):
- **F1**: H1, the tests G_cp(k) = 0 for k in K_R, together with H1b (the slope, when |K_R| >= 3); Holm over M = |K_R| +
  1{|K_R| >= 3} tests at 0.025.
- **F2**: H2, the tests Delta2(k) = 0 for k in K_R; Holm over |K_R| tests at 0.025.
G_sh(k), G_tot(k), G_pos(k), fixed-tau contrasts and secondary metrics are descriptive: unadjusted 95% intervals plus
Holm-adjusted p within each group of at most four, labelled exploratory. LLaDA (13) and the secondary conditions are not part
of the confirmatory budget. **Sensitivity for the review:** every confirmatory decision is also reported at F1 and F2 =
0.0125 (Bonferroni across the two experiments), with a column saying which claims survive; both come from the same bootstrap
output.

### 9.5 Outcome classes per hypothesis test (used in 11)

For a contrast theta with Holm-adjusted p-value p~ in its family (level alpha_F = 0.025) and margin delta (delta_cp = 0.03 for
G_cp; delta_Delta2 = 0.05 for Delta2; none for the slope):
- **supported (+ or -)**: p~ < alpha_F; the sign is the sign of the estimate. The qualifier **at or above margin** is added
  when |estimate| >= delta, **below margin** otherwise. A "supported" verdict says the effect is not zero; the qualifier says
  whether it reaches the size the design is powered for.
- **practically 0**: the bootstrap interval lies inside (-delta, delta). Per-k statements (H2 table) use the 97.5 percent
  interval (two one-sided tests at 0.0125, covering the Bonferroni over the four k). The conjunctive verdict "H1 negative"
  (11.2) uses the 95 percent interval at each k, an intersection-union test at 0.025 per claim, which needs no further
  adjustment (O1).
- **undecided (?)**: anything else.

Operating characteristics [C: `analysis/stats/exp002_stats_check.log`, "9.5 outcome classes"; normal approximation, standard
error SE = delta_cp / (z_M + z_0.80) = 0.0084 for M = 4; at M = 2 and M = 1 the SE is 0.0090 and 0.0097 and the figures move
by a few thousandths; the freeze step prints the table for the chosen M]:

| true G_cp | P(supported) at the Bonferroni level | P(supported and at or above margin) | P(practically 0), 97.5% interval | P(practically 0), 95% interval |
|---|---|---|---|---|
| 0.000 | 0.006 | 0.000 | 0.819 | 0.895 |
| 0.015 | 0.171 | 0.037 | 0.325 | 0.431 |
| 0.030 | 0.800 | 0.500 | 0.012 | 0.025 |
| 0.040 | 0.979 | 0.884 | 0.000 | 0.001 |
| 0.050 | 0.999 | 0.992 | 0.000 | 0.000 |

So: the power of 0.80 refers to "supported" at G_cp = 0.03 at one k; the probability of "supported and at or above margin"
at exactly 0.03 is 0.50, and 0.80 at about 0.037. If G_cp = 0 at every estimable k, P(H1 negative) with the 95 percent rule
is 0.64 at four k and 0.80 at two k (independent k assumed; 0.45 and 0.67 with the 97.5 percent rule) [C]: a true zero ends
as "H1 negative" in about two thirds to four fifths of runs and as "inconclusive" otherwise.

### 9.6 Sample size, the pilot and the ladder [A until the pilot]

**Constants.** With M the number of tests in F1's Holm family and power 0.80 at one test at its Bonferroni (Holm first-step)
level:

    constant(M) = (z_{1 - 0.025/(2M)} + z_{0.80})^2          (scipy.stats.norm.ppf)
    M = 5: 13.313      M = 4: 12.788 (use 12.79)      M = 3: 12.110      M = 2: 11.151      M = 1: 9.505
    n_B(R) = ceil( constant(M_R) * sigma_up^2 / delta_cp^2 )                 (delta_cp = 0.03)

z_{0.80} = 0.8416. Illustrations only [A], sigma_up = 0.25, 0.40, 0.60: n_B = 925, 2367, 5326 (M = 5); 889, 2274, 5116
(M = 4); 775, 1983, 4461 (M = 2); 661, 1690, 3803 (M = 1). The minimum detectable effect at n_B is
MDE = (z_{1 - 0.025/(2M)} + z_{0.80}) sigma_up / sqrt(n_B). The rule sizes the k-tests; F2 and H1b are not what it sizes (the
pilot prints their power, below).

**Pilot (variance and cost only; S2).** n_p = 32 samples per cell, arms A1, A2, A3, k in {4, 16}, tau in {0.9, 1.0, 1.1},
indices disjoint from main. The pilot analysis script prints only: seconds per pass and per step for each arm (the sampler
overhead s_a of 12.2), peak memory; per-cell SD of Y_s and of H_s (SDs, no means) and their within-cell correlation; the
correlations rho_tau (of the per-sample influence values psi between adjacent-tau cells of one arm at the same s, pooled over
arms) and rho_ab (between arms a and b at the same tau and s, and between k = 4 and k = 16); the local slope dY/dE **pooled
over arms, one value per k** (R12; per-arm slopes enter sigma_delta without being printed); and, for each of G_cp(k),
Delta2(k) and the slope: sigma_jack, sigma_delta and sigma_c. It prints no cell mean of Y and no contrast mean (9.7).

- sigma_jack: the leave-one-out jackknife standard deviation of the per-sample influence values of the contrast under the
  full estimator (IR1 to IR5, IR4 allowed because the pilot cells may not bracket h*) applied to the pilot cells nearest in
  entropy to h*.
- sigma_delta: the delta-method value of the stage-B IR1 estimator at interpolation weight w = 0.5 from pilot components:

        sigma_delta^2 = 0.5 (1 + rho_tau) c' Sigma c,        Sigma_ab = rho_ab sigma_psi,a sigma_psi,b over arms (A1, A2, A3), rho_aa = 1,
        c = (-1, 0, 1) for G_cp,    c = (-1, -1, 2) for Delta2,
        sigma_psi,a^2 = sigma_y,a^2 + beta^2 sigma_h,a^2 - 2 beta rho_yh,a sigma_y,a sigma_h,a,

  beta the pilot slope dY/dE pooled over arms at that k. For the slope over {4, 8, 16} (OLS on log2 k) the influence is
  (psi_16 - psi_4)/2 and sigma_delta^2(slope) = (sigma_16^2 + sigma_4^2 - 2 rho_k sigma_16 sigma_4)/4 (the k = 8 term has weight
  zero); for slope over {2, 4, 8, 16} the weights are (-1.5, -0.5, 0.5, 1.5)/5 on k = 2, 4, 8, 16.
- sigma_c = max(sigma_jack, sigma_delta), taken as the larger of k = 4 and k = 16;

        sigma_up = sigma_c * sqrt( (n_p - 1) / chi2_{0.20, n_p - 1} ) = 1.1305 * sigma_c        (one-sided 80 percent upper bound).

  For rung R0 the unmeasured k = 2 is covered by an allowance sigma_up x 1.2 [A].
- Before the ladder is chosen the script prints F2's power (probability of rejecting Delta2 = 0.05 at its Bonferroni level at
  the n_B of each rung, from sigma_c(Delta2)) next to F1's, and the detectable slope for H1b.
- For N2 (10): sigma_up,Y and sigma_up,H are the largest per-cell SDs of Y_s and H_s over the A1 and A3 pilot cells at tau = 1.0
  and k in {4, 16}, times the factor 1.1305 and an allowance 1.2 for k = 1 [A] (no separate k = 1 pilot).

**Ladder (decided from the pilot and the measured costs of S0 to S2, before stage A, logged).** The rungs:
- R0: K = {2, 4, 8, 16}, M = 5 (four k and H1b); Sum_k P(k) = 960
- R1: K = {4, 8, 16}, M = 4 (three k and H1b); Sum = 448
- R2: K = {8, 16}, M = 2 (H1b not tested); Sum = 192
- R3: K = {16}, M = 1; Sum = 64 (H1b and any growth statement untestable)
Choose the first rung R, in the order R0, R1, R2, R3, whose total plan H(R, n_B(R)) of 12.4 is at most 36 GPU-hours (the
hard cap is 40, 12.1). If even R3 does not fit, run R3 at the n_B that fits and state the achieved MDE; the outcome is then
"underpowered for delta_cp unless MDE <= delta_cp". The choice cannot depend on any quality contrast (9.7). Section 12.5
gives the sigma_c each rung supports at the planning costs: bf16 branch 0.14, 0.23, 0.40, 0.69 for R0 to R3; fp32 branch
0.06, 0.14, 0.27, 0.49. Since the statistician expected sigma_c between 0.3 and 0.7 [I], R2 or R3 is the likely outcome and
k = 2 and k = 4 are not tested; Paper 1 states the rung.

delta_cp = 0.03 is the smallest effect a reader can interpret (3 percent perplexity) and that the ladder can plausibly
resolve; it is a design choice [A], not a literature value. delta_sh = delta_Delta2 = 0.05 reflect that sharpening effects
are expected to be larger. The toy ratio of coupling to sharpening (0.016 to 0.497, KL at fixed entropy loss) motivates sizing
for the small effect; it does not predict the real ratio.

### 9.7 Firewall, no peeking, pre-evaluation freeze

The pilot analysis script and the stage-A script are written so that they do not compute or print Y means or any contrast of
Y. The pilot script's source is hashed in `runs/EXP-002/pilot/` before the pilot is generated. The evaluator is invoked on
pilot, stage-A, stage-B and k = 1 token files only after all of them are generated, hashed and listed in
`runs/EXP-002/manifest.json`, in one evaluation run. No interim test, no sequential stopping, no extension of n after seeing
quality. Evaluation runs once. Stage-A token files are evaluated only in that run (for beta_A, the curvature check and the
frontier plots), never before.

**Pre-evaluation freeze (R6).** After all stage-B and k = 1 token files exist and before the evaluator runs,
`analysis/EXP-002/freeze.py` computes from entropies alone, and writes into `manifest.json` with hashes: the IR branch of
the point estimate for every (arm, k); the IR6 replicate shares of X, S and NE; the estimable set K_R; M for F1 (including
H1b) and for F2; the operating-characteristics table of 9.5 for the realised SE; the slope detectable at 80 percent power for
H1b; and the hashes of `interp.py`, `bootstrap.py`, `placebo.py`, `genppl.py` and `freeze.py`. None of these can change after
evaluation.

### 9.8 Placebo (N4)

Within each (arm, k) stage-B cell pair, randomly split the n_B indices into two halves, pair the halves' indices at random,
treat the halves as two "arms" (same arm label), and run the full estimator and the paired bootstrap over pairs for 200
random splits. The pass criterion applies to the rejection rate (0.05 two-sided) **pooled over all stage-B (arm, k) pairs**,
which must lie in [0.02, 0.09]; the interval coverage of 0 is reported. [C: per pair with all 12 required to pass a valid
test passes only 0.876 of the time; pooled it passes essentially always and still fails a test whose true level is 0.10.]
Costs no GPU.

## 10. Controls

Negative controls (the effect must vanish) and positive controls (a known effect must be recovered). All are gates in 11.

| ID | Type | Setup | Pass criterion | Protects |
|---|---|---|---|---|
| N1 | negative | k = 1: A1 versus A3 commit law. Exact on the toy (max difference); on real MDLM states with N in {8, 16, 32} from k = 1 trajectories, 2e5 rounds each, 32 states (64 if N2-H is demoted), chi-square on pooled joint (position, value) cells | toy <= 1e-12; real: no rejection at Bonferroni alpha 0.05/32 | A3 machinery at k = 1 |
| N2-H | negative, **gates stage B** (entropy only, no evaluator) | k = 1, tau = 1.0, A1 versus A3, n_1 samples each, index pool of the k = 1 block; TOST 90% interval of H(A1) - H(A3) with the arms treated as unpaired | inside +-m_H, m_H = max(0.03, 3.29 sigma_up,H sqrt(2/n_1)) | A3 at sequence scale |
| N2-Y | negative, **gates inference** (evaluated in the single evaluation run with stage B) | same samples; TOST 90% interval of Y(A1) - Y(A3) | inside +-m_Y, m_Y = max(0.05, 3.29 sigma_up,Y sqrt(2/n_1)); failing means F-control for every G_cp conclusion | A3 at sequence scale in quality |
| N3 | negative | state-independent toy models (L = 64, V = 32): flat marginals; one-hot marginals. Prop. 4 equality cases: A1, A2, A3 are equal in law for any k | all pairwise two-sample tests on token histograms and on pair statistics, 20,000 sequences per arm, alpha 0.01 with Bonferroni, no rejection; the one-hot case exact | tie rule, pipeline, no spurious G |
| N4 | negative | placebo split-half (9.8) | pooled rejection rate in [0.02, 0.09] | bootstrap and interpolation false positives |
| N5 | negative/diagnostic | (a) state level, gate: bins halved and doubled on the 64 S1 states (5.3). (b) sequence level, descriptive: A3 with double the bins, at the largest k of the rung, tau_lo, n = 512, same indices as the stage-B A3 cell; GenPPL difference and entropy difference with paired intervals | (a) mean TV <= 0.002, 95th percentile <= 0.01. (b) if the 95% interval of the Y difference excludes 0 with \|difference\| >= 0.01, G_cp at that k carries the flag "numerically sensitive" | A3 numerical error |
| P1 | positive, gates stage B | MDLM-OWT, k = 1, tau = 1.0: SF sharpens, so H(A1) < H(A2) (the 2605.12522 direction at k = 1); A2 on the first 96 indices of the k = 1 block, A1 on the same 96 | difference negative with 95% interval excluding 0 | float64 draws, score definition, arm wiring |
| P2 | positive | toy with peaked heterogeneous independent state-independent marginals (Dirichlet 0.3, L = 64, k in {4, 16}), exact within-set total correlation from Prop. 4 | A1 minus A3 pair statistic matches the exact value within Monte Carlo error; A3 is 0 | coupling is detectable by the statistic when present |
| P3 | positive | evaluator: GenPPL of held-out chunks (V1) versus the same chunks with tokens shuffled within sequence; MAUVE of V1 against V2 versus shuffled; also measures t_G | GenPPL(shuffled) / GenPPL(data) >= 3; MAUVE data vs data above 0.9 at n = 2048 vs 2048; shuffled below 0.1 | evaluator wiring |
| P3b | positive | our `genppl.py` against the repo's `Diffusion.compute_generative_perplexity` (retokenised, truncated after the first EOS) on the same 64 samples from the official sampler | Spearman correlation of per-sample values >= 0.9; the mean log ratio is reported (it is not required to be 0) | our evaluator is the repo's up to the stated differences |
| P4 | positive | stage A: E is increasing in tau for each (arm, k) up to noise; GenPPL rises with E in stage B | pooled-adjacent-violators mass (7.2) < 0.05 nats; slope dY/dE > 0 | interpolation is meaningful |
| P5 | positive | T-A3-4 reproduction of the toy prior | as in 5.3 | arms implemented as in the prior |

**N2 sizing (R7, D4).** From the pilot (9.6): n_req = ceil( 2 (z_0.95 + z_0.95)^2 max( sigma_up,Y^2 / 0.05^2, sigma_up,H^2 / 0.03^2 ) )
(the arms are treated as unpaired, no credit for correlation), n_1 = min( n_1,max, max(256, n_req) ), where n_1,max is set by
a 6-GPU-hour budget for the whole k = 1 block (A1 and A3 at n_1 each plus A2 at 96): n_1,max = 300 in the bf16 branch and
150 in the fp32 branch at the planning costs (12.3); with the cost measured in S2 the same budget is recomputed and the
integer fixed before the block. [C, statistician: n_req on Y is 542, 780, 1386, 2165 at sigma_y = 0.25, 0.30, 0.40, 0.50 and
on H is 241, 542, 962 at sigma_H = 0.10, 0.15, 0.20; so the cap binds in most cases.] When the cap binds the margins are
widened to m = 3.29 sigma_up sqrt(2/n_1) (the value at which P(pass | exact null) = 0.90), computed and logged before the
block; the achieved margins are stated in Paper 1. At the cap the planning values are m_H = 0.040 (sigma_H = 0.15, n_1 = 300)
and m_Y = 0.081 (sigma_Y = 0.30), i.e. N2 detects gross failures of A3, not errors at the scale of delta_cp = 0.03; the
finer protection against such errors is N1, T-A3-2, N5(a). A correct pipeline still fails N2-H with probability 0.10; that
risk is accepted. **Demotion:** if m_H > 0.06, N2-H is reported but does not gate stage B and N1 (real states) runs with 64
states; if m_Y > 0.10, N2-Y is reported only.

Note on the brief's wording: the coupling contrast vanishes for "exact independent toy marginals" only in the Prop. 4
equality cases (flat on the support, one-hot, N = k, or no competitor score between a position's extreme scores). With peaked
heterogeneous independent marginals SF still couples committed values (and sharpens), which is what P2 uses as a positive
control; N3 uses the cases where the equality holds.

## 11. Stop rules, outcome classes and falsifiers

Staging is by information per GPU-hour (12). Each stage ends in a written verdict file; the next stage runs only if its
precondition holds.

### 11.1 Stop rules

0. **G4 and PG** (4.1, 4.2): no stage runs before G4 is satisfied and `precision.json` exists.
1. **S0/S1 gate.** If any of T-A3-1 to T-A3-4, N1, N3, P2, P5, N5(a) fails, stop; no stage after S1 runs; the failure is
   logged and the orchestrator is told. P3 or P3b failing stops the evaluator-dependent stages only.
2. **Pilot gate and ladder.** 9.6. If sigma_up implies that R3 at the plan has MDE > 0.10, stop before stage A and report the
   design as not decidable at this budget (a result about the budget, not about SF).
3. **Calibration gate (stage A).** If for A1, A2 or A3 at some k in the rung the target h* is unreachable in Gamma_A (after
   the single A3 extension), or the entropy curve has pooled-adjacent-violator mass above 0.05 nats, stop, issue the next card
   version with a changed grid (before any stage-B data), and continue. For A4, unreachable is reported, not a stop.
4. **Control gates at scale.** N2-H, P1 and N1 (real states) failing stops stage B (the k = 1 block precedes stage A, 12).
   N2-Y failing is F-control for all G_cp conclusions, decided at evaluation.
5. **Budget.** The hard cap of 40 GPU-hours for the MDLM part is never exceeded without the orchestrator. If cumulative GPU
   time in a stage exceeds 1.5 times its pre-run estimate, stop and ask the orchestrator. An A3 overhead above 6 forward passes
   per step (c_3 above 6 t_f) triggers the reduced-score-bin variant only if T-A3-2 and N5(a) still pass at the reduced bins;
   otherwise the next rung down.
6. **Numerical.** NaN or Inf in logits or tables, or |cdf[:, -1] - 1| above 1e-9 before clamping, stops the run.
7. **No peeking, no extension** (9.7).
8. **Commit failures.** A CUDA out-of-memory with several GB of VRAM reported free is a system-commit failure (setup.md 0):
   wait on `wait_commit`, retry the batch; retries count in GPU-hours; three consecutive failures of one job stop it and are
   reported. Seeds are keyed by index, so a retry reproduces the same samples.

### 11.2 Outcome classes for the primary family (MDLM-OWT, k in K_R, estimable k only)

Let "supported" be as in 9.5. A supported G_cp(k) is **counted** when it is not repetition-flagged (8.3), the second evaluator
(where run) has the same sign, and N2-Y and N5(b) did not fail; flags "interpolation-sensitive", "numerically sensitive",
"evaluator dependent", "EOS-sensitive" are carried by the claim.
- **H1 positive (beneficial)**: at least one k with G_cp(k) counted and positive; **(harmful)**: counted and negative. Sign is
  part of the finding. The size qualifier of 9.5 ("at or above margin" or "below margin") is attached.
- **H1b positive**: |K_R| >= 3, the slope is supported in F1's Holm family, with the sign of G_cp at the largest k. **H1b not
  tested** at two or fewer k. **H1b not supported** otherwise; this is reported with its interval and the detectable slope and
  is not a falsification (power is limited, 2).
- **H1 negative (practical zero)**: G_cp(k) practically 0 (95 percent intervals, 9.5) at every estimable k in K_R, at least
  two k including the largest. Then the claim of a practically relevant coupling effect is falsified on this model at
  delta_cp = 0.03. A non-zero effect below 0.03 is not excluded. If K_R has one k, "H1 negative" cannot be declared; the
  outcome at one k is stated as "practically 0 at k = 16".
- **H1 inconclusive**: otherwise, including the "underpowered" outcomes of 9.6.
- **H2** outcome per k from the table of section 2 using the classes of 9.5 (G_sh rows exploratory); reported with Delta2.

### 11.3 Falsifiers

- F-H1: all estimable G_cp(k) practically 0 (above).
- F-H1b: not a falsifier (11.2).
- F-H2-twin: the decomposition is not interpretable if H4 (i) fails with N5(a) passed (A3 is not an entropy-equivalent twin);
  then G_sh and G_cp are reported but the split is called twin-dependent in addition to 1.5.
- F-mechanism: the kernel-level TC_A is below 1e-3 nats per step at all k >= 2 on real states while G_cp is supported. Then
  the effect is not explained by the mechanism and competing explanation C1 or C5 is raised (a check on the estimator and on
  visited-state shift).
- F-control: any N or P gate failing means no inference about SF from that stage.

### 11.4 What each outcome means for the claim and the review

See 14. In all cases the claim is restricted to MDLM-OWT (and LLaDA-8B 4-bit for H5), the precision branch, GPT-2 Large,
plain sampling, the tau range and the k set that ran.

## 12. Run order and compute budget (12 GB laptop GPU)

Order is by information per GPU-hour: analytic and toy checks, a frozen-checkpoint step-level measurement, a pilot, controls
at k = 1, calibration, the confirmatory cells, evaluation, secondary conditions, then LLaDA. All figures below are arithmetic
on the inputs of 12.2; they are plans, not results, and are replaced by the S0 to S2 measurements at the ladder decision.

### 12.1 Cap

Hard cap for the MDLM part (S0 to S7): **40 GPU-hours**. Plan: **36** (S0 to S6 including the sensitivity runs); the other 4
are the reserve (A3 extension 0.7, commit retries, overruns) and the only room for S7. LLaDA (S8) is outside this cap and
needs the orchestrator's approval of its own figure once t_LL is measured.

### 12.2 Inputs

Measured [F, timing.json]: t_f (backbone, per sequence-pass) = 0.0099 s (bf16, B = 8); 0.0345 s (fp32, B = 1, upper bound for B = 8).
Assumed [A], replaced in S2: sampler overhead per sequence-pass in float64 (attributable to the tables, independent of the
network precision): s_1 = 5 ms (A1), s_2 = 5.5 ms (A2), s_3 = 40 ms (A3), s_4 = 5 ms (A4). Reasoning: at N = 512 masked rows
an fp64 table is 0.2 GB, about 8 passes over it plus the fp64 exponentials come to 4 to 6 ms; A3 adds a histogram scatter
and the bin integrals, taken as 8 times s_1 on purpose (v0.1 assumed 16 ms in absolute terms). t_G = 0.10 s per 1024-token GPT-2
Large sequence (fp32). Per-sequence-pass cost of arm a: c_a = t_f + s_a.

| | t_f | c_1 | c_2 | c_3 | c_4 | c_1 + c_2 + c_3 |
|---|---|---|---|---|---|---|
| P-bf16 | 9.9 ms | 14.9 | 15.4 | 49.9 | 14.9 | 80.2 ms |
| P-fp32 | 34.5 ms | 39.5 | 40.0 | 74.5 | 39.5 | 154.0 ms |

(v0.1 assumed t_f = 7 ms and c_1 + c_2 + c_3 = 41.4 ms.) P(k) = 1024/k passes per sequence; Sum over K = {2, 4, 8, 16} is 960
and over {4, 16} is 320.

### 12.3 Stage formulas (GPU-hours; divide seconds by 3600)

| Stage | Content | Precondition | Formula |
|---|---|---|---|
| S0 | toy and analytic tests (CPU): T-A3-1, T-A3-3, T-A3-4, N1 (toy), N3, P2, P5, float32 sharpening unit test; evaluator P3, P3b; timing of the chosen branch at B = 8 and of GPT-2 Large (t_G) | G4, PG | 0.25 |
| S1 | frozen-checkpoint step-level: 64 sequences generated by A2 at tau = 1.0 for each k in {2, 4, 8, 16} give states at fractions {0, 0.1, 0.25, 0.5, 0.75, 0.9} of the steps; T-A3-2, N5(a), N1 (real states), TC_A, committed-score summaries; **S1-b**: the same 64 states in the other precision, reporting TV of the committed-set marginals and TC_A (informational) | S0 pass | 64 * 960 * c_2 + 0.5 (tables and N1 real, [A]) |
| S2 | pilot (9.6) | S1 pass | 32 * 3 * 320 * (c_1 + c_2 + c_3) + 0.1 (evaluation of 288 pilot sequences, analysis) |
| S3 | k = 1 block: A1 and A3 at n_1 each, A2 on 96 indices, tau = 1.0 (N2-H, P1; N2-Y later) | S2 pass | n_1 * 1024 * (c_1 + c_3) + 96 * 1024 * c_2 |
| S4 | stage A, rung R, n_A = 64: A1 and A2 on 9 taus, A3 on 5, A4 on 9 taus for k in {4, 16} of the rung | S3 pass (N2-H, P1) | 64 * Sum_R * [9 (c_1 + c_2) + 5 c_3] + 64 * 9 * c_4 * Sum_{R and {4,16}} |
| S5 | stage B, n_B per cell | S4 pass | n_B * [2 (c_1 + c_2 + c_3) Sum_R + 2 c_4 Sum_{R and {4,16}}] |
| S6 | evaluation, one run: primary GenPPL over all stage-B sequences, second evaluator on A1 to A4 at k in {4, 16}, MAUVE features, EOS-reset for A1 and A3, plus pilot, stage-A, k = 1 files (small); N5(b) run 512 * (1024/k_max) * c_3 | S5 generated and hashed | t_G * n_B * [2 (6 |R| + 2 r_46) + 8 r_46 + 4 |R|] + N5(b), r_46 = number of k of the rung in {4, 16} |
| S7 | secondary, only from the reserve, in this order: S-U (A1 to A4, k in {4, 16}, tau = 1.0, n = 256); S-N (A1, A2, A4, same); k = 1 matched-entropy cells (A1, A2, two taus, n = 256) | S6 analysed, remaining budget at least the item plus 1 | 256 * 320 * (c_1 + c_2 + c_3 + c_4); 256 * 320 * (c_1 + c_2 + c_4); 256 * 1024 * 2 * (c_1 + c_2) |
| S8 | LLaDA (13) | G4, S1 pass, download finished, orchestrator approval | 13.6 |

### 12.4 Worked values at the planning costs

| Item (GPU-hours) | P-bf16 | P-fp32 |
|---|---|---|
| S0 | 0.25 | 0.25 |
| S1 | 0.76 | 1.18 |
| S2 | 0.78 | 1.41 |
| S3, with n_1,max (A1 + A3 at n_1; A2 at 96) | 5.95 (n_1 = 300: 5.53 + 0.42) | 5.96 (n_1 = 150: 4.87 + 1.09) |
| **Fixed stages S0 to S3** | **7.75** | **8.80** |
| S4 by rung: R0 / R1 / R2 / R3 | 9.68 / 4.92 / 1.94 / 0.75 | 20.59 / 10.69 / 4.12 / 1.64 |
| S5 per 1000 n_B: R0 / R1 / R2 / R3 | 45.42 / 22.61 / 9.08 / 3.38 | 89.16 / 45.35 / 17.83 / 6.88 |
| S6 per 1000 n_B: R0 / R1 / R2 / R3 | 2.44 / 2.00 / 1.22 / 0.78 | same (t_G does not depend on the branch) |
| N5(b) at the rung's largest k (R0 to R3 all k_max = 16) | 0.45 | 0.68 |
| S7 items: S-U / S-N / k = 1 matched cells | 2.16 / 1.03 / 4.41 | 4.40 / 2.71 / 11.58 |

### 12.5 Ladder at the plan of 36 GPU-hours

n_B affordable = floor( (36 - fixed - S4 - N5(b)) / (S5 + S6 per n_B) ). sigma_up max = the largest sigma_up for which that n_B
reaches MDE = 0.03 (n_B >= constant(M) sigma_up^2 / 0.03^2). MDE at sigma_up = 0.25 / 0.40 / 0.60 is at the affordable n_B.

| Branch, rung (k; M) | n_B affordable | sigma_up max (sigma_c max) | MDE at sigma_up 0.25 / 0.40 / 0.60 |
|---|---|---|---|
| bf16 R0 ({2,4,8,16}; 5) | 378 | 0.16 (0.14) | 0.047 / 0.075 / 0.113 |
| bf16 R1 ({4,8,16}; 4) | 929 | 0.26 (0.23) | 0.029 / 0.047 / 0.070 |
| bf16 R2 ({8,16}; 2) | 2509 | 0.45 (0.40) | 0.017 / 0.027 / 0.040 |
| bf16 R3 ({16}; 1) | 6504 | 0.79 (0.69) | 0.010 / 0.015 / 0.023 |
| fp32 R0 | 64 | 0.07 (0.06) | not usable |
| fp32 R1 | 334 | 0.15 (0.14) | 0.049 / 0.078 / 0.117 |
| fp32 R2 | 1175 | 0.31 (0.27) | 0.024 / 0.039 / 0.058 |
| fp32 R3 | 3248 | 0.56 (0.49) | 0.014 / 0.022 / 0.033 |

Worked plan, bf16, rung R2, n_B = 2509: S0 to S3 7.75 + S4 1.94 + S5 22.78 + S6 3.06 + N5(b) 0.45 = 36.0 GPU-hours; reserve 4.
fp32, rung R3, n_B = 3248: 8.80 + 1.64 + 22.35 + 2.53 + 0.68 = 36.0. The sizing is by the pilot, not by these examples.

### 12.6 What is dropped, in this order, if the ladder forces it

1. S7 (S-U, S-N, k = 1 matched cells, new fixed-tau cells): run only from the reserve; the first thing cut. (The k = 1
   matched-entropy cells G_tot(1) are already out of the plan.)
2. A4 at k = 4, then A4 altogether (H3 is secondary): saves 4 to 10 percent of S5.
3. The second evaluator and MAUVE (secondary endpoint S4 of 8.2, exploratory) on part of the cells: cut to k = 16.
4. k = 2 (R0 to R1), then k = 4 (R1 to R2), then k = 8 (R2 to R3), in the ladder order of 9.6. H1b goes with the third k.
5. n_1 (the k = 1 block) below 256 down to the floor allowed by 6 GPU-hours, with the margin widening and demotion of N2 (10).
Never dropped: T-A3-1 to T-A3-4, N1, N3, P1 to P5, N5(a), N4, the primary contrast at the largest k, the firewall and the freeze.

## 13. LLaDA-8B-Instruct secondary (H5; exploratory, direction check)

Status at v0.2: the download is not finished and nothing has been loaded; no LLaDA timing, no quantisation test and no
accuracy exists (setup.md section 4). Everything below stays [A] until C3 of the setup is done. G4 (4.1) applies to this
stage too, and S8 needs S1 to have passed.

13.1 **Model and decoding.** LLaDA-8B-Instruct, 4-bit quantised (backend and bits from setup.md item 4; [A] NF4 with bf16
compute), chat template, no guidance, GSM8K, generation length 256, semi-autoregressive blocks of the released length (32
[A]); the competitor set of SF is the masked positions of the current block (N <= 32), k tokens per step, steps per block =
32/k. k in {4, 16} for arms A1 to A4; k = 1 only for N1/N2-type controls on a few problems. A5 (argmax at A4 positions) at
tau -> 0 is the reference practitioners use.
13.2 **Scoring convention.** Primary here follows the released code: the score is the untempered softmax probability of the
drawn token (condition S-U above), draws at tau, because that is what practitioners run. This differs from the MDLM primary
(tempered score); both are stated. The tempered score is a sensitivity run if budget allows. [A until setup.md item 4 is
checked against the released code.]
13.3 **Temperatures and endpoint.** tau in {0.5, 1.0} for A1 to A4 (two points are not enough for interpolation; the
matched-entropy read is exploratory only where the entropy ranges overlap, using the entropy of the generated answer tokens
and h*_LL = entropy of A2 at tau = 0.5, k = 4 on pilot problems). Endpoint: GSM8K final-answer exact match by a pinned
extraction script unit-tested on the gold solutions; unit = problem (mean over attempts); n_att attempts per problem per
cell. pass@k and HumanEval are not in this card (deferred to a later version; cost and code-execution safety).
13.4 **Power.** For a paired accuracy difference with per-problem SD s_d, two-sided 0.05 and 80 percent power,
MDE = (1.96 + 0.8416) s_d / sqrt(n_prob). With n_att = 1, s_d near 0.46 [A], n_prob = 200 gives MDE = 0.091 (9 points; 0.11
is the figure at 90 percent power); with n_att = 4 and E[p_i(1 - p_i)] near 0.1 [A], s_d near 0.22 and n_prob = 300 gives
about 0.04. The full test set (1319 problems, n_att = 4) would give about 0.02 but costs 70 to 280 GPU-hours and is not
planned. Consequence: the design cannot test H1 at 2 points and can detect only large effects (the total effect A1 versus A2,
or A5 versus A1). The result is reported as intervals; if an interval contains 0 and its half-width exceeds the stated MDE, H5
is "undecided at this n", not "no effect".
13.5 **Threats.** Quantisation noise perturbs the marginals and may change the size of every effect; the 4-bit model is not
the model of the LLaDA paper. Sanity gate: A5 accuracy on **100** train problems is within 10 points of the published figure
for the full-precision model, the figure and its page to be recorded by the lab-engineer [A] (standard error about 0.046 at
p = 0.7). The scoring convention of 13.2 differs from MDLM's. Semi-autoregressive blocks cap the competitor set at 32, so
coupling is strong (k = 16 of 32) but the regime differs from MDLM's N up to 1024.
13.6 **Compute.** H_LL = T_LL * n_prob * n_att * [ (w1' + w2' + w3') * |tau| + w4' * |tau| + w5' ] * Sum_{k in {4,16}} (256 / k),
with w' the overhead factors on a pass that is two to three orders slower than the sampler step (w' about 1.02 to 1.05 [A])
and T_LL = t_LL / 3600, t_LL the per-sequence-pass seconds at batch B from setup.md [A: 0.1 to 0.4 s; unmeasured]. Pass-equivalents
per attempt are about 9.2 * 80 = 736; for n_prob = 200, n_att = 1 that is 147k pass-equivalents, 4 to 16 GPU-hours.
13.7 **Stop.** LLaDA runs only after G4 and S1 pass; if the sanity gate of 13.5 fails, only the controls run.

## 14. What the review (Paper 1) states under each outcome

Statements are restricted to the checkpoint, precision branch, evaluator, sampling convention, k set and tau range tested.
Until this card is signed and run, the four-arm measurement stays an open problem with the evidence it needs (framework-v2 D4
item 4, and the check of 2605.12522 is done: it covers k = 1 only, 2605.12522 experiments file). The review credits 2605.12522
for the resample fix and the k = 1 comparison.

| Outcome (MDLM-OWT, 170M, plain sampling) | Paper 1 states |
|---|---|
| H1 positive beneficial, H1b positive | SF at k >= the smallest k that ran carries a measurable joint coupling that improves log GenPPL at matched entropy, growing with k (numbers with intervals); "SF equals a state-dependent tilt" holds in law at k = 1 only; sampler comparisons at k >= 2 cannot treat SF as a tilt |
| H1 positive beneficial, H1b not supported or not tested | A coupling effect is present at some k without a demonstrated dose pattern; reported as such; no growth claim |
| H1 positive harmful | SF's coupling hurts quality at matched entropy; practitioners' k >= 2 SF decoding pays a cost that a tilted or resampled sampler avoids at the same passes |
| H1 negative (practical zero) and G_sh 0 | At matched entropy SF is indistinguishable from plain sampling at another temperature on this model within the stated margin; reported entropy gains at unmatched temperature are the entropy loss |
| H1 negative and G_sh + | SF's per-position tilt helps beyond a global temperature; coupling is below the margin; a position-dependent tilt suffices on this model (G_sh rows exploratory: "consistent with") |
| H1 inconclusive | The decomposition is stated with its design, the achieved MDE and the intervals; the question remains open; no inference about SF |
| H2: Delta2 > 0 / < 0 | The sign of Delta2 and its size class, with the statement that the split is relative to the twin A3 (1.5); "coupling larger than sharpening" only with both classed + |
| H3 | The SF position law against max-probability ranking at k >= 2, at matched entropy, replicating or contradicting the k = 1 result of 2609.34509 |
| H4 (i) fails with N5(a) passing | Coupling changes diversity on this model; the entropy-deficit read of SF alone does not identify it |
| H5 | Direction on a second model with the stated MDE; no claim if undecided |
| Rung R2 or R3 ran | The k-range tested is stated (k in {8, 16} or k = 16); no statement about smaller k and no "k >= 2" wording; the toy's k = 2 is not tested |
| Any gate fails | The estimator is not established on a real network; the review keeps the proposal and the toy verification only and reports the failed gate |
| Underpowered (MDE > 0.03 at the cap) | The review reports the interval and the MDE, not a null |

In every case the review reports the cost of the measurement, the precision branch and the G4 verdict, that G_cp is a quality
contrast and not a KL or a budget term, that the split is twin-dependent and checkpoint-specific, and the claims that
survive with every confirmatory level halved (9.4). It does not state any size of V, E_fact, E_learn or E_sel.

## 15. Risks the red-team should attack first

1. A3 correctness at N = 1024 with binned scores; the claim "tilted twin" rests on the quadrature (T-A3-2, N5(a)); an error
   here appears as coupling. N2 at the capped n_1 detects only gross failures (10).
2. Entropy matching at one scalar (unigram entropy) can hide longer-range repetition differences; guards 8.3 catch only part
   of it.
3. Power: delta_cp = 0.03 is resolved only at rung R2 or R3 with the measured costs, and only if sigma_c is below 0.40 (bf16)
   or 0.27 / 0.49 (fp32); the ladder trades coverage over k for n, and the likely outcome leaves k = 2, 4 untested.
4. The split depends on A3 (1.5, red-team M1 analogue); a different twin gives a different split.
5. Visited-state shift: contrasts are kernel effects on outputs; common random numbers help only early in each trajectory.
6. GenPPL under GPT-2 Large is a weak proxy of quality and shares domain with OWT; EOS-crossing contexts (C10).
7. Stage A is an entropy-only calibration with a data-defined h*; if MDLM-OWT's entropy curve near h* is flat in tau, the cells
   will not be well placed (IR4 fallback, with beta_A noise now in the interval).
8. The tempered-score convention differs from the released LLaDA code; S-U is a descriptive condition only.
9. LLaDA quantisation and its large MDE; nothing about LLaDA has been measured.
10. Draw-level independence in A3 is across members within a step; across steps it is the sampler's own chain.
11. **Precision.** The shipped bf16 path and the fp32 path disagree on top-1 at 21.5 percent of masked positions with a
    0.32-nat entropy gap (setup.md 3.2); the card runs one of them (PG) and every contrast is internal to it. Whether the
    flash_attn shim is faithful is untested. G4 is open.
12. **Atoms.** bf16 logits create exactly tied token scores; the A3 recipe and its exact reference must treat atoms the same
    way (Prop. 4 tie term), or T-A3-2 can pass while kappa_hat is biased where ties are dense.
13. **Environment.** System commit exhaustion causes spurious OOMs and variable throughput; GPU-hours are wall-clock and the
    estimates carry that risk (reserve of 4).
14. **Sampler overhead.** s_3 = 40 ms is a deliberately high guess; if the measured A3 overhead is much larger, rungs move down.

## 16. Deliverables of the run

`runs/EXP-002/{constants,precision,s1,pilot,k1,stageA,stageB,eval,conditions,llada}/` each with config, seeds, git SHA of the
code, per-sample token files, per-step logs (N, k, committed scores, entropy of committed marginals, TC_A in A3 runs), hashes,
`manifest.json`, and a verdict file per stage; `runs/EXP-002/precision.json` (4.2); `analysis/EXP-002/` with `genppl.py`,
`interp.py` (IR1 to IR5), `bootstrap.py`, `placebo.py`, `freeze.py`, `budget.py` (prints the 12.4 and 12.5 tables from the
measured inputs), scripts that regenerate every table. Ledger rows (hypotheses H1 to H5; experiment EXP-002) are added only
after both signatures, by the orchestrator.

## 17. Deviations from the brief (read by the orchestrator)

- A3 is computed from the exact Prop. 4 closed form on a score grid (deterministic quadrature, error = discretisation,
  specified by eps_3 and the bins ladder), not estimated by replicate Monte Carlo with a stated M, because conditioning on a
  specific selected set is infeasible by Monte Carlo (5.3). Monte Carlo only enters the final categorical draw. An
  importance-sampling implementation is allowed if it passes the same tests (reports ESS in place of M).
- "Exact-independent toy marginals => the coupling contrast vanishes" is corrected: it vanishes only in the Prop. 4 equality
  cases (N3); peaked heterogeneous independent marginals are a positive control (P2).
- The brief's grid-wide interpolation is implemented as calibrate-then-measure: stage A locates tau for entropy h* +- 0.05
  (entropy only), stage B measures quality at two cells that straddle h*. Same estimand, about an order of magnitude fewer
  expensive cells.
- Sized for a small coupling effect (delta_cp = 0.03) per the orchestrator's toy prior, with a pre-stated ladder rather than an
  assumed n; with measured costs the ladder will in practice drop k = 2 and k = 4.
- LLaDA is a direction check with a stated large MDE; HumanEval and pass@k are deferred.
- h* is data-defined (the held-out OWT unigram entropy), not the output entropy of any arm.
- v0.2: the cap on the MDLM part is 40 GPU-hours (v0.1 proposed 60 for the programme); N2's n_1 is bounded by a 6-GPU-hour
  budget, not by 1024; stage A is reduced for A3 (change-log items 7, 26, 27).

## 18. Sign-off

| Role | Check | Status |
|---|---|---|
| statistician | v0.2 change log items 1 to 22 applied as required; re-look at items 7, 8, 13, 18, 27, 28, 30, 31 (sections 7.2, 7.4 IR8, 9.5, 9.6, 10 N2 and N5, 11.2) | unsigned |
| red-team | sections 1.4, 5.3, 10, 15: A3 correctness, controls, confounds, twin-dependence, precision and atoms | unsigned |
| lab-engineer | section 3 open items filled, S0 and S1 pass, overhead s_a and t_G measured, batch-8 fp32 timing if P-fp32 | pending |
| repro-engineer / orchestrator | gate G4 (4.1) and the precision branch (4.2) | open (report not yet written) |
| novelty-auditor | recheck of concurrent work before freezing (1.3) | pending |
| gate-auditor | stage verdicts against this card | pending |

## 19. Change log

The v0.1 to v0.2 table is at the top of this file.

- v0.1 (2026-10-14): first draft by experiment-designer; nothing frozen. Preserved at commit f719a61.
- v0.2 (2026-10-14): statistician review applied (R1 to R12, O1 to O3, O5 to O11), measured MDLM timings and precision facts
  (setup.md, timing.json), gates G4 and PG, budget recomputed under a 40 GPU-hour cap, ladder costed per precision branch;
  draft, unsigned. Pre-freeze amendments allowed (do not need a new version): filling the open items of section 3, the
  pilot-derived n_B, n_1 and ladder rung (9.6, 10), package pins, the tau grid if stage A shows h* unreachable (11.1 item 3),
  the MaskGIT noise schedule (section 3 item 10), the planning costs of 12.2 replaced by measurements. Any other change after
  signing creates a new version with a dated entry here.
