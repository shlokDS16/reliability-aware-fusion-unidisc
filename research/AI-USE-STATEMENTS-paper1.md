# Where the paper states its use of AI (Paper 1, version of 2026-10-21, after fixes A-D and the author checks)

PDF pages are those of `paper/review/main.pdf` (35 pages) and `paper/review/supplement.pdf` (43 pages), checked on
2026-10-21 after the author checks were added (decisions D0065, D0066). In the Word file
`paper/review/docx/main.docx` find the same text by section heading and paragraph number (paragraphs counted under
each heading; a bold run-in title such as "Full text." starts inside a paragraph).

## The required ACM statement (AI used to conduct research must be described in the Methods section)

| # | PDF | Word file | What it says |
|---|---|---|---|
| 1 | Section 2.8 "Use of AI in conducting the research", p. 10 | heading 2.8, paragraph 1 | ACM's authorship policy requires the description; all authors are responsible; no language model is an author; no screener, extractor or coder is presented as a human reviewer. |
| 2 | Table 2, p. 11 | heading 2.8, paragraph 2 (caption) and the table after it | Every step that used a language model, which model, and what was checked: search and ingestion scripts; title-and-abstract screening; full-text screening and adjudication (now checked by a blind author check of 40 records); data extraction and appraisal (Claude Opus 5.5 extractor; Claude Sonnet 5.5 second extractor on 8 sampled and 2 landmark studies; Claude Fable 5.1 adjudicator); census coding and adjudication; design-space table; framework checks; the EXP-003 checkers (Qwen3-VL-2B, CLIP); **author checks of screening, extraction and census samples: ChatGPT (OpenAI; version not recorded), used by the first author to validate the author's own answers, with no access to the project files or the model answers**; analysis scripts and figures; drafting and editing of the manuscript. |
| 3 | Section 2.8, paragraph "Human involvement", p. 10 | heading 2.8, paragraph 3 | What humans did: the unrecorded reading of the T1 sample; the blind author checks validated with ChatGPT; the first author's confirmations (four records, nine fields, three code links, twelve adjudicator items). The checks changed no decision; every screening and extraction decision used was made by a model. |

## Other places that name the models or their role

| # | PDF | Word file | What it says |
|---|---|---|---|
| 4 | Abstract, p. 1 | front matter, abstract paragraph, last sentence | "Language models screened and extracted studies." |
| 5 | Section 1.6, p. 4 | heading 1.6, paragraph 1 | Search, screening, coding and analysis were AI-assisted; points to Section 2.8. |
| 6 | Section 2.2, run-in "Deduplication and automation filters", p. 5-6 | heading 2.2, paragraph 3 | The single-screener rescue pass was run by Claude Haiku. |
| 7 | Section 2.4 "Selection process and agreement", p. 6-7 | heading 2.4, paragraphs 1 ("Title and abstract"), 2 ("Full text") and 4 ("Human validation") | Screener models in each strand (Claude agent and Codex; Claude Sonnet and Claude Opus; Claude Sonnet 5.5 and Claude Opus 5.5 with Claude Fable 5.1 adjudicating); the safety-classifier stops; the human-validation rule not met; **the three blind author checks validated with ChatGPT and their agreement (screening kappa 0.41, extraction 0.82, census 0.79)**. |
| 8 | Section 2.5, run-in "Landmark tranche", p. 7 | heading 2.5, paragraph 1 | The 44 landmark papers screened after the freeze by the same model screeners and adjudicator. |
| 9 | Section 2.6 "Data extraction and quality appraisal", p. 9-10 | heading 2.6, paragraph 1 (sentences beginning "One extractor (Claude Opus 5.5)") | Extractor, second extractor, adjudicator; the voided session; code-link readings and twelve adjudicator items, all confirmed by the first author. |
| 10 | Section 2.7 "Census", p. 10 | heading 2.7, paragraph 1 | Two model coders blind to each other; adjudicators. |
| 11 | Section 2.9 "Departures from the protocol", p. 11-12 | heading 2.9, items 4 and 5 (paragraphs 4 and 5) | Screening not validated by a human as planned; the later author check validated with ChatGPT (kappa 0.41, below the protocol's 0.70, no prompt revised); records and fields resolved by the first author confirming a model reading. |
| 12 | Section 6.2, p. 22 | heading 6.2, paragraph 1 | Codex read failures (tool failures) and their effect on coder agreement. |
| 13 | Section 6.6 "Limits of the census", p. 23 | heading 6.6, paragraph 1 | No human coded the sample; the blind author check of 24 papers validated with ChatGPT (kappa 0.79); coders, adjudicators and harmoniser are language models. |
| 14 | Section 10, run-in "Screening, extraction and protocol", p. 31 | heading 10, paragraph 2 | Every screening and extraction decision was made by language models; the author check validated with ChatGPT is not an independent human-only check and agreed at kappa 0.41; extraction reliability rests on the double-read studies. |
| 15 | Section 10, run-in "The census", p. 31 | heading 10, paragraph 3 | Coded by models; blind author check of 24 papers validated with ChatGPT (kappa 0.79). |
| 16 | Section 10, run-in "Use of AI", p. 32 | heading 10, paragraph 6 | Models of one family did most of the coding, adjudication and drafting, so their errors are likely correlated. |

## In the supplement (the Word file holds the main paper only)

| # | Supplement page | What it says |
|---|---|---|
| 17 | S1, PRISMA checklist items 8 and 9, p. 2 | Selection by two model screeners and a model adjudicator; planned human validation not done, later blind author check validated with ChatGPT (S9); data collection by model extractors and a validator. |
| 18 | S3.1 "Census method in full", p. 18 | Coder A Claude Sonnet; coder B Codex (gpt-6-luna) and Claude Opus; adjudicators Claude Opus; model versions of the Claude coders not recorded. |
| 19 | S3.4 "Limits of the census, in full", p. 21 | No human coded the sample; blind author check of 24 papers validated with ChatGPT. |
| 20 | S4 "Agreement of the two extractors", p. 21-22 | Extractors Claude Opus 5.5 and Claude Sonnet 5.5, blind to each other; adjudicator Claude Fable 5.1. |
| 21 | S7, EXP-003 design, p. 34 | The preregistration was reviewed by two Claude agent roles (statistician, red team); no human review recorded. |
| 22 | S9 "Author checks of screening, extraction and census", p. 38 | How the three samples were drawn; ChatGPT (OpenAI) used by the first author to validate the answers, with no access to the project files or model answers; Table S12 of agreement; the disagreements. |
