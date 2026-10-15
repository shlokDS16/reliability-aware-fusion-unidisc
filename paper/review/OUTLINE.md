# Paper 1 outline: critical systematic review for ACM Computing Surveys (draft v1, 2026-10-15)

Working title (D0007): *Diffusion Language Models and Unified Multimodal Generation: A Critical
Systematic Review of Discrete and Continuous Approaches*. "and Meta-Analysis" is NOT in the title:
the pooling threshold of protocol section 7 is not met on current evidence
(`research/review/feasibility/stage2/summary-*.md`). PLAN.md sections 3 and 4 still describe the
older D0006 title and "meta-analytic estimates"; they are out of date (see Contradictions in the
hand-back).

Format: `acmart`, `acmsmall`, `\acmJournal{CSUR}`, single column, 6.75 x 10 in, about 600 words
per page of running text, about 30 references per page (`research/review/dossier/csur.md` Part A;
`dossier/exemplar-anatomy.md` section 4). Hard limit 35 pages including references; anything
beyond goes to the marked electronic supplement. Abstract at most 100 words.

Contribution labels (D0011, `research/review/framework-v2.md` section D):
**C1** design space in one notation tested on 47 models; **C2** value-rule census (random sample,
`coverage/census-result-v2.md`; numbers marked `\todo{audit}` until the gate audit
`audits/2026-10-15-gate-census-v2.md` is applied); **C3** the error budget as a taxonomy;
**C4** open problems with the evidence each needs. Not claimed: the "Not claimed" paragraph of
framework-v2 section D.

## 1. Section map and page budget

Total 34.0 pages including 8.0 of references, 0.5 front matter, 1.0 slack.

| # | Section | Pages | Carries | Status in this draft |
|---|---|---|---|---|
| 0 | Title, abstract (100 words), CCS, keywords | 0.5 | all | draft abstract with `\todo` |
| 1 | Introduction | 2.5 | all (states C1-C4, RQ1-RQ6, not-claimed) | drafted |
| 2 | Review method (PRISMA 2020, screening, census coding, AI-use statement) | 3.0 | C2 (method), all (transparency) | drafted; gaps are `\todo` |
| 3 | A unified notation (C1-C5, symbols, two short algorithms) | 2.0 | C1, C3 | stub |
| 4 | The design space, tested on 47 models | 4.5 | C1 | stub |
| 5 | What the evidence shows, by research question (RQ2, RQ3, RQ4, RQ5) | 3.5 | RQ answers, C4 inputs | stub |
| 6 | A census of value rules and reporting | 3.5 | C2 | drafted |
| 7 | The error budget as a taxonomy | 3.0 | C3 | stub |
| 8 | Open problems and the evidence each needs | 2.0 | C4 | stub |
| 9 | A targeted measurement on a frozen unified model (EXP-003) | 0.75 | supports C2 reading | placeholder only |
| 10 | Threats to validity and limitations | 0.75 | all | stub |
| 11 | Conclusion | 0.5 | all | stub |
| - | References (about 240 entries) | 8.0 | | `references.bib` started |
| | **Total** | **34.0** | | |

Electronic supplement (marked in the manuscript; not counted in the 35): S1 full search strings
and the PRISMA 2020 checklist; S2 per-record screening table; S3 census codebooks v1, v1.1, v1.2
and the 176-row final table; S4 field-level agreement tables and the disagreement list; S5 the
47-model design-space table in full; S6 per-study extraction and quality-appraisal tables; S7
EXP-003 detail if it enters.

## 2. Paragraph-level evidence map

Every number in a drafted section carries `% src: <path>` in the LaTeX source. "Feeds" lists the
files a paragraph is allowed to use.

