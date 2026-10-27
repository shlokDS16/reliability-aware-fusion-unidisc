```yaml
agent: method-architect
date: 2026-10-28
brief: GATE spec v2. Revises v1 (GATE-METHOD-SPEC-2026-10-28.md, unchanged) against the red team (RED-TEAM-GATE-SPEC-2026-10-28.md, GO WITH CHANGES 0.45), the novelty re-audit (NOVELTY-REAUDIT-GATE-2026-10-28.md, narrow delta 0.50) and the crash diagnosis (PROBE2-CRASH-DIAGNOSIS-2026-10-28.md); adds a measurement framing, a primary contrast against no gate with measured headroom, a power section and a deadline plan.
sources_examined:
  - research/paper2/method/GATE-METHOD-SPEC-2026-10-28.md (v1, own)
  - research/paper2/method/RED-TEAM-GATE-SPEC-2026-10-28.md (full)
  - research/paper2/ideation/NOVELTY-REAUDIT-GATE-2026-10-28.md (full)
  - research/paper2/probes/PROBE2-CRASH-DIAGNOSIS-2026-10-28.md (full)
  - runs/P2-PROBE-01/items.jsonl (300 rows; per-item fields), runs/P2-PROBE-01/config.json
  - runs/P2-PROBE-02/selection.json (image ids only)
  - exp_p2/run_probe1.py lines 1-12 and 40-70 (score definitions)
coverage: >
  Re-read the three reviews in full. Read probe-1 per-item scores to measure clean headroom and margins (script in Appendix A;
  output quoted, not stored in a run directory; the statistician should rerun it and store it). Not read: Trust but Verify,
  Gomes et al., CO2Jump, UniDisc App. G.1 (their content comes from the re-audit, E2-partial or E1+ there, E1 here); the UniDisc
  output parameterisation (whether logits at unmasked positions are meaningful; decides the Trust-but-Verify-style baseline).
claims:
  - statement: "The image-direction full-mask statistic (probe-1 b_full) has measured headroom on clean pairs: 0.843 paired accuracy, 47 of 300 items wrong."
    status: supported
    evidence: runs/P2-PROBE-01/items.jsonl, Appendix A script
    level: E4 (re-computed here from stored per-item scores; exploratory probe, not preregistered)
    confidence: 0.95
  - statement: "Probe 1's text-direction null ('afull_null') masks the whole caption and the whole image, so it depends only on the layout (U3 of v1 resolved)."
    status: supported
    evidence: exp_p2/run_probe1.py line 10 (docstring) and line 55 (add("afull_null", cap, ..., img))
    level: E3
    confidence: 0.95
  - statement: "GATE-M beats no gate on the image-direction verification of corrupted pairs for at least one realistic corruption."
    status: unknown
    evidence: untested; GPU on hold (runs/P2-PROBE-02/HOLD.txt)
    level: E0
    confidence: 0.35
competing_explanations:
  - geometry of the mask, not detection (red team M5): tested by a geometry-matched random gate
  - texture or encoder instability, not corruption (red team M4): tested by non-generative baselines on the same labels
  - pixel-domain denoising does the same job more cheaply (red team M4b): tested as a defence arm
unknowns:
  - U1 whether the GPU will run (crash cause about 50 percent likely a driver fault on idle-to-boost ramps, a hypothesis)
  - U2 per-row time (estimate 0.15 s, conservative; see section 10) and VQ encode time (unmeasured; assumed at most 1 s)
  - U4 COCO instances annotations and CLIP weights on disk
  - U7 whether UniDisc's logits at unmasked positions are meaningful (Trust-but-Verify-style baseline)
  - U8 whether COCO val2017 was in UniDisc's or LlamaGen-VQ's training data (red team m6)
  - U9 date: the coordinator writes "Fri 31 Oct / Sat 1 Nov"; the red team writes "Wed 28 Oct" for today, which makes Friday 30 Oct. The plan below uses Wed 28 = today and freezes results on Fri 30
next_test:
  hypothesis: "Corrupted-no-gate image-direction verification falls below clean, and an oracle gate restores part of it, for at least one realistic corruption"
  intervention: "M3 headroom check: 100 held-out items, 2 caption-only passes per item plus VQ encodes"
  primary_metric: "paired difference of the per-item evidence z-score (section 7.2), clean minus corrupted and oracle minus corrupted"
  falsifier: "both differences below 2 paired SE for every realistic corruption at every severity on the ladder"
  gpu_hours: "about 0.18 (estimate)"
```

# GATE method specification, version 2

v1 (`GATE-METHOD-SPEC-2026-10-28.md`) is unchanged and remains the reference for anything not restated here (notation of
v1 section 1, the context levels $A,B,C,D$ of v1 section 3.1, the proofs of v1 Props. 3, 6, 7). Where v2 and v1 disagree, v2
wins. No results are claimed. Number provenance as in v1: "probe 1" = probe report; "items.jsonl" = recomputed from
`runs/P2-PROBE-01/items.jsonl` by the Appendix A script; "crash diagnosis" = `PROBE2-CRASH-DIAGNOSIS-2026-10-28.md`, which
cites run files; "derived" = arithmetic; "design choice"; "estimate" for every GPU-hour figure.

Red team before implementation: v2 changes the primary experiment, so `red-team` should check sections 7, 9 and 11 before
`lab-engineer` writes M3/M4 code. M0-M1 need no new method code and can start once Shlok releases the GPU.

---

## 1. Resolution table (issue -> change -> section)

