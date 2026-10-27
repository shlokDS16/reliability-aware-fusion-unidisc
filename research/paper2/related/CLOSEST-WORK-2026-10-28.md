```yaml
agent: paper-reader
date: 2026-10-28
brief: Forensic read of the work closest to Paper 2 idea 1 (GATE) - Dropout Decoding, DiSP, UniDisc (App. G.1), plus FreeCorrection and Token-Critic taken from the 2026-10-27 novelty audit - with synthesis of baselines, protocols and hostile-reviewer sentences.
sources_examined:
  - arXiv:2412.06474v2 (Dropout Decoding, NeurIPS 2025)      # E2 + E3 partial
  - arXiv:2602.22246v1 (DiSP)                                # E2 + E3 partial
  - arXiv:2503.20853v1 (UniDisc)                             # E2 (main text + App. B.4, B.5, C, G, H, I; see coverage) + E3 listing only
  - arXiv:2602.02927v1 (FreeCorrection, "Training-Free Self-Correction for Multimodal Masked Diffusion Models")  # E2 + E3 partial
  - arXiv:2209.04439v1 (Token-Critic)                        # E2 (main text) 
  - arXiv:2607.13188v1 (CO2Jump / SC-CMJP)                   # NOT requested; partial read (abstract, related work, Sec. 4 excerpts, grep). E1/E2-partial
  - arXiv:2606.29814 (Nemotron-Labs-Diffusion-Image)         # abstract page only (E1)
  - research/paper2/ideation/NOVELTY-AUDIT-2026-10-27.md, IDEAS-RAW-2026-10-27.md (Idea 1), RED-TEAM-2026-10-27.md (Idea 1), probes/PROBE-REPORT-2026-10-27.md
coverage: >
  PDFs fetched to research/sources/pdfs/, text in research/sources/md/ (markitdown for Dropout Decoding, pdftotext for the rest; the two-column
  layout scrambles some tables, which I re-extracted with pdftotext -layout where noted). Read in full: Dropout Decoding (main text, appendices A-D,
  checklist skipped), DiSP (main text, App. A proof start, B, C, D), FreeCorrection (all), Token-Critic (all except the derivation appendix and the
  extra qualitative figures). UniDisc: abstract, Secs. 1-5, App. B.4/B.5, C, G.1, G.2, H tables, I, J; NOT read in detail: App. A (pseudo-code), D, E, F ablations.
  Code (never executed, downloaded as untrusted text under research/sources/code_*): Dropout Decoding models/llava.py at 1ce15558; DiSP self_purify/self_purification.py,
  llava_llada.py, modeling_llada.py (generate_prompt_mask_kl_approx, lines ~1508-1860) at 3c477323; FreeCorrection generators/* and inference/inference_t2i_trajectory.py at 17fc37af;
  UniDisc file listing, README, docs/EVAL.md, grep of demo/*.py at 3ee3e47a. NOT covered: OpenReview reviews of any of these papers, any paper citing them,
  the LLaDA-V / LaViDa / Lumina-DiMOO papers, Salazar et al. 2020, ImageNet-C. Search for concurrent work is one WebSearch pair plus two arXiv abstract fetches, so weak.
claims:
  - statement: "Dropout Decoding scores each visual token by KL(its logit-lens text distribution || the image-average text distribution) and drops high-score tokens at random with score-scaled probability; it is validated only on CHAIR/THRONE/MMBench, never against corrupted-token ground truth."
    status: supported
    evidence: "2412.06474 Eqs. 3-6, 9; Sec. 6-7; App. B-C; code models/llava.py get_image_attention_mask method 'epis' (lines ~484-660)"
    level: E3
    confidence: 0.85
  - statement: "The Dropout Decoding text claims +16% / +12% (CHAIR_I / CHAIR_S) over the second-best method on InstructBLIP; Table 1 gives those gains over greedy, not over the second-best (beam search, 4.3% / 5.2%)."
    status: contradicted
    evidence: "2412.06474 Sec. 6.2 vs Table 1 (p.8), InstructBLIP rows: greedy 27.87/7.90, beam 25.87/6.93, DD 24.53/6.63 (my arithmetic)"
    level: E2
    confidence: 0.9
  - statement: "Dropout Decoding improves MMBench on both LLaVA-1.5 and LLaVA-NeXT."
    status: mixed
    evidence: "Table 2: LLaVA-1.5 71.86 -> 74.01 (OPERA 73.86); LLaVA-NeXT 74.57 -> 74.31 (below the unmodified model). No CIs."
    level: E2
    confidence: 0.9
  - statement: "Random token masking matches or beats Dropout Decoding's CHAIR_S in the authors' own ablation; the authors dismiss this as repetition artefact."
    status: supported
    evidence: "2412.06474 Table 4 (p.10): LLaVA-1.5 CHAIR_S 35.93 random vs 39.80 DD; InstructBLIP 23.80 vs 24.53. Table 4 greedy CHAIR_I for LLaVA-1.5 (7.90) disagrees with Table 1 (12.83)."
    level: E2
    confidence: 0.85
  - statement: "DiSP selects vision tokens by a Fisher-Jacobian influence score on first-step generation logits and replaces them with the mask-token embedding; the purpose is backdoor removal by rewriting training responses, and the evaluation has no natural-corruption, detection-AUROC, or marginalise-vs-impute component."
    status: supported
    evidence: "2602.22246 Eqs. 3-11, Algorithm 1, Sec. 4; code self_purify/self_purification.py + modeling_llada.py generate_prompt_mask_kl_approx"
    level: E3
    confidence: 0.85
  - statement: "DiSP's training loss masks only response tokens, so the mask-token embedding at vision positions is, by the paper's own Eq. 2, not a trained state in LLaDA-V/LaViDa; UniDisc is trained with masked image tokens."
    status: supported
    evidence: "2602.22246 Sec. 3.2 Eq. 2 (loss over response x0, prompt (v,p) unmasked); 2503.20853 Sec. 3.2-3.3, Fig. 2. Inference from the papers' equations; LLaDA-V training code not read."
    level: E2
    confidence: 0.6
  - statement: "UniDisc App. G.1 / Fig. 8 / Fig. 20 shows qualitative repair of corrupted image-caption pairs by random masking of both inputs, re-unmasking, and best-of-n selection by the model's own likelihood; there is no per-token score, no gate, no metric."
    status: supported
    evidence: "2503.20853 p.11 (Fig. 8 caption), App. G.1 (p.28), Fig. 20"
    level: E2
    confidence: 0.9
  - statement: "UniDisc is trained with 10% whole-modality masking, so p(token | other modality masked) is a trained quantity; the proposed PMI null term equals the CFG unconditional branch."
    status: supported
    evidence: "2503.20853 Sec. 3.3 (CFG paragraph), Sec. 4, App. I (cfg logits = (1+w)cond - w uncond)"
    level: E2
    confidence: 0.9
  - statement: "UniDisc text claims it outperforms AR on all retrieval tasks; Fig. 7 shows a tie on DataComp text retrieval (0.85 vs 0.85) and AR ahead on DataComp image retrieval (0.96 vs 0.95)."
    status: mixed
    evidence: "2503.20853 Sec. 4.3 text vs Fig. 7 table (p.10)"
    level: E2
    confidence: 0.85
  - statement: "FreeCorrection (arXiv 2602.02927) already reports that a pretrained multimodal MDM (Lumina-DiMOO) assigns higher predicted probability to original than to flipped tokens, the premise GATE needs, but measures it on its own partially noised sequences with mean-probability curves, not AUROC, and not as a cross-modal PMI."
    status: supported
    evidence: "2602.02927 Sec. 4.1, Figs. 1-2 (Flickr8k, 2000 samples)"
    level: E2
    confidence: 0.8
  - statement: "FreeCorrection's released code (pinned commit 17fc37af) imports generators.image_generation_generator_trajectory in inference_t2i_trajectory.py but that file is absent from the tree, and the understanding generator contains no remasking-with-reevaluation; only an image-to-image trajectory generator carries the remask logic."
    status: supported
    evidence: "GitHub tree of huge123/FreeCorrection at 17fc37af; inference/inference_t2i_trajectory.py line 19; generators/text_understanding_generator.py grep"
    level: E3
    confidence: 0.8
  - statement: "Token-Critic is a trained, class-conditional ImageNet critic that scores generated VQ tokens; no code link in the paper; no text conditioning."
    status: supported
    evidence: "2209.04439 Secs. 3-4, Table 1, Sec. 4.3; grep for github finds only guided-diffusion"
    level: E2
    confidence: 0.85
  - statement: "No work among those read scores the given conditioning tokens of a unified masked-diffusion model by cross-modal pointwise mutual information, calibrates a false-alarm threshold on clean data, and compares withdrawal ([MASK]) with re-infilling against known corrupted-token labels."
    status: supported
    evidence: "negative finding over the papers above plus audit; absence is weak evidence (see unknowns)"
    level: E2
    confidence: 0.55
competing_explanations:
  - "Any GATE gain may be generic input masking (regularisation / reduced over-commitment), which Dropout Decoding's random-mask arm and DiSP's random-mask ablation both hint at."
  - "A detector built on PMI may be a texture/entropy detector rather than a corruption detector (IDEAS-RAW mechanism M3)."
unknowns:
  - "UniDisc licence for code and weights: no LICENSE file in repo root at 3ee3e47a, no licence in the Hugging Face model metadata for aswerdlow/unidisc_interleaved or unidisc_non_interleaved (API returned none)."
  - "Whether UniDisc's G.1 best-of-n editing recipe is in the released code: grep of demo/inference.py for best/likelihood/edit/select returned nothing; not exhaustively searched."
  - "Whether the oracle 'Data filtering' baseline in DiSP retrains from scratch or continues from the backdoored model (ASR stays 74.5-95% on LLaDA-V); paper text is ambiguous."
  - "Whether CO2Jump (2607.13188) ever remasks conditioning tokens: its Sec. 4 treats the task conditioning as fixed context; I did not read the full paper."
  - "The Nemotron-Labs-Diffusion-Image mechanism (token editing). The red-team's 'confidence threshold, corruption-trained' description is not confirmed by the abstract page."
  - "Concurrent unpublished or OpenReview-only work."
next_test: {hypothesis: "GATE's token score finds corrupted conditioning tokens better than max-probability, a ported Dropout-Decoding KL score and a ported DiSP saliency score", intervention: "Probe 2 restart (on HOLD) plus three ported-score arms on the same corrupted token sets", primary_metric: "AUROC against the known corrupted-token map, per corruption, with random and oracle gates for the downstream arm", falsifier: "GATE AUROC not above the best ported baseline's 95% CI, or random gate matches GATE downstream", gpu_hours: 3}
```

