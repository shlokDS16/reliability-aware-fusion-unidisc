# DOCX build notes (Paper 2, IEEE TNNLS)

Decision D0093: the DOCX must be the two-column IEEE Transactions Word template. This folder holds the converter output;
the converter is `paper2-tnnls/scripts/make_docx.py` (helpers `docx_tex.py`, `docx_ast.py`, `docx_post.py`, `docx_verify.py`).
Written 2026-10-30. Nothing in `sections/`, `tables/`, `supplement/`, `main.tex` is touched; the script only reads them.

## Rebuild (one command)

```
cd paper2-tnnls && latexmk -pdf main.tex && latexmk -pdf -cd supplement/supplement.tex     # aux, bbl and PDFs must be current
python paper2-tnnls/scripts/make_docx.py                  # from the repository root; any working directory works
```

Options: `--camera` (non-anonymous build, `\anonfalse`: author block, `\thanks` notes as footnote-style paragraphs, biographies; output name
gets `_camera`; its text comparison against the anonymous PDF is meaningless), `--main-only`, `--render` (also exports each DOCX to
`*.word.pdf` through Microsoft Word, COM, for a visual check; skipped if Word is absent), `--keep DIR` (pandoc input, AST, raw DOCX,
table specs), `--no-verify`. Needs pandoc >= 3.1 on PATH, python-docx (system python), `pdftotext` (MiKTeX/poppler); LibreOffice is not
needed (and was not installed here; Word was used for the render check).

Outputs: `Paper2_TNNLS_manuscript.docx` (two sections, two columns), `Paper2_TNNLS_supplement.docx` (one section, one column, same styles;
IEEE has no supplement template), `verify_*.txt` (structure and text-comparison reports), `*.word.pdf` (Word render, only with `--render`).
The converter warns when `main.aux` is older than a source file.

## How it works

1. `docx_tex.py`: strips comments with TeX semantics (a comment line removes its line break), expands `\input`, resolves `\ifanon` (default from
   main.tex, `--camera` flips it), takes citation numbers from `main.aux` (`\bibcite`) and prints `[n]`, `[a]-[c]` (3 or more consecutive) like the
   `cite` package; `\cref/\Cref/\ref/\eqref` become the cleveref text from `main.aux` (`Section IV-B`, `Fig. 3`, `Table II`, `(5)`, `Sections IV-B and
   IV-C`, `Proposition 2`; external labels of the supplement via `\externaldocument`), each as an internal hyperlink; headings are numbered like the
   PDF (I., A., run-in `1)` and `\paragraph*` headings in italics, `Appendix A` plus title, unnumbered `\section*`); equations are numbered
   with the same counter as LaTeX and cross-checked against `main.aux` (a mismatch is a warning); `align` blocks are grouped by the numbered line;
   theorem-like environments become `Lemma 1 (title).` paragraphs with italic body; `\todo{}` becomes a yellow highlighted bold `[...]`;
   `\nolinkurl` becomes monospace; floats are pulled apart into caption, label, image or parsed `tabular` (rows, `\multicolumn`, booktabs
   rules, `\cmidrule` ranges, notes). `main.bbl` is parsed into the reference list (IEEEtran macros stripped, URLs as hyperlinks).
2. pandoc (LaTeX reader to JSON AST); `docx_ast.py` turns the sentinel paragraphs into structure (equations, tables, figures, bibliography,
   front matter) with the template's style names; pandoc writes the DOCX with the IEEE template as `--reference-doc`.
3. `docx_post.py` (python-docx): maps pandoc styles to the template (`Text`, `Heading 1/2`, `Title`, `Authors`, `Abstract` with "Abstract" in
   italics plus an em dash, `IndexTerms`, `Figure Caption`, `Table Title`, `References`, `Reference Head`, `Equation`), numbering of Heading 2/3 switched
   off (numbers are in the text, as in the PDF), reference paragraphs use the template's own `[1]` list definition, equation paragraphs get a
   centre tab and a right tab at the column width with the number flush right, sections and columns are rebuilt from the template's own
   `sectPr` (below), the template header (page number, running head) is kept with its "manuscript ID" line replaced by
   `IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS`, orphan template images and links are dropped, picture alt text with local paths is
   emptied, and core properties are anonymised (author "Anonymous"). Package contents were checked for personal names and local paths: none.
4. `docx_verify.py`: structure report and the text comparison below.

## Layout, columns, floats

- Page: Letter, margins 0.65 in left/right, 0.70 in top/bottom (template values). The template's first section (one column, type continuous,
  carries the header) holds the title and the author line only; the second section is `<w:cols w:num="2" w:space="720" w:equalWidth="0">` with two
  5040-twip (3.5 in) columns, and holds abstract, index terms and the whole body. This is the template's own order (its section break is after
  the author paragraph) and matches the PDF, where the abstract is in the left column.
- Single-column figures and tables sit in the column (3.5 in): image paragraph (`Figure Image`) plus `Figure Caption`; table title in two
  `Table Title` lines ("TABLE I" and the caption, small caps), the table, a `Table Note` paragraph.
