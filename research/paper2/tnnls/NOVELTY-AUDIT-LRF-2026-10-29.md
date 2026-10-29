```yaml
agent: novelty-auditor
date: 2026-10-29
brief: novelty audit of LRF (learned reliability-aware evidence fusion), Paper 2, IEEE TNNLS target
sources_examined:
  - "arXiv abstract pages fetched: 2303.15233, 2303.16203, 2306.01879, 2404.01291, 2505.17955, 2510.26799, 2412.06474, 2603.19122, 2510.12060, 2602.02927, 2608.07006, 2405.17871, 2607.08056, 1802.04712, 2610.22380"
  - "passage-level: ar5iv 2303.15233 (timestep weighting passage); arxiv.org/html/2505.17955v3 (reweighting section, chars 0-100000 only)"
  - "search-result summaries only (E1, not opened): 2306.02050, 2102.02051, 2204.11423, 2406.04802, 2204.00102, CVPR 2022 Multimodal Dynamics (Han et al.), 2305.16397, 2011.04305, LAPS (CVPR 2024), SEPS 2511.01390, 2212.08044, 2004.13912, Brummer/FoCal, 2608.09986, 2604.23950"
  - "project files: research/paper2/posthoc/LEARNED-CEILING-REPORT-2026-10-29.md, LRF-FROZEN-2026-10-29.md, research/paper2/method/THEORY-ADDENDUM-2026-10-29.md (lines 1-120), research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md (lines 60-99)"
coverage: >
  About 45 web searches/fetches (log in section 7). Roughly 40 hits screened on title/snippet, 15 abstract pages read, 2 passages read.
  NO paper in the closest set was read in full text (E2 not reached). All comparisons are E1 (abstract) except the two passage reads.
  NOT covered: OpenReview ICLR 2027 / NeurIPS 2026 submission lists (not reachable by this search tool; two web queries returned nothing relevant),
  IEEE Xplore TNNLS/TPAMI/TIP tables of contents (search tool returns no IEEE listing pages), arXiv listing pages by date
  (only keyword search). paper2/ LaTeX has no LRF text yet (grep count 0), so the claim was taken from the two posthoc reports.
claims:
  - statement: "No work found that learns per-token weights for summing masked-diffusion per-token log-likelihood-ratio evidence in a unified text-image masked diffusion model using caption-withheld features, trained by an item-level loss."
    status: supported
    evidence: "section 7 query log; absence in 45 queries, 15 abstracts"
    level: E1
    confidence: 0.6
  - statement: "Each ingredient of LRF (learned aggregation weights over generative-classifier scores; per-instance learned weights with bag-level loss; reliability-weighted multimodal fusion; with/without-conditioning token reweighting; uncertainty-based visual token dropping; GAM shape functions) has a published precedent."
    status: supported
    evidence: "sections 2-3"
    level: E1
    confidence: 0.85
competing_explanations: []
unknowns:
  - "Zhou & Lu 2027 (Inf. Fusion 139, 104860) and any paywalled TNNLS/TPAMI paper: unread."
  - "Whether arXiv Aug-Oct 2026 holds a masked-diffusion matching paper that the keyword search did not surface."
next_test: {hypothesis: "n/a (novelty audit)", intervention: "n/a", primary_metric: "n/a", falsifier: "a read paper that learns token weights on diffusion/AR token likelihoods for caption matching", gpu_hours: 0}
```

# Novelty audit: LRF (learned reliability-aware evidence fusion), Paper 2, TNNLS

## 0. Verdict

- **Candidate, as one falsifiable sentence.** In a frozen unified masked discrete diffusion model (UniDisc 1.4B), a logistic-GAM that
  maps caption-withheld per-token features (own-context masked likelihood, image-only null, uncertainty, texture, codebook-neighbour distance,
  one-pass score, position and rank) to non-negative per-token weights, trained with an item-level logistic loss on the weighted margin,
  raises image-caption matching accuracy over the unweighted sum of per-token log-likelihood-ratio evidence under Gaussian pixel noise
  (0.778 against 0.676, cross-fitted, post hoc on M4), by keeping roughly the top fifth of tokens (central, locally homogeneous,
  confidently predicted). Mechanism: the per-token evidence is a signal whose reliability can be predicted from caption-withheld
  statistics, and the weighted sum approximates the matched filter. Stated claim status: exploratory, M4 is the discovery set, one corruption only.
