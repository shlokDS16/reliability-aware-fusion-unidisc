```yaml
agent: red-team
date: 2026-10-28
brief: hostile review of GATE-METHOD-SPEC-2026-10-28.md before any code is written (props, calibration, LDA fusion, circularity, falsifiability, feasibility, IF fit, novelty)
sources_examined:
  - research/paper2/method/GATE-METHOD-SPEC-2026-10-28.md (read in full, 685 lines)
  - research/paper2/IDEAS.md (full)
  - research/paper2/ideation/RED-TEAM-2026-10-27.md (full; my earlier verdict)
  - research/paper2/probes/PROBE-REPORT-2026-10-27.md (full)
  - exp_p2/scoring.py (full), exp_p2/run_probe2.py (lines 1-100)
  - runs/P2-PROBE-02/{HOLD.txt, chunks.jsonl, items.jsonl} (read-only, to check the crash pattern)
coverage: >
  NOT read: the three cited papers (Dropout Decoding, DiSP, UniDisc App. G.1), the novelty audit, the UniDisc training code
  (so what mask patterns UniDisc saw in training is unknown to me), exp_p2/core.py, runs/P2-PROBE-01/summary.json. No GPU, no
  web search. Statements about prior art are taken from the earlier red-team file or marked "to be verified".
claims:
  - statement: "As specified, E3's primary contrast (GATE-M minus random gate) can be won by a gate that is worse than no gate."
    status: supported
    evidence: "spec 4.5 consequence (ii) says a random gate always lowers SNR; spec 13 primary contrast is GATE-M vs random gate"
    level: E0 (reasoning from the spec's own proposition)
    confidence: 0.9
  - statement: "The calibration guarantee does not cover the use case (corrupted items)."
    status: supported
    evidence: "spec 5 'What is not guaranteed' (i), (ii); Prop. 5 statement"
    level: E0
    confidence: 0.9
competing_explanations:
  - "any GATE-vs-random gain = mask-geometry difference (clustered vs scattered masks), not detection"
  - "any AUROC above 0.5 on JPEG/noise = texture/entropy detector, not corruption detector"
  - "any fusion gain = two fitted weights on a supervised calibration set, not fusion"
unknowns: [UniDisc training mask patterns, COCO val membership in UniDisc/LlamaGen training data, true cause of the 0x116 crashes, hard-negative false-negative rate]
next_test: {hypothesis: "q separates codes changed by JPEG q10 / noise 0.1 from unchanged codes better than a texture-only and a neighbour-codebook-distance baseline", intervention: "CPU-only baselines on the 20 stored probe-2 items plus pixel statistics, before any GPU", primary_metric: "per-item AUROC vs Z", falsifier: "cheap CPU baseline within the paired-bootstrap CI of q", gpu_hours: 0}
```

# Red-team report: GATE method specification (2026-10-28)

Severity: BLOCKER (stops the gate; must be resolved or the claim withdrawn), MAJOR (a sceptical reviewer rejects or heavily
discounts the paper on this), MINOR. "Resolved if" states the observable condition that would clear the finding; it is a
criterion, not a design.

## Verdict (summary first)

**GO WITH CHANGES, confidence 0.45 that this verdict is right; my judgement (not measured) of the probability that the spec as
written yields a defensible Information Fusion submission by Fri 31 Oct / Sat 1 Nov is about 0.15.** Three blockers (B1 to B3). The
spec is much better than the raw idea (the cancellation flaw is fixed in design, a headroom rule exists, theory is honest about
several limits), but the central downstream experiment is built so that it can pass without the method working and is likely to
return a null at a ceiling, and nothing can start until the GPU crash is understood.

## 0. Were my earlier findings (RED-TEAM-2026-10-27) truly resolved?

