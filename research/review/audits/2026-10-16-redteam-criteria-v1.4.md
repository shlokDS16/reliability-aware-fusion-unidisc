```yaml
agent: red-team
date: 2026-10-16
brief: Fourth, focused red-team pass on full-text screening criteria v1.4 (Paper 1). Covers the status of V1-V6 and m1-m10 from the v1.3 audit, new fatal or major problems introduced by v1.4, reproduction of the v1.4 re-check scripts, a fact check of the D0032 row, and a verdict.
sources_examined:
  - research/CONTRACT.md
  - research/review/audits/2026-10-16-redteam-criteria-v1.3.md (own previous audit, all)
  - research/review/screening/criteria-v1.4-screener.md (all 274 lines)
  - research/review/screening/criteria-v1.4.md (all 393 lines)
  - analysis/screening/quote_check.py (v1.4, all; v1.3 from git HEAD for comparison)
  - analysis/screening/ta_recheck_oc_v14.py, ta-recheck-oc-v1.4.txt
  - analysis/screening/ta_recheck_c8_v14.py, ta-recheck-c8-candidates-v1.4.jsonl, ta-recheck-c8-v1.4.log
  - analysis/screening/ta_recheck_select.py (frames(), classes(), CAP); frozen frame and sample files
  - research/ledgers/decisions.jsonl (D0020, D0027-D0030, row count and last id)
  - research/review/protocol.md s4 (l.80-100) and s10 D0020 entry (l.186-194)
  - research/review/coverage/census-codebook-v1.2.md B-4 to B-7 (l.50-84)
  - research/review/screening/criteria-v1.2.md (grep "150"); tools/ledger.py (cmd_add)
  - research/USER-ACTIONS-2026-10-16.md item 6a
  - ~/.claude/tools/graph_memory.py (repo(), project_name(), cmd_brief, cmd_sync, cmd_init) and ~/.claude/graph-memory.json
coverage: >
  I read every line of both v1.4 files and of the three changed or new scripts. Both v1.4 scripts were
  rerun with python -I in scratchpad/v14 and give byte-identical output (cmp). All eight repository
  digests were checked before and after the run (sha256sum -c: all OK). I ran the quote_check self-test
  (19/19) and 26 new adversarial probes (scratchpad/v14/probes.py), and ran the v1.3 quote_check from
  git HEAD on the audit probes. I recomputed the OC numbers independently. I counted C8-query matches
  inside the frozen frame and sample (scratchpad/v14/probe_c8.py). NOT covered: no full text (none
  exists) and no pilot. I could not verify that the model ids claude-sonnet-5-5, claude-fable-5-1 and
  claude-haiku-5-5 exist or can be run.
claims:
  - statement: "ta-recheck-oc-v1.4.txt, ta-recheck-c8-candidates-v1.4.jsonl and ta-recheck-c8-v1.4.log are reproduced byte-for-byte; the frozen frame (a9180fe4...d79a) and sample (95886765...7ac6c) are unchanged"
    status: supported
    evidence: "scratchpad/v14 rerun 2026-10-16; cmp identical; sha256sum -c before.sha all OK"
    level: E4
    confidence: 0.97
  - statement: "The K >= 1 operating characteristics (0.125/0.235/0.416/0.660/0.802/0.827/0.885/0.962/0.988), the upper bound of 22 at K = 0 and the binomial false-inclusion rows are correct"
    status: supported
    evidence: "independent recomputation in pure Python"
    level: E4
    confidence: 0.97
  - statement: "quote_check v1.4 rejects elided quotes and a quote that drops a negation word placed immediately before it"
    status: supported
    evidence: "self-test 19/19; v1.3 script (git HEAD) returns True on all three audit probes, v1.4 returns elided, elided, negation_before"
    level: E4
    confidence: 0.95
  - statement: "quote_check v1.4 enforces 'no preceding negation' (S l.231)"
    status: contradicted
    evidence: "probes: 'share weights' in 'do not fully share weights' -> found; in 'We do not, however, share weights' -> found; 'lacks shared weights', 'dont share weights', 'w/o shared weights' -> found"
    level: E4
    confidence: 0.95
  - statement: "The isolation check detects any read caused by the user-level CLAUDE.md routine (A l.130)"
    status: contradicted
    evidence: "graph_memory.py cmd_brief reads <vault>/Projects/<cwd folder name>/sessions/*.md and cmd_sync writes there; the Bash calls carry no path, so a path-based check (A l.44-48) cannot see them"
    level: E3
    confidence: 0.85
  - statement: "Every factual statement in the proposed D0032 row matches the files"
    status: mixed
    evidence: "section 4 below; all numbers, digests and attributions verified; 'about 650 in-scope records' drops D0029's 'that pass'; the model ids could not be verified"
    level: E4
    confidence: 0.9
competing_explanations:
  - "A low K can reflect the adjudicator model's own title/abstract leaning rather than the absence of loss. If the Haiku fallback fires, C ruled on 63 of the 100 sampled records at title/abstract."
  - "High A/B agreement can come from one screener reading the other's session note through the shared Obsidian vault (graph-memory), not from clear rules."
  - "Disagreement on C8 records can come from the D5 ambiguity (recipe or checkpoint), not from the screeners."
unknowns:
  - "Whether claude-sonnet-5-5, claude-fable-5-1 and claude-haiku-5-5 can be run as subagents, and whether Fable needs spend."
  - "How many passed or C8 records train an MDLM/SEDD/Plaid-type text DLM recipe from scratch on non-language strings (W1)."
  - "Whether dispatch subagents actually run the user-level graph-memory routine."
next_test: {hypothesis: "Two blind screeners apply D5/R7/R14 identically and screen independently", intervention: "blind dual pilot (screener copy only) on C8 records plus records that train an MDLM/SEDD recipe from scratch on SMILES, DNA or Sudoku; inspect transcripts for any graph-memory or vault call", primary_metric: "decision agreement on D5; count of sessions that call graph-memory", falsifier: "any D5 disagreement, or any graph-memory call in a screener session", gpu_hours: 0}
```

