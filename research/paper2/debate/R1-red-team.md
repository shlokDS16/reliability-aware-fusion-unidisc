```yaml
agent: red-team
date: 2026-10-28
brief: Debate round 1, questions Q1-Q5, hostile reviewer for Information Fusion or better
sources_examined: [research/CONTRACT.md, debate/QUESTION-2026-10-28.md, MORNING-2026-10-28.md, prereg/PREREG-GATE-MUST-v3-2026-10-28.md lines 1-257 (sections 1-14; section 15-17 not read)]
coverage: SAP, spec v2, sign-off and novelty re-audit not re-read; I rely on the card's quotations of them. No numbers below are mine; every figure is quoted with its source, estimates labelled.
```

## Verdict
Reject as it stands, and still reject with all three additions, unless the minimum set below exists. Ledger rows: none added (brief asked for the file only).

## Q1. Is the measurement claim enough? (fatal)
No. The card says the most probable outcome is "inconclusive or a null" (section 12; spec confidence 0.35, SAP power 0.19-0.36 at n = 300 under Holm). A high-impact venue does not accept "a threshold we built did not clearly help, on one 1.4B model, one dataset, one corruption draw, one mask seed". The "novelty" is "incremental, 0.50" and "only as a measurement paper" (re-audit, quoted in card section 1). Information Fusion fit is not argued: the card itself says the MUST tier "contains no fusion result", fusion is "untestable at that ceiling" (text direction 0.990), and caption corruption and re-infilling are not run (section 13). A fusion journal paper with no fusion result is a scope rejection by itself.

## Q2. The core validity problems (what I would reject on, with or without additions)
1. **"GATE-M" is not a method run in the network.** It drops terms from a mean over a caption-only pass (writer's point; card section 3). It is a post-hoc trimmed mean. Dropping the lowest-evidence tokens raises d = mean/sd by construction (card competing explanation 6, "variance trimming"). Only a removal that changes the network's own computation (S2) tests the stated mechanism. Fatal for the word "re-masking".
2. **The guarantee does not cover the claim.** CRC bounds false alarms on clean tokens of exchangeable clean items. Tokens are nested in items, and corrupted inputs are a shift. The guarantee says nothing about power, so "conformal" is decoration for the downstream result. The card reports a 21-item AUROC of 0.52-0.54 on JPEG/noise against 0.76 for sign-flipped pixel variance (exploratory). If the detector is at chance there, no threshold rescues it. Major.
3. **Endpoint is easy and indirect.** Matching against a deranged negative (clean accuracy 0.843 in probe 1) is not a downstream task. Nobody uses this accuracy. Major.
4. **Comparators.** The denoise arm is a sigma-matched NLM that "lowers PSNR by 1.69 dB" on JPEG and "favours GATE-M" (card S-DN, D17). The rival in S-D is chosen on the data over about nine candidates. Major.
5. **Contamination (U8).** COCO val2017 may be in UniDisc or LlamaGen training data; unmeasured. Major.
6. **Narrow estimand.** One model, one corruption realisation per image, one mask seed, variance across seeds "not in the intervals" (section 7). Major.

## Q3. The three additions
**(1) Patch and swap into the main test: mostly window dressing, and it damages rigour.** Patch and swap replace tokens by uniformly random codes (positive-control text, section 6). A likelihood-based gate removing random-code tokens is close to tautological: the card already records dry-run AUROC 0.967 and 0.962 on 21 items. Winning there shows the pipeline is not broken (that was their pre-registered role as a chance bar), not that the method is useful. Moving the positive control into the primary family after seeing that JPEG/noise look null is a forking-paths decision; "disclosed" does not repair it. If they join P, m rises above 3 and the Holm bar on the realistic corruptions gets stricter; if they replace P, the claim is selected on the dry run. Risk: reviewer reads it as retargeting to where the answer is known. Cost: small GPU (M4 already encodes patch), large prereg cost (card v4, new SAP addendum, new gate-auditor pass).
**(2) Omni-Diffusion 8B 4-bit: high risk, low credit.** Different tokenizer, different layout, different likelihood. The folds, L1-L10 layout checks, the UniScorer, the headroom ladders and calibration are all UniDisc-specific; the 202 tests "do not cover any real-GPU path" (section 14). 4-bit on Blackwell is unverified, SenseVoice needs a fix, and it cannot be costed before a timing run (MORNING). Quantisation noise confounds a likelihood-based detector, so a null there is uninterpretable and a positive is unauditable. Unaudited new code under a deadline. A second model that is run on a subset, with a different protocol, is worse than none, because it invites "worked on A, not B, so B was reported as a robustness check".
**(3) A real published corruption benchmark: depends which, and likely mismatched.** FOIL-COCO is caption-side. The frozen claim is image-token corruption; the caption direction is at ceiling (0.990) and the caption-corruption runner (S1) is not built or frozen. Image "benchmarks" of corruption (JPEG, noise, blur recipes) are the same synthetic recipes again, not real corruption. Needs data check, statistician addendum and an unbuilt runner. Window dressing unless the primary endpoint matches the benchmark's labels natively.

## Q4. Improvisation
Nothing extra: every additional arm adds an unfrozen path. The only item with real value is S2 re-infill (see Q2.1); it is not built, and the card says it cannot enter P or any Tier-2 family.

## Q5. Where the Thursday deadline breaks rigour
- GPU is on hold, two crashes on 27 Oct, M0 not run, the diagnosis is "about 50 percent" confidence (section 11b). MUST is "2.6 GPU-h item time (estimate), about 5 h wall" (MORNING); M0 adds about 45 min. The red team's earlier judgement (not a measurement) was about 0.20 chance of a defensible submission by the weekend; the deadline is now earlier.
- Any added arm needs an addendum "before the first item" (section 13). Adding all three plus S2 in one day means either unfrozen runs or no time to audit. Freezing and running on the same day invites peeking: the card forbids M4 analysis before the fold completes (section 10); a Thursday-evening manuscript with figures forces looks.
- Writing the manuscript before M4 exists means results sections get written to fit; the 35 todos are the evidence of this risk.
- A crash mid-run leaves a prefix; under n < 240 the card says "not rejected is not evidence". A rushed null cannot be reported as negative; it is "inconclusive" by the card's own rule.
- Adding families after the headroom check changes m after information has been seen.

## Q-min. What would have to exist for the claim to be credible (acceptance conditions, not proposals)
(a) M0-M5 run exactly as frozen at 623faaff, complete n >= 240, all arms reported incl. nulls; (b) the S-M geometry-matched control rejected on the same corruption as P with b > c; (c) at least one effect in the network (S2), against UniDisc G.1 as matched baseline, not a post-hoc sum; (d) the detection result at a level beating the best non-generative rival out of sample (S-D2) on at least one realistic corruption; (e) a second configuration under an identical frozen protocol, complete, not a subset.

## Results that force rejection
No Holm rejection in P with b > c (K3); S-M not rejected (K5/K6); K2 on JPEG and noise; completed n < 240; any look at M4 data before completion; any arm added after the first test item without an addendum; any sentence in the abstract claiming fusion, re-infilling or caption corruption without those runs.

## One experiment whose absence causes rejection
S2: true re-masking in the network with real repaired images against the G.1 recipe.
