```yaml
agent: experiment-designer
date: 2026-10-14
brief: Preregistration card EXP-001 v0.2, cross-modal dependence during sampling in UniDisc (P5a, P5b of framework-v2 section C; validity hypothesis H-C). Revision of v0.1 for the statistician's 12 required changes, the setup facts of runs/env-2026-10-14, and a core path of at most about 25 GPU-hours.
card:
  id: EXP-001
  version: v0.2
  status: draft, unsigned
  signatures: {statistician: none, red-team: none}
  frozen: false          # frozen when both sign; afterwards changes only as a new version with a change log
  supersedes: v0.1 (same path, overwritten in place; v0.1 text is in git history)
  hypothesis_ledger_ids: to be assigned when the rows are added (H-A, H-B, H-C); no ledger rows written by this draft
sources_examined:
  - research/CONTRACT.md
  - research/review/framework-v2.md (A, B, C, D, E)
  - research/review/dossier/primer-multimodal.md (0, 1, 2.2, 2.4, 4, 5/Q5)
  - research/review/audits/2026-10-14-red-team-selection-term.md (M10, lines 347-371)
  - analysis/framework/check_crossmodal_mixture.py and .log
  - research/review/method/selection-term.md (T6, T9)
  - research/preregistration/review-statistician-2026-10-14.md (EXP-001 part: findings S1-S8, R1-R12, O1-O8, power notes)
  - runs/env-2026-10-14/setup.md (all) and timing.json (UniDisc stage_c, via setup.md section 2.1)
  - web (v0.1): github.com/linzhiqiu/t2v_metrics (E1), github.com/alexanderswerdlow/unidisc (E1); cocodataset.org terms page did not render (not verified)
coverage: >
  Read in full: the files above at the sections named. NOT read: the UniDisc paper or code (the sampler, layout and
  precision facts below come from setup.md, which cites E3/E4 for them; I did not re-read the code); the
  statistician's EXP-002 part; MMaDA-Parallel code; any paper on dependence-aware parallel unmasking for
  single-modality DLMs (novelty not audited, see 1.3). Nothing in this card has been run.
claims:
  - statement: "No paper in the set measures a cross-modal quantity per step; the only joint-versus-sequential contrast (MMaDA-Parallel Table 10) is confounded."
    status: supported
    evidence: primer-multimodal.md sections 0 and 4 (rows B1-B3)
    level: E2
    confidence: 0.7
  - statement: "The mixture-reference estimator removes the marginal-inconsistency term on toy models (naive 0.08109 vs mixture 0 on red-team block J)."
    status: supported
    evidence: analysis/framework/check_crossmodal_mixture.log lines 1-3 (toy only)
    level: E4 (toy)
    confidence: 0.9
  - statement: "UniDisc interleaved has no time conditioning, a joint 48,385-token vocabulary, bidirectional attention within a document, and a pass costs 0.129 s at L=1536 (batch 1) and 0.606 s at L=5120."
    status: supported
    evidence: setup.md sections 2.1-2.2, timing.json stage_c
    level: E4
    confidence: 0.9
  - statement: "H-A: S_theta is front-loaded and concentrated on object nouns in UniDisc 1.4B."
    status: unknown
    evidence: none (prediction)
    level: E0
    confidence: 0.35
  - statement: "H-B: dependence-aware separation beats joint commitment at matched passes and matched per-window per-modality token budgets."
    status: unknown
    evidence: none (prediction)
    level: E0
    confidence: 0.3
competing_explanations:
  - within-modality total correlation traded for cross-modal (pure passes commit more same-modality tokens per pass)
  - off-support states (E_learn) in text-first and image-first arms
  - metric artifacts (caption shortening, image collapse, CLIP bag-of-words)
  - estimator artifacts (marginal inconsistency, finite-R bias, chunked-draw bias, bf16 quantisation, S bounded by entropy)
  - confidence-rule artifact (early commits are low-entropy, low-dependence tokens)
unknowns: [section 3 items still open: CLIP/tagger/VQA pins, COCO draw, resolution gate PG-1, empty-prompt gate PG-2]
next_test: {hypothesis: "H-A, H-B, H-C", intervention: "commit schedule (sets of modality-pure windows) at matched passes", primary_metric: "paired CLIP ViT-L/14 matched-minus-shuffled lift, DA minus J at k0", falsifier: "section 11", gpu_hours: "core path about 17 (t_b = 0.129 s) or 12 (t_b = 0.09 s) at 512 px; formula in section 12"}
```

# EXP-001 v0.2: cross-modal dependence during sampling in UniDisc (P5a, P5b, H-C)

Tags: [S] source fact, [I] inference, [H] hypothesis, [A] assumption until the pilot, [V] verified on a toy,
[C] computed by the statistician (analysis/stats/exp001_stats_check.log, as reported in the review), [E4] measured
in runs/env-2026-10-14. Nothing in this card has been run on the experiment. Every [A] number is replaced by a
pilot estimate before freezing, by the rule stated next to it.

## Change log v0.1 to v0.2 (read this first)

### A. Statistician's required changes (review-statistician-2026-10-14.md), all 12 applied

| Item | Applied where | How |
|---|---|---|
| R1 pilot firewall | 10.5 | Pilot script writes only SDs of influence values, SEs and correlations of contrasts, cost, floors, padding share, Lift(J) with SE; never the mean Lift of Alt, TF, IF, Ref-T2I or of any contrast; source hashed before D0 is generated. NC-5 on the pilot runs on J only |
| R2 sizing | 10.4 | sigma_d,up from the bootstrap SE of Alt - J at k0 on D0 (full Lift pipeline), chi-square upper 80 percent factor; n_conf = min(1000, max(500, n_req)); rho halving clause deleted; "only primary and H-B2 run" branch deleted; achieved MDE reported if n_req > 1000 |
| R3 gatekeeping | 10.2 | Fixed sequence: step 1 H-B1 at 0.05; step 2 Holm at 0.05 over six secondaries only if step 1 rejects, else exploratory with adjusted p; a test not run enters Holm with p = 1; DA - J at k- moved to H-B3 (estimation only). Option chosen: gatekeeping, not one Holm family |
| R4 classes and OC | 10.2 | "positive" = Holm-adjusted p <= 0.05 and d_hat > 0 (family members) with the label "at or above the MEI" when d_hat >= 1.0 (second option, as recommended); OC table [C] included |
| R5 p-values | 10.1 | Bootstrap p-value formula; rerun at B = 100,000 with fixed seed if within 2 sqrt(p(1-p)/B) of a threshold |
| R6 IUT for maxima | 2, 10.2, 11.3 | H-B2 = both one-sided 95 percent upper limits (TF - Alt, IF - Alt) below 1.0; stop rule 3 uses "TF - J and IF - J both null"; sentence on conjunctions added |
| R7 H-A rules | 2, 8.3, 10.3, 11.2 | D2 = 256 trajectories at k0, fixed, no extension; probe definition (windows 1-2 vs 7-8 centres, pass 1 separate); H-A decided at k0 only; entropy-normalised companion R_Q,d with the wording rule; H-A2 on all still-masked text positions at early centre probes, exclusion shares reported |
| R8 H-C stratified | 10.3, 10.4 | rho_strat = mean of within-k Spearman over windows, permutation within k, critical value 0.440; SE(Delta_w) from the pilot bootstrap; the 0.15 bound's requirement (rho_pair >= 0.65 at n = 500 or >= 0.30 at n = 1000) stated |
| R9 freeze before scoring | 9 item 11 | Analysis run end-to-end on scrambled D0 outputs, hashed, hash in manifest with D3 token hashes; D3 scored once |
| R10 PC-A units | 8.8 | Unpaired bootstrap, each cell resampled independently with its baseline recomputed |
| R11 error control | 10.2 | Per-claim error control stated; no Bonferroni across EXP-001 and EXP-002; every-level-halved sensitivity reported |
| R12 gate | 6 | Gate statistic pinned (point estimate of Lift(J), D0, k0); the fork changed (see B5); estimand named "DA - J at k0 under the condition the gate selects"; logged before D1; false-fail operating characteristic stated |

Recommended items: O2, O3, O4, O5, O6, O7, O8 adopted (7.2, 8.8, 10.2, 11.2, 10.1). **O1 not adopted**: R12's point-estimate
gate is kept. Reason: with the fork now leading to an alternative position rule (B5) rather than "untestable",
a false fail costs a different but valid condition, not the experiment, so the extra complexity of an 80 percent
bound buys little. The statistician may overrule.

### B. Setup facts and re-scoping (runs/env-2026-10-14/setup.md, timing.json)

1. **Geometry replaced.** v0.1 assumed L_T = 128, L_I = 256. Real: UniDisc's official layout is a fixed system
   prompt, the user prompt, then **32 masked text positions**, `</s>`, and the image (setup.md 2.2). I use L_T = 32
   masked text tokens after an empty user prompt. The checkpoint is run at **512 px (L_I = 1,024)** if a pre-pilot
   gate (PG-1) confirms the checkpoint works there; the official inference experiment is 1,024 px (L_I = 4,096), and 256 px
   is the fallback. The row is about 1,085 tokens at 512 px [A: 23 system tokens + about 30 template tokens + 32 + 1,024].
