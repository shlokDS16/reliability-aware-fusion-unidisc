# Where the paper states its use of AI (Paper 1, final version of 2026-10-21, after fixes A-D)

PDF pages are those of `paper/review/main.pdf` (35 pages) and `paper/review/supplement.pdf` (42 pages), checked on
2026-10-21 after fix D (decisions D0061-D0064) and the dataset reference. In the Word file
`paper/review/docx/main.docx` find the same text by section heading and paragraph number (paragraphs counted under
each heading; a bold run-in title such as "Full text." starts inside a paragraph).

## The required ACM statement (AI used to conduct research must be described in the Methods section)

| # | PDF | Word file | What it says |
|---|---|---|---|
| 1 | Section 2.8 "Use of AI in conducting the research", p. 10 | heading 2.8, paragraph 1 | ACM's authorship policy requires the description; all authors are responsible; no language model is an author; no screener, extractor or coder is presented as a human reviewer. |
| 2 | Table 2, p. 11 | heading 2.8, paragraph 2 (caption) and the table after it | Every step that used a language model, which model, and what was checked: search and ingestion scripts; title-and-abstract screening; full-text screening and adjudication (including the landmark tranche); data extraction and appraisal (Claude Opus 5.5 extractor; Claude Sonnet 5.5 second extractor on 8 sampled and 2 landmark studies; Claude Fable 5.1 adjudicator); census coding and adjudication; design-space table; framework checks; the EXP-003 checkers (Qwen3-VL-2B, CLIP); analysis scripts and figures; drafting and editing of the manuscript. |
| 3 | Section 2.8, paragraph "Human involvement", p. 10 | heading 2.8, paragraph 3 | What humans did and did not do; no screening or extraction decision was made independently by a human. |

## Other places that name the models or their role

| # | PDF | Word file | What it says |
|---|---|---|---|
| 4 | Abstract, p. 1 | front matter, abstract paragraph, last sentence | "Language models screened and extracted studies." |
| 5 | Section 1.6, p. 4 | heading 1.6, paragraph 1 | Search, screening, coding and analysis were AI-assisted; points to Section 2.8. |
| 6 | Section 2.2, run-in "Deduplication and automation filters", p. 5-6 | heading 2.2, paragraph 3 | The single-screener rescue pass was run by Claude Haiku. |
| 7 | Section 2.4 "Selection process and agreement", p. 6-7 | heading 2.4, paragraphs 1 ("Title and abstract"), 2 ("Full text") and 4 ("Human validation") | Screener models in each strand (Claude agent and Codex; Claude Sonnet and Claude Opus; Claude Sonnet 5.5 and Claude Opus 5.5 with Claude Fable 5.1 adjudicating); the safety-classifier stops; the human-validation rule not met. |
| 8 | Section 2.5, run-in "Landmark tranche", p. 7 | heading 2.5, paragraph 1 | The 44 landmark papers screened after the freeze by the same model screeners and adjudicator. |
| 9 | Section 2.6 "Data extraction and quality appraisal", p. 9 | heading 2.6, paragraph 1 (sentences beginning "One extractor (Claude Opus 5.5)") | Extractor, second extractor, adjudicator; the voided session; model readings for the first author to confirm. |
| 10 | Section 2.7 "Census", p. 10 | heading 2.7, paragraph 1 | Two model coders blind to each other; adjudicators. |
| 11 | Section 2.9 "Departures from the protocol", p. 10 | heading 2.9, items 4 and 5 (paragraphs 4 and 5) | Records and fields resolved by the first author confirming a model reading; no independent second screening by a human. |
| 12 | Section 6.2, p. 22 | heading 6.2, paragraph 1 | Codex read failures (tool failures) and their effect on coder agreement. |
| 13 | Section 10, run-in "Screening, extraction and protocol", p. 30 | heading 10, paragraph 2 | Every screening and extraction decision was made by language models; extraction reliability rests on the double-read studies. |
| 14 | Section 10, run-in "Use of AI", p. 31 | heading 10, paragraph 6 | Models of one family did most of the coding, adjudication and drafting, so their errors are likely correlated. |

## In the supplement (the Word file holds the main paper only)

| # | Supplement page | What it says |
|---|---|---|
| 15 | S1, PRISMA checklist items 8 and 9, p. 2 | Selection by two model screeners and a model adjudicator; data collection by model extractors and a validator. |
| 16 | S3.1 "Census method in full", p. 19 | Coder A Claude Sonnet; coder B Codex (gpt-6-luna) and Claude Opus; adjudicators Claude Opus; model versions of the Claude coders not recorded. |
| 17 | S4 "Agreement of the two extractors", p. 21 | Extractors Claude Opus 5.5 and Claude Sonnet 5.5, blind to each other; adjudicator Claude Fable 5.1. |
| 18 | S7, EXP-003 design, p. 34 | The preregistration was reviewed by two Claude agent roles (statistician, red team); no human review recorded. |
