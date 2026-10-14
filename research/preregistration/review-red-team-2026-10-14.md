```yaml
agent: red-team
date: 2026-10-14
brief: Pre-compute attack on EXP-001 v0.2 (cross-modal dependence in UniDisc) and EXP-002 v0.2 (value-rule decomposition of sample-then-filter on MDLM-OWT); problems only, ranked, each with failure scenario and minimal fix; verdict per card.
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-001-crossmodal-unidisc.md (v0.2, lines 1-515, in full)
  - research/preregistration/EXP-002-value-rule-decomposition.md (v0.2, lines 1-1091, in full)
  - research/preregistration/review-statistician-2026-10-14.md (headers; S7 of both cards; R7; closing note)
  - research/preregistration/review-statistician-2026-10-14-round2.md (in full; read after the restart, to avoid duplicating E1-E7, M1-M6)
  - research/review/framework-v2.md (A-E, in full)
  - research/review/audits/2026-10-14-red-team-selection-term.md (F1, F2, M10)
  - research/review/dossier/prior-art-2605.12522-experiments.md (in full)
  - research/review/dossier/prior-art-selection.md (grep for 2609.34509, Hayakawa; lines 281-298)
  - analysis/framework/check_coupling_k2.py and .log; check_crossmodal_mixture.py and .log
  - runs/env-2026-10-14/setup.md (sections 0-3.5)
  - runs/G4-mdlm-repro-2026-10-14/logs/t1a_shim_unit_v1.out, t1a_shim_unit_v2.out; git diff of runs/env-2026-10-14/scripts/shims/flash_attn/layers/rotary.py (shim v1 -> v2)
  - analysis/framework/redteam_exp_002_coupling_bins.py/.log, redteam_exp_002_toy_direction.py/.log, redteam_exp_001_floor_lift.py/.log (written for this review; CPU only, no GPU)
coverage: >
  Both cards read in full. Not read: UniDisc, MDLM, LLaDA or 2605.12522 code; Hayakawa 2510.04525 itself (only the
  dossier's summary of it); timing.json; the statistician's scripts. LLaDA (EXP-002 section 13) attacked only for scope.
  No GPU was used. The three scripts are synthetic or toy computations about the estimators, the endpoint and the regime;
  none is a measurement on UniDisc or MDLM. Statistical points that the round-2 review already settled (NC-6' rule, G5
  statistic, R_Q 0/0, H-A1 power at realistic cv, P_rand fork, P(H1 negative), N2 OC, N5(b), H4 reading, n_B pinning,
  claim scope by rung) are not repeated.
claims:
  - statement: "Under the exact Prop. 4 law, SF's within-set value coupling (pairwise MI of two members given A) is below 1e-11 nats at N = 1024 for k = 2, 8, 16 in every synthetic regime tried, and of order 1e-3 to 4e-2 only when N/k <= 8 (diffuse or identical rows)."
    status: supported
    evidence: analysis/framework/redteam_exp_002_coupling_bins.log, Q1 and Q1b
    level: E4 (synthetic rows, V = 256)
    confidence: 0.75
  - statement: "In the card's own toy prior, the coupling contrast in the GenPPL direction (reverse KL with a perfect evaluator) at matched entropy is +0.0054 nats per 4-token sequence (positive 10/12), about 0.0014 nats per token; the forward-KL figure the card quotes is +0.016 per sequence."
    status: supported
    evidence: analysis/framework/redteam_exp_002_toy_direction.log, summary lines
    level: E4 (toy)
    confidence: 0.9
  - statement: "The card's 2048-log-bin A3 recipe is within mean TV 6e-4 of the exact-score law in the synthetic regimes tried; the bins ladder agrees (8e-4). The top-bin lumping of [0.98660, 1) did not produce a measurable error there."
    status: supported
    evidence: redteam_exp_002_coupling_bins.log, Q2 and Q2b
    level: E4 (synthetic)
    confidence: 0.6
  - statement: "A pure bf16 floor (no dependence) in the mixture estimator rises with marginal entropy: 1.7e-5 nats per position at H 2.5 against 7.8e-5 at H 9.6 (s = 0.005), 1.35e-4 against 3.2e-4 (s = 0.02)."
    status: supported
    evidence: analysis/framework/redteam_exp_001_floor_lift.log, Part 1
    level: E4 (synthetic, perturbation model assumed)
    confidence: 0.7
  - statement: "At fixed pair consistency, a rise in content diversity raises the matched-minus-shuffled lift by about 1 point (the MEI) while the mean pairwise image cosine moves by less than the 0.05 that guardrail (ii) allows; an arm with lower consistency (0.55 vs 0.60) can show a higher lift (+0.94 to +1.71)."
    status: supported
    evidence: redteam_exp_001_floor_lift.log, Part 2
    level: E4 (synthetic embeddings, not CLIP)
    confidence: 0.7
competing_explanations: []
unknowns:
  - whether unconditional UniDisc captions (empty prompt) are descriptive at all (one smoke sample under a strong prompt read as debris)
  - real MDLM states in the last 8 steps of a k = 8 or 16 trajectory (diffuse or confident), which decides whether any coupling exists
  - Hayakawa 2510.04525 Sec 5 language experiment and App D-E, not read by anyone
  - whether UniDisc runs through the patched flash_attn rotary shim (v1 had extra bf16 roundings) or its own RoPE
next_test: {hypothesis: "SF's kernel-level coupling on real MDLM states is too small to move log GenPPL by 0.03", intervention: "S1 of EXP-002 only, with TC_A computed at states from the final 8 steps as well as the six fractions", primary_metric: "trajectory-summed TC_A per sequence at k = 8 and 16", falsifier: "summed TC_A per token above about 0.01 nats", gpu_hours: "about 0.8 (S1 as costed in the card), not run here"}
```

