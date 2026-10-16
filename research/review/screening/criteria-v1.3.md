# Full-text screening criteria v1.3 (audit copy; supersedes v1.2, which stays as history)

```yaml
agent: dlm-expert
date: 2026-10-16
brief: revise criteria v1.2 after the red-team re-audit of 2026-10-16 (adopt with fixes; 9 new major N1-N8, N11; 3 minor N9, N10, N12; 7 v1.1 findings partly resolved)
sources_examined:
  - research/review/audits/2026-10-16-redteam-criteria-v1.2.md (all)
  - research/review/screening/criteria-v1.2.md and criteria-v1.2-screener.md (own previous version)
  - research/review/protocol.md s2, s4, s10 (D0020); census-codebook-v1.2.md B-4, B-7, B-8
  - analysis/screening/ta_recheck_select.py and its outputs
coverage: >
  No full text read. Record examples are title/abstract level (E1); "expected" outcomes are what a rule
  gives if the full text confirms the abstract, not decisions. Every number in section 5 comes from
  analysis/screening/ta-recheck-v1.2.log, ta-recheck-oc-v1.3.txt and the frozen frame and sample files
  named there; scripts were run on 2026-10-16.
status: draft for the red-team's check of the fixes; not frozen; protocol, ledgers and other screening files untouched
```

## 0. Files and who may read them

| File | Content | Readers |
|---|---|---|
| `criteria-v1.3-screener.md` | **Normative rules** (D1-D4, R1-R14, code order, doubt and adjudication, briefs for Screeners A/B and adjudicator C). No record ids, no outcomes (`grep -cE "\b[MR][0-9]{4,5}\b"` gives 0). | Screeners A, B, C, the human validator, auditors |
| `criteria-v1.3.md` (this file) | Examples, finding map, re-check design, amendment and ledger proposals. Names record ids and title/abstract codes. | Orchestrator, auditors. Not screeners or adjudicator C. |
| `analysis/screening/ta-recheck-frame-v1.3-frozen.jsonl`, `ta-recheck-sample-v1.3-frozen.json` | Frozen re-check frame (797) and sample (100), with title/abstract codes | Orchestrator only |
| `analysis/screening/quote_check.py` | Evidence-quote check, with `--self-test` (9/9 cases pass) | Orchestrator |

**Dispatch (N12).** Each screener or adjudicator session gets a dispatch folder outside the
repository working tree (in the scratchpad). The folder holds only `CONTRACT.md`,
`criteria-v1.3-screener.md`, the full-text files of its batch and, for C, the two screener rows per
record. The orchestrator checks each session's tool log for any read outside the folder; a session
that read outside it is discarded and its batch is rerun. Blinding is therefore enforced by
isolation and by a log check, not by instruction alone.

Scope, timing and the subscription queue are as in v1.2 section 0, with section 5 below replacing the
re-check paragraph. v1.3 was written after the title/abstract decisions had been seen and before any
full text was screened.

---

## 1. Examples and reasons per rule (rule text: screener copy)

Changes from v1.2 are marked **(v1.3)**.

