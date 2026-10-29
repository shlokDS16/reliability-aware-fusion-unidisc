---
agent: paper-reader
date: 2026-10-29
brief: Exemplar study for Paper 2 at IEEE TNNLS (Full Paper, IEEEtran, 10 + up to 5 paid pages); 8 close method papers read; blueprint and 15 rules.
sources_examined:
  - arXiv:2306.15711 (Devillers, Maytie, VanRullen; Semi-supervised multimodal representation learning through a Global Workspace; TNNLS 36(5) 7843-7857)
  - arXiv:2301.02424 (Wang et al.; Conformal Loss-Controlling Prediction; TNNLS 36(2) 2973-2983)
  - arXiv:2502.01785 (Alawode et al.; AquaticCLIP; TNNLS 37(8) 3956-3969)
  - arXiv:2512.05515 (Wen et al.; DashFusion; arXiv comment says accepted to TNNLS 2025; not verified on Xplore)
  - arXiv:2408.08704 (Nan et al.; Beyond the Hype, RadVUQA; TNNLS 36(10) 17623-17634)
  - arXiv:2303.16203 (Li et al.; Your Diffusion Model is Secretly a Zero-Shot Classifier; ICCV 2023)
  - arXiv:2404.01291 (Lin et al.; VQAScore and GenAI-Bench; ECCV 2024)
  - arXiv:2306.02050 (Zhang et al.; Provable Dynamic Fusion for Low-Quality Multimodal Data, QMF; ICML 2023)
  - research/paper2/venue/TNNLS-DEEP-DIVE-2026-10-29.md ; research/paper2/benchmark/LENS-CRAFT.md ; LENS-ARGUMENT.md (headings only)
coverage: >
  Main body of all eight papers read from pdftotext dumps (introduction, method/theory, experiments, discussion, limitations, conclusion).
  Nine pages viewed as rendered images (CLCP p6, DashFusion p4 and p8, QMF p3, Beyond-the-Hype p1, Global Workspace p8, Diffusion Classifier p7,
  VQAScore p8, AquaticCLIP p7) to check figure density, bolding and table layout. NOT read closely: reference lists; appendices and supplements
  (headings, captions and table names only: Diffusion Classifier A-G, VQAScore A-F, QMF A-C, AquaticCLIP supplement, Global Workspace A-B).
  Counts of words, pages, equations and references come from text extraction and are approximate (column interleaving; equation counts are the
  highest numbered equation). Page numbers below are PDF pages of the arXiv file, NOT journal pages.
  Version caveat: seven of the eight are arXiv versions; for the three TNNLS papers with a known journal length the published version differs
  (Global Workspace 15 journal pages vs 18 arXiv pages; AquaticCLIP 14 journal pages and 122 references vs a 29-page arXiv preprint that merges
  the supplement; Beyond the Hype 12 pages in both; CLCP 11 pages in both). Tables of structure describe the arXiv file.
claims:
  - statement: Accepted TNNLS method papers in this set state 3 to 4 contributions, validate with 3 to 5 tables, and use baselines from older methods; none uses more than ~12 numbered equations in the main text
    status: supported
    evidence: per-paper dissections below (Section 3)
    level: E2
    confidence: 0.75
  - statement: A TNNLS paper with a theorem and no baseline comparison exists (CLCP); a TNNLS paper that admits a single-seed main experiment exists (Global Workspace p13)
    status: supported
    evidence: CLCP Section IV p5-10; Global Workspace VIII-B p13
    level: E2
    confidence: 0.9
  - statement: The closest TNNLS reliability-aware fusion methods (TCPFMC, uncertainty-aware multihop evidence GNN, informative data selection with uncertainty) could not be obtained as full text from arXiv
    status: supported
    evidence: arXiv API title queries 2026-10-29 returned no match for these titles
    level: E1
    confidence: 0.7
competing_explanations:
  - "Median numbers (4 figures, 4-5 tables) come from 8 papers of which 5 are TNNLS; they describe typical, not best, TNNLS practice. 'Best paper TNNLS has published' cannot be identified from this sample; TNNLS awards are judged about two years after publication (deep dive 1.10)."
unknowns:
  - Final journal layout of DashFusion (arXiv v1 is a JOURNAL OF LATEX CLASS FILES preprint).
  - Whether Flow-CLIP (arXiv 2610.21937, surfaced by a web search, compositional image-text matching) is concurrent work; abstract not read here.
  - TNNLS reviewer expectations beyond what accepted papers show.
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
---

# TNNLS exemplar study for Paper 2 (2026-10-29)

Evidence tags as in CONTRACT: everything below is **source fact** (from the cited page of the cited paper) unless marked **[inference]**. A paper's own
claim is E2 for "the paper reports X", never for "X is true". Quotes are under 15 words with a page.

## 1. Selection

Selection rule: method papers (or method-plus-benchmark), close to reliability-aware fusion, cross-modal verification or generative scoring, with a
legally available full text. TNNLS first (5), then top-venue papers nearest to our method (3).

