---
agent: venue-intel
date: 2026-10-29
brief: Deep venue analysis of IEEE TNNLS for Paper 2 and a possible follow-up model paper; official sources only; 10-15 recent TNNLS papers; fit of paper2/main.tex
sources_examined:
  - https://cis.ieee.org/publications/t-neural-networks-and-learning-systems (journal page) and /tnnls (Information for Authors), /tnnls-guidelines-for-paper-submission, /tnnls-arxiv, /tnnls-information-on-special-issues, /tnnls-featured-papers
  - https://ieeexplore.ieee.org/xpl/aboutJournal.jsp?punumber=5962385 (Xplore "About Journal": aims, peer review, metrics, EiC)
  - https://journals.ieeeauthorcenter.ieee.org/ (submission and peer review policies; structure your article; prepare supplementary materials; IEEE article templates)
  - https://template-selector.ieee.org/ ; https://ctan.org/pkg/ieeetran
  - https://cis.ieee.org/awards (Outstanding Paper Award listing)
  - Xplore document pages (public abstract/metadata) for 15 TNNLS papers, DOIs in section 3
coverage: >
  Read in full: the TNNLS Information for Authors page; the Xplore About Journal page; the IEEE Author Center pages on submission/peer-review/AI policy,
  supplementary materials and article structure. Abstract, page range and reference count only (paywalled, full text NOT read): 13 of the 15 papers.
  Partly read (open access, structure counted from the HTML page, body text not read closely): 2 papers. NOT covered: the IEEE Author Portal
  (ieee.atyponrex.com/journal/tnnls) which sits behind a Cloudflare bot check (not bypassed) and probably holds the anonymisation and checklist
  details; the IEEE PSPB Operations Manual PDF (cited by the journal page, not opened); any official review-time figure (none found);
  reviewer-form text (not public).
claims:
  - statement: TNNLS caps a Full Paper at 10 pages without charge, 15 pages with a mandatory USD 200/page over-length charge; supplementary material is excluded from the count
    status: supported
    evidence: https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls section H (accessed 2026-10-29)
    level: E1
    confidence: 0.95
  - statement: The journal's own pages disagree on anonymity (CIS page: double-anonymous; Xplore page: single and/or double, reviewers know authors)
    status: supported
    evidence: CIS Information for Authors section A vs Xplore About Journal "Peer Review" (both 2026-10-29)
    level: E1
    confidence: 0.9
  - statement: IEEE's AI-disclosure rule places the disclosure in the Acknowledgements section, which conflicts with a Declaration-only practice
    status: supported
    evidence: CIS Information for Authors section K; IEEE Author Center "Guidelines for AI-Generated Content" (2026-10-29)
    level: E1
    confidence: 0.95
  - statement: No page of the journal states a policy on negative results, preregistration or reproducibility studies
    status: supported
    evidence: keyword read of every CIS TNNLS page listed above; the Xplore aims text names only "original review articles and surveys" as acceptable without new data
    level: E1
    confidence: 0.8
  - statement: In 2024-2026 TNNLS, an Xplore search finds no paper on masked/discrete diffusion language models or unified multimodal discrete diffusion; one discrete-diffusion image-captioning paper (MALFM-Captioner, 2026) exists
    status: mixed
    evidence: in-page Xplore search API, queries "discrete diffusion", "masked AND diffusion" (index coverage unknown; search is a lead, not a census)
    level: E1
    confidence: 0.6
competing_explanations:
  - "Few diffusion-language papers in TNNLS may reflect the search index (title/abstract/keyword only) rather than the journal's scope."
unknowns:
  - Time to first decision and acceptance rate (not on any official page read)
  - Exact anonymisation rules and whether TNNLS is double- or single-anonymous in practice (portal not readable without a browser check/login)
  - Whether supplementary material has a size or content limit for TNNLS (IEEE general page gives formats only)
  - TNNLS code/data policy (none found; IEEE general pages ask for a README for datasets)
  - Reviewer form
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
---

# TNNLS deep dive for Paper 2 (2026-10-29)

