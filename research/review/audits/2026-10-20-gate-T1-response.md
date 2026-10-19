# Response to the gate audit of T1 full text (2026-10-20)

Audit: `2026-10-20-gate-T1-fulltext.md` (verdict FAIL; 2 major, 7 minor, 4 info). Orchestrator: session 9d5203d7.
Status of each finding. "Done" means committed; "needs the human author" means a decision row or a choice that
the orchestrator must not make alone.

| # | Finding | Status |
|---|---|---|
| 1 | t1b081 B rows written by `claude-opus-5` after a safety-classifier stop | **Done (in progress):** B logged failed (batch-log), rows/isolation/quote files renamed `*-DISCARDED-model-fallback`, B rerun with `claude-opus-5-5` in a fresh folder; C rulings on M07919 (c-t1-15) and U04280 (c-t1-16) superseded (`analysis/screening/ft-t1/c-superseded.jsonl`) because C saw the invalid rows; any record that still needs C after the rerun goes to a new C group; then decisions, summary, agreement, K and PRISMA are regenerated. `tools/ft_model_check.py` checked all 219 mapped A/B/C sessions: no other mismatch (2 harness API-error turns, `<synthetic>`, in t1b010 A and t1b043 A); the check now runs inside `ft_postbatch.py` and `ft_cpost.py`. Record: `analysis/screening/ft-t1/model-check-2026-10-20.jsonl`. |
| 2 | T1 not closed (348 rescue positives; seed-corpus route; 18 sample, 1 C8, 4 TA passes pending) | **Needs the human author** (USER-ACTIONS 16a, 16b). Until then every document labels 885/608/277 as "T1 screened so far (interim)". |
| 3 | Two unused t1b078 dispatch folders without a log line | **Done:** two `discarded` events in batch-log. |
| 4 | Quote return skipped for 18 records in t1b001-t1b024 (sessions could not be resumed) | **Needs the human author:** proposed decision row below (deviation, disclosed in methods). All 18 went to C. |
| 5 | 9 A=B records differ on a secondary field (code, i1, nonlang_only); refresh takes A's value | **Needs the human author:** proposed rule below. |
| 6 | D0034 cites kappa 0.853 (n = 715); the file now gives 0.895 (n = 885) | **Needs a note row** (proposed below); the manuscript must cite the value that matches its n. |
| 7 | PRISMA lacks C8 and sample boxes | **Done:** `prisma-flow.json` recheck.boxes: sample 100 -> 82 screened (4 include, 78 exclude), 18 not yet screened; C8 32 -> 31 screened (1 include, 30 exclude), 1 not yet screened (M14933). |
| 8 | Session self-report not logged for A/B | **Done** in substance: transcript model ids are now logged per session (`model_ok_A/B` in batch-log, `model_ok`/`models_seen` in c-run-log) and recorded for all past sessions in the model-check file. The self-report itself is not asked of screeners (it would add a turn that the isolation rules do not cover); the transcript id is the stronger evidence. Disclose in methods. |
| 9 | `ft` provenance string says "open-access PDF" for every record | **Done:** `analysis/screening/ft-t1/t1-provenance.jsonl` (route per record from fetch-log: arXiv 304, OpenReview API 404, e-gateway via Chrome 61, ACL 47, OA URL 32, remaps 30, OA retry 7); `tools/ft_dispatch.py` string corrected for future dispatches. |
| 10-13 | Info | Disclose in methods: discarded sessions changed one decision toward caution (t1b001 A, M06963); re-check records concentrated in part 19 (screeners blind); pilot records screened twice, pilot rows unused. |

## Proposed rows for the human author (not yet in the ledger)

**P1 (finding 4), deviation.** "In t1b001-t1b024, 18 records with an unaccepted evidence quote could not be
returned to their screener because the screener sessions could not be resumed (batch-log l.77-94,
`quote_return_not_possible`). Instead of the one return of criteria v1.6 s4 item 2, all 18 were sent to C
(c-queue-2: 13 queued only for this reason). Effect: more conservative (C reads every such record). Disclosed in the
methods with the 18 ids in the supplement."

**P2 (finding 5), rule.** Recommended: "When A and B agree on the decision but differ on a secondary field (exclusion
code, I1 basis, nonlang_only), the human author resolves the field at protocol s4 step 4; until then counts are
reported with A's value and the sensitivity with B's value (exclude codes X0 76-77, X2 86-87, X3 6-7, X4 3-4; I1 a
552-555, ab 15-17, b 38-39; nonlang_only 12 either way)." Alternative: a fixed tie-break (earliest code in the
screener copy's section C order) stated in the methods. 9 records: M17653, M18667, M17462 (code); M10840, M12859,
U04330, M16043 (i1); M11389, M18059 (nonlang_only). (Counts to be re-derived after the t1b081 rerun.)

**P3 (finding 6), note.** "D0034's kappa 0.853 [0.799, 0.903] is A-B agreement on t1b001-t1b076 (n = 715; id-set sha256
equals human-validation-t1/sample-manifest.json frame_sha256). After part 19 the file reports the T1 value on
n = 885 (to be re-derived after the t1b081 rerun). The manuscript cites the value whose n it states."

## Re-audit

After the t1b081 rerun and its C group: regenerate all derived files, then ask gate-auditor for the re-audit
(same scripts). Findings 2, 4, 5, 6 stay open until the human author acts on P1-P3 and items 16a/16b.

## Update after re-audit 1 (`2026-10-20-gate-T1-reaudit-1.md`; finding 1 closed)

| # | Finding | Status |
|---|---|---|
| 14 | 3 B-unavailable records (M13184, M15873, M17195; classifier stop -> fallback in 3 of 3 B sessions) parked without a decision row | **Needs the human author**: row P4 below. |
| 15 | PRISMA lumped the 3 with "not yet screened" | **Done**: status `awaiting_second_screener_B_unavailable` (ft-routes-extra 3); C8 box lists them under `awaiting_second_screener` (C8: 32 -> 28 decided, 3 awaiting B, 1 not retrieved). |
| 16 | `ft_model_check.py` skipped agent-map lines with a label before the id | **Done**: id taken from any token; map sweep now 223 sessions, 3 mismatches = exactly the 3 discarded B sessions. |
| 17 | Model-check record stale | **Done**: regenerated `model-check-2026-10-20.jsonl`. |
| 18 | Provenance left out the 3 pending records | **Done**: 885 rows. |
| 19 | progress.md showed 885/608/277 without "interim" | **Done** in HANDOFF 18. |
| 20 | c-t1-15/16 ruled on 6 other records with invalid t1b081 rows in view | Info. Those 6 records (incl. K records M03416, R1202) are from other batches; C's dispatch folders held per-record screener rows, so the t1b081 rows were present only for M07919/U04280 and could not enter the other rulings, which rest on each record's own text and rows. They stand. |

**P2 ranges updated** (after the rerun): exclude codes X0 77-78, X2 85-86, X3 6-7, X4 3-4; I1 a 552-555, ab 15-17, b 38-39.

**P4 (finding 14), decision row, options for the human author.** Criteria v1.6 s4 item 1 applied per record: no
other model may act as B. Route for M13184, M15873, M17195 (A: exclude X1 nontext for all three):
(a) **recommended**: the human author screens the 3 blind to A's rows (closest to the protocol's fallback when C cannot
run; about 10 minutes); (b) C (Fable) rules with A's row alone (outside C's role; may hit the same stop); (c) A's
decision stands as a disclosed deviation. Reporting either way: agreement stays at n = 882; PRISMA shows them as
awaiting a second screener until resolved.
