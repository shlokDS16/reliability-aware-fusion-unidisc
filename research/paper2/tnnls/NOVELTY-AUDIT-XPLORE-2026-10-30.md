```yaml
agent: novelty-auditor
date: 2026-10-30
brief: IEEE Xplore extension of the 2026-10-29 LRF novelty audit; claims (a) Study 2 learned per-token reliability weighting, (b) Study 1 CRC-calibrated masked-likelihood token gating
sources_examined:
  - "Crossref public API, 10.1109 prefix and ISSN filters (TNNLS 2162-237X, TPAMI 0162-8828, TIP 1057-7149, TMM 1941-0077): titles, venues, DOIs only; no abstracts returned (22 queries, 3 returned HTTP 429)"
  - "WebSearch with allowed_domains=ieeexplore.ieee.org (the filter is not enforced; many arXiv hits returned): 13 queries, result snippets only"
  - "arxiv.org/abs/2305.07021 (Petryk et al.), ar5iv.labs.arxiv.org/html/2305.07021 (method passage, via fetch-tool summary)"
  - "arxiv.org/abs/2606.30458, 2609.01375, 2603.20721 (abstract pages)"
  - "project files: paper2-tnnls/sections/related.tex, introduction.tex (lines 30-70), references.bib (gomes2025crc), research/paper2/tnnls/NOVELTY-AUDIT-LRF-2026-10-29.md"
coverage: >
  IEEE Xplore itself was NOT searched through its own interface. The search page returned HTTP 418 to WebFetch (bot block, not bypassed), document pages
  render empty (JavaScript), and no mcp__Claude_Browser__* tools exist in this session. Substitute: Crossref, which indexes IEEE-published records by DOI
  (journals, CVPR/ICCV/WACV/ICME/ICASSP/IJCNN proceedings), so a title-level screen of IEEE content is possible; abstracts are not. About 60 hits screened
  on title; 4 read at abstract level (Petryk, 2606.30458, 2609.01375, 2603.20721); 1 read at method-passage level via a summarising fetch tool (Petryk).
  No full text read. Items in Crossref that are not yet in its index (very recent early-access papers) would be missed. OpenReview ICLR 2027 / NeurIPS 2026
  lists and arXiv listing pages were again not accessed.
claims:
  - statement: "No IEEE-published work found (title screen, 2023 to Oct 2026) that learns per-token reliability weights for the log-likelihood-ratio evidence of a masked diffusion model for image-text verification under image corruption."
    status: supported
    evidence: "section 6 query log; no title among about 60 screened matches the mechanism"
    level: E1
    confidence: 0.55
  - statement: "A peer-reviewed IEEE-indexed precedent exists for learned per-token confidence used to verify image-caption correctness (Petryk et al., WACV 2024); it works on text tokens of an autoregressive captioner, with no image corruption and no conformal step."
    status: supported
    evidence: "arxiv.org/abs/2305.07021; ar5iv method passage; Crossref DOI 10.1109/wacv57701.2024.00564"
    level: E1
    confidence: 0.8
  - statement: "No IEEE-published work found that sets a conformal-risk-control threshold on a generative model's token likelihood to filter input image tokens."
    status: supported
    evidence: "Crossref title queries 'conformal risk control' (25 hits), 'conformal vision-language' (25), 'conformal caption hallucination token' (15); none is image-token filtering"
    level: E1
    confidence: 0.55
competing_explanations: []
unknowns:
  - "Abstracts of IEEE-indexed items surfaced by title only: VAGA (TMM 2026, 10.1109/tmm.2026.3718638), Parameter-Efficient Score Calibration for Text-Image Retrieval (IJCNN 2026, 10.1109/ijcnn69854.2026.11728594), Dual Diffusion (CVPR 2025), CAIR-Net (TCSVT 2026, 10.1109/tcsvt.2026.3662605), Text-to-Image Diffusion Models are AI-Generated Image Quality Scorers (ICME 2025, 10.1109/icme59968.2025.11209391)."
  - "Whether CVPR 2026 papers (2603.20721, possibly 2606.30458 if accepted) are in IEEE Xplore; venue of 2606.30458 is unstated."
next_test: {hypothesis: "n/a (novelty audit)", intervention: "n/a", primary_metric: "n/a", falsifier: "a read paper in an IEEE venue that learns token weights on generative-model token likelihoods for image-text verification, or that sets a CRC threshold on image-token likelihood", gpu_hours: 0}
```

