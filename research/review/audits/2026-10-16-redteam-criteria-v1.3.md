```yaml
agent: red-team
date: 2026-10-16
brief: Third red-team pass on full-text screening criteria v1.3 (Paper 1): status of the 12 v1.2 re-audit findings and 7 partly-resolved v1.1 findings, new fatal/major problems, reproduction of the frozen re-check, check of the proposed D0032 row, verdict
sources_examined:
  - research/CONTRACT.md
  - research/review/screening/criteria-v1.3-screener.md (all 214 lines)
  - research/review/screening/criteria-v1.3.md (all 220 lines)
  - research/review/screening/criteria-v1.2-screener.md (diff against v1.3 only)
  - research/review/audits/2026-10-16-redteam-criteria-v1.2.md (all); 2026-10-16-redteam-criteria-v1.1.md (counts, M6/M7/M8/M15 headings)
  - analysis/screening/ta_recheck_select.py, ta_recheck_freeze.py, ta_recheck_oc.py, quote_check.py (all)
  - analysis/screening/ta-recheck-frame-v1.3-frozen.jsonl, ta-recheck-sample-v1.3-frozen.json, ta-recheck-oc-v1.3.txt, ta-recheck-v1.2.log, ta-recheck-candidates-v1.2.jsonl
  - research/review/protocol.md s2, s4, s10 (D0020 entry)
  - research/review/coverage/census-codebook-v1.2.md B-4 to B-8 (l.50-91)
  - research/ledgers/decisions.jsonl rows D0020, D0027-D0031
  - research/progress.md, research/FRAMEWORK.md, CLAUDE.md (grep only: record ids and re-check mentions)
coverage: >
  Every line of both v1.3 files and of the four scripts. The selection, freeze and OC scripts were rerun
  in a scratch mirror (scratchpad/m, with copies of records.jsonl, screener-A/B and v2/), never over the
  frozen files: all five outputs are byte-identical to the repository copies (cmp), and the repository
  digests are unchanged after the run. quote_check.py --self-test was run in place (9/9, exit 0) and
  probed with three extra quotes. Hypergeometric operating characteristics and exact upper bounds were
  recomputed independently in pure Python. NOT covered: no full text (none exists), no pilot, census
  codebook outside B-4 to B-8, protocol sections other than s2, s4, s10.
claims:
  - statement: "The frozen frame, sample and OC files are reproduced byte-for-byte from the declared scripts and inputs"
    status: supported
    evidence: "scratch rerun 2026-10-16; cmp identical for frame (sha256 a9180fe4...d79a), sample (958867658120...7ac6c), OC (7f6499ce...5570), v1.2 log, candidates"
    level: E4
    confidence: 0.97
  - statement: "The OC table (0/0.079/0.265/0.617/0.826/0.927) and upper bounds (22 at K=0, 35 at K=1) are correct"
    status: supported
    evidence: "independent recomputation; also P(K>=2|F=13) = 0.50, P(K>=2|F=12) = 0.456"
    level: E4
    confidence: 0.95
  - statement: "Frame and sample composition: 797 (D1 74, D2 278, R 445); sample R 63, D2 28, D1 9; C4-only 136 in frame, 22 in sample"
    status: supported
    evidence: "count over ta-recheck-frame-v1.3-frozen.jsonl"
    level: E4
    confidence: 0.97
  - statement: "The screener copy contains no record id"
    status: supported
    evidence: "grep -cE '\\b[MR][0-9]{4,5}\\b' criteria-v1.3-screener.md -> 0"
    level: E4
    confidence: 0.98
  - statement: "quote_check.py verifies that evidence quotes are verbatim"
    status: contradicted
    evidence: "quote 'The understanding ... and the generation ... share weights' returns True on a text saying the two modules 'do not share weights' (probe run 2026-10-16)"
    level: E4
    confidence: 0.95
  - statement: "The cap of 150 was set in an orchestrator brief written before the selection script ran (A l.80; D0032 row)"
    status: unknown
    evidence: "the quoted brief text 'too large (say >150)' occurs in no repository file except criteria-v1.3.md l.80; the script first enters git in WIP commit 5605e8e"
    level: E1
    confidence: 0.8
  - statement: "R7 (v1.3) is justified by census B-7"
    status: contradicted
    evidence: "B-7 (codebook l.80-84) keeps non-language strings 'as tasks of a model that is eligible on other grounds'; R7 (S l.74-77) excludes a text DLM fine-tuned to emit them"
    level: E2
    confidence: 0.85
competing_explanations:
  - "K >= 2 can be produced by full-text false inclusions among sampled records, not by title/abstract loss: with a 1 percent per-record false-include rate and no true loss, P(K >= 2) = 0.26."
  - "A low K can reflect which model is chosen as adjudicator C (not fixed in advance, possibly the same model as screener B) as much as the absence of loss."
  - "High full-text agreement under v1.3 can reflect two Claude-family screeners sharing priors, and the ellipsis-tolerant quote check passing elided quotes, rather than rule clarity."
unknowns:
  - "Size of the final included set (the L = 16 rationale needs at least 800)."
  - "How many passed unified-model records describe a frozen MLLM with trained LoRA or learnable queries (V5)."
  - "How many passed records fine-tune or evaluate an existing text DLM only on non-language content (V1)."
  - "The authors' answer to O1."
next_test: {hypothesis: "v1.3 rules are applied identically by two blind screeners and the quote check rejects non-verbatim evidence", intervention: "blind dual pilot (screener copy only) on passed records of three classes: text DLM fine-tuned on SMILES/puzzles, frozen MLLM with LoRA or query tokens plus a trained diffusion decoder, AR-text VLA with instruction-conditioned diffusion actions; run quote_check on the rows", primary_metric: "decision- and code-level agreement per rule; count of elided quotes passing", falsifier: "any disagreement traced to R7/R14, R10 b3 or R9(1)/X2, or any passing quote whose elision changes its meaning", gpu_hours: 0}
```

