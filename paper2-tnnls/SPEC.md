# Paper 2 build spec v2: IEEE TNNLS Full Paper (lead, 2026-10-30)

> **SPEC v2.3 (2026-10-31).** Lead rulings after the red team on the Mask-DiFuser presentation pass
> (`research/paper2/tnnls/REDTEAM-MASKDIFUSER-PASS-2026-10-30.md`), ledger rows D0107-D0110, binding on top of v2.2:
> - D0107: Proposition 2 with Fig. 3 and the token-detection Fig. 5 stay in the supplement (overrides rule 4 of section 4); A4.2.2 item 2 is met by one
>   main-text sentence (IV-C4) giving the M1 rival's sign, AUROC with CI and the paired difference to the gate score.
> - D0108: Study 2's Table IV and Section V-H carry no Study 1 object: no trimmed-at-gate-count row, no "gate" clause, median and 20% trimmed mean by
>   formula only, the denoiser described by its operation, no CLIP/SigLIP pointer (A6.6, A6.12, rule 3).
> - D0109: Table IV has no bold or underline; italics mark the highest value per column, descriptive, no second-best mark; only the unweighted rule
>   and LRF were fixed before the fold was opened.
> - D0110: the Table IV caption states that 4 of the 10 learned refits are shown, chosen after the fold was scored (all 10 in S-VII); VI-C states that
>   the linear logit on the same features was at or above LRF in three of four columns and above the unweighted rule with an interval excluding zero in all four.

v2 implements red-team conditions RS-1 to RS-12 (`research/paper2/tnnls/REDTEAM-SPEC-2026-10-30.md`, verdict on v1: DO NOT SIGN)
and decisions D0090-D0094. v1 is in git history (b5dd8a05). This file is the contract for every writer, figure, citation and review
agent. Read `research/CONTRACT.md` first. Facts and numbers come only from committed `runs/` files and the preregistration documents.

## 0. Hard rules (any violation fails the build)

1. **No number without a `runs/<exp-id>/` file.** Every number in .tex carries `% run: <path>:<json key>` on the same or preceding
   line (the paper2/ draft does this). Predictions, plans and design targets are not results. Never quote in-sample or
   `freeze_check.json` numbers, or any accuracy of the re-frozen LRF on its design items, as performance (C6-8), even in the supplement.
2. **Binding wording** (substance fixed; only typography may change):
   - Study 1 (GATE): `research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md` A4.2.2 (rules 1-7, scope {S1}), A4.2.3 NEG (abstract sentence,
     6.1-opening sentence), A4.2.4 (contribution bullets 1-6), A4.2.5 (figure rules), A4.1.10 (Tier-3 placement), AB.1; family H:
     `SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md` A5.9 (Results and supplement only, own subsection with its prefix, never title, abstract,
     highlights, conclusion, cover letter; D0085). Reuse the paper2/ (elsarticle) draft's sentences, which follow these.
   - Study 2 (LRF): `SAP-ADDENDUM-A6-LRF-2026-10-29.md` A6.12 (branch A, scope {S2}, sentences, placement, must-not) and A6.13 (disclosure,
     Methods, once, plus the D0094 clause). Gate audits `GATE-AUDIT-FAMILY-L-2026-10-30.md`, `GATE-AUDIT-FAMILY-LG-2026-10-30.md`.
   - LG (D0091): print one-sided p, Holm p and two-sided p for every LG cell; impulse: two-sided 0.058 and 95% CI lower bound 0.0 stated;
     no two-sided claim.
3. **The two studies are separate (C6-4, AB.1, A6.1, A6.12 placement 2, D0090).** Neither is the other's motivation, explanation or
   contrast in any sentence, section order, figure, table, caption or notation. No shared weight notation: Section III defines only the
   unweighted sum S = sum_j Delta_j; the gate indicator I_j appears only in Study 1, the weight w_j only in Study 2, and neither section
   uses the other's symbol. No figure or table holds both GATE-M results and LRF numbers. No sentence compares LRF with GATE-M or LRF with
   CLIP/SigLIP. LRF's features are defined by formula, never by their Study 1 role (no "the M1 rival", no "what the gate missed"). Family B
   keeps its preregistered descriptor and never "fusion" in a heading. The chronology appears once (Study 2 Methods, A6.13).
