```yaml
agent: red-team (hostile area chair + ambition critic)
date: 2026-10-28
brief: Attack PANEL-P2-PLAN (mdm-expert upgrade plan for Paper 2, GATE, Information Fusion research article); verify the sigma=None concern; assess "think bigger" options under the preregistration; hostile IF review
sources_examined:
  - research/CONTRACT.md
  - research/paper2/benchmark/PANEL-P2-PLAN.md (all)
  - research/paper2/benchmark/LENS-ARGUMENT.md (headings, section 8); LENS-CRAFT.md (headings only)
  - paper2/main.tex; paper2/sections/{introduction,method,results,discussion,conclusion}.tex (all); protocol.tex lines 37-70, 240-262; wc -w of all sections
  - research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md (all); PREREG-GATE-MUST-v3 lines 140-155, 210-218
  - research/paper2/prereg/SAP-GATE-2026-10-28.md sections 2-7, 9, A2.2, AB.1-AB.5 (headings of the rest)
  - research/paper2/CONFIRM-EVENING-2026-10-28.md sections 4-11; LEAD-ATTESTATION-A2 (grep)
  - runs/P2-GATE-M1/analysis.json (every key), tbv_verdict.json, detection_frozen.json (head); runs/P2-GATE-M2/items.jsonl (line count)
  - research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md sections 0-6; NOVELTY-REAUDIT-GATE section 7
  - research/paper2/related/INFFUS-CITATIONS-2026-10-28.md sections 2-5
  - exp_p2/scoring.py (all); exp_p2/gate/theory.py (all); exp_p2/gate/detect.py lines 1-80; exp_p2/run_gate_m4.py (grep: stored arrays)
  - exp001/unidisc_net.py lines 1-80; runs/env-2026-10-14/scripts/unidisc_setup.py lines 1-40
  - models/third_party/unidisc at 3ee3e47a9e64bac2fdca59957726f14723371ced (clean tree): configs/config.yaml, configs/experiments/{large_scale_train,large_scale_train_high_res_interleaved,large_scale_high_res_interleaved_inference}.yaml, configs/model/extra_large.yaml, model.py lines 424-560 and 640-800, model_setup.py lines 630-685, models/dit.py lines 1064-1140, 1180-1300, 1324-1390
  - checkpoint key names of unidisc_interleaved.pt (HF snapshot 2b344ca8...), read from pytorch_model_fsdp/data.pkl inside the zip, no tensor loaded
coverage: >
  Not read: the SR survey PDF; LENS-CRAFT body; related.tex; protocol.tex outside the lines named; SAP addenda A3, A3b, AD.*
  except as quoted by the card; IF-METHOD-ANATOMY (the plan's word-count and figure-position rules from it are unchecked);
  Zhou & Lu full text (E1 for everyone). Nothing was run on a GPU; no model was instantiated. No edits to manuscript, code,
  prereg files or ledgers (brief). Ledger rows added: 0 (brief forbids ledger edits).
claims:
  - statement: "UniDisc's backbone, as configured for the checkpoint the project loads, has no time/sigma pathway; sigma=None is the authors' own inference setting, so exp_p2/scoring.py:111 and :162 are not a defect."
    status: supported
    evidence: "configs/config.yaml:15 time_conditioning False (no experiment overrides it; grep of configs/); models/dit.py:1105, 1186-1188, 1377-1379 (sigma_map None, c=None); dit.py:1078-1090 (final layer without adaLN); large_scale_high_res_interleaved_inference.yaml:30-31 force_null_sigma/allow_null_sigma true; model.py:660-662; checkpoint pickle has no sigma_map/adaLN keys"
    level: E3
    confidence: 0.92
  - statement: "Every M1 number quoted in PANEL-P2-PLAN section 5.0 matches runs/P2-GATE-M1/analysis.json."
    status: supported
    evidence: "analysis.json keys table.*, paired_q_vs_best_cheap.*, falsifier.*, chance_bar_both.verdict"
    level: E4
    confidence: 0.95
  - statement: "On the realistic corruptions the non-finetuned one-pass TbV score has higher mean per-item AUROC than q (JPEG 0.581 vs 0.561; noise 0.607 vs 0.503) while q is far above TbV on patch and swap (0.961 vs 0.854; 0.955 vs 0.859); the plan does not draw this out."
    status: supported
    evidence: "runs/P2-GATE-M1/analysis.json table.{jpeg,noise,patch,swap}.{q,tbv}"
    level: E4
    confidence: 0.9
  - statement: "The plan's synthesis framing ('when does input gating help', C6, Fig 5, ranked take-aways with mechanism) cannot be delivered under a P null without breaking SAP AB.1."
    status: supported
    evidence: "SAP AB.1 items 1(a), 2, 3; card v4 section 2 B-1; PANEL-P2-PLAN 1.2 C6, 5.1 title rule, 1.1 row 6"
    level: E2
    confidence: 0.8
competing_explanations:
  - "Patch/swap AUROC near 0.96: uniform random codes are improbable under any context model; even neighbour codebook distance reaches 0.74-0.79 (analysis.json table.*.nbr). Shows the pipeline works, not that the gate sees realistic damage."
  - "Texture-with-flipped-sign win on JPEG/noise: the changed-code label marks tokenizer instability in flat regions, not damage (label circularity, v3 line 151)."
unknowns:
  - "Whether model keys absent from the checkpoint were silently initialised: the loader uses strict=False (model_setup.py:665 with config.yaml:188); not checkable without instantiating the model."
  - "Splice detection AUROC (no M1 cell; M4 stores the arrays)."
  - "Zhou & Lu full text (E1)."
  - "Whether COCO val2017 images are in UniDisc's training mix (cambrian_10m_v5 is in large_scale_train_high_res_interleaved.yaml:34; its COCO content is E0, my background knowledge)."
next_test: {hypothesis: "n/a (review)", intervention: "n/a", primary_metric: "n/a", falsifier: "n/a", gpu_hours: 0}
```

