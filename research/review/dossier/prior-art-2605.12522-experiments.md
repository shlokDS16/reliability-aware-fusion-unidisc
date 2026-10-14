```yaml
agent: paper-reader
date: 2026-10-14
brief: "Decide from full text and released code of arXiv 2605.12522 which arms of our four-arm value-rule experiment (framework-v2 D4) it already runs, under which conditions."
sources_examined:
  - arXiv:2605.12522 v1 (Zhang et al.), local copy research/sources/md/2605.12522.md and pdfs/2605.12522.pdf (28 pages; Fig 3 page rendered and viewed)
  - github.com/imzzy1201/DifferenceDiffusionAutoregressive @ 8bafc9e (HEAD, 2026-07-28; fetched via gh api into the session scratchpad: README.md, src/config.py, decode.py, eval_utils.py, models.py, train.py, fineweb_data.py, tinystories_data.py, trained_tokenizer.py; train.py and the data loaders were listed but only grepped, not read)
  - research/review/dossier/prior-art-selection.md section P1 (as the pointer the brief named; not re-used as evidence)
coverage: >
  Paper: full text of the markdown conversion lines 1-1600 read (abstract, Sec 1-7, App A, B, C.1-C.4 text, references skimmed).
  Figures 2, 5-13 exist only as extracted axis text; only Fig 3 was viewed as an image (page 8). Numbers in Figs 8-13 were NOT read.
  Code @8bafc9e: src/config.py, src/decode.py, src/eval_utils.py in full; src/models.py lines 1-606 in full (generate_ntp, generate_block, evaluate, cross-entropy);
  train.py, fineweb_data.py, tinystories_data.py not read beyond grep. NOT covered: any run of the code (nothing executed except a CPU torch.topk tie check, below), any launch script (none in repo), wandb logs, released checkpoints (none listed in the tree).
  Repo tree at 8bafc9e has 11 files, 3 commits (6619af1 2026-04-01, d666c9c 2026-05-14 "Add code", 8bafc9e 2026-07-28 README badges); one branch (main).
claims:
  - statement: "2605.12522 runs sample-then-filter at k = 1 (low-confidence remasking: sample every masked position of the block, keep the one whose sampled token has the highest probability) at block lengths 2, 8, 32 with N = B, i.e. our arm 1 at k = 1."
    status: supported
    evidence: "Sec 3.1 p3 and Sec 5.1 p7; App C.1 p21; models.py:425-430, 441-448 (x0 sampled by Gumbel-max, confidence = softmax prob of x0, topk k=1)"
    level: E3
    confidence: 0.95
  - statement: "2605.12522 runs 'sample, select, resample' at k = 1 (our arm 2): positions chosen by SF, values redrawn from the same logits before writing."
    status: supported
    evidence: "Sec 5.2 p9 (bias elimination), App C.2 p24; decode.py:78-91 (resample=True for lcr, dlcr at B in 2, 8, 32); models.py:456-460"
    level: E3
    confidence: 0.95
  - statement: "2605.12522 does not run a rank-then-sample sampler that ranks by max_v p (our arm 3). The nearest arm is entropy remasking ('er', rank by negative entropy, then sample), which is state-only but uses a different score."
    status: supported
    evidence: "models.py:434-436 (er score = sum p log p), 432-433 (rr = random score); config.py:24 and models.py:60 restrict strategies to rr, lcr, dlcr, er; Sec 3.1 p3-4"
    level: E3
    confidence: 0.9
  - statement: "2605.12522 does not run a tilted twin (state-only tilt with the same law as SF at k = 1) (our arm 4). No code path or text describes it."
    status: supported
    evidence: "full text; decode.py:47-93 lists all 19 decode variants; none is a tilt"
    level: E3
    confidence: 0.9
  - statement: "2605.12522 sweeps no temperature on any decoding arm and reports no entropy-matched or quality-versus-entropy frontier; all Sec 5 decoding is at the code default eval_temperature = 1.0 (not stated in the Sec 5 text)."
    status: supported
    evidence: "config.py:59 default 1.0; README decode command passes no temperature flag; decode.py never sets it; App B.2 p18 states T = 1.0 only for the Sec 4 sequential decoding"
    level: E3
    confidence: 0.85
  - statement: "2605.12522 runs only one token per step for every arm (N = B), so there is no k >= 2 regime and no step sweep; the only sweep is the block length (competitor-set size) 2, 8, 32."
    status: supported
    evidence: "Sec 5.1 p7; App C.1 p21 ('we set N = B'); models.py:413 (one loop iteration per block position, topk k=1)"
    level: E3
    confidence: 0.95
  - statement: "2605.12522 tests no image, multimodal or unified model. MaskGIT appears only as a citation for confidence remasking."
    status: supported
    evidence: "grep of full text (no image-generation experiment; Chang et al. 2022 cited at Sec 2 and Sec 3.1 only); Wang et al. 2026 vision-language paper cited in Sec 2 only"
    level: E2
    confidence: 0.95
  - statement: "Forward passes are matched across all arms by construction: 480 generated tokens per sequence, one model call per token, resample adds no model call. The dynamic-threshold arm (dlcr) does not save forward passes in the code, because the loop runs a fixed number of iterations per block."
    status: mixed
    evidence: "models.py:413-419 (fixed range(current_block_len) loop, one forward per iteration); generate_ntp 352-356 (one forward per token); paper Sec 3.1 p3 says dlcr may take fewer steps (text) but the code does not realise that"
    level: E3
    confidence: 0.8
  - statement: "Intervals: none. Fig 3 has no error bars; one decode run per configuration per training seed; 512 sequences."
    status: supported
    evidence: "Fig 3 p8 (viewed); decode.py:199-218 (single evaluate call per variant); config.py:58 eval_num_samples 512, seed default 0"
    level: E3
    confidence: 0.9
  - statement: "The paper does not state the tokenizer vocabulary size; the code trains a BPE tokenizer of about 5000 types, which is far from the vocabulary of the pretrained models in Sec 3.3."
    status: supported
    evidence: "config.py:48 vocab_size 5000; trained_tokenizer.py:5-14; paper text has no vocabulary figure (grep)"
    level: E3
    confidence: 0.85
competing_explanations: []
unknowns:
  - "Whether the Sec 5 decode runs used eval_temperature 1.0 (inferred from defaults and the README command; no launch script or wandb config in the repo)."
  - "Whether the 'other seeds' in Figs 8-10 are retrained models (3 training seeds, Sec 4.2 and App C.3) or only re-decodes of one model; the text says 'repeating the main experiments', which reads as retraining."
  - "Numerical values of any Fig 3 / Fig 8-10 bar (figures only; no table)."
  - "Whether the dlcr plus resample defect described below changes the dlcr+rs bars (not run on GPU; CPU torch only)."
  - "What the Count column of App A Table 1 counts (prompts or continuations; the maximum is 999 although 20 continuations per prompt were drawn)."
next_test:
  hypothesis: "At k >= 2 with matched forward passes, the SF twin (resample) matches the entropy of the state-only twins while SF does not, and the entropy-quality frontier separates the arms; at k = 1 this is the Zhang et al. result."
  intervention: "Run our four arms on one frozen masked-diffusion checkpoint with temperature swept per arm and a step sweep (k in 1, 2, 4), reporting quality against entropy."
  primary_metric: "quality at matched entropy (frontier), with sample-level bootstrap intervals"
  falsifier: "All four arms fall on one frontier at k >= 2, or the resample twin differs from SF in entropy only at k = 1."
  gpu_hours: "not estimated here (outside brief)"
```

