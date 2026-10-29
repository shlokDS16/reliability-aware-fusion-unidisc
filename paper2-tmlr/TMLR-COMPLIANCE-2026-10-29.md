# Paper 2: TMLR compliance audit (2026-10-29)

Scope: `paper2-tmlr/` (main.tex, sections/, build of `main.pdf`, 41 pages) against the official TMLR requirements.
Master content in `paper2/` is newer and will be re-synced later; nothing here was synced or edited in the manuscript.
Standing rule applied: AI use appears only in the section "Declaration of generative AI use" (this overrides placement only).
Evidence tags: SOURCE = official page text; OUR = file:line or command on this repo. Web content was treated as data.

## 0. Result in one line

5 FAIL, 5 WARN, 0 build problems (0 undefined references, 0 overfull boxes). The PDF is in the correct anonymous TMLR mode; what blocks
submission is unfinished text (26 red `\todo` items), a role/venue leak inside one of them, the missing anonymised artefact, the empty
AI declaration, and one missing data-ethics sentence.

## 1. Sources and access dates (all accessed 2026-10-29)

| ID | Page | Notes |
|---|---|---|
| S1 | https://jmlr.org/tmlr/author-guide.html | Fetched through a summarising fetcher (it would not return verbatim text). Style-file link, format, supplementary, licence, preprints. |
| S2 | https://jmlr.org/tmlr/editorial-policies.html | Titled "Submission Guidelines and Editorial Policies". LLM policy quoted verbatim by a second, targeted fetch. |
| S3 | https://jmlr.org/tmlr/acceptance-criteria.html | Two criteria; AI-generated clause. |
| S4 | https://jmlr.org/tmlr/ethics.html | Broader impact and data rules. |
| S5 | https://jmlr.org/tmlr/faq.html | 12-page threshold, camera-ready, preprint, survey exclusion. |
| S6 | https://jmlr.org/tmlr/reviewer-guide.html | Review timelines by length. |
| S7 | https://jmlr.org/tmlr/submissions.html and https://jmlr.org/tmlr/ (home) | Submission goes through OpenReview; style-change warning; news (pause windows). |
| S8 | https://github.com/JmlrOrg/tmlr-style-file (zip downloaded 2026-10-29 to `paper2-tmlr/style/`) | Read locally: `main.tex` (example paper), `tmlr.sty`, `README.md` (one line). `tmlr.sty`, `tmlr.bst`, `fancyhdr.sty` in `paper2-tmlr/` are byte-identical to the downloaded copies (`diff -q`, empty). Example-paper file date in the zip is 2023; no newer version number exists in the repo. |
| S9 | https://api2.openreview.net/invitations?id=TMLR/-/Submission | Public JSON of the OpenReview submission form fields (read through the summarising fetcher). The visual form was not opened. |

Limits of this audit: S1 to S7 and S9 were read through a summarising fetcher, so wording is paraphrase except where marked "verbatim".
The first fetch of S5 returned a statement that LLM use must be disclosed in a first-page footnote. A second fetch of S5 asking for the exact
LLM entry returned only "Yes, but ... the authors' responsibility", and the verbatim S2 policy neither requires nor recommends disclosure.
The footnote claim is therefore **not confirmed** and is treated as absent. Shlok or a browser session should re-read the FAQ entry
"Can I use ChatGPT or other large language model systems to assist in writing my TMLR submission?" before submission (D5).

## 2. Checklist of TMLR requirements, with audit of `paper2-tmlr/`

Status: PASS / FAIL / WARN (risk, not a rule breach) / N/A / AUTHOR (only the authors can supply).

### A. Style file, format, length