# Red-team review of EXP-001 v0.2 and EXP-002 v0.2 (pre-compute)

Tags: [S] source fact with location; [I] inference; [C] computed here (script and log named; CPU only); [A] assumption.
Nothing in either card has run. Every number below from my scripts is a synthetic or toy result about an estimator, an
endpoint or a regime, not a measurement on UniDisc or MDLM.

Note on the brief: my standing rule is "problems only, no fixes". The orchestrator's brief asks for a minimal fix per
finding, so each finding ends with one. Each fix is the smallest condition that would close the problem, not a redesign.

Scope relative to the statistician: round 2 (review-statistician-2026-10-14-round2.md) settles the decision rules
(E1-E7, M1-M6). I do not repeat those. My findings are about whether the endpoints measure what the claims say, which
confounds the controls leave open, and implementation risks. Where a finding touches a round-2 item, it says so.

Severity: **fatal** = the claim as worded cannot be supported by the design even if everything runs correctly; blocks the
gate until a resolution is recorded in the decision ledger. **major** = a positive or negative result would be open to a
cheaper explanation the card does not control, or a procedure cannot run as written. **minor** = wording, reporting or
robustness.

---

# EXP-001 v0.2 (UniDisc 1.4B, S_theta trace and commit schedules)

Counts: **fatal 1, major 8, minor 5.**

## Fatal

**X1-F1. The primary endpoint's construct, text-image consistency of a caption with its image, is never established for
the "captions" this setup produces, and no gate can detect that it fails.** Location: 4 (G0, PG-2), 6 (dynamic-range
gate), 7.1, 14 risk 1.
- Source facts. The only free 32-token tail observed so far, under a strong observed prompt, read "(c) photoshiko shui
  copyright (c) 1 2 3 / 02 a / 12 3 / 15 a" (setup.md 2.1 (a), "web-caption debris"). An earlier layout with the masked
  tokens in an assistant turn was filled with `<unk>` (setup.md 2.6). G0 has an empty user prompt, so nothing pushes the
  tail toward a description.
- Failure scenario. PG-2 passes on at least 4 non-special tokens, and debris passes that. The dynamic-range gate needs
  only Lift(J) >= 2 points. CLIP ViT-L/14 was trained on web alt-text, so it links "copyright", "stock photo", dates
  and watermark strings to images with overlaid text, borders or stock-photo style. Lift(J) can clear 2 points on those
  associations alone. A positive DA - J then means the schedule changes how often debris co-occurs with a matching image
  style. Paper 1 would report this as "higher text-image consistency". None of the guardrails (length, diversity, empty
  rate, truncation, CLIP-IQA, KID) looks at caption semantics. The VQA secondary scores 250 seeds with no decision role.
- Cheapest alternative explanation for any positive H-B1: the schedule changes OCR, watermark or style coupling, not
  object-level consistency.
- What forces rejection of the claim: on D0, fewer than about half of J's captions name an object (NOUN or PROPN) that a
  pinned image tagger or a blinded rater finds in the image.
- Minimal fix: a pre-D1 caption-validity gate on the D0 J samples, logged together with the other gate outcomes (round 2
  E5c). Use the share of captions with at least one NOUN or PROPN confirmed present in the image, by a pinned
  tagger/VQA or by a blinded rating of 32 pairs, with a threshold fixed now. If the gate fails, the "a photo of" prefix
  fork (PG-2) is applied. If it still fails, H-B is "untestable on unconditional captions". Report the primary
  restricted to descriptive captions as a sensitivity.

## Major

