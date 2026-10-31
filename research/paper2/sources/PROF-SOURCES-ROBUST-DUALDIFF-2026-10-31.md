---
agent: mdm-expert
date: 2026-10-31
brief: Read the two professor resources (Qiu et al. DMLR 2024; DualDiff project page) and judge them as a hostile TNNLS reviewer for the Paper 2 manuscript; no computation, no manuscript edit.
sources_examined:
  - research/sources/md/prof-2026-10-31/2212.08044v3.md (local markdown of arXiv:2212.08044v3; read in full for Abstract, Sec. 1, 3, 4.1-4.3, 5, App. A, B, C, H, I; Tables 3, 5, 8; the 56-page appendix result tables 9-38 were only skimmed by caption)
  - https://arxiv.org/abs/2212.08044 (WebFetch, abstract page, version history)
  - https://zijieli-jlee.github.io/dualdiff.github.io/ (WebFetch, project page)
  - https://arxiv.org/abs/2501.00289 and https://arxiv.org/html/2501.00289 (WebFetch summaries by a small model: E1) and https://arxiv.org/pdf/2501.00289v2 (downloaded to the session scratchpad, text extraction badly garbled; used only for grep checks of abstract, Sec. 3.2 "do not corrupt the conditioning samples", Table 3, absence of any robustness evaluation)
  - https://github.com/zijieli-Jlee/Dual-Diffusion (README summary via WebFetch: E1)
  - https://raw.githubusercontent.com/bethgelab/imagecorruptions/c959e659c9713837d2acd7ce785a81202d4be799/imagecorruptions/corruptions.py (the commit our exp_p2/gate/suite.py:PACKAGE pins; WebFetch extraction of the parameter lists)
  - Manuscript files, read-only: paper2-tnnls/sections/{related,introduction,study1,study2,discussion}.tex, paper2-tnnls/references.bib, exp_p2/gate/corruptions.py, research/paper2/tnnls/EXPLORATORY-PLAN-SEVERITY-2026-10-31.md
coverage: >
  Qiu et al.: text and Tables 3, 5, 8 read; per-model result tables 25-38 NOT read (all are averages over five severities, so they hold no per-level numbers; checked by caption grep).
  Table 3 in the markdown has a damaged layout: only the first columns after "Clean" (Gaussian) are reliably aligned; do not quote other columns without checking the PDF page 8.
  DualDiff: abstract, architecture, loss, sampling, benchmark list taken from the arXiv page, project page and HTML summary; no equation was re-derived; checkpoint size and VRAM not measured.
claims:
  - statement: "Qiu et al. is arXiv:2212.08044v3 (19 Jan 2024), published in the Journal of Data-centric Machine Learning Research (DMLR) 2024 (submitted 10/23, revised 01/24, published 01/24), OpenReview id Vc1fXQ8mJg."
    status: supported
    evidence: "markdown header lines 1-4, 26; arXiv abs page (v1 15 Dec 2022, v2 18 Jan 2024, v3 19 Jan 2024; comment 'Accepted by DMLR 2024')"
    level: E2
    confidence: 0.95
  - statement: "Qiu et al. use 17 image perturbations (4 noise, 4 blur, 4 weather, 4 digital, 1 stylize), each at 5 severities (85 methods), with the parameters of Hendrycks and Dietterich (2019)."
    status: supported
    evidence: "Sec. 3.1 (p. 4); App. A 'Magnitude of Perturbation'; Table 5 (p. 29); Table 8 (p. 31)"
    level: E2
    confidence: 0.95
  - statement: "Their Gaussian-noise standard deviations on normalised pixels are 0.08, 0.12, 0.18, 0.26, 0.38 for severities 1 to 5; JPEG quality is 25, 18, 15, 10, 7."
    status: supported
    evidence: "Table 8 (p. 31); identical to the imagecorruptions commit c959e65 (gaussian_noise c=[.08,.12,.18,.26,.38]; jpeg_compression c=[25,18,15,10,7]; c[severity-1])"
    level: E2 (paper) / E3 (package list via fetch)
    confidence: 0.9
  - statement: "Retrieval results (Table 3, App. C Tables 25-38) are scores AVERAGED over the five severities; no per-severity numbers are reported. MMI = (s_clean - s_perturbed)/s_clean, averaged."
    status: supported
    evidence: "Sec. 4.2 MMI definition (p. 7); App. B 'Task-Specific Experimental Settings' (p. 25); captions of Tables 25-38"
    level: E2
    confidence: 0.95
  - statement: "Qiu et al. contain no unified or masked discrete diffusion model, no verification or foil-detection task, no corruption-aware scoring rule, and keep image-text pairs matched (human check: 99.00 percent of perturbed pairs still judged a pair)."
    status: supported
    evidence: "Model list Sec. 4.1 (p. 6-7), App. B; App. A 'Human Verification', Table 10"
    level: E2
    confidence: 0.9
  - statement: "DualDiff (D-DiT) is a CVPR 2025 paper that combines discrete masked diffusion for text with continuous flow-matching diffusion for image latents in one dual-branch MM-DiT initialised from SD3-medium; it does not evaluate robustness, verification or likelihood-ratio scoring."
    status: supported
    evidence: "arXiv 2501.00289v2 abstract; project page 'Brief intro'; Sec. 3.1-3.3 per HTML summary; PDF grep finds no robustness evaluation"
    level: E1 (E2 for the abstract and for 'conditioning is not corrupted')
    confidence: 0.8
