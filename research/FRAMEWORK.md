# DLM Discovery: merged research framework (v1, 2026-10-13)

Merges `DLM_Research_Discovery_Blueprint.md` (ChatGPT, 24 agents, called A0 to A23 below) and
`AI Research Agent Framework Proposal.pdf` (Gemini, 14 agents, called G1 to G14), the
`q1-research-paper` skill, the `research-humanizer` skill and the earlier paper-build prompt.
The blueprint stays in the repo as the long-form reference; this file is the operating version.

## 0. What was kept, changed and dropped

| Source | Kept | Changed or dropped, and why |
|---|---|---|
| Blueprint | Evidence levels, ledgers, gates, discovery loop, scale ladder, fair-comparison and statistics rules | 24 agents merged to 19 (section 4); its 10-week schedule compressed to a 14-day sprint plus hardening; cloud tiers D to F made optional |
| Gemini PDF | Structural-hole search across citation clusters, assumption inversion, a mathematical red team before compute, the self-recovering lab agent, venue analysis | Its pre-chosen idea ("continuous-time speculative diffusion with T2M correction") is **not adopted**: token-to-mask remasking is already published (its own reference 6, plus ReMDM 2503.00307, RemeDi 2509.23653, CoDR 2610.08833), and the claimed gains are predictions, not results. "Watermark neutralisation" and detector evasion are replaced by a clarity editor with AI-use disclosure. "Impact factor 40+" framing dropped: the target is an A* conference. |
| q1 skill | Numerical consistency, honesty policy, figure rules, reviewer-response workflow | Word and docx workflow replaced by LaTeX conference templates (`.claude/skills/astar-ml-paper`) |
| Earlier prompt | progress file, checklists, validation tracking, audit agent, 13 to 14 figures, staged algorithms, equations, sample-paper study | Order changed: venue is fixed after results, sample papers studied at Gate 7 |

## 1. Mission and success test

Find, test and publish one new scientific result on diffusion language models (DLMs) or unified
multimodal discrete-diffusion models. A result counts only if it has: a falsifiable claim, a
novelty case against concurrent work, an experiment that could have failed, support across seeds
and at least two models or datasets, a mechanism that predicts something beyond the first setting,
and a reproducible trail from raw predictions to every number in the paper.

Non-negotiables: no planned result reported as observed; no invented citation, DOI, number or
protocol; no test-set tuning; negative results and failed runs are kept; the human authors approve
the idea, any spend, and the final claims.

## 2. Constraints measured on 2026-10-13

- **Hardware:** RTX 5070 Ti *Laptop* GPU, **12 GB VRAM** (not 16), 31 GB RAM, Core Ultra 9 275HX,
  66.7 GB free on C:. An 8B DLM runs only quantised (4-bit about 6 GB). MMaDA's own training used
  64 A100-80GB GPUs; retraining it is out of reach. Local work is ladder levels A to C (section 8).
- **Venues:** ICLR 2027 closed 2026-09-25 and AAAI-27 closed 2026-07-28 (official pages). Open:
  ACL 2027 via ARR, 2027-01-04 (official); IJCAI 2027 about mid-January, ICML 2027 about late
  January, NeurIPS 2027 about May (all three projected, CFPs not yet posted).
- **Token budget:** weekly limit 29 percent used with about 11 percent of the week elapsed, which
  is FRUGAL mode under the token-steward rules. Hence waves of at most 3 subagents, file-based
  reports, Exa Agent for literature sweeps (about 0.10 USD per medium run, no Claude tokens), and a
  fresh session per phase.

## 3. Discovery loop

1. Observe a failure, trade-off or table-versus-text mismatch. 2. Write the current explanation
and its hidden assumptions. 3. Generate at least three competing mechanisms, including "evaluation
artifact". 4. Find the cheapest intervention on which they disagree. 5. Preregister claim, metric,
thresholds and stop rule. 6. Run the cheapest falsification first. 7. Update the hypothesis ledger;
a rescued hypothesis is a new version. 8. Test invariance: seeds, a second model family, a second
dataset. 9. Explain why, with a prediction the baseline account does not make. 10. Let independent
reviewers try to break it.

Idea sources, in order of yield: reproduction gaps, anomalies in published tables, structural holes
between citation clusters, inverted assumptions, analogies from adjacent fields.

## 4. Agent roster (19 subagents plus the orchestrator)

Generated from `tools/build_agents.py` into `.claude/agents/`. Edit the roster there and rerun.

