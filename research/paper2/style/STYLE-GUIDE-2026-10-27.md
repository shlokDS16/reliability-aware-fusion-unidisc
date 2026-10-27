```yaml
agent: venue-intel
date: 2026-10-27
brief: Learn the target style for a new research article in Elsevier Information Fusion (exemplars + current Guide for Authors) so the writer agent can follow it exactly
sources_examined:
  - C:\Users\Shlok\Downloads\Multi-Modality Language model\1-s2.0-S1566253526004987-main.pdf  (Information Fusion 137 (2027) 104621, survey)
  - C:\Users\Shlok\Downloads\Multi-Modality Language model\1-s2.0-S1574013725001571-main.pdf  (Computer Science Review 60 (2026) 100881, survey)
  - https://www.sciencedirect.com/journal/information-fusion/publish/guide-for-authors  (read in full via text fetch of the official page; WebFetch itself got HTTP 403)
  - https://www.sciencedirect.com/journal/information-fusion/about/insights
  - https://www.sciencedirect.com/journal/information-fusion/publish/open-access-options
  - https://www.elsevier.com/about/policies-and-standards/the-use-of-generative-ai-and-ai-assisted-technologies-in-writing-for-elsevier  (read via WebFetch summary, not verbatim)
  - https://www.elsevier.com/researcher/author/tools-and-resources/graphical-abstract
  - https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions
coverage: >
  Both exemplars: front matter, introduction, section headings, figure and table captions, a sample of body paragraphs,
  closing sections, declarations and the reference list head/tail. Not read line by line: the method-family sections.
  Guide for Authors: all sections. Elsevier "Generative AI policies for journals" page: only the first ~1,200 characters
  came back from the fetch tool, so the AI policy below rests on the Information Fusion guide itself plus an older
  Elsevier policy page read through a summarising fetch (E1 for the older page).
  NOT covered: the Yang et al. CSUR 2023 PDF (it is gitignored and absent from both the main folder and this worktree;
  only research/paper2/professor-sources/README.md exists). No Information Fusion RESEARCH (method) article was
  examined: both exemplars are surveys. The elsarticle class option used by Information Fusion is not stated on any
  page I could read.
claims:
  - statement: Information Fusion research articles are limited to 10-35 pages (figures, tables, references, appendices included) and 50 references; surveys to 50 pages and 300 references; non-compliance may cause desk rejection.
    status: supported
    evidence: Guide for Authors, "Article types" and "Mandatory Submission Requirements for LaTeX Manuscripts"
    level: E2
    confidence: 0.95
  - statement: The journal requires highlights (3-5 bullets, max 85 characters each), abstract max 250 words, 1-7 keywords, a data statement, and a cover letter answering seven mandatory questions.
    status: supported
    evidence: Guide for Authors, sections Abstract, Keywords, Highlights, Data statement, Submission checklist/Cover Letter
    level: E2
    confidence: 0.95
  - statement: Authors must declare generative-AI use in manuscript preparation in a new section before the reference list; AI use inside the research methods is a separate matter and, where relevant, must be described in the methods.
    status: mixed
    evidence: Guide for Authors "Declaration of generative AI use"; older Elsevier policy page (summary) for the methods clause
    level: E2 (guide) / E1 (methods clause)
    confidence: 0.8
  - statement: Neither exemplar is a method paper, so section order and figure mix for a method article are NOT learned from them.
    status: supported
    evidence: both PDFs are surveys
    level: E2
    confidence: 0.99
competing_explanations: []
unknowns:
  - elsarticle option and whether the 35-page limit is measured in single-column review layout or two-column CAS layout
  - whether a 2025/2026 Information Fusion RESEARCH paper on multimodal diffusion exists to copy structure from (not searched)
  - the impact-factor year (the Insights page does not state it)
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Information Fusion style guide for Paper 2 (2026-10-27)

Evidence tags per CONTRACT: guide rules are E2 (page text read); exemplar observations are E2 for what was read.
Journal: Information Fusion (Elsevier), ISSN 1566-2535. Both exemplars are **surveys**; for a research article the
page and reference limits are much tighter than either exemplar shows (see 1.1).

## 1) Guide-for-authors checklist

Base URL for every rule below: https://www.sciencedirect.com/journal/information-fusion/publish/guide-for-authors
(section name given in brackets). The page is blocked for WebFetch (HTTP 403); a text-extraction fetch of the same
official URL worked. No mirror was used.

### 1.1 Hard limits (desk-rejection risk)
| Rule | Value | Section |
|---|---|---|
| Research article length | 10-35 pages including figures, tables, references, appendices, biosketches | Article types |
| Research article references | **maximum 50** | Article types |
| Survey length / references | up to 50 pages / max 300 | Article types |
| LaTeX | must use the journal LaTeX template; all editable sources (.tex, figures) on submission; PDF alone refused; page limit measured on the final formatted version in the template | Mandatory Submission Requirements |
| Consequence | "may result in desk rejection" | same |
| Cover letter | mandatory questions (1.4); missing answers may cause desk rejection | Cover Letter |

Consequence for us: the exemplars cite 157 and about 124 works; our paper may cite **50**. Budget references hard.

### 1.2 Front matter
- Abstract: concise, factual, **max 250 words**; states purpose, procedures, main findings, principal conclusions; stands alone; avoid references and non-standard abbreviations. [Abstract]
- Keywords: **1 to 7**, English, avoid multi-word keywords with "and"/"of" where possible. [Keywords]
- Highlights: required at submission; **3 to 5 bullets, each max 85 characters including spaces**; separate editable file whose name contains "highlights". [Highlights]
- Graphical abstract: encouraged, not required; separate file; at least 1328 px wide, longest side horizontal, readable at 13 cm width; TIFF/EPS/PDF/Office preferred. Elsevier's own page adds min. 1328 x 531 px, 300 dpi, no extra text outside the image, no "graphical abstract" heading. [Graphical abstract] and https://www.elsevier.com/researcher/author/tools-and-resources/graphical-abstract
- Title: concise, informative, avoid abbreviations and formulae unless established. [Title page]
- Title page: author names, affiliations (lowercase superscript letters, full postal address and country), one corresponding author with published email. [Title page]
- Peer review: single anonymised (reviewers anonymous, authors visible), so the manuscript need not be anonymised. [Peer review]

### 1.3 Body, figures, tables, maths, references
- Numbered sections 1, 1.1, 1.1.1; do not number the abstract; cross-refer by number ("Section 3.2"), not "the text". [Article sections]
- Equations: editable text, variables in italic, display equations numbered consecutively in order of reference; appendix equations Eq. (A.1), tables Table A.1, figures Fig. A.1. [Math formulae; Appendices]
- Tables: editable text, captioned, cited in the text, notes below the body, **avoid vertical rules and shading**, use sparingly and do not duplicate results given elsewhere. [Tables]
- Figures: each cited, numbered, with a caption = short title plus description (every symbol and abbreviation explained); vector EPS/PDF with embedded fonts; photographs 300 dpi (min. 1063 px single column, 2244 px full page); bitmapped line art 1000 dpi (3543 / 7480 px). Do not combine multiple images in one file, except images intended for side-by-side comparison. Make colours accessible to colour-blind readers. [Figures; Color artwork]
- References: numbers in square brackets in order of first appearance, author names allowed but number always given; journal names abbreviated per LTWA; give DOIs; datasets cited with "[dataset]" prefix, software cited like any source, preprints clearly marked and replaced by the published version when one exists; every reference must be a real, existing source. [Reference style, Software references, Preprint references]
- Appendices lettered A, B. Footnotes sparingly. Acknowledgments in a separate section directly before the references. [Appendices; Acknowledgements]
- Language: American or British English, not mixed. [Language and editing]

### 1.4 Cover letter (mandatory answers, Cover Letter subsection)
1. Compared to the state of the art? List **5 key references** or justify why not.
2. Which public datasets are common for the problem; which did you use?
3. Which validation measures are standard; which did you apply?
4. Main claim and its significance **to the Information Fusion community** ("we are the first" alone is insufficient).
5. Evidence supporting the claim (main results and implications).
6. Closest related works by others and how this paper relates.
7. Any part published before (conference, preprint)? If so, details and the new contribution; omission may cause desk rejection.
Also: explain how the study fits the journal's aim and scope; be concise.

### 1.5 Declarations at the end
- CRediT author statement required (14 roles; list in the guide). [Author contributions: CRediT]
- Competing interests: complete the declarations tool, upload the generated Word file; "I have nothing to declare" if none. [Declaration of competing interests]
- Funding: standard sentence; if none, the fixed sentence "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors." [Funding sources]
- Data: **Option C**: deposit research data in a repository, cite and link it, or state why not; data statement required at submission, shown on ScienceDirect. Code, models and scripts count as research data. [Research data; Data statement]
- Generative-AI declaration: see 1.6.

### 1.6 Declaration of generative AI: what the policy requires, precisely
Source: the Information Fusion guide, "Declaration of generative AI use" and "Generative AI and figures..." (E2); the older Elsevier policy page (E1, summarised by the fetch tool); https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals (only its first lines were retrievable).
1. **When and where:** declare at first submission, as a statement "at the end of the manuscript", in a **new section before the reference list**; it appears in the published article.
2. **Heading (guide wording):** "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process". The older Elsevier policy page gives the variant "...in the writing process". Use the guide's version (the Information Fusion exemplar also uses it, placed after the CRediT statement and before "Declaration of competing interest").
3. **Template sentence:** "During the preparation of this work the author(s) used [NAME OF TOOL/SERVICE] to [REASON]. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article." The older policy page asks for tool name, purpose and extent of oversight, so the section can be detailed.
4. **Not covered:** basic grammar, spelling and reference-checking tools; specialist disability assistive features. If nothing to disclose, no statement is needed.
5. **AI in the research process is a separate rule.** The older policy page states that AI use in the research process should be declared and described in the methods section where relevant, with tool name, version and manufacturer, reproducibly. The guide's figure rule likewise says the policy "does not prevent" AI in formal research design or methods. This is **not** satisfied by the end-of-paper declaration alone.
6. **Figures:** AI may help make explanatory diagrams and data visualisations derived reproducibly from data. AI must not create or alter images that represent primary observed or experimental data not directly obtained in the research. **If generative AI created any image, the caption of that image must say so, in addition to the declaration.** Graphical abstracts made with AI must comply with the policy.
7. Authors may not list or cite an AI tool as author. Authors are accountable for every reference (AI-generated references can be fabricated).

Interaction with the project rule "AI appears only in the declaration" (MASTER-BRIEF section 1):
- Writing/editing assistance, literature work and code help fit the declaration-only placement.
- The diffusion models we train and evaluate are the **research subject**, not authoring tools; they must be named, versioned and described in the methods like any model. That is ordinary reporting and is unaffected.
- Where an AI system carried out parts of the research itself (wrote experiment code, ran analyses, screened or extracted data), the policy as written points to a methods-section description "if relevant". That clause conflicts with declaration-only placement. Decide this with the user (open question Q1); do not resolve it silently.
- Any explanatory figure produced with a generative image tool needs a caption disclosure. Avoid the issue by drawing diagrams with code (TikZ, matplotlib) and tagging real model samples in captions as "model outputs, unedited".

### 1.7 Open access and cost
- Gold OA APC **USD 4,130** excluding taxes (personalised price shown at submission); or subscription route with **no fee**; the choice does not affect peer review. CC BY, CC BY-NC, CC BY-NC-ND offered. Green self-archiving embargo 24 months. URL: https://www.sciencedirect.com/journal/information-fusion/publish/open-access-options
- Metrics (official Insights page, year not stated there): **Impact Factor 17.4, CiteScore 26.7**. URL: https://www.sciencedirect.com/journal/information-fusion/about/insights
- Free SSRN preprint posting offered at submission; preprints are not prior publication.

### 1.8 LaTeX
Template is Elsevier `elsarticle` (documentation and class via https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions; numbered style `elsarticle-num`, which matches bracketed numeric citations). The option (`review`, `preprint`, `3p`, `5p`) is **unknown**: not stated on any page read. The exemplar PDFs are the two-column published layout. Page limits apply to "the final formatted version using the journal template".

## 2) Exemplar anatomy (side by side)

| Item | Exemplar 1: Information Fusion 137 (2027) 104621 | Exemplar 2: Computer Science Review 60 (2026) 100881 |
|---|---|---|
| Type | Survey: multimodal fusion for food nutrition estimation | Survey: fusing LLMs and diffusion models |
| Title pattern | "Multimodal information fusion for <task>: A survey" (topic, colon, type) | "Fusing LLMs and diffusion models: A comprehensive survey of progress, challenges, and future directions in generative AI" |
| Length | 23 pages, about 22k words incl. references and tables | 21 pages, about 19k words incl. references and tables |
| Abstract | one unstructured paragraph, about 198 words; sentence order: field and why it matters, why it is hard, how fusion helps, what this paper does, how it differs from prior surveys, taxonomy, what is compared, limits and directions, one-line value statement | one paragraph, about 222 words: gap, importance, method, key findings, challenges, trends, value; ends with a repository URL |
| Keywords | 4 (e.g. "Multimodal information fusion", "Artificial intelligence") | 9 (more than Information Fusion allows, so do not copy) |
| Highlights | not printed in the PDF; guide requires 3-5 at submission | printed "HIGHLIGHTS" box, 5 bullets of about 70-90 characters, each starting with a verb ("Summarizes...", "Identifies...") |
| Sections | 1 Introduction (1.1 scope and methodology, 1.2 differences with related surveys, 1.3 rationale and novelty of taxonomy); 2 Background (problem formulation, challenges, single-modal progress); 3 Datasets and metrics; 4-7 four method families, each with "x.1 Principles and representative frameworks" and "x.2 Discussion and comparative insights"; 8 Evaluation (critical comparison; quantitative table on one benchmark); 9 Applications; 10 Challenges and future directions; 11 Conclusion | 1 Introduction; 2 Background (LLMs, diffusion models); 3 Classification (three families, 3.4 comparative quantitative analysis, 3.5 deployment); 4 Challenges and limitations (eight subsections); 5 Future directions; 6 Conclusion |
| Introduction ending | four contribution bullets, each beginning "This survey ...", then a roadmap paragraph ("Section 2 ... Section 11 ...") | no bullets; scope sentence, then roadmap paragraph |
| Figures | 9: (1) chronological milestone timeline, (2) overall framework layer diagram, (3) taxonomy tree, (4) generic pipeline schematic, (5) dataset sample images, (6-9) one architecture overview per method family | 5: (1) bar/line chart of publications per year, (2) selection flow diagram, (3) attention schematic, (4) three diffusion-family schematic, (5) taxonomy tree. No grid of model outputs in the paper body |
| Tables | 6: related-survey comparison, datasets, method-family critical comparison (strengths, risks, applicability), quantitative results on one benchmark, applications, challenges | 6, several long multi-page catalogues of surveyed methods; Table 4 reports FID (lower better), CLIPScore, inference time per image |
| Results presentation | single benchmark, one metric (PMAE, lower is better); text names top methods and states the metric direction; explicit caveat about protocol differences before comparing | values copied from original papers with an explicit non-comparability caveat; arrows in column headers |
| Equations | few; one problem-formulation paragraph with set notation for modalities and outputs (maths glyphs were lost in text extraction, so count unreliable) | about 44 numbered equations in the background and per-method "mathematical representation" subsections |
| Related-work organisation | by problem-oriented taxonomy, not by year or architecture; a table contrasting prior surveys and stating "main difference from this survey" | by integration mechanism and application |
| References | 157, numbered [n], order of appearance, authors, title, abbreviated journal, volume, pages, DOI | about 124, same numeric style, arXiv entries as "arXiv preprint arXiv:..." |
| Declarations (order) | Conclusion; CRediT; Declaration of generative AI and AI-assisted technologies in the manuscript preparation process; Declaration of competing interest; Acknowledgments; Data availability ("No data was used..."); References | Conclusion; Declaration of competing interest; Acknowledgements; Data availability; References (no CRediT, no AI section) |
| AI declaration wording (exemplar 1) | one tool named for language editing and wording refinement; authors reviewed and edited and take full responsibility; three sentences | none |
| Corresponding author | footnote with symbol and email list | same |
| Dates block | Received, revised, accepted, available online | same |

Observation (E2): in exemplar 1 the Introduction alone runs roughly 4 pages and uses the sub-structure scope, differences, novelty. A research article under a 35-page ceiling and 50 references cannot copy survey structure.

## 3) Figure catalogue and what our paper should emulate

Types seen in the exemplars and the equivalent for a method paper. Project rule: only real model outputs and real measured numbers (MASTER-BRIEF section 0); every figure traceable to a run directory.

| Type seen | Seen in | Our counterpart | Notes |
|---|---|---|---|
| Overall framework diagram (data, method, output layers) | Ex1 Fig. 2 | Fig. 1: one-page overview of the model/method: text, image, audio token streams, masking, shared denoiser, unmasking order | draw with TikZ/matplotlib, not a generative image tool |
| Pipeline schematic | Ex1 Fig. 4 | method figure: masking schedule, sampler loop, conditioning on a subset of modalities | |
| Dataset samples | Ex1 Fig. 5 | one strip of benchmark inputs actually used | real samples, citation of licence |
| Timeline / publications-per-year | Ex1 Fig. 1, Ex2 Fig. 1 | skip (survey device) | |
| Taxonomy tree | Ex1 Fig. 3, Ex2 Fig. 5 | at most one small design-space figure if the contribution needs it | |
| Selection/flow diagram | Ex2 Fig. 2 | not used (screening removed) | |
| Architecture per family | Ex1 Figs 6-9 | single architecture figure | |
| Tables of method comparison | both | one main results table (mean with interval, best in bold, arrows for direction), one ablation table | no vertical rules or shading (guide) |
| Not in exemplars; stated by the brief as the reference style (Yang et al. CSUR 2023, not available locally, so unverified) | n/a | (a) step-by-step unmasking strip for text and image from the same prompt; (b) qualitative comparison grid, columns = methods, rows = prompts, with measured metric printed under each cell; (c) ablation line plots with intervals; (d) a bar or heat-map of cross-modal consistency per condition | each panel from a committed script; side-by-side comparison grids are allowed as one file by the guide's exception for images meant to be compared |

Figure production rules: vector PDF for plots; samples as PNG at the stated resolutions; font size legible at single-column width (about 8.4 cm); colour-blind-safe palette; caption = bold-free short title sentence plus description, units, and the sentence that images are unedited model outputs when true. A graphical abstract is optional; if made, 1328 px wide minimum.

Budget: a 35-page ceiling with 50 references suggests about 6-9 figures and 3-5 tables. This is an inference, not a venue rule.

## 4) Writing-style rules for the writer (30 max)

Derived from exemplar 1 (clean IF prose) and avoiding exemplar 2's looser style. Paraphrased patterns only.

1. Present tense for what the paper does and for established facts; past tense only for what was run ("trained for", "measured").
2. Impersonal voice: "this paper", "the proposed sampler". Exemplar 1 contains no "we"; exemplar 2 uses "we" occasionally. Prefer the first style for consistency.
3. Short declarative sentences, mostly 12-25 words; one claim per sentence.
4. Paragraphs of 5-9 sentences, opening with a topic sentence; the last sentence delivers the consequence.
5. Open the introduction with a one-sentence definition of the problem ("X aims to ..."), then why it matters, then why it is hard.
6. Contrast with prior work explicitly: pattern "Different from existing ..., this paper ...".
7. End the introduction with contribution bullets (3-4), each starting with the same subject and a verb, 2-3 lines, each tied to a section or a figure, then a roadmap paragraph naming every section by number.
8. Use fusion vocabulary in the framing: modalities, heterogeneous sources, cross-modal interaction, complementary information, missing-modality robustness. Define "fusion" once, operationally, for this model.
9. Every comparison states the direction of the metric ("lower is better") and the protocol; state when numbers are not comparable.
10. Name every subsection to say what it contains: "Principles and ...", "Discussion and ...", "Implementation details", "Ablation of ...".
11. Present tables with a one-line caption that states the metric, split and number of seeds; bold the best entry; give interval or standard deviation for every learned result; footnote the interval type.
12. Each figure and table is cited in the text before it appears and is interpreted in the text in one or two sentences, not only listed.
13. Keep equations to what a reader needs: define symbols directly after each display equation ("where x denotes ..."), number all displayed equations, refer to them as Eq. (n) or "Eq. (n)".
14. Present the algorithm as a numbered pseudo-code block with inputs, outputs and one comment per step; refer to it as Algorithm 1.
15. Report statistical evidence plainly: effect size, interval, test, n; no "significant" without a test; say "no detectable difference" when intervals overlap.
16. Hedge by quantity, not by adverb: write "in three of four tasks" rather than "generally"; keep "may" for genuine uncertainty and "suggests" for inference; use "shows" only for what a table shows.
17. State limitations in their own subsection or paragraph in Discussion, with concrete scope (datasets, model sizes, sequence lengths).
18. Banned words (read as machine-written; present in exemplar 2): meticulously, comprehensive (unless a count backs it), highly informative, pivotal, landscape, delve, underscore, paradigm shift, seamless, unprecedented, notably used as filler.
19. Avoid sentence pairs of the form "not only ... but also", em-dash asides, and lists of three adjectives.
20. Use one term per concept (for example "unmasking order", not also "decoding schedule"); define abbreviations at first use in the body and again in the abstract only if needed.
21. No citations in the abstract; no abbreviations unexplained there; abstract in one paragraph of about 200-250 words, order: problem, gap, method, evidence with numbers from run directories, consequence.
22. Highlights: 3-5 bullets, at most 85 characters each, start with a verb, one result per bullet, numbers allowed only if they appear in the paper.
23. Keywords: 5-7, single concepts ("Masked diffusion", "Multimodal fusion", "Discrete diffusion", "Cross-modal generation").
24. Cite by number in order of appearance, author name optional but number mandatory ("Smith et al. [12] report ..."); cite the original source for each factual claim; at most 50 references in total, so cite surveys for background and primary sources only for what the argument uses.
25. Related work: organise by the problem-oriented axis of our contribution (for example how modalities are tokenised, how masking is scheduled, how modalities are coupled), end with one comparison table versus the closest 4-6 works and a sentence on the difference; do not narrate papers one by one.
26. Section 8-style discussion block: for each result, give the observation, the likely cause as hypothesis (marked as such), and what would falsify it.
27. Conclusion: three to five sentences restating findings with the same numbers, limits in one sentence, future work in one sentence; no new claims.
28. Cross-reference by number ("Section 5.2", "Table 3"); never "above" or "the following".
29. Keep AI mentions out of the body per the project rule, except where the policy requires methods-level disclosure (see 1.6 and Q1). Name the studied models and versions precisely in the methods.
30. Final pass with research-humanizer; verify no number, citation or claim strength changed; check page count in the elsarticle template (at most 35) and reference count (at most 50).

## 5) Scope fit and framing for unified multimodal masked discrete diffusion

Official scope (Guide for Authors, Aims and scope): multi-sensor, multi-source, multi-process information fusion; articles should emphasise architectures, algorithms or applications; theory and real-world application both welcome. The topic list includes data/image, feature, decision and multilevel fusion; intelligent techniques for fusion processing; fusion learning in imperfect, imprecise and incomplete environments; fusion system design and algorithmic issues, computational demands. Generative modelling is not named anywhere in the list.

Assessment (inference, E1-E2): a masked-diffusion multimodal generator is **not an obvious fit** and a desk rejection on scope is a real risk. Both exemplars show the journals accept multimodal and "fusion of model families" framings when the word fusion is operational rather than decorative (exemplar 1 builds its whole taxonomy around what fusing each modality contributes; exemplar 2 treats LLM-diffusion integration as fusion). Required framing to reduce the risk:
1. Treat the shared token space as the fusion mechanism: text, image and audio tokens enter one masked sequence, and the denoiser performs early, token-level cross-modal fusion. Say so in the abstract and first paragraph.
2. Make the fusion benefit a measured result: does conditioning on an additional modality improve the generation or recovery of another, for which subsets of observed modalities (any-subset conditioning), and by how much. This is the "incomplete environments / missing modality" scope item.
3. Report cross-modal consistency and robustness to degraded or missing input, which are fusion evaluation concerns, next to the usual quality metrics.
4. State architecture/algorithm contribution as the Journal's "architectures and algorithms" facet; mention computational demands (sampler steps, memory, latency on the 12 GB GPU) because the scope names it.
5. Put "fusion" in the title and keywords, for example "...for multimodal information fusion"; avoid a title that reads as a pure generative-model benchmark.
6. The cover letter must answer the seven questions in 1.4 with exact references. Question 4 needs a sentence on significance to the fusion community, not to the diffusion community.
7. Fallback: if the evidence turns out to be mostly sample quality with little fusion content, a generative-AI-oriented Elsevier journal may fit better. I did not verify any candidate; the only same-publisher journal examined, Computer Science Review, accepts reviews, not method papers (its exemplar is a survey; I did not open its scope page). Candidates to check later (unverified, not fetched): other Elsevier computer-vision and AI journals. Do not rely on this list.

## 6) Open questions for the user

Q1. AI placement versus the policy (decision needed before drafting). The policy requires the end-of-paper declaration for authoring assistance, but also expects AI used in the research process (running experiments, writing analysis code, extracting data) to be described in the methods "if relevant", and requires caption disclosure for AI-generated images. Should the paper keep every AI mention inside the declaration (accepting the risk that a reviewer or editor reads that as incomplete), or add a short methods sentence for AI-run steps? The declaration can be detailed (tool names, purposes, oversight), which the policy allows.
Q2. Reference ceiling: research articles are limited to 50 references. The brief's draft plan may assume more. Confirm that 50 is acceptable and that the related-work survey knowledge from Paper 1 will be compressed into surveys plus primary sources.
Q3. elsarticle option and measurement: should the writer build in the single-column `review` layout (long) or a two-column layout for the 35-page check? The guide says limits apply to the template's final format but does not name the option. Suggest the two-column layout as the safer reading; confirm with the professor or the Elsevier template package.
Q4. Open access or subscription? OA costs USD 4,130 (personalised price shown at submission; the corresponding author's institution may have an agreement); subscription is free. This affects only the licence choice at acceptance.
Q5. No Information Fusion research (non-survey) article was examined. Should venue-intel sample 3-5 recent Information Fusion method papers on multimodal generation or fusion to calibrate section order, figure counts and the first-page layout (the first step of the standard venue-intel procedure)? This is the largest gap in the current style guide.
Q6. Yang et al. (CSUR 2023) is referenced as the figure model but is not on disk. Provide the PDF or confirm that Section 3 figure types (strip, grid, ablation line plots) are enough.
Q7. Corresponding author and funding statement: who is corresponding author (required, email published) and what funding or "no specific grant" sentence applies? The CRediT roles must also be assigned per author.

## Appendix: ready-to-use declaration block (template, edit with real facts)

Order at the end of the manuscript, following exemplar 1 and the guide: Conclusion; CRediT authorship contribution statement; Declaration of generative AI and AI-assisted technologies in the manuscript preparation process; Declaration of competing interest; Funding; Acknowledgments; Data availability (repository link, DOI for code and run artifacts under Option C); References.

AI declaration skeleton (the user decides content; this is only the policy's frame): "During the preparation of this work the author(s) used [tool and version] to [purpose]. After using this tool, the author(s) reviewed and edited the content as needed and take full responsibility for the content of the published article."

Data availability skeleton: names the repository, the DOI, the licence and what is included (code, configs, per-example predictions, figure scripts); never "available on request".