competing_explanations: []
unknowns:
  - "DMLR volume, issue and article number (not in the markdown or on arXiv); leave them out of the bib entry until a citation-validator run."
  - "CVPR 2025 pages and DOI come from a web-search result page (CVF listing, mlanthology), not from the PDF; verify before submission."
  - "Whether the D-DiT checkpoints (HF account JleeOfficial: dual_diff_sd3_512_base, _sft) fit 12 GB with the T5 encoder: not measured."
  - "Qiu Table 3 JPEG and other late columns: unreadable in the markdown."
next_test: {hypothesis: none proposed, intervention: none, primary_metric: none, falsifier: none, gpu_hours: 0}
---

# Professor resources, 2026-10-31: Qiu et al. (DMLR 2024) and DualDiff (CVPR 2025)

Labels: SF = source fact (with location), INF = my inference, OUR = our result with run id (none computed here).

## 1. Bibliographic data

### 1.1 Qiu et al.

SF (markdown lines 1-26; arXiv abs page): Jielin Qiu, Yi Zhu, Xingjian Shi, Florian Wenzel, Zhiqiang Tang, Ding Zhao, Bo Li, Mu Li. "Benchmarking Robustness of Multimodal Image-Text Models under Distribution Shift". Journal of Data-centric Machine Learning Research (2024); Editor Hongyang Zhang; submitted 10/23, revised 01/24, published 01/24; reviewed on OpenReview, forum id Vc1fXQ8mJg; arXiv:2212.08044 (cs.CV), v1 15 Dec 2022, v3 19 Jan 2024 (the file is v3; its margin stamp reads 19 Jan 2024); arXiv DOI 10.48550/arXiv.2212.08044. Project page named in the abstract: https://MMRobustness.github.io (not opened).

```bibtex
@article{qiu2024benchmarking,
  author  = {Qiu, Jielin and Zhu, Yi and Shi, Xingjian and Wenzel, Florian and Tang, Zhiqiang and Zhao, Ding and Li, Bo and Li, Mu},
  title   = {Benchmarking Robustness of Multimodal Image-Text Models under Distribution Shift},
  journal = {Journal of Data-centric Machine Learning Research},
  year    = {2024},
  eprint  = {2212.08044},
  archivePrefix = {arXiv},
  url     = {https://openreview.net/forum?id=Vc1fXQ8mJg}
}
```
(volume and pages omitted on purpose: not in any source I opened.)

### 1.2 DualDiff