- **Verdict: `incremental`. Confidence 0.70.** (0.20 that a reviewer can credibly say `anticipated`; 0.10 `novel`.)
  - What I could not find: a paper that does this specific thing (learned per-token weighting of masked-diffusion LLR evidence for
    image-text matching, in a unified text-image masked diffusion model, with caption-withheld features).
  - Why not `novel`: every component and the overall structure have a close precedent (Section 2). A TNNLS reviewer can reconstruct LRF as
    "attention-MIL pooling with a GAM scorer, applied to diffusion-classifier evidence, using CAL-style with/without-conditioning features".
    The delta is a specific combination and setting, not a new principle.
  - Why not `anticipated`: no single precedent covers the combination, and no precedent operates on a masked-diffusion token likelihood
    for caption matching.
- **Paper most likely to be cited against us by a reviewer: Ilse, Tomczak, Welling, "Attention-based Deep Multiple Instance Learning",
  ICML 2018, arXiv 1802.04712.** It is the same learning structure: a bag (item) label, per-instance (token) weights produced by a learned
  scorer from instance features, trained end-to-end on the bag-level likelihood, with weights read as interpretable. For the diffusion-classifier
  setting the nearest paper is Clark & Jaini, arXiv 2303.15233 (learned weights on diffusion scores). The relevant delta for each is below.
- **Residual risk.** Absence of hits is weak evidence. No closest paper was read in full text. IEEE/TNNLS and OpenReview listings were not
  reachable. A masked-diffusion matching paper from Aug-Oct 2026 could have been missed by keyword search. The two files in the project's
  earlier check (Zhou & Lu 2027, closed access) are still unread.

## 1. Search coverage

See Section 7 for every query. Areas: (a) quality/reliability-aware and evidential multimodal fusion; (b) token/patch selection and
pruning in VLMs and image-text matching; (c) learned aggregation of generative-model likelihood evidence (diffusion classifiers,
VisualGPTScore, VQAScore, any-order AR classifiers, masked-LM scoring); (d) corruption robustness of image-text matching; (e) GAM and
neural-additive weighting; (f) unified masked diffusion with evidence weighting; (g) last 90 days (2026-08 to 2026-10).

## 2. Closest works with the exact delta

Cell key: S = same, P = partial, D = different (relative to LRF). Evidence level E1 for all rows unless noted.

| # | Work | Question | Mechanism | Method | Evidence type | Scale | Result |
|---|---|---|---|---|---|---|---|
| 1 | Ilse, Tomczak, Welling, ICML 2018, arXiv 1802.04712 | P (classify a bag from instances) | P (learned instance weights from instance features) | P (bag-level Bernoulli log-likelihood loss; neural attention, not GAM) | D (supervised MIL on MNIST bags, histopathology) | D | D |
| 2 | Clark & Jaini, arXiv 2303.15233 (v2 2023-09-05) | P (generative model as classifier; image-text) | P (learned weights aggregating diffusion scores) | P (20-bin linear model by max likelihood on held-out labelled data; weights over timesteps, not tokens/space) | S-ish (empirical, label-supervised) | D (Stable Diffusion, Imagen) | D (about +1 % with learned weights; the paper used a fixed exp(-7t) in the main results) |
| 3 | Jeong, Uselis, Oh, Rohrbach, arXiv 2505.17955 (NeurIPS 2025 D&B) | P | P (learned timestep weights, piecewise-constant or polynomial, low-shot 5 %) | P | P | D (SD1.5/2.0/3-m) | D |
| 4 | Xiao et al., CAL, arXiv 2405.17871 (NeurIPS 2024) | D (training of VLMs) | P (token weight from logits with versus without the image; the same "conditioning-withheld contrast" idea) | D (training-time reweighting, not learned, no GAM) | D | D | D |
| 5 | Han et al., TMC arXiv 2102.02051 (ICLR 2021) / TPAMI 2022 arXiv 2204.11423; Han et al., Multimodal Dynamics, CVPR 2022 | P (reliable fusion under noise/corruption) | P (per-sample view-level and, in Multimodal Dynamics, feature-level reliability) | D (Dirichlet / Dempster-Shafer; sparse gating) | D | D (classification) | D |
| 6 | Zhang et al., QMF, arXiv 2306.02050 (ICML 2023); Cao et al., Predictive Dynamic Fusion, arXiv 2406.04802 (ICML 2024) | P (low-quality inputs, dynamic fusion with a provable argument) | P (uncertainty- or confidence-driven weights) | D (modality-level weights, uncertainty estimator) | P (theory of when dynamic beats static) | D | D |
| 7 | Fang et al., Dropout Decoding, arXiv 2412.06474 (NeurIPS 2025) | D (LVLM hallucination) | P (per-visual-token uncertainty; drop uncertain tokens) | D (inference-time ensemble over masked token sets; unlearned) | D | D | D |
| 8 | Fu et al., LAPS (CVPR 2024); SEPS arXiv 2511.01390 (ICLR 2026) | P (image-text matching) | P (select significant patches, drop redundant ones) | D (differentiable sampling in a trained ITM model; text-guided) | D | D | D |