| Rule | Positive (expected include) | Negative (expected exclusion) | Reason |
|---|---|---|---|
| R1 | none with an id (the "about 40" and "about 20" counts are screener self-reports without ids) | M14799: X3 if the body is a survey without own experiments | s4 step 5; PRISMA 16b |
| R2 | M13102 if its body is English | M13102: X8 if its body is Catalan | I3 |
| R3 | M18918 / M09530: one study, one retained | the other report: X5 | X5; PRISMA counts studies |
| R4 | M07984 (latent diffusion decoded to text) | M17320 (cryptographic "block diffusion"): X0 | I1 needs a diffusion component |
| R5 | M09782 if its drafter meets D2 | M12594 (AR parallel decoder, dLLM baselines): X0 | D3 |
| R6 | M07984; M13234 (slot strings are words; then R14) | M13881 (tags), M14484 (span boundaries): X2, nlp-label | I1(a) |
| R7 **(v1.3)** | M12793 only through its Text8/OpenWebText results (R6); its puzzle outputs are not text | M14279 (SMILES): X1; a text DLM fine-tuned only to emit SMILES or grids is also not text; M12789 (pragma design from a program): X2 | protocol I1 ("natural-language text"); census B-7 |
| R8 | M12793 | M18900 (Ising unmasking): X1, theory-no-text | I1 output test |
| R9 **(v1.3)** | none named | M15918 (LLM prompts into an image diffusion model): X2, pipeline; M15792 (prompt through a frozen VLM into a pixel-diffusion decoder): X2, pipeline, if the method states that the prompt conditions the decoder (v1.2 expected X1; corrected); M12951 (AR text plus flow on cell profiles): X1, ar-text+nontext | protocol X2; D0020 |
| R10 **(v1.3)** | M04162 (JanusFlow) if the file states one shared backbone or joint training | M17285 (VLM and DiT via skill calls): b3 fails unless the file states joint training, then X2 pipeline; any system whose file does not describe how its released unified weights are shared or trained: b3 fails | D0020 verbatim, decided from the file |
| R11 **(v1.3)** | M15992 (Möbius, motion understanding and generation): I1(b) under the literal "3D" reading if the file shows shared parameters; `body3d: true`, `code_if_o1_no` filled | M15235 (HumanExpert, humanoid behaviour): an action, not 3D, if the paper evaluates its motions by robot execution; M12951: not a D4 modality | D0020 list; D4 order; open item O1 |
| R12 **(v1.3)** | M08652 only if its file shows text output (b1) and b3 | M15897 (navigation actions): X2 if a language instruction conditions it; actions written as text-vocabulary tokens are still not text | D0020; D1 content test |
| R13 | M08140 / M16168 if the paper performs the diffusion pretraining or compares with a causal backbone | M04871 (INFO-SEDD, synthetic and Ising data): X1 | census B-2; RQ3 |
| R14 **(v1.3)** | M14428 (hybrid decoding for LLaDA) by (a); M15731 by (b) only if the DLM's outputs in the paper are natural-language words (D1). If they are bare ICD-11 identifiers, R6 fails and the record is X2, nlp-label | M17603: X7 if the DLM step is never compared or varied | protocol X7 |

---

## 2. Map of findings to changes

### 2.1 New findings of the re-audit

