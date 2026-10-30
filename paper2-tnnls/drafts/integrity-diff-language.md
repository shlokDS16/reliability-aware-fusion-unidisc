# Integrity diff: language edit (language expert, 2026-10-30; baseline = working tree at HEAD a37f3cac)

Nothing committed. Script: `drafts/integrity-diff-language.py ORIG_DIR paper2-tnnls` (ORIG_DIR = scratch copies of every
touched file, taken before the first edit). Evaluation and change log:
`research/reports/language-expert/2026-10-30-paper2-language-evaluation.md`.

## Result

- Numbers, `\cite` keys, `\label` keys, `\ref`/`\cref`/`\eqref` keys and all mathematics (display and inline): identical
  multisets before and after, main and supplement (tables below).
- Binding regions: every edit is typography (serial comma, `90\,\%` to `90\%`), with the exceptions listed under
  "Rows marked NO", none of which is a binding sentence.
- Must-not words: no count changed (the edit added none).
- Build: main 15 pp., supplement 18 pp.; 0 errors, 0 undefined references or citations, 0 overfull boxes over 2 pt, all fonts
  embedded, 0 column gaps. Pages 1 and 2 rendered at 45 dpi and checked: no float above the title; Fig. 1 at the top of p. 2.
- Length: main text 14,929 words in the PDF against 14,976 before (about 47 words shorter, well under a quarter column).
  Page 15 has the same fill as before (79 text lines).
- All `.tex` and `.bib` files are pure ASCII (no invisible or bidirectional characters).

## Rows marked NO (explained)

- *Contribution list*: the only non-comma change is the word "and" added to complete the list
  "(exact McNemar, Holm over three realistic corruptions, and $n$ fixed by a headroom rule)" (bullet 2 heading in parentheses;
  serial-comma completion, no change of substance). A rewording of the lead-in sentence "Each item was delivered whatever the
  analysis found" was tried and reverted; it is item B5 of the report.
- *Study 2 protocol*: "Family~L has three hypotheses under a fixed sequence then Holm" became "Family~L has three hypotheses,
  tested in a fixed sequence followed by Holm"; "Per the operations log" became "According to the operations log". Neither
  sentence is in SPEC rule 2's binding list (A6.12 and A6.13 sentences are elsewhere); substance unchanged.
- Two other non-typographic edits were tried in binding text and reverted: "bounds on the difference of" -> "difference:"
  (Tier-3 sentence) and the removal of the duplicated "under that delegation" (supplement A4 disclosure (3)); the latter is item
  B33 of the report.

## Edits outside binding regions that remove text

- Fig. 8 caption (`sections/study2.tex`, ablation): the sentence "setting a group to its mean gives inputs that the model did
  not see together in fitting; an interval away from zero shows that the frozen model's decisions depend on those inputs, not
  that the group alone detects anything" repeated verbatim the body sentence two paragraphs below; the caption now reads "(see
  the text for how a knockout interval is read)". The body sentence is unchanged. This also kept the main paper at 15 pages
  (the serial commas alone had pushed two reference lines to p. 16).
- Same caption: "Differences are variant minus reference; positive favours the variant." -> "A positive value favours the
  variant." (the caption had already said "variant minus the frozen LRF").

## Main paper (sections/*.tex)
- Numbers: 625 tokens before, 625 after; lost none; gained none.
- \cite keys: 97 before, 97 after; identical multiset.
- \label keys: 56 before, 56 after; identical multiset.
- \ref/\cref/\eqref keys: 79 before, 79 after; identical multiset.
- Math (display environments and inline $...$): 307 before, 307 after; identical multiset.

## Supplement (supplement/supplement.tex)
- Numbers: 1612 tokens before, 1612 after; lost none; gained none.
- \cite keys: 0 before, 0 after; identical multiset.
- \label keys: 51 before, 51 after; identical multiset.
- \ref/\cref/\eqref keys: 68 before, 68 after; identical multiset.
- Math (display environments and inline $...$): 611 before, 611 after; identical multiset.

## Binding regions (substance fixed; typography only)
Typography normalisation used for the check: thin spaces (`\,`) removed, a comma before a final `and`/`or` removed (serial comma), whitespace collapsed, `toward`/`towards`.