# 2605.12522 (Zhang et al., "Differences in Text Generated by Diffusion and Autoregressive Language Models"): which of our four arms it already runs

Evidence tags: paper text and Fig 3 are E2 for "the paper reports X". Code lines are E3 at commit 8bafc9e. Nothing here is E4 except one CPU `torch.topk` check noted below. All "paper reports" statements say nothing about whether X is true.

## Q1. Models, checkpoints, tasks, metrics

Source facts.
- Controlled decoding study (Sec 5, the only part that touches our arms): the final checkpoint of one model trained from scratch with the full diffusion objective (bidirectional context, input masking, label masking, 1/t weighting), 120M-parameter LLaMA architecture (hidden 768, 12 layers, 12 heads), FineWeb, 2B tokens, context 512, three training seeds. Locations: Sec 4.2 p6, Sec 5.1 p7, App B.2 p18. Optimiser: AdamW, global batch 1024, peak lr 1e-3 (App B.2). Hardware A100s (README). Fig 3 (p8) is one seed; Figs 8-10 (App C.3, pp25-26) hold the other seeds, a 30M Qwen2 architecture (Fig 9) and TinyStories at context 128 (Fig 10).
- Tokenizer (code only, not in the paper): trained byte-level BPE, `vocab_size = 5000` (config.py:48, trained_tokenizer.py:5-14). The paper text never gives a vocabulary size.
- Off-the-shelf comparison (Sec 3.3 p4-5, App A Tables 1-2 pp16-17): 10 ARMs and 10 DLMs, 3B to 8B, including LLaDA-8B, Dream-7B, SDAR, Fast-dLLM-v2, 1000 FineWeb prompts (30-token prompt, 20 continuations each, up to 512 tokens), model-default decoding, prompt template "Continue the following text in approximately 500 words". Only descriptive (entropy, coherence, diversity). This uncontrolled comparison does not run any of our arms.
- Metrics (Sec 3.2 pp4, Sec 4.2, Sec 5.2): n-gram entropy (n = 1, 2, 3; plug-in estimate on the pooled generated corpus, eval_utils.py:10-30), semantic coherence (mean cosine of adjacent sentences) and semantic diversity (one minus mean pairwise cosine) with four embedding models (bge-m3, embeddinggemma-300m, all-MiniLM-L6-v2, Qwen3-Embedding-0.6B), and cross-entropy H(p_con, p_seq): the average negative log-probability of each sampled sequence under the same model decoded sequentially (Eq 9 p8; models.py:480-538, with `ref_model = model` at decode.py:205-213).
- Not in the paper: MAUVE, generative perplexity under an external model, pass@k, task accuracy, any human or LLM judge. No downstream task is run. The only "quality" proxy is the cross-entropy under the model's own sequential factorisation (a self-likelihood score, so it rewards sampling toward the mode).

