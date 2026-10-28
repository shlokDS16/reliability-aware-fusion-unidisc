```yaml
agent: method-architect
date: 2026-10-28
brief: Debate round 1, Q1-Q5 from the method designer's view (GATE, Paper 2)
sources_examined: [research/paper2/debate/QUESTION-2026-10-28.md, research/paper2/MORNING-2026-10-28.md,
  research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (secs 2-11), research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md (N3-N6),
  exp_p2/gate/pipeline.py:44-58 (worktree HEAD 872cdd98, not the 623faaff pin)]
coverage: prereg card v3 and SAP not re-read line by line (only via spec and sign-off); FOIL and corruption-suite facts are E0 and must be checked by data-steward.
claims:
  - statement: In-network re-masking already exists in the frozen M4 tier, in the text-direction arms (pipeline.text_direction masks gated image tokens in the forward pass); only re-infill (imputation, repaired images) is missing.
    status: supported
    evidence: exp_p2/gate/pipeline.py:49-58; spec v2 11.1 row M4
    level: E3 (HEAD, not pin)
    confidence: 0.8
  - statement: In the primary image direction, dropping flagged terms is exact marginalisation, not an approximation, because the per-token fuser uses caption-only marginals that never see the image.
    status: supported (derivation)
    evidence: spec v2 2.3 and Alg. 5'
    level: E0 (derivation, unreviewed)
    confidence: 0.85
  - statement: GATE's within-modality score (other modality withheld) cannot, by construction, detect a fluent foil word such as a FOIL-COCO substitution.
    status: supported (derivation); untested
    evidence: definition of q (spec 4.1)
    level: E0
    confidence: 0.75
next_test: {hypothesis: "Prop. 4 plug-in, fitted on headroom items, predicts the sign of GATE-M minus none per corruption cell on test items",
  intervention: "corruption spectrum (patch, swap, splice, JPEG, noise + suite types) x 2 severities", primary_metric: "sign agreement over cells with CI excluding 0",
  falsifier: "agreement not above chance (exact binomial over cells)", gpu_hours: "about 0.7 extra (estimate)"}
```

# R1: method architect

