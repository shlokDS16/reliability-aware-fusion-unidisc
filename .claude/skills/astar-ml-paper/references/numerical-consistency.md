# Numerical Consistency

Technical reviewers check arithmetic. Every headline number must reproduce from the
tables, use one clear definition, and appear identically everywhere it is quoted. This
file is the checklist that prevents the most damaging class of reviewer comments.

## Golden procedure

1. **List every headline number** in the paper (abstract, intro, results, conclusion,
   any comparison table cell).
2. **Recompute each from the table cells** in Python. If it does not reproduce, it is
   wrong — fix it, do not defend it.
3. **Pin each number to an explicit formula + baseline + dataset** and state that
   formula once in the metrics section.
4. **Propagate the corrected number to EVERY location** it appears. The abstract and a
   buried comparison-table cell are both locations. Miss one and a reviewer catches it.

## The three classic traps

### 1. Iso-accuracy that isn't

Claiming "all methods compared at 95% of the strong model" when some method never
reaches that accuracy. The cost reported for that method was measured at a lower
accuracy, so the comparison is invalid.

Fix: set the operating target per dataset to the tightest accuracy every compared
method actually reaches. Mark any method still short of the stated target (a dagger)
and state that its reported cost is a LOWER BOUND, because reaching the target would
require routing more to the expensive model and cost more.

```python
strong = {"MMLU":87.3,"GSM8K":93.1,"WildChat":100.0}
for ds,s in strong.items():
    print(ds, "95% target =", round(0.95*s,1))   # check each method reaches it
```

### 2. Percentage vs percentage-point

"19.7% accuracy improvement" is ambiguous and often unreproducible. An accuracy gain at
matched cost should be reported in **percentage points** (arithmetic difference of two
accuracies), not as a relative percent, unless you explicitly define the relative form
and its baseline.

```python
# percentage points (preferred for accuracy deltas):
pp = coral_acc - baseline_acc            # e.g. 86.2 - 81.4 = 4.8 pp
# relative percent (must state baseline if used):
rel = (coral_acc - baseline_acc)/baseline_acc*100
```

### 3. Wrong reduction denominator

A cost or latency reduction is (baseline − method) / baseline, against a NAMED
baseline. Recompute; a plausible-looking number is often off.

```python
cost_red = (nacu_baseline - nacu_method)/nacu_baseline*100   # e.g. (0.548-0.376)/0.548 = 31.4%
lat_red  = (lat_baseline  - lat_method )/lat_baseline *100   # e.g. (1124-987)/1124 = 12.2%  (not 14.2)
```

## Dimensionality of multi-objective claims

If the paper claims N-objective optimization but the hypervolume/Pareto summary uses a
reference point with fewer than N coordinates, the extra objective is NOT in the HV.
State plainly: the search optimizes all N objectives (the non-dominated sorting and
archive use the full N-vector), but the HV indicator is a projection onto the two
plotted axes, with the reference point and per-axis normalization named. Soften any
"Pareto-dominates across all N objectives" claim to match the projection.

## Every-column-must-exist rule

If a table caption or section heading names two metrics (e.g. "CPT and APGR"), the
table must actually contain BOTH. If only one is present, either add the second (a
second table is fine) or rewrite the text. Derive the second metric from cells already
in the paper so it cannot contradict them:

```python
# APGR = fraction of the weak->strong gap recovered at a fixed budget
apgr = (method_acc_at_budget - weak_acc)/(strong_acc - weak_acc)
```

## Cost model completeness

If input and output tokens are priced differently (they are, on commercial APIs), the
cost equation must price them separately:
`c = price_in * tokens_in + price_out * tokens_out`.
For a locally-served model, state that its per-token cost is an amortized hardware cost
(GPU hourly rental / measured throughput) and apply it to both token types.

## Final reconciliation pass

Before delivering any revision, grep the manuscript for every headline number and
confirm they all agree:
```bash
grep -n "31.4\|19.7\|14.2\|12.2\|4.8" m.md   # every hit must use the corrected, consistent value
```
