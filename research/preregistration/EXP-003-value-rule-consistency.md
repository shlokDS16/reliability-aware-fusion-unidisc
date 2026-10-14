```yaml
agent: experiment-designer
date: 2026-10-15
brief: Preregistration card EXP-003 v0.1. How much of UniDisc 1.4B's joint text-image consistency comes from its value rule? Plain sampling versus the official guided sampler, at matched forward passes, after the same rung-2 COCO prefixes, on fresh prompts and seeds. Follows decision D0016 (EXP-001 stopped at PG-V).
card:
  id: EXP-003
  version: v0.1
  status: draft, unsigned
  signatures: {statistician: none, red-team: none, novelty-auditor: none}
  frozen: false          # frozen when statistician and red-team sign and the novelty precondition (1.3) is met; afterwards changes only as a new version with a change log
  supersedes: none
  hypothesis_ledger_ids: to be assigned by the orchestrator (E3-H1, E3-H2a, E3-H2b, E3-H3, E3-H4); no ledger rows written by this draft
  decision_ledger: D0016 (names this experiment as the next step)
sources_examined:
  - research/CONTRACT.md
  - research/ledgers/decisions.jsonl (D0016)
  - runs/EXP-001/IMPLEMENTATION.md (in full)
  - research/preregistration/EXP-001-crossmodal-unidisc.md (change log v0.4 to v0.5; sections 1.3, 2 (H-A definitions only), 3, 4.1b-4.5, 5.1-5.2, 6, 7.1-7.4, 9, 10.1-10.5, 12.2, 13, Appendix B)
  - research/preregistration/EXP-002-value-rule-decomposition.md (header block only)
  - research/review/coverage/census-result-v1.md (in full)
  - runs/env-2026-10-14/setup.md (section 2, UniDisc)
  - runs/EXP-001/gates/verdict-pgv-rung1.json, verdict-pgv-rung2.json, coco_draw.json (aggregates only, used for assumed sizes)
  - exp001/ (config.py, plan.py, sampler.py, estimator.py wrapper nets, unidisc_net.py, gate_gen.py, runtools.py), analysis/EXP-001/ (prefix_rule.py, completion.py, evalmodels.py, coco_draw.py), tools/gpu_guard.py
  - models/third_party/unidisc/model_eval.py lines 1737-1760, 2440-2455, 2964-3000, 3040-3100 (get_cfg_weight, noise removal, adap_sche, _maskgit_update)
  - scratch computations in the session scratchpad (leftover COCO items; operating characteristics; cost arithmetic); not in the repository
coverage: >
  Read in full or at the sections named above. NOT read: the UniDisc paper, any generated image from EXP-001, the per-sample VLM presence values
  of the gates (not stored; only aggregates and 90 percent cluster intervals exist), the official sampler outside the lines listed, EXP-001
  sections 8 and 11 and 14-17. Nothing in this card has been run on this experiment. Every [A] number is an assumption until the cost pilot.
  The UniDisc code checkout was read as it stands in models/third_party/unidisc; its commit was not re-verified here.
claims:
  - statement: "Under plain sampling (condition P, J at k0), prefix-conditioned joint completion on UniDisc at 512 px shows no measurable completion-specific link in the OR-rule statistic (m - s_sp 0.000 at rung 1, -0.021 at rung 2, 24 prefixes), while the per-noun rates show a small gap (rung 2: matched 0.350, same-prefix 0.279, cross-prefix 0.213); images are texture-like; the checker is valid (PC-F)."
    status: supported
    evidence: runs/EXP-001/gates/verdict-pgv-rung1.json, verdict-pgv-rung2.json, verdict-pcf.json; D0016
    level: E4
    confidence: 0.75
  - statement: "The official UniDisc maskgit sampler is not plain sampling even with guidance off: per step it draws a token for every masked position, scores positions by log p(sampled token) + r_temp x Gumbel x t pooled over both modalities, commits the top schedule[step] by an arccos schedule (few tokens early, many late), uses a CFG weight cfg x (1 - t) with a second network pass, and runs one final argmax pass (noise_removal)."
    status: supported
    evidence: models/third_party/unidisc/model_eval.py get_cfg_weight L1737-1760, noise removal L2440-2447, adap_sche L2964-3000, _maskgit_update L3047-3100; runs/env-2026-10-14/setup.md 2.4-2.5
    level: E3 (checkout read; commit not re-verified)
    confidence: 0.9
  - statement: "With eval.cfg = 0 the official sampler makes one network call per step and equals the unguided marginal (max difference 0.0)."
    status: supported
    evidence: runs/env-2026-10-14/setup.md 2.1 (CFG switch, stage e)
    level: E4
    confidence: 0.9
  - statement: "Measured costs at 512 px: plain pass 0.099-0.101 s including sampler arithmetic; official guided sampler (50 steps, CFG 3.0, clean-caption T2I) 10.4 s per sample."
    status: supported
    evidence: runs/EXP-001/IMPLEMENTATION.md section 5
    level: E4
    confidence: 0.9
  - statement: "1,394 COCO val2017 items are rung-2 eligible under prefix_rule v2 and in none of the 2,800 images of any EXP-001 block, so fresh pools of the sizes below exist."
    status: supported
    evidence: scratch computation over captions_val2017.json and runs/EXP-001/gates/coco_draw.json (session scratchpad leftover.py; the engineer rewrites it into the repository and records the id-list hash)
    level: E4
    confidence: 0.85
  - statement: "E3-H1: the official guided sampler yields a larger completion-specific link than plain sampling at matched forward passes (G minus P64 on the discordant-noun link, at least +0.10)."
    status: unknown
    evidence: none (prediction)
    level: E0
    confidence: 0.5
  - statement: "E3-H2a/b: if H1 holds, part of it comes from guidance itself (G minus O0) and part from the official sampler's non-plain selection, pooled ordering and schedule (O0 minus P32)."
    status: unknown
    evidence: none (prediction)
    level: E0
    confidence: 0.4
competing_explanations:
  - the observed prefix is a common cause of completion nouns and image content, and guidance strengthens prefix conditioning (control, same-prefix sibling baseline, discordant-noun restriction, NC-1)
  - guidance lowers between-seed diversity, which mechanically shrinks any matched-minus-sibling contrast (control, discordant-noun restriction, diversity report, discordant counts)
  - the official sampler's non-plain parts, not guidance, create the link: sample-then-filter selection by sampled-token probability, pooled text-first ordering, arccos schedule (control, arm O0, contrasts E3-H2a/b, commit-order record)
  - extra compute: a guided step costs two network calls (control, primary comparator P64 at matched calls, P32 at matched steps, both reported)
  - measurement-range effect: guided images are more object-like, so the VLM is more discriminating on them without the dependence changing (control, NC-1, PC-1, PC-2, per-arm base rates, CLIP concordance rule, COCO-noun sensitivity)
  - noun composition: guided completions contain more depictive nouns (control, COCO-category-noun sensitivity, composition share reported)
  - degenerate output of G at 32 steps instead of the default 50 (control, pilot screen and stop rule 9.2)
unknowns: [Lambda_b under P and under G; discordant-noun counts per arm; whether the official sampler commits the tail before the image; per-call VLM cost; official-sampler cost per step in the joint row; completion length, empty-completion rate and debris share under G; whether G at 32 steps is non-degenerate at 512 px; whether the VLM resolves nouns on plain-sampling images well enough for PC-1]
next_test: {hypothesis: "E3-H1, E3-H2a, E3-H2b", intervention: "plain sampler (J, 64 and 32 passes) versus official sampler with CFG 0 and 3.0 (32 steps) after fresh rung-2 prefixes", primary_metric: "discordant-noun link Lambda_d, G minus P64, prefix-cluster paired bootstrap", falsifier: "section 5 (null class: 90 percent interval inside (-0.10, +0.10) with NC-1, PC-1, PC-2 passed)", gpu_hours: "about 2.8 compute-hours, about 5.8 wall-clock hours at duty 0.5 (section 8)"}
```