**X1-M1. A positive DA - J can come entirely from the shuffled baseline (diversity), and guardrail (ii) is too loose to
catch it.** Location: 7.1, 7.2 guardrail (ii).
- [C] `redteam_exp_001_floor_lift.log` Part 2 (synthetic embeddings): at fixed pair consistency a = 0.60, raising
  content diversity raises Lift by +0.88 and +1.58 points while the mean pairwise image cosine falls by 0.012 and 0.025.
  An arm with *lower* consistency (a = 0.55) beats the a = 0.60 baseline by +0.94 to +1.71 points, with image-cosine
  changes of 0.025-0.040, all inside the 0.05 that guardrail (ii) allows. [I] In this model Lift is roughly "1 minus
  the mean cross-pair topic similarity", so a 0.05 shift in image diversity buys several MEIs. Real CLIP has a modality
  gap, so the slope is smaller but unknown [A]. Guardrail (ii) does not look at caption diversity, which enters the
  baseline symmetrically.
- Failure: the image-density or text-density change in pure windows diversifies content. DA - J reaches ">= 1.0, positive"
  with flat or lower matched cosine C.
- Minimal fix: register the decomposition DA - J = (mean C difference) - (mean B difference), with an interval for each.
  Label a positive H-B1 "baseline-driven" (not support) when the C-difference interval contains 0 or is negative. Bound
  guardrail (ii) and a caption-side analogue at a fraction of the MEI on the lift scale, not at 0.05 cosine.

**X1-M2. The committed-set S_theta trace is a trace of the confidence position rule and of padding as much as of
dependence, while the claim (1.1) is general.** Location: 1.1, 2 H-A1, 8.1, 8.6; round-2 e4 asks only for reporting.
- At k0 the committed text set is the single most confident masked text position. Under an empty prompt with a
  fixed 32-token tail, the most confident positions early are plausibly pad/EOS (setup 2.6 shows the model fills tails
  with `<unk>`). Late in the trajectory, the remaining text positions are the least confident content words. On the
  image side, the most confident positions early are plausibly uniform background codes. So both committed-set
  statistics depend on which token types the rule picks at each pass. The trace can be front-loaded, flat or back-loaded
  for reasons unrelated to where dependence sits in the model. Condition R (random positions) is the only check; it has
  64 trajectories and no decision role in H-A.
- Failure: H-A1 is supported (or reversed) and Paper 1 says "the model's cross-modal dependence is front-loaded". The
  shape actually comes from the ordering of pad, function, background and content tokens under confidence ranking.
- Minimal fix: word every H-A claim "under within-modality confidence ranking". Exclude post-caption (pad/EOS) committed
  text positions from the H-A1 I->T and T->I sums, and report the excluded share per probe (this turns round-2 e4 into
  a rule). Give the condition-R trace a registered agreement check with H-A1 (same direction of the early/late ratio)
  before any position-free wording is used.

**X1-M3. The entropy normalisation R_Q covers only the receiving side.** Location: 2 H-A1-Q, 8.5; round-2 E3 fixes the 0/0
problem, not this.
- I(a; b_j | s) <= min(H(a | s), H(b_j | s)). R_Q divides by sum H(mbar_j) of the receiving positions only. For T->I at
  k0 the source is one text token. If that token is near-deterministic at late probes (content already fixed by the
  image) or at early probes (pad), the ratio moves with the *source* entropy profile. The wording rule "front-loaded
  beyond the entropy available" then claims more than R_Q tests.
- Minimal fix: compute R_Q with denominator sum_j min(H(a), H(mbar_j)) (H(a) = entropy of the drawn committed set's law,
  already available from the R draws), or add it as a second companion. Use the "beyond the entropy available" wording
  only if both pass.

