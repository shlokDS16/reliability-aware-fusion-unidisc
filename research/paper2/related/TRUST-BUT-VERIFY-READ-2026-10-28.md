```yaml
agent: paper-reader
date: 2026-10-28
brief: Full forensic read of "Trust but Verify" (arXiv 2610.22380) as closest prior art to GATE; baseline-port verdict; delta; pre-emption check of spec 2.1
sources_examined:
  - arXiv:2610.22380v1 (PDF, 10 pages, whole text incl. Appendix A; PDF at research/sources/pdfs/2610.22380.pdf, markdown at research/sources/md/2610.22380.md; pages 4-6 also checked as rendered images for Eq. 1-4, Alg. 1, Tables 1-2)
  - arXiv abs page 2610.22380 (comments, history)
  - GATE-METHOD-SPEC-v2-2026-10-28.md lines 98-142, 160-187
  - UniDisc code, local nested checkout models/third_party/unidisc at SHA 3ee3e47a9e64bac2fdca59957726f14723371ced: model.py lines 621-660 (_subs_parameterization), 674-690 and 780-788 (forward, return_logits), 960-1000 (loss); configs/config.yaml (time_conditioning False)
  - exp001/unidisc_net.py lines 120-140 (the GATE wrapper)
coverage: >
  Paper: every page, all sections, all four tables, Fig. 1 (Alg. 1), Fig. 2 caption, limitations, reference list scanned. Fig. 2 plot
  content itself not inspected (caption read). No appendix beyond Appendix A (Table 4). NO code, checkpoint, preregistration or
  data link exists in the paper or on its arXiv page (only v1; one author). A GitHub repo search for the title returned 0
  hits (a weak check, not proof of absence). So no code audit of the paper was possible; implemented loss/sampler/eval cannot be
  checked against Eq. 3 or Alg. 1.
claims:
  - statement: "TbV's detection score (Eq. 4) is the model's probability of the observed context token at its own position, where that token is present (unmasked) in the input."
    status: supported
    evidence: "p.4 Eq. 4 (s_i = p_theta(x_i^0 = x~^i | .), i in K) with Alg. 1 p.5 ('predict p(.|r) at all positions', K = observed context, H masked); Eq. 3 p.4 trains CE at i in K given x~; Sec 2 p.3 and Sec 4.2 p.6 speak of 'observed positions'. The conditioning inside Eq. 4 is the dot only (unspecified); it is the current canvas r."
    level: E2
    confidence: 0.9
  - statement: "TbV's threshold is hand-set heuristics, neither calibrated nor learned: tau annealed 0.5 to 0.1, t_lock 0.5, budget B = ceil(0.15 |K|), lambda 0.25 'set once and not tuned'."
    status: supported
    evidence: "p.4 Sec 3.3 and 3.4; p.8 'fixed heuristics'; no guarantee, no calibration set"
    level: E2
    confidence: 0.9
  - statement: "The abstract/intro headline of 0.96 recall at 0.91 precision is in-distribution detection of the training noise kernel (arm D trained with uniform mixing, tested on uniform corruption), and its detection numbers appear only in running text, not in a table."
    status: mixed
    evidence: "Abstract p.1; Sec 4.2 p.6 (arm D, uniform rho=0.1, recall 0.959 [0.954,0.963], precision 0.909, false-edit 1.07%). The paper states only that PLAUSIBLE corruptions are out-of-distribution (p.5). Table 2 covers the plausible cell only."
    level: E2
    confidence: 0.85
  - statement: "'Base model assigns roughly 50% probability to uniform-random garbage' is reported but not evidenced by any table or figure, and no protocol (positions, rate, conditioning) is given."
    status: unknown
    evidence: "Abstract p.1; Sec 1 p.2; Sec 4.2 p.6. Not in Tables 1-4 or Fig. 2 caption. Table 2 'base' row has no detection columns."
    level: E2
    confidence: 0.8
  - statement: "TbV's 'arm B detects almost nothing' (the support for 'no meaningful likelihood') rests on one operating point (plausible rho=0.1, recall 0.035), on a vanilla-SFT model, not on the pretrained base model the ~50% statement is about; no threshold-free score metric (AUROC) is reported for any arm."
    status: mixed
    evidence: "Table 2 p.6 (B: P 0.572, R 0.035, false-edit 0.29%); Sec 4.2 p.6; Table 4 p.10 shows B within +0.2 F1 of A on uniform 0.1/0.3 (0.268 vs 0.266) which is consistent with near-zero edits but is not a detection metric"
    level: E2
    confidence: 0.8
  - statement: "Plausible corruptions are only partly detectable even with finetuning: recall 0.150 (D), 0.350 (DP), 0.035 (B) at the headline cell; infill gain not significant (D-A +0.38 [-0.36,+1.09]; DP +0.51 [-0.26,+1.28])."
    status: supported
    evidence: "Table 2 p.6 and caption; Sec 4.2 p.6 ('two thirds of plausible corruptions go undetected'); abstract p.1 ('not statistically significant')"
    level: E2
    confidence: 0.9
  - statement: "Abstract's 'false-edit rate under 0.4% on clean context' holds only for the mixture-trained arms on fully clean passages (0.07 to 0.39%); in corrupted passages the false-edit rate is 0.83 to 1.84% (D, DP, E up to 1.82%) and the rate itself is never defined by numerator and denominator."
    status: mixed
    evidence: "p.6 Sec 4.2 Repair (H1) 'between 0.07% and 0.39% for the mixture-trained arms'; Table 2 false-edit column; p.5 Metrics ('false-edit rate on clean tokens, our primary safety metric'); the rho=0 per-arm values are not tabulated"
    level: E2
    confidence: 0.8
  - statement: "No code, checkpoint, or preregistration record is available for TbV; the 'pre-registered' gates cannot be checked."
    status: unknown
    evidence: "no link in text (grep for http/github finds only OpenWebText); arXiv abs page lists comments and v1 only"
    level: E2
    confidence: 0.75
competing_explanations:
  - "TbV's arm B failure may be partly caused by the annealed threshold sitting at the very probability (about 0.5) the pretrained model gives to garbage, plus the edit budget; a score-level AUROC would separate 'no signal' from 'signal but badly thresholded'. The paper does not provide it."
  - "TbV's plausible-corruption generator, its EXT detector and its judge are all GPT-2-family; the judge NLL gain of DP (2.902 vs 3.237) may partly reward GPT-2-like fluent repairs."
unknowns:
  - "Order in which context positions are tested inside Alg. 1 while the budget runs (position order or lowest s_i first): not stated."
  - "Functional form of tau(t) between 0.5 and 0.1 (linear? over t in [1, 0.5]?): not stated."
  - "Whether detection CIs are bootstrapped over tokens or passages (the CI [0.954, 0.963] is narrow for 256 passages; F1 CIs are passage-level): not stated."
  - "Whether UniDisc raw logits at observed positions carry signal (spec U7): not answered by this paper; needs a measurement."
next_test:
  hypothesis: "On UniDisc 1.4B, the raw (pre-SUBS) probability of an observed image token carries little corruption signal, while the mask-then-score statistic does (this is arm B versus GATE)."
  intervention: "Score the same clean and corrupted images with (i) raw pre-SUBS logits at unmasked observed tokens and (ii) GATE masked scoring"
  primary_metric: "threshold-free AUROC for planted token positions; plus recall at the clean-calibrated false-alarm level"
  falsifier: "AUROC of the raw unmasked score within 0.05 of GATE's, on every corruption family"
  gpu_hours: "about 0.05 (one extra forward pass per image; stored codes)"
```

