```yaml
agent: paper-reader
date: 2026-10-14
brief: Read VRCD (2605.25820), VIG-Sampler (2608.26580), PUNT (2510.21961); state what each measures about dependence among co-committed tokens vs denoising step; verdict on "model cross-modal CMI between co-committed text and image tokens is concentrated early in a unified model's trajectory".
sources_examined:
  - arXiv:2605.25820 (VRCD, v2 header, 10 Jun 2026) md=research/sources/md/2605.25820.md pdf=research/sources/pdfs/2605.25820.pdf
  - arXiv:2608.26580 (VIG-Sampler, v1 header, 27 Aug 2026) md=research/sources/md/2608.26580.md pdf=research/sources/pdfs/2608.26580.pdf
  - arXiv:2510.21961 (PUNT, v1 header, 24 Oct 2025) md=research/sources/md/2510.21961.md pdf=research/sources/pdfs/2510.21961.pdf
coverage: >
  Titles, IDs and dates verified on the arxiv.org/abs pages. P1: full text incl. appendix A.1-A.6; Fig 3 and Fig 4 rendered and
  read by eye. P2: full text incl. appendix (motivation-study details, algorithm, extra tables); Fig 2 and Fig 4 rendered and read
  by eye. P3: abstract, Sec 2-6, Appendix B (independence stability, Fig 6-7) and the start of Appendix C read; Fig 2 and Fig 3
  rendered and read by eye. NOT covered: P3 Appendix C.2-C.4 result tables/plots (NFE/step curves, protein task) and Section D
  denoising transcripts (grepped for step-wise or multimodal content only; none found); no released code for any of the three was
  inspected (E3 not reached). All figure readings are approximate eyeball reads from rendered pages, not extracted data.
claims:
  - statement: VRCD reports a per-step quantity (VRI, Eq 2) for co-committed tokens, but it is overlap of text-token-to-image-token attention among co-committed TEXT tokens, not a model mutual-information or conditional-dependence measure.
    status: supported
    evidence: P1 Sec 3.2 Eq 2; Sec 4.3 Fig 3a, Tab 4; Appendix A.2 Tab 8 (final decoder layer, head-averaged)
    level: E2
    confidence: 0.9
  - statement: VRCD does not state or show that its per-step quantity is concentrated early in the trajectory.
    status: supported
    evidence: P1 Sec 4.3 text says only that VRCD gives "consistently lower VRI throughout decoding"; Fig 3a (L=192, FR=0.25) baseline curve is roughly flat then U-shaped (see detail); Fig 4a baseline is higher early
    level: E2
    confidence: 0.8
  - statement: VIG-Sampler reports no dependence quantity against denoising step; its step-axis figure (Fig 4) shows cumulative text-token information gain per sampler, and its dependence figure (Fig 2) is binned by attention mass or attention similarity.
    status: supported
    evidence: P2 Fig 2 caption, Fig 4 caption, Eq 3-5, Appendix motivation-study details
    level: E2
    confidence: 0.9
  - statement: PUNT is text/protein only and reports no dependence-vs-step profile; its KL test statistic is plotted against the number of previously revealed tokens within one step, and its "hierarchical generation" remark is an untested hypothesis from one example.
    status: supported
    evidence: P3 Sec 3.4 (Fig 2 right), Sec 4.3 Fig 3, Appendix B Fig 6-7; Sec 3.4 says a formal investigation "is left for future work"
    level: E2
    confidence: 0.9
  - statement: None of the three papers reports that model cross-modal CMI between co-committed text and image tokens is concentrated early.
    status: supported
    evidence: all three models generate text only; image tokens are inputs and are never masked or co-committed in P1/P2 (LaViDa, MMaDA, LLaDA-V understanding/captioning tasks); P3 has no image modality
    level: E2
    confidence: 0.85
competing_explanations:
  - "Any early/late profile of a dependence proxy is sampler-conditioned: under confidence ranking, function words and format tokens are committed first (P2 cites this; P2 Fig 4 shows baseline content-token information gain arriving late, VIG-Sampler's arriving early). A step-profile therefore mixes model dependence with which tokens the sampler chose to commit at that step."
  - "VRI and image-attention similarity are attention proxies. Attention overlap can arise from near-uniform attention on format tokens and function words (P1 Sec 3.4 says so itself), so a step profile of it may track token type, not dependence."
unknowns:
  - "P1 Fig 3a and Fig 4a numeric values (only eyeballed)."
  - "P2 Fig 4 numeric values; per-step (non-cumulative) information gain not given."
  - "P3 Fig 2 left: model and sampler setting for the plotted curves not stated in the caption or nearby text I read."
  - "Whether unread neighbours measure the quantity: Li et al. 2511.15098 (visual-token redundancy across decoding steps, described in P1 Sec 2), Kim et al. 2603.12996 (dependency-aware decoding via attention), Ringel et al. 2604.02560 (dependency-guided decoding), Kim et al. 2604.05497 (Thinking Diffusion, visual-grounded reasoning). Names taken from reference lists only: E1, not read."
next_test: {hypothesis: "In a unified discrete-diffusion model that masks both text and image tokens, model-implied cross-modal dependence between co-committed text and image tokens is larger in early steps than late steps, under a fixed sampler and under a sampler-independent (random-order) schedule", intervention: "measure a model-implied dependence statistic (pairwise within-step KL or a CMI estimate from swapped-context predictions) per step on the same prompts, under confidence and random ordering", primary_metric: "cross-modal dependence per step, text-image pairs vs within-modality pairs, with intervals over prompts", falsifier: "profile flat or late-peaking under random ordering; or early peak disappears when the matched within-modality profile is subtracted", gpu_hours: "not estimated here"}
```

