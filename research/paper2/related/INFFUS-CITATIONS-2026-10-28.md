```yaml
agent: lit-scout
date: 2026-10-28
brief: Find 10-15 verified Information Fusion (Elsevier, ISSN 1566-2535) papers, preferably 2022-2026, that GATE (Paper 2) can honestly engage with; count IF papers already in the bibliography; record the IF guide-for-authors rules for references.
sources_examined:
  - "Crossref REST API: 14 DOIs fetched individually (api.crossref.org/works/<DOI>), plus 31 title/topic queries filtered to ISSN 1566-2535 from 2022-01-01 (queries listed under coverage)"
  - "OpenAlex: abstract_inverted_index for 6 DOIs; cites-filter for Conformal Risk Control (W4290055968) restricted to the IF source; source id S7560371"
  - "Exa web_search/web_fetch of ScienceDirect article pages, doi.org landing pages, ACM DL mirrors, an arXiv/HAL preprint (for abstracts)"
  - "Official guide for authors, fetched through Exa web_fetch: https://www.sciencedirect.com/journal/information-fusion/publish/guide-for-authors (direct curl and WebFetch were refused with HTTP 403)"
  - "C:/Users/Shlok/Downloads/Multi-Modality Language model/1-s2.0-S1566253526004987-main.pdf (converted with markitdown.exe; first page only read)"
  - "paper2/references.bib, paper2/sections/{introduction,related,discussion}.tex (read for placement only; not edited)"
coverage: |
  Read: abstracts (publisher abstract, or the abstract of a preprint copy) for all 14 entries; for zhou2027burden also the highlights,
  introduction, contribution list and first conclusion paragraph of the ScienceDirect preview. No entry was read in full text, so no entry is E2.
  Crossref queries run (all filtered to IF, 2022 onward): reliability-aware fusion/corrupted modality; conformal prediction multimodal fusion;
  robust multimodal learning missing modality; trusted/evidential fusion; noisy modality quality-aware fusion; image-text matching noisy
  correspondence; diffusion model multimodal fusion; "conformal prediction"; trustworthy multimodal survey; VLM hallucination; unified
  multimodal understanding and generation survey; modality corruption benchmark; masked diffusion language model; distribution-free coverage /
  risk control; corrupted sensor reliability; image-text consistency / out-of-context misinformation; VLM robustness image corruption;
  uncertainty quantification review; OOD detection multimodal; cross-modal inconsistency; low-quality data; selective prediction; token-level
  uncertainty / pseudo-log-likelihood; discrete diffusion image-text tokens; adversarial robustness of image-text models; MLLM hallucination
  detection; MLLM robustness to degraded input; VLM calibration; token-level confidence filtering; inference-time remasking; "discrete diffusion".
  OpenAlex full-text search "conformal prediction / conformal risk control / coverage guarantee" inside IF, 2022 onward.
  NOT searched: Scopus, Web of Science, Google Scholar, the ScienceDirect search box and its "cited by" lists (Cloudflare blocks them), IF special
  issues pages, IF papers before 2022 except Khaleghi 2013 (already cited), forward citations of any IF paper other than the one OpenAlex check
  below, and papers whose titles do not contain the query words (Crossref ranks by title/abstract text similarity only).
  Completeness of this search is not evidence that no closer IF paper exists.
claims:
  - statement: "paper2/references.bib has 49 entries and exactly one is an Information Fusion paper (khaleghi2013multisensor, doi 10.1016/j.inffus.2011.08.001)."
    status: supported
    evidence: "grep of journal fields in paper2/references.bib; the same count in research/paper2/related/references-draft.bib (the two files have identical key sets)"
    level: E3
    confidence: 0.95
  - statement: "The 14 entries in inffus-candidates.bib exist as Information Fusion articles with the titles, authors, volumes, article numbers and DOIs given."
    status: supported
    evidence: "Crossref works/<DOI> returned container-title ['Information Fusion'], ISSN 1566-2535, type journal-article for each; the .bib compiles with elsarticle-num.bst to 14 bibitems with no warnings (scratchpad test)"
    level: E1
    confidence: 0.97
  - statement: "Zhou and Lu 2027 (doi 10.1016/j.inffus.2026.104860) is the closest Information Fusion paper found to GATE's use of a calibrated threshold to decide whether to trust a source in a vision-language decision."
    status: supported
    evidence: "ScienceDirect preview abstract and introduction via Exa (pii S1566253526007360); no other IF hit combined vision-language, a risk-calibrated threshold and keep-or-override logic"
    level: E1
    confidence: 0.7
  - statement: "No Information Fusion paper on masked discrete diffusion language models or unified multimodal discrete diffusion models turned up."
    status: unknown
    evidence: "Crossref queries 'masked diffusion language model', 'discrete diffusion', 'unified multimodal understanding and generation survey' returned only unrelated diffusion papers (molecules, time series, image fusion); search coverage is limited as listed above"
    level: E1
    confidence: 0.5
competing_explanations: []
unknowns:
  - "Full text of every entry; in particular whether zhou2027burden or wang2025multistage do anything at token level or with corrupted modalities."
  - "Abstracts of Cuzzolin 2025 'Uncertainty measures: a critical survey' (10.1016/j.inffus.2024.102609), Gong 2024 (10.1016/j.inffus.2024.102544), Liu 2024 MinJoT (10.1016/j.inffus.2023.102071): not obtained, so they are not in the bib."
  - "Content of the corrigendum 10.1016/j.inffus.2025.103287 to wang2025multistage."
  - "Whether the 50-reference cap counts the references list only; the guide says 'Maximum 50 references' under Research article."
next_test: {hypothesis: "zhou2027burden does not threaten GATE's contribution (different unit of decision, different calibration target, no generative likelihood)", intervention: "paper-reader E2 read of the full text, appendix and code", primary_metric: "list of overlaps in method, calibration guarantee and evaluation", falsifier: "the paper gates input tokens or applies conformal risk control to a masked-likelihood score", gpu_hours: 0}
```