# Red-team audit of criteria v1.3 (third pass)

**Verdict: adopt with listed fixes.** All six major findings block adoption. Each can be fixed in one
line, and none needs a new design. No fatal finding.

- v1.2 re-audit findings (12): **8 resolved, 3 partly, 1 not resolved.**
- v1.1 findings carried as partly resolved (7): **4 resolved, 3 partly.**
- New findings: **fatal 0, major 6, minor 10.**
- The frozen re-check reproduces byte-for-byte. The OC numbers are correct.

Line numbers: `S` = criteria-v1.3-screener.md, `A` = criteria-v1.3.md.

---

## 1. Status of earlier findings

### 1.1 The v1.2 re-audit findings N1-N12

| Finding | Status | Line in v1.3 that does it | Residual |
|---|---|---|---|
| N1 D1 made SMILES/chess "text" | resolved | S l.9-19 (content test; "whatever tokenizer or vocabulary produces it"); R7 S l.74-77 | The fix creates a new conflict with R14 and B-7 (V1) |
| N2 D1 vs R12 on action tokens | resolved | S l.16-17 "also when written with ordinary text-vocabulary tokens"; R12 S l.113-117 | none |
| N3 X1/X2 through encoders | resolved | R9(2) S l.84-89 "by any path: directly, through a text encoder, or through an LLM, VLM or MLLM (frozen or trained)"; A l.56 example corrected | m1, m8 |
| N4 b3 needs outside facts | resolved | S l.94-95 "Decide b1-b3 from statements in the screened file only"; S l.107 "If the file states neither (i) nor (ii), b3 fails" | b3's own test conflicts internally (V5) |
| N5 D4 3D vs exclusions | resolved | S l.36-42 ordered D4, "(1) ... overrides (2)", humanoid case | m7 |
| N6 frame depends on O1 | resolved | S l.46-48, l.187-188 `code_if_o1_no`; A l.76, l.155. K under O1 = no can only fall, so the default is conservative | none |
| N7 reversal rule undefined/underpowered | **partly** | A l.140-153: K, K >= 2, OC table, power 0.62 at L (all verified) | The rationale for L = 16 is not supported by the files and is arithmetically inconsistent (V3) |
| N8 provisional sample, redraw | resolved | ta_recheck_freeze.py l.29-42; A l.78; frozen files reproduced byte-for-byte | Later-queue frames: seed and tolerance not fixed (m3) |
| N9 cap of 150 | **not resolved** | A l.80 states a provenance, but no file supports it | V6 |
| N10 adjudicate merged into pass | resolved | A l.119-125 (3-category agreement, adjudicate rate per screener, include/exclude for the human) | m2 |
| N11 unblinded adjudicator sets k | **partly** | S l.153-157, l.201-213; A l.79 (blind C, unflagged, K from A/B + C) | C's model is not fixed, may equal B, and C batches can be rerun (V4) |
| N12 blinding by instruction | **partly** | A l.29-34 (dispatch folder, tool-log check) | Check unspecified; conflicts with CONTRACT.md and CLAUDE.md instructions (m4) |