# Novelty audit, IEEE extension: Study 2 learned token weighting and Study 1 CRC token gating

## 0. Verdicts

| Claim | Verdict | Confidence | Paper most likely cited against us |
|---|---|---|---|
| (a) Study 2: learned per-token reliability weighting (logistic GAM, caption-withheld features) on a unified masked diffusion model's token-likelihood evidence, image-text verification under image corruption, frozen then confirmed on a preregistered fresh fold | **incremental** | 0.65 | Petryk, Whitehead, Gonzalez, Darrell, Rohrbach, Rohrbach, "Simple Token-Level Confidence Improves Caption Correctness", WACV 2024 (arXiv 2305.07021; Crossref DOI 10.1109/wacv57701.2024.00564). In the 2026-10-29 audit the top citation risk was Ilse et al. (ICML 2018); Petryk is the closest paper in an IEEE-indexed venue. |
| (b) Study 1: masked-likelihood token gating with a flag threshold set by conformal risk control, as input-level source validation of a unified masked diffusion model | **incremental** | 0.60 | Gomes, Martins, Zerva, ACL Findings 2025 (CRC threshold on masking-derived CLIPScore distributions to flag caption words; already cited as `gomes2025crc`). Not IEEE. |

Neither claim is `prior art exists` in the strict sense: no paper found does the full combination. Neither is `novel`: each ingredient has a precedent.
The IEEE search did not move either verdict from the 2026-10-29 audit (`incremental`, 0.70). It added one citable precedent (Petryk) and did not produce a scoop.

Residual risk. This is a title-level screen of Crossref, not a search of the Xplore interface, and the closest hit was read only through a summarising fetch tool.
Absence of a hit is weak evidence. Items whose abstracts were not retrievable are listed in `unknowns`.

## 1. Close hits (each: what it does, delta, concurrent?, must the related work cite it?)

