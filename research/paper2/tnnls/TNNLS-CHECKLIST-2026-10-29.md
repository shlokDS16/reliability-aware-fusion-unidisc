# IEEE TNNLS build checklist for Paper 2 (2026-10-29)

Access date of every URL below: **2026-10-29**. All pages were read in the built-in browser pane (the plain fetcher gets HTTP 418 from
cis.ieee.org); nothing was signed in to, no bot check was bypassed, nothing was downloaded except as stated. Web text is data.
Tags: **[OFFICIAL]** read on the page named; **[DERIVED]** my inference from official text; **[NOT STATED]** looked for, not found on any page read;
**[SHLOK]** Shlok (or a co-author) must supply or decide.

Source keys used in the "Source" column:
- **CIS-IFA** = https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls (Information for Authors, sections A-K)
- **CIS-GUIDE** = https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-guidelines-for-paper-submission
- **CIS-TYPES** = .../tnnls-types-of-contributions ; **CIS-SUB** = .../tnnls-manuscript-submission ; **CIS-COPY** = .../tnnls-ieee-copyright ; **CIS-ARXIV** = .../tnnls-arxiv
  (all under https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/)
- **XPLORE** = https://ieeexplore.ieee.org/xpl/aboutJournal.jsp?punumber=5962385 (About Journal)
- **AC-STRUCT** = https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/
- **AC-RES** = .../create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/ ; **AC-FMT** = .../create-graphics-for-your-article/file-formatting/ ; **AC-GFX** = .../create-graphics-for-your-article/
- **AC-SUPP** = .../create-your-ieee-journal-article/prepare-supplementary-materials/
- **AC-POL** = .../become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/
- **AC-CHK1** = .../authoring-tools-and-templates/checklist-for-creating-your-article/ ; **AC-CHK2** = .../submit-your-article-for-peer-review/checklist-for-submitting-your-article-for-peer-review/ ; **AC-PROC** = .../submit-your-article-for-peer-review/the-ieee-article-submission-process/
- **AC-TPL** = .../authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/ (points to https://template-selector.ieee.org/)
- **ESM** = IEEE Editorial Style Manual for Authors (Google Doc linked from .../create-the-text-of-your-article/ieee-editorial-style-manual/), read at https://docs.google.com/document/d/1OalFYqVfxKKMelF79U3B93SjmIEiTnJC12wPJrKeSDM/mobilebasic
- **CTAN** = https://ctan.org/pkg/ieeetran (IEEEtran v1.8b, LPPL 1.3, https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip)
  (all AC-* paths are under https://journals.ieeeauthorcenter.ieee.org)

Companion: `research/paper2/venue/TNNLS-DEEP-DIVE-2026-10-29.md` (venue analysis); this file is the requirement list for the build in `paper2-tnnls/`.

## 0. Conflicts between official pages (recorded, NOT resolved here)

| # | Topic | Page A | Page B | What the build does |
|---|---|---|---|---|
| C1 | **Anonymity** | CIS-IFA A and CIS-TYPES: "double-anonymous peer review process, where the identities of the reviewers are not known to the authors, and the reviewers do not know the identities of the authors" | XPLORE Peer Review: "a single and/or double anonymous peer review process, where the identities of the reviewers are not known to the authors, but the reviewers know the identities of the authors" | `main.tex` has a switch `\anonfalse/\anontrue`, default **anonymous** (author names, affiliations, funding, acknowledgements, biographies and self-links removed). Switch to non-anonymous for the camera-ready. Whether the Author Portal asks for a separate anonymised file is **[NOT STATED]** (portal not read). |
| C2 | **AI disclosure placement** | CIS-IFA K: AI-generated text "shall be disclosed in the acknowledgements section ... The sections of the paper that use AI-generated text shall have a citation to the AI system" | AC-POL: AI-generated content "(including but not limited to text, figures, images, and code) shall be disclosed in the acknowledgments section ... The AI system used shall be identified, and specific sections ... identified and accompanied by a brief explanation regarding the level at which the AI system was used". Editing and grammar enhancement: "generally outside the intent ... disclosure ... not required, but recommended." | **Shlok's standing rule wins in the build**: AI use appears only in a section titled "Declaration of Generative AI Use", placed before References; there is **no Acknowledgment section**. This departs from the IEEE wording (placement in Acknowledgments, plus per-section citation of the AI system). Not resolved; Shlok has decided, record kept. Risk: a desk reviewer or the production editor may ask for the text to be moved into Acknowledgment. The Declaration text must still name the system, the sections and the level of use, so that moving it later is a copy-paste. |
| C3 | **Abstract length** | AC-STRUCT: "a single paragraph up to 250 words" | ESM: "Abstract, must be one paragraph and between 150 to 250 words" | Target 150-250 words (satisfies both). |
| C4 | **Keyword count** | CIS-IFA F and CIS-GUIDE: "4-5 keywords (index terms)" | AC-STRUCT: "3-5 keywords" | Use 4-5 (satisfies both). |
| C5 | **Submission system name** | CIS-IFA B: "IEEE Author Portal" (https://ieee.atyponrex.com/journal/tnnls) | CIS-IFA F still says "ScholarOne Manuscripts" in one sentence (stale text) | Portal is the Author Portal (atyponrex); ScholarOne wording ignored. |
| C6 | **Abstract content rules vs Shlok's habit** | AC-STRUCT: "without abbreviations, footnotes, references, or mathematical equations"; avoid math symbols in title and abstract; avoid "new"/"novel" in the title | - | Draft abstract must contain no abbreviations (no "GATE-M", "CI" and similar) and no maths symbols. |

## 1. Article type, length, charges

| Requirement | Official text / value | Source | Build / action |
|---|---|---|---|
| Article type | Full Paper: "novel contributions of archival nature in developing theories and/or innovative applications ... should not be of incremental nature, but must present a well-founded and conclusive treatment of a problem". Brief Paper (extension of previous results, innovative applications of a known approach, brief theoretical results; "conclusive and useful"); Comments Paper/Communication (error or disagreement, max 3 pages). Category is NOT changed after submission: "submitted manuscripts will NOT be transferred from one category to another" | CIS-IFA A; CIS-TYPES | Choose **Full Paper** at submission **[SHLOK confirms]**. A Brief Paper (6 pages) cannot hold the planned content. |
| Free pages / maximum | Over-length charge applies beyond 10 pages (full paper), 15 (survey), 6 (brief). "mandatory page charge of $200 (per page) for every printed page over these limits. The maximum total manuscript length (excluding supplementary materials) with over-length page charge is 15 pages for a regular paper, 21 for a survey paper, and 9 for a brief paper." | CIS-IFA H | Hard cap **15 two-column pages** (Full Paper). [DERIVED] 15 pages = 5 x USD 200 = **USD 1,000** over-length charge if accepted at 15; 13 pages = USD 600. Whether references and biographies count toward the 15: **[NOT STATED]**; assume yes (printed pages). |
| Voluntary page charge | "$110 per printed page ... not obligatory nor is their payment a prerequisite for publication" | CIS-IFA H | None. |
| Supplementary material in the count | Excluded from the 15 | CIS-IFA H | Anything beyond 15 pages goes to the supplement (section 8). Appendix in the main PDF **does** count (it is part of the manuscript). |
| Colour | "Color figures are automatically posted in color on the IEEE Xplore website free of charge. The color-in-print charge is a flat rate of $275 per figure." | CIS-IFA J | Colour is free online; **figures must read in greyscale** (print is the default). Decide on colour-in-print at Article Setup **[SHLOK]**. |
| Open access | Hybrid. OA: "US$2800 for articles submitted in 2026"; IEEE Members 5% off, IEEE Society Members 20% off, no student discount, discounts not combinable; low-income-country discount for corresponding authors | CIS-IFA G | Choose traditional route (no APC) or OA at acceptance **[SHLOK]**. |
| Not published/under review elsewhere | "Authors will be asked to confirm that the work ... has not been published elsewhere nor is it currently under review by another publication." Conference records and book chapters not acceptable unless "significantly enhanced". "You can only submit your article to one publication at a time." | CIS-SUB; CIS-IFA B; AC-PROC; AC-POL (1, 1.1, 1.2) | **Withdraw/do not submit to Information Fusion or TMLR in parallel.** Disclose and cite any prior version (the project's review paper and earlier venue drafts are different works, but any text reuse must be declared, AC-POL "Recycling Content"). **[SHLOK confirms no other submission is live]** |
| Plagiarism screening | "Articles will be screened for plagiarism before acceptance." | XPLORE | Run a similarity check on the final PDF; paraphrase text shared with the project's other papers. |
| Prior-version / recycling statement | Authors must disclose prior publications/submissions and "very clearly state how the new submission differs" | AC-POL (1.1) | Cover-letter paragraph if any overlap. **[SHLOK]** |

## 2. Template and layout

| Requirement | Official text / value | Source | Build / action |
|---|---|---|---|
| Format | "PDF format; Singled-spaced, double column, standard IEEE published format." "All pages should be numbered." Manuscript must be "printable (all font embedded)" to enter review | CIS-IFA B, F; CIS-GUIDE | `\documentclass[journal]{IEEEtran}`; `build.sh` runs `pdffonts` and flags any non-embedded font (placeholder build: all embedded); IEEEtran journal mode prints the page number in the running head on every page (verified on the placeholder PDF). |
| Template | IEEE Template Selector https://template-selector.ieee.org/ (interactive; LaTeX = IEEEtran). CIS-IFA J: "An IEEE LaTeX style file can be obtained by visiting the IEEE Author Center" | AC-TPL; CIS-IFA J; CTAN | **IEEEtran v1.8b (2015/08/26)**, the CTAN and installed MiKTeX version; **IEEEtran.bst v1.14 (2015/08/26)**. I did not open the Template Selector (interactive); the CTAN release is the same class IEEE distributes, but if the Template Selector serves a newer sample file, diff `IEEEtran.cls` before submission **[SHLOK or next session: open the Selector, choose Journal -> TNNLS]**. |
| Title | "specific, concise, and descriptive"; avoid "new" or "novel"; avoid maths symbols in title. ESM: title capitalised (all nouns, pronouns, adjectives, verbs, adverbs, subordinating conjunctions) | AC-STRUCT; ESM II.A | Title in title case, no maths, no "novel/new". |
| Abstract | One paragraph, 150-250 words, self-contained "without abbreviations, footnotes, references, or mathematical equations"; "Highlight what is novel in your work"; no numbered equations or numbered citations | AC-STRUCT; ESM | Placeholder in `main.tex`; write last. |
| Index Terms | "4-5 keywords (index terms)" (CIS) / 3-5 (Author Center); alphabetical order, final paragraph of the Abstract section, capitalise the first word only; define acronyms; use IEEE Thesaurus terms where possible (free access via request form) | CIS-IFA F; AC-STRUCT; ESM | `IEEEkeywords` environment; terms not yet chosen **[SHLOK/author-team]**. |
| Section order | Title page, Abstract, Index Terms, (Nomenclature, optional), Introduction, body, Conclusion, Appendix(es), Acknowledgment, References, Photographs and Biographies | ESM II | Build follows this order; Acknowledgment replaced by the Declaration (C2); biographies only in the non-anonymous build. |
| Section headings | Primary: Roman numerals, centred, small caps; secondary: "A." italic flush left; "Reference and Acknowledgment headings ... are never enumerated"; enumeration of the other headings is "desirable, but not required" | ESM (Text Section Headings) | IEEEtran produces this by default. The Declaration section is `\section*`. |
| Footnotes | First footnote is unnumbered (dates, corresponding author, **full financial support**, prior presentation, affiliations, e-mail); no asterisks or daggers; third paragraph notice of supplementary material and colour figures | AC-STRUCT (First Footnote); ESM | Non-anonymous build: IEEEtran `\thanks{}` block with the funding line; funding is listed there "and not in the Acknowledgment". **[SHLOK: funding statement, corresponding-author e-mail, affiliations]** |
| Length of body | Authors "are encouraged to put detailed derivations in appendixes" | CIS-IFA F | Proofs go in `appendix.tex` (counts toward the 15) or the supplement (does not). |
| Inclusive/English | Standard English; fee-based editing services optional | CIS-IFA D; XPLORE ("must be written in standard English") | None. |

## 3. Authors, anonymity, identifiers, biographies

| Requirement | Official text / value | Source | Build / action |
|---|---|---|---|
| Author contact details | "detailed contact information for every author ... The paper will be returned without review if any such information is missing or incorrect." | CIS-IFA B | **[SHLOK: name, affiliation, e-mail, postal address of Shlok and of the supervising professor; the professor's full name is still `[AUTHOR]` in paper2/main.tex]** |
| ORCID | "All IEEE journals require an Open Researcher and Contributor ID (ORCID) for all authors ... The author will need a registered ORCID in order to submit a manuscript". Register at https://orcid.org/register | CIS-IFA C; AC-CHK1/2 | **[SHLOK: ORCID of both authors]** (Shlok and the supervising professor). |
| Corresponding author | "Agree on who will serve as the article's corresponding author" | AC-CHK2 | **[SHLOK/professor decide]** |
| Anonymisation | See C1. If double-anonymous: no names, affiliations, acknowledgements, funding; third-person self-citation; anonymised code/data links. IEEE gives **no** TNNLS-specific anonymisation instructions on the pages read; the Double-Anonymous Review Policy link on the journal home resolves to CIS-IFA. | CIS-IFA A; [NOT STATED] for details | Build default anonymous; links in the text use placeholders `\anonlink{...}`. **[SHLOK: read the Author Portal instructions after login]** |
| Author names in native language | Optional | CIS-IFA E; AC-STRUCT | Not used. |
| Biographies (final) | "Check that your files are complete including abstract, text, references, footnotes, biographies (for Papers), and figures captions." Bio = up to three paragraphs, begins with the full name in bold (must match the byline); education with years; positions; "Author photographs should be professional images of the head and shoulders." QR codes not accepted instead of bio/photo | CIS-IFA J; ESM (Biographies) | Biography stubs in `back/biographies.tex`, **non-anonymous build only**. **[SHLOK and professor: biographies and head-and-shoulder photos]** |
| Biographies/photos at submission | **[NOT STATED]** for TNNLS. Biographies are listed only in the final-manuscript step (CIS-IFA J). | - | Assume not needed for review (and they would break anonymity); confirm in the portal. |
| Photo file spec | JPEG acceptable for author photos only; PS, EPS, TIFF also accepted; name `gonza.tif`, `gonzb.pdf` (first five letters of surname, last letter replaced by first-name initial if surnames repeat) | AC-FMT | Final stage only. |

## 4. Figures, tables, equations

| Requirement | Official text / value | Source | Build / action |
|---|---|---|---|
| Figure formats | PS, EPS, PDF, PNG or TIFF; Office files only if originally drawn there; JPEG only for author photos; VSD/GIF/BMP not processable | AC-FMT | Figures as vector **PDF** (matplotlib `savefig(...pdf)`) with Type 1/TrueType embedded; fonts: Helvetica, Times New Roman, Arial, Cambria, Symbol recommended. |
| Resolution | Vector preferred; non-vector colour and greyscale **>300 dpi**; black-and-white line art **>600 dpi**; "increasing the resolution after image creation will not improve" quality | AC-RES | Use vector for all plots; any raster panel (e.g. example images) at >=300 dpi at final size. |
| Size | One column 3.5 in / 88.9 mm / 21 picas; two columns 7.16 in / 182 mm / 43 picas; avoid less than one column wide; maximum 7.16 x 8.8 in (182 x 220 mm) | AC-RES; AC-FMT | Figures sized `\columnwidth` or `\textwidth` (two-column floats `figure*`). |
| Type size in figures | "Type should appear approximately 9-10 point when viewed at full size"; consistent typefaces | AC-FMT | Plot fonts 8-10 pt at final width. |
| Colour-vision | "Evaluate your graphs by checking whether they can be interpreted correctly from a greyscale printout"; use colour and shape; thick lines with unique markers; direct labels | AC-GFX | Colour-blind-safe palette plus markers/linestyles in every plot. |
| Captions | "Do not include figure captions on the illustrations themselves." Captions "sufficiently clear so that the figures can be understood without detailed reference to the accompanying text." Axes "self-explanatory labels, not just symbols" | CIS-IFA J | Captions in LaTeX only. |
| Caption style | Figure: "Fig. 1." then caption, first word capitalised, no leading A/An/The. Table: label "TABLE I" (Roman numerals), caption centred above the table, no final period. Cite "Fig. N" even at sentence start; first citations in numerical order | ESM (Text Citation of Figures and Tables) | IEEEtran formats this by default; `\cref` is configured to print "Fig." and "Table"; check TABLE numbering is Roman (default in IEEEtran). |
| File naming (final) | `gonza1.tif`, tables `gonza.t1.tif` | AC-FMT | Final stage only. |
| Prohibited image | The "Lena image" is not accepted | AC-GFX; ESM | None used. |
| Equations | Follow the IEEE Mathematics Guide (https://docs.google.com/document/d/1vd5snQbsksmAlm8p6LWb8RmG2dc--a9hbaFzQUPkjxQ/edit); numbered consecutively "from the beginning of the article to the end"; variables lightface italic | AC-STRUCT (Equations); ESM | amsmath `equation`/`align`; no section-based numbering. |
| Reuse of third-party figures | Permission needed; credit | ESM | None planned. |

## 5. References

| Requirement | Official text / value | Source | Build / action |
|---|---|---|---|
| Style | "Put all references at the end of your paper in IEEE style" (IEEE Reference Guide https://docs.google.com/document/d/e/2PACX-1vSBoV_hTIURPZKtQkxI6bAONJtjyDLxQIUvCHi-XPzD8NKLcxRfZrpvQLFrjWZ3M6FFR_Obau3R-t63/pub ; check with the IEEE Reference Preparation Assistant https://refassist.ieee.org/) | CIS-IFA J; AC-CHK1; ESM | `\bibliographystyle{IEEEtran}` with IEEEtran.bst v1.14; numbered, in order of first citation. |
| Count / quality | No count limit. "Be sure to only cite references that directly support your work. Inflating citations by adding unnecessary references is considered a breach of publishing ethics." | AC-STRUCT | Cite only where a reference supports the sentence (Shlok's rule: include target-journal papers only where they genuinely support). |
| Links (Shlok's memory rule, not IEEE) | IEEEtran.bst v1.14 prints the `url` field ("[Online]. Available:") but **ignores `doi`** (checked in the .bst) | local check | `scripts/prepare_bib.py` writes `references-ieee.bib` from the unchanged copy `references.bib`: DOI -> `url = https://doi.org/...`, arXiv eprint -> `https://arxiv.org/abs/...` when no DOI/URL; hyperref `colorlinks` makes them blue. The script prints entries that still have no link (current result: 55 entries; 54 get a link, `finn1968adaptive` has no DOI, URL or arXiv id and needs one, or a replacement). Open issue: many `note` fields in references.bib are draft-internal remarks (for example "the proceedings record was not opened", "content not read") and print in the reference list; scrub before submission. |
| Preprints | Replace by published version when one exists (project rule) | project | Open item for citation-validator. |

## 6. Statements: funding, conflict of interest, ethics, data and code

| Requirement | Official text / value | Source | Build / action |
|---|---|---|---|
| Funding | Full financial support is stated in the first footnote, "listed here and not in the Acknowledgment" | AC-STRUCT (First Footnote) | **[SHLOK: funding or "no external funding" sentence; anonymised build omits it]** |
| Conflict of interest (authors) | The IEEE page on conflicts of interest addresses editors and reviewers (AC-POL "Conflict of Interest"); no author COI statement is required on any TNNLS page read. The Author Portal may ask for declarations (not read) | AC-POL; **[NOT STATED]** for TNNLS | Prepare a one-line "no competing interests" statement in the cover letter **[SHLOK confirms it is true]**. |
| Human/animal subjects | Required statement if human or animal research | AC-STRUCT; AC-POL | Not applicable (no human subjects; public benchmark images). State "not applicable" if the portal asks. |
| Data and code availability | **[NOT STATED]** as a requirement for TNNLS. IEEE asks for a README (description, size, platform, environment, major components, setup, run instructions, output description, contact) for uploaded datasets/code. Several TNNLS abstracts give a GitHub URL | AC-SUPP; deep dive 1.6 | Statement placed in the paper as a short unnumbered paragraph inside the Declaration section or Conclusion (anonymised link in review). Code/data go to Zenodo/GitHub; upload with a README as supplementary if wanted. **[SHLOK: decide whether to make the repository public or anonymous-mirror at submission.]** |
| Preprint | arXiv/TechRxiv posting allowed, with notice "This work has been submitted to the IEEE for possible publication. Copyright may be transferred without notice, after which this version may no longer be accessible."; a preprint would break double-anonymity (C1) | CIS-ARXIV; AC-POL (3.2) | **Do not post a preprint before the review decision unless Shlok chooses to.** |
| Preregistration / negative results policy | **[NOT STATED]** | deep dive 1.9 | Fit risk, not a rule. |

## 7. AI-use policy (verbatim, for the Declaration)

- CIS-IFA K: "The use of AI-generated text in an article shall be disclosed in the acknowledgements section of any paper submitted to an IEEE Conference or Periodical. The sections of the paper that use AI-generated text shall have a citation to the AI system used to generate the text."
- AC-POL, Use by Authors: "The use of content generated by artificial intelligence (AI) in an article (including but not limited to text, figures, images, and code) shall be disclosed in the acknowledgments section of any article submitted to an IEEE publication. The AI system used shall be identified, and specific sections of the article that use AI-generated content shall be identified and accompanied by a brief explanation regarding the level at which the AI system was used to generate the content." "The use of AI systems for editing and grammar enhancement is common practice and, as such, is generally outside the intent of the above policy. In this case, disclosure as noted above is not required, but recommended."
- Reviewers may not put manuscript content into public AI platforms (AC-POL).
- **Build decision (Shlok):** section "Declaration of Generative AI Use", no Acknowledgments section. See C2. The text of the Declaration must name each system and version, list which parts (text, figures, code, analysis scripts) and the level of use. **[SHLOK/orchestrator supplies the facts; the build leaves `[AUTHOR: ...]`.]** Because the AI-use pipeline here spans code and analysis, the Author Center scope (text, figures, images, code) is wider than a grammar note.

## 8. Supplementary material and multimedia

| Requirement | Official text / value | Source | Build / action |
|---|---|---|---|
| Formats | Text: TXT, DOC, DOCX, PDF; images JPG, TIF, PNG, GIF, PDF, PS, EPS, BMP; video MP4, MOV, WMV, AVI; audio MP3, AIFF, MOV, RA, WAV. "Supplementary files should be labeled as supplementary and uploaded as separate files during article submission." | AC-SUPP | `supplement/supplement.tex` compiles to a separate PDF. |
| Size limit | **[NOT STATED]** for TNNLS or for supplementary PDFs (only: graphical abstract < 45 KB recommended; video < 100 MB; audio < 3 MB) | AC-SUPP | Keep the supplement PDF modest (a few MB). |
| Excluded from page count | Yes | CIS-IFA H | Tier-3 comparison, extra tables, algorithm boxes, long proofs go here. |
| First-footnote notice | IEEE adds the notice "This article has supplementary material provided by the authors..." | ESM | None needed. |
| Datasets/code README | Sections listed in section 6 | AC-SUPP | `supplement/README-TEMPLATE.md` is not created; **[SHLOK decides]**. |
| Graphical abstract (optional) | 660 x 295 px, >=300 dpi, < 45 KB recommended, file name `gagraphic`; peer reviewed with the article; sans-serif >=16 px, 4.5:1 contrast | AC-SUPP | Not required by TNNLS pages. Optional. |
| Video (optional) | MP4, 16:9, 29.97 fps, < 100 MB, name `gavideo` plus static `gacovergraphic` | AC-SUPP | Not planned. |

## 9. Copyright, publishing agreement, final files

| Requirement | Official text / value | Source | Build / action |
|---|---|---|---|
| Copyright form | "authors are required to sign the IEEE Copyright Transfer Form before publication ... provided upon approval of the manuscript"; all-electronic, completed after final files are uploaded; questions to copyrights@ieee.org | CIS-IFA I; CIS-COPY | After acceptance **[SHLOK/professor sign]**. |
| Final files | Single zip with "all the source files of the peer approved version" (TeX/LaTeX/Word; no page-layout programs; no PostScript) | CIS-IFA J | Build keeps sources self-contained in `paper2-tnnls/`. |
| Page numbering (final) | All pages including illustrations in one series | CIS-IFA J | OK. |
| Color-in-print | $275 per figure, chosen at Article Setup | CIS-IFA J | See section 1. |

## 10. Submission steps (Author Portal; not signed in, steps from the pages)

1. Prepare: agree corresponding author; get ORCIDs; check files (AC-CHK2).
2. Open https://ieee.atyponrex.com/journal/tnnls (account needed; the page sits behind a Cloudflare check that was not bypassed in the earlier venue session) **[SHLOK does this step]**.
3. Choose article type (Full Paper) and keywords; enter contact details for every author; confirm no prior publication/concurrent submission; disclose related submissions.
4. Upload the PDF (printable, fonts embedded, double-column, numbered pages) and the supplement as separately labelled files; optional graphical abstract/video.
5. Receive manuscript ID; review by >= 2 reviewers; decisions via the portal.
6. After acceptance: final zip, biographies and photos, copyright form, colour-in-print choice, page-charge acknowledgement, OA choice.

Not found on any page read: time to first decision, acceptance rate, reviewer form, TNNLS-specific anonymisation text, any cover-letter requirement, any highlights requirement (none: TNNLS has no highlights, graphical abstract optional).

## 11. What Shlok must supply (consolidated)

1. ORCID, e-mail, postal address, affiliation for each author; supervising professor's full name; corresponding author decision.
2. Funding statement; confirmation of no competing interests.
3. Confirmation that the work is not under review elsewhere (Information Fusion, TMLR) and a prior-version/overlap statement if any.
4. Decision on anonymity handling (C1) and on repository visibility (anonymised mirror vs private until acceptance).
5. Facts for the Declaration of Generative AI Use (systems, versions, parts, level).
6. Biographies and photos (final stage only).
7. Open the Author Portal in a normal browser to read the portal's own checklist/anonymisation instructions, and open https://template-selector.ieee.org/ to confirm the template version.
8. Colour-in-print and OA choices (at acceptance); over-length charge awareness (USD 200/page above 10).
9. Index Terms (4-5), ideally from the IEEE Thesaurus.