### 1 Introduction
| Paragraph | Feeds |
|---|---|
| Motivation: growth of DLMs and unified discrete-diffusion models; comparability problem | `review/feasibility-inventory.md` (year counts of the 540-record seed), primers `dossier/primer-foundations.md`, `primer-multimodal.md` (model names, IDs), `survey-landscape.md` section 1c (evaluation critiques, E1) |
| Existing reviews and what they lack | `survey-landscape.md` section 1a (E2 flags), `dossier/competitor-anatomy.md` sections 1 to 3, protocol section 8 |
| Research questions RQ1-RQ6 and where each is answered | `review/protocol.md` section 1; `feasibility/stage2/summary-steps.md`, `summary-remask-synergy.md` for what can be pooled |
| Contributions with honest credit | decisions D0011, D0019; `framework-v2.md` sections A and D; `dossier/prior-art-selection.md` (2605.12522, 2510.04525, 2609.34509, 2401.01879) |
| Not claimed; reading guide | `framework-v2.md` section D "Not claimed"; this outline |

### 2 Review method
| Subsection | Feeds |
|---|---|
| 2.1 Design, reporting standard, protocol status (not frozen; no registration) | `review/protocol.md` header, freeze rule and section 10; `git tag` list (empty); `dossier/csur.md` section 2 |
| 2.2 Sources, strings, dates | `corpus/search-log.jsonl`, `tools/search_arxiv.py`, `corpus/awesome-dlms@194aa6bd.jsonl`, `protocol.md` section 3, `screening/dedup-report.json` |
| 2.3 Eligibility and exclusion codes | `protocol.md` section 2 and section 10 amendment; `screening/criteria-v1.md` |
| 2.4 Screening and agreement | `screening/screener-A`, `screener-B`, `screener-B/run-log.jsonl`, `tools/screening_agreement.py` (rerun 2026-10-15: kappa 0.728 pass/exclude, 0.673 three-way), `screening/disagreements.csv`, `dedup-addendum.md` |
| 2.5 PRISMA flow (Fig 1) | same files; flow generated by script (figure-smith) |
| 2.6 Census: pool, random order, stopping rule, coders, fields, codebooks | `tools/census_sample.py`, `census/census-order.csv`, `census/CLAUDE-CODER-BRIEF.md`, `coverage/census-codebook-v1.md`, `-v1.1.md`, `-v1.2.md`, `census/coder-B-run-log.jsonl`, decisions D0015, D0019, D0020 |
| 2.7 Adjudication and harmonisation | `census/adjudication-notes-r001-r088.md`, `-r089-r176.md`, `harmonisation-notes.md`, `census-random-final.jsonl` |
| 2.8 Blindness incident | decision D0019 item 2 |
| 2.9 Use of AI in the research (ACM policy) | `dossier/csur.md` section 3; run logs above; `research/progress.md` for the roster |
| 2.10 Deviations from the protocol | `protocol.md` section 6 (evaluability block, suspended: D0008, D0009), `PLAN.md` section 6 gate R1 vs `corpus/search-log.jsonl` |

### 3 A unified notation (stub)
Feeds: `framework-v1.md` section 1 (C1-C5 table, with v2 corrections), `dossier/primer-foundations.md`
section 0.1 and 2, `primer-gaussian.md` section 1, `primer-multimodal.md` section 1. Items:
symbol table (Table 3), Fig 2 (formalism diagram), Alg 1 (training objective in one notation), Alg
2 (generic commit-kernel sampler). Equations at most 8 here.

### 4 Design space on 47 models (stub, C1)
Feeds: `coverage/design-space-v1.md` and `.csv` (47 rows; 36 fit, 11 partly, 0 no; misfit list
section 3), `framework-v1.md` section 3 (lever rows L1-L14), `dossier/competitor-anatomy.md` section
3 (what the two surveys do and do not have). Items: Fig 3 taxonomy tree; Table 4 condensed design
table (47 rows x C1-C5, long form in the supplement); misfit paragraph = the framework's stated
limits. Caveat to state: rows M01-M29 were copied from the primers, not re-read (E2, confidence 0.6).

