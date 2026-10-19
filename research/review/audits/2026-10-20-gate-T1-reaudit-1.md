# Gate re-audit 1: full-text screening tranche T1 (Paper 1, PRISMA review)

```yaml
agent: gate-auditor
date: 2026-10-20
brief: narrow re-audit of gate T1 after the FAIL of 2026-10-20-gate-T1-fulltext.md (finding 1 fix, model checks, regenerated derived files, findings 3/7/8/9, the 3 B-unavailable records)
sources_examined:
  - research/CONTRACT.md; research/review/audits/2026-10-20-gate-T1-fulltext.md; research/review/audits/2026-10-20-gate-T1-response.md
  - research/review/screening/criteria-v1.6.md s4 items 1-4 (l.172-206); criteria-v1.6-screener.md l.229-236
  - analysis/screening/ft-t1/batch-log.jsonl l.224-232; c-run-log.jsonl (last 5 lines); c-queue-1..10.jsonl; c-superseded.jsonl; t1-pending-B.jsonl; model-check-2026-10-20.jsonl
  - analysis/screening/ft-t1/t1b001..t1b093/F{A,B}-*.jsonl (and the DISCARDED files in t1b081); c/c-t1-01..19/FC-*.jsonl, isolation-*.json, quote-check-*.jsonl
  - derived: t1-decisions-all.jsonl, t1-summary-all.json, agreement-ft-t1.json, ta-recheck-k.json, t1-provenance.jsonl, analysis/prisma/prisma-flow.json (+ prisma_flow.py l.125-185)
  - tools/ft_model_check.py, tools/ft_postbatch.py, tools/ft_cpost.py, tools/ft_isolation_check.py, tools/ft-session/refresh_t1.py, tools/ft-session/agent-map.txt, tools/ft_dispatch.py l.45
  - research/review/fulltext/dispatch-log.jsonl l.201-234, t1-batches-part1..19.json, ft-routes.jsonl, fetch-log.jsonl; analysis/screening/ft-routes-extra.jsonl, ta-recheck-sample-v1.3-frozen.json, ta-recheck-c8-candidates-v1.4.jsonl
  - dispatch folders (session scratchpad ft-dispatch/): B-t1b081-fd578c26-..., B-t1b081bio-006f2e45-..., C-c-t1-15/16/19-...
  - all 359 subagent transcripts under ~/.claude/projects/C--Users-Shlok-Downloads-Multi-Modality-Language-model*/*/subagents/ (both the 334706 and the fcff62 project dirs of session 9d5203d7)
  - git log 61df436..cfb039d
coverage: >
  Every derived T1 file was recomputed from the row files with my own script (scratchpad reaudit1/recompute.py, python -I),
  using fresh code rather than the generator scripts; the bootstrap was run with the generator's resampling scheme and with a
  second resampler. Model ids were read from every assistant turn of all 359 transcripts (every copy). ft_model_check.py and
  ft_isolation_check.py were re-run. NOT covered: correctness of any screening decision against the full text; findings 2, 4,
  5, 6 beyond checking whether their numbers changed; the human validation sheet (D0034). progress.md was not ticked or
  unticked and no ledger row was added: the brief makes this re-audit read-only apart from this file.
claims:
  - statement: Every row used for t1b081 (A, B and the C rulings) comes from a transcript whose assistant turns are all the role's model.
    status: supported
    evidence: agent-a0519ee0ce0c5ba94 (sonnet-5-5 x90), agent-a1347afe5802d6599 (opus-5-5 x44, incl. the quote return), agent-a75e4c4ff69ac300a (fable-5-1 x14)
    level: E4
    confidence: 0.97
  - statement: The regenerated derived files reproduce exactly from the row files.
    status: supported
    evidence: reaudit1/recompute.out.txt (scratchpad); 0 field differences over 882 decision rows; all agreement, K and PRISMA T1 fields equal
    level: E4
    confidence: 0.97
  - statement: The 3 B-unavailable records have no valid Screener B row and no decision row covering them.
    status: supported
    evidence: t1b081/FB-t1b081.jsonl (7 ids); t1-pending-B.jsonl; decisions.jsonl ends at D0034
    level: E4
    confidence: 0.98
competing_explanations: []
unknowns:
  - whether claude-fable-5-1 (C) or any screener model can read M13184, M15873, M17195 without the same classifier stop (not tested; not to be tested without a decision row)
next_test: {hypothesis: "after the human author's rows (3 B-unavailable records, finding 2, P1-P3) the T1 counts and PRISMA still reproduce", intervention: "re-run reaudit1/recompute.py and mcheck.py on the updated files", primary_metric: "field differences = 0; mismatched used sessions = 0", falsifier: "any difference or any used session with a non-role model", gpu_hours: 0}
```

