```yaml
agent: red-team
date: 2026-10-28
brief: final sign-off review of the GATE MUST-tier preregistration package (spec v2, SAP + Addenda 1-2, card v2, code audit, implementation notes, novelty re-audit, TbV read, crash diagnosis) before any GPU outcome
sources_examined:
  - research/paper2/method/RED-TEAM-GATE-SPEC-2026-10-28.md (my v1 report)
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (lines 1-150 resolution table and framing; 160-398 scores, theory, calibration, endpoint, power; headings for the rest)
  - research/paper2/prereg/PREREG-GATE-MUST-v2-2026-10-28.md (lines 1-280, full body)
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (lines 229-304, 656-883: scenario map, n-rule, headroom rule, Addenda 1-2)
  - research/paper2/prereg/GATE-CODE-AUDIT-2026-10-28.md (verdict, criteria table, findings list by grep)
  - research/paper2/method/GATE-IMPLEMENTATION-NOTES-2026-10-28.md (grep-level: dry run, hard negatives, tests)
  - research/paper2/probes/PROBE2-CRASH-DIAGNOSIS-2026-10-28.md (full)
  - git: log, diff --stat 2ab42a6e..HEAD, git show a1ac5f01 (analysis_m4.py, headroom.py), sha256sum of SAP, folds and spec v2
  - runs/P2-PROBE-02/HOLD.txt (present)
coverage: >
  NOT read in full: NOVELTY-REAUDIT and TRUST-BUT-VERIFY-READ (their content is taken from the card and spec v2 quotations, E1 here);
  the whole SAP body outside the lines listed; spec v2 sections 8-9 and 11 beyond the headings; the source of exp_p2/gate/* except the
  a1ac5f01 diff; the 8f897235, f16dda8c and e6e1c902 diffs (stat only). I did not re-run any test, script or the sha256 of the card's other
  pins (notes, audit, diagnosis, re-audit). No GPU. No invented numbers: figures are copied with their location or marked derived/judgement.
claims:
  - statement: "The card's own pre-launch check fails at HEAD: `git diff --quiet 2ab42a6e HEAD -- exp_p2 tools tests runs/P2-GATE-FOLDS` exits 1."
    status: supported
    evidence: "run in this session; git diff --stat shows 23 files, 682 insertions, 74 deletions, under exp_p2/ and tests/ (commits a1ac5f01, f16dda8c, e6e1c902, 8f897235, cd861649)"
    level: E4
    confidence: 0.95
  - statement: "SAP, folds and spec v2 SHA-256 equal the card's pins."
    status: supported
    evidence: "sha256sum: SAP b4e0bf57..., folds 450edb54..., spec v2 04470bef..."
    level: E4
    confidence: 0.95
  - statement: "Under rule R3 the analysis code prints the sentence 'GATE-M improved image-direction verification over no gate' although the primary endpoint is d."
    status: supported
    evidence: "git show a1ac5f01, analysis_m4.outcome_reading: the positive branch builds the sentence without reading `rule`"
    level: E3
    confidence: 0.9
competing_explanations:
  - "A null in family P is explained by changed-code labels sitting in low-texture regions that carry little caption evidence (not by gate failure)"
  - "A positive under R3 is explained by variance-trimming of the d ratio (mean/sd), not by corruption detection"
unknowns: [crash cause, whether any corruption has an operating point, D* (hence rule R1/R2/R3), whether q beats the cheap rivals, OpenCV default strength vs sigma 0.10]
next_test: {hypothesis: "the package is internally consistent at one pinned commit", intervention: "card v3 with a re-pin, gate-auditor re-audit of the four post-pin commits", primary_metric: "pre-launch check exit 0 and audit criteria all met", falsifier: "any criterion unmet", gpu_hours: 0}
```

# Red-team sign-off: GATE MUST-tier preregistration (2026-10-28)

## Verdict

**SIGN WITH CONDITIONS, confidence 0.6 that this is the right call.** The package is a sound design for a measurement: it fixes the
primary test against no gate, an exact test, a fixed family of three, a blind headroom rule, an exact power analysis and an outcome
reading that does not oversell a null. Two conditions (C1, C2) must be met before the freeze is declared; the rest before the first GPU
stage or the M4 analysis. The signature covers the design and the preregistration text. It does **not** say the method works or that the
paper will be good: the package itself, plus the dry-run disclosure, makes a positive primary result unlikely (N3).

**My updated probability (judgement, not measured) of a defensible submission by Fri 30 / Sat 31 Oct: about 0.20** (v1 review: about 0.15). "Defensible" =
a manuscript whose every number comes from a `runs/` directory, honestly worded, that Shlok could submit; a positive claim for GATE
about 0.05 to 0.08 of that. The gain over v1 is that blockers B1 and B2 are now design-resolved; B3 (GPU) is untouched and dominates.
Rough decomposition (judgement): the GPU stays stable through M0 to M4 about 0.45; a complete manuscript from valid data in the
remaining time about 0.5 to 0.55 given that.

