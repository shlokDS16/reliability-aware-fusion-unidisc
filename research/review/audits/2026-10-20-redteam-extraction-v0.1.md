```yaml
agent: red-team
date: 2026-10-20
brief: adversarial review of extraction and quality-appraisal instrument v0.1 (Paper 1), as hostile CSUR referee and methods statistician
sources_examined:
  - research/CONTRACT.md
  - research/review/extraction/EXTRACTION-PLAN.md, extraction-schema.json, extractor-brief.md, OPEN-QUESTIONS.md
  - research/review/protocol.md (s1, s3 'Version rated', s4, s5, s6, s7, s10)
  - research/ledgers/decisions.jsonl rows D0005-D0011, D0015, D0020, D0021, D0030, D0032, D0034
  - research/review/evaluability-rubric.md; research/review/reliability/RESULTS.md
  - research/review/framework-v2.md; paper/review/OUTLINE.md; paper/review/sections/04-design-space.tex, 05-rq-evidence.tex
  - analysis/screening/quote_check.py (read in full; functions called on real texts)
  - analysis/screening/ft-t1/t1-decisions-all.jsonl (608 includes: ids, i1, nonlang_only)
  - research/sources/md/fulltext-pymupdf/ M12766 (Muddit, unified, ICLR 2026), M13195 (CONFLUX, unified, anonymous ICLR 2027 submission), M09530 (TrustLDM, benchmark), M03416 (DiffuseDef, method with w/o ablation table); first 6 kB of all 608 include texts scanned by regex
  - research/progress.md lines 268-269 (user decision 2026-10-16); research/review/fulltext/dispatch-log.jsonl (format only); tools/ directory listing
coverage: >
  Read the four instrument files in full and the protocol, ledger rows, rubric, reliability results, framework-v2,
  outline and section stubs listed above. Called quote_check.quote_status on real passages of M03416 and M12766 and on
  a synthetic six-row ablation table; scripted counts over the 608 include texts (sizes, anonymous submissions,
  GitHub links, lines starting with w/o); binomial, hypergeometric and Monte Carlo operating characteristics of the
  pilot rules (scratchpad scripts pilot_oc.py, oc2.py; not committed). NOT covered: census codebooks v1, v1.1, v1.2
  (not in the brief), so the block-F equivalence gate check was not done; framework-v1 lever table; criteria v1.6;
  ft_dispatch.py; no full read of any paper (sections read: abstracts, main tables, ablation tables). Deviation from
  my agent definition: the brief asks for a concrete fix per finding, so fixes are given; criticism is not softened
  for that reason. Severity scale: critical = blocks the gate (agent definition 'fatal').
claims:
  - statement: quote_check.py rejects quotes of the second and later rows of a w/o ablation table, and in tables wider than about six numeric columns no 6-40-word quote of a later row can pass.
    status: supported
    evidence: quote_status on M03416 Table 3 ('w/o diffusion denoising 57.1 58.4 47.7' -> negation_before); synthetic 6-column table, row 5 passes only from a 40-word quote starting at row 1
    level: E3
    confidence: 0.9
  - statement: 287 of the 608 screened include texts are anonymous double-blind submissions.
    status: supported
    evidence: regex 'Anonymous [Aa]uthor' in the first 6,000 characters of each fulltext-pymupdf/<id>.txt
    level: E3
    confidence: 0.85
  - statement: Under the plan's per-field rule (no field below 8 of 12), a block of 16 fields whose true agreement is 0.80 each fails with probability 0.70.
    status: supported
    evidence: binomial computation, scratchpad pilot_oc.py
    level: E3
    confidence: 0.95
  - statement: The pilot threshold for claim statuses (raw agreement 0.70, P7) sits at the level at which the suspended evaluability criterion failed (raw 42/62 = 0.68, kappa 0.33).
    status: supported
    evidence: reliability/RESULTS.md lines 13 and 18-19; EXTRACTION-PLAN.md s10.4 P7
    level: E2
    confidence: 0.9
competing_explanations:
  - The w/o rejections could be avoided by extractors who quote from the table top; true only for tables of at most about 40 words above the row.
unknowns:
  - real tokens and hours per extraction record (no pilot run); my numbers are inference from the screening figure
  - whether block F equals codebook v1.2 (codebook not read)
next_test: {hypothesis: "form v0.2 units are identified reproducibly", intervention: "two extractors on a stratified 30-record gate sample after the fixes below", primary_metric: "H and K unit identification F1 with lower 90 percent cluster-bootstrap bound", falsifier: "lower bound below 0.70 for K units", gpu_hours: 0}
```

