# Gate audit: full-text screening tranche T1 (Paper 1, PRISMA review)

```yaml
agent: gate-auditor
date: 2026-10-20
brief: gate audit of full-text tranche T1 against criteria-v1.6.md s4-s5 and criteria-v1.6-screener.md s E-F; D0034
sources_examined:
  - research/review/screening/criteria-v1.6.md (s0, s4, s5), criteria-v1.6-screener.md (s C-F)
  - research/ledgers/decisions.jsonl rows D0032, D0034
  - research/review/fulltext/t1-batches-part1..19.json, dispatch-log.jsonl
  - analysis/screening/ft-t1/ (93 batch folders, batch-log.jsonl, c-queue-1..9.jsonl, c/c-t1-01..18, t1-decisions-all.jsonl, t1-summary-all.json, t1-not-retrieved.jsonl)
  - analysis/screening/c-run-log.jsonl, agreement-ft-t1.json, ta-recheck-k.json, ta-recheck-sample-v1.3-frozen.json, ta-recheck-frame-v1.3-frozen.jsonl, ta-recheck-c8-candidates-v1.4.jsonl, ft-routes-extra.jsonl
  - research/review/fulltext/ft-routes.jsonl; analysis/prisma/prisma-flow.json, prisma_flow.py; tools/ft-session/refresh_t1.py; tools/ft_dispatch.py; tools/ft_isolation_check.py
  - the 210 subagent transcripts named by the agent ids in the isolation-*.json files (~/.claude/projects/C--Users-Shlok-Downloads-Multi-Modality-Language-model*/<session>/subagents/agent-<id>.jsonl)
coverage: >
  Every row file, log, queue, adjudicator row, summary and PRISMA field named in the brief was recomputed with
  throwaway scripts (python -I, scratchpad only). The isolation checker was re-run on all 210 transcripts and every
  transcript's model ids were read. NOT covered: the correctness of any screening decision against the full text
  (no full text was read); the human validation sheet (waived by D0034); git history before 2026-10-16.
  progress.md was not ticked or unticked and no ledger row was added, because the brief makes this audit read-only
  apart from this file.
status: verdict below
```

## Verdict: FAIL

One batch has no valid Screener B rows. The 10 FB rows of t1b081 were written by `claude-opus-5`, not by
`claude-opus-5-5`, after a safety-classifier stop partway through the session (finding 1). Criteria v1.6 s4 item 1
says "No fallback for A or B", so criterion 1 ("exactly one FA and one FB row") is not met for those 10 ids, and
every T1 count that uses them (decisions, agreement, C queue, K, PRISMA) rests on rows from a model the protocol
does not allow. Apart from this, everything I checked reproduces exactly from the row files, with no difference:
decisions, summary, agreement, K and PRISMA. The re-audit can be narrow: findings 1 and 2 plus the minor corrections.