2. **Cost.** v0.1's core path (about 583k passes at 0.61 s each at 1,024 px) is about 100 GPU-hours. At 512 px
   one pass is about 0.129 s measured at L = 1,536 (about 0.09 s expected at 1,085 tokens), and passes per sample fall because
   the pass budget is now N = 32 (about 33 tokens per pass) instead of 48: core path about 416k passes, **about 17 GPU-hours
   at 0.129 s (12 at 0.09 s)**, 24 at the n = 1000 cap. **Batching does not help**: per-sample time is 0.129 s at batch 1
   and 0.146 s at batch 8 (L = 1,536), 0.606 s and 0.645 s (L = 5,120); batch 1 to 4 is used where convenient, no speed-up is assumed.
3. **Plan generator redesigned** (5.1). With 32 text and 1,024 image positions, "every arm commits exactly k tokens
   per pass" is impossible: a text-only pass can hold only the text of one window (4 tokens). The pass budget N, the
   per-window per-modality budgets (4 text, 128 image) and the position rules are matched; **tokens per pass are not matched in
   modality-pure windows**, which is intrinsic to "separating costs a pass". The grid is stated in N: k0 = N 32, k+ = N 16, k- = N 64
   (k labels kept from v0.1; k+ means more tokens per pass). New diagnostic arm Jd (5.1) isolates the image-density effect.
4. **Estimator cost and form** (8). A joint text set is now 1 token at k0, so T->I costs R passes. The joint image set has
   32 tokens, so an exact sequential draw for I->T would cost 32 R: **I->T uses a chunked joint draw (g = 4 chunks of 8)**,
   with chunk-size sensitivity as a gate (G5). Probes: D1 8 centre passes, D2 5 passes (pass 1 and the centres of windows 1, 2, 7, 8).
5. **Fork in the dynamic-range gate** (6). v0.1's fallback P' (nucleus 0.9) is replaced by **P_rand** (random positions
   within modality, values still sampled at temperature 1, V stays 0). Reason: deterministic confidence ranking without
   noise on 1,024 image tokens is a known risk for degenerate images (the official sampler adds Gumbel noise, r_temp 4.5; setup.md 2.5),
   and a position-rule fallback keeps the value rule plain.
6. **Negative control for H-B replaced.** v0.1's "k = 1, J versus Alt" identity is unaffordable (N = 1,056) and no longer
   an identity. New: **NC-6' modality-blind-model schedule null** (the effect must vanish by construction) plus a cheap
   bitwise identity I2 (Alt with empty text passes equals Jd, possible because the model has no time input).
7. All "to be filled from setup.md" items filled (section 3). Still open and procedural: the CLIP, tagger, VQA, KID and
   CLIP-IQA pins (not installed in the venv), the COCO draw, gates PG-1 and PG-2.
8. Noise floor: bf16 log-probabilities are returned in bf16 (row sums off by up to 2e-3; top-1 agreement with fp32 0.96-0.97; mean TV 0.006-0.016),
   so G1 gains a "no-information reveal" floor (G1b) and all marginals are renormalised in float64 (6).
9. Licence: UniDisc code and checkpoint carry **no licence**. Consequence stated in 3 item 6.

### C. What the re-scoping costs in power or scope
- Primary contrast: none. n_conf floor stays 500 (R2); at n = 500, sigma_L = 4, rho 0: P(significant) = 0.977 [C]. In the 1,024-px tier (only if PG-1 and the 256-px gate both fail) n_conf = 250 and power is 0.80 (computed here).
- H-A: D2 = 256 trajectories at k0 only (R7); 5 probes instead of 9; the committed text set is one token at k0, so the
  committed-set I->T statistic is noisy (the all-masked-position version is registered as companion). The I->T draw is chunked, not exact (bias direction unknown, gate G5).
- H-C: unchanged in design; its power is still likely low (10.4).
- Scope: 512 px (not the official 1,024), L_T = 32 (not 128), PC-B on 128 prompts (not 250), k = 1 identity dropped, conditional stages 4-7
  need the stop rules and an orchestrator's yes beyond the 25-hour core cap.

### D. Items that need the statistician again
(1) the chunked I->T joint draw, probe schedule and D1/D2 split (8.2-8.3); (2) the R12 fork P -> P_rand (6); (3) the new matching rule,
Jd and NC-6' (5, 8.8); (4) the H-C predictor M taken from D1 (10.3); (5) the pre-pilot gates PG-1, PG-2 (3, 10.5). R-items themselves
are applied as written, with numerics adapted to the new geometry (probe passes in 8.3).

## 0. Summary

One frozen checkpoint (UniDisc 1.4B interleaved, revision 2b344ca8, no training), unconditional joint generation of a
(32-token caption, 512-px image) pair, plain sampling at temperature 1 with no guidance as the primary value rule. Two
measurements. (1) The per-step trace of the model's own cross-modal dependence S_theta in both directions with the
mixture-reference estimator, with validity gates (H-A). (2) A family of commit schedules at matched forward passes and matched per-window
per-modality token budgets, differing in which windows commit text and image tokens in separate passes (H-B), scored by a matched-minus-shuffled
CLIP lift. Window-wise separation arms test whether S_theta predicts where separation helps (H-C). A positive, a null and a reversed
result are each reported.

## 1. Claim contract

### 1.1 Claim, one sentence
In an all-discrete unified model sampled with many tokens per pass, the model's own cross-modal dependence is concentrated
early in the trajectory and on object words, and commit schedules that do not co-commit the high-dependence text-image pairs
yield higher text-image consistency than joint commitment at the same number of forward passes.

### 1.2 Mechanism
A joint pass commits a text set a and an image set b from a product of predicted marginals. Its factorisation error contains a
cross-modal part (framework-v2 C: TC(a,b) = TC(a) + S_{T->I} + TC(b|a), S_{T->I} = sum_{j in b} I(a; b_j | s); symmetric S_{I->T}).
A schedule that commits a first and b in a later pass lets b see a. The toy [V] (primer section 4) shows the trade-off: at equal tokens per
pass, separating the modalities removes the cross term and pays within-modality total correlation, and can lose to an interleaved
schedule. Here the trade-off is sharper: separating costs a pass, so the image tokens of a pure window are committed in fewer,
larger groups. The card tests "separate the dependent pairs", not "separate the modalities", and the primary contrast J versus DA
measures the net of the cross-modal gain and the image-density cost; DA versus DA-low and the Jd diagnostic separate them.

"Joint commitment costs where cross-modal dependence is high" is close to an identity (primer section 0 item 5). The empirical
content tested here: (a) where in the trajectory and on which tokens the model's dependence sits (H-A); (b) whether any schedule
exploits it at matched passes (H-B); (c) whether the measured quantity predicts the gain from separation window by window (H-C).

