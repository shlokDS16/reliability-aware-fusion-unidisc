```yaml
agent: red-team
date: 2026-10-16
brief: Fifth, focused red-team check of full-text screening criteria v1.5 (commit 83eb816). Covers the status of W1-W3 and n1-n8, new fatal or major problems introduced by v1.5, probes of the new quote_check guards, the D0032 row facts, and a verdict.
sources_examined:
  - research/CONTRACT.md
  - research/review/screening/criteria-v1.5-screener.md (all; diffed against v1.4)
  - research/review/screening/criteria-v1.5.md (all 379 lines)
  - analysis/screening/quote_check.py at 83eb816 (all)
  - research/USER-ACTIONS-2026-10-16.md item 6a
  - analysis/screening frozen frame, sample, OC v1.4 and C8 files (digests only)
  - ~/.claude/settings.json (hooks), ~/.claude/tools/graph_memory.py (from the v1.4 check)
coverage: >
  I read every line of both v1.5 files and of quote_check.py, and diffed the screener copy against v1.4.
  Digests of the frozen frame, sample, OC v1.4 output and C8 files are unchanged. quote_check.py sha256 is
  fb6591bc...27ba, and its self-test passes 32/32 (python -I, scratchpad/v15). I ran 21 new adversarial
  probes (scratchpad/v15/probes.py). The route paragraph was compared by string across S section D,
  A section 4 and the D0032 row: identical. The screener copy contains no record id (grep 0).
  NOT covered: no full text, no pilot. The model-id list rests on the orchestrator's statement; no file
  in the repository holds it.
claims:
  - statement: "W1 is resolved: D5 now means text-pretrained weights (loaded or pretrained in the paper), not a recipe"
    status: supported
    evidence: "S l.58-69; R7 l.110-113; R14(a) l.177; A l.80 (MDLM-on-ZINC example: not D5, X1)"
    level: E2
    confidence: 0.85
  - statement: "The route paragraph is identical in S section D, A section 4 and the D0032 row"
    status: supported
    evidence: "whitespace-normalised string comparison, 1,116 characters each, equal"
    level: E4
    confidence: 0.97
  - statement: "quote_check v1.5 rejects a negation within 6 words before the quote in the same sentence"
    status: mixed
    evidence: "probes: caught for 'do not - in any stage -'; missed when 'e.g.', 'et al.' or ':' falls between the negation and the quote (eg_split, etal_split, colon -> found)"
    level: E4
    confidence: 0.9
  - statement: "The n5 fix (numbers used as poses or positions are a trajectory) is consistent with D4(2)"
    status: contradicted
    evidence: "S l.107-109 vs S l.51-53 ('3D coordinates ... including 3D human pose and motion') and R12 l.163-164 ('never a D4 modality')"
    level: E2
    confidence: 0.8
competing_explanations:
  - "Under Route H, a low K can reflect the human author's general leaning or workload interest rather than the absence of loss, because his blindness to sample status cannot be checked."
unknowns:
  - "Whether Route F or Route H will be chosen (user spend decision)."
  - "Whether any frame record has a text DLM emit 3D pose, motion or object positions as numbers (Y1)."
next_test: {hypothesis: "Blind screeners apply D4(2), R7 and R12 identically to number-encoded 3D pose", intervention: "blind dual pilot including a C4 record whose generator emits 3D joint coordinates as numbers", primary_metric: "decision agreement on D4(2) vs trajectory", falsifier: "any disagreement traced to the R7 trajectory sentence", gpu_hours: 0}
```

# Red-team check of criteria v1.5 (fifth pass)

**Verdict: adopt with listed fixes.**
- **Y1 blocks adoption.** It needs one phrase.
- **Y2 blocks only if Route H is chosen.** In that case it must be settled before the route line is
  written in c-run-log.jsonl.
- No fatal finding.

Finding status:
- **W1-W3:** 3 resolved, with residuals listed below.
- **n1-n8:** 7 resolved, 1 partly (n5, which creates Y1).
- **New findings:** fatal 0, major 2, minor 5.

Line numbers: `S` = criteria-v1.5-screener.md, `A` = criteria-v1.5.md.

## 1. Status of the v1.4 findings

