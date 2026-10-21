agent: clarity-editor
date: 2026-10-21
brief: Clarity edit of Section 5, parts of Section 2, one paragraph of Section 10, Section 11 and the compiled abstract (paper 1, ACM Computing Surveys)

# Files edited (in place, nothing committed)

- paper/review/sections/05-rq-evidence.tex (all, 21 edits)
- paper/review/sections/02-method.tex ("Data extraction and quality appraisal" including its Synthesis paragraph, and "Departures from the protocol"; 18 edits). The "Use of AI in conducting the research" subsection, Table ai and the human-involvement paragraph were not touched.
- paper/review/sections/10-limitations.tex (paragraph "Screening, extraction and protocol" only; 2 edits). The "Use of AI" paragraph was not touched.
- paper/review/sections/11-conclusion.tex (3 edits)
- paper/review/main.tex (compiled abstract paragraph only; 4 edits). Commented abstract versions were not touched.

Originals for comparison: scratchpad `orig/` (copies taken before the first edit).

# Build

`latexmk -pdf -interaction=nonstopmode main.tex`: "Output written on main.pdf (35 pages, 980376 bytes)". Before the edit it was 35 pages. Zero lines starting "!" in main.log; no undefined references or citations. Edited files remain ASCII with CRLF line endings.

# Checks

Script: scratchpad `verify.py` (compares original and edited file, whole file, so it also covers untouched parts), plus `check_text.py --compare`.

| File | Numbers (multiset) | \cite / \ref / \label / \input / \aud keys | "% src" comments (text and order) | Verdict words (untested, mixed, weakly supported, well supported) |
|---|---|---|---|---|
| 05-rq-evidence.tex | identical (607 tokens) | identical (18) | identical (23) | identical |
| 02-method.tex | identical (854) | identical (37) | identical (71) | identical |
| 10-limitations.tex | identical (96) | identical (11) | identical (10) | identical |
| 11-conclusion.tex | identical (55) | identical (11) | identical (5) | identical |
| main.tex | identical (92) | identical (14) | identical (26) | identical |

`check_text.py --compare` reports "Protected content: identical" for 02, 10 and 11. For 05 it reported one added number (25) after my first pass ("Of the 25, 23 leave ..."); I rewrote that sentence and the multiset is now identical. For main.tex the script's output was an artefact (the original copy sits outside the folder that holds `\input` files); the whole-file multiset check above covers it. Meaning warnings, all read against the originals and benign: 05 "not" 9 to 11 (two sentences changed from "are the same" to "do not change"); 02 "no" 15 to 14 and "not" 37 to 38 (departure 4: "No human validation of screening" became "Screening was not validated by a human").

Sentences over 45 words in Section 5: 9 before, 0 after. Mean sentence length 27.8 before, 19.9 after (script, whole file).

# Change log

| Location | Change | Why |
|---|---|---|
| 05, opening paragraph | Semicolon chains split into short sentences | One idea per sentence |
| 05, RQ1 count paragraphs | "28 involve ... and 13 were recorded differently" became "A further 28 ... and the two screeners recorded 13 differently"; long RQ-tag sentence split | Clear subject for each number |
| 05, Population, Reliability, Verdicts paragraphs | Long sentences split; the four verdict definitions are now four parallel sentences ("A verdict is untested if ...", "It is mixed if ...", etc.); "except RQ5 ..." moved out of a parenthesis | Referee can find each threshold; wording of the thresholds unchanged |
| 05, RQ1 sample, RQ2, RQ3, RQ4, RQ5 | Semicolons to full stops; "Verdict" lines no longer end in a trailing "and ..." clause; "ablate the very component" to "ablate the component"; "(two thirds is passed)" to "(the two-thirds threshold is passed)"; "which is why we count studies" to "so we count studies" | Plainer sentences; no verdict, direction or number touched |
| 05, RQ6 and table caption | Semicolon chains split; "12 are not supported ..." made its own sentence ("A further 12 ...") | Same |
| 02, extraction subsection | Stratified-sample paragraph, form description, extractor description, agreement paragraph, code-link paragraph and Synthesis paragraph split into shorter sentences | Sentences over 45 words removed; no content moved across "% src" comments |
| 02, departures list | Items 3, 6, 7, 8, 9, 11 split at semicolons or commas; item 4 opening reworded | Same |
| 10, Screening paragraph | Two long sentences split into five | Same |
| 11, paragraphs 2 to 4 | Three long sentences split | Same |
| main.tex abstract | "are reviewed under PRISMA 2020: 615 studies are included" became "We review ... under PRISMA 2020. The review includes 615 studies"; semicolon list split; "not confirmed by CLIP" became "CLIP does not confirm it"; "In a random census, 147 of 153 papers" became "In a census of a random sample, 147 of 153 codable papers" | Active voice, matches the body and conclusion wording for the census |

# Flags for the author

1. Abstract, census sentence: the compiled abstract said "In a random census, 147 of 153 papers"; Section 11 says "a census of a random sample ... 147 of 153 codable papers". I aligned the abstract with the body. The numbers are unchanged. Revert if you prefer the shorter wording.
2. Abstract now opens with "We review". The abstract comment says "no first person singular", so first person plural is allowed, and the commented 100-word version also opens "We review". Revert if the venue prefers a passive opening.
3. Section 2 departure 6 says the sample is 80 studies and departure 10 says the appraisal covers 79; the text of Section 2 explains that one study left the frame (D0059). Not changed.
4. The conclusion still carries the "\aud" census-count audit tag; untouched.
5. Not edited, by instruction: the AI-use statement, Table ai, the human-involvement paragraph and the "Use of AI" paragraph of Section 10. No AI-use wording was removed or weakened.
6. No Grammarly or detector score was measured; none is claimed.