## Verdict: FAIL (no orchestrator-side blocker of substance remains; every remaining blocker needs the human author)

Finding 1 is closed as a defect: no row from a fallback model, no DISCARDED row and no superseded C ruling is used
anywhere, and every derived file reproduces exactly. But closing it left 3 planned records (M13184, M15873, M17195)
without a valid Screener B row. Criterion 1 ("one FA and one FB row per planned id") is therefore still **partly**
met. Criteria v1.6 s4 item 1 says that when B cannot be run, screening "stops until a new decision is recorded", and
no such decision row exists yet (new finding 14). Findings 2, 4, 5 and 6 are still open and need the human author.
Under the hard rule I cannot waive these, so the gate fails. The model-screening data for the 882 decided records are
clean.

## Brief item 1: finding 1 closed?

| Check | Status | Evidence |
|---|---|---|
| t1b081 A rows | met | `FA-t1b081.jsonl` content unchanged since 71b742c (2026-10-18; only its mtime changed when postbatch re-ran). Agent a0519ee0ce0c5ba94, 90 assistant turns, all `claude-sonnet-5-5`, two identical copies (334706 and fcff62 dirs). |
| t1b081 B rows | met | `FB-t1b081.jsonl` (7 ids: U04280, M07919, U00696, M16235, M10111, M03148, M14023) has the same sha256 (`df4b8b43...53bf`) as the dispatch-folder file `B-t1b081-fd578c26-.../FB-t1b081.jsonl`. Agent a1347afe5802d6599: 44 assistant turns, all `claude-opus-5-5`. That includes the one quote return (user turn l.145, which only restates the quote-check statuses, with no leak), so no fallback occurred. Fresh folder (dispatch-log l.232: 7 ids, own ids_sha256). The folder holds only CONTRACT.md, the screener copy, dispatch.json, the 7 texts and the output. Isolation re-run with `--vault`: pass, no flags. quote-check-B: 25/25 found. |
| C rulings for t1b081 | met | c-t1-19 (agent a75e4c4ff69ac300a, 14 turns, all `claude-fable-5-1`; isolation re-run: pass; quote-check-C 14/14 found). Its `screener-rows.jsonl` holds exactly the valid FA and the new FB rows for M07919 and U04280. I matched each row byte for byte against the files; none came from either DISCARDED file. FC file sha256 equals the dispatch copy. Rulings: U04280 include, M07919 exclude X0, both basis B. |
| No DISCARDED rows used | met | My loader reads exactly `F{A,B}-<batch>.jsonl` per plan batch and finds no other non-DISCARDED F file. The id sets equal the 19 plans (885 ids, 93 batches) for A, and the plans minus the 3 pending ids for B. agreement_ft_t1.py and refresh_t1.py both skip DISCARDED names. |
| Superseded rulings unused | met | 118 FC rows; the 2 superseded pairs (M07919/c-t1-15, U04280/c-t1-16) are dropped, which leaves 116 rulings, each id once. Neither superseded ruling appears in t1-decisions-all.jsonl, where both records take c-t1-19's ruling. |
| Pending 3 excluded from decided counts | met | None of the 3 is in t1-decisions-all.jsonl, the agreement pairs (n = 882; `A_only_ids` lists the 3), the C queues or K. None is in the re-check sample. All 3 are C8 records in t1b081. |
| Pending 3 visible in summary | met | t1-summary-all.json `pending_B_unavailable: [M13184, M15873, M17195]`. |
| Pending 3 visible in PRISMA | **partly** | They are counted, but under the wrong label: `status_ft_routes_extra.retrieved_not_yet_screened: 3`, and the C8 box lists them under `not_yet_screened` together with M14933, which was never retrieved. Nothing in PRISMA says "screened by A, awaiting a valid second screener", and `open[]` does not mention them (finding 15). |

## Brief item 2: model checks

