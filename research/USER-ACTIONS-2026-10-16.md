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
5. Full texts for full-text screening: open-access PDFs (arXiv etc.) and paywalled ones via the
   e-gateway both need your yes before any download (count and size will be given first).

6a. **Adjudicator model for full-text screening (criteria v1.4, V4):** C = claude-fable-5-1 (A = Sonnet 5.5,
   B = Opus 5.5), fallback claude-haiku-5-5. Fable may draw usage credits on your plan; if so that is
   spend and needs your yes. Otherwise C falls back to Haiku 5.5 (decided now, before any full-text row).

## Carried over from HANDOFF 4 (still open)
6. Human screening sample (218 records) + 120 disagreements (RAISE validation).
7. Professor's name, school, e-mail; ORCIDs.
8. OSF registration (retrospective) of the protocol; protocol freeze.
