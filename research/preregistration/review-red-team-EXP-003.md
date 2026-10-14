```yaml
agent: red-team
date: 2026-10-15
brief: One-round hostile review of research/preregistration/EXP-003-value-rule-consistency.md (v0.1, unsigned) before any GPU time; problems only.
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-003-value-rule-consistency.md (in full)
  - research/ledgers/decisions.jsonl (D0014 to D0016, last three rows)
  - research/review/framework-v2.md section B (lines 28-63)
  - runs/env-2026-10-14/setup.md (sections 2.1 to 2.5, licence table)
  - models/third_party/unidisc/model_eval.py (L1737-1900 get_cfg_weight and _ddpm_forward; L2268-2300 and L2330-2436 _sample loop; L2960-3105 adap_sche and _maskgit_update)
  - exp001/unidisc_net.py (L134, sigma handling), exp001/estimator.py (float64 header)
  - runs/EXP-001/gates/verdict-pgv-rung1.json (aggregates only; rung2 file not parsed here, its numbers are taken from the card)
  - own CPU scripts: analysis/framework/redteam_exp003_commit_order.py (+ .log), analysis/framework/redteam_exp003_quality_coupling.py (+ .log)
coverage: >
  Card read in full. Code read at the lines named; the UniDisc paper, the EXP-001 card, any generated image, per-sample VLM values and the rung-2 verdict
  JSON were NOT read (the latter failed to decode under the default codec and was not retried; card values are used where cited). The UniDisc checkout is the
  one in models/third_party/unidisc; its commit was not re-verified here. Scripts are toy/sketch models (E4 only as to what the script computes, not as to
  UniDisc behaviour). No GPU used; no existing file edited; no ledger rows written.
claims:
  - statement: "Lambda_d can be +0.07 to +0.18 with zero noun-specific text-image link when a sample-level latent raises both text richness and the VLM's yes-propensity on the sample's own image."
    status: supported
    evidence: analysis/framework/redteam_exp003_quality_coupling.log (toy model, ratio-of-sums exactly as card 4.1)
    level: E4 (toy)
    confidence: 0.9
  - statement: "In the official sampler CFG's unconditional branch masks only the original conditioning positions (x0_unmask), not committed tokens; guidance therefore contrasts with-prefix against without-prefix and the card's mechanism text in 1.2 is wrong."
    status: supported
    evidence: model_eval.py L1763 and L1769 (x_uncond = x.clone(); x_uncond[x0_unmask] = mask_index); x0_unmask forwarded unchanged by _sample (L2370 area, update call with x0=x0, x0_unmask=x0_unmask) and restored by torch.where(x0_unmask, x0, x) after each step
    level: E3
    confidence: 0.9
  - statement: "Under the official maskgit sampler at 32 steps the tail is not committed ahead of the image: with the measured entropies (text 5.0, image 6.5 nats) the sketch gives mean normalised commit time 0.57 (tail) against 0.63 (image) and 29 percent of tail tokens before the first 25 percent of image tokens (24 percent expected with no preference)."
    status: mixed
    evidence: analysis/framework/redteam_exp003_commit_order.log; schedule arithmetic exact (1, 8, 12 ... 52 tokens per step), entropies from one state only, Gamma shape assumed
    level: E3/E4 for the schedule, E0 for the commit order
    confidence: 0.6
competing_explanations:
  - sample-level quality / yes-propensity coupling (F-1)
  - image diversity collapse under CFG bounding any seed-driven link (F-7)
  - prefix-conditioning strength changes only (F-3)
unknowns: [real size of image-detectability and text-richness coupling on G; whether tail precedes image in O0; whether the plain wrapper and the official forward give identical marginals on the same state (sigma None versus sigma_t)]
next_test: {hypothesis: "none proposed (red-team gives no fixes)", intervention: "n/a", primary_metric: "n/a", falsifier: "see Rejection conditions", gpu_hours: 0}
```

# Red-team review of EXP-003 v0.1 (one round)

Note on the brief: the brief asks for a minimal fix per finding. The red-team role forbids proposing fixes. Each finding therefore gives a **clears if** line, which is an observable acceptance condition, not a design.

## Verdict: **do not run as written** (2 fatal, 5 major, 5 minor). "Sign after fixes" becomes possible only after F-1 and F-2 have a recorded resolution in the decision ledger. Both are statistic-and-wording problems, not cost problems, so the GPU budget and run order are not the obstacle.