4. **Theory** (THEORY-ADDENDUM r1: R1.1, R1.2, R1.6-R1.8, section 4): only `prop:crc` (the only guarantee) and Lemma 1 + `prop:snrcorr`
   (R1.8 text) are in the main text, inside Study 1's Method, with the label "a model of when withholding helps an additive statistic;
   theory under stated assumptions, not validated on UniDisc"; never "predicts"; never linked to any result. Prop. 3 / Lemma 2 / Cor. 3.1
   only in supplement S-II beside the Tier-3 table, labelled "theory reference for Study 1's soft comparators; not used in Study 2". The
   detectability-limit proposition (addendum Prop. 1) is at most one background sentence, never beside M1, the rival or P, never "we prove".
   Refer to propositions by LaTeX label, not addendum number (F22). Study 2 carries no theory.
5. **Must-not list** (final `pdftotext` scan of PDF and supplement, plus the DOCX):
   - LRF: "robust", "generalises/generalizes", "first", "state of the art", "calibrated", "guarantee", "validated", "held-out noise
     family", "across noise types"/"across corruptions" as pooled claims, "trend"; "confirmed" only for L1; L4/LG cells as "rejected at the
     Holm-adjusted level"; no clean-image superiority claim; no claim that the weights track reliability or corruption ("reliability-aware"
     is the method's name only, F12).
   - Comparison/arc words: "outperform", "better than", "beats", "competitive", "unlike hard gating", "instead of discarding", "fixes",
     "overcomes", "solution", "addresses the limitation".
   - Theory words for any result: "predicts", "explains", "accounts for", "is consistent with".
   - Study 1: "GATE-M has no effect" (the result is a bounded null), "equivalent", "as good as", "on-manifold", "our detector",
     "decision-level fusion", "UniDisc is time-free"; "calibrated" not as a selling word.
   - H: "compositional", "replication", "SugarCrepe score".
   - "screening" anywhere (Shlok); "independent" for any audit; "novel"/"new" in the title; "we prove" for the detectability limit.
6. **AI** (D0093): only in the unnumbered "Declaration of Generative AI Use" before References; no Acknowledgment section. The audits
   (red team, gate-auditor, data-steward, statistician) were run by AI agents: Methods calls them "scripted and agent-run audits (see
   Declaration)" without the word AI and never "independent"; the Declaration lists each role, system, sections and level (F17).
7. **IEEE rules** (checklist + `research/paper2/tnnls/TEMPLATES-AND-DOCX-2026-10-30.md`): IEEEtran journal, two columns; abstract one
   paragraph 150-250 words, no abbreviations, symbols or citations; exactly 4 index terms, alphabetical; equations cited "(n)"; figure
   subpanel labels (a)(b)(c) 8 pt; no figure borders; captions in LaTeX only; TABLE Roman numerals, caption above, no final period;
   references IEEE style with DOI/URL, blue links; no "submitted to the IEEE" notice in the review PDF; anonymous build by default; target
   13 pages (cap 15 including appendix and references).
8. **Style** (Shlok, memory paper-presentation-rules): every reference linked and blue; cite verified TNNLS papers only where they support
   a sentence; prose through the writer team with research-humanizer and an integrity diff (numbers, citations, labels unchanged); no empty
   column space in the PDF.

## 1. Title (binding, branch A; D0092)

Learned Reliability-Aware Fusion of Token Evidence Raised Image-Text Verification Accuracy Under Gaussian Noise in a Unified Masked
Diffusion Model: A Preregistered Confirmation in UniDisc

Capitalisation per the IEEE Editorial Style Manual (the writer checks prepositions: "Under" vs "under"). No running head is invented.
"Image-text verification" is defined at first use in the Introduction as the image-direction decision (F30).

## 2. Abstract (RS-5)

