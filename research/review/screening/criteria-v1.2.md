# Full-text screening criteria v1.2 (audit copy; supersedes v1.1, which stays as history)

```yaml
agent: dlm-expert
date: 2026-10-16
brief: revise criteria v1.1 to resolve red-team audit 2026-10-16 (2 fatal, 15 major, 11 minor)
sources_examined:
  - research/review/audits/2026-10-16-redteam-criteria-v1.1.md (all)
  - research/review/screening/criteria-v1.1.md (own previous version)
  - research/review/protocol.md s1, s2, s3, s4, s10 (D0020, D0026, D0027)
  - research/review/coverage/census-codebook-v1.2.md B-1 to B-8
  - research/ledgers/decisions.jsonl D0020, D0026-D0031
  - title/abstract screening files read by script: screening/records.jsonl, screener-{A,B}/batch-*.jsonl,
    v2/batch-*.jsonl, v2/screener-{A,B}-batch-*.jsonl, v2/rescue/rescue-*.jsonl, v2/rescue/screener-R-rescue-*.jsonl
coverage: >
  No full text read. Record examples below are title/abstract level (E1); "expected" outcomes are
  what a rule gives if the full text confirms the abstract, not decisions. Counts in section 5 come
  from analysis/screening/ta_recheck_select.py and its log analysis/screening/ta-recheck-v1.2.log.
status: draft for gate-auditor / red-team re-check; not frozen; protocol, ledgers, other screening files untouched
```

## 0. Files and who may read them

| File | Content | Readers |
|---|---|---|
| `criteria-v1.2-screener.md` | **Normative rule text** (definitions D1-D4, rules R1-R14, code order, doubt rule, screener brief). No record ids, no outcomes. | Screeners A and B, the human validator, auditors |
| `criteria-v1.2.md` (this file) | Per-rule examples and reasons, the map of audit findings, the re-check design, the amendment and ledger proposals. Names record ids and title/abstract codes. | Orchestrator, human author, auditors. **Never given to screeners.** |
| `analysis/screening/ta-recheck-candidates-v1.2.jsonl` | Rule-selected title/abstract exclusions with their codes | Orchestrator only |

If the two criteria files differ, the screener copy governs and this file is corrected.

Scope. Full-text screening of every record that passed title/abstract screening (round 1 passes,
round 2 passes under D0030, rescue positives) and of the re-check sample of section 5. Records still
waiting for title/abstract screening (`v2/subscription-queue.jsonl`, 170 lines; `v2/title-resolved-queue.jsonl`)
are screened at title/abstract under the same rules as everything else (criteria-v1.md plus
SCREENER-BRIEF.md), so that stage stays uniform. Their exclusions join the re-check frame (section 5).

Timing, stated plainly. v1.1 and v1.2 were written after the title/abstract decisions on all records
above had been recorded and seen by the author, and before any full text was screened. The protocol
freeze (tag `protocol-v1`) has not been applied. Section 6 lists every rule whose reading could change
eligibility relative to how the title/abstract screeners applied the protocol. For each it gives a
justification from the protocol text or D0020, not from any observed record.

---

## 1. Examples and reasons per rule (the rule text is in the screener copy)