# Verdict table

Our claim: in a unified model that generates both text and image tokens, the model's cross-modal conditional mutual information (CMI) between co-committed text and image tokens is concentrated early in the trajectory.

| Paper | Quantity (what is measured) | Modality pair | Model / task | Axis | Reported trend | Verdict on our claim |
|---|---|---|---|---|---|---|
| P1 VRCD 2605.25820 | VRI (Eq 2): attention-weight overlap on the same image tokens among text tokens committed in one step. Proxy: last-layer, head-averaged text-to-image attention | text token vs text token, linked through image-token attention. Image tokens are inputs, never committed | LaViDa-Reason (LLaDA-8B + SigLIP) main; MMaDA in App A.4; M3CoT, MMBench for the VRI curves | decoding step (Fig 3a, Fig 4a); mean over steps (Tab 4) | Text states only that VRCD has lower VRI "throughout decoding". Baseline curve not early-concentrated in Fig 3a; higher early in Fig 4a (detail below) | **Not reported.** Closest per-step curve of the three, but wrong quantity, wrong pair, text-only generation |
| P2 VIG-Sampler 2608.26580 | (a) SIR (Eq 5): 1 minus joint information gain over the sum of single-token gains; (b) pairwise cosine similarity of centred image-attention vectors; (c) cumulative information gain (Eq 3-4: drop in mean entropy of remaining masked text tokens) | text vs text through image attention; info gain is text-only | LaViDa, MMaDA, LLaDA-V; COCO Caption (Fig 4), 100-image COCO subset (Fig 2) | SIR and info gain against attention mass or similarity (Fig 2); cumulative info gain against step (Fig 4) | Fig 2 bottom: SIR rises with attention similarity. Fig 4: baselines' cumulative gain near zero in early steps then convex; VIG-Sampler higher from the start | **Not reported.** No dependence quantity is plotted against step |
| P3 PUNT 2510.21961 | KL between a token's prediction with and without other tokens' sampled candidates revealed (contextual-independence test, Sec 3.2; error Eq 3) | text vs text (and protein residues). No image | Dream 7B, LLaDA 1.5; MTBench, IFEval, GSM8K, HumanEval, MBPP; MemDLM protein | tokens revealed earlier within one step (Fig 3 right); fraction of tokens accepted per step vs % known tokens (Fig 2 left) | KL stays below the threshold by construction; acceptance per step is hump-shaped over progress; headings-first behaviour shown on one prompt | **Not reported.** Text-only; no cross-modal pair; no dependence-vs-step profile |

Overall: **not reported** by any of the three. Nearest neighbours are P1 (per-step proxy curve, different object) and P3 (model-implied KL test statistic, no modality and no step axis).

# Per-paper detail

## P1 VRCD (2605.25820), source facts with locations (E2: the paper reports X)