| # | Paper | Venue | arXiv | Pages (arXiv / journal) | Why it is here |
|---|---|---|---|---|---|
| T1 | Conformal Loss-Controlling Prediction | TNNLS 36(2) 2025 | 2301.02424 | 11 / 11 | Theorem-first TNNLS paper with a finite-sample guarantee; experiments only verify the guarantee (no baselines). Model for how a guarantee is stated and tested. |
| T2 | Semi-supervised Multimodal Representation Learning through a Global Workspace | TNNLS 36(5) 2025 | 2306.15711 | 18 / 15 | Cross-modal (vision-language) TNNLS paper with formal "properties", an honest limitations subsection and a controlled design (all models share one architecture). |
| T3 | AquaticCLIP | TNNLS 37(8) 2026 | 2502.01785 | 29 / 14 | Recent TNNLS vision-language method: numbered contributions with section pointers, two ablation tables, CLIP/CoOp/MaPLe/GPT-4V/BLIP-2 baselines, a complexity subsection. |
| T4 | DashFusion (multimodal sentiment) | TNNLS 2025 (per arXiv comment) | 2512.05515 | 12 / unknown | Multimodal fusion method; plain structure in IEEE layout; ablation, bottleneck-size sensitivity and a fusion-cost table (MAdds). |
| T5 | Beyond the Hype (RadVUQA) | TNNLS 36(10) 2025 | 2408.08704 | 12 / 12 | Benchmark paper in TNNLS: evaluates corporate models (GPT-4o, BLIP-2 and others) with a question-driven discussion; model for a hard-negative benchmark section. |
| H1 | Your Diffusion Model is Secretly a Zero-Shot Classifier (Diffusion Classifier) | ICCV 2023 | 2303.16203 | 18 / 9 + refs | Generative scoring of text-image pairs via the conditional likelihood; compares with CLIP on Winoground; cost and negative results reported. |
| H2 | Evaluating Text-to-Visual Generation with Image-to-Text Generation (VQAScore) | ECCV 2024 | 2404.01291 | 29 / 11 + refs | Generative likelihood of "Yes" as an alignment score; baseline taxonomy; matched-backbone comparison; hard-negative benchmarks (Winoground, EqBen) against CLIP, BLIP-2 score, GPT-4V methods. |
| H3 | Provable Dynamic Fusion for Low-Quality Multimodal Data (QMF) | ICML 2023 | 2306.02050 | 18 / 9 + refs | The closest theory-plus-method paper to reliability-aware fusion: theorems on when dynamic weighting beats static weighting, an assumption checked by correlation. |

Files: `research/paper2/tnnls/exemplars/<arXiv id>_<slug>.pdf` (eight PDFs, about 70 MB, NOT committed; treated as data, nothing executed).

### 1.1 Papers that need Shlok's VIT e-gateway login (not obtainable legally from arXiv by title search, 2026-10-29)
From the deep dive list, in order of value for us:
1. **TCPFMC**, Trustworthy Cyclic Progressive Fusion for Multimodal Classification, 10.1109/TNNLS.2026.3661974 (37(9) 4246-4260; energy-score reliability per modality plus cyclic fusion; six datasets; 15 pp, 69 refs; GitHub). The nearest TNNLS method to ours.
2. Uncertainty-Aware GNN: A Multihop Evidence Fusion Approach, 10.1109/TNNLS.2025.3581083 (theory plus fusion plus loss; 15 pp, 67 refs).
3. Informative Data Selection With Uncertainty for Multimodal Object Detection, 10.1109/TNNLS.2023.3270159 (13 pp, 55 refs; corruption-robustness protocol).
4. Resisting Noise in Pseudo Labels: Audible Video Event Parsing With Evidential Learning, 10.1109/TNNLS.2024.3505674 (15 pp, 50 refs).
5. MALFM-Captioner (discrete-diffusion captioner with gated fusion), 10.1109/TNNLS.2026.3690650 (13 pp; the only discrete-diffusion TNNLS paper found).
6. Counterfactual Explanation of Predictive Uncertainty in Multimodal Models, 10.1109/TNNLS.2024.3476080; Satellite Pose Set Estimation by Uncertainty-Guided Conformal Keypoint Detection, 10.1109/TNNLS.2025.3598481.
7. Final published versions of T2, T3, T4 (layout and page budget) if Shlok wants page-exact numbers.
Candidates considered and not downloaded (budget): ProtoCLIP (arXiv 2206.10996, arXiv comment says accepted by TNNLS), SugarCrepe (hard negatives), Clark and Jaini diffusion zero-shot classifiers, "Revisiting the role of language priors" (generative VLM scoring).

## 2. Page-by-page structure (arXiv PDF pages) and share of the main text

Shares are approximate words of the main text without references and appendix (extraction), or page shares where noted.

### T1 CLCP (11 pp; 160-word abstract; ~6.6k body words; 38 refs; 8 figures, 1 table, 1 algorithm, 1 definition, 1 theorem with in-text proof, ~11 equations)
- p1 abstract, keywords, Introduction opens. p2 introduction continues: gap, the guarantee in one displayed line, **3 bullet contributions**, roadmap paragraph. p2-3 Section II background (ICP, conformal risk control). p3-5 Section III: set predictor, algorithm box (p4), Definition 1, Theorem 1 and its proof in the main text (p4), "CP is a special case" argument (p4-5). p5-10 Section IV experiments: three applications (UCI classification with class-varying loss, high-impact weather, temperature regression). p10 conclusion (one paragraph, future work as the limitation). p10-11 references.
- Shares: introduction 22%, background plus method plus theory 27%, experiments 45%, conclusion 3%.