| Finding | Change (screener copy unless stated) | Status |
|---|---|---|
| **N1** D1 made SMILES or chess written by a text model "text" | D1 rewritten as a **content** test: text = natural language or source code. SMILES, biological sequences, game moves, grids, identifiers, numbers alone and action content are not text, "whatever tokenizer or vocabulary produces it". The phrases "chess move" and "SMILES string" are gone. R7 adds that this holds also for a text DLM fine-tuned to emit such content. This is narrower than v1.2 and the title/abstract rules, so the re-check frame needs no new class. | resolved |
| **N2** D1 vs R12 on action tokens | D1 lists robot actions, trajectories, waypoints and progress or success signals as not text "also when written with ordinary text-vocabulary tokens"; R12 points to D1 and D4(1). The two rules now say the same thing. | resolved |
| **N3** X1 vs X2 undecidable through encoders | R9(2): X2 if the method states that text conditions the diffusion component "by any path: directly, through a text encoder, or through an LLM, VLM or MLLM (frozen or trained)". Tie-breaks: text plus other conditions is X2; if the paper does not state that text reaches the diffusion component, X1. xsub precedence is fixed (ar-text+nontext, nlp-label, pipeline, t2x, theory-no-text, nontext). The M15792 example is corrected to X2. Decidable from the method section alone. | resolved |
| **N4** b3 needed facts from outside the file | R10: b1-b3 are decided "from statements in the screened file only". b3 holds if the file states shared parameters or a joint training stage; "If the file states neither (i) nor (ii), b3 fails." Consequence, stated here: a paper that uses released unified weights without describing them is judged component by component. | resolved |
| **N5** D4 "3D coordinates" vs its exclusions | D4 is now an ordered rule. (1) Exclusions override: actions, trajectories, waypoints, joint commands, anything executed on a robot or vehicle, molecules, proteins and the rest. (2) Then 3D geometry. Humanoid case: evaluated by robot execution means action; evaluated as human motion means 3D. | resolved |
| **N6** frame depends on O1; removed records lack a code | The frame is fixed now (section 5) and does not depend on O1. The flip definition, not the frame, changes with O1. Screeners and C fill `code_if_o1_no` for every `body3d` record, so an O1 = no ruling is applied by script: those records move to their stated code, K is recounted, and the result is a sensitivity analysis, not a redraw. Default O1 = literal D0020 "3D". | resolved |
| **N7** reversal rule undefined and underpowered | Section 5.2: the decision quantity is K, the sampled records included after blind adjudication. **Reverse** (screen all 797 at full text) **if K ≥ 2**, which is the same as F̂ = K × 797/100 ≥ 15.9. The tolerable loss is fixed now at L = 16 records. Operating characteristics: P(trigger) = 0 / 0.079 / 0.265 / 0.617 at 0 / 4 / 8 / 16 true flips (0.826 at 24, 0.927 at 32). The rule is never triggered at zero flips. Power at L is 0.62, stated as a limitation. If not reversed, K, F̂ and the exact one-sided 95% upper bound for F (22 at K = 0, 35 at K = 1) are reported. Frames are reported separately in the sample (R 63, D2 28, D1 9); the rule uses the pooled K. | resolved; power limited |
| **N8** provisional sample, redraw allowed | Frame and sample frozen now: `ta_recheck_freeze.py` writes `ta-recheck-frame-v1.3-frozen.jsonl` (sha256 a9180fe4...d79a, the v1.2 candidates file unchanged) and `ta-recheck-sample-v1.3-frozen.json` (100 ids, seed 20261016, sha256 95886765...7ac6c). The script refuses to overwrite either file with different content. The subscription and title-resolved queues get **their own** frame from the same class queries after their title/abstract screening, with the same design (all candidates if ≤ 150, else a seeded sample of 100 with the same K ≥ 2 rule); never a redraw of this frame. | resolved |
| **N11** k set by an unblinded adjudicator | Section D and the adjudicator brief: every disagreement and every "adjudicate" in the whole full-text set goes first to **Screener C**, a Claude model in a fresh session. C sees only the screener copy, the full text and the A and B rows. C is not told which records are re-check records, and the sample records are mixed into the ordinary queue unflagged. **K is computed from the A/B agreements plus C's rulings.** The human author then resolves records as protocol s4 requires, for the review's final set. For sample records, the human's rulings are reported next to C's but do not change K. | resolved |
| N9 cap of 150 first appears in v1.2 | The cap was given in the orchestrator's revision brief of 2026-10-16 ("too large (say >150)"). That brief was written before the selection script existed or was run, so the cap did not depend on the count. The cap is now in the ledger row. | resolved |
| N10 adjudicate merged into pass | Section 4: adjudicate rate per screener is reported. The three-category (include/exclude/adjudicate) agreement is reported as well as pass/exclude. The human validator decides include or exclude only, and the screener-versus-human tables are 3 × 2. | resolved |
| N12 blinding by instruction only | Section 0: dispatch folders outside the working tree and a tool-log check. | resolved |

### 2.2 The seven v1.1 findings that were partly resolved

| v1.1 finding | Closed by |
|---|---|
| F2 naming loophole | N1 (content test; R7) |
| M3 vocabulary vs task | N1, N2 (content, not vocabulary, decides) |
| M4 R9 vs examples | N3 |
| M6 R10 b3 vs D0020 | N4 |
| M7 R11 post hoc closure | N5, N6 (ordered D4; O1 is a sensitivity analysis via `code_if_o1_no`) |
| M8 X1/X2 disjointness | N3 (X2 requires a stated text condition; X1 covers everything else) |
| M15 quote check missing | `analysis/screening/quote_check.py`: verbatim match tolerant to NFKC forms, quote and dash variants, whitespace, line-end hyphenation and markdown markup; ellipsis-split fragments must occur in order; case kept; self-test 9/9; exit status 1 on any miss |

