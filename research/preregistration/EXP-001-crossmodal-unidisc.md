```yaml
agent: experiment-designer
date: 2026-10-14
brief: Preregistration card EXP-001, first measurement of cross-modal dependence during sampling in a unified discrete-diffusion model (P5a, P5b of framework-v2 section C; validity hypothesis H-C).
card:
  id: EXP-001
  version: v0.1
  status: draft, unsigned
  signatures: {statistician: none, red-team: none}
  frozen: false          # frozen when both sign; afterwards changes only as a new version with a change log (section 17)
  hypothesis_ledger_ids: to be assigned when the rows are added (H-A, H-B, H-C); no ledger rows written by this draft
sources_examined:
  - research/CONTRACT.md
  - research/review/framework-v2.md (A, B, C, D, E)
  - research/review/dossier/primer-multimodal.md (0, 1, 2.2, 2.4, 4, 5/Q5)
  - research/review/audits/2026-10-14-red-team-selection-term.md (M10, lines 347-371)
  - analysis/framework/check_crossmodal_mixture.py and .log
  - research/review/method/selection-term.md (T6, T9)
  - web: github.com/linzhiqiu/t2v_metrics (E1), github.com/alexanderswerdlow/unidisc (E1); cocodataset.org terms page did not render (not verified)
coverage: >
  Read in full: the files above at the sections named. NOT read: UniDisc paper or code (everything about its
  sampler, sequence geometry, time conditioning and padding is taken from the primer, E1/E2 secondhand, and is
  listed in section 3 as "to be filled from runs/env-2026-10-14/setup.md"); MMaDA-Parallel code; any paper on
  dependence-aware parallel unmasking for single-modality DLMs (novelty not audited, see 1.3).
claims:
  - statement: "No paper in the set measures a cross-modal quantity per step; the only joint-versus-sequential contrast (MMaDA-Parallel Table 10) is confounded."
    status: supported
    evidence: primer-multimodal.md sections 0 and 4 (rows B1-B3)
    level: E2
    confidence: 0.7
  - statement: "The mixture-reference estimator removes the marginal-inconsistency term on toy models (naive 0.08109 vs mixture 0 on red-team block J)."
    status: supported
    evidence: analysis/framework/check_crossmodal_mixture.log lines 1-3 (toy only, says nothing about a real network)
    level: E4 (toy)
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
  - estimator artifacts (marginal inconsistency, finite-R bias, order dependence, S bounded by entropy)
  - confidence-rule artifact (early commits are low-entropy and low-dependence tokens)
unknowns: [section 3 list; 3 of them can change the geometry: L_T, L_I, padding]
next_test: {hypothesis: "H-A, H-B, H-C", intervention: "commit schedule (sets of modality-pure windows) at matched passes", primary_metric: "paired CLIP ViT-L/14 matched-minus-shuffled lift, DA minus J at k0", falsifier: "section 11", gpu_hours: "formula in section 12; about 10 at stage 4 if t_b = 0.06 s"}
```

# EXP-001: cross-modal dependence during sampling in UniDisc (P5a, P5b, H-C)

Tags: [S] source fact, [I] inference, [H] hypothesis, [A] assumption until the pilot, [V] verified on a toy.
Nothing in this card has been run. Every number marked [A] is replaced by a pilot estimate before the card
is frozen, and the replacement rule is stated next to it.

## 0. Summary

One frozen checkpoint (UniDisc 1.4B interleaved, no training, no fine-tune), unconditional joint generation of
a (caption, image) pair, plain sampling at temperature 1 with no guidance as the primary value rule. Two
measurements. (1) The per-step trace of the model's own cross-modal dependence S_theta in both directions with
the mixture-reference estimator (H-A), plus its validity checks. (2) A family of commit schedules at matched
forward passes and matched per-window, per-modality token budgets, differing only in which windows commit text
and image tokens in separate passes (H-B), scored by a matched-minus-shuffled CLIP lift. Window-wise
separation arms test whether S_theta predicts where separation helps (H-C). The card is written so that a
null, a positive and a reversed result are each reported.

## 1. Claim contract

### 1.1 Claim, one sentence
In an all-discrete unified model sampled with several tokens per pass, the model's own cross-modal dependence
is concentrated early in the trajectory and on object words, and commit schedules that do not co-commit the
high-dependence text-image pairs yield higher text-image consistency than joint commitment at the same number
of forward passes.

### 1.2 Mechanism
A joint pass commits a text set a and an image set b from a product of predicted marginals. Its factorisation
error contains a cross-modal part (framework-v2 C: TC(a,b) = TC(a) + S_{T->I} + TC(b|a), with
S_{T->I} = sum_{j in b} I(a; b_j | s); symmetric S_{I->T}). A schedule that commits a first and b in a later
pass lets b see a. The toy [V] (primer-multimodal-check.py, reported in primer section 4) shows the
trade-off: at equal tokens per pass, separating the modalities removes the cross term and pays within-modality
total correlation, and can lose to an interleaved schedule. Hence the card tests "separate the dependent
pairs", not "separate the modalities".

The statement "joint commitment costs where cross-modal dependence is high" is close to an identity
(primer section 0 item 5). The empirical content tested here is: (a) where in the trajectory and on which
tokens the model's dependence sits (H-A); (b) whether any schedule exploits it at matched passes (H-B); (c)
whether the measured quantity predicts the gain from separation window by window (H-C).