**X1-M4. The bf16 noise floor rises with marginal entropy, so a trace near the floor is front-loaded by construction; G1b
compares one median floor with an ambiguous target.** Location: 8.7 G1b, 6.
- [C] `redteam_exp_001_floor_lift.log` Part 1 (synthetic; per-requery perturbation s calibrated to TV 0.002-0.013,
  bracketing setup.md 2.1's 0.0055-0.0164): pure-floor I_hat per position is 1.67e-5 at H 2.46 and 7.75e-5 at H 9.58
  (ratio 4.6) for s = 0.005, and 1.35e-4 against 3.16e-4 (ratio 2.3) for s = 0.02. Early probes have higher image
  entropy than late ones (setup 2.1 (b): mean image entropy 6.5 nats at 25 percent revealed). A floor-dominated S
  therefore yields an early/late ratio above 1.5 with zero dependence. The mixture estimator removes an *a-independent*
  shift. It cannot remove input-dependent rounding, which differs per revealed value. G1b needs "median floor below 5
  percent of the smallest S_theta value used in any comparison". If that means per-trajectory values, some are near 0
  and the gate always fails. If it means probe means, it ignores that the floor is entropy-dependent.
- Minimal fix: measure G1b at the early and the late probes separately, on the same trajectories. Require each probe's
  mean S to be at least 20 times that probe's own floor. Define "smallest S value" as a probe-level mean.

**X1-M5. No control separates content dependence from non-semantic, value-dependent responses (length, termination).**
Location: 8.7 G2/G3, 8.8 NC-1, PC-D.
- G3 injects an a-independent shift. NC-1 removes cross-attention altogether. PC-D shows that a matched caption moves
  step-1 marginals. None of them tests the case M10 warned about: a value-dependent but non-semantic response. The
  prime candidate is pad/EOS against a word at a text position. That value tells the model the caption length, which can
  shift image marginals (for example toward watermark or border codes) without any object-level dependence. Early
  probes draw the text token from its widest law, so this term is plausibly largest early.
- Failure: H-A1 T->I passes on "caption length or termination" information. H-A2 (nouns) would not catch it, because
  it is an I->T statistic.
- Minimal fix: decompose the T->I estimate by the chain rule, I(a; b_j) = I(1[a is pad/EOS]; b_j) + I(a; b_j | 1[pad]),
  from the stored R draws, and decide H-A1 T->I on the second term (report both).

**X1-M6. DA-low is not a dependence-blind control, and H-C cannot separate S_theta from time.** Location: 5.1 (DA,
DA-low), 8.8 NC-7 ("dependence-blind control"), 2 H-C, 10.3. Round 2 accepted H-C on error rates; this is about what
it measures.
- If H-A holds, DA is the early windows and DA-low the late ones, so H-B1' compares early with late separation. Many
  things change with time: the value of revealing text early, the within-modality TC of the 42-43-token image passes
  and of the 4-token text pass, marginal entropy. H-C correlates M_w with Delta_w over 8 windows within k. Any effect
  that is monotone in window index gives rho near 1 when S_theta is also monotone. "S_theta predicts where separation
  helps" then reduces to "early windows matter more".
- Failure: H-B1' positive and H-C supported, reported as validation of the measured trace. A time-only predictor (window
  index, or mean marginal entropy per window from D1) does equally well.
- Minimal fix: relabel NC-7 "late-placement control". Require H-C to beat a time-only predictor: partial Spearman of
  (M_w, Delta_w) given window index, or a registered comparison against D1's per-window mean marginal entropy. If it
  does not, use the wording "consistent with S_theta, not distinguishable from time".

**X1-M7. Pure windows change two things at once: co-commitment, and how early text becomes visible. The arms isolate
neither.** Location: 1.2, 5.1 (pure window, Jd), 13.
- In a pure window all 4 text tokens are committed at pass 1, so the window's 128 image tokens see 4 more text tokens,
  0-3 passes earlier than in a joint window. A gain can come from text-earlier (more conditioning) without any role for
  the co-commitment cost (the factorisation error the mechanism names). Jd changes image density and pass count. Alt and
  DA-low share the confound. TF is off-support. No arm advances text while keeping co-commitment.
- Cheapest alternative explanation for a positive DA - J: "reveal text earlier within the window".
- Minimal fix: one pass-matched diagnostic arm at k0 on the DA windows: "text-front joint", with all 4 text tokens
  co-committed with 32 image tokens at pass 1 and 32 image tokens at each of passes 2-4. If it is not added, word the
  mechanism "committing text before image within a window", not "not co-committing dependent pairs".

**X1-M8. The resolution gate PG-1 is run in a condition that hides the failure it guards against.** Location: 4 PG-1, 14
risk 1. Round 2 gave PG-1's statistical OC (e2), not this.
- PG-1 compares 512 px with 1,024 px on guided T2I (CFG 3.0, official sampler, Gumbel ranking noise). The experiment runs
  unguided, noise-free, confidence-ranked, unconditional joint generation. CFG lifts CLIP alignment even when images are
  degraded. The setup facts show only that RoPE tables exist for 512 px (setup.md 2.2), not that the interleaved
  checkpoint was trained there. Deterministic confidence ranking on 1,024 image tokens risks collapsed images (card 0,
  5 of change-log B).
- Failure: PG-1 passes, the condition-P images at 512 px are degenerate in every arm, Lift(J) still clears 2 points on
  text debris (X1-F1), and the arm contrasts are contrasts between degenerate samplers.
- Minimal fix: add a condition-P leg to PG-1: J at k0, unguided, 512 px, with a registered degeneracy screen (CLIP-IQA or
  KID against COCO, set against the same plan at 1,024 px on 16 seeds) before D0.

## Minor

**X1-m1. Selector and intervention do not match.** DA and H-C pick windows by S_sym = (S^{T->I} + S^{I->T})/2. A
text-first pure window removes only the T->I co-commitment price. The window's text is committed before that window's
images and so still does not see them, exactly as in a joint pass. Half of the predictor is unrelated to the
intervention. Fix: select DA windows and define M_w by S^{T->I} (the image-first variant would be the I->T counterpart),
or state why S_sym is used.

