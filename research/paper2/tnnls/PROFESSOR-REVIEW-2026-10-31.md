# Technical comments from the supervising professor (received from Shlok, 2026-10-31), verbatim

* Technical limitations or concerns
   * The SNR lemma assumes conditional independence and is not empirically validated on the model; correlated-token extension remains theoretical without direct linkage to outcomes.
   * The gating suspicion score (u_j = D_j−B_j) shows poor detection on realistic corruptions (near-chance AUROCs on JPEG and Gaussian), limiting the plausibility of the gating approach as instantiated.
   * Positive-control (patch/swap) hypotheses in Study 1 did not reject, raising residual concerns about sensitivity or design, despite an internal audit.
   * Self-hosted preregistration and audits (not third-party timestamped) slightly weaken trust in the protocol integrity relative to independent registries.
* Experimental gaps or methodological issues
   * LRF is trained on the same corruption type (Gaussian σ=0.1) that anchors the primary test, so the confirmatory result isolates generalization to new images, not new corruptions; broader claims about corruption-specific reliability remain untested.
   * Only one backbone (UniDisc), one dataset (COCO val2017), and single severities per corruption are studied; generalization across models/datasets/severities is unknown.
   * Reference encoders (CLIP, SigLIP) nearly saturate accuracy on the same items, suggesting the verification task configuration may be too easy to establish broader significance.
   * Exploratory comparisons reveal a simple linear logit over the same features can match or exceed LRF in some conditions, and denoise-then-score can outperform LRF under Gaussian noise, questioning whether the proposed GAM is essential.
* Clarity or presentation issues
   * Heavy reliance on supplementary materials (S-I to S-VIII) makes it difficult to fully audit methods and decisions without access during review.
   * The abundance of families/tests and outcome wording rules, while rigorous, makes the narrative dense and adds cognitive load.
* Missing related work or comparisons
   * While related work coverage is strong, empirical comparisons to alternative token-level reliability schemes (e.g., uncertainty-driven dropout decoding, other attention/MIL variants) are mostly exploratory and not part of the preregistered core.
   * No cross-backbone evaluation or held-out corruption severities to assess whether findings are model- or condition-specific.

Detailed Comments

* Technical soundness evaluation
   * The per-token log-likelihood ratio formulation is sound and well-posed for a unified masked diffusion model; the study correctly isolates the scoring network's own evidence.
   * The conformal risk control application (bounding expected flagged share on clean items) is appropriate and correctly scoped; the guarantee is clearly stated as limited to clean exchangeable items and does not imply detection power.
   * The SNR lemma provides intuition but rests on independence (or exchangeability) and Gaussian approximations for accuracy; the authors rightly avoid over-interpreting it.
   * Study 1's positive control not rejecting invites further diagnosis (e.g., power analysis on discordant counts, sensitivity to corruption severity, or gate parameterization), though unit tests and recomputation reduce the chance of trivial code bugs.
* Experimental evaluation assessment
   * Preregistration, paired testing, Holm correction, and bootstrap intervals are all strengths and raise confidence in the narrow claims.
   * Study 1's null findings are carefully bounded (±0.05) and not overstated; token-level detection analyses explain why gating may be ineffective on realistic noise/JPEG.
   * Study 2's primary result (Gaussian σ=0.1) is statistically persuasive (one-sided McNemar p=0.0005), replicated with length-matched negatives, and clean non-inferiority is bounded by design; however, JPEG shows no significant gain, and splice improvement is borderline (Holm-adjusted p=0.049).
   * The reference encoders nearly saturate accuracy, limiting the practical value of further verification work in this setup; still, as the paper positions itself as measuring the unified model's evidence behavior, this is acceptable context rather than a required head-to-head comparison.