# Trust but Verify (arXiv 2610.22380): forensic read for GATE

Evidence level for "the paper reports X": E2 (read in full, 10 pages). Level for the UniDisc code statements: E3 (local checkout at SHA 3ee3e47a, inspected; not run). Nothing here is E4.

## 0. Bottom line

1. Delta (headline): TbV needs a finetune to make the probability of an observed token informative and scores at the unmasked position with a hand-set threshold; GATE scores each token masked, in its own modality, with the other modality withheld, on an untouched pretrained model, with a risk-controlled threshold, and measures cross-modal verification. The mask-detect-refill loop itself is NOT new (TbV names it "detect-remask-refill", Alg. 1).
2. Baseline port: the spec's "Trust-but-Verify-style" baseline is a faithful port of the SCORE but not of the METHOD. It is TbV's arm-B analogue (observed-token score, no finetuning), which TbV itself reports as near-useless. It must be labelled that way, must read raw logits (the existing wrapper cannot), and should be reported threshold-free. Details in section 6.
3. Nothing in spec 2.1 is contradicted. Three things are pre-empted or at risk: "re-masking flagged tokens" (the loop), "bidirectional consistency as the reason masked scoring beats left-context detectors" (TbV hypothesises it, p.7), and the spec's one-line description of TbV in 2.4 which understates its training noise (it also used a hard-negative mixture, which gave the best plausible-corruption results).