### 5 Evidence by research question (stub)
Feeds: `feasibility-inventory.md` (caption signals, E1), `feasibility/stage2/summary-steps.md`
(RQ4, E2), `summary-remask-synergy.md` (RQ3, RQ5, E1), `survey-landscape.md` section 2 (synergy
claims and what task-removal ablations exist), `pilot/`, `reliability/RESULTS.md` only for the
note that the evaluability rubric was dropped. Verdict vocabulary: well supported, mixed, weakly
supported, untested (`protocol.md` section 7). RQ2 has no contrast table yet. Needs the full
extraction (gate R2) before this section can be written; do not write verdicts from the stage-2
samples.

### 6 Census (drafted, C2)
Feeds: `coverage/census-result-v2.md` (all numbers), `analysis/census/agreement-random.log`,
`agreement-random-excl-readfail.log`, `summary-random.log`, scripts `agreement_random.py` and
`summary_random.py`, `coverage/census-codebook-v1.2.md` (letter definitions B-15, B-10),
`census/harmonisation-notes.md` (reading 2, reading 5), decisions D0019 and D0020. Table 5 main
result (final and sensitivity), Table 6 agreement before reconciliation, Fig 4 dot plot with Wilson
intervals, Fig 5 letter counts (could be a panel of Fig 4). The earlier 47-model purposive result
(`coverage/census-result-v1.md`) is mentioned once, as a pilot, not as evidence.

### 7 Error budget (stub, C3)
Feeds: `framework-v2.md` sections A to C, `method/selection-term.md` (Thm 1), `framework-v1.md`
sections 2.1, 2.2, 2.5, 3, `dossier/primer-samplers.md`, `dossier/prior-art-selection.md`,
`audits/2026-10-14-red-team-selection-term.md`. Items: the identity (Eq. 1) credited to its source;
V as one signed slot; G and E_approx; lever table (Table 7); what each paper reports about each
lever; P1, P3 as corollaries. Withdrawn items stay listed as withdrawn.

### 8 Open problems (stub, C4)
Feeds: `framework-v2.md` section D4 and E, `conjectures.md`, `dossier/prior-art-2605.12522-
experiments.md`, `survey-landscape.md` section 2 (CB prior statements). Each problem: statement,
evidence now (with level), the measurement that would settle it, what would refute it. Fig 6 map,
Table 8.

### 9 EXP-003 (placeholder)
No result may appear. Wording rules: `research/preregistration/EXP-003-value-rule-consistency.md`
section 10, decision D0019 (novelty limits: CO2Jump 2607.13188, UniDisc 2503.20853, MUNITE
2610.09866). Included only if the frozen analysis and the gate audit are complete.

### 10-11 Limitations and conclusion (stubs)
Feeds: census Limits; protocol status; screening human validation pending; arXiv-only search;
preprint-versus-published; closed models; E3 (code) never checked.

## 3. Figures and tables for figure-smith

Main text: 6 figures, 6 tables, at most 2 algorithms, at most 12 numbered equations. Everything
else goes to the supplement. Each figure is built from a script that reads the cited file; none
may carry a number typed by hand.

