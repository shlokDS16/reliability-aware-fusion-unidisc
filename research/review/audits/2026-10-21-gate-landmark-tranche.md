PASS WITH FIXES (8 findings: 1 blocking for release, 4 text/number fixes, 3 minor provenance)

```yaml
agent: gate-auditor
date: 2026-10-21
brief: Gate audit of landmark tranche L (D0061-D0064), commits 59b136c..51acac8
sources_examined: [analysis/screening/ft-lmk/, analysis/screening/landmark/, analysis/prisma/prisma_flow.py, prisma-flow.json,
  paper/review/figures/fig01-prisma.pdf (+ .log), analysis/extraction/lmk/ (extraction-order.json, batch-log.jsonl, agent-map.txt,
  second-reader.json, EA/EB/EC), research/review/extraction/dispatch-log.jsonl, analysis/extraction/d0052/rq-results.json,
  analysis/rq1/rq1-landmark.json, paper/review/tables/{qa-summary,qa-per-study,sensitivity,sensitivity-landmark}.tex,
  sections 02, 05, 10, supplement.tex, supplement.pdf, research/ledgers/decisions.jsonl D0039/D0056/D0061-D0064,
  subagent transcripts of session bfefb6fe (first timestamps of lmx001-003)]
coverage: all five checks of the brief. Not covered: EA-EB agreement-2 numbers (no sentence cites them); content correctness of
  individual extraction values (validator's job); Figure 1 not re-rendered (its PDF text was read and compared).
claims:
  - statement: Every number in the changed sentences equals its recomputed source, except one table cell (F4) and one wording (F3)
    status: supported
    evidence: recomputation from FA/FB batch files, lmk-decisions-all.jsonl, records.jsonl dates, rq-results.json D0060.landmark
    level: E4
    confidence: 0.9
  - statement: No pre-existing value changed; reruns reproduce the committed outputs
    status: supported
    evidence: JSON diff 59b136c..HEAD (only additions); reruns of rq_analysis.py, prisma_flow.py, rq1_landmark.py, qa_tables.py
    level: E4
    confidence: 0.95
  - statement: Order fixed and committed before the first extraction; extracted set = positions 1-16; draw follows the rule
    status: supported
    evidence: 73c7b4b 10:08:20 IST; first EA transcript line 04:39:04.96Z = 10:09:04 IST
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns: [free RAM at each landmark launch (D0062) is not logged on disk]
next_test: {hypothesis: fixes F1-F5 leave every number unchanged, intervention: apply fixes and rebuild, primary_metric: diff of rq-results.json and PDF text, falsifier: any changed value, gpu_hours: 0}
```

## Check results

1. Numbers in changed sentences: PASS except F3, F4 (and F2 for disclosure).
   Recomputed independently from the per-batch FA/FB files (last row per id): 44 assessed, A=B on 44 decisions, include 42,
   exclude 2 X1 (M00595 theory-no-text, M00430 nontext), no adjudication; frame 47, covered 3 (M00285, M03631, M04373, all in
   rq1-includes.jsonl), 41 S1243 + 3 string-filter (M00595, M00430, M05571, all `snowball_only`, `auto_excluded: string filter,
   D0026`); years 1/4/3/10/22/2 (18 before 2025); mm text 18, multimodal 19, other 1, split 4. Every RQ1-RQ6 landmark count in
   05-rq-evidence.tex equals rq-results.json D0060.landmark / verdicts.landmark(_without_rejected). qa-summary.tex landmark
   column recounted from the qa-per-study.tex landmark rows (low reading): all nine cells match. Figure 1 PDF text: 44 identified
   (seed 41, string filter 3), sought 44, retrieved 44, assessed 44, excluded 2 X1, included 42, S1243 box "41 later assessed in
   tranche L" = prisma-flow.json landmark_tranche_D0061 and assessed_later_in_landmark_tranche_D0061. D0061 retrieval claims:
   35 PDFs fetched before 2026-10-21, 9 on 2026-10-21, 44 conversions ok with pdf_sha256 equal to fetch-log.
