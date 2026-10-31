# Number and wording audit 6, Paper 2 (IEEE TNNLS), 2026-10-31

Agent: gate-auditor. Scope: `git diff 1af8c1d4..HEAD` over `paper2-tnnls/sections`, `supplement/supplement.tex`, `tables`, `SUBMISSION-PACKAGE/source/cover_letter.tex` (HEAD a177ef01), plus `pdftotext` of `paper2-tnnls/main.pdf` (13 pp, built 15:06:30) and `supplement/supplement.pdf` (11 pp). Nothing in the manuscript was edited.
Evidence level of every check below: E4 (recomputed here from the run files).

## Verdict: PASS WITH FIXES

All numbers of the Flickr30K test are correct and sourced; the table regenerates byte-identically. Four findings (M1 to M4) must be fixed before release: one undisclosed deviation, one A7.5 must-not, one digit in the abstract, and a stale submission package. Fixes are wording or rebuild only; no number changes.

## 1. Numbers (criterion 1): met

Regenerated `tables/tab_f30k.tex` with `scripts/tab_f30k.py` in a scratch copy (`...\scratchpad\copy\`): `diff` against the committed table is empty (IDENTICAL).

Every value in the text, table, abstract-free sections, conclusion, supplement was checked against `runs/P2-LRF-F30K/f30k_analysis.json`:

| Text value | Run value | Result |
|---|---|---|
| F1 0.693 to 0.792, net 0.100, [0.072, 0.128], b 128, c 41, p 6.4e-12 | 0.69266, 0.79243, 0.09977 (= 87/872), [0.07225, 0.12844], 128, 41, 6.4406e-12 | match |
| F-LEN 0.683 to 0.771, net 0.087, [0.058, 0.116], b 125, c 49, p 3.8e-9, 0 excluded | 0.68349, 0.77064, 0.08716, [0.05849, 0.11583], 125, 49, 3.7937e-9, 0 | match |
| F-NI 0.841, 0.868, net 0.028, 90% [0.009, 0.046], b 60, c 36, margin -0.03 | 0.84060, 0.86812, 0.02752, [0.00917, 0.04587], 60, 36, -0.03, lower90 0.00917 > margin | match |
| clean gain 0.028 vs noise gain 0.100 | 0.0275, 0.0998, `descriptive_only` true | match |
| 1000 images, 128 excluded, a/b/c = 0, 872 kept, floor 800, exact length match 872 | `builder_report.json`, `f30k_analysis.json` | match |
| Hamming threshold 4, smallest kept distance 6 | `leak_check.json` F2 detail | match |
| HF revision 2b239bef..., predictions SHA-256 82f0a248... | `builder_report.json` dataset.revision; `f30k_analysis.json` inputs | match |
| push 2026-10-31T06:06:10Z before first data file 06:08:31Z | `runs/P2-PROVENANCE/a7_push_vs_data.json` | match (see m4) |
| 4 + 3 = 7 families; 1 - 0.95^7 = 0.3017 -> 0.30; 1 - 0.95^4 = 0.1855 | recomputed | correct |
| 17 + 3 = 20; 0.05/20 = 0.0025; L1 p 0.000508 and F1 p 6.4e-12 below it | SAP A6.7 line 226 (17); `a6_analysis.json` family_L.L1.p_one | correct (but see M2) |

Changed non-F30K numbers in the diff (severity sweep 0.056, 0.058, 0.084, 0.031, 0.053, 0.038 and the figure `fig_severity.json`) also equal `sev_analysis.json`. Rounding is the usual: net is computed from unrounded accuracies (F1 0.792 - 0.693 prints 0.099 against net 0.100; F-LEN 0.088 against 0.087; F-NI 0.027 against 0.028); see m6.

`% run:` coverage: every number carries one, except the A7.4 facts listed in m3.

## 2. Abstract (criterion 2): partly

- 249 words by whitespace (limit 250); 258 if hyphenated words are split. No margin: a fix must not add words.
- Digits: the only digits are the "30" of "Flickr30K" (M3).
- Claims against A7.5 (confirmed branch): confirmed (F1, F-LEN), non-inferior (F-NI, both datasets, margin caveat kept), length-matched, "one model, two datasets, and one tested noise level": all match. No numbers, no abbreviations other than UniDisc.

## 3. Must-nots A6.12 and A7.5 (criterion 3): partly

- "robust", "state of the art", "generalises/generalizes": absent from the body of both PDFs (hits are reference titles and "generalised additive model"). "first": only "first caption", "first author", "first pushed", "first item"; no priority claim.
- No LRF-vs-CLIP/SigLIP comparison was added. One ambiguity created by the insertion: m1.
- Link to the earlier gate study in a sentence about this test: found in `setting.tex:87-88` (M2). The F30K subsection itself, the discussion, abstract, intro, conclusion and supplement are clean.
- Clean-vs-noise gain difference: F30K statements are descriptive ("Descriptively ... no test of that difference was preregistered", `study2.tex` F30K subsection; `discussion.tex` limitations). The abstract sentence "at the tested level it did not clearly exceed the clean-image gain" concerns the exploratory COCO sweep (`sev_analysis.json` levels.0.1.gain_minus_clean_gain 0.038 [-0.004, 0.080]) and is accurate; no change needed.

## 4. Multiplicity (criterion 4): arithmetic correct, one wording defect

Arithmetic and sources are right (table in section 1). The defect is M2.

## 5. PDF text (criterion 5): met except leftovers below

`pdftotext` of main.pdf and supplement.pdf: no author names (Goenka, Vairavasundaram, Balaji), no institution (VIT, Vellore, SCSE), no GitHub owner (shlokDS16, github.com/...), no Zenodo DOI (only "archived on Zenodo at acceptance under a reserved DOI"). PDF metadata: Author "Anonymous authors for double-anonymous review". No "??" in either file. No "one dataset" as a claim ("This test adds one dataset" is correct). Leftover inconsistent statements: M1 and m2.

## Findings (file:line, exact replacement)

### M1 (major): undisclosed deviation from the A6 rule "no further confirmatory study"
`paper2-tnnls/sections/study2.tex:33` says the A6 addendum carried "a rule that no further confirmatory study would be added" (substance of SAP A6.13 and A5.1 stop rule, A6.13 line 320). Addendum A7 adds a further confirmatory test; A7.1 says only that it "changes nothing in Addendum A6". The paper now contradicts itself and lists no deviation.
Replace the sentence at `study2.tex:33` with:
`The test was preregistered (a dated addendum to the analysis plan, commit \texttt{941a260b}) with a rule that no further confirmatory study would be added; on 31 October 2026, after this test had been run, that rule was set aside for one further preregistered test of the same frozen weighting on a second dataset (\cref{sec:study2-f30k}; deviation~(14) in \cref{sec:deviations}).`
Add after `discussion.tex:89` (end of item 13) with a `% run:` of SAP A7.1 and commit 76b85e44:
`(14) 2026-10-31: addendum A6 had stated that no further confirmatory study would be added; addendum A7 (commit \texttt{76b85e44}), written after the COCO results were known, added one confirmatory test of the same frozen object on Flickr30K, in answer to a supervisor's comment and an internal review. Addendum A6 and its results were not changed.`
Add the same as a new `\item` after `supplement.tex:206`. Check the page cap (13 of 15 now).

### M2 (major): A7.5 must-not ("no link to the earlier gate study in any sentence about this test"); ambiguous count
`paper2-tnnls/sections/setting.tex:87-88` ("Counting also the families of the earlier study (17 in all, and 20 with the three on Flickr30K) ... F1"). The sentence names the earlier study and the F1 p-value together. "17 in all" also reads as 17 families of the earlier study; per SAP A6.7 line 226 the 17 are the whole-project count, of which 4 are this paper's COCO families (13 belong to the earlier study).
Preferred replacement (removes the link; arithmetic checked, 0.05/7 = 0.00714):
`Counted as one correction over the seven families, the Bonferroni level for a one-sided test at 0.05 is $0.05/7=0.0071$, and both primary one-sided $p$-values lie below it ($p=0.0005$ for L1 and $p=6.4\times10^{-12}$ for F1).`
and change the `% run:` comment at `setting.tex:~86` to `0.05/7 = 0.007143`.
If the 20-family wording is wanted (red-team closure R2), it can stay only with an explicit waiver of A7.5 by the user in the decision ledger; I cannot waive it. Then write: `Counting also the 13 families of the earlier study (17 with the four COCO families, 20 with the three on Flickr30K), ...` and cite A6.7 minus 4 in the `% run:` line.

### M3 (major, small): digits in the abstract
`paper2-tnnls/sections/abstract.tex:18` contains "Flickr30K". Replace "on Flickr30K test images," with "on a second dataset," (A7.5 wording, same word count, 249). The dataset is named in the body.

### M4 (major for release, outside the diff): stale submission package and uncommitted bibliography
- `SUBMISSION-PACKAGE/SUBMIT-HERE.md:39-52` still holds the old abstract ("one dataset", "A preregistered one-sided exact paired test on fresh ... one level") and line 90 "one dataset, one confirmed noise severity". The abstract to paste must be `sections/abstract.tex` after M3.
- `SUBMISSION-PACKAGE/01_Manuscript_anonymous.pdf`, `02_Supplementary_Material_anonymous.pdf`, `03_Cover_Letter.pdf` (11:44) differ from `main.pdf`, `supplement.pdf`, `source/cover_letter.pdf` (15:04 to 15:06); 01 and 03 have no Flickr30K text. The Word files in `optional/` and `at-acceptance/` and the zip `optional/04_Anonymized_code_and_data.zip` (has no F30K run) are stale as well. Run `scripts/rebuild_package.sh` after M1 to M3.
- `git status`: `paper2-tnnls/references-ieee.bib` is modified and uncommitted; it holds `young2014flickr30k` and `karpathy2015deep`, so HEAD's sections cite keys missing from the committed bib. Commit it with the fixes.
- `runs/P2-PROVENANCE/a7_push_vs_data.json` contains the GitHub login, avatar and profile URLs of the author (actor object). Its siblings `first_push.json` and `github_activity_first.json` are anonymized in the existing zip; the builder must do the same for this file (or leave it out), then rerun the identifier scan.

### Minor
- m1. `study2.tex:303-304` (Reference Encoders, first sentence): "on the same items in every condition" now follows the Flickr30K subsection and can be read as Flickr30K items, i.e. an encoder comparison on the new test (A6.6/A7.5). Replace "on the\nsame items in every condition" with "on the same 450 COCO fold items in every condition".
- m2. `study2.tex:374`: "the preregistered result remains the L1 test of \cref{tab:study2}" is incomplete. Replace with "the preregistered results remain the L1 test of \cref{tab:study2} and the F1 test of \cref{tab:f30k}."
- m3. `study2.tex:261-269` (A7.4 facts: three families, F1 gain-claim level 0.025, F-NI margin -0.03 and 90% bootstrap bound) have no `% run:` line. Add before line 262: `% run: research/paper2/prereg/SAP-ADDENDUM-A7-F30K-2026-10-31.md A7.4; runs/P2-LRF-F30K/f30k_analysis.json:F1.headline_alpha (= 0.025), F_NI.margin (= -0.03)`.
- m4. `study2.tex:262-264` and `setting.tex:98` say the plan "fixed the data, the items, and the tests" and that "this test therefore has a third-party timestamp". Two limits: (i) amendment A7.2(d) (c79d3ed3, 12:14 IST) fixed the final item set after the data had been downloaded and the dry run counted 128 over-length captions, though before scoring (GPU run started 12:28 IST); (ii) the push log covers commit 76b85e44 only (06:06:10Z), not the amendment or the scored predictions; "before download" rests on local file modification times (README 06:08:31Z, 141 s after the push). Suggested edit of `study2.tex:262`: "fixed the data, the item rule (before amendment (d)), and the tests", and of `setting.tex:98`: "so unlike the earlier tests its original plan, before amendment (d), has a third-party timestamp."
- m5. `SUBMISSION-PACKAGE/source/cover_letter.tex:29`: "on Common Objects in Context image-caption pairs" is now one-sided. Replace with "on Common Objects in Context and Flickr30K image-caption pairs" (cover letter is not part of the blinded review text; check the one-page limit).
- m6. Optional table note in `study2.tex` (caption `tab:f30k`): add "Net is computed from unrounded accuracies." to pre-empt the 0.001 differences listed above.
- m7. Licence statement (`supplement.tex:~140`, dataset card has no licence field; homepage terms) rests on a WebFetch summary recorded in `builder_report.json` (E1, not a primary reading). Verify the Illinois DenotationGraph page by hand before submission, as the writer report already says.
- m8. Reference entries `young2014flickr30k` (TACL 2, 67-78, doi 10.1162/tacl_a_00166) and `karpathy2015deep` (CVPR 2015, 3128-3137, doi 10.1109/CVPR.2015.7298932) were not fetched in this audit; the writer report cites Crossref for the first only. Check the second against Crossref.

## Not covered
Figures other than `fig_severity` values; Word files; docx text; numbers of unchanged older sections (audited in audits 1 to 5); the ledger and `progress.md` (not ticked: this audit is a number and wording audit, not a gate verdict).