# EXP-003 v0.3: does the value rule carry the joint text-image consistency of a unified discrete-diffusion model?

Tags: [S] source fact, [I] inference, [H] hypothesis, [A] assumption until the cost pilot, [C] computed here (scratch, the statistician recomputes), [E3] code read, [E4] measured. EXP-001 section numbers are written "EXP-001 4.4" and so on; EXP-001 v0.5 is the signed card and its text governs wherever this card says "as EXP-001".

## 0. Summary

One frozen checkpoint (UniDisc 1.4B interleaved), 512 px, rung-2 COCO prefixes (5-9 words), 32 masked tail tokens, full bidirectional attention. Four arms on the same fresh prefixes: **P64** and **P32** (plain sampling at temperature 1, no guidance, within-modality confidence ranking, EXP-001 plan J at 64 and 32 passes), **O0** (the official maskgit sampler with guidance off) and **G** (the official sampler with CFG 3.0), both at 32 steps. The primary endpoint is the **completion-specific link**: for each noun the completion names that the sibling seed's completion does not, how much more often the VLM finds it in this sample's own image than in the sibling's image (same prefix, other seed). Primary contrast: **G minus P64**, at matched network calls, with the prefix as the cluster. Two confirmatory secondaries split the difference into guidance (G minus O0) and the rest of the official sampler (O0 minus P32). One negative control, one positive control and one instrument check say whether a null can be read as a null. A pilot on a separate pool fixes only costs and variances. If guidance does not create a completion-specific link either, the joint consistency of the guided sampler comes from the prefix, not from co-generation, and Paper 1 says so (section 10).

## 1. Claim contract

### 1.1 Claim, one sentence
On UniDisc 1.4B at 512 px, after a rung-2 COCO prefix, a 32-step variant of the official guided sampler (CFG 3.0; the shipped default is 50 steps) produces a larger completion-specific text-image link than plain sampling at the same number of network calls, and the part attributable to guidance itself is measured by holding the rest of the official sampler fixed (arm O0). Scope sentence for every statement: "on UniDisc 1.4B, at 512 px, after rung-2 prefixes of the caption form the prefix rule selects, with 32 tail tokens, CFG 3.0 (and 0) at 32 steps, with the Qwen3-VL-2B presence checker".

### 1.2 Mechanism (hypothesis, [H])
Under plain sampling at k0 each pass commits one tail token beside 32 image tokens, so image tokens are committed while most of the tail is still masked; EXP-001 measured no completion-specific link there. [I] The official sampler ranks pooled positions by the probability of the token it just drew. Text marginals are lower-entropy than image marginals in the one state measured (mean entropy 5.0 against 6.5 nats, top-1 0.18 against 0.042; setup.md 2.1 b), so text tends to be committed earlier and the image sees more of the completion. [E3, v0.2, red-team F-3] CFG replaces each marginal by (1 + w) conditional minus w unconditional with w = cfg x (1 - t), and the unconditional branch removes **only the prefix positions** (`model_eval.py` L1769); committed completion and image tokens are present in both branches. [H] Guidance therefore amplifies dependence on the **prefix** directly; any effect on the completion-image link is indirect (through what the prefix-amplified marginals commit). The sibling baseline cancels the shared prefix; the seed-balanced statistic (4.1) cancels image-level yes-bias. A run-time assertion checks that guidance acted (v0.3, red-team R1): at the **first step with t < 1** (step 1 of 32; at step 0, t = 1 and w = cfg x (1 - t) = 0, so no unconditional call is made), the guided text and image marginals differ from the conditional-only marginals at the same state (max absolute difference above 1e-3), logged per unit. G therefore makes 31 guided steps x 2 calls + 1 unguided step + the final pass = 64 calls (not 65); the matching with P64 is exact. The card separates these: prefix versus completion by the sibling baseline, guidance versus ordering by O0, compute by P64 versus P32.

### 1.3 Closest work and the exact distinction
- EXP-001 (this project): the same task and checker under plain sampling; stopped at PG-V (D0016). Distinction: fresh pools, a completion-specific statistic with a same-prefix sibling baseline, and a guided arm.
- UniDisc's own guidance study (App. I, Fig. 24-25, as relayed in EXP-001 1.3; not re-read): CFG windows move CLIP score. Distinction: no same-prefix control there, guidance is treated as the model's value of the other modality, not as a sampler component to be separated from ordering and compute.
- EXP-002 (this project): sample-then-filter decomposition on text diffusion models. The official sampler's selection step (draw, then rank by the drawn token's probability) is of that type (census class S); this card does not separate it from the pooled ordering and the schedule (section 2).
- Census (research/review/coverage/census-result-v1.md): 37 of 45 headline results use a non-plain value rule or do not state one (purposive sample of 47, not the systematic corpus). This card tests whether that matters for a joint-consistency claim in one model.
- **Novelty status.** No `novelty-auditor` verdict exists for this card. No novelty claim is made beyond "a controlled comparison"; the audit is a freeze precondition. No citation here is new; every external item comes from project files.

