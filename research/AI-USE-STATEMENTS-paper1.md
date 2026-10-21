# Where the paper states its use of AI (Paper 1, version of 2026-10-21)

Page numbers are those of `paper/review/main.pdf` (35 pages) and `paper/review/supplement.pdf` (42 pages), re-checked
on 2026-10-21 after fix D (landmark tranche: screening, extraction of 16, Section 5 landmark column; decisions
D0061-D0064). The Word file
(`paper/review/docx/main.docx`) has the same sections and headings, so the section numbers below find the same text there.

## The required statement (ACM policy: AI used to conduct the research must be described in the Methods section)

| # | Where | What it says |
|---|---|---|
| 1 | **Section 2.8 "Use of AI in conducting the research"**, p. 10 | ACM's authorship policy requires AI use to be described in Methods; all authors remain responsible; no language model is an author; no screener, extractor or coder is presented as a human reviewer. |
| 2 | **Table 2**, p. 11 (inside Section 2.8) | Every step that used a language model, the model, and what was checked: search and ingestion scripts (Claude Code); title-and-abstract screening (Claude agent, Codex gpt-6-luna, Claude Sonnet, Claude Opus, Claude Haiku); full-text screening and adjudication (Claude Sonnet 5.5, Claude Opus 5.5, Claude Fable 5.1); data extraction and appraisal (Claude Opus 5.5, Claude Sonnet 5.5 on 8 and on 2 landmark studies, Claude Fable 5.1 adjudicating those 10); census coding (Claude Sonnet; Codex gpt-6-luna and Claude Opus); census adjudication and codebook (Claude Opus 5.5); design-space table (Claude reading agents); framework and derivation checks (Claude, Claude red-team); the EXP-003 measurement's checkers (Qwen3-VL-2B-Instruct, CLIP); analysis scripts, figures, tables (Claude Code); drafting and editing of the manuscript (Claude manuscript and clarity agents). |
| 3 | **Section 2.8, paragraph "Human involvement"**, p. 10 | What humans did and did not do: the T1 validation sample was read without recorded decisions; the first author confirmed model readings for 4 records, 9 fields and 3 code links; no screening or extraction decision was made independently by a human. |

## Other places that say which model did what

| # | Where | What it says |
|---|---|---|
| 4 | **Abstract**, p. 1 | "Language models screened and extracted studies." |
| 5 | **Section 1.6 "How the work was done, and how to read the paper"**, p. 4 | Search, screening, coding and analysis were AI-assisted; points to Section 2.8. |
| 6 | **Section 2.2 "Information sources and searches"**, p. 6 | The single-screener rescue pass was run by Claude Haiku. |
| 7 | **Section 2.4 "Selection process and agreement"**, p. 6-7 | Seed strand: Claude agent and Codex (gpt-6-luna); update and subscription strands: Claude Sonnet and Claude Opus; full text: Claude Sonnet 5.5 and Claude Opus 5.5 with Claude Fable 5.1 as adjudicator; screener B's sessions stopped on a safety classifier for four biology papers and those rows were discarded; the protocol's human-validation rule was not met. |
| 8 | **Section 2.6 "Data extraction and quality appraisal"**, p. 7-10, with the paragraph "Landmark tranche" of Section 2.5 on p. 7 | Extractor Claude Opus 5.5, second extractor Claude Sonnet 5.5 on 8 studies, adjudicator Claude Fable 5.1; one adjudication session voided and re-run; three code-link cases settled by a model reading for the first author to confirm; twelve adjudicator items await the first author. The landmark tranche was screened by the same two model screeners and 16 of its studies extracted the same way, with a second extractor and adjudicator on 2. |
| 9 | **Section 2.7 "Census: sampling, coding and adjudication"**, p. 10 | Two model coders, blind to each other, and adjudicators applying codebook v1.2. |
| 10 | **Section 2.9 "Departures from the protocol"**, p. 10-12 | Items 4 and 5: records and fields resolved by the first author confirming a model reading, not by an independent second screening; item on the verdict thresholds written after the results. |
| 11 | **Section 6.2 "Agreement between the two coders"**, p. 21 | Codex read failures (tool failures) and their effect on agreement. |
| 12 | **Section 6.6 "Limits of the census"**, p. 24 | No human coded the sample; coders, adjudicators and harmoniser are language models, mostly of one family. |
| 13 | **Section 10, paragraph "The measurement on a frozen model"**, p. 31 (the detail is in supplement S7.6, item 19) | No human reviewed the EXP-003 preregistration. |
| 14 | **Section 10 "Threats to validity and limitations"**, p. 30-31, paragraphs "Screening, extraction and protocol" and "Use of AI" | Every screening and extraction decision was made by language models; extraction reliability rests on 8 studies; models of one family did most of the coding, adjudication and drafting, so their errors are likely correlated and most checks are by models of the same family. |

## In the supplement

| # | Where | What it says |
|---|---|---|
| 15 | **S1, PRISMA checklist**, items 8 and 9, p. 2 | Selection by two model screeners and a model adjudicator; data collection by one model extractor, a second on 8 (and on 2 landmark studies), and a validator; the landmark tranche screened the same way. |
| 16 | **S3.1 "Census method in full"**, p. 18-19 (coder roles on p. 19) | Coder A Claude Sonnet; coder B Codex (gpt-6-luna) and Claude Opus; adjudicators Claude Opus; exact model versions of the Claude coders not recorded; one possible leak between coders' workspaces. |
| 17 | **S3.4 "Limits of the census, in full"**, p. 20 | No human coded the sample; the two systems behind coder B; Codex read failures. |
| 18 | **S4 "Agreement of the two extractors"**, p. 21-22 | Extractors Claude Opus 5.5 and Claude Sonnet 5.5, each blind to the other; adjudicator Claude Fable 5.1. |
| 19 | **S7.6 "Question, results and reading in full"**, paragraph "Question and design", p. 34 | The EXP-003 preregistration was reviewed by Claude agent roles (statistician, red team); no human review recorded (moved from the former Section 9.1). |

## Before submission

- If you complete the blind 12-study check, Section 2.8 ("Human involvement"), Section 10 and S4 will report it, and
  item 3 above will change.
- ACM also allows naming non-author helpers in the acknowledgements; the paper currently has a placeholder there.