## Checklist (brief items 1-9)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | One FA and one FB row per planned id; DISCARDED files logged with a rerun | **partly** | 93 batches and 885 ids across 19 plan parts, no id in two batches, no batch in two parts. FA 885, FB 885, no duplicates, id sets equal the plans, screener fields correct. All 6 DISCARDED row files (t1b001 A, t1b026 A, t1b036 B, t1b040 A, t1b048 A, t1b056 A) have a `discarded` event (batch-log l.2, 43, 98, 108, 123, 140) and a later result line with a passing rerun. **Exception:** t1b081 FB came from a disallowed model (finding 1). |
| 2 | Isolation of every A/B/C session; failed sessions logged and their rows unused | **partly** | 186 isolation-A/B.json and 18 isolation-C.json files all have `pass: true` with no flags; the 6 DISCARDED isolation files have `pass: false`. No basename is reused (dispatch-log, 227 non-pilot dispatches). I re-ran `tools/ft_isolation_check.py --vault` on all 210 transcripts and got the same verdict in every case (204 pass, 6 fail). C runs: one failed session (c-t1-12, laptop crash, 0 rows) was logged and rerun (c-run-log l.17-18). Gaps: two dispatches have no log line (finding 3), and t1b081 B had a model substitution that the isolation check cannot see (finding 1). |
| 3 | Quotes returned once; still-unaccepted records sent to C | **partly** | No evidence item lacks a quote-check entry. 38 `quote_return` events cover 48 ids, none returned twice, and no decision changed after a return (consecutive result lines identical). After the return, 2 quotes were still not accepted (M09594, M18364) and 1 was truncated (M16826); all three were queued (c-queue-1, -6, -5). 22 entries are still unaccepted in the final files, and every one is queued. **Deviation:** the 18 records with unaccepted quotes in t1b001-t1b024 were never returned. They went straight to C (`quote_return_not_possible`, batch-log l.77-94), and no decision row covers this (finding 4). |
| 4 | Every disagreement or adjudicate row ruled by exactly one C session; no unqueued rulings | met | 100 records have a disagreement or an adjudicate row; all 100 are queued. 116 records are queued in total (100 plus 16 quote-only), with no duplicates. 116 FC rows, each id ruled once, all by `FC-claude-fable-5-1`, include/exclude only. 0 queued without a ruling, 0 rulings without a queue entry. The C dispatch ids_sha256 equals the FC id set for all 19 C dispatches. The queue's A/B labels match the rows. Final quote-check-C files: every entry `found`. Every complete C session passed isolation. Every C transcript is `claude-fable-5-1` only. |
| 5 | Reproduce t1-decisions-all.jsonl and t1-summary-all.json | met (with a note) | 885 rows, 0 differences in decision, code, xsub, i1, nonlang_only, source or batch; the summary matches field by field. Note: when A and B agree on the decision but differ on code, i1 or nonlang_only, the refresh script silently takes A's value (9 records; finding 5). |
| 6 | Recompute the headline agreement | met | See the numbers below. Every point estimate and 2 x 2 count matches. Bootstrap (2000 draws, seed 20261024) gives 0.8602-0.9272 against the filed 0.8603-0.9272, a 0.0001 difference in the resampling implementation. |
| 7 | Re-check: sample sha256, K, and what s5.2 requires | met | sha256 of the sample is `958867658120c323446ee5692ec82702deb4464e0977a6030287ced035b7ac6c`, the same as s5.1. The frame (`a9180fe4...d79a`), C8 (`6c4928af...e825`) and OC (`3f9c610e...a7a8`) hashes also match. K = 4 (M03416 C, M10984 A=B, R0963 A=B, R1202 C); 78 sampled excluded; 18 not yet in T1. Identical to ta-recheck-k.json. None of the 4 is in t1b081 (they are in t1b078, t1b085, t1b085 and t1b082), so finding 1 cannot lower K; a t1b081 rerun can only raise it. |
| 8 | PRISMA T1 numbers | met (with a note) | Every T1 field in prisma-flow.json matches (numbers below). The separate C8 box required by s5.3 is missing (finding 7). |
| 9 | Other threats to the T1 counts | see findings 1, 2, 3, 8-13 | No record was screened twice within T1, no id is in two batches, and no row is filed under two batches. Criteria version: the screener file sha256 is `6e9d050b...6a2`, unchanged since commit dbaeab0 (2026-10-16 07:19). That is before the route line (f9eec19, 09:33) and before the first FT rows (0090e75, 10:58). `tools/ft_dispatch.py` has copied only `criteria-v1.6-screener.md` since it was created (ccf9c16). |

## Findings

**1. Major. Screener B rows for t1b081 were written by a fallback model.**
Evidence: transcript `~/.claude/projects/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-334706/9d5203d7-a6be-4a10-8e9d-83c85c9e81ca/subagents/agent-abb630a971fe44710.jsonl`
(basename `B-t1b081-01eb40f8-70a9-4769-84f5-02739e381978`). Line 196 (05:45:55Z) records "Your response above was
stopped by a safety classifier". Line 197 is a `thinking_drop` attachment with `model: claude-opus-5`, reason
`model_mismatch`. Lines 198-231 are 12 assistant messages from `claude-opus-5`, including the `Write` of the
output file (l.226) and the handback (l.231). The quote return (l.236-249) went back to `claude-opus-5-5`. The rows
still say `"screener": "FB-claude-opus-5-5"`. isolation-B.json passes, and batch-log l.194/198/200 do not mention
the switch. This was the only model mismatch across all 210 transcripts (223 copies checked). Records affected:
M14023, U04280, M13184, M16235, M03148*, M10111*, M07919*, U00696, M17195, M15873 (* = re-check sample). The B rows
create the A/B disagreements on M07919 and U04280 that sent them to C. They also make the other 8 count as A=B.
Rule broken: criteria-v1.6.md s4 item 1 ("No fallback for A or B") and screener copy s D.
Required correction: log t1b081 B as failed (technical: model substitution after a classifier stop). Rerun B with
`claude-opus-5-5` in a fresh folder, run quote_check and the one return, and send any new disagreement or
adjudicate row to C (Route F). Then regenerate t1-decisions-all.jsonl, t1-summary-all.json, agreement-ft-t1.json,
ta-recheck-k.json and prisma-flow.json. Add a transcript model-id check (every assistant `message.model` equals the
dispatched id) to the post-batch script, and run it on every C session too.