- **`python -I tools/ft_model_check.py`** (map mode): `checked 221, transcript_not_found 0, mismatches 2`. The two
  mismatches are abb630a971fe44710 (original t1b081 B: `opus-5-5` 60, `opus-5` 12) and a2e60e8675da20d44 (t1b081bio B:
  `opus-5-5` 11, `opus-5` 15). Both sessions are discarded. **Defect (finding 16):** the parser requires the 3rd token
  of each agent-map line to be an agent id. It therefore silently skips `t1b081 B rerun2 a4020581c8fe4fe23` (a
  mismatch it does not report) and `t1b081 B rerun3-nonbio a1347afe5802d6599`, which is **the session whose rows are
  used**. The used session was checked once, by the per-transcript call inside ft_postbatch.py (batch-log l.229/231
  `model_ok_B: true`), and my own check confirms it.
- **Independent check** (scratchpad `reaudit1/mcheck.py`): 359 transcript files and 344 agents. 225 agents are
  screening sessions (A 103, B 102, C 20; 240 copies, and every copy has the same model counts as its twin). Exactly 3
  sessions contain a non-role model: abb630a971fe44710 (switch at l.199, back at l.237), a4020581c8fe4fe23 (switch at
  l.197) and a2e60e8675da20d44 (switch at l.62). All three are logged as `failed` (batch-log l.224, 228, 232) and their
  files are DISCARDED. All 205 sessions named by the non-DISCARDED isolation files (93 A, 93 B, 19 C) contain only the
  role's model, with the same basename in the transcript and in the isolation file. The 2 `<synthetic>` turns
  (a7a87221e4819017d l.150, a699c94c8d19f9889 l.327) are harness "API Error" notices.

## Brief item 3: reproduction of the derived files (no difference)

| Quantity | Recomputed | Filed |
|---|---|---|
| Decided / pending | 882 / 3 (M13184, M15873, M17195) | 882 / same (t1-summary-all.json) |
| t1-decisions-all.jsonl | 882 rows; 0 differences in any of the 10 fields | same |
| Include / exclude | 608 / 274 | 608 / 274 |
| By part (OA+remaps / OpenReview / part 19) | 228/104, 336/47, 44/123 | same |
| Exclude codes | X0 78, X1 100, X2 85, X3 6, X4 4, X7 1 | same |
| Include i1; nonlang_only | a 555, ab 15, b 38; 12 | same |
| C | 116 (include 52, exclude 64; basis B 65, neither 33, A 18) | 116 (52/64) |
| C queue | 118 rows, 116 unique = 100 disagreement/adjudicate + 16 quote-only (13 return not possible, 2 not accepted after return, 1 truncated); 0 unqueued, 0 unruled | same |
| Pass vs exclude | n 882; 635/211/27/9; raw 0.9592; kappa 0.8939; AC1 0.9337; bootstrap 0.8589-0.9268 (second resampler 0.8597-0.9270) | same; [0.8589, 0.9268] |
| p_pos / p_neg / bias / prevalence | 0.9724 / 0.9214 / 0.0204 / 0.4807 | same |
| Include vs not | 571/281/4/26; raw 0.9660; kappa 0.9238 [0.8955, 0.9483] | same |
| Three-way | raw 0.9274; kappa 0.8507 [0.8159, 0.8840]; AC1 0.9042; 3 x 3 table equal | same |
| Per screener | A 575/220/87 (adjudicate 0.0986); B 597/238/47 (0.0533); codes equal | same |
| Joint exclusions / inclusions | 211, same code 208, kappa 0.9786, same code+xsub 198 / 571, same i1 567, kappa 0.9478 | same |
| Per-rule citations | 17 rules, 0 mismatches | same |
| K | sample sha256 `9588...ac6c` unchanged; K = 4 (M03416 C, M10984 A=B, R0963 A=B, R1202 C); excluded 78; not in T1 18; every per-id entry equal | ta-recheck-k.json, prisma recheck.K |
| Re-check boxes | sample 100 → 82 screened (4/78), 18 not screened; C8 32 → 28 decided (1/27), 4 undecided (3 pending + M14933); to full text 132, decided 110 | same |
| PRISMA T1 | reports sought 1111; ft-routes 770 screened, 97 no text, 27 duplicates, 51 e-gateway, 21+30 OA failed, 4 X6; extra 16 OA + 7 e-gateway + 3 (the pending ids) | same |
| t1-provenance.jsonl | 882 rows, routes equal to the last `ok` fetch-log entry (arXiv 304, OpenReview API 401, e-gateway 61, ACL 47, OA URL 32, remap-arXiv 17, remap-direct 13, OA retry 7) | same |

