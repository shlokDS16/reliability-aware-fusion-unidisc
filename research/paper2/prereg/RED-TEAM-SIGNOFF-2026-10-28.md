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


---

# Red-team signature on A3 (SAP "Addendum A3 (2026-10-28, decisions and implementation readings made today, before outcomes)", sections A3.1 to A3.11)

Date: 2026-10-28, about 14:40 IST, on HEAD 017bffc0 (the commit that carries A3). CPU only. I opened nothing under `runs/P2-PROBE-02/` (I saw file names in `git status`, nothing else).
Read: `A3-REDTEAM-REQUEST`; SAP AD.0 to AD.15, AB.1 to AB.10, A3.1 to A3.11 and 8.1/8.2; `IMPL-A` (full), `IMPL-B` (sections 1 to 6), `IMPL-C` (sections 1 to 9), the head and sections 3 to 4 of the FOIL-L7 sign-off, `OMNI-ADAPTER-CHECKS`, `STATUS-1100`, `CONFIRM-EVENING`, `LEAD-ATTESTATION-A2`, `runs/P2-GATE-A3/a3_power_output.txt`, `runs/P2-GATE-FOIL-L7/l7_out.json` and `pool.json`, the code of `exp_p2/gate/reinfill.py`, `exp_p2/run_gate_s2.py` (lines 120 to 175 and the arm definitions), and the `git diff` of the uncommitted files `epred.py`, `edec.py`, `seeds.py`, `analysis_omni.py`, `run_gate_m2.py`. Not read: UniDisc App. G.1 (no copy), the Omni code, the FOIL file itself, `IMPL-D` beyond the A3.6 claims (I read the diff of `epred.py` instead), any gate-auditor audit (none exists for this code), any M1 output.

## Verdict: SIGN WITH CONDITIONS (confidence 0.6 that this is the right call)

I sign A3.1 (n = 300 primary, n = 150 nested sensitivity) as pre-outcome and not a forking path, A3.3, A3.7 and A3.8 (with the corrections below), and the statistical content of A3.6. I sign A3.2, A3.4 and A3.5 **only with the conditions below**; the sentences listed under "Not signed" are struck. No finding is `fatal`. Nothing here says S2, B or R will give a result; at n = 300 the SAP's own table gives S2 power 0.658 and B power 0.744 only at (pi_d 0.10, theta 0.75), and S2's effective pi_d is lower because items with g_i = 0 are concordant (`a3_power_output.txt`, section F).

The signature binds when the conditions are recorded as dated rows in the amendment log and the gate-auditor has matched the code to the text. **My signature is conditional on Shlok in two respects** (C3-7 and C3-6): his explicit confirmation of n = 300 (before the first S2 or B item), and his M1 co-attestation or a stated absence (before any M1 outcome is analysed or any sentence calls the chance bar blind).

## Numbers traced (every number in A3)

- Power tables in A3.1: all entries match `a3_power_output.txt` lines 5 to 33 (S2 and B at n = 300 and 150; powers 0.658/0.302 and 0.744/0.405; ratios 1.35 to 1.42; n = 240 gives 0.064 and n = 120 gives 0.087 at pi_d 0.10; 0.055 in the g_i = 0 illustration). The AD.4 reproduction (section E) matches. Hashes recomputed here equal the request: SAP CRLF `7e1a2418...`, LF blob of HEAD `f26b8fa5...`, script `85f394ff...`, `a2_power.py` `78fc0fb8...`, output `760fe033...`.
- 1.30 to 1.95 GPU-h at n = 150, 2.6 and 3.9 at n = 300, 0.121 s per row, 298 completed test pairs, the pool hash string and `n_sap_text = 150` match IMPL-A section 5 and IMPL-B section 2 (the pool hash is quoted from IMPL-B; I did not recompute it either).
- A3.4: 26 of 300 (8.7 percent), 5 plausibly true plus 7 ambiguous (12, 4.0 percent), 14 wrong by role, 1 of 29 hand-viewed, a/an 15 of 300 and 7 of 240 match the L7 sign-off (lines 140 to 160) and `l7_out.json`. Ball to racket 11 of 300 against 1 of 240: recomputed from `pool.json` (test 11, fit 1).
- A3.7: 25 names plus 3 equals 28; the working tree already appends `edec` (28), `omni_gate` (29), `omni_r` (30), `suite` (31), an append-only extension.
- A3.5: about 40 percent of codes differ between the two preprocessing paths: IMPL-C A8 ("about 60 percent agree", 8 images, explore script, no run id; A3 says so).
- The 10:30 approval: `STATUS-1100` was committed at 10:57 (f6e0b9f8), the FOIL pool at 13:54, the S2 runner at 14:01. The order "decision before any S2 or B artefact" is supported by git. What is not supported is the content of the decision (C3-7).

## Findings

### C3-1. The kept-draw statistic is not symmetric between the two S2 arms (MAJOR)
A3.2 item 1 says the chain log-likelihood is "the same statistic in I-GATE and I-RAND4, so the contrast is symmetric". The formula is the same; what it selects over is not. In `run_gate_s2._arm_sets`, I-GATE uses the **same set** G for all four draws (selection is over sampling noise only), while I-RAND4 draws **a new random set per draw** (as AD.5 says). Best-of-4 in I-RAND4 therefore selects among four different position sets by the summed log-probability of the sampled tokens, which favours sets of easily predicted positions (flat, context-determined regions), that is, sets least likely to cover what needs repair. The comparator is handicapped in a way I-GATE is not, and the confirmatory contrast becomes easier to pass than "flagged set versus a random set of equal size". The direction of the net bias is not established (the clustered I-GATE set is also sampled in parallel, k_s tokens per step at temperature 1, which hurts contiguous blocks more than scattered positions); that the selection treats the arms unequally is established by the code. The draw-level and all-four contrasts of AB.4 item 4 are the check, but they are descriptive, and A3 says nothing about what is claimable when they disagree with the kept-draw test.
Signature condition: the symmetry sentence is struck. A dated row, before the first S2 item, says that the draw-level contrast (mean Y over the four draws, paired bootstrap CI) is printed in the same table as every kept-draw test, and that a rejection of the kept-draw contrast whose draw-level CI includes 0 or lies on the other side is worded only "under best-of-4 selection by chain log-likelihood" and carries no location claim.