**2. Major (scope). T1 is not closed, so these counts are interim.**
Evidence: prisma-flow.json `open[0]`: 348 free-source rescue positives were never dual-screened or routed to full
text, and D0029 and D0030 conflict on them. `open[1]`: none of the seed-corpus passes (1,243) are in T1 and their
route is unconfirmed. Not yet screened: 18 sampled re-check records, 1 C8 record (M14933) and 4 unrouted TA passes
(ft-routes-extra: 13 + 5 + 1 + 4 pending). ft-routes also lists 51 pending e-gateway and 51 failed OA fetches.
Criteria v1.6 s4 item 6 defines T1 as all title/abstract passes plus the 32 C8 and 100 sampled records.
Required correction: record a decision on the 348 rescue positives and on the seed-corpus route before T1 is
called complete. Until then, label the 885/608/277 figures as "T1 screened so far" in every document.

**3. Minor. Two dispatch folders have no log line.**
Evidence: dispatch-log.jsonl l.190-191 (`A-t1b078-8d23082f-...`, `B-t1b078-1e9db6f4-...`, built on 2026-10-17,
commit 52f643f). They appear in no isolation file, batch-log event or agent-map line. Only progress.md l.47-48
says "t1b078 folders were built in the old scratchpad (unused)". t1b078 holds K record M03416.
Required correction: append a batch-log `discarded` event for each folder ("folder built, never used"), as was done
at l.39-40, citing the absence of a transcript.

**4. Minor. The quote return was skipped for 18 records in t1b001-t1b024.**
Evidence: batch-log l.77-94 (`quote_return_not_possible`, reason: earlier screener sessions could not be resumed).
Criteria v1.6 s4 item 2 requires one return. All 18 were sent to C, which is conservative: 13 were queued only for
this reason (c-queue-2). No decisions.jsonl row covers the deviation.
Required correction: add a decision row (deviation, with reason and the 18 ids) and disclose it in the methods.

**5. Minor. A=B records that differ on a secondary field are resolved silently in A's favour.**
Evidence: tools/ft-session/refresh_t1.py l.21-22 (`r = C[i] if i in C else A[i]`). Nine records are affected:
- code: M17653 X1/X2, M18667 X0/X3, M17462 X4/X1
- i1: M10840 a/ab, M12859 a/ab, U04330 a/ab, M16043 ab/b
- nonlang_only: M11389 true/false, M18059 false/true

With B's values the counts would be: exclude codes X0 76, X1 103, X2 87, X3 7, X4 3, X7 1 (filed: 77, 103, 86, 6,
4, 1); include_i1 a 552, ab 17, b 39 (filed: 555, 15, 38); nonlang_only 12 (unchanged). M18667's B code (X3) comes
earlier in the s C code order than A's (X0).
Required correction: state the tie-break rule in the methods, or send these 9 records to the human author's
resolution (protocol s4 step 4), and report the code and i1 counts as a range or with the sensitivity above.

**6. Minor. D0034 cites an agreement value that the cited file no longer holds.**
Evidence: D0034 cites agreement-ft-t1.json as kappa 0.853 (0.799-0.903). The file now gives 0.8949 (0.8603-0.9272)
on 885 records. I reproduced 0.853 (bootstrap 0.7992-0.9033) on t1b001-t1b076 (715 records). The sha256 of those
sorted ids is `1d29e553...1403`, which equals `frame_sha256` in human-validation-t1/sample-manifest.json.
Required correction: append a note row that pins both values with their n, and make sure the manuscript cites the
value matching its stated n (after finding 1 is fixed).

**7. Minor. PRISMA has no C8 box and no per-box outcomes for the re-check.**
Evidence: prisma-flow.json `recheck` gives only to_full_text 132 and full_text_screened 113. Criteria v1.6 s5.3
says C8 records are "reported in their own PRISMA box". Recomputed from the files:
- C8: 32 → 31 screened (include 1, M15804, A=B; exclude 30) and 1 not yet retrieved (M14933).
- Sample: 100 → 82 screened (include 4, exclude 78) and 18 not retrieved.

Both groups are inside the 608/277 totals.
Required correction: add both boxes in prisma_flow.py.

**8. Minor. The session self-report required by s4 item 1 is not logged for A/B.**
Evidence: batch-log and dispatch-log record only the harness model id (dispatch-log `model`). Criteria v1.6 s4
item 1 asks for "the session's self-report beside it". The transcript check in this audit stands in for it, except
for t1b081 B.
Required correction: log the self-report or the transcript model ids (see finding 1) in each result line.

**9. Minor. The full-text provenance string is wrong for some records.**
Evidence: tools/ft_dispatch.py l.47 hard-codes "pymupdf-1.27.2.3 text of the open-access PDF" into every dispatch.
All 885 A rows carry it, including OpenReview texts (t1b035-t1b076) and the e-gateway and OA-retry texts of part 19.
Required correction: report the true route from fetch-log.jsonl in the supplement. Do not use the `ft` field as
provenance.

