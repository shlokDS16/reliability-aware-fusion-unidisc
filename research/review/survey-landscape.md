```yaml
agent: lit-scout
date: 2026-10-13
brief: Existing surveys/reviews/tutorials/position papers a referee could cite against our DLM + unified multimodal diffusion review; precedents for audits; prior statements of CA and CB
sources_examined:
  # Tier 1, HTML full text scanned (E2 for the flags/sections named): 2508.10875v3 2506.13759v5 2505.02567v6 2508.08712v4 2607.12829v1 2605.25343v1
  # 2509.24435v1 2609.04778v1 2409.14993v3 2412.11694v3 2410.22217v2 2303.06574v2 2303.07576v1 2305.14671v2 2512.05092v2 2608.20743v2
  # Sections read for item (d): 2609.01607 (Sec 6, 8) 2607.04423 (Sec 3.2, 5.2-5.3, 6) 2509.24897 (Sec 5) 2410.13848 (Table 5) 2602.00286 (Sec 3.3-3.4, 8) 2510.04767 (Sec 4 Thm 1) 2508.08712 (Sec 6.1.2) 2605.25343 (Sec 3.3.2) 2505.02567 (Sec III sentence)
  # Everything else in the ledger: abstract or metadata only (E1) or existence-checked only
  - see 96 rows in research/ledgers/papers.jsonl (clusters survey-landscape/dlm, survey-landscape/unified-mm, conjecture-CA, conjecture-CB, precedent-audit)
coverage: >
  Searched OpenAlex (works?search=..., filter from_publication_date:2023-01-01, ~15 queries), arXiv abs/HTML pages, ACL Anthology pages,
  Springer/TechRxiv/SciLTP pages via Exa fetch, and 9 Exa agent_run sweeps (low/medium) whose output was treated as E0 until each ID
  was re-opened on arXiv/ACL/DOI. NOT covered: see section 5.
claims:
  - statement: None of the 14 surveys/tutorials whose full text was scanned states a PRISMA-style protocol; 1 (2509.24435) states a "systematic review" with venue/year range and inclusion criteria but no search strings or screening counts
    status: supported
    evidence: keyword scan of arXiv HTML (PRISMA, systematic review, inclusion/exclusion criteria, search string/protocol, meta-analysis, screening) per ID; contexts printed for 2508.08712, 2509.24435, 2506.13759
    level: E2
    confidence: 0.8
  - statement: No scanned DLM or unified-multimodal survey codes reporting practice (seeds, intervals, compute matching, code release) across the surveyed papers
    status: supported
    evidence: keyword scan (seed, confidence interval, reproducib, self-reported) plus H2 headings; hits were incidental (model names, future-work sentences)
    level: E2
    confidence: 0.75
  - statement: The closest prior statement to CA is arXiv 2609.01607 (Sec 6: synergy "possible but highly conditional"; Sec 8: mutual benefit is architecture-dependent)
    status: supported
    evidence: 2609.01607 Sec 6 and Sec 8, arXiv HTML v1
    level: E2
    confidence: 0.85
  - statement: The closest prior statement to CB is arXiv 2602.00286 (order sensitivity plus parallelization bias; exact verification exponential in block total correlation) together with ParallelBench Thm 1
    status: supported
    evidence: 2602.00286 Sec 3.3-3.4, 8; 2510.04767 Sec 4 Theorem 1
    level: E2
    confidence: 0.8
competing_explanations: []
unknowns:
  - Tier-2 surveys (TechRxiv, Authorea, SSRN, Vicinagearth, PeerJ, ICICSE, JEAAI, EMNLP Findings 2025, ACL Findings 2026, KDD tutorial): protocol, reference count, cutoff not determined
  - Whether other non-English or grey-literature reviews exist
  - Task-removal ablation content of the 10 candidate method papers (not read)
next_test: {hypothesis: n/a (discovery run), intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Survey landscape for the DLM + unified multimodal diffusion review

Scope: discovery and indexing only. No novelty judgement and no advice on the conjectures. Evidence tags follow `research/CONTRACT.md`: E1 = abstract/snippet/metadata, E2 = text read (section named). "Keyword scan" means a regex search over the arXiv HTML text of the latest version, not a human read of every section.

Method notes that matter for reading the table:
- Reference count = number of `ltx_bibitem` entries in arXiv HTML (may differ slightly from the PDF). Non-arXiv items are `OpenAlex referenced_works_count` and are marked.
- Literature cutoff = latest arXiv year-month appearing in an `arXiv:YYMM.` string in the text. It is a proxy; papers cited by venue only are invisible to it.
- Query URLs used: `https://api.openalex.org/works?search=<q>&filter=from_publication_date:2023-01-01&per-page=25` (queries logged in section 5), `https://api.openalex.org/works?filter=doi:<doi>|<doi>...`, and `https://arxiv.org/abs/<id>` / `https://arxiv.org/html/<id>` for every arXiv item.