### 1.1 Petryk et al., WACV 2024 (IEEE Xplore proceedings; DOI 10.1109/wacv57701.2024.00564 from Crossref; arXiv 2305.07021, submitted 2023-05-11)
- Source fact (E1, arXiv abstract page; E1+ for the method passage via the fetch tool's summary of ar5iv, not a quotation): token-level confidence (TLC) assesses whether a caption is correct for its image. TLC-A aggregates algebraic confidences (softmax score) from the autoregressive decoder of an OFA captioning model fine-tuned on MS COCO; no learning. TLC-L is a learned confidence: a 4-layer transformer encoder plus 2-layer MLP over the encoder image/instruction features and the decoder token features, trained with binary cross-entropy on whether the predicted token matches the reference, on a held-out COCO split with the captioner frozen; averaged over object words. A threshold is chosen on a validation set for 99 % precision. The fetch summary reports no image-corruption experiment, no conformal prediction, and no confidences over image tokens.
- Delta to (a): they score text tokens given the image with an autoregressive decoder; we score image codes given a caption with a masked-diffusion denoiser. Their learned estimator is a per-token correctness classifier trained on token labels; ours is a spline GAM that outputs non-negative weights for a sum of log-likelihood-ratio terms, trained on an item-level logistic loss. They have no corruption setting and no frozen-then-fresh-fold confirmation. The shared principle (learn which per-token likelihood terms to trust when verifying a caption) is theirs.
- Delta to (b): their threshold is set on a validation set for target precision, not by conformal risk control; they do not drop input tokens.
- Concurrent? No (2023, published 2024).
- Must the related work cite it? **Yes**, because it bounds the Study 2 sentence: without it, "no earlier work learns per-token ... weights" reads as broader than the record. It is not in `references.bib` (grep, 2026-10-30). The citation audit's discipline applies: a bib entry has to be verified from the proceedings page or DOI before use.

### 1.2 Reliability-gated visual tokens, arXiv 2606.30458 (Qian et al., "Cross-Resolution Semantic Transfer for Robust Text-to-Image Retrieval in Low-Resolution Surveillance", submitted 2026-06-29; venue not stated, "conference")
- Source fact (E1, abstract page): a resolution-conditioned module "estimates token reliability to suppress corrupted evidence" in a CLIP-style text-to-person retrieval model.
- Delta: a trained discriminative retrieval model with a learned reliability module, not the likelihood evidence of a generative model; degradation is resolution, not pixel noise; no frozen scorer, no preregistration.
- Concurrent? Yes in time (4 months before submission), different object.
- Cite? Optional. It supports only "learned token-level reliability under image degradation exists in discriminative retrieval". If the related work already says that for Papers in this journal and at a finer grain, one clause suffices; otherwise omit. Not verified to be in an IEEE venue.

### 1.3 Cross-modal Fuzzy Alignment Network (Deng et al.), arXiv 2603.20721, CVPR 2026 main track per the arXiv comments
- Source fact (E1, abstract page): fuzzy logic scores how reliable each text token is, so tokens with weak visual support or noise contribute less to alignment, in text-aerial person retrieval.
- Delta: text-token weighting inside a trained retrieval network; no generative likelihood; no corruption study.
- Cite? No. It does not bound a sentence the paper makes.

### 1.4 Other IEEE-indexed hits (all title-level, E0; none read)
| Title | Venue, year, DOI | Why surfaced | Verdict on relevance |
|---|---|---|---|
| Your Diffusion Model is Secretly a Zero-Shot Classifier (Li et al.) | ICCV 2023, 10.1109/iccv51070.2023.00210 | Diffusion classifier | Already cited as `li2023diffusionclassifier`; the IEEE DOI is a second route to the same paper. |
| Dual Diffusion for Unified Image Generation and Understanding | CVPR 2025, 10.1109/cvpr52734.2025.00265 | Unified diffusion model | Not close (no evidence of token weighting or corruption verification); abstract unread. |
| Text-to-Image Diffusion Models are AI-Generated Image Quality Scorers | ICME 2025, 10.1109/icme59968.2025.11209391 | Diffusion as scorer | Different question (image quality, not caption matching); abstract unread. |
| CAIR-Net: Reliability-Aware Information Routing for Robust Multimodal Object Detection Under Modality Degradation | TCSVT 2026, 10.1109/tcsvt.2026.3662605 | Reliability under degradation | Modality-level routing for detection; same family as the cited modality-reliability papers. |
| Reliability-Aware Multimodal Fusion for Multimodal Sentiment Analysis; Reliability-Aware Multimodal Emotion Recognition for Heterogeneous and Corrupted Audio-Visual Environments | ISCAIT 2026; IEEE Access 2026 (10.1109/access.2026.3699381) | Reliability-aware fusion | Modality-level; no new bound. |
| Probabilistic Attention Based on Gaussian Processes for Deep Multiple Instance Learning | TNNLS 2024, 10.1109/tnnls.2023.3245329 | Attention MIL | MIL family; Ilse et al. already covers the structural point. |
| Source-Free Image-Text Matching via Uncertainty-Aware Learning | IEEE Xplore 10740465 (venue and DOI not retrieved) | Uncertainty in image-text matching | Pair-level weighting of pseudo-pairs in domain adaptation (search snippet); no. |
| VAGA: Multi-Granular Visual-Augmented Generative Alignment for Image-Text Retrieval | TMM 2026, 10.1109/tmm.2026.3718638 | "Generative alignment" in ITR | Abstract unread. Residual risk: a TMM paper using generative likelihood for matching. Should be opened by someone with Xplore access. |
| Parameter-Efficient Score Calibration for Text-Image Retrieval: Interpretable Thresholding with Vision-Language Models | IJCNN 2026, 10.1109/ijcnn69854.2026.11728594 | Calibrated thresholding in retrieval | Abstract unread; likely score calibration, not token filtering. |
| Localized Conformal Prediction for Image Classification with Vision-Language Models; Conformal Predictions for Human Action Recognition with Vision-Language Models | EUVIP 2025; ICIPW 2025 | Conformal + VLM | Prediction sets over labels; different object from token gating. |
| Benchmarking Robustness to Text-Guided Corruptions; Towards Robustness Against Common Corruptions for Text-based Person Search | CVPRW 2023; ICICML 2024 | Corruption robustness | Benchmarks and discriminative models; no generative evidence. |

### 1.5 Non-IEEE items surfaced in this pass (for the record)
- IntroConformal, arXiv 2609.01375 (Atabuzzaman, Alexander, Thomas; submitted 2026-09-01; listed as EMNLP 2026 main): conformal risk control for LVLM factuality at the **claim** level, with hidden-state stability and verification-probability signals (E1, abstract page). Different unit (claims in generated text, not input image tokens); no corruption. Concurrent work, same family as `gomes2025crc`. Cite only if the paper wants to say CRC is applied to LVLM outputs; not needed for Study 1's sentence.
- Budgeted Conformal Evidence Acquisition, arXiv 2606.16667: seen in a search summary only (E1 at best); image-crop re-examination; no token gating.

## 2. Component status after the IEEE pass

| Component | Status | Change since 2026-10-29 |
|---|---|---|
| Learned per-token confidence for caption/image verification | Precedent: Petryk et al. 2024 (text tokens, AR captioner) | New |
| Learned weights over a generative classifier's score terms | Precedent: Clark & Jaini 2023; Jeong et al. 2025 (timesteps) | None |
| Per-instance weights from an item-level (bag) loss | Precedent: Ilse et al. 2018 | None |
| Learned token reliability under image degradation in discriminative retrieval | Precedent: arXiv 2606.30458 (June 2026), CVPR 2026 2603.20721 (text tokens) | New, arXiv only |
| Reliability-weighted fusion at modality or view level | Established (TMC, QMF, many IEEE items) | None |
| Masked-diffusion token likelihood as a per-token error signal | Precedent: arXiv 2602.02927 (self-correction); Trust but Verify 2610.22380 | None |
| CRC threshold on masking-derived scores to flag caption words | Precedent: Gomes et al. 2025 | None |
| CRC threshold on image-token likelihood of a unified masked diffusion model for input validation | Nothing found in IEEE-indexed titles or arXiv summaries | Absence only |
| Setting: unified masked discrete diffusion, caption-withheld evidence, pixel corruptions, frozen-then-fresh-fold | Nothing found | Absence only |

## 3. Sentences the related-work text may use

Current sentences in `related.tex` (lines 59 to 64) stay true but under-state one precedent and over-state the search. Wording the evidence supports, to be placed by the writer (this audit changes no paper file):

**Study 2 precedent clause** (to add before the "To our knowledge" sentence; needs a verified bib entry):
"Token-level confidences of an autoregressive captioning model, averaged or learned per token, have been used to judge whether a caption is correct for its image~\cite{petryk2024token}; that work scores text tokens given the image and reports no image-corruption setting."

**Study 2 novelty sentence:**
"To our knowledge, no earlier work learns per-token, caption-withheld weights for the log-likelihood-ratio evidence of a unified masked diffusion model and tests them on fresh images under image corruption."

**Scope sentence replacing lines 63 to 64:**
"This statement is limited to a keyword search of arXiv and of title-level records of IEEE-published journals and proceedings, logged in October 2026; it did not read full texts, the pages of IEEE Xplore itself, or the submission lists of open-review venues."
(Do not write "searched IEEE Xplore": the Xplore interface was blocked. Do not claim "no IEEE paper does this"; claim only what the title screen covered.)

**Study 1 novelty sentence** (not currently in `related.tex`; add after the Gomes sentence only if the writer wants Study 1 bounded in the same way):
"To our knowledge, no earlier work sets a conformal-risk-control flag threshold on the masked likelihood of the input image tokens of a unified masked diffusion model, with the same scope limit."

Claims that remain disallowed (unchanged from 2026-10-29): "first" or "novel principle" for learned token weighting; any statement that Petryk-style learned confidence is absent from the verification literature; any statement that IEEE Xplore was searched in full.

## 4. Concurrent-work check, last 90 days (2026-08 to 2026-10)
IEEE-indexed titles dated 2026 were screened in the Crossref lists above (TNNLS, TPAMI, TIP, TMM, plus proceedings); none matches either claim. arXiv items from the window seen in this pass: 2609.01375 (IntroConformal, claim-level CRC), 2609.03554 (WIDE, generative retrieval; surfaced in a snippet, not opened). From the 2026-10-29 audit: 2608.07006, 2610.22380. No arXiv listing page and no OpenReview ICLR 2027 / NeurIPS 2026 list was accessed. Status: incomplete, stated limitation.

## 5. Why the verdicts are `incremental` and not `novel` or `prior art exists`
- (a) Every ingredient has a published precedent, and Petryk et al. show a learned per-token confidence for caption verification at a peer-reviewed IEEE venue. The combination (image-code evidence from a masked-diffusion denoiser, caption-withheld features, GAM weights, item-level loss, corruption setting, preregistered confirmation) was not found. A reviewer can fairly say "Petryk with a different scorer", so `novel` is not defensible. No single paper does all of it, so `prior art exists` is not either.
- (b) The objects differ (image input tokens of a unified diffusion model versus caption words of CLIPScore), but the mechanism (threshold from masking-derived likelihood scores, calibrated with conformal risk control, used to flag tokens) is Gomes et al.'s. The preregistered outcome is a bounded null; the novelty is the measured object, not the mechanism.

## 6. Query and fetch log (2026-10-30)

WebSearch (standard, allowed_domains=ieeexplore.ieee.org unless noted; the filter did not restrict results):
1. reliability-weighted token fusion image-text matching under image corruption
2. diffusion model likelihood image-text matching robustness corrupted images vision-language
3. conformal risk control token filtering patch selection vision-language
4. uncertainty-aware token weighting cross-modal verification generative model likelihood IEEE Transactions on Neural Networks and Learning Systems
5. attention multiple instance learning weights generative classifier diffusion scores image-text
6. conformal risk control image-text vision-language hallucination word-level flag
7. noisy image robust image-text matching patch uncertainty weighting Gaussian noise JPEG corruption IEEE Transactions
8. discrete diffusion multimodal model image-text matching score likelihood understanding unified masked
9. diffusion classifier zero-shot classification timestep weighting learned
10. generalized additive model token importance weights vision-language fusion interpretable reliability
11. Simple Token-Level Confidence Improves Caption Correctness Petryk arXiv (no domain filter)
12. masked diffusion model image-caption verification per-token likelihood weighting image corruption robustness 2026 (no domain filter)
13. conformal risk control mask image tokens low likelihood unified discrete diffusion input validation source validation (no domain filter)

Crossref API (api.crossref.org/works, filter prefix:10.1109 unless an ISSN is named; from-pub-date 2023-01 to 2024-06):
1. TNNLS: token level reliability weighting image-text matching corruption
2. prefix: diffusion model likelihood image-text matching score
3. prefix: conformal risk control token patch filtering vision-language (HTTP 429, not retried)
4. prefix: reliability weighted token patch fusion image-text matching corrupted images (HTTP 429, not retried)
5. prefix: masked discrete diffusion unified multimodal image-text understanding
6. prefix: attention multiple instance learning instance weights generative model likelihood evidence
7. TMM: token level reliability weighting image-text matching noisy images
8. TPAMI: diffusion classifier generative likelihood zero-shot image-text compositional
9. TNNLS: conformal risk control multimodal vision-language
10. title: conformal risk control
11. title: diffusion classifier
12. title: conformal vision-language
13. title: masked diffusion image-text
14. title: image-text matching diffusion model
15. title: robustness image-text retrieval image corruptions
16. title: Source-Free Image-Text Matching via Uncertainty-Aware Learning (HTTP 429, not retried)
17. title: Dual Diffusion for Unified Image Generation and Understanding (DOI check)
18. title: Enhancing Cross-modal Semantic Consistency via Key Token Alignment for Image-text Retrieval (DOI check)
19. title: conformal caption hallucination token
20. TIP: uncertainty-aware token weighting image-text matching
21. title: reliability-aware token multimodal
22. title: likelihood image-text alignment generative vision-language score

Fetches: ieeexplore.ieee.org search page (HTTP 418, abandoned, not retried or bypassed); ieeexplore.ieee.org/document/11209993 (empty body); arxiv.org/abs/2305.07021; ar5iv.labs.arxiv.org/html/2305.07021; arxiv.org/abs/2606.30458, 2609.01375, 2603.20721.

Tool caveats. The fetch tool summarises pages with a small model, so wording from the Petryk method passage is paraphrase; the 99 % precision threshold and the TLC-L architecture should be re-checked against the PDF before a sentence leans on them. Crossref returns titles and venues, not abstracts, so every "IEEE-indexed" item in section 1.4 is judged from its title only (E0).
Ledger: papers P0136 (Petryk, E1) and P0137 (Dual Diffusion, E0) appended.