# Red-team audit: extraction and appraisal instrument v0.1

Verdict: **do not draw the pilot.** Three critical findings block the gate: the evidence tool cannot
verify the ablation rows the form depends on, the unit definitions are not reproducible, and the
extraction scope contradicts a recorded user decision. Counts at the end.

Line references: PLAN = EXTRACTION-PLAN.md, BRIEF = extractor-brief.md, SCHEMA = extraction-schema.json,
OQ = OPEN-QUESTIONS.md, PROT = protocol.md, QC = analysis/screening/quote_check.py.

---

## Critical

### C1. The quote checker cannot verify ablation rows; the evidence rule is impossible for credited ablations
**Evidence.** QC 113-121: an occurrence is rejected if any of the 6 *letter* words before it in the same sentence
is a negation word; `_WORD` (QC 75) does not match digits, so numeric cells do not count toward the 6-word
window, and sentences end only at ". " (QC 72), which table lines rarely contain. "w/o", "without", "no" and
"none" are negation words (QC 51-55, 119). Tests on real text:
- M03416 Table 3: `w/o diffusion denoising 57.1 58.4 47.7` -> **negation_before** (the earlier `w/o ensembling`
  row label is within 6 letter words); `w/o diffusion denoising ... w/o adv training 80.3 80.9 80.5` ->
  negation_before; only a quote starting at the first w/o row passes.
- Synthetic table, 6 benchmark columns, rows `Ours` + 6 `w/o` rows: row 5 passes only with a quote that starts
  at row 1 or earlier (40 or 47 words); every shorter start fails. At 7 or more columns no quote of 40 words or
  fewer can pass (ex_validate is to enforce the 40-word cap, PLAN s11).
- 361 of 608 include texts contain a line that starts with w/o, W/o, without, "No " or "w/ " (scripted
  regex; an approximation of how many have such tables).
PLAN s9 runs quote_check.py "unchanged" and BRIEF E2 tells extractors to extend quotes back to the
negation, which for wide tables leads past the 40-word cap. Consequence: K units of class credited-other and
RQ3, and QA7a/b quotes, fail for a tool reason; P1 (95 percent first-pass acceptance, PLAN s10.4) fails for
the same reason, and the fallback "unverified, to EC" (PLAN s9) moves exactly the QA7 evidence into
unverified status.
**Rejection test.** Run quote_check on the pilot's K-unit quotes: if more than 5 percent are negation_before on
table text, P1 cannot be met by any extractor.
**Fix.** Before the pilot, a table-aware rule in a versioned quote_check (v1.7) with self-tests: the
negation window stops at a line break that follows a numeric cell, or the window ignores negations that
begin a row label different from the quoted row; plus a validator rule that the quoted row label must be the
first token run of the cell quote. Re-run the 38 self-tests and add the M03416 cases.

### C2. Unit (H and K) definitions are not reproducible, so P6 and every RQ2-RQ5 table rest on sand
**Evidence.**
1. *Five overlapping generators, no deduplication.* H units come from abstract numbers (PLAN s5.1 item 1),
   main-table default rows (item 2), claims ("create H or K units as needed", BRIEF 274-275) and K units from
   RQ classes (s5.2), credited ablations, and the main comparison (BRIEF 121-124). An abstract number that is
   also a main-table cell gets two units with different alignment keys (`where` = abstract vs Table n, PLAN s8);
   no rule says it is one unit.
2. *H has no value type.* CONFLUX (M13195) abstract: "improves MMLU by 7.56 points ... comparable FID (3.67
   versus 3.09) ... fully trainable 0.6B backbone". Under BRIEF 315-316 ("every quantitative result in the
   abstract, any metric and model ... one unit per number") these become H units with metric MMLU and value
   7.56 (a difference), a baseline's FID 3.09, and a size 0.6B. SCHEMA h_unit (218-241) has no field for
   level / difference / ratio / size, nor for the reference arm, so any script reads 7.56 as an MMLU score.