# Red-team audit of criteria v1.4 (fourth pass)

**Verdict: adopt with listed fixes.** Three new major findings block adoption. Each needs one or two
sentences, and none needs a new design. There is no fatal finding.

- v1.3 blocking findings V1-V6: **4 resolved (V2, V3, V5, V6), 2 partly (V1, V4), 0 not.**
- v1.3 minors m1-m10: **9 resolved, 1 partly (m4).**
- New findings: **fatal 0, major 3 (all blocking), minor 8.**
- Reproduction: byte-identical, and the frozen files are unchanged.

Line numbers: `S` = criteria-v1.4-screener.md, `A` = criteria-v1.4.md.

---

## 1. Status of the v1.3 findings

### 1.1 Blocking findings V1-V6

| Finding | Status | v1.4 line | Residual |
|---|---|---|---|
| V1 R7 vs R14; B-7 exception dropped | **partly** | S l.87-104 states the precedence (R14 overrides R7 for non-language strings). B-7 is quoted in full at S l.89-94 and A l.289-293 (checked verbatim against codebook l.80-84). New D5 at S l.55-61; R12 l.158; R14 l.173-174 | D5 creates a new conflict with R7's own example (W1) |
| V2 elided quotes pass | resolved | quote_check.py l.12-23 and l.77-102; brief S l.223-232; self-test 19/19 (rerun). The v1.3 script returns True on all three probes, v1.4 returns elided, elided, negation_before (verified against git HEAD) | The negation guard covers only the immediately preceding word (n1) |
| V3 L = 16 unsupported; "15.9 >= 16" | resolved | A l.214-219 (L = 13 = 0.02 x 650, sources quoted verbatim); rule K >= 1; OC at A l.226-229 (recomputed); timing disclosed at A l.246-248; false inequality removed | n7 (wording of the denominator) |
| V4 C's model not fixed; reruns | **partly** | S l.199-204 and l.256-260; A l.174-185 (model pinned, run log, rerun only for failure or isolation, K from the first valid run, the others reported) | The fallback model is the title/abstract excluder of 63 percent of the sample (W2) |
| V5 b3 frozen MLLM + LoRA/queries | resolved | S l.138-148 Sides clause: understanding side only if the b1 output is computed with the parameter; queries, connectors and decoders are generation side; a frozen understanding model is not common for (i). Checked against LoRA-active, query-token, MoT and separate-LoRA cases: no internal conflict found | none |
| V6 cap provenance | resolved | A l.366-368 and the D0032 row: "first stated in criteria v1.2 (ta_recheck_select.py CAP = 150), written together with the script that counted the candidates". Matches criteria-v1.2.md l.84 and l.154, ta_recheck_select.py l.31 and git history (both first enter at 5605e8e/f9041a9) | none |