- Definition. Sec 3.2, Eq 2. For the committed set S_t with m = |S_t| tokens, v_i(u) is the normalized token-to-image attention of text token i on image token u. VRI = sum over u of (sum_i v_i(u) minus max_i v_i(u)) divided by (m-1), 0 if m is less than 2. Range 0 to 1. Instantiated with attention "as a lightweight proxy", citing Kim et al. 2026 (2603.12996).
- Which tokens. Only text tokens committed in the same step. Image tokens are the conditioning input. Attention source: final decoder layer, head-averaged (App A.2, Tab 8).
- Model, task, hardware. lavida-llada-reason, 980 pooled image tokens per image (App A.2). VRI curves on M3CoT (Sec 4.3) and M3CoT plus MMBench for the alpha sweep (Fig 4). Main runs on L40 GPUs, others on RTX 4090 (App A.1). Seeds not stated in what I read.
- Settings of the step curves. Fig 3: L=192, FR=0.25, so about 48 steps with 4 tokens per step. Fig 4: L=384, FR=0.125 (Sec 4.4), about 48 steps with 8 tokens per step.
- Reported numbers (Tab 4, mean VRI over steps): LaViDa 0.752 / 0.685 / 0.784 / 0.720 and VRCD 0.712 / 0.588 / 0.743 / 0.623 for (L, FR) = (192, 0.25), (192, 0.5), (384, 0.25), (384, 0.5). IG is 0.749 / 0.679 / 0.783 / 0.718, within 0.006 of LaViDa in every setting.
- Trend in the text. Sec 4.3: "IG remains close to LaViDa, while VRCD exhibits consistently lower VRI throughout decoding." The text gives no statement about early versus late VRI. Sec 4.2 says early choices "can affect later decoding behavior" as motivation for the gains; that is a stated rationale, not a measured profile.
- Trend by eye (approximate, from rendered Fig 3a and Fig 4a; values not extracted).
  - Fig 3a, baseline LaViDa: about 0.753 to 0.764 over steps 0 to about 16, a dip to about 0.74 around steps 20 to 26, then a climb back to about 0.757 by the last steps. A band of roughly 0.02. This is flat-to-U-shaped, not early-concentrated. VRCD tracks the same shape about 0.04 lower and rises to about 0.737 at the end.
  - Fig 4a, baseline (alpha = 0) on M3CoT: a sharp dip at steps 1 to 2, a plateau near 0.90 for steps 3 to 14, then about 0.83 to 0.84 from step 25 on. So the baseline VRI is about 0.06 to 0.07 higher in the first third than later. MMBench shows the same shape (about 0.92 early, about 0.85 late). This is the only place where a higher-early pattern appears, in a different quantity (text-to-image attention overlap) and for a text-output model. The paper does not comment on it.
- Mechanism claim about timing. The abstract and Sec 1 say redundancy "leav[es] less complementary visual grounding available for later decoding". Supporting evidence in the paper is the accuracy gain and lower remaining-position entropy (Fig 3b, Fig 4b), not a measurement of dependence over steps.
- Gaps and cautions. VRI depends on how many tokens are committed per step (m) and on which tokens (format tokens and function words have near-uniform attention; Sec 3.4 admits VRI "can still include this attention noise"). No uncertainty intervals or seeds for the VRI curves in the text I read. Single model family for the curves.

## P2 VIG-Sampler (2608.26580), source facts

- Section numbering. The arXiv PDF uses unnumbered headings. What the auditor called Sec 2.2 Eq 5 is Eq 5 under "Motivating Observations" (p 3 to 4). Eq 5 is SIR.
- Definitions. Eq 3: U = mean entropy of the model's predictions over the masked set after removing S. Eq 4: information gain dU_t(S) = U before minus U after unmasking S. Eq 5: SIR_t(S) = 1 minus (dU_t(S) divided by the sum over i in S of dU_t({i})). Image-attention mass m_i = sum of last-layer, head-averaged attention from position i to image tokens (Eq 6). Pairwise similarity G_ij (Eq 8-9) is cosine of attention vectors centred over the masked set, clipped at 0.
- Which tokens and pairs. Text tokens only (masked response positions). Information gain is over text predictions. Cross-modal element: image attention as a proxy, plus a counterfactual grounded flag (re-predict one token with image embeddings zeroed; changed prediction means "grounded"). That flag is a model-implied text-given-image dependence per token, collected under k=1 decoding on 100 COCO validation images (Appendix, motivation-study details). It is binned by attention mass in Fig 2 top, not by step.
- Fig 2 (axes). Top: token fraction or mean info gain against image-attention mass. Bottom: SIR against mean pairwise image-attention similarity for k = 2, 4, 8. By eye, SIR rises with similarity: k=2 stays near 0.05 to 0.1 until similarity about 0.6 then jumps to about 0.4; k=4 goes from about 0.2 to about 0.58; k=8 from about 0.5 to about 0.68. No step axis; step enters only as the pool of steps averaged within each bin.
- Fig 4 (axis = decoding step). Caption: cumulative information gain across decoding steps for k in {2, 4, 8}, COCO Caption, LaViDa, punctuation/articles/function words excluded. Text: VIG-Sampler "consistently achieves the highest cumulative information gain across all commit budgets". By eye: Confidence, Entropy, Info-Gain and PC-Sampler curves are near zero for the first part of the trajectory and rise convexly; VIG-Sampler starts higher and rises roughly steadily. This is a result about the sampler's information gain on content tokens, not about model dependence, and it is the opposite shape (late) for the baselines. Values not read.
- Run setup. Generation length N=32 (128 with block decoding on DetailCaps), greedy (temperature 0), single run, RTX A5000 (Appendix, evaluation setup). Gamma=1, lambda=3 fixed.
- Claim about trajectory timing. Intro: uninformative tokens "are often decoded first in the early steps", cited to Martinez 2024 and Huang 2026, not measured here.

