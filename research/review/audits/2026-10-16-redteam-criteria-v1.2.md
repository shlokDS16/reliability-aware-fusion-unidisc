```yaml
agent: red-team
date: 2026-10-16
brief: Re-audit criteria v1.2 (screener copy, audit copy, re-check selection script) against the 28 v1.1 findings; find new fatal/major problems
sources_examined:
  - research/CONTRACT.md
  - research/review/screening/criteria-v1.2-screener.md (all 176 lines)
  - research/review/screening/criteria-v1.2.md (all 229 lines)
  - analysis/screening/ta_recheck_select.py (all), ta-recheck-v1.2.log, ta-recheck-candidates-v1.2.jsonl
  - research/review/audits/2026-10-16-redteam-criteria-v1.1.md (own previous report)
  - research/review/protocol.md s2, s4, s10 (read for the v1.1 audit, not re-read)
coverage: >
  Every line of both v1.2 files and the script. The selection script was run once
  (python analysis/screening/ta_recheck_select.py). Before and after the run the candidates file
  SHA-256 is the same (a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a) and the log
  is byte-identical (diff empty): deterministic. Frames D1 210, D2 999, R 4,073 (total 5,282);
  797 candidates, confirmed. Extra checks used a scratch script (scratchpad rt_v12.py, not committed)
  that imports frames() from the selection script unchanged. NOT covered: no full text, no pilot,
  census codebook beyond B-1 to B-8.
claims:
  - statement: "The selection script is deterministic and gives 797 candidates of 5,282 exclusions"
    status: supported
    evidence: "run 2026-10-16; candidates sha256 unchanged; log diff empty"
    level: E4
    confidence: 0.97
  - statement: "Every v1.1 finding is resolved (audit copy section 2)"
    status: mixed
    evidence: "21 resolved, 7 partly, 0 not resolved (table below)"
    level: E1
    confidence: 0.8
  - statement: "A random sample of 100 of 797 with the stated reversal rule can detect a loss above about 2 percent of included studies"
    status: contradicted
    evidence: "with 8 true flips among 797, P(k=0) = 0.34; with 12, 0.20; at k=0 the Wilson 95 percent upper bound scaled to 797 is 29.5 records (rt_v12.py)"
    level: E4
    confidence: 0.9
competing_explanations:
  - "A k=0 result in the sample is explained as well by low power (P(k=0) = 0.34 at 8 true flips) as by the absence of a loss."
  - "If k is low, the adjudicator's knowledge of which records are re-check records and of the reversal consequence (screening all 797) explains it as well as the rules do."
unknowns:
  - "How many passed VLA records emit actions as text-vocabulary tokens (N2)."
  - "The final number of included studies, which the reversal threshold depends on."
  - "The authors' answer to O1."
next_test: {hypothesis: "v1.2 rules are applied identically by two blind screeners", intervention: "blind dual pilot on passed records from the classes in N1-N5 using the screener copy only", primary_metric: "decision- and code-level agreement per rule", falsifier: "disagreements traced to D1/R12, R9(2), R10 b3, D4", gpu_hours: 0}
```

# Red-team re-audit of criteria v1.2

**Verdict: adopt with listed fixes.** The listed fixes are blocking: none of N1-N8 or N11 can wait
until after full-text screening starts. No new fatal finding.

- Old findings (28): **21 resolved, 7 partly resolved, 0 not resolved.**
- New findings: **fatal 0, major 9, minor 3.**

The selection script is deterministic and gives 797 candidates, as claimed. It now covers the
records I named as missed in the v1.1 audit, with one exception: M08480 EndoCoT.

As the brief asked, each new finding ends with a one-line minimal fix.

Line numbers: `S` = criteria-v1.2-screener.md, `A` = criteria-v1.2.md.

---

## 1. Status of the 28 v1.1 findings