| Layer | Agent | Model | Merges | Output |
|---|---|---|---|---|
| Orchestration | **orchestrator** (main session) | session | A0, G6 | decisions, queue, gates, budget |
| Discovery | lit-scout | sonnet | A1, A3, G1 | papers ledger, reading queue |
| Discovery | paper-reader | sonnet | A2 | claims ledger |
| Discovery | novelty-auditor | opus | A4 | closest-10 matrix, verdict |
| Discovery | hypothesis-smith | opus | A5, G2 | mechanisms and prediction table |
| Discovery | experiment-designer | sonnet | A7 | prereg card |
| Data | data-steward | sonnet | A8, A9, G4, G5 | dataset cards, manifests |
| Execution | repro-engineer | sonnet | A10 | reproduction report |
| Execution | method-architect | opus | A11, G7 | derivation, staged algorithms |
| Execution | lab-engineer | sonnet | A12, A13, G7, G14 | code, runs, telemetry |
| Execution | eval-harness | sonnet | A14 | frozen harness, predictions |
| Execution | ablation-robustness | sonnet | A16, A17 | ablation and robustness matrix |
| Publishing | venue-intel | sonnet | A19, G8 | venue-fit matrix, style files |
| Publishing | figure-smith | sonnet | new | figures, tables, visual QA log |
| Publishing | manuscript-writer | sonnet | A20, G9, G10 | LaTeX sections |
| Publishing | clarity-editor | sonnet | A21, G13 | edited prose, diff, disclosure |
| Assurance | red-team | opus | A6, G3, G12 | findings rated fatal, major, minor |
| Assurance | statistician | sonnet | A15 | analysis plan, intervals |
| Assurance | citation-validator | haiku | A18, G11 | references ledger |
| Assurance | gate-auditor | opus | A23, audit agent | gate verdicts |

**Independent panel (A22)** is deliberately not a Claude agent: use the `codex:codex-rescue` agent
(GPT through Codex) and NotebookLM (Gemini, `mcp__notebooklm__*`) on the same artifact. Each
objection is checked against a primary source or a rerun. Agreement among models is not evidence.

## 5. Delegation protocol

- **Brief template** (the agent knows nothing else): goal in one sentence; what is already ruled
  out; exact files and ledger IDs to read; scope limits; report path; the 8-line reply format.
- **Waves:** at most 3 agents at once. Discovery and review agents may run in parallel. Agents that
  write code or LaTeX never run in parallel with each other.
- **Proposer is never validator.** hypothesis-smith and method-architect propose; novelty-auditor,
  red-team, statistician and gate-auditor judge, and their tool list has no Edit.
- **Artifacts move as paths.** The orchestrator reads report headers and ledger rows, not
  transcripts, and tracks every dispatch in `research/progress.md` (agent, brief, report, verdict on
  whether the output was useful).
- **Model is always named.** Opus only for the five judgement roles above.
- **Stop rule:** an agent that returns nothing checkable twice is replaced by a narrower brief.

## 6. Ledgers and evidence levels

`research/ledgers/*.jsonl`, append-only, through `tools/ledger.py`: papers, claims, hypotheses,
experiments, failures, decisions, references.

| Level | Meaning | Allowed wording |
|---|---|---|
| E0 | model suggestion | "we hypothesise" (internal only) |
| E1 | search snippet, README, Exa summary | lead to follow |
| E2 | primary paper read in full | "X et al. report" |
| E3 | code or protocol inspected at a pinned SHA | implementation details |
| E4 | reproduced here within tolerance | "we reproduce" |
| E5 | preregistered, repeated, with intervals and controls | "we show" |

## 7. Phases, gates and calendar

| Gate | Phase | Days | Exit criteria (checked by gate-auditor) |
|---|---|---|---|
| G0 | Setup and source integrity | 1 | repo, ledgers, agents, environment lock, sources hashed |
| G1 | Frontier map and anomaly list | 2 to 4 | Awesome-DLMs links inventoried; closest 10 per candidate read in full; MMaDA claim matrix |
| G2 | Hypothesis selection | 5 | 3 or more candidates with prediction tables; novelty verdict and red-team report for each; **user approves one** |
| G3 | Preregistration | 6 | claim contract and analysis plan frozen and signed by statistician and red-team |
| G4 | Baseline reproduction | 6 to 8 | one published row reproduced or the gap quantified; quantisation gap measured |
| G5 | Decisive pilot | 8 to 10 | effect beyond noise on the primary endpoint; best alternative weakened; otherwise pivot to the backup candidate |
| G6 | Generalise and stress | 10 to 14 | 3 or more seeds, second model or dataset, ablations, robustness matrix, intervals on every claim |
| G7 | Venue fixed | 14 | venue chosen from what the evidence supports; 5 sample papers analysed |
| G8 | Manuscript | hardening | every number traced to a run; references verified; LLM-use statement; panel objections resolved |
| G9 | Release | before deadline | clean-room reproduction passes; code and artifacts archived with a DOI |

The 14 days end at a go or no-go on the evidence, not at a submitted paper. Hardening continues
until the venue deadline. An arXiv preprint goes up as soon as G8 passes, because the field moves weekly.

