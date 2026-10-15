# Resume prompt for the next DLM Discovery session

Paste the block below into a new Claude Code session opened in
`C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\dlm-discovery-resume-ca3357`.

```
Resume DLM Discovery. Run `graph-memory brief`, then read the top RESUME block of
research/progress.md (HANDOFF 2 overrides older blocks), then research/review/framework-v2.md
sections A and D.

Context: Paper 1 is a critical systematic review for ACM Computing Surveys. Its contributions
(decision D0011) are the design space tested on 47 models, a value-rule census (37 of 45
headline results use a non-plain or unstated value rule), the error budget as a taxonomy, and
open problems. EXP-001 stopped at its construct gate (D0016). EXP-003 (plain vs guided
consistency on UniDisc, card research/preregistration/EXP-003-value-rule-consistency.md
v0.3.2, signed) was left running unattended; its controls showed PC-1 failing (D0017), so
nulls are "not measurable".

Do next, in order:
1. Check the laptop restarted or not (System log events 41, 1001, 6008, 1074 since the last
   handoff) and the EXP-003 driver: runs/EXP-003/driver.log tail, STOPPED.txt or DONE.txt,
   the PID in runs/EXP-003/DRIVER_PID.txt. Restart it if needed with the Start-Process command
   in runs/EXP-003/IMPLEMENTATION.md section 4. Every GPU job runs through tools/gpu_guard.py.
2. When DONE.txt exists: run `python analysis/EXP-003/frozen_analysis.py main` with the
   .venv-eval interpreter, have gate-auditor reconcile every number against runs/EXP-003/,
   and record the result in the ledgers and progress.md, worded by the card's rules W0-W5.
3. Review and record the engineer's interpretation calls (runs/EXP-003/IMPLEMENTATION.md
   section 5) and the card correction about UniDisc's unconditional branch.
4. Novelty audit of EXP-003 before any claim is written.
5. Census: Claude Opus as coder B for the rest of the 150-eligible random sample
   (research/review/census/), Claude Sonnet as blind coder A on all; agreement, adjudication.
6. Then start the manuscript (manuscript-writer, then research-humanizer for clarity; the
   ACM LLM-use statement stays in).

Rules: at most 3 agents at a time; agents return text when report writes are refused and you
save it. Codex is unavailable until 2026-11-10 (D0015); when it returns, Codex tools resume one
read-only thread per 20 calls. No download size limit; hand off at about 850k context. Check the
weekly budget with get_usage before dispatching. Update progress.md and run
`graph-memory sync` before stopping.
```

Human tasks still open for Shlok: the 218-record screening sample
(`research/review/screening/HUMAN-SCREENING-INSTRUCTIONS.md`) and the 120 screener
disagreements (`research/review/screening/disagreements.csv`).