**X1-m2. The all-masked-position version is front-loaded by count.** Summed over still-masked positions, it grows with
the number masked (about 1,000 early against about 100 late). Fix: report it only as a per-position mean. A summed
version must never appear as evidence of front-loading.

**X1-m3. Precision facts and the shim.** The bf16-versus-fp32 figures (setup 2.1) predate the rotary-shim correction (v1
had extra bf16 roundings; 31 percent of elements differed by one or two bf16 steps,
`runs/G4-mdlm-repro-2026-10-14/logs/t1a_shim_unit_v1.out`). Whether UniDisc uses that shim or its own 2D RoPE is not
stated. Fix: record the shim version (or "not used") in the run manifest and re-measure G1b under it.

**X1-m4. Novelty of H-B is unaudited** (1.3: dependence-aware parallel unmasking in single-modality DLMs "not audited").
The card already limits the claim to the measurement. The novelty-auditor check must come before the card is frozen,
because the comparison class decides what H-B1 adds.

**X1-m5. Licence.** With no licence on code or weights, a hostile reviewer can ask for released generations and
reproduction artefacts. The card states the limit (3 item 6). Paper 1 must say what is withheld and why.

## Checked and not a finding (EXP-001)
- Matched forward passes: J, Alt, DA, DA-low, Sep_w, TF and IF all have N passes. Probe passes run on state copies and
  are not charged to arms. Jd and O are labelled unmatched (exploratory per round-2 E7a).
- Common random numbers: one float64 uniform per position used at its commit pass. Probes use a separate stream. G6
  checks probe invariance. No validity problem. I2 (bitwise identity) may fail from kernel nondeterminism; G6 already
  sets a rate rule, and I2 should borrow it.
- Toy use: the toy (block J) validates the estimator only. It does not set any H-A or H-B threshold. The MEI is taken
  from UniDisc's reported CFG-window differences, not from the toy.
- D1/D2/D3 seed pools are disjoint. DA's windows come from D1 only.

## What Paper 1 can and cannot say (EXP-001), given the findings
- H-B1 positive with X1-F1, M1 and M7 unresolved: "a schedule changes the CLIP lift of jointly generated pairs on this
  checkpoint". It cannot say "improves text-image consistency" or "by avoiding co-commitment of dependent pairs".
- H-A1 positive with M2, M4 and M5 unresolved: "the committed-set trace under confidence ranking is larger early". It
  cannot say "the model's cross-modal dependence is front-loaded", or anything semantic.
- H-C supported with M6 unresolved: "S_theta and the per-window gain are both larger early". It cannot say "S_theta
  predicts where separation helps".
- A null H-B at matched passes stays a valid statement about this checkpoint, value rule, 512 px and metric. A null is
  the outcome least exposed to these findings, provided X1-F1 is resolved (a null on debris captions is uninformative).

## Verdict EXP-001: **sign after listed fixes**
X1-F1 must be resolved (caption-validity gate) and recorded in the decision ledger before D0. X1-M1 to M8 must be fixed
in the v0.3 card or carried as explicit wording limits in section 13.

---

# EXP-002 v0.2 (MDLM-OWT, SF decomposition with resampled and tilted twins)

Counts: **fatal 0, major 7, minor 6.**

## Major

**X2-M1. The premise "the coupling part is non-zero and grows with k" is predicted near zero, in law, for all but the
last few steps. The toy prior that sized the design is its most favourable regime, and the card spends about 30
GPU-hours before reading the state-level quantity that can settle it.** Location: 1.1, 2 H1 and H1b, 9.6 (delta_cp
rationale), 12 (S1 placement), 15 risk 3.
- [C] `redteam_exp_002_coupling_bins.log` Q1 (exact Prop. 4 law, synthetic rows, V = 256): the pairwise MI between two
  members of the selected set at N = 1024 is <= 1e-11 nats for k = 2, 8 and 16 in every regime (diffuse, identical rows
  as at the all-mask state, mid, late). At N/k = 32 (k = 8, N = 256; k = 16, N = 512) it is 3e-6 to 4e-3. It reaches
  2e-3 to 3.6e-2 per pair only at N/k <= 8 in diffuse or identical-row regimes (Q1b), and 4e-5 to 1e-2 in the "mid"
  regime at N/k 2-8. The mechanism: with many competitors the selection threshold concentrates, members are truncated
  at an almost fixed level, and their value laws collapse toward the argmax. Mean H(kappa_i | A) is 0.0-0.3 nats
  against H(P_i) of 3.7-4.5 at N/k = 32. That is heavy sharpening and almost no coupling.
- [I] With N_n = L - nk, steps with N/k <= 8 are the last 8 of each trajectory: 64 of 1,024 tokens at k = 8 and 128 at
  k = 16 (6 and 12.5 percent). G_cp can only be produced there. The share of affected tokens is 8k/L, so it grows
  linearly in k by bookkeeping, which matters for any growth claim (X2-m3).