## 1. Problem, model, training (paper-reported)

- Problem: corrupted conditioning (context) tokens in masked diffusion are treated as certain, because under the absorbing process an observed token has "infinite signal-to-noise" (Abstract p.1, Sec 1 p.2). Task evaluated: infilling of 1 to 4 contiguous hole spans covering 10 to 50% of a 512-token passage with a corrupted rest-of-passage context (Sec 3.2 p.3; Sec 4.1 p.5).
- Model: public MDLM 170M checkpoint pretrained on OpenWebText, GPT-2 tokenizer, finetuned on FineWeb-Edu (400k blocks of 512 tokens, about 205M tokens), 8,000 steps at batch 32 x 512, lr 3e-5 cosine, bf16, "identical seeds", one seed per arm (Sec 4.1 p.5; limitations p.8). Under 4.5 h per arm on a 6 GB RTX 3060 laptop GPU.
- Finetune design: "region-inhomogeneous" forward process. Holes H follow the absorbing kernel (mask with prob. t). Context K is substituted at rate eta per sequence with eta ~ 0.5 delta_0 + 0.5 U(0, 0.15] (Eq. 1, p.4), substituted token z ~ q_noise, z != x_i (Eq. 2). Ten percent of batches use plain pretraining loss. q_noise has two instances: (i) uniform over the vocabulary; (ii) "hard-negative mixture" of equal parts uniform, corpus-unigram, top-32 embedding-space neighbours of the true token, and masked self-proposals from the base model (p.4).
- Objective (Eq. 3, p.4): L = E[ (1/t) sum_{i in H} 1[x~_i = M] CE_i + lambda sum_{i in K} CE_i ], CE_i = -log p_theta(x_0^i | x~), lambda = 0.25 "set once and not tuned". The authors call it "a deliberate surrogate", not the variational bound. No auxiliary flag marks K as possibly corrupted (p.4). So the model is trained to output the CLEAN token at an observed (possibly substituted) position: the score of Eq. 4 is a trained output, not an incidental one.

## 2. Detection score, threshold, refill (exact)

Equations as printed (p.4; symbols checked on the rendered page):
- Eq. 1: eta ~ (1/2) delta_0 + (1/2) U(0, eta_max], eta_max = 0.15.
- Eq. 2: x~_i = [MASK] w.p. t (i in H); x~_i = z ~ q_noise w.p. eta, x_0^i otherwise, z != x_0^i (i in K).
- Eq. 3: loss above.
- **Eq. 4: s_i = p_theta( x_0^i = x~^i | . ), i in K.** "is a suspicion score for context." The dot (the conditioning) is not spelled out. From Alg. 1 it is the current canvas r (holes masked or partly filled, context as observed).

Masked or unmasked: **unmasked.** The observed token x~_i sits at position i in the model input; the model is asked for the probability that its own clean value equals that observed token. The paper never scores a context token after masking it (masking is the repair action, not the score). The literal phrase "unmasked position" does not occur in the paper; the meaning is established by Eq. 3, Eq. 4, Alg. 1 and the arm-B explanation "a model whose training dynamics never visit a wrong unmasked state" (p.6). Also, the score is recomputed at every reverse step on the evolving canvas (Alg. 1 "predict p(.|r) at all positions"), not once.