## 1. Survey table

### 1a. Tier 1: full text scanned (E2 on the flags)

| Canonical ID (latest version) | Venue / status | Scope | Refs | Cutoff | Taxonomy axes (H2/H3 headings) | Stated search protocol | Quantitative synthesis | Audits reporting |
|---|---|---|---|---|---|---|---|---|
| arXiv:2508.10875 v3, 2026-06-04 (v1 2025-08-14) | preprint; list repo VILA-Lab/Awesome-DLMs | Diffusion LMs: continuous, discrete, hybrid AR-diffusion, training, inference, multimodal, applications | 228 | 2605 | paradigm (continuous / discrete / hybrid) x pre- vs post-training x inference (parallel decoding, unmask/remask, guidance, efficiency) x multimodal x application | none found | partial: Sec VI "Performance Study" compares DLMs with AR models on PIQA, HellaSwag, HumanEval, GSM8K, GenEval, MME, MMMU, GQA using numbers "primarily taken from original publications"; figures, no pooling or intervals | none found |
| arXiv:2506.13759 v5, 2025-09-19 (v1 2025-06-16) | preprint | Discrete diffusion LLMs and discrete diffusion multimodal LLMs | 175 | 2508 | maths formulation x modelling x representative models x training x inference x quantization x privacy/safety x applications | none found | none found (catalog tables only; table captions not parsed) | none found |
| arXiv:2505.02567 v6, 2026-01-26 (v1 2025-05-05) | preprint; v6 adds papers after Aug 2025 (arXiv comment) | Unified multimodal understanding and generation | 403 | 2512 | architecture paradigm (diffusion-based / AR-based / hybrid) x datasets x benchmarks x challenges | none found | partial: Table IV "statistical summary of current evaluations and benchmarks" (descriptive counts) | none found |
| arXiv:2508.08712 v4, 2026-02-10 (v1 2025-08-12) | preprint | Parallel text generation, AR-based and non-AR (incl. DLMs) | 270 | 2601 | AR-based (draft-and-verify, decomposition-and-fill, multi-token prediction) vs non-AR (one-shot, masked generation, edit-based refinement) x speed/quality/resource | partial: "inclusion criteria" stated for the speculative-decoding subsection only (~50 papers, three categories) | partial: App A theoretical (analytic) comparison of speed/quality/resource, no numeric pooling | none found |
| arXiv:2607.12829 v1, 2026-07-14 | accepted IJCAI-ECAI 2026 survey track (arXiv comment) | Inference efficiency of masked-diffusion LLMs | 58 | 2607 | latency decomposition (Eq. 1) x algorithmic / architectural-systems / inference-time-scaling factors; practitioner decision matrix | none found | none found | none found |
| arXiv:2605.25343 v1, 2026-05-25 | preprint | Native multimodal modelling roadmap | 297 | 2605 | task formalisation (Multi-to-Text, Multi-to-Target, Multi-to-Multi) x architecture x data x training (late/mid/early fusion) x inference x evaluation | none found | none found (Table 1 model comparison, Table 3 benchmark list) | none found |
| arXiv:2609.04778 v1, 2026-09-04 | preprint | DLMs for edge and agentic AI | 162 | 2609 | resource-efficient DLM x edge deployment x serving x applications x metrics | none found | none found | none found |
| arXiv:2509.24435 v1, 2025-09-29 | preprint | Alternatives to next-token prediction (multi-token, plan-then-generate, latent, continuous, non-Transformer) | 78 | 2509 | five method families | partial: Sec 3 says "systematic review" of ACL/EMNLP/ICLR/NeurIPS/ICML/arXiv 2020-2025 with inclusion criteria; no search strings, counts or flow diagram found | none found | none found |
| arXiv:2409.14993 v3, 2025-11-25 (v1 2024-09-23) | IEEE TCSVT 2025 (arXiv journal-ref) | Multimodal LLMs + multimodal diffusion + unification | 223 | 2509 | MLLM understanding x diffusion generation x unification x datasets | none found | none found | none found |
| arXiv:2412.11694 v3, 2025-03-04 (v1 2024-12-16) | Findings of ACL 2025 (search-agent report; not seen on arXiv record) | Omni-modal MLLMs | 297 | 2501 | architecture x training x data/evaluation | none found | none found | none found |
| arXiv:2410.22217 v2, 2024-10-30 | preprint | Unifying understanding and generation, autoregression perspective | 153 | 2410 | methodology by autoregressive modelling choices | none found | none found | none found |
| arXiv:2303.06574 v2, 2023-05-13 | IJCAI 2023 Survey Track | Diffusion for non-autoregressive text generation | 53 | 2305 | process definition x key designs x PLM use | none found | none found | none found |
| arXiv:2303.07576 v1, 2023-03-14 | preprint | Diffusion models in NLP | 22 | 2303 | preliminaries x NLP applications | none found | partial: Sec IV "Visualization Analysis" = bibliometric counts of cited papers by year and venue | none found |
| arXiv:2305.14671 v2, 2023-06-14 (v1 2023-05-24) | preprint | Diffusion models in NLP | 46 | 2305 | general framework x diffusion vs other generative models x techniques | none found | none found | none found |
| arXiv:2512.05092 v2, 2026-08-18 (v1 2025-12-04) | preprint (stat.ML), tutorial-style | Self-contained introduction to diffusion in general state spaces (includes discrete) | 132 | 2512 | discrete-time to continuous-time to generator view to latent diffusion | not applicable (derivation) | not applicable | not applicable |
| arXiv:2608.20743 v2, 2026-08-29 (v1 2026-08-21) | preprint | Peripheral: multimodal speculative decoding with diffusion drafters (survey plus diagnosis) | 77 | 2608 | drafter-side parallelism levels | none found | partial: "empirical diagnosis" (not read beyond headings) | not determined |

