```yaml
agent: red-team
date: 2026-10-20
brief: second adversarial review of extraction and appraisal instrument v0.2 (Paper 1); verify v0.1 fix claims, test unit keys and the cell validator on real texts, sampling, gate calibration, cost
sources_examined:
  - research/CONTRACT.md
  - research/review/extraction/EXTRACTION-PLAN-v0.2.md, extraction-schema-v0.2.json, extractor-brief-v0.2.md, OPEN-QUESTIONS-v0.2.md, RESPONSE-TO-REDTEAM-v0.1.md (all read in full)
  - research/review/audits/2026-10-20-redteam-extraction-v0.1.md (my v0.1 report)
  - research/progress.md l.260-275 (user decision of 2026-10-16 at l.268-269)
  - analysis/screening/quote_check.py l.1-200 (normalise, quote_status, check); tools/ft_model_check.py (role map l.15)
  - analysis/screening/ft-t1/t1-decisions-all.jsonl (HEAD and commits 749126f, cfb039d); corpus title files named in PLAN header
  - analysis/extraction/working-v0.2/ (README, proto_cell.py, gate_oc.py)
  - research/review/audits/2026-10-20-gate-T1-reaudit-1.md (verdict line 47); research/ledgers/decisions.jsonl (last row D0034)
  - research/sources/md/fulltext-pymupdf/ M03416, M12766 (Muddit), M09530 (TrustLDM), M13864 (dLLM vs AR code-comment translation), M07474 (FDM), M08100 (LLaDA2.1), M14370/M14372; first 6 kB and sizes of all 608 include texts
coverage: >
  Read the five instrument files in full. Re-implemented PLAN s6.3 checks 1-8 from the spec text (scratchpad cellv.py,
  cellv2.py; quote_check imported read-only) and ran them on M03416 Table 3, Muddit Tables 1-2, FDM Table 2,
  LLaDA2.1 Table 1 and TrustLDM Table 10. Reproduced the s2.3-s2.4 counts from the decisions file and corpus titles
  (strata.py), listed every C2 title match, searched frame R for multimodal records by title and by the first 5,000
  characters (fn.py), counted repeated row labels per page over all 608 texts (hier.py), computed gate operating
  characteristics (oc.py, scipy binomial) and simulated the pooled QA weighted kappa (qak.py). Derived unit keys by
  hand on the five papers from their tables and abstracts only (sections listed per paper below). NOT covered:
  census codebook v1.2 equivalence of block F (gate-auditor), ft_isolation_check internals, protocol.md (not in the
  brief), no paper read in full. Deviation from my agent definition: the brief asks for a concrete fix per finding,
  so fixes are given; criticism is not softened. Severity: critical = blocks the gate (agent definition 'fatal').
  Brief allows one output file, so no ledger rows were added.
claims:
  - statement: Including the per-field flag rule G6, an instrument at the plan's own 'good' levels (blocks 0.85 per field) passes the gate with probability about 0.2, not about 0.7.
    status: supported
    evidence: oc.py; per-field P(flag | n_f 30, true 0.85) = 0.153; P(G6 pass, 6 blocks x 10 judged fields) = 0.29; product with the listed criteria 0.67-0.74 gives 0.20-0.21
    level: E3
    confidence: 0.8
  - statement: The s6.3 validator accepts a value attributed to the wrong column, and a value taken from the wrong row group of a hierarchical table, without any warning.
    status: supported
    evidence: cellv.py on M03416 (58.4 at col 2 labelled BA, pass); cellv2.py on M12766 Table 1 (Counting value labelled Overall, pass), M07474 Table 2 (HumanEval row cited for a GSM8K unit, pass), M09530 Table 10 (LLaDA 1.5 row cited for LLaDA, pass)
    level: E3
    confidence: 0.9
  - statement: The C2 title regex has at least one substring false positive and misses at least 13 clearly multimodal includes in frame R.
    status: supported
    evidence: strata.py and fn.py output (M16622 matched on 'vision' inside 'Revision'; missed M06241, M08240, M09491, M19267, M13756, M04245, M15668, M10855, M16229, M09298, M08804, M14667, M01397)
    level: E3
    confidence: 0.85
  - statement: Group matching requires equal rq_class, so M-class on matched groups is 1 by construction; H matching requires equal value_printed, so M-val on H values is 1 by construction.
    status: supported
    evidence: PLAN s5.5 (group match 'same where and rq_class'), s5.2 (H key includes value_printed), s10.3 (M-class, M-val definitions)
    level: E2
    confidence: 0.95
competing_explanations:
  - The G6 false-fail rate is lower if real per-field agreement is mostly above 0.90 while the block mean is 0.85; that requires a few very poor fields, which G6 would then flag correctly, so the gate still fails.
unknowns:
  - real per-record tokens (no run); the cost findings are about internal consistency only
  - real prevalence of I1-I5 flags in frame R (needed for subgroup precision)
next_test: {hypothesis: "after the fixes below, two extractors produce the same G and K keys", intervention: "Stage A (12 records) with the rule additions of F-MA1, then re-run the joint gate simulation of F-CR1", primary_metric: "F1_G and F1_K on Stage A plus joint P(pass | good) from the committed simulation", falsifier: "F1_G below 0.6 on Stage A, or joint P(pass | good) below 0.85", gpu_hours: 0}
```