| Rule | Positive (expected include) | Negative (expected exclusion) | Reason (protocol / RQ) |
|---|---|---|---|
| R1 | none with an id in the ambiguity file (screener statements of "about 40" DLM-pointing titles and "about 20" full-text reads are self-reports without ids) | M14799: X3 if the body is a survey without own experiments; `x3_scope` true if it covers DLMs | s4 step 5: full-text codes from s2; PRISMA 16b |
| R2 | M13102 if its body is English | M13102 X8 if its body is Catalan | I3: full text in English |
| R3 | M18918 / M09530 (TrustLDM, same title apart from a plural): one study, one retained | the other report: X5 if the retained one is included | X5; PRISMA counts studies and links reports |
| R4 | M07984 (latent diffusion decoded to text): D2 holds | M17320 (encryption "block diffusion"): X0 | I1 needs a diffusion component |
| R5 | M09782 if its drafter is trained with a masked denoising objective over a range of rates | M12594 (AR parallel decoder, dLLMs as baselines): X0 | I1 concerns the paper's own method (D3) |
| R6 | M07984 (text from decoded latents); M13234 (a DLM regenerates slot strings), then R14 | M13881 (tag diffusion), M14484 (noise on entity boundaries): X2, xsub nlp-label | I1(a): output includes natural-language text |
| R7 | M12793 if its natural-language results (Text8, OpenWebText per screener note) are confirmed; the puzzle tasks do not decide | M14279 (SMILES): X1; M16987 (Newick trees from DNA): X1; M12789 (pragma design from a program): X2 | census B-7; I1 names text, not symbol strings |
| R8 | M12793 (as above) | M18900 (Ising-model unmasking, no text): X1, xsub theory-no-text | I1 output test; naming never decides |
| R9 | none named (masked-diffusion ASR or captioning would be R6 includes) | M15918 (LLM-written prompts into an image diffusion model): X2, xsub pipeline; M12951 (autoregressive text with flow on cell profiles): X1 by step (1), D0020 | protocol X2; D0020's X1 widening |
| R10 | M04162 (JanusFlow) if the full text confirms one shared backbone | M15792 (pixel-diffusion decoder on a *frozen* VLM): not shared, not joint, so components are judged separately (expected X1, xsub pipeline); M17285 (VLM and DiT via skill calls): X2 unless jointly trained | D0020 verbatim |
| R11 | M15992 (Möbius: motion understanding and generation in shared attention) is I1(b) under the literal "3D" reading if motion is 3D geometry; `body3d: true` | M12951 (cell expression): not a D4 modality | D0020 list; open item O1 |
| R12 | M08652 only if the model also produces text from images (b1) and is one model | M15897 (navigation actions from a diffusion VLM): X2 if a language instruction is its input | D0020: actions are X1 or non-modality; I1(b) needs understanding |
| R13 | M08140 / M16168 (pplx-embed) if the paper performs the diffusion pretraining or compares with a causal backbone; also checked under R3 | M04871 (INFO-SEDD on synthetic and Ising data): X1 | I1 "analyses"; census B-2; RQ3 |
| R14 | M14428 (a hybrid decoding strategy for LLaDA) by (a); M15731 (six models, one a DLM, on ICD-11 coding: under D1 the DLM's code strings are text) by (b) | M17603: X7 if the DLM step is never compared with another generator and its settings are never varied | protocol X7; (b) and (c) are the RQ2 and RQ4 evidence that make a finding "model-level" |

---

## 2. Map of audit findings to changes

| Finding | Change in v1.2 (screener copy unless stated) | Status |
|---|---|---|
| **F1** R4 vs R6 on continuous and latent text diffusion | R6 now tests the decoded output of the generation path ("judge the decoded output, not the variable denoised"); D1 lists embeddings and hidden states as not text only as final outputs. M07984 is now a positive for both R4 and R6. The brief no longer restates the old list. | resolved |
| **F2** R7(b)/R8(b) admitted non-text outputs on naming | R7(b) and R8(b) deleted. R7: a model whose vocabulary is a non-language alphabet produces no text "however the paper names it". R8: include only if a text result of the paper's own method exists. D1 makes the vocabulary the test. Bio "diffusion language models" (M16270 and the audit's titles) are excluded at full text unless they produce natural-language text. | resolved |
| M1 R4 vs R5 on authors' own DLM baselines | D3 defines the paper's own method (contribution plus ablations; baselines excluded). R4 now reads "the paper's own method (D3)" and "baselines do not count". R5 points to R4. | resolved |
| M2 masked-generative, MLM and continuous flow in I1(a) | D2 requires training over a range of corruption levels **and** multi-step (or distilled) generation. A fixed-rate MLM is out. Continuous flow matching and masked diffusion over a range of rates are in. This is disclosed as a reading in amendment item (3). | resolved |
| M3 vocabulary vs task output | D1: "The test is the vocabulary, not the task." Task-specific heads and special task tokens are not text. Examples corrected (M15731 is text; dWorldEval progress tokens are not). Extractive outputs: generated as vocabulary tokens means text; positions or boundaries mean not text. | resolved |
| M4 R9 literal test vs X2 examples | R9 X2 test now asks whether text is an input of the diffusion component, "written by a person or by another component such as an LLM". LLM-to-diffusion pipelines are X2, consistent with the examples. | resolved |
| M5 R13 vs R14 on fine-tuning | R13 applies when the final model does not generate; R14 when it generates. R14(a) reads "non-generative fine-tuning is R13, not (a)". R13's X0 is consistent with D2(ii) (nothing in the paper generates by diffusion). | resolved |
| M6 R10 b3 widened and narrowed D0020; b1 undecidable | b3 quotes D0020 verbatim, with "shared weights" and "jointly trained" each defined operationally. Frozen understanding models with a newly trained generator are no longer eligible. Jointly trained systems with a text interface are eligible. b1: understanding is shown in the paper's own experiments, or stated in the paper for the same weights (a reprinted number about different weights does not count). The RQ5 justification is withdrawn. | resolved (follows D0020) |
| M7 R11 closed list post hoc | R11/D4 uses D0020's list verbatim. "3D" takes its literal, unqualified reading (any 3D geometry, including 3D human pose and motion), which matches B-4's open "perceptual signal". Records that depend on it carry `body3d: true` so they can be removed without re-screening. Open item O1 goes to the user and professor. | resolved (follows D0020) |
| M8 X2-first hides boundaries; mismatch with B-8 | X1 and X2 are now disjoint (R9 steps 1-3), so the order is census B-8 exactly (X8, X3, X5, X4, X0, X1, X2, X7). New `xsub` field (t2x, nlp-label, pipeline, ar-text+nontext, theory-no-text, nontext) gives the NLP-label and pipeline counts. | resolved |
| M9 doubt defaults to exclusion | New decision value "adjudicate" (section D). Doubt never excludes; every adjudicate goes to the human author. For agreement statistics, pass = include or adjudicate. | resolved |
| M10 protocol s4 steps 3-4 missing | Section 4 below: human validation sample, kappa against the human, rerun threshold, agreement report. Also in D0032. | resolved |
| M11 brief breaks blinding | Screener copy contains no record id and no outcome (checked: `grep -cE "\b[MR][0-9]{4,5}\b"` gives 0). The brief points only to it and forbids other files. Re-check sample records are mixed into normal batches, unflagged. | resolved |
| M12 hand-picked, irreproducible 19-record list | Replaced by `analysis/screening/ta_recheck_select.py`: seven declared regex classes over all title/abstract exclusions (round 1 dual, round 2 dual, rescue single). It gives 797 candidates, above the 150 cap, so the full check is dropped and a seeded random sample of 100 is used (section 5). | resolved |
| M13 option (b) selective; RQ2-context into synthesis | RQ2-context removed. Sampled records included at full text enter the review with extraction and appraisal, flagged `source: ta-recheck-sample` for a sensitivity analysis. The sample estimates the loss across all 797 and carries a reversal rule. | resolved |
| M14 written after seeing decisions; timing misstated | Timing stated in section 0 and in the amendment. Section 6 lists every reading that could change eligibility, with protocol-based justifications. | resolved |
| M15 one quote; no check; RQ tags without evidence | Evidence is a list, one verbatim quote per deciding condition. Quotes are string-matched by script; a quote not found is returned once, then goes to adjudication. `rq_loc` gives a table or figure for each RQ2-RQ5 tag. Not done: a string-match script is not written yet (it is listed for the orchestrator in section 4). | resolved in rules; script pending |
| m1 X6 in eligibility order | X6 is out of the order; "not retrieved" files are reported in PRISMA's reports-not-retrieved box. The retrieval steps of v1.1 s3 are unchanged. | resolved |
| m2 off-topic surveys on the positioning list | `x3_scope` flag; only X3 records with `x3_scope: true` go to the positioning list. | resolved |
| m3 X5 nominal; dup_of disagreement; retention vs s3 | X5 is set by script. The retained report is the one screened under protocol s3 (latest arXiv version, published version resolved separately). A `dup_of` disagreement goes to the human. PRISMA reports X5 records as additional reports of included studies. | resolved |
| m4 first-version date and search date | X8 date is filled by script from metadata (arXiv v1 date or earliest publication date) against the per-source search date in `search-log.jsonl`. | resolved |
| m5 taxonomy surveys | R1: a survey that proposes a taxonomy or framework without new experiments or proofs is X3. | resolved |
| m6 mm undefined for non-D4 inputs | mm values "text", "multimodal", "other". | resolved |
| m7 rule single-valued | `rules` is a list. | resolved |
| m8 brief omissions | Brief adds doubt, R3, R5, and a model id and version in the screener field. | resolved |
| m9 subscription queue criteria | Scope paragraph (section 0). | resolved |
| m10 reversal clause too narrow | D0032 reversal lists every contested reading. | resolved |
| m11 unverifiable counts | Marked in section 1 (R1) as screener self-reports without ids. | resolved |

