# Integrity diff: revision pass 3 (clarity-editor, 2026-10-30; baseline HEAD fa075e7f)

Baseline copies: session scratchpad `orig3/` (sections, tables, supplement.tex, main.tex at fa075e7f). Script: `drafts/integrity-diff-edit1.py`;
number table: `drafts/integrity-diff-edit3-numbers.md`. Nothing committed.

## 0. Restored: supplement edits lost at b508e292 (found while doing this pass)

`supplement/supplement.tex` at b508e292 (W2: V-G, S-VII, delegation wording) was written over a copy from 4ead5b4e. It dropped every
supplement change of edit passes 1 and 2 (commits 9dd240bc, 4bf23dde): xr-hyper; the proof of Proposition 2 moved from App. A; the PS
table; the Study 1 protocol details; Family B detail; the LRF search, slot checks and full feature table; and the S-VIII source list.
The main text still pointed to all of them; the proof of a main-text proposition was in neither PDF.
**Fix:** three-way merge (`git merge-file`; ours = 4bf23dde, base = 4ead5b4e, theirs = b508e292); 0 conflicts. Then this pass's edits
were merged onto the result (0 conflicts after normalising CRLF). Every W2 addition (S-VII, ablation tables, delegation record) and every
edit-1/2 move is present (grep checks: `xr-hyper`, `sup:proof-snrcorr`, `stab:ps`, `sup:protocol1`, `sup:lrfdetail`, `stab:features`,
`sup:sources`, S-VII heading, "delegated").

## 1. Result

- Main 15 pp (cap 15). Last page full. Supplement 17 pp. Both build clean: 0 errors, 0 undefined references or citations, 0 overfull
  boxes over 2 pt, all fonts embedded, 0 column gaps. Floats end on p. 12; References p. 14 to 15, with no float after them.
- Abstract 247 words.
- **No number changed.** Changes are restorations, the run-file corrections the coordinator ordered, or deletions of repeats:
  - M2: L3 Holm p printed as 0.382 (was 0.38; `a6_analysis.json:family_L.L3.p_holm` = 0.38169).
  - M1: the Tier-3 sentence in IV-C and S-II now states the table (noise: median 0.678, 20 % trimmed mean 0.682, hard gate 0.676;
    `tier3_fusion.json:cells.noise0.1.arms.*.acc`). The intervals contain 0 ("not distinguishable"). Under JPEG and splice both are
    below the hard gate (readings "below").
  - M4: "200 detection items" becomes "about 200 (Table III gives the exact count per corruption)". The table caption drops the
    "200". The Items column is unchanged (197, 198).
  - D0100: download printed as 5.2 GB (`runs/P2-ENV/hf_cache_sizes.json:total_gb_decimal` = 5.229) against "about 2 to 4 GB"
    quoted. The 584-test comment now points to runs/P2-A23-AUDIT and the A2.3 audit record (line 75). The 17-family / 0.58 comments
    point to SAP A6.7.
  - L-NI 90 % interval (0.009 to 0.053) restored beside the binding L-NI sentence in Intro and Conclusion (coordinator item 7; same
    values as the abstract and V-D).
  - Removed from prose: "200" (M4) and one repeat of "0.0004" (S-D sentences merged; the value stays in the text and the table).
- **Citation keys:** none added or removed; counts unchanged. **Labels:** new `tab:glance`. The section pointers in the regrouped
  Intro now point to whole sections.

## 2. Binding sentences and intended scope changes

All binding sentences are present verbatim except these intended changes:

