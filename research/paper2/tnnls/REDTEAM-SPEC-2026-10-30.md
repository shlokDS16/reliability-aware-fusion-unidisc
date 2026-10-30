```yaml
agent: red-team
date: 2026-10-30
brief: Hostile review of the Paper 2 TNNLS build spec (paper2-tnnls/SPEC.md) against the binding preregistration, theory and audit rules, before any prose is written
sources_examined:
  - research/CONTRACT.md
  - paper2-tnnls/SPEC.md (full)
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md (full; r1, r2)
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md lines 273-348 (A4.1.10), 390-603 (A4.2.1-A4.2.6), 606-631 (A4.3.1), 673-678 (A4.5)
  - research/paper2/prereg/SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md lines 380-447 (A5.9, A5.10)
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md lines 653-901 (A6 signature K1-K14, C6-1..C6-11, A6 r1 check)
  - research/paper2/method/THEORY-ADDENDUM-2026-10-29.md sections 1.7, 2.1-2.6, 3.1-3.4, 4, R1.1-R1.8
  - research/paper2/prereg/GATE-AUDIT-FAMILY-L-2026-10-30.md lines 40-161; GATE-AUDIT-FAMILY-LG-2026-10-30.md lines 96-128 (+ grep)
  - research/paper2/tnnls/TNNLS-CHECKLIST-2026-10-29.md sections 0-11; EXEMPLARS-2026-10-29.md sections 3-8
  - research/paper2/tnnls/NOVELTY-AUDIT-LRF-2026-10-29.md (verdict, section 6)
  - research/paper2/CONFIRM-EVENING-2026-10-28.md section 18 (writer notes, deviations items)
  - runs/P2-LRF-L1/a6_analysis.json; runs/P2-LRF-LG/a6_analysis.json; runs/P2-GATE-M4/analysis.json (primary, outcome, ps, caveats); runs/P2-LRF-BASELINES/baselines.json; directory listings of runs/P2-LRF-BASELINES-PARITY-L1, runs/P2-ENV, runs/P2-THEORY-CHECK
  - paper2/sections/method.tex (grep for reliability / w_j only)
coverage: >
  Read in full: SPEC, A6, the A6 signature and r1 check. Read by section: A4, A5, theory addendum, gate audits, checklist, exemplars.
  NOT read: paper2/sections/*.tex prose (except one grep), the decisions ledger beyond D0085-D0089 heads, A4 r1 table, A5 sections other
  than A5.9-A5.10, SAP body (AB.1 quoted from A4.2.6), the H3/H4/S2/FOIL/suite run files, the baselines-parity run contents, the
  IEEE Editorial Style Manual itself (title-casing of prepositions is therefore unverified). No GPU, no code run beyond JSON reads.
claims:
  - statement: "The spec's Section IV places Prop. 3 (SNR-optimal soft weights) in the main text with a proof in Appendix A, which the theory addendum r1 forbids (Prop. 3 is a reference for Study 1's Tier-3 soft arms only, beside the Tier-3 table, not in Method as a contribution)."
    status: supported
    evidence: "THEORY-ADDENDUM R1.1 table row 'Prop. 3, Cor. 3.1'; R1.6 heading; 3.4 last bullet; SPEC section 3 row IV and App. A"
    level: E3
    confidence: 0.9
  - statement: "LRF also raised clean-image accuracy (net +0.031, 90% CI +0.009 to +0.053) and splice128 accuracy (net +0.031, 95% CI +0.007 to +0.058) on the fresh fold, so a corruption-unspecific reweighting is not excluded by any preregistered test."
    status: supported
    evidence: "runs/P2-LRF-L1/a6_analysis.json family_L.L-NI, family_L.L4"
    level: E4
    confidence: 0.9
  - statement: "Off-the-shelf CLIP ViT-L/14 and SigLIP so400m reach 0.996-1.000 on every condition of the fresh fold."
    status: supported
    evidence: "runs/P2-LRF-BASELINES/baselines.json table"
    level: E4
    confidence: 0.95
  - statement: "baselines.json records pixel_parity 'not run'; parity was run afterwards in separate directories; no gate-auditor report on the baselines or parity exists among the audits named in the brief."
    status: supported
    evidence: "runs/P2-LRF-BASELINES/baselines.json key pixel_parity; CONFIRM s18 02:05 line; grep of research/paper2/prereg for P2-LRF-BASELINES (only the LG audit mentions the path)"
    level: E4
    confidence: 0.8
  - statement: "Study 1 noise0.1 had zero discordant items (b 0, c 0, n 500), so its printed 90% bootstrap CI is the degenerate [0, 0]."
    status: supported
    evidence: "runs/P2-GATE-M4/analysis.json primary.per_corruption.noise"
    level: E4
    confidence: 0.95
competing_explanations:
  - "L1 gain = a generic token reweighting that helps on every condition (clean +3.1, splice +3.1, noise +6.9 points), larger under noise only because NONE has more headroom there (0.733 vs 0.887 clean); no preregistered test separates this from corruption-specific reliability weighting."
  - "L1 gain = a supervised fit to the tested corruption: the frozen object was trained on all 500 M4 items x {clean, jpeg10, noise0.1, splice128}, so L1 tests new images under the training corruption, not a new corruption."
  - "L1 gain = a Gaussian-noise detector inside nbr/tbv (red-team A6 (ii)); no feature ablation exists on fresh images."
unknowns:
  - "IEEE ESM rule for capitalising four-letter-plus prepositions ('Under') - not read."
  - "Whether any third-party timestamp (OSF, Zenodo) of A6 r1 exists before the first L item - none found by grep."
  - "Abstract word count under the binding sentences - not drafted; estimated over 250 (derived, below)."
next_test: {hypothesis: "a spec v2 that removes the shared theory/weight frame passes this red team", intervention: "revise SPEC per conditions RS-1..RS-12", primary_metric: "number of fatal/major findings open", falsifier: "any fatal open", gpu_hours: 0}
```