SF (project page; arXiv abs page): the page title is "Dual Diffusion for Unified Image Generation and Understanding"; authors Zijie Li, Henry Li, Yichun Shi, Amir Barati Farimani, Yuval Kluger, Linjie Yang, Peng Wang (CMU, Yale, ByteDance Seed); the page links paper https://arxiv.org/abs/2501.00289 and code https://github.com/zijieli-Jlee/Dual-Diffusion. arXiv v1 31 Dec 2024, v2 1 Apr 2025. Venue (web search, CVF Open Access listing and mlanthology, E1): CVPR 2025, pp. 2779-2790, DOI 10.1109/CVPR52734.2025.00265. The arXiv page itself shows no venue. A search hit listing "CVPR 2024" is wrong.

```bibtex
@inproceedings{li2025dualdiffusion,
  author    = {Li, Zijie and Li, Henry and Shi, Yichun and Farimani, Amir Barati and Kluger, Yuval and Yang, Linjie and Wang, Peng},
  title     = {Dual Diffusion for Unified Image Generation and Understanding},
  booktitle = {Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)},
  year      = {2025},
  pages     = {2779--2790},
  doi       = {10.1109/CVPR52734.2025.00265},
  eprint    = {2501.00289},
  archivePrefix = {arXiv}
}
```
(pages and DOI: E1, from a search result; run citation-validator before they go into the submission.)

## 2. What each source does, and where

### 2.1 Qiu et al. (claim locations; page numbers from the PDF footers visible in the markdown)

| Claim | Location |
|---|---|
| Benchmarks 12 open image-text models (CLIP, ViLT, ALBEF, BLIP, TCL, METER, GRIT, LLaVa, Mini-GPT4, BLIP2, GLIDE, Stable Diffusion) on 5 tasks: retrieval (Flickr30K, COCO), visual reasoning (NLVR2), visual entailment (SNLI-VE), captioning (COCO), text-to-image (COCO) | Abstract; Sec. 4.1 (p. 6-7); Table 2 |
| 17 image perturbations from ImageNet-C and Stylize-ImageNet in 5 categories (noise: Gaussian, shot, impulse, speckle; blur: defocus, frosted glass, motion, zoom; weather: snow, frost, fog, brightness; digital: contrast, elastic, pixelate, JPEG; stylize); 5 severities each = 85 | Sec. 3.1 (p. 4); Table 5 (p. 29) |
| 16 text perturbations (character, word, sentence level); 60 variants | Sec. 3.2 (p. 5); Table 6 |
| Magnitudes = Hendrycks and Dietterich parameters; quality drop checked with SSIM and LPIPS "within the same level across severities" | App. A (Magnitude; Image Quality Drop); Table 8 (p. 31); Table 9 |
| Gaussian sigma 0.08, 0.12, 0.18, 0.26, 0.38; JPEG quality 25, 18, 15, 10, 7; impulse 0.03-0.27; speckle and others | Table 8 (p. 31) |
| MMI = (s_c - s_p)/s_c, relative drop vs clean, "averaged"; MOR (missing object rate) for text-to-image | Sec. 4.2 (p. 7); Fig. 7, Tables 4 and 20 |
| Retrieval reported as RSUM "averaged on five perturbation levels"; no per-level result | Sec. 4.3 and Table 3 (p. 8); App. B (p. 25); captions of Tables 25-38 |
| Findings: image perturbations hurt more than text; zoom blur most severe; glass blur and brightness least harmful; character-level text edits most severe; BLIP lowest MMI | Sec. 4.3, Sec. 5 (p. 12-13), App. I |
| Example from Table 3 (Gaussian column, averaged over 5 severities, RSUM): Flickr30K ViLT FT 522.0 to 413.0, CLIP ZS 533.7 to 501.7, BLIP FT 580.9 to 536.2; COCO ViLT FT 441.5 to 372.2, CLIP ZS 394.5 to 363.0, BLIP FT 516.6 to 471.9 (markdown layout damaged; verify on PDF p. 8 before quoting) | Table 3 [Top] |
| Perturbed pairs remain matched: 10 volunteers, 5,000 pairs each, 99.00 percent "still a pair" | App. A (Human Verification); Table 10 |
| Learning-based shifts (adversarial FGSM, BERT-Attack, Co-Attack, ...) on retrieval only, in the appendix | App. H; Tables 21-24 |
| Limitation: only synthetic perturbations; real-world shifts and mitigation (augmentation) are future work | Sec. 5 "Limitations and future work" (p. 13) |
| Inconsistency to avoid: Table 8 lists the salt-and-pepper amounts 0.03-0.27 in the shot-noise row (they are the impulse values). The pinned imagecorruptions code has shot_noise c=[60,25,12,5,3] (Poisson), impulse [.03,.06,.09,.17,.27], speckle [.15,.2,.35,.45,.6]. Cite the package, not Table 8, for shot noise. | Table 8 vs commit c959e65 |

