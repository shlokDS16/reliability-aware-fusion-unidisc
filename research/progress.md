# Progress ledger

## RESUME
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