| Earlier finding | Status | Why |
|---|---|---|
| F1.1 r = A - B cancels (fatal) | Resolved in design | q = B - D, plain-B, r kept as control (spec 3.2, Prop. 3). Untested on the real model (probe 2 never ran). |
| F1.2 token swap is the easy case | **Not resolved** | "Patch occlusion with random codes" is relabelled "realistic" (spec 13 Corruptions, primary list). It is the same uniform-random-code corruption as swap, clustered. See M3. |
| F1.3 no measurable drop, ratio of noise | Partly | Headroom rule exists (spec 13, E3) but probe 1 already shows a 0.990 ceiling; see B2. |
| F1.4 forking paths | Partly | One primary contrast is declared, but it is the wrong contrast (B1); arms, scores, K, alpha, severities still number in the dozens. |
| F1.5 masking as regularisation | Partly | "GATE on clean" control present; the random control has a different mask geometry (M5). |
| X1 weak generator | Resolved for verification; **open for E5** (T2I typo grid and CLIPScore on a generator whose images the earlier red team called defective). |
| X3 one model (my "one missing experiment") | **Not resolved** | E7 is optional, last in the order, unsized, on an unmeasured 8B 4-bit stack (spec 13). See M9. |
| X5 IF scope | **Not resolved** | See M7. |
| Prior art (Token-Critic 2209.04439, Nemotron-Labs-Diffusion-Image 2606.29814, self-correction 2602.02927, all E1 snippet level in my earlier file) | **Dropped** | Spec 11 compares only against Dropout Decoding, DiSP and UniDisc G.1. See M8. |

## BLOCKERS

### B1. The primary contrast does not test the claim, and its control is guaranteed to lose by the spec's own theory
- Evidence: spec 4.5 (ii): "A random gate (beta = alpha) ... always lowers SNR". Spec 13 "Pre-declared primary contrast": accuracy of
  LDA-fused GATE-M **minus the same statistic with a random gate of equal size**. YAML claim 5: "restores ... more than a random gate".
- Problem: if random gating is by theory strictly harmful, then any gate that is merely less harmful than random (including one
  that is worse than no gate) wins the primary test. The paper's stated purpose is restoration under corruption; the comparator
  that measures that (no gate, corrupted) is only a secondary arm, and the headroom check is the only place it enters.
  Under the spec's own Prop. 4(iv) GATE on clean is also predicted to be harmful, so "GATE beats random" is predicted to hold
  even on clean inputs, where there is nothing to restore.
- Resolved if: the primary contrast is GATE-M versus no gate on the corrupted arm, with the random gate demoted to a
  mechanism control; the claim is withdrawn if GATE-M does not beat no gate on at least one realistic corruption.

### B2. The downstream experiment is very likely a null at a ceiling, and the theory does not cover the dominant statistic
- Evidence: probe 1: a_full_pmi alone and a_full_pmi + b_full are both 0.990 (CI 0.977 to 1.000) on easy deranged negatives;
  spec 7 "Headroom problem", F8. Spec 4.5 last sentence: the text-direction statistic "is not additive ... gives only the
  qualitative ordering" (so the theory covers only the image direction, 0.843 alone, which carries the smaller weight in any
  fusion with a 0.990 partner).
- Problems:
  1. The fused decision is dominated by the text direction, which conditions on the whole image with about 5% of tokens masked
     (48 to 51 tokens at alpha = 0.05, spec 5) or one 64-token patch. Nothing in the spec or probe 1 suggests such a change moves
     a 0.990 statistic by a measurable amount. The most probable outcome (my judgement) is that every arm, including random
     and oracle, sits within noise of the clean value, the headroom rule excludes the corruptions, and the primary family is empty.
  2. The fusion claim is untestable at that ceiling by the spec's own admission (spec 12: "single direction near LDA at the clean
     ceiling"). The "fusion" half of the paper therefore has no measurable result unless hard negatives open headroom.
  3. Hard negatives are "the caption of another test image sharing at least one COCO category", with a deranged fallback (spec 13
     E3, U4 unresolved). Another image's caption that shares a category can be a valid description of the true image (COCO scenes
     are multi-object), so some negatives are true positives: label noise puts a ceiling below 1 for every method and makes
     small differences uninterpretable. No false-negative audit is planned.
  4. No power analysis (my F1.3 ask was never met). With n = 300 paired items near a high accuracy, the number of discordant items
     is small; for illustration, if only 12 of 300 items change between two arms, a 9 versus 3 split gives a two-sided exact
     McNemar p of about 0.15 (arithmetic, assumption labelled). The spec states no minimum detectable effect.
  5. The headroom exclusion rule makes the Holm family size data-dependent (spec 13: corruptions with no headroom are removed from
     the family after the data are seen).