# Information Fusion citation candidates for Paper 2 (GATE)

All bibliographic fields below were read from Crossref (container-title "Information Fusion", ISSN 1566-2535) on 2026-10-28. Evidence levels follow the
contract: E1 = abstract or publisher preview, not the paper. "Supports" statements below are limited to what the abstract (or preview) says; the lines
marked *inference* are my reading of how it relates to GATE, not source facts. Year is the volume cover-date year, which is how Information Fusion prints
its own references (the local PDF header reads "Information Fusion 137 (2027) 104621").

## 1. What the bibliography already contains

| Item | Count |
|---|---|
| Entries in `paper2/references.bib` | 49 (limit 50, so one free slot) |
| of which Information Fusion papers | **1**: `khaleghi2013multisensor` (Information Fusion 14(1):28-44, 2013, doi 10.1016/j.inffus.2011.08.001) |
| Information Fusion papers from 2022 or later | **0** |

The local PDF `1-s2.0-S1566253526004987-main.pdf` is Teng et al., "Multimodal information fusion for food nutrition estimation: A survey", Information Fusion 137 (2027) 104621
(Crossref confirms; abstract page read). It is a survey on a different topic. It is useful only as a format specimen (numbered references, as the guide requires). I do not recommend citing it.

## 2. Verified candidates (14), ordered by usefulness

Priority: A = cite if any IF paper is cited; B = cite if space allows; C = background, cut first.
Competitor column: **NEAR** = closer to GATE than we assumed (read the full paper before submission); related = same problem family, different method; background = no overlap in method.

