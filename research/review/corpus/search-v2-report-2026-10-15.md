# Search v2 report, 2026-10-15 (decision D0026)

Agent: lit-scout. Brief: D0026 items 1, 2, 4 and the follow-on tasks (revise S1/S2, rerun every accessible source, merge, string-filter the snowball records, enrich abstracts, update the subscription sheet). Nothing here is a screening decision. Every count is read from the JSON files named in section 10; the tools that produce them are `tools/string_rounds.py`, `tools/search_sources.py`, `tools/merge_new_records_v2.py`, `tools/make_search_sheet_v2.py`.

## 1. Headline

- Recall of the 540 seed entries on title and abstract, locally: S1/S2 453/540, S1'/S2' 525/540. Multimodal DLMs (MM28): 26/28 to 28/28. Random 50 (R50): 40/50 to 47/50.
- Precision proxy (random 200 titles of the 539 records of the 14,794 collected earlier that S1'/S2' add; seed 20261017): 67 look in scope, 46 unclear, 87 other.
- Precision on what the databases returned (stratified sample of the queue, 200 titles, seed 20261018): an estimated 12% of the 6,376 queued records look in scope, 18% in scope or unclear (section 2.4).
- New records not in `screening/records.jsonl`: 19,328 (database searches 6,252, snowballing only 13,076). v1 had 14,794.
- Snowball-only records marked ineligible by the string filter: 12,952; snowball-only records that match a string and go to screening: 124.
- **To screen: 6,376** (6,252 database records + 124 string-matching snowball records). Still without an abstract after enrichment: 598 (482 database, 116 snowball).

## 2. String revision (D0026 item 1)

**Why.** The pilot criterion of protocol section 3 (all 28 MM28 records and a random 50 others) was not met: combined searches retrieved 27/28 MM28, 41/50 R50, 470/540 of 540 entries. The 70 entries not retrieved all fail S1 and S2 on their own title and abstract (local test), so the strings and not the sources limit recall. The 540 entries are 539 distinct arXiv IDs (2506.17298 is listed twice); counts below are over entries, as in `pilot-recall-2026-10-15.json`.

### 2.1 Why each of the 70 missed entries fails S1 and S2, and what captures it now

Reasons, in groups (entries per group): NLP task or text generation with a diffusion model: 21; name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion): 10; continuous or latent diffusion language model: 9; out of scope: image, video or foundation model without text (X1): 8; diffusion drafter for speculative decoding: 7; out of scope: protein or molecule (X1): 5; context clause (discrete or masked diffusion, no language word): 4; other vocabulary (any-order, non-autoregressive language models; no diffusion term): 2; dropped by an exclusion, arguably in scope: 2; no diffusion or flow term in title or abstract: 1; vision-language-action: 1.