RULED (statistician, research/paper2/tnnls/ABSTRACT-RULING-2026-10-30.md, rows R1-R12): use its candidate with fallback F4 (names the
estimand of the L-NI interval, "of the net change"); if an edit exceeds 250 words, fallback F1 (alpha clause to Results) first. The
red team countersigns that the merged opening scope is scope, not a link sentence (else F3). The text below is the earlier plan.

Skeleton and word counts: `paper2-tnnls/drafts/abstract-skeleton-v1.md` (295 words full, 290 merged; over 250). The statistician rules in
a dated row which binding sentences may be shortened or moved to the body to reach at most 250 words (no writer choice). Order: setting
(one sentence), Study 1 (gate description, NEG sentence, "This does not show that the gate has no effect"), Study 2 (L1 sentence with the
L-LEN clause, L-NI sentence), scope; no sentence links the studies; no harm clause; no openness claim beyond the preregistration
definition of rule 9.

## 3. Structure and page budget (target 13 pages main incl. references and appendix)

| # | Section | Pages | Content and sources |
|---|---|---|---|
| I | Introduction (Fig. 1) | 1.3 | One problem: how a unified masked diffusion model's own per-token likelihood evidence for image-caption verification behaves when the image is damaged, and why the model's own evidence is the object (a unified model scoring its inputs without an external encoder; cited uses). Two preregistered questions stated each on its own terms: Q1 does discarding tokens flagged by the model's masked-likelihood score, with a conformal-risk-control threshold, change verification accuracy? Q2 does one frozen learned per-token weighting raise accuracy on fresh images? No "however/therefore/instead" between them; no chronology. **Contribution list** (RS-4): A4.2.4 bullets 1-6 in substance (bullet 6 by status only: S2 "run, formal", B "run, formal", family H by its status "run; headroom not met (H-NOGO), H4 not run" with the A5.9 post hoc label; R not run, so not in the bullet), plus Study 2 bullets (the frozen, hash-pinned object; the preregistered confirmation with {S2}; reference encoders and cost measured, without comparison), each ending with a section pointer. **"Scope of this paper" paragraph** (F14): two preregistered measurements on one model; no baseline race and why; what is not claimed. |
| II | Related work | 0.9 | generative and likelihood scoring with diffusion models (Diffusion Classifier, Clark and Jaini 2023, VQAScore); unified masked discrete diffusion (UniDisc, MMaDA, LaViDa, Muddit, Lumina-DiMOO; cite the TNNLS survey by Moser et al. where it supports a sentence); reliability-aware and dynamic multimodal fusion and attention-based multiple-instance pooling (QMF, Ilse et al. 2018, trusted/evidential fusion incl. TNNLS papers); conformal risk control; corruption benchmarks; preregistration in machine learning. Study 2's novelty sentence rewritten for Study 2 alone, scoped "to our knowledge" to the logged search (`research/paper2/tnnls/NOVELTY-AUDIT-LRF-2026-10-29.md`; its matched-filter sentence and its section-6 sentence joining LRF with gating SNR are BANNED, F13). |
| III | Shared setting | 0.8 | UniDisc, tokens, image-direction evidence Delta_j, the UNWEIGHTED S = sum_j Delta_j and its decision; corruptions; COCO data and the fresh-image policy; test conventions (exact McNemar, one/two-sided, Holm); multiplicity sentence (17 families, 1 - 0.95^17 = 0.58, "no adjustment across families"; F25); "preregistered" defined once (rule 9); the A4.3.1 time-input sentence (table in the supplement; F19). Sources: paper2/sections/method.tex ssec:notation, ssec:scores, ssec:evidence; protocol.tex. |
| IV | Study 1: masked-likelihood token gating with conformal risk control | 3.6 | IV-A method: the gate's masked-likelihood suspicion score u_j, CRC threshold, `prop:crc`, the gate I_j, GATE-M, then Lemma 1 + `prop:snrcorr` (R1.8 text "directly after the paragraph that ends with eq:snr") and Fig. 2 (theory frontier, theory only). IV-B preregistered protocol (folds, corruptions, headroom rule and n, arms and controls, families, tests). IV-C results: family P (Table I + Fig. 3), calibration S-C, positive control PS (own table "Positive control (pipeline check)"), detection S-D with the M1 rival, sign and AUROC with CI (own table, A4.2.2 item 2), mechanism S-M, re-infilling S2, family B (preregistered descriptor), family H in its own subsection "Family H (added after the primary result)" with the A5.9 prefix (H-NOGO; H4 not run), exploratory suite (one sentence), cost of Study 1 (own sentence/table). Sources: paper2/sections/{method,protocol,results}.tex; runs/P2-GATE-M4, M1, M5, S2, FOIL-TEST (+ FOIL analysis commit 10e6bc0f), H3/family.json, SUITE/analysis.json. |
| V | Study 2: learned reliability-aware fusion of token evidence | 3.2 | V-A provenance (A6.13 with the D0094 clause, once). V-B the frozen object, motivated on its own terms from reliability-weighted fusion and attention-based pooling literature (never from Study 1 or Prop. 3): features by formula in groups (table), w_j = sigmoid(f(x_j)) logistic GAM, objective, HPO, refit on the 500 design items under clean, JPEG 10, noise 0.1 and splice 128 (training conditions stated in plain words, F11), fixed caption slot, hashes; Fig. 4 learned weight shapes + token-weight maps (descriptive; rule of section 4). V-C preregistered protocol: fresh fold of 533 (L7 signed), n-rule n_L = 450, endpoints L1, L3, L4, L-NI, L-LEN, LG, gatekeeping and Holm, exact one-sided McNemar. V-D results: Table II + Fig. 5 (family L), LG block in Table II with all three p-values (D0091), the clean estimate stated once as positive with "superiority on clean images was not a preregistered hypothesis" (F12), L4's Holm margin stated. V-E reference encoders (Table III, own table, A6.6 sentence, CLIP/SigLIP cost inside it; only after the RS-12 audit). V-F cost of Study 2 (own sentence/table; NONE as its only reference). V-G exploratory ablation (section 6; Tier 3, labelled). Sources: SAP A6; runs/P2-LRF-*. |
| VI | Discussion | 1.0 | VI-A Study 1, opening with the A4.2.3 NEG 6.1 sentence, then the Tier-3 pointer and the H paragraph after it (A4.1.10, A5.9). VI-B Study 2 (what L1 shows and does not; cheapest alternative explanations from the red-team report, worded as open). VI-C Limitations (section 7). VI-D Deviations box (section 8). |
| VII | Conclusion | 0.3 | one paragraph per study, no link, no H, no rescue |
| - | Declaration of Generative AI Use; Reproducibility and data availability | 0.3 | rule 6; rule 9 |
| - | References | 1.5 | 45-65 verified entries |
| App. A | Proof of `prop:snrcorr` (short) | 0.4 | THEORY R1.8 |

