agent: statistician
date: 2026-10-30
brief: RS-5 / V2-3 abstract ruling for Paper 2 (IEEE TNNLS): 150-250 words, no abbreviations, no equations or symbols
sources_examined:
  - paper2-tnnls/drafts/abstract-skeleton-v1.md (295 / 290 words)
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md A4.2.2 item 7, A4.2.3 NEG (lines 433-485)
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md A6.12 (lines 267-304), L-NI and L-LEN wording gate (lines 182-190)
  - research/paper2/tnnls/TNNLS-CHECKLIST-2026-10-29.md C3, C6; TEMPLATES-AND-DOCX-2026-10-30.md (abbreviation lines)
  - research/paper2/tnnls/REDTEAM-SPEC-2026-10-30.md F9/RS-5, F12, N1, V2-1, V2-3
  - paper2-tnnls/SPEC.md section 2
  - runs/P2-GATE-M4/analysis.json primary.per_corruption.{jpeg,noise,splice}; runs/P2-LRF-L1/a6_analysis.json family_L.{L1,L-NI,L-LEN}
coverage: >
  Every number in the candidate was read from the two analysis files and rounded to three decimals by the same script
  that counted the words (whitespace split, python -I). Not read: the IEEE Editorial Style Manual itself (the repo
  checklist quotes it; no proper-name exemption for abbreviations appears in any repo source). Not checked: the
  body text, Table I and Table II.
claims:
  - statement: "The candidate abstract below is 243 words by whitespace split, with no abbreviation, symbol or equation, and every number in it matches a runs file."
    status: supported
    evidence: scratchpad script c4.py (output printed in this file); runs/P2-GATE-M4/analysis.json; runs/P2-LRF-L1/a6_analysis.json
    level: E4
    confidence: 0.9
competing_explanations: []
unknowns:
  - "Whether the red team accepts the merged opening scope (row R1). If not, fallback F3 (250 words) applies."
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}

# Ruling RS-5 / V2-3, 2026-10-30

Authority: SPEC section 2 ("the statistician rules in a dated row; no writer choice"). Rows R1-R10 below are the dated rows.
A row never changes a number, an interval, a scope element or a hedge. It may only compress logic, move a non-binding
description to the body, or replace an abbreviation. No sentence is added that interprets the P discordance (A5.9 must-not 1, V2-1).

## Numbers used (source fact, runs files)

| Quantity | Value in abstract | Source |
|---|---|---|
| JPEG quality 10: net, 90% interval, n | -0.002, -0.006 to 0.000, 500 | M4 per_corruption.jpeg: delta -0.002, ci90 [-0.006, 0.0], n 500 |
| Noise 0.1: net, 90% interval, n | 0.000, 0.000 to 0.000, 500 | M4 per_corruption.noise: delta 0.0, ci90 [0.0, 0.0], n 500 (b = c = 0) |
| 128-pixel splice: net, 90% interval, n | -0.004, -0.010 to 0.002, 500 | M4 per_corruption.splice: delta -0.004, ci90 [-0.01, 0.002], n 500 |
| L1 accuracies | 0.733 without weighting, 0.802 with | family_L.L1 acc_b 0.7333, acc_a 0.8022 |
| L1 net, 95% interval | 0.069, 0.029 to 0.109 | net 0.06889, ci95 [0.02889, 0.10889], n 450 |
| L1 test | exact one-sided McNemar, 0.0005 | p_one 0.000508 (b 58, c 27); label confirmed, headline_p_le_0025 true, branch A |
| L-LEN | clause "including with length-matched negatives" allowed | label rejected, b 67 > c 33, p 0.00044 (A6.12 wording gate satisfied) |
| L-NI | 90% interval 0.009 to 0.053 | ci90 [0.00889, 0.05333], margin 0.03, non_inferior true, margin_note present |

## Ruling table