# Red team on PANEL-P2-PLAN (Paper 2, GATE, Information Fusion)

Scope note. Sections A, B and D are attack only. Section C was requested explicitly by the orchestrator ("think bigger");
it is written as an adversarial assessment of options (what each would add, what it would cost, how it could overclaim), and
it is kept separate so that it does not soften A or D.

Severity scale: **fatal** blocks the gate until the orchestrator records a resolution in the decision ledger; **major**
would draw a reject-level reviewer comment or break the timeline; **minor** is a correctness or polish defect.

---

## 0. Verdict in six lines

1. The plan makes the paper look like the benchmark, but it does not deal with what the evidence implies. The only analysed
   result (M1) says the preregistered detector **fails on both realistic corruptions** it was tested on, and the preregistered
   prior for the headline is low (spec 0.35; red-team 0.05-0.08 for a positive claim; v3 lines 210-216).
2. One framing choice is **fatal unless resolved**. The "when does input gating help" synthesis (C6, Fig 5, the question title,
   take-aways "with mechanism") can only be answered under a P null by using PS, E-pred, E-dec or detection as an explanation,
   and AB.1 forbids that.
3. B is **not a defect**. sigma=None is UniDisc's intended inference path, the architecture has no time input, and the
   checkpoint has no time weights. M1 and the pending stages are unaffected.
4. The plan's numbers check out against `runs/P2-GATE-M1/analysis.json`.
5. The plan is over-scoped for the freeze: 9 figures, 11 tables, a renaming of 20 symbols and 14 CPU work items, while the GPU
   sheet needs roughly 16-19 wall-h, has stalled twice in two hours, and slowed down when CPU agents were running.
6. A hostile Information Fusion reviewer rejects this paper on substance (fit, breadth, a weak task, a detector beaten by
   one-pass and texture baselines), not on craft. Better craft does not move that verdict.

---

## A. Attack on the plan (ranked)

### A1. FATAL (conditional on a P null, the most probable labelled outcome): the synthesis framing contradicts AB.1
- **What the plan says.** C6 is "A synthesis: when does input gating help". Fig 5 sets "conditions stated in advance" beside
  every measured cell, including the PS rows, the detection AUROCs and E-pred. Discussion 6.1 has "ranked take-aways with
  mechanism". The conclusion has "ranked take-aways". The question-form title is "allowed for every outcome because it claims
  nothing" (PANEL 1.2, 1.1 row 6, 3.2 Fig 5, 5.1).
- **What binds.** AB.1 item 2 says a P null is reported "with no causal clause drawn from PS, E-pred, E-dec, S2, B, R or the
  suite, in the title, abstract, highlights or conclusion". AB.1 item 1(a) bans "the gate works where detection is easy" and
  any use of PS as a demonstration, "whether PS is met or not". AB.1 item 1(b) bans "predicted" or "explained" for any P
  result. AB.3 item 4 allows "predicted" only inside the E-pred table.
- **Why it is fatal.** Under a P null, the only data that could answer "when does it help" are PS (patch and swap, expected to
  pass), detection (S-D) and E-pred. Fig 5 places exactly those beside the P cells, with the conditions of method.tex:235-247
  as row labels. The figure itself makes the forbidden inference: helps where detection is easy and conditions (ii)/(iii)
  hold, fails where they do not. A title that asks a question the paper is barred from answering is an overclaim by
  construction. Shlok approved D18 ("when does input gating help", CONFIRM-EVENING section "Shlok's answer" item 7), so this
  is a conflict between two recorded decisions, not a drafting slip.
- **What forces rejection of the framing.** Any sentence, caption or figure layout in title, abstract, highlights,
  conclusion or Discussion 6.1 that links a P null to PS, detection or the conditions (ii)/(iii).
- **Resolution needed in the ledger.** How the title, Fig 5 and 6.1 read under each A2.2 label. In particular, whether
  Fig 5 may show PS and P cells on one canvas at all.