Evidence tags: **[OFFICIAL]** text read on the page named; **[ABSTRACT]** public Xplore abstract and metadata only; **[DERIVED]** my arithmetic or inference from official
text, stated as such. Access date for every URL below: **2026-10-29**. Dates shown by Xplore as "dateOfInsertion" are not submission dates and are not used.

## 1. Official facts about TNNLS

### 1.1 Aims and scope [OFFICIAL]
- Source: https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls ; https://ieeexplore.ieee.org/xpl/aboutJournal.jsp?punumber=5962385
- Scope: "technical articles that deal with the theory, design, and applications of neural networks and related learning systems". Authors are encouraged to submit
  manuscripts that "disclose significant technical achievements, indicate exploratory developments, or present significant application".
- Xplore "About Journal" adds: the journal "considers original works that enhance the existing body of knowledge. Original review articles and surveys are acceptable, even if new
  data/concepts are not presented." Expanded conference versions may be submitted. Results must not be submitted or published elsewhere. Articles are screened for plagiarism.
- Sponsor: IEEE Computational Intelligence Society. EiC (Xplore page): Yongduan Song, Chongqing University. Frequency 12 issues/year.
- Metrics shown by Xplore (Clarivate 2025 JCR released June 2026; Scopus 2025): Impact Factor **9.7**, Eigenfactor 0.11445, Article Influence 3.1, CiteScore **23.7**.

### 1.2 Article types and limits [OFFICIAL, section A and H of the Information for Authors]
| Type | Definition (quoted idea) | Free pages | Over-length | Hard maximum |
|---|---|---|---|---|
| Full Paper | "novel contributions of archival nature in developing theories and/or innovative applications"; "should not be of incremental nature, but must present a well-founded and conclusive treatment of a problem" | 10 | mandatory USD 200 per printed page over 10 | 15 pages |
| Survey | "well organized survey of literature on topics of current interest" | 15 | USD 200/page | 21 pages |
| Brief Paper | "extension of previous results or algorithms, innovative applications of a known approach..., brief theoretical results"; "conclusive and useful" | 6 | USD 200/page | 9 pages |
| Comments Paper / Communication | error in, or significant disagreement with, a published paper | - | - | 3 pages |
- Limits exclude supplementary material. Categories are not switched after submission. A voluntary page charge of USD 110/page is "not obligatory". Colour is free online; colour in print is USD 275 per figure.
- **References:** no reference limit stated on the journal pages. IEEE Author Center warns that "inflating citations by adding unnecessary references is considered a breach of publishing ethics" (structure-your-article page).
- Source: https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls ; https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/
- [DERIVED] A 15-page Full Paper costs 5 x 200 = USD 1,000 in mandatory over-length charges; 13 pages, USD 600. The Moser survey (21 journal pages) sits at the survey maximum.

### 1.3 Template and format [OFFICIAL]
- Manuscript must be PDF, "single-spaced, double column, standard IEEE published format", all pages numbered, fonts embedded, 4-5 keywords (CIS page) and an abstract. Author Center says abstract: single paragraph, up to 250 words, self-contained "without abbreviations, footnotes, references, or mathematical equations", 3-5 keywords; avoid "new" or "novel" in the title; avoid maths symbols in title and abstract.
- Template: the IEEE Template Selector, https://template-selector.ieee.org/ (interactive; I did not download). The class on CTAN is IEEEtran v1.8b (last CTAN update listed 2015-08-28, LPPL 1.3): https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip (page https://ctan.org/pkg/ieeetran). The Template Selector may serve a newer sample file; compare before use. [DERIVED] Journal layout is `\documentclass[journal]{IEEEtran}` (standard IEEEtran usage; not re-verified on an official page here).
- Authors are encouraged "to put detailed derivations in appendixes". Final files: single zip of TeX/LaTeX sources. ORCID is required for every author (CIS page, section C).
- Submission portal: IEEE Author Portal, https://ieee.atyponrex.com/journal/tnnls (account needed; the page is behind a Cloudflare check that I did not bypass). Authors must give full contact details for every author or the paper is returned without review.