### 1.2 The seven v1.1 findings left partly resolved by v1.2

| v1.1 finding | Status | Line in v1.3 |
|---|---|---|
| F2 naming loophole | resolved | S l.9-13 content test; R7 S l.74-76 "however the paper names it"; R10 S l.107-108 |
| M3 vocabulary vs task | resolved | S l.9 "The test is the content of the output, not the tokens" |
| M4 R9 vs examples | resolved | R9(2) S l.84-89; A l.56 |
| M6 R10 b3 vs D0020 | **partly** | S l.100-108 removes outside knowledge. The frozen-versus-joint test can now be read both ways (V5) |
| M7 R11 post hoc closure | resolved | S l.36-45 literal D0020 "3D" with ordered exclusions; O1 as a sensitivity analysis. Residual m7 |
| M8 X1/X2 disjointness | **partly** | S l.147-148 claims disjointness. The claim is false for the R9(1) class (m1) |
| M15 quote check missing | **partly** | quote_check.py exists, self-test 9/9 (rerun here). It passes quotes whose elision inverts their meaning (V2) |

---

## 2. New findings

### Major (all blocking)

**V1. R7 (new in v1.3) contradicts R14 and the source it cites (S l.74-77 vs S l.126-132; codebook B-7 l.80-84).**
R7: content that is not language is not text, "this holds also for a text diffusion model fine-tuned
to emit such content. Such a record is eligible only if R6 holds for some other result of the
paper." R14(a): a paper that generates with "an existing text diffusion model" is included if it
"trains or fine-tunes it as a generator", and R14(b) includes it if a table compares it with another
generator. Consider a paper that fine-tunes LLaDA or Dream only to emit SMILES, Sudoku grids or
Countdown equations. R7 excludes it and R14(a) includes it. The brief lists both rules under I1(a)
with no precedence (S l.169).