### 1.4 Competing explanations
Listed in the header with their controls; the controls are in sections 2, 4, 6 and 9.

## 2. Conditions, pass accounting and the choice of primary matching

All arms: same weights (bf16), SDPA attention as EXP-001, layout `PREFIX + <m>*32` with no space (prefix_rule v2), 512 px (L_I = 1,024, 1,056 generated positions), batch size 1, eval-mode assertion (section 8).

| Arm | Sampler | Value rule | Position rule and schedule | Steps | Network calls | Est. s per sample |
|---|---|---|---|---|---|---|
| P64 | exp001 `run_sample`, plan J, N = 64 (EXP-001 5.1, k-) | plain, T = 1, float64 inverse CDF | within-modality confidence ranking; uniform counts (about 16.5 tokens per pass) | 64 | 64 | 6.4 [E4 x 64] |
| P32 | same, N = 32 (EXP-001 k0, the condition EXP-001 gated) | plain | same (about 33 tokens per pass) | 32 | 32 | 3.2 [E4 x 32] |
| O0 | official `_sample`, maskgit, `eval.cfg = 0`, `noise_removal` on, r_temp 4.5 | token drawn by `torch.multinomial` at T = 1, then kept or deferred by its own probability (sample-then-filter type) | pooled over both modalities by log p(drawn token) + 4.5 x Gumbel x t; arccos schedule | 32 | 33 (32 + final pass) | about 3.4 [A] |
| G | same with `eval.cfg = 3.0` (the UniDisc inference setting; weight cfg x (1 - t)) | O0's rule with guided marginals | as O0 | 32 | 64 (step 0 has w = 0: 1 + 2 x 31 + final pass; v0.3) | about 6.8 [A: 10.4 s x 32/50 + 0.1] |
| G-low (optional, descriptive) | as G with `eval.cfg = 1.0` | | | 32 | 65 | about 6.8 |

**Official-sampler settings.** Everything at the UniDisc inference experiment's defaults (setup.md 2.5) except the step count, which is 32 instead of 50 (`sampling.steps` and `sampling.max_sampling_steps` both set; they must be equal). Reason for 32: it makes the call count of G (65) equal that of P64 (64) to within the official final argmax pass, and 32 is the step count of the demo UI [S, setup.md 2.5]. The final pass commits nothing if the last scheduled step empties the mask; the number of positions still masked before it is recorded per sample. The official final pass is counted in O0 and G.

**What O0 and G are.** The official sampler bundles four things that P does not have: (a) a selection step on the drawn value, (b) pooled text-and-image ranking with Gumbel noise, (c) an arccos schedule, (d) for G, guidance. O0 minus P bundles (a) to (c); G minus O0 is (d) alone. The card does not separate (a), (b) and (c) from each other. The phrase "the value rule" in Paper 1 therefore refers to (a) and (d) together with the ordering that (a) induces, and says so.

**Primary matching: network calls (G against P64).** Justification. (1) A guided step costs two network calls; comparing G with a plain sampler of 32 passes would credit the value rule with what twice the compute buys. The project compares at matched forward passes (EXP-001 5.2, EXP-002). (2) The choice favours P (finer schedule, 16.5 tokens per pass instead of 33), so a positive for G is the conservative finding and a null is the stronger null. (3) The steps-matched contrast G minus P32, and the plain sampler's own response to doubling its passes (P64 minus P32), are reported with intervals so that the reader sees both ("matched denoising steps" and "matched forward passes"). E3-H2a is the clean steps-matched statement about guidance because O0 and G share steps, ordering and schedule.

## 3. Pools, pairing, seeds

- **Source.** COCO val2017, one caption per image (smallest annotation id), rung-2 prefix rule v2 (EXP-001 4.2, `analysis/EXP-001/prefix_rule.py`, spaCy en_core_web_sm 3.8.0), exactly as EXP-001 3 item 8.
- **Fresh items.** Exclude every image id in any block of `runs/EXP-001/gates/coco_draw.json` (2,800 ids). 2,200 images remain, 1,394 of them rung-2 eligible [C]. Permute the eligible leftovers with seed 1303 and take, in this order: E3-PILOT 16 prefixes, E3-CTRL 48, E3-MAIN 150. The id lists and their SHA-256 go to `runs/EXP-003/pools.json`, with a machine check of disjointness from `coco_draw.json`, before any generation. The 32 guided-T2I images of EXP-001 PG-1 are used only for PC-2 (section 6), never as evidence on E3-H1 to H4.
- **Unit.** The prefix is the cluster; each arm generates 2 seeds per prefix. Seed index i = base + 2p + e (e in {0, 1}): E3-PILOT base 61000, E3-CTRL 62000, E3-MAIN 60000. Pool codes 31, 32, 33 for the counter-based generator (additive registration; if it needs an edit of `exp001/config.py` the edit is logged and the 130 EXP-001 tests are rerun).
- **Randomness.** Plain arms use the Philox float64 uniforms of EXP-001 4.5 (common random numbers between P32 and P64 by position). The official arms seed `torch` and `numpy` with 7,000,000 + i immediately before `_sample` (the sampler uses the global generators); O0 and G share the seed but diverge as the states diverge. There is no common-random-number link between P and the official arms. **Pairing is at the prefix level** (all arms see the same prefixes); the seed label carries no information because the primary statistic is symmetric in the two seeds.
- **No sample is filtered, retried or discarded.** Failures (NaN, OOM, exception swallowed by `try_except` in `_sample`) are counted and reported; an exception returns `None` and the unit is rerun once, then logged as failed.

## 4. Endpoints

