# H2 pilot: computation rules (frozen 2026-10-13, before any pilot table was read)

Purpose: decide whether the slack conjecture H2 (`conjectures.md`) is computable from published
tables and worth organising the review around. The pilot is exploratory (about 15 papers). The
confirmatory test runs on the full corpus after the protocol is frozen; pilot papers are flagged
there and results are given with and without them.

Inputs after the novelty audit (`novelty-H2-H5.md`): H2 judged novel with confidence 0.55; the
closest work is arXiv 2609.33947 (2026-09-27), which argues simple baselines are stronger few-step
generators than reported, for temperature and generative perplexity. H5 judged incremental
(arXiv 2606.29228 already reports up to 9 percent cross-study discrepancy for LLaDA-8B on GSM8K),
so H5 is kept only as a descriptive analysis under RQ6, credited to that paper.

## Unit
One unit is (paper, task, model, generation length L, metric) for which the paper reports a
proposed method at T_m forward passes with quality Q_m, and the baseline sampler at a headline
configuration (T_h, Q_h). The extraction is done by an agent that is not told the conjecture.

## Quantities
- Headline speed-up S_head = T_h / T_m. T_h is the baseline configuration the paper's own speed-up
  statement divides by; if no statement, the baseline row with the most forward passes in the
  same table. Units with S_head <= 1 are excluded.
- Tolerance eps: the reported seed standard deviation of Q_m if given; else 0.5 points for
  metrics on a 0 to 100 scale, or 1 percent of Q_m for other metrics. For lower-is-better metrics
  the comparison is mirrored.
- T*: scanning the baseline's own sweep from the fewest steps upward, the first T at which baseline
  quality reaches Q_m - eps, with linear interpolation in log T between the two bracketing sweep
  points. On a non-monotone sweep the first crossing from the low side is used (primary);
  the crossing on the running-maximum envelope is reported as a sensitivity variant.
- Attributable speed-up S_att = T* / T_m. Slack share sigma = 1 - log S_att / log S_head, clipped
  to [0, 1].

## Edge cases (decided in advance)
| Case | Rule | Flag |
|---|---|---|
| Baseline never reaches Q_m - eps at any swept T | sigma = 0 | dominates |
| Baseline reaches it at T <= T_m | sigma = 1 | baseline-sufficient |
| Lowest swept baseline T is above T_m and already reaches Q_m - eps | sigma >= 1 - log(T_low / T_m) / log S_head, reported as a lower bound | censored |
| Baseline has fewer than 3 swept levels | not computable | no-sweep |
| Speed-up is wall-clock only (caching, kernels) | separate stratum, not in sigma | wall-clock |
| Baseline numbers copied from another paper | computed, reported separately | copied |

## Summaries and decision thresholds
- Claim (a): among pilot papers with a headline forward-pass speed-up at comparable quality, the
  share whose baseline is swept with at least 3 levels reaching down to 2 T_m or fewer.
  Supports H2(a) if below one third; contradicts it if one half or more.
- Claim (b): paper-level sigma = median over that paper's units; pilot statistic = median of
  paper-level values, censored units entered at their bound, with the count in each flag.
  Supports H2(b) if at least 0.5; contradicts it if below 0.25; otherwise inconclusive.
- Also reported: sigma against L within papers that vary L (claim c), and the sensitivity variant.
- With about 15 papers no interval is meaningful; the pilot reports counts and the raw units.

## What the pilot cannot show
Whether the result holds corpus-wide, whether baselines were tuned fairly in other respects, and
anything causal. A known counter-signal is recorded up front: arXiv 2606.29228 reports GSM8K
accuracy of 77.64, 74.28 and 66.02 for one, two and four tokens per step at length 128, which
suggests little slack at short lengths; arXiv 2509.23924 Table 5 peaks at 32 steps for length 256,
which suggests large slack at long lengths. H2(c) and mechanism M1 are about exactly this contrast.