### A2. MAJOR: the plan upgrades craft against a survey benchmark, not substance against an IF method-paper reviewer
- Moser et al. is a survey. Six of the plan's ten "beats" rows (PANEL 6.1) compare a preregistered research article with
  defects of a survey: no search protocol, a decorative taxonomy, copied numbers. That comparison is a category error. Nobody
  will judge Paper 2 against a survey.
- What decides acceptance at Information Fusion is a fusion contribution, empirical breadth and a method that beats fusion
  baselines. The plan adds no new evidence on any of these. Its 63 % to 37 % word rebalancing and its 9 figures are a better
  package for the same evidence.
- **What forces rejection.** Reviewer comment: "well-presented negative measurement of one 1.4B model on COCO random
  negatives; out of scope". The plan contains nothing that pre-empts it (see D).

### A3. MAJOR: C1 and C3 sell the detector against the M1 evidence
- C1 is "A reliability gate ... built from one masked-likelihood primitive". C3 is "A detection map of what a generative model
  can see". The M1 evidence is as follows (`runs/P2-GATE-M1/analysis.json`):
  - q is at or near chance on the realistic corruptions: JPEG 0.561 [0.547, 0.575], noise 0.503 [0.493, 0.513].
  - The non-finetuned one-pass TbV score is **above q on both**: JPEG 0.581 [0.569, 0.593], noise 0.607 [0.597, 0.618], with
    non-overlapping marginal intervals on noise. No paired q-vs-TbV test exists, and none may be added as confirmatory.
  - Texture with its sign chosen on the data reaches 0.756 and 0.768.
  - The null normalisation that motivates q over plain-B is slightly harmful on patch (-0.0033) and swap (-0.0053),
    and q equals plain-B within about 0.008 on JPEG and noise (table.*.plainB vs table.*.q).
  - The mask-then-score design beats the one-pass score only on the uniform-code sanity corruptions
    (patch q 0.961 vs TbV 0.854; swap 0.955 vs 0.859).
- The plan reports all of this in Table 6 and Fig 4, which is correct. But its contribution list and fusion paragraph
  present the primitive as the asset. A reviewer will read M1 as: "the paper's detector loses to a single forward pass on
  realistic damage, and its distinguishing design choice (D-normalisation) does nothing".
- **What forces rejection of C1/C3 as worded.** The M1 table itself.

### A4. MAJOR: contributions promise stages that are probably "not run"
- C5 ("Repair, two-way fusion and a second model") lists Omni R, which runs only if P+ is non-empty (card v4 section 2,
  AD.7). That depends on the outcome judged least likely (positive claim about 0.05-0.08, v3 lines 210-216).
- FOIL B can be "untestable at ceiling". Probe-1's full-mask text direction is 0.990 on clean random negatives
  (protocol.tex:255, run P2-PROBE-01). FOIL negatives are harder, so the ceiling is unknown, but the risk is real.
- S2 is last in the run order and is 3.9 busy GPU-h (CONFIRM section 8, estimate).
- A numbered contribution that is "not run" is an overclaim in the introduction. It also breaks the plan's own rule
  (roadmap checked against the delivered content).
- **What forces rejection.** A contribution bullet whose Results subsection says "not run".

### A5. MAJOR: the most probable stage-level outcomes are not planned for
- **K1 / R3 risk is not treated.**
  - Splice at 128 px touches about 64-81 of 1,024 token cells (derived: 16-px tokens, detect.py:22; protocol.tex
    corruption table). Diluting about 6-8 % of tokens rarely flips the sign of a mean margin. JPEG codes change where the
    tokenizer is unstable, not necessarily where the evidence changes.
  - So D* (binary flips) may be small. That leads to rule R3, where the primary endpoint becomes d_R (SAP 4.6).
  - Under R3, "verification" and "improved" are banned, S-M is uninformative in advance, and "trimming heavy-tailed tokens
    can raise d" must accompany every d (v3 line 214). The plan's C4 ("changes a cross-modal decision") and Fig 6 headline
    do not survive R3. It has one axis note and no R3 framing.
- **There is no splice detection evidence at all.** M1 has swap, patch, JPEG and noise only (analysis.json table keys).
  Splice is the claim-bearing realistic cell of both P and S2 (AD.5). Its detection AUROC appears only after M4 (M4 stores
  `*_B`, `*_D`, `*_z`: run_gate_m4.py:144-157). If splice detection is near chance, S2-splice is close to decided before it
  runs.
- **What forces rejection.** A P null, K1 on two of three corruptions, or R3. All are within the preregistered expectation
  (v3 line 216).

### A6. MAJOR: the timeline cannot carry the plan
- GPU: about 8-9 busy / 16-19 wall-h for the whole sheet (CONFIRM section 8, estimates). M2 is at 114 of 300 rows and halted
  since 21:45 IST on 28 Oct until Shlok answers (CONFIRM section 11; `runs/P2-GATE-M2/items.jsonl` 114 lines). There were
  two slow-item stops within about two hours, and the second came with three CPU agents running and free RAM at 4.15 GB.
  The freeze is Fri 30 Oct 18:00 IST.