Counts: fatal 2, major 5, minor 5.

---

## FATAL

### F-1 (fatal). Lambda_d can be positive with no noun-specific link, and no control in the card can see it
**Attack.** The card asserts (4.1, "Why this statistic") that image sharpness and checker bias "enter both terms" and cancel. They cancel only if sharpness is independent of which nouns are discordant. It is not. Discordance is defined through the sibling's text: n is discordant for (p, e) when the sibling's completion lacks it. A sibling whose completion is short, empty, debris, or pad-heavy makes every noun of the own completion discordant. In a joint sampler a degenerate completion and a degenerate image plausibly share a cause (a bad early commit, a "texture" mode, an early pad commit). Then the discordant instances come disproportionately from (own = rich text, sharp image) paired with (sibling = poor text, mushy image), and y(own) minus y(sibling) is positive for every noun, because a sharp image earns more VLM yeses for any noun. No noun-specific link is involved.

**Evidence.** `analysis/framework/redteam_exp003_quality_coupling.py` implements the card's estimator verbatim (ratio of sums over discordant nouns, own minus sibling image) on a model in which a noun's identity never influences the image. Result (log in `.log`):

| text-richness coupling | image-detectability slope | Lambda_d |
|---|---|---|
| 0 | 0 | -0.002 |
| 0.5 | 0 | +0.001 |
| 0 | 1.0 | -0.002 |
| 0.3 | 1.0 | +0.070 |
| 0.5 | 1.0 | +0.118 |
| 0.5 | 2.0 | +0.176 |

Either coupling alone gives zero; both together give a value at or above the MEI of 0.10. The data already say the detectability term is large: in the card's own EXP-001 numbers the VLM says "present" for 0.213 of nouns in images of other prefixes on texture-like images, and the PC-F note in D0016 gives s_real = 0.47 on real images with shuffled partners. Yes-propensity is a big image-level property, not a small one.

**Why every control in the card misses it.** NC-1 (Ind) generates text and image in independent passes, so there is no shared sample-level latent by construction; Lambda_d(Ind) = 0 cannot test it. PC-1 (TF) adds a true link and would also carry the coupling, so TF minus Ind is inflated. PC-2 is a cross-caption contrast on a different sampler. W1 (CLIP completion-only sibling link) has the same confound: a sharper image has higher cosine with any caption. The composition sensitivity (4.3 item 8) restricts to COCO-category nouns, which does not separate noun-specific from sample-level effects either.

**Cheapest alternative explanation for a positive Delta1:** G's images vary more in quality across seeds than P64's (CFG changes the sharpness distribution), and text richness covaries with that, so G has a larger quality-driven Lambda_d.

**Clears if:** a same-image placebo (the identical statistic computed on nouns that do not belong to the sample, matched on frequency and discordance construction) is shown on the G arm to be within noise, and Delta1 is stated net of it, or the claim wording drops "completion-specific".

### F-2 (fatal). The headline null row asserts something the null test does not test
**Attack.** The null class is a statement about the **difference** Delta1 = Lambda_d(G) minus Lambda_d(P64), 90 percent interval inside (-0.10, +0.10) (section 5). The bold row of section 10 states: "Guidance does not create a completion-specific link either. The joint text-image consistency of the guided sampler is carried by the observed prefix ... not by co-generation." That requires the **absolute** links to be near zero. If Lambda_d(G) = Lambda_d(P64) = +0.30 the card classes the result "null" and prints a false sentence. The parenthetical "(the sibling-referenced link is within (-0.10, 0.10))" is not a tested quantity: no rule in 5 or 7 requires Lambda_d(G) itself to be inside the band.

The EXP-001 rung-2 gate gave a per-noun matched-minus-same-prefix gap of 0.07 under plain sampling (card 4.1), so P64 is itself not shown to be zero, and a null difference does not make G's link zero.

A second gap in the same sentence: "not by co-generation" is inferred from a within-prefix, seed-to-seed contrast. If CFG shrinks seed-to-seed image variation (F-7), a joint dependence that is carried by the prefix **and** by the completion is not visible in a sibling contrast of near-identical images. The statistic measures how much of the seed-driven variance passes between modalities, not whether the model co-generates.

