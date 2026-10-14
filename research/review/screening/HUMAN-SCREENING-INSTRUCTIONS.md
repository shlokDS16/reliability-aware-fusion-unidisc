# Human validation of screening (protocol section 4, step 3)

For: a human author (Shlok, or the professor). Time needed: about 2 to 3 hours.

1. Open `human-sample.csv` (218 records, a random 15 percent of the 1453 screened records, drawn
   with seed 20261014; open in Excel).
2. Read `criteria-v1.md` once. It is the exact text both machine screeners received.
3. For each row, read only the title and abstract and fill:
   - decision: include, exclude or unclear;
   - code, only for exclude: X0 (no diffusion component), X1 (non-text diffusion only), X2 (text
     only as conditioning), X3 (survey or position), X4 (no result), X7 (application of an
     unchanged model), X8 (before 2021 or not English);
   - note: optional.
4. Do not look at the machine screeners' decisions (`screener-A/`, `screener-B/`) before you
   finish.
5. Save the file under the same name and tell Claude. The script then reports Cohen's kappa for
   each machine screener against you and against each other. If either is below 0.70 against
   you, its prompt is revised and the stage rerun (protocol rule).

The paper's Methods section will state that two language-model screeners were used and validated
against this human sample; it will not present them as human reviewers.
