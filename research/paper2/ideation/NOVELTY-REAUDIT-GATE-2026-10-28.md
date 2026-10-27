```yaml
agent: novelty-auditor
date: 2026-10-28
brief: Re-audit of the GATE method (spec 2026-10-28) against CO2Jump (2607.13188) and 2025-2026 work on masked-likelihood or remasking detection of corrupted input tokens with calibrated false-alarm control or multimodal evidence fusion.
sources_examined:
  - research/sources/md/2607.13188.txt            # CO2Jump, local text, read sections 1-4 and the experimental setup (E2 for those parts)
  - arXiv:2610.22380 (Trust but Verify)           # PDF converted locally, read abstract, intro, related work, Sec 3.4, Alg. 1, parts of Sec 4 by grep (E2-partial)
  - arXiv:2504.01225 (Gomes et al., CRC on CLIPScore)  # html read through the fetch tool's summariser, not verbatim (E1+)
  - abstract-only (E1): 2606.12807, 2512.15596, 2606.06031, 2605.26436, 2608.26574, 2509.23625, 2604.12035, 2609.01375, 2610.05125, 2602.11590 (title/summary via search snippet), 2510.01384, 2602.04096, 2209.07068, 2305.16397
  - context only (not redone): research/paper2/ideation/NOVELTY-AUDIT-2026-10-27.md, research/paper2/related/CLOSEST-WORK-2026-10-28.md, research/paper2/method/GATE-METHOD-SPEC-2026-10-28.md (lines 1-554 and 572-598; lines 555-571 and 600-685 not read)
coverage: >
  CO2Jump: Sec 1 to 4.4 and Algorithm 1 read; Sec 5 results only by grep (setup, Table 1 captions, scaling claims);
  appendices, the maze/nonogram tables and the limitations paragraph were NOT read. Trust but Verify: Sec 1-3 and Algorithm 1
  read; Sec 4 results and discussion only by grep. Everything else is abstract or snippet level and is marked so below.
  Venues checked: arXiv search pages (title/abstract fields, sorted by announcement date, to 2026-10-28), web search. OpenReview ICLR 2027 and
  NeurIPS 2026 listings were NOT searchable (web search returned no ICLR 2027 submissions; the NeurIPS 2026 virtual site
  surfaced one hit, Trust but Verify). Google Scholar and Semantic Scholar were not directly queryable from this tool; web search stood in.
claims:
  - statement: "CO2Jump remasks tokens the sampler itself generated, using self-confidence (text) and an attention-weighted cross-modal confidence mixture (image); it does not treat input/conditioning tokens as suspect, has no calibrated threshold, and does not use a masked-likelihood with the other modality masked."
    status: supported
    evidence: 2607.13188 Sec 4.2 (conditioning c is given context), Eq. 8-12, Alg. 1, Sec 4.4 (death quota set by the ReMDM schedule, not by a threshold)
    level: E2 (Sec 1-4), appendices unread
    confidence: 0.85
  - statement: "A concurrent paper (Trust but Verify, 2610.22380, 2 Oct 2026, NeurIPS 2026 workshop) already detects corrupted conditioning tokens in a masked discrete diffusion model from the model's own probability of the observed token and re-noises them to [MASK] then refills them, text only."
    status: supported
    evidence: 2610.22380 abstract, Sec 3.4 Eq. 4, Alg. 1
    level: E2-partial
    confidence: 0.9
  - statement: "No found work combines (masked-likelihood or remasking detection of corrupted INPUT tokens in a unified multimodal MDM) with (conformal or risk-control false-alarm threshold)."
    status: supported-as-absence (weak evidence)
    evidence: query log below
    level: E1 (absence of hits)
    confidence: 0.6
  - statement: "Conformal risk control with masking-derived scores for word-level error detection in image-captioning already exists, on CLIPScore."
    status: supported
    evidence: arXiv:2504.01225 (Findings of ACL 2025)
    level: E1+
    confidence: 0.8
competing_explanations:
  - "Reviewers will read GATE as 'Trust but Verify plus conformal plus multimodal, without finetuning'. That is a real, narrower claim, but it is a composition claim, so its value depends on measured results GATE does not yet have."
unknowns:
  - "Whether any ICLR 2027 / NeurIPS 2026 submission under review (not public) covers input-token gating in a unified MDM."
  - "CO2Jump appendices and limitations, and whether a v2 extends to input tokens."
  - "Trust but Verify Sec 4 detail: whether its base-model arm B scored observed tokens at unmasked positions only (it appears so)."
next_test: n/a (novelty audit)
```

