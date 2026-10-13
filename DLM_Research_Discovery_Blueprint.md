# Research Discovery Blueprint: Diffusion Language Models and Unified Multimodal Models

**Prepared:** 10 October 2026  
**Primary orchestrator:** Claude Max / Claude Code, subject to verified tool access  
**Initial seed sources:** MMaDA (arXiv:2505.15809v2) and VILA-Lab/Awesome-DLMs  
**Status:** Architecture and first-pass research reconnaissance; not a claim that every external paper linked from Awesome-DLMs has already been read.

---

## 0. Mission and operating definition of success

The goal is to identify, test, and publish a genuinely new scientific result in diffusion language models (DLMs), especially the intersection of discrete diffusion, reasoning, multimodal understanding/generation, training objectives, and inference. The goal is **not** to produce a paper-shaped document first and then optimize its claims.

A result is considered a candidate breakthrough only if it has:

1. **A nontrivial, falsifiable claim** about how or why DLMs behave—not just a new name for a collection of tricks.
2. **A credible novelty case** against prior work and concurrent work, including papers that appeared after the initial survey was written.
3. **A discriminative experiment** that could have shown the idea was wrong.
4. **Independent empirical support** across appropriate datasets, baselines, random seeds, and preferably more than one model family or scale.
5. **A mechanism or explanatory principle** that makes predictions beyond the exact setting in which it was first observed.
6. **A reproducible evidence trail:** data provenance, configurations, model/checkpoint hashes, code commits, raw results, statistical analysis, and reference verification.
7. **An honest publication fit:** choose the venue after the strength and breadth of the result are clear. A journal impact factor is not a controllable outcome and is not evidence that an individual paper is good.

### Non-negotiable rules

- Never report a planned experiment as completed, a predicted metric as observed, or a simulated result as empirical evidence.
- Never make up citations, DOIs, sample sizes, results, repository paths, or benchmark protocols.
- Never trust an LLM's claim that it has read a paper, inspected a codebase, or verified a DOI without a traceable artifact of that action.
- Separate **source facts**, **inferences**, **hypotheses**, and **verified experimental outcomes**.
- Do not use test-set results to select hyperparameters, edit claims, or choose which hypotheses to report. Reserve a final holdout where feasible.
- Preserve negative results and failed runs. They are part of the evidence, not debris to delete.
- The human researcher remains accountable for the scientific claims, author approval, ethics, and publication integrity.
- Replace “humanize/watermark removal” with a **scholarly clarity and disclosure agent**. It may improve readable prose, preserve meaning, enforce attribution, and flag AI-use disclosure requirements; it must not remove provenance marks or attempt to evade AI-detection systems.

## 1. What the seed sources tell us

### 1.1 MMaDA paper: technical map