| Region | Raw text changed | Equal after typography normalisation |
|---|---|---|
| Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope) | yes | yes |
| Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix) | yes | NO |
| Time-input sentence (A4.3.1) | no | yes |
| Multiplicity sentence (A6.7) | no | yes |
| Preregistered definition and audit wording (rules 6, 9) | yes | yes |
| prop:crc and the only-guarantee paragraph (R1) | no | yes |
| Theory label (R1.8) | no | yes |
| Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3) | yes | yes |
| Detection with the M1 rival (A4.2.2 item 2) | no | yes |
| Family H (A5.9 prefix) | yes | yes |
| Tier-3 placement (A4.1.10) | yes | yes |
| Provenance disclosure (A6.13, D0094 clause) | yes | yes |
| Study 2 protocol: families and tests (A6.4-A6.7) | yes | NO |
| Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091) | yes | yes |
| Reference-encoder sentence (A6.6) | no | yes |
| Discussion VI-A (NEG 6.1 opening, H paragraph) | yes | yes |
| Limitations (SPEC section 7) | yes | yes |
| Conclusion (binding sentences repeated) | yes | yes |
| Declaration of Generative AI Use (fixed by the authors) | no | yes |
| Supplement: A4 disclosures | yes | yes |
| Supplement S-III family H (A5.9) | yes | yes |

