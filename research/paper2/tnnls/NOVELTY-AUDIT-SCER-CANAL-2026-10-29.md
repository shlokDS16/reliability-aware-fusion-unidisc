```yaml
agent: novelty-auditor
date: 2026-10-29
brief: novelty audit of Paper 2 TNNLS method candidates SCER (design A), CANAL (design B) and their combination; verify VGR, CEBC, Flow-CLIP and the named anchors; last-90-days check
sources_examined:
  - research/paper2/tnnls/DESIGN-A-2026-10-29.md, DESIGN-B-2026-10-29.md (read in full); research/paper3/proposals/NOVELTY-AUDIT-2026-10-29.md (read in full)
  - arXiv API metadata and abstracts (E1): 2610.21937, 2510.26799, 1901.05287, 2306.01879, 2404.01291, 2303.16203, 2305.16397, 2609.34772, 2609.01375, 2609.01318, 2606.16667, 2605.06157, 2602.23906, 2604.01624, 2605.14570, 2510.19871, 2509.23625, 2502.20560, 1805.06549, 2604.16587, 2403.02325, 2603.01367, 2602.02927, 2406.03736, 2607.16704, 2609.23717, 2608.15971, 2305.07021 and the id-check list in section 7
  - ICML 2026 poster page of VGR (icml.cc/virtual/2026/poster/66650) and the VGR GitHub README (E1, page text only)
  - CEBC, ACL 2026 long paper 2142, PDF converted with markitdown.exe to scratchpad cebc.md; Sec. 3.1 to 3.6 read, abstract, related work and grep for guarantee/theorem (E2-partial)
  - arxiv.org/html/2510.26799 (MDC scoring section) and arxiv.org/html/2503.20853 (UniDisc) through a summarising fetch tool (E2-partial, not verbatim)
coverage: >
  NOT covered: VGR full text (the OpenReview forum returned a bot-check page twice; the GitHub README is a placeholder); CEBC Sec. 4 onward, experiments and appendix;
  full text of every paper not named above; OpenReview ICLR 2027 / NeurIPS 2026 submission lists (not accessible; one web search returned nothing relevant);
  IEEE Xplore (no access; TNNLS 2024-2026 covered only by web search snippets); CVPR/ICCV/ECCV/ACL/EMNLP proceedings only through web search and arXiv metadata.
  arXiv API queried through 2026-10-29. The fetch tool summarises with a small model, so every "no mention" below is weak evidence.
claims:
  - statement: SCER (exact shared-context ratio) is incremental: the identity and the one-position comparison are classical (Goldberg 1901.05287 for text MLMs), image-conditioned masked diffusion captioners are already scored on SugarCrepe by whole-caption likelihood (MDC 2510.26799), and no paper found does shared-context edit-position scoring for an image-conditioned or unified masked diffusion model.
    status: supported (search-level)
    evidence: sections 2 and 5
    level: E1/E2-partial
    confidence: 0.65
  - statement: CANAL is incremental, leaning anticipated at the headline level "detect and fix visual hallucinations by remasking spans in a masked diffusion VLM" (VGR, ICML 2026), with real but narrow deltas (external captions, explicit channel posterior, false-edit risk control with a theorem).
    status: supported (search-level; VGR unread beyond abstract)
    evidence: sections 3 and 5
    level: E1/E2-partial
    confidence: 0.6
  - statement: "CEBC" exists and is verified: Mishra, Kumar, Shah, Bhattacharya, Foltin, "CEBC: Conformal Evidence-Bounded Control for Low-Hallucination Vision-Language Generation", ACL 2026 long, pp. 46193-46206, DOI 10.18653/v1/2026.acl-long.2142 (no arXiv version). It is a detector-driven editor, not a masked-diffusion method, and states no finite-sample theorem in the parts read.
    status: supported
    evidence: aclanthology.org/2026.acl-long.2142 and PDF; grep for guarantee/theorem found none in the paper's own claims
    level: E2-partial
    confidence: 0.85
  - statement: Flow-CLIP (arXiv 2610.21937, Wei, Zhu, Cao, 2026-10-15) exists and is a trained dual-encoder scoring method; it is not a threat to SCER or CANAL.
    status: supported
    evidence: arXiv API abstract
    level: E1
    confidence: 0.85
  - statement: No scoop of SCER, CANAL or their combination was found in the last 90 days (2026-07-31 to 2026-10-29) on arXiv listings reachable through the API; ICLR 2027 and NeurIPS 2026 submissions were not searchable.
    status: supported, weak (absence)
    evidence: query log Q1 to Q40
    level: E1
    confidence: 0.5
competing_explanations: []
unknowns:
  - Whether VGR needs training (the GitHub release plan lists "LLaDA-VGR training code" and a "VGR-Instruct dataset", which suggests a trained model; the poster page does not say) and whether it ever edits captions written by another model.
  - Whether any ICLR 2027 submission (double-blind, invisible) does shared-context scoring or masked-diffusion caption auditing.
  - Whether the MDC text, read in full, scores only differing positions anywhere (the fetch summary says whole-caption sums).
next_test: {hypothesis: n/a (novelty audit), intervention: "paper-reader on VGR (once code or PDF is reachable through Shlok's browser), CEBC Sec. 4-6, MDC Sec. 3.2 and appendix, Woodpecker Sec. 3", primary_metric: n/a, falsifier: "VGR or a 2026 paper contains a training-free, external-caption, word-level edit of a masked diffusion VLM; or MDC/another paper scores minimal pairs by the edit-position conditional", gpu_hours: 0}
```

