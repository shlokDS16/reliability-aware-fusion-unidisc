# Scopus queries run 2026-10-16 (Chrome, VIT institutional access; D0031)

Plan: the union of S1, S2 (protocol), S1', S2' (D0026) is run in five queries; S1''/S2'' (D0027) are
applied locally afterwards. Scopus processes AND NOT after OR and AND, so the parts that carry NOT
clauses are run separately, verbatim from the sheet (S1p-A2-r2, S1p-A3-r4, S1p-B, S1p-C). Q1 is a
superset of S1, S2, S1':A1, S1':A2-r1, S1':A3-r1..r3, S2':M, S2':VLA (it widens the language clause of
the S1 terms to S1':A2's word list).

Q1:
TITLE-ABS-KEY(("diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms OR "non-autoregressive language model*") OR (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*" OR "absorbing state" OR "any-order" OR "discrete flow matching" OR "diffusion LLM" OR ("non-autoregressive" AND diffusion)) AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) OR (("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) OR (("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms))) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)

Q2 = S1p-A2-r2, Q3 = S1p-A3-r4, Q4 = S1p-B, Q5 = S1p-C: verbatim from research/review/corpus/subscription-search-sheet.md (Scopus, S1' section).

Hit counts and export files: filled in below as run.
Run 2026-10-16 (IST), Chrome, VIT institutional access, "Documents" tab (Preprints tab not used):
- Q1 combined: 876 documents
- Q2 S1p-A2-r2: 530
- Q3 S1p-A3-r4: 134
- Q4 S1p-B: 1,670
- Q5 S1p-C: 836
Export blocked: Scopus export needs a personal Scopus account signed in (user to sign in); user approved downloading the five CSVs (citation, bibliographic, abstract and keywords). Rerun each query from its results URL after sign-in, then export.
