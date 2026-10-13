```yaml
agent: hypothesis-smith
date: 2026-10-13
brief: Conjecture candidates (5 to 7) that can organise the critical systematic review and that published within-paper evidence can test without training
sources_examined:
  - research/CONTRACT.md
  - .claude/agents/hypothesis-smith.md
  - research/review/feasibility-inventory.md
  - research/review/protocol.md (sections 1, 6, 7, 9)
  - research/review/survey-landscape.md (YAML claims, sections 1c, 2, 3, 4)
  - research/debates/2026-10-13-review-angle/round-01..04 (.md only)
  - research/reports/lit-scout/2026-10-13-frontier-map.md
  - research/review/feasibility/captions.jsonl (keyword queries, listed in the appendix)
  - research/review/corpus/awesome-dlms@194aa6bd.jsonl (titles; abstracts of 14 records named in the text)
coverage: >
  Files above read as stated. captions.jsonl was queried by regular expression over caption text
  (535 records with HTML); about 110 captions were read as truncated samples. No paper was read
  in full for this report. NOT covered: feasibility/stage2/, the ledgers, PLAN.md, FRAMEWORK.md,
  any PDF. Every count below that comes from a caption query is E1 (a keyword matched a caption),
  not a count of usable sweeps or contrasts.
claims:
  - statement: 268 of 535 papers carry a step-sweep caption; 96 of them mention an accuracy-type outcome in a step caption and 52 mention perplexity
    status: supported
    evidence: feasibility-inventory.md table; caption queries Q1, Q2 (appendix)
    level: E1
    confidence: 0.8
  - statement: Only 21 of the 268 papers with a step caption mention seeds, standard deviation, error bars or plus-minus inside a step caption
    status: supported
    evidence: caption query Q1 (appendix); captions only, so tables that give variance without saying so in the caption are missed
    level: E1
    confidence: 0.6
  - statement: Step captions that mention both perplexity and entropy occur in 18 papers; perplexity alone in 52
    status: supported
    evidence: caption queries Q2, Q3 (appendix)
    level: E1
    confidence: 0.7
  - statement: A small set of baseline cells is reused very widely (captions naming both LLaDA and GSM8K in 61 papers; HumanEval 47, MATH500 37, MBPP 33; MDLM with OpenWebText 20)
    status: supported
    evidence: caption query Q3 (appendix)
    level: E1
    confidence: 0.7
  - statement: In multimodal papers the step-sweep evidence is thin (17 of 28 have a step caption; 6 of those mention an image metric in it)
    status: supported
    evidence: feasibility-inventory.md; caption query Q3
    level: E1
    confidence: 0.7
competing_explanations: [listed per candidate in section 2 of each]
unknowns:
  - How many flagged sweeps hold everything but the step count fixed and have at least three points (stage 2 decides)
  - Whether any candidate is already stated in the full text of 2502.09622, 2604.02718, 2510.18480, 2606.29228, 2508.19982 or 2602.00286 (abstracts or second-hand section notes only)
  - Whether the derivations marked E0 below are correct; none has been checked numerically
next_test: {hypothesis: all seven (unranked), intervention: stage-2 extraction with the per-candidate fields listed in section 9, primary_metric: number of usable sweeps and contrasts per candidate against the protocol section 7 threshold, falsifier: fewer than 8 contrasts from 5 groups for a candidate means it can only be reported as a vote count, gpu_hours: 0}
```

# Conjecture candidates for the review (unranked, unscored)

All seven are **hypotheses (E0)**. Nothing here is a verified result. Order is arbitrary.
Novelty has not been audited; the "closest prior statements" lists are what I could find in our
own files or recall, and they are a starting list for `novelty-auditor`, not a clearance.

## 0. Shared definitions

These terms are used with one meaning throughout.

- **L**: number of positions that are masked (or noised) at the start of generation and scored at
  the end, as stated by the paper (its "generation length").