# Novelty audit: SCER, CANAL and their combination (Paper 2, IEEE TNNLS)

Evidence tags: E1 abstract, listing or page text; E2-partial a method section read through a converter or summarising fetch (not a verbatim full-text reading). Nothing here is E3 or higher. Rule followed: this file says only whether the work is new; it does not suggest how to rescue anything. "Claims not to make" are limits on what can be said, not repairs.

## 0. Verdicts

| candidate | verdict | confidence | paper most likely cited against |
|---|---|---|---|
| SCER (design A) | **incremental** | 0.65 | Goldberg 1901.05287 for the mechanism; Feng, Wei, Owens 2510.26799 (MDC) for "masked diffusion scored on SugarCrepe" |
| CANAL (design B) | **incremental, leaning anticipated** at headline level | 0.60 | Song et al., VGR, ICML 2026 (OpenReview 1knvdLwxQq) |
| SCER + CANAL combined (exact scoring plus calibrated detect/locate/repair) | **incremental** | 0.60 | VGR for the system; Goldberg for the scoring half |

Probability that a reviewer can name a paper that already does the combined system: about 0.15 (mostly unread VGR full text and invisible ICLR 2027 / NeurIPS 2026 submissions). Probability that each half separately has a close precedent a reviewer will find in a 30-minute search: SCER 0.8, CANAL 0.8.

## 1. Restated claims

**SCER.** Falsifiable sentence: for an image-conditioned masked discrete diffusion model and two captions that differ at token-aligned positions S, the difference of the model's conditional log-probabilities of the two edit spans given the shared caption context and the image, read from one softmax (k = 1) or a tree of passes (k > 1), plus a blind null from the model's own whole-image-masked state, decides which caption is correct more accurately and with fewer network passes than Monte-Carlo ELBO scoring and than full-mask one-pass scoring on SugarCrepe replace/swap and FOIL pairs. Mechanism: chain-rule cancellation of the shared context, tree-shared passes, order averaging, alpha-weighted PMI. Not `not-yet-a-claim`.

**CANAL.** Falsifiable sentence: a frozen unified masked diffusion model, reading a caption written by another system, localises (T2) and corrects (T3) a wrongly substituted word more accurately than the blind-only control and than CLIP-style word deletion, using Bayes posteriors of a one-substitution channel built from per-word slot posteriors with the image visible and masked, with a conformal-risk-control threshold bounding the expected share of correct words edited on exchangeable clean captions. Mechanism: Proposition 1 posteriors, CRC threshold, region-masking evidence maps. Not `not-yet-a-claim`.

**Combination.** The same model supplies the exact pairwise score (SCER) and the calibrated word-level audit (CANAL), with the preregistered GATE study as the analysis section.

## 2. SCER: closest five works and the exact delta