# Red-team audit 2: extraction and appraisal instrument v0.2

Verdict: **Stage A (development) may be drawn once the blocking preconditions and the three pre-draw fixes below
are done; Stage B (gate) may not be run until F-CR1 to F-MA4 are fixed.** v0.2 is a real advance: the cell-evidence
kind solves the v0.1 ablation-row failure, the scope now follows the user's decision, and the pilot has a gate
with defined metrics. But the gate as written fails a good instrument most of the time; two of its metrics are
identically 1; the unit keys still allow several compliant readings in four of five real papers; and the
validator does not verify columns.

References: PLAN = EXTRACTION-PLAN-v0.2.md, BRIEF = extractor-brief-v0.2.md, SCHEMA = extraction-schema-v0.2.json,
RESP = RESPONSE-TO-REDTEAM-v0.1.md, OQ = OPEN-QUESTIONS-v0.2.md. Scripts are in my session scratchpad (not committed).

---

## 1. Are the claimed v0.1 fixes real?

| v0.1 | Claimed | Verified | Note |
|---|---|---|---|
| C1 | fixed (alternative) | **real** for its rejection test | My re-implementation of s6.3 from the spec text gives T01 pass, T02 cells_mismatch, T03 row_not_found, T05 value_mismatch / value_outside_cells, T08 row_not_found, T10 header_not_found on M03416. New gaps: F-MA4. |
| C2 | fixed | **partly** | Muddit Table 1 now has one reading, as claimed. Muddit Tables 2, 4, 7, TrustLDM K-F groups, FDM, M13864 and LLaDA2.1 each still have two or more compliant readings (section 2). The K key uses a free string (column_printed). F-MA1. |
| C3 | fixed in instrument | **partly** | K on sample + multimodal is implemented. Putting L+Q+H on all 608 is the plan's own reading of "RQ data", not the user's words. The draft row says it is "recording the user decision". No ledger row exists (the last row is D0034). F-MA6. |
| M1 | fixed | **real in design**, calibration defective | F-CR1, F-MA2, F-MA3. |
| M2 | fixed | real | The not-checkable status, kappa over the union and the rescoped sentence (BRIEF l.33-35) are present. Residual: claim matching "by sentence identity" is undefined (F-mi7). |
| M3 | fixed | real | S14 is a table plus row pair; M-S14 is gated. |
| M4 | fixed | **partly** | `ynun` (SCHEMA l.198) allows null whatever n is. s6.4 checks only "n = yes exactly when S14 is NA", not "a-d null only when n = yes", so an omitted QA4-QA7 sub-item still validates (F-mi5). |
| M5 | partly | agree | |
| M6 | fixed | real, small residual | "inherited" exists only for a loaded checkpoint; a choice taken from a cited recipe without a checkpoint has no value (F-mi13). |
| M7, M8, M10, M18 | fixed | real | |
| M9 | fixed | real in the specification | The lookups do not exist yet (built in Stage A). |
| M11 | fixed | **not real for columns** | The row is verified. The column is verified only by position j, and column_printed only has to occur somewhere in the header. A wrong column passes silently. F-MA4. |
| M12, M13 | partly | agree | |
| M14 | fixed | real | tools/ft_model_check.py l.15: A sonnet-5-5, B opus-5-5, C fable-5-1. |
| M15 | fixed (specified) | specification only | Acceptable before the pilot. |
| M16 | fixed (modified) | real; side effect | Jaccard credits are not Bernoulli, so the binomial c(n_f) flag rule is undefined for set-valued fields (F-mi6). |
| M17 | fixed | **partly** | F-MA7. |
| m1, m2, m4-m12, m14-m16 | fixed | real | |
| m3 | fixed | **partly** | s6.2-s6.4 do not exempt "figure-only" or "unreadable" values from value_not_in_quote or the cell checks (F-mi9). |
| m13 | fixed | real, but creates F-MA2 | Putting value_printed in the H key makes M-val vacuous for H. |
| m17 | partly | agree | Duplicate works are already in the frame (F-mi10). |
| Item 4 rows 1-9 | in PLAN s13 | real | Rows 1, 8, 9-15 and 17 present. |