**Result that forces rejection of the wording:** Lambda_d(G) interval excluding (-0.10, +0.10) while Delta1 falls in the null class.

**Clears if:** the null wording is conditioned on a test of Lambda_d(G) and Lambda_d(P64) themselves, and on image seed-diversity not being collapsed on G.

---

## MAJOR

### F-3 (major). The guidance mechanism in 1.2 is contradicted by the code
**Attack.** Card 1.2: "the conditional branch contains every committed token, so guidance can amplify the dependence of uncommitted image tokens on committed completion words". In `_ddpm_forward` (L1763-1769) `x_uncond = x.clone(); x_uncond[x0_unmask] = mask_index`. `x0_unmask` is the fixed set of conditioning positions passed unchanged through `_sample` (restored after each step by `torch.where(x0_unmask, x0, x)`). So both branches contain every committed completion token and every committed image token; the only thing removed in the unconditional branch is the **prefix**. Guidance in this experiment is, by construction, "with prefix minus without prefix": prefix-adherence guidance. It has no term that targets the completion-to-image dependence.

Consequences. (1) The designer's concern (guidance raising Lambda_d through the prefix) is not a side risk but the defining action of G; a positive Delta2a cannot be worded "guidance creates a completion-specific link" on mechanism, and the mechanism paragraph (1.2) and the 1.3 distinction ("the model's value of the other modality") are wrong as written. (2) The weight is cfg x (1 - t): zero at the start, 3.0 at the end, which is exactly when the arccos schedule commits about 48-52 tokens per step (script log), so guidance is applied hardest to the largest parallel batches. (3) A silent failure: if the engineer's joint runner forgets to pass `x0`/`x0_unmask` (prefix inserted by building `x` only), the guard `x0_unmask is not None and x0_unmask.sum() > 0` is false, no guidance is applied, G becomes O0 and costs one call. The card checks neither that G's marginal differs from O0's on a real state nor that the second call occurs.

**Clears if:** the card's mechanism and Section 10 positive row describe G as prefix-removal guidance, and a run-time assertion shows guidance acted (marginal differs from O0 at the same state).

### F-4 (major). O0 is not a clean control for "the value rule"; the ordering premise is unsupported
**Attack.** Position rule and schedule are not value rules in the project's own framework (framework-v2 B: V is the value slot; rho is the position law). Delta2b (O0 minus P32) bundles selection by drawn-token probability, pooled text-and-image ranking with Gumbel noise, an arccos schedule with up to 52 tokens per step against 33 uniform, different RNG (global torch/numpy multinomial on bf16 probabilities against float64 inverse CDF), and a possible difference in the network input (`sigma=None` in `exp001/unidisc_net.py` L134 against `_sigma = sigma_t` unless `trainer.force_null_sigma`; the config shows that key true for the inference experiment and false in the base config; the card does not say which is in force, and does not check that the P and O0 first-step marginals on one state agree). The card admits the bundle (section 2) and then still lets Section 10 hang "the census point" (value rule) on Delta2b: "Positive ... Delta2b ... 'the official sampler's selection, ordering and schedule, not guidance'". That is not a value-rule finding.

The premise in 1.2 that the official sampler commits text earlier is not supported by the numbers the card cites. With text entropy 5.0 and image 6.5 nats and the Gumbel scale r_temp x t = 4.5 at the start, the ranking is mostly noise early: my sketch (`redteam_exp003_commit_order.log`) gives mean normalised commit time 0.574 for the tail against 0.631 for the image, and 29 percent of tail tokens committed before the first quarter of the image (24 percent with no preference). The sketch is crude (Gamma shape assumed, one measured state), but it shows no reason to expect "text first". The only evidence in the card is the optional commit-order record (4.3 item 9, "if possible"). Without it the narrative for O0 minus P32 and any "the tail sees the image" or "the image sees the tail" attribution is unfounded, and the direction of any link is unknown (the positive control PC-1 exercises text to image only).

**Clears if:** Section 10's census-point sentence is dropped from Delta2b rows, and the commit order is a required output rather than "if possible".