- CPU: 14 work items (W1-W14), 9 figure generators, 11 table generators, a renaming of 20 symbols across three .tex files,
  and an appendix crosswalk. The plan itself says to run CPU agents only while the GPU is idle (PANEL 7). Those two
  constraints conflict: either the GPU sheet slips or most of the CPU list happens on Saturday.
- Fig 8 needs row 9 (S2-FIG, GPU), the last stage of the sheet. Fig 1's overlay needs `threshold.json` (M2, incomplete).
  Fig 9 needs FOIL. Five of nine main figures wait on the GPU.
- **What forces rejection.** Submission without M4. Shlok already ruled that out: move the deadline (D18).

### A7. MAJOR: the notation pass (W2) damages the audit trail it is meant to serve
- The SAP, card, `theory.py` and frozen output keys use alpha, beta, rho, mu_c, sigma2_c, alpha_obs and beta_obs
  (theory.py:15-47; SAP 4.1 A4; E-pred). Renaming them to a_0, a_1, Sigma_R, theta_hat and so on means every reviewer who
  opens the Zenodo/OSF artefacts has to use a crosswalk to check a number.
- 20 renames made by an agent across method/protocol/results under deadline is the classic way to introduce equation
  errors. An equation error in a paper whose selling point is rigour is worse than symbol overload.
- **What forces rejection.** One mismatched symbol between paper and preregistration that a reviewer finds.

### A8. MAJOR: the "fusion" claim rests on an independence assumption the data violate
- The paper calls the per-token sum "the naive-Bayes rule of distributed detection" (`chair1986optimal`; method.tex:385;
  PANEL 1.3). Chair-Varshney optimality needs sources that are conditionally independent given the hypothesis. Image tokens
  are strongly dependent: each Delta_j comes from p(v_j | c) with the image fully masked, which is a product-of-marginals
  pseudo-likelihood.
- The SNR analysis (method.tex:290-314; theory.py) also assumes independent tokens.
- An IF reviewer who knows distributed detection will say that the fusion framing borrows the rule but not its conditions.
  On top of that, the gate is a hard 0/1 weight, where the classical answer is reliability-weighted (soft) fusion.
- **What forces rejection.** The question "why hard gating rather than reliability weighting or a robust combiner?",
  answered with no data.

### A9. MAJOR (task validity): the primary decision uses the weaker of two available statistics
- Probe 1: on clean random negatives the full-mask text direction scores 0.990 and the image direction 0.843
  (protocol.tex:255, P2-PROBE-01). The image direction was chosen because it has headroom (protocol.tex:257-258).
- A practitioner would use the text direction or fuse the two. Gating the weaker statistic so that a gate has something to
  repair makes the primary endpoint a constructed setting. The negative captions are deranged captions of other images
  (SAP 2.1), which is an easy matching task.
- **What forces rejection.** The reviewer question "in a deployment you would use the 0.99 statistic; what does the gate
  buy there?" Family B answers it only if it runs and is below ceiling.

### A10. MINOR: correctness and wording items in the plan
1. "Holm p 0.0004 each" (PANEL 5.0) is the bootstrap resolution floor: p = 0.00019998 = 2/10001 before Holm
   (analysis.json falsifier.*.p). Report it as a floor, not as an exact p.
2. Fig 4 and Table 6 list an "A - B control". analysis.json has no such key. It is presumably `r_original` (detect.py:6-7:
   B = s1 - r_original), but the mapping is not stated in the plan. It must be verified before the figure is labelled.
3. The Fig 1 item-selection rule is "written before viewing", but the M1 per-item AUROCs are already analysed. The rule is
   only pre-specified for image viewing, not blind to outcomes, and the caption must say so.
4. The texture rival exists only for JPEG and noise (no `tex` key under table.swap or table.patch; detect.py:9-10). Fig 4's
   facets will have empty texture cells for patch and swap. Mark them "n/a (no pixel image)", not "-".
5. The plan's IF anatomy figures (13-15k words, motivation figure on p.1-2) were not checked here. The plan cites a file
   outside my brief.
6. s3 (u^unc) is at chance on swap (0.495 [0.491, 0.498]) but 0.943 on patch. The s3 top-k control will look strong on
   patch for a reason (missing local context) that is unrelated to corruption detection. The plan does not anticipate this
   reading.

### A11. Numbers check (plan section 5.0 against `runs/P2-GATE-M1/analysis.json`)
All verified. q patch 0.961 [0.959, 0.963], swap 0.955 [0.952, 0.957], JPEG 0.561 [0.547, 0.575], noise 0.503 [0.493, 0.513].
plain-B 0.964 / 0.960 / 0.560 / 0.511. TbV JPEG 0.581, noise 0.607. tex_neg 0.756 / 0.768. q - rival JPEG -0.195
[-0.214, -0.175], noise -0.265 [-0.278, -0.253]. q - plain-B patch -0.0033 [-0.0042, -0.0026], swap -0.0053 [-0.0058, -0.0047].
n = 179 excluding dry-run items. JPEG 197 and noise 198 usable items. `chance_bar_both.verdict` PASSED. `tbv_verdict.json`
copy_suspected false. Word counts (wc -w): method 3534, protocol 3356, total 10990, results 687, conclusion 136. References:
49 entries in references.bib. M2 rows: 114.