## 1. My v1 findings

| v1 finding | Status | Evidence |
|---|---|---|
| **B1** primary contrast vs random gate | **Resolved** | Card section 3 / SAP 2.1-2.4: primary is GATE-M vs no gate, exact McNemar, Holm over a fixed m = 3, rejection counts only with b > c; random, geometry-matched and changed-code gates are controls (section 6). Code: `analysis_m4.primary`, audit criterion 1 "supported" (recomputed against scipy). |
| **B2** ceiling / theory coverage / hard negatives / power / data-dependent family | **Partly** | Resolved: endpoint moved to the image direction (probe-1 b_full 0.843, 47 of 300 wrong, spec v2 7.2); Prop. 4 covers it; family fixed at m = 3 with p = 1 for corruptions without an operating point; exact power (N* = 43; SAP 4.2); headroom rule blind to the method (no GATE flag computed, script asserts it). **Not resolved**: headroom under *corruption* is unknown until M3; the SAP's own scenario map shows power 0.19 to 0.59 at n = 300 (Holm) unless the gate removes about 80 to 90 percent of the corruption noise (SAP 4.5); hard negatives are exploratory, on a selected subset (yield 74 and 76 percent, 'person' items skipped), runner not built (card section 13). |
| **B3** crash undiagnosed, workload new | **Open** | Diagnosis: cause is a hypothesis (about 50 percent driver fault on idle-to-boost ramps; AC flap in crash 1 only). HOLD.txt still present. The card calls it a hypothesis and stages M0 accordingly (good), but nothing is demonstrated. Throttle and nvidia-smi-NA abort rules are operator-enforced; directly launched `run_gate_m*` bypasses `gpu_guard` (card 11b). |
| M1 Prop. 1 / data-dependent gate / untested coherence | Resolved in design | Prop. 1' (spec v2 5.1) names the four conditions and says in advance that masking helps least for JPEG/noise; Alg. 12 coherence test pending (M5). |
| M2 Prop. 4 errors | Resolved in design | Spec v2 5.3 now has the inclusion-variance term and general mu_c; plug-in check with a pre-stated refutation. I checked the stated variance formulas; they match the model they state. |
| M3 detection theory, falsifier, patch labelled realistic, selection data | Resolved in design; **empirically adverse** | Prop. 2 scoped to context-independent corruptions (5.2); patch/swap are sanity; statistic fixed a priori (no tuning fold); falsifier = beat the best cheap rival with sign oracle (S-D, K2). The 21-item dry run: plain-B AUROC 0.543 (JPEG) and 0.515 (noise) against sign-flipped pixel variance 0.756 and 0.774 (exploratory, no q). |
| M4 circular labels / missing baselines | Resolved in design | Texture, neighbour distance, rarity, s3, plain-B top-k, TbV-style, pixel-denoise defence arm. See N6 on the denoiser setting. |
| M5 geometry / "oracle" | Resolved | Geometry-matched gate (3 seeds, seed 1 confirmatory), changed-code gate renamed. |
| M6 guarantee wording / ties / Mondrian | Resolved in design; code present | Mandatory wording, jitter at calibration and test, pooled only; Z_cal rule K4 implemented (commit e03d76a3 per card). |
| M7 Information Fusion fit | **Open** | The framing (sensor FDI, distributed vs centralised fusion) is a paragraph, not a result. See N5. |
| M8 narrow delta / strawman / prior art | Partly | Claim reworded to the re-audit's surviving sentence; Trust but Verify, Gomes et al., CO2Jump, Token-Critic added; re-audit verdict "incremental, 0.50". Citation status: card cites commit f0d7ed1f ("49 entries verified"); I did not re-check it, and the earlier citation check (57b2a099) said FAIL. |
| M9 single model | Accepted limitation | Scope in title and abstract; E7 COULD. A reviewer will still ask. |
| M10 LDA fusion | Partly | Demoted to secondary, same-negative-type fitting, Stouffer first. But see N5: in MUST it is never tested. |
| M11 tests that cannot catch real failures | Partly | Alg. 12 and L10 planned; no result exists. |
| m1, m2 | Resolved | Folds exclude all 494 probe ids (audit recomputed 900 distinct ids, zero overlap); probe-1 null masks caption and image (`run_probe1.py` line 55). |
| m6 contamination | Open | Stated unknown (U8). |
| m3, m4, m5, m7, m8 | Accepted or mitigated | As in spec v2 section 1. |

## 2. New problems in v2, the SAP and the card