3. *Benchmark and analysis papers.* G1 (BRIEF 41-43) makes every evaluated model "own method"; the main-table
   rule takes "every cell of the final method's default row". TrustLDM (M09530) Table 1 has 4 models x 6
   context settings x 2 subsets = 48 cells, every row "own", no "default row": the rule yields 0 or 48 units
   depending on the reader.
4. *RQ2-vs-ar with several baselines.* BRIEF 328-330 gives "levels: the two arms", while a K unit is "one
   factor ... two or more levels". Muddit (M12766) Table 1 has three AR models (LWM 7B, SEED-X 17B,
   Chameleon 7B) and seven GenEval columns: one unit with 4 levels, 3 units of 2 levels, or 21 units are all
   compliant readings. Whether Show-O (AR text, discrete-diffusion image) or Transfusion counts as an
   "autoregressive baseline" in a text-to-image table is undefined.
5. *The K alignment key uses free text* ("K03 normalised", PLAN s8), with no normalisation algorithm, so unit
   identification F1 (P6) is not a defined statistic.
6. *No comparison-group id.* One ablation scored on three benchmarks (Muddit Table 4: GenEval, MS-COCO,
   VQAv2) is three unrelated K units; nothing ties them for RQ5 ("a metric for each of the two task kinds")
   or for dependence in s7.
**Rejection test.** Two extractors on Muddit, CONFLUX and TrustLDM under v0.1: if K identification F1 is below
0.70 on these three, P6 is unmeetable by construction.
**Fix.** One generator per unit type with an explicit precedence and dedup rule (a number is one unit; an
abstract occurrence is a second `source` on the same unit); add `value_type` {level, difference, ratio,
size, other} and `reference_arm`; a benchmark/analysis rule (e.g. the abstract's first-named model, or the
F1 row only, plus K units for the paper's stated comparisons); a multi-baseline rule for RQ2 (one unit per
AR baseline row, or all AR rows as levels, pick one) and a definition of "autoregressive baseline" for
unified models; `group_id` linking units from the same arms; an alignment key built only from fields with
controlled vocabularies (table id, row label, column label as printed plus normalised benchmark id).

### C3. Extraction scope contradicts the user's recorded decision; the pilot and tools are built for the wrong default
**Evidence.** research/progress.md 268-269: "User decisions 2026-10-16: full-text screen ALL records, extract
RQ data on a stratified sample + all multimodal". PLAN s1 (67-70) takes all 608 includes as the population
and PLAN s7 (352) has EA extract "every included study under the frozen form"; OQ-01 recommends a hybrid (b)
but the plan implements the full form provisionally. The user's line is not in the ledger, which is a ledger
gap, not a licence to override it. The scope fixes the pilot's strata, which blocks the pilot tests, the P8
workload rule, ER's 10 percent frame and the cost estimate (see M17).
**Rejection test.** If the user confirms the 2026-10-16 instruction, every production design choice in PLAN
s7-s10 changes.
**Fix.** Enter the scope decision row (OQ-01) before any tool is built: which blocks go to all studies,
which to a sample, the strata, the size, the seed and the sampling weights. Draw the pilot from the same
strata.

---

## Major

### M1. Pilot of 12 cannot run the stop/revise rule (statistics)
- *Per-field rule is a multiplicity trap.* P3 "no single field below 8 of 12" (PLAN s10.4). P(field at or below
  7/12) is 0.073 at true agreement 0.80, 0.024 at 0.85, 0.004 at 0.90. Over the 16 study and design categorical
  fields: false fail 0.70 at 0.80, 0.32 at 0.85, 0.07 at 0.90; over 25 fields 0.85, 0.45, 0.10. A field with true
  agreement 0.60 still passes with probability 0.44. P4 over 9 QA items: false fail 0.49 at 0.80, 0.20 at 0.85.
  (pilot_oc.py.)
- *"Pooled kappa" is undefined.* Same simulated data (16 fields, mixed prevalence, raw agreement 0.75): pooled
  kappa 0.53 if category labels are shared across fields, 0.74 if labels are namespaced by field, mean of
  per-field kappas 0.45 (oc2.py). P3 passes or fails depending on an unstated computation; with namespacing the
  "kappa at least 0.70 and raw at least 0.80" pair is nearly redundant.
- *P5.* F1 unit identical in 9 of 12: pass probability 0.49 at true 0.70, 0.65 at 0.75, 0.80 at 0.80. A
  coin-weighted gate.