* Comparison with related work (using the summaries provided)
   * The work complements prior diffusion-based classifiers and scoring (e.g., diffusion classifiers, zero-shot reweighting), by probing token-level evidence in a unified masked diffusion model rather than pixel/latent denoising errors across classes.
   * Relative to robustness benchmarks for multimodal models, the present study is narrower (one model; token-evidence fusion) but addresses a less-studied angle (token-level reliability under image corruption without external encoders).
   * Reliability-aware/dynamic fusion literature (e.g., C2MF, DMS, evidential methods) generally handles modality-level or view-level reliability; this paper pushes to token-level within a unified model. However, unlike those works, it offers limited evidence of generalization beyond the trained noise type or across backbones.
   * DUEL-style exact likelihood for masked diffusion is not used here; exploring exact token-likelihoods under deterministic unmasking policies could strengthen the theoretical–empirical link.
* Discussion of broader impact and significance
   * The main value lies in a careful, preregistered measurement paradigm for unified masked diffusion models as verifiers and an existence proof that token-level reliability weighting can help under certain corruptions without harming clean performance.
   * Practical impact is constrained: CLIP/SigLIP already solve the verification task on these items; LRF's gains are modest and sometimes surpassed by simple preprocessing or linear models. Nonetheless, as unified masked diffusion models proliferate, understanding their internal evidence aggregation under corruptions is of scientific interest.

Questions for Authors

1. Can you diagnose why the positive control (patch/swap) in Study 1 failed to reject—was power insufficient given discordant counts, or is the gate fundamentally unhelpful even when corruption labels are token-level ground truth?
2. How sensitive are LRF's Gaussian-noise gains to noise severity (e.g., σ ∈ {0.05, 0.2}) and to mismatched severities at test time? Could you report a small-sample severity sweep?
3. Given the exploratory finding that a linear logit on the same features can match/exceed LRF in some conditions, why prefer the hinge-basis GAM? Is there any inductive-bias advantage (e.g., interpretability of learned shapes) realized in practice?
4. Can you provide a cross-backbone check (e.g., a second unified masked diffusion model or a smaller UniDisc variant) to assess whether the LRF improvements are model-specific?
5. Would DUEL-style exact likelihood under a deterministic unmasking policy change the per-token evidence measurement or suggest alternative token weighting rules with stronger theoretical grounding?
6. How robust is LRF to domain shift (e.g., Flickr30K or a different caption corpus) and to different negative-caption sampling protocols (beyond category-disjoint)?
7. Could you re-run Study 1's gate with a more powerful token-level detector (e.g., learned from B/D features) while maintaining conformal false-alarm control on clean items, to test whether detection, not the withholding idea, is the bottleneck?
8. The self-hosted preregistration and audits are commendable; can you provide an independent timestamp (e.g., OSF/Zenodo private DOIs) in the camera-ready to strengthen the record?
9. For efficiency, can you quantify the marginal compute overhead of LRF at inference (beyond stored arrays) and discuss how the approach might scale to larger image token grids?

Overall Assessment
This is a careful, transparent, and statistically rigorous study of token-level evidence aggregation in a unified masked diffusion model under image corruptions. Study 1's negative result is informative: a conformally controlled masked-likelihood gate does not alter verification accuracy beyond ±5 points on realistic corruptions at tested severities, and the token suspicion score lacks detection power on JPEG/noise. Study 2 provides a well-executed preregistered confirmation that a frozen, learned token-weighting can improve performance under Gaussian-like noise without harming clean accuracy on fresh images. However, the broader impact is limited by scope (one model/dataset, single severities), by training on the same corruption type used for confirmation, by very strong reference encoders on the same task, and by exploratory evidence that simpler alternatives (linear models; pixel denoising) can match or exceed the proposed weighting in some cases. The paper's value lies more in methodology, openness, and empirical characterization than in a general-purpose robust verifier. With additional validation across backbones, severities, datasets, and a stronger justification for the particular weighting model over simpler alternatives, this work could make a solid contribution. As it stands, I view it as a thorough and honest measurement paper with moderate novelty and impact.
