# Author checks of screening, extraction and census: results (2026-10-21)

Three random samples were checked against the final model decisions: extraction (12 studies, D0060), full-text
screening of tranche T1 (40 records) and the value-rule census (24 papers). Sheets, draws and scripts:
`research/HUMAN-CHECK-2026-10-21.xlsx`, `research/HUMAN-CHECK-SCREENING.xlsx`, `research/HUMAN-CHECK-CENSUS.xlsx`;
`analysis/extraction/d0052/human_check_*.py`, `analysis/screening/human_check_screening_*.py`,
`analysis/census/human_check_census_*.py`. Every number below is in the agreement JSON next to each script.

## How the answers were made (describe exactly this in the paper)

The first author's own words in the chat on 2026-10-21: "Actually I checked then validated again with ai then
replaced my mundane analysis with combination of ai and my analysis." So each recorded answer is the first author's
final answer, made after reading the paper and after comparing it with a reading by a separate AI system. It is not
a human-only reading, and the author's first answers were not kept. The notes in the sheets are partly the AI's
text (for example "unavailable in this runtime", "full text/local copy not accessible here").

Blindness: the AI's notes say the local `C:\` copies were not reachable from where it ran, so it could not open the
repository or the model-answer files; the author states that they did not open them. The AI system is not named in
the record yet (ask the author before the paper names it; the venue's LLM-use statement must list it).

Accordingly the paper must say "author check, assisted by an AI system", not "human validation", and the limitation
that no purely human screening sample was recorded stays in Section 10 (reworded, not removed).

## Results

**Extraction (6 study-level flags behind RQ2-RQ6, 12 studies).** 7 of 12 studies answered; 5 marked unclear on every
question. 34 yes/no pairs: 31 agree (91 percent), kappa 0.82 (95 percent bootstrap interval over studies 0.63 to
0.95; 2000 draws, seed 20261022). Per question: Q1 6/7, Q2 1/1, Q3 7/7, Q4 6/7, Q5 6/6, Q6 5/6.

**Screening (include/exclude of T1, 20 model-included and 20 model-excluded).** 40 of 40 filled; 10 unclear
(7 model-include, 3 model-exclude; mostly "full text not retrievable" by the AI). 30 decided pairs: 21 agree
(70 percent), kappa 0.41 (95 percent bootstrap interval 0.09 to 0.71; 2000 draws, seed 20261023). Table (author |
model): include|include 10, include|exclude 6, exclude|include 3, exclude|exclude 11. Exclusion code on the 11 both
call exclude: 11/11 agree.
- Author include, model exclude (6): U04039 (model X2), M14797 (X2), M15989 (X2) -- all three turn on whether a
  multimodal system is one unified model (I1(b), R10 b3); M13335 (X0, adjudicated), M10607 (X0, adjudicated),
  M13723 (X7, adjudicated).
- Author exclude, model include (3): M16593 (author X0: diffusion only as baselines), M14971 (author X1), U01304
  (author X2, decided from the abstract only).
- Unclear (10): M18853, M16622, M15673, M12741, M15810, M16383, M15650, M13313, U00122, M13333.
- **Protocol trigger.** Protocol section 4 (lines 92-93) says a machine screener with kappa below 0.70 against the
  human triggers revision of its prompt and a rerun. This check compares the final adjudicated decision (not each
  screener) on 40 records (the protocol sample is at least 100) with an AI-assisted author reading, several of them
  from abstracts only, so it is not the protocol's validation sample; but 0.41 is below the bar and must be
  reported as such, with the 9 disagreements, not explained away.

**Census (24 papers; drawn 12 non-plain, 8 not stated, 4 plain, of a frame of 96 / 50 / 6).** 24 of 24 filled.
- Q2 value-rule class: 21/24 agree, kappa 0.79 (0.56 to 1.00); agreement weighted back to the frame 0.93. The 3
  disagreements are all the author answering "not stated": R0191 (census non-plain), R0802 and R0669 (census
  plain). Census claim split (non-plain or not stated vs plain): 22/24, kappa 0.63 (0.00 to 1.00); both changes move
  papers from plain into the claim's group, so the 147/153 figure is, if anything, conservative.
- Q3 diversity reported: 23/24, kappa 0.86 (0.47 to 1.00) (R0875 author yes, census no).
- Q4 step sweep: 20/24, kappa 0.64 (0.27 to 0.91) (R0773, R0517, R1068, R0696).
- Q1 headline is the one the rules pick: yes 20, no 2 (R0875, R1354), unclear 2.
- Optional letters: given for 11 papers, 6 exact matches with the census F2 code.

## Author-check items (AUTHOR-CHECKS Parts 1 and 3): confirmed (D0065)

The first author, chat 2026-10-21: "This should be removed I have already validated everything with human action
performed." So the Methods sentence that twelve adjudicator items "await the first author's confirmation"
(02-method.tex, after the code-link sentence) is replaced by one saying the first author confirmed them. The values
stay as reported (the adjudicator's), since the author confirmed rather than changed them.

## What this does and does not fix

It replaces "no human ever checked a decision" with recorded, blind, AI-assisted author checks on all three
pipelines, with agreement statistics. Extraction and census agreement are good. Screening agreement is moderate and
below the protocol's 0.70, mainly on the unified-model boundary (I1(b)) and on adjudicated X0/X7 calls; the unclear
rate (10 of 40) comes from the checker not reaching full texts. Recommended before submission: the first author
re-reads the 9 disagreements and the 10 unclear records from the local full texts (paths in the sheet), records a
resolution per record, and the paper reports both the pre-resolution kappa above and how many model decisions were
confirmed or overturned (any overturned include or exclude is corrected in the counts).