| # | Requirement (source) | Status | Evidence / fix |
|---|---|---|---|
| A1 | PDF made with the TMLR LaTeX style and template; changes that alter formatting, fonts or layout may lead to rejection without review (S1, S7, S8 "Final instructions") | PASS | `main.tex:5,7` (`article` 10pt + `\usepackage{tmlr}`); style files identical to S8 copy. |
| A2 | Submission mode = no option; `[accepted]` and `[preprint]` must not be used for the submission (S8 `main.tex` comments, `tmlr.sty:28-37,110-132`) | PASS | `main.tex:6-7`. PDF p.1 header reads "Under review as submission to TMLR" and "Anonymous authors / Paper under double-blind review". |
| A3 | Do not change style parameters; text area 6.5 x 9 in, 1 in left margin, 10 pt, 11 pt leading (S8) | WARN | Geometry untouched. But `main.tex:54-60` overrides float fractions, `main.tex:19` sets `\emergencystretch`, `main.tex:21-23` declares a font shape, `main.tex:16` loads microtype, and tables are shrunk with `adjustbox` (`results.tex:52,95,134,270,367,412,517,562`; `appendix.tex:49-50`, `related.tex:86-87` use `\footnotesize`/`\tabcolsep`). None is geometry, but S7 warns that layout changes may cause rejection. Fix (optional, low cost): at re-sync, check that no scaled table renders below about 7 pt, and consider removing the float overrides if the layout survives. |
| A4 | US Letter, not A4; pages numbered (S8) | PASS | `pdfinfo main.pdf`: 612 x 792 pts, 41 pages; numbering from `tmlr.sty`. |
| A5 | Abstract: one paragraph, 10 pt (S8) | PASS | `main.tex:70-90` is one paragraph (293 words). OpenReview limit 5 000 characters (S9); the abstract is about 1 650 characters. Contains an open `\todo` (see F1). |
| A6 | Title: OpenReview limit 250 characters (S9) | PASS | `main.tex:63`, about 125 characters. |
| A7 | Headings bold, flush left, 12/10/10 pt (S8) | PASS | Produced by `tmlr.sty`; no heading overrides found. |
| A8 | Figure caption after figure, table title before table, lower case except first word and proper nouns, centred, legible, not hand-drawn (S8) | PASS | Tables: `\caption` before `\begin{tabular}` (`results.tex:40-53`). Figures are Matplotlib PDFs (`../paper2/figures/`). Captions begin with a capital and use sentence case; acronyms and symbols are proper nouns for this purpose. |
| A9 | Citations with natbib: `\citet` in the sentence, `\citep` otherwise; `tmlr.bst` (S8) | PASS | `main.tex:122-123`; `main.log` has 0 undefined citations or references. |
| A10 | Length: unrestricted but must be justified by content; unusually long main text may delay review. Main text over 12 pages (before references) is reviewed on a 4-week rather than 2-week reviewer deadline; the form asks Regular (<= 12 pages) or Long (S1, S5, S6, S9) | WARN | Main text ends on p.32 and the references start on p.33 (`pdftotext`, page scan); appendix pp.34-41; total 41. The submission type must be set to **Long**. Reviewer burden is the real risk: 32 main pages for a preregistered null result invites "justify the length". Suggest, at re-sync, moving the exploratory Tier 3, E-dec/E-pred and the status table to the appendix so the main text carries the preregistered question, the primary result, and the controls. Not a rule breach. |
| A11 | Appendix may follow the references in the same PDF; reviewers need not read it (S1, S5) | PASS | `main.tex:125-126` (`\appendix` after `\bibliography`). |
| A12 | PDF upload at most 50 MB (S9) | PASS | `main.pdf` is 1.1 MB. |
| A13 | Figure sources path | N/A | `main.tex:29` points to `../paper2/`; only the PDF is submitted, but the supplementary ZIP must be self-contained (see C3). |

### B. Anonymisation