| Finding | Status | Evidence |
|---|---|---|
| F1 R4/R6 continuous and latent | resolved | S l.61-65 "Judge the decoded output, not the variable denoised"; the brief (S l.148) no longer lists embeddings |
| F2 naming loophole | **partly** | R7 S l.66-67 and R8 S l.68-70 close the naming route. D1 S l.11-13 opens a new one: non-language strings written in a text vocabulary count as text (N1) |
| M1 R4/R5 baselines | resolved | D3 S l.30-33; R4 S l.55-56 "Baselines do not count" |
| M2 MLM / masked-generative / flow | resolved | D2 S l.20-28 (range of corruption levels plus multi-step); disclosed in amendment item (2), A l.196-199. CMLM-type models are now in, deliberately (class C7) |
| M3 vocabulary vs task | **partly** | D1 S l.11-16 settles task heads. It conflicts with R12 for action tokens in a text vocabulary (N2) |
| M4 R9 vs examples | **partly** | R9(2) S l.74-76 settles decoded-text pipelines. Text that reaches the diffusion component through an encoder or VLM is undecided (N3) |
| M5 R13/R14 | resolved | R13 S l.99-100 "Applies when the paper's final model does not generate"; R14 S l.110 |
| M6 R10 b3 vs D0020 | **partly** | D0020 is now quoted verbatim (S l.85-92). The added clause "in the work that produced the weights it uses" needs knowledge from outside the file (N4) |
| M7 R11 post hoc closure | **partly** | D4 S l.35-40 uses the literal "3D", tagged with body3d. O1 is open when screening starts, and D4 conflicts with its own exclusions (N5, N6) |
| M8 X2-first hides boundaries | **partly** | B-8 order (S l.115-128) and `xsub` (S l.77-79) are in place. The claim that X1 and X2 are disjoint depends on N3 |
| M9 doubt defaults to exclusion | resolved | Section D, S l.131-135 |
| M10 s4 steps 3-4 | resolved | A l.115-121; D0032 item (6), A l.210-212 |
| M11 blinding | resolved | `grep -cE "\b[MR][0-9]{4,5}\b"` on S returns 0 (rerun here); brief S l.140-143. Enforcement is by instruction only (N12) |
| M12 irreproducible list | resolved | Script run here: deterministic, 797. Audit-named misses M16907, M17608, M09922, M14963 (C2), M13010 (C3/C5/C6), M14003 (C3/C4) are now candidates; M08480 is not |
| M13 selective re-open; RQ2-context | resolved | RQ2-context is gone from S. Sampled includes enter with appraisal and a sensitivity analysis (A l.165-166) |
| M14 timing | resolved | A l.38-42; amendment A l.186-187 |
| M15 evidence | **partly** | Per-condition quotes and rq_loc are in place (S l.152-163). The quote-check script is not written (A l.87, l.121) and must exist before screening |
| m1 X6 | resolved | S l.128-129 |
| m2 off-topic X3 | resolved | `x3_scope`, S l.47 |
| m3 X5 / R3 | resolved | S l.51-54, l.121; A l.90 |
| m4 X8 date | resolved | S l.119 (script, per-source search date) |
| m5 taxonomy surveys | resolved | S l.46 |
| m6 mm | resolved | S l.164-165 |
| m7 rules list | resolved | S l.169 |
| m8 brief omissions | resolved | S l.147-151, l.173 |
| m9 subscription queue | resolved | A l.32-36 (but see N8) |
| m10 reversal clause | resolved | A l.227 |
| m11 unverifiable counts | resolved | A l.50 |

---

## 2. New findings

### Major

