# Full-text screening criteria v1.4 (audit copy; supersedes v1.3, which stays as history)

```yaml
agent: dlm-expert
date: 2026-10-16
brief: revise criteria v1.3 after the third red-team audit of 2026-10-16 (adopt with listed fixes; 6 blocking majors V1-V6, 10 minors m1-m10; still partial N7, N9, N11, N12, M6, M8, M15)
sources_examined:
  - research/review/audits/2026-10-16-redteam-criteria-v1.3.md (all)
  - research/review/audits/2026-10-16-redteam-criteria-v1.2.md (N7, N9, N11, N12); 2026-10-16-redteam-criteria-v1.1.md (M6, M8, M15)
  - research/review/screening/criteria-v1.3-screener.md and criteria-v1.3.md (own previous version, all)
  - research/review/screening/criteria-v1.md and v2/SCREENER-BRIEF.md (title/abstract rules, for the re-check classes)
  - research/review/protocol.md s2, s4, s10 (D0020 entry)
  - research/review/coverage/census-codebook-v1.2.md B-4 to B-8
  - research/ledgers/decisions.jsonl D0020, D0027-D0031 (and the id of the last row, D0033)
  - analysis/screening/quote_check.py, ta_recheck_select.py, ta_recheck_freeze.py, ta_recheck_oc.py; frozen frame, sample and OC files
coverage: >
  No full text read; record examples are title/abstract level (E1), and "expected" outcomes are what a rule
  gives if the full text confirms the abstract. New numbers come from two scripts run on 2026-10-16 in the
  output folder, which read the frozen frame and the title/abstract screening files and write nothing in the
  repository: ta_recheck_oc_v14.py (ta-recheck-oc-v1.4.txt) and ta_recheck_c8_v14.py (ta-recheck-c8-v1.4.log,
  ta-recheck-c8-candidates-v1.4.jsonl). quote_check.py v1.4 --self-test was run with python -I (19/19, exit 0).
  The frozen frame (797) and sample (100, seed 20261016) are unchanged: digests checked before and after.
  NOT done: the blind dual pilot the audit names in its section 5 (needs full texts and screener sessions).
status: draft for the red-team's check of the fixes; not frozen; protocol, ledgers and other screening files untouched
```

## 0. Files and who may read them

| File | Content | Readers |
|---|---|---|
| `criteria-v1.4-screener.md` | **Normative rules** (D1-D5, R1-R14, code order, doubt and adjudication, briefs for Screeners A/B and adjudicator C). No record ids, no outcomes (`grep -cE "\b[MR][0-9]{4,5}\b"` gives 0). | Screeners A, B, C, the human validator, auditors |
| `criteria-v1.4.md` (this file) | Examples, finding map, re-check design, amendment and ledger proposals. Names record ids and title/abstract codes. | Orchestrator, auditors. Not screeners or adjudicator C. |
| `analysis/screening/ta-recheck-frame-v1.3-frozen.jsonl`, `ta-recheck-sample-v1.3-frozen.json` | Frozen re-check frame (797) and sample (100), unchanged | Orchestrator only |
| `analysis/screening/ta-recheck-c8-candidates-v1.4.jsonl`, `ta-recheck-c8-v1.4.log` (new) | Supplementary class C8 (32 records, all to full text; section 5.3) | Orchestrator only |
| `analysis/screening/ta-recheck-oc-v1.4.txt`, `ta_recheck_oc_v14.py` (new) | Operating characteristics of the v1.4 reversal rule | Orchestrator, auditors |
| `analysis/screening/quote_check.py` (v1.4) | Evidence-quote check: contiguous, whole-word, negation guard; `--self-test` 19/19 | Orchestrator |
| `analysis/screening/c-run-log.jsonl` (to be created at the first C session) | One line per C session (section 4) | Orchestrator, auditors |

**Dispatch (N12, m4).** Each screener or adjudicator session starts with its working directory in
a dispatch folder outside the repository working tree (in the scratchpad), so the project
CLAUDE.md is not loaded. The folder holds only `CONTRACT.md`, `criteria-v1.4-screener.md`, the
full-text files of its batch and, for C, the two screener rows per record. The brief tells the
session that CONTRACT.md's pointers to files outside the folder, its graph-memory step and its YAML
report format do not apply (the JSON rows replace the report). **Isolation check, named:** after
each session the orchestrator lists every path in the session transcript's tool calls (Read, Grep,
Glob, Bash, Edit, Write) and every WebFetch or WebSearch call; any path outside the dispatch
folder or any web call is a breach. A breached session is discarded and its batch rerun with the
same model and queue; both runs are logged (section 4). Residual: the user-level
`~/.claude/CLAUDE.md` loads in every session; it holds no record id (grep), so it cannot leak
sample status, but its session-start routine (graph-memory) may run inside the folder.

Scope, timing and the subscription queue are as in v1.2 section 0, with section 5 below replacing the
re-check paragraph. v1.4 was written after the title/abstract decisions had been seen and before any
full text was screened.

---

## 1. Examples and reasons per rule (rule text: screener copy)

Changes from v1.3 are marked **(v1.4)**. Example ids are taken from the title/abstract records; none
of them is in the frozen re-check sample (checked against `ta-recheck-sample-v1.3-frozen.json`;
the one v1.3 example that was, under R9 and R11, is removed, m6).