| # | Requirement (source) | Status | Evidence / fix |
|---|---|---|---|
| B1 | No author names; non-anonymous submissions are rejected without review (S8, S1) | PASS | `main.tex:64` `\author{Anonymous authors}`; case-insensitive grep for the authors, collaborators, VIT, Vellore, e-mail domains, GitHub, Zenodo, OSF in `main.tex`, `sections/`, `references.bib`: no hit. |
| B2 | PDF metadata free of identity | PASS | `pdfinfo main.pdf`: Author, Title, Keywords empty. Figure PDFs carry only "Creator: Matplotlib". |
| B3 | Self-citation, links to named versions, acknowledgements, funding hidden (S1, S8) | PASS (with AUTHOR check) | No self-citation by name. Acknowledgements, funding and contributions are absent (`declarations.tex`). AUTHOR: confirm that none of the 48 reference entries is written by a co-author (the co-author list is not in the repo). |
| B4 | No role or venue leak in the PDF | **FAIL (F2)** | `discussion.tex:114` (red text in the PDF, p.31) says "settle the scope-fit question with the supervising professor"; the abstract todo, `discussion.tex:86,156,166` and `related.tex:129` also discuss reading "Zhou and Lu" for "this journal". Delete or rewrite all red items (F1). |
| B5 | Source files must not travel with the submission | WARN | `main.tex:2` and `PORT-NOTES.md` name the Elsevier Information Fusion version and a person ("for Shlok to supply"). If any source is put in the supplementary ZIP, exclude `PORT-NOTES.md` and strip comments. |
| B6 | Supplementary / code must be anonymised (S1) | **FAIL (F3)** | `declarations.tex:5-13`: the text promises an anonymised artefact at commit `164a18a5`, and the link is a red placeholder (`declarations.tex:6-7`). The git history of that commit carries the committer identity, so an anonymous snapshot must be a fresh tree without history (or an anonymising mirror), with licence text and README free of names. |
| B7 | Text mentions of "Information Fusion" | WARN | `introduction.tex:29,63`, `related.tex:112,117`, `discussion.tex:112,165` describe cited work published in that journal. They reveal nothing about authors but frame the paper for another venue ("Why this is a fusion problem", `introduction.tex:22`). Decide at re-sync whether to keep the fusion framing for TMLR's audience. |

### C. Statements, code, supplementary

| # | Requirement (source) | Status | Evidence / fix |
|---|---|---|---|
| C1 | Broader Impact Statement: required if the work carries a significant risk of harm (S1); S4 says submissions are "expected, when applicable" to discuss negative societal impact; the template calls it optional (S8) | WARN | None in the paper, which is consistent with S1 (no significant risk: a gate on image tokens, evaluated on a public benchmark). Reviewers are asked to judge whether one is needed (S6). Cheap hedge: one unnumbered `\subsubsection*{Broader Impact Statement}` of 2 to 3 sentences before the references. |
| C2 | Human-derived data: explain permission to use/share data, consent, PII, offensive content, licence handling (S4) | **FAIL (F5)** | `protocol.tex:20-26` cites COCO val2017 only; `declarations.tex:11-12` says COCO is not redistributed. Add 2 to 3 sentences in the data subsection or the broader-impact paragraph: public benchmark, terms of use followed (verify the current COCO terms of use and licence before stating them; not verified here), images of people, no new collection, no redistribution of COCO. Also state that UniDisc and tokenizer weights are used under their licences (verify each licence). |
| C3 | Supplementary: at most 100 MB, PDF or ZIP, made by the authors, anonymised, directly supports the paper; reviewers may skip it; code/data encouraged (S1, S9) | **FAIL (F3, pending build)** | Not built yet. Contents promised at `declarations.tex:8-11`. Fix: build a self-contained ZIP (code `exp_p2/` and tests, fold file, preregistration card, SAP, per-item scores for each cited run directory, scripts), well under 100 MB, no git history, no absolute paths or usernames in logs, then replace the placeholder with the sentence "supplementary material" or an anonymous link. Large arrays: check size before including. |
| C4 | Reproducibility statement | PASS (content) | `declarations.tex:5-13` is complete except the link (C3). Hashes and commit id are content identifiers. |
| C5 | Human-subjects approval details (OpenReview field) (S9) | N/A for PDF; AUTHOR for form | No human-subject experiment in the paper. Field is mandatory; enter "N/A" with one sentence (public benchmark, no human participants). |
| C6 | Competing interests, last 36 months (OpenReview field, mandatory) (S9) | AUTHOR | See section 3. |
| C7 | Funding | N/A for PDF | No funding field exists in the OpenReview form (S9). S1 lists funding among items authors report; the template puts funding in the Acknowledgments after acceptance (S8). Nothing to put in the anonymous PDF. |
| C8 | Keywords / subject areas | N/A | The OpenReview form has no keywords or subject-area field (S9); TMLR's template has none. Only the action-editor recommendation (asked by e-mail after submission, S7). |
| C9 | Open problems in the PDF | **FAIL (F1)** | 26 `\todo` calls: `main.tex:88` (abstract); `appendix.tex:94,100`; `conclusion.tex:16,17`; `declarations.tex:6,16`; `discussion.tex:86,114,156,166`; `introduction.tex:109,118`; `protocol.tex:235,280,332`; `related.tex:129`; `results.tex:68,258,429,436,448,619,620,622,629`. They print in red in the PDF. They include pending results (S2, FOIL, suite, status table) and an unfinished Figure 1 (`introduction.tex:118`). All must be resolved or deleted before submission. This is expected until the last results are in and the master is re-synced. |