Not done: M08480 (EndoCoT), named by the re-audit as missed by the classes, is not added by hand.
The frame is defined by its declared queries only; this is stated as a limitation.

---

## 3. Rule-level differences from v1.2

- D1 is a content test.
- D4 is an ordered rule, with exclusions first and a humanoid tie-break.
- R7 covers fine-tuned text DLMs.
- R9(2) counts text conditioning by any path, with tie-breaks and an xsub order.
- R10 decides b1-b3 from the file only.
- R12 is aligned with D1.
- Adjudicator C is added, with a brief.
- `code_if_o1_no` is a new field.
- Screeners work only in a dispatch folder.

---

## 4. Agreement, validation and adjudication

1. Screeners A (Claude Sonnet) and B (Claude Opus) screen independently from dispatch folders. The model id and version are in every row.
2. `quote_check.py` runs on every batch. A missing quote is returned to the screener once; if it is still missing, the record goes to C.
3. Reported before reconciliation:
   - three-category agreement and pass/exclude agreement, with kappa and bootstrap interval, p_pos, p_neg, and prevalence and bias indices;
   - the adjudicate rate per screener;
   - code-level agreement on joint exclusions;
   - agreement per rule.
4. Adjudicator C rules on every disagreement and every adjudicate, blind (section 2.1, N11). C's agreement with the human author is reported.
5. **Human validation (protocol s4 step 3).** A human author screens a random 15% of the full-text set (at least 100 records), include or exclude, blind to A, B and C. Kappa of each screener against the human uses 3 × 2 tables. A screener below 0.70 triggers revision of the screener copy and a rerun.
6. The human author resolves the final set (protocol s4 step 4). Counts of C rulings overturned are reported.

---

## 5. Re-check of title/abstract exclusions (frozen design)

### 5.1 Frame and sample
- **Classes.** C1-C7 as in v1.2 section 5, declared in `ta_recheck_select.py`. v1.3's changes are all narrower or code-only, so no class is added.
- **Frame.** Run of 2026-10-16: 5,282 title/abstract exclusions (round 1 dual 210, round 2 dual 999, rescue single 4,073) and **797 candidates** (74, 278, 445). These are frozen in `ta-recheck-frame-v1.3-frozen.jsonl`. 136 candidates match C4 (3D body) only.
- **Sample.** Simple random sample of **100**, seed 20261016, frozen in `ta-recheck-sample-v1.3-frozen.json`. By frame: R 63, D2 28, D1 9; 22 are C4-only.
- **Dispatch.** Sample records are mixed unflagged into ordinary full-text batches for A and B.
- **Subscription and title-resolved queues.** These get their own frame and design (section 2.1, N8).

### 5.2 Reversal test (fixed now)
- **Decision quantity.** K, the number of sampled records included at full text after A/B agreement or C's blind ruling, under the default O1.
- **Rule.** If K ≥ 2 (F̂ ≥ 15.9 ≥ L = 16 rounded), all 797 candidates are screened at full text. Otherwise the review reports K, F̂ and the exact one-sided 95% upper bound for F.
- **Operating characteristics** (`ta_recheck_oc.py`, hypergeometric, N = 797, n = 100; output `ta-recheck-oc-v1.3.txt`, sha256 7f6499ce...5570):

  | true flips F in frame | 0 | 4 | 8 | 16 | 24 | 32 |
  |---|---|---|---|---|---|---|
  | P(trigger), K ≥ 2 | 0.000 | 0.079 | 0.265 | 0.617 | 0.826 | 0.927 |
  | for comparison, K ≥ 1 | 0.000 | 0.416 | 0.660 | 0.885 | 0.962 | 0.988 |
  | for comparison, K ≥ 3 | 0.000 | 0.007 | 0.067 | 0.325 | 0.598 | 0.789 |