**N1. D1 makes non-language strings "text" when a text-vocabulary model writes them (S l.11-13).**
"a natural-language model that writes ... a chess move or a SMILES string in its text vocabulary
produces text". A text DLM fine-tuned to emit SMILES, Sudoku grids or chess moves is then I1(a). Its
output is still not natural-language text (protocol I1; census B-7: "Strings that are not language
(SMILES ...) do not"). Section 6 (A l.170-177) does not list this widening, and no re-check class
covers it, although title/abstract screeners coded such records X1. It is also undecidable: is a
BPE tokenizer trained on SMILES "the vocabulary of a natural language" or "a non-language alphabet"
(S l.17)? Thirty title/abstract exclusions match a text-DLM term plus a non-language or action term
and are not candidates (regex in rt_v12.py; for example R0747 "D3LM: A Discrete DNA Diffusion
Language Model", M15804 "LEAF: Large Language Diffusion Model for Time Series").
*Minimal fix:* text = natural-language or code content, not tokenizer membership; delete "SMILES string" and "chess move" from D1.

**N2. D1 and R12 conflict on action tokens (S l.11-16 vs l.96-98).** VLAs that map actions onto
existing text-vocabulary tokens (bins on rarely used tokens) emit tokens "in its text vocabulary".
D1's first sentence makes that text. D1's exclusion covers only special tokens "added for a task",
and R12 says actions are never text. Discrete-diffusion VLA records passed title/abstract and will
meet this boundary at full text.
*Minimal fix:* state that action, trajectory and progress content is not text whatever the tokens used.

**N3. Whether X1 or X2 applies is undecidable when text reaches the diffusion component through an encoder (S l.74-76).**
R9(2) asks whether text is "an input of the diffusion component". In a standard text-to-image model
the prompt passes through a frozen text encoder, and everyone will code X2 (t2x). In a frozen-VLM
system (query tokens or hidden states into a decoder) the prompt passes through a frozen VLM. The
structure is the same, but the audit copy expects X1 "pipeline" (A l.59, M15792). Screeners, who see
no examples, will split, and the adjudicator, who reads the audit copy, will apply a third reading.
The disjointness on which the M8 fix rests (S l.128) fails for this class, and so do the `xsub`
"pipeline" and "t2x" counts.
*Minimal fix:* define "input of the diffusion component" to include text passed through any encoder, and correct A l.59.

**N4. The b3 "jointly trained" test needs facts from outside the screened file (S l.88-90).**
"in this paper or in the work that produced the weights it uses". Screeners may not look elsewhere
(S l.143). A system built on released unified weights rarely restates how those weights were
trained. The condition is then undecidable from the file and will either go to "adjudicate" in bulk
or be guessed.
*Minimal fix:* decide b3 from statements in the file only; if not stated there, b3 fails.

**N5. D4's "3D coordinates" contradicts its own exclusions (S l.36-39).**
"any output or input that the paper represents as three-dimensional geometry: 3D coordinates ...
including 3D human pose and motion" against "Not other modalities: ... robot actions and
trajectories". Robot end-effector trajectories, driving waypoints and humanoid whole-body joint
trajectories are 3D coordinates. The text gives no precedence, so humanoid motion generation for
robots (the M15235 class) can be read either way.
*Minimal fix:* state that the exclusions override "3D coordinates", and name the humanoid case.

**N6. O1 is open when screening starts, and the re-check frame depends on it (A l.175, l.152).**
Class C4 has 167 candidates. 136 match C4 only, and 22 of the 100 sampled ids are C4-only
(rt_v12.py). If the authors rule "no", those candidates are not "more inclusive" under v1.2. The
frame (797) and the scaling factor change after the sample is drawn, so k/100 × 797 is wrong for
either answer. Removing `body3d` records by script (A l.175) also leaves them without an exclusion
code (the screeners never coded the I1(a)/R9 path), and PRISMA needs one code per exclusion.
*Minimal fix:* obtain the O1 ruling before sampling and screening, or have screeners also code the "O1 = no" path.

**N7. The reversal rule of the re-check cannot be applied as written and the sample is underpowered (A l.160-162; amendment item 7).**
- **Threshold undefined:** "if the estimate exceeds about 2 percent of the included studies" does not say whether the point estimate or the upper bound is compared, and "about" is not a threshold. The denominator (included studies) is unknown until full-text screening ends.
- **Under the upper-bound reading:** at k = 0 the Wilson 95 percent upper bound scaled to 797 is 29.5 records, which exceeds 2 percent of any plausible included set (fewer than about 1,475 studies). The full re-check is then always triggered and the sample is pointless.
- **Under the point-estimate reading:** with 8 true flips among the 797 the sample shows k = 0 with probability 0.34; with 12 flips, 0.20 (hypergeometric, rt_v12.py). k = 1 already gives a point estimate of 8.0.
- **Mixed frames:** 63 of the 100 sampled ids come from frame R (single Haiku screener) and 37 from the dual frames. One pooled ratio hides that the two frames have different prior flip rates. This is a lesser point.

*Minimal fix:* state the compared quantity, a numeric threshold fixed now, and the power at that threshold, or stratify by frame.

**N8. The sample is provisional and is to be redrawn on a larger frame, with no rule on which draw counts (A l.155-158).**
The log already holds 100 sample ids (seed 20261016). The plan redraws "after the subscription-queue
and title-resolved records have been screened ... The current sample ids are provisional." Redrawing
with the same seed on a changed frame gives a largely different sample. Nothing forbids screening
the provisional draw first, so two draws can coexist and one can be chosen after results are seen.
This is the same pre-declaration problem as v1.1 M12/M14.
*Minimal fix:* draw once, after the frame closes and before any re-check record is dispatched; delete the provisional ids from the log.

**N11. The quantity that triggers the reversal, k, is decided by an unblinded adjudicator (A l.160, l.120, l.27).**
k counts sampled records "included after adjudication". The human author adjudicates every
disagreement and every "adjudicate". The human author also reads the audit copy (expected outcomes
and title/abstract codes for about 40 named records) and has access to the orchestrator-only
candidates file, which flags `in_sample`. The adjudicator therefore knows which records are re-check
records and that k ≥ 2 or so means screening 797 more papers. Screener-level blinding (S l.158 "mixed
into ordinary batches, without a flag") does not reach the person who sets k.
*Minimal fix:* adjudicate re-check records blind to their sample status, or have a second person adjudicate them.

### Minor

- **N9. The 150 cap first appears in v1.2 (A l.154; script `CAP = 150`).** It was set by the author who wrote the script that counts the candidates. It is not in v1.1 or any ledger row. *Fix:* state when and why the cap was set.
- **N10. "Adjudicate" is merged into "pass" for agreement (A l.81, l.118).** This hides a screener that adjudicates heavily. The 3-way decision has no stated kappa category for the human validation (A l.119), and there is no cap or report of adjudicate rates although one human adjudicates everything. *Fix:* report adjudicate rates per screener and define the validation categories.
- **N12. Blinding is by instruction only (S l.3-5, l.142-143).** criteria-v1.1.md, criteria-v1.2.md and ta-recheck-candidates-v1.2.jsonl sit in the same repository the screener agents can read. S l.4 says the audit copy is "held by the orchestrator", but it is in the same folder. *Fix:* dispatch screeners with a working copy that excludes these files, or log their file reads.

---

## 3. Answers to the specific questions

- **Sample-of-100 design and its reversal rule:** not usable as written (N7, N8, N11). Its frame also depends on O1 (N6).
- **Include-for-adjudication default:** sound in principle, since it resolves M9. Reporting gaps only (N10). The real risk sits downstream: the person who adjudicates also sets k (N11).
- **Frozen-VLM exclusion:** it follows D0020's wording and is disclosed in the reversal clause, so it is not post hoc. Two problems remain. The "work that produced the weights" clause cannot be decided from the file (N4), and frozen-VLM systems cannot be coded consistently as X1 or X2 (N3). It also removes a large part of the frozen-backbone unified literature from RQ5. That is a scope consequence the authors should see stated with its count before they answer the reversal option.
- **O1 (pose and motion as 3D):** the default and the tag are reasonable. The rule text conflicts with itself (N5), and leaving O1 open breaks the re-check estimate and the coding of removed records (N6).
- **Blinding of the screener file:** clean. The grep for record ids returns 0, and the file contains no outcomes. The remaining exposure is in enforcement (N12) and at the adjudicator (N11).

## 4. Result that would force rejection of "v1.2 is ready"
Run a blind dual pilot with the screener copy only on passed records from these classes: VLA with
text-vocabulary actions, text DLMs emitting SMILES or puzzles, frozen-VLM decoders, unified systems
built on released weights, and humanoid motion. Any decision- or code-level disagreement traced to
D1/R12, R9(2), R10 b3 or D4 rejects the claim.