### T2 Global Workspace (18 pp arXiv; 15 journal; 231-word abstract; ~12k body words; 49 refs; 8 figures, 3 tables, ~11 equations)
- p1-2 introduction (short, 4%: one paragraph of motivation, one of "we propose") and related work (three subsections). p3-4 Section III Problem Statement: four named properties (translation, contrastive, demi-cycle, cycle), four relations R1-R4 between them, Table I of the compared models (p4). p4-5 datasets (three). p6-7 model. p7-12 experiments: primary properties (p8-9), secondary (p10), downstream (p10-11), effect of unpaired data (p11), COCO retrieval with Tables II and III (p12, p14). p13-14 discussion: summary, **Limitations and open questions (p13)**, future model extensions, implications. p15-16 references; p17-18 appendix (architectures, dataset generation).
- Shares: intro 4%, related 12%, problem statement 9%, datasets 12%, model 12%, experiments 40%, discussion 11%.

### T3 AquaticCLIP (arXiv 29 pp; main text p1-8; 206-word abstract; 149 refs in the arXiv file, 122 in the journal version)
- p1 abstract and introduction. p2 Fig. 1 (three-step pipeline) and **three numbered contributions each with a section pointer (Sec. III-A to C, III-D to F, Sec. IV)**; related work (short, 9%). p3-5 Section III model (dataset construction, then encoders, loss, zero-shot inference; Fig. 2 architecture p4, Fig. 3 module detail p5). p5-8 Section IV experiments: setup, datasets, ablations (Tables I-II, p7), SOTA list, zero-shot comparison (Table III, p7), linear probe, detection (Table IV, p8), computational complexity (IV-H, p8). p8 conclusion (one paragraph, no limitations paragraph). p9-12 references. p13-29 supplement (dataset curation, extra ablations, extra tasks, visual results).
- Shares of the main text: intro 19%, related 9%, model 33%, experiments 36%, conclusion 3%.

### T4 DashFusion (12 pp; 195-word abstract; ~7.2k body words; 38 refs; 4 figures, 5 tables, ~12 equations)
- p1 abstract, introduction, Fig. 1 (problem: temporal misalignment and heterogeneity). p2 introduction ends with **3 bullet contributions** and a roadmap paragraph; related work (three subsections). p3 method begins. p4 Fig. 2 (whole architecture), preliminaries. p5-6 alignment, contrastive loss, hierarchical bottleneck fusion, objective, Fig. 3. p7 datasets, metrics (5 seeds averaged), features. p8 baselines (eight, each described in one line) and Table II. p9 Table III, Fig. 4 (bottleneck size sensitivity). p10 Table IV (component ablation), Table V (fusion variants with MAdds), conclusion. p10-12 references.
- Shares: intro 16%, related 12%, method 31%, setup 16%, results 23%, conclusion 3%.

### T5 Beyond the Hype (12 pp; 213-word abstract; ~8.1k body words; 27 refs; 4 figures, 6 tables)
- p1 abstract, Fig. 1 (benchmark composition as five questions). p1-2 introduction, Table I (comparison with existing benchmarks), **4 bullet contributions** (p2). p2-3 related work, Fig. 2. p3-4 methods (data, question design). p5 experimental settings (models, hardware, decoding, LLM-as-judge metric). p6 results (Table II: capability by question type, mean with spread in brackets). p7-10 discussion built as bold run-in questions (CT windowing, chain-of-thought, unharmonised data, synthetic data), Tables III-VI, Figs. 3-4. p11 conclusion as five bullet findings. p11-12 references.
- Shares: intro 11%, related 11%, methods 21%, settings 10%, results 9%, **discussion 35%**, conclusion 2%.

### H1 Diffusion Classifier (18 pp; 202-word abstract; main text p1-9; 84 refs; 9 figures, 12 tables in total of which 5 in the main text)
- p1-2 abstract, introduction with the framing sentence and Fig. 1 (overview with the objective on the figure). p2-3 related work (three paragraphs). p3 method (Bayes rule, ELBO, Algorithm 1). p4 variance reduction by paired difference testing (Figs. 2-3) and practical considerations (timestep, efficient classification, runtime stated). p5 setup and baselines (Fig. 4). p6 **six numbered research questions**, Table 1 zero-shot results. p7 Table 2 (how in-distribution each test set is for the generator), Winoground (Fig. 5, Table 3). p8 Table 4 supervised ImageNet, Fig. 6 effective robustness with Clopper-Pearson intervals. p9 Table 5 objective ablation, conclusion with accelerating inference and design caveats. p10-12 references. p13-18 appendix A-G, including "Techniques that did not help" (p17-18, Tables 11-12, Figs. 8-9).
- Page shares of main text: introduction 20%, related 10%, method plus practical 30%, setup 9%, results 30%.

