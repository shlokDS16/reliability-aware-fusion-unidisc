```yaml
agent: novelty-auditor
date: 2026-10-13
brief: Decide whether conjecture candidates H2 (slack) and H5 (noise floor) are already known.
sources_examined:
  - research/CONTRACT.md
  - research/review/conjectures.md (section 0, H2, H5 only)
  - arXiv:2606.29228 (also ICLR 2027 submission, OpenReview forum psvNRxzYZv)
  - arXiv:2609.33947
  - arXiv:2607.24763
  - arXiv:2510.04767
  - arXiv:2508.19982
  - arXiv:2510.18480
  - arXiv:2606.19475
  - arXiv:2602.22661
  - arXiv:2510.04019
  - arXiv:2607.12829
  - arXiv:2003.03033 (precedent, via ar5iv)
  - abstracts only: 2610.02657, 2609.35472, 2601.15593, 2606.16908, 2606.10829, 2608.00146, and 21 IDs
    checked through one arXiv API id_list call (listed in section 6)
coverage: >
  Section-level reading of 11 papers through WebFetch on arXiv HTML (sections named per paper in
  section 3). WebFetch returns text produced by an intermediary model, so its "verbatim" quotes are
  relayed, not seen by me. For four papers (2606.29228, 2609.33947, 2607.24763, 2510.04767) I
  downloaded the HTML and checked every quote used below against the raw text. No paper was read in
  full, so nothing here is above E1. Last 90 days: two date-bounded arXiv API queries (26 and 27
  hits, 2026-07-10 to 2026-10-14) plus three unbounded recent-first pages. OpenReview: five API term
  searches on ICLR.cc/2027/Conference. NOT covered: Exa (connector needs authentication, unavailable
  this session); Semantic Scholar; NeurIPS 2026 on OpenReview (the one query returned zero notes, so
  either the group id is wrong or nothing is public; treated as not searched); workshops, blog
  posts, GitHub issues; appendices of most papers; any paper whose abstract avoids the keywords in
  section 6.
claims:
  - statement: No located work defines or measures an attributable speed-up or slack share for
      training-free NFE-reducing samplers on frozen masked-diffusion checkpoints, and none counts
      how many such papers sweep the baseline down to the method's step count.
    status: supported
    evidence: section 3.1 matrix; searches in section 6 (absence, search-bounded)
    level: E1
    confidence: 0.6
  - statement: The genus of H2 (a gain over a default configuration includes what the baseline
      sampler leaves unused) is stated in the DLM literature, for temperature and generative
      perplexity, not for step count on accuracy tasks.
    status: supported
    evidence: arXiv:2609.33947 Sec 5 and App D (quote checked on raw HTML)
    level: E1
    confidence: 0.85
  - statement: The existence and rough size of the between-paper spread of the flagship H5 cell
      (LLaDA-8B-Instruct, GSM8K) is already published as a one-sentence statement.
    status: supported
    evidence: arXiv:2606.29228 Sec 1 (quote checked on raw HTML)
    level: E1
    confidence: 0.9
  - statement: No located work computes a cross-paper dispersion statistic for a DLM baseline cell,
      compares claimed gains with it, tests whether a paper's own baseline sits below the
      cross-paper median, or compares that dispersion with seed standard deviation.
    status: supported
    evidence: section 4.1 matrix; searches in section 6 (absence, search-bounded)
    level: E1
    confidence: 0.6
competing_explanations:
  - A scooping paper exists but uses vocabulary my keyword queries did not hit, or sits on a venue
    I could not search (NeurIPS 2026, workshops).
  - A cross-paper table exists in an appendix I did not open (appendices were read for only four
    papers).
unknowns:
  - Whether NeurIPS 2026 accepted papers or ICLR 2027 submissions outside my five queries cover
    either candidate.
  - Full text of arXiv:2505.24857 and arXiv:2512.09106 (not read; search snippets only).
  - The true submission date of arXiv:2607.24763 (HTML header prints "04 Jun 2026" under a 2607
    identifier).
next_test: not applicable. The auditor's brief forbids proposing tests, fixes or reformulations.
```

# Novelty audit: H2 (slack) and H5 (noise floor)

Verdict vocabulary used here. **scooped**: a located work measures the same quantity in the same
scope. **incremental**: the thesis is already stated for this scope or its headline fact is already
published, and the candidate adds quantification or breadth. **novel**: no located work states the
claim or measures the quantity in this scope. **unclear**: the search could not discriminate.