### C3-2. The S2 sampler and the "G.1-inspired" label (MAJOR)
The implemented sampler (random order, 16 steps, temperature 1, unguided, parallel unmasking of ceil(g/(17-s)) tokens per step, caption masked) shares with UniDisc's `_sample` (MaskGIT order, arccos schedule, Gumbel noise, guidance in the demonstration) only the network. App. G.1 has not been read (E1). The comparator is therefore not G.1, and the label "G.1-inspired" asserts an affinity nobody has checked. What the paper may claim from S2: "with this plain random-order re-infill, repairing the set GATE-M flagged gives higher (or not higher) image-direction verification accuracy than repairing equal-size random sets, best of four by chain log-likelihood, caption masked". It may not claim anything about UniDisc's own re-infill, about re-masking as a mechanism, about the gate's detection (a flagged set that scores better may simply contain fewer clean, evidence-bearing tokens), or that location "does not matter" if S2 is inconclusive. Re-infilling clean positions with caption-masked prior samples destroys real caption evidence, so I-RAND4 may be worse than NONE; the contrast then indexes how many clean tokens each set touches. AB.4 item 2 discloses this in part; it should sit beside the result.
Signature condition: "G.1" does not appear in the title, abstract, highlights, figure titles or the S2 table header; where it appears in the text it is followed by "the sampler differs from UniDisc's in order, schedule and guidance". The sampler specification of A3.2 item 2 is copied into the run card (signed as written). A negative or inconclusive S2 is never read as a statement about location or about the gate. The I-CHG cut is inferentially free for the confirmatory family (checked in code: arm streams are indexed by the fixed `ARM_ID`, not by position in the arm list, so dropping I-CHG changes no other arm's draws); "decided at launch, all items, time only" is adequate under AB.9, with the cut logged with its time.

### C3-3. FOIL: the label-noise bounds, the ceiling rule and the untriggered case (MAJOR)
(a) "About 4 percent (up to 8.7 percent)" is presented as a range. 4.0 percent is one reader's count among the 26 pairs flagged by the COCO-instance rule; 8.7 percent is the flag rate. Neither is an upper bound on the plausibly-true rate: the same rule fails to find the category of the **original, true** noun in 26 of 300 test pairs (`l7_out.json`, test.`target_mapped_but_absent`, 26 entries; 33 of 240 for fit), so an "absent" flag is weak evidence, and 274 test pairs and 222 fit pairs were not viewed. For the 240 fit pairs, on which the ceiling rule and the best direction are decided, no judgement exists beyond the rule's own count (18 flagged). "Up to" is not supported.
(b) Rule (ii) as written (0.95 on the fit pairs) sits near the label-noise cap of an image reader: if 4 to 9 percent of foils are plausibly true, the image direction cannot reliably reach 0.95, so the rule can mainly trigger through the text direction, that is through text-only cues (a/an mismatch: 7 of 240 fit, 15 of 300 test; 14 test pairs are wrong by role with the foil object present, where an image-likelihood score is structurally disadvantaged). The wording for the **triggered** case is adequate ("text-only cues are not excluded as a cause").
(c) For the **untriggered** case A3.4 says only that a fusion result "carries the same caution". That is not a wording rule. A positive B is exactly the case in which a reader takes a gain as evidence that image and text evidence fuse, while the gain can come from the LDA weighting a text-side cue whose mix differs between fit and test (ball to racket 11 of 300 against 1 of 240; AD.6 says LDA is fitted on "the same negative type").
(d) The label-noise cap also bounds the possible net gain of B (at most 1 minus the best single accuracy minus the noise); the A3.1 power table is silent on this.
Signature condition: the noise sentence in the paper states the three numbers with what each is (26 flagged by the rule, 12 judged questionable by one reader, rule miss rate on true nouns 26 of 300) and does not say "up to". B1 with an untriggered ceiling is worded "the combination of the two UniDisc scores beat the better single score on these FOIL pairs; part of the gain may come from text-only cues; no text-only baseline was run". No sentence says FOIL tests fusion of image and text evidence. The no-exclusion rule is signed; the descriptive sensitivity without the 26 flagged pairs is signed as exploratory.

### C3-4. "Run and signed by the gate-auditor" for the Omni adapter (MAJOR)
A3.5 item 4 reads AB.5 item 1 as: the auditor runs the CPU checks and **reviews** `selfcheck.json` produced by the timing stage. The checks that need the real model (A4 GPU variant, A5, A6 GPU variant, A7) are executed by `exp_p2/omni/checks.py`, written by the adapter's author and launched by the lead or the GPU runner. Reviewing the output of the author's code is not "run ... not by the author", and it is the structure B-5 objected to (the proposer validates the proposer). Two further points. The checks file says the auditor may tighten thresholds "before signing", that is after `selfcheck.json` and the A5 numbers exist, while A3.5 item 3 says "before the timing stage". And the timing stage and the signature come after P is known (R runs only if P+ is non-empty), so the discretionary "every A-result inspected" is exercised with knowledge of what a NO-GO would cost.
Signature condition: A3.5 item 4 is **not signed as meeting AB.5 item 1**. It is accepted as a recorded deviation: the gate-auditor reads `checks.py` against the text (A4 is an exact identity against the literal sampler line and can be checked by reading), the deviations box says "adapter checks executed by the implementer's code and reviewed, not executed, by the auditor", and no sentence says "independently verified". The tightening window is **before the timing stage** only; the checks file is corrected by a dated commit; the hash of the checks file at the A3 commit is written into the amendment row (A3 says "as committed at the time of this addendum" without a hash).

### C3-5. Omni family R: structure and wording (MAJOR)
(a) **The n_R = 120 trap.** A3.5 item 2: the GO rule uses the planned n_R, the test status uses the completed n, and completed n < 120 is descriptive. If the size rule selects n_R = 120, a single exclusion by the Omni token rule makes the completed n 119 and R descriptive, so that branch is formal only with zero exclusions. The text calls this "not a shrinking of the protocol"; in effect it is.
(b) **What the positive control covers.** AB.5 item 2 is a code-level patch control (no encode). The corruptions of R are pixel corruptions pushed through a two-stage preprocessing path that changes about 40 percent of the codes relative to Omni's own path (IMPL-C A8; decode PSNR 19 to 22 dB on three images), after JPEG and noise are attenuated by the 512 to 256 downsample, with a 4-bit model and a caption mask that Omni never saw in training. The control passes or fails without touching the path most likely to break R. "A pass proves only non-chance on patch" is correct but must add "at code level, without the encode path".
(c) **GO rule (c) is a guard setting.** AD.7 (c) says peak memory "within the guard cap in force"; A3.8 says guard settings touch no statistical rule. For R they do: a different ceiling or cap changes which timing run is GO. Pre-outcome and harmless if the Omni caps are fixed before the timing stage (A3.5 item 3 says none is raised after an Omni memory reading); then A3.8 (i) must carve out AD.7 (c).
(d) **P+ under R3** is read on a d-based Wilcoxon rejection with the sign of the d difference, while R tests Y by McNemar. Acceptable as a gate (written before any P outcome); the wording "directional replication" is not available under R3, because the endpoints differ.
(e) The implementer-written thresholds (A5 margin 1.0 nat, 7,000 MiB, 9,500/9,000/1,500 MiB, 2,500 MiB before load) are E0 and uncalibrated. "Adopt as committed, never loosen" is adequate against a retuned GO; the cost is a possible permanent NO-GO from a threshold that is too strict, which only removes R.
Signature condition: (a) the n_R = 120 branch is declared "formal only if no pair is excluded", or the floor for R is restated; (b) the control sentence adds "without the encode path"; (c) A3.8 (i) carves out AD.7 (c) and the Omni caps are written into the run card before the timing stage; (d) under R3 the R sentence reads "the evidence-ratio effect found in P was / was not accompanied by an accuracy change on Omni", not "direction replicated"; every R result carries the confound list (4-bit, 40 percent code change, attenuated JPEG and noise, masked caption out of distribution, same test images under R2).

### C3-6. M1 resume, the chance bar on a partial pool, and the firewall (MAJOR)
A3.8 is correct that guard settings are not statistical rules (with the AD.7 (c) carve-out) and that resuming from item 106 on the same list, with the stopped item retried, needs no new addendum (SAP 8.1, AD.8). What A3 does not say: **AB.7 item 3 defines the chance bar on all 200 items and on items 21 to 199, and both lower bounds must exceed 0.5.** If M1 completes fewer than 200 items (a further guard stop "halts it for good" per the status note; 106 of 200 are done), the pools are items 0 to k and 21 to k with k below 199. No rule says what is computed, what the verdict is (the code has an "undecided" state, `combine_chance_bars`), what an undecided bar triggers, or whether M1 is waited for in full. The statistician has not read M1; the first person to see a partial bar will also be the person deciding what to do with it.
Firewall: `LEAD-ATTESTATION-A2` covers 09:56 to the commit of A2 (10:06). The M1 stop at 10:26 was investigated afterwards (`chunks.jsonl` last line; `peak_gb` of items 0 to 25 and the telemetry, per `CONFIRM-EVENING` section 1). A3's statement that nobody read M1 outputs beyond items 0 to 25 is the lead's assertion (HANDOFF 57) and is not covered by a dated attestation after 10:06.
Signature condition: before any M1 outcome is analysed, a dated row fixes (i) the partial-pool rule (the bar is computed on the completed prefix and on the prefix minus items 0 to 20; both lower bounds above 0.5 is a pass; anything else is "failed" or "undecided" and reported so; "undecided" is never read as a pass; with fewer than 100 items in the late pool the bar is "undecided"), and (ii) that the decision to wait for 200 or to proceed uses time only (AB.9). `LEAD-ATTESTATION` is extended, dated, to cover 10:06 to the A3 commit and the 10:26 investigation, listing what was opened. Shlok's co-attestation (requested since A2) is given in his own words, or its absence is stated beside every use of "blind" for the chance bar.

### C3-7. n = 300 and what Shlok approved (MAJOR as to the wording of A3.1; not a forking path)
Not a forking path: the change is made before any S2 or B outcome exists (git: decision on record 10:57, pool 13:54, runner 14:01), n is fixed with no optional stopping, the original n is a nested prefix reported beside the primary, and no test, family, Holm size or alpha changes. The dry run (21 probe-2 items) contains no S2 or FOIL quantity, so it cannot have steered this choice. "Sensitivity can neither reject nor rescue" is enough against a forking-paths reading **as to the family result**; what remains is presentation (a rejected sensitivity next to a non-rejecting primary will be quoted), and A3.1 item 3 already requires both to be shown with "sensitive to n".
What is weaker than A3 states: (i) Shlok's recorded reply (`STATUS-1100`: "Yeah after review will let you to continue then go with your recommended plan") does not mention n; the lead reads it as approval of the plan item "raise S2 and FOIL to n = 300 (about +1 GPU-h, estimate)". (ii) That cost basis is not the current one: IMPL-A puts S2 at 3.9 GPU-h busy and about 8 h wall at n = 300 against 1.95 and about 4 h at n = 150, an increment of about 1.95 GPU-h and 4 h of wall time for S2 alone, roughly double what he was told. (iii) `CONFIRM-EVENING` lists "S2 and FOIL at n = 300" under "Already decided (no answer needed)". The larger cost raises the chance that S2 is cut by the freeze and ends as a partial prefix (120 to 239 completed, a labelled state with printed MDE), so the choice buys less power than the table suggests.
Signature condition: A3.1 is signed **conditional on Shlok's explicit confirmation of n = 300 for S2 and B with the updated cost, recorded as a dated row before the first S2 or B item**. The floor of 120 is signed as written (a formal test at 120 has an MDE of 0.087 to 0.128 at pi_d 0.10 to 0.20 and the exact test keeps its size); the label "partial prefix" and the MDE are mandatory; a prefix-based result is never described as an n = 300 result.

### C3-8. E-pred split, `theory.py` freeze, and unpinned code (MINOR)
The fit/score split does not get round AB.3 item 5: the fit code, its hashes and the seed fingerprint are what B-3 fenced, and `score` refuses on a hash mismatch. Residuals: (i) the observed-sign, agreement and rival definitions live in `epred.py`, which may be edited after M4 data exist as a "bug fix" judged by its author; the pre-fix output is kept, which helps; the auditor, not the author, classifies a post-M4 edit as a bug fix. (ii) `theory.py` is imported by `analysis_m4` (P-side plug-in) and the suite; freezing it forces a choice between fixing a P-side bug and keeping E-pred, and the rule "an edit makes E-pred not run" gives the wrong incentive. Accepted as written, with the P fix taking priority and E-pred then "not run". (iii) The working tree has uncommitted edits to `epred.py` (63 lines), `edec.py`, `seeds.py`, `analysis_omni.py`, `suite.py` (about 100 lines removed: the suite's prototype E-dec and E-pred functions appear to be gone, which A3.6 item 5 anticipates) and `run_gate_m2.py`, so "the code at the commit that carries this addendum" is not the code that will run. Not a statistical defect; it is the N1 problem of the first signature again.
Signature condition: card v4 pins one commit of all of `exp_p2/`, the auditor's audit covers it, and any post-pin edit is logged as in the amendment rule.

### C3-9. Smaller points (MINOR)
- A3.1 item 3: "the sensitivity exists only if the completed n is at least 150" is ambiguous for B (the first 150 positions give about 148 completed after the token rule), and AD.6 says "the first 150 eligible pairs", which after exclusions is not the first 150 positions. "SAP as written" is therefore approximate for B. The B sensitivity is the first 150 pool positions, tested if the overall completed n is at least 120, and labelled as such.
- A3.2 smoke (3 S2 items, Y not read): adequate at three items with a crash fix that leaves sampler parameters alone; the firewall is an honour rule. A script prints only `peak_gb`, `seconds`, `n_rows`; `analysis_s2` is not run on the smoke directory.
- A3.4 item 2 says label noise "plausibly lowers pi_d ... attenuates Delta_B" and, in the same passage, "the sign of any bias on Delta_B is not established". Only the second is supported.
- A3.5 item 6: the `p_cal` fallback of 12 passes is flagged; the working tree now writes `n_rows` in M2 rows, so the fallback is moot only if M2 runs with the modified file. The run card says which was used.

## B-1 holds after A3 (check 5)
No A3 clause lets a secondary family explain or rescue a null P. A3.1 item 5 repeats that no claim becomes available at n = 300 that was not at 150; A3.2 item 3 and C3-2 forbid reading an inconclusive S2 as evidence about the gate; A3.4 gives no B wording that touches P; R is gated on P+ (the R3 definition is written before any P outcome, C3-5 d); A3.6 keeps E-pred without a p-value. The one new route I found is by wording, not by test: the C3-1 situation (a kept-draw rejection of S2-patch or S2-splice read as "the flagged set is better placed") offered to explain a P null. AB.1 item 2 already forbids a causal clause from S2 in title, abstract, highlights and conclusion; I hold A3 to it.

## Answers to the nine check items
1. A3.1: acceptable as written (C3-7); the floor of 120 is sound for validity and weak for inference; the sentence "sensitivity can neither reject nor rescue" is enough.
2. A3.2 item 1: the chain log-likelihood is a faithful reading of "own caption-masked likelihood"; it is not symmetric between the arms (C3-1).
3. A3.2 item 3: the I-CHG cut is inferentially free for the confirmatory family (checked in code); "at launch, all items, time only" is adequate under AB.9.
4. Smoke: adequate at three items with the print-only reading rule (C3-9).
5. A3.4: the no-exclusion rule holds; the label-noise wording does not (C3-3 a); the ceiling wording is incomplete (C3-3 c).
6. A3.5: (i) "same corrupted pixels as P" is a defensible reading of AD.7 and was decided before outcomes, but it is not the P+ corruption parameters at Omni's resolution, and the 40 percent code change is a larger confound than the one disclosed (C3-5 b). (ii) adequate with the carve-outs (C3-4, C3-5 e). (iii) not met as read (C3-4). (iv) acceptable as a gate; wording changes (C3-5 d).
7. A3.6: not a way round AB.3 item 5; bug-fix-only is adequate with auditor classification; the `theory.py` freeze affects P only through the incentive, accepted (C3-8).
8. A3.8: guard settings touch no statistical rule **except AD.7 (c)** (C3-5 c); resuming M1 needs no new addendum (C3-6).
9. The chance bar at fewer than 200 items is undefined (C3-6); also the missing post-10:06 attestation, the unpinned code (C3-8), and the missing hash of the Omni checks file (C3-4).

## Signed and not signed
Signed: A3.1 (conditional on Shlok, C3-7); A3.2 items 2 (sampler specification, with C3-2), 3, 4, 5, 6; A3.3; A3.4 items 1, 4, 5 and the no-exclusion rule of item 2; A3.5 items 1, 2 (with C3-5 a), 3 (with the hash), 6, 7; A3.6 (statistical content); A3.7; A3.8 (with the carve-out); A3.9 (the disclosure list is accurate; add the C3 items).
Not signed: the A3.2 item 1 sentence "so the contrast is symmetric"; "G.1-inspired" outside the text body; the A3.4 item 2 phrase "(up to 8.7 percent)"; the A3.4 item 3 sentence "carries the same caution" as a wording rule; A3.5 item 4 as a reading that meets AB.5 item 1; the A3.8 sentence that guard settings touch no statistical rule, without the AD.7 (c) carve-out; the A3.5 item 2 description of the n_R = 120 branch as "not a shrinking".

## What would make me withdraw this signature
- Any S2, FOIL, Omni, suite or M2 to M5 outcome read by an author or the lead before the corresponding conditions are logged and then used in an edit to A3.
- An S2 table that omits the draw-level contrast beside the kept-draw test, or a sentence that calls the S2 contrast a location effect when the draw-level CI includes 0.
- A change of n, floor, sensitivity definition, kept-draw rule, sampler parameter, arm set (other than the logged I-CHG cut), pairing key, ceiling, exclusion rule or Omni threshold after the first item of that family.
- Omni R run before the auditor's signature and the checks-file hash row; a sentence "independently verified" for the adapter.
- Use of the M1 chance bar as a blind pre-registered pass/fail without the extended attestation and Shlok's co-attestation (or the stated absence).
- A sentence that explains or rescues a null P from S2, B, R, E-dec, E-pred or the suite.

## Results that would force rejection of a claim made from A3
- S2: kept-draw rejection with draw-level CI including 0 or on the other side: no location claim. I-GATE not above NONE descriptively and S2-splice not rejected: no repair claim. I-GATE below I-RAND4 with CI excluding 0: the location claim is refuted. Any S2 result with I-CHG cut: nothing about the sampler or the gate.
- B: rejection with b < c_cnt, n_fit < 100, ceiling >= 0.95, or completed n < 120: no fusion claim. A rejection in the untriggered case without the text-cue sentence: invalid as worded.
- R: no rejection means "not replicated; inconclusive at this n" (and with the n_R = 120 branch, possibly descriptive only); a rejection with b < c_cnt refutes direction; a failed positive control is "pipeline defect: not run".
- Primary at n = 300 and sensitivity at n = 150 on opposite sides of rejection: "sensitive to n", and the primary is the result.

## Residual risks the signature does not cover
Eleven test families with no cross-family control (AB.3); single UniDisc model; contamination of COCO val2017 captions (U8), which applies with more force to FOIL because c+ are COCO captions; mask-seed and corruption-seed variance outside every interval; the 8.2 GB peaks and eight GPU crashes since 10-14 (memory notes), which make partial prefixes the likely state of the last-run families; no gate-auditor audit of the S2, FOIL, Omni, E-dec and E-pred code exists yet; I read none of the Omni code, the FOIL file, or UniDisc App. G.1. Judgement, not measured: A3 adds three secondary families whose most likely labelled outcome is "inconclusive"; the chance of a defensible positive claim stays at about 0.05 to 0.08, and what A3 adds is a better chance of a reportable, honestly worded measurement paper if M4 runs.


---

# A4 signature (SAP "Addendum A4", file `research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md`, commit 40828e96, sections A4.1 to A4.6)

Date: 2026-10-28, after commit 40828e96, M3 running. CPU only. I read no M3 or M4 value and opened nothing under `runs/`; the M1 numbers A4 quotes are checked against REDTEAM-P2-PLAN A11, where I compared them with `runs/P2-GATE-M1/analysis.json` earlier. The only commands run were a character count of the nine highlights and a print of ledger rows D0072 to D0075.
Read: A4 in full; CONTRACT; SAP AD.12, A2.2, section 7, section 9, the K1-K7 table, AB.1 to AB.10; card v4 sections 2, 3, 7, 9; REDTEAM-P2-PLAN sections 0, A1-A11, B, C.1; NOVELTY-CHECK-INFFUS section 4; CONFIRM-EVENING section 7 and "Shlok's answer"; `exp_p2/run_gate_m4.py` lines 100-189, `gate/evidence.py`, `gate/seeds.py`, `gate/calibrate.py`, `gate/fit_threshold.py`, `gate/scores.py` 108-110, `gate/pipeline.py` (gate_scores, image_delta, compact); ledger D0072-D0075. Not read: the paper sources, `run_gate_s2.py`, `run_gate_foil.py` (A4's statement that FOIL draws no random numbers and takes no M2-M4 input is E1 here), the UniDisc code (section B of my plan review is my own earlier reading), `huang2025evidential`, Wilcox and Tukey (E0 in A4, E0 here).

## Verdict: SIGN WITH CONDITIONS (confidence 0.6 that this is the right call)

I sign Part 1 (the Tier-3 comparators) as a specification, Part 3(a) (time-input sentence) as written, and Part 3(b) (FOIL before S2) with C4-10. I sign Part 2 (the outcome book) only in part; the sentences listed under "Not signed" are struck from the signature. No finding is `fatal`. Ten are `major`: each would leave a sentence in a title, abstract or contribution list that the SAP, the card or the data cannot carry. The signature binds when the conditions are recorded as dated rows before `analysis_m4` is first run on M4 data (C4-1 and C4-2 must be met earlier, before `family.json` is committed where they say so). Nothing here says any comparator will tell us anything: Part 1 is close to non-discriminative at n = 300 (F7).

## What I checked and found sound (Part 1 mechanics)

- Every array A4.1.2 names exists as stated: `<cond>_delta` (run_gate_m4.py:144), `_B` and `_D` (154), `_flag{al:g}` (156-157, key "0.05"). Denoised copies store Delta and codes only (145-148, `continue`). Verified by reading.
- The u recomputation is exact: `suspicion_q` casts B and D to float32 before subtracting (scores.py:108-110) and D is stored as float32. A4 correctly does not need the jittered u.
- The consistency gate (A4.1.3) will not stop on rounding: `pipeline.compact` keeps the full-precision floats of `evidence_from_delta` on the same float32 delta that is saved, so the 1e-9 tolerance is met by identity. A stop would indicate a real discrepancy.
- Arithmetic: floor(0.20 x 1024) = 204 per tail leaves 616; 511 per tail leaves the two middle values (the median); floor(g/2) per tail leaves m - g or m - g + 1. `seeds.ANALYSES` has 32 names (suite = 31), so `tier3_fusion` is 32 and `SeedSequence(20261028, spawn_key=(32,))` equals the appended child. For SOFT, tau is a jittered calibration score (calibrate.py:92-95) and the unjittered S_cal at tau is consistent because the jitter is below half the minimum gap.
- No p-value, a fixed contrast list, one shared resample matrix, all cells reported, PS cells in their own table, denoised and text-direction cells excluded: tighter than SAP 7, signed.
- A no-gate (NONE) and a hard-gate (GM) reference are present for every comparator on the accuracy scale. On the d scale NONE and GM are reported, but only TM-G and TM20 are contrasted with GM (not with NONE). Answer to check (2): neither the 20 percent trim nor the g/2 rule reads as tuned; both are fixed before data. The 20 percent default is E0 but not outcome-driven.

## Findings

### F1 (major). The binding clause is circular and the commit order is not tied to `family.json`
A4 "binds when (i) committed before `analysis_m4`, (ii) the red team has read it, (iii) the gate-auditor has matched the Tier-3 code to the text before that code is run". A4.1.11 then says the code and its audit are not required before `analysis_m4`, and the code does not exist. So (iii) cannot hold when P becomes visible, and a reader can say Parts 2 and 3 were not yet binding. Separately, nothing requires A4 to precede `family.json`, `ps_frozen.json` or `epred_frozen.json`; M3 is running now. The n-rule, the operating points and PS status could be known to whoever finishes the text, and the label table of A4.2.1 depends on them. The author's firewall statement ("nothing chosen with knowledge of any M3 value") is true now and is not made a condition.

### F2 (major). The contribution list promises a stage that may be "not run", and one bullet overstates M1
Bullet 5 is "the same for every label" and names the Part 1 comparison. Part 1 is void if A4 is not committed first, stops on any consistency-gate mismatch, and does not run until the auditor matches code that is not yet written. This is plan review item A4 again (a numbered contribution whose Results subsection says "not run"). Bullet 5 also makes a Tier-3 analysis a numbered contribution while A4.1.10 item 1 bars it from title, highlights and conclusion; a conclusion normally restates the contributions. Bullet 4 says the score is "below a one-pass score without fine-tuning (0.581 and 0.607)": on JPEG q is 0.561 [0.547, 0.575] against 0.581 [0.569, 0.593], and those intervals overlap; no paired q-versus-TbV test exists or may be added (plan review A3). Only noise has non-overlapping marginal intervals.

### F3 (major). HARM and MIXED put a claim from a c > b rejection in the title; the card forbids it
Card v4 section 2, family P row, "Forbidden": "any claim from a rejection with c > b". SAP section 9 allows "GATE-M reduced verification accuracy". A4 follows SAP 9 and builds the HARM and MIXED titles, highlights and abstracts on it ("Gating flagged image tokens lowered ... accuracy") without noting the conflict. One of the two documents is wrong for these labels and A4 does not say which.

### F4 (major). POS-G asserts equivalence and a cause from a non-rejection
POS-G is triggered by K5 (S-M not rejected) or K6. The title says "but no more than a same-shape random mask", highlight 1 says "as did a same-shape random mask", and 6.1 says "a random mask of the same shape did as well, so the gain belongs to removing a set of that shape, not to the positions the score flagged". SAP 9 allows only "improvement, but not distinguishable from masking the same shape elsewhere"; K5 allows "not attributable to detection beyond mask geometry". A non-rejection at n = 300 is not "did as well" (A4's own Part 1 rule says "never equivalent, never as good as"), and "the gain belongs to" is a causal attribution.

### F5 (major). R3 has no label for a harm on d, and R3-INC would then be false
R3-INC is "R3; no such rejection". A Holm-adjusted Wilcoxon rejection with GATE-M lowering d is a rejection that is not R3-POS, so it falls into R3-INC, whose abstract says "gating did not change d detectably" and whose 6.1 says the same. That is false in that case. A mixed result under R3 (one corruption up, one down) is also undefined. Under R1/R2 A4 defined HARM and MIXED; the R3 path was left out.

### F6 (major). The POS-M title promises fusion that P does not test, and no title names a model
"Masked-likelihood token gating before image-text evidence fusion: a preregistered gain ...". P is the image direction alone (no text direction, no fusion). The only fusion test is family B, which can be "not run" or "untestable at ceiling". This is N5 and C4 of my first signature (no fusion claim in title, abstract or highlights unless the fusion run exists) and plan review A4. A4.2.2 item 4 licenses the word on "a P rejection with b > c", which is a statement about the gate, not about fusion. My first signature also required scope in the title (M9, single model); all nine titles say "a unified masked diffusion model" and none names UniDisc or one model.

### F7 (major). Part 1 cannot discriminate, and its comparator set is narrower than its names
(a) The detector-free rivals are the median and two symmetric trims. The corruption's effect on Delta has a known sign (replaced codes lower the matched caption's advantage), yet no estimator uses it. The "finding against the method" reading can then be reached only by the weakest natural rival, and the omission is fixed now ("not computed"). (b) SOFT discounts only tokens the hard gate already flagged (w = 1 elsewhere, w <= 1 on F = 1), so tokenwise its weights lie between GM's and NONE's. It does not answer plan review A8 (reliability weighting of every token); the contribution list and A4.1.10 call it "a soft reliability weight" without that limit. (c) When the detector is at chance (JPEG AUROC 0.56, noise 0.50), g_i is about 51 for every item, so TM-G is NONE trimmed by about 2.5 percent per tail and TM-G - GM repeats P's own contrast. (d) "Not distinguishable" counts as a finding against the method (A4.1.10), yet at n = 300 the SAP's own MDE is 0.08 to 0.11, and A4 admits the weakness only under R3 (A4.4 item 4). The rule turns low power into a reported negative.

### F8 (major). The mandatory abstract clause is wrong in one case, stronger than its trigger in another, and lets Tier 3 change a P abstract
(i) For "above GM" the clause says the comparator "was not shown to do worse"; it did better, and A4.1.10 itself calls that a finding against the method. (ii) Which comparator the clause names ("median / trimmed mean") is left free when several qualify. (iii) The R3 sentence "raised d at least as much" is triggered by "upper bound >= 0", which includes an interval such as [-0.3, 0.01] whose point estimate is far below GM. (iv) The clause makes the wording of a P-positive abstract depend on a step-5a Tier-3 result. AD.12 last sentence: "Nothing computed in steps 4 to 9 may change the wording of step 3"; SAP 7: no Tier-3 result enters a claim. A4 inserts step 5a but does not list this clause as an amendment of AD.12.

### F9 (major). Part 1 wording rules contradict each other and AB.1 item 2
A4.1.10 puts "findings against the method" "in the same paragraph as P". A4.2.2 item 5 says Part 1 may not "explain, qualify or predict" P and appears later "only as separate findings". AB.1 item 2 allows secondary results in Results "not as an explanation of P". A4.1.10 item 4 describes a comparator that beats NONE where GM did not as "a property of mean aggregation under this corruption": that is a causal clause about a P null, drawn from a secondary family.

### F10 (major). D18: the framing part is the right reading, the submission part is a rewrite, and the default is to bind without Shlok
(a) That "when does input gating help" cannot be a title, highlight or 6.1 opening under a P null follows from AB.1 and from plan review A1; A4 is consistent with it. (b) D18 as recorded (CONFIRM section 7 and "Shlok's answer" item 7) is conditional: submit as a "when does input gating help" article if S2, PS and FOIL are informative; the other branches are a CPU-only note or another venue. A4 replaces the condition with "submit under every complete P label", argues that "informative" is undefined and that a condition would make the venue decision outcome-dependent. That changes Shlok's decision; it is not a reading of it. AB.9 limits the lead's run and cut decisions; it does not limit the owner's submission decision, and "informative" can be defined from the AD.11 status map (run formal, run descriptive, not run, untestable at ceiling) without reading any estimate. (c) Admissible alternative reading, stated because you asked: AB.1 bans causal clauses and the use of PS as a demonstration; it does not ban a question-form framing whose answer is a set of separately labelled family results. A4's stricter bar (the phrase absent from highlights and 6.1) is admissible too. Which one is wanted is Shlok's call. (d) A4.4 item 5 says the outcome book "binds" until he answers, while A4.2.6 says the window for the literal reading closes at `analysis_m4`, and nothing stops `analysis_m4` from running first. "All recommended" accepted a recommendation that did not mention the AB.1 conflict, so it is not an answer to the question A4 now poses.

### F11 (minor). The highlight fallback does not fit
Counting characters (limit 85, itself E0): POS-M, POS-G, HARM and R3-POS become 88 to 89 with "{k} of 3 corruptions", and R3-INC 87. A two-name X ("JPEG and Gaussian noise") takes POS-M to 93. The stated repair does not repair.

### F12 (minor). NEG: figure and highlight against the claim
The NEG claim rests on the 90 percent interval lying inside plus or minus 0.05, but the summary figure shows 95 and 98.33 percent intervals with the dashed lines, so a reader sees an interval crossing the line beside an abstract that says exclusion. The highlight "moved matching accuracy by under 5 points" states a bound as if it were the size of a movement.

### F13 (minor). Pin scope and the seeds edit
`exp_p2/gate/tier3_fusion.py`, `tests/exp_p2/test_tier3_fusion.py` and the `seeds.py` append all fall inside the card's pre-launch scope (`git diff --quiet f2f7b2e1 HEAD -- exp_p2 tools tests`, card row A-1). Committing them before the remaining GPU stages makes every later pre-launch check fail unless a pin row moves first. `seeds.py` is imported by `analysis_m4`, and `meta()` writes `spawn_order` into every analysis output, so appending before `analysis_m4` changes the bytes of the P output file. The fallback seed makes the append unnecessary, and A4 does not say when it may be made.

### F14 (minor). Part 3(b) under AB.9
A time-only trigger with a logged inequality is admissible. Residual discretion: (i) the freeze (Fri 30 Oct 18:00 IST) is a constant here, but D18 lets the deadline move; a freeze moved after P is visible changes the inequality. (ii) W_S2 may be the constant (8 or 5.2 wall-h) or the smoke-based estimate; the choice is made when P is already visible (card row 6 commits `analysis.json` before row 7). (iii) "Does not invert the AD.8 priority" holds only when the check passes; a crash after FOIL has run leaves FOIL complete and S2 partial, which is the inversion the cut order exists to prevent. The 2 h margin covers one guard stop, and eight crashes are on record since 10-14. (iv) That FOIL has no input from M2-M4 and draws no random numbers is the author's reading of 75 lines (E3 by the author, not audited).

### F15 (minor). Smaller points
The printed multiplicity sentence contradicts SAP 7 ("no multiplicity statement is made"); A4 says "stricter" without noting it. "About 0.6 would exclude 0" is an expected count for 12 intervals, while the part reports many more. "No Delta distribution from M1-M4 was looked at" is the author's assertion about his own behaviour. The citations for TM20 and the evidential-discounting analogy are E0.

## Answers to the five check items

1. Tier-3 comparators: specified except the construction of the bootstrap index matrix (shape and generator call), which can move a CI in the third decimal. Arrays, order and seeds verified. None can enter P or explain a P null as written in A4.1.1, but F8 and F9 show clauses that let one qualify a P positive and describe a P null.
2. Forking paths: the 20 percent trim and the g/2 rule are not tuned, and NONE and GM are present for each. The risk is the narrow comparator set (F7), not a tuned one.
3. Outcome book: no title conflicts with AB.1 or K2 (D0074). It conflicts with the card, SAP 9 and the data in F3, F4, F5, F6; bullet 5 promises a stage that may be "not run" (F2).
4. D18: F10.
5. Part 3: (a) signed; (b) F14 and C4-10.

## Signed and not signed

Signed: A4.1.1 to A4.1.9 as specification; A4.1.10 items 1, 3, 6; A4.2.1 labels as definitions for NEG, INC, K1, R3-POS, POS-M and POS-G (conditions, not wording); A4.2.2 items 1 to 7 except the fallback in item 6; A4.2.3 titles, highlights, abstract and 6.1 sentences of NEG, INC, K1 and R3-POS (with F11, F12); A4.2.4 bullets 1, 2, 3, 6; A4.2.5 items 1 to 7; A4.3.1; A4.5.
Not signed: the binding clause of A4 as written (F1); contribution bullets 4 (the TbV clause) and 5 (F2); HARM and MIXED titles, highlights and abstracts (F3); POS-G title, highlight and 6.1 (F4); R3-INC abstract and 6.1 and the R3 label gap (F5); the POS-M title (F6); A4.1.10 item 2 clause wording, item 4's "property of mean aggregation", item 5, and "same paragraph as P" (F8, F9); A4.2.6 "reading I recommend" and A4.4 item 5 as default-binding (F10); A4.3.2 as written (F14).

## Conditions (dated rows by the lead; all before `analysis_m4` is first run on M4 data unless stated)

- **C4-1.** A4 binds for its specification (Parts 1 to 3) from its commit; condition (iii) gates only the running of the Tier-3 code. A row records the commit time of A4 relative to `family.json`, `ps_frozen.json` and `epred_frozen.json`; if A4 is committed after any of them, the row lists which of their values were visible to whoever finished A4.2.1 to A4.2.5.
- **C4-2.** Shlok's own sentence on D18, or a dated row "no answer; the AB.1 reading binds and the submission condition of D18 is unchanged", exists before `analysis_m4`. The submission condition ("S2, PS and FOIL informative") is recorded as his decision, with the status-map meaning of "informative" fixed in the same row, or as explicitly dropped by him. A4.4 item 5 (default binding) is struck.
- **C4-3.** Bullet 5 of A4.2.4 names Part 1 only if Part 1 has run. Bullet 4's TbV comparison is limited to what the intervals support (noise: non-overlapping marginal intervals; JPEG: overlapping; no paired test).
- **C4-4.** A dated row settles card section 2 ("forbidden: any claim from a rejection with c > b") against SAP 9 ("reduced") for HARM and MIXED; the title, highlight and abstract sentences of those labels are re-signed afterwards.
- **C4-5.** POS-G uses SAP 9 and K5 wording only; "no more than", "as did", "did as well" and "belongs to" are removed.
- **C4-6.** R3 gets labels for a harm on d and for mixed directions; R3-INC cannot state "no detectable change" in either case.
- **C4-7.** "Fusion" is absent from every title unless family B ran and was formal (C4 of the first signature); the title scope phrase names one model.
- **C4-8.** A4.1.10 items 2 and 5 are re-worded so that an "above GM" comparator is reported as better, the trigger matches the sentence (R3 included), the named comparator is fixed by a rule, and A4 states that it amends the last sentence of AD.12 for this clause (or the clause is struck).
- **C4-9.** One rule for where Part 1 appears relative to P (the "same paragraph" instruction and the "property of mean aggregation" sentence reconciled with AB.1 item 2 and A4.2.2 item 5). SOFT is named "discounting of the gate-flagged tokens" everywhere. Every "not distinguishable" carries n_d and the minimum detectable difference beside it, and the limits of F7 (a) to (d) are disclosed beside the Part 1 table.
- **C4-10.** Before the Tier-3 module or the `seeds.py` append is committed, a dated pin row covers both (card section 7). The `seeds.py` append waits until after `analysis_m4` or is not made (fallback seed). For FOIL before S2: the freeze constant and the W_S2 estimator (constant or smoke) are fixed in the rule now, a freeze moved after P is visible does not enter the inequality, and the inversion risk is added to the deviations box.
- **C4-11.** Minor wording: a highlight fallback that fits 85 characters; the NEG figure shows the interval that carries the claim; SAP 7 "no multiplicity statement" reconciled with the printed sentence.

## What would make me withdraw this signature

- Any Tier-3 number computed or printed before A4 and the C4-1 row are committed, or from a cell, contrast, trim, weight or seed other than those of A4.1.
- A P, PS, S-M or M4 value read by whoever finishes the A4.2 text before C4-4 to C4-6 are recorded, and then used in an edit.
- Part 1 run before the auditor's match to A4.1.11, or with a failed consistency gate.
- Any sentence that calls a P null "explained", "predicted" or "caused" by a comparator, SOFT, PS, S2, B or detection; any title, highlight or conclusion that names Part 1.
- A "when does input gating help" framing in title, abstract, highlights, conclusion or 6.1 under a P-null label without a dated amendment of AB.1 that I have signed before `analysis_m4`.

## Results that would force rejection of a claim made from A4

- Consistency gate mismatch (A4.1.3): no Part 1 number is valid until the discrepancy is explained against the unit tests.
- A comparator contrast whose interval excludes 0 in favour of the comparator on a P cell: a finding against the method for MED, TM-G and TM20, and against discarding only for SOFT; never against the detector. A comparator that beats NONE where GM did not is reported under the Tier-3 label as a property of the comparator, not as an account of the P result.
- A "not distinguishable" interval is not evidence of equivalence and may not be worded as such.
- POS-G, NEG or INC sentences that exceed SAP 9 wording: the claim they support is invalid as worded.
- If HARM, MIXED or an R3 harm occurs and C4-4 or C4-6 is unrecorded, no title or highlight can be drawn from it; the P table with the SAP 9 sentence stands.

## Residual risks the signature does not cover

Citations (E0); the 85-character limit (E0, for the venue scout); the claim that FOIL has no random draws or M2-M4 input; the E3 reading of UniDisc in A4.3.1 is mine (plan review B), not reproduced, with the non-strict load unclosed; many intervals with no multiplicity control; a single model; the lead's and the statistician's firewall statements are assertions, not attestations. Judgement, not measured: the most probable labelled outcomes are INC or R3-INC (v3 section 12), so most of this book is about stating a null well. A4 improves that, and the chance of a defensible positive claim stays at about 0.05 to 0.08.



---

# A4 r1/r2 re-signature (red team, 2026-10-29, after commit eadfa00b; M4 running; CPU only)

Read: the full current A4 (r1 + r2); `git diff f1671c91 5ee84384` on A4 (r2 is 23 added lines, all in the r2 row, the r2 notes and A4.1.10); card v4 section 2 (family P row) and its precedence clause; SAP 9 and A2.2; AB.1; v3 section 12; NOVELTY-CHECK section 4; CONFIRM-EVENING sections 7, 8, 12 and "Shlok's answer"; ledger D0073-D0076; GATE-CODE-AUDIT-TIER3 in full; `tier3_fusion.py` at 00b92d4d lines 205-262 (`reading`, `counts_against`, `accuracy_contrasts`). Not opened: anything under `runs/P2-GATE-M4`; no M3 or M4 value (I took rule R2, n = 500, endpoint Y from the subject line of commit f6ad4c56 and `stat` birth times of M3 files). One synthetic check (numpy/scipy on made-up discordance counts, CPU, seconds). Not read: huang2025evidential, Wilcox, Tukey (E0 as before).

## Verdict: SIGN WITH CONDITIONS (C4r-1 to C4r-5); confidence 0.65
No finding is `fatal`. Three are `major` (G1, G2, G3). I sign: r1 as the answer to C4-1 (in fact), C4-3, C4-5 (except the pooling gap G1), C4-6 (labels), C4-7, C4-8, C4-9, C4-10, C4-11; the r2 notes N1 and N3; the precedence reading of C4-4 (SAP 9 over card section 2); the D18 reading-1 outcome. I do not sign: the POS-G sentences as written (G1); the HARM and MIXED 6.1 and "counts against" wording (G2); the r2 rule for n_d < 10 as the basis for any "finding" label (G3); R3-HARM and R3-MIXED (moot, G6). The signature binds when the C4r rows are recorded before `analysis_m4`.

## Check (1): each C4-n
| C4 | Status | Evidence |
|---|---|---|
| 1 | met in fact; row not yet written | r1 committed 22:44:54; `family.json` file birth 22:45:00.336, `c1_head.json` 22:45:00.679, `ps_frozen.json` 22:45:13, `epred_frozen.json` 23:09:47 (stat). A4.2 text is unchanged since r1 (diff f1671c91..5ee84384 touches only the r2 lines). r2 (00:00:54) is after all three files, edits only A4.1.10 (Tier 3), and quotes n = 500, so R2 was visible to its author; the row must say so. No C4-1 row exists in `decisions.jsonl` (last row D0076). The M3 `items.jsonl` (headroom data) existed from 22:23, before r1; "not read" is the author's assertion |
| 2 | met in substance, with defects (G5) | D0076 plus CONFIRM s12 |
| 3 | met | Part 1 absent from the contribution list; bullet 4 limits the TbV clause to noise, JPEG overlap stated, no paired test; bullet 6 is status-conditional |
| 4 | precedence met; sentences not (G2); row not written | |
| 5 | met except pooling (G1) | "no more than", "as did", "did as well", "belongs to" are gone; title, abstract and 6.1 use SAP 9 and K5 words |
| 6 | labels met; sentences moot (G6) | R3-HARM and R3-MIXED exist; R3-INC needs no rejection in either direction |
| 7 | met | no title contains "fusion"; every title names UniDisc |
| 8 | met | abstract clause and R3 Results clause struck; AD.12 last sentence untouched |
| 9 | met, subject to G3 | one placement rule; SOFT-G and SOFT-A names; n_d and MDD beside each "not distinguishable"; F7 (a)-(d) printed beside the table; the sign-aware estimator is excluded with a reason I accept (it uses the label) |
| 10 | met | no `seeds.py` edit; pin row before the module; freeze constant fixed (Fri 30 Oct 18:00); W_S2 a constant (8.0 or 5.2; 5.2 = 2.6 busy GPU-h at duty 0.5, checked against CONFIRM s8 and card section 3); no smoke input; a stop ends FOIL-first; inversion risk in the deviations box; auditor confirmation of the FOIL reading is a precondition |
| 11 | met | I counted every highlight 1 for single names and the "{k} corruptions" fallback: maximum 85 (POS-G, R3-HARM), within the E0 limit of 85; the figure shows the 90 percent interval; the multiplicity sentence is replaced by a count |

## Findings
### G1 (major). POS-G pools corruptions with different S-M outcomes under one "not distinguishable" sentence
POS-G fires when K5 or K6 holds for at least one rejected corruption (A4.2.1). Its title, highlight, abstract and 6.1 use one `{X}` and say the gain is "not distinguishable from a same-shape random mask / masking the same shape elsewhere". Nothing restricts `{X}` to the corruptions where S-M did not reject. With JPEG S-M-rejected and noise not, the title would assert the limitation for JPEG, where S-M rejected: false. MIXED handles it ("by the S-M result for {X}"); POS-G does not.

### G2 (major). HARM and MIXED: the precedence reading is sound, two sentences are not licensed, and the text states a motive that a reviewer will quote
The reading that SAP 9 ("GATE-M reduced verification accuracy") outranks card section 2 ("any claim from a rejection with c > b") is correct under the card's own precedence clause. But (i) HARM 6.1 adds "the preregistered test counts this against the gate", a verdict that is in neither SAP 9 nor the card; (ii) A4.2.1 says no title carries a harm "to keep the harm out of the most visible place": positive results get a title claim, a Holm-rejected harm does not, and the document records the reason in those words; (iii) the HARM and MIXED highlights ("Token gating reduced ...", "Gating: ... rose ...") name no gate, model or severity, so a general statement rests on a one-model, one-severity rejection (the title carries the only scope); (iv) the MIXED highlight says "rose under {X}" with no K5 qualifier when X is S-M-unrejected. The ledger row that settles the card-versus-SAP conflict (C4-4 asked for a dated row) is not written.

### G3 (major). The r2 rule does not touch the reading that produces the "finding"
r2 replaces only the MDD test for n_d < 10. The three-way reading (`reading()`, tier3_fusion.py:216-224) is still the percentile-bootstrap interval for every n_d, and `counts_against` turns "above" into "finding_against_the_method" (detector-free) or "finding_against_discarding" (SOFT). My synthetic check (10,000 resamples as in A4.1.7, exact two-sided sign test for comparison): b = 4, c = 0 gives a lower bound of 0.0033 at n = 300 and 0.0020 at n = 500, i.e. "above GM", with exact p = 0.125; b = 3, c = 0 gives lower bound 0.0 (p = 0.25); b = 8, c = 0 gives lower 0.010 (p = 0.008). So four discordant items in one direction yield a finding against the method, and r2 prints B beside it as if B governed the label. The percentile bootstrap is not a valid interval at that n_d.

### G4 (minor). r2 override: coincides with the code at n = 500, differs elsewhere, and is not clean in the artifact
Verified numerically: B = 0.0122 (n_d = 0, n = 300) and 0.0074 (n = 500); B <= 0.05 up to n_d = 7 at n = 300 (0.0475; n_d = 8 gives 0.0519) and up to 15 at n = 500 (0.049). At the fold in force (n = 500) every n_d < 10 satisfies B <= 0.05, so r2 and the code's MDD rule give the same label and differ only in wording. At n = 300 they differ for n_d = 8, 9, and the switch back to MDD at n_d = 10 (MDD about 0.03) makes n_d = 10 "against" and n_d = 8 "uninformative": non-monotone, and the two thresholds are not commensurate (a power quantity against a confidence bound). The write-once `tier3_fusion.json` will carry `mdd` = 0.0 and `finding_against_added_value` for n_d = 0 with no "not used" label; r2 item 5 lets the lead choose, after the output exists, between hand-applying the rule and changing audited code (new SHA, new delta check).

### G5 (minor to major for the record). D0076 and CONFIRM s12: timestamps, "explicit", and the D18 frame
(i) The commit that contains the row and the answer is eadfa00b, 2026-10-29 00:05:46; CONFIRM s12 dates the question ~00:05 and Shlok's answer ~00:10, and D0076 `ts` is 00:12:00. The record cannot have been written after the answer it quotes. The order against `analysis_m4` is unaffected (M4 at about 115 of 500), but a preregistration audit trail with a row dated after its own commit invites doubt. (ii) D0076 says "explicit delegation"; the sentence ("Choose whatever alleviate") answers no option and is the lead's reading of an ambiguous sentence, as CONFIRM s12 itself says ("Read as a delegation"). (iii) The "informative" definition was offered to Shlok and not adopted by him; the lead adopts it under the delegation. This is the narrowing I asked to see in a row, so it is acceptable, but the row should name who fixed it. (iv) D0076 says "D18 submission condition unchanged", but D18's verbatim text submits the paper "as a 'when does input gating help' article"; reading 1 bars that phrase from title, abstract, highlights, conclusion and the opening of 6.1. The row does not say what becomes of the frame. What C4-2 required (reading 1 plus the unchanged condition with a status-only meaning of "informative", before `analysis_m4`) is present.

### G6 (minor). R3 sentences
The family file fixes rule R2 (commit f6ad4c56), so no R3 label can occur. For the record: SAP 9 has no row for a lowering of d and A2.2 allows only positive or inconclusive under R3, so R3-HARM and R3-MIXED have no governing clause; R3-HARM 6.1 says the result "says nothing about matching accuracy and counts against the gate"; R3-POS says trimming "raises d whatever their corruption status" where v3 section 12 says it "can"; A4.2.2 item 4 bars "verification" under R3 and the R3-POS title and abstract contain it.

### G7 (minor). Partial folds
A4.2.1 modifier: "completed n < 240 for a corruption gives INC". A corruption rejected with b > c at n < 240 is positive by A2.2's definition and inconclusive by "everything else"; the two sentences disagree.

## Check (2): sentence-level result
POS-M: consistent with SAP 9, K5/K6, K2 (D0074: the 6.1 clause says the score did not beat cheap rivals on JPEG and noise; no "our detector"), AB.1. POS-G: G1. MIXED, HARM: G2. R3-POS, R3-INC: no conflict with A2.2; R3-HARM, R3-MIXED: G6. K1, NEG, INC: unchanged since my first signature. Must-not claims 10-13 (NOVELTY-CHECK s4): no "first", no "risk-calibrated" as a selling word, "input-level source validation" kept, no "decision-level". "Fusion" in no title.

## Check (3): r2 rule for n_d < 10
The Clopper-Pearson formula, the bound |A^k - A^GM| <= pi_d and the quoted numbers are right. Gaps: G3 (the label comes from the bootstrap reading, not from B) and G4 (override unclean; it coincides with the code at n = 500).

## Check (4): D18 reading-1 row against C4-2
Present and sufficient in substance; defects in G5. A4.4 item 5 no longer says "binds by default" (it asks for the row).

## Conditions (dated ledger rows by the lead before `analysis_m4` is first run on M4 data)
- **C4r-1.** POS-G title, highlight, abstract and 6.1 carry the K5/K6 limitation only for corruptions where S-M did not reject, and carry none for a corruption where it did.
- **C4r-2.** A dated row settles card section 2 against SAP 9 for HARM and MIXED (my acceptance: SAP 9 governs). "Counts this against the gate" is not used unless SAP 9 or a signed addendum carries it. The motive phrase in A4.2.1 is not carried into any paper text. The HARM and MIXED highlights are re-signed after their scope and the MIXED K5 qualifier are settled. R3-HARM and R3-MIXED are recorded as moot under rule R2 and stay unsigned.
- **C4r-3.** No "finding against the method" or "against discarding" label is issued for a contrast with n_d < 10 on the strength of a percentile-bootstrap interval alone; the reading used for n_d < 10 is stated and signed before the output is read. Until then those cells are reported with n_d, b, c and B only.
- **C4r-4.** Rows: the C4-1 commit-order row with the file birth times above and the statement that r2 postdates the three frozen files and edits only A4.1.10; the D0076 correction (times, "explicit", who fixed the "informative" meaning, what becomes of D18's "when does input gating help" frame under reading 1); the pin row naming `test_gate_tier3_fusion.py` before the module is committed; and which of r2 item 5's two routes the lead takes, recorded before the Tier-3 output exists.
- **C4r-5.** The partial-fold sentence of A4.2.1 is made consistent with A2.2 for a rejected corruption at n < 240; the n_d = 8, 9 cliff of r2 at n = 300 is either declared moot by a row (n = 500 in force) or removed.

## What would force rejection of a claim made from A4 r1/r2
- A "finding against the method" or "against discarding" printed for any cell with n_d < 10 from the bootstrap reading (G3), before C4r-3.
- A POS-G sentence that applies the S-M limitation to a corruption where S-M rejected (G1).
- A title, highlight or abstract that states a harm as "counts against the gate", or the unscoped "Token gating reduced/raised" (G2).
- A P, PS, S-M or M4 value read by whoever edits A4.2 or A4.1.10 before the C4r rows exist, then used in an edit.
- Any Tier-3 number printed before the pin row and the auditor's match, or with a failed consistency gate (unchanged from the first A4 signature).

## Residual risks
All firewall statements (statistician, coordinator, lead: "no M3/M4 value read") are assertions, not attestations. The M3 headroom `items.jsonl` existed before r1. The E0 limit of 85 characters and the E0 citations are unchanged. Judgement, not measured: the most likely labels remain INC or NEG; r1 and r2 improve how a null is stated and leave the chance of a defensible positive claim at about 0.05 to 0.08.


---

# A5 signature (red team, 2026-10-29, on SAP addendum A5 final, commit b32e72a1; family H, SugarCrepe hard negatives; CPU only)

Read: `SAP-ADDENDUM-A5-HARDNEG-2026-10-29.md` in full (the draft only through the changes table); AB.1 of the SAP; `CONFIRM-EVENING` sections 12 to 14; `decisions.jsonl` D0080; the feasibility note (lines 14-41, 91-135); card v4 rows A-2, A-4, A-5 and v4-8; `threshold.json` of M2 (keys only); import lines of `run_gate_s2.py` and the `analysis_*`/`tier3`/`edec`/`epred` modules; grep of `run_gate_m4.py` for output. Recomputed with stdlib: exact McNemar (12,0) 0.00049, (18,6) 0.0227, (24,6) 0.00143, (6,0) 0.0313, (12,6) 0.238; P(G >= 3 of 50) at pi_d 0.04 = 0.323 (by hand); the three clock bounds 12:27, 12:36, 13:42 (all right). Not read: the code of `h3_gonogo`, `h_strata`, `build_hardneg_items` (none exists on this branch; it is at 336b31c6 only), the IMPL-J report, any S2/FOIL/Tier-3/H output. I opened no `runs/` outcome file. Evidence level of every finding below: E3 (text and code imports read), except the arithmetic (E4).

## Verdict: SIGN WITH CONDITIONS (C5-1 to C5-8); confidence 0.6 that this is the right call
No finding is `fatal`. Six are `major` (F1 to F5 and F9); F6 is major on one point (b). The design of H is sound as a separately labelled test on fresh images: the n-rule is outcome-blind to the sign, H3 and H4 images are disjoint, the exact test is valid conditional on the H3 decision, the arithmetic checks out, and the clock rule is not binding on the current schedule (S2 launched 09:01 for about 7.7 h ends near 16:45 Thu; H3 and H4(300) would finish Thursday night against a Fri 18:00 freeze). I sign the statistics (A5.4 to A5.6, A5.13), the data rules A5.2 as specified, and A5.5 / A5.5a as a rule. I do **not** sign the sentences and clauses listed under "Not signed". The signature binds when the conditions are recorded as dated rows before the first H3 item. It says nothing about whether H will give a result: by the addendum's own figures the likely outcomes are H-NOGO or H-INC (see F8).

## Findings

**F1 (major). The conclusion is both barred and permitted.** A5.1 says AB.1 extends "word for word": no clause from H in the title, abstract, highlights, conclusion or opening of 6.1. A5.9 placement item 4 then says "H may appear later in the conclusion with its prefix". The two cannot both bind, and the weaker one is in the section a reader quotes. AB.1 item 2 is about causal clauses, but item 4 of A5.9 lets any H sentence (including a positive) sit in the Conclusion beside the P null. Also unlisted in the placement rules: the cover letter, graphical abstract, figure captions, supplementary and README/Zenodo text, the "limitations" and "future work" paragraphs, and any statement of significance.

**F2 (major). The disclosure paragraph (A5.14) is narrower than what the file itself says was seen, and it carries a P explanation.** A5.0 says the statistician read, before r0, the P section, `outcome`, `s_m`, `c1_test`, `completeness`, parts of `mechanism` and `calibration`, and the one-line Tier-3 summary; A5.17 says H was written after P, PS, S-M, E-dec, E-pred and Tier-3 outcomes. The paragraph that goes into the paper says only "after the primary family had been analysed (label negative) and after the positive-control audit". It omits S-M, mechanism, E-dec, E-pred and Tier-3. It also states, as the motive, that the audit "had shown that the preregistered task changed few binary decisions". That is the sentence Must-not 1 bars elsewhere ("P was null because ... lacked headroom"), placed in Methods, where the placement rules allow it. The file never says which governs. A reviewer will read the Methods sentence as the explanation of the P null that AB.1 forbids.

**F3 (major). Nothing bounds further post-P families, and the placement rules can be loosened after the H result.** A5 is the fourth family-level addition after P's outcome (PS audit, Tier 3, FOIL and S2 stages, now H). There is no statement that H is the last. The feasibility note lists other candidates it declined (Winoground, ARO). If H is null, the logic that justified H (the P task lacked headroom) justifies another population, and the family-wise error of "some population rejects" is then unbounded and undisclosed. Separately, D-H2 is a default ("abstract: never") that Shlok may change; a switch after an H-POS would be outcome-dependent. The file says only "any change after the signature is a dated row, before any H item".

**F4 (major). The length rule cannot catch a length-driven rejection.** The add_obj and add_att negatives are longer (mean token difference 3.95 and 2.63); they are about 86 of 300 items. The wording clause fires only if the length-matched estimate for that corruption has the **opposite** sign with a 95 percent CI that excludes 0. With about 215 items and n_d of order 10 to 30, that interval will almost always include 0, so an effect carried entirely by the add_* items (b > c there, about 0 elsewhere) triggers nothing. "Length-matched subsets reported separately" is met in form, not in effect. The same holds for the per-subset "CIs only".

**F5 (major). Provenance of D-H2, D-H3, D-H4 and the audit trail.** A5.15 says "Source for all four: Shlok ... 'Yes, add it'". The question put to Shlok (CONFIRM s14) contained the family, its order (after S2, before the suite) and "P stays the preregistered headline". It did not mention the abstract (D-H2), patch and swap (D-H4) or unattended running (D-H3). CONFIRM s14 itself says these are the lead's reading ("since he gave no other instruction"), so "answered" overstates it. Unattended GPU use is the one with eight crashes on record since 10-14, and the memory on file says no unattended GPU; the A-2 approval was for the M2 relaunch ("Yes, both", 3x slow limit overnight). No ledger row exists for D-H2 to D-H4 (the last row is D0080, which names only the family). The file says "Written ... from about 10:40 IST" but its commit is 10:30:07 (Shlok's answer 10:23:21; draft 10:17:38). Same kind of defect as G5 in the A4 r1/r2 signature.

**F6 (major on point (b), otherwise minor). The H3 firewall is an honour rule, and a back door is left open.**
(a) `run_gate_m4` writes signed GATE-M arm summaries per item (`arm_summary` in each row) and per-chunk driver output into `runs/P2-GATE-H3/`. The module's JSON is clean, but nothing stops anyone, including the lead who must commit that directory, from reading the rows. A5.8 and A5.16 item 6 admit this ("honour rule").
(b) A5.8 lets "H3 signed results ... be reported only as pilot, descriptive" once the H4 analysis is committed. If the outcome is H-NOGO or "cut by time", H4 is never analysed, and a 50-item signed GATE-M-versus-none table is then available as a descriptive result with no test, after the rule said "do not test". The H-NOGO sentence forbids "no effect", but not the table.
(c) The tests described check output keys (`b`, `c`, `acc_gate`) and invariance to `yg` values, not stdout, stderr or logs; `load_items` loads the signed fields.

**F7 (minor). Rule details that leave discretion or do not match.**
- `decide` runs "after H3 is complete or at its deadline", but no deadline is defined in A5.5a or A5.12; `--now` exists "only for tests", and the operator can run `decide` later and so move n from 300 to 200 or 0 by the clock alone (outcome-blind, but discretion).
- Rule (a) is scaled to n = 300 (x6) while n_H4 may be 200 (x4); the bound is then not the one the test has.
- The H-NOGO sentence uses "{G*}", which is undefined when H+ is empty; and a NO-GO can come from headroom (a) alone, which only the bracket covers.
- G* is a maximum over up to three corruptions, so R1/R2 and the printed power statement carry a winner's curse; harmless for the test, misleading in the power statement.
- Rules (a) and (b) are not tied: F- items and the G items need not overlap, so a corruption can pass (a) on two clean-to-wrong flips and (b) on three unrelated gate flips.
- Rule 1 of A5.12 is "logged by the lead": the start decision is the lead's.

**F8 (minor, informational). H is unlikely to be discriminative, and the cheapest explanation of a positive is not excluded by the label.** From the addendum's own tables: P(GO at H3) is 0.008 at pi_d 0.008 (about the realised P rate), 0.32 at 0.04, 0.58 at 0.06; at n = 300 and pi_d 0.06 the power is 0.31 for theta 0.75 and 0.08 for theta 0.65. H-NOGO and H-INC dominate. Costs: about 3.7 GPU-h on a laptop with eight crashes on record, and a 13-family paper (1 - 0.95^13 = 0.49 under a global null, no adjustment). If a rejection with b > c appears, the cheapest alternatives are: (i) any 5 percent token removal trims heavy-tailed per-token evidence on thin-margin hard-negative items whatever the corruption (H-M addresses shape; H-C, the clean-image control, is descriptive and not in the label, so a gain that also appears on clean images does not change H-POS-M); (ii) a memorised COCO positive (U8); (iii) the H-POS templates use one {X} for several corruptions, the pooling defect of G1 and C4r-1 again.

**F9 (major). Code order lets the frozen P analyser change under pending work.** A5.11 changes `analysis_m4.py`, `run_gate_m4.py`, `run_gate_m3.py` and `gate_driver.py` by merge. `analysis_s2`, `analysis_omni`, `edec`, `epred` and `tier3_fusion` all import `analysis_m4` (checked by grep), and the S2 job is running now from the pin `8d1bee3a`, with the FOIL, S2, Tier-3 and Omni analyses still to come. A5.11's order says audit PASS, then merge, then pin row A-6, but not "after S2 and the dependent analyses are written", and it does not require that `analysis_m4` on the committed P2-GATE-M4 rows reproduces the committed `analysis.json` unchanged after the merge. "Defaults unchanged" is asserted from IMPL-J (E4 there), not re-run for P. Changing the P analyser's source after P's result is public is the case the card's pin discipline exists for.

## Check items of the brief

1. **Can H rescue or reinterpret P?** Not by any statistic: separate alpha, no pooling, no P-versus-H contrast, P's A4.2 sentences "whatever H shows", H never in title, highlights or abstract, Must-not 1 to 7 are good. It can by sentence, through F1 (conclusion), F2 (Methods motive), the unlisted places in F1, and F3 (placement changeable by default). Not airtight until C5-1, C5-2, C5-3.
2. **Honest and fully disclosed after P?** The file is honest internally (A5.0 and A5.17 say plainly that H is post hoc and motivated by P). The public disclosure paragraph is narrower than the internal admission (F2), and there is no stop rule (F3). Multiplicity inside H is right (Holm over the same three; untested corruptions keep p = 1; conservative). Across families: 13, unadjusted, printed. No test combines P and H.
3. **H3 go/no-go.** Discretion: the F7 list. Leakage into H4: statistically none (disjoint images, gid-keyed corruption seeds, frozen threshold, exact test conditional on the decision); procedurally F6. Gate flags on headroom items: acceptable as a disclosed deviation, because SAP 5 existed to keep operating points blind and none is chosen on H3. It stays acceptable only while F6 is closed and the H3 images never re-enter anything.
4. **Pool, strata, exclusions, leakage.** The disjointness set is complete for what exists: cal, head, test, test_ext, probe-1 and 2, M1, M5; FOIL lies inside the folds (the file's claim 3, a CPU check by its author; I did not repeat it). H-L6 positive control and H-L7 steward check are right. Equal subset weighting and one row per image are fine; the unstratified exact test is conservative under heterogeneity (variance of b - c is at most E[n_d]). Length: F4. Contamination caveat: printed and adequate.
5. **Cut order and time rule versus the Fri 30 Oct 18:00 freeze.** Arithmetic correct (12:27, 12:36, 13:42). The rule is outcome-independent except for H3's own unsigned counts. Residual: the conditions before H3 (audit, merge, pin, builder, steward, my signature) are not in the time rule; if they slip past Fri 12:27 H is "not run", which is acceptable and honest. The cut order (suite, H4, H3, ..., S2 last) agrees with running H after S2 and before the suite.

## Conditions (dated ledger rows by the lead before the first H3 item unless stated)

- **C5-1.** One placement rule for the Conclusion (A5.1 or A5.9 item 4), stated once; the barred places extended to the cover letter, graphical abstract, captions, supplementary, README and Zenodo text, limitations, future work and any statement of significance, for H clauses that explain, qualify or predict the P result (F1).
- **C5-2.** The A5.14 paragraph names everything read before r0 (S-M, mechanism, calibration, E-dec, E-pred, the Tier-3 one-liner, per A5.0 and A5.17) and says which sentence governs where the audit finding appears (motive, stated once in Methods, versus Must-not 1); the "changed few binary decisions" clause is either removed from paper text or marked as motive only and kept out of Results and Discussion (F2).
- **C5-3.** A dated row states that family H is the last family added after the P outcome (or that any later family is labelled the same way and listed in the deviations box), and that the A5.9 placement rules may only be tightened after the first H3 item (F3).
- **C5-4.** The length rule is restated so that it can fire (for example the length-matched and mismatched n_d, b, c printed beside every H rejection, with the clause unless the length-matched estimate is on the same side with an interval excluding the opposite effect). A5 says which, before H3 (F4).
- **C5-5.** A5.15 is corrected: D-H2 and D-H4 are the lead's defaults awaiting Shlok's veto; D-H3 (unattended) is either confirmed by Shlok in words about H or limited to attended runs; rows are written for D-H2 to D-H4; "from about 10:40 IST" is corrected against the commit time 10:30:07 (F5).
- **C5-6.** A dated row states: no person opens `runs/P2-GATE-H3/items.jsonl`, chunk outputs or driver logs before the H4 analysis is committed; signed H3 numbers are never reported when H4 was not analysed (H-NOGO, cut by time, pilot incomplete); the `h3_gonogo` tests also assert that stdout, stderr and logs contain no signed gate quantity, and the auditor reads the code for that (F6).
- **C5-7.** A5.5a gets a defined `decide` deadline (a clock time or "at H3 completion"), the H-NOGO sentence's {G*} is defined for an empty H+, and the (a) bound is stated as scaled x4 when n_H4 = 200 (F7).
- **C5-8.** Before merge: the auditor's delta audit includes a byte-identical regeneration of `runs/P2-GATE-M4/analysis.json` (and of any committed Tier-3, E-dec or E-pred output) from the merged `analysis_m4`; the merge waits until S2 has ended; the pin row A-6 records both (F9).

## Not signed

The A5.15 statement that the four D-H answers are Shlok's answers (F5); A5.9 placement item 4 as written (F1); the A5.14 paragraph as written (F2); the length rule of A5.7 as a safeguard (F4); the last sentence of A5.8 on reporting H3 signed results as "pilot, descriptive" without the C5-6 limit (F6).

## What would make me withdraw this signature

- Any H3 row, summary or log with a signed GATE-M quantity opened, quoted or copied by anyone before the H4 analysis is committed; or a signed H3 number printed anywhere when H4 was not analysed.
- Any change to the placement rules, labels, quotas, seed, corruptions, threshold or rule constants after the first H3 item that is not a dated addendum signed first.
- A paper sentence that calls the P null explained, predicted or caused by headroom, hard negatives or task difficulty; any H clause in title, highlights or abstract.
- Code changes to `analysis_m4` or the frozen stages that are not shown to leave committed P outputs byte-identical.
- A further family added after the H outcome without the C5-3 labelling.

## Results that would force rejection of a claim made from H

- A Holm rejection with b > c whose length-matched and mismatched counts show the effect only in the add_* items, with no length clause: no claim.
- A rejection with H-CAL Z_cal above 2.13 printed without the realised clean flagged share: the CRC wording is invalid for H.
- H-M not rejected: no "beyond a random mask" wording. A rejection with the clean-image control (H-C) showing a comparable gain: the corruption-specific reading is void.
- H-L6 count zero, H-L7 not signed by the steward, or a `folds_hardneg.json` hash different from the committed one: nothing from H is usable.
- Completed n below 240: no H-NEG.
- A rejection with b < c: a harm claim only, worded as in A5.9, never "the gate fails on hard negatives".

## Residual risks the signature does not cover

Single model; U8 contamination (COCO val2017 positives); selected subset of val2017 (exchangeability is an assumption, H-CAL can only refute it); LLM-written negatives with possible residual text cues; 13 families without adjustment; the honour-rule firewalls (lead, statistician) are assertions, not attestations; GPU stability (eight crashes since 10-14, S2 still running); I did not read the code, the IMPL-J report or any output. Judgement, not measured: H adds a small chance of a reportable positive (about 0.05, mostly H-POS-G) and a high chance of H-NOGO or H-INC; it does not change my estimate of a defensible positive headline claim (about 0.05 to 0.08).

---

# A5.1 amendment and A6 signature (red team, 2026-10-29, on SAP addendum A6 DRAFT, commit 71c78306, and the freeze commit bf2edd7c; CPU only)

Read: `research/CONTRACT.md`; `SAP-ADDENDUM-A6-LRF-2026-10-29.md` in full; A5 r1 sections A5.0 and A5.1 and the r1 table (C5-3); my A5 signature above; `LEARNED-CEILING-REPORT-2026-10-29.md` in full; `LRF-FROZEN-2026-10-29.md` (front matter, sections 3 and 4); `runs/P2-LRF-FROZEN/spec.json`, `freeze_check.json`, `hpo.json` (head), `diagnostics.json` (feature ranking head, `length_checks`); `CONFIRM-EVENING` sections 14 to 16; `decisions.jsonl` D0080 to D0082; code: `exp_p2/run_gate_m4.py` 97, 100-165; `exp_p2/gate/pipeline.py` 30-58; `exp_p2/gate/scores.py` 82-110; `exp_p2/gate/baselines.py` 29-37; `analysis_posthoc/learned_ceiling/lrf.py` 40-80, `data.py` 55-90. Checked (E4, CPU, stdlib/numpy): `tier3_fusion.json` noise0.1 arm accuracies; the image ids of all 14 `runs/P2-*/items.jsonl` files against `folds.json`, probe-1/2 and M1; `git ls-files` for the M1 codebook and the D cache; exact McNemar power at n 520 (0.730 at Delta 0.05, 0.863 at 0.06, 0.370 at 0.03, size 0.041 at alpha 0.05; script in the session scratchpad `rt_power.py`). Not read: the TNNLS design notes and Codex review, any S2, FOIL, suite or H output, the A6 power script. Opened no fresh-fold or H file (none exists).

## Verdict: SIGN WITH CONDITIONS (C6-1 to C6-11); confidence 0.6 that this is the right call

(1) The A5.1 stop rule may be amended **once**, before the first H3 item, to admit Study 2; text below. (2) A6 is signed as a design **only** with the conditions. One finding (K1) is **fatal as written**: the tested object reads the true caption's length at test time, and A6 lets L1 alone license "confirmed". It is resolved only by the dated ledger row of C6-1; until then the gate is blocked. Eight findings are major, five minor. The rest of A6 is sound: fresh images, gid-keyed corruption seeds, a hash-pinned object, exact tests, fixed-sequence logic, prespecified wording for every branch including the null, and an honest power statement (I reproduced the L1 numbers).

## (1) The A5.1 stop rule: decision and the text I sign

**Decision.** Admissible once, for three reasons. First, no H data exist, so admitting Study 2 now exploits no H outcome. Second, Study 2 tests a new object on new images, so it cannot change P's alpha. Third, the information it uses (P, PS, Tier 3, the learned ceiling) is disclosed. Against it: C5-3 was written so that post-P analyses stay Tier 3, and A6 promotes exactly such a Tier-3 result (bdc87e4e) to a confirmatory family (K8). This is acceptable once, with full disclosure, and never again. The amendment binds only if C6-1 to C6-11 are dated rows before the first H3 item (C6-9 states which may come later).

**Amendment text (signed as written; wording of item 7 editable, substance binding):**

> **A5.1 amendment 1 (2026-10-29; red-team signed with conditions C6-1 to C6-11; written before any H item and before any Study 2 item).**
> 1. The C5-3 stop rule is amended once. Exactly one further confirmatory study is admitted after the P outcome: Study 2 (Addendum A6 r1), a test of one frozen method (LRF; the single object named under C6-1 and pinned under C6-2) on a fresh COCO val2017 fold. Its families are L, L-NI, L-LEN and LG as defined in A6 r1, and no others.
> 2. After this amendment, family H and Study 2 are the last confirmatory families of Paper 2. No further family, study, population, fold, method, model, corruption, refit or re-freeze receives alpha, for any reason: an L1 or H outcome, a change of route (D0082 Route A or B) or venue, or a reviewer request before acceptance. Any later analysis is Tier 3, labelled "added after the primary, family H and Study 2 results", listed in the deviations box, and kept out of the title, abstract, highlights, conclusion, contribution list, cover letter and repository front matter. This amendment cannot itself be amended to admit another family. A second amendment of the stop rule removes the confirmatory label from every post-P family: H and Study 2 then become Tier 3.
> 3. Timing. This amendment and A6 r1 are committed before the first H3 item. If an H3 item exists before both commits, this amendment is void, and A6's tests are Tier 3 (CIs only, LRF never "confirmed").
> 4. Multiplicity. P (Holm, m 3), H (Holm, m 3), L (fixed sequence, m 4), L-NI (m 1), L-LEN (m 1) and LG (Holm, m 3) are separate families, each at 0.05. Nothing is pooled or contrasted across P, H and Study 2. The paper prints the family count (17) and 1 - 0.95^17 = 0.58, with "no adjustment across families". P keeps its A4.2 sentences under every H and Study 2 outcome. AB.1 extends to Study 2 word for word.
> 5. Run order: S2 -> H3 -> H4 -> L1 -> LG -> baselines -> suite. The order and the A5.12 and A6.10 bounds and cut order depend only on time and on whether audited code is ready. No stage is started, delayed, cut, repeated or extended because of an outcome of another stage. A missed H bound is final: H is "not run", even if GPU time later becomes free.
> 6. Placement rules of A5.9 and A6.12, and A6 as a whole, may only be tightened after the first H3 item or the first L item, whichever comes first.
> 7. Disclosure (Methods, once, and the deviations box): "Study 2 was added after Study 1 had been analysed (primary result negative), when the target venue changed. The method it tests (LRF) was designed post hoc on Study 1's 500 test items. Before the design, Study 1's primary and secondary results, its positive-control audit, its exploratory comparators and an exploratory learned-weighting analysis had all been seen. In that analysis four learned-weighting families were compared and a logistic generalised additive model was selected; two other method designs were considered and not pursued. The configuration was frozen (SHA-256 {model}, commit {c}) before any Study 2 image was selected. Study 2 was preregistered (Addendum A6 r1, commit {c}) with a rule that no further confirmatory study would be added. All LRF numbers on Study 1's items are post hoc and exploratory. Study 2 tests a different method on different images and does not bear on Study 1's conclusion." No sentence in the paper gives Study 1's result as the reason for LRF's design (AB.1).

## (2) Findings on A6

**K1 (fatal as written). The tested object reads the true caption's length, and L1 alone can license "confirmed".**
- Every caption-withheld feature is computed on a sequence built from the **true** caption's tokens:
  - `run_gate_m4.py:142`: `gate_scores(sc, cap_tok, ...)`.
  - `pipeline.py:32-34`: B and s3 are computed on `sc.build(cap_tok, codes)`, and D comes from the cache keyed by `len(cap_tok)`.
  - `run_gate_m4.py:153`: tbv on `sc.build(cap_tok, codes)`.
- The content is masked, but the length is not. The frozen report measures the channel: the length of c+ is recoverable from item feature summaries (cross-validated R^2 0.41; permutation null max 0.019, p 0.005; `diagnostics.json` `length_checks`).
- B and tbv were not re-scored at the other length. tbv has the largest per-feature contribution SD in the diagnostics (0.70).
- Clean and splice128 show a leak-shaped stratum pattern (difference 0.045, p 0.15 and 0.16). The frozen report itself concludes "as frozen, LRF is not order-blind by construction" and recommends a length-neutral re-freeze (LRF-FROZEN section 3).
- The fresh-fold L1 run computes features in the same way (A6.11 item 2 reuses `run_gate_m4`), and the true caption always occupies the scored slot. So L1 tests a decision rule that receives a label-dependent input at test time.
- A6.7 makes the only clean test (L-LEN, where c+ and c-_L have equal length and the rule becomes order-symmetric) a wording clause, not a condition for "confirmed".
- A reviewer who reads Methods or the code will call the method non-deployable and the confirmation leaky, whatever the size of the leak.
- The cheapest alternative explanation of a positive L1 is not excluded by design.

**K2 (major). Which object A6 tests is unresolved, and resolving it opens a fork.**
- A6.2 names "the model in `runs/P2-LRF-FROZEN/`" (sha ca5c4e2f), while the frozen report recommends a re-freeze at L_FIX = 13.
- If the M4 items are re-scored, the protocol is re-fitted and the re-frozen model's M4 accuracy is then looked at before one of the two objects is chosen, that choice is selection on M4 outcomes.
- A6 does not say which object is tested, who chooses, by when, or on what information.

**K3 (major). Inputs of the frozen features are not pinned, and a missing input fails silently.**
- nbr is the top-ranked feature in `diagnostics.json`, and it needs `runs/P2-GATE-M1/codebook.npy`. D needs `runs/P2-GATE-DCACHE/DI_n*.npy`. Both are untracked in git (`git ls-files` returns nothing).
- The frozen hash set (`spec.json` `code_sha256`, `model_sha256`) covers only `data.py`, `families.py`, `lrf.py` and the model.
- `baselines.neighbour_codebook_distance` returns NaN when the codebook is absent (`baselines.py:31-32`). `lrf.raw_from_npz` and `infer_item` (`lrf.py:41-73`) have no finiteness check, so NaN weights give `decision=False`, which is counted "wrong".
- An L1 run from a checkout without these files would turn into a non-confirmation silently. A6.3 already says some steps must run in the main worktree.

**K4 (major). L2 is L1 restated, and its sentence sits next to AB.1.**
- On the M4 items GATE-M and NONE are identical on noise0.1: both 0.676, with the same b/c of 85/34 against SEL (learned-ceiling report, table).
- L2 is therefore close to a duplicate of L1. A confirmed L2 would turn one finding into two sentences, and it unlocks L3 and L4 at no cost.
- Its template, "LRF also exceeded the masked-likelihood gate", is the closest sentence in A6 to "LRF fixes GATE" (A6.1 item 2).

**K5 (major). The route record contradicts AB.1.**
- `CONFIRM-EVENING` section 16 says "with the preregistered GATE study as motivation/analysis"; D0082 says "GATE preregistered study kept as analysis".
- A method paper that presents a null for hard gating and then a learned soft weighting reads as problem and solution, whatever its individual sentences say. A6.12 controls sentences, but it does not control section order, figures or tables.
- The natural motivating sentence of a soft-fusion paper ("hard gating discards useful evidence") is A6.1's own example of a barred sentence. The writer team will meet this rule on page 1.

**K6 (major). The headline is at an effective two-sided 0.10, and it is the paper's second headline attempt.**
- P (Holm at 0.05) failed. L1 is a second confirmatory headline at one-sided 0.05.
- Under a global null, the chance that at least one of the two headlines is a false positive is about 1 - 0.95 x 0.95 = 0.0975 (derived).
- A6 prints the 0.025 flag but lets a title or abstract gain claim rest on 0.025 < p <= 0.05.

**K7 (major). Rescue routes remain open if L1 is not confirmed.**
- LG, L-LEN and L-NI are not gatekept by L1. The LG row lets "under {type} (held out, severity 3) LRF raised accuracy" appear in Results after an L1 failure.
- D0082 says "Shlok may switch to Route A". A switch after L1 data would choose the paper's method on L1's outcome.
- The titles for the two branches are not fixed in A6.
- With F2 on Mon 18:00 and submission on Tue morning, text drafted on the assumption that L1 is confirmed is the likely failure mode.

**K8 (major). A Tier-3 result is promoted, and the disclosure lists what was seen but not what was tried.**
- Had the learned ceiling been null there would be no A6, so the paper adds a confirmatory study because an exploratory analysis looked good. The fresh fold makes L1 valid, but paper-level honesty needs the candidates as well as the results.
- A6.1 lists the results seen. It does not list the candidates considered: F1 to F4 and SEL; SCER and CANAL, for which a novelty audit exists, `research/paper2/tnnls/NOVELTY-AUDIT-SCER-CANAL-2026-10-29.md`; Routes A and B.

**K9 (major). Power and the winner's curse.**
- I verified power 0.73 at Delta 0.05 and 0.37 at 0.03.
- The +0.102 belongs to the cross-fitted procedure, with per-fold HPO. The frozen object, refitted on all 500 items, has **no** out-of-sample estimate at all.
- `freeze_check.json` in-sample accuracies (noise0.1 0.788) are training accuracy.
- With L-LEN as a co-primary (C6-1 option b), joint power falls. As an assumption-laden illustration, L-LEN alone at n 460, pi_d 0.30, Delta 0.05 has power 0.59.
- A null is likely to be inconclusive, not negative. A6.3 already says so.

**K10 (minor). The L-NI margin was chosen after the clean CI was seen.**
- 0.03 was set after the M4 clean CI (-0.024 to +0.030) and the in-sample clean 0.90 had been seen.
- Three points is a 25 percent relative increase in clean error (0.12 to 0.15).
- A6 calls the margin "fixed now" but does not say it was chosen after this was seen.

**K11 (minor). "Held-out noise" overstates what LG tests.**
- Shot and speckle noise are close relatives of additive Gaussian noise. Impulse noise is the only structurally different cell.
- Severity 3 is not matched to sigma 0.1.
- Power is 0.54 at pi_d 0.20 and Delta 0.06.
- "Held-out noise family" will be read as a generalisation test that the design cannot deliver.

**K12 (minor). The exclusion list is enumerated, not a union.**
- My check (E4): all image ids in the 14 `runs/P2-*/items.jsonl` files lie in `folds.json`, probe-1, probe-2 or M1, so the A6.3 list is complete today.
- The rule is still an enumerated list. Runs added before the fold build (S2 completion, the suite, `P2-SUITE-SMOKE` images) are covered only if someone remembers them.

**K13 (minor). The CLIP and SigLIP comparison.**
- Printing "drops" side by side invites a robustness ranking that A6 bans in words.
- The clean-accuracy gap to CLIP and SigLIP on random COCO negatives is not measured here (unknown). If it is large, the reader's question becomes "why not use CLIP?", which is a significance problem for TNNLS, not a validity one.

**K14 (minor for A6, major for TNNLS). LRF has no novelty audit.**
- The only audit in `research/paper2/tnnls/` covers SCER and CANAL.
- D0081's "something not in existence" is unverified for a logistic-GAM token weighting of likelihood-ratio evidence. This is unknown, not shown to be false.

## (3) What a TNNLS reviewer or an AI evaluator will call circular

1. **The features see the label's length** (K1). This is the one objection that is true as the object stands.
2. **"Your preregistered test set became your training set, and then you preregistered again."** This is not circular if three things hold: the commit order is object, then A6 r1, then fold build, then first L item; nothing on the fresh fold is fitted; and nothing is added afterwards (C6-1, C6-9, the amendment). It reads as circular if any M4-item LRF number appears beside P's GATE numbers in a main-text table or figure (C6-4), or if the in-sample numbers are quoted (C6-8).
3. **"Hard gating fails, so we propose soft learned gating."** This is AB.1 by structure (K5).
4. **"The second confirmation is the first one again."** This is L2 (K4).
5. **"One corruption, one severity, one model, one negative rule; same pipeline."** L1 replicates on a new image sample; it does not show that the method generalises. The A6.12 scope sentence covers this only if every LRF sentence carries it.
6. **The same team designs, freezes, builds the fold, runs and analyses.** This is mitigated by hashes, the auditor and the data-steward. The firewalls on what was read are still statements, not attestations (A6.0 item 6).

**Cheapest alternative explanations of a positive L1, in order:**
- (i) A caption-length channel through the layout of c+ (K1).
- (ii) A Gaussian-noise detector built into nbr and tbv. LRF may be a learned version of "down-weight noise-damaged codes", which is unlikely to be new. The exploratory comparators argue partly against a trivial rule: median 0.678, 20 percent trimmed mean 0.682, soft gates 0.676, DET 0.712, CHG oracle 0.746, against SEL 0.778. These numbers are on M4 only, and no single-feature rule was tried.
- (iii) The particular noise realisations, which are fresh per gid, so this is mitigated.

The cheapest explanation of a null: power 0.73 at half the exploratory effect, or winner's-curse shrinkage beyond half.

## Conditions (dated ledger rows by the lead; before the first H3 item unless stated)

- **C6-1 (K1, K2; resolves the fatal).** A6 r1 names exactly one tested object, by a rule fixed now:
  - **(a)** The L_FIX = 13 re-freeze of LRF-FROZEN section 3:
    - The invariance check gives max abs diff 0 on 5 items x 4 conditions.
    - The protocol is unchanged, and the new sha is committed before the fold build.
    - The choice of (a) is declared **before** any re-frozen M4 accuracy is computed. Any such numbers are reported as exploratory whatever they show.
    - Model ca5c4e2f is never scored on fresh items.
  - **(b)** Otherwise, model ca5c4e2f:
    - "Confirmed", "validated" and any title, abstract or conclusion gain claim require **both** L1 and L-LEN to be rejected with b > c (an intersection-union test; no alpha split).
    - Every LRF sentence says "with caption-withheld scores laid out at the true caption's length; not order-blind".
    - The frozen report's length-stratum analysis (its step 5) is printed beside L1.
    - If L-LEN is "not run", LRF is "not confirmed (length control not run)".
  - Whether (a) applies is decided by a clock time stated in the row: (a) only if its commit exists by that time, else (b). Nothing else enters the choice.
- **C6-2 (K3).** The object's hash set adds `codebook.npy`, every `DI_n*.npy` the fold can use, and the scoring entry point. The scorer refuses to run when any feature or weight is non-finite, and verifies all hashes at start in the checkout that runs. The gate-auditor tests the NaN path.
- **C6-3 (K4).** Every L2 sentence prints GATE-M versus NONE on noise0.1 beside it. L2 never appears in the title, abstract, highlights or conclusion, and is never worded as LRF "outperforming" or "improving on" gating.
- **C6-4 (K5).** A dated row supersedes "GATE study as motivation" (CONFIRM section 16, D0082):
  - Study 1 is not the motivation of LRF in any paper text.
  - No section, figure or table arranges Study 1 and Study 2 as problem and solution.
  - No table or figure puts LRF numbers (fresh or M4) beside GATE-M results on the M4 items outside the supplement's exploratory section.
  - The chronology appears once, in Methods (amendment item 7).
- **C6-5 (K6).** A title, abstract or highlight gain claim needs one-sided p <= 0.025 for L1. If 0.025 < p <= 0.05, the result is "confirmed at the preregistered one-sided 0.05 level" in Results only. If L1 is in the abstract, the L-NI sentence is in the abstract too.
- **C6-6 (K7).**
  - If L1 is not confirmed (or a partial prefix is not rejected), L3, L4, L-LEN, LG and L-NI appear only in Results, with the L1 non-confirmation in the same paragraph, and nowhere in the title, abstract, highlights, conclusion or cover letter.
  - A6 r1 fixes the title for each L1 branch now.
  - Route and venue are fixed before the first L item. A later switch does not remove Study 2 from the paper.
- **C6-7 (K8).** The disclosure of amendment item 7 is used, naming every candidate considered (F1 to F4, SEL, SCER, CANAL).
- **C6-8 (K9).** A6 r1 states that the frozen object has no out-of-sample estimate. `freeze_check.json` and in-sample accuracies are never quoted as performance.
- **C6-9 (timing).**
  - A6 r1, with C6-1 to C6-8 and C6-10 to C6-11 in its text, is committed before the first H3 item; after that it may only be tightened.
  - The C6-1 object commit, the A6.0 item 6 statement and the C6-2 hashes come before the fold build.
  - The fold build comes before the first L item.
  - Git order is the evidence.
- **C6-10 (K12).** L0 checks disjointness against the union of image ids in every `runs/P2-*` items, selection and pool file present at build time, plus all SugarCrepe images, not against an enumerated list. The data-steward's L7 record states that union.
- **C6-11 (K10, K11).** LG is worded "other noise types (shot, impulse, speckle; imagecorruptions severity 3)", never "held-out noise family". L-NI states that its margin was fixed after the M4 clean interval had been seen.

## Not signed

- A6.7 as a safeguard under option (b) without the C6-1 conjunction (K1).
- The A6.12 L2 row as written (K4).
- The LG and L-LEN rows as usable after an L1 failure without C6-6 (K7).
- A6.1 as the public disclosure (K8).
- CONFIRM section 16's "GATE study as motivation" (K5).

## What would make me withdraw this signature

- Any refit, re-freeze, threshold or feature change after the first L item.
- A choice between the C6-1 objects made after re-frozen M4 accuracies were seen.
- A fold build commit earlier than the object commit.
- Any Study 2 output read before its run is complete.
- A family, study or method added after this amendment.
- A route switch used to drop an L1 null.
- Any sentence, section order or figure linking LRF to the P null.
- An M4-item LRF number outside the "post hoc, exploratory" label.

## Results that would force rejection of a claim made from A6

- L1 one-sided p > 0.05 or b <= c: no LRF gain claim anywhere. Under option (b): L-LEN not rejected with b > c: no "confirmed".
- Any hash mismatch, a non-finite feature, the L6 count zero, L7 unsigned, or a broken commit order: nothing from Study 2 is confirmatory.
- Under (b), a gain present only in the true-caption-longer stratum: the length reading wins and no method claim stands.
- L-NI not shown while L1 is in the abstract: "a clean-image loss of up to three points is not excluded" goes in the abstract.
- L3 or L4 rejected with c > b: a harm sentence is mandatory wherever the L1 gain appears.
- Baseline pixel parity not shown: no CLIP or SigLIP number in the main text.

## Residual risks the signature does not cover

- One model, one severity per corruption, one negative rule.
- UniDisc and the CLIP and SigLIP pretraining may include COCO (unknown).
- The firewall statements are honour rules.
- GPU stability (eight crashes on record) makes "not run" the most likely failure.
- I did not read the TNNLS designs, the A6 power script or any code beyond the lines listed.
- LRF's novelty is unaudited (K14).
- Judgement, not measured: if C6-1(a) is met, a defensible LRF headline has probability of about 0.4 to 0.55 (power at a plausible shrunk effect, times the chance the effect is real). Under (b) it is lower.

**Ledger.** No rows added: the brief allows edits to this file only. Under the red-team rules, the fatal K1 blocks the gate until the orchestrator records the C6-1 resolution in `decisions.jsonl`.

---

# A6 r1 check (red team, 2026-10-29, on commit 941a260b: A6 r1 and A5 r2; ledger D0083 at 5ff2c0d7, D0084 at 635e781e; CPU only)

Read:
- `git diff 71c78306 941a260b` for both addenda: A6 r1 in full, and A5 r2 (the r2 table, the quoted amendment and the edited stop-rule line).
- Ledger rows D0083 and D0084.

Checked (E4):
- **Amendment text.** It matches my signed text word for word, items 1 to 7.
- **Hashes.** `sha256sum` of `codebook.npy`, `DI_n013.npy`, `data.py`, `families.py` and `lrf.py` equals the A6.2 table.
- **No outputs exist.** There is no H3, H4, re-score, L_FIX, fold or Study 2 directory under `runs/`.
- **Commit order.** Signature 0ea9cf33 (14:35:18), then D0083 5ff2c0d7 (14:35:19), then A6 r1 and A5 r2 941a260b (14:40:35), then D0084 (14:40:36). All of these precede any H3 item.

## Per condition

| Condition | Status | Evidence in r1 / note |
|---|---|---|
| C6-1 (K1, K2; fatal) | **MET** | Option (a) was declared (D0083) before any re-scored output existed. A6.2 fixes:<br>- the L_FIX = 13 layout for B, s3, D and tbv;<br>- the positive control at the true length;<br>- the invariance gate across c+, c- and PAD (0, or at most 1e-6 by an auditor row before any re-frozen output);<br>- no re-frozen accuracy before the hash commit;<br>- ca5c4e2f retired.<br>A6.10 item 2 has no fallback. That is stricter than my clock rule (Study 2 is "not run" instead of option (b)), so it is acceptable. Delta keeps its own lengths, as it should. tex and nbr do not depend on the layout. **K1 is resolved in design**; it is closed in fact only when the invariance check passes. |
| C6-2 (K3) | **MET** | The hash table includes the codebook and `DI_n013.npy` (values verified). The entry points go into the pin row. The scorer checks hashes at start. A non-finite value is an error, never "wrong". The auditor tests three failure paths. |
| C6-3 (K4) | **MET** (exceeded) | L2 is removed. GATE-M on the fresh fold is supplement-only. No LRF/GATE-M comparison appears in any text. |
| C6-4 (K5) | **MET** | A6.1 items 2 and 3, A6.12 placement 2 and 3, and the A6.13 chronology appear once each. D0084 corrects the "motivation" wording of D0082 and CONFIRM s16. |
| C6-5 (K6) | **MET, one clause open (minor)** | A6.4 sets the headline threshold at 0.025, and branch B keeps "confirmed" in Results only. Open clause: branch B's abstract sentence prints {D} and p for L1 without the L-NI sentence, although C6-5 says "if L1 is in the abstract, L-NI is too". A tightening closes it (allowed at any time). |
| C6-6 (K7) | **MET** | The no-rescue paragraph is in place. Branch titles A to D are fixed. Route and venue are fixed before the first L item (A6.0 item 3). |
| C6-7 (K8) | **MET** | A6.13 names F1 to F4, SEL by inner CV, SCER, CANAL, two routes and the first-freeze length defect. |
| C6-8 (K9) | **MET** | A6.2 step 4, A6.14 item 1 and the Must-not list. The L_FIX cross-fit is exploratory and only sets n. |
| C6-9 | **MET** (text and git order so far) | A6.0 items 1 to 3. Still to be met by execution: the object commit, the lead's statement and the full hash set before the fold build. |
| C6-10 (K12) | **MET** | A6.3 uses the union of image ids, SugarCrepe is included, and the manifest lists every file read. |
| C6-11 (K10, K11) | **MET** | A6.5 has the LG wording. A6.4 and A6.12 state that the L-NI margin was chosen after the M4 clean CI had been seen. |

## New points in r1 (none fatal, none major)

- **R1 (minor). The n-rule depends on design data.** n_L is set from the L_FIX cross-fit on the M4 items.
  - It is a prefix of a fixed 533-item list, decided before any fresh item exists, so it cannot bias L1.
  - The risk: a large cross-fit effect lowers n towards 400. Power at a true half-size effect (Delta 0.05) is then about 0.62, the shrinkage being applied once only.
- **R2 (minor). The re-score GPU stage has no go-ahead clause.** It is a GPU stage of about 2.5 h, possibly overnight before Mon 04:15. A6.0 requires Shlok's GPU go-ahead only before the first L item, so the re-score (and its unattended status) needs his words too.
- **R3 (minor). Titles B and C put both studies under one question.** "Does learned reliability weighting help ...? Two preregistered studies" groups Study 1 (a hard gate) with Study 2.
  - This is not a causal link, so AB.1 holds.
  - A reader may still take Study 1 as a failed case of the same question. The A6.12 placement rule 2 binds the text under them.
- **R4 (minor). The family list does not add up as printed.** A6.7 lists 12 names for "17 families". The count comes from AD.11 and A5.13, which I did not recompute.

## Verdict: SIGNED (all of C6-1 to C6-11 met in text; C6-5 has one minor open clause, R2 needs Shlok's words before the re-score)

- The A5.1 amendment 1 (A5 r2) and A6 r1 are signed.
- K1 no longer blocks the gate: D0083 and A6.2 resolve it in design.
- The signature lapses for Study 2 if any of the following happens:
  - the invariance check fails beyond 1e-6;
  - a re-frozen accuracy is computed before the object's hash commit;
  - the object commit misses T_RF;
  - any item of the "What would make me withdraw" list of the A6 signature occurs.

No ledger rows added (the brief allows edits to this file only).
