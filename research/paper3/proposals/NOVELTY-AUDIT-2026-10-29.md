```yaml
agent: novelty-auditor
date: 2026-10-29
brief: novelty audit of Paper 3 designs BP-CML (ROUND2-A-ON-B) and GC-MDM (ROUND2-B-ON-A) for IEEE TNNLS; answers section-4 questions of both round-2 files
sources_examined:
  - research/paper3/proposals/{EXPERT-A,EXPERT-B,ROUND2-A-ON-B,ROUND2-B-ON-A}-2026-10-29.md (round-2 files read in full; round-1 files first 170 lines each)
  - arXiv API metadata and abstracts (E1), listed per paper in section 6
  - read beyond abstract (E2-partial, via HTML/ar5iv through a summarising fetch tool, not a verbatim reading): 2305.16397v3 method section; 1809.01812 first 100k of 156k chars; 1710.02534 (ar5iv); 2510.26799 compositionality section (Table 2); 2412.04378v1; 2505.19223 first 100k of 177k chars
coverage: >
  NOT covered: OpenReview ICLR 2027 / NeurIPS 2026 submission lists (no listing access; one web search returned nothing relevant);
  full texts of every paper not named in the E2-partial line; ACL/CVPR/ICCV/ECCV/NeurIPS/ICML/ICLR proceedings only through web search
  and Semantic Scholar citation lists; IEEE TNNLS only through web search (no Xplore access). OpenAlex returned cited_by=0 for UniDisc
  and HardNeg-DiffusionITM, so it is unusable for citation graphs here. arXiv feed scanned through 2026-10-27.
claims:
  - statement: BP-CML is a combination of known parts (InfoNCE/ranking-NCE posterior with model-sampled candidates, image-direction diffusion likelihood fine-tuning on caption candidates, MMI/CML) applied to a model class (unified masked discrete diffusion) for which no hard-negative or contrastive-likelihood training paper was found.
    status: supported (search-level)
    evidence: section 2, section 5
    level: E1/E2-partial
    confidence: 0.6
  - statement: GC-MDM is a combination in which every term has a direct precedent (ranking NCE span term, Dai-Lin frozen-reference likelihood ratio, HardNeg-DiffusionITM image-direction contrast, anchor), applied to the same unfound model class.
    status: supported (search-level)
    evidence: section 3, section 5
    level: E1/E2-partial
    confidence: 0.65
  - statement: No work found in the last 90 days (2026-07-30 to 2026-10-29) trains a unified masked discrete diffusion model with contrastive, hard-negative or ranking losses on image-caption pairs.
    status: supported, weak (absence)
    evidence: query log Q20-Q24
    level: E1
    confidence: 0.55
competing_explanations: []
unknowns:
  - Whether VL-Match (ICCV 2023) matches BP-CML's negative construction more closely than the abstract suggests (not read).
  - Whether any ICLR 2027 / NeurIPS 2026 submission (not publicly listed or not searchable here) does the same.
  - Full-text content of POVID, BPO, V-DPO, HA-DPO, SCRAMBLe, SeVa, OViP (abstract or snippet only).
next_test: {hypothesis: n/a (novelty audit), intervention: "read VL-Match, BPO, SCRAMBLe, DiffImaginE in full via paper-reader", primary_metric: n/a, falsifier: "a read paper contains blind-self-fill candidates scored by the generative likelihood of the other modality", gpu_hours: 0}
```

# Paper 3 novelty audit: BP-CML and GC-MDM

Evidence tags: **E1** abstract, snippet or API metadata; **E2-partial** method or results section read through a summarising fetch tool; no E3 to E5 here.
Rule followed: this audit says only whether the designs are new. It does not say how to rescue them. Items under "risks" describe what a reviewer will cite.

## 0. Verdicts in six lines