### D. Policies (originality, preprints, licence, LLM, ethics)

| # | Requirement (source) | Status | Evidence / fix |
|---|---|---|---|
| D1 | Original work only; no reuse of written text, figures or results with a published, accepted or parallel-submitted archival paper (S2) | PASS (with AUTHOR confirm) | OUR check: 8-word shingle overlap between `paper2-tmlr/sections/` (23 366 words) and the review paper's `sections/` in the worktree `resume-dlm-discovery-exp-003-334706` (31 204 words) = **0 shared 8-grams**. Both use UniDisc; no EXP-003 result or sentence appears in Paper 2. The check used that worktree's copy, not the frozen release (`release/dlm-review-fusion-v1.1.0`), so re-run on the final review text before submission. |
| D2 | Not in official proceedings elsewhere; parallel submission to another archival venue not allowed (S2, S5) | AUTHOR | Confirm the Elsevier version of Paper 2 (`paper2/`) has not been submitted to Information Fusion (VENUE-OPTIONS says one venue at a time). |
| D3 | Preprints (arXiv, bioRxiv) allowed at any time with or without names; the TMLR submission must not link to a version showing author names; use the `[preprint]` option for a de-anonymised copy (S1, S2, S5) | PASS / N/A | Nothing linked. If a preprint is posted, build it with `[preprint]` and do not cite it in the PDF. Reviewers are asked not to search for it. |
| D4 | Licence: all submissions are CC BY 4.0 from submission through publication; authors keep copyright (S1) | AUTHOR | Authors accept this on submission (see section 3). Check that no third-party figure or table is reproduced: all figures are own Matplotlib output; the UniDisc evidence table (appendix) restates repository facts and cites them. |
| D5 | LLM use: LLMs may be used as general-purpose assistive tools; authors fully responsible; LLMs cannot be authors; largely LLM-generated low-quality work is examined for misconduct (S2, verbatim). No disclosure is required or recommended. Acceptance criteria say papers "almost entirely AI-generated with little human involvement" are unlikely to qualify (S3). | **FAIL (F4)** | Recorded; Shlok's rule applies: mention only in the section "Declaration of generative AI use" (`declarations.tex:15-19`, present, before the references). Text of that section is a red placeholder. Fix: write the wording (tools, versions, purposes, extent of human review, responsibility, no author-identifying detail). Because S3 weighs "human involvement", keep the statement accurate about where humans made the design, preregistration, analysis and checking decisions. No other place in the PDF mentions AI (grep of the PDF text: only `declarations.tex`). |
| D6 | Scope and evaluation: original work on principles of learning in brains or machines; accept if claims are supported by accurate, convincing, clear evidence and some audience is interested; no requirement for significance, novelty or state of the art; narrowing claims is an accepted remedy (S2, S3) | PASS | The abstract and conclusion narrow the claim to a bounded null ("excludes an improvement larger than 0.05", "not a finding that GATE-M has no effect"). This fits criterion 1 directly. |
| D7 | Ethics: discredited datasets not allowed; GDPR/PII considerations for human data (S4) | PASS (see C2) | COCO is not on the page's discredited example (DukeMTMC-ReID). Covered by the C2 fix. |
| D8 | Survey papers: TMLR no longer considers surveys from 2026-09-01 (S5) | N/A | Paper 2 is an empirical study. The companion review cannot go to TMLR anyway. |
| D9 | Certifications (Outstanding, Featured, Reproducibility, Survey, J2C, Expert) (S2) | N/A | Assigned by editors; the "Reproducibility" certification is for reproduction papers and does not apply. Nothing to declare. |
| D10 | Rejected papers stay public on OpenReview; revealing identity bars a revised version; resubmission only as a new submission linking the old one; desk-rejected papers are never public (S2, S5) | AUTHOR | Informational; decision for Shlok (section 3). |