- **Why K ≥ 2.**
  - K ≥ 1 fires with probability 0.42 when only 4 records are lost, which is well below the tolerance, and would turn a single borderline ruling into 797 extra full-text screenings.
  - K ≥ 3 has power 0.33 at L.
  - K ≥ 2 never fires at zero flips, rarely fires below L/2, and has power 0.62 at L and 0.83 at 1.5 L.
- **Why L = 16.** The D0027 tolerance, "about 2 percent" of in-scope records, applied to D0029's estimate of about 650 in-scope round-2 records gives 13. Round-1 records make the included set larger, so 16 is at most 2% of any included set of 800 or more. L was fixed before any re-check record was screened.
- **O1 = no.** If the authors rule that pose and motion are not "3D", K is recounted from `code_if_o1_no` with the same frame and sample, and both results are reported.
- **Limitations, stated in the review.** The classes are regex proxies, so exclusions outside them are not re-checked. Power at L is 0.62. Sampled records included at full text enter the review flagged `source: ta-recheck-sample`, and the synthesis is repeated without them.

---

## 6. Readings that could change eligibility (justified from protocol text, not records)

1. X0 code. Unchanged from v1.2.
2. D2, the diffusion component. Unchanged.
3. **D1 content test (v1.3).** I1 says "natural-language text"; census B-7 says that strings that are not language do not count. Code is kept, as in criteria v1 ("Diffusion models for code ... include"). This reading is narrower than v1.2.
4. I1(b) follows D0020 verbatim, decided from statements in the file. The consequence for unified models whose files do not describe their weights is stated in section 2.1 (N4).
5. "3D" is the literal D0020 reading, with an ordered exclusion list that keeps D0020's own exclusions (robot actions, molecules) on top. **Open item O1** goes to the user and professor. Default: literal. If they rule otherwise, a sensitivity analysis follows via `code_if_o1_no`.
6. I3 is read on the language of the body. Doubt goes to blind adjudication, then the human author.

---

## 7. For the orchestrator: proposed protocol s10 amendment and ledger row

```text
- <date> (D0032; full-text screening criteria v1.3: research/review/screening/criteria-v1.3-screener.md
  normative, criteria-v1.3.md audit copy; v1.1 and v1.2 superseded after red-team audits of
  2026-10-16). Written after the title/abstract decisions had been recorded and seen, before any full
  text was screened and before the freeze rule was applied. I1-I4 are unchanged; the following codes
  and readings govern full-text screening, each justified from the protocol text or D0020.
  (1) Code X0: no diffusion component in the paper's own method. One code per excluded record, first
  applicable in the order X8, X3, X5, X4, X0, X1, X2, X7 (census B-8). X2: the method states that text
  conditions a non-text diffusion component by any path (directly, through a text encoder, or through
  an LLM, VLM or MLLM); X1: every other non-text diffusion output, including a model with
  autoregressive text whose diffusion component generates actions, molecules or other outputs outside
  the I1(b) list (D0020). Reports not retrieved (X6) are reported before eligibility.
  (2) Diffusion component: trained to reverse a corruption applied over a range of corruption levels,
  or along a discrete or continuous flow-matching path, and generating in more than one step or by a
  sampler distilled from such a component.
  (3) I1(a): the diffusion component produces text, read by content: natural-language words or
  sentences, or source code; chemical and biological sequences, game and puzzle states, identifiers,
  actions and other non-language content are not text whatever tokens carry them; naming never decides.
  (4) I1(b): D0020 verbatim (understanding: text from an image, video, audio or speech, or 3D input;
  generation of that modality by a diffusion, masked-generative or flow component; one model with
  shared weights or one jointly trained system), decided from statements in the screened file only.
  "3D" is read literally (3D geometry, including 3D human pose and motion), with D0020's exclusions
  (robot actions and anything executed on a robot, molecules) taking precedence; whether pose and motion
  count is open item O1 for the authors, and each such record also carries the code it would get if not.
  (5) I3: the language of the main body decides.
  (6) Decisions are include, exclude or adjudicate; disagreements and adjudicate go to a blind
  adjudicating model and then to the human author; evidence quotes are verified by script; a human
  screens a random 15 percent (at least 100) of the full-text set and a screener below kappa 0.70
  against the human triggers revision and rerun (s4 step 3).
  (7) Title/abstract decisions are not re-opened. A declared, scripted query selected 797 of 5,282
  title/abstract exclusions in classes where these readings are more inclusive (cap of 150 for a full
  re-check set in advance); a frozen random sample of 100 (seed 20261016) is screened at full text,
  blind to its sample status, and reported in its own PRISMA box. If at least 2 sampled records are
  included, all 797 are screened (tolerable loss fixed at 16 records; trigger probability 0, 0.08,
  0.27, 0.62 at 0, 4, 8, 16 true flips). Queues screened later at title/abstract get their own frame
  and the same design.
```