- Resolved if: before E3, a CPU or small-GPU check shows corrupted-no-gate accuracy below clean by at least 2 paired SE on a
  hard-negative set audited for false negatives, and a stated minimum detectable effect at n = 300 is below the effect the paper
  claims. If no realistic corruption passes, the downstream claim is withdrawn (not reworded).

### B3. Nothing can be run: the crash is undiagnosed and the spec makes the GPU workload larger and newer
- Evidence: `runs/P2-PROBE-02/HOLD.txt` (two 0x116 crashes, whole-GPU memory to 12,087 MiB in 5 s both times, 75% PyTorch cap
  did not help). `chunks.jsonl`: the second run resumed at done = 20 (so the crash is not tied to one item index); it died about
  two minutes after chunk start, after one item. `items.jsonl` has 21 rows. Probe report: seventh unexpected restart since 14 Oct.
  Spec 13 estimates about 7.9 GPU-h of item time, about 16 h wall at duty 0.5, plus E7; spec F12 mitigates with the same safeguards
  that already failed. Today is Wed 28 Oct; deadline Fri/Sat.
- Problems: (a) The failing job was only the small probe 2 (about 81 passes per item at most); E3 alone is about 204 passes per
  item and the spec adds code paths never executed on this machine (C and D all-masked passes, 16-step re-infill sampling,
  gate-conditioned batches). (b) The estimate 0.12 s per pass comes from a median; probe 1's mean item time is 9.7 s against a
  7.0 s median and one item took 635 s (a stall nobody explained). (c) Eight algorithms, ten unit tests, a data-steward step
  (COCO instances, CLIP weights, both U4, status unknown) and a manuscript with eight figures must all fit in about 2.5 days, on a
  plan the earlier red team already rated 0.35 for a "clean result set by Thursday" before the scope grew.
- Resolved if: a diagnosed, fixed crash cause with a completed 200-item run of the existing probe 2 (no new code) before any E-series
  work starts; otherwise the spec's timeline is not a plan.

## MAJOR

### M1. Prop. 1 ("masking is marginalising") is a restatement of the training objective, and its use here ignores data-dependent gating
- Evidence: spec 4.1; Alg. 4/5 (G chosen from observed values, then masked).
- (a) With assumption (a1) (Bayes-optimal denoiser) the statement is the definition of the conditional; its content is entirely
  in (a1) and (a2), which are never tested on the real network. Probe 1 itself is evidence against coherence: the same model scores
  0.730 (K = 8) versus 0.943 (full mask) for the text direction (probe report table), i.e. its predictions under different mask
  patterns disagree materially. The spec reads that as "dilution" (inference) but it is equally a measurement of the
  amortisation gap that (a1) assumes away.
- (b) The proposition holds for a gate G fixed independently of the data. GATE chooses G because x_G looks improbable. Conditioning
  on R while ignoring that G was selected on the values of x_G is informative missingness (selection on the unobserved value);
  p(x_j | x_R, G chosen) is not p(x_j | x_R). The spec cites Rubin (decisions list, item 6) but no proposition uses the distinction.
- (c) Under real corruption with detection rate beta < 1, x_R still contains corrupted tokens, outside the clean-data model that
  makes the identity meaningful. "Exact marginalisation" does not imply robustness.
- Resolved if: a test on UniDisc (not on a fake network) of consistency between mask patterns (chain-rule agreement of a two-token
  joint evaluated in both orders, or marginal-versus-mask equality on held-out pairs) with a stated tolerance; and the proposition
  restated for a data-dependent G.

### M2. Prop. 4 (when gating helps) has a variance error, a false premise for the realistic corruptions, and demands an implausible detection rate
- Evidence: spec 4.5.
- (a) Proof error: after gating, each included token contributes Delta_j with probability (1 - alpha) (clean) or (1 - beta)
  (corrupted). Treating inclusion as random across items adds a Bernoulli term alpha(1 - alpha)mu^2 per clean token to the variance;
  the stated "after" denominator omits it. (The algebra from the stated formulas to the final inequality is correct; the formulas
  are not.)