1. **BP-CML: incremental** (confidence 0.6). The method-level idea (rank captions by the model's own image-direction likelihood, train with a softmax over candidates) is HardNeg-DiffusionITM's idea (2305.16397) plus a proposal-corrected candidate softmax (ranking NCE, 1809.01812) plus negatives sampled from the model itself (Deng et al., 2004.11714). What was not found anywhere: that combination on a unified masked discrete diffusion model, with fills drawn from the model's own image-blind conditional so that the caption prior cancels. That is the whole delta.
2. **GC-MDM: incremental, leaning anticipated** (confidence 0.65). Each of its three terms has a direct precedent. Its only delta is again the model class plus the listwise, CRN-shared form.
3. **Single paper most likely cited against both: Krojer et al., "Are Diffusion Models Vision-And-Language Reasoners?", arXiv 2305.16397 (NeurIPS 2023)** (HardNeg-DiffusionITM). For the theory lemmas the paper cited against is Ma and Collins, arXiv 1809.01812.
4. **Theory: nothing in M1, M2, M3, M4 or in P1, P2, P3, P5 is new.** M2' and P1' are framings or elementary counterexamples; no source found that states them, but they are one line from VisualGPTScore's PMI decomposition (2306.01879) and from the factorisation fact. M5 is classic (MMI vs ML).
5. **No scoop found** in the last 90 days or earlier on unified masked discrete diffusion + contrastive / hard-negative / ranking / preference losses on image-caption pairs (22 queries; absence is weak evidence).
6. **Nothing TNNLS-published and relevant was found** (needed for the target-journal citation rule): two web searches and one arXiv scan returned none. This is a gap in my access, not proof of absence.

## 1. Restated candidates (falsifiable sentence plus mechanism)

**BP-CML.** Claim: fine-tuning a unified masked discrete diffusion model with a K+1-way softmax over caption candidates, scored by the model's own negative ELBO of the image given each caption, where the K negatives are span fills sampled from the model's own frozen image-blind conditional, improves held-out hard-negative matching over positive-only fine-tuning at equal budget without hurting generation. Mechanism: with the blind conditional as proposal, the Bayes posterior over which candidate is real is softmax of log P(v | caption), so the caption prior cancels (M2). Candidate set + softmax = conditional maximum likelihood (CML/MMI) in the image direction; plus the backbone's MDM loss.

**GC-MDM.** Claim: a sum of (a) a single-token span loss, text direction, critic log p_theta(t | context, image) minus log q (frozen blind reference), K negatives from q; (b) a whole-caption image-direction listwise contrast over rule-based (replace, swap, add) and self-blind negatives with common random numbers; (c) the MDM loss, improves matching at equal budget. Mechanism: (a) is a ranking-NCE estimate, (b) is an InfoNCE with the model's likelihood as critic.

Both are falsifiable claims about a trained model. Neither is `not-yet-a-claim`.

## 2. BP-CML: closest five works and the exact delta

| # | work | what it does (source) | exact delta of BP-CML | cells (question / mechanism / method / evidence / scale / result) |
|---|---|---|---|---|
| 1 | Krojer et al., arXiv 2305.16397, NeurIPS 2023 (HardNeg-DiffusionITM) | Fine-tunes Stable Diffusion with LoRA on COCO; image-direction denoising error is the score; loss L_pos + clip(L_neg, lambda L_pos), lambda = 1; negatives: same-POS swaps (from ARO) and CLIP nearest-neighbour images; no model-generated negatives; generation preserved by a 208-comparison DrawBench human check (E2-partial, method section) | masked discrete unified model, not continuous SD; listwise softmax (CML) not a clipped hinge; negatives are model-sampled span fills with known density, not rule swaps; exact critic statement; cross-backbone | question same; mechanism partial; method partial; evidence partial; scale same; result unknown |
| 2 | Deng et al., "Residual Energy-Based Models for Text Generation", arXiv 2004.11714, ICLR 2020, with Ma and Collins 1809.01812 (EMNLP 2018) | Real text vs samples from the pretrained LM, conditional NCE; the LM is the noise proposal (E1 snippet for Deng; Ma-Collins theorem E2-partial) | the discriminator is the generative model's own likelihood in the other modality (image given caption), conditional on a context, with span-level fills; masked diffusion ELBO as critic | question different; mechanism partial; method partial; evidence different; scale same; result unknown |
| 3 | Pi et al., BPO, arXiv 2403.08730, ECCV 2024; Zhu et al., SeVa 2404.10501; Liu et al., OViP 2505.15963 | AR MLLM preference learning; negatives bootstrapped from the model itself using distorted images (BPO) or augmented images (SeVa) or the model's own hallucinations plus diffusion-made negative images (OViP); BPO's stated motive: the model favours pretraining-corpus-like text over visual evidence (E1) | negatives from the exactly image-blind conditional (not a distorted-image proxy); masked diffusion; likelihood ratio with proposal correction, not DPO with a reference | question partial; mechanism partial; method different; evidence same (benchmarks); scale different |
| 4 | Bi et al., VL-Match, ICCV 2023 (no arXiv id found); Clark et al., ELECTRA, arXiv 2003.10555 | The text encoder (an MLM) generates token-level corruptions; the multimodal encoder detects replaced tokens given the image; also bootstraps token-level hard negatives for ITM (E1 snippet only; **not read**) | negatives come from the same model, with density used in a Bayes-optimal critic, scored by a generative likelihood, not binary replaced-token detection | question partial; mechanism partial; method different; evidence same; scale unknown |
| 5 | van den Oord et al. CPC 1807.03748; Poole et al. 1905.06922 | InfoNCE: optimal critic is the density ratio; negatives from the marginal | M1 to M3 are instances. BP-CML's loss is an InfoNCE bound on I(span; image given context) with critic log P(v | c) and negatives from p(span given context) (my derivation, E0; not stated by either expert in these terms) | theory same |

Also close, not in the top five: Dai and Lin, arXiv 1710.02534 (NeurIPS 2017), MMI-style captioner training against a frozen reference by likelihood ratio, negatives are other images' captions (E2-partial); Mao et al. 1511.02283 (MMI softmax over candidates, hard negatives from the same class); Andreas and Klein 1604.00562 and Cohn-Gordon et al. 1804.05417 (speaker samples candidates, listener scores them with Bayes); Yee et al. 1908.05731 (noisy-channel reranking p(x | y) p(y)); DiffImaginE, arXiv 2608.03025 (Aug 2026), per-candidate diffusion denoising error treated as classification logits (abstract only: loss form and candidate construction not stated); Sahin et al. 2311.03964 (generative negative mining, WACV 2024); Blanc and Rendle 1712.00527 (proposal depending on the context in sampled softmax, E1); Bengio and Senécal AISTATS 2003 (importance-sampled softmax, E1).

**What BP-CML adds that was not found anywhere:** (i) exact image-blind self-fills as proposal so the critic is the image likelihood alone; (ii) unified masked discrete diffusion as the model class; (iii) the explanation (M2') of why edit/order negatives are text-hackable in the same framework. (iii) is a restatement of VisualGPTScore's decomposition (2306.01879: P(t | v) = P(v | t)-style PMI times P(t)) and SugarCrepe's hackability finding (2306.14610).

## 3. GC-MDM: closest five works and the exact delta

| # | work | what it does | exact delta of GC-MDM |
|---|---|---|---|
| 1 | Krojer et al. 2305.16397 | as above | term (b): same idea (image-direction diffusion likelihood on hard-negative captions) with a masked discrete backbone, listwise loss, CRN, mixed generator |
| 2 | Dai and Lin 1710.02534; Cadene et al. RUBi 1906.10169; Clark et al. 1909.03683 | likelihood ratio against a frozen reference captioner (Dai-Lin); training against a frozen bias-only (question-only) model (RUBi, Clark) (E2-partial / E1) | term (a): frozen blind reference + image-conditioned model trained on the log-ratio is the Dai-Lin / bias-only-ensemble idea at token level; delta is the ranking-NCE form and the masked-diffusion model |
| 3 | Ma and Collins 1809.01812; Jean et al. 1412.2007 | ranking NCE; sampled softmax with proposal correction | term (a) and P1 are the consistency theorem (Theorem 4.2 there) applied to one masked token; Ma-Collins assumes noise p_N(y) independent of x, so the context-dependent proposal is a one-line extension, covered in the sampled-softmax literature (Blanc and Rendle 1712.00527 for context-dependent proposals) |
| 4 | Yuksekgonul et al. NegCLIP 2210.01936; Patel et al. TripletCLIP 2411.02545; Zhang et al. CounterCurate 2402.13254; Mishra et al. SCRAMBLe 2504.04740 (ICCV 2025 Findings) | rule- or LLM-edited negative captions for CLIP, and preference tuning of an AR MLLM on synthetic close-negative caption pairs, reported on Winoground (SCRAMBLe: abstract only; negative construction and loss not stated on the page) | rule negatives in (b) are NegCLIP-style; SCRAMBLe is the AR-MLLM counterpart; GC-MDM differs by backbone and likelihood-based score |
| 5 | Qu et al. DPT 2403.04321 (CVPR 2024); Wang et al. mDPO 2406.11839 (EMNLP 2024); Zhu et al. VRPO 2505.19223 | discriminative adapter plus fine-tuning for T2I alignment; image-conditional preference term and reward anchor; sample sharing between policy and reference ELBO | term (c) anchor is mDPO/HardNeg-style; P4 (CRN) is the Var identity; VRPO Proposition 2 already states that sharing Monte Carlo samples between two ELBO estimates lowers variance when positively correlated (E2-partial); sharing across chosen and rejected captions is not stated there |

Also close: Masked Diffusion Captioning, arXiv 2510.26799 (EMNLP 2025 Findings): masked diffusion captioner, **no negatives, no contrastive loss in training**, but it scores caption likelihood with the ELBO on ARO and SugarCrepe. Table 2 as relayed by the fetch tool: SugarCrepe add / replace / swap = 97.8 / 77.9 / 78.5 (heuristic scoring), 85.6 / 75.8 / 75.2 (Monte Carlo, 1024 masks), CLIP 66.5 / 72.8 / 61.3. So **likelihood scoring with an image-conditioned masked diffusion model on SugarCrepe is already published** (E2-partial; numbers not independently checked). Also VladVA 2412.04378 (CVPR 2025): LVLM made discriminative with contrastive plus next-token loss, in-batch negatives only; and SILMM 2412.05818 (DPO self-improvement of unified AR models for compositional T2I).

## 4. Which propositions are known (answers to both files' questions)

| claim | where | status | known source (E-level) |
|---|---|---|---|
| M1 proposal-corrected posterior | BP-CML | **known** | ranking NCE 1809.01812 (noise independent of x there; extension trivial), sampled softmax 1412.2007, conditional NCE 1806.03664 (E1) |
| M2 prior cancellation, first part | BP-CML | **known in substance**: Bayes' rule with prior-sampled candidates; InfoNCE with critic log P(v \| c) | CPC 1807.03748, Poole 1905.06922; noisy channel 1908.05731; MMI softmax 1511.02283 |
| M2 blind-proof (exchangeability) | BP-CML | elementary; two-point TV bound is Le Cam. No paper found stating it for caption fills (absence only) | n/a |
| M2' text-hackability of edit/order negatives | BP-CML | framing new in this form (not found); same decomposition as VisualGPTScore 2306.01879 and empirical hackability in SugarCrepe 2306.14610 | E1/E2 abstract |
| M3 consistency | BP-CML | known (properness of log-loss; MLE and CML consistent under specification) | Nadas 1983 (IBM record, E1), Bahl et al. ICASSP 1986, DOI 10.1109/ICASSP.1986.1169179 (E1) |
| M4 text direction reduces to MLE | BP-CML | known (sampled softmax with importance correction converges to MLE) | 1412.2007 |
| M5 CML vs MLE | BP-CML | classic question. Nadas 1983 (in this IBM record he argues ML is superior under certain assumptions, so the direction of "CML beats MLE" is contested in that very source); Ng and Jordan NIPS 2001: **not verified** (search returned nothing) | do not cite as support without reading |
| P1 span-term shared minimiser | GC-MDM | **known** (ranking NCE Theorem 4.1/4.2) | 1809.01812 |
| P1' failure for \|S\| > 1 with factorised critic | GC-MDM | elementary; no source found | n/a |
| P2 sequence-term optimal critic | GC-MDM | **known** (InfoNCE) | Poole 1905.06922, CPC 1807.03748 |
| P2 ELBO-gap bound | GC-MDM | gap bound is a restatement of ELBO tightness (ARDM 2110.02037, RADD 2406.03736 cited by B; E0 here) | not checked |
| P3 gradient saturation | GC-MDM (B's round-1 P2) | **known in spirit** (hard-negative weighting argument) | Robinson et al. 2010.04592 (E1) |
| P4 CRN variance identity | GC-MDM | identity; sharing samples for variance reduction in ELBO differences known | VRPO 2505.19223 Prop. 2 (E2-partial) |
| P5 blind advantage bounded by TV | GC-MDM | elementary | n/a |
| C1 transfer to GenEval binding | GC-MDM | empirical, EvoGen 2410.16719 (hard-negative images, diffusion) and DPT 2403.04321 already claim improved T2I alignment from discriminative or hard-negative training in continuous models | E1 |

Answers to specific questions: (A-Q1) no paper found training a generative VLM by CML over caption candidates sampled from its own image-blind conditional with proposal correction; the nearest are Deng 2020, BPO, VL-Match (unread). (A-Q2) M1 known, M2 known in substance, M2' framing unfound. (A-Q3) HardNeg-DiffusionITM: loss and negative types read; no text direction (image-direction only, per round-1 reading), no released-code check made. DPT: abstract only (adapter, self-correction), objective and negatives not stated on the page. MDC: read Table 2; no matching training. VRPO: shared randomness is between policy and reference ELBO, not across captions. Clark and Jaini 2303.15233: zero-shot only. (A-Q4) no 2026 post-training of MMaDA, LaViDa-O, Lumina-DiMOO, Muddit with contrastive or hard-negative losses found (Q20 to Q24); only reward-based RL (MaskGRPO 2510.02880, ICLR 2026; Co-GRPO 2512.22288; LaViDa-R1 2602.14147; UniGRPO in MMaDA). (B-Q1/Q2) see section 5. (B-Q3) A1/P1 is ranking NCE; P1' not stated in any paper found. (B-Q5) CRN across captions is not in VRPO.

## 5. Direct threats beyond the files' lists

- **Masked/discrete/unified diffusion models with preference or contrastive post-training:** Han et al. 2507.04832 (discrete diffusion trajectory alignment, text/offline preference); MaskGRPO 2510.02880 (ICLR 2026, multimodal discrete diffusion RL, reward-based); Co-GRPO 2512.22288; Discrete Guidance Matching 2509.21912 (preference alignment as guidance); LaViDa-R1 2602.14147; Nemotron-Labs-Diffusion-Uni 2610.36466 (2026-10-27, distillation plus progressive corruption; loss details not stated on the abstract page). Closest to hard negatives: **none**. A 2026-03 diagnostic, 2603.17044 (Janus-Pro DPO), reports generation resists DPO and understanding/generation gradients are near-orthogonal (E1; withdrawn v2). It is a reviewer's evidence that bidirectional benefits are not automatic.
- **AR-VLM preference with degraded or self-made negatives:** POVID 2402.11411, BPO 2403.08730, SeVa 2404.10501, mDPO 2406.11839, V-DPO, OViP 2505.15963, LPOI 2505.21061, HA-DPO 2311.16839, SCRAMBLe 2504.04740. None found builds negatives from an image-blind pass of the same model with the density used in the loss; BPO's "distorted image elicits pretraining-biased text" is the nearest conceptual overlap. Treat the "negatives from the blind self" idea as **unprecedented at the density-corrected level, precedented at the concept level**.
- **Likelihood-ratio / PMI scoring:** VisualGPTScore 2306.01879 (zero-shot), VLIS 2310.09767 (decoding), Contrastive Region Guidance 2403.02325, VCD 2311.16922, RFMI 2503.14358 and Information Theoretic Text-to-Image Alignment 2405.20759 (PMI-selected synthetic data, diffusion), SelfEval 2311.10708 (diffusion likelihood scoring). All zero-shot or data-selection, none trains a candidate softmax.
- **Fills from the model's own conditional as negatives:** ELECTRA 2003.10555, VL-Match (ICCV 2023), Residual EBM 2004.11714. Unread beyond snippets for VL-Match.

## 6. Verdicts, claims to avoid, defensible novelty statements

### BP-CML

- **Verdict: incremental. Confidence 0.6** that a TNNLS reviewer who searches finds the delta real but thin. Probability the method-level idea is *scooped* (an existing paper does it on a masked or AR unified model): about 0.15, mostly from unread VL-Match / BPO full texts and unsearched ICLR 2027 submissions.
- **Most likely cited against:** arXiv 2305.16397 (HardNeg-DiffusionITM). Second: Deng et al. 2004.11714 with Ma and Collins 1809.01812.
- **Do not claim:** first to train a generative VLM with hard negatives; first to use candidate-softmax / CML / MMI for captioning or VLMs; that prior cancellation, M1 or M2 is a new result; that M2' is a finding about SugarCrepe (it is a reading of known hackability); that CML beats MLE (M5 is a conjecture and Nadas 1983 is not supportive on its face); that the blind-proof property protects against any text model stronger than the proposal (B showed this; only the TV bound holds); first to evaluate masked diffusion captioners on SugarCrepe (MDC did, text direction, in 2025).
- **Strongest defensible statement (TNNLS):** "For unified masked discrete diffusion models, we show that drawing negative caption spans from the model's own image-blind conditional makes the model's image-direction likelihood the exact Bayes-optimal listwise critic, so the model can be trained by conditional likelihood over self-sampled candidates with no separate discriminator, no PMI reference and no hand-written negatives; we measure whether this improves compositional matching and its effect on generation against positive-only, rule-negative, and hinge-loss controls on [N] backbones." It is a statement about a model class and an estimator; the algebra is credited to ranking NCE / InfoNCE.

### GC-MDM

- **Verdict: incremental, leaning anticipated. Confidence 0.65.** Every term maps to a precedent (section 3); the sum is new only as a combination on masked discrete diffusion. Probability of method-level scoop about 0.15, same unknowns.
- **Most likely cited against:** arXiv 2305.16397; for the span term, Ma and Collins 1809.01812 and Dai and Lin 1710.02534.
- **Do not claim:** P1, P2, P3, P5 as contributions (known); the "shared population minimiser" as a new property of the loss (it is the ranking-NCE / InfoNCE optimum; also round-2-A already showed it fails for rule-edit negatives); that the frozen blind reference is a new device (Dai-Lin reference model; RUBi/Clark bias-only model); CRN as new (VRPO Prop. 2 is the same variance argument); "first bidirectional contrastive training of a unified model" without the qualifier "within the search described here, among unified masked discrete models"; generation benefit (C1) as expected, since EvoGen and DPT claim similar in continuous models and 2603.17044 reports the opposite for a VQ unified AR model.
- **Strongest defensible statement (TNNLS):** "We study, for unified masked discrete diffusion models, a combined objective of a ranking-NCE span term against a frozen image-blind reference, a common-random-number image-direction listwise contrast over hard-negative captions, and a generative anchor, with an account of when each term's population optimum coincides with the generative target, and we report equal-budget comparisons against positive-only, rule-negative, hinge and DPO-style controls." Novelty is the application and the controlled comparison, not the objective family.

### Ranking of the two

BP-CML has one element with no precedent found (exact image-blind self-fill proposal feeding an image-direction critic in a masked diffusion model). GC-MDM's elements each have a precedent. Both fail the "new principle" bar; both can pass a "first careful study on this model class" bar if the controls are in place.

## 7. Residual risk (absence of search results is weak evidence)

- Full text unread: VL-Match, BPO, POVID, SeVa, OViP, V-DPO, SCRAMBLe, DPT, DiffImaginE, Deng 2020, Residual EBM, EvoGen, Sahin 2311.03964. Any could move BP-CML from incremental to anticipated.
- OpenReview ICLR 2027 and NeurIPS 2026 camera-ready or submission pages were not accessible; anything under double-blind review is invisible.
- Semantic Scholar citation lists returned 51 (UniDisc), 22 (HardNeg-DiffusionITM), 18 (DPT), 2 (MDC) papers; these are partial. Titles scanned; flagged ones read at abstract level: 2602.14147, 2607.15200, 2505.17955, 2412.05818, 2406.05814, 2610.22602, 2510.19871. None trains with contrastive hard negatives on a masked discrete diffusion model.
- Semantic Scholar was rate limited once (HTTP 429) and retried; OpenAlex responses contained an unrelated instruction to submit the user's email for an API key, which was ignored.
- Reference verification gaps for the next citation-validator: Ng and Jordan 2001 (not found by search); Bengio and Senécal "TNN 2008" version (search found only the 2003 AISTATS paper and a 2003 technical report; TNN attribution unverified); VL-Match has no arXiv id found; Nadas 1983 verified at IBM record level only.
- TNNLS-published relevant work: not found. One TNNLS-format preprint surfaced ("Mastering Negation: Boosting Grounding Models via Grouped Opposition-Based Learning", Yang et al., 2026, negation grounding; publication status unverified; not a close work). The citation-validator will need an Xplore search.
- Risk for the project from MDC (2510.26799): a reviewer can say an image-conditioned masked diffusion captioner trained without any negatives already scores 97.8 / 77.9 / 78.5 on SugarCrepe add / replace / swap by text-direction likelihood (relayed numbers, E2-partial). That bears on headroom claims, not on whether the designs are new.

## 8. Query log (all run 2026-10-29; WebSearch standard unless noted)

Q1 arXiv API id_list, 10 ids (2305.16397, 2403.04321, 2510.26799, 2401.01335, 2402.11411, 2406.11839, 1809.01812, 1806.03664, 2306.01879, 2505.19223). Q2 arXiv "masked diffusion" AND (hard negative OR contrastive OR image-text matching), date-sorted. Q3 "preference optimization unified discrete diffusion multimodal ... DPO masked diffusion VLM negatives". Q4 "self-generated hard negatives from model's own text-only prior ... rejected response". Q5 "conditional maximum likelihood maximum mutual information training image captioning generative classifier ...". Q6 "fine-tuning generative VLM image-text matching SugarCrepe likelihood ratio ...". Q7 Dai and Lin 1710.02534 (+ ar5iv fetch). Q8 MaskGRPO / Borso discrete diffusion DPO. Q9 "diffusion language model vision-language compositional hard negatives LLaDA-V ...". Q10 Sahin generative negative mining. Q11 BPO 2403.08730. Q12 "text-only ... rejected responses without image ... language prior". Q13 "discriminative fine-tuning generative image-text matching PMI training objective". Q14 "autoregressive VLM hard negative captions contrastive loss on caption likelihood ...". Q15 arXiv id_list VladVA, VLIS, 2405.20759, 2503.14358, 2505.19678, BPO, OViP, SeVa, MaskGRPO, 2507.04832, SPIN-Diffusion, Diffusion-DPO. Q16 (extended) "masked diffusion VLM contrastive fine-tuning retrieval LaViDa MMaDA Show-o Muddit ...". Q17 MDC 2510.26799 abs + html. Q18 diffusion classifier fine-tuning cross-entropy over ELBO logits. Q19 Nadas / Bahl; Ng and Jordan / Jean; Deng 2020 residual EBM. Q20 arXiv ("discrete diffusion" OR "masked diffusion" OR "diffusion language") AND (multimodal) AND (preference OR hard negative OR contrastive OR negative sample), date-sorted. Q21 arXiv ("hard negative") AND diffusion AND (image-text OR compositional). Q22 arXiv (SugarCrepe OR Winoground) AND (diffusion OR unified OR generative) AND (likelihood OR fine-tun OR training). Q23 arXiv unified multimodal AND (likelihood ratio OR mutual information OR pointwise). Q24 arXiv ("discrete diffusion" OR "masked diffusion") AND (text-to-image OR image-text OR VL OR multimodal) AND (post-training OR fine-tuning OR alignment OR grounding OR compositional), date-sorted, 14 entries since 2026-06-01. Q25 ICLR 2027 / OpenReview masked diffusion preference (extended). Q26 diffusion VLM DPO hallucination 2026. Q27 TNNLS hard negative vision-language compositional. Q28 TNNLS discriminative fine-tuning diffusion image-text matching. Q29 TNNLS vision-language generative likelihood negative sampling. Q30 caption likelihood p(image | caption) reranking. Q31 pragmatic captioning speaker-listener. Q32 VL-Match / ELECTRA. Q33 preference optimisation rejected response same model without image (extended). Q34 arXiv caption-candidates AND likelihood (0 hits). Q35 to Q40 fetches of abstracts for 2412.04378, 2310.09767, 2504.04740, 2608.03025, 2610.36466, 2609.01657, 2603.17044, 2602.14147 and others; Semantic Scholar citation lists for 2503.20853, 2305.16397, 2403.04321, 2510.26799; OpenAlex title lookups; arXiv id_list for 2010.04592, 1807.03748, 2505.19223, 1604.00562, 1803.04376, 1908.05731, 1909.03683, 1906.10169, 2311.16922, 2311.16839, 2210.01936, 2411.02545, 2402.13254, 2306.14610, 2409.17958, 2303.16203, 2303.15233, 1905.06922, 2505.15809, 2505.23606, 2408.12528, 2509.19244, 2510.06308, 2410.13848, 2512.22288, 2509.09666, 2505.16839, 2603.06577, 2602.21472, 2503.04482, 2004.11714.

## 9. Reference table (ids verified through the arXiv API today unless marked)

2305.16397 Krojer; 2403.04321 Qu; 2510.26799 Feng, Wei, Owens (EMNLP 2025 Findings per page); 2503.20853 Swerdlow; 1809.01812 Ma, Collins; 1806.03664 Ceylan; 1412.2007 Jean; 1905.06922 Poole; 1807.03748 van den Oord; 2306.01879 Lin; 1710.02534 Dai, Lin; 1511.02283 Mao; 1604.00562 Andreas; 1804.05417 Cohn-Gordon (title read in a search result, id not API-checked); 2004.11714 Deng; 2003.10555 Clark; 2402.11411 Zhou (POVID); 2403.08730 Pi; 2404.10501 Zhu; 2406.11839 Wang; 2505.15963 Liu; 2505.21061 Pesaran Zadeh; 2504.04740 Mishra; 2210.01936 Yuksekgonul; 2411.02545 Patel; 2402.13254 Zhang; 2311.03964 Sahin; 2306.14610 Hsieh; 2410.16719 Han; 2412.04378 Ouali; 2412.05818 Qu; 2505.19223 Zhu (LLaDA 1.5); 2510.02880 Ma; 2507.04832 Han; 2512.22288 Zhou; 2602.14147 Li; 2608.03025 Zhang; 2610.36466 Li; 2603.17044 Rao; 2010.04592 Robinson; 1712.00527 Blanc; 1906.10169 Cadene; 1909.03683 Clark. Not API-verified: Nadas 1983 and Bahl et al. 1986 (IBM records), Ng and Jordan 2001, Bengio and Senécal 2003 (AISTATS record found), VL-Match ICCV 2023 (CVF page found, no arXiv id).
