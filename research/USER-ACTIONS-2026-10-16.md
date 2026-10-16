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
