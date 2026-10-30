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
