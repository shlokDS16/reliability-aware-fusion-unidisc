# Integrity diff: clarity and length edit 2 (clarity-editor, 2026-10-30; lead decisions after commit 9dd240bc)

Baseline: the files of commit 9dd240bc, copied before the first edit to the session scratchpad (`.../scratchpad/orig2/`). Script:
`drafts/integrity-diff-edit1.py` (same checks as edit 1); full table in `drafts/integrity-diff-edit2-numbers.md`. Nothing committed.

## Result

- **Page count: 15** (unchanged count; last page now about 0.25 page of references, was a full page). The 14-page target with 0.35 page of
  headroom for V-G was **not reached**: it needs about 0.6 page more (0.25 to end on p. 14, plus 0.35 headroom).
- **Binding sentences: 36 of 36 present**; one intended wording change: Limitations "Whether COCO images were in the pretraining data of
  UniDisc, its tokeniser, CLIP or SigLIP is unknown" (the Setting sentence on UniDisc's tokeniser was merged into this Limitations item; the
  item keeps its substance and gains the tokeniser). Deviations box: 17 items before and after (wording of Study 1 items 2 and 7 and
  Study 2 item 5 shortened).
- **Citation keys:** none removed, none added, no count change in the main text.
- **Labels:** `tab:ps` moved to the supplement as `stab:ps`; `app:snrcorr` (and the appendix) removed from the main text.
- **Numbers changed: none.** Removed numbers are moves or deletions of repeats (below). Numbers added to the prose are the positive-control
  values from the moved table `tables/tab_ps.tex` (unchanged file): 0.870, 0.870, 0.876, nets 0.000 and 0.006, 95 % intervals -0.008 to
  0.008 and -0.008 to 0.020, p 1.00 and 0.581, Holm-adjusted 1.00 and 1.00, 500 items (lead: "the PS result sentence(s) with their numbers
  stay in Section IV"). Run comment: `runs/P2-GATE-M4/analysis.json:ps.per_corruption.{patch,swap}.{acc_a,acc_b,delta,ci95,p,p_holm}`.

## Moves (lead decisions 1 and 2)

| From (main) | To (supplement) | Check |
|---|---|---|
| Appendix A, proof of `prop:snrcorr` (`sections/appendix.tex`, kept on disk as a record, no longer input; `\appendices` removed from main.tex) | S-II "Proof of Proposition 2 of the main paper (withholding with exchangeably correlated tokens)", `sup:proof-snrcorr` | 20 of 24 sentences verbatim; the other 4 are the heading and the edit-1 short forms of items (iii) and (iv), replaced by their full edit-0 text (closed form of b, numerical instance 0.9500, 0.4892, 0.5080); cross-references to the main paper's (9), (11), (12), (10), Fig. 2 and Proposition 2 resolve through `xr-hyper` (prefix `M-`; the supplement build needs `../main.aux`, which build.sh produces first) |
| Main-text pointer "\Cref{app:snrcorr} gives the full proof" | "The full proof is in supplement S-II." | proof sketch, statement, R1.8 label and Fig. 2 unchanged |
| Table II, positive control (`tables/tab_ps.tex`) | S-II "Positive control (PS, pipeline check)", `stab:ps`, with its full caption note and sources | PS result sentence with its numbers added in IV-C; detection table stays in the main text (decision 3) |

The S-VIII source list now cites main-paper figure and table numbers through `xr-hyper`, so they follow the renumbering (Table II is now the
detection table, III the feature groups, IV the Study 2 families, V the reference encoders).

## Further prose tightening (deletions of repeats; nothing binding removed)

- Intro: bullet 4 keeps its point estimates (0.961, 0.955, 0.561, 0.503, 0.607, 0.581, 0.756, 0.768) and points to the detection table for
  the intervals (0.493 to 0.513, 0.547 to 0.575, 0.569 to 0.593, 0.597 to 0.618, all in that table); bullet 8 keeps 0.733, 0.802, p = 0.0005,
  the L-LEN clause, the L-NI statement with its margin note and the {S2} scope, and drops the net, CI and L-NI interval (all in the abstract
  and V-D); "the name describes its design" kept once, in Section V.
- Section I outline and Section III opening sentence; Setting sentence "corruptions used by only one study"; Fig. 1 colour legend (the
  figure carries its own legend).
- Study 1: opening and Study 2 opening now point to Q1 and Q2 instead of restating them; the Neyman-Pearson sentence and the non-finite stop
  rule of LRF moved verbatim to S-I and S-IV; results preamble, mechanism, S2, exploratory and GATE-I sentences merged.
- Study 2: motivation sentence shortened (its citations unchanged: chair1986optimal, kittler1998combining, zhang2023provable,
  han2023trusted, li2026tcpfmc, ilse2018attention); arms sentence points to III-C; reference-encoder method sentence points to S-VI;
  Table IV and Table V notes and Fig. 4 and Fig. 5 captions shortened (no number removed that is not in the table, text or S-VIII).
- Discussion: VI-B alternatives (i) to (v) kept as one run-in sentence pointing to VI-C for their evidence; VI-A scope sentence shortened.
- Related work: two sentence merges; "It differs from the expected-loss statement..." merged into the wang2025conformal sentence.
- Conclusion: the closing "second backbone" sentence removed (stated in VI-B).
- Declaration: "the appendix" removed from the two lists of affected parts (there is no appendix now; the supplement, which holds the
  former appendix, stays listed). The disclosure's roles, systems, sections and level are otherwise unchanged.

## Checks

Build: main 15 pp and supplement clean (0 errors, 0 undefined references or citations, no overfull box over 2 pt, all fonts embedded,
0 column gaps, no float after the References). Must-not scan of the main body and the supplement: only the mandatory theory label "not
validated on UniDisc" remains. Hidden-character scan of all .tex: 0.