| Rule | Positive (expected include) | Negative (expected exclusion) | Reason |
|---|---|---|---|
| R1 | none with an id | M14799: X3 if the body is a survey without own experiments | s4 step 5; PRISMA 16b |
| R2 | M13102 if its body is English | M13102: X8 if its body is Catalan | I3 |
| R3 | M18918 / M09530: one study, one retained | the other report: X5 | X5; PRISMA counts studies |
| R4 | M07984 (latent diffusion decoded to text) | M17320 (cryptographic "block diffusion"): X0 | I1 needs a diffusion component |
| R5 | M09782 if its drafter meets D2 | M12594 (AR parallel decoder, dLLM baselines): X0 | D3 |
| R6 | M07984; M13234 (slot strings are words; then R14) | M13881 (tags), M14484 (span boundaries): X2, nlp-label, **if** the tag or span model is trained by the paper and is not an existing text DLM (D5) | I1(a) |
| R7 **(v1.4)** | M12793 only through its Text8/OpenWebText results (R6); a paper that fine-tunes an existing text DLM (D5) only on SMILES, Sudoku or target-number equations: included by R14(a), R14 overriding R7 | M14279 (SMILES): X1 if its diffusion model is trained by the paper; a protein or DNA "diffusion language model" trained by the paper: X1 (a domain "language model" is not D5); M12789 (pragma design from a program): X2 | protocol I1 ("natural-language text"); census B-7 with its exception (section 6 item 3) |
| R8 | M12793 | M18900 (Ising unmasking): X1, theory-no-text | I1 output test |
| R9 **(v1.4)** | none named | M15918 (LLM prompts into an image diffusion model): X2, pipeline; M15792 (prompt through a frozen VLM into a pixel-diffusion decoder): X2, pipeline, if the paper states that the prompt conditions the decoder; an AR-text model whose flow component generates cell profiles (example id withheld, m6): X1, ar-text+nontext, also if the instruction conditions the flow component (R9 step 1, m1) | protocol X2; D0020 |
| R10 **(v1.4)** | M04162 (JanusFlow) if the file states one shared backbone or joint training; a frozen MLLM with LoRA adapters that the file says are active for understanding, trained in one optimisation with the diffusion decoder: b3 by (ii) | M17285 (VLM and DiT via skill calls): b3 fails unless the file states joint training; a frozen MLLM with learnable query tokens or a connector and a trained diffusion decoder: b3 fails (queries and connector are generation side); any system whose file does not describe how its released unified weights are shared or trained: b3 fails | D0020 verbatim ("not a pipeline of separately trained models"); v1.1 M6 |
| R11 **(v1.4)** | M15992 (Möbius, motion understanding and generation): I1(b) under the literal "3D" reading if the file shows shared parameters; `body3d: true`, `code_if_o1_no` filled | M15235 (HumanExpert, humanoid behaviour): an action if its main results evaluate the motions by robot execution; a text-to-motion paper whose only robot content is a retargeting demo stays 3D (m7); cell profiles: not a D4 modality | D0020 list; D4 order; open item O1 |
| R12 | M08652 only if its file shows text output (b1) and b3 | M15897 (navigation actions): X2 if a language instruction conditions it; actions written as text-vocabulary tokens are still not text; R14's override does not reach actions | D0020; D1 content test |
| R13 | M08140 / M16168 if the paper performs the diffusion pretraining or compares with a causal backbone | M04871 (INFO-SEDD, synthetic and Ising data): X1 | census B-2; RQ3 |
| R14 **(v1.4)** | M14428 (hybrid decoding for LLaDA) by (a); M15731 by (b) if the compared DLM is an existing text DLM (D5): included whether its outputs are words or bare ICD-11 identifiers (identifiers are non-language strings, so R14 overrides R7; v1.3 expected X2 nlp-label for identifiers, corrected) | M17603: X7 if the DLM step is never compared or varied | protocol X7; census B-7 |

---

## 2. Map of findings to changes

Line references: `S` = criteria-v1.4-screener.md section, `A` = this file's section.

### 2.1 Blocking findings of the third audit

