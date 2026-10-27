```yaml
agent: lit-scout
date: 2026-10-28
brief: Resolve the 3 unidentified placeholders, the withdrawn comparator and the mismatches from CITATION-CHECK-2026-10-28.md, and draft a bibliography of at most 50 entries for Paper 2 (Information Fusion, elsarticle-num)
sources_examined:
  - arXiv API export.arxiv.org (2 batches, 46 ids, 2026-10-28) for authors, dates, comments
  - Crossref REST (works/<doi> and bibliographic queries) for every DOI below; update-to / updated-by fields read
  - OpenAlex (works?search, works/doi:10.48550/arxiv.<id> location lists) for published-version links and for the Finn 1968 record
  - Exa web search for: Finn and Johnson RCA Review index (worldradiohistory.com, CiNii), Holm 1979 (JSTOR/ime.usp.br copy), CRC and RADD and LaViDa and D3PM proceedings pages, CLIP PMLR page, Chair-Varshney abstract, Samy 2011 abstract, Vovk book page, Khaleghi corrigendum
  - arXiv HTML or PDF text, grep of the relevant passage only: UniDisc 2503.20853, Diffusion ITM 2305.16397, Gomes 2504.01225, Trust but Verify 2610.22380, DiSP 2602.22246, uChecker 2209.07068
coverage: >
  Metadata (authors, title, year, venue, pages, DOI) seen for all 49 entries. Claim-level reading is E1 (abstract or snippet) for most;
  E2-partial (passage located by text search, paper not read in full) only for the six papers listed above. No paper was read in full.
  NOT searched: Semantic Scholar graph, forward-citation expansion, OpenReview pages (blocked by a browser check), DBLP (rate-limited, 429),
  Google Scholar, a new 90-day concurrent-work sweep. This is a bibliography task; completeness here is not evidence of novelty.
claims:
  - statement: "The three section 13 placeholders (CFAR, sensor FDI, decision fusion) are replaced by identified, existing sources."
    status: supported
    evidence: entries 36-38 (CFAR), 39-40 and 45 (FDI), 41-44 (decision fusion), Crossref/CiNii/RCA index
    level: E1 (metadata seen; abstract seen only for Chair-Varshney, Rohling)
    confidence: 0.85
  - statement: "The bibliography has 49 entries, one under the Information Fusion limit of 50."
    status: supported
    evidence: references-draft.bib (49 keys, bibtex run with elsarticle-num.bst in the scratchpad, 49 bibitems, 6 warnings for missing pages or publisher)
    level: E4 (compiled here)
    confidence: 0.95
competing_explanations: []
unknowns:
  - "Whether Diao et al. 2024 covers CFAR in depth (abstract not seen; its reference list is CFAR-heavy)."
  - "Content of the Khaleghi 2013 corrigendum (Information Fusion 14(4):562)."
  - "Trust but Verify score definition (Eq. 4) and the spec's phrase 'unmasked position' (phrase not found in the HTML text)."
  - "Published versions of the preprints (PRISM, CORE, RemeDi, FreeCorrection, CO2Jump, DiSP, UniDisc, Remask Don't Replace): OpenAlex showed none for UniDisc, LlamaGen, CRC arXiv; not checked for the others."
next_test: n/a
ledger_rows_added: 0 (the brief says write only these two files; contract item 3 asks for papers rows, orchestrator to decide)
```

# Paper 2 reference draft (2026-10-28)

49 entries (limit 50). BibTeX: `references-draft.bib` (keys `firstauthorYEARtag`, compiles with `elsarticle-num.bst`).
Reference style per the style guide: numbers in order of first appearance (so the table order below is not the final number order), DOIs given, preprints marked, published version used where one exists.

Evidence legend. **M** = metadata seen in the named source. **C** = what was checked about the claim: `abs` = abstract only (E1); `passage` = relevant passage found by text search in the paper (E2-partial); `meta` = title and metadata only, claim attribution is the purpose of the citation and is not checked. Cite-in codes: **I** intro, **RW** related work, **M** method, **E** experiments.

## 1. The three placeholders and Rubin: resolved