# Re-audit of GATE: novelty after CO2Jump and a sweep to 28 Oct 2026

Evidence tags follow the contract (E1 snippet or abstract, E2 paper read, E2-partial = parts read).

## 0. Verdict

**incremental** (narrow delta still open), confidence **0.50** that the composed delta is open at submission (down from 0.60 in the first audit).
Per component: the unified-MDM gate score is open (0.65); the conformal clean-FAP calibration is open for MDMs but not for the vision-language idea in general (0.55); the marginalise-versus-impute comparison and the two-way PMI fusion are open as measurements (0.70) but PMI scoring itself is not new.
The paper most likely to be cited against us: **Trust but Verify, arXiv 2610.22380** (2 Oct 2026, NeurIPS 2026 workshop). For the conformal piece in a vision-language setting: **Gomes, Martins, Zerva, arXiv 2504.01225** (Findings of ACL 2025).
Residual risk: absence of hits is weak evidence; submissions under review at ICLR 2027 are not visible; the field produced at least four remasking/self-correction papers per month in 2026.

## 1. The candidate as one falsifiable sentence

Claim: on a pretrained unified masked discrete diffusion model, scoring each input token (image code or caption word) by its masked likelihood inside its own modality with the other modality masked, flagging tokens above a threshold set by conformal risk control on clean pairs (expected false-alarm proportion at most alpha), and then re-masking (or re-infilling) the flagged tokens, preserves two-way full-mask PMI verification and matching under input corruption better than a random gate of equal size and than an uncertainty-ranked gate.
Mechanism: absorbing-state denoiser gives p(x_j | partial context) for any mask pattern; masking a gated token marginalises it (Prop. 1); CRC gives the threshold; the evidence-separation rule keeps cross-modal terms out of the R1 gate.
Note: the claim about preserving verification under corruption is **untested** (spec: no results; probe 2 stopped at 20/200 items).

## 2. CO2Jump (2607.13188, 14 Jul 2026, v1 only) placed exactly against GATE (E2 for Sec 1-4)

Source facts (file `research/sources/md/2607.13188.txt`):
- Authors Le, Comas, Lattas, ... Samaras, Qiu; Google / Stony Brook. cs.LG. Single version v1 (arXiv abs page).
- Setting: concurrent text and image **generation** in a unified MDM; three tasks (image editing on an extended ImgEditBench, JMaze, JNono); backbone Lumina-DiMOO fine-tuned per task on 64 H100 GPUs, only the sampler changes (Sec 5 setup, line 960).
- Mechanism (Sec 4.3-4.4, Alg. 1): one forward pass per step; text score = self-confidence (probability of the Gumbel-sampled token, Eq. 8); image score = (1-lambda) * rank(self-confidence) + lambda * rank(cross-signal), where the cross-signal is text self-confidence weighted by image-to-text attention (Eq. 9-10) and lambda is a per-step scalar from mean entropies (Eq. 11-12). A ReMDM-style death step reverts the lowest-scoring committed tokens to [MASK]; the number reverted per step is a quota from the schedule and the valid-posterior constraint (Sec 4.4), not a threshold.
- The conditioning context c (edit prompt, source image, puzzle specification) is treated as given (Sec 4.2). No statement anywhere in Sec 1-4 treats conditioning tokens as unreliable.
- No calibration, no conformal or risk-control guarantee, no false-alarm control; no corrupted-input benchmark; "no auxiliary evaluator" (intro).

Placement:

| Axis | CO2Jump | GATE | Relation |
|---|---|---|---|
| Which tokens are remasked | tokens the sampler committed during generation | input tokens of an observed pair (image codes, caption words) | different |
| Trigger | low self-confidence / attention-weighted cross-modal confidence of the sampled token | masked likelihood of the observed token within its own modality, other modality masked (R1), statistic q = B - D | different; CO2Jump's cross-modal term is what GATE R1 forbids in a gate (rule 4.4) |
| Threshold | schedule quota (lowest k scores) | conformal risk control on clean pairs, FAP at most alpha | different |
| Use after remask | refill by the sampler | marginalise (stay masked) or re-infill; PMI evidence fusion | partial: re-infill resembles refill |
| Model/training | fine-tuned Lumina-DiMOO, 64 H100 | pretrained UniDisc 1.4B, no finetune | different |
| Tasks | editing, maze, nonogram generation | detection, verification, matching, repair | different |
| Mechanism class | remasking in a unified MDM using cross-modal signals | same class | **same class; the sentence "cross-modal remasking in a unified MDM" belongs to CO2Jump** |