### E. Submission mechanics (OpenReview) and timing

| # | Item (source) | Status |
|---|---|---|
| E1 | Fields: title (<= 250), abstract (<= 5 000), authors with OpenReview profiles (hidden from reviewers), pdf (<= 50 MB), submission type Regular / Long / Beyond PDF, supplementary (ZIP or PDF <= 100 MB), previous TMLR submission URL and changes (only for resubmissions), competing interests (mandatory; 36 months or "N/A"), human subjects reporting (mandatory; "N/A" allowed) (S9) | AUTHOR |
| E2 | Complete, active OpenReview profiles for all authors (affiliations, conflicts, publication history); author list cannot change after submission (S1, S2) | AUTHOR |
| E3 | Authorship quota: Generalized Harmonic Quota Rule with N1 = 2, N9 = 9; each submission, including a desk-rejected one, consumes budget by author count; every author needs remaining budget (S2) | AUTHOR |
| E4 | After submission an e-mail asks for recommended action editors; AE assigned within about a week, may desk-reject for scope, quality, or format violations; then at least three reviewers; decision target about 9 weeks, not guaranteed; authors respond within 2 weeks of the third review; discussion 2 to 4 weeks (S2, S5) | Informational |
| E5 | Submission pause windows: 2024-12-02 to 2025-01-06 and 2025-12-02 to 2026-01-05 were announced for past years (S7 home page). **Projected, not official:** a similar pause around 2026-12-02 to 2027-01-05 may be announced. Submit before 2026-12-02 to be safe. | Informational |

### F. Camera-ready (after acceptance; from S2, S5, S8)