The audit copy cites census B-7 as the justification (A l.54, l.164). B-7 says the opposite for this
case: such strings do not count "except as tasks of a model that is eligible on other grounds".
Section 6 item 3 quotes B-7 without that exception. The audit copy also expects R14 to depend on D1
(the M15731 example, A l.61), but the screener copy does not say so. Screeners will see no example.
This is the same split between the two copies that v1.2 N3 had. Arithmetic expressions ("numbers ...
on their own" against "query ... or proof language", S l.12-15) make the boundary harder still. Core
masked-DLM reasoning papers evaluated only on Countdown or Sudoku fall on it.
*Rejection condition:* two blind screeners disagree on a passed record of this class.
*Fix (blocking):* state in the screener copy whether R7 overrides R14 or R14 overrides R7, and make section 6 quote B-7 in full.

**V2. quote_check.py accepts quotes whose ellipsis inverts their meaning (quote_check.py l.10-11, l.33, l.52-67).**
An ellipsis splits a quote into fragments that only have to occur in order, with no limit on the
gap and no minimum fragment length. Probe run here, on the text "...the two modules do not share
weights":
- `The understanding ... and the generation ... share weights` returns **True**.
- `understanding ... share weights` returns **True**.

b3, the decisive I1(b) condition, can therefore be "evidenced" by a quote that drops the negation.
The screener brief never mentions ellipses (S l.173-177), so the script allows something the rules
do not define. M15's purpose, evidence that can be checked, is not met for the conditions that
matter most.
*Rejection condition:* any passing quote in the pilot whose elided span changes its meaning.
*Fix (blocking):* ban ellipses in quotes, or bound the gap and fragment length and add the negation probe to the self-test.

**V3. The tolerable loss L = 16 rests on a premise no file supports, and its stated equivalence is false (A l.141, l.154; amendment A l.206).**
- **False equivalence.** "K >= 2 (F̂ >= 15.9 >= L = 16 rounded)": 15.94 < 16. The rule "reverse if F̂ >= L" with L = 16 is K >= 3, not K >= 2. The K >= 2 rule itself is unambiguous.
- **Derivation.** The sources give D0027's "about 2 percent" times D0029's "roughly 650 in scope that pass", which is 13 (A l.154 says so). L is then raised to 16 because "16 is at most 2% of any included set of 800 or more". No file shows that the included set will reach 800. D0030 reports 954 round-2 title/abstract passes, not full-text includes.
- **Power.** At the tolerance the files do support (13), power is **0.50**, not the 0.62 stated (recomputed: P(K >= 2 | F = 13) = 0.500).
- **Borrowed threshold.** D0027's 2 percent was set for a different decision, the automation filter. When that filter breached 2 percent, D0029 rescued every exclusion. Here a breach of the same size is accepted with probability 0.5.
- **Timing.** L = 16 matches 2 × 797/100 exactly. The text says "L was fixed before any re-check record was screened". It does not say L was fixed before the OC table was seen.

*Rejection condition:* the final included set is below 800 (L then exceeds 2 percent).
*Fix (blocking):* state L = 13 with power 0.50, or cite the file that supports an included set of at least 800, and correct "15.9 >= 16".

**V4. The adjudicator who produces K is not pre-specified (S l.155-157, l.201; A l.79, l.33, l.117).**
C is "a Claude model in a fresh session; model id recorded". The model is chosen later, by the
orchestrator, who knows which records are sample records and has seen how A and B decide. C may be
Claude Opus, the same model as screener B. Its "basis" then measures self-agreement, and K inherits
B's leaning. A l.33 lets "a session that read outside" the folder be "discarded and its batch ...
rerun". That is a sanctioned path to rerunning a C session after its rulings are seen. v1.2 N11 was
about the person who sets k; v1.3 moves the problem to the choice of model and of rerun.
*Rejection condition:* C's model id is chosen after any A/B row exists, or any C batch holding sample records is rerun without all runs being reported.
*Fix (blocking):* fix C's model id and version now (not B's model), and require every C run, including discarded ones, to be logged and reported.

**V5. The b3 test conflicts with itself for frozen backbones with trained adapters or queries (S l.100-107).**
(ii) holds if a training stage "updates parameters on the understanding side and on the generation
side in one optimisation". The next sentence says: "A file that says the understanding model is
frozen while a generator or connector is trained has neither." A common unified-model file says
"the MLLM is frozen; we train LoRA adapters on it jointly with the diffusion decoder". Another says
"learnable query tokens are fed into the frozen MLLM". Both sentences apply. The rule gives no
precedence and does not say which side LoRA weights or query tokens belong to. This is the largest
borderline class for RQ5, and the class that M6 and N3/N4 circled.
*Rejection condition:* a blind pilot on frozen-MLLM + LoRA/query + diffusion-decoder records gives any b3 disagreement.
*Fix (blocking):* say whether trained adapters or query tokens inside a frozen understanding model count as updating the understanding side.