Reading: CO2Jump does not scoop GATE's delta. It does remove any claim to be first to remask in a unified multimodal MDM, or first to use cross-modal evidence as a remask trigger. A reviewer will say "GATE is CO2Jump's death step run at step zero"; the answer is the input/conditioning role, the hypothesis-free score, and calibration. CO2Jump Sec 3 claims to be "the first to couple the remasking signal across modalities" (line 264); GATE must not contest this.
Not read: appendices and limitations; v2 could extend scope.

## 3. Search log (every query string; engine: web search unless noted)

Web search:
1. conformal risk control masked diffusion language model detect corrupted tokens remasking calibrated threshold
2. unified multimodal discrete diffusion corrupted input image tokens detection masked likelihood remask re-infill robustness arXiv 2026
3. masked language model pseudo-log-likelihood token-level anomaly detection typo noisy token detection conformal
4. conformal token filtering language model false discovery rate token-level hallucination detection calibrated
5. CoRe context-robust remasking diffusion language models training-free context-brittle tokens arXiv
6. conformal prediction discrete diffusion model tokens uncertainty guarantee masked diffusion
7. diffusion vision-language model adversarial image perturbation detection masked token likelihood purification unified discrete diffusion
8. image-text mismatch detection masked generative model cross-modal pointwise mutual information verification discrete diffusion
9. masked diffusion model detects wrong conditioning tokens "context corruption" OR "corrupted context" re-noise suspicious tokens infilling 2026
10. conformal risk control token-level false alarm vision-language tokens calibration set exchangeable pruning masking multimodal 2026
11. PRISM token quality head self-correction masked diffusion language models remasking arXiv
12. noisy prompt typos robustness text-to-image masked generative transformer detect and mask erroneous prompt tokens
13. OpenReview ICLR 2027 submission masked diffusion unified multimodal remasking input reliability conformal
14. likelihood-based image-text matching unified discrete diffusion model zero-shot retrieval conditional minus unconditional likelihood 2026
15. Conformal Risk Control Framework for Granular Word Assessment and Uncertainty Calibration of CLIPScore Quality Estimates
16. Are Diffusion Models Vision-And-Language Reasoners? Diffusion ITM image-text matching likelihood arXiv
17. diffusion vision-language model adversarial or corrupted image tokens robustness defense discrete diffusion VLM LLaDA-V MMaDA input perturbation 2026
18. MLM-based spelling error detection masked language model probability of original token threshold calibrated false positive rate

arXiv search pages (all-fields, sorted by announcement date descending, fetched 2026-10-28; the tool reads AND-semantics, so long queries returned nothing):
19. masked diffusion remasking conformal (0 results)
20. unified multimodal masked diffusion corrupted input robustness (0)
21. remasking multimodal diffusion (4 in 2026: 2608.26574, 2608.01856, 2607.13188, 2601.14041)
22. conformal diffusion language (none relevant)
23. masked diffusion corrupted tokens detection (2610.22380, 2605.26436)
24. discrete diffusion noisy context robust (none relevant)
25. masked diffusion vision language hallucination remask (0)
26. unified discrete diffusion self-correction image (2605.04040, not relevant)
27. conformal risk control multimodal (2026 hits: 2609.01375, 2604.12035, others unrelated)
28. diffusion language model uncertainty calibrated tokens (2610.05125 and unrelated)
29. masked diffusion multimodal robustness (16 hits; 2602.02927 known; 2605.14530, 2605.07399, 2603.25711 judged unrelated on title only)
30. masked diffusion conformal (none relevant)
31. diffusion language model false alarm (0 in 2026)
32. unified multimodal diffusion cross-modal consistency remask (0)

Hits screened on title/abstract: about 60 distinct items. Opened (abstract page or text): 17. Read at text level: CO2Jump, Trust but Verify (partial), Gomes (via summariser). The first audit's 32 ids and the closest-work file are not repeated.

## 4. Hits that matter (id, date, overlap, non-overlap)

