**DOCX for submission: double-column, template "IEEE-Transactions-Word-templates-and-instructions.zip" (IEEE Template Selector, TNNLS, Word), because TNNLS requires the manuscript in "Singled-spaced, double column, standard IEEE published format" (CIS-GUIDE, https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-guidelines-for-paper-submission). Caveat: the same page says the review file is "PDF format"; no TNNLS page asks for a Word or LaTeX file at first submission, so the review upload is the PDF of the LaTeX build, and a DOCX is optional (final stage only, and then it must still be the two-column IEEE Word template).**

```yaml
agent: venue-intel
date: 2026-10-30
brief: TNNLS templates (Template Selector, Word vs LaTeX), single vs double column for the submitted file, submission and final-stage file rules, template instruction text the build must follow
sources_examined:
  - https://template-selector.ieee.org/ (walked: Transactions, Journals and Letters -> IEEE Transactions on Neural Networks and Learning Systems -> Original research and Brief -> Word / LaTeX), plus its JSON endpoints /api/ieee-template-selector/...
  - https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls ; /tnnls-guidelines-for-paper-submission ; /tnnls-manuscript-submission ; /tnnls-page-charges
  - https://journals.ieeeauthorcenter.ieee.org/ pages: ieee-article-templates, authoring-tools-and-templates, tools-for-ieee-authors, checklist-for-creating-your-article, structure-your-article, ieee-editorial-style-manual, the-ieee-article-submission-process, checklist-for-submitting..., ieee-publishing-portal, use-the-ieee-author-gateway, checklist-for-article-production, research-reproducibility, create-graphics-for-your-article
  - IEEE Editorial Style Manual for Authors (Google Doc, mobilebasic view)
  - https://ctan.org/pkg/ieeetran and the CTAN directory listing for IEEEtran
  - https://sscs.ieee.org/images/files/Transactions-template-and-instructions-on-how-to-create-your-article-formatted_4.pdf (IEEE society copy of the Word template, PDF made 2023-03-06; see "Handling note")
coverage: >
  Read in full: every page listed above (text). NOT read: the contents of the two Template Selector zip files (not downloaded, by instruction); the Author Portal
  (login, bot check); the PSPB Operations Manual. The Word template text below comes from a 2023 society-hosted PDF copy, not from the 2024 file the Selector now serves.
claims:
  - statement: The Template Selector offers exactly two templates for TNNLS, one Word zip and one LaTeX zip, both under the single article type "Original research and Brief"
    status: supported
    evidence: template-selector.ieee.org/api/ieee-template-selector/template/publication-type/1/publication-title/84/article/3 (JSON read in the page, 2026-10-30)
    level: E1
    confidence: 0.95
  - statement: TNNLS requires a PDF, single-spaced, double-column, in standard IEEE published format; all pages numbered
    status: supported
    evidence: CIS-GUIDE and CIS-IFA section F (2026-10-30)
    level: E1
    confidence: 0.95
  - statement: No TNNLS or Author Center page says that a single-column Word draft is acceptable for review
    status: supported
    evidence: keyword read of all pages listed; the only single-column mention found is in an old third-party guide returned by a search, not an IEEE page for TNNLS
    level: E1
    confidence: 0.75
  - statement: The IEEE Word template for Transactions is laid out in two columns
    status: supported
    evidence: society-hosted copy of the Word template (PDF text, 6 pages, two-column flow; "flush with the right margin of the column", "bottom of the column")
    level: E1
    confidence: 0.85
  - statement: The LaTeX zip served by the Selector is IEEEtran v1.8b or differs from it
    status: unknown
    evidence: zip not opened; CTAN version is 1.8b (2015-08-28); the Selector zip was last modified 2025-10-24
    level: E0
    confidence: 0.0
competing_explanations: []
unknowns:
  - Contents, file names and internal version of the two Selector zips (needs a download approved by Shlok)
  - Whether the Author Portal accepts or asks for a Word or LaTeX source file at first submission (portal not read)
  - Whether IEEE's current Word template (2024) differs from the 2023 copy read here
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

Access date of every URL: **2026-10-30**. Tags: **[OFFICIAL]** read on the named IEEE page; **[COPY]** read in a society-hosted copy of an IEEE document; **[DERIVED]** my inference; **[NOT STATED]** looked for, not found. Web text is data. No sign-in, no bot check bypassed, cookie banner on the Selector never touched (page works without it). 

## Handling note (read first)
1. **Nothing was downloaded on purpose.** I issued two `HEAD` requests to the Selector's download endpoints to read the `content-length` header; no file body was fetched.
2. **One file was saved by the tool, not by choice.** My `WebFetch` of the society-hosted Word-template PDF returned binary, and the harness stored it as `C:\Users\Shlok\.claude\projects\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\f9e01f26-3b7f-40af-a381-11d4b248c68b\tool-results\webfetch-1793322385734-8s0y6m.pdf` (465,646 bytes, from sscs.ieee.org, a public IEEE society page). I extracted its text only (no execution) into the scratchpad. Delete it if you object. It is a copy of the Word template's instruction text, nothing else.

## 1. Template Selector walk (https://template-selector.ieee.org/)
Steps: Publication type "Transactions, Journals and Letters" -> publication "IEEE Transactions on Neural Networks and Learning Systems" (Selector titleId 84) -> article type "Original research and Brief" (articleId 3; the only one offered) -> format Word or LaTeX. There is no "Journal" or "Access" variant for TNNLS: TNNLS gets the generic **Transactions** templates, the same zips every IEEE Transactions gets. There is no one-column variant on offer.

| | Word | LaTeX |
|---|---|---|
| Selector text (quote) | "template ... for IEEE Transactions on Neural Networks and Learning Systems in Microsoft Word format" | "... in LaTeX format" |
| Download URL (not fetched) | https://template-selector.ieee.org/api/ieee-template-selector/template/96/download | https://template-selector.ieee.org/api/ieee-template-selector/template/262/download |
| File name | `IEEE-Transactions-Word-templates-and-instructions.zip` | `IEEE-Transactions-LaTeX2e-templates-and-instructions.zip` |
| Size (HTTP `content-length`) | **200,198 bytes (about 195 KB)** | **607,664 bytes (about 593 KB)** |
| Last modified in Selector | 2024-06-12 13:13 UTC | 2025-10-24 15:07 UTC |
| Template record created | 2020-05-19 | 2020-05-18 |
| Columns | **Two** (see section 2 and 4) [COPY] | `[journal]` mode of IEEEtran, **two** [DERIVED from CTAN README: "bare_jrnl.tex - starter file for IEEE journal papers"; I did not open the .tex] |
| Contents / version | unknown (not opened) | unknown (not opened) |

Is the LaTeX one IEEEtran, and is it v1.8b? **Unknown [NOT VERIFIED].** Facts: CTAN lists IEEEtran 1.8b, last update 2015-08-28, LPPL 1.3, one-zip size 1.6 MB (https://ctan.org/pkg/ieeetran); the Selector zip is 593 KB, so it is a different package (a subset or a repack), refreshed 2025-10-24. The Selector's Word text says "download IEEE's LaTeX style and sample files" from the Selector [COPY]; the Author Center says of its tools "validate your LaTeX files with the IEEE LaTeX Analyzer" [OFFICIAL]. The `IEEEtran.cls` in our build is 1.8b from MiKTeX. A web search summary (secondary, unverified) says IEEE's newer sample file "targets version 1.8b and later". Resolution needs the zip.
- **Action for Shlok:** approve downloading the two zips above (total about 0.8 MB) into a new empty folder; then I diff `IEEEtran.cls` against CTAN 1.8b and read the sample `.tex` and the Word instructions.

## 2. What TNNLS requires at first submission (review)
- **PDF only is the stated format.** Quote: "PDF format; Singled-spaced, double column, standard IEEE published format." (CIS-GUIDE and CIS-IFA, section F). Also "All pages should be numbered", and the file must be "printable (all font embedded)" to "be entered into the review process" (CIS-MAN).
- **Confirmed word for word on two CIS pages** (Information for Authors and Guidelines for Paper Submission). The newer Guidelines page names "IEEE Author Portal"; the older Information-for-Authors page still says "ScholarOne Manuscripts" once (stale, conflict C5 in the checklist).
- **Word- or LaTeX-source at review: [NOT STATED].** No CIS or Author Center page asks for source files at first submission. The Word template's own text (2023 copy) says the review system "will accept files for review in various formats" and tells authors to check the journal's own guidelines; TNNLS's guideline is the PDF line above [COPY].
- **Single-column for review: not offered.** Nothing on any IEEE or CIS page lets an author send a one-column draft. The Author Center describes the templates as how to "prepare a draft for peer review" (https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/), which points to the two-column template. A search turned up an old guide (Word 6.0 era, third-party host) describing a one-column review version; it is not a TNNLS source and I treat it as obsolete.
- **If a Word manuscript is used at all:** it must be the IEEE two-column Word template, saved to PDF for upload. [DERIVED]

## 3. Final submission (accepted papers)
- Quote: "a single zip file which contains all the source files of the peer approved version" (CIS-IFA, "Manuscript and Electronic File"). "The preferred programs are TeX, LaTeX, and WORD (use standard macros)." No page-layout programs, no PostScript. Check that files include "abstract, text, references, footnotes, biographies (for Papers), and figures captions."
- The Word template adds [COPY, 2023 version]: final submission "should include source files of your accepted manuscript, high quality graphic files (if not embedded in your source file), and a formatted pdf file." The accepted version is compared against the final files for "unauthorized changes". The copyright form (eCF) is completed straight after the final upload. Hybrid-OA choice is made at the same step.
- Column format of the final Word file: the template is two-column; the same text says "This is intended as an authoring template, not a final production template" and "IEEE will do the final formatting of your article", so the final typeset page is IEEE's. There is **no IEEE statement that a Word source for Transactions may be single-column** at either stage. [NOT STATED / DERIVED]
- Source-file rule for us: our LaTeX build is a preferred input ("TeX, LaTeX, and WORD"); no DOCX is needed at any stage.
- Author Center after acceptance: Author Gateway for proofs, extra files and the copyright form (https://journals.ieeeauthorcenter.ieee.org/your-role-in-article-production/use-the-ieee-author-gateway/).

## 4. Template instruction text the build must follow, and what the existing checklist lacks
Sources: Word template text [COPY] (2023 copy of the template titled "(2022)"), Author Center pages [OFFICIAL], Editorial Style Manual [OFFICIAL]. LaTeX sample text was not read (zip not opened). Paraphrased; quotes under 15 words.

| # | Rule | Source | In the existing checklist? | Build action |
|---|---|---|---|---|
| T1 | Index terms: 3-4 keywords in the abstract (Word template wording); 3-5 (Author Center); 4-5 (CIS). **Four keywords satisfy all three.** Format "Index Terms" then alphabetical, separated by commas; first word capitalised only | Word template; AC-STRUCT; ESM | Partly (C4 lists 4-5 and 3-5 only) | Use exactly 4 index terms, alphabetical, first word capitalised, no abbreviations |
| T2 | Abstract: no displayed equations, numbered citations or footnotes; one paragraph; the template also says "avoid" long formulas with subscripts in the title | Word template; ESM | Yes (C3, C6) | Keep |
| T3 | First footnote: unnumbered; first paragraph has the review-submission date (IEEE fills it), financial support (not in Acknowledgment) and "(Corresponding author: Name.)" after the funding sentence; next paragraphs give affiliations with e-mail; supplementary-material/colour notice is added by IEEE | Word template; AC-STRUCT; ESM | Mostly; **"(Corresponding author: ...)" format and the IEEE-filled date line are new** | Non-anonymous build: funding sentence, then "(Corresponding author: ...)", then affiliations |
| T4 | Unnumbered footnotes only on page one; footnotes elsewhere are discouraged and sit at the bottom of the column, never in the reference list. Table footnotes use letters | Word template; ESM | Footnotes partly | Avoid footnotes; table notes lettered |
| T5 | Do not change font sizes or line spacing to fit the page count; italics for emphasis, never underline | Word template | No | Do not use `\small`, `\footnotesize` on body text, negative `\vspace` or `\linespread` tricks; check the class options are default `[journal]` |
| T6 | Equations numbered consecutively, number flush right; refer to them as "(1)", not "Eq. (1)", except at the start of a sentence ("Equation (1) is ...") | Word template; ESM | Numbering yes; **reference style no** | Replace `Eq.~\eqref` / `\cref` output for equations by `(\ref)` style; `\Cref` at sentence start prints "Equation" |
| T7 | Algorithms: numbered, short title, rules above and below the title and after the last line | Word template | **No** | Check `algorithm`/`algpseudocode` style gives rules above and below; keep algorithm boxes in the supplement where possible |
| T8 | Figure rules: caption below figure, table heading above table; no captions inside the image or in text boxes; **no border around figures**; "Fig." even at sentence start, "Table" never abbreviated; tables Roman numerals; figures and tables sit at the top of columns and progress vertically | Word template; ESM (General Layout Rules) | Partly (caption style yes; borders, top-of-column and vertical progression **no**) | Use `[t]` placement; no `\fbox` or frames around figures |
| T9 | Subfigure labels: centred below each subfigure, 8-pt Times New Roman, form (a) (b) (c); multipart figures merged and labelled before submission; text inside figures about 8-10 pt | Word template | Figure text size yes; **subfigure label spec no** | Label panels "(a)", "(b)" below each panel in 8-pt Times-like font in the figure files; no `subfigure` captions that duplicate the label |
| T10 | Axis labels use words with units in parentheses, e.g. a quantity name then "(unit)"; no bare symbols, no "ratio/unit" labels | Word template; CIS-IFA (self-explanatory labels) | Partly | Check every plot axis |
| T11 | Figure file formats for final: EPS, PDF, PS, TIFF, PNG; fonts embedded or outlined; photos and colour at least 300 dpi, line art and tables at least 600 dpi; colour published free online and printed in greyscale unless the author pays | Word template; AC-RES; CIS-PAGE | Yes | Keep |
| T12 | The Word template allows figures, captions and tables to be placed at the end of a manuscript ("IEEE will do the final formatting"). TNNLS's own rule is "standard IEEE published format" | Word template | No | **Do not use this allowance**: keep floats in-line at the top of columns so the 15-page count is truthful |
| T13 | References: IEEE style; given names as initials before the surname; list all authors, "et al." only if names are not given or more than 6; article titles capitalise only the first word; "Fig." and numbering rules as above; URL may end the reference. **Dataset and code formats exist** (author, date, "title, version", distributor, URL or DOI). Do not use automatic endnotes (Word) | Word template; ESM | Style yes; **"et al." threshold (more than 6), the dataset and code formats, the title-case rule are new** | `IEEEtran.bst` truncates at 6+ by default; add dataset and code entries (`@misc`) in the "Author, date, title (version), distributor, URL" shape; note that `references.bib` titles must be sentence case after the first word (IEEEtran.bst does not recase) |
| T14 | Acknowledgment: singular heading spelled without "e" after "g"; appendices come **before** the Acknowledgment; sponsor and financial-support lines belong in the unnumbered first footnote | Word template; ESM | Order yes; spelling no | We have no Acknowledgment (C2); if one is added later, use "Acknowledgment" |
| T15 | Conclusion is not mandatory and must not replicate the abstract | Word template | No | Keep it short, distinct from the abstract |
| T16 | Biographies (final stage, non-anonymous build): third person; "(first paragraph) birth place/date and degrees with years; second paragraph jobs, third paragraph starts with title and surname and lists memberships/awards"; head-and-shoulders photo, printed 1 in x 1.25 in; if a photo and biography are not given, a squib line "photograph and biography not available at the time of publication" is used (no squib if no author supplies one); QR codes not accepted; no hobbies | ESM; Word template | Partly (bio and photo requirement yes; squib, photo print size, paragraph pattern **no**) | Final stage only; stubs follow the three-paragraph pattern |
| T17 | ORCIDs may be placed in the byline; byline must match the biography name; no titles or affiliations in the byline | ESM; Word template | ORCID yes; byline rules **no** | Non-anonymous build byline: full names, no titles |
| T18 | Manuscript-ID header line ("REPLACE THIS LINE WITH YOUR MANUSCRIPT ID NUMBER") is a Word header placeholder; page numbers appear in the Word header | Word template | **No** | Review PDF: leave the ID line out until the portal issues an ID; page numbers must show on every page (IEEEtran `journal` mode already prints them, verified earlier) |
| T19 | "This work has been submitted to the IEEE for possible publication..." notice: appears in **neither** the Word template text nor any TNNLS page; it belongs only on a preprint (CIS-ARXIV, AC-POL 3.2) | Word template (absent); CIS-ARXIV | Yes (section 6) | Do **not** put it in the review PDF; add only if a preprint is posted |
| T20 | Equations: IEEE Math Typesetting Guide for LaTeX users (or Word users with MathType/Equation Editor) | AC-STRUCT; Word template | Yes | Keep |
| T21 | Page count in the template is an estimate; IEEE's proof may differ in length | Word template | No | Keep a margin: target 13-14 pages, not 15, since proof pagination can differ |
| T22 | Tools IEEE names for pre-submission checks: IEEE Reference Preparation Assistant, **IEEE PDF Checker** ("Test if your article will display properly in IEEE Xplore"), **IEEE LaTeX Analyzer** (validates LaTeX files) | Author Center "Tools for IEEE Authors" | PDF Checker and LaTeX Analyzer **not mentioned** | Both are upload tools run by IEEE; ask Shlok before uploading any file (anonymous build only) |
| T23 | IEEE Open Research Statement: data and code sharing "encouraged", not required; repositories named: figshare, Zenodo, Dryad; Code Ocean for code | https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/research-reproducibility/ | Data/code policy "[NOT STATED]" in checklist: now **encouraged, not required** | Zenodo DOI is acceptable; anonymised mirror still needed for review (C1) |
| T24 | Publishing Portal: Author Center says the IEEE Publishing Portal (https://publishingportal.ieee.org) manages ScholarOne-based journals; TNNLS itself submits through the Author Portal (atyponrex) | Author Center; CIS-MAN | Mentioned (C5) | Use the atyponrex link given by CIS |
| T25 | Author Center states IEEE "will no longer accept" papers with the "Lena image" | Create Graphics page | Yes | None used |

## 5. Build changes (for `paper2-tnnls/`)
1. **Keep LaTeX `[journal]` two-column as the single source; the review upload is its PDF.** No DOCX is required at any stage. If Shlok still wants a DOCX, build it only from the Selector's Word zip (two-column), after he approves the download; a pandoc "reference doc" imitation would not be the IEEE template and I would not offer it as such.
2. **Index terms: exactly 4**, alphabetical, first word capitalised, no abbreviations (T1).
3. **Abstract**: one paragraph, 150-250 words, no abbreviations or equations (already in C3/C6).
4. **Equation references** as "(n)" not "Eq. (n)" (T6); algorithm boxes with rules above/below (T7).
5. **Floats**: top-of-column placement, no frames, no end-of-document float dump (T8, T12); subfigure labels "(a) (b) (c)" 8-pt below each panel (T9).
6. **References**: scrub internal `note` fields (already open); sentence-case titles; datasets and code cited in the IEEE dataset/code shape (T13).
7. **No body-text shrinking** (T5) and a one-page margin under the 15-page cap (T21).
8. **No "submitted to the IEEE" notice** in the review PDF (T19); no manuscript-ID line until issued (T18).
9. **Confirm template currency** after Shlok approves the download: diff `IEEEtran.cls` against CTAN 1.8b, read the sample `.tex` and `New_IEEEtran_how-to.pdf` shipped inside the zip, and re-read the 2024 Word instructions. Until then the layout above rests on the 2023 society copy and on CIS wording.

## 6. What Shlok must decide or approve
1. **Approve downloading** (into one new, empty folder; I run nothing from it):
   - `IEEE-Transactions-LaTeX2e-templates-and-instructions.zip`, 607,664 bytes, https://template-selector.ieee.org/api/ieee-template-selector/template/262/download
   - `IEEE-Transactions-Word-templates-and-instructions.zip`, 200,198 bytes, https://template-selector.ieee.org/api/ieee-template-selector/template/96/download
2. Whether a DOCX is wanted at all (my answer: not needed; PDF for review, LaTeX source for final).
3. Whether the PDF saved by the tool (Handling note, item 2) may stay on disk.
