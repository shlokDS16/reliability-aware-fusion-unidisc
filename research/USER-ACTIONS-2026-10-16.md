# Needs Shlok (collected 2026-10-16 while you were in class)

Do these together in one sitting. Claude keeps this list current; items are struck when done.

## In your Chrome (VIT access), with Claude in Chrome driving
1. **IEEE Xplore I3, I4, I5** (245, 41, 12 hits): CSV export refused with "file limit exceeded".
   Options: (a) retry the CSV links in `research/sources/search-raw/ieee-xplore/ieee-download-links.html`
   (the limit may be per day or per session); (b) the ACM route: Claude reads the result pages in the
   tab and saves the metadata as one JSONL file (needs your yes for that one file save).
   Also: I1 files hold 1,199 rows against 1,203 hits (230 + 506 + 463); 4 rows short in the 2026 slice,
   probably count drift between search and export. Claude will note it in the log unless you want a re-export.
2. **SpringerLink**: queries ready in `research/review/corpus/subscription-search-sheet.md` (S1'/S2' runs,
   title-only run A + full-text sample run B). Counts first, then your yes per CSV download.
3. **ScienceDirect**: same; split runs because of the Boolean-operator limit per field. RIS export,
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

## Carried over from HANDOFF 4 (still open)
6. Human screening sample (218 records) + 120 disagreements (RAISE validation).
7. Professor's name, school, e-mail; ORCIDs.
8. OSF registration (retrospective) of the protocol; protocol freeze.
