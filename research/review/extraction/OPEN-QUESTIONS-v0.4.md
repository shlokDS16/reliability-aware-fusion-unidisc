# Open questions for the human author: extraction and appraisal form v0.4 (2026-10-20)

Each item names the gap, the options with their counts or costs, and where the plan uses the answer.
**Decision row** = needs a row in `research/ledgers/decisions.jsonl` (entered by the orchestrator) before the
stage named. The drafting agent decided none of them. Token figures are inference (E0). Items of
OPEN-QUESTIONS-v0.3.md not repeated here stay open as written there (list in part E).

## A. Scope

**OQ4-03 What "all multimodal" means (decision row, with OQ3-01; replaces OQ3-03).** The red-team found that
the v0.3 rule (screening field mm = "multimodal") counts a paper as multimodal when it contains any image,
video, audio or 3D experiment. About 29 of the 108 C2 records are text or general discrete-diffusion papers
whose only such work is a separate model (examples: M00285 ARDM with separate CIFAR-10 and SC09 models;
M14706 a text-diffusion thesis with one image chapter; M16730 LLaDA text plus MNIST). Meanwhile M18118, which
gives images to a diffusion LM (LLaDA-V on MathVista), is in frame R. Counts from
`analysis/extraction/multimodal_options.py` (log `multimodal_options-log.txt`); K records = C1 + C2 [+ C2b] +
the frame-R sample of 120:

| Option | What counts as multimodal | C1 | C2 | C2b | Frame R | K records | Block K (scope Option 1) | All blocks (scope Option 2) |
|---|---|---|---|---|---|---|---|---|
| (a) | C1 only (i1 in {b, ab}) | 53 | 0 | 0 | 543 | 173 | 6.9M-13.8M | 13.5M-23.4M |
| (b) | C1 + any D4 experiment in the paper (v0.3 rule) | 53 | 108 | 0 | 435 | 281 | 11.2M-22.5M | 21.9M-37.9M |
| (c) | C1 + papers where a D4 modality enters or leaves the model that produces the text; side-experiment papers join frame R | 53 | 80-89 | 0 | 454-463 | 253-262 | 10.1M-21.0M | 19.7M-35.4M |
| (d) | as (c), and side-experiment papers kept as a labelled census stratum C2b (block K with certainty, reported separately) | 53 | 80-89 | 29 | 425-434 | 282-291 | 11.3M-23.3M | 22.0M-39.3M |

What each option does: (a) makes every multimodal table a C1 census and leaves 55 more i1 = a multimodal
records to the weighted frame-R estimate; (b) mixes side-experiment text papers with vision-language, speech
and OCR models in the multimodal columns; (c) and (d) need one more coding pass (the 29 ids and 10 frame-R
candidates) before any draw. The ranges in (c) and (d) come from the provisional inputs: the 29 ids are the
red-team's reading of screener notes (E1); 1 frame-R record is confirmed joint-model (M18118) and 9 more are
keyword candidates (M07165, M13735, M14023, M15097, M15613, M15736, M16249, M17056, M17150). RQ5 uses C1
only under every option. Whatever is chosen, the multimodal columns carry the rule's name.

**OQ4-04 Human check before any draw (about 1-2 hours; replaces OQ3-04).** Please confirm or override, from the
full texts:
1. The 3 split text/multimodal records v0.3 decided by keyword (M02955 C2; M18118, M18656 frame R). The
   keyword tie-break is retired (red-team m4).
2. The 6 includes where screeners A and B agreed on the decision but not on i1 or nonlang_only; the decisions
   file carries screener A's value (m3): M10840, M12859, U04330 (i1 a against ab: C1 if ab); M16043 (ab
   against b, C1 either way); M11389, M18059 (nonlang_only).
3. The 15 B2 and 2 B3 borderline ids and the 6 duplicate-work candidates of OQ3-04.
4. Only if option (c) or (d) is chosen: the 29 side-experiment ids and the 10 frame-R candidates (list in
   multimodal_options-log.txt), each coded joint-model, side-experiment or text.
Results go to `analysis/extraction/mm-construct.jsonl`, `strata-overrides.jsonl` and `duplicate-works.jsonl`.

## B. Gate

**OQ4-07 Gate design and size (decision row, before Stage B; replaces OQ3-07).** With the four new criteria
of the red-team's C1 (19 criteria), a fixed gate of 60 passes an instrument at every good level with
probability 0.866 if the intra-record correlation (ICC) is 0.10, 0.660 at 0.20 and 0.486 at 0.30
(`gate_oc_v04-log.txt`). The ICC is unknown. Stage A's 12 records give only a wide bound (the Neyman 80
percent bound is calibrated but has a median of 0.18 when the true ICC is 0.10; `icc_check-log.txt`).
Options:

| Option | Rule | P(pass, all good) over ICC 0.05-0.30 | Largest P(pass, one bad) | Gate cost |
|---|---|---|---|---|
| (i) B-IP (plan s10.7) | 60 records, ICC re-estimated on them, extend to the n the rule needs, at most 120 | 0.935 (0.05), 0.915 (0.10), 0.912 (0.15), 0.910 (0.20), 0.860 (0.30) | 0.070 | expected 10.8M-19.0M (ICC 0.05), 12.5M-22.0M (0.10), 17.5M-30.8M (0.20), 20.9M-36.8M (0.30) |
| (ii) fixed n from Stage A | n from Stage A's bound, fixed before the gate | the 0.85 target is met when the bound covers the ICC (about 0.85 of cases); n 90 or more in 0.39-0.61 of cases at ICC 0.05-0.10 | 0.074 (n 90) | 10.6M-37.2M depending on n |
| (iii) fixed n 60 | as v0.3 | 0.930 (0.05), 0.852 (0.10), 0.660 (0.20), 0.486 (0.30) | 0.076 | 10.6M-18.6M |
| (iv) split | L/Q/H criteria on 30, K criteria on 60 (or 90) | K on 60: 0.817 (0.10), 0.569 (0.20); K on 90: 0.936 (0.10), 0.755 (0.20), 0.484 (0.30) | 0.082 | 8.9M-16.2M (12.5M-23.1M) |

Recommendation: (i). It is the only option that keeps P(pass | good) at or near 0.85 over the ICC range the
red-team called plausible, and it spends more only when the gate's own data show the ICC is high. The human
author may prefer (ii) if a fixed size before the gate matters more than cost.

**OQ4-08 Gate levels (decision row, before Stage B; replaces OQ3-08).** Plan s10.4: 19 criteria. New, for
approval or change now (they cannot change after the gate row): K-attr good 0.85 / bad 0.70 (line 0.71);
M-anchorG 0.85 / 0.70 (0.71); M-pool 0.85 / 0.70 (0.71); M-sign 0.97 / 0.90 (0.91). M-sign is stricter
because a sign disagreement reverses a contrast; it is also the criterion with the second-lowest pass rate
at the good level (0.960 at n 60, ICC 0.10). If you set M-sign's good level to 0.98 or 0.99 (sign
disagreement should be rare), P(pass | good) rises; the simulation must then be rerun before the gate row.
G5 line by n: 43 of 60, 51 of 72, 63 of 90, 72 of 105, 82 of 120.

## C. Unit rules

**OQ4-10 Anchor clauses (with v0.3 s13 row 3).** U3 now names its clauses; value-identity uses every earlier
table that holds the reference arm, with a factor-of-2 scale test; a full-configuration clause keeps a
single-task or "w/o" arm from being the anchor of a removal group. On Muddit it gives 0.6 (Table 3) and Joint
training (Table 4), where v0.3 allowed 0.2 and "T2I only". Approve.

**OQ4-11 Conditions in figures (row 35).** A condition never splits figure units, whether a series, an x-axis
category or a panel; figure trends are coded only from a stated sentence. Approve.

**OQ4-12 Unmapped benchmark and metric strings (row 34).** K units whose strings are not in the frozen lookups
match on the normalised printed string; a lenient match and the share of such units are reported, not gated.
Approve, or ask for a lenient primary match (the simulation does not depend on this choice).

## D. Process

**OQ4-16 Red-team review of v0.4 (plan s14 A6).** The parts to attack first: design B-IP (s10.7,
gate_adaptive_v04.py), the Neyman ICC bound (icc_check.py), the U3 value-identity clause, and the
contamination check.

**OQ4-17 Commit.** The v0.4 files and seven scripts with logs are written but not committed.

## E. Still open from v0.3 (unchanged)
OQ3-01 scope reading; OQ3-02 package; OQ3-05 frame-R sample size; OQ3-06 nonlang_only; OQ3-09 budget ceiling
(now with the m6 component, 1.5M-9.1M, and the B-IP gate cost); OQ3-10 suite rule; OQ3-11 training-free
replacement groups; OQ3-12 figures; OQ3-13 F1 readings; OQ3-14 S14 basis; OQ3-15 long-tail K workload;
OQ3-16 T1 gate. From v0.2: OQ2-07 to OQ2-12, OQ2-15 to OQ2-23 as listed in OPEN-QUESTIONS-v0.3.md part E;
OQ2-10 gold subset now with seed 20266100.