- *Composition.* P(no i1 b/ab record in 12) = 0.331; expected 1.05 multimodal records (hypergeometric, 53 of
  608). D03, D06, D09, RQ5 K classes, QA6n/QA7n NA paths and theory/benchmark rules are untested in most draws.
- *NA inflation.* s10.3 reports per-field raw agreement "out of 12", which counts NA-NA as agreement; s8
  defines applicability as non-NA by either reader. The two definitions disagree.
- *Revision loop.* Revising only failing fields and re-testing them on a fresh 12 does not re-test fields the
  revision may have changed; with the false-fail rates above, fields are dropped by chance after round 2.
**Fix (design with numbers).** Two stages. Stage A, development, n = 12, purposive: 4 i1 b/ab, 2 benchmark or
analysis (title keywords as proxy), 2 from the top size decile (>133 kB), 4 random; no pass/fail, used to fix
rules. Stage B, gate, fresh stratified random n = 30: 20 from i1 a (split at the median text size), 10 from
i1 b/ab (weights 27.75 and 5.3 for pooled estimates); P(no multimodal) is then 0. Gate on the lower 90 percent
cluster-bootstrap bound of block raw agreement (and namespaced pooled kappa, computation written down) at 0.70;
in simulation at n = 30 and raw agreement 0.80 the 90 percent range is 0.74-0.85, at n = 12 0.72-0.89. Per
field: only fields with at least 15 applicable pairs are judged, flagged if at or below 11/15 (false flag
0.056 at true 0.90, detection 0.83 at true 0.65); fields with fewer pairs are "untested" and stay descriptive
until the production second reading supplies them. Cost: 60 extraction records plus about 30 EC records, about
the cost of the plan's worst case (three rounds of 12 = 36 double records) with a decisive operating
characteristic.

