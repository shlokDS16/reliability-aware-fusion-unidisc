# Where the paper states its use of AI (Paper 1, version of 2026-10-21, declaration-only layout, D0067)

PDF pages are those of `paper/review/main.pdf` (35 pages) and `paper/review/supplement.pdf` (48 pages), checked on
2026-10-21 after the AI description moved into a declaration (decision D0067). In the Word file
`paper/review/docx/main.docx` find the same text by heading.

Decision D0067 (the user's words): "Just mention in short in the declaration only. Remove the ai part from all other
parts of the paper." Risk recorded there: ACM's authorship policy asks for AI used to conduct research to be
described in the Methods section; the authors will follow reviewer or editor guidance if asked.

## The declaration

| # | PDF | Word file | What it says |
|---|---|---|---|
| 1 | "Declaration on the use of AI", p. 31, unnumbered, after "Data and code availability" and before the references | heading "Declaration on the use of AI" | AI tools did the screening, extraction, census coding and adjudication, and assisted with scripts, figures, drafting and editing; no AI system is an author; the authors take full responsibility. Names: Claude agent and Codex (gpt-6-luna) for seed title-and-abstract screening; Claude Sonnet and Claude Opus for the update and subscription strands; Claude Haiku for the rescue pass; Claude Sonnet 5.5 and Claude Opus 5.5 as full-text screeners, Claude Fable 5.1 as adjudicator; Claude Opus 5.5 extractor, Claude Sonnet 5.5 second extractor, Claude Fable 5.1 adjudicator; census coders Claude Sonnet, Codex and Claude Opus, adjudication and harmonisation Claude Opus 5.5; Claude models in Claude Code for design-space readings, framework checks, scripts and text; Qwen3-VL-2B-Instruct and CLIP ViT-L/14 as EXP-003 checkers. The checks made, and that the first author's blind checks were validated with ChatGPT (OpenAI), which had no access to the project files or the model answers. Models of one family did most of the work, so their errors are likely correlated. |

## Pointers in the main text (no model names, so readers do not think humans screened)

| # | PDF | What it says |
|---|---|---|
| 2 | Section 2.4 "Title and abstract", p. 6 | "Two automated screeners (see the Declaration on the use of AI)". |
| 3 | Section 2.4 "Human validation", p. 7 | The first author's three blind checks, "validated as described in the Declaration on the use of AI", with kappa 0.41, 0.82 and 0.79. |
| 4 | Section 2.6, p. 10 | "One automated extractor"; code-link and adjudicator items read automatically and confirmed by the first author. |
| 5 | Section 2.7, p. 10 | "Two automated coders, blind to each other". |
| 6 | Section 2.8 "Departures from the protocol", items 4 and 5, p. 11 | Screening not validated by a human as planned; the later author check (kappa 0.41, below 0.70); fields resolved by the first author confirming an automated reading. |
| 7 | Section 6.6 "Limits of the census", p. 23 | The coders, adjudicators and harmoniser are automated tools, mostly of one model family. |
| 8 | Section 9, p. 29 | The Qwen3-VL-2B checker, a measurement instrument of EXP-003 (kept: it is part of that method). |
| 9 | Section 10 "Screening, extraction and protocol" and "The census", p. 30 | Every screening and extraction decision was automated; the author check is AI-validated and not an independent human-only check. |

## In the supplement (detailed method record; model names kept, D0067)

| # | Supplement page | What it says |
|---|---|---|
| 10 | Title, p. 1 | "Electronic supplement. Not part of the 35 pages under review". |
| 11 | S1, PRISMA checklist items 8 and 9, p. 2 | Model screeners and adjudicator; planned human validation not done; later blind author check validated with ChatGPT (S9). |
| 12 | S3.1 "Census method in full", p. 18 | Coder A Claude Sonnet; coder B Codex (gpt-6-luna) and Claude Opus; adjudicators Claude Opus. |
| 13 | S3.4 "Limits of the census, in full", p. 21 | No human coded the sample; blind author check of 24 papers validated with ChatGPT. |
| 14 | S4 "Agreement of the two extractors", p. 21-22 | Extractors Claude Opus 5.5 and Claude Sonnet 5.5; adjudicator Claude Fable 5.1. |
| 15 | S7, EXP-003 design, p. 36 | The preregistration was reviewed by two Claude agent roles; no human review recorded. |
| 16 | S9 "Author checks of screening, extraction and census", p. 40 | How the samples were drawn; ChatGPT used by the first author to validate the answers; Table S12. |