### H2 VQAScore (29 pp; main text p1-11; ~290-word abstract; 94 refs; 4 figures and 5 tables in the main text)
- p1-4 introduction with Figs. 1-3 and a **numbered "Contribution summary" (3 items, p4)**. p5 related work (short), method (one equation, one template, a model description). p6 experiments: **baseline taxonomy of five method types** (p6), SOTA on matching benchmarks. p7 Table 1 (Winoground, EqBen). p8 Table 2 (same backbones, ours vs three decomposition methods, random-chance row, green highlight), Table 3 (skill breakdown). p9 Table 4 (agreement with human ratings), GenAI-Bench (Fig. 4, p10). p11 Table 5 (video and 3D), conclusion containing "Limitations and future work". p12-17 references. p17-29 appendix (skills, benchmark detail, ablations of language model, question template, answer format).
- Shares of the main text: introduction 26%, related 6%, method 8%, experiments 34%, benchmark 18%, extension 7%, conclusion 2%.

### H3 QMF (18 pp; 138-word abstract; main text p1-9; **theory p3-5**; refs p10-13; appendix p14-18; 3 figures, 3 main tables, 2 theorems, 1 lemma, 1 assumption, 1 algorithm)
- p1-2 abstract, introduction, Fig. 1 (accuracy gap against the best unimodal model on noisy data), **3 bullet contributions** (theory, a design principle, a method). p2-3 related work (two subsections). p3 Fig. 2 (the bound drawn as an equation-figure with the hypothesis-space picture), Section 3 theory begins with the roadmap sentence. p4 Theorem 1 (bound with an explicit covariance term), Theorem 2 (dynamic beats static under a stated sign condition), remark. p5 Assumption 1 (uncertainty estimator positively correlated with loss), Lemma 1, Section 4 method. p6 Algorithm 1; experiments open with **three questions mapped to Theorem 1, Theorem 2 and Assumption 1**. p7 Fig. 3 (10 seeds: accuracy and Pearson r). p8 Table 1 (50% corrupted; best three marked). p9 Table 2 ablation, Table 3 Pearson r between fusion weights and loss, **Section 6 Limitations**, conclusion. p14 proofs (Appendix A), p15 experimental details, p16-18 full tables with standard deviations.
- Page shares: introduction 17%, related 9%, theory 26%, method 13%, experiments 30%, limitations plus conclusion 5%.

## 3. Dissection by dimension

### 3.1 How the contribution is stated
| Paper | Form | Where | Evidence pointer? |
|---|---|---|---|
| T1 | 3 bullets (framework; proved guarantee; empirical verification) | p2 | No; claims are in order of the sections. |
| T2 | one "in short" sentence, no bullets | p2 | Section III names the properties and relations the experiments test. |
| T3 | 3 numbered items | p2 | **Yes: each item ends with its section range.** |
| T4 | 3 bullets (alignment; fusion; "extensive experiments ... SOTA") | p2 | No. |
| T5 | 4 bullets (benchmark; new scenarios; larger models; insights) | p2 | No; the conclusion repeats 5 findings as bullets (p11). |
| H1 | prose paragraph plus "11 benchmarks" evidence claim | p2 | Six numbered research questions on p6 act as the pointer. |
| H2 | 3 numbered items under "Contribution summary" | p4 | Partly (tables and figures named in the text). |
| H3 | 3 bullets (theory; principle; method) | p2 | **Yes, through Q1-Q3 on p6**, each tied to Theorem 1, Theorem 2, Assumption 1. |
Three or four contributions is the norm in all eight. The strongest pair for claims-versus-evidence is H3 (question to theorem) and T3 (item to section).

### 3.2 Theory presentation
- **H3 QMF (p3-5, p14).** Notation subsection (3.1), then a one-sentence roadmap, Theorem 1, Theorem 2, a remark that explains the sign condition, then Assumption 1 and Lemma 1 in the method section. Main text carries the statements and an informal summary; full proofs sit in Appendix A (p14, about 330 words). Fig. 2 (p3) draws the bound term by term (empirical loss, complexity, "uncertainty awareness" covariance term) next to a hypothesis-space picture. Limitation of the theory stated openly (p9): it rests on Assumption 1.
- **T1 CLCP (p3-5).** Short enough to keep inside the paper: algorithm box, one definition, one theorem, a proof of about 200 words, and a corollary-style remark that the earlier method is a special case. No appendix.
- **T2 (p3-4).** Not theorems but named properties with a small calculus (relations R1-R4, one footnote proof, p4) that fix what experiments must measure.
- T3, T4, T5, H1, H2 have no theorems. H1 derives its estimator in three displayed steps (Bayes, ELBO, paired differences; p3-4); H2 has one equation.
- **[inference]** For a TNNLS method paper the pattern that earns space is: notation (0.3 page), 2 propositions or theorems with an assumption list and a stated sign or correlation condition, a one-paragraph interpretation, proofs in an appendix, and a figure that restates the bound. Short proofs (under ~200 words) may stay in place, as in T1.