---

## B. Verification: does `sigma=None` in the scorer misuse UniDisc?

**Verdict: no defect.** sigma=None is the intended inference path for this checkpoint. Evidence is E3 (code at the
pinned UniDisc SHA `3ee3e47a9e64bac2fdca59957726f14723371ced`, `git status` clean) plus a read of the checkpoint's
key names.

| # | Evidence | File:line |
|---|---|---|
| 1 | Default `time_conditioning: False`; `diffusion: absorbing_state`; `parameterization: subs`. No experiment config overrides `time_conditioning` or sets `force_time_conditioning` (grep of `configs/` finds only this line) | `configs/config.yaml:12,14,15` |
| 2 | The project composes exactly the official demo experiments `[large_scale_train, large_scale_train_high_res_interleaved, eval_unified, large_scale_high_res_interleaved_inference]` and loads `unidisc_interleaved.pt` | `runs/env-2026-10-14/scripts/unidisc_setup.py:17,30-35`; `exp001/unidisc_net.py:46-47` |
| 3 | The official inference experiment sets `force_null_sigma: true` and `allow_null_sigma: true`. The authors' own samplers then pass `None` | `configs/experiments/large_scale_high_res_interleaved_inference.yaml:30-31`; `model_eval.py:2057,2086,3019,3060,3186` |
| 4 | `forward` accepts `sigma=None` only when `allow_null_sigma` is true, then passes it straight on | `model.py:660-662, 691, 729` |
| 5 | The backbone builds a timestep embedder only if time conditioning is on. Otherwise `sigma_map = None` and the conditioning vector `c = None`, so sigma is never read | `models/dit.py:1105, 1186-1188, 1377-1379` |
| 6 | The final layer has an adaLN time modulation only under time conditioning | `models/dit.py:1064-1090` |
| 7 | `scale_by_sigma: True` in the model config is stored but never read in `dit.py` or `model.py` (grep: only the assignment) | `configs/model/extra_large.yaml:8`; `models/dit.py:1290` |
| 8 | Checkpoint key names (`pytorch_model_fsdp/data.pkl` in `unidisc_interleaved.pt`): blocks hold attention, mlp and norm1/norm2/post_ff_norm/pre_residual_norm; top level holds output_layer.linear, output_layer.norm_final, vocab_embed, modality_embed. **No `sigma_map`, no `adaLN_modulation`; the string "sigma" does not occur in the pickle.** The network was trained without a time input | HF snapshot `2b344ca856bd108b52a2d022a3463dace131249f` |
| 9 | `return_logits=True` returns the raw backbone logits before the SUBS step (which would force observed positions to a copy). The scorer's fp32 restricted log-softmax and the TbV "raw logits" are therefore meaningful | `model.py:784-788` |

**Training support of the mask patterns GATE uses (bears on A0/A1 and the coherence premise).**
- Training masks every position with one per-row rate `move_chance`, shared by both modalities (`model.py:438`).
- With probability `mask_entire_modality` it also masks one whole modality: 0.15 in `large_scale_train.yaml:137`, 0.2 in
  `large_scale_train_high_res_interleaved.yaml:70`. Which value the released checkpoint was trained with is not
  recoverable from the code (E1). The block logic is at `model.py:470-531`.
- So the patterns B (caption fully masked, 1/K of the image masked), D (everything masked) and Lambda (image fully masked,
  caption visible) are all in the training support.
- This supports A0 (absorbing-state masking of the joint sequence) and A1 (time-free conditional) at E3. Only the weight of
  these patterns in training is unknown.

**Effect on M1 and the pending stages:** none from sigma. The scorer's forward is the authors' inference forward.
`UniScorer.selfcheck` (scoring.py:136-171) compares against the same sigma=None path, so it could not have caught a sigma
issue. There is no sigma issue to catch.

**Residual caveat (minor, unknown).** `_load` passes `strict = config.trainer.disable_strict_load` (`model_setup.py:665`).
That is `false` by default (`configs/config.yaml:188`), so the state dict is loaded **non-strictly**. Model parameters that
are missing from the checkpoint would keep their initialisation silently. The checkpoint keys look complete for the DiT
layout, and the probe accuracies (0.843 / 0.990, protocol.tex:255) argue against a gross defect. Code reading cannot exclude
a silent partial load, though. One `load_state_dict` call that prints missing and unexpected keys would close it. That is a
CPU/GPU action this report does not take.

**What to write in the paper (assumption A1 of the plan):** "UniDisc's denoiser has no time input (time conditioning off in
the released configuration; no time-embedding weights in the checkpoint), and the scorer uses the authors' null-sigma
inference path." Cite the file:line evidence in App. A. Work item W9 of the plan is done by this section.

---

## C. Think bigger, honestly (options assessed under the preregistration)

Constraints that bind every option:
- **SAP 2.5 / card v4 section 2:** the headline comes only from family P, and no secondary family result may be an abstract
  headline.