# Closest work to GATE: forensic notes and synthesis

Evidence labels follow research/CONTRACT.md. "Source fact" = what the paper reports (E2 for "the paper reports X", never for "X is true"). "Inference" = mine. Numbers are copied from the table or page named. Short quotes only.

Note on GATE as specified: IDEAS-RAW Idea 1 defines r_i = log p(x_i | rest, other modality) - log p(x_i | rest, other modality masked), gate = {r_i < tau}, tau = q-quantile on clean calibration data, arms (M) marginalise, (I) impute, (M+I). The red-team (F1.1) flagged that this score may be incoherent for token-level corruption detection; my own earlier Probe 1 only supports it at pair level (0.940 vs 0.730 caption-vs-wrong-caption accuracy with and without the null term; P2-PROBE-01 summary.json, exploratory). Token-level AUROC is untested because probe 2 crashed the machine twice.

---

## 1. Dropout Decoding (Fang, Yang, Chen, Zhao, Zhou), arXiv:2412.06474v2, NeurIPS 2025

**Exact claim (abstract).** An inference-time method that "quantifies the uncertainty of visual tokens and selectively masks uncertain tokens" in large vision-language models (LVLMs), reducing object hallucination (CHAIR, THRONE) and keeping general quality (MMBench).

**What is scored.** Each visual token i's top-layer hidden state is projected through the LM head (logit lens, Eq. 3) to a text-vocabulary distribution q_i. The mean distribution over the N visual tokens is q-bar (Eq. 4). Score U_epi(i) = KL(q_i || q-bar) (Eq. 6), the "epistemic" part of an entropy decomposition of H[q-bar] (Eq. 5, App. A). Inference: the paper itself says high U_epi corresponds to informative patches (Fig. 1 caption and Sec. 4), i.e. the score measures how atypical a token is relative to the image average, not whether the token is wrong. Inference: it is an informativeness/atypicality score, never validated against a corrupted-token label.

