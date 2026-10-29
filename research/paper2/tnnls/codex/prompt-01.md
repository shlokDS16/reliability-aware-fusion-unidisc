You are an external reviewer for IEEE TNNLS (hostile but fair; you review as an area chair would, and as an AI evaluator a journal might use). Read these files in this repository (read-only; do not modify anything):
- research/paper2/tnnls/DESIGN-A-2026-10-29.md (method SCER: shared-context exact ratio scoring of one-token caption edits in a unified masked discrete diffusion model, training-free)
- research/paper2/tnnls/DESIGN-B-2026-10-29.md (method CANAL: training-free per-word Bayes posterior with image visible vs masked, detect/locate/correct wrong words with a conformal-risk-control bound on false edits, region-masking evidence maps)
- research/paper2/tnnls/EXEMPLARS-2026-10-29.md (what strong TNNLS papers contain)
- paper2/sections/results.tex (the preregistered GATE study; main result negative)
Constraints of the authors: one 12 GB laptop GPU, no training beyond a few GPU-hours, submission by Sunday 1 Nov 2026, backbone UniDisc 1.4B (optionally Omni-Diffusion 8B 4-bit).
Answer, concisely and concretely:
1. For each method: is it genuinely new? Name the closest prior work you know (with arXiv ids or venues) and the exact delta. Do not invent papers; say "unsure" when unsure.
2. The top 5 weaknesses a TNNLS reviewer (or an AI evaluator like you) would raise against a paper built on each, ranked by severity.
3. Would combining them (SCER for exact scoring + CANAL for calibrated detect/locate/repair, with the GATE study as analysis) make a stronger paper? What is the single strongest framing and claim that is defensible?
4. What experiment or result would most convincingly show it beats corporate-scale models (CLIP, SigLIP, BLIP-2, VQAScore) on something that matters, and where should the authors expect to lose?
5. Any mathematical claim in the designs you believe is wrong (give a counterexample).
Write your answer in English, under 1200 words.