### F-5 (major). The controls do not test the contrast the primary statistic makes
**Attack.**
- **NC-1 pass criterion is non-rejection.** Pass = the 95 percent interval of Lambda_d(Ind) contains 0, with 48 clusters and the card's own sigma 0.45 (SE about 0.065, half-width about 0.13). A pipeline bias of the size of the MEI (0.10) passes. A pass is not evidence of absence at the scale the card cares about. The card also says a pass has probability 0.95 "if the pipeline is unbiased", which is a size statement, not a power statement.
- **PC-2 tests the easy contrast.** It compares own-caption against another-caption images (cross-prefix), where VLM presence differs by a lot; Lambda_d needs the checker to separate two images that share the prefix and differ in seed. A VLM that passes PC-2 can still be flat on that within-prefix contrast. Thresholds (0.60, 0.25) are chosen now ("[A]") on 32 images with no interval.
- **PC-1 runs on plain-sampling images, not the guided ones** (open item 3 in the card). The card's own concern that guided images are more object-like (measurement-range effect) is exactly the case PC-1 cannot cover. There is no positive control on G images.
- W2 lets a "null" label stand when these three pass.

**Clears if:** each control has an acceptance rule at the scale of the MEI and is run on the arm and contrast it licences.

### F-6 (major). Outcome-to-wording rules turn non-significance into a statement about the other arm
**Attack.**
- "Positive" needs only p <= 0.05 and d > 0 (section 5); the MEI is used only to say "at or above". The Section 10 positive row then prints "plain sampling at the same number of network calls does not" and "Guidance itself ... accounts for the difference" for any positive d, including d = 0.03. P(positive) at a true 0.05 is 0.28 (card's own table).
- "plain sampling ... does not" needs Lambda_d(P64) to be tested near zero; it is only a component of the difference.
- W4: "Delta2a positive after Holm and Delta2b not positive" is worded "guidance itself". "Not positive" includes inconclusive. Holm second-step power at a true 0.10 is 0.68 (card), so about a third of true-0.10 Delta2b cases fall into "not positive" and are written as "guidance itself, not the sampler".
- W1 passes with a 90 percent lower limit above 0 on a CLIP contrast that shares F-1's confound; no effect-size floor.
- W3 is opaque in direction: a small COCO-noun contrast is read as "may reflect noun composition", but under independence composition cannot create a positive Lambda_d (it only rescales it), so the rule attaches the wrong cause.

**Clears if:** each sentence in Section 10 maps to a tested statement (equivalence, not non-significance, for every "does not").

### F-7 (major). Seed-diversity collapse under CFG bounds the statistic and is not a gate
**Attack.** The card lists diversity as a competing explanation and a descriptive item (4.3 item 7, H4), but the decision rules ignore it. If G's images are nearly identical across the two seeds of a prefix, y(n, own) minus y(n, sibling) is bounded near zero for every n regardless of what the model does with the completion, and the null class is reached through the instrument, not the model. The only guard (guardrail iii: discordant nouns >= 0.4 x P64) concerns text, not image diversity, and guardrails are read with a positive Delta1 only (4.4), not with a null. W2's controls are all on plain-sampling arms, so none can be reached by a collapsed G.

**Clears if:** the null rule includes a measured image seed-diversity floor on G.

---

## MINOR

### F-8 (minor). Matching by network calls and the 32-step choice
G (32 steps, 65 calls) is compared with P64 (64 steps, 64 calls). Calls are not the quantity that governs dependence between co-committed tokens; the number of tokens committed per step and the order are. The arccos schedule at 32 steps commits 47-52 tokens per step at the end against 16.5 uniform in P64 (the shipped 50-step schedule commits at most 35). Statement (2) of section 2 ("a positive for G is the conservative finding and a null is the stronger null") is asserted, not shown: P64 minus P32 is unmeasured and may be zero or negative. G at 32 steps with CFG 3.0 is not the shipped setting (50 steps); the scope sentence says 32, but the title question ("official guided sampler") is read by a reader as the shipped one. **Clears if:** the claim names the configuration as a variant and not "the official sampler".

### F-9 (minor). Power rests on an unmeasured sigma
Sigma 0.30 per arm is taken from the OR-rule statistic's 90 percent interval over 24 clusters and is assumed to carry over to a per-discordant-noun ratio with many zero-discordant prefixes under G. The pilot gives 16 clusters and cannot change the cap n = 150. Achieved MDE 0.119 exceeds the MEI 0.10 at power 0.90, so a true effect at the MEI is "positive and >= 0.10" only half the time (0.50 in the card's table), and a Paper 1 table can be dominated by "inconclusive".