**10. Info. The isolation and model checks were independently reproduced.** tools/ft_isolation_check.py re-run on
all 210 transcripts (with the vault test) agrees with every filed verdict. Model ids match the dispatch for 98 A,
93 of 94 B and 18 C transcripts.

**11. Info. Discarded sessions did not change outcomes.** Comparing the 6 DISCARDED row files with their reruns,
the only change is t1b001 A, M06963 exclude → adjudicate (more conservative). In t1b026 A, a session first accepted
as a false positive (batch-log l.42) was then discarded under the strict reading (l.43). The rows were identical.

**12. Info. Re-check records are concentrated in part 19.** All 113 screened re-check records (82 sample + 31 C8)
are in t1b077-t1b093, 3 to 7 per batch, mixed unflagged with 57 ordinary records. The exclusion rate there is
126/170 (74 percent) against 47/383 in the OpenReview part (t1b035-t1b076). Screeners were blind to the
composition, but the context shift should be disclosed.

**13. Info. Pilot records were screened twice.** The 8 pilot records (ft-pilot01, after the route line, before T1)
were screened again in T1. The pilot rows are not used (pilot-report.json says so).

## What s5.2 requires given K = 4

K ≥ 1, so all 797 frame candidates are screened at full text. The 82 already screened in T1 are part of the 797,
which leaves 715. The 18 unretrieved sample ids and the 14 in-frame C8 records not in the sample are among them.
Criteria v1.6 s4 item 6 makes these 715 a further tranche, with its own 15 percent human-validation draw (seed
20261016, sorted ids) that must be screened before the human author sees any A, B or C row of that tranche. D0034
waives human validation for T1 only. Report K with its denominator ("K = 4 of 82 screened sampled records; 18 not
retrieved"). The 18 cannot change the trigger. After finding 1 is fixed, K can only stay at 4 or rise.

## Recomputed numbers (from F*/FC* rows; all equal to the filed files unless stated)

| Quantity | Recomputed | Filed (file) |
|---|---|---|
| T1 screened | 885 (770 ft-routes + 113 re-check + 2 unrouted TA passes) | 885 (t1-summary-all.json; prisma-flow screened) |
| Include / exclude | 608 / 277 | 608 / 277 |
| By part: t1b001-034 / t1b035-076 / t1b077-093 | 228/104, 336/47, 44/126 | same |
| Exclude codes | X0 77, X1 103, X2 86, X3 6, X4 4, X7 1 | same |
| Include i1 | a 555, ab 15, b 38; nonlang_only 12 | same |
| Ruled by C | 116 (include 52, exclude 64); basis B 65, neither 33, A 18 | 116 (52/64) |
| C queue | 116 = 100 disagreement/adjudicate + 16 quote-only (13 return not possible, 2 not accepted after return, 1 truncated) | same (agreement-ft-t1.json C_queue) |
| Pass vs exclude 2 x 2 | both_pos 635, both_neg 214, A_only 27, B_only 9 | same |
| Raw agreement / kappa | 0.9593 / 0.8949 (bootstrap 0.8602-0.9272) | 0.9593 / 0.8949 (0.8603-0.9272) |
| p_pos / p_neg / bias / prevalence | 0.9724 / 0.9224 / 0.0203 / 0.4757 | same |
| Include vs not (sensitivity) | 571/284/4/26; raw 0.9661, kappa 0.9243 | same |
| Three-way | raw 0.9277, kappa 0.8518 | same |
| Adjudicate rate A / B | 0.0983 (87) / 0.0531 (47) | same |
| Kappa on t1b001-t1b076 (D0034 frame) | 0.853, bootstrap 0.7992-0.9033, n 715 | D0034 text |
| K | 4 (M03416 C, M10984 A=B, R0963 A=B, R1202 C); excluded 78; not in T1 18 | ta-recheck-k.json, prisma-flow recheck.K |
| Re-check to full text / screened | 132 / 113 (sample 82, C8 31) | 132 / 113 |
| Reports sought | 1111 = 1000 - 27 duplicates + 138 extra | 1111 |
| X6 not retrieved | 4 (M13187, M15046, M15574, M18918; none in the sample) | 4 |
| Pending, ft-routes-extra | 23 (oa_url 16, e-gateway 7) | 16 / 7 |

## To pass on re-audit
Fix finding 1 (rerun, log, regenerate), then either decide finding 2 or carry its "interim" label into every
document. Fix findings 3-9. The re-audit will re-run the same scripts on the regenerated files.