| Row | Item | Ruling | Exact text | Reason |
|---|---|---|---|---|
| R1 | Setting, scope merge (SPEC variant B) | MAY merge the model and dataset parts of the two scope sentences into the opening sentence. The merged element names the model and dataset only: no result, no motivation, no "both", no "same method". Study 1 keeps its own negative-type sentence; Study 2 keeps its own sample, exclusion and severity sentence. NOT allowed: "both studies use ...", "the same gate", "building on", any sentence that relates a result of one study to the other. | "we report two separately preregistered studies in one pretrained model of this kind (UniDisc, 1.4 billion parameters) on Common Objects in Context image-caption pairs." then "Each negative is a random other caption." (study 1) and "This is on 450 validation-split images not used to design or fit the method, at that one severity." (study 2) | Saves about 20 words. Substance of A4.2.2 item 7 and A6.12 scope is kept element by element. The title already carries the model. Red team to countersign that this is scope, not a link (A6.12 placement 1). Fallback F3 repeats the scope per study (250 words). |
| R2 | Study 1 scope sentence form | MAY be reworded from "This is {S}" to "Each negative is a random other caption" once model and dataset sit in the opening. Must keep model, dataset, negative type. | as R1 | Shortening only. |
| R3 | NEG sentence, exclusion clause | MAY merge the two parallel clauses (logical conjunction reduction: "an improvement larger than 0.05 is excluded and a loss larger than 0.05 is excluded" equals "an improvement or a loss larger than 0.05 is excluded"). MUST keep "no improvement was detected", the 90 percent interval, the three triples, n, and the sentence "This does not show that the gate has no effect." | "so an improvement or a loss larger than 0.05 is excluded." | Same truth conditions, 4 words. Not allowed: dropping either direction, dropping any interval, replacing "excluded" with "unlikely" or "small". |
| R4 | Study 1 method description (not binding in the abstract) | MAY be shortened to one clause and the alpha guarantee sentence MAY move to Methods. If the guarantee is ever mentioned in the abstract it must keep the A4.2.2 rule 3 wording ("the expected flagged share of a clean pair's tokens is at most alpha"); no "calibrated". Conformal risk control moves to the body. | "In the first, a gate discards low-likelihood image tokens." | The abstract needs only to say what was tested. "Suspect" and "detects" are barred by K2 (the score is a measured object, not an asset); "low-likelihood" is neutral. |
| R5 | L1 sentence | MAY NOT be shortened beyond the substitutions in R6. Keep: "frozen", "learned reliability-aware fusion of token evidence", "fresh preregistered fold", both accuracies, net, 95 percent interval, exact McNemar one-sided, "including with length-matched negatives" (allowed: L-LEN rejected, b 67 > c 33). | see candidate | Binding A6.12 sentence; headline claim; branch A requires p <= 0.025 (0.0005 passes). |
| R6 | L-NI sentence and margin note | MAY NOT be shortened or merged. Keep "lost no more than three points", the 90 percent interval 0.009 to 0.053, and "the margin was fixed after an exploratory clean interval had been seen". Required whenever L1 is in the abstract (C6-5). | see candidate | Binding. See concern C-1 (sign of the interval). |
| R7 | Study 2 scope | MAY be shortened: "COCO val2017" becomes "validation-split" with the dataset named in the opening (R1). "Gaussian noise" is already named in the L1 sentence, so the scope tail reads "at that one severity". Keep: 450, not used to design or fit the method, one severity. | "This is on 450 validation-split images not used to design or fit the method, at that one severity." | val2017 is a file-level identifier; it goes to Methods. |
| R8 | alpha clause "(preregistered one-sided level 0.05)" (question 4) | STAYS in the abstract, merged into the test phrase. It MAY move to Results only as the pre-ruled overflow valve: if any later edit pushes the count above 250, the clause moves and the abstract keeps "exact one-sided McNemar test" (fallback F1, 238 words). No other element is the valve. | "exact McNemar test at the preregistered one-sided level 0.05, probability value 0.0005" | The candidate has room (243), so no reason to drop a binding clause. A one-sided test at 0.05 is the less conventional choice; disclosure belongs where the p-value is. |
| R9 | Abbreviations and symbols (question 2) | GATE-M phrase: "This does not show that the gate has no effect." CI: "confidence interval". sigma 0.1: "standard deviation 0.1". "p = 0.0005": "probability value 0.0005" (no letter p, no equals sign; "p-value" avoided because the letter p is a variable). 1.4B: "1.4 billion parameters". McNemar: KEPT (a surname, as Gaussian is; the test name is not an abbreviation). UniDisc: KEPT (name of the evaluated model; it is in the title and in the binding scope; no repo source gives an exemption, see C-2). "val2017": moved to Methods (R7). No "%", "=", "+/-" in the abstract: "percent", "plus or minus" are spelt out. | see candidate | C6 plus the V2-3 symbol condition. |
| R10 | JPEG and COCO (question 2) | MUST be expanded. Proper names are NOT accepted as an exemption, because no repo source (checklist C6, AC-STRUCT quotation, templates file) gives one and "no abbreviations" is the quoted rule. Write "Joint Photographic Experts Group compression" and "Common Objects in Context". The short forms are defined in Methods. Cost: 6 words (JPEG +3, COCO +3). | see candidate | If Shlok or the editors accept proper names, fallback F2 (237 words) swaps them back. This is a choice of risk, not of statistics. |
| R11 | Degenerate noise interval (question 3) | KEEP "0.000, 0.000 to 0.000" exactly as computed (b = c = 0 gives a point-mass bootstrap interval). No wording is added to the abstract. No new number: no exact-binomial or rule-of-three bound is in any runs file (theta_cp95 for noise is NaN), so none may appear. No sentence anywhere may say the gate "rarely acted" or "changed no decision" (A5.9 must-not 1, V2-1). | as computed | The binding NEG content prints the computed interval. The faithful body statement is about the estimator, not the result (see below). |
| R12 | Count rule | The word count is the whitespace split of the abstract paragraph, numbers and hyphenated tokens counting as one word. Limit 150 to 250. Any later edit re-runs the count; above 250, R8 applies first. | | |

### Body sentence that makes the degenerate interval honest (allowed, red team to confirm)

