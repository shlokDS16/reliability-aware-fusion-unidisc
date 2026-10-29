# Technical Debt

Shortcuts, TODOs, known limitations, and refactor opportunities.

| Added | Item | Why it exists | Cost if ignored | Trigger to fix |
|---|---|---|---|---|

- 2026-10-30: runner env-lock.txt is empty because it calls pip, which the venv lacks; switch it to importlib.metadata before the release gate (A6 LG audit F3). Workaround committed: runs/P2-ENV/pip-freeze-2026-10-30.txt.
- 2026-10-30: baselines.py resolves --out-dir relative to a cwd that UniDisc changes; make it absolute at parse time.
