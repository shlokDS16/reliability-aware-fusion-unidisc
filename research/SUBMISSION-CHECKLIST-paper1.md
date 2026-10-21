# Paper 1 submission checklist (ACM Computing Surveys), state on 2026-10-21

Manuscript: `paper/review/main.pdf` (35 pages including references, the CSUR limit; abstract 98 words, limit 100;
body about 18,900 words and references about 2,600 words, CSUR sets no word limit) and its Word version
`paper/review/docx/main.docx` (same text, numbering of sections, tables, figures, equations and citations as the PDF;
no line or page numbers; built by `paper/review/scripts/make_docx.py`), and `paper/review/supplement.pdf`
(37 pages, electronic supplement). Sources in `paper/review/`. Every AI-use statement is listed with its page in
`research/AI-USE-STATEMENTS-paper1.md`.
Release folder (local, not uploaded): `C:\Users\Shlok\Downloads\Multi-Modality Language model\release\dlm-review-prisma-v1`
(2,472 files, 185 MB, abstracts stripped, secret scan clean, MANIFEST.sha256).

## Done (with the record)

| Item | Record |
|---|---|
| Screening frozen, PRISMA flow and checklist | D0051; supplement S1; Figure 1 |
| Extraction of 80 studies, second reader on 8, adjudication | analysis/extraction/d0052/ (EA, EB, EC; one voided session re-run) |
| Primary estimates on included studies, seed apart, stated verdicts | D0060; Section 5; supplement S6 |
| Gate audit, red-team, re-audit | research/review/audits/2026-10-21-gate-section5*.md, -redteam-section5.md |
| Citation gate (68 references) | research/review/audits/2026-10-21-citations-paper1.md |
| Census numbers re-verified from raw rows | research/review/audits/2026-10-21-census-reverify.md (PASS) |
| Clarity edit, numbers and citations unchanged | research/review/audits/2026-10-21-clarity-section5.md |
| Page limit, AI-use statement, data availability statement | main.pdf; Section 2.8, Table 2 |

## Only you can do these (in this order)

1. **Author checks**: `research/AUTHOR-CHECKS-2026-10-21.md` part 1 (12 yes/no, about 25 min) and part 2, the blind
   12-study check in `research/HUMAN-CHECK-2026-10-21.xlsx` (1.5 to 2 h). Tell me when done; I report the agreement
   in Section 2 and supplement S4. Without part 2 the paper says no human check of the extraction was recorded.
2. **Front matter**: ORCIDs of the three authors; who is the corresponding author; the funding statement and any
   acknowledgements (the paper shows a red to-do there).
3. **GitHub and Zenodo** (`research/RELEASE-GUIDE-paper1.md`): you create the repository yourself (decided
   2026-10-21) and upload the release folder; make it public, connect Zenodo, publish release v1.0.0, then send me the
   GitHub link and the DOI. I put both into the data availability statement in the PDF and the Word file (both are
   highlighted placeholders now).
4. **Final read-through** of main.pdf by the authors (ACM: all authors are responsible for the content).
5. **Submit** through the CSUR system (Manuscript Central): main.pdf, supplement.pdf as supplementary material, the
   LaTeX sources if asked, the AI-use statement is in Section 2.8.

## Known limits a referee will see (all stated in the paper)

Screening frozen before the seed corpus was assessed; no independent human screening or extraction (unless part 2
is done); extraction on a stratified sample of 59 included studies with structural agreement below the plan's line on
the 8 double-read studies; verdict thresholds and estimator chosen after the results; census coded by language models.