### 4.1 Primary (one): the discordant-noun link
For an arm, a prefix p and a seed e, take the completion by the caption-end rule (EXP-001 4.1b, `caption_end.py`, `debris_patterns.txt`) and its completion nouns N_pe by the EXP-001 4.4 rule (word-initial subtokens tagged NOUN or PROPN on the final caption, not in the prefix, not in `nonvisual_nouns.txt`). Noun key kappa(n) = lower-cased surface with a final -s or -es removed when at least three letters remain (`analysis/EXP-003/nounkey.py`, frozen, unit-tested); the key is used for set operations only, the VLM is asked the surface form. The sibling of (p, e) is (p, 1 - e) in the same arm.
- y(n, x) = 1 if the pinned VLM answers `Is there a {noun} in this image? Please answer yes or no.` with P(yes) at least 0.5 for image x (EXP-001 7.2/4.4 template, Qwen3-VL-2B-Instruct at the EXP-001 pin, two-way softmax of the Yes and No logits).
- Discordant nouns D_pe = { n in N_pe : kappa(n) not in kappa(N_p,1-e) }: nouns this completion names and the sibling's completion does not.
- **Seed-balanced link (v0.2, primary; red-team F-1).** For a prefix with both D_p0 and D_p1 non-empty, L_p = (1/2) [ mean over n in D_p0 of ( y(n, x_p0) - y(n, x_p1) ) + mean over n in D_p1 of ( y(n, x_p1) - y(n, x_p0) ) ], and **Lambda_b(arm) = the mean of L_p over the eligible prefixes** of that arm. Each seed's own-minus-sibling mean enters with weight 1/2 whatever its noun count, so an additive image-level yes-bias (b0 for x_p0, b1 for x_p1) enters as +(b0 - b1)/2 and -(b0 - b1)/2 and cancels exactly; the v0.1 instance-weighted ratio Lambda_d does not cancel it when a seed's yes-bias correlates with its discordant count (toy: +0.07 to +0.18 with no noun link, `analysis/framework/redteam_exp003_quality_coupling.py`). Prefixes with an empty side are excluded from Lambda_b for that arm; their share is reported per arm, and an arm contrast uses the prefixes eligible in both arms (count reported). The v0.1 ratio Lambda_d is reported as a sensitivity.
- **Placebo nouns (NC-2, v0.2).** For every eligible prefix and seed, as many placebo nouns as |D_pe|, drawn without replacement from the discordant nouns of a different prefix of the same arm (one fixed derangement, seed 5302) and absent from both completions' noun keys, are scored on x_p0 and x_p1 and pass through the same L_p formula: Lambda_b^plac(arm). It bounds only bias that is additive or independent of which nouns the sample's own text selected (v0.3, red-team R2): placebo nouns are not selected by the sample's text, so a quality effect that changes both which nouns a completion names and how findable those nouns are in its own image is invisible to NC-2 (red-team toy: Lambda_b +0.05 to +0.16 with zero noun link and a clean placebo, `analysis/framework/redteam_exp003_balanced_check.py`).
- **Quality-matched sensitivity (v0.3, descriptive).** Lambda_b recomputed on the prefixes whose two sibling images differ in CLIP-IQA by less than the arm's median absolute sibling difference, and the slope of L_p on the sibling CLIP-IQA difference (cluster bootstrap). A positive Lambda_b that vanishes in the quality-matched half, or a slope whose interval excludes 0, is reported as "consistent with quality-mediated coupling". **Pass on G and on P64:** the 95 percent cluster interval of Lambda_b^plac contains 0 and has half-width at most 0.10. **Delta1 is also reported net of placebo**, Lambda_b - Lambda_b^plac per arm (sensitivity, not the primary).
- **Why this statistic.** Prefix and checker bias enter both terms of the difference; the sibling image shares the prefix, the arm, and the guidance strength, so a prefix common cause cancels. Restricting to nouns the sibling's text lacks keeps the contrast identified when guidance makes completions more alike: a noun both seeds name tells nothing about dependence. The cost is fewer instances; their counts are reported per arm.
- **Primary contrast: Delta1 = Lambda_b(G) - Lambda_b(P64).** Minimum effect of interest (MEI) 0.10 [a choice, not derived: ten points of presence rate on a scale where the whole per-noun matched-minus-same-prefix gap under P in the EXP-001 gate was 0.04 (rung 1) to 0.07 (rung 2), all nouns, 24 clusters, descriptive only, not evidence].

### 4.2 Confirmatory secondaries (Holm, section 7)
- **Delta2a = Lambda_b(G) - Lambda_b(O0)**: guidance alone at matched steps (G costs twice the calls; that is the treatment).
- **Delta2b = Lambda_b(O0) - Lambda_b(P32)**: the official sampler without guidance against plain sampling at the same steps and (33 against 32) the same calls: selection, pooled ordering, arccos schedule.
- Delta1 = Delta2a + Delta2b + (Lambda_b(P32) - Lambda_b(P64)) exactly; the last term is reported.