- (b) Corrupted tokens are modelled with mean 0 for the evidence. For JPEG and noise a changed code is a noisy version of the same
  content and still carries caption information, so mean > 0 and gating removes signal. The oracle gate is then not an upper bound
  (spec 12 calls it one).
- (c) Using the spec's own numbers: patch 8x8 gives rho = 64/1024 = 0.0625; alpha = 0.05. The condition becomes
  beta - 0.0975 > 0.7125 sigma^2 / sigma_c^2 (derived). If sigma_c^2 is about sigma^2 the gate must detect more than about 81% of the
  patch tokens at 5% false alarms to help at all. The spec never says what sigma_c^2 / sigma^2 is, nor offers a measurement plan.
  Corruption fraction for JPEG q10 and noise 0.1 (the changed-code fraction) is also never stated; if it is large, rho -> 1 and the
  intra-modal context that q relies on is contaminated (F4).
- Resolved if: the corrected inequality, with measured sigma^2, sigma_c^2, mu and the changed-code fractions, is reported next to
  the observed beta and predicts the sign of the observed GATE-versus-none difference.

### M3. The detection premise (q on realistic corruptions) has no theory, the E1 falsifier is toothless, and patch is mislabelled realistic
- Evidence: spec 4.2 ("This is closer to JPEG and noise"), YAML falsifier, spec 13 E1, probe-2 code (`run_probe2.py` lines 49-52: patch is uniform random codes).
- (a) Prop. 2 assumes the corrupted value is drawn from a density that does not depend on the context. For JPEG and noise the corrupted
  code is a deterministic-plus-noise function of the clean code, strongly context-dependent. The proposition says nothing about the
  case the paper wants to be about; "closer to JPEG and noise" is an assertion.
- (b) The falsifier is "AUROC of -q not above random (CI includes 0) on all three realistic corruptions". A detector at AUROC 0.55 passes
  this. It does not compare with any cheap alternative, so E1 cannot kill the idea even if q is a texture detector.
- (c) Only two of the three "realistic" primaries are realistic (JPEG, noise). Patch with uniform random codes is the easy case I
  flagged (F1.2). If patch passes and JPEG/noise fail, the paper's evidence is the easy case only.
- (d) Statistic selection (plain-B vs q) is done per Prop. 2 by corruption type on the tuning fold. A deployed gate does not know the
  corruption type, so "hypothesis-free" is not true of the selected, corruption-specific statistic.
- (e) E1 is run on the tuning fold (spec 13: the same 200 items select the statistic, K and aggregation). The detection AUROCs
  reported in Fig. 3 would be the selection data. Probe-2's existing 21 rows cannot serve.
- Resolved if: a pre-set margin (AUROC above the best cheap baseline, not above random), computed on items not used for selection, on
  JPEG and noise separately; patch reported as a sanity check.

### M4. Circularity and missing cheap baselines in the detection and repair evaluation
- Evidence: spec 3 (Z = 1[code changed]), F5, F6, 11, 12.
- (a) The label is defined by the tokenizer (code changed), the detector by a model of tokenizer codes. Codes flip most where the
  encoder is unstable (textured regions), and the model's masked likelihood is lowest where local entropy is highest for clean tokens
  too. AUROC pooled within an item mixes spatial-texture variation with corruption. The only controls are `random` and s3 (an
  uncertainty score that ignores the observed value and is predicted by the spec itself to be weak on swap/patch, Prop. 2/spec 12);
  a baseline chosen to lose is not a control.
- (b) Missing baselines a reviewer will name: local pixel variance/gradient; distance of a token's codebook embedding to its
  neighbours' (no network); code rarity; and, decisively for JPEG and noise, ordinary pixel-domain denoising/deblocking before the
  tokenizer. The corruption acts on pixels, so a defence after tokenisation must beat a defence before it.