- **T**: number of denoiser forward passes used for one sample (the paper's steps or NFE). Where a
  paper reports only an average NFE of an adaptive sampler, T is that average.
- **k = L / T**: mean tokens committed per forward pass. k = 1 is one token per pass.
- **r = T / L**: forward passes per generated token.
- **Sweep**: a set of at least three points (T_j, Q_j) from one paper in which checkpoint, task,
  prompt, L, sampler family, temperature and guidance are held fixed and only T changes. The
  **reference point** is the point with the largest T; a sweep is admissible only if that T is at
  least L / 2.
- **Contrast**: two configurations from one paper that differ in one declared factor, with both
  outcome values reported. This is the only unit of evidence; no raw score is compared across papers
  except in H5, where the object is the dispersion of one nominally identical cell.
- **Relative deficit**: for an outcome where higher is better and bounded in [0, 1],
  delta_j = 1 - Q_j / Q_ref. For generative perplexity, delta_j = log(PPL_j / PPL_ref).
- **Metric class** (assigned from the benchmark definition before any sweep is looked at):
  **G** global exact (every output token can change the score: Sudoku solved, Countdown, code
  pass@k, exact-match structured output); **A** answer-span exact (free-form reasoning then a short
  scored answer: GSM8K, MATH500, multiple-choice); **S** soft or averaged (BLEU, ROUGE, CIDEr,
  generative perplexity, MAUVE, FID, CLIP score).
- **Sampler class V** (context-measurable): the set of positions committed at a pass is a function
  of the already committed context and independent randomness only; each committed token is drawn
  from the model's conditional marginal at temperature 1; nothing is remasked. Uniform random order
  and thresholding on the predicted distribution both belong to V. **Class V'**: anything else
  (argmax decoding, selection on the probability of the token just sampled, temperature below 1,
  remasking). Most LLM-scale accuracy sweeps are V' (E0, from the sampled captions; to be coded).
- **Theory anchors, by ID.** T-a: arXiv 2510.04767 Sec. 4 Theorem 1, the KL of a factorised model
  decoding in T parallel sets is lower-bounded by the sum over steps of the expected total
  correlation of each set given its prefix (E2 in `survey-landscape.md`). T-b: arXiv 2602.00286
  Sec. 3.3 to 3.4, factorised parallel decoding is exact only under conditional independence within
  the block; remasking cannot guarantee distributional correctness (E2 in the same file). T-c:
  arXiv 2505.21400, KL error decays as 1/T and scales with token mutual information (E1, abstract).
  T-d: arXiv 2602.20126, KL scales with total correlation over K (E1, abstract). T-e: arXiv
  2502.09622, perplexity is near-optimal in a number of steps independent of length while sequence
  error rate needs steps linear in length (E1, abstract read in the corpus file). T-f: arXiv
  2604.02718, generative perplexity and entropy are two components of the KL to a reference
  distribution (E1, abstract).
- **Derivation D0 (mine, E0, unchecked).** For a class-V sampler with exact marginals the chain
  rule gives equality in T-a: KL(p || q_T) = sum over steps of E[TC(X_S | context)]. With uniform
  random sets of size k, the number of co-revealed pairs is T * k(k-1)/2 = L(k-1)/2, so each pair
  is co-revealed with probability (k-1)/(L-1). When pairwise terms dominate the total correlation,
  KL is approximately L(k-1)/2 times the mean conditional mutual information of a co-revealed pair.
  If only m of the L positions are non-deterministic given the prompt, the factor becomes about
  (k-1) m^2 / (2L). To first order in (k-1)/L the sampled distribution is p plus a perturbation
  linear in (k-1), so the probability of any scored event moves linearly in (k-1) at onset.

---

## H1. Linear-onset law for step sensitivity (resubmission of CD with an estimand)

**1. Statement.** For an admissible sweep with a fixed number of tokens committed per pass, let the
onset region be the points with 0 < delta_j <= 0.25. Define the **onset exponent** beta as the
slope of log delta on log(k - 1) over the onset region (mixed model, random intercept per sweep,
standard errors clustered by paper), and the **sensitivity coefficient** c of a sweep as the
least-squares slope through the origin of delta on (k - 1) over the same region.

- (a) For sweeps coded as random-order (class V or its argmax variant), pooled beta = 1: the
  deficit starts linearly in k - 1.
- (b) For sweeps coded as confidence-ordered with a fixed number per pass, beta > 1 (convex onset),
  because the pairs added as k grows are the more dependent ones.
- (c) Within one paper, one checkpoint and one sampler, c is ordered by metric class: c_G >= c_A >= c_S.
- (d) beta does not differ between model families (absorbing-state masked, uniform-state,
  discrete flow) once (a) and (b) are separated.

Scope: discrete-state models with a factorised per-position output; no remasking; no distilled
few-step students (their marginals are trained to absorb the dependence); k between 1 and L/4.
Assumptions that the theory needs and published sweeps may violate: exact marginals, class V,
temperature 1, pairwise-dominated dependence, a deficit small enough for the first-order term.

**2. Why it is not obvious.**

| Mechanism | beta, random order | beta, confidence order | c ordered G > A > S within paper | c changes when L is padded |
|---|---|---|---|---|
| M1 dependence (T-a, T-c, D0) | 1 | above 1 | yes | falls roughly as m^2 / L |
| M2 slack (H2): outputs contain many near-deterministic tokens | flat, then abrupt | flat, then abrupt | no, ordered by answer-to-length ratio | falls sharply |
| M3 commitment error: wrong early tokens, not dependence, cause the loss | not a power law; can be non-monotone | below or near 1 | weak | unchanged |
| M4 metric saturation: deficit reflects the ceiling of the benchmark | depends on Q_ref | depends on Q_ref | reverses when Q_ref is near chance | unchanged |

T-e predicts the G-against-S ordering asymptotically; M1 adds a functional form at onset and a
sampler split that T-e (as far as its abstract shows) does not give.

**3. Published evidence, estimand, refutation.** Step-sweep captions: 268 papers (E1). Subsets by
caption keyword: accuracy-type outcome 96 papers (203 captions), perplexity 52, puzzle tasks 15,
both a soft and an exact metric in step captions of the same paper 9. Estimands: beta per sampler
code; the sign of c_X - c_Y for each within-paper pair of classes. Refuted if any of: (R1) the
95 percent interval of pooled beta for random-order sweeps excludes 1; (R2) beta for
confidence-ordered sweeps is not larger than for random-order sweeps (one-sided, interval of the
difference includes 0 or below); (R3) the class ordering holds in fewer than 60 percent of
within-paper pairs, or the sign test against 50 percent has p above 0.05 with at least 12 pairs;
(R4) more than a quarter of admissible sweeps are non-monotone in T beyond their reported
variation. Part (c) probably has too few within-paper pairs (9 candidate papers) to reach the
pooling threshold and would be a vote count.

**4. Cheap corroboration (not run).** Enumerate exactly. Vocabulary 3, L = 8; three targets: an
independent product, a first-order Markov chain with tunable coupling, and a chain with one global
parity constraint. Compute the exact output distribution of the T-step sampler for T in
{8, 4, 2, 1} under random order and under lowest-entropy-first order, with exact conditionals.
Report KL, the probability of an all-correct sequence (class G analogue), the probability of a
correct last token (class A) and mean per-token log-likelihood (class S), each against k - 1 on
log axes. D0 is confirmed if the random-order slope is 1 +/- 0.1 at weak coupling and the
confidence-ordered slope is larger. 3^8 states times 2^8 mask patterns; seconds on a CPU.

**5. Closest prior statements.**
- arXiv 2502.09622 (E1): metric-dependent step requirement, theory plus experiments. Differs: no
  onset exponent, no within-paper ordinal test on published LLM sweeps, no sampler split
  (unverified beyond the abstract).
- arXiv 2510.04767 Theorem 1 (E2 in our files), 2505.21400 and 2602.20126 (E1): bounds on KL. Differ:
  they bound a divergence; H1 is a claim about reported task metrics and about which sampler codes
  inherit the form.
- arXiv 2601.15593 (E1, abstract): parallelism varies with task domain across 8 models. Differs:
  own runs, descriptive metrics, no functional form.
- arXiv 2508.08712 Sec. 6.1.2 (E2 in our files): qualitative speed-quality statement.
- CD in debate round 3 (ours): a single common exponent on one curve. H1 drops the collapse,
  states two exponents by sampler code, moves the task claim to a within-paper ordinal test, and
  lists the assumptions.

**6. Follow-up article on frozen checkpoints.** On `kuleshov-group/mdlm-owt` and `s-sahoo/duo`
(about 130M, E1 names from the frontier map, to be verified on the Hub): estimate the conditional
mutual information of co-revealed pairs from the model's own conditionals (two forward passes per
pair and context), predict c from D0 with no free parameter, and compare with measured sweeps under
class V. Then repeat the sweep on LLaDA-8B and Dream-7B in 4-bit on three benchmarks, one per
metric class, with argmax and with temperature-1 decoding. Kill: rank correlation between
predicted and measured c at or below 0 over at least 6 task-model cells, or measured beta under
class V outside [0.75, 1.25].