| id | date (v1) | level | overlaps with GATE | does not overlap |
|---|---|---|---|---|
| **2610.22380** Trust but Verify (Jhingran; NeurIPS 2026 workshop "AI for Stochastic Dynamics") | 2 Oct 2026 | E2-partial | Detects corrupted **conditioning/context** tokens in a masked discrete diffusion model from the model's own probability of the observed token (Eq. 4, "free suspicion score"), re-noises them to the absorbing state, refills with bidirectional context (detect-remask-refill, Alg. 1). Reports recall 0.96 / precision 0.91 on uniform corruption and a **false-edit rate on clean context** (under 0.4% in the abstract; 1.07% for arm D in the results text). Closest statement of "input reliability by the model's own likelihood, then remask". | Text only, one 170M model; requires an 8,000-step finetune with uniform-mixing noise on context (its arm B says a model trained only under absorbing dynamics gives no meaningful likelihood to observed positions); score is the probability at the **unmasked** position, not a mask-then-score likelihood; threshold annealed 0.5 to 0.1 by hand, plus an edit budget from an assumed 15% corruption rate, so no calibration guarantee; no cross-modal evidence, no verification task; plausible corruptions detected only partially (gains about 0.5 F1, not significant) |
| **2504.01225** Gomes, Martins, Zerva, CRC for CLIPScore (Findings of ACL 2025) | 1 Apr 2025 | E1+ | Conformal risk control with **masking-derived score distributions** to flag erroneous/foil **caption words** given an image (FDR on FOIL-it/nocaps, FPR on Rich-HF); masks caption words and image patches; word-level, subword pieces masked together; a guarantee tied to a chosen risk level. Direct prior art for "CRC + masking scores + word gate + vision-language". | CLIP embeddings, not a generative MDM; the score is the CLIPScore change under masking (cross-modal), not within-modality likelihood; calibrated on labelled foil data controlling FDR/FPR, not on clean pairs controlling the clean false-alarm proportion; bound is high-probability (concentration bound, Bentkus/Hoeffding), not expected-loss CRC; no image-token gate, no remask/repair, no evidence fusion |
| 2607.13188 CO2Jump | 14 Jul 2026 | E2 (Sec 1-4) | See section 2. | See section 2. |
| 2606.12807 Detect-Remask-Repair (Zou et al.) | 11 Jun 2026 (v2 3 Sep) | abstract only | Uses masked diffusion LMs to find outdated summary spans, mask and rewrite them. | Text only, summarisation staleness; detector not described in abstract; no calibration |
| 2512.15596 Corrective Diffusion LMs (Zhang et al.) | 17 Dec 2025 | abstract only | Post-training so the model lowers confidence on wrong visible tokens and localises errors (Code Revision Benchmark). | Text/code; trained, not training-free; no calibration |
| 2606.06031 NAVIRA | 4 Jun 2026 | abstract only | Two-pass decoupled score-then-remask (flag in pass 1, regenerate from cleaned context in pass 2). Same structure as GATE's score-then-mask. | Output tokens, text-only 170M, no calibration |
| 2510.01384 PRISM (ICLR/ICML 2026) | 1 Oct 2025 | abstract only | Learned per-token quality head, remask low scorers. | Output tokens; trained head; text/Sudoku/code |
| 2602.04096 CoRe | 4 Feb 2026 (v3 13 Mar) | abstract only | Training-free remasking of "context-brittle" tokens by perturbing the masked context. | Output tokens, LLaDA-8B text, no calibration |
| 2604.18738 / 2605.26436 token-to-mask refinement | Apr 2026 / 6 Apr 2026 (v2 withdrawn) | abstract only (2605.26436) | Remask rather than replace a suspect token; three error detectors. | Output tokens, text |
| 2608.26574 DARD | 27 Aug 2026 | abstract only | Excludes unreliable decoded tokens from the verification context; includes Flickr30K captioning. | Decoded tokens, not input; no calibration |
| 2509.23625 RIV (mask diffusion VLM) | 28 Sep 2025 | abstract only | Introspection and remasking in a diffusion VLM. | Own generated text; trained introspector |
| 2602.11590 ProSeCo; 2509.23653 RemeDi | 2026 / 2025 | snippet only | Learned self-correction in diffusion LMs. | Output tokens, trained |
| 2604.12035 Confidence under visual token pruning | 13 Apr 2026 (v4 4 Oct) | abstract only | CRC calibrates a confidence threshold for a prune-then-re-answer cascade in MLLMs; conformal + visual tokens. | Tokens removed by a pruner, not corrupted tokens; probably autoregressive; no masked likelihood |
| 2609.01375 IntroConformal | 1 Sep 2026 | abstract only | CRC with model-internal signals for LVLM claim-level factuality. | Claim-level abstention, LVLM outputs; not input tokens, not diffusion |
| 2209.07068 uChecker (2022); 2005.07421 soft-masked BERT | 2022 / 2020 | snippet only | Masked LM probability of the original token as a typo detector, fixed threshold. Prior art for masked-likelihood token anomaly scoring in text. Salazar et al. 1910.14659 (PLL) and Kauf and Ivanova 2305.10588 (PLL-word-l2r, relevant to multi-piece words) cited in the spec. | Single modality, MLMs not diffusion, no conformal |
| 2305.16397 Diffusion ITM (NeurIPS 2023) | May 2023 | snippet only | Image-text matching with a generative diffusion model, conditional error normalised by unconditional error (a PMI-like score); beats CLIP on compositional tasks. Prior art for the null-normalised evidence term. | Continuous latent diffusion, no gate |
| 2503.20853 UniDisc | Mar 2025 | known | Retrieval reported; App. G.1 random mask + re-infill of corrupted pairs. | Already covered in CLOSEST-WORK |