Source: [MMaDA: Multimodal Large Diffusion Language Models](https://arxiv.org/abs/2505.15809), uploaded version arXiv:2505.15809v2 dated 25 September 2025. The current MMaDA GitHub README describes the work as NeurIPS 2025 and points to later related work, including MMaDA-Parallel and dLLM-RL.

**Core proposal.** MMaDA uses discrete masked-token prediction for both language and image tokens in a shared transformer. Text uses the LLaDA tokenizer; image tokens use the pretrained Show-o/MAGVIT-v2 quantizer. At 512×512 image resolution, a downsampling factor of 16 yields 32×32 = 1,024 image tokens; the codebook size is 8,192.

**Three stages and claimed contributions.**

- **Unified diffusion pretraining:** a masked-token cross-entropy objective is used across text and image token sequences.
- **Mixed long chain-of-thought fine-tuning:** reasoning traces for text reasoning, multimodal reasoning, and world-knowledge-aware text-to-image generation are placed in a unified format. The paper describes using open models to produce candidate traces and verifier models to filter them.
- **UniGRPO:** a GRPO-style policy-gradient method for diffusion generation. It samples response masking ratios, evaluates masked-token log probabilities, approximates sequence-level likelihood by averaging over masked tokens, and combines clipped policy updates with a KL penalty. Rewards vary by task: answer correctness and format rewards for reasoning; CLIP and ImageReward components for generation.

**Reported training scale.** The paper describes an initial 200K-step pretraining stage followed by another 400K steps with more diverse image-text pairs, 50K steps of instruction/reasoning fine-tuning, and 50K steps of UniGRPO. Main training is reported on 64 A100 80GB GPUs, global batch size 1,280, AdamW, initial learning rate 5e-5, cosine schedule. A design-choice RL ablation uses 8 A100 GPUs. This is a major full-reproduction cost, not a workload that a single consumer GPU should be assumed to reproduce faithfully.

**Inference choices.** Text generation uses semi-autoregressive blocks (the paper describes length 1,024, block length 64, 512 steps, and unmasking two low-confidence tokens per step). Image generation uses the full sequence as one block, a cosine remasking schedule, 50 denoising steps, and classifier-free guidance scale 3.5.

**Reported quantitative claims worth preserving accurately.**

- **Multimodal understanding, Table 2 (paper p. 9):** MMaDA reports POPE 86.1, MME 1,410.7, Flickr30k 67.6, VQAv2 76.7, GQA 61.3, MMMU 30.2, MMB 68.5, SEED 64.2. It improves on several unified-model baselines but does not beat every specialized baseline on every benchmark; for example, the table gives LLaVA-v1.5 MME 1,510.7 and some specialized models higher VQAv2 values.
- **Image generation, Table 3 (paper p. 10):** MMaDA reports WISE Cultural 0.67, ImageReward 1.15, CLIP Score 32.46, and GenEval overall 0.63. These exceed the listed SDXL metrics on CLIP/ImageReward and Janus on GenEval overall in the displayed table, but any comparison must preserve each benchmark's exact protocol.
- **Text benchmarks, Table 4 (paper p. 12):** MMaDA-8B reports MMLU 68.4, ARC-C 57.4, TruthfulQA 43.1, GSM8K 73.4, MATH 36.0, GPQA 28.4. Qwen2-7B is listed at 70.3, 60.6, 54.2, 80.2, 43.5, 30.8 respectively. Thus the table does **not** support a blanket claim that MMaDA outperforms Qwen2-7B on the displayed text benchmarks. The abstract names LLaMA-3-7B, while Table 4 displays LLaMA-3-8B. This discrepancy must be traced through the paper version, benchmark protocols, and evaluation code before any comparison is repeated or cited.
- **Stage ablation, Table 5 (paper p. 15):** GSM8K progresses 17.4 → 65.2 → 73.4; MATH500 4.2 → 26.5 → 36.0; GeoQA 8.3 → 15.9 → 21.0; CLEVR 10.3 → 27.5 → 34.5; CLIP Score 23.1 → 29.4 → 32.5; ImageReward 0.69 → 0.84 → 1.15 from Stage 1 to + mixed long-CoT to + UniGRPO. These are the paper's reported results, not independently reproduced results.
- **Denoising-step study, Table 6 (paper p. 16):** image CLIP score is 32.8 at 1,024 steps, 32.0 at 50, 31.7 at 15; multimodal understanding score is 35.5 at 1,024, 36.1 at 512, 35.4 at 256; text MMLU is 66.9 at 1,024, 66.3 at 512, 65.7 at 256. The multimodal result is not strictly monotonic with step count.

### 1.2 MMaDA evidence gaps and research leads

These are audit findings and research opportunities, not accusations of invalidity:

1. **Claim-to-table inconsistency:** the text-reasoning claim versus Table 4 needs reconciliation, as noted above.
2. **Evaluation reproducibility gap:** the released MMaDA evaluation README explicitly says its language evaluation currently implements the non-thinking version and that results are not yet aligned with internal results. This is a hard requirement for our reproduction plan: do not treat a checkpoint plus a table as a reproducible result without matching protocols.
3. **Causal interpretation of “synergy”:** the paper shows joint metric improvements during training, but co-movement of metrics alone does not isolate which data mixture or objective caused cross-task transfer. We need task-drop, mixture, and matched-compute interventions if we study this claim.
4. **Statistical uncertainty:** the displayed main tables and ablation narrative do not foreground multi-seed confidence intervals or hypothesis tests. The next study should predefine primary outcomes and quantify uncertainty rather than depend on curve appearance or a single run.
5. **Baseline fairness:** some qualitative figures compare against models said not to support the task; such examples are illustrations, not sufficient comparative evidence. Quantitative comparisons need aligned access, decoding budgets, prompt sets, and tuning effort.
6. **Approximate diffusion-policy likelihood:** UniGRPO's masked-token log-probability / sequence aggregation is an approximation. Its bias, variance, validity conditions, and effects on reward optimisation can be investigated—but the area is crowded, so no novelty claim is allowed until recent policy-gradient work is audited.
7. **Reasoning format is not reasoning quality:** long CoT traces can be verbose, repetitive, or confidently wrong. Score final answer correctness, calibration, robustness, and trace usefulness separately; do not reward length by itself.
8. **Data provenance:** the paper describes generated/synthetic reasoning traces and factual text-to-image pairs. Future work must report generation provenance, filtering, contamination checks, licensing, and dependence on teacher models.

### 1.3 MMaDA paper reading map (all 37 pages)

This page map is a working index for the paper-reading agent. The agent must add exact claim IDs and evidence references as it expands each section; this summary is not a substitute for preserving the original PDF.

| PDF pages | Contents | What the reader must extract |
|---|---|---|
| 1–2 | Abstract, introduction, Table 1, contributions | Main thesis; architecture families; claims and baseline framing; identify claims requiring independent verification. |
| 3 | Figure 1 qualitative examples | Distinguish illustrative examples from benchmark evidence; note unsupported-task comparisons. |
| 4 | Figure 2 pipeline; unified diffusion objective | Tokenization; masking objective; architecture diagram; assumptions in the unified probability formulation. |
| 5 | Mixed long-CoT data and fine-tuning loss | Trace source models/datasets; verification; masking/loss details; leakage risks. |
| 6–7 | UniGRPO derivation, algorithm, reward models | Mathematical assumptions; approximate log probabilities; masking strategy; clipping/KL; reward scaling; pseudocode-to-code correspondence. |
| 8 | Inference schedules | Semi-AR text strategy; image-generation schedule; exact token length, block sizes, steps, guidance; latency/quality trade-off. |
| 9–10 | Experimental setup and multimodal/image tables | Dataset sources; baselines; test prompts; implementation and compute; exact metric values. |
| 11–13 | Qualitative comparisons and text benchmark table | Compare narrative claims to numbers; note answer correctness and CoT redundancy; avoid overclaiming. |
| 14–16 | Ablations, task-synergy plots, step-count results, inpainting | Effect sizes; whether runs are repeated; plots' uncertainty; causal versus correlational interpretation; limits of demonstrations. |
| 17–23 | Related work, conclusion, references | Map every reference to DOI/arXiv/venue/code; flag duplicated or malformed metadata; locate closest predecessors and follow-up work. |
| 24–27 | Appendix: discrete diffusion, PPO/GRPO, UniGRPO details | Re-derive equations; check symbols, conditions, normalization and the implemented loss; compare paper pseudocode to training repository. |
| 28–34 | Qualitative CoT examples | Create failure taxonomy: factuality, arithmetic, visual grounding, verbosity, robustness; do not use qualitative success as quantitative validation. |
| 35–37 | Examples without reasoning CoT | Separate basic instruction-following from reasoning capability; inspect for hallucinated scene attributes. |

### 1.4 Current state of the supplied DLM repository

**Live GitHub audit update (10 October 2026):** The connected GitHub integration confirms that [VILA-Lab/Awesome-DLMs](https://github.com/VILA-Lab/Awesome-DLMs) has only two tracked files in its current tree (`README.md` and `timeline4.png`), with HEAD commit SHA `194aa6bd664b1aa22a77ee927fa2351865415e1d` (its Git tree object is `1573537dcb9c36a08cb2736081e29a945944c498`). Its 182,774-character README yielded 614 non-badge outbound link occurrences and 594 globally unique URLs. The latest retrieved commit is 2 October 2026 and adds MDVLM-TAL to Multimodal DLMs. This is an index/timeline, not an implementation repository.

The same live audit found 628 tracked files at MMaDA HEAD commit `3cdb8709635beb29f66e4e23cd66060872ac3996` (tree object `0d3fddc1c1d23ca6b27d1ba369afca9cc2db8b74) in [Gen-Verse/MMaDA](https://github.com/Gen-Verse/MMaDA), including 554 under `evaluation/`, much of which is a vendored evaluation toolkit. The current README explicitly delegates UniGRPO to [Gen-Verse/dLLM-RL](https://github.com/Gen-Verse/dLLM-RL); inspect and pin both repositories. The current public evaluation guide has apparent stale path/script instructions: it refers to `evaluation_demo/` although the tree contains `evaluation/`, shows `pip install -e` without a target, and its Stage 2.1 command names `training/train_mmada_stage_cot_sft.py` while the tree contains `training/train_mmada_cot_sft.py`. It also explicitly says the public language evaluation is non-thinking-only and not aligned with internal results. See `Live_GitHub_Audit_2026-10-10.md` for details and source SHAs.

The link resolves to [VILA-Lab/Awesome-DLMs](https://github.com/VILA-Lab/Awesome-DLMs), the public index associated with [A Survey on Diffusion Language Models](https://arxiv.org/abs/2508.10875). The repository itself is mainly a README and timeline figure; its scientific value comes from its many linked papers, codebases, demos, benchmarks, and surveys—not a single implementation to clone.

The README taxonomy includes: Must-Read; Surveys; Diffusion Foundation; Discrete DLMs; Continuous DLMs; Multimodal DLMs; Training Strategies; Inference Optimization; Training Frameworks; Inference Frameworks; Benchmarks; Applications; Resources. It has hundreds of external links and is actively updated. The current surfaced snapshot includes, among others, DARTree (August 2026), work on reducing pretraining-generation mismatch (August 2026), representation-confidence gaps (August 2026), and multiple new RL/post-training papers. The list is a starting point, not a novelty certificate.

**Relevant follow-up links from the MMaDA project:**

- [MMaDA code and README](https://github.com/Gen-Verse/MMaDA)
- [MMaDA evaluation notes](https://github.com/Gen-Verse/MMaDA/blob/main/evaluation/eval.md)
- [dLLM-RL framework](https://github.com/Gen-Verse/dLLM-RL)
- [MMaDA-Parallel paper](https://arxiv.org/abs/2511.09611)
- [Awesome-DLMs survey](https://arxiv.org/abs/2508.10875)

**Important: the repo link audit is not yet complete paper-by-paper.** Every link needs to be enumerated, canonicalized, deduplicated, resolved, assigned a status, and triaged for reading. Do not describe the repo's hundreds of linked papers as “fully reviewed” until the link ledger records a specific review outcome for each one.

---

## 2. How the system should generate scientific ideas rather than merely generate text

The framework should not pretend an LLM has a human's lived experience or automatically possesses “50 years of research intuition.” It should reproduce useful *research behaviours* that experienced researchers demonstrate: question assumptions, search for failure cases, compare mechanisms, seek simple discriminative tests, know when results are inconclusive, and update beliefs when evidence conflicts with a preferred idea.

A useful documented example is *Attention Is All You Need*: the paper identifies a structural limitation—sequential computation in recurrent models—proposes dispensing with recurrence in favor of attention, tests translation quality and efficiency, and also checks transfer to constituency parsing. The authors' contributions show multiple people proposing, implementing, tuning, and evaluating variants; the discovery was not a single unreasoned leap. Source: [original NeurIPS paper](https://proceedings.neurips.cc/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf).

Translate this into the following scientific-discovery loop:

1. **Observe a surprising failure or trade-off.** Use literature, benchmark residuals, model outputs, training curves, and reproducibility failures to identify something the field cannot explain.
2. **Describe the current explanation and hidden assumptions.** Make each assumption explicit. Search for counterexamples, not only confirming papers.
3. **Generate competing explanations, not just competing methods.** For one anomaly, produce at least three materially different mechanisms and their predicted signatures.
4. **Derive a discriminative experiment.** Ask which smallest intervention would make the explanations predict different outcomes. Prefer tests with high expected information gain over expensive leaderboard runs.
5. **Pre-register the hypothesis and failure condition.** Record the expected direction, primary metric, negative outcome, and stop rule before looking at the holdout.
6. **Run the cheapest falsification first.** Use analytic checks, synthetic/toy problems, frozen-model measurements, and small-scale ablations before scaling.
7. **Update rather than rationalize.** If evidence contradicts the hypothesis, update the hypothesis ledger; don't write a post-hoc story that reframes every result as success.
8. **Seek invariance and generalization.** Test other task families, datasets, seeds, model families, decoding budgets, and realistic distribution shifts.
9. **Explain why it works.** Produce predictions that differ from existing approaches; use a theoretical derivation, mechanistic diagnostics, or controlled intervention where possible.
10. **Let independent reviewers try to kill the result.** Reviewers should have enough details to reproduce it and should be rewarded for discovering a flaw.

A recent discussion in *Nature Methods* highlights that hypothesis generation is difficult to explain even in conventional science and cautions against treating AI-generated idea lists as equivalent to human scientific judgment. The solution here is not to claim simulated human consciousness; it is to build a closed loop in which ideas are tested against evidence and the system learns from failures. See [“What’s your hypothesis?” (Nature Methods, 2026)](https://www.nature.com/articles/s41592-026-03104-y).

## 3. Agent architecture

Claude is the orchestration layer, but no agent can approve its own evidence. Keep agent outputs structured, versioned, and reviewable. Prefer independent first-pass work before group discussion to reduce anchoring and copied assumptions.

### Agent roster (recommended)

| ID | Agent | Responsibilities | Required output / acceptance condition |
|---|---|---|---|
| A0 | Principal investigator / orchestrator (Claude) | Maintains objective, research state, budget, decisions, dependencies, and stop/go gates. Assigns work; cannot silently change the scientific claim. | A decision log, experiment queue, budget burn, and open-risk list. No scientific claim without citations or run IDs. |
| A1 | Repository crawler and link auditor | Enumerates every README link, image, code link, issue, paper, benchmark, and resource. Normalizes arXiv/DOI/GitHub URLs and records status. | Deduplicated link inventory with canonical URL, category, publication state, access status, code, and assigned reviewer. |
| A2 | Paper forensic reader | Reads full texts, appendices, tables, figures, supplementary data, and methods. Extracts claims and exact evidence locations. | Claim-evidence matrix with page/section/equation/table references; never paraphrases an unsupported point as fact. |
| A3 | Citation-graph / related-work agent | Performs backward/forward citation search, reference snowballing, author/group mapping, and concurrent-work alerts. | Citation graph, must-read set, and closest-prior-work comparison. |
| A4 | State-of-the-art and gap auditor | Compares each candidate against the closest prior work, including papers that post-date the original survey. | “Closest 10 works” table, difference matrix, overlap risk, and a written novelty verdict with confidence. |
| A5 | Research-method / expert-practice agent | Applies documented research heuristics: assumption audit, analogy, counterexample search, competing mechanisms, and decisive-test design. | At least 3 distinct hypotheses per anomaly, explicit predictions, and the cheapest disconfirming test. Does not claim literal decades of lived experience. |
| A6 | Contrarian reviewer | Independently tries to falsify the premise, novelty, theoretical derivation, datasets, metrics, and expected impact. Begins without seeing the proposer’s preferred narrative where practical. | Red-team report, top failure modes, counterexamples, and “what result would force rejection?” statement. |
| A7 | Hypothesis and experiment-design agent | Converts candidate ideas into preregisterable hypotheses, primary endpoints, controlled interventions, negative controls, and stop rules. | Experiment card approved before running: hypotheses, controls, metrics, expected results, alternatives, and stop criteria. |
| A8 | Dataset and benchmark steward | Finds datasets; checks licensing, provenance, splits, label quality, leakage, contamination, and benchmark fit. | Dataset cards and split manifest; no dataset enters training/evaluation without license and leakage checks. |
| A9 | Data engineering / quality agent | Builds versioned ingestion, deduplication, normalization, augmentation, filtering, and data validation. | Deterministic preprocessing, unit tests, checksums, and a reproducible data pipeline. |
| A10 | Reproduction agent | Reproduces cited methods/checkpoints with original protocols before proposing modifications. | Baseline replication report with differences from paper, logs, command, environment, seed, and raw outputs. |
| A11 | Algorithm / architecture agent | Designs objective, sampler, training loss, policy objective, or model changes. Derives equations and tests limiting cases. | Specification, proof or clear assumptions, implementation plan, unit tests, and ablation map. |
| A12 | Training / model-engineering agent | Implements training, checkpointing, distributed training, recovery, mixed precision, gradient checks, and profiling. | Tested training code; reproducible configs; no untracked edits during an experiment. |
| A13 | Compute and scaling agent | Plans a staged hardware ladder and estimates memory, throughput, wall time, and cloud spend before large runs. | Cost estimate, measured pilot throughput, resource caps, and a scale-up justification. |
| A14 | Evaluation harness agent | Runs benchmark suites with matched preprocessing and decoding; creates blinded evaluation for generated outputs. | Frozen evaluation version, verified metric definitions, raw predictions, and reproducible scores. |
| A15 | Statistics agent | Plans seeds/sample sizes, uncertainty, paired tests, bootstrap confidence intervals, effect sizes, correction for multiple comparisons, and subgroup analysis. | Statistical analysis plan finalized before outcome inspection; uncertainty attached to every key claim. |
| A16 | Mechanism / causal ablation agent | Separates correlation from causation; removes objectives/data sources one at a time; tests interactions and mediators. | Factorial or sequential ablation plan and explicit interpretation limits. |
| A17 | Robustness / contamination red team | Tests prompt variations, distribution shift, adversarial examples, data leakage, benchmark contamination, reward hacking, and failure concentration. | Robustness matrix, contamination statement, failure examples, and exploit tests. |
| A18 | Citation, DOI, and reference validator | Checks title/authors/venue/year/DOI against Crossref or publisher records; checks retractions/corrections and in-text relevance. | Verified reference database; every citation has status; no guessed DOI and no decorative citations. |
| A19 | Journal / venue intelligence agent | Checks official scope, article type, length, format, ethics policy, data/code availability, reviewer checklist, and recent sample papers. | Venue-fit matrix with official links, current requirements, and reasons the contribution fits or does not fit. |
| A20 | Scientific writer / structure agent | Writes only from the evidence ledger; separates methods/results/discussion and preserves all numbers and caveats. | Claim-linked manuscript; every result traces to a raw run and every factual background statement to a source. |
| A21 | Clarity and research-integrity editor | Improves clarity and human readability while preserving technical meaning, attribution, limitations, and AI-use disclosure requirements. | Diff-based edits; no claims invented, no citation removed without review, no watermark/detection evasion. |
| A22 | Independent LLM audit panel | Uses a different model or provider (e.g., Gemini plus another model) to challenge interpretation, implementation and paper claims. | Each objection labeled as correct / partly correct / unsupported, with external evidence or a reproducible test. Consensus alone is not proof. |
| A23 | Artifact/release auditor | Checks code, configs, data declarations, licenses, seeds, checkpoints, environment, scripts, and replication instructions. | Clean-room reproduction checklist and release package manifest. |

### Interaction rules

- **Proposer ≠ validator.** The model that suggests a method does not deliver the only review of that method.
- **Evidence first.** Each agent must return source links or experiment IDs, not unsupported prose.
- **No circular citation.** A paper citing another paper is not independent confirmation of the latter's result.
- **No majority voting for truth.** Two or more LLMs can share the same hallucination. Resolve disagreements with primary sources, source code, or experiments.
- **Escalation:** any unresolved critical issue in novelty, correctness, contamination, statistics, or reproducibility blocks scaling or submission.
- **Human checkpoint:** user/researcher signs off at idea selection, high-cost compute commitment, and final manuscript claims.

## 4. Research memory and audit data model

Use a durable project store (Git + Markdown/JSON/SQLite or PostgreSQL). A chat transcript alone is not a research memory system.

### Required ledgers

1. **Paper ledger:** `paper_id`, title, DOI, arXiv ID/version, venue/status, year, canonical URL, authors, related code, model/checkpoint, datasets, hardware, methods, main claims, limitations, reviewer, review status.
2. **Claim-evidence ledger:** `claim_id`, exact claim, source identifier, page/section/equation/table or code path, direct evidence excerpt (short), evidence type, status (`supported`, `contradicted`, `mixed`, `unknown`), confidence, reviewers, follow-up action.
3. **Hypothesis ledger:** ID, observation, assumptions, competing mechanisms, predicted signatures, falsification condition, novelty audit, feasibility, current belief, evidence that changed belief.
4. **Experiment ledger:** immutable experiment ID, parent hypothesis, Git SHA, config hash, dataset hash/version, model revision, seed, machine/GPU, software stack, start/end, wall time, cloud cost, metrics, logs, artifact locations, deviations, status.
5. **Failure ledger:** failure symptom, suspected cause, diagnostic test, outcome, what changed, what did not change, and reusable lesson.
6. **Decision ledger:** decision, options, evidence available at decision time, risk, owner, deadline, and conditions for reversal.
7. **Reference audit ledger:** DOI / arXiv / publisher identifiers, title and author match, publication status, corrections/retractions, cited section and claim supported.

### Evidence levels

- **E0: model-generated suggestion** — no evidence; brainstorming only.
- **E1: secondary source or README claim** — useful discovery clue, not final support.
- **E2: primary paper/publisher/preprint source inspected** — supports a description of what the paper reports, not that the result is correct.
- **E3: code/protocol inspected** — can support implementation details after path/version is verified.
- **E4: independent reproduction** — run matches a predefined tolerance and protocol; discrepancy report retained.
- **E5: repeated, statistically supported result** — primary endpoint predefined, uncertainty estimated, controls and independent tests passed.

The manuscript cannot state that a method “establishes” a new empirical effect based solely on E0–E2. Claims about the reported paper can be supported by E2; claims about our implementation require E3/E4; strong general claims should aim for E5.

## 5. End-to-end workflow and decision gates

### Phase 0 — Project setup and source integrity (Day 1–2)

**Actions:** create Git repository, project charter, source database, Zotero library, ledgers, secrets policy, and artifact store. Add the uploaded MMaDA PDF with checksum. Pin the exact Awesome-DLMs commit/date and save a raw README snapshot plus timeline image. Use a GitHub connection in Claude only after access is authorized and confirmed.

**Gate 0:** all source copies have provenance and stable identifiers; no model or agent is allowed to overwrite the source PDF or silently rewrite research memory.

### Phase 1 — Complete source and repository audit (Days 2–5)

**Actions:** enumerate every outbound URL in Awesome-DLMs; normalize and deduplicate; mark category, publication date, peer-review status, DOI/arXiv, code/checkpoint, license, and access. Fetch paper abstracts first, then prioritize full text and appendices. Inspect all MMaDA paper sections, figure/table images, appendix derivations, released code and evaluation notes. Compare version v2 to the current project README / venue version. Search forward citation and follow-up work.

**Deliverables:** repository link inventory, reading queue, MMaDA claim-evidence matrix, and exact reproduction blockers.

**Gate 1:** no statement of novelty until the top 30–50 closest works for each candidate have been screened and the closest 10 have full-text comparison. For a claim near active work, expand the search window to the latest papers and conference proceedings available on the review date.

### Phase 2 — Map the research frontier (Days 4–8)

Organize literature by **underlying scientific question**, not only keyword or model name:

- discrete diffusion fundamentals, transition kernels and objective validity;
- pretraining/inference mismatch and context conditioning;
- sequence likelihood and policy-gradient estimation for diffusion;
- reasoning, verifiers, reward design, and post-training stability;
- multimodal fusion and understanding–generation transfer;
- uncertainty, calibration, commitment/remasking, and adaptive compute;
- inference speed, memory, KV caching, speculative decoding, and quality drift;
- robustness, data contamination, safety, watermarking/provenance, and evaluation reliability;
- scaling laws, data mixture, compute-quality trade-offs, and reproducibility.

For each cluster extract: dominant assumptions, best-supported findings, unresolved disagreements, metrics used, failure modes, baseline weaknesses, recent parallel work, and where current methods merely trade one metric for another.

**Gate 2:** at least two independent literature agents agree on the closest prior work map, and a contrarian agent has tried to find a paper that invalidates each proposed gap. Agreement is provisional, never proof.

### Phase 3 — Divergent ideation, then convergence (Days 7–10)

Do not ask one LLM for “the revolutionary idea.” Use independent passes:

1. **Anomaly mining:** inspect reproducibility gaps, scaling curves, inconsistent tables, ablation interactions, error classes, low-confidence/high-accuracy cases, and high-compute/low-quality zones.
2. **Assumption inversion:** for each method, list hidden assumptions and consider what would happen if one failed (e.g., confidence predicts correctness; task metrics track true transfer; masked-token log-probability approximates the desired sequence objective; benchmark improvements imply generalization).
3. **Mechanism generation:** ask separate agents for theory-driven, data-driven, systems-driven, and evaluation-driven explanations.
4. **Prediction table:** each hypothesis must make predictions that differ from at least two alternatives. If predictions are indistinguishable, it is not yet experimentally useful.
5. **Prior-art attack:** the novelty agent searches exact claims and methodological cousins, including concurrent preprints and code commits.
6. **Small decisive test:** select the experiment most likely to falsify the top candidates at low cost.

### Candidate-scoring rubric

Score 0–5 per category, with an evidence note for every score. Suggested weights:

| Dimension | Weight | What a 5 means |
|---|---:|---|
| Scientific significance | 20% | Resolves a major bottleneck or changes how the field understands a core behavior. |
| Novelty against prior art | 20% | Clear substantive distinction from the closest prior work, supported by claim-level comparison. |
| Mechanistic depth | 15% | Predicts *why* the effect occurs and identifies conditions where it should fail. |
| Falsifiability / discriminative power | 10% | A feasible early experiment cleanly separates the hypothesis from alternatives. |
| Generality | 10% | Plausibly transfers across multiple datasets, tasks, or model families. |
| Experimental feasibility | 10% | A low-cost pilot is available and large runs are gated on success. |
| Reproducibility / external validity | 10% | Data and baselines are accessible; result can be reproduced independently. |
| Value per unit compute | 5% | Important result can be reached without an unbounded training race. |

A high weighted score is a prioritization aid, not proof. Any fatal novelty conflict, data leakage, invalid objective, or irreproducible baseline is a hard stop regardless of score.

### Phase 4 — Define hypotheses before implementation (Days 9–12)

For the selected idea, write a short internal “scientific claim contract”:

- Primary claim (one sentence)
- Mechanism or mathematical proposition
- Closest existing methods and exact distinction
- Primary metric / endpoint and clinically or practically meaningful effect size (chosen after pilot variance / power analysis)
- Secondary metrics and expected regressions
- At least two competing explanations
- Positive, negative, and inconclusive outcomes
- Minimal experiment, controls, negative controls, and ablations
- Predefined stop/go threshold
- Compute ceiling for the pilot

**Gate 3:** the independent reviewer and stats agent sign off before hyperparameter search begins.

### Phase 5 — Reproduce the baseline first (Week 2)

**Sequence:** reproduce inference before training; match exact prompt/data splits; verify metric code; reproduce a published table row or record a quantified discrepancy. For training, first run a small sanity subset and confirm loss curves, masking/label semantics, gradients, checkpoint restore, and evaluation consistency. Only then proceed to the full baseline.

**Gate 4:** a baseline is considered reproduced only when the output is within a pre-agreed tolerance and all deviations are documented. If it is not reproduced, the result is a reproduction finding, not evidence for a new method.

### Phase 6 — Prototype and falsification (Weeks 2–3)

Start small. Use synthetic or controlled tasks to isolate the claimed mechanism; then frozen-checkpoint measurements; then adapter/fine-tuning experiments; then larger runs. Implement ablations before large training so the causal interpretation is testable.

Run one change at a time initially, then factorial tests for interactions. Save intermediate predictions, not only aggregate scores. Stop early if the mechanism fails its decisive test; revise the hypothesis only as a new version with a change log.

**Gate 5:** scale only if the key effect is present in the pilot, exceeds noise and practical significance thresholds, and the best alternative explanation has been weakened by a discriminating experiment.

### Phase 7 — Scale, generalize, and compare fairly (Weeks 3–8+)

- Validate at increasing scales and document scaling effects.
- Compare against current strongest open baselines, including recent DLM work, not only original MMaDA-era baselines.
- Use matched parameter/data budgets where appropriate; also report real-world throughput/latency and hardware costs.
- Separate quality at fixed compute from quality at fixed wall time and quality at fixed latency.
- Use multiple seeds for stochastic training where resources permit, paired bootstrap over examples, confidence intervals, effect sizes, and corrected multiple comparisons for multiple primary claims.
- Test out-of-distribution prompts, longer contexts, prompt formatting variations, robust and adversarial examples, and data contamination.
- For image generation, do not rely on CLIP or ImageReward alone: combine benchmark-specific alignment, compositional evaluation, blinded human preference when justified, and factual/attribute consistency checks.
- For reasoning, score final-answer correctness separately from trace length and verifier score. Add calibration and error analysis.

**Gate 6:** a main claim needs uncertainty estimates, key ablations, strong baselines, no unexplained protocol asymmetry, and replication on held-out data or a second model/task family where relevant.

### Phase 8 — Independent audit and paper readiness (Weeks 7–10+)

Run separate audits for: (a) scientific validity, (b) novelty, (c) statistical validity, (d) implementation/data, (e) references, (f) publication fit, and (g) ethics/disclosures. Give Gemini and another model the paper, data tables, and method specification independently; ask for concrete objections, then check each with primary sources or code. Do not let another model merely “rewrite” Claude's text.

**Gate 7:** every material claim is supported by a paper/figure/table/code/run ID; all contradictory evidence is discussed; every cited reference is verified; key results can be regenerated from a clean environment.

### Phase 9 — Publication strategy (after results are stable)

Choose the venue based on what the work proves:

- **Top ML conference** for a focused algorithm, model, benchmark, or systems contribution (e.g., NeurIPS, ICML, ICLR, CVPR, ACL depending on fit and current rules).
- **Specialist AI journal** when the contribution has depth, full analysis, and a fit to the journal's readers.
- **General-science/high-impact journal** only when the result changes understanding beyond a narrow benchmark/task and can be explained to broader scientific readers, with evidence strong enough for that bar.

Nature's current peer-review criteria include technical soundness, strong evidence, novelty, importance to the field, and interest to a general scientific audience. NeurIPS provides a submission checklist emphasizing reproducibility, training details, statistical significance, and compute transparency. Read official rules for the intended cycle; do not rely on a prior-year template or copied formatting.

The paper-writing agent must read the live author guide and several recent comparable papers only after the result is defined. Learn structure and clarity, not distinctive phrasing. Do not contort the findings to imitate a journal's style.

### Phase 10 — Release and replication

Publish a versioned code release, exact model/checkpoint identifiers, data statements, training/evaluation scripts, environment lock, seed list, run manifest, raw or appropriately shareable predictions, and limitations. Use an archival DOI/repository release where appropriate. Keep artifacts immutable and assign provenance IDs.

---

## 6. Research tools and suggested integrations

Use tools to fill specific evidence gaps; do not buy subscriptions merely to accumulate tabs. Confirm each tool's actual access, API limits, and terms in the chosen Claude environment before depending on it.

| Job | Tool(s) | Best use | What it cannot prove by itself |
|---|---|---|---|
| Broad literature discovery | Exa search/fetch; web search | Discover papers, author pages, implementation pages, recent work, and primary-source text. | A retrieved snippet does not replace the paper, nor does search completeness prove novelty. |
| Research graph / forward-backward citation discovery | ResearchRabbit, Litmaps | Expand from seed papers, find clusters, discover follow-up work, monitor new papers. Litmaps advertises citation/reference-based discovery and Zotero sync. | Graph centrality is not scientific truth or a novelty decision. |
| Bibliographic metadata and DOI checking | Crossref REST API, OpenAlex, Semantic Scholar, publisher pages | Cross-check title/authors/year/DOI, venue and citation graph; Crossref has a public metadata API and OpenAlex a works/authors/sources graph API. | Not every preprint has a DOI; metadata can be incomplete. A DOI resolving does not prove the cited claim. |
| Paper library | Zotero + Better BibTeX | One source of truth for PDFs, tags, notes, keys, citation export, versioning and duplicate detection. | Citation managers do not validate that a reference supports the sentence. |
| Primary paper / peer review | arXiv, OpenReview, conference proceedings, publisher pages, ACL Anthology | Latest preprints plus final conference/journal versions and reviews where available. | A preprint is not the same as an accepted, peer-reviewed paper. |
| Code, issues, commit history | GitHub (connect to Claude where authorized), project Git, CI | Inspect training/eval scripts, releases, issues, open bugs, code changes, and exact source revision. | README commands are not proof that scripts run or outputs match the paper. |
| Models and datasets | Hugging Face Hub, dataset cards, original dataset sites | Inspect checkpoint files, model cards, licenses, dataset revisions, and inference demos. | Download availability does not imply license permission or training-data transparency. |
| Experiment tracking | Weights & Biases or MLflow | Run configs, metrics, system telemetry, artifacts, sweep history, comparisons. | A dashboard is not a reproducibility plan unless configs, code SHA, seeds, and data versions are captured. |
| Data/model versioning | DVC or immutable object storage, Git LFS where appropriate | Dataset manifests, hashes, checkpoints, generated predictions. | Version control cannot solve data licensing or contamination by itself. |
| Training and CI | PyTorch, Accelerate/DeepSpeed as appropriate, pytest, ruff, Docker/containers, pinned environment | Repeatable training/evaluation, unit tests, environment control, automated smoke tests. | A container alone does not guarantee determinism across GPU/kernel stacks. |
| Job orchestration | Simple Python workflow first; SLURM/Ray/Submitit for jobs; n8n for alerts and cross-service glue | Schedule jobs, retry failed workflow steps, notify on new papers/results, sync run summaries. | Do not route inner-loop gradient updates or GPU scheduling through an improvised n8n graph. |
| Statistics | SciPy/statsmodels or reviewed analysis scripts; bootstrap and paired tests | Confidence intervals, effect sizes, paired tests, uncertainty and multiple-comparison control. | A p-value does not establish novelty or practical significance. |
| Writing / formatting | Overleaf/LaTeX; Paperpal as a language assistant; official author guidelines | Clarity, bibliography, templates, grammar, journal-specific requirements. | These tools cannot validate scientific truth. Paperpal should never be the source of results or citations. |
| Independent critique | Gemini and another independent model + domain expert when available | Find overlooked baselines, logical gaps, ambiguous claims, and alternative explanations. | Majority vote among LLMs is not evidence. |

### Recommended minimum stack

**Claude Code + versioned Skills/MCP configuration + GitHub + Exa + Zotero + Crossref/OpenAlex + Litmaps or ResearchRabbit + Hugging Face + W&B/MLflow + pinned Python environment + a statistical analysis script.** Add Paperpal/Overleaf when writing begins. Keep n8n for event-driven notifications and report delivery, not research truth or experiment state.

### GitHub access note

A GitHub connector was surfaced as an available integration in this environment, but it is not assumed to be connected. Connect it only after you authorize it. Claude must explicitly verify it can read the target repository and record the commit SHA before the link auditor claims complete repository inspection.

---

## 7. Compute and model strategy

The research plan must treat compute as a measured resource even if money is available. More GPU hours do not rescue a weak hypothesis.

### Scale ladder

1. **Level A — theory and toy tasks:** derive the objective, run invariance/edge-case checks, build small synthetic diffusion examples, and validate the expected signature.
2. **Level B — frozen-checkpoint diagnostics:** run forward passes on accessible open DLM checkpoints, collect trajectories/logits/hidden states, and test whether the purported signal exists before training.
3. **Level C — small adapter/fine-tuning study:** use small open checkpoints or LoRA/adapters for screening; 3 seeds when stochasticity matters; run decisive ablations.
4. **Level D — 1B–3B validation scale:** cloud multi-GPU or a suitably provisioned instance only after the small-scale signal survives.
5. **Level E — 7B/8B and multi-family validation:** reserve for the strongest candidate; reproduce competitive baselines and measure actual throughput/memory.
6. **Level F — training from scratch or larger-scale scaling:** only if the discovery claim specifically depends on pretraining-scale behavior. Plan distributed training, storage, checkpointing, data pipelines, and budget before starting.

Your RTX 5070 Ti can be useful for prototyping, profiling, quantized inference, small models and some parameter-efficient tuning, depending on the specific card's available VRAM and software compatibility. It should not be treated as equivalent to reproducing MMaDA's reported 64×A100-80GB training setup. Use cloud multi-GPU compute after pilot evidence warrants it; record instance type, GPU hours, throughput, cost, CUDA/driver, interconnect, and storage bottlenecks.

### Compute gate before expensive runs

Require: (i) a passing small-scale decisive test; (ii) baseline reproduced; (iii) a fixed config and data version; (iv) measured throughput and memory from a pilot; (v) expected effect and stopping thresholds; (vi) maximum budget and checkpoint/recovery plan; (vii) an explanation of why the larger run can answer a question the pilot could not.

### Fair comparison matrix

Report at minimum:

- Model and parameter count; training data scale and source; fine-tuning data; compute and training steps.
- Accuracy/quality at a matched inference budget.
- Latency/throughput, memory, tokens per second, denoising steps, and hardware.
- Quality at matched wall time or cost where that is the actual claim.
- Robustness/calibration and subgroup metrics when relevant.
- Confidence intervals/seed variation for the primary comparison.
- Results by task, not only a single composite score.

A method may have the best score but lose on speed, robustness, memory or total cost. State which Pareto frontier it improves.

---

## 8. Dataset and evaluation policy

Do not choose a dataset because it produces the largest result. Choose it because it distinguishes competing hypotheses and has credible evaluation properties.

### Candidate evaluation families (choose based on the hypothesis)

- **Text reasoning:** GSM8K, MATH-500, GPQA and carefully chosen reasoning suites; also language understanding/factuality where the proposed mechanism should generalize. Verify exact versions and possible contamination.
- **Multimodal understanding/reasoning:** MMMU, MathVista/MathVerse, GQA, VQAv2, POPE, CLEVR and/or GeoQA depending on the claimed capability. Separate image-grounded performance from text priors.
- **Image generation:** GenEval for compositional alignment, WISE for world-knowledge prompts, CLIP Score and ImageReward as secondary metrics, and blinded human pairwise preference if the claim requires perceptual quality. Verify current benchmark versions, licenses, prompt sets, evaluator models and leakage risk.
- **Controlled synthetic tests:** build tasks where the ground-truth relation is known and only one variable changes. These are valuable for mechanism validation, not substitutes for real-world evaluation.
- **Robustness / calibration:** perturb instructions, corrupt inputs, shift task distribution, vary context length, separate confidence from correctness, and evaluate failure concentration.

### Dataset admission checklist

For each dataset: source and date retrieved; license/terms; task definition; train/dev/test split; duplicate detection; contamination check; label-generation process; known limitations; language/domain coverage; evaluation script version; and whether any examples are used for training, tuning, or only final testing.

### Statistical protocol

- Define one primary endpoint per main claim and justify its practical significance.
- Estimate variance in the pilot; use it to select a sample size / seed plan. Do not choose a sample size after seeing the final outcome.
- Use at least three independent training seeds for important stochastic training comparisons when feasible; increase where pilot variance indicates it is needed. For fixed pretrained inference, use paired bootstrap across examples and vary decoding seeds where sampling is stochastic.
- Report mean, standard deviation or confidence intervals, exact n, paired effect size, and test method. Respect dependence between items and model outputs.
- Use paired comparisons on the same examples/prompts. Correct for multiple comparisons when many endpoints are tested.
- Never report only the best seed or best checkpoint without stating the selection protocol.
- Keep benchmark test labels hidden from the algorithm/hyperparameter agent. Use separate development and final held-out sets.
- Store raw example-level predictions and grader outputs; aggregate scores must be reproducible from them.

---

## 9. Manuscript construction and publication integrity

Paper writing begins after the claim is stable. The manuscript should be claim-led, not prestige-led.

### Recommended order of construction

1. One-sentence contribution and strongest qualifying evidence.
2. Figure/table plan with a claim assigned to every panel and explicit evidence source.
3. Related-work matrix demonstrating the exact distinction from the closest methods.
4. Methods and experiment preregistration record.
5. Results produced from a frozen evaluation pipeline.
6. Limitations, failure cases, assumptions, data provenance, compute and reproducibility.
7. Introduction / abstract written last, after the findings are fixed.
8. Venue-format pass based on the current official guide and recent appropriate examples.

### Reference validation pipeline

For every citation: extract the DOI/arXiv ID; query Crossref/OpenAlex/publisher; check exact title, author list, year, venue and version; confirm whether accepted/published or only a preprint; inspect correction/retraction status; read the source; confirm that it supports the sentence cited; then run a final citation-key and bibliography integrity test. Missing DOI is not an automatic error for arXiv-only work; fabricated or misattributed DOI is.

### High-impact venue logic

General-science journals look for more than benchmark superiority: the finding must alter an important understanding and matter beyond a small subcommunity. A strong target package therefore needs a generalizable principle, clear evidence, credible mechanism, transparent limitations, and reproducibility. If the contribution is a rigorous but narrow optimization, a top ML conference or a specialist AI journal may be the better and more honest fit. The agent should maintain three ranked venue paths, each based on official current scope and rules, rather than promise a “40+ impact factor” outcome.

### AI writing and attribution

LLMs can help with discovery, analysis, code, and prose, but authors remain responsible for correctness and disclosure. Never use generated prose to fabricate experiments or citations. Keep an edit diff and claim trace for substantive edits. Follow the selected publisher's current policy for AI-assisted research and manuscript preparation. The clarity agent must not impersonate an author, fabricate human contributions, or evade provenance detection.

---

## 10. First-pass research triage: what not to assume is novel

The current DLM literature is moving quickly. The repo and searches surfaced nearby 2026 work on:

- pretraining–generation mismatch, e.g. [Reducing Pretraining-Generation Mismatch in Diffusion Language Models](https://arxiv.org/abs/2608.09424);
- representation–confidence gaps, e.g. [Unsure but Certain](https://arxiv.org/abs/2608.08791);
- RL with external rollouts, e.g. [ERILS](https://arxiv.org/abs/2608.01717);
- mask-aware policy gradients, listed by Awesome-DLMs under training strategies;
- speculative diffusion decoding, e.g. [DARTree](https://arxiv.org/abs/2608.13524);
- cross-task transfer in unified multimodal models, e.g. the [ECCV 2026 Transferability Between Understanding and Generation paper](https://cvlab-kaist.github.io/UMM_Transferability/).

These examples are included to show how fast candidate topics become crowded. They are **not** endorsed as exhaustive reviews of those works and do not prove that a gap is closed. Before selecting a thesis, each must be read at full text/code level where possible, alongside its nearest competitors and later citations. In particular, do not declare “new RL for diffusion,” “adaptive remasking,” “calibrated confidence,” “faster decoding,” or “cross-modal synergy” novel just because the initial MMaDA paper leaves them open.

### Discovery territories to test—not final paper topics

1. **Objective/protocol validity:** which training-time signal truly predicts inference-time performance, and under what conditions does the estimator become biased?
2. **Mechanism of cross-task benefit or interference:** when does joint multimodal training improve a capability without direct supervision, and when does it merely cause metric co-movement or trade-offs?
3. **Calibrated decision-making during denoising:** does confidence/uncertainty track token correctness, and can interventions improve the right error cases without hurting quality or speed?
4. **Quality–compute frontiers:** can a principled controller allocate denoising, verification, or remasking budget based on a measurable state rather than a heuristic schedule?
5. **Scientific evaluation itself:** which claims survive protocol-matched reproduction across model families, hidden tests, and corrected uncertainty estimates?

These are broad search territories. The agent must use the prior-art gate and small decisive test to select a specific contribution or discard the territory. Do not pre-commit to any of these as the final paper idea.

---

## 11. First 14 days: concrete execution plan

| Day | Action | Output | Gate |
|---|---|---|---|
| 1 | Create repo, ledgers, Zotero collection, checksums, immutable source folder; verify current tool access | Project skeleton and source manifest | No source can be silently overwritten |
| 2 | Extract all MMaDA sections/tables/figures and record claim IDs; inspect current README/evaluation notes | MMaDA evidence map | Claim/table mismatch explicitly tracked |
| 3–4 | Crawl every Awesome-DLMs outgoing URL; canonicalize, deduplicate, tag, assign owners | Complete link inventory | Every outbound link has a status, even if unread |
| 4–6 | Screen must-read/survey/foundation/multimodal/training/inference papers; discover forward citations | Cluster taxonomy + reading priority | No novelty verdict from abstract-only review |
| 6–7 | Full-read the closest works; inspect code/issue history for contenders | Closest-prior-work matrices | Contrarian review completed |
| 8 | Agents independently mine anomalies and propose competing mechanisms | Hypothesis set with predictions | At least 3 materially distinct candidates |
| 9 | Score ideas and conduct targeted novelty audit | Ranked shortlist and overlap risk | Human/researcher approves top 1–2 |
| 10 | Create a preregistered experiment card and stats plan | Claims, metrics, controls, stop rule | No coding beyond scaffolding before approval |
| 11–12 | Verify baseline install, run smoke tests and frozen-checkpoint diagnostics | Reproduction plan + first traces | Evaluation implementation verified |
| 13 | Run the smallest discriminative experiment | Raw outputs + stats | Continue only if signal survives noise and controls |
| 14 | Independent-model / human critique, update decision log | Go/no-go memo for scale | No cloud-scale run without explicit evidence-based justification |

The 14-day plan is a sprint to choose and test the direction. It is not a promise that a breakthrough or paper will be complete in two weeks.

---

## 12. Ready-to-use agent prompt contracts

Use the following fields as required output from any agent. Keep the domain-specific task in its system prompt, but enforce a common schema:

```yaml
agent_id: Axx
mission: one bounded task
sources_examined:
  - canonical_url_or_artifact_id
coverage: exact pages/sections/links/code paths reviewed
claims:
  - claim_id: Cxx
    statement: concise and testable
    status: supported | contradicted | mixed | unknown
    evidence: source location or experiment_id
    confidence: 0.0-1.0
    caveats: []
competing_explanations: []
unknowns: []
recommended_next_test:
  hypothesis: ...
  intervention: ...
  primary_metric: ...
  falsifying_outcome: ...
  estimated_compute: ...
  prerequisites: []
stop_conditions: []
review_needed_from: []
```

A novelty agent must also include exact-match search strings, synonyms, closest prior works, and the difference claimed. A training agent must include configuration hash, data/model revision, seed, hardware, environment lock, and artifact IDs. A paper agent must include page/table/equation references. A statistics agent must include exact n, estimand, test, uncertainty method and multiplicity handling.

---

## 13. External references for the workflow

- MMaDA paper: https://arxiv.org/abs/2505.15809
- MMaDA repository and model/training instructions: https://github.com/Gen-Verse/MMaDA
- MMaDA evaluation limitations: https://github.com/Gen-Verse/MMaDA/blob/main/evaluation/eval.md
- Awesome-DLMs repository: https://github.com/VILA-Lab/Awesome-DLMs
- DLM survey: https://arxiv.org/abs/2508.10875
- Transformer original paper: https://proceedings.neurips.cc/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf
- Nature peer-review criteria: https://www.nature.com/nature/for-referees/policies-and-processes
- Nature author/formatting guide: https://www.nature.com/nature/for-authors/formatting-guide
- NeurIPS paper checklist: https://neurips.cc/public/guides/PaperChecklist
- Crossref REST API: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- OpenAlex API: https://help.openalex.org/api/
- Litmaps features: https://www.litmaps.com/features
- Nature Methods, “What’s your hypothesis?” (2026): https://www.nature.com/articles/s41592-026-03104-y
- Research idea-generation study, LiveIdeaBench (Nature Communications, 2026): https://www.nature.com/articles/s41467-026-70245-1

---

## Bottom line

Start with reproducible evidence and falsifiable hypotheses, not an agent count or a target journal's prestige. Claude should coordinate a closed-loop research process in which literature, code, data, experiments, statistics, and writing share a common audit trail—and in which independent agents can block a favored idea. Scale only after a small experiment provides a strong reason to spend more compute. The intended outcome is not “a paper that sounds revolutionary”; it is a finding that survives the strongest attempts to show it is already known, incorrectly measured, or not real.
