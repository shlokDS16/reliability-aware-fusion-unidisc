# Master prompt for this project (v2, replaces the earlier paper-build prompt)

Paste the block for the current phase into a fresh session. Each block assumes `CLAUDE.md` has
loaded and starts from `research/progress.md`.

## Resume (any session)
```
Resume DLM Discovery. Run `graph-memory brief`, read the RESUME block of research/progress.md,
check plan usage, then continue from the first unticked item of the current gate. Follow
research/FRAMEWORK.md sections 5 to 7. Dispatch at most 3 subagents at a time and log each one in
the dispatch table. Before you stop: update progress.md, run gate-auditor if a gate's items are all
ticked, then `graph-memory sync --note ... --next ...`.
```

## Gate 1: frontier map
```
Goal: complete Gate 1. (a) lit-scout: inventory every outbound link of VILA-Lab/Awesome-DLMs at
its current HEAD into the papers ledger and pin the SHA. (b) paper-reader: full claim matrix for
MMaDA (arXiv 2505.15809v2) against Gen-Verse/MMaDA and Gen-Verse/dLLM-RL at pinned SHAs.
(c) lit-scout then paper-reader: the closest 10 works for candidates T1 and T2 in
research/reports/lit-scout/2026-10-13-frontier-map.md, read in full. Finish with an anomaly list
in research/reports/anomalies.md. No novelty statement from abstracts alone.
```

## Gate 2: hypothesis selection
```
Goal: complete Gate 2. hypothesis-smith writes 3 or more candidates with competing mechanisms and
a prediction table. For each: novelty-auditor verdict, red-team report, and a Codex review through
codex:codex-rescue. Score with the rubric in the blueprint (section 3, candidate-scoring). Present
the ranked shortlist with the decisive pilot and its GPU-hours, and ask the user to choose.
```

## Gates 3 to 6: preregister, reproduce, pilot, generalise
```
Goal: Gates 3 to 6 for hypothesis <H-id>. experiment-designer and statistician freeze the card;
red-team signs it. repro-engineer reproduces the baseline and measures the quantisation gap.
lab-engineer runs the decisive pilot. If the preregistered threshold is missed, record it and
switch to the backup hypothesis; do not reinterpret. If it is met: seeds, second model or dataset,
ablation-robustness, statistician intervals. All runs through `python -m dlm.run`.
```

## Gates 7 to 9: venue, manuscript, release
```
Goal: Gates 7 to 9. venue-intel fixes the venue from official pages and analyses 5 accepted papers.
figure-smith builds the figure set from run artifacts and inspects every render. manuscript-writer
drafts with the astar-ml-paper skill; clarity-editor edits with research-humanizer;
citation-validator verifies every reference; red-team, Codex and NotebookLM review; gate-auditor
runs the number audit and the clean-room reproduction.
```

## Standing requests to the user
Exact steps for anything only the user can do (logins, gated downloads, eGateway PDFs, disk space)
go in `research/SETUP_STEPS.md`, written against the live site or CLI on the day they are needed.