### 1.3 Closest methods and the exact distinction
- MMaDA-Parallel Table 10 (fully parallel 71.0/63.2/59.8, semi-parallel 68.3/60.7/57.5, sequential
  64.2/56.5/54.1) [S, primer]. Confounds: sequential text cannot see the image; training differs; passes not
  matched; one run; GPT-4.1 judge; no interval. Its released sampler is not fully parallel (image commits from
  text_steps//4, E3). Distinction here: one set of weights, bidirectional attention in every arm, every committed
  token visible to every later pass, matched passes and matched per-window per-modality budgets, paired seeds,
  intervals.
- UniDisc App. I, Fig. 24-25 [S, primer]: conditional-vs-unconditional logit distance shrinks with decoding;
  CFG only on steps 1-3 of 24 gives CLIP 0.301 against 0.283 on steps 22-24. Guidance drops a whole modality,
  so it measures the value of the other modality's information per step, not the cost of co-commitment, and it
  changes the marginals. Distinction: no guidance in the primary condition; S_theta is a reveal-and-requery
  quantity on committed sets. The guidance result is reproduced as a positive control (PC-B), not used as evidence.
- LaViDa-O layout-first (Tables 13, 16) [S, primer]: trained planner, extra passes, baseline is image-only.
  Distinction: no training, matched passes, joint baseline.
- Framework-v2 estimator and EB-sampler identity (2505.24857 Eq. 7) are the accounting; the reveal-and-requery
  estimator with a mixture reference has no published counterpart in the papers read [E1, "not found"].
- Dependence-aware parallel unmasking in single-modality DLMs: not audited. Before any novelty wording in
  Paper 1, `novelty-auditor` must check it. The review claims the measurement, not the idea of dependence-aware
  scheduling.

### 1.4 Competing explanations (each has a control, section 9)
1. Within-modality cost: a pure text pass commits k text tokens where a joint pass commits about k/3 of them.
   Gains or losses of separation may be within-modality, not cross-modal. Control: DA-low (same number of
   pure windows placed where S_theta is lowest), window arms, text perplexity as a secondary.
2. Off-support states: text-first and image-first put the model in states (one modality complete, the other
   all mask) seen in training only through the 10 percent modality drop (primer Q5 risk 1). Control: window arms
   keep the per-modality masked fractions equal at every window boundary.
3. Metric artifacts: CLIP rewards short generic captions or collapsed images. Control: shuffled-partner
   baseline built into the primary, guardrails on caption length, caption and image diversity, quality.
4. Estimator artifacts: marginal inconsistency (0.081 nats per token at zero dependence in block J), finite-R
   bias, order dependence of the sequential joint draw, and the bound S_j <= H(marginal_j). Controls: mixture
   reference, injection test, R-sweep, order check, entropy-normalised token-type statistic.
5. Position-rule artifact: confidence ranking commits low-entropy (often padding) tokens first, so early
   committed sets may carry little dependence for reasons unrelated to the model's cross-modal coupling.
   Control: condition R (random positions) for the trace, and S reported on all masked positions as well as on
   committed sets.
6. Placement: any separation helps equally, wherever placed. Control: DA against DA-low.

## 2. Hypotheses (falsifiable; direction and minimum effect of interest)

Notation. k = tokens committed per pass (total, both modalities), W = 8 equal windows of the pass index,
"early" = windows 1-2, "late" = windows 7-8. S^{T->I}_n, S^{I->T}_n = the committed-set quantities of
section 8 at probed pass n. Lift = the primary endpoint of section 7 (points, scale 100 x cosine).

**H-A (P5a), measurement hypothesis.** Under plain sampling at temperature 1 from the all-mask state, on
UniDisc 1.4B:
- H-A1 (early concentration, both directions): for each direction d in {T->I, I->T},
  ratio_d = mean over samples of S^d (probes in windows 1-2) / mean over samples of S^d (probes in windows 7-8)
  is at least 1.5 (minimum effect of interest; 1.0 means flat). Both directions must pass.
- H-A2 (object words): in the I->T direction, restricted to the early probes, the entropy-normalised
  information fraction Q (section 8.5) on object-noun positions divided by Q on function-word positions is at
  least 1.5.
- Operationalisation of "layout and object tokens": objects = word-initial subtokens whose word is tagged NOUN or
  PROPN by the pinned tagger on the final caption; function words = DET, ADP, AUX, PRON, CCONJ, SCONJ, PART,
  PUNCT; "layout" = a fixed list of spatial-relation words (left, right, above, below, behind, in front of,
  next to, top, bottom, center, middle, background, foreground; list frozen in the repository before the pilot),
  reported as exploratory because it will have few occurrences. Padding and EOS positions are excluded from
  types. Image-side "salient regions" are dropped from the confirmatory claim: they need a segmenter whose
  validity on 1.4B-model images is itself unverified. An exploratory image-side map is allowed (section 8.6).

**H-B (P5b), schedule hypothesis.** At matched forward passes N, matched total tokens per pass k, and matched
per-window per-modality token budgets (section 5), on the primary condition:
- H-B1 (primary): Lift(DA) - Lift(J) >= 1.0 point at k0, where DA separates the four windows with the highest
  profiled S_theta and J is joint commitment in every window.
- H-B1' (placement): Lift(DA) - Lift(DA-low) >= 1.0 point at k0.
- H-B2 (sequential need not beat alternating): max(Lift(TF), Lift(IF)) - Lift(Alt) < 1.0 point at k0
  (a non-superiority claim; its upper confidence limit must be below 1.0).
- H-B3 (dose): the gain Lift(DA) - Lift(J) is non-increasing as k decreases (k+ >= k0 >= k-), and at k = 1 the
  contrast J - Alt is exactly 0 (identity, a pipeline check, not a hypothesis).
The minimum effect of interest of 1.0 point equals the size of the differences UniDisc's authors report between
CFG-window conditions (0.301 vs 0.293 vs 0.283 on a 0-1 cosine scale, i.e. 0.8 to 1.8 points) [S, primer C3];
it is a documented, interpretable scale, not a tuned one.

**H-C (validity).** Let Delta_{w,k} = Lift(Sep_w) - Lift(J) at pass budget k, where Sep_w separates only window
w. Let M_{w,k} = P_w x S_sym(centre of window w), S_sym = (S^{T->I} + S^{I->T})/2 measured on the confirmation
probes, P_w = passes in the window. Over the 16 cells (w = 1..8, k in {k0, k+}), Spearman rho(M, Delta) >= 0.5.
Otherwise S_theta is a descriptive trace only and Paper 1 says so. H-C is conditional on H-B showing a nonzero
Delta somewhere (section 11, stop rule 4).

Directions are stated; each hypothesis is two-sided in its test so that a reversed result is detected.

## 3. To be filled from runs/env-2026-10-14/setup.md

The card does not depend on these values, but freezing requires each one filled (as a pre-freeze amendment, section 17).

| # | Needed | Why it matters | Default used for the numbers in this card |
|---|---|---|---|
| 1 | L_T, L_I (positions per modality), image resolution, vocabulary sizes, how text length/padding/EOS are handled, whether padding positions are predicted and sampled | k grid, windows, the pad-null control, cost | [A] L_T = 128, L_I = 256 (primer: 256 px gives 256 tokens, text 128, default sequence 384); the 1.4B model may use 512 px (1,024 image tokens), which triples cost |
| 2 | Whether the network takes a time or noise-level input, and what the official sampler feeds | confound across arms | rule if it does: t_n = overall masked fraction of L_T + L_I at pass start, same function in every arm |
| 3 | The official sampler's code path: how it ranks (global pool vs per modality), Gumbel noise, nucleus, temperature, default N, CFG implementation and default w | arms J-global, O, condition G; PC-B | [S primer] confidence ranking in one pool, w = 1.5; rest unknown |
| 4 | Whether the pipeline supports a clean modality-blind forward (mask all positions of the other modality) | NC-1 | assumed yes (the modality-drop training makes it a valid input) |
| 5 | Forward-pass seconds per sample at batch B in bf16 and fp32; peak memory; deterministic-kernel behaviour; noise floor of re-running the same state in different batch positions | t_b, probe dtype, gate G1 | formulas in section 12 |
| 6 | Licence of checkpoint and code (primer: none stated) | publication of generations | any release of generated images waits on a written answer; the card does not need release |
| 7 | Exact CLIP, VQA, KID, CLIP-IQA, GPT-2, POS-tagger package versions and weight hashes | endpoint definitions | candidates in section 7; pinned by hash in setup.md |
| 8 | COCO val2017 caption file hash and the list of the 500 items drawn | reference arms | draw: seed 777, sorted by image id |

## 4. Task, data, seeds

- **G0 (primary): unconditional joint generation.** Start: all L_T + L_I positions masked, no prompt. Output:
  one caption (text tokens, padding stripped) and one image. This is the only task in which both modalities
  are committed under a free schedule, which is where the cross-modal term exists. T2I with a clean caption
  has no text set to co-commit, so arms cannot differ; likewise I2T.
- **Unit of analysis ("prompt")**: the seed index i. All arms use the same i. There is no text prompt in G0.
- **References on a public prompt set (not used in any hypothesis test).** COCO val2017 captions, 500 items
  (seed 777). Licence: annotations CC BY 4.0 and images under their Flickr terms [E0, the terms page did not
  render when fetched; engineer to confirm and record]. Used only for evaluation, never redistributed.
  - Ref-real: the 500 real (caption, image) pairs through the metric pipeline. Ceiling and PC-A.
  - Ref-T2I: clean COCO caption, image committed in L_I / k image-only passes (the second phase of TF with an
    oracle text). Ceiling for the image side.
  - Ref-I2T: clean COCO image, caption committed in L_T / k text-only passes.
  Same value rule, same k0, same metric.
- **Not covered**: multi-segment interleaved generation (many images and text spans). It is outside the one-pair
  geometry in which committed sets are defined here; Paper 1 does not claim anything about it.
- **Seed pools (disjoint; per-position uniforms from a counter-based generator keyed by pool and i)**:
  D0 pilot i in [0, 64); D1 profile [10000, 10128); D2 H-A confirmation [20000, 20128), extension
  [20128, 20512) only by rule 11.2; D3 arms [30000, 31000), the first n_conf used (section 10.4); D4 secondary
  conditions [40000, 40250).
- **Common random numbers**: sample i draws a float64 uniform u_j for every position j once; a position's value
  is the inverse-CDF draw from its marginal at the pass in which it is committed using u_j, in every arm. Probes
  use a separate stream and must not touch the sampler stream.

## 5. Arms and schedules

### 5.1 Geometry and the plan generator
Notation: L = L_T + L_I; k tokens per pass; N = L/k passes; W = 8 windows; c_T = L_T/W, c_I = L_I/W tokens per
modality per window; P_w = N/W = (c_T + c_I)/k passes per window. Requirement: k divides gcd(c_T, c_I). With the
default geometry (128, 256): c_T = 16, c_I = 32, gcd = 16.
Grid: k0 = the divisor of gcd(c_T, c_I) with N closest to 48 in log scale (default 8, N0 = 48); k+ = 2 k0
(N = 24, default 16); k- = k0/2 (N = 96, default 4). If 2 k0 does not divide the gcd, set W = 4 once; if it still
fails, drop k+. Recorded as an amendment before the pilot.

Every arm commits exactly k tokens in every pass (the last pass is full because L is a multiple of k). Within a
modality the positions committed are the top-count masked positions by maximum marginal probability, ties
broken by lowest position index (condition P; condition R uses uniform random positions); values are sampled
from the unmodified marginals (section 6). Every arm uses the same weights, the same attention (full
bidirectional, no modality mask), the same position embeddings, and every committed token is visible to every
later pass.

Window rules (pass q = 1..P_w inside window w):
- **Joint window**: text count tau_q = floor(q c_T / P_w) - floor((q-1) c_T / P_w); image count k - tau_q.
  Per-window totals are exactly (c_T, c_I).
- **Pure window**: n_T = c_T / k text-only passes and n_I = c_I / k image-only passes in the window, pass q is a
  text pass iff floor(q n_T / P_w) > floor((q-1) n_T / P_w). Per-window totals are again (c_T, c_I).
A schedule is a set M of pure windows; all other windows are joint.

| Arm | Definition | Role |
|---|---|---|
| J | M = {} (joint every window, proportional split) | primary comparator |
| Alt | M = {1..8} | modality-pure everywhere, interleaved at the proportional rate |
| DA | M = the 4 windows with the largest profiled S_sym (D1), fixed before any D3 run | dependence-aware schedule, zero extra passes at test time |
| DA-low | M = the 4 windows with the smallest profiled S_sym | placement control (same number of pure passes) |
| Sep_w, w=1..8 | M = {w} | H-C window arms |
| TF | text-only passes until all L_T text tokens are committed (L_T / k passes), then image-only | modality-sequential; off-support |
| IF | the reverse | modality-sequential; off-support |
| J-global | no plan: top-k over the pooled masked positions of both modalities by max probability (the official ranking without the official value rule) | split by confidence; descriptive |
| O | the official sampler with its own defaults (steps, temperature, nucleus, guidance, noise) | reference only, condition G |

The "dependence-aware" claim is tested at phase level (which windows separate), not pair by pair; an
instance-level controller (reveal and requery on the candidate pair, which costs extra passes that would have
to be charged to the budget) is out of scope for this card and listed as future work. The profile that sets M
for DA uses J trajectories on D1 only, then M is saved to `runs/EXP-001/da_windows.json` with a hash before D3
starts. The same window set (in normalised time) is used at k+ and k-.

TF and IF cannot be window-matched. Their per-modality budgets match J only at the end of the run. They enter H-B2
and as descriptive references; a loss of TF or IF against J is not read as support for P5b (competing explanation 2).

### 5.2 Matching rules and why
- Matched forward passes N and matched tokens per pass k (the toy shows E_fact depends on k).
- Matched per-window per-modality commit budgets (window-based arms), so masked fractions per modality agree at
  every window boundary and states stay near the training support.
- Matched CFG accounting in condition G: a guided pass counts as 2 forward passes.
- Time input (item 2 of section 3) identical function of the state in every arm.
- The MMaDA-Parallel lesson: no arm uses a differently trained model or a mask that blocks attention, and "text
  first" means the image positions stay masked while text is committed, then the finished text is visible to the
  image passes.

## 6. Value rule (fixed across arms)

- **Primary condition P**: plain sampling at temperature 1 from the unmodified marginals, no top-p, no top-k,
  no guidance, position rule = within-modality confidence ranking (a deterministic function of the state).
  Reason: with a state-only position rule and values drawn from the product of marginals, the value slot V of
  framework-v2 B is 0 and the output differs from the path law by G = 0, so differences between arms are
  differences in schedule, not in value rule. Sample-then-filter (MaskGIT-style) would put a non-product value
  law at k >= 2 into every arm differently (framework-v2 B).
- **Secondary condition G (official guided setting)**: official sampler defaults for value rule (guidance,
  temperature, nucleus, noise), arms J, Alt, DA, DA-low, TF, IF with their plans, O at its default steps. Reason:
  it is what a user runs; guidance also changes the cross-modal conditioning, so results here are labelled as
  mixed effects.
- **Robustness condition R**: condition P with uniformly random positions within modality, for the trace (H-A)
  and arms J, Alt, DA. Reason: competing explanation 5.
- **Float precision**: all logits converted to float64 before softmax and categorical draws; inverse-CDF with
  float64 cumulative sums (32-bit draws truncate and sharpen; selection-term T9). Forward pass dtype per setup.md.
- **Dynamic-range gate and one pre-registered fallback**: in the pilot, if Lift(J) on D0 is below 2.0 points
  (twice the effect of interest), condition P is replaced once by P' = P with nucleus top-p 0.9 in every arm
  (value rule then a state-only tilt; V is no longer 0, stated in the report). If Lift(J) is still below 2.0, H-B
  is declared untestable on this checkpoint and only H-A (descriptive) proceeds. The gate uses only J, Ref-real and
  the shuffled baseline, no contrast between arms.

## 7. Endpoints

### 7.1 Primary (one): matched-minus-shuffled CLIP lift
Model: CLIP ViT-L/14 from the `openai/clip-vit-large-patch14` checkpoint [E0 name; revision hash recorded in
setup.md], text truncated at 77 tokens, the same for every arm, image preprocessing as the checkpoint's. For a
cell (arm, k) with n samples, e_I(x_i) and e_T(c_i) are the L2-normalised embeddings, C_i = cos(e_I(x_i), e_T(c_i)),
B_i = 0.5 x [mean_{j != i} cos(e_I(x_j), e_T(c_i)) + mean_{j != i} cos(e_I(x_i), e_T(c_j))],
**Lift_i = 100 (C_i - B_i)**. The endpoint of an arm is mean_i Lift_i; the contrast is the paired mean
difference over seeds. The shuffled baseline is computed within the arm's own samples, which removes caption-only
and image-only offsets and penalises collapse (low diversity raises B). No sample is excluded: empty or
degenerate captions are scored as they are and counted in the guardrails.
Rationale for CLIP over VQA-type scores as the primary: it is cheap enough to build full n x n matrices for the
shuffled baseline and for bootstrap recomputation, and the checkpoint is available; VQA-type scores cost a
multi-billion-parameter forward per pair.

### 7.2 Secondary
- Raw matched score 100 C_i (no baseline).
- VQA-type consistency (VQAScore family) on a fixed random 250-sample subset of each cell at k0, matched pairs
  only. The t2v_metrics README lists the CLIP-FlanT5 models as legacy v3.0 and the current v3.1 list names other
  VLMs [E1]; the model is pinned in setup.md, not here. TIFA excluded (it needs an LLM question generator).
- Image quality: KID (Inception features, subsets) against 5,000 COCO val2017 images; FID is not used because
  n = 500 is below the 2,048-dimensional feature size. CLIP-IQA per image (package and version pinned).
- Text quality: perplexity of the caption content tokens under a pinned GPT-2 model; non-pad caption length;
  distinct-1 and unigram entropy across the cell's captions.
- Diversity: mean pairwise cosine of image embeddings within a cell.
- Expected regressions (stated now): text perplexity higher in Alt, DA, DA-low (k text tokens per text pass
  against about k/3 in joint passes); KID higher in TF and IF (off-support).
- **Guardrails for a positive H-B1**: DA's caption length within [0.8, 1.25] of J's, image-embedding diversity
  within 0.05 cosine of J's, empty-caption rate not higher by more than 2 percentage points, CLIP-IQA and KID not
  worse by more than 0.2 pilot standard deviations. A positive with a failed guardrail is reported as "positive
  with regression" and is not used as support without that qualifier.

### 7.3 Measurement endpoint for H-A
The per-probe S_theta traces of section 8, both directions, committed-set and all-masked-position versions.

## 8. Estimator protocol for S_theta

### 8.1 Definition
At a probed pass n of a J-arm trajectory with state s: the committed sets are the plan's sets, text set
A^T (k_T positions) and image set A^I (k_I positions), chosen by the position rule as a function of s alone.
For every still-masked image position j (set J_I), the model's dependence is
I_theta(a; b_j | s) = E_a KL(p(b_j | s, a) || mbar_j), mbar_j = E_a p(b_j | s, a), with a drawn from the model's own
joint over A^T. This is the named split "text-first S_theta" (framework-v2 C). The committed-set quantity is
S^{T->I}_n = sum_{j in A^I} I_theta(a; b_j | s); the all-masked-position version sums or averages over J_I.
S^{I->T} is symmetric (b drawn jointly, text marginals requeried). S_theta is the model's own price of
co-commitment; it is not the symmetric cross term X and not a statement about the data law q (red-team M10).

### 8.2 Procedure per probed pass, per direction
1. Baseline pass at s (the sampler's own pass; shared). Record the one-pass marginals p1_j.
2. For r = 1..R: order A^T by the confidence order at s (fixed). For t = 1..k_T: take the marginal of the t-th
   position from the pass at s plus the first t-1 drawn tokens (pass at t = 1 is the baseline), draw a_t by
   float64 inverse-CDF with the probe stream. After k_T draws run one requery pass at s plus a^(r) and store
   the image marginals m_r(j, .) for all j in J_I (float64). Passes added per draw: k_T.
3. mbar_j = (1/R) sum_r m_r(j); I_hat_j = (1/R) sum_r KL(m_r(j) || mbar_j) (plug-in mixture estimator).
4. Naive reference for the inconsistency check: N_j = (1/R) sum_r KL(m_r(j) || p1_j). Identity at any finite R:
   N_j = I_hat_j + KL(mbar_j || p1_j), so the inconsistency term I_inc,j = KL(mbar_j || p1_j) costs nothing extra
   and is reported next to S_theta at every probe.
5. S^{T->I}_n = sum_{j in A^I} I_hat_j. Direction I->T the same with the roles exchanged (k_I draws).
Probe isolation: probes run on copies of the state and never change the sampler's RNG state or the trajectory.

### 8.3 What is probed
- Probed passes: pass 1 and the centre pass of each of the 8 windows (9 probes per trajectory). Default
  geometry at k0: passes 1, 3, 9, 15, 21, 27, 33, 39, 45 of 48.
- R = 8 for D1 and D2 (plug-in bias is negative and not larger than about 35 percent at R = 4 on the toy [V],
  and larger where dependence is larger, which works against the early-concentration prediction, i.e. is
  conservative for H-A1). All R = 8 draws are stored so that R = 4 (two disjoint halves) and R = 8 estimates are
  reported; the extrapolation 2 I(8) - I(4) is a sensitivity analysis only. Block check at R = 32 (section 8.4, G4).
- Joint draw: k_T sequential passes per sample, in the fixed confidence order. The order matters for a model
  that is not exactly consistent; section 8.4 G5 tests it.
- Samples: D1 128 trajectories (profile), D2 128 trajectories at k0 and the first 64 at k+ (confirmation),
  extension to 512 at k0 only by rule 11.2. Condition R: 64 trajectories at k0.

### 8.4 Cost as a formula
Extra forward passes per probed pass per direction = R k_T (T->I) or R k_I (I->T). Both directions:
R (k_T + k_I) = R k. (Framework-v2 C states R k_T + R per direction; the exact count is smaller by R - 1 because
the baseline pass is shared. Either is within the budget below.) Per trajectory:

    passes_traj = N + (1 + W) x R x k x f_ord,       f_ord in {1, 2} (2 only if G5 fails)

Default k0 = 8, N = 48, W = 8, R = 8: 48 + 9 x 8 x 8 = 624 passes per trajectory. GPU time =
passes x t_b (forward time per sample-pass; fp32 for probe passes if gate G1 requires, then t_b -> t_f).

### 8.5 Information fraction (for H-A2)
Q_j = I_hat_j / H(mbar_j), the share of position j's mixture-marginal entropy that the revealed other modality
explains (0 <= Q_j <= 1 because I <= H). Positions with H(mbar_j) < 0.05 nats are excluded. Q controls the bound
S_j <= H_j (nouns are high-entropy slots; function words are not). Raw S_j by type is reported as well.
Labels (POS) come from the final caption at word-initial subtokens, assigned after the trajectory ends;
because the label is realised, a position's type is correlated with its marginal, which is why Q is the
primary statistic.

### 8.6 Exploratory maps (no decision rule)
S_{T->I} per image position on the 2D token grid against a foreground map of the final image (pinned segmenter,
quality of the segmenter on these images unverified); S_{I->T} by the spatial-word list; correlation of
sample-level cumulative S with sample-level Lift within the J arm.

### 8.7 Validity checks of the estimator (gates)
- **G0 unit test on the toy**: the production estimator, run on the probability tables of
  `analysis/framework/check_crossmodal_mixture.py`, reproduces: identity naive = I + KL(mbar||p1) to 1e-12;
  block J gives naive 0.08109, mixture 0; finite-R estimate below I_theta in 40/40 within 3 standard errors.
- **G1 noise floor**: the same state run twice in different batch positions and compositions gives per-token KL
  between marginals with median below 5 percent of the smallest S_theta value used in any comparison. Failing
  that, probe passes run in fp32 (cost t_f); failing that too, H-A and H-C are declared not measurable.
- **G2 null by construction (NC-1)**: the modality-blind wrapper (text marginals from a pass with all image
  positions masked, image marginals from a pass with all text positions masked) must give |S^{T->I}| and
  |S^{I->T}| and I_inc below the G1 floor at all probes of 16 trajectories.
- **G3 injection test (block J on the real network)**: wrapper that returns the modality-blind image marginals
  mixed 70/30 with uniform whenever any text token beyond s is revealed, and the unmixed ones otherwise. True
  dependence is 0 by construction. Required: mixture estimator below the G1 floor; naive estimator equals I_inc
  within 1e-6 and is above 10 x the floor at least at the first probe. This shows the estimator would not
  manufacture early concentration from marginal inconsistency.
- **G4 bias**: on 16 trajectories and probes at windows 1, 4, 8, compare R = 8 with R = 32; the early/late ratio
  of S computed with R = 8 must be within 25 percent of the one with R = 32, in both directions.
- **G5 order**: on 16 trajectories compare S under the confidence order and its reverse; if the median relative
  difference exceeds 0.3, every S_theta used afterwards is the mean over both orders (f_ord = 2).
- **G6 probe invariance**: generation with probes on equals generation with probes off (identical token
  sequences; if kernels are nondeterministic, the rate of differing sequences must not exceed the rate between
  two probe-off runs).
If G1, G2, G3 or G4 fail, H-A and H-C are reported as "not measurable by this estimator on this checkpoint",
and no inferential claim is made about S_theta; H-B still runs without the S-guided arm's justification (DA is
then labelled "profile-guided by an unvalidated trace").

### 8.8 Negative and positive controls in one table

| Id | Kind | Setting | Required result |
|---|---|---|---|
| NC-1 | negative (estimator) | modality-blind wrapper | S, I_inc below the G1 floor |
| NC-2 | negative (estimator) | injection test (G3) | mixture below floor, naive above 10 x floor |
| NC-3 | negative (token types) | permute type labels within a sample, 1,000 times | Q_O / Q_F permutation distribution centred within 0.05 of 1 |
| NC-4 | negative (padding) | probe positions that end as padding or EOS (if padding is sampled, setup item 1) | Q on those positions below the Q of function words |
| NC-5 | negative (endpoint) | permute pairs within each cell, run the full Lift pipeline | mean Lift within +-0.05 point, CI contains 0 |
| NC-6 | negative (schedule) | k = 1: J versus Alt, 64 seeds | identical samples (the plans coincide), so contrast exactly 0 |
| NC-7 | negative (placement) | DA-low | enters H-B1' as the dependence-blind control |
| PC-A | positive (endpoint) | Ref-real vs shuffled Ref-real | Lift(Ref-real) > Lift(Ref-T2I) > Lift(J) > 0, each with a CI excluding the next |
| PC-B | positive (harness) | reproduce UniDisc App. I: CFG on steps 1-3, 12-14, 22-24 of 24 and all steps, T2I with 250 COCO captions | ordering CLIP(1-3) > CLIP(22-24) with paired CI excluding 0; mean conditional-vs-unconditional logit distance decreasing over steps (Spearman <= -0.8). The CLIP variant of the paper is unknown, so only the ordering is required |
| PC-C | positive (estimator code) | G0 | as in 8.7 |
| PC-D | positive (sensitivity) | T2I step-1 image marginals under the matched caption vs the caption of another COCO item | mean KL above 10 x the G1 floor (the model's image marginals can respond to text at all) |

A failing positive control means the pipeline cannot recover a known effect; the experiment stops at that stage
and the failure is logged, no later stage runs.

## 9. Controls and confounds (checklist the engineer signs)

1. Matched passes, matched tokens per pass, matched per-window per-modality budgets (5.1).
2. Same weights, same attention, same position embeddings, all committed tokens visible in all later passes.
3. Time input identical function of the state (setup item 2).
4. Tie rule: lowest position index; no random tie-breaking anywhere.
5. float64 for every softmax-after-logits and categorical draw; common random numbers by position (4).
6. Guidance off in condition P and R; in G a guided pass counts as 2.
7. No generation is filtered, retried or discarded; failures (NaN, empty caption) are counted.
8. Hyperparameters are not tuned on D3; the only tuned object, M for DA, comes from D1.
9. Evaluation models load after generation, one at a time, from pinned hashes; no network access during scoring.
10. All per-sample outputs (tokens, caption, image, per-pass committed sets, probe arrays) saved under
    `runs/EXP-001/<stage>/`; every number in Paper 1 traces to those files.

## 10. Statistics

### 10.1 Unit, design, interval
Unit = seed i. Every comparison is paired over seeds (same i in both arms). Interval: percentile paired bootstrap
over seeds, B = 10,000, recomputing the shuffled baseline inside each replicate (partners with the same original
seed index excluded when a seed is drawn twice); BCa as a sensitivity. Pairing helps only if arms' outcomes
correlate across seeds; common random numbers by position help for plans that share a prefix (window arms), not
for TF/IF. The pilot measures rho_pair; the sample-size calculation below assumes 0.

### 10.2 Primary contrast and multiplicity
- **Primary (single, alpha = 0.05, two-sided):** H-B1, DA - J at k0.
- **Secondary confirmatory family (Holm, familywise 0.05, m = 7):** (1) Alt - J at k0; (2) DA - J at k+;
  (3) DA - DA-low at k0 (H-B1'); (4) TF - J at k0; (5) IF - J at k0; (6) DA - J at k-; (7) the one-sided
  non-superiority test of H-B2: H0: max(TF, IF) - Alt >= 1.0 point at k0.
- H-A and H-C are separate claims with their own rules (section 11); no claim of joint significance across H-A,
  H-B, H-C is made. Secondary metrics of section 7.2 are descriptive with intervals, uncorrected, flagged as such.
- Outcome classes for a contrast with estimate d and 95 percent interval (lo, hi), minimum effect m = 1.0:
  positive: lo > 0 and d >= m; reversed: hi < 0 and d <= -m; null: (lo, hi) inside (-m, m); inconclusive: else.

### 10.3 H-A and H-C statistics
- H-A1: ratio of means (early over late) per direction; percentile bootstrap over trajectories, B = 10,000;
  supported if the lower limit of the 95 percent interval is >= 1.5 in both directions.
- H-A2: ratio of per-sample means of Q (object over function), bootstrap over trajectories, early probes;
  supported if lower limit >= 1.5; the permutation null NC-3 reported.
- H-C: Spearman rho over 16 cells, one-sided permutation test (cell labels permuted, 100,000 draws; the
  one-sided 5 percent critical value is about 0.43 for 16 exchangeable cells [simulated]); the interval for rho is
  a double bootstrap (seeds for Delta, trajectories for M). Supported if rho >= 0.5 and the permutation p <= 0.05.

### 10.4 Sample size and its stated assumptions [A until the pilot]
Assumptions: the standard deviation of Lift_i within an arm sigma_L = 4 points; rho_pair = 0 for contrasts
between arms with different plans, so the standard deviation of a paired difference is sigma_d = sigma_L sqrt(2)
= 5.7 points; effect of interest m = 1.0.
- n for power 0.90 at two-sided alpha: n = ((z_{1-a/2} + z_{0.90}) sigma_d / m)^2 = 337 at alpha = 0.05 and
  505 at alpha = 0.05/7 (the Holm worst case). Computed here, not from a source.
- Default n_conf = 500: power 0.977 for the primary and 0.897 for a Holm-level test at sigma_L = 4; 0.885 and
  0.68 at sigma_L = 5; 0.75 and 0.48 at sigma_L = 6.
- **Rule**: after the pilot, n_conf = min(1000, max(500, ceil(((1.96 + 1.2816) sigma_d_hat / m)^2 x 1.5))) with
  sigma_d_hat the pilot estimate (upper 80 percent limit of its bootstrap), halved in its (1 - rho_pair) factor
  only if the pilot rho_pair interval lies above 0.3. If the rule would exceed 1000, only the primary contrast
  and H-B2 are run and the power shortfall is reported.
- H-A: with per-trajectory coefficients of variation near 0.6 and correlation 0.3 between early and late S [A],
  SE(ln ratio) is about 0.063 at 128 trajectories, half-width about 0.12, enough to separate 1.5 from 1.0.
  The pilot replaces cv; extension to 512 only by rule 11.2.
- H-C: SE(Delta_w) = sigma_L sqrt(2 (1 - rho_pair)) / sqrt(n). With sigma_L = 4, n = 500 and rho_pair = 0.5 this is
  0.18 point, while a single window may move Lift by well under 1 point. H-C is likely underpowered unless
  rho_pair >= 0.7; stop rule 11.4 decides before running Sep arms.

### 10.5 Pilot (only variance and cost)
D0, 64 seeds. Arms J, Alt, TF, IF at k0; J and Alt at k+; Ref-real, Ref-T2I on 64 COCO items. Probes on 16
trajectories (G1 to G6). Purpose: sigma_L, rho_pair per arm pair, t_b and t_f, memory, noise floor, share of
padding, magnitude of I_inc and S (descriptive), the dynamic-range gate of section 6. **No hypothesis test is
run on pilot data and pilot data are not reused in D1 to D4.** Pilot-based changes allowed: n_conf by the rule,
batch size, probe dtype, fp32/bf16, the fallback P'. Not allowed: arms, endpoint, effect of interest, window
count (except the divisibility rule of 5.1), decision thresholds.

## 11. Stop rules and falsifiers

Staging is by information per GPU-hour (section 12). Each stage ends in a written verdict file; the next runs
only if its precondition holds.

1. **Stage gates.** G0 to G6 and NC/PC checks must pass at stage 1; a failed positive control or a failed gate
   stops the later stages for the measurement it protects (8.7).
2. **H-A.** Positive: both directions' lower limit >= 1.5 (H-A1) and H-A2 lower limit >= 1.5. Falsified in the
   weak form ("below the effect of interest") if the upper limit of any ratio is < 1.5. Reversed if the upper
   limit of an H-A1 ratio is < 1.0 (late dependence exceeds early). If an interval straddles 1.5, extend D2 once
   from 128 to 512 trajectories (k0 only) and decide on the final interval; no second extension.
   The trace shape (monotone, mid-trajectory peak) is reported whatever the verdict.
3. **H-B, stage 3.** Run arms J, Alt, DA, DA-low, TF, IF at k+ and k0. If, at both k, Alt - J and DA - J are null
   (interval inside (-1, 1)) and max(TF, IF) - J is null, then H-B is reported as "null at k in {k+, k0}", stages
   4 and 5 do not run, and the claim is limited to those k and this value rule. If either contrast is positive,
   run stage 5 (k-). If reversed (J better than Alt or DA by at least 1.0 with interval below 0), still run stage 5
   and stage 4 to localise it.
4. **H-C, stage 4.** Run the Sep arms only if (i) some contrast at stage 3 is positive or reversed, and (ii) the
   projected SE(Delta_w) from the pilot sigma_L and rho_pair at the allowed n is at most 0.15 point. Otherwise H-C
   is "not tested at this budget" and S_theta stays descriptive; this is decided before any Sep run and logged.
5. **Dose.** H-B3 is supported if the DA - J estimate does not increase as k decreases (point estimates ordered
   k+ >= k0 >= k-); it is reported as a pattern, not a test; NC-6 must hold exactly.
6. **Budget stop.** If cumulative GPU time passes 40 hours before stage 4 ends, stop and ask the orchestrator.
7. **What makes P5 leave the review's open problems or be reported as negative.**
   - Report as negative (on this checkpoint and this value rule only): H-A1 falsified in the weak form in
     either direction, or H-B null at k+ and k0 with all gates passed. A negative H-A with a positive H-B is
     reported as such (separation helps although the trace is not front-loaded; the mechanism claim is dropped).
   - Drop P5 from the open problems (replace with "measured, small"): both of the above hold, G0 to G6 passed,
     and condition R reproduces the null for H-A.
   - Keep P5 open and say the measurement was inconclusive: any of G1 to G4 failed, the dynamic-range gate
     failed, or an interval straddles its effect of interest after the one allowed extension.
   - Do not generalise to any other checkpoint, to guided sampling, or to the data law q in any of these cases.

## 12. Compute budget on the 12 GB laptop GPU

Symbols: t_b = seconds per sample-pass at the chosen batch and dtype (setup item 5), t_f for fp32 probe passes,
t_e = evaluation seconds per sample (CLIP embeddings, VQA subset, KID, CLIP-IQA, GPT-2; setup item 5), L = L_T + L_I.
Memory: weights in bf16 about 2.8 GB by arithmetic on 1.4B parameters [I, unverified; the file is 5.63 GB,
consistent with fp32]; the scoring models load after generation, one at a time.

Passes by stage (n_conf = 500, defaults L = (128, 256), k0 = 8, R = 8; formulas then numbers):

| Stage | What | Passes formula | Passes (default) |
|---|---|---|---|
| 0 | analytic and toy checks (G0), plan generator tests, metric pipeline on Ref-real | CPU (plus 500 CLIP forwards) | 0 |
| 1 | pilot D0 and gates G1-G6, NC-1/2/5/6, PC-A/C/D | 64 x (4 N0 + 2 N+) + 16 (probed traj) x 624 + k=1 check 2 x 16 x 384 + 16 x ~600 | about 35,000 |
| 1b | PC-B harness reproduction | 5 x 250 x 24 x ~1.5 | 45,000 |
| 2 | profile D1 at k0 (128 traj) | 128 x passes_traj(k0) | 79,900 |
| 3a | H-A confirmation D2 at k0 (128) and k+ (64) | 128 x 624 + 64 x (24 + 9 x 8 x 16) | 155,000 |
| 3b | core arms, n_conf each: J, Alt, TF, IF, DA, DA-low at k+ and k0, plus J-global at k0 | n (6 (N+ + N0) + N0) | 240,000 |
| 3c | references Ref-T2I, Ref-I2T | n (L_I/k0 + L_T/k0) | 24,000 |
| 4 | window arms Sep_1..8 at k0 and k+ | 8 n (N0 + N+) | 288,000 |
| 5 | dose: six arms at k- | 6 n N- | 288,000 |
| 6 | condition G (six arms at k0, n = 250, guided = 2 passes) plus O at its default steps | 2 x 6 x 250 x N0 + 2 x 250 x N_def | about 176,000 (N_def = 64 assumed) |
| 7 | condition R (J, Alt, DA at k0, n = 250; trace 64 traj) | 3 x 250 x N0 + 64 x 624 | about 76,000 |
| 8 | k = 1 identity check at scale | 2 x 64 x 384 | 49,000 |

    GPU hours = (sum of passes) x t_b / 3600  +  n_scored x t_e / 3600  [+ probe passes at t_f instead of t_b if G1 requires fp32]

Totals under the defaults: stages 0 to 3c (everything needed for H-A and the primary H-B contrast) are about
583,000 passes (stages 1, 2, 3a, 3b, 3c and 8; stage 1b is extra and adds 45,000), i.e. 583,000 x t_b / 3600 hours: 4.9 h at t_b = 0.03 s, 9.7 h at 0.06 s,
19 h at 0.12 s. All stages: about 1.46 million passes, i.e. 12 h, 24 h or 49 h at the same three values of t_b.
t_b is not known: rough arithmetic for a 1.4B model on 384 tokens gives about 1.1 TFLOP per sample-pass, so on the
order of 0.05 to 0.1 s at 10 to 20 effective TFLOP/s [I]; the primer's own estimate of 6 to 10 hours for a smaller
design implies the lower end. If the image side is 512 px (1,024 tokens, 1,152 positions) multiply the pass time
by about 3 and re-derive k0. Evaluation: n_scored about 20,000 images and captions under CLIP (cheap), VQA subset
about 3,000 pairs, KID and CLIP-IQA about 20,000 images; set t_e from the pilot; expected under 2 h.
Stages 4 and 5 run only if stop rules 3 and 4 allow; stages 6 and 7 are optional, run in that order if budget
remains. No training stage exists in this card (no small fine-tune, no scale-up). A hard stop at 40 GPU-hours
needs the orchestrator (11.6).

## 13. What the review (Paper 1) states under each outcome

Statements are restricted to the checkpoint, geometry, value rule and metric tested, and say "on UniDisc 1.4B
under plain sampling at temperature 1". Until this card is signed and run, P5 stays an open problem with the
evidence it needs, as in framework-v2 D4.

| Outcome | Paper 1 states |
|---|---|
| H-A positive, H-B positive, H-C supported | A measured cross-modal dependence trace, front-loaded and on object words, and a schedule built from it that beats joint commitment at matched passes by at least 1 CLIP-lift point; the trace predicts where separation helps. Credits the identity to its sources; claims the measurement and the paired comparison, not the idea of dependence-aware scheduling (novelty audit pending). Notes the 12 GB-scale, single checkpoint, single metric family limits |
| H-A positive, H-B null | Cross-modal dependence is measurable and front-loaded but co-committing it costs less than 1 lift point at the k tested; the identity holds, the cost is small on this model; the schedule lever is not worth its passes here |
| H-A negative (flat or late), H-B positive | Separation helps but not through the front-loaded dependence the review predicted; the mechanism claim is withdrawn; the within-modality explanation is raised (DA-low and text perplexity reported) |
| H-A and H-B null | P5 is a measured small effect on one checkpoint; removed from the open problems list with the numbers; no generalisation |
| H-B reversed (J better) | Joint commitment is at least as good as separation at matched passes on this model; bidirectional context benefit exceeds the cross-modal cost; consistent with the direction of MMaDA-Parallel Table 10 but with matched passes and one set of weights, so it no longer carries that paper's confounds. P5b is reported as contradicted on this checkpoint |
| H-C not supported or not tested | S_theta is a descriptive trace; the review does not use it to select schedules; it still reports I_inc to show why the one-pass reference is unusable |
| Any gate fails | The estimator's validity is not established on a real network; the review keeps the estimator as a stated proposal with its toy verification only, and reports that the real-network checks failed |

Whatever happens, the review reports the cost of the measurement (R k passes per probe) and that S_theta is
the text-first and image-first split of the model, not the data law's cross-modal term.

## 14. Risks the red-team should attack first

1. Padding and EOS: if most of the 128 text positions are padding, confidence ranking commits them first and the
   "tokens per pass" accounting is dominated by uninformative commits (setup item 1).
2. Whether the unconditional joint distribution of this checkpoint gives captions that CLIP can score above the
   shuffled baseline at all (dynamic-range gate).
3. Whether pure passes (k text tokens at once, three times the joint rate) are so costly within modality that
   Alt and DA lose for reasons unrelated to P5; DA-low and window arms are the only controls.
4. The sequential joint draw uses the model's own chain; G5 tests order dependence only on a subset.
5. H-C has 16 cells and noisy Delta; it may be untestable by design.
6. The primary metric is a single CLIP model; VQA-type scores are secondary and on a subset.

## 15. Deliverables of the run

`runs/EXP-001/{pilot,profile,haconfirm,arms,windows,dose,condG,condR}/` each with config, seeds, git SHA of the
code, per-sample outputs, probe arrays, logs; `runs/EXP-001/da_windows.json` with hash; analysis scripts under
`analysis/EXP-001/` that regenerate every table; a verdict file per stage. Ledger rows (hypotheses H-A, H-B,
H-C; experiment EXP-001) are added only after both signatures, by the orchestrator.

## 16. Sign-off

| Role | Check | Status |
|---|---|---|
| statistician | sections 10 and 11: tests, multiplicity, interval method, sample-size rule, extension rule, outcome classes | unsigned |
| red-team | sections 1.4, 5, 8.7, 8.8, 9, 14: confounds, controls, estimator validity, attack on DA | unsigned |
| lab-engineer | section 3 filled, plan generator tested, G0 passes, cost measured | pending |
| gate-auditor | stage verdicts against this card | pending |

## 17. Change log

- v0.1 (2026-10-14): first draft by experiment-designer; nothing frozen. Pre-freeze amendments allowed:
  filling section 3, the k grid and window divisibility of 5.1, package pins of section 7, the sample-size rule
  output of 10.4. Any other change after signing creates v0.2 with a dated entry here.
