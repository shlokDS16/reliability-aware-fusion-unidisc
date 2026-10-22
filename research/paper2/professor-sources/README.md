# Paper 2 sources from the supervising professor (received 2026-10-22)

Direction set by the professor: a research paper (not a survey) proposing something new on **masked discrete diffusion
models**, especially unified multimodal ones (text, image, speech or audio). The PDFs in this folder are kept locally
and are not committed (see .gitignore); re-download them from the arXiv links if missing.

| # | Source as given | What it is | Local file |
|---|---|---|---|
| 1 | https://github.com/VITA-MLLM/Omni-Diffusion | Code for Omni-Diffusion (ICML 2026): "the first any-to-any multimodal language model built on a mask-based discrete diffusion model", jointly modelling discrete text, image and speech tokens. Repo has SFT training, inference and evaluation scripts; weights at Hugging Face `lijiang/Omni-Diffusion`; uses GLM-4-Voice tokenizer/decoder and MAGVIT-v2 image tokenizer. Base model, sizes, hardware and licence not stated on the page. Project page: https://omni-diffusion.github.io | 2603.06577v2.pdf |
| 2 | "Mask-based Discrete Diffusion Model" (1st PDF) | Li et al., "Omni-Diffusion: Unified Multimodal Understanding and Generation with Masked Discrete Diffusion", arXiv:2603.06577v2 (Nanjing Univ., Tencent Youtu, CASIA) | 2603.06577v2.pdf |
| - | 2nd PDF | Li et al., "Sparse-LaViDa: Sparse Multimodal Discrete Diffusion Language Models", arXiv:2512.14008v2 (Adobe, UCLA): truncates redundant masked tokens at each step with register tokens and a matching training attention mask; up to 2x speed-up on LaViDa-O for text-to-image, editing and maths reasoning | 2512.14008v2.pdf |
| 3 | "Explore similar kinds of papers" | arXiv search, 35 papers (metadata only, unfiltered) | ../related-arxiv-2026-10-22.md |
| 4 | https://homepage.jackli.org/projects/lavida/ | LaViDa, arXiv:2505.16839: multimodal discrete diffusion language model for vision-language tasks (vision encoder + MLP projection + non-causal Transformer; complementary masking, prefix KV cache, timestep shifting); code at github.com/jacklishufan/LaViDa. Follow-up LaViDa-O, arXiv:2509.19244 (ICLR 2026), unified understanding and generation; Sparse-LaViDa builds on it | 2505.16839.pdf, 2509.19244.pdf |
| 5 | https://machinelearning.apple.com/research/tri-modal-masked-diffusion | Béthune et al., "The Design Space of Tri-Modal Masked Diffusion Models", arXiv:2602.21472 (Apple; NeurIPS per the page): text, image-text and audio-text MDM pretrained from scratch, 3B parameters on 6.4T tokens; scaling laws, modality mixing ratios, noise schedules, batch-size SDE reparameterisation, sampling defaults. Code not stated | 2602.21472.pdf |
| - | Reference survey (format model) | Yang et al., "Diffusion Models: A Comprehensive Survey of Methods and Applications", ACM Computing Surveys 56(4), 2023 | yang2023-diffusion-survey-csur-3626235.pdf |

Notes for the next session:
- Before proposing an idea, run the novelty check against these and the related list; the area moves weekly
  (e.g. LLaDA2.0-Uni 2604.20796, LLaDA-o 2603.01068, Intern Lumina U2 2610.20818, training-free self-correction for
  multimodal MDMs 2602.02927, understanding/generation balance 2602.01362).
- The survey's open problems (Section 9: dependency-aware commitment, value-rule bracketing, cross-modal commitment
  schedules) are candidate seeds; any experiment must run on the 12 GB laptop GPU (check the GPU-crash memory) or with
  the user's approval for other compute.
