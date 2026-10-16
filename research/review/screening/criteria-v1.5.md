# Full-text screening criteria v1.5 (audit copy; supersedes v1.4, which stays as history)

```yaml
agent: dlm-expert
date: 2026-10-16
brief: revise criteria v1.4 after the fourth red-team audit of 2026-10-16 (adopt with listed fixes; 3 blocking majors W1-W3, 8 minors n1-n8)
sources_examined:
  - research/review/audits/2026-10-16-redteam-criteria-v1.4.md (all)
  - research/review/screening/criteria-v1.4-screener.md and criteria-v1.4.md (own previous version; repository copies identical to the delivered files by sha256)
  - research/USER-ACTIONS-2026-10-16.md item 6a
  - research/review/coverage/census-codebook-v1.2.md B-4, B-7; research/review/protocol.md s2, s4, s10 (D0020); research/ledgers/decisions.jsonl D0027, D0029, D0030
  - ~/.claude/tools/graph_memory.py (project_name, repo; vault layout Projects/<name>/sessions) and ~/.claude/graph-memory.json (vault path)
  - analysis/screening/ta_recheck_select.py (frames, DIFF), ta_recheck_c8_v14.py (EXISTING_DLM), frozen frame and sample
coverage: >
  No full text read; examples are title/abstract level (E1). One read-only count was run on 2026-10-16 (C8 query
  inside the frozen frame: 16 records, 2 of them sampled), reproducing the audit's figure. quote_check.py v1.5
  --self-test was run with python -I in the output folder: 32/32, exit 0. The frozen frame, sample, OC and C8
  files are unchanged and no script that produces them changed. Model ids are cited from the Claude Code harness
  model list, 2026-10-16 (orchestrator's confirmation), not checked by me. NOT done: the blind dual pilot.
status: draft for the red-team's check of the fixes; not frozen; protocol, ledgers and other screening files untouched
```

## 0. Files and who may read them

| File | Content | Readers |
|---|---|---|
| `criteria-v1.5-screener.md` | **Normative rules** (D1-D5, R1-R14, code order, doubt and adjudication with the adjudication route, briefs with session rules). No record ids, no outcomes (`grep -cE "\b[MR][0-9]{4,5}\b"` gives 0). | Screeners A, B, C, the human author when adjudicating, auditors |
| `criteria-v1.5.md` (this file) | Examples, finding map, re-check design, amendment and ledger proposals. Names record ids and title/abstract codes. | Orchestrator, auditors. Not screeners, not C, not the human author while adjudicating under Route H. |
| `analysis/screening/ta-recheck-frame-v1.3-frozen.jsonl`, `ta-recheck-sample-v1.3-frozen.json` | Frozen re-check frame (797) and sample (100), unchanged | Orchestrator only |
| `analysis/screening/ta-recheck-c8-candidates-v1.4.jsonl`, `ta-recheck-c8-v1.4.log`, `ta_recheck_c8_v14.py` | Class C8, unchanged (section 5.3) | Orchestrator only |
| `analysis/screening/ta-recheck-oc-v1.4.txt`, `ta_recheck_oc_v14.py` | Operating characteristics, unchanged | Orchestrator, auditors |
| `analysis/screening/quote_check.py` (v1.5) | Quote check: 6-40 words, contiguous, whole words, negation windows, link and tag handling; `--self-test` 32/32 | Orchestrator |
| `analysis/screening/c-run-log.jsonl` | First line: the adjudication route (written before the first full-text row); then one line per C session | Orchestrator, auditors |

**Dispatch and isolation (N12, m4, W3).**
- **Folder.** Each screener or adjudicator session starts with its working directory in its own
  dispatch folder outside the repository (in the scratchpad). The basename is
  `<role>-<batch>-<uuid4>` (for example `FA-b03-<uuid4>`, `FB-b03-<uuid4>`, `FC-q01-<uuid4>`), new
  for every session including reruns; the orchestrator checks that no basename has been used before.
  The folder holds only `CONTRACT.md`, `criteria-v1.5-screener.md`, the full-text files of the batch
  and, for C, the two screener rows per record.
- **Waiver.** The brief's SESSION RULES (screener copy section E, applied word for word to C) waive
  the user-level `~/.claude/CLAUDE.md` routines and the project routines for these sessions: no
  graph-memory (brief, init, sync, where, module, impact), no graphify, no Obsidian vault, no rtk, no
  skills, agents, web, MCP or tool search; Bash or PowerShell only with an explicit path inside the
  folder.
