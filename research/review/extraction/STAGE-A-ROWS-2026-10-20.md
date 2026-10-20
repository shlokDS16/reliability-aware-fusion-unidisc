# Stage A decisions: one list for the human author (2026-10-20)

Stage A is the development run of the extraction form on 12 included papers (plan v0.5 s10.2). It has no pass
or fail. These are the decisions it still needs (plan v0.5 s14, items A2, A3 and A10). Reply "all rec", or give
an item number and your choice (for example "S2 b, S24 amend"). Nothing here is decided, and no ledger row has
been written. The orchestrator enters the rows after you answer. "608 includes" always means **T1, interim**:
the 608 includes among the 882 decided records (gate re-audit 2, verdict and brief item 3).

Short names used below:
- **L** means the light study fields. **Q** is quality appraisal. **H** is headline numbers. **K** is contrast data.
- **F** is the census block: the earlier value-rule coding, extended to every include by D0011.
- **C1** is unified multimodal models. **C2** is other multimodal papers. **C2b** is side-experiment papers.
- **Frame R** is the text-only includes, from which the sample is drawn.
- **EC** is the adjudicator session.
- **F1 unit** is the census's main result for a paper (codebook v1.2 rule F1).
- **S14** is the main comparison that QA3-QA6 are scored on.

## Decisions