### 1.3 Closest methods and the exact distinction
- MMaDA-Parallel Table 10 (fully parallel 71.0/63.2/59.8, semi-parallel 68.3/60.7/57.5, sequential 64.2/56.5/54.1) [S, primer]. Confounds:
  sequential text cannot see the image; training differs; passes not matched; one run; GPT-4.1 judge; no interval; its released sampler is not fully parallel (image
  commits from text_steps//4, E3). Distinction: one set of weights, bidirectional attention in every arm, every committed token visible to every later
  pass, matched passes and matched per-window budgets, paired seeds, intervals.
- UniDisc App. I, Fig. 24-25 [S, primer]: logit distance conditional-vs-unconditional shrinks with decoding; CFG only on steps 1-3 of 24 gives CLIP 0.301 against 0.283 on
  steps 22-24. Guidance drops a whole modality, so it measures the value of the other modality's information per step, not the cost of co-commitment, and it changes marginals.
  Distinction: no guidance in the primary condition; reproduced as a positive control (PC-B), not used as evidence. Note the guidance weight is cfg x (1 - t) in the code (setup.md 2.2), so it is step-dependent by construction.
- LaViDa-O layout-first (Tables 13, 16) [S, primer]: trained planner, extra passes, image-only baseline. Distinction: no training, matched passes, joint baseline.
- Framework-v2 estimator and the EB-sampler identity (2505.24857 Eq. 7) are the accounting; the reveal-and-requery estimator with a mixture reference has no published counterpart in the papers read [E1, "not found"].
- Dependence-aware parallel unmasking in single-modality DLMs: not audited. `novelty-auditor` must check it before any novelty wording in Paper 1. The review claims the measurement, not the idea.

### 1.4 Competing explanations (each has a control, section 9)
1. Within-modality cost: a pure text pass commits 4 text tokens where a joint pass commits 1 (at k0); the image passes of a pure window carry 42-43 tokens where joint passes carry 32. Control: DA-low, window arms, Jd, text perplexity and image-quality secondaries.
2. Off-support states (text-first, image-first). Control: window arms keep the per-modality masked fractions equal at every window boundary; TF and IF are not read as support for P5b.
3. Metric artifacts (short generic captions, collapsed images). Control: shuffled-partner baseline in the primary; guardrails.
4. Estimator artifacts: marginal inconsistency (0.081 nats per token at zero dependence in block J), finite-R bias (cap ln R), chunked-draw bias, bf16 quantisation, the bound S_j <= H(marginal_j). Controls: mixture reference, injection test, R and chunk sweeps, G1b floor, entropy-normalised statistics.
5. Position-rule artifact: confidence ranking commits low-entropy (often padding) tokens first. Control: condition R, all-masked-position S alongside committed-set S.
6. Placement: any separation helps equally. Control: DA versus DA-low.

## 2. Hypotheses (falsifiable; direction and minimum effect of interest)

Notation: k labels = pass budgets, k0 = N 32, k+ = N 16, k- = N 64 (total tokens per pass about 1056/N: 33, 66, 16.5). W = 8 equal windows of the
pass index. "Early" = windows 1-2, "late" = windows 7-8. Lift = the primary endpoint of section 7 (points, 100 x cosine). Hypotheses are two-sided in their tests so a reversed result is detected.

**H-A (P5a), measurement hypothesis.** Under plain sampling at temperature 1 from the all-mask state, on UniDisc 1.4B, **decided at k0 only (k+ is descriptive)**:
- H-A1 (early concentration): for each direction d in {T->I, I->T}, ratio_d = [mean over trajectories of S^d averaged over the centre probes of windows 1 and 2] / [same over windows 7 and 8]
  is at least 1.5 (minimum effect of interest; 1.0 is flat). Both directions must pass. S^d is the committed-set quantity of 8.1. Pass 1 is reported separately (its committed set is the same size here but the state is the all-mask start).
- H-A1-Q (entropy-normalised companion, registered now): R_Q,d = [mean over trajectories of sum_{j in committed set} I_hat_j / sum_j H(mbar_j), early probes] / [same, late probes].
  Wording rule: a raw H-A1 lower limit >= 1.5 supports "cross-modal dependence in nats is front-loaded". The claim "front-loaded beyond the entropy available" needs the R_Q,d lower limit >= 1.0 in both directions as well. Otherwise Paper 1 says the trace follows the entropy profile.
- H-A2 (object words): in the I->T direction, on all still-masked text positions at the early centre probes (windows 1 and 2), the pooled ratio of means
  [sum of Q over object-noun positions / their count] / [sum of Q over function-word positions / their count] is at least 1.5; Q is the information fraction of 8.5. Bootstrap over trajectories. The share of positions excluded by H(mbar) < 0.05 nats is reported by type.
- Operationalisation of "layout and object tokens": objects = word-initial subtokens whose word is tagged NOUN or PROPN by the pinned tagger on the final caption; function words = DET, ADP, AUX, PRON, CCONJ, SCONJ, PART, PUNCT; "layout" = a fixed list of spatial-relation words (left, right,
  above, below, behind, in front of, next to, top, bottom, center, middle, background, foreground; frozen in the repository before the pilot), exploratory because of few occurrences. Positions after the first `</s>` or equal to pad (id 0) are excluded from types. Image-side "salient regions" are dropped from the confirmatory claim (no validated segmenter on 1.4B-model images); an exploratory map is allowed (8.6).

**H-B (P5b), schedule hypothesis.** At matched forward passes N and matched per-window per-modality token budgets (5), on the condition the gate of section 6 selects:
- H-B1 (primary): Lift(DA) - Lift(J) > 0 at k0, reported "at or above the MEI" if the estimate is >= 1.0 point. DA separates the four windows with the highest profiled S_theta; J is joint in every window.
- H-B1' (placement): Lift(DA) - Lift(DA-low) > 0 at k0.
- H-B2 (sequential need not beat alternating): both TF - Alt and IF - Alt have one-sided 95 percent upper limits below 1.0 point at k0 (non-superiority; intersection-union).
- H-B3 (dose, estimation only): the gain DA - J does not increase as k decreases (k+ >= k0 >= k-). DA - J at k- is estimated, not tested.
The minimum effect of interest of 1.0 point equals the scale of the differences UniDisc's authors report between CFG-window conditions (0.301 vs 0.293 vs 0.283 on a 0-1 cosine scale, i.e. 0.8 to 1.8 points) [S, primer C3]; it is a documented scale, not a tuned one.

**H-C (validity).** Let Delta_{w,k} = Lift(Sep_w) - Lift(J) at budget k, Sep_w separating only window w. Let M_{w,k} = P_w x S_sym(centre of window w) measured on the **profile set D1**, S_sym = (S^{T->I} + S^{I->T})/2 committed-set values, P_w = passes in the window. Then
rho_strat = mean over k in {k0, k+} of the within-k Spearman correlation of (M_{w,k}, Delta_{w,k}) over w = 1..8 is at least 0.5 (one-sided permutation p <= 0.05, permuting windows within each k). Otherwise S_theta is a descriptive trace only and Paper 1 says so.
H-C is conditional on H-B showing a nonzero Delta somewhere and on a variance check (stop rule 4).

## 3. Setup facts (filled from runs/env-2026-10-14/setup.md) and what is still open

| # | Item | Value | Source |
|---|---|---|---|
| 1 | Geometry | Layout: fixed system prompt (23 tokens), `<s>` empty user prompt, **L_T = 32 masked text tokens**, `</s>`, `<s>`, space, `<image>` marker, image tokens in raster order, `</s>`; images placed last; one document, full bidirectional attention. L_I = (res/16)^2: 256 px 256, **512 px 1,024**, 768 px 2,304, 1,024 px 4,096. Official inference experiment: 1,024 px. Row at 512 px about 1,085 tokens [A]. Text vocabulary 32,001 (Llama-2 SentencePiece, mask id 32000, pad = id 0 `<unk>`, EOS = id 2), image codes 16,384 (ids from 32,001), joint vocabulary 48,385 | setup.md 2.2, E3/E4 |
| 1b | Padding | the 32-token tail is fixed length followed by `</s>`; whether the model fills it with EOS/pad early is unknown until the pilot (pad share measured, reported). Positions after the first `</s>` or pad are "post-caption" and enter NC-4 | setup.md 2.2; pilot |
| 2 | Time input | none (`force_null_sigma: true`); the same masked state gives the same marginals in every arm, and a pass that commits nothing is a no-op | setup.md 2.1 |
| 3 | Official sampler | `maskgit`: one pass per step over all positions pooled, a token per position by `torch.multinomial` at temperature 1 (no top-p, no temperature in this sampler), score log p(sampled) + r_temp x Gumbel x t with r_temp 4.5, commit the top `schedule[step]` by an arccos schedule, ties can commit more than k; default 50 steps, CFG 3.0 with weight cfg x (1 - t) needing a second network pass; final `noise_removal` argmax pass. No custom order in the official code: use `ordered_commit` (tested, committed sets equal prescribed sets) | setup.md 2.4-2.5 |
| 4 | Modality-blind forward | feasible: put the mask id at all positions of the other modality (image: all L_I; text: the L_T tail), template tokens stay; marginals at masked positions are renormalised inside their own modality slice by the model's output head | setup.md 2.2-2.3 |
| 5 | Timings (bf16 weights, SDPA attention, E4) | L = 1,536: batch 1 0.129 s (3.1 GB), batch 4 0.589 s, batch 8 1.167 s (5.2 GB); CFG batch 8 2.575 s (7.6 GB). L = 5,120: batch 1 0.606 s, batch 8 5.164 s (10.8 GB); CFG batch 8 OOM. **No batching speed-up.** Weights 2.82 GB; peak memory is dominated by full-vocabulary logits (B x L x 48,385). Planning value t_b = 0.129 s (upper) and 0.09 s (expected at 1,085 tokens) | setup.md 2.1, timing.json |
| 5b | Precision | bf16 weights are the experiment's precision in every arm (the checkpoint is fp32); bf16 vs fp32 weights under autocast: top-1 agreement 0.962-0.972, mean TV 0.0055-0.0164, mean entropy difference 0.059-0.125 nats; returned log-probabilities are bf16 (row sums 0.9977-1.0009). fp32 weights cost 6.3 GB VRAM and have no timing yet | setup.md 2.1 |
| 5c | Machine reliability | system commit nearly exhausted by other processes; CUDA allocation is charged to it; OOM with free VRAM is a commit failure. Runs gate on free commit, write results per seed and resume. Recommended before long runs: reboot or close the stale processes and re-time (OOM boundaries may move) | setup.md 0 |
| 6 | Licence | **UniDisc code (commit 3ee3e47a, main) and checkpoint (aswerdlow/unidisc_interleaved, revision 2b344ca8) state no licence.** Consequence: use is private research; the card does not release weights, code wrappers of the model, or generated images; Paper 1 may report metrics and, for figures with generated images, needs the authors' written permission first (to be asked by the orchestrator, not by this card) | setup.md 1 |
| 7 | Pins | torch 2.11.0+cu130, transformers 4.49.0, torchmetrics 1.9.0, numpy 2.5.2, Python 3.12.14 (`env-lock.txt`); Llama-2 tokenizer mirror rev 8efe6c9b; GPT-2 large rev 32b71b12 (MIT); UniDisc commit and weights as above. **Not yet installed, to be pinned by hash before the pilot (procedural, allowed as a pre-freeze amendment):** CLIP ViT-L/14 (candidate `openai/clip-vit-large-patch14` [E0]), the POS tagger, the VQA-family model (t2v_metrics lists CLIP-FlanT5 as legacy v3.0 [E1]), the KID/Inception weights and CLIP-IQA implementation (torchmetrics classes are candidates [E0, verify]) | setup.md 1 |
| 8 | COCO val2017 draw | 500 items for references (seed 777, sorted by image id), plus 32 disjoint items for PG-1 and 128 for PC-B; file hash recorded when downloaded. Licence: annotations CC BY 4.0 and images under Flickr terms [E0, the terms page did not render; engineer confirms] | open |

## 4. Task, data, seeds

- **G0 (primary): unconditional joint generation.** Start: the official layout with an empty user prompt, all 32 tail text positions and all L_I image positions masked. Output: one caption (tokens before the first `</s>` or pad, special tokens stripped, detokenised with the pinned Llama-2 tokenizer) and one image (VQ-16 decode). Only here are both modalities committed under a free schedule. T2I with a clean caption has no text set to co-commit; likewise I2T.
- **Pre-pilot gate PG-2 (empty prompt).** On 16 seeds outside all pools with the official sampler, the empty-prompt layout must give captions with at least 4 non-special tokens before `</s>` in at least 12 of 16 samples and non-degenerate images (engineer's visual log, not a statistic). If it fails, a fixed neutral prefix "a photo of" (the same for every seed and arm) is observed before the 32 masked tail tokens, logged before D0 is generated. This is a feasibility gate that uses no arm contrast.
- **Pre-pilot gate PG-1 (resolution).** Official sampler (50 steps, CFG 3.0), T2I with 32 COCO captions disjoint from the references, at 512 px and (first 16) 1,024 px. Pass if mean raw matched CLIP score (100 x cosine) at 512 px >= the 1,024-px mean minus 2.0 points and the 512-px matched-minus-shuffled lift >= 0.8 x the 1,024-px lift. If it fails, repeat at 256 px against the same 1,024-px values. If both fail, the 1,024-px tier below applies. Cost about 0.4 h. Thresholds are feasibility choices, not hypothesis tests.
  - Tier costs (same plan, other resolutions): 256 px: c_I = 32, t_b about 0.04 s [A, cost model 0.12 s per 1,000 tokens], core path about 5 GPU-hours. 1,024 px: c_I = 512, t_b = 0.606 s; only a reduced design fits about 25 hours (n_conf = 250, D1 64 trajectories, D2 128, k0 arms only, no J-global/Jd, no NC-6', PC-B dropped, power 0.80 for the primary); the orchestrator decides.
- **Unit of analysis**: the seed index i. All arms use the same i. There is no text prompt in G0.
- **References on a public prompt set (not in any hypothesis test).** COCO val2017 captions: Ref-real (500 real pairs through the metric), Ref-T2I (clean caption, image decoded in the 24 image-pass structure of Alt at k0), Ref-I2T (clean image, caption in 8 text-only passes). Same value rule, same metric. COCO is used for evaluation only and not redistributed.
- **Not covered**: multi-segment interleaved generation, text lengths other than 32 tail tokens, resolutions other than the one PG-1 selects.
- **Seed pools (disjoint; counter-based generator keyed by pool and i)**: PG [90000, 90048); D0 pilot [0, 64); D1 profile [10000, 10128), with the first 64 reused for k+; **D2 H-A confirmation [20000, 20256)** at k0; D3 arms [30000, 31000), the first n_conf used; D4 secondary conditions [40000, 40250); D5 blind-model null [50000, 50128).
- **Common random numbers**: sample i draws a float64 uniform u_j for every position j once; a position's value is the inverse-CDF draw from its float64 marginal at the pass in which it is committed, in every arm. Probes use a separate stream and never touch the sampler stream.

## 5. Arms and schedules

### 5.1 Geometry and the plan generator
L_gen = L_T + L_I (1,056 at 512 px). N passes; W = 8 windows; c_T = L_T / W = 4 text and c_I = L_I / W = 128 image tokens per window (at 512 px); P_w = N / W passes per window. Requirements: W divides N and P_w >= 2. Grid: **k0: N = 32 (P_w = 4), k+: N = 16 (P_w = 2), k-: N = 64 (P_w = 8)**. At 256 px the same N grid is used with c_I = 32.

Within a modality the committed positions are the top-count masked positions by maximum marginal probability (ties: lowest position index); condition R and the P_rand fallback use uniformly random positions; values are drawn from the unmodified marginals (section 6). Every arm uses the same weights, attention (full bidirectional), position embeddings, and every committed token is visible to every later pass.

Window rules (pass q = 1..P_w inside window w; floor rule f(q, c, m) = floor(q c / m) - floor((q-1) c / m)):
- **Joint window**: text count f(q, c_T, P_w), image count f(q, c_I, P_w) (at k0: 1 text and 32 image per pass). Per-window totals exactly (c_T, c_I).
- **Pure window**: pass 1 of the window is a text-only pass committing all c_T text tokens; passes 2..P_w are image-only with counts f(q-1, c_I, P_w - 1) (at k0: 42, 43, 43 image tokens; at k+: one pass of 128; at k-: seven passes of about 18). Per-window totals exactly (c_T, c_I). Text goes first inside a pure window, which removes the S_{T->I} split; the image-first variant is exploratory.
A schedule is a set M of pure windows; the other windows are joint.

| Arm | Definition | Role |
|---|---|---|
| J | M = {} | primary comparator |
| Alt | M = {1..8} (8 text-only passes, one per window) | modality-pure everywhere |
| DA | M = the 4 windows with the largest profiled S_sym on D1, fixed before any D3 run | dependence-aware schedule, zero extra passes at test time |
| DA-low | M = the 4 windows with the smallest profiled S_sym | placement control (same number of text-only passes) |
| Sep_w, w = 1..8 | M = {w} | H-C window arms |
| TF | passes 1..8 text-only (4 tokens each), then N - 8 image-only passes (floor rule) | modality-sequential; off-support |
| IF | N - 8 image-only passes, then 8 text-only passes | modality-sequential; off-support |
| J-global | no plan: pooled top-count by max probability over both modalities, total tokens per pass f(q, L_gen, N) | descriptive; shows what confidence does across modalities |
| Jd | diagnostic, not pass-matched: Alt's image pass structure (N - 8 image passes) with the 32 text tokens co-committed by the floor rule over those passes | isolates image-density from separation: Alt - Jd has equal image density, Jd - J has equal co-commitment |
| O | the official sampler with its defaults (maskgit, 50 steps, CFG 3.0, r_temp 4.5, final noise removal) | reference only, condition G |

The "dependence-aware" claim is tested at phase level (which windows to separate), not pair by pair; an instance-level controller costs extra passes that would have to be charged and is future work. M for DA comes from the D1 profile only and is saved to `runs/EXP-001/da_windows.json` with a hash before D3 starts. The same window set (in normalised time) is used at k+ and k-.

TF and IF are not window-matched (their per-modality budgets match J only at the end). They enter H-B2 and as references; a loss of TF or IF against J is not read as support for P5b (explanation 2).

### 5.2 Matching rules and why
- Matched forward passes N in every arm except Jd (reported with its N - 8) and O (50 steps, guided passes count 2).
- Matched per-window per-modality commit budgets (window arms): masked fractions per modality agree at every window boundary, so states stay near the training support.
- **Tokens per pass are not matched** in modality-pure windows (text pass 4 tokens, image passes 42-43 against 1 and 32 in joint passes). This replaces v0.1's "k per pass in every arm" and is why DA-low and Jd exist.
- No time input exists (setup item 2), so no time-matching rule is needed.
- The MMaDA-Parallel lesson: no arm uses a differently trained model or an attention mask that blocks anything; "text first" means the image positions stay masked while text is committed, then the finished text is visible to the image passes.

## 6. Value rule (fixed across arms)

- **Primary condition P**: plain sampling at temperature 1 from the unmodified marginals, no top-p, no top-k, no guidance, position rule = within-modality confidence ranking (a deterministic function of the state). Reason: with a state-only position rule and values drawn from the product of marginals, the value slot V of framework-v2 B is 0 and G = 0, so arm differences are differences in schedule, not value rule. The official sample-then-filter would put a non-product value law at k >= 2 into every arm differently.
- **Float precision and renormalisation**: model log-probabilities (bf16) are exponentiated and renormalised inside the modality slice in float64; all categorical draws and every KL use float64; inverse-CDF with float64 cumulative sums.
- **Secondary condition G (official guided setting)**: arms J, Alt, DA, DA-low, TF, IF with their plans, values sampled at temperature 1 from guided marginals (CFG 3.0, weight cfg x (1 - t), a guided pass counts 2), through `ordered_commit(guided=True)`; plus O. Labelled mixed effects (guidance changes cross-modal conditioning).
- **Robustness condition R**: condition P with uniformly random positions within modality, for the trace (64 trajectories) and arms J, Alt, DA (n = 250).
- **Dynamic-range gate and one pre-registered fork (R12)**: Gate statistic = the point estimate of Lift(J) on D0 at k0 with the full pipeline. If it is below 2.0 points, **J (only) is regenerated on D0 under P_rand** (random positions, otherwise P) and the same statistic is recomputed. If P_rand passes, the primary estimand becomes "DA - J at k0 under P_rand" and D1, D2, D3 run under P_rand; if both fail, H-B is declared untestable on this checkpoint and only H-A (descriptive) proceeds under P. The choice is logged before D1 starts. The primary estimand is therefore always "DA - J at k0 under the condition the gate selects". Operating characteristic [A]: SE of the gate statistic is about 0.5-0.7 points at n = 64, so a true Lift(J) of 2.5 fails about 20 percent of the time; a false fail changes the condition, it does not end the experiment.

## 7. Endpoints

### 7.1 Primary (one): matched-minus-shuffled CLIP lift
Model: CLIP ViT-L/14 (candidate `openai/clip-vit-large-patch14` [E0]; revision hash and file SHA recorded in setup before the pilot), text truncated at 77 tokens (captions are at most 32 Llama tokens, so truncation is expected to be rare and its rate is reported), the checkpoint's own image preprocessing. For a cell (arm, k) with n samples, e_I(x_i), e_T(c_i) are L2-normalised embeddings,
C_i = cos(e_I(x_i), e_T(c_i)), B_i = 0.5 x [mean_{j != i} cos(e_I(x_j), e_T(c_i)) + mean_{j != i} cos(e_I(x_i), e_T(c_j))], **Lift_i = 100 (C_i - B_i)**.
The endpoint of an arm is mean_i Lift_i; a contrast is the paired mean difference over seeds. The shuffled baseline is computed inside the arm's own samples (removes caption-only and image-only offsets, penalises collapse). No sample is excluded; empty or degenerate captions are scored as they are and counted in the guardrails.
The per-seed influence value of the mean Lift is psi_i = 100 (C_i - 2 B_i) (Hajek projection; statistician S1); sizing uses it through the bootstrap SE (10.4).
Rationale for CLIP over VQA-type scores as the primary: full n x n similarity matrices make the baseline and the bootstrap recomputation cheap.

### 7.2 Secondary (descriptive, intervals, uncorrected, flagged as such)
- Raw matched score 100 C_i; the primary contrast also expressed as a share of the gap Lift(Ref-real) - Lift(J) (O2).
- VQA-family consistency on a fixed random 250-seed subset, **the same 250 seed indices in every arm** (O7), matched pairs only; model pinned at setup time. TIFA excluded.
- Image quality: KID (Inception features, subsets) against 5,000 COCO val2017 images; FID not used (n = 500 is below the feature dimension). CLIP-IQA per image.
- Text quality: GPT-2 large perplexity of caption content tokens (rev 32b71b12); non-special caption length; distinct-1 and unigram entropy across a cell's captions.
- Diversity: mean pairwise cosine of image embeddings in a cell.
- Expected regressions (stated now): text perplexity higher in Alt, DA, DA-low (4 text tokens per text pass against 1 in joint passes); KID higher in TF and IF (off-support) and possibly in Alt (denser image passes).
- **Guardrails for a positive H-B1 (defined on point estimates, O3, O4)**: (i) DA's mean caption length within [0.8, 1.25] of J's; (ii) mean pairwise image-embedding cosine within 0.05 of J's; (iii) empty-caption rate not higher by more than 2 percentage points; (iv) rate of captions truncated at 77 CLIP tokens within 5 percentage points of J's; (v) mean CLIP-IQA not lower than J's by more than 0.2 x the SD of per-image CLIP-IQA in J; (vi) KID not higher than J's by more than 1 SD of the KID subset estimates of J (the KID protocol's own subsets). A positive with a failed guardrail is reported as "positive with regression" and is not used as support without that qualifier.

### 7.3 Measurement endpoint for H-A
The per-probe S_theta traces of section 8, both directions, committed-set and all-masked-position versions, and the information fraction Q.

## 8. Estimator protocol for S_theta

### 8.1 Definition
At a probed pass n of a J-arm trajectory with state s, the committed sets are the plan's sets: text set A^T (1 token at k0, 2 at k+) and image set A^I (32 at k0, 64 at k+), chosen by the position rule as a function of s alone. For every still-masked image position j (set J_I), the model's dependence is
I_theta(a; b_j | s) = E_a KL(p(b_j | s, a) || mbar_j), mbar_j = E_a p(b_j | s, a), with a drawn from the model's own joint over A^T. This is the named split "text-first S_theta" (framework-v2 C). Committed-set quantity S^{T->I}_n = sum_{j in A^I} I_theta(a; b_j | s); the all-masked-position version sums over J_I. S^{I->T} is symmetric (b drawn jointly, text marginals requeried; committed-set sum over A^T, all-masked version over still-masked text positions). S_theta is the model's own price of co-commitment; it is not the symmetric cross term X and not a statement about the data law (red-team M10).

### 8.2 Procedure per probed pass, per direction
1. Baseline pass at s (the sampler's own pass; shared). Record the one-pass marginals p1_j.
2. T->I: for r = 1..R, draw the text set. At k0 it is one token drawn from its marginal (exact joint); at k+ two tokens sequentially (one pass between). Then one requery pass at s plus a^(r) stores the image marginals m_r(j, .) for all j in J_I (float64, renormalised). Passes added per r: k_T (1 at k0, 2 at k+).
3. I->T: for r = 1..R, draw the image set b in confidence order in **g = 4 chunks** (8 tokens each at k0): within a chunk the draw is from the product of marginals, between chunks the marginals are requeried with the earlier chunks revealed (3 intermediate passes), then one requery pass gives the text marginals. Passes added per r: g = 4. This is an approximate joint draw; the exact one would need 32 passes per r. Its sensitivity is gate G5.
4. mbar_j = (1/R) sum_r m_r(j); I_hat_j = (1/R) sum_r KL(m_r(j) || mbar_j) (plug-in mixture estimator; bounded above by ln R per position).
5. Naive reference for the inconsistency check: N_j = (1/R) sum_r KL(m_r(j) || p1_j). Exact identity at any finite R: N_j = I_hat_j + KL(mbar_j || p1_j), so I_inc,j = KL(mbar_j || p1_j) costs nothing extra and is reported next to S_theta at every probe.
6. S^{T->I}_n = sum_{j in A^I} I_hat_j. S^{I->T}_n = sum_{j in A^T} I_hat_j.
Probe isolation: probes run on copies of the state and never change the sampler's RNG state or the trajectory. A saturation diagnostic (share of positions with I_hat_j > 0.5 ln R) is reported.

### 8.3 What is probed and how many trajectories
- R = 8 for D1 and D2. All R draws are stored: R = 4 (two disjoint halves) and R = 8 estimates are reported; the extrapolation 2 I(8) - I(4) is a sensitivity analysis only. The plug-in bias is negative and larger where dependence is larger (toy: 35 percent low at R = 4, 1.4 percent at R = 64 [V]), which works against the early-concentration prediction (conservative for H-A1).
- **D1 (profile, sets M for DA and the predictor M for H-C)**: 128 trajectories at k0 with probes at the centre pass of each window: centre(w) = (w - 1) P_w + 2, i.e. passes 2, 6, 10, 14, 18, 22, 26, 30 of 32; 64 trajectories at k+ with probes at the first pass of each 2-pass window (centre(w) = 2(w - 1) + 1, passes 1, 3, ..., 15).
- **D2 (H-A confirmation)**: 256 trajectories at k0 with probes at pass 1 and the centres of windows 1, 2, 7, 8 (passes 1, 2, 6, 26, 30). No extension (R7).
- Condition R trace: 64 trajectories at k0, same probes as D2.
- Probe passes at k0: R (k_T + g) = 8 (1 + 4) = 40 per probed pass; at k+: 8 (2 + 4) = 48.

### 8.4 Cost as a formula
Extra forward passes per probed pass = R (k_T + g) (T->I: R k_T; I->T: R g). Per trajectory:

    passes_traj = N + n_probe x R x (k_T + g) x f_ord,     f_ord in {1, 2} (2 only if G5 requires both orders)

Defaults: k0 D1: 32 + 8 x 40 = 352; k0 D2: 32 + 5 x 40 = 232; k+ D1: 16 + 8 x 48 = 400. GPU time = passes x t_b (t_f for fp32 probe passes if G1b requires, after measuring t_f).

### 8.5 Information fraction (for H-A1-Q and H-A2)
Q_j = I_hat_j / H(mbar_j), the share of position j's mixture-marginal entropy that the revealed other modality explains (0 <= Q_j <= 1 because I <= H). Positions with H(mbar_j) < 0.05 nats are excluded. Q controls the bound S_j <= H_j (nouns are high-entropy slots, function words are not). Raw S_j by type is reported too. POS labels come from the final caption at word-initial subtokens, assigned after the trajectory ends; because the label is realised, a position's type is correlated with its marginal, which is why Q is the primary statistic.

### 8.6 Exploratory maps (no decision rule)
S_{T->I} per image position on the 2D token grid against a foreground map of the final image (pinned segmenter, quality on these images unverified); S_{I->T} by the spatial-word list; correlation of sample-level cumulative S with Lift within the J arm.

### 8.7 Validity checks of the estimator (gates)
- **G0 unit test on the toy**: the production estimator, run on the tables of `analysis/framework/check_crossmodal_mixture.py`, reproduces: identity naive = I + KL(mbar||p1) to 1e-12; block J gives naive 0.08109, mixture 0; finite-R estimate below I_theta in 40/40 within 3 standard errors.
- **G1 noise floor**: (G1a) the same state run in different batch positions and compositions; (G1b) a **no-information reveal**: reveal one token of probability above 0.999 (for example a post-EOS position) and compute the per-token KL between all other marginals before and after. This is the bf16-quantisation floor under a changed input (setup.md 2.1: bf16 log-probabilities, row sums off by 2e-3). Median floor must be below 5 percent of the smallest S_theta value used in any comparison. Failing that, probe passes run with fp32 weights (6.3 GB, t_f to be measured) and the gate repeats; failing that too, H-A and H-C are declared not measurable.
- **G2 null by construction (NC-1)**: the modality-blind wrapper (text marginals from a pass with all image positions masked, image marginals from a pass with all text tail positions masked; two passes per evaluation) must give |S^{T->I}|, |S^{I->T}| and I_inc below the G1 floor at all probes of 16 trajectories.
- **G3 injection test (block J on the real network)**: wrapper that returns the modality-blind image marginals mixed 70/30 with uniform over the image slice whenever any text token beyond s is revealed, unmixed otherwise. True dependence is 0 by construction. Required: mixture estimator below the G1 floor; naive estimator equals I_inc within 1e-6 and is above 10 x the floor at the first probe. This shows the estimator does not manufacture early concentration from marginal inconsistency.
- **G4 bias**: on 16 trajectories, probes at windows 1, 4, 8, compare R = 8 with R = 32; the early/late ratio of S computed with R = 8 must be within 25 percent of the one with R = 32, in both directions.
- **G5 draw order and granularity**: on 8 trajectories at two probes compare the I->T estimate for g = 4 against g = 8 and g = 32 (exact), and the confidence order against its reverse. If the median relative difference between g = 4 and g = 32 exceeds 0.3, g = 8 becomes the registered choice if its difference from g = 32 is below 0.3, otherwise I->T is reported as "chunk-dependent" and excluded from the H-A1 conjunction (H-A1 is then decided on T->I alone and labelled so). If the order difference exceeds 0.3, S_theta used afterwards is the mean over both orders (f_ord = 2).
- **G6 probe invariance**: generation with probes on equals generation with probes off (identical token sequences; if kernels are nondeterministic, the rate of differing sequences must not exceed that between two probe-off runs).
If G1, G2, G3 or G4 fail, H-A and H-C are reported as "not measurable by this estimator on this checkpoint" and no inferential claim is made about S_theta; H-B still runs with DA labelled "profile-guided by an unvalidated trace".

### 8.8 Negative and positive controls

| Id | Kind | Setting | Required result |
|---|---|---|---|
| NC-1 | negative (estimator) | modality-blind wrapper | S, I_inc below the G1 floor |
| NC-2 | negative (estimator) | injection test (G3) | mixture below floor, naive above 10 x floor |
| NC-3 | negative (token types) | permute type labels within a sample, 1,000 times | Q_O / Q_F permutation distribution centred within 0.05 of 1 |
| NC-4 | negative (padding) | probe positions after the first `</s>` or pad | Q on those positions below the Q of function words |
| NC-5 | negative (endpoint) | permute pairs within a cell, run the full Lift pipeline (pilot: J only, R1) | mean Lift within +-0.05 point, CI contains 0 |
| NC-6' | **negative (schedule)**: independent-modality control | **modality-blind model** (as NC-1) driving the sampler, 128 seeds (D5), arms J, Alt, DA, TF at k0 | every arm's Lift and every contrast has CI containing 0 and |d| < 0.3 point. Cross-modal dependence is absent by construction, so no schedule can improve consistency; this tests the pipeline, the metric and the bootstrap for artefacts (for example from shared positions or caption length). Cost: two passes per step |
| I2 | pipeline identity | Alt with empty text passes (a text-only pass that commits nothing) equals Jd, 8 seeds | bitwise identical samples (no time input, common random numbers) |
| NC-7 | placement control | DA-low | enters H-B1' as the dependence-blind control |
| PC-A | positive (endpoint) | Ref-real vs shuffled Ref-real; Ref-real vs J | Lift(Ref-real) > 0 and Lift(Ref-real) > Lift(J), each with an interval excluding 0 (O5; unpaired bootstraps, each cell resampled independently with its baseline recomputed, R10). The ordering Lift(Ref-T2I) > Lift(J) is descriptive |
| PC-B | positive (harness) | reproduce UniDisc App. I: CFG on steps 1-3, 12-14, 22-24 of 24 and all steps, T2I with 128 COCO prompts, at the selected resolution | ordering CLIP(1-3) > CLIP(22-24) with paired CI excluding 0; mean conditional-vs-unconditional logit distance decreasing over steps (Spearman <= -0.8). The paper's CLIP variant is unknown, so only the ordering is required |
| PC-C | positive (estimator code) | G0 | as in 8.7 |
| PC-D | positive (sensitivity) | T2I step-1 image marginals under the matched caption vs the caption of another COCO item | mean KL above 10 x the G1 floor |

A failing positive control means the pipeline cannot recover a known effect; the experiment stops at that stage and the failure is logged.

## 9. Controls and confounds (checklist the engineer signs)

1. Matched passes, matched per-window per-modality budgets; the unmatched tokens per pass in pure windows reported per arm (5.2).
2. Same weights (bf16), same attention, same position embeddings; all committed tokens visible in all later passes.
3. No time input (setup item 2); no time rule needed.
4. Tie rule: lowest position index; no random tie-breaking anywhere (the official sampler's "ties can commit more than k" is not used: `ordered_commit` commits exactly the prescribed set).
5. float64 for every renormalisation, softmax-after-logits, categorical draw and KL; common random numbers by position (4).
6. Guidance off in conditions P and R; in G a guided pass counts as 2.
7. No generation is filtered, retried or discarded; failures (NaN, empty caption, OOM) are counted and reported.
8. Nothing is tuned on D3; the only tuned object, M for DA, comes from D1.
9. Evaluation models load after generation, one at a time, from pinned hashes; no network access during scoring.
10. All per-sample outputs (tokens, caption, image, per-pass committed sets, probe arrays) saved under `runs/EXP-001/<stage>/` atomically per seed, resumable (machine reliability, setup item 5c); free system commit logged per stage.
11. **Freeze before scoring (R9)**: before any D3 caption or image is scored, `analysis/EXP-001/` (Lift, bootstrap, Holm, classes, H-A, H-C) is run end-to-end on D0 pilot outputs with labels scrambled, hashed, and its hash written into `runs/EXP-001/arms/manifest.json` with the hashes of all D3 token files. CLIP scoring of D3 runs once.

## 10. Statistics

### 10.1 Unit, design, interval, p-values
Unit = seed i. Every comparison is paired over seeds. Interval: percentile paired bootstrap over seeds, B = 10,000, recomputing the shuffled baseline inside each replicate (partners with the same original seed index excluded when a seed is drawn twice); BCa as a sensitivity. In a synthetic check the bootstrap SE matched the true sampling SD (0.307 against 0.306) [C]. Sensitivity for the primary (O8): an arm-swap randomization test (swap DA and J samples within seed, recompute both baselines, 10,000 draws); reported, not decisive.
**Two-sided p for a paired contrast (R5)**: p = 2 min{(1 + #{theta* <= 0})/(B + 1), (1 + #{theta* >= 0})/(B + 1)}, capped at 1, from the same bootstrap that gives the interval. If any p lies within 2 sqrt(p(1-p)/B) of the Holm threshold it is compared with, that bootstrap is rerun once with B = 100,000 and a fixed seed recorded in the manifest, and the B = 100,000 value is used. For H-A and H-C see 10.3.
Common random numbers by position help for plans sharing a prefix (window arms) and not for TF/IF. The sample-size rule uses a directly estimated paired SE and needs no rho term.

### 10.2 Primary contrast, multiplicity, outcome classes, error control
- **Fixed-sequence gatekeeping at FWER 0.05 for H-B (R3).** Step 1: H-B1 (DA - J at k0), two-sided 0.05. Step 2, only if step 1 rejects: Holm at 0.05 over the six secondary tests (1) Alt - J at k0, (2) DA - J at k+, (3) DA - DA-low at k0, (4) TF - J at k0, (5) IF - J at k0, (6) H-B2 by intersection-union (R6; p = the larger of the two one-sided p-values for H0: d >= 1.0). If step 1 does not reject, the six are reported with Holm-adjusted p-values and labelled exploratory. A test that is not run enters Holm with p = 1. DA - J at k- is part of H-B3 (estimation only).
- **Outcome classes (R4)** for a contrast with estimate d and 95 percent interval (lo, hi), m = 1.0: *positive* = Holm-adjusted p <= 0.05 (for the primary: unadjusted p <= 0.05) and d > 0, labelled "at or above the MEI" if d >= m; *reversed* = the same with d < 0; *null* = (lo, hi) inside (-m, m); *inconclusive* = otherwise. Unadjusted 95 percent intervals are always reported. Operating characteristics [C] (n = 500, sigma_L = 4, rho 0):

| true d (points) | P(lo > 0) | P(lo > 0 and d_hat >= 1) | P("null") |
|---|---|---|---|
| 0.0 | 0.024 | 0.000 | 0.954 |
| 0.5 | 0.507 | 0.024 | 0.506 |
| 1.0 | 0.976 | 0.501 | 0.026 |
| 1.25 | 0.999 | 0.839 | 0.002 |
| 1.5 | 1.000 | 0.976 | 0.000 |

  "Power 0.977" is P(significant) at d = 1.0; the probability of being labelled "at or above the MEI" at d = 1.0 is 0.50 and at least 0.84 for d >= 1.25.
- **Conjunctions are intersection-union tests** and need no multiplicity adjustment: the H-B null across k+ and k0 and contrasts, H-B2, "TF - J and IF - J both null".
- **Error control is per claim (R11).** H-B: FWER 0.05 as above. H-A: one conjunctive claim (H-A1 both directions and H-A2, intersection-union, one-sided 0.025 per ratio, i.e. the 95 percent two-sided lower limit). H-C: one-sided 0.05. No Bonferroni across EXP-001 and EXP-002 (unrelated hypotheses on different models). Paper 1 also reports the sensitivity with every confirmatory level halved (primary 0.025, Holm family 0.025, H-A 0.0125 per ratio, H-C 0.025) and which claims survive; both come from the same bootstrap output.
- Secondary metrics of 7.2 are descriptive with intervals, uncorrected, flagged.

### 10.3 H-A and H-C statistics
- H-A1: ratio of means (early over late) per direction, with the probe averaging of section 2; percentile bootstrap over trajectories, B = 10,000; supported if the lower 95 percent limit is >= 1.5 in both directions. Weak falsification: the **97.5 percent upper limit** of any of the three ratios (two directions and H-A2) is < 1.5; this is a disjunction, so P(false weak falsification) can reach about 0.075 when all three true ratios equal 1.5, and this is stated in the report (O6). Reversed: the upper limit of an H-A1 ratio is < 1.0.
- H-A1-Q and H-A2: as in section 2, same bootstrap.
- **No extension (R7a)**: D2 = 256 trajectories at k0. [C] SE(ln ratio) = 0.0444 at n = 256 (cv 0.6, correlation 0.3 [A]); P(lower limit >= 1.5) = 0.935 at a true ratio of 1.75 and 0.025 at 1.5; the three-part conjunction is about 0.82.
- H-C: rho_strat = mean of the within-k Spearman correlations of (M_{w,k}, Delta_{w,k}) over w = 1..8, for k in {k0, k+}; one-sided permutation test permuting windows within each k separately (100,000 draws); supported if rho_strat >= 0.5 and p <= 0.05. One-sided 5 percent critical value of rho_strat = 0.440 [C]. Reason for stratifying: a pooled Spearman over 16 cells can be "supported" by a between-k shift alone (false support in 97 percent of cases in the statistician's simulation). The interval for rho_strat is a double bootstrap (seeds for Delta, trajectories of D1 for M). M comes from D1, which is independent of D3 (the selection of DA's windows used D1 only).

### 10.4 Sample size and its stated assumptions [A until the pilot]
- Assumptions: sigma_L = 4 points; rho_pair = 0; effect of interest m = 1.0. Under the influence-based SD the required n rises by about 35 percent (Holm-level n about 680) [I, statistician power notes], still under the cap.
- n for power 0.90 at two-sided alpha: n = ((z_{1-a/2} + z_{0.90}) sigma_d / m)^2 with sigma_d = 5.66: 337 at alpha = 0.05 and 505 at 0.05/7 [C]. At n = 500: power 0.977 and 0.897 (sigma_L = 4), 0.885 and 0.682 (5), 0.750 and 0.478 (6).
- **Rule (R2)**: sigma_d,up = sqrt(64) x (bootstrap SE of the paired contrast Alt - J at k0 on D0, full Lift pipeline with in-replicate baseline recomputation, B = 10,000) x sqrt(63 / chi2_{0.20, 63}). n_req = ceil(1.5 x ((1.96 + 1.2816) sigma_d,up / 1.0)^2). **n_conf = min(1000, max(500, n_req))**. If n_req > 1000, n_conf = 1000, all tests still run, and the achieved MDE (1.96 + 1.2816) sigma_d,up / sqrt(1000) is reported. (Alt - J is the conservative proxy for DA - J: it differs from J in all 8 windows, DA in 4.)
- H-C: the SE of Delta_w is projected from the pilot Alt - J bootstrap SE ("bootstrap SE of Delta_w"); stop rule 4's bound of 0.15 point needs rho_pair >= 0.65 at n = 500 or >= 0.30 at n = 1000 (by the card's own formula, hand-computed). H-C is likely underpowered; "not tested at this budget" is the expected outcome unless the pilot shows strong pairing.

### 10.5 Pilot (only variance and cost; firewall, R1)
D0, 64 seeds. Arms J, Alt, TF, IF at k0; J and Alt at k+; Ref-real on 32 COCO items; probes on 16 trajectories for G1 to G6, NC-1, NC-2. Purpose: sigma of the influence values psi_i, the bootstrap SE of Alt - J, rho_pair, t_b and t_f, memory, noise floors, padding share, magnitude of I_inc and S (descriptive), the dynamic-range gate of section 6.
**The D0 analysis script computes and writes only**: per-arm SDs of the influence values psi_i, bootstrap SEs and correlations of paired contrasts, cost and memory figures, noise floors, padding share, and the point estimate of Lift(J) with its bootstrap SE (for the dynamic-range gate), and Lift(Ref-real) for PC-A. It does not compute into any printed or saved field the mean Lift of Alt, TF, IF or Ref-T2I, or the mean of any contrast. Its source is hashed in `runs/EXP-001/pilot/` before D0 is generated. NC-5 on the pilot uses J only; the other arms' NC-5 runs at stage 3.
No hypothesis test is run on pilot data and pilot data are not reused in D1 to D5. Allowed pilot-based changes: n_conf by the rule, batch size, probe dtype, the P_rand fork. Not allowed: arms, endpoint, effect of interest, window count, decision thresholds.

## 11. Stop rules and falsifiers

Staging is by information per GPU-hour (section 12). Each stage ends in a written verdict file; the next runs only if its precondition holds.

1. **Stage gates.** PG-1, PG-2, G0 to G6 and the NC/PC checks must pass at stages 0-1; a failed positive control or gate stops the later stages for the measurement it protects (8.7).
2. **H-A.** Positive: H-A1 lower limits >= 1.5 in both directions and H-A2 lower limit >= 1.5 (with the wording rule for H-A1-Q). Weak falsification as in 10.3; reversed as in 10.3. Decided once at n = 256, no extension. The trace shape (monotone, mid-trajectory peak) is reported whatever the verdict.
3. **H-B, stage 3.** Run arms J, Alt, TF, IF, DA, DA-low at k+ and k0. If at both k the contrasts Alt - J and DA - J are null (interval inside (-1, 1)) and TF - J and IF - J are both null, then H-B is reported as "null at k in {k+, k0}" (an intersection-union conclusion), stages 4 and 5 do not run, and the claim is limited to those k and this value rule. If any contrast is positive, run stage 5 (k-). If reversed (J better than Alt or DA with p <= 0.05 and d <= -1), run stages 5 and 4 to localise it.
4. **H-C, stage 4.** Run the Sep arms only if (i) some stage-3 contrast is positive or reversed, and (ii) the projected SE(Delta_w) from the pilot Alt - J SE at the allowed n is at most 0.15 point (needs rho_pair >= 0.65 at n = 500 or >= 0.30 at n = 1000). Otherwise H-C is "not tested at this budget", S_theta stays descriptive; decided before any Sep run and logged.
5. **Dose.** H-B3 reported as a pattern of point estimates (k+ >= k0 >= k-); estimation only.
6. **Budget stop.** The core path (stages 0-3) has a cap of **25 GPU-hours**. Conditional stages 4-7 each need their preconditions and an orchestrator's yes if cumulative time would pass 40 hours. Exceeding the core cap stops the work for the orchestrator.
7. **What makes P5 leave the review's open problems or be reported as negative.**
   - Negative (on this checkpoint, resolution and value rule only): H-A weak falsification in any of its ratios, or H-B null at k+ and k0 with all gates passed. A negative H-A with a positive H-B is reported as such (separation helps although the trace is not front-loaded; the mechanism claim is dropped).
   - Drop P5 from the open problems (replace with "measured, small"): both of the above hold, G0 to G6 passed, and condition R reproduces the null for H-A.
   - Keep P5 open and say the measurement was inconclusive: any of G1 to G4 failed, the dynamic-range gate failed in both conditions, or an interval straddles its effect of interest at the fixed n.
   - Do not generalise to any other checkpoint, to guided sampling, or to the data law q in any of these cases.

## 12. Compute budget on the 12 GB laptop GPU

Symbols: t_b = seconds per sample-pass (batch 1; no batching gain), t_f for fp32 probe passes, t_e = evaluation seconds per scored sample, N0 = 32, N+ = 16, N- = 64, R = 8, g = 4. Weights bf16 2.82 GB; the largest tensor is the logits (about 0.1 GB per sample at 1,085 tokens), so memory is not binding at batch 1-4; the binding resource is time and system commit.

Passes by stage (512 px, n_conf = 500):

| Stage | What | Passes formula | Passes |
|---|---|---|---|
| 0 | PG-1, PG-2, PG-3 (plan-generator tests, G0, ordered_commit sets); COCO draw; metric pipeline on Ref-real | PG-1 about 0.4 h at the 1,024-px comparison; others small | about 0.5 h |
| 1 | pilot D0 (J, Alt, TF, IF at k0; J, Alt at k+; P_rand regeneration of J; probes for G1-G6, NC-1, NC-2; I2) | 64 x 160 + 2,048 + about 28,000 probe/gate passes | about 45,000 |
| 1b | PC-B (CFG windows, 128 prompts, pass-equivalents with CFG factor 2.2) | 128 x 159.6 | about 20,000 |
| 2 | profile D1: k0 128 traj, k+ 64 traj | 128 x 352 + 64 x 400 | 70,656 |
| 3a | H-A confirmation D2 at k0 | 256 x 232 | 59,392 |
| 3b | core arms: J, Alt, TF, IF, DA, DA-low at k0 and k+, plus J-global and Jd at k0 | n x (6 x 32 + 6 x 16 + 32 + 24) | 172,000 |
| 3c | references Ref-T2I and Ref-I2T | n x (24 + 8) | 16,000 |
| 3d | NC-6' blind-model null: 128 seeds x 4 arms x 32 passes x 2 | 32,768 | 32,768 |
| 4 | window arms Sep_1..8 at k0 and k+ | 8 n (32 + 16) | 192,000 |
| 5 | dose: six arms at k- | 6 n x 64 | 192,000 |
| 6 | condition G (six arms at k0, n = 250, guided = 2.2 passes) plus O at 50 steps | 6 x 250 x 32 x 2.2 + 250 x 50 x 2.2 | about 133,000 |
| 7 | condition R (J, Alt, DA at k0, n = 250; trace 64 trajectories) | 3 x 250 x 32 + 64 x 232 | about 39,000 |

    GPU hours = (sum of passes) x t_b / 3600  +  n_scored x t_e / 3600  [+ probe passes at t_f instead of t_b if G1b requires fp32]

Core path (stages 1 to 3d): about 416,000 passes, i.e. 416,000 x t_b / 3600: **14.9 h at t_b = 0.129 s, 10.4 h at 0.09 s**; plus stage 0 (0.5 h) and evaluation (t_e: CLIP is negligible; the VQA subset, KID, CLIP-IQA and GPT-2 about 1.5 h, to be set from the pilot) gives **about 17 GPU-hours (12 at 0.09 s)**. At the n_conf cap of 1,000 the stage 3b and 3c passes double to 344,000 and 32,000, giving about 604,000 passes: 21.6 h at 0.129 s, about 24 h with evaluation, inside the 25-hour core cap. Conditional stages at t_b = 0.129 s: stage 4 6.9 h, stage 5 6.9 h, stage 6 4.8 h, stage 7 1.4 h; all stages about 37 h. No training stage exists. Other tiers: 256 px core path about 5 h; 1,024-px reduced design about 22-25 h (section 4).
Reliability: runs gate on free system commit and resume by seed (setup item 5c); a reboot or closing the stale processes before long runs is recommended there and may move the batch-4 and CFG OOM boundaries.

## 13. What the review (Paper 1) states under each outcome

Statements are restricted to the checkpoint, resolution, geometry, value rule and metric tested, and say "on UniDisc 1.4B under plain sampling at temperature 1". Until this card is signed and run, P5 stays an open problem with the evidence it needs (framework-v2 D4). Because UniDisc states no licence, any figure with generated images waits for the authors' permission.

| Outcome | Paper 1 states |
|---|---|
| H-A positive, H-B positive, H-C supported | A measured cross-modal dependence trace, front-loaded and on object words (with the entropy-normalised wording rule), and a schedule built from it that beats joint commitment at matched passes; the trace predicts where separation helps. Credits the identity to its sources; claims the measurement and the paired comparison, not the idea of dependence-aware scheduling (novelty audit pending). States the single-checkpoint, 512-px, single-metric-family limits |
| H-A positive, H-B null | Dependence is measurable and front-loaded but co-committing it costs less than the effect of interest at the budgets tested; the identity holds, the cost is small on this model; the schedule lever is not worth its passes here |
| H-A negative (flat or late), H-B positive | Separation helps but not through the front-loaded dependence the review predicted; mechanism claim withdrawn; the within-modality and image-density explanations are raised (DA-low, Jd, text perplexity reported) |
| H-A and H-B null | P5 is a measured small effect on one checkpoint; removed from the open problems with the numbers; no generalisation |
| H-B reversed (J better) | Joint commitment is at least as good as separation at matched passes on this model; the bidirectional-context benefit exceeds the cross-modal cost; consistent in direction with MMaDA-Parallel Table 10 but with matched passes and one set of weights. P5b contradicted on this checkpoint |
| H-C not supported or not tested | S_theta is a descriptive trace; the review does not use it to select schedules; it still reports I_inc to show why the one-pass reference is unusable |
| Any gate fails | The estimator's validity on a real network is not established; the review keeps it as a proposal with its toy verification only and reports the failure |

Whatever happens, the review reports the measurement cost (R (k_T + g) passes per probe) and that S_theta is the text-first and image-first split of the model, not the data law's cross-modal term.

## 14. Risks the red-team should attack first

1. The checkpoint at 512 px and the empty-prompt layout are unvalidated (PG-1, PG-2); an unconditional caption of 32 tokens may be debris (the 32-token sample in setup.md read as web-caption debris), which would put Lift(J) at the floor.
2. Pure windows put 4 text tokens in one pass and 42-43 image tokens in an image pass against 32 in joint passes; the primary contrast mixes cross-modal gain and image-density cost. DA-low and Jd are the only controls.
3. With one committed text token per joint pass at k0, the committed-set I->T statistic rests on a single position per probe; the all-masked version carries the type analysis.
4. The I->T draw is a chunked approximation; the bias direction is unknown (G5 tests it on 8 trajectories).
5. bf16 quantisation of log-probabilities may dominate small S values (G1b).
6. H-C has 8 cells per stratum and noisy Delta; it may be untestable by design.
7. The primary metric is one CLIP model; VQA-type scores are secondary and on a subset.
8. No licence for the checkpoint limits what can be published.

## 15. Deliverables of the run

`runs/EXP-001/{pilot,profile,haconfirm,arms,windows,dose,condG,condR,blindnull}/` each with config, seeds, git SHA of the code, per-sample outputs, probe arrays, logs; `runs/EXP-001/da_windows.json` with hash; `runs/EXP-001/arms/manifest.json` (R9); analysis scripts under `analysis/EXP-001/` that regenerate every table; a verdict file per stage. Ledger rows (hypotheses H-A, H-B, H-C; experiment EXP-001) are added only after both signatures, by the orchestrator.

## 16. Sign-off

| Role | Check | Status |
|---|---|---|
| statistician | sections 10 and 11 (R1-R12 applied; items in change log D need a second look: chunked draw, gate fork, matching rule, H-C predictor source, PG gates) | unsigned |
| red-team | sections 1.4, 5, 8.7, 8.8, 9, 14: confounds, controls, estimator validity, attack on DA | unsigned |
| lab-engineer | section 3 open items, plan generator tested, G0 passes, PG gates, cost re-timed after commit cleanup | pending |
| gate-auditor | stage verdicts against this card | pending |

## 17. Change log

- v0.1 (2026-10-14): first draft by experiment-designer.
- v0.2 (2026-10-14): statistician R1-R12 applied; O2-O8 adopted, O1 declined with reason; setup facts filled (section 3); geometry, plan generator, estimator cost and compute re-scoped (change log at the top, B and C); negative control NC-6' and identity I2 replace the k = 1 identity; gate fork changed (P' to P_rand); pre-pilot gates PG-1, PG-2 added. Pre-freeze amendments still allowed: the open items of section 3 (pins, COCO draw), the output of the sample-size rule (10.4), and the gate outcomes (PG-1, PG-2, dynamic range). Any other change after signing creates v0.3 with a dated entry here.
