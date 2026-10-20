# Item 12: three tool rules for extraction (drafted for the human author, 2026-10-20)

Source of the questions: `analysis/extraction/stageA-gaps-log.txt` Q1-Q3 (tools built and tested, nothing drawn).
These are the orchestrator's recommendations only. Nothing is applied until you choose and a decision row is
written. None of them blocks Stage A (12 development records); Q1 must be settled before the gate (Stage B), Q2
and Q3 before Stage A results are scored.

## Q1. Should a failed number or sign reject the table cell it cites? (G1)

Today G1 ("evidence located") fails an entry only when a check names that entry (table, cell, row, prose). Value
errors (a number not in the cited cell, wrong column, wrong row label) and sign errors name the unit, not the
entry, so they do not lower G1; they are counted by M-val and M-sign.

| Option | Effect |
|---|---|
| (a) keep as is | G1 measures "found the right place"; M-val and M-sign measure "read it right". Matches the v0.5 gate simulations. |
| (b) a value or sign fail also fails every entry its unit cites | One error is counted twice (G1 and M-val); G1's pass rate drops and the v0.5 operating characteristics no longer hold (gate re-simulation needed). |
| (c) report G1 both ways, gate on one | Transparent; the gate keeps one definition. |

**Recommended: (c), gating on (a)'s definition.** The G1-under-(b) figure is printed beside it as report-only, so a
reader sees how often a located cell was misread. Also: a record rejected at first pass only for block or session
findings counts as **not** accepted at first pass (the conservative reading), reported by cause.

## Q2. When does a field count as "searched"? (E1 coverage)

The brief marks fields [Q] (quote needed for a positive value, "searched" otherwise) in prose with several variants;
there is no machine-readable list, "positive value" is undefined for `other`, `NA`, numbers and lists, and "unclear"
is missing from the negative list.

**Recommended:** method-architect writes one field table (field id, record path, positive values, negative values,
whether NA needs a reason), red-team checks it against the brief, and ex_validate reads it. Defaults to put in that
table unless you say otherwise: `unclear` counts as negative (needs "searched"); `other`, any number and any non-empty
list count as positive (need a quote); `NA` needs neither quote nor "searched" when the brief's skip logic makes the
field not applicable, and needs "searched" otherwise.

## Q3. How are derived fields filled? (--fill-derived)

Derived fields (parsed numeric values, rq_class, metric and benchmark ids from the lookups, K15 matched flag, M14/M15
from the draw manifest) have rules in several versions of the plan; where the filled values live and what happens
when a filled value differs from an extractor's value is not stated.

**Recommended:**
1. Filled values go to a separate file next to each record file (`*-derived.jsonl`), written after the pass-2
   re-run; extractor-written values are never overwritten.
2. A filled value that differs from an extractor-written one is logged as a finding and goes to EC (not a reject).
3. Only QA items that still exist in the v0.5 item set are scored; method-architect maps v0.2 s7.1, QA3c, QA7n and
   the D12 levers to v0.5 items (or retires them) in one table.
4. Unmapped strings go to one queue file (string, field, record, count) that you review when updating the lookups.

## Your answer

Reply "item 12 rec" to accept all three, or name the option per question (for example "Q1 a, Q2 rec, Q3 rec").
