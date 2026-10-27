```yaml
agent: lab-engineer
date: 2026-10-28
brief: MUST-tier code of GATE-METHOD-SPEC-v2 section 11 (M1-M5) with CPU tests; no GPU, no model weights, no runner launched, HOLD file untouched
sources_examined:
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (full), GATE-METHOD-SPEC-2026-10-28.md (v1, sections 0-13 read)
  - research/paper2/probes/PROBE2-CRASH-DIAGNOSIS-2026-10-28.md (section 5, abort rules and staged plan)
  - exp_p2/{scoring,core,common,run_probe1,run_probe2,driver}.py, exp001/runtools.py, tools/gpu_guard.py (head)
coverage: all of v2 sections 4-11 that MUST needs; SHOULD/COULD items are listed under "Not built". Nothing was run on a GPU.
claims:
  - statement: "110 CPU tests in tests/exp_p2 pass (24 s), 96 of them new (test_gate_*.py; the other 14 are the existing probe tests), under the project .venv (Python 3.12, with a copied pytest shim) and under the default python"
    status: supported
    evidence: "command in section 5; output captured this session, not stored in runs/"
    level: E4 (code), not a research result
    confidence: 0.9
  - statement: "Every GPU path (UniScorer layout, tokenizer, VQ encode, real logits, memory, timing) is untested; only the fake network exercised it"
    status: supported
    evidence: section 4
    level: E0 for the GPU path
    confidence: 0.95
```

# GATE implementation notes (M0-M5)

Code is in `exp_p2/gate/` (library) and `exp_p2/run_gate_m{0..5}.py`, `exp_p2/analyze_gate_m1.py` (entry points); tests in `tests/exp_p2/test_gate_*.py` with the
CPU stand-in `tests/exp_p2/fake_gate.py`. Probe 1 and probe 2 code, tests and run directories are untouched (git shows only new files). Commits: c8d8e923,
5b295ee4, ae4d33ff, 9ef850f8 and the last one of this session.

## 1. Spec section to code