### 1b. Tier 2: metadata or abstract only (E1). Protocol, quantitative synthesis, audit: **not determined**

| Canonical ID | Date | Venue / status | Scope (from title/abstract) | Refs (OpenAlex; 0 = unknown) |
|---|---|---|---|---|
| ACL:2026.findings-acl.1853 "Towards Unified Multimodal Large Language Models: A survey" | 2026-07 | Findings of ACL 2026 | unified MLLMs: architectures, losses, alignment, representation | unknown |
| DOI:10.36227/techrxiv.175502932.20939890/v2 "Diffusion-based Large Language Models Survey" | 2025-08-26 | TechRxiv | DLLMs: foundations, sampling, guidance, schedules, caching, applications | unknown |
| DOI:10.22541/au.176918713.36402137/v1 "Efficient Diffusion Language Models: A Comprehensive Survey" | 2026-01-23 | Authorea | efficiency | unknown |
| DOI:10.36227/techrxiv.177102145.58136415/v1 "Accelerating Inference in Diffusion Large Language Models: A Survey" | 2026-02-13 | TechRxiv | inference | unknown |
| DOI:10.2139/ssrn.7393940 "Beyond Left-to-Right: A Survey of Decoding Schedulers in DLMs" | 2026 | SSRN | decoding schedulers (generation order) | unknown |
| DOI:10.1007/s44336-026-00040-5 "An overview of discrete diffusion models in natural language processing" | 2026-09-30 | Vicinagearth | discrete diffusion for NLP | 46 |
| DOI:10.7717/peerj-cs.1905 "Diffusion models in text generation: a survey" | 2024-02-23 | PeerJ CS | text diffusion | 125 |
| DOI:10.1109/icicse66971.2025.11430022 "A Technical Overview of Continuous and Discrete Diffusion-based Language Models" | 2025-12-12 | ICICSE 2025 | overview | 24 |
| DOI:10.18653/v1/2025.findings-emnlp.716 "Mitigating Sequential Dependencies: A Survey of Algorithms and Systems for Generation-Refinement Frameworks in Autoregressive Models" | 2025 | Findings of EMNLP 2025 | generation-refinement, parallel decoding | unknown |
| DOI:10.65563/jeaai.v1i4.38 "Innovations and Frontiers of Diffusion Models in NLP: A Review" | 2025-07-31 | JEAAI | review | unknown |
| DOI:10.1109/tpami.2023.3277122 "A Survey on Non-Autoregressive Generation for NMT and Beyond" | 2023-05-18 | IEEE TPAMI | NAR generation (pre-diffusion-LLM) | 280 |
| DOI:10.1145/3770855.3816476 "A Hands-on Tutorial for Diffusion Language Models with dLLM" | 2026-08-07 | KDD 2026 tutorial | hands-on tutorial | unknown |
| DOI:10.36227/techrxiv.176289261.16802577/v1 "A Survey of Unified Multimodal Understanding and Generation: Advances and Challenges" | 2025-11-11 | TechRxiv | unified models | unknown |
| DOI:10.1007/s44336-025-00032-x "A survey: advances in multi-modal visual understanding and generation" | 2026-05-28 | Vicinagearth | multimodal understanding and generation | 99 |
| URL:exa.ai/library/publication/xv07v2wsjk3 "Understanding Meets Generation: Design Philosophies and Emerging Directions Toward Unified Models" | 2026-02-20 | preprint (DOI not captured) | unified models | unknown |
| URL:sciltp.com/journals/dmml/articles/2510001963 "A Survey of Multimodal Models on Language and Vision: A Unified Modeling Perspective" | 2025-12-03 | DMML | broader multimodal | unknown |
| DOI:10.1007/s10462-026-11525-6 "Generative AI for multimodal content: a survey with empirical and experimental evaluations" | 2026-03-19 | AI Review | title claims empirical evaluations; scope unchecked | 134 |
| DOI:10.1109/tpami.2026.3690925 "Simulating the Real World: A Unified Survey of Multimodal Generative Models" | 2026-05-05 | IEEE TPAMI | peripheral | unknown |

