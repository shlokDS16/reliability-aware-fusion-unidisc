```yaml
agent: paper-reader (census coder 3, adjudicator)
date: 2026-10-14
brief: Adjudicate every census row where coder 1 (design-space-v1.csv) and coder 2 (census-coder2.csv) disagree on non-plain value rule, F3 or F4, under census-codebook-v1.
sources_examined:
  - research/CONTRACT.md
  - research/review/coverage/census-codebook-v1.md
  - research/review/coverage/census-coder2-notes.md
  - research/review/coverage/census-coder2.csv
  - research/review/coverage/design-space-v1.csv
  - analysis/census/agreement.log
  - cached paper text in the main checkout research/sources/md/ (21 files, IDs listed below)
coverage: >
  21 papers: 2310.16834, 2406.07524, 2406.04329, 2406.03736, 2409.02908, 2202.04200, 2505.24857,
  2211.15089, 2305.18619, 2506.10892, 2505.15809, 2505.20147, 2505.14683, 2305.08379, 2502.13917,
  2410.17891, 2506.20639, 2505.22618, 2410.08709, 2410.01949, 2604.00007. For each: the sampling or
  experimental-setup passages and the cited F1/F3/F4 tables or figures, found by keyword search and
  then read in context (sampling, temperature, top-p/k, argmax/greedy, guidance, steps, entropy,
  diversity). Papers were NOT read end to end. Code was not opened. F1 values were not re-derived
  for M22 and M39. F5 text was not re-read for M24, M30, M39 and M40 (left unresolved, see below).
claims: []
competing_explanations: []
unknowns:
  - F5 for M24, M30, M39, M40: c1 says the value rule is fixed across the sweep, c2 says not stated; not on the adjudication list and not re-read. final-csv keeps c2 (conservative).
  - F0 versions of the five Exa copies (M02-M06) remain unstated.
next_test: {}
```

# Census adjudication (coder 3)

Outputs: `census-adjudication.csv` (126 rows: 21 papers x F1 to F6), `census-final.csv` (47 rows, coder 2 layout; only adjudicated cells replaced, the `notes` cell of the 21 rows gets an appended pointer).

Evidence level: E2 for "the paper reports X" on the 21 papers, for the passages listed. No ledger rows written.

## Rows adjudicated (computed from the two CSVs, not typed in)

- Set 1, non-plain value rule disagreements (15, from agreement.log): M03 M04 M05 M06 M07 M12 M14 M15 M17 M22 M24 M27 M39 M40 M45.
- Set 2, F3 differs on yes/no rows (7): M10 M30 M31 M36 M37 M40 M41.
- Set 3, F4 differs, coder 1 "ns" excluded (2): M14 M22.
- Union: 21 papers (M40 is in sets 1 and 2; M14 in 1 and 3; M22 in 1 and 3).

## Who was right (listed disputes only)

| field | coder 1 right | coder 2 right | both partly | neither | n |
|---|---|---|---|---|---|
| F2 value rule (set 1) | 2 (M12, M45) | 13 | 0 | 0 | 15 |
| F3 (set 2) | 3 (M10, M37, M41) | 4 (M30, M31, M36, M40) | 0 | 0 | 7 |
| F4 (set 3) | 2 (M14, M22) | 0 | 0 | 0 | 2 |

Pattern: in the 13 F2 rows where coder 2 was right, coder 1 either had not coded the row (M03 to M06: "unknown") or had inferred a default the codebook forbids (greedy from a theorem: M39; guidance from CFG dropout: M27; best-of from a separate row: M24; ancestral for tau-leaping: M40; final argmax counted as A: M14, M17 variant, M15). In the 2 rows where coder 1 was right, coder 2 had missed a sentence it should have found (M12: zero temperature "for all experiments"; M45: "tokens are sampled") or missed a table (M14 Table 2 and M22 Table 6 step sweeps). Coder 2 read by keyword search, not end to end, and these are the misses that produces. Coder 2's F3/F4 "Yes" calls on M10 and M41 were over-reads of the codebook's pairing rule.

Corrections found outside the listed disputes (incidental, counted separately): F2 M10 (T removed, c2 right), M31 (G removed, c2 right), M36 (T dropped, c1 right); F4 M37 (Partial, c1 right); F5 M12 (Stated, c1 right), M22 (Not stated, c1 right), M14 (Stated, neither); F6 M22 and M45 (Not stated, both c2 NA wrong).

## Census headline after adjudication (F2 on 47 rows)