- [C] `redteam_exp_002_toy_direction.log`: the toy prior (L = 4, so N/k <= 2 at every step, the most favourable regime)
  gives G_cp in the card's GenPPL direction (reverse KL with a perfect evaluator, at matched entropy) of +0.0054 nats
  per 4-token sequence (positive in 10/12), about 0.0014 per token. The card sizes delta_cp = 0.03 per token "per the
  orchestrator's toy prior" (17), which is about 20 times the toy's per-token effect. The sign transfers (10/12); the
  size does not.
- Failure: the likely outcome is "practically 0 at k = 16" or "H1 negative". The design is valid for that. But Paper 1 and
  the statistician's scope note ("Prop. 4 and the kernel readout predict coupling (TC_A) to increase with k",
  round-2) present the question as open, when the card's own Prop. 4 predicts the answer. A hostile reviewer asks why
  about 36 GPU-hours went to an effect that a CPU computation bounds. Also, the S1 states (fractions 0 to 0.9 of the
  steps) miss the final steps where any coupling lives: at k = 16, fraction 0.9 is N of about 100 (N/k about 6). The
  mechanism readout and F-mechanism ("TC_A < 1e-3 at all k") therefore look in the wrong place.
- What forces rejection of the premise: trajectory-summed TC_A on real MDLM states, including the final 8 steps, below
  about 0.01 nats per token at k = 16.
