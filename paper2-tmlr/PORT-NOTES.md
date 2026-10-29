# Paper 2: TMLR-format port (2026-10-29)

Format port of `../paper2/` (Elsevier Information Fusion version, untouched) to the Transactions on Machine Learning Research (TMLR)
LaTeX style, in anonymous submission mode. Every number, claim, table and algorithm is as in `../paper2/sections/`. Build:
`latexmk -pdf main.tex` inside `paper2-tmlr/` (US Letter, 41 pages, 0 undefined references or citations, 0 overfull boxes).
Figures are read from `../paper2/figures/` through `\graphicspath{{../paper2/}}` (no binaries copied). Web content below was read as data.

## Sources read
- Author guide: https://jmlr.org/tmlr/author-guide.html (fetched 2026-10-29; the page itself gives the style-file URL).
- Editorial policies: https://jmlr.org/tmlr/editorial-policies.html (anonymity, LLM policy, originality, rejected-paper visibility).
- TMLR home: https://jmlr.org/tmlr/ (no further submission rules on the page).
- Style file (downloaded to `style/tmlr-style.zip`, extracted to `style/tmlr-style-file-main/`; zip and its PDFs are git-ignored):
  https://github.com/JmlrOrg/tmlr-style-file/archive/refs/heads/main.zip. Its README is one line; the rules come from its example
  paper `style/tmlr-style-file-main/main.tex` and `tmlr.sty`. `tmlr.sty`, `tmlr.bst` and `fancyhdr.sty` are copied unchanged to
  this folder so the build is self-contained (the style must not be modified).
- Venue comparison: `research/paper2/venue/VENUE-OPTIONS-2026-10-29.md`, TMLR section.

## TMLR rules applied
| Rule | Source | Applied as |
|---|---|---|
| Use the TMLR LaTeX style and template; PDF output | author guide; style example | `\documentclass[10pt]{article}`, `\usepackage{tmlr}` with no option (submission mode: header "Under review as submission to TMLR", "Anonymous authors / Paper under double-blind review") |
| Do not use `[accepted]` or `[preprint]` in the submission | style example `main.tex` comments | not used; they de-anonymise |
| Double-blind; authors hidden; non-anonymous submissions are rejected | author guide; editorial policies; example `main.tex` | `\author{Anonymous authors}`; no names, affiliations or e-mails anywhere (including source comments) |
| Do not change formatting parameters or the text rectangle | example `main.tex`, "Final instructions" | only float-placement parameters (`topfraction` etc., allowed by LaTeX, not page geometry) are set in `main.tex`; `tmlr.sty` untouched |
| US Letter paper | example `main.tex` | set by `tmlr.sty` (8.5 x 11 in) |
| Abstract: one paragraph | example `main.tex` | abstract is a single paragraph (same text as the Elsevier version) |
| Title in the TMLR title format | `tmlr.sty` | `\title{...}` same wording as the Elsevier version |
| Citations: natbib author-year, `\citet` in the sentence, `\citep` in parentheses; references alphabetical | example `main.tex` section "Citations within the text" | all `\cite` converted to `\citep`; "Zhou and Lu" and "Gomes et al." written-out names became `\citet`; `\bibliographystyle{tmlr}` (`tmlr.bst`) |
| No page limit; length must be justified by content; long main text may delay review | author guide | no content cut; 41 pages in total |
| Appendix after the references, in the same PDF | author guide | `\appendix` placed after `\bibliography`; sections A to D unchanged; in-text pointers now read "Appendix A" (see below) |
| Supplementary material up to 100 MB, PDF or ZIP, anonymised | author guide | availability paragraph points to an anonymised artefact (placeholder) |
| Unnumbered end sections as third-level headings (broader impact, author contributions, acknowledgments) | example `main.tex` | two unnumbered sections `\subsubsection*{...}` before the references (see below) |
| Broader impact statement only if the work carries a significant risk of harm | author guide | none added |
| Acknowledgments, author contributions, funding: only after acceptance and de-anonymisation; funding and competing interests go in the OpenReview form | example `main.tex`; author guide | CRediT, funding, competing-interest and acknowledgement sections of the Elsevier version are not in this PDF |
| LLMs may be used as general-purpose assistive tools; authors responsible; no disclosure required; LLMs cannot be authors | editorial policies | no disclosure required, so the Declaration of generative AI use section is extra and permitted; kept per the project rule (see below) |
| No reuse of text, figures or results with another archival paper under submission; arXiv preprints allowed; no link to a version naming the authors | editorial policies; author guide | see "Open flags" |
| Rejected submissions stay public on OpenReview | editorial policies | see "Open flags" |
| Figure caption below, table caption above; tables and figures centred, legible | example `main.tex` | unchanged from the source sections |

