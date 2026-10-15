```yaml
agent: clarity-editor
date: 2026-10-15
brief: Cut paper/review (Paper 1, ACM CSUR) from 38 to at most 35 pages by moving material to paper/review/supplement.tex, clarity-edit every section, verify integrity by diff, compile.
sources_examined: [research/CONTRACT.md, research/review/dossier/csur.md (Part A, lines 36-40 and 149-155), paper/review/OUTLINE.md, paper/review/main.tex, paper/review/sections/01..11, paper/review/tables/design-space-condensed.tex]
coverage: all eleven section files and main.tex read in full; every edit listed below. NOT covered - references.bib (not edited, another agent changed it during the run), figures (not edited), the abstract wording (left unchanged), research/ ledgers (no rows added).
claims:
  - statement: main.pdf is 35 pages (acmsmall, references and acknowledgements included) after the edits; it was 38 before.
    status: supported
    evidence: pdfinfo main.pdf, latexmk -pdf main.tex, 2026-10-15 (log lists zero undefined references, zero errors)
    level: E4
    confidence: 0.95
  - statement: No number, citation key, "% src:" comment, \aud marker, \todo marker, equation, or hedge was lost or changed in the main text plus supplement.
    status: supported
    evidence: scratchpad scripts integ.py, numdiff.py, hedges.py and check_text.py --compare against the copy of the 38-page sources (tables below)
    level: E4
    confidence: 0.9
competing_explanations: []
unknowns: [whether the page count stays at 35 once the citation-validator's pending references.bib changes are built (slack is about 9 lines on page 35)]
next_test: {hypothesis: none, intervention: none, primary_metric: none, falsifier: none, gpu_hours: 0}
```

# Clarity edit and cut to length, Paper 1 (2026-10-15)

## 1. Length rule applied

The CSUR author guidelines ("Paper Length", as recorded in `research/review/dossier/csur.md`, claim at lines 38-40 and the paragraph "Length and supplement" at lines 151-155) allow a long survey of at most 35 pages in the Surveys (acmsmall) style, including references. Extra material may go to an electronic supplement if the manuscript marks which pages form the 35. I applied that rule to `main.pdf` built with `\documentclass[acmsmall]{acmart}`: all 35 pages (title, text, tables, figures, acknowledgements, references) count. The supplement is not counted. The existing `\todo` in Section 1.5 (mark which pages form the 35) is untouched and still needs the author.

## 2. Pages

| State | Pages of main.pdf | Note |
|---|---|---|
| Start | 38 | `main.pdf` as found |
| Table 4 moved | 37 | the longtable was one page, not the larger saving I expected |
| plus EXP-003 deviations and diversity | 36 | |
| plus Memory, "Withdrawn." (7.6), Algorithm 2, refinements paragraph | 36 | last page 31 of about 58 lines |
| plus gap-ruling table | 36 | last page 12 lines |
| plus "What was withdrawn." (7.2) | 35 | last page 55 lines |
| plus EXP-003 control values, screening table, OP3 estimator paragraph, final clarity edits | 35 | last page 51 of about 58 lines |
| `supplement.pdf` | 8 | compiled separately |

The brief's list was exhausted at 36 pages (the OUTLINE's own cut candidates were needed as well), so I moved four further blocks. They are marked in section 3 as "beyond the brief list". Slack on page 35 is about 9 lines, so a few added reference entries would push the paper back to 36.

## 3. What moved where

New file `paper/review/supplement.tex` (own `acmart` document, author-year citations, section numbers S2, S3, S5, S7, S8 so that the S1, S3, S5 and S7 promised in the main text and OUTLINE keep their meaning; S1, S4, S6 and the readme are listed in a `\todo` as not assembled). Cross-references from the supplement to main labels use `scripts/mainrefs.py` (reads `main.aux`, writes `mainrefs.tex`, which is git-ignored). Cross-references from main to supplement tables are the macros `\suppTabScreen`, `\suppTabGap`, `\suppTabDesign` in `main.tex` (Table S1, S2, S3; checked against `supplement.aux`).