**7. Most likely rejection.** "The theorem covers class V with exact marginals; nearly every
benchmark sweep is argmax with confidence selection and reports three or four step counts with no
variance. A slope fitted to two onset points per sweep is not an exponent, and the metric classes
were chosen to make the ordering come out."

---

## H2. Slack conjecture: most reported acceleration recovers over-provisioning of the default schedule

**1. Statement.** For a paper that reports a speed-up at "comparable" quality on a task:
**headline speed-up** S_head = T_base / T_method, where T_base is the baseline configuration the
paper divides by. **Attributable speed-up** S_att = T*_base(Q_method) / T_method, where
T*_base(q) is the smallest T at which the same paper's sweep of the *baseline* sampler reaches
quality q - eps (linear interpolation in log T; eps = the reported seed standard deviation, or
0.5 points if none). **Slack share** sigma = 1 - log S_att / log S_head, clipped to [0, 1].
Only speed-ups counted in forward passes enter; wall-clock gains from caching form a separate
stratum and are not covered.

- (a) Fewer than one third of papers that report a headline NFE speed-up also report the baseline
  sampler swept down to the method's own T (so that S_att can be computed).
- (b) Where it can be computed, the median sigma is at least 0.5.
- (c) Within a paper that varies L on a fixed task, sigma does not decrease as L grows.

Scope: training-free samplers on a frozen masked-diffusion checkpoint; class A and G tasks.

**2. Why it is not obvious.**

| Mechanism | median sigma | sigma against L (task fixed) | accuracy when L is cut to the answer length | share of papers with a baseline sweep |
|---|---|---|---|---|
| M1 slack: padded outputs make k = 1 wasteful (D0 with m << L; arXiv 2508.19982 early answer convergence, E1) | at least 0.5 | rises | unchanged | low |
| M2 frontier shift: the method commits dependent tokens more safely | below 0.25 | flat | unchanged | any |
| M3 padding is computation (arXiv 2603.05197, E1: EoS tokens act as extra capacity) | intermediate | rises | falls | any |
| M4 selective reporting: sweeps are shown only when the method survives them | observed sigma biased low | n/a | n/a | low, and (b) is then conservative |

M1 and M3 agree on (c) and disagree on what happens when L is shortened, which no published
contrast may contain; that disagreement is for the follow-up article.

**3. Published evidence, estimand, refutation.** Inference Optimization papers with a step caption:
99 of 164 (E1, inventory). Step captions naming both an accuracy outcome and a cost (NFE,
throughput, latency): 41 papers. Captions mentioning generation length among step captions: 64.
Speed-up wording in an Inference Optimization caption: 42. Estimands: the proportion in (a);
the median sigma with a bootstrap interval clustered by paper in (b); the sign of the within-paper
change of sigma with L in (c). Refuted if (R1) the proportion in (a) is at or above one half, or
(R2) the upper end of the 95 percent interval of the median sigma is below 0.5, or (R3) sigma
falls with L in a majority of within-paper cases (at least 6 cases needed).

**4. Cheap corroboration (not run).** Extend the H1 enumeration: L = 12 with m = 3 content
positions forming a coupled Markov chain and 9 positions deterministic given the prompt. Compute
exact all-correct probability for the uniform random-order sampler at T in {12, 6, 4, 3, 2} and for
a threshold sampler that commits every position whose top probability exceeds tau. Compute S_head
against T = 12, S_att against the baseline's own curve, and sigma, then repeat for m in {3, 6, 12}.
D0 predicts that the baseline tolerates k up to about L / m with little loss, hence sigma near
log(L/m) / log S_head.

**5. Closest prior statements.**
- arXiv 2508.19982 (E1): correct answers are identifiable by half the steps on GSM8K and MMLU.
  Differs: used to motivate a method; no attribution of other papers' speed-ups.