| ID | Type | Content | Source file(s) | Section | Main/supp |
|---|---|---|---|---|---|
| Fig 1 | flow diagram | PRISMA 2020: 1903 records identified (572 + 1158 + 173), 450 duplicates, 1453 screened, 210 both exclude, 120 disagreements (unresolved), 1123 pass both, 1106 with arXiv ID (census pool), 176 sampled, 167 eligible, 153 with a value-rule code (152 with a generated-sample metric, 1 samples-only; census-result-v2.md at commit 8dd2af3). Build the box counts by script from `screening/` and `census-random-final.jsonl`. Human-validation and full-text stages shown as "not yet done" | `screening/dedup-report.json`, `tools/screening_agreement.py` output, `census/census-random-final.jsonl`, `analysis/census/summary-random.log` | 2 | main |
| Fig 2 | diagram | commit-kernel formalism (state, C1-C5) | `framework-v1.md` section 1 | 3 | main |
| Fig 3 | tree | master taxonomy, leaves carry citations | `coverage/design-space-v1.csv`, `framework-v1.md` section 3 | 4 | main |
| Fig 4 | dot plot | census proportions, Wilson 95 percent intervals, final vs sensitivity, with letter counts as second panel | `analysis/census/summary-random.log`, `summary_random.py` | 6 | main |
| Fig 5 | timeline/histogram | included records by first-version year and group (screened pool and seed) | `screening/records.jsonl`, `feasibility-inventory.md` | 1 or 2 | main (optional, if pages allow) |
| Fig 6 | map | open problems: each problem against the evidence it needs | `framework-v2.md` D4, E | 8 | main |
| Tab 1 | table | search sources, strings, dates, hits, SHA-256 | `corpus/search-log.jsonl` | 2 | main |
| Tab 2 | table | screening agreement, confusion table A vs B | `tools/screening_agreement.py` | 2 | main |
| Tab 3 | table | symbols | `framework-v1.md` | 3 | main |
| Tab 4 | table | condensed design-space table, 47 models | `design-space-v1.csv` | 4 | main (long form S5) |
| Tab 5 | table | census main result, final and sensitivity | `census-result-v2.md` | 6 | main |
| Tab 6 | table | census agreement before reconciliation | `agreement-random.log` | 6 | main |
| Tab 7 | table | lever table: lever, term lowered, what it pays, papers that use it | `framework-v2.md` B, `framework-v1.md` section 3 | 7 | main |
| Tab 8 | table | open problems and evidence needed | `framework-v2.md` D4 | 8 | main |
| Tab S1-S6 | tables | search strings, coder roster, codebook letters, 176-row census table, per-study extraction, quality appraisal | as listed above | supp | supp |

Colour-blind-safe palette, vector PDF, sizes at 5.48 in text width, `\Description{}` for every
figure (ACM accessibility request), greyscale-readable.

## 4. Evidence rules for the writer

1. Empirical sentence: `% src: path` (and a run or log name) next to it. Background sentence: a
   key that exists in `references.bib`. The key is the arXiv ID with a `arXiv` prefix where the
   work has one.
2. Tags: only source facts and our verified counts are stated as fact. Inference and hypothesis
   are worded as such.
3. Interval-bound claims only. "Most" is written as the count with its interval.
4. Negative and mixed results stay: the 0.05 eligibility kappa, the PC-1 control failure (if
   EXP-003 enters), the human validation still pending.
5. The ACM AI-use statement lives in section 2.9 and is part of the Methods, not an
   acknowledgement.

## 5. Open items that block submission (not drafting)

Human validation sample (218 records) and the 120 screening disagreements; full-text screening of
the 1123 records that passed (only a random sample of 176 is read at full text); the other
databases named in protocol section 3; extraction and quality appraisal of all included studies
(gate R2); gate audit of census-result-v2; EXP-003 frozen analysis and audit; reference
validation (citation-validator); `research-humanizer` pass; red-team referee simulation.

## 6. Draft status (2026-10-15, first compile)

`latexmk -pdf main.tex` compiles with zero undefined references and one overfull box of 1.46 pt
(acmart 2.20, acmsmall). Current PDF: 18 pages, of which about 11.8 are the three drafted sections
(Introduction about 3.6, Review method about 4.7, Census about 3.5) against a budget of 9.0, so
about 2.8 pages must be cut after the stubs are filled (candidates: Table 3, the departures list,
the research-question list in the PDF, the gap-ruling table to the supplement). Census numbers are
those of census-result-v2.md at commit 8dd2af3 (value-rule denominator 153, F3 to F6 on 152) and
carry `\aud` / `\todo{audit}` until the gate-auditor re-verifies the corrected file.
