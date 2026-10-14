# Title-and-abstract screening criteria v1 (fixed prompt; protocol sections 2 and 4)

You are screening records for a systematic review of diffusion language models and unified
multimodal diffusion models. Decide from the title and abstract only. Do not use outside knowledge
of the paper.

INCLUDE if all of the following are plausible from the title and abstract:
- I1. The record proposes, analyses, evaluates or benchmarks either (a) a diffusion model
  (discrete or continuous state space, including masked or absorbing diffusion, discrete flow
  matching, and diffusion on embeddings or the simplex) whose output includes natural-language
  text or code, or (b) a unified model that both understands and generates across text and at
  least one other modality using a diffusion, masked-generative or discrete-flow component.
- I2. It is a primary study with a method, theory or empirical result.
- I4. First public version from 2021-01-01 on.

EXCLUDE with one code if any applies:
- X1 diffusion for images, audio, video, molecules, proteins or other non-text data only, with no
  text generation and no unified understanding-and-generation;
- X2 text is used only as a conditioning input (for example text-to-image models that do not
  generate text and do not unify understanding with generation);
- X3 secondary study (survey, tutorial, position paper). A benchmark that evaluates models
  empirically is a primary study and is included;
- X4 no method, theory or empirical result;
- X7 application that uses an existing diffusion language model unchanged and reports no
  model-level finding;
- X8 before 2021-01-01 or not in English.

UNCLEAR: the abstract is missing or does not let you decide. Unclear records go to full-text
screening. When in doubt between include and exclude, choose UNCLEAR.

Notes on frequent cases:
- Autoregressive models, VAEs, GANs or flows with no diffusion component: X1 if non-text, else
  exclude as X4 only if there is no diffusion at all (use code X0 "no diffusion component").
- Speculative decoding or drafting that uses a diffusion LM as drafter: include.
- Diffusion models for code, mathematics or structured text (SQL, tables as text): include.
- Diffusion LMs used for reinforcement learning, alignment or reasoning studies: include.
- Vision-language models that use diffusion only for image generation with a frozen LLM and no
  unified training: X2 unless the abstract presents them as unified understanding-and-generation.

OUTPUT: one JSON object per record, one per line, nothing else:
{"sid": "<sid>", "decision": "include" | "exclude" | "unclear", "code": "<X0|X1|X2|X3|X4|X7|X8 or empty>", "reason": "<at most 15 words>"}