No Elsevier highlights block and no keywords block: the TMLR template has neither, and the author guide does not ask for them.
The 250-word abstract limit and the reference limit of the Elsevier version no longer apply; the abstract text is unchanged.

## Layout fix (float queue)
Floats keep `[t]` or `[!tbp]` in the section files; `main.tex` raises the float fractions (`topfraction` 0.9, `bottomfraction` 0.8,
`textfraction` 0.1, `floatpagefraction` 0.75, `topnumber` 3, `bottomnumber` 2, `totalnumber` 5) and calls `\FloatBarrier`
(`placeins`) at the end of every numbered section, so no float is carried into the next section. Checked on the PDF: every
table, figure and algorithm is on the page of its first in-section reference or the next page, except tables that are cited from an
earlier section as forward pointers (Table 1 notation, the appendix tables) and the Tier 3 table (page 28, referenced on page 27).
Figure 1 appears on page 19 at the end of the protocol section, as in the Elsevier version.

## Anonymisation
- Author block: removed (anonymous). Affiliation, postal address, corresponding-author line, CRediT names: removed.
- GitHub, Zenodo and OSF links: none were in the text; the Elsevier "Data availability" placeholder is replaced by an unnumbered
  section "Reproducibility and artefact availability" with a red placeholder for an anonymised-artefact link, and a statement of what
  will be released: code at commit `164a18a5` (`exp_p2/`, tests), the fold file (SHA-256 `450edb54...f311`), preregistration card,
  statistical analysis plan (SHA-256 `b4e0bf57...6c47`), per-item scores and predictions of every cited run directory, analysis and
  figure scripts, licence; COCO, UniDisc and tokenizer weights are third-party and not redistributed; a permanent de-anonymised
  record with a DOI after review. Commit and file hashes are content identifiers, not identities.
- "Our previous work": none in the text and no self-citation in `references.bib` (checked by search for author names and for the
  review paper). The companion review is not mentioned.
- Source comments naming a person (a "Shlok's decision" comment in `declarations.tex`) removed by rewriting that file; no name,
  institution or place appears in `sections/` or `main.tex`.
- The working-title todo "settle the scope-fit question with the supervising professor" (discussion, red text) is an open author
  item and must be deleted before submission; it names a role, not a person.
- Run-directory paths (`runs/P2-GATE-...`) and the hardware line (one 12 GB laptop GPU) are kept; they identify no author.

## Declaration of generative AI use
Kept only as the unnumbered section "Declaration of generative AI use", before the references. Its wording is the red AUTHOR
placeholder (the exact tools and extent are for Shlok to supply). AI is mentioned nowhere else in the PDF (the Elsevier todo that
said "do not draw it with a generative image tool" was reworded). TMLR gives no rule on anonymising this section; the section
names no author, so it is safe as written, but the final wording must contain no author-identifying detail.

## Other edits to the section files (all non-numerical)
- `\cite` to `\citep` / `\citet` (natbib); 6 phrases "this journal" / "the journal" became "Information Fusion" (introduction 2,
  related 2, discussion 2), because the sentences describe prior work in that journal, not the target venue.
- Bare `\ref{app:...}` became `Appendix~\ref{app:...}` (13 places); the Elsevier version printed "Appendix Appendix D" once.
- Introduction todo about Figure 1: removed "per IF anatomy rule 31" and the generative-tool sentence.
- Preregistered wording rules in the protocol and Appendix A still say "title, abstract, highlights, conclusion"; they quote the
  preregistration (which named a highlights list) and are left unchanged. This version has no highlights.
- `main.tex` adds a font-shape declaration (`scit` to small caps) to silence a Latin Modern warning inside italic text.
- All `\todo` / `[AUTHOR: ...]` / `[RESULT: ...]` items of the Elsevier version are kept (red); none was filled.
- `references.bib` is a copy; only the first five comment lines (Elsevier header) were replaced. Two bibtex warnings: empty
  publisher fields for `lezama2022tokencritic` and `lin2014coco` (both render correctly).

## Open flags for the authors
1. TMLR keeps a rejected submission public on OpenReview (anonymous unless the authors reveal themselves, which bars resubmission).
2. Originality: the same authors' review paper goes to a different journal. TMLR bars reuse of text, figures or results with any
   archival paper under submission elsewhere; the text of this paper contains no review text, but the overlap in topic should be
   stated honestly in the OpenReview form (not in the PDF).
3. The author guide gives no rule on links to code or on self-citation; the port follows the usual double-blind practice
   (no link that names an author, institution or account).
4. Venue-specific content of the Elsevier version (fusion framing, discussion of Information Fusion papers, subsection "Where the
   work sits in information fusion") is kept as is, per the instruction not to rewrite; for a TMLR audience it may deserve a
   shorter fusion framing, which is a content decision, not a format one.
5. `\todo` items must be resolved before upload; the OpenReview profiles of all authors must be complete (author guide).