### Every edit inside a binding region
- Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope): ...noise with standard deviation `0.1` -> `0.1,`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...over three realistic corruptions, `` -> `and`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...quality~10, Gaussian noise with `$\sigma=0.1$` -> `$\sigma=0.1$,`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...on 500 design images, `frozen` -> `frozen,`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...more than three points `(90\,\%` -> `(90\%`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...plans, hash pins, every `deviation` -> `deviation,`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...reported (\cref{sec:deviations}; supplement S-I, `S-II` -> `S-II,`
- Preregistered definition and audit wording (rules 6, 9): ...timestamp exists. The plans, `pins` -> `pins,`
- Preregistered definition and audit wording (rules 6, 9): ...commit order, the hash `checks` -> `checks,`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...quality~10, Gaussian noise with `$\sigma=0.10$` -> `$\sigma=0.10$,`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...each tested corruption the `90\,\%` -> `90\%`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...($0.000$ to $0.000$) under `noise` -> `noise,`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...$b$, $c$, $n_d$, the `98.33\,\%` -> `98.33\%`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...$n_d$, the 98.33\,\% Holm-level `intervals` -> `intervals,`
- Family H (A5.9 prefix): ...item was scored (disclosure, `caveats` -> `caveats,`
- Tier-3 placement (A4.1.10): ...token; the median and `20\,\%` -> `20\%`
- Tier-3 placement (A4.1.10): ...the gate flagged (exact `95\,\%` -> `95\%`
- Tier-3 placement (A4.1.10): ...the difference of 0.023, `0.014` -> `0.014,`
- Tier-3 placement (A4.1.10): ...those cells (every cell, `comparator` -> `comparator,`
- Tier-3 placement (A4.1.10): ...intervals only), no cell's `95\,\%` -> `95\%`
- Provenance disclosure (A6.13, D0094 clause): ...positive-control audit, its exploratory `comparators` -> `comparators,`
- Provenance disclosure (A6.13, D0094 clause): ...gradient-boosted trees, a multilayer `perceptron` -> `perceptron,`
- Provenance disclosure (A6.13, D0094 clause): ...the result of its `family~B` -> `family~B,`
- Study 2 protocol: families and tests (A6.4-A6.7): ...\paragraph*{Arms, `families` -> `families,`
- Study 2 protocol: families and tests (A6.4-A6.7): ...\cref{sec:setting-corruptions}. Family~L has three `hypotheses under` -> `hypotheses, tested in`
- Study 2 protocol: families and tests (A6.4-A6.7): ...under a fixed sequence `then` -> `followed by`
- Study 2 protocol: families and tests (A6.4-A6.7): ...claim in the title, `abstract` -> `abstract,`
- Study 2 protocol: families and tests (A6.4-A6.7): ...lower bound of the `90\,\%` -> `90\%`
- Study 2 protocol: families and tests (A6.4-A6.7): ...not matched to $\sigma=0.1$. `Per` -> `According to`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...to 0.802 (net 0.069, `95\,\%` -> `95\%`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...more than three points `(90\,\%` -> `(90\%`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...was detected (net 0.016, `95\,\%` -> `95\%`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...a reduction: the lowest `95\,\%` -> `95\%`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...(net 0.050), and the `95\,\%` -> `95\%`
- Discussion VI-A (NEG 6.1 opening, H paragraph): ...quality~10, Gaussian noise with `$\sigma=0.1$` -> `$\sigma=0.1$,`
- Limitations (SPEC section 7): ...One model, one data `set` -> `set,`
- Limitations (SPEC section 7): ...of UniDisc, its tokeniser, `CLIP` -> `CLIP,`
- Limitations (SPEC section 7): ...codes: it agreed on `98.8\,\%` -> `98.8\%`
- Limitations (SPEC section 7): ...agreed on 98.8\,\% and `98.9\,\%` -> `98.9\%`
- Limitations (SPEC section 7): ...and on at least `98.6\,\%` -> `98.6\%`
- Limitations (SPEC section 7): ...of the $B$ pass `alone` -> `alone,`
- Conclusion (binding sentences repeated): ...quality~10, Gaussian noise with `$\sigma=0.1$` -> `$\sigma=0.1$,`
- Conclusion (binding sentences repeated): ...to 0.802 (net 0.069, `95\,\%` -> `95\%`
- Conclusion (binding sentences repeated): ...more than three points `(90\,\%` -> `(90\%`
- Supplement: A4 disclosures: ...the title, abstract, highlights, `conclusion` -> `conclusion,`
- Supplement S-III family H (A5.9): ...S-D2, S-C), the calibration `check` -> `check,`
- Supplement S-III family H (A5.9): ...conditions by the adversarial `review` -> `review,`
- Supplement S-III family H (A5.9): ...primary family's corruptions, severities, `threshold` -> `threshold,`

## Must-not words (SPEC rule 5): occurrences in main + supplement prose, before -> after
A word that is present before and after is a pre-existing use (most are allowed contexts, e.g. 'only guarantee', 'does not show that the gate has no effect', 'first author'); the edit added none.

- calibrated: 2 -> 2
- guarantee: 7 -> 7
- validated: 4 -> 4
- fixes: 1 -> 1
- solution: 3 -> 3
- has no effect: 4 -> 4
- replication: 2 -> 2
- independent: 23 -> 23
- first: 31 -> 31


---

# Round 2: type (b) items approved by the lead (decision D0105), 2026-10-30

Baseline: scratch copies of the committed round-1 files (`orig2/`, taken before the first round-2 edit). Same script,
`drafts/integrity-diff-language.py orig2 paper2-tnnls`. Nothing committed.

## Result

- Build: main **15 pp.**, supplement 18 pp.; 0 errors, 0 undefined references or citations, 0 overfull boxes over 2 pt, all
  fonts embedded, 0 column gaps. Rendered all 15 main pages at 45 dpi and looked at pages 1-2 and every float page (pp. 2, 4,
  6, 7, 8, 10, 11, 12): no float above the title; floats where they were. Rendered supplement pp. 6 and 10 (restructured tables).
- Abstract: 248 words (whitespace split). B1 (+4), B2 (+1) and B3 (+1) took it to 253, so the pre-ruled overflow valve R8/F1
  was applied: the test phrase is now "exact one-sided McNemar test, probability value 0.0005", and the alpha clause stays in the
  Results ("preregistered one-sided $\alpha=0.05$", Section V-D) verbatim. The abstract's B2 is "three percentage points" only;
  "(0.03 in accuracy)" would have exceeded 250 words, so it is used in the body, Introduction and Conclusion.
- Every number change is intended: main prose lost `0.05` x2 (the abstract alpha clause, R8/F1; the merged exclusion clause, B16)
  and `0.10` x1 (B15, now `0.1`), and gained `0.03` x3 (B2; run key `family_L.L-NI.margin (= 0.03)`, added to the Conclusion's run
  comment). Supplement lost `4` (B27: "Fig.~4" became the cross-document reference `Fig.~\ref{M-fig:lrf_weights}`, which prints 6)
  and `6` (B26: "edit 6" removed), and gained `2` x8 (the `\vspace{2pt}` of the eight restructured table notes, B30).
- `\cite` and `\label` unchanged. References: main lost one `\cref{tab:glance}` and one `\cref{sec:study2-reference}` (two
  duplicate sentences removed to hold 15 pages, below); supplement gained `M-fig:lrf_weights` (B27).
- Mathematics: lost `$\sigma=0.10$` and `$128$` (B15: `$\sigma=0.1$`, plain 128); gained `$z$`, `$\mu_z$`, `$\sigma_z^2$` (B13, the
  symbols of the existing proof formula now defined) and `$p=0.006$`, `$p=0.011$` x2 (B22). No equation changed.
- Must-not words: no count changed. "independent" is unchanged (B11 held).
- Generated table `tables/tab_families_glance.tex` regenerated by `scripts/tab_glance.py` (B31): "not run (gatekept)" ->
  "not run (no P rejection)" (the first wording tried, "not run (no P rejection with $b>c$)", made the column-width table
  9.5 pt too wide); serial commas in two rows. No number changed.

## B19 and B24 (conditional)

- B19 "network rows": defined at first use (Section IV-C10) as "one row is one input sequence in a forward-pass batch". Source:
  the Study 1 draft, `paper2/sections/appendix.tex` app:cost ("network passes (one row of a batch)"), and the `n_rows` field of
  the items files (`exp_p2/gate/analysis_omni.py` lines 80-82).
- B24 "fixed time inequality": defined in supplement S-I, A4 disclosure (5), as "the current time plus the planned duration of the
  re-infilling stage and fixed margins had to fall before a deadline fixed in Addendum A4". Source: SAP Addendum A4, FOIL-first
  rule item 3 (`research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md`, the inequality with $W_{\rm S2}$, 0.3 h and 2 h). The
  main Deviations item (4) points there: "(a scheduling rule; supplement S-I)".

## Rule note on B31 and B30

- B31: the status words of the Study 1 status map are prescribed by SAP A4.2.5 item 6 ("not run (gatekept: P+ empty)"), which
  SPEC rule 2 lists as binding. The main table already printed a shortened form; the new wording follows D0105. The supplement
  status map (`tables/supp_status_map_study1.tex`) keeps the prescribed text. Main text Section IV-C "gatekept" became "conditional
  on" for consistency with the new table wording.
- B30: SAP A4.2.5 item 5 requires "the F7 limits in the caption" of the Tier-3 table, so Table S17's caption keeps the title and
  limits (a)-(d); its definitions, reading rules and source moved below the table. The other seven tables have a short
  title-case caption and all notes below.

## Edits made to hold the 15-page cap (text removed only where it repeated text that stays; no font or spacing change)

The round-2 clarifications (B4, B6, B7, B13, B19, B20 and others) added about 20 column lines and pushed the references to
p. 16. Removed or tightened:
1. Section IV-B, end of "Families and reading rules": "Table I lists the families reported in the main text with their status;
   supplement S-II maps all of them." (Section III-E says the same, and the Table I note says "supplement S-II maps every Study 1
   family".)
2. Table I note: "Status only; each study's Results give the outcomes." (the caption says "(Status Only)", and Section III-E says
   that each study's Results give the outcomes).
3. Section V-G: "This comparison was added after the Study 2 results and is not a test." (the subsection opens with "Exploratory;
   added after the primary, family H, and Study 2 results", and the Fig. 8 caption says "intervals only, no test").
4. Section VI-B, last sentence: "The paper measures the evidence that the model computes about its own inputs; it makes no claim of
   a verifier that ranks with dedicated encoders, and the two reference encoders are near ceiling on these items (Section V-E)."
   (Limitations, Study 2, keeps "The reference encoders almost solve this matching task (Section V-E); this paper makes no claim
   of a verifier that ranks with them", and the Introduction's scope paragraph states the object of measurement.)
5. Widow-line trims with unchanged meaning: "None of these works reports" -> "None of them reports" (II); "every image of the
   SugarCrepe release" -> "every SugarCrepe image" (III-D); "the reference rule decides wrongly" -> "the reference rule wrongly"
   (III-E); "(the TbV score, named after Trust but Verify [ref])" -> "(TbV, after Trust but Verify [ref])" (IV-B); "and that time was
   not recorded" -> "and were not timed" (V-F); Limitations "self-hosted in the sense of Section III-E, and the audits were automated
   audits run in" -> "self-hosted (Section III-E), and the audits were run automatically in" ("not independent reviews" kept, B11).

PDF word count of the main paper: 14,933 (14,929 after round 1).

## Round-2 tables (script output)

## Main paper (sections/*.tex)
- Numbers: 625 tokens before, 626 after; lost {'0.05': 2, '0.10': 1}; gained {'0.1': 1, '0.03': 3}.
- \cite keys: 97 before, 97 after; identical multiset.
- \label keys: 56 before, 56 after; identical multiset.
- \ref/\cref/\eqref keys: 79 before, 77 after; DIFFERENT: lost {'tab:glance': 1, 'sec:study2-reference': 1} gained {}.
- Math (display environments and inline $...$): 307 before, 312 after; DIFFERENT: lost ['\\sigma=0.10', '128'] gained ['\\sigma=0.1', 'z', '\\mu_z', '\\sigma_z^2', 'p=0.006', 'p=0.011'].

## Supplement (supplement/supplement.tex)
- Numbers: 1612 tokens before, 1618 after; lost {'4': 1, '6': 1}; gained {'2': 8}.
- \cite keys: 0 before, 0 after; identical multiset.
- \label keys: 51 before, 51 after; identical multiset.
- \ref/\cref/\eqref keys: 68 before, 69 after; DIFFERENT: lost {} gained {'M-fig:lrf_weights': 1}.
- Math (display environments and inline $...$): 611 before, 611 after; identical multiset.

## Binding regions (substance fixed; typography only)
Typography normalisation used for the check: thin spaces (`\,`) removed, a comma before a final `and`/`or` removed (serial comma), whitespace collapsed, `toward`/`towards`.

| Region | Raw text changed | Equal after typography normalisation |
|---|---|---|
| Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope) | yes | NO |
| Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix) | yes | NO |
| Time-input sentence (A4.3.1) | yes | NO |
| Multiplicity sentence (A6.7) | no | yes |
| Preregistered definition and audit wording (rules 6, 9) | no | yes |
| prop:crc and the only-guarantee paragraph (R1) | no | yes |
| Theory label (R1.8) | no | yes |
| Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3) | yes | NO |
| Detection with the M1 rival (A4.2.2 item 2) | yes | NO |
| Family H (A5.9 prefix) | no | yes |
| Tier-3 placement (A4.1.10) | no | yes |
| Provenance disclosure (A6.13, D0094 clause) | no | yes |
| Study 2 protocol: families and tests (A6.4-A6.7) | no | yes |
| Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091) | yes | NO |
| Reference-encoder sentence (A6.6) | no | yes |
| Discussion VI-A (NEG 6.1 opening, H paragraph) | no | yes |
| Limitations (SPEC section 7) | yes | NO |
| Conclusion (binding sentences repeated) | yes | NO |
| Declaration of Generative AI Use (fixed by the authors) | no | yes |
| Supplement: A4 disclosures | yes | NO |
| Supplement S-III family H (A5.9) | yes | NO |

### Every edit inside a binding region
- Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope): ...sharing no annotated object `category.` -> `category with the test image.`
- Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope): ...0.029 to 0.109; exact `` -> `one-sided`
- Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope): ...to 0.109; exact McNemar `test at the preregistered one-sided level 0.05,` -> `test,`
- Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope): ...no more than three `` -> `percentage`
- Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope): ...had been seen. This `is` -> `result holds`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...Each item was delivered `whatever` -> `regardless of`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...was delivered whatever the `analysis found;` -> `outcome;`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...items 1 and 2 `are` -> `belong to`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...and 2 are Study~1, `` -> `and`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...are Study~1, item 3 `is` -> `to`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...of an additive evidence `sum,` -> `sum. The condition is`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...image tokens are dependent, `with an extension` -> `and it is extended`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...splice. At the token `level` -> `level,`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...score separates code-level random `replacements (area` -> `replacements, with an area`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...the receiver operating characteristic `curve, AUROC,` -> `curve (AUROC) of`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...AUROC, 0.961 for a `patch,` -> `patch and`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...patch, 0.955 for swapped `codes)` -> `codes,`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...Gaussian noise (0.561 and `0.503); on` -> `0.503). On`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...descriptive; no paired test), `` -> `and`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...on JPEG the two `overlap, and in` -> `overlap. In`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...two directions on foil `captions: run, formal.` -> `captions were run as formal tests.`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...over the same three `corruptions):` -> `corruptions) was`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...same three corruptions): run; `` -> `its`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...three corruptions): run; headroom `` -> `condition was`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...run; headroom not met, `` -> `so`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...met, its test stage `` -> `was`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...no more than three `` -> `percentage`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...more than three points `(90\%` -> `(0.03 in accuracy; 90\%`
- Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix): ...had been seen. This `is` -> `result holds`
- Time-input sentence (A4.3.1): ...checkpoint contains no time-embedding `weights; the` -> `weights. The`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...quality~10, Gaussian noise with `$\sigma=0.10$,` -> `$\sigma=0.1$,`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...with $\sigma=0.10$, or a `$128$-pixel` -> `128-pixel`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...each, so an improvement `larger than 0.05 is excluded and` -> `or`
- Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3): ...after Holm correction over `three,` -> `the three hypotheses,`
- Detection with the M1 rival (A4.2.2 item 2): ...the evidence; the rival's `win` -> `higher AUROC`
- Detection with the M1 rival (A4.2.2 item 2): ...win is read as `` -> `a sign of`
- Detection with the M1 rival (A4.2.2 item 2): ...is read as this `label-circularity concern,` -> `label circularity,`
- Detection with the M1 rival (A4.2.2 item 2): ...label-circularity concern, not as `an account of` -> `evidence about`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...is therefore confirmed. This `is` -> `result holds`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...no more than three `` -> `percentage`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...more than three points `(90\%` -> `(0.03 in accuracy; 90\%`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...Holm-adjusted $p$ is 0.049, `a margin of` -> ``
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...0.017 to 0.103; one-sided `0.006,` -> `$p=0.006$,`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...0.103; one-sided 0.006, Holm-adjusted `0.011,` -> `$p=0.011$,`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...0.006, Holm-adjusted 0.011, two-sided `0.011).` -> `$p=0.011$).`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...The one-sided and Holm-adjusted `$p$` -> `$p$-values`
- Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091): ...and Holm-adjusted $p$ are `0.029` -> `both 0.029,`
- Limitations (SPEC section 7): ...2.} One model, one `data set,` -> `dataset,`
- Limitations (SPEC section 7): ...sharing no annotated COCO `category).` -> `category with the test image).`
- Limitations (SPEC section 7): ...The preregistration is self-hosted `in the sense of \cref{sec:setting-tests},` -> `(\cref{sec:setting-tests}),`
- Limitations (SPEC section 7): ...and the audits were `automated audits` -> ``
- Limitations (SPEC section 7): ...were automated audits run `` -> `automatically`
- Conclusion (binding sentences repeated): ...sharing no annotated COCO `category).` -> `category with the test image).`
- Conclusion (binding sentences repeated): ...no more than three `` -> `percentage`
- Conclusion (binding sentences repeated): ...more than three points `(90\%` -> `(0.03 in accuracy; 90\%`
- Supplement: A4 disclosures: ...the authors' study pipeline `under that delegation` -> ``
- Supplement: A4 disclosures: ...the main test was `read (decision` -> `read. Decision`
- Supplement: A4 disclosures: ...(decision records D0076 and `D0077;` -> `D0077 document this;`
- Supplement: A4 disclosures: ...D0077; D0077 corrects D0076's `wording: the` -> `wording (the`
- Supplement: A4 disclosures: ...end of the coherence `stage;` -> `stage (the current time plus the planned duration of the re-infilling stage and fixed margins had to fall before a deadline fixed in Addendum A4);`
- Supplement S-III family H (A5.9): ...pilot images, so the `family's test was not run. The` -> ``
- Supplement S-III family H (A5.9): ...It was specified in `SAP` -> ``
- Supplement S-III family H (A5.9): ...in SAP Addendum A5 `` -> `of the statistical analysis plan`

## Must-not words (SPEC rule 5): occurrences in main + supplement prose, before -> after
A word that is present before and after is a pre-existing use (most are allowed contexts, e.g. 'only guarantee', 'does not show that the gate has no effect', 'first author'); the edit added none.

- calibrated: 2 -> 2
- guarantee: 7 -> 7
- validated: 4 -> 4
- fixes: 1 -> 1
- solution: 3 -> 3
- has no effect: 4 -> 4
- replication: 2 -> 2
- independent: 23 -> 23
- first: 31 -> 31
