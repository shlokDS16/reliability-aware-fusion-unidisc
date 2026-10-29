# Lessons Learned

Anything that would save a future engineer time. Append only.

Format: **[date]** - what happened, what it cost, what to do instead.

**[2026-10-14]** Run the novelty audit and a full-text prior-art read before the method-architect formalises a "new term", not after: the selection term took one opus formalisation and one opus red-team to fall, and the decisive prior art (2605.12522, 2510.04525) was findable by search. Also: never silence `git add` errors (`2>/dev/null`); one missing path aborted a commit and the primers went uncommitted for an hour.

**[2026-10-15]** Preregistration paid off twice: EXP-001's construct gate stopped a 27-hour run that would have measured nothing, and the red-team's toy models caught a bias (instance-weighted noun ratio) before any data. Run cheap feasibility gates (PG-1, PG-V) as soon as code exists, before polishing the full design through many review rounds. Batch tools that call an external model must be checked against its quota and session rules before the first run.

- 2026-10-30: UniDisc's loader changes the working directory, so any relative --out-dir in a process that loads UniDisc lands under runs/env-2026-10-14/smoke_unidisc/. Pass absolute output paths.
- 2026-10-30: the venv has no pip; record the environment with importlib.metadata (runs/P2-ENV/pip-freeze-2026-10-30.txt). The runner's env-lock.txt files are 0 bytes for that reason.
- 2026-10-30: transformers reads its default cache_dir from an import-time global (transformers/utils/hub.py TRANSFORMERS_CACHE); a test that wants an empty HF cache must patch that too, not only HF_HUB_CACHE.