### F-10 (minor). Measurement details
Discordance is by surface key (synonyms and hypernyms count as different nouns; "dog" against "puppy"); spaCy tagging on debris tails; word-initial sub-tokens as nouns; one Qwen3-VL-2B prompt at a hard 0.5 threshold; binary y loses the graded P(yes) on which an image-level propensity shows most clearly (F-1). None alone is fatal.

### F-11 (minor). Numerical precision differs by arm
Official path with `force_bf16_eval`: the guided logits (1 + w) x logit_c - w x logit_u with w up to 3 are formed in bf16 (resolution 0.06-0.12 at logit magnitudes 16-32, amplified by (1 + w)); plain arms use float64 arithmetic after the forward. The G arm therefore carries an extra rounding noise that O0 and P do not. Size not measured.

### F-12 (minor). Licence
UniDisc code and checkpoint carry no licence (setup.md 2.2, 2.3). The card handles figures. It does not cover: release of generated completions, token files and per-image presence matrices (deliverables in section 11 list "presence matrices as JSONL" and per-stage outputs); redistribution of `exp003/` code that wraps or patches `model_eval._sample` through a pre-hook; or that, without any image release, a reader cannot see the "texture-like images" on which the plain-sampling premise rests. COCO captions and the Qwen/CLIP pins have their own licences not checked here.

---

## What I attacked and found sound (so it is not re-opened)
- The identification of Lambda_d = 0 under independent seeds given the prefix (exchangeability of own and sibling image) is correct as an expectation statement; the damage is F-1 (sample-level coupling), not the algebra.
- Identity Delta1 = Delta2a + Delta2b + (Lambda(P32) - Lambda(P64)) checked by hand.
- Fresh-pool disjointness and the pilot firewall are plausible as written (not run).
- `eval.cfg = 0` gives a single pass in the code (get_cfg_weight returns 0; `(_w > 0).any()` false).

## Rejection conditions (results that would force rejection of the claim)
1. A same-image placebo-noun Lambda_d on the G arm at or above about 0.05 (F-1).
2. Lambda_d(G) or Lambda_d(P64) outside (-0.10, 0.10) while Delta1 is in the null class (F-2).
3. G image sibling-cosine above P64's by more than the sampling noise with Lambda_d(G) near 0 (F-7).
4. G and O0 first-step marginals identical on a prefix state, or G costing one call per step (F-3).
5. Commit-order record showing the tail committed on average no earlier than the image in O0 (kills the ordering story behind Delta2b, F-4).

## The one analysis whose absence would cause rejection
A same-image placebo for the primary statistic: the identical ratio computed with nouns drawn from other prefixes' completions (matched on count and on the discordance construction), in every arm. Without it, a positive Lambda_d cannot be separated from sample-level image quality or VLM yes-propensity, and a null cannot be separated from collapsed seed variation.

## Open for the orchestrator
- Fatal items F-1 and F-2 block the gate until a resolution row is recorded in the decision ledger. I wrote no ledger rows.
- Scripts left for reproduction: `analysis/framework/redteam_exp003_commit_order.py`, `analysis/framework/redteam_exp003_quality_coupling.py` (with `.log` files). They are toy models; they establish possibility (F-1) and a sketch (F-4), not UniDisc behaviour.

---

# v0.2 check (2026-10-15; card commits a0073e1 and 8accefe; scripts `analysis/framework/redteam_exp003_balanced_check.py` + `.log`)

**Verdict: NOT SIGNED. Four remaining conditions (R1 to R4); R1 and R2 block signature. F-1 is reduced from fatal to major; F-2 is cleared; F-3, F-4, F-6, F-7, F-8 are cleared except as noted.**

## Toy rerun (CPU, 12,000 prefixes per row; se about 0.003)
| scenario (true noun link 0 unless stated) | Lambda_d (v0.1) | Lambda_b (v0.2) | placebo (NC-2) |
|---|---|---|---|
| no coupling | -0.004 | +0.000 | +0.006 |
| additive yes-bias, text richness coupled (the v0.1 toy) | +0.124 / +0.173 | +0.001 / +0.005 | +0.002 / -0.002 |
| non-additive: yes-prob rises with quality x noun detectability, quality also shifts which nouns are mentioned | +0.143 / +0.214 | **+0.054 / +0.162** | -0.007 / -0.000 |
| same, image-level bias term zero | +0.140 | **+0.155** | -0.003 |
| true link added (additive coupling kept) | +0.242 | +0.125 | -0.003 |