### N1. The card is not pinned to the code it will run (MAJOR; condition C1)
Card v2 freezes code at `2ab42a6e` and its own pre-launch check is `git diff --quiet 2ab42a6e HEAD -- exp_p2 tools tests runs/P2-GATE-FOLDS`.
At HEAD `cd861649` that exits 1 (checked): five later commits changed 23 files (+682, -74), including the R3 routing and outcome
reading (`a1ac5f01`), the real-tokenizer exclusion (`f16dda8c`), C1 and the chance bar (`e6e1c902`) and the TbV score (`8f897235`). The card still lists
D14, D15 and D16 as open. SAP, folds and spec pins do match. The gate-auditor's re-audit after F1-F6 is still not on disk (card D9), and the
code it audited was before ~700 changed lines. Signing a card that describes code other than the code that will run is not a preregistration.
Resolved if: card v3 pins the final SHA, logs each post-pin commit with the amendment-rule conditions (test-pinned, SHA, no outcome path
touched), the pre-launch check exits 0, and the gate-auditor's re-audit covers those commits.

### N2. Rule R3 changes what "positive" means, and the code words it as verification (MAJOR; condition C2)
- SAP 4.6: R3 triggers when D* < 18 (an oracle gate flips fewer than 18 of 100 headroom verdicts). The primary becomes a Wilcoxon on the paired
  change of d = mean/sd of the per-token evidence over R. That is an evidence-strength ratio, not a verification outcome.
- `outcome_reading` (commit a1ac5f01) prints "GATE-M improved image-direction verification over no gate on ..." for a positive result under every rule. Under R3 nothing about
  verification accuracy was tested, and R3 exists precisely because accuracy has too few possible flips to test. This is the same overclaim the SAP forbids elsewhere ("never worded as...").
- d rises when tokens with extreme per-token evidence are removed, whatever their reason. The geometry-matched and scattered random gates keep the moments of d roughly unchanged
  by construction, so they do not separate "detects corruption" from "trims heavy tails". The only controls that could (plain-B top-k, s3 top-k) are Tier 3, no p-value. S-M is an
  accuracy McNemar and, under R3, has by the same logic too few discordant items to say anything.
- "Negative" is unavailable under R3, so the outcome space is positive or inconclusive only.
Resolved if: the R3 positive sentence says "increased the evidence ratio d" and nothing about verification, S-M under R3 is stated as uninformative in advance, and the
variance-trimming explanation is listed as a competing explanation with plain-B top-k reported next to the P result.

### N3. The primary family is where the card's own theory predicts no benefit, and the dry run points the same way (MAJOR; accepted with disclosure, condition C3)
- Spec v2 5.1 (Prop. 1') predicts masking helps most for patch/swap and "least, possibly not at all, for JPEG and noise". Family P is JPEG, noise, splice; patch/swap are sanity and outside P (card 3).
  The corruptions where the method is expected to work therefore cannot confirm the claim; the ones that can confirm it are those the theory disfavours.
- Dry run (n = 21, exploratory, q not computed; card 7): plain-B AUROC against changed-code labels 0.543 (JPEG) and 0.515 (noise); sign-flipped pixel variance 0.756 and 0.774.
  If the sign-flipped result holds, changed codes sit mostly in flat regions. Flat-region codes plausibly carry little caption evidence, so the headroom drop (T1) can be small
  and the changed-code gate (T2) may recover little even though "corruption" is real. That is a competing explanation for an empty family (K1) or a null P, not a gate failure,
  and the package has no arm that separates the two. (Inference.)
- The spec's own confidence that GATE-M beats no gate is 0.35 (spec yaml). My judgement, given the dry run, is lower. This is not a defect of the preregistration (it is built to
  report a null); it is a defect of the project's expectation. Condition C3 asks that this be stated now, with the fallback decided now.

### N4. Power and the n-rule make a conclusive result unlikely unless corruption is severe (MAJOR; informational)
SAP 4.5: at n = 300, Holm first step, power is 0.19 to 0.36 if the gate removes 50 percent of the corruption noise (rows tau 0.2 / f 0.5, 0.3 / f 0.7), 0.82 only at f = 0.9; R1 needs D* >= 29 of
100 headroom items to flip under a perfect gate while the clean error is 16 percent (47 of 300 wrong). The rule makes R2 (500 items) or R3 the plausible branches, each with
a cost (+0.8 to 1 GPU-h, estimate; or the N2 problem). The card's reachability note says a "negative" label needs realised discordance below about 25 percent. Net: the most probable labelled
outcome (judgement) is inconclusive. That is honest, but a submission whose headline result is "inconclusive on one model" is thin.