| Spec (v2 unless "v1") | What | Where |
|---|---|---|
| v1 3.1-3.3, v2 4.1 | B (K=8 masks, caption masked), C/Lambda (image fully masked, caption visible), D (everything masked, layout only), q = B - D, u = -q in float32, s3 from the B passes, TbV-style observed-position pass, caption-side B (S1) | `gate/scores.py` |
| v1 3.3 "D per n, at most 28" | disk-backed null cache `runs/P2-GATE-DCACHE/` (image null 64 MiB per n, text null), memory-mapped; L10 layout-only check | `gate/dcache.py`, `gate/checks.py: l10_once` |
| v1 5, v2 6, Alg. 3, 4' | CRC threshold, ties by jitter U(0, eps0) at calibration AND test with eps0 = half the smallest non-zero gap of the pooled calibration scores, strict `u > tau`, infeasible alpha (< 1/(n+1)) flags nothing, word units (min piece score) | `gate/calibrate.py`, CPU fit: `gate/fit_threshold.py` |
| v2 4.3, 7.4, Alg. 10 | no gate, geometry-matched random gate (random non-zero torus shift of GATE's own mask), scattered random, changed-code gate, plain-B top-k, s3 top-k, text-side random words | `gate/arms.py` |
| v2 Alg. 5', 7.2 | Delta_j = Lambda^{c+}[v] - Lambda^{c-}[v]; Y = 1[mean_R Delta > 0] (ties wrong); z_R; also d = mean/sd; empty R gives exactly 0; text-direction PMI (probe-1 `afull` layout with gated image tokens masked) | `gate/evidence.py`, `gate/pipeline.py` |
| v2 4.2 | patch texture, neighbour codebook distance, code rarity (leave-one-item-out), s3, plain-B, TbV-style (+ copy-through diagnostic for U7), random; sign-oracle copies (`*_neg`) | `gate/baselines.py`, `gate/detect.py`, `exp_p2/analyze_gate_m1.py` |
| v2 4.3, 7.3 | JPEG q10/q5 and Gaussian noise 0.10/0.20 (identical calls to `run_probe2.corrupt`, tested), splice 128/192, patch and swap (token level), OpenCV `fastNlMeansDenoisingColored` with library defaults | `gate/corruptions.py` |
| v2 7.5 | calibration 300 / headroom 100 / test 300, seeded, disjoint, excluding the 494 probe ids (300 + 200 - 6 shared), 5-32 tokens; deranged negatives restricted to images sharing no annotated COCO category; extension of the test fold to 500 | `gate/folds.py`, `gate/data.py` |
| v2 Alg. 11 | hard negatives: 80-category synonym table written once, same-supercategory replacement not annotated and not mentioned in the five references, number and article handling, skip counts, audit sheet, `apply_audit` with Wilson interval | `gate/hardneg.py` |
| v2 7.3, 9, Alg. 9 | headroom check (ladder walk, H1/H2 at 2 paired SE), `family.json`, discordance scaling and the n_d rule | `gate/headroom.py`, `gate/stats.py` |
| v2 5.3 | Prop. 4 general form, corrected special case, plug-in estimation from per-token Delta | `gate/theory.py` |
| v2 7.1, 7.4, 6 | M4 analysis: McNemar + Holm, mechanism contrasts, realised FAP, precision, FAP on clean tokens of corrupted items, Prop. 4 refutation flag | `gate/analysis_m4.py` |
| v2 7.6, 11.4 | per-item AUROC tables, paired bootstrap of q against the best cheap rival, falsifier; CPU fallback on partial probe-2 data | `gate/detect.py`, `exp_p2/analyze_gate_m1.py` |
| v2 8 | Stouffer and Fisher LDA weights (secondary) | `gate/fusion.py` |
| v2 Alg. 12 | coherence test: pairs, half masks, 3-pass gaps, noise floor, pre-stated reading | `gate/checks.py`, `exp_p2/run_gate_m5.py`, `gate/coherence_report.py` |
| v2 11.1 | M1 post-hoc, M2, M3, M4, M5 item functions; resumable loop (arrays written first, the row is the commit marker; torn tail repaired; failed items logged) | `exp_p2/run_gate_m{1..5}.py`, `gate/runner.py` |
| HOLD, crash diagnosis 5 | project-wide hold check (`runs/P2-PROBE-02/HOLD.txt`, `runs/<run>/HOLD.txt`, `runs/GATE-HOLD.txt`) in every runner and in the driver; per-item guards with the diagnosis thresholds; 1 s telemetry, `--max-temp 80`; M0 stage-1 script | `gate/hold.py`, `gate/guards.py`, `gate/gate_driver.py`, `exp_p2/run_gate_m0.py` |

Row and array budgets per item match the spec's itemisation and are asserted on the fake network: M2 12 passes, M3 2, M4 75 (70 without TbV) with a 3-member
family, M5 24 (+24 on every fourth item), `test_gate_runners_fake.py`.

## 2. Commands (all from the worktree root; GPU commands only after Shlok removes the hold file)

`PY` = `C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe`. Nothing below has been executed.

**M0 (crash-diagnosis stages; Shlok present, AC power, other GPU apps closed).**
```
:: stage 0 (CPU)
set CUDA_VISIBLE_DEVICES=
python -m pytest tests/exp_p2            (the .venv has no pytest; see section 5)
:: stage 1: load, one batch-4 forward, 5 min idle  (refuses while any hold file exists)
PY tools/gpu_guard.py --log runs/P2-M0-STAGE1/telemetry.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.run_gate_m0 --run-id P2-M0-STAGE1 --idle-minutes 5
:: stage 2: probe 1 control, 10 items into a NEW run dir (this module does not look at hold files)
PY tools/gpu_guard.py --log runs/P2-M0-STAGE2/telemetry.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.run_probe1 --run-id P2-M0-STAGE2 --n 10 --limit 10 --soft-minutes 10
:: stage 3: probe 2 items 21-25 (resumes the existing run unchanged)
PY tools/gpu_guard.py --log runs/P2-PROBE-02/telemetry-m0s3.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.run_probe2 --resume --limit 5 --soft-minutes 10
```
The diagnosis' source edits to `run_probe2.py` (first-item memory limit, power stop, `MEM_FRAC=0.60`) are NOT made: they change probe 2 and need Shlok's approval. The new
runners carry equivalent guards (`gate/guards.py`). Open point: `MEM_FRAC=0.60` caps PyTorch at about 7.2 GB, below the 8.2 GB peak the probe report measured at
batch 4; I kept the runners' default at 0.75 (`--mem-frac`).

**M1.**
```
PY -m exp_p2.gate.gate_driver --stage p2                      :: completes probe 2 (run_probe2 unchanged) under the hold check, 1 s telemetry
PY -m exp_p2.gate.gate_driver --stage m1 --extra "--tbv"      :: D at stored codes (<= 28 null passes) + TbV-style pass on the 4 corrupted images; exports the VQ codebook if reachable
python -m exp_p2.analyze_gate_m1 --probe-run P2-PROBE-02 --m1-run P2-GATE-M1      :: CPU: AUROC table, paired q vs best cheap, falsifier, tbv_verdict.json
```
**M2.** `PY -m exp_p2.gate.gate_driver --stage m2` (builds `runs/P2-GATE-FOLDS/folds.json` with the real tokenizer on first use), then
`python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2` (CPU; writes `threshold.json`, `codefreq.npy`). Commit `folds.json` and `threshold.json` before M4.

**M3.** `PY -m exp_p2.gate.gate_driver --stage m3`, then `python -m exp_p2.gate.headroom --run-id P2-GATE-M3` (CPU; `family.json` with the endpoint decision). Commit
`family.json` before any M4 item is scored. If it says "UNDER-POWERED", decide (500-item test fold via `--n 500` on M4, or z-score primary) and record it before M4.

**M4.** `PY -m exp_p2.gate.gate_driver --stage m4 [--extra "--tbv on"]` (refuses to start without `threshold.json` and `family.json`; `--tbv auto` follows
`tbv_verdict.json`), then `python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-M4 --family-run P2-GATE-M3`.

**M5.** `PY -m exp_p2.gate.gate_driver --stage m5`, then `python -m exp_p2.gate.coherence_report --run-id P2-GATE-M5 --mu <clean mean per-token paired evidence from M4>`.

CPU-only, any time: `python -m exp_p2.gate.cpu_dryrun` (section 5), `python -m exp_p2.analyze_gate_m1 ... --out-dir runs/P2-GATE-CPU/m1_fallback --no-pixels`.
Hard-negative audit: `hardneg.audit_sheet` / `apply_audit` are library calls (no CLI); the reviewer pass itself is not automated.

## 3. Ambiguities and how I resolved them

1. **z does not behave as the spec says under a random gate.** v2 7.2 says a random gate "leaves z unchanged in expectation". With z_R = mean/(sd/sqrt(|R|)) it scales by
   sqrt(1 - g) (tested). So H2 (changed-code gate versus none, which shrinks R) is biased against passing. I kept the spec's z as the default endpoint and also store
   d = mean/sd (size-invariant); `headroom --endpoint d` applies the rule to d. The choice must be fixed before any test item is scored (statistician). This affects the
   family, so it is the most consequential open point.
2. **Denoise arm count.** v2 11.1 counts 2 denoised encodes with a 3-member family. I denoise the jpeg and noise conditions only (`config.DENOISE_FOR`, `--denoise-for`); splice
   has no denoise arm. Denoised codes get the image-direction `none` arm only (no gate), as 4.3 lists denoise and "denoise + GATE-M" (S4) separately.
3. **D is not in the M2 itemisation (12 passes).** Resolved by the null cache: one pass per caption length n, on disk, shared by M1, M2, M4 (at most 28 image nulls and 28 text
   nulls in total). First-use cost is real: the first items of each new n spend 1-2 extra passes.
4. **Text-direction statistic.** Mean per-token PMI (probe-1 `a_full_pmi`, the 0.990 reference), not the sum of Alg. 5 step 3, because c+ and c- have different lengths. Caption
   lengths are stored (`n_tok`, `n_tok_neg`) so the analysis can recompute sums.
5. **Y on ties and NaN.** Y = 1 only if mean > 0 (ties wrong, as Appendix A). z/d are NaN when |R| < 2 or sd = 0; analyses drop non-finite items per test and report the count
   (M4d). Empty R gives exactly 0 with n = 0 (L2).
6. **Seeds.** New `SEED_GATE = 20261029`; per-item key = fold offset (cal 0, head 1000, test 2000) + index, so no two folds share mask partitions. M1 reuses probe 2's own seeds
   because it consumes probe 2's B. The partition seed rule is probe 2's `[SEED, item, 99]`.
7. **Geometry-matched random gate seeds.** 3 seeds for the image-direction arms; the text-direction conditioning arm uses the first seed ("geo seed 1" in v2 11.1).
8. **Text-direction conditioning for the patch sanity condition and denoised copies** is not run (v2 lists it for the 3 realistic corruptions and clean only).
9. **Falsifier (7.6).** "CI does not exclude 0 on JPEG and on noise" read with the intent "q must beat the best cheap baseline": a CI that excludes 0 on the negative side also counts as
   falsified; both lists are reported.
10. **Cheap rivals get a sign oracle.** The patch-texture sign is a free choice, so the analysis adds the negated copy of texture, neighbour distance and rarity and picks the best
    mean AUROC among all (generous to the rivals). Texture is NaN for token-level corruptions (no observed pixels).
11. **Rarity** is leave-one-item-out over the clean codes available (M1: the probe-2 items; M2 writes `codefreq.npy` from the 300 calibration items).
12. **Hard-negative noun choice:** leftmost matched noun whose category is annotated and has a same-supercategory alternative; ambiguous words (orange, plant, bag, bat) are not in
    the table; 'person' items are skipped (single-member supercategory). Replacement display names are written once in `hardneg.CATS`.
13. **Folds need the tokenizer** (5-32 tokens), so they are built inside the first GPU runner (M2) and then frozen; the CPU dry run uses 1.3 x words and is never used as the folds.
14. **Guards are proposals.** `Guards` defaults are the diagnosis thresholds (9,000 MiB; 10,000 MiB first item; +1.5 GB rise; 2x median item time; AC loss). Using them as
    defaults needs Shlok's approval; every value is a CLI flag (`--max-used-mib` etc., `--no-ac-check`).
15. **HOLD scope.** The existing `exp_p2.driver` only reads `runs/<run>/HOLD.txt`, which would not stop a gate run. The gate runners and `gate_driver` also read
    `runs/P2-PROBE-02/HOLD.txt` and `runs/GATE-HOLD.txt`. The hold file lives in the worktree's `runs/`; a run from another checkout has its own `runs/`.
16. **A latent bug in `common.append_jsonl` (not changed):** after a hard kill mid-row, the next append glues onto the partial line and that row is lost on read. The gate runner
    repairs the tail (adds a newline) before appending; probes 1 and 2 still have the issue.
17. **Prop. 1, 6, 7 enumerations (v1 L4, L9) are not tested**: they need the 3^7 toy joint and test the theory, not the code; the brief asked for the limiting cases L1, L2, L3, L5, L6,
    L7, L8, L10, calibration, geometry, resume and HOLD, all covered.

## 4. Not testable without the GPU (all untested)

- `UniScorer.build/encode/selfcheck`, the real tokenizer, `ensure_folds` with real token counts, the real VQ encoder, real bf16 logits.
- Whether `vae.quantize.embedding.weight` exists in UniDisc's VQ wrapper (guess from LlamaGen's layout; absence is logged to `codebook.json` and the neighbour baseline becomes NaN).
- U7: whether UniDisc's logits at unmasked positions are meaningful (the TbV diagnostic `copy_through_stat` runs in M1/M4).
- Real memory (two 64 MiB Lambda matrices on the GPU plus batch-4 logits), real time per row (the 0.15 s estimate), real tie structure of q (hence the real eps0; the `eps0_resolvable`
  flag in `threshold.json` must be True), real fraction of changed codes per rung (decides the family).
