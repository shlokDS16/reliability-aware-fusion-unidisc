# Open questions for the human author: extraction and appraisal form v0.2 (2026-10-20)

Each item names the gap or conflict, the options, a recommendation and where the plan implements it.
**Decision row** = needs a row in `research/ledgers/decisions.jsonl` (entered by the orchestrator) before the
step named. Nothing here was decided by the drafting agent; the form implements each recommendation
provisionally. v0.1 items that v0.2 settles are listed at the end with where they went.

## A. Scope (user decision of 2026-10-16)

**OQ2-01 Which package of the scope decision (decision row, before the pilot).**
The user's line fixes contrast data on "a stratified sample + all multimodal"; it does not say whether the
census extension (D0011) and the appraisal (protocol s6) get a second extractor on every include.
Options (tokens, inference from the red-team's per-record estimates, plan s2.8): MIN 44.2M-67.1M (second
reading on a stratified 10 percent only; deviations on D0011 and protocol s6); REC 59.9M-89.5M (MIN plus block F
double-extracted on every include, meets D0011); FULL 69.3M-107.9M (block F and QA double on every include,
meets D0011 and protocol s6). T1 screening cost about 44M-58M.
Recommendation: REC. Draft row: plan s2.9.

**OQ2-02 What "all multimodal" means.**
Options: (a) C1 only: i1 in {b, ab}, 53 in T1 (the I1(b) unified models; the RQ5 population); (b) C1 plus C2:
i1 = a includes with a multimodal corpus title (52; diffusion VLMs and MLLMs, speech, captioning), plus the
completion rule for any further i1 = a include whose light-pass modality is not text (count unknown until the
light pass); (c) (b) without the completion rule.
Recommendation: (b). It matches the user's words; C2 costs about 1.7M-2.8M tokens. RQ5 tables still use C1 only.

**OQ2-03 Size of the random sample.**
Options: 90, 120, 150 from the 491-record frame. 95 percent half-widths for a study-level share: 0.093, 0.078,
0.067; within a subgroup at 50 percent prevalence: 0.132, 0.110, 0.094. Each step of 30 costs about 1.0M-1.6M
EA tokens.
Recommendation: 120 (plan s2.5); 90 is step 2 of the cost fallback ladder.

**OQ2-04 Headline-number units on every include or on the sample only.**
H units are now only abstract outcome numbers and the F1 number (about 3k-5k tokens per record). Protocol s5
asks for headline numbers per study, the census needs the F1 unit on every include, and QA8's match status
rests on their traces.
Recommendation: every include (plan s2.2).

**OQ2-05 Inventory flags I1-I5 and the targeted-extension rule.**
Five yes/no flags in the light pass (diffusion-vs-AR table, training ablation, inference sweep, task or
modality removal, credited ablation) let the review count contrast types over every include and let a cell
near the pooling threshold be extended to a census of that cell (plan s2.7). They are close to "RQ data"
but carry no values.
Recommendation: keep both (decision row with OQ2-01).

**OQ2-06 nonlang_only includes (12).**
Recommendation: L, Q and H only, no block K, a separate row in every table (D0032 item 3). Was v0.1 OQ-21,
where full extraction was recommended; the change follows the user's scope.

## B. Appraisal

**OQ2-07 Adjudicator route.** claude-fable-5-1 as EC drew no extra spend on 2026-10-16 (Route F). Please
reconfirm that this still holds before the gate. (v0.1 OQ-05.)

**OQ2-08 Public versions of anonymous submissions (decision row, before the pilot).**
287 of 608 T1 texts are anonymous submissions; their code links and affiliations are removed by
double-blind rules, so QA1, QA2 and affiliations would measure which version was fetched (red-team M5).
Plan s7.4: tools/ex_metadata.py finds the latest public version, fetches it (one PDF per record that has one;
size small; downloads are within D0012), and a short EQ session answers QA1 a-c and QA2 a-c from it (about
1.4M-2.9M tokens at most). RQ6 reports QA1 and QA2 by version class.
Options: (a) as planned; (b) no fetch; report QA1 and QA2 stratified by anonymous_version only.
Recommendation: (a).

**OQ2-09 QA1 link check.** One dated web pass by the orchestrator over every QA1a URL (HTTP status, visible tag
or release), logged at evidence level E1, fills QA1d; until it exists QA1 is published two-level.
Recommendation: yes, run once after production.

**OQ2-10 Minimum human reading (decision row, before production).**
Option (a): a human gold subset, 6 gate records (2 per stratum), unit values and QA sub-items checked against
the PDF, about 3 hours; it estimates the error the Claude-model pair cannot see (red-team M12). Option (b):
none; the limitation is stated as D0034 states it for screening.
Recommendation: (a) if the human author has the 3 hours; otherwise (b) with the row.

**OQ2-11 QA8 status (decision row, before the pilot).**
QA8's claim statuses reuse part of the suspended evaluability construct (D0008). Plan s7.3: QA8 is
descriptive only (no composite, no sensitivity rule), has a not-checkable status, and is published only if the
CL status kappa over every claim either reader listed reaches 0.60 in the gate and in the 10 percent reading.
Recommendation: approve.

