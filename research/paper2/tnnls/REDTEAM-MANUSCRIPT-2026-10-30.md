```yaml
agent: red-team
date: 2026-10-30
brief: Hostile TNNLS area chair plus preregistration auditor on the full Paper 2 TNNLS draft (main.pdf 15 pp, supplement.pdf); compliance pass against SPEC v2.2 rules 0-11 and RS/V2 conditions, then hostile review with fixes.
sources_examined:
  - paper2-tnnls/main.pdf (pdftotext -layout and raw; two builds: 08:3x and 08:41 IST rebuild that added V-G)
  - paper2-tnnls/supplement/supplement.pdf (14 pp, then 15 pp after the 08:41 rebuild)
  - paper2-tnnls/sections/*.tex (abstract, study1, study2, discussion, introduction read where cited)
  - paper2-tnnls/SPEC.md (v2.2); research/ledgers/decisions.jsonl D0090-D0095
  - research/paper2/tnnls/REDTEAM-SPEC-2026-10-30.md (my v1 review and v2 re-check)
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md (A4.1.10, A4.2.2-A4.2.5, A4.3.1, A4.5)
  - research/paper2/prereg/SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md (A5.9, A5.14)
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md (A6.2, A6.4-A6.7, A6.12, A6.13, A6.14)
  - research/paper2/method/THEORY-ADDENDUM-2026-10-29.md (R1.7, R1.8 by grep)
  - research/paper2/tnnls/EXEMPLARS-2026-10-29.md (sections 5-6), TNNLS-CHECKLIST (anonymity rows)
  - figures: fig3_study1_P.png; rendered main pages 1, 2, 6, 8-12, 15; supplement page 5
  - runs/P2-GATE-H3/family.json; runs/P2-LRF-L1/a6_analysis.json; exp_p2/gate/folds.py (negative rule); git log 24d36a8a, 941a260b
coverage: >
  Main text read in full (first build) and diffed against the 08:41 rebuild (only V-G and reflow changed).
  Supplement: S-I (pins, audits, families, amendments, time input, A4 disclosures, deviations), S-II Table S5-S8 and
  the Tier-3/Prop. S1 label, S-III, S-IV, S-V, S-VI, S-VIII read; S-II detail tables S9-S16 skimmed by grep only.
  Must-not scan run over raw pdftotext of both PDFs (both builds). NOT covered: the DOCX (not scanned); Section V-G and
  S-VII (out of scope per brief, read only for the hostile review); the bibliography's correctness (citation-validator's
  job); number reconciliation beyond the spot checks listed in "Numbers spot-checked".
claims:
  - statement: "Supplement Table S5 places P, S-C, PS, S-D (AUROC and rival), S-M, S2, B and H on one canvas."
    status: supported
    evidence: supplement.pdf p.5 (rendered), TABLE S5; supplement.tex
    level: E4
    confidence: 0.98
  - statement: "Study 1 and Study 2 negatives are category-disjoint, not 'a random other caption'."
    status: supported
    evidence: exp_p2/gate/folds.py lines 6-7 (assign_negatives); main Sec. IV-B "shares no annotated COCO category"; A6.4 "M4 negative rule"
    level: E3
    confidence: 0.9
  - statement: "No anonymised mirror that preserves commit hashes exists; anonymising git author metadata changes every commit hash."
    status: supported (absence: no mirror named in any project file; git hash semantics)
    evidence: grep of research/paper2/tnnls/*.md, SPEC.md, progress.md for mirror/anonymous.4open; SPEC s9 lists it as a plan
    level: E3
    confidence: 0.8
  - statement: "A6.4's 'reported with every test' quantities (90% CI, Clopper-Pearson CI of b/n_d, mid-p) for L1, L3, L4, L-LEN and LG are computed but printed nowhere."
    status: supported
    evidence: runs/P2-LRF-L1/a6_analysis.json family_L.L1 keys ci90, cp95_b_over_nd, p_mid_one; grep of both PDFs (0 hits for mid-p)
    level: E4
    confidence: 0.9
  - statement: "The Study 1/Study 2 separation (no LRF beside GATE-M, no shared weight symbol, theory placement) holds in the main text."
    status: supported
    evidence: grep of sections/study1.tex and study2.tex (non-comment lines); Sec. V has no 'GATE-M' or 'gate'; Sec. IV has no 'LRF', 'Study 2', 'w_j'
    level: E4
    confidence: 0.85
competing_explanations: []
unknowns:
  - Whether every agent stage ran on the three Claude models named in the Declaration (memory records a silent fallback to claude-opus-5 for one screener in this project).
  - Whether TNNLS will charge or cap at 15 pages for this article type (SPEC cap is 15; main is at 15).
next_test: {hypothesis: "the build passes the binding placement rules after the fixes", intervention: "split Table S5; rerun the must-not scan on main, supplement and DOCX", primary_metric: "zero true violations", falsifier: "any P/PS/H/AUROC co-canvas or must-not hit", gpu_hours: 0}
```

# Red-team review of the Paper 2 TNNLS manuscript draft (2026-10-30)

Note on method. My agent rules say "find problems only"; this brief explicitly asks for a fix per weakness, as my
spec reviews did. Fixes are given; they do not soften the severity ratings.

Build note. main.pdf and supplement.pdf were rebuilt at 08:41 while I worked (commit b508e292: V-G paragraph,
S-VII, and the S-I delegation wording). I diffed both builds. The rebuild changed V-G and S-VII, resolved the
supplement's [AUTHOR] placeholder, and reflowed text; every finding below holds on the 08:41 build.

## Verdict

**Compliance: DO NOT SIGN as built.** There is one fatal finding, A1: a binding canvas rule (A4.2.5 item 3, A5.9
placement 1-3) is broken in supplement Table S5, which is the regression of RS-2/F5. The fix is mechanical. Once A1
and the majors A2-A6 are fixed, the verdict becomes **SIGN WITH CONDITIONS** (the minors). The main text itself is
largely compliant. The two studies are separated, the theory is placed and labelled correctly, the binding sentences
are faithful, LG prints all three p-values, the must-not scan has no true violation in the main text, and the
abstract has 247 words with no abbreviations.

**Hostile AC: reject and resubmit (4/10), confidence 4/5.** The best realistic outcome is major revision, from a
reviewer who values the preregistration.

---

## Pass A. Compliance

### A-findings (numbered; severity; location; rule; fix)

