# Claude, round 5: the inventory you asked for, and two candidates to lead

## Your settling test was run (keyword level, then a reading sample is in progress)
Captions of 535 papers were scanned by script. Papers with at least one caption on: a sweep over
denoising or sampling steps 268; an ablation 401; a remasking contrast 53; an
understanding-generation synergy contrast 18. Variation across runs is mentioned in 62 percent of
papers, intervals or significance in 21 percent; only 21 of the 268 step-sweep papers mention
seeds or error bars in a step caption. Two agents are now reading a stratified sample of 62 papers
to count truly matched, numeric contrasts. So I concede round 4 in full: the title no longer says
"meta-analysis" (it returns only if a question reaches 8 matched contrasts from 5 groups), synergy
is dropped as an organising theme, and inverse-variance pooling is unlikely; expect slope and
sign-based syntheses with intervals clustered by paper.

The professor's instruction since then: a **critical** review matters most, with a quality
appraisal of every included study. An independent agent proposed seven candidates. I select two.

## H2, slack conjecture (inference papers; 99 of 164 have a step caption)
For a paper reporting a speed-up at comparable quality: headline speed-up S_head = T_base /
T_method in forward passes. Attributable speed-up S_att = T*_base(Q_method) / T_method, where
T*_base(q) is the smallest step count at which the same paper's sweep of the baseline sampler
reaches quality q minus eps (eps = reported seed standard deviation, else 0.5 points). Slack share
sigma = 1 - log S_att / log S_head, clipped to [0, 1]. Claims: (a) fewer than one third of papers
reporting a headline speed-up also sweep the baseline down to the method's step count; (b) where
computable, median sigma is at least 0.5; (c) within a paper, sigma does not fall as generation
length grows. Scope: training-free samplers on a frozen masked-diffusion checkpoint. Refuted if
the proportion in (a) is at least one half or the median in (b) is below 0.25.

## H5, noise-floor conjecture (rigour of the evidence base)
A cell is (checkpoint, benchmark, metric, generation length, steps, sampler, shots). It qualifies
if at least 5 papers with disjoint author lists report a baseline value for it. sigma_B is the
standard deviation of that baseline value across papers. Delta is each paper's own favoured-method
minus baseline in that cell. Claims: (a) in most qualifying cells median |Delta| is below
2 sigma_B; (b) a paper's own baseline value falls below the cross-paper median of the cell in more
than half of cases where it proposes a competing method; (c) sigma_B is at least twice the
within-paper seed standard deviation. Candidate cells: LLaDA-8B and Dream-7B on GSM8K, MATH500,
HumanEval, MBPP (captions naming LLaDA and GSM8K together: 61 papers).

## My positions, for you to attack
1. H5 does not break the rule we agreed in round 3. It regresses nothing; it uses the dispersion
   of one nominally identical cell as a yardstick for within-paper contrasts. Protocol differences
   hidden under one name are the finding, not a nuisance.
2. H2 and H5 together give the review one organising claim that suits a critical review: reported
   progress in this literature is typically smaller than two uncontrolled sources of variation,
   the slack in the baseline's own step schedule and the between-paper spread of the baseline.
3. Both are testable from published tables alone, and both can be checked later on frozen
   checkpoints by rerunning baselines on one GPU.
4. H2 leads and H5 supports, because H2's quantities come entirely from within one paper.
5. The main risks: H2 may be anticipated by work on early answer convergence and by ParallelBench;
   H5(b) may be confounded if papers pick cells where their method happens to win; cells may not
   reach 5 disjoint papers once generation length and steps are matched exactly.

Attack the definitions first. Which claim fails on a careful reading of real tables?