Notes on specific cells.
- Row 1: structurally closest. LRF's difference is that (i) the instance "features" are caption-withheld scores of a frozen generative
  model, (ii) the weighted statistic is a sum of known LLR terms (not a learned feature embedding), (iii) the scorer is a spline GAM, (iv) weights
  are non-negative and the decision is scale-free. These are choices inside the MIL template. I did not find that the MIL literature
  applies it to diffusion-model likelihood evidence, but I did not search that sub-literature exhaustively.
- Row 2: Clark & Jaini state in the passage I read that learning the weights "requires label information", so they left it out of the main
  results. LRF is supervised too, so the same disclosure applies. Their weights are over diffusion timesteps, LRF's over tokens/space.
  An explicit counter-reading: the principle "learn the aggregation weights of a generative classifier's score terms by maximum likelihood /
  logistic loss" is published.
- Row 3: shows a 2025 peer-reviewed line on learned aggregation weights in diffusion classifiers, again over timesteps.
- Row 4: the closest thing to LRF's "caption-withheld" signal in spirit. Not a scoring-time method, not learned.
- Rows 5-6: the "dynamic reliability weighting improves robustness to noise/corruption" claim is established, at modality or
  feature level. TNNLS reviewers will know this family. LRF's novelty is at token level in a generative matching score.
- Rows 7-8: token- and patch-level dropping/selection by reliability or text-guided significance exists in LVLMs and ITM. LRF's "keep about
  the top fifth" will be read as selection.

### Further works that matter but are not in the top 8 (E1)

- Chen et al., Generalized Pooling Operator, CVPR 2021, arXiv 2011.04305: learns pooling coefficients over feature positions for
  image-text retrieval. Another "learned weights over instance scores" precedent in ITM.
- Lin et al., VisualGPTScore, arXiv 2306.01879 (ICML 2024): caption likelihood as the match score; PMI decomposition with a prior. The
  LLR-versus-null structure of LRF's evidence is a PMI-type quantity. I read only the abstract; per-token form not verified.
- Lin et al., VQAScore, arXiv 2404.01291: a probability of "Yes"; no per-token weighting.
- Krojer et al., DiffusionITM / GDBench, arXiv 2305.16397 (NeurIPS 2023): matching score from noise-prediction error normalised by an unconditional error.
- Li et al., Diffusion Classifier, arXiv 2303.16203 (ICCV 2023): uniform average over timesteps, no learned weighting in the abstract.
- Feng, Wei, Owens, Masked Diffusion Captioning, arXiv 2510.26799 (EMNLP Findings 2025): masked-diffusion caption likelihood used for
  image-caption matching on compositionality benchmarks (reported in a search summary; I read the abstract page, which does not state this).
- Sudakov et al., arXiv 2603.19122 (2026): any-order AR generative image classifier; averaging over token orders; notes single-order
  predictions use partial cues. Chen et al., VARC, arXiv 2510.12060: token-wise mutual information for explanation. Neither learns weights.
- Ouyang et al., arXiv 2602.02927, and arXiv 2607.08056 (July 2026, GRPO-learned generation-order controller): multimodal masked
  diffusion models with training-free or learned control. Different question (generation). Wang et al., arXiv 2608.07006 (2026-08-07):
  entropy-based evidence admission for retrieved pages in multimodal DLMs. Different object (retrieved documents, not tokens of one item).
- Jhingran, "Trust but Verify", arXiv 2610.22380 (2026-10-02): heuristic suspicious-context detection in discrete diffusion. Not learned,
  not weighting (previous project check; abstract re-read).
- Neural Additive Models arXiv 2004.13912 and kin (E1): GAM-style shape functions in neural pipelines are established; I found no GAM
  used as token weighter for a VLM. That is an absence, not a precedent.