The deltas from the first audit are fully explained by the 3 pending records: they were A=B exclude X1 rows under the
invalid B, so exclude falls from 277 to 274, X1 from 103 to 100 and both_neg from 214 to 211, and C8 decided falls
from 31 to 28. The t1b081 changes go in opposite directions on the codes: X0 +1 and X2 -1 net (M07919 is now C
exclude X0).

## Brief item 4: findings 3, 7, 8, 9

| # | Status | Evidence |
|---|---|---|
| 3 | **closed** | batch-log l.225-226: `discarded` events for A-t1b078-8d23082f and B-t1b078-1e9db6f4 ("folder built, never used"). |
| 7 | **closed, with a residue** | prisma-flow.json `recheck.boxes` has both boxes; the numbers reproduce. Residue: the 3 pending C8 records are labelled `not_yet_screened` (finding 15). |
| 8 | **closed in substance** | `model_ok_A/B` in batch-log result lines from l.227 on; `model_ok`/`models_seen` in c-run-log (c-t1-19). Not asking for a self-report needs a line in the methods (as the response says). Residue: `model-check-2026-10-20.jsonl` was written before the reruns (219 sessions) and holds only the mismatch line and the summary, not "transcript model ids for all past sessions" as the response states (finding 17). |
| 9 | **closed, with a residue** | t1-provenance.jsonl reproduces; tools/ft_dispatch.py l.45 now gives the neutral string pointing to fetch-log and provenance (seen in the new dispatch.json files). Residue: provenance covers only the 882 decided ids and omits the 3 pending records that A read (all `openreview-api`) (finding 18). |

## Brief item 5: the 3 B-unavailable records against criteria v1.6

**Facts.** In all 3 B sessions that read these records (agents abb630a971fe44710, a4020581c8fe4fe23 and
a2e60e8675da20d44), a safety-classifier stop handed the session to `claude-opus-5`. The orchestrator used none of
those rows. A (`claude-sonnet-5-5`) excluded all 3 as X1. They are C8 records, not in the re-check sample, so K is
unaffected.

**Consistency.** The handling follows criteria v1.6 s4 item 1 and screener copy l.235-236: no fallback rows, and B
was stopped. The rule says that when B "cannot be run, full-text screening does not start (or stops) until a new
decision is recorded". The orchestrator applied this per record (B ran cleanly on the other 7 records) and parked the
3 records instead of halting all screening. That per-record reading is reasonable, but it is an interpretation the
protocol does not state. The protocol also has no route for a record that one screener cannot screen. **A decision
row is therefore required, and nothing about these 3 records can be finalised without it.**

**What the row must contain.**
- **Scope:** the 3 ids, the 3 failed agents and the transcript lines where the switch happens (l.199, l.197, l.62).
- **Reading:** a statement that s4 item 1 is applied per record.
- **Route, chosen by the human author.** The options are:
  - (a) the human author screens the 3 as second screener, blind to A's row, with any disagreement or "adjudicate"
    row going to the human author's adjudication. This is the nearest analogue in v1.6: s4 item 4 sends work to the
    human author when C cannot be run.
  - (b) C (claude-fable-5-1) is given A's row alone. This is outside C's defined role, and C may hit the same stop.
  - (c) A's single-screener decision is accepted as a disclosed deviation.
- **Reporting:** the A-B agreement stays at n = 882, with the 3 reported as A-only; in PRISMA the 3 appear as
  "awaiting second screener" until resolved, then in the C8 box under the chosen route; the methods disclose the
  deviation with the 3 ids.
- **Model rule:** no other model may be tried as B (that would be a fallback).

## Brief item 6: new findings

**14. Major (needs the human author). 3 planned records have no valid FB row and no decision row.**
See item 5. This blocks criterion 1 and the C8 box.

**15. Minor. PRISMA mislabels the pending records.**
prisma_flow.py l.155 counts any retrieved id that is not in t1-decisions as `retrieved_not_yet_screened`, and the C8
box lists `not_yet_screened`. Both lump M13184, M15873 and M17195 (screened by A, B unavailable) with M14933 (never
retrieved). Fix: add a `pending_B_unavailable` field read from t1-pending-B.jsonl, in `full_text_T1` and in the C8
box, and add an `open[]` line.

**16. Minor. The map sweep of ft_model_check.py skips labelled agent-map lines.**
tools/ft_model_check.py l.48 requires `p[2]` to be an agent id. So `rerun2` and `rerun3-nonbio` lines are skipped, and
the sweep neither checks the session actually used for t1b081 B nor reports the rerun-1 mismatch. It also reports
discarded sessions as plain mismatches, and it reads only the first copy of a transcript. All copies are identical
today. Fix: take the last token matching `a[0-9a-f]{16}`, mark discarded agents in the map, and check every copy.