INF: the paper is a benchmark of the discriminative and generative image-text stack of 2020-2023. It has no per-token evidence, no foil negatives, no corruption-aware decision rule, and (by design) pairs that remain matched.

### 2.2 DualDiff (D-DiT)

| Claim | Location |
|---|---|
| End-to-end diffusion model for both generation and understanding; draws on MM-DiT and discrete diffusion language modelling; trains conditional likelihoods of images and text under one loss through both branches | arXiv abstract; project page "Brief intro" |
| Image side: continuous latents (SD3 image VAE kept frozen) with flow matching, velocity prediction. Text side: absorbing-state masked diffusion, T5 encoder/tokenizer, <extra_id0> as mask, log-linear schedule, negative-ELBO cross-entropy. Loss = flow-matching loss + weighted text loss (weight 0.2 pretraining, 1.0 tuning). "We do not corrupt the conditioning samples during training." | Sec. 2.1-2.2, 3.1-3.2 (Eqs. 7-9); Sec. 4.1; text grep of the PDF (conditioning sentence) |
| Initialised from SD3-medium (2B, per the model table); about 40M pairs; Table 3 reports VQAv2 60.1, MME 1124.7, POPE 84.0, COCO CIDEr 56.2; GenEval 0.65 | Sec. 4.1-4.3, Tables 2-3 (E1, HTML summary) |
| VQA is done by in-filling the answer tokens with the image and question fixed | Sec. 3.3 |
| No robustness, corruption, verification, reranking or likelihood-ratio evaluation; limitation list (fixed output length, small-object detail, long prompts) | Sec. 4, Sec. 7 (E1 for the full paper; PDF grep found no robustness evaluation) |
| Checkpoints released (HF, 512 base and 512 SFT), MIT code licence; VRAM and parameter counts not stated | GitHub README (E1) |

## 3. Hostile-reviewer verdicts

### 3.1 Qiu et al.: what it implies for our paper

Finding 1 (citation gap, real). Our Related Work cites only ImageNet-C and the imagecorruptions package for corruptions (related.tex lines 79-82) and a TNNLS fusion paper in the Introduction (introduction.tex lines 36-37). Qiu et al. is the established benchmark of image corruptions for COCO-trained image-text models. A reviewer who knows it will ask why a paper on image-caption verification under image corruption does not cite it. This is a small, cheap fix; the professor sent it, so citing it also follows the "cite provided papers" rule.

Finding 2 (novelty is not threatened). Qiu et al. keep the pair matched (99.00 percent human-verified), test no unified masked diffusion model, report no verification decision, and offer no defence. Our contribution (per-token reliability weighting of the likelihood-ratio sum, and the null gate) is outside their scope. The sentence in related.tex "none of them reports a verification decision under image corruption in a unified masked diffusion model" stays true.

Finding 3 (their severity practice is not ours; do not claim a match). They use five fixed levels per corruption and publish only the average over the five levels. We use named levels (JPEG 10, sigma 0.1, splice 128 px) and an exploratory per-level sweep. A claim that the sweep "matches the five-level practice" would be false: our sweep has 3 new sigmas, not on their grid. What is true is that our per-level reporting is finer than theirs (they give no per-level number), and that our sigma is on the same scale (pixels in [0,1]) as their Gaussian levels.

Finding 4 (MMI should not be adopted as an endpoint). MMI is a relative drop from the clean score. Our primary quantity is the paired difference LRF minus NONE and verification accuracy, with a chance floor of 0.5 for a binary decision; a relative drop from clean does not account for chance and would hide the paired structure. If a reviewer asks, MMI of the unweighted sum can be derived from numbers already in the runs at zero GPU cost; it is not warranted otherwise.