- Classical, not searched in depth: logistic-regression fusion of log-likelihood-ratio scores (Brummer's FoCal line in speaker recognition),
  inverse-variance weighting, Fisher LDA, matched filter and Neyman-Pearson. These are the prior art for Prop 2/3 (matched-filter soft weights).
  The theory addendum itself notes that the AUROC-TV constant was not searched.

## 3. Component-by-component status

| LRF component | Prior art found | Residual novelty |
|---|---|---|
| Sum of per-token LLR evidence for matching | VisualGPTScore, DiffusionITM, Diffusion Classifier | none |
| Learning weights on a generative score's terms | Clark & Jaini (timesteps, linear, labelled held-out), Jeong et al. (timesteps) | token/space axis, nonparametric spline |
| Per-instance weights learned by bag-level loss | Ilse et al. | none in structure |
| Reliability-aware fusion under noise | TMC, Multimodal Dynamics, QMF, PDF | token level in a generative matching score |
| Weights from with/without-conditioning contrast | CAL, VisualGPTScore PMI | used as inputs to a learned weighter at scoring time |
| Token selection by reliability | Dropout Decoding, LAPS, SEPS | selection learned from caption-withheld statistics of a frozen MDM |
| GAM shape functions | NAM line | use as token weighter (absence only) |
| Matched-filter / SNR theory for gating | classical detection and fusion theory | correlated-token gating condition (Prop 2) and non-negative soft threshold (Prop 3): unsearched as theory, E0 in project |
| Setting: unified masked diffusion (UniDisc), image tokens, pixel corruptions | UniDisc, Muddit and others evaluate generation and retrieval; no weighting found | this setting (absence only) |

## 4. Last 90 days (2026-08 to 2026-10)

Keyword searches for masked/discrete diffusion + image-text matching + token weighting + corruption (4 queries) returned nothing within the
window that does this. Items in the window that matter: arXiv 2608.07006 (2026-08-07, evidence admission, different object), 2607.08056
(2026-07-09, just outside, learned order controller), 2610.22380 (2026-10-02, heuristic context re-masking). No arXiv listing page and no
OpenReview ICLR 2027 / NeurIPS 2026 submission list was accessed, so this check is incomplete (stated limitation, not a negative finding).

## 5. Claims that must not be made

1. "First learned token weighting for generative image-text matching" or "first reliability-aware fusion in unified masked diffusion".
   At most: "we found none" with the search scope stated.
2. That learning aggregation weights of a generative classifier's score is new. Clark & Jaini (2023) and Jeong et al. (2025) did it over timesteps.
3. That per-instance weights trained from an item-level loss are a new learning principle (attention MIL, 2018).
4. That conditioning-withheld contrasts as a token-reliability signal are new (CAL 2024; VisualGPTScore PMI).
5. That the matched-filter / SNR optimal weight, inverse-variance weighting or logistic LLR fusion is new. Prop 2/3 may be called a
   specialisation to correlated tokens with gating, and only after the theory is itself checked; the addendum marks it E0.
6. That LRF detects corruption. The project's own finding is that z (changed code) is uninformative on noise0.1 (93 % of tokens change)
   and the z-oracle arms gain nothing.
7. "Training-free" or "zero-shot". LRF is supervised on 500 items (Clark & Jaini flag the same point).
8. Robust image-text matching in general, or any gain on jpeg10, splice128 or clean images. Only noise0.1 shows a cross-fitted gain
   (+0.102, CI +0.060 to +0.144, post hoc); the other conditions are not distinguishable.
9. Any superiority over other weighting schemes, MIL pooling, QMF/TMC-style fusion, CAL-style weights or PMI weights. None is in the
   evidence (the learned-ceiling run compared only F1-F4 and oracle arms).
10. That shape functions give an interpretable reading of single features. The project's own report notes collinearity; read groups only.
11. That spatial context is the mechanism. The group occlusion is in-sample and correlational; F4's failure is not evidence either way.
12. Any sentence that rests on M4 numbers as a method claim before the fresh preregistered fold (D0082), or that links LRF to the P null.
13. Novelty of the GAM as a token weighter beyond "we did not find one" (NAM line establishes GAM-in-neural-pipeline).

## 6. Strongest defensible novelty sentence (TNNLS)

"Prior work learns weights over diffusion timesteps for generative classification (Clark & Jaini 2023; Jeong et al. 2025) and
modality- or feature-level reliability for fusion (Han et al. 2021, 2022; Zhang et al. 2023); to our knowledge, no earlier work learns
per-token, caption-withheld reliability weights for the log-likelihood-ratio evidence of a unified masked discrete diffusion model, and
we report, as an exploratory result on one corruption (Gaussian pixel noise), that such a weighting raises matching accuracy over the
unweighted sum, together with a condition under which gating raises the evidence SNR for correlated tokens."

Every clause of "to our knowledge" is scoped to the 45-query search in Section 7. Add "exploratory" and the corruption scope in the abstract.
The sentence must be re-checked after the fresh fold and after a read of the closest papers (Ilse; Clark & Jaini; Jeong; CAL).

## 7. Query and fetch log (2026-10-29)

Web searches (standard unless noted):
1. QMF 2306.02050 "Provable Dynamic Fusion for Low-Quality Multimodal Data"
2. diffusion classifier per-token likelihood ratio learned weighting aggregation image-text matching masked diffusion
3. learned token weighting generative image-text matching likelihood noisy images robustness unified masked discrete diffusion arXiv
4. patch-level reliability weighting image-text matching noise corruption token selection vision-language arXiv
5. diffusion classifier timestep weighting learned adaptive time step selection zero-shot classification arXiv
6. Trusted multi-view classification evidential fusion TMC ETMC dynamic evidential fusion
7. token-level reliability weighting multimodal fusion uncertainty per-token evidence aggregation vision-language 2025
8. generalized additive model interpretable weighting neural pipeline spline shape functions token weights vision-language
9. diffusion classifier spatial weighting pixel patch reliability weighting denoising error classification robustness
10. benchmarking robustness image-text retrieval image corruptions Gaussian noise JPEG vision-language
11. Predictive Dynamic Fusion ICML 2024 Cao Zhang reliability multimodal
12. visual token pruning VLM FastV SparseVLM learned token importance reliability
13. Are diffusion models vision-and-language reasoners? Diffusion ITM (2305.16397)
14. Learning the Best Pooling Strategy for Visual Semantic Embedding (GPO)
15. image-text matching patch selection redundant patches learned selection fine-grained alignment token pruning
16. dynamic multimodal fusion Xue Marculescu 2204.00102
17. diffusion language model image-text retrieval masked diffusion likelihood noisy corrupted image robustness token weights 2026 (extended)
18. UniDisc 2503.20853 image-text retrieval likelihood
19. masked diffusion model image-text matching evidence token weighting caption-withheld likelihood null reranking 2026 (extended)
20. weighted pseudo-log-likelihood masked language model token weights learned scoring
21. unified multimodal diffusion understanding discriminative zero-shot classification generative likelihood UniDisc Muddit MMaDA
22. generative classifier VQ image tokens autoregressive likelihood corrupted images token-level evidence selection
23. arXiv October 2026 unified discrete diffusion image-text alignment scoring reliability-weighted tokens corruption
24. generative VLM image-text matching score token weighting learned likelihood ratio unconditional baseline PMI
25. ICLR 2027 submission OpenReview masked diffusion multimodal evidence weighting noise robustness
26. Trusted Multi-View Classification arXiv 2102.02051
27. Brummer logistic regression fusion of LLR scores FoCal
28. IEEE TNNLS reliable multimodal fusion token-level reliability weighting image-text matching noise 2025
29. Multimodal Dynamics: Dynamical Fusion for Trustworthy Multimodal Classification CVPR 2022
30. attention-based multiple instance learning patch weighting generative classifier log-likelihood evidence aggregation

Fetches: arxiv.org/abs/ for 2303.15233, 2306.01879, 2404.01291, 2303.16203, 2505.17955, 2510.26799, 2412.06474, 2603.19122, 2510.12060,
2602.02927, 2608.07006, 2405.17871, 2607.08056, 1802.04712, 2610.22380; ar5iv.labs.arxiv.org/html/2303.15233; arxiv.org/html/2505.17955v3;
arxiv.org/pdf/2303.15233 (binary, unreadable by the fetch tool, abandoned).

Tool caveats. The search tool's summaries mis-attributed one result (the learned timestep weighting was credited to Li et al.; the fetch of
2303.15233 shows it is Clark & Jaini). All attributions above are from the fetched arXiv pages, not from search summaries. The fetch tool
summarises pages with a small model, so wording of passages is paraphrase, not a quotation, except the "requires label information" point which I report as the
fetch tool's quote and have not re-checked against the PDF.
