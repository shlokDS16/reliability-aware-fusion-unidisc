```yaml
agent: statistician
date: 2026-10-28
brief: Debate R1, inference view on patch/swap, second model (Omni-Diffusion 8B), real benchmark
sources_examined: [research/CONTRACT.md, research/paper2/debate/QUESTION-2026-10-28.md, research/paper2/prereg/SAP-GATE-2026-10-28.md (lines 1-574 of 883), research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md section 11, MORNING-2026-10-28.md (grep GPU-h only)]
coverage: SAP sections 1-10 and Appendix A script; SAP lines 575-883 (rest of Appendix A output) not read. No run files opened. Power numbers below were computed this session on CPU with the Appendix A exact-McNemar machinery (scratchpad pw.py); they are assumption-conditional, not results.
claims:
  - statement: "Moving patch and swap into family P (m 3 -> 5) costs little power but buys nothing and adds a post-dry-run fork; keep them outside P."
    status: supported (derived)
    evidence: "exact power, n=300, pi_d=0.10, theta=0.75: 0.59 at alpha'=0.0167 (m=3), 0.52 at 0.01 (m=5); MDE net gain 0.060 -> 0.063"
    level: derived under SAP assumptions A1-A3
    confidence: 0.85
```

## Position
The inference contract is: the headline test is family P (JPEG, noise, splice; UniDisc; exact McNemar; Holm m=3 fixed), frozen at the commit of the SAP and code pin 623faaff. Nothing Shlok added may change it, enlarge it, or share its alpha. Every addition goes in its own, pre-declared, labelled family. Gains are in coverage, not in the strength of the headline.

## Q1. Cleanest primary claim
Keep the measurement claim, scoped exactly: "On UniDisc, for each of three realistic image corruptions at a headroom-selected severity, we measure the paired accuracy change of image-direction verification when GATE-M drops flagged tokens, with the pre-fixed Holm family of three." A rejection with b > c is the only route to "GATE-M helps". A null is reported with the 95 percent interval (SAP section 9). The measurement claim is enough for the statistics; whether it is enough for Information Fusion is the novelty question (re-audit 0.50), which a p-value cannot settle. Do not add words such as "robust", "general" or "across models" to the abstract unless family R (below) supports them.

## Q3. Each addition: inference value, risk, power, disclosure
**1. Patch and swap.** Value: positive-control (existence proof) that the detector and the gate can work when the corruption is large and easy. Risk: it was added after the 21-item dry run showed model-score AUROC about 0.52-0.54 on JPEG and noise (E4, exploratory). Large corruptions are chosen to favour the method; a reader will see a favourable condition picked after an unfavourable look. Handling: stay Tier 3 as in SAP section 7 ("sanity corruptions"), reported with the same table layout, paired bootstrap CI only, no p-value in any claim, wording "positive control, not evidence of generalisation". Do not promote to P: m=5 lowers power (0.59 -> 0.52 at (0.10, 0.75), derived) and the promotion would itself be a post-hoc forking path. Cost: near zero (one encode per item already in M4).
**2. Second model (Omni-Diffusion 8B, 4-bit).** Value: the only way to say anything beyond "one 1.4B model". Risks: (a) a different tokenizer and head, so it needs its own calibration fold and its own headroom check; no UniDisc threshold transfers; (b) 4-bit on Blackwell untested and per-pass time unmeasured; (c) with two models there is no meta-analysis and no "heterogeneity" estimate. Design: family R, gatekept: Omni is tested only on corruptions rejected in P (b > c); one exact McNemar each, Holm over a fixed denominator of 3 (p = 1 for corruptions not eligible), alpha 0.05 inside R, never rescues P. Models are not interchangeable replacements: if Omni fails to load or crashes, report the failure; do not swap in another model. Wording on success: "the direction replicated on a second model", not "generalises".
**3. Real benchmark.** Value: external validity of the corruption. Risk: FOIL-COCO foils are caption corruptions (text side), which probe the text-direction gate (S1), not the image gate in MUST; real image degradations carry no token-level truth, so detection AUROC is unavailable and only Y can be scored. Also COCO overlap: check ids against probe-1/2/calibration/headroom/test lists and UniDisc/LlamaGen training statements (U8) before scoring. Design: one frozen subset (ordered id list, fixed seed, committed before any GPU run), one pre-named endpoint (paired accuracy of GATE-M vs none), one test (family B, m=1, alpha 0.05, exact McNemar), descriptive interval otherwise.