### 3.3 Figure catalogue (main text)
| Paper | Count | Types | What they prove | Density |
|---|---|---|---|---|
| T1 | 8 | bar plots of loss frequency vs level; boxen plots; set-size bars (p6-10) | empirical validity of Theorem 1 (bars below the preset level) and the efficiency trade-off | 2 per page, full column; no schematic, no pipeline figure |
| T2 | 7 + 1 | model-property diagram (p3), dataset examples (p5), architecture (p6), learning-curve panels (p8, p11, p12) | translation and alignment versus number of paired examples; the 4-7x data-saving claim | multi-panel, log axes, one figure fills a column-width block |
| T3 | 3 | pipeline (p2), architecture (p4), module detail (p5) | design only; quantitative evidence is in tables | schematics only in the main text; qualitative results in the supplement |
| T4 | 4 | problem illustration (p1), architecture (p4), bottleneck layer (p6), sensitivity plot (p9) | the problem, the method, the one hyper-parameter | 1 data figure only |
| T5 | 4 | benchmark composition (p1), failure examples (p3), hallucination plot (p7), degradation plot (p10) | benchmark scope and deficiency findings | question-wheel teaser on page 1 |
| H1 | 6 in main | overview with the objective on the figure (p2), error-vs-timestep (p4), scaling curves (p5), Winoground examples (p7), effective-robustness plot with intervals (p8) | variance reduction, cost-accuracy trade-off, robustness claim | one figure per claim |
| H2 | 4 | method figure (p2), side-by-side score examples vs CLIPScore (p3-4), benchmark composition and leaderboard (p10) | the failure of CLIPScore on compositions | qualitative first, quantitative in tables |
| H3 | 3 | accuracy gap under noise (p2), bound/hypothesis-space equation-figure (p3), accuracy and Pearson r over 10 seeds (p7) | the motivating problem, the theory, the link between uncertainty quality and accuracy | each figure carries one of the three contributions |
Median 4 figures; at least one schematic of the whole method (T3, T4, H1, H2) and one figure that visualises the result the theory predicts (T1, T2, H1, H3).

### 3.4 Table catalogue and reporting conventions
| Paper | Main tables | Baselines | Metrics and variability | Bolding or highlighting | Significance |
|---|---|---|---|---|---|
| T1 | 1 (dataset list, p5) | none (guarantee verified) | frequency of loss above level, 10 repeats averaged, plots only | n/a | none |
| T2 | 3 (compared models p4; linear probe and zero-shot p12; COCO retrieval p14) | ablated variants of one architecture (supervised, contrastive, cycle) | single seed for the main sweeps (admitted p13); COCO retrieval mean with spread over 5 runs | not seen | none |
| T3 | 4 (ablation x2 p7; zero-shot and supervised classification p7; detection p8) | Frozen and fine-tuned CLIP, CoOp, MaPLe, GPT-4V, BLIP-2, MarineGPT, vision-only ResNet/ViT/ConvNeXt | accuracy and F1 as "acc|F1", single values | **bold best, underline second best** (p7) | none, no standard deviations |
| T4 | 5 (datasets, MOSI/MOSEI, CH-SIMS, ablation, fusion variants with cost) | eight published methods, some reproduced under one setting and marked | 5-seed average; no spread printed | bold best; ties and losses visible (not best on Acc-7) | none |
| T5 | 6 (benchmark comparison; capabilities; robustness; windowing; chain-of-thought; synthetic data) | 10+ LVLMs including GPT-4o, BLIP-2, Gemini, Claude, medical models | mean score with spread in brackets; hallucination rate | not seen | none |
| H1 | 5 (zero-shot; in-distribution check; Winoground; ImageNet; objective ablation) | CLIP RN50, OpenCLIP ViT-H/14 "for reference only", synthetic-data classifier, SD-features classifier | accuracy; 99.5% Clopper-Pearson intervals on Fig. 6 | cells highlighted where ours wins (Table 4) | intervals, no tests |
| H2 | 5 | five method families (CLIPScore, BLIPv2Score; human-feedback models; visual programming; divide and conquer; GPT-4V methods) | accuracy per Winoground/EqBen split, AUROC, pairwise accuracy | **green rows for ours, random-chance row** (p8) | none |
| H3 | 3 main + 3 appendix | static and dynamic fusion baselines, unimodal baselines | mean, std and worst-case over 10 seeds (stds in appendix); Pearson r | best three bold, best highlighted | worst-case accuracy as a robustness readout |
Of the TNNLS papers none prints a statistical test; two (T1, T4) average over repeats; only T5 prints spread in the main table. **[inference]** A paper that prints confidence intervals and paired tests would sit above this sample on rigor; it will not be penalised for it.

