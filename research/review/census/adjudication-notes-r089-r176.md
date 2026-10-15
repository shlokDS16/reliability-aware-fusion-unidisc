# Census adjudication notes, ranks 89 to 176 (2026-10-15)

Adjudicator: Claude (Opus), not blind (read both coders' rows and the paper texts).
Governing rules: codebook v1.2 (`research/review/coverage/census-codebook-v1.2.md`) on top of v1.1 and v1.
Output: `research/review/census/census-random-final-r089-r176.jsonl` (88 rows, ranks 89 to 176, one per rank, sorted by rank).
Inputs: coder A `coder-A-claude-r081-r120.jsonl`, `-r121-r160.jsonl`, `-r161-r176.jsonl`; coder B `coder-B.jsonl` (Codex, ranks 89 to 91), `coder-B-claude-r092-r128.jsonl`, `coder-B-claude-r129-r176.jsonl`; `disagreements-random.csv` (59 rows for ranks 89 to 176); paper texts in `research/sources/census-text/`.
Agreement figures are not recomputed here (v1.2 disclosure paragraph). Every adjudicated cell carries an `adjudication` entry with A, B, final and basis.

## Row totals

| Status | Ranks | Count |
|---|---|---|
| eligible yes | all others | 81 |
| eligible no | 123 (X1), 128 (X1), 151 (X1), 165 (X1), 169 (X0) | 5 |
| NO_TEXT | 90, 144 | 2 |

Among the 81 eligible rows: F1 = NA for 6 (142, 149, 157, 162, 170, 173), no QL rows, so the F2 to F6 denominator is 75.
F2 in those 75: non-plain yes 48, no 3 (U: 112, 124, 153), unknown 24 (NS); base rule not determinable (NS or +NS) 34.
F3 yes 16 / no 59. F4 yes 26, partial 5, no 44. F5 among the 31 sweeps: stated 9, not stated 22, co-varied 0.

## Counts of adjudicated fields

### Field-level disagreements from `disagreements-random.csv` (48 field rows; the 11 derived `nonplain` rows follow F2_codes)

| field | A | B | neither | total |
|---|---|---|---|---|
| eligible | 2 | 0 | 0 | 2 |
| F2_codes | 3 | 7 | 8 | 18 |
| F3 | 3 | 1 | 0 | 4 |
| F4 | 1 | 8 | 0 | 9 |
| F5 | 3 | 8 | 0 | 11 |
| F6 | 0 | 3 | 1 | 4 |
| total | 12 | 27 | 9 | 48 |

Derived `nonplain` class (11 rows): A 2 (152, 153), B 8 (125, 129, 134, 139, 150, 154, 159, 160), neither 1 (128, now ineligible). Note that for 134, 139 and 154 the final letter (C) differs from coder B's A, but the derived class (non-plain yes) matches B.

Per rank: A won 116 F3; 123 eligible; 124 F3, F5; 152 F2; 153 F2, F3, F5; 164 F2; 169 eligible; 176 F4, F5.
B won 91 F2; 94 F4; 96 F5; 98 F4, F5; 111 F2, F4, F5, F6; 116 F2; 118 F4, F5; 119 F4, F5; 129 F2; 148 F4, F5; 158 F2, F3, F4, F5; 160 F2; 167 F2; 172 F6; 175 F4, F5, F6.
Neither: 99 F2 (G+NS); 125 F2 (M+NS); 128 F2 (NA, ineligible); 134 F2 (C); 139 F2 (C); 150 F2 (G+NS); 154 F2 (C); 159 F2 (G+NS); 166 F6 (NA).

### Cells changed outside the disagreement list (70 entries)

| field | A | B | neither (both coders overruled) | both (normalisation only) | total |
|---|---|---|---|---|---|
| eligible | 0 | 0 | 2 | 0 | 2 |
| exclusion_code | 2 | 0 | 2 | 0 | 4 |
| F0_version | 0 | 3 | 1 | 0 | 4 |
| F1_value (F1 choice) | 14 | 11 | 5 | 1 | 31 |
| F2_codes | 0 | 0 | 17 | 0 | 17 |
| F4 | 0 | 0 | 4 | 0 | 4 |
| F5 | 0 | 0 | 5 | 0 | 5 |
| F6 | 0 | 0 | 2 | 0 | 2 |
| F4_location | 0 | 0 | 1 | 0 | 1 |
| total | 16 | 14 | 39 | 1 | 70 |

- F1 was not part of the agreement computation, but where the coders chose different F1 cells I chose one and recorded it (31 ranks). A: 98, 119, 121, 124, 134, 138, 139, 140, 143, 153, 159, 161, 164, 176. B: 91, 104, 109, 115, 125, 136, 145, 148, 154, 158, 174. Neither: 116, 129, 147, 155, 172. Normalisation only: 100 ("curves only" to figure-only).
- F0_version: 124, 125, 163 set to v2 to match the census-text header (B); 123 set to NA by the B-27 coupling. F0 is also NA on the other ineligible rows (128, 151, 165, 169) by the same coupling.
- Agreed cells overruled under a v1.2 trigger visible in the coders' own notes or F2_detail: F2_codes at 101, 103, 110, 113, 114, 115, 117, 120, 122, 133, 140, 141, 148, 155, 156, 163, 166; F4/F5 at 109, 129, 152, 166; F5/F6 at 99; F6 at 163; eligibility at 128, 165.

## v1.2 (and v1.1) rules invoked, with ranks

- A-2 (abstract number first; adaptation-table clause): 104, 109, 115, 125, 129, 147, 161, 176.
- A-3 process-level clause: 91, 114, 120, 141 (with B-21), 152, 158.
- A-4 (per-step projection is A): 167.
- A-6 / B-14 (tuned temperature without value is NS): 99.
- A-8 (exactly two settings is partial; appendix figure without numbers is partial): 94, 111, 148, 158.
- A-9 (stated / not stated): 99, 111, 124, 148, 153, 158, 163.
- B-2 (detectors, scorers, probes eligible when they report findings about the DLM): 157, 162, 170 (kept eligible, F1 = NA).
- B-3 (theory and synthetic-token studies): 128, 165 to X1; 142, 158 kept eligible.
- B-4 (unified models): 119, 123 (X1, robot actions), 151 (X1), 154.
- B-5 (diffusion-style operator in an AR model): 169 (X0).
- B-6, B-8 (X1 reading, code order): 123, 128, 165, 169.
- B-7 (scene text is text): 172.
- B-9 (F1 from the in-scope component): 116, 119, 145, 150, 153, 154, 158, 159, 172.
- B-10 (generated-sample metric; likelihood-scored MMLU skipped): 129.
- B-11 (F1 cell order): 91, 98, 116, 121, 124, 134, 136, 138, 139, 140, 143, 145, 148, 155, 158, 164, 174.
- B-12 (extraction must not move the F1 table): 116, 121, 161.
- B-13 (statement precedence): 129, 160.
- B-14 (U requirements; background samplers do not count): 99, 112 (U kept), 132 (NS kept), 134, 139, 153.
- B-15 (confidence-ranked unmasking, letter C; self-planning): C at 101, 110, 113, 115, 117, 122, 133, 134, 139, 140, 148, 154, 155; A at 89, 97, 129, 160; S at 103, 164.
- B-16 (training-only settings): 133, 154.
- B-17 (best-of-N and filtering as M): 111, 125; oracle@10 noted at 164.
- B-19 (particle/MTM selection with external reward = M + G): 116, 166.
- B-20 (constraint steering as G): 138 (kept A+G), 159, 163.
- B-21 (+NS when the base rule is unstated): 91, 99, 114, 120, 125, 141, 150, 156, 159, 166.
- B-23 (what counts as a sweep): 96, 98, 109, 111, 118, 119, 148, 175, 176.
- B-24 (sweeps on another task or axis): 109, 129, 152, 166.
- B-25 (co-varied only when stated; NA couplings): 98, 99, 109, 111, 118, 119, 129, 152, 163, 166, 172, 175, 176.
- B-26 (blanket sentences): 96 (not applied), 153.
- B-27 (vocabulary and couplings): 100, 123, 128 and all ineligible rows.

## Cases v1.2 does not settle (my call, flagged)

1. **Process-level continuous samplers with guidance (91, 114, 120, 141).** Euler ODE (91), DDIM (114), DPM-Solver (120) and a flow SDE sampler (141) with CFG or probe guidance, no statement on temperature or truncation. A-3 says process-level samplers (ODE integration) are plain only with an explicit statement; B-14 allows a sampler-settings list to stand in for (3) but does not repeal the A-3 clause. I coded G+NS for all four. 91 was disputed (A G, B G+NS). 114, 120 and 141 were agreed G cells that I changed for consistency; if the orchestrator reads v1.2's "other agreed cells stand" strictly, revert those three to G. Stochastic ancestral samplers (DDPM in 126, multinomial diffusion in 143) were left as G.
2. **TPP-style rank-then-sample (103).** B-15 codes confidence-ranked positions with a sampled value as S. The paper ranks positions by top-token probability and then samples, and argues explicitly that this is not LCR sample-then-filter; v1 lists "rank-then-sample" under U. I applied B-15 literally (T+S). The non-plain class is unchanged (T already present).
3. **Rank 116 quoted row.** The text quotes the MDLM trigram-steering row as "37.2 vs 79.2", but Table 4 shows 40.3 vs 85.3. I took that row and read the value from the table (40.3; B-11, B-12).
4. **Rank 124 table versus figure.** The OWT results sit in a tabular lower panel of Figure 3, before Table 1 (GSM8K). B-11 uses a figure only if no table exists, so I took Table 1. Reading the panel as a table would give coder B's F1 (OWT) and F3 yes.
5. **Rank 129 adaptation table.** Table 2 (50B against 100B adaptation) is the first results table. Under A-2's adaptation clause I used Table 3, the first dQwen3.5 row and its first generated-sample column (GSM8K 20.55, because MMLU is likelihood-scored). F4 is no either way (sweeps are on HumanEval, MBPP and MATH500 only).
6. **Abstract relative gains as F1 (104, 109, 115, 125, 147, 161, 176).** I read A-2 as admitting "improves accuracy by up to X%" claims as the first generated-sample result. This changes F4 at 109 (the HumanEval headline has no step sweep). At 147 the abstract's "up to 15%" is not tied to one benchmark.
7. **Rank 96 blanket sentence.** The only qualifying sweep is the block-length ablation (Table 7), and "In the main experiments, we use greedy decoding" may not cover it, so I coded F5 not stated (conservative v1 rule).
8. **Rank 158 eligibility (B-3).** The abstract is about absorbing discrete diffusion in general but ends by framing the result for diffusion language models, and the appendix has a SEDD text experiment. I kept it eligible and took F1 from the appendix (coder B). By contrast, 128 and 165 present generic results (pixels/phonemes/words; text and images) with no language framing, so they are X1.
9. **Rank 111 Top@1.** The selecting reward model is also the evaluation's scoring model. Under B-17 it is an inference-time score without ground truth, so I coded M; an "oracle" reading would give T+G.
10. **Rank 99 temperature grid.** Every candidate temperature (0.3, 0.6 and 0.9) is below 1, but the selected value is not stated. Under B-14/A-6 the temperature part is NS (G+NS), not T.
11. **Rank 152 argmax location.** The argmax token rule is stated in an analysis subsection (Sec 4.4.3) that describes the sampler used. I accepted it as A under A-3(b).
12. **Rank 156 best-first.** "Keep the top-K_t recovered tokens" does not name the ranking score, so I did not code C. The value rule is unstated, so G+NS.
13. **Ranks 143 and 91 quoted cells.** At 143 the text quotes both the test-other and test-clean WER; I took test-other, the number quoted first, in the introduction. At 91 both the 114M and 768M rows are quoted; I took 768M, which the text calls the best result. F2 to F6 are unaffected.
14. **Rank 112 U and rank 132 NS** were kept as agreed. At 112 the Sec 5 settings sentence counts as a complete list under B-14. At 132, a headline that matches the 2D-beam row of another table is an inference (B-14), so B-18 was not applied.