2. No pre-existing value changed: PASS. JSON diff 59b136c..HEAD: rq-results.json only adds D0060.landmark, landmark_meta,
   landmark_without_rejected, verdicts.landmark, verdicts.landmark_without_rejected; prisma-flow.json only adds
   landmark_tranche_D0061 and the S1243 field (pdfs_downloaded_before_freeze value unchanged); rq1-counts.json, sensitivity.tex,
   qa-table.jsonl unchanged; qa-summary.tex included/seed cells unchanged (labels shortened only). Reruns of rq_analysis.py,
   rq1_landmark.py and qa_tables.py left the tree clean; prisma_flow.py reproduced every value but reorders the keys of
   identified_not_screened_by_status (non-deterministic Counter order; restored with git checkout, not a value change).
3. Design claims: PASS. extraction-order.json touched only by 73c7b4b (10:08:20 +0530); order and frame_sha256 reproduce from
   random.Random(20261024); first EA sessions started 10:09:04 IST (transcript agent-a47bf40903056c656.jsonl). EA ids =
   positions 1-16 exactly, batch lmxNNN = position NNN. All 31 batch-log rows (EA 16 sessions incl. pass 2, EB 2, EC 2):
   model_ok true with the stated model (opus-5-5 / sonnet-5-5 / fable-5-1), isolation true, no flags. EC validator_exit 2 is
   the validator refusing role EC (as for d0052, whose EC sessions are not in its batch-log at all). Draw
   random.Random(20261025) over the prefix, k = max(2, ceil(16/10)) = 2 -> R0268, R0326, reproduced. Landmark enters no
   included/seed/combined estimate (check 2).
4. Overstatement: PASS except F3 and F5. Targeted, reported apart, 16 of 42 and "not a sample of any defined population" are
   stated in 02 (para "Landmark tranche", departures item), 05 (Population para), 10 and S6; QA1 non-comparability is stated in
   05 RQ6 and the qa-summary caption.
5. Decision rows: PASS. D0061 (frame, 41+3, 35+9 PDFs, sha256) and D0063 (order commit 73c7b4b, stop at 86-87 percent after
   position 16 per agent-map.txt, EB/EC models, k = 2, R0268/R0326, separate column, QA1 text-only) match disk. D0064: no
   extension beyond 16 (prefix 16). D0062: see F8.

## Findings

F1 (blocking for release). paper/review/supplement.tex:329: the backslash of `\ref` is a lone CR byte ("Table~" CR
"ef{tab:s-sens-landmark}"). Built supplement.pdf p. 29 prints "Table eftab:s-sens-landmark". The lone CR also stopped git's
autocrlf normalisation, so the whole file was committed with CRLF (blob at 59b136c: 0 CR; HEAD: 531 CRLF + 1 lone CR), which is
why the diff shows 1061 changed lines and hides the real edits. Fix: replace the CR byte with a backslash so the text reads `\ref{tab:s-sens-landmark}`, renormalise the file
to LF (`git add --renormalize`), rebuild supplement.pdf, confirm the diff against 59b136c is only the intended rows.

F2. Unresolved I1 split on R0523 (MMaDA-Parallel): screener A `a`, B `ab` (lmkb002 FA/FB). Under D0039 such secondary-field splits
go to the first author (route D0056) and are reported meanwhile as A's value with B's range; here A's value is used silently.
Affects 05-rq-evidence.tex:16 ("31 ... I1(a) ... 8 through both": range a 30-31, ab 8-9) and :53 ("Four of the 16 extracted
landmark studies are unified models": 5 under B's value; R0523 is in the extracted prefix, so the RQ5 landmark denominator is
4 or 5). 02-method.tex:108 "agreed on every record" is true for the decision only. Fix: resolve R0523 by the D0056 route, or
give the range in both sentences and say "agreed on the decision for every record".

F3. 05-rq-evidence.tex:32 "10 of the 16 claim in the abstract that they match or beat an autoregressive model": the field is CT6
(extractor-brief-v0.5.md:345: "matches, approaches, is competitive with or outperforms"). Fix: "match, approach or beat", as in the
included-studies sentence.

F4. paper/review/tables/sensitivity-landmark.tex:12 "5/11 0.46": exact 0.4545 -> 0.45. Double rounding: qa_tables.py:127 formats
the share already rounded to 3 dp in rq-results.json (0.455). Only cell affected among the landmark columns (all others checked
against count/of). Fix: format count/of for the unweighted landmark columns (or keep unrounded shares in rq-results.json).

