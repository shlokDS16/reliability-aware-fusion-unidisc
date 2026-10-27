```yaml
agent: security-engineer (general briefed audit)
date: 2026-10-27
brief: Security audit and study of 4 public repos; best practice for Claude Code subagents and sub-sessions; recommendations for the expert-team skill and the research-paper team
sources_examined:
  - github.com/ashishpatel26/500-AI-Agents-Projects @ 9beeb721c2af551bacaab827a76bddaecaa0ca5e
  - github.com/rshah515/claude-code-subagents @ 872758205aa89f50ddd689db40d5162da278ff25
  - github.com/stanfordnlp/dspy @ 4dbeec17c267f296117630af59274bbeaf142117
  - github.com/AnasHXH/Connecting-LLMs-to-Diffusion-Models-A-Survey @ 8ac637eba0397fc1e00d3a236c1bf3f72d8fc055
  - code.claude.com docs: sub-agents, agent-teams, skills, costs, cross-session-messaging
  - platform.claude.com: skill authoring best practices
  - anthropic.com/engineering: multi-agent-research-system, effective-context-engineering-for-ai-agents, writing-tools-for-agents
  - prompt-enhancer SKILL.md (AppData/Roaming/Claude/local-agent-mode-sessions/.../skills/prompt-enhancer/SKILL.md, first 120 of about 190 lines)
coverage: >
  Part A: all four repos cloned shallow into C:\Users\Shlok\AppData\Local\Temp\claude\repo-audit-2026-10-27\{500agents,subagents,dspy,survey}.
  Nothing from them was executed, installed or imported. Hidden-Unicode scan (script in ...\_scripts\scan.py, run with python -I) covered
  .md .json .py .yaml .yml .txt .sh .toml .ipynb .cfg .js .ts in all four repos (109, 171, 695, 1 files). Pattern greps (injection phrases,
  curl/wget/eval/base64, ssh/credential words, settings.json, hooks, non-GitHub URLs, long base64, HTML comments) ran over .md/.json/.sh
  (subagents) and .md/.py/.txt/.json (500agents). Frontmatter statistics computed for all 165 agent files in repo 2. NOT covered: I did not
  read every agent file in repo 2 (about 12 read in part: orchestrators/tech-lead, project-manager, prd-writer; core/code-reviewer, debugger;
  quality/security-auditor; research/ml-researcher, research-engineer); the 21 agents/ code folders and crewai_mcp_course in repo 1 were
  grepped, not read (only agents/20 and agents/21 read in part); dspy was not scanned beyond Unicode, metadata and optimizer code/doc
  skims, and its dependency tree was not audited; the PNG in repo 4 was not inspected. Part B: official docs for hooks and the Agent SDK were
  NOT fetched. Fetched pages came through a summarising fetch tool; agent-teams, costs, cross-session and skill-best-practices returned
  near-verbatim, the others were summarised (treat as E1).
claims:
  - statement: No hidden-Unicode carriers (bidi overrides, tag characters, zero-width space/non-joiner/BOM) exist in the scanned text files of any of the four repos; only U+FE0F (emoji variation selector) and U+200D (ZWJ inside emoji sequences) occur.
    status: supported
    evidence: scan.py output; 500agents 36 hits in 12 files, subagents 3 hits in 3 files, dspy 207 hits in 16 files (all U+FE0F), survey 0
    level: E3
    confidence: 0.9
  - statement: rshah515/claude-code-subagents contains no hooks, settings.json, MCP configs, binaries or base64 blobs; its only script is a 22-line git helper whose commands are git branch/commit with commented remote examples.
    status: supported
    evidence: find for risky file types; github-setup.sh lines 10-21; long-base64 grep empty
    level: E3
    confidence: 0.85
  - statement: 500-AI-Agents-Projects agents/21-pii-sanitization-agent posts user text to the third-party host api.trustboost.dev (crypto-payment gated); it should not be run.
    status: supported
    evidence: agents/21-pii-sanitization-agent/agent.py:33, .env.example:10-11
    level: E3
    confidence: 0.9
  - statement: The survey README's arXiv badge (2108.10257) points to an unrelated paper (SwinIR), and the README lists only one masked-generative paper (Muse).
    status: supported
    evidence: survey/README.md line 2 and line 31; arxiv.org/abs/2108.10257 title returned "SwinIR"
    level: E1
    confidence: 0.85
  - statement: stanfordnlp/dspy is the official Stanford repo and `pip install dspy` is the documented package.
    status: supported
    evidence: gh api (Organization, MIT, 38,815 stars, pushed 2026-10-26); pyproject name="dspy" version 3.4.1; README.md:31; PyPI JSON lists 3.4.1, MIT, author email okhattab@stanford.edu
    level: E3
    confidence: 0.9
competing_explanations: []
unknowns:
  - Whether Ollama has any model pulled (the `ollama list` call hung beyond 120 s and was moved to a background shell; check before any DSPy demo).
  - Real cost of a GEPA or MIPROv2 run on a local 7-8B model for our briefs (not measured; no run was made).
  - Hooks and Agent SDK documentation, and Anthropic's agent-teams token multiple beyond the figures quoted below.
next_test: {hypothesis: "A role prompt tuned against a rubric metric beats the hand-written one on held-out tasks", intervention: "manual reflect-and-rewrite loop on 2 roles (novelty-auditor, citation-validator) using gate-auditor feedback", primary_metric: "rubric score on 10 held-out tasks", falsifier: "no gain over baseline beyond noise", gpu_hours: 0}
```