- **AB.1:** nothing rescues or explains a P null.
- **SAP 7:** Tier-3 analyses are exploratory, use CIs only, and no Tier-3 p-value enters a claim.
- **Must-not list:** items 1-13 (NOVELTY-REAUDIT section 7; NOVELTY-CHECK-INFFUS section 4).

One consequence follows directly and kills the most tempting "big" move. **The M1 detection limit cannot be the paper's
headline**, however clean it is, because S-D is a secondary family. A bigger paper here means a deeper and better-anchored
version of the P measurement. It does not mean promoting M1.

### C.1 Must do (cheap, no new GPU, inside the rules)

| # | Idea | What it adds | What it needs | Overclaim risk | Fits before the freeze? |
|---|---|---|---|---|---|
| M-a | **Put the B verification in the paper (A0, A1 at E3)** | Removes a reviewer question ("is the scorer using the model correctly?"). It also turns "time-free denoiser" from a citation (`ou2025radd`) into a checked property of this checkpoint | Two sentences in Method plus a file:line table in App. A (section B above) | Low. Say "no time input in the released configuration", not "UniDisc is time-free in general" | Yes, about 15 min of text |
| M-b | **Rewrite the contribution list to what exists or is guaranteed to have a cell** | C1 becomes the gate as a measured object, not an asset. C3 states the detection limit with TbV and texture beside q. C5 is folded into "secondary families, reported as run or not run". This removes A3/A4 | M1 table (exists); card v4 section 2 | Low if every bullet maps to a delivered subsection | Yes |
| M-c | **Settle the title and the 6.1 framing for each A2.2 label before `analysis_m4`, in a dated row** | Removes A1 (fatal). For positive, inconclusive, negative and K1, the title, highlight 1 and the 6.1 opening sentence are fixed in advance, and Fig 5's layout rule is fixed (whether PS shares a canvas with P) | Orchestrator plus Shlok (D18 is his). The plan's W11 already writes three abstracts; extend it to titles and Fig 5 | This option *reduces* overclaim risk | Yes, CPU text only, but it must precede row 6 |
| M-d | **A theory figure with no data: the gating-helps frontier** | The closed form at method.tex:303-307 gives, for mu_c = 0, the region in the (alpha, beta) plane (false-alarm rate, flag rate on corrupted tokens) where hard gating raises the SNR of an additive LLR sum, with kappa = rho sigma_c^2 / ((1-rho)(sigma^2+mu^2)) as the only free parameter. The necessary condition beta > 2 alpha - alpha^2 is 0.0975 at alpha = 0.05 (derived). This is the paper's fusion-theory statement as one picture: how good must source validation be before discarding sources pays off? It needs no data and sits with the Section 3 analysis | `exp_p2/gate/theory.py` (pinned, unchanged; a new plotting script only reads it); a dated commit before `analysis_m4` | **Medium.** Overlaying measured (alpha_obs, beta_obs) points is E-pred content. It must use AB.3 wording ("agreed in A of K_eval"), never "predicted", and never sit in the abstract or conclusion as an explanation of a P null. With no overlay it is pure theory and low risk | Yes, CPU under 1 h; commit the plotting script before row 6 |
| M-e | **Name the classical-fusion competitors and pre-specify them as Tier-3 exploratory analyses on stored M4 arrays, in a dated note before `analysis_m4`** | Answers the fusion reviewer's first question (A8). Three candidates: (i) robust combiners of the same Delta_j (median, symmetric trimmed mean at the realised flag rate), which need no detector; (ii) soft reliability weighting, w_j a monotone function of u_j fixed in advance, as the evidential-discounting analogue (`huang2025evidential` in INFFUS-CITATIONS); (iii) the hard gate. M4 stores the per-token `*_delta`, `*_B`, `*_D` and flags (run_gate_m4.py:144-157), so this is CPU only | A dated note listing the exact combiners and parameters, committed before `analysis_m4` is first run; computed after the P section is committed (AD.12) | **High if mishandled.** If a detector-free robust combiner equals or beats GATE-M, that is a finding against the method and must be reported as such. It may never rescue a P null and never enters the abstract. Without pre-specification it is a forking-paths exercise and a reviewer will say so | Yes (CPU, 1-2 h after M4), *only* if the note precedes row 6 |
| M-f | **Make the M1 failure case the opening, with the honest two-sided reading** | LENS-ARGUMENT research rule 1. It also shows a real finding about unified MDMs: the model's own masked likelihood sees replacement by random codes (0.96) and barely sees JPEG or noise (0.50-0.56), and a one-pass score does better there. Information Fusion readers care about whether a source's self-consistency can validate it | analysis.json (exists); a Fig 1 rule note | Medium. K2 wording binds: no "q detects better than cheap methods", the rival is chosen on the data, and the texture win is reported as label circularity, not as an explanation. It is not the headline (SAP 2.5) | Yes |

### C.2 Nice to have (only if C.1 is done and the GPU sheet is on time)

