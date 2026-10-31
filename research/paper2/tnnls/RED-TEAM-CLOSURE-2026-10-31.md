```yaml
agent: red-team
date: 2026-10-31
brief: closure check of the single-study Paper 2 (TNNLS review build) against the binding wording rules, abstract, sweep/Dempster hedging, anonymity
sources_examined:
  - paper2-tnnls/main.pdf (11 pp, pdftotext, read in full except reference list entries 41-68)
  - paper2-tnnls/supplement/supplement.pdf (pdftotext, S-I and the source list; not every table)
  - paper2-tnnls/sections/{abstract,study2,setting,discussion}.tex (line refs below)
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md (A6.6, A6.7, A6.12, A6.13, C6-4, C6-5)
  - research/paper2/tnnls/{SINGLE-STUDY-REWRITE,PROFESSOR-SUGGESTIONS-ANALYSIS}-2026-10-31.md
  - paper2-tnnls/SUBMISSION-PACKAGE/{01,02,03 PDFs, source/cover_letter.tex, optional/04_Anonymized_code_and_data.zip}
coverage: >
  Arithmetic of Table I and the discordant counts re-derived by hand (net, Holm, Fig. 4 counts, Table III differences);
  PDF text and PDF metadata scanned for author, institution, repository and DOI strings (main.pdf and supplement.pdf clean);
  the anonymised-code zip scanned for the same strings. NOT covered: figures as images, main_camera.pdf, the Word files,
  the claims of references 25, 33, 40 (not re-verified), any rerun of code or numbers from runs/.
claims:
  - statement: The single-study paper breaks no verbatim A6.12 must-not (no LRF-GATE-M link, no CLIP/SigLIP comparison word, no "robust/generalises/first/state of the art", no "held-out noise family", no pooling)
    status: supported
    evidence: pdftotext keyword scan of main.pdf; Table II has no LRF column; Section IV-E says "no test and no comparison"
    level: E4
    confidence: 0.85
  - statement: The disclosure of the earlier (null) study is adequate and honest
    status: contradicted
    evidence: study2.tex:21; discussion.tex:77; A6.13 substance list
    level: E4
    confidence: 0.8
  - statement: The number-free abstract does not overstate
    status: mixed
    evidence: abstract.tex:13-25 against study2.tex:319 and discussion.tex limitations
    level: E4
    confidence: 0.75
  - statement: The sweep and Dempster sentences are correctly hedged
    status: supported
    evidence: IV-H heading "Exploratory; no test", "same 450 images", "unadjusted 95% interval", "specified and scored after the preregistered results" in the Table III note
    level: E4
    confidence: 0.8
  - statement: The review-build main.pdf and supplement.pdf leak no identity
    status: supported
    evidence: byte scan for Shlok, Goenka, Khekare, Vellore, vit.ac, github, zenodo = 0 hits in both; PDF Author = "Anonymous authors" (main) / empty (supplement)
    level: E4
    confidence: 0.9
competing_explanations: []
unknowns:
  - whether a companion manuscript for the earlier study exists, is under review, or is merely planned
  - whether the stale package files will be uploaded
next_test: {hypothesis: the omission of the earlier study's negative primary result is read by an AC as selective reporting, intervention: state the result in one sentence in IV-A, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Red-team closure, Paper 2 (TNNLS), single-study version

## Verdict: SIGN WITH CONDITIONS (confidence 0.75). No fatal finding. Two majors in the paper text (R1, R2), one major package-level risk (R3), minors R4-R9.

Hostile-AC score: **5/10 (borderline, major revision), confidence 3/5**, up from 4/10. Reasons: one question, one hash-pinned object, p = 0.0005 that survives even a x17 multiplicity; but the task is solved at 0.996-1.000 by a CLIP/SigLIP pass, a linear logit and a pixel denoiser match or beat the confirmed object, the gain is not shown to be noise-specific (clean-image gain 0.031; excess over clean at sigma 0.1 is 0.038, interval -0.004 to 0.080), "preregistered" is self-hosted git, and the earlier null study is now invisible.

## Answers to (a)-(d)

**(a) Binding wording and disclosure.**
- A6.12 must-nots: pass. Checked "confirmed" (only L1; L-LEN gate satisfied; L-NI worded as non-inferior), "calibrated"/"guarantee" (only about conformal literature and "carries no such guarantee"), LG wording (C6-11 wording used, "no claim ... corruption types not tested"), no pooling, harm sentence present in IV-D ("No tested condition showed a reduction"). Table II holds no LRF numbers (A6.6 respected); no merged LRF-vs-CLIP table.
- C6-4 and C6-5: pass. No Study 1 result is a motivation; p = 0.0005 is under 0.025; the title carries no gain claim.
- **Not adequate on A6.13 and on honesty of the null (R1, R2).**

**(b) Abstract and title.** Every sentence is true. Overstatement is by omission (R4, R5). The title does not state a gain, so the p <= 0.025 rule is satisfied trivially.

**(c) Sweep and Dempster.** Correctly hedged. The abstract sentence is the weak point, not the body (R4).

**(d) Desk-rejection and anonymity.** main.pdf and supplement.pdf are clean (R6 minors only). The submission package is not (R3).

## Findings

| # | Sev | Where | Finding | Why it matters |
|---|---|---|---|---|
| R1 | major | `sections/study2.tex:21-33`; `sections/discussion.tex:77` | A6.13 makes its substance binding: "added after Study 1 had been analysed (primary result negative), when the target venue changed", "designed post hoc on Study 1's 500 test items", and the cross-reference that Study 2 does not bear on Study 1. The paper says only "an earlier preregistered study ... tested a different question and is reported separately" and that the analysts "had seen the results of that study's analyses, which are not reported here". The negative primary result is never stated. Deviation (10) declares a departure from A6.12 (abstract placement) only; the departure from A6.13 substance is not declared. "Reported separately" has no citation, no preprint, no anonymised pointer (the analysis file promised "anonymised citation"), and no evidence a companion exists. | A reviewer is told the design images carry an unreported analysis whose results the authors saw, and is not told the result was null. That reads as concealment of the first headline attempt, and the "tested a different question" gloss makes it worse. The preregistration the paper leans on is the thing that required the sentence. |
| R2 | major | `sections/setting.tex:82` ("four preregistered families ... 0.19"); supplement S-I "Families" | The family count was cut from 17 (A6.7: 0.58 under a global null) to 4 (0.19). True for "this paper", but the program that produced the object had 13 further families and an earlier failed headline; C6-5 itself gave "second headline attempt" as the reason for the 0.025 threshold and that reason is no longer printed. The 0.19 figure therefore understates the selection the reader should price. | Substantively harmless (0.0005 x 17 = 0.0085 < 0.05, so the confirmation survives full program-level adjustment), but the paper does not say so; an AC will do the 17-family arithmetic from the supplement's own "Addenda A2 to A6" and "Row A-8" remnants (R7) and conclude the reduction was convenient. |
| R3 | major (package) | `paper2-tnnls/SUBMISSION-PACKAGE/01_Manuscript_anonymous.pdf`, `02_Supplementary_Material_anonymous.pdf`, `03_Cover_Letter.pdf`, `optional/04_Anonymized_code_and_data.zip`, `optional/*.docx` | These files are stale two-study versions (01 is 15 pp with the branch-A long title; 02 is 21 pp; the cover letter PDF is dated 20:40 on 30 Oct and predates the rewritten .tex). The zip (34 MB, built 01:20 on 31 Oct) carries the entire gate study: `research/paper2/prereg/PREREG-GATE-*.md`, `runs/P2-GATE-*`, `exp_p2/gate/*`, and `paper2-tnnls/sections/declaration.tex` with a reserved Zenodo DOI (10.5281/zenodo.23810711) and a github path; Windows user-path strings (`c:\users...downloads`) are in about 30 files. | If uploaded, the code zip shows reviewers the null study the single-study text declines to report (contradicting "reported separately" in a way that looks like a cover-up), a DOI that resolves to an identifiable record, and local paths. Uploading 01/02 would submit the wrong paper. |
| R4 | major (wording) | `sections/abstract.tex:23` against `sections/study2.tex:319` | "An exploratory sweep ... found the gain at milder and stronger Gaussian noise as well" is true, but the paper's own next sentence says the gain at the fitted level is not distinguishable from the clean-image gain (excess 0.038, interval -0.004 to 0.080) and noise-specific excess is clear only at sigma 0.3. The abstract keeps the "damage" framing (abstract.tex:8, title "Reliability-Aware") and never says the weighting was trained on the tested corruption (Gaussian noise 0.1 is a training condition, IV-B). | A reader takes "gain under damage at several levels" as damage-specific robustness. The data say a general +3 to +7 point improvement over the plain sum, including clean images. A6.12 must-not on overclaim is not literally broken, but the abstract omits the two sentences that bound the claim and sit in Limitations. |
| R5 | major (title/claim) | `main.tex:82` title | "Reliability-Aware" and "in Unified Discrete Diffusion". The paper says "reliability-aware" is a name for the design, not a measured property, and that the weights are not shown to track reliability. The scope in the title is a model class, the evidence is one model (UniDisc); A6.12 branch titles and scope {S} said "a unified masked diffusion model ... in UniDisc". Deviation (11) says "claim unchanged"; the scope has widened. | Title asserts a mechanism and a class that the body disclaims. Fixed by wording only, but a hostile AC quotes the mismatch. |
| R6 | minor | `sections/discussion.tex:71` | "quoted to the first author" in a double-anonymous main text (harmless but odd). Section III-D: "every SugarCrepe image that the project had prepared" names a benchmark whose role is never explained in this paper, which invites the question of what hard-negative work was run. | Small anonymity and transparency leakage. |
| R7 | minor | `supplement/supplement.tex:89` ("Addenda A2 to A6"), `:123` ("Row A-8 ... pin 1871fe7d"), "gate-auditor", "fold builder read every image set of the project" | Remnants of the removed study: addenda A2-A5 and amendment rows A-1 to A-7 are undefined in this document. | Points a reviewer straight at the hidden material. |
| R8 | minor | Table III row "Dempster combination [37]"; `sections/study2.tex` IV-H | The row is the authors' own construction (opinions from max(j,0), Dirichlet prior 2, discounted by the rank weight), cited to Han et al. The note admits it is not an evidential head. Sentence "had lower accuracy than no weighting in every condition" is correct (0.722/0.838/0.889/0.884 against 0.733/0.849/0.896/0.887) and hedged, but the label lends [37] an outcome it did not produce. | Straw-man attribution risk for the professor's evidential papers. |
| R9 | minor | abstract.tex:15-18 | Abstract names L1 and L-NI only; L3 (JPEG, not detected) and L4 (splice, Holm 0.049) are in Results. The abstract's "one level" and "other corruptions" disclaimers cover this, but the preregistered null on JPEG is not named. | Selective-emphasis argument; mild. |

## Preregistration strength (carried, not new)
"Preregistered" in the abstract is git history with first push on 30 Oct after the tests; the definition is in III-E, not in the abstract. Commit dates are author-controlled. This is disclosed and is a known weakness, not a new defect.

## What result would force rejection of the claim
(i) A re-score of the pinned model.npz on the same 450 items that differs from Table I by more than the 98.6-98.9% tokenisation agreement can explain; (ii) the paper's own L1 b/c (58/27) failing a byte-identical regeneration; (iii) evidence that the 450 fold images or captions overlap the 500 design images (the eight-check leak test passed, with an injected-leak positive control). None observed here; I did not rerun them.

## Conditions to SIGN (each is wording or file hygiene; no new run)

1. **R1.** `sections/study2.tex:21-22`: replace the sentence "...tested a different question and is reported separately." with: "...tested a different question; its primary preregistered result was negative, and it is not reported in this paper." and add that "the design of the method followed that analysis, on those images". Remove "is reported separately" unless an anonymised preprint or manuscript exists and is cited; if one exists, cite it as an anonymised reference. Extend deviation (10) (`discussion.tex:77`, `supplement.tex:182`) with "and departs from the A6.13 disclosure, which named the negative primary result; the sentence is restored in IV-A".
2. **R2.** `sections/setting.tex:82` and supplement S-I "Families": after the 0.19 sentence add: "The design images came from a study with further families; even a Bonferroni factor of 17 on the L1 one-sided p of 0.0005 leaves 0.0085." (p to be read from `runs/P2-LRF-L1/a6_analysis.json`, not retyped.)
3. **R3.** Before any upload: rebuild 01, 02, 03 from the current .tex, delete or rebuild `optional/04_Anonymized_code_and_data.zip` without `PREREG-GATE-*`, `runs/P2-GATE-*`, `exp_p2/gate`, `declaration.tex` Zenodo DOI and local paths (or withhold the zip), and re-scan with the same string list.
4. **R4.** `sections/abstract.tex:23`: append "; the gain at the fitted level was not distinguishable from the gain on clean images" and add to line 13-14 "including the Gaussian noise level of the test" so the training overlap is in the abstract.
5. **R5.** Title (`main.tex:82` and the supplement title line): add "in UniDisc" or "a" before the model class (scope), or add "learned" before "weighting" in the first sentence of the abstract and the sentence "The name describes the design, not a measured property" into the abstract's last sentence (the last sentence already says the weights are not shown to track reliability, so this is the lighter of the two).
6. Minors R6-R9 before camera-ready, not blocking: `discussion.tex:71`, `study2.tex` III-D SugarCrepe clause, `supplement.tex:89,123`, the Table III label for the Dempster row.

Conditions 1, 3 and 4 are the ones I would not sign without.

## Not judged
The Acknowledgment AI wording (author-owned, per brief).
