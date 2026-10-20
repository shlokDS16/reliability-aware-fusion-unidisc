# Lookups v1: DRAFT for Stage A (not frozen)

`benchmark-ids-v1.csv` and `metric-ids-v1.csv` are v1 drafts, written 2026-10-20 for Stage A of the Paper 1
extraction pilot (EXTRACTION-PLAN-v0.5 s5.4, s10.2; plan v0.4 s14 A7 "lookup CSV skeletons with the KA1(b) list and
direction column"). The orchestrator and method-architect revise them from Stage A, then the mi4 check (plan v0.5
s10.2) may revise them once more; the version that enters the B2 gate row is hashed there together with the brief.
Do not cite these files as final.

## Format (as the readers read it)
- No comment rows. The first line must be the header. `tools/ex_validate.py` (`load_metric_lookup`) rejects a
  printed cell starting with `#` and a header without `printed,id,higher_is_better`; `agreement.py` reads the same
  file through that function and reads the benchmark file with `csv.DictReader`, so a leading comment would become
  the header and the run would stop.
- `benchmark-ids-v1.csv`: `printed,id`.
- `metric-ids-v1.csv`: `printed,id,higher_is_better`, the direction being `true`, `false` or empty (null). Any other
  value (yes, no, 1, 0) is refused.
- Keys: each printed string is keyed by `metric_norm` (plan v0.4 s5.4: normalise, lower case, arrows, enclosing
  parentheses, a trailing citation and whitespace removed). Metric lookups also try the key without the KA1
  qualifiers (top-1, avg., gen., average, mean) and read pass@<n> as pass@k.

## One direction list for both tools
`ex_validate.py` and `agreement.py` (which imports `ex_validate.py` by path) use the same table: the KA1(b) list
built into `ex_validate.py` plus this CSV. The loader refuses a CSV that gives a KA1(b) name a different direction
(the brief and the lookup must not drift apart, plan v0.5 s5.4) or gives one metric id two directions. Every KA1(b)
key is also a row here, with the same id, so the built-in list adds nothing when this file is used
(tests/extraction/test_stagea_gaps.py checks this).

## Seeds (nothing else)
- Metric rows with a direction: exactly the KA1(b) list of plan v0.5 s5.4 / brief v0.5 KA1(b), with the aliases of
  the built-in list in `tools/ex_validate.py` (acc, acc., EM, ROUGEL, CLIP-score, speedup, steps), plus `pass@k`.
- Metric rows with an empty direction: metric names printed in `analysis/extraction/we-expected.jsonl` or the plan
  that are not in KA1(b): COMET, Score, Overall, Time (sec.), Tokens/Seconds, EOD, HR, LR. Plan v0.5 s5.4 gives a
  direction only to KA1(b) names, so their sign goes to EC.
- Benchmark rows: benchmark names printed in `analysis/extraction/we-expected.jsonl` (worked examples v0.4) or in
  the extraction plan (AGNews, CRUXEval, GPQA, MBPP, MMLU). Printed variants are kept as separate ids (HumanEval and
  HumanEval+, BigCodeBench and BigCodeBench-Full, CRUXEval and CRUXEval-O, GPQA and GPQA-Diamond, IFEval and
  IFEval-strict-prompt): a wrong merge is worse than a raw key.
- No web lookup and no value from a paper that can be drawn; names only.

## Left for Stage A (decisions, not made here)
- Whether `Tokens/Seconds` is an alias of TPS and `Time (sec.)` of latency (both would then take a KA1(b)
  direction); today they are their own ids with no direction.
- worked-example benchmark strings that are not benchmarks or are paper-specific and are left unmapped (raw keys):
  `Average`, `corpus`, `fairness`, `fairness benchmark`, `privacy`, `privacy benchmark`.
- `ARC` is kept as printed; ARC-Challenge, ARC-Easy and ARC-AGI are not seeded.
