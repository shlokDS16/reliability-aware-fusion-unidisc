# Census codebook v1.1 (amendment of v1, 2026-10-14)

v1 (`census-codebook-v1.md`) stays as the record; the 47-paper result v1 was coded under v1.
v1.1 applies to the full-corpus coding. Each amendment answers one item A-1 to A-10 in
`census-adjudication-notes.md`; the decision and reason are given. Fields not mentioned are
unchanged from v1.

**A-1 (F3).** Diversity metrics for images count: recall (as in precision/recall), LPIPS-based
diversity, Vendi score, and FID only when the paper presents it as a diversity measure. Quality-only
scores (classification accuracy score, CLIP score, Inception score) do not. "Explicitly pairs": the
diversity number is for the same model, sampler setting and task as F1, and is either in the same
table or figure or in an appendix item that the main text cites for that experiment. Reason: the
census asks whether a reader can see the diversity cost of the headline setting; image papers
report it with recall, not entropy.

**A-2 (F1).** Adopt coder 2's policy A1: skip abstract numbers that are speed-only or
likelihood-only; take the first generated-sample metric for the paper's own method. Main task:
the task the abstract names first. When the first table is an adaptation or ablation table, use
the first table reporting the final method. Multi-task unified models: the first generation task
named in the abstract (text-to-image before understanding when both are named). When a table has a
plain and a guided or best-of row, the headline is the row the abstract or text quotes; if none is
quoted, the best row of the method. Reason: reproducible choice that matches what readers see first.

**A-3 (F2 U, "states").** A value rule counts as stated if (a) the experiment section or caption
states it, or (b) a method-level sampler definition states it and the experiment section refers to
that definition or says the default sampler is used, or (c) a hyperparameter table lists it.
Process-level samplers (tau-leaping, Euler CTMC, ODE integration) are U only with an explicit
statement that no temperature, truncation or guidance is applied. Reason: separates "said" from
"inferable".

**A-4 (F2 A).** A per-step argmax or projection inside the sampling loop is A. The final rounding
or nearest-embedding step of a continuous channel is recorded as a note, not as A.

**A-5 (F2 variants).** Code the headline row only (A-2); list other variants of the paper's own
sampler shown with it in the notes field.

**A-6 (F2 T).** T means a stated temperature other than 1, with the value recorded in F2_detail;
values above 1 are recorded as "T>1" in the detail. Annealing without a stated value is NS for the
temperature part. Reason: the census records departures from plain sampling in both directions.

**A-7 (F2 evidence).** Theorems or analyses about a decoding rule are not a statement of the
experimental value rule. A blanket experimental statement ("zero temperature for all
experiments") is.

**A-8 (F4).** A hyperparameter or results table with a step-count (or NFE, or tokens-per-step) row
and a generated-sample metric counts as a sweep. Exactly two settings is Partial. For multi-task
models the sweep must be on the F1 task's metric.

**A-9 (F5, F6).** Stated: an experiment-level sentence, caption or table entry saying the rule
is the same across the sweep, or a single stated rule with the text saying only the step count
varies. A method-level default without such a sentence is Not stated. F6 for multi-task sweeps:
code for the F1 task only.

**A-10 (F1 qualitative).** New code F1 = QL for papers whose only generated-sample evidence is
qualitative (samples shown, no metric). F2 is coded as usual for QL papers; F3 to F6 are NA.
