## 1. Novelty and closest prior work

**SCER — limited, plausible novelty in the application and computation, not in the identity.** The chain-rule cancellation for two captions that share context is standard, and edit-position scoring has a text-MLM precedent in Goldberg et al. ([arXiv:1901.05287](https://arxiv.org/abs/1901.05287)); pseudo-log-likelihood scoring is also established by Salazar et al. ([arXiv:1910.14659](https://arxiv.org/abs/1910.14659)). Masked Diffusion Captioning scores whole captions with a confidence-ordered chain ([arXiv:2510.26799](https://arxiv.org/abs/2510.26799)); DUEL computes exact likelihood along a deterministic unmasking path for masked diffusion models ([arXiv:2603.01367](https://arxiv.org/abs/2603.01367)). The possible delta is using shared-context conditionals to score **image-conditioned caption edits in a unified masked model**, with shared forward passes and an image-masked baseline. That is a narrower novelty claim than “exact likelihood scoring for MDMs”; the design’s search did not establish priority.

**CANAL — the task combination may be new; its components are not.** Closest work includes FOIL’s detect, locate, and correct tasks ([arXiv:1705.01359](https://arxiv.org/abs/1705.01359)); conformal risk control (Angelopoulos et al., [arXiv:2208.02814](https://arxiv.org/abs/2208.02814)); and VGR, which detects and corrects visual hallucinations in diffusion VLM generations via confidence fluctuation and remasking (ICML 2026, [PMLR paper](https://proceedings.mlr.press/v306/song26d.html)). CANAL’s potential delta is auditing *external captions* with per-word image-visible versus blind conditionals, then applying a clean-caption false-edit-share bound. That combination is plausible, but “posterior” depends on a correctly specified substitution channel and coherent model conditionals—neither follows from a pretrained denoiser.

## 2. Main weaknesses, ranked by severity

**SCER**

1. **Its exactness claim assumes a coherent joint distribution.** The design reports measurable order gaps, especially for adjacent tokens, so order-averaged conditionals are not generally an exact likelihood ratio.
2. **The empirical premise is untested:** no SCER results are reported. The existing GATE headline is negative; it cannot serve as evidence for SCER.
3. **Novelty is incremental and easily crowded.** Minimal-pair MLM scoring, diffusion likelihood methods, and full-caption masked-diffusion scoring leave a demanding priority and significance bar.
4. **The proposed controls may not isolate visual grounding.** Better shared-context scores could come from language context; blind and mismatched-image controls are essential.
5. **Scope and comparison risks:** token alignment excludes many edits, and beating CLIP/SigLIP on templated hard negatives would not establish broad vision-language superiority.

**CANAL**

1. **The channel-posterior derivation appears incorrect as stated** (see counterexample below); the clean-caption context factor need not cancel when substitutions change the distribution of contexts.
2. **The false-edit guarantee is narrow.** It covers exchangeable clean captions, not generated captions, shifted captioners, or edits inside captions that already contain errors.
3. **The channel \(Q\) is a consequential assumption.** “Blind” substitution and a confusion matrix fit on FOIL may not represent real caption errors; the latter also uses supervision.
4. **Repair can compound errors.** Sequential edits change later conditionals, and the stated guarantee explicitly does not cover the iterative repair procedure.
5. **Region maps are expensive and not automatically causal explanations.** Masking image regions measures sensitivity under the model’s masking distribution; the observed order gaps weaken the “exact marginalisation” interpretation.

## 3. Combining them

Combining them could make a stronger *research program*, but not automatically a stronger paper. SCER’s edit ratios can supply CANAL’s image-visible evidence; CANAL adds a task and a narrowly scoped risk-control statement. The preregistered GATE result should appear as a separate negative analysis, not supporting evidence for either method.

Most defensible framing: **“Training-free masked-diffusion auditing of caption edits: shared-context evidence and a clean-caption false-edit control.”** Claim only that the method computes a shared-context score under stated coherence assumptions and controls the expected flagged-word share on exchangeable clean captions. Do not claim exact posteriors or a general false-edit guarantee unless the derivation and domain assumptions are repaired and validated.

## 4. Experiment that would matter

Run a preregistered, paired evaluation on **human-verified, non-COCO relation and attribute errors** and external captions from several captioners. Compare SCER/CANAL with CLIP, SigLIP, BLIP-2 ITM, and VQAScore on detection, localization, correction, false edits on clean captions, and latency. The persuasive result would be a clear gain in *localizing and correcting subtle word-level errors at a fixed false-edit rate*, with blind, shuffled-image, and mismatched-image controls.

Expect to lose on broad recognition and aggregate image-text matching: large contrastive and instruction-tuned systems have stronger visual representations and vastly more training data. The defensible target is selective word-level auditing with calibrated restraint, not overall model superiority.

## 5. Mathematical issue and counterexample

**CANAL Proposition 1 does not follow from the stated channel.** It treats the context probability as a common factor across “no substitution” and “substitution.” But the channel allows \(Q\) to depend on the original word and context, so the probability of observing the unchanged context can differ between cases.

Take two contexts \(x\in\{a,b\}\) and one word \(y\in\{0,1\}\). Let the clean distribution put probability \(1/2\) on \((a,0)\) and \(1/2\) on \((b,1)\). Let the substitution always flip the word, with \(\pi=1\). Observing \((a,1)\) implies substitution with probability one. Yet the proposition’s ratio uses only the conditional at context \(a\): \(P(1\mid a)=0\), making \(N/P(1\mid a)\) undefined, while the actual posterior is well-defined. The derivation therefore needs additional support and context-invariance assumptions—or a revised channel likelihood that includes the context probability.

**SCER also needs qualification:** when masked conditionals are inconsistent, averaging over orders does not become an exact joint likelihood ratio; the chain-rule identity applies to a coherent joint.