### M2. QA8 and the claim list bring back the suspended evaluability criterion with a lower bar
D0008 suspended the evaluability theme because the criterion failed (kappa 0.33). The CL statuses (match,
direction, partial, unsupported, contradicted; PLAN s6 337-341) ask whether the paper's tables carry each
claim, which is the failed construct; PLAN 93-94 concedes it. P7 accepts CL status agreement of 0.70 raw "on
claims both listed" (conditional on listing agreement). The failed rubric had raw evaluable agreement 42/62 =
0.68 (RESULTS.md 18-19) at kappa 0.33: the new bar would have passed the instrument the project already
rejected. BRIEF 31-32 says "You never judge whether a claim is true", while "contradicted" and "partial" are
judgements of exactly that. No status exists for vague claims (Muddit: "competitive or superior performance
compared to significantly larger autoregressive models in both quality and efficiency"), so readers split
between direction and partial. **Fix.** Gate CL status on kappa (at least 0.60) over all claims either reader
listed (unlisted = missing status), add a status "not checkable (no direction)", delete the "never judge"
sentence or scope it, and record in the decision row for OQ-02 that QA8 is descriptive only.

### M3. The main comparison (S14) is ambiguous and drives four QA items
S14 = "the comparison behind the first comparative claim in the abstract" and must point to one K unit
(BRIEF 121-124), but a K unit is one metric on one dataset, while abstract claims span many ("on 8
benchmarks"; Muddit's quality-and-efficiency claim spans Tables 1, 2 and 10). QA4, QA5 and QA6 are scored on
S14 and QA3 on "the main result" (BRIEF 290-292), which is a different anchor from F1 (QA3c) and from S14. One
upstream disagreement changes up to four QA scores; P4 pools QA kappa and never measures S14 agreement.
**Fix.** Define the main comparison as a table plus row pair (own default row against a named baseline row),
not a unit; report S14 agreement as its own pilot metric; anchor QA3 to the same comparison.

### M4. QA scores are biased downward by the tie rule and the schema
G4 (BRIEF 50) sends doubt to "no"; for QA sub-items "no" is not neutral, it lowers rigour. SCHEMA qa_item.sub
(186-187) has no required keys and allows null, so an omitted sub-item validates and the scoring rule ("2 if a
and ...", PLAN s6) treats it as not yes. QA1 can reach 2 only through sub-item d, a web pass that does not
exist (OQ-11), so text-only QA1 is effectively {0, 1}. The headline of RQ6 ("how rigorous is the evidence
base") then partly reflects the instrument. **Fix.** Require every sub-item key, with a third value "unclear"
reported separately from "no"; report QA distributions with unclear as no and as yes (bounds); do not publish
QA1 until d exists, or rescale it as a two-level item.

### M5. Version confound: 47 percent of the texts are anonymous submissions
287 of 608 include texts contain "Anonymous author(s)" on the first page (276 say "under review"). A literal
`github.com/` string occurs in 148 of 321 non-anonymous texts (46 percent) and in 63 of 287 anonymous ones
(22 percent) (scripted; links to other people's code inflate both). Double-blind rules remove code links and
affiliations, so QA1, QA2 and S11 measure which version was fetched, and S11 ("independent groups", s7) is
empty for about half the corpus. PROT s3 says the latest arXiv version is rated; OQ-17 treats the difference
only as a pooled-number issue. **Fix.** Decision row: for anonymous texts, appraise QA1/QA2 and take
affiliations from the latest public (arXiv or camera-ready) version, or record `anonymous_version` and report
RQ6 stratified by it; affiliations from metadata, not the file.

### M6. The design block confuses "not stated" with "not this paper's choice"
D01-D11 describe "the paper's own main model and its F1 sampler" (BRIEF 126) and G3 forbids inferring from a
cited paper. A training-free sampler or caching paper on LLaDA will code C2 reveal law, C3 predictor and head
layout as not_stated because training is LLaDA's, not the paper's, so section 4's counts "over all included
studies" (PLAN s1, 57-58) mix reporting gaps with inapplicability and count LLaDA's design once per derivative
paper. Benchmark and analysis papers with several models get scalar D fields (G5 lists only list-valued fields).
D13 (yes if no value is "other") is not the construct of the 47-model test, where "partly" also covers "the
identity does not apply as written" (04-design-space.tex line 14), so the two fit rates cannot be compared.
**Fix.** Add per-field provenance {contributed, inherited-from-named-checkpoint, not_stated, NA}; count
section 4 per distinct model (S07/S08) as well as per study; either drop D13 or restate it as "no other value"
and never set it beside the 36/47 figure.

### M7. RQ2 comparability fields are missing
RQ2 asks "under which protocols were the comparisons made" (PROT s1). K units carry per-arm parameters (K10),
an inference-budget flag (K09) and a baseline source (K11), but no per-arm training tokens or data, no per-arm
evaluation protocol (shots, prompt template, likelihood-scored vs generated, harness), and one `metric_kind`
for both arms, so a contrast where the AR baseline is likelihood-scored and the DLM generated cannot be
flagged. K11 is ambiguous: a citation in the row label ("LWM (Liu et al., 2024c)") cites the model, not the
source of the number. **Fix.** Per-arm `train_tokens_printed`, `shots_printed`, `scoring` {generated,
likelihood, not stated} and `number_source` {run-by-authors, copied (stated), not stated}, with the rule that
a row-label citation alone is "not stated".

### M8. RQ4 dose-response cannot be built from K units
K04 levels are strings ("T=8", "64", "1/4"), with no numeric level and no dose unit {steps, NFE,
tokens-per-step, threshold, cache interval}; H16 `setting` is per unit, not per level, so a sweep in which
generation length changes with steps cannot be encoded; figure-only series "count for RQ4 shape descriptions"
(PLAN s5.2) but no field records a shape. F4 (three settings on the F1 task) and RQ4-steps (two levels, any
task) are different sweep notions that will give conflicting counts. **Fix.** `levels_num`, `dose_unit`,
per-level `gen_length`, and for figure-only series a `shape` code {monotone up, monotone down, peaked, flat,
unclear}; state that F4 and RQ4-steps are counted separately.

### M9. Inputs that s7 pooling needs are absent
s7 asks for paired differences standardised within benchmark, random effects with study clusters, at least 8
matched contrasts from 5 groups. (a) 92 percent of stage-two contrasts report no variance (05-rq-evidence.tex
RQ6 item) and the form records no evaluation-set size or number of samples, so no binomial or sampling SE can
be computed for accuracy metrics. (b) Without a comparison-group id (C2.6) one table scored on 8 benchmarks is
8 "contrasts". (c) Metric and dataset are free strings as printed ("GSM8K", "GSM8k", "4-shot GSM8K"); there is
no controlled benchmark or metric vocabulary, and scales differ within one paper (Muddit GenEval 0.61 in Table
1 and 61.6 in Table 4). **Fix.** `n_eval_printed` (items or samples), `group_id`, a benchmark-id and metric-id
lookup table frozen before production, and a scale field.

### M10. RQ1 fields: objective missing; task-family definition contradicts itself
RQ1 lists "state space, forward process, objective, parameterisation, sampler" (PROT s1); there is no
objective field (loss and weighting). S05 counts families "in which the paper's own method has a
generated-sample result" (BRIEF 96) and defines language modelling by "perplexity, likelihood" (BRIEF 97-98),
which F1 says are not generated-sample metrics (BRIEF 172-173); likelihood-only papers (common before 2025)
get an empty family list while their H units must carry `task_family` (required, SCHEMA 233). **Fix.** Add
`design.objective` {elbo-ce, weighted-ce, score-entropy, mse-x0, mse-eps-or-velocity, flow-matching, other,
not_stated}; define S05 over all results, with a separate flag for generated-sample.

### M11. Number evidence does not establish which cell a value comes from
The validator checks that H13/K05 strings occur "inside a quote of its unit" (PLAN s11): a substring test that
"45.2" passes inside "45.21" and that any value of a 40-word run of cells passes whatever its row. A quote made
only of numbers is accepted: `0.61 0.98 0.72 0.54 0.82 0.19` -> found in M12766. PyMuPDF scrambles headers: in
Muddit Table 1 the header lines read "Overall ↑Objects ↑Counting ↑Colors ↑Position ↑ | Color ↑ | Attribution |
Single Two" and the Single and Two object values are one line ("0.98 0.72"), so column attribution needs
reconstruction, and the only check is the second reader on 10 percent. **Fix.** Validator: value matched as a
whole token, occurring once in the quote or with its ordinal position recorded; the row label must be inside
the cell quote and the column label inside the header or caption quote; report the share of units whose
column could not be matched to a header token.

### M12. The "field-level error rate" is a disagreement rate among Claude models
PLAN s8: e(r,f) = 1 if EA differs from the adjudicated value, and EC rules only fields on which EA and ER
differ (BRIEF adjudicator paragraph). Fields where both are wrong in the same way count as correct; EA, ER and
EC are all Claude models (D0015, D0021), whose shared misreadings of scrambled tables are correlated. PROT s5
asks for a field-level error rate, which implies a truth reference; the pilot has no accuracy criterion and
OQ-22's human check is optional. **Fix.** Call it "disagreement-based error rate" in the paper, and add a
human-verified gold subset (for example 6 records of the gate sample, unit values and QA sub-items only, about
3 hours) to estimate the error that the model pair cannot see.

### M13. Census extension is single-extracted for 90 percent, contrary to D0011
D0011 (decisions.jsonl row 11) and framework-v2 lines 132-133: the census is "to be extended to all included
records with a second extractor". The 176-rank random census was fully double-coded and adjudicated (D0020).
PLAN s7 gives ER 10 percent; PLAN s12 does not list this as a deviation. The paper's main critical finding (C2)
would rest on a weaker standard than its own pilot. **Fix.** Either double-extract block F on every included
study (block F is small) or enter a decision row and report the extension as single-coded with the 10 percent
agreement.

### M14. The fallback-model check that the T1 gate failure produced is not in the harness
Commit 61df436 (gate T1 FAIL: a B batch written by fallback model claude-opus-5) added tools/ft_model_check.py.
PLAN s9 lists only ft_isolation_check.py and quote_check.py after each session and s11 omits model checking,
although the plan was written after that commit (2053a01). **Fix.** Add ft_model_check.py to the post-session
checks and to ex_dispatch's log, with discard-and-rerun on mismatch.

### M15. Metadata the RQs need has no source
M03 first_version_date and M05 venue_resolved are "Md" (filled by script), but PLAN s11 builds no script for
them and no venue or published-version resolution exists in tools/ or analysis/ (grep for venue_resolved,
published_version, first_version: only the schema). RQ1 counts per year and RQ6 by year and venue type
depend on them; PROT s3's published-version resolution has not been done. **Fix.** Add a metadata tool to s11
(arXiv first-version date from the API; venue from Semantic Scholar/OpenAlex/DBLP, logged as evidence level
E1) and a decision on records without arXiv ids (U and R prefixes, 15 records).

### M16. Fields that feed main-text tables have no reliability gate
D12 levers (Tab 7, section 7) is a judgement field with no evidence and no definition beyond one line (BRIEF
163-168); s10.3 computes mean Jaccard for S05, D10, D11, D12 and S09 stages, but s10.4 sets no pass line for
any set-valued field. S13 (drives QA7 and K02) and K03 (in the K alignment key) are excluded from error rates
as free text (PLAN s8). **Fix.** A Jaccard pass line (for example mean at least 0.70, lower bound reported) for
set-valued fields; S13 coded to a short controlled list (component type) with agreement reported.

### M17. Workload is not costed; the full form on every study is about two T1 screenings
Calibration: a 10-record screening batch costs 250k-330k subagent tokens per screener (25k-33k per record).
Include texts: median 73 kB (about 18k tokens at 4 characters per token; numeric tables tokenise worse), 90th
percentile 133 kB, 11 texts over 200 kB, 49.7 MB in total. Fixed session input (brief, schema, contract):
60 kB, about 15k tokens. Output per record under v0.1: up to 40 H units and 10-20 K units at 400-600 tokens,
60-120 evidence entries at 60-80 tokens, plus blocks: about 20k-35k. Inference: 60k-100k tokens per record,
2-3 times screening. Estimates (inference, to be replaced by the pilot's measurement):

| Scope | EA | ER | QA second rater (OQ-14a) | EC | Total |
|---|---|---|---|---|---|
| Plan as drafted, 608 records | 36-61M | 61 rec, 4-6M | 608 rec at 30k-45k, 18-27M | 61 full + 300-450 QA cases, 12-23M | **70-117M** |
| OQ-01 (b): blocks on all, units on ~150 (all 53 multimodal + ~100) | 21-30M + 5-8M | 4M | (not included) | 3M | **33-45M** |
| OQ-01 (c): whole form on a stratified 150 | 12M | 1-2M | | 1-2M | **14-16M** |

T1 full-text screening was about 885 x 2 x 25k-33k = 44M-58M; the drafted plan is 1.2-2.7 times that.
Wall time: about 1 hour per 3-record session (20-45 minutes of output generation plus tool turns), 203 EA
sessions at 3 in parallel, about 68 hours for EA alone, against the two-week Paper 1 horizon of D0010 (about
2026-10-28). A 3-record batch of 90th-percentile papers reaches about 250k tokens of context. PLAN s10.4 last
bullet names no budget number. **Fix.** Put a token ceiling per record in the stop rule (for example median
above 80k triggers the OQ-01 scope fallback), batch by size (1 record above 133 kB, 2 otherwise), and settle
OQ-14 on the measured cost.

### M18. RQ6 distributions are confounded by study type
QA2 is trivially 2 for training-free sampler papers (public base weights, public benchmarks), QA7 is NA for
benchmark and analysis papers, QA6 depends on whether a baseline exists. The study-type mix shifts toward
training-free inference papers in 2025-2026, so "rigour by year" partly measures that shift. **Fix.** Report
RQ6 by S01 and training_free, and state in the protocol amendment that year and venue comparisons are
within-stratum.

---

## Minor

- m1. Three different rules for `searched`: PLAN s3 (S code only on marked fields) and s11 ("every S field
  with a negative value"), BRIEF E1 57-58 (every negative of every Q field), BRIEF 311-312 ("each no that an
  appendix could have answered"). Validation and extractor behaviour will diverge. Fix: one rule, one key form
  (QA4a vs QA4).
- m2. SCHEMA 178 cond pattern excludes QA6n and QA7n; sub-fields share one cond (S09 tokens vs compute, S10's
  four values, D07 rule vs blockwise), so the validator cannot check "a quote for every printed value" per
  sub-field. Fix: conds such as S10.steps.
- m3. figure-only and unreadable F1 need an H unit with is_F1 (BRIEF 187-188) whose value_printed must be in a
  quote (PLAN s5.4); H has no "figure-only" literal (K does). Fix: allow it and exempt it from the check.
- m4. QA4 is narrowed to the main comparison (BRIEF 293-294) while PROT s6 QA4 is not; "run" is undefined
  (sampling seeds vs training runs). Not in PLAN s12. Fix: define run; list the narrowing.
- m5. QA7 n is "theory, benchmark or analysis" in PLAN s6 but "S13 is NA" in BRIEF 302; theory papers with a
  new sampler and system papers fall between. Fix: one rule keyed to S13.
- m6. EC sees role labels (EA, ER), which reveal the production extractor and invite anchoring. Fix: neutral
  labels X/Y, randomised per study.
- m7. The pilot frame is not final: the T1 gate audit failed (61df436), a B batch was rerun and two C rulings
  superseded. Fix: draw only after the T1 gate passes, frame SHA recorded then.
- m8. "Pilot studies keep their adjudicated records" (PLAN s10.4) mixes v0.x and v1.0 records if fields change.
  Fix: re-extract revised fields under v1.0.
- m9. D12 keeps L11 value rules and L12 guidance as separate rows; framework-v2 line 137 merges the value rows
  into one row keyed by mechanism. Fix: align with the lever table the paper will print.
- m10. S02 counts diffusion VLMs that only understand images as text+image, beside unified models; RQ1
  modality counts will mix the two. Fix: report S02 with M06.
- m11. RQ5-synergy-benchmark is a benchmark, not a contrast, but is coded as a K unit with levels.
- m12. metric_kind (codebook B-10) is not defined in the brief, which claims to be self-contained (BRIEF 6-8).
- m13. Abstract H units share the key (abstract, '', '', metric, dataset); two abstract numbers on one
  benchmark collide in alignment.
- m14. PROT s5 asks for "limitations stated"; only QA9a (yes/no) is captured, not what they are.
- m15. params_b is a conversion the "never compute" rule (BRIEF 32) forbids; say that unit conversion is
  allowed.
- m16. PLAN s10.4 has the human author sign the pilot verdict; project rules say gates pass only on a
  gate-auditor verdict.
- m17. No field links records that report the same model or work (for example the 363 kB dissertation M18816
  and the papers it contains; base-model families), which bears on s7 independence and on counts.

---

## Item 4: deviations from protocol and ledger that need a decision row

Listed in PLAN s12: (1) E1-E3 and evaluability not implemented, no s10 amendment; (2) contrasts narrowed,
headline defined; (3) QA from sub-items with NA; (4) independent double extraction; (5) scope; (6) QA dual
rating; (7) extraction version.
**Missing from PLAN s12:**
1. Census extension single-coded on 90 percent, against D0011 and framework-v2 D2 (M13).
2. Model adjudicator for extraction and appraisal (claude-fable-5-1) where PROT s4 step 4 (applied to appraisal
   through s6 "as in section 4") has a human resolve disagreements; and no human validation sample for the
   appraisal (PROT s4 step 3 via s6). OQ-05 and OQ-14 discuss them; s12 does not list them.
3. QA1 "usable (repository exists ...)" scored from text only, with the existence check deferred (OQ-11).
4. QA4 narrowed to the main comparison (m4).
5. QA8 claim statuses as a reintroduction of the suspended criterion, descriptive only (M2).
6. Error rate defined against model adjudication (M12).
7. Anonymous-submission texts appraised as fetched (M5), distinct from OQ-17's version question.
8. CT1-CT6 published from a component of a rubric that failed its criterion (OQ-03 not marked as a decision
   row).
9. Scope against the user's 2026-10-16 instruction, which is itself not in the ledger (C3).

## Item 6 summary
See M17. In short: the drafted plan with OQ-14(a) is about 70M-117M subagent tokens and about 68 hours of EA
wall time, 1.2-2.7 times the whole T1 full-text screening; OQ-01 (b) is about 33M-45M; a whole-form sample of
150 is about 15M but makes RQ6, section 4 and the census sample estimates.

## Item 7 summary: what would make the data unusable for the paper's tables
H values without a value type (C2.2); duplicate units across generators (C2.1); K units without group ids or
numeric levels (C2.6, M8); free-string metrics and datasets (M9); design counts that mix inherited and
not-stated values (M6); QA scores that depend on which version was fetched (M5) and on the tie rule (M4); no
year or venue metadata (M15).

## Not checked
Block F against codebook v1.2 (codebook not in the brief; PLAN s11 assigns this to gate-auditor). Isolation
wording against ft_isolation_check.py. Whether t1-decisions-all.jsonl already reflects the t1b081 rerun.

Counts: critical 3, major 18, minor 17. Single most important fix: rewrite the H and K unit rules into one
non-overlapping, keyed definition (value type, comparison-group id, numeric levels with a dose unit, explicit
multi-baseline and benchmark/analysis rules) before any pilot is drawn.