### 1c. Position papers, technical notes and evaluation critiques (E1, abstracts read)

| Canonical ID | Date | What it is |
|---|---|---|
| arXiv:2601.14041 | 2026-01-20 | Self-described Perspective: ten open challenges for DLMs, four-pillar roadmap including unified multimodal intelligence |
| arXiv:2604.02718 | 2026-04-03 | Technical note on DLM evaluation methodology (benchmark choice, generative perplexity vs entropy, "generative frontiers"); not a literature audit |
| arXiv:2510.18480 | 2025-10-21 | Empirical study of DLM efficiency-evaluation practice; AR higher throughput |
| arXiv:2606.29228 | 2026-06-28 | Empirical: parallel-decoding method rankings depend on prompt template; reports inconsistent results across prior studies |
| arXiv:2601.15593 | 2026-01-22 | Empirical: 8 MDLMs x 58 benchmarks; parallelism and order metrics |
| arXiv:2606.19475 | 2026-06-17 | Empirical: unified protocol across 8 DLMs |

Grey literature surfaced by Exa (snippet only, not opened further): Sander Dieleman, "Continuous diffusion language models" (sander.ai, 2026-08-24); Jake Zhao, "Some Theoretical and Practical Thoughts on Diffusion Language Models" (2026-08-08); Aman's AI Journal primer on Diffusion LLMs; Hugging Face blog "Unified Models for Image Understanding and Generation" (2025-09-15). A referee could cite these as tutorials.

## 2. Prior statements close to CA and CB

### CA: cross-task synergy in unified models is conditional; decoupled visual pathways not worse at matched scale

