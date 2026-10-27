```yaml
agent: novelty-auditor
date: 2026-10-27
brief: Novelty audit of Ideas 1-5 in research/paper2/ideation/IDEAS-RAW-2026-10-27.md (unified multimodal masked discrete diffusion, Information Fusion paper)
sources_examined:
  - arXiv:2602.22246v1 (DiSP), 2412.06474v2 (Dropout Decoding), 2602.02927v1 (FreeCorrection), 2508.13021v4 (PC-Sampler/Uncode), 2503.17076v1 (Halton), 2603.06577v2 (Omni-Diffusion)
  - arXiv:2503.20853v1 (UniDisc), 2306.01879v4 (VisualGPTScore), 2305.16397v3 (DiffusionITM), 2603.01367v2 (DUEL), 2410.03355v3 (LANTERN), 2508.07747v1 (GSD)
  - arXiv:2604.00007v1 (Dynin-Omni), 2603.26364v1 (LLaDA-TTS), 2605.30748v3 (Chatterbox-Flash), 2601.22889v1 (DiffuSpeech), 2604.24357 (DPRM), 2509.19244v3 (LaViDa-O), 2512.14008v2 (Sparse-LaViDa)
  - abstracts only: 2605.25820v2 (VRCD), 2608.26580v1 (VIG-Sampler), 2607.29079v1, 2610.12214v1, 2610.03320v1, 2609.35407v2, 2506.02095v2, 2405.20759v3, 2303.16203v3, 2209.04439v1, 2307.14701v2
coverage: >
  Full text (arXiv HTML converted to plain text, grep plus targeted reads of method, limitation and appendix
  passages; math is stripped by the converter so formulas were read only where noted) for the first 13 listed
  works plus DPRM Appendix C-I, LaViDa-O Sec. 3 and Sparse-LaViDa Sec. 3. Not covered: OpenReview (no ICLR 2027
  or NeurIPS 2026 submission could be listed with the tools available; WebSearch returned nothing for it), code
  of any paper, Semantic Scholar (HTTP 429 on every call, 12 attempts), the references of each closest paper
  (not chased), and any paper not indexed by arXiv API or the search engine in the last 90 days.
claims:
  - statement: "Idea 1: no found work scores discrete conditioning tokens of a unified MDM by masked pointwise mutual information and gates, marginalises or imputes them; but DiSP masks vision tokens of multimodal diffusion LMs at inference (backdoor purpose) and UniDisc shows qualitative repair of corrupted image-caption pairs."
    status: supported
    evidence: arXiv:2602.22246 abstract and Sec. 3.3; arXiv:2503.20853 App. G.1
    level: E2
    confidence: 0.6
  - statement: "Idea 2: the boundary-first mechanism for repeated top/bottom image patterns is already hypothesised by the Omni-Diffusion authors (Sec. 3.4, citing PC-Sampler); remedies by fixed order exist (LaViDa-O stratified, Halton, Sparse-LaViDa); UniDisc states it is positionally invariant (App. G.2)."
    status: supported
    evidence: arXiv:2603.06577 Sec. 3.4 and ref [21]; arXiv:2509.19244 Sec. 3; arXiv:2503.20853 App. G.2
    level: E2
    confidence: 0.85
  - statement: "Idea 3: each component (per-direction null-debiased likelihood score, UniDisc bidirectional retrieval, shared-mask variance reduction, staged sample allocation) exists separately; no work found that fuses two directions inside one unified MDM with variance weighting."
    status: supported
    evidence: arXiv:2306.01879, 2305.16397, 2503.20853 Sec. 4.3, 2303.16203 (abstract/supplement via search)
    level: E2
    confidence: 0.55
  - statement: "Idea 4: probability aggregation over latent-proximity token sets is established for AR speculative-decoding acceptance (LANTERN, GSD); no found work uses it for position selection in masked diffusion."
    status: supported
    evidence: arXiv:2410.03355 Sec. 4.1-4.2; arXiv:2508.07747 Sec. 3-4
    level: E2
    confidence: 0.65
  - statement: "Idea 5: joint text-plus-speech generation in one masked canvas with global confidence unmasking exists (DiffuSpeech, Omni-Diffusion); no found work measures commit order or text-speech disagreement between the modalities or gates speech by aligned text."
    status: supported
    evidence: arXiv:2601.22889 Sec. 3.4 and Alg. 1; arXiv:2603.06577 Sec. 3.4; arXiv:2604.00007 Sec. 3 'Modality-specific decoding patterns'
    level: E2
    confidence: 0.55
competing_explanations: []
unknowns:
  - "Whether Omni-Diffusion ranks text and speech positions with one global entropy ranking (Idea 5 premise): Sec. 3.4 says 'entropy-based decoding consistent with Dream' and describes a single mask sequence, but I did not read the code. The pre-infilling index (0.25L in the ideas file) was lost in HTML conversion."
  - "UVC (ECCV 2026, THU-BPM) cited in the ideas file: not found by any query. Treat as unverified, not as absent."
  - "ICLR 2027 / NeurIPS 2026 OpenReview submissions: not searchable here."
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Novelty audit: Ideas 1-5

## Summary

| Idea | Verdict | Conf. | Closest work that a reviewer would cite against us |
|---|---|---|---|
| 1 GATE | NOVEL-WITH-NARROW-DELTA | 0.60 | Dropout Decoding (NeurIPS 2025), 2412.06474; DiSP 2602.22246 for the MDLM premise |
| 2 Boundary prior / PPC | NOVEL-WITH-NARROW-DELTA (hypothesis and fixes largely known) | 0.50 | PC-Sampler/Uncode 2508.13021 plus Omni-Diffusion 2603.06577 |
| 3 Two-way fusion | NOVEL-WITH-NARROW-DELTA (assembly only) | 0.55 | VisualGPTScore 2306.01879 / UniDisc 2503.20853 |
| 4 Equivalence-class confidence | NOVEL-WITH-NARROW-DELTA | 0.65 | GSD 2508.07747 (LANTERN 2410.03355 first) |
| 5 Text leads speech | NOVEL-WITH-NARROW-DELTA | 0.55 | DiffuSpeech 2601.22889 |

No idea is ANTICIPATED outright. In all five the narrow delta is a measurement or an assembly, not a new principle. Absence of hits is weak evidence: the arXiv API's phrase search returned zero entries for many sensible queries, Semantic Scholar was rate-limited throughout, and OpenReview could not be queried. Residual risk is highest for Ideas 1 and 2 (active areas, with two 2026 papers directly adjacent).

ID check: all 32 arXiv ids in the ideas file that I tested resolve to the stated papers (arXiv API id_list, 2026-10-27). Notes: 2508.13021 is one paper with several titles (v1 "PC-Sampler: Position-Aware Calibration...", v4 "Empirical Analysis of Decoding Biases in Masked Diffusion Models"; "Uncode" is the method name in later versions); 2306.01879 (VisualGPTScore, "id from memory") is correct; 2602.02927 is titled "Training-Free Self-Correction for Multimodal Masked Diffusion Models" ("FreeCorrection" is the repo name). UVC could not be verified (see unknowns). IDs 2610.15227 and 2610.20818 resolve (Luo; Yu) but I did not read them.

---

## Idea 1. GATE: reliability-gated conditioning

**Falsifiable sentence.** In a unified MDM with discrete conditioning tokens, a per-token score (masked log-likelihood of the token given the rest, minus the same with the other modality masked) detects corrupted conditioning tokens with AUROC >= 0.8, and masking the flagged set during decoding recovers more of the corruption-induced loss than a random gate of equal size.

**Searched (query log, abridged).** arXiv API: masked diffusion + corrupted conditioning; + missing modality; discrete diffusion + robust + multimodal + noisy; unified + masked + purification; diffusion language + visual tokens + unreliable; + image corruption; MaskGIT + robust/corrupted; diffusion language + noisy image; remasking + conditioning + image; multimodal + modality dropout; diffusion VLM hallucination training-free; multimodal + masked diffusion + perturbation (19 queries). WebSearch: "masked diffusion multimodal corrupted image conditioning remask unreliable input tokens"; "Dropout Decoding ..."; "unified masked diffusion marginalize corrupted conditioning [MASK] missing evidence"; "robustness of multimodal diffusion language models to image corruption MMaDA LLaDA-V"; "discrete token image purification MaskGIT VQ re-infill"; "self-correction multimodal masked diffusion"; "UVC ..."; "noisy prompt typo robustness masked diffusion T2I"; "Self-Purification backdoors MDLM"; "pseudo-likelihood masked LM token anomaly PMI"; "dMLLM robustness image perturbation occluded 2026"; "openreview ICLR 2027 ...".

**Closest works read (E2).**
- **DiSP, Wan et al., arXiv:2602.22246v1 (Feb 2026).** On LLaDA-V and LaViDa, "selectively masking certain vision tokens at inference time can neutralize a backdoored model's trigger-induced behaviors"; the rationale states MDLMs "can flexibly take partially masked inputs" (Introduction). Token choice uses a Fisher-Jacobian saliency score (Eq. 3-8, Hutchinson probes, gradient w.r.t. visual embeddings), not likelihood of the token. Masking is applied to continuous projector embeddings (the mask-token embedding replaces the visual embedding). The use is to rewrite responses for a poisoned training set, then fine-tune. Evaluated on backdoor ASR and MMMU, with a random-drop and a pruning baseline. Left: no natural corruption, no detector AUROC, no discrete-token likelihood score, no marginalise-versus-impute comparison, no text-side conditioning, no generation tasks.
- **Dropout Decoding, Fang et al., arXiv:2412.06474v2 (NeurIPS 2025).** AR LVLMs. Visual-token epistemic uncertainty from projecting tokens to text space; selective dropout with an ensemble over K masks; random-masking ablation (Table 4) and a high-confidence-masking ablation exist. Aims at hallucination (CHAIR, THRONE, MMBench), not corrupted input. Left: diffusion, discrete conditioning tokens, in-distribution [MASK] semantics, detection accuracy, imputation arm.
- **UniDisc, arXiv:2503.20853v1, App. G.1 and Fig. 8/20.** Zero-shot "editing" of corrupted and mismatched image-caption pairs: COCO objects overlaid on images, LLM-corrupted captions, random masking of both inputs and re-unmasking, best of n selected by the model's own likelihood. Qualitative figure only; no metric, no per-token score, no gate. This is the nearest demonstration of the repair behaviour and a reviewer on this model will know it.
- **FreeCorrection, arXiv:2602.02927v1.** Remasks the model's own generated tokens (outputs); T2I and multimodal understanding. Input-side gating not addressed.
- Searched-and-not-found: any MaskGIT/MUSE/unified-MDM paper on corrupted conditioning, missing-modality inference, or VQ-token purification. Related but different: MDiff4STR (scene text recognition, token replacement noise), MIM-OOD (2307.14701, masked image modelling for OOD detection in medical images, image-side anomaly scoring, not a conditioning gate), Token-Critic (2209.04439, scores generated tokens).

**Difference matrix (S same, P partial, D different).**

| Work | Question | Mechanism | Method | Evidence | Scale | Result |
|---|---|---|---|---|---|---|
| DiSP | P (masking inputs in MDLM) | P (mask visual tokens) | D (gradient saliency, continuous embeds, fine-tune) | D (backdoor ASR) | P (8B) | D |
| Dropout Decoding | P (uncertainty-gated input masking) | P | D (AR, text-space projection, ensemble) | D (hallucination) | P | D |
| UniDisc G.1 | P (repair corrupted pair) | P (random mask, re-unmask, own likelihood) | D (no score, no gate) | D (qualitative) | P (1.4B, same model) | n/a |
| FreeCorrection | D (outputs) | P (remasking) | D | D | P | D |

**Verdict: NOVEL-WITH-NARROW-DELTA, confidence 0.60.** The idea that a masked diffusion model can hide visual input tokens at inference is established (DiSP, UniDisc). Not found: a likelihood-ratio reliability score on discrete conditioning tokens, a clean-calibrated false-alarm gate, detection AUROC against known corrupted-token maps, and the marginalise-versus-impute comparison.

**Defensible claim (one sentence).** We measure whether a unified MDM's own masked pointwise-mutual-information score detects corrupted discrete conditioning tokens (image and text) and compare withdrawing them to [MASK] (marginalise) with re-infilling them (impute) at matched forward passes, with a false-alarm-controlled threshold calibrated on clean data.

**Most likely cited against us:** Dropout Decoding (2412.06474), with DiSP for the "masked inputs are in-distribution for MDLMs" premise and UniDisc G.1 for the repair behaviour. Residual risk: the cluster is active (three relevant papers in nine months); a concurrent submission on "input remasking" would not surface through the tools used.

**References to cite (verified ids).**
1. Fang, Y. et al. 2025. Enhancing Vision-Language Model Reliability with Uncertainty-Guided Dropout Decoding. arXiv:2412.06474v2 (NeurIPS 2025).
2. Wan, G. et al. 2026. Self-Purification Mitigates Backdoors in Multimodal Diffusion Language Models. arXiv:2602.22246v1.
3. Swerdlow, A. et al. 2025. Unified Multimodal Discrete Diffusion. arXiv:2503.20853v1.
4. Ouyang, Y. et al. 2026. Training-Free Self-Correction for Multimodal Masked Diffusion Models. arXiv:2602.02927v1.
5. Salazar, J. et al. 2020. Masked Language Model Scoring. arXiv:1910.14659v3 (pseudo-log-likelihood scoring that the score builds on); optional: Lezama, J. et al. 2022. Improved Masked Image Generation with Token-Critic. arXiv:2209.04439v1.

---

## Idea 2. Inherited boundary prior and positional prior calibration

**Falsifiable sentence.** In text-initialised unified MDMs, early commit maps over image tokens show a first/last-row excess (>= 1.5x) that is absent in a from-scratch model (UniDisc), and a null-prompt-calibrated positional prior removes the top/bottom duplication without the hand-set penalty.

**Searched.** arXiv API: boundary bias + masked diffusion; position bias + diffusion language + decoding; decoding order + unified + masked diffusion; low-discrepancy + masked + image; MaskGIT + scheduler; positional prior + masked diffusion; position penalty + image + diffusion. WebSearch: "unified masked diffusion repeated top bottom patterns decoding order inherited from text"; "positional bias image token unmasking order MMaDA Lumina-DiMOO raster"; "masked diffusion decoding position prior calibration null prompt ... text-initialized"; "Omni-Diffusion position penalty OR repetitive patterns ..." (11 queries).

**Closest works read (E2).**
- **Omni-Diffusion, arXiv:2603.06577v2, Sec. 3.4.** The authors themselves state the hypothesis: repetitive patterns arise "because the model tends to decode mask tokens from the beginning and the end of the sequence towards the center, a phenomenon discussed in prior studies [21]" (ref [21] = PC-Sampler, 2508.13021), and "simultaneous decoding at both ends ... can result in identical patterns appearing in the top and bottom regions". The fix is a logit scale-down on the last N tokens early on. Tab. 6 shows quality drops without it. Not tested: the cause. So the mechanism M1 of the ideas file is not new as a hypothesis; the test of it is.
- **PC-Sampler/Uncode, arXiv:2508.13021v4.** Text only (LLaDA-8B-Instruct, LLaDA-1.5, Dream-7B; GSM8K, MATH500, code, Sudoku). Rigid Boundary Bias documented with unmasking-probability heatmaps (Fig. 2); positional trajectory prior is a hand-set exponential weight with strength parameter; a semantic-informativeness prior calibrates with corpus token frequencies (Appendix A.14 'Impact of Calibration Corpus'). So "calibrate with a corpus" exists for tokens, not for positions, and not for images. No image or multimodal experiment.
- **Halton, arXiv:2503.17076v1.** Fixed low-discrepancy order replacing confidence in MaskGIT, class-to-image and text-to-image; motivated by clustering of high-confidence tokens, mutual-information analysis. Not unified, not text-initialised, not content-adaptive.
- **LaViDa-O, arXiv:2509.19244v3, Sec. 3 'Stratified Random Sampling'** and **Sparse-LaViDa, arXiv:2512.14008v2 (Sec. 3)**: image generation uses a data-independent hierarchical spread order instead of confidence because "high-confidence tokens tend to cluster around already unmasked tokens". This is the baseline that already sidesteps the issue in two unified MDMs.
- **UniDisc, arXiv:2503.20853v1, App. G.2:** "UniDisc has [no] strong positional bias ... is positionally invariant" (concept segmentation over timesteps). So the from-scratch control is supported qualitatively by the UniDisc authors.
- **DPRM, arXiv:2604.24357, App. C-I:** uses Omni-Diffusion as a host (keeps its top-p, repetition and position penalties), reorders visual positions by a CLIP-reward lookahead. A negative result is reported: order values learned by phase and confidence did not transfer across prompts. Different mechanism and aim; shows Omni-Diffusion ordering is already a target of concurrent work.
- **Chatterbox-Flash, arXiv:2605.30748v3:** subtracts a block-level marginal token distribution from confidence (speech); a prior-calibration cousin for tokens.

**Difference matrix.**

| Work | Question | Mechanism | Method | Evidence | Scale | Result |
|---|---|---|---|---|---|---|
| Omni-Diffusion Sec. 3.4 | S (why top/bottom repeats) | S (boundary-first, both ends) | D (hand-set penalty) | P (ablation only) | S (8B) | P |
| PC-Sampler/Uncode | P | S (boundary bias) | P (position prior; hand-set) | D (text benchmarks) | P | D |
| Halton | P (clustering of confidence) | D | D (fixed order) | P (images) | P | D |
| LaViDa-O / Sparse-LaViDa | P | D (clustering, not boundary) | D (stratified order) | P | S | D |
| UniDisc App. G.2 | P (positional invariance) | S (control) | n/a | D (qualitative) | P | S |
| DPRM-Omni | P | D | D (reward lookahead) | P | S | D |

**Verdict: NOVEL-WITH-NARROW-DELTA, confidence 0.50.** What is left open: (a) a controlled test of the inheritance hypothesis (commit maps in text-initialised versus from-scratch models, raster transposition); (b) a positional prior calibrated on null prompts rather than set by hand; (c) top/bottom duplication as a measured harm. A reviewer will say the mechanism is the Omni-Diffusion authors' and the correction is Uncode's applied to images, so only (a) is clearly empty.

**Defensible claim.** First controlled test of whether the sequence-boundary decoding prior of text-initialised unified MDMs transfers into the image-token span, using commit maps, a from-scratch control and a raster-transposition intervention, with a null-prompt-calibrated positional correction compared against Omni-Diffusion's position penalty, stratified order and Halton order at matched steps.

**Most likely cited against us:** PC-Sampler/Uncode (2508.13021), together with Omni-Diffusion (2603.06577), which states the hypothesis.

**References.**
1. Huang, P. et al. 2025. Empirical Analysis of Decoding Biases in Masked Diffusion Models (PC-Sampler/Uncode). arXiv:2508.13021v4.
2. Li, L. et al. 2026. Omni-Diffusion. arXiv:2603.06577v2.
3. Besnier, V. et al. 2025. Halton Scheduler for Masked Generative Image Transformer. arXiv:2503.17076v1 (ICLR 2025).
4. Li, S. et al. 2025. LaViDa-O. arXiv:2509.19244v3 (and Sparse-LaViDa arXiv:2512.14008v2).
5. Swerdlow, A. et al. 2025. UniDisc. arXiv:2503.20853v1 (App. G.2).

---

## Idea 3. Two-way evidence fusion

**Falsifiable sentence.** In one unified MDM, inverse-variance fusion of the two null-debiased directional estimates (text given image, image given text), with sequential mask allocation, beats either direction at equal network calls on SugarCrepe, and best-of-N selection by the fused score beats random-of-N.

**Searched.** arXiv API: masked diffusion + image-text matching; discrete diffusion + image-text retrieval; unified + masked diffusion + compositionality; diffusion language + winoground; ELBO + masked diffusion + retrieval; generative classifier + masked diffusion. WebSearch: VisualGPTScore id; "generative image-text matching masked diffusion both directions SugarCrepe"; "discrete diffusion ELBO variance reduction complementary masks"; "diffusion classifier adaptive allocation / sequential test"; "unified MDM as its own verifier best-of-N"; "PMI estimation masked diffusion null condition"; "diffusion LM zero-shot classifier ELBO multimodal"; "inverse-variance weighting bidirectional VLM score"; "cycle consistency text-to-image captioning reranking unified"; "Janus/Chameleon image-text matching likelihood" (16 queries).

**Closest works read (E2).**
- **VisualGPTScore, Lin et al., arXiv:2306.01879v4 (ICML 2024).** Scores image-text by P(text | image) from generative VLMs; derives test-time debiasing by the ratio of language priors (blind-text prior); shows ARO-type benchmarks are solvable by P(text) alone. One direction (text given image). So null-prior debiasing of the text direction is known and named.
- **DiffusionITM, Krojer et al., arXiv:2305.16397v3.** Stable Diffusion as image-text matcher; "overcomes the asymmetry between image and text retrieval ... via unconditional normalization" (error conditioned on text divided/subtracted by unconditional error). So null-condition debiasing of the image direction in a diffusion model is known. Continuous diffusion, one direction.
- **UniDisc, arXiv:2503.20853v1, Sec. 4.3 and Fig. 7/13.** Evaluates image retrieval p(x_img | x_txt), text retrieval p(x_txt | x_img) and joint retrieval p(x_img, x_txt) over 16 random negatives (Winoground and DataComp1B), finds CFG and denoising steps matter strongly. No null-term debiasing, no variance weighting, no hard negatives (SugarCrepe not used), no best-of-N.
- **DUEL, arXiv:2603.01367v2:** exact likelihood under deterministic unmasking for text MDMs; a possible replacement for the Monte Carlo ELBO, no multimodal use found.
- Adjacent, abstract level: Diffusion Classifier (2303.16203) staged elimination of classes with fewer samples (the sequential-allocation precedent); CycleReward (2506.02095, round-trip captioning/T2I verification with separate models, ICCV 2025); MI-TUNE (2405.20759, PMI from a pretrained denoiser for alignment fine-tuning); LLaDA 1.5 VRPO (2505.19223, shared masks and variance analysis of ELBO estimates, for training).

**Difference matrix.**

| Work | Question | Mechanism | Method | Evidence | Scale | Result |
|---|---|---|---|---|---|---|
| VisualGPTScore | P (debiased generative matching) | P (null prior) | D (AR, one direction) | P (retrieval/compositional) | P | D |
| DiffusionITM | P | P (unconditional normalisation) | D (continuous, one direction) | S (GDBench, Winoground) | P | D |
| UniDisc Sec. 4.3 | P (both directions, joint) | P (ELBO scoring) | D (no PMI, no fusion) | P (random negatives) | S (same model) | P |
| Diffusion Classifier | D | P (staged allocation) | D | D | D | D |
| CycleReward | P (two-direction verification) | D (two models) | D | D | D | D |

**Verdict: NOVEL-WITH-NARROW-DELTA, confidence 0.55.** Every ingredient is published (null debiasing per direction, bidirectional scoring in UniDisc, variance-aware ELBO estimation, staged sample allocation, best-of-N verification). What I did not find is their assembly inside one unified MDM with inverse-variance fusion and a sequential stopping rule. The delta is an assembly, which is exposed to a reviewer judgement of "incremental"; I report the facts only.

**Defensible claim.** For one unified masked-diffusion model, we estimate pointwise mutual information in both conditioning directions with shared-mask Monte Carlo ELBOs, fuse the two by inverse-variance weights and spend masks adaptively, and report accuracy against network calls on hard-negative compositional benchmarks and as a best-of-N selector.

**Most likely cited against us:** VisualGPTScore (2306.01879) for the debiased generative score, with UniDisc (2503.20853) for the unified-MDM bidirectional evaluation.

**References.**
1. Lin, Z. et al. 2024. Revisiting the Role of Language Priors in Vision-Language Models. arXiv:2306.01879v4 (ICML 2024).
2. Krojer, B. et al. 2023. Are Diffusion Models Vision-And-Language Reasoners? arXiv:2305.16397v3 (NeurIPS 2023).
3. Swerdlow, A. et al. 2025. UniDisc. arXiv:2503.20853v1.
4. Li, A. C. et al. 2023. Your Diffusion Model is Secretly a Zero-Shot Classifier. arXiv:2303.16203v3 (ICCV 2023).
5. Hsieh, C.-Y. et al. 2023. SugarCrepe. arXiv:2306.14610v1 (benchmark); optionally Turok, G. et al. 2026. DUEL. arXiv:2603.01367v2.

---

## Idea 4. Equivalence-class confidence for visual and speech tokens

**Falsifiable sentence.** Replacing max-probability by the best soft-class mass (class kernel built from decoded patch similarity) as the commit score changes the commit ranking (Kendall tau < 0.8 early) and improves T2I quality at 8-16 steps beyond a matched-entropy temperature-smoothing control.

**Searched.** arXiv API: speculative + masked + image + tokens; codebook + confidence + unmasking; MaskGIT + scheduler; plus WebSearch: "Grouped Speculative Decoding ICCV 2025 arXiv"; "masked image generation confidence unmasking codebook similar tokens cluster probability mass"; "semantic entropy token level visual tokens codebook equivalence class masked diffusion unmasking order"; "cluster-level or group-level confidence parallel decoding discrete image tokens"; "visual redundancy controlled decoding dMLLM"; "masked generative image sampling aggregate probabilities of similar codebook tokens ... Meissonic Lumina-DiMOO"; "speculative decoding discrete diffusion image relaxed acceptance latent neighbor" (10 queries).

**Closest works read (E2).**
- **LANTERN, Jang et al., arXiv:2410.03355v3 (ICLR 2025).** Defines "latent proximity" (tokens close in latent space are interchangeable; resampling each token uniformly from its 100 nearest neighbours leaves images intact), and relaxes speculative-decoding acceptance by aggregating the probabilities of a candidate's nearest neighbours (Sec. 4.1-4.2). AR visual models only; acceptance, not position selection.
- **GSD, So et al., arXiv:2508.07747v1 (ICCV 2025).** Diagnoses that image tokens have "inherent redundancy and diversity" giving "relatively low and uniformly distributed next-token probabilities"; partitions the vocabulary into clusters and accepts on grouped probability mass (Eq. 2-3, Theorem 1); reports static embedding-distance clustering (t-SNE of visual token embeddings, Fig. 3) is insufficient so uses context-aware dynamic clustering. This is the exact premise of Idea 4 (spread over equivalent codes looks like uncertainty), for acceptance in AR.
- Position-selection work in dMLLMs: VRCD (2605.25820, abstract) and VIG-Sampler (2608.26580, abstract) change which positions to commit using attention to image tokens; text-output decoding, not code-equivalence confidence. Uncode's semantic-informativeness prior (2508.13021) reweights by token frequency (text). Chatterbox-Flash (2605.30748) subtracts the block marginal token distribution (speech), a prior-calibration, not a geometry one. CLAD (2605.29607, abstract via search) clusters adjacent confident positions (positional, text).
- Not found: any MaskGIT or unified-MDM sampler that aggregates probability over codebook-similar tokens to rank positions, for images or speech. IAR (2501.00880) and coarse-to-fine (2503.16194) use codebook clusters at AR training time (read at abstract level only).

**Difference matrix.**

| Work | Question | Mechanism | Method | Evidence | Scale | Result |
|---|---|---|---|---|---|---|
| LANTERN | P (confidence spread over interchangeable codes) | S (aggregate neighbour mass) | D (AR acceptance) | D | P | D |
| GSD | S (low top-1 from redundancy) | S (grouped mass) | D (acceptance, dynamic clustering) | D | P | D |
| VRCD / VIG-Sampler | P (position selection in dMLLM) | D (attention) | D | D | P | D |
| Uncode | P | D (frequency prior) | P | D (text) | P | D |
| Chatterbox-Flash | P | D (marginal subtraction) | P | D (speech TTS) | P | D |

**Verdict: NOVEL-WITH-NARROW-DELTA, confidence 0.65.** The principle (aggregate mass over a latent-proximity set) is published twice for AR acceptance; its use as the commit score for position selection in masked diffusion is not found. GSD's finding that static embedding-distance groupings fail is a published caution for the kernel construction, not a novelty issue.

**Defensible claim.** We use codebook-equivalence-class mass as the confidence for position selection in masked-diffusion sampling of image (and speech) tokens, and test it against a matched-entropy temperature-smoothing control at few steps.

**Most likely cited against us:** Grouped Speculative Decoding (2508.07747), preceded by LANTERN (2410.03355).

**References.**
1. Jang, D. et al. 2025. LANTERN. arXiv:2410.03355v3 (ICLR 2025).
2. So, J. et al. 2025. Grouped Speculative Decoding for Autoregressive Image Generation. arXiv:2508.07747v1 (ICCV 2025).
3. Besnier, V. et al. 2025. Halton Scheduler. arXiv:2503.17076v1.
4. Seo, D. et al. 2026. Chatterbox-Flash. arXiv:2605.30748v3.
5. Yuan, Y. et al. 2026. Visual-Redundancy-Controlled Parallel Decoding for dMLLMs. arXiv:2605.25820v2.

---

## Idea 5. Text leads speech in one canvas

**Falsifiable sentence.** Under Omni-Diffusion's default sampler, more than 30% of speech tokens are committed before their aligned text tokens, and gating speech commitment on aligned text lowers the WER between Whisper's transcript of the speech and the generated text at matched steps.

**Searched.** arXiv API: spoken dialogue + masked diffusion; text + speech + unified + diffusion language; codebook + confidence + unmasking; plus WebSearch: "masked diffusion jointly generates text response and speech response simultaneously"; "speech-text consistency spoken dialogue models text leads speech WER between transcript and text diffusion"; "modality-calibrated confidence rank normalization vocabulary sizes multi-modality masked diffusion"; "interleaved text-speech masked diffusion" (7 queries); last-90-day arXiv date-bounded scan "masked diffusion + speech".

**Closest works read (E2).**
- **DiffuSpeech, Lou et al., arXiv:2601.22889v1 (Jan 2026).** "Jointly generates reasoning traces and speech tokens through iterative denoising" in one masked diffusion process on LLaDA with a unified vocabulary; sequence format is [task, conditioning, thinking, reply]; inference unmasks the top-k most confident positions by a single confidence over the vocabulary (Alg. 1, Sec. 3.4). TTS WER by Whisper-large-v3. Left: no analysis of which modality commits first, no text-to-speech consistency measurement, no gating, no calibration across vocabularies. This is the main anticipating-adjacent work for the one-canvas setting.
- **Omni-Diffusion, arXiv:2603.06577v2, Sec. 3.4.** Special token pre-infilling places [begin-of-speech] at a fixed index so text is generated in the first segment and speech in the rest, within one mask sequence; the stated aim is "the model can explicitly attend to text content during speech generation". Text-speech agreement is not measured in the text I grepped (no WER-between-transcript-and-text found). Decoding is "entropy-based ... consistent with Dream"; I did not verify per-modality ranking.
- **Dynin-Omni, arXiv:2604.00007v1, Sec. 3 'Modality-specific decoding patterns'.** Text and speech both decoded with a block-wise (left-to-right blocks) strategy, images fully parallel; applied at inference only. No joint text-plus-speech response mode found in the text read; this is a different answer to the modality-scale problem (separate decoding patterns), not a calibration.
- **LLaDA-TTS, arXiv:2603.26364v1, Sec. 4.5.** Text and prompt are always-visible conditioning, only speech tokens are masked; documents emergent left-to-right unmasking and attention heads (L16-H2 / L11-H5) that align text to speech. Supplies the alignment signal; no joint canvas.
- **Chatterbox-Flash, 2605.30748v3:** prior-calibrated position scoring within speech tokens (marginal subtraction) and an early-decoding rule. In-modality calibration, not cross-modality.
- AR precedent, abstract level: Wu et al. 2025, Towards Efficient Speech-Text Jointly Decoding within One Speech Language Model, arXiv:2506.04518v3: compares joint decoding patterns, interleaved gives best alignment. Last-90-day neighbours: DiffuPlex (2610.12214, full-duplex rolling masked diffusion), "Refinement buys intelligibility" (2610.03320, MDM TTS), Revise-TTS (2610.19499, title only); none addresses cross-modality commit order.

**Difference matrix.**

| Work | Question | Mechanism | Method | Evidence | Scale | Result |
|---|---|---|---|---|---|---|
| DiffuSpeech | P (joint text-speech in one MDM) | S (global confidence) | D (no order intervention) | D (QA acc., TTS WER) | P | D |
| Omni-Diffusion Sec. 3.4 | P (text then speech in one canvas) | P (pre-infilling fixes layout) | D | D (no consistency metric found) | S | D |
| Dynin-Omni | P | D (block-wise per modality) | P (modality-specific) | D | S | D |
| LLaDA-TTS | P (alignment heads) | P | D (speech only) | P | D | D |
| Chatterbox-Flash | P (calibrated scoring) | P | P | D | D | D |

**Verdict: NOVEL-WITH-NARROW-DELTA, confidence 0.55.** The one-canvas setting is occupied (DiffuSpeech, Omni-Diffusion) and so is in-modality calibration (Chatterbox-Flash) and alignment heads (LLaDA-TTS). Not found: measurement of cross-modal commit order in a text-plus-speech canvas, text-speech disagreement as a metric for a diffusion model, or alignment-gated speech commitment. Premises not verified in this audit: that Omni-Diffusion ranks both modalities with one global score (needs code), and the pre-infilling index.

**Defensible claim.** In a masked-diffusion model that writes a text answer and its spoken version in one canvas, we measure which modality commits first, quantify text-speech disagreement as the WER between an ASR transcript of the speech and the generated text, and test a rank-normalised, alignment-gated commitment rule against the default sampler at matched steps.

**Most likely cited against us:** DiffuSpeech (2601.22889), for joint text-speech generation under a single confidence rule.

**References.**
1. Lou, Y. et al. 2026. DiffuSpeech: Silent Thought, Spoken Answer via Unified Speech-Text Diffusion. arXiv:2601.22889v1.
2. Li, L. et al. 2026. Omni-Diffusion. arXiv:2603.06577v2.
3. Kim, J. et al. 2026. Dynin-Omni. arXiv:2604.00007v1.
4. Fan, X. et al. 2026. LLaDA-TTS. arXiv:2603.26364v1.
5. Seo, D. et al. 2026. Chatterbox-Flash. arXiv:2605.30748v3 (optional: Wu, H. et al. 2025. arXiv:2506.04518v3).

---

## Last-90-day check (2026-07-25 to 2026-10-27)

Date-bounded arXiv API queries (7 themes: masked diffusion + multimodal; diffusion language + image + decoding; unified + discrete diffusion; masked diffusion + speech; MaskGIT; DLM + vision + robust; image tokens + unmasking) returned: 2610.15227 (attention probing of CFG in unified VLMs), 2607.29079 (content drift under acceleration of dMLLMs, not related to Ideas 1-5 mechanisms), 2608.26580 VIG-Sampler (position selection in dMLLMs, Idea 4 neighbour), 2610.12214 DiffuPlex and 2610.03320 (speech MDM, Idea 5 neighbours), 2609.35407 BiMoGen (bidirectional motion-text unified masked diffusion; training-time, not a likelihood fusion), 2610.20818 Intern Lumina U2. None scoops an idea. NeurIPS 2026 poster listing for VRCD (2605.25820) and a NeurIPS 2026 poster "Understanding and Enhancing Conditioning Robustness of Text to Image Diffusion Models" (continuous diffusion, neurips.cc/virtual/2026/164742, title only) were seen. OpenReview ICLR 2027 and Semantic Scholar could not be queried; residual risk stated above.

## Unverified items in the ideas file

- "UVC (ECCV 2026, THU-BPM/UVC)": two searches found nothing. Do not cite until a link is produced.
- "Omni-Diffusion T2I uses a 256-token canvas per Table 3 text": not checked here; DPRM App. C-I independently reports a 260-token template with 256 visual codes (consistent).
- Ideas 1's "MMaDA understanding path is discrete": not checked; DiSP shows LLaDA-V and LaViDa use continuous projector embeddings (consistent with the ideas file's note).