| Spec s13 item | Decision | Entries | Why this choice |
|---|---|---|---|
| A2 "a CFAR reference" | Original paper, the standard order-statistic CFAR paper, one recent review | 36 Finn and Johnson 1968; 37 Rohling 1983; 38 Diao et al. 2024 | Finn and Johnson introduced the cell-averaging threshold set from neighbouring-cell clutter estimates. Rohling gives the CFAR definition (adaptive threshold for constant false-alarm rate) and the ordered-statistic variant. Diao is a recent review whose coverage of CFAR is inferred from its reference list only (see 3.1) |
| A3 "sensor fault detection and isolation" | Seminal survey plus one recent survey, plus the Information Fusion review that treats spurious or faulty sensor data | 39 Willsky 1976; 40 Gao, Cecati, Ding 2015; 45 Khaleghi 2013 (Information Fusion) | Willsky is the classical failure-detection survey. Gao et al. is a survey of fault diagnosis, Part I. Khaleghi is the Information Fusion review that names data imperfection and outliers. **Rejected**: Samy, Postlethwaite, Gu 2011 (Control Eng. Pract. 19:658), titled "Survey and application of sensor fault detection and isolation schemes": its abstract (Exa/ScienceDirect snippet) describes a neural-network SFDIA design tested on a UAV model, not a review. Do not cite it as a review |
| A4 "decision fusion with unreliable sensors" | Classical LLR/weighted-vote fusion rule, its distributed-detection setting, a recent review on unreliable or falsified sensors, and the classifier-combination view | 41 Chair and Varshney 1986; 42 Tenney and Sandell 1981; 43 Vempaty, Tong, Varshney 2013; 44 Kittler et al. 1998 | Chair-Varshney abstract (seen): individual decisions are weighted by detector reliability, then thresholded. That is the naive-Bayes / log-likelihood-ratio rule in spec s2.3. Vempaty et al. is a review of distributed inference with unreliable (falsified) sensor data |
| A5 "Rubin on missing data" | Biometrika 1976, DOI 10.1093/biomet/63.3.581 | 46 Rubin 1976 | The ETS 1975 item has the same title; the journal version is the citable one. The claim it should support is the missing-data mechanism distinction (red team note, RED-TEAM-GATE-SPEC line 127: the flagged set is data-selected, so p(x_j given x_R, G chosen) differs from p(x_j given x_R)). Rubin's abstract was not read here, so the spec must keep the sentence at "ignorability of the missingness mechanism" level |

## 2. Bibliography table

### A. Masked diffusion foundations, unified multimodal MDMs, tokenizer