| Source | What was actually claimed or shown | Tag |
|---|---|---|
| arXiv:2609.01607 Sec 6 | "Existing work provides no clear consensus"; surveys prior interference-vs-transfer work and concludes synergy "is possible but highly conditional", with effects "entangled with specialized modules, auxiliary losses, task-specific formulations". Their controlled native setting studies representation, task and system level. Limitation (Sec 7): formulation is discrete AR text + continuous diffusion images; generality to other formulations "remains to be empirically validated". Concurrent work (posted 2026-09-01). | E2 (Sec 6, 7) |
| arXiv:2609.01607 Sec 8 | Mutual benefit is "architecture-dependent"; task-aware specialisation allows both capabilities without asymmetric degradation; joint training helps when tasks share knowledge; end-to-end UMM beats a matched modular pipeline when understanding, reasoning and generation interact closely. | E2 (Sec 8) |
| arXiv:2607.04423 Sec 3.2 | Controlled post-training transfer experiments. Fully shared transformer + unified vision encoder (Lumina-DiMOO) shows strongest understanding-to-generation transfer; separate visual pathways (Janus-Pro) show "weaker or absent" transfer. Cites two prior studies [92, 91] for unified encoders producing synergy. | E2 (Sec 3.2) |
| arXiv:2607.04423 Sec 5.2, 5.3 | Joint und+gen training on counting: the two objectives alternate rather than improve together (oscillation); transfer "does not necessarily translate" into joint gains. Understanding-side training preserved general benchmarks (POPE, MMBench, MMMU, MME-P in Table 7). | E2 (Sec 5.2-5.3) |
| arXiv:2509.24897 (RealUnify) Sec 5 | 1,000-instance benchmark with Understanding-Enhances-Generation and Generation-Enhances-Understanding axes; reports current unified models "far from achieving genuine synergy"; stepwise decomposition works, end-to-end does not. | E2 (Sec 5) |
| arXiv:2605.25343 Sec 3.3.2 | Roadmap names a "Comprehension-Generation Dilemma" (semantic abstraction vs pixel detail, "task interference") and lists two remedies: physical decoupling (Janus-Pro separate encoders; BAGEL MoT) and encoder-free modelling. Descriptive, no new experiments. | E2 (Sec 3.3.2) |
| arXiv:2505.02567 v6 Sec III | Restates Liquid's insight that understanding and generation "can mutually benefit when unified under a single autoregressive objective and shared visual token representation". | E2 (sentence) |
| arXiv:2412.04332 (Liquid) abstract | Claims the unified token space lets generation and comprehension "mutually enhance each other" and that the unified-training penalty shrinks with model size. Ablation content not read. | E1 |
| arXiv:2410.13848 (Janus) Table 5 | Rows A-F at 1.3B scale: shared VQ tokenizer joint (A: POPE 60.1, MMB 35.0, FID 8.72), shared semantic tokenizer joint (B: 82.4, 52.7, 7.11), decoupled SigLIP+VQ joint (D: 87.0, 69.4, FID 8.53), SigLIP understanding-only (E: 85.9, 70.6), VQ generation-only (F: FID 8.92). A task-removal ablation exists here (D vs E vs F). | E2 (Table 5) |
| arXiv:2603.03241 (UniG2U-Bench) | Over 30 models: unified models generally underperform their base VLMs; generate-then-answer typically degrades; gains only in spatial and multi-step subtasks. | E1 |
| arXiv:2511.20561 (UniSandbox) | Reports an understanding-generation gap in reasoning-generation and knowledge transfer; explicit CoT in the understanding module bridges it. | E1 |
| arXiv:2604.25072 (XTC-Bench) | Cross-task consistency "governed by how tightly learning objectives are coupled across modalities, not by architectural unification alone". | E1 |
| arXiv:2606.26984 (Unison) | Benchmark with unified and decoupled tracks "allowing ... quantitative analysis of the gains from unified modeling". Results not read. | E1 |
| arXiv:2506.03591 (UTAMoE) | Asserts intrinsic task-objective conflict between understanding and generation; proposes task-aware MoE. | E1 |
| arXiv:2504.03641, 2505.10483, 2510.13759 | MME-Unify, UniEval, Uni-MMMU: benchmarks for unified models; existence verified, abstracts not read. | E1 |

Candidate sources for a task-removal-ablation census, **content not read** (a search agent reported ablations; treat as E0): JanusFlow 2411.07975, VILA-U 2409.04429, Transfusion 2408.11039, TokenFlow 2412.03069, UniTok 2502.20321, QLIP 2502.05178, BAGEL 2505.14683, Show-o2 2506.15564, UniFork 2506.17202, Emu3 2409.18869; MMaDA 2505.15809 (abstract read only).

