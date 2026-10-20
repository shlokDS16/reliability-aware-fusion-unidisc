# Needs Shlok (collected 2026-10-16 while you were in class)

Do these together in one sitting. Claude keeps this list current; items are struck when done.

## In your Chrome (VIT access), with Claude in Chrome driving
1. **IEEE Xplore I3, I4, I5** (245, 41, 12 hits): CSV export refused with "file limit exceeded".
   Options: (a) retry the CSV links in `research/sources/search-raw/ieee-xplore/ieee-download-links.html`
   (the limit may be per day or per session); (b) the ACM route: Claude reads the result pages in the
   tab and saves the metadata as one JSONL file (needs your yes for that one file save).
   Also: I1 files hold 1,199 rows against 1,203 hits (230 + 506 + 463); 4 rows short in the 2026 slice,
   probably count drift between search and export. Claude will note it in the log unless you want a re-export.
2. ~~**SpringerLink**~~ (done: exported and ingested 2026-10-16): queries ready in `research/review/corpus/subscription-search-sheet.md` (S1'/S2' runs,
   title-only run A + full-text sample run B). Counts first, then your yes per CSV download.
3. ~~**ScienceDirect**~~ (done: 12 files ingested; rescue + dual title/abstract screening finished 2026-10-16 17:00): same; split runs because of the Boolean-operator limit per field. RIS export,
   your yes per download.

## Decisions / approvals
4. Commits: Claude committed the crash-surviving untracked files in the exp-003 worktree (f9041a9,
   local only, not pushed). Say if you want a different commit policy.
5. **Full-text downloads (need your yes).** Route table for the 1,000 title/abstract passes:
   `research/review/fulltext/ft-routes.jsonl` (metadata only, nothing downloaded).
   - Batch 1, open access: 774 URLs (OpenReview 403, arXiv 235, ACL 45, other OA 91; 3 of the OA ones are
     'bronze' = free to read, no licence stated). Roughly 1-2 GB. One logged download job, every file hashed.
   - Batch 2, e-gateway in your Chrome: 102 (IEEE 51, Elsevier 20, Springer Nature 20, ACM 4, 7 others).
     About 8 IEEE ones are CVPR/ICCV/WACV papers that are often free at CVF; Claude checks those first.
   - No download: 27 duplicates of known records; 97 without a findable full text (10 blog/product posts,
     6 sentence fragments, 81 reference fragments with no title match). 32 of them have a near-miss
     candidate (e.g. truncated or renamed titles); a 5-minute human check could rescue most.