| # | work | what it does (source) | exact delta of SCER | question / mechanism / method / evidence / scale / result |
|---|---|---|---|---|
| 1 | Goldberg, "Assessing BERT's Syntactic Abilities", arXiv 1901.05287 (2019-01-16) | Text-only BERT; compares the masked-position probability of the correct versus the wrong word in minimal pairs (agreement, anaphora). E1 abstract plus the design's own description (E1) | Image-conditioned; masked diffusion with chain over multi-token spans, order averaging, tree-shared passes, blind null from a whole-modality-masked state; two-alternative image-text benchmarks | question partial; mechanism **same** (edit-position conditional); method partial; evidence different; scale different; result different |
| 2 | Feng, Wei, Owens, MDC, arXiv 2510.26799 (EMNLP 2025 Findings) | Image-conditioned masked diffusion captioner; zero-shot SugarCrepe/ARO by caption likelihood: ELBO with 1,024 masks, or a fully-masked confidence-ordered N-step chain summing true-token log-likelihoods (E2-partial, HTML through a summarising fetch). The fetch reported that all caption positions are summed and no one-softmax or edit-only variant, no localisation or correction, appears | Scores only the differing span given the shared context (no ELBO, no full-caption chain); uses a unified model with a native image-masked null; theory for when each alternative fails | question **same** (compositional discrimination by masked-diffusion likelihood); mechanism partial; method partial; evidence same (SugarCrepe); scale same; result unknown |
| 3 | Kauf and Ivanova, "A Better Way to Do Masked Language Model Scoring", arXiv 2305.10588 (ACL 2023), with Salazar et al. 1910.14659 and Abramson and Emami 2201.09377 | PLL scoring; PLL-word-l2r masks the target token and the within-word tokens to its right (abstract, E1); Abramson and Emami use PLL to compare "substitution alternatives" in forced-choice tasks (abstract, E1) | SCER's chain over a multi-token span with a fixed order is the same device as PLL-word-l2r when S is one word; delta is image conditioning, MDM, order averaging, tree sharing, blind null | question partial; mechanism **partial-to-same** for k > 1; method partial; evidence different; scale different |
| 4 | Lin, Chen, Pathak, VisualGPTScore, arXiv 2306.01879 | AR generative VLM score P(t given v) with a tempered language-prior debiasing; shows benchmark language-prior effects (E1 abstract) | Edit-restricted rather than whole-caption; MDM; the blind null is the model's trained image-masked state, not a separate text model. The alpha-PMI form and the editor-asymmetry argument (P3) are the same idea | question same; mechanism partial; method partial; evidence same; scale different; result unknown |
| 5 | Swerdlow et al., UniDisc, arXiv 2503.20853 | The model being used: trains with a random whole modality masked (p = 0.1) "to learn unconditional likelihood"; scores retrieval by joint/conditional probability and uses "the model's own likelihood as a scoring function" for edit selection; demonstrates joint correction of mismatched pairs (E2-partial, summarising fetch) | Edit-slot conditional ratio and calibrated word-level audit are not in the paper; text-only inpainting with the image fixed is not described there | question partial; mechanism partial; method different; evidence same model; result unknown |

Also close, not in the five: Li et al. Diffusion Classifier 2303.16203 and Krojer et al. 2305.16397 (image-direction likelihood scoring for continuous diffusion, zero-shot and fine-tuned); Clark and Jaini 2303.15233; DUEL 2603.01367 (exact test-time likelihood for masked diffusion by deterministic unmasking; E1); Ou et al. 2406.03736 (absorbing denoiser equals clean conditional); Young et al. 2301.00068 and Torroba Hennigen and Kim 2305.15501 (MLM conditionals are mutually inconsistent, which bears on the word "exact"); VLIS 2310.09767.

**What was not found anywhere:** an image-conditioned or unified masked diffusion model scored by the edit-position conditional ratio with tree-shared passes and a native whole-modality-masked null; a statement of "full-mask scoring is a positional bag of words" (P4) or of the flip-invariance impossibility (P5).