Build order: `latexmk -pdf main.tex; python scripts/mainrefs.py; latexmk -pdf supplement.tex`.

| # | Material | From | To | Left in main |
|---|---|---|---|---|
| 1 | Table 4 (condensed design-space longtable) and the code key | 4.2 | S5.1 as Table S3 | one-sentence pointer; the "pilot" caveat about the value-rule column stays; Fig. 3 stays |
| 2 | EXP-003 "Deviations" paragraph (items 1 to 6) | 9.3 | S7.1 | pointer sentence plus the audit finding that no deviation could have been influenced by an outcome; the "single run, outputs not archived" sentence and its `\todo` stay in place |
| 3 | EXP-003 "Diversity" paragraph | 9.2 | S7.2 | pointer; "we make no statement that guidance lowers diversity" stays |
| 4 | Section 7 "Memory" paragraph | 7.4 | S8.3 | two sentences with the "our unchecked inference" hedge |
| 5 | Section 7 "Withdrawn." paragraph | 7.7 | S8.4 | one sentence naming both withdrawn statements as not claimed |
| 6 | Section 3 Algorithm 2 (Generate) | 3.4 | S8.1 as Algorithm S1 | text now points to Algorithm S1 |
| 7 | Section 4 refinements paragraph (four rows that fit) | 4.3 | S8.2 | one sentence; "three features that look like misfits are not" stays |
| 8 | Gap-ruling table (OUTLINE cut candidate) | 6.4 | S3 as Table S2 | the prose reading of it stays |
| 9 | "What was withdrawn." paragraph (beyond the brief list) | 7.2 | S8.4 | first sentence (the two terms), "both are withdrawn (decision D0011) and not claimed", and credit for the sample-then-filter vocabulary kept |
| 10 | EXP-003 NC-1, NC-2, PC-2 values and guardrails (i) to (iv) (beyond the brief list) | 9.2 | S7.3 | statement that NC-1, NC-2, PC-2 and guardrails (i) to (iii) pass and (iv) was not computed by the frozen analysis; PC-1 failure and CLIP non-confirmation stay in full |
| 11 | Screening confusion table (beyond the brief list) | 2.4 | S2 as Table S1 | all counts and kappas in the text; I added to the main text the caption's hedge "agreement between two language-model screeners; it is not agreement with a human" |
| 12 | OP3 cross-modal estimator paragraph (beyond the brief list) | 8.3 | S8.5 | pointer plus the hedge "algebra checked on toy models only" |

