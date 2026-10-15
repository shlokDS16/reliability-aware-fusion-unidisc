# Census harmonisation notes, ranks 1 to 176 (random sample)

Date: 2026-10-15. Harmoniser: Claude (Opus 5.5), not blind (read both adjudicated halves, both coders' rows and the paper texts).
Governing rules: codebook v1.2 (`research/review/coverage/census-codebook-v1.2.md`), with v1.1 and v1 where v1.2 is silent.
Inputs (not edited): `census-random-final-r001-r088.jsonl`, `census-random-final-r089-r176.jsonl` and their adjudication notes;
coder rows `coder-A-claude-r*.jsonl`, `coder-B.jsonl`, `coder-B-claude-gapfill.jsonl`, `coder-B-claude-r092-r128.jsonl`,
`coder-B-claude-r129-r176.jsonl`; paper texts in `research/sources/census-text/`.
Output: `census-random-final.jsonl` (176 rows, sorted by rank). Each row keeps its `adjudication` object and has a `harmonisation`
list of `{field, before, after, item, basis}`; `before` is the value in the half file, `after` the merged value, so entries with
before = after record a confirmation or an item-6 keep. Agreement under v1.1 is not recomputed (v1.2 disclosure).

## Readings chosen

**Item 1. Argmax or greedy stated outside the experiment section.** A statement counts, in B-13 order, when it is (a) in the
experiment section or a caption for the F1 experiment, (b) in a hyperparameter table, or (c) in the paper's own method-level
definition of the sampler it evaluates by name, wherever that definition sits (method section, algorithm box, or an ablation
subsection that defines the method's own sampling step), provided it leaves no value parameter free (A-3(b), B-14). It does not
count when it sits in preliminaries, background or related work describing an earlier or generic sampler, even if the method
later reuses that sampler (B-14, last clause), nor when it is a theorem or analysis about a decoding rule (A-7). Reason: B-14
names background and preliminaries explicitly and admits method-level definitions only through A-3(b); the location of a
definition is not the test, its subject is. Result: the halves already agree. Half 1 coded C at 5, 9, 46 and 62 (argmax only
in preliminaries), as half 2 did at 139 (and 134). Half 2's A at 152 rests on Sec 4.4.3, which defines TiDAR's own
verification token ("we propose to apply an aggregate function ... before sampling the token as arg max"), so it is case (c),
like half 1's A at 1, 37, 43 and 54. Rank 129 is A from an experiment-level statement (App C.1), not A-3(b); rank 154 is C
(the argmax sentence describes the training-time Teacher, B-16), not A. No cell changed.

**Item 2. Process-level continuous samplers with guidance.** The A-3 clause stands: tau-leaping, Euler CTMC, ODE and SDE
integration (Euler/flow ODE, DDIM, DPM-Solver, SDE samplers) have a stated plain base rule only with an explicit statement that
no temperature or truncation is applied. B-14 is tagged [literal] and makes A-3 checkable item by item; it does not mention, and
so does not repeal, the process-level clause ("Fields and rules not mentioned are unchanged"). With guidance stated and no such
statement, B-21 gives G+NS. Ancestral samplers (DDPM, MDLM or multinomial reverse steps) are not process-level; for them B-14(1)
is met by the named ancestral sampler and B-14(3) by a complete settings list, so G stands. Result: 91, 114, 120 and 141 stay
G+NS; 126 and 143 stay G. Half 1 has no equivalent row: its process-level rows are NS without guidance (2, 58 with omega = 0,
64) or already G+NS for another reason (29, 72). No cell changed.

**Item 3. Rank-then-sample.** B-15 governs: a position score that reads the model's predicted distribution (confidence,
top-token probability, margin, entropy, threshold) with a stated sampled value is S (temperature in T). v1's "rank-then-sample"
under U is read as ranking that does not read the predicted distribution (random, fixed or scheduled order, or a separate
planner), which B-15's last sentence keeps out of the value-rule letters. Reason: v1.2 is the later and more specific rule and
defines the score class explicitly. Result: 103 stays T+S. A scan of every eligible row without S, C or A found no other row
that ranks positions by the predicted distribution and samples the value (57 ranks by hidden-state query relevance, which
B-15 excludes); rows 10, 12, 14, 22, 35 and 164 already carry S. No cell changed.

**Item 4. B-24 and the F1 model.** B-24 is read literally: the sweep must be on the F1 benchmark or dataset (any
generated-sample metric) and, by B-23, of the paper's own method; it does not require the F1 backbone or model size. For an
empirical study with no method of its own, the F1 system stands in for "the paper's own method". Reason: B-24 names the task and
loosens the metric but is silent on the model; requiring the F1 model would add a condition the text does not contain. Result:
76 stays F4 = no, now on the task criterion alone (Tables 8-9 sweep HumanEval, MBPP, LiveCodeBench and HumanEval-X, not MBPP+;
Sec 4.3.2). Half 2 has no row where the F1-model clause decides F4; 148 (sweep on the paper's own Uniform 3B/10B models,
same GSM8K task, F1 row Masking 3B) stays partial under the literal reading. No cell changed.

**Item 5. Abstract gains as F1.** A gain, ratio or retention figure in the abstract ("improves by up to X%", "+15.0 points",
"99.55% of original performance") is an F1 value when (i) it is computed from a generated-sample metric (B-10) of the paper's own
method, or of the studied system in a B-2 analysis paper; (ii) it is on an in-scope task (B-9); and (iii) the abstract, or the
text or table it summarises, identifies one setting: a benchmark (or a stated average over named benchmarks) and a
configuration; for "up to" claims, the cell where the maximum occurs. If (iii) fails, the claim is skipped and the next
abstract number is tried, else B-11. The value is recorded as printed (B-27). Reason: v1 defines F1 as "the first quantitative
result ... in the abstract", A-2 skips only speed-only and likelihood-only numbers, and B-10's exclusion list does not name
gains; condition (iii) is needed because F2 to F6 are coded for the F1 setting. Both halves already accepted gains (half 1 at
4, 6, 15, 20, 21, 31, 88, 96; half 2 at 104, 109, 115, 125, 147, 161, 176). Condition (iii) fails at 125 ("2%-7% in certain
cases") and 147 ("up to 15%", which matches no single Table 1 cell; Sec 4 says "roughly 5-15% ... on most reasoning and coding
tasks"), so their F1 moved to Table 1 cells; the other rows meet it (176 resolves to MATH500 static, 78.5 / 74.0 = 1.061).
Agreed gain cells at 4, 20, 88, 89 and 96 stand under item 6; 89 is a text-quoted gain from a figure, not an abstract claim,
and is flagged but not changed because both coders agreed and neither note shows a v1.2 trigger.

**Item 6. Reopened agreed cells.** A cell both coders agreed on (values equal after B-27 normalisation, compared against the
coders' own rows) keeps its adjudicated change only if (a) either coder's own notes, F2_detail or location field show the
trigger of a v1.2 rule, or (b) the change uses a v1.2 letter or convention that did not exist under v1.1 (C, or +NS) and that
the agreed value cannot express, and the change is correct under v1.2. A change that follows mechanically from a kept change
(F5 = NA after F4 = no, an exclusion code after eligibility, F6 after a new G) is kept with it. F0 header reads and B-27
couplings of ineligible rows are listed separately as mechanical and not counted as reopened decisions. Every reopened cell in
both halves met the standard, so none was restored.

## Changed cells

9 cells changed, all F1 description fields in three rows; no eligible, exclusion, F2, F3, F4, F5 or F6 cell changed.

| rank | field | before | after | item |
|---|---|---|---|---|
| 125 | F1_value | surpasses real data by 2%-7% in certain cases | 0.906 | 5 |
| 125 | F1_task | synthetic structured data generation (tabular, code, tools) evaluated by downstream task performance | synthetic tabular data generation, Adult dataset, DiffLM (downstream XGBoost MLE) | 5 |
| 125 | F1_metric | downstream performance relative to real data | MLE (AUC of XGBoost trained on synthetic data) | 5 |
| 125 | F1_location | Abstract (Table 1 tabular MLE) | Table 1, DiffLM (ours) row, Adult MLE column (abstract "2%-7% in certain cases" not tied to one setting) | 5 |
| 147 | F1_value | up to 15% | 84.15 | 5 |
| 147 | F1_task | reasoning and coding benchmarks (GSM8K, MATH, HumanEval, MBPP), FReDA-4B Best-of-N vs 7-8B diffusion base models | GSM8K (4-shot), FReDA-4B (Best-of-N refinement) | 5 |
| 147 | F1_metric | absolute accuracy gain | accuracy (%) | 5 |
| 147 | F1_location | Abstract (Table 1) | Table 1, FReDA-4B (Best-of-N) row, GSM8K (4) column (abstract "up to 15%" not tied to one benchmark; 1.5-1.8x speed-only) | 5 |
| 176 | F1_task | mathematical reasoning benchmarks, TraDo-8B-Instruct (TraceRL on SDAR-8B) | MATH500, TraDo-8B-Instruct (TraceRL on SDAR-8B), static sampling | 5 |

F2 to F6 at 125 and 147 were already coded for the new F1 setting (125: tabular outputs with JSON validity filtering, M+NS;
147: Best-of-N on GSM8K, A+M, F4 yes from Fig 2), so they stand. The 125 and 147 F1 values are now coder A's (0.906) and
coder B's (84.15) choices respectively.

## Reopened agreed cells (item 6)

### Half 1 (ranks 1-88): 11 reopened cells (10 decisions, 1 couplings); kept 11, restored 0

| rank | field | agreed | final | verdict | trigger or basis |
|---|---|---|---|---|---|
| 9 | F2_codes | A | C | keep | A's note: greedy only in preliminaries, borderline A-3 (B-14); C is a v1.2 letter NS/A cannot express |
| 20 | F2_codes | T+P | T+P+S | keep | A's F2_detail: confidence by top-prob margin (LLaDA) or negative entropy (Dream) = B-15 trigger; sampled token stated, so S |
| 29 | F2_codes | G | G+NS | keep | A's note: no temperature, steps or CFG statement for the multimodal runs; +NS is a v1.2 convention G cannot express (B-21) |
| 41 | F2_codes | G | G+M+NS | keep | A's detail: FK-Steering with 4 particles (B-19 resampling = M, external reward = G) and base unmasking rule not stated (+NS, B-21) |
| 44 | F1_value | 70.16 | 68.51 | keep | A's location note: 'best own row' = the v1/A-2 row conflict B-11 settles (first row unless plain vs guided/best-of) |
| 51 | F2_codes | NS | S | keep | A's note: corrector updates only tokens below a 0.1 probability threshold = B-15 threshold trigger with stated resampled value (S) |
| 72 | F2_codes | G | G+NS | keep | A's detail: sampling rule of the AR decoder not stated; +NS is a v1.2 convention G cannot express (B-21) |
| 75 | F2_codes | A | A+G | keep | A's note: DFA/NFA hard constraint 'not coded as G' = B-20 trigger (hard constraint is G) |
| 76 | F4 | yes | no | keep | A's F4 note: Mercury not included in the sweep; Tables 8-9 omit MBPP+ (B-23/B-24, item 4) |
| 76 | F5 | not stated | NA | keep (coupling) | B-25 coupling: follows the kept F4 = no |
| 80 | F2_codes | NS | C | keep | both coders' details: confidence threshold 0.9, token rule unstated = the disclosure's own B-15 example; C is new in v1.2 |

### Half 2 (ranks 89-176): 34 reopened cells (27 decisions, 7 couplings); kept 34, restored 0

| rank | field | agreed | final | verdict | trigger or basis |
|---|---|---|---|---|---|
| 99 | F5 | co-varied | not stated | keep | both coders quote 'Selection is performed independently inside each denoising budget' = B-25 trigger (rank 99 class): a procedure applied identically at every budget is not co-varied |
| 99 | F6 | co-varied | not stated | keep | same B-25 trigger as F5 |
| 101 | F2_codes | NS | C | keep | both details: confidence-based sampling per Dream, token rule unstated = B-15; C is new in v1.2 |
| 103 | F2_codes | T | T+S | keep | both details: TPP ranks positions by top-token probability then samples = B-15 trigger (position score reads the predicted distribution, value sampled: S; item 3) |
| 109 | F4 | yes | no | keep | B's F4 note: Table 2 NFE changes with generation length and prints speed-ups (B-23), Table 3 is GSM8K (B-24); F1 itself was disputed (A GSM8K, B HumanEval), so the agreed 'yes' rested on different tasks |
| 109 | F5 | not stated | NA | keep (coupling) | B-25 coupling: follows the kept F4 = no |
| 110 | F2_codes | NS | C | keep | both details: low-confidence remasking, temperature unstated ('cannot be split into A or S') = B-15; C new in v1.2 |
| 113 | F2_codes | NS | C | keep | both details: 0.9 confidence-based sampling threshold, value rule unstated = B-15; C new in v1.2 |
| 114 | F2_codes | G | G+NS | keep | no note trigger; +NS is a v1.2 convention that agreed G cannot express, and under item 2 (A-3 process-level clause) the DDIM base rule is unstated |
| 115 | F2_codes | NS | C | keep | both details: confidence-based parallel decoding (0.95), value rule unstated = B-15; C new in v1.2 |
| 117 | F2_codes | NS | C | keep | both details: Fast-dLLM confidence-threshold acceptance, no temperature/argmax statement = B-15; C new in v1.2 |
| 120 | F2_codes | G | G+NS | keep | no note trigger; +NS is a v1.2 convention that agreed G cannot express, and under item 2 the DPM-Solver (ODE) base rule is unstated |
| 122 | F2_codes | NS | C | keep | both details: confidence-threshold (0.9) unmasking, sampling of values not stated = B-15; C new in v1.2 |
| 128 | eligible | yes | no | keep | both coders' notes: eligibility borderline, output is synthetic token sequences, not natural language = B-3 trigger |
| 128 | exclusion_code | NA | X1 | keep (coupling) | B-3/B-6/B-8: follows the kept eligibility change |
| 129 | F4 | yes | no | keep | B's F4 note lists sweeps on HumanEval, MBPP, MATH500 while B's own F1 is GSM8K = B-24 trigger; F1 was disputed (A MMLU, B GSM8K 0.8B; final GSM8K 2B) |
| 129 | F5 | not stated | NA | keep (coupling) | B-25 coupling: follows the kept F4 = no |
| 133 | F2_codes | NS | C | keep | both details: confidence-based semi-AR decoding, evaluation temperature unstated = B-15; C new in v1.2 |
| 140 | F2_codes | NS | C | keep | both details: token 'by argmax or the model's configured stochastic decoding rule', unstated for Table 1 = B-15; C new in v1.2 |
| 141 | F2_codes | G | G+NS | keep | no note trigger; +NS is a v1.2 convention that agreed G cannot express, and under item 2 the SDE (process-level) base rule is unstated |
| 148 | F2_codes | NS | C | keep | both details: confidence heuristic picks positions, committed value (argmax vs sample) unstated = B-15; C new in v1.2 |
| 152 | F4 | yes | no | keep | B's note: tokens-per-NFE varies across separately trained block sizes rather than a step sweep = B-24 trigger |
| 152 | F5 | not stated | NA | keep (coupling) | B-25 coupling: follows the kept F4 = no |
| 155 | F1_value | 34.8 | 49.3 (baseline 44.9) | keep | both coders note the text quotes BBH 44.9 to 49.3 = B-11 'row/metric the text quotes' trigger |
| 155 | F2_codes | A | C | keep | both notes: greedy stated for code benchmarks only, BBH rule unstated; BBH commits high-confidence tokens = B-15; C new in v1.2 |
| 156 | F2_codes | G | G+NS | keep | both details: value rule (argmax vs sampled) not stated; +NS is a v1.2 convention G cannot express (B-21) |
| 163 | F2_codes | A | A+G | keep | B's note: 'Grammar-constraint filtering is not one of the F2 letters' = B-20 trigger (per-step hard constraint is G) |
| 163 | F6 | NA | stated | keep (coupling) | A-9/B-25 coupling: F2 now has G and F4 = yes; Sec 5 "All constrained methods use the same task-specific grammars" while only steps vary |
| 165 | eligible | yes | no | keep | both coders' notes: theory on a generic discrete state space, text only as motivation, eligibility borderline = B-3 trigger |
| 165 | exclusion_code | NA | X1 | keep (coupling) | B-3/B-6/B-8: follows the kept eligibility change |
| 166 | F2_codes | G | G+M+NS | keep | both details: reward-based MTM selection among proposals (B-19: M with G) and base token temperature not stated (+NS, B-21) |
| 166 | F4 | yes | no | keep | both F4 notes: NFE axis is IterRef iterations k and particles N with denoising steps fixed = B-24 trigger |
| 166 | F5 | not stated | NA | keep (coupling) | B-25 coupling: follows the kept F4 = no |
| 172 | F1_value | 22.43 | 73.23% | keep | B's F1 task note '(image branch)' shows the F1 came from the out-of-scope image component = B-9 trigger (text branch is the eligible component, B-7) |

Half 1's own count (11) matches. Half 2's notes report 39 "neither" cells outside the disagreement list; that figure also
counts cells where the coders disagreed (F1 choices at 116, 129, 147; F4_location) and the F0 coupling at 123, so the agreed
cells it reopened are the 34 above. Three of them (114, 120, 141) have no trigger in the coders' notes and are kept under
clause (b): +NS is new in v1.2, agreed G cannot express "guided, base rule unstated", and item 2 makes +NS correct there.

### Mechanical changes to agreed cells (not counted above)

| rank | field | agreed | final | reason |
|---|---|---|---|---|
| 21 | F0_version | NA | v2 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 24 | F0_version | NA | v1 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 26 | F0_version | NA | v2 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 27 | F0_version | NA | v1 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 28 | F0_version | NA | v1 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 34 | F0_version | NA | v3 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 36 | F0_version | NA | v3 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 37 | F0_version | NA | v2 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 38 | F0_version | NA | v1 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 39 | F0_version | NA | v1 | F0 read from the arXiv header; eligibility (disputed) resolved to yes |
| 128 | F0_version | v2 | NA | B-27 coupling: row ineligible |
| 128 | F1_value | 29 | NA | B-27 coupling: row ineligible |
| 128 | F3 | no | NA | B-27 coupling: row ineligible |
| 128 | F4 | yes | NA | B-27 coupling: row ineligible |
| 128 | F5 | stated | NA | B-27 coupling: row ineligible |
| 151 | F0_version | v1 | NA | B-27 coupling: row ineligible |
| 165 | F0_version | v3 | NA | B-27 coupling: row ineligible |
| 169 | F0_version | v1 | NA | B-27 coupling: row ineligible |

Totals: half 1 10, half 2 8; all kept.

## Confirmations logged without a change

Item 1: 5, 46, 62, 129, 139, 152, 154 (9 is logged under item 6). Item 2: 91, 126, 143 (114, 120, 141 under item 6). Item 3: 103
(under item 6). Item 4: 76 (also item 6), 148. Item 5: 6, 15, 31, 104, 109, 115, 161 (condition (iii) met).

## Merged file summary (computed from `census-random-final.jsonl`)

Rows 176: eligible yes 167, no 5, NA (NO_TEXT) 4. Among eligible rows F1 = NA 14, QL 1; F2 denominator 153.
Non-plain yes 97, no 6, unknown 50; base rule not determinable (NS or +NS) 65.
F3 yes 28 / no 124; F4 yes 49, partial 6, no 97; F5 among sweeps stated 20, not stated 35, co-varied 0.
These equal the sums of the two halves' final rows, because no F2 to F6 cell changed in harmonisation.

## Flags for the orchestrator

- 89: F1 is a gain quoted in the text about a figure (abstract has no number); B-11 would point to a figure cell. Agreed by
  both coders, no v1.2 trigger in their notes, so it stands under item 6.
- Item 5 makes F1_value a mix of levels and gains: 15 rows carry a gain, ratio or retention figure (4, 6, 15, 20, 21, 31, 88,
  89, 96, 104, 109, 113, 115, 161, 176; 113 is a retention column of its table). F1_value is descriptive and no denominator
  uses it, but any report of headline values should separate the two.
- Averages over several benchmarks as F1 (15, 21, 104, 115): B-24 does not say whether a sweep on one member benchmark is "on
  the F1 task". No row turns on it here (all four have F4 = no with no member-benchmark sweep recorded), but v1.2 is silent.
- Item 2 relies on the A-3 process-level clause surviving v1.2; if the orchestrator reads B-14 as replacing it, 91, 114,
  120 and 141 would become G if each has a settings list naming no truncation (the coders' details suggest one at 114 and
  120; not checked in the papers at 91, 114, 120 or 141).