Threshold and how set (p.4, Alg. 1 p.5): while t > t_lock = 0.5, any not-yet-edited context token with s_i < tau(t) is set to [MASK] and moved into H, until the edit budget B = ceil(rho_hat |K|), rho_hat = 0.15 ("assumed corruption rate"), is spent. tau(t) is "annealed from 0.5 to 0.1". All constants are hand-set heuristics; none is calibrated or learned ("fixed heuristics", p.8). The authors state the step is not derived from the reverse dynamics (p.4, p.8). Past t_lock the context is frozen. A cheaper comparator ("frozen + read-out repair") keeps the context frozen and overwrites positions with s_i < 0.1 once at t = 0 (arms C and CP).

Refill: the re-masked positions are refilled by the ordinary reverse dynamics, 64 reverse steps, greedy commits (ceil(m/R) most confident per step, p.4). One detail they flag: context tokens must enter the low-confidence commitment rule with confidence s_i (not 1) or the sampler never revisits them. Unspecified: order in which positions are tested under the budget; the form of tau(t).

## 3. Experiments (paper-reported, with locations)

Data: FineWeb-Edu passages held out from documents 400k positions downstream (p.5). 13 evaluation cells, fully paired, 256 passages per cell: planted context-corruption rate rho in {0, 0.02, 0.05, 0.1, 0.2} crossed with {uniform, plausible} at 30% hole coverage, plus coverage {10%, 50%} at rho = 0.1 (p.5).

Corruption types: (1) uniform random substitution ("conspicuous"; same family as the C/D training kernel, so in-distribution for those arms); (2) "plausible": GPT-2 samples conditioned on left context, top-50, true token excluded; a generator disjoint from all training noise, so out-of-distribution for every arm (p.5). Rates 0 to 0.2.

