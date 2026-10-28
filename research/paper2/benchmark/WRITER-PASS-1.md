```yaml
agent: manuscript-writer
date: 2026-10-28
brief: Pre-results revision of Paper 2 (paper2/main.tex, paper2/sections/*.tex, paper2/references.bib) to card v4, SAP Addendum A4 r1 and the benchmark panel/red-team plan reviews. No M4 or later result exists and none is used.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/benchmark/REDTEAM-P2-PLAN.md (all)
  - research/paper2/benchmark/PANEL-P2-PLAN.md (sections 0-2, 3.2, 5, 6, 7)
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md (r1, all)
  - research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md (sections 1, 2, 3, 4, 5, 6, 9)
  - research/paper2/prereg/PREREG-GATE-MUST-v3-2026-10-28.md (K1-K7 lines 170-179, K2 lines 150-151)
  - research/ledgers/decisions.jsonl (D0074)
  - research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md; NOVELTY-REAUDIT-GATE-2026-10-28.md section 7 (must-not 1-9)
  - research/paper2/related/INFFUS-CITATIONS-2026-10-28.md; inffus-candidates.bib
  - research/paper2/benchmark/LENS-ARGUMENT.md section 8
  - runs/P2-GATE-M1/analysis.json, tbv_verdict.json; runs/P2-UNIDISC-KEYCHECK/README.md; exp_p2/gate/theory.py (symbols only)
  - paper2/main.tex, sections/*.tex, references.bib (all)
coverage: >
  Not read: the SR survey, LENS-CRAFT, IF-METHOD-ANATOMY and STYLE-GUIDE (the page/word targets used are those quoted in PANEL-P2-PLAN),
  Zhou & Lu full text (nobody has it; every statement about it is worded "as described in the abstract"), any M2/M3/M4 value
  (runs/P2-GATE-M3/family.json exists in the repository but was deliberately not opened, so no wording was shaped by the headroom
  decision), SAP body beyond the addenda quoted by A4, the code except theory.py symbol names. No figure, code, prereg file or ledger was edited.
claims:
  - statement: "Every number added to the manuscript is either from runs/P2-GATE-M1/analysis.json, from the design values already in protocol.tex, or from runs/P2-PROBE-01, P2-GATE-CPU, P2-UNIDISC-KEYCHECK as already cited."
    status: supported
    evidence: "M1 values checked against analysis.json keys table.*, falsifier*, paired_q_vs_best_cheap (rounded to 3 decimals; q-minus-plainB 0.0033/0.0053; p_holm 0.00039996 quoted as 0.0004, the resolution floor)"
    level: E4
    confidence: 0.9
  - statement: "paper2 compiles with latexmk -pdf: 0 undefined references, 0 undefined citations, 0 overfull boxes, no float-too-large warning."
    status: supported
    evidence: "paper2/main.log after the last run (57 pages in the 12pt preprint layout)"
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - page count in the final layout (5p,twocolumn not tried; the preprint layout is 57 pages)
  - Shlok's D18 answer / the lead's "no answer" row (A4.2.6)
  - red-team re-signature of the HARM, MIXED, R3-HARM, R3-MIXED sentences (A4 C4-4); the manuscript only quotes the SAP 9 sentence in protocol.tex and defers all label sentences
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# WRITER-PASS-1: what changed

## 1. Scope and claims (items 1, 6)
- **introduction.tex** rewritten. Opens with the fusion problem, then one measured failure case (M1: 0.961/0.955 on patch/swap, 0.561/0.503 on JPEG/noise, run comment `P2-GATE-M1`), stated as a separate secondary-family measurement that "does not enter the headline test and is not used to interpret it". Contributions are the six bullets of A4.2.4 (measured object; closed-form condition; preregistered test; token detection with the A4 wording, noise-only one-pass comparison, no paired test; calibration check; secondary families "reported as run or not run", with a comment that at submission the bullet lists only families whose status is "run"). The detector is "the gate's score ... a measured object, not an asset". The v3 pilot bullet is removed. Zhou & Lu enter the "what exists" paragraph as "in their abstract". Roadmap regenerated from the real headings and appendices.
- **protocol.tex** rewritten to card v4: 11 test families (P plus PS, S2, B, R and the six v3 secondaries), P the only headline family, no cross-family control, cut order, "no secondary family can rescue a null". The A2.2/A4 reading of P (positive, mixed, negative, inconclusive, harm, no operating point, R3) replaces the v3 text; the outdated rule "detection not better than the best rival stops the claim" is corrected to the K2 consequence (wording only, P still runs). Table of secondary families, pins, audit record, deviations and amendment rows moved to **appendix.tex** (new). Pilot, hardware, diagnostics and cost tables partly moved to Appendix C.
- **Contributions that are not guaranteed a cell** (re-infill, FOIL fusion, second model, Part 1 comparators) appear in no numbered contribution except the status-conditional bullet 6; Part 1 appears nowhere in contributions, abstract, highlights or conclusion (A4.1.10 placement rule).
- **Title**: replaced the "Calibrated gating ... measurement" title by the outcome-neutral question title QT of A4.2.3 (names UniDisc, no "fusion", no "calibrated"). A positive label replaces it with the A4 title for that label. Abstract: provisional, outcome-neutral, one `\todo{RESULT}` slot that cites the outcome book.

## 2. method.tex:~109 (item 2)
The sentence implying that null normalisation helps detection is replaced: the NP-optimality statement is limited to the idealised case it names, "the null normalisation is not assumed to improve detection, and the measurement does not show that it does", followed by the M1 facts (plain-B slightly above q on patch 0.964 vs 0.961 and swap 0.960 vs 0.955; JPEG 0.560 vs 0.561 and noise 0.511 vs 0.503, "less than 0.01", no paired test run on JPEG/noise). All numbers from `runs/P2-GATE-M1/analysis.json` (`table.*.{q,plainB}`), run comment in place.

## 3. Time-input statement (item 3)
protocol.tex Section 4.1, paragraph "Time input": A4.3.1 sentence verbatim ("in the released configuration" kept), then the key-check result (342/342 tensors, 0 missing, 0 unexpected, 0 shape mismatches; `P2-UNIDISC-KEYCHECK`) and the three limits (tokeniser not covered; key equality is not the intended final weights; mask-pattern training weight unrecoverable). The file:line table of REDTEAM-P2-PLAN section B is Appendix B (UniDisc SHA and HF snapshot given). Method intro points to both.

## 4. Notation (item 4)
Kept: alpha (CRC level), beta role, rho, mu, sigma, Y_R, d_R, z_R, Delta_j, K, R, G, S, S_r, k_s, b/c, T1/T2, D*, Z_cal and all SAP/theory.py names except where one letter carried two meanings **inside the paper**:
- alpha/beta in the SNR analysis (flag probabilities) vs the CRC level alpha: SNR flag probabilities are now phi_0, phi_1 (observed: phi_hat; code names alpha, beta, alpha_obs, beta_obs). This is the one place where the paper departs from theory.py/SAP spelling; the crosswalk is Appendix A.6 and the notation table says so. **If Shlok prefers to keep alpha/beta in the SNR equations, revert Eqs. (mean)-(snr) and the table row; nothing else depends on it.**
- partition groups S_k (clash with statistic S and steps S_r) -> Gamma_k.
- re-infill samples L (clash with loss L_i) -> n_draw (the SAP's own name).
- Algorithm 1 outputs pi_j (log-softmax vs probability) and rho_j (clash with corrupted fraction rho) -> eta_j and pi^max_j.
- empirical calibration risk R-hat (clash with reliable set R) -> F-hat_cal (the realised test version stays F-hat).
- Holm size m -> m_H in the appendix family table.
- marginalise/impute arm -> GATE-M/GATE-I (SAP name I-GATE stated once); word score "minimum" -> suspicion is the maximum over pieces (equivalently minimum of q).
Compact notation table rewritten (footnotesize, 17 rows, protocol-only symbols left out). Left as is, noted in the table: c (caption/discordant count), D_j vs D_c, Z_j vs Z_cal, T modality vs T_1, E (expectation) vs E_{T<-I}; each is separated by subscript and context and appears in the SAP.

## 5. Other consistency fixes found while editing
- **Algorithm ReInfill** now matches the SAP-fixed S2 sampler (fixed random order drawn up front, S_r steps, temperature one, unguided, caption masked, best of n_draw by chain likelihood). The max-probability order of spec v2 is gone; the "hybrid" variant is stated as not part of any family. The sentence "preregistered prediction: marginalise at least as good as impute" is removed (not a test in card v4).
- SNR section: the "refuted if sign disagrees" rule is replaced by the E-pred descriptive wording (agreement in A of K_eval cells); "prediction stated in advance" reworded (AB.3 item 4 allows "predicted" only in the E-pred table).
- Naive-Bayes sentence now carries its conditional-independence condition (red-team A8).
- Fusion weights: "fitted on calibration pairs" -> "fitted on pairs disjoint from the test pairs" (B uses separate fit pairs); ceiling rule stated as the card's (fit pairs, 0.95).
- Pins: v3 pin text (commit 164a18a5, SAP b4e0bf57) replaced by the card v4 pins (9c4e1e25, moved by row A-1 to f2f7b2e1; SAP LF e33f078c; folds LF/CRLF).

## 6. Related work and the five Information Fusion papers (item 5)
Added to references.bib (verbatim from inffus-candidates.bib, `note` fields removed so no evidence level prints): zhou2027burden, huang2025evidential, shao2024ddef, wang2025multistage, zhang2026lowquality. Placement: Introduction (fusion paragraph: zhang2026lowquality, shao2024ddef, huang2025evidential; "what exists": zhou2027burden in their abstract), Related work (new paragraph after "Source validation before fusion" with the drafted novelty sentences 1-3, Zhou & Lu strictly "as described in its abstract", the starred phrase about labelled calibration omitted; a `\todo{AUTHOR}` asks for the full-text read), Discussion (sentence 4 and limitation sentence 5 of the novelty check, "narrow novelty" and "concurrent work" bullets), Protocol (huang2025evidential in the hard-versus-graded paragraph). Must-not 10-13 honoured: no "first", no "decision-level" for the gate, no contrast with Zhou & Lu that needs the full text, Gomes bullet extended with Zhou & Lu in the introduction and limitations. Wang's corrigendum is not cited; a comment records it.

## 7. Two requested paragraphs (item 7)
- **Task validity (red-team A9)**: protocol.tex Section 4.8 "Why the image direction is the primary endpoint" (probe 1: 0.990 text vs 0.843 image, chosen after seeing the pilot, easy random negatives, what the result does and does not say, family B as the only two-direction test, untestable at ceiling), plus a limitation bullet "A constructed task" and one sentence in the introduction scope paragraph.
- **Hard gate vs graded/robust combiners (A4 Part 1)**: protocol.tex Section "Exploratory comparison with robust and weighted combiners": why the gate is binary (CRC bounds a count of flags), the five pre-specified combiners, CIs and MDD only, no p-value, A4.1.10 reading and placement rule, "has not been run". Limitation bullet "A hard gate and dependent tokens". Nothing in abstract, highlights, conclusion or contributions.

## 8. Results, discussion, conclusion
- results.tex restructured in card-v4 order (headroom, calibration, P, S-M, S-D, PS, S-DN, S-Z/E-pred, E-dec, coherence, S2, B, R, exploratory comparisons, status map and cost). Only S-D has text (M1 numbers, K2 wording, label-circularity sentence, 179-item and reselection robustness, copy check). Everything else stays `\todo{RESULT}` with the wording rule. The primary-results table environment is untouched.
- discussion.tex: Section 6.1 stays a `\todo` (must open with the outcome-book sentence); 6.2 written (what is fused, at what level, where reliability enters, what is not claimed, Zhou & Lu sentence); limitations extended (task validity, hard gate/dependence, time input and key-check scope, eleven families without cross-family control, hard-negative contamination, label circularity).
- conclusion.tex: five slots re-aimed at the outcome book; no content.

## 9. Word counts (wc -w, LaTeX-inclusive, HEAD -> now) and prose-only share
| Section | before | after |
|---|---|---|
| introduction | 1100 | 1523 |
| related | 1166 | 1461 |
| method | 3534 | 3742 |
| protocol | 3356 | 3985 |
| results | 687 | 1508 |
| discussion | 636 | 1320 |
| conclusion | 136 | 211 |
| appendix (new) | 0 | 2276 |
| declarations | 375 | 375 |

Prose only (comments, citations, math, tables, algorithms stripped): method + protocol 5022 -> 5915 words; body (without appendix and declarations) 8158 -> 11112; **method + protocol share of the body 61.5 % -> 53 %**. The absolute size grew because card v4 added families, the time-input paragraph, the task-validity and comparator sections; the plan's target (about 37 %) is reached only when Results are filled (about 3,600 words), when the share becomes roughly 42 %. Further cuts if wanted: algorithms ImageEvidence, CalibrateThreshold, ReInfill, GeometryMatchedGate to an appendix (the plan's W12; not done because the writer rule asks the algorithms to build on each other in the main text), and the "Wording and scope" paragraphs of Section 3.4. Page count: 57 pages in the 12pt `preprint` layout; the 35-page limit is measured on the final layout and was not tested.

## 10. References over the cap (item 5): do not delete; authors decide
`bibtex` prints cited entries only. Before this pass: 49 entries, 47 printed (hessel2021clipscore and radford2021clip are uncited and print nowhere). Now: 54 entries, **52 printed, limit 50**. FOIL, Omni-Diffusion and an image-corruption suite still have no verified bib entries (`\todo{AUTHOR: cite ...}` in protocol.tex); each will add one more, so about 4-5 drops are needed.
Candidates to drop, weakest first (each is cited once or twice and has a stronger or equivalent neighbour):
1. diao2024radar (radar-detection review; cited once, in a triple with finn1968adaptive and rohling1983cfar that already carry CFAR).
2. wan2026disp (backdoor self-purification; cited once, tangential, called "not evaluated against labels" in the text).
3. vovk2005algorithmic (book; conformal background; angelopoulos2023gentle covers the sentence).
4. tenney1981detection (second citation for distributed detection; chair1986optimal carries the rule).
5. lou2024sedd (background for absorbing-state diffusion; austin2021d3pm carries it).
Reserve: nie2025llada, bates2023outliers, hessel2021clipscore and radford2021clip (already unprinted; delete from the .bib if desired). Dropping 1 and 2 needs a one-sentence edit in related.tex (dropout/DISP paragraph) or its removal.

## 11. Not done or open
- Zhou & Lu full-text read (E1 only): `\todo` in related.tex and discussion.tex. The Wang corrigendum is unread.
- FOIL, Omni-Diffusion and the corruption-suite citations: no verified entries, `\todo{AUTHOR}`.
- D18 answer (A4.2.6) and the C4-4 re-signature: not in the manuscript; Appendix A.4 item 11 is a `\todo`. No sentence uses "when does input gating help" (reading 1).
- M1 co-attestation status: `\todo` in Appendix A.4 item 7.
- Fig. 1, the summary figure and the status-map figure belong to the figure engineer; only the existing probe-1 figure environment was kept in place.
- Highlights (`\item \todo`) and the abstract result sentence wait for the label; highlight length limit (85 characters) is in the outcome book.
- The 5p,twocolumn page estimate was not run.
- I did not open runs/P2-GATE-M3/family.json, so the Results headroom section and the operating-point wording are placeholders.