### N5. The MUST tier contains no fusion result; the Information Fusion fit rests on a paragraph (MAJOR; condition C4)
Card section 13: caption corruption (S1), hard negatives (S3, runner not built) and the re-infill arm (S2) are outside the frozen tier. Tier 3 says two-way fusion is analysed only if the best single direction is below
0.95 on clean test items; on the primary (deranged) negatives the text direction was 0.990 in probe 1, so the card's own rule will report fusion as untestable. Hard negatives, which would open headroom, are
a selected subset (skips 'person' items, ambiguous nouns, unannotated nouns; yield 74 and 76 percent) with a reviewer-agent audit that is not automated (D12). So every sentence in the paper about "fusion" is framing
(sensor FDI, distributed vs centralised fuser) rather than a measured result. M7 stays open, and arguably is now more exposed: the primary experiment is a naive-Bayes sum of per-token log-ratios with
tokens dropped, i.e. the re-masking (marginalisation) mechanism the title leans on is not exercised at all by the primary endpoint (dropping terms from a sum from a caption-only pass; no network re-masking).
Resolved if: fusion, marginalisation and re-infill are absent from title, abstract and highlights unless an addendum adds S3 (or S2) before the first item, or the paper says explicitly that they were not tested.

### N6. The pixel-domain denoise arm is fixed at library defaults without a check that it denoises (MAJOR/MINOR; condition C5)
Spec v2 4.3: OpenCV `fastNlMeansDenoisingColored` "with library defaults" for all corruptions, "fixed now". The documented default filter strength, as I recall it, is small (h = 3; to be verified against the installed OpenCV 4.13.0), while
Gaussian noise sigma 0.10 on [0, 1] is about 25 grey levels and JPEG q10 gives block artefacts. A defence set up so that it barely acts is the same strawman charge I made against the "DD-style" baseline in v1 (M8b), now on the other side of
the comparison (S-DN would favour GATE-M). Resolved if: before M4, on CPU and without any GATE flag, the denoised copies are shown to change the changed-code fraction (or the clean-vs-corrupted evidence gap) at both corruptions; or S-DN is worded only as
"against a default-strength denoiser".

### N7. C1 anchors on a selected number and cannot see most defects (MINOR)
C1 compares the clean none-arm accuracy with probe 1's 0.843 (Wilson 0.798 to 0.880). That 0.843 is the best of several exploratory variants chosen after seeing probe-1 results (b 0.783, b_k2 0.827, b_full 0.843; probe report), so some regression is expected; the new negatives are
"restricted deranged" (images sharing no annotated category), which SAP A2.3 says are "if anything easier" (asserted, not measured); a value above 0.88 is explicitly not alarming. The trigger (non-overlap, about 2.7 SE) detects gross defects (sign, layout, indexing) only. Not
a flaw as a labelled descriptive check; it is a flaw if anyone later reads a pass as validation (the card forbids that wording). Also note look (i) (after M2, before M3/M4) can halt the schedule through an audit and amended rerun on a two-day clock.

### N8. The sign oracle and K2 (accepted)
The sign-oracle rival is generous to the rival and biases q minus rival downward; the paper must say so beside the result (card 8). Because of the dry run, K2 (q not better than the best cheap rival on both JPEG and noise) is the more likely outcome (judgement). The pre-stated consequences (no claim that q
detects better than cheap methods; the gate-based test still runs and is worded "a gate built on q helps") are adequate. Reporting detail: the rival's win is described as a label-circularity concern, not as evidence about texture (card 8); I would not add more.

### N9. Hard-negative and negative construction (MINOR; informational)
Primary negatives are one fixed deranged caption per item, restricted to images sharing no annotated category (folds.json; audit: negatives inside their block, no self or identical-caption negatives). Restriction likely raises clean accuracy relative to probe 1's unrestricted derangement
(inference), shrinking headroom; C1's wording already allows it. Hard negatives (Alg. 11: noun replacement within a supercategory, never valid by construction) are exploratory and a selected subset. Because they are not in MUST, B2's "hard negatives may be true" is resolved by construction but
not exercised.