| # | Key | Citation | ID / DOI | M (source) | C | Why cited, where |
|---|---|---|---|---|---|---|
| 1 | austin2021d3pm | Austin, Johnson, Ho, Tarlow, van den Berg. Structured denoising diffusion models in discrete state-spaces. NeurIPS 34, 2021 | arXiv 2107.03006 | proceedings.neurips.cc page (Exa) | abs | Absorbing-state discrete diffusion; origin of the mask corruption. I, RW |
| 2 | lou2024sedd | Lou, Meng, Ermon. Discrete diffusion modeling by estimating the ratios of the data distribution. arXiv v3 (comment: ICML 2024 oral) | arXiv 2310.16834 | arXiv API | meta | Score-entropy objective for discrete diffusion. RW |
| 3 | sahoo2024mdlm | Sahoo et al. Simple and effective masked diffusion language models. NeurIPS 37, 2024, pp. 130136-130184 | doi 10.52202/079017-4135; arXiv 2406.07524 | Crossref | meta | Simplified masked-diffusion training; the model class GATE scores. M |
| 4 | ou2025radd | Ou et al. Your absorbing discrete diffusion secretly models the conditional distributions of clean data. ICLR 2025 | arXiv 2406.03736 | ICLR proceedings page (Exa) | abs | Time-independent conditionals p(x_j given unmasked context): the property behind masked-likelihood scoring (spec Prop. 1). M |
| 5 | nie2025llada | Nie et al. Large language diffusion models. NeurIPS 38, 2025, pp. 56354-56392 | doi 10.52202/085713-1689; arXiv 2502.09992 | Crossref | meta | Scaled masked-diffusion LM. I |
| 6 | chang2022maskgit | Chang, Zhang, Jiang, Liu, Freeman. MaskGIT. CVPR 2022, pp. 11305-11315 | doi 10.1109/CVPR52688.2022.01103; arXiv 2202.04200 | Crossref | meta | Masked image-token generation, the image side of UniDisc. RW |
| 7 | swerdlow2025unidisc | Swerdlow, Prabhudesai, Gandhi, Pathak, Fragkiadaki. Unified multimodal discrete diffusion. arXiv v1 | arXiv 2503.20853 | arXiv API | passage (HTML text, Sec 1, 4.3, App G.1) | The backbone (UniDisc 1.4B, trained on web-scale image-text; retrieval on Winoground and DataComp1B). App. G.1 (read): overlay COCO objects on images, LLM-made wrong captions, randomly mask image and text, unmask, best-of-n over n noise masks chosen by the model's own likelihood. This is the closest prior art to re-infilling and must be compared. I, RW, M, E |
| 8 | yang2025mmada | Yang et al. MMaDA. NeurIPS 38, 2025, pp. 154021-154061 | doi 10.52202/085713-4636; arXiv 2505.15809 | Crossref | meta | Another unified multimodal diffusion LM. I, RW |
| 9 | li2025lavida | Li et al. LaViDa. NeurIPS 38, 2025 | arXiv 2505.16839 | NeurIPS proceedings page (Exa) | abs | Diffusion VLM (understanding side). Complementary-masking training. I, RW |
| 10 | shi2025muddit | Shi et al. Muddit. arXiv v5 (comment: ICLR 2026) | arXiv 2505.23606 | arXiv API | meta | Unified discrete diffusion for text and image. I, RW |
| 11 | sun2024llamagen | Sun et al. Autoregressive model beats diffusion: Llama for scalable image generation. arXiv v1 | arXiv 2406.06525 | arXiv API | meta | Source of the LlamaGen VQ-16 tokenizer used in the codebook-distance baseline and to define "clean" (spec s4.2, s6). M, E |

### B. Remasking and self-correction

| # | Key | Citation | ID / DOI | M (source) | C | Why cited, where |
|---|---|---|---|---|---|---|
| 12 | wang2025remdm | Wang, Schiff, Sahoo, Kuleshov. Remasking discrete diffusion models with inference-time scaling. NeurIPS 38, 2025, pp. 163488-163545 | doi 10.52202/085713-4927; arXiv 2503.00307 | Crossref | meta | Training-free remasking of a masked diffusion model's own samples. RW |
| 13 | kim2025prism | Kim, Kim, Lee, Pan, Kim, Kakade, Chen. Fine-tuning masked diffusion for provable self-correction (PRISM). arXiv v4 | arXiv 2510.01384 | arXiv API | abs | Learned per-token quality score, remask low scorers; needs finetuning, GATE does not. No venue claimed (record has none). RW |
| 14 | schiff2026proseco | Schiff et al. Learn from your mistakes: self-correcting masked diffusion models (ProSeCo). arXiv v4 (comment: NeurIPS 2026) | arXiv 2602.11590 | arXiv API | abs | Trained self-correction. RW |
| 15 | huang2025remedi | Huang, Wang, Chen, Qi. Don't settle too early: self-reflective remasking for diffusion language models (RemeDi). arXiv v1 | arXiv 2509.23653 | arXiv API | abs | Jointly predicts tokens and per-token confidence; remask low-quality tokens. RW |
| 16 | zhai2026core | Zhai, Mollah, Wang, Shah. CORE: context-robust remasking for diffusion language models. arXiv v3 | arXiv 2602.04096 | arXiv API | abs | Training-free; context-brittle tokens found by perturbing the masked context. Nearest training-free text-side remasking. RW |
| 17 | yao2026remask | Yao. Remask, don't replace: token-to-mask refinement in diffusion language models. arXiv v3 | arXiv 2604.18738 | arXiv API | abs | **Replaces the withdrawn arXiv 2605.26436.** Training-free remask of low-confidence positions. The count of error detectors is not confirmed for this id; do not state one. RW |
| 18 | lezama2022tokencritic | Lezama, Chang, Jiang, Essa. Improved masked image generation with Token-Critic. ECCV 2022, LNCS, pp. 70-86 | doi 10.1007/978-3-031-20050-2_5; arXiv 2209.04439 | Crossref | abs | Learned critic that decides which sampled image tokens to resample. Comparator family for plain-B top-k (an uncalibrated uncertainty ranking, not a learned critic; say so). RW, E |

