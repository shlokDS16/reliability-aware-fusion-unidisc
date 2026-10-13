# Q1 Paper Structure (IMRaD and beyond)

The section skeleton a Q1 methods/systems paper is expected to have, and what each
section must contain to survive review.

## Standard order

1. **Title** — specific, informative, includes the method name and the problem.
2. **Abstract** — 4-part structure (see q1-writing-style.md).
3. **Keywords** — 5-7, mixing the problem domain and the method family.
4. **Introduction**
   - Open with a concrete, quantified motivation (real cost numbers, real scale).
     Vague "LLMs are impressive" openings get flagged. Lead with the problem's size.
   - State the gap: what existing lines of work do and what they all miss.
   - State the contribution as a precise question the paper answers.
   - End with a paper-organization paragraph ("Section 2 reviews... Section 3 formalizes...").
5. **Related Work / Background**
   - Group by approach, not chronology.
   - Include a comparative summary table (methods × properties) — reviewers love this.
   - Give the single closest competitor its own detailed treatment (and a diagram).
   - End with an explicit "critical gap" that names each prior method and says why it
     does not solve the problem. This is where novelty is won or lost.
6. **Problem Formulation**
   - Notation table / definitions first, each symbol introduced with its equation.
   - Formal problem statement with numbered equations.
   - A Proposition + proof sketch if any theoretical claim is made. Even an informal
     but rigorous argument beats hand-waving; technical reviewers demand it.
7. **Method / Framework**
   - Architecture overview paragraph + an architecture diagram (see figures ref).
   - Each component in its own subsection.
   - **Algorithm 1** as numbered pseudocode with explicit inputs, outputs, fitness
     computation, update rules, and archive/termination. Add a concrete one-pass
     worked example so the method is tangible.
   - Justify every hyperparameter and design choice (why this value, not just what).
8. **Experimental Setup**
   - Datasets (named, public, with links/citations).
   - Model suite: exact versions, checkpoints, temperature, API settings, pricing.
   - Baselines: ONE consistent list, all defined at the same scope, same budget.
   - Evaluation metrics: exact formulas, and the reproducibility/code statement.
9. **Results**
   - Main table (accuracy/cost/latency or domain equivalent).
   - Statistical significance: means over multiple seeds, 95% CIs, hypothesis tests.
   - Per-metric analysis tables (e.g. CPT/APGR); every column named in the caption
     must actually appear in the table.
10. **Discussion / Limitations**
    - Interpretation, ablation reading, and explicit scenarios where the method gives
      little or no benefit.
11. **Conclusion** — one concrete takeaway + future work. Not a results re-list.
12. **Declarations** — Code availability, Data availability, Funding, Conflicts.
    These MUST be consistent with the body (a "Not Applicable" code statement while
    the body promises code release is an instant reviewer flag).
13. **References** — consistent style, strict alphabetical (Harvard) or citation-order
    (Vancouver).
14. **Appendices** — sensitivity analysis, extended tables (e.g. latency percentiles).

## Consistency invariants (check these every revision)

- Every figure and table is referenced from the body ("as shown in Figure X").
- Figure/table numbers are sequential and every reference matches. If you insert a new
  figure mid-paper you must renumber ALL later figures AND their in-text references —
  or append at the end to avoid renumbering (often the pragmatic choice mid-revision).
- Every equation is numbered; every in-text "Equation (n)" points to the right one.
- Every symbol used is defined once, at first use.
- Declarations match the body.
- Abstract numbers == results numbers == table numbers == conclusion numbers.