| Finding | Status | v1.5 line | Residual |
|---|---|---|---|
| W1 D5: weights or recipe | resolved | S l.58-69 (D5 "weights, not recipe", (i) loads text-generating weights, (ii) own text pretraining, recipe from random init on non-language content is not D5); R7 l.110-113; R14(a) "trains further" l.177; A l.80 MDLM-on-ZINC example | y5 (what "pretrains on text" means in D5(ii)) |
| W2 Haiku fallback | resolved | S l.214-231: Route F (Fable only with spend approval and a harness test session) or Route H (human); "No other model is ever C"; route written as line 1 of c-run-log.jsonl before the first A/B row. The paragraph is identical in A l.168-179 and the row (string comparison). USER-ACTIONS 6a matches | Route H is underspecified (Y2) |
| W3 isolation blind to graph-memory | resolved | S l.6-8 and l.237-243 (SESSION RULES override user and project routines); A l.36-60 (check by name, pathless Bash, Skill/Agent/web/MCP, vault folder `Projects/<basename>`, `<role>-<batch>-<uuid4>`); the false v1.4 claim is corrected at A l.56-60 | Rule (1) dropped Bash/PowerShell paths (y3) |
| n1 negation guard | resolved | quote_check.py: 6-word before and 3-word after windows within the same sentence; wider word list; 6-word minimum; brief S l.267-269 matches | The sentence splitter breaks at abbreviations (y4) |
| n2 markdown false rejections | resolved as disclosed | link targets and `<sup>` markers stripped (probes found); citations and page headers verbatim by rule (S l.258-262); typed superscripts disclosed | none new |
| n3 C8 wording | resolved | A l.239-261, amendment (7) l.359-362: regex proxy; 16 records in the frame, 2 sampled, 14 reach full text only if K >= 1 (matches my count); later-queue C8 screened in full | none |
| n4 asymmetry and puzzle DLMs | resolved | D5(ii) S l.63-64; disclosure A l.280-284 and amendment (3) | y5 |
| n5 trajectories and LaTeX | **partly** | D1 LaTeX S l.16-17 (resolved). The trajectory sentence S l.107-109 conflicts with D4(2) | Y1 |
| n6 self-reported model ids; A/B fallback | resolved | A l.153-157, l.187-190; S l.229-231 | The model list comes from the orchestrator's statement; no repository file holds it |
| n7 "650 in-scope" | resolved | A l.221-225; row | none |
| n8 `nonlang_only` | resolved | S l.183-184, l.279-280, l.289; A l.164-165 | none |

## 2. New findings introduced by v1.5

### Major

**Y1. The n5 fix turns 3D human pose and object positions written as numbers into "trajectories". By R12, a trajectory is "never a D4 modality". D4(2) makes the same content 3D (S l.107-109 vs l.51-53, l.163-164). This blocks adoption.**

R7 now reads: "numbers that the paper uses as positions, poses, waypoints or the path of an agent,
robot, vehicle or object are a trajectory". R12 says trajectories "are never text and never a D4
modality". D4(2) says "3D" is any output represented as three-dimensional geometry: "3D coordinates
... including 3D human pose and motion". D4's humanoid rule decides action against motion by the
main results, not by how the output is encoded.

Consider a text DLM (or unified DLM) that emits SMPL joint coordinates or 3D object positions as
digits. There are two readings:
- **Global reading** of the R7 sentence: the output is a trajectory, so R12 applies. It is never
  I1(b), and D4(1) "overrides (2)".
- **Override-only reading**, scoped to R7's parenthetical: D4(2) applies, the output is 3D, R10
  decides, and `body3d` is set.

Two consequences follow:
- Encoding (digits against VQ tokens) now decides eligibility. That contradicts D1's "content of the
  output, not the tokens".
- The class overlaps C4: 136 frame records and 22 sampled records, so it bears directly on K and O1.