Finding 5 (an honest weakness it exposes). Their headline is that zoom blur is the most severe image perturbation for retrieval, with glass blur and brightness the mildest, and that noise reduces recall noticeably (Table 3 Gaussian column above). Our three realistic corruptions (JPEG, Gaussian noise, splice) were not chosen by a severity ranking and splice has no counterpart in their taxonomy. A reviewer can say that the evaluated set omits blur, the family they found hardest. Our exploratory suite (Study 1 supplement S-II) already contains defocus blur at severities 2 and 4 for the gate, but not for LRF. State it as a limit; no new run is needed for that.

### 3.2 Mapping: our corruptions vs their taxonomy and severity grid

Our Gaussian noise is applied to [0,1] pixels and clipped (exp_p2/gate/corruptions.py lines 25-29), the same scale as Hendrycks and Dietterich and Qiu Table 8 ("first normalize the pixel values"). The nearest level is by absolute distance in sigma; "between" means the value is not on the grid.

| Our corruption (run) | Their category / perturbation | Their severity levels (Table 8) | Our value vs their grid |
|---|---|---|---|
| Gaussian noise sigma 0.1 (confirmatory, Study 2) | Noise / Gaussian | 0.08, 0.12, 0.18, 0.26, 0.38 | Between level 1 (0.08) and level 2 (0.12), 0.02 from each; not on the grid |
| Gaussian sigma 0.05 (sweep) | Noise / Gaussian | same | Below level 1 (0.03 under 0.08); outside their range |
| Gaussian sigma 0.2 (sweep) | Noise / Gaussian | same | Between level 3 (0.18) and level 4 (0.26); nearest level 3 (0.02) |
| Gaussian sigma 0.3 (sweep) | Noise / Gaussian | same | Between level 4 (0.26) and level 5 (0.38); nearest level 4 (0.04) |
| (no run) | | | 0.38, their level 5, is above our largest sigma |
| JPEG quality 10 (Study 1 and 2) | Digital / JPEG compression | quality 25, 18, 15, 10, 7 | Exactly level 4 |
| JPEG quality 5 (Study 1 ladder rung 2, per corruptions.py header) | Digital / JPEG | same | Harsher than their level 5 (7) |
| shot_noise3, impulse_noise3, speckle_noise3 (family LG, imagecorruptions severity 3) | Noise / Shot, Impulse, Speckle | shot 60,25,12,5,3 (package; Qiu Table 8 text is wrong for this row); impulse 0.03-0.27; speckle .15-.6 | Exactly level 3 (the middle level) by construction: same package parameters |
| pixelate, defocus_blur, fog, impulse_noise at severities 2 and 4 (Study 1 gate suite, supplement S-II) | Digital / pixelate; Blur / defocus; Weather / fog; Noise / impulse | levels 2 and 4 of 5 | Exact levels 2 and 4 |
| Splice 128 px (Study 1 and 2) | none | none | No counterpart in the 17; it is a local content edit, not a statistical degradation |
| Sanity corruptions patch and swap (token level) | none | none | Token-level, not a pixel perturbation |

The mapping rests on the package parameter lists (E3 for those lists via a fetch of the pinned commit) and on Qiu Table 8 (E2). I did not check that our encoder resize order matches theirs (we corrupt at 512x512 after preprocessing; their resize order is not stated in what I read), so the equivalence is of the parameter, not necessarily of the final pixel statistics.

### 3.3 DualDiff

Relevance: low to moderate; it is a unified diffusion model (one transformer, two coupled branches), so it belongs in the neighbouring-models sentence of the related-work paragraph on unified models. It is not a masked discrete diffusion model for images: the image side is continuous flow matching on SD3 VAE latents. Our method needs, for the image direction, per-token categorical likelihoods of discrete image tokens (UniDisc, VQ codes); D-DiT has no such quantity. INF: the LRF image-direction evidence sum cannot be defined on it. A text-direction analogue (masked caption tokens given the image) is definable from its NELBO, but it is a different evidence sum with a different reliability question; building it would be new method work, not a second backbone for LRF.

