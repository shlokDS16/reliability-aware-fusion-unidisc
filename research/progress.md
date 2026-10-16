# Progress ledger

## RESUME
- **HANDOFF 7 (2026-10-16 ~13:45 IST; newest, overrides older blocks).** Work happens in THIS worktree
  (exp-003-334706); the driving session runs in worktree crash-a57ec7, whose Edit/Write tools are blocked
  here by a hook, so files here are written by Bash/python (user approved).
  **User to-do:** `research/USER-ACTIONS-2026-10-16.md` (IEEE I3-I5; ScienceDirect 23 runs on
  `search-raw/sciencedirect/sd-download-links.html`; OpenReview 387 papers via `tools/fetch_openreview.py`
  with the user's own credentials in env vars - first test failed 'Invalid username or password', user is
  re-setting them in single quotes; 1,421 Springer records without abstracts (Springer Meta API key
  suggested); 9 near-miss arXiv matches; 102 e-gateway papers; routes+download of the 130 re-check/C8
  records; 15 percent human validation sample of T1 before seeing any screener row; HANDOFF 4 items).
  **Done today (after HANDOFF 6):** SpringerLink exported (5 CSVs, user downloads) and ingested (6,854 unique,
  177 queued); ScienceDirect: 8-connector limit, no wildcards, automatic plurals verified, 23 re-packed runs,
  automation blocked by bot protection (stopped); rescue pass 3 (687; 7 unclear) and dual TA batch-sub-02
  (4 pass) -> 1,004 TA passes. Adjudication route F (claude-fable-5-1) written as line 1 of
  analysis/screening/c-run-log.jsonl. Open-access full texts: 328 PDFs (fetch-log.jsonl); text via PyMuPDF
  (markitdown glued words; `tools/pdf_to_text.py`); OpenReview needs login (387 unmapped).
  **Full-text screening T1 (criteria v1.6, D0032), in progress:** harness `tools/ft_dispatch.py`
  (isolated folders), `tools/ft_isolation_check.py` (14 tests), `tools/ft_postbatch.py`; batches of 10 in
  `research/review/fulltext/t1-batches-part1.json` (t1b001-031) and `-part2.json` (t1b032-034); results in
  `analysis/screening/ft-t1/<batch>/` and `batch-log.jsonl`. Pilot: analysis/screening/ft-pilot01.
  Status at handoff: t1b001-t1b016 complete (149/160 agree; 23 ids to adjudication), t1b017 A done / B
  running, t1b018 A running. Per batch: Screener A = sonnet, B = opus, prompt = 'brief is section E of
  criteria-v1.6-screener.md in the dispatch folder; no /tmp; one-line reply'; after both: postbatch;
  a failed isolation check or API failure -> log 'discarded'/'failed' in batch-log and rerun in a fresh
  folder. Helper in the driving session's scratchpad: ft-dispatch/next.sh (build/postbatch) and
  agent-map.txt (batch -> agent ids). Cost about 0.4 percent of the weekly limit per batch (37 percent at
  t1b018); pause at 55 percent. **After all batches:** return non-accepted quotes once to their screener,
  then adjudicator C (Fable) on disagreements + 'adjudicate' rows (log every C session in c-run-log.jsonl),
  then the re-check sample/C8 records and OpenReview/e-gateway papers as further T1 batches, K test
  (criteria-v1.6.md s5), human validation.
- **HANDOFF 6 (2026-10-16 ~08:30 IST; newest, overrides older blocks).** Session resumed after the 04:48
  crash in this worktree (exp-003-334706); HANDOFF 5 was stale (v1.1 audit, criteria v1.2/v1.3, ACM DL,
  IEEE I1-2026 + I2 had all been done before the crash). **User-facing to-do list:
  `research/USER-ACTIONS-2026-10-16.md`** (IEEE I3-I5 'file limit exceeded'; SpringerLink; ScienceDirect;
  adjudicator route F/H; full-text download batches; title resolution API limits; HANDOFF 4 items).
  **Done this session:** D0032 = full-text criteria v1.6 adopted (red-team audits v1.3-v1.6 in
  `review/audits/`; protocol s10 amendment); D0033 = title-resolution design rule (check sample must be
  complete). Ingest now reads ACM in-page JSONL (`tools/ingest_subscription.py`): Scopus + WoS + IEEE
  (I1, I2) + ACM -> 4,606 unique, 174 queued, 1,808 string failures. Rescue pass (Haiku, D0029 design,
  `screening/v2/rescue-subscription/`): 10 include + 62 unclear. Dual screening (A Sonnet, B Opus) of 246
  (`screening/v2/dual-subscription/`): kappa 0.930 [0.861, 0.985]; D0030 -> 46 pass. Total title/abstract
  passes 1,000. Full-text access routes (`review/fulltext/ft-routes.jsonl`): 774 open access, 102
  e-gateway, 27 duplicates, 97 no full text (32 near-miss candidates for a human check).
  **Blocked:** title-resolution rerun stalled at 100/393 slow lookups (API limits), stopped; rerun
  `python tools/resolve_title_only.py run --s2-patient=90` after 05:30 IST or with an S2 key.
  **Next:** with the user: IEEE I3-I5, SpringerLink, ScienceDirect (then rerun ingest, rescue, dual screen
  the delta); adjudicator route; download batch 1 (open access) then batch 2 (e-gateway); then full-text
  screening per criteria v1.6 (dispatch rules in criteria-v1.6-screener.md: isolated folders, session
  rules, c-run-log.jsonl first line = route). Writes into this worktree from the crash-a57ec7 session are
  blocked for Edit/Write tools by a worktree hook; the user approved writing here (done via Bash).