Checked and judged unrelated on title/abstract: 2605.07399 (jailbreaking a diffusion VLM), 2605.14530, 2603.25711 (hallucination in diffusion VLMs, output side), 2610.05125 BayesER (calibration error of output sequences, no conformal), 2608.01856 EchoChange (dual-pass remasking for captioning).

Conformal prediction for masked diffusion tokens: nothing found (searches 1, 6, 19, 22, 30). TECP (2509.00461, snippet) uses token entropy conformal scores for autoregressive LLMs.

## 5. Difference matrix, closest 10

Cells: S same, P partial, D different (relative to GATE).

| Work | Question (input-token reliability) | Mechanism (within-modality masked likelihood, other modality masked) | Method (calibrated threshold, CRC) | Evidence type (known corruption maps, FAP) | Scale/model (unified MDM, pretrained, no finetune) | Result/use (remask/marginalise then cross-modal verification) |
|---|---|---|---|---|---|---|
| Trust but Verify 2610.22380 | S (conditioning tokens) | P (own probability of observed token, unmasked, finetuned) | P (clean false-edit rate reported, threshold heuristic) | S (known corrupted positions, precision/recall, false-edit) | D (170M text, finetune) | P (re-noise and refill; no verification) |
| Gomes CRC-CLIPScore 2504.01225 | P (caption words vs image) | P (masking-derived, cross-modal CLIP score) | S (CRC, but foil-calibrated FDR/FPR, high-prob bound) | P (FOIL labelled foil words) | D (CLIP) | D (flag only) |
| CO2Jump 2607.13188 | D (own generations) | D | D | D | P (unified MDM, finetuned) | P (remask, cross-modal trigger) |
| UniDisc App. G.1 2503.20853 | S (corrupted pairs) | D (random) | D | D (qualitative) | S | P (re-infill, best of n) |
| FreeCorrection 2602.02927 | D (own output) | P | D | D | P (multimodal MDM) | P |
| Dropout Decoding 2412.06474 | P (visual tokens, uncertainty) | D (projection-based) | D | D | D (AR LVLM) | D |
| DiSP 2602.22246 | P (visual inputs, saliency) | D (gradient) | D | D | D (continuous inputs) | D |
| PRISM 2510.01384 | D (own output) | D (learned head) | D | D | D | P (remask) |
| uChecker 2209.07068 | S (typo tokens) | S (masked likelihood, text MLM) | D (fixed threshold) | P | D (MLM) | D |
| Diffusion ITM 2305.16397 | D | D | D | D | D | P (null-normalised likelihood for matching) |

No single row is S across question, mechanism and method. The composition of the three columns "input-token question + within-modality masked likelihood + CRC" is new in this set; each pair is partly covered (question+mechanism by Trust but Verify, question+method by Gomes, mechanism+question by uChecker).

## 6. Last-90-days check (29 Jul to 28 Oct 2026)

Found: Trust but Verify (2 Oct), BayesER (4 Oct), DARD (27 Aug), IntroConformal (1 Sep), CRC-token-pruning v4 (4 Oct), EchoChange (3 Aug). Only Trust but Verify is on-topic. arXiv search pages for remask, conformal, diffusion language and multimodal returned nothing else within the window. OpenReview ICLR 2027 (deadline passed or not public) and NeurIPS 2026 camera-ready listings could not be searched; treat as open residual risk. ICLR 2027 submissions typically become visible after the deadline; recheck once before submission.