```json
{
  "id": "D0032",
  "decision": "Full-text screening uses criteria v1.3 (normative: research/review/screening/criteria-v1.3-screener.md, no record ids or outcomes; audit copy criteria-v1.3.md), replacing v1.1 and v1.2 after red-team audits of 2026-10-16 (v1.1: 2 fatal, 15 major, 11 minor; v1.2 re-audit: adopt with fixes, 9 major, 3 minor; every finding mapped in the audit copies). (1) X0 added; one code per record in census B-8 order; X2 = text conditions a non-text diffusion component by any path, X1 = all other non-text diffusion (incl. D0020's autoregressive-text class); xsub field; X6 reported before eligibility. (2) Diffusion component: range of corruption levels or flow-matching path plus multi-step or distilled generation. (3) Text is natural language or source code by content; naming never decides. (4) I1(b) is D0020 verbatim, decided from the screened file only; '3D' literal with D0020's exclusions first; open item O1 (pose and motion) for the authors, default literal, with code_if_o1_no recorded for a sensitivity analysis. (5) I3 on the body language. (6) Include, exclude or adjudicate; disagreements and adjudicate go to a blind adjudicating model (Screener C) and then the human author; quotes checked by analysis/screening/quote_check.py; human validation of a random 15 percent (at least 100) with kappa 0.70 rerun threshold; screeners work in isolated dispatch folders with a tool-log check. (7) Title/abstract decisions not re-opened; ta_recheck_select.py selects 797 of 5,282 exclusions (above the cap of 150 set in the orchestrator's brief before the script ran); frozen random sample of 100 (seed 20261016; ta-recheck-sample-v1.3-frozen.json) screened blind to sample status; full re-check of the 797 if K >= 2 sampled includes (tolerable loss 16 records; operating characteristics in analysis/screening/ta-recheck-oc-v1.3.txt); later queues get their own frame.",
  "options": ["criteria v1.2 as written", "criteria v1.3 with frozen sample and K >= 2 reversal", "criteria v1.3 with a full re-check of all 797 candidates", "criteria v1.3 with K >= 1 reversal"],
  "evidence": "research/review/audits/2026-10-16-redteam-criteria-v1.1.md; research/review/audits/2026-10-16-redteam-criteria-v1.2.md; research/review/screening/criteria-v1.3.md; criteria-v1.3-screener.md; analysis/screening/ta_recheck_select.py, ta_recheck_freeze.py, ta_recheck_oc.py, quote_check.py; ta-recheck-v1.2.log; ta-recheck-oc-v1.3.txt; protocol.md s2, s4, s10; census-codebook-v1.2.md B-4, B-7, B-8; D0020, D0027, D0029, D0030",
  "owner": "orchestrator (user delegated expert judgement)",
  "reversal": "any of: the authors rule on O1 (pose and motion), applied by code_if_o1_no as a sensitivity analysis or primary analysis as they decide; a referee or the professor rejects the D2 reading, the content test for text, or the decoded-output test for continuous and latent text diffusion; the professor wants frozen-backbone systems or unified models whose files do not describe their weights counted as unified (protocol amendment and rescreen of R10 exclusions); NLP label or span diffusion is ruled text output; K >= 2 in the re-check sample (screen all 797); a blind pilot shows two screeners cannot apply a rule without discussion"
}
```