# Red-team review of the Paper 2 TNNLS build spec (2026-10-30)

## Verdict: DO NOT SIGN (as written). One fatal, sixteen major, eleven minor.

The fatal finding (F1) blocks the gate until the orchestrator records a resolution in `decisions.jsonl`. The spec becomes signable
once conditions RS-1 to RS-12 (end of file) are met in a spec v2; I will then re-check that version only.

Note on method. My role rules say "find problems only"; the brief asks for a fix per finding. I have written each fix as a
**signature condition** (a requirement the spec must meet), not as a design suggestion. That keeps the criticism at full strength.

Results used here (all from committed runs files): Study 2 L1 noise0.1 0.802 vs 0.733, b 58 c 27, one-sided p 0.00051, 95% CI
+0.029 to +0.109 (n 450); L3 jpeg10 +0.016, Holm p 0.38; L4 splice128 +0.031, 95% CI +0.007 to +0.058, Holm p 0.049; L-NI clean +0.031,
90% CI +0.009 to +0.053; L-LEN +0.076 (n 449); LG shot +0.093 (Holm 0.00046), speckle +0.060 (0.011), impulse +0.050 (0.029; two-sided
p 0.058; 95% CI lower bound 0.0). Study 1 family P: jpeg b 0 c 1, noise b 0 c 0, splice b 1 c 3; label negative. CLIP/SigLIP
0.996-1.000 on every condition.

---

## Answers to the five questions

### Q1. Does the section order or Fig. 1 create a problem/solution arc? Yes, and by design.

The spec's sequence is: Section III defines `S_w = sum_j w_j Delta_j` as "the shared notation of both studies". Section IV then gives
Prop. 2 ("when hard withholding raises the SNR") followed by Prop. 3 ("SNR-optimal weights"). The corrected Prop. 3(a) (R1.6 item 1) says
the optimal weight is soft, and a 0/1 gate is optimal only in a degenerate case. Section V presents the 0/1 rule and its null. Section VI
presents the learned soft rule and its gain. Fig. 1 draws the two rules as two panels of one schematic.

That is the textbook arc of a method paper: a general frame, then theory showing the special case is suboptimal, then the special case
failing, then the general learned case succeeding. No sentence is needed for the reader to conclude "hard gating failed, so we learned
soft weights". The red-team A6 signature (K5) names exactly this risk: "A6.12 controls sentences, but it does not control section order,
figures or tables". The withdrawal list includes "any sentence, section order or figure linking LRF to the P null" (signoff line 825).
A6.1 consequence 2 bars it in section order, figure or table. The spec's own rule 3 forbids it. Sections III-IV and Fig. 1 contradict
rule 3 of the same file. See F1 to F4.

**Compliant architecture (condition RS-1).** The paper's coherence must come from the shared measurement object, not from a weight axis
that makes Study 2 a generalisation of Study 1:
- **I Introduction.** One problem: how a unified masked diffusion model's own per-token likelihood evidence for image-caption verification
  behaves when the image is damaged. Two separately preregistered questions follow, each stated on its own terms: (Q1) does discarding
  tokens flagged by the model's masked-likelihood score, with the threshold set by conformal risk control, change verification accuracy?
  (Q2) does one frozen, learned per-token weighting raise accuracy on fresh images? The contribution list is A4.2.4 bullets 1-6 for Study 1
  plus Study 2 bullets, each with a section pointer. No "however", "therefore" or "instead" between Q1 and Q2. No chronology (see F11).