Supplement (separate PDF): S-I preregistration record (pins, audits, amendments, full deviations list, time-input table); S-II Study 1
secondary/descriptive families (S-Z, S-DN, E-dec, E-pred, coherence) and the Tier-3 table with Prop. 3 beside it as theory reference;
S-III family H detail (A5.9 prefix); S-IV Study 2 exploratory material permitted by A6.12 placement 3 (M4-item cross-fit numbers, in their
own table; fresh-fold GATE-M arm, descriptive, in a SEPARATE table; no LRF column next to any GATE-M number); S-V symbol crosswalk;
S-VI reference-encoder details and pixel parity; S-VII the Tier-3 ablation in full. No section for the detectability limit (F20).

## 4. Figures (vector PDF, colour-blind safe, greyscale-legible, 8-10 pt at final size)

1. **Fig. 1**: the shared measurement only: image and caption to tokens, the per-token Delta_j map, the unweighted sum, the decision, and
   corruption as input damage. No weight rule, no study labels, no 0-to-learned axis (F2).
2. **Fig. 2** (Study 1 Method): the `prop:snrcorr` frontier, theory only, no measured point, no marking of where any condition sits, no
   inset (F4).
3. **Fig. 3** (Study 1 results; A4.2.5 item 1): family P only, one row per P1-P3, net accuracy difference GATE-M minus none with the 90%
   (thick) and 95% (thin) bootstrap intervals, solid line at 0, dashed lines at +-0.05; nothing else on the canvas.