### SCER: claims that must not be made
1. "First likelihood scoring of a masked diffusion model on SugarCrepe/ARO": MDC did it in 2025.
2. "New identity" or "new scoring principle": the chain-rule cancellation and the edit-position conditional are Goldberg 2019 and the PLL line; PLL-word-l2r is the multi-token chain.
3. "Exact likelihood ratio" unqualified. The k = 1 number is exactly the model's conditional ratio, but it equals the log-ratio of a joint only if the model's conditionals are coherent. Young et al. 2301.00068 shows MLM conditionals generally are not, and the design's own M5 gap (0.071 nats median, 0.25 adjacent) is the evidence. Wording that survives: "exact for the model's own conditionals, with the order spread reported as the coherence error."
4. "No ELBO gap" as a novel advantage over MDC: MDC's chain heuristic is not an ELBO; the gap argument applies only to the Monte-Carlo variant.
5. PMI / alpha-debiasing as new: VisualGPTScore 2306.01879 (the design already notes this).
6. "Cheap" or "fewer passes" without the equal-pass curve (F2) against MDC's chain and Monte-Carlo variants.
7. Anything about beating BLIP-2 ITM, VQAScore or CLIP in general.
8. "Unified-only": the edit-position softmax works for any masked model with image conditioning, including an MDC-type captioner; the unified part is only the native image-masked null.

## 3. CANAL: closest five works and the exact delta

| # | work | what it does (source) | exact delta of CANAL | cells |
|---|---|---|---|---|
| 1 | Song, Chen, Tan, Li, Sun, "When Diffusion Language Models Hesitate: Detecting and Correcting Visual Hallucinations via Confidence Fluctuation" (VGR), ICML 2026 poster 66650, OpenReview 1knvdLwxQq, code github.com/SongWZ3214/VGR; no arXiv id | Multimodal diffusion LM (built on LLaDA-V per README); flags uncertain spans from the confidence trajectory across denoising steps, extracts targeted visual evidence, remasks the spans in place; fewer hallucinations and better detail recall on captioning and hallucination benchmarks (E1: poster abstract and README). Training status **unclear**: the README release plan lists "LLaDA-VGR training code" and a "VGR-Instruct dataset". Whether it edits another model's captions is not stated. **Full text not read** | Delta: (a) input is any external caption, scored by a posterior, not the model's own denoising trajectory; (b) unified model with discrete image tokens, so the image side can be masked; (c) explicit channel posterior for detect/locate/correct rather than a confidence heuristic; (d) a false-edit risk theorem. Same task family and same repair action (remask and re-infill) | question **same**; mechanism partial; method partial; evidence same (hallucination benchmarks); scale unknown; result unknown |
| 2 | Mishra, Kumar, Shah, Bhattacharya, Foltin, CEBC, ACL 2026 long, DOI 10.18653/v1/2026.acl-long.2142 | Training-free; base caption from a VLM (greedy or best-of-K); external DETR / OWL-ViT object evidence; "conformal-style" threshold set from detector scores of hallucinated mentions on a calibration set, tau = clip(Quantile_(1-alpha)(H), tau_min, tau_max) with H = detector scores of hallucinated mentions (Sec. 3.3, eqs. 3-4); minimal edits remove or revise unsupported object mentions; risk-first candidate selection; MS-COCO (80 classes), GQA, POPE; CHAIR/POPE and CIDEr/BLEU/CLIPScore (E2-partial: Sec. 3.1-3.6 read; grep finds no theorem or finite-sample statement of its own) | Different risk: CEBC calibrates on **hallucinated** mentions (a detection-side quantile, needs ground truth of hallucinations) and has no stated theorem; CANAL's CRC bounds the expected share of **correct** words edited, with a stated theorem. Different scorer: no generative model scores words in CEBC. Different scope: CEBC covers 80 object nouns, CANAL any word. CEBC edits other captioners' captions (LLaVA etc.), so "post-hoc, calibrated, minimal edit of another model's caption" is not new | question same; mechanism partial; method partial; evidence same (COCO, CHAIR); scale same; result unknown |
| 3 | Yin et al., Woodpecker, 2310.16045; Zhou et al., LURE, 2310.00754; Lee et al., Volcano, 2311.07362 | Post-hoc correction of captions or answers of an existing MLLM (Woodpecker training-free with detectors and an LLM; LURE a trained reviser; Volcano self-feedback revision) (E1 titles and abstracts) | Generative masked-diffusion verifier instead of detectors plus LLM; conformal risk control; word-level posterior. "Training-free correction of another MLLM's caption" is known (Woodpecker) | question same; mechanism different; method partial; evidence same; scale unknown |
| 4 | Li et al., ConfLVLM, 2502.20560 (EMNLP 2025); Atabuzzaman et al., IntroConformal, 2609.01375; Xu et al., BCEA, 2606.16667 | Claim-level conformal filtering of LVLM outputs with finite-sample guarantees; IntroConformal is training-free CRC using hidden-state stability and a verification probability; none edits external captions (E1 abstracts) | Word-level with a channel posterior; filtering is replaced by re-infilling; the unit and score differ. CRC applied to a per-caption loss is a routine use of Angelopoulos et al. 2208.02814 | question partial; mechanism partial; method partial; evidence same; result unknown |
| 5 | Ji et al., ReDiff 2510.19871; Li et al., RIV 2509.23625; FOIL, Shekhar et al. 1705.01359 and Defoiling Foiled Image Captions, Madhyastha, Wang, Specia 1805.06549 | Trained revision for dVLMs on synthetic or expert errors (ReDiff, RIV); FOIL defines T1/T2/T3 and Defoiling attacks detection with supervised object-based models, finding strong linguistic bias (E1 abstracts) | Training-free; posterior from slot conditionals; task definitions T2/T3 are FOIL's | question same; mechanism different; method different; evidence same (FOIL); result unknown |