- **Isolation check, after every session.** The orchestrator flags the session if its transcript
  shows any of: (1) a Read, Grep, Glob, Edit or Write path outside the dispatch folder; (2) a Bash or
  PowerShell call whose command names no explicit path inside the dispatch folder; (3) a command
  containing `graph-memory`, `graph_memory`, `graphify`, `obsidian`, `vault` or `rtk`; (4) a Skill,
  Agent, WebFetch, WebSearch, ToolSearch or MCP call. It also checks the vault directory named in
  `~/.claude/graph-memory.json`: a folder `Projects/<dispatch basename>` there means graph-memory ran
  (graph_memory.py names a non-git folder's project after its basename), and the session is flagged
  even if its transcript check passed. A flagged session is discarded and its batch rerun with the
  same model and queue in a new folder; both are logged.
- **Correction of v1.4.** v1.4 (A l.130) said that the isolation check "detects any read" the
  user-level routine causes. That was wrong: graph-memory reads and writes the vault through Bash
  calls that carry no path, which a path list cannot see. v1.5 detects the call by name, flags every
  pathless Bash call, checks the vault for the dispatch basename, and unique basenames mean that even
  an undetected brief could not print another session's note.

Scope, timing and the subscription queue are as in v1.2 section 0, with section 5 below replacing the
re-check paragraph. v1.5 was written after the title/abstract decisions had been seen and before any
full text was screened.

---

## 1. Examples and reasons per rule (rule text: screener copy)

Changes from v1.4 are marked **(v1.5)**. No example id is in the frozen re-check sample (checked).

| Rule | Positive (expected include) | Negative (expected exclusion) | Reason |
|---|---|---|---|
| R1 | none with an id | M14799: X3 if the body is a survey without own experiments | s4 step 5; PRISMA 16b |
| R2 | M13102 if its body is English | M13102: X8 if its body is Catalan | I3 |
| R3 | M18918 / M09530: one study, one retained | the other report: X5 | X5; PRISMA counts studies |
| R4 | M07984 (latent diffusion decoded to text) | M17320 (cryptographic "block diffusion"): X0 | I1 needs a diffusion component |
| R5 | M09782 if its drafter meets D2 | M12594 (AR parallel decoder, dLLM baselines): X0 | D3 |
| R6 | M07984; M13234 (slot strings are words; then R14) | M13881 (tags), M14484 (span boundaries): X2, nlp-label, if the tag or span model is not text-pretrained (D5) | I1(a) |
| R7 **(v1.5)** | M12793 only through its Text8/OpenWebText results (R6); a paper that loads LLaDA or Dream weights and fine-tunes them only on SMILES, Sudoku or target-number equations: R14(a) (D5(i)), `nonlang_only: true` | M14279 (SMILES): X1 if its diffusion model is a recipe trained from random initialisation on SMILES; included by R14(a) only if the file states that it loads text-pretrained weights. "We adopt MDLM and train it on ZINC SMILES": not D5 (recipe), X1. A protein or DNA "diffusion language model": X1. M12789 (pragma design from a program): X2 | protocol I1; census B-7 with its exception (section 6 item 3) |
| R8 | M12793 | M18900 (Ising unmasking): X1, theory-no-text | I1 output test |
| R9 | none named | M15918: X2, pipeline; M15792: X2, pipeline, if the paper states that the prompt conditions the decoder; an AR-text model whose flow component generates cell profiles (id withheld, in the sample): X1, ar-text+nontext | protocol X2; D0020 |
| R10 | M04162 (JanusFlow) if the file states one shared backbone or joint training; frozen MLLM with LoRA active for understanding, trained jointly with the decoder: b3 by (ii) | M17285: b3 fails unless the file states joint training; frozen MLLM with query tokens or a connector and a trained decoder: b3 fails | D0020 verbatim; v1.1 M6 |
| R11 | M15992 (Möbius): I1(b) under the literal "3D" reading if the file shows shared parameters; `body3d: true` | M15235 (HumanExpert): an action if its main results evaluate the motions by robot execution; cell profiles: not D4 | D0020 list; D4 order; O1 |
| R12 **(v1.5)** | M08652 only if its file shows text output (b1) and b3 | M15897 (navigation actions): X2 if a language instruction conditions it; a text DLM fine-tuned to forecast object positions as numbers: trajectory, R12, not the R14 override | D0020; D1 |
| R13 | M08140 / M16168 if the paper performs the diffusion pretraining or compares with a causal backbone | M04871 (INFO-SEDD): X1 | census B-2; RQ3 |
| R14 **(v1.5)** | M14428 (hybrid decoding for LLaDA) by (a); M15731 by (b) if the compared DLM is text-pretrained (D5), whether its outputs are words or ICD-11 identifiers (`nonlang_only: true` in the second case) | M17603: X7 if the DLM step is never compared or varied | protocol X7; census B-7 |

---

## 2. Map of findings to changes

`S` = criteria-v1.5-screener.md, `A` = this file.

### 2.1 Blocking findings of the fourth audit (W1-W3)

| Finding | Change | Where |
|---|---|---|
| **W1** D5: loaded weights or published recipe? | **Weights, not recipe.** D5 is renamed "text-pretrained diffusion model" and holds only if the file states (i) that the paper loads pretrained weights that generate text, or (ii) that the paper itself pretrains the model on natural-language text or code in a stage it reports. A published architecture, objective or recipe (MDLM-, SEDD-, Plaid-type) trained from random initialisation only on non-language content is not D5, whatever it is called; if the file states neither (i) nor (ii), D5 fails. Justification: census B-7 keeps non-language strings only "as tasks of a model that is eligible on other grounds", and under protocol I1 a model is eligible if its "output includes natural-language text". Weights trained only on SMILES or Sudoku have never produced text, so that model is not eligible on other grounds; a recipe is a method, not a model. Text-pretrained weights, loaded or pretrained in the paper, do produce text. R7's example, R14(a) ("trains further or fine-tunes"), the R7 examples in A section 1 (the old A l.72 entry for M14279) and the C8 description (A 5.3) now say the same thing. D5(ii) also removes the own-pretraining asymmetry of n4. | S: D5, R7, R14; A: 1, 5.3, 6 item 3 |
| **W2** Haiku fallback | **Adopted, the orchestrator's suggestion: no model fallback.** Route F (C = claude-fable-5-1) only if the user approves any spend and a test session runs; otherwise Route H: disagreements and "adjudicate" rows go straight to the human author, and every count that would use C's rulings, K included, uses the A/B agreement rows plus the human author's decisions. Trigger, who decides, when and log location are one paragraph, identical in S section D, A section 4 and the D0032 row (checked by string comparison). claude-haiku-5-5 is never C: it made the title/abstract exclusions behind 445 of the 797 frame records and 63 of the 100 sampled records (D0029 rescue pass; audit of v1.4). Why not argue for another model: the only other listed models are A's and B's, and a screener cannot adjudicate its own disagreement. Cost, stated: under Route H the human author adds every disagreement and adjudicate of the whole full-text set to the 15 percent validation sample. **USER-ACTIONS item 6a must be updated by the orchestrator** to the same trigger (it still names the Haiku fallback); I could not edit it. | S: D, F; A: 4, 7 |
| **W3** isolation check blind to graph-memory | Brief: SESSION RULES that override the user-level and project routines (graph-memory, graphify, vault, rtk, skills, agents, web, MCP; Bash only with a path in the folder). Check: flags graph-memory, graphify, obsidian, vault and rtk calls by name, every pathless Bash or PowerShell call, every Skill, Agent, web, ToolSearch or MCP call, and a vault folder named after the dispatch basename. Unique basenames `<role>-<batch>-<uuid4>`. The false claim of v1.4 (A l.130) is corrected in A section 0. | S: header, E, F; A: 0 |

### 2.2 Minor findings of the fourth audit (n1-n8)

| Finding | v1.5 | Where |
|---|---|---|
| n1 negation guard one word; no minimum length | Fixed in quote_check.py: negation window of 6 words before and 3 words after the quote, within the same sentence; lexicon widened (lack/lacks/lacking/lacked, rather, instead, unlike, hardly, fail/fails/failed, absent, neglect(s), dont/doesnt/didnt/isnt/arent/wasnt/werent/cant/wont, any n't word, w/o); after the quote only strong negators (not, no, never, neither, nor, without, none); minimum 6 words (`too_short`). Self-test adds the audit's probes: "not, however,", "It is not the case that", "lacks", "w/o", "in neither stage" after, a 5-word quote. The brief's wording now matches the script ("no negation word in the 6 words before or the 3 words after it in the same sentence"). Residual, disclosed: qualifiers that are not negations ("only in stage 1", "which is kept frozen") outside the windows; the brief asks screeners to include such qualifiers. | quote_check.py; S E |
| n2 false rejections from markdown | Partly fixed: markdown link targets and HTML tags are removed on both sides (a footnote-marker `<sup>` element with its content); citations, case and page headers stay verbatim, and the brief says to copy citations as they appear and to split a passage cut by a page header. Self-test adds the link and footnote cases and a disclosed limitation (typed-out superscript). | quote_check.py; S E |
| n3 C8 "screened in full" overstated | Fixed in wording: C8 is a regex query on text-DLM terms (it also catches recipe-trained and protein or DNA models, which D5 then excludes). 16 frozen-frame records meet the C8 query (count rerun 2026-10-16, read-only); 2 of them are in the sample and are screened as sample records; the other 14 reach full text only if K ≥ 1. The 32 C8 records outside the frame are screened in full. Later queues: their C8 candidates go to full text in full, apart from the sampled union of C1-C7. | A: 5.3, 5.4, 7 |
| n4 own-pretraining asymmetry; from-scratch puzzle DLMs | Asymmetry removed by D5(ii). Disclosed: masked-DLM reasoning or puzzle papers trained from random initialisation only on Countdown, Sudoku or chess are X1 unless they report a text result; the review's RQ4 evidence on unmasking order therefore omits them, and the review says so. | S D5; A 6 item 3, 7 (3) |
| n5 trajectories as numbers; LaTeX | Numbers that the paper uses as positions, poses, waypoints or a path of an agent, robot, vehicle or object are a trajectory (R12), not a non-language string under the override. D1: markup counts when it carries words or a program; a formula or equation alone, in any notation including LaTeX, is not text. | S D1, R7; A 1 (R12) |
| n6 model ids self-reported; no A/B fallback | Ids cited from the Claude Code harness model list, 2026-10-16. The run log records the model id set in the harness dispatch, with the session's self-report beside it. A and B have no fallback model: if either cannot be run, full-text screening does not start (or stops) until a new decision is recorded (no Haiku: it made title/abstract decisions; no Fable: it is C). | S D, E; A 4 |
| n7 "about 650 in-scope records" | Now "about 650 in-scope records that pass the automation filter (D0029)", here and in the amendment and row. | A 5.2, 7 |
| n8 R14-over-R7 inclusions mixed into I1(a) | New row field `nonlang_only`; these records are counted and reported separately from text-output I1(a) inclusions, and the synthesis is repeated without them. | S R14, E, F; A 4, 7 |

### 2.3 Status of the third audit's findings (from the fourth audit)

V2, V3, V5, V6 and m1-m3, m5-m10 were resolved in v1.4 (mapped in criteria-v1.4.md section 2). The
two partly resolved findings are closed here: V1 by W1 (D5), V4 by W2 (route). m4 is closed by W3.

### 2.4 Deferred, with reasons

- **Blind dual pilot** (audit sections 5 and next_test): needs retrieved full texts and screener
  sessions. It should cover C8 records, records that train an MDLM/SEDD/Plaid recipe from scratch on
  SMILES, DNA or Sudoku, and a check of every transcript for graph-memory calls.
- **USER-ACTIONS item 6a** still describes the Haiku fallback; the orchestrator has to align it with
  the route paragraph (I cannot edit repository files).
- **C8 records inside the frozen frame outside the sample (14).** Screening them now would be cheap,
  but it would put non-sample frame records into full text outside the frozen design. I left the
  design unchanged and disclosed the gap; the orchestrator can decide to add them.
- **Non-negation qualifiers in quotes** and **typed-out superscripts**: not checkable by string
  matching; left to C or the human author.
- **Same-family screeners** (all Claude), **M08480**, **O1**, **DLM-backbone VLAs and TTS**: as in v1.4.

---

## 3. Rule-level differences from v1.4

- D1: markup counts only with words or a program; a formula alone (LaTeX included) is not text.
- D5: "text-pretrained diffusion model", weights not recipe; loading or own text pretraining must be
  stated.
- R7: the override names numbers used as positions or paths as trajectories (R12).
- R14(a): "trains further or fine-tunes"; new field `nonlang_only`.
- Section D: adjudication route F/H with trigger, decider, time and log; no model fallback for A, B
  or C.
- Briefs: SESSION RULES; quotes 6 to 40 words, qualifiers and negations included, citations as
  they appear; the adjudicator brief applies the session rules; human row format under Route H.

---

## 4. Agreement, validation and adjudication

1. Screeners A (claude-sonnet-5-5) and B (claude-opus-5-5) screen independently from dispatch folders.
   Model ids: Claude Code harness model list, 2026-10-16. Each row carries `FA-...` or `FB-...`; the
   orchestrator's log records the model id set in the harness dispatch and the session's self-report
   beside it. **No fallback for A or B:** if claude-sonnet-5-5 or claude-opus-5-5 cannot be run,
   full-text screening does not start (or stops) until a new decision is recorded.
2. `quote_check.py` (v1.5) runs on every batch. A quote with status `not_found`, `too_short`,
   `elided`, `negation_before` or `negation_after` is returned to the screener once; if it is still
   not accepted, the record goes to adjudication. Self-test on 2026-10-16, `python -I quote_check.py
   --self-test` in the output folder: 32/32 passed, exit 0.
3. Reported before reconciliation: three-category and pass/exclude agreement (kappa with bootstrap
   interval, p_pos, p_neg, prevalence and bias indices); adjudicate rate per screener; code-level
   agreement on joint exclusions; agreement per rule; inclusions with `nonlang_only: true` counted
   separately from text-output I1(a) inclusions.
4. **Adjudication route** (identical in S section D and the D0032 row):

   Adjudication route, fixed before the first full-text row of Screener A or B is written. Route F:
   adjudicator C is claude-fable-5-1, used only if both hold: (1) the user has approved in writing any
   usage-credit spend that claude-fable-5-1 draws on the user's plan, or has confirmed that it draws
   none; (2) a test session of claude-fable-5-1, started from the Claude Code harness with that model
   id, runs. Otherwise Route H: there is no model adjudicator; every disagreement between A and B and
   every "adjudicate" row goes straight to the human author, who is not told why a record is in the
   queue, and every count that would use C's rulings is computed from the A/B agreement rows plus the
   human author's decisions. The user decides (1); the orchestrator runs (2) and writes the route, the
   outcome of (1) and (2) and the date as the first line of analysis/screening/c-run-log.jsonl before
   the first full-text row of A or B. The route is not changed after that line, except that if
   claude-fable-5-1 later cannot be run, the rest of C's queue goes to the human author, logged in the
   same file. No other model is ever C.

   For the re-check this means: under Route H, **K = the sampled records that A and B both include
   plus the sampled records the human author includes** among those sent to adjudication. The human
   author adjudicates blind to sample status: the queue is unflagged, and the author does not open
   this file's section 5, the frame, sample or C8 files, or USER-ACTIONS notes about the re-check,
   until the queue is done. Why Haiku is excluded: it made the title/abstract exclusions behind 445 of
   the 797 frame records and 63 of the 100 sampled records (D0029 rescue pass).
5. **Run log** (`analysis/screening/c-run-log.jsonl`): line 1 is the route line above; then one line
   per C session when it ends: dispatch basename, model id set in the harness, the session's
   self-reported id, start and end time, queue file and sha256, output file and sha256 (or "none"),
   status (`complete`, `failed`, `discarded-isolation`, `rerun-of:<basename>`), reason. Every line is
   reported in the supplement. K uses the first complete session that passed the isolation check;
   K from every other complete session is reported beside it.
6. **Human validation (protocol s4 step 3).** A human author screens a random 15% of the full-text set
   (at least 100 records), include or exclude, blind to A, B and C. Kappa of each screener against the
   human uses 2 × 2 tables with "adjudicate" counted as include (D0030's convention); the 3 × 2 tables
   are also reported. A screener below 0.70 triggers revision of the screener copy and a rerun. Under
   Route H the validation sample is drawn and screened before the author sees the adjudication queue.
7. The human author resolves the final set (protocol s4 step 4). Counts of C rulings overturned are
   reported (Route F).

---

## 5. Re-check of title/abstract exclusions (frozen design)

### 5.1 Frame and sample (unchanged)
- **Classes.** C1-C7 as in v1.2 section 5, declared in `ta_recheck_select.py`.
- **Frame.** 5,282 title/abstract exclusions and **797 candidates** (D1 74, D2 278, R 445), frozen in
  `ta-recheck-frame-v1.3-frozen.jsonl`, sha256
  `a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a`.
- **Sample.** Simple random sample of **100**, seed 20261016, frozen in
  `ta-recheck-sample-v1.3-frozen.json`, sha256
  `958867658120c323446ee5692ec82702deb4464e0977a6030287ced035b7ac6c` (R 63, D2 28, D1 9; 22 C4-only).
- **Dispatch.** Sample records are mixed unflagged into ordinary full-text batches.

### 5.2 Reversal test (unchanged from v1.4 except wording)
- **Decision quantity.** K, the sampled records included at full text after A/B agreement or the
  adjudication route (C's blind ruling under Route F, the human author's under Route H), under the
  default O1. K counts full-text inclusions whether or not the inclusion is itself correct.
- **Rule.** If **K ≥ 1**, all 797 candidates are screened at full text. Otherwise the review reports
  K = 0 and the exact one-sided 95% upper bound for F, 22.
- **Tolerable loss.** **L = 13 records**: D0027's threshold, "more than about 2 percent of in-scope
  records", applied to D0029's "roughly 650 in scope that pass" the automation filter (0.02 × 650 =
  13). These 650 are the round-2 database records that pass the automation filter, not the in-scope
  set of the frame's three sources; L is a reference for the operating characteristics, not part of
  the trigger.
- **Operating characteristics** (`ta-recheck-oc-v1.4.txt`, sha256
  `3f9c610ed888a7cd7b204e2ba9ef55428add7a843ea095999b04ddded623aca7`):

  | true flips F in frame | 0 | 2 | 4 | 8 | 12 | **13 = L** | 16 | 24 | 32 |
  |---|---|---|---|---|---|---|---|---|---|
  | P(trigger), **K ≥ 1** | 0.000 | 0.235 | 0.416 | 0.660 | 0.802 | **0.827** | 0.885 | 0.962 | 0.988 |
  | for comparison, K ≥ 2 | 0.000 | 0.016 | 0.079 | 0.265 | 0.456 | 0.500 | 0.617 | 0.826 | 0.927 |

  With F = 0 and full-text false inclusions at a hypothetical rate r, P(K ≥ 1) = 0.221 / 0.394 /
  0.634 / 0.867 at r = 0.25 / 0.5 / 1 / 2 percent (assumptions, not estimates).
- **Why K ≥ 1, timing, O1 = no, limitations.** As in criteria-v1.4.md section 5.2. The adjudication
  route does not change the rule; under Route H the human author's decisions replace C's in K.

### 5.3 Supplementary class C8 (description corrected, n3)
C8 is a regex query, declared in `ta_recheck_c8_v14.py`: title/abstract exclusions coded X1 or X2
whose title or abstract has a diffusion word and a text-DLM term (`diffusion language model`,
`diffusion llm`, `dllm`, `large language diffusion`, `diffusion-based (large) language model`, `masked
diffusion language`, `llada`, `mdlm`, `sedd`, `plaid`, `diffusion large language`). It is a proxy: it
also catches recipe-trained models and protein or DNA "diffusion language models", which D5 then
keeps out; it exists to find papers that adapt text-pretrained weights.
- **Outside the frozen frame:** 32 records (D1 8, D2 24, R 0), at most 150, so **all 32 are
  screened at full text**; file `ta-recheck-c8-candidates-v1.4.jsonl`, sha256
  `6c4928af43387750941994f1bc36a7867ea14d8416a203cfd4377719e641e825`; log sha256
  `729bee67db74fa952c5560588c9ff5af433f2aeed9dbfc682b4fefd7e7d651d8`.
- **Inside the frozen frame:** 16 records meet the same query (read-only count, 2026-10-16). 2 are in
  the sample and are screened as sample records; **the other 14 reach full text only if K ≥ 1.** This
  gap is disclosed in the review.
- C8 records are flagged `source: ta-recheck-c8` and reported in their own PRISMA box.

### 5.4 Later queues
The subscription and title-resolved queues get their own frame after their title/abstract screening.
C1-C7 candidates: all if at most 150, otherwise a simple random sample of 100, seed 20261016 (the
`ta_recheck_select.py` call, `random.Random(seed).sample` over the candidate ids in (frame, id)
order), and the rule K ≥ 1, with operating characteristics on N' and L' (2 percent of that queue's
in-scope passes) reported before screening. **C8 candidates of a later queue that are not already C1-C7
candidates are all screened at full text**, as for the 32 above. Never a redraw of the frozen frame.

---

## 6. Readings that could change eligibility (justified from protocol text, not records)

1. X0 code. Unchanged.
2. D2, the diffusion component. Unchanged.
3. **Text by content, with B-7's exception, for text-pretrained weights only (v1.5).** Census
   codebook v1.2, B-7, in full: "**B-7 Scene text, OCR strings and captions [literal].** Words or
   sentences of a natural language count as natural-language text whatever their length or source
   (scene-text strings, OCR transcriptions, captions); code counts, as in the coder brief. Strings
   that are not language (SMILES, protein sequences, digit grids, abstract symbols) do not, except
   as tasks of a model that is eligible on other grounds. Reason: I1 sets no minimum length. (172)"
   Protocol I1 makes a model eligible when its "output includes natural-language text". Text-pretrained
   weights (loaded, or pretrained in the paper) meet that, so they are "eligible on other grounds",
   and a paper that trains further, fine-tunes, re-samples or compares them only on non-language
   strings is included (R14 over R7), recorded `nonlang_only: true` and reported separately. A
   recipe trained from random initialisation only on non-language strings has never produced text,
   so it is not eligible on other grounds (R7, X1). **Disclosed consequences:** (a) masked-DLM
   reasoning or puzzle papers trained from scratch only on Countdown, Sudoku or chess are X1 unless
   they report a text result, so the review's RQ4 evidence on unmasking order omits them; (b) a paper
   that pretrains its own text DLM and reports only non-language results is included through D5(ii),
   like a paper that loads someone else's weights. The override stops at actions and D4-modality
   outputs; whether DLM-backbone VLAs or speech models enter through R14 is left to the authors.
4. **I1(b): D0020 verbatim, decided from the file, with the Sides clause.** Unchanged from v1.4.
5. **"3D" literal, ordered exclusions, humanoid main-results test, open item O1.** Unchanged.
6. I3 is read on the language of the body. Doubt goes to the adjudication route, then the human author.

---

## 7. For the orchestrator: proposed protocol s10 amendment and ledger row

```text
- <date> (D0032; full-text screening criteria v1.5: research/review/screening/criteria-v1.5-screener.md
  normative, criteria-v1.5.md audit copy; v1.1-v1.4 superseded after red-team audits of 2026-10-16).
  Written after the title/abstract decisions had been recorded and seen, before any full text was
  screened and before the freeze rule was applied. I1-I4 are unchanged; the following codes and
  readings govern full-text screening, each justified from the protocol text, D0020 or census
  codebook v1.2.
  (1) Code X0: no diffusion component in the paper's own method. One code per excluded record, first
  applicable in the order X8, X3, X5, X4, X0, X1, X2, X7 (census B-8). X1 and X2 are decided in this
  order: X1 for a model with autoregressive text whose diffusion component generates actions,
  molecules or other outputs outside the I1(b) list (D0020), also when text conditions that
  component; otherwise X2 if the paper states that text conditions the non-text diffusion component
  by any path; otherwise X1. Reports not retrieved (X6) are reported before eligibility.
  (2) Diffusion component: trained to reverse a corruption applied over a range of corruption levels,
  or along a discrete or continuous flow-matching path, and generating in more than one step or by a
  sampler distilled from such a component.
  (3) I1(a): the diffusion component produces text, read by content: natural-language words or
  sentences, or source code; chemical and biological sequences, game and puzzle states, formulas and
  equations without words, identifiers, actions and other non-language content are not text whatever
  tokens carry them; naming never decides. Following census B-7 ("except as tasks of a model that is
  eligible on other grounds"), a paper that trains further, fine-tunes, re-samples or compares a
  text-pretrained diffusion model (weights it loads, or weights it pretrains on natural-language text
  or code) is eligible even when its outputs in the paper are only non-language strings; such records
  are reported separately. A published recipe trained from random initialisation only on non-language
  content is not such a model; masked-diffusion puzzle or reasoning papers of that kind are therefore
  excluded unless they report a text result. The exception does not extend to actions, trajectories
  or outputs in another modality.
  (4) I1(b): D0020 verbatim, decided from statements in the screened file only. A trained parameter
  counts on the understanding side only if the understanding output is computed with it; a frozen
  understanding model with trained query tokens, connector, generation-only adapters or decoder is a
  pipeline. "3D" is read literally (3D geometry, including 3D human pose and motion), with exclusions
  taking precedence: D0020's (robot actions, molecules), census B-4(ii)'s (trajectories and other
  non-perceptual outputs), and those added by these criteria (waypoints, joint or end-effector
  commands, outputs generated as robot or vehicle commands, proteins, cell profiles, graphs, tables,
  time series, 2D keypoints and trajectories); a human motion is an action only if the paper's main
  results evaluate it by robot execution. Whether pose and motion count is open item O1 for the
  authors, and each such record also carries the code it would get if not.
  (5) I3: the language of the main body decides.
  (6) Decisions are include, exclude or adjudicate. Screener A is claude-sonnet-5-5 and screener B
  claude-opus-5-5 (Claude Code harness model list, 2026-10-16), with no fallback models. Adjudication
  route, fixed before the first full-text row of Screener A or B is written. Route F: adjudicator C is
  claude-fable-5-1, used only if both hold: (1) the user has approved in writing any usage-credit spend
  that claude-fable-5-1 draws on the user's plan, or has confirmed that it draws none; (2) a test
  session of claude-fable-5-1, started from the Claude Code harness with that model id, runs.
  Otherwise Route H: there is no model adjudicator; every disagreement between A and B and every
  "adjudicate" row goes straight to the human author, who is not told why a record is in the queue,
  and every count that would use C's rulings is computed from the A/B agreement rows plus the human
  author's decisions. The user decides (1); the orchestrator runs (2) and writes the route, the
  outcome of (1) and (2) and the date as the first line of analysis/screening/c-run-log.jsonl before
  the first full-text row of A or B. The route is not changed after that line, except that if
  claude-fable-5-1 later cannot be run, the rest of C's queue goes to the human author, logged in the
  same file. No other model is ever C. Every adjudicator session is logged and reported. Screener and
  adjudicator sessions run in uniquely named dispatch folders, under session rules that waive the
  user-level and project routines, with an isolation check after each session. Evidence quotes are
  contiguous passages of 6 to 40 words verified by script. A human screens a random 15 percent (at
  least 100) of the full-text set, and a screener below kappa 0.70 against the human triggers revision
  and rerun (s4 step 3), and then resolves the final set (s4 step 4).
  (7) Title/abstract decisions are not re-opened. A declared, scripted query selected 797 of 5,282
  title/abstract exclusions in classes where these readings are more inclusive; this is above the
  cap of 150 first stated in criteria v1.2 (ta_recheck_select.py CAP = 150), which was written
  together with the script that counted the candidates. A frozen random sample of 100 (seed
  20261016) is screened at full text, blind to its sample status, and reported in its own PRISMA
  box. If at least 1 sampled record is included, all 797 are screened. Tolerable loss 13 records (2
  percent of about 650 in-scope records that pass the automation filter, D0027 and D0029); trigger
  probability 0.42, 0.66, 0.83, 0.89 at 4, 8, 13, 16 true flips; at zero sampled inclusions the exact
  one-sided 95 percent upper bound for the frame is 22 records. A supplementary regex query on
  text-DLM terms (class C8) selects 32 further exclusions outside the frame, all screened at full
  text; 14 records of the frame meet the same query outside the sample and are screened only if the
  reversal fires. Queues screened later at title/abstract get their own frame and the same design.
```

Ledger row. `tools/ledger.py add` numbers a row as (row count + 1) and lets the row's own `id` and
`ts` override that. The ledger's last id is already D0033, so the row must carry `"id": "D0032"`
explicitly. `ts` is the adoption time, filled when the row is appended.

```json
{
  "id": "D0032",
  "ts": "<adoption time, ISO 8601, set when appended>",
  "decision": "Full-text screening uses criteria v1.5 (normative: research/review/screening/criteria-v1.5-screener.md, no record ids or outcomes; audit copy criteria-v1.5.md), replacing v1.1-v1.4 after red-team audits of 2026-10-16 (v1.1: 2 fatal, 15 major, 11 minor; v1.2 re-audit: 9 major, 3 minor; v1.3 audit: 6 major, 10 minor; v1.4 audit: adopt with listed fixes, 3 major, 8 minor; every finding mapped in the audit copies). (1) X0 added; one code per record in census B-8 order; X1/X2 decided in R9's order (X1 for autoregressive text with a diffusion component generating actions, molecules or other outputs outside I1(b), D0020, also when text conditions it; else X2 if the paper states text conditions the non-text diffusion component by any path; else X1); xsub field; X6 reported before eligibility. (2) Diffusion component: range of corruption levels or flow-matching path plus multi-step or distilled generation. (3) Text is natural language or source code by content (formulas alone are not text); naming never decides; per census B-7 ('except as tasks of a model that is eligible on other grounds') a text-pretrained diffusion model (weights the paper loads, or pretrains on natural-language text or code) trained further, fine-tuned, re-sampled or compared only on non-language strings is eligible (R14 over R7), recorded nonlang_only and reported separately; a published recipe trained from random initialisation only on non-language content is not, so from-scratch puzzle or reasoning DLM papers without a text result are X1; not extended to actions, trajectories or other-modality outputs. (4) I1(b) is D0020 verbatim, decided from the screened file only; a trained parameter is on the understanding side only if the understanding output is computed with it; '3D' literal with exclusions first: D0020's (robot actions, molecules), census B-4(ii)'s (trajectories, other non-perceptual outputs) and these criteria's additions; human motion is an action only if the main results evaluate it by robot execution; open item O1 for the authors, with code_if_o1_no recorded. (5) I3 on the body language. (6) Include, exclude or adjudicate; screener A claude-sonnet-5-5, screener B claude-opus-5-5 (Claude Code harness model list, 2026-10-16), no fallback models. Adjudication route, fixed before the first full-text row of Screener A or B is written. Route F: adjudicator C is claude-fable-5-1, used only if both hold: (1) the user has approved in writing any usage-credit spend that claude-fable-5-1 draws on the user's plan, or has confirmed that it draws none; (2) a test session of claude-fable-5-1, started from the Claude Code harness with that model id, runs. Otherwise Route H: there is no model adjudicator; every disagreement between A and B and every \"adjudicate\" row goes straight to the human author, who is not told why a record is in the queue, and every count that would use C's rulings is computed from the A/B agreement rows plus the human author's decisions. The user decides (1); the orchestrator runs (2) and writes the route, the outcome of (1) and (2) and the date as the first line of analysis/screening/c-run-log.jsonl before the first full-text row of A or B. The route is not changed after that line, except that if claude-fable-5-1 later cannot be run, the rest of C's queue goes to the human author, logged in the same file. No other model is ever C. Every C session including failed, discarded and rerun ones is logged in that file and reported; reruns only for technical failure or a failed isolation check. Sessions run in uniquely named dispatch folders (<role>-<batch>-<uuid4>) under session rules that waive the user-level and project routines (graph-memory, graphify, vault, rtk, skills, agents, web, MCP); the isolation check flags paths outside the folder, pathless Bash calls, graph-memory, graphify, obsidian, vault or rtk calls, skill, agent, web or MCP calls, and a vault folder named after the dispatch basename. Evidence quotes are contiguous passages of 6 to 40 words checked by analysis/screening/quote_check.py v1.5 (sha256 fb6591bc95acad4ea7d3b98f9879daff6ae7f974101c8fdd55381549dbca27ba; self-test 32/32). Human validation of a random 15 percent (at least 100), adjudicate counted as include for kappa, 0.70 rerun threshold. (7) Title/abstract decisions not re-opened; ta_recheck_select.py selects 797 of 5,282 exclusions, above the cap of 150 first stated in criteria v1.2 (ta_recheck_select.py CAP = 150, written together with the script that counted the candidates); frozen frame analysis/screening/ta-recheck-frame-v1.3-frozen.jsonl (sha256 a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a) and frozen random sample of 100 (seed 20261016; ta-recheck-sample-v1.3-frozen.json, sha256 958867658120c323446ee5692ec82702deb4464e0977a6030287ced035b7ac6c) screened blind to sample status; full re-check of the 797 if K >= 1 sampled includes (K from A/B agreement plus C's rulings under Route F or the human author's under Route H); tolerable loss 13 records (2 percent of about 650 in-scope records that pass the automation filter, D0027 x D0029); trigger probability 0.416, 0.660, 0.827, 0.885 at 4, 8, 13, 16 true flips; exact one-sided 95 percent upper bound 22 at K = 0 (analysis/screening/ta-recheck-oc-v1.4.txt, sha256 3f9c610ed888a7cd7b204e2ba9ef55428add7a843ea095999b04ddded623aca7); supplementary regex class C8 on text-DLM terms (ta_recheck_c8_v14.py): 32 exclusions outside the frame, all screened at full text (ta-recheck-c8-candidates-v1.4.jsonl sha256 6c4928af43387750941994f1bc36a7867ea14d8416a203cfd4377719e641e825); 14 frame records outside the sample meet the same query and are screened only if the reversal fires; later queues get their own frame with the same classes, seed, cap, sample size and rule, and their C8 candidates screened in full.",
  "options": ["criteria v1.4 as written (Haiku fallback adjudicator, D5 undefined for recipes)", "criteria v1.5 with Route F/H adjudication and D5 as text-pretrained weights", "D5 also covering published recipes trained from scratch on non-language strings", "criteria v1.5 with K >= 2 reversal (L = 13, power 0.50)", "criteria v1.5 with a full re-check of all 797 candidates"],
  "evidence": "research/review/audits/2026-10-16-redteam-criteria-v1.1.md, -v1.2.md, -v1.3.md, -v1.4.md; research/review/screening/criteria-v1.5.md; criteria-v1.5-screener.md; analysis/screening/ta_recheck_select.py, ta_recheck_freeze.py, ta_recheck_oc.py, ta_recheck_oc_v14.py, ta_recheck_c8_v14.py, quote_check.py; ta-recheck-v1.2.log; ta-recheck-oc-v1.3.txt; ta-recheck-oc-v1.4.txt; ta-recheck-c8-v1.4.log; protocol.md s2, s4, s10; census-codebook-v1.2.md B-4, B-7, B-8; ~/.claude/tools/graph_memory.py; D0020, D0027, D0029, D0030",
  "owner": "orchestrator (user delegated expert judgement)",
  "reversal": "any of: the authors rule on O1 (pose and motion), applied by code_if_o1_no as a sensitivity analysis or primary analysis as they decide; a referee or the professor rejects the D2 reading, the content test for text, B-7's exception for text-pretrained diffusion models, the weights-not-recipe reading of D5, or the decoded-output test for continuous and latent text diffusion; the professor wants frozen-backbone systems or unified models whose files do not describe their weights counted as unified; the authors want DLM-backbone action or speech models included through R14; NLP label or span diffusion is ruled text output; K >= 1 in the re-check sample (screen all 797); a blind pilot shows two screeners cannot apply a rule without discussion, or a screener or adjudicator transcript shows a graph-memory call"
}
```