Methods (estimator definition, not a result): "The percentile bootstrap interval has zero width whenever no pair is discordant; the
discordant count for each corruption is in Table I." This states a property of the estimator and points to the number that Table I
is already allowed to print (A5.9 must-not 1). It does not say how often the gate acted. Expect a reviewer to ask what the zero-width
interval means for the noise exclusion; the answer in the response may be the estimator property plus Table I, nothing more. The
exclusion under noise rests on the preregistered rule as computed; its claim strength is weaker than the other two (an interval
with no sampling variation excludes nothing by itself). That is a statistical weakness, recorded as concern C-3, not an
authorised abstract caveat.

## Candidate abstract for the writers (243 words, whitespace split)

Unified masked diffusion models verify captions against images, but received images may be damaged; we report two separately preregistered studies in one pretrained model of this kind (UniDisc, 1.4 billion parameters) on Common Objects in Context image-caption pairs. In the first, a gate discards low-likelihood image tokens. In the preregistered test no improvement was detected under Joint Photographic Experts Group compression at quality 10, Gaussian noise with standard deviation 0.1 and a 128-pixel splice; for each tested corruption the 90 percent confidence interval of the net accuracy change lay inside plus or minus 0.05 (-0.002, -0.006 to 0.000; 0.000, 0.000 to 0.000; -0.004, -0.010 to 0.002; 500 pairs each), so an improvement or a loss larger than 0.05 is excluded. This does not show that the gate has no effect. Each negative is a random other caption. In the second, on a fresh preregistered fold, a frozen learned reliability-aware fusion of token evidence raised image-direction verification accuracy under Gaussian noise with standard deviation 0.1 from 0.733 without reliability weighting to 0.802 (net 0.069, 95 percent confidence interval 0.029 to 0.109; exact McNemar test at the preregistered one-sided level 0.05, probability value 0.0005), including with length-matched negatives. On clean images it lost no more than three points (90 percent confidence interval 0.009 to 0.053); the margin was fixed after an exploratory clean interval had been seen. This is on 450 validation-split images not used to design or fit the method, at that one severity.

Checks run on this text: no "%", "=", "CI", "sigma", "GATE", "1.4B", "JPEG", "COCO", "p =" ; no sentence links the two studies; no harm clause; no
Study 1 object beside a Study 2 number; no H, PS, E-pred or detection content; one paragraph. Index terms are not part of the count.

## Fallbacks (apply only on the stated trigger)

| ID | Trigger | Change | Words |
|---|---|---|---|
| F1 | A later edit exceeds 250 | Replace the test phrase by "exact one-sided McNemar test, probability value 0.0005"; alpha clause goes to Results verbatim (R8) | 238 |
| F2 | Shlok or the editors accept proper-name exemption for the format and dataset | "JPEG compression" and "COCO" replace the expansions | 237 |
| F3 | Red team rules that R1 is a link sentence | Opening ends after "two separately preregistered studies." Study 1 scope: "This is in one pretrained unified masked diffusion model (UniDisc, 1.4 billion parameters) on Common Objects in Context image-caption pairs with a random other caption as the negative." Study 2 scope: "This is in the same model, on 450 validation-split images not used to design or fit the method, at that one severity." If "the same model" is also refused, repeat the full model phrase (about +9 words, 259) and apply F1 and F2 together (about 246) | 250 |
| F4 | Red team insists the L-NI interval be labelled (concern C-1) | "(90 percent confidence interval of the net change 0.009 to 0.053)" | 247 |

Nothing in this ruling needs Shlok to proceed. Two items are Shlok's if he wants to deviate from the conservative reading:
JPEG/COCO proper names (F2), and the UniDisc name as an abbreviation (C-2).

## Concerns

- **C-1 (L-NI sign, red team F12).** In `a6_analysis.json` L-NI the net is +0.031 (LRF minus no weighting, clean), interval +0.009 to +0.053,
  so "lost no more than three points" is true but the printed interval is all positive. A reader may take it for the size of the loss. The
  binding sentence is kept verbatim (R6). F4 adds three words to name the estimand. Table II and Results must print both clean accuracies
  and say, once, that clean superiority was not a preregistered hypothesis (F12 disposition).
- **C-2 (UniDisc).** The name is contracted from a longer phrase. No repo source grants an exemption, but it is the model's name, in the
  binding title and scope. Kept; flagged for the red team.
- **C-3 (noise exclusion strength).** With zero discordant pairs the bootstrap interval has no variation, so "an improvement larger than
  0.05 is excluded" under noise follows the preregistered rule but has no sampling-error content. An exact bound would be a new
  number outside the preregistered plan and is not in any runs file. If wanted, it can only enter as a labelled exploratory
  sensitivity in the analysis script and Results, never in the abstract. Lead's decision.
- **C-4 (percent in figures).** "0.05" is a proportion and "three points" is a percentage-point margin; the abstract uses both. Body keeps
  one convention (proportions), with "three points" defined as 0.03 at first use in Methods.
- **C-5 (A5.9 wording).** The abstract says "net accuracy change" without a sign convention; the body must state that positive favours
  the gate (Study 1) or the learned fusion (Study 2).