4. **Fig. 4** (Study 2 Method): (a) partial-dependence curves of w for the features with the largest learned effect range; (b) token-weight
   maps for the first 3 fold items, clean AND noisy on one colour scale, caption "descriptive; not evidence that the weights track
   corruption" (F12). Source runs/P2-PAPER-FIGS/.
5. **Fig. 5** (Study 2 results): family L only (L1 emphasised, L3, L4 with Holm p); L-NI in its own panel with its 90% CI and the -0.03 margin. LG is
   reported in Table II only (no across-noise-types figure; LG audit).
Scripts in `paper2-tnnls/scripts/` read only committed runs; outputs in `paper2-tnnls/figures/`.

## 5. Tables

- **Table I** family P only: n, b, c, n_d, accuracies of both arms, net, 90/95/98.33% CIs, Holm p, preregistered decision (RS-2, RS-11).
  Any exact bound for n_d = 0 is computed into a `runs/P2-PAPER-*` file, labelled "added at writing, descriptive", and listed in the
  deviations box; the NEG sentence is unchanged.
- **Table (Study 1)** Positive control (pipeline check), own table. **Table (Study 1)** detection: AUROC with CI per corruption for the
  gate's score, the one-pass score and the M1 rival with its sign. **Table (Study 1)** cost.
- **Table II** Study 2: L1, L3, L4 (Holm), L-NI, L-LEN, LG x3: accuracy without/with LRF, b, c, net, CI, one-sided p, Holm p where
  applicable, two-sided p, decision.
- **Table III** reference encoders (CLIP ViT-L/14, SigLIP so400m): accuracy per condition and paired drop with 95% CI, their cost, the A6.6
  caption sentence, the pixel-parity result citing BOTH runs/P2-LRF-BASELINES-PARITY-L1 and -LG (and explaining the main run's stale
  "pixel_parity: not run" field); the clean accuracy on the same 300 items printed beside the LG cells (computed into a runs file); cost
  "not measured" unless a named timing run exists; no robustness reading (cells at ceiling, CIs degenerate). RS-12 MET: gate-auditor PASS
  WITH FIXES, research/paper2/prereg/GATE-AUDIT-BASELINES-PARITY-2026-10-30.md.
- **Table (Study 2)** LRF feature groups (by formula). **Table (Study 2)** cost (NONE as only reference).
Bold convention: a cell is bold only when its preregistered test rejected at its preregistered level; no underline; no ranking.

## 6. Exploratory ablation (Tier 3; the red team's "experiment whose absence causes rejection")

Plan written by the ml-expert and checked by the statistician BEFORE any variant is scored on fresh-fold items, committed, then run once
on CPU from stored arrays (`runs/P2-LRF-L1/arrays`, LG arrays): simpler weight rules fitted ONLY on the 500 design items (re-scored arrays)
with the same protocol, frozen, then scored on the fresh fold; plus group knockouts of the frozen LRF. Every variant is reported. Label
"exploratory; added after the primary, family H and Study 2 results"; kept out of title, abstract, conclusion and contributions; listed in
the deviations box; no p-value enters a claim; no variant is called better or worse than LRF in a claim (intervals only). Main text: one
short subsection V-G and one table; full detail S-VII.

## 7. Limitations (named subsection; each item attributed to its study; no restated chronology)

