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