| # | What is decided | Options | Recommended | Source | Needed before |
|---|---|---|---|---|---|
| S1 | **Package.** How much second reading the work gets. | MIN: a second reader on a stratified 10 percent only. This deviates from D0011 and from protocol s6 "two raters" (v0.2 s13 rows 7, 8). REC: MIN, plus block F read twice on every other record. This meets D0011. FULL: REC, plus a second QA rater on every record. This meets protocol s6. Option 1 tokens (v0.3 figures): MIN 53.2M-89.3M, REC 70.1M-113.9M, FULL 89.8M-145.0M. | **REC.** OQ3-02 withdrew v0.2's REC recommendation only because it depended on the reading. v0.2 recommended REC under Option 1, and D0042 chose Option 1. | OPEN-QUESTIONS-v0.3 OQ3-01 table, OQ3-02; OPEN-QUESTIONS-v0.2 OQ2-01; plan v0.5 s14 A2 | Stage A (A2 scope row) |
| S2 | **Budget ceiling.** The largest total token spend you approve. The budget check (G7) stops or narrows the work above it. | (a) Give a fixed number now. (b) Make the ceiling the chosen package's total. The orchestrator re-costs that total for Option 1 + option (d) + the v0.5 gate. The number is written into the gate row (B2). The S1 figures above leave out three later costs: the m6 second reading (1.5M-9.1M, v0.4 s2.8), the v0.5 gate at n_cap 120 (up to 21.1M-37.2M, v0.5 s2.8), and C2b under option (d). | **No recommendation in the plan.** The plan implies (b) (default, marked as such). v0.5 s10.7 step 1 applies the ceiling before Stage B, and no re-costed total exists on disk yet. | OPEN-QUESTIONS-v0.3 OQ3-09; OPEN-QUESTIONS-v0.5 OQ5-07 (n_cap); plan v0.5 s2.8, s10.7 step 1 | Stage A (A2 lists it); applied before Stage B |
| S3 | **Sample size from frame R.** This is the number of text-only papers that get contrast data (block K). | 90, 120 or 150. 95 percent half-widths of a share over the whole frame: 0.092, 0.076, 0.065. Each 30 papers costs 1.2M-2.4M under Option 1. | **120** | OPEN-QUESTIONS-v0.3 OQ3-05; plan v0.3 s2.9 draft row | Stage A (scope row); used at the production draw |
| S4 | **The 12 nonlang_only includes.** These are papers with no language output. | (1) L, Q and H, no K, a separate row in every table. (2) No extraction. | **(1).** It follows from D0042 (light fields and QA on all includes) and D0032 item 3. | OPEN-QUESTIONS-v0.3 OQ3-06; OPEN-QUESTIONS-v0.2 OQ2-06 | Stage A (A2) |
| S5 | **Papers whose include status changes later.** This covers a T1 include that is reversed at your final-set step (protocol s4 step 4). It also covers the 4 D0039 tie records (M10840, M12859, U04330, M16043), whose stratum depends on the I1 basis field. | (a) A reversed include leaves every extraction frame and estimate. Extraction already done stays on file, flagged, and is reported. The 4 tie records take the I1 value you give in the OQ5-04 workbook. (b) Another rule you state. | **No recommendation in the plan.** Default (a), marked as such. The gate audit says this rule must be written into the plan but does not block the gate. | gate-T1-reaudit-2, brief item 3 point 3; D0039 | Stage A draw |
| S6 | **Duplicate works.** A pair confirmed as one study in the human check is counted as one study. The second id leaves the frames as a report of the first. | Approve, or keep both. | **No explicit recommendation.** Plan default: approve. | plan v0.3 s13 row 30; OPEN-QUESTIONS-v0.3 OQ3-04 | Stage A draw |
| S7 | **Extra ids in the human check.** 20 more C2 ids go into the human construct check (red-team mi6). They are already in the workbook. | Approve, or check only the 29 + 10 of OQ4-04. | **Approve.** v0.5 s2.3 says this check applies under every option. | plan v0.5 s13 row 42, s2.3; OPEN-QUESTIONS-v0.5 OQ5-04 | any draw |
| S8 | **Evaluability.** Extraction does not implement the suspended evaluability rubric or hypotheses E1-E3 (D0008, D0009). A protocol s10 amendment records this. | Confirm, or reopen. | **No OQ item.** Plan default: confirm, which is what the plan implements (v0.2 s3). | plan v0.2 s13 row 2, s3 | Stage A |
| S9 | **Contrasts narrowed.** Contrast data covers only the RQ comparison classes plus ablations of the credited component. For sub-scores of one benchmark, only the aggregate column is extracted. | Approve, or extract every within-paper contrast. | **Approve.** | plan v0.2 s13 row 3, s5.3-5.4; OPEN-QUESTIONS-v0.2 OQ2-16 | Stage A |
| S10 | **Suite rule.** A table with more than 10 benchmark rows that prints an average is recorded as the average only. For LLaDA2.1 this gives 1 unit instead of 33. | Approve; or record every benchmark (the workload grows about tenfold); or a different threshold. | **No explicit recommendation.** Plan default: approve. v0.3 s5.4 implements it. | OPEN-QUESTIONS-v0.3 OQ3-10; plan v0.3 s5.4, s13 row 3 | Stage A |
| S11 | **Training-free method papers.** Other decoders on the same base model form one replacement group (U6a). That group is counted as an ablation of the credited component, never as baselines. | Approve, or treat them as baselines. | **Approve.** This is the red-team's fix. | OPEN-QUESTIONS-v0.3 OQ3-11; plan v0.3 s13 row 3 | Stage A |
| S12 | **Anchor clauses (U3).** These rules pick the reference arm of a group. The arm is found by identical values in earlier tables, with a factor-of-2 scale test. A single-task or "w/o" arm never anchors a removal group. | Approve, or keep v0.3's looser rule. | **Approve.** | OPEN-QUESTIONS-v0.4 OQ4-10; plan v0.3 s13 row 3 | Stage A |
| S13 | **Headline numbers.** These are the outcome numbers in the abstract plus the F1 number, on every include. This narrows protocol s5 "every reported headline number". D0042 names light fields and QA on all includes. H on all includes is part of the Option 1 reading that D0042 confirms. | Approve, or define headline numbers otherwise. | **Approve.** OQ2-04 recommends every include. | plan v0.2 s13 row 4, s5.2; OPEN-QUESTIONS-v0.2 OQ2-04 | Stage A |
| S14 | **Quality items from sub-items.** Each sub-item is yes, no or unclear. Each item gets low and high scores, with unclear counted as no and as yes. QA4-QA8 are NA by rule where they cannot apply. This replaces protocol s6's 0/1/2. | Approve, or score 0/1/2 directly. | **No OQ item.** Plan default: approve, as implemented in v0.2 s7.1. | plan v0.2 s13 row 5, s7.1 | Stage A |
| S15 | **Model adjudicator (A10).** claude-fable-5-1 as EC resolves disagreements in place of a human (Route F). You reconfirm that it still draws no extra spend. | Reconfirm; or not, and name another route. | **Reconfirm**, if the account still shows no extra spend. This is a fact check plus your yes. | OPEN-QUESTIONS-v0.2 OQ2-07; plan v0.2 s13 row 9, s8.3; plan v0.5 s14 A10 | Stage A |
| S16 | **QA1 code availability.** QA1 is judged from the text. One dated link check by the orchestrator (evidence level E1) fills QA1d after production. Until then QA1 is published at two levels. | Approve, or skip the link check. | **Approve (yes, run once after production).** | OPEN-QUESTIONS-v0.2 OQ2-09; plan v0.2 s13 row 11, s7.1-7.2 | Stage A |
| S17 | **Main comparison (S14).** QA3-QA6 are scored on the F1 table and a baseline chosen by rule. v0.2 used the first comparative claim instead. The new basis is reproducible but further from claims that name a comparator. | Approve, or keep v0.2's basis. | **No explicit recommendation.** Plan default: approve, as implemented in v0.3 s5.6. | OPEN-QUESTIONS-v0.3 OQ3-14; plan v0.3 s5.6, s13 row 12 | Stage A |
| S18 | **QA8 claim status.** QA8 is descriptive only, with a not-checkable status. It is published only if its kappa reaches 0.60 in the gate and in the 10 percent second reading. | Approve, or drop QA8. | **Approve.** | OPEN-QUESTIONS-v0.2 OQ2-11; plan v0.2 s13 row 13, s7.3 | Stage A |
| S19 | **Version extracted.** Data come from the screened PyMuPDF text, and its version is recorded. The latest version is checked only where a number enters a pooled estimate. | Approve, or always use the latest version. | **Approve.** | OPEN-QUESTIONS-v0.2 OQ2-23; plan v0.2 s13 row 16 | Stage A |
| S20 | **Task families and state spaces.** These are fixed readings of the protocol's lists. Captioning and knowledge multiple choice go under understanding. Editing means non-text editing. Edge cases are handled as drafted. | Approve as in the brief, or amend. | **As drafted in the brief.** | OPEN-QUESTIONS-v0.2 OQ2-21; plan v0.2 s13 row 21 | Stage A |
| S21 | **Design-block changes.** D12 levers are derived by script. D13 design_fit is dropped. Two fields are added: D15 training objective and D16 provenance (contributed or inherited). | Approve, or keep the framework-v2 D1 list. | **No OQ item.** Plan default: approve, as implemented in v0.2 s4.3. | plan v0.2 s13 row 22, s4.3 | Stage A |
| S22 | **Figures.** Numbers printed inside figures are not extracted. A condition never splits figure units. Figure trends are coded only from a stated sentence. | Approve; or allow figure data labels, which needs a validator design. | **Approve.** | OPEN-QUESTIONS-v0.3 OQ3-12; OPEN-QUESTIONS-v0.4 OQ4-11; plan v0.3 s13 row 28; v0.4 s13 row 35 | Stage A |
| S23 | **Unmapped benchmark and metric names.** These match on the normalised printed string. A lenient match and the share of such units are reported, not gated. | Approve, or use a lenient match as primary. | **Approve.** The simulation does not depend on this choice. | OPEN-QUESTIONS-v0.4 OQ4-12; plan v0.4 s13 row 34 | Stage A |
| S24 | **Contrast attribute rules KA1-KA4.** KA1: higher-is-better comes from a printed arrow or statement, else a fixed list, else null. KA2: when budgets count as matched across arms. KA3: likelihood or generated scoring. KA4: when an ablation removes the credited component. Under KA2, a diffusion-vs-autoregressive group counts as "matched" only if the diffusion steps equal the generation length. Many such groups will therefore leave RQ2 pooling. | Approve as in brief v0.5 block K. Or amend KA2 per red-team mn3: when both steps and NFE are stated and differ, NFE takes precedence. | **No explicit recommendation (OQ5-13 asks "approve or amend").** Plan default: approve. The mn3 amendment is the red-team's fix (minor). It needs a brief edit and a rerun of the contamination check (A12). | OPEN-QUESTIONS-v0.5 OQ5-13; plan v0.5 s13 row 36; redteam-extraction-v0.5 mn3 | Stage A |