## P3 PUNT (2510.21961), source facts

- Sec 3.2-3.3. Candidates sorted by confidence. Anchor set S0 and test set S1 per round; for each j in S1 compute d_j = KL(p_j(. | x_unmasked, y_S0) || p_j(. | x_unmasked)); drop j if d_j exceeds epsilon. Log2|M| rounds, one forward pass each. The kept set R is "contextually independent" (Def 3.2, Eq 2). Relies on Assumption 3.3 (independence stability), justified in Sec 3.4 and App B by an attention argument, with an empirical check (Fig 6: joint distribution of KL and total attention; Fig 7: layer-output change).
- Re-query. Yes, each round is a re-query with anchors revealed; KL is the dependence statistic. It is an influence of sampled candidates on a prediction at a point, thresholded; it is not a mutual-information estimate, and it is computed within one step.
- Against what axis. Sec 4.3 and Fig 3 right: KL error of the i-th token against the number of previously revealed tokens in the same step (LLaDA, 1024-token MTBench responses); by construction below epsilon, with Q5 below 1e-3 across positions. Fig 2 left: tokens unmasked per step (percent) against percent of known tokens, for writing and coding prompts at two epsilon values; by eye hump-shaped, lowest at the start and end, peaking mid-trajectory (about 4 to 6 percent per step at the peak). Model and exact sampler setting for this plot not stated in the caption. This is the closest thing to a trajectory-profile of dependence in P3, since acceptance rate is lower where candidates depend on each other; it is an indirect, text-only, sampler-conditioned read.
- Early-structure remark. Sec 3.4 and Fig 2 right show one prompt at steps 9 and 18 (headings fixed before body text) and offer a hypothesis that structural tokens are independent of fine detail. Stated limitation: "A formal investigation of this phenomenon is left for future work." So the timing statement is anecdotal, one example, and about text structure.
- Models and tasks. Dream 7B and LLaDA 1.5 (text), MemDLM (protein). No image or multimodal model anywhere in the paper (grep for image, vision, multimodal found only a reference title).
- Paper's own limitations (Sec 6 and App C): weaker NFE efficiency on short-answer tasks; per-step cost; unresolved formal study of hierarchical behaviour.

# What differs from our planned claim

1. Object measured. Ours: model-implied CMI, a property of the model's joint predictive distribution. P1 and P2: attention-overlap proxies. P3: a pointwise KL influence test, closer in spirit but within-step and text-only.
2. Pairs. Ours: text-image pairs that are co-committed. P1 and P2 never commit image tokens (image is input; tasks are captioning or VQA). P3 has no images. A unified generating model (e.g. MMaDA text-to-image, Lumina-DiMOO, Muddit) is outside all three.
3. Axis. Only P1 (Fig 3a, Fig 4a) puts a within-step quantity on a step axis, and its text draws no early/late conclusion. P2 and P3 do not.
4. Sampler confound. Every profile above is generated under a particular ordering rule. A claim about the model needs a profile under a sampler-independent schedule or an explicit control; none of the three provides one.
5. Directional evidence is mixed and not about our quantity: P1 Fig 3a flat/U-shaped, P1 Fig 4a higher early, P2 Fig 4 baselines' content-token gain late, P3 Fig 2 left acceptance low early. These cannot be combined into a prior for our claim.

# Concerns

- Figure numbers are eyeball reads of rendered pages; do not quote them in a manuscript without extraction from per-step data or the authors' code (VRCD code is announced at github.com/infiniteYuanyl/VRCD; not inspected).
- Unread neighbours that could change the verdict: Li et al. 2511.15098 (visual-token redundancy across decoding steps in dMLLMs), Kim et al. 2603.12996 (DAPD, attention dependency), Ringel et al. 2604.02560, Kim et al. 2604.05497. All E1 here. A novelty-auditor or paper-reader pass on them is the cheapest way to close the remaining risk.
