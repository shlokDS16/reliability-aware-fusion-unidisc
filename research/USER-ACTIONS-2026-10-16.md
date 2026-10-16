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
5. **Full-text downloads (need your yes).** Records passing title/abstract so far: 1,000 (954 from the
   free-source update + 46 from the subscription databases), plus the 100-record re-check sample, the 32
   C8 records and up to 7 title-resolved records; the 797 re-check frame only if the sample triggers it.
   By route (of the 1,000): OpenReview 403, arXiv 225, ACL Anthology 45 (open access, about 673 PDFs,
   roughly 1-2 GB); DOI only 197 (mostly need the e-gateway in your Chrome); Semantic Scholar id only 23
   and no identifier 107 (Claude looks these up first). Proposed: approve the open-access batch as one
   download job (Claude logs every file and hash), then do the DOI-only ones together through the e-gateway.

6a. **Adjudicator for full-text screening (criteria v1.5, route F or H):** C = claude-fable-5-1 only if
   you approve any usage spend it needs (or confirm there is none); otherwise route H: every full-text
   disagreement and 'adjudicate' row goes straight to you (no model fallback; Haiku is excluded because it
   made many of the title/abstract exclusions being re-checked). Route H adds those rows to your
   workload on top of the 15 percent validation sample. Decide before the first full-text row.

## Carried over from HANDOFF 4 (still open)
6. Human screening sample (218 records) + 120 disagreements (RAISE validation).
7. Professor's name, school, e-mail; ORCIDs.
8. OSF registration (retrospective) of the protocol; protocol freeze.