- **HANDOFF 5 (2026-10-16 ~00:15 IST; newest, overrides older blocks; session in progress).**
  Date correction: Scopus ran 2026-10-15 ~22:20 IST (file times), not 10-16; the `-20261016` file names
  stay (hashed). Search date for all subscription databases = 2026-10-15.
  **Web of Science DONE:** Q1 599, Q2 376, Q3 105, Q4 1,012, Q5 543, union #6 2,267 exported (3 RIS,
  Full Record, user approved); `search-raw/web-of-science/wos-queries-20261015.md` (strings, hashes).
  **IEEE Xplore:** the sheet's 6-term limit was wrong (78 and 93 field terms accepted); 5 merged
  queries I1 1,203 / I2 101 / I3 245 / I4 41 / I5 12 (`search-raw/ieee-xplore/ieee-queries-20261015.md`,
  generator `ieee_queries_20261015.py`). CSV cap 1,000 -> I1 split by year: 2021-24 (230) and 2025
  (506) on disk; 2026, I2-I5 still to download (user downloads by hand from `ieee-download-links.html`,
  because Chrome stopped saving automated downloads). User approved IEEE downloads.
  **ACM DL:** queries Q1-Q5 built (per-concept Title/Abstract/Keyword groups, `search-raw/acm-dl/
  acm_queries_20261015.py`, hashes checked), NOT run: loading the long doSearch URL made the Claude in
  Chrome safety check block every call for ~20 min (fixed by restarting the extension). Retry with the
  advanced-search form or shorter queries. SpringerLink, ScienceDirect: not started.
  **Ingest:** `tools/ingest_subscription.py` (rerun: `python tools/ingest_subscription.py`), report
  `corpus/subscription-ingest-report-2026-10-15.md`: Scopus+WoS+IEEE slice -> 3,895 unique, 170 queued
  (`screening/v2/subscription-queue.jsonl`); 1,222 new string failures still need the D0029-style
  rescue pass; front-matter volumes excluded.
  **Title resolution (D0029-2) NOT complete:** 1,161/2,107 classified, 946 lookup-incomplete (S2/arXiv
  rate limits, OpenAlex quota until ~05:30 IST); queue empty because untested
  (`corpus/title-resolution-report-2026-10-16.md`). The previous session (Resume DLM Discovery
  EXP-003) edited `tools/resolve_title_only.py` at 23:50 to look up only reference-marker records plus a
  random check of 60 others, unrecorded, and left `nohup python tools/resolve_title_only.py run`
  (PID 37132) running; its outputs will overwrite the lit-scout outputs. Decide between the two designs
  from its random-check result, then record a decision.
  **Criteria v1.1** drafted (`screening/criteria-v1.1.md`, 14 rules, new X0, D0032 row proposed;
  recommends option b: 19 both-excluded records get a pre-declared full-text check). Red-team audit
  running -> `review/audits/2026-10-16-redteam-criteria-v1.1.md`; D0032 not yet recorded.
  Note: the `dlm-expert` agent type is not registered in sessions started outside this worktree; run
  it as general-purpose with `.claude/agents/dlm-expert.md`.
