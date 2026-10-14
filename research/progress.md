# Progress ledger

## RESUME
- **CURRENT STATE (2026-10-14, late session; newest block, overrides all older ones).**
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