F5. Stale after L: 10-limitations.tex:7 "2,020 identified records were not assessed at full text: 1,242 seed records ..." is
now false for 41 of them (prisma-flow.json assessed_later_in_landmark_tranche_D0061 = 41); the Figure 1 Description
(02-method.tex:100) says "1,242 of these are not assessed" while the figure box says "41 later assessed in tranche L"; the
string-filter box does not note the 3 later assessed. Fix: keep the at-freeze counts and add "(41 of them, and 3 records removed
by the string filter, were later assessed in the landmark tranche)" in 10 and the Description.

F6 (minor). 05-rq-evidence.tex:58 "Of the 19 sampled studies, in either column, that say code is released": there are now three
columns and the landmark links were not checked. Fix: "in the included or seed column".

F7 (minor provenance). analysis/extraction/lmk/EC/ecl002/ has no dispatch.json (ecl001, both EB, all EA and all d0052 EC
folders have one); the dispatch-log.jsonl row exists. Fix: file the session's dispatch.json if it survives in the scratch
dispatch root, else note its absence in agent-map.txt.

F8 (minor, unverifiable). D0062's evidence ("free RAM 3.5-4.2 GB ... wait_ram.ps1 checks") has no log on disk, and lmx001-003
were launched within 0.3 s (transcripts 04:39:04.96Z-04:39:05.26Z), which D0062 allows only at >= 4 GB free RAM. Fix: record
the RAM reading at each launch in agent-map.txt from now on; state in D0062's evidence that the readings were not logged.

## Out of scope (pre-existing, unchanged since 59b136c)
- Figure 1 Description (02-method.tex:100) says T1 "274 excluded"; the figure and 885 - 608 give 277.

## Re-check (2026-10-21, commit 15381e4)

PASS

- F1 fixed: supplement.tex has 0 CR bytes in HEAD (no changed text file holds a CR); line reads `Table~\ref{tab:s-sens-landmark}`;
  `git diff 59b136c -- paper/review/supplement.tex` is 7+/6- lines (acmart screen option from d1072c2, S1 rows 8/9/16a, S6 notes,
  the new \input). Rebuilt supplement.pdf p. 29: "Table S10 gives the same inputs"; no "eftab".
- F2 fixed: 05 RQ1 gives the 30/9 range on B's reading, RQ5 gives "five on screener B's reading"; checked EA-lmx011(-pass2) for
  R0523: factor types block-or-parallel, model-class, objective, rl (no synergy group), CT5 no, so RQ5 counts and verdict hold.
  02 says "every include or exclude decision". R0523 listed in research/AUTHOR-CHECKS-2026-10-21.md:58.
- F3 fixed ("match, approach or beat"; "match or beat" absent from main.pdf).
- F4 fixed: sensitivity-landmark.tex:12 now 5/11 0.45 (qa_tables.py prints count/of for the landmark columns); supplement.pdf shows it.
- F5 fixed: 10-limitations.tex:7 and the Figure 1 Description note the 41 seed records assessed later (text found in main.pdf).
- F6 fixed ("in the included or seed column").
- F7 withdrawn: analysis/extraction/lmk/EC/ecl002/dispatch.json is tracked and dated 12:36; my first listing was cut off by `head`.
- F8 resolved: readings now in both agent-map.txt files; spot-check of the session transcript: "Free RAM is 5.6 GB" at
  04:38:42Z, 22 s before lmx001-003 started (04:39:04Z), within D0057 (3 agents at >= 4.0 GB).
- Description now says 277 T1 exclusions = prisma-flow.json full_text_T1.exclude_incl_resolved 277 (= 885 - 608).
- No other number changed: 51acac8..15381e4 touches only the lines above in sections/tables; rq-results.json, prisma-flow.json,
  qa-summary.tex unchanged; tables/sensitivity.tex vs 59b136c is layout only (\begingroup\setlength{\tabcolsep}{4pt}, p{5.2cm} to
  p{4.6cm}, \endgroup); qa-per-study.tex change is layout only (tabcolsep 3.5pt, p{5.6cm} to p{4.0cm}).
- Out of scope, pre-existing since before 59b136c: supplement.pdf p. 21 (S5.1) prints "Figure ??" because supplement.tex:272
  uses \Mref{fig:taxonomy} for a label defined in the supplement itself (supplement.tex:268); \ref would resolve it.