Rejected findings: none. One part of a finding is only partly met: M15's quote-check script is
specified but not written. It is an orchestrator task before screening starts.

---

## 3. Rule-level differences from v1.1 (summary)

R4 and R5 restricted to the paper's own method. R6 judges decoded output. R7(b) and R8(b) deleted.
R9 rewritten (disjoint X1/X2, D0020 step, xsub). R10 b3 follows D0020 verbatim (frozen-backbone
systems now out, jointly trained text-interface systems in). R11 follows D0020's unqualified "3D"
(motion and pose now in, tagged). R13/R14 split by generative versus non-generative use. Code order
follows census B-8. "Adjudicate" added. RQ2-context removed. Evidence per condition.

---

## 4. Agreement, human validation and adjudication (protocol s4 at full text)

1. Screeners A (Claude Sonnet) and B (Claude Opus) screen independently from the same files with the screener copy; model id and version are recorded in every row.
2. Reported before reconciliation: pass (include or adjudicate) versus exclude, with raw agreement, Cohen's kappa with a bootstrap interval, p_pos and p_neg, and prevalence and bias indices (as in `analysis/screening/agreement_v2.py`). Code-level agreement on records both screeners exclude. Agreement per rule (from `rules`).
3. **Human validation (protocol s4 step 3):** a human author independently screens a random 15 percent of the full-text set (at least 100 records) with the screener copy, blind to both screeners. Kappa of each screener against the human, with confusion tables. If either screener is below 0.70, the screener copy is revised and the full-text stage is rerun.
4. The human author resolves every disagreement, every "adjudicate" and every `dup_of` disagreement. The count is reported.
5. Before screening starts, the orchestrator writes two scripts: (a) a quote check that string-matches every evidence quote against the converted full text after whitespace and hyphenation normalisation; (b) the X8 date fill and the X5 assignment.