### 1.2 Minors m1-m10

| Minor | Status | v1.4 line |
|---|---|---|
| m1 X1/X2 disjointness for R9(1) | resolved | S l.108-111 ("also when the text or instruction conditions that component"), S l.190-191, amendment (1) A l.329-333 |
| m2 kappa with 3 x 2 tables | resolved | A l.186-190 (adjudicate counts as include, the same as D0030's "include or unclear" rule, verified) |
| m3 later-queue seed and tolerance | resolved | A l.273-280 (seed, call, OC on N', L' reported). Residual in n3 (C8 in later queues) |
| m4 dispatch isolation | **partly** | A l.39-50 names a check and moves the cwd outside the repository. The residual is understated and the check is blind to it (W3) |
| m5 "never fires at zero flips" | resolved | A l.211-213, l.231-233 (binomial values verified) |
| m6 sampled record named | resolved | 30 ids in A, none in the sample (checked). M12789, M13881, M14279 and M18900 are in the frame, as stated |
| m7 robot demo turns motion into action | resolved | S l.43-47 (main results decide) |
| m8 "method section states" | resolved | S l.112 "in any section or the appendix" |
| m9 D0020 attribution | resolved | A l.350-355 and the row: D0020 (robot actions, molecules; protocol l.191-192), B-4(ii) (trajectories, non-perceptual; codebook l.58-59), and additions attributed to these criteria. All verified |
| m10 freeze digests | resolved | A l.202-207, l.221-223, l.266-268 and the row: full sha256 for frame, sample, OC v1.4, C8 file and quote_check.py. All verified |

---

## 2. New findings introduced by v1.4

### Major (all blocking)

**W1. D5 does not say whether an "existing text diffusion model" means pretrained weights the paper loads or a published model recipe the paper trains itself. R14(a) and R7's own example then give opposite answers (S l.55-61, l.101-103, l.168).**
D5 says the model is one "that the paper did not create and that the file ... describes as a
diffusion (large) language model ... without naming a non-language domain". R14(a) includes a paper
that "trains or fine-tunes it as a generator". R7 says it "decides alone when the diffusion
component is not an existing text diffusion model (for example one the paper trains from scratch on
non-language content)".

Take a typical file: "We adopt MDLM (Sahoo et al.), a masked diffusion language model, and train it
on ZINC SMILES" or on Sudoku or DNA.
- **Inclusion reading.** The paper did not create MDLM, and the file describes MDLM as a diffusion
  language model without a domain qualifier. So D5 holds, the paper "trains" it, and R14(a) includes it.
- **Exclusion reading.** The paper trains the model from scratch on non-language content. So R7
  decides alone, and the code is X1.

Neither reading is ruled out by the text. The author's own example inherits the gap: "M14279 (SMILES):
X1 if its diffusion model is trained by the paper" (A l.72). This is the class C8 was built for: the
C8 regex names `mdlm`, `sedd` and `plaid`, all published recipes that are routinely retrained from
scratch on molecules, DNA and puzzles. A further wrinkle is that "PLAID" is also a protein model.
v1.3's V1 was a conflict between two rules. v1.4 moves the conflict into the definition that decides
the override.
*Rejection condition:* two blind screeners disagree on D5 for a record that trains an MDLM/SEDD/Plaid-type recipe from scratch on non-language strings.
*Required property:* D5 must say whether "existing" means weights pretrained elsewhere and loaded by the paper, or also a published architecture or objective that the paper trains from scratch.

**W2. The pre-declared fallback adjudicator, claude-haiku-5-5, made the title/abstract exclusions behind 445 of the 797 frame records and 63 of the 100 sampled records (S l.258-260; A l.174-178).**
The R frame consists of exclusions from the D0029 rescue pass, which a Claude Haiku screener ran
alone (decisions.jsonl D0029; 4,421 rows tagged `R-claude-haiku`). The frozen sample holds 63 R-frame
records. If the fallback fires, the model that produces C's share of K rules on its own earlier
exclusions. That is the inherited-leaning problem of V4 again, in a new form, and it biases K toward
0.

The audit copy's own reason for choosing Fable ("not the small tier, so ... the hardest records ...
are not ruled by the smallest model", A l.175-177) argues against this fallback. The fallback is
likely to fire. USER-ACTIONS item 6a says Fable "may draw usage credits", and that refusing spend
makes C fall back to Haiku. The trigger also differs between files: S l.258 says "cannot be run",
while USER-ACTIONS ties it to spend approval. Neither file names where the fallback decision is
logged before the first A/B row, since c-run-log.jsonl is created only "at the first C session"
(A l.37).
*Rejection condition:* C = claude-haiku-5-5 rules on any sampled R-frame record.
*Required property:* the fallback adjudicator must not be a model that made the title/abstract decision on sampled records (and the fallback trigger and its log location must be stated identically in S and USER-ACTIONS).

**W3. The named isolation check cannot see the one leak path the audit copy leaves open, and the copy says it can (A l.44-50, l.129-130).**
A l.130 says "the isolation check detects any read it causes". The check lists "every path in the
session transcript's tool calls". The user-level CLAUDE.md, which loads in every dispatch session,
tells the session to run `graph-memory brief` at the start and `graph-memory sync --note
"<what changed>"` at the end. I checked `~/.claude/tools/graph_memory.py`:
- A dispatch folder in the scratchpad is not a git repository (verified). There, `repo()` names the
  project after the folder's basename.
- `cmd_brief` prints the last two session notes from `<vault>/Projects/<basename>/sessions/`, which
  is outside the folder. So does `init`, which runs `sync` after "no graph here".
- `cmd_sync --note` writes the session's own summary into that vault directory.

All of these are Bash calls with no path argument, so the named check passes them. Two leaks follow:
- If Screener A's and Screener B's folders share a basename (for example `batch-01` under different
  parents), B's session-start brief prints A's "What happened" note. That breaks the independence
  protocol s4 step 2 requires ("Neither sees the other's decision").
- Screening summaries are written into the user's vault outside the dispatch folder.

The screener brief waives "CONTRACT.md's ... graph-memory step" (S l.210-211) but not the
user-level CLAUDE.md's session routines. That file says its instructions "OVERRIDE any default
behavior". Folder naming is not specified (A l.39-41).
*Rejection condition:* any screener or C transcript contains a graph-memory call, or two dispatch folders share a basename.
*Required property:* the isolation check must flag any graph-memory or vault access, and the brief must explicitly waive the user-level session routines; A l.130 must not claim detection it lacks.

### Minor

- **n1. The negation guard checks one word and a fixed lexicon, but S l.231 and the D0032 row promise "no preceding negation".** These probes all returned `found`: "share weights" from "do not fully share weights"; "share weights between the two branches" from "We do not, however, share weights between..."; "both modules share weights" from "It is not the case that both modules share weights"; "shared weights" after "lacks", "w/o" or "rather than"; and "share weights" from "dont share weights". A negation after the quote also passes: "share weights in neither stage". So do qualifiers dropped at the end: "trained jointly only in stage 1"; "run through one transformer, which is kept frozen". A l.134-135 discloses only the last kind. There is also no minimum quote length, so a one- or two-word quote ("jointly trained") supports any condition.
- **n2. The quote check falsely rejects ordinary copies of markdown.** These returned `not_found`: a quote that drops a link URL ("LLaDA fine-tuned on SMILES" against `[LLaDA](https://...) fine-tuned`), text around `<sup>` footnote tags, a quote that leaves out a citation, a case change at a sentence start, and a passage split by a page header. Each failure returns the record to the screener and then sends it to C, which adds C load unrelated to the eligibility doubt. A soft hyphen, NBSP, U+2011, curly apostrophes, whitespace runs and line-end hyphenation all match correctly (probed).
- **n3. C8 is "screened in full" only outside the frozen frame.** 16 frozen-frame records meet the C8 query (X1/X2, a diffusion word and a text-DLM term), and only 2 are in the sample (R1364, M13388). The other 14 reach full text only if K >= 1. They include M14279 (SMILES) and M09229 (BlockVLA). Amendment (7) (A l.373-374) describes the class as "existing text diffusion models applied to non-language strings, 32 records ... screened in full". The query is a regex on DLM terms, and most hits are protein or DNA models, as A l.268-269 admits. Later queues (A l.275-277) put C8 into the sampled union, which contradicts "C8 all to full text".
- **n4. The override creates an asymmetry that the amendment does not disclose.** A paper that pretrains its own text DLM and reports only non-language results falls outside D5 (S l.60-61). It then fails R6, while a paper that fine-tunes someone else's DLM on the same strings is included. Masked-DLM reasoning papers trained from scratch on Countdown, Sudoku or chess are now X1 by rule. That consequence for RQ4 (unmasking order) is not stated in A 6 item 3 or in the amendment.
- **n5. Two new boundaries.** First, the override covers "numbers" and time series (not a D4 modality) but not "trajectories" (R12). A text DLM fine-tuned to forecast positions as numbers falls on both sides. Second, D1 makes LaTeX "markup" text but "equations without words" not text (S l.13-17).
- **n6. Model ids in the C run log are "as reported by the session" (A l.180).** Self-reported ids are unreliable. A and B have no pinned fallback if claude-sonnet-5-5 cannot be run.
- **n7. "2 percent of about 650 in-scope records" (amendment (7), row).** D0029's figure is "roughly 650 in scope that pass" the automation filter, which is the round-2 database queue. It is not the in-scope set of the frame's three sources (round 1, round 2, rescue). L is not part of the trigger, so only the wording is wrong.
- **n8. Records included by R14 over R7 are recorded i1 "a" (S l.174) although no diffusion output is text.** The review's I1(a) counts will therefore mix text-output studies with non-language-only studies unless they are reported separately.

---

## 3. Reproduction

| Output | Repository sha256 | Scratch rerun (scratchpad/v14) | Result |
|---|---|---|---|
| ta-recheck-oc-v1.4.txt | 3f9c610ed888a7cd7b204e2ba9ef55428add7a843ea095999b04ddded623aca7 | ta_recheck_oc_v14.py --frame (frozen frame) | byte-identical |
| ta-recheck-c8-candidates-v1.4.jsonl | 6c4928af43387750941994f1bc36a7867ea14d8416a203cfd4377719e641e825 | ta_recheck_c8_v14.py --repo (read-only) | byte-identical |
| ta-recheck-c8-v1.4.log | 729bee67db74fa952c5560588c9ff5af433f2aeed9dbfc682b4fefd7e7d651d8 | same | byte-identical |
| ta-recheck-frame-v1.3-frozen.jsonl | a9180fe4...d79a | sha256sum -c before and after | unchanged |
| ta-recheck-sample-v1.3-frozen.json | 958867658120c323446ee5692ec82702deb4464e0977a6030287ced035b7ac6c | same | unchanged |
| quote_check.py | cb4567e4b6fe7bb16a2ea25129015b99388db4833d9cff1cfa7ff20515f4e9dc | self-test 19/19, exit 0 | as stated |

C8: there are 32 candidates (D1 8, D2 24, R 0). Frame codes show why R is 0: the R frame is 76 percent
X0, and only 2 R records carry a text-DLM term at all.

## 4. D0032 row: fact check

| Statement in row or amendment | Verified against | Result |
|---|---|---|
| v1.1 2/15/11; v1.2 9 major 3 minor; v1.3 6 major 10 minor | audits | correct |
| 797 of 5,282; frame and sample sha; seed 20261016 | rerun, sha256sum | correct |
| cap 150 "first stated in criteria v1.2 ... written together with the script" | criteria-v1.2.md l.84, l.154; select.py l.31; git | correct |
| K >= 1; trigger 0.416/0.660/0.827/0.885 at 4/8/13/16; UB 22; OC sha | recomputation, sha | correct |
| L = 13 from D0027 "more than about 2 percent of in-scope records" x D0029 "roughly 650 in scope that pass" | decisions.jsonl D0027 reversal field, D0029 decision | arithmetic and quotes correct; "about 650 in-scope records" drops "that pass" (n7) |
| C8 32 records, sha | rerun | correct; "screened in full" overstates the class (n3) |
| quote_check sha and 19/19 | sha, self-test | correct; "contiguous ... verified by script" fine, "no preceding negation" in S overstated (n1) |
| B-7 quote "except as tasks of a model that is eligible on other grounds" | codebook l.80-84 | verbatim |
| D0020 (robot actions, molecules); B-4(ii) (trajectories, non-perceptual) | protocol l.191-192; codebook l.58-59 | correct |
| D4 additions attributed to "these criteria" | S l.39-47 | correct |
| A claude-sonnet-5-5, B claude-opus-5-5, C claude-fable-5-1, fallback claude-haiku-5-5 | USER-ACTIONS 6a (consistent); D0028 names only "Claude Sonnet"/"Claude Opus" | consistent in the files; existence of the ids **not verifiable**; fallback trigger differs from USER-ACTIONS (W2) |
| "screeners work in isolated dispatch folders with a named isolation check" | A l.39-50; graph_memory.py | the check is blind to graph-memory vault I/O (W3) |
| ledger has 32 rows, last id D0033; ledger.py lets the row's id override | decisions.jsonl; tools/ledger.py l.65-66 | correct |
| protocol s4 step 2 named Codex for B | protocol l.89 | correct |
| D0030 "include or unclear" convention | D0030 | correct |

## 5. What would force rejection of "v1.4 is ready"

Run a blind dual pilot from the screener copy on C8 records and on records that train an
MDLM/SEDD/Plaid recipe from scratch on SMILES, DNA or Sudoku, and inspect every transcript for
graph-memory calls. Any one of these rejects the claim:
- a D5 disagreement;
- a graph-memory call in a screener or C session;
- a C run on claude-haiku-5-5 that covers sampled R-frame records.

## 6. Fixes

Blocking:
1. W1: D5 must say whether "existing" means pretrained weights loaded by the paper, or also a published recipe the paper trains from scratch, and A l.72 must match.
2. W2: the fallback adjudicator must not be the model that excluded sampled records at title/abstract (Haiku, 63 of 100); state the fallback trigger and where it is logged, identically in S and USER-ACTIONS.
3. W3: the brief must waive the user-level session routines and the isolation check must flag any graph-memory or vault call; remove the claim at A l.130 and require distinct dispatch-folder basenames.

Non-blocking:
1. n1: the S l.231 and row wording must match the one-word guard; disclose leading-adverb and trailing-negation truncation; set a minimum quote length.
2. n2: state how URLs, citations, `<sup>` tags and page headers inside a quoted passage are handled.
3. n3: describe C8 as a DLM-term query; disclose the 14 C8-type frame records outside the sample; keep later-queue C8 consistent with "all to full text".
4. n4: disclose in amendment (3) that from-scratch puzzle and reasoning DLM papers are X1, and the own-pretraining asymmetry.
5. n5: settle trajectories-as-numbers under the override, and LaTeX equations under D1.
6. n6: take model ids from the harness, not the session; state A/B fallbacks.
7. n7: write "2 percent of about 650 in-scope records passing the automation filter (D0029)".
8. n8: report R14-over-R7 inclusions separately from text-output I1(a) inclusions.
