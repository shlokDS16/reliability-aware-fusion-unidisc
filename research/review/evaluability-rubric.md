# Claim-evaluability rubric (v0.2, 2026-10-14; under reliability test, not yet frozen)

Purpose: record which kinds of advantage a paper's abstract asserts and, for each, whether the
paper's own tables contain the comparison needed to check it. The rater sees the abstract, every
table and figure caption, and the tables as text. The rater does not judge whether a claim is true.

## Change log
- v0.1 failed its preset reliability threshold on 40 papers (claim type kappa 0.57, criterion
  weighted kappa 0.29, uncertainty kappa 0.64; `reliability/`). Cause: abstracts carry several
  claims and the two raters often chose different "primary" ones; the three-level criterion mixed
  several conditions, some not observable in tables (hardware, training budget).
- v0.2: every claim type is coded separately as asserted or not; each criterion is split into
  yes/no items that can be seen in a table or caption; unobservable conditions are removed.

## Step 1. For each claim type, is it asserted in the abstract? (yes or no, all six)

Judge from the abstract only. A type is asserted if the abstract states that advantage for the
paper's own method or model, with or without a number.

| Code | Asserted if the abstract says | Not enough |
|---|---|---|
| CT1 steps | fewer denoising steps, sampling steps, forward passes or function evaluations; or a reduction expressed in steps | "efficient" or "fast" with no mention of steps |
| CT2 time | faster in time, a speed-up factor, higher throughput, lower latency | fewer steps only |
| CT3 inference quality | better output quality or accuracy from a technique applied at generation time without training (a sampler, decoding or remasking rule, guidance, constrained decoding; "training-free") | quality gains from a method that trains anything |
| CT4 training quality | better output quality or accuracy from anything that involves training (a new model, objective, fine-tuning, reinforcement learning, distillation, architecture) | a quality gain with no training involved |
| CT5 unification | that tasks, modalities or objectives help each other, or that unifying them improves performance | reporting results on several tasks without saying one helps another |
| CT6 versus autoregressive | matches, approaches, is competitive with or outperforms autoregressive models, named as a class or by a specific autoregressive model | comparison only with other diffusion models |

Several types can be `yes` for one paper. A paper with no method (pure analysis, theory, benchmark
or dataset) has all six `no`.

## Step 2. For each asserted type, answer its items (yes or no) from captions and tables

Answer `yes` only if you can point to the table or figure. If the relevant table is cut off in the
extract, answer `no`. A comparison shown only in a figure counts if its caption names what is compared.

| Type | Item a | Item b |
|---|---|---|
| CT1 | a baseline sampler (not the proposed method) is reported at two or more different step or forward-pass counts on one task and metric | at least one of those baseline counts is no more than twice the proposed method's count on that task |
| CT2 | a time, throughput or latency figure for the proposed method appears in the same table row as a quality metric | the same table gives the time, throughput or latency of a baseline as well |
| CT3 | a table compares the same model on the same task with and without the technique | that table also gives steps, forward passes or time for both arms |
| CT4 | a table compares the proposed model or training method against a version of itself without the proposed component (an ablation) | that ablation is on a benchmark that also appears in the paper's main results table |
| CT5 | a table compares the model trained with and without the other task, modality or objective, or shared against decoupled pathways | the comparison reports a metric for each of the two task kinds involved |
| CT6 | a results table includes an autoregressive model whose parameter count is stated and within a factor of two of the diffusion model's | the diffusion model's number of steps or forward passes is stated in that table or its caption |

Items for types not asserted are `na`.

## Step 3. Uncertainty
`yes` if any results table reports repeated runs (three or more seeds), a standard deviation, a
confidence interval or a significance test that the paper defines. An undefined plus-minus is `no`.

## Output, one JSON object per paper
```json
{"record_id": "...",
 "claims": {"CT1": {"asserted": "yes|no", "a": "yes|no|na", "b": "yes|no|na"},
            "CT2": {...}, "CT3": {...}, "CT4": {...}, "CT5": {...}, "CT6": {...}},
 "uncertainty": "yes|no",
 "evidence": "table or figure labels used, at most 20 words"}
```

## Reliability threshold for v0.2 (set before round 2 is rated)
On a fresh 40-paper sample (`reliability/round2/`, no overlap with round 1): Cohen's kappa of at
least 0.60 for `asserted` pooled over the six types, and at least 0.60 for the evaluable flag
pooled over claims both raters marked asserted. Item-level and per-type figures are reported too.
If either pooled figure is below 0.60 the rubric is not adopted in this form.

## How the items are used
An asserted claim is **evaluable** if both of its items are `yes`. Hypothesis E1 concerns the share
of asserted claims that are evaluable, per claim type. The items are a floor: a paper can satisfy
them and still be confounded, and a control described only in running text is not credited here
(a stated limitation of rating from tables).