Tool note. The brief asked for the Exa connector. It requires authentication and was not available.
I used the general web search tool, WebFetch, the arXiv export API and the OpenReview API instead.
This changes coverage, not data: nothing below is filled in from memory except where marked E0.

## 1. Summary

| | H2 slack | H5 noise floor |
|---|---|---|
| Verdict | novel | incremental |
| Confidence | 0.55 | 0.70 |
| Paper a referee is most likely to cite against it | arXiv:2609.33947 | arXiv:2606.29228 |
| Runner-up | arXiv:2606.29228 | arXiv:2510.04019 App B.3; outside DLMs, Blalock et al. arXiv:2003.03033 |
| Most exposed sub-claim | (b) | (a) |
| Least exposed sub-claim | (a) | (b) inside DLMs (but it has an exact precedent in IR) |

## 2. Restatement (procedure step 1)

**H2.** One sentence: for training-free samplers on a frozen masked-diffusion checkpoint, on
answer-span and global-exact tasks, at least half of the log of the reported NFE speed-up at
"comparable quality" is reproduced by the same paper's baseline sampler run at fewer steps, and
fewer than one third of the papers reporting such a speed-up show that baseline sweep. Mechanism:
the default of one pass per position is over-provisioned because few output positions are
undetermined given the prompt. This is a claim: (a), (b) and (c) each have a stated refutation.

**H5.** One sentence: for baseline cells reused by at least five disjoint author groups, the
standard deviation of the baseline value across papers is at least half the typical claimed gain in
that cell and at least twice the within-paper seed standard deviation, and papers place a competing
baseline below the cross-paper median more often than not. Mechanism: undeclared harness
differences, declared protocol differences under one name, or under-tuned competitor baselines.
This is a claim: (a), (b) and (c) each have a stated refutation.

## 3. H2

### 3.1 Difference matrix

Cells are marked against H2: S same, P partial, D different. "Quantity" means the estimand, not the
topic. All rows E1 (sections named in 3.2).

| # | Work | Question | Quantity measured | Evidence type | Scope |
|---|---|---|---|---|---|
| 1 | 2609.33947 Simple DLMs are more effective few-step generators than reported | P: are few-step gains an artefact of an under-configured baseline sampler | D: generative perplexity and judged quality of a re-tempered MDLM at 16 to 1024 steps; no ratio | D: own re-runs | D: MDLM-Small, OpenWebText, class S; distilled successors, not training-free accelerators; LLaDA and Dream only in App A.8 for temperature |
| 2 | 2606.29228 Evaluation illusion in dLLMs | P: do training-free decoding methods really keep quality while cutting steps | P: accuracy per method per prompt template, including fixed Top-K at k = 2 and 4; Std and Range across templates; Kendall tau of rankings; no ratio | D: own re-runs of 7 methods | S: LLaDA-8B-Instruct and LLaDA-1.5, GSM8K, MATH500, code |
| 3 | 2510.04767 ParallelBench | P: how much quality is lost per unit of parallelism, static against adaptive | P: accuracy against tokens per step for Random Top-k, Confidence Top-k, threshold, with an oracle; no ratio to a published headline | D: own benchmark runs | P: same checkpoints, but new synthetic and rewriting tasks; says GSM8K, MATH, IFEval "occupy a narrow range" |
| 4 | 2508.19982 Know the answer before decoding | P: is the default step budget larger than needed | P: share of items already correct at half the steps; one table with static budgets beside the method | D: own runs, motivating a method | S: LLaDA-8B, Dream; GSM8K, MMLU, Sudoku, HumanEval |
| 5 | 2607.24763 CaRE | P: do published gains survive compute matching | P: quality at matched actual NFE against nominal steps | D: own re-runs of 7 strategies, 3 seeds | D: remasking strategies; MAUVE and perplexity on OpenWebText and LM1B, HumanEval as a side check |
| 6 | 2510.18480 How efficient are DLMs | D: are DLMs faster than AR under realistic serving | D: throughput against sequence length and batch size | D: own benchmarking | P: LLaDA-8B-Instruct, Fast-dLLM v2, GSM8K; wall-clock, which H2 excludes |
| 7 | 2606.19475 DLMs: an experimental analysis | D: how do 8 DLMs behave across budgets | P: accuracy against steps and against steps-to-block-length ratio, own runs | D: own re-runs | P: 8 models, GSM8K, HumanEval, MBPP and others; no accelerator compared |
| 8 | 2607.12829 Survey of efficient inference | D: taxonomy and latency decomposition | D: none; recommends reporting total forward passes | D: narrative survey | S: training-free and trained accelerators |
| 9 | 2602.22661 dLLM framework | D: reproducible training and evaluation | D: official against reproduced accuracy; Fast-dLLM speed-up multipliers | D: own re-runs | P: LLaDA, Dream, Fast-dLLM |

