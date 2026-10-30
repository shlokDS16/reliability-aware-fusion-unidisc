# Integrity diff: clarity and length edit 1 (clarity-editor, 2026-10-30)

Scope: main paper sections (abstract, I to VII, App. A, back matter), main tables, supplement. Originals saved before the first edit in
the session scratchpad (`.../scratchpad/orig/`: sections/, tables/, supplement.tex, main.tex, both .bib, main.orig.pdf). Script:
`.../scratchpad/integrity.py` (comments stripped; whitespace-normalised). Nothing committed.

## Result

- **Binding sentences: 36 of 36 present verbatim** in the revised main text (NEG abstract-form and 6.1 opening, A4.2.4 bullets 1, 4, 5,
  A6.12 L1 / L-NI / {S2} / baselines (Table VI A6.6) sentences, A6.13 first and last sentences and the D0094 clause, clean-estimate
  sentence, L4 Holm 0.049, LG three p-values for each cell, impulse CI lower bound 0.0, multiplicity sentence, "preregistered"
  definition, H prefix, the only-guarantee sentence, the theory label, every SPEC section 7 Limitations item). Deviations box: 17 items
  before, 17 after (8 Study 1, 9 Study 2), wording shortened only.
- **Labels:** none removed or added. **Citation keys:** none removed from the paper; three keys lose one occurrence each
  (`zhang2026lowquality`, `shao2024ddef`, `huang2025evidential`: the Study 2 Method sentence "Examples are ..." was deleted and merged into
  one shorter sentence; all three remain cited in Section II). No key added. Reference list unchanged (63 entries).
- **Cross-references:** the outline sentence of the Introduction was deleted (its refs to `sec:related`, `sec:discussion`,
  `sec:conclusion`); several refs to `sec:setting` now point to its subsections (`sec:setting-evidence`, `-corruptions`, `-data`, `-tests`).
- **Numbers changed: none.** Every number removed from the main prose was either (a) deleted with its sentence because it is repeated
  elsewhere in the main text or in a main table, or (b) moved verbatim to the supplement. Numbers added: 98.8 %, 98.9 % and 98.6 %
  (the A-8 replacement, below).

## A-8 residual (task 3)

Replaced "can differ by up to about 1.5 % of tokens between processes (card row A-8)" (no runs file) by: "A fresh tokenisation of the
same pixels in another process need not reproduce the stored codes: it agreed on 98.8 % and 98.9 % of image tokens in the two stopped
self-checks of card row A-8, and on at least 98.6 % in the pixel-parity runs." Run comments:
`runs/P2-LRF-L1.try1/selfcheck.json:image_tokens_frac_equal (= 0.98828125)`, `runs/P2-LRF-L1.try2/selfcheck.json:image_tokens_frac_equal
(= 0.9892578125)`, `runs/P2-LRF-BASELINES-PARITY-LG/baselines.json:pixel_parity.min (= 0.986328125)`.
Note for the lead: SPEC section 7 still says "up to about 1.5% of tokens"; update the SPEC text if it is reused elsewhere.

## Moved to the supplement (verbatim; run comments carried)

| From (main) | To (supplement) | Content and numbers |
|---|---|---|
| IV-B Headroom rule | S-I "Protocol details of Study 1" | rungs (JPEG 10 then 5; sigma 0.10 then 0.20; splice 128 then 192 px); pass rule (paired t >= 2.0, n_v >= 90, $\bar\Delta/s$); R1 300 items if D* >= 29, R2 500 if 18 <= D* < 29, R3 below 18 |
| IV-B Families | S-I same subsection | design MDE 0.053 at n = 300, assumed discordance 10 % |
| IV-A CRC threshold | S-I same subsection | tie-breaking jitter sentence (main keeps a short pointer) |
| IV-C S-C | S-II Table S (calibration, already there) | shares 0.0064 at alpha 0.01 and 0.0956 at 0.10 (already in the supplement table; main sentence deleted) |
| IV-C Family B | S-II "Family B: fit pairs and minimum detectable gain" | 239 fit pairs, text direction 0.887, ceiling 0.95; MDE 0.054 at discordance 0.10 (test n 298 added with its run key) |
| App. A (iii), (iv) | S-II "Correlated-token proposition ... closed-form frontier and a numerical instance" | closed form of b(phi0; G, chi); instance m0 900, m1 100, gamma 0.05, gamma01 -0.045, mu 0.1, eigenvalue 0.9500, ratio 0.4892 -> 0.5080 at (0.3, 0); labelled theory, not validated on UniDisc, not used in Study 2 |
| V-B Objective and tuning | S-IV "Weight-model search, caption-slot checks and the full feature table" | nine configurations, successive halving factor 3 at 4, 13, 40 epochs, three inner folds |
| V-B Fixed caption slot | S-IV same subsection | five-item, four-condition invariance check, maximum absolute difference 0 |
| Table IV (table*, full names) | S-IV Table S (full table, `tables/tab_features.tex` unchanged) | main keeps a column-width Table IV by group and formula (`tables/tab_features_main.tex`, hand-copied counts and formulas: 7, 3, 8, 4, 6, 6, 1; total 35) |
| Every figure/table caption "Source:" path, Fig. 2 and Fig. 4 drawing notes | S-VIII "Sources of the Main Paper's Figures and Tables" | paths and keys unchanged |
| Table VI caption model revisions | S-VI (already present in full) | 32bd6428..., 9fdffc58..., CLIP cosine, SigLIP logit |