- arXiv 2505.24857 (E1): a partially masked sequence often determines several tokens. Same
  observation at token level; no audit.
- arXiv 2510.18480 (E1): critique of efficiency evaluation; AR throughput higher; gains shrink with
  batch size. Differs: throughput and batch size, own benchmarking; sigma is not defined.
- arXiv 2606.29228 (E1): parallel-decoding rankings depend on the prompt template.
- arXiv 2607.12829 (survey of inference efficiency; flags in our files show no audit).
- arXiv 2510.04767 (E1, abstract): standard maths and code benchmarks do not expose parallel
  decoding damage. Closest in spirit; it responds with a new benchmark, not with an attribution
  ratio over published numbers. The full text must be checked for a baseline-sweep control.

**6. Follow-up article.** LLaDA-8B-Instruct and Dream-7B in 4-bit: sweep the default sampler over T
and L on GSM8K and HumanEval subsets (about 300 items each), reimplement two public training-free
accelerators, and report sigma with seed intervals. Then the M1-against-M3 test: cut L to 1.25
times the reference answer length and remeasure. Kill: sigma below 0.25 with an interval excluding
0.5 for both checkpoints. Quantisation is a confound and needs one full-precision control on the
smallest feasible configuration.

**7. Most likely rejection.** "Nobody claims the full-step default is a tuned baseline; it is a
convention. The papers that omit the baseline sweep are exactly the ones you cannot score, so (b)
is estimated on a self-selected minority and (a) is a reporting count, not a conjecture."

---

## H3. Budget crossover for remasking and other training-free correctors

**1. Statement.** A **corrector contrast** is a within-paper pair, corrector on against off, with
checkpoint, task, L and total forward passes T matched (a corrector is any inference-time rule
that returns a committed token to the masked state or resamples it). Let Delta_R(r) be the
standardised quality difference, positive when the corrector is better, at budget r = T / L.

- (a) Within a paper that reports the contrast at two or more budgets, Delta_R increases with r.
- (b) There is a crossover r* in [0.25, 1]: pooled Delta_R is not above 0 for r <= 0.25 and is
  above 0 for r >= 1.
- (c) On generative perplexity, a positive Delta_R is accompanied by lower sample entropy (links to H4).

Scope: training-free correctors on a factorised masked denoiser. Excludes models trained to
remask and uniform-state diffusion, where revision is part of the process.

**2. Why it is not obvious.** The ReMDM abstract (arXiv 2503.00307, E1) says that with a limited
budget the sampler "better maintains quality", which is the opposite of (b).

| Mechanism | sign of Delta_R at r <= 0.25 | at r >= 1 | class A or G accuracy against perplexity | entropy change |
|---|---|---|---|---|
| M1 budget: each remask uses a pass that would have lowered k (T-a, T-b) | zero or negative | positive | same pattern on both | none required |
| M2 correction: early commitment errors dominate at every budget | positive, largest at low r | positive | larger on accuracy | none |
| M3 entropy artefact: remasking sharpens samples | positive on perplexity | positive on perplexity | absent on accuracy and MAUVE | falls |
| M4 calibration: helps only where confidence tracks correctness | depends on the model, not r | same | follows calibration, not metric | none |

**3. Published evidence, estimand, refutation.** Remasking captions: 53 papers, 118 captions (E1).
Remask captions that also mention steps or NFE: 36 papers; papers with both a remask and a step
caption: 34; both flags on one caption: 10. Estimands: the sign of the within-paper slope of
Delta_R on log r; pooled Delta_R in the two budget bands. Refuted if (R1) the slope is positive in
fewer than 60 percent of papers with two or more budgets (at least 8 papers), or (R2) pooled
Delta_R at r <= 0.25 is above 0 with a 95 percent interval excluding 0. If fewer than 8 contrasts
from 5 groups share metric and task family, only the vote count is reported.

**4. Cheap corroboration (not run).** Same enumeration as H1 (vocabulary 3, L = 6 to 8). Add a
remasking kernel that returns each committed position to the mask with probability s per pass,
total passes fixed at T. Compute exact KL and all-correct probability for s in {0, 0.05, 0.1, 0.2}
and T in {L/4, L/2, L, 2L, 4L}, first with exact conditionals, then with conditionals perturbed by
a fixed logit noise to imitate model error. Output: the sign map of the corrector's gain over
(r, s, noise). M1 predicts a negative region at low r that shrinks as noise grows.

**5. Closest prior statements.**
- arXiv 2503.00307 (E1): remasking gives inference-time scaling and helps at low budget. H3
  contradicts the second half as a general rule.
- arXiv 2602.00286 Sec. 3.3 to 3.4, 8 (E2 in our files): remasking cannot guarantee
  distributional correctness. No budget-matched sign claim.
- arXiv 2512.25014 (E1): revision gives optimal space in a simulation result. Different question.
- arXiv 2509.23653, 2610.08833 (E1, frontier map row 2): trained or learned correction; outside scope.
- Predictor-corrector samplers for discrete diffusion (E0, unverified; no ID given).

**6. Follow-up article.** `kuleshov-group/mdlm-owt` with a ReMDM-style sampler and LLaDA-8B 4-bit
with low-confidence remasking: a grid over r in {0.125, 0.25, 0.5, 1, 2, 4} at matched T, three
seeds, reporting MAUVE, entropy-matched perplexity and class A accuracy. Kill: Delta_R above 0 with
an interval excluding 0 at r = 0.125 and r = 0.25 on both checkpoints.

