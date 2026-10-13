## Claim-by-claim

1. **NEEDS-EVIDENCE.** A systematic protocol and reporting audit could distinguish this review, but redundancy is not established just by calling existing works “narrative.” Compare their search coverage, extraction, and audit methods against the proposed review before deciding the gap. Also, “every included paper’s reported numbers” needs a defined extraction scope to be feasible and reproducible.

2. **NEEDS-EVIDENCE.** CA is a promising question, but its proposed mechanism bundles several claims: shared visual token space, shared likelihood, a tokenisation information-rate bound, and no task regression from decoupling. The transcript gives no evidence for these links. Published benchmark scores alone would not establish the causal “only when” claim; designs, data, and training differ together. The Janus comparison also needs a precise definition of “not worse” and matched training conditions.

3. **REJECT.** As stated, the trilemma is too broad: “factorised denoiser,” “free generation order,” “few parallel steps,” and “exact joint sampling” are not operationally defined, and no assumptions delimit the sampler class. A counterexample under one plausible interpretation could invalidate the universal “at most two” claim. The proposed frontier plot would describe empirical tradeoffs, not prove the trilemma.

4. **NEEDS-EVIDENCE.** The transcript’s citations and characterisation of the literature are not verified here, so they cannot support the ranking. Even if parallel-decoding theory is crowded, that does not show CA is novel or causally testable with a frozen model. A frozen-model test cannot isolate training-time effects of shared versus decoupled pathways.

5. **REJECT.** Random effects for benchmark and paper do not make heterogeneous scores comparable. They do not correct differences in evaluation protocol, data contamination, prompt or decoding choices, or selective reporting. A regression could be a descriptive map, but treating its coefficients as evidence for CA would overstate what the data support. The review should first assess overlap and comparability, then report associations only where defensible.

6. **NEEDS-EVIDENCE.** Breadth may suit the journal, but covering text DLMs and unified multimodal systems risks two adjacent reviews joined by a weak inheritance claim. The scope should follow a shared analytic question and a demonstrable gap in prior surveys, not presumed journal preference.

## Strongest counter-argument

The main position—lead with CA and use cross-paper meta-regression as review-level evidence—risks making the review’s central conjecture look empirically supported when the available comparisons are confounded. A disciplined systematic map, with CA framed as a hypothesis and the reporting audit as the contribution, is more defensible until comparable evidence exists.

## Cheapest settling observation

Build a small comparison matrix of the closest existing surveys and the proposed review: search protocol, included-paper coverage, quantitative extraction, and reporting-bias audit. It would quickly show whether the systematic-review contribution is genuinely distinct. For CA, first check whether published studies contain any matched shared-versus-decoupled comparisons; if not, the meta-regression cannot settle the causal claim.

## POSITION

Write a systematic review only if the coverage comparison confirms a gap. Frame CA as a conjecture, not a finding.

## CONCESSIONS

The review’s reporting audit could be a real contribution. Text DLMs and multimodal models may belong together if the organizing question genuinely connects them.

## OPEN DISAGREEMENTS

Whether CA is novel and whether published results support a useful quantitative synthesis remain unresolved.

## WHAT WOULD CHANGE MY MIND

A coverage matrix showing prior surveys lack this audit, plus a set of sufficiently matched comparisons that can test CA’s design-level predictions.