6b. **Title resolution (D0033) is blocked by API limits.** The rerun stalled at 100 of 393 slow lookups
   (OpenAlex free budget used up, arXiv API 429, Semantic Scholar's shared pool); stopped 08:25, resumable
   from cache. Either (a) rerun after the OpenAlex reset (05:30 IST tomorrow), or (b) request a free
   Semantic Scholar API key (semanticscholar.org/product/api, you apply; Claude never handles the key in
   chat - put it in an environment variable yourself). D0033's check sample of 60 must complete before the
   design is decided; its 7+ queued records join dual screening after that.

5b. ~~**387 OpenReview papers need a decision~~ (resolved: option (b), your credentials in .env; download running at ~25/hour, 26 so far) (about 39 percent of the full-text set).** OpenReview now puts every
   automated request (site and API) behind a browser challenge, and these 387 have no arXiv version
   (research/review/fulltext/arxiv-map/unmapped.jsonl). Claude will not try to get past the challenge.
   Options: (a) you sign in to OpenReview in Chrome and download them yourself from a links page Claude
   builds (about 2-3 hours by hand); (b) you run a small script Claude writes that uses the official
   openreview-py client with YOUR account, credentials set by you in environment variables (Claude never
   sees them) - works only if authenticated API calls are not challenged; (c) ask the authors / skip and
   report as 'reports not retrieved' (not recommended at this size). 9 near-miss arXiv matches in
   arxiv-map/near-miss.jsonl also need a yes/no from you (most are clearly the same paper).

5c. **1,421 SpringerLink records have no abstract** (Crossref and Semantic Scholar had none for their DOIs), so
   they cannot go through the title/abstract rescue pass yet (list: screening/v2/rescue-subscription/
   pending-no-abstract.txt). Options: (a) a free Springer Nature Meta API key (dev.springernature.com; you
   register and put the key in an environment variable yourself) - Claude then fetches the abstracts
   officially; (b) Semantic Scholar retry after its rate limit resets; (c) screen them on title only and
   report it. Recommended: (a).

## Carried over from HANDOFF 4 (still open)
6. Human screening sample (218 records) + 120 disagreements (RAISE validation).
7. Professor's name, school, e-mail; ORCIDs.
8. OSF registration (retrospective) of the protocol; protocol freeze.

## Status 2026-10-16 ~17:00 IST (screening session)
9. **Full-text T1 model screening, batches 1-34, is complete**: 332 records, 228 include and 104 exclude,
   66 of them settled by adjudicator C (Fable). This is before your part. Per protocol s4 and criteria
   v1.6 s5, you screen the **human validation sample of T1 blind (without seeing any A, B or C row) before
   you look at any screener output**; Claude can prepare the sample sheet (records and full texts only)
   when you are ready.
10. Two new title/abstract passes from ScienceDirect (U06894, U07166) need full-text routes; Claude will
   look for open-access copies; if they are subscription-only they join the e-gateway list (item 5).
11. OpenReview: nothing needed from you while the download runs; Claude screens the PDFs in batches as
   they arrive.

## Status 2026-10-17 ~12:00 IST (screening session)
12. **Full-text T1 model screening is complete for everything downloaded: 715 records, 564 include and 151
   exclude** (99 settled by adjudicator C). Item 9 stands: the blind human validation sample of T1 comes
   before you look at any screener row; say when, and Claude prepares the sample sheet (records and full
   texts only).
13. OpenReview download complete: 4 notes no longer exist on OpenReview (M13187, M15046, M15574, M18918),
   recorded as X6 reports not retrieved. If you can find copies elsewhere, they can still be screened.

## Status 2026-10-17 ~15:00 IST (follow-up session; low-token work until the Mon 19 Oct reset)
14. **Human validation sample of T1 is ready (do this BEFORE you look at any T1 screener row).**
   Read `research/review/screening/human-validation-t1/INSTRUCTIONS.md` (one page), then fill
   `human-validation-t1-sheet.xlsx` in the same folder: 108 papers (15 percent of the 715, seed 20261016),
   include/exclude, one code, one quote each; about 6-10 hours, can be split. Save as
   `human-validation-t1-DONE.xlsx` and tell Claude. Until then do not open `analysis/screening/` or the other
   files the instructions list.
15. **E-gateway list updated** (in your Chrome, VIT access, when you choose): `research/review/fulltext/egateway-list.csv`,
   119 records (IEEE, Elsevier, Springer Nature, ACM and a few others), one row each with DOI link and an
   empty `downloaded` column. Your yes per download as before. Also 121 further open-access PDFs (arXiv,
   OpenReview, ACL, publisher OA links) for new T1 records are ready to fetch on your yes (no login except
   the OpenReview ones, which use your credential script as before).
16. **Decisions needed (Claude found these while counting the PRISMA flow, `analysis/prisma/prisma-flow.md`):**
   (a) 348 records the rescue screener passed (25 include, 323 unclear) in the free-source rescue pass never
   went to dual screening or full text; D0029 says dual queue, D0030 says straight to full text. Recommended:
   dual title/abstract screening first (as was done for the subscription rescue), after the reset.
   (b) The 1,243 seed-corpus records that passed title/abstract in the first round are not in any full-text
   tranche (the census read 176 of them). Do they get full-text screening under criteria v1.6? Recommended: yes,
   as a further tranche.
   (c) 55 open-access links failed (29 errors, 26 not PDFs); Claude retries or moves them to the e-gateway list.
17. Correction to item 5c (2026-10-17): 1,413 SpringerLink records still lack an abstract, not 1,421; 8 on that
   list later gained one and were already rescue-screened (analysis/prisma/prisma-flow.md). Options unchanged.
   Item 16 is otherwise unchanged; the "off by 8" point is resolved.
18. **Open-access downloads done (2026-10-17, your yes):** 81 of the 100 non-OpenReview open-access records for
   the new T1 records, plus 7 of the failed links recovered by the retry: 88 new PDFs, hashed in
   `research/review/fulltext/fetch-log.jsonl`, converted to text, each checked against its record title
   (`tools/ft_title_check.py`). 67 records still have no PDF: 30 behind HTTP 403 bot walls (ACM, ScienceDirect,
   SSRN, ResearchGate, Wiley), most of the rest behind bot-check pages (Elsevier, Springer, Nature, MDPI, IEEE)
   or dead links. Claude does not answer bot checks; these need your Chrome or the e-gateway. The list
   (`research/review/fulltext/oa-retry-unresolved.csv`) is regenerated after the OpenAlex free budget resets
   (05:30 IST); it is not final until then. Still waiting for your yes: 21 OpenReview PDFs (your credential
   script) and 17 + 102 e-gateway records.
19. **Downloads with your yes (2026-10-17 evening):** 21 of 21 OpenReview PDFs (your credential script) and 61 of the
   119 e-gateway records (all IEEE, via your Chrome with VIT access); all converted and title-checked. **58 need you
   by hand** (`research/review/fulltext/egateway-manual.csv`, reason per row): ScienceDirect 24 (Cloudflare check in
   the automated tab; Claude does not answer it), Springer 22 (chapters are not in VIT's subscription; journal PDFs
   started returning HTML/503 after a burst of 22 requests and the VIT access line then vanished from the page:
   **please open one Springer article yourself to check that VIT access still works**; Claude stopped all automated
   access), ACM 4 (Chrome saved no file from dl.acm.org), 8 others not attempted. Save each as
   `Downloads/<id>.pdf` and tell Claude to import.
20. **Human validation T1:** recorded as you asked (D0034): you checked the sample and judged it correct; no
   per-record rows, so the paper reports A-B agreement only and states the deviation. You may now look at T1 rows.

## Status 2026-10-18 ~13:00 IST (screening session; paused at 97 percent weekly until the Mon 19 Oct reset)
21. **Item 19 made easier:** the 58 hand downloads are now a readable checklist,
   `research/review/fulltext/egateway-manual-checklist.xlsx` (sheet "Start here": 9 steps; sheet "Papers": one row per
   paper, grouped by publisher, clickable link, file name to save as, Status drop-down, Note; sheet "Progress": counts).
   Check VIT access on one Springer article first. Save PDFs as `Downloads/<id>.pdf`, then say "import the e-gateway PDFs".
22. Full-text screening of the 170 newly retrieved records (part 19): 60 screened (t1b077-t1b082), 4 of 8 adjudications
   done; the rest (t1b083-t1b093 and 4 adjudications) continues after the weekly reset. Nothing needed from you for it.

## Status 2026-10-20 ~01:00 IST (overnight run)
23. **Full-text screening of T1 is complete: 885 records, 608 include, 277 exclude** (116 settled by adjudicator C;
   A-B agreement before adjudication kappa 0.895). Nothing needed from you for it.
24. **Decision needed: the re-check test came out positive (K = 4).** 4 of the 100 randomly sampled title/abstract
   exclusions were included at full text. The frozen rule (criteria v1.6 s5.2) then says: **screen all 797 re-check
   candidates at full text.** That needs their PDFs: Claude will build the route table (metadata only) and ask your
   yes for the open-access downloads, as before; subscription ones join the e-gateway list. Route table built (metadata only, `analysis/screening/ft-routes-recheck797-summary.json`): 82 of the 797 are already
   screened (the sample), 18 more already routed; **697 new: 577 open access** (arXiv 380, publisher OA 125, OpenReview 58,
   ACL 14; roughly 1-1.5 GB) **and 118 e-gateway** (IEEE 68, others 50), 2 with no identifier. Reply "yes, start the 797
   tranche" for the open-access downloads (logged, hashed, title-checked as before); the e-gateway ones go to a new
   checklist like item 21.

## Status 2026-10-20 day (execution session d7bb06; you are in class)
25. Your 08:00 answers are decision rows **D0035-D0043**. Items 16a, 16b and 24 above are therefore settled.
26. **The evening page lists everything for you**, in one place: `research/EVENING-2026-10-20.md`, section "New
   decisions" (N1-N6 and item 12) and "Hands-on" (3 biology papers, extraction check OQ5-04, two blind validation
   sheets, three e-gateway checklists). Do the validation sheets before you look at any screener row of their tranche.