Do these only after the AE accepts; the camera-ready is final and changes are not allowed (EiC exceptions by e-mail to tmlr-editors@jmlr.org).
1. Replace `\usepackage{tmlr}` by `\usepackage[accepted]{tmlr}` (`main.tex:7`). Header becomes "Published in TMLR (month/year)" and the title block prints "Reviewed on OpenReview: <link>".
2. Set `\def\month{MM}`, `\def\year{YYYY}`, `\def\openreview{\url{https://openreview.net/forum?id=...}}` (the forum link of the review page is mandatory).
3. Replace `\author{Anonymous authors}` by the template block: `\name`, `\email`, `\addr` per author, separated by `\AND`.
4. Add (optional, template says only after acceptance and de-anonymisation) unnumbered third-level sections: Broader Impact Statement, Author Contributions, Acknowledgments (with funding).
5. De-anonymise the artefact: real repository, Zenodo DOI, licence; replace the placeholder paragraph in `declarations.tex`.
6. Keep the "Declaration of generative AI use" section (Shlok's rule) and keep no AI mention elsewhere.
7. If the decision is "accept with minor revision", make the AE's required changes in the camera-ready; the AE verifies.
8. Code or video can be uploaded and associated with the camera-ready version (S5).
9. Post-publication changes are documented publicly (S2).

## 3. FAIL list with exact fixes (5)

| ID | Where | Fix |
|---|---|---|
| F1 | 26 `\todo` calls listed in C9 | Resolve each with final results at re-sync, or delete the sentence. The `\todo` macro (`main.tex:34`) should have no remaining call; `grep -n '\\todo' sections/*.tex main.tex` must return only the definition. Abstract sentence at `main.tex:88-89` becomes a plain status sentence of at most 13 words. |
| F2 | `discussion.tex:114` (and the other "read Zhou and Lu" notes at `related.tex:129`, `discussion.tex:156,166`) | Delete the supervising-professor / scope-fit todo. It is a role and venue leak and is part of F1. |
| F3 | `declarations.tex:5-13`; supplementary ZIP | Build the anonymised ZIP (no history, no names or absolute paths, licence, README), upload it as supplementary material, and replace the placeholder by an accurate sentence. Check that the ZIP is under 100 MB. Exclude `PORT-NOTES.md`, LaTeX comments naming Information Fusion or a person. |
| F4 | `declarations.tex:15-19` | Write the declaration (tools, versions, purpose, extent of human work and checking, authors' responsibility). Placement stays in this section only. |
| F5 | `protocol.tex:20-26` | Add the COCO / model-licence / human-derived-data sentences required by the ethics guidelines (C2). Optionally add the 2-3 sentence Broader Impact Statement (C1). |

## 4. What Shlok must provide or do himself

1. **OpenReview accounts.** One complete profile per author: affiliations (Education & Career History gives domain conflicts for the last 3 years), Advisors, Relations & Conflicts (personal conflicts, PhD advisor, collaborators within 3 years), publication history. I cannot create accounts or enter passwords.
2. **Final author list and order** (cannot be changed after submission). TMLR does not ask for ORCIDs on the pages read (the template has no field); add ORCIDs in the OpenReview profiles and in the camera-ready if wanted. Contribution statements are optional (S2).
3. **Quota check** for every author with the CMU tool linked from S2 (N1 = 2, N9 = 9; desk rejections also count; do not create duplicate accounts).
4. **Conflicts** of interest: domain and personal, as above; do not declare false conflicts to block reviewers.
5. **Form entries:** competing interests (36-month relationships or "N/A"), human-subjects field ("N/A" plus one sentence), submission type **Long**, acceptance of CC BY 4.0 on submission, supplementary ZIP, and the action-editor recommendations requested by e-mail after submission. There is no keyword or subject-area field and no funding field.
6. **Declaration wording** for the generative-AI section (`declarations.tex:15-19`), and a final check of the FAQ entry on LLM disclosure (D5). Rule: AI only in that section.
7. **Anonymised artefact:** approve what goes in the ZIP and the anonymised link (F3); keep the real GitHub/Zenodo record for the camera-ready.
8. **Reference check:** confirm no reference entry is by a co-author (B3), and that the COCO, UniDisc and tokenizer licences are as stated (C2).
9. **Venue exclusivity:** confirm Paper 2 is not under review at Information Fusion or elsewhere (D2). Decide whether to keep the Information-Fusion-flavoured framing (B7).
10. **Overlap note for the review paper (Information Fusion).** The review is an archival paper under submission, so TMLR's rule on reuse of text, figures or results applies. Statement to keep ready: "Paper 2 and the companion review share only the backbone UniDisc as an object of study. They share no text, figure, table or result; the review's UniDisc measurement (guided versus plain sampling, text-image link) asks a different question from Paper 2 (token gating under image corruption)." My shingle check found 0 shared 8-grams against the review sections in `resume-dlm-discovery-exp-003-334706`; re-run it on the frozen review text (the release folder or the final `main-infus.tex`). TMLR has no form field for this; keep the note for the action editor if asked. If the review appears in print before the TMLR decision, any citation of it from Paper 2 would be a self-citation and must be anonymised ("Anonymous, 2026").
11. **Public visibility.** A rejected TMLR submission stays public on OpenReview (anonymised), and revealing identity bars a revised TMLR submission; the paper is a preregistered null result, so decide whether that is acceptable.
12. **Timing.** Aim to submit before the projected winter pause (E5), after the last results and the re-sync (F1).

## 5. Re-check after the re-sync

Re-run: `latexmk -pdf main.tex` inside `paper2-tmlr/`; `grep -n '\\todo' sections/*.tex main.tex`; `pdftotext main.pdf - | grep -n -i 'AUTHOR\|RESULT'`; `pdfinfo main.pdf` (metadata empty, Letter); `pdftotext` page scan for the page where "References" starts (set submission type: Regular if <= 12, otherwise Long); the author-name grep of B1; the shingle overlap check of D1.