No row is S in the quantity column and no row is S in the evidence-type column. No located work
uses the published record as its data. Rows 2, 3 and 4 each contain a baseline step sweep of
their own.

### 3.2 What each closest work says (source facts, with location)

1. **arXiv:2609.33947** (2026-09-27; Amin, Yin, Khanna). Read: abstract, Sec 5, App A.8, App D;
   quotes checked on raw HTML. Abstract: "much of the supposed quality gap at few steps can instead
   arise from a suboptimally configured sampler." Sec 5: "A new method should beat the baseline's
   best sampler. A gain over a default configuration mixes a new method's contribution with what
   the baseline sampler leaves on the table." App D lists four practices, among them "Report
   configured steps and network calls separately". App A.8 ("Large diffusion LMs already sit at
   their sharp limit"): LLaDA-8B-Instruct and Dream-v0-Base-7B on 256 GSM8K items and HumanEval
   under the Fast-dLLM protocol; "Greedy is best for both models on GSM8K". App D: "our analysis
   does not attribute a particular adaptive sampler's gain to temperature." Not in the paper
   (checked by the fetch extraction, E1): any fraction of other papers' gains, any count of papers
   that tuned the baseline, any training-free accelerator evaluated.
2. **arXiv:2606.29228** (2026-06-28; Zhang, Ren, Xie, Wei). Read: Sec 1, 3.2, 4.1 to 4.3, 5, App
   A.2, C.2; quotes checked on raw HTML. Abstract: "Single-template evaluation can lead to an
   illusion that decoding methods improve inference efficiency without performance degradation" and
   "current parallel decoding methods consistently underperform the single-token decoding
   baseline". Vanilla is run at generation length 128 with one token per step. The
   near-identical-template table (GSM8K, LLaDA-8B-Instruct; checked on raw HTML) puts fixed Top-K
   beside threshold decoding: mean accuracy over eight templates is 77.64 for Vanilla, 74.28 for
   Top-K (k=2) and 66.02 for Top-K (k=4). So the paper does contain the baseline sampler at half
   and a quarter of the steps, as a sensitivity exhibit, not as a control for other papers'
   speed-ups. Sec 4.2:
   "template H achieves 78.47% accuracy with 48 steps, while template G achieves only 67.85%
   accuracy despite consuming 57 steps". The fetch extraction reports no systematic comparison of a
   reduced-step vanilla sampler with parallel methods at equal steps. App A.2: "a more systematic
   evaluation framework remains an important direction for future work."
3. **arXiv:2510.04767** (ParallelBench). Read: Sec 1, Sec 6, App F.1 opening; quotes checked on raw
   HTML. Sec 1: standard benchmarks "may not adequately expose the quality degradation of parallel
   decoding in real-world scenarios." Sec 6: "In contrast to existing benchmarks like GSM8K ...,
   MATH ..., and IFEval ..., which occupy a narrow range, ParallelBench spans a broad spectrum of
   parallel decoding difficulty." Sec 6, Fig 7 text: "Static unmasking (top-k) methods show
   dramatic accuracy drops as tokens-per-step increase, while adaptive unmasking (threshold)
   achieves superior trade-offs." This answers the open item in conjectures.md H2 section 5: the
   paper does plot static and adaptive samplers on shared tokens-per-step axes, on its own tasks.
   It does not decompose any published speed-up (fetch extraction).
4. **arXiv:2508.19982**. Read through fetch extraction only: Sec 3.2, Sec 5, Tables 1 and 3(a).
   Reported: early-convergence shares by half the steps (for example 97.2% on GSM8K under random
   remasking, 24.2% under low-confidence remasking); Table 3(a) lists static step budgets 16 to 128
   beside the 256-step baseline and the method; speed-ups 1.20x to 2.46x are divided by steps equal
   to generation length; Sec 5.3 presents the method as complementary to Fast-dLLM. No statement
   about other papers' speed-ups. These numbers were relayed by the fetch model and not checked on
   raw HTML.