| # | Sev. | Location | Finding | Rule | Fix |
|---|---|---|---|---|---|
| A1 | **fatal** | Supplement S-II, TABLE S5 "Study 1 Families on One Overview" (p.5) | One table holds P (3 rows), S-C, **PS** (2 rows, "positive control not met"), **S-D (AUROC, q minus frozen rival)**, S-M, S2, B and **H** ("H-NOGO: not tested; downstream claim withdrawn"). Its caption names H and cites runs/P2-GATE-H3. It is not the optional status map, because it prints estimates. This is the F5 defect I rated in v1, which RS-2 resolved in the spec; the build has reintroduced it. | A4.2.5 item 3 ("PS never shares a canvas with P, any label"), item 4 ("Nothing else on the P canvas: no AUROC, rival"); A5.9 placement 1 (no H in "the caption of any figure or table other than H's own"), 2 (H only in its subsection, S-III, deviations box, status map), 3 ("never on the P canvas ..., never beside PS"); SPEC rule 7/RS-2 | Delete Table S5. If an overview is wanted, use the A4.2.5 item 6 status map: one row per family, status text only, no estimates, no intervals, H by status only, hatched. P stays in main Table I; PS in Table S9; detection in main Table II; S2 and B in their own supplement tables. Then re-run the scan. |
| A2 | major | Abstract ("Each negative is a random other caption"), IV-C1 ({S}: "a random other caption as the negative"), VI-C "Both studies. All results are for random-caption negatives", Conclusion ("random-caption negatives") | The negative is the caption of another image **that shares no annotated COCO category** with the true image (Sec. IV-B; `exp_p2/gate/folds.py` l.6-7). Study 2 uses the same "derangement rule" without saying so (V-C). "Random other caption" understates how easy the negatives are, and that bears directly on reading Table V (CLIP/SigLIP 0.996-1.000). The binding {S} is literally inaccurate, and the scope sentences of both studies inherit the error. | A4.2.2 item 7 ({S}) vs the protocol; CONTRACT rule 1 (accuracy); A6.4 estimand ("M4 negative rule") | A dated decisions row records that the scope is tightened (substance becomes narrower, which is allowed). "a random other caption" becomes "the caption of another image sharing no annotated COCO category" in the abstract (within 250 words; the statistician recounts), IV-C1, VI-C and the Conclusion. V-C states the rule in plain words. |
| A3 | major | Reproducibility paragraph: "for review, an anonymised mirror is provided that preserves the commit times and hashes on which the definition of 'preregistered' ... rests" | (i) No mirror exists in any project record; SPEC s9 lists it as a plan (CONTRACT rule 5). (ii) Anonymising git author/committer metadata changes every commit hash, so commit ids printed in the paper (24d36a8a, 941a260b, 40828e96, f1671c91, ...) would not resolve in a mirror that hides the authors; file-only mirrors carry no commit history at all. During double-anonymous review the commit-order evidence behind "preregistered" therefore cannot be checked. | SPEC rule 9 ("Claim nothing more"); CONTRACT rules 4-5 | State only what exists. For example: "The repository ... with its commit history is released at acceptance; for review, an anonymised copy of the files is provided [link]; the commit identifiers in supplement S-I refer to the full repository." Before claiming that times or hashes are preserved, build the mirror and verify that property. |
| A4 | major | Declaration of Generative AI Use | (i) Two "[AUTHOR: confirm ...]" placeholders remain in the main PDF (systems list; level of use). (ii) The level-of-use sentence ("the authors directed the work ... approved ... the decisions recorded in them") conflicts with supplement S-I G(3): under the first author's delegation, "the stricter reading ... was adopted by the agent-run study pipeline" (D0076-D0077). (iii) Completeness of the systems list is unverified: project memory records a silent fallback to claude-opus-5 for one screener, and a Fable adjudicator was used in Paper 1 of this project. | SPEC rule 6 (Declaration lists each role, system, sections, level; F17); TNNLS AI policy (checklist C2) | Shlok resolves both placeholders. The level-of-use sentence names the delegated decision (D0076-D0077). The systems list is checked against the session logs of every Paper 2 stage, and any fallback model is added. |
| A5 | major | Deviations box Study 1 item (1); supplement S-I G(1) | They say the Tier-3 comparators were "fixed in an addendum committed before the main run's headroom decision". That is true of A4 draft and r1, but it omits A4 **r2 and r3**, which changed the Tier-3 reading and labelling rules (the r2 n_d < 10 bound and the r3 exact Clopper-Pearson labels). r3 was written "after family.json (R2, test fold 500) was committed and read" (A4 header, r3 row). This was before any M4 value or Tier-3 output, but after the headroom decision. A preregistration auditor will find this from the addendum header. | A4.5 item (1) ("the commit times of A4 and r1 relative to family.json and analysis_m4"); C6-7 spirit (name what was known) | Add one clause to item (1) and to S-I G(1): "the reading rules for few discordant items (revisions r2 and r3) were added after the headroom decision file was committed and read, before any main-test value or Tier-3 output existed". |
| A6 | major | Table IV and supplement S-IV | A6.4 "Reported with every test" requires b, c, n_d, n, both accuracies, net with **90 and 95%** paired bootstrap CIs, the **Clopper-Pearson CI of b/n_d**, exact one- and two-sided p, and **mid-p**. The 90% CI (except L-NI), the CP interval and the mid-p appear nowhere, although they are computed (`runs/P2-LRF-L1/a6_analysis.json` family_L.L1: `ci90`, `cp95_b_over_nd`, `p_mid_one`). n_d is not a column. | A6.4 (binding reporting rule) | Add a supplement table to S-IV with n_d, the 90% CI, the CP 95% CI of b/n_d and the one- and two-sided mid-p for L1, L3, L4, L-LEN and each LG cell, from the runs files, with `% run:` comments. Point to it from the Table IV caption. |
| A7 | major (presentation, IEEE) | Page 1, Q1/Q2 list | The description-list labels "Q1 (Study 1, Section IV)" and "Q2 (Study 2, Section V)" overprint the first line of each question; the text is illegible in the PDF (pdftotext gives "Q1 (StuDdoyes1,dSiseccatriodningIVt)h.e"). Page 1 is what the editor reads first. | SPEC rule 7/8 (layout); IEEE ESM | Use a wider label (`\begin{description}` with `\settowidth`, or `enumerate` with `label=Q\arabic*` and a separate "(Study 1, Section IV)" in the text). |
| A8 | minor | Sec. V-A, D0094 clause: "the code of the decision rule of its family H" | H is mentioned outside the A5.9 allowed places and without the prefix. It is procedure, not an H result, label, number, status or interpretation (A5.9's definition of "H content"), and D0094 mandates the clause. True hit, **not a violation**; recorded so that no later edit expands it. | A5.9 placement; D0094 | Leave as is. Do not add any H outcome to this sentence. |
| A9 | minor | Table III (Study 2) uses q_j = B_j - D_j; Sec. IV-C4 defines q_j = -u_j as "the gate's masked-likelihood score". B_j's partition size K = 8 is defined only in Study 1 (IV-A). Fig. 4(a) panel titles and V-G use code names (tbv, nbr, ltex, rank_B, nb3mean_ltex, itemsd_*); "tbv" is the "TbV score [32]" of Study 1 IV-B. | Symbol and name echoes across the studies. Every feature is defined by formula (F29 met), but a reader can rebuild the "gate score as LRF feature" link from shared symbols. | SPEC rule 3 spirit ("no shared notation"); F29 | Give the Study 2 feature its own symbol (e.g. r_j for B_j - D_j) and define K in Sec. III-B. Fig. 4 and V-G use the Table III group names or plain descriptions; code names go only in Table S21. |
| A10 | minor | Throughout | σ has four meanings: noise standard deviation; the logistic function in (13); the per-token standard deviation in Lemma 1; and σ_j, the pixel variance in Table III. n is both the caption token count (III-A) and the item count. | IEEE clarity; SPEC rule 8 | Use a distinct symbol for the logistic function (e.g. sigm or ς), call the pixel statistic v_j, and use L for caption length. |
| A11 | minor | Supplement S-II: "they predict no ranking of the comparators"; S-I G(5): "A code reading confirmed that no output of family B can reach an input of S2" | "predict" appears outside the E-pred table (R1.7 item 3 keeps "predicted" inside that table only). "confirmed" is used for something other than L1 (SPEC rule 5, LRF list; strict reading). Both are true hits on the list; neither is a substantive violation. | THEORY R1.7 item 3; SPEC rule 5 | "they imply no ranking"; "A code reading showed". |
| A12 | minor | Page 15 | The last page has an empty right column (references in one column). | SPEC rule 8 ("no empty column space"); IEEE last-page balance | Use `\IEEEtriggeratref{n}` or `balance`. |
| A13 | minor | Supplement S-I | Mild de-anonymisation cues: "IST" timestamps, "the operating system restarted the laptop for an update", "first author's written co-attestation that he...". | TNNLS double-anonymous (checklist C1) | Use UTC or plain dates. Write "the workstation" or drop the detail. Use gender-neutral wording. |
| A14 | minor | Deviations box (VI-D), env-lock item | Study 2 item (3) lists "design, re-score, L1 and other-noise stages". SPEC s8 also lists M1, the Study 1 detection stage, which is not in the Study 1 list. | SPEC s8 | Add "detection stage (M1)" to the Study 1 list. |
| A15 | minor | A5.14 disclosure | It sits only in supplement S-III; the main deviations item (5) is a pointer. A5.14 says "Methods and deviations box". The binding sample-size-proxy clause ("47.5 discordant items ... against 1, 0 and 4") is correctly dropped under A5.9 must-not 1 (r1), which governs A5.14. | A5.14 placement | Record the move in a dated row (page budget), or add one Methods sentence pointing to S-III. |
| A16 | pending | V-G / S-VII (out of scope per brief) and VI-C | Condition V2-2(d): "If a simpler rule's interval covers LRF's, that is stated in V-G **and in Limitations**, with no rescue sentence." Under noise, V-G reports intervals containing 0 for the linear logit, the B-and-D-only, the s3-only and the attention-MIL variants. VI-C says only "No ablation was preregistered; Section V-G is exploratory." V-G's sentence "an interval that contains zero does not show that the difference is zero" works as a rescue for LRF when it sits next to those rows. | V2-2(d) | One Limitations sentence: "In the exploratory ablation, several simpler weightings (a linear logit, B and D features alone, attention pooling) were not distinguishable from LRF under noise." Move the "does not show zero" sentence to the interval-definition paragraph of S-VII only. |

### Must-not scan (pdftotext raw of main and supplement, 08:41 build; every hit category, context, verdict)

**Main (15 pp).** Every hit below is checked; "no" means the hit is not a true violation.

| Word/pattern | Hits | Contexts | True violation? |
|---|---|---|---|
| robust | 3 | titles of refs [10], [26], [53] | no |
| generalis/z- | 5 | "logistic generalised additive model" (method name ×4); ref [61] title | no |
| first | 13 | ordinal or temporal only ("first test item", "first rung", "first 300 fold items", "first author", "first drafts") | no priority claim |
| calibrat- | 12 | Study 1 calibration set or statistic; ref [52] title; none for LRF | no |
| guarantee | 4 | CRC related work ×2; "This is the only guarantee in the paper" (Prop. 1); "The guarantee does not cover ..." | no (Study 1 only, permitted wording) |
| validat- | 6 | "validation-split images", "source-validation gate" (A4.2.4 term), "not validated on UniDisc" ×2 (theory label), "cross-validation" | no |
| trend | 1 | ref [48] journal title | no |
| confirm- | 4 (+2 placeholders) | title "Confirmation" (binding branch A); bullet 8; L1 definition and "L1 is therefore confirmed"; Table IV "confirmed (one-sided)"; "confirmatory study" (A6.13); **two "[AUTHOR: confirm ...]" placeholders** | wording no; placeholders yes (A4) |
| beat | 1 | ref [55] title | no |
| unlike | 1 | Prop. 2(v) "unlike (10), the condition depends on m" | no (mathematical) |
| instead | 1 | "Study 1 uses the expected-loss statement of conformal risk control instead" | no |
| solution | 3 | "super-resolution" ×2, "resolution floor" | no (false positives) |
| predict- | 12 | "trained to predict any masked token"; conformal prediction; predictive uncertainty; "stored predictions" | no (no theory-to-result use) |
| explain / accounts for / consistent with | 0 | | |
| no effect | 4 | "does not show that the gate/gating has no effect" (abstract, IV-C1, VI-A, VII) | no (binding NEG substitution) |
| compositional- | 2 | ref titles [12], [14] | no |
| independent | 8 | statistical or mathematical (independent tokens or families) | no audit called independent |
| new | 5 | "a new clean test item", "new folds", "new images, not a new corruption", "New York" | no (not in title) |
| AI | 4 | Declaration only | no |
| track | 4 | two negations ("not ... track"), "untracked" ×2 | no |
| superior | 1 | "superiority on clean images was not a preregistered hypothesis" | no (required by F12) |
| improv- | 9 | NEG sentences; [24] description "gated-fusion design improves image-text alignment"; ref [29] title | no |
| headroom | 12 | Study 1 protocol; H-NOGO sentences; no "lacked headroom" about P | no |
| hard gate | 4 | Study 1 Tier-3 (IV-C9) and its VI-A pointer | no (Study 1 only, never beside LRF) |
| fusion | 25 | title and LRF name; related work; refs; "the preregistered two-way fusion test" (family B body text, not a heading) | no (D0092; SPEC rule 3 permits B's descriptor outside headings) |
| outperform, better than, beats (claim), competitive, overcomes, fixes, addresses, equivalent, as good as, on-manifold, our detector, decision-level, time-free, replicat-, SugarCrepe score, screen-, novel, we prove, rescue, Proposition 3/Lemma 2/Corollary | 0 | | |

**Supplement (15 pp).** The same categories were scanned. True hits: "they predict no ranking" (S-II, Prop. S1 label) and
"A code reading confirmed" (S-I G(5)); see A11. All other hits are not violations:
- "predicted sign" sits inside the E-pred table, which R1.7 allows.
- "explain", "rescue", "superiority" and "improves" occur only in Table S3's must-not column or in the A4.1.10 sentence
  "cannot explain, qualify or rescue".
- "independent" occurs in "none is described as independent" and in mathematics.
- "Proposition 3, Lemma 2, Corollary 3.1 of the theory addendum" appears only in the Table S22 crosswalk.
- "reliability weighting of every token gave higher accuracy than the hard gate under swap" is the A4.1.10 "above GM"
  sentence with its binding comparator name.

**DOCX: not scanned** (SPEC rule 5 requires it; outside this brief).

### SPEC rule and RS/V2 condition checklist

| Rule / condition | Status | Note |
|---|---|---|
| 0.1 numbers from runs, `% run:` comments | spot-checked, PASS on the cells checked | See "Numbers spot-checked". No in-sample or freeze_check number found; Table S18 is the cross-fit, labelled "sets the rule only". |
| 0.2 binding wording | PASS except A2 | A4.2.3 NEG abstract and 6.1 opening are faithful (with the dated "does not show" substitution). A4.2.4 bullets 1-6 are faithful. A6.12 L1, L-LEN, L-NI and baseline sentences are faithful. A6.13 and the D0094 clause are faithful. H-NOGO uses variant (i), which is correct: `G_max_headroom` is null in runs/P2-GATE-H3/family.json. |
| 0.2 LG p-values (D0091) | PASS | All three p-values are printed per cell. Impulse: one-sided and Holm 0.029, two-sided 0.058, CI lower bound 0.000; "no two-sided claim". |
| 0.3 separation | PASS in main; **FAIL in supplement (A1)** | No LRF number beside GATE-M in main. The fresh-fold GATE-M arm has its own table S19 with no LRF column. Sec. V has no gate vocabulary outside V-A. Sec. IV has no LRF. No LRF-vs-CLIP sentence. Echoes: A9. |
| 0.4 theory | PASS | Prop. 1 (CRC) is "the only guarantee". Lemma 1 and Prop. 2 sit in IV-A with the label. The E-pred sentence is R1.8 text. Prop. 3 appears only as Prop. S1 with "Theory reference for Study 1's soft comparators; not used in Study 2". No "we prove". Propositions are referred to by label. Study 2 carries no theory. |
| 0.5 must-not | PASS main (placeholders aside); minor hits in supplement (A11) | |
| 0.6 AI / Declaration | **FAIL until A4 is fixed** | Methods wording ("scripted and agent-run audits (see the Declaration)") is correct, with no "AI" and no "independent". Roles are listed. "not by outside reviewers" is present. |
| 0.7 IEEE | PASS except A7, A12 | Abstract is 247 words in one paragraph with no abbreviations or citations. Exactly 4 index terms, alphabetical. Equations are cited "(n)". TABLE numerals are Roman with the caption above and no final period. Subpanel labels are present. The header carries the journal name only. 15 pages = the SPEC cap (target 13). |
| 0.8 style | partial | Links are blue. See B-W7 for "in this journal" citation tells and [13]. |
| RS-1 ... RS-12 | met in the main text | RS-2 regressed in the supplement (A1). RS-9 is weakened by A3 and A5. |
| V2-1 (no n_d sentence) | PASS | Study 1 Limitations is scope only. n_d appears only in Table I and the protocol's pointer "(counts in Table I)". |
| V2-2 (ablation plan) | not re-checked (out of scope) | Item (d) is pending in Limitations (A16). |
| V2-3 (abstract symbols) | PASS | "probability value 0.0005", "90 percent confidence interval". COCO is spelt out. |
| V2-4 (CLIP/SigLIP gate) | PASS | RS-12 audit cited. Both parity runs are cited in Table V. The stale field is explained. |

### Numbers spot-checked against runs or by derivation (E4)

- Table I: P3 net (1-3)/500 = -0.004. Exact two-sided McNemar for 1 vs 3 is 0.625. Clopper-Pearson upper bounds 0.011
  (n_d = 1), 0.007 (n_d = 0) and 0.020 (n_d = 4) match.
- Table IV: every net equals (b-c)/n, and so does L-LEN with 34/449. LG Holm steps 0.0005, 0.011 and 0.029 follow from
  the one-sided p. L4 Holm 2 × 0.0245 = 0.049 and L3 Holm 0.382 are consistent. L1 (`a6_analysis.json`): acc 0.7333 to
  0.8022, b = 58, c = 27, p_one 0.000508, p_two 0.00102.
- Lemma 1 condition (10): re-derived; the necessary condition ρ1 > 2ρ0 - ρ0², the "random gate lowers" statement and
  Prop. 2(ii) all hold.
- Commits 24d36a8a (re-frozen object) and 941a260b (A6 r1) exist with the stated messages.
- One unexplained arithmetic step (minor): 2,449 eligible + 2,526 excluded = 4,975, not 5,000. S-IV says images without
  instance annotations were not eligible; V-C should say so.

---

## Pass B. Hostile review as a TNNLS area chair

### Summary

The paper studies UniDisc (1.4B), a unified masked discrete diffusion model, as a verifier of image-caption pairs.
Every image token is masked; each caption is shown; the per-token log-likelihood ratio of the observed code under the
true versus a wrong caption is summed. The paper reports two preregistered studies.

- **Study 1.** A conformal-risk-control gate discards the tokens flagged by a caption-free masked-likelihood suspicion
  score. Under JPEG quality 10, Gaussian noise σ = 0.1 and a 128-px splice (n = 500 each), the 90% intervals of the
  accuracy change lie within ±0.05. The gate changed 1, 0 and 4 of 500 decisions. The positive control (random-code
  corruptions) was not met. The score's token detection is near chance on JPEG and noise and below a texture rival.
  A section of SNR theory for withholding is labelled as not validated.
- **Study 2.** A logistic GAM maps 35 caption-masked token features to non-negative weights. It was fitted on Study 1's
  500 test images under the four conditions, then frozen and tested on 450 fresh images. Under σ = 0.1 noise accuracy
  rose from 0.733 to 0.802 (one-sided p = 0.0005). It is non-inferior on clean images (in fact +0.031) and positive
  under splice (Holm p = 0.049) and three other noise types.
- **Reference encoders.** CLIP and SigLIP score 0.996-1.000 on the same items.
- **Exploratory ablation.** Several simpler weightings are not distinguishable from LRF under noise.

### Strengths

1. Unusually rigorous inference for this venue. Exact paired McNemar tests, Holm within families, a printed count of
   17 families, intervals everywhere, and a hash-pinned object scored once on a prefix-fixed fresh fold.
2. Full disclosure of the design history and deviations. A null reported as a bounded null with the exact discordance
   counts. Positive-control failure reported, not buried.
3. The L1 result is statistically solid (p = 0.0005, n_d = 85). It holds with length-matched negatives and replicates
   in direction on three other noise types.
4. A correct, carefully scoped application of conformal risk control. The theory states its assumptions and does not
   overreach.

### Weaknesses, ranked by severity for acceptance

**W1 (decisive): Practical significance.** The verifier under study is weak: 0.887 clean and 0.733 under noise
without weighting. CLIP and SigLIP solve the same task at 0.996-1.000, and the negatives are category-disjoint (A2),
so the task is easy. A gain from 0.733 to 0.802 on an easy task, by a verifier that loses to off-the-shelf encoders by
20 points, will read as an improvement to a strawman. The "Scope of this paper" paragraph says the object is the model's
own evidence, but the paper never shows a setting where that evidence is what one must use (no external encoder
available, or the verifier driving UniDisc's own generation or repair).
- *Fix within rules (text only).* Strengthen Intro paragraph 2 into a concrete statement of why a unified model's
  self-evidence matters: UniDisc's authors select repairs by the model's own likelihood [4]; remasking samplers use the
  model's own confidence [25]-[31]. Say plainly in III-B that the all-image-masked, one-pass evidence was chosen
  because it makes withholding exact and costs one pass per caption, and that it is not UniDisc's strongest
  verification signal. Correct the negative description (A2). Do not argue against CLIP (banned). An exploratory
  downstream demonstration (e.g. LRF-weighted evidence for best-of-N repair selection) would be new Tier-3 work; it is
  allowed only if labelled exploratory and kept out of the abstract and conclusion, and it costs GPU time on a laptop
  with a crash record. I would not start it before submission.

**W2 (major): Generality.** One model, one dataset, one severity. LRF was trained on the tested corruption, so L1
tests new images, not a new corruption. The LG cells are close relatives of Gaussian noise, and the one structurally
different cell (impulse) has a CI starting at 0.000. TNNLS asks for "well-founded and conclusive"; a reviewer will say
the claim is "a supervised reweighting helps on the corruption it was trained on, in one model".
- *Fix within rules.* Already disclosed in Limitations, which is the honest maximum in text. A second backbone or a
  corruption held out of LRF's training would be the decisive addition. Under A6 ("no further confirmatory study") it
  can only be exploratory Tier 3; flag it as future work.

**W3 (major): Method novelty, and what the ablation shows.** LRF is attention-MIL / reliability weighting applied to
per-token LLRs (the closest-precedents sentence says as much). V-G and S-VII report that under noise a linear logit, a
B-and-D-only additive model, an s3-only model and attention-MIL pooling are not distinguishable from LRF. A-LIN lay
*above* LRF under JPEG and A-S-BD above it under impulse (S-VII). The specific GAM design is therefore not shown to
matter; "learned reweighting of this evidence helps under noise" is the supportable reading. In addition, the novelty
statement admits the search "did not reach ... the journal tables of contents of IEEE Xplore". For a TNNLS
submission, that sentence invites a desk comment.
- *Fix.* (a) Run the logged IEEE Xplore and OpenReview search (e-gateway) before submission and update the scope of the
  novelty sentence; that is a literature task, not new data. (b) Limitations sentence per A16. (c) In V-B, describe
  LRF as one instance of learned per-token weighting, without implying that the hinge GAM is essential.

**W4 (major): Two unlinked studies in one paper.** The rules forbid any link, so the reader gets a null study (with
the paper's only theory) followed by an unrelated positive study, and must guess why both are here. Section order,
the shared Fig. 1 and "two questions about this evidence" carry the only connection. Reviewers will ask for a split,
or ask what Study 1 contributes. Study 1's own interpretability is weak:
- the positive control was not met (PS 0.870 vs 0.870 under the patch corruption, with detection AUROC 0.961);
- under JPEG and noise, 96% and 93% of codes change (Table S8), so "discard the corrupted tokens" has almost nothing
  clean to keep;
- the gate changed at most 4 of 500 decisions.

AB.1 forbids using any of these to explain P, and that is right; but a reviewer will use them, and the paper cannot
answer.
- *Fix within rules.* (a) In Sec. I, one sentence on why two measurements of the same evidence are reported together,
  with no causal or motivational link: "both studies measure fixed rules applied to the same per-token evidence; they
  were preregistered separately and are reported separately". (b) Give the changed-code share of each corruption as a
  property of the corruptions in Sec. III-C (from runs/P2-GATE-M4 calibration fields). This is a description of the
  input, with no "so", "because" or "therefore" to any result; it needs a lead or statistician ruling first that it is
  not an account of P. (c) Keep PS non-pass where it is (IV-C3), which is honest. (d) Shorten Study 1's secondary
  material in the main text (S-D2 detail, the S2 paragraph) to free space for W1's motivation.

**W5 (major): The theory is decorative.** Lemma 1 and Prop. 2 are variance algebra for a thinned sum. Assumption (b)
(keep indicators independent of the evidence) is violated by construction, because flags and evidence are computed
from the same observed codes (the text admits it). Neither statement is tested, and both are explicitly "linked to no
result". Prop. 1 is Theorem 1 of CRC with B = 1. A TNNLS theory reviewer will call this about one page of untested
modelling attached to a null.
- *Fix within rules.* Keep the label (binding). Cut the consequence list (i)-(v) to the two consequences used by
  Fig. 2's caption, and move the rest to S-II with the proof. Say in one sentence what the frontier is for: the regime
  map of a withholding rule under stated assumptions. Do not add any link to results.

**W6 (major): Preregistration credibility under review.** The registry is self-hosted. There is no third-party
timestamp. The environment was recorded after the runs, and env-lock files are empty. Arrays are untracked. The audits
were run by the authors' agents. The anonymised mirror cannot show commit order (A3). Two placeholders remain in the
Declaration (A4), and an omission sits in the deviations box (A5). A sceptical reviewer can discount "preregistered"
to "planned in a private repo".
- *Fix.* A3, A4, A5 and A6. Optionally deposit the frozen plans and the hash manifest on Zenodo now, and state its
  date honestly as the deposit date. That adds a third-party timestamp for the record without claiming it predates the
  runs.

**W7 (moderate): Readability and structure against the TNNLS exemplars.**
- *Internal vocabulary in the main text.* About 25 internal labels without a key (GATE-M, GATE-I, S-C, S-D, S-D2,
  S-M, S2, B, PS, R, E-pred, E-dec, Tier-3, L1/L3/L4, L-NI, L-LEN, LG, H-NOGO). Main-text deviations use "card row
  A-8", "row A-9", "SAP A2.3", "Addendum A6 r1". Table V's caption prints run paths and a JSON field
  (`pixel parity:notrun`).
- *Contributions.* Nine contributions run about 0.9 page; the exemplars state three (EXEMPLARS rule 1).
- *Abstract.* Three nested number triples in the abstract read as a table.
- *Deviations box.* An unbroken paragraph.
- *Citation tells.* "In this journal" (twice) and "Papers in this journal take the same view" read as citation
  targeting. [13] (an image super-resolution survey) is cited for "diffusion models are trained by maximising a
  variational lower bound", which it does not primarily support.
- *Fig. 1* draws sparse token damage, while Table S8 shows 93-96% of codes changing under JPEG and noise. The caption
  says "conceptual", but the picture misleads.
- *Fig. 4(a)* panel titles are code names.

Moser et al. set the bar with a clear taxonomy figure, consistent terminology and every abbreviation defined once.
This draft does not meet that bar on terminology.
- *Fix (text and figures).*
  - Add a one-column "families at a glance" table in III-E: label, study, question, status only, with no estimates
    (allowed as a status map).
  - Replace card or row identifiers in the main text with "supplement S-I, item n".
  - Move run paths out of the Table V caption into S-VI. SPEC s5 required citing both parity runs; cite them as
    "the two parity runs (supplement S-VI)".
  - Merge contribution bullets 4 and 5 and bullets 7 and 9 typographically (the substance of A4.2.4 is kept).
  - Typeset the deviations box as a compact two-column list.
  - Drop "in this journal" phrasing; cite [13] only where it fits.
  - Redraw Fig. 1 with dense damage, or put "illustrative; under JPEG and noise most codes change (supplement Table S8)"
    in the caption.
  - Retitle the Fig. 4 panels with Table III group names.

**W8 (minor): Statistics, wording and presentation.**
- The L-NI margin was chosen just below a previously seen interval; this is disclosed, and the claim adds little.
- The headline L1 p = 0.0005 would survive a Bonferroni split over all 17 families (0.05/17 = 0.0029). The paper does
  not say so, and it is the best answer to the multiplicity worry.
- The bootstrap "Holm-adjusted p = 0.0004, the resolution floor" is reported like an exact p.
- The S-C "calibration statistic of -3.59 against the violation bound of 2.13" is undefined in the main text.
- The title is 26 words (binding).
- "Added ... when the target venue changed" (binding A6.13 substance) will read as publication-driven.
- *Fix.* Compute the Bonferroni check into a runs/P2-PAPER-* file and print it once in V-D, labelled "added at writing,
  descriptive". This needs a statistician ruling; it is not a new test. Define Z_cal in one clause. Write "p < 0.001
  (bootstrap resolution)" for the floor.

### Questions to the authors (as AC)

1. Why mask *all* image tokens? A partially masked or multi-step likelihood would use image context. What is UniDisc's
   accuracy on this task with its own best scoring procedure?
2. Under JPEG and noise 93-96% of codes change. In what sense is a per-token "reliability" weight meaningful there, as
   opposed to a global recalibration of the evidence?
3. Does the L1 gain survive on a second unified masked diffusion model, or on a corruption excluded from LRF's
   training?
4. How large is the gain with harder (category-sharing) negatives, where the 0.73-0.89 baseline might matter more?
5. Is the A-LIN / A-S-BD / A-MIL result compatible with any claim that the GAM form matters?
6. Can reviewers verify the commit order behind "preregistered" during double-anonymous review?

### Score

- **Reject and resubmit, 4/10; confidence 4/5.** A reviewer who prizes preregistration might give major revision. A
  method-oriented TNNLS reviewer gives reject on W1-W3.
- **The one experiment whose absence would cause rejection:** a test of the frozen weighting on a second unified
  masked diffusion backbone, or on a corruption held out of its training. Without either, the positive result is "a
  supervised reweighting helps on its training corruption in one model", and reviewers will not call that conclusive.
  Under A6 it can only be exploratory now. The V-G ablation already answers the earlier "simpler rule" request, with
  an outcome that weakens the method claim (W3).

### What would make a reviewer say "accept"

1. A demonstrated use of the self-evidence (W1).
2. A second backbone or a held-out corruption (W2).
3. A crisp three-contribution framing, a glossary or status table, and figures without internal names (W7).
4. A preregistration record a reviewer can verify (A3, W6).

Items 3 and 4 are pure text or build work and should be done before submission. Items 1 and 2 are the difference
between major revision and acceptance.

---

## Cheapest alternative explanations of the positive results (updated with the ablation)

1. **L1:** a generic learned recalibration of the summed evidence. Clean +0.031 and splice +0.031 are positive.
   Simpler weightings (linear, B-and-D-only, attention-MIL) are not distinguishable from LRF under noise (S-VII,
   exploratory).
2. **L1:** a supervised fit to the training corruption (noise σ = 0.1 was a training condition).
3. **L1, LG:** a global noise-level detector inside the image-level features. Under noise 93% of codes change, so a
   per-image statistic can drive the weights. The knockout of the neighbourhood group (-0.062) and the B/D group
   (-0.053) shows dependence, not mechanism.
4. **LG:** shot and speckle are close relatives of Gaussian noise; impulse has CI lower bound 0.000 and two-sided p
   0.058.
5. **L4:** Holm p 0.049; one or two discordant items flip it.
6. **Study 1 NEG** (authors only, never paper text, per V2-1): the gate barely acted.

## What would force rejection of a claim in the manuscript

- Any co-canvas of P with PS, AUROC or H (A1 as built), or any LRF number beside GATE-M or CLIP/SigLIP. The first
  withdraws the A4/A5 signature; the second the A6 signature.
- A scope sentence that misstates the negative population (A2), if it is left uncorrected after this report.
- A reproducibility statement that claims a verifiable commit order the reviewers cannot see (A3).
- A Declaration with placeholders, or one that conflicts with S-I G(3) (A4).

## Ledger

I added no rows. The brief names one output file. A1 is fatal and blocks the gate until the orchestrator records a
resolution in `decisions.jsonl`.

---

# Re-check 2026-10-30 (red team, on HEAD 9268e34b: main.pdf 15 pp, supplement.pdf 17 pp, both built 10:08 IST after the last source edit)

Read: D0096-D0101 in full. The main text was diffed sentence by sentence against the 08:41 build, and every changed
sentence was read. Read in full: abstract, contributions, V-A, V-D, V-G, VI-B, VI-C, VI-D, the Reproducibility
paragraph and the Declaration. Rendered: page 1 and page 4 (Table I). Supplement read: Table S5 (status map), Table
S18, S-VII in full with Table S24, and the S-I audit and G(3) text. Must-not scan re-run on pdftotext of both PDFs.
Git order checked: ablation plan 506818c7 (07:13), then the fits 45f4a717 (08:23), then the scoring facab605 (08:35).
Not re-checked: the DOCX; S-II detail tables S9-S16; last-page column balance (A12); numbers beyond those quoted below.

## Verdict: DO NOT SIGN as built (one fatal, R1). One table change turns it into SIGN WITH CONDITIONS (R2-R6).

A1-A7 are resolved, so the earlier fatal is gone. The new main-text **Table I** repeats the A1 defect in a lighter
form: decision words instead of numbers, but in the main text, and with both studies on one canvas.

## Status of the earlier findings

| # | Status | Evidence |
|---|---|---|
| A1 | **RESOLVED** in the supplement | Table S5 is now a status-only map (status words of A4.2.5 item 6; no estimates). PS, detection and H have their own tables (S9, main III, S17). |
| A2 | RESOLVED | The abstract ("a random caption of an image sharing no annotated object category"), IV-C1, V-C (rule stated in plain words), VI-C and VII all carry the category-disjoint scope (D0097). |
| A3 | RESOLVED | The Reproducibility paragraph no longer claims a hash-preserving mirror. It now says: "available to the reviewers on request through the editor and will be released at camera-ready". Minor: "link withheld for double-anonymous review" is stated twice. |
| A4 | **OPEN, author item (D0101)** | See R5. |
| A5 | RESOLVED | Deviations item (1) now carries the r2/r3 clause. |
| A6 | RESOLVED | Table S18 prints n_d, the 90% CI, the Clopper-Pearson CI of b/n_d and mid-p. V-D points to it. |
| A7 | RESOLVED | Q1/Q2 are run-in paragraphs; page 1 renders cleanly. |
| A8 | unchanged, not a violation | D0094 clause in V-A. |
| A9 | PARTLY | Fig. 4 panel titles are now plain names. Table IV still writes q_j = B_j - D_j, the Study 1 symbol. V-G uses the undefined code names tbv, ltex, nbr, s3 and rad (see R6). |
| A10, A12, A15 | not re-checked / unchanged | minor |
| A11 | RESOLVED | "predict no ranking" and "A code reading confirmed" are gone. |
| A13 | RESOLVED | Timestamps in UTC. "One laptop GPU (12 GB)" in Table S14 is a hardware fact; acceptable. |
| A14 | RESOLVED | Deviations item (9): detection-stage and main-test env-lock files. |
| A16 / V2-2(d) | RESOLVED | VI-C names the four simpler weightings not distinguishable from LRF under noise. The "does not show zero" sentence now sits only in S-VII's interval-definition paragraph. |

## New findings

| # | Sev. | Location | Finding | Rule | Fix |
|---|---|---|---|---|---|
| R1 | **fatal** | Main **Table I** "Preregistered Families at a Glance (Decision Words Only)", Sec. III-E (p.4). Text: "Table I lists the families with their preregistered decisions only" (III-E); "with its status" (IV-B). | (a) The **Decision** column holds results, not statuses. P reads "bounded null", directly beside PS "not rejected" (the failed positive control), S-D "rejected (Holm)" (the rival result) and H "not run". That is PS and the detection rival on the P canvas, and H on a results canvas beside P and PS. (b) The same table has a Study 2 block (L1 "confirmed", L4 and LG "rejected (Holm)") under the Study 1 block, in the shared Setting section before either study. A reader sees "Study 1: bounded null; Study 2: confirmed" on one canvas, which is the arc that F1/F2 were about. D0096 allowed "decision words". A lead row cannot loosen A4.2.5 (item 3: "any label"; item 6: "status only") or A5.9 (placement 5: "tightened, never loosened"). My W7 fix asked for status only; the decision column goes beyond it. | A4.2.5 items 3, 4, 6; A5.9 placement 3; C6-4 / A6.12 placement 2 (no canvas arranges the studies as problem and solution) | Replace the Decision column with the status words of Table S5 ("run, formal"; "not run (gatekept: P+ empty)"; "run; headroom not met (H-NOGO)"; for Study 2, "run, formal" per family), and make III-E and IV-B consistent ("status"). Alternatively, split into two status tables, one in each study's section. Amend D0096 by a dated row. With status words only, the table is the allowed status map and the two blocks carry no outcome. |
| R2 | major | V-D, D0099 sentence: "None of the three other noise types ... was a training condition of the frozen weighting ... On these types (n = 300 each), each LG hypothesis was rejected with b > c." | Read in sequence, this is the held-out-family framing that A6.5/C6-11 bans, without the words. The C6-11 caveat (shot and speckle are close relatives of Gaussian noise; severity 3 is not matched to σ = 0.1) is a page earlier, in V-C. | A6.5 and C6-11 wording; A6.12 must-not ("held-out noise family", "generalises" without a test) | Keep D0099's sentence, but follow it in the same paragraph with the C6-11 clause ("shot and speckle noise are close relatives of Gaussian noise, impulse noise is the structurally different cell, and severity 3 is not matched to σ = 0.1") before the LG results. |
| R3 | minor | IV-C9 (Study 1 Tier 3): "Under JPEG and splice the median and 20% trimmed-mean combiners scored below the hard gate; under noise they scored 0.678 and 0.682 against 0.676 ..., and the data do not show a difference" | The A4.1.10/r3 sentences must carry the net, its 95% CI and the exact discordant-split interval ("below GM"), or n_d and B/MDD ("not distinguishable"), beside the claim. These sit only in Table S15. | A4.1.10 r3 items 3 and 5 | Add the nets with their exact intervals, n_d and B in the text, or move the two sentences to S-II and keep only the trimmed-mean sentence, which already carries its bounds. |
| R4 | minor | Supplement Table S5, E-pred row: "out-of-sample sign prediction"; B row: "hard-negative foil pairs" | "prediction" appears outside the E-pred table (R1.7 item 3). "Hard-negative" for FOIL pairs invites confusion with family H, whose name is "hard negatives". | THEORY R1.7 item 3; A5.9 clarity | "out-of-sample sign agreement"; "one-word foil pairs". |
| R5 | **open author item (D0101); blocks submission, not the build** | Declaration: "The authors used Claude (Anthropic) to improve the language and grammar of the manuscript." | Body sentences this makes inaccurate (each points the reader to a Declaration that no longer contains what it promises, or contradicts it): (1) III-E "verified by scripted and agent-run audits (see the Declaration)"; (2) IV-C3 "The plan's audit (scripted and agent-run, see the Declaration)"; (3) V-C "passed scripted and agent-run audits (see the Declaration)"; (4) VI-C "the audits were agent-run (see the Declaration)"; (5) supplement S-I B, the list of the statistician's, red team's, gate-auditor's and data-steward's checks "(see the Declaration of the main paper)"; (6) supplement S-I G(3): the outcome-book reading "was adopted by the agent-run study pipeline (see the Declaration)", which contradicts "language and grammar" outright; (7) S-VII: "The plan ... was written and checked by the statistician", a role now undisclosed. Beyond the dangling references, the project record (agent-written code, analysis scripts, figures, drafts, agent-run audits and a delegated decision) is wider than "language and grammar". Submitting with the interim text would misstate AI use relative to the paper's own supplement. | SPEC rule 6 (F17); IEEE AI policy (checklist s7) | Author decision with the supervisor (D0101). Until then: do not submit. When the text is final, either restore the role-by-role content (draft kept in drafts/declaration-full-disclosure-draft.tex), or rewrite sentences (1)-(7) so that none relies on the Declaration. The second route would still leave (6) describing an agent-made decision, which must be disclosed somewhere. |
| R6 | minor | V-G | V-G uses code names (tbv, ltex, nbr, s3, "feature rad") that the main text never defines; Table IV defines the features by formula only. "tbv" echoes Study 1's "TbV score". | A9 / F29 spirit; clarity | Use the Table IV descriptions ("the one-pass observed-position score", "patch texture", "codebook-neighbour distance", "confidence of the B pass", "radial position"), or add a name column to Table IV. |

## V-G / S-VII compliance (V2-2 and SPEC s6)

| Condition | Status |
|---|---|
| (a) Variants and quantities fixed before any fresh scoring | **PASS.** The plan (506818c7, 07:13) precedes the fits (45f4a717, 08:23) and the score (facab605, 08:35). S-VII discloses what the plan author had seen, including that the direction of A-UNL was fixed after seeing the shape functions. |
| (b) No Study 1 object | **PASS.** No GATE-M, conformal-risk-control or masked-likelihood hard gate, no A4 Tier-3 comparator, no hard-versus-soft framing. A-S-BD uses B and D, which are defined in shared Sec. III. A-UNL ranks s3, not u_j. |
| (c) Fit and selection on design items only | PASS (stated; the A-SF selection "used no fresh item"). |
| (d) Every variant reported; covering intervals stated in V-G and Limitations; no rescue sentence | **PASS** (A16 resolved). |
| (e) Kept out of title, abstract, conclusion and contributions | **PASS.** In the Discussion it appears only in alternative reading (3). |
| SPEC s6: no p-value; no variant called better or worse in a claim; label; deviations entry | **PASS.** "Exploratory; added after the primary, family H and Study 2 results"; "not a test"; intervals only; dependence and multiplicity caveat (336 intervals). The deviations box has item (9) in main and item 12 in S-I. |
| C6-8 (no design-item accuracy of the frozen LRF as performance) | PASS on Table S24 and the S-VII text. Tables S25-S27 were not read in full. |

## Must-not rescan (HEAD 9268e34b)

- **Main.** No true violation.
  - Changed counts are explained by the new text.
  - The only new hits: "improve" in the Declaration, which describes language editing and is not a claim; "improves" in
    the Petryk et al. title [47]; "confirmed" only for L1 and in Table I's L1 row (see R1).
  - "AI" appears only in the Declaration.
  - "independent" is never used for an audit.
  - "first", "calibrat-", "guarantee", "validated", "generalised" and "robust": same benign classes as before.
  - Zero hits: "held-out" as a claim (the only hits are "held-out clean test pairs" and "held-out labelled data" [8]),
    "explains", "predicts" (as a theory word), "outperform", "better than", "competitive", "equivalent", "screening",
    "novel", "we prove".
- **Supplement.** One minor true hit, R4 ("prediction" in the status map). "superiority" appears twice, both negated
  (Table S3, Table S18 note). "independent" is used in mathematics and in "none is described as independent". "confirm-"
  appears only in "confirmed" for L1, "confirmatory family" (A5.14) and the first author's "dated confirmation".
- **DOCX.** Not scanned.

## Hostile AC score after revision: still reject and resubmit, 4/10, confidence 4/5

What improved:
- Presentation: page 1, four contributions, category-disjoint scope stated, A6.4 table.
- Honesty: the corrected search scope, Petryk et al. as the closest precedent, and the ablation reported in full.

What did not improve:
- W1 (practical significance) and W2 (one model, trained on the tested corruption).

What got sharper:
- W3 (novelty). Petryk et al. already learn an aggregation of token-level confidences to judge caption correctness. The
  ablation shows a linear logit, B-and-D-only features and attention-MIL pooling are not distinguishable from LRF under
  noise, and A-LIN and A-S-BD lie above it in one cell each. The supportable claim is "a learned reweighting of this
  evidence helps under noise", not this GAM.

Two items would cost points at a TNNLS desk:
- R1 (a two-study outcome table on page 4).
- R5, if it is submitted as is: a Declaration contradicted by its own supplement is an ethics flag, not a style point.

The one experiment whose absence causes rejection is unchanged: a second backbone, or a corruption held out of LRF's
training. It can only be exploratory.

## Conditions for signature

**R1 (must, before any signature).** After R1, SIGN WITH CONDITIONS:
- R2 before submission;
- R3, R4 and R6 at the next edit pass;
- R5 resolved by the authors before submission (recorded as an open author item, D0101).

## Ledger

No rows added. R1 is fatal and blocks the gate until the orchestrator records a resolution (amend D0096).