**17. Minor. `model-check-2026-10-20.jsonl` is stale and thinner than described.**
It records 219 sessions checked and 1 mismatch, and was written before rerun 1, rerun 3, the bio session and
c-t1-19. Fix: re-write it after fixing finding 16, with one line per session (agent, role, basename, models,
used/discarded).

**18. Minor. Provenance omits the 3 pending records.**
t1-provenance.jsonl is built from t1-decisions-all.jsonl. Fix: build it from the FA rows (885), so that every text a
screener read has its route.

**19. Minor. State files lag the regenerated numbers.**
- research/progress.md RESUME (HANDOFF 17, last commit 6795020 at 00:46) still says "T1 total: 885 records, include
  608, exclude 277", kappa 0.895, with no "interim" label.
- t1-summary-all.json and prisma-flow.json `status` say "part 19 complete" while 3 part-19 records await B.

Fix: update the label in both files (finding 2's interim label also applies).

**20. Info. Superseding was per record, not per session.**
c-t1-15 also ruled M03416 (a K record), M13335 and R0927; c-t1-16 also ruled R1202 (a K record), U03826 and U06471.
Both sessions saw the invalid t1b081 B rows for M07919 and U04280. Those rows concern other papers and C rules each
record separately, so I see no route by which they could change these 6 rulings. The response should still say in
one sentence why the 6 rulings stand.

**21. Info. B rerun 3 differs in context and matches the discarded rows.**
B rerun 3 screened 7 records in a 7-record batch (the original batch had 10). Its decisions on M07919 (exclude X0)
and U04280 (include) are the same as the discarded fallback rows, and C ruled with B on both.

**22. Info. A logging gap in the rerun-3 result line.**
The batch-log result line for rerun 3 (l.229) does not name the B agent. The agent id appears only in the quote_return
event (l.230) and in isolation-B.json.

## Status of the open findings from the first audit (numbers re-derived)

- **2 (major, scope): open.** Needs USER-ACTIONS 16a/16b. The interim label is still missing in progress.md (finding 19).
- **4 (minor): open.** P1 is not in decisions.jsonl. Its text is still accurate.
- **5 (minor): open.** P2 is not in the ledger. The same 9 records are affected (none in t1b081), but P2's draft
  ranges are now stale. With B's values: X0 77, X1 100, X2 86, X3 7, X4 3, X7 1 (filed 78/100/85/6/4/1); i1 a 552,
  ab 17, b 39 (filed 555/15/38); nonlang_only 12. The ranges to write are therefore X0 77-78, X2 85-86, X3 6-7,
  X4 3-4, i1 a 552-555, ab 15-17, b 38-39.
- **6 (minor): open.** For P3, the current file value is kappa 0.8939 [0.8589, 0.9268] at n = 882. The D0034 value
  0.853 (n = 715, t1b001-t1b076) is unaffected by t1b081.

## Gate checklist now

| # | Criterion | Status |
|---|---|---|
| 1 | One FA and one FB row per planned id | **partly**: 885 FA, 882 FB; 3 ids without valid FB (finding 14) |
| 2 | Isolation and model check of every session; failed sessions logged, rows unused | met |
| 3 | Quotes returned once; unaccepted to C | **partly** (finding 4, P1 pending) |
| 4 | Every disagreement/adjudicate row ruled once by C | met |
| 5 | Reproduce decisions and summary | met (finding 5, P2 pending) |
| 6 | Agreement | met |
| 7 | Re-check sha256, K, s5.2 | met (K = 4 of 82 screened sampled records; 18 not retrieved) |
| 8 | PRISMA T1 | **partly** (finding 15) |
| 9 | Other threats | findings 14-22 |
| scope | T1 closed | **open** (finding 2) |

## What remains to pass

- **Human author:**
  - (i) a decision row for M13184, M15873 and M17195 (item 5), then its execution;
  - (ii) decisions on the 348 rescue positives and the seed-corpus route (finding 2), or an explicit row that the gate
    is audited as "T1 screened so far (interim)";
  - (iii) rows P1, P2 (with the updated ranges above) and P3.
- **Orchestrator (minor):** findings 15-19, then regenerate.
- **Re-audit 2:** re-run `reaudit1/recompute.py` and `reaudit1/mcheck.py` on the updated files and check the new rows.