Plain U 8; non-plain 25; not determinable (NS or NA) 14. Before adjudication coder 2 had U 8, non-plain 23, NS/NA 16. Rows that move: M12 NS to A; M45 NS to S; M36 loses T (T+P to P). Everything else keeps coder 2's class, including M14 (c1's A rejected) and M10 (S only, c1's T rejected). The 14 undeterminable rows are the real finding for the E_sel-type question: for about 30 percent of the papers the text does not state the value rule for the headline.

## Per-row decisions that rest on a judgement call

- M04 MDLM: coded U on Sec 4.1 (each token sampled from p_theta) reused by Sec 4.2 SAR decoding; Table 5 never restates the temperature. Borderline; NS is the alternative.
- M07: F1 row taken as Fig 9 (own sampler, 64-bit). Fig 7 compares prior samplers in 32-bit and is not the own method.
- M14: U on the per-step rule with stated defaults; final argmax is a note under the codebook rule.
- M15 Plaid: F1 = NA kept (no generated-sample metric for the headline model); the stated rule (ancestral, T=4096, score temperature 0.9, final argmax, Sec 5) is in the F2 detail as a note.
- M17 Duo: F1 row is base Duo, ancestral. Greedy-Tail (A on last step only) is a separate variant in the same figures; a row-per-variant reading would give U and A.
- M36: only P coded; the "temperature of top-k 0.98" wording is ambiguous.
- M10: S only; "temperature annealing" has no value or direction.

## Proposed codebook amendments (not applied; codebook v1 untouched)

- A-1 (F3). The list is closed (entropy, distinct-n, self-BLEU, MAUVE, pass@k). Decide whether image-diversity metrics (Precision/Recall, CAS, LPIPS diversity) count; applied literally they do not (M10). Define "explicitly pairs": same experiment in an appendix that the main text never cites does not pair (M41); say whether an appendix titled as an extension of the F1 experiment does.
- A-2 (F1). Define "main task" and "paper's own method" for (a) adaptation or ablation tables that come first (M31, M36), (b) unified models with several tasks (M22, M45; policy P2 was used), (c) a plain row and a best-of or guided row in the same table (M24: take the base row). Adopt coder 2's policy A1 formally: skip speed-only and likelihood-only abstract numbers.
- A-3 (F2 U). State what counts as "states": a section-level sampler definition reused by the experiment (M04), a table of stated defaults (M14), a blanket "no temperature scaling" for an experiment (M03). Add a rule for process-level samplers (tau-leaping, Euler CTMC, ODE): plain only with an explicit statement.
- A-4 (F2 A). Say that a per-step argmax projection inside the sampling loop is A (M30, M31) while the final rounding of a continuous channel is only a note (M14, M15). The current text allows both readings.
- A-5 (F2 variants). When a paper reports a plain and a non-plain variant of its own sampler in the F1 figure (M17 Greedy-Tail; M24 best-of row), require one F2 row per variant, or name which variant is the headline.
- A-6 (F2 T). T requires a stated value below 1; annealing without a value (M10) and ambiguous wording (M36) are not T. Say that explicitly. Also say whether a temperature above 1 is T (coder 2 A22).
- A-7 (F2 evidence). Theorems and proofs about greedy decoding are not a statement of the experimental value rule (M39); a sentence like "zero temperature for all experiments" is (M12). Add a line to the codebook.
- A-8 (F4). Say that a hyperparameter table that includes a step-count row with generated-sample metrics counts as a sweep (M14 Table 2), that a main-text figure with exactly two settings is Partial (M37), and which metrics count as "generated-sample" for multi-task models (M22 Table 6 mixes CLIP score and MMLU).
- A-9 (F5, F6). Define "Stated" (experiment-level sentence versus method-level default) and say what F6 is when the sweep spans several tasks and only some use guidance (M22, M45: coded Not stated).
- A-10 (F1 = NA). Add a code for qualitative-only samples with a stated rule (Plaid), so the value rule is kept rather than dropped.

## Concerns for the orchestrator

1. Coder 2 missed explicit text on 4 of 21 rows (M12, M45, M14 and M22 tables). Agreement statistics computed before adjudication understate how often the paper states its rule. Re-run agreement.py on census-final.csv as the reconciled record, and report the pre-adjudication kappas as the blind-coding result.
2. Coder 1 did not code F3/F4/value rule for M03 to M06 and several others; those are abstentions, not disagreements. Counting them as coder 1 errors inflates coder 2's win rate (13 of 15).
3. F5 on M24, M30, M39, M40 is unresolved (c1 Stated, c2 Not stated, not on the list, not re-read).
4. M04 (U) and M10 (F3 No by literal rule) are the two calls most likely to change if the codebook is amended; A-1 and A-3 should be settled before the census table is published.
