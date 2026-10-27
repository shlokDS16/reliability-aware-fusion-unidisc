# Master brief (2026-10-27): new high-impact paper on multimodal masked diffusion, built by an expert agent team

Written from Shlok's instructions of 2026-10-27 (improved for agents, as he asked). Shlok's own words are the
authority; where this brief and his words differ, follow his words.

## 0. Goal and deadline
- Replace the screening-based review with a **new, novel paper with substantial original results** on multimodal
  (text, image, audio/speech) **masked discrete diffusion** models, for a high-impact Elsevier journal in the style of
  **Information Fusion** (two exemplar papers: `1-s2.0-S1566253526004987-main.pdf` (Information Fusion) and
  `1-s2.0-S1574013725001571-main.pdf` (Computer Science Review), in the project root). Deadline: **Fri 31 Oct or Sat
  1 Nov 2026**. Daily follow-up with Shlok; he sleeps at night and the work continues unattended.
- **Remove screening entirely** (no PRISMA screening narrative, no screening agreement statistics). The previous review
  can supply related-work knowledge, taxonomy and the design space, never a screening method.
- The paper must present **real, reproducible, novel results** with **exemplary figures** (real model outputs:
  step-by-step unmasking of text and images, text-to-image/text-to-audio samples, comparison grids labelled with
  measured metrics, ablation plots), like the figures in Yang et al. (CSUR 2023) and the exemplar papers. Nothing is
  drawn or edited to look like a result; every number comes from a committed script and run directory.
- **Human in the loop** is a core principle: Shlok (and the professor) approve the topic, the claims and the figures.

## 1. Hard rules
- **AI only in the Declaration on the use of AI** at the end of the paper (it may be detailed: where AI was used,
  including writing). Nowhere else in the paper any hint of AI. This is Shlok's explicit decision.
- Never invent a number, citation or result. Verify every reference (Crossref/arXiv). Novelty audit before any claim.
- Token and model rules from `~/.claude/CLAUDE.md` ("Token budget rules"): Opus lead, Sonnet implementers, Haiku for
  mechanical work, **no Fable**, explicit `model` on every agent; at most 5 agents working at once; session cap set at
  start and re-checked each phase; **hand off to a fresh session at about 250k context, never past 850k**; a
  context-watch step at every phase boundary (get_usage on each running session).
- GPU: RTX 5070 Ti laptop, 12 GB. It crashed twice under sustained load (memory `laptop-gpu-crashes`): short runs,
  checkpointing, telemetry, and resumable jobs. Call `request_keep_awake` for overnight work. Network switches to
  mobile data around 23:00 and VIT Wi-Fi drops at 00:15: make downloads resumable. Cloud spend needs Shlok's yes.
- Codex/ChatGPT discussions: **one thread**, run from this project folder, resumed by id (memory `codex-one-thread`).
  Shlok says the Codex app is congested: list the sessions this project created and **archive** them (do not hard-
  delete files; tell Shlok which to delete if archiving is not possible).

## 2. Phase plan (each phase ends with a commit, a HANDOFF line in `research/progress.md` and a budget check)
1. **Setup (first hours).** `graph-memory brief`/`sync` (graphify) for context; read memories on GPU, tokens,
   downloads; read this brief, `research/paper2/professor-sources/README.md`, `GEMINI-FRAMEWORK-2026-10-27.md`
   (screening parts are void; verify its claims), `related-arxiv-2026-10-22.md`.
2. **Expert team design.** Study and security-check the repos Shlok gave:
   https://github.com/ashishpatel26/500-AI-Agents-Projects , https://github.com/rshah515/claude-code-subagents
   (security check required before using any file), https://github.com/stanfordnlp/dspy (prompt optimisation; combine
   with the `anthropic-skills:prompt-enhancer` skill), https://github.com/AnasHXH/Connecting-LLMs-to-Diffusion-Models-A-Survey .
   Research current best practice for Claude Code subagents and sub-sessions. Build (a) a **global, reusable skill**
   that assembles an expert team for any goal (research, website, app, startup, learning), where a lead "big brain"
   writes each expert's brief from the task, and (b) a project-specific team for this paper in `.claude/agents/`
   (literature/taxonomy, ideation, novelty audit, red team, method architect, ML engineer, lab/GPU runner,
   statistician, figure engineer, journal-style writer, citation integrity, language editor, context/budget steward).
   Shlok may supply individual agent instructions: incorporate them when given.
3. **Learn the target style.** Read the two exemplar papers and recent Information Fusion papers (Chrome; Shlok logs
   in via VIT e-gateway/ScienceDirect when needed): structure, figure types, result presentation, writing style.
   Read the journal's guide for authors and follow it strictly.
4. **Topic and proposal.** With the team: 3-5 candidate ideas on multimodal masked diffusion (Omni-Diffusion,
   LaViDa/LaViDa-O/Sparse-LaViDa, Apple tri-modal MDM, MMaDA, UniDisc), each with closest prior work, novelty audit,
   red-team verdict, GPU cost on 12 GB, and the figures it would produce. Shlok chooses (human in the loop).
5. **Experiments.** Preregister, run on the laptop GPU (small/4-bit models), save every output; produce figures.
6. **Writing.** Journal structure; strong introduction with recent work; results with figures; AI only in the
   Declaration. Language quality: improve the `research-humanizer` skill using `C:\Users\Shlok\Downloads\research-humanizer.zip`
   and the exemplar papers' style; find and security-check grammar/paraphrase tools (repos, plugins, skills; a
   Grammarly login via Chrome if Shlok provides it) to replace the Paperpal pass he can no longer run.
7. **Audit and package.** Hostile review, citation check, number reconciliation, DOCX/PDF, cover letter.

## 3. What Shlok wants reported at the end
Everything added (skills, plugins, agents, repos used, with security-check results), budget used, and what is left.