The three tool rules of item 12 (G1, E1 coverage, derived fields) are a separate answer. See
`ITEM12-RECOMMENDATIONS-2026-10-20.md`. That file says Q2 and Q3 are needed before Stage A results are scored,
and Q1 before Stage B.

## Not decisions: work before Stage A

- **A1 T1 gate: met, within its scope.** The verdict is PASS WITH CORRECTIONS for the 882 decided records and
  the 608 includes (T1, interim). The draw frame is pinned by sha256 c9770998... (gate-T1-reaudit-2, verdict;
  brief item 3).
  - Corrections 23 and 24 are in commit e7645bb, according to its message.
  - The next T1 audit checks them. Nothing else blocks the draw.
- **A4: open (gate-auditor).** This is the gate-auditor's check of block F and the readings C-F1a to C-F1e
  (v0.3 s13 row 27; OQ3-13).
  - The audits folder has no such file.
  - It becomes a decision only if a reading changes a census coding. That would need a codebook version.
- **A5: open (your hands-on work, then the orchestrator's).** You fill in `human-check-oq5-04.xlsx`, about 1.5-2.5 h
  (OQ5-04). Then the orchestrator:
  - writes mm-construct.jsonl, strata-overrides.jsonl and duplicate-works.jsonl;
  - reruns strata.py and multimodal_options.py;
  - records the hashes.
- **A6: met.** Red-team v0.5 has 0 critical findings, 3 major and 5 minor (redteam-extraction-v0.5, verdict and
  counts).
  - Its condition for Stage A: the Stage A report must include the MJ1 sign-coverage counts (s5 item 8).
  - The Stage A integration log prints such a line on test data (stageA-integration-log.txt l.44).
  - MJ1-MJ3 block Stage B, not Stage A.
- **A7: tools built.** See commit 57589c4 and stageA-gaps-log.txt. The orchestrator or an auditor should tick
  A7 against its list. I did not run the tools.
- **A8 / OQ5-17: done.** v0.5 is committed (017202d) and so is its red-team review (28193e3). The s14 line still
  says "not committed".
- **A9: open (orchestrator).** Show that ft_isolation_check.py and ft_model_check.py are unchanged and pass. The
  red-team did not verify "passing" (s5 item 6).
- **A10: a confirmation, not a design choice.** It is listed as S15 because only you can reconfirm the route. The
  orchestrator can check the usage record first.
- **A11: partly open (method-architect).** `analysis/extraction/we-expected.jsonl` exists (275 lines) but holds no
  KA attribute values; grep for the KA field names returns 0. Add them after S24 is answered (red-team v0.5 s5
  item 5).
- **A12: met for the s10.8 files.** Rerun brief_contamination_v05.py after any brief edit, for example the S24
  amendment.

## Already settled

- **D0042 (scope)** settles three things:
  - OQ3-01: the reading OQ3-01 calls Option 1, light fields and QA on all includes.
  - OQ4-03 and v0.4 s13 row 33: the multimodal construct is option (d). This replaces OQ2-02 and OQ3-03.
  - Most of OQ2-04 (see S13).

  It applies after the human check (A5).
- **D0043 (public versions)** settles OQ2-08 and plan v0.2 s13 row 15. Its tool is tools/fetch_public_versions.py
  (commit c562e59, not yet run).
- **D0039** sets the tie rule that S5 builds on.
- **D0041** keeps its 3 records outside the 608.
- **Reviews and gate:**
  - OQ3-16 (T1 gate) is answered by gate re-audit 2.
  - OQ3-17, OQ4-16 and OQ5-16 (red-team reviews) are done.
  - OQ5-17 (commit) is done.

**Stage B, not asked tonight.** These items are:
- OQ5-02 sign gating (recommendation (i), row 37);
- OQ5-08 levels (row 38);
- OQ5-07 rule and n_cap (rows 39-40);
- the mi4 check (row 41);
- the gold subset (OQ2-10, B6);
- item 12 Q1.

Red-team v0.5 puts Stage B on NO-GO until MJ1-MJ3 are fixed. MJ2 in particular asks for the P80/P50 choice to be
re-made, so asking now would be premature. OQ3-15 (long-tail workload) is recommended for after Stage A.