Every moved block keeps its `% src:` comment. One provenance comment was added in S7.3 (it cites the original paragraph's comment, which is unchanged in Section 9).

## 4. Integrity check

Method: scratchpad scripts `integ.py` (numbers, `\cite` keys, `% src:` comments, `\aud`, `\todo`, equations, inline math, per file and for main plus sections plus supplement), `numdiff.py` (ordered diff of number tokens), `hedges.py` (hedge phrases), `check_text.py --compare` of the original and revised `main.tex`. The original sources were copied before the first edit.

Main-text sections only (before / after); a drop is moved material, accounted for in section 3:

| Section | Numbers | Cite keys | `% src:` | `\aud` | `\todo` | Equations | Result |
|---|---|---|---|---|---|---|---|
| 1 Introduction | 59 / 59 | 41 / 41 | 23 / 23 | 1 / 1 | 2 / 2 | 0 / 0 | identical in all counts |
| 2 Method | 318 / 298 | 3 / 3 | 57 / 55 | 0 / 0 | 10 / 10 | 0 / 0 | screening table (21 numbers) to S2; two table ranges now "1 to 91", "92 to 176" |
| 3 Notation | 49 / 42 | 48 / 48 | 18 / 18 | 0 / 0 | 0 / 0 | 4 / 4 | Algorithm 2 symbols to S8.1 |
| 4 Design space | 99 / 72 | 16 / 15 | 26 / 25 | 0 / 0 | 0 / 0 | 0 / 0 | Table 4 and refinements to S3, S8.2 |
| 5 RQ evidence | 12 / 12 | 3 / 3 | 6 / 6 | 0 / 0 | 1 / 1 | 0 / 0 | identical (not edited) |
| 6 Census | 298 / 243 | 5 / 5 | 30 / 29 | 2 / 2 | 1 / 1 | 0 / 0 | gap table to S2 |
| 7 Error budget | 88 / 91 | 36 / 32 | 23 / 20 | 1 / 1 | 0 / 0 | 4 / 4 | Memory, both withdrawn blocks to S8; pointers add section numbers |
| 8 Open problems | 64 / 64 | 3 / 3 | 15 / 14 | 2 / 2 | 0 / 0 | 0 / 0 | estimator to S8.5 (0.081 moves) |
| 9 EXP-003 | 271 / 224 | 17 / 16 | 17 / 15 | 0 / 0 | 1 / 1 | 3 / 3 | deviations, diversity, control values to S7 |
| 10 Limitations | 9 / 9 | 0 / 0 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | identical |
| 11 Conclusion | 7 / 7 | 0 / 0 | 3 / 3 | 1 / 1 | 0 / 0 | 0 / 0 | identical |

Main plus supplement against the original:

| Item | Result |
|---|---|
| Numbers | none lost. Two tokens differ only in format (`-91`, `-176`, from "ranks 1--91" to "ranks 1 to 91", house rule for ranges). All other count increases are pointer text (S2, S7.3, Table S3 and so on), the supplement's own title, abstract and headings, and the sentence "28 of the 152" in Section 7 (the same 152 as before, now named twice). |
| Citation keys | identical multiset, except `arXiv:2604.00375`, cited once more (main pointer in 7.2 keeps credit for the sample-then-filter vocabulary) and `acmauthoryear` (a `\citestyle` line in the supplement, not a key). `arXiv:2207.12598` is now cited only in the supplement (S7.2). |
| `% src:` comments | identical, plus two additions in the supplement (file header; S7.3 provenance note). No existing comment was edited. Comment text still says "Table 4" at one place in Section 4 (design-space-v1 note, unchanged by rule); that table is now Table S3. |
| `\aud` | 9 uses unchanged (the count of 10 includes the macro definition in the supplement). |
| `\todo` | all 15 original-section markers unchanged and in place; two added in the supplement (assemble S1, S4, S6 and readme; long form of the design table). |
| Equations and inline math | 11 display equations identical; Algorithm 2 moved verbatim. |
| Hedges | `not confirmed by CLIP` 3, `not detected` 4, `may include quality-mediated coupling` 3, `not measurable with this instrument` 2, `PC-1 failed` 2, `we draw no conclusion`, `we state no share`, `we do not state that the effect is at least [0.10]`, all "We do not claim" items (6) present in main with the same counts. "Not claimed" statements for the U-shaped step dependence and the entropy proposition remain in main as one sentence and in S8.4 in full. |
| ACM AI-use statement and Table `tab:ai` | text unchanged; only two ranges in one cell now read "1 to 91" and "92 to 176", and the cross-reference to the screening table is the macro. |
| Hidden characters | none in `.tex` and `.bib` (zero Cf/Cc code points, no non-breaking spaces or tag characters). |

## 5. Clarity edits (change log)

Argument pass: no claim restructured. Structure pass: long mixed paragraphs split where one paragraph made two points. Sentence pass: sentences split or reordered, filler removed; sentence count over 45 words fell from 56 to 41 (partly because material moved), mean sentence length 24.9 to 23.8 words. Surface pass: no AI-vocabulary hits beyond the file name "landscape file"; no em or en dashes in prose except the conventional compound en dash ("text--image", "key--value", "vision--language"), left as is because the manuscript uses it throughout including the abstract.

| Location | Change | Why |
|---|---|---|
| 1.2, 1.3 | "Its performance study compares ...": semicolon replaced by a sentence break; "That work is not complete, and Section 5 is a stub until it is"; "a reason particular to" | split 85- and 48-word sentences |
| 2.1 | amendment sentence split in three | 71 words |
| 2.3 | inclusion sentence split ("satisfies all of the following") | 81 words |
| 2.4 | "no human decision has been entered"; full-text sentence reworded to "judged only for a random sample of 176 of them" | precision |
| 2.5 | "the extra ranks do not bias the proportions" | clearer subject |
| 2.5 | adjudication sentence split in three | 74 words |
| 2.5 | blindness incident: "We report it as a possible leak" | filler |
| 2.6 | table ranges "1 to 91", "92 to 176", "M01 to M29" | house rule for ranges |
| 3.2, 3.3 | simplex sentence split; two long "restrictions" sentences split | 61 and 87 words |
| 4.3 | "none was left unplaced" | double negative |
| 6.1 | question sentence split | 49 words |
| 6.4, 6.5 | sensitivity sentence split (6.4); diversity sentence split ("This holds even for") and "has been argued for" with a colon list of four citations (6.5) | readability; verb kept at "argued" (not "shown") |
| 7.1 | identity-sources sentence (82 words) split in five; "Second ..." caution split | readability |
| 7.2 | withdrawal reasons split | 67 words |
| 7.7 | census-levers sentence (81 words) split in three | readability, numbers and the `\aud` untouched |
| 8.3 | "The problem has two parts." | fragment |
| 9.2 | question split into two sentences; last sentence of "Checks and controls" split in three | 58 and 53 words |
| 10 | "Second, no human coded it." made its own sentence | readability |
| 11 | "The review makes four contributions." | vague opener |
| 9.2 (coordinator request) | "is the criterion of multimodal VAEs" replaced by "is done as in MMVAE", citation key `arXiv:1911.03393` kept | the one cited paper (MMVAE) does not support a statement about multimodal VAEs in general; this narrows the claim |

Wording not touched on purpose: the abstract (numbers and sentences), the primary-result sentence of Section 9 (its wording is the one permitted by the gate audit EXP-003 section 5), the AI-use statement, all tables other than the ranges noted, all equations.

## 6. Flags for the author

1. Section 6.5 says a reader of "most headline results" cannot tell which value rule produced them, then gives 50 of 153 not stated. That is one third, not most; the 97 stated non-plain results do tell the reader the rule class. I left the claim strength as written; the sentence should be narrowed or the wording "or only that it is non-plain" added.
2. Page slack is about 9 lines on page 35. `references.bib` and `research/ledgers/references.jsonl` were being changed by another agent while I worked; added entries may push the paper to 36 pages.
3. The supplement is a separate `acmart` document with author-year citations and its own bibliography; its table and algorithm numbers (S1 to S3, Algorithm S1) are hard-coded in three macros in `main.tex` and a few "Section S..." strings in the text. Recheck them against `supplement.aux` after any change to the supplement order.
4. Overfull box of 38.7 pt in the AI-use table, row "Measurement in Section 9" (`\texttt{openai/clip-vit-large-patch14}`); I did not edit that row. A line break inside the `\texttt` fixes it.
5. S1 (search strings, PRISMA checklist), S4, S6 and the CSUR readme are still unassembled; the main text promises S1, S3, S5 and S7 and the Section 1.5 `\todo` stays open.
6. Two reference keys are now cited only from the supplement or once in main: `arXiv:2207.12598` (supplement only), `arXiv:2604.00375` (restored in main by the 7.2 pointer).
7. I added no ledger rows (the brief named none); the cut could be recorded as a decision row by the orchestrator.

Diff of main.tex, sections and .gitignore: `research/review/audits/2026-10-15-clarity-paper1.diff` (supplement.tex and scripts/mainrefs.py are new files and are not in the diff). Nothing was committed.
