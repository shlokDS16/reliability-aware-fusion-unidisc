# Progress ledger

## RESUME
- **Current gate:** G0 nearly done (environment lock outstanding), then G1.
- **Next action:** create the Python environment (SETUP_STEPS section 4), then run the Gate 1
  block of `research/prompts/MASTER_PROMPT.md`.
- **Waiting on the user:** disk space, `hf auth login`, direction preference between T1 and T2
  (final choice is made at G2 with audits in hand).
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