| Item | Change | Authority |
|---|---|---|
| NEG {S} (IV-C), Conclusion, Limitations "Both studies", abstract | "random other caption" becomes "a random caption of an image sharing no annotated (COCO) category (category-disjoint)". Abstract: "...sharing no annotated object category" (no abbreviation) | D0097; verified in `exp_p2/gate/folds.py` assign_negatives. Study 2: `runs/P2-LRF-FOLD/folds_lrf.json` `neg_restricted` true for 533 of 533, length-matched `n_unrestricted` 0 |
| Clean-estimate sentence | "The clean-image estimate, descriptive, was positive ..." | coordinator item 7 |
| A-8 limitation | "card row A-8" becomes "(supplement S-I, Study 2 deviation 1)"; numbers unchanged | red-team W7, coordinator A1 |
| Abstract setting sentence | "We report two separately preregistered studies of image-text verification under image damage in one pretrained unified masked diffusion model (UniDisc, 1.4 billion parameters) on Common Objects in Context image-caption pairs." | Codex rewrite 1; frees the words for D0097 |
| Abstract scope | "not used to design or fit the frozen weighting" ("design" kept) | coordinator item 7 |
| "Only guarantee" sentence | "This is the only guarantee in the paper, and it applies only to the expected share of flagged tokens in a clean test pair exchangeable with the calibration pairs, which is at most alpha" | Codex rewrite 5 (scope beside the CRC statement) |
| Contribution list | Six Study 1 and three Study 2 items regrouped into four bullets (D0098). Every A4.2.4 element is kept in substance (bullet 4's point estimates are kept; the marginal non-overlap is now called "a descriptive observation"). "H-NOGO" becomes "headroom not met". The bullets do not link the studies | D0098 |
| Deviations | Study 1 (1) gains the r2/r3 clause (A5). New Study 1 (9): env-lock of the detection and main-test stages empty (A14; both files 0 bytes). Study 2 (1) "card row A-8 ... row A-9" becomes "a dated amendment ... a second". Study 2 (6) gains 5.2 GB. Now 18 items: 9 for Study 1, 9 for Study 2 | A5, A14, D0100 |

## 3. Other edits (coordinator items)

- A1: supplement Table S5 (estimates of P, PS, detection and H on one canvas) is deleted. `tables/supp_status_map_study1.tex` (status
  only) replaces it, with a pointer to each family's own table. `tables/tab_families_glance.tex` is placed at the end of III-E as
  Table I (decision words only, one block per study). Internal labels removed from the main prose: S-C, S-D, S-D2, S-M, S-Z, S-DN,
  E-dec, GATE-I, family R, R1 to R3, H-NOGO, Tier-3, SAP A2.3, Addendum A4 and A6 r1, card rows A-8 and A-9. E-pred stays only inside the
  binding R1.8 theory text. P, PS, H, L1 to L4, L-NI, L-LEN and LG remain, and Table I defines them.
- A3: the Reproducibility paragraph no longer claims an anonymised mirror. It states the repository with its commit history, the link
  withheld for review, availability to reviewers on request through the editor, release at camera-ready, and that the printed commit
  identifiers refer to it. Arrays (untracked, manifests) and the environment record are unchanged.
- A4: the level-of-use sentence now names the delegated reading (supplement S-I, A4 disclosure (3); D0076 and D0077). Both \todo{AUTHOR}
  items are kept.
- A6: `tables/supp_tests_full_study2.tex` is input in a new S-IV subsection, marked as preregistered output. V-D says the quantities are
  there.
- A7: the Q1/Q2 list is now two run-in paragraphs, so the overprint is gone.
- A11, A13 (supplement): "predict no ranking" becomes "imply no ranking"; "A code reading confirmed" becomes "showed". IST times become
  UTC (00:10 and 00:12 IST on 29 October become 18:40 and 18:42 UTC on 28 October). "the operating system restarted the laptop" becomes
  "the workstation restarted". "that he had not looked" becomes "of not having looked".
- A16 / V2-2(d): a Limitations sentence names the ablation variants whose intervals contain zero under noise: linear logit, B and D
  alone, s3 alone, attention pooling (V-G values, unchanged). The "does not show zero" sentence is moved out of V-G; S-VII already
  carries it.
- D0099: LG training-conditions sentence added in V-D (wording of D0099).
- AC item 8: one sentence in VI-B. The paper measures the model's own evidence and makes no claim of a verifier that ranks with
  dedicated encoders; the reference encoders are near ceiling (the word "competitive" is avoided: SPEC rule 5).
- Codex rewrites applied with substance kept: setting sentence; "evidence that the unified model computes itself"; the image-code
  probability sentence; the one-sided/two-sided rule; the CRC scope; the first-freeze sentence; alternatives (i) to (v) as a numbered
  list; detection paragraph leads with the frozen-rival result, labels the same-item result "same-item selection" and calls the
  marginal non-overlap descriptive. Also: Z_cal defined in one clause (from `exp_p2/gate/analysis_m4.py` z_cal); the Study 2
  negative rule stated in plain words (V-C); 2 449 eligible images explained (red-team arithmetic note, M11).

## 4. Must-not scan (pdftotext -raw, main body before References, and the supplement); every hit justified

Main:
- "Confirmation" (title, binding D0092); "preregistered confirmation" (bullet 3 heading, refers to L1); "confirmed" (L1 definition and
  the Table V row).
- "[AUTHOR: confirm ...]" placeholder (Shlok must answer).
- "independent" ×3: independent-token approximation, independent families, Lemma 1 (mathematical).
- "not validated on UniDisc" ×2: mandatory theory label.
- "unlike (10)": Prop. 2(v), mathematical.
- "generalised" ×3: method name (logistic generalised additive model).
- "predict": "trained to predict any masked token".
- "superiority": required clean-estimate clause (F12).

No hit for outperform, better than, beats, competitive, fixes, overcomes, addresses, equivalent, as good as, explains, accounts for,
consistent with, screening, novel, we prove, replication or SugarCrepe score.

Supplement:
- "not validated on UniDisc" (theory label).
- "independent" ×4 (mathematical or "not independent samples").
- "No Guarantee" (caption of the fresh-fold GATE-M arm table, a Study 1 object).
- "threshold calibrated at the true-caption layout" (the GATE-M threshold; not a selling word, not LRF).
- "cannot explain, qualify or rescue" (binding A4.1.10 sentence).
- "superiority ... was not preregistered" (L-NI note).
- "confirmed (one-sided)" (L1 row).
- "predicted sign": E-pred table, allowed by R1.7.

## 5. Checks

Hidden-character scan of every .tex under sections/, tables/, supplement/ and main.tex: 0 hits.
