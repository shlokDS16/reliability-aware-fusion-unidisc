# Red-team closure check, Paper 2 TNNLS (HEAD 87bc6970), 2026-10-31

Agent: red-team (Sonnet). The lead saved the agent's returned text in condensed form and recorded the lead's fixes after it.

**Verdict: SIGN WITH CONDITIONS.** No fatal finding remains.
- Open conditions: F8 (rebuild the DOCX and the package), F9 (the Acknowledgment's AI wording, author-owned), N1 (broken supplement text).
- Hostile area chair: 4/10 (unchanged). The denoiser result is reported honestly. It also shows plainly that a stock denoiser
  exceeds the titled method under Gaussian noise, and that a linear logit matches it.

## Status of F1-F15
- Closed: F1 (rival AUROC restored, matches `runs/P2-GATE-M1/analysis.json`), F2, F3, F6, F7, F10, F11, F12, F13, F14.
- Partly closed:
  - F4: no gate-auditor verdict on the overrides; no ledger row for the denoiser run.
  - F5: miscount ("4 of the 10" should read "4 of the 9 learned refits").
  - F15: no meta file for the regenerated figures.
- Open: F8 (process), F9 (authors).

## Denoiser reporting
Plain and in the right places, with no rescue sentence; the abstract and conclusion are unchanged, as the binding rules require.
Three wording problems:
- the sixth reading's "matches or exceeds" understates the result;
- the VI-C "practical significance" sentence is a non-sequitur;
- the JPEG loss of denoise-then-LRF below the unweighted sum is shown only in S-VII.

## New defects
- N1: supplement S-I item 13 printed "olinkurl..." and "exttt..." (backslashes lost).
- N2: the F5 count.
- N3: the VI-C linear-logit interval was not marked unadjusted.
- N4: "calibrated" appears negated in a Study 1 context (no action).
- Scans clean: must-not words, bold, anonymity, AI mentions, Study 1/Study 2 separation.

## Lead's fixes after this check (2026-10-31, with number audit 4: PASS WITH FIXES)
- N1/A1: backslashes restored.
- A3: "item 3" corrected to "item 4".
- Audit-3 F1: the "moved from the main paper" wording removed in four places.
- F5/N2: "4 of the 9 learned refits"; ledger D0111 corrects D0110 and records the E1 run and its reporting.
- Sixth reading now: "exceeded in this sample, with an exploratory, unadjusted interval excluding zero".
- VI-C sentence now: "the paper does not show that LRF is the better choice against this noise".
- N3: "unadjusted, one of 40 exploratory variant-by-condition cells" added.
- Rebuilt: main and author versions 15 pp, 0 undefined references, no broken text, no identifiers in the review PDFs.

## Remaining
- F8: Word files and package (in progress).
- F9: the Acknowledgment wording (Shlok and his supervisor).