Region-masking evidence maps (CANAL Sec. 3.4): token-level ablation by hiding an image region is not new. Contrastive Region Guidance (Wan, Cho et al., 2403.02325) contrasts outputs with and without a blacked-out region; VSTREAM (2604.16587, E1) defines a token-level ablation effect as the log-probability drop when a region is hidden, with a trained estimator; Zintgraf et al. 1702.04595 is the prediction-difference origin. The delta claimed in design B, that masking image tokens is in-distribution for a model trained to denoise them, is a property of the model class and was not found stated for captions. Also related and checked at abstract level: Petryk et al. 2305.07021 (token-level confidence for caption correctness, trained); MetaToken 2405.19186 and HalLoc 2506.10286 (trained token-level hallucination detectors); C-PMI 2505.19678 (conditional PMI decoding, a mitigation not a detector); 2609.34772 (DynaHall, diffusion-VLM hallucination trajectories, steering of masked answer states, not external captions); 2609.01318 (reliability evaluation of diffusion VLMs); OSCAR 2604.01624 and TRE 2607.22661 (text diffusion LLMs).

**What was not found anywhere:** a masked diffusion VLM used as an exact noisy-channel verifier of captions written by another model; a CRC bound on false-edit share for word-level re-infilling; a Bayes posterior over (substituted?, where, what) assembled from per-word slot posteriors with image visible and masked. Proposition 1's structure is the classical noisy-channel decomposition used for text error correction (Flachs et al., BEA 2019 with MLMs; Yee et al. 1908.05731 for reranking), so its novelty is only the multimodal slot posterior; it is elementary.