| Finding | Change | Where |
|---|---|---|
| **V1** R7 vs R14 for a text DLM fine-tuned only on non-language output; B-7's exception dropped | R7 now states the precedence: **R14 overrides R7 for non-language strings**. A paper that generates with an existing text diffusion model and meets R14(a), (b) or (c) is included even if every output is a non-language string; R7 decides alone for diffusion components that are not existing text DLMs. B-7 is quoted in full in R7 and in A section 6 item 3, with its exception. New definition **D5** (existing text diffusion model) makes "existing text diffusion model" decidable from the file and keeps domain "language models" (protein, DNA, chemical) outside it. The override stops at actions (R12, D0020) and D4-modality outputs (R10, R9), which B-7 does not address. D1 adds "arithmetic expressions or equations without words" and "mathematical solutions written in words" to settle the target-number puzzle boundary. The M15731 example is corrected (A section 1). Consequence for the re-check: v1.4 is more inclusive than the title/abstract rules for this class, so a supplementary class C8 is declared (A section 5.3). | S: D1, D5, R7, R12, R14; A: 1, 5.3, 6 |
| **V2** quote_check.py accepted elided quotes that drop a negation | **Ellipses are forbidden**: a quote is one contiguous passage; an ellipsis matches only an ellipsis in the file, and an elided quote gets status `elided`. Two further guards: a match must sit on whole-word boundaries (no "shared" inside "unshared", no "autoregressive" inside "non-autoregressive"), and an occurrence directly after a negation word gets status `negation_before`. The screener brief now defines quotes the same way (contiguous, no ellipsis, start with a preceding negation, two entries if split). Self-test: the audit's two probes and eight more adversarial or regression cases added; 19/19 pass with `python -I` (A section 4). | `quote_check.py`; S: E (EVIDENCE), F |
| **V3** "F̂ ≥ 15.9 ≥ L = 16" false; L = 16 unsupported | L restated from the files only: **L = 13** (D0027 "about 2 percent" × D0029 "roughly 650 in scope that pass"). No included-set size is assumed. The reversal rule is changed to **K ≥ 1** (acceptance number 0): power 0.827 at L = 13 (K ≥ 2 would give 0.500). The false inequality is removed; F̂ at K = 1 is 8.0. Operating characteristics recomputed with the ta_recheck_oc.py logic on the frozen frame (A section 5.2). | A: 5.2, 7 |
| **V4** adjudicator C's model not fixed; reruns possible | **C = claude-fable-5-1**, fixed now, before any full-text row exists; A = claude-sonnet-5-5 and B = claude-opus-5-5 are pinned too. Pre-declared fallback: claude-haiku-5-5, only if Fable cannot be run, established and logged before the first A or B full-text row. Every C session is logged in `c-run-log.jsonl` and reported, including failed, discarded and rerun sessions; reruns only for technical failure or a failed isolation check, same model and queue; K comes from the first complete run that passed the isolation check, and K from every other complete run is reported beside it. | S: D, E, F; A: 4 |
| **V5** b3 contradicts itself for a frozen MLLM with trained LoRA or query tokens | b3 gains a **Sides** clause: a trained parameter is on the understanding side only if the understanding output of b1 is computed with it. LoRA or adapters inside the understanding model count on the understanding side only if the file states or reports understanding with them active; query tokens, connectors, projectors, decoders and generation-only adapters are generation side, even when queries pass through the MLLM. A frozen understanding model is not a common set of trained parameters for (i). Hence frozen MLLM + queries/connector + trained decoder fails b3; frozen MLLM + understanding-active LoRA trained jointly with the decoder meets (ii). Justified from D0020 ("one jointly trained system, not a pipeline of separately trained models") and census B-4 ("components trained or fine-tuned jointly"): parameters that never touch the understanding output cannot make understanding and generation one jointly trained system. | S: R10 (b3); A: 1, 6 item 4 |
| **V6** unsupported provenance of the cap of 150 | The D0032 row and amendment item (7) now say: "cap of 150 first stated in criteria v1.2 (ta_recheck_select.py CAP = 150), written together with the script that counted the candidates; no earlier record of it exists". The claim about the orchestrator's brief is removed, also from this file (old A section 2.1 N9 row). The D0020 misattribution (m9) is fixed in the same row: the execution clause and the other added exclusions are attributed to these criteria, not to D0020. | A: 2.2 (N9), 7 |

### 2.2 Items still partly resolved after the third audit

| Item | v1.4 status | Where |
|---|---|---|
| N7 reversal rule | resolved by V3: rule K ≥ 1, L = 13 from the files, OC stated including the weakness (at K = 0 the exact one-sided 95% upper bound is 22 > L) | A 5.2 |
| N9 cap of 150 | resolved by V6: provenance stated as what the files show (first stated in v1.2 with the script); not claimed to be independent of the count | A 7 |
| N11 adjudicator | resolved by V4: model fixed, run log, rerun rule | S D, F; A 4 |
| N12 blinding | partly: isolation check named; CONTRACT.md conflict settled in the brief; project CLAUDE.md not loaded (dispatch cwd outside the repository). Residual: user-level CLAUDE.md (m4) | A 0 |
| M6 b3 vs D0020 | resolved by V5 (Sides clause) | S R10 |
| M8 X1/X2 disjointness | resolved by m1: the table no longer claims disjointness; R9's order decides, and R9 step 1 states that it holds also when text conditions the component | S R9, C |
| M15 quote check | resolved by V2 | quote_check.py |

### 2.3 Minor findings of the third audit