### 1.4 Review model [OFFICIAL, with a conflict]
- CIS Information for Authors: at least two independent reviewers, **double-anonymous** (reviewers do not know authors and authors do not know reviewers). The journal home page carries "ATTENTION AUTHORS: Please read the Double-Anonymous Review Policy before submitting"; that link resolves to the same Information for Authors page, and I found no separate policy text on how to anonymise.
- Xplore About Journal says reviewers use "a single and/or double anonymous peer review process, where the identities of the reviewers are not known to the authors, but the reviewers know the identities of the authors", citing PSPB Operations Manual 8.2.1.C and 8.2.2.A.
- **Conflict (not resolved here):** the two official pages describe different anonymity. Anonymisation rules for links, preregistration records and Zenodo/GitHub artefacts are therefore unknown; for a double-anonymous track the OSF/Zenodo/GitHub links would need anonymised mirrors. Other IEEE CIS journals that moved to double-anonymous (e.g. T-AI, T-Games) ask for removal of names, affiliations, acknowledgements, self-links and third-person self-citation (cis.ieee.org TAI and T-Games pages, via search summary; not TNNLS rules).
- Review time: **not stated** on any official page read. Acceptance rate: not stated.

### 1.5 Supplementary material [OFFICIAL for the general rule; TNNLS-specific limit not found]
- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/ : supplementary files (text TXT/DOC/DOCX/PDF, images, video, audio) are labelled supplementary and uploaded as separate files at submission; a graphical abstract (660 x 295 px, 300 dpi, under about 45 KB) and video summary (under 100 MB) are peer reviewed with the article; datasets and multimedia need a README (setup, run instructions, contact); accepted supplements are posted on Xplore as a zip. The first footnote notes that supplementary material exists.
- TNNLS page-limit text excludes supplementary material from the count. [DERIVED] There is no stated rule that reviewers must read it; treat it as optional reading.

### 1.6 Code and data policy [not stated]
- No TNNLS code/data mandate on any page read. IEEE asks only for READMEs with dataset/supplement uploads. [ABSTRACT] Several recent TNNLS abstracts end with a GitHub URL (TCPFMC, RadVUQA, the LLM-uncertainty review), so code release is common practice, not a requirement. Preprints: IEEE policy permits arXiv posting before and after submission with the stated copyright notices (https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-arxiv ; Author Center submission policies); how that squares with double-anonymous review is not addressed on the pages read.

### 1.7 AI-use policy and the conflict with Shlok's rule [OFFICIAL]
- CIS Information for Authors, section K: "The use of AI-generated text in an article shall be disclosed in the acknowledgements section of any paper submitted to an IEEE Conference or Periodical. The sections of the paper that use AI-generated text shall have a citation to the AI system used to generate the text."
- IEEE Author Center (newer, broader wording), https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/ : AI-generated content "(including but not limited to text, figures, images, and code) shall be disclosed in the acknowledgments section"; the AI system is identified, the specific sections are identified, with a brief explanation of the level of use. AI for editing and grammar is "generally outside the intent": disclosure not required but recommended. Reviewers must not upload manuscripts to public AI platforms.
- **Conflict, stated precisely:** IEEE places the disclosure in **Acknowledgements** (text, and per the Author Center page also figures, images and code), and the CIS page adds a citation to the AI system in the affected sections. Shlok's standing rule keeps AI only in a separate "Declaration of generative AI use" section. The two cannot both hold literally. The Author Center page also says acknowledgements may be placed elsewhere only by the journal's rule; I found no TNNLS carve-out for a Declaration section. Not resolved; it needs Shlok's decision (or a query to the EiC/editorial office).
- [DERIVED] The Author Center scope (code, figures) is wider than the project's current Declaration; the paper's code was written with agent help, so the disclosure would be more than a grammar note.