## 8. Compute ladder on this machine

| Level | Work | Fits 12 GB? |
|---|---|---|
| A | derivations, synthetic and toy tasks, models under 50M parameters | yes, minutes |
| B | frozen-checkpoint measurement: activations, logits, trajectories of MDLM, SEDD, Duo (about 130M to 170M), LLaDA-8B, Dream-7B, MMaDA-8B at 4-bit | yes; report the quantisation gap |
| C | fine-tuning or training models of 100M to 400M; LoRA on quantised 8B with short sequences | yes, hours to days |
| D+ | full fine-tuning of 8B, multi-seed RL post-training | no; cloud only, and only after G5 with a written cost estimate and user approval |

Before any scale-up: pilot passed, baseline reproduced, config frozen, throughput measured, stop
thresholds set, budget cap written, and a reason the larger run answers what the pilot could not.

## 9. Tool matrix (status verified 2026-10-13)

| Job | Tool | Status | Use |
|---|---|---|---|
| Literature sweep | Exa connector `agent_run` | working | multi-search sweeps with `outputSchema`; effort low or medium; do not request grounding-heavy schemas |
| Lookup, page read | Exa `web_search_exa`, `web_fetch_exa` | working | single questions; batch URLs in one fetch |
| Citation graph, DOI | OpenAlex, Semantic Scholar, Crossref REST via `curl` | no key needed | forward and backward citations, reference validation |
| Repos | `gh` CLI (logged in as shlokDS16) | working | trees, SHAs, issues; GitHub plugin MCP is optional |
| PDFs | `markitdown.exe` to file, then grep headings | working | never load a whole paper into context |
| Paywalled papers | VIT eGateway in the user's Chrome | user action | user logs in; PDFs saved to `research/sources/pdfs/` |
| Models, datasets | Hugging Face Hub (`hf` CLI) | **not installed** | see `SETUP_STEPS.md` |
| Python env | `uv` with Python 3.12 or 3.13 | uv present | system Python 3.14 is too new for parts of the ML stack |
| Tracking | run directories plus `metrics.jsonl`; Trackio optional | local | no external account needed |
| LaTeX | MiKTeX `latexmk` | working | conference style files in `paper/style/` |
| Independent review | Codex plugin, NotebookLM MCP | available | panel reviews at G2, G5, G8 |
| Prose | `research-humanizer`, `hidden-unicode` skills | installed | clarity pass and stray-character cleanup |
| Memory | `graph-memory` (wrapper repaired today) | working once code exists | brief at session start, sync at session end |
| Not used | n8n, task-master-ai, Zotero, W&B, Litmaps, ResearchRabbit, Paperpal, Overleaf | failed, or adds an account without adding evidence | ledgers and `.bib` cover their role |

## 10. Venue strategy

**Revised 2026-10-13 (D0004, supersedes D0002): journal first.** VIT reimburses journal charges
and a journal has no deadline, which suits a 12 GB machine.

| Step | Journal | 2025 JIF | Cost | Source checked 2026-10-13 |
|---|---|---|---|---|
| 1 | Nature Machine Intelligence | 29.8 | subscription route free; gold OA 12,850 USD | journal metrics and publishing-options pages |
| 2 | IEEE TPAMI | 20.4 | subscription route free; OA 2,800 USD; over-length pages 220 USD each | IEEE 2026 APC list (official); JIF from a third-party page, recheck |
| 2b | Nature Communications | 18.1 | 7,350 USD, no free route | third-party page quoting the journal page, recheck |
| 3 | Q1 fallback chosen at G7 (Information Fusion, IJCV, TNNLS, Pattern Recognition) | not yet verified | | |

One journal at a time. The same work cannot also go to ICML, IJCAI or NeurIPS proceedings; those
remain the route only if steps 1 and 2 both fail. An arXiv preprint is posted at submission.
What step 1 demands of the evidence: a finding about how unified diffusion models work, shown
with interventions on at least three model families, at full precision for the headline numbers,
with code and data released. venue-intel reads the live author guide at G7 (word limit, number of
main display items, Extended Data rules); figures beyond the main limit move to Extended Data.

## 11. Paper build rules

See `.claude/skills/astar-ml-paper/SKILL.md`. In short: claim-led; about 6 figures in the main text
and 7 to 8 in the appendix, each generated by a script and visually inspected; numbered `amsmath`
equations with every symbol defined; `algorithm2e` algorithms that build from primitives to the
final procedure; every number traced to a run; references verified one by one.

## 12. Integrity and AI use

The paper is edited for clarity, not to defeat detectors, and it carries the LLM-use statement the
venue requires. No watermark or provenance removal. No result, citation or dataset is fabricated.
Earlier papers' topics (conformal water-quality retrieval on GLORIA; evaluation protocol and
battery state of health) are excluded.
