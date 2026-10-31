# Text fixes F1-F6, F8 (skipped), F9 for the TNNLS manuscript (2026-10-31)

Task list: `PROFESSOR-REVIEW-TRIAGE-2026-10-31.md`, "Text fixes". F7 not done (the lead's). Nothing committed. The Acknowledgment and every AI
wording are untouched. The qualitative figure stays. Nothing under `exp_p2/`, `tools/`, `analysis/`, `runs/` was edited.

## Build and page counts
`bash paper2-tnnls/build.sh`: `main.pdf` 15 pages, `main_camera.pdf` 15 pages, `supplement.pdf` 22 pages. Zero undefined references or citations
(main, camera, supplement). No new overfull box (the one reported, 11.4 pt at supplement lines 296-297, S-VII, was there before). Fonts embedded; no
empty column regions. Before the edits both builds were full on page 15 (0 to 1.4 blank lines); the first edit pass gave 16 pages; after the cuts below
both builds end with about **4.4 blank lines** in the last column of page 15 (measured by pixel run, not by page count). The lead's one sentence fits;
three table rows will need a float to move, so check after adding them.

## What changed, file and line (line numbers as of this build)
| Fix | Where | Change |
|---|---|---|
| F5 | `sections/setting.tex:44-45` (III-B) | One sentence: the sum of one-pass conditionals is a factorised surrogate for the joint log-likelihood ratio; an exact ordered likelihood was not computed. No number. |
| F6 | `sections/setting.tex:89-91` (III-E) | After "no third-party timestamp exists": first push to "a code-hosting service" on 30 October 2026, after both studies; "its push log is the only third-party record, and it dates the push, not the commits" (added the last clause so the sentence does not contradict the one before it). No service name, no Zenodo DOI, same text in the review and author builds. Date source: triage fact 5 (13:55 UTC, lead-verified). There is no `runs/` file for it; flagged in the `% run:` comment. |
| F1 | `sections/study1.tex:214-221` (IV-C3) | "Post hoc, from the audit; descriptive." paragraph, 5 sentences, numbers below. Ends "This control does not separate a working pipeline from a defective one and is not read as validating it." No statement about P or its mechanism. |
| F1 | `supplement/supplement.tex:455-462` (note under Table S10, `stab:ps`) | Same facts in the table note, with the source keys. |
| F4 | `sections/study1.tex:248-255` (IV-C5, end) | Changed-code gate minus no gate, three values with intervals, "exploratory; intervals only", "exact flags raised accuracy under noise only", and the caveat that the labels mark codes the tokeniser changed, not evidence, so the figures do not transfer to a detector. Study 1 only; no LRF number anywhere near (LRF is in Section V; Table S12 is the supplement's equal-size-gates table, `stab:mech`). It is worded as a description of the oracle gate, not as an account of the P result (AB.1, A4.2.2 item 5). |
| F2 | `sections/study2.tex:267-275` (V-F) | "LRF adds no network row" replaced by an itemised count: unweighted sum = 2 caption-visible passes; LRF = those 2 + 8 complementary-mask passes (for B and the uncertainty of the B pass) + 1 observed-position pass = 2 + 9 = 11 against 2. D from the cached fixed-slot null; texture and codebook-neighbour features need no pass. One hedged sentence: the count follows K = 8, not the 1024 grid positions; another K or grid was not tried. Placeholder `% TODO-LEAD: CPU scorer time` at line 273 (the clause "in a time that was not measured" is to be replaced). |
| F2 | `supplement/supplement.tex:1212-1215` (note under the Study 2 cost table, `stab:cost2`) | Same count, same placeholder at line 1213; "adds no network row" removed. |
| F3 | `sections/study2.tex:320-322` (V-H, last sentence) | "Nothing here favours the additive form over a linear logit on the same features; the confirmed object is the frozen weighting, and the preregistered result remains the L1 test"; LRF was chosen by inner cross-validation among four learned families on the design items (points to V-A); learned shapes in S-IV are descriptive. No new number. |
| F9 | `sections/study1.tex:96-102` (IV-A) | Lemma 1, eqs. (8)-(10), its proof and the three consequences removed; replaced by the two-sentence statement (necessary condition phi1 > 2 phi0 - phi0^2, random gate lowers the ratio; added "and the sum has a positive mean" so the statement is exact). "Correlated tokens" paragraph (lines 104-109) shortened, same content. |
| F9 | `supplement/supplement.tex:691-728` (S-II, `sup:snrcorr`) | The lemma (`slem:meanvar`, now "Lemma S1"), eqs. `seq:mean`, `seq:var`, `seq:snr`, proof and the three consequences, moved unchanged. Every `M-eq:*` and `M-lem:meanvar` reference re-pointed to the local labels; the E-pred table note and the crosswalk row now say "Lemma S1". |
| F9 | `sections/setting.tex:82-84` | Table I (`tab:glance`) removed and replaced by a pointer: supplement S-I lists every family with its test, S-II gives the status of each Study 1 family, each study's Results give the outcomes. `tables/tab_families_glance.tex` and `scripts/tab_glance.py` are now unused (left in place). Study 2 statuses are not tabulated anywhere now except in Results and S-I's test table. |
| F9 | `sections/introduction.tex` (contribution 1) | Reworded: the condition is stated in IV-A; the closed form, proof and correlated extension are in S-II; "linked to no result" kept. |

## Numbers added, with source (each carries a `% run:` comment in the .tex)
| Number | Source |
|---|---|
| n_d = 4 (patch), 13 (swap) of 500; 0.008 and 0.026 | `runs/P2-A23-AUDIT/a23_ps_audit.json` `per_condition.{patch,swap}.share_items_gate_differs_from_none`; `runs/P2-GATE-M4/analysis.json` `ps.per_corruption.{patch,swap}.n_d` (4, 13) |
| gate vs none 2/2 p 1.0; 8/5 p 0.581 | already in the paper (`ps.per_corruption`); not repeated |
| 5 and 9 decisions changed by the corruption; b/c 5/0 p 0.0625 and 7/2 p 0.1797 (printed 0.18) | `a23_ps_audit.json` `per_condition.{patch,swap}.clean_vs_corrupt_none.{b,c,p}` (swap values verified: 7, 2, 0.1797) |
| changed-code arm 4/2 p 0.6875 (0.69); 7/4 p 0.5488 (0.55) | `a23_ps_audit.json` `per_condition.{patch,swap}.chg_vs_none.{b,c,p}` (swap verified) |
| 0.05 to 0.20 assumed discordance | `research/paper2/prereg/SAP-GATE-2026-10-28.md` AD.4 ("ASSUMED"); pointer comment, not a `runs/` file |
| Holm thresholds 0.025 and 0.05 | AD.4 (same file) |
| Oracle: -0.084 [-0.122, -0.046]; 0.070 [0.036, 0.104]; 0.004 [-0.010, 0.018]; n = 500 | `runs/P2-GATE-M4/analysis.json` `mechanism.{jpeg10,noise0.1,splice128}.y.changed_code_minus_none.{diff,lo,hi,n}` (all three re-read from the file) |
| 2, 8 + 1 = 9, 2 + 9 = 11 passes; K = 8; m = 1024 | `runs/P2-LRF-RESCORE/items.jsonl` `n_rows` (median 36 per item = 4 conditions x 9; min 36); `runs/P2-LRF-L1/config.json` `K` = 8; code read at `exp_p2/gate/pipeline.py` `caption_lambdas` (2 passes, "do not depend on any_codes"), `exp_p2/run_gate_m4.py` `process()` (gate_scores 8 passes + cached null; tbv 1 pass), `exp_p2/gate/config.py` `K = 8`, `GRID = 32` |

Two caveats on F2: (1) the measured 67 rows of the fold pass (for four conditions) are not decomposed here and the text does not claim they equal
11 x anything; the text only gives the per-image minimum from the code, confirmed by the re-scoring run's 36 rows per item. (2) The paragraph says the
count was not varied with K or grid; nothing stronger.

## F8: skipped
The VI-C Study 1 sentence ("the +-0.05 margin was reached with no discordant item under noise"; GATE-M and no gate decided identically on 500 items,
`runs/P2-GATE-M4/analysis.json` `mechanism.noise0.1.y.gate_minus_none` = 0.0, n = 500) is a sentence about the P discordance. It is barred by red-team
condition V2-1 (`REDTEAM-SPEC-2026-10-30.md` line 344: "No sentence anywhere states or interprets the P discordance outside Table I"), by SPEC v2.2
section 7 (the P discordance counts appear only as numbers in the table, never in a sentence), and by A5.9 must-not 1, and it would qualify the P
result, which AB.1 item 2 and A4.2.2 item 5 forbid outside the P table. The zero-width interval under noise is already visible in the existing P numbers
(0.000 [0.000, 0.000]) and in the existing sentence on zero-width percentile intervals. If the lead wants F8 anyway, it needs a dated ruling that
overrides V2-1.

## Notes for the lead
- Placeholders to fill: `sections/study2.tex:273` and `supplement/supplement.tex:1213` (`% TODO-LEAD: CPU scorer time`).
- The oracle gate's noise value (0.070, Study 1, IV-C5) and LRF's 0.069 (Study 2) are in different sections and never adjacent.
- Tracked PDFs (`main.pdf`, `main_camera.pdf`, `supplement/supplement.pdf`) and build logs were rebuilt; `docx/` was not touched, so the Word build needs the
  same changes carried over.
- Source files use CRLF; edits kept CRLF (scripts in the session scratchpad, not in the repo).