27. T1 gate re-audit 2: PASS WITH CORRECTIONS for "T1 screened so far (interim)", 882 decided; fixes done.

## Status 2026-10-20 ~17:30 IST (session 92c0b6b9; screening frozen by your D0051)
28. **Screening is frozen (D0051).** The re-check tranche (R797) stopped at the batches already running; the seed-tranche
    downloads were stopped (276 of 1,219 PDFs fetched, none screened). Final screening numbers: `research/progress.md`
    HANDOFF 26 and `analysis/prisma/prisma-flow.md`. A fresh session writes the manuscript next.
29. **One more record for you as second screener (D0041/D0046): R0308.** Screener B fell back to another model after a
    safety stop in 2 of 2 sessions that read it (r797b036; r797b069 alone). Screener A excluded it (X2 pipeline). Add it
    to your 3 biology papers (`research/review/screening/human-p4/human-p4-sheet.xlsx` holds those 3; R0308 is listed in
    `analysis/screening/ft-r797/r797-pending-B.jsonl`). Text: `research/sources/md/fulltext-pymupdf/R0308.txt`.

## Status 2026-10-20 ~20:00 IST (manuscript session 0839c9f4; D0051 build)
Tonight's list is `research/EVENING-2026-10-20-paper1.md`: P1 (core papers missing from the 615 includes; options
A-C), P2 (extraction sample D0052, confirm), P3 (PRISMA seed-count fix, FYI); sheets for the 4 B-unavailable papers
(human-p4-sheet.xlsx + human-p4-sheet-R0308.xlsx) and the 9 D0039 fields (d0039-fields/d0039-fields-sheet.xlsx);
author details and ORCIDs; who checked what; final read-through Thursday. Earlier hands-on items (validation sheets
for R797 and S1243, e-gateway PDFs, OQ5-04 check) are moot under D0051 unless you reopen screening.