The A l.85 example ("object positions as numbers: trajectory") and the row ("not extended to actions,
trajectories") support the global reading.
*Rejection condition:* two blind screeners disagree on a record whose generator emits 3D human pose, motion or 3D object positions as numbers.
*Required property:* the trajectory sentence must leave 3D human pose and motion (and 3D object geometry) to D4(2) and the humanoid rule, or say explicitly that it overrides them.

**Y2. Route H is underspecified in ways that bear on K and on the blind validation (A l.181-186, l.193-197; S l.221-226). This blocks only if Route H is chosen.**
- **Blindness to sample status rests on an honour rule.** The human author is "not told why a record
  is in the queue" and "does not open" section 5, the frame, sample or C8 files. Nothing logs or
  checks this, unlike C's isolation check and run log. The frozen sample file and the v1.2 log, which
  lists sample ids, sit in the repository he owns. He is also the person whose workload rises if
  K >= 1: approving downloads for 797 more full texts, and about 120 more validation records at
  15 percent. Under Route H he sets the adjudicated part of K.
- **The order of validation and adjudication is stated once, for one queue.** A l.197 says "the
  validation sample is drawn and screened before the author sees the adjudication queue". But the
  full-text set grows by queue: the main set plus C8 plus the 100 sampled records, then the
  subscription and title-resolved queues, then 797 more if K >= 1. K itself needs the human's
  adjudications. Neither file says whether the 15 percent is drawn per tranche, or how blindness is
  kept for tranches drawn after he has adjudicated earlier ones.

*Rejection condition:* under Route H, any validation record is screened by the human after he has seen its A/B rows, or he cannot attest he did not open the sample files before finishing the queue.
*Required property:* under Route H, the validation draw and its timing must be fixed per tranche, and the human's blindness must be recorded (attestation or access log) in c-run-log.jsonl.

### Minor

- **y3. Isolation-check rule (1) no longer covers paths inside Bash or PowerShell commands (A l.47-51).** v1.4 listed "Read, Grep, Glob, Bash, Edit, Write". v1.5 rule (1) lists Read, Grep, Glob, Edit and Write. Rule (2) flags only Bash calls that name *no* inside path. A command such as `cat ./paper.md ../FB-b03-<uuid>/out.jsonl` names an inside path, so neither rule flags it, and A's and B's folders are siblings in the scratchpad. "Explicit path" is also undefined: if a bare relative filename (`cat paper.md`) counts as pathless, ordinary sessions are discarded.
- **y4. The negation guard's sentence splitter breaks at abbreviations and colons (quote_check.py `_SENT_END`).** These probes returned `found`:
  - `share weights between the understanding and generation modules` from "We do not, e.g. as Show-o does, share weights ...";
  - the same quote from "The model does not, following Chen et al. 2024, share weights ...";
  - a negation separated from the quote by a colon;
  - a negation more than 6 words back, behind a parenthetical (the window size is disclosed in kind).

  The tag regex also deletes spans such as `<q and not r>` in inline maths, on both sides, so a negation inside such a span is invisible. In the other direction, an affirmative "X ..., not a pipeline of ..." is rejected (`negation_after`), and "Instead of two models, we use one transformer ..." is rejected (`negation_before`). These cost work, not errors.
- **y5. D5(ii) says "pretrains the model on natural-language text or code" (S l.63-64) without saying that text is what the model generates.** A text-conditioned molecule or protein diffusion model trained on text-molecule pairs can be read as D5(ii), which opens the R14 override where R9 would give X2. It also collides with D5's last sentence for domain "language models" that are pretrained with natural-language annotations. The heading ("weights ... trained to generate text") points the right way. Clause (ii) does not.
- **y6. The vault-folder test and the D0032 evidence depend on `~/.claude/tools/graph_memory.py`**, a user-home file that is not versioned or digested. The test relies on its `project_name` behaviour (a basename outside the GENERIC list). If that file changes, the test can weaken without anyone noticing.
- **y7. The 6-word minimum excludes short evidence that cannot be lengthened contiguously.** Examples are a table header or a caption fragment such as "Steps", or an R14(c) column label. The record then goes to adjudication for formatting, not for doubt.

## 3. D0032 row: fact check

| Statement | Result |
|---|---|
| audit counts incl. "v1.4 audit: adopt with listed fixes, 3 major, 8 minor" | correct |
| frame a9180fe4..., sample 95886765..., OC v1.4 3f9c610e..., C8 6c4928af...; seed 20261016 | unchanged (sha256 checked) |
| quote_check.py v1.5 sha256 fb6591bc95acad4ea7d3b98f9879daff6ae7f974101c8fdd55381549dbca27ba; self-test 32/32 | correct |
| K >= 1; 0.416/0.660/0.827/0.885; UB 22; L = 13 "that pass the automation filter" | correct (verified in the v1.4 check; wording now matches D0029) |
| C8: 32 outside the frame screened in full; 14 frame records outside the sample screened only if the reversal fires | correct (16 in frame, 2 sampled) |
| route paragraph | identical to S and A (string comparison) |
| model ids "Claude Code harness model list, 2026-10-16" | the only source is the orchestrator's statement; no repository artifact |
| "not extended to actions, trajectories or other-modality outputs" | correct as text, but inherits Y1's ambiguity on poses and positions |
| evidence includes ~/.claude/tools/graph_memory.py | outside the repository, not digested (y6) |
| last id D0033, explicit "id": "D0032" needed | correct |

## 4. Fixes

Blocking:
1. Y1: the R7 trajectory sentence must not reclassify 3D human pose, motion or 3D object geometry that D4(2) and the humanoid rule govern, or it must state that it overrides them. A l.85 must match.

Blocking only if Route H is chosen (before the route line is written):
2. Y2: fix the per-tranche order of the 15 percent validation draw against adjudication, and record the human adjudicator's blindness to sample status in c-run-log.jsonl.

Non-blocking:
3. y3: isolation rule (1) must also cover paths inside Bash and PowerShell commands, including `..`, and "explicit path" must be defined.
4. y4: the negation-window sentence splitter must not break at "e.g.", "i.e.", "et al.", "Fig." or a colon; disclose the inline-maths tag deletion.
5. y5: D5(ii) must say the model is pretrained to generate natural-language text or code, not merely trained with text as a condition.
6. y6: digest or copy graph_memory.py, or cite it with its sha256, in the D0032 evidence.
7. y7: state how evidence shorter than 6 contiguous words (table headers, labels) is handled.
