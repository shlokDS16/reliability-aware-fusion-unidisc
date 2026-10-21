```yaml
agent: gate-auditor
date: 2026-10-21
brief: Re-verify every census number in Paper 1 against the raw adjudicated rows (census-random-final.jsonl) and census-result-v2.md, before the \aud tags and the 06-census.tex line 8 to-do are removed
sources_examined:
  - research/review/census/census-random-final.jsonl (176 rows; last commit 8dd2af3, clean in git status)
  - research/review/census/coder-A-claude-*.jsonl, coder-B.jsonl, coder-B-claude-*.jsonl
  - research/review/census/census-order.csv; research/review/screening/records.jsonl, screener-A/, screener-B/
  - research/review/census/harmonisation-notes.md; adjudication-notes-r001-r088.md; adjudication-notes-r089-r176.md
  - research/review/coverage/census-result-v2.md (commit 8dd2af3); census-codebook-v1.2.md (rule headings)
  - analysis/census/summary_random.py, agreement_random.py, gap_rulings.py and their committed logs
  - paper/review/main.tex (abstract and its comments), sections/01-introduction.tex, 02-method.tex,
    06-census.tex, 07-error-budget.tex, 08-open-problems.tex, 10-limitations.tex, 11-conclusion.tex,
    05-rq-evidence.tex (line 41), supplement.tex S3 (lines 152-238), figures/fig04-census.log, scripts/fig04_census.py
coverage: >
  Every census number in the compiled text, tables, figure description and the main.tex abstract
  (compiled and commented variants). Not covered: the codebook prose itself, the per-paper correctness
  of adjudicated cells (no paper re-read), the PDF build, and process facts that are not numbers
  (model identifiers; supplement.tex line 179 to-do is outside this brief).
claims:
  - statement: All census counts, proportions and Wilson intervals in the manuscript equal values recomputed from census-random-final.jsonl
    status: supported
    evidence: scratchpad reruns of summary_random.py plus an independent re-implementation (section 2)
    level: E4
    confidence: 0.97
  - statement: The agreement table (raw agreement, kappa, n) equals values recomputed from the coder files
    status: supported
    evidence: agreement_random.py rerun (all ranks and 15 read failures excluded) plus an independent kappa implementation
    level: E4
    confidence: 0.97
  - statement: The gap-ruling table and the B-3/B-4/B-6/B-8 counts equal gap_rulings.py output on the final rows
    status: supported
    evidence: gap_rulings.py rerun, byte-identical to analysis/census/gap-rulings.log
    level: E4
    confidence: 0.97
  - statement: The sensitivity column (agreed cells restored) equals the recomputation
    status: supported
    evidence: summary_random.py sensitivity block; reopened-cell counts recomputed from harmonisation entries
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - Whether adjudicated cells are correct against the papers (not re-read; outside a number audit).
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Census number re-verification, Paper 1 (2026-10-21)

## Verdict: PASS (0 mismatches)

All census numbers in the manuscript match values I recomputed from the raw adjudicated rows
(`research/review/census/census-random-final.jsonl`) and the coder files. They also match
`research/review/coverage/census-result-v2.md` (commit 8dd2af3). The census inputs have not changed since that
commit: `git status` shows no change to `research/review/census/` or to census-result-v2.md.

**The `\aud` tags can be removed.** They are at 01-introduction.tex:58, 06-census.tex:65 and 66,
07-error-budget.tex:110, 08-open-problems.tex:30 and 59, and 11-conclusion.tex:5. The tag also appears in
the commented 237-word abstract at main.tex:72. The **06-census.tex line 8 to-do** can also be removed,
together with the header comment at 06-census.tex:3-4 ("All numbers in this section are \aud until ...").
The `\aud` macro definitions (main.tex:32-33, supplement.tex:31) can be dropped once nothing uses them.
Only the user can waive criteria, and this audit waives none. Nothing failed.

## 1. Method

- Copies of `analysis/census/summary_random.py`, `agreement_random.py` and `gap_rulings.py` were run with
  `python -I` from the session scratchpad. Their repository root was hard-set and all outputs (including the
  disagreement CSV, via `--out`) went to the scratchpad. No repository file was written except this report.
- `analysis/census/summary.py`, named in the brief, is the obsolete v1 script. It reads
  `coverage/census-final.csv` (the 47-model purposive pilot), not the random sample, so it is not a source
  for any number in the manuscript. The random-sample counts come from `summary_random.py`, which I ran.
- Independent recomputation: I wrote separate inline code (not the repository scripts) for the
  denominators, class counts, letters, F3 to F6, Wilson intervals (z = 1.959964, standard formula),
  Cohen's kappa (from the full confusion matrix), the 150th-eligible rank, reopened agreed cells,
  adjudication outcomes (A / B / neither) over the 158 disagreements, and the census pool.
- The census pool was rebuilt from `screening/records.jsonl` and both screeners' batch decisions with the
  filter and seed in `tools/census_sample.py`. It gives 1106 records, and the shuffled order reproduces
  `census-order.csv` row for row.

## 2. Recomputed values

**Script reruns against committed logs.** `summary_random.py` output is identical to
`summary-random.log`, `gap_rulings.py` to `gap-rulings.log`, and `agreement_random.py` to
`agreement-random.log`. The run excluding ranks 1, 21, 24, 26, 34, 37, 42, 43, 59, 64, 82, 83, 84, 85
and 87 reproduces every table row of `agreement-random-excl-readfail.log`. That committed log carries one
duplicated row ("non-plain value rule (yes/no/unknown)" printed twice); this is cosmetic and changes no
number.

**Final rows.**

| Quantity | Recomputed |
|---|---|
| Ranks / no text | 176 / 4 (ranks 23, 33, 90, 144) |
| Eligible of 172 with text | 167 (X1: 123, 128, 151, 165; X0: 169) |
| F1 NA / QL / metric | 14 / 1 (rank 71, F1_value QL, F2 T) / 152 |
| Value-rule denominator | 153 |
| Non-plain or NS | 147/153 = 0.9608 [0.9171, 0.9819] |
| Stated non-plain | 97/153 = 0.6340 [0.5552, 0.7062] |
| U | 6 (ranks 3, 45, 49, 112, 124, 153) |
| NS | 50 (50/153 = 0.327, "about a third") |
| Letters | A 33, C 20, G 22, M 12, P 12, S 12, T 14 |
| +NS | 15 (G+NS 11, G+M+NS 3, M+NS 1) |
| F3 | 28/152 = 0.1842 [0.1306, 0.2534] |
| F4 yes or partial | 55/152 (49 + 6) = 0.3618 [0.2897, 0.4408] |
| F5 stated among sweeps | 20/55 (35 not stated) = 0.3636 [0.2493, 0.4958] |
| 150th eligible under final eligibility | rank 157 (176 - 157 = 19 extra ranks) |

**Sensitivity (agreed cells restored).** Non-plain or NS 148/154 = 0.961 [0.918, 0.982]. Stated
non-plain 86/154 = 0.558 [0.480, 0.634]. U 6/154. NS 62/154. F3 28/153 = 0.183 [0.130, 0.252]. F4
61/153 = 0.399 [0.325, 0.478]. F5 21/61 = 0.344 [0.237, 0.470].

**Reopened agreed cells.** From the "Item 6 KEEP" harmonisation entries in the final rows: 45 in total,
of which 3 are F1_value (ranks 44, 155, 172) and 42 are count-relevant. 25 of the 45 are F2 codes, and 20
of those 25 end in C or +NS (9, 29, 41, 72, 80, 101, 110, 113, 114, 115, 117, 120, 122, 133, 140, 141,
148, 155, 156, 166). Ranks 91, 114, 120 and 141 are G+NS.

**Agreement (independent kappa).**

| Comparison | Raw | kappa | n |
|---|---|---|---|
| Eligible | 0.872 | 0.054 | 172 |
| Eligible, 15 read failures excluded | 0.955 | 0.202 | 157 |
| Non-plain (yes/no/unknown) | 0.812 | 0.648 | 149 |
| Non-plain, both determinable | 0.968 | 0.734 | 62 |
| Class A | 0.984 | 0.967 | 62 |
| Class T | 0.968 | 0.870 | 62 |
| Class P | 0.984 | 0.932 | 62 |
| Class S | 0.919 | 0.402 | 62 |
| Class G | 0.984 | 0.960 | 62 |
| Class M | 0.968 | 0.815 | 62 |
| F3 | 0.926 | 0.826 | 149 |
| F4 | 0.832 | 0.722 | 149 |
| F5 | 0.832 | 0.702 | 149 |
| F6 | 0.973 | 0.682 | 149 |

The determinable row (0.83, 0.65, 149) was checked by script rerun. For F6, 141 of the 149 pairs are
NA/NA. There are 22 eligibility disagreements: 20 are A yes / B no, and 15 of those are Codex read
failures (X8 in 12, X4 at 26 and 42, none at 84). The other 5 are X7 (27, 28, 36, 38, 39). The
disagreement CSV has 158 rows over 88 ranks.

**Adjudication outcomes.** The final values settle the 158 disagreements as follows: coder A 73, coder B
66, neither 19. By half: ranks 1-88 give 59 / 31 / 9; ranks 89-176 give 14 / 35 / 10, which matches the
notes (12 + 2, 27 + 8, 9 + 1).

**Gap rulings** (rerun output in brackets: rows in F2 denominator, non-plain, NS, U):

| Ruling | Recomputed |
|---|---|
| B-15 | 40 (39 / 0 / 1) |
| B-21 | 19 (18 / 1 / 0) |
| B-24 | 18 (12 / 6 / 0) |
| B-10 | 15 ranks, 12 in the denominator (7 / 5 / 0) |
| B-9 | 14 (7 / 5 / 2) |
| B-19 | 6 (6 / 0 / 0) |
| B-13 | 3 (3 / 0 / 0) |
| B-17 | 3 (3 / 0 / 0) |
| B-22 | 1 (1 / 0 / 0) |
| B-18 | 0 |

The eligibility rulings B-3, B-4, B-6 and B-8 decided 2, 3, 3 and 4 ranks.

**Other.** 15 rows carry F1 as a gain, ratio or retention figure (harmonisation-notes "Flags": 4, 6, 15,
20, 21, 31, 88, 89, 96, 104, 109, 113, 115, 161, 176). Coder B has 86 Codex rows for ranks 1-91 (19 and
79 failed; 23, 33 and 90 have no text) and 87 Claude Opus rows (92-176 plus 19 and 79). Coder A has 176
rows. `figures/fig04-census.log` matches every value above, and the script asserts its numbers against
the summary log string by string.

## 3. Checks of the manuscript text (all match)

| Location | Text | Check |
|---|---|---|
| main.tex:73 (compiled abstract) | 147 of 153 codable papers | match |
| main.tex:70, 72 (comments) | 147 of 153; random sample of 176 | match |
| 01-introduction.tex:58 | 176 of 1106; 167 eligible; 153 (152 + 1 samples only); 147, 96%, 92 to 98; 28 of 152; 55; 20 | match |
| 01-introduction.tex:73 | frame wording | consistent with tools/census_sample.py |
| 02-method.tex:130 | 1,106; seed 20261015; ranks 1-176; 4 no text, 5 ineligible, 167 eligible | match |
| 06-census.tex:18-22 | 172; kappa 0.82 to 0.97 (A, T, P, G, M); 62; S 0.40; 149, 0.65, 0.65; 0.05 at 0.87; 20 of 22, 15 of 20; 0.96, 0.20; F6 0.97, 141 of 149 | match |
| 06-census.tex:32-46 (Table tab:census-agree) | all 15 rows | match |
| 06-census.tex:54-55 | 176, 4, 167 of 172, X1 4, X0 1, 14, one, 152; 153; 1106 | match |
| 06-census.tex:58 (caption) | 20 coded C, 15 +NS | match |
| 06-census.tex:65-71 (Table tab:census-main) | every final and sensitivity cell | match |
| 06-census.tex:76-78 | 147/153, 96%, 92-98; 97, 50, 6; 28 (18%) of 152; 55 = 49 + 6; 20; letters | match |
| 06-census.tex:83, 85 (figure caption, description) | 153; 147/153, 97, 50, 6, 28/152, 55/152, 20/55; 33 down to 12 | match |
| 06-census.tex:90 | 148/154 = 0.961; 97 to 86 | match |
| 06-census.tex:95, 99, 106 | 50 of 153 (about a third), 6; 28; 1106 | match |
| 07-error-budget.tex:110 | 147 of 153; 55 of 152; 20; 28 of 152 | match |
| 08-open-problems.tex:30, 59 | 55 of 152, 20; 50 of 153 | match |
| 11-conclusion.tex:5 | 147 of 153 | match |
| supplement.tex:161-162 | 1106; 20261015; 150, 151 at 176; 15; rank 157; 19; ranks 23, 33, 90, 144 | match |
| supplement.tex:167 | 14; QL 1; 153; 152 | match |
| supplement.tex:177-178 | 176; 86 rows; 19, 79; 15 read failures among 1-88 | match |
| supplement.tex:182 | 172; 15; 158 | match |
| supplement.tex:185 | six readings; 73 / 66 / 19 = 158; 45 reopened; 114, 120, 141; 42 | match |
| supplement.tex:198-213 (Table tab:census-gap and caption) | all nine rows; B-10 15 ranks, 12 in count | match |
| supplement.tex:220-221, 224 | 45, 42, 25, 20; 148/154 = 0.961; 97 to 86; 39; 2, 3, 3, 4 | match |
| supplement.tex:229-236 | 1106; 15 read failures; fifteen F1 gain rows; ranks 91, 114, 120, 141; 19 extra ranks | match |
| 05-rq-evidence.tex:41, 10-limitations.tex:16 | no census numbers | n/a |

## 4. Mismatches

None.

## 5. Observations (not number mismatches; none blocks the gate)

1. **02-method.tex:149 (AI-use table).** The text says "B: Codex gpt-6-luna (ranks 1 to 91), Claude Opus
   (ranks 92 to 176)". Claude Opus also coded ranks 19 and 79. Optional fix: "Codex (ranks 1 to 91 except
   19 and 79), Claude Opus (ranks 92 to 176, 19 and 79)", which matches supplement.tex:177.
2. **supplement.tex:161.** "the primary coder's eligible count reached 150". census-result-v2.md says the
   stopping rule was coder B's count, and the paper never defines a "primary coder". Optional fix:
   "coder B's eligible count".
3. **Number format.** 02-method.tex:130 writes "1,106"; every other location writes "1106". Pick one style.
4. **B-10 labelling.** supplement.tex:174 calls B-10 a rule "that settles a gap", and the Table
   tab:census-gap caption calls it a "gap-filling ruling". Codebook v1.2 tags B-10 [literal]. The script
   includes B-10 "disclosed as a judgement call". Optional fix: add "and B-10, a judgement call" to the
   caption.
5. **Comment only.** The committed `analysis/census/agreement-random-excl-readfail.log` prints the
   non-plain row twice. This is cosmetic, and the rerun prints it once.

No ledger rows added. `research/progress.md` was not edited, because the brief made the worktree
read-only except for this report.
