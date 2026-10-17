# Human validation of full-text tranche T1: instructions (one page)

**What this is.** 108 papers drawn at random (seed 20261016; 15 percent of the 715 T1 full texts, at
least 100) from the full-text set. You screen them at full text, include or exclude, before you see
any screener (A, B) or adjudicator (C) row of T1. Your rows are the reference for the screeners'
kappa (criteria v1.6 audit copy s4 item 6, protocol s4 step 3). A screener below 0.70 against you
triggers a revision of the rules and a rerun.

**Files.** Sheet: `human-validation-t1-sheet.xlsx` (same content in `.csv`). Each row has the
record id, the title and two local paths, relative to the repository folder: the PDF
(`research/sources/pdfs/fulltext/<id>.pdf`) and the text extraction the screeners read
(`research/sources/md/fulltext-pymupdf/<id>.txt`). Read the PDF; use the text file only to search.
The only rule text you need is `research/review/screening/criteria-v1.6-screener.md` (sections A-C:
definitions, rules, codes). It names no record and states no outcome.

**Do not open until your sheet is finished** (blindness):
- anything under `analysis/screening/` (screener rows, adjudication, agreement statistics, re-check files);
- `research/review/screening/criteria-v1.6.md` (the audit copy; it discusses individual records);
- `research/progress.md`, `research/USER-ACTIONS-*.md` beyond the item that sent you here, and any
  Claude status message that names record ids;
- the title/abstract screening files, `research/review/fulltext/ft-routes.jsonl` (its `screen` field holds
  earlier decisions) and the session notes.
If you open one by accident, write which one in the `note` column of the first row; it is reported.

**How to fill each row.**
1. `decision`: `include` or `exclude` (drop-down). If you cannot decide, pick the one you lean to and
   write "doubt" plus why in `note`. There is no "adjudicate" for you.
2. `code`: only for exclusions, one code, the first that applies in the order of section C
   (X8, X3, X5, X4, X0, X1, X2, X7; X6 is not used: every file here was retrieved).
3. `quote`: one contiguous passage of 6 to 40 words copied from the paper that carries the decision
   (for an include, the passage that shows the diffusion component generating text; for an exclude,
   the passage behind the code). `quote_location`: page and section, e.g. "p.5, s4.1".
4. `note`: optional, e.g. I1(a)/I1(b), nonlang_only, or a reading you were unsure of.

Work alone, without Claude or any other model reading the papers for you, and without web
searches about the papers' screening. You may stop and resume at any time.

**When done.** Save the sheet as `human-validation-t1-DONE.xlsx` in this folder and tell Claude. Claude
then records the file's sha256 and the date (so the rows are fixed before you see any A, B or C row),
computes kappa of A, B and C against you (2 x 2 with adjudicate counted as include, and 3 x 2), and
only then shows you the T1 screener rows and the adjudication queue for your author review (protocol
s4 step 4).

Rough effort: 3 to 6 minutes per paper if you read the abstract, method and experiments sections
first (about 6 to 10 hours in all; it can be split across days).