**7. Most likely rejection.** "Remasking schedules are tuned per budget, so 'corrector on' is not
one intervention; the crossover location is whatever the tuning makes it. The band [0.25, 1] is
wide enough to be unfalsifiable, and ten same-caption contrasts will not pool."

---

## H4. Entropy confound: published generative-perplexity gains mostly move along the frontier

Bears on RQ6 (validity of a headline metric) and RQ4; uses step sweeps.

**1. Statement.** For any within-paper contrast on unconditional or prefix-conditional generation
that reports, for both configurations, generative perplexity (exponential of the mean per-token
negative log-likelihood of the samples under a fixed evaluator model) and sample entropy (the
paper's own statistic, usually mean per-sample unigram entropy): let g = difference in log
generative perplexity (negative means "better") and h = difference in entropy, favoured
configuration minus comparator.

- (a) Sign concordance: among contrasts with g < 0, h < 0 in at least two thirds.
- (b) Let b be the within-paper slope of log perplexity on entropy along a temperature or
  nucleus sweep of one configuration (the paper's own frontier), and g_adj = g - b h. Where b is
  available, the median of |g_adj| / |g| is at most 0.5.
- (c) Along a step sweep of an ancestral masked sampler, entropy falls as T rises in papers that do
  not state 64-bit sampling, and does not in papers that do.
- (d) Fewer than half of the papers that report generative perplexity against steps report entropy
  alongside it.

Scope: small-scale language-modelling benchmarks (OpenWebText, LM1B, text8) where this metric is
the headline.

**2. Why it is not obvious.**

| Mechanism | P(h < 0 given g < 0) | median |g_adj| / |g| | entropy against T | survives 64-bit sampling |
|---|---|---|---|---|
| M1 frontier movement (T-f): gains are sharpening | high | low | any | yes |
| M2 numerical truncation of Gumbel noise (arXiv 2409.02908, E1) | high, only at large T | low | falls with T | no |
| M3 real improvement: the frontier shifts | near one half | near 1 | flat | yes |
| M4 distillation collapse: few-step students lose diversity | high for distilled students only | low for those | n/a | yes |

**3. Published evidence, estimand, refutation.** Step captions mentioning perplexity: 52 papers
(118 captions); mentioning perplexity and entropy together: 18; any caption with both: 25; papers
whose captions name generative perplexity explicitly: 30; MDLM with OpenWebText: 20 (all E1). The
18-of-52 figure is a first reading of (d) from captions alone. Estimands as defined in (a) to (d).
Refuted if (R1) the proportion in (a) has a 95 percent interval lying below two thirds; (R2) the
median ratio in (b) exceeds 0.5 with an interval excluding 0.5; (R3) the entropy trend in (c) does
not differ between the two groups of papers.

**4. Cheap corroboration (not run).** Target p: a first-order Markov chain over a vocabulary of 4,
L = 8. "Evaluator" = p itself. Enumerate the exact output distribution q of the T-step sampler
with (i) temperature in {1, 0.9, 0.8, 0.7}, (ii) selection on the probability of the sampled token
(class V'), (iii) Gumbel noise truncated at a 32-bit-like bound. For each, compute E_q[-log p]
(the perplexity analogue), H(q), mean unigram entropy, and KL(q || p). Confirms the mechanism if
(ii) and (iii) lower both perplexity and entropy while KL(q || p) rises, and gives the value of b
relating the unigram proxy to true entropy on this toy.

**5. Closest prior statements.**
- arXiv 2409.02908 (E1): 32-bit categorical sampling lowers effective temperature, making
  perplexity-only evaluation unfair. Mechanism M2; no audit of other papers.
- arXiv 2604.02718 (E1): perplexity and entropy as two parts of a KL; proposes generative
  frontiers; "empirical observations on model quality at this scale" (content not read). **Highest
  overlap risk**: if that note already re-scores published results at matched entropy, H4 reduces
  to extending its count. Must be read in full first.
- arXiv 2602.19619 (E1, frontier map row 8): sampler correctness; content not read.
- H4 differs, as far as abstracts show, by stating a literature-wide regularity with a numeric
  share and by (c), a dated split that separates M1 from M2.

**6. Follow-up article.** `kuleshov-group/mdlm-owt`, `louaaron/sedd-small`, `s-sahoo/duo`:
reproduce 6 to 10 published sampler contrasts, trace full temperature frontiers at 32-bit and
64-bit, and report each published gain as a frontier shift at matched entropy with seed intervals.
All fit in 12 GB at full precision. Kill: more than half of the reproduced gains keep at least half
their size at matched entropy.

**7. Most likely rejection.** "This is the thesis of the generative-frontiers note and of Zheng
et al.; the community already reports entropy. Unigram entropy is a poor proxy, so g_adj depends
on an estimated slope b that most papers do not let you compute."

---

## H5. Noise-floor conjecture: the typical claimed gain is smaller than twice the between-paper spread of its own baseline (RQ6)

**1. Statement.** A **cell** is (checkpoint name, benchmark, metric, L, T, sampler as named,
shot count). A cell **qualifies** if at least 5 papers with disjoint author lists report a
baseline value for it. sigma_B = standard deviation across papers of that baseline value (also
reported as 1.4826 times the median absolute deviation). For each paper, Delta = favoured method
minus baseline in that cell, from that paper's own table (a contrast).

- (a) In a majority of qualifying cells, the median |Delta| is below 2 sigma_B.
- (b) Home-baseline deficit: a paper's own baseline value is below the cross-paper median of the
  cell in more than half of the cases where the paper proposes a competing method.
- (c) sigma_B exceeds the median within-paper seed standard deviation reported for the same cell by
  a factor of at least 2.

Scope: the widely reused cells of 2025 and 2026 (candidates: LLaDA-8B variants and Dream-7B on
GSM8K, MATH500, HumanEval, MBPP; MDLM and SEDD on OpenWebText). This is not a regression of raw
scores: the dispersion of one nominally identical cell is used only as a yardstick for
within-paper contrasts. If the orchestrator reads the "no cross-paper raw scores" rule as covering
this too, (a) and (c) fall and only the protocol-variance description survives.

**2. Why it is not obvious.**

| Mechanism | median |Delta| / sigma_B | sigma_B after matching on every declared protocol field | sign in (b) | sigma_B against seed SD |
|---|---|---|---|---|
| M1 undeclared harness variance (prompt template, answer parser, stop rule) | below 2 | stays large | near one half | much larger |
| M2 declared protocol differences hidden under one name | below 2 before matching | shrinks by half or more | near one half | larger before matching only |
| M3 under-tuned competitor baseline | below 2 | stays | clearly above one half | larger |
| M4 gains are robust | above 2 | small | near one half | comparable |

**3. Published evidence, estimand, refutation.** Captions naming LLaDA: 139 papers; Dream: 81;
GSM8K: 102; LLaDA and GSM8K together: 61; HumanEval 47; MATH500 37; MBPP 33; OpenWebText 34
(all E1, any caption). Estimands: per-cell ratio median |Delta| / sigma_B with a bootstrap interval
over papers; the proportion in (b); the ratio in (c) using the papers that report seeds (variation
mentioned in 62 percent of papers, intervals in 21 percent, per the inventory). Refuted if (R1)
the ratio exceeds 2 in a majority of qualifying cells, or (R2) fewer than 3 cells qualify after
strict matching (then the claim is untestable from the literature and is reported as such), or
(R3) for (b), the proportion's interval includes one half.

**4. Cheap corroboration (not run).** No model needed: a derivation plus a resampling exercise on
extracted numbers. With per-paper baseline values y_i = mu + u_i + e_i (u between-paper, e seed
noise) and claimed gains Delta_i, the probability that a later paper's baseline exceeds an earlier
paper's method is Phi((mu_B - mu_M) / sqrt(2 (s_u^2 + s_e^2))); compute it from the extracted
sigma_B and median Delta and compare with the observed frequency of such rank inversions across
papers, which is countable from the tables.

**5. Closest prior statements.**
- arXiv 2606.29228 (E1): inconsistent results across prior parallel-decoding studies; rankings
  depend on the prompt template. One sub-area, own reruns; no ratio.
- arXiv 2606.19475, 2601.15593 (E1): unified reruns across 8 models. Supply neutral values that can
  anchor the cells.
- arXiv 1711.10337 (E1 in our files): budget and tuning explain differences among GANs.
- arXiv 2406.10229, 2606.20536 (E1 in our files): seed and sampling variance of benchmark scores.
- Bouthillier et al., "Accounting for variance in machine learning benchmarks"; Musgrave et al.,
  "A metric learning reality check"; Armstrong et al., "Improvements that don't add up" (all E0,
  IDs unverified).
- Differs: none of the above, as listed in our files, measures the ratio for diffusion language
  models from the published record.

**6. Follow-up article.** Fix one cell (LLaDA-8B-Instruct, GSM8K, declared L and T, 4-bit and one
full-precision control), and vary only undeclared factors found in the extraction: prompt
template, answer parser, stop rule, block length, 5 seeds each. Report the share of sigma_B each
factor reproduces. Kill: the undeclared factors together reproduce less than a quarter of sigma_B.

**7. Most likely rejection.** "The cells are not identical; you are measuring protocol
differences and calling them noise. And the comparison of baseline values across papers is the
cross-paper comparison you said you would not make."

---

## H6. Decline on independent re-run, with a rigour gradient (RQ6)

**1. Statement.** A **re-run pair** is: paper P0 proposes method M and reports gain Delta_0 over
baseline B in a cell; a later paper P1 with a disjoint author list reports both M and B in the same
nominal cell, giving Delta_1. Both are within-paper contrasts. **Retention** s = Delta_1 / Delta_0
(pairs with Delta_0 <= 0 excluded and counted).

- (a) s < 1 in at least two thirds of re-run pairs, and the median s is below 0.75.
- (b) Rigour gradient: the median s is lower for P0 with protocol item QA4 = 0 (no variation
  reported) than for P0 with QA4 >= 1.
- (c) Source gradient: the median s is higher when P1 proposes no competing method (a benchmark or
  analysis paper) than when P1 proposes a competitor.
- (d) For comparisons against autoregressive baselines (RQ2), the share of contrasts favouring the
  diffusion model is lower among contrasts scored QA6 = 2 (matched or reported budget) than among
  QA6 = 0, within the same task family.

**2. Why it is not obvious.**

| Mechanism | median s | lower s when P0 reports no variation | higher s in neutral P1 | B moves between P0 and P1 |
|---|---|---|---|---|
| M1 winner's curse: selection on noisy gains, regression to the mean | below 1 | yes | no difference | no |
| M2 competitor handicap: P1 under-tunes M | below 1 | no | yes | no (M falls, B stays) |
| M3 protocol drift: the cells differ | scattered around 1 | no | no | yes, both move |
| M4 gains are real and portable | near 1 | no | no | no |

(b) separates M1 from M2; (c) separates M2 from M1; H5's sigma_B measures M3.

**3. Published evidence, estimand, refutation.** Ablation or component captions: 401 papers;
comparison with autoregressive models: 240, of which a quality metric is named in the caption for
81 and matched-size or matched-data wording appears for 32 (E1). The number of re-run pairs is
**unknown**: it requires the extraction of method names appearing as baselines in later papers.
Inference Optimization (164 papers on a handful of checkpoints) is where pairs are most likely.
Estimands: median s with a bootstrap interval clustered by P0; the difference of medians in (b)
and (c); the difference of proportions in (d). Refuted if (R1) the interval for the median s
includes 1, or (R2) fewer than two thirds of pairs have s < 1 with at least 15 pairs. Parts (b) to
(d) are refuted if the stated ordering is reversed; with wide intervals they are reported as
undetermined, not supported.

**4. Cheap corroboration (not run).** Closed form and a short simulation. True gains theta ~
N(mu, tau^2); each run adds noise N(0, sigma^2); P0 reports the best of n_c configurations
evaluated on n_s seeds and publishes only if the reported gain exceeds a threshold; P1 runs once.
Derive E[s] = tau^2 / (tau^2 + sigma^2 / n_s) corrected for the expected maximum of n_c draws and
the truncation, then tabulate E[s] for sigma taken from the seed standard deviations that the
reporting papers give. This yields the size of the gradient in (b) that M1 alone can produce, to be
compared with the observed one.

**5. Closest prior statements.**
- arXiv 2606.29228 (E1): method rankings change under multi-template evaluation. One P1 for many P0.
- arXiv 2510.18480 (E1): acceleration gains diminish at larger batch size. A specific moderator.
- DOI 10.18653/v1/2026.acl-short.22 (E1 in our files): randomness controls missing in 75 percent
  of 55 pipeline papers. A reporting rate, no link to effect size.
- arXiv 1909.06674 (E1 in our files): 255 papers re-implemented.
- Henderson et al., "Deep reinforcement learning that matters"; Dodge et al., "Show your work";
  Marie et al., meta-evaluation of machine-translation papers; the "decline effect" literature in
  medicine and psychology (all E0, IDs unverified).
- Differs: retention measured from the published record itself, with the re-run pair as the unit,
  and a stated gradient on the review's own appraisal items QA4 and QA6.

**6. Follow-up article.** Choose 5 training-free methods with public code that each have at least
3 re-run pairs; rerun M and B on one frozen checkpoint under a preregistered protocol (5 seeds,
the P0 protocol and a neutral one). Report retention against P0 and where our value falls among
the P1 values. Kill: our retention under the P0 protocol is at or above 0.9 for at least 4 of 5.

**7. Most likely rejection.** "Later papers are not replications; they change length, steps and
prompts, and they have every reason to make the competitor look worse. Retention below 1 is what
both bias stories predict, the gradients that separate them will have intervals covering zero, and
QA4 is scored by your own language-model raters."

---

## H7. Scored dependence, not modality, sets step tolerance in unified models

**1. Statement.** For an admissible sweep, **step tolerance** k*_10 is the largest k at which the
relative deficit is at most 0.10 (log-linear interpolation between sweep points). Add one metric
class to section 0: **Gc**, compositional exact scores on images (GenEval counting, position and
attribute-binding sub-scores; rendered-text accuracy).

- (a) Within a unified discrete-diffusion model, k*_10 for image generation scored by class S
  (FID, CLIP score) is at least 8 times k*_10 for text generation scored by class A or G.
- (b) Within one image sweep, k*_10 on class Gc sub-scores is at most half of k*_10 on class S.
- (c) Within one text-output sweep of a multimodal model, k*_10 on a class S score (captioning
  CIDEr or BLEU) is at least twice k*_10 on a class A score (exact-match question answering).
- Consequence if (a) to (c) hold: the sampling-efficiency advantage reported for unified discrete
  diffusion (for example the Lumina-DiMOO and UniDisc abstracts, E1) is a property of soft-scored
  outputs and should not be expected on understanding or reasoning outputs of the same model.

Scope: models with discrete image tokens and a masked or discrete-flow objective. This candidate
gives the multimodal half of the review the same organising variable as H1.

**2. Why it is not obvious.**

| Mechanism | (a) image S against text A/G | (b) image Gc against image S | (c) text S against text A | k*_10 against guidance scale |
|---|---|---|---|---|
| M1 scored dependence (T-a, T-e, D0) | large gap | Gc lower | S higher | weak |
| M2 modality: image tokens are locally redundant, low total correlation | large gap | no difference | no difference | weak |
| M3 decoder repair: the VQ decoder hides token inconsistency from pixel metrics | large gap | Gc lower only for rendered text | no difference | weak |
| M4 guidance: classifier-free guidance, used for images and rarely for text, supplies the tolerance | large gap | no difference | no difference | strong |

**3. Published evidence, estimand, refutation.** Multimodal papers with a step caption: 17 of 28;
with an image metric named in a step caption: 6; papers in any section whose step captions name
FID, GenEval or ImageNet: 8; papers whose step captions mention both image and text outcomes: 7
(all E1). This is **below the pooling threshold**; the literature can supply an ordinal vote count
for (a) and probably nothing for (b) and (c), since per-step GenEval sub-scores are rarely
tabulated (unverified). Estimands: the within-paper ratios of k*_10. Refuted if (R1) the ratio in
(a) is below 8 in a majority of models with both sweeps (at least 4 models), or (R2) in (b) the
Gc sub-score tolerance equals or exceeds the class S tolerance in a majority of sweeps, or (R3) in
(c) the ratio is below 1 in a majority. The honest expected verdict from published data alone is
"untested" for (b) and (c).

**4. Cheap corroboration (not run).** Exact enumeration on a 4 x 4 binary Ising grid with
nearest-neighbour coupling ("image-like") and on a length-16 binary chain with the same coupling
("text-like"). For T in {16, 8, 4, 2, 1}, random order, exact conditionals: compute a soft score
(distance between sampled and true pairwise correlation functions) and an exact compositional score
(the target distribution is conditioned on the number of +1 sites being a given value; the score is
the probability that a sample has that count, the counting analogue) on **both** lattices. M1 predicts the score type, not the lattice, sets k*_10; M2 predicts the lattice
does. 2^16 states; minutes on a CPU.

**5. Closest prior statements.**
- arXiv 2502.09622 (E1): metric dependence for text. No image or cross-modal statement in the abstract.
- arXiv 2503.20853 (E1): a quality-against-inference-time trade-off for joint text and image; its
  Figure 5 caption plots joint perplexity against time and entropy. No split by metric class.
- arXiv 2510.06308, 2505.15809, 2505.20147 (E1): unified discrete-diffusion or discrete-flow
  models; step ablation content not read.
- Few-step masked image generation (MaskGIT) as common knowledge (E0, ID unverified).
- arXiv 2609.01607, 2607.04423, 2509.24897 (E2 in our files): these concern training-time synergy
  (the retired CA), a different question. H7 makes no synergy claim.

**6. Follow-up article.** `Gen-Verse/MMaDA-8B-Base` in 4-bit (name from the frontier map, to be
verified): one step sweep each for text-to-image (GenEval with sub-scores and CLIP score, a few
hundred prompts), captioning and exact-match visual question answering, with and without guidance.
A second unified model if its weights load. Kill: Gc and S tolerances on images within a factor
of 1.25 of each other, or captioning and question-answering tolerances within 1.25.

**7. Most likely rejection.** "Everyone knows images need fewer steps than text and that counting
is harder than FID. The published evidence is six captions, the 8 times threshold is arbitrary,
and with a 4-bit model on a laptop the follow-up cannot separate metric class from quantisation damage."

---

## 8. Cross-links (description, not ranking)

- H1, H2 and H7 share the estimand family (deficit against k) and derivation D0; H2 is H1 with
  m << L; H7 is H1(c) across modalities.
- H3(c) and H4 share the entropy measurement. H5's sigma_B is the measure of mechanism M3 in H6.
- Requirement check: evidence-base rigour (RQ6) is the subject of H5 and H6, and also of H4 and
  H2(a); step-sweep evidence is used by H1, H2, H3, H4 and H7.
- One enumeration script (vocabulary 3 to 4, L up to 12, exact T-step sampler with options for
  order rule, temperature, remasking, padding, noise truncation) covers the corroborations of
  H1 to H4; a second small one covers H7; H5 and H6 need only arithmetic on extracted numbers.

## 9. Fields stage-2 extraction must record for these candidates to be testable

Per sweep: L, every (T, Q) point, metric and metric class, order rule (random, confidence, other),
argmax or sampled, temperature, tokens per pass fixed or adaptive, remasking on or off, guidance
scale, whether the baseline sampler is swept, entropy alongside perplexity, 32-bit or 64-bit
sampling if stated, variance and its kind. Per contrast: cell identity as defined in H5, whether
the baseline value is rerun or copied (and from where), author list, and whether the paper
proposes a competing method. Without the order rule and the argmax flag H1 cannot be split;
without the copied-or-rerun flag H5(b) and H6 cannot be computed.

## Appendix: caption queries behind the E1 counts

All run on 2026-10-13 over `feasibility/captions.jsonl` (records with HTML), case-insensitive, on
caption text restricted to captions carrying the named flag unless "any caption" is stated.

| ID | Flag | Pattern (regular expression) | Papers |
|---|---|---|---|
| Q1 | steps | `seed|std|standard dev|error bar|\pm|±|confidence interval|shaded` | 21 |
| Q2 | steps | `perplex|ppl` | 52 (118 captions) |
| Q2 | steps | `accura|gsm8k|humaneval|sudoku|pass@` | 96 (203 captions) |
| Q3 | steps | perplexity pattern and `entropy` in one caption | 18 |
| Q3 | any caption | perplexity pattern and `entropy` in one caption | 25 |
| Q3 | steps | accuracy pattern and cost pattern (`\bnfe|speed|throughput|tps|latency`) in the paper's step captions | 41 |
| Q3 | steps | `sudoku|countdown|puzzle|planning` | 15 |
| Q3 | steps | soft-metric and exact-metric patterns both present in the paper's step captions | 9 |
| Q3 | steps | `length` | 64 |
| Q3 | remask | `step|nfe|\bt ?=` | 36 |
| Q3 | paper level | steps and remask flags both set | 34 (same caption: 10) |
| Q3 | paper level | steps and vs_ar flags both set | 131 (same caption: 42) |
| Q3 | any caption | `llada`; `dream`; `gsm8k`; `llada` and `gsm8k`; `humaneval`; `math-?500`; `mbpp`; `openwebtext|owt`; `mdlm` and OWT | 139; 81; 102; 61; 47; 37; 33; 34; 20 |
| Q3 | vs_ar | quality-metric pattern; matched-size wording (`param|same size|matched|comparable|similarly sized|same data`) | 81; 32 |
| Q3 | steps, Multimodal section | flag set; with `\bfid\b|geneval|clip|image` | 17; 6 |
| Q3 | steps, any section | `\bfid\b|geneval|clip score|imagenet|text-to-image`; image pattern and a text-outcome pattern both present | 8; 7 |
| Q3 | any caption, Inference Optimization section | `speed-?up|speedup|\d ?(x|×)|faster` | 42 |

Known weakness: "dream" and "length" are loose patterns; the cost and metric patterns over-match;
captions miss contrasts given only in running text. These numbers say where to read.
