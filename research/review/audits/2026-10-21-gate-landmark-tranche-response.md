# Response to the gate audit of the landmark tranche (2026-10-21)

Audit: research/review/audits/2026-10-21-gate-landmark-tranche.md (PASS WITH FIXES, 8 findings).

- F1 (blocking) fixed. The heredoc had turned the backslash of `\ref` into a carriage return in supplement.tex S6;
  restored to `Table~\ref{tab:s-sens-landmark}` and the file rewritten with LF line endings. `git diff 59b136c --
  paper/review/supplement.tex` now shows only the intended 7 lines; no other changed text file holds a bare CR.
- F2 fixed. R0523 is the only landmark record whose secondary fields differ (I1: A a, B ab). Under D0039 the counts
  keep A's value and give B's as a range: Section 5 RQ1 now reads "31 ... and 8 through both (30 and 9 on screener B's
  reading of one study, which awaits the first author)", and RQ5 "Four ... (five on screener B's reading of one study,
  which has no synergy ablation or claim)" (checked: EA-lmx011-pass2 has no synergy group, CT5 no, no synergy
  benchmark, so the RQ5 counts and verdict do not change). Section 2 now says the screeners agreed "on every include
  or exclude decision". R0523 is item 1 of research/AUTHOR-CHECKS-2026-10-21.md part 3.
- F3 fixed: "match, approach or beat" (CT6).
- F4 fixed: in Table S-sens-landmark the landmark columns print count/of and the exact quotient (one stratum, so the
  share is count/of); 5/11 now 0.45. tables/sensitivity.tex and qa-summary.tex unchanged by this fix.
- F5 fixed: Section 10 and the Figure 1 Description say 41 of the 1,242 seed records were assessed later in the
  landmark tranche.
- F6 fixed: "in the included or seed column".
- F7 not reproduced: dispatch.json is present in the session folder
  (scratchpad/ex-dispatch/EC-ecl002-6ad5a676-...) and in analysis/extraction/lmk/EC/ecl002/ (copied by postbatch.py).
- F8 addressed: the free-RAM readings seen before each launch are now logged in tools/ft-session/agent-map.txt
  (screeners) and analysis/extraction/lmk/agent-map.txt (extraction). lmx001-003 were launched together at 5.6 GB, which
  D0057 allows (3 agents at >= 4 GB); D0062's one-at-a-time rule applies only between 3 and 4 GB (screeners lmkb004 B,
  lmkb005 A and B).
- Outside the gate: the Figure 1 Description said T1 had 274 exclusions; the figure and prisma-flow.json
  (full_text_T1.exclude_incl_resolved) give 277 (274 + 3 resolved by the first author, D0058). The Description now says
  277.