## Disclosure required given the 21-item dry run (all in the paper, Methods plus a "deviations" box)
1. The dry run (21 items of probe 2, CPU fallback, runs/P2-GATE-CPU/m1_fallback/analysis.json) was seen before the following were decided: patch/swap emphasis, the second model, the benchmark, and (if done) any baseline orientation rule. State this with the date and commit SHA of each decision.
2. 21 items give no usable interval for AUROC; any statement from them is exploratory. S-D must be reported on all 200 probe-2 items and on the 179 items not in the dry run (sensitivity).
3. "Sign-flipped pixel variance about 0.76" is a post-hoc orientation. Rule to fix before M4: each cheap baseline's sign is set on the calibration fold (or the 179 unseen items), never on the 21 or on test; baselines are otherwise left as in SAP 2.5. This is a SAP amendment (A2) with a before-data timestamp; it biases against q, which stays stated.
4. If K2 triggers (q not above the best cheap baseline) say so in the abstract; do not rescue it by restricting to patch/swap.
5. Report every model, benchmark subset and corruption run, including failed loads and aborted runs.

## Q4/feasible sample sizes (GPU budget; every GPU figure is an ESTIMATE)
UniDisc MUST: 300 items (2.6 GPU-h item time, spec 11.1), 500 only if rule R2 fires (+about 0.8-1 GPU-h). The spec's whole-MUST limit is about 6 GPU-h with contingency 3.9, leaving roughly 2 GPU-h for additions, if the GPU holds.
- Omni (ASSUMED 4-6x per-pass time of UniDisc, unmeasured): 100 calibration items plus 120-150 test items, image direction only, clean + the P-rejected corruptions (about 1.5 GPU-h; could be 2x higher). Power at n=150, alpha 0.05, 80 percent: needs net gain about 0.074 at 10 percent flips, 0.106 at 20 percent (derived). At n=120 about 0.082 and 0.118. So Omni can only confirm a large effect; with no gating on UniDisc results its CI will be wide, say so and call it "directional replication".
- Real benchmark: 150 items from one frozen list (about 0.2 GPU-h per corruption condition on UniDisc, ASSUMED from 0.15 s/pass). Same MDE as above.
- Kill points: Omni load or timing check fails at the 20-pass measure-only chunk (spec 11.3), or projected Omni time exceeds 1.5 GPU-h: drop it and say "single model". Benchmark list not frozen by the time M4 starts: drop it.

## Q5/order (inference only)
1. Freeze ordered lists, SAP amendment A2 (baseline orientation; families R and B; patch/swap Tier 3), commit, before GPU.
2. M2, M3 (headroom), sample-size rule, then M4 on UniDisc: the only run whose result decides the headline.
3. Only after M4 completes: family R conditional on P-rejections; family B.
4. Cut first: Omni, then benchmark, then S-D extras. Never cut: the full P table, calibration check, completeness report.
No look at Y until each planned fold is complete or the freeze (SAP 8.2).

## Concerns
- The dry run already points toward K2 (q about chance); expect an honest "detection falsifier met" and plan the abstract for it.
- Omni timing/crash risk after two crashes on 27 Oct.
- Mask-seed and corruption-seed variance remain outside every interval.
- A p-value says nothing about novelty or practical importance; the Information Fusion decision rests on the former.