# Repo audit and subagent best practice, 2026-10-27

Verdicts: **500-AI-Agents-Projects: SAFE TO READ. claude-code-subagents: SAFE TO READ (clean), copy nothing wholesale. dspy: SAFE TO READ (official; install not needed). Connecting-LLMs-to-Diffusion survey: SAFE TO READ (low value, unverified IDs).**

## A1. ashishpatel26/500-AI-Agents-Projects

| Item | Finding |
|---|---|
| SHA | 9beeb721c2af551bacaab827a76bddaecaa0ca5e |
| Size | 2.0 MB, 145 files (30 .md, 25 .py, 24 .txt, 24 .example, 21 .yaml, 2 .jsx, 2 .js, images) |
| Metadata (gh api) | 39,060 stars, 7,016 forks, MIT, user account, last push 2026-07-27, created 2024-12-20 |
| Hidden Unicode | 36 hits in 12 files, all U+FE0F or U+200D (emoji in README.md and in `print` strings of agents/*/agent.py). No bidi, no tag characters. |
| Injection text | Grep for "ignore previous", .ssh, exfiltrat, curl/wget, pipes to shell, base64, eval/exec, os.system, subprocess, pickle, settings.json: no hits. No HTML comments. |
| Hooks / MCP / binaries | None. `web/` is a Vite front end (package.json not run); `scripts/star-history.mjs` not run. |
| Non-GitHub hosts | img.shields.io (badges), microsoft.github.io (AutoGen notebooks), newsapi.org, tavily, openai. One unusual host: **api.trustboost.dev**. |

Flag: `agents/21-pii-sanitization-agent/agent.py:33` sets `API_BASE` to `https://api.trustboost.dev` and posts the text to `/sanitize` with a wallet address and a Solana `tx_hash` (free trial of 50 calls). It is a "redact PII" tool that ships the PII to a third party. README.md also advertises it in the industry table. Do not run it. Nothing else in `agents/` calls an unknown host (the other 20 use OpenAI/Tavily/NewsAPI with a `.env`).

Verdict: **SAFE TO READ.** Nothing here is worth copying: the 500 "projects" are a README table of links to other repos (E1: I did not follow them), and the 21 runnable agents are small LangChain/OpenAI demos (default model `gpt-4o-mini`, not Claude).

Useful, relevant patterns (all E1 or E3 for code I read):
- Framework comparison table (README.md:67-85): LangGraph for stateful graphs and RAG, CrewAI for role-based teams, AutoGen for code and research with group chat, Agno for light single agents. Relevant lesson: our "expert team" is closest to CrewAI's role/task/crew vocabulary, but Claude Code subagents already provide the runtime, so we need only the vocabulary.
- `agents/20-multi-agent-debate/agent.py` (read lines 1-60): two advocates (temperature 0.6, word-capped to 150 words, told the opponent's last argument) plus an impartial judge (temperature 0) that returns winner, scores, strongest argument per side and a synthesis. Maps directly onto proposer versus red-team with a gate-auditor as judge; the word cap and "respond to the opponent's last point" are the transferable parts.
- Research-type entries in the link table (README lines 158, 174, 236-244, 258): AutoGen group chat of 6, "Research Scholar Agent", "DeepKnowledge" iterative search, LangGraph "information gathering via prompting". Pattern: planner, searcher, reader, writer, with a loop that decides when evidence is sufficient. Not verified (links not opened).
- README lists "Citadel" (orchestrates Claude Code agent fleets with lifecycle hooks) and "Agent Memory Guard" (memory poisoning). Link-only, not examined.
- SECURITY.md exists with an email contact; irrelevant to us.

## A2. rshah515/claude-code-subagents

| Item | Finding |
|---|---|
| SHA | 872758205aa89f50ddd689db40d5162da278ff25 |
| Size | 3.1 MB, 173 files; 165 agent definitions (+ README, WORKFLOWS, WORKFLOW_CONFIG, CLAUDE.md, CONTRIBUTING, LICENSE, github-setup.sh) |
| Metadata | 105 stars, 18 forks, MIT (Raj Shah, 2025), last push 2025-08-08, created 2025-08-03. Stale (11 months). |
| Hidden Unicode | 3 hits, all U+FE0F, in README.md:621, WORKFLOWS.md:525, WORKFLOW_CONFIG.md:203 (emoji). |
| Injection text | Grep for the injection set across .md/.json/.sh: matches are only benign uses of "hooks" (React hooks, pre-commit hooks, webhooks), "credentials" (checklists such as "No hardcoded credentials", security-auditor.md:257) and "settings". No instruction aimed at the model to exfiltrate, fetch or disable safety. No HTML comments except a README template example (README.md:633). |
| Scripts | `github-setup.sh` (22 lines): `git branch -M main`; remote commands are commented out. No curl, no sudo, no rm. |
| Hooks / settings / MCP | None in the repo. Some agents *name* MCP tools in `tools:` (context7 in at least 63 files, firecrawl in at least 21); they only work if you have those servers. |
| URLs | docs.anthropic.com, github.com, example.com. |
| Frontmatter | 165 agent files, 0 set `model:` (all inherit). **136 of 165 grant Bash** and most also grant Write/MultiEdit; common line is "Read, Write, MultiEdit, Bash, Grep, TodoWrite, WebSearch, mcp__context7__..." (53 files). Five .md files have no frontmatter. None sets opus or fable. |

Flags:
1. `CLAUDE.md` at repo root (line 1 onward) is written as a build instruction ("You are building a comprehensive collection...", local path /Users/rajshah/...). If the repo is cloned **inside** a project, or added with `--add-dir`, that file can be loaded as instructions. Never put the repo root in a project; copy single agent files only.
2. Broad tool grants: Bash on reviewers and planners (core/code-reviewer.md `tools: Grep, Glob, Read, TodoWrite, Bash`). Fine as text, but any file we adopt must have its `tools:` rewritten to the minimum.
3. `orchestrators/project-manager.md` has `tools: Task, ...` (subagent spawning) and its body tells the agent to launch parallel tasks "in a single response"; it also contains no spend cap. Do not adopt as is; it encourages over-spawning.

Verdict: **SAFE TO READ** (content clean). **SAFE TO COPY SPECIFIC FILES only after editing `tools:` and `model:`**, but I recommend copying none: quality is low for our purpose (below). If you copy for structure only: orchestrators/project-manager.md, orchestrators/prd-writer.md, core/code-reviewer.md, core/debugger.md, quality/security-auditor.md, research/ml-researcher.md.

What is well written and the prompt pattern (observed in the 8 files read, E3):
- Uniform skeleton in all 165 (167 files contain "Communication Style" and "With "): frontmatter with `name`, long `description`, `tools`; one-paragraph role statement ("You are a code reviewer who..."); a first-person "Communication Style" paragraph; topical sections with bold-labelled bullet lists; ASCII box diagrams for frameworks; a one-line "Framework" paragraph per section giving the principle; "Best Practices" numbered list; "Integration with Other Agents" list ("With refactorer: ...").
- Good parts to borrow: (a) the descriptions in orchestrators say when to auto-invoke (prd-writer: "PRIMARY AGENT for project planning... Automatically invoked for ... build a feature"), consistent with the docs' advice to put "use proactively" in descriptions; (b) project-manager.md lines 46-56 give a delegation checklist: Context Provision, Clear Deliverables, Integration Guidelines, Quality Criteria, Timeline Context, plus "Never assume specialists know about other parallel work - explicitly state interfaces." This is the single most reusable passage for a lead's brief writer; (c) code-reviewer.md:135 "Priority Classification: Critical, major, minor, suggestion" is a usable severity scale; (d) debugger.md best practices: "Reproduce first", "Minimal changes", "Test the fix".
- Weak parts (do not imitate): no output format or report contract (only 1 file contains "Output Format"), no stop condition, no effort or budget rule, no evidence discipline, no `model:`; 1,500-2,100 words per agent with 8 ASCII boxes (research/ml-researcher.md) that burn tokens each time the agent starts and say nothing Claude does not already know; first-person "I'm collaborative" personas add tone, not behaviour; "Integration with Other Agents" lists invite agents to call each other. The Anthropic skill guidance says "Claude is already very smart; only add context Claude doesn't already have" (platform.claude.com best-practices), which these files violate.
- The research folder has only two agents (ml-researcher, research-engineer), both generic MLOps/architecture text; there is nothing on literature, novelty, statistics, red-teaming or citation integrity. Our existing project agents (novelty-auditor, red-team, statistician, citation-validator, gate-auditor) are already ahead; use this repo only as a style foil.

## A3. stanfordnlp/dspy

| Item | Finding |
|---|---|
| SHA | 4dbeec17c267f296117630af59274bbeaf142117 |
| Size | 28 MB, 766 files |
| Identity (gh api, PyPI JSON) | Organization `stanfordnlp`; 38,815 stars; 3,455 forks; MIT ("Copyright (c) 2023 Stanford Future Data Systems"); last push 2026-10-26; latest GitHub release 3.4.1 published 2026-10-12; PyPI latest 3.4.1, requires_python `>=3.10,<3.16`, author email Omar Khattab <okhattab@stanford.edu>. |
| Package name | pyproject.toml `name="dspy"`, version 3.4.1; README.md:31 `pip install dspy`. Official. (Older `dspy-ai` name is a historical alias in my memory, not verified here.) |
| Unicode | 207 hits in 16 files, all U+FE0F (tutorial notebooks, evaluate.py:350-352 print strings). |
| Not done | No full code scan, no dependency audit (litellm, openai, diskcache, etc.), no script run (.github/workflow_scripts/install_testpypi_pkg.sh and scripts/bootstrap_python.sh not read or run). |

Verdict: **SAFE TO READ.** Installing is acceptable in a throwaway venv if we ever want it, but this audit does not vouch for the transitive dependencies.

Ideas to apply to brief writing without running DSPy (E3 for code/doc read; E1 for effect on quality):
- **Signature** = typed declaration of inputs and outputs for one step. Equivalent for us: every brief is a fixed record with named input fields (objective, context pointers, already-ruled-out) and named output fields (report path, yaml claims, reply line). The contract already has the output side; add the input side as a schema the lead fills.
- **Module** = strategy wrapped around a signature (Predict, ChainOfThought, ReAct). Equivalent: the agent definition is the module (stable role, tools, method), the brief is the signature instance. Keep the role file small and move task detail to the brief.
- **Metric** is the engine of all optimisers. docs/docs/learn/optimization/optimizers.md says an optimiser takes a program, a metric and "a few training inputs"; 5-10 examples can be enough. For us the metric is a rubric per role (for example citation-validator: every entry resolves in Crossref/arXiv; novelty-auditor: names closest prior work with IDs; red-team: each finding has a falsifier) scored by gate-auditor or by a script.
- **Few-shot bootstrapping** (BootstrapFewShot): run the program, keep traces that pass the metric as demonstrations. Equivalent: store 1-3 accepted past reports per role as exemplars in `research/paper2/team/exemplars/<role>.md` and point the brief at them (pointer, not paste).
- **Instruction optimisers**: COPRO (coordinate-ascent over instruction rewrites), **MIPROv2** (bootstrap demos, propose instructions, Bayesian search over combinations; `auto` modes in code: light = 6 candidates, 100 validation examples; medium 12/300; heavy 18/1000; mipro_optimizer_v2.py:46-50), SIMBA (finds high-variance examples, reflects on failures), **GEPA** (reflects on trajectories and uses textual feedback from the metric; a metric may return `{score, feedback}` text, gepa.py around lines 57-64 and 201-235). The transferable idea of GEPA is the loop: run, read the failure trace plus the auditor's text feedback, rewrite the instruction, keep a Pareto set of candidates. We can run that loop by hand or with one Opus review per role.
- **Cost**: docs (optimizers.md:112-113) say a typical simple optimisation run costs on the order of $2 and ten minutes on an API model, ranging from cents to tens of dollars. We cannot spend API money on loops (and the Claude Code subscription is not an API budget), so automatic MIPROv2/GEPA over Claude is out.
- **Is a small local run feasible?** Mechanically yes: DSPy takes any LM through litellm, and an Ollama binary exists at C:\Users\Shlok\AppData\Local\Programs\Ollama\ollama (model inventory unverified). A 7-8B quantised model fits the 12 GB GPU. But (a) briefs are consumed by Claude, so a prompt optimised for a small local model need not transfer; (b) reflection quality of an 8B proposer is weak; (c) we have no labelled task set yet; (d) GPU runs need a go-ahead and share the card with other sessions (memory: parallel-research-sessions, laptop-gpu-crashes). Recommendation: do not run DSPy now. If wanted later, a demo on one role with 10 tasks, `auto="light"`, local model, is a few hours of GPU at most, but I did not measure it.
- **Combining with prompt-enhancer**: the prompt-enhancer skill (first 120 lines read) is a rewriter, not an optimiser: mandatory GOAL and DELIVERABLE, optional CONTEXT, AUDIENCE, CONSTRAINTS, FORMAT, STACK, RESEARCH, EXAMPLES, SUCCESS CRITERIA, OPEN QUESTIONS; "fewer sharper blocks beat more vague ones"; "does NOT execute". It is the signature template. DSPy contributes the missing half: a metric and a test set to decide whether a rewritten brief is actually better. Practical combination: lead drafts brief with the prompt-enhancer block set plus our research blocks (EVIDENCE LEVEL, REPORT PATH, BUDGET, ALREADY RULED OUT), then a role-level rubric (metric) judges the report; role prompts are revised by reflection (GEPA-style) only when the rubric shows a repeated failure.

## A4. AnasHXH/Connecting-LLMs-to-Diffusion-Models-A-Survey

| Item | Finding |
|---|---|
| SHA | 8ac637eba0397fc1e00d3a236c1bf3f72d8fc055 |
| Size | 40 KB, 2 files (README.md 13,955 bytes, chart.png) |
| Metadata | 8 stars, 1 fork, **no licence**, last push 2024-12-17, personal account. |
| Unicode / injection | 0 hits. README contains only titles and links. PNG not inspected. |

Verdict: **SAFE TO READ.** It is a paper list, not a survey text, with no licence (do not copy its text; cite the papers themselves).

Concern: the arXiv badge on line 2 links `arxiv.org/abs/2108.10257`, which arXiv shows as "SwinIR: Image Restoration Using Swin Transformer" (Liang et al.), unrelated. So the repo does not give a verifiable arXiv ID for the survey it names. All IDs below are copied as given in the README and are E1 (not checked against arXiv).

"Taxonomy" as given: three headings only, with the direction "LLM helps diffusion":
1. Enhancing text-to-image (README lines 8-53, about 40 entries)
2. Multimodal Input to Multimodal Output (lines 54-67, 12 entries)
3. Application (lines 68+, about 15 entries, partly duplicated from section 1)

Masked / discrete / unified entries as given in the README (the list has no discrete diffusion language model entries at all):
- Muse: Text-To-Image Generation via Masked Generative Transformers, arXiv 2301.00704 (only masked-generative paper; section 1, line 31)
- NExT-GPT: Any-to-Any Multimodal LLM, arXiv 2309.05519 (section 2; LLM plus separate diffusion decoders, not discrete diffusion)
- MINIGPT-5: Interleaved Vision-and-Language Generation via Generative Vokens, arXiv 2310.02239
- VL-GPT: A Generative Pre-trained Transformer for Vision and Language Understanding and Generation, arXiv 2312.09251
- De-Diffusion Makes Text a Strong Cross-Modal Interface, arXiv 2311.00618
- M-VADER: A Model for Diffusion with Multimodal Context, arXiv 2212.02936
- EasyGen: Easing Multimodal Generation with a Bidirectional Conditional Diffusion Model and LLMs, arXiv 2310.08949
- ImageBind-LLM: Multi-modality instruction tuning, arXiv 2309.03905

Use for Paper 2: marginal. It predates LLaDA/MDLM-style masked diffusion LMs and the unified discrete models already in `research/paper2/professor-sources`; I would not cite it. It is only a pointer for the older "LLM + continuous diffusion" family that Paper 2's related work can contrast with.

## B. Best practice for subagents and sub-sessions (docs read 2026-10-27)

Sources: [Sub] https://code.claude.com/docs/en/sub-agents ; [Teams] https://code.claude.com/docs/en/agent-teams ; [Skills] https://code.claude.com/docs/en/skills ; [SkillBP] https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices ; [Costs] https://code.claude.com/docs/en/costs ; [Xsess] https://code.claude.com/docs/en/cross-session-messaging ; [MAR] https://www.anthropic.com/engineering/multi-agent-research-system ; [Ctx] https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents ; [Tools] https://www.anthropic.com/engineering/writing-tools-for-agents.

**B1. Subagent, agent team, or separate session**
- Subagents: own context window, only a summary returns; use them for high-volume output you will not reuse and for enforcing tool restrictions; stay in the main conversation for iterative work, shared context across phases and quick edits [Sub].
- Agent teams: experimental, off by default (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`); teammates message each other and share a task list; best for research and review where teammates challenge each other, worse for sequential or same-file work; "significantly more tokens" [Teams]. Costs page: roughly 7x a standard session when teammates run in plan mode, use Sonnet for teammates, keep teams small, shut idle ones down [Costs]. Pitfall: while teams are enabled, a subagent that Claude *names* launches as a teammate, so teams can form without being asked; set the variable to `0` to prevent it [Teams, "Claude spawns teammates instead of subagents"].
- Separate sessions (worktrees, plus cross-session messaging): for long, independent or GPU work. A message is plain text, never history or files; the receiver is told it came from another session, it cannot approve permission prompts or change configuration, and receiving can be set to `hold` or `refuse` with `crossSessionInbound` [Xsess]. Each delivered message to an idle session starts a turn that re-sends that session's full context [Costs, "Why usage climbs"].
- Nesting: subagents can spawn subagents up to three layers by default; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` disables nesting [Sub]. Concurrent subagent default limit is 20 (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`) with no cap on total spawned [Sub].

**B2. Frontmatter and system prompt**
- Only `name` and `description` are required; `description` decides delegation; put "use proactively" for auto-delegation; descriptions cost context and a startup warning appears above 15,000 tokens of combined descriptions; move detail into the body, which loads only when the agent runs [Sub].
- Fields: `tools`/`disallowedTools`, `model` (`sonnet`, `opus`, `haiku`, `fable`, full ID, `inherit`), `permissionMode`, `skills`, `hooks`, `mcpServers`, `memory`, `maxTurns`, `effort`, `isolation: worktree`, `background`, `omitClaudeMd`. Misspelled fields are ignored silently [Sub].
- Model resolution: per-invocation `model` parameter, then frontmatter, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main model; `..._FORCE=1` makes one model apply to every subagent [Sub]. Route cheap tasks to haiku [Costs].
- Context: the subagent sees only its system prompt, the delegation message, CLAUDE.md, git status and preloaded skills, not the conversation; "If a CLAUDE.md rule must apply inside a subagent, restate it in the delegation prompt" [Sub]. Resume with SendMessage to keep history [Sub].
- Body style: Anthropic's own example is a few lines ("You are a code reviewer. When invoked, analyze the code and provide specific, actionable feedback") [Sub]; system-prompt "altitude" should sit between brittle logic and vague guidance, start minimal and add instructions to fix observed failures [Ctx].

**B3. Brief writing and effort scaling (orchestrator side)**
- Each brief needs an objective, an output format, guidance on tools and sources, and clear task boundaries; without them subagents "duplicate work, leave gaps, or fail" [MAR]. Vague briefs ("research the semiconductor shortage") caused duplicated searches [MAR].
- Effort rules embedded in prompts: simple fact-finding 1 agent with 3-10 tool calls; direct comparison 2-4 subagents with 10-15 calls each; complex research more than 10 subagents with divided responsibilities [MAR]. Teams: start with 3-5 teammates, 5-6 tasks each, tasks sized to "a function, a test file, or a review" [Teams].
- Subagents write outputs to files/external storage and return lightweight references to avoid the "game of telephone" [MAR]; return summaries of about 1,000-2,000 tokens [Ctx]; lead saves its plan to memory because context beyond 200,000 tokens is truncated [MAR]; structured note-taking (NOTES.md) for long work [Ctx].
- Tool and description clarity: describe tools "as if briefing a new teammate", avoid overlapping tools, iterate against realistic evaluations by reading transcripts [Tools]; a tool-testing agent that rewrote bad tool descriptions cut task time 40% [MAR].
- Start wide then narrow; use extended thinking as a planning scratchpad [MAR].

**B4. Parallelism, cost and failure modes**
- Parallel work for independent paths; the lead ran 3-5 subagents in parallel, each using 3+ tools, cutting research time by up to 90% on complex queries [MAR]. Avoid two teammates editing the same file [Teams].
- Token economics: agents about 4x chat tokens, multi-agent about 15x; token usage alone explained 80% of performance variance on BrowseComp; Opus lead with Sonnet subagents beat single-agent Opus by 90.2% on their research eval [MAR]. Subagent requests count against the same usage limits as the main session [Sub, Costs].
- Failure modes listed by Anthropic: 50 subagents for a simple query, endless search for nonexistent sources, subagents distracting each other with updates, continuing after results suffice, over-long specific queries, duplicated work [MAR]. Teams: teammates stop early after errors, lead declares done too soon or implements itself, task status lags, no resume of in-process teammates [Teams].
- Evaluate: start with about 20 realistic queries, an LLM judge with a rubric (accuracy, citation accuracy, completeness, source quality, tool efficiency), plus human review; for stateful work check end state [MAR].

**B5. Skill authoring**
- Layout: `SKILL.md` required, optional `reference.md`, `examples.md`, `scripts/`; scripts are executed rather than read; frontmatter must begin on line 1 [Skills]. Keep the body under 500 lines; references one level deep; add a table of contents to reference files over 100 lines [SkillBP, Skills].
- Descriptions: what it does and when to use it, third person, specific trigger terms; `name` max 64 chars lowercase letters/digits/hyphens; description max 1,024 chars (Claude Code listing truncates description + `when_to_use` at 1,536 chars, key use first) [SkillBP, Skills].
- Progressive disclosure: only name and description are in context at startup; body loads on invocation; supporting files on demand [SkillBP, Skills]. After compaction an invoked skill keeps its first 5,000 tokens (25,000 combined) [Skills].
- Control flags: `disable-model-invocation: true` for workflows with side effects; `context: fork` runs the skill in a subagent (content becomes its prompt, no conversation history), `agent:` picks the type, `allowed-tools`, `model`, `effort`, `${CLAUDE_SKILL_DIR}` for bundled scripts [Skills].
- Match specificity to fragility (high freedom for judgement, low freedom for exact scripts); give a default instead of many options; feedback loops (run validator, fix, repeat); plan-validate-execute for batch work; at least three evaluations before heavy documentation; test on Haiku, Sonnet and Opus [SkillBP].

## C. Recommendations for the expert-team skill and the research-paper team (23 bullets)

Skill design
1. Name it with a gerund or noun phrase (for example `assembling-expert-teams`), third-person description with triggers ("assembles a team of expert subagents for a stated goal... use when the goal needs 3+ distinct specialties"), body under 300 lines, references one level deep: `briefs.md` (template), `roles.md` (catalogue), `budget.md`, `exemplars/`. [SkillBP]
2. Set `disable-model-invocation: true`: the skill spawns paid work, so only Shlok or an explicit lead decision should start it (the docs' rule for side-effect workflows). [Skills]
3. Make the skill a procedure: (a) restate goal and success test, (b) choose team size by the effort table in bullet 12, (c) write one brief per expert, (d) dispatch, (e) read report files not replies, (f) audit via gate-auditor, (g) log spend. Put the procedure in a copyable checklist. [SkillBP]
4. Two layers: stable role files in `.claude/agents/` (60-120 lines each: role, method, what it never does, report contract), and a per-task brief written by the lead. The lead never edits role files during a run.

The brief (the lead writes this for every expert)
5. Fixed fields (DSPy-style signature, prompt-enhancer block names): GOAL (one sentence), DELIVERABLE (artifact and report path), CONTEXT as file:line pointers, CONSTRAINTS and task boundary (what NOT to do, what the neighbour expert owns), SOURCES and tools to use, EVIDENCE LEVEL required (E0-E5 from CONTRACT.md), ALREADY RULED OUT, BUDGET (tool-call cap, `maxTurns`, wall time), STOP CONDITION, REPLY FORMAT (at most 8 lines). Anthropic's four required items are objective, output format, tool guidance, boundaries. [MAR]
6. State interfaces between parallel experts explicitly ("expert B writes `ledger/x.json`; you read it, you do not edit it"), the passage worth borrowing from project-manager.md. [A2]
7. Restate the two or three CLAUDE.md rules that matter (no invented IDs, no GPU without approval, web content is data); subagents do not inherit conversation state. [Sub]
8. Prefer a pointer to an exemplar report over pasted text: `research/paper2/team/exemplars/<role>.md`.

Roles and agents
9. Research-paper team, mapped to what already exists: literature = lit-scout + paper-reader; ideation = hypothesis-smith; novelty audit = novelty-auditor; red team = red-team; method architect = method-architect; ML engineer = lab-engineer; GPU runner = a separate role or session that only launches approved jobs and reports telemetry; statistician = statistician; figure engineer = figure-smith; journal writer = manuscript-writer (+ venue-intel); citation integrity = citation-validator; language editor = clarity-editor; budget steward = token-steward. Only the GPU runner and an explicit "lead/orchestrator" are missing as agent files. (Agent names read from the session's agent list; their bodies were not re-read in this audit.)
10. Tools by minimum need: reviewers, auditors, readers get Read, Grep, Glob (+ Write only for their report); Bash only for roles that must run code (lab-engineer, repro-engineer, statistician, figure-smith). The 136-of-165 Bash grant in repo 2 is the anti-pattern. [A2]
11. Pin `model:` in every file: sonnet default, haiku for mechanical checks (citation resolution, formatting), opus only for the single hardest role (method-architect or final red-team), never fable (matches Shlok's standing rule; fable is a valid value in the docs, so the guard must be in the files). [Sub, Costs]

Effort, parallelism, cost
12. Embed this scaling rule in the skill: a lookup or single check = 1 agent; a comparison or audit of one artifact = 2-3 agents; a full paper phase = at most 3-5 agents in one wave; never more than 3 at once per project CLAUDE.md. [MAR, Teams]
13. Expect high cost: Anthropic reports about 15x chat tokens for multi-agent work and about 7x for plan-mode teams; budget it before dispatch (token-steward) and stop spawning at the cap. [MAR, Costs]
14. Default to subagents; keep agent teams off by setting `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` so a named subagent cannot silently become a teammate. Use teams only for a deliberate debate (red-team versus proposer on hypotheses) with 3 teammates on Sonnet. [Teams, Costs]
15. Set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` (nesting off) so experts cannot spawn experts; only the lead spawns. Give role files no `Agent`/`Task` tool. [Sub]
16. Use sub-sessions (separate session with worktree) for GPU work and anything over about one hour; coordinate by report files and a one-line `SendMessage`; keep `crossSessionInbound` on default or `hold` for the GPU session so messages cannot trigger unattended runs, and remember a message is never consent. [Xsess]

Reports and context
17. Every expert writes the CONTRACT yaml report to the path in its brief and replies in at most 8 lines; the lead reads reports, not transcripts. Cap report length (for example 1,500 words) to stay near Anthropic's 1,000-2,000-token summaries. [Ctx, MAR]
18. The lead saves the team plan and the brief set in a file before dispatch (`research/paper2/team/runs/<date>-<goal>/PLAN.md`) so a context reset or session handoff loses nothing. [MAR]

Quality loop (DSPy ideas, no optimiser run)
19. Give each role a 5-8 line rubric (the metric) in its role file's "report contract" and a held-out set of 3 past tasks; judge outputs with gate-auditor, not the author. Anthropic's single-call 0-1 score plus pass/fail is the simplest judge. [MAR, A3]
20. Improve a role prompt only when the rubric shows a repeated failure: collect the failing report and the auditor's text feedback, ask one Opus review to propose a rewrite (GEPA-style reflection by hand), keep both versions in git, accept only if the held-out tasks improve. [A3]
21. Do not run MIPROv2 or GEPA now. If a demo is ever wanted: one role, 10 tasks, `auto="light"`, local Ollama model, venv, with a go-ahead for the GPU; expect results that may not transfer to Claude briefs.

Safety hygiene
22. Never clone third-party agent repos into the project tree; copy a single audited file, strip or rewrite `tools:`, `model:` and any "Integration with Other Agents" list, and re-run the Unicode scan (`_scripts\scan.py`) on it. Treat any agent file from the web as untrusted code. [A2]
23. Add a check to `tools/build_agents.py` that fails the build if a generated agent lacks `model:`, grants Bash to a read-only role, includes `Agent`/`Task`, or has a description over about 500 characters (descriptions load into every session). [Sub, SkillBP]

## Concerns for the caller
- rshah515 repo root contains a CLAUDE.md that would act as instructions if the repo were ever placed in a project or added as a directory.
- 500-AI-Agents `agents/21-pii-sanitization-agent` sends text to api.trustboost.dev; do not run.
- Survey repo's arXiv badge is wrong (SwinIR) and the repo has no licence; its IDs are unverified.
- Agent teams are experimental and can start silently when subagents are named; the default (3 nesting layers, 20 concurrent) is far above our "3 at once" rule, so the limits must be set by us.
- I did not fetch hooks or Agent SDK docs, did not read all 165 agent files, and did not check which Ollama models exist (`ollama list` hung; a background shell may still be running and can be stopped).