Reading. Lambda_b removes the **additive** bias exactly, as the card says (F-1 as I built it is cleared), and keeps a real link (the true-link row is not attenuated to zero). But when the bias is not additive (a sample's quality changes both which nouns its text names and how findable those nouns are in its own image), Lambda_b stays at +0.05 to +0.16 and **NC-2 reads about 0**. The placebo cannot see it, because placebo nouns are by construction not selected by the sample's own text, so they do not carry the text-mention / image-findability coupling. The card's sentence that NC-2 "measures what remains of image-level bias after balancing (non-additive bias, yes-rate interacting with noun class)" is false for this case. (This is a toy; whether UniDisc has the coupling is unknown. It is a class-level dependence through a shared latent, arguably real text-image consistency, but it is not a completion-specific noun link, and the card words it as one.)

## Condition-by-condition ("clears if" of each finding)
- **F-1: partly cleared.** Additive bias cancelled (toy). NC-2 does not bound the non-additive residual. See R2.
- **F-2: cleared on the test side** (per-arm 90 percent intervals, NC-2, diversity floor, W5 scope). One residue: the null sentence still ends "joint text-image consistency ... is carried by the prefix, not by co-generation"; nothing tested shows the prefix carries the consistency (the prefix gap is descriptive only, 4.3 item 3). See R3.
- **F-3: text cleared; the assertion is wrong.** Card 1.2 says that at the first step of every G unit the guided marginals must differ from O0's by more than 1e-3. At step 0, t = 1 exactly and w = cfg x (1 - t) = 0, so `(_w > 0).any()` is false, no second call is made, and the guided marginal equals O0's. As written the assertion fails every G unit (or is satisfied only by noise). It also means G makes 64 calls, not 65. See R1.
- **F-4: cleared** (Delta2b rows carry no value-rule claim; commit order required with a token-identity hook check).
- **F-5: not addressed.** The diff touches only the NC-1 half-width rule. PC-2 is still a cross-caption contrast on a different sampler; PC-1 is still plain images only; open item 3 stands; thresholds still [A] on 32 images. NC-1 and NC-2 now have half-width limits, which is an improvement; the sensitivity of the instrument to **within-prefix** differences on **guided** images is still not tested. See R4.
- **F-6: cleared** (W4, W5, Section 10 rows now map to tested statements; hypotheses tested against 0). W1 and W3 unchanged: W1's CLIP bar shares the quality confound and is a lower limit above 0 only; minor.
- **F-7: cleared in form** (sibling CLIP cosine below 0.92 and Jaccard below 0.80 on G). The thresholds are [A] with no P64 reference value; if P64 also exceeds them the floor blocks every null by construction; minor.
- **F-8: cleared** (named "32-step variant").
- **Stale text (minor):** the YAML header `next_test` still reads "primary_metric: discordant-noun link Lambda_d" and the falsifier lists NC-1, PC-1, PC-2 without NC-2; Section 10 (E3-H4 row) not rechecked.

## Remaining conditions
- **R1 (blocks signature).** The guidance assertion must not be evaluated at a step where w = 0 (step 0, t = 1); it must name a step with t < 1, and the call-count arithmetic for G (64 or 65) must follow.
- **R2 (blocks signature).** State that NC-2 bounds only additive and noun-class-independent bias, drop the sentence claiming it measures the non-additive part, and word a positive Lambda_b as a noun-level dependence that may include quality-mediated class-level coupling (the toy reaches +0.16 with zero noun link and a clean placebo). W1 and the Section 10 positive rows use "completion-specific link"; that term is not licensed by Lambda_b alone.
- **R3.** The null sentence's last clause ("carried by the prefix, not by co-generation") is not supported by any tested quantity; limit it to what is tested (no seed-specific noun link larger than 0.10 among discordant nouns).
- **R4.** The PC-2 and PC-1 mismatch (cross-caption, plain images) is carried over from F-5; either record it as an accepted limitation in the wording of W2 or test the contrast it licenses.

Rejection conditions 1 to 5 above stand, with condition 1 now read on the **non-additive** placebo as well: a Lambda_b above 0.05 in G with a clean NC-2 is not distinguishable from quality-mediated class-level coupling.
