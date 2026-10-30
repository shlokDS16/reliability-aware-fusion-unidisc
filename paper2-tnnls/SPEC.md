# Paper 2 build spec: IEEE TNNLS Full Paper (lead: Paper 2 session, 2026-10-30)

This file is the contract for every writer, figure, citation and review agent. It points to sources; it does not restate them.
Read `research/CONTRACT.md` first. Facts and numbers come only from committed `runs/` files and the preregistration documents.

## 0. Hard rules (any violation fails the build)

1. **No number without a `runs/<exp-id>/` file.** Every number in .tex carries a LaTeX comment `% run: <path>:<json key>` on the
   same or preceding line (the paper2/ draft already does this; keep the convention). Predictions, plans and design targets are not results.
2. **Binding wording** (preregistered; substance may not change, only typography):
   - Study 1 (GATE): SAP Addendum A4, section A4.2 (outcome book, label NEG), A4.2.2 must-nots, AB.1 (no secondary result explains the null),
     A5.9 (family H placement: Results and supplement ONLY; never title, abstract, conclusion, cover letter; D0085).
     File: `research/paper2/prereg/SAP-ADDENDUM-A4-*.md` and `SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md`. The existing Study 1 draft
     `paper2/` (elsarticle) already follows these; reuse its sentences.
   - Study 2 (LRF): `research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md` A6.12 (lines ~267-310) and A6.13 (disclosure, Methods,
     once). Branch **A** (L1 confirmed, one-sided p <= 0.025). Gate audits: `research/paper2/prereg/GATE-AUDIT-FAMILY-L-2026-10-30.md`
     and `GATE-AUDIT-FAMILY-LG-2026-10-30.md` (their "binding wording" items and writer notes are binding).
   - Writer notes in `research/paper2/CONFIRM-EVENING-2026-10-28.md` section 18 (impulse two-sided p 0.058 and CI lower bound 0.0, so stated
     with its one-sided Holm p only; "per the operations log" wording; deviations-box items (a)-(d)).
3. **Separation of the two studies (C6-4, AB.1, A6.12 placement 2).** Study 1 and Study 2 are two separate preregistered studies. Neither is
   the other's motivation, explanation or contrast, in any sentence, section order, figure or table. No figure or table holds both GATE-M
   results and LRF numbers. No sentence compares LRF with GATE-M, or LRF with CLIP/SigLIP. No "problem/solution" arc. The chronology
   (A6.13) appears once, in Study 2's Methods.
4. **Must-not words** for LRF: "robust", "generalises/generalizes", "first", "state of the art", "calibrated", "guarantee", "validated";
   "confirmed" only for L1 (and L4/LG cells only as "rejected at Holm-adjusted ..."). For GATE: "GATE-M has no effect" is forbidden
   (the result is a bounded null: changes beyond +-0.05 excluded).
5. **Theory labels** (`research/paper2/method/THEORY-ADDENDUM-2026-10-29.md` sections 1.7, 3.4, 4 and R1.6-R1.8): every proposition is
   "theory under stated assumptions, not validated on UniDisc"; Props. 2 and 3 are "a model of when withholding or weighting helps an
   additive statistic", never "predicts"; Props. 2 and 3 are never combined in one sentence (R1.6 item 3); no proposition explains any
   result; Prop. 3 is never used to motivate LRF or to explain the L1 result. The calibration guarantee (paper2 method.tex
   `prop:crc`) is the only guarantee in the paper and belongs to Study 1.
