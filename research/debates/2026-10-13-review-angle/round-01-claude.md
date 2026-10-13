# Claude, round 1: which review to write, and around which conjecture

Context. Two students and a professor, one 12 GB laptop GPU, strong tooling for systematic
reading. Goal: one review article on diffusion language models (masked or discrete diffusion LLMs
such as LLaDA, Dream, MDLM, SEDD) and unified multimodal discrete-diffusion models (MMaDA, UniDisc,
Show-o, FUDOKI, Lumina-DiMOO), aimed at ACM Computing Surveys (35 pages, surveys only, a new result
is in scope only if it organises the material). Narrative surveys already exist: "A Survey on
Diffusion Language Models" (arXiv 2508.10875) and a 2025 survey of discrete diffusion in language
and multimodal models. A later research article will test the review's conjecture experimentally.

My claims, for you to attack:

1. A third narrative taxonomy would be rejected as redundant. The defensible contribution is a
   systematic review: registered search and inclusion protocol, quantitative extraction of every
   included paper's reported numbers and protocols, a reporting audit (seeds, intervals,
   compute-matched baselines, claim-versus-table consistency), and one organising conjecture.

2. Lead conjecture CA, "conditional synergy". In unified understanding-and-generation models,
   cross-task benefit is not a consequence of unification itself. It appears only when both tasks
   read and write one visual token space under one likelihood; it is bounded by the information
   rate of that tokenisation; and at matched backbone size and data, models with decoupled visual
   pathways (Janus-style) are not worse on either task. Evidence without training: meta-regression
   of published understanding scores and generation scores on design factors across all unified
   models found (shared or decoupled visual encoder, discrete or continuous tokens, autoregressive,
   diffusion or hybrid objective), with backbone size and data as covariates; and a census of how
   many synergy claims rest on a task-removal ablation.

3. Alternative CB, "commitment trilemma". A sampler built on a factorised denoiser can have at
   most two of: free generation order, few parallel steps, exact joint sampling. Evidence:
   published speed and quality numbers collapse onto one frontier when expressed per function
   evaluation per token; exact computation on small synthetic distributions.

4. I rank CA above CB because (a) parallel-decoding theory is crowded (ParallelBench 2510.04767,
   total-correlation bounds, "Breaking the Factorization Barrier" 2603.00045), so CB risks being a
   restatement of known theorems, while causal evidence on synergy is sparse; (b) CA hands the
   follow-up research article a clean causal test on a frozen model.

5. A meta-regression over published tables is legitimate evidence for a review-level conjecture
   even though the numbers come from heterogeneous protocols, provided heterogeneity is modelled
   (random effects per benchmark and per paper) and the limitation is stated.

6. Scope should cover both text DLMs and unified multimodal models in one article rather than
   narrowing to multimodal only, because the journal rewards breadth and the multimodal models
   inherit their objective and samplers from the text ones.

Where I am least sure: claim 5 (whether published numbers are comparable enough to regress on),
and whether CA is already an accepted view after benchmarks that test unified models for real
synergy. Tell me where this plan fails.