### 1.8 Open access and cost [OFFICIAL]
- Hybrid. Traditional route: no APC (page charges apply as above). Open access: **USD 2,800** for articles submitted in 2026; IEEE Members 5 % off, IEEE Society Members 20 % off, not combinable, no discount for undergraduate or graduate students; corresponding authors in World Bank low-income countries get a discount (India's classification not checked here).

### 1.9 Stance on negative results, reproducibility, preregistration
- Not stated on any page. The nearest official wording is the Full Paper definition ("not of incremental nature... well-founded and conclusive treatment of a problem") and the scope phrase "exploratory developments". The Brief Paper definition ("extension of previous results... conclusive and useful") also does not describe a null measurement. A preregistered null that adds no method has no stated home; this is a fit risk, not a rule.

### 1.10 "Best paper in the journal"
- The CIS awards page lists an **IEEE TNNLS Outstanding Paper Award**; for the current round no external nominations are taken and all 2024 publications are considered automatically (https://cis.ieee.org/awards). A search summary of CIS pages gives "overall quality" as the stated basis, up to three awards a year, USD 1,000, judged two years after publication; I did not read the criteria page itself. So "best paper till date" is not something a submission can aim at by format; it is decided about two years after publication, by overall quality.

## 2. What the journal's own pages imply for Paper 2's format
- 15 two-column pages maximum, including references, figures, tables and algorithms. Current draft: 77 pages single column; about 26,000 words in `paper2/sections/*.tex` (appendix 3,650 words; main body about 22,400), 20 tables, 8 algorithm boxes, 16 numbered equation environments, 2 propositions, 2 figures, 55 cited keys.
- [DERIVED] A 15-page IEEEtran page carries roughly 900-1,100 words of text without floats, so the paper would need roughly 8,000-10,000 words of running text plus floats. That means cutting the main text by more than half, and moving the Tier-3 comparison, most algorithm boxes, most tables and proofs into a supplement and appendix. I did not compile an IEEEtran version, so this is an estimate.

## 3. Fifteen recent TNNLS papers, closest to our topic
Source for every row: public Xplore abstract page (abstract, page range, reference count) opened 2026-10-29 unless noted. Page count = last minus first page + 1 of the published page range (includes references). **Full text of 13 papers is paywalled and was not read**; counts of figures, tables and equations exist only for the two open-access papers. "Early access" papers show unpaginated "1-N" ranges.

| # | Paper (DOI), volume(issue), pages | Proposes | Validation as stated in the abstract | Pages / refs | Access |
|---|---|---|---|---|---|
| 1 | TCPFMC: Trustworthy Cyclic Progressive Fusion for Multimodal Classification (10.1109/TNNLS.2026.3661974), 37(9) 4246-4260 | A modality "energy score" to measure each modality's confidence, plus a cyclic progressive fusion | Six multimodal datasets vs state of the art; code on GitHub | 15 / 69 | paywalled |
| 2 | Informative Data Selection With Uncertainty for Multimodal Object Detection (10.1109/TNNLS.2023.3270159), 35(10) 13561-13573 | Uncertainty-aware fusion of point clouds and images, uncertainty embedded in box generation | KITTI 2-D detection plus derived "dirty" data (Gaussian noise, motion blur, frost); robustness analysis | 13 / 55 | paywalled |
| 3 | A Framework for Counterfactual Explanation of Predictive Uncertainty in Multimodal Models (10.1109/TNNLS.2024.3476080), 36(7) 12507-12520 | Counterfactual explanations in a multimodal VAE latent space plus a Bayesian local linear approximation to judge them | Multimodal classification and regression tasks | 14 / 54 | paywalled |
| 4 | Conformal Loss-Controlling Prediction (10.1109/TNNLS.2024.3356512), 36(2) 2973-2983 | Extends conformal prediction from miscoverage to a general loss, per test object | Finite-sample guarantee proved under exchangeability; experiments on classification with class-varying loss and weather-forecast post-processing | 11 / 49 | paywalled |
| 5 | Satellite Pose Set Estimation by Uncertainty-Guided Conformal Keypoint Detection (10.1109/TNNLS.2025.3598481), 36(12) 20120-20132 | Inductive conformal sets on keypoints propagated to pose sets via PnP | SPEED and LineMOD-Occlusion datasets; coverage of the true pose checked | 13 / 47 | paywalled |
| 6 | Comparing Uncertainty Measurement and Mitigation Methods for LLMs: A Systematic Review (10.1109/TNNLS.2026.3723117), early access | Survey plus benchmark of uncertainty and calibration methods | Seven methods on three reliability datasets; review list and code on GitHub | 21 / not shown | paywalled |
| 7 | Beyond the Hype: A Dispassionate Look at Vision-Language Models in Medical Scenario (10.1109/TNNLS.2025.3558857), 36(10) 17623-17634 | Benchmark RadVUQA (anatomy, multimodal comprehension, quantitative reasoning, physiology, robustness) | Evaluates existing LVLMs; reports "critical deficiencies"; code on GitHub | 12 / 30 | paywalled |
| 8 | Evaluating Large Language Models on Named Entity Recognition (10.1109/TNNLS.2025.3636917), 37(6) 2658-2672 | Evaluation of 28 LLMs plus an LLM-NER framework with a Check phase against hallucination | 13 datasets, 5 domains, four perspectives (fine-tuning, scale, hallucination, prompts) | 15 / 96 | paywalled |
| 9 | MALFM-Captioner: Multipath Alignment Learning for Image Captioning With Feature Mask (10.1109/TNNLS.2026.3690650), early access | A discrete-diffusion captioner with a feature-mask module and a gated fusion module | MS COCO and Flickr30K; +0.9 % BLEU-4, +1.9 % CIDEr; compared with DDCap and Bit Diffusion | 13 / not shown | paywalled |
| 10 | Semi-Supervised Multimodal Representation Learning Through a Global Workspace (10.1109/TNNLS.2024.3416701), 36(5) 7843-7857 | Shared latent workspace over frozen unimodal encoders, trained by cycle-consistency | Three datasets, vision-language pairings; needs 4 to 7 times less matched data; includes a limitations section | 15 / 56 | open access |
| 11 | AquaticCLIP: A Vision-Language Foundation Model and Dataset for Underwater Scene Analysis (10.1109/TNNLS.2026.3657138), 37(8) 3956-3969 | Domain CLIP, 2-million image-text dataset, prompt-guided vision encoder | Ablations, comparison with state-of-the-art methods, computational complexity section | 14 / 122 | open access |
| 12 | Uncertainty-Aware Graph Neural Networks: A Multihop Evidence Fusion Approach (10.1109/TNNLS.2025.3581083), 36(10) 18463-18477 | Evidence-theory GNN with a parameter-free cumulative belief fusion and a three-term loss | "Various datasets and theoretical analyses"; accuracy, trustworthiness, attack robustness | 15 / 67 | paywalled |
| 13 | Resisting Noise in Pseudo Labels: Audible Video Event Parsing With Evidential Learning (10.1109/TNNLS.2024.3505674), 36(6) 10874-10888 | Evidential deep learning against noisy modality-wise pseudo labels | Audio-visual video parsing benchmarks (abstract truncated in my read) | 15 / 50 | paywalled |
| 14 | Covariate Balancing Methods for Randomized Controlled Trials Are Not Adversarially Robust (10.1109/TNNLS.2023.3266429), 35(4) 5014-5026 | An empirical demonstration that standard balance measures admit worst-case assignments; an adversarial attack and an index | Empirical (abstract truncated in my read) | 13 / 76 | paywalled |
| 15 | Off-Policy Prediction Learning: An Empirical Study of Online Algorithms (10.1109/TNNLS.2024.3373749), 36(3) 4477-4491 | Empirical study of 11 algorithms, then two step-size methods derived from it | Three small tasks, sensitivity, speed, asymptotic error | 15 / 54 | paywalled |

Reference-paper facts (full text read earlier, `research/paper2/benchmark/LENS-CRAFT.md`): Moser et al., 10.1109/TNNLS.2024.3476671, 36(7) 11793-11813, 21 pages, 8 figures, 4 tables, 47 numbered equations, 185 references, no appendix, no code, no PRISMA.

Counts for the two open-access papers (HTML page elements, approximate; I did not read the bodies closely): #10: 7 figures, 3 tables, about 10 numbered equations, sections Introduction, Related Work, Problem Statement, Datasets, Model, Experiments, Conclusion with subsections "Limitations and Open Questions" and "Implications for Cognitive Science". #11: 7 figures, 12 tables, about 6 numbered equations, sections Related Work, Proposed Model, Experimental Evaluations (implementation, datasets, ablation, SOTA comparison, complexity), Conclusion.

### 3.1 What the 15 show [DERIVED from the table; abstract-level evidence]
1. **Length.** Published length is 11 to 15 pages for 14 of 15 (median 14); only the survey/benchmark review is 21. Most accepted articles use the 15-page maximum and so pay the over-length charge.
2. **References.** 30 to 122 where shown, median about 55 (Paper 2 has 55).
3. **Constructive artefact is the norm.** Even evaluation papers (#7, #8, #14, #15) attach a benchmark, a framework, an attack or two derived methods. I found no pure-null measurement in this set. This is inference from abstracts; the three evaluation papers #7, #8, #14 do report negative or critical findings ("critical deficiencies", "not adversarially robust"), so a negative headline is admissible when paired with an instrument others can use.
4. **Breadth of validation.** Six datasets (#1), 28 models by 13 datasets (#8), several tasks (#4), ablations plus complexity (#11). Single-model, single-dataset studies do not appear in this set.
5. **Theory where claimed.** #4 and #12 pair a proved guarantee or "theoretical analyses" with experiments. The conformal papers (#4, #5) are 11 and 13 pages with 47 to 49 references.
6. **Scope neighbours.** Reliability-aware fusion appears (#1, #2, #12, #13) but each proposes a trained method with a baseline table. No paper in this search is on masked discrete diffusion LMs; #9 is the only discrete-diffusion paper and reports small gains (0.9 and 1.9 points), so TNNLS does take modest SOTA increments in applied diffusion work.
7. **Open code.** Three of the 15 abstracts name a GitHub repository.

## 4. What a TNNLS paper must contain to be outstanding there [DERIVED, from sections 1 and 3]
- A "well-founded and conclusive treatment of a problem" (official wording), stated as a single technical contribution: a method, a theory, or a benchmark/analysis instrument. Not incremental.
- Evidence across more than one dataset or backbone, with named strong baselines, ablations and a cost/complexity statement.
- A theory or guarantee when one is claimed, with the long derivations in appendices (IEEE advice).
- Honest scope and limitations; a limitations subsection appears in the open-access sample.
- Compact: 13 to 15 pages including references; figures that carry the argument (the Moser reference uses eight single-column schematics and no data plots, see LENS-CRAFT).
- Code release, and, if the paper reports AI-generated content, the Acknowledgements disclosure.
- Outstanding status is awarded about two years later by the Society; I found no feature a submission can request.

## 5. Mapping Paper 2 (`paper2/main.tex`) against TNNLS
State of the draft: preregistered NEGATIVE main result (GATE-M, net accuracy change inside +/-0.05 under JPEG, noise, splice; n = 500 each; one pretrained model, UniDisc 1.4B, COCO), correlated-token gating theory (Proposition 2), exploratory Tier-3 comparison of hard gate, robust combiners and soft weighting, family H (SugarCrepe hard negatives) pending, no new method ("The paper proposes no new fusion rule"). Current target is Information Fusion.

| TNNLS expectation | Paper 2 today | Gap |
|---|---|---|
| Full Paper "not incremental", "conclusive treatment" | A null on one gate, scope stated as one model and one dataset, "not a finding that GATE-M has no effect" | Wording of the aims favours a positive, general conclusion. The honest scope sentence is correct but weak against it. |
| 15 two-column pages | 77 single-column pages | More than 50 % cut; Tier 3, algorithms, tables to supplement |
| Validation breadth (datasets, backbones, baselines, ablations) | One model, one dataset, eleven preregistered families, ablation-like comparisons exist (Tier 3) | Breadth is thin on models and datasets; family H adds a second task type if it runs |
| Theory with proofs | Proposition 2 plus a correlated-token analysis, detailed in method.tex | A real asset; needs a proof appendix and a statement of what is proved vs measured |
| Constructive artefact | A gate with a conformal-risk threshold and a released evaluation harness; no new model | Evaluation papers in TNNLS carry a benchmark or framework; the harness could be framed that way, but it is not framed that way now |
| Reproducibility | Preregistration, pinned code, Zenodo planned | Anonymisation of links under double-anonymous review is undecided; IEEE has no preregistration category |
| Abstract: single paragraph, up to 250 words, no abbreviations, no equations | 232 words but uses "GATE-M", "CI", maths ($\pm0.05$) | Rewrite |
| Keywords 4-5 (CIS) or 3-5 (Author Center) | 6 keywords | Cut |
| Title without "novel/new" or maths | Question title, no selling word | Fits |
| References: cite only what supports the work (IEEE) | 55 keys; Shlok's rule asks for verified TNNLS papers to be cited | A handful of TNNLS fusion/conformal papers from section 3 are on topic; cite only where each supports a sentence |
| AI disclosure in Acknowledgements | Declaration-only practice | Conflict, section 1.7 |
| ORCID for all authors; native contact details | Supervising professor name not yet filled | Needed before submission |

Overall [inference]: the theory and the preregistered design are strengths; the single-model scope, absence of a trained method and the 15-page cap are the main risks. The abstract-level evidence in section 3 shows no accepted pure-null paper, but it shows accepted critical-evaluation papers that bring a reusable instrument. I did not find any official statement that would block a null result, and none that welcomes one.

## 6. Options and what a follow-up "new model" paper would need
- **Option A: send Paper 2 as is, compressed to 15 pages.** Highest scope-fit risk; reviewers trained on method papers may read "no improvement detected" as "no contribution". Information Fusion remains the better home for this version (its pages are in `VENUE-OPTIONS-2026-10-29.md`).
- **Option B: restructure Paper 2 as measurement + theory + instrument for TNNLS** (frame the harness and the conformal-threshold check as the reusable artefact; add family H and a second backbone only if runs exist). Needs the supervising professor's agreement; changes the claim and the preregistration must be respected (no claim beyond the registered wording).
- **Option C: a separate model paper** that uses the null and the correlated-token theory as motivation. For TNNLS it would need:
  1. A named mechanism with a stated assumption set (for example a reliability signal trained or calibrated for correlated tokens) and a proof or bound tied to the correlated-token result.
  2. At least two backbones and more than one task or dataset (the TNNLS sample runs from 3 to 13 datasets), strong baselines including GATE-M, robust and soft fusion and a trusted/evidential fusion baseline of the #1/#12/#13 type, ablations of each module, and a compute/complexity table.
  3. Several corruptions and severities, confidence intervals, and released code.
  4. A 13-15 page layout with theory in an appendix.
  5. IEEE originality handling: the earlier paper must be cited and the differences stated; overlapping text, figures or results need a clear "differs from" statement; the two papers must not be under review at the same time (IEEE disclosure of concurrent submissions, Author Center "Recycling content").
  - Practical limit: the laptop GPU is 12 GB with a crash history in this project, so training a second backbone is a real cost.
- Concurrent submission to Information Fusion and TNNLS of the same work is not allowed by IEEE policy ("not under review for another refereed publication").

## 7. Items that need Shlok (login or a decision)
1. Open the IEEE Author Portal (https://ieee.atyponrex.com/journal/tnnls) in a normal browser to read the anonymisation instructions and submission checklist (Cloudflare check and account).
2. Decide the AI-disclosure placement (section 1.7) or ask the editorial office.
3. Ask the editorial office (or an associate editor) whether TNNLS is double- or single-anonymous in practice and whether a null measurement with theory is within scope.
4. ORCID for each author; supervising professor's full name and affiliation.
5. Whether IEEE Society membership or an institutional agreement applies to the OA fee (USD 2,800), or whether the traditional route plus over-length charges (about USD 1,000 at 15 pages) is preferred.
6. Review time: not found officially; a person at the journal must supply it.

## 8. Notes
- The user-provided link https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=5962385 returned HTTP 418 to the plain fetcher; the CIS pages, the Xplore About Journal page and the IEEE Author Center were read in the built-in browser instead. No login, no bot-check bypass, no download.
- Third-party deadline or acceptance-rate sites were not used.
- No ledger rows added (no ledger named in the brief).