Study 1: one model and one severity per corruption (the P discordance counts appear ONLY as numbers in Table I, never in a sentence:
red-team re-check V2-1, A5.9 must-not 1); negatives worded as scope only ("all results are for random-caption negatives"), never as a reason for P.
Study 2: one model, one dataset, one severity; LRF was trained on the tested corruption (noise 0.1 was a training condition), so L1 tests
new images, not a new corruption; no preregistered test separates corruption-specific weighting from a generic gain (clean and splice
estimates were also positive); the title's "under Gaussian noise" names the tested condition, not a specificity; L4's Holm p is 0.049; the
impulse cell's two-sided p is 0.058; the clean-image margin was fixed after an exploratory clean interval was seen; unknown overlap of COCO
with UniDisc, CLIP and SigLIP pretraining; one corruption realisation and one mask seed per image; the A-8 residual (self-check token agreement 0.988 and 0.989 in the failed L1 starts and at least 0.986 in the parity runs; runs files;
agreement between processes); the reference encoders almost solve this matching task ("This paper makes no claim of a competitive
verifier"); no ablation was preregistered (section 6 is exploratory). Both: the preregistration is self-hosted (rule 9); audits were
agent-run (rule 6).

## 8. Deviations box (enumerated; sources in brackets)

Study 1: A4.5 items (1)-(5); A5.14; A5.1 amendment item 7; S2-FIG effective_n reason text; the data-steward's builder notes (neg/mismatch
image ids not collected; zero effect); D0087 committed after the H3 driver started and before any H3 row; the 162 unopened JSON files
(steward); the time-input table moved to the supplement (F19). Study 2: L1 try 1 and try 2 self-check stops and card row A-8 (pin
1871fe7d); the scorer pins file written 22:42 during L1 (values only from records committed before L1); card row A-9 (pin 84be25c4,
test-only); env-lock files empty in M1, M4, RESCORE, L1, LG (environment recorded after the runs, runs/P2-ENV/pip-freeze-2026-10-30.txt;
imagecorruptions commit verified from the venv); arrays untracked (SHA-256 manifests committed); CRLF and LF hash forms (both refer to the
same content); parity files moved unchanged from a wrong output directory; baselines.json "pixel_parity: not run" superseded by the
PARITY runs; no hash of the parity files was taken before the move (audit-time SHA-256s recorded in the baselines audit); CLIP/SigLIP download 5.0 GB against 2-4 GB quoted to Shlok; D0094 (what the lead had seen before the re-freeze); "no output
read before its run completed" rests on the operations log; Tier-3 ablation added at writing (section 6); the exact Clopper-Pearson bounds of Table I
added at writing (runs/P2-PAPER-BOUNDS, descriptive). [CONFIRM-EVENING-2026-10-28.md s18; gate audits L and LG; card rows A-5 to A-9]

## 9. Reproducibility paragraph and "preregistered" (F16)

Define once: "preregistered" = a dated analysis-plan addendum committed to a version-controlled repository before the first test item,
with the tested object hash-pinned and the commit order as the evidence; no third-party timestamp. State: code, plans, pins, predictions
and analysis outputs are in the repository (anonymised mirror at review that preserves commit times and hashes); item arrays are untracked
with SHA-256 manifests; the environment record was taken after the runs. Claim nothing more.

## 10. Other texts (F27)

Cover letter, response to reviewers, README and Zenodo description follow the abstract's placement rules: no H, no study link, no rescue.

## 11. Exemplar overrides (F28)

From EXEMPLARS take only layout, contribution-with-section-pointer and limitations conventions. Overridden: its rule 2 (experiments tied to
propositions), rule 3 (page-1 failure-and-fix figure), 5.2 Fig. 4 ("the result the theory predicts"), 5.3 ablation "hard gate versus soft
weighting", section 7 (gating analysis as a test of a proposition).

## 12. Agents and order (at most 3 at once; proposer is never validator)

1. Now: red-team re-check of this v2; statistician abstract ruling (RS-5); gate-auditor RS-12 (baselines and parity); ml-expert Tier-3
   ablation plan (then statistician check, commit, run); citation-validator bibliography; figure-smith revisions (Figs. 1, 3-5, tables
   split per section 5).
2. Writers (Opus): W1 Sections I-III, VI-VII, abstract; W2 Sections IV-V, App. A, supplement.
3. clarity-editor (research-humanizer, integrity diff); gate-auditor number reconciliation; red-team hostile-AC review; Codex review in
   thread 01a18699-8f14-79c1-8343-0cdc7c2466f7.
4. Build: PDF (no empty column space, check_column_gaps.py, pdffonts), supplement PDF, two-column DOCX on the IEEE Transactions Word template
   (D0093), must-not scan of all three.