- **HANDOFF 4 (2026-10-16 early; overrides older blocks).**
  Read memory `dlm-tool-access-requests` and the KB `research/expert/dlm-expert-kb.md` (+ three
  `web-digest-*.md`). New core agent `dlm-expert` (tools/build_agents.py) is the default worker;
  auditors unchanged; max 3 agents at once (was breached twice; keep to it).
  **Done since HANDOFF 3:** EXP-003 done + audited (D0022-D0025; result in H0007-H0009); census v2
  (D0020-D0021); manuscript 35 pp + 8 pp supplement, abstract 100 words, citations validated;
  free-source searches + string revisions (D0026-D0028: S1''/S2''); screening of 1,953 records by
  A (Sonnet) and B (Opus): kappa 0.911 [0.892, 0.929] (`analysis/screening/agreement-v2.log`),
  rule D0030 = pass if either passes -> 954 pass; validation of the automation filter (D0029,
  reversal triggered) -> Haiku rescue pass over 4,421 exclusions done (15+ includes, ~300 unclear;
  sensitivity 2/2 on V1); `screening-ambiguities.md` lists every class to settle in criteria v1.1
  before full text. **User decisions 2026-10-16:** full-text screen ALL records, extract RQ data on
  a stratified sample + all multimodal; e-gateway first.
  **In progress:** (1) title resolution of 2,107 title-only snowball records (lit-scout running ->
  `research/review/screening/v2/title-resolved-queue.jsonl`, `corpus/title-resolution-2026-10-15.json`);
  (2) Scopus via the user's Chrome (Claude in Chrome; VIT access works there, the built-in browser
  lacks the user's access extension): five queries run (`research/sources/search-raw/scopus/
  scopus-queries-20261016.md`, counts 876/530/134/1,670/836); EXPORT needs the user to sign in to a
  personal Scopus account; user approved the five CSV downloads. Then Web of Science, IEEE, ACM DL,
  SpringerLink, ScienceDirect the same way (combined NOT-free query + NOT parts separately; record
  counts; ask download approval per database).
  **Update 2026-10-16 ~03:00 IST: Scopus DONE.** User signed in to a personal Scopus account in
  Chrome; five CSV exports (4,046 rows, all with abstracts) in `research/sources/search-raw/scopus/`
  (hashes in `scopus-queries-20261016.md`; D0031). Export dialog recipe: select all, Export > CSV,
  tick Bibliographical information + Abstract & keywords, turn OFF "Truncate to optimize for Excel",
  do not tick "Save as preference"; files land in C:\Users\Shlok\Downloads as scopus_export_*.csv.
  **Remaining databases (in the user's Chrome, Claude in Chrome tools):** Web of Science (TS=,
  export cap 1,000 per file: split by PY), IEEE Xplore, ACM DL, SpringerLink, ScienceDirect; same
  plan (combined NOT-free union query + NOT parts separately, counts first, then ask download
  approval per database). The title-resolution lit-scout agent was still running at handoff: check
  for `research/review/screening/v2/title-resolved-queue.jsonl` and
  `research/review/corpus/title-resolution-2026-10-15.json`; if absent, rerun it (brief in D0029 item 2).
  **Next after searches:** lit-scout ingest + dedup of exports; dual-screen new database records;
  criteria v1.1 from the ambiguities; full-text screening of all passing records (two screeners on
  key sections); extraction on the sample; section 05 RQ evidence; PRISMA counts final; red-team
  referee pass. **Still needs the user:** human screening sample (218) + 120 disagreements (RAISE
  validation); professor's name/school/e-mail, ORCIDs; OSF registration (retrospective) of the
  protocol; protocol freeze.
- **STATE 2026-10-15 ~17:30 IST (newest; overrides older blocks).** Order of work confirmed by the
  user: Paper 1 (review, ACM CSUR) first, Paper 2 (research article) second; keep the framework
  (D0011) as the spine. **EXP-003 done and audited** (gate PASS WITH CORRECTIONS): E3-H1 positive,
  Delta1 = 0.126 [0.076, 0.177] (not confirmed by CLIP; may include quality-mediated coupling);
  E3-H2a not detected (W2); E3-H2b positive 0.077 [0.024, 0.131]; ledger H0007-H0009, X0003,
  D0022-D0025; results committed on branch claude/dlm-discovery-resume-ca3357 (077fb1d, b007f05).
  **Manuscript** `paper/review/`: all sections drafted except 05 (RQ evidence, needs full-text
  extraction), main 35 pp (CSUR limit incl. references) + supplement 8 pp; clarity edit done;
  citations validated (96 entries). **Running:** lit-scout on the free databases (OpenReview, ACL
  Anthology, Semantic Scholar, OpenAlex, DBLP, snowballing) -> `review/corpus/new-records-2026-10-15.jsonl`
  and `subscription-search-sheet.md`. **Needs the user:** subscription databases (Scopus, WoS, IEEE,
  ACM DL, Springer, ScienceDirect) through the VIT e-gateway in the built-in browser (user logs in;
  Claude runs searches and exports with per-download consent); human screening sample (218) and
  120 disagreements; professor's details; protocol freeze decision. **Then:** screen new records,
  full-text screening and extraction for RQ1-RQ6 (section 05), PRISMA counts final, red-team
  referee pass, release package.
- **HANDOFF 3 (2026-10-15, about 08:45 IST; newest block, overrides all older). Start here.**
  **Two worktrees.** The EXP-003 driver runs in `.claude/worktrees/dlm-discovery-resume-ca3357`
  (its `runs/EXP-003/` is untracked and only there). All other work now happens in
  `.claude/worktrees/resume-dlm-discovery-exp-003-334706` (branch fast-forwarded to the ca3357 tip
  6573351; the harness blocks writes into another worktree). Check the driver at
  `<ca3357>/runs/EXP-003/driver.log`; when DONE.txt exists, run the frozen analysis there.
  **Done this session:** no restart since HANDOFF 2 (boot 04:32; no events 41, 1001, 6008, 1074
  after 08:00); driver PID 37236 alive in M1. D0018: engineer's interpretation calls accepted,
  card 1.2 erratum appended (unconditional branch masks all observed positions, verified in code),
  firewall disclosure recorded. **User decision 2026-10-15:** run everything now despite weekly
  88 percent (user will upgrade the plan if the limit is hit); save work often.
  **Running (agents write as they go):** novelty-auditor on EXP-003 ->
  `review/audits/2026-10-15-novelty-EXP-003.md`; census coder B (Claude Opus) ranks 92-128 ->
  `review/census/coder-B-claude-r092-r128.jsonl`; coder A (Claude Sonnet, blind) ranks 1-40 ->
  `coder-A-claude-r001-r040.jsonl`. Brief for all coders: `review/census/CLAUDE-CODER-BRIEF.md`.
  **Remaining batches:** B 129-165, 166-202 (stop when B's eligible count, Codex ranks 1-91 plus
  Claude, reaches 150; Codex had 66 eligible); A 41-80, 81-120, 121-160, 161-202 (A codes every rank
  B coded). Then agreement (before reconciliation, raw disagreements kept), adjudication,
  census-result-v2. Then EXP-003 analysis and gate-auditor, then manuscript.
  **Update 2026-10-15 ~10:00 IST.** Novelty audit done (D0019: incremental 0.65; wording limits).
  Census coding complete: sample = ranks 1-176; coder B (Codex 1-91, Claude Opus 92-176 plus
  19, 79) 151 eligible; coder A (Sonnet, blind) all 176 ranks. Agreement before reconciliation in
  `analysis/census/agreement-random.log` (script `agreement_random.py`), 158 field disagreements in
  `review/census/disagreements-random.csv`; ambiguities in `review/census/coder-ambiguities-2026-10-15.md`.
  **Running:** adjudicator (Opus) writing `review/coverage/census-codebook-v1.2.md` (rules only).
  **Next:** two adjudicators apply v1.2 to the disagreements (ranks 1-88, 89-176) ->
  `review/census/census-random-final.jsonl` + notes; census-result-v2; then EXP-003 analysis when
  DONE.txt exists; then manuscript. Datasets deleted by the user (C: 203 GB free).
  **Update 2026-10-15 ~10:35 IST.** Census adjudicated (v1.2, two adjudicators + harmoniser;
  D0020; protocol section 10 amended) -> `review/census/census-random-final.jsonl`; result
  `review/coverage/census-result-v2.md` (146/152 headlines non-plain or unstated; summary log
  `analysis/census/summary-random.log`). Codex coder B failed to read 15 papers in ranks 1-88
  (adjudicated from the paper; agreement also reported without them). **Running:** gate-auditor on
  census-result-v2 -> `review/audits/2026-10-15-gate-census-v2.md`; manuscript-writer: outline,
  acmart skeleton, Introduction, Review method, census section in `paper/review/`.
  **Next:** apply audit corrections; EXP-003 frozen analysis + gate-auditor when DONE.txt exists;
  manuscript sections design space, error budget, open problems; then research-humanizer.
  **Update 2026-10-15 ~10:50 IST.** Census v2 corrected after gate audit (D0021): 147/153 =
  0.961 [0.917, 0.982]. Manuscript started (`paper/review/`, commit 7c71535): OUTLINE.md, acmsmall
  skeleton, Introduction, Review method, census section drafted (18 pp; ~2.8 pp over budget);
  stubs: notation, design space, RQ evidence, error budget, open problems, EXP-003, limitations,
  conclusion. **PRISMA blockers found by the writer (need the user and professor):** (a) only two
  arXiv searches run; the protocol's other databases and snowballing not run; (b) logged S1 query
  differs from the protocol string; recall vs seed list 421/540 = 78 percent, no pilot record;
  (c) human validation (218 sample) and the 120 screening disagreements still undone; (d) no
  full-text screening of the 1123 passed records (only the 176-record census sample read);
  (e) protocol never frozen (still DRAFT); (f) PLAN.md and D0011 still cite the old meta-analysis
  title and 47-model counts; (g) professor's name, school, e-mail, ORCIDs, and exact model IDs of
  screener A and the Claude coders not recorded. Weekly usage 98 percent at 10:50.
  **Update 2026-10-15 ~12:00 IST (after weekly reset; user upgraded plan).** D0022: EXP-003 hard
  stop raised to 8.5 GPU-h with the user's yes (cost overrun ~1.4x; watcher kills the driver at
  8.5 h; `runs/EXP-003/ACK_STOP_BUDGET.txt`). Manuscript now 33 pp, sections 01-04, 06-08 drafted,
  figures 1-4 from scripts (`paper/review/scripts/`), Table 4 codes verified, citations validated
  (`review/audits/2026-10-15-citations-paper1.md`; support fixes applied; anonymous OpenReview
  source kept once, flagged). **Next:** when DONE.txt exists (expected ~15:00): frozen analysis in
  the ca3357 worktree, gate-auditor, ledger + section 09 under card rules W0-W5 and D0019 wording
  limits; then limitations, conclusion, abstract; clarity edit (research-humanizer); cut to budget
  (candidate: Table 4 to the supplement, Fig. 3 duplicates it).
  **User side task (done):** delete datasets for storage (Paper 3 `data/raw` 187.9 GB, ML paper `data`
  0.3 GB, Dam `periyar_ccd_rnn/data` 0.14 GB); commands given in chat; Claude does not hard-delete.
- **HANDOFF 2 (2026-10-15, 08:10 IST).**
  Overnight: the EXP-003 driver finished the pilot (no stop rule; n_generate 138, 120 eligible,
  share 0.875) and the controls generation and scoring, then stopped at 03:16 on a **code bug**
  (UTF-8 files read with the Windows code page; KeyError on a non-ASCII noun). The laptop
  restart at 04:29-04:32 was **Windows Update** (System log 1074, MoUsoCoreWorker and
  TrustedInstaller), not a GPU crash, and interrupted nothing. Fixed (explicit UTF-8 in
  tables.py, frozen_analysis.py, score.py, chunks.py; pilot_analysis.py left as run under its
  frozen hash). Controls (D0017): NC-1 pass (-0.0003), PC-2 pass (guided T2I matched 0.77 vs
  cross 0.17), **PC-1 fail** (TF - Ind = 0.031, p 0.40): under plain sampling even an image
  generated after the whole completion shows no detectable noun-level dependence on it, so every
  EXP-003 null is "not measurable with this instrument" (W2), while a positive G - P64 stays
  readable. Main stage restarted 08:06: driver PID 37236 (`runs/EXP-003/DRIVER_PID.txt`),
  M1 (P64 and G) -> M2 (O0) -> M3 (P32) -> scoring -> DONE.txt.
  **If the laptop restarts again:** check `runs/EXP-003/driver.log` tail and STOPPED.txt; restart
  with the `Start-Process` command in `runs/EXP-003/IMPLEMENTATION.md` section 4 (every unit is
  resumable; the GPU clock persists in clock.json). Ask Shlok to pause Windows Update while runs
  are going (Settings > Windows Update > Pause updates).
  Everything in HANDOFF (below) still applies.
- **HANDOFF (2026-10-15, about 01:50 IST).**
  **Running now, unattended:** EXP-003 driver, PID 54920 (`runs/EXP-003/DRIVER_PID.txt`, log
  `runs/EXP-003/driver.log`). Card `research/preregistration/EXP-003-value-rule-consistency.md`
  v0.3.2 SIGNED (statistician and red-team; ledger H0004-H0006, X0002). Implementation and how to
  check, stop or resume after a reboot: `runs/EXP-003/IMPLEMENTATION.md` (sections 4, 5; restart
  with the PowerShell `Start-Process` form, not `run_all.bat`). The driver runs pilot -> firewalled
  pilot analysis with the n rule and stop rules 9.1-9.3, 9.6 by script -> controls (NC-1 stop) ->
  M1-M3 -> analysis freeze -> scoring. It writes `runs/EXP-003/STOPPED.txt` (exit 3) if a stop
  rule fires, `DONE.txt` when finished.
  **First actions next session:** (1) `tasklist /FI "PID eq 54920"`; tail `driver.log`; if
  STOPPED.txt exists, read it: the likely trigger is stop rule 9.1 (scoring costs more than the
  card's 10.6 s per prefix: cross-prefix queries, placebo nouns for four arms and CLIP). The
  engineer's suggested remedy, scoring placebo for P64 and G only, needs a dated card amendment
  before any change. (2) Review and record the engineer's interpretation calls (IMPLEMENTATION.md
  section 5: noun-key -es rule, PC-2 derangement seed 5303, placebo pool smaller than |D|, the
  "such samples" definition in 9.2, the constant 1.21 in the n rule) and the factual correction
  that UniDisc's unconditional branch masks every observed position (system prompt, markers,
  prefix), not only the prefix (card 1.2 says prefix only). (3) Firewall disclosure to record: the
  engineer's smoke tests used pilot prefixes 0-1 in the scratchpad and printed a 2-prefix Delta1
  class; nothing entered `runs/`; pilot data never enter tests. (4) After DONE.txt:
  `python analysis/EXP-003/frozen_analysis.py main`, then gate-auditor check of the numbers.
  (5) Not implemented: tail-entropy hook, G-low/M4, CLIP lift bootstrap (embeddings stored).
  **State of the science.** EXP-001 stopped at PG-V (D0016): under plain T = 1 sampling UniDisc's
  joint completions show no completion-specific image link (textures). EXP-002 demoted (D0013).
  MDLM reproduced (G4, -0.50%). Framework v2 (`review/framework-v2.md`, D0011): E_sel/E_tilt
  withdrawn; contributions = design space (47 models), value-rule census (37 of 45 headlines
  non-plain or unstated; `review/coverage/census-result-v1.md`), budget as taxonomy, open
  problems. Screening done (1453 records, kappa 0.728); random-sample census: Codex coded 86 (66
  eligible) before its limit (until 2026-11-10, D0015).
  **After the 2026-10-19 17:00 UTC reset:** census coder B (Claude Opus) for the rest of the
  150-eligible sample, coder A (Claude Sonnet) blind on all, agreement, adjudication; novelty audit
  of EXP-003 before any claim; then manuscript drafting. **Human tasks for Shlok:** 218-record
  screening sample (`review/screening/HUMAN-SCREENING-INSTRUCTIONS.md`), 120 disagreements
  (`review/screening/disagreements.csv`).
  **Safety and process rules now in force:** every GPU job through `tools/gpu_guard.py`
  (two HYPERVISOR_ERROR crashes on 2026-10-14); Codex tools resume one read-only thread per 20
  calls; downloads have no size limit; hand off at about 850k context. Budget: weekly 86 percent.
- **Superseded (2026-10-15, early).**
  EXP-001 v0.5 was signed, implemented (130 tests pass; `exp001/`, `analysis/EXP-001/`,
  `runs/EXP-001/IMPLEMENTATION.md`) and STOPPED at its construct gate PG-V under preregistered
  rule 11.1 (D0016): under plain sampling at T = 1 UniDisc's joint completions show no
  completion-specific image link (rung 2 m - s 0.151 < 0.25; m - s_sp about 0; images are
  textures); checker valid (PC-F). One protocol deviation recorded (prefix layout space fix
  between rung-1 runs). Images are unlicensed and kept local (`runs/EXP-001/image-hashes.txt`).
  G4 done: MDLM reproduced (22.935 vs 23.05, -0.50%; `runs/G4-mdlm-repro-2026-10-14/report.md`);
  the bf16 gap was dropout (train mode).
  **EXP-003** (new, preregistration draft `research/preregistration/EXP-003-value-rule-consistency.md`):
  plain vs official guided sampler vs CFG-0 on fresh prefixes; primary discordant-noun link
  Lambda_d; about 6 wall-clock GPU-hours. Running: statistician and red-team reviews (sonnet).
  Codex exhausted until 2026-11-10 (D0015): census coding by Claude coders after the 2026-10-19
  reset; Codex tools fixed to resume one read-only thread per 20 calls.
  **Budget: weekly 86 percent on 2026-10-15** (resets 2026-10-19 17:00 UTC). Before reset: only
  EXP-003 review, sign-off and the guarded run. After reset: census coders A and B, novelty audit
  of EXP-003, then manuscript drafting. Human tasks pending: 218-record screening sample, 120
  screening disagreements.
- **Superseded (2026-10-14, night).**
  Laptop crashed twice under sustained GPU load (bugcheck 0x20001; memory `laptop-gpu-crashes`);
  user chose guarded runs: every GPU job through `tools/gpu_guard.py` (15-min chunks, 85 C stop,
  telemetry), checkpointed, duty cycle about 50 percent, batch <= 8. Python child processes exit
  0xC0000409 at teardown after finishing (results written); watch it.
  D0013: EXP-002 demoted (coupling negligible at N = 1024; red-team check reproduced). EXP-001 is
  the single preregistered experiment: card v0.4 "draft for signature" (commit 7bce081), task =
  prefix-conditioned joint completion (D0014), core path about 27.3 wall-clock GPU-hours.
  Novelty: per-step cross-modal measurement novel (audit 0.60 plus full-text check of VRCD,
  VIG-Sampler, PUNT: not reported); dependence-aware schedule incremental (DAPD 2603.12996).
  **Running:** statistician round 4 and red-team round 3 (signature checks); repro-engineer G4
  (MDLM, guarded; gates EXP-002's optional check only); Codex census coder B (86+ coded);
  LLaDA download (4 connections).
  **Next:** signatures -> ledger rows (hypotheses H-A, H-B, H-C; experiment EXP-001) -> lab-engineer
  implements EXP-001 (samplers with custom commit plans, S_theta estimator, gates PG-1, PG-2,
  PG-V) -> gates -> pilot -> core path. Budget: weekly 76 percent at 2026-10-14 night; Claude
  census coder A and manuscript drafting wait for the 2026-10-19 reset.
- **Superseded (2026-10-14, evening).**
  User: no download size limit; continue in this session to about 850k context (D0012).
  **Experiments (the significant result):** EXP-001 (cross-modal dependence on UniDisc) and EXP-002
  (sample-then-filter decomposed into sharpening and coupling at k >= 2; new: 2605.12522 and
  2609.34509 are k = 1 only, `review/dossier/prior-art-2605.12522-experiments.md`) are drafted in
  `research/preregistration/`; statistician: "sign with 12 required changes" each
  (`review-statistician-2026-10-14.md`). Toy prior `analysis/framework/check_coupling_k2.py`.
  Lab engineer (running) is setting up UniDisc and MDLM: `runs/env-2026-10-14/` (MDLM 21 ms per
  pass at L = 1024; UniDisc OOM issues, layout may be 1024 px). **Next:** apply statistician
  changes plus setup facts as card v0.2, red-team sign-off, pilots.
  **Census (Paper 1 contribution 2):** 47-model census reconciled (`review/coverage/census-
  result-v1.md`: 37 of 45 headlines use a non-plain value rule or do not state one; 12 report
  entropy; 10 of 37 sweeps state the rule fixed; blind kappa before reconciliation in
  `analysis/census/agreement.log`). Codebook v1.1 for the corpus. **Screening done:** 1453 records
  (`review/screening/`), A (Claude) vs B (Codex) pass/exclude kappa 0.728, 1123 pass both, 120
  disagreements for the human (`disagreements.csv`); human validation sample of 218 waiting for the
  user (`HUMAN-SCREENING-INSTRUCTIONS.md`). **Random-sample census:** order seed 20261015 over 1106
  records (`review/census/census-order.csv`), texts in main checkout `research/sources/
  census-text/`; Codex coder B running to 150 eligible (`review/census/coder-B.jsonl`); then a
  Claude coder A on the same ranks, blind; then agreement and adjudication.
- **Superseded (2026-10-14, end of build session).**
  Handoff because controller context passed 250k. Read `review/framework-v2.md` first (sections A
  and D), then decision D0011.
  **Outcome of the build:** the selection term failed. Red-team (`review/audits/2026-10-14-red-
  team-selection-term.md`, 2 fatal, 11 major, 10 minor; scripts reproduce) and the full-text
  prior-art check (`review/dossier/prior-art-selection.md`: 2605.12522 has the k = 1 commit law,
  majorisation and the sample-select-resample fix in code; Hayakawa et al. 2510.04525; 2609.34509;
  Beirami et al. 2401.01879) mean E_sel and E_tilt are withdrawn as new terms (D0011). framework-v2
  uses one signed value slot V; P2 withdrawn; P1 narrowed to k = 1; P5 restated in a named split
  S_theta with a mixture-reference estimator, checked by enumeration
  (`analysis/framework/check_crossmodal_mixture.py`, 0 failures). Paper 1's contribution is now:
  (1) design space tested on 47 models, (2) value-rule and reporting census (29 of 40 headlines use
  a non-plain value rule; 5 report entropy; 1 of 14 guided models sweeps steps with guidance fixed),
  (3) budget as taxonomy with credited identity, (4) open problems with the evidence each needs.
  Codex round 4 (`research/debates/2026-10-14-framework-v1/round-04-codex.md`): ACCEPT D3 and D4;
  NEEDS-EVIDENCE D1, D2, D5; census needs independent coding with agreement before reconciliation;
  the one addition that would move the review to acceptance is a controlled frozen-checkpoint
  four-arm value-rule result, unless 2605.12522 already has it.
  **Next, in order (fresh session; weekly budget 64 percent, reset 2026-10-19 17:00 UTC):**
  (1) paper-reader, short: do 2605.12522's experiments cover the four-arm comparison (SF,
  resampled twin, confidence-ranked RS, tilted twin) at matched passes with an entropy-matched
  frontier? This decides Paper 2 and D4. (2) Write the census fields and operational definitions
  into `review/protocol.md` section 6 (value rule classes, entropy reported, sweep with value rule
  fixed, guidance fixed), with statistician sign-off on the agreement plan. (3) Screening plan for
  the 883 new arXiv records (`review/corpus/arxiv-S1-*.jsonl`, `arxiv-S2-*.jsonl`). (4) Ask the user
  about downloads above 5 GB (UniDisc 5.63 GB for P5; LLaDA-8B 16 GB) once Paper 2's first
  experiment is chosen. (5) Tie correction to the k = 1 law in `method/selection-term.md` T2(a)
  (prior-art-selection.md concern 3). (6) Human authors read framework-v2.
  Dispatch record this session: paper-reader x4 (sonnet; primers, design space, prior art; all
  useful), method-architect (opus; useful, then refuted in part), red-team (opus; decisive),
  novelty-auditor (opus; useful but missed Hayakawa and was wrong on N4 at k = 1; E1 only),
  Codex rounds 2 and 4.
- **Superseded (2026-10-14, build session).**
  User said "start the build" with the recommended plan, despite FRUGAL budget (weekly 63 percent).
  Done and committed: `review/framework-v1.md` (25 primer edits applied, v0 kept);
  `review/coverage/design-space-v1.md` + `.csv` (47 models, 36 fit, 11 partly, 0 no; misfits:
  length-changing edit channels, stochastic memory, graded evidence, joint-over-set predictors,
  sequence-level selection; census: 29 of 40 headlines use a value tilt or selection, 5 of those
  report entropy); `review/method/selection-term.md` with `analysis/framework/check_selection.py`
  (61 exact checks pass on rerun). Key results: E_sel is defined only against a reference; the
  canonical one is matched rank-then-sample (same position law, values resampled), runnable as
  sample-select-resample; per-step forward E_sel is infinite for sample-then-filter; temperature,
  top-p, argmax and CFG are state-only tilts (E_tilt, inside the identity), so only 4 of the 29
  census headlines use true E_sel (sample-then-filter) [recount needed]; **P2's premise is false**
  (E_fact alone can push entropy far below H(q)); toy U-shape in steps under SF. arXiv S1+S2
  retrieved: 1303 unique, recall 78 percent, 883 new candidates (not yet screened). Codex debate
  `research/debates/2026-10-14-framework-v1` round 2: P1 not identified as stated, E_sel may be
  decomposition-dependent, framework risks reading as identity plus labels without one validated
  new prediction. `tools/debate.py` fixed (relative path bug).
  **Running at this point:** red-team (opus) on selection-term + framework-v1 + Codex objections,
  report `review/audits/2026-10-14-red-team-selection-term.md`; novelty-auditor (opus) on N1-N8,
  report `review/audits/2026-10-14-novelty-selection-term.md`.
  **Next:** read both audits; write `review/framework-v2.md` applying the 15 method edits as
  amended by the audits; Codex round 3 with the content pasted into the debate folder; recount
  the census with the tilt/selection split; screening plan for the 883 new records.
- **Earlier state (2026-10-14, late session).**
  User: two-week horizon for Paper 1 (about 2026-10-28), quality first, the review must carry a
  significant result (D0010). Budget was FRUGAL (weekly 58 percent at about 22 percent elapsed;
  resets 2026-10-19 17:00 UTC), so the user chose sequential primer agents only this session.
  **Done this session (step 1 and 2 of the plan):**
  - `review/dossier/primer-gaussian.md` (paper-reader, sonnet, 364k tokens; useful). Six papers
    read (Diffusion-LM, CDCD, Plaid, DFM, Duo, BD3-LM; SSD-LM method only; TESS, CANDI, Simplex
    Relaxation not read). Corollary 3 (step size as parallelism) not stated in any of them; toy
    per-step TC ~ step^2.16. Gaussian samplers add a final-rounding factorisation term
    TC(x given z_0); self-conditioning breaks "policy depends on z_n only"; "implicit revision"
    is qualified (pinned conditioning, freezing below an identifiability noise level); Duo's
    duality is per-position per-time only, not trajectories. 14 numbered edits in section 5.
    Two proof steps flagged as possibly unjustified (BD3-LM App. B.5; Duo Thm 3.2 setup), low
    confidence because of conversion: check against the PDFs.
  - `review/dossier/primer-multimodal.md` (paper-reader, sonnet, 374k tokens; useful). Show-o,
    UniDisc, MMaDA, MMaDA-Parallel, FUDOKI, Lumina-DiMOO, Transfusion, BAGEL, Show-o2, LaViDa-O
    at sections-read level (E2-); Muddit, LaViDa, Dynin-Omni not read. **P5: no paper measures a
    cross-modal quantity per step.** Premise has weak indirect support (UniDisc App. I CFG
    Fig. 24-25; LaViDa-O Table 13). The only joint-vs-sequential contrast (MMaDA-Parallel
    Tables 3, 10) favours joint but is confounded. E3: the released MMaDA-Parallel-A sampler
    commits no image tokens in the first quarter of steps (parallel_generator.py lines 156-160,
    219-220), unlike the paper's text. Toy [V]: E_fact = within-text + within-image + cross-modal
    CMI (error 6.6e-16), so P5 as worded is near an identity; split into P5a/P5b (D0010).
    "No new machinery" fails in four places (guidance, per-modality weights and schedules,
    continuous image channels, output-level revision). 11 numbered edits in section 6.
    Cheapest P5 test: frozen UniDisc 1.4B interleaved checkpoint, **5.63 GB download, which
    needs the user's yes (above 5 GB)**, licence not stated (E1), about 8 GPU-hours, not run.
  - arXiv count retry worked (S1 1158, S2 173, S1n 731 hits); `run` not yet executed.
  **Next, in order (fresh session):** (1) write `review/framework-v1.md` (v0 stays) applying the
  25 edits from both primers, with P5a/P5b and rewritten P1-P3; (2) method-architect (opus)
  formalises E_sel (law of committed values under keep-the-most-confident-sample selection,
  and CFG as an E_sel analogue) and the multimodal E_fact^X term; red-team (opus) attacks both;
  (3) 40-model design-space table and coverage test; (4) `python tools/search_arxiv.py run S1 S2`;
  (5) ask the user about the UniDisc download for the P5 pilot (Paper 2 candidate); (6) humans
  read framework-v1. Weekly budget should be checked first; heavy steps after the reset.
- **Earlier state (2026-10-14, end of day).**
  User decision: the target stays ACM Computing Surveys (D0009). Paper 1 is being rebuilt on an
  integrating framework: `review/framework-v0.md` (generation as a commitment process, five design
  choices C1 to C5, an error budget of factorisation, learning, selection and stale-computation
  terms, and a taxonomy of methods by the term they change). It has been checked once against
  sources: `review/dossier/competitor-anatomy.md` (organisation absent from both surveys),
  `review/dossier/primer-foundations.md` (three unification claims correct with restrictions),
  `review/dossier/primer-samplers.md` (the two-term identity is already published: ARDM
  2110.02037 and the entropy-bounded sampler 2505.24857; selection and stale-computation terms and
  the taxonomy not found), plus an exact-enumeration check in `analysis/framework/`.
  **Next, in order:** (1) primer chapters still missing: the Gaussian and embedding diffusion
  family; unified multimodal models (Show-o, UniDisc, MMaDA, MMaDA-Parallel, FUDOKI, Lumina-DiMOO
  and the hybrid autoregressive-plus-diffusion models), with a check of proposition P5;
  (2) rewrite P1 to P3 from the primers and have method-architect formalise the selection term
  (what is the law of committed values under keep-the-most-confident-sample selection) and
  red-team attack the derivations; (3) coverage test: place every corpus record on C1 to C5 and on
  the lever table, starting with a design-space table of about 40 major models; records that fit
  nowhere show where the framework is incomplete; (4) retry the arXiv searches; (5) the humans
  read `framework-v0.md`. The claim-evaluability rubric and hypotheses E1 to E3 stay suspended;
  quality appraisal will be a descriptive component.
- **STOP AND READ FIRST (2026-10-14): the plan failed its own audits.**
  `review/audits/2026-10-14-red-team-plan.md` (editor's decision: reject without review; three
  fatal findings: scope trap at ACM Computing Surveys, evaluability construct unreliable and
  unvalidated, no expert human reads the corpus) and
  `review/audits/2026-10-14-statistician-protocol.md` (claim-identification "pass" not
  established, lower bound 0.59; E2 and E3 not testable as written; a real validation needs about
  160 papers and human raters). **Hypotheses E1 to E3 and "organised around claim evaluability"
  are suspended** pending the user's and professor's decision on the orchestrator's proposal:
  (1) Paper 1 becomes a PRISMA systematic review whose core is an integrating framework and
  critical synthesis by research question, with quality appraisal as a descriptive component
  built from extractive, checkable items; (2) first target Artificial Intelligence Review, with a
  scope inquiry to the ACM Computing Surveys editors in parallel; (3) the slack and evaluability
  questions move to Paper 2 as an experimental re-evaluation with reruns; (4) a stated minimum of
  human author reading. Nothing below this block overrides it.
  Work that is valid under any outcome: the integrating framework (RQ1), the database searches,
  the published-version resolution, PRISMA bookkeeping.
- **Order of work changed 2026-10-13 (D0005):** Paper 1 is a systematic review for ACM Computing
  Surveys; Paper 2 (research article, Nature Machine Intelligence) follows. Plan and gates R0 to
  R6: `research/review/PLAN.md`. The G0 to G9 gates below now belong to Paper 2.
- **Title and journal approved by the professor (D0006):** "Diffusion Language Models and Unified
  Multimodal Generation: A Systematic Review and Meta-Analysis", ACM Computing Surveys.
- **Current gate:** R0. Done: dossier (`review/dossier/csur.md`, `exemplar-anatomy.md`), Codex
  round 2, corpus seed (572 records from Awesome-DLMs at 194aa6bd). Pending: survey landscape
  (lit-scout was still running at handoff), protocol.
- **Next action, in order:** (1) rerun `python tools/ingest_awesome.py
  research/sources/md/awesome-dlms@194aa6bd.md` to fill arXiv metadata (API returned 429 today);
  (2) read `review/survey-landscape.md` header and write Claude round 3 in
  `research/debates/2026-10-13-review-angle/` (concede cross-paper regression, propose matched
  within-paper contrasts, split CA); (3) experiment-designer plus statistician write
  `review/protocol.md` (PRISMA 2020, inclusion rules, extraction form, meta-analysis plan);
  (4) novelty-auditor on CA; (5) database searches beyond the repo, then dual screening.
- **Update after lit-scout and Codex round 4 (2026-10-13, evening); this replaces steps 2 to 4:**
  - `review/survey-landscape.md` is done (96 papers rows). No existing survey has a PRISMA-style
    protocol or a reporting audit (14 scanned at keyword level, 18 at abstract level only).
  - **CA is not new as a qualitative claim**: arXiv 2609.01607 (2026-09-01), 2607.04423 Sec. 3.2
    and RealUnify 2509.24897 already say synergy is conditional or absent. CA survives only as
    pooled questions Q1 and Q2, credited to them. New candidate CD (step-scaling law) and the
    questions Q1 to Q5 are in debate round 3.
  - Codex round 4 rejects fixing "Meta-Analysis" in the title before poolable contrasts are shown
    to exist, and rejects CD as untested. Agreed settling step, **do this first**: a feasibility
    inventory. paper-reader agents extract every within-paper matched contrast and step sweep
    (outcome, variance information, sampler, task, what was held fixed) from the 28 multimodal
    records plus a stratified sample of about 40 inference and training records, then count how
    many meet pre-set comparability rules per question. Output `review/feasibility-inventory.md`.
    The protocol is frozen and the conjecture chosen only after that count.
  - If fewer than about 8 poolable contrasts exist for every question, tell the user: the
    subtitle "and Meta-Analysis" must change before submission.
- **Professor's guidance received 2026-10-13 (late):** critical review matters most; full PRISMA
  protocol with exact dates, database-specific strings, exclusion reasons, reviewer agreement and
  a quality appraisal table; consistent table categories; RQ1 to RQ6 answered from evidence;
  "check Discrete Diffusion too" (title or scope, meaning to be confirmed). Draft protocol
  written: `review/protocol.md` v0.1 (not frozen). Samples in `Sample papers/`: an Artificial
  Intelligence Review survey of multimodal **video** diffusion (s10462-026-11699-z; not about
  DLMs; has a "research gap analysis" section and ends with a proposed framework) and arXiv
  2506.13759v5 (closest existing survey). Both converted to `research/sources/md/`; paper-reader
  should extract their anatomy into the dossier.
- **Decisions delegated to Claude by the user (2026-10-13, night). D0007:** working title is now
  "Diffusion Language Models and Unified Multimodal Generation: A Critical Systematic Review of
  Discrete and Continuous Approaches". Budget check: weekly limit 41 percent used with 14 percent
  of the week elapsed (FRUGAL), so no agents were dispatched; a script did the work instead.
- **Running at handoff:** `tools/table_inventory.py` over all 540 arXiv records (captions flagged
  for ablations, step sweeps, remasking, AR comparisons, synergy; text flagged for seeds,
  intervals, code), then the arXiv metadata rerun. Log: `review/feasibility-run.log`; output:
  `review/feasibility/captions.jsonl`. HTML is cached, so rerunning the command resumes.
- **First actions next session:** (1) read the summary table at the end of
  `review/feasibility-run.log`; (2) dispatch hypothesis-smith (opus) with the inventory counts,
  `survey-landscape.md` section on prior CA and CB statements, and the four debate turns, to
  propose conjectures that the available within-paper data can test; (3) novelty-auditor on its
  top two; (4) debate round 5 with Codex; (5) user approval; then freeze the protocol.
- **Conjecture work (2026-10-13, late night).** `review/conjectures.md` holds seven candidates
  H1 to H7 (all E0). Orchestrator selected **H2 (slack conjecture)** and **H5 (noise-floor
  conjecture)**; ruling: H5's between-paper spread is allowed as a dispersion yardstick, not as a
  regression. Codex round 6: accepts H2 as lead candidate, rejects merging H2 and H5 into one
  claim (they measure different things), keeps H5 as a separate RQ6 analysis, and asks for a
  table-level pilot with frozen rules (interpolation of the baseline sweep, non-monotonic sweeps,
  missing variance, exact cell matching) before either organises the review. Agreed.
  Running at this point: novelty-auditor on H2 and H5 (`review/novelty-H2-H5.md`), and two
  stage-2 readers (`review/feasibility/stage2/summary-*.md`).
  **Next:** (1) read the three reports; (2) write `review/pilot-rules.md` freezing the H2 and H5
  computation rules; (3) pilot extraction on about 15 inference papers that report both quality
  and forward passes, with the extra fields listed in conjectures.md section 9, and compute the
  slack share by script; (4) debate round 7 with the pilot numbers; (5) user approval.
- **Results 2026-10-14 (supersede the "Next" list above).** Stage-2 summaries saved
  (`review/feasibility/stage2/summary-*.md`): pooling not supported for remasking or synergy,
  borderline for steps; variance almost never reported. Novelty audit: H2 novel at 0.55 (closest
  arXiv 2609.33947), H5 incremental (arXiv 2606.29228). **H2 pilot** (`review/pilot/
  h2-pilot-summary.md`): claim (a) supported at pilot scale (2 of 9 papers publish the needed
  baseline sweep), claim (b) not supported (slack share 0.00 in both computable papers).
  Debate rounds 7 and 8: both models agree to organise the review around **claim evaluability**
  with three separate pre-registered hypotheses E1 to E3; H2(b) moves to Paper 2 as an experiment.
  **Waiting on the user:** approval of this direction. **Then:** (1) write the evaluability rubric
  (one criterion per claim type, justified from the estimand) into `review/protocol.md` section 6;
  (2) two-rater reliability check on about 40 stratified papers (Claude agent and Codex, plus the
  human sample); (3) red-team and statistician sign the protocol; freeze; (4) database searches.
  Note: auditor agents have no MCP tools, so the novelty-auditor could not use Exa; either add the
  Exa tool names to AUDIT_TOOLS in `tools/build_agents.py` or have lit-scout run its searches.
- **Direction approved by the user 2026-10-14:** review organised around claim evaluability;
  slack conjecture H2(b) becomes Paper 2's experiment. Rubric and two reliability rounds done:
  `review/reliability/RESULTS.md`. Round 2 (rubric v0.2): claim identification kappa 0.71
  (passes), evaluable flag kappa 0.33 (fails); Codex is systematically stricter. Debate round 10:
  rounds 1 and 2 are development only; v0.3 must be frozen before a fresh validation sample.
  **Blocked on the user:** blind human rating of `review/reliability/round2/human-adjudication.csv`
  (30 claims; ideally a second human too). **Then:** write rubric v0.3 (extractive items, computed
  budgets, wording fixes), freeze, validate on a fresh sample, then red-team and statistician sign
  the protocol. The first-round `reliability/human-sheet.csv` is superseded.
- **2026-10-14, searches and venues.** `tools/search_arxiv.py venues` done:
  `corpus/venues-semantic-scholar.json`, 537 of 539 arXiv records found, 156 with a non-arXiv
  venue (ACL 40, NeurIPS 35, ICLR 17, EMNLP 15, ICML 11, NAACL 8, AAAI 8), 20 with a non-arXiv DOI.
  Semantic Scholar venue strings need checking against DBLP or Crossref before use in E2.
  **arXiv API returned 429 for every search request** (this IP fetched about 540 HTML pages on
  2026-10-13); no search has been logged yet. Retry `python tools/search_arxiv.py count` on
  another day before `run S1 S2`. OpenAlex answers, but its `search` parameter now maps to
  full-text search and phrase plus date filters returned zero: read the current OpenAlex API
  documentation before using it as a source; do not guess the syntax.
  Running: red-team referee review of the plan and statistician review of the protocol (both
  return text; save to `review/audits/`).
- **Agent definitions fixed:** hypothesis-smith, experiment-designer and method-architect had not
  loaded (unquoted colon in the description); `tools/build_agents.py` now quotes descriptions.
- **Exemplar reading was structural only (E1).** Before drafting, paper-reader must read two
  exemplar surveys in full.
- **Waiting on the user:** approval of the conjecture once audited; VIT reimbursement cap.
  Python environment, disk space and `hf auth login` are no longer urgent (Paper 2 only).
- **Budget mode at last check (2026-10-13):** FRUGAL (weekly 29 percent used, 11 percent elapsed).

## Gates
### G0 Setup and source integrity
- [x] Git repo, Project OS scaffold, `research/` tree
- [x] Merged framework, agent contract, 19 agents generated
- [x] Ledgers initialised (`tools/ledger.py`)
- [x] graph-memory wrapper repaired (`C:\Users\Shlok\tools\graph-memory.cmd` had a literal tab in its path)
- [x] Venue calendar checked against official pages
- [x] First frontier sweep (E1) saved
- [ ] Python environment with CUDA build verified on the 5070 Ti, lock file committed
- [ ] Seed sources hashed: MMaDA PDF, Awesome-DLMs README at pinned SHA
- [ ] gate-auditor verdict for G0

### G1 Frontier map and anomaly list
- [ ] Awesome-DLMs link inventory in papers ledger (blueprint counted 594 unique URLs at SHA 194aa6bd; recount)
- [ ] MMaDA claim-evidence matrix, including the Table 4 versus abstract mismatch and the evaluation README gap
- [ ] Closest 10 works read in full for T1 and for T2
- [ ] ECCV 2026 understanding-generation transferability paper located and read
- [ ] `research/reports/anomalies.md`
- [ ] gate-auditor verdict

### G2 Hypothesis selection
- [ ] 3 or more candidates with prediction tables
- [ ] novelty-auditor verdict per candidate
- [ ] red-team report per candidate
- [ ] Codex independent review
- [ ] **User approval of one hypothesis and one backup**

### G3 to G9
Checklists are added when the previous gate passes (criteria in FRAMEWORK section 7).

## Dispatch log
| Date | Agent or tool | Brief | Output | Useful? |
|---|---|---|---|---|
| 2026-10-13 | Exa `web_search_exa` | 2027 venue deadlines | FRAMEWORK sections 2 and 10 | yes: two of four requested venues are closed |
| 2026-10-13 | Exa `agent_run` medium | 8-question frontier map | `reports/lit-scout/2026-10-13-frontier-map.md` | yes: rows 5 and 6 sparse; grounding block was verbose, trim the schema next time |

| 2026-10-13 | Exa `web_search_exa` x3 | journal metrics and policies | PLAN section 2 | yes: CSUR JIF 30.4 and scope rule confirmed on official pages |
| 2026-10-13 | Codex via `tools/debate.py` | round 2 on review angle and conjecture | `debates/2026-10-13-review-angle/` | pending |
| 2026-10-13 | venue-intel (sonnet) | CSUR dossier and exemplar anatomy | `review/dossier/` | pending |
| 2026-10-13 | lit-scout (sonnet) | existing-survey landscape, prior statements of CA and CB | `review/survey-landscape.md` | pending |

## Validation tracker
| Item | Validated by | Date | Result |
|---|---|---|---|
| GPU is 12 GB laptop part | `nvidia-smi` | 2026-10-13 | confirmed |
| ICLR 2027 and AAAI-27 deadlines passed | iclr.cc, aaai.org | 2026-10-13 | confirmed |
| IJCAI, ICML, NeurIPS 2027 dates | third-party trackers only | 2026-10-13 | **projected, recheck** |
| Frontier map paper IDs | none yet | | **E1, unverified** |

## Decisions (mirror of the decisions ledger)
- D0001 2026-10-13: Gemini's pre-chosen architecture is not adopted (prior art, no evidence).
- D0002 2026-10-13: venue shortlist ICML or IJCAI 2027, fallback NeurIPS 2027; frozen at G7.
- D0003 2026-10-13: detector evasion and watermark removal replaced by clarity editing plus disclosure.
- D0004 2026-10-13: journal first. Nature Machine Intelligence, then IEEE TPAMI (or Nature
  Communications if VIT covers 7,350 USD), then a Q1 fallback. Supersedes D0002.
- Open with the user: VIT's reimbursement cap per paper; whether rented GPU time is acceptable
  for full-precision confirmation runs after Gate 5; restricted-data requests (SETUP_STEPS section 6).