6. **AI** appears only in the unnumbered section "Declaration of Generative AI Use" before References (checklist C2). No Acknowledgment.
7. **Style** (Shlok's rules, memory `paper-presentation-rules`): no word "screening" anywhere (also figures); every reference has a DOI or
   URL and renders blue; cite verified TNNLS papers where they genuinely support a sentence; prose edited by `research-humanizer`
   (academic register) and cross-reviewed; IEEE abstract: one paragraph, 150-250 words, no abbreviations, no symbols, no citations.
8. Anonymous build by default (`\anontrue`); author block and biographies only in the camera-ready switch.

## 1. Title (binding, branch A, set in IEEE title case)

Learned Reliability-Aware Fusion of Token Evidence Raised Image-Text Verification Accuracy Under Gaussian Noise in a Unified Masked
Diffusion Model: A Preregistered Confirmation in UniDisc

(A6.12 branch A text; only capitalisation changed. Short running head: "Learned Reliability-Aware Fusion of Token Evidence in UniDisc".)

## 2. Abstract (write last; 150-250 words; A6.12 placement 1)

Contents in this order, no linking sentence between the studies: one sentence of setting (unified masked diffusion models score
captions against images token by token; inputs can be damaged); Study 1 in its A4.2 NEG sentence form (bounded null under three
corruptions, scope); Study 2: the L1 sentence and the L-NI sentence (A6.12, branch A), with the scope {S}; one sentence on openness
(preregistration, frozen hashes, code). No abbreviations: write "conformal risk control", "learned reliability-aware fusion", no "LRF",
"GATE-M", "CI" (write "95 percent confidence interval"), no sigma symbol (write "Gaussian noise with standard deviation 0.1").
Index Terms (4-5, alphabetical): to be chosen from the IEEE Thesaurus by the writer (candidates: "Diffusion models", "Image-text
matching", "Multimodal fusion", "Reliability", "Uncertainty").

## 3. Structure and page budget (target 13 pages main + supplement; hard cap 15)

| # | Section | Pages | Sources |
|---|---|---|---|
| I | Introduction (Fig. 1 on p1-2) | 1.2 | paper2/sections/introduction.tex; this spec |
| II | Related work: generative and likelihood scoring; unified masked discrete diffusion; reliability-aware and dynamic multimodal fusion (incl. TNNLS); conformal risk control; corruption benchmarks; preregistration in ML | 0.8 | paper2/sections/related.tex; research/paper2/related*; research/paper2/tnnls/EXEMPLARS-2026-10-29.md |
| III | Setting: UniDisc, tokens, image-direction evidence Delta_j, the verification decision, corruptions; reliability-weighted evidence S_w = sum_j w_j Delta_j as the shared notation of both studies (notation only, no claim) | 0.7 | paper2/sections/method.tex ssec:notation, ssec:scores, ssec:evidence |
| IV | Theory of reliability-weighted evidence (Lemma 1, Prop. 2: when hard withholding raises the SNR with correlated tokens; Prop. 3: SNR-optimal weights under independence and exchangeable correlation). Statements + one interpretation paragraph each + labels of rule 5; proofs in Appendix A (main PDF) or supplement. Fig. 2 = the theory figure (gating frontier, no measured points; paper2/figures/F5_gating_frontier as a starting point) | 1.2 | THEORY-ADDENDUM R1.4-R1.8 (manuscript-ready text in R1.8); paper2/sections/method.tex prop:snrcorr; runs/P2-THEORY-CHECK/output.txt (toy checks, named as such) |
| V | Study 1: calibrated token withholding (GATE-M with conformal risk control; Prop. CRC). V-A method (compressed), V-B preregistered protocol (folds, corruptions, headroom rule, arms, families, tests), V-C results: family P (primary, Table I + Fig. 3), calibration S-C, positive control PS, detection S-D, mechanism S-M, re-infilling S2, two-way fusion B, hard negatives H (results only: H-NOGO, H4 not run), exploratory suite one sentence; full secondary/descriptive families to the supplement | 3.3 | paper2/sections/{method,protocol,results}.tex; runs/P2-GATE-M4/analysis.json, M1, M5, S2, FOIL-TEST, H3/family.json, SUITE/analysis.json |
| VI | Study 2: learned reliability-aware fusion (LRF). VI-A provenance disclosure (A6.13, once); VI-B the frozen object (features in groups, logistic-GAM weight w_j = sigmoid(f(x_j)), objective, HPO, freeze, fixed caption slot, hashes; Fig. 4 = learned weight shapes from model.npz, descriptive); VI-C preregistered protocol (fresh fold of 533, n-rule n_L = 450, endpoints L1, L3, L4, L-NI, L-LEN, LG; gatekeeping and Holm; one-sided exact McNemar); VI-D results (Table II + Fig. 5), LG (Table II block), reference baselines (Table III, own table, A6.6 sentence, no comparison word), cost (Table IV) | 3.0 | SAP A6; runs/P2-LRF-FROZEN-LFIX/{spec,hpo}.json; runs/P2-LRF-FOLD; runs/P2-LRF-PLAN/n_rule.json; runs/P2-LRF-L1/a6_analysis.json; runs/P2-LRF-LG/a6_analysis.json; runs/P2-LRF-BASELINES*/baselines.json |
| VII | Discussion: what each study shows, separately; Limitations (named subsection: one model, one severity, COCO random negatives, post hoc design of LRF disclosed, n, deviations box pointer, clean-image margin chosen after a clean interval was seen, near-ceiling reference baselines), Deviations box (all disclosed deviations of both studies) | 1.0 | paper2/sections/discussion.tex; paper2/sections/appendix.tex app:deviations; CONFIRM s18 (a)-(d); A6.13 |
| VIII | Conclusion (one paragraph per study, no linking sentence, no H) | 0.3 | |
| - | Declaration of Generative AI Use; Data and code availability (anonymised link) | 0.2 | checklist C2 |
| - | References (45-65 verified) | 1.5 | citation-validator output |
| App. A | Proofs of Props. 2 and 3 (short) | 0.6 | THEORY-ADDENDUM |

Supplement (separate PDF, `supplement/supplement.tex`): S-I preregistration record (pins, audits, amendments, deviations in full);
S-II Study 1 secondary and descriptive families (S-Z, S-DN, E-dec, E-pred, Tier 3, coherence, cost, hardware); S-III family H detail;
S-IV Study 2 exploratory material allowed by A6.12 placement 3 (M4-item cross-fit numbers, supplement-only; fresh-fold GATE-M arm,
descriptive); S-V Proposition 1 (detectability limit) with its R1.2 labels; S-VI symbol crosswalk; S-VII pixel parity and baseline details.

## 4. Figures (main text; vector PDF, colour-blind safe, greyscale-legible, 8-10 pt at final width)

1. **Fig. 1** (two-column, page 1-2): schematic of image-text verification in UniDisc: image tokens, caption, per-token image-direction
   evidence Delta_j, a reliability weight w_j, the decision sign(sum w_j Delta_j). Two weight rules shown as two labelled panels
   "Study 1: calibrated withholding (0/1)" and "Study 2: learned weight w(x_j)" with NO result numbers and no arrow from one to the other.
2. **Fig. 2**: theory figure (Prop. 2 frontier in (phi_0, phi_1), no measured points; optional inset of Prop. 3 weight shapes from the toy check).
3. **Fig. 3**: Study 1 family P: net accuracy change with 90% CIs and the +-0.05 band, three corruptions (paper2/figures/F6_p_result as base).
4. **Fig. 4**: Study 2 frozen weight model: partial-dependence curves of w on the 4-6 features with the largest learned effect (computed
   on CPU from runs/P2-LRF-FROZEN-LFIX/model.npz into a new run dir `runs/P2-PAPER-FIGS/`), plus 3 example token-weight maps under
   noise for items chosen by a fixed rule (the first 3 fold items), never by outcome. Descriptive; no accuracy on the figure.
5. **Fig. 5**: Study 2 results: net accuracy change with 95% CIs for L1, L3, L4, L-NI (90% CI and the -0.03 margin), LG cells (Holm p
   in labels), on one axis per family; L1 visually primary.
All figure scripts live in `paper2-tnnls/scripts/` and read only committed runs files; outputs in `paper2-tnnls/figures/`.

## 5. Tables

- **Table I** Study 1 preregistered families: family, endpoint, n, estimate, interval, preregistered decision (P, S-C, PS, S-D, S-M, S2, B, H).
- **Table II** Study 2 preregistered families: L1, L3, L4 (Holm), L-NI, L-LEN, LG cells: acc without / with LRF, b, c, net, CI, p, decision.
- **Table III** Reference baselines (CLIP ViT-L/14, SigLIP so400m): accuracy per condition and paired drop with 95% CI; caption carries the
  A6.6 sentence ("different models trained on different data ... no test, no comparison") and the pixel-parity result.
- **Table IV** Cost: network calls per verification, wall-clock per item on the 12 GB laptop GPU, peak memory, for NONE, GATE-M, LRF
  (CPU weights on stored arrays), CLIP, SigLIP (from paper2 app:cost and runs telemetry / driver logs; only measured values).
- Table of LRF feature groups (35 features in 6-7 groups) may sit in Section VI or the supplement.

## 6. Agents and order (at most 3 at once; proposer is never validator)

1. Wave A (parallel): red-team (Opus) on this spec; figure-smith (Sonnet) Figs. 2-5 + Tables I-IV data; citation-validator (Sonnet)
   bibliography incl. verified TNNLS papers.
2. Wave B: manuscript-writer x2: W1 Sections I-IV + VII-VIII + abstract (Opus); W2 Sections V-VI + appendix + supplement (Opus).
3. Wave C: clarity-editor (research-humanizer) with integrity diff; gate-auditor number reconciliation (every number vs runs);
   red-team (Opus) hostile-AC review; Codex review in thread 01a18699-8f14-79c1-8343-0cdc7c2466f7.
4. Build: latexmk PDF (no empty column space; check_column_gaps.py; pdffonts), supplement PDF, DOCX per the template verdict in
   `research/paper2/tnnls/TEMPLATES-AND-DOCX-2026-10-30.md`; final pdftotext scan for "screen", abbreviations in the abstract, must-not words.