### 4.3 Descriptive (95 percent cluster-bootstrap intervals, uncorrected, flagged; no decision rule except the wording rules of 4.5)
1. Steps-matched total G - P32; plain doubling P64 - P32; G - P64 for every item below; **the 95 percent interval of Lambda_b for each arm separately** (v0.2, statistician 8); Lambda_b^plac per arm; the v0.1 ratio Lambda_d per arm.
2. All-noun link Lambda (all completion nouns, matched minus sibling) and the EXP-001 4.4 OR-rule rates m, s, s_sp with m - s_sp (one cross-prefix derangement, base seed 5301, instead of four).
3. Prefix versus completion: per-noun matched minus cross-prefix presence (all nouns), and the matched and sibling rates separately, per arm (P32 has no cross-prefix calls; Ind has them). Under the hypothesis that guidance mainly strengthens the prefix, this gap rises more than Lambda_b.
4. CLIP ViT-L/14 (EXP-001 pin) matched-minus-shuffled lift of the **full caption** and of the **completion only** (EXP-001 7.1 definition: C_i - B_i, baseline inside the arm), prefix-only lift, and the **CLIP sibling link** 100[cos(x_i, c_i) - cos(x_sib, c_i)] for completion-only and full text. Empty completions are scored as they are and counted. CLIP truncation rate reported.
5. Image quality: mean CLIP-IQA per image (EXP-001 implementation on the pinned CLIP weights). Fraction of near-uniform images (pixel-SD proxy as EXP-001 PG-1).
6. Completion: length, completion nouns per sample, discordant share |D|/|N|, empty-completion rate, debris share, share of caption ends set by e2, pad share of the tail.
7. **Diversity and entropy of the text tail** (the census's point). (a) Sibling overlap: Jaccard similarity of the two seeds' completion noun-key sets per prefix. (b) Unigram entropy (nats, plug-in) of completion words pooled over an arm, on a random subsample of exactly T_ref words, T_ref = the smallest arm total, 100 subsamples, mean reported (removes the sample-size bias). (c) Distinct-2 on the same subsamples. (d) Image side: mean pairwise CLIP image cosine across prefixes, and the mean sibling cosine. (e) Model side, **only if** a read-only hook on the sampler's marginals changes neither arithmetic nor RNG use (checked by token identity on 8 samples with and without the hook): mean entropy of the tail marginals at passes 1, 8, 16, 24, 32.
8. Composition sensitivity: Lambda_b on nouns whose key is on a frozen list of single-word COCO object-category names (`analysis/EXP-003/coco_object_nouns.txt`, built from the COCO 2017 category list), and the share of each arm's nouns on the list.
9. Commit order (G, O0; P from its plan), **required output (v0.2, red-team F-4)**: a read-only record of the token row at each `_maskgit_update` entry (the hook is verified not to change tokens on 8 units): mean normalised commit step of tail tokens against image tokens, and the share of the tail committed before 25 percent of the image.
10. Pad-mass and failure counts; seconds per sample per arm; telemetry summary.

### 4.4 Guardrails read with a positive Delta1 (point estimates)
(i) G's mean completion length within [0.5, 2.0] of P64's; (ii) G's empty-completion rate below 0.25; (iii) G's discordant noun count at least 0.4 x P64's (below: "sparse", the interval is the reference); (iv) G's near-uniform image fraction at most 0.15. A positive with a failed guardrail is reported "positive with regression" and is not used as support without that qualifier.

### 4.5 Wording rules (spend no alpha)
- **W0 term (v0.3, red-team R2).** A positive Lambda_b or Delta1 is worded "a seed-specific noun-level dependence between the completion and the image, which may include quality-mediated class-level coupling"; the term "completion-specific link" is not used for any result of this card. The quality-matched sensitivity (4.1) is reported beside it.
- **W1 concordance.** A positive Delta1 is worded as in W0 (not as "not confirmed by CLIP") only if the CLIP completion-only sibling-link contrast G - P64 has a 90 percent lower limit above 0. Otherwise: "higher VLM noun presence in the own image than in the sibling image, not confirmed by CLIP".
- **W2 instrument.** A "null" or "no link" wording needs NC-1, NC-2 (on G and P64), PC-1 and PC-2 passed, and carries the stated limitation (v0.3, red-team R4): the instrument's sensitivity to within-prefix differences was tested on plain-sampler images (PC-1) and its cross-caption sensitivity on guided images (PC-2); its within-prefix sensitivity on guided images is untested. Otherwise the label is "not measurable with this instrument".
- **W3 composition.** If Delta1 is positive and the COCO-noun sensitivity contrast has a 90 percent upper limit below 0.05, add "may reflect noun composition".
- **W4 attribution (v0.2).** Each sentence maps to a tested statement: "positive" needs the Holm-adjusted test; "not detected" is the default for a non-significant contrast; "does not" or "not from" needs that contrast's null class (equivalence). No share-of-effect statement.
- **W5 scope of a null (v0.2, statistician 4).** Any null or "no link" statement carries the per-arm discordant-noun and eligible-prefix counts and is worded "among nouns that one seed names and the other does not". If G's discordant count is below 0.4 times P64's, the null is labelled "sparse".

## 5. Hypotheses, effect sizes, outcome classes, falsifiers

Contrasts are two-sided so that a reversed result is detected. d is a point estimate, (lo, hi) the 95 percent paired cluster interval, m = 0.10.
- **E3-H1 (primary).** Delta1 > 0, tested two-sided against 0 (v0.2, statistician 2). The MEI 0.10 is the power target and the equivalence margin; "at or above the MEI" is a point-estimate descriptor only (P(d >= 0.10 | true 0.10) = 0.50) and is never worded as "shown to be at least 0.10". Prediction (E0, 0.5): positive.
- **E3-H2a (confirmatory).** Delta2a > 0 (guidance raises the link at matched steps), tested against 0.
- **E3-H2b (confirmatory).** Delta2b > 0 (the official sampler's bundle without guidance raises it), tested against 0.
- **E3-H3 (descriptive).** The prefix-driven gap (4.3 item 3) rises under G by more than Lambda_b does.
- **E3-H4 (descriptive, directional).** G lowers diversity against P64: sibling Jaccard higher and pooled unigram entropy lower, each with a 95 percent interval excluding 0. A claim in Paper 1 needs both.
- Dose (G-low) is descriptive: Lambda_b(O0) <= Lambda_b(G-low) <= Lambda_b(G) is stated as observed or not.

**Outcome classes for Delta1.** *Positive*: p <= 0.05 (two-sided) and d > 0; "at or above the MEI" if d >= 0.10. *Reversed*: p <= 0.05 and d < 0. *Null*: the percentile **and** the BCa 90 percent intervals both lie inside (-0.10, +0.10) (TOST at 5 percent; v0.2, statistician 4 and 6). *Inconclusive*: otherwise. Delta2a and Delta2b: positive and reversed at their Holm-adjusted levels; null by the unadjusted 90 percent percentile and BCa intervals, with the sentence that no family-wise claim is made about the Delta2 nulls. The margin 0.10 exceeds the whole per-noun gap EXP-001 saw (0.04 to 0.07), so a null reads "no link larger than 0.10 on the presence scale" (statistician 1).

**Falsifiers.** E3-H1 is falsified by the null class (with W2 satisfied). A positive Delta1 with a null Delta2a falsifies "guidance creates it". By the identity of 4.2, a null Delta1 together with a positive Delta2b and a null Delta2a implies that P64 - P32 is positive; the report states the three numbers whenever it states any one of them.

## 6. Controls

All on E3-CTRL (48 prefixes x 2 seeds), plain value rule, before the main stage (section 8).
- **NC-1 negative control (effect must vanish).** Arm **Ind**: plan J at N = 32 through a wrapper that returns text marginals from a forward pass with all image positions masked and image marginals from a pass with all tail positions masked and the prefix kept (EXP-001 `BlindNet` with the prefix retained on the image side; new wrapper in `exp003/`). The image law is independent of the completion given the prefix, so Lambda_b(Ind) = 0 in expectation while the prefix common cause is intact. Cost 2 calls per pass, 6.4 s per sample. **Pass (v0.2):** the 95 percent cluster interval of Lambda_b(Ind) contains 0 and its half-width is at most 0.10. NC-1 runs on plain-sampler images, so it does not control a bias specific to guided images; NC-2 (placebo nouns, 4.1) does that on G, and W2 states both. The per-noun matched-minus-cross-prefix gap of Ind is reported (expected positive: it shows the common cause is visible while the link is zero).
- **PC-1 positive control (known effect).** Arm **TF**: plan_TF at N = 32 (EXP-001 5.1: 8 text-only passes of 4 tokens, then 24 image-only passes), plain value rule, confidence ranking. The image is generated after the whole tail, so the link must be recoverable. **Pass:** Lambda_b(TF) - Lambda_b(Ind) >= 0.10 and its 90 percent lower limit above 0. If PC-1 fails, the VLM cannot register a link even when the image sees the full completion, on plain-sampling images.
- **PC-2 instrument check on guided-sampler images.** The 32 clean-caption guided T2I images already produced by EXP-001 PG-1 (512 px, 50 steps, CFG 3.0). Per-noun presence of the clean caption's nouns (stoplist applied) in the own image and in the image of another caption (one fixed derangement). **Pass:** matched >= 0.60 and matched minus cross >= 0.25 [A, chosen now]. These images are not evidence on any hypothesis here.
- Power of PC-1 [C]: with 48 clusters and sigma_d 0.45, P(pass) is 0.75 if the true TF link exceeds Ind's by 0.15 and 0.99 at 0.25.

## 7. Statistics

- **Unit and design.** Prefix cluster; every contrast is paired over the same prefixes; both seeds of a prefix move together.
- **Interval.** Percentile cluster bootstrap, B = 10,000, the same resampled prefix indices in every arm, the ratio numerators and denominators recomputed in each replicate. A replicate with zero discordant nouns in an arm is redrawn and the redraw count reported. Two-sided p as EXP-001 10.1 (R5): p = 2 min{(1 + #{theta* <= 0})/(B + 1), (1 + #{theta* >= 0})/(B + 1)}, capped at 1; if p lies within 2 sqrt(p(1 - p)/B) of its threshold, rerun that bootstrap once with B = 100,000 and a recorded seed. CLIP quantities recompute the within-arm shuffled baseline in each replicate, excluding partners with the same original index (EXP-001 10.1).
- **One primary test:** Delta1, two-sided, alpha 0.05. **Fixed sequence:** if the primary test rejects (either direction), Holm at 0.05 over {Delta2a, Delta2b}; if it does not, both are reported with Holm-adjusted p and labelled exploratory. Everything in 4.3 is descriptive.
- **Sensitivity** (reported, not decisive): confirmatory levels halved (primary 0.025, Holm family 0.025); BCa intervals; Lambda_b with discordance by exact surface string instead of the noun key.
- **Sample size and its assumptions [A until the pilot].** Sigma of the per-prefix contrast: a single arm's per-prefix link has SD about 0.19 (rung 1) to 0.31 (rung 2), obtained from the 90 percent cluster intervals of the OR-rule m - s_sp in the EXP-001 gate (24 prefixes) as SE x sqrt(24) [C]; the discordant per-noun version is assumed to be about 0.30. With paired-arm correlation 0, sigma_d = 0.30 x sqrt(2) = 0.42, rounded up to **0.45**. Required n for power 0.90 at the MEI, alpha 0.05: n = ((1.96 + 1.2816) x 0.45 / 0.10)^2 = 213 [C]. The budget (section 8) allows **n = 150 prefixes (300 samples per arm)**, floor 120. Operating characteristics at n = 150 **conditional on sigma_d = 0.45** [C; statistician recomputed: paired SD 0.32 to 0.52 depending on discordant nouns per sample; power at a true 0.10 is 0.94, 0.78, 0.61, 0.47 at sigma_d 0.35, 0.45, 0.55, 0.65; P(null | true 0) 0.44 at 0.55 and 0.19 at 0.65]. The seed-balanced estimator (v0.2) weights seeds equally, which may raise sigma_d over the instance-weighted ratio; the pilot SD is that of the paired per-prefix difference L_p(G) - L_p(P64), covariance included, not a single-arm SD times sqrt 2 (statistician 5c): SE 0.0367; achieved MDE at power 0.90 is 0.119 (0.103 at power 0.80); sigma_d 0.35 gives P(lo > 0) 0.94 and sigma_d 0.55 gives 0.61 at a true 0.10.

| true Delta1 | P(positive) | P(positive and d >= 0.10) | P(null class) |
|---|---|---|---|
| 0.00 | 0.025 | 0.003 | 0.72 |
| 0.05 | 0.28 | 0.09 | 0.38 |
| 0.10 | 0.78 | 0.50 | 0.05 |
| 0.15 | 0.98 | 0.91 | 0.00 |
| 0.20 | 1.00 | 1.00 | 0.00 |

  Holm second-step power for a Delta2 of 0.10 is 0.68 (0.97 at 0.15). **n rule after the pilot:** n_conf = clamp(n_req, 120, min(150, n_cap)), where n_req uses sigma_d,up = 1.21 x the pilot SD of the paired per-prefix influence values (sqrt(15 / chi2_{0.20, 15}) = 1.206, the 80 percent upper factor for 16 clusters) and n_req = ceil(((1.96 + 1.2816) sigma_d,up / 0.10)^2) and n_cap is the largest n for which the projected wall-clock (section 8) with the pilot's measured costs is at most 6.0 hours. If no n >= 120 fits, the overrun goes to the orchestrator before the controls start. Whatever n_conf is, all tests run and the report states the achieved MDE and the power at the MEI.
- **Pilot firewall.** The pilot analysis script (hashed before the pilot is generated) writes only: costs, memory, telemetry, per-arm completion counts, noun and discordant counts, failure and degeneracy counts, and the SD of the paired per-prefix difference L_p(G) - L_p(P64) and the eligible-prefix share per arm (v0.2). It computes no Lambda_b or Lambda_d, no arm mean of any link, no contrast, and no CLIP lift. No pilot sample enters any test. Allowed pilot-based changes: n_conf, chunk length, batch size (1), hook feasibility. Not allowed: arms, steps, CFG values, MEI, endpoint, thresholds, pools.

## 8. Runs in order of information per GPU-hour, GPU regime, budget

**Order.**
0. CPU: analytic check (section 7 table); unit tests of the new statistic on synthetic samples with injected link 0, 0.1, 0.3 (recovered within the interval; invariance under swapping the two seeds; discordance, ratio estimator, zero-denominator redraw, noun key); disjointness check of pools; manifest with SHA-256 of every reused EXP-001 file (re-hashed from `runs/EXP-001/gates/manifest.json`) and of the new files.
1. **Cost pilot (E3-PILOT, 16 prefixes x 2 seeds)**: arms P64, P32, O0, G; G at 50 steps on the first 8 prefixes (one seed) for the degeneracy comparison only; Ind and TF on 4 prefixes (smoke); determinism rerun of 4 units; hook checks; analysis script run end-to-end on the pilot outputs with arm labels scrambled and hashed (the freeze of EXP-001 9 item 11).
2. **Controls (E3-CTRL)**: Ind, TF (generation); scoring; PC-2 scoring. Decision: 9.4.
3. **Main stage M1**: P64 and G on all n_conf prefixes, interleaved by prefix (each unit is prefix x seed x arm, ordered so that a truncation leaves complete prefixes). **M2**: O0. **M3**: P32. Then scoring (CLIP, CLIP-IQA, VLM) once, in the eval venv, offline, after generation; the analysis script and its hash are frozen before the first main sample is scored. **M4 (optional)**: G-low on the first 64 prefixes; +0.28 compute-hours (+0.6 wall-clock), outside the 6-hour core path; runs only with the orchestrator's yes.

**Cost model [A, replaced by pilot values].** Per prefix (2 seeds): generation 2 x (6.4 + 3.2 + 3.4 + 6.8) = 39.6 s; scoring (VLM at 0.08 s per call [A: EXP-001 rung-2 evaluation, 1,710 calls in 167 s including load]; 3 calls per noun for P64, O0 and G, 2 for P32; about 6 nouns per sample) 10.6 s; total 50.2 s. Compute-hours: main at n = 150, 2.09; pilot 0.27; controls 0.32; model loads (about 20 chunks at 25 s) 0.14; **total 2.8 compute-hours**. Wall-clock = compute / duty 0.5 + 20 chunk pauses x 0.5 min = **about 5.8 hours** (the 6-hour budget read as wall-clock at duty 0.5, the convention of EXP-001 12.1; read as compute-hours the card has headroom of about 3 hours, which would pay for G-low and for n = 213).

**GPU regime (EXP-001 12.2, applied unchanged).** Every GPU stage, including scoring, runs as `python tools/gpu_guard.py --log runs/EXP-003/<stage>/telemetry-<stage>-<chunk>.csv --max-temp 85 --max-minutes 15 -- python <stage script> --resume`; the first chunk of each new stage at `--max-minutes 5` with the engineer watching. Duty cycle about 50 percent: after each unit the driver idles for as long as the unit ran (`Duty`), and starts a chunk only when the GPU is below 65 C, no other compute process is on it, and free system commit exceeds the gate (EXP-001 3 item 5c); pause between chunks 30 s plus that wait. After an exit 90 the next chunks use `--max-minutes 10` and the idle doubles; three exit-90 stops stop the stage. **Batch size 1** (no batching speed-up; the cap is 4). Outputs written atomically per (arm, prefix, seed); the `.json` is the done marker; a restart skips finished units. **Eval-mode assertion before every forward**: `assert_eval()` in the plain path (exists) and, for the official sampler, a forward pre-hook on the backbone that calls `assert_eval()` so that every forward inside `_sample` is checked, plus the assertions before and after `_sample`; a train-mode forward aborts the unit and is logged. Telemetry summary and the wall-to-compute ratio are written per stage. New code lives in `exp003/` and `analysis/EXP-003/` only; files hashed in the EXP-001 manifest are not edited.

## 9. Stop rules and falsifiers of the plan

1. **Budget.** If the pilot projects more than 6.0 wall-clock hours at n = 120, the orchestrator decides before the controls start. If cumulative GPU wall-clock reaches 6.0 hours before P64 and G are complete at n >= 120, stop and report the arm-level n reached (inconclusive by budget); hard stop at 7.0 hours.
2. **G degenerate at 32 steps.** After the pilot, before the controls: if at least half of G's 32 pilot samples have an empty completion or a pad-only tail, or at least 8 of 32 G images are near-uniform, while G at 50 steps on the 8-prefix check has at most 1 of 8 such samples, stop and tell the orchestrator; the fix is a new card version (50 steps against P at 100 passes), not a silent change. If both are degenerate, the finding is the report.
3. **Instrument cannot reach a decision (v0.2, statistician 5).** If the achieved MDE at 80 percent power at n_cap exceeds 0.15 on the pilot's upper SD (sigma_d,up above about 0.66), stop and tell the orchestrator before the controls. For an MDE between 0.10 and 0.15 the main stage runs and "inconclusive" is the expected outcome for a true effect near 0.10; the report says so.
4. **Controls.** NC-1 fails: stop; the pipeline or the wrapper is biased; fix under a new version before the main stage. PC-1 or PC-2 fails: the orchestrator decides; the main stage may still run to look for a positive, but every "null" label becomes "not measurable with this instrument" (W2).
5. **Thermal and crashes.** Three exit-90 stops in a stage stop it. A crash or reboot is logged to the failures ledger by the orchestrator, and the stage resumes from the manifest.
6. **Determinism.** The plain arms must be token-identical on 4 of 4 rerun units (EXP-001 reached 27 of 27). The official arms' rate is reported (global RNG and bf16 may differ); below 3 of 4 the cause is investigated before the main stage.
7. No generation is tuned, filtered or discarded because of its look or its score. Test-set (main-pool) results never choose a hyperparameter, a threshold or wording.

## 10. What Paper 1 states under each outcome

Statements are restricted to the scope sentence of 1.1.

| Outcome | Paper 1 states |
|---|---|
| Positive Delta1 (W1, NC-2 and guardrails pass), Delta2a positive | "Under the 32-step variant of the official guided sampler UniDisc 1.4B shows a seed-specific noun-level dependence between completion and image (a completion's discordant nouns are found more often in its own image than in its sibling's), larger than plain sampling at the same number of network calls (d, interval), which may include quality-mediated class-level coupling (quality-matched sensitivity reported); Lambda_b(P64) is (its interval). G minus O0 is positive (d, interval)." The three terms of the identity of 4.2 are reported, including P32 - P64; no share-of-effect statement (statistician 3). The census point stands: a joint-consistency number reported without its value rule is not attributable. |
| Positive Delta1, Delta2a not detected, Delta2b positive | "O0 minus P32 is positive (d, interval): the official sampler's bundle of selection, pooled ordering and schedule raises the link; a guidance effect is not detected (Delta2a interval)." "Not from guidance" only if Delta2a is in the null class. O0 minus P32 bundles position rule and schedule, which are not value rules, so this row makes no value-rule claim (red-team F-4). |
| Positive Delta1, neither Delta2 positive | "A bundle effect, not attributable at the precision achieved" with the three intervals. |
| Null Delta1 (controls passed) | "G does not differ from P64 by more than 0.10 on the seed-balanced link." **Only if, in addition, the 90 percent intervals of Lambda_b(G) and of Lambda_b(P64) each lie inside (-0.10, +0.10), NC-2 passed on G, and G's image seed diversity is above its floor (G's mean sibling image CLIP cosine below 0.92 and G's sibling noun-key Jaccard below 0.80; [A] feasibility thresholds; red-team F-2, F-7):** "Neither the guided nor the plain sampler shows a seed-specific noun-level dependence larger than 0.10 among nouns that one seed names and the other does not." (v0.3, red-team R3: no clause about what carries consistency; the prefix-driven gap of 4.3 item 3 is reported descriptively beside it.) Every null statement carries the per-arm discordant-noun and eligible-prefix counts (W5). Followed by the diversity numbers of E3-H4. |
| Null Delta1, an instrument control failed | "Not measurable with this instrument": the number of discordant nouns, the controls, and no statement about co-generation. |
| Reversed Delta1 | "Guidance reduces the completion-specific link on this model", with the candidate reasons the data allow (diversity, prefix over-conditioning), not asserted. |
| Inconclusive | The interval, the achieved MDE, and no claim. |
| E3-H4 supported | "The guided rule lowers diversity (sibling Jaccard, unigram entropy, image sibling cosine, with intervals) at the consistency it buys." Not supported: "no diversity cost measured at this precision". |
| P32 replicates the EXP-001 null (Lambda_b(P32) interval contains 0 and the OR-rule m - s_sp interval contains 0) | One sentence: the EXP-001 gate result holds on fresh prefixes at n = 150 clusters. |

Because UniDisc states no licence (EXP-001 3 item 6, 15.1), any figure with generated images waits for the authors' permission; metrics are reported without it.

## 11. Deliverables, freeze, sign-off, open items

- **Deliverables.** `runs/EXP-003/` (pools.json, manifest.json, per-stage outputs and telemetry, presence matrices as JSONL, verdict files for the pilot, controls and main), `analysis/EXP-003/` (statistic, nounkey, noun list, bootstrap, pilot script, frozen-analysis driver), `exp003/` (official joint runner with the pre-hook, prefix-only wrapper, drivers), a run report with every number traced to `runs/EXP-003/`.
- **Freeze.** The card is frozen when the statistician and the red-team sign and the novelty precondition is met. Afterwards changes are a new version with a change log. Frozen before the pilot: this card, `nounkey.py`, `coco_object_nouns.txt`, the pilot script, the derangement seed 5301, the pool permutation seed 1303. Frozen before the main stage: the full analysis script with its hash, and the pilot's n_conf.
- **Sign-off.** Statistician: _unsigned (v0.2 check pending)_. Red-team: _unsigned (v0.2 check pending)_. Novelty-auditor verdict: _deferred to after the 2026-10-19 budget reset; run before any claim is written, not before the run (orchestrator decision; the card makes no novelty claim)_.
- **Open items for the reviewers.** (1) Whether the null class should use the 90 percent or the 95 percent interval. (2) Whether sigma_d 0.45 is adequate; the pilot supplies a 16-cluster estimate with wide uncertainty and the n rule caps n at 150 regardless. (3) Whether PC-1, which runs on plain-sampling images, is a sufficient positive control for a statistic read on guided images, given PC-2 covers only the checker. (4) The G-low dose point is outside the core path. (5) The ledger rows (hypotheses E3-H1 to E3-H4) are to be added by the orchestrator.

## 12. Change log
v0.1 (2026-10-15): first draft after D0016.
v0.3 (2026-10-15, orchestrator, applying the red-team's v0.2 check R1-R4): guidance assertion moved to the first step with t < 1 and G's call count corrected to 64 (R1); NC-2 scope stated, W0 bans "completion-specific link" and words a positive as a seed-specific noun-level dependence that may include quality-mediated coupling, plus a quality-matched sensitivity (R2); the null sentence limited to what is tested (R3); the PC-1/PC-2 mismatch recorded as a W2 limitation (R4); header metric renamed.
v0.2 (2026-10-15, orchestrator, applying `review-statistician-EXP-003.md` 1-8 and `review-red-team-EXP-003.md` F-1 to F-8): primary statistic changed to the seed-balanced link Lambda_b, which cancels additive image-level yes-bias (F-1), plus placebo-noun control NC-2 on G and P64 with Delta1 also reported net of placebo; null wording conditioned on per-arm intervals, NC-2 and an image seed-diversity floor (F-2, F-7, S1); hypotheses tested against 0 with the MEI as descriptor (S2); W4 maps every sentence to a tested statement and W5 scopes nulls (S3, S4, F-6); the null class needs percentile and BCa agreement, Delta2 nulls unadjusted (S6); NC-1 half-width rule (S7); stop rule 9.3 tightened to an MDE of 0.15 and power stated conditional on sigma_d (S5); per-arm intervals reported (S8); mechanism corrected to prefix-removal guidance with a run-time guidance assertion (F-3); Delta2b rows make no value-rule claim and the commit order is a required output (F-4); the configuration is named a 32-step variant (F-8). F-9 to F-12 (minor) are covered by S5, the existing measurement details, the precision table and the licence sentence.