**V6. The D0032 row and amendment state a provenance for the cap of 150 that no file supports (A l.80, l.203-204, l.214).**
"(above the cap of 150 set in the orchestrator's brief before the script ran)" and "cap of 150 for a
full re-check set in advance". The quoted brief text "too large (say >150)" occurs in no repository
file other than criteria-v1.3.md l.80. The script and the cap first appear together in the
post-crash WIP commit 5605e8e. Under the project's hard rule, a ledger fact needs an artifact. This
one has none, and a referee checking pre-declaration cannot verify it. N9 is therefore not resolved.
*Fix (blocking):* either cite a file that holds the brief with its timestamp, or reword the row and amendment to "cap of 150 first stated in criteria v1.2 (ta_recheck_select.py CAP)".

### Minor

- **m1. X1/X2 disjointness is false for R9(1), and amendment (1) contradicts itself (S l.81-89, l.143-148; A l.180-184).** An AR-text VLA whose diffusion action head is conditioned on the instruction through the VLM meets X2's table meaning ("text conditions the diffusion component by any path"), but R9(1) codes it X1. S l.147 says "X2 needs a stated text condition; X1 is everything else", and amendment (1) says "X1: every other ... including a model with autoregressive text ...". R9's "apply in this order" decides the code, so eligibility is unaffected, but the frozen amendment text and the disjointness claim are wrong.
- **m2. Kappa "uses 3 × 2 tables" (A l.125).** Cohen's kappa needs a shared category set. The handling of "adjudicate" against the human's include/exclude is not defined, and it directly moves the 0.70 rerun trigger.
- **m3. Later-queue frames (A l.78).** "a seeded sample of 100 with the same K >= 2 rule": the seed is not declared, and K >= 2 on a frame of N' ≠ 797 implies a different tolerance (2N'/100) that is not stated.
- **m4. Dispatch isolation is undermined by the files and context it carries (A l.29-34).** CONTRACT.md, which goes into the folder, names research/FRAMEWORK.md and research/progress.md (l.4), prescribes graph-memory (l.19) and a YAML report format that conflicts with the screener JSON rows. The project CLAUDE.md, auto-loaded when an agent starts in the repository, says every session reads progress.md. The "tool log" and the check script are not named. Grep here: progress.md, FRAMEWORK.md, CONTRACT.md and CLAUDE.md contain no record ids, so no sample id leaks this way. The risk is that the discard rule fires on every session, or is waived.
- **m5. "Never fires at zero flips" (A l.153) holds only by definition.** K counts full-text inclusions, true or false. With no true title/abstract loss and a 1 percent per-record false-include rate, P(K >= 2) = 0.26 (recomputed). This errs toward extra work, not toward loss, but the "tolerable loss" wording misdescribes what triggers the rule.
- **m6. A sampled record is a named example with its expected outcome (A l.56, l.58).** M12951 is in the frozen sample (in_sample true). The audit copy, read by the orchestrator, states that it is expected X1. The human's rulings do not change K, so the impact is limited to the reported human column.
- **m7. One robot demonstration turns human motion into an "action" (S l.37-42).** "any output the paper executes on a robot ... overrides (2)": a text-to-motion paper with a retargeting demo loses I1(b). Section 6 and the D0032 reversal do not disclose this.
- **m8. R9(2) says "method section states", R9(3) says "the paper does not state" (S l.84, l.88-89).** Text conditioning stated only in the experiments section falls to X1 by "Otherwise", against the evident intent (t2x).
- **m9. Amendment (4) attributes "anything executed on a robot" to D0020 (A l.194-195).** The D0020 entry in protocol s10 says "Robot actions, molecules and other non-text domains with autoregressive text are X1". The execution clause, joint commands, cell profiles, tables and 2D keypoints are v1.3 additions, not D0020.
- **m10. The freeze is protected only inside one script.** The D0032 row names the frozen files but not their full SHA-256 digests, and the audit copy gives truncated digests (A l.78, l.142). After adoption, an edited sample file would not be detectable from the ledger.

---

## 3. Re-check reproduction (task item 2)