Arms (Table 1, p.5): base (pretrained, frozen context); A (vanilla SFT, eta = 0, frozen); B (A weights plus the annealed sampler = inference-only); C and D (uniform-eta weights; C = read-out repair, D = annealed sampler); E (eta = 0.15 fixed, no zero component); CP and DP (hard-negative mixture; read-out vs annealed); EXT (GPT-2 left-context surprisal flags the top-k context tokens, k matched per sequence to DP's edit count, refilled by arm A).

Metrics (p.5 to 6): detection precision and recall over planted positions; correction accuracy (edited to the true token); false-edit rate on clean tokens ("our primary safety metric"); infill token-F1 per hole span, deltas in points with paired bootstrap 95% CI (10k passage resamples); judge NLL (gpt2-large on the completed passage); containment (infill accuracy by distance to nearest corruption); non-regression (clean-context metrics, held-out variational bound).

**Clean false-edit rate definition.** Only: "the false-edit rate on clean tokens" (p.5). Numerator and denominator are not stated. Inference (not stated): fraction of context tokens that were NOT corrupted but were re-masked by the sampler, per cell. Reported values: 0.07 to 0.39% "on fully clean context" for the mixture-trained arms (p.6), abstract "under 0.4%" (p.1); in corrupted passages it is higher (Table 2: B 0.29, C 0.26, D 0.83, E 1.82, CP 0.31, DP 1.28, EXT 4.87; uniform rho = 0.1: D 1.07%, DP 1.84%, p.6). The rho = 0 per-arm values are not tabulated. The budget (15% of |K| even on clean input) is the upper bound on the numerator.

### Reported numbers (all verified against the text; table columns re-aligned from the rendered page)

Table 2 (p.6), plausible, rho = 0.1, 30% coverage, n = 256:

| Arm | Infill F1 | Det. P | Det. R | False-edit % | Correction | Judge NLL |
|---|---|---|---|---|---|---|
| base | 0.275 | - | - | - | - | 3.250 |
| A | 0.287 | - | - | - | - | 3.237 |
| B | 0.286 | 0.572 | 0.035 | 0.29 | 0.756 | 3.209 |
| C | 0.286 | 0.716 | 0.058 | 0.26 | 0.756 | 3.173 |
| D | 0.291 | 0.668 | 0.150 | 0.83 | 0.730 | 3.083 |
| E | 0.292 | 0.625 | 0.272 | 1.82 | 0.716 | 2.980 |
| CP | 0.291 | 0.878 | 0.197 | 0.31 | 0.773 | 3.052 |
| DP | 0.292 | 0.752 | 0.350 | 1.28 | 0.743 | 2.902 |
| EXT | 0.279 | 0.062 | 0.029 | 4.87 | 0.260 | 3.101 |

Caption: paired-bootstrap F1 deltas vs A: DP +0.51 [-0.26, +1.28]; D +0.38 [-0.36, +1.09]; E +0.51 [-0.30, +1.31]; CP +0.40 [-0.31, +1.10]; none significant.

Text-only numbers (Sec 4.2, p.6 to 7):
- Uniform rho = 0.1, arm D: recall 0.959 [0.954, 0.963], precision 0.909, false-edit 1.07%; DP: recall 0.959, precision 0.853, false-edit 1.84%. Corrections land on the exact true token 52 to 77% across eta-arms and corruption types.
- At rho = 0.2 recall pins at about 0.76: the edit budget (rho_hat = 0.15) binds (p.6), so recall is not comparable across rho.
- Pre-registered primary gate (D over A by at least 3 F1 points at rho = 0.1): uniform D-A +3.84 [+2.82, +4.91] (pass), +6.42 [+5.42, +7.47] at rho = 0.2; E +4.47, DP +3.64, C +3.15 [+2.25, +4.10] pass; CP +2.46 [+1.67, +3.29] short. Plausible D-A +0.38 [-0.36, +1.09]: gate fails; at rho = 0.2 plausible D +1.19 [+0.32, +2.06], DP +1.69 [+0.72, +2.65], significant but below the gate. I recomputed D-A from Table 4 (p.10): uniform 0.1/0.3 0.304 - 0.266 = +3.8, uniform 0.2/0.3 0.286 - 0.222 = +6.4, plausible 0.2/0.3 0.281 - 0.269 = +1.2: consistent.
- Table 3 (p.7) judge NLL, clean / uniform 0.1 / plausible 0.1: A 2.565 / 4.084 / 3.237; D 2.581 / 2.610 / 3.083; DP 2.573 / 2.610 / 2.902. "Restores 97% of the damage" checks (A pays +1.52, D and DP +0.03 to +0.04).
- Containment (Fig. 2 caption p.8): uniform rho = 0.1, vanilla arms dip to 0.088 to 0.11 accuracy 1 to 2 tokens from a corruption (0.14 to 0.16 at 3 to 4); eta-arms 0.20 to 0.24; converge by distance 5 or more. Plausible: all arms coincide.
- Non-regression (H3): clean paired F1 deltas straddle zero; held-out bound +0.0036 nats/token (A 3.4072, C/D weights 3.4108; gate 0.02). Arm E (no zero component) is worse: clean-context CE 0.06 vs 0.03, bound +0.0071, false-edit 1.82%.
- Annealing (H4): C to D recall 0.058 to 0.150, CP to DP 0.197 to 0.350 on plausible, at higher false-edit; the authors say this "supports the sampler as a whole, not annealing specifically".
- EXT (GPT-2 surprisal, k matched to DP's edit count): uniform rho = 0.1 recall 0.90 vs D 0.96, F1 0.297 vs 0.304, judge NLL 2.701 vs 2.610; plausible recall 0.003 to 0.076, false-edit up to 10.4%.
- Training dynamics (p.5, no figure): clean-context CE 3.93 to 0.03 nats; substituted-context CE 11.2 to 2.5.

## 4. The "plausible corruptions are barely detectable" finding

Where: Abstract p.1; Table 2 p.6; Sec 4.2 Repair and "The detectability-damage regularity" p.6 to 8. Content: with the GPT-2-left-context plausible corruptions, best recall is 0.350 (DP) at precision 0.752; D 0.150; vanilla 0.035 to 0.058; "two thirds of plausible corruptions go undetected" (p.6). Infill gain +0.38 to +0.51 F1, not significant at rho = 0.1; at rho = 0.2 significant but small (+1.19, +1.69). Their reading (explicitly untested, "we do not measure the divergence directly", p.8): detectability and damage are both governed by how far the corruption kernel is from the data conditional; near-conditional corruptions are invisible and also harmless to neighbouring infill (Fig. 2 right). Wording note: the paper says "partial", not "barely"; "barely" is accurate for the vanilla arms and for EXT, not for DP. Open class they do not cover: entity and number swaps (near-conditional and damaging).

## 5. Limitations

Stated by the paper (Sec 5 p.8, plus p.4, p.6, p.7): single scale (170M), one seed per arm, one text domain; plausible gains small; mixture and annealing ablations confounded (E differs from D in two ways; the C-to-D comparison changes threshold, timing, budget and refill at once); one external detector only (left-context GPT-2), no bidirectional or ELECTRA-style detector; plausible corruptions from one generator family; no entity or number swaps, no code-bug injection, no pairwise preference evaluation; deferred objective ablations (lambda, upweighting); budget rho_hat = 0.15 caps recall at 0.76 for rho = 0.2; Eq. 3 is a surrogate; the re-noising step is a heuristic not shown to preserve the reverse dynamics; the trust-axis and continuous-inpainting link are "motivating analogies, not formal results"; judge NLL is an indirect proxy that may reward fluent but unfaithful repairs; no homogeneous hybrid-noise arm (contrast with GIDD is indirect); scaling to LLaDA-class open.

Not stated, found here (inference):
1. No threshold-free metric (no AUROC or PR curve) for any arm. Detection is reported only at one heuristic operating point under a budget; discriminability of the base or arm-B score is never measured, so "no meaningful likelihood" is an inference from low recall at tau about 0.5 to 0.1.
2. The "about 50% on uniform garbage" statement concerns the pretrained checkpoint; the "recall 0.035" evidence concerns arm B (vanilla SFT). Different weights; the pretrained base is not run through the sampler. Arm B on uniform corruption is not reported in text (only F1 in Table 4: +0.2 over A).
3. The abstract headline (0.96 / 0.91) is for D on the kernel D was trained on.
4. The budget rho_hat = 0.15 is a prior on the corruption rate that the sampler is given; EXT also receives DP's own edit count. Both use information a deployed detector would not have.
5. Evaluation passages are English web text, the plausible generator, the EXT detector and the judge are all GPT-2-family.
6. Detection CIs (about +/-0.005 at n = 256 passages) imply token-level resampling, unlike the passage-level F1 CIs; not stated.
7. "Pre-registered" hypotheses and gates are asserted, but no registry record or file is cited.
8. Single author, 10-page workshop paper, no code: results cannot be reproduced or audited at the implementation level.

## 6. (a) Is the spec's "Trust-but-Verify-style" baseline a faithful port?

Spec text (GATE-METHOD-SPEC-v2 line 179): score -log p_theta(v~_j | nothing masked in the image, caption masked) at the observed position; "only if U7 shows these logits are meaningful"; otherwise "not applicable (consistent with Trust but Verify's own arm B)".

Verdict: faithful for the score, NOT for the method. Keep it, but rename and fix three things.

What matches: the score is the model's own probability of the observed token at its unmasked position (Eq. 4); -log p is a monotone transform of s_i, rank-equivalent (TbV thresholds the probability); one pass with nothing masked in the image equals the first reverse step's score (TbV recomputes it per step, Alg. 1).

What differs and what to do:
1. **No finetuning is not the TbV method.** TbV's score is informative only because the model was finetuned to output the clean token at observed, possibly substituted, positions (Eq. 3). On a model that was not, the port equals TbV's arm B (vanilla SFT plus sampler: recall 0.035, Table 2) or its base row. Label it "TbV-score on the non-finetuned model (arm-B analogue)" and never "the Trust but Verify baseline". A genuine port needs an eta-finetune of UniDisc (uniform or hard-negative substitution of context image tokens, CE at observed positions). That is outside the M1 to M4 plan; say so in the paper as a scoped limitation, or run a small adapter-based version only if the lead approves (not costed here).
2. **Raw logits are required; the existing wrapper cannot supply them.** UniDisc's `_subs_parameterization` (model.py:621-660) sets every unmasked position to log-prob 0 on the observed token and -inf elsewhere; `exp001/unidisc_net.py:134` calls `self.model.forward(...)` and slices that SUBS output, so a TbV-style pass through the wrapper returns exactly 0 (p = 1) at every observed image token for every image, corrupted or not. That is a degenerate score and would be reported wrongly as "baseline fails". `forward(..., return_logits=True)` (model.py:685 and 784-786) returns the backbone logits before SUBS; use those, and apply the same normalisation convention as the GATE `masked_logprobs` (mask index to -inf, same vocabulary slice, softmax) so only "masked vs unmasked" differs. Inference (E3, not run): UniDisc's loss gathers from the SUBS output (model.py:966-967), so the raw logits at unmasked positions receive no direct gradient, which is TbV's arm-B situation; TbV nevertheless reports about 50% probability to garbage for MDLM, so the raw output may be partly copy-like rather than constant. U7 is an empirical question; do not pre-judge it.
3. **Information set.** TbV conditions on all non-hole tokens as observed. The spec masks the caption, which matches the information GATE's image score uses (good for a controlled comparison). Add one more arm with the caption observed (literal TbV context), clearly marked as using more information than GATE's flag, so a reviewer cannot say the baseline was handicapped.
4. **Report threshold-free.** Because TbV gives no AUROC for its own score, a fair port reports AUROC (and recall at the clean-calibrated false-alarm level) for the raw observed-token score, plus a second variant using TbV's own rule (flag s_i < tau, budget B = ceil(0.15 |K|)) at matched edit count, as TbV did for EXT. Then "no signal" and "bad threshold" are separated.
5. Time input: UniDisc uses `time_conditioning: False` and the wrapper passes `sigma=None` (configs/config.yaml; unidisc_net.py:134), so no noise-level mismatch arises for the raw pass. Checked at SHA 3ee3e47a.

## 7. (b) Precise delta of GATE against this paper

1. **Score on an unmodified model.** TbV: s_i = probability of the observed token at its unmasked position, informative only after an 8,000-step eta-finetune; the authors say the training-time process "appears necessary" and that the same sampler on a vanilla model detects almost nothing (p.6). GATE: mask the token, score it within its own modality with the other modality withheld, on pretrained UniDisc 1.4B with no network finetuning. This is the query an absorbing-trained model is built for. Whether it actually works is a measurement GATE still has to make (re-audit caveat); if it does, it is a counterpoint to TbV's necessity statement, which is scoped to TbV's own observed-token score.
2. **Threshold with a stated guarantee vs hand heuristics.** TbV: tau annealed 0.5 to 0.1, t_lock 0.5, budget from an assumed rho_hat = 0.15, empirical clean false-edit rate (0.07 to 0.39% on clean passages) with no guarantee. GATE: conformal risk control on clean pairs for the expected false-alarm proportion, token losses nested in items. TbV does report a clean false-edit metric, so the claim must be "calibrated and guaranteed", not "first to measure false edits".
3. **Two modalities, cross-modal evidence, and a different outcome measure.** TbV: text only, single-modality 170M MDLM, FineWeb-Edu, GPT-2 tokenizer; outcome is infill token-F1, judge NLL and containment. GATE: VQ image tokens and caption tokens in a unified model, with the other modality withheld during scoring, and the outcome is two-way PMI verification preserved under corruption.
4. **Re-mask versus re-infill as a measured comparison.** TbV has one remedy, re-mask and refill by iterative reverse steps ("detect-remask-refill"). GATE compares marginalise (withdraw flagged tokens) with impute (re-infill) in the verification task. The loop itself is not a contribution of GATE.
5. **What GATE lacks relative to TbV (be candid in related work):** TbV has a trained-in capability and a 13-cell paired evaluation with CIs and containment analysis; GATE has none of its outcome results yet (spec 2.2 item 8). Reviewers may read GATE as "TbV plus conformal plus multimodal, without finetuning" (re-audit); that is a composition claim and stands only on measured results.

## 8. (c) Spec section 2.1 (and 2.4) against this paper

Spec 2.1: "On a pretrained unified text-image masked diffusion model (UniDisc 1.4B), with no finetuning, we score each input token by its masked likelihood in its own modality with the other modality withheld, set the flag threshold by conformal risk control on clean pairs ... and measure whether re-masking (or re-infilling) the flagged tokens preserves two-way cross-modal verification under image-token and caption corruption."

Contradicted by TbV: nothing.

Pre-empted or exposed:
- "re-masking ... the flagged tokens": pre-empted as a mechanism for text (Alg. 1, p.5; they re-noise to [MASK] and refill). The claim survives only as "measures whether it preserves cross-modal verification". Do not call the loop novel or reuse "detect-remask-refill" as GATE's name.
- "masked likelihood in its own modality": not pre-empted. TbV never scores a masked context token. But TbV hypothesises (p.7) that detecting plausible corruptions "requires bidirectional consistency checking"; the motivation for masked, context-conditioned scoring is therefore already in their paper as a conjecture. Cite it rather than present it as new reasoning.
- "with no finetuning": not contradicted. TbV supports the premise that the OBSERVED-position score needs finetuning, which is the justification for GATE's choice. It does not test masked scoring on a non-finetuned model.
- "conformal risk control on clean pairs": not pre-empted (TbV: hand-set, no guarantee, no calibration set).
- "two-way cross-modal verification" and image tokens: not covered (text-only).
- Related risk (spec F5): TbV's result that plausible corruptions are only partly detectable even with finetuning means GATE's expected weak spot (JPEG, noise) is a known difficulty, not a surprise; write it as an expected outcome with a pre-stated falsifier.

Spec 2.4 description of TbV, checked line by line:
- "text-only 170M model": correct (Sec 4.1).
- "finetuned with uniform-mixing noise": incomplete. Also a hard-negative mixture (uniform, unigram, embedding neighbours, masked self-proposals; p.4) and an eta = 0 mixture component; the hard-negative arms (CP, DP) were best on plausible corruption (DP recall 0.350). Correct the sentence.
- "scores the observed token at its unmasked position": correct in meaning (Eq. 4, Eq. 3, Alg. 1); the phrase itself is not in the paper (this closes unresolved item 1 of REFERENCES-DRAFT).
- "hand-annealed threshold": correct (0.5 to 0.1, heuristic).
- "reports a clean false-edit rate": correct, but denominator unstated (section 3).
- "no meaningful likelihood" (A7, CITATION-CHECK): verified as paraphrase of Sec 2 p.3 and Sec 4.2 p.6, applied to the vanilla model (arm B), not to the pretrained base; the separate "about 50%" statement about the base is unevidenced in the paper.

## 9. Concerns for the orchestrator

1. The wrapper-based TbV-style pass would return a trivial p = 1; U7 must be tested on raw `return_logits=True` output, otherwise the baseline row is wrong.
2. Rename the baseline (arm-B analogue) and add AUROC; a real TbV port needs a finetune that is outside the current plan.
3. Fix spec 2.4's "uniform-mixing noise" sentence (also hard-negative mixture).
4. No TbV code or preregistration exists; cite it as a 10-page workshop preprint, one seed per arm.
5. Ledger rows: none added (brief said write only the report). Candidate rows: the claims block above (statements 3, 4, 5, 7).

Files created beyond this report (source artifacts per the reader procedure): research/sources/pdfs/2610.22380.pdf, research/sources/md/2610.22380.md; rendered page images are in the session scratchpad only.