Retrieval note, not a novelty claim: this search returned no item that (i) regresses published understanding and generation scores on design factors across many unified models while controlling for size and data, or (ii) counts how many synergy claims rest on a task-removal ablation. Section 5 lists what was not searched.

### CB: trade-off among free generation order, few parallel steps and exact joint sampling for factorised denoisers

| Source | What was actually claimed or shown | Tag |
|---|---|---|
| arXiv:2602.00286 Sec 3.3-3.4, 8 | Two failure sources separated: order sensitivity and parallelisation bias. Under perfect modelling, order does not matter (order-invariance); factorised parallel decoding is exact only under conditional independence within the block; otherwise sampling bias persists even when all marginals are exact; reverse KL can be arbitrarily large; exact verification removes the bias at cost exponential in block total correlation; remasking cannot guarantee distributional correctness. Concludes it clarifies "the fundamental trade-off between decoding efficiency and fidelity". | E2 |
| arXiv:2510.04767 (ParallelBench) Sec 4 Thm 1 | For a factorised model decoding in T parallel sets, minimum achievable KL is lower-bounded by the sum over steps of expected total correlation of each set given its prefix. Plus a benchmark of tasks easy for humans/AR but hard under parallel decoding. | E2 |
| arXiv:2508.08712 Sec 6.1.2 | Survey statement: "almost all parallel decoding techniques trade generation quality for speed"; for masked generation fewer tokens recovered per step improves quality but lowers speed. Qualitative; also Sec 6.2.1 "Ignored Dependencies in High-Entropy Scenarios". | E2 |
| arXiv:2509.22738 | Abstract: exact joint sampling requires one unmasking per full-model forward pass; ADJUST adds a light sampler for approximate joint sampling. | E1 |
| arXiv:2504.20456 | Abstract: any-subset AR models generate in any order and in parallel; ASSD provably gives the correct joint with neural calls bounded by tokens predicted. Different model class (not a factorised denoiser). | E1 |
| arXiv:2502.09622 | Abstract: efficiency-accuracy trade-off depends on metric; near-optimal perplexity in steps independent of length, but sequence error rate needs more steps (exact scaling truncated in my capture; a search agent said linear in length, unverified). | E1 |
| arXiv:2505.21400 | Abstract: KL error decays as 1/T and scales with token mutual information; covers T < L. | E1 |
| arXiv:2602.20126 | Abstract: randomised unmasking schedule adapting to dependence; KL scales with total correlation over K. | E1 |
| arXiv:2606.22976 | Abstract: lowest-entropy parallel unmasking not uniformly better than random parallel sampling on graph random-walk sandbox; bisection samplers with logarithmic steps. | E1 |
| arXiv:2410.01949, 2603.00045, 2510.21961, 2603.20216 | Abstracts each state that per-step independent marginals miss dependencies, limiting few-step quality (copula; probabilistic circuit; conditional-independence vs confidence conflict; local AR). | E1 |
| arXiv:2512.25014 | Abstract: DLMs with polynomial CoT simulate any parallel sampler in optimal sequential steps; remasking/revision gives optimal space. | E1 |
| arXiv:2601.15165 | Abstract: arbitrary order may limit reasoning potential; forgoing it with GRPO works better on maths/code. | E1 |
| arXiv:2601.15593 | Abstract: 8 MDLMs, 58 benchmarks; MDLMs lag comparable AR models, attributed to weakened inter-token dependencies under parallel modelling. | E1 |
| arXiv:2606.29228, 2510.18480 | Abstracts: current parallel decoding methods fail to overcome the speed-quality trade-off under multi-template evaluation; AR throughput generally higher. | E1 |

Retrieval note, not a novelty claim: no item retrieved states a three-way trade-off over free order, few parallel steps and exact joint sampling together, nor re-expresses published speed/quality numbers per function evaluation per token on one frontier. 2602.00286 treats order and parallelisation as two coupled sources of error and states an efficiency-fidelity trade-off; ParallelBench gives the per-set KL bound.

## 3. Gap table: which planned differentiators already exist