| # | Citekey | Full reference | DOI | Verified by | Level | Supports (sentence or section of our paper) | Competitor? | Pri |
|---|---|---|---|---|---|---|---|---|
| 1 | zhou2027burden | G. Zhou, Y. Lu, Burden of proof: Calibrated evidential arbitration for asymmetric decision-level fusion in vision-language recognition, Inf. Fusion 139 (2027) 104860 (online 2026-10-13) | 10.1016/j.inffus.2026.104860 | Crossref; ScienceDirect preview (pii S1566253526007360) via Exa | E1+ (abstract, highlights, introduction, contributions, first conclusion paragraph) | Related work "Source validation before fusion" and Discussion subsection "Where the work sits in information fusion": a recent IF paper that frames a vision-language fusion decision as keep-or-override with a calibrated risk threshold. Source facts: a default prediction is replaced by a challenger only when a combined Dempster-Shafer score reaches a threshold chosen with a Clopper-Pearson upper bound on the proportion of harmful overwrites; evidence channels are frozen CLIP and DINOv3; four few-shot benchmarks; blind adoption of the challenger overwrites a correct default in 18-46% of conflicts; trains no network | **NEAR (moderate)** | A |
| 2 | huang2025evidential | L. Huang, S. Ruan, P. Decazes, T. Denoeux, Deep evidential fusion with uncertainty quantification and reliability learning for multimodal medical image segmentation, Inf. Fusion 113 (2025) 102648 | 10.1016/j.inffus.2024.102648 | Crossref; ScienceDirect abstract page and HAL preprint via Exa | E1 | Related work "Source validation before fusion" (next to Chair-Varshney and Kittler): per-source reliability coefficients applied by contextual discounting before Dempster's rule, i.e. soft down-weighting of an unreliable source. GATE withholds a flagged token instead of discounting it | related | A |
| 3 | shao2024ddef | Z. Shao, W. Dou, Y. Pan, Dual-level Deep Evidential Fusion: Integrating multimodal information for enhanced reliable decision-making in deep learning, Inf. Fusion 103 (2024) 102113 | 10.1016/j.inffus.2023.102113 | Crossref; OpenAlex abstract | E1 | Introduction "Why this is a fusion problem": abstract states that multimodal approaches often overlook the varying importance of modalities and neglect uncertainty estimation, which limits generalisation and gives unreliable predictions; Dirichlet/BBA plus Dempster-Shafer fusion across modalities | related | A |
| 4 | wang2025multistage | B. Wang, W. Li, A. Bradlow, A. Watt, A.T.Y. Chan, E. Bazuaye, Multi-stage multimodal fusion network with language models and uncertainty evaluation for early risk stratification in rheumatic and musculoskeletal diseases, Inf. Fusion 120 (2025) 103068 | 10.1016/j.inffus.2025.103068 | Crossref; OpenAlex abstract | E1 | Related work / Method (conformal guarantee): an IF paper that attaches conformal prediction to a multimodal fusion network to flag unreliable predictions for human review. Prediction-level, clinical text and tabular data, not a token gate, no corrupted-modality test. **Caution:** a corrigendum exists (Inf. Fusion 122 (2025) 103287, doi 10.1016/j.inffus.2025.103287, content not read) | related | A |
| 5 | zhang2026lowquality | Q. Zhang, Y. Wei, Z. Han, H. Fu, X. Peng, Q. Hu, C. Deng, C. Xu, J. Wen, D. Hu, C. Zhang, Multimodal fusion on low-quality data: A comprehensive survey, Inf. Fusion 135 (2026) 104437 | 10.1016/j.inffus.2026.104437 | Crossref; abstract and introduction of the preprint text served at the DOI via Exa | E1 | Introduction (first paragraph of "Why this is a fusion problem"): the survey names four low-quality settings (noisy, incomplete, imbalanced, quality-varying) and says the reliability of fusion under low-quality data is largely unexplored. *Inference:* GATE falls under "noisy" and "quality-varying" data; use its taxonomy to place the corruption families (JPEG, noise, splice, patch, swap) | background (framing) | A |
| 6 | wu2025omnifuse | Y. Wu, J. Chen, L. Hu, H. Xu, H. Liang, J. Wu, OmniFuse: A general modality fusion framework for multi-modality learning on low-quality medical data, Inf. Fusion 117 (2025) 102890 | 10.1016/j.inffus.2024.102890 | Crossref; abstract via Exa (doi.org page and ACM DL mirror) | E1 | Related work on robustness to corrupted or absent modalities: three named failures (absent informative modality, imbalance, information entangled with noise) and a learned mechanism that identifies and removes noise-carrying modality combinations. Learned, medical (EHR, chest X-ray, PET/CT); not calibrated and not token-level | related | B |
| 7 | zhou2024uncertaintyaware | Q. Zhou, T. Chen, H. Zou, X. Xiao, Uncertainty-aware incomplete multimodal fusion for few-shot Central Retinal Artery Occlusion classification, Inf. Fusion 104 (2024) 102200 | 10.1016/j.inffus.2023.102200 | Crossref; ScienceDirect abstract page and ACM DL via Exa | E1 | Related work: predictive uncertainty (Monte Carlo dropout) is used to weight modality-specific features adaptively when modalities are missing ("trustworthy fusion"). Contrast: GATE's reliability score is a masked likelihood and the cut-off is calibrated | background | B |
| 8 | dong2026itmreview | C. Dong, C. Wei, A review for image-text matching from deep learning perspective, Inf. Fusion 126 (2026) 103453 | 10.1016/j.inffus.2025.103453 | Crossref; abstract via ACM DL mirror (Exa) | E1 | Related work on image-text matching: three method families (feature enhancement, cross-modal alignment, vision-language pretraining). Our two-way verification task (does the caption describe the image) is adjacent to retrieval-style matching, so cite for the task background only | background | B |
| 9 | han2026mfvlm | X. Han, S. Chen, Z. Fu, Z. Feng, L. Fan, D. An, C. Wang, L. Guo, W. Meng, X. Zhang, R. Xu, S. Xu (12 authors, full list in .bib), Multimodal fusion and vision-language models: A survey for robot vision, Inf. Fusion 126 (2026) 103652 | 10.1016/j.inffus.2025.103652 | Crossref; abstract via Exa | E1 | Introduction / Discussion subsection "Where the work sits in information fusion": IF itself treats vision-language models as part of multimodal fusion (the survey compares VLMs with traditional fusion methods and lists cross-modal alignment among open challenges and adversarial robustness among future directions). Helps answer the scope-fit question. It is also cited by zhou2027burden (seen in that paper's reference list) | background | B |
| 10 | huang2024glf | S. Huang, W. Fu, Z. Zhang, S. Liu, Global-local fusion based on adversarial sample generation for image-text matching, Inf. Fusion 103 (2024) 102084 | 10.1016/j.inffus.2023.102084 | Crossref; ACM DL abstract via Exa | E1 | Evaluation / FOIL-COCO paragraph: image-text matching in IF is already framed around robustness to attacks, with adversarial (hard) samples used in training. FOIL-COCO hard negatives play a similar role here but only at evaluation time | background | C |
| 11 | zhang2024cascade | B. Zhang, Y. Shi, Y. Han, Q. Hu, W. Ding, Cascade & allocate: A cross-structure adversarial attack against models fusing vision and language, Inf. Fusion 104 (2024) 102179 | 10.1016/j.inffus.2023.102179 | Crossref; abstract via Exa and the authors' GitHub README | E1 | Introduction: abstract states that data fusion systems across modalities raise adversarial-robustness concerns (image-captioning models, MS COCO and Flickr30k). Our corruptions are not adversarial, so this supports only the general point that image-side damage reaches vision-language models | background | C |
| 12 | zhang2026trustt2i | Y. Zhang, Z. Chen, C.-H. Cheng, W. Ruan, X. Huang, D. Zhao, D. Flynn, S. Khastgir, X. Zhao, Trustworthy text-to-image diffusion models: A timely and focused survey, Inf. Fusion 133 (2026) 104264 | 10.1016/j.inffus.2026.104264 | Crossref; abstract via Exa | E1 | Introduction or Discussion: trustworthiness (robustness, fairness, security, privacy, explainability) of diffusion generators is an active IF topic, 96 papers surveyed. Continuous text-to-image diffusion, not discrete masked diffusion | background | C |
| 13 | fang2026alignment | Y. Fang, X. Pang, Q. Yu, F. Min, X. Cao, P. Tao, T. Li, Alignment in large vision language models: A survey, Inf. Fusion 133 (2026) 104294 | 10.1016/j.inffus.2026.104294 | Crossref; abstract via Exa | E1 | Background on how modalities are aligned in vision-language models; the survey lists "fusion-stage architectural alignment" and "inference-time dynamic alignment" among five pillars. Weak link to GATE | background | C |
| 14 | gao2027codif | P. Gao, J. Cheng, C. Fei, S. Ren, Y. Fan, P. Zhang, CoDIF: Conditional diffusion fusion with soft alignment for robust multimodal 3D object detection, Inf. Fusion 139 (2027) 104821 (online 2026-09-29) | 10.1016/j.inffus.2026.104821 | Crossref; **third-party summary** of the paper (ebiotrade.com, Chinese) via Exa, because the English abstract was not retrievable | E1 (partial, secondary) | Related work / evaluation: IF paper that uses a diffusion model inside multimodal fusion and tests robustness on a corruption benchmark (nuScenes-C, 27 corruption types at 5 severities per the summary). Precedent for ImageNet-C-style evaluation in fusion. LiDAR-camera, continuous diffusion; re-check the English abstract before citing | background | C |

## 3. Near competitors and concurrent work

**zhou2027burden (flag).** It was published 2026-10-13, 15 days ago, so it is inside the 90-day concurrent-work window and has no citations yet. Overlaps with GATE as stated in its abstract:
a vision-language setting; frozen pretrained models, no training; a threshold chosen on held-out data so that a bad-outcome proportion stays below a target; the default is kept unless the evidence clears the threshold.
Differences, all *inference from the abstract and introduction, not from the full text*:
(a) the unit decided is a whole recogniser prediction in few-shot recognition, not an input token of one modality;
(b) the evidence comes from CLIP and DINOv3 similarity margins turned into Dempster-Shafer masses, not from a masked likelihood under a generative model;
(c) calibration uses labelled conflicts and a Clopper-Pearson bound on the selected-hurt proportion, whereas GATE calibrates on clean pairs with conformal risk control on the false-alarm proportion;
(d) no corrupted-modality scenario is mentioned.
Consequence for the draft: any sentence that implies nobody has used a risk-calibrated gate in vision-language fusion needs rewording (the draft already carries a no-"first" rule). Recommend a paper-reader E2 pass on the full text and a novelty-auditor check before the discussion paragraph is written.
It also sits close to what a reviewer who knows IF will think of first, so citing it openly is the safer course.

**wang2025multistage (watch).** Conformal prediction inside an IF fusion network, so a reviewer cannot say conformal methods are foreign to the journal. Prediction-level and clinical. Corrigendum exists.

**Within the last 90 days (since 2026-07-30), IF papers found:** zhou2027burden (2026-10-13), gao2027codif (2026-09-29). Nothing else among the 14.

**No IF paper found** on masked discrete diffusion language models, unified multimodal discrete diffusion (UniDisc-type), conformal risk control for token-level gating, or masked-likelihood scoring of input tokens. Per the coverage statement this does not show absence. Practical reading: Information Fusion reviewers will meet the diffusion side as an imported tool, so the scope-fit argument should rest on source validation and decision fusion (the draft's Introduction paragraph "Why this is a fusion problem" and the Discussion subsection on fit already do this), with the IF papers above supplying the journal-internal context.

## 4. Considered and not included

| Paper | Why not |
|---|---|
| Cuzzolin, Uncertainty measures: A critical survey, Inf. Fusion 114 (2025) 102609, 10.1016/j.inffus.2024.102609 | Bibliographic fields verified, abstract not obtained, so no supports-statement can be written. Reserve candidate for an uncertainty-theory sentence |
| Gong et al., robust text-image person retrieval, 10.1016/j.inffus.2024.102544; Liu et al., MinJoT noise learning, 10.1016/j.inffus.2023.102071 | Abstract not obtained |
| Cheng et al., MAAB-ER robust emotion recognition, 10.1016/j.inffus.2026.104368 | Abstract read; modality imbalance in emotion recognition, too far from GATE |
| Zhang et al., OnPoKD, 10.1016/j.inffus.2026.104812 | Abstract read; a distillation method, "low-quality" only in the title |
| Sanchez et al., reliability-weighted diffusion, 10.1016/j.inffus.2026.104490 | Abstract read; survival clustering, unrelated despite the title words |
| Yumlembam et al., botnet detection with conformal prediction, 10.1016/j.inffus.2024.102529 | Conformal in IF but not multimodal; not read beyond the OpenAlex hit |

## 5. Guide for authors (Information Fusion)

Source: https://www.sciencedirect.com/journal/information-fusion/publish/guide-for-authors (text retrieved 2026-10-28 through Exa; direct fetches returned 403).

- **Research article:** original research; manuscripts 10-35 pages including figures, tables, references, appendices and biosketches; **maximum 50 references**. Survey article: up to 50 pages, maximum 300 references. (Article types section.)
- **Citation style:** numbers in square brackets in the text, always given even when author names are used (e.g. "Barnaby and Jones [8] obtained ..."); references numbered in order of first appearance; journal names abbreviated per the LTWA; give DOIs where available.
  Journal-article format, with article number: `[2] J. van der Geer, T. Handgraaf, R.A. Lupton, 2022. The art of writing a scientific article. Heliyon. 19, e00205. https://doi.org/...`
- Every reference must correspond to a real, existing source; references in the abstract must be given in full; unpublished results are discouraged in the list.
- **Preprints:** may be cited if central, marked with the word "preprint" or the server name plus the preprint DOI; replace by the published version when one exists.
- **Datasets and software:** cite like other sources; datasets carry a "[dataset]" prefix; software gets creator, title, venue, date, identifier and version; if a paper describes the software, cite both.
- Generative-AI use statement goes in a new section before the reference list.
- Secondary sources (kanzhiwang.com, journalsworld.com, scispace.com) repeat the numbered style and a 250-word abstract limit; the project's `research/paper2/style/STYLE-GUIDE-2026-10-27.md` records the same rules from an earlier read of the official page.

Budget consequence: the bibliography is at 49 of 50. Every IF paper added needs one existing entry removed. If the authors want an IF section of the related work, I would add the five priority-A papers (1-5) and drop the same number of the least-used classical references; the decision on what to drop is not mine.

## 6. Provenance of the verification

- Crossref per-DOI calls: 14 candidates plus the corrigendum 10.1016/j.inffus.2025.103287 (its `update-to` field names 10.1016/j.inffus.2025.103068, type erratum).
- Issue dates from Crossref `issued`: 104437 and 104860 carry future cover dates (2026-11 and 2027-03) while having been online since 2026-05-01 and 2026-10-13; citing the cover-date year follows IF's own practice.
- OpenAlex check: works citing Conformal Risk Control (W4290055968) with primary source IF returned zero results; OpenAlex reference coverage is incomplete (it counted only 37 citations for that paper), so this is weak evidence.
- Test compile: `inffus-candidates.bib` with `elsarticle-num.bst` gives 14 bibitems and no warnings (scratchpad, not in the repo).
- Nothing in `paper2/`, `references.bib` or `references-draft.bib` was edited. No GPU use and nothing under `runs/` was touched.