### C. Closest work

| # | Key | Citation | ID / DOI | M (source) | C | Why cited, where |
|---|---|---|---|---|---|---|
| 19 | ouyang2026freecorrection | Ouyang et al. Training-free self-correction for multimodal masked diffusion models. arXiv v1 (name FreeCorrection is only in the abstract's code URL) | arXiv 2602.02927 | arXiv API | abs | Training-free self-correction in a multimodal MDM; blocks any "first to re-mask in a unified MDM" claim. RW |
| 20 | jhingran2026trustverify | Jhingran. Trust but verify: designing region-inhomogeneous forward dynamics for discrete diffusion. arXiv v1 (comment: NeurIPS 2026 workshop) | arXiv 2610.22380 | arXiv API | passage (HTML text) | Text-only 170M model, finetuned; sampler returns context tokens whose score is below a threshold annealed 0.5 to 0.1 to the absorbing state, within an edit budget from an assumed corruption rate 0.15 (read); reports a clean false-edit rate (read); GPT-2 surprisal flagging is its external-detector baseline (read). The spec's wording "scores the observed token at its unmasked position" was NOT found as a phrase in the text; Eq. 4 not read. Closest prior art. I, RW, E |
| 21 | gomes2025crc | Gomes, Martins, Zerva. A conformal risk control framework for granular word assessment and uncertainty calibration of CLIPScore quality estimates. Findings ACL 2025, pp. 12348-12365 | doi 10.18653/v1/2025.findings-acl.638; arXiv 2504.01225 | Crossref | passage (HTML text) | CRC with masking-derived CLIPScore distributions for caption words. Read: upper confidence bound from Hoeffding and Bentkus (1-delta), benchmarks FOIL-it, FOIL-nocaps, Rich-HF. So the guarantee is high-probability, calibrated on foil-labelled data, versus GATE's expected clean false-alarm proportion. I, RW, M |
| 22 | le2026co2jump | Le, Comas, Lattas, Moschoglou, Velez, Raj, Germuth, Beeler, Samaras, Qiu. Concurrent image understanding and generation: self-correcting coupled Markov jump processes (CO2Jump). arXiv v1 | arXiv 2607.13188 | arXiv API | abs | Remasking jump that retracts commitments when cross-modal evidence turns against them; training-free sampler. Quota-versus-threshold and Sec 4.4 claims in the spec are not checked here. RW |
| 23 | fang2025dropout | Fang, Yang, Chen, Zhao, Zhou. Enhancing vision-language model reliability with uncertainty-guided dropout decoding. NeurIPS 38, 2025, pp. 165747-165772 | doi 10.52202/085713-4991; arXiv 2412.06474 | Crossref | abs | Masks uncertain visual tokens at decoding; the s3 baseline is "Dropout-Decoding-inspired" only. RW, E |
| 24 | wan2026disp | Wan, Li, Fang, Ma, Wang. Self-purification mitigates backdoors in multimodal diffusion language models (DiSP). arXiv v1 | arXiv 2602.22246 | arXiv API | passage (HTML text) | Backdoor defence. Read: visual-token saliency = curvature of the output KL divergence wrt input embeddings (Fisher-Jacobian, gradients through the language tower), highest-saliency tokens masked, model finetuned. Not a corrupted-input detector. RW |

### D. Conformal prediction and conformal risk control

| # | Key | Citation | ID / DOI | M (source) | C | Why cited, where |
|---|---|---|---|---|---|---|
| 25 | angelopoulos2024crc | Angelopoulos, Bates, Fisch, Lei, Schuster. Conformal risk control. ICLR 2024 | arXiv 2208.02814 | ICLR proceedings page (Exa), arXiv API | abs | Controls the expected value of a monotone loss; the guarantee GATE uses (spec Prop. 5 is CRC applied). M |
| 26 | angelopoulos2023gentle | Angelopoulos, Bates. Conformal prediction: a gentle introduction. Found. Trends Mach. Learn. 16(4):494-591, 2023 | doi 10.1561/2200000101; arXiv 2107.07511 | Crossref | meta | Tutorial citation for split conformal and exchangeability. M |
| 27 | bates2023outliers | Bates, Candes, Lei, Romano, Sesia. Testing for outliers with conformal p-values. Ann. Statist. 51(1):149-178, 2023 | doi 10.1214/22-AOS2244; arXiv 2104.08279 | Crossref, arXiv API | meta | Conformal outlier detection with false-discovery control: the general-statistics precedent for "calibrate a flag threshold on clean data". Added as a neutral reference for the clean-calibration idea. Whether it fits GATE's token-nested-in-item loss is not checked. RW, M |
| 28 | vovk2005algorithmic | Vovk, Gammerman, Shafer. Algorithmic Learning in a Random World. Springer, 2005 | doi 10.1007/b106715 | Crossref (no authors in record), Springer page (authors) | meta | Original reference for conformal prediction. M |

### E. Image-text matching metrics, datasets, masked-likelihood scoring

| # | Key | Citation | ID / DOI | M (source) | C | Why cited, where |
|---|---|---|---|---|---|---|
| 29 | hessel2021clipscore | Hessel, Holtzman, Forbes, Le Bras, Choi. CLIPScore. EMNLP 2021, pp. 7514-7528 | doi 10.18653/v1/2021.emnlp-main.595; arXiv 2104.08718 | Crossref | meta | Image-text consistency metric; the T2I/consistency check and the metric Gomes builds on. M, E |
| 30 | radford2021clip | Radford et al. Learning transferable visual models from natural language supervision (CLIP). ICML 2021, PMLR 139:8748-8763 | arXiv 2103.00020 | PMLR page (Exa) | abs | The encoder behind CLIPScore. E |
| 31 | lin2014coco | Lin, Maire, Belongie, Hays, Perona, Ramanan, Dollar, Zitnick. Microsoft COCO. ECCV 2014, LNCS, pp. 740-755 | doi 10.1007/978-3-319-10602-1_48; arXiv 1405.0312 | Crossref (8 authors; the arXiv v3 author list has 10) | meta | Dataset (val2017 images, captions, instances). E |
| 32 | krojer2023diffusionitm | Krojer, Poole-Dayan, Voleti, Pal, Reddy. Are diffusion models vision-and-language reasoners? NeurIPS 36, 2023, pp. 8385-8405 | doi 10.52202/075280-0367; arXiv 2305.16397 | Crossref | passage (HTML text) | DiffusionITM: image-text matching with a diffusion model, normalised by the unconditional (no text) denoising error (read). So a null-normalised generative image-text score exists for continuous diffusion; GATE must not claim to be first. RW, M |
| 33 | salazar2020mlm | Salazar, Liang, Nguyen, Kirchhoff. Masked language model scoring. ACL 2020, pp. 2699-2712 | doi 10.18653/v1/2020.acl-main.240; arXiv 1910.14659 | Crossref | abs | Pseudo-log-likelihood from masking tokens one by one: the masked-likelihood score. M, RW |
| 34 | kauf2023plwl2r | Kauf, Ivanova. A better way to do masked language model scoring. ACL 2023 short, pp. 925-935 | doi 10.18653/v1/2023.acl-short.80; arXiv 2305.10588 | Crossref | abs | PLL-word-l2r for multi-piece words; supports the text-side "word unit, minimum over pieces" choice. The novelty file said the spec already cites it; the spec does not (check item B1), so add it to spec s2.4 or drop it here. M |
| 35 | li2022uchecker | Li. uChecker: masked pretrained language models as unsupervised Chinese spelling checkers. arXiv v1 (comment: COLING 2022) | arXiv 2209.07068 | arXiv API | passage (PDF text) | Read: unsupervised detection from the probability of the original input token under a masked LM, thresholded by u (UnsupDetection); BERT parameters frozen at detection. So a masked-likelihood token-anomaly detector with a fixed threshold is prior art (supports the novelty file's description). No Crossref record, so venue rests on the arXiv comment. RW |

### F. Classical fusion references (CFAR, sensor fault detection and isolation, decision fusion, missing data)

| # | Key | Citation | ID / DOI | M (source) | C | Why cited, where |
|---|---|---|---|---|---|---|
| 36 | finn1968adaptive | Finn, Johnson. Adaptive detection mode with threshold control as a function of spatially sampled clutter-level estimates. RCA Review 29(3):414-464, 1968 | no DOI; page range 414-464 (CiNii) vs 414-463 (OpenAlex) | RCA Review 1968 index page (authors H. M. Finn and R. S. Johnson, p. 414) via Exa/worldradiohistory; CiNii | meta | Original CFAR threshold-from-neighbours paper. The reference for "threshold set from the data to hold the false-alarm rate fixed", the analogy to GATE's clean-pair calibration. I, M |
| 37 | rohling1983cfar | Rohling. Radar CFAR thresholding in clutter and multiple target situations. IEEE TAES AES-19(4):608-621, 1983 | doi 10.1109/TAES.1983.309350 | Crossref; abstract in Exa | abs | CFAR definition and ordered-statistic CFAR. I, M |
| 38 | diao2024radar | Diao, Alves, Poussot, Azarian. A review of radar detection fundamentals. IEEE AES Magazine 39(9):4-24, 2024 | doi 10.1109/MAES.2022.3177395 | Crossref (2024 issue date), Exa | meta | Recent review; CFAR content inferred from its reference list, abstract not seen. Alternative if this is rejected: Rohling, "Ordered statistic CFAR technique, an overview" (DGON 2011, hdl 11420/12560, no DOI). I |
| 39 | willsky1976survey | Willsky. A survey of design methods for failure detection in dynamic systems. Automatica 12(6):601-611, 1976 | doi 10.1016/0005-1098(76)90041-8 | Crossref | meta | Seminal failure detection and isolation survey. Basis for "GATE is sensor fault detection and isolation" (spec s2.3). I, RW |
| 40 | gao2015survey | Gao, Cecati, Ding. A survey of fault diagnosis and fault-tolerant techniques, Part I. IEEE Trans. Ind. Electron. 62(6):3757-3767, 2015 | doi 10.1109/TIE.2015.2417501 | Crossref | meta | Recent survey of model-based and signal-based fault diagnosis. Abstract not seen. I, RW |
| 41 | chair1986optimal | Chair, Varshney. Optimal data fusion in multiple sensor detection systems. IEEE TAES AES-22(1):98-101, 1986 | doi 10.1109/TAES.1986.310699 | Crossref; abstract in Exa | abs | Optimum fusion given the detectors: decisions weighted by detector reliability, then thresholded. The log-likelihood-ratio fusion rule of spec s2.3. I, M |
| 42 | tenney1981detection | Tenney, Sandell. Detection with distributed sensors. IEEE TAES AES-17(4):501-510, 1981 | doi 10.1109/TAES.1981.309178 | Crossref | meta | Bayesian distributed detection (named in the Chair-Varshney abstract as the work it follows). Note: a short "Additions and Changes" item exists (AES-17(5):736, doi 10.1109/TAES.1981.309118). I |
| 43 | vempaty2013byzantine | Vempaty, Tong, Varshney. Distributed inference with Byzantine data: state-of-the-art review on data falsification attacks. IEEE Signal Process. Mag. 30(5):65-75, 2013 | doi 10.1109/MSP.2013.2262116 | Crossref | meta | Review of decision fusion when some sensors report falsified data. The "unreliable sensors" reference. Abstract not seen. I, RW |
| 44 | kittler1998combining | Kittler, Hatef, Duin, Matas. On combining classifiers. IEEE TPAMI 20(3):226-239, 1998 | doi 10.1109/34.667881 | Crossref | meta | Product and sum rules for combining classifier outputs; the classifier-combination view of naive-Bayes fusion. Optional (first to cut if space is short). RW |
| 45 | khaleghi2013multisensor | Khaleghi, Khamis, Karray, Razavi. Multisensor data fusion: a review of the state-of-the-art. Information Fusion 14(1):28-44, 2013 | doi 10.1016/j.inffus.2011.08.001 | Crossref; Exa | meta | Information Fusion review; frames sensor imperfection and spurious data. A corrigendum exists (Information Fusion 14(4):562, doi 10.1016/j.inffus.2012.10.004; content not read, so verify nothing cited from the review was corrected). I |
| 46 | rubin1976inference | Rubin. Inference and missing data. Biometrika 63(3):581-592, 1976 | doi 10.1093/biomet/63.3.581 | Crossref | meta | Missing-data mechanisms, for the marginalise-versus-impute comparison and the caution that the flagged set is data-selected (see section 1). M |

### G. Statistics used in the analysis plan

| # | Key | Citation | ID / DOI | M (source) | C | Why cited, where |
|---|---|---|---|---|---|---|
| 47 | mcnemar1947 | McNemar. Note on the sampling error of the difference between correlated proportions or percentages. Psychometrika 12(2):153-157, 1947 | doi 10.1007/BF02295996 | Crossref | meta | Exact McNemar test on discordant pairs (primary endpoint). E |
| 48 | holm1979sequentially | Holm. A simple sequentially rejective multiple test procedure. Scand. J. Statist. 6(2):65-70, 1979 | no Crossref DOI; JSTOR 4615733 | Exa (first page of the paper read, abstract and header) | abs | Holm correction over the corruption family (spec s7). E |
| 49 | clopper1934 | Clopper, Pearson. The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika 26(4):404-413, 1934 | doi 10.1093/biomet/26.4.404 | Crossref | meta | Exact binomial intervals for coverage and false-alarm proportions. E |

## 3. Fixes to the citation check items

| Check item | Problem | Resolution | New level |
|---|---|---|---|
| A2-A4 | Three unidentified references | Section 1 above | metadata verified |
| A5 Rubin | Two works with one title | Biometrika 1976 chosen (entry 46) | metadata verified; claim not checked |
| B9 Targeted Remasking (2605.26436) | Withdrawn, superseded | arXiv API comment re-read today: "withdrawn ... superseded by arXiv:2604.18738". Cite entry 17 (2604.18738). Do not cite 2605.26436, and do not state its v1 date (API gives 2026-04-06 under a 2605 id; unresolved, irrelevant once dropped) | resolved |
| B10 three-detector count | The count belongs to the withdrawn abstract | Say "error-detection and remask decomposition" for 2604.18738, no count | resolved |
| B1 Kauf and Ivanova "cited in the spec" | Spec does not cite it | Included as entry 34; the spec (s2.4 or s4.2 text side) must add the citation, or remove entry 34 | open, needs a spec edit |
| B2 Soft-Masked BERT (2005.07421) | Called a masked-likelihood detector | Correct sentence: "a learned error-detection network whose output soft-masks the input of a BERT correction network" (abstract, per the check). Not in this bibliography | corrected wording |
| B3 ELECTRA (2003.10555) | Called a masked-likelihood detector | Correct sentence: "pretraining by replaced-token detection with a discriminator" (abstract). Not in this bibliography. OpenAlex mapped this arXiv id to an unrelated 2026 title, so do not trust OpenAlex for this id; arXiv API title and authors are correct | corrected wording |
| B15 BayesER (2610.05125) | Called a calibration-error measure | Correct sentence: "post-hoc Bayesian decoding that reorders token commitment by predictive entropy" (abstract, per the check). Not in this bibliography | corrected wording |
| A11 uChecker | Threshold description not in abstract | Now confirmed in the paper text (entry 35): probability of the original input token, threshold u | supported (E2-partial) |
| A17 DiSP | Saliency and gradient labels not in abstract | Confirmed in the paper text (entry 24) | supported (E2-partial) |
| A12 Diffusion ITM | Null normalisation unconfirmed | Confirmed (entry 32); continuous diffusion, noise-prediction error | supported (E2-partial) |
| A8 Gomes | Calibration details not in abstract | Hoeffding plus Bentkus (1-delta) bound and FOIL-labelled benchmarks confirmed (entry 21) | supported (E2-partial) |
| A15 UniDisc | G.1, size, retrieval unverified | All three confirmed (entry 7) | supported (E2-partial) |
| A7 Trust but Verify | "Unmasked position" score and "no meaningful likelihood" unverified | Annealed threshold, edit budget and clean false-edit rate confirmed; **the phrase "unmasked position" not found and Eq. 4 not read; "no meaningful likelihood" not checked** | partial; still open |
| B17 PRISM | Venue "ICLR/ICML 2026" unsupported | Entry 13 states no venue | resolved |
| A1 CRC | Venue from a snippet | ICLR 2024 proceedings page seen (entry 25) | resolved |
| A10 Token-Critic | "proxy" label | Entry 18 comment: plain-B is an uncalibrated ranking, not a learned critic | wording to apply in spec s4.2 |
| A16 Dropout Decoding, A14 FreeCorrection, A13 Salazar, A6 McNemar | ids missing in spec | Ids and DOIs in the table | resolved |

## 4. Reserve list (verified metadata, not in the 49; add only if a slot is needed)

arXiv 2606.12807 Detect, Remask, Repair (Zou et al., 2026-06); 2512.15596 Corrective DLMs (Zhang et al.); 2509.23625 RIV; 2606.06031 NAVIRA; 2510.06308 Lumina-DiMOO (32 authors, arXiv v1); 2306.10193 Conformal language modeling (Quach et al., arXiv comment: ICLR 2024); 2101.02703 / doi 10.1145/3478535 Risk-controlling prediction sets (J. ACM 68(6)); 2110.01052 / doi 10.1214/24-aoas1998 Learn then Test (Ann. Appl. Stat. 19(2)); 2005.07421 / doi 10.18653/v1/2020.acl-main.82 Soft-Masked BERT; 2003.10555 ELECTRA (ICLR 2020 per arXiv comment); 1705.09406 Baltrusaitis et al., multimodal machine learning survey; Isermann, doi 10.1016/0005-1098(84)90098-0 (Automatica 20(4):387-404); Kam, Zhu, Gray, doi 10.1109/7.256317 (correlated local decisions).

## 5. Budget notes and cut order

49 of 50. The style guide says to cite surveys and primary sources only where the argument uses them. If the text needs two or more extra references, cut in this order: 44 Kittler, 49 Clopper-Pearson, 10 Muddit, 34 Kauf and Ivanova, 28 Vovk (keep 26 as the tutorial), 2 Lou et al., 5 LLaDA, 40 Gao et al., 27 Bates et al. All 49 are used by at least one section, but the ones listed are not load-bearing.

## 6. Unresolved or weak points

1. Entry 38 (Diao): CFAR coverage not confirmed from an abstract. Alternative named above.
2. Entry 20 (Trust but Verify): the spec's "unmasked position" sentence and the "no meaningful likelihood" paraphrase are not verified. This is the closest prior art, so a full read (`paper-reader`) of Sec 3 to 4 is the right next step before the delta sentence is frozen.
3. Entry 22 (CO2Jump): the quota-not-threshold claim and the fine-tuned-backbone point (abstract says training-free) are unchecked.
4. Preprint-only entries (2, 7, 10, 11, 13, 14, 15, 16, 17, 19, 20, 22, 24, 35): venue unverified, or none exists. Re-check for published versions at submission time. OpenAlex showed no published version for UniDisc and LlamaGen.
5. Entry 36 page range disagrees between sources (414-464 vs 414-463).
6. Entry 48 has no DOI that resolves in Crossref (JSTOR identifier only).
7. Entries 39, 40, 42, 43, 44, 45, 46: attribution of the fusion framing to these papers rests on the spec's own framing (s2.3) and general knowledge; only the Chair-Varshney, Rohling and Holm abstracts were seen. The Introduction sentences should be written to claim only what those abstracts support.
8. No new 90-day concurrent-work sweep was run in this task. Within 90 days of today, the entries here dated after 2026-07-30 are Trust but Verify (2026-10-02) and the ProSeCo v4 update (2026-10-20). The re-audit's own sweep (2026-10-28) is the last one done.
9. A ledger `papers` row for each entry was not added (the brief limits writes to these two files).