| arXiv | Title | Why S1 and S2 fail | Group | S1' / S2' part |
|---|---|---|---|---|
| 2502.09992 | Large Language Diffusion Models | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':B/S1':C |
| 2303.07576 | Diffusion Models in NLP: A Survey | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2209.03003 | Flow Straight and Fast: Learning to Generate and Transfer Data with Re | S1: none of its phrases; S2: no group-A phrase | out of scope: image, video or foundation model without text (X1) | not captured |
| 2011.13456 | Score-Based Generative Modeling through Stochastic Differential Equati | S1: none of its phrases; S2: no group-A phrase | out of scope: image, video or foundation model without text (X1) | not captured |
| 2010.02502 | Denoising Diffusion Implicit Models | S1: none of its phrases; S2: no group-A phrase | out of scope: image, video or foundation model without text (X1) | not captured |
| 2006.11239 | Denoising Diffusion Probabilistic Models | S1: none of its phrases; S2: no group-A phrase | out of scope: image, video or foundation model without text (X1) | not captured |
| 1907.05600 | Generative Modeling by Estimating Gradients of the Data Distribution | S1: none of its phrases; S2: no group-A phrase | out of scope: image, video or foundation model without text (X1) | not captured |
| 1503.03585 | Deep Unsupervised Learning using Nonequilibrium Thermodynamics | S1: none of its phrases; S2: no group-A phrase | out of scope: image, video or foundation model without text (X1) | not captured |
| 2608.10615 | Simplex Relaxation for Discrete Diffusion | S1: phrase 'discrete diffusion' but no language word; S2: no group-A phrase | context clause (discrete or masked diffusion, no language word) | S1':A2 |
| 2607.05722 | Nemotron-Labs-Diffusion: A Tri-Mode Language Model Unifying Autoregres | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':C |
| 2603.21342 | Generalized Discrete Diffusion from Snapshots | S1: phrase 'discrete diffusion' but no language word; S2: no group-A phrase | context clause (discrete or masked diffusion, no language word) | S1':A2 |
| 2509.13866 | Masked Diffusion Models as Energy Minimization | S1: phrase 'masked diffusion' but no language word; S2: no group-A phrase | context clause (discrete or masked diffusion, no language word) | S1':A2 |
| 2507.19227 | Jailbreaking Large Language Diffusion Models: Revealing Hidden Safety  | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':B/S1':C |
| 2402.04997 | Generative Flows on Discrete State-Spaces: Enabling Multimodal Flows w | S1: phrase 'discrete diffusion' but no language word; S2: no group-A phrase | out of scope: protein or molecule (X1) | not captured |
| 2310.09930 | FiLM: Fill-in Language Models for Any-Order Generation | S1: none of its phrases; S2: no group-A phrase | other vocabulary (any-order, non-autoregressive language models; no diffusion term) | S1':A3 |
| 2605.14531 | Language Generation as Optimal Control: Closed-Loop Diffusion in Laten | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':B/S1':C |
| 2605.11577 | BitLM: Unlocking Multi-Token Language Generation with Bitwise Continuo | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':A1/S1':B/S1':C |
| 2604.24416 | Scaling Properties of Continuous Diffusion Spoken Language Models | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':C |
| 2604.02028 | Why Gaussian Diffusion Models Fail on Discrete Data and How to Prevent | S1: none of its phrases; S2: no group-A phrase | dropped by an exclusion, arguably in scope | not captured |
| 2510.04573 | LaDiR: Latent Diffusion Enhances LLMs for Text Reasoning | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':C |
| 2507.12469 | Perfect diffusion is $\mathsf{TC}^0$ -- Bad diffusion is Turing-comple | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':C |
| 2402.19009 | Unified Generation, Reconstruction, and Representation: Generalized Di | S1: none of its phrases; S2: no group-A phrase | dropped by an exclusion, arguably in scope | not captured |
| 2307.13949 | How Does Diffusion Influence Pretrained Language Models on Out-of-Dist | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':C |
| 2304.12519 | GlyphDiffusion: Text Generation as Image Generation | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2302.10025 | DINOISER: Diffused Conditional Sequence Learning by Manipulating Noise | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':B |
| 2211.15089 | Continuous diffusion for categorical data | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':B |
| 2208.00638 | Composable Text Controls in Latent Space with ODEs | S1: none of its phrases; S2: no group-A phrase | no diffusion or flow term in title or abstract | not captured |
| 2206.05895 | Latent Diffusion Energy-Based Model for Interpretable Text Modeling | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':B |
| 2511.01718 | Unified Diffusion VLA: Vision-Language-Action Model via Joint Discrete | S1: none of its phrases; S2: no group-A phrase | vision-language-action | S2':VLA |
| 2509.06040 | BranchGRPO: Stable and Efficient GRPO with Structured Branching in Dif | S1: none of its phrases; S2: no group-A phrase | out of scope: image, video or foundation model without text (X1) | not captured |
| 2305.04465 | Can Diffusion Model Achieve Better Performance in Text Generation? Bri | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2608.13524 | DARTree: Speculative Diffusion Decoding with Autoregressive Draft Tree | S1: none of its phrases; S2: no group-A phrase | diffusion drafter for speculative decoding | S1':B/S1':C |
| 2608.05448 | DBLAST: Dependent Block Drafting for Stochastic Speculative Decoding | S1: none of its phrases; S2: no group-A phrase | diffusion drafter for speculative decoding | S1':A1/S1':B/S1':C |
| 2607.25852 | AngelSpec: Towards Real-World High Performance Inference with Speculat | S1: none of its phrases; S2: no group-A phrase | diffusion drafter for speculative decoding | S1':A1/S1':B/S1':C |
| 2606.31315 | BlockPilot: Instance-Adaptive Policy Learning for Diffusion-based Spec | S1: none of its phrases; S2: no group-A phrase | diffusion drafter for speculative decoding | S1':B |
| 2606.02091 | DFlare: Scaling Up Draft Capacity for Block Diffusion Speculative Deco | S1: none of its phrases; S2: no group-A phrase | diffusion drafter for speculative decoding | S1':A1/S1':B/S1':C |
| 2606.01813 | Cost-Aware Diffusion Draft Trees for Speculative Decoding | S1: none of its phrases; S2: no group-A phrase | diffusion drafter for speculative decoding | S1':A1/S1':B/S1':C |
| 2604.12989 | Accelerating Speculative Decoding with Block Diffusion Draft Trees | S1: none of its phrases; S2: no group-A phrase | diffusion drafter for speculative decoding | S1':A1/S1':B/S1':C |
| 2602.23792 | Divide and Conquer: Accelerating Diffusion-Based Large Language Models | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':C |
| 2512.21336 | Optimizing Decoding Paths in Masked Diffusion Models by Quantifying Un | S1: phrase 'masked diffusion' but no language word; S2: no group-A phrase | context clause (discrete or masked diffusion, no language word) | S1':A2/S1':A3 |
| 2510.11052 | Latent Refinement Decoding: Enhancing Diffusion-Based Language Models  | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':B/S1':C |
| 2509.23094 | d$^2$Cache: Accelerating Diffusion-Based LLMs via Dual Adaptive Cachin | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':C |
| 2406.01572 | Unlocking Guidance for Discrete State-Space Diffusion and Flow Models | S1: none of its phrases; S2: no group-A phrase | out of scope: protein or molecule (X1) | not captured |
| 2512.17065 | XLM: A Python package for non-autoregressive language models | S1: none of its phrases; S2: no group-A phrase | other vocabulary (any-order, non-autoregressive language models; no diffusion term) | S1':A3 |
| 2604.24089 | BiMol-Diff: A Unified Diffusion Framework for Molecular Generation and | S1: none of its phrases; S2: no group-A phrase | out of scope: protein or molecule (X1) | not captured |
| 2507.19081 | Arg-LLaDA: Argument Summarization via Large Language Diffusion Models  | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':B |
| 2506.21557 | Debunk and Infer: Multimodal Fake News Detection via Diffusion-Generat | S1: none of its phrases; S2: no group-A phrase | out of scope: image, video or foundation model without text (X1) | not captured |
| 2501.00862 | DiffETM: Diffusion Process Enhanced Embedded Topic Model | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2410.22971 | Private Synthetic Text Generation with Diffusion Models | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2409.13739 | Table-to-Text Generation with Pretrained Diffusion Models | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2404.10763 | LaDiC: Are Diffusion Models Really Inferior to Autoregressive Counterp | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2404.08938 | Improved Paraphrase Generation via Controllable Latent Diffusion | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2404.06760 | DiffusionDialog: A Diffusion Model for Diverse Dialog Generation with  | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2402.17011 | DiffuCOMET: Contextual Commonsense Knowledge Diffusion | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2403.00808 | IPED: An Implicit Perspective for Relational Triple Extraction based o | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2402.15289 | Let's Rectify Step by Step: Improving Aspect-based Sentiment Analysis  | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2402.10699 | Thinker-DDM: Modeling Deliberation for Machine Translation with a Drif | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B/S1':C |
| 2401.03514 | ROIC-DM: Robust Text Inference and Classification via Diffusion Model | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':C |
| 2310.15587 | ScanDL: A Diffusion Model for Generating Synthetic Scanpaths on Texts | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B/S1':C |
| 2310.15296 | DeTiME: Diffusion-Enhanced Topic Modeling using Encoder-decoder based  | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B/S1':C |
| 2310.10605 | ForceGen: End-to-end de novo protein generation based on nonlinear mec | S1: none of its phrases; S2: no group-A phrase | out of scope: protein or molecule (X1) | S1':A1 |
| 2308.15459 | ParaGuide: Guided Diffusion Paraphrasers for Plug-and-Play Textual Sty | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B/S1':C |
| 2306.08456 | PoetryDiffusion: Towards Joint Semantic and Metrical Manipulation in P | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B/S1':C |
| 2306.08505 | DiffuDetox: A Mixed Diffusion Model for Text Detoxification | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B/S1':C |
| 2306.02531 | PLANNER: Generating Diversified Paragraph via Latent Language Diffusio | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':B |
| 2305.19512 | Fine-grained Text Style Transfer with Diffusion-Based Language Models | S1: none of its phrases; S2: no group-A phrase | name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion) | S1':A1/S1':B |
| 2305.20009 | Protein Design with Guided Discrete Diffusion | S1: phrase 'discrete diffusion' but no language word; S2: no group-A phrase | out of scope: protein or molecule (X1) | not captured |
| 2305.15025 | Dior-CVAE: Pre-trained Language Models and Diffusion Priors for Variat | S1: none of its phrases; S2: no group-A phrase | continuous or latent diffusion language model | S1':B/S1':C |
| 2305.13298 | DiffusionNER: Boundary Diffusion for Named Entity Recognition | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |
| 2305.01735 | DiffuSum: Generation Enhanced Extractive Summarization with Diffusion | S1: none of its phrases; S2: no group-A phrase | NLP task or text generation with a diffusion model | S1':B |

