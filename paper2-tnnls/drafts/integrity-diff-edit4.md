# Integrity diff: final fix pass 4 (clarity-editor, 2026-10-30; baseline HEAD 2bf794d5 / 39062dcf)

Baseline copies: `git show HEAD:` of sections, tables, supplement and main.tex, saved to the session scratchpad `orig4/`.
Number table: `drafts/integrity-diff-edit4-numbers.md`. Nothing committed.

## Result

- Main: 15 pp. The last page is full in the left column and about 65 lines in the right. Supplement: 17 pp.
- Both build clean: 0 errors, 0 undefined references or citations, 0 overfull boxes over 2 pt, all fonts embedded, 0 column gaps.
- Floats end on p. 12 and the References start on p. 13, so no float follows the References.
- **No number changed. No citation key or label was added, removed or changed. No cross-reference was removed.**
- Numbers that left the main prose: 0.676, 0.678 and 0.682 (R3). They remain in supplement S-II (Tier-3 table and paragraph).
- Numbers added to the main prose: σ = 0.1 and "severity 3", from the C6-11 caveat (R2). Both values are already in V-C.
- Deviations box: 18 items before and after.
- Binding sentences: unchanged from edit 3. The four "NO" rows of the script are the dated edit-3 changes (D0097, "descriptive", and the
  A-8 pointer), not changes made in this pass.

## Changes by item

| Item | Change |
|---|---|
| R1 (D0102) | `scripts/tab_glance.py` rewritten and `tables/tab_families_glance.tex` regenerated. The column is now "Status", with status-map words only: "run, formal", "not run (gatekept)" and "headroom not met; H4 not run". No outcome word appears ("bounded null", "confirmed", "rejected", "not rejected" and "shown" are all gone). Study 1 and Study 2 are separate blocks with no cross-study row. Every status is asserted against its run file. S-D/S-D2 are one row; the three LG cells are one row "LG"; S-M matches the status map ("geometry-matched random gate"); B reads "one-word foil pairs". Caption: "Preregistered Families Reported in the Main Text (Status Only)", note "Status only; each study's Results give the outcomes ...". III-E: "lists the families reported in the main text with their status only; each study's Results give the outcomes". IV-B (N3): "lists the families reported in the main text with their status; supplement S-II maps all of them". The column width was set to 0.46 of the column, which fixes a 9.8 pt overfull box. |
| R2 | V-D: directly after the D0099 sentence, before the LG results, the C6-11 caveat: "Shot and speckle noise are close relatives of Gaussian noise, impulse noise is the structurally different cell, and severity 3 is not matched to σ = 0.1; no claim is made about corruption types not tested." |
| R3 | IV-C: the median and 20 % trimmed-mean sentences (JPEG and splice "below", noise 0.678/0.682 against 0.676) are deleted from the main text and replaced by a pointer: "The median and 20 % trimmed-mean combiners are reported with their exact intervals in supplement S-II". S-II already prints them with nets, exact intervals, n_d and B/MDD, and its M1-corrected first sentence. The trimmed-mean-at-flag-count sentence, which carries its bounds (0.023, 0.014, 0.017), stays. This option is shorter than adding the intervals in the text. |
| R4 | `scripts/tab_status_map.py` and its table: "out-of-sample sign prediction" becomes "out-of-sample sign agreement"; "hard-negative foil pairs" becomes "one-word foil pairs". No other row changed. |
| R6 | V-G and Limitations use the Table IV descriptions instead of code names. tbv becomes "the one-pass observed-position score"; ltex "the patch texture"; nbr "the codebook-neighbour distance"; s3 "the uncertainty of the B pass" (Table IV: 1 − max p of the pass that gives B); rad "the distance from the grid centre"; the KO-S-nbr row "the codebook-neighbour-distance features". The values are unchanged. |
| N1 | Supplement S-I Study 2 deviation: "5.0 GB" becomes "5.2 GB", with `% run: runs/P2-ENV/hf_cache_sizes.json:total_gb_decimal (= 5.229)`. |
| D0103 | III-E, IV-C (PS audit), V-C (fold audit), VI-C ("Both studies") and supplement S-I "Audits" now say "automated audits run in the authors' own pipeline (not independent reviews)" (grammar adapted; IV-C reads "an automated audit run in the authors' own pipeline, not an independent review"). S-I "Audits" lists the checks without role names: the plan review, the adversarial review, the code, commit-order and hash audit, and the fold and leak checks. S-I G(3): "was adopted within the authors' study pipeline under that delegation". S-VII: "checked by the plan's automated statistical review". Other role names printed as people were also neutralised: S-I deviation list "The fold builder's notes ... the fold check"; S-III "signed with conditions by the adversarial review"; main deviation (7) "The fold builder did not collect ...". The S-II pointer drops "red-team A1" and now reads "an earlier overview with estimates was deleted; decisions D0096 and D0102". The Declaration was not touched (D0101). |
| N5 | Table header comments now name the real generators: `tab_status_map.py`, `tab_glance.py` and `tab_tests_full.py`. This used the `script=` argument of `tablib.write`. Note: changing `tab_tests_full.py` (one argument, header only) goes slightly beyond the files named in the brief; N5 needed it, and its table changed only in its first comment line. |

## Must-not rescan (pdftotext -raw; main body before References, and supplement)

Main hits, all allowed:
- "Confirmation" (title); "preregistered confirmation" (bullet 3, refers to L1); "confirmed" (L1 only).
- "independent" three times in the mathematical sense (Lemma 1, independent-token approximation, independent families), and twice in "(not independent reviews)". The second use is the D0103 wording: it negates, so no audit is called independent.
- "not validated on UniDisc" twice (theory label); "unlike (10)" (mathematical); "generalised" three times (method name); "predict", "prediction" or "predictions" in non-theory senses ("trained to predict", conformal prediction, predictive uncertainty, stored predictions); "superiority" (required clause); "held-out labelled data" (a description of [8]).
- No hit for "bounded null", "statistician", "red team", "agent", outperform, better than, beats, competitive, fixes, addresses, explains (as a theory word), equivalent, screening, novel or we prove.

Supplement hits:
- "(not independent reviews)" (D0103); "none is described as independent"; "independent" in mathematics.
- "No Guarantee" and "not covered by the guarantee" (both Study 1); "threshold calibrated at the true-caption layout" (GATE-M threshold).
- "cannot explain, qualify or rescue" (binding A4.1.10); "superiority ... was not preregistered" (L-NI).
- "predicted" inside the must-not column of the families table (S-I), naming what is not allowed; "confirmed (one-sided)" (L1).
- The status map no longer has "prediction" (R4).

## Checks

Hidden-character scan of every .tex in sections/, tables/, supplement/ and main.tex: 0 hits.