- (c) The graded-label fix (AUROC "on the upper half of the embedding distance", F5) is a post-hoc subset chosen after seeing
  distances.
- (d) Items with fewer than 5 corrupted or clean tokens return NaN (spec 8 L2b, `run_probe2.py`); for dense corruption this may drop
  most items and bias the average AUROC to the survivors. Drop counts are not planned.
- Resolved if: q beats the texture, neighbour-distance and pixel-denoise baselines under the paired bootstrap, with item-drop rates
  reported per corruption.

### M5. The random-gate and oracle controls differ from GATE in more than "detection"
- Evidence: spec 12, 13 (random gate "of equal size, 3 seeds"; oracle G = {Z = 1}).
- GATE's flagged set is spatially clustered (corrupted patches, textured regions); a random gate is scattered. Block masks and
  scattered masks are very different inputs to a masked model (the spec itself notes low-density patterns, F10). A GATE-vs-random
  difference can come from mask geometry. For noise/JPEG the "oracle" masks nearly every flipped code and is not an oracle for
  evidence (M2b). So both controls bound the wrong thing.
- Resolved if: a geometry-matched control (random placement of GATE's own mask pattern) is included and the GATE-versus-geometry-
  matched-random difference is the mechanism test.

### M6. The calibration guarantee is real but narrower than readers will read it; two protocol gaps
- Evidence: spec 5, Prop. 5, Alg. 3/4.
- (a) Prop. 5 bounds the expected fraction of flagged tokens on a **clean** item. Every use case is a corrupted item, where the spec
  itself says the bound does not apply to its clean tokens (swamping, 5 (ii)). The word "guarantee" will be read as "a flagged token is
  corrupted with confidence 1 - alpha" or "at most alpha of good tokens are lost". Neither holds.
- (b) Using the spec's numbers: at alpha = 0.05, 960 clean tokens in a patch-8x8 image give about 48 expected false flags
  (derived) against at most 64 true flags, so precision is at most 0.57 even at beta = 1 and 0.40 at beta = 0.5 (derived). The
  guarantee says nothing about false discoveries among flagged tokens.
- (c) The guarantee is averaged over positions; the spec expects a non-flat clean false-alarm map (F6). A marginal bound with 48 false
  flags concentrated on image borders is a marginally valid but practically different gate. Mondrian variants multiply classes
  and thresholds, and the choice between pooled and Mondrian is made after looking at the clean FAP map (a calibration-set
  decision; 5 (v) forbids it).
- (d) Ties: jitter is added in calibration (Alg. 3 step 1) but Alg. 4 (test-time gating) has no jitter step. With bf16 logits spaced
  0.0625 (F7) many scores tie; strict "u > tau" with un-jittered test scores and jittered calibration scores breaks exchangeability.
- (e) "Clean" COCO tokens are the VQ codes of an already JPEG-compressed photo through a lossy tokenizer; the calibration null is
  "COCO-as-tokenised", and the labelled corruption is relative to that.
- (f) Multiplicity: a single threshold from clean data is reused across corruptions, so there is no multiplicity in tau. The multiplicity
  is in the choices around it (score, K, alpha in {0.01, 0.05, 0.10}, pooled/Mondrian, word/piece, min/sum) and the headroom-
  dependent family (B2). The spec lists these but fixes none before the tuning fold.
- Resolved if: the paper's wording states "expected false-alarm proportion among clean tokens of clean items"; precision/FDR among
  flagged tokens and FAP on clean tokens of corrupted items are reported with the same prominence; test-time jitter is specified.

### M7. Information Fusion fit: this reads as a generative-model robustness trick with a fusion label
- Evidence: spec 4.4, 7; IDEAS.md decision 4 (scope risk accepted, no enquiry).
- The evidence-separation rule forbids the gate from using the other modality in R1. So the "gate" is single-modality outlier
  detection plus dropping, and the only cross-modal operation is a 2-feature linear classifier on two PMI readings from the **same
  network** on the **same pair**. The cases where cross-modal information gates the other modality (R2, tot = A - D) are the
  ones with a trusted reference, i.e. repair with a known clean caption, which is the secondary task. The two "sources" are not
  independent sensors; there is no fusion of conflicting information that is not a single learned joint model's conditional.
  The Kalman-gate analogy is invoked for R2 and then excluded by the paper's own R1 rule for the main experiments.
- Prior red team: "None of the five yields a clearly 17+ IF contribution"; X5 unresolved. A reviewer sees 'purify tokens before
  likelihood scoring', not 'fusion'.
- Resolved if: an IF editor or reviewer-proxy reads the abstract and the experimental design and identifies the fusion contribution
  without prompting; otherwise desk-rejection risk stands (not quantified; no data).

### M8. Novelty delta is narrow, one baseline is a strawman, and prior art was dropped
- Evidence: spec 11 (table and baseline paragraph); my earlier file (Token-Critic, Nemotron-Labs-Diffusion-Image, 2602.02927: E1).
- (a) "Pseudo-log-likelihood outlier score on masked tokens" is Salazar et al. (which the spec already cites) applied to image
  codes; "conformal threshold on an anomaly score" is a known pattern (conformal outlier testing; I have not checked it, to be verified,
  and the spec cites none). What remains is the particular combination plus the evidence-separation rule, which is a design choice
  with no experiment that could show it matters except F2's gate-induced false acceptance.
- (b) The "DD-style" baseline ranks by s3 = 1 - max p, which ignores the observed token. Spec 12 predicts it loses; real Dropout
  Decoding uses a different estimator (as the spec says, labelled adaptation) and is autoregressive. A baseline predicted to lose
  by the authors' own theory cannot support "better than Dropout Decoding".
- (c) The UniDisc G.1 comparison is "random gate then re-infill"; G.1 as described in the spec selects best-of-n by own likelihood,
  which is not what the baseline does.
- (d) Token-Critic-style "score tokens with a critic then resample" is the natural comparator for the repair half and is absent.
- Resolved if: the introduction's delta sentence survives a side-by-side with these works; a baseline that uses the observed value
  (plain-B without the conformal threshold, i.e. GATE minus calibration) is run as the DD/Token-Critic proxy.

### M9. Single small model; generalisation unaddressed
- Evidence: spec 13 E7 ("optional, unverified"; Omni-Diffusion 8B 4-bit time and memory never measured), F15. My earlier "one missing
  experiment" (second model) is still missing. UniDisc has no stated licence (setup note, earlier file). Given B3, E7 is not
  schedulable.
- Resolved if: either a second model result exists, or all claims, title and abstract are scoped to "one 1.4B model" and the
  reviewer-expected objection is accepted as a stated limitation.

### M10. Fusion rule (Fisher LDA) is a supervised two-parameter classifier presented as a principled combiner
- Evidence: spec 7.
- (a) Weights are fitted on 500 calibration pairs of true versus **deranged** wrong captions, then used on **hard-negative** test
  pairs and on corrupted/gated statistics. The optimal direction depends on the negative type and on the gate; fixed weights are
  mismatched to exactly the test conditions (and the gate-aware rule omega_T(1 - g) is an untested guess).
- (b) The baselines (single directions) have no fitted weights, so the fused arm has two extra degrees of freedom fitted on labelled
  match/mismatch data in a paper that calls the method training-free; the equal-pass control (spec 7 (d)) equalises passes, not
  fitted parameters.
- (c) At the 0.990 ceiling the rule cannot show a gain (B2), and the spec predicts that.
- (d) Idea C's inverse-variance weights are declared undefined (no Monte Carlo variance under full masking, spec 7), i.e. what
  remains of Idea C is "add two numbers with fitted weights". My earlier verdict was KILL standalone / GO only as a component.
- (e) Unpaired AUROC is reported (spec 13) but E is a sum over n caption terms and about 1024 image terms; caption length and image
  content confound it, and the paired-difference weights have no offset or length normalisation.
- (f) Gaussianity of Delta is assumed for "optimal"; never checked.
- Resolved if: a fused-versus-best-single comparison on hard negatives where the best single is not at ceiling, with weights fitted
  on the same negative type, and a held-out fold for the weights.

### M11. The unit tests cannot detect the failures that matter
- Evidence: spec 8, L4, L1, L10.
- The "perfect denoiser" fake returns exact conditionals, so it satisfies Props. 1, 6, 7 by construction; L1 checks the conformal
  arithmetic on synthetic scores. The only real-model test (L10) checks that cached logits are identical (and claims "bitwise-equal"
  across different batch compositions, which bf16 kernels with batch-dependent reductions may violate; minor). No test measures how
  far UniDisc is from (a1). Props. 1 and 6 are also stated so that either outcome is accommodated: M >= I is "theory"; I > M is
  "amortisation, F10". A claim that explains both signs is not a prediction.
- Resolved if: Props. 1/6 get a pre-stated tolerance on the real model (M1) and a result in either direction is stated in advance to
  refute or support them.

## MINOR

- m1. The 0.990 PMI accuracy comes from an exploratory choice among about ten probe-1 variants on 300 items (probe report); if the test fold overlaps probe-1 items (spec 13 leaves it as "check selection.json") the evidence statistic was selected on test data.
- m2. U3 unresolved: how probe 1's "image-masked null" was built (caption masked too?). The spec's D (everything masked) may not be what produced 0.990, so the 0.990 is not guaranteed to transfer.
- m3. Conformal Risk Control reference is "from memory" (spec 5); do not cite before citation-validator checks. The spec also lists a CFAR reference and a Kalman innovation-gate reference unchecked.
- m4. Word-level text gating: min over pieces; typo tokens are rare pieces; on 5 to 32-token captions with about 5 to 25 words and alpha = 0.05 the per-caption FAP is lumpy (0 or at least 1 word), and caption-side headroom is also at ceiling (E4 has the same B2 problem).
- m5. E5: the T2I typo grid needs a sampler change (gated words left as [MASK] and never unmasked) on a model not shown to tolerate masked prompt tokens during generation; CLIPScore on images the earlier red team described as defective (X1); CLIP weights availability unknown (U4).
- m6. Contamination unknown: whether COCO val2017 images or captions were in UniDisc's or the LlamaGen tokenizer's training data is not checked; memorisation would inflate 0.99 and make the score "restoration" meaningless.
- m7. bf16: spec F7 says the logit spacing (0.0625 for logits in [8, 16)) is coarser than the probe-1 per-token margin (+0.005 nats); the sum over 1024 tokens averages some of this, but gating on single-token scores is exactly where quantisation bites. U5 (fp32 final projection) open.
- m8. Cost table inconsistency risk: "about 204 passes per item" for E3 is not itemised; the count cannot be audited from the spec.

## What result would force rejection of the claim (stated now)
1. GATE-M does not beat **no gate** on a corrupted arm for any of JPEG q10, noise 0.1 (B1).
2. The corrupted-no-gate arm is within 2 paired SE of clean on hard negatives for every realistic corruption (B2): no restoration claim is possible.
3. q does not beat the best of {texture, neighbour codebook distance, pixel-domain denoise} on JPEG and noise on held-out items (M3, M4).
4. Realised FAP on clean test items exceeds alpha by more than its CI after the specified tie handling (M6).
5. A geometry-matched random gate equals GATE-M (M5).
6. Fused accuracy does not exceed the best single direction on a set where the best single direction is below the ceiling (M10).

## The one experiment whose absence would cause rejection by a sceptical NeurIPS/ICML-style reviewer
GATE versus **no gate** (and versus pixel-domain denoising before tokenisation) on JPEG and noise corruptions, on a hard-negative
set with measured headroom and a stated power, on a second model or with the claim scoped to one. The spec's primary contrast
(vs random, B1) and ceiling (B2) make that result unobtainable as designed.

## Verdict
**GO WITH CHANGES, confidence 0.45.** Not KILL because the fixed design is internally coherent, probe 1 shows a real
likelihood signal, and the changes needed (B1 contrast, B2 headroom check on CPU data, M3 baselines) are cheap to state. It
becomes KILL if B3 is not cleared early on Thursday: with the GPU on hold and 16 h wall of work, there is no path to the primary
contrast by Fri/Sat, and a negative or feasibility note would be the honest output.