**OQ2-12 CT1-CT6 publication.** Publish a claim type only where its kappa reaches 0.60 in the gate and in the
10 percent reading (v0.1 OQ-03 option (a)). Recommendation: approve.

## C. Gate and production

**OQ2-13 Gate thresholds and decision rule (decision row, before Stage B).**
Plan s10.4 with the operating characteristics of s10.6: blocks LB90(raw) >= 0.70 and kappa >= 0.60; F1_H LB90
>= 0.70; F1_G and F1_K LB90 >= 0.60; value agreement LB90 >= 0.85; rq_class >= 0.75; S14 and F1 unit identical in
at least 23 of 30; flags in at most a quarter of judged fields per block; one re-gate. They must not change
after the first gate row. Recommendation: approve as drafted or edit now.

**OQ2-14 Cost ceiling and fallback ladder.** G7: median EA tokens per gate record at most 120k, P90 at most
200k, median H at most 10 and K at most 30; ladder: narrow K, then sample 90, then C2 completion-only, then H =
F1 only, each step brought back to the user. Recommendation: approve.

**OQ2-15 Who builds and approves the benchmark and metric lookups.** Built from Stage A by the orchestrator
and method-architect, frozen with v1.0; later additions only by EC under a new lookup version with a log line.
Recommendation: approve; red-team reviews lookup v1 with the gate files.

**OQ2-16 Aggregate-column rule (decision row with s13 row 3).** For sub-scores of one benchmark only the
aggregate column becomes a contrast unit (plan s5.4). It narrows protocol s5 further than v0.1 did.
Recommendation: approve; per-category results stay in the text file and can be added later for a named question.

**OQ2-17 Model family of the second reader.** All roles are Claude models. Re-run the 10 percent agreement
sample with Codex after 2026-11-10 as a sensitivity check, if time allows (v0.1 OQ-23 option (c)).
Recommendation: as before.

## D. Carried over from v0.1 (still open; recommendation unchanged unless noted)

**OQ2-18 Protocol freeze** (v0.1 OQ-19): freeze the form at v1.0 with a tag and hashes and a protocol s10
amendment citing it; ask the professor whether the protocol should be frozen as amended.

**OQ2-19 Independent groups for pooling** (v0.1 OQ-18): the statistician fixes the rule before any pooling;
M11 affiliations (from metadata), S08 checkpoints and M16 family_id keep every option computable.

**OQ2-20 Census coding of studies already in the 176-rank random sample** (v0.1 OQ-15): code fresh and blind,
report agreement with the earlier final rows as test-retest.

**OQ2-21 Task-family readings and state-space edge cases** (v0.1 OQ-08, OQ-09): as drafted in the brief
(decision row, s13 row 21).

**OQ2-22 Study type as one value** (v0.1 OQ-10): one value; the first listed contribution decides.

**OQ2-23 Version extracted** (v0.1 OQ-17): extract from the screened PyMuPDF text and record its version; check
the latest version where a number enters a pooled estimate (decision row, s13 row 16).

## v0.1 questions settled by v0.2

| v0.1 | Where it went |
|---|---|
| OQ-01 scope | OQ2-01 to OQ2-06; plan s2 |
| OQ-02 evaluability amendment | plan s13 row 2 (still needs the row and the s10 amendment) |
| OQ-04 independent double extraction | adopted; plan s8.2; s13 row 6 |
| OQ-06 contrasts narrowed | plan s5.3; s13 row 3; OQ2-16 |
| OQ-07 headline definition | plan s5.2 (abstract outcome numbers plus F1); s13 row 4 |
| OQ-11 QA1 and QA2 offline | plan s7.2, s7.4; OQ2-08, OQ2-09 |
| OQ-12 NA scores | plan s7.1 (NA for QA4-QA8 by rule); s13 row 5 |
| OQ-13 anchors | plan s7.1 with unclear and bounds; s13 rows 5, 12 |
| OQ-14 QA dual rating | OQ2-01 (packages MIN, REC, FULL) |
| OQ-16 pilot composition | resolved by the stratified gate (P(no multimodal) = 0) |
| OQ-20 pilot thresholds | OQ2-13 |
| OQ-21 nonlang_only | OQ2-06 |
| OQ-22 human reading | OQ2-10 |

## Draft decision rows (orchestrator enters after the author answers; none entered)
1. Scope (OQ2-01 to OQ2-06): text in plan s2.9.
2. Evaluability suspension and the s10 amendment (s13 row 2).
3. Contrast, headline and aggregate-column definitions (s13 rows 3, 4; OQ2-16).
4. QA rules: sub-items with unclear, bounds, NA rules, S14 anchoring, run definition, QA1 two-level, QA8
   descriptive and gated, CT per-type rule (s13 rows 5, 11, 12, 13, 17; OQ2-09, OQ2-11, OQ2-12).
5. Second reading and adjudication route (s13 rows 6, 9; OQ2-07).
6. Version rules (s13 rows 15, 16; OQ2-08, OQ2-23).
7. Gate design, thresholds, cost ceiling (s13 row 19; OQ2-13, OQ2-14).
8. Human reading (s13 row 10; OQ2-10) and error-rate naming (s13 row 14).
9. Design-block changes (s13 row 22) and RQ6 strata (s13 row 23).
10. Form v1.0 freeze with hashes after the gate (OQ2-18).
