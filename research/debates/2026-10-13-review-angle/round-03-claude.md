# Claude, round 3: concessions, new evidence, a revised proposal

## Concessions (you were right)
- Claim 5. Random effects do not make scores from different protocols comparable. Cross-paper
  regression of raw scores is dropped as evidence; it stays only as a descriptive map.
- Claim 3. CB as I wrote it has no defined sampler class and proves nothing with a frontier plot.
- Claim 2. CA bundled four claims, and "only when" is causal language that published tables cannot carry.
- Claim 4. A frozen-model experiment cannot isolate training-time effects of shared against
  decoupled pathways. The follow-up article can test mediation in a trained model, not the design counterfactual.

## New evidence since round 1 (from a literature agent; levels stated)
- Your settling test for claim 1 was run. 14 existing surveys in the area were scanned in full
  text for protocol terms and headings (a keyword-and-heading scan, not a careful read): none has a
  PRISMA-style protocol, none audits reporting practice. One (arXiv 2509.24435) calls itself
  systematic but gives no search strings or screening counts. Two (2508.10875 Sec. VI, 2505.02567
  Table IV) tabulate numbers without pooling or intervals. 18 further surveys were seen at abstract
  level only. So the gap looks real but is not yet fully established.
- CA is not new as a qualitative statement. arXiv 2609.01607 (1 Sep 2026) says synergy is
  "possible but highly conditional"; 2607.04423 Sec. 3.2 reports transfer strongest with a shared
  backbone and unified encoder and weak for separate pathways; RealUnify (2509.24897) reports no
  genuine synergy. No pooled estimate and no census of task-removal ablations was found.
- For CB the closest are 2602.00286 and ParallelBench Theorem 1; no three-way statement was found.

## Revised proposal for you to attack
1. The title is now fixed as "...: A Systematic Review and Meta-Analysis", so the quantitative
   core must be a real meta-analysis. Unit of analysis: the matched within-paper contrast (an
   ablation or controlled comparison where the paper itself holds everything else fixed),
   converted to a standardised effect and pooled across papers per pre-registered question.
2. Candidate questions: (Q1) effect on understanding of adding or removing the generation
   objective; (Q2) shared against decoupled visual encoder; (Q3) quality against number of
   denoising steps within one model; (Q4) remasking on against off; (Q5) reinforcement-learning
   post-training against its own supervised baseline.
3. New conjecture CD, "step-scaling law". Theory gives a sampling error of order 1/T for T
   parallel steps, governed by dependence among tokens unmasked together. Conjecture: within-paper
   step sweeps, re-expressed as quality gap to the many-step limit against tokens revealed per
   step, collapse onto one curve with a common exponent, and the residual is explained by task
   type (tasks with strong token dependence, such as arithmetic reasoning, deviate more than
   captioning or classification-style answers). Falsified if exponents differ by model family
   beyond their intervals or if task type does not order the residuals.
4. CA is kept only as question Q1 and Q2 with a pooled estimate, credited to the 2026 papers above.

Rank CD, a formalised CB, and quantified CA as the organising result, and say which pre-registered
question you expect to have too few matched contrasts to pool.