### 3.5 Validation protocol
- **Datasets:** T3 about 14 (7 for zero-shot, 4 for detection plus segmentation); T4 3; T5 2 modalities, 5 question families; H1 11 benchmarks; H2 about 10 (Winoground, EqBen, TIFA160, Pick-a-Pic, DrawBench, EditBench, COCO-T2I, Flickr8K, GenAI-Bench, video and 3D); H3 4; T2 3; T1 24 (20 UCI plus 4 weather datasets).
- **Corporate or foundation baselines:** T3 (CLIP, CoOp, MaPLe, GPT-4V, BLIP-2, MarineGPT); T5 (GPT-4o, Gemini, Claude, BLIP-2, LLaVA); H1 (CLIP, OpenCLIP, "for reference only"); H2 (CLIPScore, BLIP-2 score, PickScore, ImageReward, HPSv2, GPT-4V-based methods, with the open-source VQA models run on the same backbones in Table 2).
- **Ablations:** T3 two tables with a check-mark matrix of modules; T4 component and fusion-variant tables; H1 one objective ablation in the main text and "did not help" in the appendix; H2 in the appendix (language model, question template, answer format, decomposition); H3 weighting-versus-regulariser (Table 2).
- **Sensitivity:** T4 bottleneck count 4 to 64 (Fig. 4, p9); H1 timestep distribution (Fig. 3-4, p4-5); H3 noise level sweep.
- **Efficiency:** T4 MAdds of five fusion variants (Table V, p10); T3 a complexity subsection (p8); H1 runtime stated in the practical section (about 1000 s per ImageNet image, p4) with a speed-up discussion (p9); H2 "as few as 4 frames" (p11).
- **Confound checks:** H1 Table 2 (how in-distribution each test set is for the generator, p7); T4 text-dominance caveat for MOSI/MOSEI (p9); T5 histogram-equalisation harmonisation check (p9-10).

### 3.6 How superiority is argued, and how limitations are handled
- **Claims scale to the evidence.** T4 says "better or comparable" and names the metrics where it loses (p8-9: Acc-7; the NN setting). H1 and H2 say "outperforms" only against specific named baselines and add "for reference only" for non-comparable ones (H1 p5).
- **Fair-comparison device.** H2 Table 2 puts method and rivals on the same three backbones; T2 holds the architecture fixed and varies only the loss properties (Table I, p4).
- **Mechanism evidence.** H3 correlates the uncertainty measure with per-sample loss (Table 3, Fig. 3); H1 shows variance falls under paired testing (Fig. 2).
- **Limitations.** T2 has a named subsection (VIII-B, p13) listing single seed, two simple datasets, bijective relation between modalities. H3 has a numbered section (Section 6, p9) naming the dependence on Assumption 1 and on uncertainty estimation. H2 gives one sentence in the conclusion (p11). H1 puts cost and design caveats in the conclusion (p9) and lists failed techniques in Appendix G (p17). T1 gives one future-work sentence. T3 and T4 give none.
- **Negative or modest results** appear as "did not help" lists (H1 App. G), per-split losses (T4), or explicit caveats on a headline (H1 p8: no robustness gain on ImageNetV2 and ObjectNet).

### 3.7 Writing style (IEEE format)
- Abstract 138 to 231 words in all eight (CLCP 160, DashFusion 195, AquaticCLIP 206, Beyond the Hype 213; H2 is longest at about 290); single paragraph, problem then gap then method then evidence, last sentence gives the result.
- Introduction moves (T1, T4): application motivation (1 para); why existing methods fall short with citations (1-2 paras); the idea in plain words (1 para); contributions (bullets); roadmap paragraph ("Section II reviews ..."). T4's introduction is 16% of the text, T1's 22%, T2's only 4%.
- Related work is organised by the method's components (T4: alignment, fusion, contrastive learning; T3: VLMs, prompt learning, marine models; H3: fusion, uncertainty), 9-12% of the text, ending without a gap table. T2 keeps related work to the two features that matter and says an exhaustive review is out of scope (p2).
- Numbers: results text names the winner and the margin, then the explanation in one sentence (T4 p8). Captions are long and carry the interpretation (T3 Tables I-III; H2 Table 2).
- Section titles are descriptive, not topic labels (T1 "Conformal loss-controlling prediction and its theoretical analysis").

## 4. Synthesis

### 4.1 Typical TNNLS method paper, from this sample **[inference]**
Eleven to fifteen pages in the journal; 1-2 pages of introduction with Fig. 1; 0.7 pages related work; method 2-3 pages with one whole-method figure and 7-12 numbered equations; setup about 1 page; results 3-4 pages with 3-5 tables; limitations absent or short; references 1.2-2 pages (27-122 entries). Baselines are published methods plus, in vision-language papers, CLIP and one or two corporate models. Standard deviations and tests are rare.