Claimed fixes that are not real: **M11** (column attribution). Claimed "fixed" but only partly true: **C2, C3, M4,
M17, m3**.

## 2. Keyed unit definition on five real included texts

Rules applied: PLAN s5.2-s5.5 and BRIEF G1, H-1/H-2, K-RQ2, K-AR, K-F, "not groups". Sections read: abstract plus every
table listed. "Readings" are interpretations that comply with the text of the rules.

**M07474, FDM (method, training-free sampler, ablation, four base models).** Abstract: no numbers, so no H-1 units. H-2 (F1):
either Table 1 (page 1, intro: LLaDA on ARC, FDM-A 86.30) or Table 2 (main results), depending on whether a motivating
intro table counts as "the first main-text results table". Focal model: the abstract names FDM, a decoding method,
first. LLaDA is not named. Table 2 is structured as benchmark row-groups (GSM8K, HumanEval, Countdown, ...) x method rows
(Probability, Margin, Entropy (T=256), FDM K=2/3/4) x base-model columns (LLaDA, LLaDA-1.5, MMaDA-MixCoT, LLaDA-MoE) x
{Accuracy, TPS}.
- Reading A: heuristic decoders are "the focal model against non-AR baselines" and so not groups (s5.3 item 3). Only the
  FDM K-sweep remains: 4 groups (second factor = base model; anchor K=2 from l.423 "γ = 0.6 and K = 2"), 4 benchmarks x 2
  metrics = 8 K units each, 32 in total.
- Reading B: the heuristics are "the credited component replaced by a standard alternative" (s5.3 item 2, QA7a). That
  gives 4 groups with 6 arms each, rq_class RQ4-order or credited-other, credited_ablation true, 32 K units with
  different arms.
- Reading C: both, giving 8 groups and 64 units.
Group match requires the same rq_class (s5.5), so readings A, B and C share almost no matched groups. Figures 4-11 (K, γ,
η1, η2) add 4-8 figure-only groups. The rules do not settle whether these are main-text or appendix duplicates.

**M12766, Muddit (unified, several AR baselines).** No abstract numbers. H-2 (F1): GenEval Overall 0.61, or COCO CIDEr if
"text generation" (named first in the abstract) is taken as the first generation task (census rule, unchanged).
- Table 1, RQ2: anchor "Muddit (512 × 512)" plus LWM, SEED-X, Chameleon. Show-O and Transfusion are excluded (image
  generator not AR). One K unit (GenEval Overall: 0.61 / 0.47 / 0.49 / 0.39). **One reading: agreed.**
- Table 2, RQ2: the anchor is "Muddit (512×512)" or "Muddit (1024×1024)", with no default stated. AR arms number 11, or 9
  if LWM and Chameleon count as "rows already recorded from an earlier table" (s5.3 item 3; the rule does not say
  whether a row means a label or a set of values). Five K units, but the two-level header ("VQAv2 / Acc. ↑") leaves
  column_printed as "VQAv2", "Acc." or "VQAv2 Acc. ↑", and the K match needs "same normalised column_printed".