- `torch.cuda` guards (`gpu_used_mib`, `set_per_process_memory_fraction`), `gpu_guard.py --every 1`, the staged commands of M0, `run_gate_m0.py` beyond its hold exit.
- Not built (SHOULD/COULD): S1 caption-typo runner (the caption-side score and word-unit helpers exist), S2 re-infill sampler, S3 hard-negative runner (the builder exists), S4 denoise + GATE-M,
  S5 K ablations, S6, E7, T2I, Mondrian, iterated gate, fp32 head.

## 5. Tests and the CPU dry run

```
set CUDA_VISIBLE_DEVICES=
python -m pytest tests/exp_p2 -q                       -> 110 passed in about 24 s (default python 3.14, pytest 9.0.2, torch 2.11)
PY -m pytest tests/exp_p2 -q   with PYTHONPATH=<folder holding copies of _pytest, pytest, pluggy, iniconfig, py>   -> 110 passed (project .venv, Python 3.12)
```
The project `.venv` has no pytest and nothing was installed; the second run used a copy of the pure-Python pytest packages from the default interpreter on `PYTHONPATH` (scratchpad folder).
`tests/test_ex_validate.py` fails at collection on a CRLF hash of `validator-tests.jsonl`; it is unrelated to this work and was not touched.

What the tests pin: CRC threshold equals a brute-force search over every jittered candidate; realised false-alarm proportion of 2,000 calibrate-then-test repetitions is at most
alpha + 3 MC SE, with and without heavy ties (L1); uniform scores give a random gate (L5); jitter never reorders distinct calibration values; geometry-matched gates are non-zero torus
translations, uniform over the 15 shifts on a 4x4 grid; B masks exactly one group plus the whole caption per pass and equals a direct forward; K=1 refused and B == D (L6); K=m equals
leave-one-out (L7); alpha=0 gives the empty gate and bit-identical evidence (L8); independent joint gives A == B, C == D and zero image evidence (L3); all gated gives exactly 0 (L2) and
the text direction equals its null; nulls depend only on caption length (L10); resume appends each item once, arrays precede rows, a torn tail is repaired, failures are logged; a hold
file stops every runner and the driver before a model, a CUDA call or even a run directory exists; the real hold file is not modified; jpeg/noise/swap/patch reproduce `run_probe2.corrupt`
exactly; the power table of v2 section 9 is reproduced (47/29/20 and 63/39/27 with alpha' = 0.0167).

CPU dry runs on real local data, stored under `runs/P2-GATE-CPU/` (exploratory, not preregistered, not research results):
- `m1_fallback/analysis.json` (command: `python -m exp_p2.analyze_gate_m1 --probe-run P2-PROBE-02 --m1-run P2-GATE-M1-NOTHERE --out-dir runs/P2-GATE-CPU/m1_fallback --boot 2000`): 21 probe-2 items,
  no q yet. Mean per-item AUROC against changed-code labels: swap plain-B 0.962, patch plain-B 0.967, r_original 0.495/0.506/0.453/0.504 (swap/patch/jpeg/noise); **jpeg: plain-B 0.543
  (CI 0.495-0.597), s1 0.541, texture with the sign flipped 0.756 (0.704-0.792); noise: plain-B 0.515, s1 0.515, texture sign-flipped 0.774 (0.749-0.803)**. So on these 21 items a pixel-variance
  detector beats the model's own likelihood on the two realistic corruptions; this is the red team's M4 concern in miniature and bears on the v2 7.6 falsifier. n = 21, one seed.
- `cpu_dryrun.json` (command: `python -m exp_p2.gate.cpu_dryrun`): 80-category table equals the instances file; 494 probe ids excluded; folds of 300/100/300 built and disjoint; 100 percent of negatives
  restrictable by category; hard-negative yield 74 of 100 (head) and 228 of 300 (test) with the approximate token counts; skips: no known noun 10 / 37, only 'person'-like or no free
  same-supercategory alternative 14 / 29, noun not annotated 2 / 6. The first 100 of each fold are in `hardneg_audit_sheet_*_first100.jsonl` for the reviewer pass (not yet judged).
