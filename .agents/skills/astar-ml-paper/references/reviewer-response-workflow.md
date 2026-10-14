# Reviewer Response Workflow

How to process a review round from letter to delivered revision. This is the highest-
value part of the skill: most of the real work in getting a Q1 paper published is
handling reviews, not the first draft.

## Step 0 — Read the decision type correctly

- **Reject (flat)** — often a scope mismatch, not a fixable-comments situation. The
  editor may say "not mature enough" or "better fit elsewhere" with NO specific
  reviewer comments. Do not invent changes. Advise a better-fit journal and, if there
  is a real weakness (e.g. simulated results), address that before resubmitting.
- **Reject with reviewer comments** — the comments ARE the roadmap for the next
  submission even though this venue is closed. Address them, then submit elsewhere.
- **Major revision** — substantial work, same venue. Address everything thoroughly.
- **Minor revision** — close to acceptance. Be precise and complete; do not
  over-engineer. Each comment gets a clean, direct fix.

## Step 1 — Read the whole manuscript

`pandoc manuscript.docx -t markdown -o m.md` then read every line. Locate every table,
equation, algorithm, and section heading with line numbers (`grep -n`). You cannot map
comments to locations you have not read.

## Step 2 — Number and map every comment

Create a table: comment ID (R1-C1...), the reviewer's exact words, the manuscript
location(s) it points at, and the severity. One comment can touch several locations.

## Step 3 — Verify each comment against the paper

Reviewers who flag inconsistencies are usually right. Recompute. Common real issues:
- Iso-accuracy claims where a method never reaches the target accuracy.
- Headline percentages that do not reproduce from the tables.
- A "% increase" vs "percentage-point increase" confusion.
- A hypervolume/Pareto claim over N objectives while the HV uses a lower-dimensional
  reference point.
- An algorithm with a naming error or missing detail.
- A baseline count that disagrees with the number actually defined.
- A cost model that ignores separately-priced components (input vs output tokens).
- A declarations section contradicting the body (code availability).
- Repetition across Results/Discussion/Conclusion.

See `references/numerical-consistency.md` for how to recompute and fix each.

## Step 4 — Brainstorm honest, internally-consistent fixes

For numerical holes, derive the corrected value from the numbers already in the paper
so the fix cannot contradict published cells. For method-detail holes, expand the
algorithm/setup to a reproducible level. For overclaims, soften to what the data
actually supports. Never defend a real hole with rhetoric.

## Step 5 — Write replacements in humanized Q1 prose

Apply `/humanizer` and `references/q1-writing-style.md` to every replacement. Keep the
author's plagiarism score intact: original wording, no copied phrasing, no em-dashes if
the author bans them.

## Step 6 — Produce the two deliverables

See `references/deliverables.md`. Change-instruction docx + Response-to-Reviewers docx.

## Step 7 — Cross-validate (do not skip)

Before delivering, run the consistency audit in `references/response-to-reviewers.md`:
every response claim maps to a change box, every change box maps to a real location,
and (once the author highlights) every claimed change is present AND highlighted in the
manuscript. Report gaps to the author before the professor/editor sees them.

## Multi-round reality

Papers commonly go through several rounds and even venue changes. Keep a running record
of what each round changed. Later reviewers may re-open earlier fixes; a correct earlier
change should not be reversed just because a new reviewer phrases things differently.