- Table 3 (text loss weight, columns orientation): rq_class RQ3-objective-or-architecture or credited-other. The anchor
  is 0.6 (best) or 0.3 (the scaled model's stated weight).
- Table 4 (joint training, RQ5-task-removal): the "Joint training" column repeats Table 3's 0.6 column (61.6 / 59.9 /
  68.2). Under "first appearance wins" it is dropped and the group has no anchor (fails s6.4); otherwise 3 arms and 3
  units.
- Table 5 (steps, RQ4-steps): the anchor is T=64 (its values equal Table 2's 59.9 / 68.2) or T=32 (Figure 12: "We use
  32 inference steps").
- Table 7: Show-O is labelled "AR + Discrete Diff". It is an RQ2 arm under K-AR read per output, and not one under
  "labelled autoregressive". Its values repeat Table 2. So 0 or 1 group (3 units).
- Table 9 (CFG): one group, anchor CFG = 1.5. One reading.
Total K units: 17-21 depending on the reading.

**M09530, TrustLDM (benchmark).** No abstract numbers and no model named. Focal = LLaDA (first diffusion row of Table 1).
RQ2: no AR rows, so none. **Agreed.** K-F is where readers diverge. Tables 10-26 (appendix) give per-model decoding order
(Random, L2R, R2L, Entropy, Confidence, Margin) x context (6 levels). Under "one group per level of the second factor"
that is about 6 groups per table x 15 tables for LLaDA alone, about 90 groups. Every non-RQ2 group needs exactly one
anchor (s6.4), but the paper states no default decoding order (no "default" in the text). Readers either invent an
anchor or skip. Whether context configurations (prompt attacks) are a factor of the focal model is not covered. Figure
2-4 sweeps (block size, generation length) add figure-only groups. Range: 0 to about 90 groups.

**M13864, dLLM vs AR for code-comment translation (analysis).** No abstract numbers. G1 makes DiffuCoder the focal
model ("two diffusion LLMs (DiffuCoder and Dream)"), but Table 1 has two DiffuCoder rows, and every analysis beyond
Table 1 (Table 2, rate sweep, remasking comparison in Figure 5) is on Dream. Following G1, the paper's RQ4 contrasts are
not groups ("factor groups for the focal model only"); a reader who treats Dream as focal records them.
- Table 1, RQ2 (analysis rule): 5 diffusion rows plus Qwen2.5-7B, anchor null. Four K units (BLEU ru/en, COMET ru/en),
  but column_printed is undefined: "ru" occurs twice in the header.
- Table 2 repeats Dream (rate=1) and Qwen. Qwen's COMET-ru is 0.531 here and 0.532 in Table 1, so "already recorded" is
  undecidable.
- Row-label extent: "Dream-v0-Instruct-7B" and "Dream-v0-Instruct-7B (rate=1)" both pass the cell check (first_col
  shifts by one), but the arm labels differ, so value matching by label fails.

**M08100, LLaDA2.1 (several AR baselines, columns orientation).** H-1: 892, 801, 663 TPS (three speed units). The rule
excludes "16B", "100B" and "33 benchmarks". **One reading: agreed.** H-2 (F1): Table 1 is columns-oriented (models are
columns, benchmarks are rows), so the census "row the text quotes, else default configuration" fits the axes the wrong
way round. S Mode or Q Mode x "Average" or the first benchmark gives four readings.
- RQ2: no default between "two distinct personas" (S and Q Mode), so the anchor is ambiguous. The caption labels AR only
  collectively ("for AR model, we report its scores only").
- About 33 K units in Table 1 and about 33 more in Table 2 (mini), i.e. 66 from RQ2 alone.
- Table 4 (w/o vs w/ MBE, two models as second factor) adds 2 groups.

**Answer.** Two extractors would produce the same keys only for the simplest cases (Muddit Table 1, TrustLDM RQ2,
LLaDA2.1 abstract H units). Divergence comes from: (i) no rule when the paper states no default or several (anchor);
(ii) baseline versus credited-component replacement for training-free sampler papers, a large share of the 2025-2026
corpus; (iii) "rows already recorded" (label or values?); (iv) column_printed in the K key for multi-level headers;
(v) the focal rule for analysis and benchmark papers picks a model the paper does not analyse; (vi) no rule for
anchorless factor groups; (vii) row-label extent over several lines; (viii) rq_class for loss weights and similar
factors, which is fatal to matching because rq_class is in the group key.

## 3. Table-aware validator against M03416 and a 7-column table

The spec can be built: my re-implementation took about 100 lines.

Correct cells accepted:
- M03416 rows: yes.
- Muddit Table 1 (8 metric columns plus 3 descriptor columns): the own row and AR rows pass with the correct col.
- Synthetic T14 (7 columns): passes (also in the author's prototype).

Correct cells falsely rejected or warned:
- A label glued to the next cell by PyMuPDF ("UniDisc (512 × 512) (Swerdlow et al., 2025b)Discrete") gives
  row_not_found for the label as printed. Only the file-token form passes, and check 8 then forces that garbage into the
  arm label. Rare: the glue pattern occurs in 2 of 608 texts.
- Header tokens with glued arrows ("↑Counting") give header_mismatch on a correct column.
- A header split by a hyphen before a capital ("Qwen3-30B-" / "A3B-Inst-2507") is not re-joined by step 2, so a correct
  arm gets label_header_mismatch.

Wrong cells accepted (the M11 claim fails):
- (a) M03416: value 58.4 at col 2 (TB) with column_printed "BA": pass, no warning.
- (b) Muddit Table 1: LWM's Counting value 0.41 recorded as "Overall": pass, no warning. Muddit Table 2: Show-O's GQA
  58.0 recorded as "VQAv2": pass.
- (c) FDM Table 2: the "Margin (T=256)" row of HumanEval cited for a GSM8K unit: pass. Check 3 ignores row groups.
- (d) TrustLDM Table 10: LLaDA 1.5's "Suffix (Short)" row cited for LLaDA: pass.
- (e) Columns orientation (LLaDA2.1): the arm a value is assigned to is never checked, only its position j. A Q-Mode
  value given to the S-Mode arm passes if j is counted correctly. "|" separators count as tokens and shift j.

Scale: 527 of 608 include texts have a page on which one label precedes numeric cells at least twice (hier.py; a
noisy proxy for hierarchical tables, sub-tables and repeated labels).

## 4. Sampling

- Counts, allocation and weights reproduce exactly: C1 53, C2 52, FR 491, NL 12; strata 166/75/79/171; allocation
  41/18/19/42; weights 4.049/4.167/4.158/4.071; list hashes 91615db3..., b09306d3..., 08e76b1b...; Kish deff 1.34.
  The strata script itself is missing: analysis/extraction/working-v0.2/README.md says "the strata selection script
  was not found".
- 120: the arithmetic is right (half-width 0.078 overall, 0.110 at 50 percent subgroup). It is adequate for headline
  frame-R shares only (F-mi4).
- Title-regex C2: not defensible as the definition of "all multimodal" (F-MA5). A screening-field rule is not available
  (T1 recorded only i1 and nonlang_only), but the light-pass S02 is.
- Seeds: reproducible given a pinned Python version, but they collide (F-mi3).

## 5. Gate operating characteristics

The author's "about 0.7" is correct only for the subset it multiplies: G3 at 0.85, G4 F1_H 0.85, F1_G and F1_K 0.75,
M-val 0.95, G5 at 0.85, giving 0.67-0.74 by my recomputation. It omits G6, G1, G2, G7, M-class, the kappa criteria and
the QA weighted kappa. G6 dominates. See F-CR1 for the corrected figure and the fix.

## 6. Cost

Component sums agree with the totals to rounding (44.1 vs 44.2, 67.0 vs 67.1). REC and FULL add up correctly. The
inconsistencies are listed in F-MA7.

---

## Findings

### Critical

**F-CR1. The gate fails a good instrument about 80 percent of the time (blocks Stage B).**

Evidence:
- G6 fails a block if more than a quarter of its judged fields are flagged. The flag threshold c(n_f) is calibrated at
  true agreement **0.90** (PLAN s10.3), while the plan's own "good" level for blocks is **0.85** (s10.6 reading).
- At per-field 0.85: P(flag) = 0.153 (n_f 30) to 0.177 (n_f 15). A 10-field block then fails G6 with probability
  about 0.19, and a 6-field block (CT) with 0.23. Six blocks pass G6 together with probability **0.29**.
- With the listed criteria (0.67-0.74), P(pass | good) is about **0.20-0.21**. With one re-gate, a good instrument ends
  with "blocks descriptive or dropped" with probability about 0.64.
- G5 (23 of 30) passes 0.76 at 0.80 and 0.28 at 0.70. Exact identity of a table plus two rows (S14) or of the F1 cell
  is fragile in 4 of the 5 papers in section 2, none of which has an abstract number.
- The OC simulation used strata 20 + 10, while Stage B has three strata of 10.

Rejection test: a committed joint simulation of every hard criterion at the s10.6 good levels gives P(pass) below 0.85.

Fix:
1. Write the good and bad levels per criterion into s10.4.
2. Make G6 diagnostic: flags trigger text revision and production re-measurement, not FAIL. If it stays gating,
   calibrate at 0.85 with a per-field false-flag rate of 0.01: c(30) = 20, c(20) = 12, c(15) = 8 (false flag 0.010,
   0.006, 0.004; detection at 0.60: 0.82, 0.58, 0.39).
3. For G5 use 22 of 30 (P(pass) 0.094 at 0.60, 0.87 at 0.80, 0.97 at 0.85), or measure S14 and F1u on 45 records with
   L+Q only (c = 33: 0.045 at 0.60, 0.90 at 0.80).
4. Commit one joint simulation of every hard criterion with record correlation and the real 3 x 10 strata. Require
   P(pass | good) >= 0.85 and P(pass | one quantity at bad) <= 0.10 before the gate row is frozen. If n = 30 cannot meet
   this, raise n (10 records cost about 1.6M-2.6M on the plan's 160k-260k per gate record).

### Major

**F-MA1. Unit keys are still not reproducible (C2 partly fixed).**

Evidence: section 2. Ambiguities (i)-(viii). The K key contains column_printed, a free string. The group key contains
rq_class, a judgement.

Rejection test: F1_G below 0.6 on Stage A.

Fix, before Stage A so that the development stage is informative:
- Anchor rule when no default or several defaults are stated: the first own row of the first table that has one; else
  null with a flag, allowed by s6.4.
- Training-free method papers: other decoders on the same base model are one credited-ablation group, never
  "baselines".
- "Already recorded" means the same label with the same values for the same columns.
- K key = (group, benchmark_id, metric_id, split, second-level label), with a written composition rule for multi-level
  headers ("<level1> / <level2>").
- Group key without rq_class: (where, Jaccard of arm labels), with rq_class measured as an attribute.
- Focal rule for analysis and benchmark papers: the model with the most result rows, or every evaluated diffusion
  model, with a cap.
- Row label = every line above the first value token on that row.
- A rule for factor groups without an anchor in benchmark papers (anchor null; contrasts are derived pairwise).

**F-MA2. Two gate metrics are 1 by construction.**

Evidence: group match requires the same rq_class (s5.5), so M-class on matched groups (s10.3) is 1. The H key includes
value_printed (s5.2), so M-val over H values is 1. Disagreements on these move silently into F1_G and F1_H.

Fix: take rq_class and value out of the keys (see F-MA1). Compute M-class and H value agreement on the groups and units
matched without them.

**F-MA3. The kappa criteria have no bite, or are inflated.**

Evidence:
- With namespaced categories, p_e is about (mean within-field p_e) / (number of fields). Kappa >= 0.60 is then
  equivalent to raw agreement >= 0.61 (20 fields), 0.62 (13) or 0.65 (6), always implied by LB90(raw) >= 0.70.
- The AC1 switch ("one category exceeds 0.90 of values in a block") cannot fire under namespacing in a multi-field
  block.
- The QA weighted kappa pooled over QA1-QA9 counts differences between item means as agreement. In simulation
  (assumed marginals, qak.py), raters independent within every item give 0.28. Mean per-item weighted kappa 0.49 gives
  a pooled 0.64, which passes the 0.60 line.

Fix: report per-field kappa or AC1 and gate on the mean per-item QA weighted kappa (or namespaced), with its threshold
re-derived.

**F-MA4. The validator does not verify columns, arms in columns groups, or row groups (M11 not fixed).**

Evidence: section 3, cases (a)-(e). The reported "header_mismatch share" counts false warnings on correct columns
(glued arrows, split headers) and misses wrong columns, so it does not estimate column error.

Fix:
- Locate column_printed's position in the header token run and require it to map to j. For multi-level headers, record
  header_level1 and header_level2 positions. Where the header cannot be aligned (scrambled), the status is
  column_unverified (warning), and the unit goes to the second reader with certainty, not on a 10 percent sample.
- Add `row_group` (the row-group label as printed, e.g. "HumanEval", "LLaDA 1.5") to the cell entry and check that it is
  the nearest preceding row-group line above the matched row.
- In columns groups, check the arm's header position against j.
- Add T23-T27 for cases (a)-(e).

**F-MA5. The C2 title regex misclassifies in both directions.**

Evidence:
- False positive: `vision` without a word boundary matches "Revision" (M16622, a code-generation paper). M13760 (a model
  of human speech production) and M15684 (a 347 kB survey-like text) are doubtful.
- At least 13 clearly multimodal includes are in frame R: M06241 (DIFFA, audio), M08240, M09491, M19267 (ASR), M13756
  (diffusion CTC), M04245 (sign-language translation), M15668 (remote-sensing captioning), M10855, M16229, M09298
  (document OCR/recognition), M08804 (chest X-ray report), M14667 (omni), M01397 (any-to-any).
- Consequences: the "C2 census" column is not a census, and frame R is not "language-only" (s2.5). The completion rule
  covers only undrawn records; drawn multimodal records stay in frame-R estimates and their place in the multimodal
  tables is unstated.
- Misclassification does not bias the pooled 596 estimate (C2 is a certainty stratum), only the labels and per-stratum
  tables.

Fix (preferred): two-phase draw. Run L+Q+H on all 608 first, define multimodal by S02 (which the gate measures), then
draw K's random sample from S02 = text. K already has its own cost component, so the extra cost is a second read of
225 texts (about 225 x 18k = 4M tokens, inference).
Fix (minimum): word-bounded regex over title plus abstract, the resulting list checked by hand once and committed with
its hash before the draw. Re-label the columns "C2 (rule)" and report the light-pass misclassification.

**F-MA6. The scope reading is not confirmed (C3 partly fixed).**

Evidence: progress.md l.268-269 says "extract RQ data on a stratified sample + all multimodal". RQ1 and RQ6 data are
also RQ data. PLAN s2.1 reads "RQ data" as block K only and so puts L+Q+H on all 608. That is component 1, 23.1M-33.4M,
52 percent of MIN. The draft row (s2.9) calls this "recording the user decision". OQ2-01 asks only about second
extractors, not this reading.

Fix: put the reading itself to the user as an option (L+Q+H on all vs on sample + multimodal). Word the row as the
user's choice, not as a recording.

**F-MA7. Cost: G7 does not protect the stated budget, and several bases are inconsistent (M17 partly fixed).**

Evidence:
- The table assumes 71k-108k per full-form record (s2.8 bases), but G7 passes up to a **median** of 120k (P90 200k).
  Totals scale with means, and the text-size distribution is right-skewed (median 73 kB, P90 133 kB). At the ceiling,
  MIN is about 75M, against 44.2M-67.1M stated (inference).
- The bases are the v0.1 red-team inference for a smaller form. v0.2 adds 13-field arms and a caption plus header in
  every cell entry.
- EC bases differ: 15k-30k (s2.8 text), about 18k-44k (implied by the component 6 range of 160k-260k per gate record),
  41k-57k (component 4: 2.5M-3.5M over 61).
- Component 4 counts 61 records against the 62 of component 3.
- Option 8 implies 46k-75k per record including EC, below the sum of its own stated parts (QA rater 30k-45k plus F
  25k-33k).

Fix: one per-record table (EA light, EA K, ER, EC, EQ) used everywhere. Set G7 as a mean-based ceiling equal to the
budget the user approves, and recompute MIN, REC and FULL from Stage A measurements before Stage B.

### Minor

- **F-mi1.** PLAN header and s2.9 cite the decisions file as sha256 00b6247b... with 885 rows. That is the
  superseded commit 749126f. HEAD is 962e3171... with 882 rows, after cfb039d. The include set is identical (checked).
  Fix: cite the HEAD hash.
- **F-mi2.** Appendix A scripts are not in the repository, and the strata script is lost (README). I reproduced every
  count, but the plan's evidence is not re-runnable. Fix: commit strata.py before the draw.
- **F-mi3.** Seeds collide although s2.4 says they were "checked unused":
  - 20261113: RQ anon-long and Stage B h=1.
  - 20261114: RQ anon-short, Stage B h=2 and re-gate h=0.
  - 20261115: RQ named-long, the ER draw (s8.2) and re-gate h=1.
  - 20261116: RQ named-short, re-gate h=2 and EC labels record 0.
  - 20261117: the bootstrap and EC labels record 1.
  Draws on overlapping sorted frames become correlated. Fix: one seed table with disjoint ranges per purpose; pin the
  Python version in the manifest.
- **F-mi4.** The precision case for n = 120 uses p = 0.5 on frame-R study shares. Class-specific RQ3/RQ4 cells (cache,
  remask, RL, distillation) at 10-20 percent prevalence have half-widths of about 0.18-0.25. Contrast-level clustering is
  ignored. Fix: state that class-specific frame-R cells are descriptive unless the census or extension covers them.
- **F-mi5.** `ynun` nulls are not tied to n = yes (M4 residual). Fix: an if/then in the schema or a validator rule.
- **F-mi6.** The c(n_f) rule assumes binary credits, so it is undefined for Jaccard-credited set fields. Fix: exclude
  them from flags or use a bootstrap flag.
- **F-mi7.** M-CL matches claims "by sentence identity of their prose evidence", but quotes are 6-40-word windows, and no
  sentence segmentation is defined. Fix: match by overlap of quote spans in the normalised text.
- **F-mi8.** Hyphen handling differs between paths. The cell path joins only lower-case continuations and drops the
  hyphen ("self-" / "conditioning" becomes "selfconditioning", so a label quoted as printed fails). quote_check joins
  any word character and has a de-hyphenated fallback. Fix: use quote_check's rule in both, with the de-hyphenated
  fallback.
- **F-mi9.** "figure-only" and "unreadable" values have no validator exemption in s6.2-s6.4 (m3 residual).
- **F-mi10.** Duplicate works are in the frame: M14370 and M14372 (Esoteric LMs, the anonymous ICLR copy and the
  workshop copy), and the title-prefix pairs M03951/M16269 and M09657/M15091. One work can be drawn twice, and
  family_id comes after extraction. Fix: deduplicate the frame before the draw, or cluster by work.
- **F-mi11.** Three T1 records are pending (B unavailable). If any is included, the frame and the allocation (42/41/19/18)
  written into the draft row change. Fix: put the allocation rule, not the numbers, in the row.
- **F-mi12.** The place of targeted-extension records (s2.7) in weighted estimates is unstated. Fix: same rule as for
  completion records.
- **F-mi13.** Provenance has no value for choices taken from a cited recipe without a loaded checkpoint (M6 residual).
  Fix: add inherited-from-cited-method.

## Blocking preconditions (process, not instrument findings)

1. The T1 gate is not passed. 2026-10-20-gate-T1-reaudit-1.md l.47: "Verdict: FAIL", with every remaining blocker
   needing the human author. PLAN s10.1 requires a pass.
2. No decision row of PLAN s13 marked "before the pilot" is entered: rows 1-6, 9, 11-13, 15, 16, 19, 21, 22. The last
   ledger row is D0034.
3. None of the s11 tools exists: ex_dispatch, ex_validate, ex_metadata, the draw scripts, agreement.py, the lookups.
   Stage A needs at least ex_dispatch, ex_validate (with the F-MA4 checks) and draw_pilot.

## May the pilot be drawn?

- Stage A: yes, after preconditions 1-3 and three pre-draw fixes:
  - F-MA5: the C2 definition fixes the pools.
  - F-MA6: the scope row fixes the strata.
  - F-MA1: the rule and key additions, so that Stage A tests the rules it will freeze.
- Stage B: only after F-CR1, F-MA2, F-MA3 and F-MA4 (and F-MA7's G7 restatement), frozen in the gate row.

Counts: critical 1, major 7, minor 13; Stage A may be drawn after the blocking preconditions plus F-MA1, F-MA5 and F-MA6 (Stage B only after F-CR1 to F-MA4); single most important remaining fix: recalibrate the gate (G6 diagnostic or calibrated at 0.85, vacuous metrics removed, one joint simulation showing P(pass | good) >= 0.85).