5. **arXiv:2607.24763** (CaRE). Read: abstract, Sec 4.1; quotes checked on raw HTML. "At 256 nominal
   steps, actual NFE ranges from 128 (none) to 513 (running_conf.)"; at matched NFE "none dominates
   MAUVE at every budget"; on HumanEval "high_entropy appears to outperform none (31.7 vs. 28.3
   pass@1)" at nominal steps and the order reverses at matched NFE. Scope stated by the paper:
   remasking strategies.
6. **arXiv:2510.18480**. Read through fetch extraction: Sec 3, 5.1 to 5.3, 6. Throughput against AR
   and batch size on GSM8K; "These acceleration strategies are most effective when the batch size
   is set to one". No step-matched baseline; no cross-paper numbers.
7. **arXiv:2606.19475**. Fetch extraction of Sec 5.2: own step sweeps; "both models perform poorly
   at low step counts"; no accelerator compared; no comparison with originally published numbers.
8. **arXiv:2607.12829**. Fetch extraction of Sec 7 and 8: recommends reporting total forward
   passes; "direct comparisons across papers are often confounded by differences in model scale,
   evaluation protocol, and hardware configuration." No table of collated speed-ups; nothing on
   the default step budget.
9. **arXiv:2602.22661**. Fetch extraction of Sec 3.3 and App B: Fig 5 varies one sampling
   hyperparameter at a time (one condition generates four tokens per step) and shows performance
   "can degrade sharply from the optimal configuration".

### 3.3 Inference

- The mechanism M1 of H2 (default budget exceeds need) is published as an observation (row 4) and
  the genus of the thesis is published as a principle (row 1). Neither is new.
