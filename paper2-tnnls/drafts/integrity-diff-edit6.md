# Integrity diff: integration pass 6, figure set v3 (clarity-editor, 2026-10-30; baseline HEAD daa6108c)

Baseline copies: `git show HEAD:` in the session scratchpad `orig6/`. Number table: `drafts/integrity-diff-edit6-numbers.md`.
Nothing committed.

## Result

- Main: 15 pp. The last page is full, so the margin is zero lines. Supplement: 18 pp.
- Both build clean: 0 errors, 0 undefined references or citations, 0 overfull boxes over 2 pt, all fonts embedded, 0 column gaps.
- I rendered pages 1 to 15 at 45 dpi and looked at every page that carries a float.

Float map (figure or table: page; first mention):

| Float | Page | First mention |
|---|---|---|
| Fig. 1 (measurement) | p. 2, top | as fixed by the lead |
| Table I (families, status only) | p. 4 | III-E, same page |
| Fig. 2 (gate method and calibration) | p. 6, top, two-column | IV-A, p. 5 to 6 |
| Fig. 3 (frontier) | p. 6, right column | IV-A |
| Fig. 4 (family P) | p. 7 | IV-C1 |
| Fig. 5 (detection) | p. 8 | IV-C, p. 8 |
| Fig. 6 (LRF schematic and weights) | p. 10, top, with Table II below | V-B, p. 9 |
| Table II (Study 2 families) | p. 10 | V-D, p. 10 to 11 |
| Fig. 7 (family L) | p. 11, top | V-D, p. 11 |
| Table III (reference encoders) | p. 12, top left | V-E, p. 11 |
| Fig. 8 (ablation) | p. 12, left column | V-G, p. 11 to 12 |

No float sits above the title, and none follows the References (p. 14 to 15).

To keep Table II and Fig. 7 from drifting to p. 12 I moved their source definitions forward, to just before V-C. Earlier builds had
put them after the Discussion. Their wording is unchanged.

## Decisions on what moved to the supplement

- **Family P table (former Table I) moved to S-II as Table S-familyP (`stab:familyP`).** A4.2.5 item 1 requires a P-only summary
  figure and says only "the 98.33 percent interval is in the P table". It does not require that table in the main text. The table
  holds the 98.33 % intervals unchanged, and the P-only summary figure (Fig. 4) stays in the main text. Items 3 and 4 still hold:
  the PS table is its own table (S-II), and the P table carries nothing else. V2-1 also still holds, because the P discordance
  counts still appear only as numbers in the P table. The main text now points to it in IV-B, IV-C, the Fig. 4 caption and
  Deviations item (8). This was needed for the 15-page cap.
- **Detection table moved to S-II** (`stab:detection`), unchanged. Fig. 5 carries the A4.2.2 item 2 content in figure and caption:
  the M1 rival, with its name and sign in the row label ("sign chosen on same items"), and AUROC with 95 % intervals. The caption
  keeps the `% run:` comments for 492, 497 and p = 0.0004.
- **Feature table (main `tab_features_main`) dropped from the main text.** Fig. 6(a) shows the seven groups with their counts. The
  full table by name and formula was already in S-IV (`stab:features`), and V-B points to Fig. 6(a) and S-IV.
- **fig_margins moved to S-IV** (`sfig:margins`, new subsection "Item-level margins on the fresh fold (descriptive)"). The
  15-page cap bound, and the figure-smith had named this figure first candidate for the supplement. The S-IV text and caption state
  that it is descriptive only and that "superiority on clean images was not a preregistered hypothesis". V-D points to it in one
  sentence.

## Text cut to make room (repetition the figures now carry; nothing binding)

**IV-C**
- The S-C calibration statistic sentence (-3.59 against 2.13) and the clean-token flagged-share sentence (0.036 to 0.044; 0.089)
  are replaced by a pointer to Fig. 2(b),(c) and S-II. Both sets of values are already in the supplement calibration and flags
  tables.
- Detection: the frozen-rival sentence is kept, with its values and Holm p.
- The PS audit sentence is tightened, with the same facts (584, 5, 0; all 500 items; not read as a whole-pipeline check).
- The Tier-3 pointer is merged into the preceding sentence.

**Intro**
- Bullet 2 keeps the A4.2.4 detection substance and the point estimates 0.961, 0.955, 0.561 and 0.503. The values 0.607, 0.581,
  0.756 and 0.768 now live in Fig. 5 and S-II.
- The scope clause "reference encoders ... context, not rivals" is removed; VI-B's practical-significance sentence says the same.

**V-B**
- The features sentence points to Fig. 6(a).
- The hash sentence is shortened, with the same fact.
- The Fig. 6 caption is the new three-panel caption.

**V-E**
- Shortened to "Nearly every cell is at or next to its ceiling, so no reading beyond the stated accuracies is drawn, and no test is
  made". The drop intervals stay in Table III.

**V-G**
- The per-variant interval sentences are replaced by Fig. 8 and a classification sentence: which variants' intervals contain zero,
  lie below or lie above, as computed from the JSON and stated in the audited V-G.
- The plan's section 8 mandatory items are kept: the label, the A-SF selection-budget clause, the knockout sentence, "not a test",
  the seed spread and K = 336.
- The figure caption states the sign, as plan section 8 requires.
- The phrase "an interval that contains zero does not show ..." stays only in S-VII, as red-team A16 asks.
- Removed from the prose: the V-G interval values (-0.011, -0.002, -0.033, -0.009, -0.053, 0.040, -0.062 with their ends). They are
  plotted in Fig. 8 and printed in the S-VII tables.

**VI-A, VI-B, VI-D**
- The scope sentence after the binding 6.1 opening ("It concerns this gate at ...") is removed. The Limitations Study 1 item and the
  Conclusion carry the same scope.
- The VI-B list (5 items) is set as a run-in list, numbered (1) to (5).
- "A second backbone or a corruption held out of training would settle these questions; neither was run." The clause about a
  preregistered comparison with simpler rules is cut; Limitations still states that no ablation was preregistered.
- Deviations Study 1 (9) and Study 2 (5) are shortened; each keeps its fact.

**Related work**
- The sentence citing `li2023diffusionclassifier` for zero-shot classification by denoising error is removed. The key is still cited
  in the Introduction for the same point, and the reference list is unchanged (64 entries).

## Integrity

- **Numbers:** none changed. Every number removed from the main prose is in a main figure caption, a main table, or a supplement
  table (see the numbers file). New numbers in the main prose come only from the new figure captions: 300, 500, 0.01/0.05/0.10,
  10 000, 2 000, 2.5 to 97.5 %, 450, 35. Each has a `% run:` comment above its caption.
- **Citations:** no key added or removed. `li2023diffusionclassifier` drops from 2 to 1 occurrences.
- **Labels:** removed from main: `tab:familyP`, `tab:detection`, `tab:features` (now `stab:familyP`, `stab:detection`, and the existing
  `stab:features` in the supplement). New: `fig:gate-method`, `fig:detection`, `fig:ablation`. In the supplement, `sfig:margins` and
  `stab:familyP` are new.
- **Binding sentences:** all present. The four "NO" rows of the script are the dated edit-3 changes. Deviations box: 18 items.
- **Must-not:** the new caption text adds "guarantee" only for Prop. 1 (CRC), "descriptive", and "exploratory". The ablation caption
  carries no better/worse words.