| # | Idea | Adds | Needs | Overclaim risk | Fits? |
|---|---|---|---|---|---|
| N-a | **Detectability proposition** (Bayes-model statement): if the corrupted value at j is distributed as the model's own conditional given the visible context, every score that is a function of (x_j, visible context) has AUROC 0.5 against Z. Corollary: within-modality validation can only see off-manifold damage | Gives the M1 pattern a theoretical frame and connects to Trust-but-Verify's "plausible corruptions barely detectable" (NOVELTY-REAUDIT section 7) | Theory only; a three-line proof | **High.** It must not be used to say JPEG codes *are* on-manifold (not measured), nor to explain a P null (AB.1), nor as "texture explains" (K2). It is a statement about an ideal model, and it is close to obvious, so a reviewer may call it padding | Yes if written and dated before the M4 analysis; otherwise it reads as post hoc |
| N-b | **Correlated-token extension of the SNR analysis** (Var S with an intra-item correlation or design effect) | Answers A8 in theory and states when the independence approximation misleads | Theory only. It must not touch the frozen E-pred (`theory.py` and `epred_fit.py` are pinned, card v4 1.2) | Medium. It is a new proposition introduced after M1, so it must be dated before M4, labelled as not used by E-pred, and never presented as validated | Tight |
| N-c | **Label-instability descriptive figure:** P(Z = 1) against texture decile for JPEG and noise, from probe-2/M1 arrays plus regenerated pixels (detect.regen_pixels) | Makes the label-circularity concern visible instead of asserted. IF readers get a data-quality point about tokenised fusion inputs | CPU pixel regeneration for 200 images | **High.** K2 says the texture win "is reported as the red team's label-circularity concern, not as evidence that texture explains the corruption effect". This figure describes the label, so it is allowed only with that caption, labelled exploratory | Yes, CPU about 1 h, but it competes with the GPU for RAM (A6) |
| N-d | **Cost figure** (passes, seconds, peak memory per arm) | IF anatomy rule 33 (per the plan). Cheap and uncontroversial | Telemetry CSVs, config.json | Low | Yes, after the freeze |
| N-e | **Second mask-seed check (D4)** | Answers "does the gate depend on the partition?" | New code, audit and a pin row (card v4 section 5 item 6: no code at the pin) | Low | **Probably not**: it costs CPU agent time during GPU stages, which is the A6 risk |

### C.3 Ideas rejected because they break a rule or the evidence
- M1 detection as headline or title: forbidden by SAP 2.5 and the card v4 headline rule.
- "When does input gating help" answered with PS or detection under a P null: forbidden by AB.1 (A1).
- A q-vs-TbV or q-vs-texture *test* written as a claim: a new confirmatory comparison. Only the preregistered S-D falsifier
  exists.
- Pooling or "generalises" with Omni: forbidden by AB.5 and must-not 9.
- Any word from "fusion", "repair" or "robust" in the title without a P rejection with b > c (main.tex comment; red-team C4).
- A soft-weight or robust-combiner arm presented as "our improved method": unpreregistered and post hoc. Only the
  Tier-3 framing of M-e is allowed.

---

## D. Hostile Information Fusion review (as it stands and as planned)

**Summary.**
- The paper scores each image token of a COCO image-caption pair with UniDisc 1.4B's masked likelihood (caption withheld).
- It flags tokens above a threshold calibrated by conformal risk control on clean pairs, and drops them from an averaged
  per-token log-likelihood-ratio statistic that compares the true caption with a random other caption.
- A preregistered McNemar test against no gate is run on three pixel corruptions, with geometry-matched random gates,
  cheap detectors and a denoiser as controls.
- Secondary families cover re-infilling, two-direction fusion on FOIL and a 4-bit second model.

**Strengths.**
- Unusually careful preregistration, multiplicity control and null reporting.
- The guarantee is stated narrowly and correctly (CRC applied, B = 1).
- The evidence-separation rule is clear.
- The mechanism control (geometry-matched random gate) is the right one.
- The authors report a detection result that goes against their own method.

**Weaknesses (as stands).**
1. *Scope fit.* The "fusion" is the mean of per-token LLRs under an independence assumption that image tokens violate. The
   gate is a hard 0/1 weight. There is no comparison with reliability-weighted fusion, evidential discounting or robust
   combiners, which are the field's standard answers to unreliable sources (A8).
2. *The method's core does not work on realistic damage.* q is at 0.50-0.56 AUROC on JPEG and noise, below a non-finetuned
   one-pass score and far below a texture heuristic. Its distinguishing normalisation does nothing (M1).
3. *Constructed task.* A random-negative caption match on the weaker of two available statistics (0.843 vs 0.990 clean) is
   chosen for headroom (A9).
4. *Breadth.* One model, one dataset, synthetic corruptions, no training seeds, contamination unknown.
5. *Results.* The results section is empty apart from a pilot. The preregistration apparatus takes about 63 % of the words.
6. *Novelty.* The novelty is a composition of known parts ("incremental", 0.50; NOVELTY-CHECK-INFFUS section 0). The
   closest work in the journal (Zhou & Lu 2027) has been read only at E1.

