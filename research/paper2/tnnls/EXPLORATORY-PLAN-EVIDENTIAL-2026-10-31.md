# Exploratory plan E4: Dempster combination of evidence-derived token opinions (2026-10-31)

Written by the Paper 2 lead before any computation; committed before the script is run. Source: the professor's sources of
2026-10-31 (evidential and uncertainty-aware fusion papers); expert reading and proposal in
`research/paper2/sources/PROF-SOURCES-FUSION-2026-10-31.md` section 5 (definition and derivation taken from there unchanged).
EXPLORATORY: specified after the preregistered Study 2 results; no test, no tuning, no p-value, no multiplicity claim.

## Question
Does an unlearned evidential (Dempster-Shafer) combination of the per-token evidence, the family of rule used by trusted and
evidential multimodal fusion, differ from the unweighted sum, the unlearned rank weight (A-UNL) and the frozen LRF on the fresh fold?
Limit stated in advance: those methods learn opinions with an evidential head and loss; the frozen scorer has none, so the opinions
here are constructed from Delta_j. This is "Dempster combination of evidence-derived opinions", not a reproduction of any method.

## Definition (no fitting; inputs `<cond>_delta` and `<cond>_s3` only)
Frame {c+, c-}, Dirichlet prior weight 2. Per token j: e+ = lam max(Delta_j, 0), e- = lam max(-Delta_j, 0), S = e+ + e- + 2,
b+ = e+/S, b- = e-/S. Shafer discount r_j: m(+) = r_j b+, m(-) = r_j b-, rest on the frame. Dempster's rule multiplies the
commonalities q(+) = 1 - r_j b-, q(-) = 1 - r_j b+, so the combined decision is c+ iff D = sum_j [log q_j(+) - log q_j(-)] > 0;
a tie (D = 0) is wrong, as in every other row.
- Primary arm, fixed now: lam = 1 (Delta in nats), r_j = 1 - rank_s3_j (the A-UNL weight: within-image percentile rank of s3,
  `analysis_posthoc/learned_ceiling/data._rank`).
- Reference arm: lam = 1, r_j = 1 (no discount; closed form D = sum_j sgn(Delta_j) log(1 + |Delta_j|/2)).
- Sensitivity only (supplement): lam in {0.1, 10}, with and without the discount. lam is never chosen by accuracy.
Expected, stated before computing: near A-UNL and the unweighted sum (for small |Delta_j| the discounted D is about
(lam/2) sum_j r_j Delta_j, i.e. A-UNL).

## Data, checks, reporting
- The 450 fresh-fold items x {noise0.1, jpeg10, splice128, clean} in `runs/P2-LRF-L1/arrays`; labels and NONE/LRF decisions from
  `runs/P2-LRF-L1/predictions.jsonl`. No design item, no refit, no frozen object touched.
- Consistency gate before anything is written: the unweighted sum recomputed from `<cond>_delta` must equal `y_none` for every
  item and condition; A-UNL recomputed from `<cond>_s3` must reproduce the stored A-UNL accuracy of
  `runs/P2-LRF-ABL-SCORE/ablation_analysis.json` in every condition.
- Reported per condition: accuracy; paired difference against NONE, A-UNL and LRF, (b - c)/n with discordant counts, 95 percent
  paired percentile bootstrap interval (10,000 item resamples, SeedSequence(0), one index matrix per condition shared by all arms,
  as `e2_combiners.py`). After the accuracies are written: median and 95th percentile of |Delta_j| over the fold (descriptive).
- Output `runs/P2-LRF-E4/evidential.json` from `analysis/paper2/lrf/e4_evidential.py`. Placement: one row in Table IV if the page
  cap allows, else supplement S-VII; one clause in V-G; the constructed-opinion limit in the table note or VI-C.