### 4.2 Where our paper can be clearly stronger than the TNNLS exemplars
- Theory with an explicit assumption, a sign or correlation condition and a numerical check of that assumption (H3 is the template; none of the TNNLS five has this for fusion).
- Spread printed in every main table and paired tests on the headline contrasts (no exemplar does).
- Preregistration of the gating analysis, and an honest negative or conditional result reported next to the method (closest precedents: H1 Appendix G and T4's open admission of lost metrics).
- A hard-negative benchmark section with a per-category breakdown, as H2 Table 3 and T5 Table II do.

### 4.3 Fit warning **[inference from the project record, not from the exemplars]**
All eight exemplars propose something that wins on a main table (T1 proves a guarantee; T5 reports deficiencies of others, not of its own method). The current Paper 2 record is a preregistered NEGATIVE main result on one gate with "no new method" (research/progress.md HANDOFF 60; deep dive section 5). The blueprint below assumes the new reliability-aware fusion method exists with results on at least two backbones; if it does not, the T1 pattern (theorem plus verification of the guarantee, no baseline race) and the T5 pattern (instrument plus deficiency findings) are the only two in this set that fit, and the preregistered result must stay worded exactly as registered. No number for the method appears here: none exists in a runs/ directory that I read.

## 5. Blueprint for our paper (IEEEtran, two columns, Full Paper)

### 5.1 Section budget (pages including floats; text words are of running text without floats; about 1,000 words per text page)
| Section | 10 pages (no charge) | 13 pages | 15 pages (USD 1,000 over-length) | Content |
|---|---|---|---|---|
| Abstract, introduction, Fig. 1 | 1.1 | 1.2 | 1.4 | 150-200-word abstract, no abbreviations or symbols; 5 paragraphs; **3 numbered contributions each ending with a section pointer** (T3 p2); roadmap sentence; Fig. 1 on page 1 or 2 shows the failure (one-direction scores accept a hard negative) and the fused fix |
| Related work | 0.6 | 0.7 | 0.8 | three threads only: generative or likelihood scoring (H1, H2); contrastive and corporate verifiers; reliability-aware fusion (H3, TCPFMC if read); cite TNNLS papers where they support a sentence |
| Problem setting and notation | 0.5 | 0.6 | 0.7 | the two conditional directions of the masked diffusion model, the reliability signal, the verification task; one notation paragraph, no table |
| Method (reliability-aware fusion) | 1.2 | 1.5 | 1.8 | Fig. 2 whole-method schematic; 5-8 numbered equations; Algorithm 1 as a short box |
| Theory | 1.0 | 1.3 | 1.6 | two propositions with assumptions and a stated condition, interpretation paragraph, a Fig. 3 that draws the bound (H3 Fig. 2); proofs in Appendix A of the supplement or end of the paper |
| Experimental setup | 0.9 | 1.1 | 1.3 | datasets and hard-negative benchmarks, baseline families (Table I as the baseline taxonomy, H2 p6), metrics, protocol, seeds, hardware |
| Results | 2.4 | 3.2 | 3.6 | main comparison (Table II) 0.8; hard-negative breakdown (Table III) 0.5; ablation (Table IV) 0.4; sensitivity or robustness figure 0.5; efficiency (Table V) 0.3; preregistered gating analysis 0.8 at 15 pages; below that 0.4 |
| Discussion, limitations, conclusion | 0.6 | 0.7 | 0.8 | named Limitations subsection (H3 p9, T2 p13), what did not help (H1 App. G pattern) |
| References | 1.1 | 1.4 | 1.5 | 45-65 verified entries; no reference padding (IEEE ethics rule in deep dive 1.2) |
| Total | 9.4-10 | 11.7-13 | 13.5-15 | |
Declarations (AI use; deep dive 1.7 states the IEEE placement conflict) and Acknowledgements must be settled by Shlok; they cost about 0.1 page.

### 5.2 Required figures (5) and tables (5) in the main text
1. Fig. 1: teaser with the failure and the fused fix (T5 Fig. 1 p1; H1 Fig. 1 p2; H2 Fig. 1 p2).
2. Fig. 2: method schematic with the equation symbols on the nodes (H3 style; Moser Fig. 8 in LENS-CRAFT).
3. Fig. 3: the bound as an equation-figure plus the hypothesis-space picture (H3 Fig. 2 p3).
4. Fig. 4: the result the theory predicts: gate benefit against token-reliability correlation, with intervals (H3 Fig. 3 p7; H1 Fig. 6 p8).
5. Fig. 5: sensitivity to the one hyper-parameter (T4 Fig. 4 p9) or robustness under corruption severity.
Tables: I baseline taxonomy with the corporate models marked "reference only" where training data differ; II main comparison on the hard-negative benchmarks with mean and spread; III category breakdown of the benchmark (H2 Table 3); IV ablation with a check-mark matrix of modules (T3 Table I); V efficiency (forward passes per verification, latency, memory; T4 Table V, H1 p4). Optional VI: preregistered analysis table inside the results (family, estimate, interval, preregistered decision).

### 5.3 Baseline and ablation set
- **Baselines, grouped as in H2 p6:** (1) contrastive encoders: CLIP, OpenCLIP, SigLIP; (2) captioning-or-VQA likelihood: BLIP-2 ITM/score, VQAScore with open models; (3) the diffusion model's own single-direction scores (text-given-image, image-given-text) and their plain product; (4) the existing reliability gate and robust combiners from the project record; (5) a trusted or evidential fusion baseline of the QMF or TCPFMC type, ported to our two-score setting. State for each corporate model its training data and why it is "reference only" (H1 p5).
- **Ablations (one row per module, check-mark matrix):** each direction alone; fusion without reliability; reliability from a different estimator; hard gate versus soft weighting; with and without the correlation correction suggested by Proposition 2 (our own theory item).
- **Sensitivity:** gate threshold or weighting temperature (T4 Fig. 4 style), number of masking draws.
- **Variability:** at least 5 seeds or bootstrap intervals on every cell (H3 Fig. 3 uses 10), paired difference intervals on headline contrasts.

### 5.4 Efficiency table (required)
Columns: model calls per verification, wall-clock on the 12 GB laptop GPU, peak memory, parameters touched. Rows: CLIP/SigLIP, BLIP-2, VQAScore backbone, single-direction diffusion score, our fusion at the chosen number of draws. H1 shows that an honest statement of a 1000-second worst case does not block acceptance (p4); T4 puts cost in the ablation family (Table V).

### 5.5 Limitations paragraph (required)
List: single or few backbones; token-correlation assumption of Proposition 2; benchmark scope (hard negatives are template-generated); corporate models used as published checkpoints; dependence on the reliability estimate (H3 p9 states this for QMF); preregistered null on the gate stated with its interval. Put under a named heading (H3 Section 6, T2 VIII-B).

## 6. Fifteen rules, each tied to an exemplar page

1. **State exactly three contributions as a numbered list and end each with the section that proves it.** AquaticCLIP p2 (section ranges), VQAScore p4, QMF p2.
2. **Open the experiments with numbered questions and tie each to a proposition or assumption.** QMF p6 (Q1 to Theorem 1, Q2 to Theorem 2, Q3 to Assumption 1); Diffusion Classifier p6 (six questions).
3. **Put a first-page figure that shows the failure and the fix.** Beyond the Hype Fig. 1 p1; Diffusion Classifier Fig. 1 p2 (objective on the figure); QMF Fig. 1 p2 (accuracy gap).
4. **Keep the abstract at 150-210 words, one paragraph, result in the last sentence, no abbreviations.** CLCP p1 (about 160 words), DashFusion p1 (about 195).
5. **Give theory its own section of 1-1.5 pages: notation, roadmap sentence, theorem statements, a remark that spells out the condition, proofs in the appendix.** QMF p3-5 and p14; CLCP p3-5 when proofs are short.
6. **Draw the theorem.** An equation-figure that labels the terms of the bound beside a hypothesis-space picture. QMF Fig. 2 p3.
7. **Check every theoretical assumption with a number.** QMF Table 3 and Fig. 3 (Pearson r between weights and loss, 10 seeds, p7 and p9); CLCP Figs. 1, 3, 6 (frequency of loss above the level, p6-9).
8. **Group baselines by method family and add a same-backbone comparison.** VQAScore baseline taxonomy p6, Table 2 p8; Global Workspace Table I p4 (all models share one architecture).
9. **Mark non-comparable corporate models as reference only and say why.** Diffusion Classifier p5 (CLIP rows); AquaticCLIP Table III p7 puts GPT-4V and BLIP-2 in the main table beside CLIP and CoOp.
10. **Make ablations a check-mark matrix with one row per module and one column per dataset.** AquaticCLIP Tables I-II p7; DashFusion Table IV p10.
11. **Include one sensitivity figure for the hyper-parameter you ask readers to trust.** DashFusion Fig. 4 p9; Diffusion Classifier Figs. 3-4 p4-5.
12. **Print a cost table or cost paragraph with a number.** DashFusion Table V (MAdds) p10; Diffusion Classifier p4 (about 1000 s per ImageNet image); AquaticCLIP IV-H p8.
13. **Print variability and, where the claim is a difference, an interval.** QMF Fig. 3 p7 (10 seeds, worst case); Diffusion Classifier Fig. 6 p8 (Clopper-Pearson); do not copy Global Workspace p13 (single seed, admitted) or AquaticCLIP Table III (no spread).
14. **Break the hard-negative benchmark down by category and run a confound check.** VQAScore Table 3 p8 (skills); Beyond the Hype Table II p6 (question types); Diffusion Classifier Table 2 p7 (how in-distribution each test set is).
15. **Give limitations a named heading and list what did not help.** QMF Section 6 p9; Global Workspace VIII-B p13; Diffusion Classifier Appendix G p17; and concede lost metrics in the results text as DashFusion p8-9 does.

## 7. Notes on our preregistered analysis **[inference]**
- Best structural home: a results subsection placed after the main comparison, framed as the empirical test of Proposition 2, the way QMF Table 3 tests Assumption 1 and CLCP Figs. 1, 3, 6 test Theorem 1. A conditional or null result is then an answer to "under what condition does gating help" (QMF Q2), not a missing win.
- Report the registered decision rule, the interval, and the decision in one table row per family; keep the registered wording.
- Exemplars show no preregistration of any kind. Reviewers will have no precedent; cite the registration record in the text and state it in the limitations or protocol paragraph, but check double-anonymous rules for links first (deep dive 1.4, unresolved).

## 8. Concerns (for the orchestrator)
1. The brief says "a new method"; the project record says "no new fusion rule" and a preregistered negative result. Section 4.3 and the blueprint branch on which is true.
2. Seven exemplars are arXiv versions; layouts and reference counts of the journal versions differ (T2, T3). T4's TNNLS status rests on an arXiv comment only.
3. Closest TNNLS fusion methods (TCPFMC and others, Section 1.1) are paywalled; the blueprint's fusion-baseline row for a trusted or evidential method should be informed by TCPFMC before it is fixed.
4. Flow-CLIP (arXiv 2610.21937, compositional image-text matching via image-conditioned residual scoring) surfaced in a web search; I did not read it. It may be concurrent work for the novelty audit.
5. Appendices and supplements of the exemplars were not read closely; claims about them are from headings and captions only.