- The species is not located anywhere: step-count slack, for training-free accelerators, on
  LLM-scale accuracy tasks, expressed as a share of the log speed-up, estimated from the published
  record. Row 1 expressly stops short of it ("does not attribute a particular adaptive sampler's
  gain").
- Sub-claim (a), a count of reporting practice, has no located counterpart in the DLM literature.
  Its form has precedents elsewhere (section 5).
- Sub-claim (b) is the most exposed. A referee can assemble it from row 4 (budget is
  over-provisioned), row 1 (default baselines leave gains on the table) and row 2 (the "comparable
  quality" premise is itself template-dependent) and call the result a quantification of known
  points.
- Sub-claim (c): the only related located statement is a search snippet attributed to Fast-dLLM
  (arXiv:2505.22618) that its speed-up is larger at generation length 1024 (up to 27.6x). I did not
  open that paper. No located work relates a slack share to L.

### 3.4 Verdict for H2

**novel, confidence 0.55.** The estimands (attributable speed-up, slack share, proportion of papers
with a baseline sweep) and the evidence type are not in any located work. Confidence is held down
by three things: the thesis genus was published 16 days ago (2609.33947) and is in the ICLR 2027
cycle; 2606.29228, also an ICLR 2027 submission, attacks the same papers in the same scope from
another angle; and my search could not use Exa or reach NeurIPS 2026. If the bar is "the idea that
accelerator gains partly reflect a weak default", the candidate is incremental; the verdict above
applies to the quantified claim as written.

Single paper most likely to be cited against H2: **arXiv:2609.33947**.

## 4. H5

### 4.1 Difference matrix

Cells are marked against H5: S same, P partial, D different. All rows E1.

| # | Work | Question | Quantity measured | Evidence type | Scope |
|---|---|---|---|---|---|
| 1 | 2606.29228 Evaluation illusion in dLLMs | S for the premise: do nominally identical DLM evaluations disagree, and does that mislead method comparison | P: one cross-paper range for one cell stated in prose ("up to 9%", four studies); Std and Range across prompt templates in own runs; no dispersion over published values, no ratio to gains, no seed SD | P: one anecdote from the published record, then own re-runs | S: LLaDA-8B-Instruct, LLaDA-1.5; GSM8K, MATH500, code |
| 2 | 2510.04019 Simple policy gradients | D: a method paper | P: a table of base-model accuracy from two prior papers and the authors' reproduction; no statistic | P: three sources tabulated | S: LLaDA-8B-Instruct on GSM8K, MATH-500, Countdown, Sudoku |
| 3 | 2602.22661 dLLM framework | D: reproducible tooling | P: official against reproduced values per cell (gaps up to 5.3 points) | D: own re-runs against one official value | S: LLaDA and Dream on MMLU, GSM8K, HumanEval |
| 4 | 2607.24763 CaRE | P: are published rankings artefacts of protocol | D: variance explained by temperature, strategy, interaction; rankings at matched NFE | D: own re-runs, 3 seeds | D: remasking; MAUVE on OpenWebText, LM1B |
| 5 | 2610.02657 Context-tower conversion (abstract only) | D: a method paper | P: protocol-induced score shift for one published model, with the AR parent as contrast | D: own re-evaluation | P: one converted dLLM |
| 6 | 2606.19475 Experimental analysis | D | D: own values for 8 models; no comparison with published values | D: own re-runs | P |
| 7 | 2609.33947 Simple DLMs | P: are baselines under-configured | D: baseline quality after sampler tuning | D: own re-runs | D: MDLM, OpenWebText |
| 8 | 2604.02718 Generative frontiers (abstract only, already in our files) | P | D | D | D: generative perplexity methodology |

No row is S in the quantity column. Row 1 is S in question and scope.

### 4.2 What each closest work says (source facts, with location)

1. **arXiv:2606.29228**. Sec 1, checked on raw HTML: "existing studies report inconsistent
   evaluation results even under seemingly identical evaluation settings, hindering reliable
   evaluation of decoding methods (Nie et al., 2026; Chen et al., 2026b; Liu et al., 2026). For
   instance, the reported accuracy on GSM8K for LLaDA-8B-Instruct exhibits a discrepancy of up to
   9% across different studies, despite using the same decoding method and generation configuration
   (Hu et al., 2025; Wu et al., 2026b; Zheng et al., 2026; Zhu et al., 2026)." Table for
   near-identical templates, checked on raw HTML: Vanilla accuracy 77.10 to 78.17 across eight
   templates, Std 0.355, Range 1.070. Sec 1: the variation appears "even under identical random
   seeds and evaluation settings". Sec 4.3 (fetch extraction): accuracy differs across GPU types
   under identical conditions and FP32 largely removes it; few-shot count and generation length
   also change conclusions. Absent, checked by keyword scan of the raw text ("seed" occurs once,
   in the sentence above; "standard deviation" occurs only for the across-template statistic): any
   seed standard deviation, any table of values collected from prior papers. Absent per fetch
   extraction: any comparison of claimed gains with the variation, any statement that competitor
   baselines are reported low.
2. **arXiv:2510.04019** (fetch extraction of App B.3, Table 2; not checked on raw HTML): "our
   reproduced baselines for LLaDA-8B-Instruct and LLaDA 1.5 are slightly higher than baselines
   reported in the aforementioned works (and that variation exists between these works as well).
   We attribute this to our use of a more amenable system prompt and robust parsing system".
   Table 2 is titled "Comparison of base model accuracies reported in previous work vs. reproduced
   in our work."
3. **arXiv:2602.22661** (fetch extraction of Sec 3.3, App B; not checked on raw HTML): LLaDA-Instruct
   GSM8K official 69.4 against reproduced 74.7; MMLU 65.5 against 69.8; HumanEval 49.4 against 47.0;
   Dream-Instruct GSM8K 81.0 against 82.0. "DLMs are especially sensitive to inference
   hyperparameters, as prior work often relies on task-specific hyperparameter tuning and
   postprocessing".
4. **arXiv:2607.24763**. Sec 1, checked on raw HTML: seven remasking strategies are each "evaluated
   under different step budgets, metrics, and sampling temperatures, producing contradictory
   rankings where the same strategy is reported as best in one paper and worst in another". It
   re-runs; it does not tabulate the seven papers' values (fetch extraction).
5. **arXiv:2610.02657** (abstract): "evaluation protocol substantially affects a published
   500B-token conversion's scores in both directions across tasks, while its AR parent's scores
   vary by less than three points, so comparing dLLMs needs a common protocol."

### 4.3 Inference

- The premise of H5 and its mechanism M1 are published for the flagship cell: a between-paper
  discrepancy of "up to 9%" for LLaDA-8B-Instruct on GSM8K (the paper does not say whether this
  is absolute or relative), attributed experimentally to prompt
  templates, with GPU type, shot count and generation length as further factors (row 1). Rows 2, 3
  and 5 are independent corroborating remarks by method papers.
- Sub-claim (a) is the most exposed. Decoding papers in this cell claim gains of a few points, and a
  reader who has the 9% discrepancy in hand reaches (a) for that cell without further work. That
  step is my inference; row 1 does not make the comparison itself.
- Sub-claim (b), the home-baseline deficit, has no located counterpart in the DLM literature. Its
  exact form exists in information retrieval (Armstrong et al., section 5).
- Sub-claim (c) has no located counterpart: none of rows 1 to 3 reports seed standard deviation.
  Row 4 reports three seeds for a different metric and scope.
- What remains unmeasured by anyone located: a dispersion statistic over at least five papers per
  cell, more than one cell, the ratio to claimed gains, the direction test in (b), the seed ratio in
  (c).

### 4.4 Verdict for H5

**incremental, confidence 0.70.** The headline fact and its leading mechanism are in print for the
main cell, in a paper that is also under review at ICLR 2027 (forum psvNRxzYZv, title changed to
"Understanding Evaluation Inconsistency in Diffusion Large Language Models"). The candidate's
additions are systematic measurement across cells and papers, and two sub-claims, (b) and (c), that
are new inside this literature but follow templates established in other fields.

Single paper most likely to be cited against H5: **arXiv:2606.29228**.

## 5. Methodological cousins outside DLMs (precedents, not scooping)

IDs, titles and first authors were checked in one arXiv API call (E1, abstract level) unless marked.

For H2 (baseline slack, matched-budget comparison):
- arXiv:2205.01966, Helcl et al., "Non-Autoregressive Machine Translation: It's Not as Fast as it
  Seems" and arXiv:2006.10369, Kasai et al., "Deep Encoder, Shallow Decoder: Reevaluating
  Non-autoregressive Machine Translation". Speed claims of non-autoregressive MT against
  under-optimised autoregressive baselines. Nearest cousins in form.
- arXiv:1707.05589, Melis et al.; arXiv:1711.10337, Lucic et al.; arXiv:1907.06902, Ferrari Dacrema
  et al.; arXiv:2007.01547, Schmidt et al.; arXiv:2003.08505, Musgrave et al. Properly tuned old
  baselines match newer methods.
- arXiv:2206.00364, Karras et al. Cited for the image-diffusion convention of comparing samplers on
  quality against NFE. That this paper reports matched-NFE comparisons is E0 (my background, not
  checked in this run).
- Inside DLMs but another sub-area: arXiv:2609.35472 (abstract): guidance loses to a simpler
  baseline once all forward passes are charged to one budget.

For H5 (between-paper variance, weak baselines):
- arXiv:2003.03033, Blalock et al., "What is the State of Neural Network Pruning?" Read via ar5iv
  (fetch extraction): 81 papers aggregated; "Different training and fine-tuning settings can yield
  nearly as much variability as different methods"; "methods often introduce changes in accuracy of
  much less than 1% at reported operating points"; "more than a fourth of our corpus does not
  compare to any previously proposed pruning method". Closest template for H5 (a) and for H2 (a).
- Armstrong, Moffat, Webber, Zobel, "Improvements that don't add up: ad-hoc retrieval results since
  1998", CIKM 2009, pp. 601-610 (no arXiv ID; verified by search result from the authors' page,
  E1): "Baselines are generally weak, often being below the median original TREC system". Exact
  template for H5 (b).
- arXiv:2103.03098, Bouthillier et al., "Accounting for Variance in Machine Learning Benchmarks".
  Template for H5 (c).
- arXiv:2106.15195, Marie et al. (meta-evaluation of 769 MT papers); arXiv:1804.08771, Post (BLEU
  varies by up to 1.8 between reporting configurations); arXiv:1709.06560, Henderson et al.;
  arXiv:1909.03004, Dodge et al.
- Evaluation-harness and prompt variance for LLM benchmarks: arXiv:2405.14782, Biderman et al.;
  arXiv:2310.11324, Sclar et al.; arXiv:2401.00595, Mizrahi et al.; arXiv:2406.10229, Madaan et
  al.; arXiv:2411.00640, Miller.

The three IDs listed as unverified in conjectures.md H5 section 5 are now verified at abstract level
(2103.03098, 2003.08505) or by bibliographic search (Armstrong et al., CIKM 2009).

## 6. Search log

Web search (general tool; strings verbatim):
1. masked diffusion language model acceleration "fewer steps" baseline step-matched comparison speedup disappears LLaDA re-evaluation
2. diffusion language models reproducibility baseline discrepancies across papers LLaDA GSM8K reported accuracy inconsistent evaluation
3. "diffusion language models" benchmark unified re-evaluation of parallel decoding samplers "under a unified" protocol inconsistent results prior work 2026
4. "masked diffusion" language model "random" baseline "same number of function evaluations" OR "matched NFE" OR "equal NFE" confidence unmasking acceleration overstated
5. arXiv 2606.29228 parallel decoding diffusion language models prompt template rankings inconsistent
6. diffusion LLM acceleration "simply reducing" steps baseline "comparable" accuracy Fast-dLLM critique "generation length" padding EOS tokens wasted steps analysis
7. "reality check" OR "are we really making progress" OR "rethinking evaluation" masked diffusion language models decoding strategies 2026 arXiv
8. diffusion LLM decoding "tokens per step" "random top-k" baseline matches adaptive unmasking "at the same NFE" training-free sampler comparison GSM8K HumanEval revisited
9. arXiv 2608 OR 2609 OR 2610 diffusion language models evaluation critique baselines "step budget" acceleration "speed-quality" benchmark unified reproducibility
10. "diffusion language models" "meta-analysis" OR "systematic review" OR "audit" reported results baselines variance across papers 2026
11. openreview.net ICLR 2027 submission diffusion language models evaluation "parallel decoding" baseline fewer steps fair comparison (domain openreview.net)
12. openreview NeurIPS 2026 diffusion language model benchmark evaluation illusion decoding methods reproducibility position paper
13. "masked diffusion" language models samplers benchmark "simple baseline" "top-k" strong "surprisingly" competitive with adaptive unmasking methods under same step budget 2026
14. diffusion LLM "over-provisioned" OR "redundant denoising steps" OR "unnecessary steps" default "steps equal to generation length" LLaDA accuracy unchanged half steps analysis
15. dLLM acceleration papers "speedup" "is largely due to" OR "mostly comes from" OR "can be attributed to" reducing steps of baseline LLaDA 256 steps "weak baseline" Fast-dLLM comparison unfair
16. "Learning Unmasking Policies for Diffusion Language Models" heuristics confidence threshold strong baseline matched NFE result
17. diffusion language model papers "we survey" OR "we reviewed" OR "we audit" reporting practices number of papers report seeds baselines step sweep evaluation checklist dLLM
18. Armstrong Moffat Webber Zobel "Improvements that don't add up: ad-hoc retrieval results since 1998" CIKM 2009 weak baselines
19. benchmark toolkit unified evaluation of diffusion LLM acceleration methods Fast-dLLM dKV-Cache Elastic-Cache KLASS EB-Sampler re-implemented one codebase "same protocol" leaderboard 2026
20. "LLaDA" baseline accuracy "differs from" OR "lower than reported" OR "could not reproduce" OR "discrepancy" GSM8K HumanEval MBPP prior papers evaluation harness dLLM 2026

arXiv export API (search_query, sorted by submittedDate descending):
- A1. abs:"diffusion" AND abs:"language model" AND (abs:"evaluation" OR abs:"benchmark" OR abs:"reproducib") AND (abs:"baseline" OR abs:"steps"), max 100. The fetch tool showed 37 entries back to 2026-09-26 only (truncated).
- A2. (abs:"diffusion language" OR abs:"masked diffusion" OR abs:"discrete diffusion" OR abs:dLLM OR abs:dLLMs) AND (abs:evaluation OR abs:benchmark OR abs:reproducible OR abs:reproducibility OR abs:inconsistent OR abs:matched OR abs:fair), start 30, max 35. Reached back to 2026-09-27 only.
- A3. Same model terms AND (inconsistent, reproducibility, "fair comparison", "matched", tuned, revisiting, rethinking, pitfalls, illusion, audit, overstated, overestimate, "than reported", "evaluation protocol", "evaluation practices"), max 40. totalResults 467; first page only (too broad).
- A4, date-bounded, submittedDate 2026-07-10 to 2026-10-14: same model terms AND (inconsistent, reproducibility, "fair comparison", pitfalls, illusion, audit, overstated, "than reported", "evaluation practices", "compute-matched", "matched NFE", "tuned baselines", "strong baseline", "re-evaluation", "critical examination", "common protocol", "unified protocol"). totalResults 26, all listed and screened by title; 7 flagged and screened by abstract.
- A5, same date bounds: model terms plus LLaDA AND ("prompt template(s)", "across seeds", "seed variance", "evaluation harness", "error bars", "statistical significance", leaderboard, "step budget", "fewer steps", "speed-quality", "early exit", "early stopping", redundant, Pareto). totalResults 27, all screened by title; 11 flagged and screened by abstract sentence.
- A6. id_list verification call for 21 IDs: 2003.03033, 2003.08505, 2103.03098, 1711.10337, 1707.05589, 1709.06560, 1907.06902, 2205.01966, 2006.10369, 1804.08771, 2106.15195, 2405.14782, 2310.11324, 2406.10229, 2401.00595, 2206.00364, 2411.00640, 2007.01547, 1909.03004, 2409.02908, 2604.02718. All 21 returned with matching titles.

OpenReview API (api2.openreview.net/notes/search, type=terms, content=all, source=forum):
- O1. "diffusion language model evaluation baseline", group ICLR.cc/2027/Conference: 32 notes; one relevant (psvNRxzYZv).
- O2. Same term, group NeurIPS.cc/2026/Conference: 0 notes.
- O3. "masked diffusion sampler matched NFE benchmark evaluation", ICLR 2027: 18 notes; none an evaluation audit.
- O4. "diffusion large language models parallel decoding speed-quality trade-off evaluation", ICLR 2027: 2 notes (psvNRxzYZv; 0nl7tNIEOi, an information-theoretic analysis).
- O5. "diffusion language models evaluation inconsistency reproducibility", no group: 3 relevant notes, none new.
- O6. "diffusion language fewer steps baseline acceleration reality check", ICLR 2027: no DLM evaluation paper; one cousin on vision-language-action acceleration benchmarks (1ivlJ9lC5d).

Screening counts: about 150 arXiv feed titles (with overlap between queries) and 55 OpenReview
titles screened; 9 abstracts read in full and 21 more checked by a one-line gist; 11 papers read at
section level.

## 7. Residual risk

- Absence of hits is weak evidence. The date-bounded arXiv queries are keyword-bound: a scooping
  paper that says, for example, "step-normalised" or "budget-aware" without any of my terms is
  missed. Volume is high: the broad query A2 returned 35 hits for four days in late September
  2026.
- NeurIPS 2026 was effectively not searched. ICLR 2027 was searched with five term queries, not by
  listing.
- Exa and Semantic Scholar were not used, so citation-graph neighbours of 2606.29228, 2609.33947
  and 2510.04767 were not walked. Papers citing those three are the most likely place for a
  scooping result to appear.
- Both dangerous papers are in the ICLR 2027 cycle. Revised versions or rebuttal-stage additions
  (for example a cross-paper table added to 2606.29228 at a reviewer's request) could close the
  gap for H5 (a) at any time.
- Seven of the eleven section-level readings rest on quotes relayed by the fetch tool's model.

## 8. Out-of-scope observations (for the orchestrator; no recommendation attached)

These are source facts met during the audit that bear on whether the candidates are true, which is
not this agent's question.
- ParallelBench Sec 6 states that threshold samplers achieve "superior trade-offs" to static top-k
  on its tasks (checked on raw HTML).
- A search snippet attributed to dLLM-Cache (arXiv:2506.06295) says that reducing denoising steps
  to 32 drops accuracy to 22.25% while the method keeps 70.66%. Not opened; E1 snippet.
- 2606.29228 concludes that parallel decoding methods "consistently underperform the vanilla
  baseline" across most templates. Its near-identical-template table gives 77.64 (one token per
  step), 74.28 (Top-K k=2) and 66.02 (Top-K k=4) mean GSM8K accuracy at generation length 128
  (checked on raw HTML).
- conjectures.md H2 section 5 describes 2606.29228 only as "rankings depend on the prompt
  template" and "inconsistent results across prior parallel-decoding studies"; the Sec 1 figure
  ("up to 9%" across four studies for LLaDA-8B-Instruct on GSM8K) and the fixed Top-K rows are
  not recorded in H2 section 5 or H5 section 5.

## 9. Ledger rows added

papers: P0097 (2609.33947), P0098 (2607.24763), P0099 (2508.19982), P0100 (2602.22661), P0101
(2510.04019), P0102 (2610.02657), P0103 (2609.35472), P0104 (2606.29228, supersedes P0079).
claims: C0009, C0010, C0011.