**Weaknesses (as planned).** Items 1, 3, 4 and 6 are unchanged by the plan. Item 2 is reported honestly but still sits under
contribution C1/C3 wording. Item 5 improves only if M4 lands. The most probable outcome is P null or inconclusive, possibly
under R3 where only d_R is tested, with Omni not run. The paper is then a rigorous negative measurement, which Information
Fusion rarely publishes as a research article.

**Questions to the authors.**
- Why gate the image-direction statistic when the text direction is at 0.99?
- Why a hard gate rather than a reliability-weighted sum?
- What is the detection AUROC on splice, the only realistic corruption in S2?
- Would a median or trimmed mean of the same Delta_j, which needs no detector, match GATE-M?
- Under R3, how is the trimming effect on d_R separated from detection?
- Was COCO val2017 in the training mix (`cambrian_10m_v5` is in `large_scale_train_high_res_interleaved.yaml:34`)?

**Score.**
- As stands: **reject (3/10), confidence 4/5.** No results.
- As planned with a P null or an inconclusive P: **reject (3-4/10), confidence 4/5.** Out of scope and too narrow for a
  negative result.
- As planned with a P positive that survives S-M on a realistic corruption: **major revision (5-6/10).** Breadth and the
  robust-combiner question remain.

**The one experiment whose absence causes rejection.** A comparison of GATE-M with a detector-free robust or
reliability-weighted combiner of the same per-token evidence (median or trimmed mean of Delta_j at the realised flag rate,
and a soft weight in u_j) on the M4 test fold. Without it, a fusion reviewer cannot tell whether the gate adds anything
beyond robust aggregation, which is the oldest answer to unreliable sources in the field. (M4 stores the needed arrays,
run_gate_m4.py:144-157. It can only be Tier-3 exploratory, see C.1 M-e.)

**Three changes with the largest effect on acceptance** (the brief asks for them; listed by effect, not by effort):
1. **Settle the claim structure before `analysis_m4`**, with titles, highlights and the 6.1/Fig 5 layout fixed for each
   A2.2 label, consistent with AB.1. Drop or condition the contributions that may be "not run", and stop presenting the
   detector as the asset (A1, A3, A4). This decides whether the paper is internally consistent at all.
2. **Answer the fusion reviewer with data:** a pre-specified Tier-3 comparison against robust and reliability-weighted
   combiners on stored M4 arrays, plus the gating-helps frontier as the theory figure (C.1 M-d, M-e; A8). This is the only
   change that adds fusion content rather than packaging.
3. **Cut the main-text apparatus and face the task-validity question head on:** pins, deviations and the family table go to
   App. A. Method plus protocol fall from about 63 % toward the plan's target. One paragraph says why the image direction
   is gated when the text direction is near ceiling, and points to family B as the only test of the realistic two-direction
   setting (A9). Also verify Zhou & Lu in full text before the related-work paragraph is final (NOVELTY-CHECK-INFFUS
   section 6).

---

## Cheapest alternative explanation for each positive result (existing and possible)

| Result | Cheapest alternative |
|---|---|
| M1 patch/swap AUROC about 0.96 (q, plain-B), chance bar PASSED | Uniform random codes are improbable under any context model. TbV gets 0.85 and neighbour codebook distance 0.74-0.79 (analysis.json). This is a pipeline check, not a detection capability for realistic damage |
| M1 falsifier robust to reselection and to the dry-run exclusion | The changed-code label tracks tokenizer instability in flat regions (tex_neg wins), so every likelihood score is near chance against a label that is not damage |
| A future P rejection with b > c under R1/R2 | Dilution removed from any 5 % of tokens with low own-context likelihood, whatever their corruption status. S-M controls geometry only, not "low-B tokens are low-evidence tokens" |
| A future P rejection under R3 (d_R) | Trimming heavy-tailed Delta_j raises d_R (v3 line 214). There is no preregistered control for trimming. S-M is uninformative under R3 |
| A future S2 rejection on splice | Any detector with AUROC > 0.5 passes I-GATE vs I-RAND4 (AB.4 item 2). The kept draw is the best of 4 by own likelihood |
| A future B (FOIL) fusion gain | Two weights fitted on calibration pairs (Fisher LDA) against a single-direction baseline near ceiling. The gain is bounded by 1 - best single accuracy |
| A future R replication | 4-bit quantisation confounds the likelihood detector (AB.5 wording). The same test images are used under R2 |

## Concerns (for the orchestrator)
1. A1 is fatal-conditional. It needs a ledger resolution before row 6 (`analysis_m4`), because the framing must be fixed
   before the P outcome is seen.
2. CPU agent work during GPU stages, including this review, is the documented trigger of the second M2 stop
   (CONFIRM section 11). Sequence the plan's W-items against the GPU, not alongside it.
3. Non-strict checkpoint loading (B residual) is cheap to close with one key-diff print. It is not closed here.
4. Splice detection is unknown and splice carries the realistic cells of P and S2.
5. M-e is worth doing only if its dated note precedes `analysis_m4`. After that it becomes forking paths.
