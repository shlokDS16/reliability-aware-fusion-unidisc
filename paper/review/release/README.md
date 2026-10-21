# Diffusion Language Models and Unified Multimodal Generation: data and code of a critical systematic review

This repository holds the data, code and manuscript sources behind the review "Diffusion Language Models and Unified
Multimodal Generation: A Critical Systematic Review of Discrete and Continuous Approaches" (Shlok Goenka,
Subramaniyaswamy Vairavasundaram, Balaji G N; School of Computer Science and Engineering, Vellore Institute of
Technology). The review follows PRISMA 2020. Every number in the paper carries a `% src:` comment in the LaTeX source
naming the file it comes from.

Archived version: DOI pending (Zenodo).

## What is here

| Path | Contents |
|---|---|
| `paper/review/` | LaTeX sources of the paper and the supplement, figure and table scripts (`scripts/`), generated tables (`tables/`), figures, and the compiled `main.pdf` and `supplement.pdf` |
| `research/review/protocol.md` and `research/review/` | protocol, eligibility criteria, screening rows of both screeners and the adjudicator, extraction form (v0.5) and plans, census codebooks and tables, audits, feasibility notes |
| `research/review/corpus/` | identified records (ids, titles, authors, years, venues, identifiers) and the search log with every query and export checksum; abstracts removed |
| `research/ledgers/` | decision ledger (one row per decision, D0001 onwards) and other ledgers |
| `analysis/prisma/` | PRISMA flow counts (`prisma_flow.py`, `prisma-flow.json`) |
| `analysis/rq1/` | RQ1 counts over all 615 included studies |
| `analysis/extraction/d0052/` | stratified extraction sample: extractor records (EA, EB), adjudicated records (EC), validator reports, agreement on the double-read studies, the RQ analysis (`rq_analysis.py` -> `rq-results.json`, block `D0060` holds the reported estimates), QA1 link check, sensitivity analyses |
| `analysis/census/`, `research/review/census/` | value-rule census of a random sample of the seed corpus |
| `runs/EXP-003/analysis/` | outputs of the preregistered measurement on UniDisc (Section 9) |
| `tools/` | search, screening dispatch, extraction dispatch and validation tools |

## Reproducing the reported numbers

Python 3.14 with numpy and openpyxl; LaTeX with latexmk.

    python -E -P analysis/extraction/d0052/rq_analysis.py        # RQ2-RQ6 estimates (rq-results.json)
    python -I paper/review/scripts/qa_tables.py                   # appraisal and sensitivity tables
    python -I paper/review/scripts/agreement_table.py             # extractor agreement tables
    python -I analysis/prisma/prisma_flow.py                      # PRISMA counts
    cd paper/review && latexmk -pdf main.tex && python -I scripts/mainrefs.py && latexmk -pdf supplement.tex && python -I scripts/supprefs.py && latexmk -pdf main.tex

The screening and extraction themselves were run by language models in isolated sessions (Section 2.8 and Table 2 of
the paper); their outputs are included, the full texts they read are not.

## What is not here, and why

- Full texts and PDFs of the reviewed papers, and the HTML texts read for the census: copyright of the publishers and
  authors. Every record carries an identifier (arXiv id, DOI or OpenReview id) from which the text can be retrieved.
- Raw exports of the subscription databases: their licence terms.
- Images generated in the EXP-003 measurement: UniDisc states no licence.

## Licences

Code: MIT (`LICENSE`). Data, tables, manuscript text and figures: CC BY 4.0 (`LICENSE-DATA`).

## Use of AI

Language models screened, extracted and coded the studies and drafted parts of the manuscript under the authors'
direction; the paper's Section 2.8 and Table 2 list each step, the model and what was checked. The authors are
responsible for the content.