Inference. The cross-entropy is an in-model quantity. Any arm that sharpens the sampled law lowers it, so it cannot by itself say a lower-entropy sampler is "worse"; Zhang et al. use it only to show H(p_con, p_seq) falls below H(p_seq) (their inequality chain, Eq 8).

## Q2. Which arms they run; matched forward passes; tokens per step; step counts

The 19 decode variants are fixed in decode.py:47-93 (README "Decode variants (19 total)"): the sequential baseline (block length 1), then block lengths {2, 8, 32} x {rr, lcr, dlcr, er} (12), then block lengths {2, 8, 32} x {lcr, dlcr} with resample (6).

| Our arm | Their variant | Paper location | Code location | Match |
|---|---|---|---|---|
| 1. SF (sample all masked positions, keep top-k by sampled-token probability) | lcr, called "Confidence" | Sec 3.1 p3; Fig 3 p8 | models.py:425-430 (x0 by Gumbel-max; confidence = softmax probability of x0), 441-448 (top-1) | k = 1 only. Competitor set = the unrevealed positions of the current block of B in {2, 8, 32} (line 441 sets confidence outside the block to -inf), not the whole sequence |
| 2. Resampled twin | lcr + resample, called "Bias elimination of Confidence" | Sec 5.2 p9; App C.2 p24; Fig 3 hatched bars | models.py:456-458 (fresh Gumbel draw from the same logits for all positions, then written only at the selected index at line 460) | k = 1 only. Same positions, same marginals, same temperature (1.0) |
| 3. Rank-then-sample on max_v p | not run. Nearest: "er" (rank by negative entropy, then sample) and "rr" (random rank, then sample) | Sec 3.1 p4 | models.py:432-436 | Partly. State-only ranking is present but the score is entropy or random, not max_v p; k = 1; T = 1 |
| 4. Tilted twin (state-only tilt, same law as SF at k = 1) | not run | none | none | No |

Threshold variant. Their "dlcr" additionally commits every position whose sampled-token probability exceeds 0.9 (Sec 3.1 p3-4, tau = 0.9; models.py:450-454). This is the only place more than one token can be committed in a step. App C.1 Case 2 (p23) is the weight 1[q > tau] on that rule. It is a threshold rule, not top-k with k >= 2, and the proof still fixes N = B.

Matched forward passes. All arms generate 480 tokens (512 minus a 32-token prompt) with exactly one model call per token: generate_ntp loops `range(32, 512)` (models.py:352-356), generate_block loops `range(current_block_len)` per block (models.py:413-419). Resample adds no model call (models.py:456-458). So forward passes are matched by construction at 480 per sequence, but the paper never states or reports this as a matched-compute design; it follows from N = B.
- Inference (E3, not run): in generate_block the loop count is fixed at the block length, so dlcr does not reduce forward passes even when several tokens are committed in one step; later iterations of that block run idle. The paper text (Sec 3.1 p3) says dlcr may take fewer steps; the code does not realise that.