Legend: Y = present as defined in PLAN.md section 3; P = partial (what is partial is given); N = none found; ? = not determined (E1 only). Based on section 1; "none found" for tier 1 is a keyword scan plus headings.

| Item | Systematic protocol | Quantitative synthesis | Reporting audit | Organising conjecture |
|---|---|---|---|---|
| 2508.10875 DLM survey | N | P (Sec VI descriptive plots of reported numbers, no pooling/CI) | N | N |
| 2506.13759 discrete diffusion survey | N | N | N | N |
| 2505.02567 unified MM survey | N | P (Table IV benchmark counts) | N | N |
| 2508.08712 parallel text generation | P (inclusion criteria for one subsection) | P (analytic comparison, App A) | N | P (Sec 6.1.2 quality/speed trade-off, stated in prose) |
| 2607.12829 masked-DLM efficiency | N | N | N | P (latency decomposition equation as organiser; no conjecture) |
| 2605.25343 native multimodal roadmap | N | N | N | P (Comprehension-Generation Dilemma as organising challenge) |
| 2609.04778 edge DLM | N | N | N | N |
| 2509.24435 alternatives to NTP | P (stated systematic review, venues, years, inclusion criteria; no strings/counts) | N | N | N |
| 2409.14993, 2412.11694, 2410.22217, 2303.06574, 2305.14671 | N | N | N | N |
| 2303.07576 | N | P (bibliometric counts only) | N | N |
| 2512.05092 | n/a | n/a | n/a | n/a |
| 2608.20743 (peripheral) | N | ? (empirical diagnosis, not read) | ? | ? |
| 18 tier-2 surveys (section 1b) | ? | ? | ? | ? |
| Non-survey: 2609.01607 | N | N (own controlled experiments) | N | P (synergy "highly conditional" framing, empirical) |
| Non-survey: 2601.15593, 2606.19475 | N | P (own runs across 8 DLMs; not synthesis of published numbers) | N | N |
| Non-survey: 2510.18480, 2606.29228, 2604.02718 | N | N | P (evaluation-practice critiques; not coded audits of N papers; 2606.29228 notes inconsistent reported results) | N |

Methodological precedents for the three non-conjecture differentiators exist in neighbouring fields (all E1, abstracts read; none concerns DLMs or unified multimodal models):

| Differentiator | Precedent (canonical ID) | What it did |
|---|---|---|
| Systematic protocol | DOI:10.1007/s44196-026-01490-x (IJCIS 2026, early access) | PRISMA 2020-guided search of five sources, 182 LLM-evaluation studies |
| Systematic protocol / audit | arXiv:2511.04703 (NeurIPS 2025 D&B) | 29 reviewers, 445 LLM benchmark papers coded for construct validity |
| Systematic protocol | DOI:10.18653/v1/2026.gem-main.50 (GEM 2026) | systematic review of 55 contamination studies |
| Reporting audit | arXiv:2304.01816 (CVPR 2023) | 37 text-to-image papers audited for human-evaluation reporting |
| Reporting audit | DOI:10.18653/v1/2024.eacl-long.5 (EACL 2024) | 255 papers using GPT-3.5/4 audited for contamination and malpractice |
| Reporting audit | DOI:10.18653/v1/2026.acl-short.22 (ACL 2026 short) | 55 LLM-pipeline papers; randomness controls missing in 75% |
| Reporting audit | arXiv:1909.06674, arXiv:2003.12206, DOI:10.1609/aaai.v32i1.11503 | reproducibility studies (255 papers re-implemented; NeurIPS 2019 programme; AAAI 2018) |
| Quantitative synthesis of variance | arXiv:2406.10229, arXiv:2606.20536 | seed and sampling variance of benchmark scores; FID over training and generation seeds |
| Compute-matched comparison | arXiv:1711.10337 | neutral large-scale GAN comparison; budget and tuning explain differences |
| Benchmark survey | arXiv:2408.08632 | review of 200 MLLM benchmarks |

## 4. Reading queue (closeness to the question)