## Q1. The single change that most raises significance
Change the claim from "GATE beats no gate" (one McNemar family, most probable outcome inconclusive per red team N4) to **a falsifiable
sensor-fault account of when input-token gating helps a unified masked-diffusion model, tested out of sample.** Concretely, the paper
contributes (a) a decomposition of the corruption loss into a *detection* part and a *treatment* part, and (b) a model (Prop. 1' + Prop. 4)
that predicts, per corruption, whether gating raises evidence SNR, checked on held-out items across a spectrum of corruptions.
Why: a measurement claim alone is thin for Information Fusion; a predictive account is valuable whatever GATE's win/loss pattern is.
A null on JPEG/noise then becomes a confirmed prediction (Prop. 1' (ii)-(iii) say it should be null), not a failed method. The fusion
framing becomes literal: image direction = distributed naive-Bayes fuser where dropping a sensor is **exact** marginalisation; text
direction = centralised fuser where the network itself marginalises (in-network mask). Both are measured in M4 already.

Endpoints to add (preregistered before the first M4 item):
- **E-dec (0 GPU):** per corruption, on the z-score endpoint, loss_total = z(clean) - z(none) split into treatment loss = z(clean) - z(chg-gate)
  and detection loss = z(chg-gate) - z(GATE-M); paired bootstrap CIs. All arms are in M4.
- **E-pred:** fit $\rho,\mu,\sigma^2,\mu_c,\sigma_c^2$ on the 100 headroom items, take $\alpha_{\rm obs},\beta_{\rm obs}$ from GATE on calibration/headroom,
  predict sign of $\Delta$SNR per cell; score sign agreement with observed GATE-M minus none on test items. Fitting and testing on
  disjoint folds avoids the circularity of the spec's same-data plug-in (5.3).

## Q2. Should S2 be MUST?
The writer's premise is half right. True in-network re-masking is already in M4 (text-direction arms, `pipeline.py:49-58`), but it sits on an
endpoint at ceiling with deranged negatives (0.990 in probe 1), so it shows nothing. What is truly absent is **re-infill (impute)**.
Recommendation: **S2-lite becomes MUST-conditional** (runs only after M4 finishes; first thing cut if M4 is late).
- **Alg. 13 ReInfill** (new code, CPU unit tests with the fake network first). Inputs: codes $\tilde v$, gate $G$, steps $S_r=16$, seed. 1. Set $v_G\leftarrow$[MASK],
  **caption masked** (leakage control: a caption-visible re-infill trivially favours $c^+$). 2. For $s=1..S_r$: one pass, unmask $|G|/S_r$ positions
  in a fixed random order, sample from $p_\theta$. 3. Return $\hat v$ and decode to pixels for figures.
- Arms (patch and splice, 150 items, 1 seed): GATE-I, chg-gate-I (oracle imputation), UniDisc-G.1 (random gate of equal size, best of 4 by own
  caption-masked likelihood). Image direction on $\hat v$ costs **0 passes** (gather from the cached caption-only $\Lambda^c$); text direction 2.
- What it shows: (1) **M vs I** on the text direction, where the Prop. 6 coherence argument applies (single imputation is a noisy draw of the
  marginal, so M >= I expected; I > M with CI excluding 0 refutes coherence). On the image direction, I only asks whether imputed codes carry
  caption evidence via scene context; say so, do not call it a Prop. 6 test. (2) Repaired-image strips (the figure reviewers ask for). (3) GATE vs
  G.1 at equal gate size: detection beyond random re-infill.
- Cost (derived from the spec's 0.15 s/pass): about (3 arms x 16 + 4 x 16 for G.1 + 6 text) per corruption x 2 x 150 items ~ 0.75 GPU-h item time (estimate).

## Q3. The three additions
| Addition | Method value | Risk | Cost (estimate) | Prereg/SAP change |
|---|---|---|---|---|
| Patch + swap in main test | The two-sided test of Prop. 1': gain predicted here, none on JPEG/noise. Code-level, so no encodes; image direction free | "Synthetic and easy" critique; post-dry-run decision | swap adds 8 B + 8 text passes x 300 ~ 0.2 GPU-h; patch already in M4 | Amendment A2: keep P_real (JPEG, noise, splice; Holm m=3) unchanged as primary; add P_struct (patch, swap; Holm m=2) as a separately labelled confirmatory family; add the interaction prediction (effect on P_struct > P_real). Disclose "decided after a 21-item dry run without q". Headroom H1/H2 also on P_struct |
| Omni-Diffusion 8B 4-bit | Answers "one small model". GATE needs only an adapter: encode/decode, mask id, `masked_logprobs(seq, mask_set)`. CRC is recalibrated on the same 4-bit model, so the guarantee holds for the model as run | Untested 4-bit on Blackwell, CPU-RAM crash history, SenseVoice fix; tokenizer details unknown (E0) | unknown until a 20-pass timing chunk; then passes x items x t_pass | Separate "replication" section declared before its first item: same K, alpha, arms reduced to none / GATE-M / chg / geo, 1-2 corruptions, 100-150 items; no tuning; 4-bit disclosed |
| Real benchmark | **FOIL-COCO is a misfit as a corruption to gate**: a fluent foil word is invisible to a within-modality score with the image withheld (by construction). Its real fit is as **published hard negatives**: it moves the text direction off ceiling, which makes two-way fusion (red team N5) and the in-network M arms testable, and replaces the self-built Alg. 11 audit. Real image-side alternative: a standard published corruption suite (ImageNet-C-style; E0, verify package and licence) | FOIL source, licence, COCO-2014 vs val2017 overlap with our folds, UniDisc training contamination: all unverified | negatives only: text 2 arms x 2 captions per image condition; ~0.3 GPU-h for 300 items (estimate) | Statistician addendum: FOIL negatives define a new secondary family (fusion gain, GATE-M vs none under corruption); data-steward check is a kill point |

## Q4. Improvisations (at most 2)
1. **Error-budget decomposition E-dec** (Q1). 0 GPU-h; one figure: per corruption, stacked detection vs treatment loss. Highest value per GPU-h.
2. **Corruption spectrum with out-of-sample Prop. 4 prediction E-pred**: 3-4 suite types x 2 severities on the 100 headroom + 100 test items, gate
   passes only (8 per image; image direction free), about 0.5-0.7 GPU-h (estimate). One figure: predicted vs observed $\Delta z$ per cell. This is the
   result that makes the paper about *when* gating works, which is the transferable knowledge.

Ablation map (what theory predicts): drop calibration (plain-B top-k) -> same mean effect, FAP no longer controlled; geometry-matched random gate ->
no gain if gain is detection, equal gain if it is gate shape; chg-gate -> upper reference only for P_struct (Prop. 1' (ii)); GATE on clean -> small loss,
never a gain ($\rho=0$); K 4 vs 16 (S5) -> detection AUROC changes, CRC validity does not.

## Q5. Plan that finishes Thu 29 evening
- **Now to ~14:00 Wed (CPU):** amendment A2 (P_struct, E-dec, E-pred, S2-lite, FOIL secondary) -> red-team + statistician sign-off before any M4 item;
  Alg. 13 + unit tests; data-steward FOIL/suite check. Kill: FOIL unverified by 14:00 -> drop FOIL, keep Alg. 11 status quo.
- **GPU order (on Shlok's yes):** M0 -> M1 -> M2 + M3 (now also headroom for P_struct and E-pred fitting) -> M4 with swap -> spectrum -> S2-lite -> Omni 20-pass
  timing -> Omni replication. Rough wall time from spec figures x2 duty: ~9 h to the end of S2-lite (estimate).
- **Kill points:** M0 abort -> CPU note (spec 11.4). M3 empty P_real -> P_struct + E-pred carry the paper. M4 not finished by Thu 10:00 -> cut spectrum to 2 types.
  Omni timing says replication exceeds remaining hours -> drop E7, scope stays one model. **Results freeze Thu 15:00**; nothing runs after.
- **Cut order (first cut first):** Omni replication, S5, S1, M5 coherence (keep only if S2-lite runs), spectrum to 2 types, S2-lite to patch only.
  Never cut M1-M4 primary or E-dec.