Tokens per step: 1 for rr, lcr, er, and for the sequential baseline; 1 plus the above-threshold set for dlcr (Sec 5.1 p7: "N equal to the block length B"). Step counts swept: none. What is swept is block length B in {2, 8, 32}, which moves the competitor-set size and the steps together (N = B), so the number of steps per sequence is constant while the competitor set changes; it is not a step sweep at fixed block length. Sec 5.1 p7 states that the steps per block equal the block length, targeting one token per step.

## Q3. Temperature-swept or entropy-matched frontier?

No. Source facts: App B.2 p18 states T = 1.0 and no top-p or top-k for the Sec 4 sequential decoding; Sec 5 states no temperature; the code default is `eval_temperature = 1.0` (config.py:59), decode.py never overrides it, and the README decode command has no temperature flag (E3). Fig 3 reports, per arm, one n-gram entropy bar and one cross-entropy bar at that single temperature. There is no curve over temperature, no quality-versus-entropy frontier and no equal-entropy comparison.

One adjacent fact that is not a frontier: the resample arm's entropy returns to about the sequential level at T = 1 (Sec 5.2 p9, Fig 3), so the SF arm and its twin are compared at different entropies by design. The paper reads this difference as the "bias". Entropy-matching by temperature is untouched.

Another code fact that matters once T differs from 1: the confidence score is the untempered softmax probability of a token drawn at temperature T (models.py:425-430 samples with `add_gumbel_noise(logits, temperature)` but scores with `F.softmax(logits)`). At T = 1 the two coincide, so the paper's runs are unaffected; a temperature sweep on this code would score by the untempered probability.

## Q4. Multimodal or image models?

No. No image, vision-language or unified model is run. MaskGIT (Chang et al., 2022) is cited as the origin of confidence remasking (Sec 2 p2; Sec 3.1 p3) and appears in the reference list; Wang et al. 2026 (a vision-language embedding-space analysis) is a related-work citation only. All Sec 5 experiments are text on the 120M model and its two ablation variants. Sec 7 p10 lists small model scale and the simplified theory as the limitations and mentions "broader DLM architectures" as future work, without naming multimodal.

## Q5. Seeds, sample sizes, intervals

- Sample size per decode configuration: 512 sequences x 480 generated tokens, from 32-token prompts taken from the FineWeb eval split (Sec 4.2 p6; config.py:58, 60; decode.py:171-177 with dataset seed = seed + 10000). Pooled n-gram counts come from about 245k tokens per configuration against a trained vocabulary of about 5000 (so trigram plug-in entropy is a biased estimate; the same for every arm).
- Seeds: three training seeds (Sec 4.2 p6; Fig 5). Sec 5.1 p7 and App C.3 p24: Fig 3 = seed 0; Fig 8 = seeds 1 and 2; Fig 9 = Qwen2 30M; Fig 10 = TinyStories. Decode code has one `seed_all(seed)` at import (config.py:154-161) and one evaluation per variant (decode.py:199-218); no repeated decodes with different sampling seeds.
- Intervals: none anywhere in Sec 5 or App C (Fig 3 viewed: bars only). Claims of consistency rest on the figures for seeds 0, 1, 2 agreeing by eye; I did not read the numbers of Figs 8-10.
- Sec 3.3 (off-the-shelf): per-model sample counts after degeneracy filtering vary from 215 (Dream-v0-Instruct-7B) to 999 (App A Table 1 p16), with filter removing "extremely short" or "excessively repeated" outputs; the filter removes far more DLM outputs than ARM outputs (DLM counts 215 to 982, ARM counts 946 to 999). That filter is applied before the entropy comparison. This is the paper's own descriptive result, not our concern, but it limits using Table 2 as a baseline for anything.

## Q6. Verdict per arm and per condition

Condition key: C1 = k = 1 (one token per step), T = 1, small from-scratch bidirectional model, block-limited competitors, text; C2 = k >= 2 at matched forward passes (step sweep); C3 = entropy-matched frontier via temperature sweep; C4 = pretrained model (LLaDA/Dream scale); C5 = unified multimodal or image model.

| Arm | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| 1 SF | Already done (lcr) | Not done (dlcr is a threshold rule at N = B) | Not done | Not done | Not done |
| 2 Resampled twin | Already done (lcr + rs) | Not done | Not done | Not done | Not done |
| 3 Rank-then-sample on max_v p | Partly done: er (entropy score) and rr (random score) run; max_v p score not run | Not done | Not done | Not done | Not done |
| 4 Tilted twin | Not done | Not done | Not done | Not done | Not done |