| Finding | v1.4 | Where |
|---|---|---|
| m1 X1/X2 disjointness false for R9(1); amendment (1) self-contradictory | fixed: section C text and amendment (1) say R9's order decides and R9(1) is X1 even with a text condition | S C, R9; A 7 |
| m2 kappa with 3 × 2 tables undefined | fixed: for kappa against the human, "adjudicate" counts as include (the screener did not exclude; same convention as D0030's "include or unclear passes"); the 3 × 2 tables are reported descriptively | A 4 |
| m3 later-queue seed and tolerance undeclared | fixed: same classes C1-C8, seed 20261016, cap 150, n = 100, rule K ≥ 1; OC for the queue's N' computed with ta_recheck_oc_v14.py logic and reported before any record of that frame is screened; L' = 2 percent of that queue's in-scope passes, reported, not used by the rule | A 5.4 |
| m4 dispatch isolation undermined | partly fixed (A 0); residual user-level CLAUDE.md | A 0 |
| m5 "never fires at zero flips" only by definition | fixed: wording now says K counts full-text inclusions, true or false; P(K ≥ 1) with no title/abstract loss and a hypothetical false-include rate r is 0.221, 0.394, 0.634 at r = 0.25, 0.5, 1 percent; errors of this kind cost work, not records | A 5.2 |
| m6 a sampled record named with its expected outcome | fixed: the example in R9 and R11 is withheld; all remaining example ids are outside the sample (checked). Four examples (M12789, M13881, M14279, M18900) are in the frozen frame but not the sample; they matter only if the reversal fires, and the orchestrator is not a screener | A 1 |
| m7 one robot demo turns human motion into an action | fixed: D4(1) decides by the main results; a demo outside them does not change the class; disclosed in A 6 item 5 | S D4 |
| m8 "method section states" vs "paper does not state" | fixed: R9(2) reads "the paper states, in any section or the appendix" | S R9 |
| m9 "anything executed on a robot" attributed to D0020 | fixed in amendment (4) and the D0032 row: D0020's own exclusions (robot actions, molecules), B-4(ii)'s (trajectories, other non-perceptual outputs) and the additions of these criteria are named separately | A 7 |
| m10 freeze protected only inside one script | fixed: full SHA-256 digests of the frozen frame and sample, the OC files, the C8 files and quote_check.py are in this file (A 5) and in the D0032 row | A 5, 7 |

### 2.4 Deferred, with reasons

- **Blind dual pilot (audit section 5).** Needs retrieved full texts and three screener sessions; it is
  the next step, not a rule change. It should cover the three classes the audit names plus a C8 record.
- **User-level CLAUDE.md in dispatch sessions (m4 residual).** Changing user configuration is outside
  this brief and needs the user; the isolation check detects any read it causes.
- **Same-family screeners.** A, B and C are all Claude models (the brief's options); protocol s4 step 2
  named Codex for screener B, which D0028 changed. Shared priors stay a stated limitation; the human
  validation is the cross-check.
- **Semantic limits of the quote check.** A contiguous quote can still omit a qualifier that follows it
  ("share weights only in stage 1"). The script cannot judge meaning; C and the human see the full text.
- **DLM-backbone VLAs and TTS on an existing text DLM.** v1.4 keeps v1.3's handling (R12, R10, R9);
  whether the authors want them included through R14 is a scope question for them (A 6 item 3).
- **M08480 (EndoCoT)** is still not added by hand; the frames are defined by declared queries only.

---

## 3. Rule-level differences from v1.3

- D1 adds equations without words (not text) and mathematical solutions in words (text).
- D4(1): robot-command outputs replace "any output the paper executes"; the humanoid case is decided by
  the main results.
- D5 (new) defines an existing text diffusion model.
- R7 states that R14 overrides it for non-language strings and quotes B-7 in full; R12 and R14 say
  where the override stops.
- R9 order is explicit, step 1 covers text-conditioned action heads, and step 2 reads the whole paper.
- R10 b3: (i) needs parameters trained for both; a Sides clause places adapters, queries and connectors.
- Section C no longer claims X1/X2 disjointness.
- Section D: every C session logged and reported; reruns only for failure or a failed isolation check.
- Briefs: model ids pinned (A claude-sonnet-5-5, B claude-opus-5-5, C claude-fable-5-1); quotes are
  contiguous with no ellipsis; CONTRACT.md's report format replaced by the JSON rows.

---

## 4. Agreement, validation and adjudication

1. Screeners A (claude-sonnet-5-5) and B (claude-opus-5-5) screen independently from dispatch folders.
   The model id is in every row (`FA-...`, `FB-...`).
2. `quote_check.py` (v1.4) runs on every batch. A quote with status `not_found`, `elided` or
   `negation_before` is returned to the screener once; if it is still not accepted, the record goes
   to C. Self-test on 2026-10-16, in the output folder, `python -I quote_check.py --self-test`:
   19/19 passed, exit 0. The v1.3 script returns True on both audit probes and on "share weights";
   v1.4 returns `elided`, `elided` and `negation_before`.
3. Reported before reconciliation:
   - three-category agreement and pass/exclude agreement, with kappa and bootstrap interval, p_pos,
     p_neg, and prevalence and bias indices;
   - the adjudicate rate per screener;
   - code-level agreement on joint exclusions;
   - agreement per rule.
4. **Adjudicator C** = claude-fable-5-1, fixed in v1.4 (fallback claude-haiku-5-5 only as stated in
   S section F). Why this model: it is the only listed model that is neither A's nor B's and is not
   the small tier, so C's "basis" does not measure a screener's agreement with itself, and the
   hardest records (those A and B split on) are not ruled by the smallest model. C rules on every
   disagreement and every adjudicate, blind; sample records are mixed unflagged into the queue.
   **Run log** (`analysis/screening/c-run-log.jsonl`, one line per session, written when the
   session ends): session id, model id as reported by the session, start and end time, queue file
   and its sha256, output file and its sha256 (or "none"), status (`complete`, `failed`,
   `discarded-isolation`, `rerun-of:<session id>`), reason. Every logged session and its rows are
   reported in the supplement. K uses the first complete session that passed the isolation check;
   K from every other complete session is reported beside it. C's agreement with the human author
   is reported.
5. **Human validation (protocol s4 step 3).** A human author screens a random 15% of the full-text
   set (at least 100 records), include or exclude, blind to A, B and C. Kappa of each screener
   against the human is computed on 2 × 2 tables in which the screener's "adjudicate" counts as
   include (the screener did not exclude; D0030's convention); the 3 × 2 tables are also reported.
   A screener below 0.70 triggers revision of the screener copy and a rerun.
6. The human author resolves the final set (protocol s4 step 4). Counts of C rulings overturned are
   reported.

---

## 5. Re-check of title/abstract exclusions (frozen design)

### 5.1 Frame and sample (unchanged)
- **Classes.** C1-C7 as in v1.2 section 5, declared in `ta_recheck_select.py`.
- **Frame.** 5,282 title/abstract exclusions (round 1 dual 210, round 2 dual 999, rescue single
  4,073) and **797 candidates** (D1 74, D2 278, R 445), frozen in `ta-recheck-frame-v1.3-frozen.jsonl`,
  sha256 `a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a`. 136 candidates match
  C4 (3D body) only.
- **Sample.** Simple random sample of **100**, seed 20261016, frozen in
  `ta-recheck-sample-v1.3-frozen.json`, sha256
  `958867658120c323446ee5692ec82702deb4464e0977a6030287ced035b7ac6c`. By frame: R 63, D2 28, D1 9;
  22 are C4-only. Not redrawn; digests checked on 2026-10-16 before and after the v1.4 scripts ran.
- **Dispatch.** Sample records are mixed unflagged into ordinary full-text batches for A and B.

### 5.2 Reversal test (v1.4)
- **Decision quantity.** K, the number of sampled records included at full text after A/B agreement
  or C's blind ruling, under the default O1. K counts full-text inclusions, whether or not the
  full-text inclusion is itself correct (m5).
- **Rule.** If **K ≥ 1**, all 797 candidates are screened at full text. Otherwise the review reports
  K = 0, F̂ = 0 and the exact one-sided 95% upper bound for F, which is 22.
- **Tolerable loss.** **L = 13 records**: D0027's reversal threshold, "more than about 2 percent of
  in-scope records", applied to D0029's "roughly 650 in scope that pass" (0.02 × 650 = 13). No
  included-set size is assumed. L is a reference for the operating characteristics, not part of
  the trigger.
- **Operating characteristics** (`ta_recheck_oc_v14.py`, the ta_recheck_oc.py hypergeometric logic,
  N = 797, n = 100; output `ta-recheck-oc-v1.4.txt`, sha256
  `3f9c610ed888a7cd7b204e2ba9ef55428add7a843ea095999b04ddded623aca7`; the v1.3 output
  `ta-recheck-oc-v1.3.txt`, sha256 `7f6499cec3171b9a144885d411e448ccd50c3f156c755eb5c7c5ccf1d00e5570`,
  agrees in every shared cell):

  | true flips F in frame | 0 | 2 | 4 | 8 | 12 | **13 = L** | 16 | 24 | 32 |
  |---|---|---|---|---|---|---|---|---|---|
  | P(trigger), **K ≥ 1** | 0.000 | 0.235 | 0.416 | 0.660 | 0.802 | **0.827** | 0.885 | 0.962 | 0.988 |
  | for comparison, K ≥ 2 | 0.000 | 0.016 | 0.079 | 0.265 | 0.456 | 0.500 | 0.617 | 0.826 | 0.927 |

  With no title/abstract loss (F = 0) and full-text false inclusions at a hypothetical per-record
  rate r, P(K ≥ 1) = 0.221 / 0.394 / 0.634 / 0.867 at r = 0.25 / 0.5 / 1 / 2 percent (K ≥ 2: 0.026 /
  0.090 / 0.264 / 0.597). These r values are assumptions, not estimates.
- **Why K ≥ 1.**
  - It is an acceptance-sampling plan with acceptance number 0: one eligible record among the 100
    sampled exclusions sends the whole frame to full text.
  - At L it fails to fire with probability 0.173; K ≥ 2 fails with probability 0.500. When the
    automation filter breached the same 2 percent threshold, D0029 rescued every exclusion, so a
    coin-flip acceptance of a breach of that size would be inconsistent with the project's own
    precedent.
  - Its errors fall on the side of extra work: at F = 4 it fires with probability 0.42, and false
    full-text inclusions can fire it. Either way the cost is 797 extra full-text screenings, never a
    lost record.
  - Even K = 0 cannot certify F ≤ 13: the exact one-sided 95% upper bound at K = 0 is 22. The review
    states this.
- **Timing.** L = 13 is read from D0027 and D0029. The rule K ≥ 1 was chosen on 2026-10-16 after the
  v1.3 operating characteristics for K = 1, 2, 3 had been computed and audited, and before any
  re-check record was screened at full text; no full-text outcome of any record is known.
- **O1 = no.** If the authors rule that pose and motion are not "3D", K is recounted from
  `code_if_o1_no` with the same frame and sample, and both results are reported. The reversal uses
  the default O1.
- **Limitations, stated in the review.** The classes are regex proxies, so exclusions outside them are
  not re-checked. At K = 0 the upper bound for F is 22. Sampled records included at full text enter
  the review flagged `source: ta-recheck-sample`, and the synthesis is repeated without them.

### 5.3 Supplementary class C8 (V1)
v1.4's R7/R14 precedence is more inclusive than the title/abstract rules (criteria-v1.md X1 names
"molecules, proteins or other non-text data only") for papers that adapt an existing text DLM to
non-language strings. The frozen classes do not cover this class fully (C2 drops titles with a
domain word; C3 needs X7 or a serving word). C8 is declared in `ta_recheck_c8_v14.py`: title/abstract
exclusions coded X1 or X2, not in the frozen frame, whose title or abstract has a diffusion word and
names a text-DLM term (`diffusion language model`, `diffusion llm`, `dllm`, `large language
diffusion`, `diffusion-based (large) language model`, `masked diffusion language`, `llada`, `mdlm`,
`sedd`, `plaid`, `diffusion large language`). Run of 2026-10-16: **32 candidates** (D1 8, D2 24, R 0),
at most 150, so **all 32 go to full text** (no sampling, no reversal rule); file
`ta-recheck-c8-candidates-v1.4.jsonl`, sha256
`6c4928af43387750941994f1bc36a7867ea14d8416a203cfd4377719e641e825`; log sha256
`729bee67db74fa952c5560588c9ff5af433f2aeed9dbfc682b4fefd7e7d651d8`. Many are protein or DNA
"diffusion language models", which R7 and D5 keep out; the class exists to find the few that
adapt a text DLM. C8 records are flagged `source: ta-recheck-c8` and reported in their own PRISMA box.
The frozen frame and sample are not touched.

### 5.4 Later queues (m3)
The subscription and title-resolved queues get their own frame after their title/abstract screening,
from the same class queries C1-C8: all candidates if at most 150; otherwise a simple random sample
of 100 with seed 20261016 (the same call as `ta_recheck_select.py`: `random.Random(seed).sample`
over the candidate ids in (frame, id) order) and the rule K ≥ 1. Before any record of that frame is screened, its
operating characteristics are computed with the `ta_recheck_oc_v14.py` logic on its N', and L' = 2
percent of that queue's in-scope passes is reported beside them (not used by the rule). Never a
redraw of the frozen frame.

---

## 6. Readings that could change eligibility (justified from protocol text, not records)

1. X0 code. Unchanged from v1.2.
2. D2, the diffusion component. Unchanged.
3. **Text by content, with B-7's exception (v1.4).** I1 says "natural-language text". Census
   codebook v1.2, B-7, in full: "**B-7 Scene text, OCR strings and captions [literal].** Words or
   sentences of a natural language count as natural-language text whatever their length or source
   (scene-text strings, OCR transcriptions, captions); code counts, as in the coder brief. Strings
   that are not language (SMILES, protein sequences, digit grids, abstract symbols) do not, except
   as tasks of a model that is eligible on other grounds. Reason: I1 sets no minimum length. (172)"
   v1.4 applies both halves: non-language strings are not text (R7), and an existing text diffusion
   model (D5), eligible on other grounds, stays eligible when the paper trains, re-samples or
   compares it only on such strings (R14 over R7). This is wider than v1.3 and wider than the
   title/abstract rules, hence class C8. The override stops at actions and D4-modality outputs,
   which D0020 and B-4 govern; whether DLM-backbone VLAs or text DLMs adapted to speech should also
   enter through R14 is left to the authors (it would widen I1(a) beyond B-7's "strings").
4. **I1(b) follows D0020 verbatim, decided from statements in the file (v1.4 Sides clause).**
   D0020: "one model (shared weights or one jointly trained system), not a pipeline of separately
   trained models"; B-4: "a shared backbone, or components trained or fine-tuned jointly and
   presented as one model". A trained parameter counts on the understanding side only if the
   understanding output is computed with it. So trained query tokens, connectors and decoders around
   a frozen MLLM are a pipeline with a trained interface (v1.1 M6's reading), and LoRA adapters
   active for understanding and trained jointly with the generator make one jointly trained system.
   Unified models whose files do not describe their weights are judged component by component.
5. **"3D" is the literal D0020 reading**, with an ordered exclusion list on top: D0020's own (robot
   actions, molecules), B-4(ii)'s (trajectories, other non-perceptual outputs) and the additions of
   these criteria (waypoints, joint or end-effector commands, robot or vehicle commands, proteins,
   cell profiles, graphs, tables, time series, 2D keypoints and trajectories). A human motion is an
   action only if the main results evaluate it by robot execution (m7). **Open item O1** goes to the
   user and professor. Default: literal. If they rule otherwise, a sensitivity analysis follows via
   `code_if_o1_no`.
6. I3 is read on the language of the body. Doubt goes to blind adjudication, then the human author.

---

## 7. For the orchestrator: proposed protocol s10 amendment and ledger row

```text
- <date> (D0032; full-text screening criteria v1.4: research/review/screening/criteria-v1.4-screener.md
  normative, criteria-v1.4.md audit copy; v1.1, v1.2 and v1.3 superseded after red-team audits of
  2026-10-16). Written after the title/abstract decisions had been recorded and seen, before any full
  text was screened and before the freeze rule was applied. I1-I4 are unchanged; the following codes
  and readings govern full-text screening, each justified from the protocol text, D0020 or census
  codebook v1.2.
  (1) Code X0: no diffusion component in the paper's own method. One code per excluded record, first
  applicable in the order X8, X3, X5, X4, X0, X1, X2, X7 (census B-8). X1 and X2 are decided in this
  order: X1 for a model with autoregressive text whose diffusion component generates actions,
  molecules or other outputs outside the I1(b) list (D0020), also when text conditions that
  component; otherwise X2 if the paper states that text conditions the non-text diffusion component
  by any path (directly, through a text encoder, or through an LLM, VLM or MLLM); otherwise X1.
  Reports not retrieved (X6) are reported before eligibility.
  (2) Diffusion component: trained to reverse a corruption applied over a range of corruption levels,
  or along a discrete or continuous flow-matching path, and generating in more than one step or by a
  sampler distilled from such a component.
  (3) I1(a): the diffusion component produces text, read by content: natural-language words or
  sentences, or source code; chemical and biological sequences, game and puzzle states, equations
  without words, identifiers, actions and other non-language content are not text whatever tokens
  carry them; naming never decides. Following census B-7 ("except as tasks of a model that is
  eligible on other grounds"), a paper that trains, fine-tunes, re-samples or compares an existing
  text diffusion model is eligible even when its outputs in the paper are only non-language strings;
  this does not extend to actions or to outputs in another modality.
  (4) I1(b): D0020 verbatim (understanding: text from an image, video, audio or speech, or 3D input;
  generation of that modality by a diffusion, masked-generative or flow component; one model with
  shared weights or one jointly trained system), decided from statements in the screened file only.
  A trained parameter counts on the understanding side only if the understanding output is computed
  with it; a frozen understanding model with trained query tokens, connector, generation-only
  adapters or decoder is a pipeline. "3D" is read literally (3D geometry, including 3D human pose and
  motion), with exclusions taking precedence: D0020's (robot actions, molecules), census B-4(ii)'s
  (trajectories and other non-perceptual outputs), and those added by these criteria (waypoints,
  joint or end-effector commands, outputs generated as robot or vehicle commands, proteins, cell
  profiles, graphs, tables, time series, 2D keypoints and trajectories); a human motion is an action
  only if the paper's main results evaluate it by robot execution. Whether pose and motion count is
  open item O1 for the authors, and each such record also carries the code it would get if not.
  (5) I3: the language of the main body decides.
  (6) Decisions are include, exclude or adjudicate. Screener A is claude-sonnet-5-5 and screener B
  claude-opus-5-5. Disagreements and adjudicate go to a blind adjudicating model, claude-fable-5-1
  (fixed before any full-text row; claude-haiku-5-5 only if Fable cannot be run, established before
  the first full-text row), and then to the human author; every adjudicator session, including
  failed, discarded and rerun sessions, is logged and reported. Evidence quotes are contiguous
  passages verified by script. A human screens a random 15 percent (at least 100) of the full-text
  set, and a screener below kappa 0.70 against the human triggers revision and rerun (s4 step 3).
  (7) Title/abstract decisions are not re-opened. A declared, scripted query selected 797 of 5,282
  title/abstract exclusions in classes where these readings are more inclusive; this is above the
  cap of 150 first stated in criteria v1.2 (ta_recheck_select.py CAP = 150), which was written
  together with the script that counted the candidates. A frozen random sample of 100 (seed
  20261016) is screened at full text, blind to its sample status, and reported in its own PRISMA
  box. If at least 1 sampled record is included, all 797 are screened. Tolerable loss 13 records (2
  percent of about 650 in-scope records, D0027 and D0029); trigger probability 0.42, 0.66, 0.83,
  0.89 at 4, 8, 13, 16 true flips; at zero sampled inclusions the exact one-sided 95 percent upper
  bound for the frame is 22 records. A supplementary class (existing text diffusion models applied to
  non-language strings, 32 records) is screened in full. Queues screened later at title/abstract get
  their own frame and the same design.
```

Ledger row. `tools/ledger.py add` numbers a row as (row count + 1) and lets the row's own `id` and
`ts` override that. The ledger has 32 rows and its last id is already D0033, so the row must carry
`"id": "D0032"` explicitly, or ledger.py would write a second D0033. `ts` is the adoption time, filled
when the row is appended (shown here as a placeholder to replace).

```json
{
  "id": "D0032",
  "ts": "<adoption time, ISO 8601, set when appended>",
  "decision": "Full-text screening uses criteria v1.4 (normative: research/review/screening/criteria-v1.4-screener.md, no record ids or outcomes; audit copy criteria-v1.4.md), replacing v1.1, v1.2 and v1.3 after red-team audits of 2026-10-16 (v1.1: 2 fatal, 15 major, 11 minor; v1.2 re-audit: adopt with fixes, 9 major, 3 minor; v1.3 audit: adopt with listed fixes, 6 major, 10 minor; every finding mapped in the audit copies). (1) X0 added; one code per record in census B-8 order; X1/X2 decided in R9's order: X1 for autoregressive text with a diffusion component generating actions, molecules or other outputs outside I1(b) (D0020), also when text conditions it; else X2 if the paper states text conditions the non-text diffusion component by any path; else X1; xsub field; X6 reported before eligibility. (2) Diffusion component: range of corruption levels or flow-matching path plus multi-step or distilled generation. (3) Text is natural language or source code by content; naming never decides; per census B-7 ('except as tasks of a model that is eligible on other grounds') an existing text diffusion model trained, fine-tuned, re-sampled or compared only on non-language strings is eligible (R14 over R7), not extended to actions or other-modality outputs. (4) I1(b) is D0020 verbatim, decided from the screened file only; a trained parameter is on the understanding side only if the understanding output is computed with it, so a frozen understanding model with trained query tokens, connector, generation-only adapters or decoder is a pipeline; '3D' literal with exclusions first: D0020's (robot actions, molecules), census B-4(ii)'s (trajectories, other non-perceptual outputs) and these criteria's additions (waypoints, joint or end-effector commands, robot or vehicle commands, proteins, cell profiles, graphs, tables, time series, 2D keypoints and trajectories); human motion is an action only if the main results evaluate it by robot execution; open item O1 (pose and motion) for the authors, default literal, with code_if_o1_no recorded for a sensitivity analysis. (5) I3 on the body language. (6) Include, exclude or adjudicate; screener A claude-sonnet-5-5, screener B claude-opus-5-5; disagreements and adjudicate go to blind adjudicator C claude-fable-5-1 (fallback claude-haiku-5-5 only if Fable cannot be run, established before the first full-text row), then the human author; every C session including failed, discarded and rerun ones is logged in analysis/screening/c-run-log.jsonl and reported; reruns only for technical failure or a failed isolation check; evidence quotes are contiguous (no ellipsis) and checked by analysis/screening/quote_check.py v1.4 (sha256 cb4567e4b6fe7bb16a2ea25129015b99388db4833d9cff1cfa7ff20515f4e9dc; self-test 19/19); human validation of a random 15 percent (at least 100), adjudicate counted as include for kappa, 0.70 rerun threshold; screeners work in isolated dispatch folders with a named isolation check. (7) Title/abstract decisions not re-opened; ta_recheck_select.py selects 797 of 5,282 exclusions, above the cap of 150 first stated in criteria v1.2 (ta_recheck_select.py CAP = 150, written together with the script that counted the candidates); frozen frame analysis/screening/ta-recheck-frame-v1.3-frozen.jsonl (sha256 a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a) and frozen random sample of 100 (seed 20261016; ta-recheck-sample-v1.3-frozen.json, sha256 958867658120c323446ee5692ec82702deb4464e0977a6030287ced035b7ac6c) screened blind to sample status; full re-check of the 797 if K >= 1 sampled includes; tolerable loss 13 records (2 percent of about 650 in-scope records, D0027 x D0029); trigger probability 0.416, 0.660, 0.827, 0.885 at 4, 8, 13, 16 true flips; exact one-sided 95 percent upper bound 22 at K = 0 (analysis/screening/ta-recheck-oc-v1.4.txt, sha256 3f9c610ed888a7cd7b204e2ba9ef55428add7a843ea095999b04ddded623aca7, from ta_recheck_oc_v14.py); supplementary class C8 (existing text-DLM terms, X1/X2, not in the frozen frame; ta_recheck_c8_v14.py; 32 records, all screened at full text; ta-recheck-c8-candidates-v1.4.jsonl sha256 6c4928af43387750941994f1bc36a7867ea14d8416a203cfd4377719e641e825); later queues get their own frame with the same classes, seed, cap, sample size and rule.",
  "options": ["criteria v1.3 as written", "criteria v1.4 with K >= 2 reversal (L = 13, power 0.50)", "criteria v1.4 with K >= 1 reversal (L = 13, power 0.83)", "criteria v1.4 with a full re-check of all 797 candidates", "R7 over R14 for non-language strings (v1.3 reading, against census B-7)"],
  "evidence": "research/review/audits/2026-10-16-redteam-criteria-v1.1.md; research/review/audits/2026-10-16-redteam-criteria-v1.2.md; research/review/audits/2026-10-16-redteam-criteria-v1.3.md; research/review/screening/criteria-v1.4.md; criteria-v1.4-screener.md; analysis/screening/ta_recheck_select.py, ta_recheck_freeze.py, ta_recheck_oc.py, ta_recheck_oc_v14.py, ta_recheck_c8_v14.py, quote_check.py; ta-recheck-v1.2.log; ta-recheck-oc-v1.3.txt; ta-recheck-oc-v1.4.txt; ta-recheck-c8-v1.4.log; protocol.md s2, s4, s10; census-codebook-v1.2.md B-4, B-7, B-8; D0020, D0027, D0029, D0030",
  "owner": "orchestrator (user delegated expert judgement)",
  "reversal": "any of: the authors rule on O1 (pose and motion), applied by code_if_o1_no as a sensitivity analysis or primary analysis as they decide; a referee or the professor rejects the D2 reading, the content test for text, B-7's exception for existing text diffusion models, or the decoded-output test for continuous and latent text diffusion; the professor wants frozen-backbone systems or unified models whose files do not describe their weights counted as unified (protocol amendment and rescreen of R10 exclusions); the authors want DLM-backbone action or speech models included through R14; NLP label or span diffusion is ruled text output; K >= 1 in the re-check sample (screen all 797); a blind pilot shows two screeners cannot apply a rule without discussion"
}
```