### CANAL: claims that must not be made
1. "First training-free detection and correction of visual hallucination with a diffusion language model": VGR (ICML 2026) is the nearest and its training status is unverified; "remask and re-infill a suspicious span" belongs to VGR (design B already says so). Do not say VGR is trained until the full text is read.
2. "First conformal guarantee for caption hallucination" or "first conformal editing of captions": CEBC (conformal-calibrated, training-free, edits other captioners' captions), ConfLVLM, IntroConformal precede. Avoid "first calibrated editor".
3. "First to edit captions written by other models": Woodpecker, LURE, CEBC do.
4. Any guarantee for captions of another captioner. The CRC theorem covers clean captions exchangeable with the calibration set; BLIP or Janus captions are not exchangeable with human COCO captions. The abstract may say "expected share of correct words edited in exchangeable clean captions" only.
5. Proposition 1 as a new theorem: Bayes' rule on a noisy channel; the equal-length restriction (53.4 % of FOIL foils) is also the scope.
6. Evidence maps as a new attribution method: CRG, VSTREAM, Zintgraf. Only the "in-distribution region marginal for a unified masked model, one pass per region" framing is available, and its exactness is limited by the measured order gap (0.25 nats for adjacent tokens exceeds the clean mean evidence of 0.199).
7. "Beats CLIP/VQAScore" unless the numbers say so; FOIL T2/T3 baselines in the literature are 2017-2018 trained models.
8. "Unified-only": VGR and ReDiff operate on diffusion VLMs without image tokens; the unified part is the image-side masking only.

## 4. The combination

The combined paper is a pipeline of three known ingredients each with a close precedent (edit-position scoring: Goldberg; remask-and-fix in a masked diffusion VLM: VGR; conformal threshold on editing: CEBC/ConfLVLM/Angelopoulos), joined on one model class where none was found joined. A reviewer who reads VGR and CEBC will see the combination as an engineering synthesis; the difference is that no paper combines an exact edit-position posterior from a generative multimodal model with a risk-controlled word-level editor, and that is a narrow statement. The preregistered GATE study is neither a prior-art risk nor a novelty source here.

Interaction risks: (i) the exactness claim of SCER is exact only for aligned equal-length edits, the same restriction as Proposition 1, so the "exact" label covers about half of FOIL foils and a minority of SugarCrepe add rows; (ii) the CRC bound is for flagging, while repair re-scores iteratively and breaks monotonicity (design B says so), so "calibrated repair" must be worded as "calibrated flagging, then repair"; (iii) MDC reports 97.8 / 77.9 / 78.5 on SugarCrepe add / replace / swap with a trained masked-diffusion captioner (relayed through a fetch summary, not independently verified), which fixes the headroom reviewers will compare against.

## 5. Last 90 days (2026-07-31 to 2026-10-29) and venues

arXiv API date-sorted queries on: masked diffusion + hallucination/remasking; diffusion language + visual hallucination; conformal + vision-language + hallucination/factuality; SugarCrepe; UniDisc; masked diffusion + caption; noisy channel + caption + correction; FOIL + localisation/correction. In the window, the relevant hits are 2609.34772 (DynaHall, 2026-09-28), 2609.01318 (reliability of diffusion VLMs, 2026-09-01), 2609.01375 (IntroConformal, 2026-09-01), 2609.23717 (BindCLIP, 2026-09-20), 2608.15971, 2610.21937 (Flow-CLIP, 2026-10-15), 2610.36466 (Nemotron-Labs-Diffusion-Uni, 2026-10-27, unrelated loss details), 2610.08833 (CoDR, text). None does shared-context scoring of image captions or masked-diffusion caption auditing of external captions. ICLR 2027 and NeurIPS 2026: OpenReview was not reachable except the VGR forum page behind a bot check; one search for ICLR 2027 returned nothing relevant. IEEE TNNLS 2024-2026: web searches returned no relevant TNNLS paper (access gap, not proof of absence). Absence is weak evidence; double-blind submissions are invisible.

## 6. Strongest defensible novelty sentences for TNNLS

**SCER alone (if kept as the method):** "For unified masked discrete diffusion models, we show that two captions differing on an aligned edit set can be compared through the edit-span conditionals given their shared context, read from one softmax for single-token edits, together with the model's own image-masked state as a blind null, and we test where this beats whole-caption Monte-Carlo and chain scoring, where it ties, and why (positional factorisation, editor asymmetry, flip invariance)."

**Combined paper:** "We use one frozen unified masked discrete diffusion model both to compare minimally different captions through shared-context edit-span conditionals and to audit a caption written by another system word by word, with a Bayes posterior of a one-substitution channel, a conformal-risk-control threshold on the expected share of correct words edited (exchangeable clean captions), and image-region masking evidence, and we report where this does and does not match trained and detector-based baselines under blind, mismatched-image and length-only controls."

Both sentences are about a model class, an estimator and a controlled comparison; the algebra is credited to Goldberg, PLL scoring, noisy-channel decoding and conformal risk control. Neither sentence uses "first".

## 7. Residual risk

- VGR unread beyond abstract and README. If its method scores external text, or is training-free with a posterior-based detector, CANAL moves to anticipated. Highest-value read.
- CEBC Sec. 4 onward not read; its conformal part may carry a statement not seen in the grep.
- MDC read only through a summarising fetch; if any variant scores only differing tokens, SCER moves toward anticipated.
- OpenReview ICLR 2027 / NeurIPS 2026 invisible; one competing dual of SCER is plausible given MDC and DUEL activity.
- The fetch tool's "no mention" answers come from a small summariser; treat as weak.
- Reference status: all arXiv ids in this file were returned by the arXiv API today except 1702.04595, 1908.05731 and 1807.08024-type secondary ids carried over from the designs (not re-checked here). VGR has no arXiv id; CEBC has no arXiv id (ACL Anthology DOI above). Flachs et al. BEA 2019 is a search-result attribution, not API-verified. Bates and Granger 1969 not checked.
- Did not check: whether Omni-Diffusion (2603.06577; Dream-7B backbone, image tokens with codebook 8,192 per a secondary summary) reports any caption likelihood or verification use.

## 8. Query log (all 2026-10-29)

Q1 arXiv API id_list 2610.21937, 2510.26799, 1901.05287, 2306.01879, 2404.01291, 2303.16203, 2305.16397. Q2 exact title of VGR. Q3 CEBC conformal caption editor (found ACL 2026-acl-long.2142). Q4 fetch icml.cc poster 66650. Q5 fetch aclanthology 2026.acl-long.2142 (page and PDF). Q6 fetch GitHub SongWZ3214/VGR. Q7 fetch OpenReview 1knvdLwxQq (bot check) and api2.openreview.net (redirect to challenge). Q8 masked diffusion VLM hallucination remasking correction training-free 2026 (extended). Q9 fetch arXiv 2602.02927. Q10 fetch arXiv 2610.21937. Q11 fetch arxiv.org/html/2510.26799 scoring section. Q12 masked diffusion likelihood ratio minimal pair single forward pass. Q13 UniDisc caption verification word-level hallucination. Q14 conformal risk control caption editing false edit rate. Q15 MLM noisy-channel error detection localisation correction. Q16 FOIL T2/T3 2024-2025. Q17 conformal factuality LVLM claim filtering. Q18 to Q21 arXiv API: masked diffusion + hallucination/caption editing; unified + discrete diffusion + verifier; conformal + caption + hallucination; foil + caption + localisation/correction. Q22 to Q26 arXiv API: diffusion + hallucination + remasking; diffusion language + visual hallucination; conformal + vision-language + hallucination; UniDisc; SugarCrepe + diffusion/masked. Q27 arXiv API id_list for 12 hallucination/conformal ids. Q28 fetch arXiv 2609.34772. Q29 Omni-Diffusion caption likelihood. Q30 multimodal MLM at foil position / VALSE. Q31 token-level PMI hallucination detection. Q32 Contrastive Region Guidance region masking evidence map. Q33 training-free post-hoc correction of external captions. Q34 Bayes-optimal posterior single-word substitution caption. Q35 arXiv API id_list for 10 abstracts (2604.16587, 2512.17189, 2403.02325, 2607.22661, 2609.20539, 2602.02927, 2603.01367, 2505.19678, 2604.04863, 2406.03736). Q36 to Q38 arXiv API: BLiMP/minimal pairs + diffusion language (0 hits); image tokens + masked + attribution + discrete diffusion; noisy channel + caption + hallucination (0 hits). Q39 conformal language editing. Q40 ICLR 2027 masked diffusion VL likelihood; diffusion LM as caption evaluator; PLL single-token substitution; hallucination correction MLM infill; image-conditioned MLM PLL Winoground; Flow-CLIP title; arXiv API id_list 2607.16704, 2609.23717, 2608.15971 and a UniDisc/MMaDA/Lumina verification search; arXiv API id_list for 20 anchor ids (2310.16045, 2310.00754, 2403.00425, 2311.07362, 2311.17911, 2311.16922, 1809.02156, 2305.07021, 2112.07566, 2204.03162, 2306.14610, 1910.14659, 2305.10588, 2402.10978, 2208.02814, 2306.10193, 2503.20853, 2310.09767, 2311.10708, 2303.15233); fetches of arXiv 2305.10588 and 2201.09377 abstracts and arxiv.org/html/2503.20853.