- **II Related work.**
- **III Shared setting (notation only).** UniDisc, tokens, `Delta_j`, the **unweighted** sum `S = sum_j Delta_j` and its decision,
  corruptions, the fold and fresh-image policy, test conventions, and the multiplicity statement (17 families, 0.58, "no adjustment
  across families"). No `w_j`, no `I_j`, no `S_w`.
- **IV Study 1, self-contained.** Method: the gate, `prop:crc` (the only guarantee), then Lemma 1 and Prop. 2 in the R1.8 text "directly
  after the paragraph that ends with Eq. eq:snr", with the theory figure here (A4.2.5 item 7: "in the Method section"). Then protocol and
  results. `I_j` is introduced here.
- **V Study 2, self-contained.** V-A the A6.13 disclosure (once). Then the method, motivated on its own terms (A6.1 consequence 3) from
  the reliability-weighted fusion and attention-MIL literature, never from Props. 2-3. `w_j` is introduced here. Then protocol, results,
  reference baselines (own table) and cost (own numbers).
- **VI Discussion.** VI-A Study 1, opening with the A4.2.3 NEG "6.1 opens" sentence, then the Tier-3 pointer and the H paragraph, each
  after that opening (A4.1.10 placement 2; A5.9 placement 2). VI-B Study 2. VI-C Limitations, each item attributed to its study, no H.
  VI-D Deviations box.
- **VII Conclusion.** One paragraph per study, no link, no H.
- **Prop. 3, Lemma 2 and Cor. 3.1** go to the supplement beside the Tier-3 table, labelled "theory reference for Study 1's soft
  comparators; not used in Study 2". Alternatively they are dropped.
- **Fig. 1** shows the shared measurement only: image and caption to tokens, the per-token `Delta_j` map, the sum, the decision, and
  corruption as input damage. It has no weight rule, no study panels and nothing on a 0-to-learned axis. Each study's method figure, if
  any, sits inside its own section.
- **Order.** Keep the chronological order (Study 1, then Study 2). Reversing the order would put the post hoc study ahead of the study it
  was designed on, and the A6.13 sentence "added after Study 1 had been analysed" would then point forward. It would also make Study 1
  read as an ablation of LRF ("the hard version fails"), which is the banned "contrast". Neither order is safe while a shared weight frame
  exists. With the frame removed, chronological order is the honest one.

### Q2. Is Prop. 3 allowed in the main text? No.

- R1.1 (status table, r1 governs r0) lists Prop. 3 and Cor. 3.1 as "Theoretical reference for the A4 soft arms only ... Beside the A4
  Tier-3 table, as a reference; not in Method as a contribution".
- R1.6's heading repeats "reference for the soft arms only". Section 3.4: "A later reader may use Prop. 3 only to say what the arms
  approximate under a model."
- R1.6 item 3: Props. 2 and 3 "are not jointly applicable, and no sentence may combine them". A shared theory section that states them
  in sequence under one title ("Theory of reliability-weighted evidence") combines them by construction.
- The spec moves the Tier-3 table to supplement S-II, so Prop. 3's only permitted home is supplement S-II.
- The theory addendum's r0 section 4.1 (Prop. 3 in Method) is superseded by r1.
- The spec's rule 5 also rewrites the binding label "a model of when withholding helps an additive statistic" (section 4 item 2) as
  "withholding **or weighting**". The added two words are exactly the bridge to Study 2.

What the paper can carry: `prop:crc` (Study 1, the only guarantee); Lemma 1 and Prop. 2 (R1.8 text, Study 1 Method, theory-only figure,
labels of section 4 item 2, R1.7 rules); optionally the R1.5 sentence; Prop. 1 as at most one background sentence, and only with the
lead's must-not-claim-6 ruling (R1.2 item 4). Study 2 carries no theory. That is a fit cost (F14), and it is the honest state.

### Q3. The branch A title

- **Acceptable for TNNLS.** No must-not word, no symbol, no "new/novel" (checklist C6). The model is named (A4.2.2 item 3). The checklist
  records no length cap. The title is long (24 words) and declarative ("Raised", past tense), which is unusual but not barred. A
  declarative result title is what a confirmation licenses.
- **Title-casing is typography, not substance.** One caveat: the checklist's ESM summary capitalises "nouns, pronouns, adjectives, verbs,
  adverbs, subordinating conjunctions" and names no prepositions. "Under" should therefore follow the ESM text verbatim (not read by me).
  Either form is typography.
- **No alternative is permitted.** Reasons: A6.12 (branch titles "fixed now"); gate audit L line 137 ("the branch A title ... and no
  other"); A5.1 amendment item 6 (A6 may only be tightened after the first L item). A shorter title would drop scope, which loosens. An
  added qualifier would be a substance change, needing a signed amendment, and is not needed.
- **Two problems remain:**
  - (a) "fusion" is in the title, while A4.2.2 item 4 says "'fusion' appears in **no title** (C4-7)". A6 > A4 "only on the points
    listed". A6.12's title is such a point, but no dated row says so (F10).
  - (b) The spec invents a running head ("Learned Reliability-Aware Fusion of Token Evidence in UniDisc"). That is a second, shorter
    title. It drops the result and "preregistered" and keeps "fusion". It is an "other" title under the L audit (F10).

### Q4. TNNLS fit: the biggest rejection risks and how the text can face them honestly

| # | Risk (hostile-AC wording) | Severity for acceptance | What the text must do (within the rules) |
|---|---|---|---|
| R1 | "A 20-point-worse verifier made 7 points less bad, at 27 s per item, while CLIP is at 1.000." (baselines 0.996-1.000) | likely reject alone | Intro states why the model's **own** evidence is the object (a unified model scoring its own inputs without an external encoder), with cited uses. Limitations says, without comparison words: "This paper makes no claim of a competitive verifier; the reference encoders in Table III almost solve this matching task." The ops-log note (s18 02:05) already uses this sense. |
| R2 | "Incremental: attention-MIL pooling (Ilse et al. 2018) with a GAM scorer on diffusion-classifier evidence (Clark & Jaini 2023)." Novelty audit verdict `incremental`, 0.70 | major | Related work cites both and states the delta. No "first". "To our knowledge" is scoped to the search. TNNLS Full Paper asks for work "not of incremental nature" (checklist section 1), so the contribution must be stated as a preregistered confirmation plus a bounded null, not as a new principle. |
| R3 | "One model, one severity, one dataset, random negatives, 450 images." | major | `{S}` in every LRF sentence. The stop rule (A5.1 amendment item 2) bars new confirmatory work, so a response to a reviewer request can only offer Tier 3. Plan that response wording now. |
| R4 | "No ablation, no fusion baselines: is the 35-feature GAM needed, or is it one noise detector?" | major (the experiment whose absence rejects; see the AC preview) | Name the absence in Limitations. Any CPU ablation on the stored fresh-fold arrays is Tier 3: labelled "added after the primary, family H and Study 2 results", every variant reported, kept out of title, abstract, conclusion and contributions, and listed in the deviations box. |
| R5 | "'Reliability-aware' is a name, not a finding: it also gains on clean and splice." | major | F12. |
| R6 | "Trained on sigma 0.1 noise, tested on sigma 0.1 noise." | major | F11: say it in Methods and Limitations. |
| R7 | "Preregistration in a private git repo with self-recorded times, audited by the same team." | major | F16, F17. |
| R8 | "Seventeen families; L4 at Holm 0.049; impulse two-sided 0.058." | minor | Print the family count, Holm p and the two-sided p (F7, F25). |
| R9 | "Study 1's noise interval is [0, 0]; that is not an interval." | major | F18. |

### Q5. What is missing from the spec

These items are covered in F8, F9, F15, F16, F17, F19, F25, F27 and F28: the contribution list; the Discussion-opening sentence; the
second scope sentence and the abstract word budget; the enumerated deviations box including D0088; the reproducibility statement
(empty env-locks, untracked arrays, CRLF/LF hashes); AI-run audits; the time-input table (A4.3.1); the family-count sentence; the cover
letter, README and Zenodo placement; and an override list for the exemplar blueprint. The full must-not word list is under RS-10.

---

## Findings

| # | Sev. | Finding | Rule broken | Fix (condition) |
|---|---|---|---|---|
| F1 | **fatal** | Section IV, "Theory of reliability-weighted evidence" (Lemma 1, Prop. 2, Prop. 3, proofs in App. A), sits between the shared notation and the two studies. It makes Prop. 3's soft optimum the frame that Study 1 falls short of and Study 2 instantiates. This is a problem/solution arc by section order and theory placement. | A6.1 cons. 2-3; A6.12 placement 2; C6-4 ("no section ... arranges Study 1 and Study 2 as problem and solution"); signoff withdrawal list l.825; THEORY R1.1, R1.6 (heading, item 3), 3.4; SPEC rule 3 and rule 5 | RS-1 architecture. Delete Section IV. Put Lemma 1, Prop. 2 and the theory figure in Study 1's Method (R1.8 placement). Put Prop. 3, Lemma 2 and Cor. 3.1 in supplement S-II beside the Tier-3 table with the "reference for the soft comparators" label, or drop them. Remove Prop. 3 from App. A. The orchestrator records the resolution in `decisions.jsonl`. |
| F2 | major | Fig. 1 draws "Study 1: calibrated withholding (0/1)" and "Study 2: learned weight w(x_j)" as two panels of one schematic. Without arrows or numbers it still shows the hard and soft cases on one axis, on page 1. | C6-4 (no figure arranges the studies as problem/solution); A6.12 placement 2 | Fig. 1 shows the shared measurement only (RS-1). No weight rule and no study labels appear on it. |
| F3 | major | Section III's `S_w = sum w_j Delta_j` "as the shared notation of both studies" recasts Study 1's input-level gate as a fusion weight. Study 2 then becomes its generalisation; "notation only, no claim" does not undo that. | A4.2.2 item 3 ("input-level source validation, never decision-level fusion"); A4.2.4 bullet 1 (the measured object); C4-7; A6.1 cons. 2 | Section III defines only the unweighted `S`. `I_j` is defined in Study 1, `w_j` in Study 2, and neither section references the other's symbol. |
| F4 | major | Fig. 2 = the Prop. 2 frontier plus an "optional inset of Prop. 3 weight shapes". That puts Props. 2 and 3 on one canvas. The inset would sit two figures before Fig. 4 (LRF's learned weight shapes): a visual "theory explains LRF". | R1.6 item 3; SPEC rule 5 (Prop. 3 never motivates or explains LRF); A4.2.5 item 7 | No inset. The frontier figure is theory only, with no measured point, no marking of where any condition "sits", and no annotation of the diagonal "random gate" region beyond the statement itself. It sits in Study 1's Method. |
| F5 | major | Table I holds P, S-C, PS, S-D, S-M, S2, B and H in one table. | A4.2.5 item 3 ("PS never shares a canvas with P ... own table or figure"); item 4 (nothing else on the P canvas: no AUROC); A5.9 placement 1-3 (H only in its own table and figure, with the prefix, never beside PS, never in another table's caption) | Table I = family P only (n, b, c, n_d, accuracies, net, 90/95/98.33% CIs, Holm p, preregistered decision). PS gets its own table, "Positive control (pipeline check)". Detection gets its own table with the M1 rival, sign and AUROC with CI (A4.2.2 item 2). H gets its own subsection "Family H (added after the primary result)" with the mandatory prefix. An optional status map shows status only, no estimates (A4.2.5 item 6). |
| F6 | major | Table IV (cost) rows NONE, GATE-M, LRF, CLIP, SigLIP put GATE-M results measured on M4 beside LRF numbers, and LRF beside CLIP/SigLIP. | A6.12 placement 2 ("No figure or table contains both GATE-M results on M4 items and LRF numbers"); A6.6 ("no column of LRF numbers inside that table"); A6.12 must-not (any comparison of LRF with GATE-M or CLIP/SigLIP) | Split cost three ways: GATE-M cost in Study 1; LRF cost in Study 2 (own sentence or table, NONE as its only reference); CLIP/SigLIP cost inside Table III. No cross-study cost table. |
| F7 | major | SPEC rule 2 says impulse is "stated with its one-sided Holm p only". The LG audit (lines 119-120) requires "the one-sided preregistered alpha and the two-sided p beside the impulse row". A6.4 requires "exact one- and two-sided p" with every test. The ops-log note (s18 01:07 item (i)) is the outlier. Following it hides that impulse fails a two-sided test. | A6.4 "Reported with every test"; LG audit section 5 | Print the one-sided p, Holm p and two-sided p (0.058) for every LG cell, and state that the 95% CI lower bound is 0.0. "Only" applies to the claim (no two-sided claim), not to what is printed. The lead logs which writer note governs. |
| F8 | major | The spec has no contribution list and no mapping of the binding Discussion opening. A4.2.4 fixes Study 1's numbered bullets. A4.2.3 fixes the NEG "6.1 opens" sentence. A4.1.10 and A5.9 place Tier 3 and H only *after* that opening. | A4.2.3, A4.2.4, A4.1.10 placement 2, A5.9 placement 2 and 4 | Add a contribution list: A4.2.4 bullets 1-6 verbatim in substance (bullet 6 by status only; H by status with the post hoc label), plus Study 2 bullets (frozen object, preregistered confirmation with `{S}`, reference and cost). Each bullet ends with a section pointer, and no bullet links the studies. VI-A opens with the NEG 6.1 sentence. |
| F9 | major | The abstract spec is incomplete and probably over 250 words. (a) Study 1's NEG sentence ends "This is {S}" with **A4.2.2 item 7's** scope (random other caption as the negative). The spec names only A6.12's `{S}`. (b) The NEG sentence quotes "'GATE-M has no effect'", an abbreviation the abstract rule bars, and the spec gives no substitution. (c) A6.12's L1 sentence carries the L-LEN clause, which the spec omits. (d) Estimate (derived, not drafted): setting about 30 words, NEG with three triples about 75, A4 scope about 30, L1 with the L-LEN clause about 55, L-NI about 35, A6 scope about 35, openness about 20: about 280-330 words. | A4.2.3 NEG; A4.2.2 item 7; A6.12 sentences; checklist C3, C6 | Before W1 starts, the lead writes the abstract skeleton from the binding sentences with every abbreviation spelt out, counts it, and logs a dated row for each substitution: "This does not show that the gate has no effect" for the quoted phrase, and "95 percent confidence interval" for "CI". If the count exceeds 250, the statistician rules in a dated row on merging the shared part of the two scope sentences. That is not a writer's choice. No harm clause appears in the abstract (no condition fell); the "no reduction" sentence is Results-only (L audit line 143). |
| F10 | major | (a) "fusion" in the title against A4.2.2 item 4 / C4-7, with no dated precedence row. (b) The invented running head is a second title, keeps "fusion" and drops "preregistered". | A4.2.2 item 4; A6 precedence clause (line 43); L audit line 137 | (a) A dated row: A6.12's branch-A title governs A4.2.2 item 4 for Study 2's title only, and Study 1's family B never appears in any title. (b) No invented short title. The anonymous build uses the journal name only in the header; at camera-ready the production short title is the full title or a dated-row abridgment that keeps "preregistered" and the scope. |
| F11 | major | The Limitations list breaks one rule and misses the most damaging items. (a) "post hoc design of LRF disclosed" restates the chronology outside Methods. (b) "COCO random negatives" next to the P null is one clause away from the barred "P was null because the negatives were easy". (c) Missing: LRF was **trained on the tested corruption** (all 500 M4 items x {clean, jpeg10, noise0.1, splice128}, A6.2), so L1 tests new images, not a new corruption; possible COCO overlap in UniDisc, CLIP and SigLIP pretraining (unknown); one corruption realisation and one mask seed per image (A6.4 estimand); the A-8 residual (up to about 1.5% of tokens differ between processes); the margin note. | A6.12 placement 3 and A6.13 ("once"); A5.9 must-not 1; A6.2; L audit fix 4(b); signoff "residual risks" | Limitations points to Section V-A for the design history and does not restate it. The negatives line is worded as scope only ("all results are for random-caption negatives") and kept out of the Study 1 limitations paragraph. Add every missing item (c), each attributed to its study. Study 2 Methods states the training conditions in plain words. |
| F12 | major | "Reliability-aware" asserts a mechanism that no test supports. LRF also raised clean (+0.031, 90% CI +0.009 to +0.053) and splice128 (+0.031) accuracy; a generic reweighting is the cheapest explanation. The binding L-NI sentence ("lost no more than three points") is printed with an all-positive interval, which a reader can take as concealment. Fig. 4's example maps "under noise" only invite a reading of the weights as noise detectors. | A6.12 must-not (no validated claim); L audit line 152 (clean superiority not preregistered); SPEC rule 5 spirit | "Reliability-aware" is the method's name only. No sentence says the weights track reliability or corruption. Table II prints both arms' clean accuracy and the net with CIs. Results says, once, that the clean estimate was positive and that superiority on clean images was not a preregistered hypothesis. Limitations states that no preregistered test separates corruption-specific weighting from a generic gain, and that the title's "under Gaussian noise" names the tested condition, not a specificity. Fig. 4's maps show the same three items clean and noisy on one colour scale, captioned "descriptive; not evidence that weights track corruption", or are dropped. |
| F13 | major | The novelty audit (`incremental`, 0.70) is not a spec source. Its two quotable sentences break binding rules: (i) "the weighted sum approximates the matched filter" (Prop. 3 as LRF's mechanism); (ii) the section 6 novelty sentence, which joins LRF and "a condition under which gating raises the evidence SNR" in one sentence and calls the result "exploratory". | SPEC rule 5; R1.6; A6.1 cons. 2-3; A6.14 item 4 | Add the audit to the spec's source list with a ban on both sentences. The novelty sentence is rewritten for Study 2 alone (fresh fold, confirmed, scoped "to our knowledge" to the logged search). Ilse et al. 2018 and Clark & Jaini 2023 are cited by citation-validator. |
| F14 | major | Fit: the paper's only theory belongs to the null study, the method has none, and there is no ablation, competing-fusion baseline or second model. The EXEMPLARS blueprint (section 5) assumes all of these. The spec does not say how the text faces it. | checklist section 1 (Full Paper: "well-founded and conclusive", "not of incremental nature") | A named "Scope of this paper" paragraph in the Introduction: two preregistered measurements on one model, no baseline race, why. Limitations names each absence (R1-R4 above). No sentence compensates with Prop. 3. |
| F15 | major | The deviations box is "all disclosed deviations" with no list, so items will be lost. Unlisted: D0088 (the lead saw the S2 table, the FOIL B result and the H3 rule code before the re-freeze; A6.13 omits it; the L audit fix 4(d) leaves it to the writer). Also D0087 committed after the H3 driver started (s18 19:01). Also pins.json at 22:42 during L1. Also try1/try2. Also the steward's 162 unopened JSON files. Also the CRLF/LF hash forms. Also env-lock files empty and pip freeze taken after the runs. Also parity files moved from a wrong out-dir. Also baselines.json "pixel_parity: not run" against the later PARITY runs. And A4.5 items (1)-(5), A5.14, A5.1 amendment item 7. | A6.0 item 2; A6.13 (C6-7: name what was seen); A4.5; L audit fix 4; LG audit F2-F3; CONFIRM s18 | The spec enumerates the box, item by item, with sources. Red-team position on D0088: **add one clause to the A6.13 disclosure** (S2 table, FOIL B and H3 rule code seen before the re-freeze; the re-freeze protocol was fixed). Leaving it out is the omission a preregistration auditor will find first. |
| F16 | major | There is no reproducibility statement, and the openness sentence ("preregistration, frozen hashes, code") overstates. env-lock.txt is 0 bytes in M1, M4, RESCORE, L1 and LG; the environment exists only as a pip freeze taken after the runs (`runs/P2-ENV/pip-freeze-2026-10-30.txt`). The arrays are untracked, so a clone cannot regenerate the predictions. The registration consists of commits in a private repository with self-recorded times; no third-party timestamp was found. | L audit section 5 "not done"; LG audit F3; A6.14 item 6; signoff (3) item 6 | A reproducibility paragraph states each fact. "Preregistered" is defined once, exactly: a dated addendum in a version-controlled repository, hash-pinned object, commit order as evidence, no third-party timestamp. The anonymised mirror must preserve commit times and hashes. The abstract's openness sentence claims no more than that. |
| F17 | major | The auditing roles (red team, gate-auditor, data-steward, statistician) are AI agents. Rule 6 confines AI to the Declaration, so a Methods sentence such as "an independent auditor verified the commit order" would mislead by omission. | AC-POL (identify sections and level of AI use, checklist section 7); CONTRACT rule 4 | Methods names the checks as "scripted and agent-run audits (see Declaration)" without the word AI. The Declaration lists each role, the system and the sections affected. Never "independent" for any check run by the authors' pipeline. |
| F18 | major | Study 1 P2 (noise): n_d = 0, so the bootstrap 90% CI is [0, 0] and the NEG claim's interval is degenerate. P1 has n_d = 1 and P3 n_d = 4. A reviewer will say the gate changed no decision on noise and that "[0, 0]" is not an interval. | A4.1.10 r2/r3 reasoning (degenerate bootstrap at small n_d); A4.2.2 item 1 (numbers only from committed files) | Table I prints b, c and n_d for every row. If an exact bound (Clopper-Pearson upper limit of n_d/n) is shown, it is computed into a `runs/P2-PAPER-*` file, labelled "added at writing, descriptive", and listed in the deviations box. The NEG sentence is unchanged. |
| F19 | minor | A4.3.1's mandatory statement ("UniDisc's denoiser has no time input in the released configuration ...") with its file:line table and the key-check limits is not placed anywhere. | A4.3.1 | Put the sentence in Section III and the table in the supplement (with a pointer). Record the move from "App. A" in the deviations box. |
| F20 | minor | Supplement S-V presents "Proposition 1 (detectability limit)" as a section. r1 withdrew it as a contribution: at most one background sentence, ruling-dependent; Cor. 1.1(iii) is nowhere. | THEORY R1.1, R1.2 item 4, R1.3 | Drop S-V. Keep the one permitted sentence if the lead's must-not-claim-6 ruling allows it, never next to M1, the rival or P. |
| F21 | minor | S-IV puts M4-item LRF cross-fit numbers and the fresh-fold GATE-M arm in one section. A shared table would compare LRF and GATE-M. S-II (Tier 3, with GM on M4) and S-IV must also never share a table. | A6.12 placement 2-3; A6.1 cons. 1; C6-8 | Separate tables. No LRF column next to any GATE-M number. No in-sample or `freeze_check.json` number anywhere, including the supplement. |
| F22 | minor | Proposition numbering: method.tex's `prop:crc` is cited elsewhere as "Prop. 1", while the spec uses the addendum's "Props. 2 and 3". Writers will collide. | THEORY 1.7 item 4 | The spec refers to `prop:crc`, `prop:snrcorr` and so on by label, not by addendum number. |
| F23 | minor | Fig. 3 spec says "90% CIs and the +-0.05 band". A4.2.5 item 1 requires the 90% interval thick, the 95% thin, a solid 0 line and dashed +-0.05 lines. | A4.2.5 item 1 | Copy A4.2.5 item 1 into the Fig. 3 spec. |
| F24 | minor | Naming echoes link the studies. Study 1's algorithm is `ReliabilityScores` (method.tex l.142). Study 1's family B is "two-way fusion". Section V's title is "calibrated token withholding" ("calibrated is not a selling word"). | A4.2.2 items 2-4; C6-4 | Study 1 uses "the gate's masked-likelihood score" and "suspicion score u_j". B keeps its preregistered descriptor, never "fusion" in a heading. Section V is titled with "conformal risk control" or "masked-likelihood token gating". |
| F25 | minor | The family-count sentence (17 families, 1 - 0.95^17 = 0.58, "no adjustment across families") is not in the spec. The L audit says it must accompany family-L claims. | A6.7; L audit line 151; LG audit line 106 | Put it in Section III and repeat it in both Results sections. |
| F26 | minor | The page budget sums to 13.8 pages before title, abstract and float slack; App. A counts toward the 15-page cap. | checklist section 1 | Recompute after RS-1 (App. A shrinks without Prop. 3). Target 13 or less. |
| F27 | minor | The cover letter, response text, README and Zenodo description are not under any spec rule. H is barred there (A5.9). The no-link and no-rescue rules cover the cover letter (C6-6). | A5.9 placement 1; C6-6 | Add a section: these texts follow the abstract's placement rules, with no H and no study link. |
| F28 | minor | The spec cites EXEMPLARS as a writer source. Its blueprint conflicts with binding rules: rule 2 ties experiments to propositions; rule 3 asks for a page-1 "failure and fix" figure; 5.2 Fig. 4 is "the result the theory predicts"; 5.3 ablates "hard gate versus soft weighting"; section 7 frames the gating analysis "as the empirical test of Proposition 2". | AB.1; R1.7; THEORY section 4 item 4; C6-4 | The spec lists those exemplar rules as overridden. Writers take only layout, contribution-pointer and limitations conventions from EXEMPLARS. |
| F29 | minor | LRF's features include Study 1's score components (D, B, s3) and Study 1's detection rivals (tbv, tex, nbr). Writers will describe them by their Study 1 roles ("the M1 rival"), which builds the link through the feature table. | A6.1 cons. 2; A4.2.2 item 2 (K2) | The feature table (in the main text, Section V) defines each feature by formula. No feature is named by its Study 1 role, and no sentence says LRF "uses what the gate missed". |
| F30 | minor | The title says "image-text verification"; the measured decision is image-direction (A4.2.2 item 1; A6.12 L1 sentence). | A4.2.2 item 1 | The first use in the Introduction defines the title's term as the image-direction decision. |

---

## Cheapest alternative explanations of the positive results (for the Discussion and Limitations)

1. **L1:** a corruption-unspecific reweighting. The clean (+0.031) and splice (+0.031) gains point this way, and the noise gain is larger
   where NONE has more headroom. Not excluded by any preregistered test.
2. **L1:** a supervised fit to the training corruption (noise0.1 was a training condition). L1 replicates on new images, not on a new
   corruption.
3. **L1, LG:** a noise detector inside nbr and tbv. With no feature ablation on fresh images, Fig. 4 cannot separate this.
4. **LG:** shot and speckle noise are close relatives of Gaussian noise. Impulse, the one structurally different cell, has a 95% CI that
   starts at 0.0 and a two-sided p of 0.058.
5. **L4:** Holm p 0.049, a margin of 0.001; one or two discordant items flip it.
6. **Study 1 NEG:** the gate changed almost no decision (n_d 0, 1 and 4 of 500), so the "bounded null" bounds an intervention that
   barely acted.

## Hostile area-chair preview (TNNLS), on the paper as the spec would produce it

- **Summary.** Two preregistered studies on UniDisc 1.4B, image-caption verification under three image corruptions. A conformal-risk-
  control token gate changes accuracy by less than 5 points. A learned GAM token weighting, designed on the first study's test items and
  frozen, raises accuracy under sigma 0.1 noise from 0.733 to 0.802 on 450 fresh images.
- **Strengths.** Exact paired tests and intervals everywhere. A hash-pinned frozen object and a fresh fold. A full disclosure of the
  design history. A bounded null reported as such. Honest multiplicity accounting.
- **Weaknesses.**
  - CLIP and SigLIP are at 0.996-1.000 on the same items, so the practical significance is unclear.
  - Novelty is incremental over attention-MIL and diffusion-classifier weighting.
  - One model, one dataset, one severity; the method was trained on the tested corruption.
  - No ablation or competing fusion method.
  - The theory belongs to the null study.
  - "Reliability-aware" is unvalidated (clean gain).
  - The preregistration is self-hosted.
- **Questions.** Is the GAM needed, or would one feature do? Does the gain survive on a second backbone? Why should a reader use UniDisc's
  own evidence for verification?
- **Score.** Reject (weak reject at best); confidence 4/5.
- **The one experiment whose absence causes rejection:** a fresh-image comparison of the frozen weighting against simpler aggregation
  rules at the same budget (a single-feature weight, an unlearned reliability weight, an attention-MIL pooling baseline). Without it a
  reviewer cannot tell whether the method or one noise feature carries the gain. Under the stop rule it can only be Tier 3 now.

## Conditions for signature (spec v2)

- **RS-1** (F1-F4): the architecture of Q1. No shared theory section, no `S_w`, a measurement-only Fig. 1, Prop. 3 in the supplement or
  dropped. A dated `decisions.jsonl` row resolves F1.
- **RS-2** (F5, F6, F21, F23): table and figure canvases as in the fixes. P alone. PS, detection and H separate. No cross-study cost
  table. A4.2.5 item 1 for Fig. 3.
- **RS-3** (F7): both p-values printed for every LG cell. A dated row reconciles the ops-log note with the LG audit.
- **RS-4** (F8): the contribution list and the 6.1-opening mapping.
- **RS-5** (F9): an abstract skeleton, counted, with dated substitution rows before W1 starts.
- **RS-6** (F10): a precedence row for "fusion"; no invented running head.
- **RS-7** (F11, F12): the Limitations rewrite (training corruption, generic-gain alternative, pretraining overlap, A-8, no restated
  chronology). "Reliability-aware" as a name only. The Fig. 4 rule.
- **RS-8** (F13, F14, F28): the novelty audit as a source with its two sentences banned, an exemplar override list, and a scope paragraph.
- **RS-9** (F15, F16, F17): an enumerated deviations box including the D0088 clause in the A6.13 disclosure; a reproducibility paragraph;
  the "preregistered" definition; the audit-role wording.
- **RS-10** (must-not list for the final pdftotext scan, in addition to SPEC rule 4):
  - comparison and problem/solution words: "outperform", "better than", "beats", "competitive", "unlike hard gating", "instead of
    discarding", "fixes", "overcomes", "solution", "addresses the limitation";
  - theory words for any result: "predicts", "explains", "accounts for", "is consistent with";
  - Study 1 words: "equivalent", "as good as", "on-manifold", "our detector", "decision-level fusion", "UniDisc is time-free";
  - H words: "compositional", "replication", "SugarCrepe score";
  - Study 2 words: "held-out noise family", "across noise types" and "across corruptions" as pooled claims, "trend";
  - "we prove" for Prop. 1, "independent" for any audit, "novel" and "new" in the title.
- **RS-11** (F18): Table I shows n_d, and any exact bound comes from a runs file with a label.
- **RS-12** (F15 sub-item): a gate-auditor verdict on `runs/P2-LRF-BASELINES` and both PARITY runs, reconciling baselines.json's
  "pixel_parity: not run" field, before any CLIP or SigLIP number enters the main text (A6.6: "else no baseline number in the main text";
  FRAMEWORK: gates pass only on a gate-auditor verdict).

## What would force rejection of a claim in the eventual manuscript

- Any section order, figure, table or sentence that presents Study 1 as LRF's motivation or LRF as Study 1's answer, including a shared
  weight frame or Prop. 3 in the main text. That withdraws the A6 signature.
- Any LRF number beside a GATE-M number in one table or figure, or LRF beside CLIP/SigLIP in one table.
- A clean-image superiority claim, or a claim that the weights track reliability or corruption.
- CLIP/SigLIP numbers in the main text without an audited parity record.
- A preregistration description that implies a third-party timestamp or an independent auditor.

## Ledger

No rows added. The brief names one output file; the resolution of F1 is the orchestrator's `decisions.jsonl` row.

---

# Re-check of v2 (red team, 2026-10-30, on commit bc02667b: paper2-tnnls/SPEC.md v2, decisions D0090-D0094, drafts/abstract-skeleton-v1.md)

Read: SPEC v2 in full; D0090-D0094 in full; abstract skeleton in full. Not re-read: the binding addenda (quoted from the v1 review above).
Not checked: the AD.11 status map behind the v2 contribution-bullet-6 statuses; the RS-12 audit (running); the statistician's RS-5
ruling (pending).

## Verdict: SIGN WITH CONDITIONS (V2-1 to V2-6). The fatal F1 is resolved (D0090, SPEC rules 3-4, section 3 rows III-V, Fig. 1-2 rules). Confidence 0.75.

## Status of v1 conditions

| Condition | Status in v2 |
|---|---|
| RS-1 (F1-F4) | **MET.** No shared theory section, no `S_w`; `I_j` only in Study 1 and `w_j` only in Study 2; Prop. 3 in S-II with the required label; Fig. 1 shows the measurement only; Fig. 2 is theory only, no inset; chronological order. The D0090 row exists. |
| RS-2 (F5, F6, F21, F23) | **MET.** Table I is P only; PS, detection and H have their own canvases; cost is split per study, with CLIP/SigLIP cost inside Table III; S-IV tables are separate; Fig. 3 follows A4.2.5 item 1. |
| RS-3 (F7) | **MET** (D0091). |
| RS-4 (F8) | **MET, one gap** (V2-5). |
| RS-5 (F9) | **OPEN, pending.** The skeleton counts 295/290 words; the statistician ruling is due (V2-3). |
| RS-6 (F10) | **MET** (D0092). |
| RS-7 (F11, F12) | **MET for Study 2. One new violation in the Study 1 Limitations** (V2-1). |
| RS-8 (F13, F14, F28) | **MET** (section 3 row II, row I scope paragraph, section 11). |
| RS-9 (F15-F17) | **MET** (sections 8, 9; rule 6; D0094). |
| RS-10 | **MET** (rule 5). |
| RS-11 (F18) | **MET** (Table I). |
| RS-12 | **OPEN, pending** the gate-auditor verdict. Table III is correctly gated on it (section 5). |

## New findings on v2

**N1 (major). The Study 1 Limitations sentence breaks A5.9 must-not 1, and my v1 report caused it.**
- v2 section 7 says: "the gate changed few decisions (n_d 0, 1 and 4 of 500), so the bounded null bounds an intervention that rarely acted".
- A5.9 must-not 1 says: "The realised P discordance may be printed in the P table as a number, nothing more", and it applies "in Methods and
  the deviations box too". "Rarely acted" is also a near relative of the barred "lacked headroom".
- My v1 list of cheapest alternative explanations (item 6) and my F18 rationale used the same reading.
- **That item is withdrawn for any paper text.** It may only inform the authors.
- In the paper, n_d appears only as numbers in Table I.

**N2 (major). The section 6 Tier-3 ablation can rebuild the banned Study 1 / Study 2 contrast, and its placement list is incomplete.**
- "Simpler weight rules" are not restricted. A hard-gate row, a conformal-risk-control or masked-likelihood threshold row, or any A4 Tier-3
  comparator (MED, TM-G, TM20, SOFT-G, SOFT-A) scored beside LRF on the fresh fold would put a Study 1 object next to LRF numbers. That
  breaks A6.12 placement 2 and the must-not, C6-4, and section 11 (the "hard gate versus soft weighting" exemplar override).
- A5.1 amendment item 2 also keeps every later analysis out of the highlights, the cover letter and the repository front matter, and v2
  section 6 lists only title, abstract, conclusion and contributions.
- The variants are chosen after L1 and LG are known. Only a fixed, complete variant list in the plan stops the choice of easy or hard
  rivals.

## Conditions still open

- **V2-1 (major, N1).** Strike the Study 1 Limitations sentence about n_d and "an intervention that rarely acted". Study 1 Limitations keeps
  scope items only (one model, one severity per corruption, random-caption negatives as scope). No sentence anywhere states or interprets
  the P discordance outside Table I.
- **V2-2 (major, N2).** The ablation plan must meet all of the following before it is committed:
  - (a) It lists every variant and every reported quantity before any fresh-fold scoring.
  - (b) It contains no Study 1 object: no GATE-M, no conformal-risk-control or masked-likelihood hard gate, no A4 Tier-3 comparator, and
    no row framed as "hard versus soft".
  - (c) It fits and selects only on the 500 design items, with no fresh-fold choice of any kind.
  - (d) It reports every variant whatever the result. If a simpler rule's interval covers LRF's, that is stated in V-G and in Limitations,
    with no rescue sentence.
  - (e) Section 6's exclusion list gains highlights, cover letter and repository front matter (A5.1 amendment item 2).
  - The statistician's check confirms (a)-(e).
- **V2-3 (pending, RS-5).** The statistician ruling must also cover the remaining abstract items:
  - "p = 0.0005" (a symbol; write it as "p-value 0.0005" or similar);
  - "JPEG" and "COCO" kept as proper names (dated row);
  - the degenerate noise interval "0.000, 0.000 to 0.000", which is binding NEG content. Keep it, and expect a reviewer to ask about it.
- **V2-4 (pending, RS-12).** No CLIP or SigLIP number in any text before the gate-auditor PASS on `runs/P2-LRF-BASELINES` and both PARITY runs.
- **V2-5 (minor).** Contribution bullet 6 names family H by status with the post hoc label (A5.9 placement 4). The gate-auditor checks the
  S2 and B "run, formal" statuses against the AD.11 status map during number reconciliation. Rule 4's detectability-limit sentence is
  used only if the lead's must-not-claim-6 ruling row exists (THEORY R1.2 item 4).
- **V2-6 (minor).** Fig. 5 shows L-NI in its own labelled panel as family L-NI (m = 1), not as a member of family L.

Writers may start once V2-1 and V2-2 are in the spec. V2-3 and V2-4 gate the abstract and Table III only.

Ledger: no rows added (the brief allows this file only).