1. 2609.01607, 2607.04423, 2509.24897 (CA; first two within or near the last 90 days)
2. 2602.00286, 2510.04767 (CB; read in full, appendices for proofs)
3. 2508.10875 v3, 2506.13759 v5, 2505.02567 v6 (the three referee-obvious surveys)
4. 2508.08712 v4, 2605.25343, 2509.24435 (partial protocol, trade-off or dilemma framing)
5. ACL:2026.findings-acl.1853 and the TechRxiv/Authorea/SSRN tier-2 surveys (open and fill section 1b)
6. 2601.15593, 2606.19475, 2510.18480, 2606.29228, 2604.02718 (evaluation-practice overlap)
7. Precedents: 2511.04703, DOI:10.1007/s44196-026-01490-x, 2304.01816, ReproEvalCard
8. The ten candidate ablation papers (section 2 CA list) for the task-removal census

Concurrent work from the last 90 days (2026-07-15 to 2026-10-13): 2609.01607 (Sep 1), 2609.04778 (Sep 4), 2608.20743 (Aug 21, v2 Aug 29), Vicinagearth overview DOI:10.1007/s44336-026-00040-5 (Sep 30), KDD 2026 tutorial DOI:10.1145/3770855.3816476 (Aug 7), IJCAI proceedings version of 2607.12829 (Sep 1; arXiv posting Jul 14 is 91 days back), 2512.05092 v2 revision (Aug 18). 2607.04423 (Jul 7) is just outside the window.

## 5. What was not searched, and tool problems

- Not searched directly: IEEE Xplore, ACM DL, Springer, OpenReview search, Google Scholar, Crossref. They were reached only through OpenAlex indexing plus a few page fetches. Two ACM DL fetches returned unrelated pages.
- arXiv API returned "Rate exceeded" and Semantic Scholar returned HTTP 429 throughout, so no keyword search over arXiv listings and no Semantic Scholar citation expansion. Substitutes: OpenAlex search, Exa search, arXiv abs/HTML pages by ID.
- No forward-citation snowballing from the seeds: OpenAlex has `referenced_works_count = 0` for arXiv records and `cited_by_count` of 0-2 for them, so `filter=cites:` would have been uninformative.
- Seeds verified: 2508.10875 (title, 3 versions, v3 2026-06-04), 2506.13759 (title confirmed, 5 versions), 2505.02567 (title confirmed, 6 versions), 2510.04767, 2602.00286 (titles confirmed). All five exist; none needed correction.
- OpenAlex queries run (each with from_publication_date 2023-01-01): survey diffusion language models; survey discrete diffusion models text generation; review masked diffusion language models; survey non-autoregressive text generation; survey text diffusion models; survey unified multimodal understanding and generation; survey any-to-any multimodal generation; diffusion large language models survey reasoning reinforcement learning; diffusion language models tutorial; diffusion language models challenges perspective; masked diffusion models for language: a review of theory and practice; survey discrete diffusion models theory sampling; autoregressive versus diffusion language models critical comparison review; unified multimodal models survey autoregressive diffusion hybrid understanding generation; survey multimodal discrete diffusion models.
- Exa agent_run IDs (outputs are E0 until re-opened): agent_run_4e5c84e0496f4ca48b3d3364cd426894, agent_run_ca52b46711304421873bc68b6b057515, agent_run_05f6a8e49d7741fea8e21ab616eb9856, agent_run_51e3c05d79a948639f9f618bcc4fd8af, agent_run_ca33ff891f4b40b1ba5dd01ab219d0f2, agent_run_23972af347124e409cb35c17ec1da089, agent_run_687e1c2745a84192aadc3a769c7187e4, agent_run_52a4739b42f74bf88f26bcf657961a9f, agent_run_cf378792e3974a839e28d800def2fe85.
- Search-agent output errors found and corrected before ledgering: wrong title for 1711.10337, 2406.10229, 2403.11821, 2501.18897; wrong venue for 2304.01816 (agent said ACL Findings 2023; arXiv says CVPR 2023); title drift for 2606.22976. Any agent-sourced number I did not re-open is labelled E0 in the ledger notes or omitted.
- Surveys of other diffusion modalities (image, video, audio, molecules), theses, books, and non-English venues were not searched.
- The 14 Tier-1 scans are keyword-plus-heading scans. A referee-grade "no stated protocol" claim for any single survey needs a human read of its introduction and appendices.

Ledger: 96 `papers` rows added (P0001 onward), status `indexed`, clusters as listed in the YAML header.
