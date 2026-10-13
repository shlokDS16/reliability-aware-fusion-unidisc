---
name: astar-ml-paper
description: >
  Build an A* machine-learning conference paper (NeurIPS, ICML, ICLR, IJCAI, AAAI, ACL) in LaTeX
  from verified experiment artifacts. Use when planning figures and tables, drafting or revising
  any section, typesetting equations or algorithms, filling the venue checklist, preparing the
  appendix, the rebuttal or the camera-ready, or checking that every number in the draft matches
  the raw runs. Adapted from the q1-research-paper skill for conference templates; use that skill's
  docx workflow only for journal resubmissions.
---

# A* ML conference paper

Conference reviewers decide in one read whether the claim is new, whether the evidence could have
come out otherwise, and whether they could reproduce it. Everything below serves those three questions.

## Golden rules
1. **Write from the ledgers.** An empirical sentence needs a run ID (`% run: X0012`), a background
   sentence needs a verified citation key. No ledger entry, no sentence.
2. **Numbers reconcile.** Abstract, introduction, tables, figures and conclusion give the same value
   with the same definition, recomputed from `predictions.jsonl` by a script. See
   `references/numerical-consistency.md`.
3. **Claims match intervals.** "Improves" needs an interval that excludes zero on a preregistered
   endpoint. Otherwise write "is comparable to" or report the null.
4. **Limits stay in.** Losses to a baseline, the quantisation confound, single-machine compute and
   failed directions are reported in the main text or a named appendix section.
5. **Prose passes through `research-humanizer`** for clarity, with its protected-content check. The
   venue's LLM-use statement is included and accurate.

## Order of work
1. Claim sentence and the strongest qualifying evidence (one paragraph, frozen at Gate 6).
2. Figure and table plan: one claim per panel, source run IDs listed (`paper/plan.md`).
3. Method (notation, equations, algorithms). 4. Experiments. 5. Related work as a difference
matrix turned into prose. 6. Limitations and broader impact. 7. Introduction. 8. Abstract and
title last. 9. Appendix, checklist, reproducibility statement. 10. Red-team review, then revise.

## Page budget (confirm against the current style file at Gate 7)
First page: problem, gap, one-sentence claim, teaser figure. Method about 2 pages, experiments
about 3.5, related work about 0.75, limitations about 0.25. The appendix carries proofs, full
protocols, extra ablations, per-dataset tables and the remaining figures.

## Figures (target 13 to 14 in total: about 6 main, the rest appendix)
Suggested set: (1) teaser showing the phenomenon, (2) method diagram, (3) main result with
intervals, (4) mechanism evidence, (5) ablations, (6) quality against compute; appendix:
(7) per-dataset breakdown, (8) seed variance, (9) robustness matrix heatmap, (10) quantisation
gap, (11) negative control, (12) failure cases, (13) sensitivity to hyperparameters,
(14) qualitative trajectories.

- matplotlib with one style file, vector PDF output, sizes set at final column width, fonts
  matching the template, a colour-blind-safe palette reused in every figure, identity encoded by
  colour and by marker or line style.
- Uncertainty drawn on every comparison and defined in the caption.
- After each render, open the PNG preview and check: no overlapping or clipped text, even spacing,
  legible at single-column width, legend off the data. Record the check next to the script.
- Captions state the takeaway first, then how to read the panel.

## Equations
`amsmath`, numbered, referred to with `\eqref`. Define each symbol where it first appears and keep
`paper/notation.md` as the single table of symbols. Introduce an equation with the question it
answers and follow it with what each term does; a referee should be able to re-derive every step
from the stated assumptions. Proofs go to the appendix with a two-line sketch in the main text.

## Algorithms: build up, do not dump
Use `algorithm2e` so the result matches the user's reference style (ruled box, vertical block
lines, numbered lines, Input, Output and Data headers, a named Function):

```latex
\usepackage[ruled,vlined,linesnumbered]{algorithm2e}
\SetKwInOut{Input}{Input}\SetKwInOut{Output}{Output}\SetKwInOut{Data}{Data}
\SetKwProg{Fn}{Function}{:}{}
\begin{algorithm}[t]
\caption{Score one denoising state}\label{alg:score}
\Input{$x_t$: partially masked sequence; $\theta$: denoiser}
\Output{$s$: per-position score}
\Fn{\textsc{Score}$(x_t,\theta)$}{
  $p \leftarrow f_\theta(x_t)$\;
  \For{each masked position $i$}{ $s_i \leftarrow \max_v p_i(v)$\; }
  \Return $s$\;
}
\end{algorithm}
```

Place Algorithm 1 (a primitive) where its idea is introduced, Algorithm 2 (which calls 1) where the
next idea appears, and the final algorithm, which composes the earlier ones by name, at the end of
the method section. Each algorithm is cited in the text next to the equation it implements.

## Tables
`booktabs`, generated from data files. Mean and interval over seeds, n stated, best in bold, second
best underlined, compute columns (parameters, function evaluations, wall time) beside quality.

## Before submission
- `gate-auditor` number audit and `citation-validator` pass with zero open items.
- Venue checklist answered with section pointers; anonymity checked (no names in PDF metadata,
  repo links anonymised); page limit met with the official style file unmodified.
- Two independent-model reviews (Codex, NotebookLM) and one `red-team` review resolved in writing.

## References
| File | Use |
|---|---|
| `references/numerical-consistency.md` | reconciling numbers across sections |
| `references/paper-structure.md`, `references/q1-writing-style.md` | journal-oriented guidance; conference rules above take precedence |
| `references/reviewer-response-workflow.md` | rebuttal: map each reviewer point to a concrete change or experiment |