Quality reporting: their metrics are n-gram entropy, semantic coherence and diversity and a self-cross-entropy; no task or reference-quality metric, so "quality against an entropy-matched frontier" is not run in any form.

What remains genuinely new, in one paragraph. The comparison of arm 1 against arm 2 at k = 1 and T = 1 on text is already in 2605.12522 (Fig 3 and App C.2): their resample fix is our arm 2 as an operation, so a result of the form "SF has lower entropy than its resampled twin" at k = 1 is not new and must be cited as theirs. Genuinely absent from the paper and its code: (a) the tilted twin, arm 4, which has no counterpart; (b) any k >= 2 regime at matched forward passes with a step sweep (their theorem and runs are N = B only); (c) any temperature sweep and entropy-matched frontier; (d) a rank-then-sample arm scored by max_v p (their entropy arm is the nearest); (e) any model beyond a 120M text model, including a pretrained text DLM and any image or unified multimodal model. The smallest extension that makes the experiment new on this paper's evidence is to run arms 1, 2 and 4 at k >= 2 (at least k in 1, 2, 4 at matched forward passes) with a per-arm temperature sweep reporting quality against entropy; either the tilted twin or the k >= 2 step sweep alone already separates it from their design, and the frontier makes the comparison meaningful where theirs is a single point. A unified multimodal model would add a new setting but, if it only repeats arms 1 and 2 at k = 1, would be a replication of their claim in a new modality, not a new result about the value rule. These are inferences from this one paper; novelty against 2609.34509 (which the dossier records as sweeping T in {0.6, 0.8, 1.0, 1.2} on LLaDA-8B for LCR against a max-probability ranker at one token per step) and the other prior art is outside this brief and should not be assumed from this report.

## Gaps between paper and code (E3 at 8bafc9e)

1. Vocabulary size 5000 (config.py:48) is not in the paper. The "off-the-shelf" claim in Sec 1 and Fig 1 concerns 3B to 8B models with ordinary vocabularies; the controlled mechanism is shown on a 5000-type vocabulary. Whether the entropy deficit scales with vocabulary size is unknown.
2. dlcr does not reduce the number of forward passes in the code (loop count fixed, models.py:413), contrary to the Sec 3.1 description of fewer steps (E3 inference from reading; not run).
3. Possible defect in dlcr plus resample (not run on GPU): once dlcr fills the block early, remaining iterations of that block have every confidence at -inf (non-masked positions set at models.py:445, positions beyond the block at 441), `torch.topk` still returns an index (models.py:447), and with `resample` on, `x0` is redrawn for every position (models.py:458) so `x[transfer_index] = x0[transfer_index]` (line 460) can overwrite an already-committed or prompt token. I checked only that CPU `torch.topk` (torch 2.11.0+cu130) on an all -inf row returns index 0, which is a prompt position (prompt length 32). The GPU tie-breaking and whether any block actually fills early (needs probability above 0.9 on a non-top-ranked position) were not tested. It does not touch the lcr + rs arm (k = 1 means every iteration has a masked position in the block), so it does not affect our arm 2 comparison; it could affect their D-Confidence hatched bars in Fig 3.
4. Confidence is the untempered probability of a temperature-T draw (models.py:425-430); relevant only if T is varied.
5. decode.py takes `latest_ckpt_name` by trainer-state step (decode.py:154-163), consistent with "final checkpoint" in Sec 5.1; Sec 4.3's equal-loss checkpoint matching applies to the Sec 4 comparison only.

## Stated and unstated limitations

Stated (Sec 7 p10): small models; theory under simplifying assumptions. Unstated, found here: no temperature variation; only k = 1 (N = B); competitor set limited to blocks of 2, 8, 32 (not whole-sequence SF); no intervals and a single decode per configuration; metrics are self-referential or descriptive (no task or reference quality); the "other seeds" figures were not read numerically; vocabulary size 5000 undisclosed in the paper; dlcr code and text disagree on step savings; Sec 3.3 sample filtering is uneven between ARMs and DLMs.

## Corrections relative to the existing dossier

None to the dossier's P1 description of the fix (models.py:~425-458 matches: x0 drawn, confidence of that x0, top-1 selection, `if resample:` redraw, write at selected indices). Additions: the arm-by-arm table above; the vocabulary size; the fixed-iteration dlcr point; the possible dlcr + rs overwrite; confirmation that decode.py runs 19 variants with no temperature argument. The dossier's "temperature for Sec 5 not stated" unknown is narrowed from "unknown" to "default 1.0 by code (E3), not stated in the text".
