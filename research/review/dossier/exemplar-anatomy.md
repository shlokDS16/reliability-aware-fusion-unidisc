```yaml
agent: venue-intel
date: 2026-10-13
brief: Anatomy of five recent CSUR surveys (generative, diffusion, LLM, multimodal), one with an explicit PRISMA protocol, to set rules and a 35-page budget for the planned systematic review (Part B)
sources_examined:
  - doi:10.1145/3696415  Xing et al., A Survey on Video Diffusion Models, CSUR 57(2), 2024-11-07, pp 1-42. Read via arXiv:2310.10647v2 (pdfs/arxiv-2310.10647.pdf, md/arxiv-2310.10647.md)
  - doi:10.1145/3796982  Liu et al., Alignment of Diffusion Models: Fundamentals, Challenges, and Future, CSUR 58(9), 2026-03-10, pp 1-37. Read via arXiv:2409.07253v4
  - doi:10.1145/3713070  Yuan, Li, Zhao, A Survey of Multimodal Learning: Methods, Applications, and Future, CSUR 57(7), 2025-02-20, pp 1-34. Read via the ACM DL full-text page (md/acm-3713070.md); no arXiv copy found
  - doi:10.1145/3735632  Li et al., Fundamental Capabilities and Applications of Large Language Models: A Survey, CSUR 58(2), 2025-09-08, pp 1-42. Read via the ACM DL full-text page (md/acm-3735632.md)
  - doi:10.1145/3801961  Da Ros et al., Large Language Models for Combinatorial Optimization: A Systematic Review, CSUR 58(11), 2026-04-21, pp 1-53. PRISMA. Read via arXiv:2507.03637v1 (md/arxiv-2507.03637.md)
  - Crossref API (page ranges, reference counts), also used for two further CSUR pages counts (10.1145/3783986 pp 1-39 and 10.1145/3731445 pp 1-41, from their DL pages)
coverage: >
  Structural reading, NOT a full read. Per exemplar I extracted text with pdftotext and markitdown (or saved the DL page text),
  computed section spans, counted captions and numbered equations by script, and read: first page and introduction,
  methodology (exemplar 5), every comparison table header, the taxonomy figure (rendered image for 3 of them), the
  open-problems and limitations sections, and the conclusion. Technical content of the method sections was not read, and
  none of the five was verified against its reference list. Evidence level for every statement below: E1 (structural
  extraction), not E2. The arXiv copies differ from the CSUR versions in layout and, for two, in page count, so page shares
  are measured on arXiv copies; counts of figures and tables come from the same copies and may differ by one or two in the
  published version. Tables or figures that exist only as images in the ACM web rendering may be missed for exemplars 3 and 4.
claims:
  - statement: In the three exemplars measured by page, the reference list takes 26.4 to 28.2 percent of all pages (312, 263 and 254 references)
    status: supported
    evidence: pdftotext page positions of the References heading in arxiv-2310.10647, arxiv-2409.07253, arxiv-2507.03637
    level: E1
    confidence: 0.85
  - statement: None of the five exemplars contains an algorithm environment, and none pools reported numbers statistically (no intervals, no meta-regression)
    status: supported
    evidence: grep for Algorithm and Input blocks in all five texts; table and section reading
    level: E1
    confidence: 0.8
  - statement: Only one of the five (LLM4CO) reports a search and inclusion protocol; two others state a data source and date for a bibliometric figure
    status: supported
    evidence: section read per exemplar, below
    level: E1
    confidence: 0.85
  - statement: Six of seven recent CSUR surveys checked exceed the stated 35-page limit (37 to 53 pages)
    status: supported
    evidence: Crossref page fields and DL pages
    level: E1
    confidence: 0.8
competing_explanations:
  - Page counts above 35 may include a supplement or appendix that the DL page range counts, or be editor-approved exceptions; no ACM rule says how often.
unknowns:
  - Extraction accuracy of the counts below was not checked against the published PDFs (the ACM DL PDF is behind a Cloudflare challenge here).
  - Number of display items in the published CSUR versions of exemplars 1, 2 and 5 (arXiv copies used).
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Exemplar anatomy: five CSUR surveys, 2024 to 2026

Scope: structure only. No sentence of any exemplar is reproduced; they are described. Do not copy their wording.
Selection rule: published in CSUR 2024 to 2026, topic generative or diffusion models, LLMs or multimodal learning, at
least one with an explicit protocol. Candidates were found by search of dl.acm.org (E1) and chosen to cover (i) two
diffusion surveys, (ii) one multimodal survey, (iii) one LLM survey with a quantitative tally, (iv) one PRISMA review. No
CSUR survey on discrete diffusion language models or on unified multimodal diffusion was found in 2024 to 2026 by that
search, which supports the novelty of our topic for this journal (E1, search-based, not exhaustive).

## 1. Summary table

| | 1 Video diffusion (V) | 2 Diffusion alignment (A) | 3 Multimodal learning (M) | 4 LLM capabilities and applications (F) | 5 LLMs for combinatorial optimisation, systematic review (C) |
|---|---|---|---|---|---|
| CSUR pages (Crossref) | 42 | 37 | 34 | 42 | 53 |
| Pages of copy measured | 37 (arXiv v2, acmsmall box) | 35 (arXiv v4, letter) | 34 (DL text) | 42 (DL text) | 52 (arXiv v1, letter, of which about 17 appendices) |
| References | 312 | 263 | 169 | 296 | 255 |
| Reference share of pages | 28.0% (10.4 pp) | 28.2% (9.9 pp) | about 6 pp (est., 30 per page) | about 10 pp (est.) | 26.4% (13.7 pp) |
| Figures | 7 | 5 | 6 | 3 | 3 |
| Tables | 4 | 4 | none seen in web text; datasets in the electronic supplement | 3 | 7 (3 in body, 4 in appendices) |
| Numbered equations | 5 | about 15 | 0 seen | 0 seen | 0 |
| Algorithms | 0 | 0 | 0 | 0 | 0 |
| Method or search protocol section | none | none | none (a bibliometric figure with stated source) | none (a tally with expert labelling) | yes, 8.3% of pages |
| Dedicated open-problems section | yes, 2.8% | yes, 4.3% plus embedded | yes, 5.8% | none (conclusion only) | yes, 1.2% plus a limitations section |
| Abstract words | 203 | 135 | not counted | not counted | 123 |
| Claims "first" | yes | yes | no (argues fragmentation) | no | yes |

Display items per exemplar run 3 to 7 figures and 3 to 7 tables; no exemplar has an algorithm. The project plan's "13 to 14
figures and 6 to 8 tables" plus staged algorithms is about twice the exemplar range (see section 4).

## 2. Per-exemplar anatomy

### Exemplar V: A Survey on Video Diffusion Models (doi:10.1145/3696415)

**Section map (share of the 37 arXiv pages; page numbers in that copy).**

| Section | Pages | Share |
|---|---|---|
| Front matter on p1 (title, 8 authors, 203-word abstract, CCS, keywords, ACM reference format) | 0.5 | 1.5% |
| 1 Introduction | 1.4 | 3.8% |
| 2 Preliminaries (diffusion basics, related research domains, datasets, metrics; Tables 1 and 2) | 4.8 | 12.9% |
| 3 Video generation (text-to-video, other conditions, unconditional, completion; results Tables 3 and 4) | 12.3 | 33.2% |
| 4 Video editing | 4.5 | 12.2% |
| 5 Video understanding with diffusion | 1.8 | 4.9% |
| 6 Challenges and future trends | 1.0 | 2.8% |
| 7 Conclusion | 0.2 | 0.6% |
| References (312) | 10.4 | 28.0% |

**Counts.** 7 figures (trend statistics, diffusion overview, three taxonomy trees, qualitative results, challenges
collage), 4 tables, 5 numbered equations, 0 algorithms.

**First page.** About half is front matter; the introduction opens on p1 with the claim that diffusion models took over image generation
and are spreading to video.

**Taxonomy figure.** Left-to-right tree, root at the left rotated label, three to four levels, boxes at the leaves hold
method names with numeric citations in rows (roughly 10 to 25 method names per leaf box); Fig. 3 (generation) fills about
half a page, Figs. 5 and 6 (editing, understanding) sit side by side on one page.

**Main comparison tables (columns).**
- Table 1, caption-level datasets: dataset, year, text source, domain, number of clips, resolution.
- Table 2, category-level datasets: dataset, year, categories, clips, resolution.
- Table 3, zero-shot text-to-video: method, year, training data, extra dependency, resolution, parameters (B), then for
  MSR-VTT FID, FVD, CLIPSIM and for UCF-101 FID, FVD, IS. Rows grouped non-diffusion vs diffusion; "-" where unreported.
  Two sentences of reading follow (extra conditions and extra data help). No intervals, no protocol-matching caveat in
  the passage read.
- Table 4, fine-tuned generation: method, year, type (GAN, autoregressive, diffusion), resolution, extra, then FVD, IS,
  KVD on UCF-101, TaiChi-HD, Time-lapse.

**Introduction justification.** Names five families of earlier surveys (foundation models in AIGC, diffusion models in
general, multimodal learning, text-to-image, text-to-3D) and says they are coarse on video or image-centric. Adds a
bibliometric figure (papers per year, share by video generation, editing, understanding; marked "partial data" for the
last year). Then a contribution paragraph, a "first to concentrate on this domain" claim, an invitation to authors to send
missing work, and a one-paragraph section guide.

**Methodology.** None. Inclusion is implicit ("most representative works"). The living repository is the only
completeness mechanism.

**Open problems.** One section, 1.0 page, five themed paragraphs (video-text data scale, physical realism and long
videos, training and inference cost, benchmark and metric limits, controllable editing). Each paragraph gives a concrete
number or failure (a dataset size and resolution, a model limit) and a vague direction; one figure of failure cases.
Not ranked, not framed as testable.

### Exemplar A: Alignment of Diffusion Models (doi:10.1145/3796982)

**Section map (share of 35 arXiv v4 pages; CSUR copy is 37 pages).**

| Section | Pages | Share |
|---|---|---|
| Front matter (title, 9 authors, 135-word abstract, 4 CCS concepts, keywords) | 1.0 | 2.9% |
| 1 Introduction (3 figures) | 3.3 | 9.3% |
| 2 Overview of diffusion models | 1.4 | 4.0% |
| 3 Fundamentals of human alignment (data, preference models, algorithms, challenges) | 2.9 | 8.3% |
| 4 Alignment techniques for diffusion (RLHF, DPO, test-time, beyond text-to-image, open challenges) | 10.3 | 29.5% |
| 5 Benchmarks and evaluation (feedback datasets, reward models, model evaluation) | 4.5 | 12.7% |
| 6 Future directions | 1.5 | 4.3% |
| 7 Summary | 0.3 | 0.7% |
| References (263) | 9.9 | 28.2% |

**Counts.** 5 figures (conceptual illustration, bibliometric overview with pies, survey framework tree, diffusion
process, RLHF and DPO overview), 4 tables, about 15 numbered equations, 0 algorithms.

**Taxonomy figure.** Fig. 3 is the survey's own table of contents drawn as a left-to-right tree with four levels
(fundamentals; techniques; benchmarks and evaluation), rounded boxes, leaves list citation numbers; it fills about two
thirds of a page. Placed at the end of the introduction as the roadmap.

**Main tables (columns).**
- Table 1: list of symbols (symbol, meaning), shared by LLMs and diffusion, the only unified-notation table in the five.
- Table 2: paradigm comparison matrix: compute cost, feedback or reward type, scalability, key limitations, best use cases;
  rows RLHF, DPO, test-time alignment; qualitative cells.
- Table 3: feedback datasets: dataset, reward model, prompt source, prompt count, image source, image count, annotator
  information, annotation count.
- Table 4: reward-model accuracy across five preference datasets; footnote marks which numbers come from which source
  paper; bold best per dataset; then a reading that accuracy is highest on each model's native dataset and mostly below
  80 percent. This is the closest any exemplar gets to our "synthesis" task, and it is a comparison with provenance, not
  a pooled estimate.

**Introduction justification.** Does not list prior surveys. Argues by data: papers per venue per year, and the share of
alignment papers on LLMs (93.5 percent) versus diffusion (6.5 percent), then by analogy with LLM post-training as a
validated roadmap, and by stating why diffusion differs from token prediction. "First comprehensive review" claim.
Data source stated in a footnote (Google Scholar, date given).

**Methodology.** None beyond that footnote.

**Open problems.** The strongest treatment of the five: "challenge" subsections inside sections 3, 4 and 5, then Section 6
with three directions, each with named candidate formalisms from the literature, and one explicit forward-looking
hypothesis (that large diffusion models already hold implicit preference knowledge, with two paths to test it). Total
about 1.5 pages in section 6.

### Exemplar M: A Survey of Multimodal Learning (doi:10.1145/3713070)

**Section map (share of body text by characters; the DL page text has no pagination; 34 pages total, about 6 pages of references).**

| Section | Share of body text |
|---|---|
| 1 Introduction (modalities and combinations, bibliometric trend analysis) | 8.4% |
| 2 Audio-visual (6 tasks) | 26.1% |
| 3 Text-visual (5 tasks) | 20.2% |
| 4 Touch-visual (4 tasks) | 12.4% |
| 5 Depth-visual (6 tasks) | 18.6% |
| 6 Beyond bimodal (contrastive pre-trained models; LLMs) | 5.1% |
| 7 Other modalities | 2.6% |
| 8 Look into the future | 5.8% |
| 9 Conclusion | 0.8% |

**Counts.** 6 figures (modality overview, DBLP trend analysis in four panels, one overview per modality pair), no
tables in the web text (about 120 datasets are surveyed in the electronic supplement), 0 equations, 0 algorithms, 169
references.

**Taxonomy.** Organised by modality pair then task, one level of subsections; the five-modality figure and one overview
figure per pair serve as taxonomy. No tree.

**Introduction justification.** No comparison with other surveys. Argues that multimodal work is fragmented by modality
pair so researchers lack the overall picture. Supports with a trend analysis from DBLP records up to October 2022
(filtered by year, type and keywords) in four panels.

**Methodology.** None; the bibliometric figure states its data source and cut-off.

**Open problems.** 1.6 pages, five prose themes (modality gap, practical data issues, dual-modality dominance, LLM cost and
hallucination, interpretability and a "continually learning knowledge base" proposal), with a closing point that
multimodal models can underperform unimodal ones. Not testable as stated; opinion with citations.

**Supplement use.** The dataset survey of about 120 datasets sits in the electronic supplement; this is the template for
moving per-paper detail out of the 35 pages.

### Exemplar F: Fundamental Capabilities and Applications of LLMs (doi:10.1145/3735632)

**Section map (share of body text by characters; 42 pages; about 10 pages of references (296, est.)).**

| Section | Share of body text |
|---|---|
| 1 Introduction (two stated issues, two contributions, section guide) | 4.6% |
| 2 Fundamental and interactive capabilities (memorisation, reasoning, generalisation, diversification, interaction) | 27.1% |
| 3 Applications in nine domains (medicine, law, computational biology, finance, social science, programming, robots and agents, AI for disciplines, creative work) | 58.6% |
| 4 Capability assessment in specific domains (tally, radar charts, two case studies) | 9.3% |
| 5 Conclusion | 0.4% |

**Counts.** 3 figures (relationship among capabilities, domain-to-capability map, radar charts), 3 tables (capability
tally by domain; benchmark accuracies of models on three medical benchmarks; the same for programming), 0 equations, 0
algorithms, 296 references.

**Taxonomy.** A two-axis frame: capabilities (rows) against domains (columns), shown as a mapping figure and a table of
counts. No tree.

**Introduction justification.** Two stated problems (capabilities are described too coarsely to match domains; benchmark
scores may not transfer to domain use), not a comparison with named surveys.

**Quantitative synthesis.** Section 4 tallies, for 186 papers across nine domains (25, 19, 20, 24, 22, 23, 22, 15 and 16),
how many involve each capability, by expert evaluation, and converts the tally to percentages for radar charts. In the
passage read, the paper does not state how the 186 papers were selected, who labelled them, or agreement between
labellers. It is a counting exercise, not a meta-analysis, and shows that CSUR accepted counted evidence in a survey.
This is the weakest-protocol example among the five and the nearest in kind to our planned census; ours must state what
this one does not.

**Methodology.** None. **Open problems.** No dedicated section (the three-sentence conclusion lists none), so a
survey without an open-problems section was accepted; consistent with the Charter, which says exposing needed research
is not the main purpose.

### Exemplar C: LLMs for Combinatorial Optimization: A Systematic Review (doi:10.1145/3801961)

**Section map (share of the 52 arXiv pages; CSUR 53 pages).**

| Section | Pages | Share |
|---|---|---|
| Front matter | 0.5 | 0.9% |
| 1 Introduction | 0.8 | 1.6% |
| 2 Aims and motivations (six research questions) | 0.6 | 1.1% |
| 3 Related work (each earlier work described; stated that none is systematic) | 0.6 | 1.1% |
| 4 Background (LLMs; combinatorial optimisation process) | 2.8 | 5.4% |
| 5 Methodology (PRISMA 2020, terminology, search, screening, inclusion) | 4.3 | 8.3% |
| 6 Analysis (process step, LLM architecture, benchmark datasets, application domains, non-experimental literature) | 8.9 | 17.1% |
| 7 Future research directions | 0.6 | 1.2% |
| 8 Limitations | 0.5 | 1.0% |
| 9 Conclusions and future work | 0.7 | 1.3% |
| References (254 in arXiv copy; 255 Crossref) | 13.7 | 26.4% |
| Appendices: A PRISMA checklists 3.0 pp; B to F description of each included study and classification tables 15.0 pp (together about 17 pp) | 17.0 | 32.6% |

**Counts.** 3 figures (optimisation-process overview, PRISMA flow diagram, BPMN screening diagram), 7 tables (queries; included
study characteristics; task examples; then four appendix classification tables), 0 equations, 0 algorithms, 254 references.

**Taxonomy.** No tree. Classification matrices in the appendix (study by process step, by LLM role and architecture, by
benchmark, by domain) with check marks, and counts reported in prose.

**Introduction justification.** Problem framing, then a separate "Aims and motivations" section with six numbered
research questions, then a "Related work" section that describes each earlier review and says none is a systematic
review. The differentiator is the method, not the topic.

**Methodology section (the model for ours).**
- Adopts PRISMA 2020 and explains its terms for a non-medical field (study, report, record, outcome, result, and how
  they were merged for a computing review).
- Date-stamped search (two databases, one date), 14 queries tabulated with hit counts, how duplicates and records without
  authors were removed, citation tracking on a second date.
- Eight eligibility rules coded INCL1-4 and EXCL1-4 and used when excluding; examples of borderline decisions.
- Screening described by person: one author ran searches and first filter, three authors each read one third at full text,
  all cross-checked, the third author resolved conflicts; the workflow drawn as a BPMN diagram.
- PRISMA flow diagram with counts that reconcile (1,472 screened to 123 sought to 103 included, 174 = 103 + 2 + 69), with
  a second column of the same diagram for citation tracking.
- Checklist in an appendix. No reporting of agreement statistics; no risk-of-bias tool; no use of AI tools described in the
  passages read.
- No meta-analysis: studies are classified and counted.
- A separate Limitations section: pre-prints included (about half the studies), possible overstatement from selection of
  positive reports, closed-source models limit replication.

**Open problems.** Six listed directions in 0.6 page (each one to three sentences, with the citations that anticipated
it), plus ethics and bias; no hypotheses.

## 3. Twelve rules a successful CSUR author follows (derived from the five)

Each rule has its pointer. Rules are descriptive of these five and of the Charter; they are not guarantees of acceptance.

1. **Differentiate from named earlier surveys on a stated axis, then say what the axis is.** C does it in a related-work
   section ("none is systematic"); V names five survey families and the gap; A argues by data instead. Four of five claim
   "first"; we cannot (two DLM surveys already exist per PLAN section 3, to verify), so claim the method and the
   conjecture, not priority. [C section 3; V section 1; A section 1]
2. **Show the field's growth with a dated, sourced figure early.** V Fig. 1 (counts by direction), A Fig. 2 (venue and
   LLM-versus-diffusion shares, source and date in a footnote), M Fig. 2 (DBLP, cut-off October 2022). Our PRISMA counts
   and a year histogram of included papers do this job with a stricter source. [V, A, M]
3. **Draw one master taxonomy as a left-to-right tree whose leaves carry citations, and place it where the roadmap is.**
   A Fig. 3 at the end of the introduction; V Figs. 3, 5, 6 at the start of each branch. About half to two thirds of a
   page each. [A Fig. 3; V Fig. 3]
4. **End the introduction with contributions and a section guide, and state the research questions.** All five do; C
   numbers six research questions, which is what lets its Analysis section be organised by question. [V section 1; C
   section 2]
5. **Keep background short and give it one notation table.** Background and preliminaries take 4 to 13 percent of pages
   (C 5.4, A 4.0 plus 8.3 for fundamentals, V 12.9). Only A has a symbol table and equations; our formalism belongs here.
   [A Table 1; C section 4]
6. **Let the taxonomy generate the section list, and close each section with a challenge or evaluation note.** The method
   sections are 40 to 50 percent of pages in V and A; M ends each task subsection with how it is evaluated and what is
   unresolved. [V sections 3 to 5; A section 4; M section 2]
7. **Comparison tables have fixed columns per task, show unreported entries as "-", and carry the provenance of each number
   and a short reading.** V Tables 3 and 4, A Tables 2 and 4. None of the five pools numbers with intervals, tests
   protocol comparability, or audits reporting; our quantitative section is new for the journal, so keep it self-contained,
   label it as the result that organises the material (the Referee page's wording), and keep claims at "consistent with".
   [V Tables 3-4; A Tables 2, 4; F section 4]
8. **If the paper is systematic, write the method as its own section (about 8 percent of pages) with date-stamped
   searches, tabulated queries, coded inclusion rules, who screened what, a flow diagram whose counts reconcile, and a
   checklist in an appendix.** Only C does, and it is the one that differentiates itself by method. [C section 5, Figs 2-3,
   Table 1, Appendix A]
9. **Add a limitations section when selection could bias the evidence.** C names pre-print inclusion, positive-result
   bias and closed-source models; our reporting audit and ledger make the same threats measurable. [C section 8]
10. **Give open problems their own short section (about 3 to 5 percent), tie each to evidence in the paper, and attach a
    candidate route.** V has five themes, C six directions, A three directions with named formalisms and one explicit
    hypothesis with two test paths. F has none and was accepted, so the section is not mandatory, but the Charter's
    question ("what does it mean to researchers and practitioners") is answered best here. Our organising conjecture,
    with its supporting and refuting counts, belongs in this section. [A section 6; V section 6; C section 7]
11. **Budget pages from the reference list.** References take 26 to 28 percent of pages when a survey cites 250 to 310
    papers (V, A, C), about 30 entries per page in acmsmall. Every 30 extra references cost a page. [V p27-37; A p26-35;
    C p21-35]
12. **Use the electronic supplement for per-paper detail.** M puts a survey of about 120 datasets there; C needs 17
    appendix pages for per-study tables, PRISMA checklists and classifications. Both the 35-page limit and the "indicate
    which pages are the 35" instruction make this the sanctioned place for the extraction table, full search strings and
    checklist. [M supplemental material; C Appendices A-D; author guidelines]

Two observations that are not rules. (a) Published CSUR surveys exceed the stated limit: pages 34 (M), 37 (A), 39 and 41
(two further 2025 to 2026 surveys), 42 (V and F), 53 (C), so only 1 of 7 is at or below 35; the guideline still says
excessive length may be rejected without review, so plan for 35 and treat any more as editor-granted. (b) Abstracts of
123 to 203 words are published against a 100-word guideline.

## 4. Recommended section and page budget for our 35 pages (acmsmall)

Assumptions, all measured on the exemplar copies (E1): about 600 words per page of running text including floats; about 30
references per page; a figure about 0.45 page, a table about 0.55 page. Target 35.0 pages including references, slack
0.5.

| Section | Pages | Content | Floats |
|---|---|---|---|
| Front matter and 1 Introduction | 2.0 (0.5 front matter) | scope, gap against the two existing DLM surveys and the multimodal surveys by method, six numbered research questions, contributions, guide; growth figure from PRISMA counts | Fig 1 (growth by year and group) |
| 2 Scope and review protocol | 2.5 | PRISMA 2020 adaptation, queries, eligibility codes, screening roles, extraction and the 10 percent accuracy check, the AI-use description required by ACM (item 3 of csur.md), threats; full strings and checklist in the supplement | Fig 2 (flow), Table 1 (eligibility and screening summary) |
| 3 Background and unified formalism | 2.5 | notation table, forward masking, parametrised reverse process, composed sampler; at most 3 compact algorithms and 12 numbered equations | Table 2 (symbols), Fig 3 (formalism diagram) |
| 4 Taxonomy and landscape | 1.5 | master tree, timeline | Fig 4 (tree, 0.6 page), Fig 5 (timeline) |
| 5 Diffusion language models | 5.5 | objectives, architectures, sampling and decoding, scaling, post-training; one comparison table | Table 3 |
| 6 Unified multimodal diffusion models | 5.0 | shared tokenisation, design space, understanding and generation coupling; one comparison table | Table 4, Fig 6 (design-space map) |
| 7 Quantitative synthesis and reporting audit | 3.5 | forest plot, frontier plot, reporting heatmap; claims as "consistent with", not "validated" | Figs 7-8, Table 5 |
| 8 Open problems and the organising conjecture | 2.0 | five to six problems, each with evidence and a route; the conjecture with supporting and refuting counts | Fig 9 (open-problem map) |
| 9 Limitations and conclusion | 1.0 | selection bias, pre-prints, closed models (rule 9) | none |
| References | 9.0 | about 270 entries; cite the full included set from the supplement and keep the main text near 250 | none |
| Total | 34.5 | | |

Main-text display budget: at most 9 figures, 5 tables, 12 numbered equations, 3 algorithms. This is below the plan's 13 to
14 figures, 6 to 8 tables and staged algorithms, because floats cost about 7 of the 25.5 body pages and the five exemplars
carry 3 to 7 of each with no algorithms. Move the rest (extra forest plots, per-study extraction table, per-paper
tables, full search strings, PRISMA checklist, a long algorithm listing) to the electronic supplement, flagged in the
manuscript as the guidelines require. At 600 words per page, 25.5 body pages minus about 7 pages of floats leaves about
11,000 words of running text, against 13,000 to 15,500 in the exemplars; the coverage sections (5 and 6, 10.5 pages) are
smaller than in V and A (17 and 15 pages) because ours also carries a protocol and a synthesis section. Mitigation: dense
comparison tables and a supplement table listing every included study.

## 5. Concerns for the orchestrator

1. The exemplar analysis is structural (E1); for rules that matter most (the methodology of C and the open-problem
   arguments of A and V) the passages were read, but nothing was verified against the published PDFs.
2. The plan's display-item and algorithm counts exceed what any exemplar carries; revise PLAN section 6.
3. Keep "first" claims out of the introduction.
4. Whether our reference count can be reduced without hurting the "no cherry-picking" criterion depends on the CSUR
   office's answer on supplement references (csur.md, open question 2).