### N10. Deadline realism with the GPU on hold (MAJOR; condition C6)
- Time: the repository clock (commits 02:42 to 02:52 IST; `date` 02:59 IST) puts "now" in the early hours of Wed 28 Oct; Fri is 30 Oct, Sat 31 Oct. HOLD.txt is present (checked). D1 to D12 are all Shlok's decisions (release, memory cap 0.75 vs 0.60, guard thresholds, 75 vs 80 C, seed check, unattended runs, hard-negative audit time, optional driver steps). The crash protocol assumes Shlok present and AC verified; no unattended runs.
- Work remaining on one GPU, in order: M0 stages 0-3, M1 (probe-2 items 21 to 199, the existing code path that crashed twice), M2 (calibration, 300 items; C1 look i), M3 (headroom, 100 items), then the n-rule, then M4 (300 or 500 items, plus denoise and geometry arms), M5. Spec 11.1 estimates 2.6 GPU-h of item time (estimate, not measured), 3.9 with contingency, plus about 0.8 to 1 if R2; wall time is about double at duty 0.5 (spec 13). Model reloads and chunk restarts are extra.
- Branches: a crash at M0 stage 2 is declared environmental (no GPU until driver and power are fixed, Shlok's call); any M0 abort sends the project to the CPU-only note, which is not an Information Fusion research article (card 11b, spec 11.4). One crash after M2 costs an amended run, and the SAP forbids analysis of M4 data before the planned fold completes.
- The package also needs, after the data: calibrated analysis scripts, figures, a manuscript at an Information Fusion length with at most 50 references, a bibliography check and the generative-AI declaration. The spec's own plan freezes results Fri 30 Oct 12:00; I see no slack in it.
- My estimate (judgement): meaningful chance (about half) the GPU path fails or is delayed enough that the research article is not feasible by Sat 31 Oct, in which case the honest output is the CPU note or a later deadline (card D5 already says so). Decide the fallback now, not Thursday noon.

## 3. Conditions for the signature

Before the freeze is declared (the signature does not bind until these are met):
- **C1.** Card v3 pins the final code SHA; each post-pin commit logged with the amendment rule's conditions; the pre-launch check exits 0; the gate-auditor's re-audit of those commits is on disk (N1).
- **C2.** R3 wording and S-M-under-R3 as in N2, in code and card, before any M4 outcome exists (the code sentence is a test-pinned change; it touches no number).

Before the first GPU stage / the first analysis:
- **C3.** The card states, before M0, the expected status of H-G given Prop. 1' and the dry run, and Shlok's decision D5 (fallback and deadline if the GPU stays on hold, or if K1/K2/K3 occur) is recorded (N3, N10).
- **C4.** Title, abstract and highlights make no claim about fusion, marginalisation versus imputation, or caption corruption unless an addendum adds those runs before the first item (N5).
- **C5.** Denoise-arm strength check on CPU, or the weaker wording (N6).
- **C6.** M0 run exactly as the diagnosis' staged plan, Shlok present, AC and Id-105 checks, D2/D3 values logged as a change-log row before M0; no hand launch that bypasses `gpu_guard` (N10; card 11b).

## 4. What would make me withdraw the signature
- Any change to the score, K, alpha, folds, rungs or arms after the first M2 outcome that is not a new card version.
- Any analysis of M4 data before the planned fold is complete (SAP 8.2), or a headroom decision that reads a GATE flag.
- A card sentence that attributes a P result to detection without S-M, or any "validation" wording for C1.

## 5. Residual risks the signature does not cover
Single 1.4B model with no stated licence (M9); contamination of COCO val2017 (U8); the IF scope question (M7), which only an editor can settle; the incremental novelty verdict (re-audit 0.50); the citation status.


---

# Red-team signature on A2 (SAP "Addendum A2 (2026-10-28, debate decisions, before outcomes)", sections AD.0 to AD.15)

Date: 2026-10-28, after commit 3f998076 (10:06 IST), while M1 (probe-2 items 26 to 199) is running. No GPU. I opened nothing under `runs/P2-PROBE-02/`. I did open
`runs/P2-GATE-CPU/m1_fallback/analysis.json` (21 dry-run items only; the AD.10 figures for patch and swap match it: plain-B 0.967 and 0.962), `exp_p2/run_probe2.py` and `exp_p2/gate/config.py` (constants only),
the git history of `exp_p2/gate/corruptions.py`, and SAP sections 5, 8.1, 8.2, A1.2, A2.5. Not read: the gate code that implements AD.2 to AD.8 (it does not exist yet: `analysis/paper2/gate/` holds only `a2_power.py`),
UniDisc App. G.1, the FOIL-COCO release, the Omni-Diffusion code.

## Verdict: SIGN WITH CONDITIONS (confidence 0.6 that this is the right call)

I sign that P is untouched (AD.1), that A2 is pre-outcome as far as the file shows, and that the secondary families are fenced from P by separate alpha and by the order of analysis (AD.12).
I do **not** sign the sentences and clauses listed under Blockers; they are struck from the signature. No finding is `fatal`. The signature binds only when the conditions are recorded as dated rows
in the amendment log and the gate-auditor has checked the code (AD "Binding condition"). Nothing here says any family will give a result; most are underpowered by the addendum's own figures (S2 power 0.30 at the middle
assumption; B and R reach 0.8 only for net gains of 0.07 to 0.11).

## Blockers (to be met before the first M4 item unless a family is named; all major)