## 7. Does GATE's delta remain open?

Delta as specified (section 11 of the spec): input-token reliability via within-modality masked likelihood + conformal false-alarm control + cross-modal PMI fusion, on a unified MDM.

- **Input-token reliability inside an MDM:** no longer new as an idea. Trust but Verify did it for text with a finetuned 170M model, with a clean false-edit rate and partial detection of plausible corruptions. What remains: pretrained unified model, no finetune, mask-then-score rather than score-at-unmasked-position, two modalities.
- **Conformal false-alarm control:** open for MDMs (no hit). Not open as a general idea (Gomes uses CRC with masking scores for caption word errors with an image; CRC itself is Angelopoulos et al.). GATE's differences are real but technical: calibration on clean items to bound the clean false-alarm proportion in expectation, token-level losses nested inside an item, and a within-modality score.
- **Cross-modal PMI fusion:** the null-normalised likelihood is known (Diffusion ITM; UniDisc retrieval). The fusion rule (LDA) and the evidence-separation rule are GATE's, but are design choices, not a research question until tested.
- **Marginalise versus impute:** Prop. 1 is a direct consequence of the MDM objective (any-order/time-free denoiser results; arXiv 2507.07586 shows the absorbing MDM models the posterior). Prop. 6 and 7 are small calculations. The empirical comparison at matched passes is open.

### Contribution sentence that survives
"On a pretrained unified text-image masked diffusion model, with no finetuning, we score each input token by its masked likelihood in its own modality with the other modality withheld, set the flag threshold by conformal risk control on clean pairs so that the expected false-alarm proportion on clean inputs is at most alpha, and measure whether re-masking or re-infilling the flagged tokens preserves two-way cross-modal verification under image-token and caption corruption."
Caveat: this survives only as a measurement paper. Every outcome clause (preserves, better than random or uncertainty-ranked gate) is a hypothesis with no result yet, and Trust but Verify reports that plausible corruptions are barely detectable even with finetuning, which is the same risk the spec lists as F5 for JPEG/noise.

### Claims the paper must NOT make
1. First to detect and re-mask corrupted conditioning or input tokens in a masked diffusion model (Trust but Verify, 2610.22380).
2. First to re-mask or self-correct in a unified multimodal MDM, or first to use cross-modal evidence as a remask trigger (CO2Jump 2607.13188; FreeCorrection 2602.02927; UniDisc G.1).
3. First use of conformal risk control or a risk-controlled threshold with masking-derived scores for token or word error detection in vision-language (Gomes et al. 2504.01225). Do not describe the clean-FAP calibration as the first guarantee for flagging erroneous captions words.
4. First masked-likelihood detector of anomalous tokens (uChecker, Salazar PLL, soft-masked BERT, ELECTRA), or first use of a null-normalised generative likelihood for image-text matching (Diffusion ITM).
5. Prop. 1 as a new theorem (it is the standard MDM denoiser property); Prop. 5 as a new conformal result (it is CRC applied).
6. Any guarantee beyond the stated one: no bound on detection power, none on false alarms among the clean tokens of a corrupted item, none under calibration/test shift; "certified robust" or "provably reliable" wording.
7. Training-free novelty framed as the contribution, as such: other remasking methods are also training-free (CoRe, Targeted Remasking, ReMDM).
8. Any statement that GATE improves verification, repair or T2I under corruption before E-runs exist.
9. Generality beyond the tested model (spec F15): do not generalise from UniDisc 1.4B.

### Reviewer exposure
- "Hasn't Trust but Verify done this?" Answer ready: text-only, finetuned, unmasked-position score, hand threshold, no cross-modal evidence. Must cite and compare in related work; GATE should include a baseline in the spirit of its score (probability at the unmasked observed position) if the UniDisc logits allow it, otherwise state the difference.
- "Gomes already has CRC + masking for caption word errors": cite; explain clean-pair calibration versus foil-calibrated FDR, generative within-modality score, image-token gate.
- "CO2Jump remasks with cross-modal confidence": cite; explain input versus generated tokens and the evidence-separation rule.

Ledger rows added: 0 (brief: write only this report). Candidate rows for the orchestrator: 2610.22380, 2504.01225, 2606.12807, 2512.15596, 2606.06031, 2604.12035, 2609.01375.