- Two-column floats (`figure*`, `table*`) are one-column container tables, 7.2 in wide, that are Word floating tables (`w:tblpPr`, anchored to
  the margin, `tblpYSpec="top"`, centred, `tblOverlap never`). A wide figure container has two rows (picture, caption); a wide table container
  holds the "TABLE n" row, the caption row, the data rows with booktabs-like borders (1 pt top and bottom rule, 0.5 pt mid rules, `\cmidrule` limited to
  its columns) and a note row. Word places such a float at the top of the page that carries its anchor paragraph, spanning both columns and
  pushing the column text down, which reproduces `[!t]` placement. No continuous section breaks are used for floats (they would balance
  the columns on the preceding page).
- Table font size is chosen per table from the character count of its columns (6 to 8 pt, style `Table Text n`); column widths follow the
  longest cell per column. LaTeX `\resizebox` scaling is not reproduced.
- Figures are the PNG previews in `paper2-tnnls/figures/` (same basename as the PDF); `\textwidth` is 7.2 in and `\columnwidth` 3.5 in.

## Verification (Word render, structure, text)

Checked on a consistent snapshot (sources copied to a scratch folder and compiled with latexmk, so aux, bbl and PDF match the source) and again
on the live tree (whose `main.aux` was older than one edited section, as the converter warned); both gave the same picture:

- `python-docx`: manuscript has 2 sections: section 0 one column (title, authors), section 1 two columns of 5040 twips; the supplement has 1
  section with one column. Both open in Word (COM export to PDF succeeded: manuscript 15 to 17 pages depending on the source state, PDF 15 to 17;
  supplement 13 pages, PDF 14).
- Zero leftover sentinels, zero raw LaTeX commands in the text, zero undefined reference markers, every internal hyperlink has its bookmark,
  equation numbers run 1..15 without gaps and match `main.aux`, reference list has all 63 entries, tables and figure captions are numbered like
  the PDF (supplement S1..S22).
- Text against `pdftotext main.pdf` (running head, page numbers, hyphens removed): PDF words found in the DOCX 96.4 % (all tokens) and 97.9 % (prose
  words of three or more letters); 5-gram match 89.7 % (all tokens) and 94.8 % (prose). Supplement: 98.7 % and 99.8 % word recall, 5-gram 83.7 % and
  90.3 %. The PDF text that is not matched in sequence is: (a) text inside the vector figures (Fig. 1 labels, plot labels), which exist only as PNG
  in the DOCX; (b) math glyph strings, which Word stores as OMML and pdftotext reads as scattered letters; (c) table cells that pdftotext reads
  in a different order (every word is present: 29 of 31 prose spans in the last run; the other two are `S-Dec` and `edge-aware`
  hyphen splits). No paragraph of prose is missing; no DOCX paragraph lacks a PDF counterpart.

## Known differences from the PDF

- Equations are Word OMML (Cambria Math), so glyph shapes and line breaking differ; an `align` block with several lines is one aligned
  equation with one number (placed at the vertical centre), numbers are typed text, not Word fields, and cross-references are text with internal
  links, not Word REF fields: they do not renumber if someone edits the document.
- No drop cap for the first word (`\IEEEPARstart`); the letter is plain.
- `\todo` items are yellow highlighted bold, not red; links are blue without underline; running head is the journal name (template line for the
  manuscript ID replaced); page count differs from the PDF.
- Theorem bodies are italic text runs (math inside is upright); `Proof` blocks are the author's own `\emph{Proof.}` text.
- Long paths and URLs carry zero-width spaces after `/ _ - . ? = & % #` so that Word can break them (the PDF uses `\UrlBreaks`); copy and paste may
  include them.
- Wide-float placement is decided by Word (top of the anchor page), not by TeX, so figure and table positions can differ from the PDF.
- Not covered: algorithm2e environments, `\footnote` (none in the paper), photographs in biographies (`IEEEbiography` is flattened to bold name plus
  text), `\thanks` in the camera build is added as paragraphs instead of a real first-page footnote.
- The supplement has no running abstract or index terms; it keeps the S- numbering of sections, tables, figures, equations and propositions.

## Word layout pass (2026-10-30, after Shlok found Fig. 1 above the title in the DOCX)
- `scripts/docx_page1.py` runs after conversion (main manuscript only; needs Microsoft Word). It asks Word where each
  paragraph and float lands and places every wide (two-column) float, in source order, before the first paragraph that
  starts on its page: never page 1 (Word would draw it above the title) and at most one wide float per page (two stacked
  wide floats made Word leave the rest of the page blank). Skip with `--no-page1`; a failure prints `ERROR page-1 float check`.
- `docx_post.typeset_pass`: references 8 pt on exact 9 pt lines (IEEEtran), invisible U+200B break points in reference URLs
  (display text only; link targets unchanged), Word hyphenation on except title, author line and headings.
- `docx_tex`: IEEEtran's `\hskip 1em plus 0.5em minus 0.4em\relax` no longer leaks into references [48] and [62].
- Result at this commit: Word renders the manuscript in 15 pages (Fig. 1 top of page 2) and the supplement in 17.
  Always check the Word render (`--render`, then look at the `.word.pdf` pages), not only the LaTeX PDF.