---

## 5. Changes from the title/abstract rules, and the re-check of title/abstract exclusions

Title/abstract decisions are not re-opened (D0030). The table says whether a v1.2 reading is more
inclusive than the rules the title/abstract screeners applied, and which declared class of the
selection script covers it.

| # | v1.2 reading | More inclusive than title/abstract? | Script class |
|---|---|---|---|
| 1 | Binary decisions plus "adjudicate"; no "unclear" | no | - |
| 2 | X8 language read from the body (R2) | yes, for non-English titles with English abstracts | C1 |
| 3 | Generic theory and methods: a text result anywhere in the paper is enough (R8) | yes, the body can show text experiments the abstract does not | C2 |
| 4 | Inference, serving and hardware methods never X7; comparison or settings sweep is a model-level finding (R14) | yes | C3 |
| 5 | Literal "3D" includes 3D human pose and motion (R11) | yes, title/abstract screeners mostly coded motion X1 | C4 |
| 6 | Text is defined by vocabulary (D1): OCR, captions, transcripts, slot and entity strings generated as tokens | yes, for records excluded on the task rather than the output | C5 |
| 7 | Jointly trained systems with a text interface are one model (R10 b3) | yes; frozen-backbone systems become *less* eligible, which full-text screening of passed records handles | C6 |
| 8 | D2 includes continuous flow matching and masked diffusion over a range of rates without diffusion wording | yes, for records coded X0 | C7 |
| 9 | Disjoint X1/X2 with xsub; order as census B-8 | no (codes only) | - |
| 10 | Non-language vocabularies never text; naming never decides (R7, R8) | no (narrower) | - |
| 11 | X3 scope flag, X5/X6 handling, evidence format | no | - |

**Selection (reproducible).** `python analysis/screening/ta_recheck_select.py`. It applies classes C1-C7
(regexes declared in the script) to every title/abstract exclusion. The frames are: round 1 records
both screeners excluded, round 2 records both screeners excluded, and rescue records the single
screener excluded. The log `analysis/screening/ta-recheck-v1.2.log` gives, as of this run (candidates
file SHA-256 a9180fe4...d79a, recorded in full in the log):