| Output | Repository sha256 | Scratch rerun | Result |
|---|---|---|---|
| ta-recheck-candidates-v1.2.jsonl | a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a | ta_recheck_select.py | byte-identical |
| ta-recheck-v1.2.log | cddfc60aad88937322934634788a6aaf777b0d21b56463655f316f37d931f524 | ta_recheck_select.py | byte-identical |
| ta-recheck-frame-v1.3-frozen.jsonl | a9180fe4...d79a (same as candidates) | ta_recheck_freeze.py | byte-identical |
| ta-recheck-sample-v1.3-frozen.json | 958867658120c323446ee5692ec82702deb4464e0977a6030287ced035b7ac6c | ta_recheck_freeze.py | byte-identical |
| ta-recheck-oc-v1.3.txt | 7f6499cec3171b9a144885d411e448ccd50c3f156c755eb5c7c5ccf1d00e5570 | ta_recheck_oc.py | byte-identical |

The reruns were made in the session scratchpad mirror (`.../scratchpad/m`). Repository digests were
unchanged afterwards. The independent recomputation agrees with every OC cell and with the upper
bounds 22, 35 and 47. The frozen sample is the same draw (seed 20261016) that the v1.2 log already
listed. Freezing it rather than redrawing is acceptable, because no re-check record has been screened.

## 4. Proposed D0032 row and amendment (task item 3)

| Statement | Supported? |
|---|---|
| v1.1: 2 fatal, 15 major, 11 minor | yes (v1.1 audit l.56, l.183) |
| v1.2 re-audit: adopt with fixes, 9 major, 3 minor | yes |
| every finding mapped in the audit copies | yes (A section 2; v1.2 audit copy section 2) |
| selects 797 of 5,282 exclusions | yes (rerun) |
| "above the cap of 150 set in the orchestrator's brief before the script ran"; amendment "cap of 150 ... in advance" | **no artifact** (V6) |
| frozen sample of 100, seed 20261016, file named | yes (rerun) |
| K >= 2, tolerable loss 16; OC file; trigger probabilities 0, 0.08, 0.27, 0.62 | numbers yes; the L = 16 rationale is not in the row and is unsupported in A (V3) |
| (4) "D0020 verbatim" ... "D0020's exclusions (robot actions and anything executed on a robot, molecules)" | **partly**: the execution clause is not D0020 (m9) |
| (3) content test, with evidence including census B-7 | B-7 contradicts R7 for fine-tuned text DLMs (V1) |
| (6) blind adjudicating model, then the human author | consistent with S section D; C's model not specified (V4) |
| (1) X2/X1 definitions | self-contradictory for the R9(1) class (m1) |
| evidence list D0020, D0027, D0029, D0030 | rows exist; D0027/D0029 do not support L = 16 (V3) |

## 5. What would force rejection of "v1.3 is ready"

Run a blind dual pilot with the screener copy only on passed records from three classes:
- a text DLM fine-tuned or evaluated only on non-language content;
- a frozen MLLM with LoRA or query tokens and a trained diffusion decoder;
- an AR-text VLA with instruction-conditioned diffusion actions.

Then run quote_check on the rows. Any decision or code disagreement traced to R7/R14, R10 b3 or R9(1)
rejects the claim. So does any passing quote whose elision changes its meaning.

## 6. Blocking fixes (one line each)

1. V1: state the precedence between R7 and R14 in the screener copy and quote B-7 with its exception.
2. V2: forbid ellipses in evidence quotes (or bound gap and fragment length) and add a negation probe to the self-test.
3. V3: replace the L = 16 rationale with a supported one (L = 13, power 0.50, or a cited included-set size), and correct "15.9 >= 16".
4. V4: fix adjudicator C's model id and version now, different from B's, and report every C run including discarded ones.
5. V5: say whether trained adapters or query tokens in a frozen understanding model count as updating the understanding side for b3.
6. V6: remove or source the claim that the cap of 150 was set before the script ran, in the D0032 row and amendment item (7).