Novelty threat: none found. It reports no corruption, verification, reranking or likelihood-ratio scoring (arXiv HTML summary and PDF grep), and it explicitly does not corrupt conditioning inputs in training (Sec. 3.2), which is the opposite regime from ours. The statement in related.tex line 38-39 ("None of them reports a verification decision under image corruption in a unified masked diffusion model") is unaffected.

Use as a second backbone: not recommended. The open "second backbone" limitation (discussion.tex line 40) needs a model with discrete image tokens and a per-token masked likelihood (the other models already named in related.tex: Muddit, Lumina-DiMOO, MMaDA-type, LaViDa). Even apart from that mismatch, D-DiT carries SD3-medium (2B per its table) plus a T5-XXL text encoder (T5-XXL listed in its Table 3); from general knowledge, not verified here, the T5-XXL encoder alone is around 9 to 10 GB in bf16, which makes a 12 GB run fragile.

Cite or not: optional. A one-clause citation is defensible in the unified-model sentence ("dual-branch models pair masked text diffusion with continuous image flow [D-DiT]"). If the 15-page cap bites, drop it; its absence cannot be attacked as a novelty gap. I would not add it to the Discussion limitation.

## 4. Proposed text changes (at most two; each at most 30 words)

1. Target: paper2-tnnls/sections/related.tex, paragraph "Corruption benchmarks and preregistration", after the hendrycks2019benchmarking sentence (new bib key qiu2024benchmarking, section 1.1).
   "Qiu et al. apply 17 common corruptions at five severities to COCO and other image-text data, report retrieval recall averaged over severities, and test no unified masked diffusion model~\cite{qiu2024benchmarking}." (29 words)

2. Target: paper2-tnnls/sections/study2.tex, next to the family LG definition (lines 168-169), or the corruption paragraph of the setting section if one exists; also suitable for the sweep table caption in the supplement.
   "Gaussian sigma is on [0,1] pixels, as in ImageNet-C (levels 0.08 to 0.38); JPEG quality 10 is its level 4, and family LG uses level 3." (27 words)
   This states the alignment that is true and makes no claim that the sweep follows the five-level practice. If the page cap forbids a sentence, drop change 2 first (the sweep caption can carry the "0.05 below level 1; 0.2 and 0.3 between levels 3 and 5" note in the supplement).

## 5. Is a new experiment warranted?

No. Evidence: both resources change what we cite and how we describe the corruption levels, not what we claim. Specifically:
- Re-running the severity sweep on the Qiu grid (0.08, 0.12, 0.18, 0.26, 0.38) would add two or more levels; the plan's estimate for three levels is about 1 to 1.5 h wall at duty 0.5 (EXPLORATORY-PLAN, Compute and guards), so five levels would be roughly 2 to 2.5 h, over the 2 h budget, and the current sweep is still running; the project memory also records GPU crashes on long runs. It would not change any confirmatory result (noise 0.1, 0.733 to 0.802).
- Adding a blur family for LRF (their hardest family) would need a new pre-written plan and a pass through the audit and the n-rule; out of scope for 2 h and it would be exploratory, outside the 15-page budget.
- DualDiff as a second backbone: not feasible as argued above (no discrete image-token likelihood; weights plus T5-XXL near the 12 GB limit).
- MMI table: derivable from stored per-item arrays at no GPU cost if a reviewer asks; not recommended for the paper.

## 6. Concerns for the orchestrator
1. DMLR volume, issue and pages, and the CVPR pages and DOI, are unverified; send both bib entries to citation-validator before submission.
2. Qiu Table 3 is garbled in the markdown; only the Gaussian column numbers above are usable, and only after a check on PDF p. 8.
3. Qiu Table 8 has a shot-noise row error; cite the package for shot noise, and do not cite Table 8 for shot-noise values.
4. The DualDiff method and results come from a small-model summary of the arXiv HTML plus a garbled PDF grep (E1, E2 for abstract only); a paper-reader pass is needed if the paper is to be cited for anything beyond "one dual-branch unified diffusion model with continuous images".
5. No ledger row was added (the brief names no ledger); no manuscript file, run or ledger was changed.
