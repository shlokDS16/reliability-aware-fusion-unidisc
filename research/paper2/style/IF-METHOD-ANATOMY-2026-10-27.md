```yaml
agent: venue-intel
date: 2026-10-27
brief: Learn the anatomy of recent Information Fusion RESEARCH (method) articles so the writer can model a unified multimodal masked discrete diffusion paper on them; extends STYLE-GUIDE-2026-10-27.md (closes its Q5 gap)
sources_examined:
  - arXiv:2410.13597 (TransDLM; IF 127, 103907, doi:10.1016/j.inffus.2025.103907)
  - arXiv:2508.05264 (SGDFuse; IF 133, 104290, doi:10.1016/j.inffus.2026.104290)
  - arXiv:2602.00639 (Diff-PC; IF 117, 102869, doi:10.1016/j.inffus.2024.102869)
  - arXiv:2405.10121 (VIKDF; IF 118, 102985, doi:10.1016/j.inffus.2025.102985)
  - arXiv:2411.03034 (HumanVLM; IF 123, 103271, doi:10.1016/j.inffus.2025.103271)
  - arXiv:2508.16300 (MM-ORIENT; IF 126, 103628, doi:10.1016/j.inffus.2025.103628) headings, figure/table captions and reference count only
  - arXiv:2505.15809 (MMaDA) html table list, used only for the benchmark/baseline list in section 6
  - Crossref API (issn 1566-2535, from 2025-01-01) for DOIs and candidate listing; arXiv advanced search (journal_ref / comments fields) for arXiv copies
coverage: >
  For each paper the arXiv PDF was converted with markitdown and read selectively: front matter, contribution list, section headings,
  all figure/table captions, main-results table head, ablation section, efficiency statements, limitations/conclusion, reference count.
  Methods sections and proofs were not read. Two-column PDFs (Diff-PC, VIKDF) extract with interleaved columns, so section numbering for
  a few subsections and table cell contents are approximate. The arXiv versions are author preprints and may differ from the published
  versions; page counts below are for the arXiv PDFs in whatever template the authors used, not for the Information Fusion print layout.
  NOT covered: any ScienceDirect page (not fetched), published page counts, any paper on masked discrete diffusion or any-to-any
  text-image-audio generation (none found in Information Fusion; see claims). Candidate pool: about 130 Crossref hits, 16+6 arXiv hits
  with an Information Fusion note in the comments/journal_ref fields; most authors do not fill those fields, so the pool is incomplete.
claims:
  - statement: Every one of the five sampled Information Fusion method papers is open on arXiv, but none is on masked discrete diffusion or on joint text-image-audio generation; the nearest are one discrete diffusion language model (TransDLM), one image diffusion (Diff-PC), one diffusion-based fusion (SGDFuse).
    status: supported
    evidence: arXiv search by journal_ref/comments, Crossref listing; no matching title found
    level: E2
    confidence: 0.7
  - statement: Four of five analysed papers (and MM-ORIENT) list more than 50 references in the arXiv version (about 72, 45-48, 107, 51, 87, 67), so the 50-reference limit in the Guide for Authors was either not enforced for these accepted papers or is recent.
    status: mixed
    evidence: reference sections of the arXiv PDFs; Guide for Authors limit (STYLE-GUIDE 1.1)
    level: E2
    confidence: 0.7
  - statement: Reporting of statistical evidence in the sample is thin; only 2 of 5 use seeds plus a test (VIKDF one-sample t-test over 5 seeds; TransDLM paired t-test with Benjamini-Hochberg correction over 25 comparisons, in an appendix), none prints a +/- in the main table.
    status: supported
    evidence: VIKDF Sec. 4.x/5.1 text; TransDLM Appendix C text and Fig. 6; table heads of the others
    level: E2
    confidence: 0.8
  - statement: Explicit fusion framing in the title is present in 2 of 5 (SGDFuse; MM-ORIENT) ; in the abstract or keywords in 4 of 5; HumanVLM has none and was still accepted, so scope acceptance is not strictly tied to fusion vocabulary, but our scope risk (STYLE-GUIDE 5) is not reduced by this.
    status: supported
    evidence: titles/abstracts/keywords of the arXiv versions
    level: E2
    confidence: 0.75
competing_explanations:
  - The sample is small and biased towards papers whose authors posted to arXiv and noted the journal; high-effort groups may differ from the median Information Fusion paper.
unknowns:
  - Published page counts and whether the 35-page / 50-reference limits are measured as in the guide; check the live Guide once more and ask the editorial office if in doubt.
  - Whether Information Fusion has accepted any masked-discrete-diffusion or any-to-any generation paper (none found).
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Anatomy of recent Information Fusion method papers (2026-10-27)

Evidence: structural facts are E2 (paper text read, arXiv version). Recommendations in sections 4 to 6 are inference unless marked.

## 1) Sample

| # | Paper (DOI; arXiv) | Type | arXiv pages / template | Refs | Figs / Tables |
|---|---|---|---|---|---|
| A | TransDLM, text-guided molecular optimisation with a diffusion language model (10.1016/j.inffus.2025.103907; 2410.13597) | discrete-ish diffusion LM, text+molecule | 12 (authors' ACM-style conversion) | about 72 | 6 / 5 |
| B | SGDFuse, SAM-guided diffusion for infrared+visible fusion (10.1016/j.inffus.2026.104290; 2508.05264) | conditional diffusion, image fusion | 48 (single-column preprint) | about 45-48 | 21 / 9 |
| C | Diff-PC, 3D-aware controllable diffusion for portrait customisation (10.1016/j.inffus.2024.102869; 2602.00639) | text-to-image diffusion, face-conditioned | 17 (two-column, "Page n of 17") | about 107 | 21 / 8 |
| D | VIKDF, distilling implicit multimodal knowledge into LLMs for dialogue (10.1016/j.inffus.2025.102985; 2405.10121) | multimodal LLM, text generation | 14 (two-column) | 51 | 5 / 4 |
| E | HumanVLM, human-scene vision-language foundation model (10.1016/j.inffus.2025.103271; 2411.03034) | dataset + VLM | 34 (single-column, "submitted to Arxiv") | 87 | 11 / 8 |
| F | MM-ORIENT, multimodal-multitask meme analysis (10.1016/j.inffus.2025.103628; 2508.16300) | fusion classifier, headings only | 22 | about 67 | 10 / 9 |

Note: the arXiv posting of C is dated January 2026, after publication in 2025; the arXiv text may be the accepted manuscript.

## 2) Section order and names

| Paper | Section skeleton (arXiv version) |
|---|---|
| A | 1 Introduction; 2 Related work (molecular optimisation; language generation with diffusion); 3 Methodology (overall framework; description generator; tokenizer; text-guided optimisation; training); **4 Theoretical analysis** (error propagation, suppression mechanism, comparison); 5 Experiments (dataset; metrics; baselines; overall performance and visualisation; ablation; case study); **6 Limitations and future work**; 7 Conclusion; appendices (hyper-parameters, statistical testing, case-study details) |
| B | 1 Introduction; 2 Related work (3 subsections, one per ingredient); 3 Methodology (motivation; network architecture; training objectives; forward/reverse diffusion); 4 Experiments (settings: datasets, metrics, training; comparisons on 4 datasets; efficiency and sampling steps; ablation, 7 subsections; robustness; other semantic priors; intensity profiles; medical generalisation; downstream detection and segmentation); 5 Discussion; 6 Conclusion |
| C | 1 Introduction; 2 Related work (4 subsections); 3 Preliminary; 4 Method (overview; ID-Encoder; ID-Ctrl and ID-Injector; training and inference; **dataset construction**); 5 Experiments (implementation; qualitative; quantitative; user study; further analysis; ablation); 6 Conclusion; Appendix (dataset statistics, **B.1 Limitations with a failure-case figure**, ethics) |
| D | 1 Introduction; 2 Related work (2 subsections); 3 Methodology (overview; distillation stage with 3 objectives; integration stage; zero-resource detail); 4 Experiments (datasets; implementation; baselines; metrics); 5 Results (automatic; human; ablation; case study); 6 Conclusion and future work. No limitations section |
| E | 1 Introduction; 2 Related work (3); 3 Constructing the data; 4 Data-quality comparison; 5 Model (two-stage learning); 6 Experiments (general domain; human-scene tasks; ablation); 7 Conclusions. No limitations section |
| F | 1 Introduction (1.1 existing approaches and challenges; 1.2 proposed solution; 1.3 key contributions); 2 Related work; 3 Problem definition; 4 Methodology; 5 Experimental evaluation (datasets; baselines; results per dataset; ablation by component with bar charts; qualitative); 6 Conclusion |

Pattern: Introduction, Related work, (Preliminary), Method, Experiments (with the ablation inside it), Discussion/Limitations (when present), Conclusion. Related work is always before Method. Experiments is the largest block.

Approximate word shares of the body (A, B, D measured by line ranges, D rough because of column interleaving): introduction 8-14%; related work 4-17%; method 24-35%; experiments, results and ablation 40-48%; discussion/limitations 3%; conclusion 2-3%.

## 3) Per-paper observations

**Contributions list.** A: three "advantages" bullets (what the output does, error propagation, benchmark result). B: three bullets (framework, two-stage instance, guidance system plus loss). C: four bullets (framework, module, dataset, extensive experiments). D: three bullets (framework, two techniques, evaluation on two datasets). E: three numbered items (dataset, model, open resources). F: four numbered items. Typical form: 3-4 bullets, each beginning with "We propose/design/collect/conduct" and naming the module; bullets are placed at the end of the introduction. Only B and E tie bullets to sections; none lists a research question or hypothesis.

**Main results table.**
- A: Tables 1 (structure similarity: BLEU, exact match, Levenshtein, three fingerprint similarities, FCD, validity) and 2 (property metrics); 5 baselines; one dataset, one fixed random split; caption states "bold indicates the best"; direction arrows in the header; no +/-.
- B: Table 1 and Table 2 (two datasets per table); 13 baselines; 7 metrics (EN, SD, SF, MI, SCD, VIF, Qabf); best in red and second best in blue; no +/-, no test.
- C: Table 2 (main) with grouped column heads ID fidelity, face control, T2I consistency, image quality, plus inference time on one A100; Table 3 repeats on two further test sets; 4 baselines; percentages; best in bold; no +/-. A user study with 63 participants (bar chart) supplements metrics.
- D: Table 1 with two datasets side by side, a marker for zero-resource baselines, "second-best underlined", an asterisk for p<0.05; tuned-parameter count column (159M). Table 2 human evaluation.
- E: Table 4 compares with general VLMs on MME perception and cognition, MMBench (English and Chinese), CCBench-dev, VQAv2 and POPE; more tables for domain tasks scored with an LLM judge (GPT-4o scores).
- F: one table per dataset (three datasets), ablation tables per component.

**Statistics.** D: five seeds, one-sample t-test of VIKDF against the best baseline for each metric. A: five seeds, paired t-test with Benjamini-Hochberg correction over 25 comparisons (5 metrics x 5 baselines), reported as a bar chart of -log10 p in an appendix (24 of 25 below 0.05). B, C, E, F: no seeds or tests found. Human evaluations in C and D report mean scores.

**Ablation design.** A: three single-factor ablations (text input type, initialisation from source vs pure noise, backbone encoder) re-using the main-table layout, discussed in prose with a causal explanation. B: eight kinds, as tables on two datasets plus line plots (number of modules, diffusion steps), a training-convergence figure and a denoising-process visualisation with and without the semantic prior. C: component-wise (ID-Encoder, ID-Ctrl, ID-Injector, loss, dataset) as image grids plus one table. D: remove each module, run with a different LLM backbone as a separate table. E: data-ablation (with and without the high-quality caption set) on two backbones. Common: remove-one-component, backbone swap, hyper-parameter sweep; no interaction (factorial) ablations.

**Efficiency and complexity.** B has a full table (parameters in M, FLOPs in G, latency in ms, with the number of sampling steps stated) and two plots of quality against steps; its Discussion argues that the extra cost buys semantic fidelity. A states 1.02 s per molecule on a named GPU and that step-skipping cut 2000 steps to 200 with little loss. C reports one inference-time column (8 steps, A100). D reports tuned-parameter count and the 4 x RTX 4090 setup. E and F report training setup only.

**Figures by type.**
- Framework or architecture diagram: all six (1-2 each; C has an extra module diagram and an inference pipeline).
- Motivation or teaser figure on page 1-2 comparing prior behaviour with the proposed one: A (Fig. 1), B (Figs 1-3 including a with/without-prior visual ablation), C (Figs 1-2), D (Fig. 1), E (Fig. 1 radar-style comparison).
- Qualitative grid, columns = methods, rows = inputs: A (Fig. 4, molecules), B (Figs 6-9, eight grids), C (Figs 6-7), D (Fig. 5 case study, text), E (Figs 9-10).
- Ablation plot or grid: B (Figs 10-13), C (Figs 12-14), F (Figs 5-9 bar charts).
- Efficiency/step plot: B only.
- Statistics figure: A (Fig. 6, appendix). User-study bar chart: C.
- Failure cases: C only (Fig. 20-21, appendix). Attention/heat-map, t-SNE: none of the five. 
- Dataset statistics histograms: C (Figs 15-19, appendix), E.

**Limitations.** A: own section, three paragraphs (pipeline complexity, iterative sampling cost with the mitigation actually made, scope of properties and data). B: inside "Discussion", framed as admitted overhead plus three future directions. C: appendix subsection with concrete failure modes illustrated by figures (hands, occlusion, extreme expressions) and an ethics note. D and E: none apart from future work. F: not read. Concrete, scoped limitation text appears only in A and C.

**Fusion framing.** Title: B ("Image Fusion"), F ("multimodal", "cross-modal") only. Keywords include fusion: B, C ("Feature fusion"), D ("Multimodal fusion"). Abstract uses fusion operationally: A ("fusing ... textual semantics with specialized molecular representations"), C (an encoder "that fuses local and global facial features"), D (a "Bidirectional Variational Information Fusion" module). E: no use of fusion language at all.

**Data and code statement.** B: "available on request" (does not meet the journal's Option C expectation, see STYLE-GUIDE 1.5). D: code link in abstract. E: resources promised ("will release"). A and C: not checked. Open code is therefore not universal even among accepted papers.

## 4) Synthesis: what a method paper in this journal looks like

1. 12-17 pages in two-column elsarticle (about 13-15k words with figures) is typical for work that is accepted; the 35-page ceiling is rarely approached. The single-column preprint form inflates counts (B: 48 pages).
2. Contribution is a named framework with 2-3 named modules and a loss or schedule, plus a dataset or benchmark in 2 of 5.
3. Page 1-2 carries a motivation figure that shows the failure of prior approaches; page 3-4 the framework figure.
4. Evidence is breadth: several datasets (B: 4 plus a medical set; C: 3 test sets), 4-13 baselines, one or two downstream tasks. Depth (seeds, intervals) is rare; a paper that reports intervals and tests would be above the median.
5. A theory or analysis section appears in A (error propagation); an "analysis" subsection of mechanisms is not required.
6. Limitation text is usually short; place it in a dedicated subsection to meet the style guide's rule 17.

## 5) Recommended skeleton for our paper

Target: 18-22 pages in the two-column elsarticle layout (well inside 10-35), 6.5-7k words of body text, at most 50 references. Page shares are fractions of the 20-page target, figures and tables included.

| Section | Share | Pages | Content |
|---|---|---|---|
| Title, abstract, highlights, keywords | - | 0.75 | abstract at most 250 words, 3-5 highlights |
| 1 Introduction | 9% | 1.8 | problem, why fusion (shared token sequence as fusion operator), gap, motivation Figure 1, 3-4 contribution bullets tied to sections, roadmap |
| 2 Related work | 7% | 1.4 | organise by axis (tokenisation, masking schedule, cross-modal coupling), end with a comparison table versus 4-6 closest works (Table 1) |
| 3 Preliminaries and problem formulation | 4% | 0.8 | masked discrete diffusion, notation, what "fusion" means here (observed subset of modalities, missing modality) |
| 4 Method | 22% | 4.4 | architecture figure (Fig. 2), objective, sampler/unmasking order (Algorithm 1), complexity paragraph; one theory or analysis subsection only if a derivation exists (as in paper A) |
| 5 Experimental setup | 7% | 1.4 | benchmarks, baselines, metrics with direction, seeds and intervals, hardware, budget parity (matched network calls) |
| 6 Results | 22% | 4.4 | main table (Table 2), qualitative grid (Fig. 3), conditioning-on-subsets / missing-modality table and figure, cross-modal consistency |
| 7 Analysis | 12% | 2.4 | ablation (Table 3 and Fig. 6), efficiency table (Table 4: parameters, steps, latency, VRAM), robustness and failure cases |
| 8 Discussion and limitations | 5% | 1.0 | observation, hypothesised cause marked as hypothesis, falsifier; limitations paragraph with scope |
| 9 Conclusion | 2% | 0.4 | 3-5 sentences, same numbers as the paper |
| Declarations, appendix | - | 0.65 | CRediT, AI declaration, data availability (repository and DOI), hyper-parameters, extra samples |
| References | - | 1.5 | at most 50 entries |

Reference budget (inference): 6 surveys or foundations, 8-10 masked/discrete diffusion and unified-model works, 8-10 baselines and benchmarks used in tables, 6-8 tokenisers and encoders (image, audio, text), 4-6 evaluation tools, 3-4 fusion-literature anchors (to meet scope), 2-3 datasets. This leaves 3-5 spare.

## 6) Figure and table plan

Figures (8 recommended; all real model outputs or real measured numbers, each from a committed script):
1. Motivation (page 1-2): how prior unified models fuse or fail to fuse modalities, drawn as a schematic with one measured example (a before/after pair with its metric printed).
2. Framework: three token streams (text, image, audio), masking, shared denoiser, unmasking order; TikZ or matplotlib.
3. Qualitative grid: columns = methods (ours, two or three baselines), rows = prompts, measured score printed under each cell; one panel each for text-to-image, image-to-text, audio where applicable.
4. Unmasking strip: the same prompt at steps 0, 25, 50, 75, 100% for each modality (shows the commitment process).
5. Fusion benefit plot: quality of modality X as a function of which other modalities are observed (any-subset conditioning), with intervals.
6. Ablation line/bar plot with intervals (components and sampler variants).
7. Efficiency/step trade-off: quality vs number of sampling steps and latency on the 12 GB GPU (the only sampled paper with this is B; reviewers of a diffusion paper will look for it).
8. Failure cases and robustness: degraded or missing modality curves plus 4-6 failure samples (as in C).
Optional 9: user study bar chart, only if a human evaluation is run.
Do not include: t-SNE, attention heat-maps, dataset histograms in the body (move to appendix if useful).

Tables (4 recommended):
1. Related-work comparison (4-6 closest works by modalities, tokenisers, masking, coupling, evaluation).
2. Main results: methods in rows grouped by modality-task, arrow in each metric header, best bold, mean +/- standard deviation or 95% interval over stated seeds, footnote naming the interval type; no vertical rules or shading (guide).
3. Ablation (one table; component rows, same metrics as Table 2).
4. Efficiency: parameters, sampling steps, latency per sample, peak VRAM, with the sampler setting stated as in B's Table 3.
Optional 5: hyper-parameters and datasets (move to appendix to save space). Add a significance paragraph or appendix figure like A's (paired test, multiplicity correction) because the sample shows this is rare and valued.

## 7) Baselines and metrics reviewers will expect

Sources: MMaDA's benchmark and baseline lists were read in its HTML (E2 for the list). The other model names come from the project's own notes in `research/paper2/` (E1). Metric definitions and run costs here are my own general knowledge and were not re-verified in this run (E0 for cost columns). "12 GB" means inference or evaluation fits one RTX 5070 Ti Laptop GPU with 12 GB; models above about 5B parameters in bf16 do not fit without quantisation, which changes results.

| Metric / benchmark | Used for | Seen in | 12 GB? |
|---|---|---|---|
| CLIPScore | text-image alignment | MMaDA (CLIP Score), project notes | yes |
| ImageReward | preference proxy | MMaDA | yes |
| GenEval (object, count, colour, position sub-scores; needs an object detector) | compositional T2I | MMaDA | yes for a 1.4B model; a subset if time is limited |
| DPG-Bench | dense-prompt T2I | common in unified-model papers (not verified here) | yes, needs an auxiliary VQA scorer |
| FID on a COCO subset | image distribution | common (not in the five sampled IF papers except C's reference-versus-generated FID) | partial: a few thousand images only, bias at small N must be stated; report relatively, not against published 30k-image FIDs |
| POPE, MME (perception and cognition), GQA, VQAv2, MMBench, SEED | understanding | MMaDA table; E uses MME, MMBench, VQAv2, POPE | yes for models that fit; POPE and MME are small and cheap |
| MMMU | multimodal reasoning | MMaDA | partial: needs a model strong enough to be above chance; run only on models that fit |
| WER with a fixed ASR (Whisper large-v3 is in the local cache) | text-to-speech intelligibility | Apple tri-modal MDM note | yes |
| FAD | audio quality | Apple tri-modal MDM note | yes, small embedding network |
| Perplexity / generative perplexity | text quality | masked-LM papers (E0) | yes |
| Cross-modal consistency (own metric, for example discordant-noun link from EXP-003) | fusion-specific | EXP-003 | yes |
| Missing-modality / corruption robustness | fusion-specific | none in the five | yes, cheap |
| Seeds, intervals, paired test with multiplicity correction | statistical standard | A and D | yes |

Baselines (each must be run under a matched network-call budget, or reported as copied numbers with a non-comparability note):
- Masked-diffusion unified models: UniDisc (1.4B, already run locally), MMaDA (8B; needs quantisation), Lumina-DiMOO, Omni-Diffusion, Apple's tri-modal masked diffusion model (320M scale per project notes), LaViDa/LaViDa-O. Check weight availability per model first.
- Autoregressive and hybrid unified models named in MMaDA's tables: Chameleon, Show-o, Janus, Emu, SEED-X, DreamLLM.
- Single-modality references: SDXL, SD 1.5/2.1, LlamaGen for T2I; LLaVA-1.5-7B for understanding (fits in 12 GB at 4-bit); LLaDA-8B for text (quantised).
Using copied numbers for 7-8B baselines and re-running only models that fit is acceptable if each cell is marked "copied" or "re-run".

## 8) Rules for the writer, added to STYLE-GUIDE section 4

31. Place a motivation figure on page 1-2 and the framework figure on page 3-4 (all six sampled papers do).
32. Put the ablation inside the Experiments/Analysis section and give each ablation a one-sentence causal reading marked as hypothesis, then the falsifier.
33. Print the sampling-step count next to every latency or FLOPs number, and give peak VRAM (the sampled diffusion papers do this only partly).
34. Add one limitations subsection with concrete failure cases shown in a figure (only A and C do; reviewers of a hostile review will look for it).
35. Report seeds and a paired test with multiplicity correction in the main text or appendix; this is above the sample median and costs one paragraph.
36. Do not use "available on request" in the data statement (B does); use a repository and DOI.
37. Keep references at 50 even though the sample exceeds it; confirm with the editorial office or the live Guide before submission, because the guide ties the limit to desk rejection.

## 9) Open questions

Q-a. Reference ceiling: four of five accepted sample papers exceed 50 references in their arXiv versions. Keep 50 as binding (safer) or ask the editorial office? Recommendation: keep 50.
Q-b. Scope: no masked-diffusion or any-to-any generation paper was found in Information Fusion. This keeps the desk-rejection scope risk from STYLE-GUIDE 5 open; an inquiry to the editor (presubmission enquiry) before investing in the final polish may be worthwhile. It is the user's decision.
Q-c. Which of the unified masked-diffusion baselines have usable weights (UniDisc yes; MMaDA 8B needs quantisation; others unchecked).