## Deleted with the sentence (number or key still in the main text or a main table)

- Intro bullet 5: 0.0456 (0.0442 to 0.0470) (kept in IV-C S-C). Outline sentence of Section I. Scope sentence on theory and ablation
  (both stated in IV-A and VI-C).
- IV-C detection paragraph: AUROC values and intervals for patch, swap, JPEG, noise, TbV and rival, and q minus rival -0.195, -0.265 with
  intervals (all in Table III; the detection numbers also stay in Intro bullet 4). S-D2 numbers kept.
- IV-C and V-D multiplicity repeats (17 families, 0.58): kept once in III-E, as SPEC section 3 places it.
- VI-A Tier-3 paragraph (0.023, 0.014, 0.017): duplicate of IV-C, which keeps them; VI-A keeps a one-sentence pointer (SPEC VI-A).
- VI-B alternatives: net 0.031 (clean, splice) and 0.058 (in V-D and VI-C); list turned into a run-in paragraph (i) to (v).
- VII Study 2: L-NI interval 0.009 to 0.053 (kept in abstract, I, V-D); merged into the L1 sentence.
- Captions: Table V caption 449 items / impulse 0.0 and 0.058 (in V-D text); Fig. 3 caption scope line and family label (in IV-C text).

## Must-not and wording fixes

- "this paper does not say that the score detects corrupted codes better than cheap methods" -> "makes no claim that the score detects
  corrupted codes more accurately than cheap methods" (rule 5 "better than").
- Family B "the combination did not beat the better single score" -> "no gain of the combination over the better single score was
  detected"; same fix in `tables/supp_study1_families.tex` and its generator `scripts/tab1_study1.py` ("fusion did not beat").
- Related work "Preregistration fixes the questions" -> "records" (rule 5 "fixes").
- PS audit "not read as a validation of the pipeline" -> "not read as a check of the whole pipeline".
- VI-B "(iv) The reach across noise types" -> "How far the gain extends to other noise types" (rule 5 phrase).
- Family H in IV-C: "50 pilot COCO images not used elsewhere" -> "50 COCO images not used elsewhere" (A5.9 mandatory prefix).
- Fig. 4 caption no longer starts with "The".
- Two hidden TAB characters that had replaced "\ci" in `\cite{hsieh2023sugarcrepe}` (Introduction bullet 6, Discussion H paragraph)
  restored to `~\cite{hsieh2023sugarcrepe}`; the H prefix now carries its citation in both places. Final scan of all .tex and .bib for
  control, format, bidi, tag, NBSP and soft-hyphen characters: 0 hits.

## Remaining must-not scan of the main PDF body (pdftotext)

Only allowed uses remain: "guarantee" (prop:crc and conformal prediction in Section II), "independent" in its mathematical sense,
"not validated on UniDisc" (mandatory theory label), "no effect" (binding NEG sentence).

## Full machine output

See `paper2-tnnls/drafts/integrity-diff-edit1-numbers.md` (script `drafts/integrity-diff-edit1.py`) (number-by-number table: count removed, still in main prose, in a main table, added to the
supplement, already in the supplement). Every number in the "removed" table is accounted for by the rows above; the apparent removals
"023", "428", "-384", "01", "00" are fragments of cite keys and hashes, not numbers of the paper.