**What is masked, how.** Per generated text token j, K=3 dropout masks are sampled; token i is dropped with probability P(k) = alpha(k) + (beta(k)-alpha(k)) * min-max-normalised U_epi(i) (Eq. 9), range roughly 0.1 up to 0.3/0.5/0.7 across the three masks (Sec. 7.2, App. B; the PDF's Greek symbols are scrambled in extraction, so read the exact alpha/beta from App. B). An optional preliminary forward pass (Eqs. 7-8) keeps tokens whose projected top-k contains the first-pass prediction (k=5 LLaVA-1.5, k=10 InstructBLIP). K forward passes are batched, predictions are combined by majority vote, ties go to the candidate with fewest dropped tokens (Sec. 5.2). Average masked tokens in the selected candidate: 244.14 (LLaVA-1.5, 576 tokens), 879.53 (LLaVA-NeXT, about 2000), 13.67 (InstructBLIP, 32) (App. C, Table 9). Code (E3, models/llava.py, method "epis"): the mask is applied by zeroing entries of the attention mask, i.e. tokens are removed from attention, not replaced by a [MASK] embedding.

**Thresholds.** None. Drop probabilities are hyperparameters set by hand (alpha, beta, K=3, top-k). No false-alarm calibration.

**Tasks / data / protocol.** MSCOCO 2014 test, 500 random images, 3 seeds, prompt "Describe the image.", greedy, max 512 new tokens (App. B, Table 6); MMBench with 1 new token. Models: LLaVA-1.5-7B, InstructBLIP-Vicuna-7B, LLaVA-NeXT (Mistral 7B). Baselines: greedy, beam search, OPERA, VCD (OPERA and VCD hyperparameters in App. B Tables 7-8). No corruption or perturbation of the input is applied anywhere.

**Metrics and numbers (Table 1, p.8, re-extracted with pdftotext -layout; mean +- std over 3 seeds).**

| Model | Method | CHAIR_S | CHAIR_I | THRONE F1 |
|---|---|---|---|---|
| LLaVA-1.5 | greedy | 42.20+-2.86 | 12.83+-0.36 | 0.795 |
| LLaVA-1.5 | beam | 46.33+-1.10 | 13.9+-0.60 | 0.790 |
| LLaVA-1.5 | OPERA | 41.47+-0.92 | 12.37+-0.72 | 0.802 |
| LLaVA-1.5 | VCD | 49.20+-0.88 | 14.87+-0.47 | 0.786 |
| LLaVA-1.5 | Dropout Decoding | 39.80+-2.3 | 11.73+-0.25 | 0.804 |
| LLaVA-1.5 | DD without prelim pass | 39.73+-2.15 | 12.20+-0.70 | 0.799 |
| InstructBLIP | greedy / beam / OPERA / VCD | 27.87 / 25.87 / 28.07 / 39.33 | 7.90 / 6.93 / 8.23 / 19.10 | 0.809 / 0.809 / 0.805 / 0.737 |
| InstructBLIP | Dropout Decoding | 24.53+-1.26 | 6.63+-0.65 | 0.814 |
| LLaVA-NeXT | greedy | 28.80+-2.12 | 8.10+-0.92 | 0.815 |
| LLaVA-NeXT | Dropout Decoding | 26.26+-2.4 | 7.39+-0.69 | 0.821 |

Table 2 (MMBench, p.8): LLaVA-1.5 original 71.86, VCD 72.35, OPERA 73.86, DD 74.01; LLaVA-NeXT original 74.57, VCD 69.65, OPERA 74.54, DD 74.31.
Table 3 (p.9): throughput 37.0 tok/s greedy, 34.1 (-7.8%) DD without prelim, 20.1 (-45.7%) DD with prelim; uncertainty computation 73.30 ms per input at 576 tokens.
Table 4 (random masking): LLaVA-1.5 CHAIR_S 35.93 (random) vs 39.80 (DD); InstructBLIP 23.80 vs 24.53; the paper says random masking produces degenerate repeats ("apple apple apple") that inflate CHAIR and breaks THRONE. Table 5 (masking high-confidence tokens): close to greedy.

**Mismatches between text and tables (logged as claims above).**
1. Sec. 6.2: gains of "16% and 12%" "over the second-best method" on InstructBLIP. Table 1: 6.63 vs greedy 7.90 = 16.1% and 24.53 vs 27.87 = 12.0%, so the percentages are against greedy; against the second-best (beam, 6.93 and 25.87) they are 4.3% and 5.2%, inside the seed std (+-2.77 for beam CHAIR_S). Contradicted.
2. LLaVA-1.5 CHAIR_S gain (42.20 -> 39.80) is inside one seed std (2.86 / 2.3). With 3 seeds there is no test.
3. LLaVA-NeXT MMBench: DD 74.31 is below the unmodified 74.57; the Sec. 6.4 text only claims superiority on LLaVA-1.5.
4. Table 4's greedy CHAIR_I for LLaVA-1.5 (7.90+-0.63) is the InstructBLIP greedy value, and disagrees with Table 1 (12.83). Typesetting error or wrong row; cannot tell.
5. The headline "DROPOUT DECODING" rows include the preliminary pass, which costs -45.7% throughput; the cheap variant is the one at -7.8%.

**Limitations stated by the authors (Limitations section, p.14-15).** Extra forward passes; effectiveness depends on text-space projection quality of the projector. **Unstated:** no corrupted-input evaluation; no ground-truth validation of the score; AR decoder with continuous embeddings; masking by attention removal is not an in-distribution state for an AR LVLM; evaluation is object hallucination on COCO only; only 7B-class models; no CIs.

**Code and licence.** github.com/kigb/DropoutDecoding, HEAD 1ce15558fa31320df504f1aaa7aeeaaaaa510683 (pushed 2024-12-08 per API). No LICENSE file; GitHub API reports none. README lists CHAIR and THRONE; the repo also contains a pope_test directory that the paper does not report. Implemented sampler matches Eq. 9 (linear map from normalised U_epi to [0.1, prob], voting via select_by_vote, lines 335-361 and ~620-660 of models/llava.py). The same file carries several commented-out alternative masking rules, so the released snapshot is a research scratchpad (inference).

**Precise difference from GATE.**
- Signal: Dropout Decoding scores a token's atypicality relative to the image mean, through an AR model's logit lens. GATE scores the plausibility of the token itself under the other modality, as a likelihood ratio, in a model that was trained to predict such tokens.
- Representation: continuous embeddings and attention removal vs discrete codes and the trained [MASK] state.
- Calibration: none vs false-alarm quantile on clean data.
- Evaluation: hallucination in captions vs detection AUROC on known corruptions plus downstream recovery.
- Common ground (do not deny): both withdraw input tokens at inference time without training, both justify it as a form of marginalisation/regularisation, both have a random-mask control. If GATE's random-gate arm matches GATE, the contribution reduces to Dropout Decoding's.

---

## 2. DiSP: Diffusion Self-Purification (Wan, Li, Fang, Ma, Wang), arXiv:2602.22246v1 (cs.CR, 24 Feb 2026), NUS

**Exact claim (abstract).** "selectively masking certain vision tokens at inference time can neutralize a backdoored model's trigger-induced behaviors"; use that to rewrite responses of the poisoned training set with the compromised model, then fine-tune on the purified set; ASR "from over 90% to typically under 5%".

**What is scored.** Per training instance, with all response positions masked, the first-step generation logits L_gen (T x V) give a predictive distribution p. Fisher information F = diag(p) - p p^T (Eq. 3). Visual-token saliency s_i = 0.5 * e_i^T J_i^T F J_i e_i (Eq. 5), where e_i = E_v[i] - e_mask and J is the Jacobian of generation logits w.r.t. the visual embeddings; estimated with Hutchinson probes q ~ N(0, F) (Eqs. 6-8). The number of probes m is not given in the text I read; code default fisher_num_probes=6, top-k vocabulary 5, float64 Fisher (modeling_llada.py ~1542-1549; llava_llada.py generate()). So the score is the second-order change in the output distribution if that token were removed: an influence score, which the authors justify as "backdoor tokens dominate the early predictive distribution" (Sec. 1).

**What is masked, how.** Top-k tokens with k = floor(rho * L_v), rho = 0.3 (LLaDA-V) or 0.5 (LaViDa), set by hand (Sec. 4.2). Continuous visual embeddings are replaced with the mask-token embedding (Eq. 10); the selected tokens stay masked for the whole denoising of the response (Sec. 3.3). One pass for saliency (probe backprops) plus one generation. Gen length 32, 32 steps, block length 32 for LLaDA-V (App. B.1).

**Thresholds.** None; fixed mask ratio, swept 0 to 0.75 in Fig. 2 (p.5).

**Tasks / data.** Three backdoor targets: targeted refusal, content insertion ("<backdoor>" prefix), semantic misclassification (dog described as boat). Poisoned sets: 1,000 samples from CC-SBU-Align, or 500 Flickr8k dog images, 20% poison rate (40% for LaViDa misclassification), 200 triggered plus 200 clean test samples per task. Triggers: 20x20 black patch (corner for LLaDA-V, centre for LaViDa), Gaussian noise patch (std 30), four-corner multi-patch, blended image. Only the projector is fine-tuned; 8x A5000 (App. B.1).

**Metrics and numbers.** CP = MMMU accuracy (clean model LLaDA-V 49.11, LaViDa 43.56); ASR with trigger (w/t) and without (w/o). Table 1 (LLaDA-V), backdoored -> DiSP ASR(w/t): refusal 98.50 -> 1.00, content insertion 92.50 -> 0.50, misclassification 94.50 -> 0.50; CP 48.44 -> 49.44, 49.56 -> 49.22, 47.22 -> 47.56. Table 2 (LaViDa): refusal 93.50 -> 1.50, content insertion 93.50 -> 0.00, misclassification about 90 -> 1.00 (this row is scrambled in extraction). Baselines (Tables 1-2): random drop of 20% of the training samples, weight pruning (30% smallest magnitude), and an oracle data filter. Table 3 other triggers: 92.5-98.5 -> 0.0-0.5. Ablation Fig. 4 (p.8): no masking or random masking of tokens keeps ASR at or above 88%, saliency masking below 1%. Table 4: six-benchmark average of LLaDA-V changes by at most 0.12 relative to the backdoored model. Fig. 2: at 45% of tokens masked the model keeps roughly 89-91% of its MMMU accuracy (relative CP).

**Notes on the evidence.**
1. The "random drop" baseline removes training samples, not tokens. The only token-level random control is the Fig. 4 ablation.
2. Oracle data filtering (all poisoned samples removed) still leaves ASR 74.5-95% on LLaDA-V (Table 1). A perfect filter followed by fresh training should give about 0; this suggests the baseline continues from the backdoored weights. Ambiguity in the text; flagged, not resolved.
3. No variance, seeds or CIs are reported (single numbers on 200-sample tests, so a step of 0.5 is one sample).
4. Inference (E2, moderate): the training loss in Eq. 2 supervises only response positions, with prompt (v, p) unmasked, so a mask embedding at vision positions is not a state seen in training for LLaDA-V/LaViDa, although the Introduction says MDLMs "can flexibly take partially masked inputs". This is the point where UniDisc differs (image tokens are masked during training).
5. Stated limitations: none in the paper text I read (no limitations section found). Unstated: backdoor-only scope; first-step generation with all response tokens masked is assumed to expose trigger-driven behaviour; fixed mask ratio chosen per model; the purified-data pipeline needs fine-tuning.

**Code and licence.** github.com/bigglesworthnotacat/Diffusion_Self_Purification, HEAD 3c47732383c7bebd899ae5a9446a6ffa87273385 (pushed 2026-03-09). Root has no LICENSE; the vendored LLaDA-V/train/LICENSE is Apache 2.0 (header read) and lmms-eval has its own LICENSE. Implementation matches the paper: generate_prompt_mask_kl_approx computes Hutchinson-probe scores, masks the top img_mask_ratio fraction with the mask embedding, and generates (modeling_llada.py lines ~1508-1860); self_purification.py re-captions every image with one fixed prompt ("Describe this image in detail.") and overwrites the first assistant turn. **Gap:** the paper reports LaViDa (Table 2) but the repo tree contains only an LLaDA-V pipeline (no LaViDa path found by filename search), so Table 2 is not reproducible from the release.

**Precise difference from GATE.**
- Purpose and target: backdoor defence; the masked tokens are the ones that most influence the output (a trigger), not tokens that are implausible. Opposite selection logic: DiSP removes what the model relies on, GATE removes what the model cannot corroborate.
- Mask granularity and scoring: gradient/Fisher influence over continuous embeddings vs masked-likelihood ratio over discrete codes.
- Threshold: fixed ratio vs calibrated false-alarm quantile.
- Use of the masked pass: to relabel training data and fine-tune, vs inference-only decoding.
- No text-side conditioning, no generation tasks beyond short answers, no imputation arm, no detection metric.
- Common ground: it is the published demonstration that masking vision tokens in a diffusion VLM at inference suppresses a harmful input pattern, and it contains a random-masking control (Fig. 4).

---

## 3. UniDisc (Swerdlow, Prabhudesai, Gandhi, Pathak, Fragkiadaki), arXiv:2503.20853v1 (26 Mar 2025)

**Exact claim (abstract/intro).** First unified multimodal discrete diffusion model over text and image tokens; beats an AR baseline on conditional generation, inference-compute trade-off, controllability, "joint multimodal inpainting", and retrieval.

**Model facts relevant to GATE (E2).** Absorbing-state masked diffusion, bidirectional decoder-only transformer, one joint vocabulary; 1.4B scale model trained on about 250M image-caption pairs at 256x256, then 30M at 512x512 (Sec. 4.4); LFQ image tokens, 256 image tokens plus 128 text tokens = 384 sequence length for the 256-px setting (App. C). With probability 0.1 all tokens of a random modality are masked in training, so unconditional modality likelihoods are learned (Sec. 3.3). Confidence-based (MaskGIT) sampling was found best (Sec. 3.4). CFG logits (1+w)cond - w uncond (App. I); w=1.5 chosen for the small models.

**App. G.1 / Fig. 8 / Fig. 20 (the repair experiment).** Protocol, in full: "augment real images by overlaying random objects from the COCO dataset"; captions are made "purposely incorrect" by an LLM; then "randomly mask the image and text inputs and unmask", best-of-n over n distinct noise masks, selecting by "the model's own likelihood" (App. G.1, p.28). The main text (p.11) frames it as zero-shot editing of "corrupted and mismatched image/text pairs" into "an aligned, high-quality pair". Evidence is a figure of examples only (Fig. 20 plus Fig. 8). No metric, no n, no number of images, no per-token score, no detection, no baseline, no failure cases.
Related: Fig. 18 (text-conditioned inpainting), Fig. 19 and Fig. 1 (joint image-text inpainting), App. B.4/Fig. 12: against an AR model fine-tuned for joint inpainting, CLIP score vs masking ratio 0 to 1 on a DataComp1B subset (read from a plot; no table).

**Quantitative results that GATE can reuse (Sec. 4.3, Fig. 7, p.10).** 16-way retrieval with random negatives, exact accuracy: text retrieval AR/UniDisc: CLEVR-Ret 0.81/0.94, DataComp 0.85/0.85, Winoground 0.24/0.31; image retrieval: CLEVR-Ret 0.06/0.25, DataComp 0.96/0.95, Winoground 0.25/0.27; joint retrieval: CLEVR-Ret 0.06/0.5, DataComp 0.17/0.64, Winoground 0.06/0.20. Score = ELBO-type p(x|y). The text says UniDisc "significantly outperforms" AR "on all retrieval tasks" but DataComp text is a tie and DataComp image favours AR (mixed). Fig. 13: joint retrieval depends strongly on CFG and denoising steps. Other published results: FID 23.86 (MS-COCO 30K) and 18.67 (MJHQ-30K) for the 1.4B model (Table 6); GenEval in Table 5 (overall number garbled in extraction).

**Limitations.** No separate limitations section found. Unstated: the repair demo has no metric; generation quality of the released checkpoint is modest (our own EXP-001/003 show debris text; RED-TEAM X1); training-efficiency penalty 13.2x relative to AR (Sec. 4.2).

**Code and licence.** github.com/alexanderswerdlow/unidisc HEAD 3ee3e47a9e64bac2fdca59957726f14723371ced (pushed 2025-04-02). Checkpoints: aswerdlow/unidisc_interleaved and unidisc_non_interleaved on Hugging Face. **Licence: not found** (no LICENSE file at root; no licence in HF metadata). The paper says "Our code, model weights, and dataset are publicly available" (Sec. 1). grep of demo/inference.py for best-of-n/likelihood/edit returned nothing, so the G.1 recipe may not be released (not exhaustively searched). docs/EVAL.md covers only the small-scale AR/NAR evaluation script.

**Precise difference from GATE.**
- UniDisc G.1 masks at random and keeps whichever sample the model likes best; it never decides which input tokens are bad. GATE adds the token score, the calibrated gate, the marginalise-vs-impute comparison, controls and metrics.
- UniDisc retrieval is a pair-level ranking by conditional likelihood (a_text, b_image in our Probe 1 vocabulary); GATE needs per-token scores and a threshold. Our P2-PROBE-01 reproduces the pair-level signal on COCO (0.730 text direction, 0.783 image direction, 300 images; 0.940 with the null term) but did not test token-level detection.
- UniDisc is both the host model and the origin of the "repair" behaviour, so a reviewer who knows UniDisc will start from G.1 as prior art for the idea; the answer must be that GATE quantifies and controls what G.1 shows.

---

## 4. FreeCorrection: Training-Free Self-Correction for Multimodal Masked Diffusion Models (Ouyang et al.), arXiv:2602.02927v1 (stat.ML, 2 Feb 2026)

(Chosen from the audit as the closest read for Idea 1, which lists it under "Closest works read".)

**Claim.** Training-free self-correction of masked diffusion models (Lumina-DiMOO, MMaDA-8B-MixCoT) for text-to-image and multimodal understanding, fewer sampling steps. "first work to study self-correction mechanisms in multimodal masked diffusion models" (Sec. 1).

**Method.** At every step, re-evaluate p_d(x_t^d | x_t with position d re-masked) for each already-committed token (Algorithm 1, Sec. 4.2), keep a cumulated log score S_d, and remask the K_t = floor(eta_t * D) committed tokens with the lowest score (deterministic variant), or sample them. Variants in Table 4: current-step vs cumulated likelihood, deterministic vs stochastic, top-K margin, KL and Wasserstein between consecutive predictive distributions. Remask schedule eta_t is tuned on an unspecified "validation set".

**Premise experiment that matters for GATE (Sec. 4.1, Figs. 1-2).** On Flickr8k image-prompt pairs (z_image, z_prompt), noise with q(x_t | x_0), t ~ U(0,1), randomly pick unmasked tokens and flip them, then compare the model's predicted probability of the original vs the flipped value across 64 steps, averaged over 2000 samples. Result: correct tokens get "significantly higher" probability (read from a figure; no numbers, no AUROC). Fig. 2: accumulated probability ranks flipped tokens more reliably than single-step probability after step 32. It is not stated which modality the flipped tokens belong to, or whether the flipped token's own value is in context; this is plausibility under the rest of the sequence, not cross-modal PMI.

**Numbers.** Table 2 GenEval Overall (Lumina-DiMOO 64 steps, re-evaluated by the authors): 0.86 baseline, 0.87 ReMDM, 0.90 ours. Table 3: MMBench 58.7 / 57.8 / 60.7; SEED 71.4 / 74.3 / 74.2; MMMU 41.4 / 43.4 / 44.0 (baseline / ReMDM / ours; GPT-4o-mini as verifier). Table 5 (MMaDA-8B-MixCoT GenEval overall): 0.49 top-K, 0.48 top-K margin, ReMDM 0.51, ours 0.52. Fig. 4: with 16 steps ours is "comparable or better" than the 64-step baseline (read from a figure). No seeds or CIs; ReMDM is higher than ours on SEED (74.3 vs 74.2), so "consistent gains" is mixed.

**Code and licence.** github.com/huge123/FreeCorrection, MIT licence (API), HEAD 17fc37af58b57307ae96c1a020958f4ec0025158 (pushed 2026-10-01). Gap (E3): inference/inference_t2i_trajectory.py imports generators.image_generation_generator_trajectory, which is not in the tree (only image_to_image_generator_trajectory.py exists, which carries a hard-coded remask-count schedule: 0 before 40% of steps, 16 per step in 40-60%, 8 in 60-80%, 4 in 80-100%, and sets t_window = timesteps, overriding the argument); the understanding generator (text_understanding_generator.py) has no remasking-with-reevaluation. So the Table 2-5 results cannot be reproduced from this snapshot as far as I can see.

**Difference from GATE.** FreeCorrection remasks the model's own committed outputs using the same pretrained-model likelihood GATE would use (p of a token given the rest). The mechanism overlaps most with GATE's score; the object differs: outputs vs given evidence, no cross-modal null, no calibrated false-alarm threshold, no corrupted input. Treat its Sec. 4.1 as supporting evidence that the plausibility premise holds in Lumina-DiMOO, and note that it was never made into a detection metric.

## 5. Token-Critic (Lezama, Chang, Jiang, Essa), arXiv:2209.04439v1 (Google Research, 2022)

**Claim.** A trained second transformer predicts, for a masked-and-reconstructed VQ image, which tokens were originally masked (generated) vs real; at sampling time the lowest-scoring tokens are masked and resampled ("regrettable" sampling). Class-conditional ImageNet 256 and 512 with MaskGIT (1024-code VQ).

**Numbers.** Table 1 (no external classifier): FID 256: MaskGIT 6.56, MaskGIT+Token-Critic 4.69 (18 steps, two network calls per step); 512: 8.48 -> 6.80. With classifier rejection (Table 2): 4.70 -> 3.75 (256), 5.13 -> 4.03 (512). VQ refinement of finished MaskGIT samples (Sec. 4.3, Fig. 6): reject 60% lowest-score tokens with a cosine schedule for T=9 steps; FID 6.56 -> 5.73 (256), 8.48 -> 7.64 (512). Comparison is at double step count for MaskGIT (Fig. 3).

**Relevance.** It is the first-order precedent for "score VQ tokens for plausibility, mask the implausible ones, re-infill with a masked generator", including a refinement use on finished images. Differences: trained critic (600 epochs on TPUs), scores generator outputs, labels are "was generated", not external corruption; ImageNet class condition only, no text; code not found (no link in the paper). It cannot be a runnable baseline here; it must be discussed.

## 6. Adjacent items found on the way (not requested; flagged)

- CO2Jump / SC-CMJP, arXiv:2607.13188v1 (Google, 14 Jul 2026; 1348-line text read only by grep and excerpts). Joint text-image generation sampler on Lumina-DiMOO (fine-tuned): per-token self-confidence for both modalities, a cross-modal term from attention-weighted other-modality confidence, and a remask ("Death") jump that retracts committed tokens "when cross-modal evidence turns against them". Evaluated on an extended ImgEditBench (headline ImgEditBench score 1.93 vs 1.44-1.72 for baselines; mAP 0.369 overall) and maze/nonogram (JMaze, JNono). It remasks the model's own generated tokens; task conditioning is treated as fixed. It is the nearest published example of cross-modal consistency driving remasking in a unified MDM, and it postdates the audit's window by days. A reviewer may cite it for "cross-modal remasking". Not audited in the 2026-10-27 file (it lists 2610.15227, 2607.29079 etc. but not this id).
- Nemotron-Labs-Diffusion-Image (arXiv:2606.29814): abstract states a "token-editing mechanism" for revising unmasked tokens in a text-to-image masked discrete diffusion model plus a grouped cross-entropy objective; GenEval 0.90 (abstract). The red-team's description (threshold, corruption-trained) is unconfirmed.

---

## 7. Synthesis

### (a) Baselines GATE must compare against

Must have (cheap and what a reviewer will ask first):
1. No gate (identity), on clean and corrupted input.
2. Random gate of equal size and the same fraction of positions (Dropout Decoding Table 4; DiSP Fig. 4). Include clean-image gating to expose the regularisation explanation (IDEAS-RAW M2/M4).
3. Oracle gate (true corrupted set), as an upper bound.
4. Plain max-probability or pseudo-likelihood gate without the null term: p(x_i | rest) alone. This is FreeCorrection's "current-step likelihood" applied to given tokens, and the red-team's "gate by max-probability".
5. UniDisc G.1 recipe: random mask of image and text, re-unmask, best-of-n by own likelihood, at matched forward passes. This is the strongest simple baseline because it is the model authors' own repair demo.
6. Ported Dropout Decoding score: KL(q_i || mean q) computed from the model's per-position predicted distributions, with K-mask ensemble and voting. It must be labelled a port (the original is logit lens in an AR LVLM). Match K and total passes.
7. Ported DiSP score: Fisher-Jacobian saliency (probe count m=6, top-5 vocabulary as in the released code) on discrete-token embeddings, mask top rho at fixed ratios (0.3 and 0.5 as in the paper). Labelled a port. This tests whether plausibility beats influence as the selection rule.

Should have: a non-learned input-side purification baseline (JPEG/median/bilateral filtering before tokenisation) for image corruptions, since a vision reviewer will ask why not clean pixels first (my suggestion, hypothesis; no source read); marginalise-only vs impute-only vs both as already in GATE; a calibrated gate vs fixed-ratio gate (DiSP/DD style) at equal flagged fraction.

Cannot be run, must be discussed: Token-Critic (no code, trained on ImageNet), FreeCorrection as-is (released code missing the T2I generator and understanding path at the pinned commit), CO2Jump (no code checked).

Matching rules a reviewer will want: equal network calls (GATE 2K passes; DD K+1 passes with the prelim; DiSP m backprops plus one pass), same seeds, same sampler (note EXP-003: plain vs guided UniDisc sampler change coupling 0.051 vs 0.180, RED-TEAM X2), paired bootstrap CIs. None of the four papers reports CIs, so any CI we report is already stricter than the literature.

### (b) Reusable protocols

| Piece | Source | What to reuse | Caveat |
|---|---|---|---|
| Patch corruption | DiSP Sec. 4.1, App. D | 20x20 black patch (corner or centre), Gaussian noise patch std 30, four-corner multi-patch, blended image; "ASR w/o trigger" as the clean false-alarm analogue | Backdoor triggers, not accidental degradation; patch is tiny relative to a 32x32 token grid; the semantic effect is by training, not by content |
| Mask-ratio sweep | DiSP Fig. 2 | accuracy vs fraction masked (0 to 0.75), ASR vs fraction | Their Fig. 2 plots model behaviour on training data |
| Random-mask ablation | DiSP Fig. 4, DD Table 4 | same size random gate | DD says random masking breaks THRONE and inflates CHAIR via repeats; check for the same degenerate behaviour in UniDisc captions |
| Pair corruption | UniDisc App. G.1 | COCO-object overlays on images; LLM-corrupted captions; random masks plus best-of-n by model likelihood | Qualitative only; nothing numeric to compare with |
| Pair-level retrieval | UniDisc Sec. 4.3, Fig. 7 | 16-way text/image/joint retrieval accuracy on DataComp1B and Winoground, p(x|y) from ELBO | Used as sanity for the score, not for the gate |
| Flipped-token detection | FreeCorrection Sec. 4.1 | random token flips at t ~ U(0,1) on Flickr8k pairs; probability and rank vs step | Report AUROC (they do not); fix which modality is flipped |
| Caption quality | DD Sec. 6.2-6.3, App. B | CHAIR_S/CHAIR_I, THRONE P/R/F1, COCO 500 images, 3 seeds, "Describe the image.", 512 tokens, greedy | UniDisc captions are mostly debris (RED-TEAM X1); the metrics need a captioner that can write |
| Understanding benchmarks | FreeCorrection Sec. 5 | MMBench, SEED, MMMU with GPT-4o-mini as verifier; GenEval | Lumina-DiMOO/MMaDA, not UniDisc |
| Image refinement | Token-Critic Sec. 4.3 | reject the 60% lowest-score tokens, cosine schedule, T=9, FID | Class-conditional ImageNet |
| Standard natural corruptions | none of the four papers | ImageNet-C style noise/JPEG named in IDEAS-RAW | I did not read ImageNet-C; the corruption definition must be self-contained and preregistered |

No paper among those read defines a natural-corruption benchmark for conditioning tokens. Inference: GATE has to define and justify its own corruption set; reuse of DiSP's patch triggers and UniDisc's overlays gives it two partially citable anchors.

### (c) Sentences a hostile reviewer would write, with our best factual answer

1. "This is Dropout Decoding transplanted to a masked diffusion model: score input tokens, mask the uncertain ones, ensemble."
   Answer: the score is different in kind (DD: KL of a token's logit-lens text distribution to the image mean, which the paper itself says tracks informativeness; GATE: cross-modal masked likelihood ratio of the token itself) and DD has no corruption task or detection evaluation at all; GATE adds a clean-calibrated false-alarm threshold, a marginalise vs impute comparison and known-label AUROC. Concede: the idea of withdrawing input tokens at inference without training is theirs, and DD's Table 4 shows random masking can look competitive on CHAIR_S, so GATE must beat a random gate to claim anything.

2. "DiSP already showed that masking vision tokens at inference makes a diffusion VLM robust."
   Answer: DiSP's target is trigger-driven behaviour, the selection rule picks the tokens the output depends on most (Fisher-Jacobian influence), masks a fixed 30-50% of continuous embeddings, and uses the masked pass only to rewrite training labels. It has no natural-corruption evaluation and no per-token detection metric. Concede: DiSP is the citation for "masking vision tokens at inference changes a diffusion VLM's behaviour while preserving clean accuracy" (Fig. 2, Tables 1-2). One more defensible point (E2, moderate confidence): by DiSP's Eq. 2 the vision-position mask state is not trained in LLaDA-V/LaViDa, whereas UniDisc is trained with masked image tokens.

3. "UniDisc's own paper already repairs corrupted image-caption pairs (App. G.1); what is left?"
   Answer: G.1 is a qualitative figure: random masking of image and text, re-unmasking, best-of-n by model likelihood, with no per-token score, no metric and no baseline. GATE asks which tokens are corrupted, with a controlled false-alarm rate, and measures recovery against random and oracle gates at matched passes. The G.1 recipe should be run as a baseline (baseline 5 above).

4. "The null term is just classifier-free guidance's unconditional branch."
   Answer: correct; UniDisc trains with 10% whole-modality masking exactly so that p(x | other modality masked) exists (Sec. 3.3, App. I). The new part is its use as a per-token detector rather than as a guidance direction. Do not claim the quantity as new.

5. "Pseudo-log-likelihood scoring with masked models is standard (Salazar et al.); FreeCorrection already shows the pretrained masked model scores flipped tokens lower."
   Answer: yes for the premise (FreeCorrection Sec. 4.1, Figs. 1-2; I have not read Salazar et al., cited in the audit as the PLL source). FreeCorrection measures it on partially noised sequences with mean-probability curves and no detector metric, and uses it only to remask the model's own output. GATE reports detection AUROC at calibrated false-alarm rates for externally corrupted evidence. State plainly that the scoring primitive is not novel.

6. "Remasking low-likelihood tokens is ReMDM / Token-Critic / FreeCorrection / CO2Jump. Same thing at step zero."
   Answer: those four act on tokens the sampler produced; here the tokens are external evidence whose provenance is untrusted, so the question of marginalising (keep masked) versus imputing (re-infill) arises and can be tested; for self-correction, a re-infilled token is the model's own belief and no such split exists. Token-Critic's refinement (Sec. 4.3, FID 6.56 to 5.73) is the closest operational precedent and needs a trained critic; GATE is training-free. If the data show M and I behave the same, say so.

7. "The only evidence is one 1.4B model with debris captions."
   Answer (factual, from our own runs): UniDisc captions on this machine are mostly web-caption debris (RED-TEAM X1), so image-to-text CLIPScore is a weak endpoint; the pair-level likelihood signal is clean (P2-PROBE-01: 0.940 and 0.990 with PMI, 300 images, exploratory), so the score and detection can be evaluated without generation. The paper should say that a second backbone is future work unless one is run.

8. "No ground-truth study: how do you know the flagged tokens are the corrupted ones?"
   Answer: that is the AUROC against known corrupted-token maps (token swap, patch occlusion, noise, JPEG), which none of Dropout Decoding, DiSP or UniDisc's G.1 provides. Not yet measured by us (probe 2 on HOLD); do not state a number.

9. "Gains could come from masking per se."
   Answer: this is why the plan includes random-gate, oracle-gate and clean-image gate arms. The literature supports the worry: DD Table 4 (random masking CHAIR_S 35.93 vs 39.80 for DD on LLaVA-1.5) and DiSP Fig. 4 (random masking leaves ASR at or above 88%, so for DiSP the choice of tokens matters). Report both outcomes.

10. "Information Fusion needs fusion, not a robustness trick."
    Answer: the framing is source-reliability gating in a joint model (innovation gating, marginalising a missing source), and the paper should show behaviour as modalities are degraded or dropped. This is a scope argument, not a novelty fact; the style guide already rates a masked-diffusion generator as a scope risk (RED-TEAM X5).

### Biggest novelty threat, ranked (inference, my judgement)

1. UniDisc App. G.1 plus FreeCorrection Sec. 4.1 together: the host model's own authors show repair by masking and re-infilling, and a 2026 paper shows the same family of models scores corrupted tokens lower. A reviewer can say GATE's delta is a PMI normalisation and a threshold. The defence is entirely empirical (token-level AUROC, calibrated false alarms, controlled arms).
2. Dropout Decoding for the "uncertainty-guided input masking with an ensemble" framing, unless the random-gate control is beaten.
3. DiSP for "masked vision tokens in a diffusion VLM at inference", weakened by its different target and score.
4. CO2Jump (2607.13188) for cross-modal remasking in a unified MDM, if the camera-ready or a later version extends to input tokens.

### Gaps in this report
- UniDisc appendices A, D-F and the Winoground/CLEVR details were not read.
- No code was executed; E3 here means source inspected at the pinned commit, not that it reproduces the paper.
- Search for concurrent work was minimal (two web searches and two abstract fetches).
- The PDF text of Dropout Decoding Table 1 and DiSP Table 2 was scrambled by extraction; Table 1 DD numbers were re-extracted with pdftotext -layout and match Table 4. DiSP's LaViDa misclassification row is the least certain.