- exclusions in frame: D1 210, D2 999, R 4,073 (total 5,282);
- candidates matching at least one class: **797** (D1 74, D2 278, R 445). By class (overlapping): C1 2, C2 321, C3 65, C4 167, C5 253, C6 36, C7 10.

797 is above the 150 cap, so the full re-check is dropped. **Proposal:** take a simple random sample
of 100 candidates (seed 20261016, drawn by the same script; the ids are in the log). Draw it again
after the subscription-queue and title-resolved records have been screened at title/abstract and
their exclusions added to the frame. The current sample ids are provisional. Both full-text screeners
screen the sample mixed into ordinary batches, without a flag. Report it in its own PRISMA box
("title/abstract exclusions re-checked at full text, random sample"). Estimate the number of
eligible records lost as k/100 x 797 (k = sampled records included after adjudication), with a Wilson
95 percent interval scaled to the candidate count. **Reversal**, mirroring D0027: if the estimate
exceeds about 2 percent of the included studies, all candidates are screened at full text.
Exclusions that match no class are not re-checked. That is a stated limitation: the classes are
regex proxies, written before any re-check result is seen. Sampled records included at full text
enter the review with extraction and appraisal, flagged `source: ta-recheck-sample`. The primary
synthesis is repeated without them as a sensitivity analysis.

---

## 6. Readings that could change eligibility, with justifications that do not depend on records

1. **X0 code** (no diffusion component). Criteria v1 and census B-8 already used it; protocol s2 does not list it. No eligibility change; it names the failure of I1's component requirement.
2. **D2, the diffusion component.** Protocol I1 covers "a diffusion model ... in discrete or continuous state space". Criteria v1 lists "masked or absorbing diffusion, discrete flow matching, and diffusion on embeddings or the simplex". The range-of-corruption-levels requirement is what separates a diffusion model from a fixed-rate masked language model. Multi-step generation is what makes it a generative diffusion process. Continuous flow matching is the continuous-state counterpart of the discrete flow matching already listed.
3. **I1(b) one-model test.** D0020 verbatim, with "shared weights" and "jointly trained" each defined by a fact stated in a method or training section.
4. **"3D".** D0020 writes "3D" without qualification; census B-4 says "another perceptual signal such as 3D shape". The literal reading includes any 3D geometry. D0020's explicit exclusions (robot actions, molecules) are kept. **Open item O1 for the user and professor:** "Do 3D human pose and motion count as '3D' under I1(b)?" Default until answered: yes (literal). If the answer is no, records with `body3d: true` are removed by script and the count is reported.
5. **I3/X8:** the language of the body decides. This reads I3 ("full text available in English") literally.
6. **Doubt:** "adjudicate" goes to the human. This follows protocol s4 step 4 (a human resolves disagreements) and the conservative convention of D0030.

---

## 7. For the orchestrator: proposed protocol s10 amendment and ledger row