### 2.2 The revised strings (verbatim, also in protocol section 10)

S1':
```
("diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms) OR ((("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) OR (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation))) OR (("absorbing state" AND (language OR text OR token* OR "language model*")) OR ("any-order" AND (language OR text OR token* OR "language model*")) OR "non-autoregressive language model*" OR ("non-autoregressive" AND diffusion AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*))) OR (diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) OR (diffusion AND ("language model*" OR llm*) AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation))
```
S2':
```
(("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) OR (("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms))
```
Parts (S1' = A1 OR A2 OR A3 OR B OR C; S2' = M OR VLA); each source was run part by part, the union is the string:

- `S1':A1` "diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms
- `S1':A2` (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) OR (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation))
- `S1':A3` ("absorbing state" AND (language OR text OR token* OR "language model*")) OR ("any-order" AND (language OR text OR token* OR "language model*")) OR "non-autoregressive language model*" OR ("non-autoregressive" AND diffusion AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*))
- `S1':B` diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)
- `S1':C` diffusion AND ("language model*" OR llm*) AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)
- `S2':M` ("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")
- `S2':VLA` ("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms)

### 2.3 Three rounds

Round 1 is broad (phrase variants taken from the missed entries, plus 'diffusion' with text-generation words, no exclusions). Round 2 adds the biochemical and visual exclusions, NLP-task terms and the VLA branch, after the round 1 sample showed that molecules, proteins, robot policies and image generation made up most of the noise. Round 3 (final) narrows the language context of the discrete-diffusion branch (drops `sequence*`, `categorical`, `code`) and replaces `natural language` by `natural language generation`, after the round 2 sample showed those terms bringing in biological sequence papers. Recall is over the 540 seed entries; the precision sample is a random 200 of the records of the 14,794 collected earlier (`new-records-2026-10-15.jsonl`, v1) that the round adds over S1/S2.

| Round | Recall 540 | MM28 | R50 | Records added over S1/S2 | Sample seed | Looks in scope (IN) | Unclear (U) | Other (O) |
|---|---|---|---|---|---|---|---|---|
| S1/S2 | 453 | 26/28 | 40/50 | - | - | - | - | - |
| R1 | 521 | 28/28 | 48/50 | 1,016 | 20261015 | 34 | 29 | 137 |
| R2 | 528 | 28/28 | 48/50 | 660 | 20261016 | 63 | 45 | 92 |
| R3 | 525 | 28/28 | 47/50 | 539 | 20261017 | 67 | 46 | 87 |

The labels are mine, from titles only (`string-revision-labels-2026-10-15.json` holds every sampled ID and label). I proposed the strings and also labelled the sample, so this is a proxy for choosing between versions and not an independent precision estimate; the screeners decide eligibility. The sample reproduces from the stated seed (`tools/string_rounds.py` checks it: reproduced = R1 True, R2 True, R3 True).

Final round, share of the sample by the S1' / S2' part that matches (a record can match more than one part):

| Part | IN | U | O |
|---|---|---|---|
| A1 | 41 | 5 | 7 |
| A2 | 9 | 23 | 35 |
| A3 | 3 | 1 | 7 |
| B | 27 | 18 | 14 |
| C | 24 | 10 | 25 |
| S2':M | 1 | 0 | 6 |
| S2':VLA | 2 | 1 | 4 |

### 2.4 Second precision estimate, on what the revised searches actually returned

Stratified random sample of the screening queue: 40 records per tier (seed 20261018), labelled from the title as in 2.3 (`precision-actual-labels-2026-10-15.json`). Estimated number of in-scope-looking records in the queue of 6,376: 755 (11.8%); in scope or unclear: 1,172 (18.4%). Per tier:

| Tier | Records | Sampled | IN | U | O | IN share (Wilson 95%) | Estimated IN records |
|---|---|---|---|---|---|---|---|
| T1 | 1,297 | 40 | 19 | 6 | 15 | 48% (33% to 62%) | 616 |
| T2 | 220 | 40 | 1 | 4 | 35 | 2% (0% to 13%) | 6 |
| T3 | 2,221 | 40 | 2 | 3 | 35 | 5% (1% to 16%) | 111 |
| T4 | 450 | 40 | 2 | 3 | 35 | 5% (1% to 16%) | 22 |
| T5 | 2,188 | 40 | 0 | 0 | 40 | 0% (0% to 9%) | 0 |

The local pool of 2.3 overstates precision because it is made of citation neighbours of the seeds; databases return papers from every field that use the words, e.g. diffusion of innovations, diffusion-weighted imaging, discrete diffusion equations, 'dispersive liquid-liquid microextraction' (DLLME, until `dllm*` was written as the exact tokens `dllm` and `dllms`), 'discrete flow' in fluid mechanics. Tier T3 (broad branches B and C) and T5 (returned by a database, not matching any string locally) carry most of the noise.

### 2.5 What the final strings do not capture, and why that is accepted

15 of the 70 entries stay uncaptured by S1' and S2' on title and abstract (15 of the 540 in all, so no other seed entry is lost). They are:

- 2209.03003 Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Fl: image generative-model foundation (rectified flow); no text (X1).
- 2011.13456 Score-Based Generative Modeling through Stochastic Differential Equations: image generative-model foundation (score-based SDE); no text (X1).
- 2010.02502 Denoising Diffusion Implicit Models: image generative-model foundation (DDIM); no text (X1).
- 2006.11239 Denoising Diffusion Probabilistic Models: image generative-model foundation (DDPM); no text (X1).
- 1907.05600 Generative Modeling by Estimating Gradients of the Data Distribution: image generative-model foundation (score matching); no text (X1).
- 1503.03585 Deep Unsupervised Learning using Nonequilibrium Thermodynamics: image generative-model foundation (non-equilibrium thermodynamics); no text (X1).
- 2402.04997 Generative Flows on Discrete State-Spaces: Enabling Multimodal Flows with Applic: discrete flows for protein co-design; biochemical exclusion (abstract mentions protein).
- 2604.02028 Why Gaussian Diffusion Models Fail on Discrete Data and How to Prevent It?: Gaussian diffusion on discrete data (toy model); abstract mentions protein, so the biochemical exclusion drops it.
- 2402.19009 Unified Generation, Reconstruction, and Representation: Generalized Diffusion wi: generalised diffusion with latent encoder-decoder; abstract mentions protein and image, dropped by both exclusions.
- 2208.00638 Composable Text Controls in Latent Space with ODEs: latent-space text control with ODEs; the abstract has no diffusion or flow term, no string reaches it.
- 2509.06040 BranchGRPO: Stable and Efficient GRPO with Structured Branching in Diffusion Mod: reinforcement-learning for image and video diffusion; no text (X1).
- 2406.01572 Unlocking Guidance for Discrete State-Space Diffusion and Flow Models: guidance for discrete state-space models, natural-science applications; biochemical exclusion.
- 2604.24089 BiMol-Diff: A Unified Diffusion Framework for Molecular Generation and Captionin: molecular generation and captioning; biochemical exclusion (X1).
- 2506.21557 Debunk and Infer: Multimodal Fake News Detection via Diffusion-Generated Evidenc: multimodal fake-news detection with diffusion-generated images; visual exclusion.
- 2305.20009 Protein Design with Guided Discrete Diffusion: protein design with discrete diffusion; biochemical exclusion (X1).

Of the random 50, the 3 not captured are the entries listed above as outside I1 (two image-generation foundation papers and a protein-design paper); all 28 MM28 entries are captured (S1' alone: 26, S2' alone: 9; the two vision-language-action entries need the VLA branch of S2'). The foundation papers (DDPM, DDIM, score-based SDE, rectified flow, score matching, non-equilibrium thermodynamics) produce no text, fall under X1, and are in the Awesome-DLMs list as background; they stay in the corpus as seeds anyway. Two entries are arguably in scope and are lost to the exclusions (Gaussian diffusion on discrete data; generalised diffusion with latent encoder-decoder, whose abstracts mention proteins); the cost of the biochemical exclusion is that a general method paper that mentions proteins and has no language word is not retrieved. The exclusions apply only where no language word is present (A2) or to the broad branches (A3 non-autoregressive, B, C).

## 3. Searches run with S1' and S2' (D0026 item 3)

Every row is in `search-log.jsonl` (database, string, query, filters, executed_utc, hits, records, export, sha256). The original runs of the morning stay in the log. Dates are 2026-10-15 UTC. The window is 2021-01-01 to the search date.

| Source | String | Log rows | Hits reported (sum of parts, current runs) | Records retrieved | Notes |
|---|---|---|---|---|---|
| OpenAlex | S2 | 1 | 115 | 115 |  |
| OpenAlex | S1 | 2 | 566 | 566 | 1 earlier row(s) superseded by a rerun of the same part (see 3.1) |
| Semantic Scholar bulk | S1 | 1 | 1,487 | 1,487 |  |
| arXiv | S1 | 1 | 1,286 | 1,286 |  |
| arXiv | S2 | 1 | 190 | 190 |  |
| Semantic Scholar bulk | S2 | 1 | 228 | 228 |  |
| ACL Anthology | S1 | 1 | 113 | 113 |  |
| ACL Anthology | S2 | 1 | 5 | 5 |  |
| OpenReview | S1 | 40 | 1,768 | 1,768 |  |
| OpenReview | S2 | 16 | 713 | 713 |  |
| snowball | snowball-backward | 1 | 25,509 | 25,509 |  |
| snowball | snowball-forward | 1 | 26,003 | 26,003 |  |
| OpenReview | S1' | 108 | 1,944 | 1,944 |  |
| OpenAlex | S1' | 5 | 1,337 | 400 | 2 part(s) PARTIAL: OpenAlex free credits exhausted; 3 part(s) NOT RUN: OpenAlex free credits exhausted |
| arXiv | S1' | 11 | 4,318 | 4,318 | 6 earlier row(s) superseded by a rerun of the same part (see 3.1) |
| Semantic Scholar bulk | S1' | 6 | 8,462 | 8,462 | 1 earlier row(s) superseded by a rerun of the same part (see 3.1) |
| ACL Anthology | S1' | 2 | 230 | 230 | 1 earlier row(s) superseded by a rerun of the same part (see 3.1) |
| arXiv | S2' | 6 | 311 | 311 | 4 earlier row(s) superseded by a rerun of the same part (see 3.1) |
| ACL Anthology | S2' | 2 | 7 | 7 | 1 earlier row(s) superseded by a rerun of the same part (see 3.1) |
| OpenReview | S2' | 40 | 757 | 757 |  |
| OpenAlex | S2' | 2 | 0 | 0 | 2 part(s) NOT RUN: OpenAlex free credits exhausted |
| Semantic Scholar bulk | S2' | 4 | 395 | 395 | 2 earlier row(s) superseded by a rerun of the same part (see 3.1) |

Hits are summed over parts, so a record found by several parts is counted several times; unique counts are in section 4.

### 3.1 Problems met and handled

- **OpenAlex quota.** The unauthenticated allowance is 1,000 credits a day (response headers `X-RateLimit-Limit: 1000`, `Remaining: 0`, reset 39,331 s after 13:04 UTC). It was spent by the morning runs plus two parts: S1':A1 returned 200 of 412 hits and S1':A2 200 of 925; S1':A3, B, C and S2':M, VLA were not run (a log row with `NOT RUN` and the 429 headers is kept for each). **Resume** after the reset, or with an `OPENALEX_API_KEY`: `python tools/search_sources.py oa S1p S2p`. OpenAlex therefore contributes S1/S2 in full and S1' only in part.
- **arXiv wildcards.** arXiv switches stemming off for a wildcard term (`abs:image*` finds 11,800 records, `abs:image` 104,864) and `ANDNOT` with a wildcard removed almost nothing (1,147 to 1,117 against 707 with the plain term). The first arXiv run of the seven parts was therefore rerun with stem forms written out (as for OpenAlex); the first rows and raw files stay in the log and are marked superseded; the merge uses the latest row per part.
- **Exact tokens for abbreviations.** The first full run used the prefix terms `dllm*`, `dmllm*`, `dvlm*`, `vla*`, `mllm*`. A sample of what Semantic Scholar returned showed that `dllm*` matched DLLME (dispersive liquid-liquid microextraction) in analytical chemistry, hundreds of records. The five terms were written as exact tokens (`dllm`, `dllms`, ...) in the final strings, parts A1, M and VLA were rerun on arXiv and Semantic Scholar, S1' and S2' were reapplied to the ACL snapshot, and the merge uses the latest row per part; the first rows and raw files stay in the log. OpenAlex parts A1 and A2 (partial) were run before this fix and cannot be rerun until the quota resets; OpenAlex strips wildcards, so its A1 query already used the stem `dllm`.
- **Semantic Scholar throttling.** The shared unauthenticated pool returned HTTP 429 for long periods; the runner waits 90 s and retries the same page (up to 40 times) and keeps the cursor, so results are complete (hits equal retrieved in every S2 row).
- **OpenReview.** Search is a term search (listing endpoints are blocked, as in v1). The terms of S1'/S2' are phrases (see `OR_TERMS_P` in `tools/search_sources.py`); the full boolean string, including the exclusions, is applied locally to title, abstract and keywords by `tools/merge_new_records_v2.py` (`fails_local_clause` in the stats).
- **ACL Anthology.** S1' and S2' were applied to the same snapshot of the export as the morning run (sha256 in the log rows), so the two versions of the strings are compared on identical data.
- **DBLP** was not searched (D0026 item 3): proof-of-work challenge, title-only index. Its venues are covered through Semantic Scholar and OpenAlex. Reported as a limitation.
- **Subscription databases** (Scopus, Web of Science, IEEE Xplore, ACM DL, SpringerLink, ScienceDirect) cannot be run by an agent; section 'Revised strings S1' and S2'' of `subscription-search-sheet.md` has the adapted strings; the original strings stay as the second run.

## 4. Merge and deduplication (as v1, with three extra keys)

Keys, in order: arXiv ID (version stripped), DOI, source IDs, normalised title (3+ words), normalised abstract (200+ characters); union-find within and across sources. Added in v2: embedded arXiv ID in a title (reference-list fragments such as 'Large language diffusion models . 2025. arXiv: 2502.09992'), cleaned title (leading '2025.' and trailing ', 2025' removed) and a squashed title (letters and digits only, 25+ characters, which undoes hyphenation breaks). The extra keys merged 280 further pairs. `screening/records.jsonl` is unchanged (sha256 240d8e65dd7a1bf0..., equal to the v1 report).

| Source | Identified | By string | Unique within source | Duplicates within | Already in corpus | New | New and matching a string locally |
|---|---|---|---|---|---|---|---|
| openalex | 1,081 | S2 115, S1 566, S1' 400 | 713 | 368 | 391 | 322 | S1 191, S2 33, S1' 247, S2' 37 |
| semantic-scholar-bulk | 10,572 | S1 1,487, S2 228, S1' 8,462, S2' 395 | 6,768 | 3,804 | 1,399 | 5,369 | S1 261, S2 47, S1' 3,172, S2' 184 |
| arxiv-protocol-rerun | 6,105 | S1 1,286, S2 190, S1' 4,318, S2' 311 | 2,841 | 3,264 | 1,402 | 1,439 | S1 73, S2 12, S1' 1,109, S2' 102 |
| acl-anthology | 355 | S1 113, S2 5, S1' 230, S2' 7 | 234 | 121 | 96 | 138 | S1 40, S2 3, S1' 134, S2' 5 |
| openreview | 3,357 | S1 1,301, S2 155, S1' 1,728, S2' 173 | 1,205 | 2,152 | 490 | 715 | S1 489, S2 55, S1' 659, S2' 77 |
| snowball-backward | 19,423 | snowball-backward 19,423 | 6,176 | 13,247 | 530 | 5,646 | S1 88, S2 5, S1' 225, S2' 16 |
| snowball-forward | 25,998 | snowball-forward 25,998 | 9,822 | 16,176 | 1,211 | 8,611 | S1 183, S2 4, S1' 579, S2' 29 |

Union of new records across sources: **19,328**; of these 14,254 were already in the v1 file (`new-records-2026-10-15.jsonl`, 14,794) and 5,074 come from the revised-string runs. Database records 6,252; snowball-only 13,076.

Records by source combination (top 15): semantic-scholar-bulk 3,705; arxiv-protocol-rerun+semantic-scholar-bulk 837; openreview 535; arxiv-protocol-rerun+semantic-scholar-bulk+snowball-forward 199; semantic-scholar-bulk+snowball-forward 155; arxiv-protocol-rerun 130; openalex 114; snowball-backward 98; openalex+semantic-scholar-bulk 85; arxiv-protocol-rerun+openreview+semantic-scholar-bulk+snowball-forward 56; openalex+semantic-scholar-bulk+snowball-forward 41; acl-anthology+arxiv-protocol-rerun+semantic-scholar-bulk 37; arxiv-protocol-rerun+semantic-scholar-bulk+snowball-backward+snowball-forward 35; arxiv-protocol-rerun+semantic-scholar-bulk+snowball-backward 25; snowball-forward 25 (queue only).

## 5. Snowball string filter (D0026 item 4)

Snowball records come from 19,423 backward and 25,998 forward citation edges of the 539 distinct seed IDs (one level, Semantic Scholar; seeds with more than 5,000 citations skipped forward). After the date window and deduplication, 13,076 records are in no database result. A snowball-only record is screened only if its title and abstract match S1, S2, S1' or S2' (local test): S1 53, S2 1, S1' 124, S2' 1; any of the four: 124.

**12,952 snowball-only records are marked `auto_excluded` (reason 'string filter, D0026')**; for PRISMA this is 'records marked as ineligible by automation tools'. Of these, 2,107 have no abstract even after enrichment and were judged on the title alone (`auto_excluded_abstract_missing: true`); a snowball record whose title does not match and that has no abstract could be in scope, so these are a stated limitation of the filter.

## 6. Abstract enrichment (D0026 item 5)

Records without an abstract before enrichment: 2,798 of 19,328 (all new records, not only those that will be screened, so that the snowball filter is not decided by a missing abstract). Sources, in order: Semantic Scholar batch endpoint (by paperId, arXiv ID, DOI or ACL ID, 500 per request; it returned an abstract for 1 of 1,290 requested, because Semantic Scholar holds none for these records), arXiv API (`id_list`, 84 of 84), OpenAlex by DOI (50 per request; stopped at once, quota exhausted), and, in a second pass beyond the three sources named in D0026, Crossref by DOI for the 396 records that had a DOI and would be screened or could match on the title (8 abstracts). Abstracts filled by source: semantic-scholar-batch 1, arxiv-api 84, crossref-doi 8. Still missing after enrichment: 2,705 of all new records; among the records to screen: 598. Notes: OpenAlex status 429 at 0 (remaining credits 0); stopped.

Abstract source of the records to screen (field `abstract_source`): semantic-scholar-bulk 3,430, openalex 197, arxiv-protocol-rerun 1,388, acl-anthology 138, arxiv-api 11, snowball-backward 1, openreview 594, snowball-forward 10, crossref-doi 8, none 598, semantic-scholar-batch 1.

## 7. Screening queue

`screening-queue-2026-10-15.jsonl`: 6,376 records with id, title, abstract, sources, `string_match` {S1, S2, S1', S2'}, plus `queue_reason`, the matching S1'/S2' parts, DOI, arXiv ID, date and venue. Database records that match no string locally (2,188) are kept in the queue, because the database returned them (engine stemming and Boolean quirks differ from the local word test); they carry `string_match` all false and `queue_reason` 'database record', so they can be screened last or sampled. Matching locally: S1 805, S2 115, S1' 3,851, S2' 268 among 6,252 database records; 3,157 are added by the revised strings over S1/S2. 55 queue records carry `possible_duplicate_of` (title Jaccard 0.8 against an existing record; flagged, not dropped).

Screening tiers (field `queue_tier`; a guide for ordering and sampling, computed from the local test of the strings on title and abstract; not a screening decision):

| Tier | Definition | Records | Database | Snowball |
|---|---|---|---|---|
| T1 | matches S1 or S2, S1' part A1, or S2' | 1,297 | 1,209 | 88 |
| T2 | matches S1' A2 with a language word, or A3 | 220 | 219 | 1 |
| T3 | matches only S1' B or C (diffusion with text-generation, NLP-task or language-model words) | 2,221 | 2,207 | 14 |
| T4 | matches only S1' A2 without a language word | 450 | 429 | 21 |
| T5 | database record that matches no string locally | 2,188 | 2,188 | 0 |

98 queue records are reference-list fragments (snowball only, no identifier, no abstract; Semantic Scholar returns unparsed reference strings such as '2023. SSD-LM: Semi-autoregressive Simplex-based Diffusion Language Mod'): field `title_fragment`; 40 of them have a near-duplicate candidate (field `near_duplicate_candidate`: id, Jaccard, containment of the fragment) among the corpus; flagged, never merged, because a containment of 1.0 with a Jaccard of 0.5 can be a different paper.

Queue records by S1' part: A1 740, A2 1,038, B 1,577, A3 303, C 1,478; by S2' part: M 174, VLA 97.

## 8. Numbers for the PRISMA 2020 flow diagram

| Box | Count | Note |
|---|---|---|
| Identified from databases and registers, this run | 21,470 | arXiv, Semantic Scholar, OpenAlex, OpenReview, ACL Anthology; S1, S2, S1', S2' runs together, before deduplication; current runs only (superseded rows excluded); OpenAlex S1' partial |
| Identified from Awesome-DLMs list (earlier) | 572 | 540 with an arXiv ID; commit 194aa6bd |
| Identified by citation searching (edges) | 45,421 | backward + forward edges, one level |
| Duplicates removed (within source, across sources and against the corpus) | see section 4 | per-source columns |
| New records after deduplication | 19,328 | database 6,252, snowball only 13,076 |
| Marked ineligible by automation tool (string filter, D0026) | 12,952 | snowball-only records matching none of S1, S2, S1', S2' |
| Records to screen (title and abstract) | 6,376 | 6,252 database + 124 snowball matching a string |
| Of which without an abstract | 598 | screened on title alone, flagged |
| Not searched | DBLP; OpenAlex S1' parts A3, B, C and S2' parts (quota); six subscription databases (user) | limitations |

## 9. What was not searched, not done, or could not be done

- No claim of completeness: search completeness is not proof of coverage. Not searched: DBLP; OpenAlex for S1' parts A3, B, C and S2' (quota; resume command above); Google Scholar; the six subscription databases; non-arXiv venues that no free index carries; workshops outside OpenReview; anything before 2021 (I4).
- The string revision uses the 540 seeds as its vocabulary source, which are themselves a curated list built from what the list's authors knew; a paper whose abstract uses none of this vocabulary is not found by S1'/S2' either. The revision can raise recall on papers like the seeds; it cannot show that unlike papers are absent.
- Precision labels are mine and title-only.
- Snowballing was not rerun; it is one level from the seed list, not from newly found records.
- No `papers` ledger rows were added: the contract's one-row-per-item rule would add thousands of rows for records that have not been looked at; the records live in `new-records-2026-10-15-v2.jsonl` with their IDs and sources. Add rows after screening, for included records.

## 10. Decisions and checks for the orchestrator

1. **Precision of the revised strings on real databases is low.** The three rounds were judged on a pool of citation neighbours of the seeds (about a third of the added records look in scope); on what the databases returned only about one record in eight does (section 2.4). T1 (matching S1, S2, S1' A1 or S2') holds about 80 percent of the in-scope-looking records; T3 and T5 hold more than two thirds of the queue and about 2.5 percent in-scope-looking. A fourth round (for example requiring a language word in B and C, or in the no-context branch of A2, and adding 'diffusion of innovation', 'diffusion-weighted' and 'diffusion equation' exclusions) would need your decision, since D0026 allowed three. Without it, screening can start with T1 and T2 and sample T3 to T5.
2. T5 (database records that match no string locally, 2,188) could be marked as ineligible by the string filter as the snowball records are; I kept them in the queue because D0026 item 4 names snowball records only.
3. OpenAlex: resume the unrun S1' and S2' parts after the quota resets (about 11 hours after 13:04 UTC on 2026-10-15) or give an API key.
4. The snowball filter judged 2,107 snowball-only records on the title alone because no abstract could be found; say if a sample of them should be screened.

## 11. Files

- `research/review/corpus/new-records-2026-10-15-v2.jsonl`
- `research/review/corpus/screening-queue-2026-10-15.jsonl`
- `research/review/corpus/search-v2-report-2026-10-15.json`
- `research/review/corpus/search-v2-merge-stats-2026-10-15.json`
- `research/review/corpus/string-revision-2026-10-15.json`
- `research/review/corpus/string-revision-labels-2026-10-15.json`
- `research/review/corpus/abstract-enrichment-2026-10-15.json`
- `research/review/corpus/search-log.jsonl`
- `research/review/corpus/subscription-search-sheet.md`
- `research/sources/search-raw/` (raw responses, run logs)
- `tools/search_sources.py`, `tools/merge_new_records_v2.py`, `tools/string_rounds.py`, `tools/make_search_sheet_v2.py`, `tools/write_search_report_v2.py`
- `research/review/protocol.md` section 10 (amendment entry of 2026-10-15)