- Minimal fix: (1) add the final 8 steps (N in {k, 2k, ..., 8k}) to the S1 state set and to T-A3-2; (2) make S1's
  trajectory-summed TC_A per token a registered go/no-go before S2. If it cannot plausibly produce |G_cp| >= delta_cp,
  report H1 as "bounded at the kernel level" and run S2 onward only as a confirmation at reduced n, or not at all
  (orchestrator's call, logged); (3) delete "per the toy prior" as a sizing rationale, or restate it per token.

**X2-M2. The A3 acceptance tolerance is loose enough to manufacture a G_cp of the size of delta_cp, and no gate checks
the signed bias that matters.** Location: 5.3 (error specification, T-A3-2, N5(a)), 10 (N2), 15 risks 1 and 12.
- [C] On the synthetic states the recipe is accurate (mean TV 6e-4 or less against the exact-score law; bins ladder
  8e-4; Q2/Q2b). So the top-bin lumping of [0.98660, 1) that I suspected is not supported there. The problem is the
  specification, not the recipe: mean eps_3 <= 0.005 TV per committed position. [I] A per-position TV error of epsilon
  that moves mass from a row's dominant token toward alternatives Delta nats less probable shifts the committed tokens'
  log-probability by about epsilon x Delta. At epsilon = 0.005 and Delta of 3-5 nats that is 0.015-0.025 nats per token,
  on *every* committed token. The true coupling acts on 6-12 percent of tokens (X2-M1). TV is unsigned, so a test can
  pass while the bias is systematic. N2 runs at k = 1, where the recipe's k >= 2 part is trivial (round-2 M2), and has
  margins of 0.081. N5(a) checks convergence, not bias.
- Failure: A3 commits slightly flatter (or sharper) per-position laws than SF's true conditional laws. Entropy matching
  only partly absorbs this, because it acts through one scalar. G_cp is then "supported" at 0.01-0.03 and attributed to
  coupling. F-mechanism would raise C1 only if TC_A on the (wrong) S1 states is below 1e-3.
- Minimal fix: in T-A3-2, report and bound the signed first-moment error per committed position,
  sum_v (kappa_hat_i(v) - kappa_i(v)) log P_i(v), with a mean bound of delta_cp/10 = 0.003 nats. Tighten mean eps_3 to a
  value consistent with it (about 5e-4, which the recipe met in my synthetic runs). Include final-step states (X2-M1).

**X2-M3. The repetition guard allows a repetition-driven G_cp of about twice delta_cp.** Location: 8.3, 1.4 C3, 11.2.
- [I] Under GPT-2 in-context copying a repeated 4-gram costs almost nothing. If 2 percent more positions sit in repeated
  4-grams (the guard's 0.02 absolute), mean NLL falls by about 0.02 x (mean NLL of non-repeated tokens, about 3-4 nats)
  = 0.06-0.08 nats per token, against delta_cp = 0.03. Unigram entropy can stay matched while phrases repeat. Within a
  step, SF couples the score levels of co-committed tokens, and late committed sets fill in repeated subword patterns,
  so A1 and A3 can differ exactly here.
- Minimal fix: a registered sensitivity that recomputes Y with the NLL averaged over positions *outside* repeated 4-grams.
  A G_cp that changes sign or drops below half its size there carries "repetition-driven". Alternatively, set the guard
  at the repetition difference whose implied Delta Y is delta_cp/3 (about 0.003 absolute).

**X2-M4. The pilot needs the evaluator before stage B, but 9.7 says the pilot is evaluated only in the single final run.**
Location: 9.6 (pilot prints SD of Y_s; sigma_c needs Y), 9.7, 12.3 S2 ("evaluation of 288 pilot sequences"). Round 2 did
not raise this; round 1 R7 resolved the same conflict for N2 only.
- Failure: either the ladder and n_B cannot be computed as written, or the pilot is evaluated early in breach of 9.7.
  The pilot cells include A1, A2 and A3 at the same tau and indices, so per-sample Y held in memory or on disk is
  enough to compute every pilot contrast mean (a peek channel).
- Minimal fix: write an explicit carve-out. The hashed pilot script runs GPT-2 on pilot files before stage A, keeps
  per-sample Y_s only in memory, writes only the 9.6 quantities, and the pilot files enter no later estimate. Remove
  "pilot" from the 9.7 single-run list.

**X2-M5. The novelty against k >= 2 prior work is narrower than 1.3 states: Hayakawa 2510.04525 already compares
MaskGIT SF at k >= 2 with a product-tilt choose-then-sample sampler, including on an OWT-trained text model.** Location:
1.3, 17; 18 (novelty-auditor pending).
- [S] prior-art-selection.md lines 284-289: Hayakawa's "moment sampler" draws positions by a state-only rule and values
  from p^(1+1/tau), a product tilt; it is compared with MaskGIT SF at steps 8-64 (images) and 8-256 on SDTT small (a
  language model on OWT). Their Sec 5 and App D-E were not read by anyone (dossier unknowns).
- The card lists Hayakawa only for condition S-N. Against 2605.12522 (k = 1 only, E3) and 2609.34509 (one token per step,
  E2) the k in {8, 16} novelty holds. Against Hayakawa, a reviewer will say that a product-tilt twin of SF at k >= 2 on
  OWT is published. The real distinctions are: noiseless SF, an exact per-set twin (A3) against an asymptotic moment
  approximation, the matched-entropy read, intervals, and the coupling/sharpening split. These are real but narrower.
- Minimal fix: before freezing, a full read of Hayakawa Sec 5 and App D-E (novelty-auditor). Add Hayakawa to 1.3 as the
  closest k >= 2 prior with the distinctions above, and drop any wording that the tilted twin "has no counterpart".

**X2-M6. G_sh is not a clean "per-position sharpening beyond a global temperature" contrast, because the matched-entropy
read puts A2 and A3 at very different temperatures.** Location: 1.2, 2 H2 table, 1.4 C2.
- [C] Toy (`redteam_exp_002_toy_direction.log`): matched-entropy tau* is 0.45-0.63 for A2 and 0.82-1.60 for A1/A3. On
  MDLM, A2 at low tau sharpens every position, including late, already-confident ones, while A3 sharpens only the
  selected set. Unigram entropy is one scalar, and the two arms reach it through different per-position entropy
  profiles over the trajectory. G_sh then mixes "state-dependent versus global" with "which steps carry the entropy
  loss". The H2 row "the gain is state-dependent per-position sharpening beyond a global temperature" claims the first.
  The toy also does predict G_sh at matched entropy in the GenPPL direction: -0.58 per sequence, negative in 12/12
  (global temperature better). The card says the toy "gives no prediction" (2, H2).
- Minimal fix: word G_sh "SF's selected-set sharpening versus a global temperature at matched unigram entropy". Report
  the per-step entropy of committed values by arm (S6 already logs it) next to G_sh. State the toy direction as a prior,
  not a test.

**X2-M7. The evaluator check is weakest where the decision is made.** Location: 8.3 (second evaluator on k in {4, 16}
intersected with K_R, sign only), 3 item 5 (second evaluator open), 1.4 C9.
- At rung R2 only k = 16 gets a second evaluator, and at R3 only one cell. GPT-2 Large and MDLM-OWT share WebText-style
  training (round 1 S7). A "disagree" rule on point-estimate signs passes any effect a second evaluator cannot resolve,
  so "same sign" is a coin flip when the true effect is near 0. A supported G_cp at 0.01-0.03 then rests on one
  evaluator in practice.
- Minimal fix: pin the second evaluator before freezing. Run it on every stage-B cell of the rung (cost: S6 scales by
  about 2, under 1.5 GPU-hours at R2). Count a supported G_cp only if the second evaluator's 95 percent interval
  excludes the opposite sign at delta_cp/2.

## Minor

**X2-m1. Stale precision premise.** The card cites bf16-versus-fp32 top-1 agreement 0.785 and an entropy gap of 0.32 nats
(3, 4.1, 15 risk 11). These were measured with rotary shim v1, which did the rotation in bf16 with two extra roundings
(31 percent of elements one or two bf16 steps off, `t1a_shim_unit_v1.out`), replaced by v2 in G4
(`git diff runs/env-2026-10-14/scripts/shims/flash_attn/layers/rotary.py`). The PG branch, and so the rung, may rest
on a shim artefact. Fix: PG reads only a G4 measurement made under shim v2, and `precision.json` records the shim
version and hash.

**X2-m2. How TC_A is computed is not specified.** The joint entropy of kappa(. | A) over V^k (V = 50,257, k = 16) is not
directly computable. It needs the 1-D form H = -E[sum log P_i] - E[log W_A(m)] + log rho(A) on the score grid. Fix:
state the formula and add it to T-A3-1's oracle check.

**X2-m3. H1b would measure bookkeeping.** By X2-M1 the share of tokens committed at small N/k is about 8k/L, so a positive
slope of G_cp on log2 k can arise even if per-step coupling does not grow. Fix: if H1b ever runs (R0 or R1), report
G_cp per affected token (divide by the share of tokens committed at N/k <= 8) next to the slope.

**X2-m4. EOS-reset sensitivity covers A1 and A3 only.** G_sh and Delta2 involve A2, whose EOS rate at low tau may
differ the most. Fix: extend S10 to A2.

**X2-m5. Second-evaluator "disagree" is defined, but the evaluator is not chosen** (3 item 5 open). A pre-freeze
amendment is allowed. Name the model family before signing, because the choice decides C9's strength.

**X2-m6. LLaDA (H5) runs under a different scoring convention (untempered score), in 4-bit, with blocks of 32 (so N/k
is 2 to 8, the only regime with coupling, per X2-M1).** A "same sign" result there is not a replication of MDLM's
regime. Fix: state in 14 that H5 tests the small-N/k regime, which MDLM touches only in its last steps.

## Checked and not a finding (EXP-002)
- Matched forward passes: A1-A4 make one forward per step and T = L/k steps. A3's extra cost is CPU/GPU table work, not
  network passes. Matched.
- Common random numbers keyed by (s, tag, step, absolute position): sound. A1 and A3 share `draw` and `prio`, and A3
  differs only through `tilt`. Matched entropy moves A1 and A3 almost together (toy |tau*(A1) - tau*(A3)| mean 0.016),
  so G_cp is not an interpolation artefact in the toy.
- Ties: bf16 logits make within-row ties and, for saturated rows, cross-row ties at 1.0. The fixed priority rule and the
  Prop. 4 tie term cover both if the exact-score reference uses the same convention (15 risk 12 already states this).
- A3 binning: no measurable error from the 2048-bin recipe in my synthetic regimes, including the top bin (Q2). Recorded
  so the lab-engineer does not chase it, with the caveat that real MDLM late states were not simulated.

## What Paper 1 can and cannot say (EXP-002), given the findings
- "H1 negative" or "practically 0 at k = 16": "SF's within-step value coupling has no detectable effect on GPT-2 Large
  log GenPPL at matched unigram entropy at k in {8, 16}". With X2-M1, the paper must add that the exact law predicts
  coupling only in the final steps, and cite the kernel readout.
- H1 supported: only with X2-M2's signed-bias bound met, X2-M3's repetition sensitivity agreeing, X2-M7's second
  evaluator agreeing, and TC_A at final-step states consistent with the size. Otherwise "a contrast between SF and our
  computed twin, not attributable to coupling".
- G_sh and Delta2: "selected-set sharpening versus global temperature at matched unigram entropy" (X2-M6). Not
  "state-dependent sharpening beyond a temperature" in general.
- Novelty: "the first exact tilted twin and matched-entropy decomposition at k in {8, 16}", crediting Hayakawa for the
  k >= 2 tilt approximation (X2-M5). Not "no prior comparison of SF with a tilted sampler at k >= 2".

## Verdict EXP-002: **sign after listed fixes**
X2-M1 (final-step states and the S1 go/no-go on TC_A) and X2-M2 (signed A3 bias bound) come first: they decide whether
the remaining GPU-hours are spent at all and what a positive would mean. X2-M3 to M7 are card edits.

---

## Scripts and logs written for this review (CPU only, no GPU)
- `analysis/framework/redteam_exp_002_coupling_bins.py` -> `.log`: coupling (pairwise MI) as a function of N, k and regime
  under the exact Prop. 4 law; the A3 binned recipe against exact scores; the bins ladder.
- `analysis/framework/redteam_exp_002_toy_direction.py` -> `.log`: the card's toy prior re-read with temperature, a
  matched-entropy read, and both KL directions.
- `analysis/framework/redteam_exp_001_floor_lift.py` -> `.log`: the bf16 floor of the mixture estimator against entropy;
  lift against diversity at fixed consistency.
Commands: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/Scripts/python.exe analysis/framework/<script>.py` (the
single-thread flag is needed while system commit is exhausted).