| Issue (source) | Change in v2 | Section | Status |
|---|---|---|---|
| **B1** primary contrast vs random gate | Primary = GATE-M **versus no gate** on corrupted pairs. Random gates (scattered and geometry-matched) and the oracle gate are mechanism controls. Claim withdrawn if GATE-M does not beat no gate on at least one realistic corruption | 7.1, 7.4 | Resolved in design |
| **B2** null at a 0.990 ceiling; theory does not cover the dominant statistic; hard negatives may be true; no power; data-dependent family | Primary endpoint moved to the **image direction** (probe-1 b_full: 0.843 clean, 47/300 wrong, items.jsonl), the additive statistic that Prop. 4 covers. Headroom check on 100 separate items before the test (Alg. 9); the corruption family and severities are fixed on those items, never on test items. Hard negatives built to be invalid by construction plus an audit (Alg. 11). Power section | 7.2, 7.3, 7.5, 9 | Resolved in design; whether headroom exists is unknown until M3 |
| **B3** crash undiagnosed; workload larger and newer | MUST tier uses only pass types already executed in probes 1-2; M1 is the unmodified probe 2 completing its 200 items (the red team's own criterion); the crash diagnosis's staged test (stages 0-3) is M0; no re-infill sampling in MUST; MUST about 2.6 GPU-h (estimate), down from 7.9 | 11 | **Partly open**: the cause is a hypothesis (driver fault, about 50 percent, crash diagnosis); no code change can remove it. Resolved only if stages 1-3 pass |
| M1 Prop. 1 is the training objective; ignores data-dependent G; untested on the real model | Prop. 1 demoted to "standard property" (not a contribution); Prop. 1' adds the conditions under which masking a *data-selected* G is the right treatment; real-model coherence test with a pre-stated tolerance (Alg. 12, M5) | 5.1, 10, 11 | Resolved in design |
| M2 Prop. 4 variance error; mean-0 premise; implausible beta | Corrected inequality ($\sigma^2\to\sigma^2+\mu^2$); general form with $\mu_c\ne0$; all inputs measured per corruption from per-token terms, and the plug-in prediction of the sign is checked against the observed GATE-vs-none difference | 5.3 | Resolved in design |
| M3 no theory for JPEG/noise; toothless falsifier; patch mislabelled; corruption-specific statistic; selection data reused | Prop. 2 scoped to context-independent corruptions only; JPEG and noise have no theory and are stated as an empirical question. Patch and swap relabelled **sanity**; a pixel **splice** added as a third realistic candidate. Statistic fixed a priori ($q$, $K=8$, word/min, pooled, $\alpha=0.05$): no tuning fold, so E1 items are not selection data. Falsifier: $q$ must beat the **best cheap baseline**, not random | 4, 5.2, 7.6 | Resolved in design |
| M4 circular labels; missing cheap baselines; post-hoc graded label; NaN item drops | Non-generative baselines (patch texture, neighbour codebook distance, code rarity), Trust-but-Verify-style observed-position probability, plain-B top-k, s3; pixel-domain denoise **defence arm**; graded label rule fixed now and labelled exploratory; item-drop counts reported per corruption | 4.2, 7.6, 8 | Resolved in design |
| M5 random gate differs in geometry; oracle not an evidence oracle | Geometry-matched random gate (random translation of GATE's own mask, Alg. 10) is the mechanism test; scattered random kept; "oracle" renamed "changed-code gate"; the true upper bound is the clean image | 7.4 | Resolved in design |
| M6 guarantee narrower than readers will read it; ties; Mondrian chosen post hoc | Mandatory wording; precision among flagged tokens and FAP on clean tokens of corrupted items reported beside the bound; jitter at calibration **and** test; pooled only (Mondrian exploratory, COULD); "clean" defined as COCO-as-tokenised; all choices fixed now | 6 | Resolved in design |
| M7 IF fit | Reframed as sensor validation before evidence fusion: each image token is a sensor whose log-likelihood ratio is fused; the gate is fault detection and isolation for those sensors; the two-way part fuses a centralised (text-given-image) and a distributed (image-given-text) fuser | 2.3, 8 | **Open**: only an editor or blind reader can settle fit; proposed check in section 12 |
| M8 narrow delta; strawman baseline; G.1 misdescribed; Token-Critic missing | Claim reworded to the re-audit's surviving sentence; "DD-style" renamed "uncertainty-ranked (s3) gate" and not called Dropout Decoding; plain-B top-k (GATE minus calibration) is the Token-Critic/Dropout-Decoding proxy; UniDisc G.1-style = random mask, $n$ re-infills, best-of-$n$ by own likelihood (SHOULD); Token-Critic, self-correction and CO2Jump cited | 2, 4.2, 11 | Resolved in design; novelty remains narrow (0.50) |
| M9 one model | Claims, title and abstract scoped to "one 1.4B model"; E7 in COULD with a measure-first gate | 2.2, 11.3 | Accepted as a stated limitation |
| M10 LDA is a supervised classifier; mismatched negatives; no held-out fold; Gaussianity | Fusion demoted to secondary; weights fitted on calibration pairs with the **same negative type** as test, never on test; the unfitted Stouffer sum reported first; "training-free" wording replaced by "no network finetuning; two fusion weights fitted on clean labelled pairs"; normality checked | 8 | Resolved in design; the gain is untestable unless S3 opens headroom |
| M11 unit tests cannot catch real failures; props accommodate both signs | Real-model coherence test with tolerance (Alg. 12); refutation conditions stated in advance for Props. 1', 4, 6 | 5, 10 | Resolved in design |
| m1 test overlap with probe items | Test, calibration and headroom folds exclude all probe-1 and probe-2 image ids (6 ids are shared between the two probes, checked) | 7.5 | Resolved |
| m2 U3 | Resolved: probe 1's text null masks caption and image (run_probe1.py line 55) | yaml | Resolved |
| m3 unchecked citations | Listed for citation-validator | 13 | Open |
| m4 caption side at ceiling, lumpy FAP | Caption side moved to SHOULD; word-level FAP reported as realised counts | 11.2 | Accepted |
| m5 T2I grid on a weak generator | COULD only | 11.3 | Accepted |
| m6 contamination | Stated as an unknown and a limitation; a documentation check (CPU) in SHOULD | 11.2 | Open |
| m7 bf16 | Primary endpoint averages about 1024 per-token terms whose item-mean margin is 0.18 nats (items.jsonl), larger than the 0.0625 bf16 spacing; per-token gate scores jittered | 6, 7.2 | Mitigated |
| m8 E3 pass count not itemised | Every MUST item itemised | 11.1 | Resolved |
| Re-audit must-not-claim list (9 items) | Compliance list | 2.2 | Resolved |
| Re-audit: add Trust but Verify, Gomes et al., CO2Jump | Related work and baselines | 2.4, 4.2 | Resolved |
| Crash diagnosis: probe report's 635 s "stall" was a system sleep | Noted; per-item timing uses medians | 10 | Noted |

---

## 2. Claim, framing and what the paper must not say

### 2.1 The claim (measurement framing, from the re-audit's surviving sentence)
"On a pretrained unified text-image masked diffusion model (UniDisc 1.4B), with no finetuning, we score each input token by
its masked likelihood in its own modality with the other modality withheld, set the flag threshold by conformal risk
control on clean pairs so that the expected false-alarm proportion on clean inputs is at most alpha, and **measure**
whether re-masking (or re-infilling) the flagged tokens preserves two-way cross-modal verification under image-token and
caption corruption." Every outcome clause is a hypothesis until M1-M4 exist.

### 2.2 Must-not-claim compliance (re-audit list, items 1-9)
1. No "first to detect and re-mask corrupted input tokens in an MDM" (Trust but Verify, arXiv 2610.22380).
2. No "first to re-mask in a unified MDM" or "first cross-modal remask trigger" (CO2Jump 2607.13188; FreeCorrection
   2602.02927; UniDisc G.1).
3. No "first risk-controlled threshold with masking scores for vision-language token or word errors" (Gomes et al. 2504.01225).
4. No "first masked-likelihood anomaly detector" or "first null-normalised generative image-text score" (Salazar PLL
   1910.14659, uChecker 2209.07068, Diffusion ITM 2305.16397).
5. Prop. 1 is presented as the standard MDM denoiser property, Prop. 5 as conformal risk control applied. Neither is a
   contribution.
6. The only guarantee stated is the one in section 6. No bound on detection power, none on false alarms among clean tokens
   of corrupted items, none under shift. No "certified", "provably robust" or "reliable" in a guarantee sense.
7. "Training-free" is a property, not the contribution. Fusion weights are fitted (section 8), so the paper says "no
   network finetuning".
8. No sentence that GATE improves verification, repair or T2I until the corresponding run exists.
9. Scope: one model, UniDisc 1.4B, COCO val2017, the corruptions listed. Title and abstract carry the scope.

### 2.3 Fusion framing (answers M7 as far as design can)
- **Image direction = distributed fusion.** Each image token $j$ is a sensor reporting code $\tilde v_j$. Under caption
  hypothesis $c$ its log-likelihood is $\log p_\theta(\tilde v_j\mid\varnothing^I,c)$ (one caption-only pass serves all
  sensors). The paired decision sums per-sensor log-likelihood ratios $\Delta_j=\log p(\tilde v_j\mid c^+)-\log p(\tilde v_j\mid c^-)$,
  a naive-Bayes fusion rule. **GATE is sensor fault detection and isolation**: a faulty sensor is found from its
  inconsistency with neighbouring sensors ($q_j$, which never sees the hypothesis), and isolated before fusion.
- **Text direction = centralised fusion.** The image tokens are inputs to one estimator, $p(t\mid v)$; GATE withdraws
  faulty inputs (marginalise) or replaces them (impute).
- **Two-way fusion** combines the two fusers (section 8).
This is a framing to state in the Introduction. Whether IF reviewers accept it is not something the design can settle (M7 open).

### 2.4 Related work that must be compared (re-audit; content E1 here)
Trust but Verify (2610.22380): text-only 170M model, finetuned with uniform-mixing noise, scores the observed token at its
*unmasked* position, hand-annealed threshold, reports a clean false-edit rate. Gomes et al. (2504.01225): CLIP-based,
cross-modal masking score, CRC calibrated on labelled foil data (FDR/FPR, high-probability bound). CO2Jump (2607.13188):
remasks the sampler's own generated tokens with cross-modal confidence, quota not threshold. UniDisc App. G.1: random mask,
re-infill, best of $n$. Dropout Decoding, DiSP, Token-Critic, FreeCorrection as in v1 and the red team. The delta sentence
GATE can defend: pretrained unified model with no finetuning, mask-then-score within modality with the other withheld,
clean-pair CRC with token losses nested in items, and a measured marginalise-versus-impute comparison in a cross-modal
verification task.

---

## 3. Notation additions (v1 section 1 otherwise)

| Symbol | Meaning |
|---|---|
| $\Delta_j(c^+,c^-)$ | per-token paired image-direction evidence, $C_j(c^+)-C_j(c^-)$ at the observed code (the null $D_j$ cancels for a fixed image) |
| $\bar\Delta_R$, $s_R$ | mean and SD of $\Delta_j$ over the included set $R$ |
| $z_R=\bar\Delta_R/(s_R/\sqrt{|R|})$ | per-item evidence z-score (section 7.2) |
| $Y_i^{\text{arm}}\in\{0,1\}$ | paired correctness of item $i$ under an arm ($\bar\Delta_R>0$) |
| $\rho$ | fraction of changed codes in a corrupted image |
| $G^{\rm geo}$ | geometry-matched random gate (Alg. 10) |
| $G^{\rm chg}$ | changed-code gate $\{j: Z_j=1\}$ (v1's "oracle") |

---

## 4. Scores and baselines (all fixed a priori; no tuning fold)

### 4.1 GATE statistic (fixed)
R1 gate statistic $u_j=-(B_j-D_j)$ ($q$), $K=8$ complementary masks with probe 2's seed rule, caption masked, threshold by
pooled CRC at $\alpha=0.05$ (0.01 and 0.10 reported as sensitivity, not selected). Text side: word unit, minimum over
pieces. These were the v1 defaults; v2 freezes them so that no item is used to select them (M3d, M3e, M6f).
Reason for $q$ over plain-B a priori: it is the only one of the two that does not assume a uniform alternative, and a
deployed gate does not know the corruption type. Plain-B is reported as a secondary detector.

### 4.2 Baselines and controls for detection and gating

| Baseline | Uses the model? | Uses the observed value? | Cost | Role |
|---|---|---|---|---|
| random score | no | no | 0 | floor |
| **patch texture**: pixel variance of the 16x16 pixel patch of token $j$ in the observed image | no | yes (pixels) | CPU | M4: texture detector |
| **neighbour codebook distance**: mean L2 distance from $e(\tilde v_j)$ to the 8 neighbours' codebook vectors (LlamaGen VQ-16 codebook) | no | yes | CPU | M4: non-generative spatial consistency |
| **code rarity**: $-\log$ frequency of $\tilde v_j$ among the calibration fold's clean codes | no | yes | CPU | M4 |
| **s3 (uncertainty-ranked)**: $1-\max_y p_\theta$ from the same $B$ passes | yes | no | 0 extra | Dropout-Decoding-*inspired* only; not called Dropout Decoding |
| **plain-B top-k**: $-B_j$, flag the top $|G|$ (GATE without calibration, equal size) | yes | yes | 0 extra | Token-Critic / Dropout-Decoding proxy (M8b) |
| **Trust-but-Verify-style**: $-\log p_\theta(\tilde v_j\mid\text{nothing masked in the image, caption masked})$ at the observed position | yes | yes | 1 pass per image | re-audit; **only if U7 shows these logits are meaningful**. If UniDisc's parameterisation copies unmasked inputs, report it as not applicable (consistent with Trust but Verify's own arm B) |
| r_original | yes | yes | 0 extra (from probe 2) | cancellation control (v1 Prop. 3) |

### 4.3 Defence arms for the downstream task
none; GATE-M; changed-code gate; geometry-matched random gate (3 seeds); scattered random gate (3 seeds); plain-B top-k;
s3 top-k; **pixel-domain denoise** before tokenisation (a classical, non-learned denoiser with one parameter setting
fixed now for all corruptions: OpenCV `fastNlMeansDenoisingColored` with library defaults as design choice; OpenCV 4.13.0
and scikit-image 0.26.0 import in the default `python` on PATH, checked 2026-10-28; the UniDisc venv is not checked);
denoise + GATE-M (SHOULD); GATE on clean images.

---

## 5. Theory changes

### 5.1 Proposition 1' (when masking a data-selected set is the right treatment)
v1 Prop. 1 stands as the standard property of a Bayes-optimal absorbing-state denoiser for a *fixed* $G$ (not a contribution).
For a gate that selects $G$ from the observed values, let $v$ be the clean tokens, $\tilde v$ the observed ones, and $Y$ the
quantity to infer (the caption hypothesis). Masking $G$ and using $p(Y\mid \tilde v_R)$ equals the Bayes answer
$p(Y\mid\tilde v,\ \text{corruption model})$ when all of the following hold:
(i) $R$ contains no corrupted token (detection rate on $R$ is perfect);
(ii) corrupted values carry no information about the clean values ($\tilde v_G\perp v_G$), true for uniform-random-code swap
and patch, false for JPEG and noise;
(iii) corruption locations are independent of the content (true for swap and patch as coded; not for JPEG and noise, whose
changed codes concentrate where the encoder is unstable);
(iv) no clean token is in $G$, or the clean tokens in $G$ are uninformative about $Y$.
Each violation has a named cost: (i) residual corrupted evidence; (ii) discarded signal (JPEG/noise codes are noisy copies,
red team M2b), so the right treatment would be a denoising posterior $p(v_G\mid\tilde v_G,v_R)$, not marginalisation;
(iii) informative missingness: the gate selects on the observed values, so $p(v_G\mid v_R)$ is the wrong distribution for
selected positions; (iv) lost clean evidence at rate $\alpha$.
*Consequence stated in advance:* masking should help most for sanity corruptions (ii and iii hold) and least, possibly
not at all, for JPEG and noise. A result where GATE-M helps on JPEG/noise but not on patch would contradict this account.

### 5.2 Proposition 2, scope restricted
v1 Prop. 2 (likelihood-ratio form) holds only for context-independent alternatives, i.e. the sanity corruptions. For JPEG,
noise and splice there is **no** theory in this paper; detection there is an empirical question answered against the cheap
baselines (section 7.6). The v1 sentence "closer to JPEG and noise" is withdrawn.

### 5.3 Proposition 4, corrected (for the additive image-direction statistic)
Model: per-token paired evidence $\Delta_j$; clean tokens mean $\mu$, variance $\sigma^2$, kept with probability $1-\alpha$;
corrupted tokens mean $\mu_c$, variance $\sigma_c^2$, kept with probability $1-\beta$; corrupted fraction $\rho$; inclusion
independent of $\Delta_j$ within a class; tokens independent (approximation; neighbours are correlated). For
$S=\sum_j I_j\Delta_j$ over $m$ tokens:
$$\mathbb E S=m\big[(1-\rho)(1-\alpha)\mu+\rho(1-\beta)\mu_c\big],$$
$$\mathrm{Var}\,S=m\big[(1-\rho)\{(1-\alpha)\sigma^2+\alpha(1-\alpha)\mu^2\}+\rho\{(1-\beta)\sigma_c^2+\beta(1-\beta)\mu_c^2\}\big].$$
No gate: $\alpha=\beta=0$. The gate raises $\mathbb E S/\sqrt{\mathrm{Var}\,S}$ iff the ratio after exceeds the ratio before.
Special case $\mu_c=0$ (the corrected v1 inequality, red team M2a):
$$\rho\,\sigma_c^2\,(\beta-2\alpha+\alpha^2)\;>\;\alpha(1-\alpha)(1-\rho)\,(\sigma^2+\mu^2).$$
Paired decisions use the same $R$ for both captions, so the sign of the mean and of the sum agree; the per-item decision is
unaffected by normalising by $|R|$.
*Measurement plan (M2 resolution):* per corruption, estimate $\rho$, $\mu$, $\sigma^2$, $\mu_c$, $\sigma_c^2$ from the per-token
$\Delta_j$ of the M4 test items (the changed-code labels give the classes), and $\alpha_{\rm obs}$, $\beta_{\rm obs}$ from
GATE's flags. Plug into the general form; report the predicted sign of the SNR change next to the observed GATE-M minus none
difference. *Refutation stated in advance:* if the plug-in prediction and the observed sign disagree for a corruption whose
observed difference has a CI excluding 0, the independent-token model is refuted for that corruption and the paper says so.
Note: $\mu_c$ can be systematically non-zero even for random codes, because a caption that makes the predicted image
distribution flatter gives random codes higher probability. That is a bias toward vaguer captions, measurable as $\mu_c$.

### 5.4 Prop. 6 (M versus I) refutation condition (M11)
Prediction: M $\ge$ I on the paired verification endpoint. If I beats M with a paired CI excluding 0 on any realistic
corruption, that refutes the coherence premise of Prop. 6 for this model; it is reported as a refutation, not attributed
after the fact to amortisation.

---

## 6. Calibration: wording, ties and reporting (M6)

**Mandatory wording in the paper.** "The threshold is calibrated so that, for a clean test pair exchangeable with the
calibration pairs, the expected proportion of its tokens that are flagged is at most alpha." Nothing stronger.

**Clean.** "Clean" means COCO val2017 photographs as distributed (already JPEG-compressed) passed through the LlamaGen VQ-16
tokenizer at 512 px. Corruption labels are relative to that tokenisation.

**Ties.** Both calibration and test scores get an independent jitter $\epsilon\sim U(0,\epsilon_0)$ before comparison, with
$\epsilon_0$ below the smallest non-zero gap between distinct scores in the calibration set (computed, not chosen). v1 Alg. 4
gains this step (Alg. 4' step 1b). Strict inequality $u>\tau$ throughout.

**Reported with equal prominence.** Realised FAP on clean test items (with CI) for $\alpha\in\{0.01,0.05,0.10\}$; precision
among flagged tokens per corruption; FAP on the clean tokens of corrupted items; the spatial map of clean false alarms.
Illustration of why precision must be shown (derived, red team M6b): at $\alpha=0.05$ on an 8x8 patch image, about 48
expected false flags against at most 64 true ones, so precision at most 0.57 even with perfect detection.

**Fixed now.** Pooled CRC only. Mondrian, iterated gating and fp32 heads are COULD-tier exploratory items.

**Calibration fold size.** 300 clean pairs (design choice; down from 500 in v1 to fit MUST). CRC slack $1/301\approx0.0033$
(derived).

---

## 7. Primary endpoint, controls, headroom, negatives

### 7.1 Primary contrast (B1)
On corrupted test pairs, per realistic corruption that passed the headroom check: paired correctness $Y_i$ of the
image-direction statistic under **GATE-M versus no gate**. Test: exact two-sided McNemar on the discordant items; family =
the realistic corruptions that passed headroom (at most 3: JPEG, noise, splice), Holm. Claim withdrawn if no member of the
family shows GATE-M > none at the Holm-adjusted level.

### 7.2 Why this endpoint, and the key secondary
- **Measured headroom on clean pairs**: b_full paired accuracy 0.843, 47 of 300 wrong (items.jsonl, Appendix A); the
  text-direction a_full_pmi is 0.990 (3 wrong) and cannot show restoration.
- **Covered by theory**: the image direction is additive over tokens, so Prop. 4 applies to it directly.
- **Cheap**: the per-caption pass does not see the image; gating, oracle, random, denoised and corrupted arms reuse it
  (gathering only).
- **Scale**: the clean item-mean margin is 0.18 nats per token, SD 0.196 across items (items.jsonl); the K=8 version b8 has
  a margin of 0.0046 (items.jsonl), which is what the probe report's "+0.005 nats" referred to. So bf16 resolution (0.0625 at
  logits 8-16) matters for single-token gate scores, not for this item-level statistic.

Key secondary (continuous, more power): the per-item evidence z-score $z_R=\bar\Delta_R/(s_R/\sqrt{|R|})$, GATE-M minus none,
paired; bootstrap CI. It is scale-free and rises when zero-mean faulty sensors are removed; a random gate leaves it unchanged
in expectation (it only shrinks $|R|$). Other secondaries: text direction (conditioning arms), fused statistic, unpaired AUROC.

### 7.3 Headroom check before the main run (Alg. 9; red team B2 "Resolved if")
On 100 **headroom items** (disjoint from every other fold), for each realistic corruption, walk a fixed severity ladder in
order and stop at the first severity where both hold on the continuous z-score endpoint:
(H1) clean minus corrupted-none $\ge 2$ paired SE (there is a drop), and
(H2) changed-code-gate minus corrupted-none $\ge 2$ paired SE (removing the corrupted sensors recovers some of it).
Ladders (design choice): JPEG quality 10 then 5; Gaussian noise $\sigma$ 0.10 then 0.20; splice a 128x128-pixel region from
another COCO image at a uniformly random location, then 192x192. A corruption that fails both rungs leaves the family before
any test item is scored, so the family is fixed on separate data (B2.5). GATE's own flags are **not** computed on headroom
items, so the decision is blind to the method. If no realistic corruption passes, the downstream claim is withdrawn and the
paper reports detection and calibration only (section 11.4).
Also computed on the headroom items (for section 9): the discordance count between changed-code gate and none, as an upper
reference for what any gate could achieve.

### 7.4 Controls (M5)
- **Geometry-matched random gate** $G^{\rm geo}$ (Alg. 10): GATE's own mask for that item, translated by a uniformly random
  non-zero shift on the 32x32 torus; same size, same shape, different place. GATE-M versus $G^{\rm geo}$ is the mechanism test
  (detection beyond geometry). 3 seeds, averaged per item.
- **Scattered random gate**: same size, uniform positions; 3 seeds.
- **Changed-code gate** $G^{\rm chg}$: not an upper bound for JPEG/noise (Prop. 1' (ii)); the upper bound is the clean image.
- **GATE on clean images**: predicted small loss, never a gain (Prop. 4, $\rho=0$).
- **Pixel-domain denoise** and **plain-B top-k / s3 top-k** as in 4.3.

### 7.5 Folds (fixed seed, by COCO val2017 image id)
Excluded from all new folds: the 300 probe-1 ids and the 200 probe-2 ids (6 ids are in both; checked from
`runs/P2-PROBE-01/items.jsonl` and `runs/P2-PROBE-02/selection.json`). New folds: calibration 300, headroom 100, test 300.
Caption length 5-32 tokens as in the probes. Detection (M1) uses the 200 probe-2 items; since nothing is tuned, they are
held-out with respect to every choice.

### 7.6 Detection falsifier (M3b)
On the 200 probe-2 items, per realistic corruption (JPEG q10, noise 0.1 as coded in probe 2; splice in SHOULD): per-item
AUROC of $-q$ against $Z$, paired with the best cheap baseline of section 4.2 (the one with the highest mean AUROC on that
corruption, so the comparison is against the strongest cheap rival). Falsifier: the paired bootstrap CI of
(AUROC of $q$ minus AUROC of the best cheap baseline) does not exclude 0 on JPEG and on noise. Patch and swap reported as
sanity. Items with fewer than 5 corrupted or 5 clean tokens are excluded (as `run_probe2.py`); their count per corruption is
reported (M4d). Graded label (exploratory, rule fixed now): $Z^{\rm big}_j=1$ if the codebook distance between observed and
clean code exceeds the median of that distance over all changed codes of that corruption in the 200 items.

---

## 8. Two-way fusion (secondary; M10)

Order of reporting: (1) each direction alone; (2) unfitted Stouffer: standardise each direction's paired margin by its SD
over **calibration** items, sum, divide by $\sqrt{2+2\hat r}$ with the calibration correlation $\hat r$; (3) Fisher LDA on
paired differences (v1 section 7), weights fitted on the 300 calibration pairs with the **same negative type** as the test
contrast (deranged for the primary, hard negatives in S3), frozen before test. Normality of the paired differences checked
on calibration items (QQ plot in the appendix). Wording: "no network finetuning; two fusion weights fitted on clean labelled
pairs". The fusion gain is testable only where the best single direction is below ceiling, i.e. with hard negatives (S3);
at 0.990 the paper states it cannot be tested.

---

## 9. Power and sample size (inputs for the statistician)

**Measured inputs (items.jsonl, clean pairs, deranged negatives, n = 300):** image direction b_full accuracy 0.843 (47 wrong);
item-mean margin 0.18 nats per token, SD 0.196; 85 items with |margin| below half an SD (near the decision boundary).
Text direction a_full_pmi 0.990 (3 wrong). Corrupted-arm quantities are **unknown** until M3.

**Primary (McNemar, paired binary).** Only discordant items carry information. Let $\theta$ be the probability that a
discordant item favours GATE-M. Normal approximation to the sign test, two-sided, power 0.8 (derived arithmetic; the
statistician should replace it with exact binomial power):
$$n_d=\Big[\frac{0.5\,z_{1-\alpha'/2}+z_{0.8}\sqrt{\theta(1-\theta)}}{\theta-0.5}\Big]^2 .$$

| $\theta$ | $n_d$ at $\alpha'=0.05$ | $n_d$ at $\alpha'=0.0167$ (Holm, first of 3) |
|---|---|---|
| 0.70 | 47 | 63 |
| 0.75 | 29 | 39 |
| 0.80 | 20 | 27 |

With $n=300$ test items, $\theta=0.75$ needs a discordance rate of about 10 percent (29 items) unadjusted or 13 percent (39 items) at the Holm level (derived). Assumptions:
items independent; $\theta$ constant; no ties. Whether such discordance exists is unknown; it is bounded above (roughly) by
the changed-code-gate-versus-none discordance measured on the headroom items.

**Pre-registered decision on the headroom items (before the test fold is scored).** Scale the changed-code-gate-versus-none
discordant count from 100 to 300 items. If it is below $n_d$ for $\theta=0.75$ at the Holm level, even a perfect detector
would be under-powered: either raise the test fold to 500 items (about +0.8 GPU-h, estimate) or make the z-score endpoint
primary. The choice is recorded before any test item is scored.

**Key secondary (paired t on the z-score change).** Minimum detectable effect at power 0.8:
$\text{MDE}=(z_{1-\alpha'/2}+z_{0.8})\,\sigma_d/\sqrt n$, i.e. about $0.16\,\sigma_d$ at $\alpha'=0.05$ and $0.19\,\sigma_d$ at
$\alpha'=0.0167$ for $n=300$ (derived), where $\sigma_d$ is the SD of the per-item change, estimated on headroom items from the
changed-code gate.

**Headroom rule's sensitivity.** With $n=100$, the 2-SE rule passes with probability about 0.5 when the true difference
equals $0.2\,\sigma_d$ (derived). A corruption with a smaller true drop will usually be excluded; that errs toward a smaller,
honest family.

**Detection (M1).** 200 items; per-item AUROCs paired between $q$ and a baseline; the bootstrap over items gives the CI.
Not powered formally; the statistician should add a simulation-based check once probe-2 per-item AUROC spread is known.

---

## 10. Algorithms changed or added (v1 Algs. 1-8 otherwise)

**Alg. 4' Gate (replaces v1 Alg. 4).** 1. $u\leftarrow$ ReliabilityScores (R1: $q$, caption masked). 1b. $u_j\leftarrow u_j+\epsilon_j$,
$\epsilon_j\sim U(0,\epsilon_0)$ with the calibration $\epsilon_0$ and an independent seed. 2. $G=\{j:u_j>\hat\tau\}$. No iteration.

**Alg. 5' Image-direction evidence (primary).** Input: observed codes $\tilde v$, captions $c^+,c^-$, an arm's included set $R$.
1. For each caption $c$: $\Lambda^c\leftarrow$ one pass with all image tokens masked and $c$ visible, keep the
   $[m,16384]$ fp32 log-probability matrix (64 MiB) or gather immediately for every code set needed (cache per caption).
2. For every arm (none, GATE-M, geo, scattered, changed-code, top-k, denoised codes): $\Delta_j=\Lambda^{c^+}_j[\tilde v_j]-\Lambda^{c^-}_j[\tilde v_j]$ for $j\in R$.
3. Return $Y=\mathbb 1[\bar\Delta_R>0]$ and $z_R$. Cost: 2 passes per item for all arms together.

**Alg. 9 HeadroomCheck.** Input: 100 headroom items, ladders. 1. Encode clean and each ladder rung. 2. Alg. 5' with arms
none, changed-code, on clean and corrupted codes. 3. Paired z-score differences (H1), (H2) with SE. 4. For each corruption take
the first passing rung; write `family.json` (corruptions, severities, discordance counts, the endpoint decision of section 9)
and commit it before test items are scored.

**Alg. 10 GeometryMatchedRandomGate.** Input: GATE's $G$ on the 32x32 grid, seed. 1. Draw $(d_x,d_y)$ uniformly from
$\{0..31\}^2\setminus\{(0,0)\}$. 2. $G^{\rm geo}=\{((x+d_x)\bmod 32,(y+d_y)\bmod 32):(x,y)\in G\}$. 3. Return. Text analogue:
random words of equal count.

**Alg. 11 HardNegatives (for S3; never valid captions by construction).**
1. For each test image, take its annotated COCO categories (instances_val2017, U4) and its five reference captions.
2. In the scored caption, find a noun that maps to an annotated category (a fixed synonym list from the 80 category names,
   e.g. person <- man, woman, people, boy, girl; written once, before use).
3. Replace it with a category name from the **same supercategory** that is (a) not annotated in the image and (b) not
   mentioned in any of the five reference captions. Keep number (singular or plural) by a fixed rule.
4. Audit before scoring: a reviewer agent that sees the image and the caption answers "is this a correct description?"
   for every hard negative of the headroom and test folds (CPU, no GPU); items judged correct or unsure are dropped and
   counted; the false-negative rate with a binomial CI goes in the paper. A 50-item human spot check by Shlok if he has time.
5. Primary negatives remain deranged captions (probe-1 protocol), restricted when annotations exist to images that share no
   annotated category with the true image; the same audit on a 100-item sample.

**Alg. 12 CoherenceTest (M1, M11).** 100 clean calibration items; per item 4 image-token pairs $(j,k)$ (2 adjacent, 2 at
least 8 tokens apart), each in two contexts: all other image tokens visible, and a random half of them masked; caption masked.
Three passes per pair and context: $\{j,k\}$ masked; $j$ revealed; $k$ revealed. Gap
$g=[\log p(x_j\mid R)+\log p(x_k\mid R,x_j)]-[\log p(x_k\mid R)+\log p(x_j\mid R,x_k)]$, zero for a coherent model.
Noise floor: for 25 of the 100 items, the same three passes repeated in a different batch composition, $g_0$ = difference between the repeats.
Pre-stated reading: "coherent within numerical noise" if the median $|g|$ is within the 95th percentile of $|g_0|$;
"incoherent at the evidence scale" if the median $|g|$ exceeds the clean mean per-token paired evidence $\mu$ measured in M4.
In the second case Props. 1 and 6 are reported as not applicable to this model at the scale that matters. Cost: 2,400 + 600 = 3,000 passes (derived).

---

## 11. Deadline plan (assumes GPU released Wed 28 Oct daytime, Shlok present; staged test first)

Per-row time estimate: **0.15 s** (conservative). Basis: a batch-4 forward at about 1.1k tokens takes about 0.44 s, i.e. about
0.11 s per row (crash diagnosis); probe-2 items took 7.5-10.4 s for about 65 rows plus 3 VQ encodes (crash diagnosis, from
`items.jsonl`), at most about 0.16 s per row including encodes (derived). VQ encode: unmeasured, assumed at most 1 s (estimate,
to be measured in M0 stage 3). All GPU-hour figures are item time and are **estimates**; wall time is about 2x at duty 0.5.

### 11.1 MUST (about 2.6 GPU-h estimate; 3.9 with a 50 percent contingency; limit about 6)

| ID | What | Code status | Passes / encodes per item, itemised | Items | GPU-h (estimate) |
|---|---|---|---|---|---|
| M0 | Crash-diagnosis stages 0-3: CPU tests; load and one forward then 5 min idle; `run_probe1 --limit 10` on new items; `run_probe2 --limit 5` (items 21-25) with the diagnosis's guards (AC check, 1 s telemetry, abort rules) | existing code; guard changes proposed in the diagnosis need Shlok's approval | probe 1: 58 rows; probe 2: about 65 rows + 3 encodes | 10 + 5 | 0.05 |
| M1 | Complete probe 2 unchanged (items 21-199), then a post-hoc job: $D^I$ for each caption length present (at most 28 passes in total) and, if U7 allows, the Trust-but-Verify-style pass on the stored codes (4 corrupted images x 1 pass) | probe 2 unchanged; post-hoc job is new but uses only `masked_logprobs` with existing Spec patterns | probe 2 as is (A, B for 4 corruptions + prior pass); post hoc 4 | 179 (+200 post hoc) | 0.52 + 0.04 |
| M2 | Calibration fold: clean encode; $B$ ($K=8$, caption masked) = 8; fusion inputs: text direction full-mask for $c^+,c^-$ = 2; image direction caption-only for $c^+,c^-$ = 2 | Spec patterns from probes 1-2 | 12 passes + 1 encode | 300 | 0.23 |
| M3 | Headroom check (Alg. 9): encodes clean, JPEG q10, q5, noise 0.10, 0.20, splice 128, 192 = 7; caption-only passes 2 | probe-1 b_full pattern | 2 passes + 7 encodes | 100 | 0.20 |
| M4 | Main test: per item, images = clean + up to 3 family corruptions + patch (sanity) = 5; $B$ gate 8 per image = 40; TbV-style 1 per image = 5 (if U7); image direction 2 (all arms); text direction (conditioning) for the 3 realistic corruptions x 2 captions x {none, GATE-M, geo seed 1, changed-code} = 24, clean x 2 x {none, GATE-on-clean} = 4; encodes: clean, 3 realistic, 2 denoised = 6 | text-direction arms with gated image tokens masked are the probe-1 `afull` pattern plus `extra` | 75 passes + 6 encodes | 300 | 1.44 |
| M5 | Coherence test (Alg. 12) | new indexing, existing Spec | 24 passes (+24 on 25 items for the noise floor) | 100 | 0.13 |
| — | CPU, in parallel: unit tests L1-L9 (v1), folds, cheap baselines, denoiser, deranged-negative audit, Appendix A rerun, analysis scripts | CPU | — | — | 0 |

Total item time: 0.05 + 0.56 + 0.23 + 0.20 + 1.44 + 0.13 = 2.61 GPU-h (estimate).
What MUST delivers: detection AUROCs against cheap baselines (M1), a calibrated gate with realised FAP (M2 + M4 clean arm),
the headroom decision (M3), the primary contrast and all mechanism controls on the image direction, the text-direction
conditioning arms, the denoise defence, the Prop. 4 plug-in check, the coherence test. That is a complete measurement paper
on one model if the GPU holds.

### 11.2 SHOULD (about 2.8 GPU-h estimate)

| ID | What | Passes per item | Items | GPU-h (estimate) |
|---|---|---|---|---|
| S1 | Caption typos (v1 E4): captions clean, typo-1, wrong, wrong+typo; word gate $B^T$ with image masked 8 x 4; text direction 4 arms x 4; image direction with gated captions 4 x 4; reports gate-induced false acceptance (F2) | 64 | 300 | 0.80 |
| S2 | Re-infill (needs the new sampling loop): I, M+I, R1 versus caption-visible leakage control, UniDisc-G.1-style (random gate of equal size, $n=4$ re-infills, best of $n$ by own likelihood); $S_r=16$; JPEG and patch | about 208 | 150 | 1.30 |
| S3 | Hard negatives (Alg. 11, needs annotations): 2 per item, text direction on clean + 3 realistic images x {none, GATE-M} = 16, image direction 2; fusion weights refitted on calibration hard negatives (+4 per calibration item) | 18 (+4) | 300 (+300) | 0.28 |
| S4 | Denoise + GATE-M (gate on denoised images): 2 x 8 | 16 | 300 | 0.20 |
| S5 | Ablations: $K\in\{4,16\}$ for $B$ on JPEG and noise (20 x 2 = 40 passes) | 40 | 100 | 0.17 |
| S6 | Contamination check (U8): read UniDisc and LlamaGen training-data statements | CPU | — | 0 |

### 11.3 COULD
- **E7 Omni-Diffusion 8B 4-bit.** Stays in COULD. Reasons: per-pass time and peak memory never measured; a 16 GB checkpoint
  streams through CPU memory, where large CPU allocations have crashed Python on this machine (red team X4, earlier file);
  the crash hypothesis H1 concerns load ramps, which an 8B model makes larger; a second model arriving Friday would add
  claims nobody has time to red-team. Gate: a 20-pass measure-only chunk under the same guards; size anything further only
  from that measurement. Without E7 the paper is scoped to one model (M9).
- T2I typo grid and CLIPScore (CLIP weights unverified, weak generator); R2 repair figures; Mondrian calibration; iterated
  gate; fp32 output head (U5); $N=5$ matching.

### 11.4 CPU-only fallback (GPU stays on hold)
Everything here runs without a CUDA context.
1. Unit tests L1-L9 with the fake network; synthetic CRC validity study.
2. Probe-2 partial data (20 complete items of 21 rows, `runs/P2-PROBE-02/arrays`): AUROC of s1, s_cm (= s1 - r_original),
   s2, r_original, s3, random against the cheap baselines, per corruption. Labelled exploratory, n = 20, no $q$ (needs $D$,
   a GPU pass). This is the red team's own suggested next test.
3. Cheap baselines and changed-code fractions $\rho$ for JPEG/noise/splice at each severity on many images: needs the VQ-16
   encoder on CPU (a standalone loader for `vq_ds16_t2i.pt` is new code; memory small; unverified).
4. Probe-1 reanalysis (Appendix A), power inputs, hard-negative construction and audit.
5. Output: a feasibility and measurement note (theory, calibration machinery, partial detection evidence). It is **not** an
   Information Fusion research article; if the GPU stays on hold past Thursday noon, the honest options are that note or a
   later deadline. Shlok's decision.

### 11.5 Timeline and stop rules
| When | GPU (Shlok present) | CPU in parallel | Stop rule |
|---|---|---|---|
| Wed 28, day | M0 stages 1-3 (about 45 min wall) | stage 0 tests; folds; baselines; deranged audit | any abort rule of the crash diagnosis or a crash at stage 2 -> GPU on hold, go to 11.4 |
| Wed 28, afternoon-evening | M1 in 5-min chunks (about 1.2 h wall), then M2 + M3 (about 0.9 h wall) | analysis of M1; `family.json` from M3 | M1 falsifier met on JPEG and noise -> continue M4 only as a measurement of a negative result; M3 empty family -> skip M4's downstream claim, run M4 for detection and calibration only |
| Thu 29 | M4 (about 2.9 h wall) + M5 (about 0.3 h wall); then S1, S3, S4 if stable | statistician analysis; figures; writing Methods from this spec | crash -> stop GPU, write from what exists |
| Fri 30 | S2, S5 if time; results frozen by 12:00 | manuscript, red team on results, humanizer, citation check | no new runs after freeze |
| Sat 31 / Sun 1 | none | submission package | — |

Unattended overnight GPU runs: not planned; the crash diagnosis's protocol assumes Shlok present. That is his call.

---

## 12. Still open (stated plainly)
- **B3 (partly):** the crash cause is a hypothesis. The plan depends on M0 passing; nothing in the method can change that.
- **M7:** IF fit. Proposed check (CPU): give the abstract and Figure 2 caption to a fresh agent with no project context, ask
  "what is fused, and is this an information-fusion contribution?", and record the answer before submission.
- **Novelty:** narrow (re-audit 0.50); a concurrent "input remasking in unified MDMs" paper may exist under review.
- **One model** (M9), **contamination** (U8), **U7** (TbV-style baseline may be inapplicable).
- **Fusion** may be untestable if S3 does not run.

## 13. Citations to verify before use (citation-validator)
Conformal risk control (Angelopoulos et al.; id from memory, not given); a CFAR reference; a sensor fault detection and
isolation reference; a decision-fusion (naive-Bayes/log-likelihood-ratio fusion) reference; Rubin on missing data; McNemar;
Trust but Verify 2610.22380; Gomes et al. 2504.01225; CO2Jump 2607.13188; Token-Critic 2209.04439; uChecker 2209.07068;
Diffusion ITM 2305.16397 (ids from the re-audit and the red team).

---

## Appendix A. Script used for the probe-1 numbers (CPU, 2026-10-28)
Run from the worktree root with the default `python`; output quoted in sections 7.2 and 9. Not stored in a run directory;
the statistician should rerun it into `runs/P2-PROBE-01/` (for example `headroom_clean.json`).

```python
import json, statistics as st
r = [json.loads(l) for l in open('runs/P2-PROBE-01/items.jsonl')]
def stats(f, name):
    d = [f(x['true']) - f(x['mis']) for x in r]
    sd = st.stdev(d)
    print(name, 'acc', round(sum(v > 0 for v in d) / len(d), 3), 'mean', round(st.mean(d), 4), 'sd', round(sd, 4),
          'n_wrong', sum(v <= 0 for v in d), 'n_|d|<0.5sd', sum(abs(v) < 0.5 * sd for v in d))
stats(lambda s: s['bfull'], 'bfull')
stats(lambda s: s['b8'], 'b8')
stats(lambda s: s['afull'] - s['afull_null'], 'afull_pmi')
stats(lambda s: s['afull'], 'afull')
```
Output: `bfull acc 0.843 mean 0.1815 sd 0.1963 n_wrong 47 n_|d|<0.5sd 85`; `b8 acc 0.783 mean 0.0046 sd 0.0063 n_wrong 65
n_|d|<0.5sd 115`; `afull_pmi acc 0.99 mean 2.4029 sd 1.1106 n_wrong 3 n_|d|<0.5sd 10`; `afull acc 0.943 mean 2.4029 sd 1.7711
n_wrong 17 n_|d|<0.5sd 46`. Scores in `items.jsonl` are per-token means (`run_probe1.py`: `out = {t: sums[t] / cnt[t]}`).
Ties ($d=0$) count as wrong. The three accuracies match the probe report.