**B-1. Rescue by sentence.** AD.1 says PS, S2, B, R "never rescue P", but three permitted sentences together do exactly that when P is null.
(a) AD.4 bars "the gate works where detection is easy" only when PS is not met, so it is **available whenever PS is met**. PS is met when random-code replacement is detected and helps. The dry run (AUROC 0.96 to 0.97 on items 0 to 20, seen) makes that the expected outcome, and the phrase defines "easy" by the property tested. It is circular.
(b) AD.3 lets a P null be called "predicted by the independent-token model" if the committed s_c is "-", **without requiring o_c = "-"**, and with no test that separates a predicted null from a low-power null (a "-" prediction can only be refuted by a significant "+" at n = 300, power 0.19 to 0.59 under the SAP's own scenario map).
(c) AD.2 allows "the estimated detection part was V (CI)".
With S2-patch they give a P-null paper a narrative (works where easy, null predicted, shortfall is detection, repair beats random) built from secondary items. Signature condition: sentence (a) and the wording rule (b) are **not signed**; a P null is reported as "P not rejected; inconclusive at this n" with no causal clause drawn from PS, E-pred or E-dec in abstract, highlights or conclusion.

**B-2. E-pred is not what the decision promised (falsifiable, out of sample).**
- *Foregone cells.* PS1 and PS2 will almost surely have s_c = "+" and o_c = "+" (patch and swap are detected at 0.96 and the gate removes random codes). They are 2 of the 5 cells that make a formal test possible. The one-sided binomial with H0 = 0.5 is then false for those cells; the real information is in the three P cells, where K = 3 gives p >= 0.125 even at 3 of 3. AD.3's reachability argument treats cells as exchangeable coin flips.
- *Cells where the theory predicts nothing.* If q is near chance on JPEG and noise, beta_obs is close to alpha_obs and the Prop. 4 sign is the sign of sampling noise in 100-item plug-in estimates; o_c = sign(b - c) at b near c is also noise. Agreement there is a coin for any model, true or false. The test can fail to confirm the model but cannot fail the model.
- *Observed sign is not an effect.* o_c is taken whatever the p-value, so a non-significant cell counts as an observation. Prop. 4 predicts the sign of an evidence-SNR change; o_c is the sign of an accuracy count difference.
- *R3 undefined.* Under rule R3 the primary is d with a Wilcoxon test (AD.4 says so), yet o_c and "positive control met" are defined by b > c_cnt on Y. Which observed sign applies under R3 is not stated.
- *Trivial rival.* "Always +" is reported descriptively but the test is not against it.
Signature condition: E-pred is signed **only as descriptive** (A of K_eval, Clopper-Pearson, rival rules beside it); the binomial p is not signed as evidence about Prop. 4; the observed sign under R3 is fixed before M4; no sentence says Prop. 4 "predicted", "explains" or "is supported".

**B-3. The E-pred fit chunk is a look at GATE before M4.** AD.3 computes GATE flags on the 100 headroom items between `family.json` and M4. That is the first view of the method's behaviour (alpha_obs, beta_obs, hence whether detection works on JPEG and noise). SAP 5 forbids flags there only while operating points are chosen; A2 does not state that no later decision may depend on the chunk's output (n-rule, ordering, cuts, S2 cell, B/R go decisions, wording).
Signature condition: (i) `epred_fit`, the sign function of spec 5.3 and its self-test are committed and gate-auditor-checked **before** the chunk runs and not edited after; (ii) `epred_frozen.json` is committed **before the first M4 item** ("preferably" in AD.3 is not signed; the analysis-script rule does not stop a reader of `items.jsonl`); (iii) a dated row states that no decision depends on the chunk's flags.

**B-4. S2 comparator and claim.** (a) The decision asked for "the UniDisc G.1 recipe at an equal gate size". AD.5's I-G1 is the statistician's reading of spec v2 11.2, never checked against App. G.1 (E1, AD.5 says so). A homemade random-set comparator carrying the name of a published recipe is a strawman risk. Signature condition: until G.1 has been read in full (E2) and the code audited against it, the arm is called "random-set re-infill" and "G.1" is not used.
(b) The confirmatory contrast answers only "is the flagged set better placed than a random set of equal size". Any detector with AUROC above 0.5 passes it for patch, and I-GATE can be **worse** than no repair and still reject. AD.5 says so in its lists; I hold it to that: no sentence in title, abstract or highlights says re-infill or re-masking "improves" verification, and I-GATE versus NONE (descriptive) sits beside every S2 result.
(c) S2 covers patch and splice only; JPEG and noise, where the dry run was unfavourable, are excluded. AD.10 does not record that this choice was made after the dry run (B-6). If P3 has no operating point S2 reduces to S2-patch, which AD.5 itself calls a positive control; the "must" experiment then has no realistic cell and does not answer the rejection reason I gave in R1.
(d) The kept draw is the best of 4 by the image's own likelihood, so figures show best-of-4 samples. Signature condition: captions say "best of 4 draws by own likelihood, caption masked; not typical samples". "Token recovery rate" is a restoration measure while the figures may not claim restoration; it is worded as a token-level descriptive. The harm-case panels (first 4 with Y(I-GATE)=0 and Y(NONE)=1) are signed; they select on outcome in the safe direction.

**B-5. Omni family R: gatekeeping on P is sound; its own checks are not.** P-gating means R cannot rescue P (signed). But GO rule (b) is a run-card self-certification of the adapter (mask round trip, one-position logit shift, audio stub): the proposer validates the proposer. R also inherits P's selection (corruptions chosen because P rejected on these 300 items) and then tests on the first n_R of the **same** items, so item difficulty is shared and "replication" overstates independence. There is no headroom check and no positive control for Omni, so a non-rejection cannot be told from a broken 4-bit pipeline.
Signature condition: the gate-auditor, not the run card's author, signs the three adapter checks before any Omni item enters R; wording adds "same test images, not independent items; 4-bit quantisation confounds a likelihood-based detector"; if P+ is empty R is not run (signed).

**B-6. Disclosure AD.10 is accurate on what it lists and incomplete.** Signed with these additions as binding substance:
(i) S2 is restricted to patch and splice and JPEG/noise are excluded, decided after the dry run;
(ii) the patch and swap constants (patch 8, swap fraction 0.15 in `run_probe2.py` and `config.SWAP_FRAC`) were fixed at commit c8d8e923 (01:07 IST), before the dry run (analysis.json 01:45), and M4 reads the same swap constant; state this only after the auditor confirms the M4 patch size equals the probe-2 one (M4 derives it from the grid: `max(2, round(sqrt(L_I)) // 4)`, which I did not evaluate);
(iii) the 21 dry-run items (0 to 20) lie inside the M1 pool on which the A2.5 chance bar is computed, so for patch and swap that "pre-registered pass/fail" is not fully blind;
(iv) the post-dry-run additions came partly from Shlok's instruction (decision file, about 09:45); who decided what is recorded;
(v) the last sentence ("items 26 onward ... had not informed any decision") is an assertion about other people's behaviour that the author says he cannot verify (AD.0). It must be conditional on a written attestation by the lead (and by Shlok if he looked) that nothing beyond item and health counts from M1 was seen before this signature. I cannot verify it and did not open the items.
Also: the placeholders for the addendum commit SHA and the post-addendum file hash must be filled. The pin "b4e0bf57..." is the hash of the **CRLF working-tree** file; the git blob (LF) hash of the same text is `21a7fdf7...` (checked with `git show 2ab42a6e:... | sha256sum`; both 882 lines). The card must say which convention it uses or a checker will report a mismatch.

**B-7. Cut decisions after P is visible.** AD.12 puts the analysis of P (step 3) right after M4 while S2, FOIL and Omni are still queued. AD.8's cut order is fixed, but the lead decides when each is "ready". Signature condition: a dated row states that cut and go decisions for S2, B, suite and R use time left and the fixed order, not the P or PS outcome; a cut family is "not run", never replaced.

## Checks on the specific points of the brief

**Forking paths, patch/swap family.** Not forking inside P: P is unchanged; PS is outside it, m fixed at 2, endpoint, test and Holm fixed, always tested, no headroom exclusion; disclosed as post-dry-run. That is the least bad treatment. Parameters pre-date the dry run (git evidence above). Residual: the family was chosen where the answer was seen to be easy, so its rejection says nothing about the method (the addendum says so). Remaining paths are B-1 (what PS may be used for) and B-6 (disclosure). Major until those are met, then minor.

**E-dec.** Falsifiable? No hypothesis, no test; signed as descriptive. Fitted and tested on disjoint folds: nothing is fitted; it uses the M4 test fold only. The identity correction (three parts) is correct algebra (T = U + R + V). Problems: (i) U = d_clean - d_chg is called "treatment part" but the chg arm removes the changed positions, so U also contains a **composition effect** (the removed tokens, e.g. flat regions per the dry-run pixel-variance result, carry different evidence from the rest); no arm removes the same positions from the clean image; (ii) V = d_chg - d_GM mixes detection with variance trimming and gate shape, as AD.2 admits, yet the allowed wording says "detection part"; (iii) the labels are encoder-instability labels. Signed only with U named "residual loss under the oracle gate", V named "gap to the oracle gate", and no "detection" or "treatment" in the abstract.

**E-pred.** See B-2 and B-3. Fit on the 100 headroom items, scored on the test fold; disjointness is asserted by a script that does not yet exist. The fit set is also the set on which the operating points were selected (rungs chosen for a large drop), so the fitted rates describe a corruption level chosen for large effects; harmless for the sign, noted. Falsifiable only at K_eval = 5, and then against the wrong null.

**S2 comparator and repaired-image figures.** B-4. Equal gate size item by item is the fair part (signed). Not equal: scattered random positions and clustered flagged positions give the sampler different context, which helps the comparator at the infill step and helps the flagged set at hitting the corruption; the claim is correctly limited to location. Power 0.30 at (0.10, 0.75), n = 150, so S2-splice most likely ends inconclusive; an inconclusive S2 may not be described as supportive.

**FOIL leakage and fit (family B).** The design is sensible (fit ids in "cal", test ids disjoint from "cal", "head" and probe ids, one pair per image, LDA weights frozen, ceiling rule, best direction chosen on fit pairs). Gaps: (i) L2 to L4 are disjointness assertions and **pass vacuously** if FOIL image ids and folds.json ids use different formats (zero-padded file names vs integers, 2014 vs 2017 numbering); nothing shows that a known id matches. Signature condition: a positive control on id matching (count of matched ids and a hand-checked named sample) is part of the logged leak check. (ii) All dataset facts (licence, release format, overlap with val2017, record order) are E0; B stays "not run" until the data-steward verifies them; "first record per image in file order" is content-neutral only if the file order is. (iii) Fit pairs are limited to cal ids that are in FOIL and in val2017, so n_fit >= 100 may fail; B is then "not estimable" (acceptable). (iv) The c+ captions are COCO captions, likely in UniDisc's training data (U8); the text direction may be memorised. Major until (i) is met.

**Omni gatekeeping.** B-5. Gating on P is correct and R cannot rescue P. The timing thresholds (T <= 1.5 GPU-h, 2 x T before freeze) are ASSUMED but fixed before any Omni outcome, which is what matters. R is not reached if P+ is empty, the likely case.

**Can any family rescue another?** Formally no: separate alphas, P first and committed. Narratively yes through the sentences in B-1 and through the imagecorruptions suite (AD.9): an E-pred sign agreement over 8 cells with a Clopper-Pearson interval is inference-shaped and offers "the sign prediction held" once the formal K = 5 test is unreachable. Signature condition: suite agreement is never combined with AD.3 and never appears in abstract or highlights; the four types and two severities (chosen "by kind" from a package of fifteen, no rationale recorded) are marked as researcher choice.

## Signed and not signed

Signed: AD.1; AD.2 as a descriptive decomposition with the label limits above; AD.4 as a positive-control family with no claim beyond "pipeline not broken"; AD.5 except the G.1 name; AD.6 and AD.7 with B-5 and the id-match control; AD.8; AD.9 as Tier 3; AD.11; AD.12; AD.13 as a list of functions.
Not signed: the AD.4 sentence "the gate works where detection is easy"; the AD.3 binomial as evidence about Prop. 4 and its wording rule; the name "G.1" for I-G1; the last sentence of AD.10 as unconditional.

## What would make me withdraw this signature

- Any M1 outcome (AUROC, chance bar, q, pixel variance, timing) read by an author or the lead before the conditions are logged and then used in an edit to A2 (AD.0 firewall).
- Any change to a cell set, corruption, endpoint, test or wording in A2 after the first M2 outcome that is not a dated new addendum.
- `epred_frozen.json`, `ps_frozen.json` or `family.json` committed after the first M4 item exists, or any decision citing the E-pred fit chunk's flags.
- A paper sentence that calls a P null "predicted", "explained" or "caused by detection", or that states PS, S2, B, R, E-dec, E-pred or suite results in the abstract without the family label.
- Omni run before the gate-auditor signs its adapter checks; B run before its id-matching positive control.
- Code for AD.2 to AD.8 that the gate-auditor has not matched to the text before the first item of that family.

## Results that would force rejection of a claim made from A2

- PS "not met" (either cell not rejected with b > c) with no defect found by the A2.3 audit: nothing from PS, E-pred or S2-patch may be used.
- S2: I-GATE not better than NONE descriptively and S2-splice not rejected: no claim that repair helps; I-GATE worse than I-G1: the location claim is refuted.
- E-pred: agreement on the three P cells no better than "always +"; a P cell with a significant result opposite to s_c.
- E-dec: V negative with a CI excluding 0 (GATE-M beats the oracle): the "detection" reading is void and variance trimming is the live explanation.
- B: rejection with b < c, n_fit < 100, or ceiling >= 0.95: no fusion claim.
- R: no rejection means "not replicated, inconclusive"; a rejection with b < c refutes direction.

## Residual risks the signature does not cover

Twelve test families with no cross-family control (AD.11: 0.46 chance of at least one rejection if all were null); single UniDisc model; contamination (U8); mask-seed and corruption-seed variance outside every interval; the gate-auditor check of AD.2 to AD.8 code is still to come; I did not read the code, G.1, FOIL or Omni. Judgement, not measured: the A2 families add little to the chance of a defensible positive claim (about 0.05 to 0.08, unchanged); they raise the chance of a reportable, honestly worded measurement paper if M4 runs.