```text
- <date> (D0032; full-text screening criteria v1.2: research/review/screening/criteria-v1.2-screener.md
  normative, criteria-v1.2.md audit copy; v1.1 superseded after red-team audit 2026-10-16). Written
  after the title/abstract decisions had been recorded and seen, before any full text was screened and
  before the freeze rule was applied. I1-I4 are unchanged; the following codes and readings govern
  full-text screening, each justified from the protocol text or the D0020 amendment, not from records.
  (1) Exclusion code X0: no diffusion component in the paper's own method. One code per excluded
  record, first applicable in the order X8, X3, X5, X4, X0, X1, X2, X7 (census codebook B-8); X1 and X2
  are made disjoint: X1 for a model that generates text autoregressively while its diffusion component
  generates only actions, trajectories, molecules or other outputs outside the I1(b) list (D0020), and
  for non-text diffusion without text input; X2 when text, written by a person or another component,
  is an input of a non-text diffusion component. Reports not retrieved (X6) are reported before
  eligibility.
  (2) Diffusion component (I1): trained to reverse a corruption applied over a range of corruption
  levels (masking or absorbing state, token substitution, Gaussian noise on embeddings, simplex or
  latents) or along a discrete or continuous flow-matching path, and generating in more than one step
  or by a sampler distilled from such a component; a fixed-rate masked language model is not one.
  (3) I1(a) is judged on the decoded output: text (a natural-language or code vocabulary) produced by
  the diffusion component in at least one result of the paper; naming a model a "language model"
  never establishes text output.
  (4) I1(b) applies D0020 verbatim: understanding (text from an image, video, audio or speech, or 3D
  input) shown in the paper or stated for the same weights; generation of that modality by a
  diffusion, masked-generative or flow component; one model with shared weights or one jointly
  trained system (a training stage updating both sides), not a pipeline of separately trained models.
  "3D" is read literally as any 3D geometry, including 3D human pose and motion, pending the
  authors' ruling (open item O1); such records are tagged.
  (5) I3: the language of the main body decides.
  (6) Full-text decisions are include, exclude or adjudicate; doubt is never resolved by exclusion;
  the human author adjudicates; a human screens a random 15 percent (at least 100) of the full-text set
  and a screener below kappa 0.70 against the human triggers revision and rerun (s4 step 3).
  (7) Title/abstract decisions are not re-opened. A declared, scripted query
  (analysis/screening/ta_recheck_select.py) selects title/abstract exclusions in classes where
  these readings are more inclusive (797 of 5,282 at the time of writing); a seeded random sample of
  100 is screened at full text and reported in its own box, with the loss estimated; if the estimate
  exceeds about 2 percent of included studies, all candidates are screened.
```

```json
{
  "id": "D0032",
  "decision": "Full-text screening uses criteria v1.2 (normative: research/review/screening/criteria-v1.2-screener.md, which names no record and no outcome; audit copy: criteria-v1.2.md), replacing v1.1 after the red-team audit of 2026-10-16 (2 fatal, 15 major, 11 minor; every finding mapped in criteria-v1.2.md section 2). (1) X0 added; one code per record in census B-8 order (X8, X3, X5, X4, X0, X1, X2, X7) with X1 and X2 disjoint and an xsub field; X6 reported before eligibility. (2) Diffusion component defined by training over a range of corruption levels or a flow-matching path plus multi-step (or distilled) generation. (3) I1(a) judged on decoded text output (natural-language or code vocabulary); naming never decides. (4) I1(b) follows D0020 verbatim (shared weights or one jointly trained system); '3D' read literally including 3D human pose and motion, tagged body3d, pending the authors' ruling (open item O1). (5) I3 on the language of the body. (6) Decisions include, exclude or adjudicate; doubt goes to the human author; evidence quote per deciding condition, string-matched by script; human validation of a random 15 percent (at least 100) with kappa 0.70 rerun threshold (protocol s4 step 3). (7) Title/abstract decisions are not re-opened; analysis/screening/ta_recheck_select.py selects 797 of 5,282 title/abstract exclusions in classes where v1.2 is more inclusive; above the cap of 150, so a seeded random sample of 100 (seed 20261016, redrawn after the subscription and title-resolved queues are screened) is screened at full text in its own PRISMA box, with the loss estimated; included sample records enter the review flagged for sensitivity analysis.",
  "options": ["criteria v1.1 as written", "criteria v1.2 with D0020 verbatim and a random-sample re-check", "criteria v1.2 with a full re-check of all 797 candidates"],
  "evidence": "research/review/audits/2026-10-16-redteam-criteria-v1.1.md; research/review/screening/criteria-v1.2.md; research/review/screening/criteria-v1.2-screener.md; analysis/screening/ta_recheck_select.py; analysis/screening/ta-recheck-v1.2.log; protocol.md s2, s4, s10; census-codebook-v1.2.md B-1 to B-8; D0020, D0027, D0030",
  "owner": "orchestrator (user delegated expert judgement)",
  "reversal": "any of: the authors rule that 3D human pose and motion are not '3D' (remove body3d records by script); a referee or the professor rejects the D2 reading (masked diffusion over a range of rates, continuous flow matching) or the decoded-output test for continuous and latent text diffusion; the professor wants frozen-backbone VLM-plus-decoder systems counted as unified (protocol amendment and rescreen of R10 exclusions); NLP label or span diffusion is ruled text output; the re-check sample estimates a loss above about 2 percent of included studies (screen all candidates); a pilot shows two screeners cannot apply a rule without discussion (rule rewritten before screening continues)"
}
```
